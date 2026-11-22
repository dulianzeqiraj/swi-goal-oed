"""Figure of FILLIMI-GO: figF1_handover.png
(a) goal variance from the initial condition (solid) and from the boundary forcing (dashed) for a mobile-head goal
    1 km from the sea and a piezometer in the clay, with power-law aquitard memory, and the no-memory mobile goal;
(b) fitted tail exponents of the initial-condition variance against beta, with the predictions -(beta+2) and -beta;
(c) share of the initial condition in the goal variance over time, by distance of the goal from the sea.
Colours: categorical slots blue (mobile goals), orange (clay goal); no-memory reference in grey."""
import json
import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#c3c2b7', 'xtick.color': '#52514e', 'ytick.color': '#52514e',
                     'axes.labelcolor': '#0b0b0b'})
INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#898781', '#e1e0d9'
BLUE, ORANGE = '#2a78d6', '#eb6834'
RAMP = ['#cfe2f7', '#86b6ef', '#2a78d6', '#104281']
R = json.load(open('fillimi_results.json'))
TL = json.load(open('fillimi_tails.json'))
t = np.array(R['times'])
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.5), gridspec_kw=dict(width_ratios=[1.25, 0.9, 1.1]))
plt.subplots_adjust(left=0.06, right=0.985, top=0.88, bottom=0.17, wspace=0.36)
# (a)
for case, g, col, lab in (('none', 'mobile 1000 m', MUTED, 'head 1 km from the sea, no memory'),
                          ('power', 'mobile 1000 m', BLUE, 'head 1 km from the sea, clay memory'),
                          ('power', 'clay 2500 m', ORANGE, 'piezometer in the clay')):
    o = R['cases'][case][g]
    ax[0].loglog(t, o['vic'], color=col, lw=1.8, label=lab)
    ax[0].loglog(t, o['vbc'], color=col, lw=1.2, ls=(0, (3, 2)))
    if o['handover']:
        th = o['handover']; v = np.interp(np.log(th), np.log(t), np.log(o['vbc']))
        ax[0].plot([th], [np.exp(v)], marker='o', ms=5, color=col, mec='white', mew=1.0, zorder=5)
ax[0].set_ylim(1e-8, 30)
th = R['cases']['power']['clay 2500 m']['handover']
vh = np.exp(np.interp(np.log(th), np.log(t), np.log(R['cases']['power']['clay 2500 m']['vbc'])))
ax[0].annotate(f'handover after {th:.0f} yr', xy=(th, vh), xytext=(4, 0.004), fontsize=6.8, color=INK2,
               arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.7))
ax[0].plot([], [], color=INK2, lw=1.8, label='initial condition')
ax[0].plot([], [], color=INK2, lw=1.2, ls=(0, (3, 2)), label='boundary forcing')
ax[0].legend(frameon=False, fontsize=6.6, loc='lower left', ncol=1)
ax[0].set_xlabel('years after the start of the forecast')
ax[0].set_ylabel('goal variance (m$^2$)')
ax[0].set_title('(a) who controls the forecast, and when', fontsize=8.5)
ax[0].grid(color=GRID, lw=0.5, which='major'); ax[0].set_axisbelow(True)
# (b)
betas = np.array([0.3, 0.5, 0.7])
bb = np.linspace(0.2, 0.8, 10)
ax[1].plot(bb, -(bb + 2), color=BLUE, lw=1.0, ls=(0, (3, 2)))
ax[1].plot(bb, -bb, color=ORANGE, lw=1.0, ls=(0, (3, 2)))
ax[1].plot(betas, [TL[str(b)]['mobile 1000 m'] for b in betas], 'o', color=BLUE, ms=6, mec='white', mew=1.0, label='head in the aquifer: $-(\\beta+2)$')
ax[1].plot(betas, [TL[str(b)]['clay 2500 m'] for b in betas], 's', color=ORANGE, ms=6, mec='white', mew=1.0, label='piezometer in the clay: $-\\beta$')
ax[1].set_xlabel('index $\\beta$ of the memory spectrum')
ax[1].set_ylabel('tail exponent of the initial-condition variance')
ax[1].set_title('(b) boundary screening of memory', fontsize=8.5)
ax[1].legend(frameon=False, fontsize=6.6, loc='center left', bbox_to_anchor=(0.0, 0.55))
ax[1].set_ylim(-3.1, 0)
ax[1].grid(color=GRID, lw=0.5); ax[1].set_axisbelow(True)
# (c)
for g, col in zip(['mobile 250 m', 'mobile 1000 m', 'mobile 2500 m', 'mobile 4750 m'], RAMP):
    o = R['cases']['power'][g]
    share = np.array(o['vic']) / (np.array(o['vic']) + np.array(o['vbc']))
    ax[2].semilogx(t, 100 * share, color=col, lw=1.6, label=g.replace('mobile', 'head at'))
o = R['cases']['power']['clay 2500 m']
ax[2].semilogx(t, 100 * np.array(o['vic']) / (np.array(o['vic']) + np.array(o['vbc'])), color=ORANGE, lw=1.8, label='clay at 2500 m')
ax[2].axhline(50, color=INK2, lw=0.8)
ax[2].set_ylim(0, 100)
ax[2].set_xlabel('years after the start of the forecast')
ax[2].set_ylabel('share of the initial condition (%)')
ax[2].set_title('(c) the initial state fades fast near the sea', fontsize=8.5)
ax[2].legend(frameon=False, fontsize=6.6, loc='upper right')
ax[2].grid(color=GRID, lw=0.5); ax[2].set_axisbelow(True)
fig.savefig('figF1_handover.png', dpi=220)
