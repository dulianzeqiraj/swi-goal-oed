"""Field application of ZANAFILLA-GO to the West Coast Basin (Land et al., 2004).

F1  identified sets (sharp bounds of the chloride share of N, S, I, B) for every sample with all its tracers;
F2  which tracers decide: bounds with nested tracer sets;
F3  falsification: samples with an empty set and the tracer whose removal restores a non-empty set; tolerance and
    native-chloride sensitivity;
F4  comparators: fixed reported end-members (IsoSource-type ranges) and a Bayesian mixing model under two priors;
F5  the next action: predicted against realised gain of a held-out tracer (retrospective test of the design rule),
    and the expected gain of characterising the brine, the seawater tritium or the imported water.
Writes res_field/field.json (per-well results of public data; kept out of the repository by .gitignore).
Run: python field_exp.py [workers]   (about five minutes on four cores)"""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

from field_data import load, build_model, obs_of, eps_of, sd_dict, fixed_values, NOISE
from field_model import share_bounds, feasible, sample_prior, mixture, smc_posterior, shares_of, summarise_shares

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'res_field')
ALL = ['Cl', 'Br', 'I', 'B', 'd18O', 'd2H', 'H3']
SETS = {'Cl': ['Cl'], '+ Br': ['Cl', 'Br'], '+ isotopes': ['Cl', 'Br', 'd18O', 'd2H'],
        '+ tritium': ['Cl', 'Br', 'd18O', 'd2H', 'H3'], '+ iodide': ['Cl', 'Br', 'd18O', 'd2H', 'H3', 'I'],
        '+ boron (all)': ALL}
TAU_S, TAU_B = 0.5, 0.1          # decisions: seawater the main source (> 1/2)? brine material (> 0.1)?
K_EPS = 2.5


def tset_of(o, wanted):
    return [t for t in wanted if t in o]


def decided(sb):
    """(seawater decision decided?, brine decision decided?) for bounds sb (K x 2), sources N, S, I, B."""
    if sb is None:
        return False, False
    s_lo, s_hi = sb[1]
    b_lo, b_hi = sb[3]
    return bool(s_lo > TAU_S or s_hi < TAU_S), bool(b_lo > TAU_B or b_hi < TAU_B)


def _job(a):
    m, o, ts, k = a
    sb = share_bounds(m, o, ts, eps_of({t: o[t] for t in ts}, k))
    return None if sb is None else sb.tolist()


def _feas_job(a):
    m, o, ts, k = a
    return feasible(m, o, ts, eps_of({t: o[t] for t in ts}, k))


def _smc_job(a):
    """SMC posterior of one sample; optionally M simulated observations of held-out tracers from the posterior."""
    m, o, ts, alpha, seed, M, held = a
    rng = np.random.default_rng(seed)
    X, stages, acc = smc_posterior(m, o, ts, sd_dict({t: o[t] for t in ts}), alpha, rng, N=3000)
    post = summarise_shares(shares_of(X)).tolist()
    sim = []
    if M:
        pick = rng.choice(len(X['f']), size=M, replace=False)
        P = sample_prior(m, M, alpha, rng)          # fresh signatures for the held-out tracers
        for k_ in X:
            P[k_] = X[k_][pick]
        vals = []
        for h in held:
            mu = mixture(m, P, h)
            rel, ab = NOISE[h]
            vals.append(mu + rng.standard_normal(M) * (rel * np.abs(mu) + ab))
        sim = np.array(vals).T.tolist()
    return dict(post=post, stages=stages, acc=acc, sim=sim)


def run_jobs(pool, jobs):
    return pool.map(_job, jobs, chunksize=4)


def main(workers=4):
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    appA, t2 = load()
    m, notes = build_model(appA, t2)
    rows = [r for r in appA if r['date'] and r['name'] in t2]
    names = [r['name'] for r in rows]
    obs = [obs_of(r, t2[r['name']]) for r in rows]
    R = dict(sources=m.sources, notes=notes, names=names, tau_s=TAU_S, tau_b=TAU_B, k_eps=K_EPS,
             cl=[o['Cl'][0] for o in obs], table2={n: t2[n] for n in names},
             tracers={n: tset_of(o, ALL) for n, o in zip(names, obs)},
             intervals=dict(Cl=m.cl.tolist(), **{t: m.tr[t]['sig'].tolist() for t in m.tr},
                            d=[m.joint[0]['lo'].tolist(), m.joint[0]['hi'].tolist()]))
    pool = Pool(workers)
    # ---------------------------------------------------------------- F1: all tracers
    F1 = run_jobs(pool, [(m, o, tset_of(o, ALL), K_EPS) for o in obs])
    R['F1'] = F1
    print(f'F1 done {time.time() - t0:.0f}s; empty: {[n for n, s in zip(names, F1) if s is None]}')
    # ---------------------------------------------------------------- F2: nested tracer sets
    F2 = {}
    for key, ws in SETS.items():
        F2[key] = run_jobs(pool, [(m, o, tset_of(o, ws), K_EPS) for o in obs])
    R['F2'] = F2
    print(f'F2 done {time.time() - t0:.0f}s')
    # ---------------------------------------------------------------- F3: falsification diagnostics, sensitivity
    diag = {}
    for n, o, sb in zip(names, obs, F1):
        if sb is not None:
            continue
        ts = tset_of(o, ALL)
        rest = {}
        for drop in ts:
            if drop == 'Cl':
                continue
            rest[drop] = _job((m, o, [t for t in ts if t != drop], K_EPS)) is not None
        diag[n] = rest
    R['F3_diag'] = diag
    sens = {}
    for k in (2.0, 3.5):
        sens[f'k={k}'] = run_jobs(pool, [(m, o, tset_of(o, ALL), k) for o in obs])
    m_wide = m.with_interval('Cl', 0, m.cl[0, 0], 220.0)
    sens['native Cl to 220 mg/L'] = run_jobs(pool, [(m_wide, o, tset_of(o, ALL), K_EPS) for o in obs])
    R['F3_sens'] = sens
    print(f'F3 done {time.time() - t0:.0f}s')
    # ---------------------------------------------------------------- F4: comparators
    mf = m.fixed(fixed_values(appA))
    R['F4_fixed'] = run_jobs(pool, [(mf, o, tset_of(o, ALL), K_EPS) for o in obs])
    bayes = {}
    for prior, alpha in (('Dirichlet(1)', 1.0), ('Dirichlet(0.25)', 0.25)):
        out = pool.map(_smc_job, [(m, o, tset_of(o, ALL), alpha, 1000 + i, 0, []) for i, o in enumerate(obs)])
        bayes[prior] = [dict(post=r['post'], stages=r['stages'], acc=r['acc']) for r in out]
    R['F4_bayes'] = bayes
    print(f'F4 done {time.time() - t0:.0f}s')
    # ---------------------------------------------------------------- F5a: retrospective test of the design rule
    M = 16
    rng = np.random.default_rng(7)
    retro = {}
    for held in (['Br'], ['d18O', 'd2H'], ['H3']):
        key = '+'.join(held)
        idx = [i for i, o in enumerate(obs) if all(h in o for h in held)]
        sims = pool.map(_smc_job, [(m, obs[i], [t for t in tset_of(obs[i], ALL) if t not in held], 1.0, 2000 + i, M,
                                    held) for i in idx])
        jobs, meta = [], []
        for i, sim in zip(idx, sims):
            o = obs[i]
            base = [t for t in tset_of(o, ALL) if t not in held]
            for vals in sim['sim']:
                o2 = {t: o[t] for t in base}
                for h, v in zip(held, vals):
                    o2[h] = (v, '')
                jobs.append((m, o2, base + held, K_EPS)); meta.append((i, 'pred'))
            jobs.append((m, {t: o[t] for t in base}, base, K_EPS)); meta.append((i, 'base'))
            jobs.append((m, o, tset_of(o, ALL), K_EPS)); meta.append((i, 'real'))
        out = run_jobs(pool, jobs)
        per = {}
        for (i, kind), sb in zip(meta, out):
            d = per.setdefault(i, dict(pred=[], base=None, real=None, pred_empty=[]))
            ds = decided(None if sb is None else np.array(sb))
            if kind == 'pred':
                d['pred'].append(ds); d['pred_empty'].append(sb is None)
            else:
                d[kind] = ds
                if kind == 'real':
                    d['real_empty'] = sb is None
                if kind == 'base':
                    d['base_empty'] = sb is None
        rows_out = []
        for i, d in per.items():
            p_ = np.array(d['pred'], float)
            rows_out.append(dict(well=names[i], base=d['base'], real=d['real'], pred=p_.mean(0).tolist(),
                                 base_empty=d['base_empty'], real_empty=d['real_empty'],
                                 pred_empty=float(np.mean(d['pred_empty']))))
        retro[key] = rows_out
    R['F5_retro'] = retro
    print(f'F5a done {time.time() - t0:.0f}s')
    # ---------------------------------------------------------------- F5b: characterising an end-member
    feas0 = [s_ is not None for s_ in F1]
    base_dec = [decided(None if s_ is None else np.array(s_)) for s_ in F1]
    actions = {}

    def shrink(model, src, draw):
        mm = model
        for key_, (lo_, hi_) in draw.items():
            mm = mm.with_interval(key_, src, lo_, hi_)
        return mm

    def draw_for(src, keys, mode):
        dr = {}
        for key_ in keys:
            lo, hi = (m.cl[src] if key_ == 'Cl' else m.tr[key_]['sig'][src])
            if mode == 'point':
                v = rng.uniform(lo, hi)
                err = {'Cl': 0.05 * v, 'Br': 0.05 * v, 'I': 0.05 * v, 'B': 0.05 * v, 'd18O': 0.2, 'd2H': 2.0,
                       'H3': 0.1 + 0.05 * v}[key_]
                dr[key_] = (max(v - err, lo), min(v + err, hi))
            else:                                    # 'half': a sub-interval of half the width
                a = rng.uniform(lo, lo + 0.5 * (hi - lo))
                dr[key_] = (a, a + 0.5 * (hi - lo))
        return dr

    every = ['Cl', 'Br', 'I', 'B', 'd18O', 'd2H', 'H3']
    plans = [('sample the brine', 3, every, 'point'), ('sample the brine', 3, every, 'half'),
             ('sample the imported water', 2, every, 'point'), ('sample the imported water', 2, every, 'half'),
             ('measure seawater tritium', 1, ['H3'], 'point')]
    CAND, KEEP = 240, 24
    feas_idx = [i for i in range(len(obs)) if feas0[i]]
    for label, src, keys, mode in plans:
        cands = [draw_for(src, keys, mode) for _ in range(CAND)]
        models = [shrink(m, src, dr) for dr in cands]
        jobs = [(mm, obs[i], tset_of(obs[i], ALL), K_EPS) for mm in models for i in feas_idx]
        ok = pool.map(_feas_job, jobs, chunksize=16)
        nf = len(feas_idx)
        consistent = [c for c in range(CAND) if all(ok[c * nf:(c + 1) * nf])]
        res = []
        if consistent:
            use = consistent[:KEEP]
            jobs = [(models[c], o, tset_of(o, ALL), K_EPS) for c in use for o in obs]
            out = run_jobs(pool, jobs)
            n = len(obs)
            for j, c in enumerate(use):
                d = out[j * n:(j + 1) * n]
                dec = np.array([decided(None if x is None else np.array(x)) for x in d], float)
                res.append(dict(dec=dec.sum(0).tolist(), draw={k_: list(v_) for k_, v_ in cands[c].items()}))
        actions[f'{label} ({mode})'] = dict(candidates=CAND, consistent=len(consistent), kept=res)
        print(f'  {label} ({mode}): consistent {len(consistent)}/{CAND}', f'{time.time() - t0:.0f}s')
    R['F5_actions'] = actions
    R['F5_base'] = np.array(base_dec, float).sum(0).tolist()
    pool.close()
    R['seconds'] = time.time() - t0
    json.dump(R, open(os.path.join(OUT, 'field.json'), 'w'), indent=1,
              default=lambda o: o.item() if hasattr(o, 'item') else o.tolist() if hasattr(o, 'tolist') else str(o))
    print(f'all done {R["seconds"]:.0f}s')


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
