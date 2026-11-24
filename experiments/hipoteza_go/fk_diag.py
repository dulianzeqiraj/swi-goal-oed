"""Why "sea and fresh recharge only" is rejected: what the sea can deliver to well 340 against what it leaves at
wells 503 and 341, in every simulation that reproduces the heads (converged, and the discarded unconverged ones as
a check).  Writes res_fk/fk_diag_<variant>.json.  usage: FK_VARIANT=second python fk_diag.py"""
import json
import os

import numpy as np

import fk_infer as I

HERE = os.path.dirname(os.path.abspath(__file__))
VARIANT = os.environ.get('FK_VARIANT', 'second')


def main():
    z = np.load(os.path.join(HERE, 'res_fk', 'ensemble_fk.npz'))
    E = {k: z[k] for k in z.files}
    cols = I.bands(E)
    scr = [w[3] for w in I.WELLS] if VARIANT == 'second' else [0, 0, 0, 0]
    y, eps = I.data()
    kh = I.kappa_head(E)
    lo, hi = I.box([0, 2])
    # sea fraction needed (strengths at the ends of their intervals that favour the hypothesis)
    need340 = (y[2] - eps[2] - I.S_INT[2, 1]) / (I.S_INT[0, 1] - I.S_INT[2, 1])
    need_sw = (min(y[0], y[1]) + max(eps[0], eps[1]) - I.S_INT[2, 0]) / (I.S_INT[0, 0] - I.S_INT[2, 0])
    out = dict(variant=VARIANT, need340_min=float(need340), need_sw_max=float(need_sw))
    for name, sel in (('converged', z['ok']), ('unconverged', ~z['ok'])):
        hc = np.flatnonzero(sel & (kh <= 1.0))
        x = np.array([np.nanmax(E['resp'][j][cols[2], scr[2], 0]) for j in hc])       # most sea at 340's band
        ysw = np.array([np.nanmin(E['resp'][j][cols[0], scr[0], 0]) for j in hc])     # least sea at 503/341's band
        feas = np.zeros((len(hc), 4), bool)
        for n_, j in enumerate(hc):
            G = I.responses(E, j, cols, scr)
            for i in range(4):
                a, b = G[i] @ lo, G[i] @ hi
                feas[n_, i] = np.any((a <= y[i] + eps[i]) & (b >= y[i] - eps[i]))
        j340 = feas[:, 2]
        out[name] = dict(n=int(len(hc)), feasible_each={w[0]: int(feas[:, i].sum()) for i, w in enumerate(I.WELLS)},
                         feasible_all=int(feas.all(1).sum()), n340=int(j340.sum()),
                         sw_min_when_340=(float(ysw[j340].min()) if j340.any() else None),
                         sw_median_when_340=(float(np.median(ysw[j340])) if j340.any() else None),
                         toe02_when_340=(np.quantile(E['toe02'][hc][j340], [0, 0.5, 1]).tolist() if j340.any() else None),
                         x=x.tolist(), y=ysw.tolist(), toe02=E['toe02'][hc].tolist())
    json.dump(out, open(os.path.join(HERE, 'res_fk', f'fk_diag_{VARIANT}.json'), 'w'), indent=1)
    c = out['converged']
    print(VARIANT, 'need340', round(need340, 4), 'need_sw', round(need_sw, 4), '| converged', c['n'], c['feasible_each'],
          'all', c['feasible_all'], 'n340', c['n340'], 'sw min when 340', c['sw_min_when_340'], 'toe', c['toe02_when_340'])
    u = out['unconverged']
    print('   unconverged', u['n'], u['feasible_each'], 'all', u['feasible_all'], 'sw min when 340', u['sw_min_when_340'])


if __name__ == '__main__':
    main()
