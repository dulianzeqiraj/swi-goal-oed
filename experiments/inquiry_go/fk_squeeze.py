"""SQUEEZE-GO as a seventh term of the Fushe-Kuqe section: chloride expelled from the compacting cover.

usage: python fk_squeeze.py resp [workers]     -> res/fk_squeeze_resp.npz   (new solves of the head-consistent members)
       python fk_squeeze.py infer [workers]    -> res/fk_squeeze.json       (field results: not for the public repository)

When the head of the confined aquifer falls by dh(x), a cover of thickness b'(x) and skeletal specific storage S'sk
compacts by S'sk b' dh and expels that much pore water; if the water holds c_clay of chloride and the decline took
the time T, the mean solute flux into the top of the aquifer is  (c_clay S'sk / T) b'(x) dh(x).  The term is
therefore a solute source through the top with the known pattern b'(x) dh(x) and ONE unknown strength
S_SQ = c_clay S'sk / T, which the physics caps.  dh is the difference between the head without pumping and the head
with pumping in the same simulation.  The response per unit strength is computed with the transport operator of the
steady state, like the other tagged terms; the release is treated as steady at its mean rate (a first test: the
real release is a pulse that follows the decline)."""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import scipy.sparse.linalg as spla
from scipy.optimize import LinearConstraint, Bounds

HERE = os.path.dirname(os.path.abspath(__file__))
HIP = os.path.join(HERE, '..', 'hipoteza_go')
sys.path.insert(0, HIP)
import fk_core as FC  # noqa: E402
import fk_infer as I  # noqa: E402

CALIB = os.path.join(HERE, '..', '..', 'chloride_fk', 'results', 'calib_ensemble.npz')
SRC7 = I.SRC + ['SQ']
# assumed ranges for the cap (to be replaced by measurements): pore-water chloride up to that of the sea, skeletal
# specific storage of soft clay up to 1e-2 per metre, a decline that took at least 20 years
C_CLAY, SSK, T_YR = (1000.0, 21000.0), (1e-4, 1e-2), (20.0, 60.0)
S_CAP = C_CLAY[1] * SSK[1] / (T_YR[0] * 365.25)        # generous cap of the strength [g/m4/d]
S_MID = 10000.0 * 1e-3 / (40.0 * 365.25)               # a central value
U_MAX = 200.0                                          # 'uncapped': strengths up to U_MAX caps
TAU = 0.5
_G = {}


def base():
    if not _G:
        z = np.load(os.path.join(HIP, 'res_fk', 'ensemble_fk.npz'))
        ok = z['ok'] & np.isfinite(z['h_lit'])
        E = {k: (z[k][ok] if z[k].shape[:1] == ok.shape else z[k]) for k in z.files}
        R = json.load(open(os.path.join(HIP, 'res_fk', 'fk_results_second.json')))
        kh = np.array(R['kappa_head'])
        _G.update(E=E, R=R, heads=[int(j) for j in np.flatnonzero(kh <= R['union']['kappa_eff'])],
                  cols=[np.array(b) for b in R['bands']], scr=R['screens'], kap=R['union']['kappa_eff'])
        _G['y'], _G['eps'] = I.data()
    return _G


def resp_job(j):
    g = base(); E = g['E']
    calib = _G.setdefault('calib', dict(np.load(CALIB)))
    th = {k: (int(E['th_' + k][j]) if k == 'member' else float(E['th_' + k][j])) for k in FC.THETA_FK}
    M = FC.member(th, calib); s = M['sec']
    A, *_ = s.tmatrix(s.qx, s.qz, s.qsea)
    h0, *_ = s.flow(s.c, Qw=0.0)
    dh = np.clip(s.head_top(h0) - s.head_top(), 0.0, None)
    cover = np.clip(s.geo['top'] + M['ground'], 0.0, None)
    b = np.zeros(s.N); cols = np.arange(s.nx)
    b[s.idx[s.jtop[cols], cols]] = s.dx * cover * dh
    f = spla.splu(A).solve(b)
    out = np.zeros((s.nx, 3), np.float32)
    for q, kind in enumerate(('sh', 'mid', 'dp')):
        out[:, q] = [f[c].mean() if len(c) else 0.0 for c in s.screen_cells(kind)]
    return j, out, dh.astype(np.float32), cover.astype(np.float32), float(np.nanmax(np.abs(M['resp'] - E['resp'][j])))


def resp(nw=4):
    g = base(); t0 = time.time()
    with Pool(nw) as pool:
        res = pool.map(resp_job, g['heads'])
    np.savez_compressed(os.path.join(HERE, 'res', 'fk_squeeze_resp.npz'), members=np.array([r[0] for r in res]),
                        G_SQ=np.array([r[1] for r in res]), dh=np.array([r[2] for r in res]),
                        cover=np.array([r[3] for r in res]))
    print('done', f'{time.time() - t0:.0f}s', len(res), 'members; largest difference from the stored responses', max(r[4] for r in res))


class Model:
    """Mixed-integer set of one simulation with the seven strengths (the squeeze strength in units of the cap)."""

    def __init__(self, j, gsq, lib, u_max):
        g = base(); E = g['E']
        y, eps, kap = g['y'], g['eps'], g['kap']
        lo = np.zeros(7); hi = np.zeros(7)
        for k in lib:
            lo[k], hi[k] = (I.S_INT[k] if k < 6 else (0.0, u_max))
        self.lo, self.hi = lo, hi
        self.G = []
        for c, q, yi, ei in zip(g['cols'], g['scr'], y, eps):
            G6 = np.asarray(E['resp'][j][c, q, :], float)
            G7 = np.c_[np.where(np.isfinite(G6), G6, 0.0), gsq[c, q] * S_CAP]
            G7 = np.where(np.abs(G7) < 1e-12, 0.0, G7)
            a, b = G7 @ lo, G7 @ hi
            self.G.append(G7[(a <= yi + kap * ei) & (b >= yi - kap * ei)])
        self.empty = any(len(a) == 0 for a in self.G)
        self.npos = [len(a) for a in self.G]
        self.off = np.r_[7, 7 + np.cumsum(self.npos)].astype(int)
        self.nv = int(self.off[-1])
        if self.empty:
            return
        A, ub = [], []
        for i, (Gi, yi, ei) in enumerate(zip(self.G, y, eps)):
            a, b = Gi @ lo, Gi @ hi
            for p in range(len(Gi)):
                M = (b[p] - yi - kap * ei) / ei
                if M > 0:
                    r = np.zeros(self.nv); r[:7] = Gi[p] / ei; r[self.off[i] + p] = M; A.append(r); ub.append(yi / ei + kap + M)
                M = (yi - kap * ei - a[p]) / ei
                if M > 0:
                    r = np.zeros(self.nv); r[:7] = -Gi[p] / ei; r[self.off[i] + p] = M; A.append(r); ub.append(-yi / ei + kap + M)
        self.A = np.array(A) if A else np.zeros((0, self.nv)); self.ub = np.array(ub)
        self.Aeq = np.zeros((len(self.G), self.nv))
        for i in range(len(self.G)):
            self.Aeq[i, self.off[i]:self.off[i + 1]] = 1.0
        self.integ = np.r_[np.zeros(7), np.ones(self.nv - 7)]
        self.lob = np.r_[lo, np.zeros(self.nv - 7)]; self.hib = np.r_[hi, np.ones(self.nv - 7)]

    def cls(self, w, k, yes, tau=TAU):
        A, ub = [], []
        e = base()['eps'][w]
        for p in range(self.npos[w]):
            f = -tau * self.G[w][p]; f[k] += self.G[w][p][k]
            fmin = float(np.sum(np.minimum(f * self.lo, f * self.hi))); fmax = float(np.sum(np.maximum(f * self.lo, f * self.hi)))
            M = (-fmin if yes else fmax) / e
            if M <= 0:
                continue
            r = np.zeros(self.nv); r[:7] = (-f if yes else f) / e; r[self.off[w] + p] = M; A.append(r); ub.append(M)
        return (np.array(A), np.array(ub)) if A else (np.zeros((0, self.nv)), np.zeros(0))

    def solve(self, c, extra=()):
        A, ub = self.A, self.ub
        for a_, u_ in extra:
            if len(u_):
                A = np.vstack([A, a_]); ub = np.r_[ub, u_]
        cons = [LinearConstraint(self.Aeq, 1.0, 1.0)] + ([LinearConstraint(A, -np.inf, ub)] if len(ub) else [])
        return I.milp(c, constraints=cons, integrality=self.integ, bounds=Bounds(self.lob, self.hib), options=dict(time_limit=10.0))

    def feasible(self, extra=()):
        return (not self.empty) and self.solve(np.zeros(self.nv), extra).status != 2

    def min_u(self, extra=()):
        """Smallest squeeze strength (in caps), None if the set is empty."""
        if self.empty:
            return None
        c = np.zeros(self.nv); c[6] = 1.0
        r = self.solve(c, extra)
        return None if r.status == 2 or r.x is None else float(r.x[6])

    def max_share(self, w, k):
        if not self.feasible():
            return None
        lo_, hi_ = 0.0, 1.0
        for _ in range(9):
            mid = 0.5 * (lo_ + hi_)
            lo_, hi_ = (mid, hi_) if self.feasible([self.cls(w, k, True, tau=mid)]) else (lo_, mid)
        return hi_


def infer_job(args):
    n, j, gsq = args
    FULL7 = list(range(7)); SPARSE = [0, 2, 6]
    out = dict(j=j)
    m = Model(j, gsq, FULL7, U_MAX)
    out['feas7'] = m.feasible()
    out['feas6'] = Model(j, gsq, list(range(6)), U_MAX).feasible()
    ms = Model(j, gsq, SPARSE, U_MAX)
    out['sparse_min_u'] = ms.min_u()                                   # sea + fresh + squeeze: strength needed
    out['sparse_other'] = {name: Model(j, gsq, lib, U_MAX).feasible() for name, lib in (('RS', [0, 2, 4]), ('DB', [0, 2, 5]))}
    if out['feas7']:
        for w, wn in ((2, '340'), (0, '503')):
            out['need_' + wn] = m.min_u([m.cls(w, 6, True)])           # strength needed for half of the well
            out['max_uncapped_' + wn] = m.max_share(w, 6)
        for tag, um in (('cap', 1.0), ('mid', S_MID / S_CAP)):
            mc = Model(j, gsq, FULL7, um)
            out['feas_' + tag] = mc.feasible()
            for w, wn in ((2, '340'), (0, '503')):
                out[f'max_{tag}_{wn}'] = mc.max_share(w, 6) if out['feas_' + tag] else None
        out['sea_340'] = m.max_share(2, 0)
    return out


def infer(nw=4):
    g = base(); t0 = time.time()
    z = np.load(os.path.join(HERE, 'res', 'fk_squeeze_resp.npz'))
    jobs = [(n, int(j), z['G_SQ'][n]) for n, j in enumerate(z['members'])]
    with Pool(nw) as pool:
        res = pool.map(infer_job, jobs)
    dh = z['dh']; cov = z['cover']
    out = dict(n_heads=len(jobs), S_CAP=S_CAP, S_MID=S_MID, U_MAX=U_MAX, ranges=dict(c_clay=C_CLAY, ssk=SSK, t_yr=T_YR),
               decline_max=[float(np.percentile(dh.max(axis=1), q)) for q in (5, 50, 95)],
               cover=[float(np.percentile(cov, q)) for q in (5, 50, 95)], runs=res, seconds=time.time() - t0)
    json.dump(out, open(os.path.join(HERE, 'res', 'fk_squeeze.json'), 'w'), indent=1)
    print('done', f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    nw = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    (resp if sys.argv[1] == 'resp' else infer)(nw)
