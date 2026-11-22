"""KUFIRI-GO, part 2: pumping regimes as a controllable boundary, simulated by Monte Carlo.
(a) the linear drought rule Q = k(-(m + e)) with a noisy soil-moisture index (e: sensing error, Ornstein-Uhlenbeck);
(b) three discrete regimes chosen each month from the soil-moisture index: restricted / normal / emergency,
    under a status-quo rule (emergency pumping in drought) and an adaptive rule (restricted pumping in drought),
    against constant pumping. The aquifer and all other sources are those of kufiri.py.
Writes kufiri_regimes.json and kufiri_regimes.log."""
import json
import os
import time

import numpy as np
from scipy.linalg import expm

from kufiri import P, SOURCES, build, source_mats

HERE = os.path.dirname(os.path.abspath(__file__))
t0 = time.time()
rng = np.random.default_rng(23)
dt, H = P['dt'], 20.0
nsteps = int(round(H / dt))
nmc = 4000
S = build(0.0)                                   # pumping path switched off in A: the rule is applied explicitly
A, n, idx, N = S['A'], S['n'], S['idx'], S['N']
dx = P['L'] / N
iw, im, iX = int(P['x_w'] // dx), idx['m'], idx['X']
Qtot = np.zeros((n, n)); P0tot = np.zeros((n, n))
for name in SOURCES:
    Q, P0 = source_mats(S, name); Qtot += Q; P0tot += P0
Z = np.zeros((2 * n, 2 * n)); Z[:n, :n] = -A; Z[:n, n:] = Qtot; Z[n:, n:] = A.T
E = expm(Z * dt); Phi = E[n:, n:].T; Qd = Phi @ E[:n, n:]; Qd = 0.5 * (Qd + Qd.T)
Lq = np.linalg.cholesky(Qd + 1e-14 * np.eye(n) * np.max(np.diag(Qd)))
# exact response of the state to a pumping anomaly held constant over one step (sink at the well cell)
bq = np.zeros(n); bq[iw] = -1.0 / (P['Sy'] * dx)
Aaug = np.zeros((n + 1, n + 1)); Aaug[:n, :n] = A; Aaug[:n, n] = bq
Gq = expm(Aaug * dt)[:n, n]
w, V = np.linalg.eigh(P0tot); w = np.clip(w, 0, None)
z0 = (V * np.sqrt(w)) @ rng.standard_normal((n, nmc)) + S['mean0'][:, None]
noise = [rng.standard_normal((n, nmc)) for _ in range(0)]  # streams drawn on the fly with a fixed seed per scenario
sd_m = float(np.sqrt(np.linalg.solve(np.eye(1), [[0]])[0][0])) if False else None


def simulate(rule, seed=5, sig_e=0.0, tau_e=0.05):
    r = np.random.default_rng(seed)
    z = z0.copy()
    e = sig_e * r.standard_normal(nmc)
    ae = np.exp(-dt / tau_e)
    Qhist = np.zeros(nmc)
    for step in range(nsteps):
        e = ae * e + sig_e * np.sqrt(1 - ae ** 2) * r.standard_normal(nmc)
        q = rule(z[im] + e, step * dt)
        z = Phi @ z + Lq @ r.standard_normal((n, nmc)) + np.outer(Gq, q)
        Qhist += q * dt
    x = z[iX]
    return dict(sd=float(x.std()), mean=float(x.mean()), p95=float(np.percentile(x, 95)),
                pumped=float(Qhist.mean() / H))


# spread of the soil-moisture index under the stationary forcing (from a long run without pumping feedback)
mtrace = simulate(lambda m, t: 0 * m)  # warm-up check of the machinery
res, log = {}, []
z = z0.copy(); r = np.random.default_rng(1); ms = []
for step in range(500):
    z = Phi @ z + Lq @ r.standard_normal((n, nmc)); ms.append(z[im].std())
sdm = float(np.mean(ms[-100:]))
thr = 0.5 * sdm
res['sd_m'] = sdm
log.append(f'soil-moisture index sd {sdm:.3f} m/yr; regime threshold +-{thr:.3f} m/yr')
kopt = -1482.0
rules = {
    'constant pumping': lambda m, t: 0 * m,
    'linear status quo (k=+500)': lambda m, t: 500.0 * (-m),
    'linear optimal (k*=-1482)': lambda m, t: kopt * (-m),
    'regimes, status quo (emergency +150 in drought)': lambda m, t: np.where(m < -thr, 150.0, 0.0),
    'regimes, adaptive (restricted -150 in drought)': lambda m, t: np.where(m < -thr, -150.0, 0.0),
    'regimes, adaptive both ways (-150 drought, +100 wet)': lambda m, t: np.where(m < -thr, -150.0, np.where(m > thr, 100.0, 0.0)),
}
for name, rule in rules.items():
    o = simulate(rule)
    res[name] = o
    log.append(f'{name:52s} toe sd {o["sd"]:6.1f} m  mean {o["mean"]:6.1f} m  95th pct {o["p95"]:6.1f} m  mean pumping anomaly {o["pumped"]:7.1f} m2/yr')
for se in (0.0, 0.05, 0.10, 0.20):
    o = simulate(lambda m, t: kopt * (-m), sig_e=se)
    res[f'optimal rule, sensing error {se}'] = o
    log.append(f'linear optimal rule, soil-moisture sensing error sd {se:.2f} m/yr ({100 * se / sdm:4.0f}% of index sd): toe sd {o["sd"]:6.1f} m  mean {o["mean"]:6.1f} m')
res['runtime_s'] = time.time() - t0
json.dump(res, open(os.path.join(HERE, 'kufiri_regimes.json'), 'w'), indent=1)
open(os.path.join(HERE, 'kufiri_regimes.log'), 'w').write('\n'.join(log) + f"\nruntime {res['runtime_s']:.0f} s\n")
print('\n'.join(log)); print(f"runtime {res['runtime_s']:.0f} s")
