"""MESIMI-GO (mesimi: the learning). Innovation of review 46 (reinforcement learning with deep mathematics).

Learning a pumping rule online when the response of the aquifer to pumping is unknown. Monthly linear model of a
coastal aquifer, state z = (m, r, h, X):
    m' = a_m m + s_m w_m                      soil-moisture index (exogenous, drives irrigation demand)
    r' = a_r r + (1 - a_r) m                  recharge: soil moisture filtered by the unsaturated zone
    h' = a_h h + b_r r - beta q + s_h w_h     coastal head; beta = unknown response of the head to pumping q
    X' = a_X X - g h + s_X w_X                landward toe advance driven by low head
Cost per month: X^2 + lam q^2 (toe advance against water not supplied). The learner knows the structure and
estimates the head row (a_h, b_r, beta) by least squares from (h, r, q), then plays the certainty-equivalent
optimal rule of its policy class. Two classes:
    full:  q = -K z (the rule may respond to the soil-moisture index m, which is excluded from the head row);
    head:  q = -k h (the rule responds to the head only; q is then collinear with a regressor of the head row).
Proposition M (review 46, section 9): the estimate of beta is consistent without injected exploration if the
policy's variation of q orthogonal to the other regressors of the head row has positive variance; then the regret
of certainty equivalence grows like log T. If that variance is zero, certainty equivalence can lock onto a wrong
(self-confirming) value; exploration must be injected and the regret grows like sqrt T.
Writes mesimi_results.json and mesimi.log.
"""
import json
import os
import time

import numpy as np
from scipy.linalg import solve_discrete_are, solve_discrete_lyapunov
from scipy.optimize import minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
P = dict(a_m=0.8, s_m=0.6, a_r=0.7, a_h=0.9, b_r=0.5, beta=0.3, s_h=0.1, a_X=0.95, g=0.5, s_X=0.1, lam=0.5,
         beta0=0.45, T=20000, seeds=160, update=50, warm=24, ridge=1e-3)


def mats(beta, P=P):
    A = np.array([[P['a_m'], 0, 0, 0], [1 - P['a_r'], P['a_r'], 0, 0], [0, P['b_r'], P['a_h'], 0], [0, 0, -P['g'], P['a_X']]])
    B = np.array([[0.0], [0.0], [-beta], [0.0]])
    W = np.diag([P['s_m'] ** 2, 0.0, P['s_h'] ** 2, P['s_X'] ** 2])
    Q = np.diag([0, 0, 0, 1.0])
    R = np.array([[P['lam']]])
    return A, B, W, Q, R


def lqr_full(A, B, Q, R):
    Pm = solve_discrete_are(A, B, Q, R)
    return np.linalg.solve(R + B.T @ Pm @ B, B.T @ Pm @ A)          # q = -K z


def avg_cost(A, B, W, Q, R, K):
    Acl = A - B @ K
    if np.max(np.abs(np.linalg.eigvals(Acl))) >= 1:
        return np.inf
    S = solve_discrete_lyapunov(Acl, W)
    return float(np.trace(Q @ S) + np.trace(K.T @ R @ K @ S))


def k_head(A, B, W, Q, R, safe=-6.0):
    """Best head-only rule q = -k h for the model (A, B), searched inside the model's own stability region and a
    safety bound (k >= -6 keeps the true closed loop stable whatever the estimate)."""
    f = lambda k: avg_cost(A, B, W, Q, R, np.array([[0, 0, k, 0.0]]))
    lo = max(safe, -(1 + A[2, 2]) / max(-B[2, 0], 1e-6) + 1e-3)
    res = minimize_scalar(f, bounds=(lo, 0.0), method='bounded', options=dict(xatol=1e-6))
    return float(res.x)


def orth_variance(A, B, W, K):
    """Variance of q not explained by the other regressors (h, r) of the head row, under the stationary law."""
    S = solve_discrete_lyapunov(A - B @ K, W)
    q = -K[0]
    C = np.array([[0, 0, 1, 0], [0, 1, 0, 0]], float)         # h, r
    Sxx = C @ S @ C.T; Sxq = C @ S @ q; Sqq = q @ S @ q
    return float(Sqq - Sxq @ np.linalg.solve(Sxx, Sxq))


def run():
    t0 = time.time()
    A, B, W, Q, R = mats(P['beta'])
    Kf = lqr_full(A, B, Q, R)
    kh = k_head(A, B, W, Q, R)
    Kh = np.array([[0, 0, kh, 0.0]])
    J_full, J_head = avg_cost(A, B, W, Q, R, Kf), avg_cost(A, B, W, Q, R, Kh)
    s2_full, s2_head = orth_variance(A, B, W, Kf), orth_variance(A, B, W, Kh)
    log = [f'optimal full rule K* = {np.round(Kf[0], 4)} (loads on the soil-moisture index m: {Kf[0, 0]:.4f}); avg cost {J_full:.4f}',
           f'optimal head-only rule k* = {kh:.4f}; avg cost {J_head:.4f}',
           f'orthogonal variance of q in the head row: full {s2_full:.3e}, head-only {s2_head:.3e}']
    T, S_ = P['T'], P['seeds']
    rng = np.random.default_rng(2026)
    noise = rng.standard_normal((T, 4, S_))                      # common random numbers for all learners
    learners = ['full, no exploration', 'head-only, no exploration', 'head-only, exploration t^-1/4']
    out = {}
    for name in learners + ['oracle full', 'oracle head']:
        z = np.zeros((4, S_))
        G = np.tile(P['ridge'] * np.eye(3)[:, :, None], (1, 1, S_))   # Gram of (h, r, q) per seed
        bvec = np.zeros((3, S_))
        beta_hat = np.full(S_, P['beta0']); ah_hat = np.full(S_, P['a_h']); br_hat = np.full(S_, P['b_r'])
        K = np.zeros((S_, 4))
        def recompute(idx):
            for s in idx:
                Ab, Bb, Wb, Qb, Rb = mats(max(beta_hat[s], 1e-3))
                Ab[2, 2] = ah_hat[s]; Ab[2, 1] = br_hat[s]
                if name.startswith('full'):
                    try:
                        K[s] = lqr_full(Ab, Bb, Qb, Rb)[0]
                    except Exception:
                        pass
                else:
                    K[s] = [0, 0, k_head(Ab, Bb, Wb, Qb, Rb), 0]
        if name == 'oracle full':
            K[:] = Kf[0]
        elif name == 'oracle head':
            K[:] = Kh[0]
        else:
            recompute(range(S_))
        cost = np.zeros((T, S_)); berr = []
        rng_e = np.random.default_rng(7)
        for t in range(T):
            q = -np.einsum('sj,js->s', K, z)
            if name == 'head-only, exploration t^-1/4':
                q = q + (t + 1) ** -0.25 * rng_e.standard_normal(S_)
            cost[t] = z[3] ** 2 + P['lam'] * q ** 2
            m, r, h, X = z
            zn = np.empty_like(z)
            zn[0] = P['a_m'] * m + P['s_m'] * noise[t, 0]
            zn[1] = P['a_r'] * r + (1 - P['a_r']) * m
            zn[2] = P['a_h'] * h + P['b_r'] * r - P['beta'] * q + P['s_h'] * noise[t, 2]
            zn[3] = P['a_X'] * X - P['g'] * h + P['s_X'] * noise[t, 3]
            if not name.startswith('oracle'):
                x = np.vstack([h, r, -q])                          # regressors of the head row: a_h, b_r, beta
                G += np.einsum('is,js->ijs', x, x); bvec += x * zn[2]
                if (t + 1) % P['update'] == 0 and t + 1 >= P['warm']:
                    th = np.linalg.solve(np.moveaxis(G, 2, 0), np.moveaxis(bvec, 1, 0)[..., None])[..., 0]
                    ah_hat, br_hat, beta_hat = np.clip(th[:, 0], 0, 0.99), th[:, 1], np.clip(th[:, 2], 0.1, 2.0)
                    recompute(range(S_))
                if (t + 1) in (100, 1000, 10000, T):
                    berr.append([t + 1, float(np.sqrt(np.mean((beta_hat - P['beta']) ** 2)))])
            z = zn
        out[name] = dict(cost=cost, berr=berr)
    res = dict(P=P, K_full=Kf[0].tolist(), k_head=kh, J_full=J_full, J_head=J_head, s2_full=s2_full, s2_head=s2_head)
    grid = np.unique(np.round(np.logspace(1, np.log10(T), 40)).astype(int))
    for name, ref in (('full, no exploration', 'oracle full'), ('head-only, no exploration', 'oracle head'),
                      ('head-only, exploration t^-1/4', 'oracle head')):
        reg = np.cumsum(out[name]['cost'] - out[ref]['cost'], axis=0)       # common random numbers
        mean = reg.mean(1); se = reg.std(1) / np.sqrt(S_)
        sel = grid[grid >= 1000]
        slope = float(np.polyfit(np.log(sel), np.log(np.maximum(mean[sel - 1], 1e-9)), 1)[0])
        res[name] = dict(regret=mean[grid - 1].tolist(), se=se[grid - 1].tolist(), grid=grid.tolist(), slope=slope,
                         beta_rmse=out[name]['berr'], final=float(mean[-1]), final_se=float(se[-1]),
                         per_logT=float(mean[-1] / np.log(T)))
        log.append(f'{name:32s} regret at T={T}: {mean[-1]:9.2f} +- {se[-1]:6.2f}; log-log slope (T>=1000) {slope:5.2f}; '
                   f'beta RMSE at 100/1000/10000/T: {[round(b[1], 4) for b in out[name]["berr"]]}')
    res['runtime_s'] = time.time() - t0
    json.dump(res, open(os.path.join(HERE, 'mesimi_results.json'), 'w'), indent=1)
    txt = '\n'.join(log) + f"\nruntime {res['runtime_s']:.0f} s"
    open(os.path.join(HERE, 'mesimi.log'), 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    run()
