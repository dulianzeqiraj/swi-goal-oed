"""MATJA-GO: the guaranteed value of a measurement. Which instrument (an automatic head logger at one of eight sites,
or a tide gauge) buys the most guaranteed reduction of the band of a boundary function or of the recharge coefficient,
when the only series known before is the rain?

Test bed: RINDERTIMI-GO / GARANCIA-GO (32 cells x 64 weeks, ensemble smoother with the exact solver, 128 members).
A new logger records the head every week (noise 2 cm); the tide gauge records the sea level every week (noise 1 cm).
Three design criteria, each run greedily for up to three instruments:
  ES      the mean 90% half-width of the raw ensemble, 1.645 * spread (what an ensemble-based design would use)
  oracle  the mean 90% half-width of the exact posterior, 1.645 * sd (available only because the test bed is linear)
  MATJA   the guaranteed half-width: the CRC multiplier calibrated on simulated aquifers times the mean spread
Selection uses pool A of simulated aquifers; every chosen design is then recalibrated and scored on a fresh pool B
(split into calibration and test halves), so the reported guarantees hold after the selection.

usage: python matja_exp.py   (writes res/matja.json and res/matja_log.txt)"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(1, os.path.join(HERE, '..', 'rindertimi_go'))
import gar_exp as G  # noqa: E402
import rgo_model as M  # noqa: E402

G.GRID = np.linspace(0.0, 150.0, 15001)   # lambda grid, step 0.01: dense data make the ensemble very overconfident for kappa

RES = os.path.join(HERE, 'res')
ALPHA = 0.10
NENS = 128
SITES_X = (250.0, 750.0, 1250.0, 2000.0, 2750.0, 3500.0, 4250.0, 4750.0)
SITES = tuple(int(x // M.DX) for x in SITES_X)
CANDS = tuple(f'L{j}' for j in range(len(SITES))) + ('TG',)
TG_ = ('eta', 'qL', 'r', 'h0', 'kappa')
LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.append(s)


class Bed:
    def __init__(self):
        self.G, self.cQ = M.response_matrix()
        self.mu, self.Sig = M.prior_z()
        self.L = np.linalg.cholesky(self.Sig + 1e-12 * np.eye(M.NZ))
        self.Rm = G.solver_matrices()
        nx, nt = M.NX, M.NT
        # linear maps from the latent z to the targets (the kappa part is added separately)
        A = {}
        I = np.eye(M.NZ)
        A['eta'] = I[M.SL['deta']] + I[M.SL['meta']][[0] * nt]
        A['qL'] = I[M.SL['dq']] + I[M.SL['mq']][[0] * nt]
        A['r'] = I[M.SL['e']]
        A['h0'] = self.G[np.arange(nx) * nt]
        self.A = A

    def case(self, rng):
        Pd = G.daily_rain(rng)
        f = G.filtered(Pd, M.TAU_V)
        z = self.mu + self.L @ rng.standard_normal(M.NZ)
        kap = np.exp(np.log(M.KAP_MED) + M.KAP_LSD * rng.standard_normal())
        gk = M.kappa_response(f)
        tr = M.fields_from_z(z[:, None], np.array([kap]), f, self.G, self.cQ, gk)
        return dict(f=f, gk=gk, kappa=kap, h=tr['h'][0], eta=tr['eta'][0], qL=tr['qL'][0], r=tr['r'][0],
                    eh=M.SIG_H * rng.standard_normal((M.NX, M.NT)), ee=M.SIG_ETA * rng.standard_normal(M.NT),
                    seed=int(rng.integers(2 ** 31)))

    @staticmethod
    def rows(design):
        rows, kinds = [], []
        for c in design:
            if c == 'TG':
                rows += [('eta', n) for n in range(M.NT)]
            else:
                i = SITES[int(c[1:])]
                rows += [('h', i * M.NT + n) for n in range(M.NT)]
        return rows

    def data(self, cs, rows):
        y = np.empty(len(rows))
        for k, (kind, idx) in enumerate(rows):
            if kind == 'eta':
                y[k] = cs['eta'][idx] + cs['ee'][idx]
            else:
                i, n = divmod(idx, M.NT)
                y[k] = cs['h'][i, n] + cs['eh'][i, n]
        return y

    def reconstruct(self, cs, rows, y):
        """ensemble smoother from the prior ensemble given the rain; the same prior ensemble for every design."""
        rng = np.random.default_rng(cs['seed'])
        f = cs['f']
        z = self.mu[:, None] + self.L @ rng.standard_normal((M.NZ, NENS))
        kap = M.KAP_MED * np.exp(M.KAP_LSD * rng.standard_normal(NENS))
        fl = M.fields_from_z(z, kap, f, self.G, self.cQ, cs['gk'])
        X = np.concatenate([fl['h'][:, :, 0], fl['eta'], fl['qL'], fl['r']], axis=1)
        nx, nt = M.NX, M.NT
        if rows:
            Hm = np.zeros((len(rows), X.shape[1])); c = np.zeros(len(rows)); R = np.zeros(len(rows))
            for k, (kind, idx) in enumerate(rows):
                if kind == 'eta':
                    Hm[k, nx + idx] = 1.0; R[k] = M.SIG_ETA ** 2
                else:
                    Hm[k] = np.concatenate([self.Rm['h0'][idx], self.Rm['eta'][idx], self.Rm['qL'][idx], self.Rm['r'][idx]])
                    c[k] = self.Rm['cQ'][idx]; R[k] = M.SIG_H ** 2
            Y = X @ Hm.T + c
            Xc, Yc = X - X.mean(0), Y - Y.mean(0)
            Cxy = Xc.T @ Yc / (NENS - 1); Cyy = Yc.T @ Yc / (NENS - 1)
            K = np.linalg.solve(Cyy + np.diag(R), Cxy.T).T
            Xa = X + (y[None] + np.sqrt(R)[None] * rng.standard_normal((NENS, len(y))) - Y) @ K.T
        else:
            Xa = X
        ens = dict(h0=Xa[:, :nx], eta=Xa[:, nx:nx + nt], qL=Xa[:, nx + nt:nx + 2 * nt], r=Xa[:, nx + 2 * nt:])
        ens['kappa'] = np.sum(ens['r'] * f, 1) / np.sum(f * f)
        return {k: (v.mean(0), v.std(0) + 1e-9) for k, v in ens.items()}

    def exact_sd(self, cs, rows, y):
        ex = M.exact_posterior(y, rows, cs['f'], self.G, self.cQ, self.mu, self.Sig)
        w, kg = ex['w'], ex['kgrid']
        vk = float(np.sum(w * kg ** 2) - np.sum(w * kg) ** 2)
        b = dict(eta=0.0, qL=0.0, r=cs['f'], h0=cs['gk'][np.arange(M.NX) * M.NT])
        out = {}
        for k, A in self.A.items():
            dv = np.sum((A @ ex['Spost']) * A, 1)
            slope = A @ ex['mz1'] + b[k]
            out[k] = np.sqrt(np.maximum(dv + vk * slope ** 2, 0.0))
        out['kappa'] = np.array([np.sqrt(vk)])
        return out


def targets(cs):
    return dict(eta=cs['eta'], qL=cs['qL'], r=cs['r'], h0=cs['h'][:, 0], kappa=np.array([cs['kappa']]))


def evaluate_design(bed, pool, design):
    rows = bed.rows(design)
    res = []
    for cs in pool:
        y = bed.data(cs, rows)
        rec = bed.reconstruct(cs, rows, y)
        sd = bed.exact_sd(cs, rows, y)
        res.append(dict(t=targets(cs), m={k: rec[k][0] for k in TG_}, s={k: rec[k][1] for k in TG_}, sd=sd))
    return res


def criteria(res):
    """design criteria on one pool: ES, oracle and the calibrated (MATJA) half-width, for every target."""
    out = {}
    for k in TG_:
        s_mean = np.mean([np.mean(c['s'][k]) for c in res])
        L = G.loss_matrix(res, k)
        lam = G.crc_lambda(L)
        q = G.cp_quantile(G.sup_scores(res, k))
        out[k] = dict(es=float(1.645 * s_mean), oracle=float(1.645 * np.mean([np.mean(c['sd'][k]) for c in res])),
                      matja=float(lam * s_mean), matja_sup=float(q * s_mean), lam=float(lam))
    return out


def fresh_score(res, k, rng, reps=300):
    """recalibrate on half of a fresh pool and score on the other half."""
    L = G.loss_matrix(res, k); S = G.sup_scores(res, k)
    smean = np.array([np.mean(c['s'][k]) for c in res])
    sdm = np.array([np.mean(c['sd'][k]) for c in res])
    raw = np.mean([np.mean(G.resid(c, k) > 1.645) for c in res])
    risk, cov, hw, hws = [], [], [], []
    n = len(res) // 2
    for _ in range(reps):
        p = rng.permutation(len(res)); ci, ti = p[:n], p[n:]
        lam = G.crc_lambda(L[ci]); q = G.cp_quantile(S[ci])
        risk.append(L[ti, int(round(lam / G.GRID[1]))].mean()); cov.append(np.mean(S[ti] <= q))
        hw.append(lam * smean[ti].mean()); hws.append(q * smean[ti].mean())
    return dict(crc_risk=float(np.mean(risk)), sup_cover=float(np.mean(cov)), halfwidth=float(np.mean(hw)),
                halfwidth_sup=float(np.mean(hws)), es_halfwidth=float(1.645 * smean.mean()),
                exact_halfwidth=float(1.645 * sdm.mean()), raw_miss=float(raw))


def main():
    os.makedirs(RES, exist_ok=True)
    t0 = time.time()
    bed = Bed()
    rng = np.random.default_rng(101)
    poolA = [bed.case(rng) for _ in range(150)]
    poolB = [bed.case(rng) for _ in range(300)]
    cache = {}

    def crit(design):
        key = tuple(sorted(design))
        if key not in cache:
            cache[key] = criteria(evaluate_design(bed, poolA, key))
        return cache[key]

    base = crit(())
    log(f'rain only: ' + ' | '.join(f'{k} ES {v["es"]:.3f} oracle {v["oracle"]:.3f} MATJA {v["matja"]:.3f}'
                                     for k, v in base.items()))
    paths = {}
    for goal in ('r', 'qL', 'kappa'):
        for cr in ('es', 'oracle', 'matja'):
            path = []
            steps = []
            for kstep in range(3):
                best, bval = None, np.inf
                for c in CANDS:
                    if c in path:
                        continue
                    v = crit(path + [c])[goal][cr]
                    if v < bval:
                        best, bval = c, v
                path.append(best)
                steps.append(dict(design=list(path), value=bval))
            paths[f'{goal}/{cr}'] = steps
            log(f'goal {goal:5s} criterion {cr:6s}: ' + ' -> '.join(f'{"+".join(s["design"])} ({s["value"]:.3f})'
                                                                for s in steps) + f'  [{len(cache)} designs, '
                                                                f'{time.time() - t0:.0f}s]')
    # the miscalibration of the ensemble, design by design: calibrated half-width / ensemble half-width
    ratio = {'+'.join(k) if k else 'rain only': {g: v[g]['matja'] / v[g]['es'] for g in ('r', 'qL', 'kappa')}
             for k, v in cache.items()}
    # fresh-pool scores of every design on the paths, of rain only and of the four original piezometer sites
    finals = {(), ('L0', 'L2', 'L4', 'L6')}
    for steps in paths.values():
        for s in steps:
            finals.add(tuple(sorted(s['design'])))
    rngB = np.random.default_rng(202)
    fresh = {}
    for d in sorted(finals, key=lambda d: (len(d), d)):
        res = evaluate_design(bed, poolB, d)
        fresh['+'.join(d) if d else 'rain only'] = {k: fresh_score(res, k, rngB) for k in TG_}
    for name, v in fresh.items():
        log(f'fresh {name:16s} ' + ' | '.join(f'{k} hw {v[k]["halfwidth"]:.3f} (ES {v[k]["es_halfwidth"]:.3f}, exact '
                                              f'{v[k]["exact_halfwidth"]:.3f}) risk {v[k]["crc_risk"]:.3f} cover '
                                              f'{v[k]["sup_cover"]:.2f}' for k in ('r', 'qL', 'kappa')))
    maxS = {name: {k: float(max(np.max(np.abs(G.resid(c, k))) for c in evaluate_design(bed, poolB[:50], d)))
                   for k in TG_} for name, d in (('L0+L2+L4+L6', ('L0', 'L2', 'L4', 'L6')),)}
    out = dict(alpha=ALPHA, max_score_check=maxS, grid_max=float(G.GRID[-1]), n_ens=NENS, sites_x=SITES_X, sites=SITES, cands=CANDS, poolA=len(poolA), poolB=len(poolB),
               base=base, paths=paths, ratio=ratio, fresh=fresh,
               criteria={'+'.join(k) if k else 'rain only': v for k, v in cache.items()}, seconds=time.time() - t0)
    with open(os.path.join(RES, 'matja.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    with open(os.path.join(RES, 'matja_log.txt'), 'w') as fh:
        fh.write('\n'.join(LOG) + '\n')
    log(f'done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
