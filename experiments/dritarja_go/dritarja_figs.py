"""Figure figD1_window.png for review 50 (DRITARJA-GO): (a) excess average cost of pumping rules that see a window of
the past, against the length of the window: the truncated optimal controller and the best linear rule for an
observation-only window, the best linear ARX rule (past observations and past pumping), and the neural agents; (b) the
impulse response of the optimal controller on the head and the sentinel chloride, with the slowest controller pole;
(c) how the sentinel well sets the memory needed."""
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import dritarja as d

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'dritarja_results.json')))
NN = json.load(open(os.path.join(HERE, 'dritarja_neural.json'))) if os.path.exists(os.path.join(HERE, 'dritarja_neural.json')) else None
SA = json.load(open(os.path.join(HERE, 'dritarja_saa.json'))) if os.path.exists(os.path.join(HERE, 'dritarja_saa.json')) else None
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#e6e6e6', 'grid.linewidth': 0.8})
Js = D['J_star']
fig = plt.figure(figsize=(15.5, 10.4))
gs = fig.add_gridspec(2, 2, width_ratios=[1.35, 1])

a = fig.add_subplot(gs[:, 0])
ws = sorted(int(w) for w in D['fir'])
tr = np.array([np.inf if D['fir'][str(w)] is None else (D['fir'][str(w)] - Js) / Js for w in ws])
ok = np.isfinite(tr)
a.plot(np.array(ws)[ok], tr[ok], '-', color='#8a8a8a', lw=1.8, label='observations only: optimal controller truncated to w months')
for w in np.array(ws)[~ok]:
    a.plot([w], [3e-1], 'x', color='#8a8a8a', ms=7, mew=1.6)
a.text(1.0, 5.2e-1, 'x: the truncated rule does not stabilise the aquifer (w ≤ 6)', fontsize=8.5, color='#666')
fo = sorted((int(w), (v - Js) / Js) for w, v in D['fir_opt'].items())
a.plot([x[0] for x in fo], [x[1] for x in fo], 'o-', color='#eb6834', lw=2.2, ms=5, label='observations only: best linear rule for the window')
ao = sorted((int(k), max((v - Js) / Js, 1e-8)) for k, v in D['arx_opt'].items())
a.plot([x[0] for x in ao], [x[1] for x in ao], 's-', color='#2a78d6', lw=2.2, ms=6, label='observations + own past pumping (ARX): best linear rule')
a.annotate('exact for k = 4 (= state dimension)', xy=(4, 1e-8), xytext=(6.0, 2.2e-8), fontsize=8.5, color='#2a78d6', arrowprops=dict(arrowstyle='->', color='#2a78d6'))
rho = D['rho_c']
xx = np.arange(40, 200)
c0 = tr[ws.index(128)] / rho ** (2 * 128)
a.plot(xx, c0 * rho ** (2 * xx), '--', color='#555', lw=1.2, label=r'predicted decay $\rho_c^{2w}$')
if NN:
    for row in NN['summary']:
        col = '#eb6834' if row['kind'] == 'obs' else '#2a78d6'
        x = row['w']
        a.plot([x], [max(row['rel_excess_median'], 1e-5)], 'D', color='white', mec=col, mew=2, ms=8)
        a.plot([x, x], [max(row['rel_excess_min'], 1e-5), max(row['rel_excess_max'], 1e-5)], color=col, lw=1.2)
    a.plot([], [], 'D', color='white', mec='#555', mew=2, ms=8, label='neural agents, stochastic gradients (median, range of 2 seeds)')
if SA:
    for row in SA['summary']:
        col = '#eb6834' if row['kind'] == 'obs' else '#2a78d6'
        a.plot([row['w'] * 1.08], [max(row['rel_excess'], 1e-5)], '^', color=col, mec='white', ms=10)
    a.plot([], [], '^', color='#555', mec='white', ms=10, label='neural agents, full-batch training on fixed rollouts')
a.axhline(0.01, color='#bbb', lw=1, ls=':')
a.set_xscale('log', base=2); a.set_yscale('log')
a.set_ylim(5e-9, 1.0)
a.set_xlabel('months of history in the window (ARX: past pumping rates k, observations k + 1)')
a.set_ylabel('excess average cost over the optimal pumping rule (relative)')
a.set_title('(a) how much memory a pumping agent needs', fontsize=11)
a.legend(frameon=False, fontsize=8.5, loc='upper center', bbox_to_anchor=(0.5, -0.075), ncol=2)

b = fig.add_subplot(gs[0, 1])
C, V = d.obs_model(); L = d.lqg(C, V)
h = d.markov(L, 160)
k = np.arange(len(h))
b.semilogy(k, [abs(x[0, 0]) + 1e-16 for x in h], color='#1baf7a', lw=1.8, label=r'weight on the head, $|h_k|$')
b.semilogy(k, [abs(x[0, 1]) + 1e-16 for x in h], color='#9b59b6', lw=1.8, label=r'weight on the sentinel chloride, $|h_k|$')
b.semilogy(k[5:], abs(h[5][0, 1]) * rho ** (k[5:] - 5), '--', color='#555', lw=1.1, label=rf'$\rho_c^k$, $\rho_c$ = {rho:.3f}')
b.set_xlabel('lag k (months)'); b.set_ylabel('impulse response of the optimal rule')
b.set_title('(b) the optimal rule remembers through its slowest pole', fontsize=11)
b.legend(frameon=False, fontsize=8.5)

c = fig.add_subplot(gs[1, 1])
sc = D['scan']
for kap, col in zip(sorted(set(r['kappa'] for r in sc)), ['#9b59b6', '#2a78d6', '#1baf7a', '#eb6834']):
    rows = [r for r in sc if r['kappa'] == kap]
    c.plot([r['sd_cl'] for r in rows], [r['min_stable'] for r in rows], 'o-', color=col, lw=2, ms=5, label=f'κ = {kap:g}: shortest stabilising window')
    c.plot([r['sd_cl'] for r in rows], [r['w_1pct'] for r in rows], 's--', color=col, lw=1.2, ms=5, alpha=0.8)
c.plot([], [], 's--', color='#555', label='window for 1 % excess (truncated rule)')
c.set_yscale('log', base=2)
c.set_xlabel('noise of the sentinel chloride (standard deviation)'); c.set_ylabel('months of observations')
c.set_title('(c) a noisier sentinel that sees less of the clay salt needs more memory', fontsize=11)
c.legend(frameon=False, fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=2)

fig.tight_layout()
fig.savefig(os.path.join(HERE, 'figD1_window.png'), dpi=170)
print('wrote figD1_window.png')
