"""Figures for the CERTAIN-COAST Methodology: the certified safe window (method_window.py) and anytime-valid
verification (method_verify.py)."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

import method_window as MW

C_SWI, C_LIQ, C_FLD, C_WIN, INK, MUTED = '#B03A3A', '#2E6DB4', '#138D90', '#2E8B57', '#1f2328', '#5b6672'


def _style(ax):
    ax.tick_params(labelsize=9)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    ax.grid(color='#e3e6ea', lw=0.7)
    ax.set_axisbelow(True)


def window_probs(R, n=3000, seed=17, nq=61):
    th = MW.sample(n, seed)
    th['zc'] = MW.zcrit(th['qc'])
    K, d0, hL, zc = th['K'], th['d0'], th['hL'], th['zc']
    q = MW.q_amb(K, d0, hL, R); pt = MW.phi_toe(d0, R); d = d0 + R
    Qw = np.linspace(10000, 22000, nq); Qd = np.linspace(0, 12000, nq)
    pS, pL = np.zeros((nq, nq)), np.zeros((nq, nq))
    htar = MW.P['G0'] - zc - R
    for i, qd in enumerate(Qd):
        for j, qw in enumerate(Qw):
            pS[i, j] = np.mean(MW.cstar(K, q, np.full(n, qd), np.full(n, qw)) < pt)
            H = MW.h_from_phi(MW.phi_point(MW.P['xp'], MW.P['re'], K, q, qd, qw), d) + R
            pL[i, j] = np.mean((htar <= MW.P['hmin']) | (H > MW.P['G0'] - zc))
    return Qw, Qd, pS, pL


def fig_window(path, Rs, labels):
    a = MW.P['alpha']
    fig, axs = plt.subplots(1, len(Rs), figsize=(6.9, 3.05), dpi=300, sharey=True)
    for ax, R, lab in zip(axs, Rs, labels):
        Qw, Qd, pS, pL = window_probs(R)
        X, Y = np.meshgrid(Qw / 1000, Qd / 1000)
        win = (pS <= a) & (pL <= a) & (X >= MW.P['D'] / 1000)
        ax.contourf(X, Y, win.astype(float), levels=[0.5, 1.5], colors=[C_WIN], alpha=0.30)
        ax.contour(X, Y, pS, levels=[a], colors=[C_SWI], linewidths=1.8)
        ax.contour(X, Y, pL, levels=[a], colors=[C_LIQ], linewidths=1.8)
        ax.contour(X, Y, pS, levels=[0.5], colors=[C_SWI], linewidths=1.0, linestyles='--')
        ax.contour(X, Y, pL, levels=[0.5], colors=[C_LIQ], linewidths=1.0, linestyles='--')
        ax.axvline(MW.P['D'] / 1000, color=INK, lw=1.0, ls=':')
        if not win.any():
            ax.text(0.5, 0.55, 'window\nclosed', transform=ax.transAxes, ha='center', va='center', fontsize=10,
                    fontweight='bold', color=INK, bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=MUTED, lw=0.8))
        ax.set_title(lab, fontsize=9.4, color=INK)
        ax.set_xlabel('Wellfield pumping Qw (1000 m³/d)', fontsize=8.8)
        _style(ax)
    axs[0].set_ylabel('Port dewatering Qd (1000 m³/d)', fontsize=8.8)
    handles = [Patch(fc=C_WIN, alpha=0.3, label='certified safe window'),
               Line2D([], [], color=C_SWI, lw=1.8, label='intrusion limit, 95%'),
               Line2D([], [], color=C_LIQ, lw=1.8, label='liquefaction limit, 95%'),
               Line2D([], [], color=MUTED, lw=1.0, ls='--', label='limits without margin'),
               Line2D([], [], color=INK, lw=1.0, ls=':', label='water demand D')]
    fig.legend(handles=handles, loc='lower center', ncol=3, fontsize=8.6, frameon=False, bbox_to_anchor=(0.5, -0.01),
               handlelength=1.8, columnspacing=1.4)
    fig.tight_layout(rect=(0, 0.15, 1, 1))
    fig.savefig(path, dpi=300); plt.close(fig)


def fig_closing(path, res):
    cv = res['curves']
    t = np.array(cv['t']); qA, qB = np.array(cv['qA']) / 1000, np.array(cv['qB']) / 1000
    qAm, qBm = np.array(cv['qA_med']) / 1000, np.array(cv['qB_med']) / 1000
    ts, tm = res['t_cert'], res['t_median']
    top = 12.0
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.9, 3.6), dpi=300, gridspec_kw=dict(width_ratios=[1.05, 1]))
    m = t <= 150
    neg = lambda v: np.where(v >= 0, v, np.nan)
    ax.fill_between(t[m], np.clip(qA[m], 0, top), np.clip(qB[m], 0, top), where=(qB[m] >= qA[m]) & (qA[m] >= 0),
                    color=C_WIN, alpha=0.28, lw=0)
    ax.plot(t[m], neg(qA[m]), color=C_LIQ, lw=2.0, label='least dewatering against liquefaction')
    ax.plot(t[m], neg(qB[m]), color=C_SWI, lw=2.0, label='most dewatering before intrusion')
    ax.plot(t[m], neg(qAm[m]), color=C_LIQ, lw=1.0, ls='--', label='same, without margins')
    ax.plot(t[m], neg(qBm[m]), color=C_SWI, lw=1.0, ls='--')
    ax.axvline(ts, color=INK, lw=1.0)
    ax.text(ts, top * 1.015, f'certified {ts:.0f} yr', fontsize=8.6, color=INK, ha='center', va='bottom')
    if np.isfinite(tm) and tm <= 150:
        ax.axvline(tm, color=MUTED, lw=1.0, ls='--')
        ax.text(tm, top * 1.015, f'median {tm:.0f} yr', fontsize=8.6, color=MUTED, ha='center', va='bottom')
    ax.set_xlim(0, 150); ax.set_ylim(0, top)
    ax.set_xlabel('Years from now', fontsize=8.8); ax.set_ylabel('Port dewatering (1000 m³/d)', fontsize=8.8)
    ax.text(-0.02, 1.10, '(a)', transform=ax.transAxes, fontsize=9.4, fontweight='bold', color=INK)
    ax.set_yticks([0, 3, 6, 9, 12])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.27), ncol=1, fontsize=8.6, frameon=False, handlelength=1.8)
    _style(ax)

    P = res['plans']
    rows = [('Joint, certified', P['joint']), ('Flooding only', P['flood_only']),
            ('Intrusion only', P['swi_only']), ('Liquefaction only', P['liq_only'])]
    for i, (lab, pl) in enumerate(rows):
        y = len(rows) - 1 - i
        b, u = pl['believed'], pl['unsafe_from']
        if i == 0:
            bx.barh(y, b, color=C_WIN, height=0.56)
            bx.text(b + 2, y, f'{b:.0f} yr', va='center', fontsize=8.8, color=INK, fontweight='bold')
            continue
        safe = min(u, b)
        bx.barh(y, safe, color='#c9d3dc', height=0.56)
        if b > u:
            bx.barh(y, b - u, left=u, color='white', edgecolor=C_SWI, hatch='////', height=0.56, lw=0.8)
        bx.text(b + 2, y, f'believes {b:.0f}', va='center', ha='left', fontsize=8.6, color=INK)
    bx.set_yticks(range(len(rows))); bx.set_yticklabels([r[0] for r in rows][::-1], fontsize=8.8)
    bx.set_xlim(0, 150); bx.set_xlabel('Years of operation the plan believes safe', fontsize=8.8)
    bx.text(-0.02, 1.10, '(b)', transform=bx.transAxes, fontsize=9.4, fontweight='bold', color=INK)
    hs = [Patch(fc=C_WIN, label='certified joint window'), Patch(fc='#c9d3dc', label='safe'),
          Patch(fc='white', ec=C_SWI, hatch='////', label='believed safe, in fact not')]
    bx.legend(handles=hs, loc='upper center', bbox_to_anchor=(0.45, -0.27), ncol=1, fontsize=8.6, frameon=False)
    _style(bx); bx.grid(axis='y', visible=False)
    fig.tight_layout()
    fig.savefig(path, dpi=300); plt.close(fig)


def fig_sensors(path, res):
    S = res['sensors']
    names = [s['sensor'] for s in S]
    yrs = np.array([s['years'] for s in S]); se = np.array([s['years_se'] for s in S])
    red = np.array([100 * s['spread_reduction'] for s in S])
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.9, 2.3), dpi=300, sharey=True)
    y = np.arange(len(S))[::-1]
    ax.barh(y, yrs, xerr=2 * se, color=C_WIN, height=0.56, error_kw=dict(lw=0.9, capsize=2, ecolor=INK))
    for yi, v, s in zip(y, yrs, S):
        ax.text(v + 2 * se.max() + 0.4, yi, f'+{v:.1f} yr · €{s["cost"]:,}', va='center', fontsize=8.6, color=INK)
    ax.set_xlim(0, max(yrs.max() * 1.75, 1)); ax.set_yticks(y); ax.set_yticklabels(names, fontsize=8.8)
    ax.set_xlabel('Years added before the window closes', fontsize=8.8)
    ax.set_title('(a) New criterion: years of safe operation', fontsize=9.4, color=INK, loc='left')
    bx.barh(y, red, color='#8796a5', height=0.56)
    for yi, v in zip(y, red):
        bx.text(v + 1, yi, f'{v:.0f}%', va='center', fontsize=8.6, color=INK)
    bx.set_xlim(0, max(red.max() * 1.35, 10)); bx.set_xlabel('Reduction of today\'s forecast spread', fontsize=8.8)
    bx.set_title('(b) Classical criterion', fontsize=9.4, color=INK, loc='left')
    for a_ in (ax, bx):
        _style(a_); a_.grid(axis='y', visible=False)
    fig.tight_layout()
    fig.savefig(path, dpi=300); plt.close(fig)


def fig_verify(path, ver):
    from scipy.stats import beta as B
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.9, 2.9), dpi=300, gridspec_kw=dict(width_ratios=[1.35, 1]))
    n = np.arange(3, 151)
    cols = {0: '#1F3864', 1: '#2E6DB4', 2: '#7FA6D8'}
    for x in (0, 1, 2):
        ub = np.array([B.ppf(0.95, x + 1, k - x) for k in n])
        ax.plot(n, ub * 100, color=cols[x], lw=2.0, label=f'{x} miss' + ('' if x == 1 else 'es'))
        for a in (0.10, 0.05):
            k = next(int(k) for k, u in zip(n, ub) if u <= a)
            ax.plot(k, a * 100, 'o', ms=5, color=cols[x], mec='white', zorder=5)
            ax.text(k + 1.5, a * 100 + (0.9 if a == 0.10 else -1.0), str(k), fontsize=8.6, color=cols[x], fontweight='bold',
                    va='bottom' if a == 0.10 else 'top', ha='left', zorder=6, bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none'))
    for a, lab in ((10, 'αₖ = 10%'), (5, 'αₖ = 5%')):
        ax.axhline(a, color='#B45309', lw=0.9, ls='--')
        ax.text(149, a + 0.5, lab, ha='right', va='bottom', fontsize=8.6, color='#92400E')
    ax.set_xlim(0, 150); ax.set_ylim(0, 40)
    ax.set_xlabel('Number of exceedance events n', fontsize=8.8)
    ax.set_ylabel('Upper 95% bound on miss rate (%)', fontsize=8.8)
    ax.legend(loc='upper right', frameon=False, fontsize=8.6)
    ax.set_title('(a) Events needed, one planned look', fontsize=9.4, color=INK, loc='left')
    _style(ax)
    fa = ver['false_alarm']
    labs = ['Bound checked\nafter every event', 'Bound checked\nevery 10th event', 'Anytime-valid\ne-process']
    vals = [100 * fa['naive_every_event'], 100 * fa['naive_quarterly'], 100 * fa['eprocess_pooled']]
    cs = ['#c98b8b', '#c98b8b', C_WIN]
    y = np.arange(3)[::-1]
    bx.barh(y, vals, color=cs, height=0.56)
    for yi, v in zip(y, vals):
        bx.text(v + 1.5 if v >= 10 else 7.5, yi, f'{v:.0f}%' if v >= 10 else f'{v:.1f}%', va='center', fontsize=8.8, color=INK,
                fontweight='bold')
    bx.axvline(5, color='#B45309', lw=0.9, ls='--')
    bx.text(6.5, 0.5, 'allowed 5%', fontsize=8.6, color='#92400E', va='center')
    bx.set_yticks(y); bx.set_yticklabels(labs, fontsize=8.6)
    bx.set_xlim(0, 90); bx.set_xlabel('Runs flagging a calibrated alarm (%)', fontsize=8.8)
    bx.set_title('(b) Looking often, six alarms', fontsize=9.4, color=INK, loc='left')
    _style(bx); bx.grid(axis='y', visible=False)
    fig.tight_layout()
    fig.savefig(path, dpi=300); plt.close(fig)


# ------------------------------------------------------------------------------------------------ C3 and Section 4.2
K_COL = {'routine': '#9aa3ad', 'random': '#6b7680', 'eopt': '#C27C12', 'eopt_safe': '#6a4fb3', 'goal_safe': C_WIN}
K_SHORT = {'routine': 'Routine operation', 'random': 'Random perturbations', 'eopt': 'E-optimal, no safety filter',
           'eopt_safe': 'E-optimal with safety filter', 'goal_safe': 'Goal-oriented and safe (C3)'}


def fig_active(path, A):
    """(a) Certified closing year of the window during the test campaign; (b) highest chloride reached."""
    import method_active as MA
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.9, 3.35), dpi=300, gridspec_kw=dict(width_ratios=[1.1, 1]))
    kinds = ['routine', 'random', 'eopt', 'eopt_safe', 'goal_safe']
    w = np.arange(1, A['params']['CAMP'] + 1)
    for k in kinds:
        W = np.array([r['weekly'] for r in A['kinds'][k]['runs']])
        med, lo, hi = np.median(W, 0), np.percentile(W, 10, 0), np.percentile(W, 90, 0)
        ls = '--' if k == 'eopt' else '-'
        lw = 2.2 if k == 'goal_safe' else 1.5
        if k in ('goal_safe', 'eopt'):
            ax.fill_between(w, lo, hi, color=K_COL[k], alpha=0.16, lw=0)
        ax.plot(w, med, color=K_COL[k], lw=lw, ls=ls, label=K_SHORT[k])
    t_true = A['truth']['t_close']
    t_best = MA.closing(A['truth']['h_crit'])[0]
    ax.axhline(t_true, color=INK, lw=0.9, ls=(0, (4, 2)))
    ax.text(2, t_true + 0.6, f'true closing year: {t_true:.0f}', fontsize=8.6, color=INK, va='bottom')
    ax.axhline(t_best, color=MUTED, lw=0.9, ls=':')
    ax.text(2, t_best - 0.6, f'most any test can certify: {t_best:.0f}', fontsize=8.6, color=MUTED, va='top')
    ax.set_xlim(0, w[-1]); ax.set_ylim(0, 50)
    ax.set_xlabel('Weeks of the campaign', fontsize=8.8)
    ax.set_ylabel('Certified closing year (years)', fontsize=8.8)
    ax.set_title('(a) Certified closing year of the window', fontsize=9.4, color=INK, loc='left')
    _style(ax)
    y = np.arange(len(kinds))[::-1]
    for yi, k in zip(y, kinds):
        cm = 250 * np.array([r['c_max'] for r in A['kinds'][k]['runs']])
        bx.boxplot(cm, positions=[yi], vert=False, widths=0.5, whis=(5, 95), showfliers=False, patch_artist=True,
                   boxprops=dict(fc=K_COL[k] + '55', ec=K_COL[k], lw=1.1), medianprops=dict(color=K_COL[k], lw=1.6),
                   whiskerprops=dict(color=K_COL[k], lw=1.0), capprops=dict(color=K_COL[k], lw=1.0))
        over = np.mean(cm > 250)
        if over > 0:
            bx.text(272, yi, f'{100 * over:.0f}% of runs\nabove 250', fontsize=8.6, color='#92400E', va='center')
    ct = 250 * A['params']['C_TEST']
    bx.axvline(ct, color=C_LIQ, lw=0.9, ls='--'); bx.text(ct - 3, len(kinds) - 0.45, f'test limit {ct:.0f}', fontsize=8.6,
                                                          color=C_LIQ, ha='right', va='center')
    bx.axvline(250, color='#B45309', lw=0.9, ls='--'); bx.text(253, len(kinds) - 0.45, 'limit 250', fontsize=8.6,
                                                               color='#92400E', ha='left', va='center')
    bx.set_yticks(y); bx.set_yticklabels([K_SHORT[k] for k in kinds], fontsize=8.6)
    bx.set_xlim(80, 330); bx.set_ylim(-0.6, len(kinds) - 0.1)
    bx.set_xlabel('Highest chloride during testing (mg/L)', fontsize=8.8)
    bx.set_title('(b) Chloride reached', fontsize=9.4, color=INK, loc='left')
    _style(bx); bx.grid(axis='y', visible=False)
    h, l = ax.get_legend_handles_labels()
    fig.legend(h, l, loc='lower center', ncol=3, fontsize=8.6, frameon=False, handlelength=1.8, columnspacing=1.2,
               bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=[0, 0.13, 1, 1])
    fig.savefig(path, dpi=300); plt.close(fig)


def fig_story(path, S):
    """(a) Yearly exceedance probability and upper bounds; (b) certified closing year by method."""
    g = S['copies']['good']; p = S['copies']['poor']; a = S['params']['ALPHA']; n = S['params']['NFULL']
    yrs = np.arange(1, S['params']['YEARS'] + 1)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.9, 3.0), dpi=300, gridspec_kw=dict(width_ratios=[1.05, 1]))
    ax.plot(yrs, 100 * np.array(g['p_true']), color=INK, lw=2.0, label='Full model (truth)')
    ax.plot(yrs, 100 * np.array(g['p_copy']), color=C_SWI, lw=1.5, ls='--', label='Copy alone')
    ax.plot(yrs, 100 * np.array(g['median_upper_bound']['full_only']), color='#8796a5', lw=1.4,
            label=f'Bound, {n} full runs')
    ax.plot(yrs, 100 * np.array(g['median_upper_bound']['ppi']), color=C_LIQ, lw=1.6,
            label='Prediction-powered')
    ax.axhline(100 * a, color='#B45309', lw=0.9, ls='--')
    ax.text(11, 100 * a + 0.4, f'α = {100 * a:.0f}%', fontsize=8.6, color='#92400E', va='bottom')
    ax.axvline(g['t_true'], color=INK, lw=0.8, ls=':')
    ax.set_xlim(10, yrs[-1]); ax.set_ylim(0, 20)
    ax.set_xlabel('Year of the storyline', fontsize=8.8)
    ax.set_ylabel('Chloride above the limit (% of storylines)', fontsize=8.8)
    ax.set_title('(a) Exceedance, better copy', fontsize=9.4, color=INK, loc='left')
    ax.legend(loc='upper left', fontsize=8.6, frameon=False, handlelength=1.8)
    _style(ax)
    rows = [('Copy alone, poorer', p['copy_only'], C_SWI), ('Copy alone, better', g['copy_only'], C_SWI),
            (f'{n} full runs alone', g['full_only'], '#8796a5'),
            ('Pred.-powered, poorer', p['ppi'], C_LIQ), ('Pred.-powered, better', g['ppi'], C_LIQ),
            ('Exact variant, better', g['ppi_exact'], '#1F3864')]
    y = np.arange(len(rows))[::-1]
    for yi, (lab, r, col) in zip(y, rows):
        bx.plot([r['p5'], r['p95']], [yi, yi], color=col, lw=2.2, solid_capstyle='round')
        bx.plot(r['median'], yi, 'o', color=col, ms=6, mec='white', zorder=4)
        bx.text(r['p5'] - 0.7, yi, f'{r["median"]:.0f}', fontsize=8.6, color=INK, va='center', ha='right')
    bx.axvline(g['t_true'], color=INK, lw=0.9, ls=(0, (4, 2)))
    bx.text(g['t_true'] + 0.3, len(rows) - 0.35, f'true: {g["t_true"]}', fontsize=8.6, color=INK, va='center')
    bx.set_yticks(y); bx.set_yticklabels([r[0] for r in rows], fontsize=8.6)
    bx.set_xlim(18, 55); bx.set_ylim(-0.6, len(rows) - 0.05)
    bx.set_xlabel('Closing year (median, 5–95%)', fontsize=8.8)
    bx.set_title('(b) Closing year', fontsize=9.4, color=INK, loc='left')
    _style(bx); bx.grid(axis='y', visible=False)
    fig.tight_layout()
    fig.savefig(path, dpi=300); plt.close(fig)


P_ORDER = [('right', 'nominal'), ('right', 'wide2'), ('right', 'wide4'), ('right', 'box'), ('right', 'checked'),
           ('wrong1', 'nominal'), ('wrong1', 'wide2'), ('wrong1', 'checked'),
           ('wrong2', 'nominal'), ('wrong2', 'wide2'), ('wrong2', 'wide4'), ('wrong2', 'checked'),
           ('wrong3', 'nominal'), ('wrong3', 'wide2'), ('wrong3', 'wide4'), ('wrong3', 'checked')]
P_LAB = {'nominal': 'radius S', 'wide2': 'radius 2S', 'wide4': 'radius 4S', 'box': 'physics-only prior',
         'checked': 'S and conflict test'}
P_COL = {'nominal': '#2E8B57', 'wide2': '#2E6DB4', 'wide4': '#6a4fb3', 'box': '#8796a5', 'checked': '#C27C12'}
P_MISS, P_UNSAFE = '#9fb1c4', '#B45309'


def prior_rates(P, key):
    """Share of runs whose confidence set missed the true coefficients in some week, and share whose certified
    boundary was below the true one in some week (closing year beyond the most a correct certificate gives)."""
    rs, t_best = P['runs'][key], P['truth']['t_best']
    miss = float(np.mean([not r['covered_all'] for r in rs]))
    unsafe = float(np.mean([max([r['t_before'], r['t_after']] + r['weekly']) > t_best + 1e-9 for r in rs]))
    return miss, unsafe


def fig_prior(path, P):
    """(a) Certified closing year after the campaign, by prior and use of the prior; (b) how often the confidence
    set missed the truth and how often the certified boundary crossed the true one."""
    t_true, t_best = P['truth']['t_close'], P['truth']['t_best']
    rows = [(pk, m) for pk, m in P_ORDER if f'{pk}_{m}' in P['runs']]
    err = {pk: P['prior_error'][pk]['nominal'] for pk in P['prior_error']}
    # y positions, top to bottom, with a gap before each prior
    y, cur, prev, heads = [], 0.0, None, {}
    for pk, m in rows:
        if pk != prev:
            cur -= 1.05 if prev is not None else 0.0
            heads[pk] = cur + 0.62
            prev = pk
        y.append(cur); cur -= 1.0
    y = np.array(y)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.9, 6.3), dpi=300, gridspec_kw=dict(width_ratios=[1.5, 1]), sharey=True)
    for yi, (pk, m) in zip(y, rows):
        rs = P['runs'][f'{pk}_{m}']
        ta = np.array([r['t_after'] for r in rs])
        lo, md, hi = np.percentile(ta, 10), np.median(ta), np.percentile(ta, 90)
        ax.plot([lo, hi], [yi, yi], color=P_COL[m], lw=2.4, solid_capstyle='round')
        ax.plot(md, yi, 'o', color=P_COL[m], ms=6, mec='white', zorder=4)
        ax.text(max(hi, md) + 0.9, yi, f'{md:.1f}', fontsize=8.6, color=INK, va='center',
                bbox=dict(fc='white', ec='none', pad=0.4), zorder=5)
        miss, unsafe = prior_rates(P, f'{pk}_{m}')
        if miss == 0 and unsafe == 0:
            bx.text(1.5, yi, 'none', fontsize=8.6, color=MUTED, va='center')
            continue
        for off, v, colr in ((0.19, miss, P_MISS), (-0.19, unsafe, P_UNSAFE)):
            bx.barh(yi + off, 100 * v, height=0.34, color=colr)
            bx.text(100 * v + 1.5, yi + off, f'{100 * v:.0f}%', fontsize=8.6, color=(INK if v > 0 else MUTED), va='center')
    for pk, yh in heads.items():
        name = (f'Prior of Section 7.6: {err[pk]:.1f}σ from the truth (S = {P["S_nominal_sigma"]:.0f}σ)'
                if pk == 'right' else f'Optimistic prior: {err[pk]:.1f}σ from the truth')
        ax.text(0.0, yh, name, fontsize=8.6, color=INK, va='center', ha='left', fontweight='bold',
                bbox=dict(fc='white', ec='none', pad=0.3), zorder=5)
        for a in (ax, bx):
            a.axhline(yh + 0.42, color='#c9d1d9', lw=0.8)
    ax.axvline(t_true, color=INK, lw=0.9, ls=(0, (4, 2)))
    ax.axvline(t_best, color=MUTED, lw=1.0, ls=':')
    ax.set_yticks(y); ax.set_yticklabels([P_LAB[m] for pk, m in rows], fontsize=8.6)
    ax.set_xlim(-1, 50); ax.set_ylim(y.min() - 0.7, max(heads.values()) + 0.55)
    ax.set_xlabel('Certified closing year after the campaign\n(dot: median; bar: 10–90% of runs)', fontsize=8.8)
    ax.set_title('(a) Certified closing year', fontsize=9.4, color=INK, loc='left')
    _style(ax); ax.grid(axis='y', visible=False)
    bx.set_xlim(0, 118); bx.set_xticks([0, 25, 50, 75, 100])
    bx.set_xlabel('Runs (%)', fontsize=8.8)
    bx.set_title('(b) Failures of the guarantee', fontsize=9.4, color=INK, loc='left')
    _style(bx); bx.grid(axis='y', visible=False); bx.tick_params(axis='y', length=0)
    hs = [Line2D([], [], color=INK, lw=0.9, ls=(0, (4, 2))), Line2D([], [], color=MUTED, lw=1.0, ls=':'),
          Patch(color=P_MISS), Patch(color=P_UNSAFE)]
    ls = [f'True closing year ({t_true:.0f})', f'Most a correct certificate can give ({t_best:.1f})',
          'Confidence set missed the true coefficients in some week',
          'Certified boundary below the true one in some week']
    fig.legend(hs, ls, loc='lower center', ncol=2, fontsize=8.6, frameon=False, handlelength=2.2,
               columnspacing=1.6, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.075, 1, 1))
    fig.savefig(path, dpi=300); plt.close(fig)
