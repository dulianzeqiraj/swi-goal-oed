"""DRITARJA-GO, check of part B2: do the full-batch networks overfit their fixed set of rollouts?

For every window the fixed training set of dritarja_saa.py is rebuilt (same random-number sequence) and the in-sample
loss of the exactly optimal LQG rule on it is computed. A network whose in-sample loss is below that of the optimal rule
fits the particular noise of the set rather than the aquifer. Writes dritarja_saa_check.json and dritarja_saa_check.log.
"""
import json
import os

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np

import dritarja_neural as dn
import dritarja_saa as ds

HERE = os.path.dirname(os.path.abspath(__file__))


def check(kind, w):
    rng = np.random.default_rng(1000 + ds.PS['seed'])
    X0, Yh, Uh, XI = dn.stationary_bank(4000, rng)
    k = w if kind == 'arx' else 0
    wo = w if kind == 'obs' else w + 1
    dn.init_net(dn.NY * wo + k, rng)                  # consume the same random numbers as the training run
    Bs = ds.PS['BS']
    idx = rng.integers(0, len(X0), Bs)
    nw = rng.standard_normal((dn.P['T'], Bs, dn.NX)) @ dn.LW.T
    nv = rng.standard_normal((dn.P['T'], Bs, dn.NY)) @ dn.LV.T
    x = X0[idx].copy(); xi = XI[idx].copy(); tot = 0.0
    L = dn.L
    for t in range(dn.P['T']):
        y = x @ dn.C.T + nv[t]
        u = xi @ L['Hc'][0] + y @ L['Dc'][0]
        tot += np.mean(x[:, 2] ** 2 + dn.d.R[0, 0] * u ** 2)
        xi = xi @ L['F'].T + y @ L['G'].T
        x = x @ dn.A.T + np.outer(u, dn.B[:, 0]) + nw[t]
    return tot / dn.P['T']


def run():
    S = json.load(open(os.path.join(HERE, 'dritarja_saa.json')))
    out, log = [], []
    for r in S['runs']:
        opt = check(r['kind'], r['w'])
        gap = (r['loss'] - opt) / opt
        out.append(dict(kind=r['kind'], w=r['w'], loss_network=r['loss'], loss_optimal_rule=opt, rel_gap=gap,
                        n_weights=int(sum(np.prod(s) for s in [(dn.NY * (r['w'] if r['kind'] == 'obs' else r['w'] + 1) + (r['w'] if r['kind'] == 'arx' else 0), 32), (32,), (32, 32), (32,), (32, 1), (1,)]))))
        log.append(f'{r["kind"]} window {r["w"]:2d}: in-sample loss of the network {r["loss"]:.5f}, of the optimal rule {opt:.5f} '
                   f'(network - optimal: {100 * gap:+.2f}%); {out[-1]["n_weights"]} weights')
    json.dump(out, open(os.path.join(HERE, 'dritarja_saa_check.json'), 'w'), indent=1)
    open(os.path.join(HERE, 'dritarja_saa_check.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    run()
