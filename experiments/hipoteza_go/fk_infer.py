"""HIPOTEZA-GO inference for the Fushe-Kuqe data: unknown well positions as discrete nuisance parameters.

The four analysed wells have no published coordinates, only a transect position (Cenameri & Beqiraj 2016); the
chloride manuscript assigns them to distance bands and screens.  For a member theta, sample i can sit at any column
p of its band, so the data condition is
    exists S in the box and positions p_i:   |G_{i,p_i}(theta) . S - y_i| <= kappa eps_i   for all i,
a mixed-integer linear programme (one binary per candidate position, big-M rows; HiGHS through scipy.optimize.milp).
The share of source k at sample i, G_ik S_k / G_i . S, has sharp bounds by enumerating the position of sample i
and solving the Charnes-Cooper programme with the positions of the other samples as binaries.  Everything else
(tolerance factor, union over the members not ruled out, sub-library tests) is that of hip_infer."""
import contextlib
import os

import numpy as np
from scipy.optimize import milp as _milp, LinearConstraint, Bounds


@contextlib.contextmanager
def _quiet():
    """HiGHS prints internal notes on the C stdout during branch and bound; they are silenced at the descriptor."""
    fd = os.dup(1)
    nul = os.open(os.devnull, os.O_WRONLY)
    os.dup2(nul, 1)
    try:
        yield
    finally:
        os.dup2(fd, 1); os.close(fd); os.close(nul)


def milp(*a, **k):
    with _quiet():
        return _milp(*a, **k)

SRC = ['MS', 'LG', 'FW', 'AN', 'RS', 'DB']
NAMES = {'MS': 'modern seawater', 'LG': 'Patok lagoon water', 'FW': 'fresh recharge', 'AN': 'anthropogenic',
         'RS': 'legacy salinity', 'DB': 'deep saline water'}
# strengths: chloride of sea, lagoon, fresh recharge [mg/L]; anthropogenic and deep fluxes [g/m2/d]; legacy release
# [g/m3/d]
S_INT = np.array([[20500.0, 22000.0], [5000.0, 22000.0], [5.0, 25.0], [0.0, 0.25], [0.0, 0.03], [0.0, 3.0]])
WELLS = [('503', 1048.12, 'sw', 1), ('341', 1038.0, 'sw', 1), ('340', 416.86, 'c', 0), ('193', 12.92, 'ne', 0)]
CL_SD = (0.05, 1.0)          # relative and absolute: covers the 1984-2001 variation of wells 341 and 503 (about 6 %)
FACTS = [('h_lit', 3.0, 1.0), ('h_wf_ag', 1.5, 1.0), ('h_wf0_ag', 8.0, 1.5)]
K_EPS = 2.5
FULL = [0, 1, 2, 3, 4, 5]
BASE = [0, 2]                # sea and fresh recharge are in every library


def bands(E, sh=None):
    """Candidate columns of every sample."""
    from fk_core import BANDS
    d = E['dist']
    return [np.flatnonzero((d >= BANDS[b][0]) & (d <= BANDS[b][1])) for (_, _, b, _) in WELLS]


def data(wells=WELLS):
    y = np.array([w[1] for w in wells])
    return y, K_EPS * (CL_SD[0] * y + CL_SD[1])


def head_values(E):
    return {'h_lit': E['h_lit'], 'h_wf_ag': E['h_wf'] - E['ground'], 'h_wf0_ag': E['h_wf0'] - E['ground']}


def kappa_head(E, facts=FACTS, which=None):
    hv = head_values(E)
    ks = [np.abs(hv[k] - v) / (K_EPS * sd) for (k, v, sd) in facts if which is None or k in which]
    return np.max(ks, axis=0)


def responses(E, j, cols, screens):
    """G_list: for every sample the (positions x sources) responses of member j."""
    G = []
    for c, q in zip(cols, screens):
        g = np.asarray(E['resp'][j][c, q, :], float)
        g = np.where(np.isfinite(g), g, 0.0)
        G.append(np.where(np.abs(g) < 1e-12, 0.0, g))
    return G


def box(lib):
    lo = np.zeros(6); hi = np.zeros(6)
    for k in lib:
        lo[k], hi[k] = S_INT[k]
    return lo, hi


def kappa_lower(G, y, eps, lo, hi):
    """Lower bound of kappa from the boxes alone (each sample at its best position)."""
    kb = 0.0
    for g, yi, ei in zip(G, y, eps):
        a, b = g @ lo, g @ hi
        kb = max(kb, float(np.min(np.maximum(0.0, np.maximum(a - yi, yi - b)) / ei)))
    return kb


def kappa_milp(G, y, eps, lo, hi, kcap=50.0):
    """Smallest kappa for which some strengths in the box and some positions reproduce every sample."""
    ns = 6
    npos = [len(g) for g in G]
    nv = ns + 1 + sum(npos)
    c = np.zeros(nv); c[ns] = 1.0
    A, lb, ub = [], [], []
    off = ns + 1
    for g, yi, ei in zip(G, y, eps):
        M = (float(np.max(g @ hi)) + yi) / ei + kcap + 1.0
        for p in range(len(g)):
            r = np.zeros(nv); r[:ns] = g[p] / ei; r[ns] = -1.0; r[off + p] = M
            A.append(r); lb.append(-np.inf); ub.append(yi / ei + M)
            r = np.zeros(nv); r[:ns] = -g[p] / ei; r[ns] = -1.0; r[off + p] = M
            A.append(r); lb.append(-np.inf); ub.append(-yi / ei + M)
        r = np.zeros(nv); r[off:off + len(g)] = 1.0; A.append(r); lb.append(1.0); ub.append(1.0)
        off += len(g)
    integ = np.r_[np.zeros(ns + 1), np.ones(nv - ns - 1)]
    bnd = Bounds(np.r_[lo, 0.0, np.zeros(nv - ns - 1)], np.r_[hi, kcap, np.ones(nv - ns - 1)])
    r = milp(c, constraints=LinearConstraint(np.array(A), lb, ub), integrality=integ, bounds=bnd,
             options=dict(time_limit=20.0))
    return float(r.x[ns]) if r.status == 0 else (kcap if r.status == 2 else np.nan)


def kappa_member(E, j, lib, y, eps, cols, screens, kh, cut=2.5):
    """kappa of member j for a library: the larger of the head and the chloride misfit; the MILP is solved only if
    the cheap lower bound is below `cut` (above it the returned value is a lower bound)."""
    if kh > cut:
        return kh
    G = responses(E, j, cols, screens)
    lo, hi = box(lib)
    kb = kappa_lower(G, y, eps, lo, hi)
    if max(kh, kb) > cut:
        return max(kh, kb)
    return max(kh, kappa_milp(G, y, eps, lo, hi))


def share_bounds(G, y, eps, kap, lo, hi, i, srcs, senses=None):
    """Sharp bounds of the chloride shares of the sources `srcs` at sample i, over the strengths in the box and the
    positions of all samples, at tolerance kap * eps.  Returns dict k -> (lo, hi), or None if infeasible.
    senses: optional dict k -> tuple of 'min'/'max' to compute (the others are returned as nan)."""
    ns = 6
    others = [l for l in range(len(G)) if l != i]
    npos = [len(G[l]) for l in others]
    nv = ns + 1 + sum(npos)
    out = {k: [np.inf, -np.inf] for k in srcs}
    feasible = False
    for p in range(len(G[i])):
        g = G[i][p]
        a, b = g @ lo, g @ hi
        if a > y[i] + kap * eps[i] or b < y[i] - kap * eps[i]:
            continue
        tmin = 1.0 / (y[i] + kap * eps[i])
        tmax = 1.0 / max(y[i] - kap * eps[i], 1e-9)
        if a > 0:
            tmax = min(tmax, 1.0 / a)
        tmin = max(tmin, 1.0 / b)
        if tmin > tmax:
            continue
        A, lb, ub = [], [], []
        r = np.zeros(nv); r[:ns] = g; A.append(r); lb.append(1.0); ub.append(1.0)            # normalisation
        for k in range(ns):                                                                  # box, scaled
            r = np.zeros(nv); r[k] = 1.0; r[ns] = -hi[k]; A.append(r); lb.append(-np.inf); ub.append(0.0)
            r = np.zeros(nv); r[k] = -1.0; r[ns] = lo[k]; A.append(r); lb.append(-np.inf); ub.append(0.0)
        off = ns + 1
        for l in others:
            gl, yl, el = G[l], y[l], eps[l]
            M = tmax * (float(np.max(gl @ hi)) + yl + kap * el) + 1e-9
            for q in range(len(gl)):
                r = np.zeros(nv); r[:ns] = gl[q]; r[ns] = -(yl + kap * el); r[off + q] = M
                A.append(r); lb.append(-np.inf); ub.append(M)
                r = np.zeros(nv); r[:ns] = -gl[q]; r[ns] = (yl - kap * el); r[off + q] = M
                A.append(r); lb.append(-np.inf); ub.append(M)
            r = np.zeros(nv); r[off:off + len(gl)] = 1.0; A.append(r); lb.append(1.0); ub.append(1.0)
            off += len(gl)
        A = np.array(A)
        integ = np.r_[np.zeros(ns + 1), np.ones(nv - ns - 1)]
        bnd = Bounds(np.r_[np.zeros(ns), tmin, np.zeros(nv - ns - 1)],
                     np.r_[np.full(ns, np.inf), tmax, np.ones(nv - ns - 1)])
        cons = LinearConstraint(A, lb, ub)
        r0 = milp(np.zeros(nv), constraints=cons, integrality=integ, bounds=bnd, options=dict(time_limit=20.0))
        if r0.status != 0:
            continue
        feasible = True
        for k in srcs:
            if g[k] <= 0.0:
                out[k][0] = min(out[k][0], 0.0); out[k][1] = max(out[k][1], 0.0)
                continue
            for sgn in (1.0, -1.0):
                if senses is not None and ('min' if sgn > 0 else 'max') not in senses.get(k, ()):
                    continue
                cvec = np.zeros(nv); cvec[k] = sgn * g[k]
                r = milp(cvec, constraints=cons, integrality=integ, bounds=bnd, options=dict(time_limit=20.0))
                if r.status != 0:              # never a guess: fall back to the trivial bound
                    v = 0.0 if sgn > 0 else 1.0
                else:
                    v = sgn * r.fun
                if sgn > 0:
                    out[k][0] = min(out[k][0], v)
                else:
                    out[k][1] = max(out[k][1], v)
    if not feasible:
        return None
    cl = lambda v: float(np.clip(v, 0, 1)) if np.isfinite(v) else float('nan')
    return {k: (cl(v[0]), cl(v[1])) for k, v in out.items()}
