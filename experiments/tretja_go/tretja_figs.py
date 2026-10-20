"""Figures for the TRETJA-GO section. Reads tretja_results.json, tretja_grid.npz and tretja_table.npz; writes
figT1_kinetics.png and figT2_design.png (English labels).   Run: python3 tretja_figs.py"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import tretja as T

HERE = os.path.dirname(os.path.abspath(__file__))
INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
BLUE, ORANGE, GREEN, RED = '#0072B2', '#E69F00', '#009E73', '#C0392B'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.0, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK, 'figure.facecolor': 'white',
                     'axes.facecolor': 'white', 'savefig.facecolor': 'white', 'axes.spines.top': False,
                     'axes.spines.right': False})
R = json.load(open(os.path.join(HERE, 'tretja_results.json')))
G = np.load(os.path.join(HERE, 'tretja_grid.npz'))
TAB = T.load_table()
P = R['params']


def grid_ax(ax):
    ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)


# ---------- Figure 1: chemistry, rate laws, regimes ----------
fig, axs = plt.subplots(1, 3, figsize=(10.2, 3.5), gridspec_kw=dict(wspace=0.36))
ax = axs[0]
om0 = 10 ** TAB['logom'][:, 0]
ax.plot(TAB['F'], om0, color=BLUE, lw=1.8)
ax.set_xlabel('seawater fraction of the mixture'); ax.set_ylabel('calcite saturation ratio Ω', color=BLUE)
ax.set_ylim(0.5, 1.02)
ax.text(0.27, om0.min() - 0.025, f"Ω min = {om0.min():.2f}", color=BLUE, fontsize=7.5, ha='left', va='top')
ax.set_title('(a) mixing corrosion', loc='left', fontsize=9)
ax2 = ax.inset_axes([0.33, 0.57, 0.40, 0.28])
ax2.plot(TAB['F'], TAB['dsat'], color=ORANGE, lw=1.4)
ax2.set_title('calcite that can dissolve (mmol/L)', fontsize=6.5, color=INK2)
ax2.tick_params(labelsize=6); ax2.set_xticks([0, 0.5, 1]); ax2.set_ylim(0, 0.15)
for s in ('top', 'right'):
    ax2.spines[s].set_visible(False)
grid_ax(ax)

ax = axs[1]
om = np.linspace(0.0, 0.999, 400)
for n1, col in ((0.5, GREEN), (1.25, BLUE), (2.0, ORANGE)):
    gg = T.rate_shape(om[None, :], np.array([[n1]]), np.array([[3.5]]), np.array([[0.75]]))[0]
    ax.plot(om, gg, color=col, lw=1.6, label=rf'$n_1$ = {n1:g}')
ax.plot(om, 1 - om, color=INK2, lw=1.0, ls='--', label='linear law')
ax.axvspan(R['chem']['min_omega'], 1.0, color=BLUE, alpha=0.08)
ax.text(0.80, 0.90, 'range in the\nmixing zone', color=BLUE, fontsize=7, ha='center')
ax.axvline(0.75, color=MUTED, lw=0.8, ls=':')
ax.text(0.75, 1.035, r'$\Omega_c$', color=MUTED, fontsize=7.5, ha='center', va='bottom')
for k, (lab, y) in {'LF': ('far', -0.06), 'LN': ('near', -0.06)}.items():
    ax.plot(P['lab'][k], np.full(8, 0.02), '|', color=RED if k == 'LF' else GREEN, ms=8, mew=1.6)
ax.text(0.22, 0.06, 'lab far', color=RED, fontsize=7, ha='center')
ax.text(0.78, 0.06, 'lab near', color=GREEN, fontsize=7, ha='center')
ax.set_xlim(0, 1); ax.set_ylim(0, 1.12)
ax.set_xlabel('saturation ratio Ω'); ax.set_ylabel('relative dissolution rate g(Ω)')
ax.legend(frameon=False, fontsize=7, loc='lower left', bbox_to_anchor=(0.20, 0.10))
ax.set_title(r'(b) rate laws with a kink ($n_2$ = 3.5, $\Omega_c$ = 0.75)', loc='left', fontsize=9)
grid_ax(ax)

ax = axs[2]
lk = G['logk']; Gk = G['G']
LKs = np.unique(lk)
lo = np.array([Gk[lk == v].min() for v in LKs]); hi = np.array([Gk[lk == v].max() for v in LKs])
md = np.array([np.median(Gk[lk == v]) for v in LKs])
ax.fill_between(LKs, lo, hi, color=BLUE, alpha=0.18, lw=0)
ax.plot(LKs, md, color=BLUE, lw=1.8, label='kinked laws (median, range)')
ax.plot(G['lin_k'], G['lin_G'], color=INK2, lw=1.1, ls='--', label='linear law')
ax.axhline(float(G['G_lea']), color=ORANGE, lw=1.4, label='local equilibrium')
ax.axhline(P['frac_lea'] * float(G['G_lea']), color=ORANGE, lw=0.8, ls=':')
ax.text(-5.9, P['frac_lea'] * float(G['G_lea']) * 0.82, '80 % of equilibrium', color=ORANGE, fontsize=7, va='top')
ax.set_yscale('log'); ax.set_ylim(0.2, 150)
ax.set_xlabel('log₁₀ κ (field rate prefactor, mmol/L/day)'); ax.set_ylabel('calcite dissolved (mol per m of coast per year)')
ax.legend(frameon=False, fontsize=7, loc='lower right')
ax.set_title('(c) kinetic and equilibrium regimes', loc='left', fontsize=9)
grid_ax(ax)
fig.text(0.5, 0.005, 'Fresh groundwater (log pCO₂ = −2.0) and intruded seawater (log pCO₂ = −2.5), both at calcite equilibrium, 15 °C; PHREEQC, phreeqc.dat. Dissolution in the first kilometre of the mixing zone.',
         ha='center', fontsize=7, color=MUTED)
fig.subplots_adjust(left=0.06, right=0.99, top=0.9, bottom=0.17)
fig.savefig(os.path.join(HERE, 'figT1_kinetics.png'), dpi=220)
plt.close(fig)

# ---------- Figure 2: designs ----------
D = R['designs']['base']
order = ['LF', 'LN', 'LS', 'F', 'F+LF', 'F+LN', 'F+LS']
lab = {'LF': 'lab\nfar', 'LN': 'lab\nnear', 'LS': 'lab\nspread', 'F': 'field\nwell', 'F+LF': 'well\n+ lab\nfar', 'F+LN': 'well\n+ lab\nnear', 'F+LS': 'well\n+ lab\nspread'}
col = {'LF': RED, 'LN': GREEN, 'LS': INK2, 'F': BLUE, 'F+LF': BLUE, 'F+LN': BLUE, 'F+LS': BLUE}
fig, axs = plt.subplots(1, 3, figsize=(10.2, 3.6), gridspec_kw=dict(width_ratios=[1.25, 1.25, 0.9], wspace=0.34))
ax = axs[0]
xx = np.arange(len(order))
ax.bar(xx, [100 * D[d]['correct_regime'] for d in order], 0.62, color=[col[d] for d in order])
ax.axhline(100 * R['prior']['correct_regime_prior'], color=MUTED, lw=0.9, ls=':')
for i, d in enumerate(order):
    ax.text(i, 100 * D[d]['correct_regime'] + 0.8, f"{100 * D[d]['correct_regime']:.1f}", ha='center', fontsize=6.5, color=INK2)
ax.set_xticks(xx); ax.set_xticklabels([lab[d] for d in order], fontsize=6.8)
ax.set_ylim(50, 102); ax.set_ylabel('correct decisions: is equilibrium adequate? (%)')
ax.set_title('(a) the goal', loc='left', fontsize=9)
grid_ax(ax)
ax = axs[1]
ax.bar(xx, [D[d]['info_gain_nats'] for d in order], 0.62, color=[col[d] for d in order])
for i, d in enumerate(order):
    ax.text(i, D[d]['info_gain_nats'] + 0.08, f"{D[d]['info_gain_nats']:.2f}", ha='center', fontsize=6.5, color=INK2)
ax.set_xticks(xx); ax.set_xticklabels([lab[d] for d in order], fontsize=6.8)
ax.set_ylabel('information about the rate law (nats)'); ax.set_ylim(0, 6.2)
ax.set_title('(b) the parameters', loc='left', fontsize=9)
grid_ax(ax)
ax = axs[2]
sig = [0.01, 0.02, 0.05]
for d, c, ls in (('F', BLUE, '-'), ('F+LN', GREEN, '--')):
    vals = [100 * R['designs'][k][d]['correct_regime'] for k in ('precise', 'base', 'coarse')]
    ax.plot(sig, vals, color=c, ls=ls, marker='o', ms=4, lw=1.5, label='field well' if d == 'F' else 'well + lab near')
ax.set_xscale('log'); ax.set_xticks(sig); ax.set_xticklabels(['0.01', '0.02', '0.05']); ax.minorticks_off()
ax.set_xlabel('error of the calcium excess (mmol/L)'); ax.set_ylabel('correct decisions (%)')
ax.set_ylim(80, 100)
ax.legend(frameon=False, fontsize=7, loc='lower left')
ax.set_title('(c) precision of the field data', loc='left', fontsize=9)
grid_ax(ax)
fig.text(0.5, 0.005, f"Dotted line in (a): no data (prior). {P['ndraw']} noisy data sets for each of the {len(G['G'])} prior parameter sets; lab rates ±20 % with an unknown laboratory prefactor; field error 0.02 mmol/L in (a) and (b).",
         ha='center', fontsize=7, color=MUTED)
fig.subplots_adjust(left=0.06, right=0.99, top=0.9, bottom=0.23)
fig.savefig(os.path.join(HERE, 'figT2_design.png'), dpi=220)
plt.close(fig)
print('figures written')
