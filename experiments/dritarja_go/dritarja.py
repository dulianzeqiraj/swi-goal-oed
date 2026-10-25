"""DRITARJA-GO (dritarja: the window). Innovation of review 50 (deep reinforcement learning, partial observation).

The pumping agent of reviews 46-48 does not see the state of the aquifer. Monthly linear model, state z = (m, h, X, c):
    m' = 0.7 m + 0.5 w_m                      soil-moisture index (not measured)
    h' = 0.85 h + 0.3 m - 0.3 q + 0.1 w_h     coastal head (measured, noise sd 0.05)
    X' = 0.9 X - 0.5 h + 0.1 c + 0.1 w_X      landward toe advance (hidden)
    c' = 0.995 c + 0.02 X + 0.02 w_c          salt stored in the clays (hidden)
    y_Cl = X + 0.5 c + noise (sd 0.3)         chloride at a sentinel well
Cost per month X^2 + 0.5 q^2 (average cost). The toe-clay loop is unstable without pumping control.

Proposition D (review 50, section 9): (i) the LQG-optimal controller is a filter of order n = 4, so a policy that sees the
last n + 1 observations and its own last n pumping rates (an ARX window) can be exactly optimal; (ii) a policy that sees
only observations (frame stacking) needs an infinite window: truncating the optimal controller's impulse response to w
observations costs J(H_w) - J* = O(rho_c^(2w)), rho_c the spectral radius of the controller, and short windows may not
stabilise the aquifer at all.
Part A (this file, exact): costs by Lyapunov equations for the optimal, truncated (FIR) and ARX controllers, the decay
rate, and a sensitivity scan over the sentinel well. Part B (dritarja_neural.py): neural policies trained through a
differentiable simulator. Writes dritarja_results.json and dritarja.log.
"""
import json
import math
import os

import numpy as np
from scipy.linalg import solve_discrete_are, solve_discrete_lyapunov
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
A = np.array([[0.7, 0, 0, 0], [0.3, 0.85, 0, 0], [0, -0.5, 0.9, 0.1], [0, 0, 0.02, 0.995]])
B = np.array([[0.0], [-0.3], [0.0], [0.0]])
W = np.diag([0.5, 0.1, 0.1, 0.02]) ** 2
Q = np.diag([0, 0, 1.0, 0])
R = np.array([[0.5]])
N_STATE = 4
KAPPA, SD_H, SD_CL = 0.5, 0.05, 0.3


def obs_model(kappa=KAPPA, sd_h=SD_H, sd_cl=SD_CL):
    C = np.array([[0, 1.0, 0, 0], [0, 0, 1.0, kappa]])
    V = np.diag([sd_h, sd_cl]) ** 2
    return C, V


def lqg(C, V):
    P = solve_discrete_are(A, B, Q, R)
    K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
    S = solve_discrete_are(A.T, C.T, W, V)                      # prior (one-step) error covariance
    M = S @ C.T @ np.linalg.inv(C @ S @ C.T + V)                # measurement update gain
    ABK = A - B @ K
    F = ABK @ (np.eye(N_STATE) - M @ C)                         # controller state matrix
    G = ABK @ M
    Hc = -K @ (np.eye(N_STATE) - M @ C)
    Dc = -K @ M
    return dict(P=P, K=K, S=S, M=M, F=F, G=G, Hc=Hc, Dc=Dc)


def cost(C, V, Ac, Bc, Cc, Dc):
    """Average cost of the closed loop of the aquifer with the LTI controller xi' = Ac xi + Bc y, u = Cc xi + Dc y."""
    n, p, k = N_STATE, C.shape[0], Ac.shape[0]
    Acl = np.block([[A + B @ Dc @ C, B @ Cc], [Bc @ C, Ac]])
    if np.max(np.abs(np.linalg.eigvals(Acl))) >= 1 - 1e-12:
        return float('inf')
    Gn = np.block([[np.eye(n), B @ Dc], [np.zeros((k, n)), Bc]])
    Nz = np.block([[W, np.zeros((n, p))], [np.zeros((p, n)), V]])
    Sig = solve_discrete_lyapunov(Acl, Gn @ Nz @ Gn.T)
    Lu = np.hstack([Dc @ C, Cc])
    return float(np.trace(Q @ Sig[:n, :n]) + np.trace(R @ (Lu @ Sig @ Lu.T + Dc @ V @ Dc.T)))


def markov(L, kmax):
    return [L['Dc']] + [L['Hc'] @ np.linalg.matrix_power(L['F'], k - 1) @ L['G'] for k in range(1, kmax)]


def fir_controller(h, w, p):
    """u_t = sum_{k<w} h_k y_{t-k} as a state-space controller (shift register of past observations)."""
    if w == 1:
        return np.zeros((1, 1)), np.zeros((1, p)), np.zeros((1, 1)), h[0]
    k = (w - 1) * p
    Ac = np.zeros((k, k)); Ac[p:, :-p] = np.eye(k - p)
    Bc = np.zeros((k, p)); Bc[:p] = np.eye(p)
    return Ac, Bc, np.hstack(h[1:w]), h[0]


def arx_coefficients(L, n=N_STATE):
    """D(q) u = N(q) y with D the characteristic polynomial of F: u_t = -sum d_k u_{t-k} + sum_{k=0}^n N_k y_{t-k}."""
    d = np.real(np.poly(L['F']))                               # d[0] = 1
    h = markov(L, 2 * n + 3)
    Ncoef = [sum(d[j] * h[k - j] for j in range(0, min(k, n) + 1)) for k in range(0, 2 * n + 2)]
    return d, Ncoef


def arx_controller(d, Ncoef, n, p):
    """State (u_{t-1..t-n}, y_{t-1..t-n}); output u_t = -sum d_k u_{t-k} + sum N_k y_{t-k}."""
    du, dy = n, n * p
    k = du + dy
    Cc = np.hstack([-d[1:n + 1].reshape(1, -1), np.hstack(Ncoef[1:n + 1])])
    Dc = Ncoef[0]
    Ac = np.zeros((k, k)); Bc = np.zeros((k, p))
    # new u_{t} enters the first u-slot: u_t = Cc xi + Dc y_t
    Ac[0, :] = Cc[0]; Bc[0, :] = Dc[0]
    Ac[1:du, 0:du - 1] = np.eye(du - 1)
    Bc[du:du + p, :] = np.eye(p)
    Ac[du + p:, du:du + dy - p] = np.eye(dy - p)
    return Ac, Bc, Cc, Dc


def optimised_windows(C, V, L, Js):
    """Best linear policy for each window (observation-only FIR of length w; ARX of order k), by L-BFGS on the exact
    Lyapunov cost, continued from longer to shorter windows so that every start is stabilising."""
    p = C.shape[0]
    h = markov(L, 40)

    def J_fir(th, w):
        J = cost(C, V, *fir_controller([th[p * k:p * k + p].reshape(1, p) for k in range(w)], w, p))
        return J if np.isfinite(J) else 1e6
    fir_opt, theta = {}, np.concatenate([x.ravel() for x in h[:32]])
    for w in [32, 24, 16, 12, 10, 8, 7, 6, 5, 4, 3, 2]:
        r = minimize(lambda th: J_fir(th, w), theta[:p * w], method='L-BFGS-B', options=dict(maxiter=1000))
        theta = r.x; fir_opt[w] = (float(r.fun), r.x.copy())
    grid = np.linspace(-30, 30, 241)                              # one observation: grid search over static gains
    best = min(((J_fir(np.array([a, b]), 1), a, b) for a in grid for b in grid), key=lambda t: t[0])
    r = minimize(lambda th: J_fir(th, 1), np.array(best[1:]), method='L-BFGS-B')
    fir_opt[1] = (float(r.fun), r.x.copy())

    def J_arx(th, k):
        dk = np.concatenate([[1.0], th[:k]])
        Nk = [th[k + p * j:k + p * j + p].reshape(1, p) for j in range(k + 1)]
        J = cost(C, V, *arx_controller(dk, Nk, k, p))
        return J if np.isfinite(J) else 1e6
    arx_opt, prev = {}, None
    d0, N0 = arx_coefficients(L)
    exact = np.concatenate([d0[1:5], np.concatenate([x.ravel() for x in N0[:5]])])
    for k in [4, 3, 2, 1]:                    # the problem is not convex: several starts, best kept
        starts = [np.concatenate([np.zeros(k), fir_opt[k + 1][1]]),             # an observation-only start
                  np.concatenate([exact[:k], exact[4:4 + p * (k + 1)]])]          # the exact ARX(4), truncated
        if prev is not None:
            starts.append(np.concatenate([prev[:k], prev[k + 1:k + 1 + p * (k + 1)]]))   # previous order, last lag dropped
        rs = [minimize(lambda th: J_arx(th, k), s0, method='L-BFGS-B', options=dict(maxiter=2000)) for s0 in starts]
        r = min(rs, key=lambda t: t.fun)
        arx_opt[k] = float(r.fun); prev = r.x
    return {w: v[0] for w, v in fir_opt.items()}, arx_opt


def analyse(C, V, ws):
    p = C.shape[0]
    L = lqg(C, V)
    Js = cost(C, V, L['F'], L['G'], L['Hc'], L['Dc'])
    h = markov(L, max(ws) + 1)
    fir = {int(w): cost(C, V, *fir_controller(h, w, p)) for w in ws}
    rho = float(np.max(np.abs(np.linalg.eigvals(L['F']))))
    return L, Js, fir, rho


def run():
    log, res = [], {}
    C, V = obs_model()
    p = C.shape[0]
    ws = list(range(1, 17)) + [20, 24, 28, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 256]
    L, Js, fir, rho = analyse(C, V, ws)
    Jfull = float(np.trace(L['P'] @ W))
    lamF = np.linalg.eigvals(L['F'])
    res['setup'] = dict(A=A.tolist(), B=B.ravel().tolist(), W=np.diag(W).tolist(), C=C.tolist(), V=np.diag(V).tolist(),
                        kappa=KAPPA, sd_h=SD_H, sd_cl=SD_CL, open_loop_eigs=np.sort(np.abs(np.linalg.eigvals(A)))[::-1].tolist())
    res['J_star'] = Js; res['J_full_state'] = Jfull
    res['K'] = L['K'][0].tolist()
    res['controller_poles'] = sorted([float(abs(x)) for x in lamF], reverse=True)
    res['rho_c'] = rho
    res['closed_loop_state_eigs'] = sorted([float(abs(x)) for x in np.linalg.eigvals(A - B @ L['K'])], reverse=True)
    res['filter_eigs'] = sorted([float(abs(x)) for x in np.linalg.eigvals(A @ (np.eye(N_STATE) - L['M'] @ C))], reverse=True)
    res['fir'] = {str(w): fir[w] for w in ws}
    rel = {w: (fir[w] - Js) / Js for w in ws}
    finite = [w for w in ws if np.isfinite(fir[w])]
    res['fir_min_stable_w'] = int(min(finite))
    # decay rate of the excess cost between w = 48 and w = 128 against rho_c^2
    w1, w2 = 48, 128
    slope = (np.log(rel[w2]) - np.log(rel[w1])) / (w2 - w1)
    res['decay_measured'] = float(np.exp(slope)); res['decay_predicted'] = rho ** 2
    res['w_for_1pct'] = int(min(w for w in finite if rel[w] < 0.01))
    res['w_for_0p1pct'] = int(min(w for w in finite if rel[w] < 0.001))
    log.append(f'open-loop eigenvalue moduli {np.round(res["setup"]["open_loop_eigs"], 4)} (the toe-clay loop is unstable)')
    log.append(f'J* (LQG, head + sentinel chloride) = {Js:.4f}; full-state LQR {Jfull:.4f} (x{Js / Jfull:.2f})')
    log.append(f'controller poles {np.round(res["controller_poles"], 4)}; filter poles {np.round(res["filter_eigs"], 4)}')
    log.append('observation-only window (truncated optimal controller), relative excess cost: ' +
               ', '.join(f'w={w} {"unstable" if not np.isfinite(rel[w]) else f"{rel[w]:.2e}"}' for w in [1, 2, 4, 5, 8, 16, 32, 64, 128]))
    log.append(f'smallest stabilising window {res["fir_min_stable_w"]}; window for 1% excess {res["w_for_1pct"]}, for 0.1% '
               f'{res["w_for_0p1pct"]}; decay per extra observation {res["decay_measured"]:.4f} (predicted rho_c^2 = {rho ** 2:.4f})')
    # ARX window of n observations and n actions
    d, Nc = arx_coefficients(L)
    Jarx = cost(C, V, *arx_controller(d, Nc, N_STATE, p))
    tail = float(max(np.linalg.norm(x) for x in Nc[N_STATE + 1:]))
    res['arx'] = dict(J=Jarx, rel_err=abs(Jarx - Js) / Js, d=d.tolist(), N=[x.ravel().tolist() for x in Nc[:N_STATE + 1]],
                      tail_norm=tail)
    log.append(f'ARX window ({N_STATE} past actions, {N_STATE + 1} observations): J = {Jarx:.6f}, relative difference from '
               f'J* {abs(Jarx - Js) / Js:.1e}; numerator coefficients beyond lag {N_STATE}: max norm {tail:.1e} (Cayley-Hamilton)')
    # the best linear policy for each window, re-optimised (not truncated)
    fo, ao = optimised_windows(C, V, L, Js)
    res['fir_opt'] = {str(w): v for w, v in sorted(fo.items())}
    res['arx_opt'] = {str(k): v for k, v in sorted(ao.items())}
    log.append('best linear observation-only window, relative excess: ' + ', '.join(f'w={w} {(v - Js) / Js:.2e}' for w, v in sorted(fo.items())))
    log.append('best linear ARX window of order k (k past actions, k+1 observations), relative excess: ' +
               ', '.join(f'k={k} {(v - Js) / Js:.2e}' for k, v in sorted(ao.items())))
    # sensitivity: how the sentinel well sets the memory needed
    scan = []
    for kappa in [0.25, 0.5, 1.0, 2.0]:
        for sd in [0.1, 0.3, 0.6]:
            Cs, Vs = obs_model(kappa=kappa, sd_cl=sd)
            wss = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384]
            Ls, Jss, firs, rhos = analyse(Cs, Vs, wss)
            rels = {w: (firs[w] - Jss) / Jss for w in wss}
            fin = [w for w in wss if np.isfinite(firs[w])]
            w1p = min([w for w in fin if rels[w] < 0.01], default=None)
            scan.append(dict(kappa=kappa, sd_cl=sd, rho_c=rhos, J_star=Jss, min_stable=min(fin) if fin else None, w_1pct=w1p))
            log.append(f'kappa {kappa:4.2f}, chloride noise sd {sd:.1f}: rho_c {rhos:.4f}, J* {Jss:.4f}, smallest stabilising '
                       f'window {min(fin) if fin else None}, window for 1% excess {w1p}')
    res['scan'] = scan
    def clean(o):                                   # unstable windows have infinite cost: stored as null
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, list):
            return [clean(v) for v in o]
        return None if isinstance(o, float) and not math.isfinite(o) else o
    json.dump(clean(res), open(os.path.join(HERE, 'dritarja_results.json'), 'w'), indent=1)
    open(os.path.join(HERE, 'dritarja.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    run()
