"""Steady variable-density chloride section (equivalent-freshwater-head form), Picard solver.

    flow:      div[ K (grad h + eps c e_z) ] = 0,  q = -K (grad h + eps c e_z),  e_z upward
    transport: div(q c) - div(phi D grad c) = 0,   D = Dm + alpha_L|q| (along) + alpha_T|q| (across), diagonal
Cell-centred finite volumes on a masked rectangular grid (the aquifer between its top and its base), harmonic
face conductivity, anisotropic K (Kz = Kx * aniso), first-order upwind advection: the discretization of
src/vd_residual.m, generalized to a masked domain and to velocity-dependent dispersion (cross terms omitted).
Sea at x = 0 (hydrostatic seawater column, c = 1 on inflow, zero gradient on outflow; mode='henry' imposes
c = 1 on the whole sea face for the diffusive flux, as in Henry's problem), freshwater inflow Qin [m2/d per m]
at x = L distributed over the active cells of the last column in proportion to Kx.
Picard: solve flow for c, transport for q, relax c, until max|dc| < tol.
x is distance from the sea [m]; z is depth below sea level [m], positive down.
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla


class Section:
    def __init__(self, xe, ze, top, bot, Kx, aniso=0.1, eps=0.025, phi=0.25, Dm=8.64e-5, aL=10.0, aT=1.0,
                 Qin=1.0, mode='field'):
        """xe, ze: cell edges [m] (x from the sea, z depth); top, bot: aquifer top/base depth per column [m];
        Kx: horizontal conductivity per column [m/d] (or per cell, shape (nz, nx))."""
        self.xe, self.ze = np.asarray(xe, float), np.asarray(ze, float)
        self.xc, self.zc = 0.5 * (self.xe[1:] + self.xe[:-1]), 0.5 * (self.ze[1:] + self.ze[:-1])
        self.dx, self.dz = np.diff(self.xe), np.diff(self.ze)
        nx, nz = len(self.xc), len(self.zc)
        self.nx, self.nz = nx, nz
        Z = self.zc[:, None]
        self.act = (Z >= np.asarray(top)[None, :]) & (Z <= np.asarray(bot)[None, :])
        Kx = np.asarray(Kx, float)
        self.Kx = np.broadcast_to(Kx[None, :] if Kx.ndim == 1 else Kx, (nz, nx)).copy()
        self.Kz = self.Kx * aniso
        self.eps, self.phi, self.Dm, self.aL, self.aT, self.Qin, self.mode = eps, phi, Dm, aL, aT, Qin, mode
        self.idx = -np.ones((nz, nx), int)
        self.idx[self.act] = np.arange(self.act.sum())
        self.N = int(self.act.sum())
        jj, ii = np.nonzero(self.act)
        self.jj, self.ii = jj, ii
        # internal faces: x-faces between (j,i) and (j,i+1); z-faces between (j,i) and (j+1,i)
        mx = self.act[:, :-1] & self.act[:, 1:]
        self.fx_j, self.fx_i = np.nonzero(mx)
        mz = self.act[:-1, :] & self.act[1:, :]
        self.fz_j, self.fz_i = np.nonzero(mz)
        hm = lambda a, b: 2 * a * b / (a + b)
        self.Kfx = hm(self.Kx[self.fx_j, self.fx_i], self.Kx[self.fx_j, self.fx_i + 1])
        self.Kfz = hm(self.Kz[self.fz_j, self.fz_i], self.Kz[self.fz_j + 1, self.fz_i])
        self.dxf = 0.5 * (self.dx[self.fx_i] + self.dx[self.fx_i + 1])
        self.dzf = 0.5 * (self.dz[self.fz_j] + self.dz[self.fz_j + 1])
        # sea faces: west face of active cells in column 0
        self.sea_j = np.flatnonzero(self.act[:, 0])
        self.hsea = eps * self.zc[self.sea_j]                 # equivalent freshwater head of the seawater column
        # inflow faces: east face of active cells in the last column, flux share proportional to Kx * dz
        self.in_j = np.flatnonzero(self.act[:, -1])
        sh = self.Kx[self.in_j, -1] * self.dz[self.in_j]
        self.qin = Qin * sh / sh.sum() / self.dz[self.in_j]  # Darcy flux [m/d] entering each face (toward -x)

    # -------------------------------------------------------------- flow given c
    def flow(self, c):
        N, idx = self.N, self.idx
        a = idx[self.fx_j, self.fx_i]; b = idx[self.fx_j, self.fx_i + 1]
        tx = self.Kfx * self.dz[self.fx_j] / self.dxf                      # x-face transmissibility
        u = idx[self.fz_j, self.fz_i]; d = idx[self.fz_j + 1, self.fz_i]   # u above (shallower), d below
        tz = self.Kfz * self.dx[self.fz_i] / self.dzf
        rows = [a, b, a, b, u, d, u, d]
        cols = [a, b, b, a, u, d, d, u]
        vals = [tx, tx, -tx, -tx, tz, tz, -tz, -tz]
        rhs = np.zeros(N)
        # buoyancy on z-faces: upward flux q_up = -Kz (dh/dz_up + eps c); with depth z (down), dh/dz_up = -(h_d - h_u)/dzf...
        # flux from u to d (downward) = -Kz*( (h_d - h_u)/dzf ) - Kz*eps*cf  (positive downward)
        cf = 0.5 * (c[u] + c[d])
        g = self.Kfz * self.eps * cf * self.dx[self.fz_i]                 # buoyant downward flux contribution
        np.add.at(rhs, u, -g); np.add.at(rhs, d, g)
        # sea faces (half-cell distance)
        s = idx[self.sea_j, 0]
        ts = self.Kx[self.sea_j, 0] * self.dz[self.sea_j] / (0.5 * self.dx[0])
        rows.append(s); cols.append(s); vals.append(ts)
        np.add.at(rhs, s, ts * self.hsea)
        # inflow
        e = idx[self.in_j, -1]
        np.add.at(rhs, e, self.qin * self.dz[self.in_j])
        A = sp.csc_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(N, N))
        h = spla.spsolve(A, rhs)
        # fluxes [m/d], positive in +x and +z (downward)
        qx = -self.Kfx * (h[b] - h[a]) / self.dxf
        qz = -self.Kfz * ((h[d] - h[u]) / self.dzf) + self.Kfz * self.eps * cf * 0 - 0  # placeholder replaced below
        qz = -self.Kfz * (h[d] - h[u]) / self.dzf - self.Kfz * self.eps * cf * (-1.0)
        qsea = -self.Kx[self.sea_j, 0] * (h[s] - self.hsea) / (0.5 * self.dx[0])   # +x flux at the sea face
        return h, qx, qz, qsea

    # -------------------------------------------------------------- transport given q
    def transport(self, qx, qz, qsea, dt=None, c_old=None):
        N, idx = self.N, self.idx
        a = idx[self.fx_j, self.fx_i]; b = idx[self.fx_j, self.fx_i + 1]
        u = idx[self.fz_j, self.fz_i]; d = idx[self.fz_j + 1, self.fz_i]
        Ax = self.dz[self.fx_j]; Az = self.dx[self.fz_i]
        # face velocity magnitude (use the face-normal component and an average of the transverse one)
        qxc = np.zeros(N); qzc = np.zeros(N); cnt_x = np.zeros(N); cnt_z = np.zeros(N)
        np.add.at(qxc, a, qx); np.add.at(qxc, b, qx); np.add.at(cnt_x, a, 1); np.add.at(cnt_x, b, 1)
        np.add.at(qzc, u, qz); np.add.at(qzc, d, qz); np.add.at(cnt_z, u, 1); np.add.at(cnt_z, d, 1)
        qxc /= np.maximum(cnt_x, 1); qzc /= np.maximum(cnt_z, 1)
        if self.mode == 'henry':
            Dx = np.full(len(qx), self.phi * self.Dm); Dz = np.full(len(qz), self.phi * self.Dm)
            Dsea = np.full(len(self.sea_j), self.phi * self.Dm)
        else:
            qzx = 0.5 * (qzc[a] + qzc[b]); qxz = 0.5 * (qxc[u] + qxc[d])
            vx = np.sqrt(qx ** 2 + qzx ** 2) + 1e-30; vz = np.sqrt(qxz ** 2 + qz ** 2) + 1e-30
            Dx = self.phi * self.Dm + self.aL * qx ** 2 / vx + self.aT * qzx ** 2 / vx
            Dz = self.phi * self.Dm + self.aT * qxz ** 2 / vz + self.aL * qz ** 2 / vz
            s0 = idx[self.sea_j, 0]
            Dsea = self.phi * self.Dm + self.aL * np.abs(qsea)
        rows, cols, vals = [], [], []
        rhs = np.zeros(N)

        def add(r, c_, v):
            rows.append(r); cols.append(c_); vals.append(v)
        # advection, upwind: flux F = q*A*c_up, residual sum of outgoing fluxes
        for (p, q_, fl, Ar) in ((a, b, qx, Ax), (u, d, qz, Az)):
            pos = fl > 0
            F = fl * Ar
            # from p to q_ when positive: p loses F*c_p, q_ gains
            add(p[pos], p[pos], F[pos]); add(q_[pos], p[pos], -F[pos])
            ng = ~pos
            add(q_[ng], q_[ng], -F[ng]); add(p[ng], q_[ng], F[ng])
        # dispersion
        tdx = Dx * Ax / self.dxf; tdz = Dz * Az / self.dzf
        for (p, q_, t) in ((a, b, tdx), (u, d, tdz)):
            add(p, p, t); add(q_, q_, t); add(p, q_, -t); add(q_, p, -t)
        # sea face
        s = idx[self.sea_j, 0]
        As = self.dz[self.sea_j]
        Fs = qsea * As                                    # +x flux at x=0: >0 means inflow of seawater
        inflow = Fs > 0
        np.add.at(rhs, s[inflow], Fs[inflow] * 1.0)       # advective inflow with c = 1
        add(s[~inflow], s[~inflow], -Fs[~inflow])         # outflow carries c_cell
        if self.mode == 'henry':
            # repository convention (src/vd_residual.m): ghost values c = 1 at the sea and c = 0 at the
            # inflow face, one full cell away
            td = Dsea * As / self.dx[0]
            add(s, s, td); np.add.at(rhs, s, td * 1.0)
            e = idx[self.in_j, -1]
            add(e, e, Dsea[:len(e)] * self.dz[self.in_j] / self.dx[-1])
        else:
            td = Dsea * As / (0.5 * self.dx[0])
            add(s[inflow], s[inflow], td[inflow]); np.add.at(rhs, s[inflow], td[inflow] * 1.0)
        # east inflow with c = 0: advective flux enters with zero concentration (no term); diffusion zero-gradient
        if dt is not None:                               # implicit Euler storage term (pseudo-transient)
            vol = self.dx[self.ii] * self.dz[self.jj]
            add(np.arange(N), np.arange(N), self.phi * vol / dt)
            rhs = rhs + self.phi * vol / dt * c_old
        A = sp.csc_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(N, N))
        return spla.spsolve(A, rhs)

    def solve(self, tol=1e-7, maxit=500, omega=0.7, c0=None, verbose=False):
        c = np.full(self.N, 0.5) if c0 is None else c0.copy()
        for it in range(maxit):
            h, qx, qz, qs = self.flow(c)
            cn = np.clip(self.transport(qx, qz, qs), 0.0, 1.0)
            dc = np.max(np.abs(cn - c))
            c = omega * cn + (1 - omega) * c
            if verbose and it % 20 == 0:
                print(it, dc)
            if dc < tol:
                break
        self.h, self.c, self.iters, self.dc = h, c, it, dc
        return c

    def solve_ptc(self, c0=None, dt0=1.0, grow=1.4, dtmax=1e7, tol=1e-9, maxit=600, verbose=False):
        """pseudo-transient continuation: implicit Euler in time with growing steps until the steady state.
        The flow is solved with the concentration of the previous step (semi-implicit coupling)."""
        c = np.zeros(self.N) if c0 is None else c0.copy()
        dt = dt0
        for it in range(maxit):
            h, qx, qz, qs = self.flow(c)
            cn = np.clip(self.transport(qx, qz, qs, dt=dt, c_old=c), 0.0, 1.0)
            dc = np.max(np.abs(cn - c))
            c = cn
            if verbose and it % 25 == 0:
                print(it, f'dt={dt:.3g}', f'dc={dc:.3g}')
            if dt >= dtmax and dc < tol:
                break
            dt = min(dt * grow, dtmax)
        # steady residual check: one Picard update without storage
        h, qx, qz, qs = self.flow(c)
        cs = np.clip(self.transport(qx, qz, qs), 0.0, 1.0)
        self.h, self.c, self.iters, self.dc, self.steady_gap = h, c, it, dc, float(np.max(np.abs(cs - c)))
        return c

    def solve_implicit(self, c0=None, dt0=10.0, dtmax=1e5, t_end=None, tol_in=1e-8, max_in=25, tol_ss=1e-6,
                       max_steps=2000, verbose=False):
        """fully implicit Euler march to the steady state: each step converges the flow-transport coupling
        by inner Picard iterations; the step halves when the inner loop fails and grows when it converges
        in a few iterations. Stops when one step of length dtmax changes c by less than tol_ss."""
        c = np.zeros(self.N) if c0 is None else c0.copy()
        dt, t, nin_tot = dt0, 0.0, 0
        for step in range(max_steps):
            ck = c.copy(); ok = False
            for k in range(max_in):
                h, qx, qz, qs = self.flow(ck)
                cn = np.clip(self.transport(qx, qz, qs, dt=dt, c_old=c), 0.0, 1.0)
                d_in = np.max(np.abs(cn - ck)); ck = cn
                if d_in < tol_in:
                    ok = True
                    break
            nin_tot += k + 1
            if not ok:
                dt *= 0.5
                if dt < 1e-3:
                    raise RuntimeError('time step collapsed')
                continue
            dc = np.max(np.abs(ck - c)); c = ck; t += dt
            if verbose and step % 20 == 0:
                print(step, f't={t:.4g} d', f'dt={dt:.3g}', f'dc={dc:.3g}', f'inner={k + 1}')
            if step % 25 == 24:
                h_, qx_, qz_, qs_ = self.flow(c)
                gap = np.max(np.abs(np.clip(self.transport(qx_, qz_, qs_), 0.0, 1.0) - c))
                if verbose:
                    print('   steady gap', f'{gap:.3g}')
                if gap < tol_ss:
                    break
            if k < 6:
                dt = min(dt * 1.6, dtmax)
        h, qx, qz, qs = self.flow(c)
        cs = np.clip(self.transport(qx, qz, qs), 0.0, 1.0)
        self.h, self.c, self.iters, self.dc, self.t_end, self.inner = h, c, step, dc, t, nin_tot
        self.steady_gap = float(np.max(np.abs(cs - c)))
        return c

    def field(self, v):
        F = np.full((self.nz, self.nx), np.nan)
        F[self.jj, self.ii] = v
        return F

    def toe(self, level=0.5):
        """distance from the sea [m] where c at the deepest active cell of each column crosses `level`."""
        C = self.field(self.c)
        base = np.array([C[np.flatnonzero(self.act[:, i]).max(), i] if self.act[:, i].any() else np.nan
                         for i in range(self.nx)])
        for i in range(self.nx - 1):
            if (base[i] - level) * (base[i + 1] - level) < 0:
                return self.xc[i] + (level - base[i]) / (base[i + 1] - base[i]) * (self.xc[i + 1] - self.xc[i])
        return np.nan


def henry(nx=41, nz=21):
    """Henry's problem in this orientation (sea at x = 0). Returns the toe measured from the inflow face,
    the quantity reported by the repository (1.3918 m at 41 x 21)."""
    L, H = 2.0, 1.0
    s = Section(np.linspace(0, L, nx + 1), np.linspace(0, H, nz + 1), np.zeros(nx), np.full(nx, H),
                np.full(nx, 1.0e-2), aniso=1.0, eps=0.025, phi=0.35, Dm=1.62925 / 86400, aL=0, aT=0,
                Qin=6.6e-5, mode='henry')
    s.solve(tol=1e-11, maxit=3000, omega=0.5)
    return L - s.toe(), s


if __name__ == '__main__':
    t, s = henry()
    print(f'Henry 41x21: toe from the inflow face = {t:.4f} m (repository solver 1.3918 m); Picard iterations {s.iters}, last dc {s.dc:.1e}')
