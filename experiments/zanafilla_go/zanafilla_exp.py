"""ZANAFILLA-GO experiments.  Writes res/zanafilla.json and res/zanafilla_examples.npz.

E1  identified sets of the modern-seawater chloride share for six tracer sets and four levels of end-member knowledge
    (prior world): width, decidability at the threshold 0.5, coverage, empty sets; by location class.
E2  the goal-oriented ranking of the actions (one tracer added at all wells, one end-member sampled) by the gain in
    decidability over today's information.
E3  the amortised neural estimator (three quantile heads, split-conformal calibration) against the certificate, in the
    world it was trained for and in a shifted world (more relict water, a halite body more often).
E4  a source missing from the list (a Br-rich deep brine): how often the polytope is empty (existence test).
E5  stability: the point inverse and the identified interval of one sample under a continuous change of the data.
E6  check of the linear programmes against brute-force sampling.

usage: python zanafilla_exp.py [n_fields_E1] [workers]"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

import zanafilla_core as Z

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
os.makedirs(RES, exist_ok=True)
SAL = 150.0                                     # a sample is salinised above this chloride, mg/L
EM_LEVELS = {'none': [], 'relict': [1], 'relict + fresh': [1, 4], 'relict + fresh + anthropogenic': [1, 3, 4]}


def loc_class(i):
    x = Z.X[i]
    return ('coast' if x <= 1.2 else 'middle' if x <= 4.0 else 'inland') + (' upper' if Z.UP[i] else ' lower')


def fields(n, regime, seed):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        F, sig, extra = Z.draw_field(rng, regime)
        true, obs, share = Z.observe(F, sig, rng, extra)
        out.append(dict(F=F, sig=sig, extra=extra, true=true, obs=obs, share=share))
    return out


def job_bounds(args):
    o, tr, i, S = args
    return Z.share_bounds(o, tr, cap=Z.site_caps(i), sig=S)


def run_e1(flds, pool):
    tasks, keys = [], []
    for fi, fd in enumerate(flds):
        sal = np.where(fd['true']['Cl'] > SAL)[0]
        for lev, srcs in EM_LEVELS.items():
            S = Z.characterised(fd['sig'], srcs) if srcs else Z.SIG
            for name, tr in Z.TRACER_SETS.items():
                for i in sal:
                    o = {k: float(v[i]) for k, v in fd['obs'].items()}
                    tasks.append((o, tr, int(i), S)); keys.append((lev, name, fi, int(i)))
    t0 = time.time()
    res = pool.map(job_bounds, tasks, chunksize=64)
    print(f'E1: {len(tasks)} pairs of linear programmes in {time.time() - t0:.0f} s', flush=True)
    rows = {}
    for (lev, name, fi, i), (lo, hi) in zip(keys, res):
        s = float(flds[fi]['share'][i])
        ok = not np.isnan(lo)
        rows.setdefault((lev, name), []).append(dict(fi=fi, i=i, lo=lo, hi=hi, s=s, ok=ok, cls=loc_class(i),
                                                     w=(hi - lo) if ok else np.nan,
                                                     dec=bool(ok and (lo > 0.5 or hi < 0.5)),
                                                     cov=bool(ok and lo - 1e-9 <= s <= hi + 1e-9),
                                                     right=bool(ok and ((lo > 0.5 and s > 0.5) or (hi < 0.5 and s < 0.5)))))
    summary = []
    for (lev, name), r in rows.items():
        w = np.array([x['w'] for x in r])
        dec = np.array([x['dec'] for x in r]); right = np.array([x['right'] for x in r])
        by = {}
        for c in sorted(set(x['cls'] for x in r)):
            sel = [x for x in r if x['cls'] == c]
            by[c] = dict(n=len(sel), width=float(np.nanmean([x['w'] for x in sel])), decidable=float(np.mean([x['dec'] for x in sel])))
        summary.append(dict(level=lev, tracers=name, n=len(r), width_mean=float(np.nanmean(w)), width_median=float(np.nanmedian(w)),
                            decidable=float(dec.mean()), wrong_when_decided=float(((dec & ~right).sum()) / max(dec.sum(), 1)),
                            coverage=float(np.mean([x['cov'] for x in r])), empty=float(np.mean(np.isnan(w))), by_class=by))
    return summary, rows


def run_e2(summary):
    """the value of each action, measured from today's information (chloride and major ions, no end-member sampled)"""
    base = next(s for s in summary if s['level'] == 'none' and s['tracers'] == 'Cl + major ions')
    acts = [dict(level=s['level'], tracers=s['tracers'], decidable=s['decidable'], width=s['width_mean'],
                 gain_decidable=s['decidable'] - base['decidable'], gain_width=base['width_mean'] - s['width_mean'])
            for s in summary]
    acts.sort(key=lambda a: -a['gain_decidable'])
    return dict(base=dict(decidable=base['decidable'], width=base['width_mean']), actions=acts)


def job_feas(args):
    o, tr, i, S = args
    return Z.feasible(o, tr, cap=Z.site_caps(i), sig=S)


def run_e3(pool, n_train=3000, n_cal=800, n_test=250):
    """the amortised network for two tracer sets (today's and all seven), in the training world and a shifted one"""
    out = {}
    tr_sets = {'Cl + major ions': Z.TRACER_SETS['Cl + major ions'], '+ B (all)': Z.TRACER_SETS['+ B (all)']}

    def stack(flds, tr):
        Xs, ys, ids, fi_ = [], [], [], []
        for k, fd in enumerate(flds):
            sal = np.where(fd['true']['Cl'] > SAL)[0]
            feat = Z.features({t: fd['obs'][t] for t in fd['obs']}, tr)
            loc = np.c_[Z.X, Z.UP.astype(float)]
            Xs.append(np.c_[feat, loc][sal]); ys.append(fd['share'][sal]); ids.append(sal); fi_.append(np.full(len(sal), k))
        return np.concatenate(Xs), np.concatenate(ys), np.concatenate(ids), np.concatenate(fi_)
    t0 = time.time()
    train = fields(n_train, 'prior', 101); cal = fields(n_cal, 'prior', 202)
    test0 = fields(n_test, 'prior', 303); test1 = fields(n_test, 'shift', 404)
    for name, tr in tr_sets.items():
        Xtr, ytr, _, _ = stack(train, tr); Xc, yc, _, _ = stack(cal, tr)
        net = Z.QuantileMLP(Xtr.shape[1], h=64, seed=1).fit(Xtr, ytr, epochs=30)
        marg = Z.cqr_margin(net.predict(Xc), yc)
        res = {}
        for wname, flds in (('training world', test0), ('shifted world', test1)):
            Xt, yt, ids, fis = stack(flds, tr)
            q = net.predict(Xt)
            lo = np.clip(q[:, 0] - marg, 0, 1); hi = np.clip(q[:, 2] + marg, 0, 1)
            cov = (yt >= lo) & (yt <= hi)
            dec = (lo > 0.5) | (hi < 0.5); right = ((lo > 0.5) & (yt > 0.5)) | ((hi < 0.5) & (yt < 0.5))
            # the certificate on the same samples (no end-member sampled)
            tasks = [({k: float(v[i]) for k, v in flds[f]['obs'].items()}, tr, int(i), Z.SIG) for f, i in zip(fis, ids)]
            bnd = np.array(pool.map(job_bounds, tasks, chunksize=64))
            okc = ~np.isnan(bnd[:, 0])
            covc = okc & (yt >= bnd[:, 0] - 1e-9) & (yt <= bnd[:, 1] + 1e-9)
            decc = okc & ((bnd[:, 0] > 0.5) | (bnd[:, 1] < 0.5))
            inside = okc & (lo >= bnd[:, 0] - 1e-9) & (hi <= bnd[:, 1] + 1e-9)
            res[wname] = dict(n=int(len(yt)), nn_coverage=float(cov.mean()), nn_width=float(np.mean(hi - lo)),
                              nn_decidable=float(dec.mean()), nn_wrong_when_decided=float((dec & ~right).sum() / max(dec.sum(), 1)),
                              nn_median_abs_error=float(np.median(np.abs(q[:, 1] - yt))),
                              cert_coverage=float(covc.mean()), cert_width=float(np.nanmean(bnd[:, 1] - bnd[:, 0])),
                              cert_decidable=float(decc.mean()),
                              nn_inside_certificate=float(inside.mean()),
                              nn_coverage_when_inside=float(cov[inside].mean()) if inside.any() else None,
                              nn_coverage_when_outside=float(cov[~inside].mean()) if (~inside).any() else None)
        out[name] = dict(margin=marg, n_train=int(len(ytr)), n_cal=int(len(yc)), worlds=res)
        print(f'E3 {name}: {json.dumps(res)}', flush=True)
    print(f'E3 in {time.time() - t0:.0f} s', flush=True)
    return out


def run_e4(pool, n=150):
    flds = fields(n, 'missing', 505)
    ref = fields(n, 'prior', 606)
    out = {}
    for label, srcs in (('no end-member sampled', []), ('relict + fresh sampled', [1, 4])):
        for tname in ('+ Br', '+ B (all)'):
            tr = Z.TRACER_SETS[tname]
            res = {}
            for wname, FL in (('with an unlisted brine', flds), ('model complete', ref)):
                tasks, frac = [], []
                for fd in FL:
                    S = Z.characterised(fd['sig'], srcs) if srcs else Z.SIG
                    sal = np.where(fd['true']['Cl'] > SAL)[0]
                    for i in sal:
                        tasks.append(({k: float(v[i]) for k, v in fd['obs'].items()}, tr, int(i), S))
                        frac.append(float(fd['extra']['f'][i]) if fd['extra'] is not None else 0.0)
                feas = np.array(pool.map(job_feas, tasks, chunksize=64))
                frac = np.array(frac)
                hit = frac > 0.005
                res[wname] = dict(n=int(len(feas)), empty=float(np.mean(~feas)),
                                  empty_where_brine_above_half_percent=float(np.mean(~feas[hit])) if hit.any() else None,
                                  n_brine=int(hit.sum()))
            out[f'{label} | {tname}'] = res
            print('E4', label, tname, res, flush=True)
    return out


def ls_point(o, tracers, sv):
    """non-negative least squares on the simplex for given signature values sv (dict of K-vectors), errors as weights"""
    from scipy.optimize import nnls
    rows, rhs = [], []
    for t in tracers:
        if t == 'Cl':
            st = sv['Cl']
        else:
            key, kind = Z.KIND[t]
            st = sv[key] * sv['Cl'] if kind == 'cl' else sv[key]
        sd = Z.noise_sd(t, o[t], o['Cl'])
        rows.append(st / sd); rhs.append(o[t] / sd)
    A = np.vstack(rows + [1e3 * np.ones(Z.K)]); y = np.array(rhs + [1e3])
    f, _ = nnls(A, y)
    c = f * sv['Cl']
    return float(c[0] / max(c.sum(), 1e-12))


def run_e5(n_fields=15, n_sig=40):
    """non-uniqueness of the point inverse.  For every salinised sample (all seven tracers, no end-member sampled): the
    least-squares share with the central signatures, its range over n_sig signature sets drawn inside the intervals
    (each set reproduces the data about equally well), the identified interval and the truth."""
    rng = np.random.default_rng(11)
    tr = Z.TRACER_SETS['+ B (all)']
    cen = {k: v.mean(1) for k, v in Z.SIG.items()}
    draws = [{k: rng.uniform(v[:, 0], v[:, 1]) for k, v in Z.SIG.items()} for _ in range(n_sig)]
    rec = []
    for _ in range(n_fields):
        F, sig, extra = Z.draw_field(rng)
        true, obs, share = Z.observe(F, sig, rng)
        for i in np.where(true['Cl'] > SAL)[0]:
            o = {k: float(v[i]) for k, v in obs.items()}
            p0 = ls_point(o, tr, cen)
            ps = np.array([ls_point(o, tr, d) for d in draws])
            lo, hi = Z.share_bounds(o, tr, cap=Z.site_caps(i))
            rec.append(dict(s=float(share[i]), p0=p0, pmin=float(ps.min()), pmax=float(ps.max()), lo=lo, hi=hi))
    s = np.array([r['s'] for r in rec]); p0 = np.array([r['p0'] for r in rec])
    pmin = np.array([r['pmin'] for r in rec]); pmax = np.array([r['pmax'] for r in rec])
    lo = np.array([r['lo'] for r in rec]); hi = np.array([r['hi'] for r in rec])
    err = np.abs(p0 - s)
    return dict(n=len(rec), median_abs_error=float(np.median(err)), frac_error_above_0p25=float(np.mean(err > 0.25)),
                wrong_side_of_half=float(np.mean((p0 > 0.5) != (s > 0.5))), mean_spread=float(np.mean(pmax - pmin)),
                truth_outside_ls_range=float(np.mean((s < pmin - 1e-9) | (s > pmax + 1e-9))),
                truth_outside_set=float(np.mean((s < lo - 1e-9) | (s > hi + 1e-9))), mean_set_width=float(np.nanmean(hi - lo)),
                examples=rec[:60])


def run_e6(n=6, draws=300000):
    """brute force: draw fractions and signatures, keep those consistent with the data, compare the range of the share
    with the linear-programming bounds (Cl + Br + BEX, nothing sampled).  The sampled range must lie inside the bounds and
    approach them."""
    rng = np.random.default_rng(21)
    tr = Z.TRACER_SETS['+ Br']
    out = []
    for k in range(n):
        F, sig, extra = Z.draw_field(rng)
        true, obs, share = Z.observe(F, sig, rng)
        i = int(rng.choice(np.where(true['Cl'] > SAL)[0]))
        o = {t: float(v[i]) for t, v in obs.items()}
        lo, hi = Z.share_bounds(o, tr, cap=Z.site_caps(i))
        cap = Z.site_caps(i)
        f = rng.dirichlet(np.ones(Z.K) * 0.4, draws)
        f = f[(f <= cap).all(1)]
        cl = rng.uniform(Z.SIG['Cl'][:, 0], Z.SIG['Cl'][:, 1], (len(f), Z.K))
        br = rng.uniform(Z.SIG['BrCl'][:, 0], Z.SIG['BrCl'][:, 1], (len(f), Z.K))
        bx = rng.uniform(Z.SIG['BEXCl'][:, 0], Z.SIG['BEXCl'][:, 1], (len(f), Z.K))
        c = f * cl
        C, B, E = c.sum(1), (c * br).sum(1), (c * bx).sum(1)
        ok = (np.abs(C - o['Cl']) <= Z.eps_of('Cl', o['Cl'], cl=o['Cl'])) & (np.abs(B - o['Br']) <= Z.eps_of('Br', o['Br'], cl=o['Cl'])) \
            & (np.abs(E - o['BEX']) <= Z.eps_of('BEX', o['BEX'], cl=o['Cl']))
        s = c[:, 0] / C
        out.append(dict(i=i, lp_lo=lo, lp_hi=hi, n_consistent=int(ok.sum()),
                        mc_lo=float(s[ok].min()) if ok.any() else None, mc_hi=float(s[ok].max()) if ok.any() else None))
    return out


def main(n_e1=40, workers=4):
    t0 = time.time()
    with Pool(workers) as pool:
        flds = fields(n_e1, 'prior', 7)
        summary, rows = run_e1(flds, pool)
        e3 = run_e3(pool)
        e4 = run_e4(pool)
    e5 = run_e5()
    e6 = run_e6()
    # an example field for the figure of intervals
    ex = {}
    for (lev, name), r in rows.items():
        if (lev, name) in (('none', 'Cl + major ions'), ('none', '+ B (all)'), ('relict + fresh', '+ B (all)')):
            sel = [x for x in r if x['fi'] == 0]
            ex[f'{lev}|{name}'] = dict(i=[x['i'] for x in sel], lo=[x['lo'] for x in sel], hi=[x['hi'] for x in sel], s=[x['s'] for x in sel])
    fd = flds[0]
    np.savez_compressed(os.path.join(RES, 'zanafilla_examples.npz'), F=fd['F'], share=fd['share'], cl=fd['true']['Cl'],
                        X=Z.X, Zs=Z.Z, UP=Z.UP)
    out = dict(settings=dict(k_eps=2.5, salinised_mg_L=SAL, n_fields_E1=n_e1, tracer_sets=Z.TRACER_SETS, em_levels=EM_LEVELS,
                             sources=Z.SOURCES, signatures={k: v.tolist() for k, v in Z.SIG.items()},
                             noise={k: v for k, v in Z.NOISE.items()}, bex_noise=[Z.BEX_REL, Z.BEX_ABS]),
               E1=summary, E2=run_e2(summary), E3=e3, E4=e4, E5=e5, E6=e6, examples=ex, seconds=round(time.time() - t0, 1))
    with open(os.path.join(RES, 'zanafilla.json'), 'w') as fh:
        json.dump(out, fh, indent=1, default=lambda v: None if (isinstance(v, float) and np.isnan(v)) else v)
    for s in summary:
        print(f"E1 {s['level']:32s} {s['tracers']:16s} width {s['width_mean']:.3f} decidable {s['decidable']:.3f} "
              f"wrong {s['wrong_when_decided']:.3f} coverage {s['coverage']:.3f} empty {s['empty']:.3f}")
    print('E5', {k: v for k, v in e5.items() if k != 'examples'})
    print('E6', e6)
    print('done in', round(time.time() - t0), 's')


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 40, int(sys.argv[2]) if len(sys.argv) > 2 else 4)
