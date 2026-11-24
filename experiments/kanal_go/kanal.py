"""KANAL-GO: which pumping experiment measures the causal information flow from pumping to the toe best?

World: the RRJEDHA-GO well field (../rrjedha_go/rrjedha.py): the operator's annual decision A in {0, 1} given an
alarm level R (4 classes), drought D (3) and last year's decision; the yearly toe change dX in 3 classes; both
potential outcomes (twin worlds) for every well-year.

Goal: the interventional information flow of a pumping rule pi(a | r) (Ay-Polani type),
    TE(pi) = sum_r p(r) sum_a pi(a|r) KL( P(dX | do a, r) || sum_a' pi(a'|r) P(dX | do a', r) )   [bits],
for three rules: the operator's own marginal rule, a cautious rule, and the balanced rule pi = 1/2 (which, for
weak effects, equals the causal channel capacity of pumping at each alarm level).

Designs: a one-year pumping test on n well-years drawn from the field, with pumping randomized as
q(1 | r): 'natural' q = pi (follow the target rule), 'balanced' q = 1/2, 'capped' q = 1/2 except at the highest
alarm level where q is capped at the operator's own rate; and, as a reference, the operator's records with
back-door adjustment for (D, A_prev).

Small-effect theory (derived in the report): with Delta_k = P(k | do 1, r) - P(k | do 0, r),
    TE_r(pi) ~ 4 pi (1 - pi) C_r,   C_r ~ chi2_r / (8 ln 2),   chi2_r = sum_k Delta_k^2 / Pbar_k,
and the variance-optimal allocation for TE(pi) is q*(a|r) ~ pi(a|r) sd_a,r ~ pi(a|r) pi(1-a|r), i.e. q* = 1/2 for
every rule. The variance ratio natural / balanced at level r is 1 / (4 pi (1 - pi))."""
import os
import sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
for p in (os.path.join(HERE, '..', 'rrjedha_go'), os.path.join(HERE, '..', 'rrjedha')):
    if os.path.isdir(p):
        sys.path.insert(0, p)
import rrjedha as Rj

NR, NK, ND = 4, 3, 3
ALPHA = 0.5                                   # Dirichlet pseudo-count per (a, r) cell distribution


def world(n, rng, dbins, dxbins):
    d = Rj.simulate(n, rng, dbins=dbins, dxbins=dxbins)
    return dict(R=d['R'], D=d['D'], Ap=d['Aprev'].astype(int), A=d['A'].astype(int),
                K=d['dXb'], K0=d['dX0b'], K1=d['dX1b'], dX0=d['dX0'], dX1=d['dX1'])


def te_batch(pdo, pi, pr):
    """pdo[..., a, r, k], pi[r, a], pr[..., r] -> TE in bits, vectorized over leading axes."""
    M = np.einsum('ra,...ark->...rk', pi, pdo)
    with np.errstate(divide='ignore', invalid='ignore'):
        L = np.where(pdo > 0, pdo * np.log2(pdo / M[..., None, :, :]), 0.0)
    return np.einsum('...r,ra,...ar->...', pr, pi, L.sum(-1))


def truth(w):
    pdo = np.zeros((2, NR, NK))
    for a, key in ((0, 'K0'), (1, 'K1')):
        for r in range(NR):
            m = w['R'] == r
            pdo[a, r] = np.bincount(w[key][m], minlength=NK) / m.sum()
    pr = np.bincount(w['R'], minlength=NR) / len(w['R'])
    pA = np.array([w['A'][w['R'] == r].mean() for r in range(NR)])
    return pdo, pr, pA


def rule(p1):
    p1 = np.asarray(p1, float)
    return np.stack([1 - p1, p1], axis=1)                 # pi[r, a]


def capacity(pdo):
    """binary-input channel capacity per alarm level (bits) and the capacity-achieving P(A = 1)."""
    ps = np.linspace(0.0005, 0.9995, 1999)
    C, pst = np.zeros(NR), np.zeros(NR)
    for r in range(NR):
        best = -1
        for p in ps:
            v = te_batch(pdo[:, r:r + 1, :], rule([p]), np.array([1.0]))
            if v > best:
                best, bp = v, p
        C[r], pst[r] = best, bp
    return C, pst


def chi2_cap(pdo):
    D = pdo[1] - pdo[0]; Pb = 0.5 * (pdo[0] + pdo[1])
    return (D ** 2 / Pb).sum(-1) / (8 * np.log(2))


# --------------------------------------------------------------------- designs and estimators
def run_design(w, idx, q1, rng):
    """randomized one-year pumping test on rows idx with P(A = 1 | R) = q1[R]; returns counts[a, r, k]."""
    R = w['R'][idx]
    A = (rng.random(len(idx)) < q1[R]).astype(int)
    K = np.where(A == 1, w['K1'][idx], w['K0'][idx])
    cnt = np.zeros((2, NR, NK)); np.add.at(cnt, (A, R, K), 1)
    return cnt


def est_rand(cnt, pi):
    """plug-in TE(pi) from randomized counts[..., a, r, k]."""
    n_ar = cnt.sum(-1, keepdims=True)
    pdo = (cnt + ALPHA / NK) / (n_ar + ALPHA)
    nr = cnt.sum(axis=(-3, -1)); pr = nr / nr.sum(-1, keepdims=True)
    return te_batch(pdo, pi, pr)


def obs_counts(w, idx):
    cnt = np.zeros((NK, 2, NR, ND, 2))
    np.add.at(cnt, (w['K'][idx], w['A'][idx], w['R'][idx], w['D'][idx], w['Ap'][idx]), 1)
    return cnt


def est_obs(cnt, pi):
    """back-door adjusted TE(pi) from observational counts[..., k, a, r, d, ap]."""
    pk = (cnt + ALPHA / NK) / (cnt.sum(-5, keepdims=True) + ALPHA)
    c_rdap = cnt.sum(axis=(-5, -4))
    p_dap = c_rdap / np.maximum(c_rdap.sum(axis=(-2, -1), keepdims=True), 1e-12)
    pdo = np.einsum('...karde,...rde->...ark', pk, p_dap)
    nr = c_rdap.sum(axis=(-2, -1)); pr = nr / nr.sum(-1, keepdims=True)
    return te_batch(pdo, pi, pr)


def boot(cnt, f, B, rng):
    """multinomial bootstrap of the cell table; returns the bias-corrected estimate and the basic interval."""
    n = int(cnt.sum()); p = cnt.ravel() / n
    cs = rng.multinomial(n, p, size=B).reshape((B,) + cnt.shape).astype(float)
    e = f(cnt); eb = f(cs)
    return 2 * e - eb.mean(), (2 * e - np.quantile(eb, 0.975), 2 * e - np.quantile(eb, 0.025)), e
