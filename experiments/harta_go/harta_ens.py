"""HARTA-GO, stage 1: prior ensembles of the Fushe-Kuqe geolocated model (fk_geo.FKGeo, prior 'base'),
with the supply wells and pumping of PRAG-GO (fk_prag_geo.py). Each row holds the heads at the 16
candidate monitoring wells, the heads at supply wells A and B, and the intruded area of the sector.
  train : 12 000 realizations, the same draws as the PRAG-GO inner ensemble (seeds 1000-1039)
  ref   : 48 000 independent realizations (seeds 20000-20159), the reference for exact EIG
  outer : 4 000 independent realizations (seeds 40000-40039), outer samples of the reference
  test  : 1 000 independent realizations (seeds 60000-60009), synthetic truths for the sequential test
Run from this folder: python3 harta_ens.py   (about 4 minutes on 4 cores). Output: harta_ens.npz
"""
import os, sys, time
import numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
PG = os.path.join(HERE, '..', 'prag_go_fushe_kuqe')
sys.path.insert(0, PG)
os.chdir(PG)                       # fk_prag_geo reads res_geo/mar_geo.json relative to its folder
sys.argv = [sys.argv[0], 'base']
import fk_prag_geo as G            # noqa: E402  (builds the model and the pumped right-hand side)


def chunk(args):
    seed, n = args
    rng = np.random.default_rng(seed)
    return np.array([G.heads(G.LG @ rng.standard_normal(G.m.Nz)) for _ in range(n)])


def ens(n, seed0, k=40):
    with Pool(4) as p:
        return np.vstack(p.map(chunk, [(seed0 + j, n // k) for j in range(k)]))


if __name__ == '__main__':
    t0 = time.time()
    out = dict(train=ens(12000, 1000), ref=ens(48000, 20000, 160), outer=ens(4000, 40000), test=ens(1000, 60000, 10))
    out['ids'] = G.ids; out['NC'] = G.NC; out['SN'] = G.SN; out['HC'] = G.HC
    out['supply'] = np.array([G.SUP['A']['id'], G.SUP['B']['id']])
    np.savez(os.path.join(HERE, 'harta_ens.npz'), **out)
    print({k: v.shape for k, v in out.items() if hasattr(v, 'shape')}, f'{time.time() - t0:.0f}s')
