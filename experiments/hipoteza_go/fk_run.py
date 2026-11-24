"""HIPOTEZA-GO on the Fushe-Kuqe data (four analyses of Cenameri & Beqiraj 2016 and three documented head facts).
Writes res_fk/fk_results.json (not in git).
usage: python fk_run.py [workers] [variant]      variant 'second' (wells 341 and 503 in the second aquifer, as in
the chloride manuscript) or 'shallow'"""
import itertools
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

import fk_infer as I

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res_fk')
E = COLS = SCR = None
VARIANT = os.environ.get('FK_VARIANT', 'second')
N_MIN, CUT = 39, 2.5


def _init():
    global E, COLS, SCR
    z = np.load(os.path.join(RES, 'ensemble_fk.npz'))
    ok = z['ok'] & np.isfinite(z['h_lit'])
    n = len(ok)
    E = {k: (z[k][ok] if (z[k].ndim and z[k].shape[0] == n) else z[k]) for k in z.files}
    COLS = I.bands(E)
    SCR = [w[3] for w in I.WELLS] if VARIANT == 'second' else [0, 0, 0, 0]


def lower_all(lib, y, eps, kh, members):
    lo, hi = I.box(lib)
    lb = np.empty(len(members))
    for n, j in enumerate(members):
        if kh[j] > CUT:
            lb[n] = kh[j]
        else:
            lb[n] = max(kh[j], I.kappa_lower(I.responses(E, j, COLS, SCR), y, eps, lo, hi))
    return lb


def kappa_min(lib, y, eps, kh, members, floor=None, stop_below=0.0):
    """Smallest kappa of a library over the members (visited in the order of a lower bound, stopped when the bound
    reaches the best value, or when the best value is below `stop_below`: then the result is an upper bound that is
    still below it).  floor: an extra lower bound per member (e.g. the kappa of a larger library)."""
    lo, hi = I.box(lib)
    lb = lower_all(lib, y, eps, kh, members)
    if floor is not None:
        lb = np.maximum(lb, floor)
    best, arg = np.inf, -1
    for n in np.argsort(lb):
        if lb[n] >= best or lb[n] > CUT or best <= stop_below:
            break
        j = members[n]
        k = max(kh[j], I.kappa_milp(I.responses(E, j, COLS, SCR), y, eps, lo, hi))
        if k < best:
            best, arg = k, int(j)
    if best > CUT:
        return float(max(CUT, lb.min())), -1, True
    return float(best), arg, False


def job_loo(a):
    """Leave one member out: it generates data (random strengths, random positions in the bands, noise; its heads
    plus noise as the facts); the smallest kappa of the other members with the library of the truth."""
    seed, n = a
    rng = np.random.default_rng(seed)
    kh_real = I.kappa_head(E)
    cand = np.flatnonzero(kh_real <= 2.0)
    hv = I.head_values(E)
    out = []
    for _ in range(n):
        j0 = int(rng.choice(cand))
        S = np.array([rng.uniform(*I.S_INT[0]), rng.uniform(*I.S_INT[1]), rng.uniform(*I.S_INT[2]),
                      0.0 if rng.uniform() < 0.3 else rng.uniform(0.02, 0.25),
                      0.0 if rng.uniform() < 0.3 else rng.uniform(0.002, 0.03),
                      0.0 if rng.uniform() < 0.3 else rng.uniform(0.1, 3.0)])
        lib = [0, 2] + [k for k in (1, 3, 4, 5) if S[k] > 0
                        and not (k == 1 and E['vL'][j0] <= 0) and not (k == 3 and E['n_an'][j0] <= 0)]
        pos = [int(rng.choice(c)) for c in COLS]
        G0 = I.responses(E, j0, [[p] for p in pos], SCR)
        yt = np.array([g[0] @ S for g in G0])
        yt = np.maximum(yt + rng.standard_normal(len(yt)) * (I.CL_SD[0] * yt + I.CL_SD[1]), 0.5)
        et = I.K_EPS * (I.CL_SD[0] * yt + I.CL_SD[1])
        facts = [(k, float(hv[k][j0] + rng.normal() * sd), sd) for (k, v, sd) in I.FACTS]
        kh = I.kappa_head(E, facts)
        members = np.delete(np.arange(len(kh)), j0)
        k, _, cens = kappa_min(lib, yt, et, kh, members, stop_below=1.0)     # only values above 1 matter
        out.append(dict(j0=j0, kmin=k, censored=cens, lib=lib))
    return out


def job_kappa(a):
    """kappa of the members of a chunk, full library, real data (lower bounds above CUT)."""
    chunk, = a
    y, eps = I.data()
    kh = I.kappa_head(E)
    lo, hi = I.box(I.FULL)
    out = []
    for j in chunk:
        out.append(I.kappa_member(E, j, I.FULL, y, eps, COLS, SCR, kh[j], CUT))
    return out


def job_sub(a):
    lib, kfull = a
    y, eps = I.data()
    kh = I.kappa_head(E)
    members = np.arange(len(kh))
    return lib, kappa_min(lib, y, eps, kh, members, floor=kfull)


SH_SRC = [0, 1, 3, 4, 5]


def job_shares(a):
    """Share bounds of one member: all pairs (spec None) or only the listed (sample, source, senses)."""
    j, kap, spec = a
    y, eps = I.data()
    G = I.responses(E, j, COLS, SCR)
    lo, hi = I.box(I.FULL)
    out = {}
    for i in range(len(I.WELLS)):
        if spec is None:
            out[i] = I.share_bounds(G, y, eps, kap, lo, hi, i, SH_SRC)
        elif spec.get(i):
            out[i] = I.share_bounds(G, y, eps, kap, lo, hi, i, list(spec[i]), senses=spec[i])
    return int(j), out


def union_shares(pool, mem, keff, n_full=30, seed=7):
    """Union of the share bounds over the members.  The first n_full members (random order) get every pair; after
    that only the pairs that still carry a statement (lower bound above 1/2, upper bound below 0.1) are followed, in
    the direction of the statement; the other pairs keep the union of the first n_full and are flagged incomplete."""
    order = np.random.default_rng(seed).permutation(mem)
    nw = len(I.WELLS)
    lo = {(i, k): 1.0 for i in range(nw) for k in SH_SRC}; hi = {(i, k): 0.0 for i in range(nw) for k in SH_SRC}
    first, rest = order[:n_full], order[n_full:]
    for j, b in pool.imap_unordered(job_shares, [(j, keff, None) for j in first]):
        for i, d in b.items():
            if d is None:
                continue
            for k, (l_, h_) in d.items():
                lo[(i, k)] = min(lo[(i, k)], l_); hi[(i, k)] = max(hi[(i, k)], h_)
    spec = {}
    for (i, k) in lo:
        sn = tuple(x for x, ok in (('min', lo[(i, k)] > 0.5), ('max', hi[(i, k)] < 0.1)) if ok)
        if sn:
            spec.setdefault(i, {})[k] = sn
    complete = {p: len(rest) == 0 for p in lo}
    for i, d in spec.items():
        for k in d:
            complete[(i, k)] = True
    if len(rest) and spec:
        for j, b in pool.imap_unordered(job_shares, [(j, keff, spec) for j in rest]):
            for i, d in b.items():
                if d is None:
                    continue
                for k, (l_, h_) in d.items():
                    if np.isfinite(l_):
                        lo[(i, k)] = min(lo[(i, k)], l_)
                    if np.isfinite(h_):
                        hi[(i, k)] = max(hi[(i, k)], h_)
    return lo, hi, complete


def main(workers=4):
    t0 = time.time()
    _init()
    M = len(E['h_lit'])
    y, eps = I.data()
    out = dict(variant=VARIANT, M=M, y=y.tolist(), eps=eps.tolist(), bands=[c.tolist() for c in COLS], screens=SCR)
    # ---------------- calibration: the head facts
    hv = I.head_values(E)
    kf = {k: (np.abs(hv[k] - v) / (I.K_EPS * sd)) for (k, v, sd) in I.FACTS}
    kh = I.kappa_head(E)
    out['facts'] = {k: dict(target=v, sd=sd, n_within=int((kf[k] <= 1).sum()),
                            q=np.quantile(hv[k], [0.05, 0.5, 0.95]).tolist()) for (k, v, sd) in I.FACTS}
    pairs = {}
    for a_, b_ in itertools.combinations([f[0] for f in I.FACTS], 2):
        pairs[a_ + '+' + b_] = int(((kf[a_] <= 1) & (kf[b_] <= 1)).sum())
    out['facts_pairs'] = pairs
    out['n_heads_all'] = int((kh <= 1).sum())
    print('facts', {k: v['n_within'] for k, v in out['facts'].items()}, 'pairs', pairs, 'all', out['n_heads_all'],
          f'{time.time() - t0:.0f}s', flush=True)
    with Pool(workers, initializer=_init) as pool:
        # ---------------- tolerance factor by leaving members out
        res = pool.map(job_loo, [(300 + b, 10) for b in range(4)], chunksize=1)
        loo = [r for rr in res for r in rr]
        kres = float(max(1.0, np.quantile([r['kmin'] for r in loo], 0.9)))
        out['loo'] = dict(kmin=[r['kmin'] for r in loo], censored=int(sum(r['censored'] for r in loo)),
                          kappa_res=kres)
        print('kappa_res', round(kres, 2), 'censored', out['loo']['censored'], f'{time.time() - t0:.0f}s', flush=True)
        # ---------------- full library, every member
        chunks = np.array_split(np.arange(M), 4 * workers)
        kap = np.concatenate(pool.map(job_kappa, [(c,) for c in chunks], chunksize=1))
        kmin = float(kap.min())
        out['full'] = dict(kappa_min=kmin, falsified=bool(kmin > kres), n_within=int((kap <= kres).sum()))
        print('full library: kappa_min', round(kmin, 3), 'members within', out['full']['n_within'],
              f'{time.time() - t0:.0f}s', flush=True)
        # ---------------- sub-libraries: sea and fresh recharge always, any subset of LG, AN, RS, DB
        libs = []
        for r in range(5):
            for comb in itertools.combinations((1, 3, 4, 5), r):
                libs.append(sorted(I.BASE + list(comb)))
        res = pool.map(job_sub, [(lib, kap) for lib in libs], chunksize=1)
        out['libraries'] = [dict(lib=[I.SRC[k] for k in lib], kappa_min=r[0], best=r[1], censored=r[2],
                                 feasible=bool(r[0] <= kres)) for lib, r in res]
        print('libraries done', f'{time.time() - t0:.0f}s', flush=True)
        for d in out['libraries']:
            print('   ', ' '.join(d['lib']), round(d['kappa_min'], 3), 'feasible' if d['feasible'] else 'FALSIFIED')
        if os.environ.get('FK_SHARES', '1') == '0':           # library tests only (sensitivity runs)
            out['seconds'] = time.time() - t0
            out['kappa_full'] = kap.tolist(); out['kappa_head'] = kh.tolist()
            json.dump(out, open(os.path.join(RES, f'fk_results_{VARIANT}.json'), 'w'), indent=1)
            print('all done (no shares)', f'{out["seconds"]:.0f}s')
            return
        # ---------------- the union of the full library
        ks = np.sort(kap)
        keff = float(min(max(kres, ks[min(N_MIN, len(ks)) - 1]), max(CUT, kres)))
        mem = np.flatnonzero(kap <= keff)
        out['union'] = dict(kappa_eff=keff, n=int(len(mem)))
        lo, hi, complete = union_shares(pool, mem, keff)
        print('shares done', len(mem), 'members', f'{time.time() - t0:.0f}s', flush=True)
    sh, cp = {}, {}
    for i, (wid, *_rest) in enumerate(I.WELLS):
        sh[wid] = {I.SRC[k]: ((lo[(i, k)], hi[(i, k)]) if lo[(i, k)] <= hi[(i, k)] else None) for k in SH_SRC}
        cp[wid] = {I.SRC[k]: bool(complete[(i, k)]) for k in SH_SRC}
    out['shares'] = sh; out['shares_complete'] = cp
    # ---------------- what the sea alone can deliver at each well (members consistent with the heads)
    hc = np.flatnonzero(kh <= kres)
    sea = {}
    for i, (wid, yi, b, q) in enumerate(I.WELLS):
        q = SCR[i]
        vals = [np.max(I.S_INT[0, 1] * E['resp'][j][COLS[i], q, 0] + I.S_INT[2, 1] * E['resp'][j][COLS[i], q, 2])
                for j in hc]
        sea[wid] = dict(max=float(np.max(vals)) if vals else None, q95=float(np.quantile(vals, 0.95)) if vals else None,
                        y=float(yi), tol=float(eps[i]))
    out['sea_only'] = dict(n_heads=int(len(hc)), wells=sea)
    # calibrated ranges of the members consistent with the heads, and of the union
    th = {k: E['th_' + k] for k in ('Kmul', 'aniso', 'Qin', 'rQ', 'x_wf', 'aL', 'aT')}
    th['Qw'] = E['Qw']; th['toe02'] = E['toe02']; th['toe50'] = E['toe50']
    th['h_lit'] = hv['h_lit']; th['h_wf_ag'] = hv['h_wf_ag']; th['h_wf0_ag'] = hv['h_wf0_ag']
    out['ranges'] = {sel_name: {k: np.quantile(v[sel], [0.05, 0.5, 0.95]).tolist() if len(sel) else None
                                for k, v in th.items()}
                     for sel_name, sel in (('prior', np.arange(M)), ('heads', hc), ('union', mem))}
    out['union_members'] = mem.tolist(); out['union_kappa'] = kap[mem].tolist()
    out['kappa_full'] = kap.tolist(); out['kappa_head'] = kh.tolist()
    out['seconds'] = time.time() - t0
    os.makedirs(RES, exist_ok=True)
    json.dump(out, open(os.path.join(RES, f'fk_results_{VARIANT}.json'), 'w'), indent=1)
    print('all done', f'{out["seconds"]:.0f}s')


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
