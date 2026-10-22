"""Estimators of the marginal structural model theta = (theta1, theta2) in KURSIM-GO data.

ols_all   regression of Y on A1, A2, L1, L2 (adjusts for the alarm, which is affected by A1)
ols_base  regression of Y on A1, A2, L1 (ignores the alarm, which confounds A2)
gform     parametric g-formula: logistic model for L2, linear model for Y, standardization (bootstrap SE)
ipw       inverse probability weighting of the MSM with stabilized weights (sandwich SE, weights treated as known)
dr        doubly robust iterated-conditional-expectation estimator (Bang-Robins augmentation; influence-function SE)
frugal    maximum likelihood in the Gaussian frugal model (observed-information SE)
All return (theta1, theta2, se1, se2).
"""
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
import kursim_model as K


def logit(X, y, it=30):
    b = np.zeros(X.shape[1])
    for _ in range(it):
        p = expit(X @ b)
        H = X.T @ (X * (p * (1 - p))[:, None]) + 1e-8 * np.eye(X.shape[1])
        step = np.linalg.solve(H, X.T @ (y - p))
        b += step
        if np.max(np.abs(step)) < 1e-10:
            break
    return b


def ols_hc0(X, y, w=None):
    w = np.ones(len(y)) if w is None else w
    XtWX = X.T @ (X * w[:, None])
    b = np.linalg.solve(XtWX, X.T @ (w * y))
    r = y - X @ b
    Bi = np.linalg.inv(XtWX)
    M = X.T @ (X * (w ** 2 * r ** 2)[:, None])
    V = Bi @ M @ Bi
    return b, np.sqrt(np.diag(V))


def ones(n):
    return np.ones(n)


def ols_all(D):
    X = np.column_stack([ones(len(D['Y'])), D['A1'], D['A2'], D['L1'], D['L2']])
    b, se = ols_hc0(X, D['Y'])
    return b[1], b[2], se[1], se[2]


def ols_base(D):
    X = np.column_stack([ones(len(D['Y'])), D['A1'], D['A2'], D['L1']])
    b, se = ols_hc0(X, D['Y'])
    return b[1], b[2], se[1], se[2]


def _gform_point(D):
    n = len(D['Y'])
    g = logit(np.column_stack([ones(n), D['L1'], D['A1']]), D['L2'])
    X = np.column_stack([ones(n), D['A1'], D['A2'], D['L1'], D['L2']])
    b = np.linalg.lstsq(X, D['Y'], rcond=None)[0]
    dpi = expit(g[0] + g[1] * D['L1'] + g[2]).mean() - expit(g[0] + g[1] * D['L1']).mean()
    return b[1] + b[4] * dpi, b[2]


def gform(D, rng, B=100):
    t1, t2 = _gform_point(D)
    n = len(D['Y']); bs = np.empty((B, 2))
    for k in range(B):
        i = rng.integers(0, n, n)
        bs[k] = _gform_point({key: v[i] for key, v in D.items()})
    se = bs.std(0, ddof=1)
    return t1, t2, se[0], se[1]


def _propensities(D):
    n = len(D['Y'])
    X1 = np.column_stack([ones(n), D['L1']]); X2 = np.column_stack([ones(n), D['L1'], D['A1'], D['L2']])
    p1 = expit(X1 @ logit(X1, D['A1'])); p2 = expit(X2 @ logit(X2, D['A2']))
    return p1, p2


def ipw(D, props=None):
    n = len(D['Y'])
    p1, p2 = _propensities(D) if props is None else props
    q1 = D['A1'].mean()
    Xn = np.column_stack([ones(n), D['A1']]); q2 = expit(Xn @ logit(Xn, D['A2']))
    num = np.where(D['A1'] > 0.5, q1, 1 - q1) * np.where(D['A2'] > 0.5, q2, 1 - q2)
    den = np.where(D['A1'] > 0.5, p1, 1 - p1) * np.where(D['A2'] > 0.5, p2, 1 - p2)
    X = np.column_stack([ones(n), D['A1'], D['A2']])
    b, se = ols_hc0(X, D['Y'], num / den)
    return b[1], b[2], se[1], se[2]


def dr(D, props=None):
    """Augmented iterated conditional expectations for the four regime means; the main-effects MSM is the least-squares
    fit to the four means, theta1 = ((m10 - m00) + (m11 - m01)) / 2, theta2 = ((m01 - m00) + (m11 - m10)) / 2."""
    n = len(D['Y'])
    p1, p2 = _propensities(D) if props is None else props
    IF = {}
    for a1 in (0, 1):
        for a2 in (0, 1):
            s2 = D['A2'] == a2
            X2 = np.column_stack([ones(n), D['L1'], D['A1'], D['L2']])
            c2 = np.linalg.lstsq(X2[s2], D['Y'][s2], rcond=None)[0]
            Q2obs = X2 @ c2
            Q2set = np.column_stack([ones(n), D['L1'], np.full(n, a1), D['L2']]) @ c2
            s1 = D['A1'] == a1
            X1 = np.column_stack([ones(n), D['L1']])
            c1 = np.linalg.lstsq(X1[s1], Q2set[s1], rcond=None)[0]
            Q1 = X1 @ c1
            g1 = p1 if a1 == 1 else 1 - p1
            g2 = p2 if a2 == 1 else 1 - p2
            I1 = (D['A1'] == a1) / g1
            I12 = I1 * (D['A2'] == a2) / g2
            phi = Q1 + I1 * (Q2set - Q1) + I12 * (D['Y'] - Q2obs)
            IF[(a1, a2)] = phi
    c1 = 0.5 * (IF[(1, 0)] - IF[(0, 0)] + IF[(1, 1)] - IF[(0, 1)])
    c2 = 0.5 * (IF[(0, 1)] - IF[(0, 0)] + IF[(1, 1)] - IF[(1, 0)])
    return c1.mean(), c2.mean(), c1.std(ddof=1) / np.sqrt(n), c2.std(ddof=1) / np.sqrt(n)


def num_hessian(f, x, h=1e-4):
    k = len(x); H = np.empty((k, k)); E = np.eye(k) * h
    f0 = f(x)
    for i in range(k):
        for j in range(i, k):
            H[i, j] = H[j, i] = (f(x + E[i] + E[j]) - f(x + E[i] - E[j]) - f(x - E[i] + E[j]) + f(x - E[i] - E[j])) / (4 * h * h)
    return H


def frugal(D, start=None):
    n = len(D['Y'])
    if start is None:
        g = logit(np.column_stack([ones(n), D['L1'], D['A1']]), D['L2'])
        t1, t2, _, _ = ipw(D)
        X = np.column_stack([ones(n), D['A1'], D['A2']])
        th0 = np.mean(D['Y'] - t1 * D['A1'] - t2 * D['A2'])
        s = np.std(D['Y'] - X @ np.array([th0, t1, t2]))
        start = np.array([g[0], g[1], g[2], th0, t1, t2, np.log(s), 0.0, 0.0])
    nll = lambda v: -K.loglik_obs(v, D).sum()
    res = minimize(nll, start, method='BFGS', options=dict(gtol=1e-6, maxiter=500))
    H = num_hessian(nll, res.x)
    try:
        V = np.linalg.inv(H)
        se = np.sqrt(np.maximum(np.diag(V), 0))
    except np.linalg.LinAlgError:
        se = np.full(9, np.nan)
    return res.x[4], res.x[5], se[4], se[5]


METHODS = ['ols_all', 'ols_base', 'gform', 'ipw', 'dr', 'frugal']


def all_estimates(D, rng, B=100):
    props = _propensities(D)
    out = {'ols_all': ols_all(D), 'ols_base': ols_base(D), 'gform': gform(D, rng, B), 'ipw': ipw(D, props),
           'dr': dr(D, props), 'frugal': frugal(D)}
    return out
