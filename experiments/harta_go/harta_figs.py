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
PLAB = {'static_lin': 'fixed\n(linearized)', 'gauss': 'Gaussian\nmap', 'rew': 're-weighting\n12 000',
        'harta1k': 'HARTA\n1 000', 'harta': 'HARTA\n12 000'}
PLEG = {'static_lin': 'fixed design of the linearized criterion', 'gauss': 'adaptive, Gaussian map (12 000 runs)',
        'rew': 'adaptive, re-weighting (12 000 runs)', 'harta1k': 'adaptive, HARTA map (1 000 runs)',
        'harta': 'adaptive, HARTA map (12 000 runs)'}
PCOL = {'static_lin': '#111827', 'gauss': '#2563EB', 'rew': '#6B7280', 'harta1k': '#34D399', 'harta': '#059669'}
fig, ax = plt.subplots(1, 3, figsize=(10.2, 3.9), sharey=True)
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
    ax[j].set_xticks(x); ax[j].set_xticklabels([PLAB[p] for p in POL], fontsize=7.2, rotation=0)
    ax[j].set_title(GLAB[goal], fontsize=9); ax[j].grid(axis='y', alpha=0.25, lw=0.5)
ax[0].set_ylabel('information gained relative to the best\nfixed 3-well design (millinats, 95% CI)')
from matplotlib.patches import Patch
fig.legend([Patch(color=PCOL[p]) for p in POL], [PLEG[p] for p in POL], loc='lower center', ncol=3,
           frameon=False, fontsize=7.5, bbox_to_anchor=(0.5, 0.035))
fig.text(0.5, 0.005, 'numbers above the bars: different well sets the policy used over 1 000 synthetic truths',
         ha='center', fontsize=7.5, color='#374151')
fig.tight_layout(rect=(0, 0.15, 1, 1))
fig.savefig(os.path.join(OUT, 'figH2_seq.png'), dpi=200)
plt.close(fig)
# ---------------------------------------------------------------- summary for the report
RF = np.load('harta_ref.npz'); Z = np.load('harta_ens.npz')
ids = Z['ids']
summ = {'P0': RF['P0'].tolist(), 'optimum': {}, 'ess_mean': {}}
for k in (3, 5):
    D = RF[f'D{k}']; EX = RF[f'EX{k}']
    summ['ess_mean'][str(k)] = float(RF[f'ESS{k}'].mean())
    for g, goal in enumerate(GOALS):
        i = int(EX[:, g].argmax())
        summ['optimum'][f'{k}|{goal}'] = {'wells': ids[list(D[i])].tolist(), 'eig': float(EX[i, g]), 'median_design_eig': float(np.median(EX[:, g]))}
json.dump(summ, open(os.path.join(OUT, 'harta_summary.json'), 'w'), indent=1)
print('figures and summary written')
