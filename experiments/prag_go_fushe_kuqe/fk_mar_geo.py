"""PRAG-MAR recomputed with the geolocated sea boundary (fk_geo.FKGeo).

fk_mar.py runs PRAG-MAR on the companion model, whose whole western margin is the sea. With the
boundary of the chloride study (sea contact only north of y = 29.5 km, coastal sector y >= 24 km)
the setting changes in three ways, and the rules below adapt the experiment to it. They were fixed
before the comparison was run.

1. No supply well is at risk without pumping. The lowest prior-mean head of an inside K-well in the
   sector is 2.6 m (A1) against the threshold h_c = delta * base = 1.0 m, and the intruded area
   (10.1 km^2) lies along the northern coast, where there are no wells. Pumping therefore has to be
   part of the problem: it is what puts the Fushe-Kuqe well field at risk.
2. Supply wells. The old pair A23 / R16 no longer fits: R16 lies in the southern plain, outside the
   sector. The companion rule took one well per sector; here the sector is split at the section
   A-A' (y = 36.5 km), which crosses the Fushe-Kuqe well field, and in each half the supply well is
   the inside K-well with the lowest prior-mean head, outside the published monitoring design.
3. Pumping rates. The companion rule chose supply wells whose prior intrusion probability was
   closest to 1/2, so that the risk question is open. Here the pumping rates Q_A, Q_B are set so
   that each well's own prior intrusion probability is 1/2 (both wells pumping, interference
   included), on a calibration ensemble independent of the evaluation ensemble.
Recharge candidates are the sector cells at least 1 km from both supply wells (recharge at the
pumping well itself would only mean pumping less). Every design uses the published selection rule:
top 3 cells, at least 6 km apart in northing.

Designs compared exactly on 2 000 prior realizations (base prior, as fk_mar.py):
  none       no recharge
  published  the three published MAR cells (companion boundary; A18 and P21 lie outside the sector)
  area       area adjoint recomputed with the new boundary and the pumping (the published pipeline)
  prag       PRAG-MAR closed form (two adjoint solves at the prior mean)
  ens        greedy optimum of the exact ensemble risk
Output: res_geo/mar_geo.json, res_geo/mar_geo_fields.npz.   Run: python3 fk_mar_geo.py  (~30 s, 4 cores)
Sensitivity: python3 fk_mar_geo.py equal  sets one pumping rate at both wells, chosen so that
P(A or B intruded) = 1/2 (res_geo/mar_geo_equal.json).
"""
import os, sys, json, time
import numpy as np
import scipy.sparse.linalg as spla
from multiprocessing import Pool
from scipy.stats import norm
from fk import FK, default_xlsx
from fk_geo import FKGeo

OUT = 'res_geo'
QS = [2500.0, 5000.0, 10000.0]       # m^3/day per recharge site
QREF = 5000.0
HC = 1.0
Y_SPLIT = 36.5                       # km, section A-A'
EXCL = 1.0                           # km, no recharge closer than this to a supply well
PUBLISHED_MON = ['P21', 'A12', 'A13', 'A21', 'A10']
N_CAL, N_EVAL = 2000, 2000
MODE = sys.argv[1] if len(sys.argv) > 1 else 'each'   # 'each': P(A) = P(B) = 1/2;  'equal': Q_A = Q_B, P(A or B) = 1/2
TAG = '' if MODE == 'each' else '_' + MODE

m = FKGeo()
LG = np.linalg.cholesky(m.Gam)


def well_cell(i):
    return m.cell_of(m.Wk[i, 0], m.Wk[i, 1])


# ---------------------------------------------------------------- supply wells (rule 2)
WIN = [i for i in np.flatnonzero(m.wellInside) if well_cell(i) >= 0 and m.valid[well_cell(i)]
       and m.wellID[i] not in PUBLISHED_MON]
def lowest(mask):
    c = [i for i in WIN if mask(m.Wk[i, 1])]
    return min(c, key=lambda i: m.h0[well_cell(i)])
iA, iB = lowest(lambda y: y >= Y_SPLIT), lowest(lambda y: y < Y_SPLIT)
cA, cB = well_cell(iA), well_cell(iB)
idA, idB = str(m.wellID[iA]), str(m.wellID[iB])


def realization(theta):
    """heads, drawdown per unit pumping at A and B, and the recharge adjoints of h_A, h_B."""
    lu = spla.splu(m.matrix(theta).tocsc())
    h = lu.solve(m.rhs)
    E = np.zeros((m.Nc, 2)); E[cA, 0] = 1; E[cB, 1] = 1
    u = lu.solve(E)                     # u[:, w]: head rise per unit recharge at supply well w
    g = lu.solve(E, trans='T')          # g[k, w] = dh_w / dQ_k (recharge at k)
    return lu, h, u, g


def cal_chunk(args):
    seed, n = args
    rng = np.random.default_rng(seed); out = []
    for _ in range(n):
        th = LG @ rng.standard_normal(m.Nz)
        _, h, u, _ = realization(th)
        out.append(np.r_[h[cA], h[cB], u[cA, 0], u[cA, 1], u[cB, 0], u[cB, 1], th])
    return out


def heads_pumped(H, QA, QB):
    """H columns: hA, hB, uAA, uAB, uBA, uBB (u: rise per unit recharge = drawdown per unit pumping)."""
    return H[:, 0] - QA * H[:, 2] - QB * H[:, 3], H[:, 1] - QA * H[:, 4] - QB * H[:, 5]


def calibrate(H):
    """Q_A, Q_B with median h_A = median h_B = h_c (each well's own P(intruded) = 1/2), or, in the
    'equal' mode, Q_A = Q_B with P(A or B intruded) = 1/2."""
    if MODE == 'equal':
        lo, hi = 0.0, 1e6
        for _ in range(60):
            mid = 0.5 * (lo + hi); a, b = heads_pumped(H, mid, mid)
            lo, hi = (mid, hi) if np.mean(np.minimum(a, b) < HC) < 0.5 else (lo, mid)
        return 0.5 * (lo + hi), 0.5 * (lo + hi)
    QA = QB = 0.0
    for _ in range(60):
        lo, hi = 0.0, 1e6
        for _ in range(60):
            mid = 0.5 * (lo + hi); a, _ = heads_pumped(H, mid, QB)
            lo, hi = (mid, hi) if np.median(a) > HC else (lo, mid)
        QA = 0.5 * (lo + hi)
        lo, hi = 0.0, 1e6
        for _ in range(60):
            mid = 0.5 * (lo + hi); _, b = heads_pumped(H, QA, mid)
            lo, hi = (mid, hi) if np.median(b) > HC else (lo, mid)
        QB_new = 0.5 * (lo + hi)
        if abs(QB_new - QB) < 1e-3: QB = QB_new; break
        QB = QB_new
    return QA, QB


QP = None
def rhs_pumped():
    r = m.rhs.copy(); r[cA] -= QP[0]; r[cB] -= QP[1]
    return r


def eval_chunk(args):
    seed, n = args
    rng = np.random.default_rng(seed); out = []
    for _ in range(n):
        th = LG @ rng.standard_normal(m.Nz)
        lu, _, _, g = realization(th)
        h = lu.solve(rhs_pumped())
        out.append((th, h[cA], h[cB], g[:, 0].astype(np.float32), g[:, 1].astype(np.float32)))
    return out


DESIGNS = None
def area_chunk(th):
    lu = spla.splu(m.matrix(th).tocsc()); h = lu.solve(rhs_pumped())
    res = [m.goalA(h)]
    for cells in DESIGNS:
        r = np.zeros(m.Nc); r[[c for c in cells if m.valid[c]]] = 1.0
        u = lu.solve(r)
        res += [m.goalA(h + Q * u) for Q in QS]
    return res


def allowed():
    d = lambda c: np.hypot(m.cx - m.cx[c], m.cy - m.cy[c])
    return m.valid & (d(cA) >= EXCL) & (d(cB) >= EXCL)


def topk(vals):
    return m.pick_topk(np.where(allowed(), vals, -np.inf), 3)


def site_info(cells):
    out = []
    for c in cells:
        w = int(np.argmin(np.hypot(m.Wk[:, 0] - m.cx[c], m.Wk[:, 1] - m.cy[c])))
        out.append({'cell': int(c), 'x': float(m.cx[c]), 'y': float(m.cy[c]), 'in_sector': bool(m.valid[c]),
                    'nearest_K_well': str(m.wellID[w]),
                    'dist_km': float(np.hypot(m.Wk[w, 0] - m.cx[c], m.Wk[w, 1] - m.cy[c]))})
    return out


if __name__ == '__main__':
    t0 = time.time(); os.makedirs(OUT, exist_ok=True)
    print(f'sector {m.valid.sum()} cells, baseline intruded area (no pumping) {m.baseArea:.1f} km^2')
    print(f'supply wells: A = {idA} ({m.cx[cA]:.2f}, {m.cy[cA]:.2f}) h0 {m.h0[cA]:.2f} m;  B = {idB} ({m.cx[cB]:.2f}, {m.cy[cB]:.2f}) h0 {m.h0[cB]:.2f} m')
    with Pool(4) as pool:
        Hc = np.array([x for c in pool.map(cal_chunk, [(7000 + k, N_CAL // 40) for k in range(40)]) for x in c])
    THc, Hc = Hc[:, 6:], Hc[:, :6]
    QP = calibrate(Hc)
    a, b = heads_pumped(Hc, *QP)
    dd = (QP[0] * Hc[:, 2] + QP[1] * Hc[:, 3]).mean(), (QP[0] * Hc[:, 4] + QP[1] * Hc[:, 5]).mean()
    print(f'pumping Q_A {QP[0]:.0f}, Q_B {QP[1]:.0f} m3/d; mean drawdown A {dd[0]:.2f} m, B {dd[1]:.2f} m; '
          f'calibration P(A) {np.mean(a < HC):.3f} P(B) {np.mean(b < HC):.3f} P(A or B) {np.mean(np.minimum(a, b) < HC):.3f}  ({time.time() - t0:.0f}s)')

    # ------------------------------------------------ closed forms at the prior mean, pumped state
    lu0, _, _, g0 = realization(np.zeros(m.Nz))
    h0p = lu0.solve(rhs_pumped())
    dz = 1e-3; S = np.zeros((2, m.Nz)); Hg = np.zeros(m.Nz)
    for z in range(m.Nz):
        tp = np.zeros(m.Nz); tp[z] = dz
        hp = spla.spsolve(m.matrix(tp), rhs_pumped()); hm = spla.spsolve(m.matrix(-tp), rhs_pumped())
        S[:, z] = [(hp[cA] - hm[cA]) / (2 * dz), (hp[cB] - hm[cB]) / (2 * dz)]
    C = S @ m.Gam @ S.T
    sA, sB = np.sqrt(np.diag(C)); r = C[0, 1] / (sA * sB)
    za, zb = (h0p[cA] - HC) / sA, (h0p[cB] - HC) / sB
    wA = norm.pdf(za) * norm.cdf((zb - r * za) / np.sqrt(1 - r * r)) / sA
    wB = norm.pdf(zb) * norm.cdf((za - r * zb) / np.sqrt(1 - r * r)) / sB
    RISK_c = wA * g0[:, 0] + wB * g0[:, 1]
    q = m.sig(h0p)
    wh = np.where(m.valid, m.area * (-(q * (1 - q)) / 0.15) / 1e6, 0.0)
    MAR_c = -lu0.solve(wh, trans='T')                   # area reduction per unit recharge
    prag_cells, area_cells = topk(RISK_c), topk(MAR_c)
    pub = FK(default_xlsx()).design_fields()
    pub_cells = np.array(pub.marCell)
    print(f'linear moments (pumped): hA {h0p[cA]:.3f} sd {sA:.3f}, hB {h0p[cB]:.3f} sd {sB:.3f}, r {r:.3f}')

    # ------------------------------------------------ exact evaluation
    with Pool(4) as pool:
        R1 = [x for c in pool.map(eval_chunk, [(9000 + k, N_EVAL // 40) for k in range(40)]) for x in c]
    TH = np.array([x[0] for x in R1]); HA = np.array([x[1] for x in R1]); HB = np.array([x[2] for x in R1])
    GA = np.array([x[3] for x in R1]); GB = np.array([x[4] for x in R1])
    print(f'evaluation ensemble {len(TH)}: P(A) {np.mean(HA < HC):.3f}, P(B) {np.mean(HB < HC):.3f}, P(A or B) {np.mean(np.minimum(HA, HB) < HC):.3f} ({time.time() - t0:.0f}s)')

    def risk(cells, Q):
        cs = [c for c in cells if m.valid[c]]
        ga = GA[:, cs].sum(1) if cs else 0.0; gb = GB[:, cs].sum(1) if cs else 0.0
        a_, b_ = HA + Q * ga, HB + Q * gb
        return np.mean(a_ < HC), np.mean(b_ < HC), np.mean(np.minimum(a_, b_) < HC)

    ok = allowed(); sel = []
    for _ in range(3):
        base_a = HA + QREF * (GA[:, sel].sum(1) if sel else 0); base_b = HB + QREF * (GB[:, sel].sum(1) if sel else 0)
        val = (1 / (1 + np.exp(-(HC - np.minimum(base_a[:, None] + QREF * GA, base_b[:, None] + QREF * GB)) / 0.05))).mean(0)
        used = [m.ys[m.aj[k]] for k in sel]
        for k in np.argsort(val):
            if not ok[k] or k in sel: continue
            if used and np.any(np.abs(m.ys[m.aj[k]] - np.array(used)) < m.P['space']): continue
            sel.append(int(k)); break
    ens_cells = np.array(sel)
    names = ['published', 'area', 'prag', 'ens']
    DESIGNS = [pub_cells, area_cells, prag_cells, ens_cells]
    with Pool(4) as pool:
        R2 = np.array(pool.map(area_chunk, list(TH), chunksize=25))
    out = {'rules': {'pumping_rule': MODE, 'y_split_km': Y_SPLIT, 'exclusion_km': EXCL, 'hc_m': HC, 'Q_mar': QS, 'n_cal': N_CAL, 'n_eval': N_EVAL},
           'sector_km2': float(m.valid.sum() * m.area / 1e6), 'area_no_pumping_km2': float(m.baseArea),
           'supply': {'A': {'id': idA, 'x': float(m.cx[cA]), 'y': float(m.cy[cA]), 'h0': float(m.h0[cA])},
                      'B': {'id': idB, 'x': float(m.cx[cB]), 'y': float(m.cy[cB]), 'h0': float(m.h0[cB])}},
           'pumping': {'QA': float(QP[0]), 'QB': float(QP[1]), 'drawdown_A': float(dd[0]), 'drawdown_B': float(dd[1])},
           'lin': {'hA': float(h0p[cA]), 'hB': float(h0p[cB]), 'sA': float(sA), 'sB': float(sB), 'r': float(r)},
           'none': {'pA': float(np.mean(HA < HC)), 'pB': float(np.mean(HB < HC)),
                    'pAB': float(np.mean(np.minimum(HA, HB) < HC)), 'area': float(R2[:, 0].mean())}}
    print(f"none: P(A or B) {out['none']['pAB']:.3f}, area {out['none']['area']:.1f} km^2")
    for j, (nm, cells) in enumerate(zip(names, DESIGNS)):
        rows = []
        for qi, Q in enumerate(QS):
            pa, pb, pab = risk(cells, Q)
            rows.append({'Q': Q, 'pA': float(pa), 'pB': float(pb), 'pAB': float(pab), 'area': float(R2[:, 1 + 3 * j + qi].mean())})
        out[nm] = {'sites': site_info(cells), 'rows': rows}
        lab = ', '.join(f"{s['nearest_K_well']}({s['x']:.1f},{s['y']:.1f}){'' if s['in_sector'] else '*'}" for s in out[nm]['sites'])
        print(f'{nm:9s} {lab}:  ' + '  '.join(f"Q {int(r_['Q'])}: P {r_['pAB']:.3f} area {r_['area']:.1f}" for r_ in rows))
    json.dump(out, open(f'{OUT}/mar_geo{TAG}.json', 'w'), indent=1)
    if MODE == 'each':                   # the prior draws, for the MATLAB port (chloride_fk/matlab/fkcl_prag_mar.m)
        D = np.vstack([THc, TH])
        np.savetxt(f'{OUT}/mar_geo_draws.csv', np.column_stack([np.r_[np.zeros(len(THc)), np.ones(len(TH))], D]),
                   delimiter=',', fmt='%.10g', header='set,' + ','.join(f'theta{k + 1}' for k in range(m.Nz)), comments='')
    np.savez(f'{OUT}/mar_geo_fields{TAG}.npz', RISK_c=RISK_c, MAR_c=MAR_c, h0p=h0p, valid=m.valid, cx=m.cx, cy=m.cy)
    print(f'done {time.time() - t0:.0f}s   (* = outside the sector, no effect)')
