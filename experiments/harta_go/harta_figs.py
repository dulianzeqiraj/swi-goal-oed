"""HARTA-GO figures. Run after harta_static.py and harta_seq.py:  python3 harta_figs.py [outdir]
figH1_static.png  share of the optimum, of the constrained optimum and rank correlation against the
                  number of model runs, for the 5-well designs of each goal
figH2_seq.png     information about the goal gained by sequential policies, relative to the best fixed
                  3-well design, with the number of different well sets each policy used
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
S = json.load(open('harta_static.json'))
NS = [250, 500, 1000, 2000, 4000]
GOALS = ['rA', 'rAB', 'rArea']
GLAB = {'rA': r'$r_A$: supply well A reached', 'rAB': r'$r_{AB}$: A or B reached', 'rArea': r'$r_{\mathrm{Area}}$: area above median'}
MCOL = {'rew': '#6B7280', 'gauss': '#2563EB', 'ns': '#D97706', 'harta': '#059669'}
MLAB = {'rew': 'nested Monte Carlo', 'gauss': 'map: Gaussian (ensemble Kalman)', 'ns': 'map: Gaussian copula', 'harta': 'map: HARTA (nonlinear)'}
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False})

# ---------------------------------------------------------------- figure 1: static designs, 5 wells
fig, ax = plt.subplots(2, 3, figsize=(10.2, 5.6), sharex=True)
for j, goal in enumerate(GOALS):
    for meth in ('rew', 'gauss', 'ns', 'harta'):
        v = [S[f'5|{goal}|{meth}|{N}'] for N in NS]
        ax[0, j].plot(NS, [x['cons'] for x in v], '-o', ms=3.5, lw=1.6, color=MCOL[meth], label=MLAB[meth])
        ax[1, j].plot(NS, [x['rho'] for x in v], '-o', ms=3.5, lw=1.6, color=MCOL[meth])
    lin = S[f'5|{goal}|lin|-']
    ax[0, j].axhline(lin['cons'], color='#111827', ls='--', lw=1.0, label='linearized (no ensemble)')
    ax[1, j].axhline(lin['rho'], color='#111827', ls='--', lw=1.0)
    ax[0, j].set_title(GLAB[goal], fontsize=9)
    ax[1, j].set_xscale('log'); ax[1, j].set_xticks(NS); ax[1, j].set_xticklabels([str(n) for n in NS])
    ax[1, j].minorticks_off(); ax[1, j].set_xlabel('model runs used to score the designs')
    ax[0, j].grid(alpha=0.25, lw=0.5); ax[1, j].grid(alpha=0.25, lw=0.5)
ax[0, 0].set_ylabel('share of the constrained optimum (%)\n(random half of the wells available)')
ax[1, 0].set_ylabel('rank correlation with\nthe exact EIG (Spearman)')
h, l = ax[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=5, frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.01))
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(os.path.join(OUT, 'figH1_static.png'), dpi=200)
plt.close(fig)

# ---------------------------------------------------------------- figure 2: sequential policies
POL = ['static_lin', 'gauss', 'rew', 'harta1k', 'harta']
PLAB = {'static_lin': 'fixed design of the\nlinearized criterion', 'gauss': 'adaptive,\nGaussian map', 'rew': 'adaptive,\nre-weighting (12 000)',
        'harta1k': 'adaptive, HARTA\n(1 000 runs)', 'harta': 'adaptive, HARTA\n(12 000 runs)'}
PCOL = {'static_lin': '#111827', 'gauss': '#2563EB', 'rew': '#6B7280', 'harta1k': '#34D399', 'harta': '#059669'}
fig, ax = plt.subplots(1, 3, figsize=(10.2, 3.6), sharey=True)
for j, goal in enumerate(GOALS):
    f = f'harta_seq_{goal}.json'
    if not os.path.exists(f):
        continue
    R = json.load(open(f))['policies']
    x = np.arange(len(POL))
    g = [1000 * R[p]['gain_vs_static_ref'] for p in POL]; e = [1000 * 1.96 * R[p]['gain_se'] for p in POL]
    ax[j].bar(x, g, yerr=e, color=[PCOL[p] for p in POL], width=0.7, capsize=2.5, error_kw={'lw': 0.8})
    for xi, p in zip(x, POL):
        n = R[p]['n_distinct_designs']
        ax[j].text(xi, (max(g[xi] + e[xi], 0) + 2), f'{n}', ha='center', va='bottom', fontsize=7.5, color='#374151')
    ax[j].axhline(0, color='#111827', lw=0.8)
    ax[j].set_xticks(x); ax[j].set_xticklabels([PLAB[p] for p in POL], fontsize=6.8, rotation=0)
    ax[j].set_title(GLAB[goal], fontsize=9); ax[j].grid(axis='y', alpha=0.25, lw=0.5)
ax[0].set_ylabel('information gained relative to the best\nfixed 3-well design (millinats, 95% CI)')
fig.text(0.5, 0.005, 'numbers above the bars: different well sets the policy used over 1 000 synthetic truths',
         ha='center', fontsize=7.5, color='#374151')
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(os.path.join(OUT, 'figH2_seq.png'), dpi=200)
plt.close(fig)
print('figures written')
