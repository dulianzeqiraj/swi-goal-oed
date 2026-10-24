"""Figure figZ1_exploration.png for review 47 (ZBULIMI-GO): (a) regret of four certainty-equivalent learners of a
three-well-field pumping rule with the predicted sqrt(T) laws, (b) error of the estimated responses of the head to
the well fields, (c) the advantage of head-neutral exploration against the strength of the pumping response."""
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'zbulimi_results.json')))
TH = json.load(open(os.path.join(HERE, 'zbulimi_theory.json')))
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#e6e6e6', 'grid.linewidth': 0.8})
C = {'CE, no exploration': ('#eb6834', 'no exploration'),
     'CE, exploration of total pumping': ('#8a8a8a', 'exploring total pumping (all wells together)'),
     'CE, isotropic exploration': ('#1baf7a', 'isotropic exploration of every well'),
     'CE, head-neutral exploration': ('#2a78d6', 'head-neutral, goal-oriented exploration')}
fig, ax = plt.subplots(1, 3, figsize=(15.5, 4.6))

a = ax[0]
for k, (col, lab) in C.items():
    g = np.array(D[k]['grid']); m = np.array(D[k]['regret']); s = np.array(D[k]['se'])
    ok = m > 0
    a.plot(g[ok], m[ok], color=col, lw=2.2, label=lab)
    a.fill_between(g[ok], np.maximum(m - 2 * s, 1e-3)[ok], (m + 2 * s)[ok], color=col, alpha=0.15, lw=0)
tt = np.logspace(2.5, np.log10(D['P']['T']), 50)
for k, c, col in [('CE, isotropic exploration', D['c_iso'], '#1baf7a'), ('CE, head-neutral exploration', D['c_go'], '#2a78d6')]:
    a.plot(tt, c * np.sqrt(tt) + D[k]['offset'], ls='--', color=col, lw=1.2)
a.set_xscale('log'); a.set_yscale('log'); a.set_ylim(3, None)
a.set_xlabel('months of learning $T$'); a.set_ylabel('regret (cumulative excess cost)')
a.set_title('(a) which exploration pays off', fontsize=11)
a.legend(frameon=False, fontsize=8.5, loc='upper left')
a.text(0.98, 0.04, r'dashed: predicted $c\sqrt{T}$ + offset', transform=a.transAxes, ha='right', fontsize=8.5, color='#555')

b = ax[1]
for k, (col, lab) in C.items():
    br = np.array(D[k]['beta_rmse'])
    b.plot(br[:, 0], br[:, 1], 'o-', color=col, lw=2, ms=5, mec='white', label=lab)
b.set_xscale('log'); b.set_yscale('log')
b.set_xlabel('months of learning'); b.set_ylabel(r'RMSE of the responses $\hat{\beta}$ (three well fields)')
b.set_title('(b) what is learned about the well fields', fontsize=11)

c = ax[2]
sens = TH['sensitivity']
sc = [x['scale'] for x in sens]; ra = [x['ratio'] for x in sens]
c.plot(sc, ra, 'o-', color='#2a78d6', lw=2, ms=6, mec='white', label='predicted ratio of constants')
meas = D['CE, isotropic exploration']['sqrt_coef'] / D['CE, head-neutral exploration']['sqrt_coef']
c.plot([1.0], [meas], 'D', color='#eb6834', ms=8, mec='white', label='measured (fitted constants)')
c.axhline(1, color='#999', lw=1)
c.set_xlabel(r'strength of the head response to pumping ($\beta$ scaled)')
c.set_ylabel('regret constant: isotropic / head-neutral')
c.set_title('(c) the advantage of head-neutral exploration', fontsize=11)
c.legend(frameon=False, fontsize=8.5, loc='upper left')
c.set_ylim(0.9, max(ra + [meas]) * 1.12)

fig.tight_layout()
fig.savefig(os.path.join(HERE, 'figZ1_exploration.png'), dpi=170)
print('ok')
