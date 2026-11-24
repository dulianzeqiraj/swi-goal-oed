"""BESA-GO data-generating processes and the frugal likelihood with a treatment-dependent Gaussian copula.

The past, policy and causal margin are those of KURSIM-GO (experiments/kursim_go/kursim_model.py):
  L1 ~ N(0,1); A1 | L1 ~ Bern(expit(a0 + a1 L1)); L2 | L1, A1 ~ Bern(pi), pi = expit(g0 + g1 L1 + g2 A1);
  A2 | L1, A1, L2 ~ Bern(expit(b0 + b1 L1 + b2 A1 + b3 L2 [+ b4 (L1^2 - 1) + b5 L1 L2]));
  Y | do(a1, a2) ~ N(theta0 + theta1 a1 + theta2 a2, s^2)   (exact for every copula below).
Copulas (W1 = L1, W2 = the jittered normal score of the alarm, V = normal score of Y):
  'gauss'  V = rho1 W1 + rho2 W2 + c eps with (rho1, rho2) that may depend on a2 (the frugal family allows a copula
           c*_a for every treatment value); c = sqrt(1 - rho1^2 - rho2^2);
  'skewdry' V = Phi^-1(G(rho1 h(W1) + rho2 W2 + c eps)), h a standardized exponential (very dry years salinize
           disproportionately) and G the exact law of the latent score (quasi-Monte Carlo table), so V ~ N(0, 1).
"""
import os, sys
import numpy as np
from scipy.special import expit, ndtri, log_ndtr
from scipy.stats import qmc

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kursim_go'))
import kursim_model as K  # noqa: E402

PAST = dict(K.PAST, b4=0.0, b5=0.0)
CAUSAL = dict(K.CAUSAL)
NULL = dict(CAUSAL, theta1=0.0, theta2=0.0)
COMMON = dict(rho1=(0.35, 0.35), rho2=(0.55, 0.55))          # (value when a2 = 0, value when a2 = 1)
PUMPDEP = dict(rho1=(0.35, 0.35), rho2=(0.30, 0.80))          # pumping strengthens the alarm-chloride link
WRONGPROP = dict(PAST, b4=1.0, b5=1.5)                        # season-2 policy with curvature and an interaction


def h_skew(w, k=1.0):
    return (np.exp(k * w) - np.exp(k * k / 2)) / np.sqrt(np.exp(2 * k * k) - np.exp(k * k))


_TAB = {}


def _skew_table(r1, r2, k=1.0, m=2 ** 18):
    key = (r1, r2, k)
    if key not in _TAB:
        Z = ndtri(np.clip(qmc.Sobol(3, scramble=True, seed=7).random(m), 1e-12, 1 - 1e-12))
        _TAB[key] = np.sort(r1 * h_skew(Z[:, 0], k) + r2 * Z[:, 1] + np.sqrt(1 - r1 ** 2 - r2 ** 2) * Z[:, 2])
    return _TAB[key]


def simulate(n, rng, past=PAST, causal=CAUSAL, cop=COMMON, copula='gauss', regime=None, k=1.0):
    p = past
    L1 = rng.standard_normal(n)
    A1 = (rng.random(n) < expit(p['a0'] + p['a1'] * L1)).astype(float) if regime is None else np.full(n, float(regime[0]))
    pi = expit(p['g0'] + p['g1'] * L1 + p['g2'] * A1)
    U2 = rng.random(n)
    L2 = (U2 > 1 - pi).astype(float)
    if regime is None:
        eta = p['b0'] + p['b1'] * L1 + p['b2'] * A1 + p['b3'] * L2 + p['b4'] * (L1 ** 2 - 1) + p['b5'] * L1 * L2
        A2 = (rng.random(n) < expit(eta)).astype(float)
    else:
        A2 = np.full(n, float(regime[1]))
    W2 = ndtri(np.clip(U2, 1e-15, 1 - 1e-15))
    j = (A2 > 0.5).astype(int)
    r1, r2 = np.asarray(cop['rho1'])[j], np.asarray(cop['rho2'])[j]
    eps = rng.standard_normal(n)
    if copula == 'gauss':
        V = r1 * L1 + r2 * W2 + np.sqrt(1 - r1 ** 2 - r2 ** 2) * eps
    elif copula == 'skewdry':
        assert np.ptp(cop['rho1']) == 0 and np.ptp(cop['rho2']) == 0
        R1, R2 = cop['rho1'][0], cop['rho2'][0]
        T = _skew_table(R1, R2, k)
        Vs = R1 * h_skew(L1, k) + R2 * W2 + np.sqrt(1 - R1 ** 2 - R2 ** 2) * eps
        V = ndtri(np.clip((np.searchsorted(T, Vs) + 0.5) / (len(T) + 1), 1e-12, 1 - 1e-12))
    else:
        raise ValueError(copula)
    Y = causal['theta0'] + causal['theta1'] * A1 + causal['theta2'] * A2 + causal['s'] * V
    return dict(L1=L1, A1=A1, L2=L2, A2=A2, Y=Y)


# ---------------------------------------------------------------- frugal likelihood, common or pumping-dependent copula
NPAR = {'common': 9, 'flex': 11}


def unpack(v, kind, A2):
    """(g, theta, s, rho1_i, rho2_i): copula parameters per observation; 'flex' lets them depend on a2."""
    g, th, s = v[0:3], v[3:6], np.exp(v[6])
    if kind == 'common':
        z1, z2 = v[7], v[8]
        d = np.sqrt(1 + z1 ** 2 + z2 ** 2)
        r1, r2 = np.full(len(A2), z1 / d), np.full(len(A2), z2 / d)
    else:
        z = np.array([[v[7], v[8]], [v[9], v[10]]])
        d = np.sqrt(1 + (z ** 2).sum(1))
        j = (A2 > 0.5).astype(int)
        r1, r2 = (z[:, 0] / d)[j], (z[:, 1] / d)[j]
    return g, th, s, r1, r2


def rho_of(v, kind):
    """Copula parameters (rho1, rho2) for a2 = 0 and a2 = 1."""
    if kind == 'common':
        z = np.array([[v[7], v[8]], [v[7], v[8]]])
    else:
        z = np.array([[v[7], v[8]], [v[9], v[10]]])
    d = np.sqrt(1 + (z ** 2).sum(1))
    return z[:, 0] / d, z[:, 1] / d


def loglik(v, D, kind='common'):
    """Per-observation log p(l2, y | l1, a1, a2) of Theorem C, with copula parameters evaluated at a2."""
    g, th, s, r1, r2 = unpack(v, kind, D['A2'])
    pi = expit(g[0] + g[1] * D['L1'] + g[2] * D['A1'])
    t = ndtri(np.clip(1 - pi, 1e-15, 1 - 1e-15))
    r = D['Y'] - th[0] - th[1] * D['A1'] - th[2] * D['A2'] - s * r1 * D['L1']
    tau2 = s ** 2 * (1 - r1 ** 2)
    mw = r * s * r2 / tau2
    sw = np.sqrt((1 - r1 ** 2 - r2 ** 2) / (1 - r1 ** 2))
    tail = np.where(D['L2'] > 0.5, log_ndtr((mw - t) / sw), log_ndtr((t - mw) / sw))
    return -0.5 * np.log(2 * np.pi * tau2) - r ** 2 / (2 * tau2) + tail


def true_vector(past=PAST, causal=CAUSAL, cop=COMMON, kind='common'):
    out = [past['g0'], past['g1'], past['g2'], causal['theta0'], causal['theta1'], causal['theta2'], np.log(causal['s'])]
    for j in ((0,) if kind == 'common' else (0, 1)):
        r1, r2 = cop['rho1'][j], cop['rho2'][j]
        c = np.sqrt(1 - r1 ** 2 - r2 ** 2)
        out += [r1 / c, r2 / c]
    return np.array(out)
