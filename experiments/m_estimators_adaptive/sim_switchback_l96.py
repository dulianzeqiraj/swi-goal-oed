"""E9. KAUZ-OED under chaos: adaptive switchback "pumping" tests on Lorenz-96, compared with the
observational fluctuation-dissipation (FDT) prediction and the naive regression.

Model (identical to KAUZ-OED Test 2, scratchpad/num/causal_l96.py): Lorenz-96 with N = 20 nodes,
    dx_i/dt = (x_{i+1} - x_{i-2}) x_{i-1} - x_i + F_i,   F_i = F = 8,
integrated with classical RK4, dt = 0.01. "Pumping" node p = 0, "monitoring zone" g = 3.

Switchback design. Periods k = 1..K of length ell. In period k the forcing at node p is F + Delta s_k,
s_k in {-1, +1}, Delta = 1 (all other nodes keep F). The outcome is
    Y_k = mean of x_g(t) over the RK4 step times t in (t_k + b, t_k + ell]      (burn-in b).
Potential outcomes. The system is deterministic, so Y_k(+1) and Y_k(-1) are functions of the state
x(t_k) at the start of the period, i.e. of the realised path up to k-1. In the simulation both are
computed by BRANCHING: from x(t_k) both forcings are integrated over the period, the realised branch
(s_k) is kept, the other is discarded. Design-based estimand along the realised path:
    tau_k = Y_k(+1) - Y_k(-1),     taubar_K = (1/K) sum_{k<=K} tau_k.
Assignment. P(s_k = +1 | F_{k-1}) = pi_k, F_{k-1} = past states, assignments and outcomes.
  'A' adaptive "pumping operation" (stationary system):
        pi_k = clip( 1 / (1 + exp(a1 zY_{k-1} + a2 T_{k-1})), pi_min, 1 - pi_min ),
        zY_{k-1} = (Y_{k-1} - mean(Y_1..Y_{k-1})) / sigma_Y   (pump less after a salty period),
        T_{k-1}  = running IPW t-statistic of the effect      (pump less once pumping is shown to salt),
        a1 = 1, a2 = 0.5, sigma_Y = 1, pi_min = 0.15, pi_k = 1/2 for k <= 10.
  'B' Bernoulli(1/2) switchback (pi_k = 1/2).
  'C' as A, but the operator sees Y_k^obs = Y_k + eta_k with a seasonal background
        eta_k = 0.75 sin(2 pi k / 52) (one "year" = 52 periods) that pumping does not cause.
        tau_k is unchanged (eta_k cancels); the dynamics are the same L96 model.
Estimators of taubar_K (S'_k = 1{s_k = +1}, W_k = sqrt(pi_sta(s_k) / pi_k(s_k)), pi_sta = 1/2):
  naive  difference in means of Y^obs, Welch standard error;
  AW     W_k-weighted difference in means = weighted LS of Y on (1, S') with the base paper's
         square-root stabilising weights, sandwich standard error;
  Hajek  W_k^2-weighted difference in means (Robins' stabilised IPW weights), linearised s.e.;
  IPW    tauhat_k = (Y_k^obs - m_{k-1}) (S'_k / pi_k - (1 - S'_k) / (1 - pi_k)), predictable
         baseline m_{k-1} = EWMA(lambda = max(1/k, 0.1)) of Y_1^obs..Y_{k-1}^obs (m_0 = 0);
         E[tauhat_k | F_{k-1}] = tau_k exactly, so tauhat_k - tau_k is a martingale difference.
         Variance proxy V_K = sum_k (tauhat_k - mean)^2 (conservative: it also contains sum (tau_k - taubar)^2).
         Fixed-K Wald:  mean +- 1.96 sqrt(V_K) / K.
         Asymptotic CS (Waudby-Smith et al. 2024, normal mixture, empirical variance):
             mean +- sigmahat_K sqrt((K + r)(log((K + r) / r) + 2 log(1/alpha))) / K,
             sigmahat_K^2 = V_K / K,  r = t* / (2 log(1/alpha) + log(2 log(1/alpha) + 1)),  t* = 1500.
Coverage of taubar_K: fixed-K miss rate, "Wald peeking" ever-miss and CS ever-miss over K0 <= K' <= K
(K0 = 20). Cost: first K with 0 outside the CS; K at which the CS half-width reaches 0.03 (projected
from sigmahat at K_max with the same boundary, since 0.03 is far beyond the simulated horizon).
Reference values (re-computed here with the exact code of causal_l96.py, same seeds):
  direct steady response R = d<x_3>/dF_0 from +-1 constant-forcing runs, 2 Delta R;
  quasi-Gaussian FDT with all nodes R_FDT = [int_0^4 C(u) du C(0)^{-1}]_{g p}, 2 Delta R_FDT;
  naive regression C(0)_{gp} / C(0)_{pp}, 2 Delta times it.
Dependence on ell and b: step responses from 24000 states of the switchback process (pi = 1/2,
ell = 5), both forcings over 10 time units, give E[tau](ell, b) for all (ell, b) at once; validated by
direct switchbacks with pi = 1/2 at ell in {0.5, 1, 2} (and B at ell = 5). FDT-predicted curve:
2 Delta / (ell - b) int_b^ell chi_F(t) dt, chi_F(t) = int_0^min(t,4) [C(u) C(0)^{-1}]_{gp} du.
Run: OMP_NUM_THREADS=1 python3 sim_switchback_l96.py   (2 worker processes; about 9 min).
Output: results/switchback_l96.json
"""
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy.stats import norm

from common import dump

N, F, DT, P, G = 20, 8.0, 0.01, 0, 3
DELTA = 1.0
ELL, BURN = 5.0, 1.0
R = 300
KMAX = dict(A=3000, B=3000, C=1500)
PI_MIN, A1, A2, SIG_Y, K_WARM = 0.15, 1.0, 0.5, 1.0, 10
LAM = 0.1
SEAS_A, SEAS_T = 0.75, 52
ALPHA = 0.05
Z = norm.ppf(1 - ALPHA / 2)
T_STAR = 1500
LA = 2 * np.log(1 / ALPHA)
RHO = T_STAR / (LA + np.log(LA + 1))
K0 = 20
H_TARGET = 0.03
B_LIST = (0.0, 0.5, 1.0)          # burn-ins recorded for the ell-dependence (B and validation runs)
QUICK = os.environ.get('QUICK') == '1'
if QUICK:
    R = 40
    KMAX = dict(A=400, B=400, C=400)


class L96:
    """In-place RK4 for many trajectories, state shape (N, M) (node-major, trajectories contiguous)."""

    def __init__(self, M):
        self.xp = np.empty((N + 3, M))
        self.k = [np.empty((N, M)) for _ in range(4)]
        self.y = np.empty((N, M))

    def rhs(self, x, Fv, out):
        xp = self.xp
        xp[2:N + 2] = x; xp[:2] = x[N - 2:]; xp[N + 2] = x[0]      # xp[j] = x[j - 2] (periodic)
        np.subtract(xp[3:], xp[:N], out=out)                        # x_{i+1} - x_{i-2}
        out *= xp[1:N + 1]                                          # * x_{i-1}
        out -= x
        out += Fv
        return out

    def step(self, x, Fv):
        k1, k2, k3, k4 = self.k; y = self.y
        self.rhs(x, Fv, k1)
        np.multiply(k1, .5 * DT, out=y); y += x; self.rhs(y, Fv, k2)
        np.multiply(k2, .5 * DT, out=y); y += x; self.rhs(y, Fv, k3)
        np.multiply(k3, DT, out=y); y += x; self.rhs(y, Fv, k4)
        k2 += k3; k2 *= 2; k1 += k2; k1 += k4; k1 *= DT / 6; x += k1


def mix_halfwidth(sig, K):
    """Asymptotic CS half-width (normal mixture, empirical sigma), Waudby-Smith et al. (2024)."""
    return sig * np.sqrt((K + RHO) * (np.log((K + RHO) / RHO) + LA)) / K


def spinup(rng, M, T=20.0):
    x = F + rng.standard_normal((N, M)); s = L96(M); Fv = np.full((N, M), F)
    for _ in range(int(round(T / DT))):
        s.step(x, Fv)
    return x


# ----------------------------------------------------------------------------------------------
def switchback(cfg, seed, ell=ELL, burn=BURN, K=None, Rr=None, record_b=False, hov=False):
    """Run Rr replicate switchback experiments in parallel, branching every period."""
    Rr = R if Rr is None else Rr
    K = KMAX[cfg] if K is None else K
    rng = np.random.default_rng(seed)
    n = int(round(ell / DT)); nb = int(round(burn / DT))
    blist = [b for b in B_LIST if b < ell - 1e-9] if record_b else [burn]
    nbs = [int(round(b / DT)) for b in blist]
    x = spinup(rng, Rr)
    sim = L96(2 * Rr); xx = np.empty((N, 2 * Rr)); Fv = np.full((N, 2 * Rr), F)
    Fv[P, :Rr] = F + DELTA; Fv[P, Rr:] = F - DELTA
    ar = np.arange(Rr)
    # per-period storage (K, Rr)
    Yp = np.zeros((K, Rr)); Ym = np.zeros((K, Rr)); S = np.zeros((K, Rr), bool); PI = np.zeros((K, Rr))
    Yb = {b: np.zeros((K, 2, Rr)) for b in blist} if record_b else None
    # estimator state
    m_base = np.zeros(Rr); sumY = np.zeros(Rr)
    ipw_s = np.zeros(Rr); ipw_q = np.zeros(Rr); tau_s = np.zeros(Rr)
    est = {k: np.zeros((K, Rr)) for k in ('ipw', 'naive', 'aw', 'hajek', 'taubar')}
    se = {k: np.zeros((K, Rr)) for k in ('ipw', 'naive', 'aw', 'hajek')}
    # weighted sums per arm: index 0 = '+', 1 = '-'; powers of weights used
    acc = {w: np.zeros((3, 2, Rr)) for w in ('u', 'W', 'W2', 'W4')}   # sum w, sum w Y, sum w Y^2
    hovrec = None
    if hov:
        nh = 8; hovrec = dict(x=np.zeros((nh * n // 5, N)), x3cf=np.zeros(nh * n // 5), s=[], tau=[], periods=nh)
    for k in range(K):
        # ---- assignment probability from the past only ----
        if cfg == 'B' or k < K_WARM:
            pi = np.full(Rr, 0.5)
        else:
            yobs_prev = np.where(S[k - 1], Yp[k - 1], Ym[k - 1]) + (eta(k - 1) if cfg == 'C' else 0.0)
            zY = (yobs_prev - sumY / k) / SIG_Y
            mean_ = ipw_s / k; var_ = np.maximum(ipw_q / k - mean_ ** 2, 1e-12)
            tst = mean_ / np.sqrt(var_ / k)
            pi = np.clip(1 / (1 + np.exp(A1 * zY + A2 * tst)), PI_MIN, 1 - PI_MIN)
        s1 = rng.random(Rr) < pi
        PI[k] = pi; S[k] = s1
        # ---- branch: integrate both forcings over the period ----
        xx[:, :Rr] = x; xx[:, Rr:] = x
        accb = [np.zeros(2 * Rr) for _ in nbs]
        for i in range(n):
            sim.step(xx, Fv)
            for j, nbj in enumerate(nbs):
                if i >= nbj:
                    accb[j] += xx[G]
            if hov and k < hovrec['periods'] and i % 5 == 4:
                r = k * n // 5 + i // 5
                hovrec['x'][r] = xx[:, 0] if s1[0] else xx[:, Rr]
                hovrec['x3cf'][r] = xx[G, Rr] if s1[0] else xx[G, 0]
        x = np.where(s1[None, :], xx[:, :Rr], xx[:, Rr:])
        jb = blist.index(burn) if burn in blist else 0
        yb = accb[jb] / (n - nbs[jb])
        Yp[k] = yb[:Rr]; Ym[k] = yb[Rr:]
        if record_b:
            for j, b in enumerate(blist):
                Yb[b][k, 0] = accb[j][:Rr] / (n - nbs[j]); Yb[b][k, 1] = accb[j][Rr:] / (n - nbs[j])
        if hov and k < hovrec['periods']:
            hovrec['s'].append(int(s1[0])); hovrec['tau'].append(float(Yp[k, 0] - Ym[k, 0]))
        # ---- estimators ----
        e = eta(k) if cfg == 'C' else 0.0
        yobs = np.where(s1, Yp[k], Ym[k]) + e
        tau_s += Yp[k] - Ym[k]
        th = (yobs - m_base) * np.where(s1, 1 / pi, -1 / (1 - pi))
        ipw_s += th; ipw_q += th ** 2
        lam = max(1.0 / (k + 1), LAM)
        m_base = (1 - lam) * m_base + lam * yobs
        sumY += yobs
        pa = np.where(s1, pi, 1 - pi)
        W = np.sqrt(0.5 / pa)
        arm = np.where(s1, 0, 1)
        for key, w in (('u', np.ones(Rr)), ('W', W), ('W2', W ** 2), ('W4', W ** 4)):
            a = acc[key]
            a[0, arm, ar] += w; a[1, arm, ar] += w * yobs; a[2, arm, ar] += w * yobs ** 2
        K1 = k + 1
        est['taubar'][k] = tau_s / K1
        mi = ipw_s / K1
        est['ipw'][k] = mi
        se['ipw'][k] = np.sqrt(np.maximum(ipw_q / K1 - mi ** 2, 0) / K1)
        with np.errstate(divide='ignore', invalid='ignore'):
            # naive with Welch s.e.
            nn, sy, syy = acc['u']
            mu = sy / nn; v = np.maximum(syy / nn - mu ** 2, 0) * nn / np.maximum(nn - 1, 1)
            est['naive'][k] = mu[0] - mu[1]; se['naive'][k] = np.sqrt(v[0] / nn[0] + v[1] / nn[1])
            # AW (weights W) and Hajek (weights W^2); sandwich: sum w^2 (Y - mu)^2 / (sum w)^2 per arm
            for key, wk, w2k in (('aw', 'W', 'W2'), ('hajek', 'W2', 'W4')):
                sw, swy, _ = acc[wk]; s2, s2y, s2yy = acc[w2k]
                mu = swy / sw
                vv = (s2yy - 2 * mu * s2y + mu ** 2 * s2) / sw ** 2
                est[key][k] = mu[0] - mu[1]; se[key][k] = np.sqrt(np.maximum(vv[0], 0) + np.maximum(vv[1], 0))
    out = dict(Yp=Yp, Ym=Ym, S=S, PI=PI, est=est, se=se, Yb=Yb, hov=hovrec, ell=ell, burn=burn)
    return out


def eta(k):
    return SEAS_A * np.sin(2 * np.pi * (k + 1) / SEAS_T)


# ----------------------------------------------------------------------------------------------
def summarise(cfg, o):
    est, se = o['est'], o['se']
    K, Rr = est['ipw'].shape
    Ks = np.arange(1, K + 1)
    tb = est['taubar']
    # IPW Wald and CS
    sig = se['ipw'] * np.sqrt(Ks)[:, None]
    hw_w = Z * se['ipw']; hw_cs = mix_halfwidth(sig, Ks[:, None])
    err = est['ipw'] - tb
    miss_w = np.abs(err) > hw_w; miss_cs = np.abs(err) > hw_cs
    mon = Ks >= K0
    ever_w = np.logical_or.accumulate(miss_w & mon[:, None], axis=0)
    ever_cs = np.logical_or.accumulate(miss_cs & mon[:, None], axis=0)
    miss_naive = np.abs(est['naive'] - tb) > Z * se['naive']
    miss_aw = np.abs(est['aw'] - tb) > Z * se['aw']
    miss_haj = np.abs(est['hajek'] - tb) > Z * se['hajek']
    grid = np.unique(np.round(np.geomspace(K0, K, 60)).astype(int))
    gi = grid - 1
    # exclusion of 0 (first K >= K0 with 0 outside), CS and Wald
    excl_cs = (np.abs(est['ipw']) > hw_cs) & mon[:, None]
    excl_w = (np.abs(est['ipw']) > hw_w) & mon[:, None]
    def first(b):
        f = np.where(b.any(0), b.argmax(0) + 1, -1)
        return f
    f_cs = first(excl_cs); f_w = first(excl_w)
    # projected K for half-width H_TARGET using sigmahat at K_max
    sK = sig[-1]
    lo = np.full(Rr, 10.0); hi = np.full(Rr, 1e8)
    for _ in range(80):
        mid = np.sqrt(lo * hi); big = mix_halfwidth(sK, mid) > H_TARGET
        lo = np.where(big, mid, lo); hi = np.where(big, hi, mid)
    Kh_cs = hi; Kh_w = (Z * sK / H_TARGET) ** 2
    # first K with half-width <= h for checkable h, to validate the projection
    hcheck = {}
    for h in (0.25, 0.2, 0.15, 0.12, 0.1):
        b = hw_cs <= h
        f = first(b)
        proj_lo = np.full(Rr, 10.0); proj_hi = np.full(Rr, 1e8)
        for _ in range(80):
            mid = np.sqrt(proj_lo * proj_hi); big = mix_halfwidth(sK, mid) > h
            proj_lo = np.where(big, mid, proj_lo); proj_hi = np.where(big, proj_hi, mid)
        hcheck[str(h)] = dict(frac_reached=float((f > 0).mean()),
                              median_observed=float(np.median(f[f > 0])) if (f > 0).any() else None,
                              median_projected=float(np.median(proj_hi)))
    # true conditional variance of the IPW term vs the variance proxy (conservativeness)
    PI = o['PI']; Yp, Ym = o['Yp'], o['Ym']
    yo = np.where(o['S'], Yp, Ym)
    # baseline sequence used (recompute)
    eta_k = np.array([eta(k) for k in range(K)])[:, None] if cfg == 'C' else 0.0
    yobs = yo + eta_k
    mb = np.zeros_like(yobs); m = np.zeros(Rr)
    for k in range(K):
        mb[k] = m; lam = max(1.0 / (k + 1), LAM); m = (1 - lam) * m + lam * yobs[k]
    a = Yp + eta_k - mb; bb = Ym + eta_k - mb
    condvar = a ** 2 * (1 - PI) / PI + bb ** 2 * PI / (1 - PI) + 2 * a * bb
    proxy = a ** 2 / PI + bb ** 2 / (1 - PI)
    tau = Yp - Ym
    Kf = [k for k in (100, 300, 1000, 1500, 3000) if k <= K]
    res = dict(
        R=Rr, K=K, grid=grid,
        ever_miss=dict(cs=ever_cs[gi].mean(1), wald_peek=ever_w[gi].mean(1)),
        miss=dict(wald=miss_w[gi].mean(1), cs=miss_cs[gi].mean(1), naive=miss_naive[gi].mean(1),
                  aw=miss_aw[gi].mean(1), hajek=miss_haj[gi].mean(1)),
        bias=dict({k: (est[k][gi] - tb[gi]).mean(1) for k in ('ipw', 'naive', 'aw', 'hajek')}),
        bias_se=dict({k: (est[k][gi] - tb[gi]).std(1) / np.sqrt(Rr) for k in ('ipw', 'naive', 'aw', 'hajek')}),
        hw_cs_median=np.median(hw_cs[gi], 1), hw_w_median=np.median(hw_w[gi], 1),
        frac_excl_cs=(f_cs[None, :] > 0) & (f_cs[None, :] <= grid[:, None]),
        frac_excl_w=(f_w[None, :] > 0) & (f_w[None, :] <= grid[:, None]),
        first_excl_cs=f_cs, first_excl_w=f_w,
        K_half_cs=Kh_cs, K_half_w=Kh_w, hcheck=hcheck,
        sigmahat_Kmax=sK,
        mean_condvar=condvar.mean(), mean_proxy_minus_tau2=(proxy.mean() - (tau.mean(0) ** 2).mean()),
        tau_stats=dict(mean=tau.mean(), se=tau.mean(0).std() / np.sqrt(Rr), sd=tau.std(),
                       q=np.quantile(tau, [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]),
                       frac_neg=(tau < 0).mean(), kurt=((tau - tau.mean()) ** 4).mean() / tau.var() ** 2),
        taubar_Kmax=dict(mean=tb[-1].mean(), sd=tb[-1].std()),
        pi=dict(median=np.median(PI[gi], 1), q10=np.quantile(PI[gi], 0.1, 1), q90=np.quantile(PI[gi], 0.9, 1),
                frac_at_clip=(np.minimum(PI, 1 - PI) <= PI_MIN + 1e-12)[gi].mean(1)),
        fixedK={str(k): dict({e: dict(bias=(est[e][k - 1] - tb[k - 1]).mean(),
                                       bias_se=(est[e][k - 1] - tb[k - 1]).std() / np.sqrt(Rr),
                                       sd=est[e][k - 1].std(), rmse=np.sqrt(((est[e][k - 1] - tb[k - 1]) ** 2).mean()),
                                       cover=1 - (np.abs(est[e][k - 1] - tb[k - 1]) > Z * se[e][k - 1]).mean(),
                                       cover_Etau=1 - (np.abs(est[e][k - 1] - tau.mean()) > Z * se[e][k - 1]).mean(),
                                       med_se=np.median(se[e][k - 1]))
                              for e in ('ipw', 'naive', 'aw', 'hajek')},
                             cs_cover=1 - miss_cs[k - 1].mean(), cs_ever=ever_cs[k - 1].mean(),
                             wald_ever=ever_w[k - 1].mean(), med_hw_cs=np.median(hw_cs[k - 1]),
                             med_hw_w=np.median(hw_w[k - 1]))
                for k in Kf},
        dist_err=dict({e: (est[e][-1] - tb[-1]) for e in ('ipw', 'naive', 'aw', 'hajek')}),
        dist_err_K=K,
    )
    res['frac_excl_cs'] = res['frac_excl_cs'].mean(1); res['frac_excl_w'] = res['frac_excl_w'].mean(1)
    # representative replicate: CS exclusion time closest to the median exclusion time
    fc = f_cs.astype(float); fc[fc < 0] = np.inf
    medf = np.median(fc)
    rr = int(np.argmin(np.abs(fc - medf))) if np.isfinite(medf) else 0
    res['trace'] = dict(rep=rr, ipw=est['ipw'][:, rr], taubar=tb[:, rr], naive=est['naive'][:, rr],
                        aw=est['aw'][:, rr], hw_cs=hw_cs[:, rr], hw_w=hw_w[:, rr], pi=PI[:, rr],
                        first_excl_cs=int(f_cs[rr]))
    # histogram of tau_k
    bins = np.linspace(-6, 6, 121)
    res['tau_hist'] = dict(edges=bins, counts=np.histogram(np.clip(tau, -5.999, 5.999), bins)[0],
                           n=tau.size)
    return res


# ----------------------------------------------------------------------------------------------
def step_response(seed=7, n_states=24000, T=10.0, batch=600):
    """Branch +-Delta from states of the pi = 1/2 switchback process (ell = 5) for T time units."""
    rng = np.random.default_rng(seed)
    nchain = batch; x = spinup(rng, nchain)
    s = L96(nchain); Fv = np.full((N, nchain), F)
    sim = L96(2 * batch); Fb = np.full((N, 2 * batch), F); Fb[P, :batch] += DELTA; Fb[P, batch:] -= DELTA
    nT = int(round(T / DT)); every = 5
    CD = []; CA = []; CP = []; CM = []
    nb = n_states // batch
    for bi in range(nb):
        for _ in range(2):          # two switchback periods (10 time units) between samples
            Fv[P] = F + DELTA * np.where(rng.random(nchain) < 0.5, 1, -1)
            for _ in range(int(round(ELL / DT))):
                s.step(x, Fv)
        xx = np.concatenate([x, x], 1)
        cp = np.zeros((nT // every + 1, batch)); cm = np.zeros_like(cp)
        run_p = np.zeros(batch); run_m = np.zeros(batch)
        for i in range(nT):
            sim.step(xx, Fb)
            run_p += xx[G, :batch]; run_m += xx[G, batch:]
            if (i + 1) % every == 0:
                cp[(i + 1) // every] = run_p; cm[(i + 1) // every] = run_m
        CP.append(cp); CM.append(cm)
    CP = np.concatenate(CP, 1); CM = np.concatenate(CM, 1)     # cumulative sums of x_g at steps 1..i
    return CP, CM, every


def ell_curves(CP, CM, every):
    tg = np.round(np.arange(0.1, 10.0001, 0.05), 4)
    out = {}
    for b in B_LIST:
        mean_, se_, sdA, sdY, sdtau, ells = [], [], [], [], [], []
        for ell in tg:
            if ell <= b + 0.15:
                continue
            ie = int(round(ell / DT)) // every; ib = int(round(b / DT)) // every
            nst = (ie - ib) * every
            yp = (CP[ie] - CP[ib]) / nst; ym = (CM[ie] - CM[ib]) / nst
            tau = yp - ym
            ells.append(ell); mean_.append(tau.mean()); se_.append(tau.std() / np.sqrt(tau.size))
            sdA.append(((yp + ym) / 2).std()); sdY.append(np.concatenate([yp, ym]).std()); sdtau.append(tau.std())
        out[str(b)] = dict(ell=ells, mean=mean_, se=se_, sd_avg=sdA, sd_branch=sdY, sd_tau=sdtau)
    return out


def periods_needed(eff, sig):
    """K with asymptotic-CS half-width equal to eff for per-period sigma sig (vectorised bisection)."""
    eff = np.asarray(eff, float); sig = np.asarray(sig, float)
    lo = np.full(eff.shape, 1.0); hi = np.full(eff.shape, 1e9)
    for _ in range(90):
        mid = np.sqrt(lo * hi); big = mix_halfwidth(sig, mid) > np.abs(eff)
        lo = np.where(big, mid, lo); hi = np.where(big, hi, mid)
    return hi


# ----------------------------------------------------------------------------------------------
def reference_values():
    """Exact code of scratchpad/num/causal_l96.py (np.roll RK4, same seeds) + FDT response function."""
    def rhs(x, Fv): return (np.roll(x, -1, 1) - np.roll(x, 2, 1)) * np.roll(x, 1, 1) - x + Fv

    def run(Fv, ntraj=100, T=1000.0, seed=0, sample_every=5, keep=False):
        r = np.random.default_rng(seed); x = F + r.standard_normal((ntraj, N))
        for _ in range(int(20 / DT)):
            k1 = rhs(x, Fv); k2 = rhs(x + .5 * DT * k1, Fv); k3 = rhs(x + .5 * DT * k2, Fv); k4 = rhs(x + DT * k3, Fv)
            x = x + DT / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        nst = int(T / DT); s = np.zeros(N); out = [] if keep else None
        for t in range(nst):
            k1 = rhs(x, Fv); k2 = rhs(x + .5 * DT * k1, Fv); k3 = rhs(x + .5 * DT * k2, Fv); k4 = rhs(x + DT * k3, Fv)
            x = x + DT / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            s += x.mean(0)
            if keep and t % sample_every == 0:
                out.append(x.copy())
        return s / nst, (np.array(out) if keep else None)
    Fp = np.full(N, F); Fp[P] += DELTA; Fm = np.full(N, F); Fm[P] -= DELTA
    mp, _ = run(Fp, seed=1); mm, _ = run(Fm, seed=2)
    Rdirect = (mp - mm) / (2 * DELTA)
    _, X = run(np.full(N, F), ntraj=50, T=400.0, seed=3, keep=True)
    X = X - X.mean((0, 1))
    dts = 0.05; maxlag = int(4.0 / dts); T_, M_, _ = X.shape
    C = np.array([np.einsum('tmi,tmj->ij', X[lag:], X[:T_ - lag]) / ((T_ - lag) * M_) for lag in range(maxlag)])
    Cint = C.sum(0) * dts - 0.5 * dts * C[0]
    C0inv = np.linalg.inv(C[0])
    R_fdt = (Cint @ C0inv)[G, P]
    reg = C[0][G, P] / C[0][P, P]
    # response function r_F(u) = [C(u) C0^{-1}]_{gp} for u up to 4 (beyond: frozen, as in Test 2)
    rF = (C[:, G, :] @ C0inv[:, P])
    # chi_F(t_j) = dts (sum_{i<j} r_F(t_i)) - dts r_F(0) / 2 (the rule of Cint), so chi_F(4) = R_fdt exactly
    lags = np.arange(maxlag + 1) * dts
    chiF = np.concatenate([[0.0], np.cumsum(rF) * dts - 0.5 * dts * rF[0]])
    return dict(R_direct=Rdirect[G], R_direct_row=Rdirect[:8], R_fdt=R_fdt, reg=reg,
                rF=rF, lags=lags, chiF=chiF, R_direct_se_from_l96check=0.006)


def fdt_curve(ref, ells, b):
    """2 Delta / (ell - b) * int_b^ell chi_F(t) dt, chi_F frozen beyond lag 4 (step-sum, dt grid)."""
    lags = np.asarray(ref['lags']); chiF = np.asarray(ref['chiF'])
    out = []
    for ell in ells:
        t = np.arange(int(round(b / DT)) + 1, int(round(ell / DT)) + 1) * DT
        c = np.interp(np.minimum(t, lags[-1]), lags, chiF)
        out.append(2 * DELTA * c.mean())
    return np.array(out)


# ----------------------------------------------------------------------------------------------
def task(name):
    t0 = time.time()
    if name in ('A', 'B', 'C'):
        seed = dict(A=101, B=202, C=303)[name]
        o = switchback(name, seed, record_b=(name == 'B'), hov=(name == 'A'))
        res = summarise(name, o)
        if name == 'B':
            res['Yb'] = {str(b): dict(mean=(v[:, 0] - v[:, 1]).mean(),
                                      se=(v[:, 0] - v[:, 1]).mean(0).std() / np.sqrt(v.shape[2]))
                         for b, v in o['Yb'].items()}
        if name == 'A':
            res['hov'] = o['hov']
        res['time_s'] = time.time() - t0
        return name, res
    if name == 'valid':
        out = {}
        for j, ell in enumerate((0.5, 1.0, 2.0)):
            K = 1200 if not QUICK else 100
            o = switchback('B', 400 + j, ell=ell, burn=0.0, K=K, Rr=200 if not QUICK else 20, record_b=True)
            out[str(ell)] = {str(b): dict(mean=(v[:, 0] - v[:, 1]).mean(),
                                          se=(v[:, 0] - v[:, 1]).mean(0).std() / np.sqrt(v.shape[2]))
                             for b, v in o['Yb'].items()}
        return name, dict(points=out, time_s=time.time() - t0)
    if name == 'step':
        CP, CM, every = step_response(n_states=24000 if not QUICK else 1200)
        res = ell_curves(CP, CM, every)
        return name, dict(curves=res, n_states=CP.shape[1], time_s=time.time() - t0)
    if name == 'ref':
        return name, dict(reference_values(), time_s=time.time() - t0)


def main():
    t0 = time.time()
    names = ['A', 'B', 'C', 'step', 'valid', 'ref']
    with Pool(2) as pool:
        out = dict(pool.imap_unordered(task, names))
    ref = out['ref']; step = out['step']
    # FDT-predicted curves and periods/time needed versus (ell, b) at pi = 1/2
    for b, cur in step['curves'].items():
        cur['fdt'] = fdt_curve(ref, cur['ell'], float(b))
        # per-period IPW sigma at pi = 1/2 with an ideal constant baseline: E tauhat^2 - (E tau)^2
        sig = 2 * np.asarray(cur['sd_branch'])
        Kn = periods_needed(np.asarray(cur['mean']), sig)
        cur['K_excl_pred'] = Kn; cur['T_excl_pred'] = Kn * np.asarray(cur['ell'])
    J = dict(setting=dict(N=N, F=F, dt=DT, p=P, g=G, Delta=DELTA, ell=ELL, burn=BURN, R=R, Kmax=KMAX,
                          pi_min=PI_MIN, a1=A1, a2=A2, sigma_Y=SIG_Y, K_warm=K_WARM, lam=LAM,
                          seas_amp=SEAS_A, seas_period=SEAS_T, alpha=ALPHA, t_star=T_STAR, rho=RHO, K0=K0,
                          h_target=H_TARGET, quick=QUICK),
             ref=dict(R_direct=ref['R_direct'], R_direct_se=0.006, R_fdt=ref['R_fdt'], reg=ref['reg'],
                      two_delta_R=2 * DELTA * ref['R_direct'], two_delta_fdt=2 * DELTA * ref['R_fdt'],
                      two_delta_reg=2 * DELTA * ref['reg'], R_direct_row=ref['R_direct_row'],
                      rF=ref['rF'], lags=ref['lags'], chiF=ref['chiF']),
             A=out['A'], B=out['B'], C=out['C'], step=step, valid=out['valid'],
             times={k: v.get('time_s') for k, v in out.items()}, wall_s=time.time() - t0)
    dump(J, 'switchback_l96.json' if not QUICK else 'switchback_l96_quick.json')
    print(f"wall {time.time() - t0:.0f}s", {k: round(v.get('time_s', 0)) for k, v in out.items()})


if __name__ == '__main__':
    main()
