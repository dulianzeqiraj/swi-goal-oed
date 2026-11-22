"""PUSI-GO, stage 1: run the calibrated chloride ensemble of the Fushe-Kuqe sector once and store what every
well-placement objective needs.

PUSI-GO (pusi: the well) is the innovation of the complete-system document of the Fushe-Kuqe coastal aquifer. It
puts the hydrochemistry into the objective that places wells: the failure event of a supply well is the
drinking-water chloride standard in its screen, not the head proxy h < 1 m of PRAG-GO / PRAG-MAR / VENDI-GO.

Model: the areal chloride model of chloride_fk (Strack single potential phi, dispersive interface, geolocated sea
boundary, sector y >= 24 km), with the 20 000 prior draws and calibration weights of chloride_fk/results/
calib_ensemble.npz (likelihood weighting on the documented facts; ESS 3 249).

The flow operator A(K) of div(K grad phi) + R = 0 is symmetric, so one factorisation and one solve with the two unit
sources at the supply wells A1 and P10 give, for every cell k,
    u[k, w] = d phi_k / d Q_w (injection at well w)  =  d phi_w / d Q_k (injection at cell k),
which is the response of each supply well to recharge anywhere (the adjoint) and the drawdown of pumping.
Stored (float64) at the supply wells, at the 16 candidate monitoring wells and at the recharge candidates:
phi0 (no pumping, no recharge), uA, uB. Output res/ens.npz (about 120 MB, not committed).
Run: python3 pusi_run.py      (about 4 minutes on 4 cores)
"""
import os, sys, time
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np
import scipy.sparse.linalg as spla
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'chloride_fk', 'python'))
import fkcl_model as M  # noqa: E402

RES = os.path.join(HERE, 'res')
SUPPLY = ('A1', 'P10')                                     # supply wells of PRAG-MAR (geolocated): one per half of the sector
MON_IDS = ['P3', 'P4', 'P12', 'P13', 'P17', 'A3', 'A4', 'A9', 'A10', 'A11', 'A13', 'A23', 'A24', 'A25', 'A28', 'A30']
EXCL = 1.0                                                 # km: no recharge closer than this to a supply well
# designs of the head-proxy pipeline (fk model, geolocated boundary; res_geo/mar_geo.json), as cell centres (km)
FK_PRAG_MAR = [(3.25, 34.25), (8.75, 28.25), (9.75, 40.25)]
FK_GREEDY = [(4.0, 36.0), (9.0, 30.0), (10.0, 24.0)]

m = M.Model()
b = m.base
ids = np.array([str(x) for x in b.wellID])


def wcell(name):
    i = int(np.flatnonzero(ids == name)[0])
    return b.cell_of(*b.Wk[i, :2])


def ccell(x, y):
    return b.cell_of(x, y)


cS = np.array([wcell(n) for n in SUPPLY])
cM = np.array([wcell(n) for n in MON_IDS])
# recharge candidates: sector cells on the 1 km lattice, at least EXCL km from both supply wells, plus the fk designs
lat = m.valid & (np.abs(m.cx - np.round(m.cx)) < 1e-9) & (np.abs(m.cy - np.round(m.cy)) < 1e-9)
far = np.min(np.hypot(m.cx[:, None] - m.cx[cS][None, :], m.cy[:, None] - m.cy[cS][None, :]), 1) >= EXCL
cR = list(np.flatnonzero(lat & far))
for xy in FK_PRAG_MAR + FK_GREEDY:
    c = ccell(*xy)
    if c not in cR:
        cR.append(c)
cR = np.array(cR)
SAVE = np.r_[cS, cM, cR]


def chunk(args):
    lo, hi = args
    E = np.load(os.path.join(ROOT, 'chloride_fk', 'results', 'calib_ensemble.npz'))
    out = np.empty((hi - lo, 3, len(SAVE)))
    U = np.zeros((m.Nc, 2)); U[cS[0], 0] = 1.0; U[cS[1], 1] = 1.0
    for j, i in enumerate(range(lo, hi)):
        K = m.K_field(E['theta'][i], E['eta'][i])
        lu = spla.splu(m.matrix(K).tocsc())
        phi = lu.solve(np.where(m.valid, E['R'][i] * m.area, 0.0))
        u = lu.solve(U)
        out[j, 0], out[j, 1], out[j, 2] = phi[SAVE], u[SAVE, 0], u[SAVE, 1]
    return out


if __name__ == '__main__':
    os.makedirs(RES, exist_ok=True)
    E = np.load(os.path.join(ROOT, 'chloride_fk', 'results', 'calib_ensemble.npz'))
    N = len(E['weight'])
    t = time.time()
    edges = np.linspace(0, N, 81).astype(int)
    with Pool(4) as pool:
        parts = pool.map(chunk, list(zip(edges[:-1], edges[1:])))
    X = np.concatenate(parts, 0)
    np.savez(os.path.join(RES, 'ens.npz'), phi0=X[:, 0], uA=X[:, 1], uB=X[:, 2], cS=cS, cM=cM, cR=cR,
             mon_ids=np.array(MON_IDS), supply=np.array(SUPPLY),
             fk_prag_mar=np.array([ccell(*xy) for xy in FK_PRAG_MAR]), fk_greedy=np.array([ccell(*xy) for xy in FK_GREEDY]),
             **{k: E[k] for k in ('weight', 'theta', 'R', 'eta', 'b_c', 'b_e', 'L_B', 'ground', 'w', 'Cl_s')})
    print(f'{N} draws, {len(cR)} recharge candidates, {len(cM)} monitoring wells, {time.time() - t:.0f} s')
