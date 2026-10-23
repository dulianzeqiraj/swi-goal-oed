"""Figures of MJEGULLA-GO: figM1_robust.png (the robust filter over time, Theorem Q, widths by design) and
figM2_design.png (where the goal-oriented design measures, budget, decisions)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False})
D = json.load(open('mjegulla.json'))
C = json.load(open('mjegulla_budget.json'))
S = D['setup']
INK, GRID = '#0b0b0b', '#e5e4df'
COL = {'round_robin': '#a3a19a', 'random': '#7a7872', 'targets': '#2a78d6', 'similar': '#2a78d6', 'entropy': '#eb6834',
       'D_opt': '#1baf7a', 'c_opt': '#6250d6', 'goal': '#e8a0a0', 'mjegulla': '#e34948'}
LAB = {'round_robin': 'round robin', 'random': 'random', 'targets': 'municipal wells', 'similar': 'similar wells',
       'entropy': 'most uncertain', 'D_opt': 'D-optimal', 'c_opt': 'c-optimal', 'goal': 'goal criterion only',
       'mjegulla': 'MJEGULLA'}
B = D['B']


def stats(kind, rule):
    v = [x[kind + ':' + rule] for x in B]
    w = np.array([e['U1'] - e['L1'] for e in v]); c = np.mean([e['L1'] <= e['gs'] <= e['U1'] for e in v])
    return w.mean(), w.std() / np.sqrt(len(w)), c


fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.8), gridspec_kw=dict(width_ratios=[1.05, 1.0, 1.15]))
ex = D['A']['example']
for rule, col in (('random', COL['random']), ('mjegulla', COL['mjegulla'])):
    tr = np.array(ex[rule]['track'])
    ax[0].fill_between(tr[:, 0], tr[:, 1], tr[:, 2], color=col, alpha=0.22, lw=0)
    ax[0].plot(tr[:, 0], tr[:, 3], color=col, lw=1.6, label=f'{LAB[rule]}: estimate and robust interval')
tr = np.array(ex['mjegulla']['track'])
ax[0].plot(tr[:, 0], tr[:, 4], color=INK, lw=1.0, ls='--', label='oracle filter (true parameters, MJEGULLA data)')
ax[0].axhline(ex['G_mon'], color=INK, lw=0.8, ls=':', label='saline municipal wells, realized')
ax[0].set_xlabel('season'); ax[0].set_ylabel('expected saline municipal wells (goal M)')
ax[0].set_ylim(0, 6.2)
ax[0].legend(frameon=False, fontsize=6.3, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=1)
ax[0].set_title('(a) the robust filter over time', fontsize=9)

k1 = S['K1']
for kind, mk in (('mon', 'o'), ('plan', 's')):
    designs = S['designs_mon'] if kind == 'mon' else S['designs_plan']
    reg = [(x, r) for x in B for r in designs if not x[kind + ':' + r]['box']]      # regular (interior) fits
    A = np.array([x[kind + ':' + r]['A'] for x, r in reg])
    hw = np.array([(x[kind + ':' + r]['U1'] - x[kind + ':' + r]['L1']) / 2 for x, r in reg])
    up1 = np.array([x[kind + ':' + r]['pen']['1.0'][1] - x[kind + ':' + r]['g0'] for x, r in reg])
    ax[1].plot(A * np.sqrt(2 * k1), hw, mk, ms=2.2, color='#e34948', alpha=0.35, mew=0, label=f'hard penalty, goal {kind[0].upper()}')
    ax[1].plot(k1 / 2 * A ** 2, up1, mk, ms=2.2, color='#2a78d6', alpha=0.35, mew=0, label=f'γ = 1, goal {kind[0].upper()}')
lim = [0.005, 6]
ax[1].plot(lim, lim, color=INK, lw=0.8)
ax[1].set_xscale('log'); ax[1].set_yscale('log'); ax[1].set_xlim(lim); ax[1].set_ylim(lim)
ax[1].set_xlabel('second-order prediction (Theorem Q)')
ax[1].set_ylabel('exact half-width of the robust interval')
ax[1].legend(frameon=False, fontsize=6.3, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2, markerscale=3)
ax[1].set_title('(b) Theorem Q against the exact intervals\n(fits inside the parameter set)', fontsize=9)

ys = 0
ticks, labels = [], []
for kind in ('mon', 'plan'):
    designs = S['designs_mon'] if kind == 'mon' else S['designs_plan']
    for r in designs:
        m, se, c = stats(kind, r)
        ax[2].barh(ys, m, xerr=1.96 * se, color=COL[r], height=0.7, error_kw=dict(lw=0.8, ecolor=INK))
        ax[2].text(m + 1.96 * se + 0.04, ys, f'{100 * c:.0f}%', va='center', fontsize=6.5, color='#3a3a3a')
        ticks.append(ys); labels.append(f'{"M" if kind == "mon" else "P"}: {LAB[r]}')
        ys -= 1
    ys -= 0.8
ax[2].set_yticks(ticks); ax[2].set_yticklabels(labels, fontsize=6.8)
ax[2].set_xlabel('mean width of the robust interval (k = 1.92)')
ax[2].set_xlim(0, None)
ax[2].set_title('(c) width by design (coverage at bar end)', fontsize=9)
fig.tight_layout(); fig.subplots_adjust(bottom=0.33); fig.savefig('figM1_robust.png', dpi=200); plt.close(fig)

# ---------------------------------------------------------------- figure 2
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.6))
bins = np.linspace(0.3, 3.0, 10)
for k, (kind, title) in enumerate((('mon', '(a) goal M: municipal wells'), ('plan', '(b) goal P: planned sites'))):
    cnt_h = np.zeros(len(bins) - 1); cnt_l = np.zeros(len(bins) - 1); cnt_t = np.zeros(len(bins) - 1)
    for x in B:
        al = x[kind + ':mjegulla']['alloc']
        d = np.array(al['d']); u = np.array(al['u']); c = np.array(al['counts']); tg = np.zeros(len(d), bool); tg[al['tgt']] = True
        cnt_t += np.histogram(d[tg], bins, weights=c[tg])[0]
        cnt_h += np.histogram(d[(u == 1) & ~tg], bins, weights=c[(u == 1) & ~tg])[0]
        cnt_l += np.histogram(d[u == 0], bins, weights=c[u == 0])[0]
    tot = cnt_t.sum() + cnt_h.sum() + cnt_l.sum()
    mid = 0.5 * (bins[1:] + bins[:-1]); wdt = (bins[1] - bins[0]) * 0.85
    ax[k].bar(mid, cnt_l / tot, width=wdt, color='#c9c6bf', label='light pumping')
    ax[k].bar(mid, cnt_h / tot, width=wdt, bottom=cnt_l / tot, color='#7a7872', label='hard pumping')
    ax[k].bar(mid, cnt_t / tot, width=wdt, bottom=(cnt_l + cnt_h) / tot, color='#2a78d6', label='municipal wells')
    ax[k].set_ylim(0, 1.1 * ((cnt_l + cnt_h + cnt_t) / tot).max())
    if kind == 'plan':
        for sd in S['sites_d']:
            ax[k].axvline(sd, color='#e34948', lw=0.8, ls=':')
    ax[k].set_xlabel('distance of the measured well from the coast (km)')
    ax[k].set_ylabel('share of MJEGULLA measurements')
    ax[k].set_title(title, fontsize=9)
ax[0].legend(frameon=False, fontsize=6.6, loc='upper right')
bud = [2, 4, 8]
for rule in ('random', 'D_opt', 'goal', 'mjegulla'):
    ax[2].plot(bud, [C['C'][str(b)][rule]['width'] for b in bud], '-o', ms=4, lw=1.6, color=COL[rule], label=LAB[rule])
ax[2].set_xticks(bud); ax[2].set_xlabel('measurements per season')
ax[2].set_ylabel('mean width of the robust interval (goal P)')
ax[2].set_ylim(0, None)
ax[2].legend(frameon=False, fontsize=6.8)
ax[2].set_title('(c) budget', fontsize=9)
fig.tight_layout(); fig.savefig('figM2_design.png', dpi=200); plt.close(fig)
print('figures written')
