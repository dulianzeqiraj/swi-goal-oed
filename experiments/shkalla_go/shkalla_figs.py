"""Figures of SHKALLA-GO: figS1_chemistry.png (mixing lines and rate laws) and figS2_design.png (designs)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shkalla as S

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False})
TAB = S.load_table(); REF = TAB['ref_la']; LKSP = REF.sum()
RS = json.load(open('shkalla_results.json'))
C_NAT, C_BAR, C_TST = '#1D4ED8', '#C2410C', '#6B7280'

# ---------------------------------------------------------------- figure 1: chemistry and rate laws
fig, ax = plt.subplots(1, 3, figsize=(10.4, 3.3))
F = TAB['F']
for L, col, lab in (('nat', C_NAT, 'natural mixing (fresh groundwater + seawater)'),
                    ('bar', C_BAR, 'barrier (injected water + seawater)')):
    om = 10 ** TAB[f'lom_{L}'][:, 0]
    r = 10 ** (TAB[f'la_{L}'][0, :, 0] - TAB[f'la_{L}'][1, :, 0])
    ax[0].plot(F, om, color=col, lw=1.8, label=lab)
    ax[1].plot(F, r, color=col, lw=1.8)
ax[0].set_xlabel('seawater fraction f'); ax[0].set_ylabel('calcite saturation ratio Ω (before reaction)')
ax[0].set_ylim(0, 1.05); ax[0].legend(frameon=False, fontsize=7, loc='lower right')
ax[0].set_title('(a) undersaturation of the mixtures', fontsize=9)
ax1b = ax[1].twinx()
mg = 10 ** TAB['la_nat'][2, :, 0]
ax1b.plot(F, mg, color='#059669', lw=1.2, ls='--'); ax1b.set_ylabel('Mg²⁺ activity (mmol), dashed', color='#059669')
ax1b.spines['top'].set_visible(False)
ax[1].set_yscale('log'); ax[1].set_xlabel('seawater fraction f'); ax[1].set_ylabel('activity ratio r = a(Ca²⁺)/a(CO₃²⁻)')
ax[1].set_title('(b) composition along the mixing lines', fontsize=9)
# rate laws for one parameter set in four waters
om = np.linspace(0.05, 0.99, 120)
psi, w, KM, KS = 1.0, 0.5, 1.0, 1.0
waters = [('dilute, r = 50', 0.0, 0.0, 50.0, '#111827', '-'), ('dilute, r = 1 000', 0.0, 0.0, 1000.0, '#111827', '--'),
          ('20% seawater, r = 500', RS['mg_mix'], RS['so4_mix'], 500.0, '#059669', '-'),
          ('seawater, r = 1 500', RS['mg_sea'], RS['so4_sea'], 1500.0, '#7C3AED', '-')]
for lab, mgv, so4, r, col, ls in waters:
    la = np.array([0.5 * (np.log10(om) + LKSP + np.log10(r)), 0.5 * (np.log10(om) + LKSP - np.log10(r)),
                   np.full_like(om, np.log10(max(mgv, 1e-12))), np.full_like(om, np.log10(max(so4, 1e-12))), np.log10(om)])
    ax[2].plot(om, -S.graph_shape(la, psi, w, KM, KS, REF), color=col, ls=ls, lw=1.6, label=lab)
ax[2].plot(om, (1 - om) * 0.5, color=C_TST, lw=1.2, ls=':', label='law in Ω alone (n = 1)')
ax[2].set_yscale('log'); ax[2].set_xlabel('saturation ratio Ω'); ax[2].set_ylabel('dissolution rate / prefactor')
ax[2].set_title('(c) one surface mechanism, four waters', fontsize=9)
ax[2].legend(frameon=False, fontsize=6.6, loc='lower left')
fig.tight_layout()
fig.savefig('figS1_chemistry.png', dpi=200)
plt.close(fig)

# ---------------------------------------------------------------- figure 2: designs
D = RS['designs']; names = list(D)
short = {'field only': 'field\nonly', 'dilute series': 'dilute\nseries', 'seawater series': 'seawater\nseries',
         'dilute + seawater': 'dilute\n+ sea', 'scenario waters': 'scenario\nwaters',
         'parameter-optimal': 'param.\noptimal', 'goal-optimal': 'goal\noptimal'}
x = np.arange(len(names))
fig, ax = plt.subplots(1, 3, figsize=(10.4, 3.4))
eg = [10 ** D[n]['graph']['med_abs_err'] for n in names]; et = [10 ** D[n]['tst']['med_abs_err'] for n in names]
qg = [10 ** D[n]['graph']['q90_abs_err'] for n in names]; qt = [10 ** D[n]['tst']['q90_abs_err'] for n in names]
ax[0].bar(x - 0.2, eg, 0.38, color=C_BAR, label='graph law (median)')
ax[0].bar(x + 0.2, et, 0.38, color=C_TST, label='law in Ω alone (median)')
ax[0].scatter(x - 0.2, qg, color=C_BAR, marker='v', s=14, zorder=3, label='90th percentile')
ax[0].scatter(x + 0.2, qt, color=C_TST, marker='v', s=14, zorder=3)
ax[0].set_yscale('log'); ax[0].set_ylabel('error factor of the predicted barrier dissolution')
ax[0].set_xticks(x); ax[0].set_xticklabels([short[n] for n in names], fontsize=6.6)
ax[0].legend(frameon=False, fontsize=6.6); ax[0].set_title('(a) prediction error for the goal', fontsize=9)
rk = [D[n]['algebra']['rank_V'] for n in names]; jr = [D[n]['algebra']['jac_rank_shape'] for n in names]
dl = [D[n]['algebra']['defect'] for n in names]
ax[1].bar(x - 0.2, rk, 0.38, color='#1F2937', label='rank of the monomial matrix V (of 7)')
ax[1].bar(x + 0.2, jr, 0.38, color='#9CA3AF', label='rank of the shape Jacobian (of 4)')
for xi in x:
    ax[1].text(xi - 0.2, rk[xi] + 0.12, f'{dl[xi]:.2f}', ha='center', fontsize=6.4, color='#B91C1C')
ax[1].set_ylim(0, 8.6); ax[1].set_ylabel('rank')
ax[1].set_xticks(x); ax[1].set_xticklabels([short[n] for n in names], fontsize=6.6)
ax[1].legend(frameon=False, fontsize=6.4, loc='upper left')
ax[1].set_title('(b) algebra: ranks (red: goal span defect)', fontsize=9)
cg = [D[n]['graph']['cover90'] for n in names]; ct = [D[n]['tst']['cover90'] for n in names]
ax[2].bar(x - 0.2, cg, 0.38, color=C_BAR, label='graph law'); ax[2].bar(x + 0.2, ct, 0.38, color=C_TST, label='law in Ω alone')
ax[2].axhline(0.9, color='#111827', lw=0.8, ls='--')
ax[2].set_ylim(0, 1.22); ax[2].set_ylabel('coverage of 90% intervals')
ax[2].set_xticks(x); ax[2].set_xticklabels([short[n] for n in names], fontsize=6.6)
ax[2].legend(frameon=False, fontsize=6.6, loc='upper center', ncol=2); ax[2].set_title('(c) honesty of the uncertainty', fontsize=9)
fig.tight_layout()
fig.savefig('figS2_design.png', dpi=200)
plt.close(fig)
print('figures written')
