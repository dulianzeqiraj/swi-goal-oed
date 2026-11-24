"""E1-E2. Two-arm Gaussian bandit: why Wald inference fails without weights and what the
adaptive weights of Zhang, Janson & Murphy (2021) restore.

Thompson sampling with a N(0,1) prior per arm and unit noise; probabilities clipped to
[0.05, 0.95] (the clipping of the base paper's simulations), or tempered Thompson
pi = (1-gamma) p + gamma/2 (Caria et al. 2024). Target: the mean of arm 1, mu_1, and the
margin Delta = mu_1 - mu_0. Estimators:
  OLS     arm sample mean, Wald interval with the realised count
  IPW     Horvitz-Thompson mean (1/T) sum 1{A=1} Y / pi_t(1), Wald interval
  AW      adaptively weighted M-estimator, W_t = sqrt(pi_sta / pi_t), pi_sta = 1/2, with the
          self-normalised statistic of Theorem 1 of the base paper:
          (sum W 1{A=1}) (mu_tilde - mu_1) / sqrt(sum W^2 1{A=1} (Y - mu_tilde)^2)
          and, for Delta, the projection of the chi^2_2 ellipsoid (conservative).
Run: python3 sim_bandit.py   (about 2 min). Output: results/bandit.json
"""
import numpy as np
from scipy.stats import norm, chi2

from common import dump

Z95 = norm.ppf(0.975)
PROJ = np.sqrt(chi2.ppf(0.95, 2))


def run(R, T, mu0, mu1, policy='ts', clip=0.05, gamma=0.2, seed=0, record=(), keep_paths=0, keep_z_at=None):
    rng = np.random.default_rng(seed)
    N = np.zeros((2, R)); S = np.zeros((2, R)); SS = np.zeros((2, R))
    SW = np.zeros((2, R)); SWY = np.zeros((2, R)); SW2 = np.zeros((2, R)); SW2Y = np.zeros((2, R)); SW2YY = np.zeros((2, R))
    IY = np.zeros((2, R)); IY2 = np.zeros((2, R)); I2 = np.zeros((2, R)); I2Y = np.zeros((2, R))
    cum_pi = np.zeros(R)
    paths = np.zeros((keep_paths, T)) if keep_paths else None
    pathsw = np.zeros((keep_paths, T)) if keep_paths else None
    cum_w = np.zeros(R)
    out = {}
    zs = {}
    mu = np.array([mu0, mu1])
    for t in range(1, T + 1):
        m = S / (N + 1.0); v = 1.0 / (N + 1.0)
        p = norm.cdf((m[1] - m[0]) / np.sqrt(v[0] + v[1]))
        if policy == 'ts':
            pi1 = np.clip(p, clip, 1 - clip)
        elif policy == 'sts':
            pi1 = (1 - gamma) * p + gamma / 2
        else:
            raise ValueError(policy)
        A = (rng.random(R) < pi1).astype(int)
        Y = mu[A] + rng.standard_normal(R)
        pia = np.where(A == 1, pi1, 1 - pi1)
        W = np.sqrt(0.5 / pia)
        for a in (0, 1):
            k = A == a
            N[a, k] += 1; S[a, k] += Y[k]; SS[a, k] += Y[k] ** 2
            SW[a, k] += W[k]; SWY[a, k] += W[k] * Y[k]; SW2[a, k] += W[k] ** 2
            SW2Y[a, k] += W[k] ** 2 * Y[k]; SW2YY[a, k] += W[k] ** 2 * Y[k] ** 2
            IY[a, k] += Y[k] / pia[k]; I2[a, k] += 1 / pia[k] ** 2; I2Y[a, k] += Y[k] / pia[k] ** 2
            IY2[a, k] += Y[k] ** 2 / pia[k] ** 2
        cum_pi += pi1
        cum_w += W ** 2 * (A == 1)
        if keep_paths:
            paths[:, t - 1] = cum_pi[:keep_paths] / t
            pathsw[:, t - 1] = cum_w[:keep_paths] / t
        if t in record:
            out[t] = stats(t, N, S, SS, SW, SWY, SW2, SW2Y, SW2YY, IY, IY2, I2, I2Y, mu, cum_pi)
            if keep_z_at == t:
                zs = out[t].pop('_z')
            else:
                out[t].pop('_z')
    return out, zs, (paths, pathsw)


def stats(T, N, S, SS, SW, SWY, SW2, SW2Y, SW2YY, IY, IY2, I2, I2Y, mu, cum_pi):
    with np.errstate(divide='ignore', invalid='ignore'):
        mhat = S / N
        var = np.maximum(SS / N - mhat ** 2, 1e-12)
        z_ols = (mhat[1] - mu[1]) / np.sqrt(var[1] / N[1])
        d_ols = (mhat[1] - mhat[0] - (mu[1] - mu[0])) / np.sqrt(var[1] / N[1] + var[0] / N[0])
        mt = SWY / SW
        res2 = SW2YY - 2 * mt * SW2Y + mt ** 2 * SW2
        s = np.sqrt(np.maximum(res2, 1e-12)) / SW            # standard error of mu_tilde_a
        z_aw = (mt[1] - mu[1]) / s[1]
        d_aw = (mt[1] - mt[0] - (mu[1] - mu[0])) / np.sqrt(s[1] ** 2 + s[0] ** 2)
        mi = IY / T
        vi = (IY2 - 2 * mi * I2Y + mi ** 2 * I2) / T ** 2
        z_ipw = (mi[1] - mu[1]) / np.sqrt(np.maximum(vi[1], 1e-12))
    ok = lambda z, c=Z95: np.mean(np.abs(z[np.isfinite(z)]) <= c)
    return dict(
        cov_ols=ok(z_ols), cov_aw=ok(z_aw), cov_ipw=ok(z_ipw),
        cov_d_ols=ok(d_ols), cov_d_aw_proj=ok(d_aw, PROJ), cov_d_aw_direct=ok(d_aw),
        width_ols=float(np.nanmedian(2 * Z95 * np.sqrt(var[1] / N[1]))), width_aw=float(np.nanmedian(2 * Z95 * s[1])),
        width_ipw=float(np.nanmedian(2 * Z95 * np.sqrt(vi[1]))),
        share1=cum_pi / T, _z=dict(ols=z_ols, aw=z_aw, ipw=z_ipw),
        n_finite=int(np.isfinite(z_ols).sum()))


def main():
    R = 4000
    Ts = [100, 250, 500, 1000, 2500, 5000]
    res = {'R': R, 'Ts': Ts}
    # E1a: coverage against T at zero margin and at margin 0.25 (Thompson, clipped)
    for nm, (m0, m1) in {'zero': (0.0, 0.0), 'm025': (0.0, 0.25)}.items():
        out, zs, _ = run(R, max(Ts), m0, m1, record=set(Ts), keep_z_at=1000, seed=11 if nm == 'zero' else 12)
        res[f'cov_T_{nm}'] = {k: {t: out[t][k] for t in Ts} for k in
                              ('cov_ols', 'cov_aw', 'cov_ipw', 'cov_d_ols', 'cov_d_aw_proj', 'cov_d_aw_direct',
                               'width_ols', 'width_aw', 'width_ipw')}
        res[f'z1000_{nm}'] = {k: v[np.isfinite(v)] for k, v in zs.items()}
        res[f'share_T5000_{nm}'] = out[5000]['share1']
    # E1b: coverage against the margin at T = 1000
    deltas = np.round(np.linspace(0, 0.5, 11), 3)
    res['deltas'] = deltas
    cov = {k: [] for k in ('cov_ols', 'cov_aw', 'cov_ipw', 'cov_d_ols', 'cov_d_aw_proj', 'cov_d_aw_direct')}
    for j, d in enumerate(deltas):
        out, _, _ = run(R, 1000, 0.0, float(d), record={1000}, seed=100 + j)
        for k in cov:
            cov[k].append(out[1000][k])
    res['cov_delta'] = cov
    # E2: running allocation share of arm 1 (= conditional variance of the unweighted score / sigma^2)
    P = 60
    for nm, kw in {'ts0': dict(mu1=0.0), 'ts25': dict(mu1=0.25), 'sts25': dict(mu1=0.25, policy='sts', gamma=0.2),
                   'sts0': dict(mu1=0.0, policy='sts', gamma=0.2)}.items():
        _, _, (paths, pathsw) = run(P, 5000, 0.0, kw.pop('mu1'), keep_paths=P, seed=200 + len(nm), **kw)
        res[f'paths_{nm}'] = paths[:, ::10]
        res[f'pathsw_{nm}'] = pathsw[:, ::10]
    out, _, _ = run(R, 5000, 0.0, 0.25, policy='sts', gamma=0.2, record={5000}, seed=31)
    res['share_T5000_sts25'] = out[5000]['share1']
    out, _, _ = run(R, 5000, 0.0, 0.0, policy='sts', gamma=0.2, record={5000}, seed=32)
    res['share_T5000_sts0'] = out[5000]['share1']
    # sampling distribution of the statistics at T = 1000, zero margin, with 20 000 replications
    out, zs, _ = run(20000, 1000, 0.0, 0.0, record={1000}, keep_z_at=1000, seed=41)
    bins = np.linspace(-4.5, 4.5, 61); qs = np.linspace(0.002, 0.998, 300)
    res['zdist'] = {k: dict(hist=np.histogram(v[np.isfinite(v)], bins=bins, density=True)[0], q=np.quantile(v[np.isfinite(v)], qs),
                            median=float(np.median(v[np.isfinite(v)])), cov=float(np.mean(np.abs(v[np.isfinite(v)]) <= Z95)))
                    for k, v in zs.items()}
    res['zdist']['bins'] = bins; res['zdist']['qs'] = qs; res['zdist']['R'] = 20000
    # without clipping (the two-arm design of the base paper; C9 is then not guaranteed)
    noclip = {}
    for nm, m1 in (('zero', 0.0), ('m025', 0.25)):
        out, _, _ = run(20000, 1000, 0.0, m1, clip=1e-12, record={1000}, seed=51 if m1 == 0 else 52)
        noclip[nm] = {k: out[1000][k] for k in ('cov_ols', 'cov_aw', 'cov_ipw', 'cov_d_ols', 'cov_d_aw_direct', 'cov_d_aw_proj')}
    res['noclip_T1000'] = noclip
    clipped = {}
    for nm, m1 in (('zero', 0.0), ('m025', 0.25)):
        out, _, _ = run(20000, 1000, 0.0, m1, record={1000}, seed=53 if m1 == 0 else 54)
        clipped[nm] = {k: out[1000][k] for k in ('cov_ols', 'cov_aw', 'cov_ipw', 'cov_d_ols', 'cov_d_aw_direct', 'cov_d_aw_proj')}
    res['clip005_T1000_R20000'] = clipped
    dump(res, 'bandit.json')
    for nm in ('zero', 'm025'):
        print(nm, {k: [round(v, 3) for v in d.values()] for k, d in res[f'cov_T_{nm}'].items() if k.startswith('cov')})
    print('delta', {k: [round(x, 3) for x in v] for k, v in cov.items()})


if __name__ == '__main__':
    main()
