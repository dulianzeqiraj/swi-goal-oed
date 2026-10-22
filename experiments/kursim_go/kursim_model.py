"""KURSIM-GO model: a frugal (Evans-Didelez) model of pumping and chloride with salinity-alarm feedback.

One unit is a supply well over two pumping seasons.
  L1 ~ N(0, 1)                                   dryness (recharge deficit) before season 1
  A1 | L1 ~ Bernoulli(expit(a0 + a1 L1))          high pumping in season 1
  L2 | L1, A1 ~ Bernoulli(pi(L1, A1)),            chloride alarm after season 1,
        pi = expit(g0 + g1 L1 + g2 A1)
  A2 | L1, A1, L2 ~ Bernoulli(expit(b0 + b1 L1 + b2 A1 + b3 L2))   high pumping in season 2 (b3 < 0: cut after alarm)
  Y  = log chloride at the supply well after season 2.

Frugal parameterization: the past (L1, A1, L2, A2) as above; the causal margin (a marginal structural model)
    Y | do(a1, a2) ~ N(theta0 + theta1 a1 + theta2 a2, s^2);
and a Gaussian copula linking Y with the Rosenblatt scores of (L1, L2) under the intervention:
    W1 = L1,  W2 ~ N(0, 1) truncated to the interval that L2 occupies, (-inf, t) if L2 = 0 and (t, inf) if L2 = 1,
    t = Phi^-1(1 - pi(L1, A1)),
    Y = theta0 + theta1 A1 + theta2 A2 + s (rho1 W1 + rho2 W2 + c eps),  c = sqrt(1 - rho1^2 - rho2^2).
Under do(a1, a2), (W1, W2) are independent standard normals, so the causal margin holds exactly whatever the past,
the policy and the copula parameters (Theorem A of the review).
"""
import numpy as np
from scipy.special import expit, ndtri, log_ndtr, ndtr

PAST = dict(a0=-0.2, a1=0.9, g0=-1.0, g1=0.8, g2=1.4, b0=0.4, b1=0.5, b2=0.6, b3=-2.2)
CAUSAL = dict(theta0=5.3, theta1=0.25, theta2=0.45, s=0.5)
COPULA = dict(rho1=0.35, rho2=0.55)


def simulate(n, rng, past=PAST, causal=CAUSAL, cop=COPULA, copula='gauss', nu=4.0, regime=None):
    """Observational data (regime None) or data under the intervention do(a1, a2) = regime."""
    p = past
    L1 = rng.standard_normal(n)
    A1 = (rng.random(n) < expit(p['a0'] + p['a1'] * L1)).astype(float) if regime is None else np.full(n, float(regime[0]))
    pi = expit(p['g0'] + p['g1'] * L1 + p['g2'] * A1)
    U2 = rng.random(n)
    L2 = (U2 > 1 - pi).astype(float)                    # U2 is the jittered Rosenblatt score of L2
    A2 = (rng.random(n) < expit(p['b0'] + p['b1'] * L1 + p['b2'] * A1 + p['b3'] * L2)).astype(float) if regime is None \
        else np.full(n, float(regime[1]))
    V = score(np.column_stack([ndtr(L1), U2]), rng, cop, copula, nu)
    Y = causal['theta0'] + causal['theta1'] * A1 + causal['theta2'] * A2 + causal['s'] * V
    return dict(L1=L1, A1=A1, L2=L2, A2=A2, Y=Y, pi=pi)


def score(U, rng, cop, copula='gauss', nu=4.0):
    """Normal score V of the outcome given the uniform Rosenblatt scores U = (U1, U2) of the past, drawn from the
    conditional copula; V ~ N(0, 1) marginally (exact causal margin)."""
    r1, r2 = cop['rho1'], cop['rho2']
    n = U.shape[0]
    if copula == 'gauss':
        W = ndtri(np.clip(U, 1e-15, 1 - 1e-15))
        return r1 * W[:, 0] + r2 * W[:, 1] + np.sqrt(1 - r1 ** 2 - r2 ** 2) * rng.standard_normal(n)
    # Student-t conditional with nu degrees of freedom: given the past scores T = F_nu^-1(U), the latent outcome score is
    # TV = rho1 T1 + rho2 T2 + scale(T) * t_{nu+2}; it is mapped to V = Phi^-1(G(TV)) with G the exact marginal law of TV
    # (U1, U2 independent uniform), so V ~ N(0, 1) and the causal margin stays exact (only the copula is non-Gaussian).
    from scipy.stats import t as tdist
    T = tdist.ppf(np.clip(U, 1e-15, 1 - 1e-15), nu)
    q = (T ** 2).sum(1)
    mu = r1 * T[:, 0] + r2 * T[:, 1]
    scale = np.sqrt((1 - r1 ** 2 - r2 ** 2) * (nu + q) / (nu + 2))
    TV = mu + scale * tdist.rvs(nu + 2, size=n, random_state=rng)
    xs, G = _t_margin(r1, r2, nu)
    return ndtri(np.clip(np.interp(TV, xs, G), 1e-15, 1 - 1e-15))


_TCACHE = {}


def _t_margin(r1, r2, nu, m=2 ** 16):
    """Marginal CDF of the latent score TV of the Student-t conditional, by randomized quasi-Monte Carlo over the two
    independent uniform past scores (Sobol points, 2^16) on a grid of 2401 values; error well below 1e-4."""
    key = (r1, r2, nu)
    if key not in _TCACHE:
        from scipy.stats import qmc, t as tdist
        P = qmc.Sobol(2, scramble=True, seed=12345).random(m)
        T = tdist.ppf(P, nu)
        mu = r1 * T[:, 0] + r2 * T[:, 1]
        scale = np.sqrt((1 - r1 ** 2 - r2 ** 2) * (nu + (T ** 2).sum(1)) / (nu + 2))
        xs = np.concatenate([-np.logspace(3, np.log10(12), 200), np.linspace(-12, 12, 2001), np.logspace(np.log10(12), 3, 200)])
        xs = np.unique(xs)
        G = np.array([tdist.cdf((x - mu) / scale, nu + 2).mean() for x in xs])
        _TCACHE[key] = (xs, G)
    return _TCACHE[key]


def cond_mean(L1, A1, L2, A2, past=PAST, causal=CAUSAL, cop=COPULA):
    """Exact observational regression E[Y | L1, A1, L2, A2] of the Gaussian frugal model (Proposition 2):
    the causal mean plus s rho1 L1 plus s rho2 times the mean of the truncated score (inverse Mills ratio)."""
    pi = expit(past['g0'] + past['g1'] * L1 + past['g2'] * A1)
    t = ndtri(1 - pi)
    phi = np.exp(-0.5 * t ** 2) / np.sqrt(2 * np.pi)
    mills = np.where(L2 > 0.5, phi / pi, -phi / (1 - pi))
    return (causal['theta0'] + causal['theta1'] * A1 + causal['theta2'] * A2
            + causal['s'] * (cop['rho1'] * L1 + cop['rho2'] * mills))


# ---------------------------------------------------------------- frugal likelihood
def unpack(v):
    g0, g1, g2, th0, th1, th2, ls, z1, z2 = v
    d = np.sqrt(1 + z1 ** 2 + z2 ** 2)
    return (g0, g1, g2), (th0, th1, th2), np.exp(ls), z1 / d, z2 / d


def loglik_obs(v, D):
    """Per-observation log-likelihood of (L2, Y) given (L1, A1, A2) in the Gaussian frugal model:
    ln p(l2, y | l1, a1, a2) = ln[ phi(r / tau) / tau ] + ln P(W2 in interval(l2) | R = r)."""
    (g0, g1, g2), (th0, th1, th2), s, r1, r2 = unpack(v)
    pi = expit(g0 + g1 * D['L1'] + g2 * D['A1'])
    t = ndtri(np.clip(1 - pi, 1e-15, 1 - 1e-15))
    r = D['Y'] - th0 - th1 * D['A1'] - th2 * D['A2'] - s * r1 * D['L1']
    tau2 = s ** 2 * (1 - r1 ** 2)
    mw = r * s * r2 / tau2
    sw = np.sqrt((1 - r1 ** 2 - r2 ** 2) / (1 - r1 ** 2))
    tail = np.where(D['L2'] > 0.5, log_ndtr((mw - t) / sw), log_ndtr((t - mw) / sw))
    return -0.5 * np.log(2 * np.pi * tau2) - r ** 2 / (2 * tau2) + tail


def true_vector(past=PAST, causal=CAUSAL, cop=COPULA):
    r1, r2 = cop['rho1'], cop['rho2']
    c = np.sqrt(1 - r1 ** 2 - r2 ** 2)
    return np.array([past['g0'], past['g1'], past['g2'], causal['theta0'], causal['theta1'], causal['theta2'],
                     np.log(causal['s']), r1 / c, r2 / c])
