"""Figure of MESIMI-GO: figM1_learning.png
(a) regret of certainty-equivalent learning of the pumping rule against months, for the drought-aware rule (no
    injected exploration), the head-only rule without and with injected exploration; references log T and sqrt T;
(b) error of the estimated pumping response beta against months for the three learners;
(c) measured regret increments of the drought-aware learner against the closed-form prediction c ln(T/T0).
Colours: categorical slots in fixed order (blue: drought-aware, orange: head-only, aqua: head-only with exploration)."""
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
COL = {'full, no exploration': '#2a78d6', 'head-only, no exploration': '#eb6834', 'head-only, exploration t^-1/4': '#1baf7a'}
LAB = {'full, no exploration': 'drought-aware rule, no exploration', 'head-only, no exploration': 'head-only rule, no exploration',
       'head-only, exploration t^-1/4': 'head-only rule, exploration $t^{-1/4}$'}
R = json.load(open('mesimi_results.json')); TH = json.load(open('mesimi_theory.json'))
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.5), gridspec_kw=dict(width_ratios=[1.2, 1.0, 0.9]))
plt.subplots_adjust(left=0.06, right=0.985, top=0.88, bottom=0.16, wspace=0.34)
for k in COL:
    g = np.array(R[k]['grid']); r = np.array(R[k]['regret']); se = np.array(R[k]['se'])
    ax[0].loglog(g, np.maximum(r, 1e-2), color=COL[k], lw=1.8, label=LAB[k])
    ax[0].fill_between(g, np.maximum(r - 2 * se, 1e-2), r + 2 * se, color=COL[k], alpha=0.15, lw=0)
g = np.array(R['full, no exploration']['grid'])
rx = R['head-only, exploration t^-1/4']['final']
ax[0].loglog(g, rx * np.sqrt(g / g[-1]), color=MUTED, lw=0.9, ls=(0, (3, 2)))
ax[0].text(g[-1] * 0.6, rx * 1.35, r'$\propto\sqrt{T}$', color=INK2, fontsize=7.5, ha='right')
ax[0].set_ylim(0.5, 4000)
ax[0].set_xlabel('months of learning $T$')
ax[0].set_ylabel('regret (cumulative excess cost)')
ax[0].set_title('(a) a rule that listens to drought learns itself', fontsize=8.5)
ax[0].legend(frameon=False, fontsize=6.6, loc='upper left')
ax[0].grid(color=GRID, lw=0.5, which='major'); ax[0].set_axisbelow(True)
for k in COL:
    b = np.array(R[k]['beta_rmse'])
    ax[1].loglog(b[:, 0], b[:, 1], marker='o', ms=4.5, color=COL[k], lw=1.6, mec='white', mew=0.8)
bb = np.array([100, 20000])
ax[1].loglog(bb, 0.034 * (bb / 100) ** -0.5, color=MUTED, lw=0.9, ls=(0, (3, 2)))
ax[1].text(300, 0.034 * 3 ** -0.5 * 0.62, 'slope $-1/2$', color=INK2, fontsize=7, ha='right')
ax[1].set_xlabel('months of learning')
ax[1].set_ylabel(r'RMSE of the pumping response $\hat{\beta}$')
ax[1].set_title('(b) what is learned about the aquifer', fontsize=8.5)
ax[1].grid(color=GRID, lw=0.5, which='major'); ax[1].set_axisbelow(True)
inc = TH['increments']
pr = [d['predicted'] for d in inc]; me = [d['measured'] for d in inc]
lim = [0, 2.0]
ax[2].plot(lim, lim, color=MUTED, lw=0.9, ls=(0, (3, 2)))
ax[2].plot(pr, me, 'o', color=COL['full, no exploration'], ms=6, mec='white', mew=1.0)
for d in inc:
    ax[2].text(d['predicted'] + 0.05, d['measured'] - 0.08, f"$T_0$={d['T0']}", fontsize=6.6, color=INK2)
ax[2].set_xlim(lim); ax[2].set_ylim(lim)
ax[2].set_xlabel(r'predicted $c\,\ln(T/T_0)$')
ax[2].set_ylabel('measured regret from $T_0$ to $T$')
ax[2].set_title('(c) the log T constant, checked', fontsize=8.5)
ax[2].grid(color=GRID, lw=0.5); ax[2].set_axisbelow(True)
fig.savefig('figM1_learning.png', dpi=220)
