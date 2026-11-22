"""Figures of the SHTEGU-GO review (English labels; every text at least 8.6 pt at the printed size, 17 cm wide).
usage: python shtegu_figs.py OUT_DIR

fig_scheme   (a) the analogy between robust pricing and warnings between samples; (b) one season: samples, the path
             between them and the online forecast that jumps at each sample and decays between (the jump-ODE structure)
fig_t37      the exceedance probability against the time scale (Proposition S1) and the information per pair of samples
             against the lag (Proposition S2), with the band each design leaves
fig_t38      the robust band over the two-component family for each design (T38)
fig_t39      coverage of the raw and of the certified band (T39)
fig_t40      online warnings: skill and reliability of three forecasters (T40)
Numbers come from res/shtegu.json."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', 'rindertimi_go'))
import gar_figs as GF  # noqa: E402
from rgo_figs import Canvas, INK, MUTED  # noqa: E402

RES = os.path.join(HERE, 'res')
MM = GF.MM
FS = GF.FS
BLUE, ORANGE, AQUA, VIOLET, REF = GF.BLUE, GF.ORANGE, GF.AQUA, GF.VIOLET, GF.REF
DCOL = {'quarterly samples': '#8a9099', 'monthly samples': '#7aa7d8', 'weekly samples': '#2f5f99',
        'daily logger': ORANGE}


def load():
    with open(os.path.join(RES, 'shtegu.json')) as fh:
        return json.load(fh)


def style(ax, grid='y'):
    GF.style(ax, grid)
    ax.tick_params(labelsize=FS)


def fig_scheme(out, R):
    fig = plt.figure(figsize=(170 * MM, 100 * MM))
    # (a) the analogy
    cv_ax = fig.add_axes([0.0, 0.0, 0.44, 1.0]); cv_ax.axis('off'); cv_ax.set_xlim(0, 1); cv_ax.set_ylim(0, 1)
    cv_ax.text(0.02, 0.96, '(a) Robust pricing and warnings', fontsize=9.4, weight='bold', va='top')
    rows = [('liquid option\nprices', 'chloride statistics\nat sampling dates'),
            ('illiquid lookback\noption', 'crossing the limit\nbetween samples'),
            ('neural SDEs fitted\nto the market', 'models consistent\nwith the records'),
            ('robust price\ninterval', 'band of the\nwarning probability'),
            ('irregular order-\nbook updates', 'irregular samples,\nlogger gaps')]
    cv_ax.text(0.24, 0.86, 'finance', fontsize=FS, ha='center', color=MUTED)
    cv_ax.text(0.74, 0.86, 'coastal aquifer', fontsize=FS, ha='center', color=MUTED)
    for k, (a, b) in enumerate(rows):
        y = 0.75 - k * 0.155
        for x, txt, ec, fc in ((0.24, a, '#5b6672', '#eef0f2'), (0.74, b, BLUE, '#e3eefb')):
            cv_ax.add_patch(plt.Rectangle((x - 0.22, y - 0.06), 0.44, 0.12, fc=fc, ec=ec, lw=0.8))
            cv_ax.text(x, y, txt, ha='center', va='center', fontsize=FS, linespacing=1.1)
        cv_ax.annotate('', xy=(0.515, y), xytext=(0.465, y), arrowprops=dict(arrowstyle='-|>', color=INK, lw=0.8))
    # (b) one season
    ax = fig.add_axes([0.53, 0.33, 0.45, 0.57])
    k = R['setup']['kappa_true']
    dt = 0.25
    n = int(120 / dt)
    mu, sd, L = R['setup']['mu'], R['setup']['sd'], R['setup']['limit']
    ts = np.array([0.0, 30.0, 61.0, 91.0])
    r = np.exp(-k * dt)
    for seed in range(1000):                      # a season that crosses the limit between samples, never at one
        rng = np.random.default_rng(seed)
        x = np.empty(n + 1); x[0] = rng.standard_normal()
        for i in range(n):
            x[i + 1] = r * x[i] + np.sqrt(1 - r ** 2) * rng.standard_normal()
        c = mu + sd * x
        cs = c[(ts / dt).astype(int)]
        if c.max() > L + 8 and cs.max() < L - 30:
            break
    t = np.arange(n + 1) * dt
    # online forecast: conditional mean jumps at each sample, decays to the mean between samples
    last = np.searchsorted(ts, t, side='right') - 1
    cm = mu + (cs[last] - mu) * np.exp(-k * (t - ts[last]))
    ax.plot(t, c, color='#9aa3ad', lw=0.8, label='chloride between samples')
    ax.plot(t, cm, color=BLUE, lw=1.4, label='online forecast (jumps, then decays)')
    ax.plot(ts, cs, 'o', color=INK, ms=4.5, label='monthly samples')
    ax.axhline(L, color=ORANGE, ls='--', lw=1.0)
    ax.text(1, L + 3, f'limit {L:.0f} mg/L', ha='left', va='bottom', fontsize=FS, color=ORANGE)
    ax.set_ylim(mu - 3.3 * sd, L + 40)
    above = c >= L
    if above.any():
        ax.fill_between(t, L, c, where=above, color=ORANGE, alpha=0.35, lw=0)
    ax.set_xlabel('day of the season', fontsize=FS)
    ax.set_ylabel('chloride (mg/L)', fontsize=FS)
    ax.set_title('(b) what happens between samples', fontsize=9.4, loc='left', weight='bold')
    ax.legend(fontsize=FS - 1, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=1)
    style(ax)
    fig.savefig(os.path.join(out, 'fig_scheme.png'), dpi=300)
    plt.close(fig)


def fig_t37(out, R):
    T = R['t37']
    kg = np.array(T['kgrid'])
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 82 * MM))
    ax = axs[0]
    ax.semilogx(1 / kg, T['curve'], color=INK, lw=1.4, label='P(crossing in the season)')
    ax.axhline(T['p_marginal'], color=MUTED, ls=':', lw=1.2, label='marginal tail')
    kt = R['setup']['kappa_true']
    ax.plot([1 / kt], [T['p_true']], 'o', color=ORANGE, ms=6, zorder=5, label='true 1/κ = 8 days')
    y0 = 1.06
    for j, (name, d) in enumerate(T['designs'].items()):
        y = y0 + 0.07 * j
        ax.plot([1 / d['khi_med'], 1 / d['klo_med']], [y, y], color=DCOL[name], lw=4, solid_capstyle='butt')
        ax.text(1 / d['klo_med'] * 1.15 if d['klo_med'] > kg[0] * 1.01 else 420, y, name, fontsize=FS - 0.8,
                va='center', color=DCOL[name])
    ax.set_xlabel('correlation time 1/κ (days)', fontsize=FS)
    ax.set_ylabel('probability', fontsize=FS)
    ax.set_ylim(0, y0 + 0.07 * len(T['designs']) + 0.02)
    ax.set_xlim(0.2, 2000)
    ax.set_title('(a) marginals do not bound the crossing (S1)', fontsize=FS, loc='left')
    # direct labels instead of a legend
    ax.text(60, 0.45, 'P(crossing\nin the season)', fontsize=FS - 1, color=INK, va='center')
    ax.text(0.25, 0.065, f"marginal tail {T['p_marginal']:.3f}", fontsize=FS - 1, color=MUTED, va='center')
    ax.annotate(f"true 1/κ = 8 days\nP = {T['p_true']:.2f}", (1 / kt, T['p_true']), xytext=(-8, 0),
                textcoords='offset points', ha='right', va='center', fontsize=FS - 1, color=ORANGE)
    style(ax)
    ax = axs[1]
    ax.plot(T['fisher_tau'], T['fisher'], color=INK, lw=1.4)
    # label positions in data coordinates, in the empty space around the curve
    pos = {'daily logger': (0.3, 2e-3, 'left'), 'weekly samples': (10, 0.9, 'left'),
           'monthly samples': (3.5, 2e-5, 'left'), 'quarterly samples': (3.5, 3e-8, 'left')}
    for name, d in T['designs'].items():
        f = np.interp(d['step'], T['fisher_tau'], T['fisher'])
        ax.plot([d['step']], [f], 'o', color=DCOL[name], ms=6, zorder=5)
        x_, y_, ha = pos[name]
        se = d['crb_rel_se']
        se_txt = f'{se:.0f}' if se >= 100 else f'{se:.2g}'
        ax.annotate(f"{name}\nrel. s.e. {se_txt}", (d['step'], f), xytext=(x_, y_),
                    textcoords='data', fontsize=FS - 1, color=DCOL[name], ha=ha, va='center',
                    arrowprops=dict(arrowstyle='-', color=DCOL[name], lw=0.6, shrinkA=2, shrinkB=4))
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.2, 200)
    ax.set_ylim(1e-9, 20)
    ax.set_xlabel('lag between two samples τ (days)', fontsize=FS)
    ax.set_ylabel('information on κ per pair (× κ²)', fontsize=FS)
    ax.set_title('(b) information decays with the lag (S2)', fontsize=FS, loc='left')
    style(ax)
    fig.tight_layout(w_pad=1.6)
    fig.savefig(os.path.join(out, 'fig_t37.png'), dpi=300)
    plt.close(fig)


def fig_t38(out, R):
    T = R['t38']
    names = ['marginals only'] + list(T['designs'])
    lo = [T['marginals_only']['lo']] + [T['designs'][n]['lo'] for n in T['designs']]
    hi = [T['marginals_only']['hi']] + [T['designs'][n]['hi'] for n in T['designs']]
    fig, ax = plt.subplots(figsize=(170 * MM, 62 * MM))
    for i, (n, a, b) in enumerate(zip(names, lo, hi)):
        ax.plot([a, b], [i, i], color=DCOL.get(n, '#c9ced6'), lw=9, solid_capstyle='butt')
        ax.text(b + 0.01, i, f'{a:.2f}–{b:.2f}', va='center', fontsize=FS)
    ax.axvline(T['p_true'], color=INK, ls='--', lw=1.0)
    ax.text(T['p_true'] + 0.008, len(names) - 0.45, f"true {T['p_true']:.2f}", ha='left', fontsize=FS)
    ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=FS)
    ax.set_xlim(0, 1.12); ax.set_ylim(-0.6, len(names) - 0.1)
    ax.set_xlabel('probability of crossing the limit in the season, over all consistent models', fontsize=FS)
    ax.invert_yaxis()
    style(ax, grid='x')
    fig.tight_layout()
    fig.savefig(os.path.join(out, 'fig_t38.png'), dpi=300)
    plt.close(fig)


def fig_t39(out, R):
    T = R['t39']
    names = list(T)
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 82 * MM), gridspec_kw=dict(width_ratios=[1, 1.15]))
    ax = axs[0]
    x = np.arange(len(names))
    ax.bar(x - 0.2, [100 * T[n]['raw_all'] for n in names], 0.4, color='#c9ced6', label='band of the family')
    cm = np.array([100 * T[n]['cert_split_mean'] for n in names])
    err = np.array([[cm[i] - 100 * T[n]['cert_split_p10'], 100 * T[n]['cert_split_p90'] - cm[i]]
                    for i, n in enumerate(names)]).T
    ax.bar(x + 0.2, cm, 0.4, color=ORANGE, label='certified band (mean of 50 splits)')
    ax.errorbar(x + 0.2, cm, yerr=err, fmt='none', ecolor=INK, elinewidth=0.9, capsize=2.5)
    ax.axhline(100 * (1 - T[names[0]]['alpha']), color=INK, ls='--', lw=0.9)
    ax.set_xticks(x); ax.set_xticklabels([n.replace(' ', '\n') for n in names], fontsize=FS)
    ax.set_ylim(0, 105); ax.set_ylabel('coverage of the true probability (%)', fontsize=FS)
    ax.set_title('(a) coverage on new aquifers', fontsize=FS, loc='left')
    ax.legend(fontsize=FS - 1, frameon=False, loc='lower left')
    style(ax)
    ax = axs[1]
    n = names[-1]
    pts = np.array(T[n]['pts'])
    o = np.argsort(pts[:, 0])
    pts = pts[o]
    d = T[n]['delta']
    xx = np.arange(len(pts))
    ax.vlines(xx, np.maximum(pts[:, 1] - d, 0), np.minimum(pts[:, 2] + d, 1), color=ORANGE, lw=1.4, alpha=0.6,
              label='certified band')
    ax.vlines(xx, pts[:, 1], pts[:, 2], color='#5b6672', lw=1.4, label='band of the family')
    inside = (pts[:, 1] <= pts[:, 0]) & (pts[:, 0] <= pts[:, 2])
    ax.plot(xx[inside], pts[inside, 0], 'o', ms=2.6, color=BLUE, label='true, inside')
    ax.plot(xx[~inside], pts[~inside, 0], 'x', ms=3.4, color='#c4563a', label='true, outside the raw band')
    ax.set_xlabel('test aquifers (sorted by the true probability)', fontsize=FS, labelpad=2)
    ax.set_ylabel('probability', fontsize=FS)
    ax.set_title(f'(b) {n}, first split: margin δ = {d:.3f}', fontsize=FS, loc='left')
    ax.legend(fontsize=FS - 1.2, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
    style(ax)
    fig.tight_layout(w_pad=1.4)
    fig.savefig(os.path.join(out, 'fig_t39.png'), dpi=300)
    plt.close(fig)


def fig_t40(out, R):
    T = R['t40']
    names = [n for n in T if n not in ('climatology', 'N')]
    col = ['#8a9099', '#7aa7d8', ORANGE]
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 70 * MM))
    ax = axs[0]
    ax.barh(range(len(names)), [100 * T[n]['skill'] for n in names], color=col)
    for i, n in enumerate(names):
        ax.text(100 * T[n]['skill'] + 0.4, i, f"{100 * T[n]['skill']:.1f}%", va='center', fontsize=FS)
    ax.set_yticks(range(len(names))); ax.set_yticklabels([n.replace(' (', '\n(').replace(' + ', '\n+ ') for n in names],
                                                         fontsize=FS)
    ax.invert_yaxis()
    ax.set_xlabel('Brier skill over climatology (%)', fontsize=FS)
    ax.set_xlim(0, max(100 * T[n]['skill'] for n in names) * 1.3)
    ax.set_title('(a) skill of the online warning', fontsize=FS, loc='left')
    style(ax, grid='x')
    ax = axs[1]
    ax.plot([0, 1], [0, 1], color=MUTED, ls=':', lw=1.0)
    for n, c_ in zip(names, col):
        rel = np.array(T[n]['reliability'])
        ax.plot(rel[:, 0], rel[:, 1], '-o', ms=3.5, color=c_, label=n)
    ax.set_xlabel('forecast probability (decile mean)', fontsize=FS)
    ax.set_ylabel('observed frequency', fontsize=FS)
    ax.set_title('(b) reliability', fontsize=FS, loc='left')
    ax.legend(fontsize=FS - 1.2, frameon=False, loc='lower right')
    style(ax)
    fig.tight_layout(w_pad=1.4)
    fig.savefig(os.path.join(out, 'fig_t40.png'), dpi=300)
    plt.close(fig)


def main(out):
    os.makedirs(out, exist_ok=True)
    R = load()
    fig_scheme(out, R)
    fig_t37(out, R)
    fig_t38(out, R)
    fig_t39(out, R)
    fig_t40(out, R)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, 'figs'))
