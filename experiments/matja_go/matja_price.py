"""MATJA-GO, check of Remark M3 (the price of an instrument) on the fresh-pool results of matja_single.py.

For each single instrument c and goal g: rho = the exact fraction of the goal's posterior variance that c removes,
eps = d_s(c)/(N-1) the first-order spurious error growth of Proposition M3, and the predicted factor of the guaranteed
half-width sqrt((1 - rho)(1 + eps)) against the measured one. The guaranteed value is predicted negative when
rho < eps/(1 + eps).

usage: python matja_price.py   (writes res/matja_price.json)"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
N = 128


def main():
    with open(os.path.join(RES, 'matja_single.json')) as fh:
        S = json.load(fh)
    base, ds = S['rain only'], S['_d_s']
    rows = []
    for c in ds:
        for g in ('eta', 'qL', 'r', 'kappa'):
            rho = 1 - (S[c][g]['exact_halfwidth'] / base[g]['exact_halfwidth']) ** 2
            eps = ds[c] / (N - 1)
            pred = float(np.sqrt(max(1 - rho, 0.0) * (1 + eps)))
            meas = S[c][g]['halfwidth'] / base[g]['halfwidth']
            rows.append(dict(inst=c, goal=g, rho=float(rho), eps=eps, pred=pred, meas=float(meas),
                             neg_pred=bool(rho < eps / (1 + eps)), neg_meas=bool(meas > 1)))
    agree = sum(r['neg_pred'] == r['neg_meas'] for r in rows)
    err = [abs(r['pred'] / r['meas'] - 1) for r in rows]
    out = dict(rows=rows, n=len(rows), sign_agree=agree, n_negative=sum(r['neg_meas'] for r in rows),
               max_rel_err=float(max(err)), median_rel_err=float(np.median(err)))
    for r in rows:
        print(f"{r['inst']:3s} {r['goal']:6s} rho {r['rho']:.2f} eps {r['eps']:.3f} pred {r['pred']:.3f} meas "
              f"{r['meas']:.3f} {'NEG' if r['neg_meas'] else '   '} {'pred NEG' if r['neg_pred'] else ''}")
    print('sign agreement', agree, '/', len(rows), '| negative values', out['n_negative'], '| factor error median',
          f"{out['median_rel_err']:.3f}", 'max', f"{out['max_rel_err']:.3f}")
    with open(os.path.join(RES, 'matja_price.json'), 'w') as fh:
        json.dump(out, fh, indent=1)


if __name__ == '__main__':
    main()
