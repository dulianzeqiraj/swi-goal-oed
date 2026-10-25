"""VITET-GO, part B: Monte Carlo check of the local minimax formula. Near-optimal operators without private information
keep logs for N months; the 4-parameter physical model is calibrated by likelihood (pumping as forcing) and its optimal
rule deployed; the exact excess cost of the deployed rule, averaged over replications, is compared with
tr(H I^-1) / (2 N J*). Writes vitet_mc.json and vitet_mc.log.
"""
import json
import os
import sys
import time

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np
from multiprocessing import Pool
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pasqyra_go'))
import pasqyra as p  # noqa: E402
import pasqyra_neural as pn  # noqa: E402
import vitet_monitor as vm  # noqa: E402

NS = [120, 360, 1200]
REPS = 100
SD_E = 0.1


def nll_data(th, Y, Q):
    try:
        A, B, Kp, Sth = p.predictor_matrices(th)
    except Exception:
        return 1e6
    F = A - Kp @ p.C
    x = np.zeros(4); E = np.zeros_like(Y)
    for t in range(len(Q)):
        E[t] = Y[t] - p.C @ x
        x = F @ x + B[:, 0] * Q[t] + Kp @ Y[t]
    E = E[24:]
    if not np.all(np.isfinite(E)):
        return 1e6
    return 0.5 * np.linalg.slogdet(Sth)[1] + 0.5 * np.mean(np.sum((E @ np.linalg.inv(Sth)) * E, 1))


def job(args):
    N, rep = args
    rng = np.random.default_rng(31000 + 1000 * NS.index(N) + rep)
    L = p.Logged(np.inf, SD_E, 0.0, 1.0)
    pn.P['burn_log'] = 600
    Y, Q, _ = pn.simulate_logs(L, N + 24, rng)
    r = minimize(lambda th: nll_data(th, Y, Q), p.THETA0 * 0.9, method='Nelder-Mead',
                 options=dict(xatol=1e-7, fatol=1e-12, maxfev=4000))
    th = r.x
    try:
        J = p.J_of(p.lqg_controller(*p.model(th)))
    except Exception:
        J = float('inf')
    return dict(N=N, rep=rep, theta=th.tolist(), J=J)


def run():
    t0 = time.time()
    with Pool(4) as pool:
        res = pool.map(job, [(N, r) for N in NS for r in range(REPS)], chunksize=5)
    a = vm.analyse(vm.BASE_NET, sd_e=SD_E)
    Js = a['J_star']; trHI = a['trHI']
    I_inv = np.linalg.inv(a['I'])
    log, out = [], {}
    for N in NS:
        rows = [r for r in res if r['N'] == N]
        ex = np.array([(r['J'] - Js) / Js for r in rows])
        fin = ex[np.isfinite(ex)]
        th = np.array([r['theta'] for r in rows])
        pred = trHI / (2 * N * Js)
        sd_emp = th.std(0); sd_crlb = np.sqrt(np.diag(I_inv) / N)
        out[str(N)] = dict(mean_excess=float(fin.mean()), median_excess=float(np.median(fin)), se=float(fin.std() / np.sqrt(len(fin))),
                           unstable=int(np.sum(~np.isfinite(ex))), predicted=pred, ratio=float(fin.mean() / pred),
                           sd_theta=sd_emp.tolist(), sd_crlb=sd_crlb.tolist())
        log.append(f'{N:5d} months ({N // 12} years): mean excess of the deployed rule {100 * fin.mean():.3f}% (SE {100 * out[str(N)]["se"]:.3f}%), '
                   f'predicted tr(H I^-1)/(2 N J*) {100 * pred:.3f}%, ratio {out[str(N)]["ratio"]:.2f}; unstable {out[str(N)]["unstable"]}/{len(rows)}; '
                   f'sd of the estimates / Cramer-Rao ' + ', '.join(f'{x:.2f}' for x in sd_emp / sd_crlb))
    log.append(f'{REPS} replications per length; {time.time() - t0:.0f} s')
    json.dump(p.clean(dict(NS=NS, reps=REPS, J_star=Js, trHI=trHI, results=out)), open(os.path.join(HERE, 'vitet_mc.json'), 'w'), indent=1)
    open(os.path.join(HERE, 'vitet_mc.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    run()
