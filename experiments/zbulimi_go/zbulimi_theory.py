"""ZBULIMI-GO, part 2: theory checks that need no simulation.
1. The rank-one structure of the optimal multi-well rule and the identity tr(M Se) for the cost of exploration.
2. The self-confirming set {beta_hat : beta_hat^T R-weighted ... }: excess cost per month of the CE rule at its points.
3. The sqrt(T) constants of isotropic and head-neutral goal-oriented exploration as the response of the head to
   pumping is scaled (beta -> s beta), and for two and four well fields.
Writes zbulimi_theory.json and zbulimi_theory.log."""
import json
import os

import numpy as np

import zbulimi as Z

HERE = os.path.dirname(os.path.abspath(__file__))
P0 = dict(Z.P)
log, res = [], {}

# 1. rank one and the exploration-cost identity
th = Z.theta_true()
A, B, W, Q, R = Z.mats(th)
K, Pm = Z.lqr(A, B, Q, R)
J0 = Z.avg_cost(A, B, W, Q, R, K)
D = Z.design(th)
rng = np.random.default_rng(1)
errs = []
for _ in range(20):
    L = rng.standard_normal((3, 3)) * 0.1
    Se = L @ L.T
    errs.append(abs((Z.avg_cost(A, B, W, Q, R, K, Se) - J0) - np.trace(D['M'] @ Se)) / np.trace(D['M'] @ Se))
res['rank_one_sv'] = np.linalg.svd(K, compute_uv=False).tolist()
res['identity_max_rel_err'] = float(max(errs))
log.append(f'singular values of K*: {np.round(res["rank_one_sv"], 8)}; exploration-cost identity tr(M Se), max relative error over 20 random Se: {res["identity_max_rel_err"]:.1e}')

# 2. the self-confirming set (a_h, b_r at truth): beta_hat such that the data under its own CE rule look like the truth
b = np.array(P0['beta'])
ex = []
for _ in range(4000):
    u = rng.standard_normal(3); u /= np.linalg.norm(u)
    bh = b / 2 + np.linalg.norm(b) / 2 * u                       # sphere with diameter [0, beta] (case R = lam I)
    if np.any(bh < 0.01):
        continue
    t2 = th.copy(); t2[2:] = bh
    A2, B2, _, _, _ = Z.mats(t2)
    K2, _ = Z.lqr(A2, B2, Q, R)
    # the played direction d2 ~ R^-1 bh; data identify beta^T d2: confirm only if beta^T d2 = bh^T d2
    d2 = np.linalg.svd(K2)[0][:, 0]
    if abs(b @ d2 - bh @ d2) > 1e-3 * abs(bh @ d2):
        # project onto the confirming set for general R: scale bh so that bh^T d2 = beta^T d2
        bh = bh * (b @ d2) / (bh @ d2)
        t2[2:] = bh; A2, B2, _, _, _ = Z.mats(t2); K2, _ = Z.lqr(A2, B2, Q, R)
        d2 = np.linalg.svd(K2)[0][:, 0]
        if abs(b @ d2 - bh @ d2) > 1e-2 * abs(bh @ d2) or np.any(bh < 0.01):
            continue
    ex.append(Z.avg_cost(A, B, W, Q, R, K2) - J0)
ex = np.array(ex)
res['self_confirming'] = dict(n=int(len(ex)), median=float(np.median(ex)), p90=float(np.quantile(ex, 0.9)), max=float(ex.max()), J_opt=J0)
log.append(f'self-confirming points found: {len(ex)}; excess cost per month median {np.median(ex):.4f}, 90th percentile {np.quantile(ex, 0.9):.4f}, max {ex.max():.4f} (J* = {J0:.4f})')

# 3. sensitivity of the constants
sens = []
for s in [0.5, 1.0, 1.5, 2.0, 3.0]:
    Pm_ = dict(P0); Pm_['beta'] = list(s * np.array(P0['beta']))
    thx = np.array([Pm_['a_h'], Pm_['b_r']] + Pm_['beta'])
    Dx = Z.design(thx, Pm_)
    sens.append(dict(scale=s, c_go=Dx['c_go'], c_iso=Dx['c_iso'], ratio=Dx['c_iso'] / Dx['c_go'],
                     cost_ratio=(Dx['c_iso'] / Dx['c_go']) ** 2))
    log.append(f'beta x {s:3.1f}: constants head-neutral {Dx["c_go"]:.3f}, isotropic {Dx["c_iso"]:.3f}, ratio {Dx["c_iso"] / Dx["c_go"]:.3f}')
res['sensitivity'] = sens
wells = []
for bet, lam in [([0.25, 0.05], [0.3, 0.8]), ([0.25, 0.15, 0.05], [0.3, 0.5, 0.8]), ([0.25, 0.15, 0.10, 0.05], [0.3, 0.5, 0.6, 0.8])]:
    Pm_ = dict(P0); Pm_['beta'] = bet; Pm_['lam'] = lam
    thx = np.array([Pm_['a_h'], Pm_['b_r']] + bet)
    Dx = Z.design(thx, Pm_)
    wells.append(dict(p=len(bet), c_go=Dx['c_go'], c_iso=Dx['c_iso'], ratio=Dx['c_iso'] / Dx['c_go']))
    log.append(f'{len(bet)} well fields: constants head-neutral {Dx["c_go"]:.3f}, isotropic {Dx["c_iso"]:.3f}, ratio {Dx["c_iso"] / Dx["c_go"]:.3f}')
res['wells'] = wells
json.dump(res, open(os.path.join(HERE, 'zbulimi_theory.json'), 'w'), indent=1)
open(os.path.join(HERE, 'zbulimi_theory.log'), 'w').write('\n'.join(log) + '\n')
print('\n'.join(log))
