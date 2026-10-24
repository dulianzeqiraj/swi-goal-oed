"""BURIMI-GO, local versus practical identification (review 49, section 9.5).

(a) For the design "no stoichiometry, irrigation + clay-facies regimes" (locally identified, fibre 0) the ten simulated
data sets of burimi.py are fitted again: the best of six random starts is compared with a fit started at the truth,
by log-likelihood and by the error of the exchange counterfactual Q2.
(b) Population check: fits to the exact covariances (no sampling noise) from 20 random starts for five designs, to see
whether a second exact solution with a different counterfactual exists (a global twin) or not.
Writes burimi_modes.json and burimi_modes.log.
"""
import json
import os

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np
from autograd import grad
from multiprocessing import Pool
from scipy.optimize import minimize

import burimi as b

HERE = os.path.dirname(os.path.abspath(__file__))
z_obs = np.array([0.012, 0.6, 1.4]) / b.TRUE['sd']
X_OBS = (b.S * b.TRUE['sd'][None, :]) @ z_obs
CF = {k: np.array(b.q_unit(b.true_params((), ()), (), (), X_OBS, k)) for k in ('pump', 'exch')}
I_IC = 3                                   # index of the irrigation + clay-facies design in burimi.EST


def rel_err(p, known, targets, k):
    return float(np.linalg.norm(np.array(b.q_unit(p, known, targets, X_OBS, k)) - CF[k]) / np.linalg.norm(CF[k] - X_OBS))


def task_data(rep):
    name, known, targets = b.EST[I_IC]
    rng = np.random.default_rng(1000 * I_IC + rep + 7)        # the same data sets as burimi.py
    data = b.simulate(targets, rng)
    fits = b.fit(known, targets, data, rng, 6)
    Ss = [np.cov(x.T, bias=True) for x in data]; ns = [len(x) for x in data]
    f = lambda q: b.nll(q, known, targets, Ss, ns)
    pt = b.true_params(known, targets)
    r = minimize(f, pt, jac=grad(f), method='L-BFGS-B', options=dict(maxiter=3000))
    best = min(fits, key=lambda t: t[0])
    return dict(rep=rep, nll_best_random=float(best[0]), nll_from_truth=float(r.fun), nll_true=float(f(pt)),
                q2_err_best_random=rel_err(best[1], known, targets, 'exch'), q2_err_from_truth=rel_err(r.x, known, targets, 'exch'))


def task_pop(args):
    known, targets, seed = args
    pt = b.true_params(known, targets)
    Ss = [np.array(C) for C in b.covs_x(pt, known, targets)]
    f = lambda q: b.nll(q, known, targets, Ss, [1.0] * len(Ss))
    g = grad(f); f0 = float(f(pt))
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(4):
        p0 = pt.copy(); i = 0
        for j in range(b.n):
            if j in known:
                p0[i] = abs(pt[i]) * rng.uniform(0.3, 3); i += 1
            else:
                p0[i:i + b.d] = rng.standard_normal(b.d) * np.std(pt[i:i + b.d]) * 1.5; i += b.d
        p0[i:i + 3] = rng.standard_normal(3) * 2.0
        p0[i + 3:i + 3 + len(targets)] += rng.standard_normal(len(targets))
        p0[-b.d:] = np.log(b.TRUE['tau']) + rng.standard_normal(b.d) * 0.5
        try:
            r = minimize(f, p0, jac=g, method='L-BFGS-B', options=dict(maxiter=5000, ftol=1e-15, gtol=1e-10))
        except Exception:
            continue
        out.append(dict(kl=float(r.fun) - f0, q1=rel_err(r.x, known, targets, 'pump'), q2=rel_err(r.x, known, targets, 'exch')))
    return known, targets, out


def run():
    log = []
    with Pool(4) as pool:
        rows = pool.map(task_data, range(10))
        designs = [((), (1, 2)), ((0,), (0, 2)), ((0, 1), (2,)), ((0, 1, 2), ()), ((), (0, 1, 2))]
        pops = pool.map(task_pop, [(k, t, s) for k, t in designs for s in range(5)])
    for r in rows:
        log.append(f"data set {r['rep']}: best of 6 random starts NLL - NLL(true) = {r['nll_best_random'] - r['nll_true']:7.2f}, "
                   f"Q2 error {r['q2_err_best_random']:.2f}; started at the truth {r['nll_from_truth'] - r['nll_true']:7.2f}, "
                   f"Q2 error {r['q2_err_from_truth']:.2f}")
    pop = {}
    for k, t, o in pops:
        pop.setdefault(f'{list(k)}|{list(t)}', []).extend(o)
    for key, o in pop.items():
        wrong = [x for x in o if x['q2'] > 0.5]
        log.append(f"population fits {key}: {len(o)} fits, KL range {min(x['kl'] for x in o):.1e}-{max(x['kl'] for x in o):.1e}; "
                   f"fits with Q2 error > 0.5: {len(wrong)}" + (f", smallest KL among them {min(x['kl'] for x in wrong):.1e}" if wrong else ''))
    json.dump(dict(design=b.EST[I_IC][0], data_sets=rows, population=pop), open(os.path.join(HERE, 'burimi_modes.json'), 'w'), indent=1)
    open(os.path.join(HERE, 'burimi_modes.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    run()
