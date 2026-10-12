"""Figures for the KRITIK-GO innovation (static PNG, light theme)."""
import json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.argv = ['x']
import kritik as KR

INK, INK2, MUTED = '#0b0b0b', '#52514e', '#8a8984'
BLUE, AQUA, ORANGE = '#2a78d6', '#1baf7a', '#eb6834'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.0, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK, 'figure.facecolor': 'white',
                     'axes.facecolor': 'white', 'savefig.facecolor': 'white'})
R1 = json.load(open('kritik_results.json')); R2 = json.load(open('kritik2_results.json'))


def clean(ax):
    for s in ['top', 'right']:
        ax.spines[s].set_visible(False)


# ---------------- Figure: saddle-node and critical slowing down (nominal parameters)
fr = np.linspace(0.05, 0.9995, 400)
xs, xu, kk = [], [], []
for f in fr:
    lam = f * KR.lamc0; Xm = np.sqrt(1 - lam)
    a = KR.stable_root(KR.mu0, lam)
    from scipy.optimize import brentq
    try:
        b = brentq(lambda X: KR.F(X, lam) - KR.mu0, Xm, 1 - 1e-12)
    except ValueError:
        b = np.nan
    xs.append(a * KR.d); xu.append(b * KR.d); kk.append(KR.Fp(a, lam) / KR.TAU)
fig, axs = plt.subplots(1, 2, figsize=(6.8, 2.6), constrained_layout=True)
ax = axs[0]
ax.plot(fr, xs, color=BLUE, lw=2, label='maja e qëndrueshme')
ax.plot(fr, xu, color=BLUE, lw=1.4, ls='--', label='rrënja e paqëndrueshme')
ax.axhline(KR.d, color=INK2, lw=0.8, ls=':'); ax.text(0.55, KR.d + 25, 'pusi (2 000 m)', color=INK2, fontsize=7, va='bottom')
ax.scatter([1.0], [np.sqrt(1 - KR.lamc0) * KR.d], s=40, color=ORANGE, edgecolors='white', linewidths=1.2, zorder=4)
ax.annotate('saddle-node\n$Q=Q_c$', (1.0, np.sqrt(1 - KR.lamc0) * KR.d), xytext=(0.62, 1650), fontsize=7, color=INK,
            arrowprops=dict(arrowstyle='->', color=INK, lw=0.7))
ax.set_xlabel('$Q/Q_c$'); ax.set_ylabel('largësia e majës nga bregu [m]'); ax.set_ylim(600, 2150)
ax.set_title('(a) dy ekuilibra që bashkohen', loc='left', fontsize=8); ax.legend(frameon=False, fontsize=7, loc='lower right'); clean(ax)
ax = axs[1]
ax.plot(fr, kk, color=BLUE, lw=2)
ax.plot(fr, kk[0] * 0 + np.sqrt(np.maximum(1 - fr, 0)) * np.interp(0.9, fr, kk) / np.sqrt(0.1), color=MUTED, lw=1, ls='--')
ax.text(0.40, 0.11, r'$k\propto\sqrt{1-Q/Q_c}$ afër pikës kritike', color=INK2, fontsize=7)
ax.set_xlabel('$Q/Q_c$'); ax.set_ylabel('shpejtësia e rikthimit k [1/vit]'); ax.set_ylim(0, 0.5)
ax.set_title('(b) ngadalësimi kritik', loc='left', fontsize=8); clean(ax)
fig.savefig('figK1_bifurcation.png', dpi=220)

# ---------------- Figure: criteria and realized accuracy against sensor position
S = np.array(R2['S_POS']); Jio = np.array(R2['J_io']); J0 = np.array(R2['J0'])
rel_io = np.array([r['relerr_near'] for r in R2['stationary']]); rel_p = np.array([r['relerr_pas'] for r in R2['stationary']])
fig, axs = plt.subplots(2, 1, figsize=(6.8, 4.6), constrained_layout=True, sharex=True)
ax = axs[0]
ax.axvspan(R1['xm_p10'], R1['xm_p90'], color=ORANGE, alpha=0.12, lw=0)
ax.text((R1['xm_p10'] + R1['xm_p90']) / 2, 1.04, 'maja kritike\n(prior, 10–90%)', ha='center', va='bottom', fontsize=7, color=INK2)
ax.plot(S, Jio / Jio.max(), color=BLUE, lw=2, marker='o', ms=3.5, label='KRITIK-GO: informacioni për ln k afër pikës kritike')
ax.plot(S, J0, color=MUTED, lw=1.6, ls='--', marker='o', ms=3, label='kriteri i gjendjes: precizioni i majës sot')
ax.set_ylabel('kriteri (max = 1)'); ax.set_ylim(0, 1.25); ax.legend(frameon=False, fontsize=7, loc='upper left')
ax.set_title('(a) ku duhet vendosur sensori i kripësisë', loc='left', fontsize=8); clean(ax)
ax = axs[1]
ax.axvspan(R1['xm_p10'], R1['xm_p90'], color=ORANGE, alpha=0.12, lw=0)
ax.semilogy(S, rel_io, color=BLUE, lw=2, marker='o', ms=3.5, label='kokë + kripësi (hyrje–dalje)')
ax.semilogy(S, rel_p, color=AQUA, lw=1.6, marker='o', ms=3, label='vetëm kripësi (pasiv, AR(1))')
ax.axhline(R2['oracle_io'], color=INK2, lw=0.8, ls=':')
ax.text(400, R2['oracle_io'] * 0.80, f"kufiri «orakull» (maja e vëzhguar pa gabim): {R2['oracle_io']:.2f}", fontsize=7, color=INK2, va='top')
for x, t in [(R2['s_status'], 'gjendja'), (R2['s_star'], 'KRITIK-GO'), (1900, 'pusi')]:
    ax.axvline(x, color=INK, lw=0.7, ls='--'); ax.text(x - 12, 0.135, t, fontsize=7, color=INK, ha='right', va='bottom')
ax.set_xlabel('pozicioni i sensorit të kripësisë, largësia nga bregu [m]')
ax.set_ylabel('gabimi relativ i k (mediana)'); ax.set_ylim(0.12, 900)
ax.legend(frameon=False, fontsize=7, loc='upper center', bbox_to_anchor=(0.52, 1.0))
ax.set_title('(b) saktësia e realizuar në gjendjen afër pikës kritike (0.85 $Q_c$), 300 realizime', loc='left', fontsize=8); clean(ax)
fig.savefig('figK2_design.png', dpi=220)
print('saved')
