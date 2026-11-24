"""Posterior chloride ensemble and maps.

Systematic resampling of the calibrated importance ensemble (fkcl_calib.py) to M members, a forward run of
each member, and per-cell posterior products for the three screen depths:
    median and 5/95 % chloride, P(Cl > 250 mg/L), P(seawater wedge at the aquifer base), median head.
Outputs:  ../results/post_cells.csv (per cell), post_summary.json (areas, checks),
          ../results/post_ensemble.npz (member fields, float32; large, not committed).
Usage:    python3 fkcl_post.py [M] [seed]
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fkcl_model as M  # noqa: E402
import fkcl_calib as C  # noqa: E402

RES = os.path.join(HERE, '..', 'results')
FIELDS = ['Cl_sh', 'Cl_mid', 'Cl_dp', 'h', 'zeta']
_m = None


def systematic(w, n, rng):
    u = (rng.random() + np.arange(n)) / n
    return np.minimum(np.searchsorted(np.cumsum(w), u), len(w) - 1)


def _init():
    global _m
    _m = M.Model()


def _work(args):
    P, rows = args
    out = {k: np.zeros((len(rows), _m.Nc), np.float32) for k in FIELDS}
    out['wedge'] = np.zeros((len(rows), _m.Nc), bool)
    for r, i in enumerate(rows):
        o = _m.run(M.Model.one(P, i))
        for k in FIELDS:
            out[k][r] = o[k]
        out['wedge'][r] = o['zeta'] < o['d'] + o['B']
    return out


def load_posterior(Mn, seed, tag=''):
    E = np.load(os.path.join(RES, f'calib_ensemble{tag}.npz'))
    w = E['weight']
    keys = ['theta', 'R', 'eta', 'b_c', 'b_e', 'L_B', 'ground', 'w', 'Cl_s']
    idx = systematic(w, Mn, np.random.default_rng(seed))
    return {k: E[k][idx] for k in keys}, idx


def main(Mn=2000, seed=5):
    m = M.Model()
    P, idx = load_posterior(Mn, seed)
    chunks = np.array_split(np.arange(Mn), 32)
    with Pool(4, initializer=_init) as pool:
        parts = pool.map(_work, [(P, c) for c in chunks])
    F = {k: np.vstack([p[k] for p in parts]) for k in FIELDS + ['wedge']}
    np.savez_compressed(os.path.join(RES, 'post_ensemble.npz'), idx=idx, **F, **{'p_' + k: v for k, v in P.items()})

    v = m.valid
    q = lambda a, qq: np.quantile(a, qq, axis=0)
    cells = pd.DataFrame(dict(cell=np.arange(m.Nc), x_km=m.cx, y_km=m.cy, valid=v.astype(int),
                              sea_row=m.sea_row[m.aj].astype(int), dist_shore_km=m.dist,
                              cover_m=m.cover, K_idw=m.Kidw))
    for k in ['Cl_sh', 'Cl_mid', 'Cl_dp']:
        a = F[k]
        cells[k + '_p05'], cells[k + '_p50'], cells[k + '_p95'] = q(a, 0.05), q(a, 0.5), q(a, 0.95)
        cells['P250_' + k[3:]] = (a > M.CL_LIMIT).mean(0)
    cells['P_wedge'] = F['wedge'].mean(0)
    cells['h_p50'] = q(F['h'], 0.5)
    cells['zeta_p50'] = q(F['zeta'], 0.5)
    for c in cells.columns:
        if c not in ('cell', 'valid', 'sea_row', 'x_km', 'y_km', 'cover_m', 'K_idw'):
            cells[c] = np.where(v, cells[c], np.nan)
    cells.to_csv(os.path.join(RES, 'post_cells.csv'), index=False, float_format='%.5g')

    A = m.area / 1e6
    areas = {k: (((F[k] > M.CL_LIMIT) & v).sum(1) * A) for k in ['Cl_sh', 'Cl_mid', 'Cl_dp']}
    areas['wedge'] = (F['wedge'] & v).sum(1) * A
    qq = lambda x: [float(np.quantile(x, a)) for a in (0.05, 0.5, 0.95)]
    summ = dict(M=Mn, seed=seed, unique_members=int(len(np.unique(idx))), sector_km2=float(v.sum() * A),
                area_km2={k: qq(a) for k, a in areas.items()},
                area_frac_polygon={k: qq(a / C.APOLY) for k, a in areas.items()},
                params={k: qq(P[k]) for k in ['R', 'eta', 'b_c', 'b_e', 'L_B', 'ground', 'w', 'Cl_s']})
    json.dump(summ, open(os.path.join(RES, 'post_summary.json'), 'w'), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2000, int(sys.argv[2]) if len(sys.argv) > 2 else 5)
