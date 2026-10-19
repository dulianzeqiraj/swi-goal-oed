"""Figures 2 and 3 of the review from results/bandit.json (sim_bandit.py)."""
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from scipy.stats import norm

from common import OI, INK, MUTED, RULE, MM, RES, panel, save, mc_band

J = json.load(open(os.path.join(RES, 'bandit.json')))
R = J['R']; Ts = np.array(J['Ts'])
COL = dict(ols=OI['vermillion'], ipw=OI['green'], aw=OI['blue'])
LAB = dict(ols='OLS (unweighted)', ipw='IPW (Horvitz–Thompson)', aw='AW-LS (weights $\\sqrt{\\pi^{\\rm sta}/\\pi_t}$)')


def fig_failure():
    fig = plt.figure(figsize=(178 * MM, 112 * MM))
    gs = GridSpec(2, 3, figure=fig, width_ratios=[1.15, 1, 1], hspace=0.55, wspace=0.42, left=0.07, right=0.985, top=0.93, bottom=0.11)
    # (a) sampling distribution of the studentised statistic, zero margin, T = 1000
    ax = fig.add_subplot(gs[0, 0])
    Z = J['zdist']; e = np.array(Z['bins'])
    x = np.linspace(-4.5, 4.5, 400)
    ax.fill_between(x, norm.pdf(x), color='#eef1f4', lw=0, zorder=0, label='$N(0,1)$')
    for k in ('ols', 'ipw', 'aw'):
        h = np.array(Z[k]['hist'])
        ax.step(e[:-1], h, where='post', color=COL[k], lw=1.0,
                label=f"{LAB[k].split(' (')[0]}: median {Z[k]['median']:+.2f}")
    ax.set_xlim(-4.2, 4.2); ax.set_ylim(0, 0.76)
    ax.set_xlabel('studentized statistic $z$ for $\\mu_1$'); ax.set_ylabel('density')
    ax.set_title('Zero margin, TS, $T=1000$', color=INK)
    ax.legend(loc='upper left', handlelength=1.2, fontsize=5.6, borderaxespad=0.2)
    panel(ax, 'a', x=-0.2)
    # (b) normal QQ plot in the tails
    ax = fig.add_subplot(gs[0, 1])
    zq = norm.ppf(np.array(Z['qs']))
    ax.plot([-3.2, 3.2], [-3.2, 3.2], color=RULE, lw=0.8, ls='--')
    for k in ('ols', 'ipw', 'aw'):
        ax.plot(zq, np.array(Z[k]['q']), color=COL[k], lw=1.1, label=f"{LAB[k].split(' (')[0]}: {100 * Z[k]['cov']:.1f}%")
    ax.legend(loc='lower right', handlelength=1.2, title='coverage', title_fontsize=6.4)
    ax.set_xlim(-3.2, 3.2); ax.set_ylim(-3.6, 3.6)
    ax.set_xlabel('$N(0,1)$ quantiles'); ax.set_ylabel('empirical quantiles')
    ax.set_title('Normal Q–Q plot', color=INK)
    panel(ax, 'b')
    # (c) where the unweighted statistic goes wrong: the realised share of arm 1
    ax = fig.add_subplot(gs[0, 2])
    s0 = np.array(J['share_T5000_zero']); s25 = np.array(J['share_T5000_m025'])
    b = np.linspace(0, 1, 41)
    ax.hist(s0, bins=b, density=True, color=OI['vermillion'], alpha=0.30, lw=0)
    ax.hist(s0, bins=b, density=True, histtype='step', color=OI['vermillion'], lw=1.0, label='$\\Delta=0$')
    ax.hist(s25, bins=b, density=True, color=OI['sky'], alpha=0.30, lw=0)
    ax.hist(s25, bins=b, density=True, histtype='step', color=OI['blue'], lw=1.0, label='$\\Delta=0.25$')
    ax.axvline(0.5, color=MUTED, lw=0.7, ls=':')
    ax.set_ylim(0, 8)
    ax.annotate('$\\Delta=0.25$: concentrated\nnear the 0.95 clip', xy=(0.89, 6.0), xytext=(0.05, 4.3), fontsize=6.0, color=OI['blue'],
                bbox=dict(fc='white', ec='none', pad=0.8), arrowprops=dict(arrowstyle='->', color=OI['blue'], lw=0.7))
    ax.set_xlabel('$\\frac{1}{T}\\sum_t \\pi_t(1)$ at $T=5000$'); ax.set_ylabel('density')
    ax.set_title('Realized information is random', color=INK)
    ax.legend(loc='upper left')
    panel(ax, 'c')
    # (d) coverage against T
    ax = fig.add_subplot(gs[1, 0])
    for nm, ls in (('zero', '-'), ('m025', '--')):
        C = J[f'cov_T_{nm}']
        for k in ('ols', 'ipw', 'aw'):
            c = np.array([C[f'cov_{k}'][str(t)] for t in Ts])
            if nm == 'zero':
                lo, hi = mc_band(c, R)
                ax.fill_between(Ts, lo, hi, color=COL[k], alpha=0.12, lw=0)
            ax.plot(Ts, c, ls, color=COL[k], marker='o' if nm == 'zero' else None, ms=2.6, lw=1.1)
    ax.axhline(0.95, color=MUTED, lw=0.7)
    ax.set_xscale('log'); ax.set_ylim(0.88, 0.975)
    ax.set_xlabel('sample size $T$'); ax.set_ylabel('coverage for $\\mu_1$ (95%)')
    ax.set_title('Coverage vs. $T$', color=INK)
    ax.text(0.98, 0.04, 'solid: $\\Delta=0$\ndashed: $\\Delta=0.25$', transform=ax.transAxes, ha='right', va='bottom',
            fontsize=5.9, color=MUTED)
    panel(ax, 'd', x=-0.2)
    # (e) coverage of the margin against Delta
    ax = fig.add_subplot(gs[1, 1])
    d = np.array(J['deltas']); C = J['cov_delta']
    for k, key, ls in (('ols', 'cov_d_ols', '-'), ('aw', 'cov_d_aw_direct', '-'), ('aw', 'cov_d_aw_proj', ':')):
        c = np.array(C[key]); lo, hi = mc_band(c, R)
        ax.fill_between(d, lo, hi, color=COL[k], alpha=0.10, lw=0)
        ax.plot(d, c, ls, color=COL[k], marker='o', ms=2.4, lw=1.1)
    ax.axhline(0.95, color=MUTED, lw=0.7)
    ax.text(0.5, 0.986, 'AW, $\\chi^2_2$ projection', color=OI['blue'], fontsize=6.2, ha='right', va='bottom')
    ax.text(0.5, 0.937, 'AW, direct contrast', color=OI['blue'], fontsize=6.2, ha='right', va='top')
    ax.text(0.03, 0.902, 'OLS', color=OI['vermillion'], fontsize=6.2)
    ax.set_ylim(0.88, 1.0); ax.set_xlabel('margin $\\Delta=\\mu_1-\\mu_0$'); ax.set_ylabel('coverage for $\\Delta$, $T=1000$')
    ax.set_title('Coverage vs. margin', color=INK)
    panel(ax, 'e')
    # (f) median width
    ax = fig.add_subplot(gs[1, 2])
    C = J['cov_T_zero']
    for k in ('ols', 'ipw', 'aw'):
        w = np.array([C[f'width_{k}'][str(t)] for t in Ts])
        ax.plot(Ts, w, color=COL[k], marker='o', ms=2.6, lw=1.1, label=LAB[k])
    ax.plot(Ts, 2 * 1.96 * np.sqrt(2 / Ts), color=MUTED, lw=0.8, ls='--', label='RCT with $\\pi=1/2$')
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_ylim(0.03, 0.7)
    ax.set_yticks([0.05, 0.1, 0.2, 0.5]); ax.set_yticklabels(['0.05', '0.1', '0.2', '0.5']); ax.yaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlabel('sample size $T$'); ax.set_ylabel('median interval width')
    ax.set_title('Price of stabilization', color=INK)
    ax.legend(loc='lower left', fontsize=5.6)
    panel(ax, 'f')
    save(fig, 'fig2_wald_failure')


def fig_condition():
    fig = plt.figure(figsize=(178 * MM, 62 * MM))
    gs = GridSpec(1, 4, figure=fig, wspace=0.36, left=0.06, right=0.99, top=0.84, bottom=0.2)
    t = np.arange(10, 5001, 10)
    spec = [('ts0', 'TS, $\\Delta=0$', OI['vermillion'], 'paths'), ('ts25', 'TS, $\\Delta=0.25$', OI['orange'], 'paths'),
            ('sts25', 'Smoothed TS, $\\Delta=0.25$', OI['green'], 'paths'),
            ('ts0', 'Weighted, TS, $\\Delta=0$', OI['blue'], 'pathsw')]
    for j, (nm, title, col, kind) in enumerate(spec):
        ax = fig.add_subplot(gs[0, j])
        P = np.array(J[f'{kind}_{nm}'])
        for p in P:
            ax.plot(t, p, color=col, lw=0.45, alpha=0.55)
        if kind == 'pathsw':
            ax.axhline(0.5, color=INK, lw=0.9, ls='--')
            ax.text(4900, 0.015, 'dashed: compensator\n$\\pi^{\\rm sta}(1)=1/2$', ha='right', va='bottom', fontsize=5.4, color=INK,
                    linespacing=1.15)
            ax.text(4900, 0.15, 'realized average\n$\\frac{1}{t}\\sum_s W_s^2 1\\{A_s=1\\}$', ha='right', va='bottom',
                    fontsize=5.4, color=INK, linespacing=1.25)
        if nm == 'sts25':
            ax.axhline(0.9, color=INK, lw=0.9, ls='--')
            ax.text(4900, 0.97, 'deterministic bound $(1-\\gamma)+\\gamma/2$', ha='right', fontsize=5.8, color=INK,
                    bbox=dict(fc='white', ec='none', pad=1.0))
            ax.text(4900, 0.04, 'smoothing parameter $\\gamma=0.2$', ha='right', va='bottom', fontsize=5.8, color=MUTED)
        ax.set_xscale('log'); ax.set_ylim(0, 1.05); ax.set_xlim(10, 5000)
        ax.set_xlabel('time $t$')
        if j == 0:
            ax.set_ylabel('average conditional variance / $\\sigma^2$\n$\\frac{1}{t}\\sum_{s\\leq t}\\pi_s(1)$')
        ax.set_title(title, color=INK, fontsize=6.9)
        panel(ax, 'abcd'[j], x=-0.18)
    save(fig, 'fig3_variance_condition')


if __name__ == '__main__':
    fig_failure()
    fig_condition()
    print('ok')
