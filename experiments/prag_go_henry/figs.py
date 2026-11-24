"""Figures for the PRAG-GO Henry report (static PNG for Word, light theme).
Palette: sequential blue ramp for salinity and probability, categorical slot 2 (orange) for the
selected wells, neutral inks for text, candidates and isochlors."""
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import spearmanr
from henry import Henry

OUT = sys.argv[1] if len(sys.argv) > 1 else 'res_gauss'
FIG = sys.argv[2] if len(sys.argv) > 2 else 'fig'
import os; os.makedirs(FIG, exist_ok=True)
INK, INK2, MUTED, SURF = '#0b0b0b', '#52514e', '#8a8984', '#fcfcfb'
ORANGE, BLUE, AQUA = '#eb6834', '#2a78d6', '#1baf7a'
SEQ = LinearSegmentedColormap.from_list('blue', ['#f3f7fd', '#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b'])
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK, 'figure.facecolor': 'white',
                     'axes.facecolor': 'white', 'savefig.facecolor': 'white'})

m = Henry(41, 21)
L = np.load(f'{OUT}/lin.npz'); R = np.load(f'{OUT}/designs_s0.01.npz')
CAND, WA, WB = L['CAND'], int(L['WELL_A']), int(L['WELL_B'])
cx, cz = m.xc[CAND % m.Nx], m.yc[CAND // m.Nx]
ax_, az_ = m.xc[WA % m.Nx], m.yc[WA // m.Nx]
bx_, bz_ = m.xc[WB % m.Nx], m.yc[WB // m.Nx]
U0, _, _ = m.solve(np.zeros(m.N)); C0 = m.conc(U0)

# prior exceedance map from a fresh ensemble of 1000 (same prior as the experiment)
X, Z = np.meshgrid(m.xc, m.yc)
Xr, Zr = X.ravel(), Z.ravel()
d2 = ((Xr[:, None] - Xr[None]) / 0.5) ** 2 + ((Zr[:, None] - Zr[None]) / 0.2) ** 2
w, V = np.linalg.eigh(0.25 * np.exp(-np.sqrt(d2))); Lc = V * np.sqrt(np.clip(w, 0, None))
if os.path.exists(f'{FIG}/pmap.npy'):
    P = np.load(f'{FIG}/pmap.npy')
else:
    rng = np.random.default_rng(77); cnt = np.zeros((m.Ny, m.Nx))
    NM = 1000
    for k in range(NM):
        U, _, _ = m.solve(Lc @ rng.standard_normal(m.N), U0=U0)
        cnt += m.conc(U) > 0.01
    P = cnt / NM
    np.save(f'{FIG}/pmap.npy', P)


def domain(ax, field, cmap, levels, label, bar=True):
    cf = ax.contourf(X, Z, field, levels=levels, cmap=cmap)
    ax.set_xlim(0, 2); ax.set_ylim(0, 1); ax.set_aspect('equal')
    ax.set_xlabel('x [m]  (freshwater left, sea right)'); ax.set_ylabel('z [m]')
    if bar:
        cb = plt.colorbar(cf, ax=ax, fraction=0.025, pad=0.02); cb.set_label(label, color=INK2); cb.outline.set_edgecolor(MUTED)
    return cf


def wells(ax, sel=None, sel_color=ORANGE):
    ax.scatter(cx, cz, s=22, facecolors='white', edgecolors=MUTED, linewidths=0.9, zorder=3)
    if sel is not None:
        ax.scatter(cx[list(sel)], cz[list(sel)], s=70, color=sel_color, edgecolors='white', linewidths=1.6, zorder=4)
    for (x, z, t) in [(ax_, az_, 'A'), (bx_, bz_, 'B')]:
        ax.scatter([x], [z], marker='v', s=80, color=INK, edgecolors='white', linewidths=1.4, zorder=5)
        ax.annotate(t, (x, z), xytext=(5, 5), textcoords='offset points', color=INK, fontsize=9, fontweight='bold')


# Figure 1: setup
fig, axs = plt.subplots(2, 1, figsize=(6.6, 6.4), constrained_layout=True)
domain(axs[0], C0, SEQ, np.linspace(0, 1, 21), 'relative salinity c')
cs = axs[0].contour(X, Z, C0, levels=[0.01, 0.5], colors=[INK, INK], linewidths=[1.0, 1.6], linestyles=['--', '-'])
axs[0].clabel(cs, fmt={0.01: '1%', 0.5: '50%'}, fontsize=7.5, colors=INK)
axs[0].add_patch(plt.Rectangle((1.0, 0.0), 0.6, 1.0, fill=False, ls=':', lw=1.2, ec=INK2))
axs[0].text(1.41, 0.955, 'salt-mass\nwindow', ha='center', va='top', color=INK2, fontsize=7.5)
toe = m.toe(U0); axs[0].annotate(f'wedge toe {toe:.2f} m', (toe, 0.0), xytext=(toe - 0.33, 0.20), color=INK, fontsize=7.5,
                                arrowprops=dict(arrowstyle='->', color=INK, lw=0.8))
wells(axs[0])
axs[0].set_title('(a) salinity at the prior mean, the 32 candidates and supply wells A, B', loc='left')
domain(axs[1], P, SEQ, np.linspace(0, 1, 11), 'P(c > 1%)')
wells(axs[1])
axs[1].set_title('(b) prior probability P(c > 1%)', loc='left')
fig.savefig(f'{FIG}/fig1_setup.png', dpi=220)

# Figure 2: the chosen designs
D3, EX, LIN = R['D3'], R['EX'], R['LIN']
best = int(np.argmax(EX[:, 1])); i_prag = int(np.argmax(LIN[:, 4])); i_mass = int(np.argmax(LIN[:, 0])); i_ens = int(np.argmax(LIN[:, 5]))
fig, axs = plt.subplots(3, 1, figsize=(6.0, 8.6), constrained_layout=True)
for ax, i, ttl in [(axs[0], i_prag, 'PRAG-GO with adjoint'), (axs[1], i_mass, 'salt mass (current project goal)'),
                   (axs[2], i_ens, 'PRAG-GO with ensemble moments')]:
    domain(ax, C0, SEQ, np.linspace(0, 1, 21), 'c', bar=False)
    ax.contour(X, Z, C0, levels=[0.01], colors=[INK], linewidths=1.0, linestyles='--')
    wells(ax, D3[i])
    ax.set_title(f'{ttl}\nwells {tuple(int(v) for v in D3[i])}: {EX[i, 1]:.3f} nats, {EX[i, 1] / EX[best, 1]:.1%} of the optimum', loc='left')
fig.savefig(f'{FIG}/fig2_designs.png', dpi=220)

# Figure 3: criterion versus exact EIG over all 4960 designs
fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.0), constrained_layout=True, sharey=True)
for ax, j, ttl in [(axs[0], 0, 'linear EIG of the salt mass [nats]'), (axs[1], 4, 'PRAG-GO with adjoint [nats]')]:
    rho = spearmanr(LIN[:, j], EX[:, 1]).correlation
    ax.scatter(LIN[:, j], EX[:, 1], s=4, color=BLUE, alpha=0.35, linewidths=0)
    k = int(np.argmax(LIN[:, j]))
    ax.scatter([LIN[k, j]], [EX[k, 1]], s=60, color=ORANGE, edgecolors='white', linewidths=1.6, zorder=4)
    ax.axhline(EX[best, 1], color=INK2, lw=0.8, ls='--')
    ax.set_xlabel(ttl); ax.set_title(f'Spearman {rho:.2f}', loc='left')
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)
axs[0].set_ylabel('exact EIG, risk at A or B [nats]')
axs[1].text(0.98, 0.04, 'orange dot: design chosen by the criterion\ndashed line: exact optimum', transform=axs[1].transAxes,
            ha='right', va='bottom', color=INK2, fontsize=7)
fig.savefig(f'{FIG}/fig3_scatter.png', dpi=220)
print('saved', FIG, 'toe', toe)
