"""Figures of the PRIRJA-GO review (English labels; every text at least 8.6 pt at the printed size, 17 cm wide).
usage: python prirja_figs.py OUT_DIR

fig_scheme   horizon-matched calibration on a time line: past origins, their windows and scored years, and the
             deployment window and field year
fig_drift    the vadose delay of the three drift laws, and the mean standardised error of kappa by year
fig_risk     realized risk against the horizon h for recharge and kappa under the three drift laws
fig_width    half-width against the horizon h for recharge and kappa, without drift and under linear drift
fig_map      the twenty papers of this review against the steps and the unknowns they inform
Numbers come from res/prirja.json."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches  # noqa: F401
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
LAWLAB = dict(none='no drift', linear='linear drift', accel='accelerating drift', step='abrupt shift (year 24)')
MSTY = dict(sims=dict(c=REF, m='o', ls='--', lab='simulations (year 0)'),
            all=dict(c=ORANGE, m='s', ls='-', lab='all 30 past years'),
            recent=dict(c='#c9a227', m='D', ls='-', lab='last 9 years'),
            ls0=dict(c=BLUE, m='o', ls='-', lab='horizon-matched, level (L = 5)'),
            ls1=dict(c=VIOLET, m='^', ls='-', lab='horizon-matched, trend (L = 10)'),
            loc0=dict(c=AQUA, m='v', ls=':', lab='level, location only'))


def load():
    with open(os.path.join(RES, 'prirja.json')) as fh:
        return json.load(fh)


def series(D, law, g, mth, key='risk'):
    hs, vs = [], []
    for h in D['hs']:
        v = D['res'][law][g][mth][str(h)]
        if v['finite'] < 0.999 and mth not in ('sims',):
            continue
        hs.append(h); vs.append(v[key])
    return hs, vs


def fig_scheme(out, D):
    cv = Canvas(170, 92)
    K, L, h = 30, 5, 6
    x0, dx = 14.0, 3.45

    def X(t):
        return x0 + (t - 0.5) * dx

    yb = 32.0
    cv.ax.add_patch(matplotlib.patches.Rectangle((X(K + 0.5), yb - 1.0), X(K + h + 0.6) - X(K + 0.5), 89.5 - yb,
                                                 fc='#f4f1fb', ec='none', zorder=0))
    cv.line([X(0.5), X(K + h + 0.6)], [yb, yb], c=MUTED, lw=0.8)
    for t in range(1, K + h + 1):
        cv.line([X(t), X(t)], [yb - 0.8, yb + 0.8], c=MUTED, lw=0.5)
    for t in (1, 10, 20, K):
        cv.text(X(t), yb - 3.2, f'{t}', color=MUTED)
    cv.text(X(K + h), yb - 3.2, 'K+h', color=VIOLET)
    cv.text(X(0.5) - 1.0, yb - 3.2, 'year', ha='right', color=MUTED)
    cv.text((X(1) + X(K)) / 2, 87.0, f'past years with a measured boundary: anchors 1 … K (K = {K})', color=INK,
            weight='bold')
    cv.text((X(K + 1) + X(K + h)) / 2 + 1.0, 87.0, 'future', color=VIOLET, weight='bold')
    rows = [(5, 'origin o'), (12, ''), (19, ''), (K - h, 'last origin')]
    y = 78.0
    for o, lab in rows:
        cv.box(X(o - L + 1) - 1.4, y - 2.2, (L - 1) * dx + 2.8, 4.4, '#dbe7fb', BLUE, lw=0.8, r=1.0)
        cv.arrow(X(o) + 1.6, y, X(o + h) - 1.6, y, c=MUTED, lw=0.8)
        cv.ax.plot(X(o + h), y, 'o', color=ORANGE, ms=5.5, zorder=30)
        if lab:
            cv.text(X(o - L + 1) - 2.6, y, lab, ha='right', color=MUTED)
        y -= 8.0
    yd = y - 1.0
    cv.box(X(K - L + 1) - 1.4, yd - 2.2, (L - 1) * dx + 2.8, 4.4, '#e7e2fa', VIOLET, lw=1.0, r=1.0)
    cv.arrow(X(K) + 1.6, yd, X(K + h) - 1.6, yd, c=VIOLET, lw=1.0)
    cv.ax.plot(X(K + h), yd, 's', color=VIOLET, ms=6.0, zorder=30)
    cv.text(X(K - L + 1) - 2.6, yd, 'deployment', ha='right', color=VIOLET)
    ty = 19.0
    cv.box(4, 2.5, 162, 21.0, '#f7f8fa', '#c9ced6', lw=0.6, r=1.4)
    cv.text(8, ty, 'window of L years: centre $c_o$ and spread $\\sigma_o$', ha='left', color=BLUE)
    cv.text(8, ty - 6.4, 'score of the year $o+h$:  $|u-c_o|\\,/\\,\\sigma_o$', ha='left', color=ORANGE)
    cv.text(8, ty - 12.8, 'the same horizon h in calibration and in use', ha='left', color=INK)
    cv.text(86, ty, '$n(h)=K-L-h+1$ scores; a band needs $n(h)\\geq 9$', ha='left', color=INK)
    cv.text(86, ty - 6.4, 'field band: $m+s\\,(c_K\\pm\\hat\\lambda\\,\\sigma_K)$', ha='left', color=VIOLET)
    cv.text(86, ty - 12.8, f'here L = {L}, h = {h}: {K - L - h + 1} scores', ha='left', color=MUTED)
    cv.fig.savefig(os.path.join(out, 'fig_scheme.png'), dpi=300)
    plt.close(cv.fig)


def fig_drift(out, D):
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 62 * MM))
    t = np.arange(0, 51)
    cols = dict(none=REF, linear=BLUE, accel=ORANGE, step=VIOLET)
    tau = dict(none=14 + 0 * t, linear=14 + 0.42 * t, accel=14 + 21 * (t / 50) ** 2,
               step=np.where(t >= D['t_step'], 28.0, 14.0))
    for law in ('none', 'linear', 'accel', 'step'):
        axs[0].plot(t, tau[law], color=cols[law], lw=1.6, label=LAWLAB[law])
        ub = D['res'][law]['kappa']['ubar_by_year']
        axs[1].plot(np.arange(1, D['K'] + 1), ub, color=cols[law], lw=1.3)
        axs[1].plot([D['K'] + h for h in D['hs']], D['res'][law]['kappa']['ubar_test'], 'o', color=cols[law], ms=3.8)
    for ax in axs:
        ax.axvspan(D['K'] + 0.5, 51, color='#f4f1fb', zorder=0)
        ax.set_xlabel('year'); GF.style(ax, grid='both')
    axs[0].set_ylabel('vadose delay in the field (d)')
    axs[0].set_title('the drift (simulator: 14 d)')
    axs[1].set_ylabel('κ error ÷ ensemble sd')
    axs[1].set_title('what it does to the κ reconstruction')
    axs[1].axhline(0, color=INK, lw=0.6)
    axs[1].text(0.70, 0.06, 'future', transform=axs[1].transAxes, color=VIOLET)
    axs[0].text(0.70, 0.06, 'future', transform=axs[0].transAxes, color=VIOLET)
    handles = [Line2D([], [], color=cols[l], lw=1.6, label=LAWLAB[l]) for l in ('none', 'linear', 'accel', 'step')]
    fig.legend(handles=handles, loc='upper center', ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.9), w_pad=2.0)
    fig.savefig(os.path.join(out, 'fig_drift.png'), dpi=300)
    plt.close(fig)


def fig_risk(out, D):
    laws = ('linear', 'accel', 'step')
    fig, axs = plt.subplots(2, 3, figsize=(170 * MM, 112 * MM), sharex=True)
    for i, (g, gl) in enumerate((('r', 'recharge $r$'), ('kappa', 'coefficient $\\kappa$'))):
        for j, law in enumerate(laws):
            ax = axs[i, j]
            for mth in ('sims', 'all', 'recent', 'ls0', 'ls1'):
                st = MSTY[mth]
                hs, vs = series(D, law, g, mth)
                ax.plot(hs, vs, color=st['c'], marker=st['m'], ls=st['ls'], lw=1.3 if mth != 'ls0' else 1.9, ms=4)
            ax.axhline(D['alpha'], color=INK, lw=0.8, ls='--')
            ax.axvline(D['h_max']['0'] + 0.5, color=BLUE, lw=0.6, ls=':')
            ax.set_ylim(-0.02, 0.7 if g == 'kappa' else 0.4)
            ax.set_title(f'{gl}, {LAWLAB[law]}' if law != 'step' else f'{gl}, abrupt shift')
            GF.style(ax, grid='both')
            if i == 1:
                ax.set_xlabel('horizon h (years after the record)')
        axs[i, 0].set_ylabel('share of weeks outside')
    handles = [Line2D([], [], color=MSTY[m]['c'], marker=MSTY[m]['m'], ls=MSTY[m]['ls'], ms=4, lw=1.3,
                      label=MSTY[m]['lab']) for m in ('sims', 'all', 'recent', 'ls0', 'ls1')]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.88), h_pad=1.0, w_pad=1.0)
    fig.savefig(os.path.join(out, 'fig_risk.png'), dpi=300)
    plt.close(fig)


def fig_width(out, D):
    fig, axs = plt.subplots(2, 2, figsize=(170 * MM, 104 * MM), sharex=True)
    for i, (g, gl, un) in enumerate((('r', 'recharge $r$', 'mm/d'), ('kappa', 'coefficient $\\kappa$', '–'))):
        for j, law in enumerate(('none', 'linear')):
            ax = axs[i, j]
            for mth in ('sims', 'all', 'recent', 'ls0', 'ls1'):
                st = MSTY[mth]
                hs, vs = series(D, law, g, mth, 'halfwidth')
                ax.plot(hs, vs, color=st['c'], marker=st['m'], ls=st['ls'], lw=1.3 if mth != 'ls0' else 1.9, ms=4)
            ax.set_title(f'{gl}, {LAWLAB[law]}')
            ax.set_ylim(bottom=0)
            GF.style(ax, grid='both')
            if i == 1:
                ax.set_xlabel('horizon h (years after the record)')
            if j == 0:
                ax.set_ylabel(f'half-width ({un})' if un != '–' else 'half-width')
    handles = [Line2D([], [], color=MSTY[m]['c'], marker=MSTY[m]['m'], ls=MSTY[m]['ls'], ms=4, lw=1.3,
                      label=MSTY[m]['lab']) for m in ('sims', 'all', 'recent', 'ls0', 'ls1')]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.87), h_pad=1.0, w_pad=1.5)
    fig.savefig(os.path.join(out, 'fig_width.png'), dpi=300)
    plt.close(fig)


def main(out, cards=None):
    os.makedirs(out, exist_ok=True)
    D = load()
    fig_scheme(out, D)
    fig_drift(out, D)
    fig_risk(out, D)
    fig_width(out, D)
    if cards is not None:
        GF.fig_map(out, cards)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, 'figs'))
