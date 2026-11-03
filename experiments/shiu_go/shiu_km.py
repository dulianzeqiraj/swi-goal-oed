"""SHIU-GO experiment E4: route A in its purest form. The soil-water jump SDE

    ds = -[cE Ep(t) min(1, s/sw) + kL ((s - sfc)+/(sbar - sfc))^bL] dt + sig_s dW + min(a, sbar - s) dN,
    N a Poisson process with seasonal rate lam(t), marks a ~ Exp(abar(t)),

is simulated hourly for ten years and discovered from observations of s itself, in three designs:

  probe      hourly readings, 25% missing at random, noise sd 0.3 mm: Kramers-Moyal coefficients from pairs one
             hour apart. For a jump-diffusion M_n(s) = lim (1/D) E[(ds)^n | s] equals drift + lam E[a] (n = 1),
             sig^2 + lam E[a^2] (n = 2) and lam E[a^n] (n >= 3); with exponential marks lam E[a^n] = lam n! abar^n,
             so abar = M4 / (4 M3) and lam = M3 / (6 abar^3). The drift law is then fitted on pairs without a jump.
  satellite  revisits every 3-6 days, 20% lost to cloud, noise sd 3 mm: the same Kramers-Moyal estimates.
  sat+gauge  the same revisits plus the daily rain gauge: the drift law is fitted by minimising the error of the
             physics forecast of s at the next revisit (the forecast principle of Krach, Nubel & Teichmann, SPA 2026,
             restricted to the bucket family), integrating the bucket over the gap with the gauge rain.

usage: python shiu_km.py   (writes res/shiu_km.json)"""
import json
import os
import sys

import numpy as np
from numba import njit
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shiu_model as SM  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TRUE_S = dict(cE=1.0, sw=120.0, sfc=130.0, kL=25.0, bL=3.0, sig_s=1.0, sbar=200.0)
YEARS = 10
HPD = 24


@njit(cache=True)
def simulate_hourly(lam_h, abar_h, Ep_h, u_ev, u_amt, w, cE, sw, sfc, kL, bL, sig_s, sbar, s0):
    n = lam_h.shape[0]
    s = s0
    S = np.empty(n); J = np.zeros(n)
    dt = 1.0 / 24.0
    for i in range(n):
        # rain events in this hour (Poisson thinning by uniform draws, at most 3 per hour)
        k = 0
        p0 = np.exp(-lam_h[i] * dt)
        c = p0; p = p0
        while u_ev[i] > c and k < 3:
            k += 1
            p *= lam_h[i] * dt / k
            c += p
        for j in range(k):
            a = -abar_h[i] * np.log(u_amt[i, j])
            inc = min(a, sbar - s)
            s += inc
            J[i] += inc
        ex = (s - sfc) / (sbar - sfc)
        L = kL * ex ** bL if ex > 0 else 0.0
        et = cE * Ep_h[i] * min(1.0, s / sw)
        s += -(et + L) * dt + sig_s * np.sqrt(dt) * w[i]
        if s < 0.0:
            s = 0.0
        if s > sbar:
            s = sbar
        S[i] = s
    return S, J


def truth(seed=7):
    rng = np.random.default_rng(seed)
    n = YEARS * 365 * HPD
    th = (np.arange(n) + 0.5) / HPD
    lam, abar = SM.rain_rates(th)
    Ep = SM.pet(th)
    S, J = simulate_hourly(lam, abar, Ep, rng.random(n), rng.random((n, 3)), rng.standard_normal(n),
                           TRUE_S['cE'], TRUE_S['sw'], TRUE_S['sfc'], TRUE_S['kL'], TRUE_S['bL'], TRUE_S['sig_s'],
                           TRUE_S['sbar'], 100.0)
    return dict(th=th, S=S, J=J, lam=lam, abar=abar, Ep=Ep, rng=rng)


def km_jumps(s0, ds, dt, month, smax=100.0):
    """Monthly lam and abar from the third and fourth Kramers-Moyal coefficients, pairs with s0 < smax."""
    out = []
    for mth in range(12):
        w = (month == mth) & (s0 < smax)
        M3 = np.mean(ds[w] ** 3) / dt
        M4 = np.mean(ds[w] ** 4) / dt
        ab = M4 / (4 * M3) if M3 > 0 else np.nan
        lam = M3 / (6 * ab ** 3) if M3 > 0 else np.nan
        out.append((lam, ab, int(w.sum())))
    return out


def drift_model(p, s, Ep):
    ex = np.clip((s - p['sfc']) / (TRUE_S['sbar'] - p['sfc']), 0, None)
    return -(p['cE'] * Ep * np.minimum(1.0, s / p['sw']) + p['kL'] * ex ** p['bL'])


def unpack(u):
    return dict(cE=np.exp(u[0]), sw=60 + 120 / (1 + np.exp(-u[1])), sfc=100 + 90 / (1 + np.exp(-u[2])),
                kL=np.exp(u[3]), bL=1 + np.exp(u[4]))


U0 = [np.log(0.7), 0.0, 0.0, np.log(10.0), np.log(1.0)]


def fit_drift_pairs(s0, ds, dt, Ep0):
    """Least squares of ds/dt on the drift law over pairs without a jump."""
    def f(u):
        return np.mean((ds / dt - drift_model(unpack(u), s0, Ep0)) ** 2)
    o = minimize(f, U0, method='Nelder-Mead', options=dict(maxiter=4000, xatol=1e-6, fatol=1e-10, adaptive=True))
    return unpack(o.x)


@njit(cache=True)
def bucket_forecast(s_start, day0, day1, Pd, Epd, cE, sw, sfc, kL, bL, sbar, nsub):
    s = s_start
    h = 1.0 / nsub
    for d in range(day0, day1):
        s += min(Pd[d], sbar - s)
        for j in range(nsub):
            ex = (s - sfc) / (sbar - sfc)
            L = kL * ex ** bL if ex > 0 else 0.0
            et = cE * Epd[d] * min(1.0, s / sw)
            s -= (et + L) * h
            if s < 0:
                s = 0.0
    return s


def main():
    T = truth()
    S, J, th = T['S'], T['J'], T['th']
    rng = T['rng']
    dt = 1.0 / HPD
    month = (((th % 365.0) // (365.0 / 12)).astype(int)).clip(0, 11)
    res = dict(true=TRUE_S)
    # monthly truth of the jump law
    res['true_month'] = [(float(T['lam'][month == m].mean()), float(T['abar'][month == m].mean())) for m in range(12)]

    # --- probe: hourly, 25% missing, noise 0.3 mm
    keep = rng.random(len(S)) > 0.25
    y = S + 0.3 * rng.standard_normal(len(S))
    i = np.where(keep[:-1] & keep[1:])[0]
    s0, ds, Ep0, m0 = y[i], y[i + 1] - y[i], T['Ep'][i], month[i]
    THR = 2.0                                   # a jump: an hourly rise above 2 mm (pair noise sd 0.42 mm)
    jump = ds > THR
    # jump law from the detected jumps: exponential marks are memoryless above the threshold
    est = []
    for mth in range(12):
        w = m0 == mth
        nj = int((jump & w).sum())
        dry = jump & w & (s0 < 150.0)            # marks not truncated by saturation (sbar - s0 > 50 mm)
        ab = float(np.mean(ds[dry] - THR)) if dry.sum() > 0 else np.nan
        rate = nj / (w.sum() * dt)
        est.append((float(rate * np.exp(THR / ab)) if nj > 0 else np.nan, ab, nj))
    res['probe_jumps'] = est
    # Kramers-Moyal check on two seasons (pairs with s0 < 150 mm, little truncation at sbar)
    km = {}
    for name, months in (('winter', (11, 0, 1, 2)), ('summer', (5, 6, 7, 8))):
        w = np.isin(m0, months) & (s0 < 150.0)
        M3 = float(np.mean(ds[w] ** 3) / dt); M4 = float(np.mean(ds[w] ** 4) / dt)
        ab = M4 / (4 * M3); lam = M3 / (6 * ab ** 3)
        wt = np.isin(month, months)
        km[name] = dict(M3=M3, M4=M4, lam_km=lam, abar_km=ab, lam_true=float(T['lam'][wt].mean()),
                        abar_true=float(T['abar'][wt].mean()), n=int(w.sum()))
    res['probe_km'] = km
    nojump = np.abs(ds) < THR
    pdrift = fit_drift_pairs(s0[nojump], ds[nojump], dt, Ep0[nojump])
    res['probe_drift'] = {k: float(v) for k, v in pdrift.items()}
    M2 = np.mean(ds[nojump] ** 2) / dt
    res['probe_sig_s'] = float(np.sqrt(max(M2 - 2 * 0.3 ** 2 / dt, 0.0)))

    # --- satellite: revisits 3-6 days, 20% cloud, noise 3 mm
    days = []
    d = 2
    while d < YEARS * 365 - 1:
        if rng.random() > 0.2:
            days.append(d)
        d += int(rng.integers(3, 7))
    days = np.array(days)
    hrs = days * HPD + 12
    ys = S[hrs] + 3.0 * rng.standard_normal(len(hrs))
    gap = np.diff(days).astype(float)
    s0s, dss = ys[:-1], np.diff(ys)
    mths = month[hrs[:-1]]
    kms = []
    for m in range(12):
        w = (mths == m) & (s0s < 100.0)
        M3 = np.mean(dss[w] ** 3 / gap[w]); M4 = np.mean(dss[w] ** 4 / gap[w])
        ab = M4 / (4 * M3) if M3 > 0 else np.nan
        lam = M3 / (6 * ab ** 3) if (M3 > 0 and ab > 0) else np.nan
        kms.append((float(lam), float(ab), int(w.sum())))
    res['sat_km'] = kms
    res['sat_n'] = int(len(days))

    # --- satellite + daily rain gauge: forecast-error fit of the drift law
    Pd = np.add.reduceat(J, np.arange(0, len(J), HPD))           # daily totals of what entered the soil
    Pd = Pd + 0.0
    Epd = SM.pet(np.arange(YEARS * 365) + 0.5)

    def ferr(u):
        p = unpack(u)
        e = 0.0
        for k in range(len(days) - 1):
            sf = bucket_forecast(ys[k], days[k] + 1, days[k + 1] + 1, Pd, Epd, p['cE'], p['sw'], p['sfc'], p['kL'],
                                 p['bL'], TRUE_S['sbar'], 6)
            e += (ys[k + 1] - sf) ** 2
        return e / (len(days) - 1)
    o = minimize(ferr, U0, method='Nelder-Mead', options=dict(maxiter=3000, xatol=1e-5, fatol=1e-8, adaptive=True))
    res['satgauge_drift'] = {k: float(v) for k, v in unpack(o.x).items()}
    res['satgauge_rmse'] = float(np.sqrt(o.fun))
    pt = dict(cE=TRUE_S['cE'], sw=TRUE_S['sw'], sfc=TRUE_S['sfc'], kL=TRUE_S['kL'], bL=TRUE_S['bL'])
    res['satgauge_rmse_true'] = float(np.sqrt(ferr([np.log(pt['cE']), -np.log(120 / (pt['sw'] - 60) - 1),
                                                     -np.log(90 / (pt['sfc'] - 100) - 1), np.log(pt['kL']),
                                                     np.log(pt['bL'] - 1)])))

    # drift error on a common grid (mean absolute error of the drift function, mm/d), summer and winter PET
    sg = np.linspace(20, 195, 60)
    for key in ('probe_drift', 'satgauge_drift'):
        p = res[key]
        errs = [float(np.mean(np.abs(drift_model(p, sg, ep) - drift_model(pt, sg, ep)))) for ep in (0.6, 5.0)]
        res[key + '_mae'] = errs
    with open(os.path.join(HERE, 'res', 'shiu_km.json'), 'w') as fh:
        json.dump(res, fh)
    # log
    print('true monthly (lam, abar):', [(round(a, 3), round(b, 1)) for a, b in res['true_month']])
    print('probe jumps (lam, abar, n):', [(round(a, 3), round(b, 1), c) for a, b, c in res['probe_jumps']])
    print('probe KM check:', {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in res['probe_km'].items()})
    print('sat   KM  (lam, abar, n):', [(round(a, 3), round(b, 1), c) for a, b, c in res['sat_km']])
    print('probe drift', {k: round(v, 2) for k, v in res['probe_drift'].items()}, 'mae', res['probe_drift_mae'],
          'sig_s', round(res['probe_sig_s'], 2))
    print('sat+gauge drift', {k: round(v, 2) for k, v in res['satgauge_drift'].items()}, 'mae', res['satgauge_drift_mae'],
          'rmse', round(res['satgauge_rmse'], 2), 'rmse at truth', round(res['satgauge_rmse_true'], 2))


if __name__ == '__main__':
    main()
