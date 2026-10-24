"""KUFIRI-GO (kufiri: the boundary). Innovation of review 45 (all the boundary and initial conditions).

A linear coastal aquifer (sea at x = 0, no-flow inland at x = L = 5 km) with every boundary and initial condition
of the coastal system, each a stochastic process, linked by a causal graph:

    rain P, temperature T  ->  soil-moisture filter m  ->  recharge r = f_r m       (atmosphere, soil)
                                m  ->  river stage zeta (Robin exchange at x_r)        (river)
                                m  ->  pumping Q = Q_eps + k (-m)   (drought response, the controllable boundary)
    sea level eta = interannual + storm surge + sea-level rise (uncertain rate)        (sea)
    initial state: head, aquitard legacy, toe position                                (initial conditions)
    toe:  dX/dt = (-gamma h(x_c) - X) / tau_X     (landward toe advance, a lagged response to the coastal head)

Head: S_y dh/dt = T h_xx - sum_k s_k a_k (h - h_k) + r - Q delta_w + C_r (zeta - h) delta_r,  dh_k/dt = a_k (h - h_k).
The goal is the toe advance X(H) at horizons H = 1, 5, 20 years. Because every source is independent and the
system is linear, the goal variance splits exactly into source contributions; the causal paths of rain
(recharge, river, pumping) and the pumping policy k are examined by intervention (setting k).
Writes kufiri_results.json and kufiri.log.
"""
import json
import os
import time

import numpy as np
from scipy.linalg import expm

HERE = os.path.dirname(os.path.abspath(__file__))
P = dict(L=5000.0, N=50, T=1000.0 * 365.25, Sy=0.10, rates=[0.01, 0.1, 1.0], cap=[0.04, 0.03, 0.03],
         x_w=1500.0, x_r=3000.0, x_c=500.0, C_r=50.0,
         sig_eta=0.06, tau_eta=1.0, sig_ss=0.25, tau_ss=3 / 365.25, slr_mean=0.004, slr_sd=0.002,
         sig_P=0.20, tau_P=0.5, Ptr_mean=-0.003, Ptr_sd=0.003,
         sig_T=0.6, tau_T=1.0, eT=0.03, Ttr_mean=0.04, Ttr_sd=0.015,
         tau_s=0.25, f_r=0.35, c_zeta=0.8, sig_z=0.2, tau_z=0.1,
         sig_Q=40.0, tau_Q=0.25, k_sq=500.0,
         gamma=1000.0, tau_X=8.0, sd_X0=150.0, sd_h0=0.2, ell_h0=1000.0, sd_leg=0.5,
         dt=0.01, horizons=[1.0, 5.0, 20.0])
SOURCES = ['sea interannual', 'storm surge', 'sea-level-rise rate', 'rain anomaly', 'drying trend',
           'temperature anomaly', 'warming rate', 'river stage noise', 'pumping noise',
           'initial toe', 'initial head', 'aquitard legacy']
GROUP = {'sea interannual': 'sea', 'storm surge': 'sea', 'sea-level-rise rate': 'sea', 'rain anomaly': 'atmosphere',
         'drying trend': 'atmosphere', 'temperature anomaly': 'atmosphere', 'warming rate': 'atmosphere',
         'river stage noise': 'river', 'pumping noise': 'pumping', 'initial toe': 'initial state',
         'initial head': 'initial state', 'aquitard legacy': 'initial state'}


def build(k, P=P, paths=('recharge', 'river', 'pumping')):
    """Augmented linear system dz = (A z + a0) dt + G dW. Returns A, the noise intensities per source, the initial
    covariance per source, the drift (means of the random rates enter through the initial mean) and indices."""
    N, L, T, Sy = P['N'], P['L'], P['T'], P['Sy']
    dx = L / N
    K = len(P['rates'])
    nh = N * (K + 1)
    # forcing states
    names = ['eta', 'ss', 'slr_level', 'slr_rate', 'P', 'Ptr_level', 'Ptr_rate', 'Tq', 'Ttr_level', 'Ttr_rate',
             'm', 'z', 'Qe', 'X']
    idx = {nm: nh + i for i, nm in enumerate(names)}
    n = nh + len(names)
    A = np.zeros((n, n))
    # aquifer
    for i in range(N):
        if i > 0:
            A[i, i - 1] += T / dx ** 2 / Sy; A[i, i] -= T / dx ** 2 / Sy
        if i < N - 1:
            A[i, i + 1] += T / dx ** 2 / Sy; A[i, i] -= T / dx ** 2 / Sy
    A[0, 0] -= 2 * T / dx ** 2 / Sy
    for kk, (a, s) in enumerate(zip(P['rates'], P['cap'])):
        sl = slice(N * (kk + 1), N * (kk + 2))
        A[:N, :N] -= np.eye(N) * s * a / Sy
        A[:N, sl] += np.eye(N) * s * a / Sy
        A[sl, sl] -= np.eye(N) * a
        A[sl, :N] += np.eye(N) * a
    # sea boundary: eta + ss + slr_level enter cell 0 through the half-cell Dirichlet flux
    for nm in ('eta', 'ss', 'slr_level'):
        A[0, idx[nm]] += 2 * T / dx ** 2 / Sy
    A[idx['eta'], idx['eta']] = -1 / P['tau_eta']
    A[idx['ss'], idx['ss']] = -1 / P['tau_ss']
    A[idx['slr_level'], idx['slr_rate']] = 1.0
    # atmosphere -> soil filter m (net infiltration anomaly, low-pass)
    A[idx['P'], idx['P']] = -1 / P['tau_P']
    A[idx['Ptr_level'], idx['Ptr_rate']] = 1.0
    A[idx['Tq'], idx['Tq']] = -1 / P['tau_T']
    A[idx['Ttr_level'], idx['Ttr_rate']] = 1.0
    im = idx['m']
    A[im, im] = -1 / P['tau_s']
    for nm, c in (('P', 1.0), ('Ptr_level', 1.0), ('Tq', -P['eT']), ('Ttr_level', -P['eT'])):
        A[im, idx[nm]] += c / P['tau_s']
    if 'recharge' in paths:
        A[:N, im] += P['f_r'] / Sy
    # river: stage z = c_zeta m (path) + z_eps; Robin exchange at x_r
    ir = int(P['x_r'] // dx)
    A[idx['z'], idx['z']] = -1 / P['tau_z']
    crate = P['C_r'] / (Sy * dx)
    A[ir, ir] -= crate
    A[ir, idx['z']] += crate
    if 'river' in paths:
        A[ir, im] += crate * P['c_zeta']
    # pumping: Q = Q_eps + k (-m), sink at x_w
    iw = int(P['x_w'] // dx)
    A[idx['Qe'], idx['Qe']] = -1 / P['tau_Q']
    A[iw, idx['Qe']] -= 1 / (Sy * dx)
    if 'pumping' in paths:
        A[iw, im] += k / (Sy * dx)
    # toe
    ic = int(P['x_c'] // dx)
    A[idx['X'], idx['X']] = -1 / P['tau_X']
    A[idx['X'], ic] = -P['gamma'] / P['tau_X']
    # sources: (white-noise intensity on a state, initial variance on states)
    def ou(nm, sig, tau):
        return dict(Q={idx[nm]: 2 * sig ** 2 / tau}, P0={idx[nm]: sig ** 2})
    x = (np.arange(N) + 0.5) * dx
    Ch = P['sd_h0'] ** 2 * np.exp(-np.abs(x[:, None] - x[None, :]) / P['ell_h0'])
    Cl = P['sd_leg'] ** 2 * np.exp(-np.abs(x[:, None] - x[None, :]) / P['ell_h0'])
    src = {
        'sea interannual': ou('eta', P['sig_eta'], P['tau_eta']),
        'storm surge': ou('ss', P['sig_ss'], P['tau_ss']),
        'sea-level-rise rate': dict(Q={}, P0={idx['slr_rate']: P['slr_sd'] ** 2}),
        'rain anomaly': ou('P', P['sig_P'], P['tau_P']),
        'drying trend': dict(Q={}, P0={idx['Ptr_rate']: P['Ptr_sd'] ** 2}),
        'temperature anomaly': ou('Tq', P['sig_T'], P['tau_T']),
        'warming rate': dict(Q={}, P0={idx['Ttr_rate']: P['Ttr_sd'] ** 2}),
        'river stage noise': ou('z', P['sig_z'], P['tau_z']),
        'pumping noise': ou('Qe', P['sig_Q'], P['tau_Q']),
        'initial toe': dict(Q={}, P0={idx['X']: P['sd_X0'] ** 2}),
        'initial head': dict(Q={}, P0block=(slice(0, N), Ch)),
        'aquitard legacy': dict(Q={}, P0block=('legacy', Cl)),
    }
    mean0 = np.zeros(n)
    mean0[idx['slr_rate']] = P['slr_mean']; mean0[idx['Ptr_rate']] = P['Ptr_mean']; mean0[idx['Ttr_rate']] = P['Ttr_mean']
    return dict(A=A, src=src, idx=idx, n=n, N=N, K=K, mean0=mean0, x=x)


def source_mats(S, name):
    n, N, K = S['n'], S['N'], S['K']
    d = S['src'][name]
    Q = np.zeros((n, n)); P0 = np.zeros((n, n))
    for i, v in d.get('Q', {}).items():
        Q[i, i] = v
    for i, v in d.get('P0', {}).items():
        P0[i, i] = v
    if 'P0block' in d:
        where, C = d['P0block']
        if where == 'legacy':
            for k1 in range(K):
                for k2 in range(K):
                    P0[N * (k1 + 1):N * (k1 + 2), N * (k2 + 1):N * (k2 + 2)] = C
        else:
            P0[where, where] = C
    return Q, P0


def propagate(S, horizons, dt, sources):
    """Goal variance of the toe at each horizon, per source (exact discretisation, Van Loan)."""
    A, n = S['A'], S['n']
    Phi = expm(A * dt)
    iX = S['idx']['X']
    out = {}
    for name in sources:
        Q, P0 = source_mats(S, name)
        if Q.any():
            Z = np.zeros((2 * n, 2 * n)); Z[:n, :n] = -A; Z[:n, n:] = Q; Z[n:, n:] = A.T
            E = expm(Z * dt); Qd = E[n:, n:].T @ E[:n, n:]; Qd = 0.5 * (Qd + Qd.T)
        else:
            Qd = None
        Pm = P0.copy(); t = 0.0; res = []
        for H in horizons:
            nsteps = int(round((H - t) / dt))
            for _ in range(nsteps):
                Pm = Phi @ Pm @ Phi.T
                if Qd is not None:
                    Pm += Qd
            t = H
            res.append(float(Pm[iX, iX]))
        out[name] = res
    return out


def mean_toe(S, horizons, dt):
    Phi = expm(S['A'] * dt)
    z = S['mean0'].copy(); t = 0.0; res = []
    for H in horizons:
        for _ in range(int(round((H - t) / dt))):
            z = Phi @ z
        t = H; res.append(float(z[S['idx']['X']]))
    return res


def monte_carlo(S, H, dt, nmc=3000, seed=11):
    """Check: simulate all sources together and compare the toe variance at H with the sum of the budget."""
    rng = np.random.default_rng(seed)
    A, n = S['A'], S['n']
    Qtot = np.zeros((n, n)); P0tot = np.zeros((n, n))
    for name in SOURCES:
        Q, P0 = source_mats(S, name); Qtot += Q; P0tot += P0
    Z = np.zeros((2 * n, 2 * n)); Z[:n, :n] = -A; Z[:n, n:] = Qtot; Z[n:, n:] = A.T
    E = expm(Z * dt); Phi = E[n:, n:].T; Qd = Phi @ E[:n, n:]; Qd = 0.5 * (Qd + Qd.T)
    Lq = np.linalg.cholesky(Qd + 1e-14 * np.eye(n) * np.max(np.diag(Qd)))
    w, V = np.linalg.eigh(P0tot); w = np.clip(w, 0, None)
    z = (V * np.sqrt(w)) @ rng.standard_normal((n, nmc))
    for _ in range(int(round(H / dt))):
        z = Phi @ z + Lq @ rng.standard_normal((n, nmc))
    x = z[S['idx']['X']]
    return float(x.var()), float(x.var() * np.sqrt(2 / (nmc - 1)))


def run():
    t0 = time.time()
    H = P['horizons']; dt = P['dt']
    res = dict(P=P, sources=SOURCES, group=GROUP)
    log = []
    # 1. budget under the status-quo policy (pumping rises in drought)
    S = build(P['k_sq'])
    bud = propagate(S, H, dt, SOURCES)
    tot = [sum(bud[s][j] for s in SOURCES) for j in range(len(H))]
    res['budget_sq'] = bud; res['total_sq'] = tot
    res['mean_sq'] = mean_toe(S, H, dt)
    for j, h in enumerate(H):
        groups = {}
        for s in SOURCES:
            groups[GROUP[s]] = groups.get(GROUP[s], 0) + bud[s][j] / tot[j]
        top = sorted(((bud[s][j] / tot[j], s) for s in SOURCES), reverse=True)[:4]
        log.append(f"H={h:4.0f} yr  toe sd={np.sqrt(tot[j]):6.1f} m  mean={res['mean_sq'][j]:7.1f} m  groups: "
                   + ', '.join(f'{g} {100 * v:.1f}%' for g, v in sorted(groups.items(), key=lambda kv: -kv[1]))
                   + '  | top: ' + ', '.join(f'{s} {100 * v:.1f}%' for v, s in top))
    # 2. Monte Carlo check of the 20-year total
    mc, mc_se = monte_carlo(S, H[-1], dt)
    res['mc_check'] = dict(H=H[-1], budget=tot[-1], mc=mc, se=mc_se)
    log.append(f"Monte Carlo check at {H[-1]:.0f} yr: budget var {tot[-1]:.0f} m2, simulated {mc:.0f} +- {mc_se:.0f} m2")
    # 3. causal paths of the atmospheric sources (rain anomaly, drying trend, temperature, warming) under the status quo
    atm = ['rain anomaly', 'drying trend', 'temperature anomaly', 'warming rate']
    paths = {}
    for p in ('recharge', 'river', 'pumping'):
        Sp = build(P['k_sq'], paths=(p,))
        bp = propagate(Sp, H, dt, atm)
        paths[p] = [sum(bp[s][j] for s in atm) for j in range(len(H))]
    allp = [sum(bud[s][j] for s in atm) for j in range(len(H))]
    res['paths'] = dict(single=paths, all=allp)
    for j, h in enumerate(H):
        cross = allp[j] - sum(paths[p][j] for p in paths)
        log.append(f"H={h:4.0f} yr atmosphere var {allp[j]:8.0f} = recharge {paths['recharge'][j]:8.0f} + river "
                   f"{paths['river'][j]:6.0f} + pumping {paths['pumping'][j]:7.0f} + cross {cross:8.0f} (m2)")
    # 4. the pumping policy as an intervention: variance and mean of the toe as functions of k (quadratic in k)
    ks = [-2 * P['k_sq'], -P['k_sq'], 0.0, P['k_sq'], 2 * P['k_sq']]
    pol = {}
    for k in ks:
        Sk = build(k)
        b = propagate(Sk, H, dt, atm + ['pumping noise'])
        other = [sum(bud[s][j] for s in SOURCES if s not in atm + ['pumping noise']) for j in range(len(H))]
        pol[str(k)] = dict(var=[sum(b[s][j] for s in b) + other[j] for j in range(len(H))], mean=mean_toe(Sk, H, dt))
    res['policy'] = pol
    kopt = []
    for j, h in enumerate(H):
        v = np.array([pol[str(k)]['var'][j] for k in ks])
        c2, c1, c0 = np.polyfit(ks, v, 2)
        ko = -c1 / (2 * c2)
        kopt.append(float(ko))
        Sk = build(ko); b = propagate(Sk, [h], dt, atm + ['pumping noise'])
        other = sum(bud[s][j] for s in SOURCES if s not in atm + ['pumping noise'])
        vopt = sum(b[s][0] for s in b) + other
        m_sq, m0, mo = pol[str(P['k_sq'])]['mean'][j], pol['0.0']['mean'][j], mean_toe(Sk, [h], dt)[0]
        log.append(f"H={h:4.0f} yr policy: k_sq={P['k_sq']:.0f} sd {np.sqrt(pol[str(P['k_sq'])]['var'][j]):6.1f} m mean {m_sq:6.1f} | "
                   f"do(k=0) sd {np.sqrt(pol['0.0']['var'][j]):6.1f} mean {m0:6.1f} | k*={ko:7.0f} sd {np.sqrt(vopt):6.1f} mean {mo:6.1f}")
        res.setdefault('kopt', []).append(dict(H=h, k=ko, sd=float(np.sqrt(vopt)), mean=mo))
    # 5. value of reducing each uncertainty (halving the sd of one source) at each horizon
    val = {}
    for s in SOURCES:
        val[s] = [float(0.75 * bud[s][j] / tot[j]) for j in range(len(H))]   # halving an sd removes 3/4 of its variance
    res['value_halving'] = val
    best = [max(SOURCES, key=lambda s: val[s][j]) for j in range(len(H))]
    log.append('largest variance reduction from halving one uncertainty: '
               + ', '.join(f'{h:.0f} yr: {b} ({100 * val[b][j]:.0f}%)' for j, (h, b) in enumerate(zip(H, best))))
    res['runtime_s'] = time.time() - t0
    json.dump(res, open(os.path.join(HERE, 'kufiri_results.json'), 'w'), indent=1)
    txt = '\n'.join(log) + f"\nruntime {res['runtime_s']:.0f} s"
    open(os.path.join(HERE, 'kufiri.log'), 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    run()
