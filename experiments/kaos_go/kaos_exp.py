"""Analysis of the KAOS-GO pore-scale experiment.  Reads the runs written by kaos_run.py and kaos_rev.py and writes
res/kaos.json (every number of the review), res/kaos_fields.npz (fields of three levels for the figures) and
res/kaos_series.npz (flux series of the long runs).

usage: python kaos_exp.py RUNS_DIR      (RUNS_DIR holds prod/ and conv/)
"""
import glob
import json
import os
import sys
from math import ceil

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
ALPHA = 0.10
Z90 = 1.6448536269514722


def load(path):
    z = np.load(path)
    return z, json.loads(str(z['meta']))


def batch_se(x, nb=8):
    """standard error of the mean of a correlated series by batch means."""
    n = len(x) // nb
    if n < 2:
        return float('nan')
    b = x[:n * nb].reshape(nb, n).mean(1)
    return float(b.std(ddof=1) / np.sqrt(nb))


def long_run_variance(x, max_lag, c=5.0):
    """long-run variance sigma_inf^2 = sum of the autocovariance over all lags (Green-Kubo form), with the automatic
    window of Sokal: the sum is cut at the first lag M with M >= c * tau(M), tau the integrated correlation time in
    samples.  Returns (sigma_inf^2, variance, M)."""
    acov = autocov(x, max_lag)
    tau = 0.5 + np.cumsum(acov[1:]) / acov[0]
    m = np.arange(1, len(acov))
    ok = np.where(m >= c * tau)[0]
    k = int(ok[0]) if len(ok) else len(tau) - 1
    return float(max(2 * tau[k], 1e-12) * acov[0]), float(acov[0]), int(m[k])


def autocov(x, max_lag):
    x = x - x.mean()
    n = len(x)
    f = np.fft.rfft(x, 2 * n)
    return np.fft.irfft(f * np.conj(f))[:max_lag] / n


def window_mean_variance(acov, M, per):
    """variance of the mean of per consecutive samples of a stationary series with autocovariance acov, cut at lag M:
    (C0 + 2 sum_{k<per} (1 - k/per) C_k) / per.  For per much larger than the correlation time it tends to
    sigma_inf^2 / per (Proposition 2)."""
    k = np.arange(1, min(per, M + 1))
    return float((acov[0] + 2 * np.sum((1 - k / per) * acov[k])) / per)


def spectrum_summary(ts, dt, seg_transits=80.0):
    """Welch spectrum of the flux (Hann window, segments of seg_transits): the frequency of the strongest line in cycles
    per transit time, the share of the variance within two bins of it, and the share at periods longer than 20 transit
    times.  A periodic flow has peak_share near 1."""
    n = int(round(seg_transits / dt)); k = len(ts) // n
    if k < 1:
        return {}
    x = ts[:k * n].reshape(k, n); x = x - x.mean(1, keepdims=True)
    S = (np.abs(np.fft.rfft(x * np.hanning(n), axis=1)) ** 2).mean(0)
    f = np.fft.rfftfreq(n, dt)
    i = int(np.argmax(S))
    return dict(f_peak=float(f[i]), peak_share=float(S[max(i - 2, 0):i + 3].sum() / S.sum()),
                slow_share=float(S[f < 0.05].sum() / S.sum()))


def level_record(path, a_ref=None):
    z, m = load(path)
    a, nu, g, phi_ = m['a'], m['nu'], m['g'], m['porosity']
    U = m['U']
    T = 2 * a * phi_ / U                                   # pore transit time, steps
    rec = dict(file=os.path.basename(path), nu=nu, g=g, a=a, L=m['L'], U=U, Re=m['Re'], Kstar=nu * U / (g * a * a),
               porosity=phi_, transit=T, budget=m['phi'] / (g * U), mean_share=m['phi_mean_flow'] / (g * U),
               fluct_share=(m['phi'] - m['phi_mean_flow']) / (g * U), tke_ratio=m['tke'] / m['ke_mean_flow'],
               U_cv=m['U_std'] / U, umax=m['umax'], samp_transits=m['samp'] / T, spin_transits=m['spin'] / T)
    if 'lyap_rates' in z.files:
        r = z['lyap_rates']
        half = r[len(r) // 2:]
        rec.update(lyap_T=float(half.mean() * T), lyap_T_se=batch_se(half) * T, lyap_transits=m['samp'] and len(r) * 200 / T)
    if 'tke' in z.files:
        fluid = ~z['solid']
        up2 = (U / phi_) ** 2
        tk = z['tke'][fluid]
        rec['unsteady_share'] = float((tk > 0.10 * 0.5 * up2).mean())       # local fluctuation energy above 10% of U_p^2/2
        if tk.sum() > 0:
            e = np.sort(tk)[::-1]
            rec['half_tke_area'] = float((np.cumsum(e) < 0.5 * e.sum()).mean())  # share of the pore space with half of it
            # per grain: mean fluctuation energy of the fluid nearest to each grain (periodic Voronoi cells)
            pts = z['pts']; L = m['L']
            yy, xx = np.meshgrid(np.arange(L) + 0.0, np.arange(L) + 0.0, indexing='ij')
            d2 = np.full((len(pts), L, L), np.inf)
            for k, (cx, cy) in enumerate(pts):
                dx = np.abs(xx - cx); dx = np.minimum(dx, L - dx)
                dy = np.abs(yy - cy); dy = np.minimum(dy, L - dy)
                d2[k] = dx * dx + dy * dy
            own = d2.argmin(0)
            g = np.array([z['tke'][fluid & (own == k)].mean() for k in range(len(pts))]) / (0.5 * up2)
            rec['grain_tke'] = [float(v) for v in g]
            rec['grains_unsteady'] = int((g > 0.05).sum())
        # concentration of the dissipation: share of the fluid area that carries half of it
        d = np.sort(z['phi_field'][fluid])[::-1]
        rec['half_dissipation_area'] = float((np.cumsum(d) < 0.5 * d.sum()).mean())
    ts = z['ts'][:, 0]
    if rec['U_cv'] > 1e-4 and len(ts) > 2000:
        dt = m['every'] / T                                 # sampling interval in transit times
        lrv, var, k = long_run_variance(ts, len(ts) // 4)
        rec.update(tau_int=0.5 * lrv / var * dt, lrv_rel=lrv * dt / U ** 2)   # Var(mean over W transits) = lrv_rel U^2 / W
        rec.update(spectrum_summary(ts, dt))
    return rec


def window_coverage(ts, U, T_steps, every, W, burn_transits, rng=None):
    """Prequential 90% intervals for the mean flux of the next window of W transit times.
    naive: the flux is taken to forget itself after one pore transit time (one independent sample per transit);
    gk: long-run variance from the burn-in; conformal: the gk scale times the conformal quantile of the standardised
    errors of the windows already seen."""
    per = max(int(round(W * T_steps / every)), 1)
    nb = int(round(burn_transits * T_steps / every))
    burn = ts[:nb]
    lrv, var, _ = long_run_variance(burn, len(burn) // 4)
    rest = ts[nb:]
    n = len(rest) // per
    m = rest[:n * per].reshape(n, per).mean(1)
    sd_naive = np.sqrt(var / W)
    sd_gk = np.sqrt(max(lrv, 1e-300) / per)
    mu, cnt = burn.mean(), 1.0 * len(burn)
    hit = dict(naive=[], gk=[], conformal=[])
    scores, qs, side, when = [], [], [], []
    for k in range(n):
        pred = mu
        # the predictor is itself a mean over cnt samples: its variance is added
        f = np.sqrt(1 + per / cnt)
        err = m[k] - pred
        hit['naive'].append(abs(err) <= Z90 * sd_naive * f)
        hit['gk'].append(abs(err) <= Z90 * sd_gk * f)
        if len(scores) >= 9:
            s = np.sort(scores)
            r = ceil((1 - ALPHA) * (len(s) + 1))
            q = s[r - 1] if r <= len(s) else np.inf
            hit['conformal'].append(abs(err) <= q * sd_gk * f)
            qs.append(q); side.append(np.sign(err)); when.append(burn_transits + (k + 0.5) * W)
        scores.append(abs(err) / (sd_gk * f))
        mu = (mu * cnt + m[k] * per) / (cnt + per)
        cnt += per
    return dict(W=W, burn=burn_transits, n=n, sd_rel_window=float(m.std(ddof=1) / U),
                naive=float(np.mean(hit['naive'])), gk=float(np.mean(hit['gk'])),
                conformal=float(np.mean(hit['conformal'])) if hit['conformal'] else None, n_conf=len(hit['conformal']),
                sd_gk_rel=float(sd_gk / U), sd_naive_rel=float(sd_naive / U),
                # width of the conformal interval over that of the interval with the measured correlation
                conf_width=float(np.mean(qs) / Z90) if qs else None, naive_width=float(sd_naive / sd_gk),
                # where the conformal interval misses: above or below the prediction, and in the last 200 transit times
                **miss_summary(hit['conformal'], side, when, burn_transits + n * W))


def miss_summary(hits, side, when, t_end):
    if not hits:
        return {}
    miss = ~np.array(hits, bool); side = np.array(side); late = np.array(when) >= t_end - 200
    return dict(conf_miss=int(miss.sum()), conf_miss_above=int((miss & (side > 0)).sum()), conf_miss_below=int((miss & (side < 0)).sum()),
                conf_miss_late=int((miss & late).sum()), conf_n_late=int(late.sum()),
                conf_miss_early=int((miss & ~late).sum()), conf_n_early=int((~late).sum()))


def fit_laws(Re, F, train):
    """least-squares fits of candidate closures F(Re) on the levels in train (boolean); returns functions."""
    x, y = Re[train], F[train]
    laws = {}
    b = np.sum(x * (y - 1)) / np.sum(x * x); laws['Forchheimer, 1 + b Re'] = lambda r, b=b: 1 + b * r
    c = np.sum(x ** 2 * (y - 1)) / np.sum(x ** 4); laws['weak inertia, 1 + c Re^2'] = lambda r, c=c: 1 + c * r ** 2
    A = np.c_[x, x ** 2]; bc = np.linalg.lstsq(A, y - 1, rcond=None)[0]
    laws['1 + b Re + c Re^2'] = lambda r, bc=bc: 1 + bc[0] * r + bc[1] * r ** 2
    pos = (y > 1.02)
    if pos.sum() >= 2:
        pm = np.polyfit(np.log(x[pos]), np.log(y[pos] - 1), 1)
        laws['power law, 1 + k Re^m'] = lambda r, pm=pm: 1 + np.exp(pm[1]) * r ** pm[0]
    return laws


def main(runs):
    out = {}
    # ---- gates ------------------------------------------------------------------------------------------------------
    gp = os.path.join(runs, 'gates.json')
    if os.path.exists(gp):
        G = json.load(open(gp))
        low = [r for r in G if r['Re'] < 1.0]
        out['gates'] = dict(rows=G, drag_dev_max=float(max(abs(r['k_sim'] / r['k_SA_nominal'] - 1) for r in low)),
                            budget_dev_max=float(max(abs(r['budget_error']) for r in G)),
                            n=len(G))
    # ---- resolution study -------------------------------------------------------------------------------------------
    conv = []
    for p in sorted(glob.glob(os.path.join(runs, 'conv', 'G*_a*.npz'))):
        r = level_record(p)
        r['G'] = int(os.path.basename(p).split('_')[0][1:])
        conv.append(r)
    out['conv'] = conv
    # ---- the sweep --------------------------------------------------------------------------------------------------
    files = sorted(glob.glob(os.path.join(runs, 'prod', 'r_*.npz')))
    files += [p for p in glob.glob(os.path.join(runs, 'conv', 'G*_a18.0.npz'))]
    lev = sorted((level_record(p) for p in files), key=lambda r: r['Re'])
    K0 = lev[0]['Kstar']
    for r in lev:
        r['F'] = K0 / r['Kstar']
        r['F_mean'] = r['F'] * r['mean_share'] / r['budget']       # shares of the measured dissipation
        r['F_fluct'] = r['F'] * r['fluct_share'] / r['budget']
        r['unsteady'] = bool(r['U_cv'] > 1e-4)
        r['chaotic'] = bool(r.get('lyap_T', -1) > 2 * max(r.get('lyap_T_se', 0), 5e-3)) if 'lyap_T' in r else False
    out['levels'] = lev
    out['K0'] = K0
    # control of the Lyapunov measurement: the same twin run at a steady level (perturbations must decay)
    ctl = sorted(glob.glob(os.path.join(runs, 'prod', 'lyapctl_*.npz')))
    if ctl:
        r = level_record(ctl[0])
        out['lyap_control'] = dict(Re=r['Re'], lyap_T=r['lyap_T'], lyap_T_se=r['lyap_T_se'])
    Re = np.array([r['Re'] for r in lev]); F = np.array([r['F'] for r in lev])
    steady = np.array([not r['unsteady'] for r in lev])
    out['onset_unsteady'] = [float(Re[steady].max()), float(Re[~steady].min())] if (~steady).any() else None
    ch = np.array([r['chaotic'] for r in lev])
    out['onset_chaos'] = [float(Re[~ch & ~steady].max()) if (~ch & ~steady).any() else float(Re[steady].max()),
                          float(Re[ch].min())] if ch.any() else None
    # ---- closures: fit on the steady levels, predict the unsteady ones; leave one level out ---------------------------
    cl = {}
    laws = fit_laws(Re, F, steady)
    for name, fn in laws.items():
        e = fn(Re[~steady]) / F[~steady] - 1
        cl[name] = dict(extrapolation_err=[float(v) for v in e], extrapolation_max=float(np.abs(e).max()) if e.size else None)
    loo = {}
    for i in range(1, len(Re)):                                     # the lowest level defines K0
        tr = np.ones(len(Re), bool); tr[i] = False
        for name, fn in fit_laws(Re, F, tr).items():
            loo.setdefault(name, []).append(float(fn(Re[i]) / F[i] - 1))
    for name in loo:
        if name in cl:
            cl[name]['loo_rms'] = float(np.sqrt(np.mean(np.square(loo[name]))))
            cl[name]['loo_max'] = float(np.max(np.abs(loo[name])))
    out['closures'] = cl
    # ---- finite-size study of the Darcy coefficient -------------------------------------------------------------------
    rp = os.path.join(runs, 'prod', 'rev.json')
    if os.path.exists(rp):
        R = json.load(open(rp))
        rows = []
        for s in R['sizes']:
            k = np.array(s['K'])
            rows.append(dict(n=s['n'], m=len(k), mean=float(k.mean()), sd=float(k.std(ddof=1)), cv=float(k.std(ddof=1) / k.mean()),
                             se_mean=float(k.std(ddof=1) / np.sqrt(len(k))), K=[float(v) for v in k],
                             solid=float(np.mean(s['solid']))))
        if len(rows) >= 2:
            sl = np.polyfit(np.log([r['n'] for r in rows]), np.log([r['cv'] for r in rows]), 1)
            out['rev'] = dict(rows=rows, slope=float(sl[0]),
                              bias_small=float(rows[0]['mean'] / rows[-1]['mean'] - 1),
                              bias_small_se=float(np.hypot(rows[0]['se_mean'], rows[-1]['se_mean']) / rows[-1]['mean']))
    # ---- long runs: statistics of window means ------------------------------------------------------------------------
    def long_record(p, coverage=True):
        z, m = load(p)
        ts = z['ts'][:, 0]
        T = 2 * m['a'] * m['porosity'] / m['U']
        dt = m['every'] / T
        lrv, var, k = long_run_variance(ts, len(ts) // 4)
        acov = autocov(ts, len(ts) // 4)
        rec = dict(nu=m['nu'], a=m['a'], Re=m['Re'], U=m['U'], transits=len(ts) * dt, U_cv=float(ts.std() / m['U']),
                   tau_int=float(0.5 * lrv / var * dt), lrv_rel=float(lrv * dt / m['U'] ** 2), sokal_window=float(k * dt),
                   budget=m['phi'] / (m['g'] * m['U']), windows=[], scaling=[])
        # the same estimate from consecutive short records of 200 transit times (what a sweep run sees)
        seg = int(round(200 / dt))
        rec['tau_segments'] = [float(0.5 * a_ / b_ * dt) for a_, b_, _ in
                               (long_run_variance(ts[i * seg:(i + 1) * seg], seg // 4) for i in range(len(ts) // seg))]
        rec['acf'] = [dict(lag=lag, rho=float(acov[int(round(lag / dt))] / acov[0])) for lag in (1, 2, 5, 10, 20, 40, 80, 160)]
        rec.update(spectrum_summary(ts, dt))
        for W in (2.5, 5, 10, 20, 40, 80):
            per = int(round(W / dt)); n = len(ts) // per
            mm = ts[:n * per].reshape(n, per).mean(1)
            zz = (mm - mm.mean()) / mm.std()
            rec['scaling'].append(dict(W=W, n=n, var_rel=float(mm.var(ddof=1) / m['U'] ** 2),
                                       var_pred_rel=window_mean_variance(acov, k, per) / m['U'] ** 2,
                                       skew=float((zz ** 3).mean())))
        # strength of the fluctuations in consecutive stretches of 100 transit times: scatter of the 5-transit means
        p5 = int(round(5 / dt)); n5 = len(ts) // p5
        w5 = ts[:n5 * p5].reshape(n5, p5).mean(1)
        rec['sd5_stretches'] = [float(w5[i * 20:(i + 1) * 20].std(ddof=1) / m['U']) for i in range(n5 // 20)]
        sc = [(s['W'], s['var_rel']) for s in rec['scaling'] if s['W'] >= 10 and s['n'] >= 12]
        rec['scaling_slope'] = float(np.polyfit(np.log([s[0] for s in sc]), np.log([s[1] for s in sc]), 1)[0])
        if coverage:
            for burn in (50, 200):
                for W in (5, 10, 20, 40):
                    rec['windows'].append(window_coverage(ts, m['U'], T, m['every'], W, burn))
        if 'lyap_rates' in z.files:
            rr = z['lyap_rates']; half = rr[len(rr) // 2:]
            rec.update(lyap_T=float(half.mean() * T), lyap_T_se=batch_se(half) * T, lyap_transits=len(rr) * 200 / T)
        return rec, ts, dt, m

    longs, series = [], {}
    for p in sorted(glob.glob(os.path.join(runs, 'prod', 'long_*.npz'))):
        rec, ts, dt, m = long_record(p)
        longs.append(rec)
        series[f"U_{m['nu']}"] = (ts / m['U']).astype(np.float32)
        series[f"dt_{m['nu']}"] = np.float32(dt)
    longs.sort(key=lambda r: r['Re'])
    for r in longs:                                              # the sweep level of the same viscosity names the long run
        lv = min(lev, key=lambda q: abs(q['nu'] - r['nu']))
        r['Re_level'] = lv['Re']; r['U_over_sweep'] = r['U'] / lv['U']
        if 'lyap_T' in lv:
            r['lyap_T_level'] = lv['lyap_T']
    out['long'] = longs
    if longs:
        def pooled(sel):
            p = {}
            for burn in (50, 200):
                for meth in ('naive', 'gk', 'conformal'):
                    ws = [w for r in longs for w in r['windows'] if w['burn'] == burn and w[meth] is not None and sel(w)]
                    wt = [(w['n_conf'] if meth == 'conformal' else w['n']) for w in ws]
                    if sum(wt):
                        p[f'{meth}_{burn}'] = dict(cov=sum(w[meth] * k for w, k in zip(ws, wt)) / sum(wt), n=sum(wt))
            return p
        # the windows of 5, 10 and 20 transit times were fixed before the sweep; 40 was added after the sweep showed a
        # correlation time of about 12 transit times at one level, before the long runs were analysed
        out['coverage'] = pooled(lambda w: w['W'] in (5, 10, 20))
        out['coverage_by_W'] = {str(W): pooled(lambda w, W=W: w['W'] == W) for W in (5, 10, 20, 40)}
        out['coverage_by_level'] = [dict(Re=r['Re'], tau_int=r['tau_int'],
                                         **{f"{k}_{w['W']}_{w['burn']}": w[k] for w in r['windows'] for k in ('naive', 'gk', 'conformal')})
                                    for r in longs]

        def pooled_level(r, sel):
            p = {}
            for burn in (50, 200):
                for meth in ('naive', 'gk', 'conformal'):
                    ws = [w for w in r['windows'] if w['burn'] == burn and w[meth] is not None and sel(w)]
                    wt = [(w['n_conf'] if meth == 'conformal' else w['n']) for w in ws]
                    if sum(wt):
                        p[f'{meth}_{burn}'] = dict(cov=sum(w[meth] * k for w, k in zip(ws, wt)) / sum(wt), n=sum(wt))
            return p
        def width(ws):
            ws = [w for w in ws if w['conf_width'] is not None]
            return float(sum(w['conf_width'] * w['n_conf'] for w in ws) / sum(w['n_conf'] for w in ws)) if ws else None
        for r in longs:
            r['coverage'] = pooled_level(r, lambda w: w['W'] in (5, 10, 20))
            r['coverage_by_W'] = {str(W): pooled_level(r, lambda w, W=W: w['W'] == W) for W in (5, 10, 20, 40)}
            r['conf_width'] = {str(b_): width([w for w in r['windows'] if w['burn'] == b_ and w['W'] in (5, 10, 20)]) for b_ in (50, 200)}
        out['conf_width'] = {str(b_): width([w for r in longs for w in r['windows'] if w['burn'] == b_ and w['W'] in (5, 10, 20)])
                             for b_ in (50, 200)}
    # ---- a decision and the allocation of pore-scale computing time ----------------------------------------------------
    # nonlinear well loss: the drawdown over its Darcy value, I = (1 / ln(Re_w / Re_e)) * int F dln(Re), Re(r) = Re_w r_w / r
    lr = np.log(Re)
    w = np.zeros(len(Re)); w[1:] += 0.5 * np.diff(lr); w[:-1] += 0.5 * np.diff(lr); w /= (lr[-1] - lr[0])
    I = float(np.sum(w * F))
    # noise of each level from its longest record: the long run where one exists, the sweep run otherwise
    long_lrv = {round(r['nu'], 6): r['lrv_rel'] for r in longs}
    noise = [long_lrv.get(round(r['nu'], 6), r.get('lrv_rel', 0.0)) for r in lev]
    c = np.array([w[i] * F[i] * np.sqrt(max(noise[i], 0.0)) for i in range(len(lev))])   # sd contribution per unit sqrt(1/W)
    uns = c > 0
    dec = dict(Re_w=float(Re[-1]), Re_e=float(Re[0]), I=I, weights=[float(v) for v in w], c=[float(v) for v in c],
               lrv_rel=[float(v) for v in noise], lrv_from_long=[round(r['nu'], 6) in long_lrv for r in lev])
    if uns.sum() >= 2:
        Wtot = float(sum(lev[i]['samp_transits'] for i in np.where(uns)[0]))
        W_eq = np.where(uns, Wtot / uns.sum(), 0.0)
        W_opt = np.where(uns, Wtot * c / c[uns].sum(), 0.0)
        var_eq = float(np.sum(c[uns] ** 2 / W_eq[uns])); var_opt = float(np.sum(c[uns] ** 2 / W_opt[uns]))
        dec.update(Wtot=Wtot, sd_equal=float(np.sqrt(var_eq)), sd_opt=float(np.sqrt(var_opt)), gain=1 - var_opt / var_eq,
                   W_opt=[float(v) for v in W_opt], W_equal=[float(v) for v in W_eq])
    if 'rev' in out:
        cv16 = [r['cv'] for r in out['rev']['rows'] if r['n'] == 16]
        if cv16:
            dec['sd_cell'] = float(cv16[0] * I)              # one cell of 16 grains, the scatter of the Darcy regime
    out['decision'] = dec
    # ---- fields for the figures ---------------------------------------------------------------------------------------
    pick = [files[int(np.argmin([abs(level_record(p)['Re'] - t) for p in files]))] for t in (0.05, 30.0, 1e9)]
    fields = {}
    for tag, p in zip(('darcy', 'inertial', 'chaotic'), pick):
        z, m = load(p)
        fields[tag + '_speed'] = (np.hypot(z['ubar'], z['vbar']) / (m['U'] / m['porosity'])).astype(np.float16)
        fields[tag + '_tke'] = (z['tke'] / (0.5 * (m['U'] / m['porosity']) ** 2)).astype(np.float16)
        fields[tag + '_phi'] = (z['phi_field'] / (m['g'] * m['U'])).astype(np.float16)
        fields[tag + '_Re'] = np.float32(m['Re'])
    fields['solid'] = z['solid']
    np.savez_compressed(os.path.join(RES, 'kaos_fields.npz'), **fields)
    if series:
        np.savez_compressed(os.path.join(RES, 'kaos_series.npz'), **series)
    with open(os.path.join(RES, 'kaos.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    # ---- console summary ------------------------------------------------------------------------------------------------
    print('levels:')
    for r in lev:
        print(f"  Re={r['Re']:8.2f} F={r['F']:.3f} budget={r['budget']:.3f} mean={r['mean_share']:.3f} fluct={r['fluct_share']:.3f} "
              f"cv={r['U_cv']:.1e} lyapT={r.get('lyap_T', float('nan')):.3f}±{r.get('lyap_T_se', float('nan')):.3f} "
              f"uns_share={r.get('unsteady_share', float('nan')):.3f} tau={r.get('tau_int', float('nan')):.2f} "
              f"f_peak={r.get('f_peak', float('nan')):.3f} peak_share={r.get('peak_share', float('nan')):.3f} slow={r.get('slow_share', float('nan')):.3f} "
              f"Ma={r['umax'] * 3 ** 0.5:.3f}")
    print('onset unsteady', out['onset_unsteady'], 'chaos', out['onset_chaos'])
    for k, v in cl.items():
        print('closure', k, 'extrap max', v.get('extrapolation_max'), 'loo rms', v.get('loo_rms'))
    if 'rev' in out:
        print('rev', [(r['n'], round(r['mean'], 4), round(r['cv'], 4)) for r in out['rev']['rows']], 'slope', out['rev']['slope'])
    for r in longs:
        print('long Re', round(r['Re'], 1), 'transits', round(r['transits']), 'tau', round(r['tau_int'], 2), 'slope', round(r['scaling_slope'], 2),
              'Sokal window', round(r['sokal_window'], 1), 'tau of 200-transit segments', [round(v, 1) for v in r['tau_segments']])
        print('    acf', [(a_['lag'], round(a_['rho'], 3)) for a_ in r['acf']])
        print('    scaling', [(s_['W'], s_['n'], round(100 * s_['var_rel'] ** 0.5, 3), round(100 * s_['var_pred_rel'] ** 0.5, 3)) for s_ in r['scaling']])
        print('    coverage of the level', {k: (round(v['cov'], 3), v['n']) for k, v in r['coverage'].items()}, 'conformal width / model width', r['conf_width'])
        print('    by window', {W: {k: round(v['cov'], 2) for k, v in c.items()} for W, c in r['coverage_by_W'].items()})
        print('    widths', [(w['W'], w['burn'], round(w['conf_width'], 2) if w['conf_width'] else None, round(w['naive_width'], 2)) for w in r['windows']])
        for w_ in r['windows']:
            print('    ', w_)
    print('coverage', out.get('coverage'))
    print('decision', {k: v for k, v in dec.items() if not isinstance(v, list)})


if __name__ == '__main__':
    main(sys.argv[1])
