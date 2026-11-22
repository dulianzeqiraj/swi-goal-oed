"""DRITARJA-GO, part B2: the same neural pumping agents trained without gradient noise. Stochastic training (part B,
dritarja_neural.py) stalls at an excess cost of about 1.3-1.6 % for every window, which hides the differences that
part A predicts. Here each agent minimises a fixed sample-average objective (BS simulated rollouts of T months drawn
once) by full-batch L-BFGS with exact gradients through the simulator; evaluation as in part B (paired simulation).
Writes dritarja_saa.json and dritarja_saa.log.
"""
import json
import os
import time

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np
from autograd import grad
from multiprocessing import Pool
from scipy.optimize import minimize

import dritarja_neural as dn

HERE = os.path.dirname(os.path.abspath(__file__))
PS = dict(BS=2048, maxiter=1000, seed=0)


def task(args):
    kind, w = args
    seed = PS['seed']
    rng = np.random.default_rng(1000 + seed)
    bank = dn.stationary_bank(4000, rng)
    X0, Yh, Uh, XI = bank
    sy = Yh.reshape(-1, dn.NY).std(0); su = float(Uh.std())
    k = w if kind == 'arx' else 0
    wo = w if kind == 'obs' else w + 1
    th = dn.init_net(dn.NY * wo + k, rng)
    shapes = [x.shape for x in th]; sizes = [x.size for x in th]
    cut = np.cumsum([0] + sizes)
    unflat = lambda v: [v[cut[i]:cut[i + 1]].reshape(shapes[i]) for i in range(len(th))]
    Bs = PS['BS']
    idx = rng.integers(0, len(X0), Bs)
    yh = Yh[idx, dn.P['hist'] - (wo - 1):, :] if wo > 1 else np.zeros((Bs, 0, dn.NY))
    uh = Uh[idx, dn.P['hist'] - k:] if k > 0 else np.zeros((Bs, 0))
    nw = rng.standard_normal((dn.P['T'], Bs, dn.NX)) @ dn.LW.T
    nv = rng.standard_normal((dn.P['T'], Bs, dn.NY)) @ dn.LV.T
    f = lambda v: dn.rollout_loss(unflat(v), kind, wo, X0[idx], yh, uh, nw, nv, sy, su)
    t0 = time.time()
    r = minimize(f, np.concatenate([x.ravel() for x in th]), jac=grad(f), method='L-BFGS-B', options=dict(maxiter=PS['maxiter']))
    ex, se, jb = dn.evaluate(unflat(r.x), kind, wo, k, bank, np.random.default_rng(77 + seed), sy, su)
    return dict(kind=kind, w=w, excess=ex, se=se, nit=int(r.nit), loss=float(r.fun), train_s=time.time() - t0)


def run():
    A_res = json.load(open(os.path.join(HERE, 'dritarja_results.json')))
    Js = A_res['J_star']
    with Pool(4) as pool:
        outs = pool.map(task, dn.CONFIGS)
    res = dict(PS=PS, P=dn.P, J_star=Js, runs=outs, summary=[])
    log = []
    for o in outs:
        lin = A_res['fir_opt'][str(o['w'])] if o['kind'] == 'obs' else A_res['arx_opt'][str(o['w'])]
        row = dict(kind=o['kind'], w=o['w'], rel_excess=o['excess'] / Js, rel_se=o['se'] / Js, linear_opt_rel=(lin - Js) / Js, nit=o['nit'])
        res['summary'].append(row)
        log.append(f'{o["kind"]} window {o["w"]:2d}: neural excess cost (full-batch training) {row["rel_excess"]:.2e} '
                   f'(paired SE {row["rel_se"]:.1e}, {o["nit"]} L-BFGS iterations); best linear policy {row["linear_opt_rel"]:.2e}')
    json.dump(res, open(os.path.join(HERE, 'dritarja_saa.json'), 'w'), indent=1)
    open(os.path.join(HERE, 'dritarja_saa.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    run()
