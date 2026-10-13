"""Figures for the KALIB-GO section (Albanian labels). Reads kalibgo_results.json."""
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
R = json.load(open('kalibgo_results.json'))
NES = [int(k) for k in R['E1']]
xs = np.arange(len(NES))
SER = [('bayes', 'Bayes (η = 1)', BLUE, 'o', '-'), ('bag', 'BayesBag', ORANGE, 's', '-'),
       ('safe10', 'SAFE-GO (SafeBayes)', AQUA, '^', '-'), ('kalib', 'KALIB-GO', VIOLET, 'D', '-'),
       ('oracle', 'orakulli (njeh leximet e sakta)', MUTED, None, '--')]

# ---------------- Figure 10.1: coverage, width and eta vs number of exact coastal readings
fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.45), constrained_layout=True)
for ax, key, lab in [(axs[0], 'cov', '(a) mbulimi i intervalit 90%'), (axs[1], 'wid', '(b) gjerësia mesore e tij [m]'),
                     (axs[2], 'eta', '(c) η mesore')]:
    for m, name, col, mk, ls in SER:
        if key == 'eta' and m in ('bag', 'oracle'):
            continue
        v = [R['E1'][str(ne)][m][key] for ne in NES]
        ax.plot(xs, v, color=col, lw=1.6 if m != 'oracle' else 1.2, ls=ls, marker=mk, ms=4 if mk != 'D' else 3.6,
                mec='white', mew=0.8, label=name, zorder=3 if m == 'kalib' else 2)
    ax.set_xticks(xs); ax.set_xticklabels([str(n) for n in NES])
    ax.set_xlabel('lexime të sakta në bregdet, $n_e$'); ax.set_title(lab, fontsize=8, loc='left')
    ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
axs[0].axhline(0.9, color=INK2, lw=0.8, ls=':')
axs[0].set_ylim(0, 1.05); axs[2].set_ylim(0, 1.05)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc='outside lower center', ncol=3, frameon=False, fontsize=7)
fig.savefig('figK1_coverage.png', dpi=220)

# ---------------- Figure 10.2: calibration curve and data worth
fig, axs = plt.subplots(1, 3, figsize=(6.3, 2.45), constrained_layout=True, gridspec_kw={'width_ratios': [1.05, 1.25, 0.9]})
ax = axs[0]
etas = np.array(R['ETAS'])
RAMP = {0: '#b3aaf0', 60: '#8274e0', 240: '#3b2a9e'}
for ne, col in RAMP.items():
    bc = R['bootcov'][str(ne)]
    ax.fill_between(etas, bc['q25'], bc['q75'], color=col, alpha=0.18, lw=0)
    ax.plot(etas, bc['med'], color=col, lw=1.6, marker='o', ms=2.8, label=f'$n_e$ = {ne}')
ax.set_xscale('log', base=2); ax.set_xticks([1 / 64, 1 / 16, 1 / 4, 1]); ax.set_xticklabels(['1/64', '1/16', '1/4', '1'])
ax.axhline(0.9, color=INK2, lw=0.8, ls=':')
ax.set_xlabel('η'); ax.set_title('(a) mbulimi bootstrap $c(\\eta)$', fontsize=8, loc='left')
ax.set_ylim(0, 1.05); ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=6.5, loc='lower left')

ax = axs[1]
ADD = [('coast', '+120\nbregdet'), ('near', '+6\nafër'), ('spread', '+6\nshpërnd.')]
DM = [('bayes', 'Bayes', BLUE), ('safe10', 'SAFE-GO', AQUA), ('kalib', 'KALIB-GO', VIOLET)]
bw = 0.26
for j, (m, name, col) in enumerate(DM):
    v = [R['decision'][m]['worth_med'][a] for a, _ in ADD]
    ax.bar(np.arange(3) + (j - 1) * bw, v, width=bw * 0.9, color=col, label=name)
ax.axhline(0, color=INK2, lw=0.6)
ax.set_xticks(np.arange(3)); ax.set_xticklabels([n for _, n in ADD], fontsize=7)
ax.set_title('(b) vlera e dukshme [m]', fontsize=8, loc='left')
ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=6.5, loc='upper right')

ax = axs[2]
DMB = DM
v = [R['decision'][m]['cov'] for m, _, _ in DMB]
ax.bar(np.arange(len(DMB)), v, width=0.62, color=[c for _, _, c in DMB])
for i, x in enumerate(v):
    ax.text(i, x - 0.04, f'{int(100 * x + 0.5 + 1e-9)}%', ha='center', va='top', fontsize=7, color='white', fontweight='bold')
ax.axhline(0.9, color=INK2, lw=0.8, ls=':')
ax.set_xticks(np.arange(len(DMB))); ax.set_xticklabels([n for _, n, _ in DMB], fontsize=7, rotation=0)
ax.set_ylim(0, 1.12); ax.set_title('(c) mbulimi pas vendimit', fontsize=8, loc='left')
ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
fig.savefig('figK2_design.png', dpi=220)
print('saved')
