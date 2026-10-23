"""Figures of QENDRESA-GO: figQ1_mechanism.png (why hazard MSMs are hard), figQ2_montecarlo.png (estimating the
marginal hazard ratio), figQ3_design.png (choosing a dynamic pumping rule under a risk budget)."""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(sys.argv[1] if len(sys.argv) > 1 else HERE)
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False})
MCJ = json.load(open('qendresa_mc.json'))
MC, TAUS, BUDGET = MCJ['results'], np.array(MCJ['taus']), MCJ['budget']
CV = json.load(open('qendresa_curve.json')) if os.path.exists('qendresa_curve.json') else None
INK, GRID = '#0b0b0b', '#e5e4df'
COL = {'frugal': '#e34948', 'twostep': '#a3a19a', 'ipw': '#2a78d6', 'gform': '#6250d6', 'frugal_safe': '#1baf7a'}
NAME = {'frugal': 'frugal MLE (joint)', 'twostep': 'frugal, two-step shortcut', 'ipw': 'IPW hazard MSM',
        'gform': 'parametric g-formula', 'frugal_safe': 'frugal, safe (upper bound)'}
METH = ['frugal', 'twostep', 'ipw', 'gform']
MINUS = lambda s: s.replace('-', '−')

# ---------------------------------------------------------------- figure 1: the mechanism
if CV is not None:
    fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.7), gridspec_kw=dict(width_ratios=[1.0, 1.0, 1.05]))
    k = np.arange(0, 6)
    nv = CV['naive']
    for key, lab, col, ls in (('true_always', 'always pump: causal', COL['frugal'], '-'),
                              ('always', 'wells that always pumped: observed', COL['frugal'], '--'),
                              ('true_never', 'never pump: causal', COL['ipw'], '-'),
                              ('never', 'wells that never pumped: observed', COL['ipw'], '--')):
        ax[0].plot(k, [1.0] + list(nv[key]), color=col, ls=ls, lw=1.8, marker='o', ms=3.2, label=lab)
    ax[0].set_xlabel('season'); ax[0].set_ylabel('share of wells still fresh')
    ax[0].set_ylim(0.38, 1.02)
    ax[0].legend(frameon=False, fontsize=6.4, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
    ax[0].set_title('(a) confounding reverses the effect', fontsize=9)

    nc = CV['noncoll']
    m = np.array(nc['m'])
    shades = ['#f2b8b5', '#e98a85', '#e34948', '#b3302f', '#7a1f1e']
    for c, col in zip(nc['curves'], shades):
        ax[1].plot(m, c['contrast'], color=col, lw=1.6, label=f'season {c["k"]}')
    ax[1].axhline(nc['beta'], color=INK, lw=0.9, ls=':', label=f'marginal β = {nc["beta"]}')
    ax[1].set_xlabel(r'dryness index of the well, $m_k=\rho\,(W_1+\dots+W_k)$')
    ax[1].set_ylabel('conditional log hazard ratio of pumping')
    ax[1].legend(frameon=False, fontsize=6.4, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3)
    ax[1].set_title('(b) the hazard ratio is not collapsible', fontsize=9)

    lim = CV['limits']
    labs = ['frugal', 'twostep', 'ipw', 'gform']
    y = np.arange(len(labs))[::-1]
    for sc, mk, off in (('null', 'o', 0.13), ('correct', 's', -0.13)):
        tr = np.array(lim[sc]['truth'])
        for j, (lb, yy) in enumerate(zip(labs, y)):
            est = np.array(lim[sc][lb])
            ax[2].plot(est[2] - tr[2], yy + off, marker=mk, color=COL[lb], ms=5.5, ls='none')
            ax[2].plot(est[3] - tr[3], yy + off, marker=mk, mfc='white', mec=COL[lb], mew=1.4, ms=5.5, ls='none')
    ax[2].axvline(0, color=INK, lw=0.8, ls=':')
    ax[2].set_yticks(y); ax[2].set_yticklabels([NAME[lb] for lb in labs], fontsize=7)
    ax[2].set_xlabel('limit minus truth (n = 400 000)')
    h = [plt.Line2D([], [], color='#555', marker='o', ls='none', ms=5, label='β, no effect'),
         plt.Line2D([], [], color='#555', marker='o', mfc='white', ls='none', ms=5, label=r'$\beta_\ell$ (lag), no effect'),
         plt.Line2D([], [], color='#555', marker='s', ls='none', ms=5, label='β, with effect'),
         plt.Line2D([], [], color='#555', marker='s', mfc='white', ls='none', ms=5, label=r'$\beta_\ell$, with effect')]
    ax[2].legend(handles=h, frameon=False, fontsize=6.4, loc='upper center', bbox_to_anchor=(0.4, -0.2), ncol=2)
    ax[2].set_title('(c) where each estimator converges', fontsize=9)
    fig.tight_layout(); fig.subplots_adjust(bottom=0.33); fig.savefig('figQ1_mechanism.png', dpi=200); plt.close(fig)

# ---------------------------------------------------------------- figure 2: Monte Carlo of the hazard MSM
SC = [('correct_n1000', 'correct model, n = 1000'), ('correct_n4000', 'correct model, n = 4000'),
      ('weak_n4000', 'weak overlap, n = 4000'), ('tcop_n4000', 'Student-t copula, n = 4000'),
      ('null_n4000', 'no effect, n = 4000'), ('null_n16000', 'no effect, n = 16 000')]
SC = [s for s in SC if s[0] in MC]
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.9), gridspec_kw=dict(width_ratios=[1.2, 1.0, 1.0]))
y = np.arange(len(SC))[::-1]
off = np.linspace(-0.27, 0.27, len(METH))
for j, mth in enumerate(METH):
    for c, (par, mk) in enumerate(((2, 'o'), (3, '^'))):
        ax[c].scatter([min(MC[k][mth]['rmse'][par], 0.33) for k, _ in SC], y + off[j], color=COL[mth], s=18, marker=mk,
                      label=NAME[mth] if c == 0 else None, zorder=3)
for a, tt in zip(ax[:2], ('(a) error of β (current pumping)', r'(b) error of $\beta_\ell$ (pumping last season)')):
    a.set_yticks(y); a.set_ylim(-0.6, len(SC) - 0.4); a.set_xlim(0, 0.34)
    for yy in y[:-1]:
        a.axhline(yy - 0.5, color=GRID, lw=0.6, zorder=0)
    a.set_xlabel('root mean squared error (1000 data sets)')
    a.set_title(tt, fontsize=9)
ax[0].set_yticklabels([l for _, l in SC], fontsize=7)
ax[1].set_yticklabels([])
ax[0].legend(frameon=False, fontsize=6.4, loc='upper center', bbox_to_anchor=(0.75, -0.16), ncol=4)
# (c) coverage of beta and beta_l
for j, mth in enumerate(METH):
    ax[2].scatter([MC[k][mth]['cover'][2] for k, _ in SC], y + off[j], color=COL[mth], s=18, marker='o', zorder=3)
    ax[2].scatter([MC[k][mth]['cover'][3] for k, _ in SC], y + off[j], facecolor='white', edgecolor=COL[mth], s=18,
                  marker='^', lw=1.2, zorder=3)
ax[2].axvline(0.95, color=INK, lw=0.7, ls=':')
ax[2].set_yticks(y); ax[2].set_yticklabels([]); ax[2].set_ylim(-0.6, len(SC) - 0.4); ax[2].set_xlim(-0.03, 1.03)
for yy in y[:-1]:
    ax[2].axhline(yy - 0.5, color=GRID, lw=0.6, zorder=0)
ax[2].set_xlabel(r'95% coverage (● $\beta$, △ $\beta_\ell$)')
ax[2].set_title('(c) honesty of the intervals', fontsize=9)
fig.tight_layout(); fig.subplots_adjust(bottom=0.24); fig.savefig('figQ2_montecarlo.png', dpi=200); plt.close(fig)

# ---------------------------------------------------------------- figure 3: choosing a rule
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.8), gridspec_kw=dict(width_ratios=[1.05, 1.0, 1.0]))
key = 'correct_n1000' if 'correct_n1000' in MC else [k for k in MC if MC[k]['rules']][0]
r = MC[key]
tr = np.array(r['rules_truth'])
ax[0].plot(TAUS, tr[:, 0], color=INK, lw=1.8, label='truth')
for mth, dx in (('frugal', -0.03), ('ipw', 0.0), ('gform', 0.03)):
    mu, sd = np.array(r['rules'][mth]['risk_mean']), np.array(r['rules'][mth]['risk_sd'])
    ax[0].errorbar(TAUS + dx, mu, yerr=1.96 * sd, color=COL[mth], fmt='o', ms=3, lw=1.0, capsize=1.5, label=NAME[mth])
ax[0].axhline(BUDGET, color=COL['frugal_safe'], lw=1.0, ls='--', label=f'risk budget {BUDGET:.2f}')
ax[0].set_xlabel(r'rule: pump unless dryness $L_k\geq\tau$')
ax[0].set_ylabel('risk of salinization within 5 seasons')
ax[0].legend(frameon=False, fontsize=6.4, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
ax[0].set_title(f'(a) risk of each rule, n = {r["n"]} (bars: 95% of data sets)', fontsize=9)
ax[0].set_xticks(TAUS[::2]); ax[0].set_xticklabels([MINUS(f'{t:g}') for t in TAUS[::2]])

for kk, ls in (('correct_n1000', '-'), ('correct_n4000', '--')):
    if kk not in MC:
        continue
    for mth in ('frugal', 'ipw', 'gform'):
        ax[1].plot(TAUS, MC[kk]['rules'][mth]['risk_rmse'], color=COL[mth], ls=ls, lw=1.6, marker='o', ms=2.5,
                   label=f'{NAME[mth]}, n = {MC[kk]["n"]}')
ax[1].set_xlabel('rule threshold τ'); ax[1].set_ylabel('root mean squared error of the risk')
ax[1].set_ylim(bottom=0)
ax[1].legend(frameon=False, fontsize=6.0, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
ax[1].set_title('(b) error of the estimated risk', fontsize=9)
ax[1].set_xticks(TAUS[::2]); ax[1].set_xticklabels([MINUS(f'{t:g}') for t in TAUS[::2]])

rows = [k for k in ('correct_n1000', 'correct_n4000', 'weak_n4000', 'tcop_n4000') if k in MC and MC[k]['rules']]
lbl = {'correct_n1000': 'correct, n = 1000', 'correct_n4000': 'correct, n = 4000', 'weak_n4000': 'weak overlap',
       'tcop_n4000': 'Student-t copula'}
RM = ['frugal', 'frugal_safe', 'ipw', 'gform']
yy = np.arange(len(rows))[::-1]
offs = np.linspace(-0.27, 0.27, len(RM))
for j, mth in enumerate(RM):
    vals = [MC[k]['rules'].get(mth, {}).get('violate', np.nan) for k in rows]
    ax[2].barh(yy + offs[j], vals, height=0.16, color=COL[mth], label=NAME[mth])
    for yv, v in zip(yy + offs[j], vals):
        if np.isfinite(v):
            ax[2].text(v + 0.006, yv, f'{v:.2f}', va='center', fontsize=5.8, color='#3a3a3a')
ax[2].set_yticks(yy); ax[2].set_yticklabels([lbl[k] for k in rows], fontsize=7)
ax[2].set_xlabel('share of data sets breaking the budget')
ax[2].set_xlim(0, max(0.5, ax[2].get_xlim()[1]))
ax[2].legend(frameon=False, fontsize=6.2, loc='upper center', bbox_to_anchor=(0.35, -0.2), ncol=2)
ax[2].set_title('(c) how often the chosen rule is unsafe', fontsize=9)
fig.tight_layout(); fig.subplots_adjust(bottom=0.33); fig.savefig('figQ3_design.png', dpi=200); plt.close(fig)
print('figures written')
