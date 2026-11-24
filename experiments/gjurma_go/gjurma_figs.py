"""Figures of GJURMA-GO:
  figG1_field.png  the trace of the missing dynamics in the Fushe-Kuqe chemistry (sheets 5 and 6)
  figG2_twin.png   the test model (base truth) and the errors of the five models in the twin experiment
  figG3_ident.png  identifiability (Fisher spectra) and where the forecast is far from Gaussian (proposal N2)
  figG4_real.png   the illustration on the field data
Colours: models use categorical slots (free blue, GJURMA orange, GJURMA with cut aqua) and neutrals (classical,
oracle); wells and years use one blue ramp ordered by distance from the coast or by time."""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import gjurma_model as G

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#c3c2b7', 'xtick.color': '#52514e', 'ytick.color': '#52514e',
                     'axes.labelcolor': '#0b0b0b'})
INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#898781', '#e1e0d9'
F = json.load(open('gjurma_field.json'))
T = json.load(open('gjurma_twin.json'))
E = json.load(open('gjurma_real.json'))
S = T['setup']
MODELS = S['models']
NPAR = {m: len(S['params']['gjurma' if m == 'gjurma_cut' else m]) for m in MODELS}
COLM = {'classical': '#a3a19a', 'free': '#2a78d6', 'gjurma': '#eb6834', 'gjurma_cut': '#1baf7a', 'oracle': INK2}
LABM = {'classical': 'classical', 'free': 'free closure', 'gjurma': 'GJURMA, joint', 'gjurma_cut': 'GJURMA, cut',
        'oracle': 'oracle'}
COLW = {'503': '#104281', '341': '#2a78d6', '340': '#86b6ef'}
IONS6 = ['Na', 'K', 'Ca', 'Mg', 'SO4', 'HCO3']
ION_LAB = {'Cl': 'Cl', 'Na': 'Na', 'K': 'K', 'Ca': 'Ca', 'Mg': 'Mg', 'SO4': 'SO$_4$', 'HCO3': 'HCO$_3$'}
REAC_LAB = {'Na-Ca exchange': 'Na–Ca\nexchange', 'Na-Mg exchange': 'Na–Mg\nexchange', 'K-Ca exchange': 'K–Ca\nexchange',
            'sulfate reduction': 'sulfate\nreduction', 'calcite dissolution': 'calcite\ndissolution'}


def grid(ax, axis='y'):
    ax.grid(axis=axis, color=GRID, lw=0.6); ax.set_axisbelow(True)


# ================================================================ figure G1: the trace in the field data
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.5), gridspec_kw=dict(width_ratios=[1.0, 1.05, 0.8]))
wells = ['503', '341', '340']
wlab = {w: f'well {w} ({100 * F["wells"][w]["f"]:.1f}% seawater)' for w in wells}
xb = np.arange(len(IONS6)); bw = 0.26
for k, w in enumerate(wells):
    dv = [F['wells'][w]['delta_meq'][i] for i in IONS6]
    ax[0].bar(xb + (k - 1) * bw, dv, bw * 0.92, color=COLW[w], label=wlab[w])
ax[0].axhline(0, color=INK2, lw=0.8)
ax[0].set_xticks(xb); ax[0].set_xticklabels([ION_LAB[i] for i in IONS6])
ax[0].set_ylabel('departure from conservative mixing (meq/L)')
ax[0].set_title('(a) departure of each ion from mixing', fontsize=9)
grid(ax[0])
ax[0].legend(frameon=False, fontsize=6.8, loc='lower right')

reac = F['reactions']; xr = np.arange(len(reac))
for k, w in enumerate(wells):
    med = np.array([F['wells'][w]['extents_meq'][r] for r in reac])
    q = np.array([F['wells'][w]['extents_q'][r] for r in reac])
    ax[1].bar(xr + (k - 1) * bw, med, bw * 0.92, color=COLW[w], label=f'well {w}')
    ax[1].errorbar(xr + (k - 1) * bw, med, yerr=[med - q[:, 0], q[:, 2] - med], fmt='none', ecolor=INK, lw=0.8, capsize=1.5)
ax[1].axhline(0, color=INK2, lw=0.8)
ax[1].set_xticks(xr); ax[1].set_xticklabels([REAC_LAB[r] for r in reac], fontsize=7)
ax[1].set_ylabel('reaction extent (meq/L)')
ax[1].set_title('(b) split on five reactions (90% intervals)', fontsize=9)
grid(ax[1])
ax[1].legend(frameon=False, fontsize=6.8, loc='upper right')

S5cl = {'503': 1048.12, '341': 1038.0, '340': 416.86}
for w in ('503', '341'):
    yrs = [1984, 1999, 2001, 2016]
    vals = [F['cl_trend'][w][str(y)] for y in yrs[:3]] + [S5cl[w]]
    ax[2].plot(yrs, vals, '-o', color=COLW[w], lw=1.6, ms=4, label=f'well {w}')
    ax[2].annotate(f'{w}', (2016, vals[-1]), xytext=(4, 6 if w == '503' else -6), textcoords='offset points', va='center',
                   fontsize=7, color=INK2)
ax[2].plot([2016], [S5cl['340']], 'o', color=COLW['340'], ms=4, label='well 340')
ax[2].annotate('340', (2016, S5cl['340']), xytext=(4, 0), textcoords='offset points', va='center', fontsize=7, color=INK2)
ax[2].set_xlim(1980, 2021); ax[2].set_ylim(0, 1300)
ax[2].set_xlabel('year'); ax[2].set_ylabel('chloride (mg/L)')
ax[2].set_title('(c) chloride: sheet 6 and 2016 (sheet 5)', fontsize=9)
grid(ax[2])
ax[2].legend(frameon=False, fontsize=6.8, loc='lower right')
fig.tight_layout(); fig.savefig('figG1_field.png', dpi=200); plt.close(fig)

# ================================================================ figure G2: the test model and the twin experiment
m0 = np.array([0.0, np.log(150.0), np.log(0.07 / 0.93), np.log(0.1), np.log(0.5), np.log(60.0)] + list(np.log(G.K_TRUE)) + [np.log(0.05)])
P = dict(s_v=np.exp(m0[[0]]), alpha_L=np.exp(m0[[1]]), f0=1 / (1 + np.exp(-m0[[2]])), a_mt=np.exp(m0[[3]]),
         b_im=np.exp(m0[[4]]), E=np.exp(m0[[5]]), logK=m0[None, 6:9], k_sr=np.exp(m0[[9]]))
years = [1975.0, 1990.0, 2000.0, 2016.0, 2045.0]
out = G.simulate(P, 'truth', obs_times=years)
ramp = ['#86b6ef', '#5598e7', '#2a78d6', '#1c5cab', '#104281']

fig = plt.figure(figsize=(10.8, 6.4))
gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 1.05], hspace=0.55, wspace=0.42)
a0 = fig.add_subplot(gs[0, :2]); a1 = fig.add_subplot(gs[0, 2:])
xk = G.XC / 1000
for y, col in zip(years, ramp):
    cl = out[y][0, :, G.I_CL] * G.MW[G.I_CL]
    a0.plot(xk, cl, color=col, lw=1.6, label=f'{int(y)}')
a0.set_yscale('log'); a0.set_ylim(4.5, 3000)
a0.legend(frameon=False, fontsize=7, loc='upper right', title='year', title_fontsize=7)
a0.axvline(G.X_P / 1000, color=MUTED, lw=0.8, ls='--')
a0.text(G.X_P / 1000 + 0.15, 2000, 'abstraction field', fontsize=7, color=INK2)
for w, xw in G.WELLS.items():
    a0.plot([xw / 1000], [5.6], marker='^', color=INK2, ms=4)
    a0.text(xw / 1000 + 0.18, 5.6, w, ha='left', va='center', fontsize=6.5, color=INK2)
a0.set_xlabel('distance from the coast (km)'); a0.set_ylabel('chloride (mg/L)')
a0.set_title('(a) base truth: chloride along the flow line', fontsize=9)
grid(a0)

c16 = out[2016.0][0]
f16 = (c16[:, G.I_CL] - G.FRESH[G.I_CL]) / (G.SEA[G.I_CL] - G.FRESH[G.I_CL])
mix = f16[:, None] * G.SEA + (1 - f16[:, None]) * G.FRESH
dmeq = (c16 - mix) * np.abs(G.Z)
cols4 = {'Na': '#2a78d6', 'Ca': '#eb6834', 'Mg': '#1baf7a', 'SO4': '#eda100'}
for ion, col in cols4.items():
    j = G.SPECIES.index(ion)
    a1.plot(xk, dmeq[:, j], color=col, lw=1.6, label=ION_LAB[ion])
    i = int(np.argmax(np.abs(dmeq[:30, j])))
    a1.annotate(ION_LAB[ion], (xk[i], dmeq[i, j]), xytext=(0, 6 if dmeq[i, j] > 0 else -9), textcoords='offset points',
                ha='center', va='center', fontsize=7, color=INK2)
a1.axhline(0, color=INK2, lw=0.8)
a1.axvline(G.X_P / 1000, color=MUTED, lw=0.8, ls='--')
a1.set_xlim(-1.0, 15); a1.set_xlabel('distance from the coast (km)'); a1.set_ylabel('departure from mixing (meq/L)')
a1.set_title('(b) base truth in 2016: the trace of exchange and sulfate reduction', fontsize=9)
a1.legend(frameon=False, fontsize=7, loc='lower right', ncol=4)
grid(a1)

B = T['B']
truth = np.array([x['truth_goals'] for x in B])
gl = ['(c) Cl at 5 km (mg/L)', '(d) Na at 3 km (mg/L)', '(e) Ca + Mg at 3 km (meq/L)', '(f) strip Cl > 250 mg/L (km)']
rng = np.random.default_rng(3)
for k in range(4):
    ax = fig.add_subplot(gs[1, k])
    labels = []
    for j, m in enumerate(MODELS):
        mean = np.array([x[m]['goal_mean'][k] for x in B])
        q05 = np.array([x[m]['goal_q05'][k] for x in B]); q95 = np.array([x[m]['goal_q95'][k] for x in B])
        e = np.abs(mean - truth[:, k]); cov = ((q05 <= truth[:, k]) & (truth[:, k] <= q95)).mean()
        bs = e[rng.integers(0, e.size, (4000, e.size))].mean(1)
        lo, hi = np.quantile(bs, [0.025, 0.975])
        y = len(MODELS) - 1 - j
        ax.barh(y, e.mean(), color=COLM[m], height=0.68)
        ax.errorbar(e.mean(), y, xerr=[[e.mean() - lo], [hi - e.mean()]], fmt='none', ecolor=INK, lw=0.8, capsize=1.5)
        labels.append((hi, y, f'{100 * cov:.0f}%'))
    ax.set_xlim(0, ax.get_xlim()[1] * 1.22)
    for hi, y, txt in labels:
        ax.text(hi + 0.025 * ax.get_xlim()[1], y, txt, va='center', fontsize=6.5, color=INK2)
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels([f'{LABM[m]} ({NPAR[m]})' for m in MODELS[::-1]] if k == 0 else [], fontsize=7)
    ax.set_xlabel('mean absolute error', fontsize=7.5)
    ax.set_title(gl[k], fontsize=8.5)
    grid(ax, 'x')
fig.text(0.5, 0.005, f'Twin experiment: {len(B)} synthetic truths; bars: mean absolute error of the posterior mean with 95% bootstrap '
         'interval; number at the bar: coverage of the 90% interval; (n): number of fitted parameters.',
         ha='center', fontsize=7, color=INK2)
fig.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.11)
fig.savefig('figG2_twin.png', dpi=200); plt.close(fig)

# ================================================================ figure G3: identifiability and non-Gaussianity
C = T['C']; D = T['D']
fig = plt.figure(figsize=(10.8, 4.2))
gs = fig.add_gridspec(3, 2, width_ratios=[1.0, 1.25], hspace=0.25, wspace=0.25)
a = fig.add_subplot(gs[:, 0])
for m in ('free', 'gjurma', 'oracle'):
    ev = np.maximum(np.array(C[m]['eig']), 1e-6)
    a.semilogy(np.arange(1, ev.size + 1), ev, '-o', color=COLM[m], lw=1.4, ms=2.8,
               label=f'{LABM[m]}: {C[m]["informed"]} of {C[m]["n_params"]} directions informed')
a.axhline(1.0, color=INK2, lw=0.8, ls='--')
a.set_xlim(0, 41)
a.text(40.5, 1.6, 'information = prior precision', fontsize=6.8, color=INK2, ha='right', va='bottom')
a.set_ylim(1e-5, 1e5)
a.set_xlabel('direction (eigenvalues in decreasing order)'); a.set_ylabel('Fisher information in prior-standardised units')
a.set_title('(a) what the 34 data inform (base truth)', fontsize=9)
a.legend(frameon=False, fontsize=6.8, loc='upper right')
grid(a)
x = np.array(D['x_km'])
rows = [('f_mean', 'mean seawater\nfraction', '(b) the 2016 forecast along the flow line (400 members)'),
        ('w2', 'W$_2$ distance,\nstandardised', None),
        ('w2_obs', 'W$_2$ distance /\nobservation error', None)]
for r, (key, lab, title) in enumerate(rows):
    ax = fig.add_subplot(gs[r, 1])
    v = np.array(D[key])
    ax.plot(x, v, color='#2a78d6' if key != 'w2_obs' else '#eb6834', lw=1.6)
    ax.set_ylabel(lab, fontsize=7)
    if key == 'w2_obs':
        ax.axhline(1.0, color=INK2, lw=0.8, ls='--')
        on = v > 1.0
        if on.any():
            ax.fill_between(x, 0, v.max() * 1.05, where=on, color='#eb6834', alpha=0.12, lw=0)
            ax.text(x[on].max() + 0.6, v.max() * 0.62, f'switch zone, {x[on].min():.1f}–{x[on].max():.1f} km:\n'
                    'transport-map analysis', ha='left', va='center', fontsize=6.8, color=INK2)
        ax.set_xlabel('distance from the coast (km)')
    else:
        ax.set_xticklabels([])
    for w, xw in G.WELLS.items():
        ax.axvline(xw / 1000, color=GRID, lw=0.8, zorder=0)
        if r == 0:
            ax.text(xw / 1000, v.max() * 1.02, w, ha='center', fontsize=6.5, color=INK2)
    ax.axvline(G.X_P / 1000, color=MUTED, lw=0.8, ls='--')
    if title:
        ax.set_title(title, fontsize=9)
    grid(ax)
fig.subplots_adjust(left=0.07, right=0.98, top=0.92, bottom=0.12)
fig.savefig('figG3_ident.png', dpi=200); plt.close(fig)

# ================================================================ figure G4: field data
dat = E['data']; d = np.array(dat['d'])
fig, ax = plt.subplots(1, 4, figsize=(10.8, 3.6), gridspec_kw=dict(width_ratios=[1.05, 1.0, 0.75, 0.75]))
cats = G.SPECIES + ['Cl trend']
yy = np.arange(len(cats))[::-1]
for j, m in enumerate(MODELS):
    v = [E[m]['misfit_by_ion'][i] for i in G.SPECIES] + [E[m]['misfit_cl_trend']]
    ax[0].plot(v, yy + (j - 2) * 0.13, 'o', color=COLM[m], ms=3.6, label=f'{LABM[m]}: {E[m]["misfit"]:.1f}')
ax[0].axvline(1.0, color=INK2, lw=0.8, ls='--')
ax[0].set_yticks(yy); ax[0].set_yticklabels([ION_LAB.get(c, c) if c != 'Cl trend' else 'Cl 1984–2001' for c in cats])
ax[0].set_xscale('log'); ax[0].set_xlim(0.5, 40)
ax[0].set_xlabel('RMS misfit / observation error (5%)')
ax[0].set_title('(a) misfit by ion (legend: overall)', fontsize=9)
ax[0].legend(frameon=False, fontsize=6.5, loc='upper center', bbox_to_anchor=(0.45, -0.2), ncol=2)
grid(ax[0], 'x')

obs = np.exp(d[:28])
for m in ('free', 'gjurma_cut', 'classical'):
    fit = np.exp(np.array(E[m]['y_mean'][:28]))
    ax[1].plot(obs, fit, 'o', color=COLM[m], ms=3.2, alpha=0.9, label=LABM[m])
lim = [0.5, 2e4]
ax[1].plot(lim, lim, color=INK2, lw=0.8)
ax[1].set_xscale('log'); ax[1].set_yscale('log'); ax[1].set_xlim(lim); ax[1].set_ylim(lim)
ax[1].set_xlabel('observed in 2016 (mg/L)'); ax[1].set_ylabel('fitted (posterior mean, mg/L)')
ax[1].set_title('(b) 28 analyses of 2016, observed and fitted', fontsize=9)
ax[1].legend(frameon=False, fontsize=6.5, loc='upper left')
grid(ax[1])

for k, (gi, title) in enumerate(((0, '(c) Cl at 5 km in 2045'), (1, '(d) Na at 3 km in 2045'))):
    a = ax[2 + k]
    for j, m in enumerate(MODELS):
        y = len(MODELS) - 1 - j
        a.plot([E[m]['goal_q05'][gi], E[m]['goal_q95'][gi]], [y, y], color=COLM[m], lw=2.2)
        a.plot([E[m]['goal_mean'][gi]], [y], 'o', color=COLM[m], ms=4)
    a.set_yticks(range(len(MODELS)))
    a.set_yticklabels([LABM[m] for m in MODELS[::-1]] if k == 0 else [], fontsize=7)
    a.set_xlabel('mg/L (mean and 90% interval)', fontsize=7.5)
    a.set_title(title, fontsize=9)
    grid(a, 'x')
fig.tight_layout(); fig.subplots_adjust(bottom=0.33); fig.savefig('figG4_real.png', dpi=200); plt.close(fig)
print('figures written')
