"""Figures for the KANAL-GO section (Albanian labels). Reads kanal_results.json."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter, FixedLocator, FixedFormatter
import kanal as K

INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#8a8984', '#e6e5e0'
BLUE, ORANGE, AQUA, VIOLET = '#2a78d6', '#eb6834', '#1baf7a', '#6250d6'
SEQ = ['#9ec5f0', '#5b9be3', '#2a78d6', '#164e94']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.0, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK, 'figure.facecolor': 'white',
                     'axes.facecolor': 'white', 'savefig.facecolor': 'white', 'axes.spines.top': False,
                     'axes.spines.right': False})
R = json.load(open('kanal_results.json'))
pdo = np.array(R['pdo']); C = np.array(R['C']); NS = R['P']['NS']; rules = {k: np.array(v) for k, v in R['rules'].items()}

# ---------------- Figure 9.1: (a) information flow at each alarm level as a function of the pumping probability;
# (b) variance ratio of following the rule versus randomizing 50/50
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.75), constrained_layout=True)
ax = axs[0]; ps = np.linspace(0.0, 1.0, 201)
for r in range(4):
    te = [1000 * float(K.te_batch(pdo[:, r:r + 1, :], K.rule([p]), np.array([1.0]))) for p in ps]
    ax.plot(ps, te, color=SEQ[r], lw=1.8, label=f'alarmi {r}')
    ax.plot(ps, 1000 * 4 * ps * (1 - ps) * C[r], color=SEQ[r], lw=0.9, ls=(0, (2, 2)))
    for g, mk in (('op', 'o'), ('caut', 's')):
        p = rules[g][r]; v = 1000 * float(K.te_batch(pdo[:, r:r + 1, :], K.rule([p]), np.array([1.0])))
        ax.plot(p, v, mk, ms=4.5, color=SEQ[r], mec='white', mew=0.6)
ax.plot([], [], 'o', color=INK2, ms=4, label='rregulli i operatorit'); ax.plot([], [], 's', color=INK2, ms=4, label='rregulli i kujdesshëm')
ax.plot([], [], color=INK2, lw=0.9, ls=(0, (2, 2)), label='4π(1−π)C')
ax.set_xlabel('probabiliteti i pompimit të lartë π'); ax.set_ylabel('rrjedha e informacionit (milibit)')
ax.set_title('(a) rrjedha sipas rregullit; maksimumi = kapaciteti', fontsize=7.4, loc='left')
ax.legend(frameon=False, fontsize=5.6, loc='upper left', ncol=2); ax.set_ylim(0, 1000 * C.max() * 1.45)
ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
ax = axs[1]; pp = np.linspace(0.02, 0.98, 200)
ax.plot(pp, 1 / (4 * pp * (1 - pp)), color=INK, lw=1.6, label='1 / (4π(1−π))')
for g, mk, lab in (('op', 'o', 'i operatorit'), ('caut', 's', 'i kujdesshëm')):
    p = rules[g]; ax.plot(p, 1 / (4 * p * (1 - p)), mk, ms=5, color=ORANGE if g == 'caut' else BLUE, mec='white', mew=0.6, label=f'rregulli {lab}, 4 nivelet')
ax.set_yscale('log'); ax.set_ylim(0.9, 7); ax.yaxis.set_major_locator(FixedLocator([1, 2, 3, 5])); ax.yaxis.set_major_formatter(FixedFormatter(['1', '2', '3', '5'])); ax.yaxis.set_minor_formatter(NullFormatter())
ax.set_xlabel('π(1 | r) e rregullit që vlerësohet'); ax.set_ylabel('varianca: ndiq rregullin / 50–50')
ax.set_title('(b) humbja nga ndjekja e rregullit në eksperiment', fontsize=7.4, loc='left')
ax.legend(frameon=False, fontsize=5.8, loc='upper center'); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
fig.savefig('figN1_kanali.png', dpi=220)

# ---------------- Figure 9.2: SD of the bias-corrected estimate vs number of well-years, two goals
E = R['E']
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.7), constrained_layout=True, sharey=True)
D = [('obs', 'regjistrat + rregullim i pasmë', MUTED, 'o', '-'), ('natural', 'eksperiment: ndiq rregullin', VIOLET, 's', '-'),
     ('balanced', 'eksperiment: 50–50', BLUE, 'D', '-'), ('capped', '50–50 me kufi në alarmin 3', AQUA, '^', '--')]
for ax, (g, title) in zip(axs, (('op', '(a) rregulli i operatorit'), ('caut', '(b) rregulli i kujdesshëm'))):
    for d, lab, col, mk, ls in D:
        sd = [1000 * E[f'{n}|{d}|{g}']['sd'] for n in NS]
        kw = dict(color=col, lw=1.6, ls=ls, marker=mk, ms=4, mec='white', mew=0.6, label=lab)
        if ls == '--':
            kw.update(mfc='white', mec=col, mew=1.2)
        ax.plot(NS, sd, **kw)
        if d in ('natural', 'balanced'):
            ax.plot(NS, [1000 * E[f'{n}|{d}|{g}']['pred_sd'] for n in NS], color=col, lw=0.8, ls=':')
    ax.set_xscale('log', base=2); ax.set_yscale('log'); ax.set_xticks(NS); ax.set_xticklabels([str(n) for n in NS])
    ax.yaxis.set_major_locator(FixedLocator([1.5, 2, 3, 4, 6, 10, 15])); ax.yaxis.set_major_formatter(FixedFormatter(['1.5', '2', '3', '4', '6', '10', '15'])); ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel('numri i pus-viteve'); ax.set_title(title, fontsize=7.6, loc='left'); ax.grid(color=GRID, lw=0.6, which='both'); ax.set_axisbelow(True)
axs[0].set_ylabel('devijimi standard (milibit)')
axs[0].plot([], [], color=INK2, lw=0.8, ls=':', label='parashikimi i teorisë')
axs[0].legend(frameon=False, fontsize=5.7, loc='lower left')
fig.savefig('figN2_dizajni.png', dpi=220)
print('saved')
