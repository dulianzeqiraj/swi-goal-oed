"""Figures of the SPIRANCA-GO note: res/figS1_map.png (sector, wells, designs; the causal picture),
res/figS2_results.png (alarms by method and scenario; designs), res/figS3_checks.png (checks of N1 and N3)."""
import os, sys, json, collections
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, 'res')
M_CLF, M_CLS = 12.92, 21781.0          # fresh and sea chloride of the section model (mg/L)
NAVY, ORANGE, TEAL, GREY, RED, GREEN, PURPLE = '#1F3864', '#D97706', '#0F766E', '#6B7280', '#B91C1C', '#15803D', '#6D28D9'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
D = json.load(open(os.path.join(RES, 'sg.json')))
ROWS = D['rows']
SC = ['none', 'worst', 'uniform', 'offspan']
SC_LAB = {'none': 'no warming', 'worst': 'worst warming', 'uniform': 'warming U(0, max)', 'offspan': 'off-span stress'}
SC_COL = {'none': NAVY, 'worst': RED, 'uniform': ORANGE, 'offspan': GREY}
METH = ['ols', 'ar_cv', 'ar_dec', 'iv', 'olsA', 'olsA_c', 'spir']
LABEL_OFF = {'A23': (-0.4, -0.9, 'right'), 'A11': (-0.5, 1.0, 'right'), 'A24': (0.2, 1.35, 'center'), 'A25': (0.5, 0.5, 'left'),
             'P13': (0.45, -0.9, 'left'), 'P17': (-0.1, -1.0, 'center'), 'A10': (0.45, 0.35, 'left'), 'P12': (0.3, 0.35, 'left'),
             'A28': (0.3, 0.45, 'left'), 'P4': (-0.4, 0.75, 'right'), 'A30': (-0.65, 0.0, 'right'), 'A9': (0.6, -0.55, 'left'),
             'A4': (0.0, 0.7, 'center'), 'P3': (0.45, -0.25, 'left'), 'A3': (0.4, 0.3, 'left'), 'A13': (0.5, 0.0, 'left')}
M_LAB = {'ols': 'least squares on heads', 'ar_cv': 'anchor regression, CV gamma', 'ar_dec': 'anchor regression, gamma of the decision',
         'iv': 'anchor regression, gamma = inf (IV)', 'olsA': 'least squares on heads and anchors',
         'olsA_c': '... + SPIRANCA certificate', 'spir': 'SPIRANCA-GO'}


def box(ax, x, y, w, h, title, lines, color, fc='white'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.01,rounding_size=0.015', fc=fc, ec=color, lw=1.5))
    ax.text(x + w / 2, y + h - 0.03, title, ha='center', va='top', fontsize=8.6, fontweight='bold', color=color)
    for k, s in enumerate(lines):
        ax.text(x + w / 2, y + h - 0.085 - 0.05 * k, s, ha='center', va='top', fontsize=7.4, color='#1F2328')


def arrow(ax, a, b, color, ls='-', lw=1.4, rad=0.0, text=None, tpos=None):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=10, color=color, lw=lw, ls=ls, connectionstyle=f'arc3,rad={rad}'))
    if text:
        ax.text(*(tpos or ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)), text, fontsize=7.0, color=color, ha='center', va='center',
                bbox=dict(fc='white', ec='none', pad=0.6))


def fig_map():
    import sg_model as G
    bed = G.Bed(); m = bed.m
    fig = plt.figure(figsize=(11.0, 5.6))
    ax = fig.add_axes([0.04, 0.07, 0.40, 0.86])
    v = m.valid
    ax.scatter(m.cx[v], m.cy[v], s=3.2, c='#E8EEF6', marker='s', lw=0)
    band = bed.hmask
    ax.scatter(m.cx[band], m.cy[band], s=3.2, c='#FCE7C8', marker='s', lw=0)
    pl = pd.read_csv(os.path.join(G.ROOT, 'chloride_fk', 'derived', 'shoreline_polyline.csv'))
    ax.plot(pl['x_km'], pl['y_km'], color=TEAL, lw=1.2)
    freq = collections.Counter(w for r in ROWS for w in r['designs']['spir']['wells'])
    near = ROWS[0]['designs']['near']['wells']
    for k, wid in enumerate(bed.mon_ids):
        c = bed.mon_cells[k]
        f = freq.get(wid, 0) / len(ROWS)
        ax.scatter(m.cx[c], m.cy[c], s=26 + 260 * f, c=[NAVY], alpha=0.25 + 0.75 * min(1, f * 1.4), edgecolor=NAVY, lw=0.8, zorder=3)
        if wid in near:
            ax.scatter(m.cx[c], m.cy[c], s=150, facecolor='none', edgecolor=ORANGE, lw=1.6, zorder=4)
        dx, dy, ha = LABEL_OFF.get(wid, (0.35, 0.25, 'left'))
        ax.text(m.cx[c] + dx, m.cy[c] + dy, f'{wid}' + (f' {100 * f:.0f}%' if f >= 0.1 else ''), fontsize=6.8, color=NAVY, zorder=5, ha=ha,
                va='center')
    for wid, c, (dx, dy) in (('A1 (goal screen)', bed.cA, (-0.5, 1.1)), ('P10', bed.cB, (-0.4, -0.9))):
        ax.scatter(m.cx[c], m.cy[c], s=120, marker='*', c=RED, zorder=6)
        ax.text(m.cx[c] + dx, m.cy[c] + dy, wid, fontsize=7.4, color=RED, ha='right', zorder=6, bbox=dict(fc='white', ec='none', pad=0.4, alpha=0.85))
    ax.set_xlim(-1.5, 12.5); ax.set_ylim(23.5, 52.5); ax.set_aspect('equal')
    ax.set_xlabel('x (km)'); ax.set_ylabel('y (km)')
    ax.set_title('(a) The coastal sector of the chloride study', fontsize=10, fontweight='bold', color=NAVY, loc='left')
    ax.text(0.98, 0.985, 'blue disc: share of the 100 aquifers in which\nthe SPIRANCA-GO design picks the well\norange ring: the three wells nearest A1\nbeige: private abstraction (0.5-4 km)\ngreen: shoreline',
            transform=ax.transAxes, fontsize=6.8, ha='right', va='top', color='#3A4350', bbox=dict(fc='white', ec='#C9D1DC', pad=3))
    # (b) the causal picture
    bx = fig.add_axes([0.47, 0.03, 0.515, 0.92]); bx.set_axis_off(); bx.set_xlim(0, 1); bx.set_ylim(0, 1)
    bx.text(0.0, 0.985, '(b) What is recorded, what is decided, what shifts unseen', fontsize=10, fontweight='bold', color=NAVY, va='top')
    box(bx, 0.00, 0.62, 0.27, 0.27, 'Anchors (recorded)', ['rain gauge anomaly r', 'operator pumping u_A, u_B', 'exogenous: nothing', 'points into them'], NAVY, '#EEF3FA')
    box(bx, 0.37, 0.62, 0.27, 0.27, 'Sources (not recorded)', ['recharge R', 'private abstraction H', 'pumping Q_A, Q_B', '(+ unrecorded noise)'], TEAL, '#ECFDF5')
    box(bx, 0.72, 0.62, 0.265, 0.27, 'Potential phi', ['linear in the sources:', 'phi = sum of unit', 'responses x sources', '(Strack, steady)'], GREY, '#F3F4F6')
    box(bx, 0.37, 0.18, 0.27, 0.27, 'Heads X (cheap)', ['piezometers, 0.1 m noise', 'the proxy reads these', 'b chosen by the goal'], NAVY, '#EEF3FA')
    box(bx, 0.72, 0.18, 0.265, 0.27, 'Goal Y', ['phi at A1 < phi*', '<=> chloride of the', 'upper screen > 250 mg/L'], RED, '#FEF2F2')
    arrow(bx, (0.27, 0.755), (0.37, 0.755), NAVY)
    arrow(bx, (0.64, 0.755), (0.73, 0.755), TEAL)
    arrow(bx, (0.86, 0.62), (0.86, 0.45), GREY)
    arrow(bx, (0.80, 0.62), (0.58, 0.45), GREY)
    arrow(bx, (0.64, 0.31), (0.73, 0.31), NAVY, text='alarm', tpos=(0.685, 0.35))
    box(bx, 0.00, 0.30, 0.25, 0.20, 'Decision (known)', ['u_A = 0.6, u_B = 0.3', 'outside the record'], ORANGE, '#FFF5E1')
    arrow(bx, (0.12, 0.50), (0.12, 0.62), ORANGE)
    box(bx, 0.00, 0.03, 0.25, 0.20, 'Warming (unseen)', ['acts like a drought the', 'gauge does not record'], PURPLE, '#F5F3FF')
    arrow(bx, (0.25, 0.13), (0.45, 0.62), PURPLE, ls='--', rad=-0.25, text='shift in span(M):\nR down, H up', tpos=(0.31, 0.34))
    bx.text(0.37, 0.07, 'Off-span stress: H up by 30 % with no change of R\n(outside the class the anchors can protect)', fontsize=7.2, color=GREY, va='center', style='italic')
    fig.savefig(os.path.join(RES, 'figS1_map.png'), dpi=220)
    plt.close(fig)


def fig_results():
    from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
    fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.6), gridspec_kw=dict(width_ratios=[1.5, 1.0], wspace=0.28))
    ax = axs[0]
    y0 = np.arange(len(METH))[::-1]
    for j, sc in enumerate(SC):
        for i, nm in enumerate(METH):
            o = np.array([r['all'][nm][sc]['over'] for r in ROWS])
            yy = y0[i] + (1.5 - j) * 0.17
            ax.plot([np.quantile(o, 0.1), np.quantile(o, 0.9)], [yy, yy], color=SC_COL[sc], lw=1.2, alpha=0.8)
            ax.scatter([o.mean()], [yy], s=16, color=SC_COL[sc], zorder=3, label=SC_LAB[sc] if i == 0 else None)
    ax.axvline(0.10, color='#1F2328', ls='--', lw=0.9)
    ax.text(0.105, y0[-1] - 0.62, 'alpha = 10 %', fontsize=7.4)
    ax.set_yticks(y0); ax.set_yticklabels([M_LAB[n] for n in METH], fontsize=8)
    ax.set_ylim(y0[-1] - 0.8, y0[0] + 0.6)
    ax.set_xscale('symlog', linthresh=0.05); ax.set_xlim(0, 1.05)
    ax.xaxis.set_major_locator(FixedLocator([0, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]))
    ax.xaxis.set_major_formatter(FixedFormatter(['0', '2 %', '5 %', '10 %', '20 %', '50 %', '100 %']))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlabel('share of future seasons in which the proxy over-predicts by more than its margin\n(dot: mean over 100 aquifers; line: 10-90 % range)', fontsize=8.4)
    ax.legend(fontsize=7.4, loc='upper left', frameon=True, title='future scenario', title_fontsize=7.4)
    ax.set_title('(a) Is the alarm still valid after the decision?', fontsize=10, fontweight='bold', color=NAVY, loc='left')
    ax = axs[1]
    lab = {'near': 'three nearest to A1', 'r2': 'largest record R²', 'spir': 'SPIRANCA-GO design'}
    col = {'near': ORANGE, 'r2': TEAL, 'spir': NAVY}
    for dn in ('near', 'r2', 'spir'):
        mg = np.array([r['designs'][dn]['spir']['margin'] / r['y_sd'] for r in ROWS])
        fa = np.array([r['designs'][dn]['spir']['worst']['false'] for r in ROWS])
        ov = np.array([r['designs'][dn]['spir']['worst']['over'] for r in ROWS])
        ax.scatter(mg, fa, s=10, color=col[dn], alpha=0.35, lw=0)
        ax.scatter([np.median(mg)], [np.mean(fa)], s=70, color=col[dn], edgecolor='white', lw=1.2, zorder=4,
                   label=f"{lab[dn]}: over-prediction {100 * ov.mean():.1f} %,\nfalse alarms {100 * fa.mean():.1f} %, margin {np.median(mg):.3f} sd")
    ax.set_xscale('log')
    ax.xaxis.set_major_locator(FixedLocator([0.02, 0.05, 0.1, 0.2, 0.5]))
    ax.xaxis.set_major_formatter(FixedFormatter(['0.02', '0.05', '0.1', '0.2', '0.5']))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlabel('certified margin / sd of Y (per aquifer; large dot: median)', fontsize=8.4)
    ax.set_ylabel('false alarms, worst warming (large dot: mean)', fontsize=8.4)
    ax.legend(fontsize=7.0, loc='upper left', frameon=False, title='SPIRANCA-GO alarm on three wells, worst warming', title_fontsize=7.2)
    ax.set_ylim(0, 0.75)
    ax.set_title('(b) Three piezometers: which three?', fontsize=10, fontweight='bold', color=NAVY, loc='left')
    fig.subplots_adjust(left=0.215, right=0.985, bottom=0.2, top=0.9)
    fig.savefig(os.path.join(RES, 'figS2_results.png'), dpi=220)
    plt.close(fig)


def fig_checks():
    C = json.load(open(os.path.join(RES, 'checks.json')))
    rng = np.random.default_rng(2026)
    N = 20000
    U = rng.uniform(-1, 1, (N, 3))
    V = rng.uniform(-1, 1, (N, 2))
    cases = [('target inside the image (m = 3)', U, np.zeros(3), 3, NAVY), ('target off a face (m = 4)', U, np.array([1.5, 0, 0]), 4, RED),
             ('one fact redundant (m = 2)', np.column_stack([V, V.sum(1) / 2]), np.zeros(3), 2, TEAL)]
    fig, axs = plt.subplots(1, 2, figsize=(11.0, 3.9), gridspec_kw=dict(wspace=0.3))
    ax = axs[0]
    taus = np.geomspace(0.03, 0.3, 30)
    for lab, S, s, mth, col in cases:
        Dd = ((S - s) ** 2).sum(1); Dstar = Dd.min() if mth == 4 else 0.0
        Db, ess = [], []
        for t in taus:
            lw = -Dd / (2 * t * t); w = np.exp(lw - lw.max()); w /= w.sum(); Db.append(w @ Dd); ess.append(1 / (w ** 2).sum())
        Db, ess = np.array(Db), np.array(ess); ok = ess > 100
        ax.plot(taus[ok] ** 2, Db[ok] - Dstar, 'o', ms=3.2, color=col, label=lab)
        ax.plot(taus[ok] ** 2, mth * taus[ok] ** 2, '-', color=col, lw=1.0, alpha=0.7)
    ax.set_xlabel('tau^2'); ax.set_ylabel('E_tau[D] - D*   (line: m tau^2)')
    ax.legend(fontsize=7.4, frameon=False)
    ax.set_title('(a) N1: misfit intercept and slope, 20 000 draws', fontsize=10, fontweight='bold', color=NAVY, loc='left')
    ax = axs[1]
    rows = C['n3']
    keys = [('eig8', '8-class EIG', '#9DB4D3'), ('eig16', '16-class EIG', '#5B84B8'), ('I_Q', 'I(Q; y)', NAVY), ('logdet', '1/2 logdet bound', ORANGE), ('hadamard', 'Hadamard bound', RED)]
    x = np.arange(len(rows))
    for j, (k, lab, col) in enumerate(keys):
        ax.bar(x + (j - 2) * 0.16, [r[k] for r in rows], 0.16, color=col, label=lab)
    ax.set_yscale('log')
    from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
    ax.yaxis.set_major_locator(FixedLocator([0.2, 0.5, 1, 2, 5])); ax.yaxis.set_major_formatter(FixedFormatter(['0.2', '0.5', '1', '2', '5']))
    ax.yaxis.set_minor_locator(NullLocator()); ax.set_ylim(0.15, 12)
    ax.set_xticks(x); ax.set_xticklabels(['{' + ','.join(str(i + 1) for i in r['S']) + '}' for r in rows], fontsize=7.4)
    ax.set_xlabel('design (three of six candidates)'); ax.set_ylabel('nats')
    ax.legend(fontsize=7.2, frameon=False, ncol=2, loc='upper left')
    ax.set_title('(b) N3: the chain holds; the analytic end is loose', fontsize=10, fontweight='bold', color=NAVY, loc='left')
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.15, top=0.9)
    fig.savefig(os.path.join(RES, 'figS3_checks.png'), dpi=220)
    plt.close(fig)


def fig_section():
    """res/figS4_section.png: the test on the variable-density section (res/sv.json)."""
    from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
    DV = json.load(open(os.path.join(RES, 'sv.json')))
    RV = DV['rows']
    SCV = ['none', 'worst', 'offspan']
    ROWSV = [('least squares on heads', 'ols', ''), ('anchor regression, gamma = inf (IV)', 'iv', ''),
             ('least squares on heads and anchors', 'olsA', ''), ('... + SPIRANCA certificate', 'olsA_c', ''),
             ('SPIRANCA-GO', 'spir', ''), ('least squares on heads and anchors,\nre-anchored yearly', 'olsA', '_ra'),
             ('SPIRANCA-GO, re-anchored yearly', 'spir', '_ra')]
    fig, axs = plt.subplots(1, 2, figsize=(11.6, 5.1), gridspec_kw=dict(width_ratios=[1.45, 1.0], wspace=0.3))
    ax = axs[0]
    y0 = np.arange(len(ROWSV))[::-1]
    for j, sc in enumerate(SCV):
        for i, (lab, nm, suf) in enumerate(ROWSV):
            o = np.array([r['all'][nm][sc + suf]['over'] for r in RV])
            yy = y0[i] + (1 - j) * 0.2
            ax.plot([np.quantile(o, 0.1), np.quantile(o, 0.9)], [yy, yy], color=SC_COL[sc], lw=1.2, alpha=0.8)
            ax.scatter([o.mean()], [yy], s=16, color=SC_COL[sc], zorder=3, label=SC_LAB[sc] if i == 0 else None)
    ax.axvline(0.10, color='#1F2328', ls='--', lw=0.9)
    ax.text(0.105, y0[-1] - 0.6, 'alpha = 10 %', fontsize=7.4)
    ax.axhspan(y0[-1] - 0.45, y0[-2] + 0.45, color='#EEF3FA', zorder=0)
    ax.set_yticks(y0); ax.set_yticklabels([r[0] for r in ROWSV], fontsize=7.8)
    ax.set_ylim(y0[-1] - 0.75, y0[0] + 0.6)
    ax.set_xscale('symlog', linthresh=0.05); ax.set_xlim(0, 1.05)
    ax.xaxis.set_major_locator(FixedLocator([0, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]))
    ax.xaxis.set_major_formatter(FixedFormatter(['0', '2 %', '5 %', '10 %', '20 %', '50 %', '100 %']))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlabel('share of future seasons in which the alarm over-predicts by more than its margin\n(dot: mean over %d aquifers; line: 10-90 %% range)' % len(RV), fontsize=8.4)
    ax.legend(fontsize=7.4, loc='upper center', frameon=False, ncol=3, bbox_to_anchor=(0.5, -0.2))
    ax.set_title('(a) Variable-density section: is the alarm still valid?', fontsize=10, fontweight='bold', color=NAVY, loc='left')
    # (b) one aquifer where the static alarm fails: chloride over the 30 years after the decision
    ax = axs[1]
    fails = [r for r in RV if r['all']['spir']['none']['over'] > 0.3]
    ex = max(fails, key=lambda r: r['all']['spir']['none']['over']) if fails else RV[0]
    ser = ex['all']['spir']['none_series']
    cl = lambda y: M_CLF + 10 ** (-np.asarray(y)) * (M_CLS - M_CLF)
    tY = np.arange(1, len(ser['Y']) + 1) * 0.5
    mg = ex['all']['spir']['margin']
    ax.plot(tY, cl(ser['Y']), color='#1F2328', lw=1.8, label='chloride at the supply screen')
    ax.plot(tY, cl(ser['yh']), color=RED, lw=1.2, label='SPIRANCA-GO prediction from heads')
    ax.plot(tY, cl(ser['yh_ra']), color=NAVY, lw=1.2, label='the same, re-anchored by a yearly sample')
    ax.axhline(250, color=ORANGE, ls='--', lw=1.0)
    ax.text(0.5, 262, '250 mg/L', fontsize=7.4, color=ORANGE)
    lim_alarm = cl(DV.get('ystar', ex.get('ystar', 1.963)) + mg)
    ax.axhline(lim_alarm, color=GREY, ls=':', lw=1.0)
    ax.text(0.5, lim_alarm * 1.04, 'alarm level of the prediction (%.0f mg/L)' % lim_alarm, fontsize=7.0, color=GREY)
    ax.set_yscale('log'); ax.set_xlabel('years after the decision'); ax.set_ylabel('chloride (mg/L)')
    ax.legend(fontsize=7.0, loc='upper left', frameon=False)
    ax.set_title('(b) One aquifer after the decision', fontsize=10, fontweight='bold', color=NAVY, loc='left')
    from matplotlib.ticker import FixedLocator as FL2, FixedFormatter as FF2, NullLocator as NL2
    ax.yaxis.set_major_locator(FL2([10, 20, 50, 100, 200, 500])); ax.yaxis.set_major_formatter(FF2(['10', '20', '50', '100', '200', '500'])); ax.yaxis.set_minor_locator(NL2())
    fig.subplots_adjust(left=0.19, right=0.985, bottom=0.26, top=0.9)
    fig.savefig(os.path.join(RES, 'figS4_section.png'), dpi=220)
    plt.close(fig)
    return ex['seed']


if __name__ == '__main__':
    which = sys.argv[1:] or ['map', 'results', 'checks']
    if 'map' in which: fig_map()
    if 'results' in which: fig_results()
    if 'checks' in which: fig_checks()
    if 'section' in which: fig_section()
