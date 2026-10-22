"""KURSIM-GO Monte Carlo study: six estimators of the MSM (theta1, theta2) in frugal pumping-chloride data.

Scenarios (1000 replications each):
  effect          baseline past and policy, theta = (0.25, 0.45), Gaussian copula; n = 300, 1500
  null            the same with theta = (0, 0); n = 300, 1500
  null_strong     strong alarm feedback (g1 = 2, g2 = 2.5, rho = (0.2, 0.8), b3 = -3), theta = (0, 0); n = 1500, 6000
  effect_tcopula  theta = (0.25, 0.45) with a Student-t copula (4 d.f.): the Gaussian frugal likelihood is misspecified;
                  n = 1500
Writes kursim_mc.json. About 8 minutes on 4 cores; `python3 kursim_exp.py effect_tcopula` reruns one scenario.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import json, time, zlib
import numpy as np
from multiprocessing import Pool
import kursim_model as K
import kursim_est as E

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
R = 1000
NULL = dict(K.CAUSAL, theta1=0.0, theta2=0.0)
STRONG = dict(K.PAST, g1=2.0, g2=2.5, b3=-3.0)
SCEN = {
    'effect': dict(past=K.PAST, causal=K.CAUSAL, cop=K.COPULA, copula='gauss', ns=[300, 1500]),
    'null': dict(past=K.PAST, causal=NULL, cop=K.COPULA, copula='gauss', ns=[300, 1500]),
    'null_strong': dict(past=STRONG, causal=NULL, cop=dict(rho1=0.2, rho2=0.8), copula='gauss', ns=[1500, 6000]),
    'effect_tcopula': dict(past=K.PAST, causal=K.CAUSAL, cop=K.COPULA, copula='t', ns=[1500]),
}


def one(args):
    name, n, rep = args
    sc = SCEN[name]
    rng = np.random.default_rng([zlib.crc32(name.encode()), n, rep])
    D = K.simulate(n, rng, past=sc['past'], causal=sc['causal'], cop=sc['cop'], copula=sc['copula'])
    D.pop('pi')
    out = E.all_estimates(D, rng)
    return [out[m] for m in E.METHODS]


def summarize(arr, truth):
    est, se = arr[:, :, :2], arr[:, :, 2:]
    res = {}
    for j, m in enumerate(E.METHODS):
        e, s = est[:, j], se[:, j]
        res[m] = dict(
            mean=e.mean(0).tolist(), bias=(e.mean(0) - truth).tolist(), sd=e.std(0).tolist(),
            rmse=np.sqrt(((e - truth) ** 2).mean(0)).tolist(), mean_se=np.nanmean(s, 0).tolist(),
            cover=np.nanmean(np.abs(e - truth) <= 1.96 * s, 0).tolist(),
            reject=np.nanmean(np.abs(e) > 1.96 * s, 0).tolist())
    return res


def main(only=None):
    """Run every scenario, or only the named ones (merged into an existing kursim_mc.json)."""
    t0 = time.time()
    out = json.load(open('kursim_mc.json'))['results'] if only and os.path.exists('kursim_mc.json') else {}
    K._t_margin(K.COPULA['rho1'], K.COPULA['rho2'], 4.0)       # table of the t margin, inherited by the workers
    with Pool(4) as pool:
        for name, sc in SCEN.items():
            if only and name not in only:
                continue
            truth = np.array([sc['causal']['theta1'], sc['causal']['theta2']])
            for n in sc['ns']:
                arr = np.array(pool.map(one, [(name, n, r) for r in range(R)], chunksize=10))
                out[f'{name}_n{n}'] = dict(scenario=name, n=n, truth=truth.tolist(), **summarize(arr, truth))
                s = out[f'{name}_n{n}']
                print(f'{name} n={n} ({time.time() - t0:.0f}s): ' + '  '.join(
                    f"{m} bias {s[m]['bias'][0]:+.3f}/{s[m]['bias'][1]:+.3f} rmse {s[m]['rmse'][0]:.3f}/{s[m]['rmse'][1]:.3f} "
                    f"cov {s[m]['cover'][0]:.2f}/{s[m]['cover'][1]:.2f} rej {s[m]['reject'][0]:.2f}/{s[m]['reject'][1]:.2f}"
                    for m in E.METHODS), flush=True)
    json.dump(dict(R=R, methods=E.METHODS, results=out, past=K.PAST, causal=K.CAUSAL, copula=K.COPULA,
                   strong=dict(past=STRONG, cop=dict(rho1=0.2, rho2=0.8))), open('kursim_mc.json', 'w'), indent=1)
    print(f'done {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:] or None)
