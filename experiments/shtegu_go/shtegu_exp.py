"""SHTEGU-GO ("shtegu" = the path): warnings for what happens between samples.

Chloride at a wellfield is sampled every few weeks or months, but the limit can be crossed between two samples. The
probability of crossing within a season is a path functional (a "lookback" in the language of the robust pricing
article), whereas sparse samples pin only the marginal law (the "vanilla prices"). Following the two articles of the
review (path-dependent neural jump ODEs; robust pricing with neural SDEs) the tests ask:
  T37  does the marginal law bound the exceedance probability between samples (Proposition S1, Slepian ordering), and
       how much do quarterly, monthly, weekly samples or a daily logger say about the time scale (Proposition S2)?
  T38  the robust band over a richer family of models consistent with the statistics each design observes (the robust
       pricing problem: inf and sup of the path functional subject to calibration);
  T39  certification of the band when the true chloride law is skewed (outside the family): split-conformal margin
       (Proposition S3);
  T40  online warnings from irregular, incomplete records: the L2-optimal forecaster trained on simulated records (the
       principle of the neural jump ODE) with Markov features, path features, and path features with a head logger.
Units: days, chloride in mg/L; the chloride anomaly is standardised (mean 0, variance 1) unless stated.
Results: res/shtegu.json, res/shtegu_log.txt. usage: python3 shtegu_exp.py [quick]"""
import json
import os
import sys
import time

import numpy as np
from scipy.stats import norm, chi2
from scipy.optimize import minimize_scalar, minimize

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
QUICK = 'quick' in sys.argv
LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


T_SEASON = 120.0        # season length (days)
DT = 0.25               # simulation step (days)
MU, SD, LIMIT = 180.0, 35.0, 250.0    # chloride mean, standard deviation, limit (mg/L)
Z0 = (LIMIT - MU) / SD                # standardised limit (2.0)
KAPPA_TRUE = 1 / 8.0                  # single-OU truth of T37 (correlation time 8 days)
YEARS = 8                             # length of the record
DESIGNS = [('quarterly samples', 91.0), ('monthly samples', 30.0), ('weekly samples', 7.0), ('daily logger', 1.0)]


# ------------------------------------------------------------------------------------------------ simulation core
def ou_paths(kappa, n_paths, n_steps, dt, rng=None, eps=None):
    """Stationary standardised OU paths (exact transitions); eps: optional common normals (n_paths, n_steps+1)."""
    if eps is None:
        eps = rng.standard_normal((n_paths, n_steps + 1))
    rho = np.exp(-kappa * dt)
    s = np.sqrt(1 - rho ** 2)
    X = np.empty_like(eps)
    X[:, 0] = eps[:, 0]
    for k in range(n_steps):
        X[:, k + 1] = rho * X[:, k] + s * eps[:, k + 1]
    return X


def bridge_max(Y, sig2, dt, U):
    """Running maximum of each path with the exact Brownian-bridge maximum inside every step (local variance sig2)."""
    a, b = Y[:, :-1], Y[:, 1:]
    m = 0.5 * (a + b + np.sqrt((b - a) ** 2 - 2 * sig2 * dt * np.log(U)))
    return m.max(axis=1)


def exceed_curve_single(kappas, zs, n_paths, rng):
    """P(sup over the season of a stationary OU >= z), common random numbers over kappa."""
    n = int(T_SEASON / DT)
    eps = rng.standard_normal((n_paths, n + 1))
    U = rng.uniform(size=(n_paths, n))
    out = np.empty((len(kappas), len(zs)))
    for i, k in enumerate(kappas):
        X = ou_paths(k, n_paths, n, DT, eps=eps)
        M = bridge_max(X, 2 * k, DT, U)
        out[i] = (M[:, None] >= np.asarray(zs)[None, :]).mean(0)
    return out


def exceed_table(kf_grid, ks_grid, w_grid, zs, n_paths, rng, horizon=T_SEASON):
    """P(sup >= z) for Y = sqrt(w) X_fast + sqrt(1-w) X_slow, independent stationary OU components."""
    n = int(horizon / DT)
    ef = rng.standard_normal((n_paths, n + 1))
    es = rng.standard_normal((n_paths, n + 1))
    U = rng.uniform(size=(n_paths, n))
    Xf = [ou_paths(k, n_paths, n, DT, eps=ef) for k in kf_grid]
    Xs = [ou_paths(k, n_paths, n, DT, eps=es) for k in ks_grid]
    P = np.empty((len(kf_grid), len(ks_grid), len(w_grid), len(zs)))
    zz = np.asarray(zs)[None, :]
    for i, kf in enumerate(kf_grid):
        for j, ks in enumerate(ks_grid):
            for l, w in enumerate(w_grid):
                Y = np.sqrt(w) * Xf[i] + np.sqrt(1 - w) * Xs[j]
                M = bridge_max(Y, 2 * (w * kf + (1 - w) * ks), DT, U)
                P[i, j, l] = (M[:, None] >= zz).mean(0)
    return P


def acf2(tau, kf, ks, w):
    return w * np.exp(-kf * tau) + (1 - w) * np.exp(-ks * tau)


# ------------------------------------------------------------------------------------------------ T37 single OU
def fisher_pair(kappa, tau):
    """Fisher information on kappa from one transition of a standardised stationary OU over lag tau (Proposition S2)."""
    r = np.exp(-kappa * tau)
    return tau ** 2 * r ** 2 * (1 + r ** 2) / (1 - r ** 2) ** 2


def sample_times(days, step, rng, jitter=0.2):
    t, out = 0.0, []
    while t < days:
        out.append(t)
        t += step * (1 + rng.uniform(-jitter, jitter))
    return np.array(out)


def ou_at_times(times, kappa, rng):
    x = np.empty(len(times))
    x[0] = rng.standard_normal()
    for i in range(1, len(times)):
        r = np.exp(-kappa * (times[i] - times[i - 1]))
        x[i] = r * x[i - 1] + np.sqrt(1 - r ** 2) * rng.standard_normal()
    return x


def ou_loglik(kappa, times, x):
    """Exact log-likelihood of standardised stationary OU observations at irregular times (marginals known)."""
    dtau = np.diff(times)
    r = np.exp(-kappa * dtau)
    v = 1 - r ** 2
    res = x[1:] - r * x[:-1]
    return float(norm.logpdf(x[0]) - 0.5 * np.sum(np.log(2 * np.pi * v) + res ** 2 / v))


def kappa_ci(times, x, kgrid):
    """Maximum-likelihood estimate and 95% likelihood-ratio interval of kappa (ends found by root-finding)."""
    from scipy.optimize import brentq
    lo_, hi_ = np.log(kgrid[0]), np.log(kgrid[-1])
    f = lambda q: -ou_loglik(np.exp(q), times, x)
    ll = np.array([-f(np.log(k)) for k in kgrid])
    i = int(np.argmax(ll))
    a, b = np.log(kgrid[max(i - 1, 0)]), np.log(kgrid[min(i + 1, len(kgrid) - 1)])
    r = minimize_scalar(f, bounds=(a, b), method='bounded', options=dict(xatol=1e-6))
    qh, lmax = r.x, -r.fun
    cut = lmax - 0.5 * chi2.ppf(0.95, 1)
    g = lambda q: -f(q) - cut
    open_lo = g(lo_) > 0
    open_hi = g(hi_) > 0
    klo = kgrid[0] if open_lo else np.exp(brentq(g, lo_, qh))
    khi = kgrid[-1] if open_hi else np.exp(brentq(g, qh, hi_))
    return float(np.exp(qh)), float(klo), float(khi), bool(open_hi), bool(open_lo)


def t37(rng):
    kgrid = np.exp(np.linspace(np.log(1 / 400), np.log(4.0), 41 if QUICK else 61))
    zs = np.round(np.arange(1.4, 2.61, 0.1), 2)
    P = exceed_curve_single(kgrid, zs, 4000 if QUICK else 16000, rng)
    iz = int(np.argmin(abs(zs - Z0)))
    curve = P[:, iz]
    p_true = float(np.interp(np.log(KAPPA_TRUE), np.log(kgrid), curve))
    mono = float(np.min(np.diff(curve)))
    out = dict(kgrid=kgrid.tolist(), zs=zs.tolist(), curve=curve.tolist(), p_true=p_true, p_marginal=float(norm.sf(Z0)),
               p_at_max=float(curve[-1]), min_increment=mono, designs={})
    days = YEARS * 365.0
    R = 60 if QUICK else 200
    for name, step in DESIGNS:
        rows = []
        for r in range(R):
            tt = sample_times(days, step, rng)
            x = ou_at_times(tt, KAPPA_TRUE, rng)
            kh, klo, khi, open_hi, open_lo = kappa_ci(tt, x, kgrid)
            plo = float(np.interp(np.log(klo), np.log(kgrid), curve))
            phi = float(np.interp(np.log(khi), np.log(kgrid), curve))
            # what the samples show: share of seasons with a sample above the limit
            seas = (tt // T_SEASON).astype(int)
            hit = np.array([np.any(x[seas == s_] >= Z0) for s_ in np.unique(seas)])
            rows.append(dict(kh=kh, klo=klo, khi=khi, open_hi=open_hi, plo=plo, phi=phi, cover=plo <= p_true <= phi,
                             seen=float(hit.mean())))
        n_pairs = len(sample_times(days, step, np.random.default_rng(0))) - 1
        info = n_pairs * fisher_pair(KAPPA_TRUE, step)
        out['designs'][name] = dict(
            step=step, n_samples=n_pairs + 1, crb_rel_se=float(1 / np.sqrt(info) / KAPPA_TRUE),
            open_upper=float(np.mean([q['open_hi'] for q in rows])),
            klo_med=float(np.median([q['klo'] for q in rows])), khi_med=float(np.median([q['khi'] for q in rows])),
            plo_med=float(np.median([q['plo'] for q in rows])), phi_med=float(np.median([q['phi'] for q in rows])),
            width_med=float(np.median([q['phi'] - q['plo'] for q in rows])),
            coverage=float(np.mean([q['cover'] for q in rows])), seen_mean=float(np.mean([q['seen'] for q in rows])))
        d = out['designs'][name]
        log(f"  T37 {name:18s}: band {d['plo_med']:.3f}-{d['phi_med']:.3f} (true {p_true:.3f}), upper bound open in "
            f"{100 * d['open_upper']:.0f}%, coverage {d['coverage']:.2f}, samples show {d['seen_mean']:.3f}, "
            f"CRB rel. s.e. {d['crb_rel_se']:.2f}")
    taus = np.linspace(0.25, 120, 240)
    out['fisher_tau'] = taus.tolist()
    out['fisher'] = (fisher_pair(KAPPA_TRUE, taus) * KAPPA_TRUE ** 2).tolist()      # in units of 1/kappa^2
    return out


# ------------------------------------------------------------------------------------------------ T38 robust band
KF = np.exp(np.linspace(np.log(1 / 30), np.log(1.0), 9))
KS = np.exp(np.linspace(np.log(1 / 400), np.log(1 / 8), 9))
WG = np.linspace(0.0, 1.0, 11)
ZT = np.round(np.arange(1.0, 3.01, 0.1), 2)
TRUTH2 = dict(kf=1 / 3.0, ks=1 / 40.0, w=0.6)
LAGS = {'quarterly samples': [91, 182], 'monthly samples': [30, 61, 91], 'weekly samples': [7, 14, 30, 61],
        'daily logger': [1, 2, 4, 7, 14, 30, 61]}


class Interp:
    """Multilinear interpolation of the exceedance table in (log kf, log ks, w, z)."""

    def __init__(self, P):
        from scipy.interpolate import RegularGridInterpolator
        self.f = RegularGridInterpolator((np.log(KF), np.log(KS), WG, ZT), P, bounds_error=False, fill_value=None)

    def __call__(self, kf, ks, w, z):
        pts = np.stack(np.broadcast_arrays(np.log(kf), np.log(ks), w, z), -1)
        return np.clip(self.f(pts), 0.0, 1.0)

    def one(self, kf, ks, w, z):
        return float(np.ravel(self(np.atleast_1d(kf), np.atleast_1d(ks), np.atleast_1d(w), np.atleast_1d(z)))[0])


def eval_grid(nf=31, ns=31, nw=41):
    kf = np.exp(np.linspace(np.log(KF[0]), np.log(KF[-1]), nf))
    ks = np.exp(np.linspace(np.log(KS[0]), np.log(KS[-1]), ns))
    w = np.linspace(0, 1, nw)
    F, S, W = np.meshgrid(kf, ks, w, indexing='ij')
    keep = F > S                                   # the fast component is the faster one
    return F[keep], S[keep], W[keep]


def acf_se(rho, n_pairs):
    """Bartlett-type standard error of a lag autocorrelation estimated from n_pairs pairs."""
    return (1 - rho ** 2) / np.sqrt(max(n_pairs, 1)) + 1e-3


def band(interp, G, lags, rho_hat, se, z_lo, z_hi):
    F, S, W = G
    ok = np.ones(F.shape, bool)
    for tau, rh, s in zip(lags, rho_hat, se):
        ok &= np.abs(acf2(tau, F, S, W) - rh) <= 2 * s
    if not ok.any():                                # nothing within tolerance: keep the closest tenth of a percent
        dev = sum(((acf2(t_, F, S, W) - r_) / s_) ** 2 for t_, r_, s_ in zip(lags, rho_hat, se))
        ok = dev <= np.quantile(dev, 0.001)
    lo = interp(F[ok], S[ok], W[ok], np.full(ok.sum(), z_hi)).min()
    hi = interp(F[ok], S[ok], W[ok], np.full(ok.sum(), z_lo)).max()
    return float(lo), float(hi), int(ok.sum())


def t38(interp, G, rng):
    tr = TRUTH2
    p_true = interp.one(tr['kf'], tr['ks'], tr['w'], Z0)
    out = dict(p_true=p_true, truth=tr, designs={})
    days = YEARS * 365.0
    lo, hi, n = band(interp, G, [], [], [], Z0, Z0)
    out['marginals_only'] = dict(lo=lo, hi=hi, n=n)
    log(f'  T38 marginals only: band {lo:.3f}-{hi:.3f} (true {p_true:.3f}, {n} models)')
    for name, step in DESIGNS:
        lags = LAGS[name]
        rh = [acf2(t_, tr['kf'], tr['ks'], tr['w']) for t_ in lags]
        se = [acf_se(r_, days / max(step, t_)) for r_, t_ in zip(rh, lags)]
        lo, hi, n = band(interp, G, lags, rh, se, Z0, Z0)
        out['designs'][name] = dict(lo=lo, hi=hi, n=n, lags=lags)
        log(f'  T38 {name:18s}: band {lo:.3f}-{hi:.3f} ({n} consistent models)')
    return out


# ------------------------------------------------------------------------------------------------ T39 certification
def skew_map(y, s):
    """Monotone skewing map of a standard normal: lognormal-type for s > 0, standardised (mean 0, variance 1)."""
    if s < 1e-9:
        return y
    m = np.exp(s ** 2 / 2)
    v = (np.exp(s ** 2) - 1) * np.exp(s ** 2)
    return (np.exp(s * y) - m) / np.sqrt(v)


def skew_inv(c, s):
    if s < 1e-9:
        return c
    m = np.exp(s ** 2 / 2)
    v = (np.exp(s ** 2) - 1) * np.exp(s ** 2)
    return np.log(c * np.sqrt(v) + m) / s


def sim_record_2c(times, kf, ks, w, rng):
    xf, xs = ou_at_times(times, kf, rng), ou_at_times(times, ks, rng)
    return np.sqrt(w) * xf + np.sqrt(1 - w) * xs


def t39(interp, G, rng):
    """Outer law: two-component OU pushed through a skewing map (chloride is right-skewed). The band is computed with the
    Gaussian two-component family from each aquifer's own record (monthly samples, and weekly samples)."""
    J = 80 if QUICK else 200
    days = YEARS * 365.0
    alpha = 0.10
    res = {}
    for name in ('monthly samples', 'weekly samples', 'daily logger'):
        step = dict(DESIGNS)[name]
        lags = LAGS[name]
        recs = []
        for j in range(2 * J):
            kf = float(np.exp(rng.uniform(np.log(1 / 6), np.log(1 / 1.5))))
            ks = float(np.exp(rng.uniform(np.log(1 / 80), np.log(1 / 15))))
            w = float(rng.uniform(0.3, 0.8))
            s = float(rng.uniform(0.0, 0.6))
            mu, sd = MU * rng.uniform(0.9, 1.1), SD * rng.uniform(0.85, 1.15)
            zstar = skew_inv((LIMIT - mu) / sd, s)          # the limit on the Gaussian scale
            p_true = interp.one(kf, ks, w, np.clip(zstar, ZT[0], ZT[-1]))
            tt = sample_times(days, step, rng)
            c = mu + sd * skew_map(sim_record_2c(tt, kf, ks, w, rng), s)
            m_hat, s_hat = c.mean(), c.std(ddof=1)
            n = len(c)
            neff = n * (1 - acf2(step, kf, ks, w)) / (1 + acf2(step, kf, ks, w))
            se_m, se_s = s_hat / np.sqrt(max(neff, 2)), s_hat / np.sqrt(2 * max(neff, 2))
            z_lo = (LIMIT - (m_hat + 2 * se_m)) / (s_hat + 2 * se_s)
            z_hi = (LIMIT - (m_hat - 2 * se_m)) / max(s_hat - 2 * se_s, 1e-6)
            u = (c - m_hat) / s_hat
            rh, se = [], []
            for t_ in lags:
                # pairs of samples about t_ apart: index offset on the (jittered, nearly regular) sampling
                m = max(1, int(round(t_ / step)))
                if len(u) <= m + 5:
                    continue
                r_ = float(np.mean(u[:-m] * u[m:]))
                rh.append(r_); se.append(acf_se(r_, len(u) - m))
            use = lags[:len(rh)]
            lo, hi, nm = band(interp, G, use, rh, se, np.clip(z_lo, ZT[0], ZT[-1]), np.clip(z_hi, ZT[0], ZT[-1]))
            recs.append(dict(p=p_true, lo=lo, hi=hi, s=s))
        cal, test = recs[:J], recs[J:]
        d = np.array([max(0.0, r['p'] - r['hi'], r['lo'] - r['p']) for r in cal])
        k = int(np.ceil((J + 1) * (1 - alpha)))
        delta = float(np.sort(d)[min(k, J) - 1])
        raw = np.mean([r['lo'] <= r['p'] <= r['hi'] for r in test])
        cert = np.mean([r['lo'] - delta <= r['p'] <= r['hi'] + delta for r in test])
        # the same over 50 random calibration / test splits of the 2J aquifers (the guarantee is on average)
        dall = np.array([max(0.0, r['p'] - r['hi'], r['lo'] - r['p']) for r in recs])
        covs, dels = [], []
        for _ in range(50):
            perm = rng.permutation(2 * J)
            dc, dt_ = dall[perm[:J]], dall[perm[J:]]
            de = float(np.sort(dc)[min(k, J) - 1])
            covs.append(float(np.mean(dt_ <= de))); dels.append(de)
        w_raw = np.median([r['hi'] - r['lo'] for r in test])
        hi_skew = [r for r in test if r['s'] > 0.4]
        raw_skew = np.mean([r['lo'] <= r['p'] <= r['hi'] for r in hi_skew]) if hi_skew else float('nan')
        res[name] = dict(J=J, delta=delta, raw=float(raw), certified=float(cert), width_raw=float(w_raw),
                         cert_split_mean=float(np.mean(covs)), cert_split_p10=float(np.quantile(covs, 0.1)),
                         cert_split_p90=float(np.quantile(covs, 0.9)), delta_split_median=float(np.median(dels)),
                         raw_all=float(np.mean(dall == 0)),
                         width_cert=float(w_raw + 2 * delta), raw_high_skew=float(raw_skew),
                         n_high_skew=len(hi_skew), alpha=alpha,
                         pts=[(r['p'], r['lo'], r['hi'], r['s']) for r in test[:120]])
        log(f"  T39 {name:16s}: raw coverage {raw:.2f} (strong skew {raw_skew:.2f}), margin {delta:.3f}, "
            f"certified coverage {cert:.2f} (50 splits: mean {np.mean(covs):.3f}, 10-90% "
            f"{np.quantile(covs, 0.1):.2f}-{np.quantile(covs, 0.9):.2f}), median width {w_raw:.3f} -> "
            f"{w_raw + 2 * delta:.3f}")
    return res


# ------------------------------------------------------------------------------------------------ T40 online warning
def logistic_fit(X, y, lam=1e-3, iters=50):
    """Logistic regression by Newton steps with a small ridge (the L2 / log-loss learner used as a stand-in)."""
    Xb = np.hstack([np.ones((len(X), 1)), X])
    b = np.zeros(Xb.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-Xb @ b))
        g = Xb.T @ (p - y) + lam * b
        H = (Xb * (p * (1 - p))[:, None]).T @ Xb + lam * np.eye(len(b))
        step = np.linalg.solve(H, g)
        b -= step
        if np.max(np.abs(step)) < 1e-8:
            break
    return b


def logistic_pred(b, X):
    return 1 / (1 + np.exp(-(b[0] + X @ b[1:])))


def t40(rng):
    """Online warning: at a random time t, P(chloride exceeds the limit within the next 30 days | records so far).
    Truth: two-component chloride (fast pumping/tide, slow recharge memory); the head logger sees the slow component
    with noise and gaps; chloride is sampled at Poisson times (mean 14 days) with laboratory noise."""
    N = 6000 if QUICK else 24000
    past, ahead = 90.0, 30.0
    n_p, n_a = int(past / DT), int(ahead / DT)
    kf, ks, w = TRUTH2['kf'], TRUTH2['ks'], TRUTH2['w']
    eps_f = rng.standard_normal((N, n_p + n_a + 1))
    eps_s = rng.standard_normal((N, n_p + n_a + 1))
    Xf = ou_paths(kf, N, n_p + n_a, DT, eps=eps_f)
    Xs = ou_paths(ks, N, n_p + n_a, DT, eps=eps_s)
    Y = np.sqrt(w) * Xf + np.sqrt(1 - w) * Xs
    zlim = 1.6                                   # a 30-day window: lower limit to keep the event frequent enough
    U = rng.uniform(size=(N, n_a))
    M = bridge_max(Y[:, n_p:], 2 * (w * kf + (1 - w) * ks), DT, U)
    target = (M >= zlim).astype(float)
    tgrid = np.arange(n_p + 1) * DT
    feats_m, feats_p, feats_h = [], [], []
    for i in range(N):
        # chloride samples: Poisson times in the past window, lab noise 5% of sd
        k = rng.poisson(past / 14.0)
        ts = np.sort(rng.uniform(0, past, size=max(k, 1)))
        idx = np.minimum((ts / DT).astype(int), n_p)
        cs = Y[i, idx] + 0.05 * rng.standard_normal(len(idx))
        el = past - ts[-1]
        last = cs[-1]
        prev = cs[-2] if len(cs) > 1 else 0.0
        gap = (ts[-1] - ts[-2]) if len(cs) > 1 else past
        mx = cs[ts >= past - 60].max() if np.any(ts >= past - 60) else last
        mn = cs[ts >= past - 60].mean() if np.any(ts >= past - 60) else last
        cnt = float(np.sum(ts >= past - 60))
        decay = np.exp(-el / 10.0)
        feats_m.append([last * decay, el / past, last])
        feats_p.append([last * decay, el / past, last, prev, gap / past, mx, mn, cnt / 10.0])
        # head logger: daily readings of the slow component plus noise, 20% missing
        days_ = np.arange(past - 14, past, 1.0)
        keep = rng.uniform(size=len(days_)) > 0.2
        hd = Xs[i, np.minimum((days_[keep] / DT).astype(int), n_p)] + 0.1 * rng.standard_normal(keep.sum())
        h_last = hd[-1] if len(hd) else 0.0
        h_mean = hd.mean() if len(hd) else 0.0
        h_trend = (np.polyfit(days_[keep], hd, 1)[0] * 14) if len(hd) > 3 else 0.0
        feats_h.append(feats_p[-1] + [h_last, h_mean, h_trend])
    del tgrid
    split = int(0.6 * N)
    out = {}
    clim = target[:split].mean()
    bs_clim = float(np.mean((target[split:] - clim) ** 2))
    for name, F in (('Markov features (last sample)', feats_m), ('path features (samples)', feats_p),
                    ('path features + head logger', feats_h)):
        F = np.array(F)
        mu_, sd_ = F[:split].mean(0), F[:split].std(0) + 1e-9
        Fz = (F - mu_) / sd_
        b = logistic_fit(Fz[:split], target[:split])
        p = logistic_pred(b, Fz[split:])
        bs = float(np.mean((target[split:] - p) ** 2))
        # reliability in deciles of the forecast
        q = np.quantile(p, np.linspace(0, 1, 11))
        bins = np.clip(np.searchsorted(q, p, side='right') - 1, 0, 9)
        rel = [(float(p[bins == b_].mean()), float(target[split:][bins == b_].mean())) for b_ in range(10)
               if np.any(bins == b_)]
        out[name] = dict(brier=bs, skill=float(1 - bs / bs_clim), reliability=rel)
        log(f'  T40 {name:32s}: Brier {bs:.4f}, skill {100 * (1 - bs / bs_clim):.1f}% over climatology')
    out['climatology'] = dict(rate=float(clim), brier=bs_clim)
    out['N'] = N
    return out


# ------------------------------------------------------------------------------------------------ checks
def checks(rng):
    out = {}
    # bridge maximum against a fine-grid maximum for a slow OU (both converge)
    k = 1 / 20.0
    n = int(T_SEASON / DT)
    eps = rng.standard_normal((20000, n + 1))
    U = rng.uniform(size=(20000, n))
    X = ou_paths(k, 20000, n, DT, eps=eps)
    out['p_bridge'] = float((bridge_max(X, 2 * k, DT, U) >= Z0).mean())
    out['p_grid'] = float((X.max(1) >= Z0).mean())
    # kappa -> 0 limit of the exceedance probability equals the marginal tail
    X0 = ou_paths(1e-5, 20000, n, DT, eps=eps)
    out['p_slow'] = float((bridge_max(X0, 2e-5, DT, U) >= Z0).mean())
    out['p_marginal'] = float(norm.sf(Z0))
    # Fisher information: Monte Carlo of the score variance against the closed form
    tau = 7.0
    r = np.exp(-KAPPA_TRUE * tau)
    x0 = rng.standard_normal(200000)
    x1 = r * x0 + np.sqrt(1 - r ** 2) * rng.standard_normal(200000)
    h = 1e-5

    def ll(kk):
        rr = np.exp(-kk * tau)
        vv = 1 - rr ** 2
        return -0.5 * (np.log(vv) + (x1 - rr * x0) ** 2 / vv)
    score = (ll(KAPPA_TRUE + h) - ll(KAPPA_TRUE - h)) / (2 * h)
    out['fisher_mc'] = float(np.var(score))
    out['fisher_closed'] = float(fisher_pair(KAPPA_TRUE, tau))
    # short-lag limit 1/(2 kappa^2)
    out['fisher_short'] = float(fisher_pair(KAPPA_TRUE, 1e-4) * KAPPA_TRUE ** 2)
    return out


def main():
    t0 = time.time()
    rng = np.random.default_rng(2026)
    R = {}
    R['setup'] = dict(T=T_SEASON, dt=DT, mu=MU, sd=SD, limit=LIMIT, z0=Z0, kappa_true=KAPPA_TRUE, years=YEARS,
                      designs=DESIGNS, truth2=TRUTH2, lags=LAGS)
    R['checks'] = checks(rng)
    log('checks:', json.dumps(R['checks']))
    R['t37'] = t37(rng)
    log(f"T37: exceedance between samples {R['t37']['p_true']:.3f} against marginal tail {R['t37']['p_marginal']:.4f}; "
        f"curve rises from {R['t37']['curve'][0]:.4f} to {R['t37']['p_at_max']:.3f}, min increment "
        f"{R['t37']['min_increment']:.2e}")
    tq = time.time()
    P = exceed_table(KF, KS, WG, ZT, 1500 if QUICK else 4000, rng)
    log(f'table {P.shape} in {time.time() - tq:.0f} s')
    interp = Interp(P)
    G = eval_grid()
    np.savez(os.path.join(RES, 'shtegu_table.npz'), P=P, KF=KF, KS=KS, WG=WG, ZT=ZT)
    R['t38'] = t38(interp, G, rng)
    R['t39'] = t39(interp, G, rng)
    R['t40'] = t40(rng)
    R['time_s'] = time.time() - t0
    with open(os.path.join(RES, 'shtegu.json'), 'w') as fh:
        json.dump(R, fh, indent=1)
    with open(os.path.join(RES, 'shtegu_log.txt'), 'w') as fh:
        fh.write('\n'.join(LOG) + '\n')
    log(f'done in {R["time_s"]:.0f} s')


if __name__ == '__main__':
    os.makedirs(RES, exist_ok=True)
    main()
