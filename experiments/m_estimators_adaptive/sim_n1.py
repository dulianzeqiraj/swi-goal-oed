"""E4. Proposal N1: smoothed continuous adaptive design, C9 by construction, and the price of stabilisation.

Design variable x in [0, 1] (e.g. the position of the next measurement along a coastal transect, or a
normalised pumping rate). Two zones, Z0 = [0, 0.5) and Z1 = [0.5, 1]. Linear model
    y = theta_0 + theta_1 1{x >= 0.5} + theta_2 (x - 0.5) + eps,   eps ~ N(0, 1),
with regressor z(x) = (1, 1{x >= 0.5}, x - 0.5). The decision-relevant parameter is the zone contrast
theta_1. The planner uses Thompson-type allocation between zones: with p_t = P(theta_1 > 0 | data)
(conjugate Gaussian posterior, known sigma, prior N(0, 10 I)) the "optimal" design density is
    q_opt,t(x) = 2 [p_t 1{x in Z1} + (1 - p_t) 1{x in Z0}]          (uniform within the chosen zone)
and the smoothed design is q_t = (1 - gamma) q_opt,t + gamma q_sta with q_sta = U(0, 1). gamma = 0 is run
with p_t clipped to [0.005, 0.995] (otherwise q_t can vanish). Estimators of theta_1:
  OLS  least squares with the classical and the sandwich (HC0) standard error
  AW   adaptively weighted least squares, W_t = sqrt(q_sta(x_t) / q_t(x_t)), sandwich standard error
       (the self-normalised statistic of Theorem 1 of Zhang, Janson & Murphy 2021)
Checks of the proposition of N1:
  (a) variance identity  E[W_t^2 f(x_t) | H] = int f q_sta     (realised average vs compensator)
  (b) ratio bounds        q_sta / q_t <= 1/gamma
  (c) Hessian bound       H_T = (1/T) sum_t int sqrt(q_sta q_t) z z^T dx  >=  sqrt(gamma) H_sta  (pathwise)
  (d) variance inflation  Var(AW) / Var(non-adaptive q_sta design) <= 1/gamma (information equality holds)
Run: python3 sim_n1.py   (about 4 min). Output: results/n1.json
"""
import time

import numpy as np
from scipy.stats import norm

from common import dump

Z95 = norm.ppf(0.975)
SIG = 1.0
# int over each zone of z z^T dx, z = (1, 1{x>=.5}, x-.5)
def zone_moments():
    def m(a, b, ind):
        # integrals of 1, u, u^2 with u = x - .5 over [a, b]
        i0 = b - a
        i1 = ((b - .5) ** 2 - (a - .5) ** 2) / 2
        i2 = ((b - .5) ** 3 - (a - .5) ** 3) / 3
        return np.array([[i0, ind * i0, i1], [ind * i0, ind * i0, ind * i1], [i1, ind * i1, i2]])
    return m(0.0, 0.5, 0.0), m(0.5, 1.0, 1.0)


M0, M1 = zone_moments()
HSTA = M0 + M1


def run(R, T, theta1, gamma, seed, record=(), clip=0.005, keep_path=0):
    rng = np.random.default_rng(seed)
    th = np.array([0.0, theta1, 1.0])
    lam = 0.1                                     # prior precision (sigma^2 = 1)
    G = np.repeat(np.eye(3)[None] * lam, R, 0)    # posterior precision
    bvec = np.zeros((R, 3))
    A_o = np.zeros((R, 3, 3)); b_o = np.zeros((R, 3))
    A_w = np.zeros((R, 3, 3)); b_w = np.zeros((R, 3))
    # residual-based sandwiches need the data; keep sufficient statistics per replicate:
    # for OLS: sum z z^T y^2 etc. We store full arrays of z, y, w (T x R) instead (memory is fine).
    Zs = np.zeros((T, R, 3)); Ys = np.zeros((T, R)); Ws = np.zeros((T, R))
    sq0 = np.zeros(R); sq1 = np.zeros(R)          # running sums of sqrt(q_t) on each zone
    w2f = np.zeros((R, 3, 3))                     # running sum of W_t^2 z z^T  (variance identity)
    share1 = np.zeros(R)
    out = {}
    paths = []
    for t in range(1, T + 1):
        Ginv = np.linalg.inv(G)
        mu = np.einsum('rij,rj->ri', Ginv, bvec)
        p = norm.cdf(mu[:, 1] / np.sqrt(Ginv[:, 1, 1]))
        p = np.clip(p, clip, 1 - clip)
        q0 = (1 - gamma) * 2 * (1 - p) + gamma          # density on Z0
        q1 = (1 - gamma) * 2 * p + gamma                # density on Z1
        zone1 = rng.random(R) < q1 / 2                  # P(Z1) = q1 * 0.5
        x = np.where(zone1, 0.5 + 0.5 * rng.random(R), 0.5 * rng.random(R))
        qx = np.where(zone1, q1, q0)
        z = np.stack([np.ones(R), zone1.astype(float), x - 0.5], 1)
        y = z @ th + SIG * rng.standard_normal(R)
        w = np.sqrt(1.0 / qx)
        G += np.einsum('ri,rj->rij', z, z); bvec += z * y[:, None]
        Zs[t - 1] = z; Ys[t - 1] = y; Ws[t - 1] = w
        sq0 += np.sqrt(q0); sq1 += np.sqrt(q1)
        w2f += (w ** 2)[:, None, None] * np.einsum('ri,rj->rij', z, z)
        share1 += zone1
        if keep_path and t % 10 == 0:
            paths.append(dict(p=p[:keep_path].copy(), share=(share1[:keep_path] / t).copy(),
                              hmin=hess_min(sq0[:keep_path] / t, sq1[:keep_path] / t)))
        if t in record:
            out[t] = estimate(Zs[:t], Ys[:t], Ws[:t], th, sq0 / t, sq1 / t, w2f / t, share1 / t)
    return out, paths


def hess_min(a0, a1):
    """smallest generalised eigenvalue of H_T = a0 M0 + a1 M1 relative to H_sta = M0 + M1"""
    L = np.linalg.cholesky(HSTA); Li = np.linalg.inv(L)
    H = a0[:, None, None] * M0 + a1[:, None, None] * M1
    S = Li @ H @ Li.T
    return np.linalg.eigvalsh(S)[:, 0]


def estimate(Z, Y, Wt, th, a0, a1, w2f, share1):
    T = Z.shape[0]
    res = {}
    for name, w in (('ols', np.ones_like(Wt)), ('aw', Wt)):
        A = np.einsum('tr,tri,trj->rij', w, Z, Z)
        b = np.einsum('tr,tri,tr->ri', w, Z, Y)
        est = np.linalg.solve(A, b[..., None])[..., 0]
        e = Y - np.einsum('tri,ri->tr', Z, est)
        Bm = np.einsum('tr,tri,trj->rij', w ** 2 * e ** 2, Z, Z)
        Ai = np.linalg.inv(A)
        V_sw = Ai @ Bm @ Ai
        se_sw = np.sqrt(V_sw[:, 1, 1])
        d = est[:, 1] - th[1]
        res[name] = dict(est=est[:, 1], se_sw=se_sw, cov_sw=float(np.mean(np.abs(d) <= Z95 * se_sw)))
        if name == 'ols':
            s2 = (e ** 2).sum(0) / (T - 3)
            se_cl = np.sqrt(s2 * Ai[:, 1, 1])
            res[name]['se_cl'] = se_cl
            res[name]['cov_cl'] = float(np.mean(np.abs(d) <= Z95 * se_cl))
    # theory: pathwise predicted variance of the AW estimator, H_T^{-1} Sigma_sta H_T^{-1} / T with Sigma_sta = sigma^2 H_sta
    H = a0[:, None, None] * M0 + a1[:, None, None] * M1
    Hi = np.linalg.inv(H)
    Vpred = (Hi @ (SIG ** 2 * HSTA) @ Hi)[:, 1, 1] / T
    v_sta = SIG ** 2 * np.linalg.inv(HSTA)[1, 1] / T
    res['theory'] = dict(v_pred_mean=float(Vpred.mean()), v_sta=float(v_sta), hess_min=hess_min(a0, a1),
                         w2f_dev=float(np.abs(w2f - HSTA[None]).max(axis=(1, 2)).mean()),
                         w2f_11=w2f[:, 1, 1], share1=share1)
    return res


def summarise(o):
    s = {}
    for k in ('ols', 'aw'):
        s[k] = dict(cov_sw=o[k]['cov_sw'], sd=float(np.std(o[k]['est'])), bias=float(np.mean(o[k]['est'])),
                    med_se=float(np.median(o[k]['se_sw'])))
    s['ols']['cov_cl'] = o['ols']['cov_cl']
    th = o['theory']
    s['theory'] = dict(v_pred_mean=th['v_pred_mean'], v_sta=th['v_sta'], hess_min_min=float(th['hess_min'].min()),
                       hess_min_q05=float(np.quantile(th['hess_min'], 0.05)), hess_min_med=float(np.median(th['hess_min'])),
                       w2f_dev=th['w2f_dev'], w2f_11_mean=float(th['w2f_11'].mean()), w2f_11_sd=float(th['w2f_11'].std()),
                       share1_mean=float(th['share1'].mean()), share1_sd=float(th['share1'].std()))
    s['infl_sd'] = s['aw']['sd'] / np.sqrt(th['v_sta'])
    s['infl_pred'] = float(np.sqrt(th['v_pred_mean'] / th['v_sta']))
    return s


def main():
    t0 = time.time()
    res = {'gammas': [0.0, 0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 1.0]}
    R = 6000; T = 1000
    for nm, th1 in (('zero', 0.0), ('m03', 0.3)):
        res[nm] = {}
        for j, g in enumerate(res['gammas']):
            out, _ = run(R, T, th1, g, seed=1000 * (nm == 'm03') + 10 + j, record={T})
            o = out[T]
            res[nm][str(g)] = summarise(o)
            if g in (0.0, 0.2) and nm == 'zero':
                res[nm][str(g)]['hess_min_all'] = o['theory']['hess_min']
                res[nm][str(g)]['z_ols'] = (o['ols']['est'] - th1) / o['ols']['se_cl']
                res[nm][str(g)]['z_aw'] = (o['aw']['est'] - th1) / o['aw']['se_sw']
            print(nm, g, {k: (round(v['cov_sw'], 3) if isinstance(v, dict) and 'cov_sw' in v else None) for k, v in res[nm][str(g)].items()},
                  'infl', round(res[nm][str(g)]['infl_sd'], 3), round(res[nm][str(g)]['infl_pred'], 3),
                  'hmin', round(res[nm][str(g)]['theory']['hess_min_min'], 3), f'{time.time() - t0:.0f}s', flush=True)
    # coverage against T for gamma = 0 and 0.2 at zero margin
    Ts = [100, 250, 500, 1000, 2000, 4000]
    res['Ts'] = Ts
    for g in (0.0, 0.2):
        out, _ = run(3000, max(Ts), 0.0, g, seed=77 + int(10 * g), record=set(Ts))
        res[f'covT_{g}'] = {str(t): dict(ols_cl=out[t]['ols']['cov_cl'], ols_sw=out[t]['ols']['cov_sw'], aw=out[t]['aw']['cov_sw']) for t in Ts}
        print('covT', g, res[f'covT_{g}'], f'{time.time() - t0:.0f}s', flush=True)
    # running paths for the design figure (zero margin): p_t, share in Z1, smallest Hessian eigenvalue ratio
    for g in (0.0, 0.2):
        _, paths = run(40, 2000, 0.0, g, seed=500 + int(10 * g), keep_path=40)
        res[f'paths_{g}'] = dict(t=list(range(10, 2001, 10)), p=np.array([q['p'] for q in paths]).T,
                                 share=np.array([q['share'] for q in paths]).T, hmin=np.array([q['hmin'] for q in paths]).T)
    res['R'] = R; res['T'] = T; res['runtime_s'] = time.time() - t0
    dump(res, 'n1.json')


if __name__ == '__main__':
    main()
