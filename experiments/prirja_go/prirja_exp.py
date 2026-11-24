"""PRIRJA-GO: guarantees when the real law drifts over the years.

Anchors are past years t = 1..K (one measured year each: a tide-gauge year, a lysimeter year, a gauged inflow year);
the field is a future year K + h. The real law Q_t drifts with t; the simulator's law is Q_0.
Test bed: that of reviews I-IV (32 cells x 64 weeks, ensemble smoother with the exact solver, 128 members, four
loggers at 0.25, 1.25, 2.75, 4.25 km).
Drift laws (sea-level mean, inland-inflow mean, recharge-coefficient median, vadose delay; the simulator keeps
14 d and the year-0 means):
  none     no drift
  linear   +5 mm/yr, -0.01 m2/d per yr, x exp(-0.01 t), +0.42 d/yr  (at t = 50: +0.25 m, -0.5 m2/d, x 0.61, 35 d)
  accel    the same values at t = 50, reached quadratically: x (t/50)^2
  step     no sea-level drift; from year 24 (a new well field lowers the water table) the inflow mean drops by
           0.5 m2/d, the coefficient by 25% and the delay jumps to 28 d
Methods (90% bands, conformal risk control on the share of weeks outside; scores u = (truth - m) / s):
  sims       lambda from 300 simulated aquifers (Q_0)
  all        all K anchors, unweighted
  recent     the last 9 anchors (the fewest that give a finite band)
  decay      weights rho^(K - t), rho = 0.9 (weighted conformal beyond exchangeability)
  loc0       horizon-matched, location only, degree 0: the score of year o + h is |u - c_o| with c_o the mean of
             u-bar over years o-L+1..o (L = 5); the band is re-centred by c_K (an ablation)
  ls0        horizon-matched location-scale, degree 0 (L = 5): the score is |u - c_o| / sigma_o, sigma_o the spread of
             the same window (within-year RMS for weekly goals, residual sd of the window fit for kappa); the band is
             m + s (c_K +- lambda sigma_K)
  ls1        the same with a straight line fitted over L = 10 years and extrapolated h years (degree 1)
Horizons h = 1, 3, 5, 10, 15, 20; 150 field cases per target year; 20 anchor candidates per past year; every
score averages 300 draws of one anchor per year.

usage: python prirja_exp.py   (writes res/prirja.json and res/prirja_log.txt)"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ankora_go'))
import ankora_exp as AX  # noqa: E402
from ankora_exp import M, G  # noqa: E402

RES = os.path.join(HERE, 'res')
ALPHA = 0.10
GOALS = AX.GOALS
K = 30
NA = 20
HS = (1, 3, 5, 10, 15, 20)
N_TEST = 150
N_SIM = 300
REPS = 300
RHO = 0.9
W_RECENT = int(np.ceil((1 - ALPHA) / ALPHA))          # 9
L_LEVEL, L_TREND = 5, 10
T_STEP = 24
LAWS = ('none', 'linear', 'accel', 'step')
METHODS = ('sims', 'all', 'recent', 'decay', 'loc0', 'ls0', 'ls1')
MATCHED = (('loc0', L_LEVEL, 0, False), ('ls0', L_LEVEL, 0, True), ('ls1', L_TREND, 1, True))
LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.append(s)


def drift(law, t):
    """(sea-level offset m, inflow offset m2/d, factor on the recharge-coefficient median, vadose delay d) in year t."""
    if law == 'none':
        return 0.0, 0.0, 1.0, M.TAU_V
    if law == 'linear':
        return 0.005 * t, -0.01 * t, float(np.exp(-0.01 * t)), M.TAU_V + 0.42 * t
    if law == 'accel':
        s = (t / 50.0) ** 2
        return 0.25 * s, -0.5 * s, float(np.exp(-0.5 * s)), M.TAU_V + 21.0 * s
    if law == 'step':
        on = t >= T_STEP
        return 0.0, (-0.5 if on else 0.0), (0.75 if on else 1.0), (28.0 if on else M.TAU_V)
    raise ValueError(law)


class DBed(AX.QBed):
    def case_t(self, rng, law, t):
        Pd = G.daily_rain(rng)
        de, dq, kf, tau = drift(law, t)
        f = G.filtered(Pd, tau)
        fo = G.filtered(Pd, M.TAU_V)
        z = self.mu + self.L @ rng.standard_normal(M.NZ)
        z[M.SL['meta']] += de
        z[M.SL['mq']] += dq
        kap = np.exp(np.log(M.KAP_MED * kf) + M.KAP_LSD * rng.standard_normal())
        gk = M.kappa_response(f)
        tr = M.fields_from_z(z[:, None], np.array([kap]), f, self.G, self.cQ, gk)
        return dict(f=f, fo=fo, Po=Pd, gko=M.kappa_response(fo), b=1.0, src='true', beff=1.0,
                    kappa=kap, h=tr['h'][0], eta=tr['eta'][0], qL=tr['qL'][0], r=tr['r'][0],
                    eh=M.SIG_H * rng.standard_normal((M.NX, M.NT)), ee=M.SIG_ETA * rng.standard_normal(M.NT),
                    seed=int(rng.integers(2 ** 31)))


def signed(bed, cases):
    """signed standardised errors u (n, T) and mean scale s (n,) per goal."""
    out = AX.run(bed, cases)
    U = {k: np.array([(c['t'][k] - c['m'][k]) / c['s'][k] for c in out]) for k in GOALS}
    S = {k: np.array([np.mean(c['s'][k]) for c in out]) for k in GOALS}
    return U, S


def crc_w(Sa, w):
    """weighted conformal risk control (B = 1, test weight 1): the smallest lambda with
    (sum_j w_j L_j(lambda) + 1) / (sum_j w_j + 1) <= alpha; L_j = share of the T scores of anchor j above lambda."""
    m, T = Sa.shape
    budget = ALPHA * (w.sum() + 1.0) - 1.0
    if budget < 0:
        return np.inf
    v = Sa.ravel(); wt = np.repeat(w / T, T)
    o = np.argsort(-v)
    cum = np.cumsum(wt[o])
    j = np.searchsorted(cum, budget, side='right')
    return float(v[o][j]) if j < len(v) else 0.0


def poly_pred(ub, years, deg, at):
    """least-squares polynomial of degree deg through (years, ub), evaluated at 'at'."""
    if deg == 0:
        return float(np.mean(ub))
    c = np.polyfit(years, ub, deg)
    return float(np.polyval(c, at))


def window_stats(A, ub, yrs, win, deg, at):
    """centre (degree-deg least-squares fit of u-bar over the window, evaluated at 'at') and spread of a window."""
    c = poly_pred(ub[win], yrs[win], deg, at)
    if A.shape[1] > 1:                                  # weekly goals: within-year RMS deviation
        sc = float(np.sqrt(np.mean((A[win] - ub[win][:, None]) ** 2)))
    else:                                               # scalar goal: residual sd of the window fit
        x, yv = yrs[win], ub[win]
        fit = np.full_like(yv, yv.mean()) if deg == 0 else np.polyval(np.polyfit(x, yv, deg), x)
        sc = float(np.sqrt(np.sum((yv - fit) ** 2) / (len(yv) - deg - 1)))
    return c, sc


def horizon_matched(A, h, L, deg, scale):
    """calibration scores and the deployment centre and spread of horizon-matched calibration.
    A: (K, T) signed scores of the anchors of years 1..K. Origins o = L..K-h (years are 1-based); the score of
    origin o is |u_{o+h} - c_o| / sigma_o (sigma_o = 1 without scale)."""
    ub = A.mean(1)
    yrs = np.arange(1, K + 1)
    rows = []
    for o in range(L, K - h + 1):
        c, sc = window_stats(A, ub, yrs, slice(o - L, o), deg, o + h)
        rows.append(np.abs(A[o + h - 1] - c) / (sc if scale else 1.0))
    c_dep, sc_dep = window_stats(A, ub, yrs, slice(K - L, K), deg, K + h)
    return (np.array(rows) if rows else np.zeros((0, A.shape[1]))), c_dep, (sc_dep if scale else 1.0)


def horizon_max(L, n_min=W_RECENT):
    return K - L - n_min + 1


def main():
    t0 = time.time()
    os.makedirs(RES, exist_ok=True)
    bed = DBed()
    rng = np.random.default_rng(1505)
    Us, _ = signed(bed, [bed.case_t(rng, 'none', 0) for _ in range(N_SIM)])
    lam_s = {k: AX.crc_exact(np.abs(Us[k]), np.abs(Us[k])[:0], 1.0) for k in GOALS}
    log(f'simulations ready [{time.time() - t0:.0f}s]')
    out = dict(alpha=ALPHA, K=K, na=NA, hs=HS, n_test=N_TEST, n_sim=N_SIM, reps=REPS, rho=RHO, w_recent=W_RECENT,
               l_level=L_LEVEL, l_trend=L_TREND, t_step=T_STEP, methods=METHODS,
               h_max={'0': horizon_max(L_LEVEL), '1': horizon_max(L_TREND)},
               h_cert={'0': horizon_max(L_LEVEL, 22), '1': horizon_max(L_TREND, 22)},
               drift={law: {str(t): drift(law, t) for t in (0, 10, 20, 30, 40, 50)} for law in LAWS}, res={})
    rs = np.random.default_rng(2606)
    for law in LAWS:
        Ua = {k: np.zeros((K, NA, 1 if k == 'kappa' else M.NT)) for k in GOALS}
        for t in range(1, K + 1):
            U, _ = signed(bed, [bed.case_t(rng, law, t) for _ in range(NA)])
            for k in GOALS:
                Ua[k][t - 1] = U[k]
        Ut, St = {k: [] for k in GOALS}, {k: [] for k in GOALS}
        for h in HS:
            U, S = signed(bed, [bed.case_t(rng, law, K + h) for _ in range(N_TEST)])
            for k in GOALS:
                Ut[k].append(U[k]); St[k].append(S[k])
        log(f'{law}: cases ready [{time.time() - t0:.0f}s]')
        R = {}
        for k in GOALS:
            acc = {mth: {h: ([], []) for h in HS} for mth in METHODS}
            for h_i, h in enumerate(HS):
                Tt, sbar = Ut[k][h_i], St[k][h_i].mean()
                acc['sims'][h][0].append(float(np.mean(np.abs(Tt) > lam_s[k])))
                acc['sims'][h][1].append(lam_s[k] * sbar)
            ub_trace = []
            for _ in range(REPS):
                pick = rs.integers(NA, size=K)
                A = Ua[k][np.arange(K), pick]                  # (K, T)
                ub_trace.append(A.mean(1))
                yrs = np.arange(1, K + 1)
                lam = {'all': crc_w(np.abs(A), np.ones(K)),
                       'recent': crc_w(np.abs(A[-W_RECENT:]), np.ones(W_RECENT)),
                       'decay': crc_w(np.abs(A), RHO ** (K - yrs))}
                for h_i, h in enumerate(HS):
                    Tt, sbar = Ut[k][h_i], St[k][h_i].mean()
                    for mth in ('all', 'recent', 'decay'):
                        acc[mth][h][0].append(float(np.mean(np.abs(Tt) > lam[mth])))
                        acc[mth][h][1].append(lam[mth] * sbar)
                    for mth, L, deg, scale in MATCHED:
                        Sc, c, sc = horizon_matched(A, h, L, deg, scale)
                        lm = crc_w(Sc, np.ones(len(Sc))) if len(Sc) else np.inf
                        acc[mth][h][0].append(float(np.mean(np.abs(Tt - c) > lm * sc)))
                        acc[mth][h][1].append(lm * sc * sbar)
            res = {}
            for mth in METHODS:
                res[mth] = {}
                for h in HS:
                    r_, w_ = np.array(acc[mth][h][0]), np.array(acc[mth][h][1])
                    fin = np.isfinite(w_)
                    res[mth][str(h)] = dict(risk=float(r_.mean()),
                                            risk_p90=float(np.percentile(r_, 90)),
                                            halfwidth=float(w_[fin].mean()) if fin.any() else None,
                                            finite=float(fin.mean()))
            ubm = np.mean(ub_trace, axis=0)
            res['ubar_by_year'] = [float(v) for v in ubm]
            res['ubar_test'] = [float(Ut[k][h_i].mean()) for h_i in range(len(HS))]
            R[k] = res
            log(f'{law:6s} {k:5s} ' + ' | '.join(
                f'{mth} ' + ' '.join(f'{res[mth][str(h)]["risk"]:.3f}' for h in HS) for mth in METHODS) +
                f'  [{time.time() - t0:.0f}s]')
        out['res'][law] = R
    out['seconds'] = time.time() - t0
    with open(os.path.join(RES, 'prirja.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    with open(os.path.join(RES, 'prirja_log.txt'), 'w') as fh:
        fh.write('\n'.join(LOG) + '\n')
    log(f'done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
