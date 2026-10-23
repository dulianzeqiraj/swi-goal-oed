"""BESA-GO asymptotics along a path of copulas: rho2 = 0.55 - gap/2 without season-2 pumping and 0.55 + gap/2 with it.

For each gap, one large simulated data set (N = 300 000 wells) gives
  * the limits of the common-copula MLE, the pumping-dependent MLE and the frugal-augmented doubly robust estimate;
  * the per-observation noncentralities of the Hausman test (d' V1^-1 d, V1 the covariance of the difference of the
    influence functions) and of the likelihood-ratio test (LR / N);
  * the asymptotic power at sample size n, P(chi2_2(n * kappa) > chi2_2,0.95), for any n.
Writes besa_curve.json (about 6 minutes on 4 cores).
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import json, time
import numpy as np
from multiprocessing import Pool
import besa_model as M
import besa_est as B

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
N = 300_000
GAPS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]


def one(gap):
    cop = dict(rho1=(0.35, 0.35), rho2=(0.55 - gap / 2, 0.55 + gap / 2))
    D = M.simulate(N, np.random.default_rng([2026, int(round(100 * gap))]), cop=cop)
    X1, X2 = B.design(D)
    props = (B.logit_fit(X1, D['A1']), B.logit_fit(X2, D['A2']))
    fc = B.fit_frugal(D, 'common')
    ff = B.fit_frugal(D, 'flex', start=np.r_[fc['v'], fc['v'][7:9]])
    dc = B.dr_frugal(D, fc, props)
    d = dc['theta'] - fc['theta']
    Dl = dc['IF'] - fc['IF'][:, 4:6]
    kH = float(d @ np.linalg.solve(np.cov(Dl.T), d))
    kLR = max(2 * (ff['ll'] - fc['ll']), 0.0) / N
    return dict(gap=gap, rho2=list(cop['rho2']), mle_common=fc['theta'].tolist(), mle_flex=ff['theta'].tolist(),
                drf_common=dc['theta'].tolist(), se1_common=(fc['se'] * np.sqrt(N)).tolist(),
                se1_drf=(dc['se'] * np.sqrt(N)).tolist(), kappa_hausman=kH, kappa_lr=kLR)


if __name__ == '__main__':
    t0 = time.time()
    with Pool(4) as pool:
        res = pool.map(one, GAPS)
    json.dump(dict(N=N, truth=[M.CAUSAL['theta1'], M.CAUSAL['theta2']], curve=res), open('besa_curve.json', 'w'), indent=1)
    for r in res:
        print(f"gap {r['gap']:.1f}: mle_common {r['mle_common'][0]:.4f}/{r['mle_common'][1]:.4f} flex {r['mle_flex'][0]:.4f}/{r['mle_flex'][1]:.4f} "
              f"drf {r['drf_common'][0]:.4f}/{r['drf_common'][1]:.4f} kH {r['kappa_hausman']:.2e} kLR {r['kappa_lr']:.2e}")
    print(f'done {time.time() - t0:.0f}s')
