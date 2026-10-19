"""Figure 4 (proposal N1, Theorem 1 of the review) from results/n1.json (sim_n1.py)."""
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

from common import OI, INK, MUTED, RULE, MM, RES, panel, save, mc_band

J = json.load(open(os.path.join(RES, 'n1.json')))
G = np.array(J['gammas']); R = J['R']
COL = dict(ols_cl=OI['vermillion'], ols_sw=OI['orange'], aw=OI['blue'])


def main():
    fig = plt.figure(figsize=(178 * MM, 112 * MM))
    gs = GridSpec(2, 3, figure=fig, hspace=0.58, wspace=0.42, left=0.07, right=0.985, top=0.93, bottom=0.1)
    # (a) the smoothed design on the transect
    ax = fig.add_subplot(gs[0, 0])
    x = np.linspace(0, 1, 401); p = 0.9
    qopt = np.where(x >= 0.5, 2 * p, 2 * (1 - p))
    for g, ls, c in ((0.0, '-', OI['vermillion']), (0.2, '-', OI['blue'])):
        q = (1 - g) * qopt + g
        ax.plot(x, q, ls, color=c, lw=1.3, label=f'$q_t$, $\\gamma={g:g}$')
    ax.plot(x, np.ones_like(x), '--', color=OI['purple'], lw=1.0, label='$q^{\\rm sta}$')
    ax.fill_between(x, 0, 0.2, color=OI['sky'], alpha=0.18, lw=0)
    ax.text(0.25, 0.08, '$\\gamma q^{\\rm sta}$', ha='center', fontsize=6.0, color=OI['blue'])
    ax.axvline(0.5, color=RULE, lw=0.7, ls=':')
    ax.text(0.25, 1.95, 'zona $Z_0$', ha='center', fontsize=6.2, color=MUTED)
    ax.text(0.75, 1.95, 'zona $Z_1$', ha='center', fontsize=6.2, color=MUTED)
    ax.set_ylim(0, 2.1); ax.set_xlabel('pozicioni i matjes $x$ (i normalizuar)'); ax.set_ylabel('dendësia e projektimit')
    ax.set_title('Projektimi i zbutur, $p_t=0.9$', color=INK)
    ax.legend(loc='center left', bbox_to_anchor=(0.0, 0.66), fontsize=5.6)
    panel(ax, 'a', x=-0.2)
    # (b) coverage against gamma, zero margin, T = 1000
    ax = fig.add_subplot(gs[0, 1])
    Z = J['zero']; xg = np.where(G == 0, 0.008, G)
    for k, lab, key in (('ols_cl', 'OLS, SE klasik', lambda d: d['ols']['cov_cl']), ('ols_sw', 'OLS, SE sandwich', lambda d: d['ols']['cov_sw']),
                        ('aw', 'AW-LS, $W_t=\\sqrt{q^{\\rm sta}/q_t}$', lambda d: d['aw']['cov_sw'])):
        c = np.array([key(Z[str(g)]) for g in G]); lo, hi = mc_band(c, R)
        ax.fill_between(xg, lo, hi, color=COL[k], alpha=0.13, lw=0)
        ax.plot(xg, c, color=COL[k], marker='o', ms=2.6, lw=1.1, label=lab)
    ax.axhline(0.95, color=MUTED, lw=0.7, ls='--')
    ax.set_xscale('log'); ax.set_xticks([0.008, 0.02, 0.05, 0.1, 0.2, 0.5, 1]); ax.set_xticklabels(['0', '0.02', '0.05', '0.1', '0.2', '0.5', '1'])
    ax.minorticks_off(); ax.set_ylim(0.9, 0.965)
    ax.set_xlabel('parametri i zbutjes $\\gamma$'); ax.set_ylabel('mbulimi për $\\theta_1$ (95 %)')
    ax.set_title('Mbulimi sipas $\\gamma$, $\\theta_1=0$, $T=1000$', color=INK)
    ax.legend(loc='lower right', fontsize=5.6)
    panel(ax, 'b')
    # (c) coverage against T
    ax = fig.add_subplot(gs[0, 2])
    Ts = np.array(J['Ts'])
    for g, ls in ((0.0, '-'), (0.2, '--')):
        C = J[f'covT_{g}']
        for k in ('ols_cl', 'aw'):
            c = np.array([C[str(t)][k] for t in Ts]); lo, hi = mc_band(c, 3000)
            if g == 0.0:
                ax.fill_between(Ts, lo, hi, color=COL[k], alpha=0.12, lw=0)
            ax.plot(Ts, c, ls, color=COL[k], marker='o' if g == 0 else 's', ms=2.4, lw=1.1)
    ax.axhline(0.95, color=MUTED, lw=0.7, ls='--')
    ax.set_xscale('log'); ax.set_xticks(Ts); ax.set_xticklabels([str(t) for t in Ts]); ax.minorticks_off()
    ax.set_ylim(0.89, 0.965); ax.set_xlabel('numri i matjeve $T$'); ax.set_ylabel('mbulimi për $\\theta_1$')
    ax.set_title('Mbulimi sipas $T$', color=INK)
    ax.text(0.97, 0.05, 'vijë e plotë: $\\gamma=0$\nvijë e ndërprerë: $\\gamma=0.2$\nportokalli-kuqe: OLS; blu: AW-LS', transform=ax.transAxes,
            ha='right', va='bottom', fontsize=5.6, color=MUTED)
    panel(ax, 'c')
    # (d) SE inflation against gamma: empirical, Hellinger prediction, bound 1/sqrt(gamma)
    ax = fig.add_subplot(gs[1, 0])
    gg = np.geomspace(0.01, 1, 200)
    ax.fill_between(gg, 1 / np.sqrt(gg), 10, color='#eef1f4', lw=0)
    ax.plot(gg, 1 / np.sqrt(gg), color=INK, lw=1.0, label='kufiri $1/\\sqrt{\\gamma}$')
    for nm, c, lab in (('zero', OI['blue'], '$\\theta_1=0$'), ('m03', OI['green'], '$\\theta_1=0.3$')):
        D = J[nm]; gpos = G[G > 0]
        e = np.array([D[str(g)]['infl_sd'] for g in gpos]); pr = np.array([D[str(g)]['infl_pred'] for g in gpos])
        ax.plot(gpos, e, color=c, marker='o', ms=2.8, lw=1.1, label=f'empirike, {lab}')
        ax.plot(gpos, pr, color=c, lw=0.9, ls=':', label=f'Hellinger, {lab}')
    ax.set_xscale('log'); ax.set_yscale('log'); ax.set_ylim(0.9, 8); ax.set_xlim(0.015, 1.05)
    ax.set_yticks([1, 1.5, 2, 3, 5]); ax.set_yticklabels(['1', '1.5', '2', '3', '5']); ax.minorticks_off()
    ax.set_xticks([0.02, 0.05, 0.1, 0.2, 0.5, 1]); ax.set_xticklabels(['0.02', '0.05', '0.1', '0.2', '0.5', '1'])
    ax.set_xlabel('parametri i zbutjes $\\gamma$'); ax.set_ylabel('$\\mathrm{sd}(\\hat\\theta_1^{\\rm AW})\\,/\\,\\mathrm{sd}$ nën $q^{\\rm sta}$')
    ax.set_title('Çmimi i stabilizimit', color=INK)
    ax.text(0.82, 0.47, 'zonë e ndaluar\nnga Pohimi 1', fontsize=5.8, color=MUTED, transform=ax.transAxes, ha='center')
    ax.legend(loc='upper right', fontsize=5.0, handlelength=1.6, borderaxespad=0.3)
    panel(ax, 'd', x=-0.2)
    # (e) pathwise Hessian bound
    ax = fig.add_subplot(gs[1, 1])
    gpos = G[G > 0]
    for nm, c, off in (('zero', OI['blue'], -0.06), ('m03', OI['green'], 0.06)):
        D = J[nm]
        q05 = np.array([D[str(g)]['theory']['hess_min_q05'] for g in gpos]); mn = np.array([D[str(g)]['theory']['hess_min_min'] for g in gpos])
        md = np.array([D[str(g)]['theory']['hess_min_med'] for g in gpos])
        xx = gpos * np.exp(off)
        ax.vlines(xx, mn, md, color=c, lw=1.6, alpha=0.6)
        ax.plot(xx, md, 'o', color=c, ms=2.8, label=f'mediana, {"$\\theta_1=0$" if nm == "zero" else "$\\theta_1=0.3$"}')
        ax.plot(xx, mn, '_', color=c, ms=6, mew=1.2)
    ax.plot(gg, np.sqrt(gg), color=INK, lw=1.0, label='$\\sqrt{\\gamma}$')
    ax.set_xscale('log'); ax.set_xlim(0.015, 1.1); ax.set_ylim(0, 1.05)
    ax.set_xticks([0.02, 0.05, 0.1, 0.2, 0.5, 1]); ax.set_xticklabels(['0.02', '0.05', '0.1', '0.2', '0.5', '1']); ax.minorticks_off()
    ax.set_xlabel('parametri i zbutjes $\\gamma$'); ax.set_ylabel('$\\lambda_{\\min}(H_{\\rm sta}^{-1/2}H_TH_{\\rm sta}^{-1/2})$')
    ax.set_title('Kufiri i Hessianit në çdo rrugë', color=INK)
    ax.legend(loc='lower right', fontsize=5.6)
    panel(ax, 'e')
    # (f) trade-off: share of measurements in the zone chosen by the design vs SE inflation (margin case)
    ax = fig.add_subplot(gs[1, 2])
    D = J['m03']; gpos = G
    sh = np.array([D[str(g)]['theory']['share1_mean'] for g in gpos]); inf = np.array([D[str(g)]['infl_sd'] for g in gpos])
    ax.plot(inf, sh, color=OI['green'], lw=1.0, marker='o', ms=3.0)
    for g, a, b in zip(gpos, inf, sh):
        up = g in (0.0, 0.05)
        ax.annotate(f'$\\gamma={g:g}$', (a, b), xytext=(0, 5) if up else (5, -7), textcoords='offset points', fontsize=5.6, color=INK,
                    ha='center' if up else 'left')
    ax.set_xlabel('zgjerimi i gabimit standard të $\\hat\\theta_1^{\\rm AW}$'); ax.set_ylabel('pjesa e matjeve në zonën $Z_1$')
    ax.set_title('Shkëmbimi: qëllimi kundrejt inferencës', color=INK)
    ax.set_xlim(0.95, 1.85); ax.set_ylim(0.45, 1.0)
    ax.text(0.97, 0.05, '$\\theta_1=0.3$: zona $Z_1$ është ajo\nqë projektimi optimal synon', transform=ax.transAxes, ha='right', va='bottom', fontsize=5.6, color=MUTED)
    panel(ax, 'f')
    save(fig, 'fig4_n1_price_of_stabilisation')


if __name__ == '__main__':
    main()
    print('ok')
