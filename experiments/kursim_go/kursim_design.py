"""KURSIM-GO policy design: how the season-2 pumping policy P(A2 = 1 | L1, A1, L2) = expit(b0 + 0.5 L1 + 0.6 A1 + b3 L2)
trades the risk of pumping during an alarm against the precision with which the causal effects can be learned.

For each policy on a grid of (b0, b3), on 200 000 simulated well-seasons:
  risk = P(L2 = 1, A2 = 1), production = P(A2 = 1);
  n x asymptotic variance of theta2 and theta1 for the frugal MLE (inverse of the expected information, from the outer
  product of exact scores), for IPW (sandwich) and for the doubly robust estimator (influence-function variance).
The causal parameters do not change with the policy (variation independence). Writes kursim_design.json.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import json, time
import numpy as np
from multiprocessing import Pool
import kursim_model as K
import kursim_est as E

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
NS = 200_000
B0 = np.round(np.linspace(-2.5, 2.5, 11), 3)
B3 = np.round(np.linspace(-7.0, 0.0, 15), 3)


def frugal_avar(D, v):
    h = 1e-5; S = np.empty((len(D['Y']), len(v)))
    for k in range(len(v)):
        e = np.zeros(len(v)); e[k] = h
        S[:, k] = (K.loglik_obs(v + e, D) - K.loglik_obs(v - e, D)) / (2 * h)
    I = S.T @ S / len(D['Y'])
    V = np.linalg.inv(I)
    return V[5, 5], V[4, 4]


def one(args):
    b0, b3 = args
    rng = np.random.default_rng(int(1000 * (b0 + 10)) * 7919 + int(1000 * (b3 + 10)))
    past = dict(K.PAST, b0=b0, b3=b3)
    D = K.simulate(NS, rng, past=past); D.pop('pi')
    fr2, fr1 = frugal_avar(D, K.true_vector(past))
    _, _, s1, s2 = E.ipw(D); ip1, ip2 = NS * s1 ** 2, NS * s2 ** 2
    _, _, d1, d2 = E.dr(D); dr1, dr2 = NS * d1 ** 2, NS * d2 ** 2
    return dict(b0=float(b0), b3=float(b3), risk=float((D['L2'] * D['A2']).mean()), prod=float(D['A2'].mean()),
                frugal2=fr2, frugal1=fr1, ipw2=ip2, ipw1=ip1, dr2=dr2, dr1=dr1)


def main():
    t0 = time.time()
    grid = [(b0, b3) for b0 in B0 for b3 in B3] + [(K.PAST['b0'], K.PAST['b3'])]
    with Pool(4) as pool:
        res = pool.map(one, grid, chunksize=4)
    base = res[-1]
    json.dump(dict(grid=res[:-1], baseline=base, NS=NS), open('kursim_design.json', 'w'), indent=1)
    print(f'baseline: risk {base["risk"]:.3f} prod {base["prod"]:.3f} frugal2 {base["frugal2"]:.2f} ipw2 {base["ipw2"]:.2f} dr2 {base["dr2"]:.2f}')
    print(f'done {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
