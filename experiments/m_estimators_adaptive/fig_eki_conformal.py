"""Figure for proposal N4 (EKI + conformal calibration) from results/eki_conformal.json (sim_eki_conformal.py)."""
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from scipy.stats import beta as beta_dist, gaussian_kde

from common import OI, INK, MUTED, RULE, MM, RES, panel, save

J = json.load(open(os.environ.get('EKI_JSON', os.path.join(RES, 'eki_conformal.json'))))
ST = J['setting']; PT = {k: np.array(v) for k, v in J['per_truth'].items()}; EX = J['example']
R = ST['R']; NX, NY = ST['NX'], ST['NY']; LX, LY = ST['LX'] / 1000, ST['LY'] / 1000
XC = np.array(J['grid']['xc']) / 1000; YC = np.array(J['grid']['yc']) / 1000
SIG = ST['sigma']; Z90 = 1.6448536269514722
CMAP = LinearSegmentedColormap.from_list('sand_blue', ['#f7f3e6', '#e6dcbc', '#b5d3dc', '#5ea7d3', '#2a6fae', '#1d4f86'])
C = dict(ens=OI['vermillion'], esmda=OI['purple'], sc=OI['blue'], scn=OI['green'])
LBL = dict(ens='ansambli\nTEKI', esmda='ansambli\nES-MDA', sc='konformal\n$|y-\\hat h|$', scn='konformal\ni normalizuar')
NAME = os.environ.get('EKI_FIG', 'fig7_n4_eki_conformal')


def grid2(v):
    return np.asarray(v).reshape(NX, NY).T          # (NY, NX) for imshow / contour


def se(v):
    v = np.asarray(v, float)
    return v.std(ddof=1) / np.sqrt(len(v))


def panel_a(ax, cax):
    lk = grid2(np.array(EX['logK']) / np.log(10))
    im = ax.imshow(lk, origin='lower', extent=(0, LX, 0, LY), cmap=CMAP, vmin=np.quantile(lk, 0.01),
                   vmax=np.quantile(lk, 0.995), interpolation='nearest', aspect='equal', zorder=0)
    xs = np.linspace(0, LX, 400)
    yc = (EX['y0'] + ST['ch_amp'] * np.sin(2 * np.pi * xs * 1000 / ST['ch_lambda'] + EX['phi'])) / 1000
    hw = ST['ch_halfwidth'] / 1000
    for sgn in (-1, 1):
        ax.plot(xs, yc + sgn * hw, color='white', lw=0.7, ls=(0, (3, 1.5)), zorder=2)
    # heads of the truth
    hh = grid2(EX['h'])
    xg = np.unique(XC); yg = np.unique(YC)
    cs = ax.contour(xg, yg, hh, levels=[2, 4, 6, 8], colors=INK, linewidths=0.45, alpha=0.55, zorder=1)
    ax.clabel(cs, fmt=lambda v: f'{v:.0f} m', fontsize=5.0, inline=True, inline_spacing=1)
    # zones
    for xb in ST['zone_xbreaks']:
        ax.plot([xb / 1000] * 2, [0, LY], color=INK, lw=0.6, ls='--', alpha=0.7, zorder=2)
    ax.plot([0, LX], [LY / 2] * 2, color=INK, lw=0.6, ls='--', alpha=0.7, zorder=2)
    xb = [0] + [v / 1000 for v in ST['zone_xbreaks']] + [LX]
    k = 1
    for i in range(3):
        for j in range(2):
            ax.text(xb[i + 1] - 0.06, (j + 1) * LY / 2 - 0.07, f'Z{k}', ha='right', va='top', fontsize=5.6,
                    color=INK, bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.75), zorder=4)
            k += 1
    # piezometers
    f = np.array(EX['fit']); c = np.array(EX['cal']); t = np.array(EX['test'])
    ax.scatter(XC[f], YC[f], marker='^', s=13, c=OI['orange'], edgecolors=INK, linewidths=0.4, zorder=5)
    ax.scatter(XC[c], YC[c], marker='o', s=11, c=OI['purple'], edgecolors='white', linewidths=0.5, zorder=5)
    ax.scatter(XC[t], YC[t], marker='s', s=8, c='white', edgecolors=INK, linewidths=0.5, zorder=5)
    # sea strip
    ax.add_patch(Rectangle((-0.16, 0), 0.16, LY, color=OI['sky'], alpha=0.55, lw=0, clip_on=False, zorder=0))
    ax.text(-0.08, LY / 2, 'deti,  $h=0$', rotation=90, ha='center', va='center', fontsize=5.6, color=INK)
    ax.add_patch(Rectangle((LX, 0), 0.16, LY, color=OI['green'], alpha=0.30, lw=0, clip_on=False, zorder=0))
    ax.text(LX + 0.08, LY / 2, f"brendësia, $h={ST['h_in']:.0f}$ m", rotation=90, ha='center', va='center',
            fontsize=5.6, color=INK)
    ich = int(np.argmax(yc)); xl = xs[ich]
    ax.text(xl, yc[ich] + hw + 0.04, 'paleokanali', fontsize=5.6, color=INK, ha='center', va='bottom', zorder=6,
            bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.8))
    ax.set_xlim(-0.16, LX + 0.16); ax.set_ylim(0, LY)
    ax.set_xticks([0, 1, 2, 3, 4]); ax.set_yticks([0, 1, 2])
    ax.set_xlabel('largësia nga bregu $x$ [km]'); ax.set_ylabel('$y$ [km]')
    ax.grid(False)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(True)
    cb = plt.colorbar(im, cax=cax)
    cb.set_label('$\\log_{10}K$ [m/d]', fontsize=6.4); cb.ax.tick_params(labelsize=5.8); cb.outline.set_edgecolor(RULE)
    h = [Line2D([], [], marker='^', ls='', ms=4, mfc=OI['orange'], mec=INK, mew=0.4,
                label=f"përshtatja e TEKI ({ST['n_fit']})"),
         Line2D([], [], marker='o', ls='', ms=3.8, mfc=OI['purple'], mec='white', mew=0.5,
                label=f"kalibrimi konformal ({ST['n_cal']})"),
         Line2D([], [], marker='s', ls='', ms=3.2, mfc='white', mec=INK, mew=0.5, label=f"test ({ST['n_test_show']})"),
         Line2D([], [], color=INK, lw=0.6, ls='--', label='zonat e modelit')]
    ax.legend(handles=h, loc='lower left', bbox_to_anchor=(-0.04, 0.995), ncol=4, fontsize=5.5, handletextpad=0.25,
              columnspacing=0.8, borderaxespad=0.2, handlelength=1.4)
    ax.set_title('Akuiferi i vërtetë (një realizim) dhe rrjeti i piezometrave', color=INK, pad=13)


def panel_b(ax):
    it = np.arange(ST['n_iter'] + 1)
    for key, col, ls, lab in (('misfit', OI['vermillion'], '-', 'mospërputhja $\\|y-\\bar G\\|^2/(m\\sigma^2)$'),
                              ('dspread', OI['blue'], '-', 'përhapja $\\mathrm{tr}\\,C^{GG}/(m\\sigma^2)$')):
        for suf, lsx in (('', '-'), ('_mda', (0, (3, 1.6)))):
            v = PT[key + suf]
            med = np.median(v, 0); lo = np.quantile(v, 0.1, 0); hi = np.quantile(v, 0.9, 0)
            if suf == '':
                ax.fill_between(it, lo, hi, color=col, alpha=0.13, lw=0)
            ax.plot(it, med, color=col, lw=1.2 if suf == '' else 0.9, ls=lsx,
                    label=lab if suf == '' else None)
    ax.axhline(1, color=MUTED, lw=0.7, ls=':')
    ax.text(10, 1.25, 'niveli i zhurmës', fontsize=5.6, color=MUTED, ha='right', va='bottom')
    ax.set_yscale('log'); ax.set_xlim(0, ST['n_iter']); ax.set_xticks(it[::2]); ax.set_ylim(2e-3, 2e4)
    ax.set_xlabel('iteracioni $n$'); ax.set_ylabel('vlera pa njësi (mediana, 10–90%)', labelpad=1)
    ax.set_title('TEKI: mospërputhja ngec, ansambli shembet', color=INK)
    h, l = ax.get_legend_handles_labels()
    h += [Line2D([], [], color=MUTED, lw=1.2, ls='-'), Line2D([], [], color=MUTED, lw=0.9, ls=(0, (3, 1.6)))]
    l += ['TEKI (100 anëtarë)', 'ES-MDA (krahasim)']
    ax.legend(h, l, loc='lower left', fontsize=5.4, handlelength=1.8, borderaxespad=0.3)
    mf = np.median(PT['misfit'][:, -1]); sp = np.median(PT['dspread'][:, -1])
    ax.annotate(f'$\\chi^2/m\\approx{mf:.0f}$', xy=(ST['n_iter'], mf), xytext=(7.4, mf * 6), fontsize=5.8,
                color=OI['vermillion'], arrowprops=dict(arrowstyle='-', color=OI['vermillion'], lw=0.5))
    ax.annotate(f'{sp:.3f}', xy=(ST['n_iter'], sp), xytext=(8.3, sp * 0.2), fontsize=5.8, color=OI['blue'],
                ha='center', va='top', arrowprops=dict(arrowstyle='-', color=OI['blue'], lw=0.5))


def panel_c(ax):
    t = np.array(EX['test']); yt = np.array(EX['ytest'])
    mu = np.array(EX['mu']); sde = np.array(EX['sd_e']); s = np.array(EX['s'])
    h = np.array(EX['h'])
    q_sc = EX['q0']['sc']; q_scn = EX['q0']['scn']
    o = np.argsort(h[t]); t = t[o]; yt = yt[o]
    xh = h[t]; res = yt - mu[t]
    xs = np.arange(len(t))
    ax.axhspan(-q_sc, q_sc, color=C['sc'], alpha=0.12, lw=0)
    ax.axhline(q_sc, color=C['sc'], lw=0.7); ax.axhline(-q_sc, color=C['sc'], lw=0.7)
    ax.axhline(0, color=RULE, lw=0.6)
    w_n = q_scn * sde[t]; w_e = Z90 * s[t]
    ax.vlines(xs + 0.18, -w_n, w_n, color=C['scn'], lw=1.6, alpha=0.85)
    ax.vlines(xs - 0.18, -w_e, w_e, color=C['ens'], lw=1.6)
    cov_e = np.abs(res) <= w_e; cov_s = np.abs(res) <= q_sc; cov_n = np.abs(res) <= w_n
    ax.scatter(xs, res, s=9, c=INK, zorder=4, lw=0)
    ax.set_xticks(xs[::5]); ax.set_xticklabels([f'{v:.1f}' for v in xh[::5]])
    ax.set_xlabel('koka e vërtetë $h(x)$ në piezometrat test [m] (renditur)')
    ax.set_ylabel('$y-\\hat h_{\\rm TEKI}(x)$ [m]')
    lim = max(np.abs(res).max(), q_sc, w_n.max()) * 1.18
    ax.set_ylim(-lim, lim * 1.38); ax.set_xlim(-0.8, len(t) - 0.2)
    ax.grid(axis='x', visible=False)
    h_ = [Line2D([], [], color=C['ens'], lw=1.6, label=f'ansambli: {cov_e.sum()}/{len(t)} të mbuluara'),
          Rectangle((0, 0), 1, 1, fc=C['sc'], alpha=0.25, ec=C['sc'], lw=0.7,
                    label=f'konformal: {cov_s.sum()}/{len(t)}'),
          Line2D([], [], color=C['scn'], lw=1.6, label=f'konformal i normalizuar: {cov_n.sum()}/{len(t)}'),
          Line2D([], [], marker='o', ls='', ms=2.8, mfc=INK, mec='none', label='mbetja e vëzhguar')]
    ax.legend(handles=h_, loc='upper left', ncol=2, fontsize=5.4, handlelength=1.4, columnspacing=1.0)
    ax.set_title('Një akuifer: intervalet 90% në 30 piezometra test', color=INK)


def violin(ax, x, v, col, c, side=0.0, alpha=0.25, grid=None):
    grid = np.linspace(0, 1, 400) if grid is None else grid
    v = np.asarray(v, float)
    d = gaussian_kde(v, bw_method=0.25)(grid)
    m = d > 1e-3 * d.max()
    ax.fill_betweenx(grid[m], x - c * d[m], x + c * d[m], color=col, alpha=alpha, lw=0)
    ax.plot(x - c * d[m], grid[m], color=col, lw=0.6); ax.plot(x + c * d[m], grid[m], color=col, lw=0.6)


def panel_d(ax):
    keys = [('ens', PT['cov_ens']), ('esmda', PT['cov_esmda']), ('sc', PT['cov_sc_1']), ('scn', PT['cov_scn_1'])]
    grid = np.linspace(0, 1, 500)
    dens = [gaussian_kde(v, bw_method=0.25)(grid).max() for _, v in keys]
    a, b = int(np.ceil((ST['n_cal'] + 1) * (1 - ST['alpha']))), ST['n_cal'] + 1 - int(np.ceil((ST['n_cal'] + 1) * (1 - ST['alpha'])))
    bmax = beta_dist(a, b).pdf(grid).max()
    c = 0.36 / max(max(dens), bmax)
    for i, (k, v) in enumerate(keys):
        violin(ax, i, v, C[k], c, grid=grid)
        m, e = v.mean(), 1.96 * se(v)
        ax.errorbar(i, m, yerr=e, fmt='o', ms=3.2, color=C[k], mec='white', mew=0.5, elinewidth=1.0, capsize=1.6,
                    zorder=5)
        if k in ('ens', 'esmda'):
            ax.text(i, v.max() + 0.03, f'{m:.3f}', fontsize=5.6, color=C[k], ha='center', va='bottom', zorder=6)
        else:
            ax.text(i, 0.62, f'{m:.3f}', fontsize=5.6, color=C[k], ha='center', va='top', zorder=6)
        if k in ('sc', 'scn'):
            bd = beta_dist(a, b).pdf(grid); mm = bd > 1e-3 * bd.max()
            ax.plot(i - c * bd[mm], grid[mm], color=INK, lw=0.6, ls=(0, (2, 1.2)))
            ax.plot(i + c * bd[mm], grid[mm], color=INK, lw=0.6, ls=(0, (2, 1.2)))
            va = PT[f'cov_{k}_avg']
            rng = np.random.default_rng(i)
            ax.scatter(i + 0.43 + 0.05 * rng.standard_normal(len(va)), va, s=1.2, color=INK, alpha=0.35, lw=0,
                       zorder=3)
    ax.axhline(1 - ST['alpha'], color=MUTED, lw=0.7, ls='--')
    ax.text(-0.45, 0.915, '$1-\\alpha=0.90$', fontsize=5.6, color=MUTED, va='bottom')
    ax.set_xticks(range(4)); ax.set_xticklabels([LBL[k] for k, _ in keys], fontsize=6.0)
    ax.set_xlim(-0.55, 3.65); ax.set_ylim(0, 1.02)
    ax.set_ylabel('mbulimi në një akuifer')
    ax.grid(axis='x', visible=False)
    h_ = [Line2D([], [], color=INK, lw=0.6, ls=(0, (2, 1.2)), label=f'teoria: Beta$({a},{b})$ (1 set kalibrimi)'),
          Line2D([], [], marker='o', ls='', ms=1.8, mfc=INK, mec='none', alpha=0.6,
                 label=f"mesatarja mbi {ST['K_draws']} sete kalibrimi"),
          Line2D([], [], marker='o', ls='-', ms=3, color=MUTED, mec='white', label='mesatarja $\\pm$ 1.96 GS (MC)')]
    ax.legend(handles=h_, loc='lower right', bbox_to_anchor=(1.0, 0.02), fontsize=5.4, handlelength=1.6)
    ax.set_title(f'Mbulimi mbi {R} akuiferë të vërtetë', color=INK)


def panel_e(ax):
    keys = ['ens', 'esmda', 'sc', 'scn']
    vals = dict(ens=PT['wid_ens'], esmda=PT['wid_esmda'], sc=PT['wid_sc_avg'], scn=PT['wid_scn_avg'])
    lg = np.linspace(np.log10(0.05), np.log10(200), 600)
    dens = {k: gaussian_kde(np.log10(vals[k]), bw_method=0.25)(lg) for k in keys}
    for i, k in enumerate(keys):
        d = dens[k]; m = d > 2e-3 * d.max(); c = 0.3 / d.max()
        ax.fill_betweenx(10 ** lg[m], i - c * d[m], i + c * d[m], color=C[k], alpha=0.25, lw=0)
        ax.plot(i - c * d[m], 10 ** lg[m], color=C[k], lw=0.6); ax.plot(i + c * d[m], 10 ** lg[m], color=C[k], lw=0.6)
        md = np.median(vals[k])
        ax.plot([i - 0.3, i + 0.3], [md, md], color=C[k], lw=1.4)
        ax.text(i + 0.33, md, f'{md:.2f} m', fontsize=5.6, color=C[k], va='center', ha='left')
    w0 = 2 * Z90 * SIG
    ax.axhline(w0, color=MUTED, lw=0.7, ls=':')
    ax.text(3.6, w0 * 0.82, f'vetëm zhurma: $2\\cdot1.645\\,\\sigma$ = {w0:.3f} m', fontsize=5.4, color=MUTED,
            ha='right', va='top')
    ax.set_yscale('log'); ax.set_ylim(0.05, 200); ax.set_xlim(-0.55, 3.85)
    ax.set_xticks(range(4)); ax.set_xticklabels([LBL[k] for k in keys], fontsize=6.0)
    ax.set_ylabel('gjerësia mesatare [m]')
    ax.grid(axis='x', visible=False)
    ax.set_title('Çmimi i vlefshmërisë: gjerësia', color=INK)
    # inset: coverage by distance from the coast
    ins = ax.inset_axes([0.07, 0.62, 0.36, 0.33])
    xb = np.array(ST['xbands']) / 1000; xm = 0.5 * (xb[1:] + xb[:-1])
    for k in ('sc', 'scn'):
        v = PT[f'band_{k}']
        m = v.mean(0); e = 1.96 * v.std(0, ddof=1) / np.sqrt(R)
        ins.fill_between(xm, m - e, m + e, color=C[k], alpha=0.2, lw=0)
        ins.plot(xm, m, color=C[k], lw=1.0, marker='o', ms=2.0)
    ins.axhline(0.9, color=MUTED, lw=0.6, ls='--')
    ins.set_xlim(0, 4); ins.set_xticks([0, 2, 4]); ins.tick_params(labelsize=5.0, length=1.5, pad=1)
    ins.set_xlabel('$x$ [km]', fontsize=5.2, labelpad=0.5)
    ins.set_title('mbulimi sipas largësisë nga bregu', fontsize=5.3, color=MUTED, loc='left', pad=2)
    ins.grid(True, lw=0.4)


def panel_f(ax, axb):
    ns = list(ST['n_cal_clust'])
    sty = dict(u=(OI['vermillion'], '-', 'o'), w=(OI['blue'], '-', 'o'), un=(OI['vermillion'], (0, (3, 1.5)), 's'),
               wn=(OI['blue'], (0, (3, 1.5)), 's'))
    lo_all, hi_all = 1.0, 0.0
    for k, (col, ls, mk) in sty.items():
        m = np.array([PT[f'cl{n}_cov_{k}_avg'].mean() for n in ns])
        e = np.array([1.96 * se(PT[f'cl{n}_cov_{k}_avg']) for n in ns])
        lo_all = min(lo_all, (m - e).min()); hi_all = max(hi_all, (m + e).max())
        ax.fill_between(ns, m - e, m + e, color=col, alpha=0.18, lw=0)
        ax.plot(ns, m, color=col, ls=ls, lw=1.2, marker=mk, ms=2.6, mec='white', mew=0.3)
        ax.text(ns[-1] * 1.08, m[-1], f'{m[-1]:.3f}', fontsize=5.4, color=col, va='center', ha='left')
    ax.axhline(0.9, color=MUTED, lw=0.7, ls='--')
    ax.text(ns[0] * 0.86, 0.9 + 0.004, '$1-\\alpha$', fontsize=5.4, color=MUTED, va='bottom', ha='left')
    ax.set_xscale('log'); ax.set_xticks(ns); ax.set_xticklabels([]); ax.minorticks_off()
    ax.set_xlim(ns[0] * 0.8, ns[-1] * 1.5)
    span = hi_all - lo_all
    ax.set_ylim(lo_all - 0.62 * span, hi_all + 0.06 * span)
    ax.set_ylabel('mbulimi marxhinal')
    h_ = [Line2D([], [], color=OI['vermillion'], lw=1.4, label='pa pesha'),
          Line2D([], [], color=OI['blue'], lw=1.4, label='me pesha $w=p_{\\rm test}/q$'),
          Line2D([], [], color=MUTED, lw=1.0, ls='-', marker='o', ms=2.4, label='rezultati $|y-\\hat h|$'),
          Line2D([], [], color=MUTED, lw=1.0, ls=(0, (3, 1.5)), marker='s', ms=2.4,
                 label='rezultati $|y-\\hat h|/s_{\\rm ens}$')]
    ax.legend(handles=h_, loc='lower left', ncol=2, fontsize=5.3, handlelength=2.0, columnspacing=1.0,
              borderaxespad=0.3, title='kalibrimi $\\sim q(x)\\propto e^{-x/1\\,{\\rm km}}$, testi uniform',
              title_fontsize=5.4, alignment='left')
    ax.set_title('Kalibrim i grumbulluar pranë bregut', color=INK)
    inf = np.array([PT[f'cl{n}_inf_w_avg'].mean() for n in ns])
    ess = np.array([PT[f'cl{n}_ess'].mean() for n in ns])
    axb.bar(ns, inf, width=np.array(ns) * 0.28, color=OI['blue'], alpha=0.35, edgecolor=OI['blue'], lw=0.6)
    for n, fi, es in zip(ns, inf, ess):
        axb.text(n, fi + 0.03, f'{100 * fi:.0f}%', fontsize=5.4, color=OI['blue'], ha='center', va='bottom')
    axb.set_xscale('log'); axb.set_xticks(ns)
    axb.set_xticklabels([f'{n}\n(ESS {es:.0f})' for n, es in zip(ns, ess)], fontsize=5.8)
    axb.minorticks_off()
    axb.set_xlim(ns[0] * 0.8, ns[-1] * 1.5); axb.set_ylim(0, max(0.62, inf.max() * 1.45))
    axb.set_yticks([0, 0.25, 0.5]); axb.set_yticklabels(['0', '25%', '50%'])
    axb.set_ylabel('$\\infty$-intervale', fontsize=6.2)
    axb.set_xlabel('numri i piezometrave të kalibrimit $n$')
    axb.grid(axis='x', visible=False)


def main():
    fig = plt.figure(figsize=(178 * MM, 178 * MM))
    gs = GridSpec(3, 1, figure=fig, hspace=0.5, left=0.075, right=0.985, top=0.935, bottom=0.065,
                  height_ratios=[1.1, 1.0, 1.0])
    top = gs[0].subgridspec(1, 3, width_ratios=[1.0, 0.03, 0.62], wspace=0.06)
    ax = fig.add_subplot(top[0, 0]); cax = fig.add_subplot(top[0, 1])
    panel_a(ax, cax); panel(ax, 'a', x=-0.1, y=1.1)
    gb = top[0, 2].subgridspec(1, 2, width_ratios=[0.42, 1.0], wspace=0.0)
    ax = fig.add_subplot(gb[0, 1]); panel_b(ax); panel(ax, 'b', x=-0.3)
    mid = gs[1].subgridspec(1, 2, wspace=0.27)
    ax = fig.add_subplot(mid[0, 0]); panel_c(ax); panel(ax, 'c', x=-0.13)
    ax = fig.add_subplot(mid[0, 1]); panel_d(ax); panel(ax, 'd', x=-0.15)
    bot = gs[2].subgridspec(1, 2, wspace=0.27)
    ax = fig.add_subplot(bot[0, 0]); panel_e(ax); panel(ax, 'e', x=-0.13)
    gf = bot[0, 1].subgridspec(2, 1, height_ratios=[1.0, 0.36], hspace=0.12)
    ax = fig.add_subplot(gf[0, 0]); axb = fig.add_subplot(gf[1, 0], sharex=None)
    panel_f(ax, axb); panel(ax, 'f', x=-0.15)
    save(fig, NAME)


if __name__ == '__main__':
    main()
    print('ok')
