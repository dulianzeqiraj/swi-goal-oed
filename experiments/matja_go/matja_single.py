"""MATJA-GO, test T6 on the fresh pool: every single instrument added to the rain, recalibrated and scored on pool B
(the same 300 simulated aquifers as matja_exp.py), so that the value of each instrument is reported without the
optimism of the selection pool.

usage: python matja_single.py   (writes res/matja_single.json)"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import matja_exp as X  # noqa: E402


def signal_dof(bed, rng, reps=10):
    vk = (np.exp(X.M.KAP_LSD ** 2) - 1) * np.exp(2 * np.log(X.M.KAP_MED) + X.M.KAP_LSD ** 2)   # variance of kappa
    nt = X.M.NT
    out = {}
    for c in X.CANDS:
        ds = []
        for _ in range(reps):
            cs = bed.case(rng)
            if c == 'TG':
                A = np.zeros((nt, X.M.NZ)); A[:, X.M.SL['deta']] = np.eye(nt); A[:, X.M.SL['meta']] = 1.0
                C = A @ bed.Sig @ A.T; R = X.M.SIG_ETA ** 2 * np.eye(nt)
            else:
                ix = X.SITES[int(c[1:])] * nt + np.arange(nt)
                Gi = bed.G[ix]
                C = Gi @ bed.Sig @ Gi.T + vk * np.outer(cs['gk'][ix], cs['gk'][ix]); R = X.M.SIG_H ** 2 * np.eye(nt)
            ds.append(float(np.trace(C @ np.linalg.inv(C + R))))
        out[c] = float(np.mean(ds))
    return out


def main():
    t0 = time.time()
    bed = X.Bed()
    rng = np.random.default_rng(101)
    _ = [bed.case(rng) for _ in range(150)]          # pool A, regenerated only to reach pool B
    poolB = [bed.case(rng) for _ in range(300)]
    rngB = np.random.default_rng(404)
    out = {}
    for d in [()] + [(c,) for c in X.CANDS]:
        res = X.evaluate_design(bed, poolB, d)
        name = d[0] if d else 'rain only'
        out[name] = {k: X.fresh_score(res, k, rngB) for k in X.TG_}
        X.log(f'{name:9s} ' + ' | '.join(f'{k} hw {out[name][k]["halfwidth"]:.3f} ES {out[name][k]["es_halfwidth"]:.3f} '
                                         f'exact {out[name][k]["exact_halfwidth"]:.3f}' for k in ('r', 'qL', 'kappa'))
              + f'  [{time.time() - t0:.0f}s]')
    out['_d_s'] = signal_dof(bed, np.random.default_rng(5))
    X.log('signal degrees of freedom: ' + ', '.join(f'{c} {v:.1f}' for c, v in out['_d_s'].items()))
    with open(os.path.join(X.RES, 'matja_single.json'), 'w') as fh:
        json.dump(out, fh, indent=1)


if __name__ == '__main__':
    main()
