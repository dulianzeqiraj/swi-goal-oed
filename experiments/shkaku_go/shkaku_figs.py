"""Figures of the SHKAKU-GO review (English labels; every text at least 8.6 pt at the printed size, 17 cm wide).
usage: python shkaku_figs.py OUT_DIR

fig_scheme    the twin network of the aquifer and one field case: factual and counterfactual head at the well, the
              counterfactual band (four loggers) and the interventional band (rain only)
fig_cf        half-width of every counterfactual band divided by the floor, three real laws (T21)
fig_design    value of abduction: the floor of six designs relative to rain only (T22)
fig_coupling  the coupling of the recharge error across worlds: floors and risks (T23)
fig_map       the twenty papers of this review against the steps and the unknowns they inform
Numbers come from res/shkaku.json (the scheme recomputes one case with the same code)."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
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
GOALS = ('dr', 'dh', 'rc', 'hc')
TICKS = ['effect\nΔr', 'effect\nΔh', 'level\nr′', 'level\nh′']
GL = dict(dr='recharge effect Δr', dh='head effect Δh', rc='counterfactual recharge r′', hc='counterfactual head h′')
METHODS = (('star', 'exact under P, λ set on the field', VIOLET, 'D'), ('sims', 'exact under P, 300 twins', REF, 'o'),
           ('anc20', 'exact under P, 20 anchor twins', BLUE, 's'), ('T_sims', 'enlarged law, 300 twins', ORANGE, 'v'))


def load():
    with open(os.path.join(RES, 'shkaku.json')) as fh:
        return json.load(fh)


def node(ax, x, y, text, fc='white', ec=INK, w=1.25, h=0.62, ls='-'):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.02,rounding_size=0.12', fc=fc,
                                ec=ec, lw=1.1, ls=ls, zorder=3))
    ax.text(x, y, text, ha='center', va='center', color=INK, zorder=4)


def arrow(ax, a, b, color=INK, ls='-', rad=0.0, both=False):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='<|-|>' if both else '-|>', mutation_scale=9, color=color, lw=1.0,
                                 ls=ls, shrinkA=14, shrinkB=14, connectionstyle=f'arc3,rad={rad}', zorder=2))


def fig_scheme(out, D):
    import shkaku_exp as S
    fig = plt.figure(figsize=(170 * MM, 78 * MM))
    ax = fig.add_axes([0.005, 0.02, 0.50, 0.96])
    ax.set_xlim(0, 10); ax.set_ylim(0, 6.6); ax.axis('off')
    OBS, CF, SH = '#e3eefb', '#fdebe3', '#efecfb'
    yF, yS, yT = 5.5, 3.3, 1.1
    node(ax, 0.8, yF, 'rain $P$', fc=OBS, ec=BLUE)
    node(ax, 2.7, yF, '$f_\\tau$')
    node(ax, 4.6, yF, '$r$')
    node(ax, 6.7, yF, '$h$')
    node(ax, 8.9, yF, 'data $y$', fc=OBS, ec=BLUE)
    node(ax, 0.8, yT, '$P\'=T(P)$', fc=CF, ec=ORANGE, w=1.5)
    node(ax, 2.7, yT, '$f\'_\\tau$', fc=CF, ec=ORANGE)
    node(ax, 4.6, yT, '$r\'$', fc=CF, ec=ORANGE)
    node(ax, 6.7, yT, '$h\'$', fc=CF, ec=ORANGE)
    node(ax, 1.75, yS, '$\\tau$', fc=SH, ec=VIOLET, w=0.9)
    node(ax, 3.65, yS, '$\\kappa$', fc=SH, ec=VIOLET, w=0.9)
    node(ax, 5.5, 4.3, '$e$', fc=SH, ec=VIOLET, w=0.8, h=0.55)
    node(ax, 5.5, 2.3, '$e\'$', fc=SH, ec=VIOLET, w=0.8, h=0.55, ls='--')
    node(ax, 8.15, yS, '$\\eta,\\ q_L,\\ h_0$', fc=SH, ec=VIOLET, w=1.75)
    for a, b in (((0.8, yF), (2.7, yF)), ((2.7, yF), (4.6, yF)), ((4.6, yF), (6.7, yF)), ((6.7, yF), (8.9, yF)),
                 ((0.8, yT), (2.7, yT)), ((2.7, yT), (4.6, yT)), ((4.6, yT), (6.7, yT))):
        arrow(ax, a, b)
    arrow(ax, (0.8, yF), (0.8, yT), color=ORANGE, ls='--')
    ax.text(0.62, 3.3, 'do', color=ORANGE, ha='right', va='center')
    for a, b in (((1.75, yS), (2.7, yF)), ((1.75, yS), (2.7, yT)), ((3.65, yS), (4.6, yF)), ((3.65, yS), (4.6, yT)),
                 ((5.5, 4.3), (4.6, yF)), ((5.5, 2.3), (4.6, yT)), ((8.15, yS), (6.7, yF)), ((8.15, yS), (6.7, yT))):
        arrow(ax, a, b, color=VIOLET)
    arrow(ax, (5.5, 4.3), (5.5, 2.3), color=VIOLET, ls=':', both=True)
    ax.text(5.72, 3.3, '$\\rho$', color=VIOLET, ha='left', va='center')
    ax.text(0.15, 6.35, 'factual world', color=BLUE, ha='left', va='center')
    ax.text(0.15, 0.25, 'twin world', color=ORANGE, ha='left', va='center')
    ax.text(9.9, 2.05, 'shared\nhistories', color=VIOLET, ha='right', va='center')
    # right panel: one field case
    bed = S.Bed()
    rng = np.random.default_rng(31)
    cs = bed.case(rng, 'none')
    tw = bed.twin(cs, 'drought', 1.0)
    rows4, rows0 = bed.rows(S.DESIGN4), bed.rows(())
    y4, y0 = bed.data(cs, rows4), bed.data(cs, rows0)
    m4, s4 = S.mix_moments(S.real_mix(bed, cs, rows4, y4, 'none', 'drought', 1.0)['hc'])
    m0, s0 = S.mix_moments(S.real_mix(bed, cs, rows0, y0, 'none', 'drought', 1.0)['hc'])
    ax2 = fig.add_axes([0.60, 0.15, 0.385, 0.64])
    w = np.arange(1, S.NT + 1)
    ax2.fill_between(w, m0 - 1.645 * s0, m0 + 1.645 * s0, color=ORANGE, alpha=0.22, lw=0)
    ax2.fill_between(w, m4 - 1.645 * s4, m4 + 1.645 * s4, color=BLUE, alpha=0.35, lw=0)
    ax2.plot(w, cs['h'][S.IW], color=REF, lw=1.4)
    ax2.plot(w, tw['hc'], color=INK, lw=1.4)
    ax2.set_xlabel('week'); ax2.set_ylabel('head at the well (m)')
    ax2.set_xlim(1, S.NT)
    GF.style(ax2, grid='y')
    handles = [Line2D([], [], color=REF, lw=1.4, label='factual head'),
               plt.Rectangle((0, 0), 1, 1, fc=BLUE, alpha=0.35, label='counterfactual band'),
               Line2D([], [], color=INK, lw=1.4, label='twin head'),
               plt.Rectangle((0, 0), 1, 1, fc=ORANGE, alpha=0.22, label='interventional band')]
    fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.515, 1.0), ncol=2, frameon=False,
               columnspacing=1.0, handlelength=1.4, borderaxespad=0.3)
    fig.savefig(os.path.join(out, 'fig_scheme.png'), dpi=300)
    plt.close(fig)


def log_axis(ax, ticks):
    ax.set_yscale('log')
    ax.yaxis.set_major_locator(FixedLocator(ticks)); ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'))


def fig_cf(out, D):
    fig, axs = plt.subplots(1, 3, figsize=(170 * MM, 74 * MM), sharey=True)
    x = np.arange(len(GOALS))
    off = np.linspace(-0.27, 0.27, len(METHODS))
    hi, lo = 1.0, 1.0
    for ax, scen, ttl in ((axs[0], 'none', 'no shift'), (axs[1], 'delay', 'delay 35 d in the field'),
                          (axs[2], 'params', 'shifted parameters')):
        R = D['cf']['drought'][scen]
        for g_i, g in enumerate(GOALS):
            fl = R[g]['floor']['halfwidth']
            for o_, (key, lab, col, mk) in zip(off, METHODS):
                v = R[g][key]
                rk = v.get('risk', 0.10)
                r_ = v['halfwidth'] / fl
                hi, lo = max(hi, r_), min(lo, r_)
                ax.plot(g_i + o_, r_, mk, color=col, ms=5.8, mfc=col if rk <= 0.105 else 'white', mew=1.3)
        ax.axhline(1, color=INK, lw=1.0, ls='--')
        ax.set_xticks(x); ax.set_xticklabels(TICKS)
        ax.set_xlim(-0.55, len(GOALS) - 0.45)
        ax.set_title(ttl); GF.style(ax, grid='y')
    log_axis(axs[0], [t for t in (0.5, 0.7, 1, 1.5, 2, 3, 5, 10, 20, 50, 100) if lo * 0.9 <= t <= hi * 1.4])
    axs[0].set_ylim(lo * 0.9, hi * 1.4)
    axs[0].set_ylabel('half-width ÷ floor of the real law')
    handles = [Line2D([], [], color=col, marker=mk, ls='', ms=6, label=lab) for _, lab, col, mk in METHODS] + \
              [Line2D([], [], color=INK, marker='o', ls='', ms=6, mfc='white', label='open: risk above 0.10')]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0),
               columnspacing=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.82), w_pad=0.8)
    fig.savefig(os.path.join(out, 'fig_cf.png'), dpi=300)
    plt.close(fig)


def fig_design(out, D):
    names = list(D['designs'].keys())
    short = ['rain\nonly', '1', '2', '4', '8', '4 +\ngauge']
    cols = dict(dr=ORANGE, dh=AQUA, rc=BLUE, hc=VIOLET)
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 70 * MM))
    x = np.arange(len(names))
    for g in GOALS:
        base = D['designs'][names[0]][g]['floor']['halfwidth']
        fl = [D['designs'][n][g]['floor']['halfwidth'] / base for n in names]
        ls, mf = ('--', 'white') if g == 'dh' else ('-', cols[g])
        axs[0].plot(x, fl, ls, marker='o', color=cols[g], ms=4.5, lw=1.4, mfc=mf, label=GL[g])
        axs[1].plot(x, [1 / v for v in fl], ls, marker='o', color=cols[g], ms=4.5, lw=1.4, mfc=mf)
    axs[0].set_ylabel('floor ÷ interventional floor'); axs[0].set_ylim(0, 1.08)
    axs[0].set_title('what abduction leaves')
    axs[1].set_ylabel('value of abduction'); axs[1].set_yscale('log')
    axs[1].yaxis.set_major_locator(FixedLocator([1, 2, 5, 10, 20, 50])); axs[1].yaxis.set_minor_locator(NullLocator())
    axs[1].yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'))
    axs[1].set_title('interventional ÷ counterfactual floor')
    for ax in axs:
        ax.set_xticks(x); ax.set_xticklabels(short); GF.style(ax, grid='y'); ax.set_xlabel('loggers')
    fig.legend(*axs[0].get_legend_handles_labels(), loc='upper center', ncol=2, frameon=False,
               bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.86), w_pad=2.0)
    fig.savefig(os.path.join(out, 'fig_design.png'), dpi=300)
    plt.close(fig)


def fig_coupling(out, D):
    C = D['coupling']
    rts = [r for r in ('1.0', '0.6', '0.0')]
    cols = {'1.0': BLUE, '0.6': AQUA, '0.0': ORANGE}
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 72 * MM))
    x = np.arange(len(GOALS))
    wb = 0.26
    hi = 1.0
    for i, rt in enumerate(rts):
        v = [C[rt][g]['floor']['halfwidth'] / C['1.0'][g]['floor']['halfwidth'] for g in GOALS]
        hi = max(hi, max(v))
        axs[0].bar(x + (i - 1) * wb, v, width=wb * 0.92, color=cols[rt], label=f'ρ = {float(rt):g} in the field')
    axs[0].set_yscale('log')
    axs[0].yaxis.set_major_locator(FixedLocator([1, 2, 5, 10, 20])); axs[0].yaxis.set_minor_locator(NullLocator())
    axs[0].yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'))
    axs[0].set_ylim(0.8, hi * 1.5)
    axs[0].set_ylabel('floor ÷ floor with shared noise')
    axs[0].set_title('price of the coupling')
    mk = dict(shared=('o', REF, 'band that assumes ρ = 1'), right=('s', BLUE, 'band with the right ρ'),
              robust=('D', VIOLET, 'band robust to every ρ'))
    off = dict(shared=-0.22, right=0.0, robust=0.22)
    for i, rt in enumerate(rts):
        for tag, (m_, c_, _) in mk.items():
            rk = [C[rt][g][tag]['risk'] for g in GOALS]
            axs[1].plot(np.full(4, i + off[tag]), rk, m_, color=c_, ms=5.2, ls='', alpha=0.9)
    axs[1].axhline(0.10, color=INK, lw=1.0, ls='--')
    axs[1].set_xticks(range(len(rts))); axs[1].set_xticklabels([f'ρ = {float(r):g}' for r in rts])
    axs[1].set_xlabel('coupling in the field'); axs[1].set_ylabel('risk (share of weeks outside)')
    axs[1].set_title('risk of each band, four goals')
    axs[1].set_ylim(0, max(0.12, max(C[rt][g]['shared']['risk'] for rt in rts for g in GOALS) * 1.1))
    for ax in axs:
        GF.style(ax, grid='y')
    axs[0].set_xticks(x); axs[0].set_xticklabels(TICKS)
    h0, l0 = axs[0].get_legend_handles_labels()
    h1 = [Line2D([], [], color=c_, marker=m_, ls='', ms=6, label=l_) for m_, c_, l_ in mk.values()]
    fig.legend(h0 + h1, l0 + [h.get_label() for h in h1], loc='upper center', ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 1.0), columnspacing=1.0)
    fig.tight_layout(rect=(0, 0, 1, 0.82), w_pad=2.0)
    fig.savefig(os.path.join(out, 'fig_coupling.png'), dpi=300)
    plt.close(fig)


def main(out, cards=None):
    os.makedirs(out, exist_ok=True)
    D = load()
    fig_scheme(out, D)
    fig_cf(out, D)
    fig_design(out, D)
    fig_coupling(out, D)
    if cards is not None:
        GF.fig_map(out, cards)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, 'figs'))
