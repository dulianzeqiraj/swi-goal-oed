"""MONTIMI-GO: the assembled system of a coastal aquifer, solved on a vertical section, with its discrete adjoint.

The assembled forward system (implicit Euler in time, finite volumes in space, unit width along the coast):

  flow        S_s dh/dt + div q = W - sum_k s_k a_k (h - h_k),            dh_k/dt = a_k (h - h_k)     (hydraulic memory)
  Darcy       q = -K (grad h + delta c e_z)                                                           (buoyancy)
  salt        n dc/dt + div(q c) - c div q - div(n D grad c) + sum_k n b_k a_k (c - c_k) = W_in (c_inj - c),
              dc_k/dt = a_k (c - c_k)                                                                 (immobile zones)
  dispersion  n D on a face = n D_m + (alpha_L q_n^2 + alpha_T q_t^2)/|q|, coefficient from the previous step
  ions        Cl, Na, K, Ca, Mg, SO4, HCO3 transported with the same operator, Gaines-Thomas exchange in every
              cell (sequential, after the salt step; GJURMA-GO routines): one-way coupled, never feeds back
  sea face    h = (1 + delta) eta(t) - delta z, inflow carries sea water (c = 1), no dispersive flux
  inland face prescribed fresh inflow q_in (c = 0);  top and base closed
  wells       supply well: sink over the top 20 m;  recharge well: fresh injection over the full thickness

Coupling: the flow and salt blocks are solved together at every step (Picard iteration to convergence; the fixed
point solves the coupled implicit system) or split (one pass, buoyancy lagged one step). Every term can be switched
off, which is how the goal-weighted budget of the note is checked against actual runs.

The adjoint is the exact discrete adjoint of the converged scheme (block Jacobians assembled analytically, including
the dependence of the dispersion coefficients on the previous step's fluxes, the local memory states and the steady
initial state), so that
  dJ/dp = - sum_n lambda_n' dR_n/dp,      J(y~) - J(y) ~ - sum_n lambda_n' (R~_n(y) - R_n(y))    (term budget)
  J_h(I y_H) - J_h(y_h) ~ sum_n lambda_n' R_n(I y_H)                                              (dual-weighted residual)
"""
import time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

YR = 365.25
CL_F, CL_S = 12.92, 21781.0              # chloride of fresh water (well 193) and Adriatic sea water, mg/L
CL_LIM, NA_LIM = 250.0, 200.0            # drinking-water standards, mg/L
EPS_LIM = (CL_LIM - CL_F) / (CL_S - CL_F)    # sea fraction at which chloride reaches 250 mg/L (0.01089)

BASE = dict(
    L=4000.0, z_top=-10.0, z_bot=-70.0,  # section: 4 km from the coast, aquifer 60 m thick, top 10 m below sea level
    K=100.0, anis=0.1, n=0.25, Ss=5e-6,  # m/d, Kz/Kx, porosity, specific storage (1/m): storativity 3e-4
    delta=0.025,                          # density contrast
    aL=20.0, aT=2.0, Dm=8.64e-5,          # dispersivities (m), molecular diffusion (m2/d)
    q_in=4.0,                             # regional fresh inflow at the inland face (m2/d per metre of coast)
    a_h=(1.0, 0.05), s_h=(2e-5, 5e-5),    # hydraulic memory: rates (1/yr) and capacities (1/m) of silt and clay
    a_c=(1.0, 0.05), b_c=(0.3, 0.6),      # immobile zones for solutes: rates (1/yr) and capacity ratios
    eta_rate=4.0,                         # sea-level rise (mm/yr)
    scr_top=-10.0, scr_bot=-30.0,         # supply screen: top 20 m of the aquifer
    E=60.0,                               # exchange capacity (meq per litre of pore water)
)
DEFAULT_OPTS = dict(memory_h=(True, True), immobile=(True, True), buoyancy=True, coupling='full', slr=True,
                    transverse=True, picard_max=12)


# ============================================================================== grid
class Grid:
    """Tensor grid, columns j (x, 0 at the sea) and rows i (z, 0 at the base); cell p = i*NX + j."""

    def __init__(self, xf, zf):
        self.xf, self.zf = np.asarray(xf, float), np.asarray(zf, float)
        self.dx, self.dz = np.diff(self.xf), np.diff(self.zf)
        self.xc, self.zc = 0.5 * (self.xf[1:] + self.xf[:-1]), 0.5 * (self.zf[1:] + self.zf[:-1])
        NX, NZ = len(self.dx), len(self.dz)
        self.NX, self.NZ, self.N = NX, NZ, NX * NZ
        I, J = np.meshgrid(np.arange(NZ), np.arange(NX), indexing='ij')
        self.I, self.J = I.ravel(), J.ravel()
        self.V = (self.dx[None, :] * self.dz[:, None]).ravel()
        cid = lambda i, j: i * NX + j
        fm, fp, A, d, kind = [], [], [], [], []           # kind 0 x-internal, 1 z-internal, 2 sea, 3 inland
        for i in range(NZ):
            fm.append(-1); fp.append(cid(i, 0)); A.append(self.dz[i]); d.append(self.dx[0] / 2); kind.append(2)
        for i in range(NZ):
            for j in range(NX - 1):
                fm.append(cid(i, j)); fp.append(cid(i, j + 1)); A.append(self.dz[i]); d.append(0.5 * (self.dx[j] + self.dx[j + 1])); kind.append(0)
        for i in range(NZ - 1):
            for j in range(NX):
                fm.append(cid(i, j)); fp.append(cid(i + 1, j)); A.append(self.dx[j]); d.append(0.5 * (self.dz[i] + self.dz[i + 1])); kind.append(1)
        for i in range(NZ):
            fm.append(cid(i, NX - 1)); fp.append(-1); A.append(self.dz[i]); d.append(self.dx[-1] / 2); kind.append(3)
        self.fm, self.fp = np.array(fm), np.array(fp)
        self.A, self.d, self.kind = np.array(A), np.array(d), np.array(kind)
        self.F = len(fm)
        self.internal = (self.kind < 2).astype(float)
        rows, cols, vals = [], [], []
        for f in range(self.F):
            if fm[f] >= 0: rows.append(fm[f]); cols.append(f); vals.append(1.0)
            if fp[f] >= 0: rows.append(fp[f]); cols.append(f); vals.append(-1.0)
        self.Div = sp.csr_matrix((vals, (rows, cols)), shape=(self.N, self.F))
        it = np.flatnonzero(self.kind < 2)
        self.Grad = sp.csr_matrix((np.r_[np.ones(len(it)), -np.ones(len(it))], (np.r_[it, it], np.r_[self.fp[it], self.fm[it]])), shape=(self.F, self.N))
        cfx, cfz = {}, {}
        for f in range(self.F):
            if kind[f] in (0, 2, 3):
                if fp[f] >= 0: cfx.setdefault(fp[f], [None, None])[0] = f
                if fm[f] >= 0: cfx.setdefault(fm[f], [None, None])[1] = f
            else:
                cfz.setdefault(fp[f], [None, None])[0] = f
                cfz.setdefault(fm[f], [None, None])[1] = f
        rows, cols, vals = [], [], []
        for f in it:
            src = cfz if kind[f] == 0 else cfx
            for c in (fm[f], fp[f]):
                for gface in src.get(c, [None, None]):
                    if gface is not None:
                        rows.append(f); cols.append(gface); vals.append(0.25 / A[gface])
        self.Tg = sp.csr_matrix((vals, (rows, cols)), shape=(self.F, self.F))

    def column(self, x):
        return int(np.clip(np.searchsorted(self.xf, x, side='right') - 1, 0, self.NX - 1))

    def interp_weights(self, x, rows):
        """weights of the mean over `rows` of the value linearly interpolated (in x) at x."""
        xc = self.xc
        if x <= xc[0]: js, ws = [0], [1.0]
        elif x >= xc[-1]: js, ws = [self.NX - 1], [1.0]
        else:
            j = int(np.searchsorted(xc, x) - 1); t = (x - xc[j]) / (xc[j + 1] - xc[j])
            js, ws = [j, j + 1], [1 - t, t]
        w = np.zeros(self.N)
        for i in rows:
            for j, a in zip(js, ws):
                w[i * self.NX + j] += a / len(rows)
        return w


def uniform_grid(nx=160, nz=24, P=BASE):
    return Grid(np.linspace(0, P['L'], nx + 1), np.linspace(P['z_bot'], P['z_top'], nz + 1))


def prolong(gH, gh):
    """Linear interpolation in x (row by row) from grid gH to grid gh (same rows): sparse N_h x N_H."""
    assert gH.NZ == gh.NZ
    rows, cols, vals = [], [], []
    for jh, x in enumerate(gh.xc):
        if x <= gH.xc[0]: js, ws = [0], [1.0]
        elif x >= gH.xc[-1]: js, ws = [gH.NX - 1], [1.0]
        else:
            j = int(np.searchsorted(gH.xc, x) - 1); t = (x - gH.xc[j]) / (gH.xc[j + 1] - gH.xc[j]); js, ws = [j, j + 1], [1 - t, t]
        for i in range(gh.NZ):
            for j, a in zip(js, ws):
                rows.append(i * gh.NX + jh); cols.append(i * gH.NX + j); vals.append(a)
    return sp.csr_matrix((vals, (rows, cols)), shape=(gh.N, gH.N))


def restrict(gh, gH):
    """volume average from the fine grid gh to a nested coarse grid gH (same rows)."""
    rows, cols, vals = [], [], []
    for jh, x in enumerate(gh.xc):
        jH = gH.column(x)
        for i in range(gh.NZ):
            rows.append(i * gH.NX + jH); cols.append(i * gh.NX + jh); vals.append(gh.dx[jh] / gH.dx[jH])
    return sp.csr_matrix((vals, (rows, cols)), shape=(gH.N, gh.N))


def graded_grid(eta_col, gh, ncol, floor=0.02, maxw=400.0):
    """Nested coarse grid in x: merge fine columns so that (indicator per metre)^(1/3) is equidistributed."""
    w = gh.dx
    dens = eta_col / w
    m = np.maximum(dens, floor * dens.max()) ** (1.0 / 3.0)
    M = np.r_[0, np.cumsum(m * w)]
    targets = np.linspace(0, M[-1], ncol + 1)
    idx = np.unique(np.r_[0, np.searchsorted(M, targets[1:-1]), gh.NX])
    xf = list(gh.xf[idx])
    out = [xf[0]]
    for a, b in zip(xf[:-1], xf[1:]):
        k = int(np.ceil((b - a) / maxw - 1e-9))
        for s in range(1, k + 1):
            out.append(gh.xf[np.argmin(np.abs(gh.xf - (a + (b - a) * s / k)))])
    return Grid(np.unique(out), gh.zf)


# ============================================================================== model
class Model:
    """One assembly of the system on one grid, for one parameter set. Wells follow a schedule of segments
    [(steps, layout), ...]: here a historical well field, then the layout under decision (recharge and supply)."""

    def __init__(self, g, P=None, opts=None, layout=None, dt_yr=0.5, H_yr=30.0):
        self.g, self.P = g, dict(BASE, **(P or {}))
        self.o = dict(DEFAULT_OPTS, **(opts or {}))
        self.dt = dt_yr * YR
        self.nsteps = int(round(H_yr / dt_yr))
        P = self.P
        Kx, Kz = P['K'], P['K'] * P['anis']
        self.Kf = np.where(g.kind == 1, Kz, Kx)
        T = self.Kf * g.A / g.d
        rows, cols, vals = [], [], []
        for f in range(g.F):
            if g.fm[f] >= 0 and g.fp[f] >= 0:
                rows += [f, f]; cols += [g.fp[f], g.fm[f]]; vals += [-T[f], T[f]]
            elif g.kind[f] == 2:
                rows.append(f); cols.append(g.fp[f]); vals.append(-T[f])
        self.Gh = sp.csr_matrix((vals, (rows, cols)), shape=(g.F, g.N))
        zf = np.flatnonzero(g.kind == 1)
        bc = -Kz * g.A[zf] * P['delta'] * 0.5
        self.Gc_full = sp.csr_matrix((np.r_[bc, bc], (np.r_[zf, zf], np.r_[g.fm[zf], g.fp[zf]])), shape=(g.F, g.N))
        self.Gc = self.Gc_full if self.o['buoyancy'] else sp.csr_matrix((g.F, g.N))
        self.sea = np.flatnonzero(g.kind == 2)
        self.inl = np.flatnonzero(g.kind == 3)
        self.T_sea = T[self.sea]
        self.z_sea = g.zc[g.I[g.fp[self.sea]]]
        self.Q_in = -P['q_in'] * g.A[self.inl] / (P['z_top'] - P['z_bot'])
        self.DivGh = (g.Div @ self.Gh).tocsr()
        self.DivGc = (g.Div @ self.Gc).tocsr()
        self.st_h = P['Ss'] * g.V / self.dt
        self.ah = np.array(P['a_h']) / YR; self.sh = np.array(P['s_h'])
        self.ac = np.array(P['a_c']) / YR; self.bc = np.array(P['b_c'])
        self.alpha_h = 1.0 / (1.0 + self.ah * self.dt); self.beta_h = 1.0 - self.alpha_h
        self.alpha_c = 1.0 / (1.0 + self.ac * self.dt); self.beta_c = 1.0 - self.alpha_c
        self.mh_on = np.array(self.o['memory_h'], float)
        self.mc_on = np.array(self.o['immobile'], float)
        self.mh_coef = [self.mh_on[k] * self.sh[k] * self.ah[k] * self.alpha_h[k] * g.V for k in range(2)]
        self.mc_coef = [self.mc_on[k] * P['n'] * self.bc[k] * self.ac[k] * self.alpha_c[k] * g.V for k in range(2)]
        self.st_c = P['n'] * g.V / self.dt
        self.Ah = (sp.diags(self.st_h + self.mh_coef[0] + self.mh_coef[1]) + self.DivGh).tocsc()
        self.Ah_lu = None
        self.scr_rows = [i for i in range(g.NZ) if P['scr_bot'] < g.zc[i] < P['scr_top']]
        self.set_layout(layout or {})

    # ------------------------------------------------------------------ wells and goal
    def wells_of(self, layout):
        """(W_out, W_in, e_Q, e_qr, wJ) of a layout: supply well over the screen, recharge well over the thickness."""
        g = self.g
        e_Q = np.zeros(g.N); e_qr = np.zeros(g.N); wJ = None
        if layout.get('xs') is not None:
            j = g.column(layout['xs'])
            tot = sum(g.dz[i] for i in self.scr_rows)
            for i in self.scr_rows:
                e_Q[i * g.NX + j] = g.dz[i] / tot
            wJ = g.interp_weights(layout['xs'], self.scr_rows)
        if layout.get('xr') is not None:
            j = g.column(layout['xr'])
            for i in range(g.NZ):
                e_qr[i * g.NX + j] = g.dz[i] / g.dz.sum()
        return layout.get('Q', 0.0) * e_Q, layout.get('qr', 0.0) * e_qr, e_Q, e_qr, wJ

    def set_layout(self, layout):
        self.layout = dict(layout)
        self.W_out, self.W_in, self.e_Q, self.e_qr, self.wJ = self.wells_of(self.layout)

    def set_Q(self, Q):
        self.layout['Q'] = Q
        self.W_out = Q * self.e_Q

    def wells(self, n=None, steady=False):
        if steady:
            return np.zeros(self.g.N), np.zeros(self.g.N)
        if n is None or not hasattr(self, 'Wn'):
            return self.W_out, self.W_in
        return self.Wn[n]

    # ------------------------------------------------------------------ pieces
    def eta(self, t, slr=None):
        slr = self.o['slr'] if slr is None else slr
        return (self.P['eta_rate'] * 1e-3 / YR * t) if slr else 0.0

    def g0(self, t, slr=None, scale=1.0):
        g0 = np.zeros(self.g.F)
        g0[self.sea] = self.T_sea * ((1 + self.P['delta']) * scale * self.eta(t, slr) - self.P['delta'] * self.z_sea)
        g0[self.inl] = self.Q_in
        return g0

    def upwind(self, Q):
        g = self.g
        up = np.where(Q >= 0, g.fm, g.fp)
        ghost = np.zeros(g.F)
        ghost[(g.kind == 2) & (Q >= 0)] = 1.0
        ok = up >= 0
        U = sp.csr_matrix((np.ones(ok.sum()), (np.flatnonzero(ok), up[ok])), shape=(g.F, g.N))
        return U, ghost

    def disp(self, Q, transverse=None, aT_scale=None):
        """n D A / d on internal faces from the face fluxes Q (m2/d), and its derivative w.r.t. Q."""
        g, P = self.g, self.P
        transverse = self.o['transverse'] if transverse is None else transverse
        aT = P['aT'] * (aT_scale if aT_scale is not None else (1.0 if transverse else 0.0))
        qn = Q / g.A
        qt = g.Tg @ Q
        s = np.sqrt(qn ** 2 + qt ** 2 + 1e-24)
        Nn = P['aL'] * qn ** 2 + aT * qt ** 2
        Dt = (P['n'] * P['Dm'] + Nn / s) * g.internal
        dqn = (2 * P['aL'] * qn / s - Nn * qn / s ** 3) * g.internal
        dqt = (2 * aT * qt / s - Nn * qt / s ** 3) * g.internal
        dD = sp.diags(dqn / g.A) + sp.diags(dqt) @ g.Tg
        return Dt * g.A / g.d, sp.diags(g.A / g.d) @ dD

    def transport_matrix(self, Q, Dcoef, W_in):
        g = self.g
        U, ghost = self.upwind(Q)
        DivQ = g.Div @ Q
        Ac = sp.diags(self.st_c + self.mc_coef[0] + self.mc_coef[1] - DivQ + W_in) + g.Div @ (sp.diags(Q) @ U - sp.diags(Dcoef) @ g.Grad)
        return Ac, ghost

    # ------------------------------------------------------------------ residual R_n(y_n, y_{n-1}, z_{n-1})
    def residual(self, y, yo, zo, t, n=None, steady=False, opts=None, hom=None):
        """Residual of step n. `opts` switches terms (alternative assemblies); `hom` scales them continuously,
        hom = {'memory_h': (s1, s2), 'immobile': (s1, s2), 'buoyancy': s, 'slr': s, 'transverse': s, 'split': s},
        each s = 1 for the model's own assembly and 0 for the term removed (split: 0 none, 1 fully lagged)."""
        o = dict(self.o, **(opts or {}))
        hm = hom or {}
        g, P, N = self.g, self.P, self.g.N
        h, c = y[:N], y[N:]
        sb = hm.get('buoyancy', 1.0) * (1.0 if o['buoyancy'] else 0.0)
        Gc = self.Gc_full * sb
        ssl = hm.get('slr', 1.0)
        W_out, W_in = self.wells(n, steady)
        aT_scale = hm.get('transverse', 1.0) * (1.0 if o['transverse'] else 0.0)
        if steady:
            Q = self.Gh @ h + Gc @ c + self.g0(0.0, o['slr'], ssl)
            Dcoef, _ = self.disp(Q, aT_scale=aT_scale)
        else:
            lag = hm.get('split', 1.0 if o['coupling'] == 'split' else 0.0)
            c_b = (1 - lag) * c + lag * yo[N:]
            Q = self.Gh @ h + Gc @ c_b + self.g0(t, o['slr'], ssl)
            Qo = self.Gh @ yo[:N] + Gc @ yo[N:] + self.g0(t - self.dt, o['slr'], ssl)
            Dcoef, _ = self.disp(Qo, aT_scale=aT_scale)
        U, ghost = self.upwind(Q)
        F = Q * (U @ c + ghost) - Dcoef * (g.Grad @ c)
        DivQ = g.Div @ Q
        Rh = DivQ + W_out - W_in
        Rc = g.Div @ F - c * DivQ + W_in * c
        if not steady:
            Rh = Rh + self.st_h * (h - yo[:N])
            Rc = Rc + self.st_c * (c - yo[N:])
            mh = np.array(o['memory_h'], float) * np.array(hm.get('memory_h', (1.0, 1.0)))
            mc = np.array(o['immobile'], float) * np.array(hm.get('immobile', (1.0, 1.0)))
            for k in range(2):
                Rh = Rh + mh[k] * self.sh[k] * self.ah[k] * self.alpha_h[k] * g.V * (h - zo[k * N:(k + 1) * N])
                Rc = Rc + mc[k] * P['n'] * self.bc[k] * self.ac[k] * self.alpha_c[k] * g.V * (c - zo[(2 + k) * N:(3 + k) * N])
        return np.r_[Rh, Rc]

    # ------------------------------------------------------------------ Jacobians
    def jac(self, y, yo, t, n=None, steady=False):
        """dR_n/dy_n (exact; upwind directions frozen)."""
        g, N = self.g, self.g.N
        h, c = y[:N], y[N:]
        split = (self.o['coupling'] == 'split') and not steady
        W_out, W_in = self.wells(n, steady)
        Q = self.Gh @ h + self.Gc @ (yo[N:] if split else c) + self.g0(t)
        if steady:
            Dcoef, dD = self.disp(Q)
        else:
            Dcoef, _ = self.disp(self.Gh @ yo[:N] + self.Gc @ yo[N:] + self.g0(t - self.dt))
        U, ghost = self.upwind(Q)
        cup = U @ c + ghost
        DivQ = g.Div @ Q
        Gc_now = sp.csr_matrix((g.F, N)) if split else self.Gc
        DivGc_now = sp.csr_matrix((N, N)) if split else self.DivGc
        Jhh = self.DivGh
        Jhc = DivGc_now
        Jch = g.Div @ sp.diags(cup) @ self.Gh - sp.diags(c) @ self.DivGh
        Jcc = g.Div @ (sp.diags(Q) @ U + sp.diags(cup) @ Gc_now - sp.diags(Dcoef) @ g.Grad) - sp.diags(DivQ) - sp.diags(c) @ DivGc_now + sp.diags(W_in)
        if steady:
            M = g.Div @ sp.diags(-(g.Grad @ c)) @ dD
            Jch = Jch + M @ self.Gh
            Jcc = Jcc + M @ self.Gc
        else:
            Jhh = Jhh + sp.diags(self.st_h + self.mh_coef[0] + self.mh_coef[1])
            Jcc = Jcc + sp.diags(self.st_c + self.mc_coef[0] + self.mc_coef[1])
        return sp.bmat([[Jhh, Jhc], [Jch, Jcc]], format='csr')

    def jac_old(self, y, yo, t):
        """dR_n/dy_{n-1}: storage, dispersion coefficients from the old fluxes, lagged buoyancy if split."""
        g, N = self.g, self.g.N
        c = y[N:]
        Qo = self.Gh @ yo[:N] + self.Gc @ yo[N:] + self.g0(t - self.dt)
        _, dD = self.disp(Qo)
        M = g.Div @ sp.diags(-(g.Grad @ c)) @ dD
        Jch = M @ self.Gh
        Jcc = M @ self.Gc - sp.diags(self.st_c)
        Jhh = -sp.diags(self.st_h)
        Jhc = sp.csr_matrix((N, N))
        if self.o['coupling'] == 'split':
            Q = self.Gh @ y[:N] + self.Gc @ yo[N:] + self.g0(t)
            U, ghost = self.upwind(Q)
            cup = U @ c + ghost
            Jhc = self.DivGc
            Jcc = Jcc + g.Div @ sp.diags(cup) @ self.Gc - sp.diags(c) @ self.DivGc
        return sp.bmat([[Jhh, Jhc], [Jch, Jcc]], format='csr')

    # ------------------------------------------------------------------ pre-development equilibrium (no wells)
    def steady(self, y0=None, tol=1e-11, verbose=False):
        g, N, P = self.g, self.g.N, self.P
        if y0 is None:
            toe = P['K'] * P['delta'] * (P['z_top'] - P['z_bot']) ** 2 / (2 * P['q_in'])
            c = ((g.xc[g.J] < 0.5 * toe * (1 - (g.zc[g.I] - P['z_bot']) / (P['z_top'] - P['z_bot'])))).astype(float)
            y = np.r_[np.ones(N), c]
        else:
            y = y0.copy()
        ptdt = 1.0 * YR
        stv = np.r_[np.full(N, 1e-3), P['n'] * g.V]
        for it in range(200):
            yp = y.copy()
            for k in range(6):
                R = self.residual(y, y, None, 0.0, steady=True) + stv * (y - yp) / ptdt
                Jm = self.jac(y, y, 0.0, steady=True) + sp.diags(stv / ptdt)
                dy = spla.spsolve(Jm.tocsc(), -R)
                lim = np.abs(dy[N:]).max()
                y = y + dy * (min(1.0, 0.5 / lim) if lim > 0 else 1.0)
                if np.abs(dy).max() < 1e-9:
                    break
            if verbose and it % 5 == 0:
                print('pt', it, ptdt / YR, np.abs(y - yp).max())
            if ptdt > 1e5 * YR and np.abs(y - yp).max() < 1e-9:
                break
            ptdt *= 2.0 if np.abs(y - yp)[N:].max() < 0.3 else 1.0
        for k in range(15):
            R = self.residual(y, y, None, 0.0, steady=True)
            if verbose:
                print('newton', k, np.abs(R).max())
            if np.abs(R).max() < tol:
                break
            y = y - spla.spsolve(self.jac(y, y, 0.0, steady=True).tocsc(), R)
        self.y_ss = y
        return y

    # ------------------------------------------------------------------ forward
    def run(self, y0=None, schedule=None, t0=0.0, keep=True, ions=False, toe=True, z0=None):
        """Implicit Euler over the schedule; returns J = sea fraction over the supply screen of the last layout."""
        g, N = self.g, self.g.N
        if y0 is None:
            y0 = self.y_ss if hasattr(self, 'y_ss') else self.steady()
        if schedule is None:
            schedule = [(self.nsteps, self.layout)]
        self.t0 = t0
        self.Wn = [None]
        self.seg = [None]
        for s, (ns, lay) in enumerate(schedule):
            Wo, Wi, _, _, _ = self.wells_of(lay)
            self.Wn += [(Wo, Wi)] * ns
            self.seg += [s] * ns
        self.set_layout(schedule[-1][1])
        nst = len(self.Wn) - 1
        self.nst = nst
        if self.Ah_lu is None:
            self.Ah_lu = spla.splu(self.Ah)
        y = y0.copy()
        z = np.r_[y[:N], y[:N], y[N:], y[N:]] if z0 is None else z0.copy()
        self.Y = [y.copy()] if keep else None
        self.Z = [z.copy()] if keep else None
        self.its = []
        self.Jt = [self.J(y)] if self.wJ is not None else None
        toe_x = [self.toe(y)] if toe else None
        if ions:
            import ions as IO
            self.ion = IO.IonBlock(self, y)
            self.ion_t = [self.ion.screen_mgL()]
        tt = time.time()
        for n in range(1, nst + 1):
            t = t0 + n * self.dt
            Wo, Wi = self.Wn[n]
            yo, zo = y, z
            Dcoef, _ = self.disp(self.Gh @ yo[:N] + self.Gc @ yo[N:] + self.g0(t - self.dt))
            mem_h = self.mh_coef[0] * zo[:N] + self.mh_coef[1] * zo[N:2 * N]
            mem_c = self.mc_coef[0] * zo[2 * N:3 * N] + self.mc_coef[1] * zo[3 * N:]
            g0 = self.g0(t)
            # split pass: flow with the old buoyancy, then salt with those fluxes (exact for the split assembly)
            h = self.Ah_lu.solve(self.st_h * yo[:N] + mem_h - g.Div @ (self.Gc @ yo[N:] + g0) - Wo + Wi)
            Q = self.Gh @ h + self.Gc @ yo[N:] + g0
            Ac, ghost = self.transport_matrix(Q, Dcoef, Wi)
            lu_c = spla.splu(Ac.tocsc())
            c = lu_c.solve(self.st_c * yo[N:] + mem_c - g.Div @ (Q * ghost))
            y = np.r_[h, c]
            nit = 0
            if self.o['coupling'] != 'split':
                # monolithic: chord Newton on the coupled step with the exact Jacobian
                lu_J = spla.splu(self.jac(y, yo, t, n).tocsc())
                prev = np.inf
                for it in range(48):
                    dy = lu_J.solve(-self.residual(y, yo, zo, t, n))
                    y = y + dy
                    nit += 1
                    err = np.abs(dy[N:]).max()
                    if err < 1e-10 and np.abs(dy[:N]).max() < 1e-8:
                        break
                    if err > 0.5 * prev:
                        lu_J = spla.splu(self.jac(y, yo, t, n).tocsc())
                    prev = err
                h, c = y[:N], y[N:]
                if ions:
                    Q = self.Gh @ h + self.Gc @ c + g0
                    Ac, ghost = self.transport_matrix(Q, Dcoef, Wi)
                    lu_c = spla.splu(Ac.tocsc())
            self.its.append(nit)
            z = np.r_[self.alpha_h[0] * zo[:N] + self.beta_h[0] * h, self.alpha_h[1] * zo[N:2 * N] + self.beta_h[1] * h,
                      self.alpha_c[0] * zo[2 * N:3 * N] + self.beta_c[0] * c, self.alpha_c[1] * zo[3 * N:] + self.beta_c[1] * c]
            if ions:
                self.W_in = Wi
                tion = time.time()
                self.ion.step(lu_c, Q, ghost)
                self.ion_cpu = getattr(self, 'ion_cpu', 0.0) + time.time() - tion
                self.ion_t.append(self.ion.screen_mgL())
            if keep:
                self.Y.append(y.copy()); self.Z.append(z.copy())
            if self.Jt is not None:
                self.Jt.append(self.J(y))
            if toe:
                toe_x.append(self.toe(y))
        self.set_layout(schedule[-1][1])
        self.cpu = time.time() - tt
        self.y_end, self.z_end = y, z
        self.toe_x = np.array(toe_x) if toe else None
        return self.J(y) if self.wJ is not None else None

    def J(self, y):
        return float(self.wJ @ y[self.g.N:])

    def toe(self, y):
        """landward end of the c = 1/2 contour on the base row (m from the coast)."""
        g = self.g
        cb = y[g.N:][:g.NX]
        idx = np.flatnonzero(cb >= 0.5)
        if len(idx) == 0:
            return 0.0
        j = idx.max()
        if j == g.NX - 1:
            return float(g.xc[-1])
        return float(g.xc[j] + (cb[j] - 0.5) / (cb[j] - cb[j + 1]) * (g.xc[j + 1] - g.xc[j]))

    # ------------------------------------------------------------------ adjoint
    def adjoint(self, wJ=None, last_segment=True):
        """Exact discrete adjoint of the stored run (from the pre-development equilibrium) for J = wJ' c_end."""
        g, N, nst = self.g, self.g.N, self.nst
        wJ = self.wJ if wJ is None else wJ
        Y = self.Y
        lam = [None] * (nst + 1)
        mu = np.zeros(4 * N)
        alpha = np.r_[np.full(N, self.alpha_h[0]), np.full(N, self.alpha_h[1]), np.full(N, self.alpha_c[0]), np.full(N, self.alpha_c[1])]
        lam_next = Jold_next = None
        for n in range(nst, 0, -1):
            t = self.t0 + n * self.dt
            rhs = np.zeros(2 * N)
            if n == nst:
                rhs[N:] += wJ
            if lam_next is not None:
                rhs -= Jold_next.T @ lam_next
            rhs[:N] += self.mh_on[0] * self.beta_h[0] * mu[:N] + self.mh_on[1] * self.beta_h[1] * mu[N:2 * N]
            rhs[N:] += self.mc_on[0] * self.beta_c[0] * mu[2 * N:3 * N] + self.mc_on[1] * self.beta_c[1] * mu[3 * N:]
            ln = spla.spsolve(self.jac(Y[n], Y[n - 1], t, n).T.tocsc(), rhs)
            lam[n] = ln
            dRz = np.r_[-self.mh_coef[0] * ln[:N], -self.mh_coef[1] * ln[:N], -self.mc_coef[0] * ln[N:], -self.mc_coef[1] * ln[N:]]
            mu = alpha * mu - dRz
            lam_next, Jold_next = ln, self.jac_old(Y[n], Y[n - 1], t)
        self.mu0 = mu
        if self.t0 == 0.0:
            rhs = -(Jold_next.T @ lam_next)
            rhs[:N] += mu[:N] + mu[N:2 * N]
            rhs[N:] += mu[2 * N:3 * N] + mu[3 * N:]
            lam[0] = spla.spsolve(self.jac(Y[0], Y[0], 0.0, steady=True).T.tocsc(), rhs)
        self.lam = lam
        last = self.seg[-1]
        steps = [n for n in range(1, nst + 1) if (self.seg[n] == last or not last_segment)]
        out = dict(dJ_dQ=-sum(lam[n][:N] @ self.e_Q for n in steps))
        gm = np.zeros(g.NX)
        share = g.dz[g.I] / g.dz.sum()
        for n in steps:
            contrib = -lam[n][:N] + lam[n][N:] * Y[n][N:]
            gm -= np.bincount(g.J, weights=contrib * share, minlength=g.NX)
        out['dJ_dqr_col'] = gm
        return out

    def weight(self, hom_dir, eps=1e-6):
        """goal weight of a term: dJ/ds at the model's assembly, s the homotopy scale of the term (s = 1 kept,
        s = 0 removed); the first-order change of J if the term is removed is - weight.
        hom_dir(s) returns the `hom` dict for scale s."""
        tot = 0.0
        for n in range(1, self.nst + 1):
            t = self.t0 + n * self.dt
            Ra = self.residual(self.Y[n], self.Y[n - 1], self.Z[n - 1], t, n, hom=hom_dir(1.0 - eps))
            Rb = self.residual(self.Y[n], self.Y[n - 1], self.Z[n - 1], t, n, hom=hom_dir(1.0))
            tot -= self.lam[n] @ (Rb - Ra) / eps
        if self.lam[0] is not None:
            Ra = self.residual(self.Y[0], self.Y[0], None, 0.0, steady=True, hom=hom_dir(1.0 - eps))
            Rb = self.residual(self.Y[0], self.Y[0], None, 0.0, steady=True, hom=hom_dir(1.0))
            tot -= self.lam[0] @ (Rb - Ra) / eps
        return tot

    def weight_steps(self, hom_dir, eps=1e-6):
        """the same weight split by time step (n = 0 is the pre-development state)."""
        w = np.zeros(self.nst + 1)
        for n in range(1, self.nst + 1):
            t = self.t0 + n * self.dt
            Ra = self.residual(self.Y[n], self.Y[n - 1], self.Z[n - 1], t, n, hom=hom_dir(1.0 - eps))
            Rb = self.residual(self.Y[n], self.Y[n - 1], self.Z[n - 1], t, n, hom=hom_dir(1.0))
            w[n] = -self.lam[n] @ (Rb - Ra) / eps
        return w

    def dwr(self, mH, Ph):
        """J_h(I y_H) - J_h(y_h) ~ sum_n lambda_n' R_n(I y_H) + lambda_0' R_0(I y_H,0): total, per fine column
        (signed) and per fine column of |lambda R| summed over cells and steps (the mesh indicator)."""
        N = self.g.N
        P4 = sp.block_diag([Ph] * 4).tocsr()
        P2 = sp.block_diag([Ph] * 2).tocsr()
        eta = np.zeros(2 * N); etab = np.zeros(2 * N)
        if self.lam[0] is not None:
            R0 = self.residual(P2 @ mH.Y[0], P2 @ mH.Y[0], None, 0.0, steady=True)
            eta += self.lam[0] * R0; etab += np.abs(self.lam[0] * R0)
        for n in range(1, self.nst + 1):
            t = self.t0 + n * self.dt
            Rn = self.residual(P2 @ mH.Y[n], P2 @ mH.Y[n - 1], P4 @ mH.Z[n - 1], t, n)
            eta += self.lam[n] * Rn; etab += np.abs(self.lam[n] * Rn)
        col = np.bincount(self.g.J, weights=eta[:N] + eta[N:], minlength=self.g.NX)
        colabs = np.bincount(self.g.J, weights=etab[:N] + etab[N:], minlength=self.g.NX)
        return float(eta.sum()), col, colabs
