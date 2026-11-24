"""Stage 1 and 2 of PRAG-GO on the Fushe-Kuqe field model.

Stage 1: prior ensemble (12 000 inner + 2 000 outer realizations) of the heads at the 32
  inside-aquifer K-wells and of the intruded area.
Stage 2: the project's linearization at the prior mean (central differences on the pilot
  zones, exactly as src/fushe_kuqe_field_design.m), for the same quantities.

Priors:  base    published configuration (12 zones, rhoF = 0.6, Lc = 8 km)
         rho805  field estimate of the cross-facies correlation (rhoF = 0.805)
         fine    10 x 16 pilot grid with Lc = 3 km (finer, more local heterogeneity)
"""
import sys, os, time
import numpy as np
from multiprocessing import Pool
from fk import FK, default_xlsx

OUT = sys.argv[1]; PRIOR = sys.argv[2]
XLSX = default_xlsx()
CFG = {'base': dict(), 'rho805': dict(rhoF=0.805), 'fine': dict(nzx=10, nzy=16, Lc=3.0)}[PRIOR]
os.makedirs(OUT, exist_ok=True)
m = FK(XLSX, **CFG)
WIN = np.flatnonzero(m.wellInside)                         # the 32 inside wells
WC = np.array([m.cell_of(m.Wk[w, 0], m.Wk[w, 1]) for w in WIN])
assert (WC >= 0).all()
LG = np.linalg.cholesky(m.Gam)


def run_chunk(args):
    seed, n = args
    rng = np.random.default_rng(seed); rows = []
    for _ in range(n):
        h = m.solve(LG @ rng.standard_normal(m.Nz))
        rows.append(np.r_[h[WC], m.goalA(h)])
    return np.array(rows)


def ensemble(n_total, seed0):
    with Pool(4) as p:
        return np.vstack(p.map(run_chunk, [(seed0 + k, n_total // 40) for k in range(40)]))


if __name__ == '__main__':
    t0 = time.time()
    print(f'{PRIOR}: zones {m.Nz}, facies counts {np.bincount(m.zfac, minlength=4)[1:]}, area0 {m.baseArea:.1f} km^2')
    inner = ensemble(12000, 1000); outer = ensemble(2000, 5000)
    np.savez(f'{OUT}/ens.npz', inner=inner, outer=outer)
    print(f'ensemble {time.time() - t0:.0f}s; area mean {inner[:, -1].mean():.1f} sd {inner[:, -1].std():.1f}')
    dd = 1e-3; S = np.zeros((len(WC) + 1, m.Nz))
    for z in range(m.Nz):
        tp = np.zeros(m.Nz); tp[z] = dd
        hp, hm = m.solve(tp), m.solve(-tp)
        S[:-1, z] = (hp[WC] - hm[WC]) / (2 * dd); S[-1, z] = (m.goalA(hp) - m.goalA(hm)) / (2 * dd)
    np.savez(f'{OUT}/lin.npz', S=S, GAM=m.Gam, mu0=np.r_[m.h0[WC], m.baseArea], WIN=WIN, WC=WC,
             ids=m.wellID[WIN].astype(str), xy=m.Wk[WIN, :2], zone=m.zone, pil=m.pil, zfac=m.zfac)
    print(f'saved {OUT}; {time.time() - t0:.0f}s')
