"""ZGJEDHJA-GO identified sets and information sources.

Information about the unseen salinized state:
  Q_BOX    q in [0, 0.5]: no information beyond plausibility;
  Q_PHYS   q in [0.08, 0.25]: range of the intrusion probability from the hydrogeological (sharp-interface) ensemble;
  sentinel m well-seasons of high pumping at frontier wells where the front has already arrived, k salinizations:
           Clopper-Pearson 95% interval for q;
  W_BOX    w in [-4, 0]: the salinized well is worth at most 4 a season less than low pumping;
  survey   n_s answers on the cost of replacement water, sd SIGMA_W each: w in wbar -/+ 1.96 SIGMA_W / sqrt(n_s);
  shape    THETA_MIN <= theta_4 <= theta_3: salinity cannot raise the profit of high pumping, which stays above a floor.
Proposition L: theta_4 = c(q) - beta q w / (1 - beta) with c(q) identified for every q; the fee effect depends on q only,
the recharge effect on (q, w).
"""
import numpy as np
from scipy.stats import beta as beta_dist
import zgjedhja_model as Z

Q_GRID = np.round(np.linspace(0.0, 0.5, 201), 6)
W_GRID = np.round(np.linspace(-4.0, 0.0, 401), 6)
Q_BOX, Q_PHYS, W_BOX = (0.0, 0.5), (0.08, 0.25), (-4.0, 0.0)
THETA_MIN = -1.0
SIGMA_W = 1.0


def clopper_pearson(k, m, alpha=0.05):
    if m == 0:
        return Q_BOX
    lo = 0.0 if k == 0 else beta_dist.ppf(alpha / 2, k, m - k + 1)
    hi = 1.0 if k == m else beta_dist.ppf(1 - alpha / 2, k + 1, m - k)
    return (lo, hi)


def tables(P1, F, qgrid=Q_GRID, wgrid=W_GRID):
    """Fee effect on the q grid; recharge effect, theta_4 and the identified theta_3 on the (q, w) grid."""
    g1 = np.array([Z.gamma_fee(P1, F, q) for q in qgrid])
    c = np.array([Z.index_c(P1, F, q) for q in qgrid])
    th3 = Z.invert(P1, F, 0.0, 0.0)[Z.S - 2]
    th4 = c[:, None] - Z.BETA * qgrid[:, None] * wgrid[None, :] / (1 - Z.BETA)
    g2 = np.array([[Z.gamma_recharge(P1, F, q, w) for w in wgrid] for q in qgrid])
    return dict(q=qgrid, w=wgrid, g1=g1, g2=g2, c=c, th4=th4, th3=th3)


def _grid_mask(g, lo, hi):
    m = (g >= lo - 1e-12) & (g <= hi + 1e-12)
    if not m.any():                       # interval narrower than the grid step: keep the nearest grid point
        m = np.zeros(len(g), bool)
        m[int(np.argmin(np.abs(g - 0.5 * (lo + hi))))] = True
    return m


def mask(T, qint, wint, shape=True):
    mq = _grid_mask(T['q'], *qint)
    mw = _grid_mask(T['w'], *wint)
    M = mq[:, None] & mw[None, :]
    if shape:
        M &= (T['th4'] <= T['th3'] + 1e-12) & (T['th4'] >= THETA_MIN - 1e-12)
    return M


def sets(T, qint, wint, shape=True):
    """Identified sets (min, max) of the fee effect and of the recharge effect; None if the restrictions are
    incompatible with the data (a rejection)."""
    M = mask(T, qint, wint, shape)
    if not M.any():
        return None, None
    qok = M.any(1)
    g1 = T['g1'][qok]
    g2 = T['g2'][M]
    return (float(g1.min()), float(g1.max())), (float(g2.min()), float(g2.max()))


def survey_interval(wbar, n_s):
    if n_s <= 0:
        return W_BOX
    h = 1.96 * SIGMA_W / np.sqrt(n_s)
    return (max(W_BOX[0], wbar - h), min(W_BOX[1], wbar + h))
