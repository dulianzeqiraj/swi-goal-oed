"""PRAG-MAR: managed-aquifer-recharge sites chosen for the supply-well risk instead of the area.

For fixed conductivity the head is linear in a point recharge Q at cell k:
    h(theta, Q) = h(theta) + Q * g(theta)_k,   g_A(theta) = -A(theta)^{-T} e_A,
so one transposed solve per supply well gives the effect of recharge at every cell at once.
Closed form at the prior mean (linear-Gaussian moments of h_A, h_B):
    P(intrusion at A or B) = 1 - Phi2(a, b; r),  a = (mu_A - hc) / s_A,  b = (mu_B - hc) / s_B
    -dP/dQ_k = phi(a) Phi((b - r a)/sqrt(1-r^2)) g_A,k / s_A + phi(b) Phi((a - r b)/sqrt(1-r^2)) g_B,k / s_B
The published pipeline instead ranks cells by the adjoint of the intruded area (MAR_c).
Both rankings use the published selection rule (top 3, at least 6 km apart in northing); the
designs are then compared exactly on 2 000 prior realizations, together with the greedy design
that maximizes the exact ensemble risk reduction.
"""
import sys, json, time
import numpy as np
import scipy.sparse.linalg as spla
from multiprocessing import Pool
from scipy.stats import norm
from fk import FK, default_xlsx

XLSX = default_xlsx()
QS = [2500.0, 5000.0, 10000.0]          # m^3/day per site
QREF = 5000.0
HC = 1.0
m = FK(XLSX).design_fields()
meta = json.load(open('res_base/meta.json'))
L = np.load('res_base/lin.npz', allow_pickle=True)
cA, cB = int(L['WC'][meta['iA']]), int(L['WC'][meta['iB']])
LG = np.linalg.cholesky(m.Gam)


def adjoints(theta):
    lu = spla.splu(m.matrix(theta).tocsc())
    h = lu.solve(m.rhs)
    E = np.zeros((m.Nc, 2)); E[cA, 0] = 1; E[cB, 1] = 1
    g = -lu.solve(E, trans='T')          # g[:, 0]: dh_A/dQ_k for every k
    return lu, h, g


def pass1(args):
    seed, n = args
    rng = np.random.default_rng(seed); out = []
    for _ in range(n):
        th = LG @ rng.standard_normal(m.Nz)
        _, h, g = adjoints(th)
        out.append((th, h[cA], h[cB], g[:, 0].astype(np.float32), g[:, 1].astype(np.float32)))
    return out


DESIGNS = None
def pass2(th):
    lu = spla.splu(m.matrix(th).tocsc()); h = lu.solve(m.rhs)
    res = [m.goalA(h)]
    for cells in DESIGNS:
        r = np.zeros(m.Nc); r[list(cells)] = -1.0
        u = lu.solve(r)                   # head change per unit Q at every site
        res += [m.goalA(h + Q * u) for Q in QS]
    return res


def topk_spaced(vals, k=3):
    return m.pick_topk(np.where(m.coastc, -np.inf, vals), k)


if __name__ == '__main__':
    t0 = time.time()
    # ------------------------------------------------ closed forms at the prior mean
    S = L['S']; G = L['GAM']
    sA, sB = np.sqrt(S[meta['iA']] @ G @ S[meta['iA']]), np.sqrt(S[meta['iB']] @ G @ S[meta['iB']])
    r = (S[meta['iA']] @ G @ S[meta['iB']]) / (sA * sB)
    _, h0, g0 = adjoints(np.zeros(m.Nz))
    a, b = (h0[cA] - HC) / sA, (h0[cB] - HC) / sB
    wA = norm.pdf(a) * norm.cdf((b - r * a) / np.sqrt(1 - r * r)) / sA
    wB = norm.pdf(b) * norm.cdf((a - r * b) / np.sqrt(1 - r * r)) / sB
    RISK_c = wA * g0[:, 0] + wB * g0[:, 1]
    prag_cells = topk_spaced(RISK_c)
    area_cells = np.array(m.marCell)
    print(f'linear moments: hA {h0[cA]:.3f} sd {sA:.3f}, hB {h0[cB]:.3f} sd {sB:.3f}, r {r:.3f}; weights wA {wA:.3f} wB {wB:.3f}')
    print('published (area adjoint):', m.snap(area_cells), ' PRAG-MAR:', m.snap(prag_cells))
    # ------------------------------------------------ exact: per-realization adjoints
    with Pool(4) as pool:
        R1 = [x for c in pool.map(pass1, [(9000 + k, 50) for k in range(40)]) for x in c]
    TH = np.array([x[0] for x in R1]); HA = np.array([x[1] for x in R1]); HB = np.array([x[2] for x in R1])
    GA = np.array([x[3] for x in R1]); GB = np.array([x[4] for x in R1])
    print(f'pass 1 ({len(TH)} realizations) {time.time() - t0:.0f}s; P(A or B) = {np.mean(np.minimum(HA, HB) < HC):.3f}')

    def risk(cells, Q):
        ga = GA[:, list(cells)].sum(1); gb = GB[:, list(cells)].sum(1)
        a_, b_ = HA + Q * ga, HB + Q * gb
        return np.mean(a_ < HC), np.mean(b_ < HC), np.mean(np.minimum(a_, b_) < HC)

    # greedy on the exact ensemble risk (same spacing rule), smoothed by a 0.05 m logistic for ranking
    sel = []
    for _ in range(3):
        best, bv = None, np.inf
        base_a = HA + QREF * (GA[:, sel].sum(1) if sel else 0); base_b = HB + QREF * (GB[:, sel].sum(1) if sel else 0)
        za = base_a[:, None] + QREF * GA; zb = base_b[:, None] + QREF * GB
        val = (1 / (1 + np.exp(-(HC - np.minimum(za, zb)) / 0.05))).mean(0)
        used = [m.ys[m.aj[k]] for k in sel]
        for k in np.argsort(val):
            if m.coastc[k] or k in sel: continue
            if used and np.any(np.abs(m.ys[m.aj[k]] - np.array(used)) < m.P['space']): continue
            best = k; break
        sel.append(int(best))
    ens_cells = np.array(sel)
    print('ensemble-greedy:', m.snap(ens_cells))
    DESIGNS = [area_cells, prag_cells, ens_cells]
    with Pool(4) as pool:
        R2 = np.array(pool.map(pass2, list(TH), chunksize=25))
    print(f'pass 2 {time.time() - t0:.0f}s')
    out = {'Q': QS, 'base': {'pA': float(np.mean(HA < HC)), 'pB': float(np.mean(HB < HC)),
                             'pAB': float(np.mean(np.minimum(HA, HB) < HC)), 'area': float(R2[:, 0].mean())}}
    for j, (nm, cells) in enumerate(zip(['area', 'prag', 'ens'], DESIGNS)):
        rows = []
        for q, Q in enumerate(QS):
            pa, pb, pab = risk(cells, Q)
            rows.append({'Q': Q, 'pA': float(pa), 'pB': float(pb), 'pAB': float(pab),
                         'area': float(R2[:, 1 + 3 * j + q].mean())})
        out[nm] = {'cells': [int(c) for c in cells], 'ids': m.snap(cells),
                   'xy': [[float(m.cx[c]), float(m.cy[c])] for c in cells], 'rows': rows}
        print(nm, m.snap(cells), [(r_['Q'], round(r_['pAB'], 3), round(r_['area'], 1)) for r_ in rows])
    out['lin'] = {'hA': float(h0[cA]), 'hB': float(h0[cB]), 'sA': float(sA), 'sB': float(sB), 'r': float(r)}
    json.dump(out, open('res_base/mar.json', 'w'), indent=1)
    np.savez('res_base/mar_fields.npz', RISK_c=RISK_c, MAR_c=m.MAR_c, EIG_c=m.EIG_c, h0=m.h0)
    print(f'done {time.time() - t0:.0f}s')
