"""Figures of KURSIM-GO: figK1_estimators.png (the model and the Monte Carlo test) and figK2_design.png (policy design)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
import kursim_model as K

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False})
MC = json.load(open('kursim_mc.json'))
DS = json.load(open('kursim_design.json'))
INK, INK2 = '#0b0b0b', '#52514e'
COL = {'frugal': '#2a78d6', 'ipw': '#eb6834', 'dr': '#1baf7a', 'gform': '#eda100', 'ols_all': '#52514e', 'ols_base': '#a3a19a'}
NAME = {'frugal': 'frugal MLE', 'ipw': 'IPW', 'dr': 'doubly robust', 'gform': 'g-formula (linear Y)',
        'ols_all': 'OLS with the alarm', 'ols_base': 'OLS without the alarm'}

# ---------------------------------------------------------------- figure 1: model and Monte Carlo test
fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.4), gridspec_kw=dict(width_ratios=[1.0, 1.15, 1.1]))

# (a) observational cell means against the causal margin
rng = np.random.default_rng(11)
D = K.simulate(1_000_000, rng)
cells = [(0, 0), (1, 0), (0, 1), (1, 1)]
obs = [D['Y'][(D['A1'] == a1) & (D['A2'] == a2)].mean() for a1, a2 in cells]
c = K.CAUSAL
cau = [c['theta0'] + c['theta1'] * a1 + c['theta2'] * a2 for a1, a2 in cells]
x = np.arange(4)
ax[0].bar(x - 0.2, cau, 0.38, color=COL['frugal'], label='causal mean E[Y | do(a)]')
ax[0].bar(x + 0.2, obs, 0.38, color='#a3a19a', label='observational mean E[Y | A = a]')
for xi, o, ca in zip(x, obs, cau):
    ax[0].text(xi + 0.2, o + 0.02, f'{o - ca:+.2f}', ha='center', fontsize=6.8, color=INK2)
ax[0].set_xticks(x); ax[0].set_xticklabels([f'({a1}, {a2})' for a1, a2 in cells])
ax[0].set_xlabel('pumping regime (a₁, a₂)'); ax[0].set_ylabel('log chloride Y')
ax[0].set_ylim(5.0, 6.35)
ax[0].legend(frameon=False, fontsize=6.8, loc='upper left')
ax[0].set_title('(a) the margin is exact, the data are confounded', fontsize=9)

# (b) RMSE of both effects, effect scenario n = 1500
R = MC['results']['effect_n1500']
order = ['ols_all', 'ols_base', 'gform', 'ipw', 'dr', 'frugal']
y = np.arange(len(order))
r1 = [R[m]['rmse'][0] for m in order]; r2 = [R[m]['rmse'][1] for m in order]
ax[1].barh(y + 0.2, r1, 0.38, color='#a3a19a', label='θ₁ (season-1 pumping)')
ax[1].barh(y - 0.2, r2, 0.38, color=COL['frugal'], label='θ₂ (season-2 pumping)')
for yi, a, b in zip(y, r1, r2):
    ax[1].text(a + 0.003, yi + 0.2, f'{a:.3f}', va='center', fontsize=6.5, color=INK2)
    ax[1].text(b + 0.003, yi - 0.2, f'{b:.3f}', va='center', fontsize=6.5, color=INK2)
ax[1].set_yticks(y); ax[1].set_yticklabels([NAME[m] for m in order], fontsize=7.4)
ax[1].set_xlabel('root mean squared error (1000 data sets, n = 1500)')
ax[1].set_xlim(0, 0.2)
ax[1].legend(frameon=False, fontsize=6.8, loc='upper right')
ax[1].set_title('(b) error of the estimated effects', fontsize=9)

# (c) false-alarm rate of the 5% test of no effect
scen = [('null_n300', 'null\nn = 300'), ('null_n1500', 'null\nn = 1500'),
        ('null_strong_n1500', 'strong\nn = 1500'), ('null_strong_n6000', 'strong\nn = 6000')]
xs = np.arange(len(scen))
for m in ['ols_base', 'gform', 'ipw', 'dr', 'frugal']:
    rej = [max(MC['results'][k][m]['reject']) for k, _ in scen]
    ax[2].plot(xs, rej, color=COL[m], marker='o', ms=4.5, lw=2.0 if m == 'frugal' else 1.4, label=NAME[m])
ax[2].axhline(0.05, color=INK, lw=0.8, ls='--')
ax[2].text(3.18, 0.05, '5%', fontsize=6.8, color=INK, va='center')
ax[2].set_xlim(-0.25, 3.45)
ax[2].set_xticks(xs); ax[2].set_xticklabels([s for _, s in scen], fontsize=7)
ax[2].set_xlabel('scenario with θ = 0 (strong = strong alarm feedback)', fontsize=7.5)
ax[2].set_ylabel('rejection rate of a true θ = 0\n(larger of the two coefficients)')
ax[2].set_ylim(0, 1.03)
ax[2].legend(frameon=False, fontsize=6.6, loc='center left', bbox_to_anchor=(0.0, 0.52))
ax[2].set_title('(c) false discoveries under no effect', fontsize=9)
fig.tight_layout(); fig.savefig('figK1_estimators.png', dpi=200); plt.close(fig)

# ---------------------------------------------------------------- figure 2: safe policies that still teach
G = DS['grid']; base = DS['baseline']
B0 = np.array(sorted({g['b0'] for g in G})); B3 = np.array(sorted({g['b3'] for g in G}))
idx = {(g['b0'], g['b3']): g for g in G}
def field(key):
    return np.array([[idx[(b0, b3)][key] for b0 in B0] for b3 in B3])
risk, prod, fr2, ip2, dr2 = field('risk'), field('prod'), field('frugal2'), field('ipw2'), field('dr2')

fig, ax = plt.subplots(1, 3, figsize=(10.8, 3.5), gridspec_kw=dict(width_ratios=[1.0, 1.0, 1.15]))
ext = [B0[0] - 0.25, B0[-1] + 0.25, B3[0] - 0.25, B3[-1] + 0.25]
def label_at(cs, b0_target, fmt):
    pos = []
    for lev, segs in zip(cs.levels, cs.allsegs):
        pts = np.vstack([sg for sg in segs if len(sg)]) if any(len(sg) for sg in segs) else None
        if pts is None:
            continue
        j = np.argmin(np.abs(pts[:, 0] - b0_target(lev)))
        pos.append(tuple(pts[j]))
    ax_.clabel(cs, fmt=fmt, fontsize=6, manual=pos, inline_spacing=2)

TICKS = ([0.8, 1, 1.5, 2, 3, 4], [2, 5, 10, 20, 50, 100, 200, 500, 1000])
for k, (F, ttl, cm) in enumerate(((fr2, r'(a) frugal MLE: $n\,\mathrm{Var}(\hat\theta_2)$', 'Blues'),
                                   (ip2 / fr2, '(b) IPW variance ÷ frugal variance', 'Oranges'))):
    ax_ = ax[k]
    im = ax_.imshow(F, origin='lower', extent=ext, aspect='auto', cmap=cm,
                    norm=LogNorm(vmin=max(F.min(), 0.5), vmax=F.max()))
    cb = fig.colorbar(im, ax=ax_, fraction=0.05, pad=0.02); cb.ax.tick_params(labelsize=7)
    tk = [t for t in TICKS[k] if F.min() <= t <= F.max()]
    cb.ax.yaxis.set_major_locator(FixedLocator(tk)); cb.ax.yaxis.set_major_formatter(FixedFormatter([f'{t:g}' for t in tk]))
    cb.ax.yaxis.set_minor_locator(NullLocator())
    cs = ax_.contour(B0, B3, risk, levels=[0.01, 0.02, 0.05, 0.1], colors=INK, linewidths=0.7)
    label_at(cs, lambda lev: 1.9, lambda v: f'risk {v:.2f}')
    cp = ax_.contour(B0, B3, prod, levels=[0.40], colors=INK, linewidths=1.0, linestyles='--')
    pts = np.vstack([sg for sg in cp.allsegs[0] if len(sg)]); j = np.argmin(np.abs(pts[:, 1] + 1.3))
    ax_.clabel(cp, fmt=lambda v: f'production {v:.2f}', fontsize=6, manual=[tuple(pts[j])], inline_spacing=2)
    ax_.plot(base['b0'], base['b3'], marker='*', ms=10, color='#e34948', mec='white', mew=0.6)
    ax_.set_xlabel('baseline pumping propensity b₀'); ax_.set_ylabel('cut after an alarm b₃')
    ax_.set_title(ttl, fontsize=9)
ax[0].annotate('current policy', xy=(base['b0'], base['b3']), xytext=(-2.4, -0.9), fontsize=7, color='#e34948',
               bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.85),
               arrowprops=dict(arrowstyle='->', color='#e34948', lw=0.8))

caps = np.linspace(0.004, 0.14, 120)
for m, key in (('frugal', 'frugal2'), ('dr', 'dr2'), ('ipw', 'ipw2')):
    best = []
    for r in caps:
        ok = [g[key] for g in G if g['risk'] <= r and g['prod'] >= 0.40]
        best.append(min(ok) if ok else np.nan)
    ax[2].plot(caps, best, color=COL[m], lw=2.0 if m == 'frugal' else 1.5, label=NAME[m])
    ax[2].plot(base['risk'], base[key], marker='*', ms=9, color=COL[m], mec='white', mew=0.6)
ax[2].set_yscale('log')
ax[2].set_xlabel('cap on P(alarm and high pumping)')
ax[2].set_ylabel(r'best $n\,\mathrm{Var}(\hat\theta_2)$ with production ≥ 0.40')
ax[2].axvline(0.02, color=INK2, lw=0.7, ls=':')
ax[2].text(0.022, 30, '2% cap', fontsize=6.8, color=INK2)
ax[2].legend(frameon=False, fontsize=7, loc='upper right')
ax[2].set_title('(c) risk–precision frontier (stars: current policy)', fontsize=9)
fig.tight_layout(); fig.savefig('figK2_design.png', dpi=200); plt.close(fig)
print('figures written')
