"""RRJEDHA-GO: does transfer entropy from pumping to the saltwater toe measure causal information flow?

Physics: the KRAMERS-GO toe model (kramers2.py), X = x_toe/d relaxing as
    dX/dt = (mu/r - F(X; lam/r)) / tau,  r = exp(eps - s^2/2),  eps an OU recharge process,
with lam = f(A) lam_crit, A = 1 (high pumping f_hi) or 0 (low pumping f_lo).

Annual decisions t = 0..T-1 for each well. At the start of year t the operator sees a coarse toe alarm
level R_t (the reading X_t + noise, in 4 bins) and a drought category D_t (mean eps over the past half
year, in 3 bins: dry / normal / wet) and chooses A_t with
    logit P(A_t = 1) = b1 (2 A_{t-1} - 1) + bR[R_t] + bD[D_t].
The outcome of the year is the toe change dX_t = X_{t+1} - X_t, in 3 bins (retreat / steady / advance).
Drought both raises pumping and pushes the toe inland: confounding.

Because the toe is deterministic given the recharge path, each well-year is also run under A_t = 0 and
A_t = 1 with the same recharge (twin worlds, a one-year intervention), which gives the interventional
distributions P(dX | do(A = a), R = r) exactly.

Quantities (bits):
  TE_obs   = I(dX; A | R)                    standard transfer entropy with the toe history
  TE_cond  = I(dX; A | R, D, A_prev)         transfer entropy conditioned on the decision log
  TE_do    = sum_r p(r) sum_a pi(a|r) KL( P(dX|do a, r) || sum_a' pi(a'|r) P(dX|do a', r) )
             interventional information flow (Ay-Polani type) for the operator's toe rule pi(a|r)
  TE_adj   = TE_do with P(dX|do a, r) = sum_{d,ap} P(dX|a,r,d,ap) P(d,ap|r)   (back-door adjustment)
PID (Williams-Beer I_min, and BROJA by constrained optimization) of I(dX; A, D) into redundancy, unique and synergy, for observational A and
for A assigned at random (twin outcomes with weight 1/2).
"""
import os
import sys
import numpy as np
from scipy.optimize import brentq
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kramers_go'))   # kramers2.py
import kramers2 as KR

P = dict(KR.P0); P['s'] = 0.30
MU = KR.mu_of(P); LC = KR.lam_crit(MU)
F_LO, F_HI, F_PRE = 0.80, 0.95, 0.85
DT, STEPS = 0.02, 50                         # one year
T = 10
SIG_R = 0.02
R_EDGES = np.array([0.60, 0.64, 0.68])       # alarm levels 0..3
B1 = 2.0
BR = np.array([0.6, 0.0, -1.0, -2.0])
BD = np.array([1.2, 0.0, -0.8])              # dry, normal, wet
X0 = brentq(lambda X: KR.F(X, F_PRE * LC) - MU, 1e-9, np.sqrt(1 - F_PRE * LC))
BURN = 0.5


def expit(z):
    return 1.0 / (1.0 + np.exp(-z))


def year(X, eps, A, rng_z):
    """integrate one year for toe X (n,) under pumping A (n,), with OU noise increments rng_z (STEPS, n);
    returns X at the end and the eps path end and the window of eps for the drought index."""
    s, th = P['s'], P['theta']; a = np.exp(-DT / th); b = s * np.sqrt(1 - a * a)
    lam = np.where(A > 0.5, F_HI, F_LO) * LC
    e = eps.copy(); x = X.copy(); win = np.empty((STEPS, len(X)))
    for k in range(STEPS):
        r = np.exp(e - 0.5 * s * s)
        xn = x + DT * (MU / r - KR.F(x, lam / r)) / P['tau']
        x = np.where(x >= KR.XESC, x, np.clip(xn, KR.XLO, KR.XESC))
        e = a * e + b * rng_z[k]; win[k] = e
    return x, e, win


def simulate(n, rng, dbins=None, dxbins=None, policy='operator', pi_r=None):
    """n wells for T years. Returns per well-year records (alive at the start of the year) with the
    observed and both potential toe changes. policy 'operator' or 'random' (A ~ pi_r[R])."""
    s, th = P['s'], P['theta']; a = np.exp(-DT / th); b = s * np.sqrt(1 - a * a)
    eps = s * rng.standard_normal(n)
    nb = int(round(BURN / DT)); w = np.empty((nb, n))
    for k in range(nb):
        eps = a * eps + b * rng.standard_normal(n); w[k] = eps
    X = np.full(n, X0); Aprev = (rng.random(n) < 0.5).astype(float)
    rec = {k: [] for k in ('R', 'D', 'Dc', 'Aprev', 'A', 'dX', 'dX0', 'dX1', 'X', 'well')}
    wid = np.arange(n)
    for t in range(T):
        alive = X < KR.XESC
        R = np.digitize(X + SIG_R * rng.standard_normal(n), R_EDGES)
        Dc = w[-nb:].mean(axis=0)
        D = np.digitize(Dc, dbins) if dbins is not None else np.zeros(n, int)
        if policy == 'operator':
            pA = expit(B1 * (2 * Aprev - 1) + BR[R] + BD[D])
        else:
            pA = pi_r[R]
        A = (rng.random(n) < pA).astype(float)
        z = rng.standard_normal((STEPS, n))
        x0, e0, w0 = year(X, eps, np.zeros(n), z)
        x1, e1, w1 = year(X, eps, np.ones(n), z)
        for k, v in (('R', R), ('D', D), ('Dc', Dc), ('Aprev', Aprev), ('A', A), ('X', X), ('well', wid),
                     ('dX0', x0 - X), ('dX1', x1 - X), ('dX', np.where(A > 0.5, x1, x0) - X)):
            rec[k].append(v[alive])
        X = np.where(A > 0.5, x1, x0); eps = e0                 # same recharge path in both branches
        w = np.concatenate([w, w0])[-nb:]
        Aprev = A
    out = {k: np.concatenate(v) for k, v in rec.items()}
    if dxbins is not None:
        for k in ('dX', 'dX0', 'dX1'):
            out[k + 'b'] = np.digitize(out[k], dxbins)
    return out


# ------------------------------------------------------------------ information measures (bits)
def H(p):
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def joint(*cols, sizes, w=None):
    idx = np.ravel_multi_index(cols, sizes)
    c = np.bincount(idx, weights=w, minlength=int(np.prod(sizes))).astype(float)
    return (c / c.sum()).reshape(sizes)


def marg(p, axes):
    return p.sum(axis=tuple(a for a in range(p.ndim) if a not in axes)) if len(axes) < p.ndim else p


def cmi(p, x_ax, y_ax, z_axes):
    """I(X;Y|Z) in bits from a joint probability table p (axes indices)."""
    z = set(z_axes)
    hz = H(marg(p, z).ravel()) if z else 0.0
    return H(marg(p, z | {x_ax}).ravel()) + H(marg(p, z | {y_ax}).ravel()) - H(marg(p, z | {x_ax, y_ax}).ravel()) - hz


def te_do(pdo, pi, pr):
    """pdo[a, r, k] = P(dX = k | do a, r); pi[r, a]; pr[r]. Interventional information flow (bits)."""
    tot = 0.0
    for r in range(len(pr)):
        mix = (pi[r][:, None] * pdo[:, r, :]).sum(axis=0)
        for a in range(2):
            p = pdo[a, r]; m = (p > 0) & (pi[r, a] > 0)
            tot += pr[r] * pi[r, a] * float((p[m] * np.log2(p[m] / mix[m])).sum())
    return tot


def estimates(d, nR=4, nD=3, nK=3, alpha=0.5, idx=None):
    """plug-in estimates from observational well-years (rows idx); alpha = Dirichlet pseudo-count for the
    adjusted conditional distributions. te_adj adjusts for (D, A_prev); te_adj_noD for A_prev only."""
    sel = (lambda v: v) if idx is None else (lambda v: v[idx])
    R, D, Ap, A, K = sel(d['R']), sel(d['D']), sel(d['Aprev']).astype(int), sel(d['A']).astype(int), sel(d['dXb'])
    cnt = np.zeros((nK, 2, nR, nD, 2)); np.add.at(cnt, (K, A, R, D, Ap), 1)
    p = cnt / cnt.sum()
    out = dict(te_obs=cmi(p, 0, 1, [2]), te_cond=cmi(p, 0, 1, [2, 3, 4]))
    c_ar = cnt.sum(axis=(0, 3, 4))
    pi = (c_ar / np.maximum(c_ar.sum(axis=0, keepdims=True), 1e-12)).T
    pr = c_ar.sum(axis=0) / c_ar.sum()
    # adjustment for (D, A_prev)
    pk = (cnt + alpha / nK) / (cnt.sum(axis=0, keepdims=True) + alpha)
    c_rdap = cnt.sum(axis=(0, 1)); p_dap_r = c_rdap / np.maximum(c_rdap.sum(axis=(1, 2), keepdims=True), 1e-12)
    out['te_adj'] = te_do(np.einsum('karde,rde->ark', pk, p_dap_r), pi, pr)
    # adjustment for A_prev only (drought not recorded)
    c2 = cnt.sum(axis=3)
    pk2 = (c2 + alpha / nK) / (c2.sum(axis=0, keepdims=True) + alpha)
    c_rap = c2.sum(axis=(0, 1)); p_ap_r = c_rap / np.maximum(c_rap.sum(axis=1, keepdims=True), 1e-12)
    out['te_adj_noD'] = te_do(np.einsum('kare,re->ark', pk2, p_ap_r), pi, pr)
    return out


def truth(d, nR=4, nK=3):
    """population values from a large simulated sample with both potential outcomes."""
    R, A = d['R'], d['A'].astype(int)
    pdo = np.zeros((2, nR, nK))
    for a, key in ((0, 'dX0b'), (1, 'dX1b')):
        for r in range(nR):
            m = R == r
            pdo[a, r] = np.bincount(d[key][m], minlength=nK) / max(m.sum(), 1)
    c_ar = np.zeros((2, nR)); np.add.at(c_ar, (A, R), 1)
    pi = (c_ar / c_ar.sum(axis=0, keepdims=True)).T; pr = c_ar.sum(axis=0) / c_ar.sum()
    return dict(te_do=te_do(pdo, pi, pr), pdo=pdo, pi=pi, pr=pr)


def pid_imin(p):
    """Williams-Beer PID of I(T; S1, S2) from p[t, s1, s2] (bits): redundancy (I_min), uniques, synergy."""
    pt = p.sum(axis=(1, 2)); ps1 = p.sum(axis=(0, 2)); ps2 = p.sum(axis=(0, 1))
    pts1 = p.sum(axis=2); pts2 = p.sum(axis=1)

    def ispec(pts, ps):
        out = np.zeros(len(pt))
        for t in range(len(pt)):
            if pt[t] == 0:
                continue
            ps_t = pts[t] / pt[t]; pt_s = np.where(ps > 0, pts[t] / np.maximum(ps, 1e-300), 0)
            m = ps_t > 0
            out[t] = float((ps_t[m] * np.log2(pt_s[m] / pt[t])).sum())
        return out
    i1, i2 = ispec(pts1, ps1), ispec(pts2, ps2)
    red = float((pt * np.minimum(i1, i2)).sum())
    I1 = float((pt * i1).sum()); I2 = float((pt * i2).sum())
    I12 = H(pt) + H(p.sum(axis=0).ravel()) - H(p.ravel())
    return dict(red=red, uni1=I1 - red, uni2=I2 - red, syn=I12 - I1 - I2 + red, I1=I1, I2=I2, I12=I12)


def pid_broja(p, iters=500):
    """BROJA (Bertschinger-Rauh-Olbrich-Jost-Ay) PID of I(T; S1, S2) from p[t, s1, s2], in bits.
    UI(T; S1 \\ S2) = min over Q in Delta_P of I_Q(T; S1 | S2), where Delta_P keeps the (T,S1) and (T,S2)
    marginals of p. Q is parametrized as Q0 + B g with B a basis of the zero-marginal directions;
    SLSQP with the analytic gradient and the constraints Q >= 0."""
    from scipy.optimize import minimize
    from scipy.linalg import null_space
    nT, n1, n2 = p.shape
    m1 = p.sum(axis=2); m2 = p.sum(axis=1); pt = p.sum(axis=(1, 2))
    Q0 = (m1[:, :, None] * m2[:, None, :] / np.maximum(pt[:, None, None], 1e-300)).ravel()
    rows = []                                                 # marginal constraint matrix
    for t in range(nT):
        for a in range(n1):
            e = np.zeros(p.shape); e[t, a, :] = 1; rows.append(e.ravel())
        for b in range(n2):
            e = np.zeros(p.shape); e[t, :, b] = 1; rows.append(e.ravel())
    Bm = null_space(np.array(rows))

    def q_of(g):
        return np.maximum(Q0 + Bm @ g, 1e-18).reshape(p.shape)

    def f(g):
        q = q_of(g); q2 = q.sum(axis=0); qs2 = q.sum(axis=(0, 1)); qt2 = q.sum(axis=1)
        return float((q * np.log2(q * qs2[None, None, :] / (qt2[:, None, :] * q2[None, :, :]))).sum())

    def grad(g):
        q = q_of(g); q2 = q.sum(axis=0); qs2 = q.sum(axis=(0, 1)); qt2 = q.sum(axis=1)
        d = np.log2(q * qs2[None, None, :] / (qt2[:, None, :] * q2[None, :, :]))
        return Bm.T @ d.ravel()
    cons = [{'type': 'ineq', 'fun': lambda g: Q0 + Bm @ g, 'jac': lambda g: Bm}]
    r = minimize(f, np.zeros(Bm.shape[1]), jac=grad, method='SLSQP', constraints=cons,
                 options=dict(maxiter=iters, ftol=1e-14))
    uni1 = max(f(r.x), 0.0)
    I12 = H(pt) + H(p.sum(axis=0).ravel()) - H(p.ravel())
    I1 = H(pt) + H(m1.sum(axis=0)) - H(m1.ravel())
    I2 = H(pt) + H(m2.sum(axis=0)) - H(m2.ravel())
    red = I1 - uni1; uni2 = I2 - red; syn = I12 - uni1 - uni2 - red
    return dict(red=float(red), uni1=float(uni1), uni2=float(uni2), syn=float(syn), I1=float(I1), I2=float(I2),
                I12=float(I12), ok=bool(r.success))
