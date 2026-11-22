"""KALIB-GO experiments (same truths and data as SAFE-GO, seeds 1000...).
E1: 30 inland readings plus n_e exact coastal readings; methods: Bayes (eta=1), SAFE-GO (SafeBayes,
    10 orders, first 10 losses skipped), BayesBag (bagged eta=1 posterior), KALIB-GO (eta calibrated on
    the toe interval by bootstrap) and the oracle that knows which readings are exact.
E2: three monitoring additions to a baseline with 60 coastal readings (as in SAFE-GO).
Usage: python3 kalibgo_exp.py NT
"""
import json, sys, time
import os
import sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'safe_go'))   # safego.py, safego_exp.py
from multiprocessing import Pool
import safego as S
import safego_exp as SE
import kalibgo as KG

METHODS = ['bayes', 'safe10', 'bag', 'kalib', 'oracle']

def summarize(ts, toe, w=None, s2=None, eta=1.0, extra=None):
    lo, hi = np.quantile(ts, [0.05, 0.95])
    d = dict(err=float(abs(np.median(ts) - toe) * S.D), cov=bool(lo <= toe <= hi), wid=float((hi - lo) * S.D),
             eta=float(eta), med=float(np.median(ts) * S.D))
    if w is not None:
        d['deg'] = float(np.sum(w * np.arange(S.P + 1))); d['s2'] = float(np.sum(w * s2))
    if extra:
        d.update(extra)
    return d

def fit(X, y, exact, toe, rng):
    out = {}
    fits = SE.fit_all(X, y, exact, rng)
    for k in ['bayes', 'safe10', 'oracle']:
        ts, w, s2, eta = fits[k]
        out[k] = summarize(ts, toe, w, s2, eta)
    Bm = S.basis(X)
    eta, cov, bag = KG.kalib(Bm, y, S.NIG(), rng)
    out['bag'] = summarize(bag, toe)
    ts, w, s2, ps = S.sample_goal(Bm, y, S.NIG(), eta, rng)
    out['kalib'] = summarize(ts, toe, w, s2, eta, {'bootcov': [float(c) for c in cov]})
    return out

def one_truth(seed):
    rng = np.random.default_rng(seed)
    K, q0, toe = SE.draw_truth(rng)
    phin = S.phi_true(SE.XIN, K, q0) + SE.SIG * rng.standard_normal(SE.M)
    rec = {'toe': float(toe * S.D), 'E1': {}, 'E2': {}}
    for ne in SE.NES:
        X = np.concatenate([np.zeros(ne), SE.XIN]); y = np.concatenate([np.zeros(ne), phin])
        ex = np.concatenate([np.ones(ne, bool), np.zeros(SE.M, bool)])
        rec['E1'][ne] = fit(X, y, ex, toe, rng)
    base = rec['E1'][SE.NE_BASE]
    c = base['safe10']['med'] / S.D
    near = np.clip(c + np.array([-0.08, -0.05, -0.02, 0.02, 0.05, 0.08]), 0.05, 0.9)
    spread = np.linspace(0.08, 0.87, 6)
    adds = {'coast': (np.zeros(120), np.zeros(120), np.ones(120, bool)),
            'near': (near, S.phi_true(near, K, q0) + SE.SIG * rng.standard_normal(6), np.zeros(6, bool)),
            'spread': (spread, S.phi_true(spread, K, q0) + SE.SIG * rng.standard_normal(6), np.zeros(6, bool))}
    X0 = np.concatenate([np.zeros(SE.NE_BASE), SE.XIN]); y0 = np.concatenate([np.zeros(SE.NE_BASE), phin])
    e0 = np.concatenate([np.ones(SE.NE_BASE, bool), np.zeros(SE.M, bool)])
    for name, (xa, ya, ea) in adds.items():
        rec['E2'][name] = fit(np.concatenate([X0, xa]), np.concatenate([y0, ya]), np.concatenate([e0, ea]), toe, rng)
    return rec

if __name__ == '__main__':
    NT = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    t0 = time.time()
    with Pool() as pool:
        recs = pool.map(one_truth, range(1000, 1000 + NT), chunksize=1)
    json.dump({'sig': SE.SIG, 'M': SE.M, 'NES': SE.NES, 'NE_BASE': SE.NE_BASE, 'B': KG.B_BOOT, 'recs': recs},
              open('kalibgo_runs.json', 'w'))
    print(f'{NT} truths in {time.time() - t0:.0f} s')
