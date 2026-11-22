"""HIPOTEZA-GO for the Fushe-Kuqe aquifer: the variable-density section A-A' (y = 36.5 km) with pumping and the
library of candidate chloride sources.

Geometry and conductivity come from a calibrated member of the areal chloride model of the chloride manuscript
(chloride_fk/python/fkcl_model.py): aquifer top from the DRASTIC depths, thickness thinning inland, K along the row.
The grid is rectangular in true depth below sea level; cells above the aquifer top (the silt-clay cover) and below
its base are inert (conductivity 1e-5 of the aquifer's).  The equations and the discretisation are those of
hip_core.Section (inherited), so the same tagged responses are computed.

Hypotheses (terms of the transport equation):
  MS  modern seawater          water entering through the western face (the GLOBE shoreline of the row)
  LG  Patok lagoon water       leakage through the cover in the first 1.5 km, ONLY where the aquifer head is below
                               the lagoon level (otherwise the gradient is upward and the term is zero)
  FW  fresh recharge           inflow at the inland boundary (Mat river and rain)
  AN  anthropogenic chloride   solute input through the cover in the plain, ONLY where the aquifer is not artesian
  RS  legacy salinity          release in the aquifer between 1 and 7 km (marine clays of the Holocene transgression)
  DB  deep saline water        solute flux through the base between 2 and 7 km
Units: m, d, g/m3 (= mg/L); flows per metre of width; heads in m above sea level."""
import os
import sys

import numpy as np

import hip_core as H

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'chloride_fk', 'python'))

Y_SEC = 36.5                      # km, row of the section (as in chloride_fk/python/fkcl_section.py)
DXS, DZS, ZMAX = 100.0, 7.5, 240.0
H_LAG = 0.3                       # m a.s.l., level of the Patok lagoon
WT_DEPTH = 0.5                    # m, water table below ground in the plain
ZONES_FK = dict(lagoon=(0.0, 1500.0), an=(2000.0, 8425.0), rs=(1000.0, 7000.0), db=(2000.0, 7000.0))
SCREEN = 40.0                     # m, screen length (as in the chloride manuscript)
BANDS = dict(sw=(0.5, 2.5), c=(3.0, 6.0), ne=(7.0, 99.0))        # distance from the shoreline, km
KEYS = ('W_MS', 'W_LG', 'W_FW', 'G_AN', 'G_RS', 'G_DB')


# ------------------------------------------------------------------------------------------------ areal geometry
_M = None


def areal():
    global _M
    if _M is None:
        import fkcl_model as M
        _M = M.Model()
    return _M


def geometry(p):
    """Section geometry from an areal member p (dict of the calibration parameters)."""
    m = areal()
    j = int(round(Y_SEC / m.dx))
    K = m.K_field(p['theta'], p['eta'])
    shore = m.shore_row[j]
    cells = np.flatnonzero(m.valid & (m.aj == j))
    cells = cells[np.argsort(m.cx[cells])]
    xe_km = m.cx[cells[-1]] + 0.5 * m.dx
    L = (xe_km - shore) * 1000.0
    nx = int(round(L / DXS))
    xe = np.linspace(0.0, L, nx + 1)
    xc = 0.5 * (xe[1:] + xe[:-1])
    xc_km = shore + xc / 1000.0
    near = cells[np.clip(np.searchsorted(m.cx[cells] - 0.5 * m.dx, xc_km) - 1, 0, len(cells) - 1)]
    d, B = m.geometry(p)
    dist = np.interp(xc_km, m.cx[cells], m.dist[cells])
    return dict(L=L, xc=xc, top=d[near], bot=d[near] + B[near], K=K[near], dist=dist, ground=float(p['ground']))


# ------------------------------------------------------------------------------------------------ the section
class FKSection(H.Section):
    def __init__(self, geo, Kmul=1.0, aniso=0.03, Qin=10.0, Qw=0.0, x_wf=4500.0, vL=0.0, aL=40.0, aT=1.0,
                 an_cols=None):
        L = geo['L']
        nx = len(geo['xc']); nz = int(round(ZMAX / DZS))
        self.nx, self.nz = nx, nz
        self.dx, self.dz = L / nx, ZMAX / nz
        self.xc = geo['xc'].copy()
        self.zc = (np.arange(nz) + 0.5) * self.dz
        self.N = nx * nz
        self.geo = geo
        top, bot = geo['top'], geo['bot']
        act = (self.zc[:, None] >= top[None, :]) & (self.zc[:, None] <= bot[None, :])
        self.act = act
        Ka = np.broadcast_to(geo['K'] * Kmul, (nz, nx))
        self.Kx = np.where(act, Ka, 1e-5 * Ka).copy()
        self.Kz = self.Kx * aniso
        self.Qin, self.Qw, self.vL, self.sL, self.aL, self.aT = Qin, Qw, vL, 0.0, aL, aT
        idx = np.arange(self.N).reshape(nz, nx)
        self.idx = idx
        hm = lambda a, b: 2 * a * b / (a + b)
        self.xa, self.xb = idx[:, :-1].ravel(), idx[:, 1:].ravel()
        self.zu, self.zd = idx[:-1, :].ravel(), idx[1:, :].ravel()
        self.Kfx = hm(self.Kx[:, :-1], self.Kx[:, 1:]).ravel()
        self.Kfz = hm(self.Kz[:-1, :], self.Kz[1:, :]).ravel()
        self.tx = self.Kfx * self.dz / self.dx
        self.tz = self.Kfz * self.dx / self.dz
        self.sea = idx[:, 0]
        self.hsea = H.EPS * self.zc
        self.tsea = self.Kx[:, 0] * self.dz / (0.5 * self.dx)
        self.east = idx[:, -1]
        sh = self.Kx[:, -1] / self.Kx[:, -1].sum()
        self.qin_cell = Qin * sh
        # first and last active row of every column
        self.jtop = act.argmax(0)
        self.jbot = nz - 1 - act[::-1].argmax(0)
        xm = lambda a, b: np.flatnonzero((self.xc >= a) & (self.xc <= b))
        cols = xm(*ZONES_FK['lagoon']); self.lag_cells = idx[self.jtop[cols], cols]
        cols = xm(*ZONES_FK['an']) if an_cols is None else np.asarray(an_cols, int)
        self.an_cells = idx[self.jtop[cols], cols] if len(cols) else np.zeros(0, int)
        cols = xm(*ZONES_FK['db']); self.db_cells = idx[self.jbot[cols], cols]
        r = ZONES_FK['rs']
        self.rs_cells = idx[act & ((self.xc >= r[0]) & (self.xc <= r[1]))[None, :]]
        # the well field: columns within 200 m of x_wf, upper 60 % of the aquifer
        cols = xm(x_wf - 200.0, x_wf + 200.0)
        fc = [idx[j, i] for i in cols for j in range(nz) if act[j, i] and self.zc[j] <= top[i] + 0.6 * (bot[i] - top[i])]
        self.field_cells = np.array(fc, int)
        self.wf_cols = cols
        self.vol = self.dx * self.dz
        self._flow_lu = None

    def toe(self, level=0.5):
        base = self.c.reshape(self.nz, self.nx)[self.jbot, np.arange(self.nx)]
        k = np.flatnonzero(base >= level)
        return 0.0 if len(k) == 0 else float(self.xc[k.max()] + 0.5 * self.dx)

    def head_top(self, h=None):
        h = self.h if h is None else h
        return h.reshape(self.nz, self.nx)[self.jtop, np.arange(self.nx)]

    def screen_cells(self, kind):
        """For every column, the active cells of a 40 m screen: 'sh' top of the aquifer, 'mid' centred at
        mid-thickness, 'dp' base."""
        top, bot = self.geo['top'], self.geo['bot']
        out = []
        for i in range(self.nx):
            if kind == 'sh':
                z0, z1 = top[i], top[i] + SCREEN
            elif kind == 'mid':
                zm = 0.5 * (top[i] + bot[i]); z0, z1 = zm - 0.5 * SCREEN, zm + 0.5 * SCREEN
            else:
                z0, z1 = bot[i] - SCREEN, bot[i]
            jj = np.flatnonzero(self.act[:, i] & (self.zc >= z0) & (self.zc <= z1))
            out.append(self.idx[jj, i])
        return out


# ------------------------------------------------------------------------------------------------ the class
THETA_FK = ('member', 'Kmul', 'aniso', 'Qin', 'rQ', 'x_wf', 'aL', 'aT', 'Kv_cov')


def draw_theta(rng, n, calib):
    """n parameter vectors: an areal member resampled by its calibration weight (geometry and K), and the section
    parameters (K multiplier, anisotropy, inland inflow, pumping as a fraction of it, well-field position,
    dispersivities, vertical conductivity of the cover for the lagoon leakage)."""
    w = calib['weight']
    mem = rng.choice(len(w), size=n, p=w / w.sum())
    out = []
    for k in range(n):
        out.append(dict(member=int(mem[k]), Kmul=float(np.exp(rng.uniform(np.log(0.5), np.log(2.0)))),
                        aniso=float(np.exp(rng.uniform(np.log(0.003), np.log(0.1)))),
                        Qin=float(np.exp(rng.uniform(np.log(3.0), np.log(80.0)))), rQ=float(rng.uniform(0.0, 0.95)),
                        x_wf=float(rng.uniform(3500.0, 6000.0)), aL=float(rng.uniform(10.0, 80.0)),
                        aT=float(np.exp(rng.uniform(np.log(0.1), np.log(3.0)))),
                        Kv_cov=float(np.exp(rng.uniform(np.log(1e-4), np.log(1e-2))))))
    return out


def areal_params(calib, i):
    keys = ['theta', 'R', 'eta', 'b_c', 'b_e', 'L_B', 'ground', 'w', 'Cl_s']
    return {k: calib[k][i] for k in keys}


def solve(s):
    for (m_, beta, maxit) in ((8, 0.5, 250), (20, 0.2, 350)):
        s.solve_steady(m=m_, beta=beta, maxit=maxit)
        if s.dc < 1e-6:
            break
    return s


def member(th, calib):
    """One forward solve of the Fushe-Kuqe class.  Returns heads, the physics gates of LG and AN, and the tagged
    responses at every column for the three screens."""
    p = areal_params(calib, th['member'])
    geo = geometry(p)
    ground = geo['ground']
    Qw = th['rQ'] * th['Qin']
    kw = dict(Kmul=th['Kmul'], aniso=th['aniso'], Qin=th['Qin'], Qw=Qw, x_wf=th['x_wf'], aL=th['aL'], aT=th['aT'])
    s = solve(FKSection(geo, vL=0.0, **kw))
    ht = s.head_top()
    # physics gates: lagoon leakage only below the lagoon level, anthropogenic input only where not artesian
    lag_cols = np.flatnonzero((s.xc >= ZONES_FK['lagoon'][0]) & (s.xc <= ZONES_FK['lagoon'][1]))
    cover = s.geo['top'][lag_cols] + ground                       # cover thickness below ground [m]
    dh = H_LAG - ht[lag_cols]
    vL = float(np.mean(np.clip(dh, 0.0, None) * th['Kv_cov'] / cover))
    an_zone = np.flatnonzero((s.xc >= ZONES_FK['an'][0]) & (s.xc <= ZONES_FK['an'][1]))
    an_cols = an_zone[ht[an_zone] < ground - WT_DEPTH]
    if vL > 0.0:                                  # the leakage changes the flow: solve again
        s = solve(FKSection(geo, vL=vL, an_cols=an_cols, **kw))
        ht = s.head_top()
    else:                                         # the anthropogenic input is a solute source only
        s.an_cells = s.idx[s.jtop[an_cols], an_cols] if len(an_cols) else np.zeros(0, int)
    tg = s.tagged()
    if len(an_cols) == 0:
        tg['G_AN'] = np.zeros(s.N)
    R = dict(ok=bool(s.dc < 1e-6), dc=float(s.dc), iters=int(s.iters), vL=vL, n_an=int(len(an_cols)),
             n_an_zone=int(len(an_zone)), ground=ground, xc=s.xc, dist=s.geo['dist'], top=s.geo['top'],
             bot=s.geo['bot'], head_top=ht, Qw=Qw)
    # heads of the facts
    sw = (s.geo['dist'] >= BANDS['sw'][0]) & (s.geo['dist'] <= BANDS['sw'][1])
    R['h_lit'] = float(np.median(ht[sw]))
    R['h_wf'] = float(np.mean(ht[s.wf_cols]))
    h0, *_ = s.flow(s.c, Qw=0.0)                                  # natural head, pumped salinity (approximation)
    R['h_wf0'] = float(np.mean(s.head_top(h0)[s.wf_cols]))
    R['toe50'], R['toe02'] = s.toe(0.5), s.toe(0.02)
    # responses at every column for the three screens (columns x screens x sources)
    resp = np.zeros((s.nx, 3, len(KEYS)), np.float32)
    sal = np.zeros((s.nx, 3), np.float32)
    for q, kind in enumerate(('sh', 'mid', 'dp')):
        cells = s.screen_cells(kind)
        for k, key in enumerate(KEYS):
            f = tg[key]
            resp[:, q, k] = [f[c].mean() if len(c) else np.nan for c in cells]
        sal[:, q] = [s.c[c].mean() if len(c) else np.nan for c in cells]
    R['resp'] = resp; R['sal'] = sal
    R['wsum_err'] = float(np.max(np.abs((tg['W_MS'] + tg['W_LG'] + tg['W_FWchk'] - 1.0)[s.act.ravel()])))
    R['sec'] = s
    return R
