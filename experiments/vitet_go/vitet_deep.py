"""VITET-GO, part C: how far are deep agents from the information floor? Near-optimal operators without private
information keep logs for N = 120, 360 or 1,200 months (10, 30, 100 years). Two learners use the same logs:
  * deep world model (tanh network with a linear skip, the last L months of head, chloride and pumping, L = 6, 18, 32)
    and a neural ARX policy trained through it by backpropagation (as in PASQYRA-GO, part C);
  * the 4-parameter physical model calibrated by likelihood: its exact plug-in rule, and the same neural policy trained
    through it.
Deployment on the true aquifer, paired with the optimal rule (256 x 2,400 months). The floor is tr(H I^-1) / (2 N J*).
Writes vitet_deep.json and vitet_deep.log.
"""
import json
import os
import sys
import time

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pasqyra_go'))
import pasqyra as p  # noqa: E402
import pasqyra_neural as pn  # noqa: E402
import vitet_monitor as vm  # noqa: E402

NS = {120: 6, 360: 18, 1200: 32}
SEEDS = 2


def task(args):
    N, seed = args
    lags = NS[N]
    rng = np.random.default_rng(77000 + 100 * list(NS).index(N) + seed)
    t0 = time.time()
    L = p.Logged(np.inf, 0.1, 0.0, 1.0)
    Y, Q, _ = pn.simulate_logs(L, N, rng)
    out = dict(N=N, seed=seed, lags=lags)
    thw, sc, Sres = pn.train_world_model(Y, Q, lags, rng)
    thp, sy, sq = pn.train_policy_in_world_model(Y, Q, thw, sc, Sres, lags, rng)
    out['deep_world_model'] = pn.deploy(pn.nn_policy(thp, sy, sq), rng)
    th = pn.calibrate_likelihood(Y, Q)
    A, B = p.model(th)
    out['physics_rule'] = float((p.J_of(p.lqg_controller(A, B)) - pn.JSTAR) / pn.JSTAR)
    thn, syn, sqn = pn.train_policy_in_physics(A, B, rng)
    out['physics_neural'] = pn.deploy(pn.nn_policy(thn, syn, sqn), rng)
    out['theta'] = th.tolist()
    out['seconds'] = time.time() - t0
    return out


def fmt(r):
    return f'unstable (month {r["month"]})' if r.get('unstable') else f'{100 * r["rel_excess"]:+.2f}%'


def run():
    with Pool(4) as pool:
        res = pool.map(task, [(N, s) for N in NS for s in range(SEEDS)])
    a = vm.analyse(vm.BASE_NET, sd_e=0.1)
    floor = {N: a['trHI'] / (2 * N * a['J_star']) for N in NS}
    log = [f'information floor tr(H I^-1)/(2 N J*): ' + ', '.join(f'{N} months {100 * floor[N]:.3f}%' for N in NS)]
    for r in res:
        log.append(f'{r["N"]:5d} months, seed {r["seed"]}: deep world model ({r["lags"]} lags) + neural policy {fmt(r["deep_world_model"])}; '
                   f'physics by likelihood: exact rule {100 * r["physics_rule"]:+.3f}%, neural policy through it {fmt(r["physics_neural"])}  [{r["seconds"]:.0f} s]')
    json.dump(p.clean(dict(NS=list(NS), floor={str(k): v for k, v in floor.items()}, runs=res)), open(os.path.join(HERE, 'vitet_deep.json'), 'w'), indent=1)
    open(os.path.join(HERE, 'vitet_deep.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    run()
