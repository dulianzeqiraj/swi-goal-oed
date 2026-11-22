"""Ensemble of the Fushe-Kuqe class (fk_core): M parameter vectors, one coupled steady solve each.
Writes res_fk/ensemble_fk.npz (not in git: it is derived from the data of the Albanian Geological Survey and of
A. Beqiraj, whose permission covers the chloride manuscript).
usage: python fk_ensemble.py [M] [workers] [seed]"""
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

import fk_core as F

HERE = os.path.dirname(os.path.abspath(__file__))
CALIB = os.path.join(HERE, '..', '..', 'chloride_fk', 'results', 'calib_ensemble.npz')
OUT = os.path.join(HERE, 'res_fk')
_calib = None


def _init():
    global _calib
    _calib = dict(np.load(CALIB))
    F.areal()


def _one(th):
    try:
        R = F.member(th, _calib)
        R.pop('sec')
        return R
    except Exception as e:                      # a failed solve is recorded, not hidden
        return dict(ok=False, error=repr(e))


def build(M, workers, seed):
    calib = dict(np.load(CALIB))
    ths = F.draw_theta(np.random.default_rng(seed), M, calib)
    t0 = time.time()
    out = []
    with Pool(workers, initializer=_init) as pool:
        for n, r in enumerate(pool.imap(_one, ths, chunksize=4)):
            out.append(r)
            if (n + 1) % 400 == 0:
                print(f'  {n + 1}/{M} members, {time.time() - t0:.0f}s', flush=True)
    good = [r for r in out if 'resp' in r]
    nx = good[0]['resp'].shape[0]
    E = dict(ok=np.array([bool(r.get('ok', False)) for r in out]))
    for k in ('h_lit', 'h_wf', 'h_wf0', 'ground', 'toe50', 'toe02', 'vL', 'n_an', 'Qw', 'wsum_err', 'dc'):
        E[k] = np.array([r.get(k, np.nan) for r in out], float)
    for k, shape in (('resp', (nx, 3, len(F.KEYS))), ('sal', (nx, 3)), ('head_top', (nx,)), ('top', (nx,)),
                     ('bot', (nx,))):
        E[k] = np.array([r[k] if k in r else np.full(shape, np.nan) for r in out], np.float32)
    E['xc'] = good[0]['xc']; E['dist'] = good[0]['dist']
    for k in F.THETA_FK:
        E['th_' + k] = np.array([t[k] for t in ths])
    os.makedirs(OUT, exist_ok=True)
    np.savez_compressed(os.path.join(OUT, 'ensemble_fk.npz'), **E)
    ok = E['ok']
    print(f'{M} members in {time.time() - t0:.0f}s; converged {ok.sum()} ({100 * ok.mean():.1f}%); '
          f'failed {sum("error" in r for r in out)}; max water-balance error {np.nanmax(E["wsum_err"]):.1e}')


if __name__ == '__main__':
    build(int(sys.argv[1]) if len(sys.argv) > 1 else 3200, int(sys.argv[2]) if len(sys.argv) > 2 else 4,
          int(sys.argv[3]) if len(sys.argv) > 3 else 2027)
