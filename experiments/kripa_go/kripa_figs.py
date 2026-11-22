"""Figures of the KRIPA-GO review (English labels; every text at least 8.6 pt at the printed size, 17 cm wide).
usage: python kripa_figs.py OUT_DIR

fig_scheme   the twin interface in a section (state abduction, dispersion) and the posterior probability that the
             shallow chloride exceeds 250 mg/L, factual and under a 40% lower recharge (Fushe-Kuqe, real facts)
fig_dose     dose-response: the effect of a recharge factor c on three goals, interventional and counterfactual (T26)
fig_cover    coverage of importance-sampling and conformal bands (T27) and what each group of facts buys (T28)
fig_disp     what the counterfactual depends on: variance shares and the cross-world law of the dispersion (T28)
fig_map      the twenty papers of this review against the steps and the unknowns they inform
Numbers come from res/kripa.json and res/kripa_maps.npz."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import FixedLocator, NullLocator, FuncFormatter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', 'rindertimi_go'))
import gar_figs as GF  # noqa: E402
from rgo_figs import INK, MUTED  # noqa: E402

RES = os.path.join(HERE, 'res')
MM = GF.MM
BLUE, ORANGE, AQUA, VIOLET, REF = GF.BLUE, GF.ORANGE, GF.AQUA, GF.VIOLET, GF.REF
GL = dict(A='salinized area\n(km²)', T='toe area\n(km²)', F='seawater fraction\n(points)')
GS = dict(A='area', T='toe', F='frac.')
GN = dict(A='salinized area', T='toe area', F='seawater fraction')
GT = dict(A='salinized\narea', T='toe\narea', F='seawater\nfraction')


def load():
    with open(os.path.join(RES, 'kripa.json')) as fh:
        return json.load(fh)


def fig_scheme(out, D):
    z = np.load(os.path.join(RES, 'kripa_maps.npz'))
    fig = plt.figure(figsize=(170 * MM, 104 * MM))
    # left: a section through the wedge
    ax = fig.add_axes([0.085, 0.24, 0.39, 0.64])
    x = np.linspace(0, 6, 400)                                        # km from the shore
    L, w, c = 6.0, 20.0, 0.6
    zeta = 180.0 * np.sqrt(x * (2 * L - x)) / L                       # schematic Strack wedge, zeta ~ sqrt(phi)
    zc = np.sqrt(c) * zeta
    ax.axhspan(0, 40, color=REF, alpha=0.22, lw=0)
    for zz, col, lab in ((zeta, BLUE, 'factual interface ζ'), (zc, ORANGE, 'twin interface ζ′ = √c ζ')):
        ax.fill_between(x, np.maximum(zz - 1.28 * w, 0), zz + 1.28 * w, color=col, alpha=0.20, lw=0)
        ax.plot(x, zz, color=col, lw=1.6, label=lab)
    ax.text(5.9, 20, 'shallow screens', ha='right', va='center', color=INK)
    ax.text(5.95, 232, 'shading: 10–90% seawater;\nwidth set by the dispersion w', color=MUTED, ha='right',
            va='center')
    ax.set_ylim(260, 0); ax.set_xlim(0, 6)
    ax.set_xlabel('distance from the shore (km)'); ax.set_ylabel('depth below sea level (m)')
    ax.legend(loc='lower left', bbox_to_anchor=(0.0, 1.0), frameon=False, handlelength=1.6, ncol=1)
    GF.style(ax, grid=None)
    # right: two maps on the model grid
    v = z['valid']; dx = float(z['dx'])
    i = np.round(z['cx'] / dx).astype(int); j = np.round((z['cy'] - 24.0) / dx).astype(int)
    nx, ny = i[v].max() + 1, j[v].max() + 1
    cmap = plt.get_cmap('Blues').copy(); cmap.set_bad('white')
    for k, (key, ttl) in enumerate((('p_fact', 'factual'), ('p_cf', '40% less recharge'))):
        axm = fig.add_axes([0.54 + k * 0.225, 0.24, 0.205, 0.64])
        img = np.full((ny, nx), np.nan)
        img[j[v], i[v]] = z[key][v]
        axm.imshow(img, origin='lower', cmap=cmap, vmin=0, vmax=1, extent=(-dx / 2, (nx - 0.5) * dx, 24 - dx / 2,
                                                                            24 + (ny - 0.5) * dx), interpolation='nearest')
        axm.set_title(ttl); axm.set_xlabel('x (km)')
        if k == 0:
            axm.set_ylabel('y (km)')
        else:
            axm.set_yticklabels([])
        GF.style(axm, grid=None)
    cax = fig.add_axes([0.56, 0.115, 0.39, 0.022])
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 1))
    cb = fig.colorbar(sm, cax=cax, orientation='horizontal')
    cb.set_label('probability that shallow chloride > 250 mg/L', labelpad=1)
    cb.outline.set_visible(False)
    fig.savefig(os.path.join(out, 'fig_scheme.png'), dpi=300)
    plt.close(fig)


def fig_dose(out, D):
    T = D['T26']['dose']
    cs = sorted([float(c) for c in T['A'].keys()] + [1.0])
    fig, axs = plt.subplots(1, 3, figsize=(170 * MM, 66 * MM))
    for ax, g in zip(axs, ('A', 'T', 'F')):
        for kind, col, lab in (('prior', ORANGE, 'interventional (no facts)'), ('post', BLUE, 'counterfactual (facts)')):
            med, lo, hi = [], [], []
            for c in cs:
                if c == 1.0:
                    med.append(0.0); lo.append(0.0); hi.append(0.0); continue
                e = T[g][f'{c:g}' if f'{c:g}' in T[g] else str(c)][kind]
                med.append(e['med']); lo.append(e['lo']); hi.append(e['hi'])
            ax.fill_between(cs, lo, hi, color=col, alpha=0.18 if kind == 'prior' else 0.30, lw=0)
            ax.plot(cs, med, '-o', color=col, ms=3.5, lw=1.4, label=lab)
        ax.axhline(0, color=INK, lw=0.8)
        ax.axvline(0.6, color=MUTED, lw=0.8, ls=':')
        ax.set_xlabel('recharge factor c'); ax.set_title(GL[g].replace('\n', ' '))
        GF.style(ax, grid='y')
    axs[0].set_ylabel('effect (twin minus factual)')
    fig.legend(*axs[0].get_legend_handles_labels(), loc='upper center', ncol=2, frameon=False,
               bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.88), w_pad=1.2)
    fig.savefig(os.path.join(out, 'fig_dose.png'), dpi=300)
    plt.close(fig)


def fig_cover(out, D):
    T27, T28 = D['T27'], D['T28']
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 70 * MM), gridspec_kw=dict(width_ratios=(1.3, 1)))
    labs, cis, ccp = [], [], []
    for g in ('A', 'T', 'F'):
        for kind, kl in (('s', 'effect'), ('cf', 'level')):
            labs.append(f'{GS[g]}\n{kl}')
            cis.append(T27[g][kind]['cover_is']); ccp.append(T27[g][kind]['cover_conformal'])
    x = np.arange(len(labs))
    axs[0].bar(x - 0.19, cis, 0.36, color=REF, label='importance sampling, 90%')
    axs[0].bar(x + 0.19, ccp, 0.36, color=BLUE, label='conformal, 90%')
    axs[0].axhline(0.9, color=INK, lw=1.0, ls='--')
    axs[0].set_ylim(0.8, 0.96); axs[0].set_xticks(x); axs[0].set_xticklabels(labs)
    axs[0].set_ylabel('coverage on 300 test data sets'); axs[0].set_title('T27: coverage')
    axs[0].legend(loc='upper left', frameon=False, ncol=1)
    groups = (('none', 'no facts'), ('heads', 'head'), ('chloride', 'chloride'), ('all', 'all'))
    cols = dict(A=BLUE, T=AQUA, F=VIOLET)
    for i, g in enumerate(('A', 'T', 'F')):
        base = T28['subsets']['none'][g]['hi'] - T28['subsets']['none'][g]['lo']
        v = [(T28['subsets'][s][g]['hi'] - T28['subsets'][s][g]['lo']) / base for s, _ in groups]
        axs[1].plot(range(4), v, '-o', color=cols[g], ms=4.5, lw=1.4, label=GN[g])
    axs[1].set_xticks(range(4)); axs[1].set_xticklabels([l_ for _, l_ in groups])
    axs[1].set_ylim(0, 1.15); axs[1].set_ylabel('90% width of the effect ÷ no facts')
    axs[1].set_xlabel('facts used'); axs[1].set_title('T28: what the facts buy')
    axs[1].legend(loc='lower left', frameon=False)
    for ax in axs:
        GF.style(ax, grid='y')
    fig.tight_layout(w_pad=1.6)
    fig.savefig(os.path.join(out, 'fig_cover.png'), dpi=300)
    plt.close(fig)


def fig_disp(out, D):
    T28 = D['T28']
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 72 * MM))
    keys = (('w', 'dispersion w', VIOLET), ('R', 'recharge R', AQUA), ('L_B', 'thinning length', ORANGE),
            ('other', 'other unknowns', REF))
    x = np.arange(3)
    bottom = np.zeros(3)
    for k, lab, col in keys:
        if k == 'other':
            v = np.array([max(0.0, 1 - sum(T28['share'][g][q]['post'] for q in ('w', 'R', 'L_B'))) for g in 'ATF'])
        else:
            v = np.array([T28['share'][g][k]['post'] for g in 'ATF'])
        axs[0].bar(x, v, 0.6, bottom=bottom, color=col, label=lab)
        bottom += v
    axs[0].set_xticks(x); axs[0].set_xticklabels([GT[g] for g in 'ATF'])
    axs[0].set_ylim(0, 1.0); axs[0].set_ylabel('share of the posterior variance')
    axs[0].set_title('first-order shares of the effect')
    axs[0].legend(loc='upper center', bbox_to_anchor=(0.5, -0.32), ncol=2, frameon=False)
    # right: the effect on the salinized area under the cross-world law of w and for low / high w
    rows = [('w low tenth', T28['w_cond']['A']['low'], VIOLET), ('w high tenth', T28['w_cond']['A']['high'], VIOLET),
            ("$w'=w$ (shared)", T28['beta']['A']['0'], BLUE), ("$w'=w\\,c^{-1/4}$", T28['beta']['A']['0.25'], ORANGE),
            ("$w'=w\\,c^{-1/2}$", T28['beta']['A']['0.5'], ORANGE)]
    for i, (lab, e, col) in enumerate(rows):
        axs[1].plot([e['lo'], e['hi']], [i, i], color=col, lw=3.0, solid_capstyle='butt')
        axs[1].plot(e['med'], i, 'o', color=INK, ms=4)
    axs[1].set_yticks(range(len(rows))); axs[1].set_yticklabels([r[0] for r in rows])
    axs[1].invert_yaxis()
    axs[1].set_xlabel('effect on the salinized area (km²)')
    axs[1].set_title('dispersion and the drought effect')
    for ax in axs:
        GF.style(ax, grid='x' if ax is axs[1] else 'y')
    fig.tight_layout(w_pad=1.6)
    fig.savefig(os.path.join(out, 'fig_disp.png'), dpi=300)
    plt.close(fig)


def main(out, cards=None):
    os.makedirs(out, exist_ok=True)
    D = load()
    fig_scheme(out, D)
    fig_dose(out, D)
    fig_cover(out, D)
    fig_disp(out, D)
    if cards is not None:
        GF.fig_map(out, cards)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, 'figs'))
