"""Figure for proposal N3 (adaptive groundwater monitoring on a synthetic coastal transect) from
results/aquifer.json (sim_aquifer.py)."""
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle
from scipy.stats import norm

from common import OI, INK, MUTED, RULE, GRID, MM, RES, panel, save, mc_band

J = json.load(open(os.path.join(RES, 'aquifer.json')))
S = J['setting']
L2 = (S['L_km'] * 1000.0) ** 2
K2C = 1e7 / L2                     # kappa (m) -> c in 1e-7 1/m
ZC, ZK = S['zone_C'], S['zone_K']
C_OLS, C_AW, C_IPW, C_CS, C_CSW, C_UNI = OI['vermillion'], OI['blue'], OI['purple'], OI['green'], OI['orange'], MUTED
LAB = dict(olscl='OLS, Wald klasik', aw='AW-LS, $W_t=\\sqrt{q^{\\rm sta}/q_t}$', cs='VS (sekuencë besimi)')


def ck(d, n, *keys):
    v = d['ck'][str(n)]
    for k in keys:
        v = v[k]
    return v


def head(u, kap, mis=False):
    h = S['a'] + S['beta'] * u + kap * u * (1 - u)
    if mis:
        b = S['bump']
        h = h - b['A'] * np.exp(-(u - b['xc']) ** 2 / (2 * b['s'] ** 2))
    return h


def zone_col(u):
    return np.where((u >= ZK[0]) & (u <= ZK[1]), OI['vermillion'],
                    np.where((u >= ZC[0]) & (u <= ZC[1]), OI['green'], MUTED))


def panel_a(ax):
    xs = np.linspace(0, 1, 500); xkm = xs * S['L_km']
    ax.axvspan(ZC[0] * S['L_km'], ZC[1] * S['L_km'], color=OI['green'], alpha=0.09, lw=0)
    ax.axvspan(ZK[0] * S['L_km'], ZK[1] * S['L_km'], color=OI['vermillion'], alpha=0.10, lw=0)
    ax.add_patch(Rectangle((S['L_km'], -3.35), 0.32, 3.35, color=OI['sky'], alpha=0.25, lw=0, zorder=0))
    ax.text(S['L_km'] + 0.16, -1.7, 'deti', rotation=90, ha='center', va='center', fontsize=5.8, color=OI['blue'])
    ax.plot(xkm, head(xs, S['kappa0']), color=OI['blue'], lw=1.4, label='$h(x)$, $c=c_0$ (marzh zero)')
    ax.plot(xkm, head(xs, S['kappa1']), color=OI['blue'], lw=1.0, ls='--', label='$h(x)$, $c=1.25\\,c_0$ (me marzh)')
    ax.plot(xkm, head(xs, S['kappa1'], True), color=OI['purple'], lw=0.9, ls=':', label='me paleokanal (specifikim i gabuar)')
    ax.axhline(0, color=RULE, lw=0.6)
    b = S['bump']
    ax.annotate('paleokanal', xy=(b['xc'] * S['L_km'], head(b['xc'], S['kappa1'], True) - 0.05),
                xytext=(3.25, 0.25), fontsize=5.6, color=OI['purple'],
                arrowprops=dict(arrowstyle='-|>', color=OI['purple'], lw=0.6, mutation_scale=5))
    ax.text(np.mean(ZC) * S['L_km'], 4.15, 'zona qendrore e ushqimit $C$', ha='center', fontsize=5.8, color=OI['green'])
    ax.text(np.mean(ZK) * S['L_km'] - 0.05, 4.15, 'zona bregdetare $K$', ha='center', fontsize=5.8, color=OI['vermillion'])
    rows = [('g0.0', 'TS, $\\gamma=0$'), ('g0.2', 'TS, $\\gamma=0.2$'), ('unif', 'uniform')]
    ys = [-0.95, -1.85, -2.75]
    nshow = 80
    for (key, lab), yv in zip(rows, ys):
        u = np.array(J['zero'][key]['paths']['u'][0][:nshow])
        ax.scatter(u * S['L_km'], np.full_like(u, yv), marker='|', s=26, lw=0.8, c=zone_col(u), zorder=3)
        sh = np.mean((u >= ZK[0]) & (u <= ZK[1]))
        ax.text(-0.12, yv, lab, ha='right', va='center', fontsize=5.9, color=INK)
        ax.text(S['L_km'] - 0.02, yv + 0.33, f'$K$: {100 * sh:.0f}%', ha='right', va='bottom', fontsize=5.2, color=MUTED)
    ax.text(0.02, -0.42, f'puset e para $n={nshow}$ (një replikim, $c=c_0$)', fontsize=5.4, color=MUTED, va='center')
    ax.set_xlim(0, S['L_km'] + 0.32); ax.set_ylim(-3.35, 4.6)
    ax.set_yticks([0, 1, 2, 3]); ax.set_xticks([0, 1, 2, 3, 4, 5])
    ax.set_xlabel('distanca nga kufiri i brendshëm $x$ (km)')
    ax.set_ylabel('ngarkesa $h$ (m)'); ax.yaxis.set_label_coords(-0.075, 0.72)
    ax.grid(False)
    ax.legend(loc='upper left', bbox_to_anchor=(0.0, 0.93), fontsize=5.3, handlelength=1.6, ncol=1)
    ax.set_title('Transekti bregdetar dhe rrjetet adaptive', color=INK)


def main():
    fig = plt.figure(figsize=(178 * MM, 122 * MM))
    gs = GridSpec(2, 3, figure=fig, hspace=0.58, wspace=0.42, left=0.085, right=0.985, top=0.94, bottom=0.09)
    # (a) transect + example networks
    ax = fig.add_subplot(gs[0, 0])
    panel_a(ax)
    panel(ax, 'a', x=-0.30)
    # (b) coverage vs n, gamma = 0, zero margin (solid) and margin (dashed), long runs to 1600
    ax = fig.add_subplot(gs[0, 1])
    Lg = J['long']; ns = Lg['ck']
    for tag, ls, mk in (('zero', '-', 'o'), ('margin', '--', 's')):
        d = Lg[f'{tag}_g0.0']; R = d['R']
        for key, col, getter in (('olscl', C_OLS, lambda n: ck(d, n, 'olscl', 'cov')),
                                 ('aw', C_AW, lambda n: ck(d, n, 'aw', 'hc3', 'cov')),
                                 ('csw', C_CS, lambda n: ck(d, n, 'csw', 'cov'))):
            c = np.array([getter(n) for n in ns])
            if tag == 'zero':
                lo, hi = mc_band(c, R); ax.fill_between(ns, lo, hi, color=col, alpha=0.14, lw=0)
            ax.plot(ns, c, color=col, ls=ls, marker=mk, ms=2.4 if tag == 'zero' else 2.0, lw=1.1 if tag == 'zero' else 0.9,
                    mfc=col if tag == 'zero' else 'white', mew=0.7)
    ax.axhline(0.95, color=MUTED, lw=0.7, ls=':')
    ax.set_xscale('log'); ax.set_xticks(ns); ax.set_xticklabels([str(n) for n in ns], fontsize=5.6); ax.minorticks_off()
    ax.set_ylim(0.885, 1.008)
    ax.set_xlabel('numri i matjeve $n$'); ax.set_ylabel('mbulimi i $c$ (95%)')
    ax.set_title('Mbulimi, TS i pastër ($\\gamma=0$)', color=INK)
    h = [plt.Line2D([], [], color=C_OLS, lw=1.1), plt.Line2D([], [], color=C_AW, lw=1.1), plt.Line2D([], [], color=C_CS, lw=1.1),
         plt.Line2D([], [], color=MUTED, lw=1.0, ls='-', marker='o', ms=2.4), plt.Line2D([], [], color=MUTED, lw=0.9, ls='--', marker='s', ms=2.0, mfc='white')]
    ax.legend(h, ['OLS, Wald klasik', 'AW-LS (HC3)', 'VS me pesha $W_t$', '$c=c_0$ (marzh zero)', '$c=1.25\\,c_0$'],
              loc='lower right', fontsize=5.2, handlelength=1.8, ncol=1)
    panel(ax, 'b', x=-0.24)
    # (c) gamma trade-off at n = 400
    ax = fig.add_subplot(gs[0, 2])
    G = [0.0, 0.05, 0.1, 0.2, 0.5]; xpos = np.arange(len(G) + 1)
    keys = [f'g{g}' for g in G] + ['unif']
    R = J['zero']['g0.0']['R']
    for est, col, get in (('olscl', C_OLS, lambda d: ck(d, 400, 'olscl', 'cov')),
                          ('aw1', C_AW, lambda d: ck(d, 400, 'aw', 'cov')),
                          ('aw3', C_AW, lambda d: ck(d, 400, 'aw', 'hc3', 'cov'))):
        for tag, ls, mfc, off in (('zero', '-', None, -0.08), ('margin', '--', 'white', 0.08)):
            c = np.array([get(J[tag][k]) for k in keys]); lo, hi = mc_band(c, R)
            lsx = ':' if est == 'aw1' else ls
            ax.errorbar(xpos + off, c, yerr=[c - lo, hi - c], color=col, ls=lsx, lw=0.9 if est != 'aw1' else 0.8,
                        marker='o' if tag == 'zero' else 's', ms=2.4, mfc=mfc or col, mew=0.7, elinewidth=0.6, capsize=0)
    ax.axhline(0.95, color=MUTED, lw=0.7, ls=':')
    ax.set_xticks(xpos); ax.set_xticklabels(['0', '0.05', '0.1', '0.2', '0.5', 'unif.'], fontsize=5.8)
    ax.set_xlabel('zbutja $\\gamma$ në $q_t=(1-\\gamma)q_{{\\rm opt},t}+\\gamma q^{\\rm sta}$')
    ax.set_ylabel('mbulimi i $c$ në $n=400$')
    ax.set_ylim(0.76, 0.99)
    ax.set_title('Zbutja e dizajnit dhe peshat', color=INK)
    h = [plt.Line2D([], [], color=C_OLS, lw=1.0), plt.Line2D([], [], color=C_AW, lw=1.0),
         plt.Line2D([], [], color=C_AW, lw=0.8, ls=':'),
         plt.Line2D([], [], color=MUTED, lw=0, marker='o', ms=2.6), plt.Line2D([], [], color=MUTED, lw=0, marker='s', ms=2.6, mfc='white')]
    ax.legend(h, ['OLS, Wald klasik', 'AW-LS (HC3)', 'AW-LS (HC0·$n/(n-3)$)', '$c=c_0$', '$c=1.25\\,c_0$'], loc='lower right',
              fontsize=5.2, handlelength=1.8)
    panel(ax, 'c', x=-0.24)
    # (d) ever-miss with peeking at every n
    ax = fig.add_subplot(gs[1, 0])
    d0 = J['zero']['g0.0']; du = J['zero']['unif']; R = d0['R']
    nn = np.arange(1, len(d0['ever']['olscl']) + 1)
    for d, key, col, ls, lab in ((d0, 'olscl', C_OLS, '-', 'OLS Wald, TS $\\gamma=0$'),
                                 (du, 'olscl', C_UNI, '--', 'OLS Wald, dizajn uniform'),
                                 (d0, 'aw', C_AW, '-', 'AW-LS, TS $\\gamma=0$'),
                                 (d0, 'cs1', C_CS, '-', 'VS, $w_t=1$'),
                                 (d0, 'csw', C_CSW, '--', 'VS, $w_t=W_t$')):
        p = np.array(d['ever'][key], float); m = np.isfinite(p)
        lo, hi = mc_band(p[m], R)
        ax.fill_between(nn[m], lo, hi, color=col, alpha=0.13, lw=0)
        ax.plot(nn[m], p[m], color=col, ls=ls, lw=1.1, label=lab)
    ax.axhline(0.05, color=MUTED, lw=0.7, ls=':'); ax.text(11, 0.065, '$\\alpha=0.05$', fontsize=5.8, color=MUTED)
    ax.set_xscale('log'); ax.set_xlim(10, 400); ax.set_ylim(-0.01, 0.75)
    ax.set_xticks([10, 25, 50, 100, 200, 400]); ax.set_xticklabels(['10', '25', '50', '100', '200', '400']); ax.minorticks_off()
    ax.set_xlabel('numri i matjeve $n$'); ax.set_ylabel('$P(\\exists\\, m\\leq n:\\ c\\notin I_m)$')
    ax.set_title('Raportim i përsëritur (çdo pus i ri)', color=INK)
    ax.legend(loc='upper left', fontsize=5.1, handlelength=1.6)
    ins = ax.inset_axes([0.60, 0.50, 0.37, 0.30])
    for key, col, ls in (('cs1', C_CS, '-'), ('csw', C_CSW, '--')):
        r = np.array(d0['width'][key], float) / np.array(d0['width']['olscl'], float); m = np.isfinite(r)
        ins.plot(nn[m], r[m], color=col, lw=0.9, ls=ls)
    ins.set_xscale('log'); ins.set_xlim(10, 400); ins.set_ylim(1.5, 4.5); ins.tick_params(labelsize=4.8, length=1.5)
    ins.set_xticks([10, 100]); ins.set_xticklabels(['10', '100']); ins.minorticks_off(); ins.grid(True, lw=0.4)
    ins.set_title('gjerësia VS / Wald', fontsize=5.2, color=MUTED, loc='center', pad=2)
    panel(ax, 'd', x=-0.24)
    # (e) studentised statistic at n = 400, zero margin, gamma = 0
    ax = fig.add_subplot(gs[1, 1])
    edges = np.linspace(-5, 5, 51); mids = 0.5 * (edges[1:] + edges[:-1]); bw = edges[1] - edges[0]
    dl = J['long']['zero_g0.0']; nz = 1600
    for key, col, lab, get in (('olscl', C_OLS, 'OLS, Wald klasik', lambda: ck(dl, nz, 'olscl')),
                               ('aw', C_AW, 'AW-LS (HC3)', lambda: ck(dl, nz, 'aw', 'hc3'))):
        o = get(); hh = np.array(o['hist'], float); hh = hh / hh.sum() / bw
        ax.stairs(hh, edges, color=col, lw=1.0, label=f"{lab}: mes. {o['mean_z']:+.2f}, s.d. {o['sd_z']:.2f}")
        ax.stairs(hh, edges, color=col, alpha=0.12, fill=True)
    xx = np.linspace(-4, 4, 300)
    ax.plot(xx, norm.pdf(xx), color=INK, lw=0.8, ls='--', label='$N(0,1)$')
    for s_ in (-1.96, 1.96):
        ax.axvline(s_, color=RULE, lw=0.6, ls=':')
    up_o = ck(dl, nz, 'olscl', 'up'); up_a = ck(dl, nz, 'aw', 'hc3', 'up')
    ax.text(2.05, 0.30, f'$P(Z>1.96)$\nOLS {up_o:.3f}\nAW {up_a:.3f}\nnominal 0.025', fontsize=5.2, color=MUTED, va='top')
    ax.set_xlim(-4, 4); ax.set_ylim(0, 0.56)
    ax.set_xlabel('statistika e studentizuar $Z=(\\hat c-c)/\\widehat{\\rm se}$'); ax.set_ylabel('dendësia')
    ax.set_title(f'Shpërndarja e $Z$, $c=c_0$, $\\gamma=0$, $n={nz}$', color=INK)
    ax.legend(loc='upper left', fontsize=5.0, handlelength=1.4)
    panel(ax, 'e', x=-0.24)
    # (f) misspecification: different targets
    ax = fig.add_subplot(gs[1, 2])
    M = J['misspec']; dm = M['g0.2']; tg = dm['targets']; eb = np.array(M['est_bins']) * K2C
    nm = 1600
    for key, col, lab in (('ols', C_OLS, 'OLS'), ('aw', C_AW, 'AW-LS'), ('ipw', C_IPW, 'IPW $W_t^2$')):
        hh = np.array(ck(dm, nm, key + '_est', 'hist'), float); hh = hh / hh.sum() / (eb[1] - eb[0])
        ax.stairs(hh, eb, color=col, lw=1.0, label=lab)
        ax.stairs(hh, eb, color=col, alpha=0.13, fill=True)
        ax.axvline(tg[key] * K2C, color=col, lw=0.8, ls='--')
    ymax = ax.get_ylim()[1] * 1.85
    ax.set_ylim(0, ymax); ax.set_xlim(1.58, 1.83)
    ax.set_xlabel(f'$\\hat c$ ($10^{{-7}}$ m$^{{-1}}$), $\\gamma=0.2$, $n={nm}$'); ax.set_ylabel('dendësia')
    ax.set_title('Specifikim i gabuar: objektiva të ndryshëm', color=INK)
    h = [plt.Line2D([], [], color=C_OLS, lw=1.0), plt.Line2D([], [], color=C_AW, lw=1.0), plt.Line2D([], [], color=C_IPW, lw=1.0),
         plt.Line2D([], [], color=MUTED, lw=0.8, ls='--')]
    ax.legend(h, ['OLS', 'AW-LS', 'IPW $W_t^2$', 'objektivi teorik'], loc='upper left', fontsize=5.1, handlelength=1.4)
    ins = ax.inset_axes([0.60, 0.56, 0.37, 0.36])
    nsm = M['ck']
    for key, col in (('ols', C_OLS), ('aw', C_AW), ('ipw', C_IPW)):
        c = np.array([ck(dm, n, key + '_est', 'cov3_sta') for n in nsm]); lo, hi = mc_band(c, dm['R'])
        ins.fill_between(nsm, lo, hi, color=col, alpha=0.15, lw=0)
        ins.plot(nsm, c, color=col, lw=0.9, marker='o', ms=1.6)
    ins.axhline(0.95, color=MUTED, lw=0.6, ls=':')
    ins.set_xscale('log'); ins.set_xticks(nsm); ins.set_xticklabels([str(n) for n in nsm], fontsize=4.4); ins.minorticks_off()
    ins.set_ylim(-0.03, 1.03); ins.set_yticks([0, 0.5, 0.95]); ins.tick_params(labelsize=4.6, length=1.5); ins.grid(True, lw=0.4)
    ins.set_title('mbulimi i $c^*(q^{\\rm sta})$', fontsize=5.0, color=MUTED, loc='center', pad=2)
    panel(ax, 'f', x=-0.24)
    save(fig, 'fig6_n3_adaptive_monitoring')


if __name__ == '__main__':
    main()
    print('ok')
