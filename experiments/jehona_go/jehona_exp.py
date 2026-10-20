"""JEHONA-GO experiments. Run: python3 jehona_exp.py   (about 10 minutes on 4 cores)
Writes jehona_results.json and jehona_walsh.npz.

1. Exact Walsh analysis (all 2^10 paths of the first 10 months, every unit): lag profile of the design-
   averaged lag effects theta_k, the share of each Walsh degree in the variance, and the identity
   Delta = sum_k theta_k + 2 * sum_{|S| odd >= 3} f_hat(S), checked to rounding error.
2. The goal: the effect of sustained pumping (always versus never) on each outcome, averaged over the
   48 units and the last 12 of 36 months, G = mean_{i,t} [Y_it(1,...,1) - Y_it(0,...,0)].
3. Designs: Bernoulli(1/2) switchbacks with blocks of B = 1, 2, 3, 6, 12 and 36 months (B = 36 is the
   parallel-arm experiment), independent across units; 1 000 randomizations each.
4. Estimators (all from one experiment):
   plain   impulse sum   2 (Y_it - c_i) sum_{j in last K} chi_ij           (block coordinates chi = 2w - 1)
   ppi     model-assisted Delta^M_it + 2 (Y_it - M_it) sum_{j in last K} chi_ij   (M: surrogate along
           the realized path, Delta^M: surrogate's own sustained-pumping effect)
   ht      path Horvitz-Thompson  (Y_it - c_i) 2^{m_t} [1{all blocks up to t pumped} - 1{none pumped}]
   model   Delta^M alone (no data)
   c_i is the unit's pre-experiment level (a fixed baseline, which keeps unbiasedness).
"""
import json, time
import numpy as np
from multiprocessing import Pool
import jehona as J

N, R = 48, 1000
BS = [1, 2, 3, 6, 12, 36]
KS = [12, 24, 36]                  # memory window of the impulse sum, months
WIN = np.arange(24, 36)            # goal window: months 25-36
U = J.make_units(N)
UM = [J.surrogate(u) for u in U]


def baseline(u):
    h0, x0 = J.initial_state(u)
    return {'head': float(h0[J._well(u)]), 'toe': x0, 'sal': float(x0 >= u['xw'])}


def unit_truth(i):
    u, m = U[i], UM[i]
    W2 = np.vstack([np.ones(J.NT), np.zeros(J.NT)])
    y, z = J.simulate(u, W2), J.simulate(m, W2)
    return {k: (y[k][0] - y[k][1], z[k][0] - z[k][1]) for k in J.OUTS}


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
    for o in J.OUTS:
        c = np.array([BASE[i][o] for i in range(N)])[None, :, None]
        dM = np.stack([TRUTH[i][o][1] for i in range(N)])[None, :, :]       # (1, N, NT)
        for K in KS:
            kb = -(-K // B)                                                    # blocks in the window
            S = np.zeros((R, N, J.NT))
            for t in range(J.NT):
                lo = max(0, bt[t] - kb + 1)
                S[:, :, t] = chi[:, :, lo:bt[t] + 1].sum(-1)
            plain = 2 * (Y[o] - c) * S
            ppi = dM + 2 * (Y[o] - M[o]) * S
            for name, E in (('plain', plain), ('ppi', ppi)):
                d_unit = E[:, :, WIN].mean(-1)                                  # (R, N)
                est[o][f'{name}_K{K}'] = (d_unit.mean(1), d_unit.std(1, ddof=1) / np.sqrt(N))
        # path Horvitz-Thompson (feasible only with few blocks)
        mt = bt + 1
        if mt[WIN].max() <= 8:
            ht = np.zeros((R, N, J.NT))
            for t in WIN:
                b = blk[:, :, :bt[t] + 1]
                ht[:, :, t] = (Y[o][:, :, t] - c[..., 0]) * (2.0 ** mt[t]) * (b.all(-1).astype(float) - (1 - b).all(-1).astype(float))
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
    TRUTH = TR; BASE = [baseline(u) for u in U]
    G = {o: float(np.mean([TR[i][o][0][WIN].mean() for i in range(N)])) for o in J.OUTS}
    GM = {o: float(np.mean([TR[i][o][1][WIN].mean() for i in range(N)])) for o in J.OUTS}
    print('goal G', G, 'surrogate', GM, f'{time.time() - t0:.0f}s', flush=True)
    with Pool(4, initializer=None) as p:
        # globals TRUTH and BASE are inherited by fork
        RES = dict(p.map(run_design, [(B, 100 + B) for B in BS]))
    out = {'N': N, 'R': R, 'NT': J.NT, 'window': [int(WIN[0]) + 1, int(WIN[-1]) + 1], 'goal': G, 'goal_surrogate': GM, 'designs': {}}
    for B in BS:
        out['designs'][str(B)] = {o: {name: summarize(e, G[o]) for name, e in RES[B][o].items()} for o in J.OUTS}
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
            print('  B=%2d ' % B + '  '.join(f'{k}: b {v["bias"]:+.3g} sd {v["sd"]:.3g} rmse {v["rmse"]:.3g} cov {v["cover"]:.2f}' for k, v in d.items() if k in ('plain_K36', 'ppi_K36', 'ppi_K12', 'ht', 'model')))
    print(f'done {time.time() - t0:.0f}s')
