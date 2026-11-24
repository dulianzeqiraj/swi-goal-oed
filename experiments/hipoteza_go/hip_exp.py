"""Numerical test of HIPOTEZA-GO on a synthetic coastal section.

H1  resolution of the ensemble: the tolerance inflation kappa_res of every data scenario (leave-one-out);
H2  attribution for truths drawn independently of the ensemble (world W0: no deep saline water), four data
    scenarios, physics-coupled (HIPOTEZA-GO) against per-sample mixing without physics (ZANAFILLA-GO);
H3  hypotheses as terms: is the anthropogenic term, or the legacy term, necessary?  (reduced libraries);
H4  a source that is not in the library (world W1: deep saline water): is the library falsified?  and with the
    term added, which are the sparsest libraries that explain the data?
H5  model error: truths with a layered conductivity that the ensemble does not contain.
Writes res/hipoteza.json.  usage: python hip_exp.py [truths] [workers]   (about fifteen minutes on four cores)
       python hip_exp.py full [workers]   adds the complete unions of scenario B to an existing result file
       python hip_exp.py context          writes res/context.json (true dominant sources) from an existing result file"""
import itertools
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'zanafilla_go', 'wrr'))
import hip_core as H  # noqa: E402
import hip_infer as I  # noqa: E402
from field_model import Model, share_bounds  # noqa: E402

E = None                                    # the ensemble, loaded once per process


def _init():
    global E
    z = np.load(os.path.join(HERE, 'res', 'ensemble.npz'))
    ok = z['ok']
    E = {k: z[k][ok] for k in z.files if k != 'ok'}


# ------------------------------------------------------------------------------------------------ mixing without physics
MIX_CL = np.array([I.S_INT[0], I.S_INT[1], I.S_INT[2], [50, 800], [200, 6000], [1000, 50000]], float)


def mixing_bounds(truth, sc, lib):
    """Per-sample identified sets with the same tracers and signature intervals but no physics: every sample has its
    own fractions (ZANAFILLA-GO).  The solute sources become 'waters' with wide chloride ranges and the isotopes of
    fresh water; without transport the tritium of every water may have decayed to zero."""
    S, R, D, T = I.intervals(truth, sc['em'])
    cl = MIX_CL[lib].copy(); cl[:3] = S[:3][[k for k in range(3)]]
    d18 = np.array([D[0], D[1], D[2], D[2], D[2], D[2]])[lib]
    h3 = np.array([[0, T[0, 1]], [0, T[1, 1]], [0, T[2, 1]], [0, T[2, 1]], [0, T[2, 1]], [0, T[2, 1]]])[lib]
    m = Model([I.SRC[k] for k in lib], cl, {'Br': dict(cls='cl', side='two', sig=R[lib]),
                                            'd18O': dict(cls='w', side='two', sig=d18),
                                            'H3': dict(cls='w', side='two', sig=h3)})
    lo = np.full((I.NS, 6), np.nan); hi = np.full((I.NS, 6), np.nan)
    obs = truth['obs']
    for i in sc['cl']:
        if obs['Cl'][i] <= 100.0:
            continue
        o = {'Cl': (obs['Cl'][i], '')}
        for t in sc['tr']:
            o[t] = (obs[t][i], '')
        ts = ['Cl'] + list(sc['tr'])
        eps = {t: I.K_EPS * I.sd_of(t, o[t][0]) for t in ts}
        sb = share_bounds(m, o, ts, eps)
        if sb is None:
            continue
        for n, k in enumerate(lib):
            lo[i, k], hi[i, k] = sb[n]
    return lo, hi


# ------------------------------------------------------------------------------------------------ metrics
def metrics(lo, hi, truth, sc, srcs=(0, 1, 3, 4, 5)):
    share = truth['share']
    sal = [i for i in sc['cl'] if truth['obs']['Cl'][i] > 100.0]
    out = dict(n_sal=len(sal), identified=0, wrong_id=0, excluded=0, wrong_excl=0, pairs=0, covered=0, width=[],
               ms_decided=0, ms_wrong=0)
    for i in sal:
        dom = int(np.argmax(share[i]))
        idk = [k for k in srcs if np.isfinite(lo[i, k]) and lo[i, k] > 0.5]
        if idk:
            out['identified'] += 1
            out['wrong_id'] += int(idk[0] != dom)
        if np.isfinite(lo[i, 0]) and (lo[i, 0] > 0.5 or hi[i, 0] < 0.5):
            out['ms_decided'] += 1
            out['ms_wrong'] += int((lo[i, 0] > 0.5) != (share[i, 0] > 0.5))
        for k in srcs:
            if not np.isfinite(lo[i, k]):
                continue
            out['pairs'] += 1
            out['covered'] += int(lo[i, k] - 1e-6 <= share[i, k] <= hi[i, k] + 1e-6)
            out['width'].append(float(hi[i, k] - lo[i, k]))
            if hi[i, k] < 0.1:
                out['excluded'] += 1
                out['wrong_excl'] += int(share[i, k] >= 0.1 + 1e-6)
    return out


def _truth_R(th, Kfield=None):
    R = H.member(th, Kfield)
    return R


# ------------------------------------------------------------------------------------------------ jobs
def job_calib(a):
    """Leave-one-out trials of one scenario: the left-out member generates data; kappa of all the others with the
    library, and the smallest kappa of the library of the truth."""
    name, seed, trials = a
    rng = np.random.default_rng(seed)
    return name, [I.calib_trial(E, I.SCEN[name], I.L5, rng) for _ in range(trials)]


def job_margin(a):
    """Leave one member out, let it generate data, attribute with the others at kappa_res, and record by how much
    the true shares fall outside the union (0 when inside).  The quantile of these misses is the margin delta."""
    name, seed, trials, kap = a
    rng = np.random.default_rng(seed)
    sc = I.SCEN[name]
    M = len(E['head'])
    miss = []
    for (j0, tr, kp, _) in trials:
        a_ = I.attribute(E, tr, sc, I.L5, kap, rng, members=np.delete(np.arange(M), j0), kap=kp)
        ok = a_['exact'] & np.isfinite(a_['lo'])
        d = np.maximum(0.0, np.maximum(a_['lo'] - tr['share'], tr['share'] - a_['hi']))
        miss += d[ok].tolist()
    return name, miss


def job_truth(a):
    """One truth through every scenario.  a = (index, theta, world, kappa_res dict, Kfield or None, tests)."""
    n, th, world, kres, Kfield, tests, delta = a
    rng = np.random.default_rng(900 + n)
    R = _truth_R(th, Kfield)
    if not R['ok']:
        return None
    truth = I.draw_truth(R, rng, world)
    out = dict(n=n, world=world, S=truth['S'].tolist(), toe02=R['toe02'], cl=truth['obs']['Cl'].tolist(), scen={})
    for name, sc in I.SCEN.items():
        res = {}
        t0 = time.time()
        a_ = I.attribute(E, truth, sc, I.L5, kres[name], rng)
        res['kappa_min'], res['falsified'], res['n_nroy'] = a_['kappa_min'], a_['falsified'], a_['n_nroy']
        res['n_res'], res['kappa_eff'] = a_['n_res'], a_['kappa_eff']
        dl = delta[name]
        lo_w, hi_w = np.clip(a_['lo'] - dl, 0.0, 1.0), np.clip(a_['hi'] + dl, 0.0, 1.0)
        res['hip'] = metrics(lo_w, hi_w, truth, sc)                         # with the calibrated margin
        res['hip_raw'] = metrics(a_['lo'], a_['hi'], truth, sc)            # the union as computed
        # coverage only where the union is complete
        lo_e = np.where(a_['exact'], lo_w, np.nan); hi_e = np.where(a_['exact'], hi_w, np.nan)
        res['hip_exact'] = metrics(lo_e, hi_e, truth, sc)
        mlo, mhi = mixing_bounds(truth, sc, I.L5)
        res['mix'] = metrics(mlo, mhi, truth, sc)
        if 'terms' in tests:
            # reduced libraries: drop the anthropogenic term, drop the legacy term
            res['k_noAN'] = I.sub_kappa(E, truth, sc, [0, 1, 2, 4], a_['members'], a_['kap'])
            res['k_noRS'] = I.sub_kappa(E, truth, sc, [0, 1, 2, 3], a_['members'], a_['kap'])
        if 'subsets' in tests:
            a6 = I.attribute(E, truth, sc, I.L6, kres[name], rng)
            sub = {}
            for r in range(4):
                for comb in itertools.combinations((3, 4, 5), r):
                    key = ''.join(I.SRC[k] + ' ' for k in comb).strip() or 'none'
                    sub[key] = a6['kappa_min'] if len(comb) == 3 else \
                        I.sub_kappa(E, truth, sc, [0, 1, 2] + list(comb), a6['members'], a6['kap'])
            res['subsets'] = sub
            res['hip6'] = metrics(np.clip(a6['lo'] - dl, 0, 1), np.clip(a6['hi'] + dl, 0, 1), truth, sc)
            res['hip6_falsified'] = a6['falsified']
        res['sec'] = time.time() - t0
        out['scen'][name] = res
    return out


def job_full(a):
    """Complete unions of every pair of sample and source for one truth of scenario B (all members of the union,
    every pair by linear programming): the example figure and the check of the coverage of all intervals."""
    n, th, kres, dl = a
    name = list(I.SCEN)[1]
    sc = I.SCEN[name]
    rng = np.random.default_rng(900 + n)
    R = _truth_R(th)
    if not R['ok']:
        return None
    truth = I.draw_truth(R, rng, 'W0')                     # the same truth as in job_truth
    a_ = I.attribute(E, truth, sc, I.L5, kres, rng, full=True)
    out = dict(n=n, falsified=a_['falsified'], n_nroy=a_['n_nroy'], S=truth['S'].tolist(), toe02=R['toe02'],
               cl=truth['obs']['Cl'].tolist())
    if a_['falsified']:
        return out
    lo_w, hi_w = np.clip(a_['lo'] - dl, 0.0, 1.0), np.clip(a_['hi'] + dl, 0.0, 1.0)
    mlo, mhi = mixing_bounds(truth, sc, I.L5)
    f = lambda v: np.where(np.isfinite(v), v, -1).tolist()
    out['hip_full'] = metrics(lo_w, hi_w, truth, sc)
    out['example'] = dict(lo=f(lo_w), hi=f(hi_w), mlo=f(mlo), mhi=f(mhi), share=truth['share'].tolist())
    return out


def full_unions(pool, kres, delta, n_truth):
    name = list(I.SCEN)[1]
    ths = H.draw_theta(np.random.default_rng(31), n_truth)     # the truths of H2
    res = pool.map(job_full, [(n, th, kres[name], delta[name]) for n, th in enumerate(ths)], chunksize=1)
    return [r for r in res if r is not None]


def layered(th, rng):
    """A conductivity field outside the class: two layers with a contrast of 3 to 6 and the same mean."""
    f = rng.uniform(3.0, 6.0)
    top = rng.uniform() < 0.5
    k1, k2 = 2 * th['Kx'] * f / (1 + f), 2 * th['Kx'] / (1 + f)
    Kf = np.empty((H.NZ, H.NX))
    Kf[:H.NZ // 2] = k1 if top else k2
    Kf[H.NZ // 2:] = k2 if top else k1
    return Kf


def main(n_truth=24, workers=4):
    t0 = time.time()
    out = {'n_truth': n_truth}
    with Pool(workers, initializer=_init) as pool:
        # ---------------- H1
        jobs = [(name, 100 + 7 * b, 12) for name in I.SCEN for b in range(4)]
        loo = {name: [] for name in I.SCEN}
        for name, k in pool.map(job_calib, jobs, chunksize=1):
            loo[name] += k
        ks = {name: [float(k[3]) for k in v] for name, v in loo.items()}            # library of the truth
        ks_full = {name: [float(k[2].min()) for k in v] for name, v in loo.items()}  # full library
        kres = {name: float(max(1.0, np.quantile(v, 0.9))) for name, v in ks.items()}
        print('H1 kappa', {k: round(v, 2) for k, v in kres.items()}, f'{time.time() - t0:.0f}s', flush=True)
        jobs = [(name, 500 + b, loo[name][b::4][:7], kres[name]) for name in I.SCEN for b in range(4)]
        ms = {name: [] for name in I.SCEN}
        for name, m_ in pool.map(job_margin, jobs, chunksize=1):
            ms[name] += m_
        delta = {name: float(np.quantile(v, 0.95)) if v else 0.0 for name, v in ms.items()}
        out['H1'] = dict(kappa_res=kres, kappa_loo=ks, kappa_loo_full=ks_full, delta=delta, n_min=I.N_MIN,
                         max_miss={name: float(max(v)) if v else 0.0 for name, v in ms.items()},
                         miss_rate_raw={name: float(np.mean(np.array(v) > 1e-6)) for name, v in ms.items()},
                         n_pairs={name: len(v) for name, v in ms.items()})
        print('H1 kappa', {k: round(v, 2) for k, v in kres.items()}, 'delta', {k: round(v, 3) for k, v in delta.items()},
              f'{time.time() - t0:.0f}s', flush=True)
        # ---------------- H2 + H3
        rng = np.random.default_rng(31)
        ths = H.draw_theta(rng, n_truth)
        res = pool.map(job_truth, [(n, th, 'W0', kres, None, ('terms',), delta) for n, th in enumerate(ths)], chunksize=1)
        out['H2'] = [r for r in res if r is not None]
        print('H2 done', f'{time.time() - t0:.0f}s', flush=True)
        out['H2full'] = full_unions(pool, kres, delta, n_truth)
        print('H2 complete unions done', f'{time.time() - t0:.0f}s', flush=True)
        # ---------------- H4
        ths = H.draw_theta(rng, 10)
        res = pool.map(job_truth, [(1000 + n, th, 'W1', kres, None, ('subsets',), delta) for n, th in enumerate(ths)],
                       chunksize=1)
        out['H4'] = [r for r in res if r is not None]
        print('H4 done', f'{time.time() - t0:.0f}s', flush=True)
        # ---------------- H5
        ths = H.draw_theta(rng, 10)
        res = pool.map(job_truth, [(2000 + n, th, 'W0', kres, layered(th, rng), (), delta) for n, th in enumerate(ths)],
                       chunksize=1)
        out['H5'] = [r for r in res if r is not None]
        print('H5 done', f'{time.time() - t0:.0f}s', flush=True)
    z = np.load(os.path.join(HERE, 'res', 'ensemble.npz'))
    out['ensemble'] = dict(M=int(len(z['ok'])), converged=int(z['ok'].sum()),
                           toe02_q=np.quantile(z['toe02'][z['ok']], [0.05, 0.5, 0.95]).tolist(),
                           wsum_err=float(z['wsum_err'].max()))
    out['seconds'] = time.time() - t0
    json.dump(out, open(os.path.join(HERE, 'res', 'hipoteza.json'), 'w'), indent=1)
    context(out)
    print('all done', f'{out["seconds"]:.0f}s')


def context(out):
    """How many salinised samples truly have a dominant source (share above 1/2), and which: the denominators that
    the text quotes.  The truths of H2 and H4 are drawn again from their seeds.  Writes res/context.json."""
    rng = np.random.default_rng(31)
    n_truth = out.get('n_truth', len(out['H2']))
    sets = [('H2', H.draw_theta(rng, n_truth), 0, 'W0'), ('H4', H.draw_theta(rng, len(out['H4'])), 1000, 'W1')]
    ctx = {}
    for key, ths, off, world in sets:
        res = {name: dict(n=0, dom=0, by={k: 0 for k in I.SRC}) for name in I.SCEN}
        for i, th in enumerate(ths):
            R = H.member(th)
            if not R['ok']:
                continue
            truth = I.draw_truth(R, np.random.default_rng(900 + off + i), world)
            stored = next(r for r in out[key] if r['n'] == off + i)
            assert np.allclose(stored['cl'], truth['obs']['Cl']), 'truth not reproduced'
            for name, sc in I.SCEN.items():
                for s_ in sc['cl']:
                    if truth['obs']['Cl'][s_] > 100.0:
                        res[name]['n'] += 1
                        k = int(np.argmax(truth['share'][s_]))
                        if truth['share'][s_, k] > 0.5:
                            res[name]['dom'] += 1
                            res[name]['by'][I.SRC[k]] += 1
        ctx[key] = res
    json.dump(ctx, open(os.path.join(HERE, 'res', 'context.json'), 'w'), indent=1)
    return ctx


def only_full(workers=4):
    """Adds the stage of complete unions to an existing res/hipoteza.json (python hip_exp.py full [workers])."""
    path = os.path.join(HERE, 'res', 'hipoteza.json')
    out = json.load(open(path))
    t0 = time.time()
    with Pool(workers, initializer=_init) as pool:
        out['H2full'] = full_unions(pool, out['H1']['kappa_res'], out['H1']['delta'],
                                    out.get('n_truth', len(out['H2'])))
    json.dump(out, open(path, 'w'), indent=1)
    print('complete unions done', f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'full':
        only_full(int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    elif len(sys.argv) > 1 and sys.argv[1] == 'context':
        context(json.load(open(os.path.join(HERE, 'res', 'hipoteza.json'))))
    else:
        main(int(sys.argv[1]) if len(sys.argv) > 1 else 24, int(sys.argv[2]) if len(sys.argv) > 2 else 4)
