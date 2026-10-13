"""KRAMERS-GO: return period of noise-induced seawater intrusion at a pumping well.

Toe of the interface on the coast-well axis (Strack 1976; X = x_toe/d), relaxing toward the
instantaneous equilibrium, with a recharge factor r = exp(eps - s^2/2) (mean 1) that scales the
regional flow q0 and therefore mu and lam:
    dX/dt = (mu/r - F(X; lam/r)) / tau,      d eps = -eps/theta dt + s sqrt(2/theta) dW.
Escape = toe reaches the well (X >= 0.98). The pair (X, eps) is a non-gradient Markov process
(no detailed balance): its mean first-passage time T(X, eps) solves the backward Kolmogorov
equation   A(X,eps) T_X - (eps/theta) T_eps + (s^2/theta) T_eps,eps = -1,  T(X_esc, .) = 0.
Compared: direct simulation, the 2D Kolmogorov solution, a 1D white-noise reduction
(Stratonovich, multiplicative) and the small-noise Kramers rule T = 2pi/k exp(gap^2/(6 Var)).
"""
import json, sys, time
import numpy as np
from scipy.optimize import brentq
import scipy.sparse as sp
import scipy.sparse.linalg as spla

P0 = dict(K=100.0, q0=1.5, B=30.0, delta=0.025, d=2000.0, tau=2.0, s=0.20, theta=0.5)
XESC, XLO = 0.98, 0.15

def F(X, lam):
    return X + 0.5 * lam * np.log((1 - X) / (1 + X))

def Fp(X, lam):
    return 1 - lam / (1 - X ** 2)

def mu_of(P):
    return P['K'] * 0.5 * P['delta'] * P['B'] ** 2 / (P['q0'] * P['d'])

def lam_crit(mu):
    return brentq(lambda l: F(np.sqrt(1 - l), l) - mu, 1e-9, 1 - 1e-12)

def Qc_of(P):
    return lam_crit(mu_of(P)) * np.pi * P['q0'] * P['d']

def lam_of(P, Q):
    return Q / (np.pi * P['q0'] * P['d'])

def drift(X, eps, mu, lam, P):
    r = np.exp(eps - 0.5 * P['s'] ** 2)
    return (mu / r - F(X, lam / r)) / P['tau']

def stable(mu, lam):
    Xm = np.sqrt(1 - lam)
    if F(Xm, lam) <= mu:
        return None
    Xs = brentq(lambda X: F(X, lam) - mu, 1e-12, Xm)
    Xu = brentq(lambda X: F(X, lam) - mu, Xm, 1 - 1e-12)
    return Xs, Xu

def kolmogorov2d(mu, lam, P, nx=360, ne=121, emax=5.0):
    """MFPT T(X, eps) on a grid; upwind in X, upwind drift + central diffusion in eps."""
    s, th = P['s'], P['theta']
    x = np.linspace(XLO, XESC, nx); e = np.linspace(-emax * s, emax * s, ne)
    hx, he = x[1] - x[0], e[1] - e[0]
    N = nx * ne
    idx = lambda i, j: i * ne + j
    rows, cols, vals = [], [], []
    b = -np.ones(N)
    De = s * s / th
    for i in range(nx):
        if i == nx - 1:                       # absorbing at the well
            for j in range(ne):
                rows.append(idx(i, j)); cols.append(idx(i, j)); vals.append(1.0); b[idx(i, j)] = 0.0
            continue
        A = drift(x[i], e, mu, lam, P)
        for j in range(ne):
            k0 = idx(i, j); diag = 0.0
            a = A[j]
            if a > 0:
                rows += [k0]; cols += [idx(i + 1, j)]; vals += [a / hx]; diag -= a / hx
            elif i > 0:
                rows += [k0]; cols += [idx(i - 1, j)]; vals += [-a / hx]; diag += a / hx
            # (reflecting at XLO: no flux when a < 0 at i = 0)
            ve = -e[j] / th
            if ve > 0 and j < ne - 1:
                rows += [k0]; cols += [idx(i, j + 1)]; vals += [ve / he]; diag -= ve / he
            elif ve < 0 and j > 0:
                rows += [k0]; cols += [idx(i, j - 1)]; vals += [-ve / he]; diag += ve / he
            if j > 0:
                rows += [k0]; cols += [idx(i, j - 1)]; vals += [De / he ** 2]; diag -= De / he ** 2
            if j < ne - 1:
                rows += [k0]; cols += [idx(i, j + 1)]; vals += [De / he ** 2]; diag -= De / he ** 2
            rows.append(k0); cols.append(k0); vals.append(diag)
    M = sp.csr_matrix((vals, (rows, cols)), shape=(N, N))
    T = spla.spsolve(M.tocsc(), b).reshape(nx, ne)
    return x, e, T

def mfpt2d(mu, lam, P, X0, **kw):
    x, e, T = kolmogorov2d(mu, lam, P, **kw)
    w = np.exp(-0.5 * (e / P['s']) ** 2); w /= w.sum()
    Tx = T @ w                                  # average over the stationary eps
    return float(np.interp(X0, x, Tx))

def mfpt1d(mu, lam, P, X0, n=40001):
    """white-noise reduction: noise linearized in eps, Stratonovich, second-order mean drift."""
    s2, th, tau = P['s'] ** 2, P['theta'], P['tau']
    x = np.linspace(XLO, XESC, n)
    Fx = F(x, lam)
    A = (mu * np.exp(0.0) - Fx) / tau                    # E[1/r] = exp(s^2): mean shift
    A = (mu * np.exp(s2) - (x + (Fx - x) * np.exp(s2))) / tau
    g = (Fx - mu - x) / tau
    Dn = g ** 2 * s2 * th
    AI = A + 0.5 * np.gradient(Dn, x)
    psi = np.concatenate([[0.0], np.cumsum(0.5 * (AI[1:] / Dn[1:] + AI[:-1] / Dn[:-1]) * np.diff(x))])
    psi -= psi.max()
    inner = np.concatenate([[0.0], np.cumsum(0.5 * (np.exp(psi[1:]) / Dn[1:] + np.exp(psi[:-1]) / Dn[:-1]) * np.diff(x))])
    integ = np.exp(-psi) * inner
    i0 = np.searchsorted(x, X0)
    return float(np.sum(0.5 * (integ[i0 + 1:] + integ[i0:-1]) * np.diff(x[i0:])))

def kramers_rule(mu, lam, P):
    Xs, Xu = stable(mu, lam)
    k = Fp(Xs, lam) / P['tau']; g = Xs / P['tau']
    var = g ** 2 * P['s'] ** 2 * P['theta'] / (k * (1 + k * P['theta']))
    return float(2 * np.pi / k * np.exp((Xu - Xs) ** 2 / (6 * var))), k, var

def simulate(mu, lam, P, X0, n=2000, tmax=4000.0, dt=0.005, seed=0):
    rng = np.random.default_rng(seed)
    s, th = P['s'], P['theta']
    X = np.full(n, X0); eps = s * rng.standard_normal(n)
    a = np.exp(-dt / th); b = s * np.sqrt(1 - a * a)
    tfp = np.full(n, np.nan); alive = np.ones(n, bool); t = 0.0
    for it in range(int(tmax / dt)):
        idx = np.nonzero(alive)[0]
        if idx.size == 0:
            break
        x = X[idx] + dt * drift(X[idx], eps[idx], mu, lam, P)
        x = np.maximum(x, XLO)
        esc = x >= XESC
        X[idx] = np.minimum(x, XESC)
        eps[idx] = eps[idx] * a + b * rng.standard_normal(idx.size)
        t += dt
        if esc.any():
            tfp[idx[esc]] = t; alive[idx[esc]] = False
    nev = int(np.sum(~np.isnan(tfp)))
    total = np.nansum(tfp) + np.sum(np.isnan(tfp)) * t
    return dict(mfpt=float(total / max(nev, 1)), events=nev, n=n, t_end=t)

if __name__ == '__main__':
    P = dict(P0); mu = mu_of(P); Qc = Qc_of(P)
    fs = [float(f) for f in sys.argv[1].split(',')] if len(sys.argv) > 1 else [0.6, 0.7, 0.8, 0.9, 0.95]
    for f in fs:
        lam = f * lam_crit(mu); Xs, Xu = stable(mu, lam)
        t0 = time.time(); T2 = mfpt2d(mu, lam, P, Xs); t2 = time.time() - t0
        T1 = mfpt1d(mu, lam, P, Xs); TR, k, var = kramers_rule(mu, lam, P)
        S = simulate(mu, lam, P, Xs, seed=int(1000 * f)) if (len(sys.argv) < 3 or sys.argv[2] != 'nosim') else dict(mfpt=np.nan, events=0, n=0)
        print(f"f={f:.2f} T_sim={S['mfpt']:.1f} ({S['events']}/{S['n']})  T_2D={T2:.1f} [{t2:.1f}s]  T_1D={T1:.1f}  T_Kramers={TR:.1f}", flush=True)
