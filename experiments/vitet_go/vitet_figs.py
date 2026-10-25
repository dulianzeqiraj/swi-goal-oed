"""Figure figV1_years.png for review 52 (VITET-GO): (a) years of logs needed for a 1% excess cost against the extra cost
paid to make the logs more informative, by detuning the operators or adding a recorded dither; (b) years for each
monitoring network; (c) the local minimax floor tr(H I^-1)/(2 N J*) against the excess cost of learners trained on N
months of logs (Monte Carlo of the physical model by likelihood, and deep agents); (d) which parameters the remaining
uncertainty sits in, for near-optimal and timid operators."""
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: json.load(open(os.path.join(HERE, f))) if os.path.exists(os.path.join(HERE, f)) else None
D, MC, DP = rd('vitet_results.json'), rd('vitet_mc.json'), rd('vitet_deep.json')
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'axes.axisbelow': True, 'grid.color': '#e6e6e6', 'grid.linewidth': 0.8})
C1, C2, C3, C4 = '#2a78d6', '#eb6834', '#1baf7a', '#eda100'
INK2 = '#555555'
fig = plt.figure(figsize=(15.5, 11.5))
gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.45)
y0 = D['years_no_dither']

# (a) operating choices
a = fig.add_subplot(gs[0, 0])
g = D['gamma']
base_cost = g[0]['J_op_rel']
gx = [100 * (r['J_op_rel'] - base_cost) for r in g[1:]]
gy = [r['years_1pct'] for r in g[1:]]
a.plot(gx, gy, '-o', color=C1, lw=2, ms=7, label='detune the operators (gain × γ)')
for r, x, y in zip(g[1:], gx, gy):
    a.annotate(f'γ = {r["gamma"]:.1f}', (x, y), textcoords='offset points', xytext=(-8, -15) if r['gamma'] < 0.45 else (6, 5), fontsize=8, color=INK2)
slow = [(100 * b, D[f'choice_{b}']['goal_years']) for b in (0.005, 0.02)] + [(100 * D['equal_cost']['extra_cost'], D['equal_cost']['dither_years'])]
a.plot(*zip(*slow), '-s', color=C2, lw=2, ms=7, label='add a slow recorded dither (AR(1), φ = 0.98)')
white = [(100 * b, D[f'choice_{b}']['white_years']) for b in (0.005, 0.02)]
a.plot(*zip(*white), '-^', color=C3, lw=2, ms=7, label='add a white recorded dither')
a.axhline(y0, color=INK2, ls=':', lw=1.2)
a.text(0.32, y0 + 0.35, f'operators as they are: {y0:.1f} years', fontsize=8, color=INK2)
a.set_xscale('log'); a.set_xlim(0.3, 160); a.set_ylim(8, 23)
a.set_xlabel('extra cost paid by the operators (% of J*, log scale)')
a.set_ylabel('years of logs for a 1% excess cost')
a.legend(frameon=False, fontsize=8, loc='lower left')
a.set_title('(a) buying information: detuning beats dithering', fontsize=11)

# (b) monitoring networks
b = fig.add_subplot(gs[0, 1])
M = sorted(D['monitoring'], key=lambda r: r['years_1pct'])
names = {'head + sentinel chloride (baseline)': 'head + sentinel chloride (baseline)',
         'sentinel chloride noise halved': 'sentinel chloride noise halved',
         "the operators' toe reading logged": "operators' toe reading logged",
         'a second sentinel that sees more clay salt': 'second sentinel (more clay salt)',
         'head noise 0.02 instead of 0.05': 'head noise 0.02 (was 0.05)',
         'a soil-moisture probe': 'soil-moisture probe'}
ys = np.arange(len(M))
cols = [INK2 if 'baseline' in r['net'] else C1 for r in M]
b.barh(ys, [r['years_1pct'] for r in M], color=cols, height=0.6)
for i, r in enumerate(M):
    b.text(r['years_1pct'] + 0.4, i, f'{r["years_1pct"]:.1f} y; excess after 10 y {r["abs_excess_10y"]:.4f}', va='center', fontsize=8, color=INK2)
b.set_yticks(ys); b.set_yticklabels([names.get(r['net'], r['net']) for r in M]); b.invert_yaxis()
b.set_xlim(0, 46); b.set_xlabel('years of logs for a 1% excess cost')
b.grid(axis='y', visible=False)
b.set_title('(b) what the monitoring network records', fontsize=11)

# (c) floor against learners
c = fig.add_subplot(gs[1, 0])
NS = np.array(MC['NS'])
yrs = NS / 12
nn = np.geomspace(100, 1400, 50)
c.plot(nn / 12, 100 * MC['trHI'] / (2 * nn * MC['J_star']), color=INK2, lw=2, label='floor tr(H I⁻¹) / (2 N J*)')
mean = [100 * MC['results'][str(n)]['mean_excess'] for n in NS]
se = [100 * MC['results'][str(n)]['se'] for n in NS]
c.errorbar(yrs, mean, yerr=se, fmt='o', color=C1, ms=7, capsize=3, label='physical model by likelihood, plug-in rule (100 runs, mean ± SE)')
TOP = 300.0
if DP:
    for k, (key, col, mk, lab) in enumerate([('physics_neural', C3, 'D', 'neural policy trained in the calibrated physical model'),
                                             ('deep_world_model', C2, 's', 'deep world model + neural policy')]):
        first = True
        for r in DP['runs']:
            v = r[key]
            x = r['N'] / 12 * (1.06 if k else 0.94)
            if v.get('unstable'):
                c.plot([x], [TOP], mk, color=col, mfc='white', mew=1.6, ms=7, label=None)
                c.annotate('', xy=(x, TOP * 1.5), xytext=(x, TOP), arrowprops=dict(arrowstyle='->', color=col, lw=1.4))
            else:
                c.plot([x], [max(100 * v['rel_excess'], 0.02)], mk, color=col, ms=7, label=lab if first else None)
                first = False
        if first:
            c.plot([], [], mk, color=col, label=lab)
c.set_xscale('log'); c.set_yscale('log'); c.set_ylim(0.05, TOP * 2)
c.set_xticks([10, 30, 100]); c.set_xticklabels(['10', '30', '100'])
c.set_xlabel('years of logs (log scale)'); c.set_ylabel('excess cost on the true aquifer (% of J*, log scale)')
c.legend(frameon=False, fontsize=8, loc='lower left')
c.set_title('(c) the floor and the learners (open symbols, arrow: unstable)', fontsize=11)

# (d) where the uncertainty sits
d = fig.add_subplot(gs[1, 1])
P4 = ['pumping -> head', 'head -> toe', 'toe retention', 'clay -> toe']
lab4 = ['pumping → head', 'head → toe', 'toe retention', 'clay → toe']
x = np.arange(4)
for k, (key, col, name) in enumerate([('near-optimal_0.1', C1, 'near-optimal operators'), ('timid_0.1', C2, 'timid operators (40% of the gain)')]):
    sh = D['base'][key]['contrib4']
    d.bar(x + (k - 0.5) * 0.36, [100 * sh[p] for p in P4], width=0.34, color=col, label=f'{name}: {D["base"][key]["years4_1pct"]:.1f} years')
d.set_xticks(x); d.set_xticklabels(lab4)
d.set_ylabel('share of tr(H I⁻¹) on the diagonal (%)')
d.grid(axis='x', visible=False)
d.legend(frameon=False, fontsize=8, loc='upper right')
d.set_title('(d) which parameters the logs leave uncertain', fontsize=11)

out = os.path.join(HERE, 'figV1_years.png')
fig.savefig(out, dpi=170, bbox_inches='tight')
print('wrote', out)
