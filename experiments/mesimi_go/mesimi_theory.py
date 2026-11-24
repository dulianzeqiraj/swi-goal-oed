"""MESIMI-GO, part 2: the closed-form log T constant of Proposition M and the tail excess cost of each learner.
Predicted regret of certainty equivalence for the drought-aware rule:
    R(T) ~ (1/2) tr(H Sigma_theta) (ln T + gamma),  Sigma_theta = s_h^2 Sigma_x^{-1},
where H is the Hessian of the true average cost J(K(theta_hat)) in the estimated head-row parameters
theta = (a_h, b_r, beta) at the truth and Sigma_x the stationary covariance of the regressors (h, r, q) under K*.
Writes mesimi_theory.json and mesimi_theory.log."""
import json
import os

import numpy as np
from scipy.linalg import solve_discrete_lyapunov

from mesimi import P, mats, lqr_full, avg_cost

HERE = os.path.dirname(os.path.abspath(__file__))
A, B, W, Q, R = mats(P['beta'])
th0 = np.array([P['a_h'], P['b_r'], P['beta']])


def J_of(th):
    Ab, Bb, _, Qb, Rb = mats(th[2]); Ab[2, 2] = th[0]; Ab[2, 1] = th[1]
    return avg_cost(A, B, W, Q, R, lqr_full(Ab, Bb, Qb, Rb))


h = 1e-3
H = np.zeros((3, 3))
for i in range(3):
    for j in range(3):
        e_i = np.eye(3)[i] * h; e_j = np.eye(3)[j] * h
        H[i, j] = (J_of(th0 + e_i + e_j) - J_of(th0 + e_i - e_j) - J_of(th0 - e_i + e_j) + J_of(th0 - e_i - e_j)) / (4 * h * h)
K = lqr_full(A, B, Q, R)
S = solve_discrete_lyapunov(A - B @ K, W)
C = np.vstack([[0, 0, 1, 0], [0, 1, 0, 0], K[0]])        # regressors (h, r, -q) with -q = K z
Sx = C @ S @ C.T
Sig = P['s_h'] ** 2 * np.linalg.inv(Sx)
c = 0.5 * np.trace(H @ Sig)
res = json.load(open(os.path.join(HERE, 'mesimi_results.json')))
T = P['T']
pred = c * (np.log(T) + 0.5772)
pred_from_warm = c * (np.log(T) - np.log(P['warm']))
out = dict(hessian=H.tolist(), Sigma_x=Sx.tolist(), constant=float(c), predicted_T=float(pred), predicted_from_warm=float(pred_from_warm))
log = [f'Hessian eigenvalues {np.round(np.linalg.eigvalsh(H), 3)}; per-step constant (1/2) tr(H Sigma) = {c:.4f}',
       f'predicted regret of the drought-aware learner at T={T}: {pred:.2f} (from t=1), {pred_from_warm:.2f} (from the warm-up), measured {res["full, no exploration"]["final"]:.2f} +- {res["full, no exploration"]["final_se"]:.2f}']
for name in ('full, no exploration', 'head-only, no exploration', 'head-only, exploration t^-1/4'):
    g = np.array(res[name]['grid']); r = np.array(res[name]['regret'])
    tail = float((r[-1] - r[-4]) / (g[-1] - g[-4]))
    out[name + ' tail excess per month'] = tail
    log.append(f'{name:32s} excess cost per month over the last {g[-1] - g[-4]} months: {tail:.4f}')
g = np.array(res['full, no exploration']['grid']); Rf = np.array(res['full, no exploration']['regret'])
inc = []
for T0 in (100, 300, 1000, 3000, 10000):
    i = int(np.argmin(np.abs(g - T0)))
    inc.append(dict(T0=int(g[i]), measured=float(Rf[-1] - Rf[i]), predicted=float(c * np.log(g[-1] / g[i]))))
    log.append(f'regret increment from T0={g[i]} to T={g[-1]}: measured {Rf[-1] - Rf[i]:.2f}, predicted c ln(T/T0) = {c * np.log(g[-1] / g[i]):.2f}')
out['increments'] = inc
out['burn_in_100'] = float(Rf[int(np.argmin(np.abs(g - 100)))])
json.dump(out, open(os.path.join(HERE, 'mesimi_theory.json'), 'w'), indent=1)
open(os.path.join(HERE, 'mesimi_theory.log'), 'w').write('\n'.join(log) + '\n')
print('\n'.join(log))
