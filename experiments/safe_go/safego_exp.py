"""SAFE-GO experiments.
E1: toe of the saltwater interface from 30 inland potential readings plus n_e exact coastal readings
    (Phi=0 at x=0); Bayes (eta=1) vs SafeBayes (R-log) vs oracle (knows which readings are exact).
E2: data worth of three monitoring additions to a baseline (30 inland + 30 coastal):
    (a) +90 coastal readings, (b) +6 wells near the current toe estimate, (c) +6 wells spread out.
Usage: python3 safego_exp.py NT
"""
import json, sys, time
import numpy as np
from multiprocessing import Pool
import safego as S

SIG = 0.7          # inland noise sd [m^2]
M = 30             # inland wells
XIN = np.linspace(0.05, 0.9, M)
NES = [0, 15, 30, 60, 120, 240]
NE_BASE = 60       # coastal readings in the E2 baseline
W_EXACT = 1e4      # oracle precision weight of exact coastal readings

def draw_truth(rng):
    while True:
        K = 100 * np.exp(0.3 * rng.standard_normal()); q0 = 1.5 * np.exp(0.2 * rng.standard_normal())
        toe = S.first_root(S.phi_true(S.XG, K, q0)[None])[0]
        if 0.3 <= toe <= 0.8:
            return K, q0, toe

def summarize(ts, toe, w, s2, eta):
    lo, hi = np.quantile(ts, [0.05, 0.95])
    return dict(err=float(abs(np.median(ts) - toe) * S.D), cov=bool(lo <= toe <= hi), wid=float((hi - lo) * S.D),
                deg=float(np.sum(w * np.arange(S.P + 1))), s2=float(np.sum(w * s2)), eta=float(eta),
                med=float(np.median(ts) * S.D))

def fit_all(X, y, exact, rng):
    """bayes: eta=1; safe: SafeBayes, one random order, all losses (as in the original method);
    safe10: SafeBayes averaged over 10 orders with the first 10 losses skipped (SAFE-GO setting);
    oracle: knows the coastal readings are exact, so uses them as one exact constraint."""
    prior = S.NIG()
    B = S.basis(X)
    out = {}
    eta1, _ = S.safebayes_eta(B, y, prior, rng)
    eta10, _ = S.safebayes_eta(B, y, prior, rng, start=10, nperm=10)
    for key, eta in [('bayes', 1.0), ('safe', eta1), ('safe10', eta10)]:
        ts, w, s2, ps = S.sample_goal(B, y, prior, eta, rng)
        out[key] = (ts, w, s2, eta)
    keep = ~exact
    Xo = np.concatenate([[0.0], X[keep]]); yo = np.concatenate([[0.0], y[keep]])
    wo = np.concatenate([[W_EXACT], np.ones(keep.sum())])
    ts, w, s2, ps = S.sample_goal(S.basis(Xo), yo, prior, 1.0, rng, wts=wo)
    out['oracle'] = (ts, w, s2, 1.0)
    return out

def one_truth(seed):
    rng = np.random.default_rng(seed)
    K, q0, toe = draw_truth(rng)
    phin = S.phi_true(XIN, K, q0) + SIG * rng.standard_normal(M)
    rec = {'toe': float(toe * S.D), 'E1': {}, 'E2': {}}
    for ne in NES:
        X = np.concatenate([np.zeros(ne), XIN]); y = np.concatenate([np.zeros(ne), phin])
        ex = np.concatenate([np.ones(ne, bool), np.zeros(M, bool)])
        fits = fit_all(X, y, ex, rng)
        rec['E1'][ne] = {k: summarize(ts, toe, w, s2, eta) for k, (ts, w, s2, eta) in fits.items()}
    # E2: baseline = 30 coastal readings; additions use the SafeBayes toe estimate for placement
    base = rec['E1'][NE_BASE]
    c = base['safe10']['med'] / S.D
    near = np.clip(c + np.array([-0.08, -0.05, -0.02, 0.02, 0.05, 0.08]), 0.05, 0.9)
    spread = np.linspace(0.08, 0.87, 6)
    adds = {'coast': (np.zeros(120), np.zeros(120), np.ones(120, bool)),
            'near': (near, S.phi_true(near, K, q0) + SIG * rng.standard_normal(6), np.zeros(6, bool)),
            'spread': (spread, S.phi_true(spread, K, q0) + SIG * rng.standard_normal(6), np.zeros(6, bool))}
    X0 = np.concatenate([np.zeros(NE_BASE), XIN]); y0 = np.concatenate([np.zeros(NE_BASE), phin]); e0 = np.concatenate([np.ones(NE_BASE, bool), np.zeros(M, bool)])
    for name, (xa, ya, ea) in adds.items():
        fits = fit_all(np.concatenate([X0, xa]), np.concatenate([y0, ya]), np.concatenate([e0, ea]), rng)
        rec['E2'][name] = {k: summarize(ts, toe, w, s2, eta) for k, (ts, w, s2, eta) in fits.items()}
    return rec

if __name__ == '__main__':
    NT = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    t0 = time.time()
    with Pool() as pool:
        recs = pool.map(one_truth, range(1000, 1000 + NT))
    json.dump({'sig': SIG, 'M': M, 'NES': NES, 'NE_BASE': NE_BASE, 'recs': recs}, open('safego_runs.json', 'w'))
    print(f'{NT} truths in {time.time() - t0:.0f} s')
