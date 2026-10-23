"""Estimators of psi = mean over treated wells of E[Y(0) | X] for BARASPESHA-GO.

naive        mean chloride of the control wells
sim_nominal  the simulator at its nominal parameters, averaged over the treated wells
sim_calib    the simulator calibrated on the control wells (Levenberg-Marquardt), delta-method interval
ols          linear regression adjustment on the four standardized covariates (implied-weights interval)
bal_generic  kernel ridge balancing weights (Gaussian kernel), penalty by cross-validated Riesz loss
aug_generic  the same weights augmented with a kernel ridge outcome model (automatic debiased ML)
aug_sim      the same weights augmented with the calibrated simulator
baraspesha   the calibrated simulator augmented with minimax weights in the physics kernel
             K = S Gamma S' + tau^2 (s_K s_K') o K_mod + B^2 K_gen, bias-aware interval
"""
import numpy as np
from scipy.linalg import solve, eigh
from scipy.optimize import nnls
from scipy.stats import norm
import baraspesha_model as M

PEN_GRID = np.geomspace(1e-4, 30.0, 18)
LAM_GRID = np.geomspace(1e-5, 1e2, 22)
ELLS = (0.5, 1.0, 2.0)
PHYS = dict(kcal=3.0, tau=0.35, ell_mod=0.7, B=0.15, ell_gen=1.0)
Z975 = norm.ppf(0.975)


def phys_kernel(S_a, S_b, Zm_a, Zm_b, Zg_a, Zg_b, P, G):
    K = S_a @ G @ S_b.T
    K += P['tau'] ** 2 * np.outer(S_a[:, 0], S_b[:, 0]) * M.rbf(Zm_a, Zm_b, P['ell_mod'])
    K += P['B'] ** 2 * M.rbf(Zg_a, Zg_b, P['ell_gen'])
    return K


def wald(est, se):
    return est, se, est - Z975 * se, est + Z975 * se


def estimate_all(F, rng, P=PHYS, exact=False, idx0=None, methods=None):
    """F: a well field (dict). idx0: optional subset of control wells whose chloride is measured (design)."""
    A = F['A']
    T = np.where(A == 1)[0]
    C = np.where(A == 0)[0] if idx0 is None else np.asarray(idx0)
    Zall = M.features(F)
    Z = M.standardize(Zall, Zall)
    Z0, Z1 = Z[C], Z[T]
    Y0 = F['Y'][C]
    out = {}
    want = (lambda k: True) if methods is None else (lambda k: k in methods)

    if want('naive'):
        out['naive'] = (Y0.mean(), np.nan, np.nan, np.nan)
    if want('sim_nominal'):
        out['sim_nominal'] = (M.f_sim(F['xw'][T], F['Q0'][T], F['kmeas'][T], np.zeros(3), exact).mean(), np.nan, np.nan, np.nan)

    # calibrated simulator (on the measured controls)
    th, J0, r0 = M.calibrate(F['xw'][C], F['Q0'][C], F['kmeas'][C], Y0, exact)
    f1 = M.f_sim(F['xw'][T], F['Q0'][T], F['kmeas'][T], th, exact)
    S1 = M.sens(F['xw'][T], F['Q0'][T], F['kmeas'][T], th, exact)
    if want('sim_calib'):
        s2 = r0 @ r0 / max(len(C) - 3, 1)
        g = S1.mean(0)
        V = s2 * np.linalg.pinv(J0.T @ J0)
        out['sim_calib'] = wald(f1.mean(), float(np.sqrt(max(g @ V @ g, 0))))

    if want('ols'):
        X0 = np.column_stack([np.ones(len(C)), Z0]); x1 = np.r_[1.0, Z1.mean(0)]
        w = X0 @ solve(X0.T @ X0, x1)
        beta = solve(X0.T @ X0, X0.T @ Y0)
        e = Y0 - X0 @ beta
        h = np.einsum('ij,ji->i', X0, solve(X0.T @ X0, X0.T))
        out['ols'] = wald(float(x1 @ beta), float(np.sqrt(np.sum(w ** 2 * (e / (1 - h)) ** 2))))

    need_generic = any(want(k) for k in ('bal_generic', 'aug_generic', 'aug_sim'))
    if need_generic:
        # outcome model: kernel ridge, (length-scale, penalty) by GCV
        best = None
        for ell in ELLS:
            K00 = M.rbf(Z0, Z0, ell)
            fit, loo, lam = M.gcv_ridge(K00, Y0 - Y0.mean(), LAM_GRID)
            sc = np.mean(loo ** 2)
            if best is None or sc < best[0]:
                best = (sc, ell, lam, fit, loo)
        _, ell, lam, fit, loo = best
        K00 = M.rbf(Z0, Z0, ell)
        K10 = M.rbf(Z1, Z0, ell)
        coef = solve(K00 + lam * np.eye(len(C)), Y0 - Y0.mean(), assume_a='pos')
        m1hat = Y0.mean() + K10 @ coef
        # balancing weights: same kernel, penalty by the Riesz loss
        pen = M.riesz_cv_pen(Z0, Z1, ell, PEN_GRID, rng)
        k01 = K10.T.mean(1)
        w = M.kr_weights(K00, k01, pen)
        se_w = float(np.sqrt(np.sum(w ** 2 * loo ** 2)))
        if want('bal_generic'):
            out['bal_generic'] = wald(float(w @ Y0), se_w)
        if want('aug_generic'):
            out['aug_generic'] = wald(float(m1hat.mean() + w @ (Y0 - (Y0.mean() + K00 @ coef))), se_w)
        if want('aug_sim'):
            r_sim = Y0 - (Y0 - r0)                     # residuals of the calibrated simulator = r0
            _, loo_s, _ = M.gcv_ridge(K00, r0, LAM_GRID)
            out['aug_sim'] = wald(float(f1.mean() + w @ r0), float(np.sqrt(np.sum(w ** 2 * loo_s ** 2))))

    if want('baraspesha'):
        est, se, mb, w = baraspesha(Z, C, T, f1, J0, r0, S1, P)
        c = M.cv_alpha(mb / se) if se > 0 else Z975
        out['baraspesha'] = (est, se, est - c * se, est + c * se)
        out['baraspesha_wald'] = wald(est, se)
        out['_bar_maxbias'] = (mb, se, 1 / float(w @ w), np.nan)
    return out


def phys_parts(Z, C, T, J0, r0, S1, P):
    """Physics kernel on the measured controls and the treated wells: K00, k01 = mean_T K(X0, .), k11."""
    Zm = Z[:, [1, 3]]                                   # position along the coast and measured conductivity
    s2c = r0 @ r0 / max(len(C) - 3, 1)                  # parametric error left after calibration:
    G = P['kcal'] ** 2 * s2c * np.linalg.pinv(J0.T @ J0)  # kcal calibration standard errors in every direction
    K00 = phys_kernel(J0, J0, Zm[C], Zm[C], Z[C], Z[C], P, G)
    k01 = phys_kernel(J0, S1, Zm[C], Zm[T], Z[C], Z[T], P, G).mean(1)
    k11 = phys_kernel(S1, S1, Zm[T], Zm[T], Z[T], Z[T], P, G).mean()
    return K00, k01, k11, G


def noise_model(sK, e2):
    """Physics form of the noise variance: var(Y | X) = a + b s_K(X)^2 (pumping-test error propagated through the
    sensitivity to conductivity), fitted by nonnegative least squares to squared leave-one-out residuals."""
    X = np.column_stack([np.ones(len(sK)), sK ** 2])
    coef, _ = nnls(X, e2)
    return coef


def baraspesha(Z, C, T, f1, J0, r0, S1, P=PHYS):
    """The calibrated simulator augmented with minimax weights in the physics kernel. Returns the estimate, a
    heteroscedasticity-robust standard error, the worst-case bias over the unit ball of the kernel and the weights."""
    K00, k01, k11, _ = phys_parts(Z, C, T, J0, r0, S1, P)
    _, loo, _ = M.gcv_ridge(K00, r0, LAM_GRID)
    a, b = noise_model(J0[:, 0], loo ** 2)
    d = np.clip(a + b * J0[:, 0] ** 2, 1e-4, None)
    w = M.kr_weights(K00, k01, d)
    est = float(f1.mean() + w @ r0)
    se = float(np.sqrt(np.sum(w ** 2 * loo ** 2)))
    mb = float(np.sqrt(max(M.imbalance2(K00, k01, k11, w), 0)))
    return est, se, mb, w
