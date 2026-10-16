"""KANAL-GO experiment. Writes kanal_results.json.
Population (200 000 wells x 10 years, twin outcomes): TE of three rules, capacity per alarm level, small-effect
approximations. Then 400 data sets of n = 500, 2 000, 8 000 well-years for each design (natural rotation,
balanced, balanced with a safety cap, observational records with back-door adjustment): bias, SD, RMSE and
coverage of the bootstrap bias-corrected estimate and basic interval (300 multinomial resamples), plus the
delta-method SD predicted by the small-sample theory."""
import json, time
import numpy as np
from multiprocessing import Pool
import kanal as K

NBIG, NS, REPS, B = 200000, [500, 2000, 8000], 400, 300
RS_PATH = None
for p in ('../rrjedha_go/rrjedha_results.json', '../rrjedha/rrjedha_results.json'):
    try:
        RS = json.load(open(p)); break
    except FileNotFoundError:
        continue
DB, DXB = np.array(RS['dbins']), np.array(RS['dxbins'])
W = None


def init():
    global W
    W = K.world(NBIG, np.random.default_rng(20261016), DB, DXB)


def setup():
    pdo, pr, pA = K.truth(W)
    rules = dict(op=pA, caut=np.array([0.9, 0.6, 0.2, 0.05]), bal=np.full(4, 0.5))
    designs = dict(natural=None, balanced=np.full(4, 0.5), capped=np.array([0.5, 0.5, 0.5, pA[3]]))
    return pdo, pr, pA, rules, designs


def pred_sd(pdo, pr, pi1, q1, n):
    """delta-method SD of the plug-in TE(pi) under randomized design q."""
    pi = K.rule(pi1); q = K.rule(q1); v = 0.0; th = np.zeros(K.NR)
    for r in range(K.NR):
        M = (pi[r][:, None] * pdo[:, r, :]).sum(0)
        for a in range(2):
            L = np.log2(pdo[a, r] / M); m = (pdo[a, r] * L).sum(); s2 = (pdo[a, r] * (L - m) ** 2).sum()
            v += pr[r] * pi[r, a] ** 2 * s2 / q[r, a]
            th[r] += pi[r, a] * m
    tot = (pr * th).sum(); v += (pr * (th - tot) ** 2).sum()
    return float(np.sqrt(v / n))


def job(args):
    n, seed = args
    rng = np.random.default_rng(seed)
    pdo, pr, pA, rules, designs = setup()
    idx = rng.integers(0, len(W['R']), n)
    out = {}
    co = K.obs_counts(W, idx)
    for g, p1 in rules.items():
        pi = K.rule(p1)
        bc, ci, raw = K.boot(co, lambda c: K.est_obs(c, pi), B, rng)
        out[f'obs|{g}'] = (raw, bc, ci)
        for dname, q1 in designs.items():
            qq = p1 if q1 is None else q1
            cnt = K.run_design(W, idx, qq, rng)
            bc, ci, raw = K.boot(cnt, lambda c: K.est_rand(c, pi), B, rng)
            out[f'{dname}|{g}'] = (raw, bc, ci)
    return out


if __name__ == '__main__':
    t0 = time.time()
    init()
    pdo, pr, pA, rules, designs = setup()
    C, pst = K.capacity(pdo); Cchi = K.chi2_cap(pdo)
    pop = {g: float(K.te_batch(pdo, K.rule(p1), pr)) for g, p1 in rules.items()}
    approx = {g: float((pr * 4 * p1 * (1 - p1) * C).sum()) for g, p1 in rules.items()}
    print('pA', pA.round(3), 'pop', {k: round(1000 * v, 2) for k, v in pop.items()}, 'approx', {k: round(1000 * v, 2) for k, v in approx.items()},
          'C', (1000 * C).round(2), 'Cchi', (1000 * Cchi).round(2), 'p*', pst.round(3), f'{time.time() - t0:.0f}s', flush=True)
    jobs = [(n, 70000 + 1000 * i + r) for i, n in enumerate(NS) for r in range(REPS)]
    with Pool(4, initializer=init) as pool:
        res = pool.map(job, jobs, chunksize=4)
    E = {}
    for i, n in enumerate(NS):
        rr = res[i * REPS:(i + 1) * REPS]
        for key in rr[0]:
            d, g = key.split('|'); th = pop[g]
            raw = np.array([o[key][0] for o in rr]); bc = np.array([o[key][1] for o in rr])
            cov = np.mean([o[key][2][0] <= th <= o[key][2][1] for o in rr])
            e = dict(raw_bias=float(raw.mean() - th), bias=float(bc.mean() - th), sd=float(bc.std()),
                     rmse=float(np.sqrt(np.mean((bc - th) ** 2))), cover=float(cov))
            if d != 'obs':
                q1 = rules[g] if designs[d] is None else designs[d]
                e['pred_sd'] = pred_sd(pdo, pr, rules[g], q1, n)
            E[f'{n}|{d}|{g}'] = e
        print(n, {k.split('|', 1)[1]: (round(1000 * v['bias'], 2), round(1000 * v['sd'], 2), round(v['cover'], 3), round(1000 * v.get('pred_sd', np.nan), 2))
                  for k, v in E.items() if k.startswith(f'{n}|')}, f'{time.time() - t0:.0f}s', flush=True)
    json.dump(dict(pop=pop, approx=approx, C=C.tolist(), Cchi=Cchi.tolist(), pstar=pst.tolist(), pA=pA.tolist(), pr=pr.tolist(),
                   pdo=pdo.tolist(), rules={k: v.tolist() for k, v in rules.items()},
                   designs={k: (None if v is None else v.tolist()) for k, v in designs.items()},
                   E=E, P=dict(NBIG=NBIG, NS=NS, REPS=REPS, B=B, ALPHA=K.ALPHA)),
              open('kanal_results.json', 'w'), indent=1, allow_nan=False)
    print(f'done in {time.time() - t0:.0f}s')
