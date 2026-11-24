"""INQUIRY-GO on the stored Fushe-Kuqe ensemble of HYPOTHESIS-GO: which next measurement decides an open verdict?

usage: python fk_inquiry.py [workers]        -> res/fk_inquiry.json   (field results: not for the public repository)

Needs ../hipoteza_go/res_fk/ensemble_fk.npz and fk_results_second.json (python ../hipoteza_go/fk_run.py). The set of
explanations is the one of the Fushe-Kuqe note: the simulations of the union (heads and chloride within the
tolerance), the six source strengths in their intervals and the unknown positions of the four sampled wells in
their bands (binary variables). A question is the chloride of a new sample at a chosen distance and screen, the
chloride of another screen at the site of a sampled well, or the bromide of a sampled well."""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
from scipy.optimize import LinearConstraint, Bounds

HERE = os.path.dirname(os.path.abspath(__file__))
HIP = os.path.join(HERE, '..', 'hipoteza_go')
sys.path.insert(0, HIP)
import fk_infer as I  # noqa: E402

TAU = 0.5
GAP = float(os.environ.get('FK_GAP', '0.02'))            # relative gap at which a programme stops
SEVEN = os.environ.get('FK_SEVEN', '0') == '1'       # with the squeeze of the cover as a seventh source
NS = 7 if SEVEN else 6
SCREENS = ['top', 'middle', 'base']                    # 'sh', 'mid', 'dp' of fk_core.screen_cells
# Br/Cl by mass of the six sources: the illustrative literature intervals of HYPOTHESIS-GO (hip_infer.BR), not
# measured at the site
BR = np.array([[3.35e-3, 3.50e-3], [3.35e-3, 3.50e-3], [3.0e-3, 5.0e-3], [1.2e-3, 2.8e-3], [2.9e-3, 3.8e-3],
               [2.9e-3, 3.8e-3]])
if SEVEN:
    BR = np.vstack([BR, [2.9e-3, 3.8e-3]])
BR_SD = (0.05, 0.005)                                  # relative and absolute error of a bromide analysis (mg/L)
VERDICTS = ([('340', 'RS'), ('340', 'DB'), ('340', 'SQ')] if SEVEN else
            [('340', 'MS'), ('340', 'RS'), ('340', 'DB'), ('503', 'MS')])
SRC = I.SRC + (['SQ'] if SEVEN else [])
RAW = 'fk_inquiry7_raw.json' if SEVEN else 'fk_inquiry_raw.json'
_G = {}


def load():
    if not _G:
        z = np.load(os.path.join(HIP, 'res_fk', 'ensemble_fk.npz'))
        ok = z['ok'] & np.isfinite(z['h_lit'])
        E = {k: (z[k][ok] if z[k].shape[:1] == ok.shape else z[k]) for k in z.files}
        R = json.load(open(os.path.join(HIP, 'res_fk', 'fk_results_second.json')))
        y, eps = I.data()
        lo, hi = I.box(I.FULL)
        mem = list(R['union_members'])
        if SEVEN:
            import fk_squeeze as FS
            zq = np.load(os.path.join(HERE, 'res', 'fk_squeeze_resp.npz')); zt = np.load(os.path.join(HERE, 'res', 'fk_squeeze_trans.npz'))
            fq = json.load(open(os.path.join(HERE, 'res', 'fk_squeeze.json')))
            mem = [r['j'] for r in fq['runs'] if r['feas7']]
            _G['sq'] = {int(j): zq['G_SQ'][n].astype(float) * FS.S_CAP for n, j in enumerate(zq['members'])}
            _G['fade'] = {int(j): zt['G_T'][n].astype(float) for n, j in enumerate(zt['members'])}
            _G['after'] = [float(a) for a in zt['after']]
            lo, hi = np.r_[lo, 0.0], np.r_[hi, 1.0]                 # the squeeze strength in units of its cap
        _G.update(E=E, R=R, y=y, eps=eps, lo=lo, hi=hi, cols=[np.array(b) for b in R['bands']], scr=R['screens'],
                  kap=R['union']['kappa_eff'], mem=mem,
                  wid={w[0]: n for n, w in enumerate(I.WELLS)})
    return _G


def resp_all(j):
    """Responses of simulation j at every column and screen, to the six sources (and to the squeeze at its cap)."""
    g = load()
    r = clean(g['E']['resp'][j])
    return np.concatenate([r, g['sq'][j][:, :, None]], axis=2) if SEVEN else r


def clean(a):
    a = np.asarray(a, float)
    a = np.where(np.isfinite(a), a, 0.0)
    return np.where(np.abs(a) < 1e-12, 0.0, a)


class Model:
    """Mixed-integer set of one simulation: x = [S (6), z (positions), v (1), B (6)].  Positions that the box of the
    strengths cannot bring within the tolerance are removed, and every big-M is the smallest valid one."""

    def __init__(self, j):
        g = load()
        self.j = j
        y, eps, kap, lo, hi = g['y'], g['eps'], g['kap'], g['lo'], g['hi']
        ra = resp_all(j)
        G0 = [ra[c, q, :] for c, q in zip(g['cols'], g['scr'])]
        self.keep, self.G = [], []
        for Gi, yi, ei in zip(G0, y, eps):
            a, b = Gi @ lo, Gi @ hi
            kp = np.flatnonzero((a <= yi + kap * ei) & (b >= yi - kap * ei))
            self.keep.append(kp); self.G.append(Gi[kp])
        self.empty = any(len(k) == 0 for k in self.keep)
        self.npos = [len(a) for a in self.G]
        self.off = np.r_[NS, NS + np.cumsum(self.npos)].astype(int)
        self.iv = int(self.off[-1]); self.ib = self.iv + 1
        self.nv = self.ib + NS
        self.lo, self.hi = lo, hi
        A, ub = [], []
        for i, (Gi, yi, ei) in enumerate(zip(self.G, y, eps)):
            a, b = Gi @ lo, Gi @ hi
            for p in range(len(Gi)):
                M = (b[p] - yi - kap * ei) / ei
                if M > 0:
                    r = np.zeros(self.nv); r[:NS] = Gi[p] / ei; r[self.off[i] + p] = M
                    A.append(r); ub.append(yi / ei + kap + M)
                M = (yi - kap * ei - a[p]) / ei
                if M > 0:
                    r = np.zeros(self.nv); r[:NS] = -Gi[p] / ei; r[self.off[i] + p] = M
                    A.append(r); ub.append(-yi / ei + kap + M)
        for k in range(NS):                                        # bromide of every source between its ratios
            r = np.zeros(self.nv); r[self.ib + k] = 1.0; r[k] = -BR[k, 1]; A.append(r); ub.append(0.0)
            r = np.zeros(self.nv); r[self.ib + k] = -1.0; r[k] = BR[k, 0]; A.append(r); ub.append(0.0)
        self.A, self.ub = np.array(A), np.array(ub)
        Aeq = np.zeros((len(self.G), self.nv))
        for i in range(len(self.G)):
            Aeq[i, self.off[i]:self.off[i + 1]] = 1.0
        self.Aeq = Aeq
        self.integ = np.zeros(self.nv); self.integ[NS:self.iv] = 1.0
        self.vmax = 1.2 * float(np.max(ra @ hi))
        self.lob = np.r_[lo, np.zeros(self.iv - NS), -self.vmax, np.zeros(NS)]
        self.hib = np.r_[hi, np.ones(self.iv - NS), self.vmax, BR[:, 1] * hi]

    def tie(self, w, rows, into='S'):
        """Rows that make v equal to rows[p] . S (or . B) at the chosen position p of well w (rows of the kept
        positions), with the range of v."""
        s0 = 0 if into == 'S' else self.ib
        blo, bhi = self.lob[s0:s0 + NS], self.hib[s0:s0 + NS]
        a, b = rows @ blo, rows @ bhi
        vlo, vhi = float(a.min()), float(b.max())
        sc = max(vhi, 1e-9)
        A, ub = [], []
        for p in range(self.npos[w]):
            r = np.zeros(self.nv); r[self.iv] = 1.0 / sc; r[s0:s0 + NS] = -rows[p] / sc; r[self.off[w] + p] = (vhi - a[p]) / sc
            A.append(r); ub.append((vhi - a[p]) / sc)
            r = np.zeros(self.nv); r[self.iv] = -1.0 / sc; r[s0:s0 + NS] = rows[p] / sc; r[self.off[w] + p] = (b[p] - vlo) / sc
            A.append(r); ub.append((b[p] - vlo) / sc)
        r = np.zeros(self.nv); r[self.iv] = 1.0 / sc; A.append(r); ub.append(vhi / sc)
        r = np.zeros(self.nv); r[self.iv] = -1.0 / sc; A.append(r); ub.append(-vlo / sc)
        return np.array(A), np.array(ub)

    def cls(self, w, k, yes, tau=TAU):
        """Rows of the verdict 'source k supplies at least tau of the chloride of well w' (or its negation)."""
        A, ub = [], []
        e = load()['eps'][w]
        for p in range(self.npos[w]):
            f = -tau * self.G[w][p]; f[k] += self.G[w][p][k]
            fmin = float(np.sum(np.minimum(f * self.lo, f * self.hi))); fmax = float(np.sum(np.maximum(f * self.lo, f * self.hi)))
            M = (-fmin if yes else fmax) / e
            if M <= 0:
                continue
            r = np.zeros(self.nv); r[:NS] = (-f if yes else f) / e; r[self.off[w] + p] = M
            A.append(r); ub.append(M)
        return (np.array(A), np.array(ub)) if A else (np.zeros((0, self.nv)), np.zeros(0))

    def solve(self, c, extra=(), tl=4.0, gap=GAP, relax=False):
        A, ub = self.A, self.ub
        for a_, u_ in extra:
            if len(u_):
                A = np.vstack([A, a_]); ub = np.r_[ub, u_]
        cons = [LinearConstraint(A, -np.inf, ub), LinearConstraint(self.Aeq, 1.0, 1.0)]
        return I.milp(c, constraints=cons, integrality=(0 * self.integ if relax else self.integ), bounds=Bounds(self.lob, self.hib),
                      options=dict(time_limit=tl, mip_rel_gap=gap))

    def rng(self, c, extra=(), relax=False):
        """[min, max] of c.x, None if the set is empty; nan where the solver did not finish.  The solver stops at
        a relative gap GAP; the dual bound is returned, so the interval is never too narrow."""
        out = []
        for sg in (1.0, -1.0):
            r = self.solve(sg * c, extra, relax=relax)
            if r.status == 2:
                return None
            ok = r.status == 0 and r.x is not None
            bd = getattr(r, 'mip_dual_bound', None)
            if bd is not None and np.isfinite(bd):
                val = min(r.fun, bd) if ok else bd              # the dual bound is valid also at the time limit
            else:
                val = r.fun if ok else np.nan
            out.append(sg * val)
        return out


def S_MAXCL(G, hi):
    return max(float(np.max(a @ hi)) for a in G)


DIST = [2.5, 3.5, 4.5, 5.5] if SEVEN else [1.5, 2.5, 3.5, 4.5, 5.5, 6.5]      # km from the shoreline, new samples
SITE = [('340', 1), ('340', 2)] if SEVEN else [('340', 1), ('340', 2), ('503', 0), ('503', 2)]
BROM = ['340'] if SEVEN else ['340', '503']
AGAIN = [('340', 10.0), ('340', 20.0)] if SEVEN else []      # the same well again, years after the heads settle


def questions():
    g = load(); d = g['E']['dist']
    Q = []
    for x in DIST:
        c = int(np.argmin(np.abs(d - x) + (np.arange(len(d)) < 13) * 9.0))
        for s_ in range(3):
            Q.append(dict(kind='new', col=c, dist=float(d[c]), screen=s_, label=f'new sample at {d[c]:.1f} km, {SCREENS[s_]} screen'))
    for w, s_ in SITE:
        Q.append(dict(kind='site', well=w, screen=s_, label=f'{SCREENS[s_]} screen at the site of well {w}'))
    for w in BROM:
        Q.append(dict(kind='br', well=w, label=f'bromide of well {w}'))
    for w, yr in AGAIN:
        Q.append(dict(kind='again', well=w, years=yr, label=f'well {w} again, {yr:.0f} years after the heads settle'))
    return Q


def member_job(j):
    g = load(); E = g['E']; m = Model(j); Q = questions(); ra = resp_all(j)
    cv = np.zeros(m.nv); cv[m.iv] = 1.0
    prep = []
    for q in Q:
        if q['kind'] == 'new':
            c = np.zeros(m.nv); c[:NS] = ra[q['col'], q['screen'], :]; prep.append((c, []))
        elif q['kind'] == 'site':
            w = g['wid'][q['well']]
            prep.append((cv, [m.tie(w, ra[g['cols'][w][m.keep[w]], q['screen'], :])]))
        elif q['kind'] == 'again':                    # the same well again, 'years' after the heads settle
            w = g['wid'][q['well']]; cols = g['cols'][w][m.keep[w]]; scr = g['scr'][w]
            F = g['fade'][j]; n = g['after'].index(q['years'])
            ratio = np.where(F[0, cols, scr] > 1e-12, F[n, cols, scr] / np.maximum(F[0, cols, scr], 1e-12), 0.0)
            rows = m.G[w].copy(); rows[:, 6] *= np.clip(ratio, 0.0, None)
            prep.append((cv, [m.tie(w, rows)]))
        else:
            w = g['wid'][q['well']]
            prep.append((cv, [m.tie(w, m.G[w], into='B')]))
    out = dict(j=int(j), v={}, nan=0, npos=[int(n) for n in m.npos], tq=[0.0] * len(Q))
    t0 = time.time()
    for wn, src in VERDICTS:
        w, k = g['wid'][wn], SRC.index(src)
        ex = {'yes': m.cls(w, k, True), 'no': m.cls(w, k, False)}
        feas = {c: bool(m.solve(np.zeros(m.nv), [ex[c]]).status != 2) for c in ex}
        rr = []
        for iq, (c, extra) in enumerate(prep):
            d = {}; tq0 = time.time()
            for cl in ('yes', 'no'):
                if not feas[cl]:
                    continue
                r = m.rng(c, [ex[cl]] + extra)
                if r is None:
                    continue
                if not np.all(np.isfinite(r)):
                    out['nan'] += 1
                    r = [0.0 if not np.isfinite(r[0]) else r[0], m.vmax if not np.isfinite(r[1]) else r[1]]
                d[cl] = [float(r[0]), float(r[1])]
            rr.append(d); out['tq'][iq] += time.time() - tq0
        out['v'][f'{wn}:{src}'] = dict(feas=feas, rng=rr)
    out['sec'] = time.time() - t0
    return out


def share_job(args):
    """Largest (sense +1) or smallest (-1) share of source k at well w in one simulation, by bisection on the
    threshold of the verdict (exact feasibility programmes; the value returned is on the safe side)."""
    j, w, k, sense = args
    m = Model(j); z = np.zeros(m.nv)
    lo_, hi_ = 0.0, 1.0
    for _ in range(9):
        mid = 0.5 * (lo_ + hi_)
        ok = m.solve(z, [m.cls(w, k, sense > 0, tau=mid)]).status != 2      # share >= mid (or <= mid) possible?
        if sense > 0:
            lo_, hi_ = (mid, hi_) if ok else (lo_, mid)
        else:
            lo_, hi_ = (lo_, mid) if ok else (mid, hi_)
    return hi_ if sense > 0 else lo_


def shares(nw=4):
    g = load(); out = {}
    with Pool(nw) as pool:
        for wn, src, sense in (('340', 'MS', 1), ('340', 'RS', -1), ('340', 'RS', 1), ('340', 'DB', 1), ('503', 'MS', 1),
                               ('503', 'MS', -1), ('503', 'RS', -1)):
            v = pool.map(share_job, [(j, g['wid'][wn], I.SRC.index(src), sense) for j in g['mem']])
            out[f'{wn}:{src}:{"max" if sense > 0 else "min"}'] = float(max(v) if sense > 0 else min(v))
            print(wn, src, 'max' if sense > 0 else 'min', round(out[f'{wn}:{src}:{"max" if sense > 0 else "min"}'], 3), flush=True)
    json.dump(out, open(os.path.join(HERE, 'res', 'fk_inquiry_shares.json'), 'w'), indent=1)


def main(nw=4):
    g = load(); t0 = time.time()
    raw = []
    path = os.path.join(HERE, 'res', RAW)
    with Pool(nw) as pool:
        for r in pool.imap_unordered(member_job, g['mem']):
            raw.append(r)
            if len(raw) % 10 == 0 or len(raw) == len(g['mem']):
                json.dump(dict(questions=questions(), verdicts=VERDICTS, raw=raw), open(path, 'w'))
                print(len(raw), 'of', len(g['mem']), f'{time.time() - t0:.0f}s', 'nan', sum(x['nan'] for x in raw), flush=True)
    print('done', f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'shares':
        shares()
    else:
        main(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
