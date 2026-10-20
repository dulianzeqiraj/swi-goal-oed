"""Grids, the joint density and helpers shared by the DARA-GO scripts.

Variables, in the order of the map: x = (xi, y, q, z1, z2, z3): design, data, goal, parameters.
Joint density: p(xi, y, q, z) = U(xi) N(y; h(xi, z), SIG^2) N(q; Q(z), TAU^2) prod phi(z_i).
"""
import numpy as np
import dara_model as M
from dara_tt import ProductDensity

XI = np.arange(100.0, 4900.0 + 1, 100.0)                      # design nodes (49)
YG = np.linspace(-4 * M.SIG, M.HL + 4 * M.SIG, int(round((M.HL + 8 * M.SIG) / (M.SIG / 2))) + 1)
Q_LO, Q_HI = 4.26, 8.78                                       # prior 1e-5 quantiles of the goal +- 4 TAU
QG = np.linspace(Q_LO, Q_HI, int(round((Q_HI - Q_LO) / (M.TAU / 2))) + 1)
ZG = np.linspace(-4.0, 4.0, 49)
GRIDS = [XI, YG, QG, ZG, ZG, ZG]
N = [len(g) for g in GRIDS]
GOAL_MEAN, GOAL_SD = 6.0, 0.5


def sqrt_joint_coords(xi, y, q, z1, z2, z3):
    h = M.head(xi, z1, z2, z3); Q = M.goal(z1, z2, z3)
    return np.exp(-(z1 ** 2 + z2 ** 2 + z3 ** 2) / 4 - (y - h) ** 2 / (4 * M.SIG ** 2) - (q - Q) ** 2 / (4 * M.TAU ** 2))


def f_index(ind):
    return sqrt_joint_coords(*(g[i] for g, i in zip(GRIDS, ind)))


def exact_samples(n, rng, xi=None):
    """Samples of the true joint; xi uniform on the design nodes unless given."""
    z = rng.standard_normal((n, 3))
    x = rng.choice(XI, n) if xi is None else np.full(n, float(xi))
    q = M.goal(*z.T) + M.TAU * rng.standard_normal(n)
    y = M.head(x, *z.T) + M.SIG * rng.standard_normal(n)
    return np.column_stack([x, y, q, z])


def snap(X):
    """Nearest grid indices (clipped to the box)."""
    return np.column_stack([np.clip(np.rint((X[:, j] - g[0]) / (g[1] - g[0])).astype(int), 0, len(g) - 1) for j, g in enumerate(GRIDS)])


def defensive():
    xa, xb = XI[0], XI[-1]
    ym, ys = M.HL / 2, M.HL / 2 + 2 * M.SIG
    norm = lambda m, s: (lambda x: -0.5 * ((x - m) / s) ** 2 - np.log(s * np.sqrt(2 * np.pi)),
                         lambda n, rng: m + s * rng.standard_normal(n))
    comps = [(lambda x: np.where((x >= xa) & (x <= xb), -np.log(xb - xa), -np.inf), lambda n, rng: rng.uniform(xa, xb, n)),
             norm(ym, ys), norm(GOAL_MEAN, 2 * GOAL_SD), norm(0.0, 1.0), norm(0.0, 1.0), norm(0.0, 1.0)]
    return ProductDensity(comps)


def log_prior_z(z):
    return -0.5 * np.sum(z ** 2, axis=1) - 1.5 * np.log(2 * np.pi)


def log_norm(x, m, s):
    return -0.5 * ((x - m) / s) ** 2 - np.log(s * np.sqrt(2 * np.pi))


# ---------------------------------------------------------------- affine (Gaussian Knothe-Rosenblatt) preconditioner
class Affine:
    """For every design node, v = (y, q, z1, z2, z3) = MU(xi) + LC(xi) w with LC the Cholesky factor of the prior
    covariance of v given xi: a lower-triangular (Knothe-Rosenblatt) Gaussian map. The tensor train is then built
    for the density of (xi, w), which is close to standard normal in w."""

    def __init__(self, nsamp=200000, seed=5, wlo=-6.0, whi=10.0, dw=0.2):
        rng = np.random.default_rng(seed)
        z = rng.standard_normal((nsamp, 3))
        q = M.goal(*z.T) + M.TAU * rng.standard_normal(nsamp)
        eps = M.SIG * rng.standard_normal(nsamp)
        self.MU = np.empty((len(XI), 5)); self.LC = np.empty((len(XI), 5, 5))
        for i, xi in enumerate(XI):
            V = np.column_stack([M.head(xi, *z.T) + eps, q, z])
            self.MU[i] = V.mean(0); self.LC[i] = np.linalg.cholesky(np.cov(V.T))
        self.logdiag = np.log(np.einsum('ijj->ij', self.LC))          # log L_jj per node
        self.WG = np.linspace(wlo, whi, int(round((whi - wlo) / dw)) + 1)
        self.grids = [XI] + [self.WG] * 5
        self.n = [len(g) for g in self.grids]

    def node(self, xi):
        i = np.rint((np.asarray(xi) - XI[0]) / (XI[1] - XI[0])).astype(int)
        return np.clip(i, 0, len(XI) - 1)

    def to_x(self, i0, W):
        """v = MU + LC w for node indices i0 (broadcastable) and W = list of 5 broadcastable arrays."""
        mu = self.MU[i0]; Lc = self.LC[i0]
        out = []
        for a in range(5):
            s = mu[..., a]
            for b in range(a + 1):
                s = s + Lc[..., a, b] * W[b]
            out.append(s)
        return out

    def to_w(self, X):
        """Leading-block coordinates: X (m x k) with columns (xi, y, q, z1, ...) -> (xi, w_1, ..., w_{k-1})."""
        i0 = self.node(X[:, 0]); k = X.shape[1]
        W = np.empty_like(X); W[:, 0] = X[:, 0]
        for a in range(k - 1):
            s = X[:, a + 1] - self.MU[i0, a]
            for b in range(a):
                s = s - self.LC[i0, a, b] * W[:, b + 1]
            W[:, a + 1] = s / self.LC[i0, a, a]
        return W, self.logdiag[i0, :k - 1].sum(1)

    def f_index(self, ind):
        i0 = ind[0]
        W = [self.WG[i] for i in ind[1:]]
        y, q, z1, z2, z3 = self.to_x(i0, W)
        xi = XI[i0]
        h = M.head(xi, z1, z2, z3); Q = M.goal(z1, z2, z3)
        return np.exp(-(z1 ** 2 + z2 ** 2 + z3 ** 2) / 4 - (y - h) ** 2 / (4 * M.SIG ** 2) - (q - Q) ** 2 / (4 * M.TAU ** 2)
                      + 0.5 * self.logdiag[i0].sum(-1))

    def snap(self, X):
        W, _ = self.to_w(X)
        cols = [self.node(X[:, 0])] + [np.clip(np.rint((W[:, j] - self.WG[0]) / (self.WG[1] - self.WG[0])).astype(int), 0, len(self.WG) - 1) for j in range(1, 6)]
        return np.column_stack(cols)


class EvalCounter:
    """Counts evaluations of the joint density requested by the cross approximation (one model run each)."""
    def __init__(self):
        self.evals = 0

    def __call__(self, ind):
        self.evals += int(np.prod(np.broadcast_shapes(*(np.shape(i) for i in ind))))
