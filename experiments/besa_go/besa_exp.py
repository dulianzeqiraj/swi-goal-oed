"""BESA-GO Monte Carlo study: is the frugal model honest, and what to do when it is not.

Scenarios (1000 data sets each; theta = (0.25, 0.45) unless 'null'):
  correct       common Gaussian copula, correct propensity models                      n = 1500, 6000
  pumpdep       the copula depends on season-2 pumping: rho2 = 0.30 (no pumping), 0.80 (pumping)   n = 1500, 6000
  pumpdep_null  the same with theta = 0                                                 n = 6000
  wrongprop     common copula; the season-2 policy has curvature in dryness and a dryness-by-alarm interaction that
                the main-effects propensity model misses                                n = 1500, 6000
  both          pumping-dependent copula and the wrong propensity model                 n = 6000
  skewdry       non-Gaussian copula: very dry years salinize disproportionately (exact causal margin)   n = 6000
Writes besa_mc.json. About 15 minutes on 4 cores; `python3 besa_exp.py pumpdep` reruns one scenario.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import json, sys, time, zlib
import numpy as np
from multiprocessing import Pool
import besa_model as M
import besa_est as B

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
R = 1000
SKEW = dict(rho1=(0.5, 0.5), rho2=(0.55, 0.55))
SCEN = {
    'correct': dict(past=M.PAST, causal=M.CAUSAL, cop=M.COMMON, copula='gauss', ns=[1500, 6000]),
    'pumpdep': dict(past=M.PAST, causal=M.CAUSAL, cop=M.PUMPDEP, copula='gauss', ns=[1500, 6000]),
    'pumpdep_null': dict(past=M.PAST, causal=M.NULL, cop=M.PUMPDEP, copula='gauss', ns=[6000]),
    'wrongprop': dict(past=M.WRONGPROP, causal=M.CAUSAL, cop=M.COMMON, copula='gauss', ns=[1500, 6000]),
    'both': dict(past=M.WRONGPROP, causal=M.CAUSAL, cop=M.PUMPDEP, copula='gauss', ns=[6000]),
    'skewdry': dict(past=M.PAST, causal=M.CAUSAL, cop=SKEW, copula='skewdry', ns=[6000]),
}


def one(args):
    name, n, rep = args
    sc = SCEN[name]
    rng = np.random.default_rng([zlib.crc32(name.encode()), n, rep])
    D = M.simulate(n, rng, past=sc['past'], causal=sc['causal'], cop=sc['cop'], copula=sc['copula'])
    try:
        o = B.besa(D)
    except Exception as e:                                # keep the run alive; failures are counted
        return None
    return [o[m] for m in B.METHODS], o['test'], o['rho_flex']


def summarize(rows, truth):
    ok = [r for r in rows if r is not None]
    est = np.array([r[0] for r in ok])                    # R x methods x 4
    tests = np.array([r[1] for r in ok])                  # R x 7
    rho = np.array([r[2] for r in ok])
    res = dict(n_ok=len(ok))
    for j, m in enumerate(B.METHODS):
        e, s = est[:, j, :2], est[:, j, 2:]
        res[m] = dict(mean=e.mean(0).tolist(), bias=(e.mean(0) - truth).tolist(), sd=e.std(0).tolist(),
                      rmse=np.sqrt(((e - truth) ** 2).mean(0)).tolist(), mean_se=np.nanmean(s, 0).tolist(),
                      cover=np.nanmean(np.abs(e - truth) <= 1.96 * s, 0).tolist(),
                      reject=np.nanmean(np.abs(e) > 1.96 * s, 0).tolist())
    res['tests'] = dict(hausman_common=float((tests[:, 1] < B.ALPHA).mean()), hausman_flex=float((tests[:, 3] < B.ALPHA).mean()),
                        lr=float((tests[:, 5] < B.ALPHA).mean()),
                        branch=[float((tests[:, 6] == b).mean()) for b in range(4)],
                        T_common_mean=float(tests[:, 0].mean()), LR_mean=float(tests[:, 4].mean()))
    res['rho_flex_mean'] = rho.mean(0).tolist()             # rho1(0), rho1(1), rho2(0), rho2(1)
    return res


def main(only=None):
    t0 = time.time()
    out = json.load(open('besa_mc.json'))['results'] if only and os.path.exists('besa_mc.json') else {}
    for sc in SCEN.values():                              # quasi-Monte Carlo table, inherited by the workers
        if sc['copula'] == 'skewdry':
            M._skew_table(sc['cop']['rho1'][0], sc['cop']['rho2'][0])
    with Pool(4) as pool:
        for name, sc in SCEN.items():
            if only and name not in only:
                continue
            truth = np.array([sc['causal']['theta1'], sc['causal']['theta2']])
            for n in sc['ns']:
                rows = pool.map(one, [(name, n, r) for r in range(R)], chunksize=10)
                s = summarize(rows, truth)
                out[f'{name}_n{n}'] = dict(scenario=name, n=n, truth=truth.tolist(), **s)
                print(f'{name} n={n} ({time.time() - t0:.0f}s, ok {s["n_ok"]}): ' + '  '.join(
                    f"{m} bias {s[m]['bias'][0]:+.3f}/{s[m]['bias'][1]:+.3f} rmse {s[m]['rmse'][0]:.3f}/{s[m]['rmse'][1]:.3f} "
                    f"cov {s[m]['cover'][0]:.2f}/{s[m]['cover'][1]:.2f} rej {s[m]['reject'][0]:.2f}/{s[m]['reject'][1]:.2f}"
                    for m in B.METHODS) + f"  tests {s['tests']}", flush=True)
                json.dump(dict(R=R, methods=B.METHODS, alpha=B.ALPHA, results=out), open('besa_mc.json', 'w'), indent=1)
    print(f'done {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main(sys.argv[1:] or None)
