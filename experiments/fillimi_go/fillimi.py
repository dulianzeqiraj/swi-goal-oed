"""FILLIMI-GO (fillimi: the beginning). Innovation of review 44 (boundary and initial conditions).

When does the initial condition stop mattering and the boundary forcing take over, and what does memory do to
that handover? Test bed: a 1-D coastal aquifer (sea at x = 0, no-flow inland at x = L) with the linearised
head equation and a completely monotone aquitard memory written as a Markovian embedding,

    S_y dh/dt = T h_xx - sum_k s_k a_k (h - h_k) + r(t),      dh_k/dt = a_k (h - h_k),     h(0, t) = eta(t),

where h_k are the heads of K aquitard storage compartments (rates a_k, capacities s_k). The system is self-adjoint
in the storage-weighted inner product W = diag(S_y, s_k), so every goal response is completely monotone.
Boundary forcing: sea-level anomaly eta and recharge anomaly r, both Ornstein-Uhlenbeck processes.
Goal: the head g(t) = h(x_g, t) at a coastal well.

Writes fillimi_results.json and fillimi.log. Theory: section 9 of review 44 (Theorem F).
"""
import json
import os
import time

import numpy as np
from scipy.linalg import expm, eigh, solve_continuous_lyapunov

HERE = os.path.dirname(os.path.abspath(__file__))
YR = 365.25
P = dict(L=5000.0, N=50, T=1000.0 * YR, Sy=0.10, sig_ic=0.5, x_goal=500.0,
         sig_eta=0.10, tau_eta=0.5, sig_r=0.10, tau_r=1.0,
         K=12, a_min=1e-3, a_max=1.0, cap_ratio=3.0, beta=0.5, a_single=0.05)


def build(case, P=P):
    """Matrices of dz/dt = -M z + b_eta eta + b_r r, z = [h (N), h_1 (N), ..., h_K (N)], and weights W."""
    N, L, T, Sy = P['N'], P['L'], P['T'], P['Sy']
    dx = L / N
    x = (np.arange(N) + 0.5) * dx
    if case == 'none':
        a, s = np.array([]), np.array([])
    elif case == 'single':
        a, s = np.array([P['a_single']]), np.array([P['cap_ratio'] * Sy])
    else:  # power-law spectrum of rates: capacity density ~ a^(beta - 1) da on a log grid -> weights ~ a^beta
        a = np.logspace(np.log10(P['a_min']), np.log10(P['a_max']), P['K'])
        w = a ** P['beta']
        s = P['cap_ratio'] * Sy * w / w.sum()
    K = len(a)
    n = N * (K + 1)
    Lap = np.zeros((N, N))
    for i in range(N):
        if i > 0:
            Lap[i, i - 1] += 1; Lap[i, i] -= 1
        if i < N - 1:
            Lap[i, i + 1] += 1; Lap[i, i] -= 1
    Lap[0, 0] -= 2                                   # Dirichlet sea boundary at half a cell
    Lap *= T / dx ** 2
    M = np.zeros((n, n))
    M[:N, :N] = -Lap / Sy
    for k in range(K):
        sl = slice(N * (k + 1), N * (k + 2))
        M[:N, :N] += np.eye(N) * s[k] * a[k] / Sy
        M[:N, sl] -= np.eye(N) * s[k] * a[k] / Sy
        M[sl, sl] += np.eye(N) * a[k]
        M[sl, :N] -= np.eye(N) * a[k]
    W = np.concatenate([np.full(N, Sy)] + [np.full(N, s[k]) for k in range(K)])
    b_eta = np.zeros(n); b_eta[0] = 2 * T / dx ** 2 / Sy
    b_r = np.zeros(n); b_r[:N] = 1.0 / Sy
    g = np.zeros(n); g[int(P['x_goal'] // dx)] = 1.0
    return dict(M=M, W=W, b_eta=b_eta, b_r=b_r, g=g, x=x, a=a, s=s, N=N, K=K, n=n)


def ic_variance(S, P0, times):
    """V_IC(t) = g' e^{-Mt} P0 e^{-M't} g, exactly, by the symmetric eigen-decomposition."""
    Wh = np.sqrt(S['W'])
    Msym = (Wh[:, None] * S['M']) / Wh[None, :]
    Msym = 0.5 * (Msym + Msym.T)
    lam, U = eigh(Msym)
    # e^{-Mt} = W^{-1/2} U e^{-lam t} U' W^{1/2};  row g' e^{-Mt} = (g/Wh)' U e^{-lam t} U' diag(Wh)
    left = (S['g'] / Wh) @ U                                   # n
    right = U.T * Wh[None, :]                                  # n x n
    out = []
    for t in times:
        row = (left * np.exp(-lam * t)) @ right
        out.append(row @ P0 @ row)
    return np.array(out), lam, left, right


def bc_variance(S, P, times, g):
    """Goal variance from the stationary stochastic boundary forcing, started from a known state:
    P(t) = P_inf + e^{At} (P(0) - P_inf) e^{A't}, exact for the linear system driven by Ornstein-Uhlenbeck forcing."""
    n = S['n']
    A = np.zeros((n + 2, n + 2))
    A[:n, :n] = -S['M']; A[:n, n] = S['b_eta']; A[:n, n + 1] = S['b_r']
    A[n, n] = -1 / P['tau_eta']; A[n + 1, n + 1] = -1 / P['tau_r']
    Q = np.zeros((n + 2, n + 2))
    Q[n, n] = 2 * P['sig_eta'] ** 2 / P['tau_eta']; Q[n + 1, n + 1] = 2 * P['sig_r'] ** 2 / P['tau_r']
    P0 = np.zeros((n + 2, n + 2)); P0[n, n] = P['sig_eta'] ** 2; P0[n + 1, n + 1] = P['sig_r'] ** 2
    Pinf = solve_continuous_lyapunov(A, -Q)
    ga = np.concatenate([g, [0, 0]])
    D0 = P0 - Pinf
    out = []
    for t in times:
        row = ga @ expm(A * t)
        out.append(ga @ Pinf @ ga + row @ D0 @ row)
    return np.array(out), float(ga @ Pinf @ ga)


def handover(times, vic, vbc):
    """First time the boundary part of the goal variance exceeds the initial-condition part (log interpolation)."""
    d = np.log(vbc + 1e-300) - np.log(vic + 1e-300)
    idx = np.where(d > 0)[0]
    if len(idx) == 0:
        return None
    i = idx[0]
    if i == 0:
        return float(times[0])
    f = d[i - 1] / (d[i - 1] - d[i])
    return float(np.exp(np.log(times[i - 1]) + f * (np.log(times[i]) - np.log(times[i - 1]))))


def cm_check(t, v):
    """Signs of the first two divided differences on the (non-uniform) grid: decreasing and convex."""
    d1 = np.diff(v) / np.diff(t)
    d2 = np.diff(d1) / (0.5 * (t[2:] - t[:-2]))
    tol = 1e-12 * np.max(np.abs(v))
    return [bool(np.all(d1 <= tol)), bool(np.all(d2 >= -tol))]


def spectral(S):
    Wh = np.sqrt(S['W'])
    Msym = (Wh[:, None] * S['M']) / Wh[None, :]
    lam, U = eigh(0.5 * (Msym + Msym.T))
    return lam, U, Wh


def run():
    t0 = time.time()
    times = np.unique(np.round(np.logspace(-2, np.log10(500), 140), 6))
    N, dx = P['N'], P['L'] / P['N']
    goals = {'mobile 250 m': ('m', 250.0), 'mobile 1000 m': ('m', 1000.0), 'mobile 2500 m': ('m', 2500.0),
             'mobile 4750 m': ('m', 4750.0), 'clay 2500 m': ('c', 2500.0)}
    res = dict(P=P, times=times.tolist(), goals=list(goals), cases={})
    log = []
    for case in ('none', 'power'):
        S = build(case)
        n, K = S['n'], S['K']
        lam, U, Wh = spectral(S)
        # smooth prior that is a function of M (Matern-like): P0 = c W^{-1/2} U phi(Lam) U' W^{-1/2}
        phi = (1.0 + lam / 1.0) ** -2
        B = (U * np.sqrt(phi)[None, :]) / Wh[:, None]          # P0 = c B B'
        c = P['sig_ic'] ** 2 / np.mean(np.sum(B[:N] ** 2, axis=1))
        P0_thm = c * B @ B.T
        x = S['x']
        Cx = P['sig_ic'] ** 2 * np.exp(-np.abs(x[:, None] - x[None, :]) / 1000.0)
        P0_leg = np.zeros((n, n))
        for k in range(K):
            for k2 in range(K):
                P0_leg[N * (k + 1):N * (k + 2), N * (k2 + 1):N * (k2 + 2)] = 4.0 * Cx   # legacy drawdown in clays, sd 1 m
        out = {}
        for gname, (kind, xg) in goals.items():
            if kind == 'c' and K == 0:
                continue
            i = int(xg // dx)
            g = np.zeros(n)
            if kind == 'm':
                g[i] = 1.0
            else:                                              # piezometer in the clay: capacity-weighted aquitard head
                for k in range(K):
                    g[N * (k + 1) + i] = S['s'][k] / S['s'].sum()
            left = (g / Wh) @ U
            nu = c * phi * left ** 2                            # goal spectral weights of the smooth prior
            vic = np.array([np.sum(nu * np.exp(-2 * lam * t)) for t in times])
            row = lambda t: ((left * np.exp(-lam * t)) @ U.T) * Wh       # g' e^{-Mt}
            vic_direct = np.array([row(t) @ P0_thm @ row(t) for t in times[::20]])
            vbc, vbc_inf = bc_variance(S, P, times, g)
            lam_bar = float(np.sum(nu * lam) / np.sum(nu))
            sel = (times > 50) & (times < 400)
            o = dict(vic=vic.tolist(), vbc=vbc.tolist(), vbc_inf=vbc_inf, lam_bar=lam_bar,
                     check=float(np.max(np.abs(vic_direct - vic[::20]) / vic[::20])),
                     cm=cm_check(times, vic),
                     jensen_ok=bool(np.all(vic >= vic[0] * np.exp(-2 * lam_bar * times) * (1 - 1e-9))),
                     t_jensen=float(np.log(vic[0] / vbc_inf) / (2 * lam_bar)) if vic[0] > vbc_inf else 0.0,
                     slope=float(np.polyfit(np.log(times[sel]), np.log(vic[sel]), 1)[0]),
                     handover=handover(times, vic, vbc),
                     share20=float(np.interp(np.log(20), np.log(times), vic / (vic + vbc))),
                     vbc_monotone=bool(np.all(np.diff(vbc) >= -1e-12)))
            if K:
                rowl = [row(t) for t in times]
                vleg = np.array([r @ P0_leg @ r for r in rowl])
                imax = int(np.argmax(vleg))
                o.update(vleg=vleg.tolist(), leg_peak=[float(times[imax]), float(vleg[imax])],
                         leg_share20=float(np.interp(np.log(20), np.log(times), vleg / (vleg + vbc))),
                         leg_handover=handover(times, vleg, vbc))
            out[gname] = o
            log.append(f"{case:5s} {gname:14s} V_BC(inf)={vbc_inf:.4f} V_IC(0)={vic[0]:.4f} lam_bar={lam_bar:7.3f}/yr "
                       f"t*={o['handover']} Jensen t*>={o['t_jensen']:.2f} ok={o['jensen_ok']} cm={o['cm']} "
                       f"slope50-400={o['slope']:.2f} chk={o['check']:.1e} ICshare20={o['share20']:.3f} vbc_mono={o['vbc_monotone']}"
                       + (f" | legacy peak t={o['leg_peak'][0]:.1f} yr V={o['leg_peak'][1]:.4f} share20={o['leg_share20']:.3f} t*={o['leg_handover']}" if K else ''))
        res['cases'][case] = out
    res['runtime_s'] = time.time() - t0
    json.dump(res, open(os.path.join(HERE, 'fillimi_results.json'), 'w'))
    txt = '\n'.join(log) + f"\nruntime {res['runtime_s']:.0f} s"
    open(os.path.join(HERE, 'fillimi.log'), 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    run()
