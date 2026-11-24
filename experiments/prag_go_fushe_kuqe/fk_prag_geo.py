"""PRAG-GO recomputed with the geolocated sea boundary (fk_geo.FKGeo).

fk_ens.py + fk_designs.py test PRAG-GO on the companion model, whose whole western margin is the sea.
This script repeats the test with the boundary of the chloride study and the setting of
fk_mar_geo.py. Choices, fixed before the comparison:
  model       FKGeo: companion physics, sea contact only on the northern 23 km (through the GLOBE
              shoreline gap), coastal sector y >= 24 km; prior 'base' (rho_F = 0.6) or 'rho805'
  supply      A1 and P10, pumped at the rates of fk_mar_geo.py (each well's own prior intrusion
              probability is 1/2; read from res_geo/mar_geo.json). Without pumping no well in the
              sector is at risk, so there would be no threshold question to design for.
  goals       rA     supply well A intruded (h_A < h_c = 1.0 m)
              rAB    A or B intruded
              rArea  intruded area of the sector above its prior median, rounded to 1 km^2 (the
                     companion test used 100 km^2, near its baseline area of 92.7 km^2)
  candidates  the other inside K-wells of the sector (16 wells), head readings with noise sd 0.2 m
  designs     every 3-well (560) and 5-well (4368) design; exact EIG of each goal by likelihood
              re-weighting (12 000 inner + 2 000 outer prior realizations), as fk_designs.py
  criteria    the eight of fk_designs.py: area, areaEns (Lemma 1 EIG of the intruded area, the
              published pipeline), hA, meanAB, pragLin, pragEns, pragNSA, pragNS (PRAG-GO)
Each criterion's best design is scored by its exact EIG as a percentage of the exact optimum.
The two published monitoring wells that lie in the sector (A10, A13) are scored as a pair against
the best pair.
Run: python3 fk_prag_geo.py [base|rho805]   (~5 min on 4 cores). Output: res_geo/prag_<prior>.json, .npz
"""
import os, sys, json, time, itertools
import numpy as np
import scipy.sparse.linalg as spla
from multiprocessing import Pool
from numpy.polynomial.hermite_e import hermegauss
from scipy.stats import norm, spearmanr
from fk_geo import FKGeo

PRIOR = sys.argv[1] if len(sys.argv) > 1 else 'base'
CFG = {'base': dict(), 'rho805': dict(rhoF=0.805)}[PRIOR]
OUT = 'res_geo'
SN = 0.2; HC = 1.0
NAMES = ['area', 'areaEns', 'hA', 'meanAB', 'pragLin', 'pragEns', 'pragNSA', 'pragNS']
GOALS = ['rA', 'rAB', 'rArea']
PUBLISHED_IN_SECTOR = ['A10', 'A13']        # the published monitoring wells P21, A12, A21 lie outside the sector

m = FKGeo(**CFG)
LG = np.linalg.cholesky(m.Gam)
MAR = json.load(open(f'{OUT}/mar_geo.json'))
SUP = MAR['supply']; QA, QB = MAR['pumping']['QA'], MAR['pumping']['QB']
cell = lambda i: m.cell_of(m.Wk[i, 0], m.Wk[i, 1])
ids_all = m.wellID.astype(str)
iA = int(np.flatnonzero(ids_all == SUP['A']['id'])[0]); iB = int(np.flatnonzero(ids_all == SUP['B']['id'])[0])
cA, cB = cell(iA), cell(iB)
WIN = [i for i in np.flatnonzero(m.wellInside) if cell(i) >= 0 and m.valid[cell(i)]]
CANDW = [i for i in WIN if i not in (iA, iB)]
WC = np.array([cell(i) for i in CANDW] + [cA, cB])
NC = len(CANDW); IA, IB, IR = NC, NC + 1, NC + 2
ids = np.array([ids_all[i] for i in CANDW])
RHS = m.rhs.copy(); RHS[cA] -= QA; RHS[cB] -= QB


def heads(theta):
    h = spla.splu(m.matrix(theta).tocsc()).solve(RHS)
    return np.r_[h[WC], m.goalA(h)]


def run_chunk(args):
    seed, n = args
    rng = np.random.default_rng(seed)
    return np.array([heads(LG @ rng.standard_normal(m.Nz)) for _ in range(n)])


def ensemble(n, seed0):
    with Pool(4) as p:
        return np.vstack(p.map(run_chunk, [(seed0 + k, n // 40) for k in range(40)]))


def h(p):
    p = np.clip(np.asarray(p, dtype=np.float64), 0.0, 1.0)
    return -(np.where(p > 0, p * np.log(np.where(p > 0, p, 1.0)), 0.0) + np.where(p < 1, (1 - p) * np.log(np.where(p < 1, 1 - p, 1.0)), 0.0))


gl_x, gl_w = np.polynomial.legendre.leggauss(64)
def Phi2(a, b, r):
    lo = -9.0; hi = np.maximum(a, lo + 1e-9)
    t = 0.5 * (hi - lo)[..., None] * gl_x + 0.5 * (hi + lo)[..., None]
    f = norm.pdf(t) * norm.cdf((b[..., None] - r * t) / np.sqrt(1 - r ** 2))
    return (0.5 * (hi - lo)[..., None] * f * gl_w).sum(-1)
hx, hw = hermegauss(24); hw = hw / hw.sum()
U1, U2 = np.meshgrid(hx, hx, indexing='ij'); W2 = np.outer(hw, hw).ravel(); UU = np.stack([U1.ravel(), U2.ravel()])


def lin_eig(A, d, g, s2):
    d = list(d); Sy = A[np.ix_(d, d)] + s2 * np.eye(len(d))
    if np.ndim(g) == 0:
        cg, vg = A[g, d], A[g, g]
    else:
        cg, vg = g @ A[:, d], g @ A @ g
    R2 = cg @ np.linalg.solve(Sy, cg) / vg
    return -0.5 * np.log(1 - min(R2, 1 - 1e-12))


def prag(A, mu, d, s2, tA, tB, two=True):
    d = list(d); Sy = A[np.ix_(d, d)] + s2 * np.eye(len(d))
    C = A[np.ix_([IA, IB], d)]
    K = C @ np.linalg.solve(Sy, C.T); Sz = A[np.ix_([IA, IB], [IA, IB])]; P = Sz - K
    if not two:
        R2 = min(K[0, 0] / Sz[0, 0], 1 - 1e-12); t = (tA - mu[IA]) / np.sqrt(Sz[0, 0])
        p = norm.cdf((t - np.sqrt(R2) * hx) / np.sqrt(1 - R2))
        return float(h(norm.cdf(t)) - (hw * h(p)).sum())
    w, V = np.linalg.eigh(K); Lk = V * np.sqrt(np.clip(w, 0, None)); mm = Lk @ UU
    s = np.sqrt(np.clip(np.diag(P), 1e-12, None)); r = np.clip(P[0, 1] / (s[0] * s[1]), -0.999, 0.999)
    p = 1 - Phi2((mu[IA] + mm[0] - tA) / s[0], (mu[IB] + mm[1] - tB) / s[1], r)
    r0 = Sz[0, 1] / np.sqrt(Sz[0, 0] * Sz[1, 1])
    p0 = 1 - Phi2(np.array((mu[IA] - tA) / np.sqrt(Sz[0, 0])), np.array((mu[IB] - tB) / np.sqrt(Sz[1, 1])), r0)
    return float(h(p0) - (W2 * h(p)).sum())


def normal_scores(v, ref):
    r = np.searchsorted(np.sort(ref), v, side='right')
    return norm.ppf(np.clip(r / (len(ref) + 1), 1e-6, 1 - 1e-6))


ST = {}
def criteria(d):
    A_lin, mu_lin, A_ens, mu_ens, A_ns, mu_ns, tA_ns, tB_ns = (ST[k] for k in ['A_lin', 'mu_lin', 'A_ens', 'mu_ens', 'A_ns', 'mu_ns', 'tA_ns', 'tB_ns'])
    s2 = SN ** 2; g = np.zeros(NC + 3); g[IA] = g[IB] = 0.5
    return [lin_eig(A_lin, d, IR, s2), lin_eig(A_ens, d, IR, s2), lin_eig(A_lin, d, IA, s2), lin_eig(A_lin, d, g, s2),
            prag(A_lin, mu_lin, d, s2, HC, HC), prag(A_ens, mu_ens, d, s2, HC, HC),
            prag(A_ns, mu_ns, d, 0.0, tA_ns, tB_ns, two=False), prag(A_ns, mu_ns, d, 0.0, tA_ns, tB_ns)]


def crit_chunk(designs):
    return [criteria(d) for d in designs]


DK = None; QW = None; P0 = None
def exact_one(d):
    Ssum = DK[d[0]].copy()
    for k in d[1:]:
        Ssum += DK[k]
    Ssum -= Ssum.min(1, keepdims=True)
    Ssum *= np.float32(-1.0 / (2 * SN * SN))
    np.maximum(Ssum, np.float32(-80.0), out=Ssum)
    w = np.exp(Ssum, out=Ssum)
    sw = w.sum(1, dtype=np.float64); p = (w @ QW).astype(np.float64) / sw[:, None]
    ess = (sw ** 2 / np.einsum('ij,ij->i', w, w).astype(np.float64)).mean()
    return np.r_[h(P0) - h(p).mean(0), ess]


def pmap(pool, f, items, k=16):
    parts = pool.map(f, [items[i::k] for i in range(k)])
    out = [None] * len(items)
    for i in range(k):
        out[i::k] = parts[i]
    return np.array(out)


if __name__ == '__main__':
    t0 = time.time()
    print(f'{PRIOR}: supply A = {SUP["A"]["id"]}, B = {SUP["B"]["id"]}, pumping {QA:.0f} / {QB:.0f} m3/d; {NC} candidate wells: {" ".join(ids)}')
    inner = ensemble(12000, 1000); outer = ensemble(2000, 5000)
    print(f'ensembles {time.time() - t0:.0f}s')
    AREA_T = float(np.round(np.median(inner[:, -1])))
    gi, go = inner[:, :NC], outer[:, :NC]
    hAi, hBi, ari = inner[:, IA], inner[:, IB], inner[:, IR]
    QIN = np.stack([hAi < HC, np.minimum(hAi, hBi) < HC, ari > AREA_T], 1).astype(np.float64)
    P0 = QIN.mean(0); QW = QIN.astype(np.float32)
    print(f'area threshold {AREA_T:.0f} km2; prior P(rA, rAB, rArea) = {np.round(P0, 3)}')
    # linearization at the prior mean (pumped), as fk_ens.py stage 2
    dz = 1e-3; S = np.zeros((NC + 3, m.Nz))
    for z in range(m.Nz):
        tp = np.zeros(m.Nz); tp[z] = dz
        S[:, z] = (heads(tp) - heads(-tp)) / (2 * dz)
    ST['A_lin'] = S @ m.Gam @ S.T; ST['mu_lin'] = heads(np.zeros(m.Nz))
    ST['A_ens'] = np.cov(inner.T); ST['mu_ens'] = inner.mean(0)
    rng = np.random.default_rng(3)
    yno = gi + SN * rng.standard_normal(gi.shape)
    nsY = np.column_stack([np.column_stack([normal_scores(yno[:, k], yno[:, k]) for k in range(NC)]),
                           normal_scores(hAi, hAi), normal_scores(hBi, hBi), normal_scores(ari, ari)])
    ST['A_ns'] = np.cov(nsY.T); ST['mu_ns'] = nsY.mean(0)
    ST['tA_ns'] = normal_scores(np.array([HC]), hAi)[0]; ST['tB_ns'] = normal_scores(np.array([HC]), hBi)[0]
    rng = np.random.default_rng(11)
    y = go + SN * rng.standard_normal(go.shape)
    DK = np.empty((NC, go.shape[0], gi.shape[0]), dtype=np.float32)
    for k in range(NC):
        DK[k] = (y[:, k, None] - gi[None, :, k]) ** 2
    res = {'prior': PRIOR, 'supply': SUP, 'pumping': MAR['pumping'], 'area_threshold_km2': AREA_T,
           'P0': P0.tolist(), 'H0': h(P0).tolist(), 'candidates': ids.tolist(), 'budgets': {}}
    with Pool(4) as pool:
        for k in (2, 3, 5):
            D = list(itertools.combinations(range(NC), k))
            LIN = pmap(pool, crit_chunk, D)
            EX = np.array(pool.map(exact_one, D, chunksize=8))
            print(f'{k}-well designs ({len(D)}): criteria and exact EIG {time.time() - t0:.0f}s')
            np.savez(f'{OUT}/prag_{PRIOR}_d{k}.npz', D=np.array(D), LIN=LIN, EX=EX)
            B = {'n_designs': len(D), 'goals': {}}
            for gk, gn in enumerate(GOALS):
                ex = EX[:, gk]; b = int(ex.argmax())
                G = {'optimum': {'wells': ids[list(D[b])].tolist(), 'eig': float(ex[b]), 'ess': float(EX[b, 3])}, 'criteria': {}}
                for j, nm in enumerate(NAMES):
                    i = int(LIN[:, j].argmax())
                    G['criteria'][nm] = {'wells': ids[list(D[i])].tolist(), 'eig': float(ex[i]), 'pct_opt': float(100 * ex[i] / ex[b]),
                                         'spearman': float(spearmanr(LIN[:, j], ex).correlation)}
                if k == 2:
                    pub = tuple(sorted(int(np.flatnonzero(ids == w)[0]) for w in PUBLISHED_IN_SECTOR))
                    G['published_in_sector'] = {'wells': PUBLISHED_IN_SECTOR, 'eig': float(ex[D.index(pub)]), 'pct_opt': float(100 * ex[D.index(pub)] / ex[b])}
                B['goals'][gn] = G
                cr = G['criteria']
                print(f'  [{k}] {gn}: optimum {G["optimum"]["wells"]} {ex[b]:.3f} nats (H0 {h(P0[gk]):.3f}); '
                      + ', '.join(f'{nm} {cr[nm]["pct_opt"]:.0f}%' for nm in NAMES)
                      + (f'; published pair {G["published_in_sector"]["pct_opt"]:.0f}%' if k == 2 else ''))
            res['budgets'][str(k)] = B
    json.dump(res, open(f'{OUT}/prag_{PRIOR}.json', 'w'), indent=1)
    print(f'done {time.time() - t0:.0f}s')
