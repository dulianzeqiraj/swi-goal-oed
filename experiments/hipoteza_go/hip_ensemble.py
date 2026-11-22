"""Ensemble of the hypothesis class: M draws of the hydraulic parameters, one coupled steady solve and the tagged
responses for each (about 0.4 s per member).  Writes res/ensemble.npz.
usage: python hip_ensemble.py [M] [workers] [seed] [out name]"""
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

import hip_core as H

HERE = os.path.dirname(os.path.abspath(__file__))


def _one(th):
    R = H.member(th)
    return R


def build(M, workers, seed, name):
    rng = np.random.default_rng(seed)
    ths = H.draw_theta(rng, M)
    t0 = time.time()
    out = []
    with Pool(workers) as pool:
        for n, r in enumerate(pool.imap(_one, ths, chunksize=4)):
            out.append(r)
            if (n + 1) % 200 == 0:
                print(f'  {n + 1}/{M} members, {time.time() - t0:.0f}s', flush=True)
    ok = np.array([r['ok'] for r in out])
    E = {k: np.array([r[k] for r in out]) for k in H.RESP_KEYS + ('head', 'sal')}
    E['toe50'] = np.array([r['toe50'] for r in out]); E['toe02'] = np.array([r['toe02'] for r in out])
    E['wsum_err'] = np.array([r['wsum_err'] for r in out]); E['ok'] = ok
    for k in H.THETA_KEYS:
        E['th_' + k] = np.array([t[k] for t in ths])
    os.makedirs(os.path.join(HERE, 'res'), exist_ok=True)
    np.savez_compressed(os.path.join(HERE, 'res', name), **E)
    print(f'{M} members in {time.time() - t0:.0f}s; converged {ok.sum()} ({100 * ok.mean():.1f}%); '
          f'max water-balance error {E["wsum_err"].max():.1e}; toe02 quantiles {np.quantile(E["toe02"], [0.05, 0.5, 0.95])}')


if __name__ == '__main__':
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 2026
    name = sys.argv[4] if len(sys.argv) > 4 else 'ensemble.npz'
    build(M, workers, seed, name)
