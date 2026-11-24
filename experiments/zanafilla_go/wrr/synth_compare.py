"""E7: coverage of three answers to the same mixing problem in the synthetic aquifer of the review, where the truth is
known.  (1) Certified bounds of ZANAFILLA-GO; (2) fixed-signature ranges (IsoSource-type: signatures at the midpoints
of their intervals, the same tolerance); (3) Bayesian credible intervals (90%) of a mixing model given every advantage
but one: signatures uniform in their true intervals, the true noise model, the site caps, and a Dirichlet prior on the
water fractions (alpha = 1 or 0.25), sampled by SMC.  Target: the share of chloride from modern seawater.
Two worlds ('prior': the world of the review; 'shift': more relict seawater, a halite body more often) and two tracer
sets (today's Cl + major ions; all seven).  The certified bounds are computed with the general code of field_model and
checked against zanafilla_core.
Writes res/wrr_synth.json.  Run: python synth_compare.py [fields per world] [workers]  (about six minutes)"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.dirname(HERE))
import zanafilla_core as zc  # noqa: E402
from field_model import Model, share_bounds, smc_posterior, shares_of  # noqa: E402

SETS = {'Cl + major ions': zc.TRACER_SETS['Cl + major ions'], 'all seven tracers': zc.TRACER_SETS['+ B (all)']}
TR = {'Br': ('BrCl', 'cl'), 'B': ('BCl', 'cl'), 'BEX': ('BEXCl', 'cl'), 'd18O': ('d18O', 'w'), 'd2H': ('d2H', 'w'),
      'H3': ('H3', 'w')}


def model_of(keep):
    """The synthetic five-source model restricted to the sources in keep (indices)."""
    tracers = {t: dict(cls=c, side='two', sig=zc.SIG[k][keep]) for t, (k, c) in TR.items()}
    return Model([zc.SOURCES[k] for k in keep], zc.SIG['Cl'][keep], tracers)


MID = {'Cl': zc.SIG['Cl'].mean(1)}
MID.update({t: zc.SIG[k].mean(1) for t, (k, _) in TR.items()})


def _job(a):
    i, o, ts, seed = a
    cap = zc.site_caps(i)
    keep = [k for k in range(zc.K) if cap[k] > 0]
    m = model_of(keep)
    mf = m.fixed({k: v[keep] for k, v in MID.items()})
    obs = {t: (o[t], '') for t in ts}
    eps = {t: zc.eps_of(t, o[t], 2.5, o['Cl']) for t in ts}
    sd = {t: zc.noise_sd(t, o[t], o['Cl']) for t in ts}
    c = cap[keep]
    sb = share_bounds(m, obs, ts, eps, cap=c)
    fx = share_bounds(mf, obs, ts, eps, cap=c)
    rng = np.random.default_rng(seed)
    out = dict(cert=None if sb is None else sb[0].tolist(), fixed=None if fx is None else fx[0].tolist())
    for alpha, key in ((1.0, 'bayes1'), (0.25, 'bayes025')):
        X, st, acc = smc_posterior(m, obs, ts, sd, alpha, rng, N=1200, moves=5, cap=c)
        phi = shares_of(X)[:, 0]
        out[key] = [float(np.quantile(phi, 0.05)), float(np.quantile(phi, 0.95)), float(phi.mean()), float(acc)]
    return out


def main(n_fields=20, workers=4):
    t0 = time.time()
    rng = np.random.default_rng(2026)
    # check of the general code against the review's code on a few samples
    F, sig, extra = zc.draw_field(rng, 'prior')
    true, obs, share = zc.observe(F, sig, rng, extra)
    worst = 0.0
    for i in range(0, zc.NS, 3):
        o = {t: float(obs[t][i]) for t in obs}
        ts = SETS['all seven tracers']
        a = zc.share_bounds(o, ts, 0, 2.5, cap=zc.site_caps(i))
        cap = zc.site_caps(i); keep = [k for k in range(zc.K) if cap[k] > 0]
        b = share_bounds(model_of(keep), {t: (o[t], '') for t in ts}, ts,
                         {t: zc.eps_of(t, o[t], 2.5, o['Cl']) for t in ts}, cap=cap[keep])
        if b is not None and np.isfinite(a[0]):
            worst = max(worst, abs(a[0] - b[0][0]), abs(a[1] - b[0][1]))
    print(f'general code against review code: largest difference of the bounds {worst:.2e}')
    pool = Pool(workers)
    R = {'check_max_diff': worst}
    for world in ('prior', 'shift'):
        samples = []
        for _ in range(n_fields):
            F, sig, extra = zc.draw_field(rng, world)
            true, obs, share = zc.observe(F, sig, rng, extra)
            for i in range(zc.NS):
                samples.append((i, {t: float(obs[t][i]) for t in obs}, float(share[i])))
        for sname, ts in SETS.items():
            jobs = [(i, o, ts, 10_000 + j) for j, (i, o, s) in enumerate(samples)]
            out = pool.map(_job, jobs, chunksize=2)
            rec = dict(truth=[s for _, _, s in samples], cert=[r['cert'] for r in out], fixed=[r['fixed'] for r in out],
                       bayes1=[r['bayes1'] for r in out], bayes025=[r['bayes025'] for r in out])
            R[f'{world} | {sname}'] = summarise(rec)
            print(world, sname, {k: (round(v, 3) if isinstance(v, float) else v)
                                 for k, v in R[f'{world} | {sname}'].items() if k != 'raw'}, f'{time.time() - t0:.0f}s')
    pool.close()
    R['settings'] = dict(n_fields=n_fields, samples_per_field=zc.NS, target='modern-seawater chloride share',
                         credible='5-95% (90%)', k_eps=2.5, smc_particles=1200)
    R['seconds'] = time.time() - t0
    json.dump(R, open(os.path.join(HERE, 'res', 'wrr_synth.json'), 'w'), indent=1)


def summarise(rec):
    tr = np.array(rec['truth'])
    out = {}
    nan2 = [np.nan, np.nan]
    cert = np.array([c if c is not None else nan2 for c in rec['cert']], float)
    ok = np.isfinite(cert[:, 0])
    out['cert_cover'] = float(np.mean((cert[ok, 0] - 1e-9 <= tr[ok]) & (tr[ok] <= cert[ok, 1] + 1e-9)))
    out['cert_width'] = float(np.mean(cert[ok, 1] - cert[ok, 0]))
    out['cert_empty'] = float(np.mean(~ok))
    fx = np.array([c if c is not None else nan2 for c in rec['fixed']], float)
    okf = np.isfinite(fx[:, 0])
    out['fixed_empty'] = float(np.mean(~okf))
    out['fixed_cover_all'] = float(np.mean(okf & (fx[:, 0] - 1e-9 <= tr) & (tr <= fx[:, 1] + 1e-9)))
    out['fixed_cover_given'] = float(np.mean((fx[okf, 0] - 1e-9 <= tr[okf]) & (tr[okf] <= fx[okf, 1] + 1e-9)))
    out['fixed_width'] = float(np.mean(fx[okf, 1] - fx[okf, 0])) if okf.any() else None
    for key in ('bayes1', 'bayes025'):
        b = np.array(rec[key], float)
        out[key + '_cover'] = float(np.mean((b[:, 0] <= tr) & (tr <= b[:, 1])))
        out[key + '_width'] = float(np.mean(b[:, 1] - b[:, 0]))
        out[key + '_mean_abs_err'] = float(np.mean(np.abs(b[:, 2] - tr)))
        out[key + '_acc'] = float(np.mean(b[:, 3]))
    b1, b2 = np.array(rec['bayes1'], float), np.array(rec['bayes025'], float)
    out['prior_shift_mean'] = float(np.mean(np.abs(b1[:, 2] - b2[:, 2])))
    out['prior_shift_max'] = float(np.max(np.abs(b1[:, 2] - b2[:, 2])))
    # where the data do not decide (certified width > 0.5) and where they do
    wide = ok & ((cert[:, 1] - cert[:, 0]) > 0.5)
    for key in ('bayes1', 'bayes025'):
        b = np.array(rec[key], float)
        cov = (b[:, 0] <= tr) & (tr <= b[:, 1])
        out[key + '_cover_wide'] = float(np.mean(cov[wide])) if wide.any() else None
        out[key + '_cover_narrow'] = float(np.mean(cov[ok & ~wide])) if (ok & ~wide).any() else None
    out['share_wide'] = float(np.mean(wide))
    out['n'] = int(len(tr))
    out['raw'] = dict(truth=tr.tolist(), cert=cert.tolist(), fixed=fx.tolist(), bayes1=b1.tolist(), bayes025=b2.tolist())
    return out


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20, int(sys.argv[2]) if len(sys.argv) > 2 else 4)
