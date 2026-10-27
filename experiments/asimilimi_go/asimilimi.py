"""ASIMILIMI-GO (asimilimi: the assimilation). Numerical checks of the theorems of the note "Updating the boundary
and initial conditions of the Fushe-Kuqe system by data assimilation".

Test bed: the linear coastal aquifer of FILLIMI-GO and KUFIRI-GO (reviews 44 and 45): 5 km, 50 cells, sea at x = 0
(Dirichlet, half-cell), no flow at 5 km, T = 1000 m2/d, Sy = 0.1, three aquitard compartments (rates 0.05, 0.5,
2 /yr), a supply well at 1.5 km. Unknowns that the data must update:
  initial conditions  h(x,0) and the aquitard legacy h_k(x,0) (the fastest compartment starts in equilibrium, a
                      linear constraint every prior member satisfies);
  boundary conditions sea-level offset eta0 (static), interannual sea level eta_ia(t) (Ornstein-Uhlenbeck),
                      recharge anomaly rho(t) (OU), mean-recharge error dR (static), unlicensed pumping E at the
                      well (static);
  missing dynamics    a closure m(x; theta) = sum_j theta_j psi_j(x) on four hat functions (Gupta-Lermusiaux form).
Observations: heads at 250, 1250, 2750, 4250 m, monthly for 10 years (sd 0.02 m); optional tide gauge.

E1  exactness of the head block (Theorem 1): ensemble smoother vs exact Gaussian posterior, error ~ N^-1/2.
E2  what data teach about initial and boundary conditions (Theorem 3): posterior sd against window length, with the
    lower bound of Theorem 3(i) for the initial state.
E3  the filter forgets a wrong initial condition (Theorem 4): Lyapunov function monotone; bounded response to a
    missing source.
E4  boundary versus missing dynamics (Theorem 5): exact confounding of dR with a uniform closure, principal angles.
E5  coverage of 90% intervals over 400 twin truths: correct model, missing dynamics, closure added.
E6  a nonlinear chloride sample (Theorem 7): mean-field EnKF vs exact conditioning; error against the distance of the
    predictive law from its Gaussian projection; the probit anamorphosis that linearises the mixing-zone operator.
E7  linear constraints survive the ensemble update (Proposition 6).
Writes res/asimilimi.json and res/run_log.txt (via run_all.sh).
"""
import json
import os
import time

import numpy as np
from scipy.linalg import expm, cho_factor, cho_solve
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
P = dict(L=5000.0, N=50, T=1000.0 * 365.25, Sy=0.10, rates=[0.05, 0.5, 2.0], cap=[0.05, 0.03, 0.02],
         xw=1500.0, xobs=[250.0, 1250.0, 2750.0, 4250.0], sig_obs=0.02, sig_gauge=0.01, dt=1.0 / 12, years=10.0,
         sd_h0=0.20, ell=1000.0, sd_leg=0.30, sig_eta=0.06, tau_eta=1.0, sig_rho=0.05, tau_rho=0.5,
         sd_eta0=0.05, sd_E=150.0, sd_dR=0.02, sd_th=0.02, hats=[1000.0, 2000.0, 3000.0, 4000.0], hw=1000.0)
DX = P['L'] / P['N']
XC = (np.arange(P['N']) + 0.5) * DX
K = len(P['rates'])
NH = P['N'] * (K + 1)


def hat(c, w):
    return np.clip(1 - np.abs(XC - c) / w, 0, None)


def build(extras):
    """Continuous augmented system dX = A X dt + dW (W with intensity Qc). extras: list of names among
    eta_ia, rho, eta0, E, dR, th0..th3, cu (uniform closure). Returns A, Qc, index dict."""
    N, T, Sy = P['N'], P['T'], P['Sy']
    idx = {nm: NH + i for i, nm in enumerate(extras)}
    n = NH + len(extras)
    A = np.zeros((n, n))
    c = T / DX ** 2 / Sy
    for i in range(N):
        if i > 0:
            A[i, i - 1] += c; A[i, i] -= c
        if i < N - 1:
            A[i, i + 1] += c; A[i, i] -= c
    A[0, 0] -= 2 * c                                                   # Dirichlet sea face at x = 0 (half cell)
    for k, (a, s) in enumerate(zip(P['rates'], P['cap'])):
        sl = slice(N * (k + 1), N * (k + 2))
        A[:N, :N] -= np.eye(N) * s * a / Sy
        A[:N, sl] += np.eye(N) * s * a / Sy
        A[sl, sl] -= np.eye(N) * a
        A[sl, :N] += np.eye(N) * a
    Qc = np.zeros(n)
    iw = int(P['xw'] // DX)
    for nm in extras:
        j = idx[nm]
        if nm in ('eta_ia', 'eta0'):
            A[0, j] += 2 * c
        if nm == 'eta_ia':
            A[j, j] = -1 / P['tau_eta']; Qc[j] = 2 * P['sig_eta'] ** 2 / P['tau_eta']
        if nm == 'rho':
            A[:N, j] += 1 / Sy
            A[j, j] = -1 / P['tau_rho']; Qc[j] = 2 * P['sig_rho'] ** 2 / P['tau_rho']
        if nm == 'dR' or nm == 'cu':
            A[:N, j] += 1 / Sy
        if nm == 'E':                                                  # m3/d per km of coast -> m2/yr per m width
            A[iw, j] -= 365.25 / 1000.0 / (Sy * DX)
        if nm.startswith('th'):
            A[:N, j] += hat(P['hats'][int(nm[2:])], P['hw']) / Sy
    return A, Qc, idx


def discretise(A, Qc, dt, doublings=10):
    """Exact discretisation: F = e^{A dt}, Qd = int_0^dt e^{As} Qc e^{A's} ds. Van Loan's block exponential is
    applied on dt / 2^10 (the diffusion operator is stiff) and the result is doubled: Qd(2t) = F(t) Qd(t) F(t)' + Qd(t)."""
    n = A.shape[0]
    h = dt / 2 ** doublings
    M = np.zeros((2 * n, 2 * n))
    M[:n, :n] = -A; M[:n, n:] = np.diag(Qc); M[n:, n:] = A.T
    E = expm(M * h)
    Fh = E[n:, n:].T
    Qh = Fh @ E[:n, n:]
    Qh = 0.5 * (Qh + Qh.T)
    for _ in range(doublings):
        Qh = Fh @ Qh @ Fh.T + Qh
        Fh = Fh @ Fh
    F = expm(A * dt)
    return F, 0.5 * (Qh + Qh.T)


def prior_cov(extras, idx):
    n = NH + len(extras)
    P0 = np.zeros((n, n))
    N = P['N']
    Ch = P['sd_h0'] ** 2 * np.exp(-np.abs(XC[:, None] - XC[None, :]) / P['ell'])
    Cl = P['sd_leg'] ** 2 * np.exp(-np.abs(XC[:, None] - XC[None, :]) / P['ell'])
    # h_k(0) = h(0) + legacy_k for the two slow compartments; the fastest starts in equilibrium, h_3(0) = h(0)
    L = np.zeros((NH, N * 3))
    for k in range(K + 1):
        L[k * N:(k + 1) * N, :N] = np.eye(N)
    L[N:2 * N, N:2 * N] = np.eye(N)
    L[2 * N:3 * N, 2 * N:3 * N] = np.eye(N)
    Cb = np.zeros((3 * N, 3 * N)); Cb[:N, :N] = Ch; Cb[N:2 * N, N:2 * N] = Cl; Cb[2 * N:, 2 * N:] = Cl
    P0[:NH, :NH] = L @ Cb @ L.T
    sd = dict(eta_ia=P['sig_eta'], rho=P['sig_rho'], eta0=P['sd_eta0'], E=P['sd_E'], dR=P['sd_dR'], cu=P['sd_dR'])
    for nm in extras:
        j = idx[nm]
        P0[j, j] = (sd[nm] if nm in sd else P['sd_th']) ** 2
    return P0


def obs_matrix(n, idx, gauge=False):
    rows = []
    for x in P['xobs']:
        r = np.zeros(n); r[int(x // DX)] = 1.0; rows.append(r)
    sig = [P['sig_obs']] * len(rows)
    if gauge:
        r = np.zeros(n)
        for nm in ('eta_ia', 'eta0'):
            if nm in idx:
                r[idx[nm]] = 1.0
        rows.append(r); sig.append(P['sig_gauge'])
    return np.array(rows), np.array(sig)


def batch(F, Qd, H, sig, P0, nsteps):
    """Joint Gaussian of (X0, y_{1:n}): returns Phi (stacked H F^k), the data covariance S and Cov(X0, y)."""
    n = F.shape[0]; m = H.shape[0]
    Phi = np.zeros((m * nsteps, n))
    Fk = np.eye(n)
    Pp = np.zeros((n, n))                                              # covariance of the process-noise part
    Pk = []
    for k in range(nsteps):
        Fk = F @ Fk
        Pp = F @ Pp @ F.T + Qd
        Phi[k * m:(k + 1) * m] = H @ Fk
        Pk.append(Pp.copy())
    S = Phi @ P0 @ Phi.T
    # process-noise covariance of the data: Cov(x_i, x_j) = F^{i-j} P_j (i >= j), block = (H F^{i-j}) (P_j H')
    HF = [H.copy()]
    for d in range(1, nsteps):
        HF.append(HF[-1] @ F)
    PH = [Pk[j] @ H.T for j in range(nsteps)]
    for j in range(nsteps):
        for i in range(j, nsteps):
            blk = HF[i - j] @ PH[j]
            S[i * m:(i + 1) * m, j * m:(j + 1) * m] += blk
            if i != j:
                S[j * m:(j + 1) * m, i * m:(i + 1) * m] += blk.T
    S += np.diag(np.tile(sig ** 2, nsteps))
    return Phi, 0.5 * (S + S.T), P0 @ Phi.T


def simulate(F, Qd, H, sig, P0, nsteps, rng, nens=1, x0=None, extra=None, clean=False):
    """Simulate trajectories; returns X0 (nens, n) and data (nens, nsteps*m). extra(k) adds a missing source."""
    n = F.shape[0]; m = H.shape[0]
    L0 = np.linalg.cholesky(P0 + 1e-12 * np.eye(n))
    Lq = np.linalg.cholesky(Qd + 1e-14 * np.eye(n))
    X0 = rng.standard_normal((nens, n)) @ L0.T if x0 is None else np.atleast_2d(x0).copy()
    x = X0.copy()
    Y = np.zeros((X0.shape[0], nsteps * m)); Yc = np.zeros_like(Y)
    for k in range(nsteps):
        x = x @ F.T + rng.standard_normal(x.shape) @ Lq.T
        if extra is not None:
            x = x + extra
        Yc[:, k * m:(k + 1) * m] = x @ H.T
        Y[:, k * m:(k + 1) * m] = Yc[:, k * m:(k + 1) * m] + rng.standard_normal((x.shape[0], m)) * sig
    return (X0, Y, Yc) if clean else (X0, Y)


def goals(idx, n):
    """Linear goals of the unknowns: mean initial head over the first km, mean slow legacy, eta0, E."""
    N = P['N']
    g = {}
    v = np.zeros(n); v[:10] = 0.1; g['initial head, first km'] = v
    v = np.zeros(n); v[N:N + N] = 1.0 / N; g['slow aquitard legacy (mean)'] = v
    for nm, lab in (('eta0', 'sea-level offset eta0'), ('E', 'unlicensed pumping E')):
        if nm in idx:
            v = np.zeros(n); v[idx[nm]] = 1.0; g[lab] = v
    return g


def main():
    t0 = time.time()
    os.makedirs(RES, exist_ok=True)
    out = dict(P=P)
    nsteps = int(round(P['years'] / P['dt']))
    base = ['eta_ia', 'rho', 'eta0', 'E']
    A, Qc, idx = build(base)
    F, Qd = discretise(A, Qc, P['dt'])
    n = F.shape[0]
    H, sig = obs_matrix(n, idx)
    P0 = prior_cov(base, idx)
    G = goals(idx, n)
    lam = np.sort(-np.linalg.eigvals(A[:NH, :NH]).real)
    out['slowest_rates_per_yr'] = lam[:6].tolist()
    print('slowest decay rates /yr', np.round(lam[:6], 4), flush=True)

    # ---------------------------------------------------------------- exact posterior of the initial and static unknowns
    Phi, S, Cxy = batch(F, Qd, H, sig, P0, nsteps)
    cS = cho_factor(S)
    Cpost = P0 - Cxy @ cho_solve(cS, Cxy.T)
    exact = {k: dict(prior_sd=float(np.sqrt(v @ P0 @ v)), post_sd=float(np.sqrt(v @ Cpost @ v))) for k, v in G.items()}
    out['exact'] = exact
    print('exact posterior sd', {k: round(v['post_sd'], 4) for k, v in exact.items()}, flush=True)

    # ---------------------------------------------------------------- E1: ensemble smoother -> exact (Theorem 1)
    rng = np.random.default_rng(1)
    xt, yt = simulate(F, Qd, H, sig, P0, nsteps, rng)
    yt = yt[0]
    mpost = Cxy @ cho_solve(cS, yt)
    Ns = [25, 50, 100, 200, 400, 800, 1600]
    reps = 20
    e1 = {}
    for Ne in Ns:
        em, es = {k: [] for k in G}, {k: [] for k in G}
        for r in range(reps):
            rr = np.random.default_rng(1000 + 37 * Ne + r)
            X0, Y, Yn = simulate(F, Qd, H, sig, P0, nsteps, rr, nens=Ne, clean=True)   # Yn: noise-free predictions
            Xa = X0 - X0.mean(0); Ya = Yn - Yn.mean(0)
            Cxy_e = Xa.T @ Ya / (Ne - 1); Cyy_e = Ya.T @ Ya / (Ne - 1)
            Kg = np.linalg.solve(Cyy_e + np.diag(np.tile(sig ** 2, nsteps)), Cxy_e.T).T
            pert = yt[None, :] + rr.standard_normal(Y.shape) * np.tile(sig, nsteps)
            Xup = X0 + (pert - Yn) @ Kg.T
            for k, v in G.items():
                gm, gs = (Xup @ v).mean(), (Xup @ v).std(ddof=1)
                em[k].append((gm - v @ mpost) / exact[k]['post_sd']); es[k].append(gs / exact[k]['post_sd'] - 1)
        e1[Ne] = {k: dict(rms_mean_err=float(np.sqrt(np.mean(np.square(em[k])))), rms_sd_err=float(np.sqrt(np.mean(np.square(es[k])))))
                  for k in G}
        print('E1', Ne, {k: (round(v['rms_mean_err'], 3), round(v['rms_sd_err'], 3)) for k, v in e1[Ne].items()}, f'{time.time() - t0:.0f}s', flush=True)
    out['E1'] = {str(k): v for k, v in e1.items()}
    # slope of log error against log N (all goals pooled)
    xs = np.log(Ns); ys = np.log([np.mean([e1[Ne][k]['rms_mean_err'] for k in G]) for Ne in Ns])
    out['E1_slope_mean'] = float(np.polyfit(xs, ys, 1)[0])
    ys2 = np.log([np.mean([e1[Ne][k]['rms_sd_err'] for k in G]) for Ne in Ns])
    out['E1_slope_sd'] = float(np.polyfit(xs, ys2, 1)[0])
    print('E1 slopes', out['E1_slope_mean'], out['E1_slope_sd'], flush=True)

    # ---------------------------------------------------------------- E2: information against window (Theorem 3)
    windows = [0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30]
    e2 = {}
    for gauge in (False, True):
        Hg, sg = obs_matrix(n, idx, gauge=gauge)
        PhiL, SL, CxyL = batch(F, Qd, Hg, sg, P0, int(round(max(windows) / P['dt'])))
        m = Hg.shape[0]
        rows = {k: [] for k in G}; lb = {k: [] for k in G}
        for W in windows:
            ns = int(round(W / P['dt'])) * m
            Ssub = SL[:ns, :ns]; Csub = CxyL[:, :ns]
            Cp = P0 - Csub @ np.linalg.solve(Ssub, Csub.T)
            # Theorem 3(i): precision <= P0^-1 + Phi' Gamma^-1 Phi (process noise and other unknowns only remove information)
            Ph = PhiL[:ns]
            Sl = Ph @ P0 @ Ph.T + np.diag(np.tile(sg ** 2, ns // m))
            Cl = P0 - P0 @ Ph.T @ np.linalg.solve(Sl, Ph @ P0)
            for k, v in G.items():
                rows[k].append(float(np.sqrt(v @ Cp @ v))); lb[k].append(float(np.sqrt(v @ Cl @ v)))
        e2['gauge' if gauge else 'heads only'] = dict(windows=windows, post_sd=rows, lower_bound_sd=lb)
        print('E2', 'gauge' if gauge else 'heads', {k: [round(x, 4) for x in r] for k, r in rows.items()}, flush=True)
    out['E2'] = e2
    # infinite-window lower bound for the initial head goal (geometric tail of the IC information)
    Phin = np.linalg.matrix_power(F, 1)
    # information contributed by observations at time t about the initial head goal direction, per year
    v = G['initial head, first km']
    w = P0 @ v / (v @ P0 @ v)                                           # direction in X0 that carries the goal prior
    contrib = []
    Fk = np.eye(n)
    for k in range(int(round(30 / P['dt']))):
        Fk = F @ Fk
        contrib.append(float(np.sum((H @ Fk @ w) ** 2 / sig ** 2)))
    out['E2_ic_info_by_time'] = dict(t=[(k + 1) * P['dt'] for k in range(len(contrib))], info=contrib)

    # ---------------------------------------------------------------- E3: the filter forgets (Theorem 4)
    def kfilter(m0, C0, Y, Fm=F, Qm=Qd, Hm=H, sg=sig):
        mm, CC = m0.copy(), C0.copy()
        means, covs, V = [], [], []
        Rm = np.diag(sg ** 2); m_ = Hm.shape[0]
        for k in range(Y.shape[0] // m_):
            mm = Fm @ mm; CC = Fm @ CC @ Fm.T + Qm
            Sk = Hm @ CC @ Hm.T + Rm
            Kk = np.linalg.solve(Sk, Hm @ CC).T
            mm = mm + Kk @ (Y[k * m_:(k + 1) * m_] - Hm @ mm)
            CC = CC - Kk @ Hm @ CC; CC = 0.5 * (CC + CC.T)
            means.append(mm.copy()); covs.append(CC.copy())
        return means, covs
    rng = np.random.default_rng(3)
    _, Y3 = simulate(F, Qd, H, sig, P0, nsteps, rng)
    Y3 = Y3[0]
    m0a = np.zeros(n); m0b = np.zeros(n); m0b[:NH] = 0.5                 # a wrong initial head: +0.5 m everywhere
    ma, ca = kfilter(m0a, P0, Y3)
    mb, cb = kfilter(m0b, P0, Y3)
    V = [float((ma[k] - mb[k]) @ np.linalg.pinv(ca[k], rcond=1e-11, hermitian=True) @ (ma[k] - mb[k])) for k in range(nsteps)]
    V0 = float((m0a - m0b) @ np.linalg.pinv(P0, rcond=1e-11, hermitian=True) @ (m0a - m0b))
    dh = [float(np.max(np.abs(ma[k][:P['N']] - mb[k][:P['N']]))) for k in range(nsteps)]
    mono = bool(all(V[k + 1] <= V[k] * (1 + 1e-9) for k in range(nsteps - 1)) and V[0] <= V0)
    mc, cc = kfilter(m0a, 10 * P0, Y3)
    Nh = P['N']
    dP = [float(np.linalg.norm(ca[k][:Nh, :Nh] - cc[k][:Nh, :Nh]) / np.linalg.norm(ca[k][:Nh, :Nh])) for k in range(nsteps)]
    gapE = [float(abs(ma[k][idx['E']] - mb[k][idx['E']])) for k in range(nsteps)]
    gapEta = [float(abs(ma[k][idx['eta0']] - mb[k][idx['eta0']])) for k in range(nsteps)]
    sdE = [float(np.sqrt(ca[k][idx['E'], idx['E']])) for k in range(nsteps)]
    sdEta = [float(np.sqrt(ca[k][idx['eta0'], idx['eta0']])) for k in range(nsteps)]
    out['E3'] = dict(V0=V0, V=V, max_head_gap=dh, monotone=mono, cov_gap_heads=dP, gap_E=gapE, gap_eta0=gapEta, sd_E=sdE, sd_eta0=sdEta)
    print('E3 V0', round(V0, 2), 'V(1y)', round(V[11], 3), 'V(5y)', round(V[59], 5), 'V(10y)', V[-1], 'monotone', mono,
          'head gap 1y/5y', round(dh[11], 4), round(dh[59], 6), 'head cov gap 1y/10y', round(dP[11], 4), dP[-1], 'E gap/sd 1y,10y', round(gapE[11] / sdE[11], 3), round(gapE[-1] / sdE[-1], 3), flush=True)
    # bounded response to a missing source (truth has a source the filter does not know)
    src = np.zeros(n); src[:P['N']] = 0.08 * hat(3000.0, 1000.0) / P['Sy']   # m/yr -> dh/dt
    Fsrc = np.zeros(n)
    # discrete effect of a constant source over one step: int_0^dt e^{As} ds src
    Mbig = np.zeros((n + 1, n + 1)); Mbig[:n, :n] = A; Mbig[:n, n] = src
    Fsrc = expm(Mbig * P['dt'])[:n, n]
    rng = np.random.default_rng(4)
    xs0, Y4 = simulate(F, Qd, H, sig, P0, nsteps, rng, extra=Fsrc)
    # the truth's states along the path (re-simulate with the same seed to record states)
    rng = np.random.default_rng(4)
    L0 = np.linalg.cholesky(P0 + 1e-12 * np.eye(n)); Lq = np.linalg.cholesky(Qd + 1e-14 * np.eye(n))
    x = rng.standard_normal((1, n)) @ L0.T
    truth = []
    for k in range(nsteps):
        x = x @ F.T + rng.standard_normal(x.shape) @ Lq.T + Fsrc
        rng.standard_normal((1, H.shape[0]))
        truth.append(x[0].copy())
    mf, cf = kfilter(np.zeros(n), P0, Y4[0])
    err = [float(np.max(np.abs(mf[k][:P['N']] - truth[k][:P['N']]))) for k in range(nsteps)]
    # bound: e_k = (I - K_k H)(F e_{k-1} + Fsrc) + gain-noise terms; the deterministic part
    ed = np.zeros(n); errd = []
    for k in range(nsteps):
        Cf = F @ (cf[k - 1] if k else P0) @ F.T + Qd
        Kk = np.linalg.solve(H @ Cf @ H.T + np.diag(sig ** 2), H @ Cf).T
        ed = (np.eye(n) - Kk @ H) @ (F @ ed + Fsrc)
        errd.append(float(np.max(np.abs(ed[:P['N']]))))
    # without assimilation the missing source accumulates towards its steady effect
    xfree = np.zeros(n); free = []
    for k in range(nsteps):
        xfree = F @ xfree + Fsrc; free.append(float(np.max(np.abs(xfree[:P['N']]))))
    out['E3_missing'] = dict(filter_err=err, det_bias=errd, free_drift=free)
    print('E3 missing source: filter head error max', round(max(err), 4), 'bias part', round(max(errd), 4),
          'free drift 10y', round(free[-1], 4), flush=True)

    # ---------------------------------------------------------------- E4: boundary vs closure (Theorem 5)
    ex4 = ['eta_ia', 'rho', 'eta0', 'E', 'dR', 'cu', 'th0', 'th1', 'th2', 'th3']
    A4, Qc4, idx4 = build(ex4)
    F4, Qd4 = discretise(A4, Qc4, P['dt'])
    n4 = F4.shape[0]
    H4, s4 = obs_matrix(n4, idx4)
    P04 = prior_cov(ex4, idx4)
    Phi4, S4, C4 = batch(F4, Qd4, H4, s4, P04, nsteps)
    Cp4 = P04 - C4 @ np.linalg.solve(S4, C4.T)
    def corr(a, b):
        return float(Cp4[a, b] / np.sqrt(Cp4[a, a] * Cp4[b, b]))
    i_dR, i_cu = idx4['dR'], idx4['cu']
    v_sum = np.zeros(n4); v_sum[i_dR] = v_sum[i_cu] = 1
    v_dif = np.zeros(n4); v_dif[i_dR] = 1; v_dif[i_cu] = -1
    # principal-angle cosine between the data responses of E and of the closure hat nearest the well, and of eta0 and th0
    def cosang(a, b):
        ga, gb = Phi4[:, a], Phi4[:, b]
        return float(abs(ga @ gb) / np.linalg.norm(ga) / np.linalg.norm(gb))
    e4 = dict(corr_dR_cu=corr(i_dR, i_cu),
              sd_sum_prior=float(np.sqrt(v_sum @ P04 @ v_sum)), sd_sum_post=float(np.sqrt(v_sum @ Cp4 @ v_sum)),
              sd_dif_prior=float(np.sqrt(v_dif @ P04 @ v_dif)), sd_dif_post=float(np.sqrt(v_dif @ Cp4 @ v_dif)),
              cos_E_th1=cosang(idx4['E'], idx4['th1']), corr_E_th1=corr(idx4['E'], idx4['th1']),
              cos_eta0_th0=cosang(idx4['eta0'], idx4['th0']), corr_eta0_th0=corr(idx4['eta0'], idx4['th0']),
              cos_dR_cu=cosang(i_dR, i_cu))
    # break the confounding with a chloride-mass-balance estimate of recharge (sd 0.02 m/yr on dR) and with a meter on E
    Hx = np.zeros((2, n4)); Hx[0, i_dR] = 1; Hx[1, idx4['E']] = 1
    sx = np.array([0.005, 30.0])
    Cxy_x = P04 @ Hx.T
    S_x = np.block([[S4, Phi4 @ P04 @ Hx.T], [Hx @ P04 @ Phi4.T, Hx @ P04 @ Hx.T + np.diag(sx ** 2)]])
    Ctot = np.hstack([C4, Cxy_x])
    Cp4b = P04 - Ctot @ np.linalg.solve(S_x, Ctot.T)
    e4['with_cmb_and_meter'] = dict(corr_dR_cu=float(Cp4b[i_dR, i_cu] / np.sqrt(Cp4b[i_dR, i_dR] * Cp4b[i_cu, i_cu])),
                                     sd_dif_post=float(np.sqrt(v_dif @ Cp4b @ v_dif)),
                                     sd_cu_post=float(np.sqrt(Cp4b[i_cu, i_cu])), sd_cu_post_heads=float(np.sqrt(Cp4[i_cu, i_cu])),
                                     corr_E_th1=float(Cp4b[idx4['E'], idx4['th1']] / np.sqrt(Cp4b[idx4['E'], idx4['E']] * Cp4b[idx4['th1'], idx4['th1']])),
                                     sd_E_post=float(np.sqrt(Cp4b[idx4['E'], idx4['E']])), sd_E_post_heads=float(np.sqrt(Cp4[idx4['E'], idx4['E']])))
    out['E4'] = e4
    print('E4', {k: (round(v, 4) if isinstance(v, float) else v) for k, v in e4.items()}, flush=True)

    # ---------------------------------------------------------------- E5: coverage over twin truths
    ntw = 400
    z90 = norm.ppf(0.95)
    res5 = {}
    clos = ['th0', 'th1', 'th2', 'th3']
    for scen in ('correct model', 'missing source, no closure', 'missing source, closure added'):
        ex = base + (clos if scen.endswith('added') else [])
        Am, Qcm, idm = build(ex)
        Fm, Qdm = discretise(Am, Qcm, P['dt'])
        nm_ = Fm.shape[0]
        Hm, sm = obs_matrix(nm_, idm)
        P0m = prior_cov(ex, idm)
        Phim, Sm, Cm = batch(Fm, Qdm, Hm, sm, P0m, nsteps)
        Km = np.linalg.solve(Sm, Cm.T).T
        Cpm = P0m - Km @ Cm.T
        Gm = goals(idm, nm_)
        # truth: the base model, plus (scenarios 2 and 3) unmodelled distributed sources drawn from the closure prior
        extr = base + ([] if scen == 'correct model' else clos)
        Atr, Qctr, idtr = build(extr)
        Ftr, Qdtr = discretise(Atr, Qctr, P['dt'])
        ntr = Ftr.shape[0]
        Htr, str_ = obs_matrix(ntr, idtr)
        P0tr = prior_cov(extr, idtr)
        Gtr = goals(idtr, ntr)
        rng = np.random.default_rng(55)
        hits = {k: 0 for k in Gm}; bias = {k: [] for k in Gm}
        for it in range(ntw):
            X0t, Yt = simulate(Ftr, Qdtr, Htr, str_, P0tr, nsteps, rng)
            mp = Km @ Yt[0]
            for k in Gm:
                tv = X0t[0] @ Gtr[k]
                est = mp @ Gm[k]; sd_ = np.sqrt(Gm[k] @ Cpm @ Gm[k])
                hits[k] += int(abs(est - tv) <= z90 * sd_)
                bias[k].append((est - tv) / sd_)
        res5[scen] = {k: dict(coverage=hits[k] / ntw, mean_z=float(np.mean(bias[k])), rms_z=float(np.sqrt(np.mean(np.square(bias[k])))),
                              post_sd=float(np.sqrt(Gm[k] @ Cpm @ Gm[k]))) for k in Gm}
        print('E5', scen, {k: (v['coverage'], round(v['rms_z'], 2)) for k, v in res5[scen].items()}, f'{time.time() - t0:.0f}s', flush=True)
    out['E5'] = res5
    out['E5_ntwins'] = ntw

    # ---------------------------------------------------------------- E6: a nonlinear chloride sample (Theorem 7)
    # forecast law at t = 10 yr from the prior (no heads), at x_o = 500 m; interface depth zeta = (h_ref + s)/delta
    Pk = P0.copy()
    for k in range(nsteps):
        Pk = F @ Pk @ F.T + Qd
    io = int(500.0 // DX)
    Cxx = P0 @ np.linalg.matrix_power(F, nsteps).T                      # Cov(X0, X_T)
    s_sd = float(np.sqrt(Pk[io, io]))
    gE = G['unlicensed pumping E']; ge = G['sea-level offset eta0']
    # static parameters are part of the state: covariance between s = h(x_o, T) and E or eta0 at time T
    cov_sE = float(Pk[io, idx['E']]); cov_se = float(Pk[io, idx['eta0']])
    delta, href, wmix, Clf, Cls, sCl = 0.025, 0.8, 3.0, 60.0, 21000.0, 25.0
    zeta_ref = href / delta
    sg = np.linspace(-6, 6, 4001) * s_sd; ws = norm.pdf(sg / s_sd); ws /= ws.sum()
    def fobs(s, zs):
        return Clf + (Cls - Clf) * norm.cdf((zs - (href + s) / delta) / wmix)
    e6 = []
    rng = np.random.default_rng(66)
    for zs in [20.0, 24.0, 28.0, 30.0, 32.0, 34.0, 36.0, 40.0, 44.0]:
        fs = fobs(sg, zs)
        Ef = float(ws @ fs); Vf = float(ws @ (fs - Ef) ** 2)
        Csf = float(ws @ (sg * (fs - Ef)))
        # exact posterior E[s|y] by quadrature; E[g|y] = (C_gs / C_ss) E[s|y] for g jointly Gaussian with s (zero means)
        st = rng.standard_normal(3000) * s_sd                          # truths drawn from the forecast law
        ys = fobs(st, zs) + rng.standard_normal(3000) * sCl
        lik = norm.pdf((ys[:, None] - fs[None, :]) / sCl) * ws[None, :]
        Z = lik.sum(1)
        Es_y = (lik @ sg) / Z
        Vs_y = (lik @ sg ** 2) / Z - Es_y ** 2
        # mean-field EnKF (statistical linearisation)
        Ks = Csf / (Vf + sCl ** 2)
        Es_k = Ks * (ys - Ef)
        Vs_k = s_sd ** 2 - Ks * Csf
        # probit anamorphosis: zs - (href + s)/delta = w Phi^{-1}(c), linear in s
        cobs = np.clip((ys - Clf) / (Cls - Clf), 1e-6, 1 - 1e-6)
        yprime = (zs - wmix * norm.ppf(cobs)) * delta - href            # equals s plus transformed noise
        sd_prime = wmix * delta * (sCl / (Cls - Clf)) / np.maximum(norm.pdf(norm.ppf(cobs)), 1e-12)
        Kp = s_sd ** 2 / (s_sd ** 2 + sd_prime ** 2)
        Es_p = Kp * yprime
        # censored probit: inside the mixing zone the probit update; a saturated sample is a one-sided (censored)
        # observation, s beyond the threshold where c leaves [eps, 1 - eps], conditioned exactly (truncated Gaussian)
        eps = 1e-3
        a_lo = (zs - wmix * norm.ppf(1 - eps)) * delta - href          # c > 1 - eps  <=>  s < a_lo
        a_hi = (zs - wmix * norm.ppf(eps)) * delta - href              # c < eps      <=>  s > a_hi
        Es_c = Es_p.copy()
        lo = cobs > 1 - eps; hi = cobs < eps
        Es_c[lo] = -s_sd * norm.pdf(a_lo / s_sd) / norm.cdf(a_lo / s_sd)
        Es_c[hi] = s_sd * norm.pdf(a_hi / s_sd) / norm.sf(a_hi / s_sd)
        # predictive law of y and its Gaussian projection: total variation distance (1-D quadrature)
        ygrid = np.linspace(min(fs.min(), Ef - 6 * np.sqrt(Vf + sCl ** 2)) - 4 * sCl, max(fs.max(), Ef + 6 * np.sqrt(Vf + sCl ** 2)) + 4 * sCl, 6000)
        py = (norm.pdf((ygrid[:, None] - fs[None, :]) / sCl) / sCl) @ ws
        pg = norm.pdf(ygrid, Ef, np.sqrt(Vf + sCl ** 2))
        tv = float(0.5 * np.trapezoid(np.abs(py - pg), ygrid))
        r = dict(screen_depth=zs, interface_sd=float(s_sd / delta), tv_to_gaussian=tv,
                 rmse_exact=float(np.sqrt(np.mean((Es_y - st) ** 2)) / s_sd),
                 rmse_enkf=float(np.sqrt(np.mean((Es_k - st) ** 2)) / s_sd),
                 rmse_anamorphosis=float(np.sqrt(np.mean((Es_p - st) ** 2)) / s_sd),
                 rmse_censored_probit=float(np.sqrt(np.mean((Es_c - st) ** 2)) / s_sd),
                 censored_minus_exact=float(np.sqrt(np.mean((Es_c - Es_y) ** 2)) / s_sd),
                 share_saturated=float(np.mean(lo | hi)),
                 enkf_minus_exact=float(np.sqrt(np.mean((Es_k - Es_y) ** 2)) / s_sd),
                 anamorphosis_minus_exact=float(np.sqrt(np.mean((Es_p - Es_y) ** 2)) / s_sd),
                 info_exact=float(1 - np.mean(Vs_y) / s_sd ** 2), info_enkf=float(1 - Vs_k / s_sd ** 2))
        e6.append(r)
        print('E6', {k: round(v, 4) for k, v in r.items()}, flush=True)
    # the error of the goal (E or eta0) is the error of s times |C_gs|/C_ss; report the transfer factors
    out['E6'] = dict(rows=e6, s_sd=s_sd, corr_s_E=cov_sE / np.sqrt(Pk[io, io] * Pk[idx['E'], idx['E']]),
                     corr_s_eta0=cov_se / np.sqrt(Pk[io, io] * Pk[idx['eta0'], idx['eta0']]),
                     params=dict(delta=delta, href=href, w=wmix, Clf=Clf, Cls=Cls, sCl=sCl, x_o=500.0))

    # ---------------------------------------------------------------- E7: constraints and the ensemble update (Proposition 6)
    rng = np.random.default_rng(77)
    N_ = P['N']
    Ch = P['sd_h0'] ** 2 * np.exp(-np.abs(XC[:, None] - XC[None, :]) / P['ell'])
    Cl_ = P['sd_leg'] ** 2 * np.exp(-np.abs(XC[:, None] - XC[None, :]) / P['ell'])
    Lh, Ll = np.linalg.cholesky(Ch), np.linalg.cholesky(Cl_)
    ne = 100
    X0 = np.zeros((ne, n))
    a = rng.standard_normal((ne, N_)) @ Lh.T
    X0[:, :N_] = a; X0[:, 3 * N_:4 * N_] = a                                  # fastest compartment in equilibrium
    X0[:, N_:2 * N_] = a + rng.standard_normal((ne, N_)) @ Ll.T
    X0[:, 2 * N_:3 * N_] = a + rng.standard_normal((ne, N_)) @ Ll.T
    for nm, sd_ in (('eta_ia', P['sig_eta']), ('rho', P['sig_rho']), ('eta0', P['sd_eta0']), ('E', P['sd_E'])):
        X0[:, idx[nm]] = rng.standard_normal(ne) * sd_
    _, Y, Yn = simulate(F, Qd, H, sig, P0, nsteps, rng, x0=X0, clean=True)
    Xa = X0 - X0.mean(0); Ya = Yn - Yn.mean(0)
    Kg = np.linalg.solve(Ya.T @ Ya / (ne - 1) + np.diag(np.tile(sig ** 2, nsteps)), (Xa.T @ Ya / (ne - 1)).T).T
    Xup = X0 + (yt[None, :] + rng.standard_normal(Y.shape) * np.tile(sig, nsteps) - Yn) @ Kg.T
    viol_prior = float(np.max(np.abs(X0[:, 3 * N_:4 * N_] - X0[:, :N_])))
    viol_post = float(np.max(np.abs(Xup[:, 3 * N_:4 * N_] - Xup[:, :N_])))
    # an inequality constraint is not preserved: EnKF on the sea fraction c of a screen (observation linear in c)
    zs = 32.0; nens = 200; outside = []
    for it in range(300):
        s_ens = rng.standard_normal(nens) * s_sd
        c_ens = norm.cdf((zs - (href + s_ens) / delta) / wmix)
        s_true = rng.standard_normal() * s_sd
        y = Clf + (Cls - Clf) * norm.cdf((zs - (href + s_true) / delta) / wmix) + rng.standard_normal() * sCl
        yp = Clf + (Cls - Clf) * c_ens
        Kc = np.cov(c_ens, yp)[0, 1] / (np.var(yp, ddof=1) + sCl ** 2)
        c_up = c_ens + Kc * (y + rng.standard_normal(nens) * sCl - yp)
        outside.append(float(np.mean((c_up < 0) | (c_up > 1))))
    out['E7'] = dict(violation_prior=viol_prior, violation_post=viol_post, ensemble=ne,
                     sea_fraction_outside_01_mean=float(np.mean(outside)), sea_fraction_outside_01_max=float(np.max(outside)),
                     share_updates_with_any_outside=float(np.mean(np.array(outside) > 0)))
    print('E7', out['E7'], flush=True)
    out['seconds'] = time.time() - t0
    json.dump(out, open(os.path.join(RES, 'asimilimi.json'), 'w'), indent=1)
    print('wrote res/asimilimi.json', f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
