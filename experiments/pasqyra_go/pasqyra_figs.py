"""Figure figP1_mirror.png for review 51 (PASQYRA-GO): (a) what each learner trained on the operators' logs believes it
costs and what it costs on the true aquifer; (b) the chloride response to a sustained extra unit of pumping in the true
aquifer, in the world model of the logs (aquifer') and in the calibrated physical model; (c) behaviour-regularised offline
RL: the cost on the true aquifer as the weight on staying close to the operators grows; (d) the mirror test: share of test
periods in which a recorded dither reveals the deluded world model, against the length of the test period."""
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import pasqyra as p

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'pasqyra_results.json')))
T = json.load(open(os.path.join(HERE, 'pasqyra_dither.json'))) if os.path.exists(os.path.join(HERE, 'pasqyra_dither.json')) else None
NN = json.load(open(os.path.join(HERE, 'pasqyra_neural.json'))) if os.path.exists(os.path.join(HERE, 'pasqyra_neural.json')) else None
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#e6e6e6', 'grid.linewidth': 0.8})
Js = D['J_star']
COL = {'near-optimal': '#2a78d6', 'timid': '#eb6834'}
fig = plt.figure(figsize=(15.5, 11.8))
gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], hspace=0.42, wspace=0.28)

# (a) believed against deployed
a = fig.add_subplot(gs[0, 0])
order = ['phys4', 'phys8', 'free', 'arx32', 'world_model_inf', 'clone_inf', 'clone_arx4', 'clone_obs8']
labels = ['physical model, 4 parameters', 'physical model, 8 parameters', 'black-box 4-state model', 'black-box ARX, 32 lags',
          'world model, unlimited capacity', 'clone, unlimited window', 'clone, 4 rates + 5 observations', 'clone, 8 observations']
TOP = 300.0
for k, (name, sh) in enumerate([('near-optimal', -0.17), ('timid', 0.17)]):
    S = D['settings'][name]
    for i, key in enumerate(order):
        r = S['learners'][key]
        y = i + sh
        J = r['J']
        x = TOP if J is None else J / Js
        a.plot([x], [y], 'o', color=COL[name], ms=7, zorder=3)
        if J is None:
            a.annotate('', xy=(TOP * 1.6, y), xytext=(TOP, y), arrowprops=dict(arrowstyle='->', color=COL[name], lw=1.5))
        if r.get('J_believed') is not None:
            xb = r['J_believed'] / Js
            a.plot([xb], [y], 'o', mfc='white', mec=COL[name], mew=1.6, ms=7, zorder=3)
            a.plot([min(xb, x), max(xb, x)], [y, y], color=COL[name], lw=1, alpha=0.5)
    a.axvline(S['J_op'] / Js, color=COL[name], ls=':', lw=1.2)
a.axvline(1.0, color='#555', lw=1)
a.set_xscale('log'); a.set_xlim(0.08, TOP * 2)
a.set_yticks(range(len(order))); a.set_yticklabels(labels); a.invert_yaxis()
a.set_xlabel('average cost / optimal records-only cost J* (log scale)')
a.plot([], [], 'o', color='#555', label='cost on the true aquifer (arrow: unstable)')
a.plot([], [], 'o', mfc='white', mec='#555', label='cost the learner believes (its own model)')
a.plot([], [], ':', color='#555', label='the operators who wrote the logs')
for name in COL:
    a.plot([], [], 's', color=COL[name], label=f'operators {name}')
a.legend(frameon=False, fontsize=8, loc='lower right')
a.set_title('(a) what learners trained on the logs believe, and what happens', fontsize=11)

# (b) step responses
b = fig.add_subplot(gs[0, 1])
m = np.arange(1, 61)
E = D['settings']['near-optimal']['equivalence']
b.plot(m, E['step_true'], color='#1baf7a', lw=2.2, label='true aquifer')
b.plot(m, E['step_prime'], color='#2a78d6', lw=2.2, label="world model of the logs (aquifer'), near-optimal operators")
b.plot(m, D['settings']['timid']['equivalence']['step_prime'], color='#eb6834', lw=2.2, label="world model of the logs, timid operators")
th = D['settings']['near-optimal']['learners']['phys4']['theta']
A, B = p.model(np.array(th)); z = np.zeros((4, 1)); st = []
for _ in range(60):
    z = A @ z + B; st.append(float((p.C @ z)[1, 0]))
b.plot(m, st, '--', color='#555', lw=1.4, label='physical model calibrated on the same logs')
b.axhline(0, color='#999', lw=0.8)
b.set_xlabel('months after pumping is raised by one unit'); b.set_ylabel('change of the sentinel chloride (noise-free)')
b.legend(frameon=False, fontsize=8.5, loc='upper left')
b.set_title('(b) the mirror: in the logs, pumping seems to freshen the aquifer', fontsize=11)

# (c) behaviour regularisation
c = fig.add_subplot(gs[1, 0])
for name in COL:
    S = D['settings'][name]
    lam = np.array([r['lam'] for r in S['regularised']]); J = np.array([np.nan if r['J'] is None else r['J'] / Js for r in S['regularised']])
    lam_p = np.where(lam == 0, 3e-3, lam)
    c.plot(lam_p, J, 'o-', color=COL[name], lw=2, ms=5, label=f'operators {name}')
    c.axhline(S['J_op'] / Js, color=COL[name], ls=':', lw=1.2)
c.axhline(1.0, color='#555', lw=1)
c.text(4e-3, 1.04, 'J*', fontsize=9, color='#555')
c.set_xscale('log'); c.set_yscale('log')
c.set_xlabel('weight on staying close to the operators (lam; 0 drawn at the left edge)')
c.set_ylabel('cost on the true aquifer / J*')
c.legend(frameon=False, fontsize=8.5)
c.set_title('(c) staying close to the operators rescues the agent only by returning to them', fontsize=11)

# (d) mirror test
d = fig.add_subplot(gs[1, 1])
if T is not None:
    cols = ['#9b59b6', '#2a78d6', '#1baf7a', '#eb6834']
    for s, col in zip(T['SDS'], cols):
        y = [T['table']['0']['cells'][f'{N}_{s}']['targeted_arx'] for N in T['NS']]
        d.plot(T['NS'], y, 'o-', color=col, lw=2, ms=5, label=f'dither sd {s} ({100 * s / 0.763:.0f}% of the pumping variation)')
        y0 = [T['table']['1']['cells'][f'{N}_{s}']['targeted_arx'] for N in T['NS']]
        d.plot(T['NS'], y0, 'x--', color=col, lw=1, ms=6, alpha=0.7)
    d.plot([], [], 'x--', color='#555', label='same test, logs without private information (false alarms)')
    d.axhline(0.05, color='#999', lw=0.8, ls=':'); d.axhline(0.8, color='#999', lw=0.8, ls=':')
    d.set_ylim(0, 1.02)
    d.set_xlabel('months of the test period with a recorded dither')
    d.set_ylabel('share of test periods that reject the world model (5% test)')
    d.legend(frameon=False, fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=2)
d.set_title('(d) the mirror test: a small recorded dither exposes the deluded model', fontsize=11)

fig.savefig(os.path.join(HERE, 'figP1_mirror.png'), dpi=170, bbox_inches='tight')
print('wrote figP1_mirror.png')
