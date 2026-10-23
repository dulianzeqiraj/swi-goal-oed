"""BESA-GO estimators and the copula check.

frugal MLE       maximum likelihood with Theorem C, common copula ('common', 9 parameters) or a copula that depends on
                 season-2 pumping ('flex', 11 parameters); model-based standard errors from the observed information
                 and per-observation influence functions IF_i = n H^-1 s_i.
frugal-augmented doubly robust estimator (BESA-DR)
                 augmented iterated conditional expectations in which the outcome regressions are the closed forms
                 implied by the fitted frugal model (Proposition E): Q2 = mu + s rho2(a2) lambda(l2, t),
                 Q1 = mu = theta0 + theta1 a1 + theta2 a2 + s rho1(a2) l1; propensities from main-effects logistic
                 models. Its influence function includes the first-order effect of estimating the frugal parameters
                 and the propensities (Jacobians by finite differences).
Hausman test     T = d' V^-1 d with d = theta_DR - theta_MLE and V the empirical covariance of the difference of the two
                 influence functions, divided by n; chi-square with 2 degrees of freedom (Theorem G).
likelihood-ratio test  2 (l_flex - l_common), chi-square with 2 degrees of freedom: is the copula the same with and
                 without season-2 pumping? It is internal to the frugal family and needs no propensity model.
BESA pipeline    (1) the likelihood-ratio test chooses the working copula (common or pumping-dependent);
                 (2) the Hausman test compares the working MLE with its frugal-augmented doubly robust estimate;
                 (3) the MLE is reported if the Hausman test does not reject, the doubly robust estimate otherwise.
"""
import os, sys
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, ndtri
from scipy.stats import chi2

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kursim_go'))
import kursim_est as KE  # noqa: E402
import besa_model as M  # noqa: E402

ALPHA = 0.05
H_FD = 1e-5


def design(D):
    n = len(D['Y']); one = np.ones(n)
    return np.column_stack([one, D['L1']]), np.column_stack([one, D['L1'], D['A1'], D['L2']])


def logit_fit(X, y):
    b = KE.logit(X, y)
    p = expit(X @ b)
    Hm = X.T @ (X * (p * (1 - p))[:, None]) / len(y)
    IF = (X * (y - p)[:, None]) @ np.linalg.inv(Hm)          # n x k, IF of the coefficients
    return b, IF


def start_vector(D, kind):
    n = len(D['Y'])
    g = KE.logit(np.column_stack([np.ones(n), D['L1'], D['A1']]), D['L2'])
    t1, t2, _, _ = KE.ipw(D)
    th0 = np.mean(D['Y'] - t1 * D['A1'] - t2 * D['A2'])
    s = np.std(D['Y'] - th0 - t1 * D['A1'] - t2 * D['A2'])
    z = [0.0, 0.0] if kind == 'common' else [0.0, 0.0, 0.0, 0.0]
    return np.array([g[0], g[1], g[2], th0, t1, t2, np.log(s)] + z)


def fit_frugal(D, kind='common', start=None):
    n = len(D['Y'])
    v0 = start_vector(D, kind) if start is None else start
    nll = lambda v: -M.loglik(v, D, kind).sum()
    res = minimize(nll, v0, method='BFGS', options=dict(gtol=1e-6, maxiter=2000))
    v = res.x
    H = KE.num_hessian(nll, v)
    Hinv = np.linalg.inv(H)
    k = len(v); S = np.empty((n, k))
    for j in range(k):
        e = np.zeros(k); e[j] = H_FD
        S[:, j] = (M.loglik(v + e, D, kind) - M.loglik(v - e, D, kind)) / (2 * H_FD)
    IF = n * S @ Hinv
    se = np.sqrt(np.maximum(np.diag(Hinv), 0))
    return dict(v=v, theta=v[4:6].copy(), se=se[4:6].copy(), IF=IF, kind=kind, ll=-float(res.fun), ok=bool(res.success) or res.status == 2)


def frugal_Q(v, kind, L1, a1, L2, a2):
    """Outcome regressions implied by the frugal model (Proposition E), with A1 = a1 and A2 = a2 set."""
    g, th, s = v[0:3], v[3:6], np.exp(v[6])
    r1s, r2s = M.rho_of(v, kind)
    r1, r2 = r1s[int(a2)], r2s[int(a2)]
    pi = np.clip(expit(g[0] + g[1] * L1 + g[2] * a1), 1e-12, 1 - 1e-12)
    t = ndtri(1 - pi)
    ph = np.exp(-0.5 * t ** 2) / np.sqrt(2 * np.pi)
    lam = np.where(L2 > 0.5, ph / pi, -ph / (1 - pi))
    Q1 = th[0] + th[1] * a1 + th[2] * a2 + s * r1 * L1
    return Q1, Q1 + s * r2 * lam


def dr_contrasts(D, v, kind, al, be, X1, X2):
    """Per-observation augmented contrasts (theta1, theta2) of the main-effects MSM fitted to the four regimes."""
    p1, p2 = expit(X1 @ al), expit(X2 @ be)
    phi = {}
    for a1 in (0, 1):
        for a2 in (0, 1):
            Q1, Q2 = frugal_Q(v, kind, D['L1'], a1, D['L2'], a2)
            g1 = p1 if a1 == 1 else 1 - p1
            g2 = p2 if a2 == 1 else 1 - p2
            I1 = (D['A1'] == a1) / g1
            I12 = I1 * (D['A2'] == a2) / g2
            phi[(a1, a2)] = Q1 + I1 * (Q2 - Q1) + I12 * (D['Y'] - Q2)
    c1 = 0.5 * (phi[(1, 0)] - phi[(0, 0)] + phi[(1, 1)] - phi[(0, 1)])
    c2 = 0.5 * (phi[(0, 1)] - phi[(0, 0)] + phi[(1, 1)] - phi[(1, 0)])
    return np.column_stack([c1, c2])


def dr_frugal(D, fit, props):
    """Frugal-augmented doubly robust estimate with its full influence function."""
    X1, X2 = design(D)
    (al, IFal), (be, IFbe) = props
    v, kind = fit['v'], fit['kind']
    C = dr_contrasts(D, v, kind, al, be, X1, X2)
    th = C.mean(0)
    IF = C - th
    for par, IFp, which in ((v, fit['IF'], 'v'), (al, IFal, 'al'), (be, IFbe, 'be')):
        J = np.empty((2, len(par)))
        for j in range(len(par)):
            e = np.zeros(len(par)); e[j] = H_FD
            args = lambda q: (q, al, be) if which == 'v' else ((v, q, be) if which == 'al' else (v, al, q))
            Cp = dr_contrasts(D, *(lambda a: (a[0], kind, a[1], a[2]))(args(par + e)), X1, X2).mean(0)
            Cm = dr_contrasts(D, *(lambda a: (a[0], kind, a[1], a[2]))(args(par - e)), X1, X2).mean(0)
            J[:, j] = (Cp - Cm) / (2 * H_FD)
        IF = IF + IFp @ J.T
    n = len(D['Y'])
    return dict(theta=th, se=np.sqrt(IF.var(0, ddof=1) / n), IF=IF)


def hausman(fit, drf):
    n = fit['IF'].shape[0]
    d = drf['theta'] - fit['theta']
    Dl = drf['IF'] - fit['IF'][:, 4:6]
    V = np.cov(Dl.T) / n
    T = float(d @ np.linalg.solve(V, d))
    return T, float(chi2.sf(T, 2))


def besa(D):
    """All estimators of one data set; returns a dict of (theta1, theta2, se1, se2) tuples and test results."""
    X1, X2 = design(D)
    props = (logit_fit(X1, D['A1']), logit_fit(X2, D['A2']))
    out = {}
    fc = fit_frugal(D, 'common')
    dc = dr_frugal(D, fc, props)
    Tc, pc = hausman(fc, dc)
    ff = fit_frugal(D, 'flex', start=np.r_[fc['v'], fc['v'][7:9]])
    df = dr_frugal(D, ff, props)
    Tf, pf = hausman(ff, df)
    tup = lambda r: (r['theta'][0], r['theta'][1], r['se'][0], r['se'][1])
    out['mle_common'] = tup(fc); out['mle_flex'] = tup(ff)
    out['drf_common'] = tup(dc); out['drf_flex'] = tup(df)
    out['dr_linear'] = KE.dr(D)
    out['ipw'] = KE.ipw(D)
    LR = max(2 * (ff['ll'] - fc['ll']), 0.0)
    pLR = float(chi2.sf(LR, 2))
    if pLR >= ALPHA:                                     # (1) working copula
        work, Tw, pw = 'common', Tc, pc
    else:
        work, Tw, pw = 'flex', Tf, pf
    out['besa'] = out['mle_' + work] if pw >= ALPHA else out['drf_' + work]     # (2)-(3)
    branch = (0 if work == 'common' else 1) + (0 if pw >= ALPHA else 2)       # 0 common MLE, 1 flex MLE, 2/3 DR
    out['test'] = (Tc, pc, Tf, pf, LR, pLR, branch)
    out['rho_flex'] = tuple(np.concatenate(M.rho_of(ff['v'], 'flex')))
    return out


METHODS = ['mle_common', 'mle_flex', 'drf_common', 'drf_flex', 'dr_linear', 'ipw', 'besa']
