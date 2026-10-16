"""Figures for the KUFI-GO section (Albanian labels). Reads kufi_results.json."""
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
R = json.load(open('kufi_results.json'))
XS = np.array(R['XS']); truth = np.array(R['truth']); A0 = str(R['alphas'][0]); NS = R['NS']
SUP_O = R['supply'][R['oracle'][A0]]; SUP_L = R['supply_lo']
gain = lambda s: (s - SUP_L) / (SUP_O - SUP_L)        # share of the achievable supply gain over always-low pumping
RULES = [('plugin', 'vlerësimi pikësor', MUTED, 'o'), ('point', 'kufi pikësor 95%', AQUA, 's'),
         ('band', 'brez i njëkohshëm', BLUE, 'o'), ('msm', 'brez nga MSM', ORANGE, 'D')]

# ---------------- Figure 10.1: the risk curve and the estimates; selected thresholds
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.7), constrained_layout=True, gridspec_kw={'width_ratios': [1, 1.15]})
ax = axs[0]; r = R['res']['2000|op+D']
ax.plot(XS, truth, color=INK, lw=1.8, label='rreziku i vërtetë')
ax.errorbar(XS - 0.003, truth + np.array(r['bias']), yerr=np.array(r['sd']), fmt='o', ms=3.5, color=BLUE, mec='white',
            mew=0.5, elinewidth=1.2, capsize=0, label='TMLE për çdo prag (±1 DS)')
ax.errorbar(XS + 0.003, truth + np.array(r['msm_bias']), yerr=np.array(r['msm_sd']), fmt='D', ms=3.2, color=ORANGE,
            mec='white', mew=0.5, elinewidth=1.2, capsize=0, label='MSM logjistik (±1 DS)')
ax.axhline(float(A0), color=INK2, lw=0.9, ls='--'); ax.text(XS[-1], float(A0) - 0.016, f'α = {A0}', fontsize=6.5, color=INK2, ha='right')
ax.set_xlabel('pragu x i leximit të majës'); ax.set_ylabel('rreziku i kripëzimit brenda 8 vjetësh')
ax.set_title('(a) kurba e rrezikut, 2 000 puse', fontsize=7.6, loc='left'); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=6.0, loc='upper left')
ax = axs[1]
labels = ['vetëm i ulët'] + [f'{x:.2f}' for x in XS]; pos = np.arange(len(labels)); w = 0.2
for i, (k, lab, col, _) in enumerate(RULES):
    h = np.array(r[A0][k]['hist']) / R['R']
    ax.bar(pos + (i - 1.5) * w, h, width=w, color=col, label=lab)
ko = R['oracle'][A0] + 1
ax.axvspan(ko + 0.5, len(labels) - 0.5, color='#f3d9cf', alpha=0.6, lw=0)
ax.text(ko + 0.65, 0.93, 'rrezik > α', fontsize=6.3, color=INK2, transform=ax.get_xaxis_transform())
ax.set_xticks(pos); ax.set_xticklabels(labels, fontsize=5.8, rotation=45, ha='right')
ax.set_ylabel('shpeshtësia e zgjedhjes'); ax.set_title('(b) pragu i zgjedhur nga çdo rregull', fontsize=7.6, loc='left')
ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True); ax.legend(frameon=False, fontsize=6.0, loc='upper left')
fig.savefig('figK1_curve.png', dpi=220)

# ---------------- Figure 10.2: violation rate and realized supply gain vs number of wells
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.8), constrained_layout=True)
LINES = [(k, lab + ', vëzhgimore', col, mk, '-', 'op+D') for k, lab, col, mk in RULES] + \
        [('band', 'brez i njëkohshëm, eksperiment', BLUE, 'o', '--', 'rct'), ('msm', 'brez nga MSM, eksperiment', ORANGE, 'D', '--', 'rct')]
for k, lab, col, mk, ls, des in LINES:
    v = [R['res'][f'{n}|{des}'][A0][k]['viol'] for n in NS]
    m = [gain(R['res'][f'{n}|{des}'][A0][k]['supply']) for n in NS]
    kw = dict(color=col, lw=1.7, ls=ls, marker=mk, ms=4, mec='white', mew=0.6, label=lab)
    if ls == '--':
        kw.update(mfc='white', mec=col, mew=1.2)
    axs[0].plot(NS, v, **kw); axs[1].plot(NS, m, **kw)
axs[0].axhline(0.05, color=INK2, lw=0.8, ls=':')
for ax in axs:
    ax.set_xscale('log', base=2); ax.set_xticks(NS); ax.set_xticklabels([str(n) for n in NS])
    ax.set_xlabel('numri i puseve'); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True); ax.set_ylim(0, 1.05)
axs[0].set_title('(a) P(rreziku i pragut të zgjedhur > α)', fontsize=7.4, loc='left')
axs[1].set_title('(b) pjesa e fitimit të mundshëm', fontsize=7.4, loc='left')
axs[1].legend(frameon=False, fontsize=5.6, loc='center left', bbox_to_anchor=(1.0, 0.5))
fig.savefig('figK2_safety.png', dpi=220)
print('saved')
