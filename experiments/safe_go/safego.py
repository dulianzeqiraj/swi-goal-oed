"""SAFE-GO prototype: Bayes vs SafeBayes (learning rate eta) for the toe of the saltwater
interface from potential observations along the coast-well axis (Strack 1976), with a
polynomial (Legendre) regression model of unknown degree and homoscedastic Gaussian noise.
Misspecification as in Grunwald & van Ommen (2017): exact 'easy' readings at the coast (x=0, Phi=0).
"""
import numpy as np
from numpy.polynomial import legendre as L
from scipy.special import gammaln, digamma

D = 2000.0          # well distance from coast [m]
PHI_TOE = 0.025 * 30.0**2 / 2   # delta*B^2/2 = 11.25 m^2
Q = 2600.0          # pumping [m3/d]
P = 12              # max polynomial degree
XG = np.linspace(0.0, 0.95, 600)   # grid in X = x/D for the goal
ETAS = 2.0 ** (-np.arange(0, 13) / 2.0)   # 1 ... 1/64

def basis(X, P=P):
    return L.legvander(2.0 * np.asarray(X) - 1.0, P)   # (n, P+1)

BG = basis(XG)

def phi_true(X, K, q0, Q=Q):
    x = X * D
    return (q0 / K) * x + Q / (2 * np.pi * K) * np.log((D - x) / (D + x))

def first_root(phig):
    """first X on XG where phi crosses PHI_TOE from below; NaN-> 0.95 (no toe before 0.95)"""
    above = phig >= PHI_TOE
    idx = np.argmax(above, axis=-1)
    has = above.any(axis=-1)
    i0 = np.clip(idx - 1, 0, len(XG) - 1)
    f0 = np.take_along_axis(phig, i0[..., None], -1)[..., 0]
    f1 = np.take_along_axis(phig, idx[..., None], -1)[..., 0]
    w = np.where(f1 != f0, (PHI_TOE - f0) / (f1 - f0 + 1e-300), 0.0)
    xr = XG[i0] + np.clip(w, 0, 1) * (XG[idx] - XG[i0])
    xr = np.where(idx == 0, XG[0], xr)
    return np.where(has, xr, XG[-1])

class NIG:
    """Conjugate normal-inverse-gamma prior beta|s2 ~ N(0, s2 v I), s2 ~ IG(a0, b0)."""
    def __init__(self, v=100.0, a0=1.0, b0=1.0):
        self.v, self.a0, self.b0 = v, a0, b0

    def post(self, S, r, yy, n, eta):
        """eta-posterior for all nested models from sufficient stats S=X'X, r=X'y, yy=y'y.
        Returns per-model arrays: logev (generalized evidence), z (L^-1 b), Linv, an, bn."""
        k = S.shape[0]
        Lam = np.eye(k) / self.v + eta * S
        Lc = np.linalg.cholesky(Lam)
        Linv = np.linalg.inv(Lc)
        z = Linv @ (eta * r)
        quad = np.cumsum(z ** 2)                     # m' Lam m for model p
        logdet = 2 * np.cumsum(np.log(np.diag(Lc)))  # log|Lam_p|
        pdim = np.arange(1, k + 1)
        an = self.a0 + eta * n / 2.0
        bn = self.b0 + 0.5 * (eta * yy - quad)
        bn = np.maximum(bn, 1e-12)
        logev = (-eta * n / 2.0 * np.log(2 * np.pi) - 0.5 * pdim * np.log(self.v) - 0.5 * logdet
                 + self.a0 * np.log(self.b0) + gammaln(an) - gammaln(self.a0) - an * np.log(bn))
        return logev, z, Linv, an, bn

def model_weights(logev):
    lw = logev - logev.max()
    w = np.exp(lw)
    return w / w.sum()

def exp_logloss(x, y, z, Linv, an, bn, w):
    """posterior-expected log loss of (x,y) under the BMA eta-posterior (randomized, R-log)"""
    u = Linv @ x
    mean = np.cumsum(u * z)          # x' m_p
    var_b = np.cumsum(u ** 2)        # x' Lam_p^-1 x  (times s2)
    El = 0.5 * np.log(2 * np.pi) + 0.5 * (np.log(bn) - digamma(an)) + 0.5 * ((an / bn) * (y - mean) ** 2 + var_b)
    return np.sum(w * El)

def safebayes_eta(Xb, y, prior, rng, etas=ETAS, start=1, nperm=1):
    """R-log SafeBayes: eta minimising the cumulative posterior-expected log loss of each point given
    the points before it. start: first point whose loss is counted; nperm: random orders averaged."""
    n, k = Xb.shape
    cum = np.zeros(len(etas))
    for _ in range(nperm):
        perm = rng.permutation(n)
        Xp, yp = Xb[perm], y[perm]
        for j, eta in enumerate(etas):
            S = np.zeros((k, k)); r = np.zeros(k); yy = 0.0
            for i in range(n):
                if i >= start:
                    logev, z, Linv, an, bn = prior.post(S, r, yy, i, eta)
                    cum[j] += exp_logloss(Xp[i], yp[i], z, Linv, an, bn, model_weights(logev))
                S += np.outer(Xp[i], Xp[i]); r += Xp[i] * yp[i]; yy += yp[i] ** 2
    cum /= nperm
    return etas[np.argmin(cum)], cum

def sample_goal(Xb, y, prior, eta, rng, ns=1000, wts=None):
    n, k = Xb.shape
    wv = np.ones(n) if wts is None else wts
    S, r, yy = (Xb * wv[:, None]).T @ Xb, Xb.T @ (wv * y), y @ (wv * y)
    logev, z, Linv, an, bn = prior.post(S, r, yy, n, eta)
    if wts is not None:   # known precisions: log-likelihood gains 0.5*sum(log w), same for all models
        logev = logev + 0.5 * eta * np.sum(np.log(wv))
    w = model_weights(logev)
    ps = rng.choice(k, size=ns, p=w)
    s2 = bn[ps] / rng.gamma(an, 1.0, size=ns)
    phig = np.empty((ns, len(XG)))
    for p in np.unique(ps):
        sel = np.where(ps == p)[0]
        Lp = np.linalg.inv(Linv[:p + 1, :p + 1])        # chol factor of Lam_p
        mp = np.linalg.solve(Lp.T, z[:p + 1])           # m_p = L_p^-T z_p
        eps = rng.standard_normal((len(sel), p + 1))
        beta = mp + np.sqrt(s2[sel])[:, None] * np.linalg.solve(Lp.T, eps.T).T
        phig[sel] = beta @ BG[:, :p + 1].T
    toe = first_root(phig)
    return toe, w, (bn / (an - 1.0 + 1e-12)), ps
