"""Figure 8 (KAUZ-OED step 4: adaptive switchback pumping tests on the linear aquifer) from
results/switchback_ou.json (sim_switchback_ou.py)."""
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from common import OI, INK, MUTED, RULE, MM, RES, panel, save, mc_band

J = json.load(open(os.path.join(RES, 'switchback_ou.json')))
I = J['info']
TAU0 = I['tau0_main']; AR = I['aR']; KMAX = I['K']
C = dict(naive=OI['vermillion'], arx=OI['orange'], ipw=OI['blue'], aw=OI['green'], cs=OI['purple'], na=OI['sky'])
SHORT = dict(naive='naiv', arx='ARX', ipw='IPW', aw='AW')
EST = ('naive', 'arx', 'ipw', 'aw')


def broken_marks(ax_top, ax_bot, d=0.012):
    kw = dict(color=RULE, clip_on=False, lw=0.7)
    ax_top.plot((-d, +d), (-2 * d, +2 * d), transform=ax_top.transAxes, **kw)
    ax_bot.plot((-d, +d), (1 - 4 * d, 1 + 4 * d), transform=ax_bot.transAxes, **kw)


def panel_a(fig, spec):
    gs = GridSpecFromSubplotSpec(2, 2, subplot_spec=spec, width_ratios=[2.0, 1], height_ratios=[1.35, 1],
                                 hspace=0.12, wspace=0.3)
    P = J['seasonal']['path']
    Y = np.array(P['Y']); U = np.array(P['U']); PI = np.array(P['PI']); S = np.array(P['season'])
    kk = np.arange(1, len(Y) + 1); n_show = 144
    sl = slice(0, n_show)
    on = U[sl] == 1
    # a1: outcomes
    ax = fig.add_subplot(gs[0, 0])
    lev = np.mean(Y) - np.mean(S)
    ax.vlines(kk[sl][on], -3, 4, color=OI['vermillion'], alpha=0.08, lw=1.6, zorder=0)
    ax.plot(kk[sl], (S + lev)[sl], color=MUTED, lw=0.9, zorder=1)
    ax.plot(kk[sl][on], Y[sl][on], 'o', ms=2.5, color=OI['vermillion'], mec='white', mew=0.3, zorder=3)
    ax.plot(kk[sl][~on], Y[sl][~on], 'o', ms=2.5, color=OI['blue'], mec='white', mew=0.3, zorder=3)
    lo, hi = Y[sl].min(), Y[sl].max()
    ax.set_ylim(lo - 0.1, hi + 0.5 * (hi - lo))
    ax.set_xlim(0, n_show + 1)
    ax.set_ylabel('kripësia $Y_k$')
    ax.tick_params(labelbottom=False)
    hs = [Line2D([], [], marker='o', ls='', ms=3, color=OI['vermillion'], mec='white', mew=0.3),
          Line2D([], [], marker='o', ls='', ms=3, color=OI['blue'], mec='white', mew=0.3),
          Line2D([], [], color=MUTED, lw=0.9)]
    ax.legend(hs, ['pompim, $U_k=1$', 'pa pompim, $U_k=0$', 'cikli sezonal i natyrës (12 periudha)'],
              loc='upper left', ncol=3, fontsize=5.9, handlelength=1.4, columnspacing=1.2, borderaxespad=0.2)
    ax.set_title('Një eksperiment adaptiv i realizuar (natyrë sezonale, $b=30$, $\\ell=50$, $\\pi_{\\min}=0.1$)',
                 color=INK)
    panel(ax, 'a', x=-0.085, y=1.03)
    # a2: assignment probabilities
    ax = fig.add_subplot(gs[1, 0])
    ax.step(kk[sl], PI[sl], where='mid', color=OI['blue'], lw=1.0)
    ax.vlines(kk[sl][on], -0.14, -0.04, color=OI['vermillion'], lw=0.9)
    ax.axhline(0.1, color=RULE, lw=0.6, ls='--'); ax.axhline(0.9, color=RULE, lw=0.6, ls='--')
    ax.axhline(0.5, color=RULE, lw=0.5, ls=':')
    ax.set_ylim(-0.17, 1.3); ax.set_yticks([0.1, 0.5, 0.9]); ax.set_yticklabels(['0.1', '0.5', '0.9'])
    ax.set_xlim(0, n_show + 1)
    ax.set_xlabel('periudha $k$'); ax.set_ylabel('$\\pi_k$')
    hs = [Line2D([], [], color=OI['blue'], lw=1.0),
          Line2D([], [], color=OI['vermillion'], lw=0.9, marker='|', ls='', ms=4),
          Line2D([], [], color=RULE, lw=0.6, ls='--')]
    ax.legend(hs, ['$\\pi_k=P(U_k=1\\mid\\mathcal{F}_{k-1})$: Thompson + kripësia e fundit', 'pompim',
                   '$\\pi_{\\min}$, $1-\\pi_{\\min}$'],
              loc='upper left', ncol=3, fontsize=5.9, handlelength=1.4, columnspacing=1.2, borderaxespad=0.2)
    # a3: running estimates over the whole experiment
    ax = fig.add_subplot(gs[:, 1])
    t = np.arange(1, KMAX + 1); est = np.array(P['est']); se = np.array(P['se']); cs = np.array(P['cs'])
    nv = np.array(P['naive_run']); t0 = 20; m = t >= t0
    ax.fill_between(t[m], (est - cs)[m], (est + cs)[m], color=OI['purple'], alpha=0.16, lw=0)
    ax.fill_between(t[m], (est - 1.96 * se)[m], (est + 1.96 * se)[m], color=OI['blue'], alpha=0.18, lw=0)
    ax.plot(t[m], est[m], color=OI['blue'], lw=1.0)
    ax.plot(t[m], nv[m], color=OI['vermillion'], lw=1.0)
    ax.axhline(TAU0, color=INK, lw=0.8, ls='--')
    ax.set_xscale('log'); ax.set_xlim(t0, KMAX)
    ylo = (est - cs)[m].min(); yhi = (est + cs)[m].max()
    ax.set_ylim(ylo - 0.62 * (yhi - ylo), yhi + 0.04)
    ax.set_xticks([20, 50, 100, 200, 400]); ax.set_xticklabels(['20', '50', '100', '200', '400']); ax.minorticks_off()
    ax.set_xlabel('periudha $t$ (nga $t=20$)'); ax.set_ylabel('vlerësimi vijues i $\\bar\\tau_t$')
    ax.set_title('Vlerësimi vijues, i njëjti eksperiment', color=INK)
    hs = [Line2D([], [], color=OI['blue'], lw=1.0), Patch(color=OI['blue'], alpha=0.3, lw=0),
          Patch(color=OI['purple'], alpha=0.25, lw=0), Line2D([], [], color=OI['vermillion'], lw=1.0),
          Line2D([], [], color=INK, lw=0.8, ls='--')]
    ax.legend(hs, ['IPW $\\hat{\\bar\\tau}_t$', 'Wald 95 % ($t$ fiks)', 'SB 95 % (uniforme)',
                   'diferenca naive', '$\\bar\\tau_t=\\tau_0$'], loc='lower right', fontsize=5.6, ncol=2,
              handlelength=1.3, columnspacing=0.9, borderaxespad=0.3)


def panel_b(fig, spec):
    ax = fig.add_subplot(spec)
    groups = (('main', 'nonadaptive', 'natyrë stacionare'), ('seasonal', 'seasonal_na', 'natyrë sezonale'))
    ypos = []; labels = []; y = 0; heads = []
    for gi, (key, keyna, gname) in enumerate(groups):
        F = J[key]['fixed'][str(KMAX)]; Fna = J[keyna]['fixed'][str(KMAX)]
        heads.append((y + 0.75, gname))
        rows = [(F[e]['draws'], C[e], SHORT[e]) for e in EST]
        rows.append((Fna['naive']['draws'], C['na'], 'naiv, $\\pi_k=1/2$'))
        for v, c, lab in rows:
            v = np.asarray(v, float)
            vp = ax.violinplot([v], positions=[y], orientation='horizontal', widths=0.82, showextrema=False)
            for b in vp['bodies']:
                b.set_facecolor(c); b.set_edgecolor(c); b.set_alpha(0.32); b.set_linewidth(0.6)
            q1, q3 = np.quantile(v, [0.25, 0.75])
            ax.plot([q1, q3], [y, y], color=c, lw=1.6, solid_capstyle='butt')
            ax.plot([v.mean()], [y], 'o', ms=2.6, color='white', mec=c, mew=0.9, zorder=4)
            ypos.append(y); labels.append(lab); y -= 1
        if gi == 0:
            ax.axhline(y + 0.4, color=RULE, lw=0.6)
            y -= 0.9
    ax.axvline(TAU0, color=INK, lw=0.9, zorder=0)
    ax.axvline(AR, color=MUTED, lw=0.8, ls='--', zorder=0)
    for yh, txt in heads:
        ax.text(-0.015, yh, txt, ha='left', va='center', fontsize=6.0, color=MUTED, style='italic')
    ax.set_yticks(ypos); ax.set_yticklabels(labels, fontsize=6.0)
    ax.tick_params(axis='y', length=0)
    ax.set_ylim(y + 0.45, 1.75)
    ax.set_xlim(-0.02, 0.5)
    ax.grid(axis='y', visible=False)
    ax.text(TAU0 - 0.006, 1.42, '$\\tau_0$', ha='right', va='center', fontsize=6.4, color=INK)
    ax.text(AR + 0.006, 1.42, '$aR_{gp}$', ha='left', va='center', fontsize=6.4, color=MUTED)
    Fs = J['seasonal']['fixed'][str(KMAX)]['naive']
    bias = Fs['mean'] - TAU0
    ax.text(0.497, heads[1][0], f"{bias:+.3f} ({100 * bias / TAU0:+.0f} %)".replace('-', '−'),
            ha='right', va='center', fontsize=5.5, color=OI['vermillion'])
    ax.set_xlabel('vlerësimi i efektit në $K=400$')
    ax.set_title('Shpërndarja e vlerësuesve', color=INK)
    panel(ax, 'b', x=-0.42)


def panel_c(fig, spec):
    gs = GridSpecFromSubplotSpec(2, 1, subplot_spec=spec, height_ratios=[2.0, 1.25], hspace=0.07)
    at = fig.add_subplot(gs[0]); ab = fig.add_subplot(gs[1], sharex=at)
    Ks = sorted(int(k) for k in J['main']['fixed'])
    for key, ls, mk in (('main', '-', 'o'), ('seasonal', '--', 's')):
        R = J[key]['R']
        for e in EST:
            c = np.array([J[key]['fixed'][str(k)][e]['cov'] for k in Ks]); lo, hi = mc_band(c, R)
            for ax in (at, ab):
                ax.fill_between(Ks, lo, hi, color=C[e], alpha=0.12, lw=0)
                ax.plot(Ks, c, ls, color=C[e], marker=mk, ms=2.3, lw=1.0, mfc='white' if key == 'seasonal' else C[e],
                        mew=0.8)
    for ax in (at, ab):
        ax.axhline(0.95, color=MUTED, lw=0.7, ls=':')
        ax.set_xscale('log'); ax.minorticks_off()
    at.set_ylim(0.88, 0.985); ab.set_ylim(0.28, 0.88)
    at.set_yticks([0.9, 0.95]); ab.set_yticks([0.4, 0.6, 0.8])
    at.spines['bottom'].set_visible(False); at.tick_params(axis='x', length=0, labelbottom=False)
    broken_marks(at, ab)
    ab.set_xticks(Ks); ab.set_xticklabels([str(k) for k in Ks])
    ab.set_xlabel('numri i periudhave $K$')
    at.set_ylabel('mbulimi (nominal 0.95)')
    at.yaxis.set_label_coords(-0.2, 0.25)
    at.set_title('Mbulimi i intervaleve me $K$ fiks', color=INK)
    hs = [Line2D([], [], color=C[e], lw=1.2) for e in EST]
    hs += [Line2D([], [], color=MUTED, lw=1.0, ls='-', marker='o', ms=2.3),
           Line2D([], [], color=MUTED, lw=1.0, ls='--', marker='s', ms=2.3, mfc='white')]
    ab.legend(hs, ['naiv', 'ARX', 'IPW', 'AW', 'stacionare', 'sezonale'], loc='lower left', fontsize=5.5, ncol=3,
              handlelength=1.6, columnspacing=0.7, borderaxespad=0.2, labelspacing=0.3)
    panel(at, 'c', x=-0.27, y=1.045)


def panel_d(fig, spec):
    ax = fig.add_subplot(spec)
    t = np.arange(1, KMAX + 1); t0 = I['t0']; m = t >= t0
    sty = dict(wald=(OI['blue'], '-', 'Wald IPW në çdo $t$'), wald_aw=(OI['green'], '-', 'Wald AW në çdo $t$'),
               cs=(OI['purple'], '-', 'SB IPW'), cs_aw=(OI['purple'], '-.', 'SB AW'))
    for key in ('main', 'seasonal'):
        R = J[key]['R']
        for k in ('wald', 'wald_aw', 'cs', 'cs_aw'):
            if key == 'seasonal' and k in ('wald_aw', 'cs_aw'):
                continue
            c, ls, lab = sty[k]
            p = np.array(J[key]['ever'][k]); lo, hi = mc_band(p, R)
            if key == 'main':
                ax.fill_between(t[m], lo[m], hi[m], color=c, alpha=0.13, lw=0)
                ax.plot(t[m], p[m], color=c, lw=1.1, ls=ls)
            else:
                ax.plot(t[m], p[m], color=c, lw=0.9, ls=(0, (3, 1.6)), alpha=0.9)
    ax.axhline(0.05, color=MUTED, lw=0.7, ls=':')
    ax.text(13, 0.044, '$\\alpha=0.05$', fontsize=5.8, color=MUTED, va='top')
    ax.set_xscale('log'); ax.set_xlim(t0, KMAX); ax.set_ylim(0, 0.48)
    ax.set_xticks([10, 20, 50, 100, 200, 400]); ax.set_xticklabels(['10', '20', '50', '100', '200', '400'])
    ax.minorticks_off()
    ax.set_xlabel('periudha $t$'); ax.set_ylabel('$P(\\exists s\\leq t:\\ \\bar\\tau_s\\notin C_s)$')
    ax.set_title('Shikimi i vazhdueshëm i të dhënave', color=INK)
    hs = [Line2D([], [], color=sty[k][0], ls=sty[k][1], lw=1.1) for k in ('wald', 'wald_aw', 'cs', 'cs_aw')]
    hs.append(Line2D([], [], color=MUTED, ls=(0, (3, 1.6)), lw=0.9))
    ax.legend(hs, [sty[k][2] for k in ('wald', 'wald_aw', 'cs', 'cs_aw')] + ['natyrë sezonale'],
              loc='upper left', fontsize=5.6, handlelength=1.6, borderaxespad=0.2)
    panel(ax, 'd', x=-0.25)


def panel_e(fig, spec):
    gs = GridSpecFromSubplotSpec(2, 1, subplot_spec=spec, height_ratios=[2.0, 1.25], hspace=0.1)
    at = fig.add_subplot(gs[0]); ab = fig.add_subplot(gs[1], sharex=at)
    S = J['pimin_sweep']; pm = np.array(sorted(float(k) for k in S)); keys = [f'{p:g}' for p in pm]
    R = S[keys[0]].get('R', 1000)
    sty = dict(cs=(OI['purple'], '-', 'o', 'SB IPW'), cs_aw=(OI['purple'], '-.', 'D', 'SB AW'),
               wald=(OI['blue'], '-', 'o', 'Wald IPW'), wald_aw=(OI['green'], '-', 's', 'Wald AW'))
    for k, (c, ls, mk, lab) in sty.items():
        mu = np.array([S[q]['hw']['at_K'][k]['mean'] for q in keys])
        qq = np.array([S[q]['hw']['at_K'][k]['q'] for q in keys])
        if k in ('cs', 'wald'):
            at.fill_between(pm, qq[:, 1], qq[:, 3], color=c, alpha=0.13, lw=0)
        at.plot(pm, mu, ls=ls, marker=mk, ms=2.4, color=c, lw=1.1, label=lab)
    nv = np.array([S[q]['fixed'][str(KMAX)]['naive']['hw'] for q in keys])
    at.plot(pm, nv, ls=':', marker='v', ms=2.4, color=OI['vermillion'], lw=1.0, label='Welch naiv (pa garanci)')
    at.set_xscale('log')
    tk = [0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]
    at.set_xticks(tk); at.set_xticklabels([f'{p:g}' for p in tk]); at.minorticks_off()
    at.tick_params(labelbottom=False)
    at.set_ylabel('gjysmë-gjerësia')
    at.text(0.012, 0.325, '$K=400$', fontsize=6.0, color=MUTED, va='top')
    at.set_title('Gjerësia dhe mungesa kundrejt $\\pi_{\\min}$ (propozimi N1)', color=INK)
    at.legend(loc='upper right', fontsize=5.6, ncol=2, handlelength=1.6, columnspacing=1.0)
    at.set_ylim(0, 0.34)
    # validity strip
    for k, c, ls, lab in (('cs', OI['purple'], '-', 'SB IPW: $P(\\exists t\\leq 400$: mungesë$)$'),
                          ('cs_aw', OI['purple'], '-.', 'SB AW'),
                          ('wald', OI['blue'], '-', 'Wald IPW: $1-$mbulimi, $K=400$')):
        if k == 'wald':
            p = np.array([1 - S[q]['fixed'][str(KMAX)]['ipw']['cov'] for q in keys])
        else:
            p = np.array([S[q]['ever'][k] for q in keys])
        lo, hi = mc_band(p, R)
        if k != 'cs_aw':
            ab.fill_between(pm, lo, hi, color=c, alpha=0.13, lw=0)
        ab.plot(pm, p, ls=ls, marker='o' if k != 'cs_aw' else 'D', ms=2.2, color=c, lw=1.0, label=lab)
    ab.axhline(0.05, color=MUTED, lw=0.7, ls=':')
    ab.set_ylim(0, 0.24); ab.set_yticks([0, 0.05, 0.1, 0.2])
    ab.set_ylabel('mungesa')
    ab.set_xlabel('$\\pi_{\\min}$ (0.5 = switchback jo-adaptiv)')
    ab.legend(loc='upper right', fontsize=5.4, handlelength=1.6, borderaxespad=0.1, labelspacing=0.25)
    for ax in (at, ab):
        ax.yaxis.set_label_coords(-0.105, 0.5)
    panel(at, 'e', x=-0.15, y=1.04)


def panel_f(fig, spec):
    gs = GridSpecFromSubplotSpec(2, 1, subplot_spec=spec, height_ratios=[2.0, 1.25], hspace=0.1)
    at = fig.add_subplot(gs[0]); ab = fig.add_subplot(gs[1], sharex=at)
    bg = np.array(I['b_grid']); tb = np.array(I['tau0_b']) / AR
    at.fill_between(bg, tb, 1, color=OI['sky'], alpha=0.2, lw=0)
    at.plot(bg, tb, color=INK, lw=1.3)
    at.axhline(1, color=MUTED, lw=0.8, ls='--')
    B = J['b_sweep']; bs = np.array(sorted(float(k) for k in B)); keys = [f'{b:g}' for b in bs]
    tz = np.array([B[k]['tau0'] for k in keys])
    at.plot(bs, tz / AR, 'D', ms=3.4, mfc='white', mec=INK, mew=0.8, zorder=5)
    tr = 1 / abs(I['slowest_eig'])
    off = dict(naive=-0.9, arx=-0.3, ipw=0.3, aw=0.9)
    for e in EST:
        mu = np.array([B[k]['fixed'][e]['mean'] for k in keys])
        se = np.array([B[k]['fixed'][e]['sd'] / np.sqrt(B[k].get('R', 1000)) for k in keys])
        ab.errorbar(bs + off[e], 100 * (mu - tz) / AR, yerr=196 * se / AR, fmt='o-', ms=2.2, lw=0.8, color=C[e],
                    elinewidth=0.7, capsize=0, label=SHORT[e])
    bm = I['b_main']
    for ax in (at, ab):
        ax.axvline(bm, color=RULE, lw=0.7, ls=':')
    at.text(bm + 0.7, 1.035, 'zgjedhja $b=30$', fontsize=5.8, color=MUTED, va='bottom')
    at.text(0.3, 0.975, 'mbartja\n$1-\\tau_0/(aR_{gp})$', fontsize=5.8, color=OI['blue'], ha='left',
            va='top')
    at.set_ylim(0, 1.13); at.set_xlim(-2, 61)
    at.tick_params(labelbottom=False)
    at.set_ylabel('$\\tau_0(b)\\,/\\,(aR_{gp})$')
    at.set_title(f'Efekti lag-0 kundrejt $aR_{{gp}}$ (koha e relaksimit $1/|\\lambda_{{\\max}}|={tr:.1f}$)',
                 color=INK)
    hs = [Line2D([], [], color=INK, lw=1.3), Line2D([], [], marker='D', ls='', ms=3.4, mfc='white', mec=INK, mew=0.8)]
    at.legend(hs, ['$\\tau_0(b)$ analitik (nga $A$)', 'simulim i degëzuar me zhurmë të përbashkët'],
              loc='lower right', fontsize=5.6, handlelength=1.4)
    ab.axhline(0, color=MUTED, lw=0.7)
    ab.set_ylim(-4.5, 9.5)
    ab.set_ylabel('zhvendosja\n(% e $aR_{gp}$)')
    ab.set_xlabel('koha e pritjes $b$ para matjes (dritarja $w=20$, $\\ell=b+w$)')
    ab.legend(loc='upper right', fontsize=5.5, ncol=4, handlelength=1.4, columnspacing=0.9, borderaxespad=0.2)
    for ax in (at, ab):
        ax.yaxis.set_label_coords(-0.105, 0.5)
    panel(at, 'f', x=-0.14, y=1.04)


def main():
    fig = plt.figure(figsize=(178 * MM, 180 * MM))
    gs = GridSpec(3, 1, figure=fig, height_ratios=[1.05, 1, 1], hspace=0.42, left=0.075, right=0.985, top=0.965,
                  bottom=0.06)
    panel_a(fig, gs[0])
    g1 = GridSpecFromSubplotSpec(1, 3, subplot_spec=gs[1], wspace=0.52, width_ratios=[1.05, 1, 1])
    panel_b(fig, g1[0]); panel_c(fig, g1[1]); panel_d(fig, g1[2])
    g2 = GridSpecFromSubplotSpec(1, 2, subplot_spec=gs[2], wspace=0.24)
    panel_e(fig, g2[0]); panel_f(fig, g2[1])
    save(fig, 'fig8_switchback_aquifer')


if __name__ == '__main__':
    main()
    print('ok')
