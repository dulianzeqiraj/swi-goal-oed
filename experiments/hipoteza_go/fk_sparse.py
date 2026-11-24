"""Completes the share bounds of fk_run.py and adds the bounds under the sparsest accepted libraries.
(1) full library: the pairs left incomplete by the staged union are followed over every member, in the directions
    that are not already trivial (lower bound 0, upper bound 1);
(2) for each sparsest accepted library: kappa of every member, union over the members within kappa_res (minimum
    population 39); every pair over 20 members, then the pairs that carry a statement (lower bound above 1/2, upper
    bound below 0.1) over all of them; the other pairs are bounds of the first 20 only (inner bounds of the union).
Writes res_fk/fk_sparse_<variant>.json.  usage: python fk_sparse.py [workers]"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

import fk_infer as I
import fk_run as RUN

HERE = os.path.dirname(os.path.abspath(__file__))
VARIANT = os.environ.get('FK_VARIANT', 'second')


def job_kappa_lib(a):
    chunk, lib = a
    y, eps = I.data()
    kh = I.kappa_head(RUN.E)
    return [I.kappa_member(RUN.E, j, lib, y, eps, RUN.COLS, RUN.SCR, kh[j], RUN.CUT) for j in chunk]


def job_shares_lib(a):
    j, kap, lib, spec = a
    y, eps = I.data()
    G = I.responses(RUN.E, j, RUN.COLS, RUN.SCR)
    lo, hi = I.box(lib)
    srcs = [k for k in RUN.SH_SRC if k in lib]
    out = {}
    for i in range(len(I.WELLS)):
        if spec is None:
            out[i] = I.share_bounds(G, y, eps, kap, lo, hi, i, srcs)
        elif spec.get(i):
            out[i] = I.share_bounds(G, y, eps, kap, lo, hi, i, list(spec[i]), senses=spec[i])
    return int(j), out


def union(pool, mem, keff, lib, spec_all=None, lo=None, hi=None):
    nw = len(I.WELLS)
    srcs = [k for k in RUN.SH_SRC if k in lib]
    lo = lo or {(i, k): 1.0 for i in range(nw) for k in srcs}
    hi = hi or {(i, k): 0.0 for i in range(nw) for k in srcs}
    for j, b in pool.imap_unordered(job_shares_lib, [(j, keff, lib, spec_all) for j in mem]):
        for i, d in b.items():
            if d is None:
                continue
            for k, (l_, h_) in d.items():
                if np.isfinite(l_):
                    lo[(i, k)] = min(lo[(i, k)], l_)
                if np.isfinite(h_):
                    hi[(i, k)] = max(hi[(i, k)], h_)
    return lo, hi


def main(workers=4):
    t0 = time.time()
    RUN.VARIANT = VARIANT
    RUN._init()
    R = json.load(open(os.path.join(RUN.RES, f'fk_results_{VARIANT}.json')))
    kres = R['loo']['kappa_res']
    out = {}
    with Pool(workers, initializer=RUN._init) as pool:
        # (1) complete the full library
        mem = np.array(R['union_members']); keff = R['union']['kappa_eff']
        sh, cp = R['shares'], R['shares_complete']
        spec = {}
        lo, hi = {}, {}
        for i, (wid, *_r) in enumerate(I.WELLS):
            for k in RUN.SH_SRC:
                v = sh[wid][I.SRC[k]]
                lo[(i, k)], hi[(i, k)] = (v if v is not None else (1.0, 0.0))
                if not cp[wid][I.SRC[k]]:
                    sn = tuple(x for x, ok in (('min', lo[(i, k)] > 0.0), ('max', hi[(i, k)] < 1.0)) if ok)
                    if sn:
                        spec.setdefault(i, {})[k] = sn
        print('completing', {I.WELLS[i][0]: {I.SRC[k]: v for k, v in d.items()} for i, d in spec.items()}, flush=True)
        if spec:
            lo, hi = union(pool, mem, keff, I.FULL, spec, lo, hi)
        out['full'] = {wid: {I.SRC[k]: (lo[(i, k)], hi[(i, k)]) for k in RUN.SH_SRC}
                       for i, (wid, *_r) in enumerate(I.WELLS)}
        json.dump(out, open(os.path.join(RUN.RES, f'fk_sparse_{VARIANT}.json'), 'w'), indent=1)
        print('full library complete', f'{time.time() - t0:.0f}s', flush=True)
        # (2) the sparsest accepted libraries
        feas = [d for d in R['libraries'] if d['feasible']]
        fset = [frozenset(d['lib']) for d in feas]
        minimal = [s for s in fset if not any(t < s for t in fset)]
        out['sparse'] = {}
        M = len(RUN.E['h_lit'])
        chunks = np.array_split(np.arange(M), 4 * workers)
        for s in minimal:
            lib = sorted(I.SRC.index(n) for n in s)
            kap = np.concatenate(pool.map(job_kappa_lib, [(c, lib) for c in chunks], chunksize=1))
            ks = np.sort(kap)
            keff_l = float(min(max(kres, ks[min(RUN.N_MIN, len(ks)) - 1]), max(RUN.CUT, kres)))
            mem_l = np.random.default_rng(11).permutation(np.flatnonzero(kap <= keff_l))
            lo_l, hi_l = union(pool, mem_l[:20], keff_l, lib)
            spec = {}
            for (i, k) in lo_l:
                sn = tuple(x for x, ok in (('min', lo_l[(i, k)] > 0.5), ('max', hi_l[(i, k)] < 0.1)) if ok)
                if sn:
                    spec.setdefault(i, {})[k] = sn
            if spec and len(mem_l) > 20:
                lo_l, hi_l = union(pool, mem_l[20:], keff_l, lib, spec, lo_l, hi_l)
            stmt = {I.WELLS[i][0]: {I.SRC[k]: list(v) for k, v in d.items()} for i, d in spec.items()}
            key = ' + '.join(I.SRC[k] for k in lib)
            out['sparse'][key] = dict(kappa_min=float(kap.min()), n_within=int((kap <= kres).sum()),
                                      kappa_eff=keff_l, n_union=int(len(mem_l)), statements=stmt,
                                      shares={wid: {I.SRC[k]: (lo_l[(i, k)], hi_l[(i, k)])
                                                    for k in RUN.SH_SRC if k in lib}
                                              for i, (wid, *_r) in enumerate(I.WELLS)},
                                      toe02=np.quantile(RUN.E['toe02'][mem_l], [0.05, 0.5, 0.95]).tolist(),
                                      Qw=np.quantile(RUN.E['Qw'][mem_l], [0.05, 0.5, 0.95]).tolist())
            print(key, 'union', len(mem_l), 'members', f'{time.time() - t0:.0f}s', flush=True)
    out['seconds'] = time.time() - t0
    json.dump(out, open(os.path.join(RUN.RES, f'fk_sparse_{VARIANT}.json'), 'w'), indent=1)
    print('all done', f'{out["seconds"]:.0f}s')


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
