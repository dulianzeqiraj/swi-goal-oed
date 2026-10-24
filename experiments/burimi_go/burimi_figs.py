"""Figure figB1_identifiability.png for review 49 (BURIMI-GO): (a) for 16 designs (known stoichiometric signatures and
regimes), the dimension of the fibre of equally good models and the share of each query's derivative that lies along
the fibre (zero = identified); (b) maximum-likelihood estimation from simulated well chemistry: relative error of the
two unit-level counterfactuals for six designs; (c) the two counterfactuals of the observed well, ion by ion."""
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'burimi_results.json')))
PR = json.load(open(os.path.join(HERE, 'burimi_precision.json')))
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#e6e6e6', 'grid.linewidth': 0.8})
SIG = {(): 'none', (0,): 'seawater', (0, 1): 'seawater, weathering', (0, 1, 2): 'all three', (2,): 'exchange'}
REG = {(): 'baseline only', (0,): 'pumping', (1,): 'irrigation', (2,): 'clay facies', (0, 2): 'pumping + clay',
       (1, 2): 'irrigation + clay', (0, 1, 2): 'all three regimes'}
KEYS = ['Q1 seawater halved (unit)', 'Q2 no exchange (unit)', 'Q3 unobserved pumping regime (population)']
FLOOR = 1e-12


def label(r):
    return f"{SIG[tuple(r['known'])]} | {REG[tuple(r['targets'])]}"


fig = plt.figure(figsize=(15.5, 8.8))
gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], height_ratios=[1, 1])

a = fig.add_subplot(gs[:, 0])
rows = D['identifiability']
M = np.array([[max(r[k], FLOOR) for k in KEYS] for r in rows])
im = a.imshow(np.log10(M), cmap='YlOrBr', vmin=-12, vmax=0, aspect='auto', extent=(0.5, 3.5, len(rows) - 0.5, -0.5))
for i, r in enumerate(rows):
    a.text(0, i, str(r['fibre']), ha='center', va='center', fontsize=11, fontweight='bold',
           color='#1b5e20' if r['fibre'] == 0 else '#333')
    for j, k in enumerate(KEYS):
        v = r[k]
        txt = 'identified' if v < 1e-6 else f'{v:.1e}'
        a.text(j + 1, i, txt, ha='center', va='center', fontsize=8.5, color='#1b5e20' if v < 1e-6 else ('white' if v > 1e-3 else '#222'))
a.set_xlim(-0.5, 3.5)
a.set_xticks([0, 1, 2, 3])
a.set_xticklabels(['fibre\ndimension', 'Q1: seawater\nhalved (well)', 'Q2: no cation\nexchange (well)',
                   'Q3: unobserved\npumping regime'], fontsize=9)
a.set_yticks(range(len(rows))); a.set_yticklabels([label(r) for r in rows], fontsize=8.5)
a.grid(False)
a.set_ylabel('known signatures | regimes observed')
a.set_title('(a) what each design identifies (share of the query along the fibre)', fontsize=11)
cb = fig.colorbar(im, ax=a, fraction=0.035, pad=0.02); cb.set_label(r'$\log_{10}$ share along the fibre')

b = fig.add_subplot(gs[0, 1])
est = D['estimation']
for i, r in enumerate(est):
    for k, col, off in [('err_pump_all', '#2a78d6', -0.15), ('err_exch_all', '#eb6834', 0.15)]:
        y = np.array(r[k]); x = np.full(len(y), i + off) + np.linspace(-0.05, 0.05, len(y))
        b.plot(x, y, 'o', color=col, ms=4.5, alpha=0.75, mec='white', mew=0.5)
        b.plot([i + off - 0.1, i + off + 0.1], [np.median(y)] * 2, color=col, lw=2.2)
    q = next(x for x in PR if x['known'] == r['known'] and x['targets'] == r['targets'])
    for k, col, off in [('pred_rel_err_pump', '#2a78d6', -0.15), ('pred_rel_err_exch', '#eb6834', 0.15)]:
        if q[k] is not None and q[k] > 1e-6:
            b.plot([i + off + 0.16], [q[k]], 'D', color='white', mec=col, mew=1.8, ms=7)
b.plot([], [], 'o', color='#2a78d6', label='Q1 seawater halved'); b.plot([], [], 'o', color='#eb6834', label='Q2 no cation exchange')
b.plot([], [], 'D', color='white', mec='#555', mew=1.8, ms=7, label='delta-method prediction (identified queries)')
b.set_yscale('log'); b.set_ylim(1e-3, 20)
b.set_xticks(range(len(est)))
b.set_xticklabels([label(r).replace(' | ', '\n') for r in est], fontsize=7.8)
b.set_ylabel('relative error of the counterfactual change')
b.set_title(f"(b) estimation from simulated wells ({est[0]['n_data']} data sets each)", fontsize=11)
b.legend(frameon=False, fontsize=8.5, loc='lower left')

c = fig.add_subplot(gs[1, 1])
ions = D['ions']; xo = np.array(D['x_obs'])
d1 = np.array(D['cf_true']['pump']) - xo; d2 = np.array(D['cf_true']['exch']) - xo
w = 0.38; xx = np.arange(len(ions))
c.bar(xx - w / 2, d1, w, color='#2a78d6', label='Q1: seawater fraction halved')
c.bar(xx + w / 2, d2, w, color='#eb6834', label='Q2: no cation exchange')
c.axhline(0, color='#777', lw=0.8)
c.set_xticks(xx); c.set_xticklabels(ions)
c.set_ylabel('counterfactual change (meq/L)')
c.set_title('(c) the two counterfactuals of the sampled well (truth)', fontsize=11)
c.legend(frameon=False, fontsize=8.5, loc='lower right')

fig.tight_layout()
fig.savefig(os.path.join(HERE, 'figB1_identifiability.png'), dpi=170)
print('wrote figB1_identifiability.png')
