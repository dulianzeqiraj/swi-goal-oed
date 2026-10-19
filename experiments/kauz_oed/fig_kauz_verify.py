"""Figure 10 (KAUZ-OED check) from results/kauz_verify.json (kauz_verify.py).
(a) theorem identities on random systems, (b) honest prior table k = 0..8 with 10-90 % bands,
(c) semigroup defects vs integrated (g, p) bias, (d) finite-record detection power,
(e) bias^2 + variance vs |S| for two record lengths, (f) pumping as a parametric perturbation."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', 'm_estimators_adaptive')))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402

from common import OI, INK, MUTED, RULE, GRID, MM, RES, panel, save, mc_band  # noqa: E402

J = json.load(open(os.path.join(RES, 'kauz_verify.json')))
P, G = 8, 27


def pa(ax):
    th = J['theorem']
    bins = np.arange(-17.0, -5.99, 0.25)
    items = [('partial', 'bias formula $B_S(\\tau)$', OI['blue']),
             ('direct', '$(g,p)$ bias', OI['green']),
             ('defect', 'identity for $D$', OI['purple']), ('lyap', 'Lyapunov residual', OI['orange'])]
    for k, lab, c in items:
        v = np.clip(np.array(th[k]['log10']), bins[0] + 1e-9, bins[-1] - 1e-9)
        ax.hist(v, bins=bins, histtype='step', color=c, lw=1.1, label=lab)
        ax.hist(v, bins=bins, color=c, alpha=0.10, lw=0)
    ax.axvline(-10, color=OI['vermillion'], lw=0.9, ls='--')
    ax.text(-9.9, 0.03, 'tolerance $10^{-10}$', transform=ax.get_xaxis_transform(), ha='left', va='bottom',
            fontsize=5.4, color=OI['vermillion'], rotation=90)
    ax.set_xlim(-17, -6); ax.set_ylim(0, 560)
    ax.set_xlabel('$\\log_{10}$ of the relative error')
    ax.set_ylabel('number of systems')
    ax.set_title('Theorem vs. direct computation', color=INK)
    ax.legend(loc='upper left', bbox_to_anchor=(0.03, 1.0), fontsize=5.1, handlelength=1.2, borderaxespad=0.2)
    n = th['nsys']
    ax.text(0.995, 0.98, f'{n} random\nsystems,\n$3\\leq n\\leq 30$,\ncond$(C_0)$\n$\\leq 10^8$', transform=ax.transAxes,
            ha='right', va='top', fontsize=5.2, color=MUTED)
    panel(ax, 'a', x=-0.2)


def pb(ax):
    t = J['numbers']['table']; k = np.array(t['k'])
    cols = dict(kauz=OI['blue'], near=OI['orange'], rand=OI['purple'])
    labs = dict(kauz='KAUZ-OED criterion (prior)', near='nearest neighbors', rand='random sensors')
    nv = t['naive']
    ax.axhspan(nv['q10'], nv['q90'], color=OI['vermillion'], alpha=0.06, lw=0)
    ax.axhline(nv['median'], color=OI['vermillion'], lw=1.0, ls='--', label='naive regression')
    for key in ('rand', 'near', 'kauz'):
        med = np.array([r['median'] for r in t[key]]); lo = np.array([r['q10'] for r in t[key]]); hi = np.array([r['q90'] for r in t[key]])
        se = np.array([r['se_median'] for r in t[key]])
        if key != 'rand':
            ax.fill_between(k, lo, hi, color=cols[key], alpha=0.11, lw=0)
        ax.errorbar(k, med, yerr=1.96 * se, color=cols[key], lw=1.2, marker='o', ms=2.6, capsize=0, elinewidth=0.8,
                    label=labs[key])
    ax.set_yscale('log'); ax.set_ylim(0.008, 250)
    ax.set_xticks(k)
    ax.set_xlabel('extra sensors $k$ ($|S|=k+2$)')
    ax.set_ylabel('relative error of $\\hat R_{gp}$ (median)')
    ax.set_title('Honest table: 200 test models', color=INK)
    ax.legend(loc='upper right', fontsize=5.1, handlelength=1.4, borderaxespad=0.2)
    ax.text(0.02, 0.03, 'bands: 10–90% of the models\nbars: $\\pm1.96$ SE of the median', transform=ax.transAxes, ha='left',
            va='bottom', fontsize=5.1, color=MUTED)
    panel(ax, 'b')


def pc(ax):
    pop = J['semigroup']['pop']
    b = np.abs(np.array(pop['bias'])); dl = np.abs(np.array(pop['Delta'])); dF = np.array(pop['DF'])
    kind = np.array(pop['kind'])
    rng = np.random.default_rng(0); idx = rng.permutation(len(b))[:2600]
    ax.scatter(b[idx], dF[idx], s=2.2, color=MUTED, alpha=0.35, lw=0, label='$\\|D(1,1)\\|_F$', rasterized=True)
    ax.scatter(b[idx], dl[idx], s=2.2, color=OI['blue'], alpha=0.35, lw=0, label='$|\\Delta_{gp}(\\tau_0=2)|$\n(target-specific defect)', rasterized=True)
    lim = np.array([1e-5, 1e2])
    ax.plot(lim, lim, color=INK, lw=0.7, ls=':')
    ax.text(2e-5, 4.2e-5, '$y=x$', fontsize=5.6, color=INK, rotation=33)
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlim(1e-5, 1e2); ax.set_ylim(1e-6, 1e2)
    ax.set_xlabel('$|\\int_0^\\infty B_S\\,d\\tau|_{gp}$ (true bias)')
    ax.set_ylabel('population defect')
    sp = pop['spearman']
    ax.set_title('Semigroup defect vs. bias', color=INK)
    leg = ax.legend(loc='upper left', fontsize=5.3, markerscale=3.0, handletextpad=0.3, borderaxespad=0.2)
    for lh in leg.legend_handles:
        lh.set_alpha(1)
    ax.text(0.98, 0.04, f"Spearman: $\\rho_\\Delta$ = {sp['Delta']:.2f},  $\\rho_D$ = {sp['DF']:.2f}\n"
            f"{len(b)} (model, $S$) pairs", transform=ax.transAxes, ha='right', va='bottom', fontsize=5.4, color=MUTED)
    panel(ax, 'c', x=-0.2)


def pd(ax):
    pw = J['semigroup']['power']; Ts = np.array(pw['Ts']); R = pw['R']; R0 = 0.0564
    lab = dict(pg='$S=\\{p,g\\}$', near1='nearest neighbors\n$k=1$', kauz3='KAUZ-OED $k=3$')
    cols = dict(pg=OI['vermillion'], near1=OI['orange'], kauz3=OI['blue'])
    for key in ('pg', 'near1', 'kauz3'):
        d = pw[key]
        p = np.array(d['DF']); lo, hi = mc_band(p, R)
        ax.fill_between(Ts, lo, hi, color=cols[key], alpha=0.12, lw=0)
        ax.plot(Ts, p, color=cols[key], lw=1.2, marker='o', ms=2.4,
                label=f"{lab[key]}: {100 * abs(d['bias']) / R0:.0f}%")
        ax.plot(Ts, d['Delta'], color=cols[key], lw=0.9, ls='--')
    d = pw['null_pg']
    ax.plot(Ts, d['DF'], color=MUTED, lw=1.0, marker='s', ms=2.0, label='Markov data (null)')
    ax.plot(Ts, d['Delta'], color=MUTED, lw=0.8, ls='--')
    ax.axhline(0.05, color=MUTED, lw=0.6, ls=':')
    ax.set_xscale('log'); ax.set_ylim(-0.02, 1.02)
    ax.set_xticks(Ts); ax.set_xticklabels([str(int(x)) for x in Ts]); ax.minorticks_off()
    ax.set_xlabel('record length $T$ (relaxation time $\\tau_c=5.6$)')
    ax.set_ylabel('power of the bootstrap test (5%)')
    ax.set_title('Detection from finite records', color=INK)
    h1 = ax.legend(loc='upper left', bbox_to_anchor=(0.0, 0.90), fontsize=5.1, handlelength=1.3, borderaxespad=0.2,
                   title='relative bias of $\\hat R_{gp}$', title_fontsize=5.1)
    h1._legend_box.align = 'left'
    ax.add_artist(h1)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], color=INK, lw=1.2), Line2D([], [], color=INK, lw=0.9, ls='--')],
              labels=['$\\|\\hat D(1,1)\\|_F$ test', '$\\hat\\Delta_{gp}(2)$ test'], loc='upper left', fontsize=5.1,
              handlelength=1.6, borderaxespad=0.2, ncol=2, columnspacing=0.8)
    panel(ax, 'd', x=-0.2)


def pe(ax):
    M = J['mse']; Ts = M['Ts']
    k = np.arange(len(M[f'T={Ts[0]:g}']['kauz'])); s = k + 2
    rows0 = M[f'T={Ts[0]:g}']['kauz']
    ax.plot(s, [r['bias2_pop'] for r in rows0], color=INK, lw=1.3, ls='-', label='$E_\\pi[$bias$^2]$')
    cT = [OI['vermillion'], OI['blue']]
    for c, T in zip(cT, Ts):
        d = M[f'T={T:g}']; rows = d['kauz']
        var = np.array([r['var'] for r in rows]); mse = np.array([r['mse'] for r in rows]); se = np.array([r['mse_se'] for r in rows])
        ax.fill_between(s, np.maximum(mse - 1.96 * se, 1e-9), mse + 1.96 * se, color=c, alpha=0.13, lw=0)
        ax.plot(s, mse, color=c, lw=1.3, marker='o', ms=2.4, label=f'MSE, $T$={T:g}')
        ax.plot(s, var, color=c, lw=0.9, ls='--', label=f'variance, $T$={T:g}')
        ax.plot(s, [r['mse'] for r in d['mse']], ls='none', marker='s', ms=3.2, mfc='none', mec=c, mew=0.7)
        ax.axhline(d['naive']['mse'], color=c, lw=0.8, ls=':')
    ax.text(10.1, M[f'T={Ts[0]:g}']['naive']['mse'] * 1.25, 'naive regression', fontsize=5.0, color=OI['vermillion'], ha='right', va='bottom')
    ax.text(10.1, M[f'T={Ts[1]:g}']['naive']['mse'] * 1.25, 'naive regression', fontsize=5.0, color=OI['blue'], ha='right', va='bottom')
    ax.set_yscale('log'); ax.set_ylim(2e-4, 3e4)
    ax.set_xticks(s)
    ax.set_xlabel('number of sensors $|S|$ (KAUZ-OED sequence)')
    ax.set_ylabel('MSE averaged over the prior')
    ax.set_title('Bias$^2$ + variance', color=INK)
    from matplotlib.lines import Line2D
    h, l = ax.get_legend_handles_labels()
    h.append(Line2D([], [], ls='none', marker='s', ms=3.2, mfc='none', mec=MUTED, mew=0.7)); l.append('MSE-greedy')
    ax.legend(h, l, loc='upper right', fontsize=4.9, handlelength=1.4, borderaxespad=0.2, ncol=2, columnspacing=0.7)
    panel(ax, 'e')


def pf(ax):
    pm = J['pumping']; i = np.arange(30)
    true = np.array(pm['true']); f = np.array(pm['f']); add = np.array(pm['additive_p'])
    sc = np.abs(true).max()
    ax.bar(i, f / np.abs(f).max(), width=0.75, color=OI['sky'], alpha=0.35, lw=0, label='effective forcing $f=A_1\\bar c+b$')
    ax.plot(i, true / sc, color=INK, lw=1.3, label='true $\\partial\\bar c/\\partial Q$ = FDT with $f$')
    ax.plot(i, add / np.abs(add).max(), color=OI['vermillion'], lw=1.1, ls='-.', label='FDT with additive forcing at $p$')
    tr = pm['targeted_records']; key = sorted(tr, key=lambda k: float(k.split('=')[1]))[-1]
    d = tr[key]; cells = np.array(d['cells'])
    med, lo, hi = np.array(d['q50']) / sc, np.array(d['q10']) / sc, np.array(d['q90']) / sc
    ax.errorbar(cells, med, yerr=[med - lo, hi - med], fmt='o', ms=2.6, color=OI['blue'], elinewidth=0.9, capsize=1.5,
                label=f"FDT with $\\hat f$, 6 sensors, $T={float(key.split('=')[1]):g}$")
    for x, t in ((P, '$p$'), (G, '$g$')):
        ax.axvline(x, ymax=0.62, color=MUTED, lw=0.6, ls=':')
        ax.text(x + 0.3, -0.36, t, fontsize=6.0, color=MUTED)
    ax.set_ylim(-0.42, 2.05); ax.set_xlim(-0.8, 29.8)
    ax.set_yticks([0, 0.5, 1.0])
    ax.axhline(0, color=RULE, lw=0.6)
    ax.set_xlabel('cell $i$ (inland $\\rightarrow$ coast)')
    ax.set_ylabel('normalized response')
    ax.set_title('Pumping: parametric perturbation of $A$', color=INK)
    ax.legend(loc='upper left', fontsize=5.0, handlelength=1.5, borderaxespad=0.2, ncol=1)
    panel(ax, 'f')


def main():
    fig = plt.figure(figsize=(178 * MM, 118 * MM))
    gs = GridSpec(2, 3, figure=fig, hspace=0.58, wspace=0.42, left=0.075, right=0.985, top=0.93, bottom=0.095)
    pa(fig.add_subplot(gs[0, 0])); pb(fig.add_subplot(gs[0, 1])); pc(fig.add_subplot(gs[0, 2]))
    pd(fig.add_subplot(gs[1, 0])); pe(fig.add_subplot(gs[1, 1])); pf(fig.add_subplot(gs[1, 2]))
    save(fig, 'fig10_kauz_check')


if __name__ == '__main__':
    main()
    print('ok')
