"""Python port of the SWI-Goal-OED Henry solver (src/vd_residual.m, vd_solve_forward.m).

Same discretization: cell-centred finite volumes, equivalent-freshwater head h and
relative concentration c, harmonic-mean face K, first-order upwind advection,
freshwater inflow flux Q at x=0, hydrostatic sea boundary with c=1 at x=L.
State packing U = [h; c], flat index k = j*Nx + i (row j = z, column i = x).
Newton with a finite-difference Jacobian built by column colouring (10 residual
evaluations per Jacobian instead of 2N) and the same halving line search.
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla


class Henry:
    def __init__(self, Nx=41, Ny=21, Lx=2.0, Ly=1.0, eps=0.025, phi=0.35,
                 Dmol=1.62925 / 86400, Q=6.6e-5, Kref=1.0e-2):
        self.Nx, self.Ny, self.Lx, self.Ly = Nx, Ny, Lx, Ly
        self.dx, self.dy, self.N = Lx / Nx, Ly / Ny, Nx * Ny
        self.xc = (np.arange(Nx) + 0.5) * self.dx
        self.yc = (np.arange(Ny) + 0.5) * self.dy
        self.eps, self.phi, self.D, self.Q, self.Kref = eps, phi, Dmol, Q, Kref
        self.hR = eps * (Ly - self.yc)                     # sea-side equivalent head per row
        self._build_colouring()

    # ------------------------------------------------------------------ residual
    def residual(self, U, theta):
        Nx, Ny, N, dx, dy = self.Nx, self.Ny, self.N, self.dx, self.dy
        h = U[:N].reshape(Ny, Nx)
        c = U[N:].reshape(Ny, Nx)
        K = (self.Kref * np.exp(theta)).reshape(Ny, Nx)
        eps, phi, D = self.eps, self.phi, self.D

        qx = np.empty((Ny, Nx + 1))
        Khx = 2 * K[:, :-1] * K[:, 1:] / (K[:, :-1] + K[:, 1:])
        qx[:, 1:Nx] = -Khx * (h[:, 1:] - h[:, :-1]) / dx
        qx[:, 0] = self.Q
        qx[:, Nx] = -K[:, -1] * (self.hR - h[:, -1]) / (0.5 * dx)
        qy = np.zeros((Ny + 1, Nx))
        Khy = 2 * K[:-1, :] * K[1:, :] / (K[:-1, :] + K[1:, :])
        qy[1:Ny, :] = -Khy * ((h[1:, :] - h[:-1, :]) / dy + eps * 0.5 * (c[:-1, :] + c[1:, :]))

        Fh = (qx[:, 1:] - qx[:, :-1]) / dx + (qy[1:, :] - qy[:-1, :]) / dy

        cx = np.empty((Ny, Nx + 2)); cx[:, 0] = 0.0; cx[:, 1:-1] = c; cx[:, -1] = 1.0
        cfx = np.where(qx > 0, cx[:, :-1], cx[:, 1:])          # upwind face values
        cy = np.empty((Ny + 2, Nx)); cy[0] = c[0]; cy[1:-1] = c; cy[-1] = c[-1]
        cfy = np.where(qy > 0, cy[:-1, :], cy[1:, :])
        fx, fy = qx * cfx, qy * cfy
        adv = (fx[:, 1:] - fx[:, :-1]) / dx + (fy[1:, :] - fy[:-1, :]) / dy
        lap = (cx[:, 2:] - 2 * c + cx[:, :-2]) / dx ** 2 + (cy[2:, :] - 2 * c + cy[:-2, :]) / dy ** 2
        Fc = adv - phi * D * lap
        return np.concatenate([Fh.ravel(), Fc.ravel()])

    # ------------------------------------------------------------------ Jacobian
    def _build_colouring(self):
        Nx, Ny, N = self.Nx, self.Ny, self.N
        jj, ii = np.divmod(np.arange(N), Nx)
        self.col5 = (ii + 2 * jj) % 5                       # distance-2 colouring of the 5-point stencil
        rows, cols = [], []
        for dj, di in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            j2, i2 = jj + dj, ii + di
            ok = (j2 >= 0) & (j2 < Ny) & (i2 >= 0) & (i2 < Nx)
            rows.append((j2 * Nx + i2)[ok]); cols.append(np.arange(N)[ok])
        r = np.concatenate(rows); cl = np.concatenate(cols)
        # cell-level pattern -> 2x2 field blocks
        R, C = [], []
        for a in (0, 1):
            for b in (0, 1):
                R.append(r + a * N); C.append(cl + b * N)
        self.pat_r = np.concatenate(R); self.pat_c = np.concatenate(C)
        self.cell_r, self.cell_c = r, cl

    def jacobian(self, U, theta, F0=None, eps_fd=1e-7):
        N = self.N
        if F0 is None:
            F0 = self.residual(U, theta)
        d = eps_fd * np.maximum(1.0, np.abs(U))
        vals = np.empty(self.pat_r.size)
        colour = np.concatenate([self.col5, self.col5 + 5])
        dF_by_col = {}
        for k in range(10):
            mask = colour == k
            Up = U.copy(); Up[mask] += d[mask]
            dF_by_col[k] = self.residual(Up, theta) - F0
        vals = dF_by_col_lookup(dF_by_col, colour, self.pat_r, self.pat_c) / d[self.pat_c]
        return sp.csc_matrix((vals, (self.pat_r, self.pat_c)), shape=(2 * N, 2 * N))

    def dR_dtheta(self, U, theta, eps_fd=1e-6):
        """Residual derivative with respect to the per-cell log-conductivity (central FD, coloured)."""
        N = self.N
        out_vals = []
        r_all, c_all = [], []
        for k in range(5):
            mask = self.col5 == k
            tp = theta.copy(); tp[mask] += eps_fd
            tm = theta.copy(); tm[mask] -= eps_fd
            dF = (self.residual(U, tp) - self.residual(U, tm)) / (2 * eps_fd)
            sel = mask[self.cell_c]
            for a in (0, 1):
                rr = self.cell_r[sel] + a * N
                out_vals.append(dF[rr]); r_all.append(rr); c_all.append(self.cell_c[sel])
        return sp.csc_matrix((np.concatenate(out_vals), (np.concatenate(r_all), np.concatenate(c_all))),
                             shape=(2 * N, N))

    # ------------------------------------------------------------------ solve
    def solve(self, theta, tol=1e-12, maxit=60, U0=None):
        N = self.N
        if U0 is None:
            U = np.zeros(2 * N); U[N:] = 0.1
        else:
            U = U0.copy()
        nF = np.inf
        for it in range(maxit):
            F = self.residual(U, theta); nF = np.linalg.norm(F)
            if nF < tol:
                break
            J = self.jacobian(U, theta, F)
            dU = -spla.spsolve(J, F)
            lam = 1.0
            for _ in range(20):
                if np.linalg.norm(self.residual(U + lam * dU, theta)) < nF:
                    break
                lam *= 0.5
            U = U + lam * dU
        return U, nF, it

    def conc(self, U):
        return U[self.N:].reshape(self.Ny, self.Nx)

    def toe(self, U):
        cb = self.conc(U)[0]
        for i in range(self.Nx - 1):
            if (cb[i] - 0.5) * (cb[i + 1] - 0.5) < 0:
                return self.xc[i] + (0.5 - cb[i]) / (cb[i + 1] - cb[i]) * (self.xc[i + 1] - self.xc[i])
        return np.nan


def dF_by_col_lookup(dF_by_col, colour, pr, pc):
    out = np.empty(pr.size)
    cc = colour[pc]
    for k, dF in dF_by_col.items():
        m = cc == k
        out[m] = dF[pr[m]]
    return out


if __name__ == '__main__':
    import time
    for (nx, ny) in [(16, 8), (32, 16), (41, 21)]:
        m = Henry(nx, ny)
        t0 = time.time()
        U, nF, it = m.solve(np.zeros(m.N))
        print(f'{nx}x{ny}: toe = {m.toe(U):.4f} m, |F| = {nF:.2e}, Newton its = {it}, {time.time() - t0:.2f} s')
    # colouring check against a dense FD Jacobian on a small grid
    m = Henry(8, 5)
    th = 0.3 * np.random.default_rng(0).standard_normal(m.N)
    U, _, _ = m.solve(th)
    J = m.jacobian(U, th).toarray()
    F0 = m.residual(U, th); Jd = np.zeros_like(J)
    for k in range(2 * m.N):
        d = 1e-7 * max(1.0, abs(U[k])); Up = U.copy(); Up[k] += d
        Jd[:, k] = (m.residual(Up, th) - F0) / d
    print('coloured vs dense Jacobian, max rel diff:', np.abs(J - Jd).max() / np.abs(Jd).max())
