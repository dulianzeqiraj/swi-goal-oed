"""Figures of ZGJEDHJA-GO: figZ1_identified.png (what the data identify) and figZ2_design.png (goal-oriented
monitoring)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker
import zgjedhja_model as Z
import zgjedhja_ident as I

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False})
D = json.load(open('zgjedhja.json'))
INK, GRID = '#0b0b0b', '#e5e4df'
C_FEE, C_REC, C_PHYS, C_SURV, C_NAIVE = '#e34948', '#2a78d6', '#1baf7a', '#eb6834', '#6250d6'
tr = D['truth']

# ---------------------------------------------------------------- figure 1: identification
P1 = np.array(tr['ccp'])
T = I.tables(P1, Z.F_TRUE, I.Q_GRID, np.round(np.linspace(-4, 0, 81), 6))
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.9), gridspec_kw=dict(width_ratios=[1.0, 1.05, 1.15]))
q = T['q']
ax[0].axvspan(*D['q_phys'], color=C_PHYS, alpha=0.13, lw=0, label='physics range of q')
ax[0].plot(q, 100 * T['g1'], color=C_FEE, lw=2.0, label='fee effect implied by the data, given q')
ax[0].axhline(0, color=INK, lw=0.6)
ax[0].plot(tr['q'], 100 * tr['fee'], 'o', color=INK, ms=5, label='truth')
ax[0].plot(0, 0, 's', color=C_NAIVE, ms=6, label='naive analysis (q = 0)')
ax[0].set_xlabel('anticipated intrusion probability at the frontier, q')
ax[0].set_ylabel('fall in 10-season salinization risk from the fee (%)')
ax[0].legend(frameon=False, fontsize=6.4, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
ax[0].set_title('(a) the fee effect depends on q only', fontsize=9)

feas = (T['th4'] <= T['th3']) & (T['th4'] >= I.THETA_MIN)
Qm, Wm = np.meshgrid(T['q'], T['w'], indexing='ij')
ax[1].contourf(Qm, Wm, feas.astype(float), levels=[0.5, 1.5], colors=['#f3f1ec'])
cs = ax[1].contour(Qm, Wm, np.where(feas, T['g2'], np.nan), levels=[0.2, 0.3, 0.4, 0.5, 0.6], colors=C_REC, linewidths=1.1)
ax[1].clabel(cs, fontsize=6.5, fmt='%.1f')
ax[1].axvspan(*D['q_phys'], color=C_PHYS, alpha=0.13, lw=0)
sv = I.survey_interval(tr['w'], 100)
ax[1].axhspan(*sv, color=C_SURV, alpha=0.18, lw=0)
ax[1].plot(tr['q'], tr['w'], 'o', color=INK, ms=5)
ax[1].set_xlim(0, 0.5); ax[1].set_ylim(-4, 0)
ax[1].set_xlabel('anticipated intrusion probability, q')
ax[1].set_ylabel('value of a salinized well per season, w')
h = [plt.Rectangle((0, 0), 1, 1, color='#f3f1ec', label=r'shape restriction holds ($-1\leq\theta_4\leq\theta_3$)'),
     plt.Rectangle((0, 0), 1, 1, color=C_PHYS, alpha=0.3, label='physics range of q'),
     plt.Rectangle((0, 0), 1, 1, color=C_SURV, alpha=0.3, label='survey of 100 answers on w'),
     plt.Line2D([], [], color=C_REC, label='recharge effect (extra high-pumping seasons)')]
ax[1].legend(handles=h, frameon=False, fontsize=6.4, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=1)
ax[1].set_title('(b) the recharge effect needs q and w', fontsize=9)

rows = D['A']['rows']
y = np.arange(len(rows))[::-1]
short = ['economic data only', '+ shape restriction', '+ shape + physics', '+ shape + survey (100)',
         '+ shape + physics + survey', '+ shape + sentinels + survey']
for yy, r in zip(y, rows):
    lo, hi = r['recharge']
    ax[2].plot([lo, hi], [yy, yy], color=C_REC, lw=5, solid_capstyle='butt')
    ax[2].text(hi + 0.06, yy, f'{lo:.2f}–{hi:.2f}', va='center', fontsize=6.6, color='#3a3a3a')
ax[2].axvline(tr['recharge'], color=INK, lw=0.9, ls=':')
ax[2].plot(0, y[0] + 0.0, 's', color=C_NAIVE, ms=6)
ax[2].set_yticks(y); ax[2].set_yticklabels(short, fontsize=7)
ax[2].set_xlim(-0.05, 3.9)
ax[2].set_xlabel('extra high-pumping seasons when recharge halves q')
ax[2].set_title('(c) identified set of the recharge effect', fontsize=9)
fig.tight_layout(); fig.subplots_adjust(bottom=0.36); fig.savefig('figZ1_identified.png', dpi=200); plt.close(fig)

# ---------------------------------------------------------------- figure 2: design
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.6))
shades = ['#c9c6bf', '#a3a19a', '#7a7872', '#4e4c48', '#1f1e1c']
for row, col in zip(D['B'], shades):
    f = np.array(row['fracs'])
    for k, key, best in ((0, 'w_fee', 'best_fee'), (1, 'w_recharge', 'best_recharge')):
        wv = np.array(row[key]) * (100 if k == 0 else 1)
        ax[k].plot(f, wv, color=col, lw=1.6, label=f'budget {row["budget"]}')
        j = int(np.argmin(wv))
        ax[k].plot(f[j], wv[j], 'o', color=C_FEE if k == 0 else C_REC, ms=4.5)
ax[0].set_ylabel('expected width of the identified set (percentage points)')
ax[1].set_ylabel('expected width of the identified set (seasons)')
for a, t in zip(ax[:2], ('(a) goal: the fee effect on salinization risk', '(b) goal: the recharge effect on pumping')):
    a.set_xlabel('share of the budget spent on sentinel wells')
    a.set_title(t, fontsize=9)
ax[0].legend(frameon=False, fontsize=6.4, loc='upper right', ncol=1)
B = [r['budget'] for r in D['B']]
ax[2].plot(B, [r['best_fee'] for r in D['B']], 'o-', color=C_FEE, lw=1.8, label='goal: fee effect')
ax[2].plot(B, [r['best_recharge'] for r in D['B']], 's-', color=C_REC, lw=1.8, label='goal: recharge effect')
ax[2].set_xscale('log'); ax[2].set_xticks(B); ax[2].set_xticklabels([str(b) for b in B])
ax[2].xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax[2].set_ylim(0, 1.02)
ax[2].set_xlabel('budget (cost of one sentinel well-season = 1)')
ax[2].set_ylabel('best share on sentinel wells')
ax[2].legend(frameon=False, fontsize=6.8, loc='lower right')
ax[2].set_title('(c) the best design depends on the goal', fontsize=9)
fig.tight_layout(); fig.savefig('figZ2_design.png', dpi=200); plt.close(fig)
print('figures written')
