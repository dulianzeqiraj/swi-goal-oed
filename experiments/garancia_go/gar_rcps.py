"""T5 (RCPS, Bates et al. 2021): risk control with high probability over the calibration set, against conformal risk
control, which controls the risk only on average over calibration sets.

RCPS (Bates et al., J. ACM 2021) with the Hoeffding-Bentkus p-value of that paper,
    p(R) = min( exp(-n h1(min(R, alpha), alpha)),  e P(Binomial(n, alpha) <= ceil(n R)) ),
    h1(a, b) = a log(a/b) + (1 - a) log((1 - a)/(1 - b)),
lambda_RCPS is the smallest lambda with p(R_n(lambda)) < delta (R_n is non-increasing, so every larger lambda passes too),
and P( E[L(lambda_RCPS) | calibration set] <= alpha ) >= 1 - delta. The conditional risk of each calibration set is
estimated on the 500 - n cases left out of it. Same pool as T1 (seed 1); also writes the smallest calibration set for
which a Bonferroni-corrected split-conformal band over H points is finite, n >= H / alpha - 1.

usage: python gar_rcps.py   (writes res/gar_rcps.json)"""
import json
import os
import sys
import time

import numpy as np
from scipy.stats import binom

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gar_exp as G  # noqa: E402

DELTA = 0.10


def h1(a, b):
    a = np.clip(a, 1e-12, b)
    return a * np.log(a / b) + (1 - a) * np.log((1 - a) / (1 - b))


def p_hb(R, n, alpha=G.ALPHA):
    hoeff = np.exp(-n * h1(np.minimum(R, alpha), alpha))
    bentkus = np.e * binom.cdf(np.ceil(n * R - 1e-9), n, alpha)
    return np.minimum(hoeff, bentkus)


def lam_rcps(L, n, alpha=G.ALPHA, delta=DELTA):
    ok = p_hb(L.mean(0), n, alpha) < delta
    return float(G.GRID[np.argmax(ok)]) if ok.any() else float(G.GRID[-1])


def main():
    t0 = time.time()
    pool = G.run_cases(G.Bed(), 500, 1, exact=True)
    print(f'pool of {len(pool)} cases in {time.time() - t0:.0f}s', flush=True)
    rng = np.random.default_rng(31)
    out = dict(alpha=G.ALPHA, delta=DELTA, reps=1000, targets={})
    for k in G.CH + ('kappa',):
        L = G.loss_matrix(pool, k)
        swid = np.array([np.mean(2 * c['s'][k]) for c in pool])
        ewid = np.array([np.mean(c['ex'][k][1] - c['ex'][k][0]) for c in pool])
        out['targets'][k] = {}
        for n in (50, 100, 200):
            rc, rr, wc, wr = [], [], [], []
            for _ in range(out['reps']):
                perm = rng.permutation(len(pool)); ci, ti = perm[:n], perm[n:]
                lc, lr = G.crc_lambda(L[ci]), lam_rcps(L[ci], n)
                rc.append(L[ti, int(round(lc / G.GRID[1]))].mean()); rr.append(L[ti, int(round(lr / G.GRID[1]))].mean())
                wc.append(np.mean(lc * swid[ti] / ewid[ti])); wr.append(np.mean(lr * swid[ti] / ewid[ti]))
            rc, rr = np.array(rc), np.array(rr)
            out['targets'][k][str(n)] = dict(crc_mean=float(rc.mean()), crc_p90=float(np.quantile(rc, 0.9)),
                                              crc_ok=float(np.mean(rc <= G.ALPHA)), rcps_mean=float(rr.mean()),
                                              rcps_p90=float(np.quantile(rr, 0.9)), rcps_ok=float(np.mean(rr <= G.ALPHA)),
                                              crc_width=float(np.mean(wc)), rcps_width=float(np.mean(wr)))
            d = out['targets'][k][str(n)]
            print(f'{k:5s} n={n:3d}  CRC risk {d["crc_mean"]:.3f} (p90 {d["crc_p90"]:.3f}, <=alpha in {d["crc_ok"]:.2f}) '
                  f'w{d["crc_width"]:.2f} | RCPS risk {d["rcps_mean"]:.3f} (p90 {d["rcps_p90"]:.3f}, <=alpha in '
                  f'{d["rcps_ok"]:.2f}) w{d["rcps_width"]:.2f}', flush=True)
    out['bonferroni_min_n'] = {k: int(np.ceil(H / G.ALPHA - 1)) for k, H in (('weeks', G.M.NT), ('cells', G.M.NX))}
    with open(os.path.join(G.RES, 'gar_rcps.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f'Bonferroni needs n >= {out["bonferroni_min_n"]}; done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
