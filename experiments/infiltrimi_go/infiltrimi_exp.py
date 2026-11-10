"""INFILTRIMI-GO: can rainfall, infiltration and soil moisture be recovered from groundwater levels?

Synthetic three-year daily record for a Mediterranean coastal plain (wet winters, dry summers). The chain is
    gauge rain Pg --(undercatch m)--> true rain P --(infiltration capacity Ic)--> infiltration I
    --(soil store theta, field capacity theta_fc, evapotranspiration k_et * PET * min(1, theta/theta_fc))-->
    drainage below the root zone (time constant tau_s) = recharge R --(specific yield Sy, drainage tau_a)--> head h.
Unknown: m, k_et, Ic, theta_fc, tau_s, phi0 (initial soil wetness), Sy, tau_a, h_b, h_0.

Checks:
  1. Water-table fluctuation in stochastic form (Proposition 1): daily and monthly recharge from heads when Sy is known.
  2. Exact scale invariance (Proposition 2): Jacobian of the heads, its null direction, and what one anchor does.
  3. Bayesian inversion by differential-evolution MCMC under five data scenarios (heads and gauge; plus a pumping
     test; plus a soil-moisture probe; plus a chloride mass balance; all) and a variant without storms above Ic
     (Proposition 4).

usage: python infiltrimi_exp.py OUT.json      (numpy only; a few minutes)"""
import json
import sys
import time

import numpy as np
from scipy.optimize import least_squares

RNG = np.random.default_rng(20261111)
N = 1096                                    # days, from 1 September
YEARS = N / 365.25
T_DAY = np.arange(N)
DOY = (T_DAY + 244) % 365                   # day of year (1 September = 244)
SIG_H = 0.01                                # head logger noise (m)
SIG_TH = 6.0                                # soil-moisture probe noise (mm of water in the root zone)

NAMES = ['m', 'k_et', 'Ic', 'theta_fc', 'tau_s', 'phi0', 'Sy', 'tau_a', 'h_b', 'h_0']
LOG = np.array([1, 1, 1, 1, 1, 0, 1, 1, 0, 0], bool)
LO = np.array([np.log(0.5), np.log(0.3), np.log(5.0), np.log(20.0), np.log(1.0), 0.01, np.log(0.03), np.log(20.0), -2.0, 0.0])
HI = np.array([np.log(2.0), np.log(1.6), np.log(300.0), np.log(500.0), np.log(60.0), 0.99, np.log(0.4), np.log(1000.0), 4.0, 3.0])
TRUE = dict(m=1.12, k_et=0.9, Ic=30.0, theta_fc=150.0, tau_s=8.0, phi0=0.25, Sy=0.2, tau_a=150.0, h_b=0.8, h_0=1.4)
SCALE = np.array([1, 1, 1, 1, 0, 0, 1, 0, 0, 0], float)     # parameters that carry millimetres (Proposition 2)


def to_z(p):
    v = np.array([p[k] for k in NAMES], float)
    return np.where(LOG, np.log(v), v)


def from_z(z):
    return np.where(LOG[None, :], np.exp(z), z)


def climate(clip=None):
    s = 0.5 * (1 + np.cos(2 * np.pi * (DOY - 350) / 365))           # wetness of the season, peak mid-December
    p_wet = 0.06 + 0.40 * s
    mean_amt = 5 + 9 * s
    wet = RNG.random(N) < p_wet
    amt = RNG.gamma(0.75, mean_amt / 0.75)
    P = np.where(wet, amt, 0.0)
    if clip is not None:
        P = np.minimum(P, clip)
    PET = 0.7 + 4.3 * 0.5 * (1 - np.cos(2 * np.pi * (DOY - 15) / 365))   # mm/day, 0.7 in January, 5.0 in July
    return P, PET


def forward(Z, Pg, PET, th_obs=None, keep=False):
    """Vectorised over K parameter sets (rows of Z). Returns heads (N x K), total recharge (K), soil SSE (K)."""
    p = from_z(np.atleast_2d(Z))
    m, ket, Ic, thfc, taus, phi0, Sy, taua, hb, h0 = p.T
    K = p.shape[0]
    th = phi0 * thfc
    h = h0.copy()
    H = np.empty((N, K))
    sumR = np.zeros(K); sse = np.zeros(K)
    out = dict(theta=np.empty((N, K)), R=np.empty((N, K)), ET=np.zeros(K), RO=np.zeros(K)) if keep else None
    for i in range(N):
        P = m * Pg[i]
        inf = np.minimum(P, Ic)
        th = th + inf
        et = ket * PET[i] * np.minimum(1.0, th / thfc)
        et = np.minimum(et, th)
        th = th - et
        d = np.maximum(th - thfc, 0.0) / taus
        th = th - d
        h = h + d / (1000.0 * Sy) - (h - hb) / taua
        H[i] = h
        sumR += d
        if th_obs is not None:
            sse += (th - th_obs[i])**2
        if keep:
            out['theta'][i] = th; out['R'][i] = d; out['ET'] += et; out['RO'] += P - inf
    return H, sumR, sse, out


class Scenario:
    def __init__(self, name, Pg, PET, h_obs, sy=None, th_obs=None, cmb=None):
        self.name, self.Pg, self.PET, self.h_obs = name, Pg, PET, h_obs
        self.sy, self.th_obs, self.cmb = sy, th_obs, cmb

    def logpost(self, Z):
        inside = np.all((Z >= LO) & (Z <= HI), axis=1)
        lp = np.full(Z.shape[0], -np.inf)
        if not inside.any():
            return lp
        Zi = Z[inside]
        H, sumR, sse, _ = forward(Zi, self.Pg, self.PET, th_obs=self.th_obs)
        ll = -0.5 * (((H - self.h_obs[:, None]) / SIG_H)**2).sum(axis=0)
        if self.sy is not None:                       # pumping test: Sy within 10 %
            ll += -0.5 * ((Zi[:, 6] - np.log(self.sy)) / 0.10)**2
        if self.th_obs is not None:                   # soil-moisture probe
            ll += -0.5 * sse / SIG_TH**2
        if self.cmb is not None:                      # chloride mass balance: mean recharge within 20 %
            ll += -0.5 * ((np.log(sumR / YEARS) - np.log(self.cmb)) / 0.20)**2
        lp[inside] = ll
        return lp


def residuals(Z, sc):
    """Weighted residuals (K x M) of heads, pumping test, soil probe and chloride balance."""
    H, sumR, _, out = forward(Z, sc.Pg, sc.PET, keep=True)
    parts = [((H - sc.h_obs[:, None]) / SIG_H).T]
    if sc.sy is not None:
        parts.append(((Z[:, 6] - np.log(sc.sy)) / 0.10)[:, None])
    if sc.th_obs is not None:
        parts.append(((out['theta'] - sc.th_obs[:, None]) / SIG_TH).T)
    if sc.cmb is not None:
        parts.append(((np.log(sumR / YEARS) - np.log(sc.cmb)) / 0.20)[:, None])
    return np.concatenate(parts, axis=1)


def fit_map(sc, n_starts=8, seed=0):
    """Most probable parameters by Levenberg-Marquardt-type least squares (bounded) from several starts; the
    Jacobian is computed in one vectorised forward run."""
    rng = np.random.default_rng(seed)
    d = len(NAMES); hs = 1e-6
    fun = lambda z: residuals(z[None, :], sc)[0]

    def jac(z):
        Zs = np.repeat(z[None, :], 2 * d, axis=0)
        for j in range(d):
            Zs[2 * j, j] += hs; Zs[2 * j + 1, j] -= hs
        Rr = residuals(Zs, sc)
        return np.stack([(Rr[2 * j] - Rr[2 * j + 1]) / (2 * hs) for j in range(d)], axis=1)

    best = None
    pad = 1e-6 * (HI - LO)
    for k in range(n_starts):
        z0 = LO + (HI - LO) * (0.15 + 0.7 * rng.random(d))
        r = least_squares(fun, z0, jac=jac, bounds=(LO + pad, HI - pad), method='trf', x_scale='jac', max_nfev=300)
        if best is None or r.cost < best.cost:
            best = r
    return best.x, best.jac, float(best.cost)


def demc(sc, K=64, iters=2500, keep_from=1000, thin=5, seed=1):
    """Differential-evolution MCMC (ter Braak, 2006) in two halves: each half proposes moves from differences of
    the other half's current states, which keeps detailed balance for the whole population. Chains start around
    the most probable parameters with the Laplace covariance. Every fifth iteration is a symmetric move along the
    scale direction of Proposition 2, a valid Metropolis kernel that explores the ridge when the data leave it flat."""
    rng = np.random.default_rng(seed)
    d = len(NAMES)
    zmap, J, cost = fit_map(sc, seed=seed)
    F = J.T @ J
    w, V = np.linalg.eigh(F)
    sd = np.where(w > 1e-6, 1 / np.sqrt(np.maximum(w, 1e-12)), 0.0)
    Z = zmap + (rng.standard_normal((K, d)) * sd) @ V.T
    Z = np.clip(Z, LO + 1e-9, HI - 1e-9)
    lp = sc.logpost(Z)
    halves = [np.arange(0, K, 2), np.arange(1, K, 2)]
    gam = 2.38 / np.sqrt(2 * d)
    e = SCALE / np.linalg.norm(SCALE)
    samples, acc, nprop = [], 0, 0
    for it in range(iters):
        for a, b in (halves, halves[::-1]):
            if it % 5 == 4:
                prop = Z[a] + rng.normal(0, 0.5, (len(a), 1)) * e[None, :]
            else:
                r1 = rng.choice(b, len(a)); r2 = rng.choice(b, len(a))
                g = 1.0 if it % 10 == 0 else gam
                prop = Z[a] + g * (Z[r1] - Z[r2]) + 1e-6 * rng.standard_normal((len(a), d))
            lpp = sc.logpost(prop)
            ok = np.log(rng.random(len(a))) < lpp - lp[a]
            Z[a[ok]] = prop[ok]; lp[a[ok]] = lpp[ok]
            if it >= keep_from and it % 5 != 4:
                acc += ok.sum(); nprop += len(a)
        if it >= keep_from and (it - keep_from) % thin == 0:
            samples.append(Z.copy())
    S = np.array(samples)
    W = S.var(axis=0, ddof=1).mean(axis=0); Bv = S.mean(axis=0).var(axis=0, ddof=1) * S.shape[0]
    n = S.shape[0]
    rhat = np.sqrt(((n - 1) / n * W + Bv / n) / W)
    return S.reshape(-1, d), dict(acceptance=float(acc / max(nprop, 1)), rhat_max=float(rhat.max()),
                                  rhat=dict(zip(NAMES, map(float, rhat))), map_cost=cost,
                                  map=dict(zip(NAMES, map(float, from_z(zmap[None, :])[0]))))


def summary(Zs, sc, true_q, nsub=1500, seed=2):
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(Zs), min(nsub, len(Zs)), replace=False)
    Zsub = Zs[idx]
    _, sumR, _, out = forward(Zsub, sc.Pg, sc.PET, keep=True)
    p = from_z(Zsub)
    Ptot = p[:, 0] * sc.Pg.sum()
    q = dict(rain_mm_yr=Ptot / YEARS, recharge_mm_yr=sumR / YEARS, R_over_P=sumR / Ptot, ET_over_P=out['ET'] / Ptot,
             runoff_over_P=out['RO'] / Ptot, Sy=p[:, 6], theta_fc=p[:, 3], Ic=p[:, 2], tau_s=p[:, 4], m=p[:, 0],
             k_et=p[:, 1])
    res = {}
    for k, v in q.items():
        lo, med, hi = np.quantile(v, [0.05, 0.5, 0.95])
        res[k] = dict(q05=float(lo), median=float(med), q95=float(hi), truth=float(true_q[k]),
                      rel_width=float((hi - lo) / true_q[k]))
    th = out['theta']; R = out['R']
    bands = dict(theta=np.quantile(th, [0.05, 0.5, 0.95], axis=1).tolist(),
                 wet=np.quantile(th / p[:, 3], [0.05, 0.5, 0.95], axis=1).tolist(),
                 R=np.quantile(R, [0.05, 0.5, 0.95], axis=1).tolist())
    mon = monthly(R)
    bands['R_month'] = np.quantile(mon, [0.05, 0.5, 0.95], axis=1).tolist()
    return res, bands, dict(m=p[:, 0].tolist()[:800], Sy=p[:, 6].tolist()[:800], Ic=p[:, 2].tolist()[:800],
                            R_over_P=(sumR / Ptot).tolist()[:800])


def monthly(R):
    edges = list(range(0, N, 30)) + [N]
    return np.array([R[a:b].sum(axis=0) for a, b in zip(edges[:-1], edges[1:])])


def truth_quantities(Pg, PET):
    z = to_z(TRUE)[None, :]
    H, sumR, _, out = forward(z, Pg, PET, keep=True)
    Ptot = TRUE['m'] * Pg.sum()
    q = dict(rain_mm_yr=Ptot / YEARS, recharge_mm_yr=sumR[0] / YEARS, R_over_P=sumR[0] / Ptot,
             ET_over_P=out['ET'][0] / Ptot, runoff_over_P=out['RO'][0] / Ptot, Sy=TRUE['Sy'],
             theta_fc=TRUE['theta_fc'], Ic=TRUE['Ic'], tau_s=TRUE['tau_s'], m=TRUE['m'], k_et=TRUE['k_et'])
    return q, H[:, 0], out['theta'][:, 0], out['R'][:, 0]


def check_wtf(h_obs, R_true):
    """Proposition 1: recharge from the heads with Sy, tau_a and h_b known (water-table fluctuation method)."""
    Sy, taua, hb = TRUE['Sy'], TRUE['tau_a'], TRUE['h_b']
    h_prev = np.r_[TRUE['h_0'], h_obs[:-1]]
    Rhat = 1000 * Sy * (h_obs - h_prev + (h_prev - hb) / taua)
    Rhat[0] = np.nan
    e = Rhat[1:] - R_true[1:]
    mon_t = monthly(R_true[1:, None])[:, 0]; mon_h = monthly(Rhat[1:, None])[:, 0]
    return dict(daily_rmse_mm=float(np.sqrt((e**2).mean())), predicted_daily_sd_mm=float(1000 * Sy * SIG_H * np.sqrt(2)),
                monthly_rmse_mm=float(np.sqrt(((mon_h - mon_t)**2).mean())), mean_monthly_recharge_mm=float(mon_t.mean()),
                Rhat=Rhat.tolist())


def jacobian(Pg, PET):
    """Proposition 2: Jacobian of the heads with respect to the sampling parameters at the truth, its null direction,
    and the smallest singular value once one anchor is added (pumping test, soil probe or chloride balance)."""
    z = to_z(TRUE); d = len(z); hstep = 1e-5
    Zs = np.repeat(z[None, :], 2 * d, axis=0)
    for j in range(d):
        Zs[2 * j, j] += hstep; Zs[2 * j + 1, j] -= hstep
    H, sumR, _, out = forward(Zs, Pg, PET, keep=True)
    cd = lambda A: np.stack([(A[:, 2 * j] - A[:, 2 * j + 1]) / (2 * hstep) for j in range(d)], axis=1)
    J = cd(H) / SIG_H
    sv, V = np.linalg.svd(J, full_matrices=False)[1:]
    v_null = V[-1]
    e = SCALE / np.linalg.norm(SCALE)
    Fi = J.T @ J
    Jth = cd(out['theta']) / SIG_TH
    g = np.array([(np.log(sumR[2 * j]) - np.log(sumR[2 * j + 1])) / (2 * hstep) for j in range(d)])
    anchors = {'pumping test': np.diag(np.eye(d)[6] / 0.10**2), 'soil probe': Jth.T @ Jth,
               'chloride balance': np.outer(g, g) / 0.20**2}
    out_ = dict(singular_values=sv.tolist(), null_vector=dict(zip(NAMES, map(float, v_null))),
                cos_with_scale_dir=float(abs(v_null @ e)))
    for name, F in anchors.items():
        out_['smallest_sv_with_' + name.replace(' ', '_')] = float(np.sqrt(max(np.linalg.eigvalsh(Fi + F)[0], 0.0)))
    return out_


def main(outp):
    t0 = time.time()
    P_true, PET = climate()
    Pg = P_true / TRUE['m']
    tq, h_true, th_true, R_true = truth_quantities(Pg, PET)
    h_obs = h_true + SIG_H * RNG.standard_normal(N)
    th_obs = th_true + SIG_TH * RNG.standard_normal(N)
    cmb = tq['recharge_mm_yr']
    res = dict(setup=dict(days=N, truth=TRUE, sigma_h=SIG_H, sigma_theta=SIG_TH,
                          gauge_mm_yr=float(Pg.sum() / YEARS), true_rain_mm_yr=float(P_true.sum() / YEARS),
                          storm_days_above_Ic=int((P_true > TRUE['Ic']).sum()),
                          days_below_field_capacity=float((th_true < TRUE['theta_fc'] - 1e-9).mean())),
               truth=tq, series=dict(Pg=Pg.tolist(), P=P_true.tolist(), PET=PET.tolist(), h_obs=h_obs.tolist(),
                                     h_true=h_true.tolist(), theta=th_true.tolist(), R=R_true.tolist(),
                                     th_obs=th_obs.tolist()))
    res['wtf'] = check_wtf(h_obs, R_true)
    res['jacobian'] = jacobian(Pg, PET)
    scen = [Scenario('S0 heads and gauge', Pg, PET, h_obs),
            Scenario('S1 + pumping test', Pg, PET, h_obs, sy=TRUE['Sy']),
            Scenario('S2 + soil-moisture probe', Pg, PET, h_obs, th_obs=th_obs),
            Scenario('S3 + chloride mass balance', Pg, PET, h_obs, cmb=cmb),
            Scenario('S4 all', Pg, PET, h_obs, sy=TRUE['Sy'], th_obs=th_obs, cmb=cmb)]
    res['scenarios'] = {}
    for i, sc in enumerate(scen):
        Zs, diag = demc(sc, seed=10 + i)
        s, bands, pts = summary(Zs, sc, tq)
        res['scenarios'][sc.name] = dict(diag=diag, summary=s, bands=bands, points=pts)
        print(sc.name, 'done', round(time.time() - t0), 's', diag['rhat_max'], diag['acceptance'], flush=True)
    # Proposition 4: the same climate without storms above Ic, anchored by pumping test and probe
    P2, _ = climate(clip=0.9 * TRUE['Ic'])
    Pg2 = P2 / TRUE['m']
    tq2, h2, th2, _ = truth_quantities(Pg2, PET)
    sc2 = Scenario('no storms above Ic', Pg2, PET, h2 + SIG_H * RNG.standard_normal(N), sy=TRUE['Sy'],
                   th_obs=th2 + SIG_TH * RNG.standard_normal(N))
    Zs, diag = demc(sc2, seed=99)
    s, _, pts = summary(Zs, sc2, tq2)
    res['no_storms'] = dict(diag=diag, summary=s, points=pts, storm_days_above_Ic=int((P2 > TRUE['Ic']).sum()))
    s4 = res['scenarios']['S4 all']['points']
    res['with_storms_Ic'] = s4['Ic']
    res['runtime_s'] = round(time.time() - t0)
    with open(outp, 'w') as fh:
        json.dump(res, fh)
    print('saved', outp, res['runtime_s'], 's')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'infiltrimi_results.json')
