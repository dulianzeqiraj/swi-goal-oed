"""Figure 6 (proposal N3): inference after ADAPTIVE groundwater monitoring on a synthetic coastal transect.
Reads results/aquifer.json (written by sim_aquifer.py) and writes figures/fig6_n3_adaptive_monitoring.(png|pdf).

Run: python3 fig_aquifer.py
"""
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Rectangle
from scipy.stats import norm

from common import OI, INK, MUTED, RULE, MM, RES, panel, save, mc_band

J = json.load(open(os.path.join(RES, 'aquifer.json')))
S = J['setting']
LKM = S['L_km']
K2C = 1e7 / (LKM * 1000.0) ** 2          # kappa (m) -> c in 1e-7 1/m
ZC, ZK = S['zone_C'], S['zone_K']
C_OLS, C_AW, C_IPW, C_CS, C_CSW, C_UNI = OI['vermillion'], OI['blue'], OI['purple'], OI['green'], OI['orange'], MUTED
SAND = '#f3ead8'
SEA = '#d6ebf7'


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


def in_zone(u, z):
    return (u >= z[0]) & (u <= z[1])


# ------------------------------------------------------------------ (a) transect and example networks
def panel_a(fig, spec):
    g = GridSpecFromSubplotSpec(2, 1, subplot_spec=spec, height_ratios=[1.55, 1.0], hspace=0.06)
    ax = fig.add_subplot(g[0]); axn = fig.add_subplot(g[1], sharex=ax)
    xs = np.linspace(0, 1, 600); xkm = xs * LKM
    xmax = LKM + 0.42
    for a_ in (ax, axn):
        a_.axvspan(ZC[0] * LKM, ZC[1] * LKM, color=OI['green'], alpha=0.08, lw=0, zorder=0)
        a_.axvspan(ZK[0] * LKM, ZK[1] * LKM, color=OI['vermillion'], alpha=0.12, lw=0, zorder=0)
        a_.axvspan(LKM, xmax, color=SEA, lw=0, zorder=0)
        a_.grid(False)
    # head profiles
    ax.plot(xkm, head(xs, S['kappa0']), color=OI['blue'], lw=1.35, label='$c=c_0$ (marzh zero)', zorder=3)
    ax.plot(xkm, head(xs, S['kappa1']), color=OI['blue'], lw=1.0, ls='--', label='$c=1.25\\,c_0$ (me marzh)', zorder=3)
    ax.plot(xkm, head(xs, S['kappa1'], True), color=OI['purple'], lw=1.0, ls=':',
            label='$c=1.25\\,c_0$ + paleokanal', zorder=3)
    ax.axhline(0, color=OI['sky'], lw=0.8)
    ax.text(LKM + 0.21, 1.75, 'deti', rotation=90, ha='center', va='center', fontsize=6.0, color=OI['blue'])
    b = S['bump']
    xb = b['xc'] * LKM
    ax.annotate('paleokanal\n(i ngrirë)', xy=(xb, head(b['xc'], S['kappa1'], True) - 0.04), xytext=(3.2, 0.55),
                fontsize=5.6, color=OI['purple'], ha='center', va='center',
                arrowprops=dict(arrowstyle='-|>', color=OI['purple'], lw=0.6, mutation_scale=5, shrinkA=1, shrinkB=1))
    ax.text(np.mean(ZC) * LKM, 3.78, 'zona qendrore e ushqimit $C$', ha='center', fontsize=5.8, color=OI['green'])
    ax.annotate('zona bregdetare $K$', xy=(np.mean(ZK) * LKM, 3.55), xytext=(4.45, 3.78), ha='center', fontsize=5.8,
                color=OI['vermillion'], arrowprops=dict(arrowstyle='-', color=OI['vermillion'], lw=0.5, shrinkA=0, shrinkB=0))
    ax.set_ylim(-0.15, 4.15); ax.set_yticks([0, 1, 2, 3])
    ax.set_ylabel('ngarkesa $h(x)$ (m)')
    ax.legend(loc='lower left', bbox_to_anchor=(0.0, 0.0), fontsize=5.4, handlelength=1.9, borderaxespad=0.3)
    plt.setp(ax.get_xticklabels(), visible=False)
    ax.tick_params(axis='x', length=0)
    ax.set_title('Transekti bregdetar dhe rrjetet e monitorimit', color=INK)
    # schematic aquifer cross-section with three example networks (first 100 wells, one replicate, c = c0)
    axn.axhspan(-0.5, 2.5, xmin=0, xmax=LKM / xmax, color=SAND, lw=0, zorder=0)
    wedge = Polygon([[LKM, -0.5], [LKM - 0.55, -0.5], [LKM, 1.1]], closed=True, color=OI['sky'], alpha=0.45, lw=0, zorder=1)
    axn.add_patch(wedge)
    axn.text(LKM - 0.06, -0.38, 'pyka\ne kripur', fontsize=4.9, color=OI['blue'], ha='right', va='bottom', zorder=4)
    rows = [('g0.0', 'TS, $\\gamma=0$'), ('g0.2', 'TS, $\\gamma=0.2$'), ('unif', 'uniform')]
    nshow = 100
    for j, (key, lab) in enumerate(rows):
        yv = 2 - j
        u = np.array(J['zero'][key]['paths']['u'][0][:nshow])
        col = np.where(in_zone(u, ZK), OI['vermillion'], np.where(in_zone(u, ZC), OI['green'], MUTED))
        axn.vlines(u * LKM, yv - 0.32, yv + 0.32, colors=col, lw=0.55, zorder=3)
        axn.text(-0.08, yv, lab, ha='right', va='center', fontsize=6.0, color=INK)
        sh = np.mean(in_zone(u, ZK))
        axn.text(LKM + 0.21, yv, f'{100 * sh:.0f}%', ha='center', va='center', fontsize=5.2, color=OI['vermillion'])
    axn.text(LKM + 0.21, 2.62, '$K$', ha='center', va='bottom', fontsize=5.4, color=OI['vermillion'])
    axn.set_ylim(-0.5, 2.95); axn.set_yticks([])
    axn.spines['left'].set_visible(False)
    axn.set_xlim(0, xmax); axn.set_xticks([0, 1, 2, 3, 4, 5])
    axn.set_xlabel('distanca nga kufiri i brendshëm $x$ (km)')
    axn.text(0.04, 2.62, f'{nshow} puset e para, një replikim, $c=c_0$', fontsize=5.3, color=MUTED, va='bottom')
    return ax


# ------------------------------------------------------------------ (b) coverage vs n
def panel_b(ax):
    Lg = J['long']; ns = Lg['ck']
    for tag, ls, mk, mfc in (('zero', '-', 'o', None), ('margin', '--', 's', 'white')):
        d = Lg[f'{tag}_g0.0']; R = d['R']
        for col, keys in ((C_OLS, ('olscl', 'cov')), (C_AW, ('aw', 'hc3', 'cov')), (C_CS, ('csw', 'cov'))):
            c = np.array([ck(d, n, *keys) for n in ns])
            lo, hi = mc_band(c, R)
            ax.fill_between(ns, lo, hi, color=col, alpha=0.16 if tag == 'zero' else 0.09, lw=0)
            ax.plot(ns, c, color=col, ls=ls, marker=mk, ms=2.5, lw=1.15 if tag == 'zero' else 0.9,
                    mfc=mfc or col, mew=0.7)
    ax.axhline(0.95, color=MUTED, lw=0.7, ls=':')
    ax.text(ns[0] * 0.92, 0.951, 'nominale 0.95', fontsize=5.4, color=MUTED, va='bottom', ha='left')
    ax.set_xscale('log'); ax.set_xticks(ns); ax.set_xticklabels([str(n) for n in ns], fontsize=5.8); ax.minorticks_off()
    ax.set_xlim(ns[0] * 0.85, ns[-1] * 1.15)
    ax.set_xlabel('numri i puseve të matjes $n$'); ax.set_ylabel('mbulimi i intervalit 95% për $c$')
    ax.set_title('Mbulimi pas monitorimit adaptiv ($\\gamma=0$)', color=INK)
    h = [Line2D([], [], color=C_OLS, lw=1.1), Line2D([], [], color=C_AW, lw=1.1), Line2D([], [], color=C_CS, lw=1.1),
         Line2D([], [], color=MUTED, lw=1.0, marker='o', ms=2.6), Line2D([], [], color=MUTED, lw=0.9, ls='--', marker='s', ms=2.4, mfc='white')]
    ax.legend(h, ['OLS, Wald klasik', 'AW-LS, sanduiç HC3', 'SB me pesha $W_t$', '$c=c_0$ (marzh zero)', '$c=1.25\\,c_0$'],
              loc='lower right', fontsize=5.3, handlelength=1.9, ncol=2, columnspacing=1.0)
    return ax


# ------------------------------------------------------------------ (c) smoothing gamma
def panel_c(ax, n=400):
    G = [0.0, 0.05, 0.1, 0.2, 0.5]; keys = [f'g{g}' for g in G] + ['unif']
    xpos = np.arange(len(keys))
    R = J['zero']['g0.0']['R']
    spec = ((C_OLS, ('olscl', 'cov'), '-', 1.0), (C_AW, ('aw', 'cov'), ':', 0.9), (C_AW, ('aw', 'hc3', 'cov'), '-', 1.0),
            (C_IPW, ('ipw', 'hc3', 'cov'), '-', 0.8))
    for col, kk, ls, lw in spec:
        for tag, off, mk, mfc in (('zero', -0.09, 'o', None), ('margin', 0.09, 's', 'white')):
            c = np.array([ck(J[tag][k], n, *kk) for k in keys]); lo, hi = mc_band(c, R)
            ax.errorbar(xpos + off, c, yerr=[c - lo, hi - c], color=col, ls=ls, lw=lw, marker=mk, ms=2.5,
                        mfc=mfc or col, mew=0.7, elinewidth=0.6, capsize=0)
    ax.axhline(0.95, color=MUTED, lw=0.7, ls=':')
    ax.set_xticks(xpos); ax.set_xticklabels(['0', '0.05', '0.1', '0.2', '0.5', 'unif.'], fontsize=6.0)
    ax.set_xlabel('zbutja $\\gamma$ në $q_t=(1-\\gamma)\\,q_{{\\rm opt},t}+\\gamma\\, q^{\\rm sta}$')
    ax.set_ylabel(f'mbulimi i $c$ në $n={n}$')
    ax.set_title('Zbutja e dizajnit dhe peshat $W_t$', color=INK)
    h = [Line2D([], [], color=C_OLS, lw=1.0), Line2D([], [], color=C_AW, lw=1.0), Line2D([], [], color=C_AW, lw=0.9, ls=':'),
         Line2D([], [], color=C_IPW, lw=0.8)]
    ax.legend(h, ['OLS, Wald klasik', 'AW-LS, HC3', 'AW-LS, HC0$\\cdot n/(n-3)$', 'IPW $W_t^2$, HC3'], loc='lower right',
              fontsize=5.2, handlelength=1.9)
    return ax


# ------------------------------------------------------------------ (d) ever-miss under repeated reporting
def panel_d(ax):
    d0 = J['zero']['g0.0']; du = J['zero']['unif']; R = d0['R']
    nn = np.arange(1, len(d0['ever']['olscl']) + 1)
    for d, key, col, ls, lab in ((d0, 'olscl', C_OLS, '-', 'OLS Wald, TS $\\gamma=0$'),
                                 (du, 'olscl', C_UNI, '--', 'OLS Wald, dizajn uniform'),
                                 (d0, 'aw', C_AW, '-', 'AW-LS (HC0), TS $\\gamma=0$'),
                                 (d0, 'cs1', C_CS, '-', 'SB, $w_t=1$'),
                                 (d0, 'csw', C_CSW, '--', 'SB, $w_t=W_t$')):
        p = np.array(d['ever'][key], float); m = np.isfinite(p)
        lo, hi = mc_band(p[m], R)
        ax.fill_between(nn[m], lo, hi, color=col, alpha=0.15, lw=0)
        ax.plot(nn[m], p[m], color=col, ls=ls, lw=1.1, label=lab)
    ax.axhline(0.05, color=MUTED, lw=0.7, ls=':'); ax.text(10.5, 0.062, '$\\alpha=0.05$', fontsize=5.6, color=MUTED)
    ax.set_xscale('log'); ax.set_xlim(10, 400)
    ax.set_xticks([10, 25, 50, 100, 200, 400]); ax.set_xticklabels(['10', '25', '50', '100', '200', '400']); ax.minorticks_off()
    ax.set_xlabel('numri i puseve të matjes $n$'); ax.set_ylabel('$P(\\exists\\, m\\leq n:\\ c\\notin I_m)$')
    ax.set_title('Raportim pas çdo pusi të ri ($c=c_0$)', color=INK)
    ax.legend(loc='upper left', fontsize=5.2, handlelength=1.8)
    return ax, d0, nn


def panel_d_inset(ax, d0, nn, rect):
    ins = ax.inset_axes(rect)
    for key, col, ls in (('cs1', C_CS, '-'), ('csw', C_CSW, '--')):
        r = np.array(d0['width'][key], float) / np.array(d0['width']['olscl'], float); m = np.isfinite(r)
        ins.plot(nn[m], r[m], color=col, lw=0.9, ls=ls)
    ins.set_xscale('log'); ins.set_xlim(10, 400); ins.tick_params(labelsize=4.8, length=1.5, pad=1)
    ins.set_xticks([10, 100, 400]); ins.set_xticklabels(['10', '100', '400']); ins.minorticks_off(); ins.grid(True, lw=0.4)
    ins.set_title('gjerësia SB / Wald (mediane)', fontsize=5.0, color=MUTED, loc='center', pad=2)
    ins.set_facecolor('white')
    return ins


# ------------------------------------------------------------------ (e) studentised statistic
def panel_e(ax, nz=1600):
    edges = np.linspace(-5, 5, 51); bw = edges[1] - edges[0]
    dl = J['long']['zero_g0.0']
    for col, keys, lab in ((C_OLS, ('olscl',), 'OLS, Wald klasik'), (C_AW, ('aw', 'hc3'), 'AW-LS, HC3')):
        o = ck(dl, nz, *keys); hh = np.array(o['hist'], float); hh = hh / hh.sum() / bw
        ax.stairs(hh, edges, color=col, alpha=0.13, fill=True)
        ax.stairs(hh, edges, color=col, lw=1.0,
                  label=f"{lab}: mes. ${o['mean_z']:+.2f}$, d.s. ${o['sd_z']:.2f}$")
    xx = np.linspace(-4, 4, 300)
    ax.plot(xx, norm.pdf(xx), color=INK, lw=0.8, ls='--', label='$N(0,1)$')
    for s_ in (-1.96, 1.96):
        ax.axvline(s_, color=RULE, lw=0.6, ls=':')
    up_o = ck(dl, nz, 'olscl', 'up'); up_a = ck(dl, nz, 'aw', 'hc3', 'up')
    lo_o = ck(dl, nz, 'olscl', 'lo'); lo_a = ck(dl, nz, 'aw', 'hc3', 'lo')
    ax.text(2.1, 0.33, f'$P(Z>1.96)$\nOLS ${up_o:.3f}$\nAW ${up_a:.3f}$\nnominale $0.025$', fontsize=5.2, color=MUTED, va='top')
    ax.text(-2.1, 0.33, f'$P(Z<-1.96)$\nOLS ${lo_o:.3f}$\nAW ${lo_a:.3f}$', fontsize=5.2, color=MUTED, va='top', ha='right')
    ax.set_xlim(-4, 4); ax.set_ylim(0, 0.62)
    ax.set_xlabel('statistika e studentizuar $Z=(\\hat c-c)/\\widehat{\\rm se}$'); ax.set_ylabel('dendësia')
    ax.set_title(f'Shpërndarja e $Z$, $c=c_0$, $\\gamma=0$, $n={nz}$', color=INK)
    ax.legend(loc='upper left', fontsize=5.0, handlelength=1.5, ncol=1)
    return ax


# ------------------------------------------------------------------ (f) misspecification
def panel_f(ax, gkey='g0.2', nm=1600):
    M = J['misspec']; dm = M[gkey]; tg = dm['targets']; eb = np.array(M['est_bins']) * K2C
    for key, col in (('ols', C_OLS), ('aw', C_AW), ('ipw', C_IPW)):
        hh = np.array(ck(dm, nm, key + '_est', 'hist'), float); hh = hh / hh.sum() / (eb[1] - eb[0])
        ax.stairs(hh, eb, color=col, alpha=0.13, fill=True)
        ax.stairs(hh, eb, color=col, lw=1.0)
        ax.axvline(tg[key] * K2C, color=col, lw=0.8, ls='--')
    ax.axvline(M['quadratic_kappa'] * K2C, color=MUTED, lw=0.7, ls=':')
    return ax, dm, tg


def main():
    fig = plt.figure(figsize=(178 * MM, 128 * MM))
    gs = GridSpec(2, 1, figure=fig, height_ratios=[1.0, 1.0], hspace=0.50, left=0.075, right=0.985, top=0.95, bottom=0.085)
    top = GridSpecFromSubplotSpec(1, 3, subplot_spec=gs[0], width_ratios=[1.42, 1.0, 1.0], wspace=0.40)
    bot = GridSpecFromSubplotSpec(1, 3, subplot_spec=gs[1], width_ratios=[1.0, 1.0, 1.0], wspace=0.40)
    ax = panel_a(fig, top[0]); panel(ax, 'a', x=-0.27, y=1.06)
    ax = fig.add_subplot(top[1]); panel_b(ax); panel(ax, 'b', x=-0.30)
    ax = fig.add_subplot(top[2]); panel_c(ax); panel(ax, 'c', x=-0.30)
    ax = fig.add_subplot(bot[0]); ax, d0, nn = panel_d(ax); panel(ax, 'd', x=-0.30)
    ax._ins_args = (d0, nn)
    axd = ax
    ax = fig.add_subplot(bot[1]); panel_e(ax); panel(ax, 'e', x=-0.30)
    ax = fig.add_subplot(bot[2]); axf, dm, tg = panel_f(ax); panel(axf, 'f', x=-0.30)
    finish_d(axd, d0, nn)
    finish_f(axf, dm, tg)
    save(fig, 'fig6_n3_adaptive_monitoring')


def finish_d(ax, d0, nn):
    ymax = max(np.nanmax(np.array(d0['ever']['olscl'], float)), np.nanmax(np.array(J['zero']['unif']['ever']['olscl'], float)))
    ax.set_ylim(-0.01, ymax * 1.08 + 0.02)
    panel_d_inset(ax, d0, nn, [0.62, 0.40, 0.35, 0.28])


def finish_f(ax, dm, tg, nm=1600):
    lo = min(tg['ols'], tg['aw'], tg['ipw']) * K2C; hi = max(tg['ols'], tg['aw'], tg['ipw']) * K2C
    pad = 0.55 * (hi - lo)
    ax.set_xlim(lo - pad, hi + pad)
    ymax = ax.get_ylim()[1]
    ax.set_ylim(0, ymax * 1.9)
    ax.set_xlabel(f'$\\hat c$ ($10^{{-7}}$ m$^{{-1}}$), $\\gamma=0.2$, $n={nm}$'); ax.set_ylabel('dendësia')
    ax.set_title('Specifikim i gabuar: objektiva të ndryshëm', color=INK)
    h = [Line2D([], [], color=C_OLS, lw=1.0), Line2D([], [], color=C_AW, lw=1.0), Line2D([], [], color=C_IPW, lw=1.0),
         Line2D([], [], color=MUTED, lw=0.8, ls='--')]
    ax.legend(h, ['OLS', 'AW-LS, $W_t$', 'IPW, $W_t^2$', 'objektivi $c^*(q)$'], loc='upper left', fontsize=5.1, handlelength=1.6)
    M = J['misspec']; nsm = M['ck']
    ins = ax.inset_axes([0.62, 0.55, 0.36, 0.33])
    for key, col in (('ols', C_OLS), ('aw', C_AW), ('ipw', C_IPW)):
        c = np.array([ck(dm, n, key + '_est', 'cov3_sta') for n in nsm]); lo_, hi_ = mc_band(c, dm['R'])
        ins.fill_between(nsm, lo_, hi_, color=col, alpha=0.18, lw=0)
        ins.plot(nsm, c, color=col, lw=0.9, marker='o', ms=1.6)
    ins.axhline(0.95, color=MUTED, lw=0.6, ls=':')
    ins.set_xscale('log'); ins.set_xticks(nsm); ins.set_xticklabels([str(n) for n in nsm], fontsize=4.4); ins.minorticks_off()
    ins.set_ylim(-0.03, 1.05); ins.set_yticks([0, 0.5, 0.95]); ins.tick_params(labelsize=4.6, length=1.5, pad=1); ins.grid(True, lw=0.4)
    ins.set_title('mbulimi i $c^*(q^{\\rm sta})$ vs $n$', fontsize=5.0, color=MUTED, loc='center', pad=2)


if __name__ == '__main__':
    main()
    print('ok')
