"""ATRIB-GO: causal attribution of a well-salinization event to a pumping increase.

Toe model of KRAMERS-GO (kramers2.py): Strack toe X = x_toe/d relaxing with time scale tau, driven by a
lognormal recharge factor r = exp(eps - s^2/2), eps an Ornstein-Uhlenbeck process (s, theta).
At t = 0 pumping rises from Q0 = f0*Qc (toe at its stable position) to Q1 = f1*Qc. Event E: the toe
reaches the well (X >= 0.98) within H years. Twin worlds share the exogenous recharge path eps(t)
(Pearl's abduction-action-prediction), so for one path the toe is a deterministic function of the
pumping and of eps.
"""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kramers_go'))   # kramers2.py
import kramers2 as KR

P = dict(KR.P0)
MU = KR.mu_of(P)
LC = KR.lam_crit(MU)
QC = KR.Qc_of(P)
DT = 0.02
H = 30.0
NT = int(round(H / DT))
TG = DT * np.arange(NT + 1)            # grid 0..H

def x0_of(f):
    return KR.stable(MU, f * LC)[0]

def ou_paths(n, rng, s=None, theta=None):
    """stationary OU paths on TG, shape (n, NT+1)."""
    s = P['s'] if s is None else s; th = P['theta'] if theta is None else theta
    a = np.exp(-DT / th); b = s * np.sqrt(1 - a * a)
    e = np.empty((n, NT + 1)); e[:, 0] = s * rng.standard_normal(n)
    z = rng.standard_normal((n, NT))
    for k in range(NT):
        e[:, k + 1] = a * e[:, k] + b * z[:, k]
    return e

def run(eps, f, x0, record=None):
    """toe paths for recharge paths eps (n, NT+1) at pumping f*Qc from x0.
    Returns event flag, event time (nan if none) and, if record is a step list, the toe at those steps."""
    n = eps.shape[0]; lam = f * LC
    X = np.full(n, x0); tev = np.full(n, np.nan); alive = np.ones(n, bool)
    rec = np.empty((n, len(record))) if record is not None else None
    rset = {k: i for i, k in enumerate(record)} if record is not None else {}
    for k in range(NT):
        x = X + DT * KR.drift(X, eps[:, k], MU, lam, P)
        x = np.maximum(x, KR.XLO)
        hit = alive & (x >= KR.XESC)
        tev[hit] = TG[k + 1]; alive &= ~hit
        X = np.where(alive, x, KR.XESC)
        if (k + 1) in rset:
            rec[:, rset[k + 1]] = X
    return ~np.isnan(tev), tev, rec

def ou_cov(s=None, theta=None):
    s = P['s'] if s is None else s; th = P['theta'] if theta is None else theta
    return s * s * np.exp(-np.abs(TG[:, None] - TG[None, :]) / th)

def avg_matrix(period):
    """rows average eps over consecutive blocks of `period` years (left-closed)."""
    m = int(round(period / DT)); nb = NT // m
    A = np.zeros((nb, NT + 1))
    for i in range(nb):
        A[i, i * m:(i + 1) * m] = 1.0 / m
    return A

class RechargeConditioner:
    """Exact Gaussian conditioning of the OU path on noisy block means (Matheron's rule)."""
    def __init__(self, period, sig):
        C = ou_cov(); self.A = avg_matrix(period); self.sig = sig
        Cey = C @ self.A.T
        Cyy = self.A @ Cey + sig * sig * np.eye(self.A.shape[0])
        self.K = np.linalg.solve(Cyy, Cey.T).T          # (NT+1, nb)
    def observe(self, eps, rng):
        return eps @ self.A.T + self.sig * rng.standard_normal((eps.shape[0], self.A.shape[0]))
    def posterior(self, y, n, rng):
        prior = ou_paths(n, rng)
        yp = prior @ self.A.T + self.sig * rng.standard_normal((n, self.A.shape[0]))
        return prior + (y[None, :] - yp) @ self.K.T


def json_clean(o):
    """Replace NaN by None so the results file is standard JSON (readable by Node)."""
    if isinstance(o, dict):
        return {k: json_clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [json_clean(v) for v in o]
    if isinstance(o, float) and o != o:
        return None
    return o
