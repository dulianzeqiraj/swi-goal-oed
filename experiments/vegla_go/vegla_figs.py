"""Figures for the VEGLA-GO section. Reads vegla_results.json and writes figV1_designs.png and figV2_rule.png
into this folder (English labels).   Run: python3 vegla_figs.py"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
CAT = ['#0072B2', '#E69F00', '#009E73']          # fixed order: first, second, third design of a budget
RED = '#C0392B'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.0, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK, 'figure.facecolor': 'white',
                     'axes.facecolor': 'white', 'savefig.facecolor': 'white', 'axes.spines.top': False,
                     'axes.spines.right': False})
R = json.load(open(os.path.join(HERE, 'vegla_results.json')))
NS = R['n']
LAB = {'none': 'none', 'H': 'H', 'A': 'A', 'R': 'R', 'H+A': 'H+A', 'H+R': 'H+R', 'A+R': 'A+R', 'H+A+R': 'H+A+R'}

# ---------------- Figure V1: structural information versus validity, and finite records
fig = plt.figure(figsize=(6.6, 2.9))
gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1, 1], wspace=0.38, left=0.07, right=0.985, bottom=0.22, top=0.88)
ax = fig.add_subplot(gs[0, 0])
for kind, mk in (('phys', 'o'), ('flat', 's')):
    ex = R['exact'][kind]
    for d in R['designs']:
        x, y = ex[d]['H_sig'], 100 * ex[d]['resolved']
        col = INK if d in ('none', 'H+A+R') else (CAT[['H', 'A', 'R'].index(d)] if len(d) == 1 else CAT[['H+A', 'H+R', 'A+R'].index(d)])
        ax.plot(x, y, mk, ms=5.2 if kind == 'phys' else 4.6, mfc=col if kind == 'phys' else 'white', mec=col, mew=1.1, zorder=3)
        if kind == 'phys':
            dx, dy, ha = 0.25, -1.0, 'left'
            if d == 'A+R': dx, dy = 0.25, -3.6
            if d == 'H+R': dx, dy, ha = -0.25, 2.0, 'right'
            if d == 'H+A': dx, dy, ha = -0.25, -4.6, 'right'
            if d == 'R': dx, dy = 0.25, 1.6
            if d == 'A': dx, dy = 0.25, -3.4
            if d == 'H': dx, dy, ha = -0.25, 0.8, 'right'
            if d == 'H+A+R': dx, dy, ha = -0.25, 2.0, 'right'
            if d == 'none': dx, dy = 0.45, -1.6
            ax.text(x + dx, y + dy, LAB[d], fontsize=6.8, color=INK2, ha=ha)
ax.plot([], [], 'o', color=INK2, ms=4.5, label='physical prior'); ax.plot([], [], 's', mfc='white', mec=INK2, ms=4.2, label='flat prior')
ax.legend(frameon=False, fontsize=6.2, loc='lower right', handletextpad=0.3)
ax.set_xlabel('structural information H(signature) (bit)', fontsize=7)
ax.set_ylabel('validity settled, large samples (%)', fontsize=7)
ax.set_title('(a) graph information vs. the goal', fontsize=7.6, loc='left')
ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True); ax.set_ylim(0, 80)

for j, (designs, title) in enumerate(((['H', 'A', 'R'], '(b) one extra measurement'), (['H+A', 'H+R', 'A+R'], '(c) two extra measurements'))):
    ax = fig.add_subplot(gs[0, 1 + j])
    for ref, ls in (('none', ':'), ('H+A+R', '--')):
        y = [100 * R['sim']['phys'][str(n)][ref]['calibrated']['correct'] for n in NS]
        ax.plot(NS, y, ls, color=MUTED, lw=1.0)
        ax.text(NS[-1] * 1.06, y[-1], 'none' if ref == 'none' else 'all three', fontsize=6.3, color=MUTED, va='center')
    ends = []
    for c, d in zip(CAT, designs):
        y = [100 * R['sim']['phys'][str(n)][d]['calibrated']['correct'] for n in NS]
        ax.plot(NS, y, '-o', color=c, lw=1.4, ms=3.8, mec='white', mew=0.5)
        ends.append([y[-1], d, c])
    ends.sort()
    for k in range(1, len(ends)):                      # keep end labels at least 3.6 points apart
        ends[k][0] = max(ends[k][0], ends[k - 1][0] + 3.6)
    for yv, d, c in ends:
        ax.text(NS[-1] * 1.06, yv, d, fontsize=6.8, color=c, va='center', fontweight='bold')
    ax.set_xscale('log'); ax.set_xticks(NS); ax.set_xticklabels([str(n) for n in NS]); ax.minorticks_off()
    ax.set_xlim(100, 1900); ax.set_ylim(0, 75)
    ax.set_xlabel('record length n', fontsize=7)
    if j == 0:
        ax.set_ylabel('correct validity decisions (%)', fontsize=7)
    ax.set_title(title, fontsize=7.6, loc='left')
    ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
fig.text(0.5, 0.005, 'Physical prior in (b)–(c); false certification calibrated to 5 %. H: coastal head, A: agricultural pumping, R: recharge.',
         ha='center', va='bottom', fontsize=6.3, color=INK2)
fig.savefig(os.path.join(HERE, 'figV1_designs.png'), dpi=230)
plt.close(fig)

# ---------------- Figure V2: the well-field graph and the danger of uncalibrated certification
fig = plt.figure(figsize=(6.6, 3.0))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.2], wspace=0.2, left=0.01, right=0.985, bottom=0.1, top=0.88)
ax = fig.add_subplot(gs[0, 0]); ax.set_xlim(0, 10); ax.set_ylim(-1.9, 7.6); ax.set_aspect('equal'); ax.axis('off')
P = {'Z': (1.0, 3.6), 'Q': (3.6, 3.6), 'H': (6.2, 3.6), 'C': (8.8, 3.6), 'A': (4.9, 1.0), 'R': (4.9, 6.4)}
full = {'Z': 'Z instrument', 'Q': 'Q pumping', 'H': 'H head', 'C': 'C chloride', 'A': 'A agric. pumping', 'R': 'R recharge'}
for v, (x, y) in P.items():
    obs = v in ('Z', 'Q', 'C')
    ax.add_patch(plt.Circle((x, y), 0.55, fc='white' if not obs else '#eef3fa', ec=INK if obs else MUTED, lw=1.2, ls='-' if obs else '--', zorder=3))
    ax.text(x, y, v, ha='center', va='center', fontsize=9, fontweight='bold', color=INK, zorder=4)
    if v == 'R':
        tx, ty, ha = x + 0.7, y + 0.45, 'left'
    elif v == 'A':
        tx, ty, ha = x + 0.7, y - 0.45, 'left'
    else:
        tx, ty, ha = x, y - 0.85, 'center'
    ax.text(tx, ty, full[v].split(' ', 1)[1], ha=ha, va='center', fontsize=6.0, color=INK2, zorder=4)


def arrow(a, b, color=INK, ls='-', rad=0.0, lw=1.2, both=False):
    (x1, y1), (x2, y2) = P[a], P[b]
    ar = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='<|-|>' if both else '-|>', mutation_scale=8, color=color, lw=lw,
                         ls=ls, connectionstyle=f'arc3,rad={rad}', shrinkA=15, shrinkB=15, zorder=2)
    ax.add_patch(ar)


for a, b in (('Z', 'Q'), ('Q', 'H'), ('H', 'C')):
    arrow(a, b, INK, lw=1.6)
for a, b, rad in (('R', 'H', 0.0), ('R', 'Q', 0.0), ('R', 'A', 0.0), ('A', 'H', 0.0), ('Q', 'C', -0.35), ('A', 'C', 0.15)):
    arrow(a, b, MUTED, rad=rad, lw=0.9)
arrow('C', 'Q', '#0072B2', rad=-0.55, lw=1.3)
for a, b, rad in (('Z', 'A', 0.0), ('Z', 'H', 0.42)):
    arrow(a, b, RED, ls='--', rad=rad, lw=1.2)
for a, b, rad in (('Z', 'R', -0.25), ('Z', 'C', -0.62)):
    arrow(a, b, RED, ls=':', rad=rad, lw=1.2, both=True)
for a, b, rad in (('Q', 'A', 0.3), ('H', 'C', 0.5), ('Q', 'C', 0.75)):
    arrow(a, b, MUTED, ls=':', rad=rad, lw=0.8, both=True)
ax.set_title('(a) the well field and its candidate edges', fontsize=7.6, loc='left')
for k, line in enumerate(['black: fixed edges · grey: optional edges · blue: feedback C→Q',
                          'red: edges that break the instrument · dotted arcs: latent confounders',
                          'shaded nodes: always observed (Z, Q, C)']):
    ax.text(0.0, -0.55 - 0.48 * k, line, fontsize=5.7, color=INK2, va='center')

ax = fig.add_subplot(gs[0, 1])
n = '240'
ds = R['designs']
x = np.arange(len(ds))
fo = [100 * R['sim']['phys'][n][d]['certify_invalid'] for d in ds]
fc = [100 * R['sim']['phys'][n][d]['calibrated']['certify_invalid'] for d in ds]
co = [100 * R['sim']['phys'][n][d]['certify_valid'] for d in ds]
cc = [100 * R['sim']['phys'][n][d]['calibrated']['certify_valid'] for d in ds]
wb = 0.36
ax.bar(x - wb / 2, fo, wb * 0.94, color=RED, label='invalid instrument certified, optimum rule')
ax.bar(x + wb / 2, fc, wb * 0.94, color='#f2b8b0', label='invalid instrument certified, calibrated rule')
ax.plot(x - wb / 2, co, '_', color=INK, ms=9, mew=1.6, label='valid instrument certified (optimum / calibrated)')
ax.plot(x + wb / 2, cc, '_', color=INK, ms=9, mew=1.6)
ax.axhline(5, color=INK2, lw=0.7, ls=':')
ax.text(len(ds) - 0.45, 6.3, '5 %', fontsize=6.3, color=INK2, ha='right')
ax.set_xticks(x); ax.set_xticklabels([LAB[d] for d in ds], fontsize=6.8)
ax.set_ylabel('instruments certified (%)', fontsize=7); ax.set_ylim(0, 128); ax.set_yticks([0, 20, 40, 60, 80, 100])
bias = R['sim']['phys'][n]['H+A+R']['false_cert_rel_bias']
ax.set_title(f'(b) certification with n = {n} records (physical prior)', fontsize=7.6, loc='left')
ax.legend(frameon=False, fontsize=6.0, loc='upper left', bbox_to_anchor=(0.0, 1.02))
ax.text(2.6, 50, f'falsely certified instruments:\nmedian IV bias ≈ {bias:.1f} × the effect (H+A+R)',
        fontsize=6.2, color=RED, ha='center', va='center')
ax.grid(axis='y', color=GRID, lw=0.6); ax.set_axisbelow(True)
fig.savefig(os.path.join(HERE, 'figV2_rule.png'), dpi=230)
plt.close(fig)
print('figures written')
