"""Figures for the ATRIB-GO section.
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
SRC = HERE + os.sep
OUT = HERE + os.sep
R = json.load(open(SRC + 'atrib_results.json'))
A2 = R['A2']; D = A2['designs']; N = np.array(A2['test_N'])
ORDER = [('none', 'event\nonly'), ('time', '+ date'), ('toe_100', '+ toe\n100 m'), ('toe_50', '+ toe\n50 m'),
         ('rain_y_0.10', '+ rain\nannual\n0.10'), ('rain_y_0.05', '+ rain\nannual\n0.05'), ('rain_y_0.02', '+ rain\nannual\n0.02'),
         ('rain_q_0.02', '+ rain\nquarterly\n0.02')]
ORDER = [(k, l) for k, l in ORDER if k in D]

# ---------------- Figure 10.1: PN vs event date, and event-level PN by design
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.7), constrained_layout=True, gridspec_kw={'width_ratios': [1, 1.55]})
ax = axs[0]
t = np.array(A2['pn_of_t']['t']); pn = np.array(A2['pn_of_t']['pn'])
ax.plot(t, pn, color=BLUE, lw=1.8, marker='o', ms=3, mec='white', mew=0.6, label='PN by date')
ax.axhline(A2['pn_pop'], color=MUTED, lw=1.1, ls='--', label='population PN')
ax.set_xlabel('year of salinization after the pumping increase'); ax.set_ylim(0, 1.02)
ax.set_title('(a) PN by event date', fontsize=8, loc='left')
ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True); ax.legend(frameon=False, fontsize=6.5, loc='lower left')
ax = axs[1]
rng = np.random.default_rng(0)
keys = [k for k, _ in ORDER if k != 'none']
for i, k in enumerate(keys):
    p = np.array(D[k]['pn'])
    jit = rng.uniform(-0.28, 0.28, size=p.size)
    ax.scatter(i + jit[N == 1], p[N == 1], s=4, color=ORANGE, alpha=0.55, lw=0, label='pumping was necessary' if i == 0 else None)
    ax.scatter(i + jit[N == 0], p[N == 0], s=4, color=BLUE, alpha=0.75, lw=0, label='well salinized anyway' if i == 0 else None)
ax.axhline(A2['pn_pop'], color=MUTED, lw=1.0, ls='--')
ax.set_xticks(range(len(keys))); ax.set_xticklabels([l for k, l in ORDER if k != 'none'], fontsize=6)
ax.set_ylim(-0.03, 1.03); ax.set_title('(b) PN of a single event by data', fontsize=8, loc='left')
ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=6.5, loc='lower left', markerscale=2.5)
fig.savefig(OUT + 'figA1_pn.png', dpi=220)

# ---------------- Figure 10.2: worth of each design for the attribution goal
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.5), constrained_layout=True)
labels = [l for _, l in ORDER]; xs = np.arange(len(ORDER))
for ax, key, title in [(axs[0], 'H', '(a) attribution uncertainty [bit]'), (axs[1], 'brier', '(b) Brier error of PN')]:
    v = [D[k][key] for k, _ in ORDER]
    cols = [MUTED if k in ('none', 'time') else (AQUA if k.startswith('toe') else VIOLET) for k, _ in ORDER]
    ax.bar(xs, v, width=0.66, color=cols)
    for i, x in enumerate(v):
        ax.text(i, x + max(v) * 0.02, f'{x:.2f}', ha='center', va='bottom', fontsize=6, color=INK)
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=5.3)  # 5.6 in the Albanian figure; English labels are wider
    ax.set_title(title, fontsize=8, loc='left'); ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
    ax.set_ylim(0, max(v) * 1.15)
fig.savefig(OUT + 'figA2_design.png', dpi=220)
print('saved')
