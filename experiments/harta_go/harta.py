"""HARTA-GO core: triangular transport maps for goal-oriented design on the Fushe-Kuqe model.

Ensemble columns: 0..15 heads at the 16 candidate monitoring wells, 16 head at supply well A,
17 head at supply well B, 18 intruded area of the coastal sector (km^2).
Goals (binary, as in PRAG-GO): rA = {h_A < 1 m}, rAB = {min(h_A, h_B) < 1 m}, rArea = {area > 12 km^2}.

The map. Every variable is first sent to a standard normal score by a monotone one-dimensional map
fitted on the training ensemble (the diagonal part of the transport). The lower block of a
lower-triangular (Knothe-Rosenblatt) map then gives the goal variables given the readings of a design d:
    z_g = m(z_d) + s(z_d) * xi,  xi ~ N(0, 1),
with m quadratic in the readings (and in z_A for the second goal variable of rAB) and log s(z_d)
linear: a monotone, invertible map component of the 'linear in the last variable' class. Because
every feature of every design is a column of one global quadratic feature matrix, each design's map
is fitted from sub-blocks of one Gram matrix (a few microseconds per design), so one pass over the
ensemble serves all 4 368 five-well designs. Other members of the family, for the ablation:
  'gauss'  raw (untransformed) variables, linear mean, constant spread: the ensemble Kalman conditional
  'ns'     normal scores, linear mean, constant spread: the Gaussian copula
  'harta'  normal scores, quadratic mean, spread depending on the readings
The expected information gain of a design is estimated by the Barber-Agakov bound with two-fold
cross-fitting: I(G; y_d) >= H(G) + E[log q(G | y_d)], with q the map's conditional.
"""
import numpy as np
from scipy.stats import norm
from scipy.special import ndtr, log_ndtr

NC, IA, IB, IR = 16, 16, 17, 18
SN, HC, AREA_T = 0.2, 1.0, 12.0
GOALS = ['rA', 'rAB', 'rArea']
LOGCHI = 1.2703628454614782          # -E[log chi^2_1]
glx, glw = np.polynomial.legendre.leggauss(16)
ghx, ghw = np.polynomial.hermite_e.hermegauss(16); ghw = ghw / ghw.sum()


def goal_of(E):
    """binary goals of ensemble rows (noise-free heads)."""
    return np.stack([E[:, IA] < HC, np.minimum(E[:, IA], E[:, IB]) < HC, E[:, IR] > AREA_T], 1)


def hb(p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -(p * np.log(p) + (1 - p) * np.log1p(-p))


class Marg:
    """monotone map x -> standard normal score, from the empirical CDF of a sample (ties averaged),
    linear interpolation inside the sample and linear extrapolation with the end slopes outside."""
    def __init__(self, x):
        xs = np.sort(np.asarray(x, float)); n = len(xs)
        q = norm.ppf((np.arange(1, n + 1) - 0.5) / n)
        u, inv = np.unique(xs, return_inverse=True)
        qq = np.bincount(inv, q) / np.bincount(inv)
        self.u, self.q = u, qq
        k = max(1, len(u) // 50)
        self.slo = (qq[k] - qq[0]) / max(u[k] - u[0], 1e-12)
        self.shi = (qq[-1] - qq[-1 - k]) / max(u[-1] - u[-1 - k], 1e-12)

    def __call__(self, x):
        x = np.asarray(x, float)
        z = np.interp(x, self.u, self.q)
        z = np.where(x < self.u[0], self.q[0] + self.slo * (x - self.u[0]), z)
        return np.where(x > self.u[-1], self.q[-1] + self.shi * (x - self.u[-1]), z)


class Space:
    """the diagonal part of the map: per-variable transforms fitted on a training set.
    kind 'ns' = normal scores; 'raw' = standardization only (no change of shape)."""
    def __init__(self, Y, E, kind):
        self.kind = kind
        cols = [Y[:, k] for k in range(NC)] + [E[:, IA], E[:, IB], E[:, IR]]
        if kind == 'ns':
            self.f = [Marg(c) for c in cols]
        else:
            self.f = [(lambda c: (lambda x, m=c.mean(), s=c.std(): (np.asarray(x, float) - m) / s))(c) for c in cols]
        self.tA = float(self.f[IA](HC)); self.tB = float(self.f[IB](HC)); self.tR = float(self.f[IR](AREA_T))

    def data(self, Y):
        return np.column_stack([self.f[k](Y[:, k]) for k in range(Y.shape[1])])

    def goals(self, E):
        return np.column_stack([self.f[IA](E[:, IA]), self.f[IB](E[:, IB]), self.f[IR](E[:, IR])])


# ------------------------------------------------------------------ global features and index sets
QK = [(k, l) for k in range(NC) for l in range(k, NC)]
QPOS = {kl: 1 + NC + i for i, kl in enumerate(QK)}
F0 = 1 + NC + len(QK)                     # 153 data features
IZA, IZA2 = F0, F0 + 1                    # z_A and z_A^2
IZAK = F0 + 2                             # z_A * z_k  (16 columns)
NF = F0 + 2 + NC


def features(Z, zA=None):
    """global quadratic features of latent readings Z (n x 16) and, optionally, of z_A."""
    n = Z.shape[0]
    P = np.empty((n, NF if zA is not None else F0))
    P[:, 0] = 1.0; P[:, 1:1 + NC] = Z
    for (k, l), j in QPOS.items():
        P[:, j] = Z[:, k] * Z[:, l]
    if zA is not None:
        P[:, IZA] = zA; P[:, IZA2] = zA * zA; P[:, IZAK:IZAK + NC] = Z * zA[:, None]
    return P


def idx_of(d, deg, withA=False):
    d = sorted(d)
    ix = [0] + [1 + k for k in d]
    if deg == 2:
        ix += [QPOS[(k, l)] for a, k in enumerate(d) for l in d[a:]]
    if withA:
        ix += [IZA] + ([IZA2] + [IZAK + k for k in d] if deg == 2 else [])
    return np.array(ix)


def lin_idx(d, withA=False):
    return np.array([0] + [1 + k for k in sorted(d)] + ([IZA] if withA else []))


class Fit:
    """sufficient statistics of one training fold for every design's map component."""
    def __init__(self, Zd, Zg, deg, hetero, lam=1e-6):
        self.deg, self.hetero, self.lam = deg, hetero, lam
        self.P = features(Zd, Zg[:, 0])
        self.G = self.P.T @ self.P
        self.c = self.P.T @ Zg                     # columns: z_A, z_B, z_R
        self.Zg = Zg; self.n = Zd.shape[0]

    def component(self, d, t, withA=False):
        """map component of goal variable t (0 = A, 1 = B, 2 = area) given design d: returns
        (beta, ix, gamma, lix) with mean P[:, ix] @ beta and log variance P[:, lix] @ gamma."""
        ix = idx_of(d, self.deg, withA)
        A = self.G[np.ix_(ix, ix)] + self.lam * self.n * np.eye(len(ix))
        beta = np.linalg.solve(A, self.c[ix, t])
        r = self.Zg[:, t] - self.P[:, ix] @ beta
        lix = lin_idx(d, withA)
        if self.hetero:
            L = self.P[:, lix]
            gamma = np.linalg.solve(self.G[np.ix_(lix, lix)] + 1e-8 * np.eye(len(lix)), L.T @ np.log(r * r + 1e-12))
            gamma[0] += LOGCHI
        else:
            gamma = np.zeros(len(lix)); gamma[0] = np.log(np.mean(r * r))
        return beta, ix, gamma, lix


def prob_goal(fit, d, goal, P, sp):
    """q(G = 1 | readings of design d). P = features(Z) of the latent readings (columns of d used)."""
    if goal in ('rA', 'rArea'):
        t, thr = (0, sp.tA) if goal == 'rA' else (2, sp.tR)
        beta, ix, gamma, lix = fit.component(d, t)
        m = P[:, ix] @ beta; s = np.exp(0.5 * (P[:, lix] @ gamma))
        return ndtr((thr - m) / s) if goal == 'rA' else ndtr((m - thr) / s)
    # rAB: P(no intrusion) = int_{z_A >= tA} P(z_B >= tB | z_d, z_A) dP(z_A | z_d)
    bA, iA_, gA, lA = fit.component(d, 0)
    bB, iB_, gB, lB = fit.component(d, 1, withA=True)
    mA = P[:, iA_] @ bA; sA = np.exp(0.5 * (P[:, lA] @ gA))
    # split the B component into its data part and its z_A part
    nd = len(idx_of(d, fit.deg)); dd = sorted(d)
    mB0 = P[:, iB_[:nd]] @ bB[:nd]
    bA1 = bB[nd]
    if fit.deg == 2:
        bA2 = bB[nd + 1]; bAk = P[:, [1 + k for k in dd]] @ bB[nd + 2:]
    else:
        bA2 = 0.0; bAk = 0.0
    lB0 = P[:, lB[:-1]] @ gB[:-1]; gzA = gB[-1]
    u0 = ndtr((sp.tA - mA) / sA)                         # P(z_A < tA)
    safe = np.zeros(len(mA))
    for x, w in zip(glx, glw):
        u = u0 + (1 - u0) * 0.5 * (x + 1)
        zA = mA + sA * norm.ppf(np.clip(u, 1e-12, 1 - 1e-12))
        mB = mB0 + zA * (bA1 + bAk) + bA2 * zA * zA
        sB = np.exp(0.5 * (lB0 + gzA * zA))
        safe += 0.5 * w * (1 - u0) * ndtr((mB - sp.tB) / sB)
    return 1 - safe


def logq(p, g):
    return np.log(np.clip(np.where(g, p, 1 - p), 1e-9, 1.0))


def eig_ba(Y, E, designs, goal, kind='ns', deg=2, hetero=True, seed=0):
    """cross-fitted Barber-Agakov EIG of every design (array of index tuples) for one goal."""
    n = len(Y); rng = np.random.default_rng(seed); perm = rng.permutation(n)
    folds = [perm[: n // 2], perm[n // 2:]]
    gi = GOALS.index(goal); Gall = goal_of(E)[:, gi]
    H0 = hb(Gall.mean())
    out = np.zeros(len(designs))
    for a, b in ((0, 1), (1, 0)):
        tr, te = folds[a], folds[b]
        sp = Space(Y[tr], E[tr], kind)
        fit = Fit(sp.data(Y[tr]), sp.goals(E[tr]), deg, hetero)
        Pte = features(sp.data(Y[te])); gte = Gall[te]
        for j, d in enumerate(designs):
            out[j] += 0.5 * (H0 + logq(prob_goal(fit, d, goal, Pte, sp), gte).mean())
    return out


def eig_rew(Gtr_heads, Gtr_goal, Yout, designs, chunk=500):
    """nested Monte Carlo (likelihood re-weighting) EIG: inner = noise-free heads of the inner ensemble,
    outer = noisy readings; plug-in posterior entropy. Gtr_goal may hold several goals (columns)."""
    g = np.atleast_2d(np.asarray(Gtr_goal, np.float64).T).T
    H0 = hb(g.mean(0)); out = np.zeros((len(designs), g.shape[1]))
    for j, d in enumerate(designs):
        d = list(d); acc = 0.0
        for s in range(0, len(Yout), chunk):
            yo = Yout[s:s + chunk, d]
            S = ((yo[:, None, :] - Gtr_heads[None, :, d]) ** 2).sum(-1)
            S -= S.min(1, keepdims=True)
            w = np.exp(-S / (2 * SN * SN))
            acc = acc + hb((w @ g) / w.sum(1)[:, None]).sum(0)
        out[j] = H0 - acc / len(Yout)
    return out
