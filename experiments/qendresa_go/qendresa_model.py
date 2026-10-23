"""QENDRESA-GO: a frugal model of salinization onset with a marginal structural hazard model as its causal margin.

A well is followed for K pumping seasons. At the start of season k (k = 1..K):
  L_k  dryness (water-level deficit), Gaussian:  L_1 = mu1 + sd1 W_1,
       L_k = g0 + g1 L_{k-1} + g2 A_{k-1} + sdL W_k   (pumping deepens next season's deficit);
  A_k  high pumping, A_k | L_k, A_{k-1} ~ Bern(expit(b0 + b1 L_k + b2 A_{k-1}))  (managers pump less when dry);
  D_k  the well salinizes in season k (chloride crosses the threshold); T = first k with D_k = 1 (K + 1 if none).
Causal margin (the marginal structural hazard model, grouped proportional hazards / complementary log-log):
  lambda(k; a) = P(T^a = k | T^a >= k) = 1 - exp(-exp(a0 + a1 (k-1) + beta a_k + betal a_{k-1})),   a_0 = 0.
Copula: W_1..W_K are the Rosenblatt scores of the dryness process; the latent rank of the failure time is
  V = rho (W_1 + ... + W_K) + sqrt(1 - K rho^2) eps,   U = Phi(V),   T = min{k : U > S(k; A)},
  S(k; a) = exp(-sum_{j<=k} exp(a0 + a1 (j-1) + beta a_j + betal a_{j-1})).
Theorem I of review 38: for every static regime a, T^a has exactly the hazards lambda(k; a); A_k is sequentially
ignorable given (L_1..L_k, A_1..A_{k-1}); the past, the hazard model and rho are variation independent.
'tcop' replaces the Gaussian copula by a Student-t copula with the same correlation (the causal margin stays exact).
"""
import numpy as np
from scipy.special import expit, ndtr, ndtri, log_ndtr
from scipy.stats import t as student_t, chi2

K = 5
PAST = dict(mu1=0.0, sd1=1.0, g0=0.0, g1=0.5, g2=0.6, sdL=0.8, b0=0.4, b1=-0.9, b2=0.8)
WEAK = dict(PAST, b0=1.2, b1=-1.8, b2=0.8)                       # strong confounding, near-violations of positivity
MSM = dict(a0=-2.8, a1=0.15, beta=0.5, betal=0.25)
NULL = dict(a0=-2.55, a1=0.15, beta=0.0, betal=0.0)               # no effect of pumping, similar event rate
RHO = 0.35
THETA_NAMES = ['a0', 'a1', 'beta', 'betal']


def theta_vec(msm):
    return np.array([msm[k] for k in THETA_NAMES])


def lin_pred(A, th):
    """eta[:, k] = a0 + a1 k + beta A_k + betal A_{k-1} (0-based k) for an n x K treatment matrix."""
    Alag = np.concatenate([np.zeros((A.shape[0], 1)), A[:, :-1]], axis=1)
    kk = np.arange(A.shape[1])[None, :]
    return th[0] + th[1] * kk + th[2] * A + th[3] * Alag


def surv_thresholds(A, th):
    """c[:, k] = Phi^-1(S(k+1; A)): the failure happens in season k+1 iff c[:, k] < V <= c[:, k-1]."""
    H = np.cumsum(np.exp(lin_pred(A, th)), axis=1)
    return -ndtri(-np.expm1(-H)), H


def simulate(n, rng, past=PAST, msm=MSM, rho=RHO, copula='gauss', nu=4, regime=None, tau=None):
    """Observed data (regime None), a static regime (array of K zeros/ones) or the dynamic rule A_k = 1{L_k < tau}.
    Returns L, A (n x K, full paths; entries after the failure are not observed), T (1..K+1), event, tlast."""
    p = past
    W = rng.standard_normal((n, K))
    eps = rng.standard_normal(n)
    xi = rng.random((n, K))
    chis = rng.chisquare(nu, n) if copula == 'tcop' else None
    L = np.zeros((n, K)); A = np.zeros((n, K))
    for k in range(K):
        aprev = A[:, k - 1] if k else np.zeros(n)
        L[:, k] = p['mu1'] + p['sd1'] * W[:, 0] if k == 0 else p['g0'] + p['g1'] * L[:, k - 1] + p['g2'] * aprev + p['sdL'] * W[:, k]
        if regime is not None:
            A[:, k] = regime[k]
        elif tau is not None:
            A[:, k] = (L[:, k] < tau).astype(float)
        else:
            A[:, k] = (xi[:, k] < expit(p['b0'] + p['b1'] * L[:, k] + p['b2'] * aprev)).astype(float)
    V = rho * W.sum(1) + np.sqrt(1 - K * rho ** 2) * eps
    if copula == 'tcop':
        logU = np.log(np.clip(student_t.cdf(V / np.sqrt(chis / nu), nu), 1e-300, 1))
    else:
        logU = log_ndtr(V)
    th = theta_vec(msm)
    H = np.cumsum(np.exp(lin_pred(A, th)), axis=1)
    fail = logU[:, None] > -H                                    # U > S(k)  <=>  log U > -H_k
    T = np.where(fail.any(1), fail.argmax(1) + 1, K + 1)
    event = T <= K
    tlast = np.minimum(T, K)
    return dict(L=L, A=A, T=T, event=event, tlast=tlast, W=W)


def true_static(msm=MSM):
    """Exact counterfactual survival S(k; a) for the 2^K static regimes (rows) and seasons 1..K (columns)."""
    regs = np.array([[(r >> j) & 1 for j in range(K)] for r in range(2 ** K)], float)
    return regs, np.exp(-np.cumsum(np.exp(lin_pred(regs, theta_vec(msm))), axis=1))


def cond_hazard(m, s, c_prev, c_now):
    """Proposition J: P(T = k | T >= k, history) = 1 - Phi((c_k - m_k)/s_k) / Phi((c_{k-1} - m_k)/s_k)."""
    return 1 - np.exp(log_ndtr((c_now - m) / s) - log_ndtr((c_prev - m) / s))


def dynamic_truth(taus, past=PAST, msm=MSM, rho=RHO, copula="gauss", n=2_000_000, seed=11):
    """Risk P(T^g <= K) and yield E[sum_k A_k^g 1{T^g >= k}] of the rules A_k = 1{L_k < tau}, by large simulation
    with the failure-time noise integrated out analytically (Gaussian copula) or simulated ('tcop')."""
    out = []
    for tau in taus:
        rng = np.random.default_rng(seed)
        if copula == 'gauss':
            r, y = frugal_rule_value(dict(past=past, th=theta_vec(msm), rho=rho), tau, rng.standard_normal((n, K)))
        else:
            D = simulate(n, rng, past, msm, rho, copula=copula, tau=tau)
            alive = np.arange(1, K + 1)[None, :] <= D['T'][:, None]
            r, y = D['event'].mean(), (D['A'] * alive).sum(1).mean()
        out.append((float(r), float(y)))
    return np.array(out)


def frugal_rule_value(par, tau, W):
    """Risk and yield of the rule A_k = 1{L_k < tau} in a Gaussian frugal model with parameters
    par = dict(past=dict(mu1, sd1, g0, g1, g2, sdL), th=(a0, a1, beta, betal), rho), using the scores W (M x K):
    P(T^g > k | W) = Phi((c_k(A^g) - m_K) / s_K) with m_K = rho sum_k W_k, s_K^2 = 1 - K rho^2."""
    p, th, rho = par['past'], np.asarray(par['th']), par['rho']
    M = W.shape[0]
    L = np.zeros((M, K)); A = np.zeros((M, K))
    for k in range(K):
        L[:, k] = p['mu1'] + p['sd1'] * W[:, 0] if k == 0 else p['g0'] + p['g1'] * L[:, k - 1] + p['g2'] * A[:, k - 1] + p['sdL'] * W[:, k]
        A[:, k] = (L[:, k] < tau).astype(float)
    c, _ = surv_thresholds(A, th)
    m, s = rho * W.sum(1), np.sqrt(1 - K * rho ** 2)
    S = ndtr((c - m[:, None]) / s)                               # P(T > k | W), k = 1..K
    Sprev = np.concatenate([np.ones((M, 1)), S[:, :-1]], axis=1)  # P(T >= k | W)
    return float(1 - S[:, -1].mean()), float((A * Sprev).sum(1).mean())
