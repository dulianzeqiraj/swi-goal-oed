"""JEHONA-GO experiments. Run: python3 jehona_exp.py   (about 10 minutes on 4 cores)
Writes jehona_results.json and jehona_walsh.npz.

1. Exact Walsh analysis (all 2^10 paths of the first 10 months, every unit): lag profile of the design-
   averaged lag effects theta_k, the share of each Walsh degree in the variance, and the identity
   Delta = sum_k theta_k + 2 * sum_{|S| odd >= 3} f_hat(S), checked to rounding error.
2. The goal: the effect of sustained pumping (always versus never) on each outcome, averaged over the
   48 units and the last 12 of 36 months, G = mean_{i,t} [Y_it(1,...,1) - Y_it(0,...,0)].
3. Designs: Bernoulli(1/2) switchbacks with blocks of B = 1, 2, 3, 6, 12 and 36 months (B = 36 is the
   parallel-arm experiment), independent across units; 1 000 randomizations each.
4. Estimators (all from one experiment). Observed outcomes carry a fixed measurement error (head 0.05 m,
   toe 20 m). With Yt = Y_it - c_i (c_i the measured pre-experiment level), Mt = M_it - c^M_i (surrogate
   along the realized path, minus its own pre-experiment level), Mr = the surrogate's response to the
   observed forcing under steady half-rate pumping (design-independent), S_it = sum of the block
   coordinates chi = 2w - 1 over the last K months, and Delta^M the surrogate's own sustained-pumping effect:
   plain   2 Yt S                                       (impulse sum, pre-experiment baseline)
   mbase   2 (Yt - Mr) S                                (model baseline: removes the forcing response)
   ppi     Delta^M + 2 (Yt - Mt) S                      (model-assisted, weight 1)
   ppix    2 (Yt - Mr) S - lam_(-i) [2 (Mt - Mr) S - Delta^M]   (weight lam cross-fitted on the other units)
   ht      (Yt - Mr) 2^{m_t} [1{all blocks up to t pumped} - 1{none pumped}]   (path Horvitz-Thompson)
   model   Delta^M alone (no data)
   Every baseline and weight is fixed or computed from other units, so each estimator is unbiased over the
   randomization for its own target: the sum of the design-averaged lag effects of Y (plus lam times the
   surrogate's interaction remainder for ppi and ppix); the path Horvitz-Thompson estimator is unbiased for G.
"""
import json, time
import numpy as np
from multiprocessing import Pool
import jehona as J

N, R = 48, 1000
BS = [1, 2, 3, 6, 12, 36]
KS = [12, 36]                      # memory window of the impulse sum, months
WIN = np.arange(24, 36)            # goal window: months 25-36
U = J.make_units(N)
UM = [J.surrogate(u) for u in U]


def baseline(u):
    h0, x0 = J.initial_state(u)
    return {'head': float(h0[J._well(u)]), 'toe': x0, 'sal': float(x0 >= u['xw'])}


def unit_truth(i):
    u, m = U[i], UM[i]
    W3 = np.vstack([np.ones(J.NT), np.zeros(J.NT), np.full(J.NT, 0.5)])
    y, z = J.simulate(u, W3), J.simulate(m, W3)
    return {k: (y[k][0] - y[k][1], z[k][0] - z[k][1], z[k][2]) for k in J.OUTS}


NOISE = {'head': 0.05, 'toe': 20.0, 'sal': 0.0}
ETA = {o: np.random.default_rng(77).standard_normal((N, J.NT + 1)) * NOISE[o] for o in J.OUTS}   # fixed errors


def unit_walsh(i, m=10):
    P = J.paths_all(m)
    o = J.simulate(U[i], P)
    popc = np.array([bin(r).count('1') for r in range(2 ** m)])
    res = {}
    for k in J.OUTS:
        y = o[k][:, -1]; c = J.walsh(y)
        theta = np.array([2 * c[1 << j] for j in range(m)])[::-1]      # theta[lag], lag 0 = current month
        delta = y[-1] - y[0]
        rem = 2 * c[(popc % 2 == 1) & (popc >= 3)].sum()
        wdeg = np.array([(c[popc == d] ** 2).sum() for d in range(m + 1)])
        res[k] = dict(theta=theta, delta=delta, rem=rem, check=delta - theta.sum() - rem, wdeg=wdeg)
    return res


def run_design(args):
    B, seed = args
    rng = np.random.default_rng(seed)
    W, blk = J.design_paths(rng, R, N, B)                         # (R, N, NT), (R, N, nb)
    chi = 2 * blk - 1
    bt = np.arange(J.NT) // B                                      # block index of each month
    est = {o: {} for o in J.OUTS}
    Y = {o: np.zeros((R, N, J.NT)) for o in J.OUTS}; M = {o: np.zeros((R, N, J.NT)) for o in J.OUTS}
    for i in range(N):
        y = J.simulate(U[i], W[:, i, :]); z = J.simulate(UM[i], W[:, i, :])
        for o in J.OUTS:
            Y[o][:, i, :] = y[o]; M[o][:, i, :] = z[o]
    # harm of the experiment itself: salinization exposure of the supply wells during the 36 months
    est['harm'] = {'exposure': float(Y['sal'].mean()), 'units_saline_at_end': float((Y['sal'][:, :, -1] > 0.5).mean()),
                   'max_toe_advance': float((Y['toe'].max(-1) - np.array([BASE[i]['toe'] for i in range(N)])[None, :]).mean())}
    for o in J.OUTS:
        c = np.array([BASE[i][o] + ETA[o][i, 0] for i in range(N)])[None, :, None]   # measured pre-level
        cM = np.array([BASEM[i][o] for i in range(N)])[None, :, None]
        dM = np.stack([TRUTH[i][o][1] for i in range(N)])[None, :, :]       # (1, N, NT)
        Mr = np.stack([TRUTH[i][o][2] for i in range(N)])[None, :, :] - cM  # forcing response of the surrogate
        Yt = Y[o] + ETA[o][None, :, 1:] - c
        Mt = M[o] - cM
        for K in KS:
            kb = -(-K // B)                                                    # blocks in the window
            S = np.zeros((R, N, J.NT))
            for t in range(J.NT):
                lo = max(0, bt[t] - kb + 1)
                S[:, :, t] = chi[:, :, lo:bt[t] + 1].sum(-1)
            A = (2 * (Yt - Mr) * S)[:, :, WIN].mean(-1)                         # (R, N)
            D = (2 * (Mt - Mr) * S - dM)[:, :, WIN].mean(-1)
            n = N - 1
            mA = (A.sum(1, keepdims=True) - A) / n; mD = (D.sum(1, keepdims=True) - D) / n
            cov = ((A * D).sum(1, keepdims=True) - A * D) / n - mA * mD
            var = ((D * D).sum(1, keepdims=True) - D * D) / n - mD * mD
            lam = np.where(var > 1e-300, cov / np.where(var > 1e-300, var, 1.0), 0.0)
            ests = {'plain': (2 * Yt * S)[:, :, WIN].mean(-1), 'mbase': A,
                    'ppi': (dM + 2 * (Yt - Mt) * S)[:, :, WIN].mean(-1), 'ppix': A - lam * D}
            for name, d_unit in ests.items():
                est[o][f'{name}_K{K}'] = (d_unit.mean(1), d_unit.std(1, ddof=1) / np.sqrt(N))
            if K == KS[-1]:
                est[o]['lam_mean'] = (lam.mean(1), np.zeros(R))
        # path Horvitz-Thompson (feasible only with few blocks), with the model baseline
        mt = bt + 1
        if mt[WIN].max() <= 8:
            ht = np.zeros((R, N, J.NT))
            for t in WIN:
                b = blk[:, :, :bt[t] + 1]
                ht[:, :, t] = (Yt[:, :, t] - Mr[:, :, t]) * (2.0 ** mt[t]) * (b.all(-1).astype(float) - (1 - b).all(-1).astype(float))
            d_unit = ht[:, :, WIN].mean(-1)
            est[o]['ht'] = (d_unit.mean(1), d_unit.std(1, ddof=1) / np.sqrt(N))
    return B, est


def summarize(est, G):
    m, se = est
    return dict(mean=float(m.mean()), bias=float(m.mean() - G), sd=float(m.std()), rmse=float(np.sqrt(((m - G) ** 2).mean())),
                cover=float((np.abs(m - G) <= 1.96 * se).mean()), mean_se=float(se.mean()))


if __name__ == '__main__':
    t0 = time.time()
    with Pool(4) as p:
        TR = p.map(unit_truth, range(N))
        WA = p.map(unit_walsh, range(N))
    TRUTH = TR; BASE = [baseline(u) for u in U]; BASEM = [baseline(m) for m in UM]
    G = {o: float(np.mean([TR[i][o][0][WIN].mean() for i in range(N)])) for o in J.OUTS}
    GM = {o: float(np.mean([TR[i][o][1][WIN].mean() for i in range(N)])) for o in J.OUTS}
    print('goal G', G, 'surrogate', GM, f'{time.time() - t0:.0f}s', flush=True)
    with Pool(4, initializer=None) as p:
        # globals TRUTH and BASE are inherited by fork
        RES = dict(p.map(run_design, [(B, 100 + B) for B in BS]))
    out = {'N': N, 'R': R, 'NT': J.NT, 'window': [int(WIN[0]) + 1, int(WIN[-1]) + 1], 'goal': G, 'goal_surrogate': GM, 'designs': {}}
    for B in BS:
        out['designs'][str(B)] = {o: {name: summarize(e, G[o]) for name, e in RES[B][o].items() if name != 'lam_mean'} for o in J.OUTS}
        out['designs'][str(B)]['harm'] = RES[B]['harm']
        for o in J.OUTS:
            out['designs'][str(B)][o]['lam_mean'] = float(RES[B][o]['lam_mean'][0].mean())
        for o in J.OUTS:
            out['designs'][str(B)][o]['model'] = dict(mean=GM[o], bias=GM[o] - G[o], sd=0.0, rmse=abs(GM[o] - G[o]), cover=float('nan'), mean_se=0.0)
    # Walsh summary over units
    ws = {}
    for o in J.OUTS:
        wdeg = np.array([w[o]['wdeg'] for w in WA]); tot = wdeg[:, 1:].sum(1)
        ok = tot > 1e-12
        ws[o] = dict(n_units=int(ok.sum()),
                     share_deg1=float(np.mean(wdeg[ok, 1] / tot[ok])) if ok.any() else None,
                     share_deg2=float(np.mean(wdeg[ok, 2] / tot[ok])) if ok.any() else None,
                     share_deg3p=float(np.mean(wdeg[ok, 3:].sum(1) / tot[ok])) if ok.any() else None,
                     rem_over_delta=float(np.mean([w[o]['rem'] / w[o]['delta'] for w in WA if abs(w[o]['delta']) > 1e-9])) if any(abs(w[o]['delta']) > 1e-9 for w in WA) else None,
                     max_check=float(max(abs(w[o]['check']) for w in WA)))
    out['walsh'] = ws
    np.savez('jehona_walsh.npz', **{f'{o}_theta': np.array([w[o]['theta'] for w in WA]) for o in J.OUTS},
             **{f'{o}_wdeg': np.array([w[o]['wdeg'] for w in WA]) for o in J.OUTS},
             **{f'{o}_delta': np.array([w[o]['delta'] for w in WA]) for o in J.OUTS},
             **{f'{o}_rem': np.array([w[o]['rem'] for w in WA]) for o in J.OUTS})
    json.dump(out, open('jehona_results.json', 'w'), indent=1)
    for o in J.OUTS:
        print(o, 'G = %.4g' % G[o])
        for B in BS:
            d = out['designs'][str(B)][o]
            if o == 'sal':
                print('  harm B=%2d' % B, out['designs'][str(B)]['harm'])
            print('  B=%2d ' % B + '  '.join(f'{k}: b {v["bias"]:+.3g} rmse {v["rmse"]:.3g} cov {v["cover"]:.2f}' for k, v in d.items() if k in ('plain_K36', 'mbase_K36', 'ppi_K36', 'ppix_K36', 'mbase_K12', 'ht', 'model')) + '  lam %.2f' % d['lam_mean'])
    print(f'done {time.time() - t0:.0f}s')
