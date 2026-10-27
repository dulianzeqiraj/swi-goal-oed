"""Figures A1 and A2 of ASIMILIMI-GO from res/asimilimi.json."""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(HERE, 'res', 'asimilimi.json')))
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#e3e6ea', 'grid.linewidth': 0.6, 'axes.edgecolor': '#9aa3ad'})
INK, MUTED = '#1f2328', '#5b6573'
GC = {'initial head, first km': '#2a78d6', 'slow aquitard legacy (mean)': '#7d4fc9', 'sea-level offset eta0': '#1baf7a',
      'unlicensed pumping E': '#eb6834'}
LAB = {'initial head, first km': 'initial head, first km', 'slow aquitard legacy (mean)': 'slow aquitard legacy',
       'sea-level offset eta0': 'sea-level offset η₀', 'unlicensed pumping E': 'unlicensed pumping E'}

fig, ax = plt.subplots(2, 2, figsize=(11.2, 8.0))
# (a) ensemble smoother -> exact
a = ax[0, 0]
Ns = sorted(int(k) for k in J['E1'])
for g, c in GC.items():
    a.plot(Ns, [J['E1'][str(n)][g]['rms_mean_err'] for n in Ns], '-o', color=c, ms=3.5, lw=1.8, label=LAB[g])
    a.plot(Ns, [J['E1'][str(n)][g]['rms_sd_err'] for n in Ns], '--', color=c, lw=1.2)
ref = np.array(Ns, float)
a.plot(ref, 2.0 * (ref / 100) ** -0.5, ':', color=INK, lw=1)
a.text(1100, 2.0 * (1100 / 100) ** -0.5 * 1.15, 'N^-1/2', fontsize=8, color=INK)
a.set_xscale('log'); a.set_yscale('log')
a.set_xlabel('ensemble size N'); a.set_ylabel('error / exact posterior sd')
a.set_title('(a) Ensemble smoother → exact posterior (solid: mean, dashed: sd)', loc='left', fontsize=9.5)
a.legend(frameon=False, fontsize=7.5, loc='lower left')
# (b) information against the window
b = ax[0, 1]
E2 = J['E2']['heads only']
W = E2['windows']
for g, c in GC.items():
    pr = J['exact'][g]['prior_sd']
    b.plot(W, np.array(E2['post_sd'][g]) / pr, '-o', color=c, ms=3.5, lw=1.8, label=LAB[g])
g = 'initial head, first km'
b.plot(W, np.array(E2['lower_bound_sd'][g]) / J['exact'][g]['prior_sd'], ':', color=GC[g], lw=1.6, label='lower bound of Theorem 3 (initial head)')
b.plot(W, 0.4 * (np.array(W) / 10) ** -0.5 * 0.1, color='white', lw=0)
b.set_xscale('log'); b.set_yscale('log')
b.set_xlabel('length of the observation window (years)'); b.set_ylabel('posterior sd / prior sd')
b.set_title('(b) Initial conditions saturate, boundary parameters keep learning', loc='left', fontsize=9.5)
b.legend(frameon=False, fontsize=7.5, loc='lower left')
# (c) forgetting and a missing source
c = ax[1, 0]
t = np.arange(1, len(J['E3']['max_head_gap']) + 1) / 12
c.plot(t, J['E3']['max_head_gap'], color='#2a78d6', lw=1.8, label='two filters, initial heads 0.5 m apart: largest head gap')
c.plot(t, np.array(J['E3']['gap_E']) / np.array(J['E3']['sd_E']), color='#eb6834', lw=1.8, label='same, gap in E / posterior sd of E')
c.plot(t, J['E3_missing']['free_drift'], color='#8a8f98', lw=1.8, ls='--', label='missing source, no data: head error')
c.plot(t, J['E3_missing']['filter_err'], color='#1baf7a', lw=1.8, label='missing source, filter: head error')
c.set_yscale('log'); c.set_ylim(1e-5, 2)
c.set_xlabel('time (years)'); c.set_ylabel('metres (or ratio)')
c.set_title('(c) The filter forgets a wrong start and bounds a missing source', loc='left', fontsize=9.5)
c.legend(frameon=False, fontsize=7.2, loc='lower left')
# (d) coverage
d = ax[1, 1]
sc = list(J['E5'])
w = 0.2
x = np.arange(len(sc))
for j, (g, col) in enumerate(GC.items()):
    v = [J['E5'][s][g]['coverage'] for s in sc]
    d.bar(x + (j - 1.5) * w, v, w * 0.92, color=col, edgecolor='white', linewidth=1.2, label=LAB[g])
d.axhline(0.9, color=INK, lw=1, ls=':'); d.text(1.3, J['E5'][sc[1]]['unlicensed pumping E']['coverage'] + 0.02, f"{100 * J['E5'][sc[1]]['unlicensed pumping E']['coverage']:.0f}%", fontsize=8, ha='center', color='#b9471a')
d.set_xticks(x); d.set_xticklabels(['correct model', 'missing source,\nno closure', 'missing source,\nclosure added'], fontsize=8)
d.set_ylim(0, 1.28); d.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 0.9, 1.0]); d.set_ylabel('coverage of 90% intervals (400 twins)')
d.set_title('(d) Calibration: the closure restores honest boundary estimates', loc='left', fontsize=9.5)
d.legend(frameon=False, fontsize=7.2, loc='upper center', ncol=2)
fig.tight_layout()
fig.savefig(os.path.join(HERE, 'res', 'figA1_asimilimi.png'), dpi=200)

fig, ax = plt.subplots(1, 2, figsize=(11.2, 3.9))
R = J['E6']['rows']
z = [r['screen_depth'] for r in R]
a = ax[0]
for key, lab, col, ls in (('rmse_exact', 'exact conditioning', INK, '-'), ('rmse_enkf', 'mean-field EnKF', '#eb6834', '-'),
                          ('rmse_anamorphosis', 'probit anamorphosis', '#7d4fc9', '--'), ('rmse_censored_probit', 'censored probit', '#1baf7a', '-')):
    a.plot(z, [r[key] for r in R], ls, marker='o', ms=3.5, color=col, lw=1.8, label=lab)
a.axvline(J['E6']['params']['href'] / J['E6']['params']['delta'], color=MUTED, lw=0.8, ls=':')
a.text(J['E6']['params']['href'] / J['E6']['params']['delta'] + 0.3, 0.05, 'mean interface depth', fontsize=7.5, color=MUTED)
a.set_xlabel('screen depth below sea level (m)'); a.set_ylabel('RMSE of the head update / prior sd')
a.set_ylim(0, 0.9)
a.set_title('(a) One chloride sample: error of the update by screen depth', loc='left', fontsize=9.5)
a.legend(frameon=False, fontsize=7.5, loc='upper center')
b = ax[1]
b.scatter([r['tv_to_gaussian'] for r in R], [r['enkf_minus_exact'] for r in R], color='#eb6834', s=26, label='mean-field EnKF', zorder=3)
b.scatter([r['tv_to_gaussian'] for r in R], [r['censored_minus_exact'] for r in R], color='#1baf7a', s=26, label='censored probit', zorder=3)
b.set_xlabel('distance of the predicted chloride from its Gaussian projection (total variation)')
b.set_ylabel('distance from the exact update / prior sd')
b.set_title('(b) The EnKF error grows with non-Gaussianity [D7]', loc='left', fontsize=9.5)
b.legend(frameon=False, fontsize=7.5, loc='upper left')
fig.tight_layout()
fig.savefig(os.path.join(HERE, 'res', 'figA2_asimilimi.png'), dpi=200)
print('wrote res/figA1_asimilimi.png and res/figA2_asimilimi.png')
