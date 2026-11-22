"""BURIMI-GO, goal-oriented precision of the counterfactual chemistry (review 49, section 9.5).

Identification is a statement about infinite data. For a finite design (N_BASE baseline samples and N_REG per
regime) the delta method gives the precision of a query q from the Fisher information of the Gaussian model,
    I(theta) = sum_k n_k/2 tr(S_k^-1 dS_k S_k^-1 dS_k),   Cov(q_hat) ~ J_q I^+ J_q^T,
valid when the query is identified (J_q in the row space of I). The predicted relative error of a unit-level
counterfactual is sqrt(tr Cov) divided by the size of the counterfactual change. This ranks the designs by what
the hydrochemist wants to know rather than by the identification of the whole model.
Writes burimi_precision.json and burimi_precision.log.
"""
import json
import os

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import autograd.numpy as anp
import numpy as np
from autograd import jacobian

import burimi as b

HERE = os.path.dirname(os.path.abspath(__file__))
d = b.d


def fisher(p, known, targets):
    covs = [np.array(C) for C in b.covs_x(p, known, targets)]
    ns = [b.N_BASE] + [b.N_REG] * len(targets)
    I = np.zeros((len(p), len(p)))
    for k in range(len(covs)):
        f = lambda q, k=k: b.covs_x(q, known, targets)[k]
        dS = jacobian(f)(p)                               # d x d x npar
        Si = np.linalg.inv(covs[k])
        A = np.einsum('ij,jkp->ikp', Si, dS)              # S^-1 dS_p
        I += 0.5 * ns[k] * np.einsum('ijp,jiq->pq', A, A)
    return I


def run():
    D = json.load(open(os.path.join(HERE, 'burimi_results.json')))
    x_obs = np.array(D['x_obs'])
    cf = {k: np.array(v) for k, v in D['cf_true'].items()}
    out, log = [], []
    for name, known, targets in b.DESIGNS:
        p = b.true_params(known, targets)
        I = fisher(p, known, targets)
        Ii = np.linalg.pinv(I, rcond=1e-10)
        row = dict(name=name, known=list(known), targets=list(targets))
        ident = next(r for r in D['identifiability'] if r['name'] == name)
        for key, qn, qi in [('pump', 'Q1 seawater halved (unit)', 'pred_rel_err_pump'),
                            ('exch', 'Q2 no exchange (unit)', 'pred_rel_err_exch')]:
            if ident[qn] > 1e-10:
                row[qi] = None
                continue
            Jq = jacobian(lambda q: b.q_unit(q, known, targets, x_obs, key))(p)
            C = Jq @ Ii @ Jq.T
            row[qi] = float(np.sqrt(max(np.trace(C), 0.0)) / np.linalg.norm(cf[key] - x_obs))
        out.append(row)
        f = lambda v: 'not identified' if v is None else f'{v:.3f}'
        log.append(f'{name:58s} predicted relative error: seawater halved {f(row["pred_rel_err_pump"])}, '
                   f'no exchange {f(row["pred_rel_err_exch"])}')
    json.dump(out, open(os.path.join(HERE, 'burimi_precision.json'), 'w'), indent=1)
    open(os.path.join(HERE, 'burimi_precision.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    run()
