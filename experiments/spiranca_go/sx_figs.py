"""Figure of review 61 (ROJA-GO): (a) the stakeholder rule in closed loop under five storylines; (b) one aquifer in the
record-shattering drought, open loop: chloride at the screen, the yearly re-anchored and the ROJA-GO predictions, and
when the watch fires. Reads res/sx.json (or res/sx_pilot.json), writes res/figR1_extremes.png."""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
M_CLF, M_CLS = 12.92, 21781.0
src = os.path.join(HERE, 'res', 'sx.json')
if not os.path.exists(src):
    src = os.path.join(HERE, 'res', 'sx_pilot.json')
D = json.load(open(src)); rows = D['rows']; SC = D['scen']
cl = lambda y: M_CLF + 10 ** (-np.asarray(y)) * (M_CLS - M_CLF)

INK, MUTED, GRID = '#1f2933', '#616e7c', '#d9dee3'
POL = [('none', 'No action', '#7b8794'), ('spir', 'Static alarm', '#e69f00'), ('spir_ra', 'Yearly sample (S5)', '#56b4e9'),
       ('oracle', 'Screen sensor', '#cc79a7'), ('spir_roja', 'ROJA-GO', '#009e73')]
SLAB = {'none': 'Ordinary weather', 'rain': 'Intense rainfall', 'drought': 'Record drought', 'causal': 'Drought + causal change',
        'compound': 'Drought, then intense rain'}

plt.rcParams.update({'font.size': 11.5, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED})
fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.0, 4.6), gridspec_kw=dict(width_ratios=[1.0, 1.25]))

# (a) closed loop
for i, s in enumerate(SC):
    y0 = len(SC) - 1 - i
    for j, (p, lab, col) in enumerate(POL):
        v = np.array([r['closed'][s][p]['exc'] for r in rows])
        yy = y0 + (j - 2) * 0.15
        ax.plot([np.quantile(v, 0.1) * 100, np.quantile(v, 0.9) * 100], [yy, yy], color=col, lw=2, alpha=0.45, solid_capstyle='round')
        ax.plot(v.mean() * 100, yy, 'o', ms=6.5 if p == 'spir_roja' else 5, color=col, mec='white', mew=1.2, label=lab if i == 0 else None, zorder=3)
ax.set_yticks(range(len(SC))); ax.set_yticklabels([SLAB[s] for s in SC[::-1]])
ax.set_xlabel('seasons above 250 mg/L at the supply screen (%)')
ax.grid(axis='x', color=GRID, lw=0.8); ax.set_axisbelow(True)
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
ax.set_title(f'(a) The decision rule in closed loop ({len(rows)} aquifers)', loc='left', fontsize=12.5, color=INK)
ax.legend(loc='upper center', bbox_to_anchor=(0.45, -0.2), ncol=3, frameon=False, fontsize=10.5)

# (b) one aquifer in the drought (open loop, first weather sequence): the one where the watch gains most
gain = [r['open']['drought']['spir_ra']['over_s'] - r['open']['drought']['spir_roja']['over_s'] for r in rows]
r = rows[int(np.argmax(gain))]
S = r['series']['drought']
t = np.arange(len(S['Y'])) * 0.5
w0, w1 = D['w_dry']
bx.axvspan(w0 * 0.5, w1 * 0.5, color='#fde8c8', lw=0, zorder=0)
bx.text((w0 + w1) * 0.25, 0.97, 'drought, −2 sd', transform=bx.get_xaxis_transform(), ha='center', va='top', fontsize=10.5, color=MUTED)
bx.plot(t, cl(S['Y']), color=INK, lw=2, label='chloride at the screen (truth)')
bx.plot(t, cl(S['spir_ra']), color='#56b4e9', lw=1.6, label='prediction, yearly sample (S5)')
bx.plot(t, cl(S['spir_roja']), color='#009e73', lw=1.6, label='prediction, ROJA-GO')
bx.axhline(250, color='#c0392b', lw=1, ls='--'); bx.text(t[1], 258, '250 mg/L', va='bottom', fontsize=10.5, color='#c0392b')
fire = np.array(S['fire'], bool)
bx.plot(t[fire], np.full(fire.sum(), 0.04), '|', color='#009e73', ms=8, mew=1.5, transform=bx.get_xaxis_transform(), label='watch fires: extra sample')
bx.set_xlabel('years after the decision'); bx.set_ylabel('chloride (mg/L)')
bx.grid(axis='y', color=GRID, lw=0.8); bx.set_axisbelow(True)
for sp in ('top', 'right'): bx.spines[sp].set_visible(False)
bx.set_title('(b) One aquifer in the record drought (open loop)', loc='left', fontsize=12.5, color=INK)
bx.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False, fontsize=10.5)
fig.tight_layout()
out = os.path.join(HERE, 'res', 'figR1_extremes.png')
fig.savefig(out, dpi=200, bbox_inches='tight')
print(out, 'aquifer seed', r['seed'])
