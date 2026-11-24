"""QENDRESA-GO Monte Carlo study (1000 data sets per row unless R is given on the command line).

Scenarios (K = 5 seasons; truth beta = 0.5, betal = 0.25 unless 'null'):
  correct    Gaussian copula rho = 0.35, the managers' rule of qendresa_model.PAST           n = 1000, 4000
  null       no effect of pumping (beta = betal = 0)                                          n = 4000, 16000
  weak       strong confounding and near-violations of positivity (qendresa_model.WEAK)       n = 4000
  tcop       Student-t copula with 4 degrees of freedom (the frugal Gaussian copula is wrong)   n = 4000
Every data set: the four estimators of the hazard MSM and (except under the null, where every rule has the same
risk) the risk and yield of the dynamic rules A_k = 1{L_k < tau} by the frugal simulator (with delta-method bands),
inverse probability weighting and the parametric g-formula, with the rule each method would choose under the risk
budget; the safe frugal choice uses the upper 95% bound of the risk. Writes qendresa_mc.json.
`python3 qendresa_exp.py [R] [scenario ...]` reruns some scenarios.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import json, sys, time, zlib
import numpy as np
from multiprocessing import Pool
import qendresa_model as M
import qendresa_est as E

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
TAUS = np.round(np.arange(-1.0, 2.01, 0.25), 2)
BUDGET = 0.45
SCEN = {
    'correct': dict(past=M.PAST, msm=M.MSM, copula='gauss', ns=[1000, 4000]),
    'null': dict(past=M.PAST, msm=M.NULL, copula='gauss', ns=[4000, 16000], rules=False),
    'weak': dict(past=M.WEAK, msm=M.MSM, copula='gauss', ns=[4000]),
    'tcop': dict(past=M.PAST, msm=M.MSM, copula='tcop', ns=[4000]),
}
METHODS = ['frugal', 'twostep', 'ipw', 'gform']
RULES = ['frugal', 'ipw', 'gform']
Z95 = 1.645                                                          # one-sided 95% upper bound of the risk
from scipy.stats import qmc
from scipy.special import ndtri
Zg = np.random.default_rng(2024).standard_normal((4000, M.K))       # fixed draws of the g-formula (MSM projection)
# Rules are integrated with scrambled Sobol points: 2^14 of them are accurate to about 5e-4 in the risk, while
# 20 000 pseudo-random draws reused in every data set gave a common error of about -0.0045.
_sob = lambda seed: ndtri(np.clip(qmc.Sobol(M.K, scramble=True, seed=seed).random(2 ** 14), 1e-12, 1 - 1e-12))
Wf = _sob(2025)                                                       # scores of the frugal simulator
Zr = _sob(2026)                                                       # draws of the g-formula for the rules


def one(args):
    name, n, rep = args
    sc = SCEN[name]
    rng = np.random.default_rng([zlib.crc32(name.encode()), n, rep])
    D = M.simulate(n, rng, past=sc['past'], msm=sc['msm'], copula=sc['copula'])
    P = E.prep(D)
    try:
        f = E.fit_frugal(P)
        th_f, se_f = E.frugal_theta(f)
        f2 = E.twostep(P)
        th_2, se_2 = E.frugal_theta(f2)
        th_i, se_i, _ = E.ipw(P)
        th_g, se_g, phi = E.gform(P, Zg)
        if sc.get('rules', True):
            fr, fse = E.frugal_rules_band(f['p'], f['cov'], f['free'], TAUS, Wf)
            rules = np.stack([fr, E.ipw_rules(P, TAUS), E.gform_rules(phi, TAUS, Zr)])
        else:
            rules = fse = None
    except Exception:
        return None
    est = np.array([[*th_f, *se_f], [*th_2, *se_2], [*th_i, *se_i], [*th_g, *se_g]])
    rho = float(np.tanh(f['p'][10]) / np.sqrt(M.K))
    return est, rules, rho, f['p'][:6], fse


def summarize(rows, truth, rtruth, oracle):
    ok = [r for r in rows if r is not None]
    est = np.array([r[0] for r in ok])                 # R x 4 methods x 8
    rules = np.array([r[1] for r in ok])               # R x 3 x taus x 2
    res = dict(n_ok=len(ok), rho_mean=float(np.mean([r[2] for r in ok])),
               past_mean=np.mean([r[3] for r in ok], 0).tolist())
    for j, m in enumerate(METHODS):
        e, s = est[:, j, :4], est[:, j, 4:]
        res[m] = dict(mean=e.mean(0).tolist(), bias=(e.mean(0) - truth).tolist(), sd=e.std(0).tolist(),
                      rmse=np.sqrt(((e - truth) ** 2).mean(0)).tolist(), mean_se=np.nanmean(s, 0).tolist(),
                      cover=np.nanmean(np.abs(e - truth) <= 1.96 * s, 0).tolist(),
                      reject=np.nanmean(np.abs(e) > 1.96 * s, 0).tolist())
    res['rules'] = {}
    if ok[0][1] is None:
        return res
    for j, m in enumerate(RULES):
        v = rules[:, j]                                # R x taus x 2
        pick = np.array([E.choose(vv, TAUS, BUDGET) for vv in v])
        res['rules'][m] = dict(
            risk_mean=v[:, :, 0].mean(0).tolist(), risk_sd=v[:, :, 0].std(0).tolist(),
            risk_rmse=np.sqrt(((v[:, :, 0] - rtruth[:, 0]) ** 2).mean(0)).tolist(),
            yield_mean=v[:, :, 1].mean(0).tolist(), yield_rmse=np.sqrt(((v[:, :, 1] - rtruth[:, 1]) ** 2).mean(0)).tolist(),
            pick_freq=np.bincount(pick, minlength=len(TAUS)).astype(float).__truediv__(len(pick)).tolist(),
            true_risk_of_pick=float(rtruth[pick, 0].mean()), violate=float((rtruth[pick, 0] > BUDGET + 0.01).mean()),
            yield_of_pick=float(rtruth[pick, 1].mean()), regret=float((rtruth[oracle, 1] - rtruth[pick, 1]).mean()))
    # the safe frugal rule: largest yield among the rules whose upper 95% bound of the risk is within the budget
    fse = np.array([r[4] for r in ok])                 # R x taus x 2
    ucb = rules[:, 0, :, 0] + Z95 * fse[:, :, 0]
    pick = np.array([E.choose(np.stack([u, v[:, 1]], 1), TAUS, BUDGET) for u, v in zip(ucb, rules[:, 0])])
    res['rules']['frugal_safe'] = dict(
        pick_freq=np.bincount(pick, minlength=len(TAUS)).astype(float).__truediv__(len(pick)).tolist(),
        true_risk_of_pick=float(rtruth[pick, 0].mean()), violate=float((rtruth[pick, 0] > BUDGET + 0.01).mean()),
        yield_of_pick=float(rtruth[pick, 1].mean()), regret=float((rtruth[oracle, 1] - rtruth[pick, 1]).mean()),
        risk_se_mean=fse[:, :, 0].mean(0).tolist(), ucb_cover=np.mean(rtruth[None, :, 0] <= ucb, 0).tolist(),
        band_cover=np.mean(np.abs(rules[:, 0, :, 0] - rtruth[None, :, 0]) <= 1.96 * fse[:, :, 0], 0).tolist())
    return res


def main(R=1000, only=None):
    t0 = time.time()
    path = 'qendresa_mc.json'
    out = json.load(open(path))['results'] if os.path.exists(path) else {}
    truths = {}
    with Pool(4) as pool:
        for name, sc in SCEN.items():
            if only and name not in only:
                continue
            truth = M.theta_vec(sc['msm'])
            rtruth = M.dynamic_truth(TAUS, past=sc['past'], msm=sc['msm'], copula=sc['copula'])
            oracle = E.choose(rtruth, TAUS, BUDGET)
            truths[name] = dict(rules=rtruth.tolist(), oracle=oracle)
            for n in sc['ns']:
                rows = pool.map(one, [(name, n, r) for r in range(R)], chunksize=5)
                s = summarize(rows, truth, rtruth, oracle)
                out[f'{name}_n{n}'] = dict(scenario=name, n=n, R=R, truth=truth.tolist(), rules_truth=rtruth.tolist(),
                                           oracle=oracle, **s)
                print(f'{name} n={n}: ok {s["n_ok"]}/{R}  ' + '  '.join(
                    f'{m}: b {s[m]["bias"][2]:+.3f} rmse {s[m]["rmse"][2]:.3f} cov {s[m]["cover"][2]:.2f} rej {s[m]["reject"][2]:.2f}'
                    for m in METHODS) + f'  [{time.time() - t0:.0f}s]', flush=True)
                json.dump(dict(taus=TAUS.tolist(), budget=BUDGET, results=out), open(path, 'w'), indent=1)
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    R = int(a[0]) if a and a[0].isdigit() else 1000
    main(R, [x for x in a if not x.isdigit()] or None)
