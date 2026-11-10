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
    fig, ax = plt.subplots(4, 1, figsize=(7.6, 6.3), sharex=True, gridspec_kw=dict(hspace=0.32))
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
    a.text(0.60, 248, 'shaded: below field capacity,\nno recharge; the heads are\nblind to soil moisture',
           fontsize=6.6, color=ORANGE, va='top')
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
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 2.65))
    a = ax[0]
    x = np.geomspace(5, 5000, 400)
    for per, lab, c in [(1, '1 day (single storms)', NAVY), (30, '1 month', BLUE), (365, '1 year (seasonal)', ORANGE)]:
        a.semilogx(x, visibility(x, per), color=c, label=lab)
    a.set_xlabel('distance of the well from the sea (m)'); a.set_ylabel('head response / response far inland')
    a.set_title('(a) Near the sea the slow recharge is hidden'); a.set_ylim(0, 1.15)
    a.legend(frameon=False, fontsize=7, loc='lower right', title='period', title_fontsize=7)
    b = ax[1]
    j = r['jacobian']
    sv = np.array(j['singular_values'])
    b.semilogy(np.arange(1, len(sv) + 1), sv, 'o', color=NAVY, label='heads and gauge')
    b.annotate('one direction is invisible:\nrain, ET, Ic, field capacity\nand Sy all × c', xy=(len(sv), sv[-1]),
               xytext=(3.6, 2e-3), fontsize=7, color=RED, arrowprops=dict(arrowstyle='->', color=RED, lw=0.8))
    anchors = [('pumping test', 'smallest_sv_with_pumping_test', ORANGE),
               ('soil probe', 'smallest_sv_with_soil_probe', BLUE),
               ('chloride balance', 'smallest_sv_with_chloride_balance', GREEN)]
    for k, (lab, kk, c) in enumerate(anchors):
        b.semilogy([len(sv) + 0.35 + 0.25 * k], [j[kk]], 's', color=c, label=f'+ {lab}: smallest')
    b.set_xlabel('singular value index'); b.set_ylabel('singular value of the head Jacobian')
    b.set_title('(b) One zero, removed by any anchor'); b.set_ylim(1e-8, 3e4)
    b.legend(frameon=False, fontsize=6.6, loc='lower left')
    fig.tight_layout(); fig.savefig(out, dpi=220); plt.close(fig)


def fig3(r, out):
    from matplotlib.lines import Line2D
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.1))
    a = ax[0]
    tr = r['setup']['truth']
    p0 = r['scenarios']['S0 heads and gauge']['points']
    a.loglog(p0['m'], p0['Sy'], '.', ms=2.2, color='#B8BEC6', zorder=1)
    handles = [Line2D([], [], ls='', marker='.', ms=6, color='#B8BEC6', label='S0 heads and gauge: a ridge')]
    for name, lw in [('S3 + chloride mass balance', 9), ('S1 + pumping test', 6), ('S2 + soil-moisture probe', 3.5)]:
        sm = r['scenarios'][name]['summary']['m']
        m_ = np.array([sm['q05'], sm['q95']])
        a.loglog(m_, tr['Sy'] * m_ / tr['m'], color=SC_COL[key(name)], lw=lw, solid_capstyle='butt', zorder=2)
        handles.append(Line2D([], [], color=SC_COL[key(name)], lw=4, label=name + ': 90 %'))
    a.loglog([tr['m']], [tr['Sy']], '*', ms=7, color=RED, zorder=3)
    handles.append(Line2D([], [], ls='', marker='*', ms=7, color=RED, label='truth'))
    a.set_xlabel('rain multiplier m (true rain / gauge)'); a.set_ylabel('specific yield Sy')
    a.set_title('(a) Heads alone: a ridge; one anchor: a segment')
    a.legend(handles=handles, frameon=False, fontsize=6.3, loc='upper left')
    b = ax[1]
    qs = [('rain_mm_yr', 'true rain'), ('recharge_mm_yr', 'recharge (mm)'), ('R_over_P', 'recharge / rain'),
          ('ET_over_P', 'ET / rain'), ('theta_fc', 'field capacity')]
    names = list(r['scenarios'].keys())
    for i, (q, lab) in enumerate(qs):
        for jdx, name in enumerate(names):
            sm = r['scenarios'][name]['summary'][q]
            y = i + (jdx - 2) * 0.15
            b.plot([sm['q05'] / sm['truth'], sm['q95'] / sm['truth']], [y, y], color=SC_COL[key(name)], lw=2.4)
            b.plot([sm['median'] / sm['truth']], [y], 'o', ms=2.5, color=SC_COL[key(name)])
    b.axvline(1, color=RED, lw=0.8)
    b.set_xscale('log'); b.set_xlim(0.4, 2.2)
    ticks = [0.5, 0.75, 1, 1.5, 2]
    b.set_xticks(ticks); b.set_xticklabels([f'{t:g}' for t in ticks]); b.minorticks_off()
    b.set_yticks(range(len(qs))); b.set_yticklabels([lab for _, lab in qs]); b.invert_yaxis()
    b.set_xlabel('90 % interval / truth'); b.set_title('(b) Shares found; amounts need an anchor')
    for name in names:
        b.plot([], [], color=SC_COL[key(name)], lw=2.4, label=name)
    b.legend(frameon=False, fontsize=6.2, loc='upper center', bbox_to_anchor=(0.35, -0.2), ncol=2)
    fig.tight_layout(); fig.savefig(out, dpi=220, bbox_inches='tight'); plt.close(fig)


def fig4(r, out):
    s = r['series']; tr = r['setup']['truth']
    n = len(s['theta']); t = np.arange(n) / 365.25
    th = np.array(s['theta'])
    fig, ax = plt.subplots(1, 3, figsize=(7.6, 2.8), gridspec_kw=dict(width_ratios=[1.25, 1.25, 1]))
    a = ax[0]
    b0 = np.array(r['scenarios']['S0 heads and gauge']['bands']['theta'])
    b2 = np.array(r['scenarios']['S2 + soil-moisture probe']['bands']['theta'])
    a.fill_between(t, b0[0], b0[2], color=GREY, alpha=0.35, lw=0, label='S0: 90 % band')
    a.plot(t, b2[1], color=BLUE, lw=1.1, label='S2 + probe (band thinner than line)')
    a.plot(t, th, color=NAVY, lw=0.7, ls='--', label='truth')
    a.set_xlabel('years from 1 September'); a.set_ylabel('soil water (mm)')
    a.set_title('(a) Amount: needs a probe'); a.legend(frameon=False, fontsize=6, loc='upper right')
    a.set_ylim(0, 470)
    b = ax[1]
    w0 = np.array(r['scenarios']['S0 heads and gauge']['bands']['wet'])
    wid = float(np.median(w0[2] - w0[0]))
    b.fill_between(t, w0[0], w0[2], color=BLUE, alpha=0.9, lw=1.6, edgecolor=BLUE,
                   label=f'S0: 90 % band, width ≈ {wid:.2f}')
    b.plot(t, th / tr['theta_fc'], color='black', lw=0.5, ls='--', label='truth')
    b.axhline(1, color=GREEN, lw=0.8, ls=':')
    b.set_xlabel('years from 1 September'); b.set_ylabel('relative wetness θ / θfc')
    b.set_title('(b) Shape: from the heads alone'); b.legend(frameon=False, fontsize=6, loc='upper right')
    b.set_ylim(0, 2.25)
    c = ax[2]
    s4 = r['scenarios']['S4 all']['summary']['Ic']; ns = r['no_storms']['summary']['Ic']
    c.axvline(tr['Ic'], color=RED, lw=0.8, alpha=0.6, zorder=1)
    c.plot([s4['q05'], s4['q95']], [1, 1], color=NAVY, lw=9, solid_capstyle='butt', zorder=3)
    c.plot([ns['q05'], ns['q95']], [0, 0], color=ORANGE, lw=5, solid_capstyle='butt', zorder=3)
    c.text(s4['q95'] * 1.25, 1, f"{s4['q05']:.1f}–{s4['q95']:.1f}", va='center', fontsize=6.5, color=NAVY)
    c.text(ns['q05'] * 1.1, 0.22, f"only a lower bound, ≥ {ns['q05']:.0f}", fontsize=6.5, color=ORANGE)
    c.axvline(0.9 * tr['Ic'], color=GREY, lw=0.9, ls=':')
    c.text(0.9 * tr['Ic'] * 0.95, 0.5, 'largest\ndaily rain', ha='right', fontsize=6.3, color=GREY)
    c.text(ns['q95'], -0.32, 'prior\nlimit', ha='right', fontsize=6.3, color=GREY)
    c.set_xscale('log'); c.set_xlim(8, 400); c.set_ylim(-0.7, 1.6)
    c.set_yticks([0, 1]); c.set_yticklabels(['no storm\nabove Ic', f"{r['setup']['storm_days_above_Ic']} storm\ndays"])
    c.set_xlabel('Ic, 90 % interval (mm/day)'); c.set_title('(c) Ic needs storms')
    fig.tight_layout(); fig.savefig(out, dpi=220, bbox_inches='tight'); plt.close(fig)


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
