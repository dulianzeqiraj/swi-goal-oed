"""ZBULIMI-GO, part 3: why the learner without exploration pays early. In the blind directions of the multi-well
problem the least-squares estimate is ill-conditioned; this script follows the non-exploring certainty-equivalent
learner over its first 400 months (80 runs, same noise as the main run) and records, at each update, the share of
runs whose raw estimate of the responses leaves the admissible range [0.01, 1] and the excess average cost of the rule
it then plays. Writes zbulimi_early.json and zbulimi_early.log."""
import json
import os

import numpy as np

import zbulimi as Z

HERE = os.path.dirname(os.path.abspath(__file__))
P = Z.P
S, T = 80, 400
th0 = Z.theta_true()
A, B, W, Q, R = Z.mats(th0)
Kopt, _ = Z.lqr(A, B, Q, R)
J0 = Z.avg_cost(A, B, W, Q, R, Kopt)
rng = np.random.default_rng(2026)
noise = rng.standard_normal((T, 4, S))
z = np.zeros((4, S))
G = np.tile(P['ridge'] * np.eye(5)[:, :, None], (1, 1, S))
bv = np.zeros((5, S))
thh = np.tile(np.array([P['a_h'], P['b_r']] + P['beta0'])[:, None], (1, S))
K = np.zeros((S, 3, 4))
for s in range(S):
    K[s] = Z.lqr(*Z.mats(thh[:, s])[:2], Q, R)[0]
rows, log = [], []
for t in range(T):
    q = -np.einsum('sij,js->is', K, z)
    m, r, h, X = z
    zn = np.empty_like(z)
    zn[0] = P['a_m'] * m + P['s_m'] * noise[t, 0]
    zn[1] = P['a_r'] * r + (1 - P['a_r']) * m
    zn[2] = P['a_h'] * h + P['b_r'] * r - np.array(P['beta']) @ q + P['s_h'] * noise[t, 2]
    zn[3] = P['a_X'] * X - P['g'] * h + P['s_X'] * noise[t, 3]
    x = np.vstack([h, r, -q])
    G += np.einsum('is,js->ijs', x, x); bv += x * zn[2]
    if (t + 1) % P['update'] == 0:
        raw = np.linalg.solve(np.moveaxis(G, 2, 0), np.moveaxis(bv, 1, 0)[..., None])[..., 0].T
        out = float(np.mean(np.any((raw[2:] < 0.01) | (raw[2:] > 1.0), 0)))
        cond = float(np.median([np.linalg.cond(G[:, :, s]) for s in range(S)]))
        th = raw.copy(); th[0] = np.clip(th[0], 0, 0.99); th[2:] = np.clip(th[2:], 0.01, 1.0); thh[:] = th
        Js = []
        for s in range(S):
            K[s] = Z.lqr(*Z.mats(thh[:, s])[:2], Q, R)[0]
            Js.append(Z.avg_cost(A, B, W, Q, R, K[s]) - J0)
        Js = np.array(Js)
        rows.append(dict(month=t + 1, share_out_of_range=out, median_excess=float(np.median(Js)), mean_excess=float(np.mean(Js)), median_condition=cond))
        log.append(f'month {t + 1:3d}: raw estimate out of range in {100 * out:3.0f}% of runs; excess cost of the rule median {np.median(Js):.3f}, mean {np.mean(Js):.3f}; median condition number of the information {cond:.1e}')
    z = zn
json.dump(dict(J_opt=J0, rows=rows), open(os.path.join(HERE, 'zbulimi_early.json'), 'w'), indent=1)
open(os.path.join(HERE, 'zbulimi_early.log'), 'w').write('\n'.join(log) + '\n')
print('\n'.join(log))
