"""HIPOTEZA-GO inference: one identified set for all samples, with the physics as the link.

For hydraulic parameters theta the tracers of every sample are LINEAR in a short vector u of source strengths and
source signatures (shared by all samples):
    Cl_i   = sum_k G_ik(theta) S_k                      S = (Cl_sea, Cl_lagoon, Cl_fresh, b_AN, b_RS, b_DB)
    Br_i   = sum_k G_ik(theta) B_k,   rho_k^- S_k <= B_k <= rho_k^+ S_k      (lifting of B_k = rho_k S_k, exact)
    d18O_i = sum_w W_iw(theta) d_w,   H3_i = sum_w T_iw(theta) t_w           (water-carrying sources, decay in T)
so for each theta the set of u that reproduces the data within kappa * eps is a polytope, and the share of chloride
of source k in sample i, G_ik S_k / sum_j G_ij S_j, has sharp bounds by two linear programmes (Charnes-Cooper).
The nonlinear directions (theta) are covered by an ensemble: a member is 'not ruled out' when its polytope is
non-empty; the answer is the union over the members not ruled out.  Hypotheses are terms of the equations:
dropping a source from the library and finding every member ruled out falsifies the reduced library.
The tolerance inflation kappa absorbs the finite resolution of the ensemble; its level is calibrated by leaving
members out (calib_kappa)."""
import numpy as np
from scipy.optimize import linprog

SRC = ['MS', 'LG', 'FW', 'AN', 'RS', 'DB']
NAMES = {'MS': 'modern seawater', 'LG': 'lagoon water', 'FW': 'fresh recharge', 'AN': 'anthropogenic',
         'RS': 'legacy salinity', 'DB': 'deep saline water'}
RESP = ['W_MS', 'W_LG', 'W_FW', 'G_AN', 'G_RS', 'G_DB']
WAT = ['W_MS', 'W_LG', 'W_FW']
TRI = ['T_MS', 'T_LG', 'T_FW']
# strengths: chloride of the three waters [mg/L]; solute fluxes [g/m2/d], release rate [g/m3/d]
S_INT = np.array([[19500, 21500], [7800, 19350], [10, 25], [0, 0.25], [0, 0.03], [0, 1.5]], float)
BR = np.array([[3.35e-3, 3.50e-3], [3.35e-3, 3.50e-3], [3.0e-3, 5.0e-3], [1.2e-3, 2.8e-3], [2.9e-3, 3.8e-3],
               [5.0e-3, 1.0e-2]])
D18 = np.array([[0.8, 1.4], [1.0, 4.0], [-7.4, -6.4]])
H3 = np.array([[0.4, 0.9], [2.0, 5.0], [3.0, 6.0]])
NOISE = {'Cl': (0.03, 1.0), 'Br': (0.05, 0.005), 'd18O': (0.0, 0.1), 'H3': (0.05, 0.3)}
SD_HEAD = 0.5                # heads: survey, datum and seasonal error [m]
K_EPS = 2.5
NV = 18                      # u = [S (6), B (6), d (3), t (3)]
NS = 20                      # samples: 10 wells x 2 screens, index 2 * well + screen
L5 = [0, 1, 2, 3, 4]         # library without the deep saline water
L6 = [0, 1, 2, 3, 4, 5]
TINY = 1e-12                 # responses below this are numerical dust (set to zero in the programmes)

ALLS = np.arange(NS)
SCEN = {
    'A  chloride at 4 wells': dict(cl=np.array([0, 1, 4, 5, 10, 11, 16, 17]), wells=np.array([0, 2, 5, 8]), tr=[],
                                   em=False),
    'B  chloride at all wells': dict(cl=ALLS, wells=np.arange(10), tr=[], em=False),
    'C  + Br, d18O, tritium': dict(cl=ALLS, wells=np.arange(10), tr=['Br', 'd18O', 'H3'], em=False),
    'D  + end-members sampled': dict(cl=ALLS, wells=np.arange(10), tr=['Br', 'd18O', 'H3'], em=True),
}


def sd_of(t, v):
    rel, ab = NOISE[t]
    return rel * np.abs(v) + ab


# ------------------------------------------------------------------------------------------------ truths
def draw_truth(R, rng, world='W0'):
    """Strengths and signatures of one truth with responses R (dict of arrays over the samples); noise-free and
    noisy tracers; true chloride shares (NS x 6)."""
    S = np.array([rng.uniform(*S_INT[0]), rng.uniform(*S_INT[1]), rng.uniform(*S_INT[2]),
                  0.0 if rng.uniform() < 0.3 else rng.uniform(0.03, 0.2),
                  0.0 if rng.uniform() < 0.3 else rng.uniform(0.003, 0.02),
                  rng.uniform(0.2, 1.0) if world == 'W1' else 0.0])
    rho = rng.uniform(BR[:, 0], BR[:, 1]); d = rng.uniform(D18[:, 0], D18[:, 1]); t = rng.uniform(H3[:, 0], H3[:, 1])
    G = np.array([R[k] for k in RESP]).T; Wf = np.array([R[k] for k in WAT]).T; Wt = np.array([R[k] for k in TRI]).T
    true = {'Cl': G @ S, 'Br': G @ (rho * S), 'd18O': Wf @ d, 'H3': Wt @ t}
    obs = {k: v + rng.standard_normal(v.shape) * sd_of(k, v) for k, v in true.items()}
    obs['head'] = R['head'] + rng.standard_normal(R['head'].shape) * SD_HEAD
    share = (G * S[None, :]) / true['Cl'][:, None]
    return dict(S=S, rho=rho, d=d, t=t, true=true, obs=obs, share=share)


def intervals(truth=None, em=False):
    """Intervals of u.  With em=True the sea, the lagoon and the fresh end-members were sampled (their chloride,
    Br/Cl, d18O and tritium shrink to the measured value +- its error) and so was the Br/Cl of the anthropogenic
    source; the legacy and deep sources cannot be sampled."""
    S, R, D, T = S_INT.copy(), BR.copy(), D18.copy(), H3.copy()
    if em and truth is not None:
        for k in (0, 1, 2):
            v = truth['S'][k]; dv = 0.03 * v + (1.0 if k == 2 else 0.0)
            S[k] = [max(v - dv, S[k, 0]), min(v + dv, S[k, 1])]
            v = truth['d'][k]; D[k] = [max(v - 0.2, D[k, 0]), min(v + 0.2, D[k, 1])]
            v = truth['t'][k]; dv = 0.05 * v + 0.1; T[k] = [max(v - dv, T[k, 0]), min(v + dv, T[k, 1])]
        for k in (0, 1, 2, 3):
            v = truth['rho'][k]; R[k] = [max(0.97 * v, R[k, 0]), min(1.03 * v, R[k, 1])]
    return S, R, D, T


# ------------------------------------------------------------------------------------------------ the linear part
def rows(E, j, sc):
    """Data rows of member j for a scenario: A (m x NV), and the keys (tracer, sample) of the rows."""
    G = np.array([E[k][j] for k in RESP]).T; Wf = np.array([E[k][j] for k in WAT]).T; Wt = np.array([E[k][j] for k in TRI]).T
    G, Wf, Wt = (np.where(np.abs(a) < TINY, 0.0, a) for a in (G, Wf, Wt))
    blocks, keys = [], []
    a = np.zeros((len(sc['cl']), NV)); a[:, 0:6] = G[sc['cl']]; blocks.append(a); keys += [('Cl', i) for i in sc['cl']]
    if 'Br' in sc['tr']:
        a = np.zeros((NS, NV)); a[:, 6:12] = G; blocks.append(a); keys += [('Br', i) for i in range(NS)]
    if 'd18O' in sc['tr']:
        a = np.zeros((NS, NV)); a[:, 12:15] = Wf; blocks.append(a); keys += [('d18O', i) for i in range(NS)]
    if 'H3' in sc['tr']:
        a = np.zeros((NS, NV)); a[:, 15:18] = Wt; blocks.append(a); keys += [('H3', i) for i in range(NS)]
    return np.vstack(blocks), keys, G


def data_of(truth, sc):
    y = [truth['obs']['Cl'][sc['cl']]]
    e = [K_EPS * sd_of('Cl', y[0])]
    for t in sc['tr']:
        v = truth['obs'][t]; y.append(v); e.append(K_EPS * sd_of(t, v))
    return np.concatenate(y), np.concatenate(e)


def fixed_part(iv, lib):
    """Coupling rows F u <= 0 of the lifted bromide variables and the bounds of u for a library (list of sources)."""
    S, R, D, T = iv
    F = []
    lo = np.zeros(NV); hi = np.full(NV, np.inf)
    for k in range(6):
        if k in lib:
            lo[k], hi[k] = S[k]
            r = np.zeros(NV); r[6 + k] = 1.0; r[k] = -R[k, 1]; F.append(r)
            r = np.zeros(NV); r[6 + k] = -1.0; r[k] = R[k, 0]; F.append(r)
        else:
            lo[k] = hi[k] = 0.0; lo[6 + k] = hi[6 + k] = 0.0
    lo[12:15], hi[12:15] = D[:, 0], D[:, 1]
    lo[15:18], hi[15:18] = T[:, 0], T[:, 1]
    return np.array(F), lo, hi


def kappa_lp(A, y, eps, F, lo, hi):
    """Smallest tolerance inflation for which the member reproduces the data: min kappa s.t. |A u - y| <= kappa eps
    (rows scaled by their tolerance)."""
    c = np.zeros(NV + 1); c[-1] = 1.0
    As, ys = A / eps[:, None], y / eps
    one = np.ones((len(y), 1))
    Aub = np.vstack([np.c_[As, -one], np.c_[-As, -one], np.c_[F, np.zeros(len(F))]])
    bub = np.r_[ys, -ys, np.zeros(len(F))]
    bounds = [(lo[v], None if np.isinf(hi[v]) else hi[v]) for v in range(NV)] + [(0, None)]
    r = linprog(c, A_ub=Aub, b_ub=bub, bounds=bounds, method='highs')
    return float(r.fun) if r.status == 0 else np.inf


def kappa_lower(E, truth, sc, iv, lib, members):
    """A lower bound of kappa for every member without a linear programme: the head misfit, and for every tracer
    row the distance of the observation from the range that the intervals of the strengths and signatures allow."""
    S, R, D, T = iv
    mask = np.zeros(6, bool); mask[list(lib)] = True
    s_lo, s_hi = np.where(mask, S[:, 0], 0.0), np.where(mask, S[:, 1], 0.0)
    obs = truth['obs']
    lb = np.max(np.abs(E['head'][members][:, sc['wells']] - obs['head'][sc['wells']][None, :]), axis=1) \
        / (K_EPS * SD_HEAD)

    def upd(lb, lo_, hi_, y, e):
        d = np.maximum(0.0, np.maximum(lo_ - y[None, :], y[None, :] - hi_)) / e[None, :]
        return np.maximum(lb, d.max(axis=1))

    G = np.stack([E[k][members] for k in RESP], axis=2)                    # members x samples x sources
    y = obs['Cl'][sc['cl']]
    lb = upd(lb, G[:, sc['cl'], :] @ s_lo, G[:, sc['cl'], :] @ s_hi, y, K_EPS * sd_of('Cl', y))
    if 'Br' in sc['tr']:
        y = obs['Br']; lb = upd(lb, G @ (R[:, 0] * s_lo), G @ (R[:, 1] * s_hi), y, K_EPS * sd_of('Br', y))
    if 'd18O' in sc['tr']:
        W = np.clip(np.stack([E[k][members] for k in WAT], axis=2), 0.0, None)
        y = obs['d18O']; lb = upd(lb, W @ D[:, 0], W @ D[:, 1], y, K_EPS * sd_of('d18O', y))
    if 'H3' in sc['tr']:
        W = np.clip(np.stack([E[k][members] for k in TRI], axis=2), 0.0, None)
        y = obs['H3']; lb = upd(lb, W @ T[:, 0], W @ T[:, 1], y, K_EPS * sd_of('H3', y))
    return lb


def kappa_all(E, truth, sc, iv, lib, members=None, cut=2.5):
    """kappa of every member (head misfit and tracer misfit).  The linear programme is solved only for the members
    whose cheap lower bound is below `cut`; the values above `cut` are lower bounds."""
    members = np.arange(len(E['head'])) if members is None else members
    y, eps = data_of(truth, sc)
    F, lo, hi = fixed_part(iv, lib)
    out = kappa_lower(E, truth, sc, iv, lib, members)
    for n in np.flatnonzero(out <= cut):
        A, _, _ = rows(E, members[n], sc)
        out[n] = max(out[n], kappa_lp(A, y, eps, F, lo, hi))
    return out


def box_share(G, lo_u, hi_u, pair):
    """Outer bounds of a share from the intervals of the strengths alone (the share increases with its own strength
    and decreases with the others)."""
    i, k = pair
    g = G[i]
    a_hi, a_lo = g[k] * hi_u[k], g[k] * lo_u[k]
    r_lo = float(g @ lo_u[:6]) - g[k] * lo_u[k]; r_hi = float(g @ hi_u[:6]) - g[k] * hi_u[k]
    hi = a_hi / (a_hi + r_lo) if a_hi + r_lo > 0 else 0.0
    lo = a_lo / (a_lo + r_hi) if a_lo + r_hi > 0 else 0.0
    return lo, hi


def member_bounds(A, y, eps, kap, F, lo, hi, G, pairs):
    """Sharp bounds of the chloride shares G_ik S_k / sum_j G_ij S_j for the listed (i, k) in one member, at tolerance
    kap * eps (Charnes-Cooper).  Returns array (len(pairs), 2), or None if the member is ruled out at this tolerance.
    A programme that the solver does not finish is replaced by the outer bound of box_share (never by a guess)."""
    nv = NV + 1
    As, ys = A / eps[:, None], y / eps
    rows_ = [np.c_[As, -(ys + kap)], np.c_[-As, (ys - kap)], np.c_[F, np.zeros(len(F))]]
    fin = np.isfinite(hi)
    I = np.eye(NV)
    rows_.append(np.c_[I[fin], -hi[fin]])
    rows_.append(np.c_[-I, lo])
    Aub = np.vstack(rows_); bub = np.zeros(len(Aub))
    bounds = [(None, None)] * NV + [(0, None)]
    out = np.zeros((len(pairs), 2))
    solved = 0
    for n, (i, k) in enumerate(pairs):
        if G[i, k] <= 0.0:                              # the source does not reach the sample
            continue
        Aeq = np.zeros((1, nv)); Aeq[0, 0:6] = G[i]
        for s_, sg in ((0, 1.0), (1, -1.0)):
            c = np.zeros(nv); c[k] = sg * G[i, k]
            r = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=[1.0], bounds=bounds, method='highs')
            if r.status != 0:
                if r.status == 2 and solved == 0:
                    return None
                r = linprog(c, A_ub=Aub, b_ub=bub, A_eq=Aeq, b_eq=[1.0], bounds=bounds, method='highs-ipm')
            if r.status == 0:
                out[n, s_] = sg * r.fun; solved += 1
            else:
                out[n, s_] = box_share(G, lo, hi, (i, k))[s_]
    return np.clip(out, 0.0, 1.0)


# ------------------------------------------------------------------------------------------------ the union
N_MIN = 39       # the hull of n exchangeable values misses a new one with probability 2 / (n + 1): 5% at n = 39


def attribute(E, truth, sc, lib, kap_res, rng, members=None, n_full=20, full=False, srcs=(0, 1, 3, 4), kap=None,
              n_min=N_MIN, cut=2.5):
    """HIPOTEZA-GO for one truth and one scenario.  Returns dict with kappa_min, the members of the union, the union
    bounds lo/hi (NS x 6, nan where not computed) and the flags of completeness of each pair.
    Falsification: no member reproduces the data within kap_res.  Otherwise the union is taken over the members
    within kappa_eff = max(kap_res, kappa of the n_min-th best member), so that it never rests on a handful of
    simulations.  After n_full members only the pairs that still carry a statement (lower bound above 1/2, or upper
    bound below 0.1) are followed; the others keep an incomplete union and are flagged."""
    iv = intervals(truth, sc['em'])
    members = np.arange(len(E['head'])) if members is None else members
    if kap is None:
        kap = kappa_all(E, truth, sc, iv, lib, members, cut)
    kmin = float(kap.min())
    out = dict(kappa_min=kmin, falsified=bool(kmin > kap_res), n_nroy=0, n_res=int((kap <= kap_res).sum()), kap=kap,
               members=members, kappa_eff=float('nan'))
    lo = np.full((NS, 6), np.nan); hi = np.full((NS, 6), np.nan); exact = np.zeros((NS, 6), bool)
    out.update(lo=lo, hi=hi, exact=exact)
    if kmin > kap_res:
        return out
    ks = np.sort(kap)
    kap_eff = float(min(max(kap_res, ks[min(n_min, len(ks)) - 1]), max(cut, kap_res)))
    nroy = rng.permutation(members[kap <= kap_eff])
    out['n_nroy'] = int(len(nroy)); out['kappa_eff'] = kap_eff
    y, eps = data_of(truth, sc)
    F, lo_u, hi_u = fixed_part(iv, lib)
    sal = np.flatnonzero(truth['obs']['Cl'] > 100.0)
    srcs = [k for k in srcs if k in lib] + ([5] if 5 in lib else [])
    pairs = [(i, k) for i in sal for k in srcs]
    run_lo = {p: 1.0 for p in pairs}; run_hi = {p: 0.0 for p in pairs}
    active, narrowed, n_ok = list(pairs), False, 0
    for j in nroy:
        A, _, G = rows(E, j, sc)
        todo = active
        if n_ok >= n_full and not full:
            active = [p for p in active if run_lo[p] > 0.5 or run_hi[p] < 0.1]
            narrowed = True
            if not active:
                break
            # outer bounds from the intervals of the strengths alone settle most pairs without a linear programme
            todo = []
            for p in active:
                bl, bh = box_share(G, lo_u, hi_u, p)
                if (run_lo[p] > 0.5 and bl > 0.5) or (run_hi[p] < 0.1 and bh < 0.1):
                    run_lo[p] = min(run_lo[p], bl); run_hi[p] = max(run_hi[p], bh)
                else:
                    todo.append(p)
            if not todo:
                continue
        b = member_bounds(A, y, eps, kap_eff, F, lo_u, hi_u, G, todo)
        if b is None:
            continue
        n_ok += 1
        for p, (l_, h_) in zip(todo, b):
            run_lo[p] = min(run_lo[p], l_); run_hi[p] = max(run_hi[p], h_)
    done = set(active) if narrowed else set(pairs)
    for p in pairs:
        if run_lo[p] <= run_hi[p]:
            lo[p], hi[p] = run_lo[p], run_hi[p]
            exact[p] = p in done
    out['sal'] = sal; out['n_ok'] = n_ok
    return out


def sub_kappa(E, truth, sc, lib_sub, members, kap_full, upto=3.0):
    """Smallest kappa of a sub-library.  A member needs at least as much tolerance with fewer terms, so the members
    are visited in the order of a lower bound (their full-library kappa and the cheap bound of the sub-library) and
    the search stops when the bound reaches the best value found (the result is then exact) or `upto` (the result
    is then censored: at least `upto`)."""
    iv = intervals(truth, sc['em'])
    y, eps = data_of(truth, sc)
    F, lo, hi = fixed_part(iv, lib_sub)
    lb = np.maximum(kap_full, kappa_lower(E, truth, sc, iv, lib_sub, members))
    best = np.inf
    for n in np.argsort(lb):
        if lb[n] >= best or lb[n] > upto:
            break
        A, _, _ = rows(E, members[n], sc)
        best = min(best, max(lb[n], kappa_lp(A, y, eps, F, lo, hi)))
    return float(best) if best <= upto else float(max(upto, lb.min()))


def true_library(truth):
    """The sources present in a truth: the three waters and the solute sources with a positive strength."""
    return [0, 1, 2] + [k for k in (3, 4, 5) if truth['S'][k] > 0]


def calib_trial(E, sc, lib, rng, world='W0'):
    """One leave-one-out trial: a member generates data; kappa of all the others with the library, and the
    smallest kappa of the library of the truth (the sources present).  A library that contains the truth needs no
    more than the latter, so its quantile bounds the rate at which a true hypothesis is falsified."""
    M = len(E['head'])
    j0 = int(rng.integers(M))
    R = {k: E[k][j0] for k in RESP + WAT + TRI + ['head']}
    tr = draw_truth(R, rng, world)
    others = np.delete(np.arange(M), j0)
    kap = kappa_all(E, tr, sc, intervals(tr, sc['em']), lib, others)
    tl = [k for k in true_library(tr) if k in lib]
    k_true = float(kap.min()) if len(tl) == len(lib) else sub_kappa(E, tr, sc, tl, others, kap)
    return j0, tr, kap, k_true
