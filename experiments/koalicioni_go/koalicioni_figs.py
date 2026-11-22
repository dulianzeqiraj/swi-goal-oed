"""Figure K1 of review 56 (KOALICIONI-GO), from res/koalicioni_summary_drift.json (physics-informed model) and
res/koalicioni_summary_local.json (local statistical model):
(a) value of each holder alone, predicted and realised, and its Shapley share per record;
(b) pairwise synergy V(ij) - V(i) - V(j), predicted and realised, for the pairs with a one-regime holder;
(c) net benefit of the merge policies against the cost of one merge;
(d) privacy: one release per holder; how often the private optimal coalition equals the non-private one.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
INK, INK2, GRID = '#0b0b0b', '#52514e', '#d9d8d4'
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4'
SHORT = ['agency', 'irrigators', 'hotels\n(all high)', 'municipal\n(all low)', 'research']


def style(ax):
    ax.tick_params(colors=INK2, labelsize=7.5)
    for s_ in ax.spines.values():
        s_.set_color(GRID)


def main():
    P = json.load(open(os.path.join(HERE, 'res', 'koalicioni_summary_drift.json')))
    L = json.load(open(os.path.join(HERE, 'res', 'koalicioni_summary_local.json')))
    fig = plt.figure(figsize=(12.0, 9.2))
    gs = fig.add_gridspec(2, 2, hspace=0.55, wspace=0.40)
    # ------------------------------------------------------------ (a) holders alone
    a = fig.add_subplot(gs[0, 0]); x = np.arange(5)
    for off, S, col, lab in ((-0.2, P, BLUE, 'physics-informed'), (0.2, L, ORANGE, 'local statistical')):
        v = [s['V'][0] for s in S['singles']]; r = [s['R'][0] for s in S['singles']]; re = [s['R'][1] for s in S['singles']]
        a.bar(x + off, v, width=0.36, color=col, alpha=0.35, edgecolor=col, lw=1.0, label=f'{lab}: predicted value')
        a.errorbar(x + off, r, yerr=re, fmt='o', ms=5, color=col, mec=INK, mew=0.5, capsize=3, lw=1.1, label=f'{lab}: realised gain (95% CI)')
    a.axhline(0, color=INK2, lw=0.9); a.set_ylim(top=0.37)
    a.set_xticks(x); a.set_xticklabels(SHORT, fontsize=7.5)
    a.set_ylabel('value of merging this holder alone (loss units)', color=INK2, fontsize=8.5)
    a.legend(loc='upper right', fontsize=6.8, frameon=False)
    a.set_title('(a) Each holder alone: one regime is not enough', fontsize=9.5, color=INK, loc='left')
    a.grid(axis='y', color=GRID, lw=0.6); style(a)
    # ------------------------------------------------------------ (b) pair synergies
    b = fig.add_subplot(gs[0, 1])
    keys = list(P['pairs'].keys())
    y = np.arange(len(keys))
    for off, S, col, lab in ((-0.18, P, BLUE, 'physics-informed'), (0.18, L, ORANGE, 'local statistical')):
        pr = [S['pairs'][k]['pred'][0] for k in keys]; re = [S['pairs'][k]['real'][0] for k in keys]; ree = [S['pairs'][k]['real'][1] for k in keys]
        b.errorbar(re, y + off, xerr=ree, fmt='o', ms=5, color=col, mec=INK, mew=0.5, capsize=2.5, lw=1.0, label=f'{lab}: realised')
        b.scatter(pr, y + off, marker='|', s=160, color=col, lw=2.2, zorder=5, label=f'{lab}: predicted')
    b.axvline(0, color=INK2, lw=0.9)
    b.set_yticks(y); b.set_yticklabels([k.replace('+', ' + ') for k in keys], fontsize=7.2); b.invert_yaxis()
    b.set_xlabel('synergy  V(i and j) − V(i) − V(j)   (< 0: substitutes, > 0: complements)', color=INK2, fontsize=8)
    b.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=2, fontsize=6.8, frameon=False)
    b.set_title('(b) Pairs of holders: substitutes or complements?', fontsize=9.5, color=INK, loc='left')
    b.grid(axis='x', color=GRID, lw=0.6); style(b)
    # ------------------------------------------------------------ (c) policies
    c = fig.add_subplot(gs[1, 0])
    costs = P['costs']
    pols = (('adaptive', 'adaptive (merge, update, re-value)', ORANGE, 'o'), ('optimal', 'optimal fixed coalition', BLUE, 's'),
            ('greedy', 'greedy', AQUA, 'D'), ('single', 'best single holder (review 55)', MAGENTA, '^'), ('all', 'all holders', INK2, 'x'))
    for S, ls in ((P, '-'), (L, '--')):
        for k, lab, col, mk in pols:
            c.plot(costs, [S['policies'][str(cc)][k][0] for cc in costs], ls=ls, color=col, marker=mk, ms=5, lw=1.5)
    c.axhline(0, color=INK2, lw=0.9)
    h1 = [Line2D([], [], color=col, marker=mk, lw=1.5, label=lab) for _, lab, col, mk in pols]
    h2 = [Line2D([], [], color=INK2, ls='-', lw=1.5, label='physics-informed model'), Line2D([], [], color=INK2, ls='--', lw=1.5, label='local statistical model')]
    l1 = c.legend(handles=h1, loc='lower left', fontsize=6.8, frameon=True, framealpha=0.9, edgecolor=GRID); c.add_artist(l1)
    c.legend(handles=h2, loc='upper right', fontsize=6.8, frameon=False)
    c.set_xlabel('cost of one merge (loss units)', color=INK2, fontsize=8.5)
    c.set_ylabel('net benefit: realised gain − cost (mean over aquifers)', color=INK2, fontsize=8.5)
    c.set_title('(c) Which coalition, in what order', fontsize=9.5, color=INK, loc='left')
    c.grid(color=GRID, lw=0.6); style(c)
    # ------------------------------------------------------------ (d) privacy
    d = fig.add_subplot(gs[1, 1])
    eps = [float(e) for e in P['privacy'].keys()]
    for S, ls in ((P, '-'), (L, '--')):
        for cc, col, mk in ((0.01, BLUE, 's'), (0.02, ORANGE, 'o')):
            d.plot(eps, [S['privacy'][e][str(cc)]['same'] for e in S['privacy']], ls=ls, color=col, marker=mk, ms=5, lw=1.5)
        d.plot(eps, [S['privacy'][e]['shapley_tau'][0] for e in S['privacy']], ls=ls, color=AQUA, marker='D', ms=5, lw=1.5)
    d.set_xscale('log'); d.set_xticks(eps); d.set_xticklabels([str(e) for e in eps]); d.set_ylim(0, 1.05)
    h1 = [Line2D([], [], color=BLUE, marker='s', lw=1.5, label='same optimal coalition, merge cost 0.01'),
          Line2D([], [], color=ORANGE, marker='o', lw=1.5, label='same optimal coalition, merge cost 0.02'),
          Line2D([], [], color=AQUA, marker='D', lw=1.5, label='Kendall τ of the Shapley ranking')]
    l1 = d.legend(handles=h1, loc='lower right', fontsize=6.8, frameon=True, framealpha=0.9, edgecolor=GRID); d.add_artist(l1)
    d.legend(handles=h2, loc='upper left', fontsize=6.8, frameon=False)
    d.set_xlabel(r'privacy budget $\varepsilon$ per holder ($\delta=10^{-6}$), one release per holder', color=INK2, fontsize=8)
    d.set_ylabel('agreement with the non-private analysis', color=INK2, fontsize=8.5)
    d.set_title('(d) All 31 coalitions from one private release per holder', fontsize=9.5, color=INK, loc='left')
    d.grid(color=GRID, lw=0.6); style(d)
    out = os.path.join(HERE, 'res', 'figK1_koalicioni.png'); fig.savefig(out, dpi=200, bbox_inches='tight'); print('wrote', out)


if __name__ == '__main__':
    main()
