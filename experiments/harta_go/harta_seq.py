"""HARTA-GO, stage 4: sequential (adaptive) choice of three monitoring wells.
For each of 1 000 synthetic truths (the 'test' ensemble, noisy readings with seed 13) a policy picks a
well, reads it, picks the next one given the reading, and so on, three times. The next well maximizes
the expected information gain about the goal given the readings so far, computed with the policy's own
conditional law:
  adapt-gauss   map family 'raw, linear, constant spread' (ensemble Kalman), fitted on 12 000 runs
  adapt-harta   map family 'normal scores, quadratic, spread depending on readings', 12 000 runs
  adapt-harta1k the same map fitted on 1 000 runs
  adapt-rew     likelihood re-weighting of the 12 000 runs (predictive by 64 systematic draws)
and is compared with two fixed designs: the reference optimum of the 3-well designs (static-ref) and
the design chosen by the project's linearized criterion (static-lin). Every final posterior is computed
with the 48 000-member reference ensemble; the score is the information gained about the goal,
H(G) + E[log p_ref(G* | readings)], with G* the goal of the truth.
Run: python3 harta_seq.py [goal] [n_truths]   (goal rA, rAB or rArea; about 10 minutes on 4 cores per goal).
Output: harta_seq_<goal>.json
"""
import os, sys, json, time
import numpy as np
from multiprocessing import Pool
import harta as H

GOAL = sys.argv[1] if len(sys.argv) > 1 else 'rAB'
NTRUTH = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
GI = H.GOALS.index(GOAL)
Z = dict(np.load('harta_ens.npz', allow_pickle=False)); RF = dict(np.load('harta_ref.npz'))   # eager: forked workers must not share a lazy file
TR = Z['train']; TE = Z['test'][:NTRUTH]; REF = Z['ref'].astype(np.float32)
YTR = TR[:, :H.NC] + H.SN * np.random.default_rng(3).standard_normal((len(TR), H.NC))
YTE = TE[:, :H.NC] + H.SN * np.random.default_rng(13).standard_normal((len(TE), H.NC))
GTE = H.goal_of(TE)[:, GI]
GREF = H.goal_of(Z['ref'])[:, GI].astype(np.float64)
GTR = H.goal_of(TR)[:, GI].astype(np.float64)
PG = os.path.join('..', 'prag_go_fushe_kuqe', 'res_geo')
LINCOL = {'rA': 2, 'rAB': 4, 'rArea': 0}
BUDGET = 3


class MapPolicy:
    def __init__(self, n, kind, deg, het, seed=0):
        sub = np.random.default_rng(seed).choice(len(TR), n, replace=False) if n < len(TR) else np.arange(len(TR))
        self.sp = H.Space(YTR[sub], TR[sub], kind)
        self.fit = H.Fit(self.sp.data(YTR[sub]), self.sp.goals(TR[sub]), deg, het)
        self.cache = {}

    def comp_data(self, o, k):
        """map component of reading k given readings o: mean and log-variance coefficients."""
        key = (tuple(o), k)
        if key not in self.cache:
            f = self.fit; ix = H.idx_of(o, f.deg); lix = H.lin_idx(o)
            A = f.G[np.ix_(ix, ix)] + f.lam * f.n * np.eye(len(ix))
            beta = np.linalg.solve(A, f.G[ix, 1 + k])
            r = f.P[:, 1 + k] - f.P[:, ix] @ beta
            if f.hetero:
                L = f.P[:, lix]
                gamma = np.linalg.solve(f.G[np.ix_(lix, lix)] + 1e-8 * np.eye(len(lix)), L.T @ np.log(r * r + 1e-12))
                gamma[0] += H.LOGCHI
            else:
                gamma = np.zeros(len(lix)); gamma[0] = np.log(np.mean(r * r))
            self.cache[key] = (beta, ix, gamma, lix)
        return self.cache[key]

    def pgoal(self, d, Zrows):
        return H.prob_goal(self.fit, tuple(sorted(d)), GOAL, H.features(Zrows), self.sp)

    def choose(self, o, zo):
        z = np.zeros(H.NC); z[o] = zo
        p0 = self.pgoal(o, z[None])[0]; best, bk = -1e9, None
        for k in range(H.NC):
            if k in o:
                continue
            beta, ix, gamma, lix = self.comp_data(o, k)
            P = H.features(z[None])
            m = (P[:, ix] @ beta)[0]; s = np.exp(0.5 * (P[:, lix] @ gamma))[0]
            rows = np.repeat(z[None], len(H.ghx), 0); rows[:, k] = m + s * H.ghx
            e = H.hb(p0) - (H.ghw * H.hb(self.pgoal(o + [k], rows))).sum()
            if e > best:
                best, bk = e, k
        return bk

    def latent(self, k, y):
        return float(self.sp.f[k](np.array([y]))[0])


class RewPolicy:
    def __init__(self):
        self.Eh = TR[:, :H.NC]; self.g = GTR

    def choose(self, o, yo):
        if o:
            S = ((yo[None, :] - self.Eh[:, o]) ** 2).sum(1); w = np.exp(-(S - S.min()) / (2 * H.SN ** 2))
        else:
            w = np.ones(len(self.Eh))
        w /= w.sum(); p0 = w @ self.g
        u = (np.arange(64) + 0.5) / 64
        idx = np.minimum(np.searchsorted(np.cumsum(w), u), len(w) - 1)
        rng = np.random.default_rng(len(o) * 7919 + int(1e3 * yo.sum()) % 100000)
        best, bk = -1e9, None
        for k in range(H.NC):
            if k in o:
                continue
            yk = self.Eh[idx, k] + H.SN * rng.standard_normal(64)
            L = np.exp(-(yk[:, None] - self.Eh[None, :, k]) ** 2 / (2 * H.SN ** 2)) * w[None, :]
            p = (L @ self.g) / L.sum(1)
            e = H.hb(p0) - H.hb(p).mean()
            if e > best:
                best, bk = e, k
        return bk


POL = {}


def init():
    POL['gauss'] = MapPolicy(12000, 'raw', 1, False)
    POL['harta'] = MapPolicy(12000, 'ns', 2, True)
    POL['harta1k'] = MapPolicy(1000, 'ns', 2, True, seed=5)
    POL['rew'] = RewPolicy()


def run_truth(i):
    out = {}
    for name in ('gauss', 'harta', 'harta1k', 'rew'):
        pol = POL[name]; o = []; t0 = time.time()
        for _ in range(BUDGET):
            if name == 'rew':
                k = pol.choose(o, YTE[i, o])
            else:
                zo = np.array([pol.latent(j, YTE[i, j]) for j in o])
                k = pol.choose(o, zo)
            o.append(k)
        out[name] = (o, time.time() - t0)
    return i, out


def post_ref(o, y):
    S = ((y[None, :] - REF[:, o]) ** 2).sum(1, dtype=np.float64)
    w = np.exp(-(S - S.min()) / (2 * H.SN ** 2))
    return float(w @ GREF / w.sum()), float(w.sum() ** 2 / (w @ w))


if __name__ == '__main__':
    t0 = time.time()
    k = BUDGET; D = [tuple(d) for d in RF[f'D{k}']]
    sref = list(D[int(RF[f'EX{k}'][:, GI].argmax())])
    lin = np.load(os.path.join(PG, f'prag_base_d{k}.npz'))['LIN'][:, LINCOL[GOAL]]
    slin = list(D[int(lin.argmax())])
    with Pool(4, initializer=init) as p:
        R = dict(p.map(run_truth, range(len(TE)), chunksize=10))
    H0 = H.hb(GREF.mean())
    res = {'goal': GOAL, 'H0': H0, 'n_truths': len(TE), 'static_ref': Z['ids'][sref].tolist(), 'static_lin': Z['ids'][slin].tolist(), 'policies': {}}
    LS = {}
    for name in ('static_ref', 'static_lin', 'gauss', 'harta', 'harta1k', 'rew'):
        ls, br, acc, ess, sec, firsts = [], [], [], [], [], {}
        for i in range(len(TE)):
            if name.startswith('static'):
                o = sref if name == 'static_ref' else slin; s = 0.0
            else:
                o, s = R[i][name]
            p, e = post_ref(list(o), YTE[i, list(o)])
            g = GTE[i]
            ls.append(np.log(max(p if g else 1 - p, 1e-9))); br.append((p - g) ** 2); acc.append((p > 0.5) == g)
            ess.append(e); sec.append(s); f = Z['ids'][o[0]]; firsts[f] = firsts.get(f, 0) + 1
        LS[name] = np.array(ls)
        n_designs = len({tuple(sorted(R[i][name][0])) for i in range(len(TE))}) if not name.startswith('static') else 1
        res['policies'][name] = dict(info=float(H0 + np.mean(ls)), info_se=float(np.std(ls) / np.sqrt(len(ls))),
                                     brier=float(np.mean(br)), acc=float(np.mean(acc)), ess=float(np.mean(ess)),
                                     sec_per_truth=float(np.mean(sec)), n_distinct_designs=n_designs, first_well=firsts)
        print(name, {k_: (round(v, 4) if isinstance(v, float) else v) for k_, v in res['policies'][name].items() if k_ != 'first_well'}, flush=True)
    # paired differences against the static reference optimum (same truths, same readings)
    for name in res['policies']:
        dl = LS[name] - LS['static_ref']
        res['policies'][name]['gain_vs_static_ref'] = float(dl.mean())
        res['policies'][name]['gain_se'] = float(dl.std() / np.sqrt(len(dl)))
        print(name, 'gain vs static_ref %.4f +- %.4f' % (dl.mean(), dl.std() / np.sqrt(len(dl))))
    json.dump(res, open(f'harta_seq_{GOAL}.json', 'w'), indent=1)
    print(f'done {time.time() - t0:.0f}s')
