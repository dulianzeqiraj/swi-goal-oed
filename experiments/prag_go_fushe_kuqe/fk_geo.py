"""The Fushe-Kuqe design model (fk.py) with the geolocated sea boundary of the chloride study.

fk.py follows the companion model: every row of the aquifer polygon drains to h = 0 at its
western-edge cell, so the whole 52 km western margin acts as the sea. Geolocated against the
GLOBE shoreline (chloride_fk/python/fkcl_geo.py), only the rows north of y = 29.5 km are in
contact with the Adriatic (92 rows, 23 km); south of them the western edge is an inland margin
behind the hills of Lalez Bay. FKGeo keeps every physical choice of fk.py (confined flow,
T = K b with b = 30 m, recharge R, the pilot zones and their prior, the Ghyben-Herzberg criterion
h < delta * base = 1.0 m) and changes only the boundary, exactly as in the chloride model
(chloride_fk/python/fkcl_model.py):
  * sea contact: the western-edge cell of each contact row drains to h = 0 at the shoreline
    through a link of length gap + dx/2 (conductance T dx / (gap + dx/2) per unit head);
  * domain: the coastal sector y >= 24 km connected to the contact cells (3545 cells,
    221.6 km^2); the southern cut and all other margins are no-flow. Without the cut the recharge
    of the southern plain would have to leave through the northern coast, which gives heads of
    hundreds of metres; in reality it drains to the Ishem and Erzen rivers.
Cells outside the sector keep h = 0 and are excluded from every goal.
"""
import os
import sys
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from fk import FK, default_xlsx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'chloride_fk', 'python'))


class FKGeo(FK):
    def __init__(self, xlsx=None, **kw):
        xlsx = xlsx or default_xlsx()
        super().__init__(xlsx, **kw)                       # builds the grid and the published fields
        import fkcl_model                                  # geometry of the chloride study
        G = fkcl_model.Model(xlsx)
        assert G.Nc == self.Nc and np.allclose(G.cx, self.cx) and np.allclose(G.cy, self.cy)
        self.valid = G.valid
        self.gI, self.gJ = G.fI, G.fJ                       # faces inside the sector
        self.sea_idx, self.sea_cond = G.sea_idx, G.sea_cond
        self.gap_row, self.sea_row = G.gap_row, G.sea_row
        self.seac = np.zeros(self.Nc, bool); self.seac[self.sea_idx] = True
        self.rhs = np.where(self.valid, self.P['R'] * self.area, 0.0)
        self.h0 = self.solve(np.zeros(self.Nz))
        self.baseArea = self.goalA(self.h0)

    # ------------------------------------------------------------------ physics
    def matrix(self, theta):
        if not hasattr(self, 'gI'):                        # during FK.__init__
            return FK.matrix(self, theta)
        T = self.K0c * np.exp(theta[self.zone]) * self.P['b']
        Tf = 0.5 * (T[self.gI] + T[self.gJ])
        diag = np.zeros(self.Nc)
        np.add.at(diag, self.gI, Tf); np.add.at(diag, self.gJ, Tf)
        diag[self.sea_idx] += T[self.sea_idx] * self.sea_cond
        diag[~self.valid] = 1.0
        I = np.r_[self.gI, self.gJ, np.arange(self.Nc)]; J = np.r_[self.gJ, self.gI, np.arange(self.Nc)]
        return sp.csc_matrix((np.r_[-Tf, -Tf, diag], (I, J)), shape=(self.Nc, self.Nc))

    def solve(self, theta):
        if not hasattr(self, 'gI'):
            return FK.solve(self, theta)
        return spla.spsolve(self.matrix(theta), self.rhs)

    def goalA(self, h):
        if not hasattr(self, 'gI'):
            return FK.goalA(self, h)
        return (self.area * self.sig(h))[self.valid].sum() / 1e6

    # ------------------------------------------------------------------ published pipeline, new boundary
    def design_fields(self):
        """the companion pipeline (linearized EIG of the intruded area, area-adjoint MAR field,
        top-k with 6 km spacing) recomputed on the sector with the geolocated boundary."""
        P = self.P; dd = 1e-3; Nz = self.Nz
        S = np.zeros((self.Nc, Nz)); Hg = np.zeros(Nz)
        for z in range(Nz):
            tp = np.zeros(Nz); tp[z] = dd
            hp, hm = self.solve(tp), self.solve(-tp)
            S[:, z] = (hp - hm) / (2 * dd); Hg[z] = (self.goalA(hp) - self.goalA(hm)) / (2 * dd)
        G = self.Gam; HGH = Hg @ G @ Hg
        gG = S @ G
        v = (gG * S).sum(1) + P['sn'] ** 2
        ifn = (gG @ Hg) ** 2 / v
        EIG = -0.5 * np.log(np.maximum(1 - ifn / HGH, 1e-12))
        EIG[~self.valid] = -np.inf
        q = self.sig(self.h0)
        # d(area)/dh with the sign convention of the published code; recharge raises h
        wh = np.where(self.valid, self.area * (-(q * (1 - q)) / 0.15) / 1e6, 0.0)
        lam = spla.spsolve(self.matrix(np.zeros(Nz)).T.tocsc(), wh)
        MAR = -lam                                          # this matrix has the opposite sign to fk.py
        MAR[~self.valid] = -np.inf
        self.S, self.Hg, self.EIG_c, self.MAR_c = S, Hg, EIG, MAR
        self.monCell = self.pick_topk(EIG, P['Nmon']); self.marCell = self.pick_topk(MAR, P['Nmar'])
        self.monID = self.snap(self.monCell); self.marID = self.snap(self.marCell)
        return self


if __name__ == '__main__':
    import time
    t0 = time.time()
    m = FKGeo().design_fields()
    v = m.valid
    print(f'sector cells {v.sum()} ({v.sum() * m.area / 1e6:.1f} km^2), sea-contact cells {len(m.sea_idx)}')
    print(f'baseline intruded area {m.baseArea:.1f} km^2; head in the sector: median {np.median(m.h0[v]):.2f} m, max {m.h0[v].max():.2f} m')
    print('monitoring (area EIG, new boundary):', ', '.join(m.monID))
    print('MAR (area adjoint, new boundary):   ', ', '.join(m.marID))
    print(f'{time.time() - t0:.1f} s')
