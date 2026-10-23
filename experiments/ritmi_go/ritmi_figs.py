"""Figures of RITMI-GO (review 43):
  figR1_blind.png   what steady and transient data identify (posterior/prior sd per parameter) and the reactive
                    exception (steady SO4 and HCO3 see one combination of the clay memory and the reaction rate)
  figR2_spectra.png resonance of the sensitivity to each memory rate, the bands of the available forcings, and the
                    flow kernel identified from tides
  figR3_design.png  forcing designs (information against salinity cost) and sampling design in time
  figR4_check.png   the nonlinear check with the ensemble smoother on synthetic truths
Colours: data sets and wells use one blue ramp (light = less information or nearer the sea); design families use
categorical slots (oscillations blue, pauses aqua, surges orange); steady data are neutral grey."""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import ritmi_model as R
import ritmi_core as C

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#c3c2b7', 'xtick.color': '#52514e', 'ytick.color': '#52514e',
                     'axes.labelcolor': '#0b0b0b'})
INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#898781', '#e1e0d9'
RAMP = ['#cfe2f7', '#86b6ef', '#2a78d6', '#104281']
GREY = '#a3a19a'
FAM = {'oscillation': '#2a78d6', 'pause': '#1baf7a', 'surge': '#eb6834', 'status quo': INK2}
RES = json.load(open('ritmi_results.json'))
PLAB = [r'$s_v$', r'$\alpha_L$', r'$f_0$', r'$a_1$', r'$b_1$', r'$a_2$', r'$b_2$', r'$E$', r'$K_{K}$', r'$K_{Ca}$',
        r'$K_{Mg}$', r'$k_{sr}$']
GROUPS = [('transport', 0, 2), ('memory', 3, 6), ('exchange', 7, 10), ('reaction', 11, 11)]


def grid(ax, axis='y'):
    ax.grid(axis=axis, color=GRID, lw=0.6); ax.set_axisbelow(True)


def group_marks(ax, y=1.07):
    for name, a, b in GROUPS:
        ax.annotate('', xy=(a - 0.4, y), xytext=(b + 0.4, y), xycoords=('data', 'axes fraction'),
                    arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.8))
        ax.text((a + b) / 2, y + 0.015, name, transform=ax.get_xaxis_transform(), ha='center', va='bottom',
                fontsize=7.2, color=INK2)
        if a > 0:
            ax.axvline(a - 0.5, color=GRID, lw=0.8)


# ================================================================ R1: blindness of steady data
S = RES['S']; HD = RES['HD']
mon = next(d for d in HD['designs'] if d['design']['kind'] == 'const')
fig, ax = plt.subplots(1, 2, figsize=(10.8, 3.5), gridspec_kw=dict(width_ratios=[2.2, 1.0]))
x = np.arange(12); bw = 0.27
sets = [('steady state (7 ions, 4 wells)', S['sd_steady'], GREY),
        ('transient history (34 data)', S['sd_hist'], RAMP[1]),
        ('history + 5 yr of monitoring', mon['sd'], RAMP[3])]
for k, (lab, v, col) in enumerate(sets):
    ax[0].bar(x + (k - 1) * bw, v, bw * 0.92, color=col, label=lab)
ax[0].set_xticks(x); ax[0].set_xticklabels(PLAB)
ax[0].set_ylim(0, 1.05); ax[0].set_ylabel('posterior sd / prior sd')
ax[0].axhline(1.0, color=MUTED, lw=0.7, ls=(0, (3, 2)))
grid(ax[0]); group_marks(ax[0])
ax[0].legend(frameon=False, fontsize=7, loc='lower left', ncol=3, bbox_to_anchor=(0.0, -0.33))
ax[0].set_title('(a) what each data set identifies (1 = nothing learned)', fontsize=9, pad=22)
v1 = np.abs(S['so4_v1']); pr = np.abs(S['so4_pred'])
xs = np.arange(3)
ax[1].bar(xs - 0.18, v1, 0.34, color=RAMP[3], label='steady Jacobian (computed)')
ax[1].bar(xs + 0.18, pr, 0.34, color='white', edgecolor=RAMP[3], hatch='////', lw=0.8,
          label=r'predicted: $\nabla\log\,[b_2a_2k_{sr}/(a_2+k_{sr})]$')
ax[1].set_xticks(xs); ax[1].set_xticklabels([r'$\log a_2$', r'$\log b_2$', r'$\log k_{sr}$'])
ax[1].set_ylim(0, 1.0); grid(ax[1])
sv = S['so4_singular_values']
ax[1].set_title('(b) steady SO$_4$, HCO$_3$: one combination\n(singular values %.2f, %.0e, %.0e)' % (sv[0], sv[1], sv[2]),
                fontsize=9)
ax[1].legend(frameon=False, fontsize=6.8, loc='upper left')
ax[1].set_ylabel('component of the informed direction')
fig.tight_layout()
fig.savefig('figR1_blind.png', dpi=220); plt.close(fig)

# ================================================================ R2: spectra and tides
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.4), gridspec_kw=dict(width_ratios=[1.15, 1.15, 1.0]))
w = np.logspace(-3, 2, 400)
for a, b, lab, col, dx in ((1.0, 0.3, r'silt: $a_1=1$ yr$^{-1}$', RAMP[2], 1.6), (0.05, 0.6, r'clay: $a_2=0.05$ yr$^{-1}$', RAMP[3], 0.62)):
    ax[0].plot(w, (w / a) / (1 + (w / a) ** 2), color=col, lw=1.8)
    ax[0].text(a * dx, 0.515, lab, ha='left' if dx > 1 else 'right', va='bottom', fontsize=7, color=col)
bands = [((2 * np.pi / 100, 2 * np.pi / 10), 'pumping history,\nfront passage', '#eef3fa'),
         ((2 * np.pi / 5, 2 * np.pi / 0.5), 'designed\noscillations', '#fdf0e6')]
for (lo, hi), lab, col in bands:
    ax[0].axvspan(lo, hi, color=col, zorder=0)
    ax[0].text(np.sqrt(lo * hi), 0.66, lab, ha='center', va='bottom', fontsize=6.8, color=INK2)
ax[0].axvline(2 * np.pi, color=MUTED, lw=0.8, ls=(0, (3, 2)))
ax[0].text(2 * np.pi * 1.1, 0.03, 'seasons', fontsize=6.8, color=INK2, rotation=90, va='bottom')
ax[0].set_xscale('log'); ax[0].set_ylim(0, 0.8)
ax[0].set_xlabel(r'angular frequency $\omega$ of the forcing (rad/yr)')
ax[0].set_ylabel(r'$|\partial\hat\kappa(i\omega)/\partial\log a_k|\;/\;b_k$')
ax[0].set_title('(a) transport memory: resonance at $\\omega=a_k$', fontsize=9)
grid(ax[0], 'both')
T = RES['T']; th = T['profiles']['theta']
wd = np.logspace(-3.5, 1.7, 400)
for a, b, lab, col, dx in ((th['a1'], th['b1'], r'fast: $a_1=1$ d$^{-1}$', RAMP[2], 0.62),
                           (th['a2'], th['b2'], r'slow: $a_2=1/60$ d$^{-1}$', RAMP[3], 0.6)):
    ax[1].plot(wd, (wd / a) / (1 + (wd / a) ** 2), color=col, lw=1.8)
    ax[1].text(a * dx, 0.515, lab, ha='right', va='bottom', fontsize=7, color=col)
for name, P in T['profiles']['periods_days'].items():
    om = 2 * np.pi / P
    ax[1].axvline(om, color=FAM['surge'] if name in ('M2', 'K1') else FAM['pause'], lw=1.0)
    ax[1].text(om * 1.08, 0.78, name, fontsize=7, color=INK2, rotation=90, va='top')
ax[1].set_xscale('log'); ax[1].set_ylim(0, 0.8)
ax[1].set_xlabel(r'angular frequency $\omega$ (rad/day)')
ax[1].set_title('(b) flow memory and the tidal constituents', fontsize=9)
grid(ax[1], 'both')
keys = ['M2', 'M2+K1', 'M2+K1+MSf', 'M2+K1+MSf+Sa']
tl = [r'$D$', r'$a_1$', r'$b_1$', r'$a_2$', r'$b_2$']
xt = np.arange(5); bw = 0.2
for k, key in enumerate(keys):
    ax[2].bar(xt + (k - 1.5) * bw, T[key]['sd'], bw * 0.92, color=RAMP[k], label=key.replace('+', ' + '))
ax[2].set_xticks(xt); ax[2].set_xticklabels(tl); ax[2].set_ylim(0, 1.34)
ax[2].axhline(1.0, color=MUTED, lw=0.7, ls=(0, (3, 2)))
ax[2].set_ylabel('posterior sd / prior sd')
ax[2].set_title('(c) tides identify the flow kernel', fontsize=9)
ax[2].legend(frameon=False, fontsize=6.6, loc='upper left', ncol=2)
ax[2].set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
grid(ax[2])
fig.tight_layout()
fig.savefig('figR2_spectra.png', dpi=220); plt.close(fig)

# ================================================================ R3: forcing designs and sampling in time
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.5), gridspec_kw=dict(width_ratios=[1.1, 1.25, 0.9]))
base = mon['logdet']
for d in HD['designs']:
    k = d['design']['kind']
    fam = 'status quo' if k == 'const' else ('pause' if k == 'block' and d['design']['A'] < 0 else
                                             'surge' if k == 'block' else 'oscillation')
    xc = d['cost'] - d['relief']
    ax[0].scatter(xc, d['logdet'] - base, s=26, color=FAM[fam], zorder=3, edgecolor='white', lw=0.6)
    lab = {'status quo': (-0.6, -0.055, 'right'), 'sine 0.5 yr': (0.9, -0.085, 'left'), 'sine 1 yr': (0.6, 0.105, 'right'),
           'sine 2 yr': (3.4, 0.135, 'right'), 'PRBS 0.25 yr': (5.2, -0.06, 'left'), 'surge 1 yr': (8.2, -0.03, 'left'),
           'doublet 2 yr': (9.6, 0.035, 'left'), 'sine 5 yr': (9.3, 0.18, 'left'), 'doublet 5 yr': (13.6, 0.27, 'right'),
           'surge 2 yr': (12.6, 0.12, 'center'), 'pause 1 yr': (-5.6, 0.035, 'left'), 'pause 2 yr': (-11.5, 0.085, 'left')}
    lx, ly, ha = lab[d['label']]
    ax[0].annotate(d['label'], (xc, d['logdet'] - base), xytext=(lx, ly), textcoords='data', fontsize=6.4, color=INK2,
                   ha=ha, va='center', arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.5, shrinkA=1, shrinkB=2))
for fam, col in FAM.items():
    ax[0].scatter([], [], color=col, s=22, label=fam)
ax[0].axvline(0, color=MUTED, lw=0.7); ax[0].axhline(0, color=MUTED, lw=0.7)
ax[0].set_xlabel('extra Cl at the well field, 2026–2045 (mg/L)\n(negative = relief)')
ax[0].set_ylabel('information added (nats)')
ax[0].set_title('(a) pumping designs, 2026–2031', fontsize=9)
ax[0].legend(frameon=False, fontsize=6.6, loc='upper left')
ax[0].set_ylim(-0.11, max(d['logdet'] - base for d in HD['designs']) + 0.1)
grid(ax[0], 'both')
G = RES['G']
P0 = C.to_P(C.M0[None, :])
out = R.simulate(P0, {'kind': 'const'})
tt = out['times']; sel = (tt >= 2016) & (tt <= 2034)
for k, wn in enumerate(['503', '341', '340']):
    col = [RAMP[3], RAMP[2], RAMP[1]][k]
    y = out['wells'][:, 0, k, R.I_CL] * R.MW[R.I_CL]
    ax[1].plot(tt[sel], y[sel], color=col, lw=1.6, label=f'well {wn}')
    for typ, wl, t in G['greedy']:
        if wl == wn:
            yi = y[R.tindex(tt, t)]
            ax[1].scatter(t, yi, s=30 if typ == 'ions' else 16, marker='s' if typ == 'ions' else 'o',
                          facecolor='white', edgecolor=INK, lw=0.9, zorder=4)
ax[1].axvspan(R.EXP0, R.EXP1, color='#f3f5f8', zorder=0)
ax[1].scatter([], [], marker='s', facecolor='white', edgecolor=INK, s=30, label='chosen ion campaign')
ax[1].scatter([], [], marker='o', facecolor='white', edgecolor=INK, s=16, label='chosen Cl sample')
ax[1].set_yscale('log'); ax[1].set_ylabel('Cl (mg/L), status quo, base truth')
ax[1].set_xticks([2016, 2020, 2024, 2028, 2032]); ax[1].set_xlim(2016, 2034)
ax[1].set_title('(b) the 12 most useful samples for the 2045 goals', fontsize=9)
ax[1].legend(frameon=False, fontsize=6.6, loc='lower right', ncol=2)
grid(ax[1], 'both')
cats = ['history', 'routine 12', 'greedy 12', 'all 210']
vals = [G['goal_sd_hist'], G['goal_sd_routine'], G['goal_sd_greedy'], G['goal_sd_all']]
xg = np.arange(2); bw = 0.2
for k, (c, v) in enumerate(zip(cats, vals)):
    ax[2].bar(xg + (k - 1.5) * bw, [v[0], v[1]], bw * 0.92, color=RAMP[k], label=c)
ax[2].set_xticks(xg); ax[2].set_xticklabels(['Cl at 5 km\n(mg/L)', 'Na at 3 km\n(mg/L)'])
ax[2].set_ylabel('posterior sd of the 2045 goal (linearised)')
ax[2].set_title('(c) value of the samples', fontsize=9)
ax[2].legend(frameon=False, fontsize=6.6, loc='upper right')
grid(ax[2])
fig.tight_layout()
fig.savefig('figR3_design.png', dpi=220); plt.close(fig)

# ================================================================ R4: nonlinear check
if 'V' in RES:
    V = RES['V']['summary']
    names = list(V)
    short = {'history': 'history', 'history + all monitoring': '+ all 210', 'history + greedy 12': '+ greedy 12',
             'history + routine 12': '+ routine 12'}
    order = ['history', 'history + routine 12', 'history + greedy 12', 'history + all monitoring']
    fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.4), gridspec_kw=dict(width_ratios=[1.0, 1.0, 1.35]))
    gl = ['Cl 5 km', 'Na 3 km', 'Ca+Mg 3 km', 'strip > 250']
    xg = np.arange(4); bw = 0.2
    for k, n in enumerate(order):
        rel = np.array(V[n]['rmse']) / np.array(V['history']['rmse'])
        ax[0].bar(xg + (k - 1.5) * bw, rel, bw * 0.92, color=RAMP[k], label=short[n])
        ax[1].bar(xg + (k - 1.5) * bw, V[n]['cover90'], bw * 0.92, color=RAMP[k])
    ax[0].set_xticks(xg); ax[0].set_xticklabels(gl, fontsize=7.5)
    ax[0].set_ylabel('RMSE / RMSE with history only'); ax[0].set_title('(a) error of the 2045 goals', fontsize=9)
    ax[0].legend(frameon=False, fontsize=6.6, loc='upper right'); grid(ax[0])
    ax[1].axhline(0.9, color=INK2, lw=0.8, ls=(0, (3, 2)))
    ax[1].set_xticks(xg); ax[1].set_xticklabels(gl, fontsize=7.5); ax[1].set_ylim(0, 1.05)
    ax[1].set_ylabel('coverage of the 90% interval'); ax[1].set_title('(b) calibration', fontsize=9); grid(ax[1])
    x = np.arange(12)
    for k, n in enumerate(['history', 'history + all monitoring']):
        ax[2].plot(x, V[n]['contraction'], marker='o', ms=4, lw=1.4, color=[RAMP[1], RAMP[3]][k], label=short[n])
    ax[2].set_xticks(x); ax[2].set_xticklabels(PLAB); ax[2].set_ylim(0, 1.1)
    ax[2].axhline(1.0, color=MUTED, lw=0.7, ls=(0, (3, 2)))
    ax[2].set_ylabel('ensemble sd / prior sd (mean over truths)')
    ax[2].set_title('(c) what the ensemble smoother learns', fontsize=9, pad=22)
    group_marks(ax[2]); grid(ax[2])
    ax[2].legend(frameon=False, fontsize=6.6, loc='lower left')
    fig.tight_layout()
    fig.savefig('figR4_check.png', dpi=220); plt.close(fig)
print('figures written')
