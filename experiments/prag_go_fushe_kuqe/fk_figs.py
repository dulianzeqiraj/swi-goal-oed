"""Figures for the PRAG-GO Fushe-Kuqe note (static PNG for Word, light theme).
Palette: sequential blue ramp for probabilities and fields, categorical slot 2 (orange) for the
selected wells / sites, neutral inks for text, candidates, boundary and the toe."""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, PowerNorm
from scipy.stats import spearmanr
from fk import FK, default_xlsx

FIG = sys.argv[1] if len(sys.argv) > 1 else 'fig'
os.makedirs(FIG, exist_ok=True)
INK, INK2, MUTED = '#0b0b0b', '#52514e', '#8a8984'
ORANGE, BLUE = '#eb6834', '#2a78d6'
SEQ = LinearSegmentedColormap.from_list('blue', ['#f3f7fd', '#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b'])
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.0, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK, 'figure.facecolor': 'white',
                     'axes.facecolor': 'white', 'savefig.facecolor': 'white'})

m = FK(default_xlsx()).design_fields()
L = np.load('res_base/lin.npz', allow_pickle=True); M = json.load(open('res_base/meta.json'))
ids = L['ids'].astype(str); xy = L['xy']; CAND = np.array(M['CAND']); iA, iB = M['iA'], M['iB']
if not os.path.exists('H1000.npy'):          # prior intrusion map from 1 000 realizations
    LG = np.linalg.cholesky(m.Gam); rng = np.random.default_rng(1)
    np.save('H1000.npy', np.array([m.solve(LG @ rng.standard_normal(m.Nz)) for _ in range(1000)]))
H = np.load('H1000.npy'); P = (H < 1.0).mean(0)


def grid(vals):
    G = np.full((m.ny, m.nx), np.nan); G[m.aj, m.ai] = vals; return G


def base_map(ax, field, vmin, vmax, cmap=SEQ, norm=None):
    ext = [-m.dx / 2, m.xs[-1] + m.dx / 2, -m.dx / 2, m.ys[-1] + m.dx / 2]
    kw = dict(norm=norm) if norm is not None else dict(vmin=vmin, vmax=vmax)
    im = ax.imshow(grid(field), origin='lower', extent=ext, cmap=cmap, interpolation='nearest', **kw)
    ax.plot(m.Bk[:, 0], m.Bk[:, 1], color=INK2, lw=0.6)
    ax.contour(m.xs, m.ys, grid(m.h0), levels=[1.0], colors=[INK], linewidths=0.9, linestyles='--')
    ax.set_xlim(0, 21.5); ax.set_ylim(0, 52.5); ax.set_aspect('equal')
    ax.set_xticks([0, 10, 20]); ax.set_yticks([0, 10, 20, 30, 40, 50])
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)
    return im


def wells(ax, sel=(), labels=True, cand=True):
    if cand:
        ax.scatter(xy[CAND, 0], xy[CAND, 1], s=10, facecolors='white', edgecolors=INK2, linewidths=0.7, zorder=3)
    for k in sel:
        ax.scatter([xy[k, 0]], [xy[k, 1]], s=42, color=ORANGE, edgecolors='white', linewidths=1.2, zorder=4)
        if labels:
            ax.annotate(ids[k], (xy[k, 0], xy[k, 1]), xytext=(5, 0), textcoords='offset points', fontsize=6.3, color=INK, va='center',
                        bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.85), zorder=7)
    for k, t in [(iA, 'A'), (iB, 'B')]:
        ax.scatter([xy[k, 0]], [xy[k, 1]], marker='v', s=36, color=INK, edgecolors='white', linewidths=0.9, zorder=8)
        ax.annotate(t, (xy[k, 0], xy[k, 1]), xytext=(-4, 7), textcoords='offset points', fontsize=7.2, color=INK, fontweight='bold',
                    ha='right', bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.85), zorder=8)


# ---------------- Figure 1: prior intrusion probability + designs with 5 wells
NAMES = ['area', 'areaEns', 'hA', 'meanAB', 'pragLin', 'pragEns', 'pragNSA', 'pragNS']
C5 = json.load(open('res_base/check5.json'))      # 48 000-member re-estimate of the key designs
pos = {w: k for k, w in enumerate(ids)}
fig, axs = plt.subplots(1, 4, figsize=(7.0, 4.5), constrained_layout=True, sharey=True)
im = base_map(axs[0], P, 0, 1); wells(axs[0], labels=False)
axs[0].set_title('(a) prior-i dhe puset', loc='left', fontsize=8)
cb = fig.colorbar(im, ax=axs, location='bottom', fraction=0.035, pad=0.02, shrink=0.45)
cb.set_label('probabiliteti prior i intrusionit, P(h < 1 m)', color=INK2); cb.outline.set_edgecolor(MUTED)
panels = [(axs[i + 1], [pos[w] for w in C5[k]['design']], t, C5[k]['eig'][1], C5[k]['pct']['rAB'])
          for i, (k, t) in enumerate([('published', '(b) dizajni i publikuar'), ('pragLin', '(c) PRAG-GO'), ('best_rAB', '(d) greedy + shkëmbime')])]
for ax, sel, ttl, v, pct in panels:
    base_map(ax, P, 0, 1); wells(ax, sel)
    ax.set_title(f'{ttl}\n{v:.3f} nats, {pct:.0%}', loc='left', fontsize=8)
for ax in axs:
    ax.set_xlabel('E [km]')
axs[0].set_ylabel('N [km]')
fig.savefig(f'{FIG}/fig1_map_designs.png', dpi=220)

# ---------------- Figure 2: criterion against exact EIG, 3-well designs
R3 = np.load('res_base/d3.npz'); LIN3, EX3 = R3['LIN'], R3['EX']
fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.6), constrained_layout=True)
for ax, j, gk, xl, yl, lt in [(axs[0], 0, 2, 'EIG lineare e sipërfaqes [nats]', 'EIG e saktë, sipërfaqja > 100 km²', '(a)'),
                          (axs[1], 0, 1, 'EIG lineare e sipërfaqes [nats]', 'EIG e saktë, rreziku A ose B', '(b)'),
                          (axs[2], NAMES.index('pragLin'), 1, 'PRAG-GO [nats]', 'EIG e saktë, rreziku A ose B', '(c)')]:
    rho = spearmanr(LIN3[:, j], EX3[:, gk]).correlation
    ax.scatter(LIN3[:, j], EX3[:, gk], s=3, color=BLUE, alpha=0.35, linewidths=0)
    k = int(np.argmax(LIN3[:, j])); best = EX3[:, gk].max()
    ax.scatter([LIN3[k, j]], [EX3[k, gk]], s=46, color=ORANGE, edgecolors='white', linewidths=1.4, zorder=4)
    ax.axhline(best, color=INK2, lw=0.8, ls='--')
    ax.set_xlabel(xl); ax.set_ylabel(yl, fontsize=7.2)
    ax.set_title(f'{lt} Spearman {rho:.3f}\nkriteri zgjedh {EX3[k, gk] / best:.0%} të optimumit', loc='left', fontsize=8)
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)
fig.savefig(f'{FIG}/fig2_scatter.png', dpi=220)

# ---------------- Figure 3: MAR fields and sites
if os.path.exists('res_base/mar.json'):
    MJ = json.load(open('res_base/mar.json')); F = np.load('res_base/mar_fields.npz')
    fig, axs = plt.subplots(1, 2, figsize=(4.6, 4.6), constrained_layout=True, sharey=True)
    for ax, fld, key, ttl in [(axs[0], F['MAR_c'], 'area', '(a) adjointi i sipërfaqes\n(rregulli i publikuar)'),
                              (axs[1], F['RISK_c'], 'prag', '(b) PRAG-MAR: rreziku\nnë A ose B')]:
        f = np.where(m.coastc, np.nan, fld); f = f / np.nanmax(f)
        im = base_map(ax, f, 0, 1, norm=PowerNorm(0.5, vmin=0, vmax=1))
        wells(ax, cand=False)
        for (x, y), t in zip(MJ[key]['xy'], MJ[key]['ids']):
            ax.scatter([x], [y], marker='D', s=58, color=ORANGE, edgecolors='white', linewidths=1.2, zorder=6)
        r = MJ[key]['rows'][1]
        ax.set_title(f"{ttl}\nP(A ose B) {MJ['base']['pAB']:.2f} → {r['pAB']:.2f}", loc='left', fontsize=8)
        ax.set_xlabel('E [km]')
    axs[0].set_ylabel('N [km]')
    cb = fig.colorbar(im, ax=axs, location='bottom', fraction=0.04, pad=0.03, shrink=0.8)
    cb.set_label('efekti relativ i rimbushjes (max = 1, shkallë rrënjë katrore)', color=INK2); cb.outline.set_edgecolor(MUTED)
    fig.savefig(f'{FIG}/fig3_mar.png', dpi=220)
print('saved', FIG)
