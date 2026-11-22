"""MJEGULLA-GO: robust (likelihood-penalized) filtering of hidden salinization states of wells and goal-oriented
monitoring.

Hidden state of well i in season t: X = 0 fresh, 1 brackish, 2 saline. With a_i = alpha + beta*u_i - KAPPA*(d_i - 1)
(u_i = 1 for hard pumping, d_i the distance from the coast in km) and r_i = rho - ETA*u_i, one season moves a fresh
well up with probability sigmoid(a_i), a saline well down with probability sigmoid(r_i), and a brackish well up or down
with the multinomial-logit probabilities e^a/(1+e^a+e^r) and e^r/(1+e^a+e^r). Observation of a
sampled well: electrical-conductivity index Y = M[X] + SIGMA*eps. Unknown parameters theta = (alpha, beta, rho),
shared by all wells; KAPPA, ETA, M, SIGMA and the initial distribution are known (hydrogeology and instruments).

Goals: M, g(theta) = sum over the target (municipal) wells of P_theta(X_{T+H} = 2 | data), the expected number of
saline target wells H seasons after the end of monitoring; P, the expected number of saline wells at four planned
sites H_PLAN seasons after drilling (a function of theta alone).

Robust filter (Cohen 2020): upper / lower expectations of the goal over parameters in the box [LO, HI] penalized by
the log-likelihood ratio; with the hard penalty (gamma -> infinity) they are the max / min of g over
{theta: l(theta_hat) - l(theta) <= k}, with k = chi2_1(0.95)/2 for one goal (profile likelihood) or chi2_3(0.95)/2
for all goals jointly.
"""
import numpy as np
from scipy.stats import chi2

KAPPA, ETA = 1.0, 0.8
M = np.array([0.0, 1.0, 2.0])
SIGMA = 0.6
THETA_TRUE = np.array([-2.6, 1.4, -2.2])
LO = np.array([-7.0, -3.0, -7.0]); HI = np.array([2.0, 5.0, 2.0])
K_REGION = chi2.ppf(0.95, 3) / 2


def sig(x):
    return 1.0 / (1.0 + np.exp(-x))


SITES_D = np.array([0.9, 1.3, 1.7, 2.1])               # planned well sites (km from the coast), hard pumping
H_PLAN = 8                                              # seasons after drilling at which the planned sites are judged
K1 = chi2.ppf(0.95, 1) / 2                             # goal-specific penalty (profile likelihood of one goal)


def theta_draw(rng):
    """The aquifer's true parameters vary from field to field."""
    return np.array([rng.uniform(-3.2, -2.0), rng.uniform(0.8, 2.0), rng.uniform(-2.8, -1.6)])


def field(n, rng, n_target=6):
    """Wells: distance to the coast (km), pumping (1 = hard), target (municipal) wells, initial distribution."""
    d = np.sort(rng.uniform(0.3, 3.0, n))
    u = (rng.uniform(size=n) < 0.5).astype(float)
    tgt = np.sort(rng.choice(np.where((d > 0.8) & (d < 2.2))[0], n_target, replace=False))
    u[tgt] = 1.0                                    # municipal wells pump hard
    z = -1.2 * (d - 1.0)
    pi0 = np.stack([np.ones(n), sig(z - 1.0) * 1.2, sig(z - 2.5)], 1)
    pi0 = pi0 / pi0.sum(1, keepdims=True)
    return dict(d=d, u=u, tgt=tgt, pi0=pi0, n=n)


def trans(theta, F):
    """Transition matrices for a batch of theta: (K, n, 3, 3)."""
    th = np.atleast_2d(theta)
    a = th[:, [0]] + th[:, [1]] * F['u'][None] - KAPPA * (F['d'][None] - 1.0)
    r = th[:, [2]] - ETA * F['u'][None]
    up, dn = sig(a), sig(r)
    ea, er = np.exp(np.minimum(a, 30)), np.exp(np.minimum(r, 30))
    up1, dn1 = ea / (1 + ea + er), er / (1 + ea + er)      # brackish state: competing moves (multinomial logit)
    K, n = up.shape
    P = np.zeros((K, n, 3, 3))
    P[:, :, 0, 0] = 1 - up; P[:, :, 0, 1] = up
    P[:, :, 1, 0] = dn1; P[:, :, 1, 1] = 1 - up1 - dn1; P[:, :, 1, 2] = up1
    P[:, :, 2, 1] = dn; P[:, :, 2, 2] = 1 - dn
    return P


def simulate(F, T, H, rng, theta=THETA_TRUE):
    """True hidden states for seasons 0..T+H-1 and potential observations Y (T x n)."""
    P = trans(theta, F)[0]
    n = F['n']
    X = np.zeros((T + H, n), int)
    X[0] = [rng.choice(3, p=F['pi0'][i]) for i in range(n)]
    for t in range(1, T + H):
        for i in range(n):
            X[t, i] = rng.choice(3, p=P[i, X[t - 1, i]])
    Yall = M[X[:T]] + SIGMA * rng.standard_normal((T, n))
    return X, Yall


def lik_obs(y):
    return np.exp(-0.5 * ((y[..., None] - M) / SIGMA) ** 2) / (SIGMA * np.sqrt(2 * np.pi))


def filt(theta, F, Mask, Y, t_end=None):
    """Forward filter for a batch of theta, using observations of seasons 0..t_end-1 (Mask, Y are T x n).
    Returns log-likelihood (K,), filtered distribution at season t_end-1 (K, n, 3) and the transition matrices."""
    P = trans(theta, F)
    K = P.shape[0]
    T = Mask.shape[0] if t_end is None else t_end
    f = np.broadcast_to(F['pi0'], (K, F['n'], 3)).copy()
    ll = np.zeros(K)
    for t in range(T):
        if t > 0:
            f = np.einsum('kns,knsr->knr', f, P)
        obs = np.where(Mask[t])[0]
        if len(obs):
            L = lik_obs(Y[t, obs])                               # (m, 3)
            w = f[:, obs, :] * L[None]
            c = w.sum(-1)
            ll += np.log(c).sum(-1)
            f[:, obs, :] = w / c[..., None]
    return ll, f, P


def propagate(f, P, steps):
    for _ in range(steps):
        f = np.einsum('kns,knsr->knr', f, P)
    return f


def goal(theta, F, Mask, Y, t_now, T_end, H, kind='mon'):
    """kind 'mon': g(theta) = sum over the municipal wells of P(X_{T_end-1+H} = 2 | data up to season t_now-1);
    kind 'plan': g(theta) = sum over the planned sites of P(X_{H_PLAN} = 2 | fresh at drilling), a function of theta
    alone. Returns g and the log-likelihood of the data."""
    ll, f, P = filt(theta, F, Mask, Y, t_now)
    if kind == 'plan':
        return goal_plan(theta), ll
    fp = propagate(f, P, (T_end - t_now) + H)
    return fp[:, F['tgt'], 2].sum(-1), ll


def goal_plan(theta):
    Fs = dict(d=SITES_D, u=np.ones(len(SITES_D)), n=len(SITES_D))
    P = trans(theta, Fs)
    f = np.zeros(P.shape[:2] + (3,)); f[:, :, 0] = 1.0
    f = propagate(f, P, H_PLAN)
    return f[:, :, 2].sum(-1)


# ------------------------------------------------------------------------------------------------------------
# maximum likelihood and observed information by batched finite differences

def stencil(th, h):
    pts = [th.copy()]
    for j in range(3):
        for s in (1, -1):
            e = np.zeros(3); e[j] = s * h; pts.append(th + e)
    for j in range(3):
        for k in range(j + 1, 3):
            for sj, sk in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                e = np.zeros(3); e[j] = sj * h; e[k] = sk * h; pts.append(th + e)
    return np.array(pts)


def grad_hess(vals, h):
    f0 = vals[0]
    g = np.zeros(3); Hm = np.zeros((3, 3))
    for j in range(3):
        fp, fm = vals[1 + 2 * j], vals[2 + 2 * j]
        g[j] = (fp - fm) / (2 * h)
        Hm[j, j] = (fp - 2 * f0 + fm) / h ** 2
    idx = 7
    for j in range(3):
        for k in range(j + 1, 3):
            fpp, fpm, fmp, fmm = vals[idx:idx + 4]; idx += 4
            Hm[j, k] = Hm[k, j] = (fpp - fpm - fmp + fmm) / (4 * h * h)
    return g, Hm


def mle(F, Mask, Y, t_now, th0=None, iters=40, h=1e-3):
    """Damped Newton on the log-likelihood with the batched stencil; returns theta_hat, l(theta_hat), J (observed
    information = -Hessian)."""
    th = np.array([-2.0, 1.0, -2.0]) if th0 is None else np.clip(np.array(th0, float), LO + 0.1, HI - 0.1)
    lam = 1e-3
    best = None
    for _ in range(iters):
        ll = filt(stencil(th, h), F, Mask, Y, t_now)[0]
        g, Hm = grad_hess(ll, h)
        if best is None or ll[0] > best[1]:
            best = (th.copy(), ll[0], -Hm)
        A = -Hm + lam * np.eye(3)
        try:
            w, V = np.linalg.eigh(A)
            w = np.maximum(w, 1e-6 + 1e-3 * np.abs(w).max())
            step = V @ ((V.T @ g) / w)
        except np.linalg.LinAlgError:
            step = g * 0.1
        nrm = np.linalg.norm(step)
        if nrm > 1.5:
            step *= 1.5 / nrm
        improved = False
        for _ in range(8):
            th_new = np.clip(th + step, LO, HI)
            ll_new = filt(th_new, F, Mask, Y, t_now)[0][0]
            if ll_new >= ll[0] - 1e-10:
                th = th_new; improved = True
                break
            step *= 0.5
        if not improved or np.linalg.norm(step) < 1e-7:
            break
    ll = filt(stencil(th, h), F, Mask, Y, t_now)[0]
    g, Hm = grad_hess(ll, h)
    return th, ll[0], -Hm


# ------------------------------------------------------------------------------------------------------------
# robust interval over the likelihood region and its second-order prediction

def fib_sphere(m):
    i = np.arange(m) + 0.5
    phi = np.arccos(1 - 2 * i / m); th = np.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], 1)


BOXW = float((HI - LO).max())


def jmetric(J, k):
    """J^(-1/2) with the eigenvalues of J floored at 2k/BOXW^2: a ray of the likelihood region then never exceeds the
    width of the parameter box, so that a flat ridge of the likelihood is explored up to the box instead of
    swallowing every search direction."""
    w, V = np.linalg.eigh(0.5 * (J + J.T))
    w = np.maximum(w, 2.0 * k / BOXW ** 2)
    return V @ np.diag(w ** -0.5) @ V.T


def ray_box(th, U):
    """Largest t >= 0 such that th + t U stays in the parameter box, for each row of U."""
    with np.errstate(divide='ignore', invalid='ignore'):
        tl = np.where(U < 0, (LO - th) / U, np.inf)
        tu = np.where(U > 0, (HI - th) / U, np.inf)
    return np.maximum(np.minimum(tl, tu).min(1), 0.0)


def robust_interval(F, Mask, Y, t_now, T_end, H, th_hat, ll_hat, J, k=K_REGION, ndir=160, nbis=16, kind='mon'):
    """Max and min of g over the likelihood region {theta in the box: l(theta_hat) - l(theta) <= k} (the hard
    penalty): along each direction of the J-metric, bisection for the boundary of the region or the box, then g at
    three radii along the ray."""
    U = fib_sphere(ndir) @ jmetric(J, k).T
    hi = ray_box(th_hat, U)
    lo = np.zeros(ndir)
    a = ll_hat - filt(np.clip(th_hat + hi[:, None] * U, LO, HI), F, Mask, Y, t_now)[0]
    open_ray = a <= k                                   # the region reaches the box along this ray
    lo[open_ray] = hi[open_ray]
    for _ in range(nbis):
        mid = 0.5 * (lo + hi)
        a = ll_hat - filt(np.clip(th_hat + mid[:, None] * U, LO, HI), F, Mask, Y, t_now)[0]
        lo = np.where(~open_ray & (a <= k), mid, lo)
        hi = np.where(~open_ray & (a > k), mid, hi)
    pts = np.concatenate([th_hat + (lo * f)[:, None] * U for f in (1.0, 0.66, 0.33)], 0)
    pts = np.vstack([th_hat, np.clip(pts, LO, HI)])
    gv, _ = goal(pts, F, Mask, Y, t_now, T_end, H, kind)
    g_lo = refine(pts[np.argmin(gv)], -1.0, F, Mask, Y, t_now, T_end, H, ll_hat, k, kind)
    g_hi = refine(pts[np.argmax(gv)], 1.0, F, Mask, Y, t_now, T_end, H, ll_hat, k, kind)
    return min(gv.min(), g_lo), max(gv.max(), g_hi), gv[0]


PATTERN = np.vstack([np.eye(3), -np.eye(3), fib_sphere(20)])


def refine(th0, sign, F, Mask, Y, t_now, T_end, H, ll_hat, k, kind, iters=40, step=0.4):
    """Pattern search from the best ray point for the extreme of g over the likelihood region (moves that leave the
    region or the box are rejected; the step halves when no move improves)."""
    th = th0.copy()
    best = sign * goal(th[None], F, Mask, Y, t_now, T_end, H, kind)[0][0]
    for _ in range(iters):
        cand = np.clip(th + step * PATTERN, LO, HI)
        gv, ll = goal(cand, F, Mask, Y, t_now, T_end, H, kind)
        val = np.where(ll_hat - ll <= k, sign * gv, -np.inf)
        j = int(np.argmax(val))
        if val[j] > best + 1e-9:
            th, best = cand[j], val[j]
        else:
            step *= 0.5
            if step < 2e-3:
                break
    return sign * best


def second_order_halfwidth(A, k=K_REGION, gamma=np.inf):
    """Theorem Q: sup_D {a'D - (D'JD/(2k))^gamma} = (2 gamma - 1) (A sqrt(k/2)/gamma)^(2 gamma/(2 gamma - 1)),
    A^2 = a'J^-1 a; gamma -> infinity gives A sqrt(2k)."""
    if np.isinf(gamma):
        return A * np.sqrt(2 * k)
    return (2 * gamma - 1) * (A * np.sqrt(k / 2) / gamma) ** (2 * gamma / (2 * gamma - 1))


def penalized_sup(F, Mask, Y, t_now, T_end, H, th_hat, ll_hat, J, ks, gammas, kind='mon', ndir=160, nrad=28):
    """Cohen's robust upper and lower expectations with a finite penalty: sup / inf over theta of
    g(theta) -/+ (alpha(theta)/k)^gamma, alpha = l(theta_hat) - l(theta), evaluated on a polar grid in the J-metric.
    Returns {(k, gamma): (lower, upper)}."""
    U = fib_sphere(ndir) @ jmetric(J, max(ks)).T
    rmax = 2.5 * np.sqrt(2 * max(ks))
    rad = rmax * (np.arange(1, nrad + 1) / nrad) ** 1.5
    pts = np.clip(th_hat + (rad[None, :, None] * U[:, None, :]).reshape(-1, 3), LO, HI)
    pts = np.vstack([th_hat, pts])
    gv, ll = goal(pts, F, Mask, Y, t_now, T_end, H, kind)
    al = np.maximum(ll_hat - ll, 0.0)
    out = {}
    for k in ks:
        for gm in gammas:
            pen = (al / k) ** gm
            out[(k, gm)] = (float(np.min(gv + pen)), float(np.max(gv - pen)))
    return out


def joint_check(rng, theta=THETA_TRUE, T=8):
    """Exactness of the per-well decomposition: a field of three wells filtered as one Markov chain on 27 states
    versus three independent filters. Returns the largest differences in log-likelihood and in the goal."""
    d = np.array([0.6, 1.2, 1.9]); u = np.array([1.0, 0.0, 1.0])
    F = dict(d=d, u=u, tgt=np.array([0, 2]), n=3,
             pi0=np.array([[0.7, 0.2, 0.1], [0.8, 0.15, 0.05], [0.6, 0.3, 0.1]]))
    X, Yall = simulate(F, T, 2, rng, theta)
    Mask = rng.uniform(size=(T, 3)) < 0.6; Mask[0] = True
    Y = np.where(Mask, Yall, np.nan)
    ll1, f1, P1 = filt(theta, F, Mask, Y)
    g1 = propagate(f1, P1, 2)[0][F['tgt'], 2].sum()
    P = trans(theta, F)[0]
    idx = [(a, b, c) for a in range(3) for b in range(3) for c in range(3)]
    Pj = np.array([[P[0, a, a2] * P[1, b, b2] * P[2, c, c2] for (a2, b2, c2) in idx] for (a, b, c) in idx])
    f = np.array([F['pi0'][0, a] * F['pi0'][1, b] * F['pi0'][2, c] for (a, b, c) in idx])
    ll = 0.0
    for t in range(T):
        if t > 0:
            f = f @ Pj
        L = np.ones(27)
        for i in range(3):
            if Mask[t, i]:
                li = lik_obs(np.array([Y[t, i]]))[0]
                L = L * np.array([li[s[i]] for s in idx])
        c = (f * L).sum(); ll += np.log(c); f = f * L / c
    for _ in range(2):
        f = f @ Pj
    g2 = sum(f[j] for j, s in enumerate(idx) if s[0] == 2) + sum(f[j] for j, s in enumerate(idx) if s[2] == 2)
    return abs(ll - ll1[0]), abs(g2 - g1)
