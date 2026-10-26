"""Figure V1 of review 57 (VENDIMI-GO) from res/vendimi.json:
(a) each stakeholder's prior probability that a supply screen exceeds 250 mg/L against the pumping scale;
(b) disagreement between stakeholders before and after information, with the bound of Proposition V1;
(c) the decisive joint choice (unanimous certified rule) against the average-belief rule;
(d) realised failure frequency under each stakeholder's own belief."""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
INK, INK2, GRID = '#0b0b0b', '#52514e', '#d9d8d4'
COLS = ['#2a78d6', '#1baf7a', '#eda100', '#7c5cc4', '#eb6834']
SHORT = ['utility', 'irrigators, hotels', 'municipality', 'water agency', 'environmental']


def style(ax):
    ax.tick_params(colors=INK2, labelsize=7.5)
    for s_ in ax.spines.values():
        s_.set_color(GRID)


def main():
    S = json.load(open(os.path.join(HERE, 'res', 'vendimi.json')))
    al = S['alpha']; sg = np.array(S['prior']['s_grid'])
    fig = plt.figure(figsize=(12.4, 8.6)); gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.27)
    a = fig.add_subplot(gs[0, 0])
    for k in range(5):
        a.plot(sg, S['prior']['curves_q0'][k], color=COLS[k], lw=1.7, label=SHORT[k])
        a.plot(sg, S['prior']['curves_q5000'][k], color=COLS[k], lw=1.2, ls='--')
    a.axhline(al, color=INK, lw=0.9, ls=':'); a.text(2.35, al + 0.015, 'risk limit 10%', fontsize=7, color=INK)
    a.set_xlim(0, 3); a.set_ylim(0, 1)
    a.set_xlabel('pumping scale s (1 = 12,060 m$^3$/d at A1 + P10)', color=INK2, fontsize=8.5)
    a.set_ylabel('prior P(a 20-m supply screen > 250 mg/L)', color=INK2, fontsize=8.5)
    h = [Line2D([], [], color=COLS[k], lw=1.7, label=SHORT[k]) for k in range(5)] + [Line2D([], [], color=INK2, lw=1.2, ls='--', label='with 3 × 5,000 m$^3$/d recharge')]
    a.legend(handles=h, fontsize=6.8, frameon=False, loc='upper left')
    a.set_title('(a) Five beliefs, one aquifer', fontsize=9.5, loc='left', color=INK); a.grid(color=GRID, lw=0.5); style(a)
    b = fig.add_subplot(gs[0, 1])
    dn = list(S['designs'].keys()); lab = ['no data', '3 heads', '1 chloride\nsample', 'chloride\n+ heads']
    sp = [S['designs'][d]['spread_mean'] for d in dn]; bd = [S['designs'][d]['bound2_mean'] for d in dn]
    b.bar(range(4), sp, color=['#8a8a8a', '#2a78d6', '#1baf7a', '#7c5cc4'], width=0.6, label='largest disagreement (mean)')
    b.scatter(range(4), bd, marker='_', s=500, color=INK, lw=2, zorder=5, label='bound of Proposition V1 (mean)')
    for i, v in enumerate(sp):
        b.text(i, v + 0.012, f'{v:.3f}', ha='center', fontsize=7, color=INK)
    b.set_xticks(range(4)); b.set_xticklabels(lab, fontsize=7.4); b.set_ylim(0, 0.72)
    b.set_ylabel('max - min over stakeholders of P(failure | data)\nat s = 0.5', color=INK2, fontsize=8.5)
    b.legend(fontsize=7, frameon=False, loc='upper right')
    b.set_title('(b) Information that resolves the event ends the dispute', fontsize=9.5, loc='left', color=INK); b.grid(axis='y', color=GRID, lw=0.5); style(b)
    c = fig.add_subplot(gs[1, 0])
    x = np.arange(4)
    nu = [S['designs'][d]['joint']['net'] for d in dn]; npool = [S['designs'][d]['joint']['pool_net'] for d in dn]
    rch = [S['designs'][d]['joint']['recharge'] for d in dn]; vet = [S['designs'][d]['joint']['pool_mean_vetoes'] for d in dn]
    c.bar(x - 0.18, nu, width=0.34, color='#1baf7a', label='unanimous certified rule (decisive)')
    c.bar(x + 0.18, npool, width=0.34, color='#c9c9c9', label='average-belief rule (vetoed)')
    for i in range(4):
        c.text(x[i] - 0.18, nu[i] + 120, f'{nu[i]:,.0f}\nrecharge\n{rch[i]:,.0f}', ha='center', fontsize=6.3, color=INK)
        c.text(x[i] + 0.18, npool[i] + 120, f'{npool[i]:,.0f}\n{vet[i]:.1f} vetoes', ha='center', fontsize=6.3, color=INK2)
    c.set_xticks(x); c.set_xticklabels(lab, fontsize=7.4); c.set_ylim(0, max(npool) * 1.45)
    c.set_ylabel('net water: pumped - 0.5 × recharged (m$^3$/d)', color=INK2, fontsize=8.5)
    c.legend(fontsize=7, frameon=False, loc='upper left')
    c.set_title('(c) The decisive choice of pumping and recharge', fontsize=9.5, loc='left', color=INK); c.grid(axis='y', color=GRID, lw=0.5); style(c)
    d = fig.add_subplot(gs[1, 1])
    for j, (dsel, mk) in enumerate((('none', 'o'), ('chloride sample (A30)', 's'))):
        fu = S['designs'][dsel]['joint']['fail_by_view']; fp = S['designs'][dsel]['joint']['pool_fail_by_view']
        xs = np.arange(5) + (j - 0.5) * 0.3
        d.scatter(xs, fu, marker=mk, s=40, color=COLS, edgecolor=INK, lw=0.5, zorder=5)
        d.scatter(xs, fp, marker='x', s=36, color=COLS, lw=1.4, zorder=4)
        for i in range(5):
            d.plot([xs[i], xs[i]], [fu[i], fp[i]], color=GRID, lw=1, zorder=1)
    d.axhline(al, color=INK, lw=0.9, ls=':')
    d.set_xticks(range(5)); d.set_xticklabels(SHORT, fontsize=7.2, rotation=12)
    d.set_ylim(0, 0.18); d.set_ylabel('realised failure frequency, by this stakeholder\'s belief', color=INK2, fontsize=8.5)
    h = [Line2D([], [], marker='o', ls='', color=INK2, label='unanimous rule, no data'), Line2D([], [], marker='s', ls='', color=INK2, label='unanimous rule, chloride sample'),
         Line2D([], [], marker='x', ls='', color=INK2, label='average-belief rule'), Line2D([], [], color=INK, ls=':', label='risk limit 10%')]
    d.legend(handles=h, fontsize=6.8, frameon=False, loc='upper left')
    d.set_title('(d) Every stakeholder is safe by their own belief', fontsize=9.5, loc='left', color=INK); d.grid(axis='y', color=GRID, lw=0.5); style(d)
    out = os.path.join(HERE, 'res', 'figV1_vendimi.png'); fig.savefig(out, dpi=200, bbox_inches='tight'); print('wrote', out)


if __name__ == '__main__':
    main()
