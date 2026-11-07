"""NDERHYRJA-GO ("ndërhyrja" = the interference): sensor placement that corrects the interference between sensors,
stays optimal against the worst plausible interference and carries a certified optimality gap.

Test bed: a linear-Gaussian coastal aquifer on the unit square (sea at y = 0). The unknown is a recharge (or salinity
source) anomaly m on a 30 x 30 grid; heads respond through a screened-Poisson operator. Candidates:
  48 piezometers in 16 nests of 3 (one shared cable per nest), served by 4 telemetry hubs (4 nests each);
  1 barometer and 4 hub reference channels (sealed reference transducers), which see the interference only.
Observation error of the candidates (metres of water):
  Gamma(theta) = D + s_a^2 b b^T + s_h^2 H H^T + s_n^2 N N^T + tau^2 E(ell)
  D      independent sensor noise (sigma0 * ss for piezometers, small for the reference channels)
  b      barometric loadings: barometric efficiency BE_i + delta_i for unvented piezometers, 1 for the barometer
  H      logger drift of each hub: 1 for the piezometers of the hub and for its reference channel
  N      cable cross-talk inside a nest (no reference channel: not correctable)
  E(ell) exponentially correlated model error among the piezometers (not correctable)
The correctable part s_a^2 b b^T + s_h^2 H H^T is removed by marginalising its sources, which the reference channels
observe; the uncertain parameters theta = (ss, s_a, s_h, s_n, tau, ell, delta_1..48) live in a box.

Tests (results in res/nderhyrja.json, arrays in res/nderhyrja_case.npz, log in res/nderhyrja_log.txt):
  self-checks  closed forms of Propositions N1-N4 against direct computation
  T33  reference sensors and the correction ceiling (Propositions N1, N2)
  T34  robustness: nominal against robust designs under the worst plausible interference (Proposition N3)
  T35  robust certificates (Proposition N4) and an exhaustive check on a 14-candidate instance
  T36  the correction in operation: calibration of the wellfield forecast and of the corrected heads
usage: python3 nderhyrja_exp.py [quick]"""
import itertools
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize, linprog

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
QUICK = 'quick' in sys.argv
LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


# ----------------------------------------------------------------------------------------------------------- test bed
NG = 30
SIG0 = 0.01            # independent piezometer noise (m), typical transducer accuracy
SIGB = 0.003           # barometer noise (m of water, about 0.3 hPa)
SIGR = 0.005           # hub reference channel noise (m)
HEAD_SD = 0.10         # prior standard deviation of the head anomaly at the piezometers (m)
NAMES = ['ss', 'sa', 'sh', 'sn', 'tau', 'ell']
LO = np.array([0.80, 0.06, 0.01, 0.00, 0.010, 0.03])
HI = np.array([1.25, 0.14, 0.05, 0.02, 0.030, 0.30])
NOM = np.array([1.00, 0.10, 0.03, 0.01, 0.020, 0.10])
DELTA = 0.15           # bound on the error of each barometric efficiency
WELLFIELD = (0.38, 0.62, 0.10, 0.30)   # x0, x1, y0, y1 of the wellfield (the forecast goal)


def lap_dirichlet(n):
    """5-point Laplacian (negative definite) on the n x n cell-centred grid of the unit square, zero outside."""
    h = 1.0 / n
    T = np.diag(-2 * np.ones(n)) + np.diag(np.ones(n - 1), 1) + np.diag(np.ones(n - 1), -1)
    I = np.eye(n)
    return (np.kron(I, T) + np.kron(T, I)) / h ** 2


def bilinear(pts, n):
    """Interpolation matrix from the cell-centred grid values to points (rows sum to 1)."""
    W = np.zeros((len(pts), n * n))
    for r, (x, y) in enumerate(pts):
        gx, gy = x * n - 0.5, y * n - 0.5
        i0, j0 = int(np.clip(np.floor(gx), 0, n - 2)), int(np.clip(np.floor(gy), 0, n - 2))
        tx, ty = gx - i0, gy - j0
        for di, dj, wt in ((0, 0, (1 - tx) * (1 - ty)), (1, 0, tx * (1 - ty)), (0, 1, (1 - tx) * ty), (1, 1, tx * ty)):
            W[r, (j0 + dj) * n + (i0 + di)] += wt
    return W


class Bed:
    """The candidate network and the data-space matrices. keep: optional list of nests (sub-instance)."""

    def __init__(self, nests=None, hubs=None, seed=7):
        rng = np.random.default_rng(seed)
        n = NG
        Lap = lap_dirichlet(n)
        A = np.eye(n * n) - 0.02 * Lap                 # prior: C ~ A^{-2}, correlation length about 0.14
        Ainv = np.linalg.inv(A)
        C0 = Ainv @ Ainv.T
        Gfw = np.linalg.inv(1.0 * np.eye(n * n) - 0.05 * Lap)   # head response to the anomaly (screened Poisson)
        centres, pz, nest_of, hub_of = [], [], [], []
        for j in range(4):
            for i in range(4):
                cx = 0.14 + 0.24 * i + rng.uniform(-0.03, 0.03)
                cy = 0.14 + 0.24 * j + rng.uniform(-0.03, 0.03)
                centres.append((cx, cy))
        centres = np.array(centres)
        for k_, (cx, cy) in enumerate(centres):
            a0 = rng.uniform(0, 2 * np.pi)
            for t in range(3):
                pz.append((cx + 0.025 * np.cos(a0 + 2 * np.pi * t / 3), cy + 0.025 * np.sin(a0 + 2 * np.pi * t / 3)))
                nest_of.append(k_)
                hub_of.append(2 * (centres[k_, 1] > 0.5) + (centres[k_, 0] > 0.5))
        pz, nest_of, hub_of = np.array(pz), np.array(nest_of), np.array(hub_of)
        bhat = rng.uniform(0.4, 0.9, len(pz))         # barometric efficiencies estimated from past records
        if nests is not None:
            sel = np.isin(nest_of, nests)
            pz, nest_of, hub_of, bhat = pz[sel], nest_of[sel], hub_of[sel], bhat[sel]
            centres = centres
        hubs = sorted(set(hub_of.tolist())) if hubs is None else hubs
        self.hubs = hubs
        hub_xy = np.array([(0.25 + 0.5 * (h % 2), 0.25 + 0.5 * (h // 2)) for h in hubs])
        self.np_ = len(pz)
        self.nr = 1 + len(hubs)
        self.n = self.np_ + self.nr
        self.xy = np.vstack([pz, [[0.5, 0.52]], hub_xy])
        self.kind = np.array(['piezo'] * self.np_ + ['baro'] + ['hubref'] * len(hubs))
        self.nest = np.concatenate([nest_of, -np.ones(self.nr, int)])
        self.hub = np.concatenate([hub_of, [-1], hubs])
        self.bhat = bhat
        self.centres = centres
        Fp = bilinear(pz, n) @ Gfw
        self.F = np.vstack([Fp, np.zeros((self.nr, n * n))])
        scale = HEAD_SD ** 2 / np.mean(np.einsum('ij,jk,ik->i', Fp, C0, Fp))
        self.C = C0 * scale
        self.K = self.F @ self.C @ self.F.T
        self.K = 0.5 * (self.K + self.K.T)
        gx = (np.arange(n) + 0.5) / n
        X, Y = np.meshgrid(gx, gx)
        x0, x1, y0, y1 = WELLFIELD
        cq = ((X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)).ravel().astype(float)
        self.cq = cq / cq.sum()
        self.z = self.F @ (self.C @ self.cq)              # covariance of the data with the goal q
        self.varq = float(self.cq @ self.C @ self.cq)
        piez = np.arange(self.np_)
        d = np.sqrt(((pz[:, None, :] - pz[None, :, :]) ** 2).sum(-1))
        self.dist = d
        self.Hm = np.zeros((self.n, len(hubs)))
        for c, h in enumerate(hubs):
            self.Hm[piez[hub_of == h], c] = 1.0
            self.Hm[self.np_ + 1 + c, c] = 1.0
        nests_ = sorted(set(nest_of.tolist()))
        self.Nm = np.zeros((self.n, len(nests_)))
        for c, k_ in enumerate(nests_):
            self.Nm[piez[nest_of == k_], c] = 1.0
        self.ps = slice(0, self.np_)
        self.nshape = 1 + self.np_                       # shape parameters: ell and the loading errors

    # ------------------------------------------------------------------------------------------------ noise model
    def loadings(self, delta):
        b = np.zeros(self.n)
        b[:self.np_] = self.bhat + delta
        b[self.np_] = 1.0
        return b

    def parts(self, amp, ell, delta):
        """The four parts of Gamma: independent, correctable, nest cross-talk, model error."""
        ss, sa, sh, sn, tau = amp
        Dd = np.empty(self.n)
        Dd[:self.np_] = (ss * SIG0) ** 2
        Dd[self.np_] = SIGB ** 2
        Dd[self.np_ + 1:] = SIGR ** 2
        b = self.loadings(delta)
        Gc = sa ** 2 * np.outer(b, b) + sh ** 2 * self.Hm @ self.Hm.T
        Gn = sn ** 2 * self.Nm @ self.Nm.T
        Ge = np.zeros((self.n, self.n))
        Ge[:self.np_, :self.np_] = tau ** 2 * np.exp(-self.dist / ell)
        return np.diag(Dd), Gc, Gn, Ge

    def gamma(self, th):
        amp, ell, delta = th[:5], th[5], th[6:]
        D, Gc, Gn, Ge = self.parts(amp, ell, delta)
        G = D + Gc + Gn + Ge
        return 0.5 * (G + G.T)

    def dgamma_shape(self, th):
        """Derivatives of Gamma with respect to ell and to each loading error delta_i (Proposition N3)."""
        sa, tau, ell = th[1], th[4], th[5]
        dE = np.zeros((self.n, self.n))
        dE[:self.np_, :self.np_] = tau ** 2 * np.exp(-self.dist / ell) * self.dist / ell ** 2
        return dE, sa ** 2, self.loadings(th[6:])

    def theta(self, amp, ell, delta):
        return np.concatenate([amp, [ell], delta])


def noncorrectable(bed, th):
    D, Gc, Gn, Ge = bed.parts(th[:5], th[5], th[6:])
    return D + Gn + Ge


def nominal(bed):
    return bed.theta(NOM[:5], NOM[5], np.zeros(bed.np_))


def upper_amp():
    return HI[:5].copy()


# ------------------------------------------------------------------------------------------- criteria in data space
def eig(K, G, S):
    S = list(S)
    if not S:
        return 0.0
    Ks, Gs = K[np.ix_(S, S)], G[np.ix_(S, S)]
    return 0.5 * (np.linalg.slogdet(Gs + Ks)[1] - np.linalg.slogdet(Gs)[1])


def eig_naive(K, Ginv, S):
    """The naive weighting of correlated noise: the S-block of the inverse (Certified OED, Proposition 14)."""
    S = list(S)
    if not S:
        return 0.0
    return 0.5 * np.linalg.slogdet(np.eye(len(S)) + Ginv[np.ix_(S, S)] @ K[np.ix_(S, S)])[1]


def gains(K, G, S, cand):
    """EIG(S + j) - EIG(S) for all j in cand, by the two Schur complements (exact)."""
    cand = np.asarray(cand)
    A = G + K
    if len(S) == 0:
        return 0.5 * (np.log(np.diag(A)[cand]) - np.log(np.diag(G)[cand]))
    S = list(S)
    Ass, Gss = A[np.ix_(S, S)], G[np.ix_(S, S)]
    XA = np.linalg.solve(Ass, A[np.ix_(S, cand)])
    XG = np.linalg.solve(Gss, G[np.ix_(S, cand)])
    a = np.diag(A)[cand] - np.einsum('ij,ij->j', A[np.ix_(S, cand)], XA)
    b = np.diag(G)[cand] - np.einsum('ij,ij->j', G[np.ix_(S, cand)], XG)
    return 0.5 * (np.log(a) - np.log(b))


def goal_var(bed, G, S):
    S = list(S)
    if not S:
        return bed.varq
    zs = bed.z[S]
    return float(bed.varq - zs @ np.linalg.solve(bed.K[np.ix_(S, S)] + G[np.ix_(S, S)], zs))


def eig_grad_shape(bed, th, S):
    """Exact gradient of EIG(S, theta) with respect to (ell, delta): 1/2 tr[((G+K)^-1 - G^-1) dG] (Proposition N3)."""
    G = bed.gamma(th)
    S = np.array(sorted(S))
    Gs, Ks = G[np.ix_(S, S)], bed.K[np.ix_(S, S)]
    M = np.linalg.inv(Gs + Ks) - np.linalg.inv(Gs)
    dE, sa2, b = bed.dgamma_shape(th)
    g = np.zeros(bed.nshape)
    g[0] = 0.5 * np.sum(M * dE[np.ix_(S, S)])
    Mb = M @ b[S]
    for pos, i in enumerate(S):
        if i < bed.np_:
            g[1 + i] = sa2 * Mb[pos]
    val = 0.5 * (np.linalg.slogdet(Gs + Ks)[1] - np.linalg.slogdet(Gs)[1])
    return val, g


# --------------------------------------------------------------------------------------------- design algorithms
def greedy(K, Gs, k, cand, crit='exact', Ginvs=None):
    """Greedy max-min over the scenario covariances Gs (one entry = nominal greedy)."""
    S = []
    cand = list(cand)
    for _ in range(k):
        rest = [j for j in cand if j not in S]
        if crit == 'exact':
            vals = np.min([eig(K, G, S) + gains(K, G, S, rest) for G in Gs], axis=0)
        else:
            vals = np.array([min(eig_naive(K, Gi, S + [j]) for Gi in Ginvs) for j in rest])
        S.append(rest[int(np.argmax(vals))])
    return S


def robust_value(K, Gs, S):
    return min(eig(K, G, S) for G in Gs)


def exchange(K, Gs, S, cand, max_pass=30):
    """Swap one selected and one unselected candidate while the robust value improves (first improvement)."""
    S = list(S)
    best = robust_value(K, Gs, S)
    for _ in range(max_pass):
        improved = False
        for i in list(S):
            base = [s for s in S if s != i]
            rest = [j for j in cand if j not in S]
            vals = np.min([eig(K, G, base) + gains(K, G, base, rest) for G in Gs], axis=0)
            j = int(np.argmax(vals))
            if vals[j] > best + 1e-9:
                S = base + [rest[j]]
                best = float(vals[j])
                improved = True
        if not improved:
            break
    return S, best


def adversary(bed, S, amp, starts, rng, n_rand=6):
    """Worst shape parameters (ell, delta) for design S with amplitudes amp, by L-BFGS-B with exact gradients."""
    lo = np.concatenate([[LO[5]], -DELTA * np.ones(bed.np_)])
    hi = np.concatenate([[HI[5]], DELTA * np.ones(bed.np_)])
    x0s = [s for s in starts]
    for _ in range(n_rand):
        x0s.append(np.concatenate([[rng.uniform(LO[5], HI[5])], rng.uniform(-DELTA, DELTA, bed.np_)]))

    def f(x):
        th = np.concatenate([amp, x])
        v, g = eig_grad_shape(bed, th, S)
        return v, g

    best = None
    for x0 in x0s:
        r = minimize(f, np.clip(x0, lo, hi), jac=True, method='L-BFGS-B', bounds=list(zip(lo, hi)),
                     options=dict(maxiter=200))
        if best is None or r.fun < best[0]:
            best = (float(r.fun), r.x.copy())
    return best


def initial_scenarios(bed, amp):
    """Scenario set: the three ends of ell with zero loading error, and the two uniform loading shifts."""
    sc = []
    for ell in (LO[5], NOM[5], HI[5]):
        sc.append(np.concatenate([[ell], np.zeros(bed.np_)]))
    for s in (-1, 1):
        sc.append(np.concatenate([[NOM[5]], s * DELTA * np.ones(bed.np_)]))
    return sc


def multistart(K, Gs, k, cand, starts):
    """Exchange from the robust greedy design and from each warm start; keep the best robust value."""
    best = None
    for S0 in [greedy(K, Gs, k, cand)] + [list(s) for s in starts]:
        S0 = [s for s in S0 if s in cand]
        rest = [j for j in cand if j not in S0]
        while len(S0) < k:                       # pad a warm start that lost candidates
            g = np.min([eig(K, G, S0) + gains(K, G, S0, rest) for G in Gs], axis=0)
            S0.append(rest.pop(int(np.argmax(g))))
        S, v = exchange(K, Gs, S0, cand)
        if best is None or v > best[1] + 1e-12:
            best = (S, v)
    return best


def nderhyrja(bed, k, cand=None, rng=None, max_rounds=12, verbose=False, starts=()):
    """NDERHYRJA-GO: amplitudes at the upper ends (Proposition N3), robust greedy and exchange (multi-start),
    adversary on the shape parameters, repeat until the adversary finds nothing worse."""
    rng = np.random.default_rng(1) if rng is None else rng
    cand = list(range(bed.n)) if cand is None else list(cand)
    amp = upper_amp()
    shapes = initial_scenarios(bed, amp)
    Gs = [bed.gamma(np.concatenate([amp, s])) for s in shapes]
    S, val = multistart(bed.K, Gs, k, cand, starts)
    rounds = 0
    for rounds in range(1, max_rounds + 1):
        x0 = [shapes[int(np.argmin([eig(bed.K, G, S) for G in Gs]))]]
        fv, x = adversary(bed, S, amp, x0, rng, n_rand=4)
        if fv < val - 1e-6:
            shapes.append(x)
            Gs.append(bed.gamma(np.concatenate([amp, x])))
            S, val = multistart(bed.K, Gs, k, cand, [S] + list(starts))
            if verbose:
                log(f'    round {rounds}: adversary {fv:.4f}, new robust value {val:.4f}')
        else:
            break
    Ges = [noncorrectable(bed, np.concatenate([amp, s_])) for s_ in shapes]
    return dict(S=sorted(S), val=val, shapes=shapes, Gs=Gs, Ges=Ges, rounds=rounds, amp=amp)


def worst_case(bed, S, extra_shapes, rng, n_rand=6):
    """Worst value of design S over the box: amplitudes at the upper ends, shapes by the adversary."""
    amp = upper_amp()
    vals = [eig(bed.K, bed.gamma(np.concatenate([amp, s])), S) for s in extra_shapes]
    starts = [extra_shapes[int(np.argmin(vals))]]
    fv, x = adversary(bed, S, amp, starts, rng, n_rand=n_rand)
    if min(vals) < fv:
        return float(min(vals)), extra_shapes[int(np.argmin(vals))]
    return fv, x


# -------------------------------------------------------------------------------- relaxation and robust certificate
def inflation(G):
    """Diagonal inflation R = t diag(G) with the largest t such that G - R is positive semidefinite."""
    d = np.diag(G)
    t = np.linalg.eigvalsh(G / np.sqrt(np.outer(d, d)))[0]
    return t * (1 - 1e-10) * d


def relax(w, G, K, r):
    """Noise-inflation relaxation with diagonal inflation r (Certified OED, eq. 36-39 and Appendix A.6):
    P_R(w) = (R + W(G - R))^-1 W; value and gradient of EIG_R(w) = 1/2 logdet(I + P_R(w) K)."""
    n = len(w)
    I = np.eye(n)
    r = np.broadcast_to(np.asarray(r, float), (n,))
    Mx = np.diag(r) + w[:, None] * (G - np.diag(r))
    U = np.linalg.inv(Mx)
    P = U * w[None, :]
    A = I + P @ K
    val = 0.5 * np.linalg.slogdet(A)[1]
    T = K @ np.linalg.solve(A, U)
    grad = 0.5 * r * np.einsum('ji,ji->i', U, T)
    return val, grad


def certificate(K, Gs, k, iters=150, tol=1e-4, Ges=None, fixed=None):
    """Kelley cutting planes for max over the capped simplex of min_theta of the relaxed criteria. Gs: scenario
    covariances (exact at binary designs); Ges: their non-correctable parts (correction ceiling, Proposition N2).
    Returns a certified upper bound on the robust k-sensor optimum over the scenario set (Proposition N4)."""
    n = K.shape[0]
    if Ges:      # G >= Ge, so the inflation valid for Ge is valid for G and much larger (Proposition N4)
        fams = [(G, inflation(Ge)) for G, Ge in zip(Gs, Ges)] + [(Ge, inflation(Ge)) for Ge in Ges]
    else:
        fams = [(G, inflation(G)) for G in Gs]
    cuts_A, cuts_b = [], []
    lb_, ub_ = np.zeros(n), np.ones(n)
    if fixed is not None:                         # candidates fixed at 0 or 1 (enumerated reference channels)
        for i, v in fixed.items():
            lb_[i] = ub_[i] = v
    free = ub_ > lb_
    w = lb_.copy()
    w[free] = (k - lb_.sum()) / free.sum()
    best_lb, ub = -np.inf, np.inf
    hist = []
    for it in range(iters):
        vals = []
        for G, r in fams:
            v, g = relax(w, G, K, r)
            vals.append(v)
            cuts_A.append(np.concatenate([-g, [1.0]]))      # t - g.v <= v - g.w
            cuts_b.append(v - g @ w)
        best_lb = max(best_lb, min(vals))
        res = linprog(np.concatenate([np.zeros(n), [-1.0]]), A_ub=np.array(cuts_A), b_ub=np.array(cuts_b),
                      A_eq=np.concatenate([np.ones(n), [0.0]])[None, :], b_eq=[k],
                      bounds=list(zip(lb_, ub_)) + [(None, None)], method='highs')
        ub = min(ub, -res.fun)
        hist.append((ub, best_lb))
        w = res.x[:n]
        if ub - best_lb < tol * max(1.0, abs(ub)):
            break
    return dict(ub=float(ub), relaxed_lb=float(best_lb), iters=it + 1, w=w, hist=hist)


# ---------------------------------------------------------------------------------------------------- self-checks
def self_checks(bed, rng):
    out = {}
    th = bed.theta(upper_amp(), 0.12, rng.uniform(-DELTA, DELTA, bed.np_))
    G = bed.gamma(th)
    K = bed.K
    # exact Schur gains
    S = list(rng.choice(bed.np_, 6, replace=False))
    rest = [j for j in range(bed.n) if j not in S]
    g = gains(K, G, S, rest)
    direct = np.array([eig(K, G, S + [j]) - eig(K, G, S) for j in rest])
    out['schur_gain_err'] = float(np.max(np.abs(g - direct)))
    # N1: value of the barometer, closed form; zero under the naive and the independent criteria
    r = bed.np_
    Gss, Ass = G[np.ix_(S, S)], G[np.ix_(S, S)] + K[np.ix_(S, S)]
    num = G[r, r] - G[r, S] @ np.linalg.solve(Ass, G[S, r])
    den = G[r, r] - G[r, S] @ np.linalg.solve(Gss, G[S, r])
    out['n1_closed_form_err'] = float(abs(0.5 * np.log(num / den) - (eig(K, G, S + [r]) - eig(K, G, S))))
    Gi = np.linalg.inv(G)
    out['n1_naive_gain'] = float(abs(eig_naive(K, Gi, S + [r]) - eig_naive(K, Gi, S)))
    Gd = np.diag(np.diag(G))
    out['n1_indep_gain'] = float(abs(eig(K, Gd, S + [r]) - eig(K, Gd, S)))
    out['n1_alone'] = float(abs(eig(K, G, [r])))
    # N2: correction ceiling and its limit with noise-free references
    amp = th[:5]
    D, Gc, Gn, Ge = bed.parts(amp, th[5], th[6:])
    Ge_all = D + Gn + Ge
    R = list(range(bed.np_, bed.n))
    ceil = eig(K, Ge_all, S)
    out['n2_with_refs'] = float(eig(K, G, S + R))
    out['n2_ceiling'] = float(ceil)
    out['n2_without_refs'] = float(eig(K, G, S))
    lim = []
    for eps in (1e-1, 1e-2, 1e-3, 1e-4):
        G2 = G.copy()
        for i in R:
            G2[i, i] = G[i, i] - D[i, i] + (eps * D[i, i])
        lim.append(float(ceil - eig(K, G2, S + R)))
    out['n2_limit_gaps'] = lim
    # N2(i): the marginal posterior mean equals the interference-free formula applied to the corrected data
    T = S + R
    d = rng.standard_normal(len(T))
    A = K[np.ix_(T, T)] + G[np.ix_(T, T)]
    Ae = K[np.ix_(T, T)] + Ge_all[np.ix_(T, T)]
    chat_term = Gc[np.ix_(T, T)] @ np.linalg.solve(A, d)          # B_S c_hat
    lhs = bed.F[T].T @ np.linalg.solve(A, d)
    rhs = bed.F[T].T @ np.linalg.solve(Ae, d - chat_term)
    out['n2_corrected_mean_err'] = float(np.max(np.abs(bed.C @ (lhs - rhs))) / np.max(np.abs(bed.C @ lhs)))
    # identity: penalty = I(m; c | y_S) = EIG_e(S) - EIG(S) >= 0 for random designs
    pen = []
    for _ in range(50):
        S2 = list(rng.choice(bed.np_, 8, replace=False))
        pen.append(eig(K, Ge_all, S2) - eig(K, G, S2))
    out['n2_min_penalty'] = float(min(pen))
    # N3: shape gradient against finite differences; amplitude monotonicity
    v, gr = eig_grad_shape(bed, th, S)
    fd = []
    for idx in [0, 1 + S[0], 1 + S[1], 1 + S[2]]:
        e = np.zeros_like(th)
        e[5 + idx] = 1e-6
        fd.append((eig(K, bed.gamma(th + e), S) - eig(K, bed.gamma(th - e), S)) / 2e-6 - gr[idx])
    out['n3_grad_err'] = float(np.max(np.abs(fd)))
    mono = []
    for a in range(5):
        e = np.zeros_like(th)
        e[a] = 1e-6
        mono.append((eig(K, bed.gamma(th + e), S) - eig(K, bed.gamma(th - e), S)) / 2e-6)
    out['n3_amp_derivs_max'] = float(max(mono))
    # N4: relaxation exact at binary points, gradient check, concavity along segments
    rho = inflation(G)
    out['n4_inflation_t'] = float(rho[0] / G[0, 0])
    errs = []
    for _ in range(20):
        S2 = list(rng.choice(bed.n, 8, replace=False))
        w = np.zeros(bed.n)
        w[S2] = 1
        errs.append(abs(relax(w, G, K, rho)[0] - eig(K, G, S2)))
    out['n4_binary_err'] = float(max(errs))
    w = rng.uniform(0.05, 0.95, bed.n)
    v0, g0 = relax(w, G, K, rho)
    fd = []
    for i in range(5):
        e = np.zeros(bed.n)
        e[i] = 1e-6
        fd.append((relax(w + e, G, K, rho)[0] - relax(w - e, G, K, rho)[0]) / 2e-6 - g0[i])
    out['n4_grad_err'] = float(np.max(np.abs(fd)))
    worst = -np.inf
    for _ in range(100):
        a, b = rng.uniform(0, 1, bed.n), rng.uniform(0, 1, bed.n)
        f = [relax(a + t * (b - a), G, K, rho)[0] for t in (0, 0.5, 1)]
        worst = max(worst, f[0] + f[2] - 2 * f[1])
    out['n4_max_second_diff'] = float(worst)
    return out


# --------------------------------------------------------------------------------------------------------- tests
def t33(bed, rng):
    """Reference sensors: value of the barometer and of a hub reference against the number of piezometers."""
    th0 = nominal(bed)
    G = bed.gamma(th0)
    K = bed.K
    Gi = np.linalg.inv(G)
    Gd = np.diag(np.diag(G))
    order = greedy(K, [G], 16, range(bed.np_))
    baro, hub0 = bed.np_, bed.np_ + 1
    rows = []
    for j in range(0, 17):
        S = order[:j]
        rows.append(dict(n=j, baro=float(eig(K, G, S + [baro]) - eig(K, G, S)),
                         hub=float(eig(K, G, S + [hub0]) - eig(K, G, S)),
                         both=float(eig(K, G, S + list(range(bed.np_, bed.n))) - eig(K, G, S)),
                         naive=float(eig_naive(K, Gi, S + [baro]) - eig_naive(K, Gi, S)),
                         indep=float(eig(K, Gd, S + [baro]) - eig(K, Gd, S))))
    return dict(curve=rows, order=[int(x) for x in order])


def designs_for_k(bed, k, rng):
    th0 = nominal(bed)
    G0 = bed.gamma(th0)
    K = bed.K
    allc = list(range(bed.n))
    piez = list(range(bed.np_))
    out = {}
    out['indep'] = greedy(K, [np.diag(np.diag(G0))], k, allc)
    out['naive'] = greedy(K, None, k, allc, crit='naive', Ginvs=[np.linalg.inv(G0)])
    S, _ = exchange(K, [G0], greedy(K, [G0], k, piez), piez)
    out['nominal_norefs'] = S
    S, _ = exchange(K, [G0], greedy(K, [G0], k, allc), allc)
    out['nominal'] = S
    rn = nderhyrja(bed, k, cand=piez, rng=rng, starts=[out['nominal_norefs']])
    out['robust_norefs'] = rn['S']
    r = nderhyrja(bed, k, rng=rng, starts=[out['nominal'], out['robust_norefs'], out['nominal_norefs']])
    out['nderhyrja'] = r['S']
    return out, r, rn


def evaluate(bed, S, shapes, rng):
    th0 = nominal(bed)
    G0 = bed.gamma(th0)
    amp = upper_amp()
    wv, ws = worst_case(bed, S, shapes, rng)
    Gw = bed.gamma(np.concatenate([amp, ws]))
    D, Gc, Gn, Ge = bed.parts(NOM[:5], NOM[5], np.zeros(bed.np_))
    piez = [s for s in S if s < bed.np_]
    return dict(S=[int(s) for s in sorted(S)], nrefs=int(sum(s >= bed.np_ for s in S)),
                nominal=float(eig(bed.K, G0, S)), worst=float(wv),
                naive_claim=float(eig_naive(bed.K, np.linalg.inv(G0), S)),
                ceiling=float(eig(bed.K, D + Gn + Ge, piez)),
                sdq_nominal=float(np.sqrt(goal_var(bed, G0, S))), sdq_worst=float(np.sqrt(goal_var(bed, Gw, S))),
                worst_shape=[float(x) for x in ws[:1]])


def t36(bed, designs, rng, R=2000):
    """Monte Carlo: the wellfield forecast q and the corrected heads under random interference in the box."""
    Lc = np.linalg.cholesky(bed.C + 1e-12 * np.eye(bed.C.shape[0]))
    th0 = nominal(bed)
    G0 = bed.gamma(th0)
    amp = upper_amp()
    # robust inference model: amplitudes at the upper ends, loading errors as random (variance DELTA^2/3)
    Gup = bed.gamma(np.concatenate([amp, [NOM[5]], np.zeros(bed.np_)]))
    Grob = Gup.copy()
    b0 = bed.loadings(np.zeros(bed.np_))
    Grob[:bed.np_, :bed.np_] += amp[1] ** 2 * DELTA ** 2 / 3 * np.eye(bed.np_)
    Gign = np.diag(np.concatenate([np.full(bed.np_, SIG0 ** 2), [SIGB ** 2], np.full(bed.nr, SIGR ** 2)]))
    models = dict(ignore=Gign, nominal=G0, robust=Grob)
    stats = {d: {m: dict(cover=0, se=0.0, width=0.0, rmse_raw=0.0, rmse_cor=0.0) for m in models} for d in designs}
    zq = 1.6448536269514722
    for r in range(R):
        lo, hi = LO.copy(), HI.copy()
        th = np.concatenate([rng.uniform(lo[:5], hi[:5]), [rng.uniform(LO[5], HI[5])],
                             rng.uniform(-DELTA, DELTA, bed.np_)])
        m = Lc @ rng.standard_normal(Lc.shape[0])
        h = bed.F @ m
        q = bed.cq @ m
        D, Gc, Gn, Ge = bed.parts(th[:5], th[5], th[6:])
        b = bed.loadings(th[6:])
        ca = th[1] * rng.standard_normal()
        ch = th[2] * rng.standard_normal(bed.Hm.shape[1])
        cn = th[3] * rng.standard_normal(bed.Nm.shape[1])
        ie = b * ca + bed.Hm @ ch                         # correctable interference
        e = np.sqrt(np.diag(D)) * rng.standard_normal(bed.n) + bed.Nm @ cn
        Le = np.linalg.cholesky(Ge[:bed.np_, :bed.np_] + 1e-14 * np.eye(bed.np_))
        e[:bed.np_] += Le @ rng.standard_normal(bed.np_)
        y = h + ie + e
        for dname, S in designs.items():
            S = np.array(S)
            P = S[S < bed.np_]
            for mname, G in models.items():
                A = bed.K[np.ix_(S, S)] + G[np.ix_(S, S)]
                sol = np.linalg.solve(A, y[S])
                mu = bed.z[S] @ sol
                var = bed.varq - bed.z[S] @ np.linalg.solve(A, bed.z[S])
                sd = np.sqrt(max(var, 1e-16))
                st = stats[dname][mname]
                st['cover'] += abs(q - mu) <= zq * sd
                st['se'] += (q - mu) ** 2
                st['width'] += 2 * zq * sd
                # corrected heads: subtract the posterior mean of the correctable interference
                if mname == 'ignore':
                    ihat = np.zeros(len(S))
                else:
                    amp_m = amp if mname == 'robust' else NOM[:5]
                    Gc_m = amp_m[1] ** 2 * np.outer(b0, b0) + amp_m[2] ** 2 * bed.Hm @ bed.Hm.T
                    ihat = Gc_m[np.ix_(S, S)] @ sol
                pos = np.isin(S, P)
                st['rmse_raw'] += np.mean((y[P] - h[P]) ** 2)
                st['rmse_cor'] += np.mean((y[S][pos] - ihat[pos] - h[P]) ** 2)
    out = {}
    for d in designs:
        out[d] = {}
        for mname in models:
            st = stats[d][mname]
            out[d][mname] = dict(coverage=st['cover'] / R, rmse_q=float(np.sqrt(st['se'] / R)),
                                 width=st['width'] / R, rmse_heads_raw=float(np.sqrt(st['rmse_raw'] / R)),
                                 rmse_heads_corrected=float(np.sqrt(st['rmse_cor'] / R)))
    out['sd_q_prior'] = float(np.sqrt(bed.varq))
    return out


def series_demo(bed, S, rng, T=120):
    """One season of daily heads at one piezometer: raw, corrected by the selected reference channels, true."""
    th0 = nominal(bed)
    G0 = bed.gamma(th0)
    S = np.array(sorted(S))
    P = S[S < bed.np_]
    i0 = int(P[0])
    pa = np.zeros(T)
    for t in range(1, T):
        pa[t] = 0.8 * pa[t - 1] + np.sqrt(1 - 0.8 ** 2) * NOM[1] * rng.standard_normal()
    drift = np.cumsum(rng.standard_normal((T, bed.Hm.shape[1])), axis=0)
    drift = NOM[2] * drift / np.std(drift, axis=0, keepdims=True)
    trend = 0.15 * np.sin(2 * np.pi * np.arange(T) / T)
    b = bed.loadings(np.zeros(bed.np_))
    raw, cor, true = [], [], []
    Ss = bed.K[np.ix_(S, S)] + G0[np.ix_(S, S)]
    Gc = NOM[1] ** 2 * np.outer(b, b) + NOM[2] ** 2 * bed.Hm @ bed.Hm.T
    Lc = np.linalg.cholesky(bed.C + 1e-12 * np.eye(bed.C.shape[0]))
    m = Lc @ rng.standard_normal(Lc.shape[0])
    for t in range(T):
        h = bed.F @ m * (1 + trend[t])
        y = h + b * pa[t] + bed.Hm @ drift[t] + SIG0 * rng.standard_normal(bed.n) * (np.arange(bed.n) < bed.np_)
        y[bed.np_:] += np.concatenate([[SIGB], np.full(bed.nr - 1, SIGR)]) * rng.standard_normal(bed.nr)
        ihat = Gc[np.ix_(S, S)] @ np.linalg.solve(Ss, y[S])
        k0 = int(np.where(S == i0)[0][0])
        raw.append(y[i0]); cor.append(y[i0] - ihat[k0]); true.append(h[i0])
    return dict(sensor=i0, raw=raw, corrected=cor, true=true, pa=pa.tolist())


def certificate_enum(bed, Gs, Ges, k, iters=100):
    """Certified bound with the reference channels enumerated (2^5 sets) and only the piezometers relaxed."""
    refs = list(range(bed.np_, bed.n))
    best, per = -np.inf, []
    for r in range(len(refs) + 1):
        for R0 in itertools.combinations(refs, r):
            if r > k:
                continue
            fixed = {i: (1.0 if i in R0 else 0.0) for i in refs}
            c = certificate(bed.K, Gs, k, iters=iters, Ges=Ges, fixed=fixed)
            per.append((list(R0), c['ub']))
            best = max(best, c['ub'])
    return dict(ub=float(best), per=per)


def t35_small(rng):
    """Exhaustive check on a 14-candidate instance: 4 nests of one hub, the barometer and the hub reference."""
    bed = Bed(nests=[0, 1, 4, 5])
    out = []
    for k in (3, 4, 5, 6):
        r = nderhyrja(bed, k, rng=rng)
        Gs = r['Gs']
        best, bestS = -np.inf, None
        for S in itertools.combinations(range(bed.n), k):
            v = robust_value(bed.K, Gs, S)
            if v > best:
                best, bestS = v, S
        cert = certificate_enum(bed, Gs, r['Ges'], k, iters=150)
        out.append(dict(k=k, n=bed.n, greedy_exchange=float(r['val']), exhaustive=float(best),
                        exhaustive_S=[int(x) for x in bestS], S=[int(x) for x in r['S']], ub=cert['ub'],
                        scenarios=len(Gs), subsets=int(sum(1 for _ in itertools.combinations(range(bed.n), k)))))
        log(f"  T35 small k={k}: greedy+exchange {r['val']:.4f}, exhaustive {best:.4f}, certificate {cert['ub']:.4f}")
    return out


def main():
    t0 = time.time()
    rng = np.random.default_rng(2026)
    bed = Bed()
    log(f'bed: {bed.np_} piezometers, {bed.nr} reference channels, var(q)^0.5 = {np.sqrt(bed.varq):.4f} m')
    R = {}
    R['bed'] = dict(n_piezo=bed.np_, n_ref=bed.nr, sd_q=float(np.sqrt(bed.varq)), sig0=SIG0, sigb=SIGB, sigr=SIGR,
                    lo=LO.tolist(), hi=HI.tolist(), nom=NOM.tolist(), delta=DELTA, head_sd=HEAD_SD,
                    wellfield=WELLFIELD, bhat=[float(x) for x in bed.bhat])
    R['checks'] = self_checks(bed, rng)
    log('self-checks:', json.dumps(R['checks']))
    R['t33'] = t33(bed, rng)
    log('T33 barometer gain at n = 0, 4, 8, 16:', [round(R['t33']['curve'][j]['baro'], 4) for j in (0, 4, 8, 16)])
    ks = (4, 8, 12) if QUICK else (4, 6, 8, 10, 12, 14, 16)
    R['t34'], R['t35'] = {}, {}
    keep = {}
    for k in ks:
        tk = time.time()
        ds, r, rn = designs_for_k(bed, k, rng)
        shapes = r['shapes'] + rn['shapes'][len(initial_scenarios(bed, None)):]
        ev = {name: evaluate(bed, S, shapes, rng) for name, S in ds.items()}
        it = 40 if QUICK else 150
        cert0 = certificate(bed.K, r['Gs'], k, iters=it)                        # relaxation alone
        cert1 = certificate(bed.K, r['Gs'], k, iters=it, Ges=r['Ges'])          # + correction ceiling
        cert = certificate_enum(bed, r['Gs'], r['Ges'], k, iters=30 if QUICK else 100)   # + enumerated references
        certn = certificate(bed.K, rn['Gs'], k, iters=it, Ges=rn['Ges'],
                            fixed={i: 0.0 for i in range(bed.np_, bed.n)})
        R['t34'][str(k)] = ev
        R['t35'][str(k)] = dict(ub=cert['ub'], ub_plain=cert0['ub'], ub_ceiling=cert1['ub'], val=r['val'],
                                rounds=r['rounds'], scenarios=len(r['Gs']), gap=cert['ub'] - r['val'],
                                gap_pct=100 * (cert['ub'] - r['val']) / cert['ub'], hist=cert1['hist'][::5],
                                ub_norefs=certn['ub'], val_norefs=rn['val'],
                                gap_norefs_pct=100 * (certn['ub'] - rn['val']) / certn['ub'],
                                per_refset=[(a, float(b)) for a, b in cert['per']])
        keep[k] = ds
        log(f"k={k:2d} ({time.time() - tk:.0f}s): " + ', '.join(
            f"{n_}: nom {e['nominal']:.2f} worst {e['worst']:.2f} refs {e['nrefs']}" for n_, e in ev.items()))
        log(f"      certificate {cert['ub']:.3f} vs robust value {r['val']:.3f} "
            f"(gap {R['t35'][str(k)]['gap_pct']:.1f}%, {len(r['Gs'])} scenarios, {r['rounds']} rounds)")
    R['t35_small'] = t35_small(rng)
    kd = 10 if 10 in keep else ks[len(ks) // 2]
    R['t36'] = t36(bed, {d: keep[kd][d] for d in ('indep', 'nominal_norefs', 'nderhyrja')}, rng,
                   R=400 if QUICK else 2000)
    R['t36']['k'] = kd
    log('T36:', json.dumps({d: {m: (round(v['coverage'], 3), round(v['rmse_q'], 4)) for m, v in x.items()}
                            for d, x in R['t36'].items() if isinstance(x, dict)}))
    R['series'] = series_demo(bed, keep[kd]['nderhyrja'], rng)
    R['time_s'] = time.time() - t0
    os.makedirs(RES, exist_ok=True)
    with open(os.path.join(RES, 'nderhyrja.json'), 'w') as fh:
        json.dump(R, fh, indent=1)
    np.savez(os.path.join(RES, 'nderhyrja_case.npz'), xy=bed.xy, kind=bed.kind, nest=bed.nest, hub=bed.hub,
             centres=bed.centres, bhat=bed.bhat, z=bed.z, Kdiag=np.diag(bed.K))
    with open(os.path.join(RES, 'nderhyrja_log.txt'), 'w') as fh:
        fh.write('\n'.join(LOG) + '\n')
    log(f'done in {R["time_s"]:.0f} s')


if __name__ == '__main__':
    main()
