"""Figures of the synthesis article (the trace and the rhythm, reviews 42 and 43):
  figA1_system.png  the augmented transient system drawn on a Fushë-Kuqe cross-section: heads then and now, the
                    two aquifer horizons with silt-clay lenses and the salt wedge, wells and the abstraction field,
                    forcings, and four insets (memory zones, exchanger, reaction in the clay, assimilation loop);
                    the numbers in brackets are equation numbers of the article
  figA2_atlas.png   the time-scale atlas: on one axis of period, what the system remembers (sensitivity of the
                    response to each rate), what forces it, what the data resolve and what the goals need
  figA3_cut.png     chloride sufficiency: the price of the cut in goal precision and its protection against a
                    misspecified reactive closure (linearised RITMI-GO), and the nonlinear twin of GJURMA-GO
Colours: water and salinity use one blue ramp; categorical slots: system blue, forcing orange, data green, goals
ink; neutral greys for geology."""
import json
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyBboxPatch, Circle, FancyArrowPatch, Ellipse
from matplotlib.patches import ConnectionPatch
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#c3c2b7', 'xtick.color': '#52514e', 'ytick.color': '#52514e',
                     'axes.labelcolor': '#0b0b0b'})
INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#898781', '#e1e0d9'
RAMP = ['#cfe2f7', '#86b6ef', '#2a78d6', '#104281']
BLUE, ORANGE, GREEN, AQUA = '#2a78d6', '#eb6834', '#1baf7a', '#0e9aa7'
SAND, SAND2, CLAY, CLAY2, AQT = '#f4ead2', '#efe1bf', '#b8a488', '#9c8a70', '#ddd1bd'
SEA = '#9cc3ec'


def box(ax, x, y, w, h, fc, ec, lw=0.8, r=0.02, z=2, alpha=1.0):
    p = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=%g' % r, fc=fc, ec=ec, lw=lw, zorder=z,
                       alpha=alpha, transform=ax.transAxes)
    ax.add_patch(p)
    return p


def arrow(ax, p0, p1, col=INK2, lw=1.0, ms=8, z=6, style='-|>', ls='-', trans=None, rad=0.0):
    a = FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms, color=col, lw=lw, zorder=z, linestyle=ls,
                        connectionstyle='arc3,rad=%g' % rad, transform=trans if trans is not None else ax.transData)
    ax.add_patch(a)
    return a


# ====================================================================================== A1: the system
def fig_system():
    fig = plt.figure(figsize=(10.8, 7.6))
    gs = fig.add_gridspec(3, 4, height_ratios=[0.95, 3.1, 1.75], hspace=0.20, wspace=0.16,
                          left=0.055, right=0.985, top=0.965, bottom=0.025)
    X0, X1 = -2.6, 15.0
    # ---------------------------------------------------------------- heads then and now
    ah = fig.add_subplot(gs[0, :])
    x = np.linspace(0, X1, 400)
    sm = lambda v: np.convolve(np.pad(v, 12, mode='edge'), np.ones(25) / 25, mode='valid')
    h_now = sm(np.interp(x, [0, 1, 2, 3.5, 5, 6, 7, 8.5, 10, 12, 15], [0, 0.4, 0.8, 1.2, 1.4, 1.5, 2.6, 4.2, 5.4, 6.5, 7.6]))
    h_then = sm(np.interp(x, [0, 0.6, 1.5, 3, 6, 10, 15], [0, 4.0, 6.2, 7.4, 8.0, 8.4, 9.0]))
    ah.fill_between([X0, 0], -0.8, 0, color=SEA, lw=0, alpha=0.7)
    ah.plot(x, h_then, color=MUTED, lw=1.4, ls=(0, (4, 2)), label='artesian head before pumping (about 8 m)')
    ah.plot(x, h_now, color=BLUE, lw=1.8, label='head today: 1.5 m at the field')
    ah.fill_between(x, h_now, h_then, color=RAMP[0], alpha=0.55, lw=0)
    tt = np.linspace(X0 + 0.15, -0.15, 200)
    ah.plot(tt, 0.35 * np.sin(2 * np.pi * (tt - X0) / 0.55), color=RAMP[3], lw=1.1)
    ah.text(X0 + 0.1, 1.15, 'tide $h_{sea}(t)$  [6]', fontsize=7.6, color=RAMP[3])
    ah.annotate('', xy=(6.0, 1.75), xytext=(6.0, 7.75), arrowprops=dict(arrowstyle='-|>', color=ORANGE, lw=1.2))
    ah.text(5.85, 4.7, 'drawdown 8.0 → 1.5 m\nafter the 1970s increase\nof pumping', fontsize=7.0,
            color=ORANGE, va='center', ha='right')
    ah.text(9.0, 2.2, 'heads: fast clock, $t_h=L^2/D_h\\approx1$ day  [1, 3]', fontsize=7.4, color=INK2)
    ah.set_xlim(X0, X1); ah.set_ylim(-0.8, 10.5)
    ah.set_ylabel('head (m a.s.l.)'); ah.set_xticks([])
    ah.spines['bottom'].set_visible(False)
    ah.legend(frameon=False, fontsize=7.2, loc='upper left', bbox_to_anchor=(0.12, 1.08), ncol=2)
    ah.grid(axis='y', color=GRID, lw=0.5); ah.set_axisbelow(True)

    # ---------------------------------------------------------------- cross-section
    ax = fig.add_subplot(gs[1, :])
    Z0, Z1 = -135.0, 22.0
    ax.set_xlim(X0, X1); ax.set_ylim(Z0, Z1)
    ground = lambda xx: 1.5 + 0.55 * np.asarray(xx, float)
    seafloor = lambda xx: -4 + 2.0 * np.asarray(xx, float)
    b_aqt = lambda xx: -16 - 0.6 * np.asarray(xx, float) * (np.asarray(xx) > 0)
    b_up = lambda xx: -52 - 1.0 * np.asarray(xx, float) * (np.asarray(xx) > 0)
    t_low = lambda xx: -60 - 1.0 * np.asarray(xx, float) * (np.asarray(xx) > 0)
    b_low = lambda xx: -112 - 0.8 * np.asarray(xx, float) * (np.asarray(xx) > 0)
    xg = np.linspace(0, X1, 300)
    xo = np.linspace(X0, 0, 60)
    xa = np.linspace(X0, X1, 500)
    # bedrock, sea-floor sediment, layers
    ax.fill_between(xa, Z0, b_low(xa), color='#cbbfae', lw=0, zorder=1, hatch='////', edgecolor='#b3a794')
    ax.fill_between(xo, b_aqt(xo), seafloor(xo), color=AQT, lw=0, zorder=1)
    ax.fill_between(xg, b_aqt(xg), ground(xg), color=AQT, lw=0, zorder=1)
    up_poly = Polygon(np.r_[np.c_[xa, b_aqt(xa)], np.c_[xa[::-1], b_up(xa[::-1])]], closed=True, fc=SAND, ec='none',
                      zorder=1)
    lo_poly = Polygon(np.r_[np.c_[xa, t_low(xa)], np.c_[xa[::-1], b_low(xa[::-1])]], closed=True, fc=SAND2,
                      ec='none', zorder=1)
    ax.add_patch(up_poly); ax.add_patch(lo_poly)
    ax.fill_between(xa, t_low(xa), b_up(xa), color=CLAY, lw=0, zorder=1, alpha=0.6)
    ax.add_patch(Polygon([(X0, 0), (0, 0), (0, -4), (X0, seafloor(X0))], closed=True, fc=SEA, ec='none', zorder=1))
    ax.plot([X0, 0], [0, 0], color=RAMP[3], lw=1.0, zorder=3)
    # silt-clay lenses (fixed positions; the first one is the anchor of inset a)
    lenses = [(1.7, -88), (0.6, -30), (3.9, -95), (7.4, -100), (8.6, -42), (9.6, -108), (10.6, -47),
              (11.2, -104), (13.2, -55), (14.1, -113), (2.6, -45), (6.9, -80), (12.6, -116)]
    for xc, zc in lenses:
        ax.add_patch(Ellipse((xc, zc), 0.9, 3.2, fc=CLAY2, ec='none', alpha=0.8, zorder=2.6))
    # salinity wedge in each horizon (saltier below), clipped to the horizon outlines
    XX, ZZ = np.meshgrid(np.linspace(X0, X1, 900), np.linspace(Z0, 0, 600))
    s_up = 0.55 / (1 + np.exp((XX - (3.3 + 0.025 * (-ZZ - 16))) / 0.5))
    s_lo = 1.0 / (1 + np.exp((XX - (5.0 + 0.03 * (-ZZ - 60))) / 0.6))
    cmap = LinearSegmentedColormap.from_list('salt', [(1, 1, 1, 0.0), (0.53, 0.71, 0.94, 0.55),
                                                      (0.16, 0.47, 0.84, 0.72), (0.06, 0.26, 0.51, 0.80)])
    for field, poly in [(s_up, up_poly), (s_lo, lo_poly)]:
        im = ax.imshow(field, extent=(X0, X1, Z0, 0), origin='lower', aspect='auto', cmap=cmap, vmin=0, vmax=1,
                       zorder=2.5, interpolation='bilinear')
        im.set_clip_path(poly)
        cs = ax.contour(XX, ZZ, field, levels=[0.12], colors=[RAMP[3]], linewidths=0.8, linestyles=[(0, (2, 1.5))],
                        zorder=3)
        cs.set_clip_path(poly)
    ax.text(4.75, -37, 'toe of the\nupper horizon', fontsize=6.8, color=RAMP[3], ha='left', va='center')
    ax.text(8.0, -86, 'toe of the lower horizon\n(saltier, ≈3,500 mg/L)', fontsize=6.8, color=RAMP[3], ha='left',
            va='center')
    ax.plot(xg, ground(xg), color=INK2, lw=0.9, zorder=4)
    # wells (positions as in GJURMA/RITMI: assumed, the source gives none)
    for xw, nm in [(1.1, '503'), (2.1, '341'), (4.5, '340'), (12.1, '193')]:
        zt = float(ground(xw))
        ax.plot([xw, xw], [zt + 3.0, float(b_low(xw)) + 6], color=INK, lw=1.1, zorder=5)
        for z0, z1 in [(float(b_aqt(xw)) - 10, float(b_up(xw)) + 10), (float(t_low(xw)) - 12, float(b_low(xw)) + 12)]:
            ax.plot([xw, xw], [z0, z1], color=INK, lw=3.0, zorder=5, solid_capstyle='butt')
        ax.text(xw, zt + 4.0, nm, ha='center', va='bottom', fontsize=7.6, color=INK, fontweight='bold')
    for dx in (-0.25, 0.0, 0.25):
        xw = 6.0 + dx
        zt = float(ground(xw))
        ax.plot([xw, xw], [zt + 2.0, float(b_low(xw)) + 4], color=ORANGE, lw=1.0, zorder=5)
        ax.plot([xw, xw], [float(t_low(xw)) - 10, float(b_low(xw)) + 8], color=ORANGE, lw=2.6, zorder=5,
                solid_capstyle='butt')
    arrow(ax, (6.0, float(ground(6.0)) + 2.5), (6.0, float(ground(6.0)) + 15.5), col=ORANGE, lw=1.6, ms=10)
    ax.text(6.4, float(ground(6.0)) + 4.0, 'abstraction field Gorre–Fushë-Kuqe\n≈750 L/s,  $Q_w(t)$  [1]',
            fontsize=7.2, color=ORANGE, va='bottom')
    # flow arrows: landward from the coast, field-ward from inland, recharge from above
    for x0, z0, dxa in [(2.3, -82, 1.4), (4.0, -88, 1.3), (1.3, -24, 1.1), (3.4, -40, 1.0)]:
        arrow(ax, (x0, z0), (x0 + dxa, z0 - 1.5), col=RAMP[3], lw=1.2, ms=8, z=6)
    ax.text(2.35, -77, '$\\mathbf{v}(t)$ landward  [7]', fontsize=7.0, color='white', zorder=7)
    for x0, z0 in [(10.4, -98), (9.9, -38)]:
        arrow(ax, (x0, z0), (x0 - 1.6, z0 + 0.6), col=INK2, lw=1.1, ms=8)
    for xr in (13.0, 13.8, 14.6):
        arrow(ax, (xr, float(ground(xr)) + 10), (xr, float(ground(xr)) + 1.2), col=GREEN, lw=1.1, ms=8)
    ax.text(13.8, float(ground(13.8)) + 10.6, 'recharge $q(t)$  [4]', fontsize=7.2, color=GREEN, ha='center')
    # labels of the layers, centred in each layer at the right edge
    xl = 14.85
    for zc, lab in [((float(ground(xl)) + float(b_aqt(xl))) / 2, 'confining silt-clay (artesian cap)'),
                    ((float(b_aqt(xl)) + float(b_up(xl))) / 2, 'upper horizon'),
                    ((float(b_up(xl)) + float(t_low(xl))) / 2, 'silt-clay interlayer'),
                    ((float(t_low(xl)) + float(b_low(xl))) / 2 + 6, 'lower horizon')]:
        ax.text(xl, zc, lab, fontsize=6.9, color=INK2, ha='right', va='center', zorder=8)
    ax.text(X0 + 0.15, -9.5, 'Adriatic Sea', fontsize=7.6, color=RAMP[3], fontweight='bold', zorder=8)
    ax.text(0.2, -129, 'salt: slow clock, $t_a=\\phi L/|\\mathbf{q}|\\approx100$ yr;  $\\varepsilon=t_h/t_a\\sim10^{-5}$'
            '  [3]   ·   vertical exaggeration ≈ 50×, schematic', fontsize=7.0, color=INK2, zorder=8)
    ax.set_ylabel('elevation (m a.s.l.)')
    ax.set_xticks([0, 2, 4, 6, 8, 10, 12, 14])
    ax.set_xticklabels(['0 km', '2', '4', '6', '8', '10', '12', '14 km'])
    # anchors of the insets (drawn in display units so they stay round)
    anchors = [(1.7, -88), (3.0, -33), (7.5, -63.5), (12.1, -96)]
    for px, pz in anchors:
        ax.plot([px], [pz], marker='o', ms=13, mfc='none', mec=INK, mew=1.0, zorder=9)

    # ---------------------------------------------------------------- insets
    titles = ['(a) memory of the silt and clay zones', '(b) cation exchange on the clays',
              '(c) reaction inside the clay', '(d) assimilation in time']
    axs = [fig.add_subplot(gs[2, k]) for k in range(4)]
    for k, a in enumerate(axs):
        a.set_xlim(0, 1); a.set_ylim(0, 1); a.axis('off')
        a.add_patch(FancyBboxPatch((0.005, 0.005), 0.99, 0.99, boxstyle='round,pad=0,rounding_size=0.03',
                                   fc='#fbfaf6', ec='#c3c2b7', lw=0.8, transform=a.transAxes, zorder=0))
        a.text(0.04, 0.93, titles[k], fontsize=7.8, fontweight='bold', color=INK, va='top')
        con = ConnectionPatch(xyA=anchors[k], coordsA=ax.transData, xyB=(0.5, 1.0), coordsB=a.transAxes,
                              color=MUTED, lw=0.7, ls=(0, (2, 2)), zorder=0)
        fig.add_artist(con)
    # (a) mobile channel between a silt and a clay block
    a = axs[0]
    a.add_patch(Rectangle((0.06, 0.60), 0.88, 0.16, fc=SAND2, ec=CLAY2, lw=0.6))
    a.text(0.08, 0.68, 'silt  $c_1$:  rate $a_1\\approx1$ yr$^{-1}$, capacity $b_1$', fontsize=6.7, va='center')
    a.add_patch(Rectangle((0.06, 0.41), 0.88, 0.14, fc=RAMP[1], ec='none', alpha=0.6))
    a.text(0.35, 0.48, 'mobile water  $c$', ha='center', va='center', fontsize=7.2, color=RAMP[3])
    a.add_patch(Rectangle((0.06, 0.16), 0.88, 0.20, fc=CLAY, ec=CLAY2, lw=0.6, alpha=0.8))
    a.text(0.08, 0.26, 'clay  $c_2$:  $a_2\\approx0.05$ yr$^{-1}$, $b_2$', fontsize=6.7, va='center')
    arrow(a, (0.80, 0.44), (0.80, 0.66), col=INK, lw=1.0, ms=7, style='<|-|>')
    arrow(a, (0.88, 0.52), (0.88, 0.26), col=INK, lw=1.0, ms=7, style='<|-|>')
    a.text(0.5, 0.045, '$\\kappa(s)=b_1a_1e^{-a_1s}+b_2a_2e^{-a_2s}$  [8, 10]', ha='center', fontsize=7.0)
    # (b) exchanger platelet with cations
    a = axs[1]
    a.add_patch(Rectangle((0.08, 0.42), 0.84, 0.08, fc=CLAY, ec=CLAY2, lw=0.6))
    a.text(0.5, 0.46, 'clay surface, capacity $E$', ha='center', va='center', fontsize=6.6, color='white')
    for xi, lab, col in [(0.16, 'Na$^+$', BLUE), (0.32, 'Ca$^{2+}$', ORANGE), (0.48, 'Mg$^{2+}$', GREEN),
                         (0.64, 'Na$^+$', BLUE), (0.80, 'K$^+$', AQUA)]:
        a.plot([xi], [0.58], marker='o', ms=9, color=col, alpha=0.9, mec='none')
        a.text(xi, 0.66, lab, ha='center', fontsize=6.6, color=INK)
    arrow(a, (0.13, 0.22), (0.13, 0.38), col=BLUE, lw=1.0, ms=7)
    arrow(a, (0.22, 0.38), (0.22, 0.22), col=ORANGE, lw=1.0, ms=7)
    a.text(0.28, 0.30, 'salinisation: Na$^+$ taken up,\nCa$^{2+}$, Mg$^{2+}$ released (503, 341)', fontsize=6.4,
           va='center')
    a.text(0.5, 0.06, '$\\partial_t(\\mathbf{c}+E\\,\\mathbf{s}(\\mathbf{c}))$, Gaines–Thomas  [7, 9]',
           ha='center', fontsize=7.0)
    # (c) sulfate reduction in organic clay
    a = axs[2]
    a.add_patch(Rectangle((0.06, 0.22), 0.88, 0.50, fc=CLAY, ec=CLAY2, lw=0.6, alpha=0.75))
    for xi, yi in [(0.14, 0.29), (0.30, 0.27), (0.52, 0.29), (0.70, 0.26), (0.86, 0.29)]:
        a.plot([xi], [yi], marker='o', ms=4.5, color='#4a3b2a', mec='none')
    a.text(0.5, 0.60, 'SO$_4^{2-}$ + 2 CH$_2$O → HS$^-$ + 2 HCO$_3^-$ + H$^+$', ha='center', fontsize=6.6)
    a.text(0.5, 0.45, 'rate $k_{sr}$, inside zone 2 only', ha='center', fontsize=6.8)
    a.text(0.5, 0.10, 'steady data see only\n$r_{eff}=b_2a_2k_{sr}/(a_2+k_{sr})$  [20]', ha='center', va='center',
           fontsize=6.9)
    # (d) assimilation loop
    a = axs[3]
    nodes = [(0.25, 0.67, 'data $\\mathbf{y}_n$: heads,\ntides, Cl, ions'), (0.75, 0.67, 'filter: EnKF\nor map  [26]'),
             (0.75, 0.31, 'state $\\mathbf{z}_n$  [13]\n$(h,\\mathbf{c},\\mathbf{c}_k,\\mathbf{s},\\theta)$'),
             (0.25, 0.31, 'design $u_n$, $H_n$;\nrobust report  [27–29]')]
    for xn, yn, lab in nodes:
        a.add_patch(FancyBboxPatch((xn - 0.215, yn - 0.105), 0.43, 0.21, boxstyle='round,pad=0,rounding_size=0.03',
                                   fc='white', ec=MUTED, lw=0.7))
        a.text(xn, yn, lab, ha='center', va='center', fontsize=6.1)
    for (p0, p1) in [((0.465, 0.67), (0.535, 0.67)), ((0.75, 0.565), (0.75, 0.415)),
                     ((0.535, 0.31), (0.465, 0.31)), ((0.25, 0.415), (0.25, 0.565))]:
        arrow(a, p0, p1, col=BLUE, lw=1.0, ms=6)
    a.text(0.5, 0.07, '$\\mathbf{z}_{n+1}=\\mathcal{M}(\\mathbf{z}_n,u_n;\\theta)+\\eta_n$  [14]', ha='center',
           fontsize=7.0)
    fig.savefig('figA1_system.png', dpi=220)
    plt.close(fig)


# ====================================================================================== A2: time-scale atlas
YR = 365.25


def fig_atlas():
    rows = [
        ('h', 'WHAT THE SYSTEM REMEMBERS', RAMP[3]),
        ('ridge', 'flow storage, fast zone ($a=1$ d$^{-1}$)', 1.0),
        ('ridge', 'flow storage, slow zone ($a=1/60$ d$^{-1}$)', 1 / 60.0),
        ('ridge', 'transport memory, silt ($a_1=1$ yr$^{-1}$)', 1.0 / YR),
        ('ridge', 'transport memory, clay ($a_2=0.05$ yr$^{-1}$)', 0.05 / YR),
        ('fade', 'cation exchange $E$, selectivities (no rate)', (0.6 * YR, 300 * YR, RAMP[2])),
        ('steady', 'clay memory × sulfate reduction, $r_{eff}$', RAMP[3]),
        ('h', 'WHAT FORCES IT', ORANGE),
        ('lines', 'tides M2, K1, MSf, Sa', [(0.5175, 'M2'), (0.9973, 'K1'), (14.765, 'MSf'), (365.24, 'Sa')]),
        ('lines', 'seasonal recharge', [(365.25, '1 yr'), (182.6, '½ yr')]),
        ('band', 'designed pumping 2026–2031', (0.25 * YR, 5 * YR, ORANGE)),
        ('band', 'pumping history 1975 / 1990 / 2000', (10 * YR, 50 * YR, ORANGE)),
        ('band', 'passage of the salt front ($t_a\\approx100$ yr)', (30 * YR, 300 * YR, ORANGE)),
        ('h', 'WHAT THE DATA RESOLVE', GREEN),
        ('band', 'head and tide loggers (15 min, 1 yr)', (1 / 48.0, YR, GREEN)),
        ('band', 'monthly Cl, wells 503, 341, 340 (5 yr)', (2 * 30.4, 5 * YR, GREEN)),
        ('band', 'half-yearly major ions (5 yr)', (YR, 5 * YR, GREEN)),
        ('band', 'Cl 1984, 1999, 2001 and 2016', (4 * YR, 32 * YR, GREEN)),
        ('steady', 'one survey of seven ions (2016)', GREEN),
        ('h', 'WHAT THE GOALS NEED', INK),
        ('fade', 'Cl and Na in 2045 under status-quo pumping', (20 * YR, 2000 * YR, INK2)),
        ('steady', 'capacity $1+b_1+b_2$ (effective velocity)', INK2),
    ]
    n = len(rows)
    fig = plt.figure(figsize=(10.8, 6.9))
    gs = fig.add_gridspec(1, 2, width_ratios=[14, 1.25], wspace=0.03, left=0.30, right=0.985, top=0.94,
                          bottom=0.075)
    ax = fig.add_subplot(gs[0, 0]); axs = fig.add_subplot(gs[0, 1], sharey=ax)
    T = np.logspace(-2, 5.6, 900)
    w = 2 * np.pi / T
    ax.set_xscale('log'); ax.set_xlim(T[0], T[-1]); ax.set_ylim(-0.6, n - 0.4)
    axs.set_xlim(0, 1)
    # guides: tidal constituents and the peaks 2 pi / a of the four rates
    for p, _ in rows[8][2]:
        ax.axvline(p, color=ORANGE, lw=0.6, ls=(0, (2, 2)), alpha=0.6, zorder=0)
    for r in rows:
        if r[0] == 'ridge':
            ax.axvline(2 * np.pi / r[2], color=RAMP[2], lw=0.6, ls=(0, (1, 2)), alpha=0.7, zorder=0)
    labels = []
    for i, r in enumerate(rows):
        y = n - 1 - i
        kind, lab = r[0], r[1]
        if kind == 'h':
            ax.axhspan(y - 0.5, y + 0.5, color='#f5f4ef', lw=0, zorder=0)
            axs.axhspan(y - 0.5, y + 0.5, color='#f5f4ef', lw=0, zorder=0)
            fig.text(0.008, ax.transData.transform((1, y))[1] / fig.dpi / fig.get_figheight(), lab,
                     fontsize=7.6, fontweight='bold', color=r[2], va='center')
            labels.append(''); continue
        labels.append(lab)
        if kind == 'ridge':
            a = r[2]
            sens = 2 * (w / a) / (1 + (w / a) ** 2)
            ax.fill_between(T, y - 0.38, y - 0.38 + 0.80 * sens, color=RAMP[1], alpha=0.75, lw=0)
            ax.plot(T, y - 0.38 + 0.80 * sens, color=RAMP[3], lw=1.0)
            tp = 2 * np.pi / a
            ax.text(tp / 4.5, y + 0.16, 'peak at $2\\pi/a$ = ' + (f'{tp:.1f} d' if tp < 300 else f'{tp / YR:.0f} yr'),
                    fontsize=6.4, color=RAMP[3], va='center', ha='right')
        elif kind in ('band', 'fade'):
            lo, hi, col = r[2]
            if kind == 'band':
                ax.add_patch(Rectangle((lo, y - 0.30), hi - lo, 0.60, fc=col, alpha=0.32, ec=col, lw=0.8))
            else:
                xs = np.logspace(np.log10(lo), np.log10(min(hi, T[-1])), 120)
                for x0, x1 in zip(xs[:-1], xs[1:]):
                    t = (np.log10(x0) - np.log10(lo)) / (np.log10(hi) - np.log10(lo))
                    al = 0.42 * np.sin(np.pi * min(max(t, 0), 1)) ** 0.6 if r[1].startswith('cation') else 0.12 + 0.30 * t
                    ax.add_patch(Rectangle((x0, y - 0.30), x1 - x0, 0.60, fc=col, alpha=al, ec='none'))
        elif kind == 'lines':
            for p, nm in r[2]:
                ax.plot([p, p], [y - 0.32, y + 0.32], color=ORANGE, lw=2.0, solid_capstyle='butt')
                ax.text(p * 1.12, y + 0.18, nm, fontsize=6.4, color=ORANGE, va='center')
        elif kind == 'steady':
            axs.add_patch(Rectangle((0.15, y - 0.30), 0.7, 0.60, fc=r[2], alpha=0.55, ec=r[2], lw=0.8))
    # explanatory notes in the rows
    note = dict(fontsize=6.4, color=INK2, va='center')
    yy = lambda i: n - 1 - i
    ax.text(0.05, yy(5), 'enters as $\\lambda E J_s$: seen by any change of composition, never at steady state',
            **note)
    ax.text(0.05, yy(6), 'only this product survives at steady state (Prop. 6)', **note)
    ax.text(0.05, yy(18), 'a single date sees $\\omega\\to0$ only', **note)
    ax.text(0.05, yy(20), 'slow forcing: needs the capacity and the clay rate, not $a_1$ (Cor. 2)', **note)
    ax.set_yticks([n - 1 - i for i in range(n)]); ax.set_yticklabels(labels, fontsize=7.2)
    ax.tick_params(axis='y', length=0)
    plt.setp(axs.get_yticklabels(), visible=False); axs.tick_params(axis='y', length=0)
    ax.set_xlabel('period of the forcing or of the response, $T=2\\pi/\\omega$ (days)')
    axs.set_xticks([0.5]); axs.set_xticklabels(['steady\n$\\omega\\to0$'], fontsize=7.0)
    for a_ in (ax, axs):
        a_.spines['left'].set_visible(False)
    axs.spines['bottom'].set_visible(True)
    sec = ax.secondary_xaxis('top')
    sec.set_xticks([1 / 24, 1, 7, 30.4, YR, 10 * YR, 100 * YR])
    sec.set_xticklabels(['hour', 'day', 'week', 'month', 'year', 'decade', 'century'], fontsize=7.2)
    sec.spines['top'].set_visible(False); sec.tick_params(length=2)
    ax.grid(axis='x', color=GRID, lw=0.5, which='major'); ax.set_axisbelow(True)
    fig.savefig('figA2_atlas.png', dpi=220)
    plt.close(fig)


# ====================================================================================== A3: the cut
def fig_cut():
    cut = json.load(open('synth_cut.json'))
    twin = json.load(open(os.path.join('..', 'gjurma_go', 'gjurma_summary.json')))['twin']
    fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.55), gridspec_kw=dict(width_ratios=[1.35, 1.15, 1.0]))
    plt.subplots_adjust(left=0.06, right=0.99, top=0.86, bottom=0.2, wspace=0.32)
    # (a) goal precision by data set and fitting strategy, relative to the prior
    sets = [('history', RAMP[0]), ('Cl only', GREEN), ('ions only', AQUA), ('joint', RAMP[3]), ('cut', ORANGE)]
    gl = ['Cl at 5 km', 'Na at 3 km', 'Ca + Mg at 3 km']
    x = np.arange(3); bw = 0.16
    pri = np.array(cut['goal_sd']['prior'])
    for k, (nm, col) in enumerate(sets):
        v = np.array(cut['goal_sd'][nm]) / pri
        ax[0].bar(x + (k - 2) * bw, v, bw * 0.92, color=col, label=nm)
    ax[0].set_yscale('log'); ax[0].set_ylim(3e-3, 0.6)
    ax[0].set_xticks(x); ax[0].set_xticklabels(gl)
    ax[0].set_ylabel('posterior sd / prior sd (log)')
    ax[0].grid(axis='y', color=GRID, lw=0.5, which='both'); ax[0].set_axisbelow(True)
    ax[0].legend(frameon=False, fontsize=6.8, ncol=5, loc='upper center', bbox_to_anchor=(0.5, -0.12),
                 handlelength=1.2, columnspacing=0.9)
    sj, sc = cut['goal_sd']['joint'], cut['goal_sd']['cut']
    for i in range(3):
        ax[0].text(i + 2 * bw, sc[i] / pri[i] * 1.18, f'+{100 * (sc[i] / sj[i] - 1):.0f}%', ha='center', fontsize=6.5,
                   color=ORANGE)
    ax[0].set_title('(a) the price of the cut in precision', fontsize=8.5)
    # (b) protection: shift of the Cl goal when one ion's data are biased by one error sd
    ions = ['Na', 'K', 'Ca', 'Mg', 'SO4', 'HCO3']
    sh = cut['shift_one_sd']
    vj = [abs(sh[i]['joint'][0]) for i in ions] + [cut['shift_worst_rms1']['joint'][0]]
    vc = [abs(sh[i]['cut'][0]) for i in ions] + [cut['shift_worst_rms1']['cut'][0]]
    xl = ['Na', 'K', 'Ca', 'Mg', 'SO$_4$', 'HCO$_3$', 'worst case\n(RMS 1 sd)']
    xx = np.arange(7) + np.r_[np.zeros(6), 0.5]
    ax[1].bar(xx - 0.19, vj, 0.36, color=RAMP[3], label='joint')
    ax[1].bar(xx + 0.19, np.maximum(vc, 0.0), 0.36, color=ORANGE, label='cut (exactly 0)')
    for xi in xx:
        ax[1].plot([xi + 0.19], [0.0], marker='_', ms=7, mew=2, color=ORANGE)
    ax[1].axhline(sj[0], color=INK2, lw=0.8, ls=(0, (3, 2)))
    ax[1].text(0.0, sj[0] + 0.22, f'joint posterior sd, {sj[0]:.1f} mg/L', fontsize=6.6, color=INK2)
    ax[1].set_xticks(xx); ax[1].set_xticklabels(xl, fontsize=7.2)
    ax[1].set_ylabel('shift of Cl at 5 km in 2045 (mg/L)')
    ax[1].text(xx[-1], vj[-1] * 0.5, f'{vj[-1]:.1f}', color='white', ha='right', fontsize=6.8,
               va='center', rotation=90)
    ax[1].legend(frameon=False, fontsize=6.8, loc='upper left', bbox_to_anchor=(0.0, 0.92))
    ax[1].grid(axis='y', color=GRID, lw=0.5); ax[1].set_axisbelow(True)
    ax[1].set_title('(b) protection against a wrong closure', fontsize=8.5)
    # (c) nonlinear twin of review 42: coverage, joint against cut
    gl4 = ['Cl at 5 km', 'Na at 3 km', 'Ca + Mg 3 km', 'strip > 250']
    cj, cc = twin['gjurma']['cover90'], twin['gjurma_cut']['cover90']
    yv = np.arange(4)[::-1]
    for i in range(4):
        ax[2].annotate('', xy=(100 * cc[i], yv[i]), xytext=(100 * cj[i], yv[i]),
                       arrowprops=dict(arrowstyle='-|>', color=MUTED, lw=1.0, shrinkA=4, shrinkB=4))
    ax[2].scatter(100 * np.array(cj), yv, color=RAMP[3], s=26, zorder=3, label='joint')
    ax[2].scatter(100 * np.array(cc), yv, color=ORANGE, s=26, zorder=3, label='cut')
    ax[2].axvline(90, color=INK2, lw=0.8, ls=(0, (3, 2)))
    ax[2].text(89, 3.45, 'nominal 90%', fontsize=6.6, color=INK2, ha='right')
    ax[2].set_yticks(yv); ax[2].set_yticklabels(gl4, fontsize=7.2)
    ax[2].set_xlim(40, 104); ax[2].set_ylim(-0.5, 3.7)
    ax[2].set_xlabel('coverage of the 90% interval (%)')
    ax[2].legend(frameon=False, fontsize=6.8, loc='lower left')
    ax[2].grid(axis='x', color=GRID, lw=0.5); ax[2].set_axisbelow(True)
    ax[2].set_title('(c) nonlinear twin (40 truths)', fontsize=8.5)
    fig.savefig('figA3_cut.png', dpi=220)
    plt.close(fig)


if __name__ == '__main__':
    fig_system()
    fig_atlas()
    fig_cut()
