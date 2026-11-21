"""Gate of the statistics code: the window-mean intervals of kaos_exp.py on synthetic stationary series with a known
correlation time (first-order autoregression), sampled as the runs are.  Writes res/stats_gate.json.

Expected: the estimated correlation time matches the true one; intervals with the measured correlation and a long record
cover about 90% or a little more; with a short record they under-cover when the correlation time is long; conformal
intervals cover about 90% in every case; intervals that assume one transit of memory under-cover.
The spread of the pooled coverage between single records (_sd, _min) says how far one real record may lie from 90% by
chance."""
import json
import os

import numpy as np

import kaos_exp as K

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(0)
T_STEPS, EVERY = 1920.0, 20
dt = EVERY / T_STEPS
n = int(1200 / dt)
out = []
for tau in (1.0, 2.5, 8.0, 30.0):       # 30 was added after the first long run had shown a correlation time of 33
    phi = np.exp(-dt / tau)
    res, taus, per_record = {}, [], {}
    for seed in range(24):
        e = rng.standard_normal(n) * np.sqrt(1 - phi ** 2)
        x = np.empty(n); x[0] = rng.standard_normal()
        for i in range(1, n):
            x[i] = phi * x[i - 1] + e[i]
        ts = 1.0 + 0.02 * x
        for burn in (50, 200):
            one = {}
            for W in (5, 10, 20):
                w = K.window_coverage(ts, 1.0, T_STEPS, EVERY, W, burn)
                for m in ('naive', 'gk', 'conformal'):
                    res.setdefault(f'{m}_{burn}', []).append((w[m], w['n_conf'] if m == 'conformal' else w['n']))
                    one.setdefault(m, []).append((w[m], w['n_conf'] if m == 'conformal' else w['n']))
            for m, v in one.items():                      # the pooled coverage of this one record, as for a real run
                per_record.setdefault(f'{m}_{burn}', []).append(sum(a * b for a, b in v) / sum(b for a, b in v))
        lrv, var, _ = K.long_run_variance(ts, len(ts) // 4)
        taus.append(0.5 * lrv / var * dt)
    rec = dict(tau=tau, tau_est=float(np.mean(taus)), tau_sd=float(np.std(taus)),
               **{k: float(sum(a * b for a, b in v) / sum(b for a, b in v)) for k, v in res.items()},
               # spread of the pooled coverage between single records of 1200 transit times
               **{k + '_sd': float(np.std(v, ddof=1)) for k, v in per_record.items()},
               **{k + '_min': float(np.min(v)) for k, v in per_record.items()},
               records=24)
    out.append(rec)
    print(rec)
json.dump(out, open(os.path.join(HERE, 'res', 'stats_gate.json'), 'w'), indent=1)
