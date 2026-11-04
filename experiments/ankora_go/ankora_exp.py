"""ANKORA-GO: a few real anchors make a simulation-calibrated guarantee independent of the simulator.

The field and m "anchor" cases (aquifers or periods where the boundary functions were measured) are draws from the
real law Q; the simulator prior P may be wrong. Test bed: RINDERTIMI-GO / MATJA-GO / RESHJA-GO (32 cells x 64 weeks,
ensemble smoother with the exact solver, 128 members), four loggers (0.25, 1.25, 2.75, 4.25 km).
Field laws Q:
  none       Q = P
  delay      the vadose delay is 35 d in the field, 14 d in the simulator
  params     field recharge coefficient median 0.25 (simulator 0.35), recharge error and inland-inflow departures x1.5
  rainbias   the rain the reconstructor sees is a product (20% record bias, daily errors of log-sd 0.6), the simulator
             assumes it exact
Methods (90% bands, conformal risk control on the share of weeks outside):
  sims       lambda from n = 300 simulated aquifers (review I)
  anchors    lambda from the m anchors only (any Q)
  anchors+   the same, with the score reshaped by a week-by-week factor learned on the simulated aquifers
  mix(psi)   one weighted calibration of simulations and anchors; psi = w n / (w n + m + 1), the share of the weight on
             simulations. All calibrations are exact (no lambda grid): weighted quantiles of the pooled scores.
Every score is averaged over 300 random draws of m anchors; the realized risk is measured on the remaining field cases.

usage: python ankora_exp.py   (writes res/ankora.json and res/ankora_log.txt)"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'reshja_go'))
import reshja_exp as RX  # noqa: E402
from reshja_exp import X, G, M  # noqa: E402

RES = os.path.join(HERE, 'res')
ALPHA = 0.10
DESIGN = ('L0', 'L2', 'L4', 'L6')
GOALS = ('r', 'qL', 'eta', 'kappa')
N_SIM, N_Q = 300, 600
MS = (10, 20, 40)
PSIS = (0.0, 0.5, 0.8, 0.95, 1.0)
REPS = 300
LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.append(s)


class QBed(RX.RBed):
    def case_q(self, rng, scen):
        Pd = G.daily_rain(rng)
        tau_true = 35.0 if scen == 'delay' else M.TAU_V
        f = G.filtered(Pd, tau_true)
        if scen == 'rainbias':
            Po, b = RX.corrupt(Pd, rng, RX.SIG_B, RX.SIG_E)
        else:
            Po, b = Pd, 1.0
        fo = G.filtered(Po, M.TAU_V)
        z = self.mu + self.L @ rng.standard_normal(M.NZ)
        kmed = 0.25 if scen == 'params' else M.KAP_MED
        if scen == 'params':           # larger recharge error and inflow departures around the same means
            z[M.SL['e']] *= 1.5
            z[M.SL['dq']] = self.mu[M.SL['dq']] + 1.5 * (z[M.SL['dq']] - self.mu[M.SL['dq']])
        kap = np.exp(np.log(kmed) + M.KAP_LSD * rng.standard_normal())
        gk = M.kappa_response(f)
        tr = M.fields_from_z(z[:, None], np.array([kap]), f, self.G, self.cQ, gk)
        return dict(f=f, fo=fo, Po=Po, gko=M.kappa_response(fo), b=b, src='true', beff=1.0,
                    kappa=kap, h=tr['h'][0], eta=tr['eta'][0], qL=tr['qL'][0], r=tr['r'][0],
                    eh=M.SIG_H * rng.standard_normal((M.NX, M.NT)), ee=M.SIG_ETA * rng.standard_normal(M.NT),
                    seed=int(rng.integers(2 ** 31)))


def run(bed, pool):
    rows = bed.rows(DESIGN)
    out = []
    for cs in pool:
        y = bed.data(cs, rows)
        rec = bed.reconstruct_r(cs, rows, y, 0.0)
        t = dict(eta=cs['eta'], qL=cs['qL'], r=cs['r'], kappa=np.array([cs['kappa']]))
        out.append(dict(t=t, m={k: rec[k][0] for k in GOALS}, s={k: rec[k][1] for k in GOALS}))
    return out


def week_factor(sims, k):
    """score shape learned on the simulations: the median of |e|/s week by week (one number for a scalar goal)."""
    return np.median(np.array([np.abs(c['t'][k] - c['m'][k]) / c['s'][k] for c in sims]), axis=0)


def scores(cases, k, a=None):
    """standardised residuals |e| / (s a), one row per case (T columns)."""
    a = 1.0 if a is None else a
    return np.array([np.abs(c['t'][k] - c['m'][k]) / (c['s'][k] * a) for c in cases])


def crc_exact(Ss, Sa, w):
    """weighted conformal risk control without a grid (B = 1): the smallest lambda with
    (w sum_sims L(lambda) + sum_anchors L(lambda) + 1) / (w n + m + 1) <= alpha, L = share of points with score > lambda.
    Ss: (n, T) simulation scores, Sa: (m, T) anchor scores. Returns inf when no finite lambda exists."""
    n, m = len(Ss), len(Sa)
    T = (Ss if n else Sa).shape[1]
    den = (w * n if w > 0 else 0.0) + m + 1.0
    budget = ALPHA * den - 1.0                       # total weight allowed above lambda
    if budget < 0:
        return np.inf
    vals = [Sa.ravel()]; wts = [np.full(Sa.size, 1.0 / T)]
    if n and w > 0:
        vals.append(Ss.ravel()); wts.append(np.full(Ss.size, w / T))
    v = np.concatenate(vals); wt = np.concatenate(wts)
    o = np.argsort(-v)
    cum = np.cumsum(wt[o])
    j = np.searchsorted(cum, budget, side='right')  # first index whose cumulative weight exceeds the budget
    return float(v[o][j]) if j < len(v) else 0.0


def realized(St, lam):
    return float(np.mean(St > lam))


def main():
    t0 = time.time()
    os.makedirs(RES, exist_ok=True)
    bed = QBed()
    rng = np.random.default_rng(808)
    sims = run(bed, [bed.case(rng, 'true') for _ in range(N_SIM)])
    log(f'simulations ready [{time.time() - t0:.0f}s]')
    out = dict(alpha=ALPHA, design=DESIGN, n_sim=N_SIM, n_q=N_Q, ms=MS, psis=PSIS, reps=REPS, res={},
               min_anchors=dict(expectation=int(np.ceil((1 - ALPHA) / ALPHA)),
                                certificate=int(np.ceil(np.log(0.10) / np.log(1 - ALPHA)))))
    rs = np.random.default_rng(909)
    for scen in ('none', 'delay', 'params', 'rainbias'):
        field = run(bed, [bed.case_q(rng, scen) for _ in range(N_Q)])
        R = {}
        for k in GOALS:
            Ss, Sq = scores(sims, k), scores(field, k)
            a = week_factor(sims, k)
            Ssa, Sqa = scores(sims, k, a), scores(field, k, a)
            sq = np.array([np.mean(c['s'][k]) for c in field])
            sqa = np.array([np.mean(c['s'][k] * a) for c in field])
            lam_s = crc_exact(Ss, Ss[:0], 1.0)
            res = dict(sims=dict(risk=realized(Sq, lam_s), halfwidth=float(lam_s * sq.mean()), lam=lam_s))
            for m in MS:
                acc = {key: [] for key in ('anc_r', 'anc_w', 'ancp_r', 'ancp_w')}
                mix = {p: ([], []) for p in PSIS if p not in (0.0, 1.0)}
                for _ in range(REPS):
                    p = rs.permutation(N_Q); ai, ti = p[:m], p[m:]
                    lam = crc_exact(Ss[:0], Sq[ai], 0.0)
                    acc['anc_r'].append(realized(Sq[ti], lam)); acc['anc_w'].append(lam * sq[ti].mean())
                    lam = crc_exact(Ssa[:0], Sqa[ai], 0.0)
                    acc['ancp_r'].append(realized(Sqa[ti], lam)); acc['ancp_w'].append(lam * sqa[ti].mean())
                    for ps in mix:
                        w = ps / (1 - ps) * (m + 1) / N_SIM          # psi = w n / (w n + m + 1)
                        lam = crc_exact(Ss, Sq[ai], w)
                        mix[ps][0].append(realized(Sq[ti], lam)); mix[ps][1].append(lam * sq[ti].mean())
                res[f'm{m}'] = dict(
                    anchors=dict(risk=float(np.mean(acc['anc_r'])), risk_p90=float(np.percentile(acc['anc_r'], 90)),
                                 halfwidth=float(np.mean(acc['anc_w']))),
                    anchors_plus=dict(risk=float(np.mean(acc['ancp_r'])), risk_p90=float(np.percentile(acc['ancp_r'], 90)),
                                      halfwidth=float(np.mean(acc['ancp_w']))),
                    mix={str(ps): dict(risk=float(np.mean(v[0])), halfwidth=float(np.mean(v[1]))) for ps, v in mix.items()})
            R[k] = res
            log(f'{scen:8s} {k:5s} sims {res["sims"]["risk"]:.3f}/{res["sims"]["halfwidth"]:.3f} | ' +
                ' | '.join(f'm={m}: anc {res[f"m{m}"]["anchors"]["risk"]:.3f}/{res[f"m{m}"]["anchors"]["halfwidth"]:.3f} '
                           f'anc+ {res[f"m{m}"]["anchors_plus"]["halfwidth"]:.3f} mix ' +
                           ' '.join(f'{v["risk"]:.3f}/{v["halfwidth"]:.3f}' for v in res[f"m{m}"]["mix"].values())
                           for m in MS) + f'  [{time.time() - t0:.0f}s]')
        out['res'][scen] = R
    out['seconds'] = time.time() - t0
    with open(os.path.join(RES, 'ankora.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    with open(os.path.join(RES, 'ankora_log.txt'), 'w') as fh:
        fh.write('\n'.join(LOG) + '\n')
    log(f'done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
