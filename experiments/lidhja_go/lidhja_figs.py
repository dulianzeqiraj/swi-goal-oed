"""Figure of LIDHJA-GO: figL1_leak.png
(a) chloride difference between a wrong and the true exchanger inside a clay lens after 100 years of salinisation
    (Nernst-Planck); with equal diffusivities or without the electric field the difference is exactly zero;
(b) relative change of the chloride taken up (or released) by the lens, over time;
(c) the leak against the flow regime Pe = D_mech / D_Cl at equal mixing depth, with the bound of Theorem 2 and the
    Fushe-Kuqe regimes marked.
Colours: closure errors use two categorical slots (blue, orange); bound and references in ink and grey."""
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
R = json.load(open('lidhja_results.json'))
I_CL = 0
SAL = 'salinisation (fresh -> 5 % sea water)'
FRE = 'freshening (5 % sea water -> fresh)'
ERRS = [('E -30%', 'exchange capacity -30%', BLUE), ('K_Na\\Ca x1.5, K_Na\\Mg x1.5', 'selectivities K(Ca), K(Mg) ×1.5', ORANGE)]

fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.5), gridspec_kw=dict(width_ratios=[1.0, 1.1, 1.25]))
plt.subplots_adjust(left=0.065, right=0.985, top=0.88, bottom=0.17, wspace=0.34)
# (a) profile of the chloride difference inside the lens
for key, lab, col in ERRS:
    r = R['L'][SAL][key]['np']
    x = np.array(r['x'])
    u = np.array(r['profile_wrong'])[:, I_CL] - np.array(r['profile_true'])[:, I_CL]
    ax[0].plot(x, u * 35.453, color=col, lw=1.8, label=lab)
ax[0].axhline(0, color=INK2, lw=0.9)
ax[0].text(0.03, 0.03, 'equal diffusivities, or no electric\nfield: difference exactly 0', transform=ax[0].transAxes,
           ha='left', va='bottom', fontsize=6.8, color=INK2)
ax[0].set_xlabel('depth into the clay lens (m)')
ax[0].set_ylabel('Cl, wrong minus true exchanger (mg/L)')
ax[0].set_title('(a) leak inside a clay lens, 100 yr', fontsize=8.5)
ax[0].legend(frameon=False, fontsize=6.8, loc='center right', bbox_to_anchor=(1.0, 0.62))
ax[0].grid(color=GRID, lw=0.5); ax[0].set_axisbelow(True)
# (b) relative change of chloride uptake by the lens
for key, lab, col in ERRS:
    for scen, ls, sl in ((SAL, '-', 'salinisation'), (FRE, (0, (3, 2)), 'freshening')):
        r = R['L'][scen][key]['np']
        ax[1].plot(r['t'], 100 * np.array(r['rel_uptake']), color=col, lw=1.6, ls=ls)
ax[1].axhline(0, color=INK2, lw=0.9)
ax[1].plot([], [], color=INK2, lw=1.4, label='salinisation (fresh → 5 % sea water)')
ax[1].plot([], [], color=INK2, lw=1.4, ls=(0, (3, 2)), label='freshening (5 % → fresh)')
ax[1].legend(frameon=False, fontsize=6.8, loc='lower left')
ax[1].set_xlabel('years')
ax[1].set_ylabel('change of Cl uptake by the lens (%)')
ax[1].set_title('(b) the memory term of chloride', fontsize=8.5)
ax[1].grid(color=GRID, lw=0.5); ax[1].set_axisbelow(True)
# (c) leak against the flow regime
pes = sorted(R['P'], key=float)
pe = np.array([float(p) for p in pes])
leak = np.array([R['P'][p]['np']['sup_u'] for p in pes])
bnd = np.array([R['P'][p]['np']['bound_t'] for p in pes])
xx = 1 + pe
ax[2].loglog(xx, bnd, color=INK, lw=1.4, marker='s', ms=3.5, label='bound of Theorem 2')
ax[2].loglog(xx, leak, color=BLUE, lw=0, marker='o', ms=5, label='leak, Nernst–Planck')
ref = leak[0] / xx
ax[2].loglog(xx, ref, color=MUTED, lw=0.9, ls=(0, (3, 2)), label='slope −1')
ax[2].set_xlim(0.7, 3e5)
ax[2].set_ylim(1e-6 * leak[0], 3 * bnd.max())
ax[2].axvspan(1e5, 3e5, color='#f3e3c8', lw=0)
ax[2].text(1.5e5, bnd.max(), 'Fushë-Kuqe\naquifer\nPe ≈ 2×10⁵', ha='center', va='top', fontsize=6.6, color=INK2)
ax[2].annotate('clay lenses (Pe ≈ 0)', xy=(1, leak[0]), xytext=(12, leak[0] * 2.2), fontsize=6.6, color=INK2,
               arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.7))
xe = np.array([300, 2e5])
ax[2].loglog(xe, leak[0] / (1 + xe), color=MUTED, lw=0.9, ls=(0, (1, 2)))
ax[2].set_xlabel(r'$1+Pe$,   $Pe=D_{mech}/D_{Cl}$')
ax[2].set_ylabel(r'$\|\Delta c_{Cl}\|$ (mmol L$^{-1}$ m$^{1/2}$)')
ax[2].set_title('(c) the flow regime suppresses the leak', fontsize=8.5)
ax[2].legend(frameon=False, fontsize=6.8, loc='lower left')
ax[2].grid(color=GRID, lw=0.5, which='major'); ax[2].set_axisbelow(True)
fig.savefig('figL1_leak.png', dpi=220)
