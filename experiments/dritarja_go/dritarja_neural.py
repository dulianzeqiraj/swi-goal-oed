"""DRITARJA-GO, part B: neural pumping policies trained through a differentiable simulator (analytic policy gradient,
backpropagation through time) for each kind of memory window, compared with the exact optimum of part A.

Policies are tanh networks with two hidden layers of WIDTH units. Inputs: the last w observations (head, sentinel
chloride), and for ARX windows also the last k pumping rates; all scaled by their stationary standard deviations.
Training: rollouts of T months from states and histories drawn from a long stationary run of the optimal LQG
controller; loss = mean cost over the rollout; Adam with a decaying step and Polyak averaging of the weights over
the second half of training. Evaluation: paired simulation against the optimal controller with
common random numbers (the excess cost has a much smaller standard error than the cost itself).
Writes dritarja_neural.json and dritarja_neural.log.
"""
import json
import os
import time

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import autograd.numpy as anp
import numpy as np
from autograd import grad
from multiprocessing import Pool

import dritarja as d

HERE = os.path.dirname(os.path.abspath(__file__))
P = dict(width=32, T=120, batch=512, iters=2000, lr=3e-3, seeds=2, eval_batch=256, eval_T=3000, hist=40, avg_from=1000)
CONFIGS = [('obs', 1), ('obs', 2), ('obs', 4), ('obs', 8), ('obs', 16), ('obs', 32), ('arx', 1), ('arx', 2), ('arx', 4)]
C, V = d.obs_model()
L = d.lqg(C, V)
A, B, Wn = d.A, d.B, d.W
NX, NY = 4, 2
LW, LV = np.linalg.cholesky(Wn), np.linalg.cholesky(V)


def stationary_bank(n_samples, rng):
    """States, observation and action histories from a long run of the optimal LQG controller."""
    x = np.zeros(NX); xi = np.zeros(NX)
    burn, keep = 3000, []
    ys, us = [], []
    for t in range(burn + n_samples * 7):
        if t >= burn and (t - burn) % 7 == 0:       # state at t with the history up to t-1 and the controller state
            keep.append((x.copy(), np.array(ys[-P['hist']:]), np.array(us[-P['hist']:]), xi.copy()))
        y = C @ x + LV @ rng.standard_normal(NY)
        u = float((L['Hc'] @ xi + L['Dc'] @ y)[0])
        ys.append(y); us.append(u)
        xi = L['F'] @ xi + L['G'] @ y
        x = A @ x + B[:, 0] * u + LW @ rng.standard_normal(NX)
    X0 = np.array([k[0] for k in keep]); Yh = np.array([k[1] for k in keep]); Uh = np.array([k[2] for k in keep])
    XI = np.array([k[3] for k in keep])
    return X0, Yh, Uh, XI                              # histories ordered oldest .. newest; last entries are y_{t-1}, u_{t-1}


def init_net(nin, rng):
    return [rng.standard_normal((nin, P['width'])) / np.sqrt(nin), np.zeros(P['width']),
            rng.standard_normal((P['width'], P['width'])) / np.sqrt(P['width']), np.zeros(P['width']),
            np.zeros((P['width'], 1)), np.zeros(1)]


def net(th, z):
    a = anp.tanh(anp.dot(z, th[0]) + th[1])
    a = anp.tanh(anp.dot(a, th[2]) + th[3])
    return (anp.dot(a, th[4]) + th[5])[:, 0]


def rollout_loss(th, kind, w, x0, yh, uh, noise_w, noise_v, sy, su):
    """Mean cost over T months under the network policy. yh: (B, w-1, NY) past observations (oldest first);
    uh: (B, k, ) past actions for ARX windows."""
    x = x0; ybuf = [yh[:, j, :] for j in range(yh.shape[1])]; ubuf = [uh[:, j] for j in range(uh.shape[1])]
    tot = 0.0
    Bv = B[:, 0]
    for t in range(P['T']):
        y = anp.dot(x, C.T) + noise_v[t]
        ybuf = ybuf[1:] + [y] if len(ybuf) == w else ybuf + [y]
        feats = [yy / sy for yy in ybuf[::-1]]
        if kind == 'arx':
            feats = feats + [anp.reshape(uu / su, (-1, 1)) for uu in ubuf[::-1]]
        z = anp.concatenate(feats, axis=1)
        u = net(th, z) * su
        tot = tot + anp.mean(anp.dot(x * x, np.diag(d.Q)) + d.R[0, 0] * u * u)
        if kind == 'arx' and w > 0:
            ubuf = ubuf[1:] + [u]
        x = anp.dot(x, A.T) + anp.outer(u, Bv) + noise_w[t]
    return tot / P['T']


def adam(g, th, m, v, it, lr):
    out_th, out_m, out_v = [], [], []
    for p_, gp, mp, vp in zip(th, g, m, v):
        mp = 0.9 * mp + 0.1 * gp; vp = 0.999 * vp + 0.001 * gp * gp
        mh = mp / (1 - 0.9 ** it); vh = vp / (1 - 0.999 ** it)
        out_th.append(p_ - lr * mh / (np.sqrt(vh) + 1e-8)); out_m.append(mp); out_v.append(vp)
    return out_th, out_m, out_v


def evaluate(th, kind, w, k, bank, rng, sy, su):
    """Paired simulation: network policy and optimal LQG controller on the same noise; returns mean excess and SE."""
    X0, Yh, Uh, XI = bank
    idx = rng.integers(0, len(X0), P['eval_batch'])
    xa = X0[idx].copy(); xb = X0[idx].copy()
    ybuf = [Yh[idx, -j, :] for j in range(w - 1, 0, -1)]
    ubuf = [Uh[idx, -j] for j in range(k, 0, -1)]
    xi = XI[idx].copy()                             # controller state of the optimal run at the start
    ca = np.zeros(len(idx)); cb = np.zeros(len(idx))
    for t in range(P['eval_T']):
        nw = rng.standard_normal((len(idx), NX)) @ LW.T; nv = rng.standard_normal((len(idx), NY)) @ LV.T
        ya = xa @ C.T + nv; yb = xb @ C.T + nv
        ybuf = (ybuf[1:] + [ya]) if len(ybuf) == w else (ybuf + [ya])
        feats = [yy / sy for yy in ybuf[::-1]]
        if kind == 'arx':
            feats = feats + [(uu / su).reshape(-1, 1) for uu in ubuf[::-1]]
        ua = np.asarray(net(th, np.concatenate(feats, axis=1))) * su
        ub = xi @ L['Hc'][0] + yb @ L['Dc'][0]
        if t >= 300:
            ca += xa[:, 2] ** 2 + d.R[0, 0] * ua ** 2; cb += xb[:, 2] ** 2 + d.R[0, 0] * ub ** 2
        if kind == 'arx' and k > 0:
            ubuf = ubuf[1:] + [ua]
        xi = xi @ L['F'].T + yb @ L['G'].T
        xa = xa @ A.T + np.outer(ua, B[:, 0]) + nw; xb = xb @ A.T + np.outer(ub, B[:, 0]) + nw
    n = P['eval_T'] - 300
    diff = (ca - cb) / n
    return float(np.mean(diff)), float(np.std(diff) / np.sqrt(len(diff))), float(np.mean(cb / n))


def task(args):
    kind, w, seed = args
    rng = np.random.default_rng(1000 + seed)
    bank = stationary_bank(4000, rng)
    X0, Yh, Uh, XI = bank
    sy = Yh.reshape(-1, NY).std(0); su = float(Uh.std())
    k = w if kind == 'arx' else 0
    nin = NY * (w if kind == 'obs' else w + 1) + k
    wo = w if kind == 'obs' else w + 1                  # number of observations seen (ARX: current + k past)
    th = init_net(nin, rng)
    m = [0 * p_ for p_ in th]; v = [0 * p_ for p_ in th]
    g = grad(rollout_loss)
    t0 = time.time(); losses = []
    for it in range(1, P['iters'] + 1):
        idx = rng.integers(0, len(X0), P['batch'])
        yh = Yh[idx, P['hist'] - (wo - 1):, :] if wo > 1 else np.zeros((P['batch'], 0, NY))
        uh = Uh[idx, P['hist'] - k:] if k > 0 else np.zeros((P['batch'], 0))
        nw = rng.standard_normal((P['T'], P['batch'], NX)) @ LW.T
        nv = rng.standard_normal((P['T'], P['batch'], NY)) @ LV.T
        lr = P['lr'] * (0.1 ** (it / P['iters']))
        gr = g(th, kind, wo, X0[idx], yh, uh, nw, nv, sy, su)
        gn = np.sqrt(sum(np.sum(x * x) for x in gr))
        if gn > 10:
            gr = [x * 10 / gn for x in gr]
        th, m, v = adam(gr, th, m, v, it, lr)
        if it == P['avg_from']:
            th_avg, n_avg = [x.copy() for x in th], 1
        elif it > P['avg_from']:                    # Polyak averaging of the weights over the second half of training
            n_avg += 1
            th_avg = [a + (x - a) / n_avg for a, x in zip(th_avg, th)]
        if it % 100 == 0:
            losses.append(float(rollout_loss(th, kind, wo, X0[idx], yh, uh, nw, nv, sy, su)))
    ex, se, jb = evaluate(th_avg, kind, wo, k, bank, np.random.default_rng(77 + seed), sy, su)
    return dict(kind=kind, w=w, seed=seed, excess=ex, se=se, J_opt_sim=jb, losses=losses, train_s=time.time() - t0)


def run():
    A_res = json.load(open(os.path.join(HERE, 'dritarja_results.json')))
    Js = A_res['J_star']
    tasks = [(kind, w, s) for kind, w in CONFIGS for s in range(P['seeds'])]
    with Pool(4) as pool:
        outs = pool.map(task, tasks)
    res = dict(P=P, J_star=Js, runs=outs, summary=[])
    log = []
    for kind, w in CONFIGS:
        rs = [o for o in outs if o['kind'] == kind and o['w'] == w]
        rel = [o['excess'] / Js for o in rs]
        lin = A_res['fir_opt'][str(w)] if kind == 'obs' else A_res['arx_opt'][str(w)]
        row = dict(kind=kind, w=w, rel_excess_median=float(np.median(rel)), rel_excess_min=float(np.min(rel)),
                   rel_excess_max=float(np.max(rel)), rel_se_median=float(np.median([o['se'] / Js for o in rs])),
                   linear_opt_rel=(lin - Js) / Js)
        res['summary'].append(row)
        log.append(f'{kind} window {w:2d}: neural excess cost (median of {len(rs)} seeds) {row["rel_excess_median"]:.2e} '
                   f'[{row["rel_excess_min"]:.2e}, {row["rel_excess_max"]:.2e}], paired SE {row["rel_se_median"]:.1e}; '
                   f'best linear policy of this window {row["linear_opt_rel"]:.2e}')
    json.dump(res, open(os.path.join(HERE, 'dritarja_neural.json'), 'w'), indent=1)
    open(os.path.join(HERE, 'dritarja_neural.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    run()
