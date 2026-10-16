"""Figures for the RRJEDHA-GO section (Albanian labels). Reads rrjedha_results.json."""
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
R = json.load(open('rrjedha_results.json'))
pop, pid, E2 = R['pop'], R['pid'], R['E2']; NS = R['P']['NS']; TD = 1000 * pop['te_do']

# ---------------- Figure 9.1: (a) population values of the four TE variants against TE_do; (b) PID of I(dX; A, D)
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.75), constrained_layout=True, gridspec_kw={'width_ratios': [1, 1.25]})
ax = axs[0]
items = [('TE_vëzh', 'te_obs', MUTED), ('TE_kusht', 'te_cond', VIOLET), ('TE_rregull', 'te_adj', BLUE),
         ('TE pa thatësirë', 'te_adj_noD', ORANGE)]
pos = np.arange(len(items))
for i, (lab, k, col) in enumerate(items):
    v = 1000 * pop[k]
    ax.bar(i, v, width=0.62, color=col)
    near = abs(v - TD) < 2.5
    ax.text(i, v - 2.4 if near else v + 0.6, f'{v:.1f}', ha='center', fontsize=6.6, color='white' if near else INK2)
ax.axhline(TD, color=INK, lw=1.4, ls='--')
ax.text(1.0, TD + 0.9, f'TE_do = {TD:.1f}', ha='center', fontsize=6.6, color=INK)
ax.set_xticks(pos); ax.set_xticklabels([it[0] for it in items], fontsize=6.4, rotation=20, ha='right')
ax.set_ylabel('milibit për pus-vit'); ax.set_ylim(0, 1.18 * max(1000 * pop[k] for _, k, _ in items))
ax.set_title('(a) rrjedha e informacionit pompim → majë', fontsize=7.6, loc='left')
ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
ax = axs[1]
parts = [('red', 'redundancë', MUTED), ('uni1', 'unike e pompimit', BLUE), ('uni2', 'unike e thatësirës', ORANGE),
         ('syn', 'sinergji', AQUA)]
cols = [('obs', 'vëzhgimore\nI_min'), ('obs_broja', 'vëzhgimore\nBROJA'), ('int', 'pompim i rastit\nI_min'),
        ('int_broja', 'pompim i rastit\nBROJA')]
x = np.arange(len(cols))
for j, (pk, lab, col) in enumerate(parts):
    bottom = np.array([sum(1000 * pid[c][q] for q, _, _ in parts[:j]) for c, _ in cols])
    h = np.array([1000 * pid[c][pk] for c, _ in cols])
    ax.bar(x, h, bottom=bottom, width=0.6, color=col, edgecolor='white', linewidth=1.0, label=lab)
for i, (c, _) in enumerate(cols):
    ax.text(i, 1000 * pid[c]['I12'] + 1.0, f"{1000 * pid[c]['uni1']:.1f}", ha='center', fontsize=6.3, color=BLUE)
ax.set_xticks(x); ax.set_xticklabels([c[1] for c in cols], fontsize=6.0)
ax.set_ylabel('milibit'); ax.set_ylim(0, 1.25 * max(1000 * pid[c]['I12'] for c, _ in cols))
ax.set_title('(b) PID e I(ΔX; A, D); numri sipër = unike e pompimit', fontsize=7.4, loc='left')
ax.legend(frameon=False, fontsize=5.8, loc='upper right', ncol=2)
ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
fig.savefig('figR1_rrjedha.png', dpi=220)

# ---------------- Figure 9.2: estimation from n wells: bias ±1 SD against each design's own TE_do, and coverage
E3 = R['E3']
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.75), constrained_layout=True)
LINES = [(E2, 'te_obs', 'TE_vëzh', MUTED, 'o', '-'), (E2, 'te_obs_bc', 'TE_vëzh, i korrigjuar', MUTED, 'o', '--'),
         (E2, 'te_adj', 'TE_rregull', BLUE, 's', '-'), (E2, 'te_adj_bc', 'TE_rregull, i korrigjuar', BLUE, 's', '--'),
         (E3, 'te_obs', 'rotacion, TE_vëzh', AQUA, 'D', '-'), (E3, 'te_obs_bc', 'rotacion, i korrigjuar', AQUA, 'D', '--')]
off = np.linspace(-0.2, 0.2, len(LINES))
for j, (E, k, lab, col, mk, ls) in enumerate(LINES):
    xx = np.array(NS) * 2 ** off[j]
    kw = dict(color=col, lw=1.5, ls=ls, marker=mk, ms=4, mec='white', mew=0.6, label=lab)
    if ls == '--':
        kw.update(mfc='white', mec=col, mew=1.2)
    b = np.array([1000 * E[str(n)][k]['bias'] for n in NS]); sd = np.array([1000 * E[str(n)][k]['sd'] for n in NS])
    axs[0].plot(xx, b, **kw); axs[0].vlines(xx, b - sd, b + sd, color=col, lw=0.9)
    if k in ('te_obs', 'te_obs_bc', 'te_adj', 'te_adj_bc'):
        axs[1].plot(np.array(NS), [E[str(n)][k]['cover'] for n in NS], **kw)
axs[0].axhline(0, color=INK, lw=1.0, ls=':')
axs[0].set_ylabel('zhvendosja (milibit)'); axs[0].set_title('(a) zhvendosja ±1 DS ndaj TE_do të dizajnit', fontsize=7.4, loc='left')
axs[1].axhline(0.95, color=INK2, lw=0.8, ls=':'); axs[1].set_ylim(-0.03, 1.03)
axs[1].set_ylabel('mbulimi i TE_do'); axs[1].set_title('(b) mbulimi i intervalit bootstrap 95%', fontsize=7.4, loc='left')
axs[1].legend(frameon=False, fontsize=5.6, loc='center left', bbox_to_anchor=(1.0, 0.5))
for ax in axs:
    ax.set_xscale('log', base=2); ax.set_xticks(NS); ax.set_xticklabels([str(n) for n in NS])
    ax.set_xlabel('numri i puseve (10 vjet secili)'); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
fig.savefig('figR2_vleresimi.png', dpi=220)
print('saved')
