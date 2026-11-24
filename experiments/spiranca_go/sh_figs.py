"""Figure for the H_max test: worst-storyline exceedance against worst-storyline water, for each configuration.
Reads res/sh.json, writes res/figH1_hmax.png and prints the summary table."""
import os, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'res', 'sh.json')))
rows, SC, CF = D['rows'], D['scen'], D['configs']


def summary():
    out = {}
    for c in CF:
        e = {s: np.mean([r['res'][c][s]['exc'] for r in rows]) for s in SC}
        g = lambda k: {s: np.mean([r['res'][c][s][k] for r in rows]) for s in SC}
        w, p, t, dcl = g('water'), g('priv'), g('total'), g('decl')
        se = max(e, key=e.get)
        out[c] = dict(exc=e[se], exc_sc=se, exc_all=e, water=min(w.values()), priv=min(p.values()), total=min(t.values()),
                      water_sc=min(w, key=w.get), priv_sc=min(p, key=p.get), decl_dry=dcl['drought'], decl_none=dcl['none'],
                      n10=sum(max(r['res'][c][s]['exc'] for s in SC) > 0.05 for r in rows))
    return out


def label(c):
    u, h = c.split('_')
    u = u[1:]; h = h[1:]
    return f"u={u}, no cap" if h == 'none' else f"u={u}, cap {h}"


if __name__ == '__main__':
    S = summary()
    INK, MUTED, GRID = '#1f2933', '#616e7c', '#d9dee3'
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    for c, v in S.items():
        cap = not c.endswith('Hnone')
        col = '#009e73' if cap else ('#0072b2' if not c.startswith('u0.3') else '#7b8794')
        ax.plot(100 * v['exc'], 100 * v['total'], 'o', ms=7, color=col, mec='white', mew=1.2, zorder=3)
        ax.annotate(label(c), (100 * v['exc'], 100 * v['total']), xytext=(6, 3), textcoords='offset points', fontsize=7.5, color=INK)
    ax.axvline(5, color='#c0392b', ls='--', lw=1); ax.text(5, 1.01, ' ε = 5%', transform=ax.get_xaxis_transform(), fontsize=8, color='#c0392b', va='bottom')
    ax.axvline(10, color=MUTED, ls=':', lw=1); ax.text(10, 1.01, ' 10%', transform=ax.get_xaxis_transform(), fontsize=8, color=MUTED, va='bottom')
    ax.set_xlabel('worst-storyline seasons above 250 mg/L (%)')
    ax.set_ylabel('worst-storyline total water delivered (%)')
    ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    ax.plot([], [], 'o', color='#7b8794', label='decided pumping +0.3, no cap')
    ax.plot([], [], 'o', color='#009e73', label='cap on private abstraction in a declared drought')
    ax.plot([], [], 'o', color='#0072b2', label='lower decided pumping, no cap')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=2, frameon=False, fontsize=7.5)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, 'res', 'figH1_hmax.png'), dpi=200, bbox_inches='tight')
    for c, v in S.items():
        print(f"{c:12s} exc {100*v['exc']:5.1f}% ({v['exc_sc']}) n>5% {v['n10']:2d}  util {100*v['water']:5.1f}%  priv {100*v['priv']:5.1f}%  total {100*v['total']:5.1f}%  decl dry {100*v['decl_dry']:.0f}% ord {100*v['decl_none']:.0f}%  " +
              ' '.join(f"{s}:{100*v['exc_all'][s]:.1f}" for s in SC))
