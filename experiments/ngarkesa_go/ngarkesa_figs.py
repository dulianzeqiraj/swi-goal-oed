"""Figures for the NGARKESA-GO section. Reads ngarkesa_results.json and ngarkesa_grid.npz; writes figN1_transport.png
and figN2_design.png into this folder (English labels).   Run: python3 ngarkesa_figs.py"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
BLUE, ORANGE, GREEN = '#0072B2', '#E69F00', '#009E73'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.0, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK, 'figure.facecolor': 'white',
                     'axes.facecolor': 'white', 'savefig.facecolor': 'white', 'axes.spines.top': False,
                     'axes.spines.right': False})
R = json.load(open(os.path.join(HERE, 'ngarkesa_results.json')))
G = np.load(os.path.join(HERE, 'ngarkesa_grid.npz'))
P = R['params']
NF, NC = len(P['Fgrid']), len(P['CECgrid'])
Fg, Cg = np.array(P['Fgrid']), np.array(P['CECgrid'])


def grid_ax(ax):
    ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)


# ---------- Figure 1: transport ----------
fig, axs = plt.subplots(1, 3, figsize=(10.2, 3.5), gridspec_kw=dict(width_ratios=[1.0, 1.1, 1.0], wspace=0.38))
ax = axs[0]
x = G['x']
cols = {'Cl': (4, BLUE), 'Na': (0, ORANGE), 'Ca': (2, GREEN), 'Mg': (3, INK2)}
for name, (k, col) in cols.items():
    ax.plot(G['c1_mid_np'][k], x, color=col, lw=1.8)
    ax.plot(G['c1_mid_f1'][k], x, color=col, lw=1.2, ls='--')
    pos_lab = {'Cl': (128, 0.32), 'Na': (62, 0.30), 'Ca': (24, 0.62), 'Mg': (3, 0.95)}
    ax.text(pos_lab[name][0], pos_lab[name][1], name, color=col, fontsize=8, fontweight='bold', va='center')
ax.set_ylim(2.2, 0); ax.set_xlim(0, 150)
ax.set_xlabel('porewater concentration today (mmol/L)'); ax.set_ylabel('depth below the aquifer (m)')
ax.set_title('(a) after 40 years of intrusion', loc='left', fontsize=9)
ax.plot([], [], color=INK2, lw=1.8, label='electroneutral (Nernst–Planck)')
ax.plot([], [], color=INK2, lw=1.2, ls='--', label='one coefficient for all ions')
ax.legend(frameon=False, fontsize=7, loc='lower right')
grid_ax(ax)

ax = axs[1]
tcl = G['tcl_np'].reshape(NF, NC); tna = G['tna_np'].reshape(NF, NC)
for j, ls in ((0, ':'), (NC // 2, '-'), (NC - 1, '--')):
    ax.plot(Fg, tcl[:, j], color=BLUE, ls=ls, lw=1.5)
    ax.plot(Fg, tna[:, j], color=ORANGE, ls=ls, lw=1.5)
ax.axhline(P['deadline'], color=MUTED, lw=0.8)
ax.text(Fg[-1], P['deadline'] + 0.4, 'deadline', color=MUTED, fontsize=7, ha='right', va='bottom')
ax.annotate('chloride (all three CEC)', xy=(7.2, 17.6), xytext=(6.3, 25.5), color=BLUE, fontsize=8, fontweight='bold',
            arrowprops=dict(arrowstyle='-', color=BLUE, lw=0.8))
ax.text(3.6, tna[0, -1] + 1.2, 'sodium', color=ORANGE, fontsize=8, fontweight='bold')
for ls, lab in ((':', 'CEC 5'), ('-', 'CEC 17.5'), ('--', 'CEC 30 meq/100 g')):
    ax.plot([], [], color=INK2, ls=ls, lw=1.2, label=lab)
ax.legend(frameon=False, fontsize=7, loc='upper right')
ax.set_xscale('log'); ax.set_xticks([4, 6, 8, 10, 12]); ax.set_xticklabels(['4', '6', '8', '10', '12'])
ax.set_xlabel('formation factor F'); ax.set_ylabel('recovery time after freshening (years)')
ax.set_ylim(5, 37)
ax.set_title('(b) recovery times of the aquifer', loc='left', fontsize=9)
grid_ax(ax)

ax = axs[2]
rel = [100 * (G['tcl_f1'] / G['tcl_np'] - 1), 100 * (G['tna_f1'] / G['tna_np'] - 1),
       100 * (G['tcl_fi'] / G['tcl_np'] - 1), 100 * (G['tna_fi'] / G['tna_np'] - 1)]
pos = [0, 1, 2.6, 3.6]
colr = [BLUE, ORANGE, BLUE, ORANGE]
for p_, r_, c_ in zip(pos, rel, colr):
    lo, med, hi = np.percentile(r_, [0, 50, 100])
    ax.plot([p_, p_], [lo, hi], color=c_, lw=6, alpha=0.35, solid_capstyle='round')
    ax.plot([p_ - 0.22, p_ + 0.22], [med, med], color=c_, lw=2)
ax.axhline(0, color=INK2, lw=0.8)
ax.set_xticks(pos); ax.set_xticklabels(['Cl', 'Na', 'Cl', 'Na'])
ax.text(0.5, -14.5, 'one coefficient\n(electroneutral)', ha='center', fontsize=7, color=INK2)
ax.text(3.1, -14.5, 'own coefficients,\nno coupling', ha='center', fontsize=7, color=INK2)
ax.text(3.1, 21.5, f"charge error up to\n{R['structure']['fick_i']['charge_max']:.0f} mmol/L", ha='center', fontsize=7, color='#C0392B')
ax.set_ylim(-18, 30); ax.set_xlim(-0.7, 4.3)
ax.set_ylabel('error of the recovery time (%)')
ax.set_title('(c) simplified transport models', loc='left', fontsize=9)
grid_ax(ax)
fig.text(0.5, 0.005, f"Middle of the prior (F = {Fg[NF // 2]:.1f}, CEC = {Cg[NC // 2]:.1f} meq/100 g) in (a); bars in (c) span the prior grid, ticks are medians.",
         ha='center', fontsize=7, color=MUTED)
fig.subplots_adjust(left=0.06, right=0.99, top=0.9, bottom=0.17)
fig.savefig(os.path.join(HERE, 'figN1_transport.png'), dpi=220)
plt.close(fig)

# ---------- Figure 2: design ----------
D = R['designs']
order = ['L', 'R', 'R+L', 'C', 'C+L', 'I']
lab = {'L': 'lab\nCEC', 'R': 'resis-\ntivity', 'R+L': 'resis-\ntivity\n+ CEC', 'C': 'Cl\nprofile', 'C+L': 'Cl\nprofile\n+ CEC', 'I': 'major\nions'}
fig, axs = plt.subplots(1, 3, figsize=(10.2, 3.8), gridspec_kw=dict(width_ratios=[1.3, 1.1, 1.0], wspace=0.34))
ax = axs[0]
xx = np.arange(len(order)); w = 0.36
ax.bar(xx - w / 2 - 0.01, [100 * D[d]['correct_cl'] for d in order], w, color=BLUE)
ax.bar(xx + w / 2 + 0.01, [100 * D[d]['correct_na'] for d in order], w, color=ORANGE)
ax.axhline(100 * R['prior']['p_cl_by_deadline'], color=MUTED, lw=0.8, ls=':')
ax.set_xticks(xx); ax.set_xticklabels([lab[d] for d in order], fontsize=6.8)
ax.set_ylim(50, 110); ax.set_yticks(range(50, 101, 10)); ax.set_ylabel('correct deadline decisions (%)')
ax.legend(handles=[Patch(color=BLUE, label='chloride goal'), Patch(color=ORANGE, label='sodium goal')], frameon=False, fontsize=7, loc='upper left', ncol=2)
ax.set_title('(a) the goals', loc='left', fontsize=9)
grid_ax(ax)

ax = axs[1]
ax.bar(xx, [D[d]['info_gain_nats'] for d in order], 0.6, color=INK2)
for i, d in enumerate(order):
    ax.text(i, D[d]['info_gain_nats'] + 0.08, f"{D[d]['info_gain_nats']:.2f}", ha='center', fontsize=6.5, color=INK2)
ax.set_xticks(xx); ax.set_xticklabels([lab[d] for d in order], fontsize=6.8)
ax.set_ylabel('information about F and CEC (nats)')
ax.set_title('(b) the parameters', loc='left', fontsize=9)
ax.set_ylim(0, 5.9)
grid_ax(ax)

ax = axs[2]
sel = ['R', 'C', 'I']
xs = np.arange(len(sel)); w = 0.2
vals = [('correct_cl', BLUE, 1.0), ('fick1_correct_cl', BLUE, 0.4), ('correct_na', ORANGE, 1.0), ('fick1_correct_na', ORANGE, 0.4)]
for k, (key, col, al) in enumerate(vals):
    ax.bar(xs + (k - 1.5) * w, [100 * D[d][key] for d in sel], w * 0.95, color=col, alpha=al)
ax.set_xticks(xs); ax.set_xticklabels([lab[d] for d in sel], fontsize=6.8)
ax.set_ylim(50, 114); ax.set_yticks(range(50, 101, 10)); ax.set_ylabel('correct deadline decisions (%)')
ax.legend(handles=[Patch(color=INK2, label='electroneutral model'), Patch(color=INK2, alpha=0.4, label='one coefficient for all ions')], frameon=False, fontsize=7, loc='upper left')
ax.set_title('(c) the model used to read the data', loc='left', fontsize=9)
grid_ax(ax)
fig.text(0.5, 0.005, f"Dotted line in (a): no data (prior). Deadline {P['deadline']:.0f} years; {P['ndraw']} noisy data sets for each of the {NF * NC} prior parameter sets; profiles at 4 depths (5 % error), resistivity 20 %, lab CEC 15 %.",
         ha='center', fontsize=7, color=MUTED)
fig.subplots_adjust(left=0.06, right=0.99, top=0.9, bottom=0.24)
fig.savefig(os.path.join(HERE, 'figN2_design.png'), dpi=220)
plt.close(fig)
print('figures written')
