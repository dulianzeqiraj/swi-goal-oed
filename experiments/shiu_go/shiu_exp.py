"""SHIU-GO experiments E1-E3 on the synthetic coastal aquifer of shiu_model.py.

E1  Route A: the recharge as a separate jump SDE (rain -> soil bucket -> Erlang vadose delay -> multiplicative OU
    error) whose law is discovered by minimising the forecast loss of Krach, Nubel & Teichmann (SPA 2026) on six
    training years of irregular, incomplete head data; compared with the Gaussian forcing of the data-assimilation
    note (M0: constant mean + OU anomaly), a linear rain transfer (M1) and the true law (oracle).
E2  Route B: the forcing as a term added to the flow equation, expanded on a library of rain-driven features plus
    seasonal terms that are not causes; selection by least squares, by best subset (BIC) and by environment
    invariance across wet, normal and dry years (EILLS objective, exact by enumeration). Identifiability of a
    multiplicative recharge error against a uniform closure source.
E3  Forecast error against the time since the last head observation, on the four test years (one a drought).

usage: python shiu_exp.py [NSEED] [OUT_NAME]   (writes res/shiu_exp.json and prints a log)"""
import itertools
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shiu_model as SM  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
GAPS = ((0, 3), (3, 7), (7, 14), (14, 10 ** 6))
FEATS = ('P5', 'P20', 'P60', 'P180', 'E20', 'X40', 'cos', 'sin', 'one')
CAUSAL = ('P5', 'P20', 'P60', 'P180', 'E20', 'X40')
GAMMAS = (1.0, 4.0, 16.0)


def sigm(u):
    return 1.0 / (1.0 + np.exp(-u))


# ------------------------------------------------------------------------------------------------ rain law (route A)
def fit_rain_law(P, t):
    """Maximum likelihood for the compound Poisson daily rain: N ~ Poisson(lam(t)), depths Exp(abar(t)),
    log lam and log abar with annual harmonics (phase free)."""
    from scipy.special import gammaln
    c, s = np.cos(SM.OMEGA * (t - 15.0)), np.sin(SM.OMEGA * (t - 15.0))
    wet = P > 0
    K = np.arange(1, 9)

    def nll(u):
        lam = np.exp(u[0] + u[1] * c + u[2] * s)
        ab = np.exp(u[3] + u[4] * c + u[5] * s)
        l0 = -lam[~wet]
        x, lw, aw = P[wet][:, None], lam[wet][:, None], ab[wet][:, None]
        lk = (-lw + K * np.log(lw) - gammaln(K + 1) + (K - 1) * np.log(x) - x / aw - K * np.log(aw) - gammaln(K))
        m = lk.max(1, keepdims=True)
        l1 = (m[:, 0] + np.log(np.exp(lk - m).sum(1)))
        return -(l0.sum() + l1.sum())
    u0 = np.array([np.log(wet.mean() + 1e-3), 0.0, 0.0, np.log(P[wet].mean()), 0.0, 0.0])
    r = minimize(nll, u0, method='Nelder-Mead', options=dict(maxiter=4000, xatol=1e-5, fatol=1e-6))
    return r.x


# ------------------------------------------------------------------------------------------------ route B features
def features(P, Ep, t):
    f = {'P5': SM.erlang2(P, 2.5), 'P20': SM.erlang2(P, 10.0), 'P60': SM.erlang2(P, 30.0),
         'P180': SM.erlang2(P, 90.0), 'E20': SM.erlang2(Ep, 10.0),
         'X40': SM.erlang2(np.maximum(SM.erlang2(P, 5.0) - Ep, 0.0), 20.0),
         'cos': np.cos(SM.OMEGA * (t - 15.0)), 'sin': np.sin(SM.OMEGA * (t - 15.0)), 'one': np.ones_like(t)}
    return f


def eills(Xs, y, env, S, gamma):
    """EILLS objective of Fan, Fang, Gu & Zhang (2024) restricted to the support S, minimised exactly (quadratic):
    sum_e mean_e r^2 + gamma sum_e |mean_e(r x_S)|^2."""
    A = np.zeros((len(S), len(S))); b = np.zeros(len(S)); const = 0.0
    parts = []
    for e in np.unique(env):
        w = env == e
        Xe, ye = Xs[w][:, S], y[w]
        Se, ue = Xe.T @ Xe / w.sum(), Xe.T @ ye / w.sum()
        A += Se + gamma * Se @ Se
        b += ue + gamma * Se @ ue
        parts.append((Se, ue, float(ye @ ye / w.sum())))
    beta = np.linalg.solve(A + 1e-12 * np.eye(len(S)), b)
    Q = sum(yy - 2 * ue @ beta + beta @ Se @ beta + gamma * np.sum((ue - Se @ beta) ** 2) for Se, ue, yy in parts)
    return beta, float(Q)


def select_routeB(Xs, y, env):
    n, K = Xs.shape
    subsets = [list(c) for k in range(1, K + 1) for c in itertools.combinations(range(K), k)]
    full = np.linalg.lstsq(Xs, y, rcond=None)[0]
    s2 = float(np.mean((y - Xs @ full) ** 2))
    best_bic, best_S = np.inf, None
    for S in subsets:
        b = np.linalg.lstsq(Xs[:, S], y, rcond=None)[0]
        rss = float(np.sum((y - Xs[:, S] @ b) ** 2))
        bic = n * np.log(rss / n) + len(S) * np.log(n)
        if bic < best_bic:
            best_bic, best_S, best_b = bic, S, b
    out = {'ls': (list(range(K)), full), 'bic': (best_S, best_b)}
    ne = len(np.unique(env))
    lam = ne * s2 * np.log(n) / n
    for g in GAMMAS:
        bestQ, bS = np.inf, None
        for S in subsets:
            b, Q = eills(Xs, y, env, S, g)
            Q += lam * len(S)
            if Q < bestQ:
                bestQ, bS, bb = Q, S, b
        out[f'eills{int(g)}'] = (bS, bb)
    return out


# ------------------------------------------------------------------------------------------------ metrics
def monthly(x, lo, hi):
    x = x[lo:hi]
    m = (hi - lo) // 30
    return x[:m * 30].reshape(m, 30).mean(1)


def rech_metrics(Rhat, R):
    lo, hi = SM.TEST
    a, b = monthly(Rhat, lo, hi), monthly(R, lo, hi)
    d0, d1 = SM.DROUGHT
    return dict(corr_month=float(np.corrcoef(a, b)[0, 1]), rmse_month=float(np.sqrt(np.mean((a - b) ** 2))),
                drought_total=float(Rhat[d0:d1].sum()), drought_true=float(R[d0:d1].sum()),
                test_total=float(Rhat[lo:hi].sum()), test_true=float(R[lo:hi].sum()))


def summary(r, tw, ref=None):
    out = dict(train=SM.window(r, *SM.TRAIN), test=SM.window(r, *SM.TEST), drought=SM.window(r, *SM.DROUGHT))
    lo, hi = SM.TEST
    w = (r['day'] >= lo) & (r['day'] < hi)
    per = r['sse'][w] / r['nob'][w]
    out['gap'] = [float(per[(r['gap'][w] > a) & (r['gap'][w] <= b)].mean()) for a, b in GAPS]
    out['gap_n'] = [int(((r['gap'][w] > a) & (r['gap'][w] <= b)).sum()) for a, b in GAPS]
    if ref is not None:
        d = ((ref['nu'][w] - r['nu'][w]) ** 2).sum(1)
        out['dist_to_oracle'] = float(d.mean())
    return out


# ------------------------------------------------------------------------------------------------ one twin
def run_seed(seed):
    t0 = time.time()
    aq = SM.aquifer()
    tw = SM.simulate_twin(seed, aq)
    t, P, Ep = tw['t'], tw['P'], tw['Ep']
    n = len(t)
    res = dict(seed=seed)
    tr = lambda r: SM.window(r, *SM.TRAIN)['loss']

    # oracle
    ro = SM.run_filter(aq, tw, tw['Rdet'], 'mult', SM.TRUE['sig_e'], SM.TRUE['tau_e'])
    res['oracle'] = summary(ro, tw)
    res['oracle']['rech'] = rech_metrics(tw['Rdet'] * (1 + ro['xm']), tw['R'])

    # rain law from the gauge (years 0-8)
    cut = SM.TEST[0]
    res['rain_law'] = fit_rain_law(P[:cut], t[:cut]).tolist()

    # M0: Gaussian forcing (constant mean + OU anomaly), as in the data-assimilation note
    def f0(u):
        return tr(SM.run_filter(aq, tw, np.full(n, u[0]), 'add', np.exp(u[1]), np.exp(u[2])))
    o0 = minimize(f0, [1.0, np.log(0.5), np.log(30.0)], method='Nelder-Mead',
                  options=dict(maxiter=400, xatol=1e-4, fatol=1e-10, adaptive=True))
    u = o0.x
    r0 = SM.run_filter(aq, tw, np.full(n, u[0]), 'add', np.exp(u[1]), np.exp(u[2]))
    res['M0'] = summary(r0, tw, ro)
    res['M0']['par'] = dict(Rbar=float(u[0]), sig=float(np.exp(u[1])), tau=float(np.exp(u[2])))
    res['M0']['rech'] = rech_metrics(u[0] + r0['xm'], tw['R'])
    sig_rho, tau_rho = float(np.exp(u[1])), float(np.exp(u[2]))

    # M1: linear rain transfer + OU
    def r1_of(u):
        Rd = u[0] + u[1] * SM.erlang2(P, np.exp(u[2]))
        return SM.run_filter(aq, tw, Rd, 'add', np.exp(u[3]), np.exp(u[4])), Rd
    o1 = minimize(lambda u: tr(r1_of(u)[0]), [0.0, 0.4, np.log(15.0), np.log(0.5), np.log(30.0)],
                  method='Nelder-Mead', options=dict(maxiter=800, xatol=1e-4, fatol=1e-10, adaptive=True))
    r1, Rd1 = r1_of(o1.x)
    res['M1'] = summary(r1, tw, ro)
    res['M1']['par'] = dict(c=float(o1.x[0]), alpha=float(o1.x[1]), tau1=float(np.exp(o1.x[2])),
                            sig=float(np.exp(o1.x[3])), tau=float(np.exp(o1.x[4])))
    res['M1']['rech'] = rech_metrics(Rd1 + r1['xm'], tw['R'])

    # Route A: the jump SDE forcing (bucket + threshold drainage + Erlang-2 delay + multiplicative OU)
    sb, sw = SM.SOIL_KNOWN['sbar'], SM.SOIL_KNOWN['sw']

    def par2(u):
        return dict(sfc=sw + (sb - sw) * sigm(u[0]), kL=np.exp(u[1]), bL=1.0 + np.exp(u[2]), tau=np.exp(u[3]),
                    sig_e=np.exp(u[4]), tau_e=np.exp(u[5]))

    def r2_of(u):
        p = par2(u)
        Rd = SM.recharge_det(P, Ep, p['sfc'], p['kL'], p['bL'], p['tau'], nsub=6)[0]
        return SM.run_filter(aq, tw, Rd, 'mult', p['sig_e'], p['tau_e']), Rd
    starts = ([0.5, np.log(10.0), np.log(1.0), np.log(8.0), np.log(0.1), np.log(30.0)],
              [-1.0, np.log(40.0), np.log(3.0), np.log(40.0), np.log(0.4), np.log(200.0)])
    best = None
    for s0 in starts:
        o = minimize(lambda u: tr(r2_of(u)[0]), s0, method='Nelder-Mead',
                     options=dict(maxiter=1500, xatol=1e-4, fatol=1e-10, adaptive=True))
        if best is None or o.fun < best.fun:
            best = o
    r2, Rd2 = r2_of(best.x)
    res['A'] = summary(r2, tw, ro)
    res['A']['par'] = {k: float(v) for k, v in par2(best.x).items()}
    res['A']['rech'] = rech_metrics(Rd2 * (1 + r2['xm']), tw['R'])
    res['A']['nfev'] = int(best.nfev)

    # Route B: augmentation of the flow equation with a library, gains from the M0 noise model
    rB = SM.run_filter(aq, tw, np.zeros(n), 'add', sig_rho, tau_rho, store_gain=True)
    f = features(P, Ep, t)
    G = np.stack([SM.kf_response(aq['F'], aq['g_r'], np.outer(f[k] / 1000.0, aq['g_r']), rB['bx'], rB['phi'],
                                 aq['H'], tw['mask'], rB['K'], np.zeros(aq['N'])) for k in FEATS], -1)
    evm = tw['mask'][rB['day']]                                   # observed coordinates per event
    ytr_w = (rB['day'] >= SM.TRAIN[0]) & (rB['day'] < SM.TRAIN[1])
    yte_w = (rB['day'] >= SM.TEST[0]) & (rB['day'] < SM.TEST[1])
    sel = evm & ytr_w[:, None]
    y = rB['nu'][sel]
    X = G[sel]
    env = SM.ENV[(rB['day'][:, None] * np.ones_like(evm, dtype=int) // SM.YEAR)[sel]]
    scale = X.std(0) + 1e-12
    Xs = X / scale
    fits = select_routeB(Xs, y, env)
    res['B'] = {}
    for name, (S, b) in fits.items():
        beta = np.zeros(len(FEATS)); beta[S] = np.asarray(b) / scale[S]
        nu_te = rB['nu'] - (G * beta).sum(-1)
        nu_te = np.where(evm, nu_te, 0.0)
        sse = (nu_te ** 2).sum(1)
        Rd = sum(beta[i] * f[k] for i, k in enumerate(FEATS))
        rr = SM.run_filter(aq, tw, Rd, 'add', sig_rho, tau_rho)
        d0, d1 = SM.DROUGHT
        wd = (rB['day'] >= d0) & (rB['day'] < d1)
        res['B'][name] = dict(support=[FEATS[i] for i in S], beta=beta.tolist(),
                              train=float(sse[ytr_w].mean()), test=float(sse[yte_w].mean()),
                              drought=float(sse[wd].mean()), test_cov=SM.window(rr, *SM.TEST)['cov'],
                              rech=rech_metrics(Rd + rr['xm'], tw['R']))

    # identifiability of a multiplicative recharge error against a uniform closure (open-loop responses)
    K0 = np.zeros_like(rB['K'])

    def resp(u):
        g = SM.kf_response(aq['F'], aq['g_r'], np.outer(u / 1000.0, aq['g_r']), rB['bx'], rB['phi'], aq['H'],
                           tw['mask'], K0, np.zeros(aq['N']))
        return g[sel]
    def resp_cl(u):
        g = SM.kf_response(aq['F'], aq['g_r'], np.outer(u / 1000.0, aq['g_r']), rB['bx'], rB['phi'], aq['H'],
                           tw['mask'], rB['K'], np.zeros(aq['N']))
        return g[sel]
    chi = np.zeros(aq['N']); chi[:5] = 1.0                       # a closure confined to the first kilometre
    g_coast = (aq['F'] / aq['Sy']) @ chi
    gco = SM.kf_response(aq['F'], aq['g_r'], np.outer(np.ones(n) / 1000.0, g_coast), rB['bx'], rB['phi'], aq['H'],
                         tw['mask'], K0, np.zeros(aq['N']))[sel]
    g_c, g_m = resp(np.ones(n)), resp(tw['Rdet'])
    cosf = lambda a, b: float(a @ b / np.sqrt((a @ a) * (b @ b)))
    res['ident'] = dict(cos_mult_vs_closure=cosf(g_c, g_m), cos_const_vs_closure=1.0,
                        cos_mult_vs_closure_cl=cosf(resp_cl(np.ones(n)), resp_cl(tw['Rdet'])),
                        cos_mult_vs_coastal=cosf(gco, g_m), cos_P60_vs_closure=cosf(g_c, resp(f['P60'])))
    res['time_s'] = round(time.time() - t0, 1)
    return res


def agg(vals):
    v = np.asarray(vals, float)
    return dict(med=float(np.median(v)), q25=float(np.percentile(v, 25)), q75=float(np.percentile(v, 75)))


def main(nseed=12, out='shiu_exp.json'):
    os.makedirs(RES, exist_ok=True)
    seeds = [101 + i for i in range(nseed)]
    t0 = time.time()
    with Pool(4) as pool:
        runs = pool.map(run_seed, seeds)
    print(f'{nseed} twins in {time.time() - t0:.0f} s')
    S = {}
    for m in ('oracle', 'M0', 'M1', 'A'):
        S[m] = {k: agg([r[m][k]['loss'] for r in runs]) for k in ('train', 'test', 'drought')}
        S[m]['test_cov'] = agg([r[m]['test']['cov'] for r in runs])
        S[m]['test_nll'] = agg([r[m]['test']['nll'] for r in runs])
        S[m]['gap'] = [agg([r[m]['gap'][i] for r in runs]) for i in range(len(GAPS))]
        for k in ('corr_month', 'rmse_month'):
            S[m][k] = agg([r[m]['rech'][k] for r in runs])
        S[m]['drought_rel_err'] = agg([r[m]['rech']['drought_total'] / r[m]['rech']['drought_true'] - 1 for r in runs])
        if m != 'oracle':
            S[m]['dist'] = agg([r[m]['dist_to_oracle'] for r in runs])
            S[m]['excess_rel'] = agg([r[m]['test']['loss'] / r['oracle']['test']['loss'] - 1 for r in runs])
    S['A_par'] = {k: agg([r['A']['par'][k] for r in runs]) for k in runs[0]['A']['par']}
    S['B'] = {}
    for name in runs[0]['B']:
        S['B'][name] = {k: agg([r['B'][name][k] for r in runs]) for k in ('train', 'test', 'drought', 'test_cov')}
        S['B'][name]['corr_month'] = agg([r['B'][name]['rech']['corr_month'] for r in runs])
        S['B'][name]['drought_rel_err'] = agg([r['B'][name]['rech']['drought_total'] /
                                               r['B'][name]['rech']['drought_true'] - 1 for r in runs])
        S['B'][name]['test_rel_oracle'] = agg([r['B'][name]['test'] / r['oracle']['test']['loss'] - 1 for r in runs])
        cnt = {k: 0 for k in FEATS}
        for r in runs:
            for k in r['B'][name]['support']:
                cnt[k] += 1
        S['B'][name]['freq'] = {k: cnt[k] / len(runs) for k in FEATS}
    S['ident'] = {k: agg([r['ident'][k] for r in runs]) for k in runs[0]['ident']}
    S['rain_law'] = {i: agg([r['rain_law'][i] for r in runs]) for i in range(6)}
    with open(os.path.join(RES, out), 'w') as fh:
        json.dump(dict(summary=S, runs=runs, params=dict(TRUE=SM.TRUE, RAIN_LAW=SM.RAIN_LAW, YEAR_MULT=SM.YEAR_MULT.tolist(),
                                                         P_DAY=SM.P_DAY, P_WELL=SM.P_WELL, SIG_O=SM.SIG_O, SIG_H=SM.SIG_H,
                                                         GAPS=GAPS, FEATS=FEATS, GAMMAS=GAMMAS, NSEED=nseed)), fh)
    # log
    for m in ('oracle', 'M0', 'M1', 'A'):
        s = S[m]
        line = (f"{m:7s} loss train {s['train']['med']:.5f} test {s['test']['med']:.5f} drought {s['drought']['med']:.5f}"
                f" | cov90 {s['test_cov']['med']:.3f} | rech corr {s['corr_month']['med']:.3f}"
                f" drought err {s['drought_rel_err']['med']:+.2f}")
        if m != 'oracle':
            line += f" | excess {s['excess_rel']['med']:+.2f} dist {s['dist']['med']:.5f}"
        print(line)
        print('        gap MSE per value', [round(g['med'], 6) for g in s['gap']])
    print('A par', {k: (round(v['med'], 2), round(v['q25'], 2), round(v['q75'], 2)) for k, v in S['A_par'].items()},
          '| true', SM.TRUE)
    for name, s in S['B'].items():
        print(f"B {name:8s} test {s['test']['med']:.5f} (+{s['test_rel_oracle']['med']:.2f} vs oracle) drought {s['drought']['med']:.5f}"
              f" cov {s['test_cov']['med']:.3f} corr {s['corr_month']['med']:.3f} drought err {s['drought_rel_err']['med']:+.2f}"
              f" | freq {', '.join(f'{k}:{v:.2f}' for k, v in s['freq'].items() if v > 0)}")
    print('ident', {k: round(v['med'], 3) for k, v in S['ident'].items()})
    print('rain law (c0,c1,c2,d0,d1,d2)', [round(S['rain_law'][i]['med'], 3) for i in range(6)], '| true', SM.RAIN_LAW)


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 12, sys.argv[2] if len(sys.argv) > 2 else 'shiu_exp.json')
