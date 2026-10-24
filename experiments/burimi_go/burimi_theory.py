"""BURIMI-GO, checks of Proposition B (review 49, section 9) at random parameter values.

(i)-(ii) With baseline data only and k known stoichiometric signatures (up to scale), the fibre of equally good models
has dimension (n - k)(n - 1) for n latent processes: rotations O(n) and the n(n-1)/2 edge coefficients, minus n - 1
conditions per known signature. (iii) A perfect intervention on the source process (pumping regime) changes the
covariance of the chemistry by a rank-one matrix along the total-effect signature h_s = G (I - A)^{-1} e_s.
The fibre dimension of all 16 designs of burimi.py is also recomputed at random parameters (genericity).
Writes burimi_theory.json and burimi_theory.log.
"""
import json
import os

import autograd.numpy as anp
import numpy as np
from autograd import jacobian

import burimi as b

HERE = os.path.dirname(os.path.abspath(__file__))
n, d = b.n, b.d


def random_params(known, targets, rng):
    p = []
    for j in range(n):
        p += [rng.uniform(0.5, 2.0) * rng.choice([-1, 1])] if j in known else list(rng.standard_normal(d))
    p += list(rng.standard_normal(3))
    p += list(rng.uniform(-1.0, 1.0, len(targets)))
    p += list(np.log(rng.uniform(0.05, 0.3, d)))
    return np.array(p, float)


def fibre(p, known, targets):
    f = lambda q: anp.concatenate([C[np.triu_indices(d)] for C in b.covs_x(q, known, targets, noise=False)])
    J = jacobian(f)(p)[:, :len(p) - d]
    sv = np.linalg.svd(J, compute_uv=False)
    return int(J.shape[1] - np.sum(sv > sv[0] * 1e-9))


def run():
    rng = np.random.default_rng(491)
    draws = 20
    out = dict(draws=draws, baseline=[], designs=[])
    log = []
    for known in [(), (0,), (2,), (0, 1), (0, 2), (0, 1, 2)]:
        fs = [fibre(random_params(known, (), rng), known, ()) for _ in range(draws)]
        pred = (n - len(known)) * (n - 1)
        out['baseline'].append(dict(known=list(known), predicted=pred, fibres=fs, all_match=all(f == pred for f in fs)))
        log.append(f'baseline only, known signatures {known}: fibre {sorted(set(fs))} over {draws} random draws; '
                   f'predicted (n-k)(n-1) = {pred}')
    for name, known, targets in b.DESIGNS:
        fs = [fibre(random_params(known, targets, rng), known, targets) for _ in range(draws)]
        out['designs'].append(dict(name=name, fibres=fs))
        log.append(f'{name:58s} fibre at random parameters: min {min(fs)}, max {max(fs)}')
    # rank-one change under a source regime, at the true parameters
    p = b.true_params((), (0,))
    S0, S1 = [np.array(C) for C in b.covs_x(p, (), (0,), noise=False)]
    G, a, newsd, _ = b.unpack(p, (), (0,))
    h = np.array(G) @ np.linalg.inv(np.eye(n) - np.array(b.Amat(a)))[:, 0]
    resid = np.linalg.norm(S1 - S0 - (float(newsd[0]) ** 2 - 1) * np.outer(h, h)) / np.linalg.norm(S1 - S0)
    sv = np.linalg.svd(S1 - S0, compute_uv=False)
    out['source_regime'] = dict(rel_residual=float(resid), sv_ratio=float(sv[1] / sv[0]))
    log.append(f'source regime: ||S1 - S0 - (sigma^2 - 1) h h^T|| / ||S1 - S0|| = {resid:.1e}; second/first singular '
               f'value of S1 - S0 = {sv[1] / sv[0]:.1e}')
    json.dump(out, open(os.path.join(HERE, 'burimi_theory.json'), 'w'), indent=1)
    open(os.path.join(HERE, 'burimi_theory.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


if __name__ == '__main__':
    run()
