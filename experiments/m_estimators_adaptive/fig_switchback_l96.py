"""Figure 9 (KAUZ-OED under chaos): adaptive switchback "pumping" tests on Lorenz-96.
Reads results/switchback_l96.json (sim_switchback_l96.py). Run: python3 fig_switchback_l96.py
"""
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from scipy.stats import norm

from common import OI, INK, MUTED, RULE, GRID, MM, RES, panel, save, mc_band

SRC = os.environ.get('SRC', 'switchback_l96.json')
J = json.load(open(os.path.join(RES, SRC)))
S = J['setting']; REF = J['ref']
C_NAIVE, C_AW, C_HAJ, C_IPW = OI['vermillion'], OI['blue'], OI['purple'], OI['green']
C_FDT, C_REG = OI['orange'], MUTED
C_B = {'0.0': OI['sky'], '0.5': OI['blue'], '1.0': '#123f66'}
CMAP = LinearSegmentedColormap.from_list('bwv', ['#0b5d99', '#5aa6d6', '#f4f6f8', '#eea270', '#c14f05'])
TWO_R, TWO_FDT, TWO_REG = REF['two_delta_R'], REF['two_delta_fdt'], REF['two_delta_reg']


def logticks(ax, kmax):
    t = [k for k in (20, 50, 100, 200, 500, 1000, 2000, 5000) if k <= kmax * 1.001]
    ax.set_xticks(t); ax.set_xticklabels([str(k) for k in t]); ax.xaxis.set_minor_formatter(plt.NullFormatter())


def sqrt_scale(ax):
    ax.set_yscale('function', functions=(lambda v: np.sqrt(np.clip(v, 0, None)), lambda v: v ** 2))


def panel_a(fig, spec):
    H = J['A']['hov']; ell, b = S['ell'], S['burn']
    X = np.array(H['x']); x3cf = np.array(H['x3cf']); s = np.array(H['s']); nper = H['periods']
    dts = 0.05; T = nper * ell
    t = (np.arange(X.shape[0]) + 1) * dts
    sub = GridSpecFromSubplotSpec(3, 1, subplot_spec=spec, height_ratios=[0.16, 1.0, 0.72], hspace=0.12)
    a0 = fig.add_subplot(sub[0]); a1 = fig.add_subplot(sub[1], sharex=a0); a2 = fig.add_subplot(sub[2], sharex=a0)
    # schedule strip
    for k in range(nper):
        col = OI['green'] if s[k] == 1 else '#d9dde1'
        a0.add_patch(Rectangle((k * ell, 0), b, 1, facecolor=col, alpha=0.35, lw=0))
        a0.add_patch(Rectangle((k * ell + b, 0), ell - b, 1, facecolor=col, alpha=0.95, lw=0))
        a0.text(k * ell + (ell + b) / 2, 0.5, '$+1$' if s[k] == 1 else '$-1$', ha='center', va='center', fontsize=5.6,
                color='white' if s[k] == 1 else INK)
    a0.set_ylim(0, 1); a0.set_yticks([]); a0.grid(False)
    for sp in a0.spines.values():
        sp.set_visible(False)
    a0.tick_params(axis='x', labelbottom=False, length=0)
    a0.text(-0.012, 0.5, '$s_k$', transform=a0.transAxes, ha='right', va='center', fontsize=7.0, color=INK)
    a0.set_title('Switchback në L96: forcim $F_0=F+\\Delta s_k$ në nyjen $p=0$', color=INK, pad=3)
    panel(a0, 'a', x=-0.135, y=1.25)
    # Hovmoller
    te = np.concatenate([[0], t])
    ne = np.arange(-0.5, 20.5, 1.0)
    vc = 2.3
    pm = a1.pcolormesh(te, ne, X.T, cmap=CMAP, norm=TwoSlopeNorm(vmin=-6.5, vcenter=vc, vmax=11.0),
                       shading='flat', rasterized=True)
    for k in range(1, nper):
        a1.axvline(k * ell, color='white', lw=0.7)
    for yy in (0, 3):
        a1.axhline(yy, color=INK, lw=0.35, alpha=0.35, ls=(0, (2, 2)))
    a1.set_yticks([0, 3, 10, 19]); a1.set_yticklabels(['$p=0$', '$g=3$', '10', '19'])
    a1.set_ylabel('nyja $i$', labelpad=1)
    a1.grid(False); a1.tick_params(axis='x', labelbottom=False)
    a1.set_ylim(-0.5, 19.5)
    cax = a1.inset_axes([1.012, 0.0, 0.022, 1.0])
    cb = fig.colorbar(pm, cax=cax, extend='both')
    cb.outline.set_edgecolor(RULE); cb.outline.set_linewidth(0.4); cb.ax.tick_params(labelsize=5.6, length=1.5, width=0.4)
    cb.ax.set_title('$x_i$', fontsize=6.2, pad=2, color=INK)
    cb.set_ticks([-5, 0, 2.3, 5, 10]); cb.set_ticklabels(['\u22125', '0', '2.3', '5', '10'])
    # x_3: realised and counterfactual branch, period means
    x3 = X[:, 3]
    a2.plot(t, x3, color=INK, lw=0.7, label='dega e realizuar')
    for k in range(nper):
        i0 = int(round(k * ell / dts)); i1 = int(round((k + 1) * ell / dts))
        tt = np.concatenate([[k * ell], t[i0:i1]])
        start = x3[i0 - 1] if i0 > 0 else np.nan
        cf = np.concatenate([[start], x3cf[i0:i1]])
        a2.plot(tt, cf, color=C_FDT, lw=0.65, ls=(0, (2.2, 1.2)), label='dega kundërfaktike' if k == 0 else None)
        ib = i0 + int(round(b / dts))
        yr = x3[ib:i1].mean(); yc = x3cf[ib:i1].mean()
        a2.plot([k * ell + b, (k + 1) * ell], [yr, yr], color=INK, lw=1.5, solid_capstyle='butt')
        a2.plot([k * ell + b, (k + 1) * ell], [yc, yc], color=C_FDT, lw=1.5, solid_capstyle='butt')
        a2.axvline(k * ell, color=RULE, lw=0.5)
    a2.set_xlim(0, T); a2.set_ylim(-9, 25)
    a2.set_yticks([-5, 0, 5, 10]); a2.set_yticklabels(['\u22125', '0', '5', '10'])
    a2.set_xlabel('koha $t$ (njësi L96)', labelpad=1); a2.set_ylabel('$x_3$', labelpad=1)
    h = [Line2D([], [], color=INK, lw=0.7), Line2D([], [], color=C_FDT, lw=0.65, ls=(0, (2.2, 1.2))),
         Line2D([], [], color=MUTED, lw=1.5)]
    a2.legend(h, ['dega e realizuar', 'dega kundërfaktike', '$Y_k(\\pm 1)$: mesatarja pas $b$'], loc='upper center',
              ncol=3, fontsize=5.3, handlelength=1.6, columnspacing=1.0, borderaxespad=0.1, bbox_to_anchor=(0.5, 1.02))
    return a0


def panel_b(ax):
    B = J['B']; H = B['tau_hist']; e = np.array(H['edges']); c = np.array(H['counts'])
    d = c / (H['n'] * np.diff(e))
    ax.stairs(d, e, fill=True, color=OI['sky'], alpha=0.28, lw=0)
    ax.stairs(d, e, color=OI['blue'], lw=0.9)
    st = B['tau_stats']
    xx = np.linspace(-5, 5, 400)
    ax.plot(xx, norm.pdf(xx, st['mean'], st['sd']), color=MUTED, lw=0.7, ls=(0, (1, 1.2)))
    ymax = 0.62
    lines = [(st['mean'], INK, '-', 1.1), (TWO_R, INK, (0, (3, 1.6)), 0.9), (TWO_FDT, C_FDT, '-.', 1.0),
             (TWO_REG, C_REG, ':', 1.1)]
    for v, col, ls, lw in lines:
        ax.plot([v, v], [0, 0.36], color=col, ls=ls, lw=lw)
    ax.set_xlim(-5, 5); ax.set_ylim(0, ymax)
    ax.set_xlabel('$\\tau_k=Y_k(+1)-Y_k(-1)$  ($\\pi_k=1/2$, $\\ell=5$, $b=1$)')
    ax.set_ylabel('dendësia')
    ax.set_title('Efektet në nivel periudhe nën kaos', color=INK)
    h = [Line2D([], [], color=INK, lw=1.1), Line2D([], [], color=INK, lw=0.9, ls=(0, (3, 1.6))),
         Line2D([], [], color=C_FDT, lw=1.0, ls='-.'), Line2D([], [], color=C_REG, lw=1.1, ls=':'),
         Line2D([], [], color=MUTED, lw=0.7, ls=(0, (1, 1.2)))]
    ax.legend(h, ['$\\mathbb{E}[\\tau_k]$ (switchback)', '$2\\Delta R$ (forcim konstant)', '$2\\Delta R_{\\rm FDT}$',
                  '$2\\Delta\\times$ regresioni', 'normale me të njëjtat momente'],
              loc='upper right', fontsize=5.3, handlelength=1.8, borderaxespad=0.1, bbox_to_anchor=(1.02, 1.02))
    ax.text(0.985, 0.50, f"d.s.$(\\tau_k)$ = {st['sd']:.2f}\n$P(\\tau_k<0)$ = {st['frac_neg']:.2f}",
            transform=ax.transAxes, ha='right', va='top', fontsize=5.6, color=INK, linespacing=1.3)
    # inset: the four numbers with uncertainty
    ins = ax.inset_axes([0.15, 0.62, 0.26, 0.33])
    vals = [(st['mean'], 1.96 * st['se'], INK, 'o', 'switchback'), (TWO_R, 1.96 * 2 * REF['R_direct_se'], INK, 'D', '$2\\Delta R$'),
            (TWO_FDT, None, C_FDT, 's', 'FDT'), (TWO_REG, None, C_REG, 'v', 'regres.')]
    for i, (v, ci, col, mk, lab) in enumerate(vals):
        y = 3 - i
        if ci is not None:
            ins.plot([v - ci, v + ci], [y, y], color=col, lw=1.0)
        ins.plot(v, y, marker=mk, color=col, ms=2.8, mfc=col if i != 1 else 'white', mew=0.8, ls='none')
    ins.axvline(0, color=RULE, lw=0.5)
    ins.set_yticks([3, 2, 1, 0]); ins.set_yticklabels([v[4] for v in vals], fontsize=5.0)
    ins.set_xlim(-0.36, 0.45); ins.set_ylim(-0.6, 3.6)
    ins.set_xticks([-0.2, 0, 0.2, 0.4]); ins.set_xticklabels(['\u22120.2', '0', '0.2', '0.4'])
    ins.tick_params(labelsize=5.0, length=1.5, pad=1)
    ins.grid(True, axis='x', color=GRID, lw=0.4); ins.grid(False, axis='y')
    ins.set_facecolor('white')
    for sp in ('top', 'right'):
        ins.spines[sp].set_visible(False)
    ins.set_title(f"$\\times${TWO_FDT / st['mean']:.1f} (FDT)", fontsize=5.2, color=C_FDT, pad=1.5, loc='right')
    panel(ax, 'b')


def panel_c(ax):
    tr = J['A']['trace']; K = np.arange(1, len(tr['ipw']) + 1); m = K >= S['K0']
    ipw = np.array(tr['ipw']); hw = np.array(tr['hw_cs']); hww = np.array(tr['hw_w'])
    ax.fill_between(K[m], (ipw - hw)[m], (ipw + hw)[m], color=C_IPW, alpha=0.16, lw=0)
    ax.plot(K[m], (ipw - hww)[m], color=C_IPW, lw=0.6, ls=(0, (2.5, 1.5)))
    ax.plot(K[m], (ipw + hww)[m], color=C_IPW, lw=0.6, ls=(0, (2.5, 1.5)))
    ax.plot(K[m], np.array(tr['naive'])[m], color=C_NAIVE, lw=0.7, alpha=0.9)
    ax.plot(K[m], ipw[m], color=C_IPW, lw=1.1)
    ax.plot(K[m], np.array(tr['taubar'])[m], color=INK, lw=1.0)
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.axhline(TWO_R, color=INK, lw=0.7, ls=(0, (3, 1.6)))
    ax.axhline(TWO_FDT, color=C_FDT, lw=0.9, ls='-.')
    ax.axhline(TWO_REG, color=C_REG, lw=0.9, ls=':')
    fe = tr['first_excl_cs']
    if fe > 0:
        lo = ipw[fe - 1] - hw[fe - 1]
        ax.plot([fe], [lo], marker='o', ms=3.2, color=C_IPW, mfc='white', mew=0.9, zorder=5)
    ax.set_xscale('log'); ax.set_xlim(S['K0'], len(ipw)); ax.set_ylim(-1.0, 1.62)
    logticks(ax, len(ipw))
    ax.set_xlabel('numri i periudhave $K$'); ax.set_ylabel('efekti i $\\pm\\Delta$ në $x_3$')
    ax.set_title('Një eksperiment adaptiv: SB asimptotike 95%', color=INK)
    h = [Line2D([], [], color=C_IPW, lw=1.1), (Rectangle((0, 0), 1, 1, color=C_IPW, alpha=0.16, lw=0)),
         Line2D([], [], color=C_IPW, lw=0.6, ls=(0, (2.5, 1.5))), Line2D([], [], color=INK, lw=1.0),
         Line2D([], [], color=C_NAIVE, lw=0.7)]
    hx = Line2D([], [], color=C_IPW, marker='o', ms=3.2, mfc='white', mew=0.9, ls='none')
    l1 = ax.legend(h[:3] + [hx], ['IPW $\\hat\\tau_K$', 'SB 95% (e vlefshme në çdo $K$)', 'Wald 95% ($K$ fikse)',
                                  f'SB përjashton 0 në $K={fe}$'],
                   loc='upper right', fontsize=5.3, handlelength=1.6, borderaxespad=0.1)
    ax.add_artist(l1)
    ax.legend([h[3], h[4]], ['$\\bar\\tau_K$ (e vërteta, nga degëzimi)', 'diferenca naive e mesatareve'],
              loc='lower right', fontsize=5.3, handlelength=1.6, borderaxespad=0.1)
    tr_ = ax.get_yaxis_transform()
    for v, lab, col in ((TWO_FDT, '$2\\Delta R_{\\rm FDT}$', C_FDT), (TWO_R, '$2\\Delta R$', INK),
                        (TWO_REG, 'regres.', C_REG)):
        ax.text(1.012, v, lab, transform=tr_, fontsize=5.4, color=col, ha='left', va='center', clip_on=False)
    panel(ax, 'c')


def panel_d(ax):
    for cfg, ls in (('A', '-'), ('C', (0, (1.2, 1.0)))):
        X = J[cfg]; g = np.array(X['grid']); Rr = X['R']
        series = [(X['ever_miss']['cs'], C_IPW), (X['ever_miss']['wald_peek'], INK),
                  (X['miss']['naive'], C_NAIVE), (X['miss']['aw'], C_AW)]
        for p, col in series:
            p = np.array(p); lo, hi = mc_band(p, Rr)
            ax.fill_between(g, lo, hi, color=col, alpha=0.10, lw=0)
            ax.plot(g, p, color=col, lw=1.1, ls=ls)
    ax.axhline(0.05, color=MUTED, lw=0.6, ls='--')
    ax.text(0.99, 0.05, '$\\alpha=0.05$', fontsize=5.6, color=MUTED, va='bottom', ha='right',
            transform=ax.get_yaxis_transform())
    sqrt_scale(ax)
    ax.set_ylim(0, 1.0); ax.set_yticks([0, 0.01, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0', '0.01', '0.05', '0.1', '0.2', '0.4', '0.6', '0.8', '1'])
    kmx = max(J['A']['grid'][-1], J['C']['grid'][-1])
    ax.set_xscale('log'); ax.set_xlim(S['K0'], kmx); logticks(ax, kmx)
    ax.set_xlabel('numri i periudhave $K$'); ax.set_ylabel('shkalla e gabimit (shkallë $\\sqrt{\\cdot}$)')
    ax.set_title('Mbulimi i $\\bar\\tau_K$: në çdo $K$ dhe me $K$ fikse', color=INK)
    h1 = [Line2D([], [], color=C_IPW, lw=1.1), Line2D([], [], color=INK, lw=1.1),
          Line2D([], [], color=C_NAIVE, lw=1.1), Line2D([], [], color=C_AW, lw=1.1),
          Line2D([], [], color=MUTED, lw=1.1), Line2D([], [], color=MUTED, lw=1.1, ls=(0, (1.2, 1.0)))]
    ax.legend(h1, ['SB (IPW): gabim në ndonjë $K\'\\leq K$', 'Wald (IPW) i parë në çdo $K$',
                   'naiv (Welch), $K$ fikse', 'AW $W_k$ (sanduiç), $K$ fikse',
                   'A: adaptiv, stacionar', 'C: adaptiv + sezonë'],
              loc='upper left', fontsize=5.2, handlelength=1.8, borderaxespad=0.1, bbox_to_anchor=(0.0, 1.02))
    panel(ax, 'd')


def panel_e(ax):
    ests = [('naive', 'naiv', C_NAIVE), ('aw', 'AW, $W_k$', C_AW), ('hajek', 'Hájek, $W_k^2$', C_HAJ),
            ('ipw', 'IPW + bazë', C_IPW), ('ipw_h', 'IPW-$h_k$', OI['sky'])]
    cfgs = [('A', 0.17, 'o'), ('C', -0.17, 's')]
    yt, yl = [], []
    for i, (e, lab, col) in enumerate(ests):
        y0 = len(ests) - 1 - i
        yt.append(y0); yl.append(lab)
        for cfg, dy, mk in cfgs:
            X = J[cfg]; v = np.array(X['dist_err_common'][e]); Kc = X['dist_err_common_K']
            q05, q25, q50, q75, q95 = np.quantile(v, [0.05, 0.25, 0.5, 0.75, 0.95])
            y = y0 + dy
            ax.plot([q05, q95], [y, y], color=col, lw=0.7, alpha=0.8)
            ax.add_patch(Rectangle((q25, y - 0.09), q75 - q25, 0.18, facecolor=col, alpha=0.18 if cfg == 'A' else 0.32,
                                   edgecolor=col, lw=0.6))
            mu = v.mean(); se = v.std() / np.sqrt(v.size)
            ax.plot([mu - 1.96 * se, mu + 1.96 * se], [y, y], color=INK, lw=1.4, solid_capstyle='butt')
            ax.plot(mu, y, marker=mk, ms=3.0, color=col, mfc='white' if cfg == 'C' else col, mew=0.9, ls='none', zorder=5)
            if str(Kc) in X['fixedK']:
                cov = X['fixedK'][str(Kc)][e]['cover']
                ax.text(0.405, y, f'{cov:.2f}', fontsize=5.3, color=col, va='center', ha='left')
    ax.plot([0, 0], [-0.55, 4.45], color=MUTED, lw=0.6, zorder=1)
    ax.set_yticks(yt); ax.set_yticklabels(yl)
    ax.set_xlim(-0.45, 0.47); ax.set_ylim(-0.55, 5.6)
    ax.grid(False, axis='y')
    ax.text(0.405, 4.66, 'mbulimi\nWald 95%', fontsize=5.0, color=MUTED, ha='left', va='center', linespacing=1.1)
    Kc = J['A']['dist_err_common_K']
    ax.set_xlabel(f'gabimi $\\hat\\tau_K-\\bar\\tau_K$ në $K={Kc}$ ({J["A"]["R"]} përsëritje)')
    ax.set_title('Zhvendosja: vlerësuesi naiv kundrejt IPW', color=INK)
    h = [Line2D([], [], color=MUTED, marker='o', ms=3.0, ls='none'),
         Line2D([], [], color=MUTED, marker='s', ms=3.0, mfc='white', ls='none'),
         Line2D([], [], color=INK, lw=1.4)]
    ax.legend(h, ['A: adaptiv, stacionar', 'C: adaptiv + sezonë', 'mes. $\\pm$ 1.96 g.s. MC'], loc='upper left',
              ncol=3, fontsize=5.2, handlelength=1.3, columnspacing=0.9, borderaxespad=0.1, bbox_to_anchor=(0.0, 1.01))
    panel(ax, 'e')


def panel_f(ax):
    st = J['step']['curves']; V = J['valid']['points']
    for bkey, col in C_B.items():
        c = st[bkey]; ell = np.array(c['ell']); m = np.array(c['mean']); se = np.array(c['se'])
        ax.fill_between(ell, m - 1.96 * se, m + 1.96 * se, color=col, alpha=0.18, lw=0)
        ax.plot(ell, m, color=col, lw=1.2)
        ax.plot(ell, np.array(c['fdt']), color=col, lw=0.9, ls=(0, (3, 1.5)))
        pts = [(float(e), d[bkey]) for e, d in V.items() if bkey in d]
        if bkey in J['B']['Yb']:
            pts.append((S['ell'], J['B']['Yb'][bkey]))
        for e, d in pts:
            ax.errorbar(e, d['mean'], yerr=1.96 * d['se'], fmt='o', ms=2.6, color=col, mfc='white', mew=0.8,
                        elinewidth=0.8, capsize=1.2, zorder=5)
    ax.axhline(TWO_R, color=INK, lw=0.7, ls=(0, (3, 1.6)))
    ax.axhline(TWO_FDT, color=C_FDT, lw=0.9, ls='-.')
    ax.axhline(TWO_REG, color=C_REG, lw=0.9, ls=':')
    ax.axhline(0, color=RULE, lw=0.5)
    ax.text(0.105, TWO_R + 0.012, f'$2\\Delta R={TWO_R:.3f}$', fontsize=5.6, color=INK, va='bottom')
    ax.text(0.105, TWO_FDT + 0.012, f'$2\\Delta R_{{\\rm FDT}}={TWO_FDT:.3f}$', fontsize=5.6, color=C_FDT, va='bottom')
    ax.text(0.105, TWO_REG + 0.012, f'regresion: ${TWO_REG:.3f}$', fontsize=5.6, color=C_REG, va='bottom')
    ax.annotate('dizajni\nkryesor', xy=(S['ell'], J['B']['Yb']['1.0']['mean']), xytext=(5.0, 0.235), fontsize=5.4,
                color=INK, ha='center', arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.5))
    ax.set_xscale('log'); ax.set_xlim(0.1, 10); ax.set_ylim(-0.31, 0.45)
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 5, 10]); ax.set_xticklabels(['0.1', '0.2', '0.5', '1', '2', '5', '10'])
    ax.set_xlabel('gjatësia e periudhës $\\ell$'); ax.set_ylabel('$\\mathbb{E}[\\tau_k]$')
    ax.set_title('Nga përgjigja kalimtare te ajo e qëndrueshme', color=INK)
    h = [Line2D([], [], color=C_B[k], lw=1.2) for k in C_B] + \
        [Line2D([], [], color=MUTED, lw=0.9, ls=(0, (3, 1.5))), Line2D([], [], color=MUTED, marker='o', mfc='white', ms=2.6, ls='none')]
    ax.legend(h, ['$b=0$', '$b=0.5$', '$b=1$', 'parashikimi FDT', 'switchback i drejtpërdrejtë'], loc='lower right',
              fontsize=5.3, handlelength=1.6, ncol=2, columnspacing=0.8, borderaxespad=0.1, bbox_to_anchor=(1.0, 0.1))
    panel(ax, 'f')


def main():
    fig = plt.figure(figsize=(178 * MM, 172 * MM))
    gs = GridSpec(3, 2, figure=fig, hspace=0.52, wspace=0.30, left=0.075, right=0.975, top=0.955, bottom=0.055,
                  height_ratios=[1.12, 1, 1])
    panel_a(fig, gs[0, 0])
    panel_b(fig.add_subplot(gs[0, 1]))
    panel_c(fig.add_subplot(gs[1, 0]))
    panel_d(fig.add_subplot(gs[1, 1]))
    panel_e(fig.add_subplot(gs[2, 0]))
    panel_f(fig.add_subplot(gs[2, 1]))
    if SRC == 'switchback_l96.json':
        save(fig, 'fig9_switchback_chaos')
    else:   # development preview outside the repository
        fig.savefig(os.environ['PREVIEW'], dpi=400, bbox_inches='tight', pad_inches=0.04); plt.close(fig)


if __name__ == '__main__':
    main()
