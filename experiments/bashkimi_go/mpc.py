"""Two-party computation of the BASHKIMI-GO merge value on secret shares (simulation).

Each party holds an additive share of every intermediate value in the ring Z_2^64 (fixed point, F fractional
bits). The candidate secret-shares its weighted Gram matrix G (computed locally from its own records); the host
secret-shares the Cholesky factor L0 of its posterior covariance, the target directions W = L0' C' and its
target means and variances. Neither party ever sees the other's inputs or any intermediate value; only the
final value is opened, to the host.
  * additions and multiplications by public constants are local;
  * products of shared values use Beaver triples from a dealer (the parties open X - A and Y - B, which are uniform);
  * truncation after a product and the comparisons (clamp, min) are dealer-assisted ideal functionalities, as in
    CrypTen's trusted-third-party mode; they are simulated by reconstruct-and-reshare and counted;
  * (I + L0' G L0)^-1 by Newton-Schulz iterations, 1/sqrt by Newton iterations started from host-known bounds,
    psi(z) = phi(z) + z Phi(z) by a Chebyshev series on [-8, 8] evaluated by Clenshaw's recurrence.
Communication is counted as the bytes both parties send when they open masked values (8 bytes per ring element).
"""
import numpy as np
from scipy.special import ndtr

F = 20
SCALE = float(1 << F)
MASK = np.uint64(0xFFFFFFFFFFFFFFFF)


class Stats:
    def __init__(self):
        self.bytes = 0; self.mults = 0; self.rounds = 0; self.trunc = 0; self.cmp = 0


ST = Stats()
_rng = np.random.default_rng(12345)


def _rand(shape):
    return _rng.integers(0, 2 ** 63, size=shape, dtype=np.uint64) * np.uint64(2) + _rng.integers(0, 2, size=shape, dtype=np.uint64)


def encode(x):
    return np.asarray(np.round(np.asarray(x, float) * SCALE)).astype(np.int64).view(np.uint64)


def decode(u):
    return np.asarray(u).view(np.int64).astype(float) / SCALE


class Sh:
    """additive sharing: value = s0 + s1 (mod 2^64)."""
    def __init__(self, s0, s1):
        self.s0, self.s1 = s0, s1

    @staticmethod
    def share(x):
        v = encode(x); r = _rand(v.shape)
        return Sh(r, v - r)

    @staticmethod
    def share_raw(v):
        r = _rand(v.shape)
        return Sh(r, v - r)

    def reveal(self):
        return decode(self.s0 + self.s1)

    def raw(self):
        return self.s0 + self.s1

    @property
    def shape(self):
        return self.s0.shape

    def __add__(self, o):
        if isinstance(o, Sh):
            return Sh(self.s0 + o.s0, self.s1 + o.s1)
        return Sh(self.s0 + encode(o), self.s1.copy())          # public constant added by party 0

    def __sub__(self, o):
        if isinstance(o, Sh):
            return Sh(self.s0 - o.s0, self.s1 - o.s1)
        return Sh(self.s0 - encode(o), self.s1.copy())

    def __neg__(self):
        return Sh(np.uint64(0) - self.s0, np.uint64(0) - self.s1)

    def __getitem__(self, idx):
        return Sh(self.s0[idx], self.s1[idx])

    @property
    def T(self):
        return Sh(self.s0.T, self.s1.T)


def rsub(c, x):
    """public constant minus shared value."""
    return (-x) + c


def trunc(x):
    """dealer-assisted exact truncation by F bits (ideal functionality)."""
    ST.trunc += 1; ST.rounds += 1; ST.bytes += 2 * 8 * x.s0.size
    v = x.raw().view(np.int64)
    v = (v + (1 << (F - 1))) >> F
    return Sh.share_raw(v.view(np.uint64))


def mulc(x, c):
    """multiply by a public real constant (array broadcastable)."""
    cc = encode(c)
    return trunc(Sh(x.s0 * cc, x.s1 * cc))


def _beaver(x, y, op):
    A = _rand(x.shape); Bm = _rand(y.shape); C = op(A, Bm)
    Ash, Bsh, Csh = Sh.share_raw(A), Sh.share_raw(Bm), Sh.share_raw(C)
    E = (x.s0 - Ash.s0) + (x.s1 - Ash.s1)          # opened
    Fm = (y.s0 - Bsh.s0) + (y.s1 - Bsh.s1)         # opened
    ST.mults += 1; ST.rounds += 1; ST.bytes += 2 * 8 * (E.size + Fm.size)
    z0 = Csh.s0 + op(E, Bsh.s0) + op(Ash.s0, Fm) + op(E, Fm)
    z1 = Csh.s1 + op(E, Bsh.s1) + op(Ash.s1, Fm)
    return trunc(Sh(z0, z1))


def mul(x, y):
    return _beaver(x, y, lambda a, b: a * b)


def matmul(x, y):
    return _beaver(x, y, lambda a, b: a @ b)


def clamp(x, lo, hi):
    """ideal secure comparison (bit-decomposition protocols in practice)."""
    ST.cmp += 1; ST.rounds += 6; ST.bytes += 2 * 8 * 64 * x.s0.size // 8
    return Sh.share(np.clip(x.reveal(), lo, hi))


def minimum_c(x, c):
    ST.cmp += 1; ST.rounds += 6; ST.bytes += 2 * 8 * 64 * x.s0.size // 8
    return Sh.share(np.minimum(x.reveal(), c))


def invsqrt(v, y0, iters=30):
    """Newton for 1/sqrt(v) from below (y0 <= 1/sqrt(v), host-known): y <- y (3 - v y^2) / 2."""
    y = y0
    for _ in range(iters):
        y = mulc(mul(y, rsub(3.0, mul(v, mul(y, y)))), 0.5)
    return y


# Chebyshev series of psi(z) = phi(z) + z Phi(z) on [-8, 8]
ZMAX = 8.0
_NCH = 64
_xk = np.cos(np.pi * (np.arange(_NCH) + 0.5) / _NCH)
_f = lambda z: np.exp(-0.5 * z * z) / np.sqrt(2 * np.pi) + z * ndtr(z)
_fx = _f(ZMAX * _xk)
CHEB = np.array([2.0 / _NCH * np.sum(_fx * np.cos(np.pi * j * (np.arange(_NCH) + 0.5) / _NCH)) for j in range(_NCH)])
CHEB[0] /= 2
CHEB = CHEB[:np.flatnonzero(np.abs(CHEB) > 1e-8).max() + 1]      # drop the negligible tail only


def psi_cheb(z):
    """Clenshaw recurrence on shares; z already clamped to [-ZMAX, ZMAX].
    b_j = c_j + 2 x b_(j+1) - b_(j+2), f = c_0 + x b_1 - b_2."""
    x = mulc(z, 1.0 / ZMAX)
    n = len(CHEB) - 1
    b1 = Sh.share(np.full(x.shape, CHEB[n])); b2 = Sh.share(np.zeros(x.shape))
    for j in range(n - 1, 0, -1):
        b = (mulc(mul(x, b1), 2.0) - b2) + CHEB[j]
        b2, b1 = b1, b
    return (mul(x, b1) - b2) + CHEB[0]


def value_mpc(G, L0, W, m0, v0, vn, ghx, ghw, t_tol, l_sal, c_cap, c_pub, ns_iters=None):
    """BASHKIMI-GO value of one merge on shares. G: candidate's input; L0, W, m0, v0, vn: host's inputs.
    c_pub >= 1 + lambda_max(L0' G L0) is public. Returns the opened value and the per-target values."""
    p = G.shape[0]
    Gs, Ls, Ws = Sh.share(G), Sh.share(L0), Sh.share(W)
    H = matmul(matmul(Ls.T, Gs), Ls)                       # whitened information
    N = mulc(H + np.eye(p), 1.0 / c_pub)                  # eigenvalues in (0, 1]
    X = Sh.share(np.eye(p))
    k = ns_iters or int(np.ceil(np.log2(c_pub))) + 6
    for _ in range(k):                                    # Newton-Schulz: X <- X (2I - N X)
        X = matmul(X, rsub(2.0 * np.eye(p), matmul(N, X)))
    Y = matmul(mulc(X, 1.0 / c_pub), Ws)                  # M^-1 W
    WY = mul(Ws, Y)
    v1 = Sh(np.sum(WY.s0, 0), np.sum(WY.s1, 0))           # column sums: w_j' M^-1 w_j
    s2 = clamp(rsub(v0, v1), 0.0, None)                   # preposterior variance of the target means
    s2e = s2 + 1e-6 * v0
    s = mul(s2e, invsqrt(s2e, Sh.share(1.0 / np.sqrt(v0 + 1e-6 * v0))))
    vv = v1 + vn
    isd = invsqrt(vv, Sh.share(1.0 / np.sqrt(v0 + vn)))
    sd = mul(vv, isd)
    J, K = len(m0), len(ghx)
    S2 = Sh(np.repeat(s.s0[:, None], K, 1), np.repeat(s.s1[:, None], K, 1))
    mu = mulc(S2, np.broadcast_to(ghx[None], (J, K))) + np.broadcast_to(m0[:, None], (J, K))
    ISD = Sh(np.repeat(isd.s0[:, None], K, 1), np.repeat(isd.s1[:, None], K, 1))
    SD = Sh(np.repeat(sd.s0[:, None], K, 1), np.repeat(sd.s1[:, None], K, 1))
    z = clamp(mul(mu - t_tol, ISD), -ZMAX, ZMAX)
    r = minimum_c(mulc(mul(SD, psi_cheb(z)), l_sal), c_cap)
    er = mulc(r, np.broadcast_to(ghw[None], (J, K)))
    er = Sh(np.sum(er.s0, 1), np.sum(er.s1, 1))
    sd0 = np.sqrt(v0 + vn)
    r0 = np.minimum(c_cap, l_sal * sd0 * _f((m0 - t_tol) / sd0))   # host computes its own term in the clear
    vj = rsub(r0, er)
    tot = Sh(np.sum(vj.s0)[None], np.sum(vj.s1)[None])
    return float(tot.reveal()[0]), vj.reveal()
