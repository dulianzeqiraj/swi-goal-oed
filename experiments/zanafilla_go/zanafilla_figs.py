"""Figures of the review "Where does the chloride come from?" (English labels; every text at least 8.6 pt at the printed
size, 17 cm wide).  usage: python zanafilla_figs.py OUT_DIR

fig_map        the thirty papers against the five routes
fig_scheme     the ZANAFILLA-GO loop
fig_aquifer    the synthetic aquifer: wedge, relict pocket, halite body, town, wells and screens
fig_intervals  identified intervals of the modern-seawater share at the samples of one field, three levels of information
fig_value      decidability and width for every tracer set and level of end-member knowledge
fig_nn         the amortised network against the certificate, in the training world and a shifted world
fig_point      the point inverse against the identified set
Numbers come from res/zanafilla.json and res/zanafilla_examples.npz."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', 'rindertimi_go'))
import gar_figs as GF  # noqa: E402
from rgo_figs import Canvas, INK, MUTED  # noqa: E402
import zanafilla_core as Z  # noqa: E402

RES = os.path.join(HERE, 'res')
MM, FS = GF.MM, GF.FS
BLUE, ORANGE, AQUA, VIOLET, YELLOW, REF = GF.BLUE, GF.ORANGE, GF.AQUA, GF.VIOLET, '#eda100', GF.REF
# fixed order of the institutions; this seven-colour palette passes the validator (light surface, adjacent pairs)
INST = {'Oxford': '#2a78d6', 'Caltech': '#eb6834', 'MIT': '#1baf7a', 'Princeton': '#c43e8f', 'Max Planck': '#eda100',
        'Harvard': '#6250d6', 'Berkeley': '#19a3c4'}
ROUTES = [('tracers', 'tracers'), ('mixing', 'unmixing'), ('inverse', 'ill-posed inversion'),
          ('ident', 'identification, design'), ('learn', 'learning')]


def style(ax, grid='y'):
    GF.style(ax, grid)


def load():
    with open(os.path.join(RES, 'zanafilla.json')) as fh:
        return json.load(fh)


# ------------------------------------------------------------------------------------------------- the map of papers
def fig_map(out, cards):
    n = len(cards)
    fig = plt.figure(figsize=(170 * MM, 170 * MM))
    left, bottom, top = 0.60, 0.015, 0.86
    ax = fig.add_axes([left, bottom, 0.985 - left, top - bottom])
    prev = None
    for i, cd in enumerate(cards):
        y = n - 1 - i
        col = INST[cd['inst']]
        if prev is not None and cd['inst'] != prev:
            ax.axhline(y + 0.5, color='#c9ced6', lw=0.6)
        prev = cd['inst']
        for j, (key, _) in enumerate(ROUTES):
            if key in cd['routes']:
                ax.plot(j, y, 'o', color=col, ms=7.0, zorder=3)
            else:
                ax.plot(j, y, 'o', color='#e1e4e8', ms=2.4, zorder=2)
        ax.text(-0.72, y, f"{cd['id']}  {cd['short']}", ha='right', va='center', color=INK, clip_on=False)
    ax.set_xlim(-0.6, len(ROUTES) - 0.4); ax.set_ylim(-0.6, n - 0.4)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    for j, (key, lab) in enumerate(ROUTES):
        ax.text(j - 0.12, n - 0.25, lab, ha='left', va='bottom', rotation=42, rotation_mode='anchor', color=INK, clip_on=False)
    x0, y0 = 0.015, 0.978
    for k, (inst, col) in enumerate(INST.items()):
        if k == 4:
            x0, y0 = 0.015, 0.95
        fig.text(x0, y0, '●', color=col, fontsize=FS + 1.5, va='center')
        fig.text(x0 + 0.02, y0, inst, color=INK, va='center')
        x0 += 0.025 + 0.0125 * len(inst)
    fig.text(0.015, 0.922, '● the paper serves this route', color=MUTED, va='center')
    fig.savefig(os.path.join(out, 'fig_map.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------- the loop
def fig_scheme(out):
    cv = Canvas(170, 86)
    t = cv.text
    B1, B2, B3 = '#e3eefb', '#fde9df', '#e2f5ee'

    def box(x, y, w, h, fc, ec, head, lines):
        cv.box(x, y, w, h, fc, ec, lw=1.0, r=1.8)
        t(x + 2.2, y + h - 4.2, head, ha='left', weight='bold', color=INK)
        for k, ln in enumerate(lines):
            t(x + 2.2, y + h - 9.0 - 4.1 * k, ln, ha='left', color=MUTED)

    box(4, 54, 50, 27, B1, BLUE, 'What is known', ['tracers at the wells;', 'end-member intervals;', 'site limits (land use, geology)'])
    box(60, 54, 50, 27, 'white', BLUE, 'The polytope', ['all fractions and signatures', 'that reproduce the data', '(Proposition 1)'])
    box(116, 54, 50, 27, B2, ORANGE, 'Sharp bounds', ['of the chloride share of each', 'source by linear-fractional', 'programming (Prop. 2)'])
    box(116, 6, 50, 27, B3, AQUA, 'Decision', ['decidable: act;', 'undecidable: say so;', 'empty set: a source is missing'])
    box(60, 6, 50, 27, 'white', AQUA, 'Design', ['which tracer, which well,', 'which end-member to sample', 'to make the decision decidable'])
    box(4, 6, 50, 27, 'white', VIOLET, 'Learned screening', ['amortised network, fast;', 'calibrated, and checked', 'against the bounds'])
    cv.arrow(54, 67.5, 60, 67.5, BLUE); cv.arrow(110, 67.5, 116, 67.5, BLUE)
    cv.arrow(141, 54, 141, 33, ORANGE)
    cv.arrow(116, 19.5, 110, 19.5, AQUA)
    cv.arrow(85, 33, 85, 54, AQUA)
    cv.arrow(54, 19.5, 60, 19.5, VIOLET)
    t(87.5, 43.5, 'next samples', ha='left', color='#0f7a55')
    t(144, 43.5, 'interval', ha='left', color='#b8451a')
    cv.fig.savefig(os.path.join(out, 'fig_scheme.png'), dpi=300)
    plt.close(cv.fig)


# ------------------------------------------------------------------------------------------------- the aquifer
def fig_aquifer(out):
    ex = np.load(os.path.join(RES, 'zanafilla_examples.npz'))
    fig, ax = plt.subplots(figsize=(170 * MM, 80 * MM), gridspec_kw=dict(left=0.075, right=0.86, top=0.97, bottom=0.22))
    x = np.linspace(0.0, 10.5, 400)
    a, w = 60.0, 15.0
    zeta = a * np.sqrt(x)
    ax.fill_between(x, zeta, 160, color='#cfe2f7', lw=0)
    ax.plot(x, zeta, color=BLUE, lw=1.4)
    ax.fill_between(x, zeta - 2 * w, zeta + 2 * w, color='#a9c9ef', lw=0, alpha=0.55)
    ax.text(0.35, 150, 'modern seawater wedge', color='#1c5cab', ha='left', va='center')
    ax.add_patch(plt.Circle((4.6, 120), 0.0, color='w'))
    th = np.linspace(0, 2 * np.pi, 100)
    ax.fill(4.6 + 1.6 * np.cos(th), 118 + 16 * np.sin(th), color='#f4d9c6', lw=0)
    ax.text(4.6, 118, 'relict pocket', color='#b8451a', ha='center', va='center')
    ax.fill(7.6 + 0.7 * np.cos(th), 145 + 9 * np.sin(th), color='#e8e0f6', lw=0)
    ax.text(7.6, 145, 'halite?', color='#4b3bb0', ha='center', va='center')
    ax.fill_between([1.5, 5.0], 0, 12, color='#f2f2f2', lw=0)
    ax.text(3.25, 6, 'town: wastewater, fertiliser', color=MUTED, ha='center', va='center')
    for xi in Z.WELL_X:
        ax.plot([xi, xi], [0, 115], color='#9aa3ad', lw=0.8, zorder=2)
    sh = ex['share']; cl = ex['cl']
    for k in range(Z.NS):
        if cl[k] > 150:
            col = plt.cm.RdYlBu_r(sh[k])
            ax.plot(Z.X[k], Z.Z[k], 's', ms=7.5, color=col, mec=INK, mew=0.5, zorder=4)
        else:
            ax.plot(Z.X[k], Z.Z[k], 's', ms=6.5, color='white', mec='#9aa3ad', mew=0.8, zorder=4)
    ax.set_xlim(0, 10.5); ax.set_ylim(160, 0)
    ax.set_xlabel('distance from the coast, km'); ax.set_ylabel('depth below sea level, m')
    style(ax, grid=None)
    sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlBu_r, norm=plt.Normalize(0, 1))
    cax = fig.add_axes([0.885, 0.3, 0.02, 0.6])
    cb = fig.colorbar(sm, cax=cax, orientation='vertical'); cb.set_ticks([0, 0.5, 1]); cb.outline.set_visible(False)
    cb.set_label('modern-seawater share of the chloride', color=INK)
    fig.text(0.075, 0.025, 'Squares: screens of one synthetic field (open: fresh, Cl < 150 mg/L). Shapes are schematic.',
             ha='left', va='bottom', color=MUTED)
    fig.savefig(os.path.join(out, 'fig_aquifer.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------- intervals of one field
def fig_intervals(out, R):
    ex = R['examples']
    keys = [('none|Cl + major ions', '(a) today: chloride and major ions'),
            ('none|+ B (all)', '(b) seven tracers at the wells'),
            ('relict + fresh|+ B (all)', '(c) seven tracers, relict and fresh water sampled')]
    fig, axs = plt.subplots(3, 1, figsize=(170 * MM, 150 * MM), sharex=True,
                            gridspec_kw=dict(left=0.09, right=0.985, top=0.965, bottom=0.12, hspace=0.32))
    for ax, (k, title) in zip(axs, keys):
        e = ex[k]
        idx = np.array(e['i']); order = np.argsort(Z.X[idx] + 0.01 * Z.Z[idx])
        for p, j in enumerate(order):
            lo, hi, s = e['lo'][j], e['hi'][j], e['s'][j]
            dec = lo is not None and (lo > 0.5 or hi < 0.5)
            col = '#0f7a55' if dec else '#9aa3ad'
            ax.plot([p, p], [lo, hi], color=col, lw=4.2, solid_capstyle='butt', zorder=2)
            ax.plot(p, s, 'o', color=INK, ms=4.2, zorder=3)
        ax.axhline(0.5, color=ORANGE, lw=0.9, ls=(0, (4, 3)))
        ax.set_ylim(-0.04, 1.04); ax.set_yticks([0, 0.5, 1]); style(ax)
        ndec = sum(1 for j in range(len(idx)) if (e['lo'][j] > 0.5 or e['hi'][j] < 0.5))
        ax.set_title(f'{title}: {ndec} of {len(idx)} samples decidable', loc='left')
    lab = [f"{Z.X[i]:g}{'u' if Z.UP[i] else 'l'}" for i in np.array(ex[keys[0][0]]['i'])[np.argsort(Z.X[np.array(ex[keys[0][0]]['i'])] + 0.01 * Z.Z[np.array(ex[keys[0][0]]['i'])])]]
    axs[-1].set_xticks(range(len(lab))); axs[-1].set_xticklabels(lab, rotation=90)
    axs[-1].set_xlabel('sample: distance from the coast (km), upper (u) or lower (l) screen')
    axs[1].set_ylabel('share of the chloride from modern seawater')
    fig.text(0.99, 0.005, 'bar: identified interval (green when it excludes 0.5); dot: truth; dashed: decision threshold',
             ha='right', va='bottom', color=MUTED)
    fig.savefig(os.path.join(out, 'fig_intervals.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------- the value of each action
def fig_value(out, R):
    levels = list(R['settings']['em_levels']); sets = list(R['settings']['tracer_sets'])
    D = np.zeros((len(levels), len(sets))); Wd = np.zeros_like(D)
    for s in R['E1']:
        D[levels.index(s['level']), sets.index(s['tracers'])] = 100 * s['decidable']
        Wd[levels.index(s['level']), sets.index(s['tracers'])] = s['width_mean']
    fig, ax = plt.subplots(figsize=(170 * MM, 74 * MM), gridspec_kw=dict(left=0.315, right=0.99, top=0.86, bottom=0.2))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list('g', ['#f3faf6', '#bfe6d2', '#62c39a', '#1baf7a', '#0b6e4c'])
    ax.imshow(D, cmap=cmap, vmin=0, vmax=50, aspect='auto')
    for a in range(len(levels)):
        for b in range(len(sets)):
            ax.text(b, a - 0.12, f'{D[a, b]:.0f}%', ha='center', va='center', color='white' if D[a, b] > 30 else INK, weight='bold')
            ax.text(b, a + 0.25, f'w {Wd[a, b]:.2f}', ha='center', va='center', color='white' if D[a, b] > 30 else MUTED)
    ax.set_xticks(range(len(sets))); ax.set_xticklabels(sets, rotation=0)
    ax.set_yticks(range(len(levels))); ax.set_yticklabels(['no end-member sampled', 'relict water sampled',
                                                           'relict + fresh sampled', 'relict + fresh + anthrop.'])
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    fig.text(0.01, 0.955, 'Decidable salinised samples: the identified interval excludes 0.5 (w: mean width of the interval)',
             ha='left', va='center', color=INK)
    ax.set_xlabel('tracers measured at the wells (cumulative from left to right)')
    fig.savefig(os.path.join(out, 'fig_value.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------- network against certificate
def fig_nn(out, R):
    E = R['E3']
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 76 * MM), gridspec_kw=dict(left=0.075, right=0.99, top=0.78, bottom=0.2, wspace=0.28))
    for ax, (name, title) in zip(axs, (('Cl + major ions', "(a) today's tracers"), ('+ B (all)', '(b) seven tracers'))):
        w = E[name]['worlds']
        xs = np.arange(2)
        nn = [100 * w[k]['nn_coverage'] for k in ('training world', 'shifted world')]
        ce = [100 * w[k]['cert_coverage'] for k in ('training world', 'shifted world')]
        ax.bar(xs - 0.2, nn, width=0.36, color=VIOLET, label='network, conformal')
        ax.bar(xs + 0.2, ce, width=0.36, color=AQUA, label='identified interval')
        for xx, v, wd in zip(xs - 0.2, nn, [w[k]['nn_width'] for k in ('training world', 'shifted world')]):
            ax.text(xx, v + 2, f'{v:.0f}%\nw {wd:.2f}', ha='center', va='bottom', color=INK)
        for xx, v, wd in zip(xs + 0.2, ce, [w[k]['cert_width'] for k in ('training world', 'shifted world')]):
            ax.text(xx, v + 2, f'{v:.0f}%\nw {wd:.2f}', ha='center', va='bottom', color=INK)
        ax.axhline(90, color=INK, lw=0.8, ls=(0, (4, 3)))
        ax.set_xticks(xs); ax.set_xticklabels(['world it was\ntrained for', 'shifted world'])
        ax.set_ylim(0, 128); ax.set_yticks([0, 30, 60, 90]); style(ax)
        ax.set_title(title, loc='left')
    axs[0].set_ylabel('coverage of the true share, %')
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc='upper center', frameon=False, ncol=2, bbox_to_anchor=(0.53, 1.0))
    fig.text(0.99, 0.01, 'w: mean width of the interval; dashed: nominal 90%', ha='right', va='bottom', color=MUTED)
    fig.savefig(os.path.join(out, 'fig_nn.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------- point inverse against set
def fig_point(out, R):
    ex = R['E5']['examples'][:40]
    ex = sorted(ex, key=lambda r: r['s'])
    fig, ax = plt.subplots(figsize=(170 * MM, 76 * MM), gridspec_kw=dict(left=0.075, right=0.99, top=0.8, bottom=0.12))
    for p, r in enumerate(ex):
        ax.plot([p, p], [r['lo'], r['hi']], color='#d5dae0', lw=5.5, solid_capstyle='butt', zorder=1)
        ax.plot([p, p], [r['pmin'], r['pmax']], color=ORANGE, lw=1.6, zorder=2)
        ax.plot(p, r['p0'], 'D', color=ORANGE, ms=3.6, zorder=3)
        ax.plot(p, r['s'], 'o', color=INK, ms=3.8, zorder=4)
    ax.set_ylim(-0.04, 1.04); ax.set_xlim(-0.8, len(ex) - 0.2)
    ax.set_xticks([]); style(ax)
    ax.set_xlabel('salinised samples, ordered by the true share'); ax.set_ylabel('modern-seawater share')
    from matplotlib.lines import Line2D
    hs = [Line2D([], [], color='#d5dae0', lw=5.5, label='identified interval'),
          Line2D([], [], color=ORANGE, lw=1.6, label='least squares, over plausible signatures'),
          Line2D([], [], color=ORANGE, marker='D', ls='', ms=4.5, label='least squares, central signatures'),
          Line2D([], [], color=INK, marker='o', ls='', ms=4.5, label='truth')]
    fig.legend(handles=hs, loc='upper center', ncol=2, frameon=False, bbox_to_anchor=(0.53, 1.0), labelcolor=INK)
    fig.savefig(os.path.join(out, 'fig_point.png'), dpi=300)
    plt.close(fig)


def main(out, cards=None):
    os.makedirs(out, exist_ok=True)
    R = load()
    if cards is not None:
        fig_map(out, cards)
    fig_scheme(out); fig_aquifer(out); fig_intervals(out, R); fig_value(out, R); fig_nn(out, R); fig_point(out, R)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'figs')
