"""QENDRESA-GO estimators of the marginal structural hazard model and of the value of dynamic pumping rules.

  frugal      joint maximum likelihood of the frugal survival model (Theorem K): dryness model, hazard MSM and
              copula together, with analytic scores; standard errors from the observed information.
  twostep     the dryness model fitted to the wells still at risk (the tempting shortcut), then the hazard MSM and
              copula with the dryness model held fixed; Proposition J(c) says the first step is biased.
  ipw         pooled complementary log-log regression with stabilized weights (marginal structural Cox-type model
              of Hernan, Brumback and Robins), robust standard errors clustered by well, weights treated as known.
  gform       parametric g-formula: a pooled cloglog model of the conditional hazard given (season, L_k, A_k,
              A_{k-1}) and a Gaussian AR dryness model fitted to the wells at risk; the 2^K static regimes are
              computed by Monte Carlo with fixed draws and projected on the hazard MSM; delta-method errors.
Dynamic rules A_k = 1{L_k < tau}: risk P(T^g <= K) and yield E[sum_k A_k^g 1{T^g >= k}] by the frugal simulator,
by inverse probability weighting (artificial censoring at the first deviation) and by the parametric g-formula.
"""
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, ndtr, ndtri, log_ndtr
import qendresa_model as M

K = M.K
LOG2PI = np.log(2 * np.pi)
NP = 11                                   # mu1, log sd1, g0, g1, g2, log sdL, a0, a1, beta, betal, z (rho = tanh z / sqrt K)
IDX_TH = slice(6, 10)


def prep(D):
    n = D['L'].shape[0]
    kk = np.arange(K)[None, :]
    O = kk < D['tlast'][:, None]                                  # season observed (well at risk at its start)
    Dk = (kk == D['tlast'][:, None] - 1) & D['event'][:, None]    # failure in that season
    Alag = np.concatenate([np.zeros((n, 1)), D['A'][:, :-1]], axis=1)
    Llag = np.concatenate([np.zeros((n, 1)), D['L'][:, :-1]], axis=1)
    return dict(L=D['L'], A=D['A'], Alag=Alag, Llag=Llag, O=O, Dk=Dk, t=D['tlast'], ev=D['event'], n=n)


def unpack(p):
    past = dict(mu1=p[0], sd1=np.exp(p[1]), g0=p[2], g1=p[3], g2=p[4], sdL=np.exp(p[5]))
    return past, np.asarray(p[6:10]), np.tanh(p[10]) / np.sqrt(K)


def _logdiff(hi, lo):
    """log(Phi(hi) - Phi(lo)), hi > lo, stable in both tails."""
    up = lo > 0
    a = np.where(up, log_ndtr(-lo), log_ndtr(hi))
    b = np.where(up, log_ndtr(-hi), log_ndtr(lo))
    return a + np.log1p(-np.exp(np.minimum(b - a, -1e-300)))


def frugal_ll(p, P, scores=False, fixed_past=None):
    """Log-likelihood (sum over wells) of Theorem K and, if scores, the n x 11 matrix of per-well scores."""
    past, th, rho = unpack(p)
    L, A, Alag, Llag, O, t, ev, n = P['L'], P['A'], P['Alag'], P['Llag'], P['O'], P['t'], P['ev'], P['n']
    sd = np.where(np.arange(K)[None, :] == 0, past['sd1'], past['sdL'])
    mean = np.where(np.arange(K)[None, :] == 0, past['mu1'], past['g0'] + past['g1'] * Llag + past['g2'] * Alag)
    w = (L - mean) / sd
    lpast = (O * (-np.log(sd) - 0.5 * w ** 2 - 0.5 * LOG2PI)).sum(1)
    sw = (O * w).sum(1)
    m = rho * sw
    s = np.sqrt(1 - t * rho ** 2)
    eta = M.lin_pred(A, th)
    H = np.cumsum(np.exp(eta), axis=1)
    c = -ndtri(-np.expm1(-H))
    r = np.arange(n)
    c_lo = c[r, t - 1]
    has_hi = ev & (t >= 2)
    c_hi = np.where(has_hi, c[r, np.maximum(t - 2, 0)], np.inf)
    z_lo, z_hi = (c_lo - m) / s, (c_hi - m) / s
    lout = np.where(ev, _logdiff(z_hi, z_lo), log_ndtr(z_lo))
    ll = lpast + lout
    if not scores:
        return ll.sum()
    # ---- scores
    phi = lambda z: np.exp(-0.5 * z ** 2 - 0.5 * LOG2PI)
    g_hi = np.where(has_hi, np.exp(-0.5 * np.where(has_hi, z_hi, 0) ** 2 - 0.5 * LOG2PI - lout), 0.0)
    g_lo = np.where(ev, -1.0, 1.0) * np.exp(-0.5 * z_lo ** 2 - 0.5 * LOG2PI - lout)
    G = np.zeros((n, NP))
    # theta through c: dc_j/dH_j = -S_j / phi(c_j); dH_j/dtheta = cumsum(exp(eta) x)
    X = np.stack([np.ones_like(A), np.broadcast_to(np.arange(K)[None, :], A.shape).astype(float), A, Alag], axis=2)
    dH = np.cumsum(np.exp(eta)[:, :, None] * X, axis=1)                         # n x K x 4
    dcdH = -np.exp(-H + 0.5 * c ** 2 + 0.5 * LOG2PI)
    dc = dcdH[:, :, None] * dH
    dc_lo = dc[r, t - 1]
    dc_hi = np.where(has_hi[:, None], dc[r, np.maximum(t - 2, 0)], 0.0)
    G[:, IDX_TH] = (g_hi[:, None] * dc_hi + g_lo[:, None] * dc_lo) / s[:, None]
    # rho through m and s
    zh = np.where(has_hi, z_hi, 0.0)
    dzlo_drho = -sw / s + z_lo * t * rho / s ** 2
    dzhi_drho = -sw / s + zh * t * rho / s ** 2
    G[:, 10] = (g_hi * dzhi_drho + g_lo * dzlo_drho) * (1 - np.tanh(p[10]) ** 2) / np.sqrt(K)
    # dryness parameters: dw/dpsi enters the past factor and m
    first = np.zeros((1, K)); first[0, 0] = 1.0
    rest = 1.0 - first
    dw = np.zeros((n, K, 6))
    dw[:, :, 0] = -first / past['sd1']
    dw[:, :, 1] = -w * first
    dw[:, :, 2] = -rest / past['sdL']
    dw[:, :, 3] = -rest * Llag / past['sdL']
    dw[:, :, 4] = -rest * Alag / past['sdL']
    dw[:, :, 5] = -w * rest
    dlogsd = np.zeros((1, K, 6)); dlogsd[0, 0, 1] = 1.0; dlogsd[0, 1:, 5] = 1.0
    Gpast = (O[:, :, None] * (-dlogsd - w[:, :, None] * dw)).sum(1)
    dm = rho * (O[:, :, None] * dw).sum(1)
    G[:, :6] = Gpast - (g_hi + g_lo)[:, None] * dm / s[:, None]
    return ll.sum(), G


def _start(P):
    """Start values: dryness model by least squares on the wells at risk, hazard MSM by an unweighted pooled cloglog."""
    O = P['O']
    L0 = P['L'][:, 0]
    X = np.stack([np.ones(O[:, 1:].sum()), P['Llag'][:, 1:][O[:, 1:]], P['Alag'][:, 1:][O[:, 1:]]], 1)
    y = P['L'][:, 1:][O[:, 1:]]
    g = np.linalg.lstsq(X, y, rcond=None)[0]
    res = y - X @ g
    th = pooled_cloglog(P, np.ones_like(P['L']))[0]
    return np.array([L0.mean(), np.log(L0.std()), *g, np.log(res.std()), *th, 0.4])


def fit_frugal(P, p0=None, which=None):
    """Joint MLE (which=None) or the second step of the two-step fit (which = indices of the free parameters)."""
    p0 = _start(P) if p0 is None else p0.copy()
    free = np.arange(NP) if which is None else np.asarray(which)

    def f(q):
        p = p0.copy(); p[free] = q
        ll, G = frugal_ll(p, P, scores=True)
        return -ll, -G.sum(0)[free]
    res = minimize(f, p0[free], jac=True, method='BFGS', options=dict(gtol=1e-6, maxiter=500))
    p = p0.copy(); p[free] = res.x
    # observed information by central differences of the analytic gradient
    h = 1e-5
    Hm = np.zeros((len(free), len(free)))
    for j in range(len(free)):
        e = np.zeros(len(free)); e[j] = h
        Hm[:, j] = (f(res.x + e)[1] - f(res.x - e)[1]) / (2 * h)
    Hm = 0.5 * (Hm + Hm.T)
    cov = np.linalg.inv(Hm)
    return dict(p=p, cov=cov, free=free, ll=-res.fun, ok=bool(res.success) or res.fun < f(p0[free])[0])


def frugal_theta(fit):
    j = list(fit['free']).index(6)
    se = np.sqrt(np.diag(fit['cov'])[j:j + 4])
    return fit['p'][IDX_TH], se


def twostep(P):
    p0 = _start(P)                                   # its dryness part is the least-squares fit to the wells at risk
    fit = fit_frugal(P, p0, which=np.arange(6, NP))
    return fit


# ------------------------------------------------------------------ pooled (weighted) complementary log-log
def pooled_cloglog(P, Wt, Xfun=None, iters=50):
    """Fisher scoring for the pooled cloglog hazard regression on the at-risk well-seasons with weights Wt;
    returns coefficients, robust (clustered) covariance and the bread."""
    O = P['O']
    if Xfun is None:
        X = np.stack([np.ones_like(P['A']), np.broadcast_to(np.arange(K)[None, :], P['A'].shape).astype(float), P['A'], P['Alag']], 2)
    else:
        X = Xfun(P)
    q = X.shape[2]
    b = np.zeros(q); b[0] = -2.5
    d = P['Dk'].astype(float)
    WO = np.where(O, Wt, 0.0)

    def loglik(b):
        eta = np.clip(X @ b, -30, 4)
        return (WO * (d * np.log(-np.expm1(-np.exp(eta))) - (1 - d) * np.exp(eta))).sum()
    cur = loglik(b)
    for _ in range(iters):                                   # damped Newton (the cloglog log-likelihood is concave)
        eta = np.clip(X @ b, -30, 4)
        h = -np.expm1(-np.exp(eta))
        u = np.exp(eta) * (d - h) / h                        # d loglik / d eta
        info = np.exp(2 * eta) * (1 - h) / h
        g = ((WO * u)[:, :, None] * X).sum((0, 1))
        I = np.einsum('nk,nki,nkj->ij', WO * info, X, X)
        step = np.linalg.solve(I, g)
        t = 1.0
        while loglik(b + t * step) < cur - 1e-9 and t > 1e-6:
            t /= 2
        b = b + t * step
        new = loglik(b)
        if np.abs(t * step).max() < 1e-10 or abs(new - cur) < 1e-12 * (1 + abs(cur)):
            cur = new
            break
        cur = new
    eta = np.clip(X @ b, -30, 4)
    h = -np.expm1(-np.exp(eta))
    u = np.exp(eta) * (d - h) / h
    Si = ((WO * u)[:, :, None] * X).sum(1)                   # per-well scores
    I = np.einsum('nk,nki,nkj->ij', WO * np.exp(2 * eta) * (1 - h) / h, X, X)
    Ii = np.linalg.inv(I)
    return b, Ii @ (Si.T @ Si) @ Ii, I, Si


def logistic(y, X, mask, iters=50):
    b = np.zeros(X.shape[-1])
    for _ in range(iters):
        p = expit(X @ b)
        g = ((mask * (y - p))[..., None] * X).reshape(-1, X.shape[-1]).sum(0)
        I = np.einsum('nk,nki,nkj->ij', mask * p * (1 - p), X, X)
        step = np.linalg.solve(I, g)
        b += step
        if np.abs(step).max() < 1e-10:
            break
    return b


def propensities(P):
    """Fitted P(A_k = A_ik | history) under the denominator (L_k, A_{k-1}) and numerator (A_{k-1}) models."""
    one = np.ones_like(P['A'])
    Xd = np.stack([one, P['L'], P['Alag']], 2)
    Xn = np.stack([one, P['Alag']], 2)
    bd, bn = logistic(P['A'], Xd, P['O']), logistic(P['A'], Xn, P['O'])
    pd, pn = expit(Xd @ bd), expit(Xn @ bn)
    A = P['A']
    return np.where(A > 0.5, pd, 1 - pd), np.where(A > 0.5, pn, 1 - pn), bd


def ipw(P):
    fd, fn, _ = propensities(P)
    SW = np.cumprod(np.where(P['O'], fn / fd, 1.0), axis=1)
    b, cov, _, _ = pooled_cloglog(P, SW)
    return b, np.sqrt(np.diag(cov)), SW


# ------------------------------------------------------------------ parametric g-formula
def _gform_X(P):
    one = np.ones_like(P['A'])
    return np.stack([one, np.broadcast_to(np.arange(K)[None, :], P['A'].shape).astype(float), P['L'], P['A'], P['Alag']], 2)


def gform_fit(P):
    """phi = (eta(5), mu0, log sd0, g0, g1, g2, log sdL) with its clustered sandwich covariance."""
    eta, _, Ieta, Seta = pooled_cloglog(P, np.ones_like(P['L']), Xfun=_gform_X)
    O = P['O']
    L0 = P['L'][:, 0]
    mu0, sd0 = L0.mean(), L0.std()
    O1 = O[:, 1:]
    Xl = np.stack([np.ones_like(P['L'][:, 1:]), P['Llag'][:, 1:], P['Alag'][:, 1:]], 2)
    y = P['L'][:, 1:]
    g = np.linalg.solve(np.einsum('nk,nki,nkj->ij', O1, Xl, Xl), ((O1 * y)[:, :, None] * Xl).sum((0, 1)))
    r = y - Xl @ g
    sdL = np.sqrt((O1 * r ** 2).sum() / O1.sum())
    n = P['n']
    S = np.zeros((n, 11))
    S[:, :5] = Seta
    S[:, 5] = (L0 - mu0) / sd0 ** 2
    S[:, 6] = (L0 - mu0) ** 2 / sd0 ** 2 - 1
    S[:, 7:10] = ((O1 * r)[:, :, None] * Xl).sum(1) / sdL ** 2
    S[:, 10] = (O1 * (r ** 2 / sdL ** 2 - 1)).sum(1)
    Bread = np.zeros((11, 11))
    Bread[:5, :5] = Ieta
    Bread[5, 5] = n / sd0 ** 2
    Bread[6, 6] = 2 * n
    Bread[7:10, 7:10] = np.einsum('nk,nki,nkj->ij', O1, Xl, Xl) / sdL ** 2
    Bread[10, 10] = 2 * O1.sum()
    Bi = np.linalg.inv(Bread)
    phi = np.concatenate([eta, [mu0, np.log(sd0)], g, [np.log(sdL)]])
    return phi, Bi @ (S.T @ S) @ Bi


def gform_paths(phi, Z, regime=None, tau=None):
    """Monte Carlo g-formula with the draws Z (M x K): survival products and treatments along each path."""
    eta, mu0, sd0, g, sdL = phi[:5], phi[5], np.exp(phi[6]), phi[7:10], np.exp(phi[10])
    Mn = Z.shape[0]
    L = np.zeros((Mn, K)); A = np.zeros((Mn, K)); h = np.zeros((Mn, K))
    for k in range(K):
        aprev = A[:, k - 1] if k else np.zeros(Mn)
        L[:, k] = mu0 + sd0 * Z[:, 0] if k == 0 else g[0] + g[1] * L[:, k - 1] + g[2] * aprev + sdL * Z[:, k]
        A[:, k] = regime[k] if regime is not None else (L[:, k] < tau).astype(float)
        h[:, k] = -np.expm1(-np.exp(eta[0] + eta[1] * k + eta[2] * L[:, k] + eta[3] * A[:, k] + eta[4] * aprev))
    return A, np.cumprod(1 - h, axis=1)


REGS = np.array([[(r >> j) & 1 for j in range(K)] for r in range(2 ** K)], float)


def msm_projection(S):
    """Hazard-MSM coefficients closest (in expected pooled cloglog log-likelihood, regimes equally weighted) to the
    counterfactual survival curves S (2^K x K); returns the truth when the MSM holds."""
    Sprev = np.concatenate([np.ones((S.shape[0], 1)), S[:, :-1]], 1)
    hz = 1 - S / Sprev
    Alag = np.concatenate([np.zeros((REGS.shape[0], 1)), REGS[:, :-1]], 1)
    X = np.stack([np.ones_like(REGS), np.broadcast_to(np.arange(K)[None, :], REGS.shape).astype(float), REGS, Alag], 2)
    b = np.array([-2.5, 0.0, 0.0, 0.0])
    for _ in range(100):
        eta = X @ b
        h = -np.expm1(-np.exp(eta))
        u = np.exp(eta) * (hz - h) / h
        g = ((Sprev * u)[:, :, None] * X).sum((0, 1))
        I = np.einsum('nk,nki,nkj->ij', Sprev * np.exp(2 * eta) * (1 - h) / h, X, X)
        step = np.linalg.solve(I, g)
        b += step
        if np.abs(step).max() < 1e-12:
            break
    return b


def gform_theta(phi, Z):
    S = np.stack([gform_paths(phi, Z, regime=reg)[1].mean(0) for reg in REGS])
    return msm_projection(S)


def gform(P, Z):
    phi, cov = gform_fit(P)
    th = gform_theta(phi, Z)
    J = np.zeros((4, 11))
    for j in range(11):
        e = np.zeros(11); e[j] = 1e-4
        J[:, j] = (gform_theta(phi + e, Z) - gform_theta(phi - e, Z)) / 2e-4
    return th, np.sqrt(np.diag(J @ cov @ J.T)), phi


# ------------------------------------------------------------------ dynamic rules
def frugal_rules(p, taus, W):
    past, th, rho = unpack(p)
    return np.array([M.frugal_rule_value(dict(past=past, th=th, rho=rho), tau, W) for tau in taus])


def frugal_rules_band(p, cov, free, taus, W, h=0.01):
    """Delta-method standard errors of the frugal risk and yield of each rule (central differences with a step
    large enough to smooth the indicator of the rule over the fixed scores W)."""
    base = frugal_rules(p, taus, W)
    J = np.zeros((len(taus), 2, len(free)))
    for j, k in enumerate(free):
        e = np.zeros(NP); e[k] = h
        J[:, :, j] = (frugal_rules(p + e, taus, W) - frugal_rules(p - e, taus, W)) / (2 * h)
    se = np.sqrt(np.einsum('tqi,ij,tqj->tq', J, cov, J))
    return base, se


def gform_rules(phi, taus, Z):
    out = []
    for tau in taus:
        A, Sp = gform_paths(phi, Z, tau=tau)
        Sprev = np.concatenate([np.ones((Z.shape[0], 1)), Sp[:, :-1]], 1)
        out.append((1 - Sp[:, -1].mean(), (A * Sprev).sum(1).mean()))
    return np.array(out)


def ipw_rules(P, taus):
    """Artificial censoring at the first deviation from the rule, inverse probability of following it; hazard-type
    (Hajek) estimate of the survival and of the yield."""
    fd, _, _ = propensities(P)
    O, Dk, L, A = P['O'], P['Dk'], P['L'], P['A']
    out = []
    for tau in taus:
        g = (L < tau).astype(float)
        follow = np.cumprod(np.where(O, A == g, True), axis=1)                # followed the rule up to season k
        Wk = np.where(follow, 1.0 / np.cumprod(np.where(O, fd, 1.0), axis=1), 0.0) * O
        Wprev = np.concatenate([np.ones((P['n'], 1)), np.cumprod(np.where(O, fd, 1.0), axis=1)[:, :-1]], 1)
        followprev = np.concatenate([np.ones((P['n'], 1)), follow[:, :-1]], 1)
        Wp = np.where(followprev, 1.0 / Wprev, 0.0) * O                      # weight at the start of season k
        S, Y = 1.0, 0.0
        for k in range(K):
            den = Wk[:, k].sum()
            hk = (Wk[:, k] * Dk[:, k]).sum() / den if den > 0 else 0.0
            Y += S * (Wp[:, k] * g[:, k]).sum() / max(Wp[:, k].sum(), 1e-12)
            S *= 1 - hk
        out.append((1 - S, Y))
    return np.array(out)


def choose(vals, taus, budget):
    """Largest yield among the rules whose risk is within the budget (the least risky rule if none is)."""
    ok = vals[:, 0] <= budget
    if not ok.any():
        return int(np.argmin(vals[:, 0]))
    return int(np.flatnonzero(ok)[np.argmax(vals[ok, 1])])
