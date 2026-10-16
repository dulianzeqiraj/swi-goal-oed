"""KUFI-GO: safe choice of a pumping threshold from observational well-field records.

Regime family d_x: pump high until a toe reading exceeds x, then low for good (x on a grid). The manager
wants the highest threshold (most high-rate pumping) whose risk of salinization within H years stays
below alpha. Each psi(x) = E[Y^{d_x}] is estimated with TMLE at the review times (tmle_go.py); the joint
influence curves of the K estimates give a one-sided simultaneous upper band. Selection rules:
  naive   largest x with the naive estimate <= alpha
  plugin  largest x with the TMLE estimate <= alpha
  point   largest x with the pointwise one-sided 95% upper bound <= alpha
  band    largest x with the simultaneous one-sided 95% upper band <= alpha
  band_first  the threshold just below the first x whose simultaneous upper band exceeds alpha
  msm     largest x whose simultaneous upper band from a working marginal structural model
          logit psi(x) = b0 + b1 x, fitted to the K TMLE estimates, is <= alpha
If no threshold qualifies, the rule falls back to always-low pumping. Truth from 400 000 simulated wells
per regime. Writes kufi_results.json."""
import json, time, warnings
import numpy as np
from multiprocessing import Pool
import tmle_go as T
warnings.filterwarnings('ignore')
XS = [round(x, 2) for x in np.arange(0.62, 0.801, 0.02)]
REGS = [f'dyn@{x:.2f}' for x in XS]
ALPHAS = [0.35, 0.38]
NS = [1000, 2000, 4000]
DESIGNS = ['op+D', 'op']
R = 300
NTRUTH = 400000
RULES = ['naive', 'plugin', 'point', 'band', 'band_first', 'msm']


def select(alpha, **curves):
    """largest threshold whose curve value is <= alpha; 'first' variants stop at the first crossing."""
    out = {}
    for rule, v in curves.items():
        ok = v <= alpha
        if rule.endswith('_first'):
            k = int(np.argmin(ok)) - 1 if not ok.all() else len(v) - 1
        else:
            k = int(np.nonzero(ok)[0].max()) if ok.any() else -1
        out[rule] = k                                              # -1 = fall back to always low
    return out


def band_crit(ICk, seed):
    """one-sided simultaneous 95% critical value for the K estimates with influence curves ICk (n x K)."""
    C = np.corrcoef(ICk, rowvar=False)
    z = np.random.default_rng(seed).multivariate_normal(np.zeros(C.shape[0]), C, size=20000, method='eigh')
    return float(np.quantile(z.max(axis=1), 0.95))


def msm_fit(est, IC, xs):
    """working marginal structural model logit psi(x) = b0 + b1 u, u = (x - 0.71)/0.1, fitted to the K TMLE
    estimates by least squares; returns the fitted curve and its influence curves (n x K)."""
    u = (np.array(xs) - 0.71) / 0.1; X = np.column_stack([np.ones_like(u), u])
    p = np.clip(est, 1e-3, 1 - 1e-3); b = np.linalg.lstsq(X, np.log(p / (1 - p)), rcond=None)[0]
    for _ in range(50):
        m = 1 / (1 + np.exp(-X @ b)); D = X * (m * (1 - m))[:, None]
        step = np.linalg.solve(D.T @ D, D.T @ (est - m)); b += step
        if np.max(np.abs(step)) < 1e-10:
            break
    m = 1 / (1 + np.exp(-X @ b)); D = X * (m * (1 - m))[:, None]
    ICb = IC @ D @ np.linalg.inv(D.T @ D)                         # n x 2
    return m, ICb @ D.T                                            # fitted curve, its influence curves


def job(args):
    n, design, seed = args
    rng = np.random.default_rng(seed); d = T.simulate(n, rng)
    nuis = T.fit_nuisance(d, design)
    est, se, naive, ics = [], [], [], []
    for reg in REGS:
        r = T.estimate(d, reg, design=design, kinds=('flex',), nuis=nuis, return_ic=True)
        est.append(r['tmle_flex']); se.append(r['se_flex']); naive.append(r['naive']); ics.append(r['ic_flex'])
    est, se, naive = np.array(est), np.array(se), np.array(naive)
    IC = np.column_stack(ics); n_ = IC.shape[0]
    cband = band_crit(IC, seed + 7)
    m, ICm = msm_fit(est, IC, XS); sem = ICm.std(axis=0) / np.sqrt(n_); cmsm = band_crit(ICm, seed + 8)
    curves = dict(naive=naive, plugin=est, point=est + 1.645 * se, band=est + cband * se,
                  band_first=est + cband * se, msm=m + cmsm * sem)
    sel = {str(a): select(a, **curves) for a in ALPHAS}
    return dict(n=n, design=design, est=est.tolist(), se=se.tolist(), naive=naive.tolist(), cband=cband,
                msm=m.tolist(), msm_se=sem.tolist(), cmsm=cmsm, sel=sel)


if __name__ == '__main__':
    t0 = time.time(); rng = np.random.default_rng(20261016)
    truth, supply = [], []
    for reg in ['lo'] + REGS:
        y, v = T.truth(reg, NTRUTH, rng, with_vol=True); truth.append(y); supply.append(v)
        print(reg, round(y, 4), round(v, 4), f'{time.time() - t0:.0f}s', flush=True)
    psi_lo, sup_lo = truth[0], supply[0]; truth = np.array(truth[1:]); supply = np.array(supply[1:])
    oracle = {str(a): int(np.nonzero(truth <= a)[0].max()) for a in ALPHAS}
    print('oracle', {a: XS[k] for a, k in oracle.items()}, flush=True)
    jobs = [(n, des, 100000 + 1000 * i + 10000 * j + r) for i, n in enumerate(NS) for j, des in enumerate(DESIGNS) for r in range(R)]
    with Pool(4) as pool:
        out = pool.map(job, jobs, chunksize=2)
    print('runs done', f'{time.time() - t0:.0f}s', flush=True)
    res = {}
    for n in NS:
        for des in DESIGNS:
            oo = [o for o in out if o['n'] == n and o['design'] == des]
            key = f'{n}|{des}'; res[key] = {}
            est = np.array([o['est'] for o in oo]); se = np.array([o['se'] for o in oo])
            res[key]['bias'] = (est.mean(0) - truth).tolist(); res[key]['sd'] = est.std(0).tolist()
            res[key]['cover_point'] = np.mean(est + 1.645 * se >= truth, axis=0).tolist()
            cb = np.array([o['cband'] for o in oo])
            res[key]['cover_band'] = float(np.mean(np.all(est + cb[:, None] * se >= truth, axis=1)))
            res[key]['cband_mean'] = float(cb.mean())
            mm = np.array([o['msm'] for o in oo]); ms = np.array([o['msm_se'] for o in oo]); cm = np.array([o['cmsm'] for o in oo])
            res[key]['msm_bias'] = (mm.mean(0) - truth).tolist(); res[key]['msm_sd'] = mm.std(0).tolist()
            res[key]['cover_msm_band'] = float(np.mean(np.all(mm + cm[:, None] * ms >= truth, axis=1)))
            res[key]['cmsm_mean'] = float(cm.mean())
            for a in ALPHAS:
                sa = str(a); res[key][sa] = {}
                for rule in RULES:
                    ks = np.array([o['sel'][sa][rule] for o in oo])
                    risk = np.where(ks >= 0, truth[np.maximum(ks, 0)], psi_lo)
                    sup = np.where(ks >= 0, supply[np.maximum(ks, 0)], sup_lo)
                    xs = np.where(ks >= 0, np.array(XS)[np.maximum(ks, 0)], np.nan)
                    res[key][sa][rule] = dict(
                        viol=float(np.mean(risk > a)), mean_risk=float(risk.mean()),
                        fallback=float(np.mean(ks < 0)), mean_x=float(np.nanmean(xs)) if np.any(ks >= 0) else None,
                        exact=float(np.mean(ks == oracle[sa])), supply=float(sup.mean()),
                        hist=[int(np.sum(ks == k)) for k in range(-1, len(XS))])
                print(key, sa, {r: (round(res[key][sa][r]['viol'], 3), round(res[key][sa][r]['exact'], 3)) for r in RULES},
                      'band cover', round(res[key]['cover_band'], 3), flush=True)
    json.dump(dict(XS=XS, alphas=ALPHAS, NS=NS, designs=DESIGNS, R=R, NTRUTH=NTRUTH, truth=truth.tolist(),
                             supply=supply.tolist(), psi_lo=psi_lo, supply_lo=sup_lo, oracle=oracle, res=res),
              open('kufi_results.json', 'w'), indent=1, allow_nan=False)
    print(f'done in {time.time() - t0:.0f}s')
