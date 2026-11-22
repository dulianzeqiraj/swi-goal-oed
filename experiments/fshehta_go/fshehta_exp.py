"""FSHEHTA-GO: deconfounding the effect of multi-well pumping on coastal salinity, with the Time Series Deconfounder
(Bica, Alaa & van der Schaar, ICML 2020) and with a physics-anchored substitute read from the heads.

Linear-response coastal aquifer, weekly steps (first order of the Strack potential, which is linear in recharge and
pumping for a fixed conductivity field; review VIII):
  hidden dryness     D_t = rho_D D_{t-1} + nu_t                 (evaporative demand, heat; never observed)
  local stress       L_t = 0.9 L_{t-1} + xi_t                   (crop stress at farm 1 only: a single-cause confounder)
  rain (observed)    f_t  seasonal filtered rain, mm/d
  recharge           R_t = kappa f_t - b D_t + e_t              regional
                     Rloc_t = -b_L L_t                          local, near well 1
  pumping (treat.)   A_tj = mu + lam D_t + psi 1{j=1} L_t + eps_tj,   j = 1..k
  salinity (outc.)   Y_t = sum_j beta_j (kS * A_j)_t - rho (kS * R)_t - rho_L (kS * Rloc)_t + eta_t
  heads at loggers   H_mt = -sum_j g_mj (kH * A_j)_t + q_m (kH * R)_t + qL_m (kH * Rloc)_t + noise
kS, kH: exponential response kernels (salinity 10 weeks, heads 4 weeks). The estimands are beta_j (effect of a
sustained unit of pumping at well j on the salinity index) and the policy effect of cutting all pumping by 20%.
Estimators (ordinary least squares on the convolved regressors, Newey-West standard errors):
  naive      Y on kS*A_j and kS*f
  tsd        + kS*Zhat, Zhat_t = E[Z_t | A_1..A_{t-1}]: a one-factor dynamic factor model of the pumping, the substitute
             built from the history as in the Time Series Deconfounder (Z_t = g(H_{t-1}))
  tsd_now    + kS*Zhat_now, Zhat_now from the current pumping (first principal component): the static deconfounder
  phys       + kS*Rhat_m, Rhat_m read from the heads: add back the known pumping response, deconvolve the head kernel
  both       tsd + phys
  oracle     + kS*R and kS*Rloc (the true recharge)
Physics-based check: regress each A_j on Zhat, f and Rhat; a significant Rhat coefficient falsifies the substitute.
Tests:
  T29  bias of every estimator as the number of wells k grows, for a persistent and a fast hidden dryness
  T30  a single-cause hidden confounder at well 1
  T31  wrong physics (drawdown coefficients and head kernel off): bias of the physics estimator vs Proposition D4
  T32  the physics-based check: rejection rates under no confounding, multi-cause and single-cause confounding
usage: python fshehta_exp.py [quick]   (writes res/fshehta.json, res/fshehta_case.npz, res/fshehta_log.txt)"""
import json
import os
import sys
import time

import numpy as np
from scipy.signal import lfilter

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
QUICK = len(sys.argv) > 1 and sys.argv[1] == 'quick'
NREP = 60 if QUICK else 400
T, BURN = 520, 104
TAU_S, TAU_H = 10.0, 4.0
NSHIFT = 99
TAU_GRID = (2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0)
LOG = []

BASE = dict(k=8, rho_D=0.9, lam=0.5, sig_eps=0.5, kappa=0.35, b=0.3, sig_e=0.10, psi=0.0, b_L=0.3, rho=1.0,
            rho_L=1.0, sig_eta=0.03, sig_h=0.01, mu=1.0, gerr=0.0, tau_h_assumed=TAU_H)


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.append(s)


def kern(x, tau, axis=0):
    a = np.exp(-1.0 / tau)
    return lfilter([1 - a], [1, -a], x, axis=axis)


def geometry(k):
    """well positions along the coast (km), the monitored supply well at 0, two loggers (near well 1 and far)."""
    xw = np.linspace(0.5, 4.0, k)
    beta = 0.4 * np.exp(-xw / 1.5)                       # effect of a sustained unit of pumping on the salinity index
    xl = np.array([0.6, 3.0])                            # logger 1 next to well 1, logger 2 inland
    g = 0.30 * np.exp(-np.abs(xl[:, None] - xw[None, :]) / 1.0)
    q = np.array([0.5, 0.5])                             # head per mm/d of regional recharge
    qL = np.array([0.5, 0.02])                           # head per mm/d of local recharge near well 1
    return beta, g, q, qL


def simulate(rng, p):
    k = p['k']
    n = T + BURN
    beta, g, q, qL = geometry(k)
    t = np.arange(n)
    nu = rng.standard_normal(n) * np.sqrt(1 - p['rho_D'] ** 2)
    D = lfilter([1.0], [1, -p['rho_D']], nu)
    L = lfilter([1.0], [1, -0.9], rng.standard_normal(n) * np.sqrt(1 - 0.81))
    f = np.maximum(2.0 + 1.5 * np.sin(2 * np.pi * t / 52) + 0.8 * rng.standard_normal(n), 0.0)
    R = p['kappa'] * f - p['b'] * D + p['sig_e'] * rng.standard_normal(n)
    Rloc = -p['b_L'] * L
    A = p['mu'] + p['lam'] * D[:, None] + p['sig_eps'] * rng.standard_normal((n, k))
    A[:, 0] += p['psi'] * L
    SA = kern(A, TAU_S); SR = kern(R, TAU_S); SL = kern(Rloc, TAU_S)
    eta = lfilter([1.0], [1, -0.5], p['sig_eta'] * rng.standard_normal(n))
    Y = SA @ beta - p['rho'] * SR - p['rho_L'] * SL + eta
    HA = kern(A, TAU_H); HR = kern(R, TAU_H); HL = kern(Rloc, TAU_H)
    H = -HA @ g.T + HR[:, None] * q[None, :] + HL[:, None] * qL[None, :] + p['sig_h'] * rng.standard_normal((n, 2))
    sl = slice(BURN, n)
    return dict(A=A, f=f, R=R, Rloc=Rloc, D=D, L=L, Y=Y, H=H, SA=SA, SR=SR, SL=SL, beta=beta, g=g, q=q, qL=qL, sl=sl)


def factor_history(A):
    """one-factor dynamic factor model of the pumping, fitted by principal components; the substitute is the one-step
    Kalman prediction E[Z_t | A_1..A_{t-1}] (built from the history, as in the Time Series Deconfounder), and the
    contemporaneous score (the static deconfounder)."""
    Ac = A - A.mean(0)
    u, s, vt = np.linalg.svd(Ac, full_matrices=False)
    lam = vt[0] * s[0] / np.sqrt(len(A))                 # loadings, factor of unit variance
    z_now = Ac @ vt[0] / (s[0] / np.sqrt(len(A)))
    resid = Ac - np.outer(z_now, lam)
    s2 = np.maximum(resid.var(0), 1e-6)
    # the score is the factor plus averaged idiosyncratic noise: separate the two before fitting the AR(1) state
    nv = float(lam @ (s2 * lam)) / float(lam @ lam) ** 2
    sz2 = max(1.0 - nv, 0.05)
    g1 = float(np.mean(z_now[1:] * z_now[:-1]))
    r = float(np.clip(g1 / sz2, 0.0, 0.999))
    q_ = sz2 * (1 - r ** 2)                              # innovation variance of the AR(1) factor
    n = len(A)
    zp = np.zeros(n); P = sz2; zf = 0.0
    Hn = lam / s2
    for t_ in range(n):
        zp[t_] = r * zf if t_ else 0.0
        Pp = r * r * P + q_ if t_ else sz2
        # update with A_t (used only for the next prediction)
        info = 1.0 / Pp + float(lam @ Hn)
        zf = (zp[t_] / Pp + float(Hn @ Ac[t_])) / info
        P = 1.0 / info
    check = float(np.mean(np.abs(np.corrcoef((Ac - np.outer(zp, lam)).T)[np.triu_indices(A.shape[1], 1)])))
    return zp, z_now, check


def physics_substitute(sim, p, tau=None):
    """the recharge read from the heads: add back the assumed pumping response, deconvolve the assumed head kernel."""
    tau = p['tau_h_assumed'] if tau is None else tau
    g_assumed = sim['g'] * (1.0 + p['gerr'])
    HA = kern(sim['A'], tau)
    Ht = sim['H'] + HA @ g_assumed.T
    a = np.exp(-1.0 / tau)
    X = np.zeros_like(Ht)
    X[1:] = (Ht[1:] - a * Ht[:-1]) / (1 - a)
    X[0] = Ht[0]
    return X                                             # (n, 2): q_m R_t + qL_m Rloc_t + amplified noise


def check_stat(A, W, Xr):
    """largest |t| of the reading Xr in the regressions of each A_j on (W, Xr); Xr already orthogonal to W."""
    Q = np.linalg.qr(W)[0]
    Ar = A - Q @ (Q.T @ A)
    Xr = Xr - Q @ (Q.T @ Xr)
    G = Xr.T @ Xr
    Gi = np.linalg.inv(G)
    b = Gi @ (Xr.T @ Ar)                                 # (2, k)
    e = Ar - Xr @ b
    s2 = np.sum(e ** 2, axis=0) / (len(A) - W.shape[1] - Xr.shape[1])
    t = b / np.sqrt(np.outer(np.diag(Gi), s2))
    return float(np.max(np.abs(t))), float(np.max(np.abs(t[:, 0])))


def ols(y, X, lag=26):
    Xc = np.column_stack([np.ones(len(y)), X])
    XtX = Xc.T @ Xc
    b = np.linalg.solve(XtX, Xc.T @ y)
    u = y - Xc @ b
    S = (Xc * u[:, None]).T @ (Xc * u[:, None])
    for l_ in range(1, lag + 1):
        w = 1 - l_ / (lag + 1)
        G = (Xc[l_:] * u[l_:, None]).T @ (Xc[:-l_] * u[:-l_, None])
        S += w * (G + G.T)
    Xi = np.linalg.inv(XtX)
    V = Xi @ S @ Xi
    return b[1:], V[1:, 1:]


def estimate(sim, p):
    sl = sim['sl']
    A = sim['A']; k = A.shape[1]
    zp, z_now, check = factor_history(A)
    X = physics_substitute(sim, p)
    SA = sim['SA'][sl]; Sf = kern(sim['f'], TAU_S)[sl]
    SZ = np.column_stack([kern(zp, TAU_S)[sl], zp[sl]]); SZn = kern(z_now, TAU_S)[sl]; SX = kern(X, TAU_S, axis=0)[sl]
    zi = np.r_[0.0, p['rho_D'] * sim['D'][:-1]]          # the best history substitute E[D_t | D_1..D_{t-1}]
    SZi = np.column_stack([kern(zi, TAU_S)[sl], zi[sl]])
    Y = sim['Y'][sl]
    # profile the head kernel: the time constant that best explains the salinity (Proposition D4, part ii)
    best = None
    for tau in TAU_GRID:
        SXc = kern(physics_substitute(sim, p, tau), TAU_S, axis=0)[sl]
        Xm = np.column_stack([np.ones(len(Y)), SA, Sf, SXc])
        rss = float(np.sum((Y - Xm @ np.linalg.lstsq(Xm, Y, rcond=None)[0]) ** 2))
        if best is None or rss < best[0]:
            best = (rss, tau, SXc)
    sets = dict(naive=[Sf], tsd=[Sf, SZ], tsd_ideal=[Sf, SZi], tsd_now=[Sf, SZn], phys=[Sf, SX], phys_prof=[Sf, best[2]],
                both=[Sf, SZ, SX], oracle=[sim['SR'][sl], sim['SL'][sl]])
    out = {}
    cond = {}
    for name, extra in sets.items():
        Xm = np.column_stack([SA] + [e.reshape(len(Y), -1) for e in extra])
        Xs = (Xm - Xm.mean(0)) / Xm.std(0)
        cond[name] = float(np.linalg.cond(Xs))            # the static substitute makes the design singular (D'Amour)
        b, V = ols(Y, Xm)
        out[name] = (b[:k], V[:k, :k])
    # Proposition D1: bias of the sum of effects from the second moments after the controls (exchangeable wells)
    d1 = {}
    SD = kern(sim['D'], TAU_S)[sl]
    for name in ('naive', 'tsd', 'tsd_ideal'):
        W = np.column_stack([np.ones(len(Y))] + [e.reshape(len(Y), -1) for e in sets[name]])
        P = np.linalg.lstsq(W, np.column_stack([SD, SA]), rcond=None)[0]
        Rz = np.column_stack([SD, SA]) - W @ P
        C = np.cov(Rz.T)
        sAd = float(np.mean(C[0, 1:])); CA = C[1:, 1:]
        sdiag = float(np.mean(np.diag(CA))); soff = float((CA.sum() - np.trace(CA)) / (k * (k - 1))) if k > 1 else 0.0
        d1[name] = p['rho'] * p['b'] * k * sAd / (sdiag + (k - 1) * soff)
    aS = np.exp(-1.0 / TAU_S)
    vmin = (1 - aS) ** 2 * (1 - p['rho_D'] ** 2)
    ve0 = p['sig_eps'] ** 2 * (1 - aS) / (1 + aS)
    d1['bound'] = k * p['lam'] * p['rho'] * p['b'] * vmin / (ve0 + k * p['lam'] ** 2 * vmin)
    # the Time Series Deconfounder's predictive check (log-likelihood statistic), on the last 20% of the weeks
    nv = len(Y) // 5
    Ah = A[sl][-nv:]; Am = A[sl][:-nv]
    lam_ = np.array([np.polyfit(zp[sl][:-nv], Am[:, j], 1) for j in range(k)])
    s2_ = np.array([np.var(Am[:, j] - np.polyval(lam_[j], zp[sl][:-nv])) for j in range(k)])
    mh = np.column_stack([np.polyval(lam_[j], zp[sl][-nv:]) for j in range(k)])
    Treal = -0.5 * np.sum((Ah - mh) ** 2 / s2_, axis=1)
    rng_ = np.random.default_rng(0)
    Trep = -0.5 * np.sum(rng_.standard_normal((200, nv, k)) ** 2, axis=2)
    pval = float(np.mean(Trep < Treal[None, :]))
    # physics-based check of the substitute: A_tj on Zhat_t, f_t and Rhat_t (all at time t), calibrated by circular time
    # shifts of the reading (they keep the autocorrelation of both series and break any link between them)
    W = np.column_stack([np.ones(len(Y)), zp[sl], sim['f'][sl]])
    Xr0 = X[sl] - W @ np.linalg.lstsq(W, X[sl], rcond=None)[0]
    S0, S10 = check_stat(A[sl], W, Xr0)
    shifts = np.linspace(26, len(Y) - 26, NSHIFT).astype(int)
    Ss = np.array([check_stat(A[sl], W, np.roll(Xr0, sh, axis=0)) for sh in shifts])
    p_chk = (1 + np.sum(Ss[:, 0] >= S0)) / (1 + NSHIFT)
    p_chk1 = (1 + np.sum(Ss[:, 1] >= S10)) / (1 + NSHIFT)
    return out, dict(check=check, p_phys=float(p_chk), p_phys1=float(p_chk1), S_phys=float(S0), cond=cond, d1=d1,
                     pval=pval, tau_hat=best[1])


def run(p, nrep, seed):
    rng = np.random.default_rng(seed)
    beta = geometry(p['k'])[0]
    meanA = p['mu']
    pol = -0.2 * meanA * beta.sum()
    stats = {}
    chk, rej, rej1, conds, d1s, pvals, taus = [], [], [], [], [], [], []
    for _ in range(nrep):
        sim = simulate(rng, p)
        out, c = estimate(sim, p)
        conds.append(c['cond']); d1s.append(c['d1']); pvals.append(c['pval']); taus.append(c['tau_hat'])
        chk.append(c['check']); rej.append(c['p_phys'] <= 0.05); rej1.append(c['p_phys1'] <= 0.05)
        for name, (b, V) in out.items():
            e = b - beta
            pe = -0.2 * meanA * b.sum()
            sp = 0.2 * meanA * np.sqrt(np.ones(p['k']) @ V @ np.ones(p['k']))
            st = stats.setdefault(name, dict(bias=[], b1=[], pol=[], cov=[], cov1=[], se1=[], sumb=[]))
            st['sumb'].append(float(e.sum())); st['bias'].append(e); st['b1'].append(e[0]); st['pol'].append(pe - pol)
            st['cov'].append(abs(pe - pol) <= 1.645 * sp)
            st['cov1'].append(abs(e[0]) <= 1.645 * np.sqrt(V[0, 0])); st['se1'].append(np.sqrt(V[0, 0]))
    res = dict(policy_true=float(pol), beta_true=beta.tolist(), check=float(np.mean(chk)),
               reject=float(np.mean(rej)), reject1=float(np.mean(rej1)),
               cond={m: float(np.median([c_[m] for c_ in conds])) for m in conds[0]},
               d1={m: float(np.mean([c_[m] for c_ in d1s])) for m in d1s[0]},
               tsd_pval=float(np.mean(pvals)), tau_hat=float(np.mean(taus)), tau_hat_sd=float(np.std(taus)),
               naive_limit=float(p['rho'] * p['b'] / p['lam']))
    for name, st in stats.items():
        E = np.array(st['bias'])
        res[name] = dict(rel_bias_pol=float(np.mean(st['pol']) / abs(pol)),
                         rel_rmse_pol=float(np.sqrt(np.mean(np.square(st['pol']))) / abs(pol)),
                         bias_b1=float(np.mean(st['b1'])), rel_bias_b1=float(np.mean(st['b1']) / beta[0]),
                         mean_abs_rel_bias=float(np.mean(np.abs(E.mean(0)) / beta)),
                         bias_sum=float(np.mean(st['sumb'])), sd_sum=float(np.std(st['sumb'])),
                         cover_pol=float(np.mean(st['cov'])), cover_b1=float(np.mean(st['cov1'])),
                         se_b1=float(np.mean(st['se1'])))
    return res


def theory_d4(p):
    """Proposition D4: with drawdown coefficients wrong by gerr, the physics substitute contains gerr*g*(kH*A); the
    predicted bias of beta_j in the large-sample limit is theta . (gerr g_mj) where theta are the outcome coefficients
    of the substitute (here rho/q for the regional logger combination). Returned for well 1 (approximate: kernels
    differ, the factor kS*kH vs kS is ignored)."""
    beta, g, q, qL = geometry(p['k'])
    # the oracle uses kS*R; the substitute X_m ~ q_m R + qL_m Rloc + gerr * g_m (A at the head kernel, deconvolved = A_t)
    # solve for the weights w on (X_1, X_2) that reproduce -rho R - rho_L Rloc:  w @ [q; qL] = [-rho, -rho_L]
    M = np.array([q, qL])
    w = np.linalg.solve(M, np.array([-p['rho'], -p['rho_L']]))
    return float(-(w @ (p['gerr'] * g[:, 0])))           # bias of beta_1: the substitute's share of the pumping term


def main():
    t0 = time.time()
    os.makedirs(RES, exist_ok=True)
    out = dict(nrep=NREP, T=T, base=BASE, T29={}, T30={}, T31={}, T32={})
    only32 = 'T32' in sys.argv[1:]
    if only32:                                           # re-run the checks alone, keep T29-T31 of the last full run
        with open(os.path.join(RES, 'fshehta.json')) as fh:
            out = json.load(fh)
        out['T32'] = {}
    M = ('naive', 'tsd', 'tsd_ideal', 'tsd_now', 'phys', 'phys_prof', 'both', 'oracle')
    if not only32:
        t29_t31(out, M, t0)
    t32(out, t0)
    finish(out, t0, only32)


def t29_t31(out, M, t0):
    # T29: number of wells, persistent and fast dryness (Proposition D1)
    for rho_D in (0.98, 0.9, 0.5):
        for k in (2, 4, 8, 16, 32, 64):
            p = dict(BASE, k=k, rho_D=rho_D)
            r = run(p, NREP if k <= 16 else NREP // 2, seed=29 + k + int(100 * rho_D))
            out['T29'][f'{rho_D}_{k}'] = r
            log(f'T29 rho_D={rho_D} k={k:2d}: bias of the sum of effects ' +
                ' '.join(f'{m} {r[m]["bias_sum"]:+.3f}' for m in ('naive', 'tsd', 'tsd_ideal', 'phys', 'oracle')) +
                f' | D1 naive {r["d1"]["naive"]:+.3f} tsd {r["d1"]["tsd"]:+.3f} ideal {r["d1"]["tsd_ideal"]:+.3f}'
                f' closed form {r["d1"]["bound"]:+.3f}'
                f' limit {r["naive_limit"]:.2f} | rel policy bias tsd {r["tsd"]["rel_bias_pol"]:+.3f} phys '
                f'{r["phys"]["rel_bias_pol"]:+.3f} | cond tsd_now {r["cond"]["tsd_now"]:.1e} | TSD check p {r["tsd_pval"]:.2f}'
                f' | physics check rejects {r["reject"]:.2f}  [{time.time() - t0:.0f}s]')
    # T30: a single-cause hidden confounder at well 1
    for psi in (0.0, 0.5, 1.0):
        p = dict(BASE, psi=psi, rho_D=0.98, k=8)
        r = run(p, NREP, seed=300 + int(10 * psi))
        out['T30'][str(psi)] = r
        log(f'T30 psi={psi}: rel bias of beta_1 ' + ' '.join(f'{m} {r[m]["rel_bias_b1"]:+.3f}' for m in M)
            + f' | cover beta_1 tsd {r["tsd"]["cover_b1"]:.2f} phys {r["phys"]["cover_b1"]:.2f} oracle '
              f'{r["oracle"]["cover_b1"]:.2f} | rel policy bias tsd {r["tsd"]["rel_bias_pol"]:+.3f} | check rejects '
              f'{r["reject"]:.2f} (well 1: {r["reject1"]:.2f})  [{time.time() - t0:.0f}s]')
    # T31: wrong physics
    for gerr in (-0.3, -0.15, 0.0, 0.15, 0.3):
        p = dict(BASE, gerr=gerr, rho_D=0.9, k=8)
        r = run(p, NREP // 2, seed=310 + int(100 * gerr))
        r['d4_pred_b1'] = theory_d4(p)
        out['T31'][f'g{gerr}'] = r
        log(f'T31 gerr={gerr:+.2f}: phys bias beta_1 {r["phys"]["bias_b1"]:+.4f} (D4 predicts '
            f'{r["d4_pred_b1"]:+.4f}), rel policy bias phys {r["phys"]["rel_bias_pol"]:+.3f} prof '
            f'{r["phys_prof"]["rel_bias_pol"]:+.3f} (tau_hat {r["tau_hat"]:.2f})  [{time.time() - t0:.0f}s]')
    for terr in (0.6, 0.8, 1.25, 1.5):
        p = dict(BASE, tau_h_assumed=TAU_H * terr, rho_D=0.9, k=8)
        r = run(p, NREP // 2, seed=320 + int(10 * terr))
        out['T31'][f't{terr}'] = r
        log(f'T31 head kernel x{terr}: rel policy bias phys {r["phys"]["rel_bias_pol"]:+.3f} prof '
            f'{r["phys_prof"]["rel_bias_pol"]:+.3f} (tau_hat {r["tau_hat"]:.2f} +- {r["tau_hat_sd"]:.2f}), beta_1 phys '
            f'{r["phys"]["rel_bias_b1"]:+.3f} prof {r["phys_prof"]["rel_bias_b1"]:+.3f}  [{time.time() - t0:.0f}s]')


def t32(out, t0):
    # T32: the checks under no confounding, multi-cause, single-cause, wrong physics
    scen = dict(none=dict(b=0.0), multi_slow=dict(rho_D=0.98), multi_fast=dict(rho_D=0.5),
                single=dict(b=0.0, psi=1.0), wrong_phys=dict(b=0.0, gerr=0.3))
    for name, ch in scen.items():
        p = dict(BASE, k=8, **ch)
        r = run(p, NREP, seed=330 + len(name))
        out['T32'][name] = r
        log(f'T32 {name:10s}: physics check rejects {r["reject"]:.3f} (well 1 {r["reject1"]:.3f}); TSD predictive check '
            f'p {r["tsd_pval"]:.2f}; rel bias policy tsd {r["tsd"]["rel_bias_pol"]:+.3f} phys {r["phys"]["rel_bias_pol"]:+.3f}'
            f'; beta_1 tsd {r["tsd"]["rel_bias_b1"]:+.3f} phys {r["phys"]["rel_bias_b1"]:+.3f}  [{time.time() - t0:.0f}s]')


def finish(out, t0, only32=False):
    # one case for the figures
    rng = np.random.default_rng(11)
    sim = simulate(rng, dict(BASE, rho_D=0.9))
    zp, z_now, _ = factor_history(sim['A'])
    X = physics_substitute(sim, BASE)
    sl = sim['sl']
    np.savez_compressed(os.path.join(RES, 'fshehta_case.npz'), D=sim['D'][sl], R=sim['R'][sl], zp=zp[sl], z_now=z_now[sl],
                        X=X[sl], A=sim['A'][sl], Y=sim['Y'][sl], H=sim['H'][sl], f=sim['f'][sl])
    out['seconds'] = time.time() - t0
    tag = '_quick' if QUICK else ''
    with open(os.path.join(RES, f'fshehta{tag}.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    logf = os.path.join(RES, f'fshehta{tag}_log.txt')
    keep = []
    if only32 and os.path.exists(logf):                  # keep the T29-T31 lines of the last full run
        with open(logf) as fh:
            keep = [ln.rstrip('\n') for ln in fh if ln.startswith(('T29', 'T30', 'T31'))]
    with open(logf, 'w') as fh:
        fh.write('\n'.join(keep + LOG) + '\n')
    log(f'done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
