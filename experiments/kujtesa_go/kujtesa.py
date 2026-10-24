"""KUJTESA-GO (kujtesa: memory). Innovation of review 48 (deep reinforcement learning with deep mathematics).

How the slow memory of the clays slows deep value learning, and a physics-informed remedy. Monthly linear closed loop
of a coastal aquifer under a pumping rule, state z = (m, h, X, c):
    m' = 0.7 m + 0.5 w_m                      soil-moisture index (fast)
    h' = 0.85 h + 0.3 m - beta q + 0.1 w_h    coastal head
    X' = 0.9 X - 0.5 h + 0.1 c + 0.1 w_X      landward toe advance
    c' = 0.995 c + 0.02 X + 0.02 w_c          salt stored in the clays (slow memory, about 17 years)
Cost per month X^2 + lam q^2, discount gamma = 0.99.
Proposition U (review 48, section 9): for fitted value iteration (the target-network loop of deep Q-learning and DQN)
with a function class that contains the quadratics, the value error after K target updates has modal components
e_ij(K) = (gamma mu_i mu_j)^K e_ij(0) in the eigenbasis of the closed loop; lambda-returns change the factor to
gamma rho (1 - lam_e) / (1 - gamma lam_e rho); potential-based shaping with a physics value Phi leaves the fixed point
unchanged and replaces e_ij(0) by the error of Phi. Part 1 checks this exactly (linear algebra, also for the
Riccati Q-iteration of the control problem); part 2 trains neural value networks by fitted value iteration with and
without the remedies. Writes kujtesa_results.json and kujtesa.log.
"""
import json
import os
import time

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')          # one thread per process: the workers run in parallel

import numpy as np
from multiprocessing import Pool
from scipy.linalg import solve_discrete_are, solve_discrete_lyapunov

HERE = os.path.dirname(os.path.abspath(__file__))
P = dict(gamma=0.99, lam=0.5, beta=0.3, a_c=0.995, outer=200, steps=200, batch=512, pool=4096, width=64,
         lr=1e-3, traj=60, lam_e=0.9, seeds=5, phys_err=0.002)
NAMES = ['m', 'h', 'X', 'c']


def system(a_c=P['a_c']):
    A = np.array([[0.7, 0, 0, 0], [0.3, 0.85, 0, 0], [0, -0.5, 0.9, 0.1], [0, 0, 0.02, a_c]])
    B = np.array([[0.0], [-P['beta']], [0.0], [0.0]])
    W = np.diag([0.5, 0.1, 0.1, 0.02]) ** 2
    Q = np.diag([0, 0, 1.0, 0])
    R = np.array([[P['lam']]])
    return A, B, W, Q, R


def lqr_discounted(A, B, Q, R, g):
    Pm = solve_discrete_are(np.sqrt(g) * A, np.sqrt(g) * B, Q, R)
    K = g * np.linalg.solve(R + g * B.T @ Pm @ B, B.T @ Pm @ A)
    return K, Pm


def value_matrix(Acl, Qcl, g):
    """V(z) = z^T P z + const for the discounted cost z^T Qcl z under z' = Acl z + w."""
    return solve_discrete_lyapunov(np.sqrt(g) * Acl.T, Qcl)


def modal(Acl):
    """Eigenvalues sorted by modulus (complex pairs kept complex) and right eigenvectors; the error of a quadratic
    form transforms as V^T E V (plain transpose), so that A^T E A becomes Lambda (V^T E V) Lambda."""
    lam, V = np.linalg.eig(Acl)
    o = np.argsort(-np.abs(lam))
    return lam[o], V[:, o]


MODES = ['slow (clay)', 'fast (real 0.70)', 'oscillatory', 'oscillatory*']


def part1(log, res):
    g = P['gamma']
    A, B, W, Q, R = system()
    K, Pric = lqr_discounted(A, B, Q, R, g)
    Acl = A - B @ K
    Qcl = Q + K.T @ R @ K
    Pv = value_matrix(Acl, Qcl, g)
    mu, V = modal(Acl)
    log.append(f'optimal pumping rule K* on (m, h, X, c) = {np.round(K[0], 4)}; closed-loop eigenvalues {np.round(mu, 4)}')
    amu = np.abs(mu)
    # (i) fitted value iteration from P0 = 0: P_{k+1} = Qcl + g Acl^T P_k Acl
    Pk = np.zeros_like(Pv); err = []
    E0 = V.T @ (Pk - Pv) @ V
    for k in range(400):
        Pk = Qcl + g * Acl.T @ Pk @ Acl
        Ek = V.T @ (Pk - Pv) @ V
        err.append(Ek)
    err = np.array(err)
    ratio_pred = np.array([[g * mu[i] * mu[j] for j in range(4)] for i in range(4)])
    ratio_meas = err[4] / err[3]
    dev = float(np.max(np.abs(ratio_meas - ratio_pred)))
    log.append(f'modal contraction of fitted value iteration: max |measured - g mu_i mu_j| over all mode pairs = {dev:.2e}')
    rel = np.abs(err) / np.abs(E0)[None]
    k_to = lambda i, j, eps: int(np.argmax(rel[:, i, j] < eps)) + 1
    res['fvi'] = dict(mu_abs=amu.tolist(), mu_re=np.real(mu).tolist(), mu_im=np.imag(mu).tolist(),
                      factor_abs=np.abs(ratio_pred).tolist(), max_ratio_dev=dev,
                      iters_to_1pct={f'{MODES[i]} x {MODES[j]}': k_to(i, j, 0.01) for i in range(4) for j in range(i, 4)},
                      rel_err_slow=rel[:, 0, 0][:300].tolist(), rel_err_fast=rel[:, 3, 3][:300].tolist(),
                      rel_err_mixed=rel[:, 0, 1][:300].tolist())
    res['fvi']['pred_iters_slow'] = float(np.log(100) / -np.log(g * amu[0] ** 2))
    res['fvi']['iters_slow'] = k_to(0, 0, 0.01); res['fvi']['iters_fast'] = k_to(3, 3, 0.01); res['fvi']['iters_mixed'] = k_to(0, 1, 0.01)
    log.append(f'updates to reach 1% error: slow x slow mode {res["fvi"]["iters_slow"]} (predicted {res["fvi"]["pred_iters_slow"]:.0f}); '
               f'slow x fast {res["fvi"]["iters_mixed"]}; fastest pair {res["fvi"]["iters_fast"]}')
    # (ii) lambda-return operator: factor g rho (1 - le) / (1 - g le rho)
    lam_e = P['lam_e']
    rho = amu[0] ** 2
    res['fvi']['lambda_factor_slow'] = float(g * rho * (1 - lam_e) / (1 - g * lam_e * rho))
    res['fvi']['lambda_iters_slow'] = float(np.log(100) / -np.log(res['fvi']['lambda_factor_slow']))
    # (iii) Riccati Q-iteration for the control problem: how fast the pumping gain on each state is learned
    Pk = np.zeros_like(Pric); gains = []
    for k in range(600):
        Kk = g * np.linalg.solve(R + g * B.T @ Pk @ B, B.T @ Pk @ A)
        gains.append(Kk[0].copy())
        Pk = Q + g * A.T @ Pk @ A - g ** 2 * A.T @ Pk @ B @ np.linalg.solve(R + g * B.T @ Pk @ B, B.T @ Pk @ A)
    gains = np.array(gains)
    rg = np.abs(gains - K[0][None]) / np.abs(K[0][None])
    it_gain = {NAMES[i]: int(np.argmax(rg[:, i] < 0.01)) for i in range(4)}
    tail = rg[401:451, 3] / rg[400:450, 3]
    res['riccati'] = dict(K=K[0].tolist(), iters_gain_1pct=it_gain, rel_gain_err=rg[:400].tolist(),
                          tail_ratio_c=float(np.median(tail)), pred_ratio=float(g * amu[0] ** 2), pred_ratio_single=float(g * amu[0]))
    log.append(f'Q-iteration of the control problem: iterations until the pumping gain is within 1%: ' +
               ', '.join(f'{k} {v}' for k, v in it_gain.items()) +
               f'; tail contraction of the gain on c {np.median(tail):.4f} (g mu_slow = {g * amu[0]:.4f}, g mu_slow^2 = {g * amu[0] ** 2:.4f})')
    # (iv) shaping with a physics value computed from a model whose clay memory is slightly wrong
    A2 = A.copy(); A2[3, 3] = P['a_c'] - P['phys_err']
    Pphi = value_matrix(A2 - B @ K, Qcl, g)
    Eshape = V.T @ (Pphi - Pv) @ V
    res['shaping'] = dict(a_c_model=float(A2[3, 3]), rel_init_err_slow=float(abs(Eshape[0, 0]) / abs(E0[0, 0])),
                          saved_iters=float(np.log(abs(E0[0, 0]) / abs(Eshape[0, 0])) / -np.log(g * amu[0] ** 2)))
    # (v) exact curves of the relative error of P_cc (value per unit of stored clay salt squared) for the three methods
    from scipy.linalg import solve_discrete_lyapunov as dlyap
    lam_e = P['lam_e']
    def T_lambda(Pm):
        Sx = dlyap(np.sqrt(g * lam_e) * Acl.T, Pm)          # S = P + g lam A^T S A
        C0 = dlyap(np.sqrt(g * lam_e) * Acl.T, Qcl)
        return C0 + g * (1 - lam_e) * Acl.T @ Sx @ Acl
    curves = {}
    for name, P0, op in [('FVI', np.zeros_like(Pv), lambda M: Qcl + g * Acl.T @ M @ Acl),
                         ('FVI, lambda-returns', np.zeros_like(Pv), T_lambda),
                         ('FVI, physics shaping', Pphi.copy(), lambda M: Qcl + g * Acl.T @ M @ Acl)]:
        M = P0.copy(); c = []
        for k in range(P['outer']):
            M = op(M); c.append(abs(M[3, 3] - Pv[3, 3]) / abs(Pv[3, 3]))
        curves[name] = c
    res['exact_pcc'] = curves
    res['exact_pcc_k10'] = {k: int(np.argmax(np.array(v) < 0.1)) + 1 for k, v in curves.items()}
    res['P_cc'] = float(Pv[3, 3]); res['phys_init_pcc'] = float(abs(Pphi[3, 3] - Pv[3, 3]) / abs(Pv[3, 3]))
    log.append('exact relative error of P_cc after 25/50/100 updates: ' + '; '.join(
        f'{k} {v[24]:.3f}/{v[49]:.3f}/{v[99]:.3f} (below 10% at {res["exact_pcc_k10"][k]})' for k, v in curves.items()))
    log.append(f'physics potential from a model with clay memory {A2[3, 3]:.3f} instead of {P["a_c"]}: initial slow-mode error '
               f'{100 * res["shaping"]["rel_init_err_slow"]:.1f}% of the unshaped one; saves {res["shaping"]["saved_iters"]:.0f} updates')
    return A, B, W, Q, R, K, Acl, Qcl, Pv, mu, V, Pphi


# ------------------------------------------------------------------ neural fitted value iteration (numpy MLP)
class MLP:
    def __init__(self, din, width, rng):
        self.W1 = rng.standard_normal((din, width)) / np.sqrt(din); self.b1 = np.zeros(width)
        self.W2 = rng.standard_normal((width, width)) / np.sqrt(width); self.b2 = np.zeros(width)
        self.W3 = rng.standard_normal((width, 1)) / np.sqrt(width); self.b3 = np.zeros(1)
        self.params = ['W1', 'b1', 'W2', 'b2', 'W3', 'b3']
        self.m = {k: 0 * getattr(self, k) for k in self.params}; self.v = {k: 0 * getattr(self, k) for k in self.params}; self.t = 0

    def copy(self):
        o = object.__new__(MLP); o.params = self.params
        for k in self.params:
            setattr(o, k, getattr(self, k).copy())
        return o

    def __call__(self, x):
        a1 = np.tanh(x @ self.W1 + self.b1); a2 = np.tanh(a1 @ self.W2 + self.b2)
        return (a2 @ self.W3 + self.b3)[:, 0]

    def step(self, x, y, lr):
        a1 = np.tanh(x @ self.W1 + self.b1); a2 = np.tanh(a1 @ self.W2 + self.b2)
        out = (a2 @ self.W3 + self.b3)[:, 0]
        r = (out - y)[:, None] / len(y)
        gW3 = a2.T @ r; gb3 = r.sum(0)
        d2 = (r @ self.W3.T) * (1 - a2 ** 2); gW2 = a1.T @ d2; gb2 = d2.sum(0)
        d1 = (d2 @ self.W2.T) * (1 - a1 ** 2); gW1 = x.T @ d1; gb1 = d1.sum(0)
        self.t += 1
        for k, gk in zip(self.params, [gW1, gb1, gW2, gb2, gW3, gb3]):
            self.m[k] = 0.9 * self.m[k] + 0.1 * gk; self.v[k] = 0.999 * self.v[k] + 0.001 * gk ** 2
            mh = self.m[k] / (1 - 0.9 ** self.t); vh = self.v[k] / (1 - 0.999 ** self.t)
            setattr(self, k, getattr(self, k) - lr * mh / (np.sqrt(vh) + 1e-8))
        return float(np.mean((out - y) ** 2))


def quad_features(z):
    i, j = np.triu_indices(z.shape[1])
    return np.hstack([z[:, i] * z[:, j], np.ones((len(z), 1))])


def fitted_P(net, Zs, sc, vs, nz):
    """Least-squares quadratic fit of the network's value on test states, returned as a symmetric matrix."""
    v = net(Zs / sc) * vs
    F = quad_features(Zs)
    coef = np.linalg.lstsq(F, v, rcond=None)[0]
    Pm = np.zeros((nz, nz)); i, j = np.triu_indices(nz)
    for c, a, b in zip(coef[:-1], i, j):
        if a == b:
            Pm[a, a] = c
        else:
            Pm[a, b] = Pm[b, a] = c / 2
    return Pm


def _neural_task(args):
    """One neural fitted-value-iteration run (method, seed) on the noise-free closed loop."""
    method, seed, sysm = args
    A, B, W, Q, R, K, Acl, Qcl, Pv, mu, V, Pphi = sysm
    g = P['gamma']
    sig = 1.0 / np.sqrt(np.diag(Pv))          # each coordinate contributes equally to the value
    vs = float(np.trace(Pv * np.outer(sig, sig)))
    cost = lambda Z: np.einsum('ij,jk,ik->i', Z, Qcl, Z)
    phi = lambda Z: np.einsum('ij,jk,ik->i', Z, Pphi, Z)
    Zt = np.random.default_rng(99).standard_normal((20000, 4)) * sig
    E0 = np.real(V.T @ (np.zeros((4, 4)) - Pv) @ V)[0, 0]
    rng = np.random.default_rng(seed)
    net = MLP(4, P['width'], rng)
    net.W3 *= 0.0                              # start from zero output: the initial error is the whole value
    tgt = net.copy()
    pcc, tot, slow = [], [], []
    for k in range(P['outer']):
        Z = rng.standard_normal((P['pool'], 4)) * sig
        if method == 'FVI, lambda-returns':
            traj = [Z]
            for _ in range(P['traj']):
                traj.append(traj[-1] @ Acl.T)
            Vb = [tgt(t / sig) * vs for t in traj]
            G_ = Vb[-1]
            for t in range(P['traj'] - 1, -1, -1):
                G_ = cost(traj[t]) + g * ((1 - P['lam_e']) * Vb[t + 1] + P['lam_e'] * G_)
            y = G_
        else:
            Z1 = Z @ Acl.T                     # expected next state: the noise only adds a constant to the value
            if method == 'FVI, physics shaping':  # learn the residual V - Phi from the shaped cost
                y = cost(Z) + g * phi(Z1) - phi(Z) + g * tgt(Z1 / sig) * vs
            else:
                y = cost(Z) + g * tgt(Z1 / sig) * vs
        for s in range(P['steps']):
            idx = rng.integers(0, P['pool'], P['batch'])
            net.step(Z[idx] / sig, y[idx] / vs, P['lr'])
        tgt = net.copy()
        Pn = fitted_P(net, Zt, sig, vs, 4)
        if method == 'FVI, physics shaping':
            Pn = Pn + Pphi
        pcc.append(float(abs(Pn[3, 3] - Pv[3, 3]) / abs(Pv[3, 3])))
        tot.append(float(np.linalg.norm(Pn - Pv) / np.linalg.norm(Pv)))
        slow.append(float(np.real(V.T @ (Pn - Pv) @ V)[0, 0] / abs(E0)))
    return method, seed, pcc, tot, slow


def part2(log, res, sysm):
    """Neural fitted value iteration with a target network. The regression states are drawn independently with
    standard deviation 1/sqrt(P_ii), so that every coordinate contributes equally to the value: with the stationary
    spread the clay term is a few per cent of the value, below the accuracy of the network (first version of this
    experiment, see the README). Targets use the expected next state."""
    g = P['gamma']
    mu = sysm[9]
    f_slow = g * abs(mu[0]) ** 2
    f_lam = g * abs(mu[0]) ** 2 * (1 - P['lam_e']) / (1 - g * P['lam_e'] * abs(mu[0]) ** 2)
    methods = ['FVI', 'FVI, lambda-returns', 'FVI, physics shaping']
    tasks = [(m, s, sysm) for m in methods for s in range(P['seeds'])]
    with Pool(4) as pool:
        outs = pool.map(_neural_task, tasks)
    out = {}
    h = P['outer'] // 2
    for m in methods:
        rows = [o for o in outs if o[0] == m]
        pcc = np.array([r[2] for r in rows]); tot = np.array([r[3] for r in rows]); slow = np.array([r[4] for r in rows])
        f = f_lam if m == 'FVI, lambda-returns' else f_slow
        # residual of the modal recursion e(k+1) = f e(k) + r(k): the per-update regression error in the slow mode
        resid = slow[:, 1:] - f * slow[:, :-1]
        sd_r = float(np.median(np.std(resid[:, h:], axis=1)))
        sd_e = float(np.median(np.std(slow[:, h:], axis=1)))
        med = np.median(pcc, 0)
        k10 = int(np.argmax(med < 0.1)) + 1 if np.any(med < 0.1) else None
        out[m] = dict(pcc_median=med.tolist(), pcc_all=pcc.tolist(), total_median=np.median(tot, 0).tolist(),
                      slow_all=slow.tolist(), k_to_10pct=k10, mean_pcc_second_half=float(np.mean(pcc[:, h:])),
                      p90_pcc_second_half=float(np.quantile(pcc[:, h:], 0.9)),
                      final_total=float(np.median(tot[:, -1])), factor=float(f), sd_resid=sd_r, sd_slow=sd_e,
                      amplification_measured=float(sd_e / sd_r), amplification_white=float(1 / np.sqrt(1 - f ** 2)),
                      amplification_worst=float(1 / (1 - f)))
        log.append(f'neural {m:22s}: P_cc error (median of {P["seeds"]} seeds) after 25/50/100/{P["outer"]} updates '
                   f'{med[24]:.3f}/{med[49]:.3f}/{med[99]:.3f}/{med[-1]:.3f}; first below 10% at {k10}; mean in the '
                   f'second half {out[m]["mean_pcc_second_half"]:.3f} (90th pct {out[m]["p90_pcc_second_half"]:.3f}); '
                   f'total error at the end {out[m]["final_total"]:.4f}; slow-mode noise: sd of residual {sd_r:.4f}, '
                   f'sd of error {sd_e:.4f}, ratio {sd_e / sd_r:.2f} (white-noise prediction {1 / np.sqrt(1 - f ** 2):.2f}, '
                   f'worst case {1 / (1 - f):.1f})')
    res['neural'] = out


def run():
    t0 = time.time()
    log, res = [], dict(P=P)
    sysm = part1(log, res)
    part2(log, res, sysm)
    res['runtime_s'] = time.time() - t0
    json.dump(res, open(os.path.join(HERE, 'kujtesa_results.json'), 'w'), indent=1)
    txt = '\n'.join(log) + f"\nruntime {res['runtime_s']:.0f} s"
    open(os.path.join(HERE, 'kujtesa.log'), 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    run()
