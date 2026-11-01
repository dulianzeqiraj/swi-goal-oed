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
