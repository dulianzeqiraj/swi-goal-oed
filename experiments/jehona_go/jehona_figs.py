"""JEHONA-GO figures. Run after jehona_exp.py:  python3 jehona_figs.py [outdir]
figJ1_walsh.png   Walsh-Fourier analysis of the potential-outcome paths (first 10 months, all 2^10 paths)
figJ2_design.png  accuracy of the estimators of the sustained-pumping effect and harm of the experiment,
                  against the block length of the switchback design
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
RS = json.load(open('jehona_results.json'))
WZ = np.load('jehona_walsh.npz')
plt.rcParams.update({'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False})
C = {'head': '#2563EB', 'toe': '#B45309', 'sal': '#7C3AED'}

# ---------------------------------------------------------------- figure 1: Walsh analysis
fig, ax = plt.subplots(1, 3, figsize=(10.2, 3.3))
for o, lab in (('head', 'head at the supply well'), ('toe', 'toe position')):
    th = WZ[f'{o}_theta']; d = WZ[f'{o}_delta']
    ok = np.abs(d) > 1e-9
    r = th[ok] / d[ok, None]
    lags = np.arange(r.shape[1])
    med = np.median(r, 0); lo, hi = np.percentile(r, 25, 0), np.percentile(r, 75, 0)
    ax[0].plot(lags, med, '-o', ms=3.5, color=C[o], label=lab)
    ax[0].fill_between(lags, lo, hi, color=C[o], alpha=0.18, lw=0)
ax[0].set_xlabel('lag k (months before month 10)'); ax[0].set_ylabel(r'$\theta_k\,/\,\Delta$ (median and quartiles)')
ax[0].set_title('(a) design-averaged lag effects', fontsize=9); ax[0].legend(frameon=False, fontsize=7.5)
ax[0].set_xticks(range(0, 10, 2))
# (b) Walsh weight by degree
labs, d1, d2, d3 = [], [], [], []
for o, lab in (('head', 'head'), ('toe', 'toe'), ('sal', 'salinization')):
    w = WZ[f'{o}_wdeg']; tot = w[:, 1:].sum(1); ok = tot > 1e-12
    if ok.sum() == 0:
        continue
    labs.append(f'{lab}\n({ok.sum()} units)')
    d1.append(np.mean(w[ok, 1] / tot[ok])); d2.append(np.mean(w[ok, 2] / tot[ok])); d3.append(np.mean(w[ok, 3:].sum(1) / tot[ok]))
x = np.arange(len(labs))
ax[1].bar(x, d1, color='#94A3B8', label='degree 1 (single lags)')
ax[1].bar(x, d2, bottom=d1, color='#F59E0B', label='degree 2')
ax[1].bar(x, d3, bottom=np.array(d1) + np.array(d2), color='#DC2626', label='degree 3 and more')
ax[1].set_xticks(x); ax[1].set_xticklabels(labs, fontsize=7.5); ax[1].set_ylim(0, 1.42)
ax[1].set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax[1].set_ylabel('share of the randomization variance'); ax[1].set_title('(b) Walsh weight by degree', fontsize=9)
ax[1].legend(frameon=False, fontsize=7, loc='upper center', ncol=1, bbox_to_anchor=(0.5, 1.0))
for xi, v in zip(x, d1):
    ax[1].text(xi, v / 2, f'{100 * v:.1f}%', ha='center', va='center', fontsize=7, color='#111827')
# (c) sustained effect against the sum of single-lag effects (toe)
d = WZ['toe_delta']; s = WZ['toe_theta'].sum(1)
ax[2].plot(d, s, 'o', ms=3.5, color=C['toe'], alpha=0.8)
m = [min(d.min(), s.min()), max(d.max(), s.max())]
ax[2].plot(m, m, '--', color='#111827', lw=0.9, label='equality (no interactions)')
ax[2].set_xlabel(r'sustained-pumping effect $\Delta$ (m)'); ax[2].set_ylabel(r'sum of lag effects $\sum_k\theta_k$ (m)')
ax[2].set_title('(c) toe, 48 units: the odd-order remainder', fontsize=9); ax[2].legend(frameon=False, fontsize=7.5)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'figJ1_walsh.png'), dpi=200)
plt.close(fig)

# ---------------------------------------------------------------- figure 2: designs
BS = [1, 2, 3, 6, 12, 36]
D = RS['designs']
fig, ax = plt.subplots(1, 3, figsize=(10.2, 3.4))
EST = [('plain_K36', 'impulse sum', '#64748B', '-o'), ('mbase_K36', 'impulse sum, model baseline', '#0EA5E9', '-s'),
       ('ppi_K36', 'model-assisted (JEHONA-GO)', '#059669', '-D'), ('ht', 'path Horvitz-Thompson', '#DC2626', '-^')]
for j, (o, unit, title) in enumerate((('toe', 'm', '(a) toe position'), ('sal', '', '(b) salinization exposure'))):
    for key, lab, col, mk in EST:
        xs = [B for B in BS if key in D[str(B)][o]]
        ys = [D[str(B)][o][key]['rmse'] for B in xs]
        ax[j].plot(xs, ys, mk, ms=4, lw=1.5, color=col, label=lab)
    ax[j].axhline(abs(D['36'][o]['model']['bias']), color='#111827', ls='--', lw=0.9, label='wrong model alone (bias)')
    ax[j].set_xscale('log'); ax[j].set_xticks(BS); ax[j].set_xticklabels([str(b) for b in BS]); ax[j].minorticks_off()
    ax[j].set_xlabel('block length B (months; 36 = parallel arms)')
    ax[j].set_ylabel(f'RMSE of the sustained-pumping effect{" (" + unit + ")" if unit else ""}')
    ax[j].set_title(title + f', G = {RS["goal"][o]:.3g}', fontsize=9)
    if o == 'toe':
        ax[j].set_ylim(0, 330)
    else:
        ax[j].set_ylim(0, 0.45)
ax[0].legend(frameon=False, fontsize=6.8, loc='upper right')
H = [D[str(B)]['harm'] for B in BS]
ax[2].plot(BS, [100 * h['exposure'] for h in H], '-o', ms=4, color='#7C3AED', label='mean exposure of supply wells')
ax[2].plot(BS, [100 * h['units_saline_at_end'] for h in H], '-s', ms=4, color='#B91C1C', label='supply wells saline at the end')
ax[2].set_xscale('log'); ax[2].set_xticks(BS); ax[2].set_xticklabels([str(b) for b in BS]); ax[2].minorticks_off()
ax[2].set_xlabel('block length B (months)'); ax[2].set_ylabel('% (same mean pumping, 50%)')
ax[2].set_title('(c) harm caused by the experiment', fontsize=9); ax[2].legend(frameon=False, fontsize=7.5)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'figJ2_design.png'), dpi=200)
plt.close(fig)
print('figures written')
