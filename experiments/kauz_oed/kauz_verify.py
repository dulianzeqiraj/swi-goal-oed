"""KAUZ-OED: adversarial verification and extensions of the hidden-node FDT proposal.

Sections (each writes into one JSON file, results/kauz_verify.json of the M-estimator review):
  1 theorem   Lyapunov sign convention, C(tau) = e^{A tau} C(0), partial-FDT bias formula, integral formula,
              exact FDT for H = {}, the exact semigroup-defect identity, the necessary and sufficient
              condition for B_S == 0 and three counterexamples to the wording of the proposal; optional
              symbolic checks with sympy (skipped if sympy is not importable).
  2 numbers   Test 1 (oracle greedy of causal_ou.py, prior greedy of causal_prior*.py), the honest prior
              table for k = 0..8 with 10-90% bands, bootstrap standard errors and the full random baseline;
              optional Lorenz-96 robustness check (independent data set, truncation lag, out-of-sample set).
  3 chaos     1-D double well (not chaotic, non-Gaussian): exact score-FDT vs quasi-Gaussian FDT, by quadrature.
  4 pumping   pumping as a parametric perturbation A(Q) = A + Q A1 (+ b Q) of the 30-cell transect with a
              sea boundary: d xbar/dQ = -A^{-1}(A1 xbar + b), FDT with effective vs additive forcing,
              finite-record estimate of the effective-forcing response.
  5 semigroup population relation between defects and the integrated (g, p) bias over prior models and
              sensor sets; finite-record parametric-bootstrap tests (exact OU sampling).
  6 mse       finite-record variance of the integrated partial-FDT estimate, bias^2 + Var along the KAUZ
              sequence, MSE-greedy design vs bias-only design on independent test models.
Run:  python3 kauz_verify.py            (all sections, about 7 min on 2 shared cores)
      python3 kauz_verify.py --skip-l96 (without the Lorenz-96 check, about 1 min less)
Symbolic checks need sympy on PYTHONPATH (optional).
"""
import argparse
import json
import os
import sys
import time

os.environ.setdefault('OPENBLAS_NUM_THREADS', '2')
os.environ.setdefault('OMP_NUM_THREADS', '2')
import numpy as np
from scipy.linalg import solve_continuous_lyapunov, expm, cholesky
from scipy.optimize import brentq
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
MEA = os.path.abspath(os.path.join(HERE, '..', 'm_estimators_adaptive'))
OUT = os.path.join(MEA, 'results', 'kauz_verify.json')

n, P, G = 30, 8, 27
OTHERS = [i for i in range(n) if i not in (P, G)]
NEAR = sorted(OTHERS, key=lambda i: min(abs(i - P), abs(i - G)))


def conv(o):
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.bool_):
        return bool(o)
    raise TypeError(type(o))


# ----------------------------------------------------------------------------------------------- models
def build(adv, damp, cpl, back, qdiag):
    """Exactly the transect model of causal_ou.py / causal_prior.py."""
    A = np.zeros((n, n))
    for i in range(n):
        A[i, i] = -2.0 - damp
        if i > 0:
            A[i, i - 1] = 1.0 + adv
        if i < n - 1:
            A[i, i + 1] = 1.0 - adv
    A[22, 5] += cpl
    A[5, 22] += back
    Q = np.diag(qdiag)
    C0 = solve_continuous_lyapunov(A, -Q)
    return A, C0, Q


def truth():
    rng = np.random.default_rng(2)
    return build(0.35, 0.15, 0.6, 0.2, 0.2 + 0.8 * rng.random(n))


def draw(r):
    return build(r.uniform(0.25, 0.45), r.uniform(0.08, 0.25), r.uniform(0.2, 1.0), r.uniform(0.0, 0.4),
                 0.2 + 0.8 * r.random(n))


def design_ensemble():
    pr = np.random.default_rng(7)
    return [draw(pr) for _ in range(60)]


def test_models(m=200):
    return [draw(np.random.default_rng(1000 + s)) for s in range(m)]


class Model:
    """Pre-computed quantities of one linear model."""

    def __init__(self, A, C0, Q):
        self.A, self.C0, self.Q = A, C0, Q
        self.Ai = np.linalg.inv(A)
        self.Cint = -self.Ai @ C0                     # int_0^inf C(tau) dtau = -A^{-1} C(0)
        self.R = -self.Ai[G, P]                       # causal steady response of x_g to unit forcing at p

    def fdt(self, S):
        S = list(S)
        x = np.linalg.solve(self.C0[np.ix_(S, S)], np.eye(len(S))[:, S.index(P)])
        return self.Cint[G, S] @ x


def fdt_many(models, S):
    """Integrated partial-FDT estimate of R_gp for a list of models (vectorised)."""
    S = list(S)
    C0 = np.array([m.C0[np.ix_(S, S)] for m in models])
    rhs = np.zeros((len(models), len(S), 1)); rhs[:, S.index(P), 0] = 1
    x = np.linalg.solve(C0, rhs)[:, :, 0]
    ci = np.array([m.Cint[G, S] for m in models])
    return np.einsum('ms,ms->m', ci, x)


def greedy(models, kmax, crit):
    S = [P, G]; seq = [list(S)]
    for _ in range(kmax):
        S = S + [min((i for i in OTHERS if i not in S), key=lambda i: crit(S + [i]))]
        seq.append(list(S))
    return seq


# ----------------------------------------------------------------------------------------- 1. theorem
def van_loan_noise(A, Q, tau):
    m = A.shape[0]
    M = np.zeros((2 * m, 2 * m)); M[:m, :m] = -A; M[:m, m:] = Q; M[m:, m:] = A.T
    E = expm(M * tau)
    Phi = E[m:, m:].T
    return Phi, Phi @ E[:m, m:]


def van_loan_integral(A, T):
    m = A.shape[0]
    M = np.zeros((2 * m, 2 * m)); M[:m, :m] = A; M[:m, m:] = np.eye(m)
    return expm(M * T)[:m, m:]                         # int_0^T e^{A s} ds


def random_system(rng):
    m = int(rng.integers(3, 31))
    fam = int(rng.integers(4))
    if fam == 0:                                       # dense Gaussian, shifted to be stable
        M = rng.standard_normal((m, m)) / np.sqrt(m)
        A = M - (np.linalg.eigvals(M).real.max() + rng.uniform(0.05, 1.0)) * np.eye(m)
    elif fam == 1:                                     # non-normal: permuted triangular
        M = np.triu(rng.standard_normal((m, m)) * rng.uniform(0.3, 1.0), 1) - np.diag(rng.uniform(0.2, 2.0, m))
        pm = rng.permutation(m); A = M[np.ix_(pm, pm)]
    elif fam == 2:                                     # aquifer-like: random tridiagonal + long-range links
        d = rng.uniform(0.5, 2, m - 1); adv = rng.uniform(-0.6, 0.6, m - 1) * d
        A = np.diag(-2 * np.r_[d, d[-1]] - rng.uniform(0.05, 0.4, m))
        A[np.arange(1, m), np.arange(m - 1)] = d + adv
        A[np.arange(m - 1), np.arange(1, m)] = d - adv
        for _ in range(int(rng.integers(0, 4))):
            i, j = rng.choice(m, 2, replace=False); A[i, j] += rng.uniform(-0.8, 0.8)
        lam = np.linalg.eigvals(A).real.max()
        if lam > -0.05:
            A -= (lam + rng.uniform(0.05, 0.5)) * np.eye(m)
    else:                                              # sparse random graph
        M = rng.standard_normal((m, m)) * (rng.random((m, m)) < 0.2)
        A = M - (np.linalg.eigvals(M).real.max() + rng.uniform(0.05, 1.0)) * np.eye(m)
    if rng.random() < 0.5:
        L = rng.standard_normal((m, m + 3)); Q = L @ L.T / (m + 3)
    else:
        Q = np.diag(rng.uniform(0.2, 1.0, m))
    return A, Q, fam


def rel(a, b):
    return np.linalg.norm(a - b) / max(np.linalg.norm(b), 1e-300)


def sec_theorem(nsys=1000, seed=11, cond_max=1e8):
    rng = np.random.default_rng(seed)
    keys = ['lyap', 'kron', 'vanloan', 'partial', 'integral', 'antider', 'exact', 'direct', 'defect']
    err = {k: [] for k in keys}
    info = dict(n=[], fam=[], condSS=[], condC0=[], kS=[], krylov=[], Bnorm=[], ASH=[])
    rejected = 0
    while len(info['n']) < nsys:
        A, Q, fam = random_system(rng)
        m = A.shape[0]
        C0 = solve_continuous_lyapunov(A, -Q)          # scipy solves A X + X A^H = q with q = -Q
        if np.linalg.cond(C0) > cond_max:              # keep numerically meaningful systems only
            rejected += 1
            continue
        err['lyap'].append(np.linalg.norm(A @ C0 + C0 @ A.T + Q) / np.linalg.norm(Q))
        K = np.kron(np.eye(m), A) + np.kron(A, np.eye(m))   # vec(A C + C A^T), column stacking
        Ck = np.linalg.solve(K, -Q.flatten('F')).reshape((m, m), order='F')
        err['kron'].append(rel(C0, Ck))
        lam = np.linalg.eigvals(A).real.max()
        tvl = rng.uniform(0.2, 2.0) / np.linalg.norm(A, 2)   # Van Loan needs e^{-A tau}: keep ||A|| tau moderate
        Phi, Sig = van_loan_noise(A, Q, tvl)            # noise covariance of x(t+tau) | x(t), without C0
        Ev = expm(A * tvl)
        err['vanloan'].append(max(rel(Phi, Ev), rel(Sig, C0 - Ev @ C0 @ Ev.T)))
        tau = rng.uniform(0.05, 2.0) / abs(lam)
        E = expm(A * tau)
        k = int(rng.integers(1, m)); S = sorted(rng.choice(m, k, replace=False)); H = [i for i in range(m) if i not in S]
        Css, Chs = C0[np.ix_(S, S)], C0[np.ix_(H, S)]
        Ct = E @ C0
        Rs = Ct[np.ix_(S, S)] @ np.linalg.inv(Css)
        Bs = E[np.ix_(S, H)] @ Chs @ np.linalg.inv(Css)
        err['partial'].append(rel(Rs, E[np.ix_(S, S)] + Bs))
        Ai = np.linalg.inv(A)
        Iint = (-Ai @ C0)[np.ix_(S, S)] @ np.linalg.inv(Css)
        err['integral'].append(rel(Iint, (-Ai)[np.ix_(S, S)] + (-Ai)[np.ix_(S, H)] @ Chs @ np.linalg.inv(Css)))
        Tb = 3.0 / abs(lam)
        err['antider'].append(rel(van_loan_integral(A, Tb), np.linalg.solve(A, expm(A * Tb) - np.eye(m))))
        err['exact'].append(rel(Ct @ np.linalg.inv(C0), E))
        if k >= 2:
            gi, pi = rng.choice(k, 2, replace=False)
        else:
            gi = pi = 0
        direct = Iint[gi, pi] - (-Ai)[S[gi], S[pi]]
        form = ((-Ai)[np.ix_(S, H)] @ Chs @ np.linalg.inv(Css))[gi, pi]
        err['direct'].append(abs(direct - form) / np.abs(Iint).max())
        t1, t2 = rng.uniform(0.05, 1.5, 2) / abs(lam)
        E1, E2 = expm(A * t1), expm(A * t2)
        Rf = lambda EE: (EE @ C0)[np.ix_(S, S)] @ np.linalg.inv(Css)
        D = Rf(E1 @ E2) - Rf(E1) @ Rf(E2)
        Pi = Chs @ np.linalg.inv(Css)
        C2 = E2 @ C0
        Dform = E1[np.ix_(S, H)] @ (C2[np.ix_(H, S)] - Pi @ C2[np.ix_(S, S)]) @ np.linalg.inv(Css)
        err['defect'].append(np.linalg.norm(D - Dform) / max(np.linalg.norm(Rf(E1 @ E2)), 1e-300))
        # Krylov form of the necessary and sufficient condition: E_S A^j [0; C_HS] for j = 1..m-1
        Z = np.zeros((m, k)); Z[H] = Chs
        kr, V = 0.0, Z.copy(); nA = np.linalg.norm(A, 2)
        for j in range(1, m):
            V = A @ V / nA; kr = max(kr, np.linalg.norm(V[S]) / np.linalg.norm(C0))
        info['n'].append(m); info['fam'].append(fam); info['condSS'].append(np.linalg.cond(Css)); info['kS'].append(k)
        info['krylov'].append(kr); info['Bnorm'].append(np.linalg.norm(Bs)); info['condC0'].append(np.linalg.cond(C0))
        info['ASH'].append(np.abs(A[np.ix_(S, H)]).max())
    out = {}
    for kk, v in err.items():
        v = np.array(v)
        out[kk] = dict(log10=np.log10(np.maximum(v, 1e-18)), max=v.max(), q99=np.quantile(v, 0.99),
                       median=np.median(v), frac_below_1e10=np.mean(v < 1e-10))
    out['info'] = {kk: np.array(v) for kk, v in info.items()}
    out['nsys'] = nsys; out['rejected_cond'] = rejected; out['cond_max'] = cond_max
    ash, bn, kr = np.array(info['ASH']), np.array(info['Bnorm']), np.array(info['krylov'])
    out['B_vs_ASH'] = dict(n_ASH_nonzero=int((ash > 0).sum()), frac_B_nonzero_given_ASH_nonzero=float(np.mean(bn[ash > 0] > 1e-8)),
                           n_ASH_zero=int((ash == 0).sum()), max_B_given_ASH_zero=float(bn[ash == 0].max()) if (ash == 0).any() else None,
                           min_krylov_given_ASH_nonzero=float(kr[ash > 0].min()))
    out['mc_ordering'] = mc_ordering_check()
    out['taylor'] = taylor_check(rng)
    out['counterexamples'] = counterexamples()
    out['symbolic'] = symbolic_checks()
    return out


def mc_ordering_check(seed=5):
    """Euler-Maruyama (independent of every closed form) for a non-normal 3-node system: which of
    e^{A tau} C0, C0 e^{A' tau} matches E[x(t+tau) x(t)'] ?  Also the stationary covariance."""
    rng = np.random.default_rng(seed)
    A = np.array([[-1.0, 2.5, 0.0], [0.0, -0.7, 1.5], [-0.4, 0.0, -1.3]])     # stable, strongly non-normal
    Q = np.diag([0.5, 1.0, 0.3])
    C0 = solve_continuous_lyapunov(A, -Q)
    dt, Rp, burn, tau = 0.002, 20000, 10.0, 0.8
    sq = np.linalg.cholesky(Q * dt)
    x = np.zeros((Rp, 3))
    for _ in range(int(burn / dt)):
        x = x + x @ A.T * dt + rng.standard_normal((Rp, 3)) @ sq.T
    x0 = x.copy()
    for _ in range(int(round(tau / dt))):
        x = x + x @ A.T * dt + rng.standard_normal((Rp, 3)) @ sq.T
    emp_c0 = x0.T @ x0 / Rp
    emp = x.T @ x0 / Rp                                  # E[x(t+tau) x(t)']
    Y = np.einsum('ri,rj->rij', x, x0)
    se = Y.std(0) / np.sqrt(Rp)
    se0 = np.einsum('ri,rj->rij', x0, x0).std(0) / np.sqrt(Rp)
    E = expm(A * tau)
    cand = dict(eAC=E @ C0, CeAT=C0 @ E.T, eATC=expm(A.T * tau) @ C0)
    z = {kk: float(np.max(np.abs(emp - v) / se)) for kk, v in cand.items()}
    return dict(max_abs_z=z, max_abs_z_C0=float(np.max(np.abs(emp_c0 - C0) / se0)),
                C0_wrong_sign_rel=rel(solve_continuous_lyapunov(A, Q), C0), dt=dt, paths=Rp, tau=tau)


def taylor_check(rng):
    """B_S(eps) ~ eps A_SH Pi and D(eps, eps) ~ eps^2 A_SH Riccati(Pi): error ratio when eps halves."""
    A, Q, _ = random_system(rng)
    while A.shape[0] < 6:
        A, Q, _ = random_system(rng)
    m = A.shape[0]; C0 = solve_continuous_lyapunov(A, -Q)
    S = list(range(m // 2)); H = list(range(m // 2, m))
    Pi = C0[np.ix_(H, S)] @ np.linalg.inv(C0[np.ix_(S, S)])
    Ric = A[np.ix_(H, S)] + A[np.ix_(H, H)] @ Pi - Pi @ A[np.ix_(S, S)] - Pi @ A[np.ix_(S, H)] @ Pi
    lead_B, lead_D = A[np.ix_(S, H)] @ Pi, A[np.ix_(S, H)] @ Ric
    res = []
    for eps in [1e-2, 5e-3, 2.5e-3]:
        e = eps / np.linalg.norm(A, 2)
        E = expm(A * e); Css = C0[np.ix_(S, S)]
        B = E[np.ix_(S, H)] @ C0[np.ix_(H, S)] @ np.linalg.inv(Css)
        Rf = lambda EE: (EE @ C0)[np.ix_(S, S)] @ np.linalg.inv(Css)
        D = Rf(E @ E) - Rf(E) @ Rf(E)
        res.append(dict(eps=e, errB=rel(B / e, lead_B), errD=rel(D / e ** 2, lead_D)))
    return res


def counterexamples():
    out = {}
    taus = np.linspace(0.0, 10.0, 201)

    def Bmax(A, C0, S, H):
        Css = C0[np.ix_(S, S)]
        return max(np.linalg.norm(expm(A * t)[np.ix_(S, H)] @ C0[np.ix_(H, S)] @ np.linalg.inv(Css)) for t in taus)

    def Dmax(A, C0, S):
        Css = C0[np.ix_(S, S)]
        Rf = lambda t: (expm(A * t) @ C0)[np.ix_(S, S)] @ np.linalg.inv(Css)
        return max(np.linalg.norm(Rf(2 * t) - Rf(t) @ Rf(t)) for t in taus[1:60])

    def intbias(A, C0, S, H):
        Ai = np.linalg.inv(A)
        return (-Ai)[np.ix_(S, H)] @ C0[np.ix_(H, S)] @ np.linalg.inv(C0[np.ix_(S, S)])

    # (i) A_SH = 0 but hidden children strongly correlated with S  ->  B == 0
    A = np.array([[-1.0, 0.3, 0.0, 0.0], [0.2, -1.5, 0.0, 0.0], [1.2, 0.0, -0.8, 0.4], [0.0, 0.9, 0.0, -1.1]])
    Q = np.eye(4); C0 = solve_continuous_lyapunov(A, -Q); S, H = [0, 1], [2, 3]
    corr = C0[np.ix_(H, S)] / np.sqrt(np.outer(np.diag(C0)[H], np.diag(C0)[S]))
    out['i_ASH_zero'] = dict(A=A, max_abs_corr_HS=np.abs(corr).max(), maxB=Bmax(A, C0, S, H), maxD=Dmax(A, C0, S))
    # (ii) both hidden nodes are parents of s and correlated with s, yet B == 0 (cancellation):
    #      (s, w) rotation pair (C_ws = 0), z driven by s but invisible to s; h1,2 = (w +/- z)/sqrt2
    beta = 1.3
    Ap = np.array([[-1.0, 1.0, 0.0], [-1.0, -1.0, 0.0], [beta, 0.0, -3.0]])
    U = np.eye(3); U[1:, 1:] = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    A = U @ Ap @ U.T; Q = np.eye(3); C0 = solve_continuous_lyapunov(A, -Q); S, H = [0], [1, 2]
    out['ii_cancellation'] = dict(A=A, A_SH=A[np.ix_(S, H)], C_HS=C0[np.ix_(H, S)], maxB=Bmax(A, C0, S, H),
                                  intB=intbias(A, C0, S, H), maxD=Dmax(A, C0, S))
    # (iii) the only hidden parent h1 is uncorrelated with s, but the hidden grandparent h2 is: B != 0
    gam = 1.5

    def mk(kap):
        A = np.array([[-1.0, 1.0, 0.0], [-kap, -1.0, gam], [0.0, 0.0, -0.7]])
        return A, solve_continuous_lyapunov(A, -np.eye(3))
    ks = np.linspace(0.05, 30, 600); vals = [mk(k)[1][1, 0] for k in ks]
    idx = [i for i in range(len(ks) - 1) if np.sign(vals[i]) != np.sign(vals[i + 1])]
    if idx:
        kap = brentq(lambda k: mk(k)[1][1, 0], ks[idx[0]], ks[idx[0] + 1], xtol=1e-14)
        A, C0 = mk(kap); S, H = [0], [1, 2]
        out['iii_uncorrelated_parent'] = dict(kappa=kap, A=A, C_h1s=C0[1, 0], C_h2s=C0[2, 0],
                                              maxB=Bmax(A, C0, S, H), intB=intbias(A, C0, S, H),
                                              R_true=(-np.linalg.inv(A))[0, 0])
    else:
        out['iii_uncorrelated_parent'] = 'no sign change found'
    # (iv) Markov-looking observations (D == 0) but biased FDT: span[I; Pi] A-invariant, correlated noise
    #      coordinates y = (u, v), u = x_S, v = x_H - Pi0 x_S; v autonomous, drives u; Cov(v, u) = 0
    Mu = np.array([[-1.0, 0.4], [0.0, -0.8]]); Kc = np.array([[0.9], [0.5]]); Nv = np.array([[-0.6]])
    Pi0 = np.array([[0.7, -0.4]])
    Cvv = np.array([[1.0]]); Quu = np.eye(2) * 4.0
    Qvv = -(Nv @ Cvv + Cvv @ Nv.T); Qvu = -(Cvv @ Kc.T)
    Ay = np.block([[Mu, Kc], [np.zeros((1, 2)), Nv]])
    Qy = np.block([[Quu, Qvu.T], [Qvu, Qvv]])
    Tm = np.block([[np.eye(2), np.zeros((2, 1))], [Pi0, np.eye(1)]])        # x = Tm y
    A = Tm @ Ay @ np.linalg.inv(Tm); Q = Tm @ Qy @ Tm.T
    C0 = solve_continuous_lyapunov(A, -Q); S, H = [0, 1], [2]
    Ai = np.linalg.inv(A)
    out['iv_markov_but_biased'] = dict(minEigQ=np.linalg.eigvalsh(Q).min(), Pi=C0[np.ix_(H, S)] @ np.linalg.inv(C0[np.ix_(S, S)]),
                                       maxD=Dmax(A, C0, S), maxB=Bmax(A, C0, S, H), intB=intbias(A, C0, S, H),
                                       true_int=(-Ai)[np.ix_(S, S)])
    return out


def symbolic_checks():
    try:
        import sympy as sp
    except Exception as e:                              # pragma: no cover
        return dict(status='skipped (sympy not importable: %s)' % e)
    res = {}
    # (a) block identity of the theorem (generic E = e^{A tau}, generic symmetric C), |S| = 2, |H| = 2
    E = sp.Matrix(4, 4, lambda i, j: sp.Symbol(f'e{i}{j}'))
    C = sp.Matrix(4, 4, lambda i, j: sp.Symbol(f'c{min(i, j)}{max(i, j)}'))
    S, H = [0, 1], [2, 3]
    sub = lambda M, r, c: M.extract(r, c)
    Css_inv = sub(C, S, S).inv()
    lhs = sub(E * C, S, S) * Css_inv
    rhs = sub(E, S, S) + sub(E, S, H) * sub(C, H, S) * Css_inv
    res['block_identity'] = bool(sp.simplify(lhs - rhs) == sp.zeros(2, 2))
    # (b) semigroup defect identity with generic E1, E2 (C(t2) = E2 C, C(t1+t2) = E1 E2 C)
    E1 = sp.Matrix(3, 3, lambda i, j: sp.Symbol(f'a{i}{j}')); E2 = sp.Matrix(3, 3, lambda i, j: sp.Symbol(f'b{i}{j}'))
    C3 = sp.Matrix(3, 3, lambda i, j: sp.Symbol(f'c{min(i, j)}{max(i, j)}'))
    S, H = [0, 1], [2]
    Ci = sub(C3, S, S).inv()
    Rf = lambda M: sub(M * C3, S, S) * Ci
    Dl = Rf(E1 * E2) - Rf(E1) * Rf(E2)
    Pi = sub(C3, H, S) * Ci
    C2 = E2 * C3
    Dr = sub(E1, S, H) * (sub(C2, H, S) - Pi * sub(C2, S, S)) * Ci
    res['defect_identity'] = bool(sp.simplify(Dl - Dr) == sp.zeros(2, 2))
    # (c) Lyapunov sign: d/dt E[x x'] = A C + C A' + Q for dx = A x dt + dW, 2x2, by Ito on a generic symbolic path
    a = sp.Matrix(2, 2, sp.symbols('A0:4')); q11, q12, q22 = sp.symbols('q11 q12 q22')
    Qs = sp.Matrix([[q11, q12], [q12, q22]])
    c11, c12, c22 = sp.symbols('c11 c12 c22'); Cs = sp.Matrix([[c11, c12], [c12, c22]])
    sol = sp.solve(list(a * Cs + Cs * a.T + Qs), [c11, c12, c22], dict=True)[0]
    # scalar sanity: A = -k gives C = q/(2k) > 0 (correct sign)
    kk, qq = sp.symbols('k q', positive=True)
    res['lyap_scalar'] = str(sp.solve(sp.Eq(-kk * sp.Symbol('c') * 2 + qq, 0), sp.Symbol('c'))[0])
    res['lyap_2x2_solved'] = len(sol) == 3
    # (d) parametric response: d/dQ [-(A + Q A1)^{-1}(F + Q b)] at Q = 0 equals -A^{-1}(A1 xbar + b)
    Qp = sp.Symbol('Q')
    A2 = sp.Matrix(2, 2, sp.symbols('m0:4')); A1 = sp.Matrix(2, 2, sp.symbols('n0:4'))
    F2 = sp.Matrix(sp.symbols('f0:2')); b2 = sp.Matrix(sp.symbols('b0:2'))
    xq = -(A2 + Qp * A1).inv() * (F2 + Qp * b2)
    d = sp.diff(xq, Qp).subs(Qp, 0)
    xbar = -A2.inv() * F2
    res['parametric_response'] = bool(sp.simplify(d - (-A2.inv() * (A1 * xbar + b2))) == sp.zeros(2, 1))
    # (e) integral of e^{lambda t}: -1/lambda for Re lambda < 0
    t = sp.Symbol('t', positive=True); lam = sp.Symbol('lambda', negative=True)
    res['int_exp'] = str(sp.integrate(sp.exp(lam * t), (t, 0, sp.oo)))
    res['status'] = 'ok (sympy %s)' % sp.__version__
    return res


# ----------------------------------------------------------------------------------------- 2. numbers
def sec_numbers(do_l96=True):
    out = {}
    A, C0, Q = truth(); T = Model(A, C0, Q)
    out['truth'] = dict(R=T.R, naive=C0[G, P] / C0[P, P], fdt_pg=T.fdt([P, G]), fdt_full=T.fdt(range(n)))
    H = [i for i in range(n) if i not in (P, G)]
    S = [P, G]
    Bform = ((-T.Ai)[np.ix_(S, H)] @ C0[np.ix_(H, S)] @ np.linalg.inv(C0[np.ix_(S, S)]))[1, 0]
    out['truth']['bias_formula'] = Bform
    out['truth']['bias_direct'] = T.fdt(S) - T.R
    # oracle greedy exactly as causal_ou.py (same RNG stream for the random baseline)
    rng = np.random.default_rng(2); rng.random(n)
    orc = {}
    for k in [1, 2, 3, 4, 6]:
        S = [P, G]
        for _ in range(k):
            S.append(min((i for i in OTHERS if i not in S), key=lambda i: abs(T.fdt(S + [i]) - T.R)))
        rnd = [abs(T.fdt([P, G] + list(rng.choice(OTHERS, k, replace=False))) - T.R) for _ in range(300)]
        orc[k] = dict(S=sorted(S), order=S, err=abs(T.fdt(S) - T.R), rnd_median=np.median(rnd),
                      near=abs(T.fdt([P, G] + NEAR[:k]) - T.R))
    out['oracle'] = orc
    oseq = greedy([T], 8, lambda S: abs(T.fdt(S) - T.R))
    out['oracle_seq_err'] = [abs(T.fdt(S) - T.R) for S in oseq]
    out['oracle_seq'] = oseq
    # prior greedy (design ensemble of 60) and its error on the true model (causal_prior.py)
    ens = [Model(*m) for m in design_ensemble()]
    ebias = lambda S: np.mean((fdt_many(ens, S) - np.array([m.R for m in ens])) ** 2)
    pseq = greedy(ens, 8, ebias)
    out['prior_seq'] = pseq
    out['prior_seq_on_truth'] = [dict(S=sorted(S), est=T.fdt(S), err=abs(T.fdt(S) - T.R),
                                      rel=abs(T.fdt(S) - T.R) / T.R, prior_rmse=np.sqrt(ebias(S))) for S in pseq]
    out['near_on_truth'] = [abs(T.fdt([P, G] + NEAR[:k]) - T.R) for k in range(9)]
    # honest table on 200 independent test models (causal_prior2.py) and extensions
    tst = [Model(*m) for m in test_models()]
    Rt = np.array([m.R for m in tst])
    relerr = lambda S: np.abs(fdt_many(tst, S) - Rt) / np.abs(Rt)
    naive = np.abs(np.array([m.C0[G, P] / m.C0[P, P] for m in tst]) - Rt) / np.abs(Rt)
    rr = np.random.default_rng(3); orig_rnd = {}
    for k in range(1, 7):                              # identical RNG use to causal_prior2.py
        orig_rnd[k] = np.median([np.median(np.abs(fdt_many(tst[:40], [P, G] + list(rr.choice(OTHERS, k, replace=False)))
                                                  - Rt[:40]) / np.abs(Rt[:40])) for _ in range(20)])
    rb = np.random.default_rng(4); bt = np.random.default_rng(9)
    boot_idx = bt.integers(0, len(tst), (2000, len(tst)))

    def summ(e):
        e = np.asarray(e)
        if e.ndim == 1:
            meds = np.median(e[boot_idx], axis=1)
        else:                                          # (draws, models): resample models
            meds = np.array([np.median(e[:, bi]) for bi in boot_idx[:400]])
        return dict(median=np.median(e), q10=np.quantile(e, 0.1), q90=np.quantile(e, 0.9), se_median=meds.std())
    tab = dict(kauz=[], near=[], rand=[], rand_med_of_med=[], kauz_beats_naive=[], k=list(range(9)))
    for k in range(9):
        ek, en = relerr(pseq[k]), relerr([P, G] + NEAR[:k])
        tab['kauz'].append(summ(ek)); tab['near'].append(summ(en))
        if k == 0:
            er = ek[None, :]
        else:
            er = np.array([relerr([P, G] + list(rb.choice(OTHERS, k, replace=False))) for _ in range(200)])
        tab['rand'].append(summ(er)); tab['rand_med_of_med'].append(np.median(np.median(er, axis=1)))
        tab['kauz_beats_naive'].append(np.mean(ek < naive))
    tab['naive'] = summ(naive)
    tab['orig_random_40models'] = orig_rnd
    out['table'] = tab
    out['design_sets'] = dict(kauz=pseq, near=[[P, G] + NEAR[:k] for k in range(9)])
    if do_l96:
        out['l96'] = l96_extra()
    return out


# Lorenz-96 helpers copied from causal_l96.py (identical integrator and settings)
N96, F96, DT96 = 20, 8.0, 0.01


def l96_rhs(x, Fv):
    return (np.roll(x, -1, 1) - np.roll(x, 2, 1)) * np.roll(x, 1, 1) - x + Fv


def l96_run(Fv, ntraj=100, T=1000.0, seed=0, sample_every=5):
    r = np.random.default_rng(seed); x = F96 + r.standard_normal((ntraj, N96)); dt = DT96
    for _ in range(int(20 / dt)):
        k1 = l96_rhs(x, Fv); k2 = l96_rhs(x + .5 * dt * k1, Fv); k3 = l96_rhs(x + .5 * dt * k2, Fv); k4 = l96_rhs(x + dt * k3, Fv)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    out = []
    for t in range(int(T / dt)):
        k1 = l96_rhs(x, Fv); k2 = l96_rhs(x + .5 * dt * k1, Fv); k3 = l96_rhs(x + .5 * dt * k2, Fv); k4 = l96_rhs(x + dt * k3, Fv)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if t % sample_every == 0:
            out.append(x.copy())
    return np.array(out)


def l96_fdt_tables(X, maxlags):
    X = X - X.mean((0, 1)); T_, M_, _ = X.shape; dts = 0.05
    Lmax = max(maxlags); C = []
    for lag in range(Lmax):
        a = X[lag:].reshape(-1, N96); b = X[:T_ - lag].reshape(-1, N96)
        C.append(a.T @ b / ((T_ - lag) * M_))
    C = np.array(C); res = {}
    for L in maxlags:
        Cint = C[:L].sum(0) * dts - 0.5 * dts * C[0]
        res[L] = (Cint, C[0])
    return res


def l96_extra():
    """Robustness of the Test-2 numbers: FDT from the original data (seed 3) and an independent data
    set (seed 4); truncation at 4 vs 8 time units; the in-sample greedy set evaluated out of sample."""
    p, g = 0, 3; others = [i for i in range(N96) if i not in (p, g)]
    t0 = time.time(); res = {}
    tabs = {}
    for seed in (3, 4):
        X = l96_run(np.full(N96, F96), ntraj=50, T=400.0, seed=seed)
        tabs[seed] = l96_fdt_tables(X, [80, 160])
        del X

    def fdt(tab, S):
        Cint, C0 = tab; S = list(S)
        return (Cint[np.ix_(S, S)] @ np.linalg.inv(C0[np.ix_(S, S)]))[S.index(g), S.index(p)]
    for seed in (3, 4):
        for L in (80, 160):
            tb = tabs[seed][L]
            res[f'seed{seed}_tau{L * 0.05:.0f}'] = dict(full=fdt(tb, range(N96)), pg=fdt(tb, [p, g]),
                                                         naive=tb[1][g, p] / tb[1][p, p])
    # in-sample greedy on seed 3 (as in causal_l96.py), evaluated on seed 4
    tb3, tb4 = tabs[3][80], tabs[4][80]
    ref3, ref4 = fdt(tb3, range(N96)), fdt(tb4, range(N96))
    S = [p, g]; seqs = {}
    for k in range(1, 7):
        S = S + [min((i for i in others if i not in S), key=lambda i: abs(fdt(tb3, S + [i]) - ref3))]
        seqs[k] = list(S)
    rng = np.random.default_rng(0)
    oos = {}
    for k in (2, 4, 6):
        rnd4 = [abs(fdt(tb4, [p, g] + list(rng.choice(others, k, replace=False))) - ref4) for _ in range(200)]
        oos[k] = dict(S=sorted(seqs[k]), in_sample=abs(fdt(tb3, seqs[k]) - ref3), out_of_sample=abs(fdt(tb4, seqs[k]) - ref4),
                      random_median_seed4=np.median(rnd4))
    res['greedy_out_of_sample'] = oos
    res['runtime_s'] = time.time() - t0
    res['note'] = 'direct response R = 0.0658 (seeds 1,2), replicates 0.060/0.062 (seeds 11-22) from the rerun logs'
    return res


# --------------------------------------------------------------------------------------------- 3. chaos
def sec_chaos():
    """dx = (x - x^3 + F) dt + sigma dW (not chaotic, bimodal invariant density).  Exact response of the
    mean: d<x>/dF = (2/sigma^2) Var(x) (exponential family); score-FDT gives the same; quasi-Gaussian FDT
    gives int C(tau) dtau / C(0) = (2/sigma^2) int Phi^2/rho dx / Var(x), Phi(x) = int_{-inf}^x (y-mu) rho."""
    x = np.linspace(-4, 4, 160001); dx = x[1] - x[0]; res = {}
    for sig in (0.5, 0.7, 1.0, 1.5):
        def rho_F(F):
            lr = (2 / sig ** 2) * (x ** 2 / 2 - x ** 4 / 4 + F * x); r = np.exp(lr - lr.max()); return r / (r.sum() * dx)
        r = rho_F(0.0); mu = (x * r).sum() * dx; var = ((x - mu) ** 2 * r).sum() * dx
        h = 1e-4
        fd = (((x * rho_F(h)).sum() - (x * rho_F(-h)).sum()) * dx) / (2 * h)
        left = np.cumsum((x - mu) * r) * dx                       # int_{-inf}^x (y - mu) rho
        right = -np.cumsum(((x - mu) * r)[::-1])[::-1] * dx + (x - mu) * r * dx   # -int_x^inf, same quantity
        Phi = np.where(x < mu, left, right)                        # each from its own tail (no cancellation)
        m = r > 1e-280
        intC = (2 / sig ** 2) * (Phi[m] ** 2 / r[m]).sum() * dx
        res[f'sigma={sig}'] = dict(var=var, exact=(2 / sig ** 2) * var, finite_diff=fd, quasi_gauss=intC / var,
                                   ratio_qg_over_exact=(intC / var) / ((2 / sig ** 2) * var))
    return res


# ------------------------------------------------------------------------------------------- 4. pumping
def pumping_operator(p=P, c_sea=1.0):
    """Upwind advection by the flow that pumping at p induces between two fixed-head boundaries (inland
    cell 0 side fresh, c = 0; coast beyond cell n-1, c = c_sea).  Unit pumping: landward velocity
    u_r = (p + 1/2)/n on the coastal side, seaward u_l = (n - p - 1/2)/n on the inland side."""
    ur = (p + 0.5) / n; ul = (n - p - 0.5) / n
    A1 = np.zeros((n, n)); b = np.zeros(n)
    for i in range(n):
        if i > p:
            A1[i, i] -= ur
            if i < n - 1:
                A1[i, i + 1] += ur
            else:
                b[i] += ur * c_sea
        elif i < p:
            A1[i, i] -= ul
            if i > 0:
                A1[i, i - 1] += ul
        else:
            A1[i, i] -= ul + ur; A1[i, i - 1] += ul; A1[i, i + 1] += ur
    return A1, b


def sec_pumping(seed=21, reps=40, T=400.0, dt=0.1, tau_max=20.0):
    A, C0, Q = truth()
    Fsea = np.zeros(n); Fsea[n - 1] = (1.0 - 0.35) * 1.0           # sea boundary through the missing neighbour
    Ai = np.linalg.inv(A)
    xbar = -Ai @ Fsea
    A1, b = pumping_operator()
    f = A1 @ xbar + b                                               # effective forcing
    true = -Ai @ f
    xq = lambda q: -np.linalg.solve(A + q * A1, Fsea + q * b)
    h = 1e-5; fd = (xq(h) - xq(-h)) / (2 * h)
    add_p = -Ai[:, P]                                               # FDT with additive unit forcing at p
    res = dict(xbar=xbar, f=f, true=true, fd=fd, fd_err=np.abs(fd - true).max(), additive_p=add_p,
               b_only=-Ai @ b, A1x_only=-Ai @ (A1 @ xbar),
               cos_additive_true=float(add_p @ true / np.linalg.norm(add_p) / np.linalg.norm(true)),
               frac_f_mass_coast=float(np.abs(f[20:]).sum() / np.abs(f).sum()))
    # finite-record estimate (full state): R_hat = Cint_hat C0_hat^{-1}, f_hat = A1 xbar_hat + b
    rng = np.random.default_rng(seed); N = int(T / dt); L = int(tau_max / dt)
    st = ou_stats(A, C0, dt, N, reps, rng, L, lags=(), mean=xbar, keep_mean=True)
    est = []
    for r in range(reps):
        Rh = st['Cint'][r] @ np.linalg.inv(st['C0'][r])
        fh = A1 @ st['mean'][r] + b
        est.append(Rh @ fh)
    est = np.array(est)
    res['est_q10'], res['est_q50'], res['est_q90'] = np.quantile(est, [0.1, 0.5, 0.9], axis=0)
    res['est_g_mean'], res['est_g_sd'] = est[:, G].mean(), est[:, G].std()
    add_est = np.array([(st['Cint'][r] @ np.linalg.inv(st['C0'][r]))[:, P] for r in range(reps)])
    res['est_additive_g_mean'] = add_est[:, G].mean()
    res['settings'] = dict(T=T, dt=dt, tau_max=tau_max, reps=reps, c_sea=1.0, F_sea=Fsea[n - 1])
    # partial observation: R_S f_S for the KAUZ sets of the additive criterion (forcing on H is lost)
    T_ = Model(A, C0, Q)
    ens = [Model(*m) for m in design_ensemble()]
    ebias = lambda S: np.mean((fdt_many(ens, S) - np.array([m.R for m in ens])) ** 2)
    pseq = greedy(ens, 8, ebias)
    part = []
    for S in pseq:
        S2 = sorted(S); Rs = T_.Cint[np.ix_(S2, S2)] @ np.linalg.inv(C0[np.ix_(S2, S2)])
        part.append(dict(S=S2, est_g=(Rs @ f[S2])[S2.index(G)], f_mass_in_S=np.abs(f[S2]).sum() / np.abs(f).sum()))
    res['partial_kauz'] = part
    # a set targeted at the effective forcing: g plus the cells carrying 99% of |f|, then oracle greedy
    order = np.argsort(-np.abs(f)); cum = np.cumsum(np.abs(f[order])) / np.abs(f).sum()
    core = sorted(set([G] + list(order[:np.searchsorted(cum, 0.99) + 1])))
    Rs = T_.Cint[np.ix_(core, core)] @ np.linalg.inv(C0[np.ix_(core, core)])
    res['targeted'] = dict(S=core, est_g=(Rs @ f[core])[core.index(G)], est_S=(Rs @ f[core]), true_S=true[core])
    # finite records observed only on the targeted set: R_S_hat f_S_hat with f_S_hat = (A1 xbar_hat + b)_S
    # (rows of A1 for these coastal cells only involve the same cells, so f_S needs only the observed means)
    assert np.all(np.abs(A1[np.ix_(core, [j for j in range(n) if j not in core])]) == 0)
    A1s = A1[np.ix_(core, core)]
    res['targeted_records'] = {}
    for Tl, reps in ((T, 200), (10 * T, 100)):
        stt = ou_stats(A, C0, dt, int(Tl / dt), reps, rng, L, lags=(), cells=core, mean=xbar, keep_mean=True)
        Rh = [stt['Cint'][r] @ np.linalg.inv(stt['C0'][r]) for r in range(reps)]
        ests = np.array([Rh[r] @ (A1s @ stt['mean'][r] + b[core]) for r in range(reps)])
        ests_fk = np.array([Rh[r] @ f[core] for r in range(reps)])          # effective forcing known exactly
        ig = core.index(G)
        res['targeted_records'][f'T={Tl:g}'] = dict(reps=reps, q10=np.quantile(ests, 0.1, axis=0), q50=np.median(ests, axis=0),
                                                    q90=np.quantile(ests, 0.9, axis=0), mean_g=ests[:, ig].mean(), sd_g=ests[:, ig].std(),
                                                    mean_g_fknown=ests_fk[:, ig].mean(), sd_g_fknown=ests_fk[:, ig].std(), cells=core)
    return res


# -------------------------------------------------------------------------------- simulation engine (exact)
def ou_stats(A, C0, dt, N, R, rng, L, lags=(), cells=None, mean=None, keep_mean=False, center=True, max_elems=6e6):
    """R independent stationary records x_0..x_{N-1} of dx = A x dt + dW sampled at spacing dt with the
    exact transition x_{k+1} = e^{A dt} x_k + eps_k, eps_k ~ N(0, C0 - Phi C0 Phi').  Returns per record
    C0_hat, the trapezoid integral dt * sum_{l=0}^{L} w_l C_hat(l dt) (forward sums, N-L pairs) and the
    lagged covariances C_hat(l) for l in lags.  Records are centred with their own sample mean."""
    m = A.shape[0]
    Phi = expm(A * dt); Sig = C0 - Phi @ C0 @ Phi.T; Sig = (Sig + Sig.T) / 2
    Ls = cholesky(Sig + 1e-15 * np.eye(m), lower=True); L0 = cholesky(C0, lower=True)
    cells = list(range(m)) if cells is None else list(cells); k = len(cells)
    chunk = max(1, int(max_elems // (N * m)))
    out = dict(C0=np.empty((R, k, k)), Cint=np.empty((R, k, k)), lag={l: np.empty((R, k, k)) for l in lags})
    if keep_mean:
        out['mean'] = np.empty((R, k))
    for r0 in range(0, R, chunk):
        r = min(chunk, R - r0)
        X = np.empty((r, N, m))
        x = rng.standard_normal((r, m)) @ L0.T
        Z = rng.standard_normal((r, N, m)) @ Ls.T
        for t in range(N):
            X[:, t] = x
            x = x @ Phi.T + Z[:, t]
        del Z
        X = X[:, :, cells] if k < m else X
        if mean is not None:
            X = X + np.asarray(mean)[cells]
        if keep_mean:
            out['mean'][r0:r0 + r] = X.mean(1)
        if center:
            X = X - X.mean(1, keepdims=True)
        st = series_stats(X, dt, L, lags)
        out['C0'][r0:r0 + r] = st['C0']; out['Cint'][r0:r0 + r] = st['Cint']
        for l in lags:
            out['lag'][l][r0:r0 + r] = st['lag'][l]
        del X
    return out


def series_stats(X, dt, L, lags=()):
    """X (..., N, k) centred series -> C0_hat, trapezoid integral of C_hat up to lag L, C_hat(l)."""
    N = X.shape[-2]
    Xt = np.swapaxes(X, -1, -2)
    C0h = Xt @ X / N
    cs = np.concatenate([np.zeros(X.shape[:-2] + (1, X.shape[-1])), np.cumsum(X, axis=-2)], axis=-2)
    z = (cs[..., L + 1:N + 1, :] - cs[..., 0:N - L, :]) - 0.5 * X[..., :N - L, :] - 0.5 * X[..., L:N, :]
    Cint = dt * (np.swapaxes(z, -1, -2) @ X[..., :N - L, :]) / (N - L)
    lag = {l: (np.swapaxes(X[..., l:, :], -1, -2) @ X[..., :N - l, :]) / (N - l) for l in lags}
    return dict(C0=C0h, Cint=Cint, lag=lag)


def pop_disc(A, C0, dt, L):
    """Population version of the discretised estimator: dt * sum_{l=0}^{L} w_l C(l dt)."""
    Phi = expm(A * dt); I = np.eye(A.shape[0])
    geo = np.linalg.solve(I - Phi, I - np.linalg.matrix_power(Phi, L + 1))
    return dt * (geo - 0.5 * (I + np.linalg.matrix_power(Phi, L))) @ C0


def theta_from_stats(C0h, Cint, S, cellidx=None):
    """Integrated partial-FDT estimate of R_gp for every record; S in model indices."""
    S = list(S); idx = S if cellidx is None else [cellidx[s] for s in S]
    Css = C0h[:, idx][:, :, idx]
    rhs = np.zeros((C0h.shape[0], len(S), 1)); rhs[:, S.index(P), 0] = 1
    x = np.linalg.solve(Css, rhs)[:, :, 0]
    gi = idx[S.index(G)]
    return np.einsum('rs,rs->r', Cint[:, gi][:, idx], x)


# ----------------------------------------------------------------------------------------- 5. semigroup
def mroot(Gm, m):
    """Principal m-th root of (a stack of) matrices via the eigendecomposition (real part)."""
    if m == 1:
        return Gm
    w, V = np.linalg.eig(Gm)
    return ((V * (w.astype(complex) ** (1.0 / m))[..., None, :]) @ np.linalg.inv(V)).real


def ar1_quantities(Cs0, Csm, Csint, ig, ip, dt, m=1):
    """Target-specific integrated defect Delta_gp(tau0) = [J_FDT - J_LIM(tau0)]_gp, tau0 = m dt.
    J_LIM is the trapezoid integral, on the same dt grid, of the Markov (LIM) extrapolation
    exp(L tau) with L = log(G(tau0))/tau0, G(tau0) = C(tau0) C(0)^{-1}:  J_LIM = dt[(I - Phi)^{-1} - I/2],
    Phi = G(tau0)^{1/m}.  For an exactly Markov S-process both agree (up to the truncation term Phi^L)."""
    k = Cs0.shape[-1]; I = np.eye(k)
    Phi = mroot(Csm @ np.linalg.inv(Cs0), m)
    Jar = dt * (np.linalg.inv(I - Phi) - 0.5 * I)
    Jf = Csint @ np.linalg.inv(Cs0)
    return (Jf - Jar)[..., ig, ip], Jf[..., ig, ip], Jar[..., ig, ip]


def sec_semigroup(seed=31, do_power=True):
    out = {}
    ens = [Model(*m) for m in design_ensemble()]
    ebias = lambda S: np.mean((fdt_many(ens, S) - np.array([m.R for m in ens])) ** 2)
    pseq = greedy(ens, 8, ebias)
    tst = [Model(*m) for m in test_models()]
    rng = np.random.default_rng(seed)
    dt = 0.25; d1 = 1.0; m0 = 8                                    # LIM lag tau0 = m0 dt = 2
    rows = []
    for mi, M in enumerate(tst):
        E1 = expm(M.A * d1); C1, C2 = E1 @ M.C0, E1 @ E1 @ M.C0
        Cdt = expm(M.A * dt) @ M.C0; Ct0 = expm(M.A * m0 * dt) @ M.C0
        Jdisc = pop_disc(M.A, M.C0, dt, 4000)                     # tau_max -> infinity
        sets = [('kauz', k, pseq[k]) for k in range(9)] + [('near', k, [P, G] + NEAR[:k]) for k in range(9)]
        sets += [('rand', k, [P, G] + list(rng.choice(OTHERS, k, replace=False))) for k in range(1, 9) for _ in range(3)]
        for kind, k, S in sets:
            S = list(S); ig, ip = S.index(G), S.index(P)
            Css = M.C0[np.ix_(S, S)]; Ci = np.linalg.inv(Css)
            bias = (M.Cint[np.ix_(S, S)] @ Ci)[ig, ip] - M.R
            R1, R2 = C1[np.ix_(S, S)] @ Ci, C2[np.ix_(S, S)] @ Ci
            D = R2 - R1 @ R1
            dl1, _, _ = ar1_quantities(Css, Cdt[np.ix_(S, S)], Jdisc[np.ix_(S, S)], ig, ip, dt, 1)
            dl, jf, jar = ar1_quantities(Css, Ct0[np.ix_(S, S)], Jdisc[np.ix_(S, S)], ig, ip, dt, m0)
            rows.append((mi, kind, k, bias, M.R, np.linalg.norm(D), D[ig, ip], dl, jar - M.R, dl1))
    mi, kind, k, bias, R, DF, Dgp, dl, arerr, dl1 = map(np.array, zip(*rows))
    ab = np.abs(bias)
    small = ab < 0.2 * R
    out['pop'] = dict(model=mi, kind=kind, k=k, bias=bias, R=R, DF=DF, Dgp=Dgp, Delta=dl, ar1_err=arerr, Delta_tau0_dt=dl1,
                      tau0=m0 * dt,
                      spearman=dict(DF=spearmanr(DF, ab)[0], Dgp=spearmanr(np.abs(Dgp), ab)[0],
                                    Delta=spearmanr(np.abs(dl), ab)[0], Delta_tau0_dt=spearmanr(np.abs(dl1), ab)[0]),
                      small_bias=dict(n=int(small.sum()), spearman_Delta=spearmanr(np.abs(dl[small]), ab[small])[0],
                                      spearman_Delta_tau0_dt=spearmanr(np.abs(dl1[small]), ab[small])[0],
                                      spearman_DF=spearmanr(DF[small], ab[small])[0],
                                      sign_agree_Delta=np.mean(np.sign(dl[small]) == np.sign(bias[small])),
                                      sign_agree_Delta_tau0_dt=np.mean(np.sign(dl1[small]) == np.sign(bias[small])),
                                      med_abs_diff_rel=np.median(np.abs(dl[small] - bias[small]) / R[small])),
                      ratio_Delta_bias=dict(median=np.median(dl / bias), q10=np.quantile(dl / bias, 0.1),
                                            q90=np.quantile(dl / bias, 0.9), same_sign=np.mean(np.sign(dl) == np.sign(bias))),
                      ar1_vs_fdt=dict(kauz_med_rel_ar1=[np.median(np.abs(arerr[(kind == 'kauz') & (k == kk)]) / R[(kind == 'kauz') & (k == kk)]) for kk in range(9)],
                                      kauz_med_rel_fdt=[np.median(ab[(kind == 'kauz') & (k == kk)] / R[(kind == 'kauz') & (k == kk)]) for kk in range(9)]),
                      dt=dt, d1=d1)
    if do_power:
        out['power'] = power_study(pseq)
    return out


def boot_stat(X, dt, L, ig, ip, l1, m0):
    """Statistics for series X (..., N, k): Delta_gp(m0 dt) and ||R(2 l1) - R(l1)^2||_F."""
    st = series_stats(X, dt, L, lags=tuple(sorted({m0, l1, 2 * l1})))
    dl, _, _ = ar1_quantities(st['C0'], st['lag'][m0], st['Cint'], ig, ip, dt, m0)
    Ci = np.linalg.inv(st['C0'])
    R1, R2 = st['lag'][l1] @ Ci, st['lag'][2 * l1] @ Ci
    return dl, np.linalg.norm(R2 - R1 @ R1, axis=(-2, -1)), st


def power_study(pseq, R=100, B=59, dt=0.25, tau_max=20.0, d1=1.0, m0=8, seed=41, Ts=(50, 100, 200, 400, 800)):
    A, C0, Q = truth(); M = Model(A, C0, Q)
    L = int(tau_max / dt); l1 = int(d1 / dt)
    sets = dict(pg=[P, G], near1=sorted([P, G] + NEAR[:1]), kauz3=sorted(pseq[3]))
    rng = np.random.default_rng(seed)
    res = dict(Ts=list(Ts), R=R, B=B, dt=dt, tau_max=tau_max, d1=d1, tau0=m0 * dt, sets={k: v for k, v in sets.items()})
    for name, S in list(sets.items()) + [('null_pg', [P, G])]:
        S = list(S); ig, ip = S.index(G), S.index(P)
        pw = dict(Delta=[], DF=[], Delta_med=[], Delta_q10=[], Delta_q90=[])
        Css = C0[np.ix_(S, S)]
        Jd = pop_disc(A, C0, dt, L)[np.ix_(S, S)]
        Ct0 = (expm(A * m0 * dt) @ C0)[np.ix_(S, S)]
        pw['Delta_pop'] = float(ar1_quantities(Css, Ct0, Jd, ig, ip, dt, m0)[0])
        pw['bias'] = M.fdt(S) - M.R
        for T in Ts:
            N = int(T / dt)
            if name.startswith('null'):                 # exactly Markov data: LIM(tau0) surrogate of the S-process
                Gp = mroot(Ct0 @ np.linalg.inv(Css), m0); Sg = psd(Css - Gp @ Css @ Gp.T)
                X = ar1_sim(np.broadcast_to(Gp, (R,) + Gp.shape), np.broadcast_to(Sg, (R,) + Sg.shape),
                            np.broadcast_to(Css, (R,) + Css.shape), N, rng)
                X = X - X.mean(-2, keepdims=True)
            else:
                X = ou_series(A, C0, dt, N, R, rng, S)
            dl, dF, st = boot_stat(X, dt, L, ig, ip, l1, m0)
            # parametric bootstrap from the fitted LIM(tau0) of each record, sampled at dt
            Gh = mroot(st['lag'][m0] @ np.linalg.inv(st['C0']), m0)
            Sh = st['C0'] - Gh @ st['C0'] @ np.swapaxes(Gh, -1, -2)
            Sh = psd(Sh)
            rej_d = np.zeros(R, bool); rej_f = np.zeros(R, bool)
            ch = max(1, int(8e6 // (B * N * len(S))))
            for r0 in range(0, R, ch):
                r1 = min(R, r0 + ch); rr = r1 - r0
                Xb = ar1_sim(np.repeat(Gh[r0:r1], B, 0), np.repeat(Sh[r0:r1], B, 0), np.repeat(st['C0'][r0:r1], B, 0), N, rng)
                Xb = Xb - Xb.mean(-2, keepdims=True)
                db, fb, _ = boot_stat(Xb, dt, L, ig, ip, l1, m0)
                db = db.reshape(rr, B); fb = fb.reshape(rr, B)
                rej_d[r0:r1] = (1 + (np.abs(db) >= np.abs(dl[r0:r1, None])).sum(1)) / (B + 1) <= 0.05
                rej_f[r0:r1] = (1 + (fb >= dF[r0:r1, None]).sum(1)) / (B + 1) <= 0.05
            pw['Delta'].append(rej_d.mean()); pw['DF'].append(rej_f.mean())
            pw['Delta_med'].append(np.median(dl)); pw['Delta_q10'].append(np.quantile(dl, 0.1)); pw['Delta_q90'].append(np.quantile(dl, 0.9))
        res[name] = pw
        print(f'    power {name}: Delta {np.round(pw["Delta"], 3)} DF {np.round(pw["DF"], 3)}', flush=True)
    return res


def psd(S):
    w, V = np.linalg.eigh((S + np.swapaxes(S, -1, -2)) / 2)
    return (V * np.maximum(w, 1e-12)[..., None, :]) @ np.swapaxes(V, -1, -2)


def ar1_sim(Gs, Ss, C0s, N, rng):
    """Stationary AR(1) records x_{t+1} = G x_t + e_t, e ~ N(0, S), x_0 ~ N(0, C0); batch over the first axis."""
    Gs, Ss, C0s = np.asarray(Gs), np.asarray(Ss), np.asarray(C0s)
    b, k = Gs.shape[0], Gs.shape[-1]
    Lc = np.linalg.cholesky(psd(Ss) + 1e-12 * np.eye(k)); L0 = np.linalg.cholesky(psd(C0s) + 1e-12 * np.eye(k))
    X = np.empty((b, N, k))
    x = np.einsum('bij,bj->bi', L0, rng.standard_normal((b, k)))
    E = np.einsum('bij,btj->bti', Lc, rng.standard_normal((b, N, k)))
    for t in range(N):
        X[:, t] = x
        x = np.einsum('bij,bj->bi', Gs, x) + E[:, t]
    return X


def ou_series(A, C0, dt, N, R, rng, cells, max_elems=6e6):
    m = A.shape[0]
    Phi = expm(A * dt); Sig = C0 - Phi @ C0 @ Phi.T; Sig = (Sig + Sig.T) / 2
    Ls = cholesky(Sig + 1e-15 * np.eye(m), lower=True); L0 = cholesky(C0, lower=True)
    X = np.empty((R, N, len(cells)))
    chunk = max(1, int(max_elems // (N * m)))
    for r0 in range(0, R, chunk):
        r = min(chunk, R - r0)
        x = rng.standard_normal((r, m)) @ L0.T
        Z = rng.standard_normal((r, N, m)) @ Ls.T
        for t in range(N):
            X[r0:r0 + r, t] = x[:, cells]
            x = x @ Phi.T + Z[:, t]
    return X - X.mean(1, keepdims=True)


# ---------------------------------------------------------------------------------------------- 6. MSE
def sec_mse(Ts=(100.0, 1000.0), dt=0.1, tau_max=20.0, n_design_reps=40, n_test=40, n_test_reps=100, kmax=8, seed=51):
    L = int(tau_max / dt)
    ens = [Model(*m) for m in design_ensemble()]
    Rd = np.array([m.R for m in ens])
    ebias = lambda S: np.mean((fdt_many(ens, S) - Rd) ** 2)
    pseq = greedy(ens, kmax, ebias)
    tst = [Model(*m) for m in test_models(n_test)]
    Rt = np.array([m.R for m in tst])
    rng = np.random.default_rng(seed)
    out = dict(Ts=list(Ts), dt=dt, tau_max=tau_max, n_design_reps=n_design_reps, n_test=n_test, n_test_reps=n_test_reps,
               kauz_seq=pseq)
    # population (discretised, truncated) bias of every test model along a sequence
    Jt = [pop_disc(m.A, m.C0, dt, L) for m in tst]

    def popbias(S):
        S = list(S); v = []
        for m, J in zip(tst, Jt):
            x = np.linalg.solve(m.C0[np.ix_(S, S)], np.eye(len(S))[:, S.index(P)])
            v.append(J[G, S] @ x - m.R)
        return np.array(v)
    for T in Ts:
        N = int(T / dt); t0 = time.time()
        dstats = [ou_stats(m.A, m.C0, dt, N, n_design_reps, rng, L) for m in ens]
        t_design = time.time() - t0

        def mse_crit(S):
            return np.mean([np.mean((theta_from_stats(st['C0'], st['Cint'], S) - m.R) ** 2) for st, m in zip(dstats, ens)])
        mseq = greedy(ens, kmax, mse_crit)
        t0 = time.time()
        tstats = [ou_stats(m.A, m.C0, dt, N, n_test_reps, rng, L) for m in tst]
        t_test = time.time() - t0
        res = {}
        for name, seq in (('kauz', pseq), ('mse', mseq), ('near', [[P, G] + NEAR[:k] for k in range(kmax + 1)])):
            rows = []
            for S in seq:
                th = np.array([theta_from_stats(st['C0'], st['Cint'], S) for st in tstats])   # (models, reps)
                err = th - Rt[:, None]
                pb = popbias(S)
                rows.append(dict(S=sorted(S), mse=np.mean(err ** 2), mse_se=np.std(np.mean(err ** 2, 1)) / np.sqrt(n_test),
                                 bias2_pop=np.mean(pb ** 2), bias2_exact=np.mean((fdt_many(tst, S) - Rt) ** 2),
                                 var=np.mean(th.var(1, ddof=1)), sq_mean_err=np.mean((th.mean(1) - Rt) ** 2),
                                 med_rel=np.median(np.abs(err) / Rt[:, None]),
                                 mse_rel=np.mean((err / Rt[:, None]) ** 2)))
            res[name] = rows
        naive = np.array([st['C0'][:, G, P] / st['C0'][:, P, P] for st in tstats])
        res['naive'] = dict(mse=np.mean((naive - Rt[:, None]) ** 2), med_rel=np.median(np.abs(naive - Rt[:, None]) / Rt[:, None]),
                            var=np.mean(naive.var(1, ddof=1)))
        res['mse_seq'] = mseq
        res['kstar'] = dict(kauz=int(np.argmin([r['mse'] for r in res['kauz']])), mse=int(np.argmin([r['mse'] for r in res['mse']])))
        res['runtime'] = dict(design_sims_s=t_design, test_sims_s=t_test)
        out[f'T={T:g}'] = res
        print(f'    T={T:g}: kstar {res["kstar"]}  design {t_design:.0f}s test {t_test:.0f}s', flush=True)
    # passive FDT vs an intervention on the true model: record length for sd(R_hat) = 0.2 R_gp
    A, C0, Q = truth(); Mt = Model(A, C0, Q); S6 = pseq[6]
    st = ou_stats(A, C0, dt, int(1000 / dt), 60, rng, L)
    th = theta_from_stats(st['C0'], st['Cint'], S6)
    sd1000 = th.std(ddof=1); target = 0.2 * Mt.R
    Sgg = 2 * Mt.Cint[G, G]                                   # long-run variance (spectral density at 0) of x_g
    out['intervention_vs_fdt'] = dict(S=sorted(S6), R=Mt.R, fdt_sd_T1000=sd1000, fdt_mean_T1000=th.mean(),
                                      fdt_T_needed=1000 * (sd1000 / target) ** 2, S_gg0=Sgg,
                                      switchback_T_needed={str(dF): 4 * Sgg / (target * dF) ** 2 for dF in (0.5, 1.0, 2.0)},
                                      tau_c=-1 / np.linalg.eigvals(A).real.max(),
                                      note='switchback: two halves of length T/2 with forcing 0 and dF at p, asymptotic variance '
                                           '4 S_gg(0)/(T dF^2), switching transients ignored')
    return out


# ----------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--skip-l96', action='store_true')
    ap.add_argument('--only', default='')
    a = ap.parse_args()
    secs = a.only.split(',') if a.only else ['theorem', 'numbers', 'chaos', 'pumping', 'semigroup', 'mse']
    res = {}
    if os.path.exists(OUT) and a.only:
        res = json.load(open(OUT))
    timing = res.get('timing', {})
    T0 = time.time()
    for s in secs:
        t0 = time.time(); print(f'[{s}]', flush=True)
        if s == 'theorem':
            res[s] = sec_theorem()
        elif s == 'numbers':
            res[s] = sec_numbers(do_l96=not a.skip_l96)
        elif s == 'chaos':
            res[s] = sec_chaos()
        elif s == 'pumping':
            res[s] = sec_pumping()
        elif s == 'semigroup':
            res[s] = sec_semigroup()
        elif s == 'mse':
            res[s] = sec_mse()
        timing[s] = time.time() - t0
        print(f'  {s}: {timing[s]:.1f} s', flush=True)
        res['timing'] = timing
        with open(OUT, 'w') as f:
            json.dump(res, f, default=conv)
    print(f'total {time.time() - T0:.1f} s -> {OUT}')


if __name__ == '__main__':
    main()
