"""Bayesian calibration of the areal chloride model to the documented facts (likelihood weighting).

Targets (sheet 7_Cenameri2016_SWI_Facts and the four analyses of sheet 5, Cenameri & Beqiraj 2016):
  T1  area whose shallow (upper-layer) chloride exceeds 250 mg/L, as a fraction of the 349 km2
      aquifer polygon (the convention of the companion study)                                ~ 0.15
  T2  littoral head, median over 0.5-2.5 km from the shoreline                                ~ 3 m a.s.l.
  T3a seawater fraction of mid-depth screens (second aquifer), SW/Adriatic band (0.5-2.5 km),
      wells 341 and 503                                                                         ~ 4.7 %
      (their TDS, 2331 and 2452 mg/L, exceeds the documented first-aquifer maximum of 1500 mg/L, so
      they sample the second aquifer; the alternative assignment is run with VARIANT='shallow')
  T3b seawater fraction of shallow screens (first aquifer; TDS 1182 mg/L), central band (3-6 km),
      well 340                                                                                  ~ 1.9 %
      HELD OUT: not used in the likelihood, reported as a posterior predictive check
  T3c chloride of shallow screens in the NE recharge band (>= 7 km, y 36-46 km), well 193       < 30 mg/L
The transect bands are taken in the Fushe-Kuqe sector (y = 30-40 km); the four wells have no published
coordinates, so the bands follow the transect positions given in the source.

Usage:  python3 fkcl_calib.py [N] [seed]      -> ../results/calib_ensemble.npz, calib_summary.json
"""
import os
import sys
import json
import time
import numpy as np
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fkcl_model as M  # noqa: E402

RES = os.path.join(HERE, '..', 'results')
APOLY = 349.09         # km2, aquifer polygon (sheet 1_Summary)
OBS = dict(area=0.15, area_sd=0.05, hlit=3.0, hlit_sd=1.0, f_sw=0.047, f_c=0.0186, logsd=0.7, cl_ne=30.0, cl_ne_s=5.0)
_m = None


def masks(m):
    sea = m.sea_row[m.aj] & m.valid
    fs = sea & (m.cy >= 30) & (m.cy <= 40)
    return dict(sw=fs & (m.dist >= 0.5) & (m.dist <= 2.5), c=fs & (m.dist >= 3) & (m.dist <= 6),
                ne=sea & (m.cy >= 36) & (m.cy <= 46) & (m.dist >= 7))


def summarize(m, o, mk):
    A = m.valid.sum()
    return np.array([((o['Cl_sh'] > M.CL_LIMIT) & m.valid).sum() * m.area / 1e6 / APOLY,
                     np.median(o['h'][mk['sw']]),
                     np.median(o['f_sh'][mk['sw']]),
                     np.median(o['f_sh'][mk['c']]),
                     np.median(o['Cl_sh'][mk['ne']]),
                     ((o['zeta'] < o['d'] + o['B']) & m.valid).sum() * m.area / 1e6,      # toe area (deep wedge), km2
                     ((o['Cl_dp'] > M.CL_LIMIT) & m.valid).sum() * m.area / 1e6 / APOLY,
                     np.median(o['f_dp'][mk['sw']]),
                     np.max(np.where(mk['sw'] | mk['c'], o['Cl_sh'], 0)),
                     np.max(np.where(mk['sw'] | mk['c'], o['Cl_dp'], 0)),
                     np.median(o['f_mid'][mk['sw']]),
                     np.median(o['Cl_sh'][mk['sw']]), np.median(o['Cl_mid'][mk['sw']]),
                     ((o['Cl_mid'] > M.CL_LIMIT) & m.valid).sum() * m.area / 1e6 / APOLY,
                     np.median(o['f_mid'][mk['c']])])


SUMNAMES = ['area250_sh', 'h_lit', 'f_sw', 'f_c', 'cl_ne', 'toe_area_km2', 'area250_dp', 'fdp_sw',
            'clmax_sh_transect', 'clmax_dp_transect', 'fmid_sw', 'clsh_sw', 'clmid_sw', 'area250_mid', 'fmid_c']


VARIANT = os.environ.get('FKCL_VARIANT', 'second')   # 'second' (primary) or 'shallow' (sensitivity)


def loglik(S):
    S = np.atleast_2d(S)
    ll = -0.5 * ((S[:, 0] - OBS['area']) / OBS['area_sd']) ** 2
    ll += -0.5 * ((S[:, 1] - OBS['hlit']) / OBS['hlit_sd']) ** 2
    fsw = S[:, 10] if VARIANT == 'second' else S[:, 2]
    ll += -0.5 * ((np.log(np.maximum(fsw, 1e-6)) - np.log(OBS['f_sw'])) / OBS['logsd']) ** 2
    # T3b (central band, S[:, 3]) is held out
    ll += -np.logaddexp(0.0, (S[:, 4] - OBS['cl_ne']) / OBS['cl_ne_s'])
    return ll


def _init():
    global _m, _mk
    _m = M.Model()
    _mk = masks(_m)


def _work(args):
    P, rows = args
    out = np.zeros((len(rows), len(SUMNAMES)))
    for r, i in enumerate(rows):
        o = _m.run(M.Model.one(P, i))
        out[r] = summarize(_m, o, _mk)
    return out


def main(N=20000, seed=11):
    os.makedirs(RES, exist_ok=True)
    m = M.Model()
    P = m.sample_prior(N, np.random.default_rng(seed))
    chunks = np.array_split(np.arange(N), 64)
    t0 = time.time()
    with Pool(4, initializer=_init) as pool:
        S = np.vstack(pool.map(_work, [(P, c) for c in chunks]))
    ll = loglik(S)
    w = np.exp(ll - ll.max()); w /= w.sum()
    ess = 1.0 / np.sum(w ** 2)
    tag = '' if VARIANT == 'second' else '_' + VARIANT
    np.savez_compressed(os.path.join(RES, f'calib_ensemble{tag}.npz'), S=S, ll=ll, weight=w,
                        **{k: v for k, v in P.items()})
    def q(x, wt, qs=(0.05, 0.5, 0.95)):
        o = np.argsort(x); c = np.cumsum(wt[o]); return [float(x[o][np.searchsorted(c, qq)]) for qq in qs]
    summ = dict(variant=VARIANT, N=N, seed=seed, ess=float(ess), seconds=round(time.time() - t0, 1),
                prior={n: q(S[:, k], np.full(N, 1 / N)) for k, n in enumerate(SUMNAMES)},
                posterior={n: q(S[:, k], w) for k, n in enumerate(SUMNAMES)},
                params_prior={k: q(v, np.full(N, 1 / N)) for k, v in P.items() if k != 'theta'},
                params_post={k: q(v, w) for k, v in P.items() if k != 'theta'})
    json.dump(summ, open(os.path.join(RES, f'calib_summary{tag}.json'), 'w'), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20000, int(sys.argv[2]) if len(sys.argv) > 2 else 11)
