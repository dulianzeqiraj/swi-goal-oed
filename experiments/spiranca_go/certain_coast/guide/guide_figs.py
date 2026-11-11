"""Figures of the illustrated CERTAIN-COAST guide: seawater intrusion, sensors, warnings, earthquakes, liquefaction.

Reads the results of guide_compute.m (res/*.mat: the open-source MATLAB package run in GNU Octave) and of the
earthquake and liquefaction experiment (../../../tronditja_go/res), computes the closed-form figures (freshwater lens,
upconing) and writes fig/figNN_*.png at 300 dpi. Every number drawn comes from those results or from the equations
quoted in the guide.

usage: python guide_figs.py [OUTDIR]"""
import json
import os
import sys
from math import erfc

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402
from scipy.io import loadmat  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
TR = os.path.join(HERE, '..', '..', '..', 'tronditja_go')
sys.path.insert(0, TR)
import liq  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'fig')
os.makedirs(OUT, exist_ok=True)

# Okabe-Ito categorical order (colour-blind safe), ink colours for text
BLUE, ORANGE, GREEN, VERM, SKY, PURPLE, YELLOW = '#0072B2', '#E69F00', '#009E73', '#D55E00', '#56B4E9', '#CC79A7', '#F0E442'
INK, MUTED, GRID = '#222222', '#666666', '#DDDDDD'
SEA = LinearSegmentedColormap.from_list('sea', ['#F7FBFF', '#C6DBEF', '#6BAED6', '#2171B5', '#08306B'])
HEAD = LinearSegmentedColormap.from_list('head', ['#F7FCF5', '#C7E9C0', '#74C476', '#238B45', '#00441B'])
INFO = LinearSegmentedColormap.from_list('info', ['#FFF5EB', '#FDD0A2', '#FD8D3C', '#D94801', '#7F2704'])
DIVERGE = LinearSegmentedColormap.from_list('div', ['#08519C', '#6BAED6', '#EEEEEE', '#FB6A4A', '#A50F15'])
W = 6.3                                    # text width (inches)

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 8.5, 'axes.titlesize': 9, 'axes.labelsize': 8.5,
    'axes.edgecolor': '#444444', 'axes.labelcolor': INK, 'xtick.color': '#444444', 'ytick.color': '#444444',
    'text.color': INK, 'axes.spines.top': False, 'axes.spines.right': False, 'legend.frameon': False,
    'legend.fontsize': 7.5, 'lines.linewidth': 1.6, 'savefig.dpi': 300, 'figure.dpi': 100,
    'axes.titleweight': 'bold', 'axes.titlelocation': 'left'})


def mat(name):
    return loadmat(os.path.join(RES, name + '.mat'), squeeze_me=True)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.png'), bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('saved', name)


def panel(ax, letter):
    ax.text(-0.02, 1.02, letter, transform=ax.transAxes, fontsize=10, fontweight='bold', ha='right', va='bottom')


TRS = np.load(os.path.join(TR, 'res', 'tronditja_series.npz'))
TRJ = json.load(open(os.path.join(TR, 'res', 'tronditja.json')))


# ------------------------------------------------------------------------------------------------ 1 the system
def fig_system():
    fig, ax = plt.subplots(figsize=(W, 3.7))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis('off')

    def box(x, y, w, h, text, fc, ec, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.6,rounding_size=2.2', fc=fc, ec=ec, lw=1.2))
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=7.6,
                fontweight='bold' if bold else 'normal', color=INK, linespacing=1.25)

    def arrow(p, q, color=MUTED, rad=0.0, style='-|>', lw=1.3):
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=11, color=color, lw=lw,
                                     connectionstyle=f'arc3,rad={rad}'))

    box(31, 49, 38, 7.5, 'Relative sea level\n(sea-level rise + land subsidence)', '#DEEBF7', BLUE, True)
    box(2, 30, 25, 9, 'Seawater intrusion\nsalt reaches the\nsupply wells', '#FDE0DD', VERM)
    box(37.5, 30, 25, 9, 'Water table and\npore pressure rise', '#E5F5E0', GREEN)
    box(73, 30, 25, 9, 'Extreme sea levels\nflooding of the port\nand the landfall', '#EFEDF5', PURPLE)
    box(73, 14, 25, 9, 'Earthquake\nshaking and a sudden\npore-pressure step', '#FEF0D9', ORANGE)
    box(37.5, 14, 25, 9, 'Liquefaction\nthe sand loses its\nstrength', '#FEF0D9', ORANGE)
    box(2, 14, 25, 9, 'Sensors\nheads, salinity, GNSS,\nseismic stations', '#F0F0F0', MUTED)
    box(14, 0.8, 72, 7, 'Model + certified alarm\ndaily bulletin, its miss rate stated in advance', '#DEEBF7', BLUE, True)
    arrow((44, 49), (15, 39.6))
    arrow((50, 49), (50, 39.6))
    arrow((56, 49), (85, 39.6))
    arrow((50, 30), (50, 23.6))
    arrow((73, 18.5), (63.2, 18.5))
    arrow((37.5, 32.5), (27.6, 32.5), color=VERM)
    ax.text(32.5, 35.0, 'pumping', fontsize=6.4, color=VERM, ha='center')
    arrow((14.5, 14), (30, 8.6), color=MUTED)
    ax.text(87.6, 4.3, 'every outcome\nlogged: the miss\nrate is checked', fontsize=6.0, color=BLUE, ha='left',
            va='center')
    save(fig, 'fig01_system')


# ------------------------------------------------------------------------------------------------ 2 freshwater lens
def lens(x, L, W_, K, delta):
    return np.sqrt(2 * W_ / (K * (1 + 1 / delta)) * (L * x - x ** 2 / 2))


def fig_lens():
    L, K, delta = 2000.0, 30.0, 0.025
    x = np.linspace(0, L, 400)
    fig, ax = plt.subplots(figsize=(W, 2.9))
    ax.axhspan(-80, 0, xmin=0, xmax=1, color='#F4F8FC', zorder=0)
    for rate, col, lab in ((200, BLUE, 'recharge 200 mm/yr'), (100, VERM, 'recharge 100 mm/yr (drought or pumping)')):
        h = lens(x, L, rate / 1000 / 365.25, K, delta)
        z = -h / delta
        if rate == 200:
            ax.fill_between(x, z, h, color='#DEEBF7', lw=0)
        else:
            ax.fill_between(x, -lens(x, L, 0.2 / 365.25, K, delta) / delta, z, color=VERM, alpha=0.12, lw=0,
                            label='fresh water lost')
        ax.plot(x, -h / delta, color=col, label=f'interface, {lab}')
        ax.plot(x, h, color=col, lw=1.0, ls='--')
    h200 = lens(L, L, 0.2 / 365.25, K, delta)
    h100 = lens(L, L, 0.1 / 365.25, K, delta)
    ax.annotate(f'water table {h200:.2f} m above sea level', xy=(L * 0.97, h200), xytext=(L * 0.52, 9),
                fontsize=7, color=BLUE, arrowprops=dict(arrowstyle='-', color=BLUE, lw=0.8))
    ax.annotate(f'fresh water reaches {h200 / delta:.0f} m below sea level  (= 40 x {h200:.2f} m)',
                xy=(L * 0.97, -h200 / delta), xytext=(L * 0.33, -h200 / delta - 16), fontsize=7, color=BLUE,
                arrowprops=dict(arrowstyle='-', color=BLUE, lw=0.8))
    ax.annotate(f'half the recharge: the interface rises {h200 / delta - h100 / delta:.0f} m',
                xy=(L * 0.75, -lens(L * 0.75, L, 0.1 / 365.25, K, delta) / delta), xytext=(L * 0.20, -20),
                fontsize=7, color=VERM, arrowprops=dict(arrowstyle='-', color=VERM, lw=0.8))
    ax.text(30, -73, 'sea water', fontsize=8, color='#2171B5', style='italic')
    ax.text(L * 0.58, -6, 'fresh water', fontsize=8, color=INK, style='italic')
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_xlim(0, L)
    ax.set_ylim(-80, 14)
    ax.set_xlabel('distance from the coast (m)')
    ax.set_ylabel('elevation (m above sea level)')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=6.8)
    save(fig, 'fig02_lens')


# ------------------------------------------------------------------------------------------------ 3 Henry field
def fig_henry():
    d = mat('henry')
    c, xc, yc, qx, qy = d['c'], d['xc'], d['yc'], d['qxc'], d['qyc']
    fig, ax = plt.subplots(figsize=(W, 3.35))
    cf = ax.contourf(xc, yc, c, levels=np.linspace(0, 1, 21), cmap=SEA)
    cs = ax.contour(xc, yc, c, levels=[0.1, 0.5, 0.9], colors=['#08306B'], linewidths=[0.7, 1.4, 0.7])
    ax.clabel(cs, fmt='%.1f', fontsize=6.5, inline_spacing=2)
    sk = (slice(2, None, 4), slice(3, None, 6))
    X, Y = np.meshgrid(xc, yc)
    ax.quiver(X[sk], Y[sk], qx[sk], qy[sk], color='#333333', scale=6e-3, width=0.0026, headwidth=4, alpha=0.85)
    toe = float(d['toes'][-1])
    ax.plot(toe, 0.012, marker='^', ms=8, color=VERM, mec='white', clip_on=False, zorder=5)
    ax.annotate(f'toe {toe:.3f} m', xy=(toe, 0.03), xytext=(toe - 0.45, 0.14), fontsize=7.5, color=VERM,
                arrowprops=dict(arrowstyle='-', color=VERM, lw=0.8))
    ax.text(0.03, 0.035, 'fresh water flows in from the left', fontsize=7.5, color=INK,
            bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='none', alpha=0.85))
    ax.text(1.97, 0.93, 'sea', fontsize=7.5, color='white', ha='right', fontweight='bold')
    ax.set_aspect('equal')
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    cb = fig.colorbar(cf, ax=ax, fraction=0.025, pad=0.02, ticks=[0, 0.25, 0.5, 0.75, 1])
    cb.set_label('relative salinity c (0 fresh, 1 sea)', fontsize=7.5)
    save(fig, 'fig03_henry')


def fig_inflow():
    d = mat('henry_inflow')
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.6), gridspec_kw=dict(width_ratios=[1.2, 1], wspace=0.38))
    panel(a, 'a')
    panel(b, 'b')
    cols = [VERM, INK, BLUE]
    for j, (fq, col) in enumerate(zip([0.6, 1.0, 1.4], cols)):
        a.contour(d['xQ'], d['yQ'], d['cQ'][:, :, j], levels=[0.5], colors=[col], linewidths=1.6)
        a.plot([], [], color=col, label=f'inflow x {fq:.1f}')
    a.set_aspect('equal')
    a.set_xlim(1.0, 2.0)
    a.set_ylim(0, 1)
    a.set_xlabel('x (m)')
    a.set_ylabel('y (m)')
    a.set_title('the 0.5 isochlor')
    a.legend(loc='upper left', fontsize=7)
    a.text(1.97, 0.04, 'sea at the right', ha='right', color=BLUE, fontsize=7, style='italic')
    wedge = 2.0 - d['toeQ']
    b.plot(d['qf'], wedge, color=BLUE, marker='o', ms=4)
    b.set_xlabel('freshwater inflow (x Henry value)')
    b.set_ylabel('length of the salt wedge (m)')
    b.set_title('less fresh water, longer wedge')
    b.grid(color=GRID, lw=0.6)
    save(fig, 'fig04_inflow')


# ------------------------------------------------------------------------------------------------ 5 upconing
def fig_upconing():
    K, d_, delta = 50.0, 20.0, 0.025
    Q = np.linspace(0, 1600, 300)
    z = Q / (2 * np.pi * d_ * K * delta)
    qmax = 0.6 * np.pi * d_ ** 2 * K * delta
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.7), gridspec_kw=dict(width_ratios=[1, 1.25], wspace=0.3))
    panel(a, 'a')
    panel(b, 'b')
    r = np.linspace(-60, 60, 400)
    zc = 6.0 * (d_ / np.sqrt(r ** 2 + d_ ** 2))           # schematic cone shape
    a.fill_between(r, -45, -30 + zc, color='#C6DBEF')
    a.fill_between(r, -30 + zc, 0, color='#F7FBFF')
    a.plot(r, -30 + zc, color=BLUE, lw=1.6)
    a.plot(r, np.full_like(r, -30), color=BLUE, lw=1.0, ls='--')
    a.add_patch(Rectangle((-1.5, -10), 3, 10, color='#555555'))
    a.annotate('', xy=(4, -10), xytext=(4, -30), arrowprops=dict(arrowstyle='<->', color=INK, lw=0.9))
    a.text(6, -21, 'd', fontsize=9, style='italic')
    a.annotate('', xy=(-6, -30), xytext=(-6, -24), arrowprops=dict(arrowstyle='<->', color=VERM, lw=0.9))
    a.text(-17, -28.5, 'z', fontsize=9, style='italic', color=VERM)
    a.text(-58, -42, 'sea water', fontsize=7.5, color='#2171B5', style='italic')
    a.text(-58, -6, 'fresh water', fontsize=7.5, style='italic')
    a.text(4, -4, 'well', fontsize=7.5)
    a.set_xlim(-60, 60)
    a.set_ylim(-45, 0)
    a.axis('off')
    a.set_title('schematic')
    b.plot(Q, z / d_, color=BLUE)
    b.axhline(0.3, color=VERM, lw=1.0, ls='--')
    b.axvspan(qmax, Q.max(), color=VERM, alpha=0.08, lw=0)
    b.text(qmax + 30, 0.05, f'unstable:\nsalt enters\nthe well', color=VERM, fontsize=7)
    b.annotate(f'Q max = {qmax:.0f} m$^3$/day', xy=(qmax, 0.3), xytext=(150, 0.42), fontsize=7.5, color=VERM,
               arrowprops=dict(arrowstyle='-', color=VERM, lw=0.8))
    b.set_xlabel('pumping rate Q (m$^3$/day)')
    b.set_ylabel('rise of the interface z / d')
    b.set_title('K = 50 m/day, d = 20 m')
    b.set_xlim(0, Q.max())
    b.set_ylim(0, 0.55)
    b.grid(color=GRID, lw=0.6)
    save(fig, 'fig05_upconing')


# ------------------------------------------------------------------------------------------------ 6 Fushë-Kuqe
def fig_fushe_kuqe():
    d = mat('fushe_kuqe')
    xs, ys, B, Wk = d['xsF'], d['ysF'], d['Bk'], d['Wk']
    ids = [str(s) for s in np.atleast_1d(d['wellID'])]
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 4.6))
    for ax, field, cmap, lab, letter in ((a, d['hMap'], HEAD, 'head (m above sea level)', 'a'),
                                         (b, d['eMap'], INFO, 'information about the intruded area (nats)', 'b')):
        panel(ax, letter)
        m = ax.pcolormesh(xs, ys, field, cmap=cmap, shading='nearest', rasterized=True)
        ax.plot(B[:, 0], B[:, 1], color='#333333', lw=0.7)
        ax.plot(Wk[:, 0], Wk[:, 1], '.', color='#333333', ms=2.5)
        ax.set_aspect('equal')
        ax.set_xlabel('km')
        ax.set_ylabel('km')
        cb = fig.colorbar(m, ax=ax, fraction=0.04, pad=0.02)
        cb.set_label(lab, fontsize=7)
    a.contourf(xs, ys, np.where(np.isfinite(d['hMap']), d['hMap'], np.nan), levels=[-1, 1.0], colors=[VERM],
               alpha=0.28)
    a.contour(xs, ys, d['hMap'], levels=[1.0], colors=[VERM], linewidths=1.2)
    a.set_title(f'intruded zone (h < 1 m): {float(d["baseArea"]):.1f} km$^2$')
    for group, mk, col, ms in ((d['monID'], 'o', BLUE, 10), (d['marID'], 'D', GREEN, 5.5)):
        for wid in np.atleast_1d(group):
            k = ids.index(str(wid))
            b.plot(Wk[k, 0], Wk[k, 1], mk, ms=ms, mfc=col, mec='white', mew=0.8, zorder=5)
    for wid in sorted(set(map(str, np.atleast_1d(d['monID']))) | set(map(str, np.atleast_1d(d['marID'])))):
        k = ids.index(wid)
        b.text(Wk[k, 0] + 1.4, Wk[k, 1] + 0.2, wid, fontsize=6.8, fontweight='bold', va='center',
               path_effects=[pe.withStroke(linewidth=2.2, foreground='white')])
    b.plot([], [], 'o', mfc=BLUE, mec='white', label='monitoring wells')
    b.plot([], [], 'D', mfc=GREEN, mec='white', label='recharge (MAR) sites')
    b.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=6.8)
    b.set_title('where a new head reading informs most')
    save(fig, 'fig06_fushe_kuqe')


# ------------------------------------------------------------------------------------------------ 7-8 sensors
def fig_sensor_map():
    d = mat('sensors_henry')
    fig, ax = plt.subplots(figsize=(W, 3.3))
    m = ax.pcolormesh(d['xS'], d['yS'], d['eigMap'], cmap=INFO, shading='nearest', rasterized=True)
    cs = ax.contour(d['xS'], d['yS'], d['cS'], levels=[0.1, 0.5, 0.9], colors=['#08306B'],
                    linewidths=[0.6, 1.2, 0.6], linestyles='-')
    ax.clabel(cs, fmt='c=%.1f', fontsize=6, inline_spacing=2)
    zx, zy = d['zoneX'], d['zoneY']
    ax.add_patch(Rectangle((zx[0], zy[0]), zx[1] - zx[0], zy[1] - zy[0], fill=False, ec=BLUE, lw=1.4, ls='--'))
    ax.text(zx[0] + 0.01, zy[1] + 0.02, 'goal: salt mass in this zone', fontsize=7, color=BLUE)
    for k, (x, y) in enumerate(zip(np.atleast_1d(d['sx']), np.atleast_1d(d['sy']))):
        ax.plot(x, y, 'o', ms=8.5, mfc='white', mec=INK, mew=0.9, zorder=5)
        ax.text(x, y, str(k + 1), ha='center', va='center', fontsize=6, fontweight='bold', zorder=6)
    ax.set_aspect('equal')
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    cb = fig.colorbar(m, ax=ax, fraction=0.025, pad=0.02)
    cb.set_label('information of one sensor (nats)', fontsize=7.5)
    save(fig, 'fig07_sensor_map')


def fig_returns():
    d = mat('sensors_henry')
    g, rnd = np.atleast_1d(d['greedyCurve']), d['randGains']
    k = np.arange(1, g.size + 1)
    fig, ax = plt.subplots(figsize=(W * 0.72, 2.6))
    bp = ax.boxplot([rnd[:, j] for j in range(g.size)], positions=k, widths=0.45, patch_artist=True,
                    showfliers=False, medianprops=dict(color=MUTED, lw=1.2))
    for patch in bp['boxes']:
        patch.set(facecolor='#EEEEEE', edgecolor='#AAAAAA')
    for item in bp['whiskers'] + bp['caps']:
        item.set(color='#AAAAAA')
    ax.plot(k, g, color=ORANGE, marker='o', ms=5, label='goal-oriented design (greedy)')
    ax.plot([], [], 's', color='#DDDDDD', mec='#AAAAAA', ms=8, label='300 random designs (box: middle half)')
    for kk, gg in zip(k, g):
        ax.text(kk, gg + 0.07, f'{gg:.2f}', ha='center', fontsize=6.8, color=ORANGE)
    ax.set_xlabel('number of salinity sensors')
    ax.set_ylabel('information about the goal (nats)')
    ax.set_ylim(0, max(g) * 1.15)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=7)
    ax.grid(axis='y', color=GRID, lw=0.6)
    save(fig, 'fig08_returns')


# ------------------------------------------------------------------------------------------------ 9-10 between samples
def fig_between_path():
    d = mat('between')
    t, x = d['pathT'], 180 + 35 * d['pathX']
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.8), gridspec_kw=dict(width_ratios=[1.45, 1], wspace=0.34))
    panel(a, 'a')
    panel(b, 'b')
    l1, = a.plot(t, x, color=MUTED, lw=0.7, label='chloride every 6 hours')
    a.axhline(250, color=VERM, lw=1.1)
    a.text(4, 258, 'limit 250 mg/L', color=VERM, fontsize=7,
           bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85))
    over = x >= 250
    a.fill_between(t, 250, x, where=over, color=VERM, alpha=0.35, lw=0)
    ts = np.arange(0, 365, 91)
    xs = np.interp(ts, t, x)
    l2, = a.plot(ts, xs, 'o', ls='none', ms=6, mfc=BLUE, mec='white', label='quarterly samples', zorder=5)
    ups = np.sum(np.diff(over.astype(int)) == 1)
    a.set_title(f'{ups} crossings, {int(np.sum(xs >= 250))} seen by the samples', fontsize=8)
    a.set_xlabel('day')
    a.set_ylabel('chloride (mg/L)')
    a.legend(handles=[l1, l2], loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=6.8)
    a.set_xlim(0, 365)
    tc = 1 / d['kGrid']
    b.plot(tc, d['curve'], color=BLUE)
    tail = 0.5 * erfc(float(d['z']) / np.sqrt(2))
    b.axhline(tail, color=MUTED, lw=1.0, ls='--')
    b.text(1.5, tail + 0.03, f'samples alone: {tail:.3f}', fontsize=7, color=MUTED)
    b.plot(8, float(d['truthP']), 'o', color=VERM, ms=6)
    b.annotate(f'8 days: {float(d["truthP"]):.2f}', xy=(8, float(d['truthP'])), xytext=(18, 0.62), fontsize=7.5,
               color=VERM, arrowprops=dict(arrowstyle='-', color=VERM, lw=0.8))
    b.set_xscale('log')
    b.set_xlabel('correlation time of chloride (days)')
    b.set_ylabel('P(crossing in a 120-day season)')
    b.set_ylim(0, 1.03)
    b.grid(color=GRID, lw=0.6)
    save(fig, 'fig09_between_path')


def fig_between_bands():
    d = mat('between')
    names = ['quarterly samples', 'monthly samples', 'weekly samples', 'daily logger']
    lo, hi = d['bandLo'], d['bandHi']
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.6), gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.45))
    panel(a, 'a')
    panel(b, 'b')
    for i, n in enumerate(names):
        y = 3 - i
        m_lo, m_hi = np.median(lo[:, i]), np.median(hi[:, i])
        a.plot([m_lo, m_hi], [y, y], color=BLUE, lw=8, solid_capstyle='butt')
        a.text(-0.02, y, n, ha='right', va='center', fontsize=7.5)
        a.text(m_lo - 0.015, y, f'{m_lo:.2f}', ha='right', va='center', fontsize=6.8, color=BLUE)
        a.text(m_hi + 0.015, y, f'{m_hi:.2f}', ha='left', va='center', fontsize=6.8, color=BLUE)
    a.axvline(float(d['truthP']), color=VERM, lw=1.2, ls='--')
    a.text(float(d['truthP']) - 0.02, 3.55, 'truth', color=VERM, fontsize=7, ha='right')
    a.set_xlim(0, 1.12)
    a.set_ylim(-0.6, 3.8)
    a.set_yticks([])
    a.spines['left'].set_visible(False)
    a.set_xlabel('warning band: P(crossing in the season)')
    tau, info = d['tau'], d['info']
    b.plot(tau, info, color=BLUE)
    for s, n in zip(d['steps_'], ['quarterly', 'monthly', 'weekly', 'daily']):
        v = np.interp(s, tau, info)
        b.plot(s, v, 'o', color=ORANGE, ms=5)
        b.text(s * 1.25, v * 1.6, n, fontsize=6.8)
    b.set_xscale('log')
    b.set_yscale('log')
    b.set_ylim(1e-10, 3)
    b.set_xlabel('days between two samples')
    b.set_ylabel('information per pair (x $\\kappa^2$)')
    b.grid(color=GRID, lw=0.6, which='major')
    save(fig, 'fig10_between_bands')


# ------------------------------------------------------------------------------------------------ 11 recharge
def fig_recharge():
    d = mat('recharge')
    n = d['Pr'].size
    t = np.arange(n)
    fig, axs = plt.subplots(3, 1, figsize=(W, 4.6), sharex=True,
                            gridspec_kw=dict(height_ratios=[1, 1.1, 1.2], hspace=0.32))
    for ax, letter in zip(axs, 'abc'):
        panel(ax, letter)
    axs[0].bar(t, d['Pr'], width=1.0, color=SKY)
    axs[0].set_ylabel('rain (mm/day)')
    axs[1].plot(t, d['hObs'], color=MUTED, lw=0.6, label='logger, 1 cm noise')
    axs[1].plot(t, d['hTrue'], color=GREEN, lw=1.2, label='true head')
    axs[1].set_ylabel('head (m)')
    axs[1].legend(loc='upper left', fontsize=6.8, ncol=2)
    edges = np.arange(1, n + 30, 30)
    edges[-1] = n
    mt = np.add.reduceat(d['Rtrue'][1:], edges[:-1] - 1)[:len(edges) - 1]
    mh = np.add.reduceat(np.nan_to_num(d['Rhat'][1:]), edges[:-1] - 1)[:len(edges) - 1]
    mid = edges[:-1] + 15
    axs[2].bar(mid - 6, mt, width=11, color=GREEN, label='true recharge')
    axs[2].bar(mid + 6, mh, width=11, color=ORANGE, label='estimated from the heads')
    axs[2].set_ylabel('recharge (mm / 30 days)')
    axs[2].legend(loc='upper center', fontsize=6.8, ncol=2)
    axs[2].set_ylim(-15, 200)
    axs[2].set_xlabel('day (from 1 September)')
    rmse = np.sqrt(np.mean((mh - mt) ** 2))
    print(f'  recharge: monthly error {rmse:.2f} mm, mean {np.mean(mt):.2f} mm')
    save(fig, 'fig11_recharge')


# ------------------------------------------------------------------------------------------------ 12 boundary
def fig_boundary():
    d = mat('boundary')
    t = d['tp'] / 365.25
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.8), gridspec_kw=dict(width_ratios=[1.5, 1]))
    panel(a, 'a')
    panel(b, 'b')
    a.axvspan(3, 8, color='#FDD0A2', alpha=0.35, lw=0)
    a.text(5.5, 0.92, 'drought: rain x 0.3', ha='center', fontsize=7, color='#A63603', transform=a.get_xaxis_transform())
    a.axvline(2, color=MUTED, lw=0.8, ls=':')
    a.text(1.9, 0.05, 'pumping\ndoubled', fontsize=6.8, color=MUTED, ha='right', transform=a.get_xaxis_transform())
    a.plot(t, d['bN'], color=ORANGE, lw=1.2, label='no-flow boundary')
    a.plot(t, d['bF'], color=VERM, lw=1.2, label='fixed-head boundary')
    a.plot(t, d['bRef'], color=INK, lw=2.4, label='the whole aquifer (truth)')
    a.plot(t, d['bL'], color=SKY, lw=1.2, ls='--', label='boundary learned from 2 piezometers')
    a.set_xlabel('years')
    a.set_ylabel('head at the model boundary (m)')
    a.legend(loc='upper center', bbox_to_anchor=(0.62, -0.2), ncol=2, fontsize=6.6)
    period = 2 * np.pi / d['om']
    b.plot(period, d['Zx'], color=INK, lw=2.4, label=f'exact ({int(d["nComp"])} compartments)')
    b.plot(period, d['Zl'], color=SKY, lw=1.3, ls='--', label='learned (12)')
    b.set_xscale('log')
    b.set_yscale('log')
    b.set_xlabel('period of the forcing (days)')
    b.set_ylabel('|Z| boundary impedance (m/day)')
    b.legend(loc='upper right', fontsize=6.6)
    b.grid(color=GRID, lw=0.6)
    save(fig, 'fig12_boundary')


# ------------------------------------------------------------------------------------------------ 13 alarm
def fig_alarm():
    d = mat('alarm')
    t, y, f, alarm, ev = d['tA'], d['truthA'], d['forecastA'], d['alarmA'].astype(bool), d['events'].astype(bool)
    s = slice(600, 720)
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.8), gridspec_kw=dict(width_ratios=[1.6, 1], wspace=0.3))
    panel(a, 'a')
    panel(b, 'b')
    tt = t[s]
    a.fill_between(tt, 0, 1, where=alarm[s], transform=a.get_xaxis_transform(), color=ORANGE, alpha=0.18, lw=0,
                   label='alarm on')
    a.plot(tt, y[s], color=INK, lw=0.9, label='observed chloride')
    a.plot(tt, f[s], color=BLUE, lw=1.0, label='forecast')
    a.plot(tt, f[s] + float(d['margin']), color=SKY, lw=1.0, ls='--', label=f'forecast + margin ({float(d["margin"]):.1f})')
    a.axhline(250, color=VERM, lw=1.1)
    hit = ev[s]
    a.plot(tt[hit], y[s][hit], 'o', ms=3.5, color=VERM, label='dangerous event')
    a.set_xlabel('time step')
    a.set_ylabel('chloride (mg/L)')
    a.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), fontsize=6.3, ncol=3)
    a.set_title(f'whole test: {int(d["nEvents"])} events, {int(d["nMiss"])} missed, {int(d["nFalse"])} false alarms', fontsize=8)
    b.plot(d['evGrid'], d['cp0'], color=GREEN, label='no miss')
    b.plot(d['evGrid'], d['cp10'], color=PURPLE, label='10% missed')
    b.axhline(0.10, color=MUTED, ls='--', lw=1.0)
    b.text(197, 0.115, 'stated rate 0.10', fontsize=7, color=MUTED, ha='right')
    b.set_xlabel('dangerous events logged')
    b.set_ylabel('95% upper bound on the miss rate')
    b.set_ylim(0, 1)
    b.set_xlim(0, 200)
    b.legend(loc='upper right', fontsize=7)
    b.grid(color=GRID, lw=0.6)
    save(fig, 'fig13_alarm')


# ------------------------------------------------------------------------------------------------ 14-16 earthquakes
def fault_outline(src):
    phi, dip = np.radians(src['strike']), np.radians(src['dip'])
    s = np.array([np.sin(phi), np.cos(phi)])
    dd = np.array([np.cos(phi), -np.sin(phi)])
    hl, hw = src['L_km'] / 2, src['W_km'] / 2 * np.cos(dip)
    corners = [hl * s - hw * dd, hl * s + hw * dd, -hl * s + hw * dd, -hl * s - hw * dd]
    top = [hl * s - hw * dd, -hl * s - hw * dd]           # up-dip edge
    return np.array(corners), np.array(top)


def fig_quake_maps():
    x = TRS['e2_x'] / 1e3
    srcs = TRJ['E2']['sources']
    fig, axs = plt.subplots(2, 2, figsize=(W, 5.6), sharex=True, sharey=True)
    vmax = 1.0
    for ax, src in zip(axs.flat, srcs):
        dh = TRS[f'e2_dh_{src["key"]}']
        m = ax.pcolormesh(x, x, dh, cmap=DIVERGE, norm=TwoSlopeNorm(0, -vmax, 0.5), shading='nearest',
                          rasterized=True)
        ax.contour(x, x, dh, levels=[-0.5, -0.1, 0.1], colors=['#333333'], linewidths=0.5, linestyles='-')
        corners, top = fault_outline(src)
        ax.add_patch(Polygon(corners, closed=True, fill=False, ec=INK, lw=1.0, ls='--'))
        ax.plot(top[:, 0], top[:, 1], color=INK, lw=2.0)
        ax.set_title(f'{src["label"]}, Mw {src["mw"]:.2f}', fontsize=7.6)
        ax.set_aspect('equal')
        ax.set_xlim(-40, 40)
        ax.set_ylim(-40, 40)
    for ax in axs[1]:
        ax.set_xlabel('east (km)')
    for ax in axs[:, 0]:
        ax.set_ylabel('north (km)')
    fig.subplots_adjust(bottom=0.15, wspace=0.12, hspace=0.25)
    cax = fig.add_axes([0.22, 0.045, 0.6, 0.018])
    cb = fig.colorbar(m, cax=cax, extend='both', orientation='horizontal')
    cb.set_label('sudden head change in a confined aquifer (m)', fontsize=7.5)
    save(fig, 'fig14_quake_maps')


def fig_quake_transect():
    s = TRS['e2_tr_s'] / 1e3
    fig, ax = plt.subplots(figsize=(W * 0.8, 2.6))
    for key, col in zip(['ganas', 'matraku', 'govorcin', 'vdheiden'], [BLUE, ORANGE, GREEN, PURPLE]):
        lab = next(v['label'] for v in TRJ['E2']['sources'] if v['key'] == key)
        ax.plot(s, TRS[f'e2_tr_{key}'], color=col, lw=1.4, label=lab)
    ax.plot(s, TRS['e2_tr_soft_mean'], color=INK, lw=1.0, ls='--', label='soft surface sand (mean of the four)')
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.set_xlabel('distance across the strike, towards N250 (km)')
    ax.set_ylabel('head change (m)')
    ax.legend(loc='lower left', fontsize=6.6)
    ax.grid(color=GRID, lw=0.6)
    save(fig, 'fig15_quake_transect')


def fig_natural_test():
    nt = TRJ['E2']['natural_test']
    t, obs, fit = TRS['e2_relax_t'], TRS['e2_relax_obs'], TRS['e2_relax_fit']
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.5), gridspec_kw=dict(width_ratios=[1.6, 1]))
    panel(a, 'a')
    panel(b, 'b')
    a.plot(t, obs, '.', color='#BBBBBB', ms=1.5, label='logger every 15 min (2 cm noise)')
    a.plot(t, fit, color=BLUE, lw=1.6, label=f'fit: tau = {nt["tau_hat_d"]:.2f} days')
    a.set_xlabel('days after the earthquake')
    a.set_ylabel('head change (m)')
    a.legend(loc='upper right', fontsize=7)
    for y, (lo, hi), lab, col in ((1, nt['ci95_quake_d'], 'one earthquake', BLUE),
                                  (0, nt['ci95_season_d'], 'one year of seasons', MUTED)):
        b.plot([lo, hi], [y, y], color=col, lw=6, solid_capstyle='butt')
        b.text(hi + 0.03, y, f'{lo:.2f}-{hi:.2f}', va='center', fontsize=7, color=col)
        b.text(2.55, y + 0.3, lab, fontsize=7.5, color=col)
    b.axvline(nt['tau_true_d'], color=VERM, lw=1.0, ls='--')
    b.set_xlim(2.55, 3.65)
    b.set_ylim(-0.6, 1.7)
    b.set_yticks([])
    b.spines['left'].set_visible(False)
    b.set_xlabel('95% interval of the leakage time (days)')
    b.set_title(f'{nt["width_ratio"]:.1f} times sharper', fontsize=8)
    save(fig, 'fig16_natural_test')


# ------------------------------------------------------------------------------------------------ 17-19 liquefaction
def fig_liq_profile():
    z, q, isl = TRS['e1_z'], TRS['e1_q'], TRS['e1_liq'].astype(bool)
    lpis = TRJ['E1']['example']
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 4.0), sharey=True, gridspec_kw=dict(width_ratios=[1, 1.4]))
    panel(a, 'a')
    panel(b, 'b')
    for ax in (a, b):
        edges = np.flatnonzero(np.diff(np.r_[0, isl.astype(int), 0]))
        for k in range(0, len(edges), 2):
            ax.axhspan(z[edges[k]] - 0.05, z[edges[k + 1] - 1] + 0.05, color='#FFF3D6', lw=0, zorder=0)
    a.plot(q, z, color=ORANGE, lw=1.2)
    a.text(150, 3.0, 'sand', fontsize=7.5, color='#A66500')
    a.text(150, 5.6, 'silty clay', fontsize=7.5, color=MUTED)
    a.set_xlabel('CPT resistance $q_{c1Ncs}$')
    a.set_ylabel('depth (m)')
    a.set_xlim(0, 200)
    a.set_ylim(20, 0)
    for zw, col in (('0.8', VERM), ('1.6', ORANGE), ('2.6', BLUE)):
        fs = TRS[f'e1_fs_{zw}']
        b.plot(np.clip(fs, 0, 3), z, color=col, lw=1.4, label=f'water table {zw} m: LPI {lpis[zw]["lpi"]:.1f}')
        b.axhline(float(zw), color=col, lw=0.8, ls=':')
    b.axvline(1.0, color=INK, lw=1.0)
    b.text(0.5, 0.45, 'liquefies', ha='center', fontsize=7.5, color=VERM)
    b.text(1.7, 0.45, 'safe', ha='center', fontsize=7.5, color=BLUE)
    b.axvspan(0, 1, color=VERM, alpha=0.05, lw=0)
    b.set_xlim(0, 2.5)
    b.set_xlabel('factor of safety FS (a$_{max}$ = 0.25 g, M 6.4)')
    b.legend(loc='lower right', fontsize=7)
    save(fig, 'fig17_liq_profile')


def fig_crr_chart():
    qg = np.linspace(21, 211, 300)
    z, q, isl = TRS['e1_z'], TRS['e1_q'], TRS['e1_liq'].astype(bool)
    fig, ax = plt.subplots(figsize=(W * 0.72, 3.0))
    ax.plot(qg, liq.crr75(qg), color=INK, lw=1.8, label='CRR curve (M 7.5, 1 atm)')
    ax.fill_between(qg, liq.crr75(qg), 0.8, color=VERM, alpha=0.06, lw=0)
    for zw, col, mfc in (('0.8', VERM, VERM), ('2.6', BLUE, 'white')):
        sel = isl & (z > float(zw))
        csr, crr = TRS[f'e1_csr_{zw}'][sel], TRS[f'e1_crr_{zw}'][sel]
        qq = q[sel]
        norm = csr * liq.crr75(qq) / crr                 # CSR brought to M 7.5 and 1 atm
        ax.plot(qq, norm, 'o', ms=3.2, mfc=mfc, mec=col, mew=0.8, label=f'sand cells, water table {zw} m')
    ax.text(40, 0.55, 'liquefaction', color=VERM, fontsize=8)
    ax.text(150, 0.06, 'no liquefaction', color=BLUE, fontsize=8)
    ax.set_xlim(20, 200)
    ax.set_ylim(0, 0.8)
    ax.set_xlabel('CPT resistance $q_{c1Ncs}$')
    ax.set_ylabel('cyclic stress ratio (M 7.5, 1 atm)')
    ax.legend(loc='upper left', fontsize=6.8)
    ax.grid(color=GRID, lw=0.6)
    save(fig, 'fig18_crr_chart')


def fig_lpi():
    zw = TRS['e1_zw_grid']
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.6))
    panel(a, 'a')
    panel(b, 'b')
    for amax, col in (('0.15', GREEN), ('0.25', ORANGE), ('0.35', VERM)):
        a.plot(zw, TRS[f'e1_lpi_a{amax}'], color=col, label=f'a$_{{max}}$ = {amax} g')
    for ax in (a, b):
        ax.axhline(5, color=MUTED, ls='--', lw=1.0)
        ax.set_xlabel('depth of the water table (m)')
        ax.grid(color=GRID, lw=0.6)
    a.text(5.9, 2.8, 'LPI = 5', ha='right', fontsize=6.8, color=MUTED)
    a.set_ylabel('liquefaction potential index LPI')
    a.legend(loc='upper right', fontsize=7)
    sl = TRJ['E1']['lpi_slope_per_m']
    b.plot(zw, TRS['e1_lpi_right'], color=ORANGE, label=f'pressure of the day: {sl["right"]:.1f} per m')
    b.plot(zw, TRS['e1_lpi_wrong'], color=MUTED, ls='--', label=f'CPT re-normalised: {sl["renormalised"]:.1f} per m')
    b.legend(loc='upper right', fontsize=6.8)
    b.set_title(f'the usual shortcut understates the slope by {100 * sl["understated"]:.0f}%', fontsize=8)
    save(fig, 'fig19_lpi')


# ------------------------------------------------------------------------------------------------ 20-21 window
def fig_window():
    a_, eta, width = TRS['e4_amax'], TRS['e4_eta'], TRS['e4_width']
    fig, ax = plt.subplots(figsize=(W * 0.82, 3.2))
    lim = np.max(np.abs(width))
    m = ax.pcolormesh(a_, eta, width, cmap=LinearSegmentedColormap.from_list('w', ['#A50F15', '#FB6A4A', '#EEEEEE',
                                                                                   '#6BAED6', '#08519C']),
                      norm=TwoSlopeNorm(0, float(width.min()), float(width.max())), shading='nearest',
                      rasterized=True)
    cs = ax.contour(a_, eta, width, levels=[0], colors=[INK], linewidths=1.6)
    ax.plot(a_, TRS['e4_eta_close'], color=INK, lw=1.0, ls='--', label='closes all year (seasonal swing 0.3 m)')
    ax.text(0.105, 0.06, 'window\nopen', fontsize=8, color='white', fontweight='bold')
    ax.text(0.33, 0.95, 'window closed', fontsize=8, color='#67000D')
    ax.set_xlabel('design peak ground acceleration a$_{max}$ (g)')
    ax.set_ylabel('sea-level rise (m)')
    ax.set_ylim(0, 1.2)
    ax.legend(loc='upper right', fontsize=6.8)
    cb = fig.colorbar(m, ax=ax, fraction=0.04, pad=0.02,
                      ticks=np.r_[np.arange(np.ceil(width.min()), 0, 2), 0, np.arange(1, np.floor(width.max()) + 1)])
    cb.set_label('width of the safe window (m of water table)', fontsize=7.2)
    save(fig, 'fig20_window')


def fig_bulletin():
    d = TRS
    days = d['e4_days']
    fig, (a, b) = plt.subplots(2, 1, figsize=(W, 3.6), sharex=True, gridspec_kw=dict(height_ratios=[1, 1.3]))
    panel(a, 'a')
    panel(b, 'b')
    a.plot(days, d['e4_zw_day'], color=GREEN)
    a.invert_yaxis()
    a.set_ylabel('water table depth (m)')
    a.grid(color=GRID, lw=0.6)
    b.plot(days, d['e4_pexc'], color=VERM)
    b.fill_between(days, 0, d['e4_pexc'], color=VERM, alpha=0.12, lw=0)
    k1, k2 = int(np.argmax(d['e4_pexc'])), int(np.argmin(d['e4_pexc']))
    for k, txt in ((k1, 'highest'), (k2, 'lowest')):
        b.annotate(f'{txt}: {d["e4_pexc"][k]:.2f}', xy=(k, d['e4_pexc'][k]), xytext=(k + 25, d['e4_pexc'][k] + 0.04),
                   fontsize=7, arrowprops=dict(arrowstyle='-', lw=0.8, color=INK))
    b.set_ylabel('P(LPI > 5 | design\nearthquake today)')
    b.set_ylim(0, 0.35)
    b.set_xlabel('day of the year (from 1 January)')
    b.grid(color=GRID, lw=0.6)
    save(fig, 'fig21_bulletin')


# ------------------------------------------------------------------------------------------------ added figures
def fig_uplift():
    x = TRS['e2_x'] / 1e3
    srcs = TRJ['E2']['sources']
    fig, axs = plt.subplots(2, 2, figsize=(W, 5.6), sharex=True, sharey=True)
    for ax, src in zip(axs.flat, srcs):
        uz = 100 * TRS[f'e2_uz_{src["key"]}']
        m = ax.pcolormesh(x, x, uz, cmap=DIVERGE.reversed(), norm=TwoSlopeNorm(0, -4, 13), shading='nearest',
                          rasterized=True)
        cs = ax.contour(x, x, uz, levels=[-2, 2, 5, 10], colors=['#333333'], linewidths=0.5)
        ax.clabel(cs, fmt='%g', fontsize=6)
        corners, top = fault_outline(src)
        ax.add_patch(Polygon(corners, closed=True, fill=False, ec=INK, lw=1.0, ls='--'))
        ax.plot(top[:, 0], top[:, 1], color=INK, lw=2.0)
        ax.set_title(f'{src["label"]}: {100 * src["uz_min_m"]:.1f} to +{100 * src["uz_max_m"]:.1f} cm', fontsize=7.6)
        ax.set_aspect('equal')
        ax.set_xlim(-40, 40)
        ax.set_ylim(-40, 40)
    for ax in axs[1]:
        ax.set_xlabel('east (km)')
    for ax in axs[:, 0]:
        ax.set_ylabel('north (km)')
    fig.subplots_adjust(bottom=0.15, wspace=0.12, hspace=0.25)
    cax = fig.add_axes([0.22, 0.045, 0.6, 0.018])
    cb = fig.colorbar(m, cax=cax, extend='both', orientation='horizontal')
    cb.set_label('vertical ground motion (cm): uplift positive, subsidence negative', fontsize=7.5)
    save(fig, 'fig22_uplift')


def fig_agree():
    x = TRS['e2_x'] / 1e3
    dh, agree, big = TRS['e2_dh_mean'], TRS['e2_agree'].astype(bool), TRS['e2_big'].astype(bool)
    fig, ax = plt.subplots(figsize=(W * 0.72, 4.3))
    m = ax.pcolormesh(x, x, dh, cmap=DIVERGE, norm=TwoSlopeNorm(0, -0.8, 0.3), shading='nearest', rasterized=True)
    ax.contourf(x, x, (~agree).astype(float), levels=[0.5, 1.5], colors='none', hatches=['////'])
    ax.contour(x, x, (~agree).astype(float), levels=[0.5], colors=[MUTED], linewidths=0.6)
    ax.contour(x, x, np.abs(dh), levels=[0.1], colors=[INK], linewidths=1.4)
    for src in TRJ['E2']['sources']:
        corners, top = fault_outline(src)
        ax.plot(top[:, 0], top[:, 1], color=INK, lw=1.2, alpha=0.6)
    ax.set_aspect('equal')
    ax.set_xlim(-30, 30)
    ax.set_ylim(-30, 30)
    ax.set_xlabel('east (km)')
    ax.set_ylabel('north (km)')
    ax.plot([], [], color=INK, lw=1.4, label='mean step larger than 10 cm')
    ax.add_patch(Rectangle((0, 0), 0, 0, fill=False, hatch='////', ec=MUTED, label='the four models disagree on the sign'))
    ax.plot([], [], color=INK, lw=1.2, alpha=0.6, label='top edges of the four faults')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=1, fontsize=6.8)
    cb = fig.colorbar(m, ax=ax, fraction=0.04, pad=0.02)
    cb.set_label('mean head step of the four models (m)', fontsize=7.2)
    save(fig, 'fig23_agree')


def fig_drainage():
    from scipy.special import erf
    L = np.linspace(0, 12, 300)
    fig, ax = plt.subplots(figsize=(W * 0.72, 2.6))
    for t, col in ((5, SKY), (15, BLUE), (30, '#08306B')):
        ax.plot(L, erf(L / (2 * np.sqrt(1.0 * t))), color=col, label=f'connected sand, {t} s of shaking')
    ax.axhline(1.0, color=VERM, ls='--', lw=1.1, label='below a clay layer: the whole step stays')
    pts = TRJ['E2']['share_left_after_15s']
    ax.plot([float(k.split()[0]) for k in pts], list(pts.values()), 'o', color=BLUE, ms=4)
    ax.set_xlabel('depth below the water table (m)')
    ax.set_ylabel('share of the step left')
    ax.set_ylim(0, 1.08)
    ax.set_xlim(0, 12)
    ax.legend(loc='lower right', fontsize=6.8)
    ax.grid(color=GRID, lw=0.6)
    save(fig, 'fig24_drainage')


def fig_lpi_chart():
    z, q, isl = TRS['e1_z'], TRS['e1_q'], TRS['e1_liq'].astype(bool)
    q = np.where(isl, q, 30.0)
    zw = np.linspace(0.3, 6.0, 58)
    am = np.linspace(0.05, 0.45, 41)
    L = np.array([[liq.lpi_profile(z, 0.1, q, isl, 19.0, w, a, 6.4) for a in am] for w in zw])
    fig, ax = plt.subplots(figsize=(W * 0.8, 3.1))
    cmap = LinearSegmentedColormap.from_list('lpi', ['#FFF5EB', '#FDBE85', '#FD8D3C', '#D94701', '#7F2704'])
    m = ax.contourf(am, zw, L, levels=[0, 1, 2.5, 5, 10, 15, 20, 30, 45], cmap=cmap)
    cs = ax.contour(am, zw, L, levels=[5], colors=[INK], linewidths=1.8)
    ax.clabel(cs, fmt='LPI 5', fontsize=7)
    ax.invert_yaxis()
    ax.annotate('', xy=(0.12, 1.0), xytext=(0.12, 3.0), arrowprops=dict(arrowstyle='-|>', color=BLUE, lw=1.6))
    ax.text(0.128, 2.0, 'the water table rises:\nsea-level rise, wet season,\nless pumping', fontsize=6.8, color=BLUE,
            va='center')
    ax.set_xlabel('peak ground acceleration a$_{max}$ (g)')
    ax.set_ylabel('depth of the water table (m)')
    cb = fig.colorbar(m, ax=ax, fraction=0.04, pad=0.02)
    cb.set_label('LPI of the example profile', fontsize=7.2)
    save(fig, 'fig25_lpi_chart')


def fig_alarm_reliability():
    d = mat('alarm_reliability')
    al, mr = np.atleast_1d(d['alphas']), d['missRate']
    n = int(d['nCal'])
    exact = 1 - np.ceil((n + 1) * (1 - al)) / (n + 1)
    fig, ax = plt.subplots(figsize=(W * 0.72, 2.8))
    pos = np.arange(al.size)
    bp = ax.boxplot([mr[:, j] for j in range(al.size)], positions=pos, widths=0.42, patch_artist=True,
                    showfliers=False, whis=(2.5, 97.5), medianprops=dict(color=MUTED, lw=1.0))
    for patch in bp['boxes']:
        patch.set(facecolor='#E8EEF6', edgecolor='#9DB8DC')
    for item in bp['whiskers'] + bp['caps']:
        item.set(color='#9DB8DC')
    ax.plot(pos, mr.mean(0), 'o', color=BLUE, ms=6, label='mean observed miss rate')
    ax.plot(pos, al, '_', color=VERM, ms=22, mew=2, label='stated miss rate')
    for j in range(al.size):
        ax.text(pos[j] + 0.27, mr[:, j].mean(), f'{mr[:, j].mean():.3f}', fontsize=6.8, color=BLUE, va='center')
    ax.set_xticks(pos)
    ax.set_xticklabels([f'{a:.2f}' for a in al])
    ax.set_xlabel('stated miss rate $\\alpha$')
    ax.set_ylabel('observed miss rate')
    ax.legend(loc='upper left', fontsize=6.8)
    ax.grid(axis='y', color=GRID, lw=0.6)
    save(fig, 'fig26_alarm_reliability')


def fig_equifinality():
    d = mat('equifinality')
    t = np.arange(d['h1'].size)
    fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.5), gridspec_kw=dict(wspace=0.3))
    panel(a, 'a')
    panel(b, 'b')
    a.plot(t, d['h1'], color=GREEN, lw=2.2, label='soil parameters as estimated')
    a.plot(t, d['h2'], color=ORANGE, lw=1.0, ls='--', label='five parameters x 1.5')
    a.set_xlabel('day')
    a.set_ylabel('head (m)')
    a.legend(loc='upper left', fontsize=6.6)
    a.set_title('identical heads', fontsize=8)
    b.plot(t, d['cum1'], color=GREEN, lw=1.8, label=f'{float(d["cum1"][-1]):.0f} mm in three years')
    b.plot(t, d['cum2'], color=ORANGE, lw=1.8, label=f'{float(d["cum2"][-1]):.0f} mm in three years')
    b.set_xlabel('day')
    b.set_ylabel('cumulative recharge (mm)')
    b.legend(loc='upper left', fontsize=6.6)
    b.set_title('50% more recharge', fontsize=8)
    save(fig, 'fig27_equifinality')


if __name__ == '__main__':
    for f in (fig_system, fig_lens, fig_henry, fig_inflow, fig_upconing, fig_fushe_kuqe, fig_sensor_map, fig_returns,
              fig_between_path, fig_between_bands, fig_recharge, fig_boundary, fig_alarm, fig_quake_maps,
              fig_quake_transect, fig_natural_test, fig_liq_profile, fig_crr_chart, fig_lpi, fig_window, fig_bulletin,
              fig_uplift, fig_agree, fig_drainage, fig_lpi_chart, fig_alarm_reliability, fig_equifinality):
        f()
