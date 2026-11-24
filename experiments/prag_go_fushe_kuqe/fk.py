"""Python port of src/fushe_kuqe_field_design.m (the shared Fushe-Kuqe design model).

Confined areal flow div(T grad h) = -R on the real aquifer polygon, coast (western envelope)
at h = 0, IDW conductivity from the 43 K-wells, 12 pilot zones with a facies prior, and the
Ghyben-Herzberg intrusion criterion h < delta * base. Every step follows the MATLAB file line
by line so that the port reproduces the published design (README / revision_r2 log):
baseline intruded area 92.7 km^2, monitoring P21, A12, A13, A21, A10 and MAR A18, P21, P16.
"""
import numpy as np
import pandas as pd
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from matplotlib.path import Path

def default_xlsx():
    """the workbook next to the scripts, or the repository copy in data/."""
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    for f in (os.path.join(os.getcwd(), 'Fushe_Kuqe_All_Data.xlsx'), os.path.join(here, '..', '..', 'data', 'Fushe_Kuqe_All_Data.xlsx')):
        if os.path.exists(f):
            return f
    raise FileNotFoundError('Fushe_Kuqe_All_Data.xlsx (see data/README.txt)')


DEFAULT = dict(b=30.0, base=40.0, R=5e-4, delta=0.025, dx=0.25, sn=0.2, rhoF=0.6, Nmon=5, Nmar=3,
               space=6.0, faciesRule='legacy', nzx=5, nzy=8, Lc=8.0)


def inpolygon(px, py, bx, by):
    """MATLAB inpolygon: interior or on the edge."""
    path = Path(np.column_stack([bx, by]))
    pts = np.column_stack([px, py])
    inside = path.contains_points(pts)
    # points lying exactly on an edge count as inside in MATLAB
    x1, y1, x2, y2 = bx[:-1], by[:-1], bx[1:], by[1:]
    for c in np.array_split(np.arange(len(pts)), max(1, len(pts) // 2000)):
        X, Y = px[c, None], py[c, None]
        cross = (x2 - x1) * (Y - y1) - (y2 - y1) * (X - x1)
        within = (np.minimum(x1, x2) - 1e-12 <= X) & (X <= np.maximum(x1, x2) + 1e-12) & \
                 (np.minimum(y1, y2) - 1e-12 <= Y) & (Y <= np.maximum(y1, y2) + 1e-12)
        on = (np.abs(cross) < 1e-12) & within
        inside[c] |= on.any(1)
    return inside


def matlab_colon(a, step, b):
    n = int(np.floor((b - a) / step + 1e-10))
    return a + step * np.arange(n + 1)


class FK:
    def __init__(self, xlsx, **kw):
        P = dict(DEFAULT); P.update(kw); self.P = P
        P['hcrit'] = P['base'] * P['delta']
        B = pd.read_excel(xlsx, sheet_name='3_Boundary_Coords').iloc[:, 1:3].to_numpy(float)
        B = B[np.all(np.isfinite(B), 1)]
        W = pd.read_excel(xlsx, sheet_name='2_All_Wells')
        WXY = W.iloc[:, 1:3].to_numpy(float); WK = W.iloc[:, 3].to_numpy(float); ID = W.iloc[:, 0].astype(str).to_numpy()
        ok = np.all(np.isfinite(np.column_stack([WXY, WK])), 1)
        self.wellInside = (W['Inside_Aquifer'].astype(str).str.upper() == 'YES').to_numpy()[ok]
        WXY, WK, self.wellID = WXY[ok], WK[ok], ID[ok]
        x0, y0 = B[:, 0].min(), B[:, 1].min(); self.x0, self.y0 = x0, y0
        self.Bk = (B - [x0, y0]) / 1000.0
        self.Wk = np.column_stack([(WXY - [x0, y0]) / 1000.0, WK])
        dx = P['dx']; self.dx = dx
        xs = matlab_colon(0.0, dx, self.Bk[:, 0].max() + dx); ys = matlab_colon(0.0, dx, self.Bk[:, 1].max() + dx)
        self.xs, self.ys = xs, ys
        GX, GY = np.meshgrid(xs, ys); ny, nx = GX.shape; self.ny, self.nx = ny, nx
        inside = inpolygon(GX.ravel(), GY.ravel(), self.Bk[:, 0], self.Bk[:, 1]).reshape(ny, nx)
        self.inside = inside
        # active cells in MATLAB (column-major) order
        actF = np.flatnonzero(inside.ravel(order='F'))
        aj, ai = actF % ny, actF // ny
        self.aj, self.ai = aj, ai; Nc = len(actF); self.Nc = Nc
        idx = -np.ones((ny, nx), int); idx[aj, ai] = np.arange(Nc); self.idx = idx
        self.cx, self.cy = xs[ai], ys[aj]
        d = np.hypot(self.Wk[None, :, 0] - self.cx[:, None], self.Wk[None, :, 1] - self.cy[:, None]) + 1e-6
        w = 1.0 / d ** 2
        self.K0c = (w @ self.Wk[:, 2]) / w.sum(1)
        self.dxm = dx * 1000.0; self.area = self.dxm ** 2
        coast = np.zeros((ny, nx), bool)
        for j in range(ny):
            ii = np.flatnonzero(inside[j])
            if len(ii): coast[j, ii[0]] = True
        self.coast = coast; self.coastc = coast[aj, ai]
        # face list for the fixed sparsity pattern: (row k, neighbour l) for every non-coast k
        rows, cols = [], []
        for k in range(Nc):
            if self.coastc[k]: continue
            j, i = aj[k], ai[k]
            for dj, di in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                jj, ii = j + dj, i + di
                if 0 <= jj < ny and 0 <= ii < nx and inside[jj, ii]:
                    rows.append(k); cols.append(idx[jj, ii])
        self.fr, self.fc = np.array(rows), np.array(cols)
        self.nc_rows = np.flatnonzero(~self.coastc); self.c_rows = np.flatnonzero(self.coastc)
        self.rhs = np.where(self.coastc, 0.0, -P['R'] * self.dxm ** 2)
        # pilot zones
        pgx, pgy = np.meshgrid(np.linspace(1, xs.max() - 1, P['nzx']), np.linspace(2, ys.max() - 2, P['nzy']))
        pil = np.column_stack([pgx.ravel(order='F'), pgy.ravel(order='F')])
        pin = inpolygon(pil[:, 0], pil[:, 1], self.Bk[:, 0], self.Bk[:, 1])
        self.pil = pil[pin]; Nz = len(self.pil); self.Nz = Nz
        self.zone = np.argmin(np.hypot(self.pil[None, :, 0] - self.cx[:, None], self.pil[None, :, 1] - self.cy[:, None]), 1)
        self.zK = np.array([self.K0c[self.zone == z].mean() for z in range(Nz)])
        if P['faciesRule'] == 'harmonized':
            self.zfac = 1 + (self.zK < 150) + (self.zK < 75)
        else:
            self.zfac = 1 + (self.zK <= 150) + (self.zK <= 80)
        self.Gam = self.build_gamma(P['rhoF'])
        self.h0 = self.solve(np.zeros(Nz))
        self.baseArea = self.goalA(self.h0)

    # ------------------------------------------------------------------ physics
    def matrix(self, theta):
        Tc = self.K0c * np.exp(theta[self.zone]) * self.P['b']
        Tf = 0.5 * (Tc[self.fr] + Tc[self.fc])
        diag = np.zeros(self.Nc); np.add.at(diag, self.fr, -Tf); diag[self.c_rows] = 1.0
        I = np.r_[self.fr, np.arange(self.Nc)]; J = np.r_[self.fc, np.arange(self.Nc)]
        return sp.csc_matrix((np.r_[Tf, diag], (I, J)), shape=(self.Nc, self.Nc))

    def solve(self, theta):
        return spla.spsolve(self.matrix(theta), self.rhs)

    def sig(self, h, s=0.15):
        return 1.0 / (1.0 + np.exp(-(self.P['hcrit'] - h) / s))

    def goalA(self, h):
        return (self.area * self.sig(h)).sum() / 1e6

    def build_gamma(self, rhoF):
        pil, zf = self.pil, self.zfac
        D = np.hypot(pil[:, None, 0] - pil[None, :, 0], pil[:, None, 1] - pil[None, :, 1])
        G = np.exp(-D / self.P['Lc']) * np.where(zf[:, None] == zf[None, :], 1.0, rhoF)
        s = np.array([0.30, 0.45, 0.60])[zf - 1]
        return np.outer(s, s) * G + 1e-9 * np.eye(len(pil))

    # ------------------------------------------------------------------ published design
    def design_fields(self):
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
        s = 0.15; q = self.sig(self.h0)
        wh = self.area * (-(q * (1 - q)) / s) / 1e6
        A0 = self.matrix(np.zeros(Nz))
        lam = spla.spsolve(A0.T.tocsc(), wh); MAR = lam.copy(); MAR[self.coastc] = 0
        self.S, self.Hg, self.EIG_c, self.MAR_c = S, Hg, EIG, MAR
        self.monCell = self.pick_topk(EIG, P['Nmon']); self.marCell = self.pick_topk(MAR, P['Nmar'])
        self.monID = self.snap(self.monCell); self.marID = self.snap(self.marCell)
        return self

    def pick_topk(self, vals, k):
        order = np.argsort(-vals, kind='stable')
        sel, used = [], []
        for kk in order:
            if not np.isfinite(vals[kk]): continue
            N = self.ys[self.aj[kk]]
            if used and np.any(np.abs(N - np.array(used)) < self.P['space']): continue
            sel.append(kk); used.append(N)
            if len(sel) >= k: break
        return np.array(sel)

    def snap(self, cells):
        out = []
        for c in cells:
            w = np.argmin(np.hypot(self.Wk[:, 0] - self.cx[c], self.Wk[:, 1] - self.cy[c]))
            out.append(self.wellID[w])
        return out

    def cell_of(self, x, y):
        """active-cell index of the cell containing the point (km)."""
        i = int(round(x / self.dx)); j = int(round(y / self.dx))
        return self.idx[j, i]


if __name__ == '__main__':
    import sys, time
    t0 = time.time()
    m = FK(sys.argv[1] if len(sys.argv) > 1 else default_xlsx()).design_fields()
    Apoly = 0.5 * abs(np.dot(m.Bk[:, 0], np.roll(m.Bk[:, 1], 1)) - np.dot(m.Bk[:, 1], np.roll(m.Bk[:, 0], 1)))
    print(f'grid {m.nx}x{m.ny}, active cells {m.Nc} ({m.Nc * m.area / 1e6:.1f} km^2), polygon {Apoly:.1f} km^2, zones {m.Nz}, facies {np.bincount(m.zfac)[1:]}')
    print(f'baseline intruded area = {m.baseArea:.1f} km^2 ({100 * m.baseArea / Apoly:.1f}% of polygon); head max {m.h0.max():.2f} m')
    print('monitoring:', ', '.join(m.monID)); print('MAR:       ', ', '.join(m.marID))
    print(f'{time.time() - t0:.1f} s')
