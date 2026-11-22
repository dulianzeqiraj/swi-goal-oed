"""Figures of BESA-GO: figB1_path.png (bias and power along a path of copulas) and figB2_scenarios.png (Monte Carlo)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import chi2, ncx2

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False})
MC = json.load(open('besa_mc.json'))['results']
CV = json.load(open('besa_curve.json'))
INK, INK2 = '#0b0b0b', '#52514e'
COL = {'mle_common': '#a3a19a', 'mle_flex': '#2a78d6', 'drf_flex': '#1baf7a', 'dr_linear': '#6250d6', 'ipw': '#eb6834',
       'besa': '#e34948'}
NAME = {'mle_common': 'frugal MLE, common copula', 'mle_flex': 'frugal MLE, pumping-dependent copula',
        'drf_flex': 'frugal-augmented DR', 'dr_linear': 'DR, linear regressions', 'ipw': 'IPW', 'besa': 'BESA procedure'}
TH2 = CV['truth'][1]
Q = chi2.ppf(0.95, 2)

# ---------------------------------------------------------------- figure 1: along the path of copulas
G = np.array([c['gap'] for c in CV['curve']])
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.9), gridspec_kw=dict(width_ratios=[1.05, 1.05, 1.0]))
for key, lab, col, ls in (('mle_common', 'MLE, common copula', COL['mle_common'], '-'),
                          ('mle_flex', 'MLE, pumping-dependent copula', COL['mle_flex'], '-'),
                          ('drf_common', 'augmented DR, common copula', COL['drf_flex'], '--')):
    ax[0].plot(G, [c[key][1] for c in CV['curve']], color=col, lw=2.0 if key != 'drf_common' else 1.5, ls=ls, marker='o', ms=3.5, label=lab)
ax[0].axhline(TH2, color=INK, lw=0.8, ls=':', label=f'true θ₂ = {TH2}')
for k, g, mk in (('correct_n6000', 0.0, 's'), ('pumpdep_n6000', 0.5, 's')):
    if k in MC:
        ax[0].plot(g, MC[k]['mle_common']['mean'][1], marker=mk, ms=6, mfc='white', mec=COL['mle_common'], mew=1.4, ls='none')
ax[0].set_xlabel('pumping effect on the copula, ρ₂(1) − ρ₂(0)')
ax[0].set_ylabel('limit of the estimate of θ₂')
ax[0].legend(frameon=False, fontsize=6.4, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
ax[0].set_title('(a) a common copula biases the effect', fontsize=9)

ng = np.linspace(0, G.max(), 61)
kH = np.interp(ng, G, [max(c['kappa_hausman'], 0) for c in CV['curve']])
kL = np.interp(ng, G, [max(c['kappa_lr'], 0) for c in CV['curve']])
for n, ls in ((1500, '--'), (6000, '-')):
    ax[1].plot(ng, ncx2.sf(Q, 2, n * kH + 1e-12), color=COL['drf_flex'], ls=ls, lw=1.8, label=f'Hausman check, n = {n}')
    ax[1].plot(ng, ncx2.sf(Q, 2, n * kL + 1e-12), color=COL['mle_flex'], ls=ls, lw=1.8, label=f'likelihood-ratio check, n = {n}')
for k, g in (('correct_n1500', 0.0), ('correct_n6000', 0.0), ('pumpdep_n1500', 0.5), ('pumpdep_n6000', 0.5)):
    if k in MC:
        ax[1].plot(g, MC[k]['tests']['hausman_common'], marker='o', ms=5, mfc='white', mec=COL['drf_flex'], mew=1.3, ls='none')
        ax[1].plot(g, MC[k]['tests']['lr'], marker='o', ms=5, mfc='white', mec=COL['mle_flex'], mew=1.3, ls='none')
ax[1].axhline(0.05, color=INK, lw=0.7, ls=':')
ax[1].set_ylim(0, 1.03)
ax[1].set_xlabel('pumping effect on the copula, ρ₂(1) − ρ₂(0)')
ax[1].set_ylabel('probability of detecting it (5% tests)')
ax[1].legend(frameon=False, fontsize=6.6, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
ax[1].set_title('(b) power of the two checks (circles: Monte Carlo)', fontsize=9)

# (c) relative efficiency at the correct model: variance of DR / variance of MLE along the path
ax[2].plot(G, [(c['se1_drf'][1] / c['se1_common'][1]) ** 2 for c in CV['curve']], color=COL['drf_flex'], lw=1.8, marker='o', ms=3.5)
ax[2].axhline(1, color=INK, lw=0.7, ls=':')
ax[2].set_xlabel('pumping effect on the copula, ρ₂(1) − ρ₂(0)')
ax[2].set_ylabel('Var(doubly robust) / Var(frugal MLE), θ₂')
ax[2].set_title('(c) the price of robustness', fontsize=9)
fig.tight_layout(); fig.subplots_adjust(bottom=0.3); fig.savefig('figB1_path.png', dpi=200); plt.close(fig)

# ---------------------------------------------------------------- figure 2: the Monte Carlo scenarios
SC = [('correct_n1500', 'correct model, n = 1500'), ('correct_n6000', 'correct model, n = 6000'),
      ('pumpdep_n1500', 'pumping-dependent copula, n = 1500'), ('pumpdep_n6000', 'pumping-dependent copula, n = 6000'),
      ('pumpdep_null_n6000', 'the same, no effect, n = 6000'), ('wrongprop_n1500', 'wrong propensity model, n = 1500'),
      ('wrongprop_n6000', 'wrong propensity model, n = 6000'), ('both_n6000', 'both wrong, n = 6000'),
      ('skewdry_n6000', 'skewed dryness copula, n = 6000')]
SC = [s for s in SC if s[0] in MC]
METH = ['mle_common', 'mle_flex', 'drf_flex', 'dr_linear', 'ipw', 'besa']
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.9), gridspec_kw=dict(width_ratios=[1.15, 1.0, 0.85]))
y = np.arange(len(SC))[::-1]
off = np.linspace(-0.3, 0.3, len(METH))
for j, m in enumerate(METH):
    ax[0].scatter([MC[k][m]['rmse'][1] for k, _ in SC], y + off[j], color=COL[m], s=16 if m != 'besa' else 26,
                  marker='o' if m != 'besa' else 'D', label=NAME[m], zorder=3)
    ax[1].scatter([MC[k][m]['cover'][1] for k, _ in SC], y + off[j], color=COL[m], s=16 if m != 'besa' else 26,
                  marker='o' if m != 'besa' else 'D', zorder=3)
for a in ax[:2]:
    a.set_yticks(y); a.set_ylim(-0.6, len(SC) - 0.4)
    for yy in y[:-1]:
        a.axhline(yy - 0.5, color='#e5e4df', lw=0.6, zorder=0)
ax[0].set_yticklabels([l for _, l in SC], fontsize=7)
ax[1].set_yticklabels([])
ax[0].set_xlabel('root mean squared error of θ₂ (1000 data sets)')
ax[0].set_title('(a) error of the season-2 effect', fontsize=9)
ax[1].axvline(0.95, color=INK, lw=0.7, ls=':')
ax[1].set_xlabel('coverage of the 95% interval for θ₂')
ax[1].set_title('(b) honesty of the intervals', fontsize=9)
ax[0].legend(frameon=False, fontsize=6.2, loc='upper center', bbox_to_anchor=(0.55, -0.16), ncol=3)
BR = ['common MLE', 'pumping-dependent MLE', 'DR (common)', 'DR (pumping-dependent)']
BC = ['#a3a19a', '#2a78d6', '#9fd8c3', '#1baf7a']
left = np.zeros(len(SC))
for b in range(4):
    v = np.array([MC[k]['tests']['branch'][b] for k, _ in SC])
    ax[2].barh(y, v, left=left, color=BC[b], height=0.62, label=BR[b], edgecolor='white', linewidth=0.8)
    left += v
ax[2].set_yticks(y); ax[2].set_yticklabels([]); ax[2].set_xlim(0, 1)
ax[2].set_xlabel('share of data sets')
ax[2].set_title('(c) what the BESA procedure reported', fontsize=9)
ax[2].legend(frameon=False, fontsize=6.2, loc='upper center', bbox_to_anchor=(0.5, -0.16), ncol=2)
fig.tight_layout(); fig.subplots_adjust(bottom=0.27); fig.savefig('figB2_scenarios.png', dpi=200); plt.close(fig)
print('figures written')
