"""SPIRANCA-GO test bed: a head-based chloride alarm for a supply well of the Fushe-Kuqe sector that must stay
valid after the pumping decision and under a warming the rain gauge does not record.

Physics: the areal model of the chloride study (chloride_fk/python/fkcl_model.py): steady Strack potential phi with
recharge, the two supply wells of PRAG-GO (A1, P10) and a hidden private abstraction spread over the coastal plain.
phi is linear in the sources, so every season is a linear combination of four unit responses:
    phi = R * phi_R + Q_A * phi_A + Q_B * phi_B + H * phi_H          (phi_A, phi_B, phi_H: responses to unit sinks)
The goal: chloride in the upper screen of A1 (the first aquifer) above 250 mg/L, i.e. phi at A1 below phi*.

Seasons (anchors are recorded, the rest is not):
    r      rainfall anomaly at the gauge (anchor), N(0, 1)
    uA, uB operator's pumping anomalies of A1 and P10 (anchors): 0.25 U(-1, 1) - 0.08 r
    R      recharge     R0 (1 + 0.25 r + 0.10 eR)          eR unrecorded infiltration variability
    H      private abstraction  Hbar (1 - 0.25 r + 0.15 eH) eH unrecorded
    X      phi at the monitoring wells (heads converted with the Strack transform) + noise (0.1 m of head)
    Y      phi at A1
Future: the decision sets uA = 0.6, uB = 0.3 (known, outside the record), and a warming acts like a drought the gauge
does not see: R -= 0.25 R0 du, H += 0.25 Hbar du with du in [0, DU_MAX] (unknown; one-sided).
Stress test outside the anchor span: H += 0.3 Hbar with no change of R.
"""
import os, sys
import numpy as np
import scipy.sparse.linalg as spla
from scipy.special import ndtr

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'chloride_fk', 'python'))
from fkcl_model import Model, DELTA, CL_F, SCREEN, screen_average  # noqa: E402

SUPPLY = ('A1', 'P10')
QBAR0 = np.array([3756.7, 17182.9])        # PRAG-GO rates (m3/d), scaled per aquifer below
HFRAC = 0.4                                # private abstraction, fraction of the utility's
CL_LIM = 250.0
U_DEC = np.array([0.6, 0.3])               # the decision (pumping anomalies of A1 and P10)
DU_MAX = 1.5                               # the largest unrecorded warming, in rainfall-anomaly units
HEAD_SD = 0.10                             # m, head noise of a monitoring well
P_EXC_DEC = 0.15                           # exceedance frequency after the decision without warming (sets the scale)


class Bed:
    def __init__(self):
        self.m = m = Model()
        b = m.base
        ids = b.wellID.astype(str)
        self.cells, self.ids = [], []
        for i, (x, y) in enumerate(b.Wk[:, :2]):
            c = b.cell_of(x, y)
            if c >= 0 and m.valid[c] and b.wellInside[i]:
                self.cells.append(c); self.ids.append(ids[i])
        self.cA = self.cells[self.ids.index(SUPPLY[0])]
        self.cB = self.cells[self.ids.index(SUPPLY[1])]
        keep = [k for k, s in enumerate(self.ids) if s not in SUPPLY]
        self.mon_ids = [self.ids[k] for k in keep]
        self.mon_cells = np.array([self.cells[k] for k in keep])
        # private abstraction: the coastal plain between 0.5 and 4 km from the shoreline
        self.hmask = m.valid & (m.dist > 0.5) & (m.dist < 4.0)

    def truth(self, p):
        """unit responses of one aquifer (prior draw p)."""
        m = self.m
        K = m.K_field(p['theta'], p['eta'])
        lu = spla.splu(m.matrix(K).tocsc())
        n = m.Nc
        rR = np.where(m.valid, m.area, 0.0)
        eA = np.zeros(n); eA[self.cA] = -1.0
        eB = np.zeros(n); eB[self.cB] = -1.0
        eH = np.where(self.hmask, -1.0, 0.0); eH /= -eH.sum()
        U = np.column_stack([lu.solve(rR), lu.solve(eA), lu.solve(eB), lu.solve(eH)])
        d, B = m.geometry(p)
        return dict(U=U, d=d, B=B, w=p['w'], Cl_s=p['Cl_s'], R0=p['R'])

    def cl_at(self, T, phi, c):
        """chloride [mg/L] of the upper screen (the first aquifer, the goal of the chloride study) at cell c."""
        d, B = T['d'][c], T['B'][c]
        phi = np.asarray(phi, float)
        phit = 0.5 * DELTA * B ** 2
        zeta = np.where(phi < phit, d + np.sqrt(2 * np.maximum(phi, 0) / DELTA), phi / (DELTA * B) + d + 0.5 * B)
        L = min(SCREEN, B)
        f = screen_average(d, d + L, zeta, T['w'])
        return CL_F + f * (T['Cl_s'] - CL_F)

    def phi_star(self, T, c):
        """phi at which the upper screen of cell c reaches 250 mg/L (chloride decreases with phi)."""
        lo, hi = 0.0, 5000.0
        if self.cl_at(T, hi, c) > CL_LIM:
            return np.nan
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if self.cl_at(T, mid, c) > CL_LIM: lo = mid
            else: hi = mid
        return 0.5 * (lo + hi)

    def dphi_dh(self, T, phi, c):
        B = T['B'][c]
        return np.where(phi < 0.5 * DELTA * B ** 2, np.sqrt(2 * np.maximum(phi, 1e-6) / DELTA), B)


def seasons(rng, n, T, s, decision=None, du=0.0, h_extra=0.0):
    """n seasons of one aquifer at pumping scale s. Returns anchors A (n x 3), X (n x len(mon)), Y (n)."""
    r = rng.standard_normal(n)
    if decision is None:
        uA = 0.25 * rng.uniform(-1, 1, n) - 0.08 * r
        uB = 0.25 * rng.uniform(-1, 1, n) - 0.08 * r
    else:
        uA = np.full(n, decision[0]); uB = np.full(n, decision[1])
    R0 = T['R0']; Qb = s * QBAR0; Hb = HFRAC * Qb.sum()
    R = R0 * (1 + 0.25 * r + 0.10 * rng.standard_normal(n)) - 0.25 * R0 * du
    H = Hb * (1 - 0.25 * r + 0.15 * rng.standard_normal(n)) + 0.25 * Hb * du + h_extra * Hb
    S = np.column_stack([R, Qb[0] * (1 + uA), Qb[1] * (1 + uB), H])   # the four sources of each season
    return np.column_stack([r, uA, uB]), S


def observe(rng, S, T, cells, xsd):
    phi = S @ T['U'][cells].T
    return phi + rng.standard_normal(phi.shape) * xsd
