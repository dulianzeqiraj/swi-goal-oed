"""Figure of KUFIRI-GO: figK1_budget.png
(a) share of the toe-forecast variance by boundary group at horizons of 1, 5 and 20 years (status-quo pumping);
(b) toe standard deviation at 5 and 20 years against the pumping response k (intervention on the controllable boundary);
(c) twenty-year toe advance, mean and +-1 sd, for six pumping rules (Monte Carlo, 4,000 paths).
Colours: boundary groups use categorical slots in fixed order (sea blue, atmosphere orange, river aqua, pumping
yellow, initial state magenta); horizons in panel (b) use the blue ramp."""
import json
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#c3c2b7', 'xtick.color': '#52514e', 'ytick.color': '#52514e',
                     'axes.labelcolor': '#0b0b0b'})
INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#898781', '#e1e0d9'
COL = {'sea': '#2a78d6', 'atmosphere': '#eb6834', 'river': '#1baf7a', 'pumping': '#eda100', 'initial state': '#e87ba4'}
RAMP = ['#86b6ef', '#104281']
R = json.load(open('kufiri_results.json'))
G = json.load(open('kufiri_regimes.json'))
H = R['P']['horizons']
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.9), gridspec_kw=dict(width_ratios=[0.9, 1.0, 1.35]))
plt.subplots_adjust(left=0.06, right=0.985, top=0.88, bottom=0.25, wspace=0.42)
# (a) stacked shares
groups = list(COL)
for j, h in enumerate(H):
    tot = R['total_sq'][j]; base = 0
    for gname in groups:
        v = 100 * sum(R['budget_sq'][s][j] for s in R['sources'] if R['group'][s] == gname) / tot
        ax[0].bar(j, v, bottom=base, color=COL[gname], width=0.62, edgecolor='white', linewidth=1.0)
        if v > 6:
            ax[0].text(j, base + v / 2, f'{v:.0f}%', ha='center', va='center', fontsize=6.8, color=INK)
        base += v
    ax[0].text(j, 102, f'sd {np.sqrt(tot):.0f} m', ha='center', va='bottom', fontsize=6.6, color=INK2)
ax[0].set_xticks(range(len(H))); ax[0].set_xticklabels([f'{h:.0f} yr' for h in H])
ax[0].set_ylim(0, 112); ax[0].set_ylabel('share of the toe-forecast variance (%)')
ax[0].set_title('(a) which boundary matters, by horizon', fontsize=8.5)
from matplotlib.patches import Patch
ax[0].legend(handles=[Patch(color=COL[g], label=g) for g in groups], frameon=False, fontsize=6.4, loc='upper left',
             bbox_to_anchor=(-0.05, -0.1), ncol=3, columnspacing=0.8, handlelength=1.0, handleheight=0.8)
# (b) policy curve
ks = [float(k) for k in R['policy']]
kk = np.linspace(-3500, 1500, 200)
for j, col in zip([1, 2], RAMP):
    v = np.array([R['policy'][str(k) if str(k) in R['policy'] else k]['var'][j] for k in R['policy']])
    c = np.polyfit(ks, v, 2)
    ax[1].plot(kk, np.sqrt(np.clip(np.polyval(c, kk), 0, None)), color=col, lw=1.8, label=f'{H[j]:.0f} years')
    ko = R['kopt'][j]['k']
    ax[1].plot([ko], [R['kopt'][j]['sd']], 'o', color=col, ms=5, mec='white', mew=1.0)
ax[1].axvline(R['P']['k_sq'], color=INK2, lw=0.8, ls=(0, (3, 2)))
ax[1].axvline(0, color=INK2, lw=0.8)
ax[1].text(R['P']['k_sq'] + 60, 8, 'status quo:\npump more\nin drought', fontsize=6.4, color=INK2)
ax[1].text(-80, 8, 'fixed\npumping', fontsize=6.4, color=INK2, ha='right')
ax[1].text(R['kopt'][2]['k'], R['kopt'][2]['sd'] - 14, 'optimal rule', fontsize=6.4, color=INK2, ha='center')
ax[1].set_xlabel('pumping response $k$ to soil-moisture deficit (m$^2$ yr$^{-1}$ per m yr$^{-1}$)')
ax[1].set_ylabel('toe standard deviation (m)')
ax[1].set_ylim(0, 230)
ax[1].set_title('(b) pumping as the controllable boundary', fontsize=8.5)
ax[1].legend(frameon=False, fontsize=6.6, loc='upper left')
ax[1].grid(color=GRID, lw=0.5); ax[1].set_axisbelow(True)
# (c) rules
rules = [('constant pumping', 'constant pumping'),
         ('linear status quo (k=+500)', 'linear, status quo'),
         ('regimes, status quo (emergency +150 in drought)', '3 regimes, status quo'),
         ('regimes, adaptive (restricted -150 in drought)', '3 regimes, adaptive'),
         ('regimes, adaptive both ways (-150 drought, +100 wet)', '3 regimes, adaptive both ways'),
         ('linear optimal (k*=-1482)', 'linear, optimal')]
for i, (key, lab) in enumerate(rules[::-1]):
    o = G[key]
    ax[2].plot([o['mean'] - o['sd'], o['mean'] + o['sd']], [i, i], color='#2a78d6', lw=2.0, solid_capstyle='round')
    ax[2].plot([o['mean']], [i], 'o', color='#104281', ms=5, mec='white', mew=1.0)
    ax[2].text(o['mean'] + o['sd'] + 12, i, f"{o['mean']:.0f} ± {o['sd']:.0f} m", va='center', fontsize=6.6, color=INK2)
ax[2].set_yticks(range(len(rules))); ax[2].set_yticklabels([lab for _, lab in rules[::-1]], fontsize=7)
ax[2].axvline(0, color=INK2, lw=0.8)
ax[2].set_xlim(-130, 330)
ax[2].set_xlabel('toe advance after 20 years (m; mean ± 1 sd)')
ax[2].set_title('(c) pumping regimes, 20 years', fontsize=8.5)
ax[2].grid(color=GRID, lw=0.5, axis='x'); ax[2].set_axisbelow(True)
fig.savefig('figK1_budget.png', dpi=220)
