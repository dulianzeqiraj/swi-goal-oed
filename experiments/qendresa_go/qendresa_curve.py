"""QENDRESA-GO large-sample computations -> qendresa_curve.json
  limits     estimates on one very large data set (n = 400 000) in the correct and null scenarios: the limits of
             the frugal MLE, the two-step fit, IPW and the parametric g-formula (the g-null paradox).
  are        Monte Carlo variance of beta-hat (frugal MLE vs IPW) as the copula strength rho varies (R = 300, n = 2000).
  noncoll    the conditional cloglog contrast of current pumping implied by Proposition J, against the dryness
             index m_k, for seasons 1..K (the marginal contrast is beta for every m).
  tilt       mean and sd of the season-k dryness score among the wells still at risk (latent law: 0 and 1; Prop. J(c)).
  naive      survival of the wells that always / never pumped (confounded) vs the exact counterfactual survival.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import json, time, zlib
import numpy as np
from multiprocessing import Pool
import qendresa_model as M
import qendresa_est as E

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
Zg = np.random.default_rng(2024).standard_normal((20000, M.K))


def limits():
    out = {}
    for name, msm in (('correct', M.MSM), ('null', M.NULL)):
        D = M.simulate(400_000, np.random.default_rng(31), msm=msm)
        P = E.prep(D)
        f = E.fit_frugal(P)
        f2 = E.twostep(P)
        b, se, _ = E.ipw(P)
        phi, _ = E.gform_fit(P)
        out[name] = dict(truth=M.theta_vec(msm).tolist(), frugal=f['p'][6:10].tolist(), twostep=f2['p'][6:10].tolist(),
                         twostep_past=f2['p'][:6].tolist(), frugal_past=f['p'][:6].tolist(), ipw=b.tolist(),
                         gform=E.gform_theta(phi, Zg).tolist(), rho=float(np.tanh(f['p'][10]) / np.sqrt(M.K)))
        print(name, {k: np.round(v, 3) for k, v in out[name].items() if k != 'rho'}, flush=True)
    return out


def _are_one(args):
    rho, rep = args
    D = M.simulate(2000, np.random.default_rng([int(rho * 1000), rep, 7]), rho=rho)
    P = E.prep(D)
    try:
        f = E.fit_frugal(P)
        b, se, _ = E.ipw(P)
    except Exception:
        return None
    th, sef = E.frugal_theta(f)
    return th[2], sef[2], b[2], se[2], th[3], b[3]


def are(pool, rhos=(0.0, 0.1, 0.2, 0.3, 0.35, 0.4), R=300):
    out = []
    for rho in rhos:
        r = np.array([x for x in pool.map(_are_one, [(rho, i) for i in range(R)], chunksize=5) if x is not None])
        out.append(dict(rho=rho, var_frugal=float(r[:, 0].var()), var_ipw=float(r[:, 2].var()),
                        se_frugal=float(r[:, 1].mean()), se_ipw=float(r[:, 3].mean()),
                        var_frugal_lag=float(r[:, 4].var()), var_ipw_lag=float(r[:, 5].var()), R=len(r)))
        print('rho', rho, 'Var ratio IPW/frugal', round(out[-1]['var_ipw'] / out[-1]['var_frugal'], 2), flush=True)
    return out


def noncoll(rho=M.RHO, msm=M.MSM):
    th = M.theta_vec(msm)
    ms = np.linspace(-1.5, 1.5, 61)
    curves = []
    for k in range(1, M.K + 1):
        hist = np.ones((1, M.K))                                # pumped in every earlier season
        cc = []
        for a in (0.0, 1.0):
            A = hist.copy(); A[0, k - 1] = a
            c, _ = M.surv_thresholds(A, th)
            c_prev = c[0, k - 2] if k >= 2 else np.inf
            s = np.sqrt(1 - k * rho ** 2)
            cc.append(M.cond_hazard(ms, s, c_prev, c[0, k - 1]))
        h0, h1 = cc
        curves.append(dict(k=k, contrast=(np.log(-np.log1p(-h1)) - np.log(-np.log1p(-h0))).tolist(),
                           h0=h0.tolist(), h1=h1.tolist()))
    return dict(m=ms.tolist(), beta=float(th[2]), curves=curves)


def tilt():
    D = M.simulate(400_000, np.random.default_rng(32))
    O = E.prep(D)['O']
    res = []
    for k in range(M.K):
        w = D['W'][:, k]
        res.append(dict(k=k + 1, at_risk=float(O[:, k].mean()), mean_w_at_risk=float(w[O[:, k]].mean()),
                        sd_w_at_risk=float(w[O[:, k]].std())))
    return res


def naive():
    """Survival of the wells that pumped in every season so far vs those that never pumped (confounded), against the
    exact counterfactual survival under always and never pumping."""
    D = M.simulate(400_000, np.random.default_rng(33))
    P = E.prep(D)
    out = {}
    for lab, a in (('always', 1.0), ('never', 0.0)):
        keep = np.cumprod(P['A'] == a, axis=1).astype(bool)   # followed the static regime up to season k
        S, curve = 1.0, []
        for k in range(M.K):
            risk = P['O'][:, k] & keep[:, k]
            S *= 1 - P['Dk'][risk, k].mean()
            curve.append(S)
        out[lab] = curve
    regs, Strue = M.true_static()
    out['true_always'] = Strue[-1].tolist(); out['true_never'] = Strue[0].tolist()
    return out


if __name__ == '__main__':
    t0 = time.time()
    out = dict(limits=limits(), noncoll=noncoll(), tilt=tilt(), naive=naive())
    with Pool(4) as pool:
        out['are'] = are(pool)
    json.dump(out, open('qendresa_curve.json', 'w'), indent=1)
    print(f'done in {time.time() - t0:.0f}s')
