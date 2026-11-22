"""ZBULIMI-GO (zbulimi: the discovery). Innovation of review 47 (reinforcement learning with deep mathematics II).

Several well fields share one coastal aquifer, and the response of the coastal head to each of them is unknown.
Monthly linear model, state z = (m, r, h, X), pumping anomalies q = (q_1, ..., q_p) of p well fields:
    m' = a_m m + s_m w_m                         soil-moisture index
    r' = a_r r + (1 - a_r) m                     recharge
    h' = a_h h + b_r r - beta^T q + s_h w_h      coastal head; beta = unknown responses to the p well fields
    X' = a_X X - g h + s_X w_X                   landward toe advance
Cost per month: X^2 + sum_i lam_i q_i^2. The learner estimates the head row theta = (a_h, b_r, beta) by least squares
and plays the certainty-equivalent (CE) Riccati rule.

Proposition Z (review 47, section 9): because the wells act on the state through the single combination beta^T q,
the optimal rule has rank one, q = -d kappa^T z with d proportional to R^{-1} beta: every well moves in a fixed
proportion. Along a CE path the data identify only (a_h, b_r, beta^T d); the p - 1 directions of beta orthogonal
to d are never excited, and CE can stop on the self-confirming set {beta_hat : beta_hat^T beta_hat = beta^T beta_hat}
(for R = lam I). Exploration is needed, and the cheapest exploration is head-neutral (beta_hat^T e = 0): the optimal
covariance is Gamma = M^{-1} V N G N V^T M^{-1} with M = R + B^T P B, V an orthonormal basis of d-perp,
N = (V^T M^{-1} V)^{-1} and G the minimiser of 2 tr(M_V G) + (s_h^2 / 2) tr(H_V G^{-1}), M_V = N, H_V the Hessian of
the average cost in the unexcited directions. Then regret ~ 2 s_h tr((M_V^{1/2} H_V M_V^{1/2})^{1/2}) sqrt(T),
against 2 s_h sqrt(tr M tr H_V) sqrt(T) for isotropic exploration of all wells.
Writes zbulimi_results.json and zbulimi.log.
"""
import json
import os
import time

import numpy as np
from scipy.linalg import solve_discrete_are, solve_discrete_lyapunov, sqrtm

HERE = os.path.dirname(os.path.abspath(__file__))
P = dict(a_m=0.8, s_m=0.6, a_r=0.7, a_h=0.9, b_r=0.5, s_h=0.1, a_X=0.95, g=0.5, s_X=0.1,
         beta=[0.25, 0.15, 0.05], lam=[0.3, 0.5, 0.8], beta0=[0.15, 0.15, 0.15],
         T=20000, seeds=160, update=50, warm=24, design_every=500, ridge=1e-3)
NP = len(P['beta'])


def mats(th, P=P):
    """th = (a_h, b_r, beta_1..beta_p)."""
    A = np.array([[P['a_m'], 0, 0, 0], [1 - P['a_r'], P['a_r'], 0, 0], [0, th[1], th[0], 0], [0, 0, -P['g'], P['a_X']]])
    B = np.zeros((4, len(th) - 2)); B[2, :] = -np.asarray(th[2:])
    W = np.diag([P['s_m'] ** 2, 0.0, P['s_h'] ** 2, P['s_X'] ** 2])
    Q = np.diag([0, 0, 0, 1.0])
    R = np.diag(P['lam'])
    return A, B, W, Q, R


def lqr(A, B, Q, R):
    Pm = solve_discrete_are(A, B, Q, R)
    return np.linalg.solve(R + B.T @ Pm @ B, B.T @ Pm @ A), Pm        # q = -K z


def avg_cost(A, B, W, Q, R, K, Se=None):
    """Stationary average cost of q = -K z + e, e ~ N(0, Se) white."""
    Acl = A - B @ K
    if np.max(np.abs(np.linalg.eigvals(Acl))) >= 1:
        return np.inf
    Wt = W if Se is None else W + B @ Se @ B.T
    S = solve_discrete_lyapunov(Acl, Wt)
    c = float(np.trace(Q @ S) + np.trace(K.T @ R @ K @ S))
    return c if Se is None else c + float(np.trace(R @ Se))


def theta_true():
    return np.array([P['a_h'], P['b_r']] + list(P['beta']))


def design(th, P=P, hstep=2e-3):
    """Exploration design at parameter th (used as truth by the plug-in learner and by the theory).
    Returns dict with K, M, d, V, H_V, M_V, the optimal head-neutral covariance Gam, the isotropic scale s_iso and the
    predicted sqrt(T) constants."""
    A, B, W, Q, R = mats(th, P)
    K, Pm = lqr(A, B, Q, R)
    M = R + B.T @ Pm @ B
    U, sv, _ = np.linalg.svd(K)
    d = U[:, 0]
    V = np.linalg.svd(np.eye(len(d)) - np.outer(d, d))[0][:, :len(d) - 1]   # orthonormal basis of d-perp

    def J_of(v):                                   # true (= th) cost of the CE rule computed at th + V v (beta only)
        t2 = th.copy(); t2[2:] = t2[2:] + V @ v
        A2, B2, _, _, _ = mats(t2, P)
        K2, _ = lqr(A2, B2, Q, R)
        return avg_cost(A, B, W, Q, R, K2)
    k = V.shape[1]
    H = np.zeros((k, k))
    for i in range(k):
        for j in range(k):
            ei = np.eye(k)[i] * hstep; ej = np.eye(k)[j] * hstep
            H[i, j] = (J_of(ei + ej) - J_of(ei - ej) - J_of(-ei + ej) + J_of(-ei - ej)) / (4 * hstep ** 2)
    H = 0.5 * (H + H.T)
    Minv = np.linalg.inv(M)
    N = np.linalg.inv(V.T @ Minv @ V)              # = M_V, the cost per unit information in V coordinates
    s = P['s_h']
    Aq = 2 * N; Bq = 0.5 * s ** 2 * H
    Ah = np.real(sqrtm(Aq)); Aih = np.linalg.inv(Ah)
    G = Aih @ np.real(sqrtm(Ah @ Bq @ Ah)) @ Aih
    G = 0.5 * (G + G.T)
    L = Minv @ V @ N
    Gam = L @ G @ L.T
    Gam = 0.5 * (Gam + Gam.T)
    s_iso = 0.5 * s * np.sqrt(max(np.trace(H), 0) / np.trace(M))
    MhalfV = np.real(sqrtm(N))
    c_go = 2 * s * float(np.trace(np.real(sqrtm(MhalfV @ H @ MhalfV))))
    c_iso = 2 * s * float(np.sqrt(np.trace(M) * max(np.trace(H), 0)))
    return dict(K=K, Pm=Pm, M=M, d=d, V=V, H=H, MV=N, G=G, Gam=Gam, s_iso=s_iso, c_go=c_go, c_iso=c_iso)


def run():
    t0 = time.time()
    th0 = theta_true()
    A, B, W, Q, R = mats(th0)
    Kopt, _ = lqr(A, B, Q, R)
    J_opt = avg_cost(A, B, W, Q, R, Kopt)
    D0 = design(th0)
    sv = np.linalg.svd(Kopt, compute_uv=False)
    log = [f'optimal rule K* (rows = well fields) =\n{np.round(Kopt, 4)}\nsingular values {np.round(sv, 6)} (rank one); '
           f'pumping direction d = {np.round(D0["d"], 4)}, R^-1 beta / |.| = {np.round(np.diag(1 / np.array(P["lam"])) @ P["beta"] / np.linalg.norm(np.diag(1 / np.array(P["lam"])) @ P["beta"]), 4)}',
           f'average cost J* = {J_opt:.4f}; H_V eigenvalues {np.round(np.linalg.eigvalsh(D0["H"]), 4)}; M eigenvalues {np.round(np.linalg.eigvalsh(D0["M"]), 4)}',
           f'predicted sqrt(T) constants: head-neutral goal-oriented {D0["c_go"]:.4f}, isotropic {D0["c_iso"]:.4f}, ratio {D0["c_iso"] / D0["c_go"]:.3f}',
           f'head-neutrality of the optimal design: |beta^T Gam beta| / tr(Gam) = {abs(np.array(P["beta"]) @ D0["Gam"] @ np.array(P["beta"])) / np.trace(D0["Gam"]):.2e}']
    T, S_ = P['T'], P['seeds']
    rng = np.random.default_rng(2026)
    noise = rng.standard_normal((T, 4, S_))
    learners = ['CE, no exploration', 'CE, exploration of total pumping', 'CE, isotropic exploration',
                'CE, head-neutral exploration']
    EXPL = learners[1:]
    out = {}
    for name in ['oracle'] + learners:
        z = np.zeros((4, S_))
        G = np.tile(P['ridge'] * np.eye(2 + NP)[:, :, None], (1, 1, S_))
        bvec = np.zeros((2 + NP, S_))
        th_hat = np.tile(np.array([P['a_h'], P['b_r']] + list(P['beta0']))[:, None], (1, S_))
        K = np.zeros((S_, NP, 4)); Lchol = np.zeros((S_, NP, NP))

        def recompute(s, with_design):
            Ab, Bb, _, _, _ = mats(th_hat[:, s])
            try:
                K[s] = lqr(Ab, Bb, Q, R)[0]
            except Exception:
                pass
            if with_design and name != 'CE, no exploration':
                try:
                    Dd = design(th_hat[:, s].copy())
                    if name == 'CE, head-neutral exploration':
                        Se = Dd['Gam']
                    elif name == 'CE, isotropic exploration':
                        Se = Dd['s_iso'] * np.eye(NP)
                    else:                                  # same total variance, all wells scaled together (along d)
                        Se = Dd['s_iso'] * NP * np.outer(Dd['d'], Dd['d'])
                    w, U = np.linalg.eigh(Se)
                    Lchol[s] = U @ np.diag(np.sqrt(np.maximum(w, 0)))
                except Exception:
                    pass
        if name == 'oracle':
            K[:] = Kopt
        else:
            for s in range(S_):
                recompute(s, True)
        cost = np.zeros((T, S_)); berr = []; ecost = np.zeros(S_)
        rng_e = np.random.default_rng(7)
        for t in range(T):
            q = -np.einsum('sij,js->is', K, z)
            if name in EXPL:
                e = (t + 1) ** -0.25 * np.einsum('sij,js->is', Lchol, rng_e.standard_normal((NP, S_)))
                q = q + e
            cost[t] = z[3] ** 2 + np.einsum('i,is->s', np.array(P['lam']), q ** 2)
            m, r, h, X = z
            zn = np.empty_like(z)
            zn[0] = P['a_m'] * m + P['s_m'] * noise[t, 0]
            zn[1] = P['a_r'] * r + (1 - P['a_r']) * m
            zn[2] = P['a_h'] * h + P['b_r'] * r - np.array(P['beta']) @ q + P['s_h'] * noise[t, 2]
            zn[3] = P['a_X'] * X - P['g'] * h + P['s_X'] * noise[t, 3]
            if name != 'oracle':
                x = np.vstack([h, r, -q])
                G += np.einsum('is,js->ijs', x, x); bvec += x * zn[2]
                if (t + 1) % P['update'] == 0 and t + 1 >= P['warm']:
                    th = np.linalg.solve(np.moveaxis(G, 2, 0), np.moveaxis(bvec, 1, 0)[..., None])[..., 0].T
                    th[0] = np.clip(th[0], 0, 0.99); th[2:] = np.clip(th[2:], 0.01, 1.0)
                    th_hat[:] = th
                    wd = (t + 1) % P['design_every'] == 0
                    for s in range(S_):
                        recompute(s, wd)
                if (t + 1) in (100, 1000, 10000, T):
                    err = th_hat[2:] - np.array(P['beta'])[:, None]
                    berr.append([t + 1, float(np.sqrt(np.mean(np.sum(err ** 2, 0))))])
            z = zn
        out[name] = dict(cost=cost, berr=berr, th_final=th_hat.copy())
    res = dict(P=P, K_opt=Kopt.tolist(), sv=sv.tolist(), J_opt=J_opt, d=D0['d'].tolist(), H_V=D0['H'].tolist(),
               M=D0['M'].tolist(), M_V=D0['MV'].tolist(), Gam=D0['Gam'].tolist(), s_iso=D0['s_iso'],
               c_go=D0['c_go'], c_iso=D0['c_iso'])
    grid = np.unique(np.round(np.logspace(1, np.log10(T), 40)).astype(int))
    b = np.array(P['beta'])
    for name in learners:
        reg = np.cumsum(out[name]['cost'] - out['oracle']['cost'], axis=0)
        mean = reg.mean(1); se = reg.std(1) / np.sqrt(S_)
        sel = grid[grid >= 1000]
        slope = float(np.polyfit(np.log(sel), np.log(np.maximum(mean[sel - 1], 1e-9)), 1)[0])
        Xd = np.vstack([np.sqrt(sel), np.ones_like(sel)]).T
        coef = np.linalg.lstsq(Xd, mean[sel - 1], rcond=None)[0]
        thf = out[name]['th_final'][2:]
        sphere = np.abs(np.sum(thf * thf, 0) - b @ thf)                      # distance to the self-confirming set
        tail = float((reg[-1] - reg[T // 2]).mean() / (T - T // 2))
        res[name] = dict(regret=mean[grid - 1].tolist(), se=se[grid - 1].tolist(), grid=grid.tolist(), slope=slope,
                         sqrt_coef=float(coef[0]), offset=float(coef[1]), beta_rmse=out[name]['berr'],
                         final=float(mean[-1]), final_se=float(se[-1]), tail_per_month=tail,
                         sphere_median=float(np.median(sphere)), beta_final_mean=thf.mean(1).tolist())
        log.append(f'{name:30s} regret at T={T}: {mean[-1]:8.2f} +- {se[-1]:5.2f}; log-log slope (T>=1000) {slope:4.2f}; '
                   f'fit A sqrt(T) + B: A = {coef[0]:.4f}, B = {coef[1]:.2f}; tail excess/month {tail:.4f}; '
                   f'beta RMSE at 100/1000/10000/T: {[round(x[1], 4) for x in out[name]["berr"]]}; '
                   f'median distance to self-confirming set {np.median(sphere):.2e}')
    res['runtime_s'] = time.time() - t0
    json.dump(res, open(os.path.join(HERE, 'zbulimi_results.json'), 'w'), indent=1)
    txt = '\n'.join(log) + f"\nruntime {res['runtime_s']:.0f} s"
    open(os.path.join(HERE, 'zbulimi.log'), 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    run()
