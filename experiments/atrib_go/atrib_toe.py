"""ATRIB-GO, toe-monitoring designs: event-level PN when the factual toe position is observed every year
with noise sigx. The recharge path is inferred with a bootstrap particle filter that keeps the full
path of each particle (resampling only when the effective sample size drops below half); the
counterfactual (pumping kept at Q0) is then run on the weighted particle paths.
Uses the same test events as atrib_exp.py (same seed and order). Usage: python3 atrib_toe.py
"""
import json, sys, time
import numpy as np
from multiprocessing import Pool
import atrib as A

F0, F1 = 0.80, 0.90
NTEST = 300
NPART = 8000
SIGXS = [50.0, 100.0]

def pf_pn(args):
    j, yx, sigx, seed = args
    rng = np.random.default_rng(seed)
    P = A.P; s, th = P['s'], P['theta']
    a = np.exp(-A.DT / th); b = s * np.sqrt(1 - a * a)
    x0 = A.x0_of(F0); lam = F1 * A.LC
    n = NPART
    path = np.empty((n, A.NT + 1)); path[:, 0] = s * rng.standard_normal(n)
    X = np.full(n, x0); alive = np.ones(n, bool)
    logw = np.zeros(n); essmin = n; nres = 0
    obs_at = {int(round(k / A.DT)): i for i, k in enumerate(range(1, int(A.H) + 1))}
    for k in range(A.NT):
        x = X + A.DT * A.KR.drift(X, path[:, k], A.MU, lam, P)
        x = np.maximum(x, A.KR.XLO)
        hit = alive & (x >= A.KR.XESC); alive &= ~hit
        X = np.where(alive, x, A.KR.XESC)
        path[:, k + 1] = a * path[:, k] + b * rng.standard_normal(n)
        if (k + 1) in obs_at:
            y = yx[obs_at[k + 1]] / P['d']; sg = sigx / P['d']
            logw += -0.5 * ((X - y) / sg) ** 2
            w = np.exp(logw - logw.max()); w /= w.sum()
            ess = 1.0 / np.sum(w * w); essmin = min(essmin, ess)
            if ess < n / 2:
                u = (rng.random() + np.arange(n)) / n
                idx = np.minimum(np.searchsorted(np.cumsum(w), u), n - 1)
                path[:, :k + 2] = path[idx, :k + 2]; X = X[idx]; alive = alive[idx]
                logw = np.zeros(n); nres += 1
    w = np.exp(logw - logw.max()); w /= w.sum()
    E1 = ~alive
    if np.sum(w * E1) <= 0:
        return j, float('nan'), essmin, 0
    w = w * E1; w /= w.sum()
    E0, _, _ = A.run(path, F0, x0)
    distinct = len(np.unique(path[:, A.NT // 2]))
    return j, float(np.sum(w * (~E0))), float(essmin), distinct

if __name__ == '__main__':
    t0 = time.time()
    rng = np.random.default_rng(2026)
    # reproduce the test events of atrib_exp.py: same seed and the same draws in the same order
    eps = A.ou_paths(200000, rng)                      # reference ensemble (not used here)
    x0 = A.x0_of(F0)
    rec_steps = [int(round(k / A.DT)) for k in range(1, int(A.H) + 1)]
    teps = A.ou_paths(20000, rng)
    E1t, t1t, Xt = A.run(teps, F1, x0, record=rec_steps); E0t, _, _ = A.run(teps, F0, x0)
    idx = np.nonzero(E1t)[0][:NTEST]
    test_N = (~E0t[idx]).astype(float); test_X = Xt[idx] * A.P['d']
    R = json.load(open('atrib_results.json'))
    assert np.allclose(test_N, R['A2']['test_N']), 'test events differ from atrib_exp.py'
    obs_rng = np.random.default_rng(77)
    for sigx in SIGXS:
        jobs = [(j, test_X[j] + sigx * obs_rng.standard_normal(test_X.shape[1]), sigx, 1000 + j) for j in range(NTEST)]
        with Pool(4) as pool:
            out = pool.map(pf_pn, jobs, chunksize=4)
        out.sort()
        pn = np.array([o[1] for o in out]); essmin = np.array([o[2] for o in out]); dist = np.array([o[3] for o in out])
        ok = ~np.isnan(pn)
        pn = np.where(ok, pn, R['A2']['pn_pop'])
        p = np.clip(pn, 1e-12, 1 - 1e-12); Hb = -(p * np.log2(p) + (1 - p) * np.log2(1 - p))
        conf = (pn >= 0.9) | (pn <= 0.1)
        d = dict(H=float(Hb.mean()), brier=float(np.mean((pn - test_N) ** 2)), conf=float(conf.mean()),
                 acc_conf=float(np.mean((pn[conf] >= 0.5) == (test_N[conf] == 1))) if conf.any() else float('nan'),
                 mean=float(pn.mean()), ess_min_med=float(np.median(essmin)), distinct_mid_med=float(np.median(dist)),
                 failed=int((~ok).sum()), method='particle filter', pn=pn.tolist())
        R['A2']['designs'][f'toe_{int(sigx)}'] = d
        print(f'toe_{int(sigx)}', {k: v for k, v in d.items() if k != 'pn'}, flush=True)
    json.dump(A.json_clean(R), open('atrib_results.json', 'w'), indent=1, allow_nan=False)
    print(f'done in {time.time() - t0:.0f} s')
