"""Figure figU1_memory.png for review 48 (KUJTESA-GO): (a) exact fitted value iteration: relative error of P_cc, the
part of the value that belongs to the salt stored in the clays, for plain updates, lambda-returns and physics shaping,
with the predicted slow-mode law; (b) target updates needed to reach 1 % error for every pair of closed-loop modes;
(c) the same three learners with a neural value network; (d) value slow, rule fast: the error of the greedy pumping
gain on each state against the error of P_cc, for plain updates."""
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'kujtesa_results.json')))
PO = json.load(open(os.path.join(HERE, 'kujtesa_policy.json')))
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#e6e6e6', 'grid.linewidth': 0.8})
C = {'FVI': ('#eb6834', 'plain target updates'),
     'FVI, lambda-returns': ('#1baf7a', r'$\lambda$-returns ($\lambda=0.9$)'),
     'FVI, physics shaping': ('#2a78d6', 'physics value as shaping potential')}
g = D['P']['gamma']
mu_s = D['fvi']['mu_abs'][0]
fig, ax = plt.subplots(2, 2, figsize=(13.2, 9.2))

a = ax[0, 0]
for k, (col, lab) in C.items():
    y = np.array(D['exact_pcc'][k]); x = np.arange(1, len(y) + 1)
    a.plot(x, np.maximum(y, 1e-6), color=col, lw=2.2, label=lab)
x = np.arange(1, len(D['exact_pcc']['FVI']) + 1)
y0 = D['exact_pcc']['FVI'][99] / (g * mu_s ** 2) ** 100      # anchored at k = 100 to compare slopes
a.plot(x, y0 * (g * mu_s ** 2) ** x, ls='--', color='#555', lw=1.2, label=r'predicted slow-mode law $(\gamma\mu_s^2)^k$')
a.axhline(0.1, color='#999', lw=1, ls=':')
a.set_yscale('log'); a.set_ylim(1e-4, 1.5)
a.set_xlabel('target updates $k$'); a.set_ylabel(r'relative error of $P_{cc}$ (exact iteration)')
a.set_title('(a) the clay part of the value is learned slowly', fontsize=11)
a.legend(frameon=False, fontsize=8.5, loc='lower left')

b = ax[0, 1]
labs = ['clay', 'soil\nmoisture', 'head–toe', 'head–toe*']
fac =np.array(D['fvi']['factor_abs'])
M = np.ceil(np.log(100) / -np.log(fac))
im = b.imshow(M, cmap='Oranges', norm=matplotlib.colors.LogNorm(vmin=3, vmax=400))
for i in range(4):
    for j in range(4):
        b.text(j, i, f'{M[i, j]:.0f}', ha='center', va='center', fontsize=11,
               color='white' if M[i, j] > 60 else '#222')
b.set_xticks(range(4)); b.set_yticks(range(4)); b.set_xticklabels(labs, fontsize=9); b.set_yticklabels(labs, fontsize=9)
b.grid(False)
b.set_title(r'(b) updates to 1 % error by pair of modes, $\lceil\ln 100/(-\ln|\gamma\mu_i\mu_j|)\rceil$', fontsize=11)
cb = fig.colorbar(im, ax=b, fraction=0.046, pad=0.04); cb.set_label('target updates')

c = ax[1, 0]
for k, (col, lab) in C.items():
    N = D['neural'][k]
    y = np.array(N['pcc_median']); x = np.arange(1, len(y) + 1)
    for s in N['pcc_all']:
        c.plot(x, s, color=col, lw=0.7, alpha=0.25)
    c.plot(x, y, color=col, lw=2.2, label=lab + ' (median of seeds)')
    c.plot(x, D['exact_pcc'][k][:len(y)], color=col, lw=1.0, ls='--')
c.axhline(0.1, color='#999', lw=1, ls=':')
c.set_yscale('log'); c.set_ylim(3e-3, 1.5)
c.set_xlabel('target updates $k$'); c.set_ylabel(r'relative error of $P_{cc}$ (neural network)')
c.set_title('(c) the same with a neural value network (thin: seeds; dashed: exact)', fontsize=11)
c.legend(frameon=False, fontsize=8.5, loc='lower left')

d = ax[1, 1]
F = PO['FVI']
x = np.arange(1, len(F['pcc']) + 1)
d.plot(x, F['pcc'], color='#eb6834', lw=2.4, label=r'value: relative error of $P_{cc}$')
G = np.array(F['gain'])
for i, (nm, col) in enumerate(zip(['soil moisture $m$', 'head $h$', 'toe $X$', 'clay salt $c$'],
                                  ['#9b59b6', '#2a78d6', '#1baf7a', '#555555'])):
    d.plot(x, np.maximum(G[:, i], 1e-7), color=col, lw=1.6, label=f'rule: relative error of the gain on {nm}')
d.axhline(0.01, color='#999', lw=1, ls=':')
d.set_yscale('log'); d.set_ylim(1e-6, 1.5)
d.set_xlabel('target updates $k$ (plain, exact)'); d.set_ylabel('relative error')
d.set_title('(d) the value is slow, the pumping rule is fast', fontsize=11)
d.legend(frameon=False, fontsize=8.2, loc='lower left')

fig.tight_layout()
fig.savefig(os.path.join(HERE, 'figU1_memory.png'), dpi=170)
print('wrote figU1_memory.png')
