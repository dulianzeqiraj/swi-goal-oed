"""Figures for the KRAMERS-GO section.
Reads the results JSON in this folder and writes the PNG figures (English labels) into this folder."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
import json
import numpy as np
import matplotlib
import matplotlib.ticker
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.0, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK, 'figure.facecolor': 'white',
                     'axes.facecolor': 'white', 'savefig.facecolor': 'white', 'axes.spines.top': False, 'axes.spines.right': False})
NUM = HERE + os.sep
OUT = HERE + os.sep
R = json.load(open(NUM + 'kramers_results.json'))
E1 = R['E1']; f = np.array([r['f'] for r in E1])

fig, ax = plt.subplots(figsize=(6.3, 2.9), constrained_layout=True)
ax.plot(f, [r['T_kramers'] for r in E1], color=ORANGE, lw=1.6, ls=':', marker='s', ms=3.5, label='weak-noise Kramers formula (Section 1.10)')
ax.plot(f, [r['T_1D'] for r in E1], color=AQUA, lw=1.6, ls='--', marker='^', ms=3.5, label='1D reduction with multiplicative white noise')
ax.plot(f, [r['T_2D'] for r in E1], color=BLUE, lw=1.8, label='KRAMERS-GO: 2D Kolmogorov equation')
ax.plot(f, [r['T_sim'] for r in E1], ls='none', marker='o', ms=5, mfc='white', mec=INK, mew=1.1, label='simulation (2 000 trajectories)')
for T in (50, 100):
    ax.axhline(T, color=MUTED, lw=0.7, ls=':'); ax.text(f[0] + 0.002, T * 1.12, f'{T} years', color=INK2, fontsize=7)
ax.set_yscale('log'); ax.set_xlabel('pumping rate as a fraction of the critical discharge, $Q/Q_c$'); ax.set_ylabel('mean time to well salinization [years]')
ax.grid(axis='y', color=GRID, lw=0.6, which='major'); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=7, loc='upper right')
fig.savefig(OUT + 'figR1_escape.png', dpi=220)

fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.75), constrained_layout=True, gridspec_kw={'width_ratios': [1, 1.2]})
TS = [t for t in R['TS'] if t >= 25]; E2 = R['E2']; E3 = R['E3']  # T=10 hits the grid cap 0.975
nom = [E2['fsafe'][str(T)] for T in TS]
draws = np.array([[d['fsafe'][str(T)] for T in TS] for d in E3])
lo, hi = np.percentile(draws, [10, 90], axis=0)
ax = axs[0]
ax.fill_between(TS, lo, hi, color=BLUE, alpha=0.15, lw=0, label='prior of K and $q_0$, 10–90%')
ax.plot(TS, nom, color=BLUE, lw=1.8, marker='o', ms=3.5, label='nominal parameters')
ax.set_xscale('log'); ax.set_xticks(TS); ax.set_xticklabels([str(t) for t in TS]); ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
ax.set_xlabel('return period T [years]'); ax.set_title('(a) safe pumping rate $Q_T/Q_c$', loc='left', fontsize=8)
ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True); ax.legend(frameon=False, fontsize=7, loc='lower left')
ax = axs[1]
E4 = R['E4']; keys = ['s', 'theta', 'tau', 'K', 'q0']
lab = {'s': '$s$\n(recharge)', 'theta': '$\\theta$\n(memory)', 'tau': '$\\tau$\n(relaxation)', 'K': '$K$\n(hydraulic\nconductivity)', 'q0': '$q_0$\n(regional\nflow)'}
Qc0 = E2['Qc']
def el(key, what):
    lo_ = [c for c in E4 if c['key'] == key and c['fac'] < 1][0]; hi_ = [c for c in E4 if c['key'] == key and c['fac'] > 1][0]
    if what == 'Qc':
        a, b = lo_['Qc'], hi_['Qc']
    else:
        a, b = lo_['fsafe']['100'] * lo_['Qc'], hi_['fsafe']['100'] * hi_['Qc']
    return (np.log(b) - np.log(a)) / (np.log(1.2) - np.log(0.8))
xs = np.arange(len(keys)); bw = 0.38
ax.bar(xs - bw / 2, [el(k, 'Qc') for k in keys], width=bw * 0.92, color=MUTED, label='critical discharge $Q_c$')
ax.bar(xs + bw / 2, [el(k, 'Q100') for k in keys], width=bw * 0.92, color=ORANGE, label='safe pumping rate $Q_{100}$')
ax.axhline(0, color=INK2, lw=0.6)
ax.set_xticks(xs); ax.set_xticklabels([lab[k] for k in keys], fontsize=6.5)
ax.set_title('(b) elasticity with respect to the parameters', loc='left', fontsize=8); ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.legend(frameon=False, fontsize=7, loc='upper left')
fig.savefig(OUT + 'figR2_safe.png', dpi=220)
print('saved')
