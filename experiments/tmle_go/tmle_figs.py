"""Figures for the TMLE-GO section.
Reads the results JSON in this folder and writes the PNG figures (English labels) into this folder."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
BLUE, ORANGE, AQUA, VIOLET = '#2a78d6', '#eb6834', '#1baf7a', '#6250d6'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.0, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK, 'figure.facecolor': 'white',
                     'axes.facecolor': 'white', 'savefig.facecolor': 'white', 'axes.spines.top': False,
                     'axes.spines.right': False})
DATA = os.path.join(HERE, 'tmle_results.json')
OUT = HERE + os.sep
R = json.load(open(DATA))
T1, T2 = R['T1'], R['T2']

# ---------------- Figure 10.1: estimators of psi_d for the three regimes
EST = [('naive', 'simple comparison', MUTED, True), ('ipw', 'IPW', AQUA, True),
       ('gcomp_mis', 'g-computation, poor model', BLUE, False), ('gcomp_flex', 'g-computation, flexible model', BLUE, True),
       ('tmle_mis', 'TMLE, poor model', ORANGE, False), ('tmle_flex', 'TMLE, flexible model', ORANGE, True)]
REG = [('hi', '(a) always high pumping'), ('lo', '(b) always low pumping'), ('dyn', '(c) dynamic regime')]
fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.6), constrained_layout=True, sharey=True)
ys = np.arange(len(EST))[::-1]
for ax, (reg, title) in zip(axs, REG):
    for y, (k, lab, col, filled) in zip(ys, EST):
        e = T1[reg][k]
        ax.plot([e['bias'] - 1.96 * e['sd'], e['bias'] + 1.96 * e['sd']], [y, y], color=col, lw=1.6, solid_capstyle='round')
        ax.plot(e['bias'], y, 'o', ms=5.5, color=col if filled else 'white', mec=col, mew=1.6)
        if k.startswith('tmle'):
            ax.text(0.98, y + 0.28, f"coverage {round(100 * e['cover'])}%", transform=ax.get_yaxis_transform(),
                    ha='right', va='bottom', fontsize=5.8, color=INK2)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_title(title, fontsize=7.6, loc='left'); ax.grid(axis='x', color=GRID, lw=0.6); ax.set_axisbelow(True)
    ax.set_xlim(-0.25, 0.25); ax.set_xticks([-0.2, -0.1, 0, 0.1, 0.2])
    ax.set_xlabel('estimate − truth', fontsize=7)
axs[0].set_yticks(ys); axs[0].set_yticklabels([lab for _, lab, _, _ in EST], fontsize=6.6)
fig.savefig(OUT + 'figT1_estimators.png', dpi=220)

# ---------------- Figure 10.2: monitoring design for the risk difference
DES = [('op', "operator's reading", BLUE, 'o'), ('precise', 'precise toe sensor', AQUA, 's'),
       ('op+D', "operator's reading + drought index", ORANGE, 'o'), ('precise+D', 'precise sensor + drought index', VIOLET, 's')]
ns = np.array(R['P']['NS2'])
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.6), constrained_layout=True)
for k, lab, col, mk in DES:
    rm = [T2[str(n)][k]['rmse'] for n in ns]; cv = [T2[str(n)][k]['cover'] for n in ns]
    axs[0].plot(ns, rm, color=col, lw=1.8, marker=mk, ms=4, mec='white', mew=0.6, label=lab)
    axs[1].plot(ns, cv, color=col, lw=1.8, marker=mk, ms=4, mec='white', mew=0.6, label=lab)
for ax in axs:
    ax.set_xscale('log', base=2); ax.set_xticks(ns); ax.set_xticklabels([str(n) for n in ns])
    ax.set_xlabel('number of wells in the data'); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
axs[0].set_ylim(0, None); axs[0].set_title('(a) RMSE of the risk difference', fontsize=7.6, loc='left')
axs[1].axhline(0.95, color=INK2, lw=0.8, ls='--'); axs[1].set_ylim(0, 1.02)
axs[1].set_title('(b) coverage of the 95% interval', fontsize=7.6, loc='left')
axs[1].legend(frameon=False, fontsize=6.0, loc='lower left')
fig.savefig(OUT + 'figT2_design.png', dpi=220)
print('saved')
