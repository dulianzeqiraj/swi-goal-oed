"""Areal chloride model for the Fushe-Kuqe coastal aquifer (Python reference implementation).

Physics (steady, confined, Dupuit, sharp interface with a dispersive transition zone):
    div(K grad phi) + R = 0                         Strack (1976) single potential phi [m^2]
    phi = 0 at the Adriatic shoreline               Robin link from the western edge over the GLOBE gap
    no flow on all other margins                    (southern half of the western edge is an inland hill margin)
    zone 2 (phi < delta B^2/2):  zeta = d + sqrt(2 phi / delta)          interface depth below sea level [m]
    zone 1 (phi >= delta B^2/2): zeta = h/delta, h = phi/B + delta (d + B/2)
    c(z) = Phi((z - zeta)/w)                         relative seawater fraction at depth z (positive down)
    Cl   = Cl_f + cbar (Cl_s - Cl_f),  cbar = screen average of c over the well screen (closed form)
Geometry: aquifer-top depth d from the 43 DRASTIC depth values (IDW), minus a ground-elevation offset;
thickness B thins linearly with the distance from the shoreline, from b_c at the coast to b_e at L_B km.
K = eta_g * K_IDW * exp(theta_zone), with the facies-conditional prior of the companion study (rho_F = 0.805).

Every array is in the active-cell order of experiments/prag_go_fushe_kuqe/fk.py (MATLAB column-major).
"""
import os
import sys
import numpy as np
import pandas as pd
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.special import ndtr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'experiments', 'prag_go_fushe_kuqe'))
import fk  # noqa: E402

DER = os.path.join(HERE, '..', 'derived')
DELTA = 0.025          # (rho_s - rho_f)/rho_f
CL_F = 12.92           # mg/L, freshwater end-member (well 193, Cenameri & Beqiraj 2016)
GAP_MAX = 5.0          # km
Y_CUT = 24.0           # km; the chloride model covers the coastal Fushe-Kuqe-Lezhe sector north of this line
SCREEN = 40.0          # m, length of the shallow and of the deep well screen
CL_LIMIT = 250.0       # mg/L, drinking-water chloride guideline (EU 98/83/EC indicator value; WHO taste threshold)
RHO_F = 0.805          # field cross-facies correlation of the companion study


def phi_n(u):
    return np.exp(-0.5 * u * u) / np.sqrt(2 * np.pi)


def G(u):
    """antiderivative of the standard normal CDF: d/du G = Phi(u)."""
    return u * ndtr(u) + phi_n(u)


def screen_average(z1, z2, zeta, w):
    """mean of Phi((z - zeta)/w) over z in [z1, z2] (depths below sea level, positive down)."""
    L = np.maximum(z2 - z1, 1e-9)
    return w / L * (G((z2 - zeta) / w) - G((z1 - zeta) / w))


class Model:
    def __init__(self, xlsx=None):
        xlsx = xlsx or fk.default_xlsx()
        self.base = fk.FK(xlsx, rhoF=RHO_F)
        b = self.base
        self.Nc, self.dx, self.dxm, self.area = b.Nc, b.dx, b.dxm, b.area
        self.cx, self.cy, self.aj, self.ai = b.cx, b.cy, b.aj, b.ai
        # shoreline per row and sea-contact rows
        sr = pd.read_csv(os.path.join(DER, 'shoreline_rows.csv'))
        shore = sr['shore_x_km'].to_numpy()
        assert len(shore) >= b.ny, 'shoreline_rows.csv does not cover the grid'
        self.shore_row = shore[:b.ny]
        west = np.full(b.ny, np.nan); east = np.full(b.ny, np.nan)
        for j in range(b.ny):
            ii = np.flatnonzero(b.inside[j])
            if len(ii):
                west[j], east[j] = b.xs[ii[0]], b.xs[ii[-1]]
        self.west_row, self.east_row = west, east
        gap = west - self.shore_row
        self.sea_row = np.isfinite(gap) & (gap <= GAP_MAX)
        self.gap_row = np.clip(gap, 0.0, None)
        self.westc = b.coastc.copy()                         # western-edge cell of each row
        self.seac = self.westc & self.sea_row[self.aj]       # western-edge cells in contact with the sea
        # Euclidean distance [km] from each cell centre to the nearest point of the GLOBE shoreline
        pl = pd.read_csv(os.path.join(DER, 'shoreline_polyline.csv'))[['x_km', 'y_km']].to_numpy()
        from scipy.spatial import cKDTree
        self.dist = cKDTree(pl).query(np.column_stack([self.cx, self.cy]))[0]
        # cover (aquifer-top depth) from the DRASTIC depth parameter, IDW power 2
        W = pd.read_excel(xlsx, sheet_name='2_All_Wells')
        ok = W['Piezometric_Level_m'].notna().to_numpy()
        wx = (W['X_GaussKruger'].to_numpy(float)[ok] - b.x0) / 1000
        wy = (W['Y_GaussKruger'].to_numpy(float)[ok] - b.y0) / 1000
        wd = W['Piezometric_Level_m'].to_numpy(float)[ok]
        dd = np.hypot(wx[None, :] - self.cx[:, None], wy[None, :] - self.cy[:, None]) + 1e-6
        ww = 1.0 / dd ** 2
        self.cover = (ww @ wd) / ww.sum(1)
        self.Kidw = b.K0c.copy()
        self.zone, self.Nz, self.Gam = b.zone, b.Nz, b.Gam
        self.Lgam = np.linalg.cholesky(self.Gam)
        # FV structure (all interior faces, each once)
        idx = b.idx
        I, J = [], []
        for k in range(self.Nc):
            j, i = self.aj[k], self.ai[k]
            for dj, di in ((1, 0), (0, 1)):
                jj, ii = j + dj, i + di
                if jj < b.ny and ii < b.nx and b.inside[jj, ii]:
                    I.append(k); J.append(idx[jj, ii])
        self.fI, self.fJ = np.array(I), np.array(J)
        # cells not connected to the sea-contact cells (a 2-cell sliver at the southern tip) are excluded
        from scipy.sparse.csgraph import connected_components
        adj = sp.coo_matrix((np.ones(len(self.fI)), (self.fI, self.fJ)), shape=(self.Nc, self.Nc))
        _, lab = connected_components(adj, directed=False)
        good = np.unique(lab[self.seac])
        self.valid = np.isin(lab, good) & (self.cy >= Y_CUT)
        # re-check connectivity inside the sector
        keep0 = self.valid[self.fI] & self.valid[self.fJ]
        adj = sp.coo_matrix((np.ones(keep0.sum()), (self.fI[keep0], self.fJ[keep0])), shape=(self.Nc, self.Nc))
        _, lab = connected_components(adj, directed=False)
        self.valid &= np.isin(lab, np.unique(lab[self.seac & self.valid]))
        keep = self.valid[self.fI] & self.valid[self.fJ]
        self.fI, self.fJ = self.fI[keep], self.fJ[keep]
        self.sea_idx = np.flatnonzero(self.seac)
        self.sea_cond = self.dxm / (1000 * self.gap_row[self.aj[self.sea_idx]] + 0.5 * self.dxm)
        self.inside = b.inside

    # ------------------------------------------------------------------ flow
    def matrix(self, K):
        Kf = 0.5 * (K[self.fI] + K[self.fJ])
        n = self.Nc
        diag = np.zeros(n)
        np.add.at(diag, self.fI, Kf); np.add.at(diag, self.fJ, Kf)
        diag[self.sea_idx] += K[self.sea_idx] * self.sea_cond
        diag[~self.valid] = 1.0
        rows = np.r_[self.fI, self.fJ, np.arange(n)]
        cols = np.r_[self.fJ, self.fI, np.arange(n)]
        vals = np.r_[-Kf, -Kf, diag]
        return sp.csc_matrix((vals, (rows, cols)), shape=(n, n))

    def solve_phi(self, K, R):
        """phi [m^2] for conductivity K [m/d] and recharge R [m/d]."""
        rhs = np.where(self.valid, R * self.area, 0.0)
        return spla.spsolve(self.matrix(K), rhs)

    def K_field(self, theta, eta):
        return eta * self.Kidw * np.exp(theta[self.zone])

    # ------------------------------------------------------------------ geometry and chloride
    def geometry(self, p):
        d = np.maximum(self.cover - p['ground'], 1.0)
        B = p['b_e'] + (p['b_c'] - p['b_e']) * np.clip(1.0 - self.dist / p['L_B'], 0.0, 1.0)
        return d, B

    def state(self, phi, p):
        d, B = self.geometry(p)
        phit = 0.5 * DELTA * B ** 2
        z2 = phi < phit
        zeta = np.where(z2, d + np.sqrt(2 * np.maximum(phi, 0) / DELTA), 0.0)
        h1 = phi / B + DELTA * (d + 0.5 * B)
        h = np.where(z2, DELTA * d + np.sqrt(2 * DELTA * np.maximum(phi, 0)), h1)
        zeta = np.where(z2, zeta, h1 / DELTA)
        return h, zeta, d, B

    def chloride(self, zeta, d, B, w, Cl_s):
        """screen-averaged chloride [mg/L] at three depths: upper ('sh', the first aquifer: top SCREEN m),
        middle ('mid', a SCREEN-m interval centred at mid-thickness, proxy for the second aquifer) and
        base ('dp': bottom SCREEN m, the wedge toe zone)."""
        L = np.minimum(SCREEN, B)
        zm = d + 0.5 * B
        f = dict(sh=screen_average(d, d + L, zeta, w),
                 mid=screen_average(zm - 0.5 * L, zm + 0.5 * L, zeta, w),
                 dp=screen_average(d + B - L, d + B, zeta, w))
        Cl = {k: CL_F + v * (Cl_s - CL_F) for k, v in f.items()}
        return Cl, f

    # ------------------------------------------------------------------ prior
    def sample_prior(self, n, rng):
        th = (self.Lgam @ rng.standard_normal((self.Nz, n))).T
        P = dict(theta=th,
                 R=5e-4 * np.exp(0.7 * rng.standard_normal(n)),
                 eta=rng.uniform(0.3, 0.8, n),
                 b_c=rng.uniform(180.0, 200.0, n),
                 b_e=rng.uniform(5.0, 10.0, n),
                L_B=rng.uniform(12.0, 20.0, n),
                 ground=rng.uniform(0.0, 5.0, n),
                 w=20.0 * np.exp(0.6 * rng.standard_normal(n)),
                 Cl_s=rng.uniform(20500.0, 22000.0, n))
        return P

    @staticmethod
    def one(P, i):
        return {k: (v[i] if k != 'theta' else v[i]) for k, v in P.items()}

    def run(self, p):
        K = self.K_field(p['theta'], p['eta'])
        phi = self.solve_phi(K, p['R'])
        h, zeta, d, B = self.state(phi, p)
        Cl, f = self.chloride(zeta, d, B, p['w'], p['Cl_s'])
        return dict(phi=phi, h=h, zeta=zeta, d=d, B=B, Cl_sh=Cl['sh'], Cl_mid=Cl['mid'], Cl_dp=Cl['dp'],
                    f_sh=f['sh'], f_mid=f['mid'], f_dp=f['dp'])
