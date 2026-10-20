"""Functional tensor trains and the squared inverse Rosenblatt transport (SIRT), written from scratch.

* tt_cross: two-site (DMRG-type) cross approximation of a function given on a tensor grid, with maxvol
  pivoting and SVD rank truncation (Oseledets & Tyrtyshnikov 2010; Savostyanov & Oseledets 2011).
* SIRT: the square of the piecewise-linear interpolant of the TT, plus a small defensive product density,
  defines an approximate density p~ with exactly computable marginals of every leading block of variables
  (Cui & Dolgov 2022). Its triangular (Knothe-Rosenblatt) structure gives the conditional densities
  p~(x_k | x_<k) and sampling by inverse conditional distribution functions.
"""
import numpy as np
import scipy.linalg as sla


# ---------------------------------------------------------------- linear algebra
def maxvol(A, tol=1.02, maxit=500):
    """Rows of a tall matrix A (N x r) whose r x r submatrix has (locally) maximal volume."""
    N, r = A.shape
    if N <= r:
        return np.arange(N)
    _, _, piv = sla.qr(A.T, mode='economic', pivoting=True)
    piv = piv[:r].copy()
    Bm = np.linalg.solve(A[piv].T, A.T).T          # A @ inv(A[piv])
    for _ in range(maxit):
        i, j = np.unravel_index(np.argmax(np.abs(Bm)), Bm.shape)
        if abs(Bm[i, j]) <= tol:
            break
        piv[j] = i
        row = Bm[i, :].copy(); row[j] -= 1.0
        Bm -= np.outer(Bm[:, j], row / Bm[i, j])
    return piv


def rsvd(M, k, rng, p=12, q=2):
    """Truncated SVD (full SVD for small matrices, randomized range finder otherwise)."""
    m, n = M.shape
    if min(m, n) <= k + p + 10:
        return np.linalg.svd(M, full_matrices=False)
    Y = M @ rng.standard_normal((n, k + p))
    for _ in range(q):
        Y, _ = np.linalg.qr(Y)
        Y = M @ (M.T @ Y)
    Qm, _ = np.linalg.qr(Y)
    Ub, s, Vt = np.linalg.svd(Qm.T @ M, full_matrices=False)
    return Qm @ Ub, s, Vt


def choose_rank(s, fro, tol, rmax):
    tail2 = fro ** 2 - np.cumsum(s ** 2)                 # energy left after keeping 1, 2, ... values
    ok = np.nonzero(tail2 <= (tol * fro) ** 2)[0]
    r = (ok[0] + 1) if len(ok) else len(s)
    return int(max(1, min(r, rmax, len(s))))


# ---------------------------------------------------------------- cross approximation
def _superblock(f, Lk, Rk2, k, n, chunk=3_000_000):
    d = len(n); rk, rk2 = Lk.shape[0], Rk2.shape[0]; nk, nk1 = n[k], n[k + 1]
    out = np.empty((rk, nk, nk1, rk2))
    per = max(1, chunk // (nk * nk1 * rk2))
    for a0 in range(0, rk, per):
        a = slice(a0, min(rk, a0 + per)); ra = a.stop - a.start
        ind = []
        for m in range(d):
            if m < k:
                ind.append(Lk[a, m][:, None, None, None])
            elif m == k:
                ind.append(np.arange(nk)[None, :, None, None])
            elif m == k + 1:
                ind.append(np.arange(nk1)[None, None, :, None])
            else:
                ind.append(Rk2[:, m - k - 2][None, None, None, :])
        out[a] = np.broadcast_to(f(ind), (ra, nk, nk1, rk2))
    return out.reshape(rk * nk, nk1 * rk2)


def tt_eval_idx(cores, idx):
    """Values of a TT at integer multi-indices idx (m x d)."""
    v = cores[0][0, idx[:, 0], :]
    for k in range(1, len(cores)):
        v = np.einsum('mr,rms->ms', v, cores[k][:, idx[:, k], :])
    return v[:, 0]


def tt_cross(f, n, rmax, init, tol=1e-6, nswp=6, rinit=12, seed=0, val=None, val_tol=1e-3, log=print, counter=None):
    """Two-site cross approximation of the tensor f on the grid n.

    f(ind) takes a list of d broadcastable integer index arrays and returns the tensor entries.
    init: integer multi-indices (m x d) of points where f is large (e.g. samples), used for the first
    right index sets. val: (idx, values) to monitor the relative error. counter(ind) is called with every
    requested block of indices (for counting model runs)."""
    rng = np.random.default_rng(seed)
    d = len(n)
    Lset = [None] * (d + 1); Rset = [None] * (d + 1)
    Lset[0] = np.zeros((1, 0), int); Rset[d] = np.zeros((1, 0), int)
    for k in range(d - 1, 0, -1):
        cand = np.unique(init[:, k:], axis=0)
        Rset[k] = cand[rng.choice(len(cand), size=min(rinit, len(cand)), replace=False)]
    cores = [None] * d
    hist = []
    g = (lambda ind: (counter(ind), f(ind))[1]) if counter else f
    for swp in range(nswp):
        for k in range(d - 1):                                   # left to right
            Mb = _superblock(g, Lset[k], Rset[k + 2], k, n)
            U, s, Vt = rsvd(Mb, rmax, rng)
            r = choose_rank(s, np.linalg.norm(Mb), tol, rmax)
            Ur = U[:, :r]
            piv = maxvol(Ur)
            a, i = np.divmod(piv, n[k])
            Lset[k + 1] = np.hstack([Lset[k][a], i[:, None]])
            cores[k] = np.linalg.solve(Ur[piv].T, Ur.T).T.reshape(Lset[k].shape[0], n[k], r)
            if k == d - 2:
                cores[d - 1] = ((Ur[piv] * s[:r]) @ Vt[:r]).reshape(r, n[d - 1], 1)
        for k in range(d - 2, -1, -1):                           # right to left
            Mb = _superblock(g, Lset[k], Rset[k + 2], k, n)
            U, s, Vt = rsvd(Mb, rmax, rng)
            r = choose_rank(s, np.linalg.norm(Mb), tol, rmax)
            Vr = Vt[:r].T
            piv = maxvol(Vr)
            j, b = np.divmod(piv, Rset[k + 2].shape[0])
            Rset[k + 1] = np.hstack([j[:, None], Rset[k + 2][b]])
            cores[k + 1] = np.linalg.solve(Vr[piv].T, Vr.T).reshape(r, n[k + 1], Rset[k + 2].shape[0])
            if k == 0:
                cores[0] = ((U[:, :r] * s[:r]) @ Vr[piv].T).reshape(1, n[0], r)
        ranks = [c.shape[2] for c in cores[:-1]]
        err = np.nan
        if val is not None:
            vi, vv = val
            err = float(np.linalg.norm(tt_eval_idx(cores, vi) - vv) / np.linalg.norm(vv))
        hist.append(dict(sweep=swp + 1, ranks=ranks, err=err))
        log(f'  sweep {swp + 1}: ranks {ranks}  validation error {err:.2e}')
        if val is not None and err < val_tol and swp >= 1:
            break
    return cores, hist


# ---------------------------------------------------------------- squared inverse Rosenblatt transport
class ProductDensity:
    """Defensive product density: list of (logpdf, sampler) per dimension."""
    def __init__(self, comps):
        self.comps = comps

    def logpdf_lead(self, X):
        out = np.zeros(X.shape[0])
        for j in range(X.shape[1]):
            out += self.comps[j][0](X[:, j])
        return out


class SIRT:
    """p~(x) = ( g~(x)^2 1_box(x) + tau * lam(x) ) / (Z + tau), g~ = piecewise-linear interpolant of a TT."""

    def __init__(self, cores, grids, lam, tau_rel=1e-3):
        self.G = cores; self.X = [np.asarray(g, float) for g in grids]; self.d = len(cores)
        self.h = [g[1] - g[0] for g in self.X]
        P = [None] * (self.d + 1); P[self.d] = np.ones((1, 1))
        for k in range(self.d - 1, -1, -1):
            Gk = self.G[k]; h = self.h[k]; nk = Gk.shape[1]
            md = np.full(nk, 2 * h / 3); md[0] = md[-1] = h / 3
            T = np.einsum('aib,bc->aic', Gk, P[k + 1])
            Pk = np.einsum('aic,dic,i->ad', T, Gk, md)
            Xo = np.einsum('aic,dic->ad', T[:, :-1], Gk[:, 1:]) * (h / 6)
            P[k] = Pk + Xo + Xo.T
        self.P = P
        self.Z = float(P[0][0, 0])
        self.tau = tau_rel * self.Z
        self.lam = lam

    def _locate(self, j, x):
        g = self.X[j]; u = (x - g[0]) / self.h[j]
        inside = (u >= -1e-12) & (u <= len(g) - 1 + 1e-12)
        i = np.clip(np.floor(u).astype(int), 0, len(g) - 2); t = np.clip(u - i, 0.0, 1.0)
        return i, t, inside

    def left(self, X):
        """Left TT products of the leading block X (m x k) and the inside-box mask."""
        m, k = X.shape
        v = np.ones((m, 1)); inside = np.ones(m, bool)
        for j in range(k):
            i, t, ins = self._locate(j, X[:, j]); inside &= ins
            Gj = self.G[j]
            v = (1 - t)[:, None] * np.einsum('mr,rms->ms', v, Gj[:, i, :]) + t[:, None] * np.einsum('mr,rms->ms', v, Gj[:, i + 1, :])
        return v, inside

    def log_marginal(self, X, chunk=4000):
        """log p~ of the leading block X (m x k), k = 1..d."""
        m, k = X.shape
        out = np.empty(m)
        for c0 in range(0, m, chunk):
            Xc = X[c0:c0 + chunk]
            v, ins = self.left(Xc)
            A = np.einsum('mr,rs,ms->m', v, self.P[k], v) * ins
            out[c0:c0 + chunk] = np.log(np.maximum(A, 0.0) + self.tau * np.exp(self.lam.logpdf_lead(Xc)))
        return out - np.log(self.Z + self.tau)

    def sample_rest(self, X, rng, chunk=4000, tt_only=False):
        """Sample the remaining variables given the leading block X (m x k) from p~(x_rest | x_lead)
        (tt_only: from the tensor-train part alone, without the defensive component)."""
        m, k0 = X.shape
        out = np.empty((m, self.d)); out[:, :k0] = X
        for c0 in range(0, m, chunk):
            Y = out[c0:c0 + chunk]
            v, ins = self.left(Y[:, :k0])
            for k in range(k0, self.d):
                A_lead = np.einsum('mr,rs,ms->m', v, self.P[k], v) * ins
                lam_lead = self.tau * np.exp(self.lam.logpdf_lead(Y[:, :k]))
                use_tt = (A_lead > 0) if tt_only else (rng.random(len(Y)) < A_lead / (A_lead + lam_lead))
                # TT part: nodal row vectors a_j = v G_k[:, j, :]
                a = np.einsum('mr,rjs->mjs', v, self.G[k])
                Pa = np.einsum('mjs,st->mjt', a, self.P[k + 1])
                Aj = np.einsum('mjt,mjt->mj', Pa, a)
                Bj = np.einsum('mjt,mjt->mj', Pa[:, :-1], a[:, 1:])
                h = self.h[k]
                cm = np.maximum(h * (Aj[:, :-1] + Bj + Aj[:, 1:]) / 3.0, 0.0)
                cum = np.cumsum(cm, axis=1); tot = cum[:, -1:]
                u = rng.random((len(Y), 1)) * tot
                j = np.minimum((cum < u).sum(1), cm.shape[1] - 1)
                rr = np.arange(len(Y))
                prev = np.where(j > 0, cum[rr, j - 1], 0.0)
                target = (u[:, 0] - prev) / h
                A0, B0, C0 = Aj[rr, j], Bj[rr, j], Aj[rr, j + 1]
                t = np.full(len(Y), 0.5); lo = np.zeros(len(Y)); hi = np.ones(len(Y))
                for _ in range(40):                           # safeguarded Newton on the cubic CDF
                    F = A0 * (t - t ** 2 + t ** 3 / 3) + B0 * (t ** 2 - 2 * t ** 3 / 3) + C0 * t ** 3 / 3 - target
                    dF = A0 * (1 - t) ** 2 + 2 * B0 * t * (1 - t) + C0 * t ** 2
                    lo = np.where(F < 0, t, lo); hi = np.where(F >= 0, t, hi)
                    tn = t - F / np.maximum(dF, 1e-300)
                    t = np.where((tn > lo) & (tn < hi), tn, 0.5 * (lo + hi))
                x_tt = self.X[k][0] + h * (j + t)
                x_def = self.lam.comps[k][1](len(Y), rng)
                xk = np.where(use_tt, x_tt, x_def)
                Y[:, k] = xk
                i, tt_, insk = self._locate(k, xk); ins &= insk
                Gk = self.G[k]
                v = (1 - tt_)[:, None] * np.einsum('mr,rms->ms', v, Gk[:, i, :]) + tt_[:, None] * np.einsum('mr,rms->ms', v, Gk[:, i + 1, :])
            out[c0:c0 + chunk] = Y
        return out
