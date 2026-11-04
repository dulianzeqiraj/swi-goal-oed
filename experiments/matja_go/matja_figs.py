"""Figures of the MATJA-GO review (English labels; every text at least 8.6 pt at the printed size, 17 cm wide).
usage: python matja_figs.py OUT_DIR

fig_scheme   the MATJA-GO loop: candidate instruments -> simulated aquifers carrying that instrument -> one reconstructor
             -> calibrated (guaranteed) width -> choice -> fresh recalibration
fig_single   one instrument at a time (fresh pool): what the ensemble, the exact posterior and the calibrated width
             say it is worth
fig_paths    guaranteed half-width (fresh pool) against the number of instruments, for the designs chosen by each criterion
fig_spur     the tide gauge with rain only (worth nothing for r, q_L, kappa): measured spread and error variance factors
             and half-width factors against the ensemble size, with the exact factors of Proposition M3
fig_map      the twenty papers of this review against the steps and the unknowns they inform
Numbers come from res/matja.json and res/matja_spur.json."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', 'rindertimi_go'))
import gar_figs as GF  # noqa: E402  (style, palette, map figure)
from rgo_figs import Canvas, C as SC, INK, MUTED, GRID  # noqa: E402

RES = os.path.join(HERE, 'res')
FS = GF.FS
BLUE, ORANGE, AQUA, VIOLET, REF = GF.BLUE, GF.ORANGE, GF.AQUA, GF.VIOLET, GF.REF
MM = GF.MM
SITES_X = (250, 750, 1250, 2000, 2750, 3500, 4250, 4750)
LAB = {f'L{j}': f'logger {x / 1000:g} km' for j, x in enumerate(SITES_X)}
LAB['TG'] = 'tide gauge'
GOALS = (('r', 'recharge $r$ (mm/d)'), ('qL', 'inflow $q_L$ (m²/d)'), ('kappa', 'coefficient $\\kappa$ (–)'))


def load():
    with open(os.path.join(RES, 'matja.json')) as fh:
        return json.load(fh)


def fig_scheme(out, D):
    cv = Canvas(170, 92)
    x = np.array(SITES_X) / 1000.0
    # row 1: candidates -> simulated aquifers with the instrument -> reconstructor -> calibrated width
    y0, h = 50, 38
    cv.box(2, y0, 40, h, SC['dat_f'], SC['dat_e'])
    cv.text(22, y0 + h - 4.5, 'Instruments', size=9.4, weight='bold', color=SC['dat_e'])
    a = cv.inset(5, y0 + 17, 34, 10)
    a.plot([0, 5], [0, 0], color=INK, lw=1.0)
    a.axvspan(-0.75, 0.0, color='#9cc3ec')
    a.plot(x, np.zeros_like(x), 'v', color=BLUE, ms=6)
    a.plot([-0.38], [0], 's', color=INK, ms=5)
    a.set_xlim(-0.8, 5.2); a.set_ylim(-1, 1); a.axis('off')
    cv.text(22, y0 + 13.4, '8 logger sites ▼')
    cv.text(22, y0 + 8.8, 'tide gauge ■ at the sea')
    cv.text(22, y0 + 4.2, 'the rain, always', color=MUTED)
    cv.box(46, y0, 38, h, SC['sim_f'], SC['sim_e'])
    cv.text(65, y0 + h - 4.5, 'Simulated aquifers', size=9.4, weight='bold', color=SC['sim_e'])
    cv.text(65, y0 + 25.5, 'each carries the data')
    cv.text(65, y0 + 20.9, 'of the instrument')
    cv.text(65, y0 + 12.5, 'truth known:')
    cv.text(65, y0 + 7.9, 'physical prior, rain law')
    cv.box(88, y0, 38, h, SC['no_f'], SC['no_e'])
    cv.text(107, y0 + h - 4.5, 'One reconstructor', size=9.4, weight='bold', color=SC['no_e'])
    cv.text(107, y0 + 25.5, 'ensemble smoother')
    cv.text(107, y0 + 20.9, 'with the exact solver')
    cv.text(107, y0 + 12.5, 'its spread $s$ can be')
    cv.text(107, y0 + 7.9, 'too narrow or too wide')
    cv.box(130, y0, 38, h, SC['lik_f'], SC['lik_e'])
    cv.text(149, y0 + h - 4.5, 'Guaranteed width', size=9.4, weight='bold', color=SC['lik_e'])
    cv.text(149, y0 + 25.5, '$W(D)=\\hat\\lambda_D\\,\\bar s_D$')
    cv.text(149, y0 + 17.5, 'CRC on the simulated')
    cv.text(149, y0 + 12.9, 'aquifers of design $D$')
    cv.text(149, y0 + 5.5, 'not $1.645\\,\\bar s_D$', color=SC['out_e'])
    for x0, x1 in ((42, 46), (84, 88), (126, 130)):
        cv.arrow(x0, y0 + 19, x1, y0 + 19, lw=1.1)
    # row 2, read from right to left: choose, then recalibrate, then the next instrument
    y1, h1 = 4, 38
    cv.box(88, y1, 80, h1, SC['out_f'], SC['out_e'])
    cv.text(128, y1 + h1 - 4.5, 'Choose the instrument', size=9.4, weight='bold', color=SC['out_e'])
    cv.text(128, y1 + 25.0, '$D_{k+1}=D_k\\cup\\{\\arg\\min_c W(D_k\\cup\\{c\\})\\}$')
    cv.text(128, y1 + 15.5, 'value of $c$ = guaranteed width it removes')
    cv.text(128, y1 + 8.0, 'an instrument can have a negative value', color=SC['out_e'])
    cv.box(2, y1, 80, h1, SC['zoom_f'], SC['zoom_e'])
    cv.text(42, y1 + h1 - 4.5, 'Recalibrate on fresh aquifers', size=9.4, weight='bold', color=SC['zoom_e'])
    cv.text(42, y1 + 25.0, 'pool A chooses, pool B calibrates')
    cv.text(42, y1 + 15.5, 'the guarantee holds for the chosen design')
    cv.text(42, y1 + 8.0, '(Proposition M1)')
    cv.arrow(149, y0, 149, y1 + h1, lw=1.1)
    cv.arrow(88, y1 + 19, 82, y1 + 19, lw=1.1)
    cv.arrow(22, y1 + h1, 22, y0, lw=1.1)
    cv.text(23.5, (y1 + h1 + y0) / 2, 'next instrument', ha='left', color=MUTED)
    cv.fig.savefig(os.path.join(out, 'fig_scheme.png'), dpi=300)
    plt.close(cv.fig)


def fig_single(out, S):
    """S: res/matja_single.json, every single instrument recalibrated and scored on the fresh pool."""
    base = S['rain only']
    cands = [c for c in S if c != 'rain only' and not c.startswith('_')]
    fig, axs = plt.subplots(1, 3, figsize=(170 * MM, 74 * MM), sharey=True)
    y = np.arange(len(cands))[::-1]
    keys = (('es_halfwidth', ORANGE, 0.22), ('exact_halfwidth', REF, 0.0), ('halfwidth', BLUE, -0.22))
    for ax, (g, ttl) in zip(axs, GOALS):
        b = base[g]
        for j, c in enumerate(cands):
            v = S[c][g]
            for key, col, dy in keys:
                ax.plot([b[key] - v[key]], [y[j] + dy], 'o', color=col, ms=5)
        ax.axvline(0, color=INK, lw=0.8)
        ax.set_title(ttl); GF.style(ax, grid='x')
        ax.set_xlabel('half-width removed')
        ax.set_ylim(-0.7, len(cands) - 0.3)
    axs[0].set_yticks(y); axs[0].set_yticklabels([LAB[c] for c in cands])
    handles = [Line2D([], [], marker='o', ls='', color=ORANGE, label='raw ensemble (1.645 s)'),
               Line2D([], [], marker='o', ls='', color=REF, label='exact posterior (oracle)'),
               Line2D([], [], marker='o', ls='', color=BLUE, label='guaranteed (MATJA-GO)')]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.9), w_pad=1.0)
    fig.savefig(os.path.join(out, 'fig_single.png'), dpi=300)
    plt.close(fig)


def logticks(ax, ticks):
    from matplotlib.ticker import FixedLocator, NullLocator, FuncFormatter
    ax.yaxis.set_major_locator(FixedLocator(ticks)); ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'))


def fig_paths(out, D):
    fr = D['fresh']
    fig, axs = plt.subplots(1, 3, figsize=(170 * MM, 70 * MM))
    cols = dict(es=(ORANGE, -0.09), oracle=(REF, 0.0), matja=(BLUE, 0.09))
    ticks = dict(r=[0.05, 0.1, 0.2, 0.5], qL=[0.05, 0.1, 0.2, 0.5, 1.0], kappa=[0.002, 0.005, 0.01, 0.02, 0.05, 0.1])
    for ax, (g, ttl) in zip(axs, GOALS):
        for cr, (col, dx) in cols.items():
            steps = D['paths'][f'{g}/{cr}']
            names = ['rain only'] + ['+'.join(sorted(s_['design'])) for s_ in steps]
            vals = [fr[n][g]['halfwidth'] for n in names]
            ax.plot(np.arange(len(vals)) + dx, vals, '-o', color=col, ms=4.2, lw=1.3, zorder=3)
            if cr == 'es':
                claim = [fr[n][g]['es_halfwidth'] for n in names]
                ax.plot(np.arange(len(vals)) + dx, claim, '--', color=ORANGE, lw=1.1, zorder=2)
        ax.set_yscale('log'); logticks(ax, ticks[g])
        ax.set_xticks(range(4)); ax.set_xlabel('instruments chosen')
        ax.set_title(ttl); GF.style(ax, grid='both')
    axs[0].set_ylabel('90% half-width (fresh pool)')
    handles = [Line2D([], [], color=c, marker='o', ms=4, lw=1.3, label=l) for c, l in
               ((ORANGE, 'guaranteed, design chosen by the raw ensemble'), (REF, 'guaranteed, chosen by the exact posterior'),
                (BLUE, 'guaranteed, chosen by MATJA-GO'))] + \
              [Line2D([], [], color=ORANGE, ls='--', lw=1.1, label='what the raw ensemble claims for its design')]
    fig.legend(handles=handles, loc='upper center', ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.84), w_pad=1.0)
    fig.savefig(os.path.join(out, 'fig_paths.png'), dpi=300)
    plt.close(fig)


def fig_spur(out, SP):
    Ns = sorted(int(k) for k in SP['sizes'])
    rows = [SP['sizes'][str(n)] for n in Ns]
    mk = dict(qL='o', r='s', kappa='^')
    goals = ('qL', 'r', 'kappa')
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 72 * MM))
    jit = dict(qL=0.94, r=1.0, kappa=1.06)
    ax = axs[0]
    ax.plot(Ns, [r_['pred_spread'] for r_ in rows], '-', color=ORANGE, lw=1.3)
    ax.plot(Ns, [r_['pred_error'] for r_ in rows], '-', color=BLUE, lw=1.3)
    for g in goals:
        x = [n * jit[g] for n in Ns]
        ax.plot(x, [r_['tg'][g]['spr2'] / r_['base'][g]['spr2'] for r_ in rows], mk[g], color=ORANGE, ms=5, mfc='white',
                mew=1.2)
        ax.plot(x, [r_['tg'][g]['err2'] / r_['base'][g]['err2'] for r_ in rows], mk[g], color=BLUE, ms=5, mfc='white',
                mew=1.2)
    ax.axhline(1, color=REF, lw=1.3)
    ax.set_yscale('log'); logticks(ax, [0.1, 0.2, 0.5, 1, 2, 5])
    ax.set_title('variance factors (tide gauge ÷ rain only)')
    ax.text(150, 1.75, 'error variance', color=BLUE, va='bottom', ha='left')
    ax.text(150, 0.55, 'spread variance', color=ORANGE, va='top', ha='left')
    ax = axs[1]
    ax.plot(Ns, [r_['pred_es'] for r_ in rows], '-', color=ORANGE, lw=1.3)
    ax.plot(Ns, [r_['pred_matja'] for r_ in rows], '-', color=BLUE, lw=1.3)
    for g in goals:
        x = [n * jit[g] for n in Ns]
        ax.plot(x, [r_['tg'][g]['es'] / r_['base'][g]['es'] for r_ in rows], mk[g], color=ORANGE, ms=5, mfc='white',
                mew=1.2)
        ax.plot(x, [r_['tg'][g]['matja'] / r_['base'][g]['matja'] for r_ in rows], mk[g], color=BLUE, ms=5,
                mfc='white', mew=1.2)
    ax.axhline(1, color=REF, lw=1.3)
    ax.set_yscale('log'); logticks(ax, [0.3, 0.5, 0.7, 1, 1.5, 2])
    ax.set_title('half-width factors')
    ax.text(150, 1.30, 'guaranteed', color=BLUE, va='bottom', ha='left')
    ax.text(150, 0.78, 'raw ensemble', color=ORANGE, va='top', ha='left')
    for ax in axs:
        ax.set_xscale('log', base=2)
        ax.set_xticks(Ns); ax.set_xticklabels([str(n) for n in Ns]); ax.minorticks_off()
        ax.set_xlabel('ensemble members $N$')
        GF.style(ax, grid='both')
    handles = [Line2D([], [], color=INK, lw=1.3, label='exact law (Proposition M3)'),
               Line2D([], [], color=REF, lw=1.3, label='exact posterior: no change')] + \
              [Line2D([], [], marker=mk[g], ls='', color=INK, mfc='white', ms=5, label=f'measured, {GF.SYM[g]}')
               for g in goals]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.84), w_pad=1.5)
    fig.savefig(os.path.join(out, 'fig_spur.png'), dpi=300)
    plt.close(fig)


def main(out, cards=None):
    os.makedirs(out, exist_ok=True)
    D = load()
    fig_scheme(out, D)
    with open(os.path.join(RES, 'matja_single.json')) as fh:
        fig_single(out, json.load(fh))
    fig_paths(out, D)
    sp = os.path.join(RES, 'matja_spur.json')
    if os.path.exists(sp):
        with open(sp) as fh:
            fig_spur(out, json.load(fh))
    if cards is not None:
        GF.fig_map(out, cards)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, 'figs'))
