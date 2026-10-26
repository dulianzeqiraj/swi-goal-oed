"""Figure R1 of RREZJA-GO (review 58) from res/rrezja.json."""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'res', 'rrezja.json')))
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#e3e6ea', 'grid.linewidth': 0.6, 'axes.edgecolor': '#9aa3ad'})
INK, MUTED = '#1f2328', '#5b6573'
COL = ['#2a78d6', '#1baf7a', '#e8a317', '#7d4fc9', '#e4572e']        # stakeholders, fixed order (as VENDIMI-GO)
SHORT = ['utility', 'irrigators, hotels', 'municipality', 'water agency', 'environmental']
RULES = [('vendimi', 'five stated beliefs\n(VENDIMI-GO)', '#8a8f98'), ('ball_z2_env', 'ball, 2 drivers\nρ = ρ_env', '#2a78d6'),
         ('ball_z8_env', 'ball, 8 drivers\nρ = ρ_env', '#1baf7a'), ('ball_z8_max', 'ball, 8 drivers\nρ = ρ_max', '#7d4fc9'),
         ('full_env', 'full ball\nρ = ρ_env', '#e4572e')]
DES = [('none', 'no data'), ('chloride sample (A30)', 'one chloride sample')]

fig, ax = plt.subplots(2, 2, figsize=(11.2, 8.0))
# (a) radii
a = ax[0, 0]
st = R['stakeholders']; pr = R['posterior_radii']
x = np.arange(5)
a.bar(x - 0.18, [s['kl'] for s in st], 0.34, color=COL, edgecolor='white', linewidth=1.5, label='before data')
med, lo, hi = np.array(pr['median']), np.array(pr['q10']), np.array(pr['q90'])
a.bar(x + 0.18, med, 0.34, color=COL, alpha=0.45, edgecolor='white', linewidth=1.5, label='after the chloride sample (median)')
a.errorbar(x + 0.18, med, yerr=[med - lo, hi - med], fmt='none', ecolor=MUTED, elinewidth=1, capsize=2)
for v, t in ((R['rho_env'], 'ρ_env'), (R['rho_max'], 'ρ_max')):
    a.axhline(v, color=INK, lw=0.8, ls=':'); a.text(-0.45, v, t, va='bottom', ha='left', fontsize=8, color=INK)
a.set_xticks(x); a.set_xticklabels(SHORT, rotation=12)
a.set_ylabel('relative entropy from the calibration (nats)')
a.set_title('(a) How far each stated belief is from the calibration', loc='left', fontsize=10)
from matplotlib.patches import Patch
a.legend(handles=[Patch(color='#5b6573', label='before data'), Patch(color='#5b6573', alpha=0.45, label='after the chloride sample (median, 10–90%)')],
         frameon=False, fontsize=8, loc='upper right', bbox_to_anchor=(1.0, 0.97))
# (b) frontier
b = ax[0, 1]
fr = R['frontier']
for (dn, lab), c in zip(DES, ('#5b6573', '#1baf7a')):
    rg = np.array(fr[dn]['rho'])
    b.plot(rg, fr[dn]['ball_z8'], '-o', color=c, ms=3.5, lw=2, label=f'tilt ball, 8 drivers ({lab})')
    b.plot(rg, fr[dn]['full'], '--', color=c, lw=1.4, label=f'full ball ({lab})')
    b.scatter([R['rho_env']], [R['designs'][dn]['vendimi']['net']], marker='*', s=110, color=c, edgecolor=INK, linewidth=0.6, zorder=5)
for v in (R['rho_env'], R['rho_max']):
    b.axvline(v, color=INK, lw=0.8, ls=':')
b.set_ylim(-16000, 9500)
b.text(R['rho_env'], 9300, ' ρ_env', fontsize=8, va='top')
b.text(R['rho_max'], 9300, ' ρ_max', fontsize=8, va='top')
b.set_xlabel('radius of belief ρ (nats)'); b.set_ylabel('net water (m³/d)')
b.set_title('(b) One number to agree on: net water against the radius', loc='left', fontsize=10)
b.legend(frameon=False, fontsize=7.5, loc='lower left')
b.text(0.98, 0.30, '★ five stated beliefs (VENDIMI-GO),\ndrawn at ρ_env for comparison', transform=b.transAxes, ha='right', va='top', fontsize=7.5, color=MUTED)
# (c) unstated beliefs
c = ax[1, 0]
w = 0.38
for j, (dn, lab) in enumerate(DES):
    vals = [R['designs'][dn][k]['unstated_z8_env']['max'] for k, _, _ in RULES]
    ses = [R['designs'][dn][k]['unstated_z8_env']['se_at_max'] for k, _, _ in RULES]
    xs = np.arange(len(RULES)) + (j - 0.5) * w
    c.bar(xs, vals, w * 0.92, color=[r[2] for r in RULES], alpha=1.0 if j == 0 else 0.5, edgecolor='white', linewidth=1.2,
          label=lab)
    c.errorbar(xs, vals, yerr=ses, fmt='none', ecolor=INK, elinewidth=0.8, capsize=2)
c.axhline(R['alpha'], color=INK, lw=1, ls=':'); c.text(4.6, R['alpha'], 'agreed limit 10%', ha='right', va='bottom', fontsize=8)
c.set_xticks(np.arange(len(RULES))); c.set_xticklabels([r[1] for r in RULES], fontsize=7.5)
c.set_ylabel('largest realised risk among unstated beliefs')
c.set_title('(c) Beliefs nobody stated, at the radius ρ_env', loc='left', fontsize=10)
c.legend(frameon=False, fontsize=8, loc='upper right', title='solid: no data; light: chloride sample', title_fontsize=7.5)
# (d) price
d = ax[1, 1]
for j, (dn, lab) in enumerate(DES):
    vals = [R['designs'][dn][k]['net'] for k, _, _ in RULES]
    xs = np.arange(len(RULES)) + (j - 0.5) * w
    d.bar(xs, vals, w * 0.92, color=[r[2] for r in RULES], alpha=1.0 if j == 0 else 0.5, edgecolor='white', linewidth=1.2)
    for xx, v in zip(xs, vals):
        d.text(xx, v + (150 if v >= 0 else -150), f'{v:,.0f}', ha='center', va='bottom' if v >= 0 else 'top', fontsize=6.5, color=INK)
d.axhline(0, color=MUTED, lw=0.8)
d.set_xticks(np.arange(len(RULES))); d.set_xticklabels([r[1] for r in RULES], fontsize=7.5)
d.set_ylabel('net water: pumped − 0.5 × recharged (m³/d)')
d.set_title('(d) The water each rule gives (solid: no data; light: chloride)', loc='left', fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(HERE, 'res', 'figR1_rrezja.png'), dpi=200)
print('wrote res/figR1_rrezja.png')
