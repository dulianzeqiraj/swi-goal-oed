"""KTHIMI-GO: how much of what the monitoring network sees reaches the pumping decision, and does that predict
the salinization risk?

Well field of RRJEDHA-GO (../rrjedha_go/rrjedha.py): the KRAMERS-GO toe X with stochastic recharge, annual
decisions A in {0, 1} by the operator from a toe alarm level R (the reading X + sigma * noise in 4 classes), the
drought class D and last year's decision:
    logit P(A_t = 1) = b0 + B1 (2 A_{t-1} - 1) + kappa * BR[R_t] + BD[D_t].
A monitoring design is the pair (sigma, kappa): reading precision and how strongly the operator responds to
the alarm; 'no monitoring' draws R independently of X. For every design the intercept b0 is calibrated so
that the mean pumping (supply) is the same.

Information quantities, exact given the model (bits per decision, averaged over the well-years):
  sensor information     I(X_t; R_t)                     = H(R) - E[H(R | X)]
  feedback information   I(X_t; A_t | A_{t-1}, D_t)      = H(A | A_prev, D) - E[h(p(X, A_prev, D))]
the second is the per-decision term of Massey's feedback directed information I(0X^{n-1} -> A^n), i.e. the
part of I(A^n; X^n) that flows from the toe to the decisions; the rest is the forward flow from pumping to the
toe. Goal: the 10-year salinization risk (toe reaching the escape point) at matched supply."""
import os
import sys
import numpy as np
from scipy.stats import norm
HERE = os.path.dirname(os.path.abspath(__file__))
for p in (os.path.join(HERE, '..', 'rrjedha_go'), os.path.join(HERE, '..', 'rrjedha')):
    if os.path.isdir(p):
        sys.path.insert(0, p)
import rrjedha as Rj
import kramers2 as KR

PR_NOMON = np.array([0.30, 0.20, 0.13, 0.37])     # alarm-level frequencies used when R carries no information


def h2(p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


def p_r_given_x(X, sig):
    """P(R = r | X) for the Gaussian reading, shape (n, 4)."""
    e = np.concatenate([[-np.inf], Rj.R_EDGES, [np.inf]])
    if sig <= 0:
        return np.eye(4)[np.digitize(X, Rj.R_EDGES)]
    c = norm.cdf((e[None, :] - X[:, None]) / sig)
    return np.diff(c, axis=1)


def simulate(n, rng, sig, kappa=1.0, b0=0.0, nomon=False, dbins=None, keep=True):
    s, th = Rj.P['s'], Rj.P['theta']; a = np.exp(-Rj.DT / th); b = s * np.sqrt(1 - a * a)
    eps = s * rng.standard_normal(n); nb = int(round(Rj.BURN / Rj.DT)); w = np.empty((nb, n))
    for k in range(nb):
        eps = a * eps + b * rng.standard_normal(n); w[k] = eps
    X = np.full(n, Rj.X0); Ap = (rng.random(n) < 0.5).astype(float)
    rec = {k: [] for k in ('X', 'Ap', 'D', 'A', 'R')}
    for t in range(Rj.T):
        alive = X < KR.XESC
        u = rng.standard_normal(n)
        R = rng.choice(4, n, p=PR_NOMON) if nomon else np.digitize(X + sig * u, Rj.R_EDGES)
        D = np.digitize(w[-nb:].mean(axis=0), dbins)
        pA = Rj.expit(b0 + Rj.B1 * (2 * Ap - 1) + kappa * Rj.BR[R] + Rj.BD[D])
        A = (rng.random(n) < pA).astype(float)
        z = rng.standard_normal((Rj.STEPS, n))
        x1, e1, w1 = Rj.year(X, eps, A, z)
        if keep:
            for k, v in (('X', X), ('Ap', Ap), ('D', D), ('A', A), ('R', R)):
                rec[k].append(v[alive])
        else:
            rec['A'].append(A[alive])
        X = x1; eps = e1; w = np.concatenate([w, w1])[-nb:]; Ap = A
    out = {k: np.concatenate(v) for k, v in rec.items() if v}
    out['risk'] = float((X >= KR.XESC).mean()); out['supply'] = float(out['A'].mean())
    return out


def information(d, sig, kappa, b0, nomon=False):
    X, Ap, D = d['X'], d['Ap'], d['D']
    PRX = np.tile(PR_NOMON, (len(X), 1)) if nomon else p_r_given_x(X, sig)
    base = b0 + Rj.B1 * (2 * Ap - 1) + Rj.BD[D]
    p = (PRX * Rj.expit(base[:, None] + kappa * Rj.BR[None, :])).sum(1)     # P(A = 1 | X, A_prev, D)
    hcond = h2(p).mean(); hmarg = 0.0
    for ap in (0, 1):
        for dd in range(3):
            m = (Ap == ap) & (D == dd)
            if m.any():
                hmarg += m.mean() * h2(p[m].mean())
    PR = PRX.mean(0)
    HR = -(PR * np.log2(PR)).sum()
    with np.errstate(divide='ignore', invalid='ignore'):
        HRX = -np.where(PRX > 0, PRX * np.log2(PRX), 0).sum(1).mean()
    return dict(feedback=float(hmarg - hcond), sensor=float(HR - HRX))


def calibrate(target, sig, kappa, nomon, dbins, n=30000, seed=11):
    lo, hi = -3.0, 3.0
    for _ in range(22):
        mid = 0.5 * (lo + hi)
        s = simulate(n, np.random.default_rng(seed), sig, kappa, mid, nomon, dbins, keep=False)['supply']
        lo, hi = (mid, hi) if s < target else (lo, mid)
    return 0.5 * (lo + hi)
