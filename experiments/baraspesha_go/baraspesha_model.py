"""BARASPESHA-GO: augmented balancing weights when the outcome model is a complex simulator.

Physics: Strack's (1976) single-potential solution for a pumping well at distance xw from the coast of an
unconfined aquifer with a sharp interface. The discharge potential on the axis through the well is
    phi(x) = (q/K) x + Q/(2 pi K) log(|x - xw| / (x + xw)),
the stagnation point lies at xs = xw sqrt(1 - mu) with mu = Q / (pi q xw), and the well draws seawater when the
potential at the stagnation point falls below the toe potential phi_toe = delta (1 + delta) d^2 / 2. The margin
    m = phi_s / phi_toe - 1
is turned into log10 chloride of the pumped water through a mixing (dispersion) width omega:
    y = log10(C_f + C_s f_max Phi(-m / omega)).

Truth: hydraulic conductivity varies along the coast and from well to well, the aquifer base can vary along the
coast (scenario S3), the mixing width grows with pumping. The analyst's simulator ("the complex model") uses the
measured local conductivity (pumping test, biased and noisy), a constant base depth, a nominal regional flux and a
constant mixing width; three global parameters theta = (log K multiplier, log q multiplier, log omega multiplier)
can be calibrated.

Estimand: psi = mean over treated wells of m0(X) = E[Y(0) | X], the counterfactual mean log10 chloride of the
wells that cut pumping, had they not cut it; the effect on the treated is mean_T(Y) - psi.
"""
import numpy as np
from scipy.stats import norm
from scipy.special import roots_hermitenorm
from scipy.linalg import solve, eigh

DELTA, CF, CS, FMAX = 0.025, 50.0, 19000.0, 0.25
D0 = 30.0                                  # aquifer base below sea level used by the simulator (m)
Y_LEN = 10.0                               # length of the coast (km)
Q_TRUE, Q0_SIM = 0.8, 0.6                  # regional freshwater discharge to the sea (m2/day): truth, simulator
OMEGA_TRUE, OMEGA0_SIM, OMEGA_POW = 0.25, 0.40, 0.3
TAU_U, TAU_E, KMEAS_BIAS = 0.30, 0.25, 0.20  # well-to-well log K spread, pumping-test noise and bias
SIGMA_EPS = 0.08                           # measurement error of log10 chloride
CUT = 0.6                                  # treated wells pump 60% of their baseline
GH_Z, GH_W = roots_hermitenorm(24)
GH_W = GH_W / GH_W.sum()


def logK_trend(y):
    """Regional log K (m/day) along the coast, y in km."""
    return np.log(25.0) + 0.35 * np.sin(2 * np.pi * y / 7.0) + 0.20 * np.cos(2 * np.pi * y / 2.5)


def base_depth(y, s3=False):
    return D0 + (6.0 * np.sin(2 * np.pi * y / 5.0) if s3 else 0.0 * y)


def margin(xw, Q, K, q, d):
    phi_toe = DELTA * (1 + DELTA) * d ** 2 / 2
    mu = Q / (np.pi * q * xw)
    s = np.sqrt(np.clip(1 - mu, 1e-300, None))
    with np.errstate(divide='ignore', invalid='ignore'):
        g = s + 0.5 * mu * np.log((1 - s) / (1 + s))
    m = q * xw / K * g / phi_toe - 1
    return np.where(mu < 1, m, -1.0 - (mu - 1))


def log_chloride(m, omega):
    return np.log10(CF + CS * FMAX * norm.cdf(-m / omega))


def f_true(xw, Q, logK, y, s3=False):
    om = OMEGA_TRUE * (Q / 300.0) ** OMEGA_POW
    return log_chloride(margin(xw, Q, np.exp(logK), Q_TRUE, base_depth(y, s3)), om)


def f_sim(xw, Q, kmeas, theta, exact=False):
    """The analyst's simulator. theta = (log K multiplier, log q multiplier, log omega multiplier).
    exact=True gives the oracle simulator of scenario S4 (unbiased conductivity, true flux and mixing law)."""
    if exact:
        om = OMEGA_TRUE * (Q / 300.0) ** OMEGA_POW
        return log_chloride(margin(xw, Q, np.exp(kmeas - KMEAS_BIAS + theta[0]), Q_TRUE * np.exp(theta[1]), D0), om * np.exp(theta[2]))
    K = np.exp(kmeas + theta[0])
    return log_chloride(margin(xw, Q, K, Q0_SIM * np.exp(theta[1]), D0), OMEGA0_SIM * np.exp(theta[2]))


def sens(xw, Q, kmeas, theta, exact=False, h=1e-5):
    """Sensitivities d f_sim / d theta_j (central differences), n x 3."""
    out = np.empty((len(xw), 3))
    for j in range(3):
        e = np.zeros(3); e[j] = h
        out[:, j] = (f_sim(xw, Q, kmeas, theta + e, exact) - f_sim(xw, Q, kmeas, theta - e, exact)) / (2 * h)
    return out


def post_logK(kmeas, y):
    """Posterior of the well's log K given its pumping-test value and position (Gaussian prior around the trend)."""
    v = 1.0 / (1 / TAU_U ** 2 + 1 / TAU_E ** 2)
    mu = v * (logK_trend(y) / TAU_U ** 2 + (kmeas - KMEAS_BIAS) / TAU_E ** 2)
    return mu, np.sqrt(v)


def m_true(xw, Q, kmeas, y, s3=False):
    """E[Y | X] for pumping Q, integrating the well's unknown conductivity (Gauss-Hermite)."""
    mu, sd = post_logK(kmeas, y)
    vals = f_true(xw[:, None], Q[:, None], mu[:, None] + sd * GH_Z[None, :], y[:, None], s3)
    return vals @ GH_W


def draw_field(n, rng, alpha1=2.0, alpha0=None, s3=False):
    """One well field: covariates, treatment, outcomes, true conditional means."""
    xw = np.exp(rng.uniform(np.log(250.0), np.log(4000.0), n))
    y = rng.uniform(0, Y_LEN, n)
    Q0 = np.exp(rng.normal(np.log(300.0), 0.4, n))
    logK = logK_trend(y) + TAU_U * rng.standard_normal(n)
    kmeas = logK + KMEAS_BIAS + TAU_E * rng.standard_normal(n)
    risk = f_sim(xw, Q0, kmeas, np.zeros(3))                      # the agency's advice uses the nominal simulator
    lin = alpha1 * (risk - 2.5) - 0.8 * np.log(xw / 1000.0)
    if alpha0 is None:
        alpha0 = ALPHA0[alpha1]
    pA = 1 / (1 + np.exp(-(alpha0 + lin)))
    A = (rng.uniform(size=n) < pA).astype(int)
    Q = np.where(A == 1, CUT * Q0, Q0)
    Y = f_true(xw, Q, logK, y, s3) + SIGMA_EPS * rng.standard_normal(n)
    m0 = m_true(xw, Q0, kmeas, y, s3)
    m1 = m_true(xw, CUT * Q0, kmeas, y, s3)
    return dict(xw=xw, y=y, Q0=Q0, kmeas=kmeas, A=A, Y=Y, m0=m0, m1=m1, pA=pA, logK=logK)


ALPHA0 = {2.0: -2.577, 3.5: -4.154}        # intercepts giving 30% treated wells (root of mean pA = 0.30, 60 000 wells)


def features(F):
    """Standardized covariates used by the generic methods: log xw, y, log Q0, kmeas."""
    Z = np.column_stack([np.log(F['xw']), F['y'], np.log(F['Q0']), F['kmeas']])
    return Z


def standardize(Z, ref):
    mu, sd = ref.mean(0), ref.std(0)
    return (Z - mu) / sd


def rbf(A, B, ell):
    d2 = ((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)
    return np.exp(-0.5 * d2 / ell ** 2)


# ------------------------------------------------------------------------------------------------------------
# calibration of the simulator (Levenberg-Marquardt on the control wells)

def calibrate(xw, Q, kmeas, Yc, exact=False, iters=80, tol=1e-12, rho=0.05, bound=3.0):
    """Levenberg-Marquardt calibration of theta on the measured control wells, with a weak Tikhonov penalty
    rho |theta|^2 (prior standard deviation of about one log unit per parameter, as in regularized inversion)
    and |theta_j| <= bound. rho = 0 gives ordinary nonlinear least squares. Returns theta, the sensitivity matrix at
    theta and the residuals."""
    th = np.zeros(3); lam = 1e-2
    obj = lambda r, t: r @ r + rho * t @ t
    r = Yc - f_sim(xw, Q, kmeas, th, exact); ss = obj(r, th)
    for _ in range(iters):
        J = sens(xw, Q, kmeas, th, exact)
        G = J.T @ J + rho * np.eye(3); g = J.T @ r - rho * th
        step = solve(G + lam * np.diag(np.diag(G)) + 1e-12 * np.eye(3), g)
        th_new = np.clip(th + step, -bound, bound)
        r_new = Yc - f_sim(xw, Q, kmeas, th_new, exact); ss_new = obj(r_new, th_new)
        if ss_new < ss:
            done = ss - ss_new < tol * max(ss, 1e-12)
            th, r, ss = th_new, r_new, ss_new
            lam = max(lam / 3, 1e-9)
            if done:
                break
        else:
            lam *= 4
            if lam > 1e8:
                break
    J = sens(xw, Q, kmeas, th, exact)
    return th, J, r


# ------------------------------------------------------------------------------------------------------------
# kernel ridge machinery

def kr_weights(K00, k01, pen, normalize=True):
    """Ridge / minimax balancing weights in the RKHS of the kernel: minimize ||sum_i w_i k(X0_i,.) - kbar_1||^2
    + pen ||w||^2, with the weights summing to one (constants balanced exactly) when normalize is True:
    w = (K00 + pen I)^-1 (k01 + nu 1), nu chosen so that 1'w = 1."""
    A = K00 + (np.diag(pen) if np.ndim(pen) else pen * np.eye(len(k01)))
    a = solve(A, k01, assume_a='pos')
    if not normalize:
        return a
    b = solve(A, np.ones(len(k01)), assume_a='pos')
    return a + (1 - a.sum()) / b.sum() * b


def imbalance2(K00, k01, k11, w):
    return float(k11 - 2 * w @ k01 + w @ K00 @ w)


def gcv_ridge(K, r, grid):
    """Kernel ridge of r on K with the penalty chosen by generalized cross-validation; returns fit, LOO residuals."""
    lam_e, U = eigh(K)
    lam_e = np.clip(lam_e, 0, None)
    Ur = U.T @ r
    best = None
    n = len(r)
    for p in grid:
        h = lam_e / (lam_e + p)
        fit = U @ (h * Ur)
        tr = h.sum()
        g = ((r - fit) ** 2).mean() / (1 - tr / n) ** 2
        if best is None or g < best[0]:
            best = (g, p, fit, h)
    g, p, fit, h = best
    Hdiag = (U ** 2) @ h
    loo = (r - fit) / np.clip(1 - Hdiag, 1e-6, None)
    return fit, loo, p


def riesz_cv_pen(Z0, Z1, ell, grid, rng, folds=5):
    """Penalty of kernel ridge balancing weights chosen by cross-validating the Riesz loss
    E[alpha^2 | A=0] - 2 E[alpha | A=1] (automatic debiased ML)."""
    i0 = rng.permutation(len(Z0)) % folds
    i1 = rng.permutation(len(Z1)) % folds
    loss = np.zeros(len(grid))
    for k in range(folds):
        tr0, te0, tr1, te1 = Z0[i0 != k], Z0[i0 == k], Z1[i1 != k], Z1[i1 == k]
        K00 = rbf(tr0, tr0, ell); k01 = rbf(tr0, tr1, ell).mean(1)
        lam_e, U = eigh(K00); lam_e = np.clip(lam_e, 0, None)
        Uk = U.T @ k01; U1 = U.T @ np.ones(len(tr0))
        Kte0 = rbf(te0, tr0, ell); Kte1 = rbf(te1, tr0, ell)
        kbar_te0 = rbf(te0, tr1, ell).mean(1); kbar_te1 = rbf(te1, tr1, ell).mean(1)
        n0 = len(tr0)
        for g_i, p in enumerate(grid):
            a = U @ (Uk / (lam_e + p)); b = U @ (U1 / (lam_e + p))
            nu = (1 - a.sum()) / b.sum()
            w = a + nu * b
            # Riesz representer implied by the weights (KKT): alpha(x) = n0 * (kbar1(x) - sum_i w_i k(x, X0_i) + nu) / p
            a0 = n0 * (kbar_te0 - Kte0 @ w + nu) / p
            a1 = n0 * (kbar_te1 - Kte1 @ w + nu) / p
            loss[g_i] += (a0 ** 2).mean() - 2 * a1.mean()
    return grid[int(np.argmin(loss))]


def cv_alpha(t, alpha=0.05):
    """Critical value of a bias-aware interval: the 1-alpha quantile of |N(t, 1)| (Armstrong-Kolesar)."""
    from scipy.optimize import brentq
    t = abs(t)
    f = lambda c: norm.cdf(c - t) - norm.cdf(-c - t) - (1 - alpha)
    return brentq(f, 0, t + 10)
