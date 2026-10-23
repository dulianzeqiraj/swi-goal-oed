"""Figures of BARASPESHA-GO: figB1_estimators.png (the undersmoothing identity and the Monte Carlo of the estimators)
and figB2_design.png (goal-oriented choice of the wells to measure)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, NullFormatter

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False})
D = json.load(open('baraspesha.json'))
G = json.load(open('baraspesha_design.json'))
INK, GRID = '#0b0b0b', '#e5e4df'
C_NOM, C_CAL, C_GEN, C_AUG, C_BAR = '#6250d6', '#7a7872', '#eb6834', '#2a78d6', '#e34948'
SC = ['S1', 'S2', 'S3', 'S4', 'S5']
SC_LAB = ['baseline', 'weak\noverlap', 'structural\nerror', 'near-correct\nsimulator', 'small field\n(n = 150)']

# ---------------------------------------------------------------- figure 1
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.7), gridspec_kw=dict(width_ratios=[1.0, 1.1, 1.1]))
sp = D['A']['spectrum']
d = np.array(sp['d'])
ax[0].plot(d, sp['ridge_lambda'], color=C_AUG, lw=1.8, label=r'outcome ridge, $\lambda$ = %g' % sp['lam'])
ax[0].plot(d, sp['ridge_delta'], color='#1baf7a', lw=1.8, label=r'weighting ridge, $\delta$ = %g' % sp['delta'])
ax[0].plot(d, sp['augmented'], color=C_BAR, lw=2.2, label='augmented estimator')
ax[0].set_xscale('log'); ax[0].set_ylim(0, 1.03)
ax[0].set_xlabel('eigenvalue d of the Gram matrix')
ax[0].set_ylabel('shrinkage of the OLS coefficient')
ax[0].legend(frameon=False, fontsize=6.6, loc='lower right')
ax[0].set_title('(a) ridge + ridge = one undersmoothed ridge', fontsize=9)

x = np.arange(len(SC))
meth = [('sim_nominal', 'nominal simulator', C_NOM, 'v'), ('sim_calib', 'calibrated simulator', C_CAL, 's'),
        ('aug_generic', 'AutoDML, generic kernel', C_GEN, 'D'), ('aug_sim', 'simulator + generic weights', C_AUG, '^'),
        ('baraspesha', 'BARASPESHA-GO', C_BAR, 'o')]
off = np.linspace(-0.24, 0.24, len(meth))
for (k, lab, col, mk), o in zip(meth, off):
    ax[1].plot(x + o, [D['B'][s][k]['rmse'] for s in SC], mk, color=col, ms=5.2, label=lab)
ax[1].set_yscale('log')
ax[1].set_xticks(x); ax[1].set_xticklabels(SC_LAB, fontsize=6.8)
ax[1].set_ylabel(r'root mean squared error of $\psi$ (log$_{10}$ mg/L)')
ax[1].grid(axis='y', color=GRID, lw=0.6, which='both')
ax[1].legend(frameon=False, fontsize=6.4, loc='upper center', bbox_to_anchor=(0.5, -0.24), ncol=2)
ax[1].set_title('(b) accuracy in five scenarios', fontsize=9)

meth2 = [('sim_calib', 'calibrated simulator', C_CAL, 's'), ('aug_generic', 'AutoDML, generic kernel', C_GEN, 'D'),
         ('aug_sim', 'simulator + generic weights', C_AUG, '^'), ('baraspesha_wald', 'BARASPESHA-GO, Wald', '#f0a3a2', 'o'),
         ('baraspesha', 'BARASPESHA-GO, bias-aware', C_BAR, 'o')]
off = np.linspace(-0.24, 0.24, len(meth2))
for (k, lab, col, mk), o in zip(meth2, off):
    ax[2].plot(x + o, [D['B'][s][k]['cover'] for s in SC], mk, color=col, ms=5.2, label=lab)
ax[2].axhline(0.95, color=INK, lw=0.8, ls=':')
ax[2].set_ylim(0.4, 1.02)
ax[2].set_xticks(x); ax[2].set_xticklabels(SC_LAB, fontsize=6.8)
ax[2].set_ylabel('coverage of the 95% interval')
ax[2].grid(axis='y', color=GRID, lw=0.6)
ax[2].legend(frameon=False, fontsize=6.4, loc='upper center', bbox_to_anchor=(0.5, -0.24), ncol=2)
ax[2].set_title('(c) honesty of the intervals', fontsize=9)
fig.tight_layout(); fig.subplots_adjust(bottom=0.33); fig.savefig('figB1_estimators.png', dpi=200); plt.close(fig)

# ---------------------------------------------------------------- figure 2
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.9), gridspec_kw=dict(width_ratios=[1.1, 1.0, 1.0]))
E = D['example']
xw = np.array(E['xw']) / 1000; yy = np.array(E['y']); A = np.array(E['A'])
h0 = ax[0].scatter(xw[A == 0], yy[A == 0], s=7, color='#c9c6bf', lw=0, label='control well (not measured)')
h1 = ax[0].scatter(xw[A == 1], yy[A == 1], s=9, marker='x', color=INK, lw=0.7, label='treated well (pumping cut)')
gsel = np.array(E['goal']); nsel = np.array(E['nearest'])
h2 = ax[0].scatter(xw[nsel], yy[nsel], s=34, facecolors='none', edgecolors=C_AUG, lw=0.9, marker='s', label='measured: matching (40)')
h3 = ax[0].scatter(xw[gsel], yy[gsel], s=18, color=C_BAR, lw=0, label='measured: goal-oriented (40)')
ax[0].set_xscale('log')
ax[0].set_xticks([0.25, 0.5, 1, 2, 4])
ax[0].xaxis.set_major_formatter(FormatStrFormatter('%g')); ax[0].xaxis.set_minor_formatter(NullFormatter())
ax[0].set_xlabel('distance of the well from the coast (km)')
ax[0].set_ylabel('position along the coast (km)')
ax[0].set_title('(a) which control wells to measure', fontsize=9)

DS = [('random', 'random', '#a3a19a', 'v'), ('space_filling', 'space-filling', '#4e4c48', 'D'),
      ('nearest', 'matching to treated', C_AUG, 's'), ('calib_D', 'calibration-optimal (D)', '#1baf7a', '^'),
      ('goal', 'goal-oriented (BARASPESHA)', C_BAR, 'o')]
for k, (sk, title) in enumerate((('S1', '(b) baseline field'), ('S3', '(c) structural error'))):
    tab = G['C'][sk]['table']
    for key, lab, col, mk in DS:
        ms = [r['m'] for r in tab if r['design'] == key]
        rm = [r['rmse'] for r in tab if r['design'] == key]
        ax[k + 1].plot(ms, rm, '-' + mk, color=col, lw=1.5, ms=4.5, label=lab)
    ax[k + 1].axhline(D['B'][sk]['baraspesha']['rmse'], color=INK, lw=0.8, ls=':', label='all control wells measured')
    ax[k + 1].set_xticks(G['budgets'])
    ax[k + 1].set_xlabel('number of control wells measured')
    ax[k + 1].set_ylabel(r'root mean squared error of $\psi$')
    ax[k + 1].set_ylim(0, None)
    ax[k + 1].grid(axis='y', color=GRID, lw=0.6)
    ax[k + 1].set_title(title, fontsize=9)
fig.legend(handles=[h0, h1, h2, h3], frameon=False, fontsize=6.6, loc='lower center', bbox_to_anchor=(0.19, 0.0), ncol=2)
hh, ll = ax[1].get_legend_handles_labels()
fig.legend(hh, ll, frameon=False, fontsize=6.6, loc='lower center', bbox_to_anchor=(0.69, 0.0), ncol=3)
fig.tight_layout(rect=(0, 0.13, 1, 1)); fig.savefig('figB2_design.png', dpi=200); plt.close(fig)
print('figures written')
