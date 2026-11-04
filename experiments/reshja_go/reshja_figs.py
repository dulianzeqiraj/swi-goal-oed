"""Figures of the RESHJA-GO review (English labels; every text at least 8.6 pt at the printed size, 17 cm wide).
usage: python reshja_figs.py OUT_DIR

fig_scheme   the rain product, the vadose filter, what the heads can see, and what can be guaranteed
fig_cover    whole-function coverage of the 90% bands against the number of loggers, for the four rain settings
fig_floor    guaranteed half-width of kappa and of the recharge against the number of loggers, with the floor of
             Proposition R1
fig_filter   Proposition R2: measured against predicted relative variance of the filtered product error, and the
             effective number of rain days
fig_map      the twenty papers of this review against the steps and the unknowns they inform
Numbers come from res/reshja.json."""
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
sys.path.insert(3, os.path.join(HERE, '..', 'matja_go'))
import gar_figs as GF  # noqa: E402
from rgo_figs import Canvas, C as SC, INK, MUTED  # noqa: E402
from matja_figs import logticks  # noqa: E402

RES = os.path.join(HERE, 'res')
MM = GF.MM
BLUE, ORANGE, AQUA, VIOLET, REF = GF.BLUE, GF.ORANGE, GF.AQUA, GF.VIOLET, GF.REF
SET = (('exact', REF, 'exact rain'), ('naive', ORANGE, 'product, as if exact'), ('aware', BLUE, 'product + its errors'),
       ('aware_r2', VIOLET, 'product + errors + R2 prior'), ('gauge', AQUA, 'local rain gauge'))
JIT = dict(exact=-0.12, naive=0.0, aware=-0.06, aware_r2=0.06, gauge=0.12)
DES = ('rain only', '1 logger', '2 loggers', '4 loggers', '8 loggers')
NLOG = (0, 1, 2, 4, 8)


def load():
    with open(os.path.join(RES, 'reshja.json')) as fh:
        return json.load(fh)


def fig_scheme(out, R):
    import gar_exp as G
    import rgo_model as M
    cv = Canvas(170, 74)
    y0, h = 31, 40
    # inset data: one record, true rain against the product, and the filtered series
    rng = np.random.default_rng(12)
    Pd = G.daily_rain(rng)
    b = 1.25
    Po = Pd / b * np.exp(0.6 * rng.standard_normal(Pd.size) - 0.18)
    cv.box(2, y0, 52, h, SC['dat_f'], SC['dat_e'])
    cv.text(28, y0 + h - 4.2, 'The rain the model sees', size=9.4, weight='bold', color=SC['dat_e'])
    a = cv.inset(6, y0 + 15, 45, 16)
    d0 = M.SPIN + 70
    t = np.arange(60)
    a.bar(t - 0.2, Pd[d0:d0 + 60], width=0.45, color=INK, label='true')
    a.bar(t + 0.25, Po[d0:d0 + 60], width=0.45, color=ORANGE, label='product')
    a.set_xticks([]); a.set_yticks([]); [sp.set_visible(False) for sp in a.spines.values()]
    cv.text(28, y0 + 10.0, 'true rain (black), product (orange)', color=INK)
    cv.text(28, y0 + 5.2, '$P_{obs}=P\\,\\epsilon/b$', color=MUTED)
    cv.box(58, y0, 52, h, SC['sim_f'], SC['sim_e'])
    cv.text(84, y0 + h - 4.2, 'The vadose filter', size=9.4, weight='bold', color=SC['sim_e'])
    a2 = cv.inset(62, y0 + 15, 45, 16)
    f = G.filtered(Pd, M.TAU_V); fo = G.filtered(Po, M.TAU_V)
    a2.plot(f / b, color=INK, lw=1.2); a2.plot(fo, color=ORANGE, lw=1.2)
    a2.set_xticks([]); a2.set_yticks([]); [sp.set_visible(False) for sp in a2.spines.values()]
    cv.text(84, y0 + 10.0, 'averages daily errors over $n_{eff}$', color=INK)
    cv.text(84, y0 + 5.2, 'rain days, passes the bias $b$ (R2)', color=INK)
    cv.box(114, y0, 54, h, SC['no_f'], SC['no_e'])
    cv.text(141, y0 + h - 4.2, 'What the heads see', size=9.4, weight='bold', color=SC['no_e'])
    cv.text(141, y0 + 26.0, '$r=(\\kappa b)\\,(k_\\tau*P_{obs})+\\dots$')
    cv.text(141, y0 + 18.0, 'only $c=\\kappa b$, never $\\kappa$, $b$ apart')
    cv.text(141, y0 + 10.0, 'a rain bias is invisible', color=SC['out_e'])
    cv.text(141, y0 + 5.2, 'to the heads (Prop. R1)', color=SC['out_e'])
    for x0, x1 in ((54, 58), (110, 114)):
        cv.arrow(x0, y0 + 20, x1, y0 + 20, lw=1.1)
    y1, h1 = 3, 22
    boxes = ((2, 'Boundary functions', 'guaranteed when the simulated', 'aquifers carry its errors (R3)',
              SC['zoom_f'], SC['zoom_e']),
             (58, 'Coefficient $\\kappa$', 'a floor no logger removes:', f'half-width ≥ {R["floor"]["halfwidth"]:.3f} at 20% bias',
              SC['out_f'], SC['out_e']),
             (114, 'A local rain gauge', 'breaks the floor: the value of', 'measuring the rain (MATJA-GO)',
              SC['lik_f'], SC['lik_e']))
    for x, t1, t2, t3, fc, ec in boxes:
        cv.box(x, y1, 52 if x < 114 else 54, h1, fc, ec)
        xc = x + (26 if x < 114 else 27)
        cv.text(xc, y1 + h1 - 4.5, t1, size=9.4, weight='bold', color=ec)
        cv.text(xc, y1 + 10.0, t2)
        cv.text(xc, y1 + 5.2, t3)
    for xc in (28, 84, 141):
        cv.arrow(xc, y0, xc, y1 + h1, lw=1.1)
    cv.fig.savefig(os.path.join(out, 'fig_scheme.png'), dpi=300)
    plt.close(cv.fig)


def fig_cover(out, R):
    goals = (('r', 'recharge $r$'), ('qL', 'inflow $q_L$'), ('eta', 'sea level $\\eta$'), ('kappa', 'coefficient $\\kappa$'))
    fig, axs = plt.subplots(1, 4, figsize=(170 * MM, 66 * MM), sharey=True)
    x = np.arange(len(DES))
    for ax, (g, ttl) in zip(axs, goals):
        for s, col, _ in SET:
            v = [R['res'][s][d][g]['sup_cover'] for d in DES]
            ax.plot(x + JIT[s], v, '-o', color=col, ms=4, lw=1.3)
        ax.axhline(0.9, color=INK, lw=0.8, ls='--')
        ax.set_xticks(x); ax.set_xticklabels([str(n) for n in NLOG])
        ax.set_ylim(-0.03, 1.03); ax.set_title(ttl); GF.style(ax, grid='y')
        ax.set_xlabel('loggers')
    axs[0].set_ylabel('whole-function coverage (target 0.90)')
    handles = [Line2D([], [], color=c, marker='o', ms=4, lw=1.3, label=l) for _, c, l in SET]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.84), w_pad=0.8)
    fig.savefig(os.path.join(out, 'fig_cover.png'), dpi=300)
    plt.close(fig)


def fig_floor(out, R):
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 70 * MM))
    x = np.arange(len(DES))
    ax = axs[0]
    for s, col, _ in SET:
        if s == 'naive':
            continue
        ax.plot(x, [R['res'][s][d]['kappa']['halfwidth'] for d in DES], '-o', color=col, ms=4, lw=1.3)
    ax.plot(x, [R['res']['aware_r2'][d]['kappa_eff']['halfwidth'] for d in DES], '--o', color=VIOLET, ms=4, lw=1.1,
            mfc='white')
    ax.axhline(R['floor']['halfwidth'], color=INK, lw=1.0, ls=':')
    ax.text(2.0, R['floor']['halfwidth'] * 0.94, 'floor of Proposition R1', ha='left', va='top', color=INK)
    ax.set_yscale('log'); ax.set_ylim(0.018, 0.25); logticks(ax, [0.02, 0.03, 0.05, 0.1, 0.2])
    ax.set_title('coefficient $\\kappa$: guaranteed half-width')
    ax = axs[1]
    for s, col, _ in SET:
        if s == 'naive':
            continue
        ax.plot(x, [R['res'][s][d]['r']['halfwidth'] for d in DES], '-o', color=col, ms=4, lw=1.3)
    ax.set_yscale('log'); logticks(ax, [0.05, 0.1, 0.2, 0.5, 1.0])
    ax.set_title('recharge $r$ (mm/d): guaranteed half-width')
    for ax in axs:
        ax.set_xticks(x); ax.set_xticklabels([str(n) for n in NLOG]); ax.set_xlabel('loggers')
        GF.style(ax, grid='both')
    handles = [Line2D([], [], color=c, marker='o', ms=4, lw=1.3, label=l) for s, c, l in SET if s != 'naive'] + \
              [Line2D([], [], color=VIOLET, ls='--', marker='o', mfc='white', ms=4, lw=1.1,
                      label='product: $c=\\kappa b$ (heads see it)')]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.84), w_pad=1.5)
    fig.savefig(os.path.join(out, 'fig_floor.png'), dpi=300)
    plt.close(fig)


def fig_filter(out, R):
    F = R['filter']
    meas, pred = np.array(F['measured']), np.array(F['predicted'])
    neff = 1.0 / np.array(F['kernel_ratio'])
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 68 * MM))
    ax = axs[0]
    ax.plot(pred, meas, 'o', color=BLUE, ms=3, alpha=0.6, mec='none')
    lo, hi = min(pred.min(), meas.min()) * 0.8, max(pred.max(), meas.max()) * 1.2
    ax.plot([lo, hi], [lo, hi], color=INK, lw=0.9)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    logticks(ax, [0.04, 0.06, 0.1, 0.15])
    from matplotlib.ticker import FixedLocator, NullLocator, FuncFormatter
    ax.xaxis.set_major_locator(FixedLocator([0.04, 0.06, 0.1, 0.15])); ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'))
    ax.set_xlabel('predicted, $v/n_{eff}$'); ax.set_ylabel('measured relative variance')
    ax.set_title('weekly filtered product error')
    ax.text(0.04, 0.96, f'daily relative variance $v$ = {F["daily_rel_var"]:.2f}', transform=ax.transAxes, va='top',
            color=MUTED)
    ax = axs[1]
    ax.hist(neff, bins=30, color=BLUE, alpha=0.85)
    ax.axvline(np.mean(neff), color=INK, lw=1.0)
    ax.text(np.mean(neff) * 1.04, ax.get_ylim()[1] * 0.92, f'mean {np.mean(neff):.1f}', color=INK, va='top')
    ax.set_xlabel('effective rain days $n_{eff}$ per record')
    ax.set_title(f'steady rain would give $4\\tau+1$ = {F["four_tau"] + 1:.0f}')
    for ax in axs:
        GF.style(ax, grid='both')
    fig.tight_layout(w_pad=1.5)
    fig.savefig(os.path.join(out, 'fig_filter.png'), dpi=300)
    plt.close(fig)


def main(out, cards=None):
    os.makedirs(out, exist_ok=True)
    R = load()
    fig_scheme(out, R)
    fig_cover(out, R)
    fig_floor(out, R)
    fig_filter(out, R)
    if cards is not None:
        GF.fig_map(out, cards)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, 'figs'))
