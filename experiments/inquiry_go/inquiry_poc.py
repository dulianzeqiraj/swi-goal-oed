"""INQUIRY-GO, proof of concept: which next measurement decides the origin verdict?

usage: python inquiry_poc.py [n_truths] [workers] [lib_size] [seed]      -> res/inquiry_poc.json

The synthetic coastal section and the library of HYPOTHESIS-GO (../hipoteza_go/res/ensemble.npz, built by
../hipoteza_go/hip_ensemble.py). The truth is one member of the library with strengths and signatures drawn in
their intervals; chloride at four wells (two screens each) and four heads are known at the start. The verdict
is whether modern seawater supplies at least half of the chloride of one saline sample. A question is one more
measurement: chloride, bromide, oxygen-18 or tritium at one of the twenty samples. Five ways of choosing the
next question are compared. No field data are used."""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'hipoteza_go'))
import hip_infer as HI  # noqa: E402

INIT_CL = np.array([0, 1, 4, 5, 10, 11, 16, 17])      # scenario A of HYPOTHESIS-GO: four wells, two screens
INIT_W = np.array([0, 2, 5, 8])
TAU, MAXQ, NSCREEN, NTOP = 0.5, 6, 40, 5
GOAL_SRC = [0, 4, 5, 3, 1]                            # sea, legacy, deep, anthropogenic, lagoon
NV, K = HI.NV, HI.K_EPS
POLICIES = ['random', 'D-optimal', 'goal variance', 'widest outcome', 'INQUIRY', 'hybrid']
_E = None


def load():
    global _E
    if _E is None:
        z = np.load(os.path.join(HERE, '..', 'hipoteza_go', 'res', 'ensemble.npz'))
        ok = z['ok']
        _E = {k: z[k][ok] for k in z.files if z[k].shape[:1] == ok.shape}
    return _E


def mats(E, j):
    G = np.array([E[k][j] for k in HI.RESP]).T
    Wf = np.array([E[k][j] for k in HI.WAT]).T
    Wt = np.array([E[k][j] for k in HI.TRI]).T
    return tuple(np.where(np.abs(a) < HI.TINY, 0.0, a) for a in (G, Wf, Wt))


def row(M, key):
    t, i = key
    a = np.zeros(NV)
    if t == 'Cl':
        a[0:6] = M[0][i]
    elif t == 'Br':
        a[6:12] = M[0][i]
    elif t == 'd18O':
        a[12:15] = M[1][i]
    else:
        a[15:18] = M[2][i]
    return a


def tol(t, y):
    return K * HI.sd_of(t, y)


def consistent(t, lo, hi):
    """Outcomes y that a prediction in [lo, hi] can produce within the tolerance K sd(y)."""
    rel, ab = HI.NOISE[t]
    return (lo - K * ab) / (1.0 + K * rel), (hi + K * ab) / (1.0 - K * rel)


class Poly:
    """The strengths and signatures with which one member reproduces the data (scaled variables v = u / sc)."""

    def __init__(self, M, keys, y, eps, fix):
        F, lo, hi, sc = fix
        A = np.array([row(M, k) for k in keys])
        As, ys = (A * sc[None, :]) / eps[:, None], y / eps
        self.M, self.sc = M, sc
        self.Aub = np.vstack([As, -As, F])
        self.bub = np.r_[ys + 1.0, 1.0 - ys, np.zeros(len(F))]
        self.bounds = [(lo[v] / sc[v], None if np.isinf(hi[v]) else hi[v] / sc[v]) for v in range(NV)]
        self.box = (lo, np.where(np.isinf(hi), sc, hi))

    def lp(self, c, extra=None):
        Aub, bub = self.Aub, self.bub
        if extra is not None:
            Aub = np.vstack([Aub, extra[None, :]]); bub = np.r_[bub, 0.0]
        r = linprog(c, A_ub=Aub, b_ub=bub, bounds=self.bounds, method='highs')
        if r.status not in (0, 2):
            r = linprog(c, A_ub=Aub, b_ub=bub, bounds=self.bounds, method='highs-ipm')
        return r

    def feasible(self, extra=None):
        return self.lp(np.zeros(NV), extra).status != 2          # an unfinished programme never rules out

    def rng_of(self, a, extra=None):
        """[min, max] of a.u; an unfinished programme is replaced by the bound of the box (never by a guess)."""
        out = []
        for sg in (1.0, -1.0):
            r = self.lp(sg * a * self.sc, extra)
            if r.status == 2:
                return None
            if r.status == 0:
                out.append(sg * r.fun)
            else:
                lo, hi = self.box
                out.append(float(np.sum(np.minimum(a * lo, a * hi))) if sg > 0 else float(np.sum(np.maximum(a * lo, a * hi))))
        return out


def fixed(iv):
    F, lo, hi = HI.fixed_part(iv, HI.L6)
    S, R = iv[0], iv[1]
    sc = np.ones(NV)
    sc[0:6] = S[:, 1]; sc[6:12] = R[:, 1] * S[:, 1]
    sc[12:15] = np.maximum(np.abs(iv[2]).max(axis=1), 1.0); sc[15:18] = iv[3][:, 1]
    F = F * sc[None, :]
    F = F / np.abs(F).max(axis=1, keepdims=True)
    return F, lo, hi, sc


def class_rows(M, i_goal, k_goal, sc):
    g = np.zeros(NV); g[0:6] = -TAU * M[0][i_goal]; g[k_goal] += M[0][i_goal, k_goal]
    g = g * sc
    g = g / max(np.abs(g).max(), 1e-300)
    return {'yes': -g, 'no': g}


def union_len(iv):
    iv = sorted(iv); tot, (a, b) = 0.0, iv[0]
    for c, d in iv[1:]:
        if c > b:
            tot += b - a; a, b = c, d
        else:
            b = max(b, d)
    return tot + b - a


def inter_len(A, B):
    """Length of the intersection of two unions of intervals."""
    return union_len(A) + union_len(B) - union_len(A + B) if A and B else 0.0


class State:
    def __init__(self, E, mem, keys, truth, fix, goal, cache):
        self.E, self.truth, self.fix, self.goal, self.cache = E, truth, fix, goal, cache
        self.keys = list(keys); self.mem = list(mem); self.polys = {}
        self.refresh()

    def data(self):
        y = np.array([self.truth['obs'][t][i] for t, i in self.keys])
        return y, np.array([tol(t, v) for (t, _), v in zip(self.keys, y)])

    def refresh(self):
        y, eps = self.data()
        self.polys = {}
        for j in self.mem:
            p = Poly(self.cache[j], self.keys, y, eps, self.fix)
            if p.feasible():
                self.polys[j] = p
        self.mem = list(self.polys)
        self.classes()

    def classes(self):
        self.cls = {}
        for j, p in self.polys.items():
            cr = class_rows(p.M, self.goal[0], self.goal[1], p.sc)
            self.cls[j] = {c: (cr[c] if p.feasible(cr[c]) else None) for c in ('yes', 'no')}

    def verdict(self):
        if not self.mem:
            return 'empty'
        ny = sum(self.cls[j]['yes'] is not None for j in self.mem)
        nn = sum(self.cls[j]['no'] is not None for j in self.mem)
        return 'yes' if nn == 0 else 'no' if ny == 0 else None

    def add(self, key):
        self.keys.append(key); self.refresh()

    def subset(self, rng, n=NSCREEN):
        """Members for the screening of the questions: the rarer verdict first."""
        if len(self.mem) <= n:
            return list(self.mem)
        Y = [j for j in self.mem if self.cls[j]['yes'] is not None]
        N = [j for j in self.mem if self.cls[j]['no'] is not None]
        rare = Y if len(Y) <= len(N) else N
        take = list(rng.permutation(rare)[:n // 2])
        rest = [j for j in self.mem if j not in set(take)]
        return [int(j) for j in take + list(rng.permutation(rest)[:n - len(take)])]

    def outcome_sets(self, key, by_class=True, members=None):
        t = key[0]
        O = {'yes': [], 'no': []} if by_class else {'all': []}
        for j in (self.mem if members is None else members):
            p = self.polys[j]
            a = row(p.M, key)
            for c in O:
                ex = self.cls[j][c] if by_class else None
                if by_class and ex is None:
                    continue
                r = p.rng_of(a, ex)
                if r is not None:
                    O[c].append(consistent(t, r[0], r[1]) if by_class else (r[0], r[1]))
        return O


def candidates(keys):
    done = set(keys)
    return [(t, i) for t in ('Cl', 'Br', 'd18O', 'H3') for i in range(HI.NS) if (t, i) not in done]


def width_of(st, key, members=None):
    O = st.outcome_sets(key, by_class=False, members=members)['all']
    lo, hi = min(a for a, _ in O), max(b for _, b in O)
    return (hi - lo) / tol(key[0], 0.5 * (lo + hi))


def pick_widest(st, rng):
    sub = st.subset(rng)
    sc = sorted(((width_of(st, key, sub), key) for key in candidates(st.keys)), reverse=True)
    if len(sub) == len(st.mem):
        return sc[0][1], sc[0][0]
    sc = sorted(((width_of(st, key), key) for _, key in sc[:NTOP]), reverse=True)
    return sc[0][1], sc[0][0]


def decisive(st, key, members=None):
    """Share of the possible outcomes of a question that leave one verdict only, and the width of the outcomes."""
    O = st.outcome_sets(key, members=members)
    if not O['yes'] or not O['no']:
        return None
    allv = O['yes'] + O['no']
    un = union_len(list(allv))
    d = 1.0 - inter_len(O['yes'], O['no']) / un if un > 0 else 0.0
    lo, hi = min(a for a, _ in allv), max(b for _, b in allv)
    return d, (hi - lo) / tol(key[0], 0.5 * (lo + hi))


def pick_inquiry(st, rng):
    """The question with the largest share of outcomes that leave one verdict only; ties and the case in which no
    question can decide go to the widest outcome. Screening on a subset of the members, then the exact value over
    all members for the best NTOP."""
    sub = st.subset(rng)
    sc = [(decisive(st, key, sub), key) for key in candidates(st.keys)]
    sc = sorted(((v, key) for v, key in sc if v is not None), reverse=True)
    if not sc:
        return None, None
    if len(sub) < len(st.mem):
        sc = sorted(((decisive(st, key), key) for _, key in sc[:NTOP]), reverse=True)
    return sc[0][1], sc[0][0][0]


class Gauss:
    """Linear-Gaussian criteria built from sample pairs only (non-intrusive, as in Koval & Nicholson 2025): the
    log-determinant of the posterior covariance of the six strengths (D-optimal), or the posterior variance of the
    goal share."""

    def __init__(self, mem, rng, i_goal, k_goal, cache, iv, goal, n=4000):
        S_, R_, D_, T_ = iv
        js = rng.choice(mem, n)
        S = rng.uniform(S_[:, 0], S_[:, 1], (n, 6)); rho = rng.uniform(R_[:, 0], R_[:, 1], (n, 6))
        d = rng.uniform(D_[:, 0], D_[:, 1], (n, 3)); t = rng.uniform(T_[:, 0], T_[:, 1], (n, 3))
        dat = np.zeros((n, 4 * HI.NS)); q = np.zeros(n)
        for r_, j in enumerate(js):
            G, Wf, Wt = cache[j]
            dat[r_] = np.r_[G @ S[r_], G @ (rho[r_] * S[r_]), Wf @ d[r_], Wt @ t[r_]]
            q[r_] = G[i_goal, k_goal] * S[r_, k_goal] / max(G[i_goal] @ S[r_], 1e-12)
        self.allk = [(tt, i) for tt in ('Cl', 'Br', 'd18O', 'H3') for i in range(HI.NS)]
        nz = np.array([HI.sd_of(k[0], dat[:, c].mean()) for c, k in enumerate(self.allk)]) ** 2
        P = (S / S.std(axis=0)) if not goal else q[:, None]
        C = np.cov(np.c_[P, dat].T); m = P.shape[1]
        self.Cpp, self.Cpd, self.Cdd = C[:m, :m], C[:m, m:], C[m:, m:] + np.diag(nz)

    def rank(self, keys):
        """Candidates in increasing order of the criterion after adding them to the measured keys."""
        chosen = [self.allk.index(tuple(k)) for k in keys]; out = []
        for c in range(len(self.allk)):
            if c in chosen:
                continue
            ix = chosen + [c]
            post = self.Cpp - self.Cpd[:, ix] @ np.linalg.solve(self.Cdd[np.ix_(ix, ix)], self.Cpd[:, ix].T)
            out.append((np.linalg.slogdet(post)[1], self.allk[c]))
        return [k for _, k in sorted(out)]


def pick_hybrid(st, gq):
    """Screening by the goal variance (no linear programme), then the exact decisive share for the best NTOP."""
    top = gq.rank(st.keys)[:NTOP]
    sc = [(decisive(st, key), -n, key) for n, key in enumerate(top)]
    sc = sorted(((v, n, key) for v, n, key in sc if v is not None), reverse=True)
    return (sc[0][2], sc[0][0][0]) if sc else (top[0], None)


def one(args):
    seed, lib_size = args
    E = load(); rng = np.random.default_rng(seed)
    n_all = len(E['head'])
    jt = int(rng.integers(n_all))
    world = 'W1' if rng.uniform() < 0.5 else 'W0'
    truth = HI.draw_truth({k: E[k][jt] for k in E}, rng, world)
    lib = np.unique(np.r_[rng.choice(n_all, min(lib_size, n_all), replace=False), jt])
    hm = np.max(np.abs(E['head'][lib][:, INIT_W] - truth['obs']['head'][INIT_W][None, :]), axis=1) <= K * HI.SD_HEAD
    mem = [int(j) for j in lib[hm]]
    cache = {j: mats(E, j) for j in mem}
    iv = HI.intervals(); fix = fixed(iv)
    keys0 = [('Cl', int(i)) for i in INIT_CL]
    out = dict(seed=seed, world=world, truth_in=bool(jt in mem), n_head=len(mem))
    goal = None
    st = State(E, mem, keys0, truth, fix, (int(INIT_CL[0]), 0), cache)
    out['truth_fits'] = bool(jt in st.mem)
    for i in INIT_CL[np.argsort(-truth['obs']['Cl'][INIT_CL])]:
        if truth['obs']['Cl'][i] < 150.0 or not st.mem or goal is not None:
            break
        for k in GOAL_SRC:
            st.goal = (int(i), k); st.classes()
            if st.verdict() is None:
                goal = (int(i), k); break
    if goal is None:
        out['skip'] = True
        return out
    i_goal, k_goal = goal
    ny = sum(st.cls[j]['yes'] is not None for j in st.mem); nn = sum(st.cls[j]['no'] is not None for j in st.mem)
    out.update(skip=False, goal=[i_goal, HI.SRC[k_goal]], n0=len(st.mem), n_yes=ny, n_no=nn,
               cl=float(truth['obs']['Cl'][i_goal]), share=float(truth['share'][i_goal, k_goal]),
               true_verdict='yes' if truth['share'][i_goal, k_goal] >= TAU else 'no', pol={})
    mem0 = list(st.mem)
    gd = Gauss(mem, np.random.default_rng(seed + 7), i_goal, k_goal, cache, iv, False)
    gq = Gauss(mem, np.random.default_rng(seed + 7), i_goal, k_goal, cache, iv, True)
    for pol in POLICIES:
        st = State(E, mem0, keys0, truth, fix, goal, cache)
        asked, info, v = [], [], None
        prng = np.random.default_rng(seed + 99)
        for step in range(MAXQ):
            if pol == 'random':
                c = candidates(st.keys); key = c[int(prng.integers(len(c)))]; sc_ = None
            elif pol == 'D-optimal':
                key, sc_ = gd.rank(st.keys)[0], None
            elif pol == 'goal variance':
                key, sc_ = gq.rank(st.keys)[0], None
            elif pol == 'hybrid':
                key, sc_ = pick_hybrid(st, gq)
            elif pol == 'widest outcome':
                key, sc_ = pick_widest(st, prng)
            else:
                key, sc_ = pick_inquiry(st, prng)
            if key is None:
                break
            st.add(key); asked.append(list(key)); info.append(sc_)
            v = st.verdict()
            if v is not None:
                break
        out['pol'][pol] = dict(asked=asked, info=[None if x is None else float(x) for x in info], verdict=v, n=len(asked),
                              n_left=len(st.mem), truth_left=bool(jt in st.mem))
    return out


def main():
    nt = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    nw = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    lib = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 2027
    t0 = time.time(); res = []
    with Pool(nw) as pool:
        for r in pool.imap_unordered(one, [(seed + 1000 * k, lib) for k in range(nt)]):
            res.append(r)
            print(len(res), 'of', nt, 'skip' if r['skip'] else {p: (d['n'], d['verdict']) for p, d in r['pol'].items()},
                  f'{time.time() - t0:.0f}s', flush=True)
            json.dump(dict(lib=lib, maxq=MAXQ, tau=TAU, runs=res), open(os.path.join(HERE, 'res', 'inquiry_poc.json'), 'w'))
    print('done', f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
