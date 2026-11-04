"""Figures of the ANKORA-GO review (English labels; every text at least 8.6 pt at the printed size, 17 cm wide).
usage: python ankora_figs.py OUT_DIR

fig_scheme   simulated aquifers, real anchors and the field: who calibrates what, and the minimum numbers of anchors
fig_risk     realized risk (share of weeks outside the 90% band) of the simulation-calibrated and anchor-calibrated
             bands, for the four field laws
fig_width    half-width of the anchor-calibrated bands relative to the simulation-calibrated band
fig_mix      risk and half-width when simulations and anchors are mixed in one calibration (share psi on simulations)
fig_map      the twenty papers of this review against the steps and the unknowns they inform
Numbers come from res/ankora.json."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', 'rindertimi_go'))
import gar_figs as GF  # noqa: E402
from rgo_figs import Canvas, C as SC, INK, MUTED  # noqa: E402

RES = os.path.join(HERE, 'res')
MM = GF.MM
BLUE, ORANGE, AQUA, VIOLET, REF = GF.BLUE, GF.ORANGE, GF.AQUA, GF.VIOLET, GF.REF
SCEN = (('none', 'no\nshift'), ('delay', 'delay'), ('params', 'para-\nmeters'), ('rainbias', 'rain\nbias'))
GOALS = (('r', 'recharge $r$'), ('qL', 'inflow $q_L$'), ('eta', 'sea level $\\eta$'), ('kappa', 'coefficient $\\kappa$'))
MCOL = {10: AQUA, 20: BLUE, 40: VIOLET}


def load():
    with open(os.path.join(RES, 'ankora.json')) as fh:
        return json.load(fh)


def fig_scheme(out, D):
    cv = Canvas(170, 76)
    y0, h = 34, 38
    cv.box(2, y0, 52, h, SC['sim_f'], SC['sim_e'])
    cv.text(28, y0 + h - 4.2, 'Simulated aquifers', size=9.4, weight='bold', color=SC['sim_e'])
    cv.text(28, y0 + 25.0, 'law $P$: the simulator prior')
    cv.text(28, y0 + 19.0, 'many, truth known')
    cv.text(28, y0 + 11.0, 'right only if $P$ is the field law', color=SC['out_e'])
    cv.box(58, y0, 52, h, SC['dat_f'], SC['dat_e'])
    cv.text(84, y0 + h - 4.2, 'Real anchors', size=9.4, weight='bold', color=SC['dat_e'])
    cv.text(84, y0 + 25.0, 'law $Q$: the real world')
    cv.text(84, y0 + 19.0, 'few, boundary measured')
    cv.text(84, y0 + 11.0, 'a site or a period with', color=MUTED)
    cv.text(84, y0 + 6.4, 'a tide gauge, a lysimeter …', color=MUTED)
    cv.box(114, y0, 54, h, SC['no_f'], SC['no_e'])
    cv.text(141, y0 + h - 4.2, 'The field', size=9.4, weight='bold', color=SC['no_e'])
    cv.text(141, y0 + 25.0, 'law $Q$, truth unknown')
    cv.text(141, y0 + 19.0, 'one reconstructor for all')
    cv.text(141, y0 + 11.0, 'band $m\\pm\\hat\\lambda\\,s$', color=INK)
    y1, h1 = 3, 25
    cv.box(2, y1, 80, h1, SC['zoom_f'], SC['zoom_e'])
    cv.text(42, y1 + h1 - 4.5, 'Calibrate on the anchors', size=9.4, weight='bold', color=SC['zoom_e'])
    cv.text(42, y1 + 11.5, 'valid for any $Q$ (Prop. A1)')
    cv.text(42, y1 + 5.5, f'at least {D["min_anchors"]["expectation"]} anchors on average, '
                          f'{D["min_anchors"]["certificate"]} for a certificate (A2)')
    cv.box(88, y1, 80, h1, SC['out_f'], SC['out_e'])
    cv.text(128, y1 + h1 - 4.5, 'Or mix them, with share $\\psi$', size=9.4, weight='bold', color=SC['out_e'])
    cv.text(128, y1 + 11.5, 'narrower, but the bias grows with $\\psi$')
    cv.text(128, y1 + 5.5, 'risk ≤ $\\alpha+\\psi\\,\\mathrm{TV}(P,Q)$ (Prop. A3)')
    cv.arrow(28, y0, 60, y1 + h1, lw=1.0)
    cv.arrow(84, y0, 44, y1 + h1, lw=1.1)
    cv.arrow(84, y0, 120, y1 + h1, lw=1.0)
    cv.arrow(28, y0, 110, y1 + h1, lw=1.0, ls='--')
    cv.arrow(110, y0 + 19, 114, y0 + 19, lw=1.1)
    cv.fig.savefig(os.path.join(out, 'fig_scheme.png'), dpi=300)
    plt.close(cv.fig)


def fig_risk(out, D):
    fig, axs = plt.subplots(1, 4, figsize=(170 * MM, 70 * MM), sharey=True)
    x = np.arange(len(SCEN))
    for ax, (g, ttl) in zip(axs, GOALS):
        ax.plot(x - 0.18, [D['res'][s][g]['sims']['risk'] for s, _ in SCEN], 'o', color=ORANGE, ms=5.5)
        for j, m in enumerate(D['ms']):
            ax.plot(x + 0.0 + 0.12 * j, [D['res'][s][g][f'm{m}']['anchors']['risk'] for s, _ in SCEN], 's',
                    color=MCOL[m], ms=4.5)
        ax.axhline(D['alpha'], color=INK, lw=0.8, ls='--')
        ax.set_xticks(x); ax.set_xticklabels([l for _, l in SCEN])
        ax.set_ylim(-0.02, 0.9); ax.set_title(ttl); GF.style(ax, grid='y')
    axs[0].set_ylabel('share of weeks outside (target ≤ 0.10)')
    handles = [Line2D([], [], marker='o', ls='', color=ORANGE, ms=5.5, label='calibrated on simulations')] + \
              [Line2D([], [], marker='s', ls='', color=MCOL[m], ms=4.5, label=f'on {m} anchors') for m in D['ms']]
    fig.legend(handles=handles, loc='upper center', ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.9), w_pad=0.6)
    fig.savefig(os.path.join(out, 'fig_risk.png'), dpi=300)
    plt.close(fig)


def fig_width(out, D):
    fig, axs = plt.subplots(1, 4, figsize=(170 * MM, 66 * MM), sharey=True)
    x = np.arange(len(SCEN))
    for ax, (g, ttl) in zip(axs, GOALS):
        for j, m in enumerate(D['ms']):
            v = [D['res'][s][g][f'm{m}']['anchors']['halfwidth'] / D['res'][s][g]['sims']['halfwidth'] for s, _ in SCEN]
            ax.plot(x + 0.12 * (j - 1), v, 's', color=MCOL[m], ms=4.5)
        ax.axhline(1.0, color=ORANGE, lw=1.0)
        ax.set_yscale('log')
        from matplotlib.ticker import FixedLocator, NullLocator, FuncFormatter
        ax.yaxis.set_major_locator(FixedLocator([1, 2, 5, 10])); ax.yaxis.set_minor_locator(NullLocator())
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'))
        ax.set_xticks(x); ax.set_xticklabels([l for _, l in SCEN])
        ax.set_title(ttl); GF.style(ax, grid='y')
    axs[0].set_ylabel('half-width ÷ simulation-calibrated')
    handles = [Line2D([], [], color=ORANGE, lw=1.0, label='simulation-calibrated (= 1)')] + \
              [Line2D([], [], marker='s', ls='', color=MCOL[m], ms=4.5, label=f'{m} anchors') for m in D['ms']]
    fig.legend(handles=handles, loc='upper center', ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.9), w_pad=0.6)
    fig.savefig(os.path.join(out, 'fig_width.png'), dpi=300)
    plt.close(fig)


def fig_mix(out, D, m=20):
    psis = [0.0] + [float(p) for p in D['psis'] if p not in (0.0, 1.0)] + [1.0]
    cols = dict(none=REF, delay=ORANGE, params=BLUE, rainbias=VIOLET)
    fig, axs = plt.subplots(2, 2, figsize=(170 * MM, 110 * MM), sharex=True)
    for j, (g, ttl) in enumerate((('r', 'recharge $r$'), ('kappa', 'coefficient $\\kappa$'))):
        for s, lab in SCEN:
            R = D['res'][s][g]
            risk = [R[f'm{m}']['anchors']['risk']] + [R[f'm{m}']['mix'][str(p)]['risk'] for p in psis[1:-1]] + \
                   [R['sims']['risk']]
            hw = [R[f'm{m}']['anchors']['halfwidth']] + [R[f'm{m}']['mix'][str(p)]['halfwidth'] for p in psis[1:-1]] + \
                 [R['sims']['halfwidth']]
            axs[0, j].plot(psis, risk, '-o', color=cols[s], ms=4, lw=1.3)
            axs[1, j].plot(psis, hw, '-o', color=cols[s], ms=4, lw=1.3)
        axs[0, j].axhline(D['alpha'], color=INK, lw=0.8, ls='--')
        axs[0, j].set_title(f'{ttl}: risk'); axs[1, j].set_title(f'{ttl}: half-width')
        axs[1, j].set_xlabel('share of the calibration weight on simulations, $\\psi$')
        for ax in axs[:, j]:
            GF.style(ax, grid='both')
    handles = [Line2D([], [], color=cols[s], marker='o', ms=4, lw=1.3, label=lab.replace('\n', ' '))
               for s, lab in SCEN]
    fig.legend(handles=handles, loc='upper center', ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.94), h_pad=1.0, w_pad=1.5)
    fig.savefig(os.path.join(out, 'fig_mix.png'), dpi=300)
    plt.close(fig)


def main(out, cards=None):
    os.makedirs(out, exist_ok=True)
    D = load()
    fig_scheme(out, D)
    fig_risk(out, D)
    fig_width(out, D)
    fig_mix(out, D)
    if cards is not None:
        GF.fig_map(out, cards)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, 'figs'))
