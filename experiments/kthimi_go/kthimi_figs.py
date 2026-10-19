"""Figures for the KTHIMI-GO section.
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
ORANGE = '#eb6834'
SEQ = ['#9ec5f0', '#5b9be3', '#2a78d6', '#164e94']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.0, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK, 'figure.facecolor': 'white',
                     'axes.facecolor': 'white', 'savefig.facecolor': 'white', 'axes.spines.top': False,
                     'axes.spines.right': False})
DATA = os.path.join(HERE, 'kthimi_results.json')
OUT = HERE
R = json.load(open(DATA))
D = R['designs']; SIGS, KAPS = R['P']['SIGS'], R['P']['KAPS']
mon = [d for d in D if not d['nomon']]; nm = [d for d in D if d['nomon']][0]

# ---------------- Figure 9.1: risk against feedback information and against sensor information
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.8), constrained_layout=True, sharey=True)
for ax, key, xl, title in ((axs[0], 'feedback', 'information that reaches the decision, I(X; A | A₋₁, D) (bit)', '(a) against feedback information (ρ = ' + f"{R['rho_feedback']:.2f}".replace('-', '−') + ')'),
                           (axs[1], 'sensor', 'information the reading carries about the toe, I(X; R) (bit)', '(b) against sensor information (ρ = ' + f"{R['rho_sensor']:.2f}".replace('-', '−') + ')')):
    for j, k in enumerate(KAPS):
        pts = sorted([d for d in mon if d['kappa'] == k], key=lambda d: d[key])
        ax.plot([d[key] for d in pts], [100 * d['risk'] for d in pts], '-o', color=SEQ[j], lw=1.2, ms=4.2,
                mec='white', mew=0.6, label=f'response κ = {k:g}')
    ax.plot(0, 100 * nm['risk'], 'D', color=ORANGE, ms=5.5, mec='white', mew=0.6, label='no monitoring')
    ax.set_xlabel(xl, fontsize=7.0); ax.set_title(title, fontsize=7.4, loc='left')
    ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
axs[0].set_ylabel('10-year salinization risk (%)')
axs[0].legend(frameon=False, fontsize=6.0, loc='upper right')
fig.savefig(os.path.join(OUT, 'figK1_kthimi.png'), dpi=220)

# ---------------- Figure 9.2: feedback information and risk reduction over the design grid
F = np.array([[[d for d in mon if d['sig'] == s and d['kappa'] == k][0]['feedback'] for k in KAPS] for s in SIGS])
G = np.array([[[d for d in mon if d['sig'] == s and d['kappa'] == k][0]['gain'] for k in KAPS] for s in SIGS])
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.75), constrained_layout=True)
for ax, M, fmt, title, cmap in ((axs[0], 1000 * F, '{:.0f}', '(a) feedback information (millibit per decision)', 'Blues'),
                                (axs[1], 100 * G, '{:.1f}', '(b) risk reduction, percentage points', 'Oranges')):
    im = ax.imshow(M, cmap=cmap, aspect='auto', origin='upper')
    for i in range(len(SIGS)):
        for j in range(len(KAPS)):
            v = M[i, j]; dark = v > 0.6 * M.max()
            ax.text(j, i, fmt.format(v), ha='center', va='center', fontsize=6.6, color='white' if dark else INK)
    ax.set_xticks(range(len(KAPS))); ax.set_xticklabels([f'{k:g}' for k in KAPS])
    ax.set_yticks(range(len(SIGS))); ax.set_yticklabels([f'{s:g}' for s in SIGS])
    ax.set_xlabel('operator response to the alarm κ'); ax.set_ylabel('reading noise σ')
    ax.set_title(title, fontsize=7.2, loc='left')
    for s in ax.spines.values():
        s.set_visible(False)
fig.savefig(os.path.join(OUT, 'figK2_rrjeta.png'), dpi=220)
print('saved')
