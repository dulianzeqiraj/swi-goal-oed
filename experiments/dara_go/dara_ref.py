"""Exact reference values for DARA-GO by quadrature on fine grids.

For a scalar head y = h(xi; z) + eps and goal q = Q(z) + eta, the densities p(y | xi) and p(q, y | xi) are
expectations of Gaussian kernels over the prior of z. They are computed by linear (cloud-in-cell) binning of
many prior samples of (Q(z), h(xi; z)) on a fine grid followed by convolution with the exact Gaussian kernels;
the information follows by quadrature:
    I(z; y | xi)  = H(y | xi) - 0.5 log(2 pi e SIG^2),
    I(q; y | xi)  = int int p(q, y) log[ p(q, y) / (p(q) p(y)) ].
"""
import numpy as np
from scipy.signal import fftconvolve
import dara_model as M


def cic1(x, lo, d, n):
    """Linear binning weights of points x on the grid lo + d * k, k = 0..n-1 (returns counts / len(x))."""
    u = (x - lo) / d; i = np.floor(u).astype(int); w = u - i
    i = np.clip(i, 0, n - 2)
    c = np.bincount(i, 1 - w, minlength=n) + np.bincount(i + 1, w, minlength=n)
    return c[:n] / len(x)


def gauss_kernel(s, d):
    m = int(np.ceil(8 * s / d)); t = np.arange(-m, m + 1) * d
    k = np.exp(-0.5 * (t / s) ** 2); return k / k.sum()


class Reference:
    def __init__(self, n=4_000_000, seed=11):
        rng = np.random.default_rng(seed)
        self.z = M.prior_samples(n, rng)
        self.Q = M.goal(*self.z.T)
        # goal grid
        self.dq = M.TAU / 10; self.q0 = self.Q.min() - 8 * M.TAU
        self.nq = int(np.ceil((self.Q.max() + 8 * M.TAU - self.q0) / self.dq)) + 1
        self.qg = self.q0 + self.dq * np.arange(self.nq)
        pq = fftconvolve(cic1(self.Q, self.q0, self.dq, self.nq), gauss_kernel(M.TAU, self.dq), mode='same') / self.dq
        self.pq = np.maximum(pq, 1e-300)
        self.Hq = -np.sum(self.pq * np.log(self.pq)) * self.dq
        self.dy = M.SIG / 10; self.y0 = -8 * M.SIG
        self.ny = int(np.ceil((M.HL + 16 * M.SIG) / self.dy)) + 1
        self.yg = self.y0 + self.dy * np.arange(self.ny)

    def logpq(self, q):
        """Exact (quadrature) log density of the smoothed goal q_tau, by linear interpolation."""
        return np.log(np.interp(q, self.qg, self.pq, left=1e-300, right=1e-300))

    def info(self, xi):
        h = M.head(xi, *self.z.T)
        ky = gauss_kernel(M.SIG, self.dy)
        py = fftconvolve(cic1(h, self.y0, self.dy, self.ny), ky, mode='same') / self.dy
        py = np.maximum(py, 1e-300)
        Hy = -np.sum(py * np.log(py)) * self.dy
        eig = Hy - 0.5 * np.log(2 * np.pi * np.e * M.SIG ** 2)
        # joint (q, y)
        uq = (self.Q - self.q0) / self.dq; iq = np.clip(np.floor(uq).astype(int), 0, self.nq - 2); wq = uq - iq
        uy = (h - self.y0) / self.dy; iy = np.clip(np.floor(uy).astype(int), 0, self.ny - 2); wy = uy - iy
        H = np.zeros((self.nq, self.ny))
        for a, wa in ((0, 1 - wq), (1, wq)):
            for b, wb in ((0, 1 - wy), (1, wy)):
                np.add.at(H, (iq + a, iy + b), wa * wb)
        H /= len(h)
        kq = gauss_kernel(M.TAU, self.dq)
        P = fftconvolve(fftconvolve(H, kq[:, None], mode='same'), ky[None, :], mode='same') / (self.dq * self.dy)
        P = np.maximum(P, 1e-300)
        pq = P.sum(1) * self.dy; py2 = P.sum(0) * self.dq
        I_q = np.sum(P * (np.log(P) - np.log(pq)[:, None] - np.log(py2)[None, :])) * self.dq * self.dy
        return dict(eig=float(eig), info_goal=float(I_q), Hy=float(Hy))


if __name__ == '__main__':
    import time
    t0 = time.time(); R = Reference(); print(f'reference set {time.time()-t0:.1f}s  H(q)={R.Hq:.4f}')
    for xi in [200, 500, 800, 1000, 1200, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 4800]:
        r = R.info(xi); print(f'xi={xi:5d}  EIG={r["eig"]:.4f}  I(goal;y)={r["info_goal"]:.4f}')
    print(f'total {time.time()-t0:.1f}s')
