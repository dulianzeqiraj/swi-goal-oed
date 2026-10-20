"""HARTA-GO, stage 3: how many model runs does each design criterion need?
For training sizes N (random subsets of the 12 000-member training ensemble, each member with one noisy
reading per well, noise seed 3), every 3- and 5-well design is scored for the three goals by
  rew    nested Monte Carlo with the N runs (two folds: inner / outer), plug-in
  gauss  map family 'raw, linear mean, constant spread' (ensemble Kalman conditional), BA bound
  ns     map family 'normal scores, linear mean, constant spread' (Gaussian copula), BA bound
  harta  map family 'normal scores, quadratic mean, spread depending on readings', BA bound
and compared with the reference EIG (harta_ref.npz). The project's linearized criteria (no ensemble:
hA for rA, pragLin for rAB, area for rArea; fk_prag_geo.py) are read from the PRAG-GO result files.
Metrics: share of the optimum reached by the chosen design, Spearman correlation with the reference,
and the mean share of the constrained optimum when each candidate well is available with
probability 1/2 (300 random availability patterns, the same for all methods).
Run: python3 harta_static.py   (about 30 minutes on 4 cores). Output: harta_static.json, .npz
"""
import json, os, time, itertools
import numpy as np
from multiprocessing import Pool
from scipy.stats import spearmanr
import harta as H

Z = np.load('harta_ens.npz'); RF = np.load('harta_ref.npz')
TR = Z['train']
YTR = TR[:, :H.NC] + H.SN * np.random.default_rng(3).standard_normal((len(TR), H.NC))
NS_ = [250, 500, 1000, 2000, 4000]
REPS = 8
METHODS = ['rew', 'gauss', 'ns', 'harta']
FAM = {'gauss': ('raw', 1, False), 'ns': ('ns', 1, False), 'harta': ('ns', 2, True)}
PG = os.path.join('..', 'prag_go_fushe_kuqe', 'res_geo')
LINCOL = {'rA': 2, 'rAB': 4, 'rArea': 0}      # columns hA, pragLin, area of PRAG-GO's LIN array
rngm = np.random.default_rng(7)
MASKS = rngm.random((300, H.NC)) < 0.5


def metrics(score, ref, D):
    b = int(np.argmax(score)); best = ref.max()
    Dm = np.array(D)
    cons = []
    for m in MASKS:
        ok = m[Dm].all(1)
        if ok.sum() < 2:
            continue
        i = np.flatnonzero(ok)
        cons.append(ref[i[np.argmax(score[i])]] / ref[i].max())
    return dict(pct=float(100 * ref[b] / best), rho=float(spearmanr(score, ref).correlation), cons=float(100 * np.mean(cons)))


def run(args):
    N, rep, k = args
    D = [tuple(d) for d in RF[f'D{k}']]
    rng = np.random.default_rng(1000 * N + rep)
    sub = rng.choice(len(TR), N, replace=False)
    Y, E = YTR[sub], TR[sub]
    out = {}
    t0 = time.time()
    perm = rng.permutation(N); a, b = perm[: N // 2], perm[N // 2:]
    gl = H.goal_of(E)
    REW = 0.5 * (H.eig_rew(E[a, :H.NC], gl[a], Y[b], D) + H.eig_rew(E[b, :H.NC], gl[b], Y[a], D))
    trew = (time.time() - t0) / 3
    for g, goal in enumerate(H.GOALS):
        ref = RF[f'EX{k}'][:, g]
        out[(goal, 'rew')] = dict(metrics(REW[:, g], ref, D), sec=trew)
        for meth in METHODS[1:]:
            t0 = time.time()
            kind, deg, het = FAM[meth]
            s = H.eig_ba(Y, E, D, goal, kind, deg, het, seed=rep)
            out[(goal, meth)] = dict(metrics(s, ref, D), sec=time.time() - t0)
    return (N, rep, k), out


if __name__ == '__main__':
    t0 = time.time()
    jobs = [(N, r, k) for k in (3, 5) for N in NS_ for r in range(REPS)]
    res = {}
    with Pool(4) as p:
        for key, out in p.imap_unordered(run, jobs):
            res[key] = out
            print(key, f'{time.time() - t0:.0f}s', {f'{g}/{m}': round(v['pct'], 1) for (g, m), v in out.items()}, flush=True)
    # linearized criteria (no ensemble) and nested MC with all 12 000 runs (PRAG-GO's exact EIG, own outer set)
    extra = {}
    for k in (3, 5):
        z = np.load(os.path.join(PG, f'prag_base_d{k}.npz'))
        assert (z['D'] == RF[f'D{k}']).all()
        D = [tuple(d) for d in RF[f'D{k}']]
        for g, goal in enumerate(H.GOALS):
            ref = RF[f'EX{k}'][:, g]
            extra[(k, goal, 'lin')] = metrics(z['LIN'][:, LINCOL[goal]], ref, D)
            extra[(k, goal, 'rew12000')] = metrics(z['EX'][:, g], ref, D)
    # summary: mean over replicates
    S = {}
    for k in (3, 5):
        for goal in H.GOALS:
            for meth in METHODS:
                for N in NS_:
                    v = [res[(N, r, k)][(goal, meth)] for r in range(REPS)]
                    S[f'{k}|{goal}|{meth}|{N}'] = {m: float(np.mean([x[m] for x in v])) for m in ('pct', 'rho', 'cons', 'sec')} | \
                        {m + '_min': float(np.min([x[m] for x in v])) for m in ('pct', 'cons')}
            for meth in ('lin', 'rew12000'):
                S[f'{k}|{goal}|{meth}|-'] = extra[(k, goal, meth)]
    json.dump(S, open('harta_static.json', 'w'), indent=1)
    print(f'done {time.time() - t0:.0f}s')
