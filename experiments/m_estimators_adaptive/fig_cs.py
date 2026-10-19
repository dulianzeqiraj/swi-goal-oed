"""Figure for proposal N2 from results/cs.json (sim_cs.py)."""
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

from common import OI, INK, MUTED, RULE, MM, RES, panel, save, mc_band

J = json.load(open(os.path.join(RES, 'cs.json')))
A = J['A']; B = J['B']
C = dict(wald=OI['vermillion'], cs_u=OI['green'], cs_w=OI['blue'], cs_i=OI['purple'])
L = dict(wald='Wald në çdo $t$', cs_u='SB, $w_s=1$', cs_w='SB, $w_s=W_s$', cs_i='SB, $w_s=W_s^2$')
CB = dict(u=OI['vermillion'], w=OI['blue'], i=OI['purple'])
LB = dict(u='OLS (pa pesha)', w='AW-LS, $W_s=\\sqrt{\\pi^{\\rm sta}/\\pi_s}$', i='IPW drejt $\\pi^{\\rm sta}$, $W_s^2$')


def main():
    fig = plt.figure(figsize=(178 * MM, 112 * MM))
    gs = GridSpec(2, 3, figure=fig, hspace=0.55, wspace=0.40, left=0.07, right=0.985, top=0.93, bottom=0.1)
    g = np.array(A['grid']); R = A['R']
    # (a) probability of ever missing
    ax = fig.add_subplot(gs[0, 0])
    for k in ('wald', 'cs_u', 'cs_w', 'cs_i'):
        p = np.array(A['ever_miss'][k]); lo, hi = mc_band(p, R)
        ax.fill_between(g, lo, hi, color=C[k], alpha=0.13, lw=0)
        ax.plot(g, p, color=C[k], lw=1.2, label=L[k])
    ax.axhline(0.05, color=MUTED, lw=0.7, ls='--'); ax.text(25, 0.065, '$\\alpha=0.05$', fontsize=6.0, color=MUTED)
    ax.set_xscale('log'); ax.set_ylim(0, 0.7)
    ax.set_xlabel('koha $t$'); ax.set_ylabel('$P(\\exists s\\leq t:\\ \\mu_1\\notin C_s)$')
    ax.set_title('Mbulimi uniform në kohë', color=INK)
    ax.legend(loc='lower right', bbox_to_anchor=(1.0, 0.09), fontsize=5.7, handlelength=1.3)
    panel(ax, 'a', x=-0.2)
    # (b) width
    ax = fig.add_subplot(gs[0, 1])
    for k in ('wald', 'cs_u', 'cs_w', 'cs_i'):
        ax.plot(g, np.array(A['width'][k]), color=C[k], lw=1.2)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('koha $t$'); ax.set_ylabel('gjerësia mediane')
    ax.set_title('Çmimi i vlefshmërisë në çdo kohë', color=INK)
    r = np.array(A['width']['cs_u']) / np.array(A['width']['wald'])
    ax2 = ax.inset_axes([0.52, 0.56, 0.44, 0.38])
    ax2.plot(g, r, color=OI['green'], lw=1.0)
    ax2.set_xscale('log'); ax2.set_ylim(1, 3); ax2.tick_params(labelsize=5.2); ax2.grid(True, lw=0.4)
    ax2.set_title('raporti SB / Wald', fontsize=5.6, color=MUTED, loc='center')
    panel(ax, 'b')
    # (c) why the targets differ under misspecification
    ax = fig.add_subplot(gs[0, 2])
    x = np.linspace(0, 1, 200)
    ax.plot(x, 0.2 + 0.6 * x ** 2, color=OI['orange'], lw=1.6, label='$f_1(x)=0.2+0.6x^2$ (e vërteta)')
    t = np.array(B['target'])
    ax.plot(x, t[0] + t[1] * x, color=OI['purple'], lw=1.2, ls='--', label='$\\theta^*(\\pi^{\\rm sta})$: projeksioni nën $\\pi^{\\rm sta}$')
    rr = B['results']['2000']
    for k in ('u', 'w'):
        ax.plot(x, rr[k]['mean_int'] + rr[k]['mean_slope'] * x, color=CB[k], lw=1.0, ls='-.', label=f"objektivi i {LB[k].split(',')[0].split(' (')[0]}")
    ax.set_ylim(-0.05, 1.0); ax.set_xlabel('konteksti $x$'); ax.set_ylabel('shpërblimi i krahut 1')
    ax.set_title('Specifikim i gabuar: objektivi varet nga $\\pi$', color=INK)
    ax.legend(loc='upper left', fontsize=5.4)
    panel(ax, 'c')
    # (d) sampling distribution of the slope at T = 2000
    ax = fig.add_subplot(gs[1, 0])
    bins = np.linspace(0.45, 0.85, 50)
    for k in ('u', 'w', 'i'):
        v = np.array(rr[k]['slopes'])
        ax.hist(v, bins=bins, density=True, color=CB[k], alpha=0.22, lw=0)
        ax.hist(v, bins=bins, density=True, histtype='step', color=CB[k], lw=1.0, label=LB[k])
    ax.axvline(t[1], color=OI['purple'], lw=0.9, ls='--')
    ax.text(t[1] - 0.006, 26.5, 'objektivi\n$\\theta_1^*(\\pi^{\\rm sta})=0.6$', ha='right', va='top', fontsize=5.8, color=OI['purple'])
    ax.set_ylim(0, 27)
    ax.set_xlabel('pjerrësia e vlerësuar $\\hat\\theta_1$, $T=2000$'); ax.set_ylabel('dendësia')
    ax.set_title('Shpërndarja e vlerësuesve', color=INK)
    ax.legend(loc='upper right', fontsize=5.2, handlelength=1.0)
    panel(ax, 'd', x=-0.2)
    # (e) joint coverage against T
    ax = fig.add_subplot(gs[1, 1])
    Ts = sorted(int(k) for k in B['results'])
    for k in ('u', 'w', 'i'):
        c = np.array([B['results'][str(n)][k]['cov_joint'] for n in Ts]); lo, hi = mc_band(c, B['R'])
        ax.fill_between(Ts, lo, hi, color=CB[k], alpha=0.13, lw=0)
        ax.plot(Ts, c, color=CB[k], marker='o', ms=2.8, lw=1.2, label=LB[k])
    ax.axhline(0.95, color=MUTED, lw=0.7, ls='--')
    ax.set_xscale('log'); ax.set_ylim(-0.02, 1.02)
    ax.set_xticks(Ts); ax.set_xticklabels([str(n) for n in Ts]); ax.minorticks_off()
    ax.set_xlabel('madhësia e mostrës $T$'); ax.set_ylabel('mbulimi i zonës $\\chi^2_2$ për $\\theta^*(\\pi^{\\rm sta})$')
    ax.set_title('Mbulimi nën specifikim të gabuar', color=INK)
    panel(ax, 'e')
    # (f) where the adaptive policy samples arm 1
    ax = fig.add_subplot(gs[1, 2])
    h = np.array(rr['x_hist_arm1']); e = np.linspace(0, 1, 41)
    ax.stairs(h, e, fill=True, color=OI['sky'], alpha=0.35)
    ax.stairs(h, e, color=OI['blue'], lw=1.0, label='TS kontekstual')
    ax.plot([0, 1], [1, 1], color=OI['purple'], lw=1.0, ls='--', label='politika $\\pi^{\\rm sta}=1/2$')
    ax.axvline(np.sqrt(0.5), color=MUTED, lw=0.7, ls=':')
    ax.text(np.sqrt(0.5) + 0.01, 0.15, '$x=\\sqrt{0.5}$', fontsize=5.8, color=MUTED)
    ax.set_xlabel('konteksti $x$'); ax.set_ylabel('dendësia e kontekstit te krahu 1')
    ax.set_title(f"Mostrimi adaptiv: $E[X\\mid A=1]$ = {rr['mean_x_arm1']:.2f}", color=INK)
    ax.legend(loc='upper left', bbox_to_anchor=(0.0, 0.88), fontsize=5.6, title='dendësia e $X\\mid A=1$', title_fontsize=5.6)
    panel(ax, 'f')
    save(fig, 'fig5_n2_confidence_sequences')


if __name__ == '__main__':
    main()
    print('ok')
