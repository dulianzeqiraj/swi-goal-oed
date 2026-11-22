"""ATRIB-GO experiments.
A1: population-level attribution (p1, p0, PN, PS) for several pumping increases, with twin worlds.
A2: event-level probability of necessity PN(data) = P(no event under Q0 | event under Q1, data) for one
    pumping increase (0.80 -> 0.90 Qc) and several monitoring designs:
      none        - event only (population PN)
      time        - event and its date
      rain        - event, date and block means of the recharge anomaly with noise sig (several sig, periods)
      toe         - event, date and annual toe positions (factual world) with noise 50 m
    Design worth = expected reduction of the binary entropy of the attribution.
Usage: python3 atrib_exp.py
"""
import json, sys, time
import numpy as np
from multiprocessing import Pool
import atrib as A

F0, F1 = 0.80, 0.90
PAIRS = [(0.70, 0.85), (0.75, 0.90), (0.80, 0.90), (0.85, 0.95)]
NREF = 200000          # reference ensemble (population level, time and toe designs)
NTEST = 300            # test events
NPOST = 1500           # posterior recharge paths per test event
DTAU = 1.0             # tolerance on the event date [yr]
SIGXS = [50.0, 100.0]  # toe observation noise [m]
RAIN = [('rain_y_0.10', 1.0, 0.10), ('rain_y_0.05', 1.0, 0.05), ('rain_y_0.02', 1.0, 0.02), ('rain_q_0.02', 0.25, 0.02)]

def h2(p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))

def summarize(pn, N):
    pn = np.asarray(pn, float); N = np.asarray(N, float)
    conf = (pn >= 0.9) | (pn <= 0.1)
    acc = np.mean((pn[conf] >= 0.5) == (N[conf] == 1)) if conf.any() else np.nan
    return dict(H=float(np.mean(h2(pn))), brier=float(np.mean((pn - N) ** 2)), conf=float(np.mean(conf)),
                acc_conf=float(acc), mean=float(np.mean(pn)))

def rain_job(args):
    name, period, sig, test_eps, test_tau, seed = args
    rng = np.random.default_rng(seed)
    RC = A.RechargeConditioner(period, sig)
    x0 = A.x0_of(F0)
    out = []; acc_rate = []
    for j in range(test_eps.shape[0]):
        y = RC.observe(test_eps[j:j + 1], rng)[0]
        post = RC.posterior(y, NPOST, rng)
        E1, t1, _ = A.run(post, F1, x0)
        keep = E1 & (np.abs(t1 - test_tau[j]) <= DTAU)
        if keep.sum() < 20:                 # fall back to the event only
            keep = E1
        E0, _, _ = A.run(post[keep], F0, x0)
        out.append(float(np.mean(~E0))); acc_rate.append(float(keep.mean()))
    return name, out, float(np.median(acc_rate))

if __name__ == '__main__':
    t0 = time.time()
    rng = np.random.default_rng(2026)
    res = {'F0': F0, 'F1': F1, 'H': A.H, 'Qc': A.QC, 'A1': [], 'A2': {}}
    # ---------------- A1: population level, several pumping increases
    eps = A.ou_paths(NREF, rng)
    for f0, f1 in PAIRS:
        x0 = A.x0_of(f0)
        E1, t1, _ = A.run(eps, f1, x0); E0, _, _ = A.run(eps, f0, x0)
        p1, p0 = E1.mean(), E0.mean()
        res['A1'].append(dict(f0=f0, f1=f1, p1=float(p1), p0=float(p0), pn=float(1 - p0 / p1),
                              pn_twin=float((E1 & ~E0).sum() / E1.sum()), ps=float(1 - (1 - p1) / (1 - p0)),
                              viol=float((E0 & ~E1).mean())))
        print('A1', res['A1'][-1], flush=True)
    # ---------------- reference ensemble for (F0, F1): event dates and annual toe records
    x0 = A.x0_of(F0)
    rec_steps = [int(round(k / A.DT)) for k in range(1, int(A.H) + 1)]
    E1r, t1r, Xr = A.run(eps, F1, x0, record=rec_steps); E0r, _, _ = A.run(eps, F0, x0)
    ref = E1r
    Nref = (~E0r)[ref].astype(float); tref = t1r[ref]; Xref = Xr[ref] * A.P['d']
    pn_pop = float(Nref.mean())
    print('reference events', ref.sum(), 'PN', pn_pop, flush=True)
    # PN as a function of the event date (kernel smoothing over the reference events)
    tg = np.arange(0.5, A.H, 1.0)
    pn_t = [float(np.average(Nref, weights=np.exp(-0.5 * ((tref - t) / 1.0) ** 2))) for t in tg]
    cnt_t = [int(np.sum(np.abs(tref - t) <= 0.5)) for t in tg]
    res['A2']['pn_of_t'] = dict(t=tg.tolist(), pn=pn_t, count=cnt_t)
    # ---------------- test events (fresh paths)
    teps = A.ou_paths(20000, rng)
    E1t, t1t, Xt = A.run(teps, F1, x0, record=rec_steps); E0t, _, _ = A.run(teps, F0, x0)
    idx = np.nonzero(E1t)[0][:NTEST]
    test_eps = teps[idx]; test_tau = t1t[idx]; test_N = (~E0t[idx]).astype(float); test_X = Xt[idx] * A.P['d']
    designs = {}
    designs['none'] = summarize(np.full(NTEST, pn_pop), test_N)
    kw = lambda t: np.exp(-0.5 * ((tref - t) / 1.0) ** 2)
    pn_time = [float(np.average(Nref, weights=kw(t))) for t in test_tau]
    designs['time'] = summarize(pn_time, test_N)
    # toe design: importance weights over the reference events (date implied by the absorbed toe)
    for sigx in SIGXS:
        pn_toe, ess = [], []
        for j in range(NTEST):
            yx = test_X[j] + sigx * rng.standard_normal(test_X.shape[1])
            ll = -0.5 * np.sum((Xref - yx[None, :]) ** 2, axis=1) / sigx ** 2
            w = np.exp(ll - ll.max()); w /= w.sum()
            pn_toe.append(float(np.sum(w * Nref))); ess.append(float(1.0 / np.sum(w * w)))
        key = f'toe_{int(sigx)}'
        designs[key] = summarize(pn_toe, test_N); designs[key]['ess_med'] = float(np.median(ess))
        designs[key]['ess_p10'] = float(np.percentile(ess, 10)); designs[key]['pn'] = pn_toe
        print(key, designs[key], flush=True)
    # rain designs (exact Gaussian conditioning of the recharge path), in parallel
    jobs = [(name, per, sig, test_eps, test_tau, 100 + i) for i, (name, per, sig) in enumerate(RAIN)]
    with Pool(4) as pool:
        for name, pn, accr in pool.map(rain_job, jobs):
            designs[name] = summarize(pn, test_N); designs[name]['accept_med'] = accr
            designs[name]['pn'] = pn
            print(name, designs[name]['H'], flush=True)
    designs['time']['pn'] = pn_time
    res['A2']['designs'] = designs
    res['A2']['test_N'] = test_N.tolist(); res['A2']['test_tau'] = test_tau.tolist()
    res['A2']['pn_pop'] = pn_pop; res['A2']['H_prior'] = float(h2(pn_pop))
    json.dump(A.json_clean(res), open('atrib_results.json', 'w'), indent=1, allow_nan=False)
    for k, v in designs.items():
        print(f"{k:12s} H {v['H']:.3f}  brier {v['brier']:.3f}  conf {v['conf']:.2f}  acc {v['acc_conf']:.2f}")
    print(f'done in {time.time() - t0:.0f} s')
