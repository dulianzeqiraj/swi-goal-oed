"""Figure M1 of MOTI-GO (review 59) from res/moti.json."""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(HERE, 'res', 'moti.json')))
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#e3e6ea', 'grid.linewidth': 0.6, 'axes.edgecolor': '#9aa3ad'})
INK, MUTED = '#1f2328', '#5b6573'
RULES = [('FW', 'fair-weather plan', '#8a8f98'), ('IC', 'decided in the crisis', '#e8a317'), ('PC', 'pre-committed plan (MOTI-GO)', '#1baf7a')]
REGS = [r['name'].replace('Extreme drought with heatwave', 'Extreme drought\n+ heatwave').replace('Extreme drought', 'Extreme\ndrought') if 'heatwave' not in r['name'] else 'Extreme drought\n+ heatwave' for r in J['regimes']]
QSUM = 12060.0
P = J['plans']
fig, ax = plt.subplots(2, 2, figsize=(11.2, 8.0))
x = np.arange(len(P)); w = 0.26
# (a) realised risk
a = ax[0, 0]
for j, (k, lab, c) in enumerate(RULES):
    v = [p[k]['risk'] for p in P]; wv = [max(p[k]['risk_by_view']) for p in P]
    a.bar(x + (j - 1) * w, v, w * 0.92, color=c, edgecolor='white', linewidth=1.2, label=lab)
    a.scatter(x + (j - 1) * w, wv, marker='_', s=140, color=INK, linewidth=1.6, zorder=4)
a.axhline(J['alpha'], color=INK, lw=1, ls=':'); a.text(-0.45, J['alpha'] + 0.01, 'agreed limit 10%', fontsize=8)
a.set_xticks(x); a.set_xticklabels(REGS, fontsize=8)
a.set_ylabel('realised probability that A1 or P10 exceeds 250 mg/L')
a.set_title('(a) Realised risk (bars: calibrated; ticks: most cautious belief)', loc='left', fontsize=9.5)
a.legend(frameon=False, fontsize=8, loc='upper left')
# (b) pumped water
b = ax[0, 1]
for j, (k, lab, c) in enumerate(RULES):
    v = [p[k]['water'] for p in P]
    b.bar(x + (j - 1) * w, v, w * 0.92, color=c, edgecolor='white', linewidth=1.2, label=lab)
    for xx, p in zip(x + (j - 1) * w, P):
        if p[k]['stop']:
            b.text(xx, 250, 'stop', rotation=90, ha='center', va='bottom', fontsize=7, color=INK)
        elif p[k]['water'] == 0:
            b.text(xx, 250, 'no pumping', rotation=90, ha='center', va='bottom', fontsize=7, color=INK)
b.set_xticks(x); b.set_xticklabels(REGS, fontsize=8)
b.set_ylabel('licensed pumping at A1 + P10 (m³/d)')
b.set_title('(b) Water supplied ("stop": emergency stop)', loc='left', fontsize=9.5)
# (c) rule curve
c = ax[1, 0]
cols = {'0': '#8a8f98', '5000': '#2a78d6', '10000': '#7d4fc9'}
for heat, ls in (('no heatwave', '-'), ('heatwave', '--')):
    cv = J['rule_curve'][heat]
    f = np.array([p['f'] for p in cv])
    for q, col in cols.items():
        s = np.array([np.nan if p['cap_by_q'][q] is None else p['cap_by_q'][q] for p in cv])
        lab = f'recharge {int(q) // 1000 if q != "0" else 0}' + (',000 m³/d per site' if q != '0' else ' m³/d') if heat == 'no heatwave' else None
        c.plot(f, s * QSUM, ls, color=col, lw=2 if heat == 'no heatwave' else 1.4, label=lab)
for r in J['regimes']:
    c.axvline(r['fR'], color=MUTED, lw=0.6, ls=':')
c.text(1.0, 21600, 'normal', fontsize=7.5, ha='center', color=MUTED)
c.text(0.75, 21600, 'dry', fontsize=7.5, ha='center', color=MUTED)
c.text(0.5, 21600, 'extreme', fontsize=7.5, ha='center', color=MUTED)
c.set_ylim(-500, 22500)
c.set_xlabel('recharge factor f (1 = normal year)'); c.set_ylabel('largest licensed pumping all stakeholders accept (m³/d)')
c.set_title('(c) The rule curve: pumping cap against drought (dashed: with heatwave)', loc='left', fontsize=9.5)
c.legend(frameon=False, fontsize=7.5, loc='lower right')
# (d) attribution
d = ax[1, 1]
comp = [('base', 'normal-year risk', '#c4c8cf'), ('climate', 'drought (climate)', '#e4572e'), ('operational', 'operators overshoot (objective human)', '#e8a317'),
        ('unlicensed', 'unlicensed coastal pumping (objective human)', '#7d4fc9')]
bottom = np.zeros(len(P))
for k, lab, col in comp:
    v = np.array([p['attribution_FW'][k] for p in P])
    d.bar(x, v, 0.55, bottom=bottom, color=col, edgecolor='white', linewidth=1.2, label=lab)
    bottom += v
for xx, t in zip(x, bottom):
    d.text(xx, t + 0.01, f'{t:.2f}', ha='center', fontsize=8)
d.axhline(J['alpha'], color=INK, lw=1, ls=':')
d.set_xticks(x); d.set_xticklabels(REGS, fontsize=8)
d.set_ylabel('risk of the fair-weather plan (Shapley shares)')
d.set_title('(d) Where the risk comes from if nothing is adapted', loc='left', fontsize=9.5)
d.legend(frameon=False, fontsize=7.5, loc='upper left')
fig.tight_layout()
fig.savefig(os.path.join(HERE, 'res', 'figM1_moti.png'), dpi=200)
print('wrote res/figM1_moti.png')
