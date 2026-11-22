"""E3. Proposal N2: score-martingale confidence sequences on bandit data, and the target of the
weighted M-estimator when the model is misspecified.

Part A (correct model, time-uniform coverage). Two Bernoulli(1/2) arms, Thompson sampling with
Beta(1,1) priors (normal approximation of the posterior), probabilities clipped to [0.05, 0.95].
Target: the mean of arm 1. For each weighting w_s in {1, W_s, W_s^2} (W_s = sqrt(pi_sta/pi_s),
pi_sta = 1/2) the score martingale S_t(theta) = sum_s w_s 1{A_s=1}(Y_s - theta) has, given A_s,
increments in an interval of length w_s 1{A_s=1}, hence is conditionally sub-Gaussian with
v_s = w_s^2 1{A_s=1}/4 (Hoeffding). The two-sided normal-mixture boundary
    |S_t| < sqrt((V_t + rho)(log((V_t + rho)/rho) + 2 log(1/alpha)))   for all t, w.p. >= 1 - alpha
(Ville's inequality applied to the Gaussian mixture of exp(lambda S_t - lambda^2 V_t / 2)) gives an
interval for theta at every t. Compared with the Wald interval recomputed at every t ("peeking").
Part B (misspecified model, fixed T). Contexts X ~ U(0,1); arm 0 pays 0.5, arm 1 pays
0.2 + 0.6 X^2, plus U(-0.2, 0.2) noise. A linear model a + b X is fitted to arm 1 (misspecified).
Contextual Thompson sampling with Bayesian linear models, clipped to [0.05, 0.95]. The target is the
projection under the stabilising policy pi_sta = 1/2: theta*_sta = (0.1, 0.6). Weighted least squares
with w in {1, W, W^2}, sandwich covariance, joint chi^2_2 region: only w = W^2 (full importance
weights towards pi_sta) is centred on theta*_sta.
Run: python3 sim_cs.py  (about 3 min). Output: results/cs.json
"""
import numpy as np
from scipy.stats import norm, chi2

from common import dump

ALPHA = 0.05


def mix_boundary(V, rho, alpha=ALPHA):
    return np.sqrt((V + rho) * (np.log((V + rho) / rho) + 2 * np.log(1 / alpha)))


def part_a(R=2000, T=5000, rho=8.0, seed=1):
    rng = np.random.default_rng(seed)
    grid = np.unique(np.round(np.geomspace(20, T, 45)).astype(int))
    n = np.zeros((2, R)); s = np.zeros((2, R))
    D = {k: np.zeros(R) for k in ('u', 'w', 'i')}; B = {k: np.zeros(R) for k in D}; V = {k: np.zeros(R) for k in D}
    SS1 = np.zeros(R)
    ever = {k: np.zeros(R, bool) for k in ('wald', 'cs_u', 'cs_w', 'cs_i')}
    out = {k: [] for k in ever}; width = {k: [] for k in ever}
    mu1 = 0.5
    for t in range(1, T + 1):
        m = (s + 1) / (n + 2); v = m * (1 - m) / (n + 3)
        pi1 = np.clip(norm.cdf((m[1] - m[0]) / np.sqrt(v[0] + v[1])), 0.05, 0.95)
        A = (rng.random(R) < pi1).astype(int)
        Y = (rng.random(R) < 0.5).astype(float)
        n[A, np.arange(R)] += 1; s[A, np.arange(R)] += Y
        a1 = A == 1
        pia = np.where(a1, pi1, 1 - pi1)
        for k, w in (('u', np.ones(R)), ('w', np.sqrt(0.5 / pia)), ('i', 0.5 / pia)):
            D[k] += w * a1; B[k] += w * a1 * Y; V[k] += w ** 2 * a1 / 4
        SS1 += a1 * Y ** 2
        if t >= 20:
            with np.errstate(divide='ignore', invalid='ignore'):
                mh = s[1] / n[1]; sd = np.sqrt(np.maximum(mh * (1 - mh), 1e-12) / n[1])
                miss = np.abs(mh - mu1) > 1.959964 * sd
                ever['wald'] |= miss & (n[1] > 1)
                wd = {'wald': 2 * 1.959964 * sd}
                for k in ('u', 'w', 'i'):
                    u = mix_boundary(V[k], rho)
                    lo = (B[k] - u) / D[k]; hi = (B[k] + u) / D[k]
                    ever['cs_' + k] |= (mu1 < lo) | (mu1 > hi)
                    wd['cs_' + k] = hi - lo
        if t in grid:
            for k in ever:
                out[k].append(float(ever[k].mean()))
                width[k].append(float(np.nanmedian(wd[k])))
    return dict(grid=grid, ever_miss=out, width=width, R=R, rho=rho, V_ratio=float(np.median(V['w'] / V['u'])))


def part_b(R=2000, T=2000, seed=2, record=(250, 500, 1000, 2000)):
    rng = np.random.default_rng(seed)
    s2 = 0.4 ** 2 / 12
    P = {a: np.repeat(np.eye(2)[None], R, 0) * 1.0 for a in (0, 1)}       # posterior precision (times s2)
    bvec = {a: np.zeros((R, 2)) for a in (0, 1)}
    acc = {k: dict(A=np.zeros((R, 2, 2)), b=np.zeros((R, 2)), Bm=np.zeros((R, 2, 2)), Z=[]) for k in ('u', 'w', 'i')}
    hist = {k: dict(x=[], y=[], w=[], a=[]) for k in ('u',)}
    X_all = np.zeros((T, R)); Y_all = np.zeros((T, R)); A_all = np.zeros((T, R), bool); PI = np.zeros((T, R))
    target = np.array([0.1, 0.6])
    out = {}
    for t in range(T):
        x = rng.random(R); z = np.stack([np.ones(R), x], 1)
        mu = {}; var = {}
        for a in (0, 1):
            Pinv = np.linalg.inv(P[a])
            mean = np.einsum('rij,rj->ri', Pinv, bvec[a])
            mu[a] = np.einsum('ri,ri->r', mean, z)
            var[a] = s2 * np.einsum('ri,rij,rj->r', z, Pinv, z)
        p1 = np.clip(norm.cdf((mu[1] - mu[0]) / np.sqrt(var[0] + var[1] + 1e-12)), 0.05, 0.95)
        A = rng.random(R) < p1
        y = np.where(A, 0.2 + 0.6 * x ** 2, 0.5) + rng.uniform(-0.2, 0.2, R)
        for a in (0, 1):
            k = A == a
            P[a][k] += np.einsum('ri,rj->rij', z[k], z[k]); bvec[a][k] += z[k] * y[k, None]
        X_all[t] = x; Y_all[t] = y; A_all[t] = A; PI[t] = p1
        if t + 1 in record:
            res = {}
            n = t + 1
            x = X_all[:n]; y = Y_all[:n]; a1 = A_all[:n]; pi = PI[:n]
            Z = np.stack([np.ones_like(x), x], -1)                          # n x R x 2
            for k, w in (('u', np.ones_like(x)), ('w', np.sqrt(0.5 / pi)), ('i', 0.5 / pi)):
                ww = w * a1
                Am = np.einsum('nr,nri,nrj->rij', ww, Z, Z)
                bb = np.einsum('nr,nri,nr->ri', ww, Z, y)
                th = np.linalg.solve(Am, bb[..., None])[..., 0]
                r = y - np.einsum('nri,ri->nr', Z, th)
                Bm = np.einsum('nr,nri,nrj->rij', ww ** 2 * r ** 2, Z, Z)
                Ainv = np.linalg.inv(Am)
                Cov = Ainv @ Bm @ Ainv
                d = th - target
                q = np.einsum('ri,rij,rj->r', d, np.linalg.inv(Cov), d)
                zsl = d[:, 1] / np.sqrt(Cov[:, 1, 1])
                res[k] = dict(cov_joint=float(np.mean(q <= chi2.ppf(0.95, 2))), cov_slope=float(np.mean(np.abs(zsl) <= 1.959964)),
                              mean_slope=float(np.mean(th[:, 1])), sd_slope=float(np.std(th[:, 1])),
                              mean_int=float(np.mean(th[:, 0])), width_slope=float(np.median(2 * 1.959964 * np.sqrt(Cov[:, 1, 1]))),
                              slopes=th[:, 1][:400])
            res['share_arm1'] = float(a1.mean())
            res['x_hist_arm1'] = np.histogram(x[a1], bins=np.linspace(0, 1, 41), density=True)[0]
            res['mean_x_arm1'] = float((x * a1).sum() / a1.sum())
            out[n] = res
    return dict(target=target, results=out, R=R)


def main():
    A = part_a()
    print('A ever-miss at T:', {k: round(v[-1], 3) for k, v in A['ever_miss'].items()}, 'V ratio', A['V_ratio'])
    Bres = part_b()
    for n, r in Bres['results'].items():
        print(n, {k: (round(v['cov_joint'], 3), round(v['mean_slope'], 3)) for k, v in r.items() if isinstance(v, dict)},
              round(r['mean_x_arm1'], 3))
    dump(dict(A=A, B=Bres), 'cs.json')


if __name__ == '__main__':
    main()
