"""CERTAIN-COAST Methodology, Section 4.2 (synthetic test): certified storyline statistics from a generative copy.

The safe window needs the probability that chloride at the wellfield exceeds its limit in each future year, over
storylines of sea-level rise and droughts. A generative copy of the coupled model (G-LED type: Gao, Kaltenbach and
Koumoutsakos, 2024) can run tens of thousands of storylines, but it carries no guarantee, and it is least reliable
where it matters: in the regime it was not trained on, near the onset of intrusion. Prediction-powered inference
(Angelopoulos, Bates, Fannjiang, Jordan and Zrnic, 2023) combines many copy runs with a few paired runs of the full
model, and gives a confidence bound that is valid whatever the copy's error; a poor copy only widens it.

Closing year of the chloride constraint under a fixed operating plan: the first year in which the exceedance
probability is above alpha. Because the true closing year is fixed, a one-sided bound that is valid in that single
year makes the certified year no later than the truth with probability 1 - delta; no correction over years is needed.

Compared, over repeated draws of the runs: the copy alone (N runs); the full model alone (n runs, Clopper-Pearson);
prediction-powered inference (N copy runs + n paired runs). The stand-in copy is the test system of method_active.py
with a weaker onset of intrusion and faster flushing, accurate in today's range and biased near the onset; the
guarantee does not depend on which generative model is used. All values are illustrative.

usage: python method_story.py [OUT_DIR]   (writes method_story.json)"""
import json
import os
import sys

import numpy as np
from scipy.stats import beta as betad, norm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import method_active as M  # noqa: E402

YEARS, WK = 50, 52
QW, QD = M.D, 2.0                           # operating plan inside today's window
ALPHA, DELTA = 0.05, 0.05
POOL, NCOPY, REPS = 40000, 10000, 2000
NFULL = int(os.environ.get("NFULL", 100))
DROUGHT_SD, DROUGHT_AR = 0.12, 0.5          # yearly head anomaly (m) of droughts and wet years, AR(1)
R_MEAN, R_SD = 0.010, 0.0025                # relative sea-level rise, m/yr


def copy_theta(onset_weaker, flushing_faster):
    """Stand-in copy: weaker onset of intrusion and faster flushing, same baseline chloride (0.4)."""
    th = M.TH_TRUE.copy()
    th[[4, 5]] *= 1 - onset_weaker
    lam = (1 - M.TH_TRUE[0]) * (1 + flushing_faster)
    th[0], th[1] = 1 - lam, 0.4 * lam
    return th


COPIES = {'poor': (0.30, 0.20), 'good': (0.10, 0.05)}


def storylines(n, rng):
    r = np.maximum(rng.normal(R_MEAN, R_SD, n), 0.0)
    d = np.zeros((n, YEARS)); d[:, 0] = rng.normal(0, DROUGHT_SD, n)
    for y in range(1, YEARS):
        d[:, y] = DROUGHT_AR * d[:, y - 1] + rng.normal(0, DROUGHT_SD * np.sqrt(1 - DROUGHT_AR ** 2), n)
    return r, d


def simulate(th, r, d, seed):
    """Yearly maximum chloride index for each storyline (vectorised over storylines)."""
    rng = np.random.default_rng(seed)
    n = len(r); h = np.full(n, M.hbar(0, QW, QD)); c = np.full(n, 0.4)
    ymax = np.zeros((n, YEARS))
    for t in range(YEARS * WK):
        y = t // WK
        hb = M.hbar(t, QW, QD) - r * (t / WK) + d[:, y]
        c = M.feats(c, h) @ th + rng.normal(0, M.SIG_C, n)
        h = M.RHO * h + (1 - M.RHO) * hb + rng.normal(0, M.SIG_H, n)
        ymax[:, y] = np.maximum(ymax[:, y], c)
    return ymax > 1.0


def first_above(p, a):
    k = np.where(p > a)[0]
    return int(k[0]) + 1 if len(k) else YEARS + 1


def evaluate(Yf, Yc):
    p_true, p_copy = Yf.mean(0), Yc.mean(0)
    t_true, t_copy_pool = first_above(p_true, ALPHA), first_above(p_copy, ALPHA)
    z = norm.ppf(1 - DELTA)
    out = {'copy_only': [], 'full_only': [], 'ppi': [], 'ppi_exact': []}
    widths = {'full_only': [], 'ppi': []}
    curves = {'full_only': [], 'ppi': [], 'ppi_exact': []}
    cover = {'ppi': np.zeros(YEARS), 'ppi_exact': np.zeros(YEARS)}
    rr = np.random.default_rng(99)
    for _ in range(REPS):
        idx = rr.permutation(POOL); lab, unl = idx[:NFULL], idx[NFULL:NFULL + NCOPY]
        pc = Yc[unl].mean(0)
        x = Yf[lab].sum(0)
        cp = np.where(x < NFULL, betad.ppf(1 - DELTA, x + 1, np.maximum(NFULL - x, 1e-9)), 1.0)
        rect = (Yc[lab].astype(float) - Yf[lab].astype(float))
        pp = pc - rect.mean(0)
        ub = pp + z * np.sqrt(Yc[unl].var(0) / NCOPY + rect.var(0, ddof=1) / NFULL)
        # exact variant: p <= P(copy exceeds) + P(full exceeds, copy does not), each by Clopper-Pearson at delta/2
        hits = Yc[unl].sum(0); miss = (Yf[lab] & ~Yc[lab]).sum(0)
        ex = (np.where(hits < NCOPY, betad.ppf(1 - DELTA / 2, hits + 1, np.maximum(NCOPY - hits, 1e-9)), 1.0)
              + np.where(miss < NFULL, betad.ppf(1 - DELTA / 2, miss + 1, np.maximum(NFULL - miss, 1e-9)), 1.0))
        out['ppi_exact'].append(first_above(ex, ALPHA)); curves['ppi_exact'].append(ex)
        cover['ppi'] += ub >= p_true; cover['ppi_exact'] += ex >= p_true
        out['copy_only'].append(first_above(pc, ALPHA))
        out['full_only'].append(first_above(cp, ALPHA))
        out['ppi'].append(first_above(ub, ALPHA))
        k = t_true - 1
        widths['full_only'].append(float(cp[k] - x[k] / NFULL)); widths['ppi'].append(float(ub[k] - pp[k]))
        curves['full_only'].append(cp); curves['ppi'].append(ub)
    res = {'p_true': p_true.tolist(), 'p_copy': p_copy.tolist(), 't_true': t_true, 't_copy_pool': t_copy_pool,
           'years': {k: v for k, v in out.items()},
           'corr_at_true_year': float(np.corrcoef(Yf[:, t_true - 1], Yc[:, t_true - 1])[0, 1]),
           'half_width_at_true_year': {k: float(np.median(v)) for k, v in widths.items()},
           'median_upper_bound': {k: np.median(np.array(v), 0).tolist() for k, v in curves.items()},
           'coverage_by_year': {k: (v / REPS).tolist() for k, v in cover.items()}}
    for k, v in out.items():
        v = np.array(v)
        res[k] = dict(median=float(np.median(v)), p5=float(np.percentile(v, 5)), p95=float(np.percentile(v, 95)),
                      later_than_true=float(np.mean(v > t_true)), years_early_median=float(np.median(t_true - v)))
        print(f'{k:10s} median year {np.median(v):5.1f} [{np.percentile(v, 5):.0f}, {np.percentile(v, 95):.0f}]  '
              f'later than truth {np.mean(v > t_true):.3f}  early by {np.median(t_true - v):.1f}')
    cy = res['coverage_by_year']
    print('coverage of the yearly bound: CLT min', round(min(cy['ppi']), 3), 'at true year', round(cy['ppi'][t_true - 1], 3),
          '| exact min', round(min(cy['ppi_exact']), 3))
    print('true closing year', t_true, '| copy (pool)', t_copy_pool, '| corr', round(res['corr_at_true_year'], 2),
          '| half-widths', res['half_width_at_true_year'])
    return res


def main(od):
    rng = np.random.default_rng(7)
    r, d = storylines(POOL, rng)
    Yf = simulate(M.TH_TRUE, r, d, 11)          # full model
    allres = {'params': dict(YEARS=YEARS, QW=QW, QD=QD, ALPHA=ALPHA, DELTA=DELTA, POOL=POOL, NCOPY=NCOPY, NFULL=NFULL,
                             REPS=REPS, DROUGHT_SD=DROUGHT_SD, DROUGHT_AR=DROUGHT_AR, R_MEAN=R_MEAN, R_SD=R_SD,
                             COPIES={k: list(v) for k, v in COPIES.items()}), 'copies': {}}
    for j, (name, (ow, ff)) in enumerate(COPIES.items()):
        Yc = simulate(copy_theta(ow, ff), r, d, 12 + j)     # copy, same storylines, its own noise
        print(f'--- copy {name}: onset {100 * ow:.0f}% weaker, flushing {100 * ff:.0f}% faster')
        allres['copies'][name] = evaluate(Yf, Yc)
    with open(os.path.join(od, os.environ.get('OUT_NAME', 'method_story.json')), 'w') as fh:
        json.dump(allres, fh)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)))
