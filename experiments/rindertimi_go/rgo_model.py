"""RINDERTIMI-GO test bed: a coastal aquifer in (x, t) whose boundary conditions and forcing are reconstructed from rain
and sparse heads by function-space diffusion posterior sampling (FunDPS; Yao et al., NeurIPS 2025).

Joint function on the (x, t) grid, NX cells by NT weeks, five channels:
  0  h(x, t)   head (m); column 0 is the initial condition h0(x)
  1  eta(t)    sea level at x = 0 (Dirichlet boundary), m, broadcast along x
  2  qL(t)     inflow through the inland boundary x = L (Neumann boundary), m2/d, broadcast along x
  3  r(t)      areal recharge, mm/d, broadcast along x
  4  f(t)      the rain filtered by the unsaturated zone, f = k_tau * P (mm/d), broadcast along x; it is computed from
               the whole rain record, so it carries the antecedent rain that the window alone does not have
Physics, per unit width, implicit Euler with weekly steps:
  S dh/dt = T d2h/dx2 + r(t) - Q delta(x - x_w),   h(0, t) = eta(t),   T dh/dx (L, t) = qL(t)
Prior: rain from the SHIU-GO rain law (marked Poisson, seasonal, with a year multiplier); recharge
r = kappa * f(P) + e(t), f the Erlang-2 vadose filter of the rain, kappa lognormal; e, eta and qL Gaussian random fields
in time around random means; h0 the steady state of the mean forcing plus a Gaussian random field in x.
Given the rain and kappa every unknown is Gaussian and the head is affine in them, so the exact posterior is a
one-dimensional mixture over kappa with a common covariance. It is the reference for the diffusion sampler.
"""
import os
import sys

import numpy as np
from scipy.linalg import lu_factor, lu_solve, cho_factor, cho_solve

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'shiu_go'))
import shiu_model as SM  # noqa: E402  (rain law of the SHIU-GO note)

NX, NT = 32, 64                      # cells, weeks
L = 5000.0                           # m
DX = L / NX
DT = 7.0                             # d
TRANS, STOR = 1500.0, 0.05           # transmissivity (m2/d) and storativity
Q_W, X_W = 1.0, 1500.0               # known pumping (m2/d per unit width) at x_w
IW = int(X_W // DX)
XC = (np.arange(NX) + 0.5) * DX
PIEZO = np.array([250.0, 1250.0, 2750.0, 4250.0])
IP = (PIEZO // DX).astype(int)
TAU_V = 14.0                         # d, time constant of the Erlang-2 vadose filter
SPIN = 240                           # d of rain before the window, for the filter
KAP_MED, KAP_LSD = 0.35, 0.25        # recharge coefficient: lognormal median and log-sd
PRI = dict(e_sd=0.15, e_l=3.0,                     # recharge error: mm/d, weeks
           eta_m_sd=0.05, eta_sd=0.10, eta_l=2.0,  # sea level: m, m, weeks
           q_m=2.0, q_m_sd=0.4, q_sd=0.4, q_l=8.0,  # inland inflow: m2/d, weeks
           h0_sd=0.3, h0_l=1000.0, ymult_lsd=0.2)  # initial-condition perturbation: m, m; rain-year multiplier
SIG_H, SIG_ETA = 0.02, 0.01          # observation noise: heads, tide gauge (m)
P_OBS = 0.25                         # probability that a piezometer is read in a given week
CH = ['h', 'eta', 'qL', 'r', 'f']


# ------------------------------------------------------------------------------------------------ operators
def se_cov(n, sd, ell, jitter=1e-8):
    i = np.arange(n)
    return sd ** 2 * np.exp(-0.5 * ((i[:, None] - i[None, :]) / ell) ** 2) + jitter * sd ** 2 * np.eye(n)


def system():
    """implicit-Euler matrix A h_n = c h_{n-1} + b_n, and the steady-state matrix."""
    g = TRANS / DX
    A = np.zeros((NX, NX))
    for i in range(NX):
        if i > 0:
            A[i, i - 1] -= g; A[i, i] += g
        if i < NX - 1:
            A[i, i + 1] -= g; A[i, i] += g
    A[0, 0] += 2 * g                                   # half-cell link to the sea
    Ass = A.copy()
    A = A + STOR * DX / DT * np.eye(NX)
    return A, Ass


A_IMP, A_SS = system()
LU_IMP = lu_factor(A_IMP)
LU_SS = lu_factor(A_SS)
C_STOR = STOR * DX / DT


def rhs(eta, qL, r_md, Q=Q_W):
    """right-hand side without the storage term; eta (..,), qL (..,), r in m/d (..,) -> (NX, ..)."""
    eta, qL, r_md = np.broadcast_arrays(np.asarray(eta, float), np.asarray(qL, float), np.asarray(r_md, float))
    b = np.zeros((NX,) + eta.shape)
    b += r_md * DX
    b[IW] -= Q
    b[0] += 2 * TRANS / DX * eta
    b[-1] += qL
    return b


def steady(eta_m, q_m, r_md_m, Q=Q_W):
    return lu_solve(LU_SS, rhs(eta_m, q_m, r_md_m, Q))


def simulate(h0, eta, qL, r_mm, Q=Q_W):
    """h0 (NX, B); eta, qL, r (NT, B), r in mm/d -> h (NX, NT, B), column 0 = h0."""
    B = h0.shape[1]
    h = np.empty((NX, NT, B))
    h[:, 0] = h0
    for n in range(1, NT):
        b = C_STOR * h[:, n - 1] + rhs(eta[n], qL[n], r_mm[n] / 1000.0, Q)
        h[:, n] = lu_solve(LU_IMP, b)
    return h


# ------------------------------------------------------------------------------------------------ prior
COV = dict(e=se_cov(NT, PRI['e_sd'], PRI['e_l']), eta=se_cov(NT, PRI['eta_sd'], PRI['eta_l']),
           q=se_cov(NT, PRI['q_sd'], PRI['q_l']),
           h0=PRI['h0_sd'] ** 2 * np.exp(-0.5 * ((XC[:, None] - XC[None, :]) / PRI['h0_l']) ** 2) + 1e-8 * np.eye(NX))
CHOL = {k: np.linalg.cholesky(v) for k, v in COV.items()}


def rain_weeks(rng, B):
    """weekly rain (mm/week) and the vadose-filtered recharge input f (mm/d), both (NT, B)."""
    nd = SPIN + NT * 7
    P = np.empty((NT, B)); f = np.empty((NT, B))
    for b in range(B):
        start = rng.uniform(0, 365)
        t = start + np.arange(nd)
        lam, abar = SM.rain_rates(t)
        lam = lam * np.exp(PRI['ymult_lsd'] * rng.standard_normal())
        k = rng.poisson(lam)
        Pd = np.where(k > 0, rng.gamma(np.maximum(k, 1), abar), 0.0)
        fd = SM.erlang2(Pd, TAU_V)
        P[:, b] = Pd[SPIN:].reshape(NT, 7).sum(1)
        f[:, b] = fd[SPIN:].reshape(NT, 7).mean(1)
    return P, f


def sample_prior(rng, B):
    """B draws of the joint function, (B, 5, NX, NT), plus the latent kappa and pieces."""
    P, f = rain_weeks(rng, B)
    kap = KAP_MED * np.exp(KAP_LSD * rng.standard_normal(B))
    e = CHOL['e'] @ rng.standard_normal((NT, B))
    r = kap * f + e                                                     # mm/d
    eta_m = PRI['eta_m_sd'] * rng.standard_normal(B)
    eta = eta_m + CHOL['eta'] @ rng.standard_normal((NT, B))
    q_m = PRI['q_m'] + PRI['q_m_sd'] * rng.standard_normal(B)
    qL = q_m + CHOL['q'] @ rng.standard_normal((NT, B))
    h0 = steady(eta_m, q_m, kap * f.mean(0) / 1000.0) + CHOL['h0'] @ rng.standard_normal((NX, B))
    h = simulate(h0, eta, qL, r)
    a = np.empty((B, 5, NX, NT))
    a[:, 0] = np.moveaxis(h, 2, 0)
    for c, v in ((1, eta), (2, qL), (3, r), (4, f)):
        a[:, c] = np.broadcast_to(v.T[:, None, :], (B, NX, NT))
    return a.astype(np.float32), dict(kappa=kap, f=f, P=P)


# ------------------------------------------------------------------------------------------------ exact posterior
NZ = NT + 1 + NT + 1 + NT + NX       # d_eta, m_eta, d_q, m_q, e, d_h0
SL = dict(deta=slice(0, NT), meta=slice(NT, NT + 1), dq=slice(NT + 1, 2 * NT + 1), mq=slice(2 * NT + 1, 2 * NT + 2),
          e=slice(2 * NT + 2, 3 * NT + 2), dh0=slice(3 * NT + 2, NZ))


def prior_z():
    mu = np.zeros(NZ); mu[SL['mq']] = PRI['q_m']
    Sig = np.zeros((NZ, NZ))
    Sig[SL['deta'], SL['deta']] = COV['eta']; Sig[SL['meta'], SL['meta']] = PRI['eta_m_sd'] ** 2
    Sig[SL['dq'], SL['dq']] = COV['q']; Sig[SL['mq'], SL['mq']] = PRI['q_m_sd'] ** 2
    Sig[SL['e'], SL['e']] = COV['e']; Sig[SL['dh0'], SL['dh0']] = COV['h0']
    return mu, Sig


def response_matrix():
    """G (NX*NT, NZ): head response to unit unknowns (zero pumping); c_Q: response to the known pumping."""
    cols = []
    zero_t = np.zeros((NT, 1)); zero_x = np.zeros((NX, 1))
    I_t = np.eye(NT)
    # d_eta: impulse in eta, h0 unaffected
    cols.append(simulate(np.zeros((NX, NT)), I_t, np.zeros((NT, NT)), np.zeros((NT, NT)), Q=0.0))
    # m_eta: eta = 1 everywhere and h0 = steady state of eta = 1
    cols.append(simulate(steady(1.0, 0.0, 0.0, Q=0.0)[:, None], np.ones((NT, 1)), zero_t, zero_t, Q=0.0))
    cols.append(simulate(np.zeros((NX, NT)), np.zeros((NT, NT)), I_t, np.zeros((NT, NT)), Q=0.0))
    cols.append(simulate(steady(0.0, 1.0, 0.0, Q=0.0)[:, None], zero_t, np.ones((NT, 1)), zero_t, Q=0.0))
    cols.append(simulate(np.zeros((NX, NT)), np.zeros((NT, NT)), np.zeros((NT, NT)), I_t, Q=0.0))
    cols.append(simulate(np.eye(NX), np.zeros((NT, NX)), np.zeros((NT, NX)), np.zeros((NT, NX)), Q=0.0))
    G = np.concatenate([c.reshape(NX * NT, -1) for c in cols], axis=1)
    cQ = simulate(steady(0.0, 0.0, 0.0)[:, None], zero_t, zero_t, zero_t).reshape(NX * NT)
    return G, cQ


def kappa_response(f):
    """head response to recharge f (mm/d, NT) with kappa = 1, h0 at the steady state of the mean (zero pumping)."""
    h0 = steady(0.0, 0.0, f.mean() / 1000.0, Q=0.0)[:, None]
    return simulate(h0, np.zeros((NT, 1)), np.zeros((NT, 1)), f[:, None], Q=0.0).reshape(NX * NT)


def observation_rows(rng, scenario):
    """indices into the flattened (x, t) head field and, for the tide gauge, into eta; with their noise."""
    rows = []
    if scenario in ('B', 'C'):
        obs = rng.random((len(IP), NT)) < P_OBS
        for j, i in enumerate(IP):
            for n in np.flatnonzero(obs[j]):
                rows.append(('h', i * NT + n))
    if scenario == 'C':
        for n in range(NT):
            rows.append(('eta', n))
    return rows


def exact_posterior(y, rows, f, G, cQ, mu, Sig, nk=241, nsamp=2000, rng=None):
    """mixture over kappa; returns the kappa grid weights, the conditional mean coefficients and exact samples."""
    gk = kappa_response(f)
    m = len(rows)
    Hz = np.zeros((m, NZ)); hk = np.zeros(m); c0 = np.zeros(m); Rn = np.zeros(m)
    for k, (kind, idx) in enumerate(rows):
        if kind == 'h':
            Hz[k] = G[idx]; hk[k] = gk[idx]; c0[k] = cQ[idx]; Rn[k] = SIG_H ** 2
        else:
            Hz[k, SL['deta'].start + idx] = 1.0; Hz[k, SL['meta']] = 1.0; Rn[k] = SIG_ETA ** 2
    lgrid = np.log(KAP_MED) + KAP_LSD * np.linspace(-5, 5, nk)
    kap = np.exp(lgrid)
    logprior = -0.5 * ((lgrid - np.log(KAP_MED)) / KAP_LSD) ** 2          # density in log-kappa
    if m == 0:
        logw = logprior
        A0 = np.zeros((NZ, 0)); Spost = Sig; mz0 = mu; mz1 = np.zeros(NZ)
    else:
        Cy = Hz @ Sig @ Hz.T + np.diag(Rn)
        cf = cho_factor(Cy)
        K = Sig @ Hz.T @ np.linalg.inv(Cy) if m < 400 else None
        r0 = y - (Hz @ mu + c0)                                          # residual at kappa = 0
        a_ = cho_solve(cf, r0); b_ = cho_solve(cf, hk)
        # log p(y | kappa) = -0.5 (r0 - kappa hk)' Cy^-1 (r0 - kappa hk) + const
        logw = logprior - 0.5 * (-2 * kap * (hk @ a_) + kap ** 2 * (hk @ b_))
        Spost = Sig - K @ Hz @ Sig
        mz0 = mu + K @ r0; mz1 = -K @ hk                                 # E[z | y, kappa] = mz0 + kappa mz1
    w = np.exp(logw - logw.max()); w /= w.sum()
    out = dict(kgrid=kap, w=w, mz0=mz0, mz1=mz1, Spost=Spost, gk=gk)
    if rng is not None:
        ks = rng.choice(nk, size=nsamp, p=w)
        Ls = np.linalg.cholesky(Spost + 1e-12 * np.eye(NZ))
        z = (mz0[:, None] + kap[ks][None, :] * mz1[:, None]) + Ls @ rng.standard_normal((NZ, nsamp))
        out['samples'] = fields_from_z(z, kap[ks], f, G, cQ, gk)
        out['kappa_samples'] = kap[ks]
    return out


def fields_from_z(z, kap, f, G, cQ, gk):
    """the five channels of the joint function from latent z (NZ, S) and kappa (S,)."""
    h = (G @ z + gk[:, None] * kap[None, :] + cQ[:, None]).reshape(NX, NT, -1)
    eta = z[SL['deta']] + z[SL['meta']]
    qL = z[SL['dq']] + z[SL['mq']]
    r = kap[None, :] * f[:, None] + z[SL['e']]
    return dict(h=np.moveaxis(h, 2, 0), eta=eta.T, qL=qL.T, r=r.T)
