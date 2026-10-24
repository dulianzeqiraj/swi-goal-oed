"""FILLIMI-GO, part 2: the tail exponents of the initial-condition influence (Theorem F, parts iii and v).
A mobile-head goal pinned by the sea boundary sees a power-law memory of index beta through t^-(beta+2)
(boundary screening); a goal inside the storage (a piezometer in the clay) sees it through t^-beta.
Long horizon (10^2-10^4 yr) and rates down to 1e-7 /yr so that the asymptotic regime is reached."""
import json
import os

import numpy as np

from fillimi import P, build, spectral

HERE = os.path.dirname(os.path.abspath(__file__))
out, log = {}, []
times = np.logspace(2, 4, 40)
for beta in (0.3, 0.5, 0.7):
    Pb = dict(P, beta=beta, a_min=1e-7, a_max=1.0, K=36, N=30)
    S = build('power', Pb)
    lam, U, Wh = spectral(S)
    N, dx, K = S['N'], Pb['L'] / Pb['N'], S['K']
    res = {}
    for gname, kind, xg in (('mobile 1000 m', 'm', 1000.0), ('mobile 4750 m', 'm', 4750.0), ('clay 2500 m', 'c', 2500.0)):
        i = int(xg // dx)
        g = np.zeros(S['n'])
        if kind == 'm':
            g[i] = 1.0
        else:
            for k in range(K):
                g[N * (k + 1) + i] = S['s'][k] / S['s'].sum()
        left = (g / Wh) @ U
        nu = left ** 2                              # white prior in the storage-weighted norm (phi = 1)
        v = np.array([np.sum(nu * np.exp(-2 * lam * t)) for t in times])
        slope = float(np.polyfit(np.log(times), np.log(v), 1)[0])
        res[gname] = slope
        log.append(f"beta={beta}  {gname:14s} fitted exponent {slope:6.2f}   theory {-(beta + 2) if kind == 'm' else -beta:5.2f}")
    out[str(beta)] = res
json.dump(out, open(os.path.join(HERE, 'fillimi_tails.json'), 'w'), indent=1)
open(os.path.join(HERE, 'fillimi_tails.log'), 'w').write('\n'.join(log) + '\n')
print('\n'.join(log))
