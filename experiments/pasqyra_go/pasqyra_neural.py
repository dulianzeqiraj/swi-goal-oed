"""PASQYRA-GO, part C: deep agents trained offline on the operators' logs, deployed on the true aquifer.

Logs: 12,000 months simulated from the logged world of pasqyra.py (aquifer + operators who also read the toe at private
wells), with the same run repeated without private information as a control. Agents (tanh networks with a linear skip
connection; the linear part is initialised by least squares, then everything is trained by Adam):
  * deep world model: y_{t+1} from the last L observations and pumping rates (L = 32 or 48 months); the pumping policy
    (an ARX window of 5 observations and 4 past pumping rates, review 50) is trained by backpropagation through 60-month
    rollouts of the world model (model-based offline deep RL); the cost it believes is measured in the world model;
  * deep clones of the operators: ARX window (5 observations, 4 past rates) and observation-only window (8 months);
  * the remedy: a recorded dither (sd 0.1) in the logs, the physical model calibrated by the dither moments on the finite
    logs, and the same neural policy trained through that model.
Deployment: 256 aquifers x 2,400 months on the true aquifer, paired with the optimal records-only rule on the same
noise. Writes pasqyra_neural.json and pasqyra_neural.log.
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
from scipy.optimize import least_squares

import pasqyra as p

HERE = os.path.dirname(os.path.abspath(__file__))
P = dict(T_log=12000, burn_log=600, width=64, pol_width=32, k=4, wm_iters=4000, wm_batch=512, wm_lr=1e-3,
         T=60, batch=256, iters=1500, lr=3e-3, avg_from=750, clone_iters=3000, eval_batch=256, eval_T=2400, burn=300,
         believe_T=600, sd_d=0.1, seeds=2)
NX, NY = 4, 2
A0, B0, C, R = p.A0, p.B0, p.C, p.R[0, 0]
LW, LV = np.linalg.cholesky(p.W), np.linalg.cholesky(p.V)
LSTAR = p.lqg_controller(A0, B0)
JSTAR = p.J_of(LSTAR)


# ------------------------------------------------------------------ logs
def simulate_logs(L, T, rng):
    """Simulate the logged world; returns y (T, 2), q (T,), d (T,)."""
    n = L.nn
    sdn = np.sqrt(np.diag(L.N))
    xi = np.zeros(2 * NX)
    Y, Q, D = np.zeros((T, NY)), np.zeros(T), np.zeros(T)
    for t in range(T + P['burn_log']):
        nz = sdn * rng.standard_normal(n)
        y = L.Hy @ xi + L.Jy @ nz; q = (L.Hq @ xi + L.Jq @ nz)[0]; d = (L.Jd @ nz)[0]
        if t >= P['burn_log']:
            Y[t - P['burn_log']] = y; Q[t - P['burn_log']] = q; D[t - P['burn_log']] = d
        xi = L.Phi @ xi + L.Gam @ nz
    return Y, Q, D


def windows(Y, Q, ly, lq, q_from):
    """Rows t (from max lag) of [y_t..y_{t-ly+1}, q_{t-q_from}..q_{t-q_from-lq+1}]."""
    T = len(Q); s = max(ly - 1, q_from + lq - 1)
    rows = []
    for t in range(s, T):
        rows.append(np.concatenate([Y[t - ly + 1:t + 1][::-1].ravel(), Q[t - q_from - lq + 1:t - q_from + 1][::-1]]))
    return np.array(rows), s


# ------------------------------------------------------------------ networks with a linear skip
def init_net(nin, nout, width, rng, lin=None):
    return [rng.standard_normal((nin, width)) / np.sqrt(nin), np.zeros(width),
            rng.standard_normal((width, width)) / np.sqrt(width), np.zeros(width),
            np.zeros((width, nout)), np.zeros(nout),
            (np.zeros((nin, nout)) if lin is None else lin[0]), (np.zeros(nout) if lin is None else lin[1])]


def net(th, z):
    a = anp.tanh(anp.dot(z, th[0]) + th[1])
    a = anp.tanh(anp.dot(a, th[2]) + th[3])
    return anp.dot(a, th[4]) + th[5] + anp.dot(z, th[6]) + th[7]


def adam(g, th, m, v, it, lr):
    out = ([], [], [])
    for p_, gp, mp, vp in zip(th, g, m, v):
        mp = 0.9 * mp + 0.1 * gp; vp = 0.999 * vp + 0.001 * gp * gp
        mh = mp / (1 - 0.9 ** it); vh = vp / (1 - 0.999 ** it)
        out[0].append(p_ - lr * mh / (np.sqrt(vh) + 1e-8)); out[1].append(mp); out[2].append(vp)
    return out


def fit_supervised(Z, T_, width, rng, iters):
    """Least-squares linear start, then Adam on the mean squared error of the full network."""
    Zc = np.hstack([Z, np.ones((len(Z), 1))])
    sol = np.linalg.lstsq(Zc, T_, rcond=None)[0]
    th = init_net(Z.shape[1], T_.shape[1], width, rng, lin=(sol[:-1], sol[-1]))
    loss = lambda th, z, t: anp.mean(anp.sum((net(th, z) - t) ** 2, axis=1))
    g = grad(loss)
    m = [0 * x for x in th]; v = [0 * x for x in th]
    for it in range(1, iters + 1):
        idx = rng.integers(0, len(Z), P['wm_batch'])
        lr = P['wm_lr'] * (0.1 ** (it / iters))
        th, m, v = adam(g(th, Z[idx], T_[idx]), th, m, v, it, lr)
    res = np.asarray(net(th, Z)) - T_
    return th, res


# ------------------------------------------------------------------ deep world model agent
def train_world_model(Y, Q, lags, rng):
    Z, s = windows(Y, Q, lags, lags, 0)                     # y_t..y_{t-L+1}, q_t..q_{t-L+1}
    Tgt = Y[s + 1:]
    Z = Z[:-1]
    sc = np.concatenate([np.tile(Y.std(0), lags), np.full(lags, Q.std())])
    th, res = fit_supervised(Z / sc, Tgt, P['width'], rng, P['wm_iters'])
    return th, sc, np.cov(res.T)


def policy_feats(ybuf, qbuf, sy, sq):
    """ybuf newest-first list of (B,2) (5 entries), qbuf newest-first list of (B,) (4 entries)."""
    return anp.concatenate([yy / sy for yy in ybuf[:P['k'] + 1]] + [anp.reshape(qq / sq, (-1, 1)) for qq in qbuf[:P['k']]], axis=1)


def wm_rollout_loss(thp, thw, sc, Lres, lags, y0, q0, eps, sy, sq):
    """Mean believed cost over T months in the world model. y0: (B, lags, 2) newest-first, q0: (B, lags) newest-first
    (q0[:,0] = q_{t-1})."""
    ybuf = [y0[:, j, :] for j in range(lags)]; qbuf = [q0[:, j] for j in range(lags)]
    tot = 0.0
    for t in range(P['T']):
        q = net(thp, policy_feats(ybuf, qbuf, sy, sq))[:, 0] * sq
        tot = tot + anp.mean(ybuf[0][:, 1] ** 2 + R * q * q)
        qbuf = [q] + qbuf[:-1]
        z = anp.concatenate([yy for yy in ybuf] + [anp.reshape(qq, (-1, 1)) for qq in qbuf], axis=1) / sc
        ynew = net(thw, z) + eps[t]
        ybuf = [ynew] + ybuf[:-1]
    return tot / P['T']


def reorder_z(Yw, Qw, lags):
    """World-model input ordering: [y_t..y_{t-L+1} flattened, q_t..q_{t-L+1}] built from newest-first buffers."""
    return np.concatenate([Yw.reshape(len(Yw), -1), Qw], axis=1)


def train_policy_in_world_model(Y, Q, thw, sc, Sres, lags, rng):
    Lres = np.linalg.cholesky(Sres + 1e-12 * np.eye(NY))
    T = len(Q); starts = np.arange(lags + 1, T - 1)
    sy, sq = Y.std(0), Q.std()
    thp = init_net(NY * (P['k'] + 1) + P['k'], 1, P['pol_width'], rng)
    m = [0 * x for x in thp]; v = [0 * x for x in thp]; avg = None; na = 0
    g = grad(wm_rollout_loss)
    for it in range(1, P['iters'] + 1):
        idx = rng.choice(starts, P['batch'])
        y0 = np.stack([Y[i - lags + 1:i + 1][::-1] for i in idx])        # y_t newest first
        q0 = np.stack([Q[i - lags:i][::-1] for i in idx])                  # q_{t-1} newest first
        eps = rng.standard_normal((P['T'], P['batch'], NY)) @ Lres.T
        gr = g(thp, thw, sc, Lres, lags, y0, q0, eps, sy, sq)
        gr = [np.clip(x, -10, 10) for x in gr]
        thp, m, v = adam(gr, thp, m, v, it, P['lr'] * (0.1 ** (it / P['iters'])))
        if it > P['avg_from']:
            na += 1; avg = [x.copy() for x in thp] if avg is None else [a + (x - a) / na for a, x in zip(avg, thp)]
    return avg, sy, sq


def believed_cost(thp, thw, sc, Sres, lags, Y, Q, sy, sq, rng):
    Lres = np.linalg.cholesky(Sres + 1e-12 * np.eye(NY))
    idx = rng.choice(np.arange(lags + 1, len(Q) - 1), P['eval_batch'])
    ybuf = [Y[idx - j] for j in range(lags)]; qbuf = [Q[idx - 1 - j] for j in range(lags)]
    tot, n = 0.0, 0
    for t in range(P['believe_T']):
        q = np.asarray(net(thp, policy_feats(ybuf, qbuf, sy, sq)))[:, 0] * sq
        if t >= 100:
            tot += np.mean(ybuf[0][:, 1] ** 2 + R * q * q); n += 1
        qbuf = [q] + qbuf[:-1]
        z = np.concatenate(ybuf + [qq.reshape(-1, 1) for qq in qbuf], axis=1) / sc
        ybuf = [np.asarray(net(thw, z)) + rng.standard_normal((len(idx), NY)) @ Lres.T] + ybuf[:-1]
        if not np.all(np.isfinite(ybuf[0])) or np.max(np.abs(ybuf[0])) > 1e4:
            return float('inf')
    return tot / n - p.V[1, 1]


# ------------------------------------------------------------------ the remedy: physics calibrated by dither moments
def pred_errors(theta, Y, Q):
    A, B, Kp, Sth = p.predictor_matrices(theta)
    x = np.zeros(NX); E = np.zeros_like(Y)
    F = A - Kp @ C
    for t in range(len(Q)):
        E[t] = Y[t] - C @ x
        x = F @ x + B[:, 0] * Q[t] + Kp @ Y[t]
    return E


def calibrate_moments(Y, Q, D, m_lags=24):
    sd2 = np.mean(D ** 2)
    def res(th):
        try:
            E = pred_errors(th, Y, Q)
        except Exception:
            return np.full(NY * m_lags, 1e3)
        E = E[50:]; Dd = D[50:]
        return np.concatenate([np.mean(E[k:] * Dd[:len(Dd) - k, None], axis=0) / sd2 for k in range(1, m_lags + 1)])
    r = least_squares(res, p.THETA0 * 0.8, xtol=1e-12, ftol=1e-12)
    return r.x


def phys_rollout_loss(th, A, B, x0, qh, yh, nw, nv, sy, sq):
    """Neural ARX policy in the physical model (A, B): latent state, observations with noise, cost (X + 0.5 c)^2 + R q^2."""
    x = x0; ybuf = [yh[:, j, :] for j in range(P['k'])]; qbuf = [qh[:, j] for j in range(P['k'])]
    tot = 0.0
    cc = p.CCL[0]
    for t in range(P['T'] * 2):
        y = anp.dot(x, C.T) + nv[t]
        ybuf = [y] + ybuf[:P['k']]
        q = net(th, policy_feats(ybuf, qbuf, sy, sq))[:, 0] * sq
        tot = tot + anp.mean(anp.dot(x, cc) ** 2 + R * q * q)
        qbuf = [q] + qbuf[:-1]
        x = anp.dot(x, A.T) + anp.outer(q, B[:, 0]) + nw[t]
    return tot / (2 * P['T'])


def model_bank(A, B, n, rng):
    """Stationary states and windows of the model (A, B) under its own optimal rule."""
    ct = p.lqg_controller(A, B)
    x = np.zeros(NX); xi = np.zeros(NX); ys, qs, keep = [], [], []
    for t in range(2000 + 7 * n):
        if t >= 2000 and (t - 2000) % 7 == 0 and len(ys) >= P['k']:
            keep.append((x.copy(), np.array(qs[-P['k']:][::-1]), np.array(ys[-P['k']:][::-1]), xi.copy()))
        y = C @ x + LV @ rng.standard_normal(NY)
        q = float((ct['Hc'] @ xi + ct['Dc'] @ y)[0])
        ys.append(y); qs.append(q)
        xi = ct['F'] @ xi + ct['G'] @ y
        x = A @ x + B[:, 0] * q + LW @ rng.standard_normal(NX)
    return (np.array([k[0] for k in keep]), np.array([k[1] for k in keep]), np.array([k[2] for k in keep]),
            np.array(ys).std(0), np.array(qs).std())


def train_policy_in_physics(A, B, rng):
    X0, Qh, Yh, sy, sq = model_bank(A, B, 4000, rng)
    th = init_net(NY * (P['k'] + 1) + P['k'], 1, P['pol_width'], rng)
    m = [0 * x for x in th]; v = [0 * x for x in th]; avg = None; na = 0
    g = grad(phys_rollout_loss)
    for it in range(1, P['iters'] + 1):
        idx = rng.integers(0, len(X0), P['batch'])
        nw = rng.standard_normal((2 * P['T'], P['batch'], NX)) @ LW.T
        nv = rng.standard_normal((2 * P['T'], P['batch'], NY)) @ LV.T
        gr = g(th, A, B, X0[idx], Qh[idx], Yh[idx], nw, nv, sy, sq)
        gr = [np.clip(x, -10, 10) for x in gr]
        th, m, v = adam(gr, th, m, v, it, P['lr'] * (0.1 ** (it / P['iters'])))
        if it > P['avg_from']:
            na += 1; avg = [x.copy() for x in th] if avg is None else [a + (x - a) / na for a, x in zip(avg, th)]
    return avg, sy, sq


# ------------------------------------------------------------------ deployment on the true aquifer
def deploy(policy, rng):
    """policy(ybuf newest-first list, qbuf newest-first list) -> q (B,). Paired with the optimal rule on the same noise.
    Returns mean excess cost relative to J*, its SE, and an instability flag."""
    nb = P['eval_batch']
    xa = np.zeros((nb, NX)); xb = np.zeros((nb, NX)); xi = np.zeros((nb, NX))
    ybuf = [np.zeros((nb, NY)) for _ in range(8)]; qbuf = [np.zeros(nb) for _ in range(8)]
    ca = np.zeros(nb); cb = np.zeros(nb)
    cc = p.CCL[0]
    for t in range(P['eval_T']):
        nw = rng.standard_normal((nb, NX)) @ LW.T; nv = rng.standard_normal((nb, NY)) @ LV.T
        ya = xa @ C.T + nv; yb = xb @ C.T + nv
        ybuf = [ya] + ybuf[:-1]
        qa = policy(ybuf, qbuf)
        qb = xi @ LSTAR['Hc'][0] + yb @ LSTAR['Dc'][0]
        if t >= P['burn']:
            ca += (xa @ cc) ** 2 + R * qa ** 2; cb += (xb @ cc) ** 2 + R * qb ** 2
        qbuf = [qa] + qbuf[:-1]
        xi = xi @ LSTAR['F'].T + yb @ LSTAR['G'].T
        xa = xa @ A0.T + np.outer(qa, B0[:, 0]) + nw; xb = xb @ A0.T + np.outer(qb, B0[:, 0]) + nw
        if not np.all(np.isfinite(xa)) or np.max(np.abs(xa)) > 1e3:
            return dict(rel_excess=None, se=None, unstable=True, month=t)
    n = P['eval_T'] - P['burn']
    diff = (ca - cb) / n
    return dict(rel_excess=float(np.mean(diff) / JSTAR), se=float(np.std(diff) / np.sqrt(nb) / JSTAR), unstable=False,
                J_ref=float(np.mean(cb / n)))


def nn_policy(th, sy, sq):
    return lambda yb, qb: np.asarray(net(th, policy_feats(yb, qb, sy, sq)))[:, 0] * sq


def clone_policy(th, sz, kind):
    if kind == 'arx':
        return lambda yb, qb: np.asarray(net(th, np.concatenate([yb[j] for j in range(P['k'] + 1)] + [qb[j].reshape(-1, 1) for j in range(P['k'])], axis=1) / sz))[:, 0]
    return lambda yb, qb: np.asarray(net(th, np.concatenate([yb[j] for j in range(8)], axis=1) / sz))[:, 0]


# ------------------------------------------------------------------ tasks
CASES = [('near-optimal', 1.0, 32), ('timid', 0.4, 48)]


def task(args):
    case, private, seed = args
    gamma, lags = {c[0]: (c[1], c[2]) for c in CASES}[case]
    rng = np.random.default_rng(5000 + 17 * seed + (0 if private else 7) + (0 if case == 'near-optimal' else 3))
    t0 = time.time()
    out = dict(case=case, private=private, seed=seed)
    L = p.Logged(p.BASE['sd_s'] if private else np.inf, p.BASE['sd_e'], 0.0, gamma)
    Y, Q, _ = simulate_logs(L, P['T_log'], rng)
    # world model agent
    thw, sc, Sres = train_world_model(Y, Q, lags, rng)
    thp, sy, sq = train_policy_in_world_model(Y, Q, thw, sc, Sres, lags, rng)
    out['world_model_agent'] = deploy(nn_policy(thp, sy, sq), rng)
    bel = believed_cost(thp, thw, sc, Sres, lags, Y, Q, sy, sq, rng)
    out['world_model_agent']['believed_rel'] = None if not np.isfinite(bel) else float((bel - JSTAR) / JSTAR)
    # clones
    Z, s = windows(Y, Q, P['k'] + 1, P['k'], 1)
    sz = np.concatenate([np.tile(Y.std(0), P['k'] + 1), np.full(P['k'], Q.std())])
    thc, _ = fit_supervised(Z / sz, Q[s:, None], P['width'], rng, P['clone_iters'])
    out['clone_arx4'] = deploy(clone_policy(thc, sz, 'arx'), rng)
    Z8, s8 = windows(Y, Q, 8, 0, 1)
    sz8 = np.tile(Y.std(0), 8)
    tho, _ = fit_supervised(Z8 / sz8, Q[s8:, None], P['width'], rng, P['clone_iters'])
    out['clone_obs8'] = deploy(clone_policy(tho, sz8, 'obs'), rng)
    # the remedy (only with private information): recorded dither, physics calibrated by its moments, neural policy
    if private:
        Ld = p.Logged(p.BASE['sd_s'], p.BASE['sd_e'], P['sd_d'], gamma)
        Yd, Qd, Dd = simulate_logs(Ld, P['T_log'], rng)
        th_iv = calibrate_moments(Yd, Qd, Dd)
        Ai, Bi = p.model(th_iv)
        thr, syr, sqr = train_policy_in_physics(Ai, Bi, rng)
        out['physics_iv_agent'] = deploy(nn_policy(thr, syr, sqr), rng)
        out['physics_iv_agent']['theta'] = th_iv.tolist()
        out['physics_iv_agent']['J_op_dither_rel'] = float((Ld.J - JSTAR) / JSTAR)
    out['J_op_rel'] = float((L.J - JSTAR) / JSTAR)
    out['seconds'] = time.time() - t0
    return out


def fmt(r):
    if r is None:
        return '-'
    if r.get('unstable'):
        return f'unstable (month {r["month"]})'
    return f'{100 * r["rel_excess"]:+.1f}% (SE {100 * r["se"]:.1f})'


def run():
    jobs = [(c[0], pr, s) for c in CASES for pr in (True, False) for s in range(P['seeds'])]
    with Pool(4) as pool:
        res = pool.map(task, jobs)
    log = [f'J* = {JSTAR:.4f}; logs of {P["T_log"]} months; deployment {P["eval_batch"]} x {P["eval_T"]} months, paired with the optimal rule']
    for r in res:
        line = (f'{r["case"]:12s} {"private" if r["private"] else "no private"} seed {r["seed"]}: operators {100 * r["J_op_rel"]:+.1f}%; '
                f'deep world-model agent {fmt(r["world_model_agent"])}, believed '
                f'{"diverges" if r["world_model_agent"]["believed_rel"] is None else f"{100 * r["world_model_agent"]["believed_rel"]:+.1f}%"}; '
                f'deep clone ARX {fmt(r["clone_arx4"])}; deep clone obs8 {fmt(r["clone_obs8"])}')
        if 'physics_iv_agent' in r:
            line += f'; physics by dither moments + neural policy {fmt(r["physics_iv_agent"])} (theta {np.round(r["physics_iv_agent"]["theta"], 3)})'
        log.append(line + f'  [{r["seconds"]:.0f} s]')
    json.dump(dict(P=P, J_star=JSTAR, runs=p.clean(res)), open(os.path.join(HERE, 'pasqyra_neural.json'), 'w'), indent=1)
    open(os.path.join(HERE, 'pasqyra_neural.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    run()
