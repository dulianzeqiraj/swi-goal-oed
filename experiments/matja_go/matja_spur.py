"""MATJA-GO, test of Proposition M3: the value of an instrument that knows nothing about the goal.

With rain only, the tide gauge records the sea level, which is independent of the recharge, the inflow and kappa under
the prior. Its exact value for those goals is zero. An N-member stochastic ensemble smoother
  shrinks the expected spread variance of every such goal by the factor   1 - delta_N
  grows the expected error variance of the ensemble mean by the factor    1 + eps_N
with delta_N = E tr(Ch (Ch + R)^-1) / (N-1) and eps_N = E tr(Ch (Ch + R)^-1 (C + R) (Ch + R)^-1) / (N-1), where C is the
prior covariance of the instrument's data, Ch its sample covariance in the ensemble and R the noise covariance (exact
identities, Proposition M3); both are about d_s/(N-1) for large N, d_s = tr(C (C + R)^-1) the signal degrees of freedom.
The script computes delta_N and eps_N by Monte Carlo, and measures both factors and the raw-ensemble and calibrated
half-widths for N = 32, 64, 128, 256 and 512 members on 300 simulated aquifers.

usage: python matja_spur.py   (writes res/matja_spur.json)"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import matja_exp as X  # noqa: E402
from matja_exp import G, M  # noqa: E402

GOALS = ('qL', 'r', 'kappa')


def d_signal():
    mu, S = M.prior_z()
    C = S[M.SL['deta'], M.SL['deta']] + S[M.SL['meta'], M.SL['meta']]
    R = M.SIG_ETA ** 2 * np.eye(M.NT)
    return float(np.trace(C @ np.linalg.inv(C + R)))


def factors(N, reps=4000, seed=7):
    """delta_N and eps_N of Proposition M3 by Monte Carlo over ensembles of the instrument's data."""
    mu, S = M.prior_z()
    C = S[M.SL['deta'], M.SL['deta']] + S[M.SL['meta'], M.SL['meta']]
    R = M.SIG_ETA ** 2 * np.eye(M.NT)
    Lc = np.linalg.cholesky(C + 1e-12 * np.eye(M.NT))
    rng = np.random.default_rng(seed)
    d1, d2 = [], []
    for _ in range(reps):
        Y = rng.standard_normal((N, M.NT)) @ Lc.T
        Yc = Y - Y.mean(0)
        Ch = Yc.T @ Yc / (N - 1)
        A = np.linalg.solve(Ch + R, Ch)            # (Ch+R)^-1 Ch
        d1.append(np.trace(A))
        d2.append(np.trace(A.T @ (C + R) @ np.linalg.solve(Ch + R, np.eye(M.NT))))
    return float(np.mean(d1) / (N - 1)), float(np.mean(d2) / (N - 1))


def run_design(bed, pool, design):
    rows = bed.rows(design)
    res = []
    for cs in pool:
        y = bed.data(cs, rows)
        rec = bed.reconstruct(cs, rows, y)
        res.append(dict(t=X.targets(cs), m={k: rec[k][0] for k in GOALS}, s={k: rec[k][1] for k in GOALS}))
    return res


def summary(res):
    out = {}
    for k in GOALS:
        err2 = np.mean([np.mean((c['t'][k] - c['m'][k]) ** 2) for c in res])
        spr2 = np.mean([np.mean(c['s'][k] ** 2) for c in res])
        smean = np.mean([np.mean(c['s'][k]) for c in res])
        lam = G.crc_lambda(G.loss_matrix(res, k))
        out[k] = dict(err2=float(err2), spr2=float(spr2), es=float(1.645 * smean), matja=float(lam * smean),
                      lam=float(lam))
    return out


def main():
    t0 = time.time()
    bed = X.Bed()
    rng = np.random.default_rng(303)
    pool = [bed.case(rng) for _ in range(300)]
    ds = d_signal()
    out = dict(d_s=ds, n_cases=len(pool), sizes={})
    for N in (32, 64, 128, 256, 512):
        X.NENS = N
        b = summary(run_design(bed, pool, ()))
        t = summary(run_design(bed, pool, ('TG',)))
        dN, eN = factors(N)
        pred_spr, pred_err = 1 - dN, 1 + eN
        row = dict(base=b, tg=t, delta=dN, eps=eN, first_order=ds / (N - 1), pred_spread=pred_spr, pred_error=pred_err,
                   pred_es=float(np.sqrt(pred_spr)), pred_matja=float(np.sqrt(pred_err)))
        out['sizes'][str(N)] = row
        X.log(f'N {N:3d}: predicted spread x{pred_spr:.3f} error x{pred_err:.3f} | ' + ' | '.join(
            f'{k}: spread x{t[k]["spr2"] / b[k]["spr2"]:.3f} error x{t[k]["err2"] / b[k]["err2"]:.3f} '
            f'ES x{t[k]["es"] / b[k]["es"]:.3f} MATJA x{t[k]["matja"] / b[k]["matja"]:.3f}' for k in GOALS)
              + f'  [{time.time() - t0:.0f}s]')
    with open(os.path.join(X.RES, 'matja_spur.json'), 'w') as fh:
        json.dump(out, fh, indent=1)


if __name__ == '__main__':
    main()
