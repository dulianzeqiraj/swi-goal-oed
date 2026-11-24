"""HIPOTEZA-GO core: hypotheses about the origin of chloride as terms of the variable-density transport equations.

Physics (vertical section, x = distance from the sea, z = depth, Boussinesq, equivalent freshwater head h):
    flow        div q = sum of water sources and sinks,   q = -K (grad h - eps c_rho e_z),   e_z downward
    salinity    phi d(c_rho)/dt + div(q c_rho) - div(D grad c_rho) = boundary inflows   (c_rho drives density)
    tagged      phi d(c_k)/dt   + div(q c_k)   - div(D grad c_k) + phi lambda_k c_k = s_k      (linear in c_k)
The discretisation is that of chloride_fk/python/fkcl_vd.py (cell-centred finite volumes, harmonic face
conductivity, first-order upwind advection, velocity-dependent diagonal dispersion, hydrostatic sea face with
c = 1 on inflow and zero gradient on outflow), on a rectangular grid, extended with
  - a pumping sink (the well field) and a leakage inflow through the top (the lagoon), which enter the flow equation;
  - tagged components for every candidate source, solved with ONE factorisation of the transport operator;
  - first-order decay (tritium);
  - an implicit transient march with a pumping history Q(t) (pumping is a bilinear input, sources are linear inputs).

Candidate sources (the hypothesis library):
  MS  modern seawater        water entering through the sea face                       (tagged water fraction W_MS)
  LG  lagoon water           leakage through the top near the coast (passive for buoyancy) (water fraction W_LG)
  FW  fresh recharge         inflow at the inland boundary                             (W_FW = 1 - W_MS - W_LG)
  AN  anthropogenic chloride solute flux through the top in the settled zone           (response G_AN per unit flux)
  RS  legacy salinity        distributed solute release in the lower central zone      (response G_RS per unit rate)
  DB  deep saline water      solute flux through the base in an inland zone            (response G_DB per unit flux)
Chloride of sample i:   Cl_i = Cl_sea W_MS,i + Cl_lg W_LG,i + Cl_fw W_FW,i + b_AN G_AN,i + b_RS G_RS,i + b_DB G_DB,i,
linear in the strengths (Cl_sea, Cl_lg, Cl_fw, b_AN, b_RS, b_DB) for given hydraulic parameters theta.
Units: m, d, g/m3 (= mg/L); flows per metre of width."""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

LAMBDA_H3 = np.log(2.0) / (12.32 * 365.25)        # tritium decay constant [1/d]

# ------------------------------------------------------------------------------------------------ geometry
L, B = 12000.0, 100.0                 # length and thickness of the confined aquifer [m]
NX, NZ = 120, 20
EPS, PHI, DM = 0.025, 0.25, 8.64e-5
ZONES = dict(lagoon=(400.0, 2400.0),             # leakage through the top [x range, m]
             an=(3000.0, 7500.0),                # anthropogenic loading through the top
             rs=(5500.0, 9000.0, 50.0, 100.0),   # legacy salinity: x range and depth range
             db=(7000.0, 10000.0),               # deep saline water through the base
             field=(4800.0, 5200.0, 40.0, 70.0)) # the well field: x range and screen depth range
WELL_X = np.array([700.0, 1500.0, 2500.0, 3500.0, 4500.0, 5000.0, 6000.0, 7000.0, 8500.0, 10000.0])
SCREENS = ((10.0, 25.0), (65.0, 85.0))           # upper and lower screens [depth range, m]


class Section:
    def __init__(self, Kx=80.0, aniso=0.05, Qin=5.0, Qw=2.0, vL=0.0, sL=0.6, aL=40.0, aT=1.5, nx=NX, nz=NZ):
        self.nx, self.nz = nx, nz
        self.dx, self.dz = L / nx, B / nz
        self.xc = (np.arange(nx) + 0.5) * self.dx
        self.zc = (np.arange(nz) + 0.5) * self.dz
        self.N = nx * nz
        Kx = np.asarray(Kx, float)
        self.Kx = np.broadcast_to(Kx, (nz, nx)).copy() if Kx.ndim else np.full((nz, nx), float(Kx))
        self.Kz = self.Kx * aniso
        self.Qin, self.Qw, self.vL, self.sL, self.aL, self.aT = Qin, Qw, vL, sL, aL, aT
        idx = np.arange(self.N).reshape(nz, nx)
        self.idx = idx
        hm = lambda a, b: 2 * a * b / (a + b)
        # x-faces between (j,i) and (j,i+1); z-faces between (j,i) and (j+1,i)
        self.xa, self.xb = idx[:, :-1].ravel(), idx[:, 1:].ravel()
        self.zu, self.zd = idx[:-1, :].ravel(), idx[1:, :].ravel()
        self.Kfx = hm(self.Kx[:, :-1], self.Kx[:, 1:]).ravel()
        self.Kfz = hm(self.Kz[:-1, :], self.Kz[1:, :]).ravel()
        self.tx = self.Kfx * self.dz / self.dx
        self.tz = self.Kfz * self.dx / self.dz
        self.sea = idx[:, 0]
        self.hsea = EPS * self.zc
        self.tsea = self.Kx[:, 0] * self.dz / (0.5 * self.dx)
        self.east = idx[:, -1]
        sh = self.Kx[:, -1] / self.Kx[:, -1].sum()
        self.qin_cell = Qin * sh                                   # inflow per east cell [m2/d]
        # masks of the zones
        xm = lambda a, b: (self.xc >= a) & (self.xc <= b)
        zm = lambda a, b: (self.zc >= a) & (self.zc <= b)
        self.lag_cells = idx[0, xm(*ZONES['lagoon'])]
        self.an_cells = idx[0, xm(*ZONES['an'])]
        self.db_cells = idx[-1, xm(*ZONES['db'])]
        r = ZONES['rs']; self.rs_cells = idx[np.ix_(zm(r[2], r[3]), xm(r[0], r[1]))].ravel()
        f = ZONES['field']; self.field_cells = idx[np.ix_(zm(f[2], f[3]), xm(f[0], f[1]))].ravel()
        self.vol = self.dx * self.dz
        self._flow_lu = None

    # ------------------------------------------------------------------ flow (matrix independent of c)
    def _flow_matrix(self):
        N = self.N
        rows = np.r_[self.xa, self.xb, self.xa, self.xb, self.zu, self.zd, self.zu, self.zd, self.sea]
        cols = np.r_[self.xa, self.xb, self.xb, self.xa, self.zu, self.zd, self.zd, self.zu, self.sea]
        vals = np.r_[self.tx, self.tx, -self.tx, -self.tx, self.tz, self.tz, -self.tz, -self.tz, self.tsea]
        self._flow_lu = spla.splu(sp.csc_matrix((vals, (rows, cols)), shape=(N, N)))

    def flow(self, c, Qw=None):
        """Heads and face fluxes for the salinity field c.  Returns h, qx (+x), qz (+down), qsea (+x at the sea face)."""
        if self._flow_lu is None:
            self._flow_matrix()
        Qw = self.Qw if Qw is None else Qw
        rhs = np.zeros(self.N)
        cf = 0.5 * (c[self.zu] + c[self.zd])
        g = self.Kfz * EPS * cf * self.dx                     # buoyant downward flux through z-faces
        np.add.at(rhs, self.zu, -g); np.add.at(rhs, self.zd, g)
        rhs[self.sea] += self.tsea * self.hsea
        rhs[self.east] += self.qin_cell
        rhs[self.field_cells] -= Qw / len(self.field_cells)
        rhs[self.lag_cells] += self.vL * self.dx
        h = self._flow_lu.solve(rhs)
        qx = -self.Kfx * (h[self.xb] - h[self.xa]) / self.dx
        qz = -self.Kfz * (h[self.zd] - h[self.zu]) / self.dz + self.Kfz * EPS * cf
        qsea = -self.Kx[:, 0] * (h[self.sea] - self.hsea) / (0.5 * self.dx)
        return h, qx, qz, qsea

    # ------------------------------------------------------------------ transport operator
    def tmatrix(self, qx, qz, qsea, Qw=None, dt=None, lam=0.0):
        """Transport operator A (csc) and the unit right-hand sides of the boundary inflows:
        A c = rhs_sea * c_sea + rhs_lag * c_lagoon + rhs_east * c_inland + sources (+ storage)."""
        N = self.N
        Qw = self.Qw if Qw is None else Qw
        nzr, nxr = self.nz, self.nx
        # cell-centred velocity components for the dispersion tensor
        QX = np.zeros((nzr, nxr)); cnt = np.zeros((nzr, nxr))
        qxm = qx.reshape(nzr, nxr - 1)
        QX[:, :-1] += qxm; QX[:, 1:] += qxm; cnt[:, :-1] += 1; cnt[:, 1:] += 1
        QX /= cnt
        QZ = np.zeros((nzr, nxr)); cnt = np.zeros((nzr, nxr))
        qzm = qz.reshape(nzr - 1, nxr)
        QZ[:-1, :] += qzm; QZ[1:, :] += qzm; cnt[:-1, :] += 1; cnt[1:, :] += 1
        QZ /= cnt
        qzx = 0.5 * (QZ[:, :-1] + QZ[:, 1:]).ravel(); qxz = 0.5 * (QX[:-1, :] + QX[1:, :]).ravel()
        vx = np.sqrt(qx ** 2 + qzx ** 2) + 1e-30; vz = np.sqrt(qxz ** 2 + qz ** 2) + 1e-30
        Dx = PHI * DM + self.aL * qx ** 2 / vx + self.aT * qzx ** 2 / vx
        Dz = PHI * DM + self.aT * qxz ** 2 / vz + self.aL * qz ** 2 / vz
        Fx, Fz = qx * self.dz, qz * self.dx
        tdx, tdz = Dx * self.dz / self.dx, Dz * self.dx / self.dz
        rows, cols, vals = [], [], []
        for (p, q_, F, td) in ((self.xa, self.xb, Fx, tdx), (self.zu, self.zd, Fz, tdz)):
            pos = F > 0
            Fp, Fn = np.where(pos, F, 0.0), np.where(pos, 0.0, F)
            # flux from p to q_: F c_up ; p loses, q_ gains
            rows += [p, q_, q_, p]; cols += [p, p, q_, q_]; vals += [Fp, -Fp, -Fn, Fn]
            rows += [p, q_, p, q_]; cols += [p, q_, q_, p]; vals += [td, td, -td, -td]
        Fs = qsea * self.dz
        inflow = Fs > 0
        Dsea = PHI * DM + self.aL * np.abs(qsea)
        tds = np.where(inflow, Dsea * self.dz / (0.5 * self.dx), 0.0)
        diag = np.zeros(N)
        diag[self.sea] += np.where(inflow, 0.0, -Fs) + tds          # outflow carries the cell value
        diag[self.field_cells] += Qw / len(self.field_cells)        # pumped water leaves with the cell value
        diag += PHI * lam * self.vol
        rhs_sea = np.zeros(N); rhs_sea[self.sea] = np.where(inflow, Fs, 0.0) + tds
        rhs_lag = np.zeros(N); rhs_lag[self.lag_cells] = self.vL * self.dx
        rhs_east = np.zeros(N); rhs_east[self.east] = self.qin_cell
        if dt is not None:
            diag += PHI * self.vol / dt
        ar = np.arange(N)
        rows.append(ar); cols.append(ar); vals.append(diag)
        A = sp.csc_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(N, N))
        return A, rhs_sea, rhs_lag, rhs_east

    # ------------------------------------------------------------------ steady state of the coupled system
    def picard(self, c):
        """One Picard update of the salinity: flow for c, then steady transport in that flow.  Only seawater drives
        the density; the lagoon leakage is a passive tagged water source (see the note)."""
        h, qx, qz, qs = self.flow(c)
        A, rs, rl, re = self.tmatrix(qx, qz, qs)
        return np.clip(spla.splu(A).solve(rs), 0.0, 1.0)

    def solve_steady(self, c0=None, tol=1e-7, maxit=400, m=8, beta=0.5):
        """Steady coupled state: a short pseudo-transient start with small steps, then Anderson acceleration of the
        Picard map (the plain Picard iteration oscillates at the toe once pumping lowers the seaward flux)."""
        c = np.zeros(self.N) if c0 is None else c0.copy()
        if c0 is None:
            dt = 100.0
            for _ in range(25):
                h, qx, qz, qs = self.flow(c)
                A, rs, rl, re = self.tmatrix(qx, qz, qs, dt=dt)
                c = np.clip(spla.splu(A).solve(rs + PHI * self.vol / dt * c), 0.0, 1.0)
                dt = min(dt * 1.3, 3000.0)
        Fs, Gs, res = [], [], np.inf
        for it in range(maxit):
            g = self.picard(c); f = g - c
            res = float(np.max(np.abs(f)))
            if res < tol:
                break
            Fs.append(f); Gs.append(g)
            if len(Fs) > m + 1:
                Fs.pop(0); Gs.pop(0)
            if len(Fs) == 1:
                c = c + beta * f
            else:
                dF = np.array([Fs[k + 1] - Fs[k] for k in range(len(Fs) - 1)]).T
                dG = np.array([Gs[k + 1] - Gs[k] for k in range(len(Gs) - 1)]).T
                gam, *_ = np.linalg.lstsq(dF, f, rcond=None)
                c = np.clip(beta * (g - dG @ gam) + (1 - beta) * (c - (dG - dF) @ gam), 0.0, 1.0)
        self.c, self.iters, self.dc = c, it, res
        self.h, self.qx, self.qz, self.qsea = self.flow(c)
        return c

    # ------------------------------------------------------------------ tagged components in the present flow field
    def tagged(self, lam=LAMBDA_H3):
        """Water fractions and unit responses of every source in the current flow field (steady transport)."""
        A, rs, rl, re = self.tmatrix(self.qx, self.qz, self.qsea)
        lu = spla.splu(A)
        out = {'W_MS': lu.solve(rs), 'W_LG': lu.solve(rl), 'W_FWchk': lu.solve(re)}
        out['W_FW'] = 1.0 - out['W_MS'] - out['W_LG']
        b = np.zeros(self.N); b[self.an_cells] = self.dx; out['G_AN'] = lu.solve(b)
        b = np.zeros(self.N); b[self.rs_cells] = self.vol; out['G_RS'] = lu.solve(b)
        b = np.zeros(self.N); b[self.db_cells] = self.dx; out['G_DB'] = lu.solve(b)
        Al, rs, rl, re = self.tmatrix(self.qx, self.qz, self.qsea, lam=lam)
        lul = spla.splu(Al)
        out['T_MS'], out['T_LG'], out['T_FW'] = lul.solve(rs), lul.solve(rl), lul.solve(re)
        return out

    # ------------------------------------------------------------------ observation operators
    def screens(self, well_x=WELL_X, screens=SCREENS):
        """List of index arrays, one per sample (well x screen), wells outer, screens inner."""
        cells = []
        for xw in well_x:
            i = int(np.argmin(np.abs(self.xc - xw)))
            for (z0, z1) in screens:
                jj = np.flatnonzero((self.zc >= z0) & (self.zc <= z1))
                cells.append(self.idx[jj, i])
        return cells

    def at(self, field, cells=None):
        cells = self.screens() if cells is None else cells
        return np.array([field[c].mean() for c in cells])

    def toe(self, level=0.5):
        base = self.c.reshape(self.nz, self.nx)[-1]
        k = np.flatnonzero(base >= level)
        return 0.0 if len(k) == 0 else float(self.xc[k.max()] + 0.5 * self.dx)

    # ------------------------------------------------------------------ transient with a pumping history
    def march(self, c0, tagged0, Qw_of_t, t_end, dt=182.625, inner=3, strengths=None, record=None):
        """Implicit Euler from the state (c0, tagged0) with pumping Qw_of_t(t) [m2/d]; the tagged components
        (dict of fields, as returned by tagged(), keys W_MS, W_LG, G_AN, G_RS, G_DB) are stepped with the same operator.
        record: list of times at which the fields are stored.  Returns dict time -> (c, tagged)."""
        c = c0.copy(); tg = {k: v.copy() for k, v in tagged0.items() if k in ('W_MS', 'W_LG', 'G_AN', 'G_RS', 'G_DB')}
        src = {'G_AN': np.zeros(self.N), 'G_RS': np.zeros(self.N), 'G_DB': np.zeros(self.N)}
        src['G_AN'][self.an_cells] = self.dx; src['G_RS'][self.rs_cells] = self.vol; src['G_DB'][self.db_cells] = self.dx
        out, t = {}, 0.0
        record = sorted(record or [t_end])
        while t < t_end - 1e-9:
            step = min(dt, t_end - t)
            for r in record:                           # land exactly on the recording times
                if t < r - 1e-9 < t + step:
                    step = r - t
                    break
            Qw = Qw_of_t(t + step)
            ck = c.copy()
            for _ in range(inner):
                h, qx, qz, qs = self.flow(ck, Qw=Qw)
                A, rs, rl, re = self.tmatrix(qx, qz, qs, Qw=Qw, dt=step)
                lu = spla.splu(A)
                ck = np.clip(lu.solve(rs + PHI * self.vol / step * c), 0.0, 1.0)
            st = PHI * self.vol / step
            tg['W_MS'] = lu.solve(rs + st * tg['W_MS']); tg['W_LG'] = lu.solve(rl + st * tg['W_LG'])
            for k in ('G_AN', 'G_RS', 'G_DB'):
                tg[k] = lu.solve(src[k] + st * tg[k])
            c = ck; t += step
            for r in record:
                if abs(t - r) < 1e-6:
                    out[r] = (c.copy(), {k: v.copy() for k, v in tg.items()})
        return out


# ------------------------------------------------------------------------------------------------ parameters
THETA_KEYS = ('Kx', 'aniso', 'Qin', 'rQ', 'vL', 'sL', 'aL', 'aT')
QW_KNOWN = 1.4          # pumping of the well field [m2/d per metre of width]: metered, hence known


def draw_theta(rng, n=1):
    """Hydraulic parameters of the hypothesis class (ranges stated in the note; log-uniform for K and anisotropy).
    Six uncertain parameters: Kx, anisotropy, inland inflow, lagoon leakage (zero in a quarter of the draws) and the
    two dispersivities.  The pumping is known; sL is not used (the lagoon is passive for buoyancy)."""
    out = []
    for _ in range(n):
        vL = 0.0 if rng.uniform() < 0.25 else rng.uniform(0.5e-4, 4e-4)
        Qin = float(rng.uniform(2.5, 6.0))
        out.append(dict(Kx=float(np.exp(rng.uniform(np.log(50), np.log(200)))),
                        aniso=float(np.exp(rng.uniform(np.log(0.01), np.log(0.1)))),
                        Qin=Qin, rQ=QW_KNOWN / Qin, vL=float(vL), sL=0.0, aL=float(rng.uniform(20.0, 80.0)),
                        aT=float(rng.uniform(0.5, 3.0))))
    return out


def section_of(th, Kfield=None):
    return Section(Kx=th['Kx'] if Kfield is None else Kfield, aniso=th['aniso'], Qin=th['Qin'], Qw=th['rQ'] * th['Qin'],
                   vL=th['vL'], sL=th['sL'], aL=th['aL'], aT=th['aT'])


RESP_KEYS = ('W_MS', 'W_LG', 'W_FW', 'G_AN', 'G_RS', 'G_DB', 'T_MS', 'T_LG', 'T_FW')


def member(th, Kfield=None):
    """One forward solve: steady coupled state, tagged responses at the samples, heads at the wells, toe."""
    s = section_of(th, Kfield)
    for (m, beta, maxit) in ((8, 0.5, 250), (20, 0.2, 300)):                    # one fallback for long wedges
        s.solve_steady(m=m, beta=beta, maxit=maxit)
        if s.dc < 1e-6:
            break
    tg = s.tagged()
    cells = s.screens()
    R = {k: s.at(tg[k], cells) for k in RESP_KEYS}
    R['wsum_err'] = float(np.max(np.abs(tg['W_MS'] + tg['W_LG'] + tg['W_FWchk'] - 1.0)))
    R['head'] = s.at(s.h, cells)[0::2]                      # head at the upper screen of every well
    R['toe50'], R['toe02'] = s.toe(0.5), s.toe(0.02)
    R['iters'], R['dc'] = s.iters, float(s.dc)
    R['ok'] = bool(s.dc < 1e-6)
    R['sal'] = s.at(s.c, cells)
    return R
