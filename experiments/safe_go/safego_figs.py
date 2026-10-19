"""Figures for the SAFE-GO section.
Reads the results JSON in this folder and writes the PNG figures (English labels) into this folder."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.0, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK, 'figure.facecolor': 'white',
                     'axes.facecolor': 'white', 'savefig.facecolor': 'white', 'axes.spines.top': False,
                     'axes.spines.right': False})
NUM = HERE + os.sep
OUT = HERE + os.sep
os.makedirs(OUT, exist_ok=True)
R = json.load(open(NUM + 'safego_results.json'))
NES = [int(k) for k in R['E1']]
xs = np.arange(len(NES))
SER = [('bayes', 'Bayes (η = 1)', BLUE, 'o', '-'), ('safe', 'SafeBayes, 1 ordering', ORANGE, 's', '-'),
       ('safe10', 'SAFE-GO: SafeBayes, 10 orderings', AQUA, '^', '-'), ('oracle', 'oracle (knows the exact readings)', MUTED, None, '--')]

# ---------------- Figure 10.1: effect of exact coastal readings
fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.35), constrained_layout=True)
for ax, key, lab in [(axs[0], 'cov', '(a) 90% interval coverage'), (axs[1], 'wid', '(b) its median width [m]'),
                     (axs[2], 'deg', '(c) mean polynomial degree')]:
    for m, name, col, mk, ls in SER:
        v = [R['E1'][str(ne)][m][key] for ne in NES]
        ax.plot(xs, v, color=col, lw=1.6 if m != 'oracle' else 1.2, ls=ls, marker=mk, ms=4, mec='white', mew=0.8, label=name)
    ax.set_xticks(xs); ax.set_xticklabels([str(n) for n in NES])
    ax.set_xlabel('exact coastal readings, $n_e$'); ax.set_title(lab, fontsize=8, loc='left')
    ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
axs[0].axhline(0.9, color=INK2, lw=0.8, ls=':')
axs[0].set_ylim(0, 1.05)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc='outside lower center', ncol=2, frameon=False, fontsize=7)
fig.savefig(OUT + 'figS1_coastal.png', dpi=220)

# ---------------- Figure 10.2: data worth of three monitoring additions
ADD = [('base', 'base'), ('coast', '+120\ncoast'), ('near', '+6\nnear'), ('spread', '+6\nspread')]
fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.35), constrained_layout=True)
bw = 0.36
for ax, key, lab in [(axs[0], 'wid', '(a) 90% interval width [m]'), (axs[1], 'cov', '(b) 90% interval coverage'),
                     (axs[2], 'err_med', '(c) median toe error [m]')]:
    for j, (m, name, col, mk, ls) in enumerate([SER[0], SER[2]]):
        v = [R['E2'][a][m][key] for a, _ in ADD]
        ax.bar(np.arange(4) + (j - 0.5) * bw, v, width=bw * 0.92, color=col, label=name, linewidth=0)
    ax.set_xticks(np.arange(4)); ax.set_xticklabels([t for _, t in ADD], fontsize=6.8)
    ax.set_title(lab, fontsize=8, loc='left'); ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
axs[1].axhline(0.9, color=INK2, lw=0.8, ls=':'); axs[1].set_ylim(0, 1.05)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc='outside lower center', ncol=2, frameon=False, fontsize=7)
fig.savefig(OUT + 'figS2_dataworth.png', dpi=220)
print('saved')
