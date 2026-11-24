"""Pore-scale flow solver for the KAOS-GO experiment: two-dimensional lattice-Boltzmann method (D2Q9), two-relaxation-time
collision (viscosity-independent wall position), body force after Guo, halfway bounce-back on the solid, periodic cell.

The quantities returned are in lattice units.  u is the physical velocity (momentum plus half the force); the strain rate
is taken from the non-equilibrium populations, S = -(3 w+ / (2 rho)) (Pi_neq + rho (u g + g u) / 2), and the dissipation
rate is 2 rho nu S:S.  Gates (kaos_gates.py): drag of a square array against Sangani & Acrivos (1982), closure of the
energy budget g.U = <dissipation>, linearity of the Darcy regime.
"""
import numpy as np
from numba import njit, prange

CX = np.array([0, 1, 0, -1, 0, 1, -1, -1, 1], dtype=np.int64)
CY = np.array([0, 0, 1, 0, -1, 1, 1, -1, -1], dtype=np.int64)
WT = np.array([4 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 36, 1 / 36, 1 / 36, 1 / 36])
OPP = np.array([0, 3, 4, 1, 2, 7, 8, 5, 6], dtype=np.int64)
MAGIC = 3.0 / 16.0


def rates(nu):
    """relaxation rates (w+, w-) of the two-relaxation-time collision for a kinematic viscosity nu."""
    tp = 3.0 * nu + 0.5
    tm = 0.5 + MAGIC / (tp - 0.5)
    return 1.0 / tp, 1.0 / tm


@njit(parallel=True, fastmath=True, cache=True)
def _step(f, fn, solid, omp, omm, gx, gy, acc, do_acc):
    """one fused pull-stream and collide step from f into fn; with do_acc the fields of acc are incremented.
    Returns the sums over the cell of ux, uy, u.u/2 (times rho) and of the dissipation rate (zeros without do_acc)."""
    ny, nx = solid.shape
    nu = (1.0 / omp - 0.5) / 3.0
    su = 0.0
    sv = 0.0
    ske = 0.0
    sphi = 0.0
    for y in prange(ny):
        fi = np.empty(9)
        ym = y - 1 if y > 0 else ny - 1
        yp = y + 1 if y < ny - 1 else 0
        for x in range(nx):
            if solid[y, x]:
                continue
            xm = x - 1 if x > 0 else nx - 1
            xp = x + 1 if x < nx - 1 else 0
            # pull: population i comes from the node at -c_i; from a solid it is the bounced-back one
            fi[0] = f[0, y, x]
            fi[1] = f[3, y, x] if solid[y, xm] else f[1, y, xm]
            fi[2] = f[4, y, x] if solid[ym, x] else f[2, ym, x]
            fi[3] = f[1, y, x] if solid[y, xp] else f[3, y, xp]
            fi[4] = f[2, y, x] if solid[yp, x] else f[4, yp, x]
            fi[5] = f[7, y, x] if solid[ym, xm] else f[5, ym, xm]
            fi[6] = f[8, y, x] if solid[ym, xp] else f[6, ym, xp]
            fi[7] = f[5, y, x] if solid[yp, xp] else f[7, yp, xp]
            fi[8] = f[6, y, x] if solid[yp, xm] else f[8, yp, xm]
            rho = 0.0
            mx = 0.0
            my = 0.0
            for i in range(9):
                rho += fi[i]
                mx += fi[i] * CX[i]
                my += fi[i] * CY[i]
            ux = mx / rho + 0.5 * gx
            uy = my / rho + 0.5 * gy
            usq = ux * ux + uy * uy
            ug = ux * gx + uy * gy
            if do_acc:
                pxx = 0.0
                pxy = 0.0
                pyy = 0.0
                for i in range(9):
                    cu = CX[i] * ux + CY[i] * uy
                    fneq = fi[i] - WT[i] * rho * (1.0 + 3.0 * cu + 4.5 * cu * cu - 1.5 * usq)
                    pxx += CX[i] * CX[i] * fneq
                    pxy += CX[i] * CY[i] * fneq
                    pyy += CY[i] * CY[i] * fneq
                c = -1.5 * omp / rho
                sxx = c * (pxx + rho * ux * gx)
                syy = c * (pyy + rho * uy * gy)
                sxy = c * (pxy + 0.5 * rho * (ux * gy + uy * gx))
                ss = sxx * sxx + syy * syy + 2.0 * sxy * sxy
                su += ux
                sv += uy
                ske += 0.5 * rho * usq
                sphi += 2.0 * rho * nu * ss
                acc[0, y, x] += ux
                acc[1, y, x] += uy
                acc[2, y, x] += usq
                acc[3, y, x] += sxx
                acc[4, y, x] += sxy
                acc[5, y, x] += syy
                acc[6, y, x] += ss
            # collide (two relaxation times) with the force term split into its even and odd parts
            for i in range(9):
                j = OPP[i]
                if j < i:
                    continue
                cu = CX[i] * ux + CY[i] * uy
                cg = CX[i] * gx + CY[i] * gy
                feq_e = WT[i] * rho * (1.0 + 4.5 * cu * cu - 1.5 * usq)
                feq_o = WT[i] * rho * 3.0 * cu
                s_e = (1.0 - 0.5 * omp) * WT[i] * rho * (9.0 * cu * cg - 3.0 * ug)
                s_o = (1.0 - 0.5 * omm) * WT[i] * rho * 3.0 * cg
                if j == i:
                    fn[i, y, x] = fi[i] - omp * (fi[i] - feq_e) + s_e
                else:
                    fe = 0.5 * (fi[i] + fi[j])
                    fo = 0.5 * (fi[i] - fi[j])
                    de = -omp * (fe - feq_e) + s_e
                    do = -omm * (fo - feq_o) + s_o
                    fn[i, y, x] = fi[i] + de + do
                    fn[j, y, x] = fi[j] + de - do
    return su, sv, ske, sphi


def advance(f, fn, solid, nu, gx, gy, nsteps, acc=None):
    """nsteps steps; the last one increments acc (when given) and returns the cell means (U, V, kinetic energy, dissipation).
    Returns (f, fn, sample) with f holding the current state."""
    omp, omm = rates(nu)
    dummy = acc if acc is not None else np.zeros((7, 1, 1))
    out = None
    for k in range(nsteps):
        last = (k == nsteps - 1) and acc is not None
        s = _step(f, fn, solid, omp, omm, gx, gy, dummy, last)
        f, fn = fn, f
        if last:
            n = solid.size
            out = (s[0] / n, s[1] / n, s[2] / n, s[3] / n)
    return f, fn, out


def init(solid, rho0=1.0):
    ny, nx = solid.shape
    f = np.empty((9, ny, nx))
    for i in range(9):
        f[i] = WT[i] * rho0
    return f, f.copy()


@njit(cache=True)
def diff_norm(f, f2, solid):
    s = 0.0
    ny, nx = solid.shape
    for i in range(9):
        for y in range(ny):
            for x in range(nx):
                if not solid[y, x]:
                    d = f2[i, y, x] - f[i, y, x]
                    s += d * d
    return np.sqrt(s)


def disks_mask(nx, ny, centres, radius):
    """solid mask of periodic disks; centres in lattice units (x, y)."""
    yy, xx = np.meshgrid(np.arange(ny) + 0.0, np.arange(nx) + 0.0, indexing='ij')
    solid = np.zeros((ny, nx), dtype=np.bool_)
    for cx, cy in centres:
        dx = np.abs(xx - cx); dx = np.minimum(dx, nx - dx)
        dy = np.abs(yy - cy); dy = np.minimum(dy, ny - dy)
        solid |= dx * dx + dy * dy < radius * radius
    return solid


def random_disks(nx, ny, n, radius, gap, rng, max_try=200000):
    """random sequential addition of n periodic disks with a minimum surface-to-surface gap."""
    pts = []
    dmin2 = (2 * radius + gap) ** 2
    tries = 0
    while len(pts) < n:
        tries += 1
        if tries > max_try:
            raise RuntimeError('random sequential addition failed')
        p = rng.random(2) * (nx, ny)
        ok = True
        for q in pts:
            dx = abs(p[0] - q[0]); dx = min(dx, nx - dx)
            dy = abs(p[1] - q[1]); dy = min(dy, ny - dy)
            if dx * dx + dy * dy < dmin2:
                ok = False
                break
        if ok:
            pts.append(p)
    return np.array(pts)
