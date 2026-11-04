"""RESHJA-GO: guarantees when the rain itself is uncertain.

The reconstructor knows the rain only through a product (a satellite or reanalysis series, or a distant station):
  P_obs(d) = P_true(d) / b * eps(d),   b ~ LogNormal(0, SIG_B) a bias for the whole record,
                                       eps(d) ~ LogNormal(-SIG_E^2/2, SIG_E) independent daily errors (wet days).
A local rain gauge is the same with a small bias and small daily errors.
Test bed: RINDERTIMI-GO / MATJA-GO (32 cells x 64 weeks, ensemble smoother with the exact solver, 128 members).

Settings (calibration pool -> test pool, both simulated aquifers of the physical prior given the rain):
  exact    the reconstructor sees the true rain (review I)
  naive    calibrated on aquifers with exact rain, used on aquifers whose rain comes from the product
  aware    calibrated and used with the product; the reconstructor's members carry the bias in their prior
  aware+R2 as aware, and the members also carry the filtered daily error of the product, drawn from the covariance
           of Proposition R2 computed from the product itself: (v/(1+v)) K diag(P_obs^2) K^T
  gauge    calibrated and used with a local gauge (aware of its small errors)
Designs: rain only, 1 logger (2.0 km), 2 loggers (2.0 and 4.75 km), 4 loggers (0.25, 1.25, 2.75, 4.25 km), all 8.
Scores: averages over 300 random draws of 200 calibration and 200 test aquifers from pools of 400 (the expected risk
and coverage that the guarantees bound).
Targets: weekly recharge r, inflow q_L, sea level eta, kappa, and the effective coefficient kappa_eff = kappa * b_eff
(b_eff = sum f_true f_obs / sum f_obs^2, what the heads can see).
Also the filter law of Proposition R2: the relative variance of the filtered product error against
SIG_E^2-type prediction sum_u K_w(t,u)^2 P(u)^2 / (sum_u K_w(t,u) P(u))^2.

usage: python reshja_exp.py   (writes res/reshja.json and res/reshja_log.txt)"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'matja_go'))
import matja_exp as X  # noqa: E402
from matja_exp import G, M  # noqa: E402

RES = os.path.join(HERE, 'res')
SIG_B, SIG_E = 0.20, 0.60            # product: record bias (log-sd) and daily error (log-sd)
GB, GE = 0.05, 0.10                  # local gauge
N_CAL, N_TEST = 200, 200
DESIGNS = {'rain only': (), '1 logger': ('L3',), '2 loggers': ('L3', 'L7'), '4 loggers': ('L0', 'L2', 'L4', 'L6'),
           '8 loggers': tuple(f'L{j}' for j in range(8))}
GOALS = ('r', 'qL', 'eta', 'kappa', 'kappa_eff')
LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.append(s)


def corrupt(Pd, rng, sb, se):
    b = float(np.exp(sb * rng.standard_normal()))
    eps = np.exp(se * rng.standard_normal(Pd.size) - se ** 2 / 2)
    return Pd / b * eps, b


class RBed(X.Bed):
    def __init__(self):
        super().__init__()
        nd = M.SPIN + M.NT * 7
        self.K = np.empty((M.NT, nd))
        for u in range(nd):
            e = np.zeros(nd); e[u] = 1.0
            self.K[:, u] = G.filtered(e, M.TAU_V)

    def case(self, rng, source='true'):
        Pd = G.daily_rain(rng)
        f = G.filtered(Pd, M.TAU_V)
        if source == 'true':
            Po, b = Pd, 1.0
        elif source == 'product':
            Po, b = corrupt(Pd, rng, SIG_B, SIG_E)
        else:
            Po, b = corrupt(Pd, rng, GB, GE)
        fo = G.filtered(Po, M.TAU_V)
        z = self.mu + self.L @ rng.standard_normal(M.NZ)
        kap = np.exp(np.log(M.KAP_MED) + M.KAP_LSD * rng.standard_normal())
        gk = M.kappa_response(f)
        tr = M.fields_from_z(z[:, None], np.array([kap]), f, self.G, self.cQ, gk)
        return dict(f=f, fo=fo, Po=Po, gko=M.kappa_response(fo), b=b, src=source, beff=float(np.sum(f * fo) / np.sum(fo * fo)),
                    kappa=kap, h=tr['h'][0], eta=tr['eta'][0], qL=tr['qL'][0], r=tr['r'][0],
                    eh=M.SIG_H * rng.standard_normal((M.NX, M.NT)), ee=M.SIG_ETA * rng.standard_normal(M.NT),
                    seed=int(rng.integers(2 ** 31)))

    def reconstruct_r(self, cs, rows, y, sig_b, r2=False):
        """ensemble smoother driven by the observed rain fo. Members draw c = kappa*b (log-sd sqrt(KAP_LSD^2+sig_b^2));
        after the update, kappa_eff = c is read from the recharge and kappa from the conditional of log kappa given
        log c."""
        rng = np.random.default_rng(cs['seed'])
        fo = cs['fo']
        z = self.mu[:, None] + self.L @ rng.standard_normal((M.NZ, X.NENS))
        sc = np.sqrt(M.KAP_LSD ** 2 + sig_b ** 2)
        c = M.KAP_MED * np.exp(sc * rng.standard_normal(X.NENS))
        if r2:                   # Proposition R2: the filtered daily error of the rain, from the rain record itself
            se = SIG_E if cs['src'] == 'product' else GE
            v = np.exp(se ** 2) - 1.0
            Sd = v / (1.0 + v) * (self.K * cs['Po'] ** 2) @ self.K.T
            Ld = np.linalg.cholesky(Sd + 1e-10 * np.eye(M.NT))
            z[M.SL['e']] -= c[None, :] * (Ld @ rng.standard_normal((M.NT, X.NENS)))
        fl = M.fields_from_z(z, c, fo, self.G, self.cQ, cs['gko'])
        Xs = np.concatenate([fl['h'][:, :, 0], fl['eta'], fl['qL'], fl['r']], axis=1)
        nx, nt = M.NX, M.NT
        if rows:
            Hm = np.zeros((len(rows), Xs.shape[1])); cc = np.zeros(len(rows)); R = np.zeros(len(rows))
            for k, (kind, idx) in enumerate(rows):
                if kind == 'eta':
                    Hm[k, nx + idx] = 1.0; R[k] = M.SIG_ETA ** 2
                else:
                    Hm[k] = np.concatenate([self.Rm['h0'][idx], self.Rm['eta'][idx], self.Rm['qL'][idx],
                                            self.Rm['r'][idx]])
                    cc[k] = self.Rm['cQ'][idx]; R[k] = M.SIG_H ** 2
            Y = Xs @ Hm.T + cc
            Xc, Yc = Xs - Xs.mean(0), Y - Y.mean(0)
            Cxy = Xc.T @ Yc / (X.NENS - 1); Cyy = Yc.T @ Yc / (X.NENS - 1)
            K = np.linalg.solve(Cyy + np.diag(R), Cxy.T).T
            Xa = Xs + (y[None] + np.sqrt(R)[None] * rng.standard_normal((X.NENS, len(y))) - Y) @ K.T
        else:
            Xa = Xs
        ens = dict(eta=Xa[:, nx:nx + nt], qL=Xa[:, nx + nt:nx + 2 * nt], r=Xa[:, nx + 2 * nt:])
        ce = np.sum(ens['r'] * fo, 1) / np.sum(fo * fo)
        ens['kappa_eff'] = ce
        if sig_b > 0:            # log kappa | log c: Gaussian, prior medians KAP_MED and 1
            w = M.KAP_LSD ** 2 / (M.KAP_LSD ** 2 + sig_b ** 2)
            lc = np.log(np.maximum(ce, 1e-6))
            mu = np.log(M.KAP_MED) + w * (lc - np.log(M.KAP_MED))
            sd = np.sqrt(M.KAP_LSD ** 2 * sig_b ** 2 / (M.KAP_LSD ** 2 + sig_b ** 2))
            ens['kappa'] = np.exp(mu + sd * rng.standard_normal(X.NENS))
        else:
            ens['kappa'] = ce
        return {k: (v.mean(0), v.std(0) + 1e-9) for k, v in ens.items()}


def targets(cs):
    return dict(eta=cs['eta'], qL=cs['qL'], r=cs['r'], kappa=np.array([cs['kappa']]),
                kappa_eff=np.array([cs['kappa'] * cs['beff']]))


def run(bed, pool, design, sig_b, r2=False):
    rows = bed.rows(design)
    out = []
    for cs in pool:
        y = bed.data(cs, rows)
        rec = bed.reconstruct_r(cs, rows, y, sig_b, r2)
        out.append(dict(t=targets(cs), m={k: rec[k][0] for k in GOALS}, s={k: rec[k][1] for k in GOALS}))
    return out


def score(calpop, testpop, same, k, rng, reps=300, n=200):
    """expected risk, coverage and guaranteed half-width over random calibration/test draws. same: both from one
    population (disjoint halves); otherwise independent draws of n from each."""
    Lc, Sc = G.loss_matrix(calpop, k), G.sup_scores(calpop, k)
    Lt, St = (Lc, Sc) if same else (G.loss_matrix(testpop, k), G.sup_scores(testpop, k))
    sb_t = np.array([np.mean(c['s'][k]) for c in testpop])
    risk, cov, hw, lams = [], [], [], []
    for _ in range(reps):
        if same:
            p = rng.permutation(len(calpop)); ci, ti = p[:n], p[n:2 * n]
        else:
            ci, ti = rng.permutation(len(calpop))[:n], rng.permutation(len(testpop))[:n]
        lam = G.crc_lambda(Lc[ci]); q = G.cp_quantile(Sc[ci])
        risk.append(Lt[ti, int(round(lam / G.GRID[1]))].mean()); cov.append(np.mean(St[ti] <= q))
        hw.append(lam * sb_t[ti].mean()); lams.append(lam)
    raw = float(np.mean([np.mean(G.resid(c, k) > 1.645) for c in testpop]))
    return dict(lam=float(np.mean(lams)), crc_risk=float(np.mean(risk)), sup_cover=float(np.mean(cov)),
                halfwidth=float(np.mean(hw)), es_halfwidth=float(1.645 * sb_t.mean()), raw_miss=raw)


def filter_law(rng, n_rec=300, n_noise=200):
    """Proposition R2: the weekly filtered product error, measured against the exact conditional variance."""
    nd = M.SPIN + M.NT * 7
    K = np.empty((M.NT, nd))
    for u in range(nd):
        e = np.zeros(nd); e[u] = 1.0
        K[:, u] = G.filtered(e, M.TAU_V)
    meas, pred, ratio = [], [], []
    for _ in range(n_rec):
        Pd = G.daily_rain(rng)
        f = K @ Pd
        v = np.exp(SIG_E ** 2) - 1.0
        pv = v * (K ** 2 @ (Pd ** 2)) / f ** 2               # predicted relative variance, week by week
        sims = np.array([K @ (Pd * np.exp(SIG_E * rng.standard_normal(nd) - SIG_E ** 2 / 2)) for _ in range(n_noise)])
        mv = sims.var(0) / f ** 2
        meas.append(float(np.mean(mv))); pred.append(float(np.mean(pv)))
        ratio.append(float(np.mean((K ** 2 @ (Pd ** 2)) / f ** 2)))
    k1 = G.filtered(np.r_[np.zeros(M.SPIN), 1.0, np.zeros(M.NT * 7 - 1)], M.TAU_V)
    return dict(daily_rel_var=float(np.exp(SIG_E ** 2) - 1), measured=meas, predicted=pred, kernel_ratio=ratio,
                check_linear=float(np.max(np.abs(K @ G.daily_rain(np.random.default_rng(9)) -
                                                 G.filtered(G.daily_rain(np.random.default_rng(9)), M.TAU_V)))),
                four_tau=4 * M.TAU_V)


def main():
    t0 = time.time()
    os.makedirs(RES, exist_ok=True)
    bed = RBed()
    rng = np.random.default_rng(505)
    pools = {src: [bed.case(rng, src) for _ in range(N_CAL + N_TEST)] for src in ('true', 'product', 'gauge')}
    settings = dict(exact=('true', 'true', 0.0, 0.0, False), naive=('true', 'product', 0.0, 0.0, False),
                    aware=('product', 'product', SIG_B, SIG_B, False), aware_r2=('product', 'product', SIG_B, SIG_B, True),
                    gauge=('gauge', 'gauge', GB, GB, False))
    rs = np.random.default_rng(707)
    out = dict(sig_b=SIG_B, sig_e=SIG_E, gauge=(GB, GE), n_cal=N_CAL, n_test=N_TEST, designs=DESIGNS, res={})
    cache = {}
    for name, (scal, stest, sbc, sbt, r2) in settings.items():
        out['res'][name] = {}
        for dn, d in DESIGNS.items():
            for key in ((scal, dn, sbc, r2), (stest, dn, sbt, r2)):
                if key not in cache:
                    cache[key] = run(bed, pools[key[0]], DESIGNS[key[1]], key[2], key[3])
            cal, test = cache[(scal, dn, sbc, r2)], cache[(stest, dn, sbt, r2)]
            out['res'][name][dn] = {k: score(cal, test, scal == stest, k, rs) for k in GOALS}
            v = out['res'][name][dn]
            log(f'{name:6s} {dn:9s} ' + ' | '.join(f'{k} hw {v[k]["halfwidth"]:.3f} risk {v[k]["crc_risk"]:.3f} cov '
                                                  f'{v[k]["sup_cover"]:.2f}' for k in GOALS) + f'  [{time.time() - t0:.0f}s]')
    bs = [c['b'] for c in pools['product']]
    out['b_spread'] = dict(sd_log=float(np.std(np.log(bs))))
    # the floor of Proposition R1 for the 90% half-width of kappa (log scale -> kappa scale at the median)
    sd_floor = np.sqrt(M.KAP_LSD ** 2 * SIG_B ** 2 / (M.KAP_LSD ** 2 + SIG_B ** 2))
    out['floor'] = dict(sd_log=float(sd_floor), halfwidth=float(M.KAP_MED * np.sinh(1.645 * sd_floor)))
    out['filter'] = filter_law(np.random.default_rng(606))
    out['seconds'] = time.time() - t0
    with open(os.path.join(RES, 'reshja.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    with open(os.path.join(RES, 'reshja_log.txt'), 'w') as fh:
        fh.write('\n'.join(LOG) + '\n')
    f_ = out['filter']
    log(f'filter law: daily rel var {f_["daily_rel_var"]:.3f}; measured {np.mean(f_["measured"]):.4f}, predicted '
        f'{np.mean(f_["predicted"]):.4f}; kernel ratio {np.mean(f_["kernel_ratio"]):.4f} (1/(4 tau) = '
        f'{1 / f_["four_tau"]:.4f}); linear check {f_["check_linear"]:.2e}; floor hw {out["floor"]["halfwidth"]:.3f}')
    log(f'done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
