"""Figures of the DYSHEMEJA-GO review (English labels; every text at least 8.6 pt at the printed size, 17 cm wide).
usage: python dyshemeja_figs.py OUT_DIR

fig_scheme   two weeks of one field case: the exact posterior densities, the one threshold of the floor and its sets,
             and the central 90% intervals
fig_ladder   half-width of every band divided by the floor, for the four goals, without shift (T18)
fig_shift    the same under the two shifts: simulation-calibrated (invalid) and anchor-calibrated bands (T19)
fig_design   the floor for six designs, relative to rain only, and the anchor band divided by the floor (T20)
fig_map      the twenty papers of this review against the steps and the unknowns they inform
Numbers come from res/dyshemeja.json (the scheme recomputes one posterior with the same code)."""
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
from rgo_figs import INK, MUTED  # noqa: E402

RES = os.path.join(HERE, 'res')
MM = GF.MM
BLUE, ORANGE, AQUA, VIOLET, REF = GF.BLUE, GF.ORANGE, GF.AQUA, GF.VIOLET, GF.REF
GOALS = (('r', 'recharge $r$'), ('qL', 'inflow $q_L$'), ('eta', 'sea level $\\eta$'), ('kappa', 'coefficient $\\kappa$'))
LADDER = (('central', 'central 90% posterior', '#9aa5b1'), ('exact_z', 'exact posterior, λ known', AQUA),
          ('exactT_star', 'enlarged law, λ known', AQUA), ('ens_star', 'ensemble, λ known', VIOLET),
          ('sims', 'ensemble, 300 sims', REF), ('m40', 'ensemble, 40 anchors', BLUE),
          ('m20', 'ensemble, 20 anchors', BLUE), ('m10', 'ensemble, 10 anchors', BLUE),
          ('exactT_m20', 'enlarged law, 20 anchors', ORANGE))
SHIFT = (('sims', 'ensemble, simulations', REF, 'o'), ('m20', 'ensemble, 20 anchors', BLUE, 's'),
         ('exactP_m20', 'exact under P, 20 anchors', VIOLET, 'D'),
         ('exactT_sims', 'enlarged law, simulations', AQUA, '^'),
         ('exactT_m20', 'enlarged law, 20 anchors', ORANGE, 'v'))


def load():
    with open(os.path.join(RES, 'dyshemeja.json')) as fh:
        return json.load(fh)


def fig_scheme(out, D):
    import dyshemeja_exp as DX
    bed = DX.AX.QBed()
    rng = np.random.default_rng(11)
    cs = bed.case_q(rng, 'none')
    rows = bed.rows(DX.DESIGN4)
    y = bed.data(cs, rows)
    post = DX.exact_post(y, rows, cs['f'], bed.G, bed.cQ, bed.mu, bed.Sig, DX.M.KAP_MED)
    m, s, w = DX.marginals(post, cs['f'])['r']
    mu = m @ w
    sd = np.sqrt(s ** 2 + (m ** 2) @ w - mu ** 2)
    tau = D['laws']['none']['r']['floor']['tau']
    t_lo, t_hi = int(np.argmin(sd)), int(np.argmax(sd))
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 64 * MM), sharey=True)
    for ax, t, ttl in ((axs[0], t_lo, 'well-observed week'), (axs[1], t_hi, 'poorly observed week')):
        x = np.linspace(mu[t] - 5 * sd[t], mu[t] + 5 * sd[t], 1200)
        p = (np.exp(-0.5 * ((x[:, None] - m[t][None, :]) / s[t]) ** 2) / (np.sqrt(2 * np.pi) * s[t])) @ w
        ax.plot(x, p, color=INK, lw=1.4)
        ax.fill_between(x, 0, p, where=p >= tau, color=BLUE, alpha=0.25, lw=0)
        ax.axhline(tau, color=ORANGE, lw=1.1, ls='--')
        cdf = np.cumsum(p) * (x[1] - x[0])
        lo, hi = x[np.searchsorted(cdf, 0.05)], x[np.searchsorted(cdf, 0.95)]
        yb = -0.06 * p.max()
        ax.plot([lo, hi], [yb, yb], color='#6b7682', lw=3.2, solid_capstyle='butt')
        sel = x[p >= tau]
        if sel.size:
            ax.plot([sel.min(), sel.max()], [2 * yb, 2 * yb], color=BLUE, lw=3.2, solid_capstyle='butt')
        mass = float(np.sum(p[p >= tau]) * (x[1] - x[0]))
        ax.set_title(f'{ttl} (sd {sd[t]:.3f} mm/d)')
        ax.text(0.02, 0.62, f'floor set:\n{100 * mass:.0f}% of the mass', transform=ax.transAxes, va='top',
                color=BLUE)
        ax.set_xlabel('recharge $r$ in that week (mm/d)')
        GF.style(ax, grid='y')
    axs[0].set_ylabel('exact posterior density')
    handles = [Line2D([], [], color=ORANGE, ls='--', lw=1.1, label='one threshold τ* for all weeks'),
               Line2D([], [], color=BLUE, lw=3.2, label='floor set {p ≥ τ*}'),
               Line2D([], [], color='#6b7682', lw=3.2, label='central 90% interval')]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.9), w_pad=1.2)
    fig.savefig(os.path.join(out, 'fig_scheme.png'), dpi=300)
    plt.close(fig)


def fig_ladder(out, D):
    R = D['laws']['none']
    fig, axs = plt.subplots(1, 4, figsize=(170 * MM, 74 * MM), sharey=True)
    yk = np.arange(len(LADDER))[::-1]
    for ax, (g, ttl) in zip(axs, GOALS):
        fl = R[g]['floor']['halfwidth']
        for yy, (key, lab, col) in zip(yk, LADDER):
            v = R[g][key]['halfwidth'] / fl
            ax.barh(yy, v - 1, left=1, color=col, height=0.62)
            ax.text(v + 0.03, yy, f'{v:.2f}', va='center', color=INK)
        ax.axvline(1, color=ORANGE, lw=1.2)
        ax.set_xlim(0.9, 1.0 + 1.25 * max(R[g][k]['halfwidth'] / fl - 1 for k, _, _ in LADDER) + 0.25)
        ax.set_title(ttl); GF.style(ax, grid=None)
        ax.set_xlabel('half-width ÷ floor')
    axs[0].set_yticks(yk); axs[0].set_yticklabels([lab for _, lab, _ in LADDER])
    fig.tight_layout(w_pad=0.8)
    fig.savefig(os.path.join(out, 'fig_ladder.png'), dpi=300)
    plt.close(fig)


def fig_shift(out, D):
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 76 * MM), sharey=True)
    x = np.arange(len(GOALS))
    off = np.linspace(-0.3, 0.3, len(SHIFT))
    for ax, scen, ttl in ((axs[0], 'delay', 'vadose delay 35 d in the field'),
                          (axs[1], 'params', 'shifted parameters')):
        R = D['laws'][scen]
        for g_i, (g, _) in enumerate(GOALS):
            fl = R[g]['floor']['halfwidth']
            for o_, (key, lab, col, mk) in zip(off, SHIFT):
                v = R[g][key]
                rk = v.get('risk_rb', v.get('risk'))
                ax.plot(g_i + o_, v['halfwidth'] / fl, mk, color=col, ms=6.2 if rk <= 0.105 else 6.2,
                        mfc=col if rk <= 0.105 else 'white', mew=1.4)
        ax.axhline(1, color=INK, lw=1.0, ls='--')
        ax.set_yscale('log')
        from matplotlib.ticker import FixedLocator, NullLocator, FuncFormatter
        ax.yaxis.set_major_locator(FixedLocator([1, 1.5, 2, 3, 4, 6])); ax.yaxis.set_minor_locator(NullLocator())
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'))
        ax.set_xticks(x); ax.set_xticklabels(['recharge\n$r$', 'inflow\n$q_L$', 'sea level\n$\\eta$',
                                              'coefficient\n$\\kappa$'])
        ax.set_xlim(-0.6, len(GOALS) - 0.4)
        ax.set_title(ttl); GF.style(ax, grid='y')
    axs[0].set_ylabel('half-width ÷ floor under the real law')
    handles = [Line2D([], [], color=col, marker=mk, ls='', ms=6, label=lab) for _, lab, col, mk in SHIFT] + \
              [Line2D([], [], color=INK, marker='o', ls='', ms=6, mfc='white', label='open: risk above 0.10')]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.82), w_pad=1.0)
    fig.savefig(os.path.join(out, 'fig_shift.png'), dpi=300)
    plt.close(fig)


def fig_design(out, D):
    names = list(D['designs'].keys())
    short = ['rain\nonly', '1\nlogger', '2\nloggers', '4\nloggers', '8\nloggers', '4 +\ngauge']
    cols = dict(r=ORANGE, qL=AQUA, eta=BLUE, kappa=VIOLET)
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 70 * MM))
    x = np.arange(len(names))
    for g, ttl in GOALS:
        base = D['designs'][names[0]][g]['floor']['halfwidth']
        fl = [D['designs'][n][g]['floor']['halfwidth'] / base for n in names]
        ra = [D['designs'][n][g]['m20']['halfwidth'] / D['designs'][n][g]['floor']['halfwidth'] for n in names]
        rt = [D['designs'][n][g]['exactT_m20']['halfwidth'] / D['designs'][n][g]['floor']['halfwidth'] for n in names]
        axs[0].plot(x, fl, '-o', color=cols[g], ms=4.5, lw=1.4, label=ttl)
        axs[1].plot(x, ra, '-o', color=cols[g], ms=4.5, lw=1.4)
        axs[1].plot(x, rt, ':', color=cols[g], marker='v', ms=4.0, lw=1.2)
    axs[0].set_ylabel('floor ÷ floor with rain only'); axs[0].set_ylim(0, 1.08)
    axs[1].set_ylabel('20-anchor band ÷ floor'); axs[1].axhline(1, color=INK, lw=0.8, ls='--')
    axs[0].set_title('what the data can buy at best'); axs[1].set_title('anchor band ÷ floor (dotted: enlarged law)')
    for ax in axs:
        ax.set_xticks(x); ax.set_xticklabels(short); GF.style(ax, grid='y')
    fig.legend(*axs[0].get_legend_handles_labels(), loc='upper center', ncol=4, frameon=False,
               bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.9), w_pad=2.0)
    fig.savefig(os.path.join(out, 'fig_design.png'), dpi=300)
    plt.close(fig)


def main(out, cards=None):
    os.makedirs(out, exist_ok=True)
    D = load()
    fig_scheme(out, D)
    fig_ladder(out, D)
    fig_shift(out, D)
    fig_design(out, D)
    if cards is not None:
        GF.fig_map(out, cards)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, 'figs'))
