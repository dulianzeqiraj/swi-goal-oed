"""Figures of the GARANCIA-GO review (English labels; every text at least 8.6 pt at the printed size).
usage: python gar_figs.py OUT_DIR

fig_scheme   the GARANCIA-GO loop: physical prior given the rain -> simulated aquifers -> one reconstructor -> scores ->
             calibrated bands for the field case, with the field check and the dispersion branch
fig_case     one test case of T1 (rain + 4 loggers): exact, raw ensemble, CRC and sup-norm bands for every boundary function
fig_t1       T1 and T1A: miss fraction, whole-function coverage, and what four loggers buy in guaranteed width
fig_t2       T2 and T5: risk and coverage against the number of calibration simulations; one calibration set
fig_t3       T3: field departures, the conformal alarm and the guarantee
fig_t4       T4: Fushe-Kuqe, which fact informs w, R and the K scale
fig_map      the twenty papers against the steps of the synthesis and the unknowns they inform
Every number comes from res/gar_exp.json, res/gar_rcps.json and res/gar_case.npz."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, NullLocator, FuncFormatter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'rindertimi_go'))
import rgo_model as M  # noqa: E402
from rgo_figs import Canvas, C as SC, INK, MUTED, GRID  # noqa: E402  (same visual language as RINDERTIMI-GO)

RES = os.path.join(HERE, 'res')
FS = 8.6                                   # the smallest text anywhere
plt.rcParams.update({'font.size': FS, 'axes.titlesize': 9.4, 'axes.labelsize': FS, 'xtick.labelsize': FS,
                     'ytick.labelsize': FS, 'legend.fontsize': FS, 'font.family': 'DejaVu Sans',
                     'mathtext.fontset': 'dejavusans', 'axes.edgecolor': '#8b949e', 'axes.linewidth': 0.6,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6,
                     'axes.titlelocation': 'left'})
# validated categorical slots (dataviz reference palette, light mode): blue, orange, aqua, violet; neutral reference
BLUE, ORANGE, AQUA, VIOLET, REF = '#2a78d6', '#eb6834', '#1baf7a', '#6250d6', '#8a9099'
INST = dict(Oxford=BLUE, Caltech=ORANGE, Berkeley=AQUA, MIT=VIOLET)
TG = ('eta', 'qL', 'r', 'h0', 'kappa')
SYM = dict(eta='$\\eta$', qL='$q_L$', r='$r$', h0='$h_0$', kappa='$\\kappa$')
MM = 1 / 25.4


def style(ax, grid='y'):
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(length=2.5)


def load():
    with open(os.path.join(RES, 'gar_exp.json')) as fh:
        E = json.load(fh)
    with open(os.path.join(RES, 'gar_rcps.json')) as fh:
        R = json.load(fh)
    case = dict(np.load(os.path.join(RES, 'gar_case.npz')))
    return E, R, case


# ------------------------------------------------------------------------------------------------ fig_scheme
def fig_scheme(out, E, case):
    W, H = 170, 130
    cv = Canvas(W, H)
    t = np.arange(M.NT)
    rng = np.random.default_rng(3)
    a_prior, _ = M.sample_prior(rng, 4)

    def title(x, y, s, col):
        cv.text(x, y, s, size=9.4, weight='bold', color=col)

    def inset_lines(x, y, w, h, series, cols, lw=0.8):
        a = cv.inset(x, y, w, h)
        for s, c in zip(series, cols):
            a.plot(np.arange(len(s)), s, color=c, lw=lw)
        a.axis('off')
        return a

    # ---------------- row 1: known -> prior -> simulated aquifers
    y0, h = 87, 41
    cv.box(2, y0, 54, h, SC['dat_f'], SC['dat_e'])
    title(29, y0 + h - 4.5, 'What is known', SC['dat_e'])
    a = cv.inset(6, y0 + 21.5, 46, 10.5)
    a.bar(t, case['P'], color=SC['dat_e'], width=0.8, lw=0); a.axis('off')
    cv.text(29, y0 + 17.6, 'rain $P(t)$: the only series')
    cv.text(29, y0 + 12.8, '+ a few heads (4 loggers)')
    cv.text(29, y0 + 8.2, '+ chloride facts')
    cv.text(29, y0 + 3.6, 'never seen: $\\eta,\\ q_L,\\ r,\\ h_0$', color=SC['out_e'])
    cv.box(60, y0, 54, h, SC['zoom_f'], SC['zoom_e'])
    title(87, y0 + h - 4.5, 'Physical prior $\\Pi$', SC['zoom_e'])
    cv.text(87, y0 + 30.4, '$f = k_\\tau * P$: vadose filter')
    cv.text(87, y0 + 25.6, '$r = \\kappa f + e$,  $\\kappa\\sim$ logN')
    cv.text(87, y0 + 20.8, '$\\eta,\\ q_L,\\ h_0$: Gaussian fields')
    cv.text(87, y0 + 16.0, 'dispersion width $w\\sim$ logN')
    inset_lines(64, y0 + 2.0, 46, 11, [a_prior[k, 3, 0] for k in range(3)], [SC['zoom_e'], '#7fbf8f', '#2f6b3f'])
    cv.box(118, y0, 50, h, SC['sim_f'], SC['sim_e'])
    title(143, y0 + h - 4.5, 'Simulated aquifers', SC['sim_e'])
    cv.text(143, y0 + 31.0, '$i = 1,\\dots,n$, truth known')
    for k in range(3):
        bx, by = 123 + 2.0 * k, y0 + 18.5 - 7.0 * k
        cv.box(bx, by, 36, 8.6, 'white', SC['sim_e'], lw=0.5, r=0.6, z=5 + 2 * k)
        a = cv.inset(bx + 1.2, by + 0.9, 33.6, 6.8)
        a.plot(t, a_prior[k, 1, 0], color=SC['sim_e'], lw=0.7); a.axis('off'); a.set_zorder(6 + 2 * k)
    cv.arrow(56, y0 + 21, 60, y0 + 21, lw=1.1)
    cv.arrow(114, y0 + 21, 118, y0 + 21, lw=1.1)
    # ---------------- row 2 (right to left): reconstructor -> calibrate -> field bands
    y1, h1 = 44, 39
    cv.box(118, y1, 50, h1, SC['no_f'], SC['no_e'])
    title(143, y1 + h1 - 4.5, 'One reconstructor', SC['no_e'])
    cv.text(143, y1 + 29.0, 'ensemble smoother with')
    cv.text(143, y1 + 24.4, 'the exact solver: $m_i,\\ s_i$')
    cv.text(143, y1 + 17.6, '$L_i(\\lambda)$: share of weeks')
    cv.text(143, y1 + 13.0, 'with $|g_i - m_i| > \\lambda s_i$')
    cv.text(143, y1 + 6.2, '$S_i = \\max_t\\, |g_i - m_i|/s_i$')
    cv.box(60, y1, 54, h1, SC['lik_f'], SC['lik_e'])
    title(87, y1 + h1 - 4.5, 'Calibrate', SC['lik_e'])
    cv.text(87, y1 + 29.0, 'CRC: smallest $\\lambda$ with')
    cv.text(87, y1 + 23.4, '$\\frac{n}{n+1}\\hat R_n(\\lambda) + \\frac{1}{n+1} \\leq \\alpha$')
    cv.text(87, y1 + 16.4, 'sup-norm: $\\hat q$ = the')
    cv.text(87, y1 + 11.6, '$\\lceil(1-\\alpha)(n+1)\\rceil$-th smallest $S_i$')
    cv.text(87, y1 + 4.6, 'T1: $\\hat\\lambda\\approx 2.0$,  $\\hat q\\approx 3.2$–$3.7$', color=MUTED)
    cv.box(2, y1, 54, h1, SC['out_f'], SC['out_e'])
    title(29, y1 + h1 - 4.5, 'Field case: bands', SC['out_e'])
    a = cv.inset(5, y1 + 13.2, 48, 17)
    g, m, s = case['qL_t'], case['qL_m'], case['qL_s']
    lc, lq = float(case['qL_lam_crc']), float(case['qL_lam_sup'])
    a.fill_between(t, m - lq * s, m + lq * s, color=AQUA, alpha=0.22, lw=0)
    a.fill_between(t, m - lc * s, m + lc * s, color=BLUE, alpha=0.35, lw=0)
    a.plot(t, g, color=INK, lw=0.9)
    a.set_xlim(0, M.NT - 1); a.axis('off')
    cv.text(29, y1 + 9.0, '$m \\pm \\hat\\lambda s$: E[share out] $\\leq \\alpha$', color=BLUE)
    cv.text(29, y1 + 3.8, '$m \\pm \\hat q s$: P(all in) $\\geq 1 - \\alpha$', color='#12805a')
    cv.arrow(143, y0, 143, y1 + h1, lw=1.1)
    cv.arrow(118, y1 + 21, 114, y1 + 21, lw=1.1)
    cv.arrow(60, y1 + 21, 56, y1 + 21, lw=1.1)
    cv.arrow(18, y0, 18, y1 + h1, lw=1.1)
    cv.text(19.5, (y0 + y1 + h1) / 2, 'field data', ha='left', color=MUTED)
    # ---------------- row 3: the field check and the dispersion branch
    y2, h2 = 2, 37
    cv.box(2, y2, 104, h2, '#f3f4f6', '#8b949e')
    title(54, y2 + h2 - 4.5, 'Field check before trusting the bands', INK)
    cv.text(54, y2 + 26.0, 'held-out heads: $p = (1 + |\\{i:\\ C_i \\geq C\\}|)/(n+1)$')
    cv.text(54, y2 + 19.6, 'under the prior $\\mathbb{P}(p \\leq \\alpha) \\leq \\alpha$; an alarm is a prior–data conflict')
    cv.text(54, y2 + 13.2, 'alarm → add the suspect law to the prior (delay $\\tau$), recalibrate')
    cv.text(54, y2 + 6.8, 'before the repair: $\\mathbb{E}_Q[L] \\leq \\alpha + \\mathrm{TV}$ of the residual laws')
    cv.box(110, y2, 58, h2, '#fde6ef', '#b8456f')
    title(139, y2 + h2 - 4.5, 'Dispersion: own branch', '#b8456f')
    cv.text(139, y2 + 26.0, 'rain and heads carry no')
    cv.text(139, y2 + 21.0, 'information on $w$ (Prop. 6)')
    cv.text(139, y2 + 14.0, 'chloride facts move it:')
    cv.text(139, y2 + 9.0, 'prior 7–53 m → 14–55 m (T4)')
    cv.arrow(29, y1, 29, y2 + h2, lw=1.0)
    cv.fig.savefig(os.path.join(out, 'fig_scheme.png'), dpi=300)
    plt.close(cv.fig)


# ------------------------------------------------------------------------------------------------ fig_case
def fig_case(out, E, case):
    fig, axs = plt.subplots(3, 2, figsize=(170 * MM, 140 * MM))
    t = np.arange(M.NT) + 1
    ax = axs[0, 0]
    ax.bar(t, case['P'] / 7.0, color='#a9c3e6', width=0.8, lw=0)
    ax.plot(t, case['f'], color=BLUE, lw=1.2)
    ax.set_title('(a) rain and filtered rain $f$ (mm/d)')
    ax.text(0.45, 0.95, 'bars: weekly mean rain\nline: $f = k_\\tau * P$', transform=ax.transAxes, ha='center', va='top',
            color=MUTED)
    style(ax); ax.set_xlim(0.5, M.NT + 0.5); ax.set_xlabel('week')
    panels = (('eta', axs[0, 1], '(b) sea level $\\eta(t)$ (m)'), ('qL', axs[1, 0], '(c) inland inflow $q_L(t)$ (m²/d)'),
              ('r', axs[1, 1], '(d) recharge $r(t)$ (mm/d)'),
              ('h0', axs[2, 0], '(e) initial head minus ensemble mean (m)'))
    for k, ax, ttl in panels:
        g, m, s = case[f'{k}_t'], case[f'{k}_m'], case[f'{k}_s']
        lo, hi = case[f'{k}_lo'], case[f'{k}_hi']
        lc, lq = float(case[f'{k}_lam_crc']), float(case[f'{k}_lam_sup'])
        x = t if k != 'h0' else M.XC / 1000
        off = m if k == 'h0' else 0.0
        ax.fill_between(x, m - lq * s - off, m + lq * s - off, color=AQUA, alpha=0.18, lw=0)
        ax.plot(x, m - lq * s - off, color=AQUA, lw=0.7); ax.plot(x, m + lq * s - off, color=AQUA, lw=0.7)
        ax.fill_between(x, m - lc * s - off, m + lc * s - off, color=BLUE, alpha=0.24, lw=0)
        ax.plot(x, lo - off, color=REF, lw=1.0, ls=(0, (1.2, 1.2))); ax.plot(x, hi - off, color=REF, lw=1.0, ls=(0, (1.2, 1.2)))
        ax.plot(x, m - 1.645 * s - off, color=ORANGE, lw=0.9, ls=(0, (3, 1.5)))
        ax.plot(x, m + 1.645 * s - off, color=ORANGE, lw=0.9, ls=(0, (3, 1.5)))
        ax.plot(x, g - off, color=INK, lw=1.2)
        ax.set_title(ttl); style(ax)
        if k == 'h0':
            ax.set_xlabel('distance from the sea (km)')
            for xp in M.PIEZO / 1000:
                ax.axvline(xp, color=MUTED, lw=0.6, ls=':')
            ax.text(M.PIEZO[1] / 1000 + 0.05, 0.97, 'loggers (dotted)', transform=ax.get_xaxis_transform(), va='top',
                    color=MUTED)
        else:
            ax.set_xlabel('week'); ax.set_xlim(0.5, M.NT + 0.5)
    ax = axs[2, 1]
    kt, km, ks = (float(np.ravel(case[f'kappa_{q}'])[0]) for q in ('t', 'm', 's'))
    lc = float(case['kappa_lam_crc'])
    rows = [('exact 90%', float(np.ravel(case['kappa_lo'])[0]), float(np.ravel(case['kappa_hi'])[0]), REF),
            ('raw ensemble', km - 1.645 * ks, km + 1.645 * ks, ORANGE),
            ('calibrated', km - lc * ks, km + lc * ks, BLUE)]
    for i, (lab, lo, hi, c) in enumerate(rows):
        ax.plot([lo, hi], [2 - i, 2 - i], color=c, lw=3.0, solid_capstyle='butt')
        ax.text(hi + 0.0015, 2 - i, f'{lab}', va='center', color=INK)
    ax.axvline(kt, color=INK, lw=1.2)
    ax.text(kt + 0.0008, 2.55, 'truth', ha='left', va='bottom', color=INK)
    ax.set_ylim(-0.6, 3.0); ax.set_yticks([])
    ax.set_xlim(min(r[1] for r in rows) - 0.004, max(r[2] for r in rows) + 0.02)
    ax.set_title('(f) recharge coefficient $\\kappa$'); style(ax, grid='x')
    ax.spines['left'].set_visible(False)
    handles = [Line2D([], [], color=INK, lw=1.2, label='truth'),
               Line2D([], [], color=REF, lw=1.0, ls=(0, (1.2, 1.2)), label='exact 90% band'),
               Line2D([], [], color=ORANGE, lw=0.9, ls=(0, (3, 1.5)), label='raw ensemble $\\pm 1.645 s$'),
               Patch(fc=BLUE, alpha=0.35, label='CRC band $m \\pm \\hat\\lambda s$'),
               Patch(fc=AQUA, alpha=0.3, ec=AQUA, label='sup-norm band $m \\pm \\hat q s$')]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.93), h_pad=1.0, w_pad=1.8)
    fig.savefig(os.path.join(out, 'fig_case.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ fig_t1
def fig_t1(out, E):
    T1, A, B = E['T1'], E['T1A_halfwidth'], E['T1_halfwidth']
    fig, axs = plt.subplots(1, 3, figsize=(170 * MM, 66 * MM), gridspec_kw=dict(width_ratios=[1.2, 1.2, 1.0]))
    x = np.arange(len(TG)); w = 0.27
    ax = axs[0]
    for j, (key, col) in enumerate((('exact', REF), ('raw', ORANGE), ('crc', BLUE))):
        v = [T1[k]['split']['crc_risk'] if key == 'crc' else T1[k][key]['frac_out'] for k in TG]
        ax.bar(x + (j - 1) * w, v, w * 0.9, color=col, lw=0)
    ax.text(x[-1], T1['kappa']['raw']['frac_out'] + 0.015, f"{T1['kappa']['raw']['frac_out']:.2f}", ha='center',
            va='bottom', color=INK)
    ax.axhline(0.10, color=INK, lw=0.8, ls=(0, (4, 2)))
    ax.set_xticks(x); ax.set_xticklabels([SYM[k] for k in TG])
    ax.set_ylabel('share of weeks outside'); ax.set_ylim(0, 0.78)
    ax.set_title('(a) pointwise misses'); style(ax)
    ax = axs[1]
    for j, (key, col) in enumerate((('exact', REF), ('raw', ORANGE), ('sup', AQUA))):
        v = [T1[k]['split']['sup_cover'] if key == 'sup' else T1[k][key]['simultaneous'] for k in TG]
        ax.bar(x + (j - 1) * w, v, w * 0.9, color=col, lw=0)
    ax.axhline(0.90, color=INK, lw=0.8, ls=(0, (4, 2)))
    ax.set_xticks(x); ax.set_xticklabels([SYM[k] for k in TG])
    ax.set_ylabel('P(whole function inside)'); ax.set_ylim(0, 1.05)
    ax.set_title('(b) whole function'); style(ax)
    ax = axs[2]
    ratio = [A[k]['crc'] / B[k]['crc'] for k in TG]
    y = np.arange(len(TG))[::-1]
    ax.barh(y, ratio, 0.6, color=BLUE, lw=0)
    for yy, rv in zip(y, ratio):
        ax.text(rv + 0.25, yy, f'×{rv:.1f}', va='center', color=INK)
    ax.set_yticks(y); ax.set_yticklabels([SYM[k] for k in TG])
    ax.set_xlabel('half-width ratio\n(rain only ÷ rain + 4 loggers)'); ax.set_xlim(0, max(ratio) * 1.3)
    ax.set_title('(c) what 4 loggers buy'); style(ax, grid='x')
    handles = [Patch(fc=REF, label='exact posterior'), Patch(fc=ORANGE, label='raw ensemble'),
               Patch(fc=BLUE, label='CRC (calibrated)'), Patch(fc=AQUA, label='sup-norm (calibrated)'),
               Line2D([], [], color=INK, lw=0.8, ls=(0, (4, 2)), label='target')]
    fig.legend(handles=handles, loc='upper center', ncol=5, frameon=False, bbox_to_anchor=(0.5, 1.0),
               handlelength=1.4, columnspacing=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.88), w_pad=1.4)
    fig.savefig(os.path.join(out, 'fig_t1.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ fig_t2
def fig_t2(out, E, R):
    T2 = E['T2']; ns = sorted(int(n) for n in T2)
    fig, axs = plt.subplots(1, 3, figsize=(170 * MM, 64 * MM))
    cols = dict(qL=BLUE, r=ORANGE, kappa=AQUA)
    for k, c in cols.items():
        m = [T2[str(n)][k]['crc_risk'] for n in ns]
        hi = [T2[str(n)][k]['crc_risk_p90'] for n in ns]
        axs[0].plot(ns, m, color=c, lw=1.3, marker='o', ms=3.4)
        axs[0].plot(ns, hi, color=c, lw=0.9, ls=(0, (1.5, 1.5)))
        m = [T2[str(n)][k]['sup_cover'] for n in ns]
        lo = [T2[str(n)][k]['sup_cover_p10'] for n in ns]
        axs[1].plot(ns, m, color=c, lw=1.3, marker='o', ms=3.4)
        axs[1].plot(ns, lo, color=c, lw=0.9, ls=(0, (1.5, 1.5)))
    axs[0].axhline(0.10, color=INK, lw=0.8, ls=(0, (4, 2)))
    axs[1].axhline(0.90, color=INK, lw=0.8, ls=(0, (4, 2)))
    axs[0].set_title('(a) CRC risk: mean, p90')
    axs[1].set_title('(b) sup-norm: mean, p10')
    axs[0].set_ylabel('share of weeks outside'); axs[1].set_ylabel('P(whole function inside)')
    axs[0].set_ylim(0, 0.22); axs[1].set_ylim(0.7, 1.0)
    nn = sorted(int(n) for n in R['targets']['r'])
    for k, c in cols.items():
        axs[2].plot(nn, [R['targets'][k][str(n)]['crc_ok'] for n in nn], color=c, lw=1.0, ls=(0, (3, 1.5)),
                    marker='o', ms=3.4, mfc='white')
        axs[2].plot(nn, [R['targets'][k][str(n)]['rcps_ok'] for n in nn], color=c, lw=1.3, marker='o', ms=3.4)
    axs[2].axhline(1 - R['delta'], color=INK, lw=0.8, ls=(0, (4, 2)))
    axs[2].set_ylim(0.4, 1.03); axs[2].set_ylabel('sets with risk $\\leq\\alpha$')
    axs[2].set_title('(c) one calibration set')
    for ax, xs in zip(axs, (ns, ns, nn)):
        ax.set_xscale('log'); ax.xaxis.set_major_locator(FixedLocator(xs)); ax.xaxis.set_minor_locator(NullLocator())
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f'{v:.0f}'))
        ax.set_xlabel('simulations $n$'); style(ax, grid='both')
    handles = [Line2D([], [], color=BLUE, lw=1.3, label='$q_L$'), Line2D([], [], color=ORANGE, lw=1.3, label='$r$'),
               Line2D([], [], color=AQUA, lw=1.3, label='$\\kappa$'),
               Line2D([], [], color=MUTED, lw=0.9, ls=(0, (1.5, 1.5)), label='p90 / p10'),
               Line2D([], [], color=MUTED, lw=1.0, ls=(0, (3, 1.5)), marker='o', ms=3.4, mfc='white', label='CRC'),
               Line2D([], [], color=MUTED, lw=1.3, marker='o', ms=3.4, label='RCPS, $\\delta = 0.1$')]
    fig.legend(handles=handles, loc='upper center', ncol=6, frameon=False, bbox_to_anchor=(0.5, 1.0),
               handlelength=1.6, columnspacing=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.88), w_pad=1.2)
    fig.savefig(os.path.join(out, 'fig_t2.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ fig_t3
def fig_t3(out, E):
    T1, T3 = E['T1'], E['T3']
    sets = [('under the prior', REF, dict(alarm=T3['parameters']['alarm_null'],
                                          **{k: dict(crc=T1[k]['split']['crc_risk'], sup=T1[k]['split']['sup_cover'])
                                             for k in TG})),
            ('parameter shift', BLUE, T3['parameters']), ('delay error', ORANGE, T3['delay']),
            ('delay in the prior', AQUA, T3['delay_repaired'])]
    fig, axs = plt.subplots(1, 3, figsize=(170 * MM, 64 * MM), gridspec_kw=dict(width_ratios=[0.7, 1.3, 1.3]))
    ax = axs[0]
    v = [s[2]['alarm'] for s in sets]
    ax.bar(np.arange(4), v, 0.66, color=[s[1] for s in sets], lw=0)
    for i, vv in enumerate(v):
        ax.text(i, vv + 0.015, f'{vv:.2f}', ha='center', va='bottom', color=INK)
    ax.axhline(0.10, color=INK, lw=0.8, ls=(0, (4, 2)))
    ax.set_xticks(np.arange(4)); ax.set_xticklabels(['P', 'S', 'D', 'R'])
    ax.set_ylabel('alarm rate'); ax.set_ylim(0, 0.8)
    ax.set_title('(a) field check'); style(ax)
    x = np.arange(len(TG))
    for j, (name, col, d) in enumerate(sets):
        off = (j - 1.5) * 0.18
        axs[1].plot(x + off, [d[k]['crc'] for k in TG], 'o', color=col, ms=4.6)
        axs[2].plot(x + off, [d[k]['sup'] for k in TG], 'o', color=col, ms=4.6)
        for i, k in enumerate(TG):
            axs[1].plot([i + off, i + off], [0, d[k]['crc']], color=col, lw=0.7, alpha=0.7)
    axs[1].axhline(0.10, color=INK, lw=0.8, ls=(0, (4, 2)))
    axs[2].axhline(0.90, color=INK, lw=0.8, ls=(0, (4, 2)))
    axs[1].set_ylabel('share of weeks outside'); axs[2].set_ylabel('P(whole function inside)')
    axs[1].set_title('(b) CRC risk in the field'); axs[2].set_title('(c) sup-norm in the field')
    for ax in axs[1:]:
        ax.set_xticks(x); ax.set_xticklabels([SYM[k] for k in TG]); style(ax)
    axs[1].set_ylim(0, 0.82); axs[2].set_ylim(0, 1.02)
    handles = [Patch(fc=s[1], label=f'{lab}: {s[0]}') for s, lab in zip(sets, 'PSDR')]
    fig.legend(handles=handles, loc='upper center', ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.0),
               handlelength=1.2, columnspacing=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.88), w_pad=1.2)
    fig.savefig(os.path.join(out, 'fig_t3.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ fig_t4
def fig_t4(out, E):
    T4 = E['T4']; S = T4['subsets']
    rows = [('prior', T4['w']['prior'], T4['R']['prior'], T4['eta']['prior'], REF),
            ('littoral head only', S['heads']['w'], S['heads']['R'], S['heads']['eta'], BLUE),
            ('chloride facts only', S['chloride']['w'], S['chloride']['R'], S['chloride']['eta'], ORANGE),
            ('all facts', S['all']['w'], S['all']['R'], S['all']['eta'], VIOLET),
            ('all facts, conformal', T4['w']['real_conformal'], T4['R']['real_conformal'], T4['eta']['real_conformal'],
             AQUA)]
    fig, axs = plt.subplots(1, 3, figsize=(170 * MM, 64 * MM), sharey=True,
                            gridspec_kw=dict(width_ratios=[1.0, 1.0, 0.8]))
    specs = ((1, '(a) width $w$ (m)', 1.0, [5, 10, 20, 50, 100], (5, 140)),
             (2, '(b) recharge $R$ (mm/yr)', 365.25e3, [50, 100, 200, 500], (40, 900)),
             (3, '(c) K scale $\\eta_g$', 1.0, [0.3, 0.5, 0.7, 0.9], (0.28, 0.98)))
    for ax, (j, ttl, sc, ticks, lim) in zip(axs, specs):
        for i, r in enumerate(rows):
            lo, md, hi = np.array(r[j]) * sc
            y = len(rows) - 1 - i
            ax.plot([lo, hi], [y, y], color=r[4], lw=3.0, solid_capstyle='butt')
            ax.plot([md], [y], 'o', color='white', mec=r[4], mew=1.3, ms=5.0, zorder=5)
            if j != 3:
                ax.text(hi * 1.06, y, f'{lo:.0f}–{hi:.0f}', va='center', color=INK)
        if j != 3:
            ax.set_xscale('log')
        ax.xaxis.set_major_locator(FixedLocator(ticks)); ax.xaxis.set_minor_locator(NullLocator())
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, p: f'{v:g}'))
        ax.set_xlim(*lim)
        ax.set_title(ttl); style(ax, grid='x')
        ax.set_ylim(-0.6, len(rows) - 0.4)
    axs[0].set_yticks(np.arange(len(rows))); axs[0].set_yticklabels([r[0] for r in rows][::-1])
    fig.tight_layout(w_pad=0.8)
    fig.savefig(os.path.join(out, 'fig_t4.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ fig_map
def fig_map(out, cards):
    steps = [('prior', 'prior from rain'), ('emulate', 'emulate'), ('invert', 'invert'), ('guarantee', 'guarantee'),
             ('check', 'field check'), ('design', 'design, operate')]
    unk = [('inputs', 'inputs'), ('dispersion', 'dispersion'), ('bcs', 'boundaries')]
    n = len(cards)
    W, H = 170, 170
    fig = plt.figure(figsize=(W * MM, H * MM))
    left, bottom, top = 0.50, 0.07, 0.75
    ax = fig.add_axes([left, bottom, 0.975 - left, top - bottom])
    ncol = len(steps) + len(unk)
    ax.add_patch(Rectangle((len(steps) - 0.5, -0.5), len(unk), n, fc='#f4f1fb', ec='none', zorder=0))
    for i, cd in enumerate(cards):
        y = n - 1 - i
        col = INST[cd['inst']]
        if i % 5 == 0 and i:
            ax.axhline(y + 0.5, color='#c9ced6', lw=0.6)
        for j, (key, _) in enumerate(steps):
            if key in cd['steps']:
                ax.plot(j, y, 'o', color=col, ms=6.6, zorder=3)
            else:
                ax.plot(j, y, 'o', color='#e1e4e8', ms=2.4, zorder=2)
        for jj, (key, _) in enumerate(unk):
            j = len(steps) + jj
            lvl = cd['informs'].get(key, 0)
            if lvl == 2:
                ax.plot(j, y, 's', color=col, ms=6.2, zorder=3)
            elif lvl == 1:
                ax.plot(j, y, 's', color='white', mec=col, mew=1.3, ms=5.8, zorder=3)
            else:
                ax.plot(j, y, 's', color='#e1e4e8', ms=2.4, zorder=2)
        ax.text(-0.75, y, f"{cd['id']}  {cd['short']}", ha='right', va='center', color=INK, clip_on=False)
    ax.set_xlim(-0.6, ncol - 0.4); ax.set_ylim(-0.6, n - 0.4)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    for j, (_, lab) in enumerate(steps + unk):
        ax.text(j, n - 0.15, lab, ha='center', va='bottom', rotation=90, color=INK if j < len(steps) else '#4a3a8a',
                clip_on=False)
    ax.plot([-0.4, len(steps) - 0.6], [-1.0, -1.0], color=MUTED, lw=0.8, clip_on=False)
    ax.plot([len(steps) - 0.4, ncol - 0.6], [-1.0, -1.0], color='#4a3a8a', lw=0.8, clip_on=False)
    ax.text((len(steps) - 1) / 2, -1.25, 'step of the synthesis', ha='center', va='top', color=MUTED, clip_on=False)
    ax.text(len(steps) + 1, -1.25, 'what it informs', ha='center', va='top', color='#4a3a8a', clip_on=False)
    x0 = 0.02
    for inst, col in INST.items():
        fig.text(x0, 0.975, '\u25cf', color=col, fontsize=FS + 1.5, va='center')
        fig.text(x0 + 0.022, 0.975, inst, color=INK, va='center')
        x0 += 0.11
    fig.text(0.02, 0.945, '\u25a0 direct lesson   \u25a1 indirect lesson   \u25cf the step it serves', color=MUTED,
             va='center')
    fig.savefig(os.path.join(out, 'fig_map.png'), dpi=300)
    plt.close(fig)


def main(out, cards=None):
    os.makedirs(out, exist_ok=True)
    E, R, case = load()
    fig_scheme(out, E, case)
    fig_case(out, E, case)
    fig_t1(out, E)
    fig_t2(out, E, R)
    fig_t3(out, E)
    fig_t4(out, E)
    if cards is None:
        from cards_gar import CARDS as cards
    fig_map(out, cards)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, 'figs'))
