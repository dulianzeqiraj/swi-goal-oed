"""KUFI-GO, designed alternative: the same number of wells, but each well is assigned a threshold at random
from the grid and the operator follows it (no drop-out: the experiment keeps every well monitored).
psi(x) is estimated by the arm means; the working MSM logit psi(x) = b0 + b1 u is fitted by pooled logistic
regression with sandwich influence curves. The same selection rules as kufi_exp.py are applied.
Adds res['<n>|rct'] to kufi_results.json."""
import json, time
import numpy as np
from multiprocessing import Pool
import tmle_go as T
import kufi_exp as K


def job(args):
    n, seed = args
    rng = np.random.default_rng(seed)
    k = rng.integers(0, len(K.XS), n); thr = np.array(K.XS)[k]
    d = T.simulate(n, rng, regime=thr); Y = d['Y']
    est = np.array([Y[k == j].mean() for j in range(len(K.XS))])
    nj = np.array([(k == j).sum() for j in range(len(K.XS))])
    IC = np.zeros((n, len(K.XS)))
    for j in range(len(K.XS)):
        IC[:, j] = (k == j) * (Y - est[j]) * n / nj[j]
    se = IC.std(axis=0) / np.sqrt(n)
    cband = K.band_crit(IC, seed + 7)
    u = (thr - 0.71) / 0.1; X = np.column_stack([np.ones(n), u]); b = np.zeros(2)
    for _ in range(50):
        m = 1 / (1 + np.exp(-X @ b)); H = (X * (m * (1 - m))[:, None]).T @ X
        step = np.linalg.solve(H, X.T @ (Y - m)); b += step
        if np.max(np.abs(step)) < 1e-10:
            break
    m = 1 / (1 + np.exp(-X @ b)); H = (X * (m * (1 - m))[:, None]).T @ X / n
    ICb = (X * (Y - m)[:, None]) @ np.linalg.inv(H).T                  # n x 2
    ug = (np.array(K.XS) - 0.71) / 0.1; Xg = np.column_stack([np.ones_like(ug), ug])
    mg = 1 / (1 + np.exp(-Xg @ b)); Dg = Xg * (mg * (1 - mg))[:, None]
    ICm = ICb @ Dg.T; sem = ICm.std(axis=0) / np.sqrt(n); cmsm = K.band_crit(ICm, seed + 8)
    curves = dict(naive=est, plugin=est, point=est + 1.645 * se, band=est + cband * se,
                  band_first=est + cband * se, msm=mg + cmsm * sem)
    sel = {str(a): K.select(a, **curves) for a in K.ALPHAS}
    return dict(est=est.tolist(), se=se.tolist(), cband=cband, msm=mg.tolist(), msm_se=sem.tolist(), cmsm=cmsm, sel=sel)


if __name__ == '__main__':
    t0 = time.time()
    RS = json.load(open('kufi_results.json'))
    truth = np.array(RS['truth']); supply = np.array(RS['supply']); psi_lo = RS['psi_lo']; sup_lo = RS['supply_lo']
    for i, n in enumerate(K.NS):
        with Pool(4) as pool:
            oo = pool.map(job, [(n, 900000 + 1000 * i + r) for r in range(K.R)])
        key = f'{n}|rct'; res = {}
        est = np.array([o['est'] for o in oo]); se = np.array([o['se'] for o in oo]); cb = np.array([o['cband'] for o in oo])
        res['bias'] = (est.mean(0) - truth).tolist(); res['sd'] = est.std(0).tolist()
        res['cover_point'] = np.mean(est + 1.645 * se >= truth, axis=0).tolist()
        res['cover_band'] = float(np.mean(np.all(est + cb[:, None] * se >= truth, axis=1))); res['cband_mean'] = float(cb.mean())
        mm = np.array([o['msm'] for o in oo]); ms = np.array([o['msm_se'] for o in oo]); cm = np.array([o['cmsm'] for o in oo])
        res['msm_bias'] = (mm.mean(0) - truth).tolist(); res['msm_sd'] = mm.std(0).tolist()
        res['cover_msm_band'] = float(np.mean(np.all(mm + cm[:, None] * ms >= truth, axis=1))); res['cmsm_mean'] = float(cm.mean())
        for a in K.ALPHAS:
            sa = str(a); res[sa] = {}
            for rule in K.RULES:
                ks = np.array([o['sel'][sa][rule] for o in oo])
                risk = np.where(ks >= 0, truth[np.maximum(ks, 0)], psi_lo)
                sup = np.where(ks >= 0, supply[np.maximum(ks, 0)], sup_lo)
                xs = np.where(ks >= 0, np.array(K.XS)[np.maximum(ks, 0)], np.nan)
                res[sa][rule] = dict(viol=float(np.mean(risk > a)), mean_risk=float(risk.mean()), fallback=float(np.mean(ks < 0)),
                                     mean_x=float(np.nanmean(xs)) if np.any(ks >= 0) else None,
                                     exact=float(np.mean(ks == RS['oracle'][sa])), supply=float(sup.mean()),
                                     hist=[int(np.sum(ks == kk)) for kk in range(-1, len(K.XS))])
            print(key, sa, {r: (round(res[sa][r]['viol'], 3), round(res[sa][r]['supply'], 4)) for r in K.RULES},
                  'band cover', round(res['cover_band'], 3), 'msm cover', round(res['cover_msm_band'], 3), flush=True)
        RS['res'][key] = res
    RS['designs'] = RS['designs'] + ['rct'] if 'rct' not in RS['designs'] else RS['designs']
    json.dump(RS, open('kufi_results.json', 'w'), indent=1, allow_nan=False)
    print(f'done in {time.time() - t0:.0f}s')
