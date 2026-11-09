"""Figures of the PERTEJ-GO theory note; English labels, every text at least 8.6 pt at the printed size.
usage: python pertej_figs.py OUT_DIR

fig_scheme  what PERTEJ-GO puts in place of the unmodelled aquifer, and where a neural network may enter
fig_n1      N1: head at the boundary cell with five boundaries; error of each (Proposition 1)
fig_n23     N2 and N3: compartments needed for the half-order boundary; energy and growth with a non-passive term
fig_n4      N4: the boundary learned from two piezometers; excitation, a closure inside the band, a new regime
fig_n5      N5: the learned prior; what it adds where the data are silent
Numbers come from res/pertej.json and res/pertej_series.npz."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.ticker import FixedLocator, NullLocator

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', 'rindertimi_go'))
import gar_figs as GF  # noqa: E402
from rgo_figs import Canvas, INK, MUTED  # noqa: E402

RES = os.path.join(HERE, 'res')
MM, FS = GF.MM, GF.FS
BLUE, ORANGE, AQUA, VIOLET, REF = GF.BLUE, GF.ORANGE, GF.AQUA, GF.VIOLET, GF.REF
GREEN, GREEN_L = '#1E6B35', '#E6F4EA'
SEA, LAND, EXT = '#cfe3f7', '#f3efe6', '#eceef1'
YR = 365.25
BANDS = dict(high=(2.5, 10), mid=(30, 10 * YR), low=(40 * YR, 200 * YR))
BAND_LAB = dict(high='2.5–10 d', mid='band of the data', low='40–200 yr')
BAND_SHORT = dict(high='2.5–10 d', mid='data', low='40–200 yr')


def load():
    with open(os.path.join(RES, 'pertej.json')) as fh:
        R = json.load(fh)
    return R, dict(np.load(os.path.join(RES, 'pertej_series.npz')))


def period_axis(ax, lo=1.0, hi=250 * YR, ticks=(7, 30, YR, 10 * YR, 100 * YR),
                labs=('1 wk', '1 mo', '1 yr', '10 yr', '100 yr')):
    ax.set_xscale('log'); ax.set_xlim(lo, hi)
    ax.xaxis.set_major_locator(FixedLocator(list(ticks))); ax.set_xticklabels(list(labs))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xlabel('period of the head change')


def shade_bands(ax, short=False):
    for k, (a, b) in BANDS.items():
        ax.axvspan(a, b, color='#eef3fa' if k == 'mid' else '#f4f4f4', zorder=0, lw=0)
        ax.text(np.sqrt(a * b), 0.975, (BAND_SHORT if short else BAND_LAB)[k], transform=ax.get_xaxis_transform(), ha='center', va='top',
                fontsize=FS, color=MUTED)


def legend_below(ax, ncol, dy=-0.30):
    ax.legend(frameon=False, loc='upper center', bbox_to_anchor=(0.5, dy), ncol=ncol, handlelength=1.6,
              columnspacing=1.2, borderaxespad=0.0)


# --------------------------------------------------------------------------------------------- scheme
def fig_scheme(out, R):
    cv = Canvas(174, 88)
    ax = cv.ax
    y0, h = 66.0, 12.0
    x_sea, x0, xg, x1 = 6.0, 18.0, 90.0, 168.0
    km = (xg - x0) / 2.0
    ax.add_patch(Rectangle((x_sea, y0), x0 - x_sea, h, fc=SEA, ec='none'))
    ax.add_patch(Rectangle((x0, y0), xg - x0, h, fc=LAND, ec='none'))
    ax.add_patch(Rectangle((xg, y0), x1 - xg, h, fc=EXT, ec='#c3c8cf', hatch='////', lw=0))
    ax.add_patch(Rectangle((x_sea, y0), x1 - x_sea, h, fc='none', ec=MUTED, lw=0.6))
    cv.line([xg, xg], [y0 - 1.2, y0 + h + 1.2], c=INK, lw=1.8)
    cv.text((x_sea + x0) / 2, y0 + h / 2, 'sea', color='#1d4f87')
    cv.text((x0 + xg) / 2, y0 + h + 3.4, 'model domain Ω, 2 km', weight='bold')
    cv.text((xg + x1) / 2, y0 + h + 3.4, 'exterior, 8 km, not modelled', color=MUTED, weight='bold')
    cv.text(xg, y0 - 3.4, 'Γ: the cut', weight='bold')
    for xk, col, mk in ((0.95, ORANGE, 'v'), (1.45, BLUE, 'o'), (1.75, GREEN, 's'), (1.85, GREEN, 's')):
        ax.plot([x0 + xk * km], [y0 + h / 2], marker=mk, ms=5.0, color=col, mec='white', mew=0.6, zorder=20)
    cv.text(x0 + 0.95 * km, y0 + h - 2.3, 'well', color=ORANGE)
    cv.text(x0 + 1.45 * km, y0 + h - 2.3, 'piezometer', color=BLUE)
    cv.text(xg - 1.6, y0 + 2.4, 'two band piezometers', color=GREEN, ha='right')
    cv.box(98.0, y0 + 1.8, 63.0, h - 3.6, 'white', '#c3c8cf', lw=0.5, r=0.8, z=3)
    cv.text(129.5, y0 + h / 2, 'any heterogeneity, leaky or closed:\nit acts on Ω only through the flux at Γ', z=31)
    # arrow down to the network
    cv.arrow(152.0, y0 - 1.0, 141.2, 45.6, c=MUTED, lw=0.9, rad=-0.25)
    cv.text(140.0, 57.0, 'replaced exactly (Proposition 1) by', color=MUTED, ha='right')
    # the network
    nx, ny, gy = 24.0, 44.0, 14.0
    ax.add_patch(Circle((nx, ny), 3.0, fc='white', ec=INK, lw=0.9, zorder=26))
    cv.text(nx, ny, 'u', size=10, weight='bold', z=27)
    cv.text(nx, ny + 9.0, 'boundary cell', ha='center')
    cv.text(nx, ny + 5.6, 'u = h − $\\bar{h}$', ha='center')
    cv.line([nx, nx], [ny - 3.0, ny - 8.0], c=INK, lw=0.9)
    cv.box(nx - 2.6, ny - 16.0, 5.2, 8.0, 'white', BLUE, lw=1.0, r=0.6, z=20)
    cv.text(nx, ny - 12.0, 'C', weight='bold', color=BLUE, z=27)
    cv.line([nx, nx], [ny - 16.0, gy], c=INK, lw=0.9)
    cv.text(nx + 4.2, ny - 12.0, 'C ≥ 0; may be a\nmonotone network', ha='left', color=GREEN)
    xs, labs = [64.0, 82.0, 100.0, 140.0], ['1', '2', '3', 'M']
    cv.line([nx + 3.0, xs[-1]], [ny, ny], c=INK, lw=0.9)
    for xb, lb in zip(xs, labs):
        cv.line([xb, xb], [ny, ny - 5.0], c=INK, lw=0.9)
        cv.box(xb - 2.6, ny - 13.0, 5.2, 8.0, 'white', AQUA, lw=1.0, r=0.6, z=20)
        cv.text(xb, ny - 9.0, f'w$_{lb}$', color='#0f7a54', weight='bold', z=27)
        cv.line([xb, xb], [ny - 13.0, ny - 18.5], c=INK, lw=0.9)
        cv.line([xb - 3.6, xb + 3.6], [ny - 18.5, ny - 18.5], c=VIOLET, lw=1.6)
        cv.line([xb - 3.6, xb + 3.6], [ny - 20.4, ny - 20.4], c=VIOLET, lw=1.6)
        cv.line([xb, xb], [ny - 20.4, gy], c=INK, lw=0.9)
        cv.text(xb + 4.6 if lb != 'M' else xb - 4.6, ny - 19.5, f'σ$_{lb}$', color=VIOLET,
                ha='left' if lb != 'M' else 'right', weight='bold')
    cv.text(120.0, ny - 9.0, '· · ·', size=12, color=MUTED)
    cv.text(120.0, ny - 19.5, '· · ·', size=12, color=MUTED)
    cv.text(60.0, ny + 4.2, 'w$_m$ ≥ 0, rates μ$_m$ fixed (3–4 per decade)', ha='left', color=GREEN)
    cv.text(145.0, ny - 19.5, 'storages\nσ$_m$ = w$_m$/μ$_m$:\nkept fixed', ha='left', color=VIOLET)
    cv.line([nx - 7.0, 150.0], [gy, gy], c=INK, lw=1.4)
    for k in range(25):
        xx = nx - 6.0 + k * 7.0
        if xx < 150:
            cv.line([xx, xx - 1.6], [gy, gy - 1.6], c=INK, lw=0.7)
    cv.text(nx - 7.0, gy - 5.4, 'reference head $\\bar{h}$, with the inflow from rain q$_{in}$(t): any network may '
            'supply it, since it is only a forcing', ha='left', color=INK)
    cv.fig.savefig(out, dpi=300); plt.close(cv.fig)


# --------------------------------------------------------------------------------------------- N1
def fig_n1(out, R, Sx):
    N1 = R['N1']
    fig, axs = plt.subplots(1, 2, figsize=(174 * MM, 84 * MM), gridspec_kw=dict(width_ratios=[1.45, 1.0]))
    ax = axs[0]
    t = Sx['t'] / YR
    sel = (t >= 6) & (t <= 14)
    ax.plot(t[sel], Sx['full_bc'][sel], color=INK, lw=2.4, label='full aquifer (truth)', zorder=5)
    ax.plot(t[sel], Sx['fixed_head_bc'][sel], color=ORANGE, lw=1.1, label='fixed head')
    ax.plot(t[sel], Sx['no_flow_bc'][sel], color=VIOLET, lw=1.1, label='no flow')
    ax.plot(t[sel], Sx['ghb_calibrated_bc'][sel], color=AQUA, lw=1.1, label='calibrated GHB')
    ax.plot(t[sel], Sx['pertej_M6_bc'][sel], color=BLUE, lw=1.2, ls=(0, (4, 2)), label='PËRTEJ-GO, 6 compartments',
            zorder=6)
    GF.style(ax); ax.set_xlim(6, 14)
    ax.set_xlabel('time (years)'); ax.set_ylabel('head at the boundary cell (m)')
    ax.set_title('(a) the boundary cell, 1.95 km from the sea', fontsize=9.4)
    fig.legend(*ax.get_legend_handles_labels(), frameon=False, loc='lower left', bbox_to_anchor=(0.06, 0.0), ncol=3,
               handlelength=1.8, columnspacing=1.4)
    ax = axs[1]
    rows = [('fixed head', N1['cases']['fixed_head']['rms_bc'], REF), ('no flow', N1['cases']['no_flow']['rms_bc'], REF),
            ('calibrated GHB', N1['cases']['ghb_calibrated']['rms_bc'], REF),
            ('PËRTEJ-GO, 3', N1['cases']['pertej_M3']['rms_bc'], BLUE),
            ('PËRTEJ-GO, 6', N1['cases']['pertej_M6']['rms_bc'], BLUE),
            ('PËRTEJ-GO, 12', N1['cases']['pertej_M12']['rms_bc'], BLUE)]
    ys = np.arange(len(rows))[::-1]
    for y, (lab, v, col) in zip(ys, rows):
        ax.barh(y, v - 1e-4, height=0.62, color=col, left=1e-4)
        ax.text(v * 1.3, y, f'{1000 * v:.1f} mm' if v >= 1e-3 else f'{1000 * v:.2f} mm', va='center', fontsize=FS,
                color=INK)
    ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xscale('log'); ax.set_xlim(1e-4, 30)
    ax.xaxis.set_major_locator(FixedLocator([1e-4, 1e-2, 1]))
    ax.set_xticklabels(['0.1 mm', '1 cm', '1 m']); ax.xaxis.set_minor_locator(NullLocator())
    GF.style(ax, grid='x'); ax.set_xlabel('rms error over 20 years')
    ax.set_title('(b) error, boundary cell', fontsize=9.4)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.91, bottom=0.30, wspace=0.62)
    fig.savefig(out, dpi=300); plt.close(fig)


# --------------------------------------------------------------------------------------------- N2 + N3
def fig_n23(out, R, Sx):
    N3 = R['N3']
    fig, axs = plt.subplots(1, 3, figsize=(174 * MM, 66 * MM), gridspec_kw=dict(width_ratios=[1.15, 1.25, 0.95]))
    ax = axs[0]
    P = 2 * np.pi / Sx['n2_omega']
    for M, col in ((4, ORANGE), (8, AQUA), (13, BLUE)):
        ax.plot(P, Sx[f'n2_err_M{M}'], color=col, lw=1.3, label=f'M = {M}')
    a, b = 30 * YR / 1e4, 30 * YR
    ax.axvspan(a, b, color='#eef3fa', zorder=0, lw=0)
    ax.axhline(0.01, color=REF, lw=0.8, ls='--')
    ax.text(0.03, 0.0082, '1%', color=MUTED, fontsize=FS, va='top', transform=ax.get_yaxis_transform())
    ax.set_yscale('log'); ax.set_ylim(1e-4, 2)
    period_axis(ax, lo=0.25, hi=300 * YR, ticks=(1, YR, 100 * YR), labs=('1 d', '1 yr', '100 yr'))
    GF.style(ax); ax.set_ylabel('relative error of the boundary')
    ax.set_title('(a) half-order boundary', fontsize=9.4)
    ax.legend(frameon=False, loc='lower right', handlelength=1.4, borderaxespad=0.2)
    ax = axs[1]
    tt = Sx['n3_t'] / YR
    E0 = N3['passive']['E0']
    ax.plot(tt, Sx['n3_E_passive'] / E0, color=BLUE, lw=1.6)
    ax.plot(tt, Sx['n3_E_neg_0.02'] / E0, color=AQUA, lw=1.3)
    ax.plot(tt, Sx['n3_E_neg_0.2'] / E0, color=ORANGE, lw=1.3)
    ax.set_yscale('log'); ax.set_ylim(1e-16, 1e62)
    ax.yaxis.set_major_locator(FixedLocator([1e-15, 1e0, 1e15, 1e30, 1e45, 1e60]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.text(0.15, 1e47, 'C = −0.2c\n(above the threshold)', color=ORANGE, fontsize=FS, ha='left', va='center')
    ax.text(4.95, 3e0, 'passive (exact network)', color=BLUE, fontsize=FS, ha='right', va='bottom')
    ax.text(2.6, 1e-9, 'C = −0.02c (below it)', color='#0f7a54', fontsize=FS, ha='center', va='top')
    GF.style(ax); ax.set_xlim(0, 5)
    ax.set_xlabel('time (years)'); ax.set_ylabel('energy / initial energy')
    ax.set_title('(b) energy, unforced model', fontsize=9.4)
    ax = axs[2]
    L = [r['L_km'] for r in N3['length_test']]
    rate = np.array([r['rate_per_day'] * 1e4 for r in N3['length_test']])
    lo = -6.0
    shown = np.maximum(rate, lo)
    cols = [AQUA if v < 0 else ORANGE for v in rate]
    ax.bar(np.arange(len(L)), shown, color=cols, width=0.62)
    ax.axhline(0, color=INK, lw=0.7)
    for k, v in enumerate(rate):
        if v < lo:
            ax.text(k + 0.36, lo + 0.15, f'{v:.0f} (axis cut)'.replace('-', '−'), ha='left', va='bottom',
                    fontsize=FS, color=INK)
        else:
            ax.text(k, v + (0.2 if v > 0 else -0.2), f'{v:+.1f}'.replace('-', '−'), ha='center',
                    va='bottom' if v > 0 else 'top',
                    fontsize=FS)
    ax.set_xticks(np.arange(len(L))); ax.set_xticklabels([f'{x:g}' for x in L])
    ax.set_ylim(lo, 4.6)
    GF.style(ax); ax.set_ylabel('growth rate (10⁻⁴ per day)')
    ax.set_xlabel('model length (km)')
    ax.set_title('(c) longer models', fontsize=9.4)
    fig.tight_layout(w_pad=1.0)
    fig.savefig(out, dpi=300); plt.close(fig)


# --------------------------------------------------------------------------------------------- N4
def fig_n4(out, R, Sx):
    N4 = R['N4']
    fig = plt.figure(figsize=(174 * MM, 150 * MM))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.95], hspace=0.78, wspace=0.26)
    P = 2 * np.pi / Sx['n4_omega']
    ax = fig.add_subplot(gs[0, 0])
    shade_bands(ax)
    ax.plot(P, Sx['n4_Z_exact'], color=INK, lw=2.4, label='exact exterior')
    ax.plot(P, Sx['n4_Z_broadband_2mm'], color=BLUE, lw=1.3, label='varied pumping, 2 mm')
    ax.plot(P, Sx['n4_Z_seasonal_2mm'], color=AQUA, lw=1.3, label='steady pumping, 2 mm')
    ax.plot(P, Sx['n4_Z_seasonal_10mm'], color=ORANGE, lw=1.3, label='steady pumping, 10 mm')
    period_axis(ax); ax.set_yscale('log'); ax.set_ylim(0.01, 400)
    GF.style(ax); ax.set_ylabel('|Z| (m/d)')
    ax.set_title('(a) excitation and noise', fontsize=9.4)
    legend_below(ax, 2, dy=-0.27)
    ax = fig.add_subplot(gs[0, 1])
    shade_bands(ax)
    ax.plot(P, Sx['n4_Z_exact'], color=INK, lw=2.4, label='exact exterior')
    ax.plot(P, Sx['n4_Z_psi_outside_band'], color=BLUE, lw=1.3,
            label=f'closure at {N4["psi_outside_band"]["cell_km"]:.2f} km (outside)')
    ax.plot(P, Sx['n4_Z_psi_in_band'], color=ORANGE, lw=1.3,
            label=f'closure at {N4["psi_in_band"]["cell_km"]:.2f} km (in the band)')
    period_axis(ax); ax.set_yscale('log'); ax.set_ylim(0.01, 400)
    GF.style(ax); ax.set_ylabel('|Z| (m/d)')
    ax.set_title('(b) an unmodelled source near the cut', fontsize=9.4)
    legend_below(ax, 1, dy=-0.27)
    ax = fig.add_subplot(gs[1, :])
    t = Sx['n4_pred_t'] / YR
    ax.axvspan(3, 8, color='#fdf0e6', lw=0, zorder=0)
    ax.text(5.5, 0.03, 'drought: recharge × 0.3', transform=ax.get_xaxis_transform(), ha='center', va='bottom',
            fontsize=FS, color='#a8461b')
    ax.axvline(2, color=REF, lw=0.8, ls='--')
    ax.text(2.07, 0.97, 'pumping 0.6 → 1.2 m²/d', transform=ax.get_xaxis_transform(), ha='left', va='top', fontsize=FS,
            color=MUTED)
    ax.plot(t, Sx['n4_pred_full'], color=INK, lw=2.4, label='full aquifer (truth)', zorder=5)
    ax.plot(t, Sx['n4_pred_ghb'], color=REF, lw=1.3, label='calibrated GHB', zorder=4)
    ax.plot(t, Sx['n4_pred_seasonal_10mm'], color=ORANGE, lw=1.2, label='PËRTEJ-GO, steady pumping, 10 mm')
    ax.plot(t, Sx['n4_pred_broadband_2mm'], color=BLUE, lw=1.3, ls=(0, (4, 2)), label='PËRTEJ-GO, varied pumping, 2 mm',
            zorder=6)
    GF.style(ax); ax.set_xlim(0, 10); ax.set_ylim(-1.55, 2.4)
    ax.set_xlabel('time (years)'); ax.set_ylabel('head at the boundary cell (m)')
    ax.set_title('(c) a regime never seen in the data: prediction at the boundary cell', fontsize=9.4)
    ax.legend(frameon=False, loc='upper right', ncol=1, handlelength=1.8, borderaxespad=0.2)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.955, bottom=0.07)
    fig.savefig(out, dpi=300); plt.close(fig)


# --------------------------------------------------------------------------------------------- N5
def fig_n5(out, R, Sx):
    N5 = R['N5']
    fig, axs = plt.subplots(1, 2, figsize=(174 * MM, 84 * MM), gridspec_kw=dict(width_ratios=[1.3, 1.0]))
    P = 2 * np.pi / Sx['n4_omega']
    ax = axs[0]
    shade_bands(ax, short=True)
    ax.fill_between(P, Sx['n5_near_Z_q05'], Sx['n5_near_Z_q95'], color='#e3defa', lw=0,
                    label=f'right prior, {N5["priors"]["near"]["K"]} exteriors (5–95%)')
    ax.plot(P, Sx['n4_Z_exact'], color=INK, lw=2.4, label='exact exterior')
    ax.plot(P, Sx['n4_Z_seasonal_2mm'], color=ORANGE, lw=1.2, label='data only')
    ax.plot(P, Sx['n5_Z_near_seasonal_2mm'], color=BLUE, lw=1.4, ls=(0, (4, 2)), label='data + right prior')
    period_axis(ax); ax.set_yscale('log'); ax.set_ylim(0.005, 400)
    GF.style(ax); ax.set_ylabel('|Z| (m/d)')
    ax.set_title('(a) steady pumping, 2 mm noise', fontsize=9.4)
    legend_below(ax, 2, dy=-0.25)
    ax = axs[1]
    keys = [('seasonal_2mm', 'steady, 2 mm'), ('seasonal_10mm', 'steady, 10 mm'), ('broadband_2mm', 'varied, 2 mm'),
            ('broadband_10mm', 'varied, 10 mm')]
    y = np.arange(len(keys))[::-1]
    for k, (key, lab) in enumerate(keys):
        cse = N5['cases'][key]
        a = cse['pred_rms_bc_plain'] * 1000
        b = cse['near']['pred_rms_bc'] * 1000
        d = cse['shifted']['pred_rms_bc'] * 1000
        ax.plot([min(a, b, d), max(a, b, d)], [y[k], y[k]], color=REF, lw=1.0, zorder=1)
        ax.scatter([a], [y[k]], color=ORANGE, s=36, zorder=3, label='data only' if k == 0 else None)
        ax.scatter([d], [y[k]], color=VIOLET, s=30, marker='s', zorder=3, label='+ wrong prior' if k == 0 else None)
        ax.scatter([b], [y[k]], color=BLUE, s=34, marker='D', zorder=4, label='+ right prior' if k == 0 else None)
    ghb = R['N4']['prediction_reference']['ghb_calibrated'] * 1000
    ax.axvline(ghb, color=REF, lw=0.8, ls='--')
    ax.text(ghb * 1.1, y[0] + 0.15, f'calibrated\nGHB: {ghb:.0f}', ha='left', va='center', fontsize=FS, color=MUTED)
    ax.set_yticks(y); ax.set_yticklabels([lab for _, lab in keys])
    ax.set_xscale('log'); ax.set_xlim(2, 3000); ax.set_ylim(-1.5, len(keys) - 0.3)
    ax.xaxis.set_major_locator(FixedLocator([3, 10, 30, 100, 300, 1000]))
    ax.set_xticklabels(['3', '10', '30', '100', '300', '1000']); ax.xaxis.set_minor_locator(NullLocator())
    GF.style(ax, grid='x'); ax.set_xlabel('prediction error (mm)')
    ax.set_title('(b) the new regime of Figure 4c', fontsize=9.4)
    ax.legend(frameon=True, facecolor='white', edgecolor='none', framealpha=1.0, loc='lower right', handlelength=1.0,
              borderaxespad=0.2)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.91, bottom=0.31, wspace=0.42)
    fig.savefig(out, dpi=300); plt.close(fig)


def main(out):
    os.makedirs(out, exist_ok=True)
    R, Sx = load()
    fig_scheme(os.path.join(out, 'fig_scheme.png'), R)
    fig_n1(os.path.join(out, 'fig_n1.png'), R, Sx)
    fig_n23(os.path.join(out, 'fig_n23.png'), R, Sx)
    fig_n4(os.path.join(out, 'fig_n4.png'), R, Sx)
    fig_n5(os.path.join(out, 'fig_n5.png'), R, Sx)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'figs'))
