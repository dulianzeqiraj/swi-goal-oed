"""Figures for INFILTRIMI-GO from infiltrimi_results.json.

usage: python infiltrimi_figs.py infiltrimi_results.json OUTDIR"""
import json
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

NAVY, BLUE, ORANGE, GREEN, GREY, RED = '#1F3864', '#2E6DB4', '#D9822B', '#3A8F5C', '#6B7785', '#B03A2E'
SC_COL = {'S0': GREY, 'S1': ORANGE, 'S2': BLUE, 'S3': GREEN, 'S4': NAVY}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.3, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.titlesize': 8.8, 'axes.titleweight': 'bold'})


def key(name):
    return name.split()[0]


def fig1(r, out):
    s = r['series']; tr = r['setup']['truth']
    n = len(s['P']); t = np.arange(n) / 365.25
    P = np.array(s['P']); th = np.array(s['theta']); R = np.array(s['R'])
    blind = th < tr['theta_fc'] - 1e-9
    fig, ax = plt.subplots(4, 1, figsize=(7.6, 7.2), sharex=True, gridspec_kw=dict(hspace=0.28))
    a = ax[0]
    a.bar(t, P, width=1 / 365.25, color=BLUE, lw=0)
    a.axhline(tr['Ic'], color=RED, ls='--', lw=0.9)
    a.text(2.98, tr['Ic'] + 3, f"infiltration capacity Ic = {tr['Ic']:g} mm/day", color=RED, ha='right', fontsize=7)
    a.set_ylabel('rain (mm/day)'); a.set_title('(a) True rain; the gauge reads it 12 % low')
    a = ax[1]
    a.plot(t, th, color=NAVY, lw=1)
    a.axhline(tr['theta_fc'], color=GREEN, ls='--', lw=0.9)
    a.fill_between(t, 0, 1, where=blind, transform=a.get_xaxis_transform(), color=ORANGE, alpha=0.15, lw=0)
    a.text(0.02, tr['theta_fc'] + 8, 'field capacity', color=GREEN, fontsize=7)
    a.text(0.62, 0.9, 'shaded: soil below field capacity, no recharge,\nthe heads carry no information on soil moisture',
           transform=a.transAxes, fontsize=7, color=ORANGE, va='top')
    a.set_ylabel('soil water (mm)'); a.set_title('(b) Soil moisture in the root zone')
    a = ax[2]
    Rh = np.array(r['wtf']['Rhat'], dtype=float)
    a.plot(t, Rh, '.', ms=1.6, color=GREY, label='from the heads, Sy known (water-table fluctuation)')
    a.plot(t, R, color=NAVY, lw=1, label='true recharge')
    a.set_ylabel('recharge (mm/day)'); a.set_title('(c) Recharge: the heads see it, in units of Sy')
    a.legend(frameon=False, fontsize=7, loc='upper right'); a.set_ylim(-6, max(R.max() * 1.15, 10))
    a = ax[3]
    a.plot(t, s['h_obs'], '.', ms=1.2, color=GREY, label='logger, noise 1 cm')
    a.plot(t, s['h_true'], color=NAVY, lw=1, label='true head')
    a.set_ylabel('head (m)'); a.set_title('(d) Groundwater head at an inland well')
    a.set_xlabel('years from 1 September'); a.legend(frameon=False, fontsize=7, loc='upper right')
    fig.savefig(out, dpi=220, bbox_inches='tight'); plt.close(fig)


def visibility(x, period, D=5000.0, L=5000.0):
    w = 2 * np.pi / period
    kap = np.sqrt(1j * w / D)
    ratio = np.exp(-kap * x) * (1 + np.exp(-2 * kap * (L - x))) / (1 + np.exp(-2 * kap * L))
    return np.abs(1 - ratio)


def fig2(r, out):
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 2.9))
    a = ax[0]
    x = np.geomspace(5, 5000, 400)
    for per, lab, c in [(1, '1 day (single storms)', NAVY), (30, '1 month', BLUE), (365, '1 year (seasonal)', ORANGE)]:
        a.semilogx(x, visibility(x, per), color=c, label=lab)
    a.set_xlabel('distance of the well from the sea (m)'); a.set_ylabel('share of the recharge signal seen')
    a.set_title('(a) Near the sea the slow recharge is hidden'); a.set_ylim(0, 1.05)
    a.legend(frameon=False, fontsize=7, loc='lower right', title='period', title_fontsize=7)
    b = ax[1]
    j = r['jacobian']
    sv = np.array(j['singular_values'])
    b.semilogy(np.arange(1, len(sv) + 1), sv, 'o', color=NAVY, label='heads and gauge')
    b.annotate('one direction is invisible:\nrain, ET, Ic, field capacity\nand Sy all × c', xy=(len(sv), sv[-1]),
               xytext=(4.3, 3e-5), fontsize=7, color=RED, arrowprops=dict(arrowstyle='->', color=RED, lw=0.8))
    anchors = [('pumping test', 'smallest_sv_with_pumping_test', ORANGE),
               ('soil probe', 'smallest_sv_with_soil_probe', BLUE),
               ('chloride balance', 'smallest_sv_with_chloride_balance', GREEN)]
    for k, (lab, kk, c) in enumerate(anchors):
        b.semilogy([len(sv) + 0.35 + 0.25 * k], [j[kk]], 's', color=c, label=f'+ {lab}: smallest')
    b.set_xlabel('singular value index'); b.set_ylabel('singular value of the head Jacobian')
    b.set_title('(b) One zero, removed by any anchor'); b.set_ylim(1e-8, 3e4)
    b.legend(frameon=False, fontsize=6.6, loc='upper right')
    fig.tight_layout(); fig.savefig(out, dpi=220); plt.close(fig)


def fig3(r, out):
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.1))
    a = ax[0]
    for name, sc in r['scenarios'].items():
        k = key(name)
        if k == 'S4':
            continue
        p = sc['points']
        a.loglog(p['m'], p['Sy'], '.', ms=2.0, alpha=0.5, color=SC_COL[k], label=name)
    tr = r['setup']['truth']
    a.loglog([tr['m']], [tr['Sy']], '*', ms=11, color=RED, label='truth')
    a.set_xlabel('rain multiplier m (true rain / gauge)'); a.set_ylabel('specific yield Sy')
    a.set_title('(a) Heads alone: a ridge; one anchor: a point')
    a.legend(frameon=False, fontsize=6.4, loc='upper left', markerscale=3)
    b = ax[1]
    qs = [('rain_mm_yr', 'true rain'), ('recharge_mm_yr', 'recharge (mm)'), ('R_over_P', 'recharge / rain'),
          ('ET_over_P', 'ET / rain'), ('theta_fc', 'field capacity')]
    names = list(r['scenarios'].keys())
    for i, (q, lab) in enumerate(qs):
        for jdx, name in enumerate(names):
            s = r['scenarios'][name]['summary'][q]
            y = i + (jdx - 2) * 0.14
            b.plot([s['q05'] / s['truth'], s['q95'] / s['truth']], [y, y], color=SC_COL[key(name)], lw=2.2)
            b.plot([s['median'] / s['truth']], [y], 'o', ms=2.5, color=SC_COL[key(name)])
    b.axvline(1, color=RED, lw=0.8)
    b.set_xscale('log'); b.set_xlim(0.35, 3.0)
    b.set_yticks(range(len(qs))); b.set_yticklabels([lab for _, lab in qs]); b.invert_yaxis()
    b.set_xlabel('90 % interval / truth'); b.set_title('(b) Fractions are found; amounts need an anchor')
    for jdx, name in enumerate(names):
        b.plot([], [], color=SC_COL[key(name)], lw=2.2, label=name)
    b.legend(frameon=False, fontsize=6.2, loc='lower right')
    fig.tight_layout(); fig.savefig(out, dpi=220); plt.close(fig)


def fig4(r, out):
    s = r['series']; tr = r['setup']['truth']
    n = len(s['theta']); t = np.arange(n) / 365.25
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.0), gridspec_kw=dict(width_ratios=[1.6, 1]))
    a = ax[0]
    for name, c in [('S0 heads and gauge', GREY), ('S2 + soil-moisture probe', BLUE)]:
        bd = np.array(r['scenarios'][name]['bands']['theta'])
        a.fill_between(t, bd[0], bd[2], color=c, alpha=0.35, lw=0, label=f'{name}: 90 % band')
    a.plot(t, s['theta'], color=NAVY, lw=0.9, label='truth')
    a.axhline(tr['theta_fc'], color=GREEN, ls='--', lw=0.8)
    a.set_xlabel('years from 1 September'); a.set_ylabel('soil water (mm)')
    a.set_title('(a) Soil moisture: shape from the heads, size from a probe')
    a.legend(frameon=False, fontsize=6.5, loc='upper right')
    b = ax[1]
    bins = np.geomspace(5, 300, 40)
    b.hist(r['with_storms_Ic'], bins=bins, color=NAVY, alpha=0.7, label=f"{r['setup']['storm_days_above_Ic']} storm days above Ic")
    b.hist(r['no_storms']['points']['Ic'], bins=bins, color=ORANGE, alpha=0.6, label='no storm above Ic')
    b.axvline(tr['Ic'], color=RED, lw=0.9)
    b.set_xscale('log'); b.set_xlabel('infiltration capacity Ic (mm/day)'); b.set_ylabel('posterior samples')
    b.set_title('(b) Ic is seen only through storms'); b.legend(frameon=False, fontsize=6.5, loc='upper right')
    fig.tight_layout(); fig.savefig(out, dpi=220); plt.close(fig)


def main(res, outdir):
    r = json.load(open(res))
    os.makedirs(outdir, exist_ok=True)
    fig1(r, os.path.join(outdir, 'infiltrimi_fig1.png'))
    fig2(r, os.path.join(outdir, 'infiltrimi_fig2.png'))
    fig3(r, os.path.join(outdir, 'infiltrimi_fig3.png'))
    fig4(r, os.path.join(outdir, 'infiltrimi_fig4.png'))
    print('saved figures in', outdir)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
