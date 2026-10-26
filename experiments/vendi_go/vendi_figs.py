"""Figure V1 of review 53 (VENDI-GO): (a) the sector, the supply wells, the existing wells read in Stage 0,
the candidate lattice and one prior truth with the sites each policy tested and built; (b) mean risk against
mean number of pilot tests for every policy, with lines of equal cost J = risk + kappa * tests.
Run after vendi.py run: python3 vendi_figs.py res/runs_0_200.json
"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vendi as V

INK, INK2, GRID = '#0b0b0b', '#52514e', '#d9d8d4'
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
NAMES = {'none': 'no recharge', 'published_cells': 'published cells', 'area_cells': 'area adjoint',
         'prag_cells': 'PRAG-MAR cells', 'prag_prior': 'PRAG-MAR (lattice)', 'prag_s0': 'PRAG-MAR after Stage 0',
         'random': 'random tests', 'thompson': 'Thompson sampling', 'confirm': 'plan and confirm',
         'vendi_noS0': 'VENDI-GO, no Stage 0', 'vendi': 'VENDI-GO', 'oracle': 'oracle (knows the aquifer)'}


def main(path):
    D = json.load(open(path)); rows = D['rows']; kappa = D['constants']['KAPPA']
    by = {}
    for r in rows:
        by.setdefault(r['policy'], {})[r['truth']] = r
    T = sorted(by['vendi'])
    stat = {}
    for p, d in by.items():
        r = np.array([d[t]['risk'] for t in T]); k = np.array([d[t]['tests'] for t in T])
        stat[p] = (r.mean(), 1.96 * r.std(ddof=1) / np.sqrt(len(T)), k.mean())
    # example truth: VENDI close to the oracle and far better than PRAG-MAR on the lattice
    score = [(by['prag_prior'][t]['risk'] - by['vendi'][t]['risk']) if
             (by['vendi'][t]['risk'] - by['oracle'][t]['risk'] < 0.01 and by['vendi'][t]['tests'] <= 5) else -1 for t in T]
    tex = T[int(np.argmax(score))]
    fig, ax = plt.subplots(1, 2, figsize=(11.2, 5.6), gridspec_kw={'width_ratios': [1.0, 1.25]})
    # ---------------------------------------------------------- (a) map
    a = ax[0]; m = V.m
    v = m.valid
    a.scatter(m.cx[v], m.cy[v], s=1.2, c='#ecebe7', marker='s', lw=0, zorder=0)
    a.scatter(m.cx[m.sea_idx], m.cy[m.sea_idx], s=3, c=BLUE, marker='s', lw=0, zorder=1, label='sea contact')
    a.scatter(m.cx[V.SITE], m.cy[V.SITE], s=4, c='#9a9893', lw=0, zorder=2, label='candidate sites (1 km lattice)')
    a.scatter(m.cx[V.OBS], m.cy[V.OBS], s=26, facecolors='white', edgecolors=INK, lw=0.9, zorder=3, label='existing wells read in Stage 0')
    for c, lab in ((V.cA, 'A1'), (V.cB, 'P10')):
        a.scatter(m.cx[c], m.cy[c], s=70, marker='^', c=INK, zorder=5)
        a.annotate(lab, (m.cx[c], m.cy[c]), xytext=(-14, 4), textcoords='offset points', fontsize=9, color=INK, ha='right')
    ve, orc, pp = by['vendi'][tex], by['oracle'][tex], by['prag_prior'][tex]
    tested = [s for s in ve['tested'] if s not in ve['sites']]
    a.scatter(m.cx[V.SITE[tested]], m.cy[V.SITE[tested]], s=46, marker='s', facecolors='none', edgecolors=ORANGE, lw=1.3, zorder=6,
              label='VENDI-GO: tested, not built')
    a.scatter(m.cx[V.SITE[ve['sites']]], m.cy[V.SITE[ve['sites']]], s=60, marker='s', c=ORANGE, edgecolors=INK, lw=0.5, zorder=7,
              label=f"VENDI-GO: built (risk {ve['risk']:.2f})")
    a.scatter(m.cx[V.SITE[orc['sites']]], m.cy[V.SITE[orc['sites']]], s=150, marker='o', facecolors='none', edgecolors=INK, lw=1.2, zorder=8,
              label=f"oracle (risk {orc['risk']:.2f})")
    a.scatter(m.cx[V.SITE[pp['sites']]], m.cy[V.SITE[pp['sites']]], s=60, marker='x', c=BLUE, lw=1.6, zorder=8,
              label=f"PRAG-MAR on the lattice (risk {pp['risk']:.2f})")
    a.set_aspect('equal'); a.set_xlabel('Easting from the model origin (km)', color=INK2, fontsize=9)
    a.set_ylabel('Northing from the model origin (km)', color=INK2, fontsize=9)
    a.set_xlim(m.cx[v].min() - 0.8, m.cx[v].max() + 0.8); a.set_ylim(m.cy[v].min() - 0.8, m.cy[v].max() + 0.8)
    a.tick_params(colors=INK2, labelsize=8)
    for s_ in a.spines.values(): s_.set_color(GRID)
    a.legend(loc='upper right', fontsize=7.2, frameon=True, framealpha=0.95, edgecolor=GRID, borderpad=0.5)
    a.set_title(f'(a) Prior truth {tex}: what was tested and built', fontsize=10, color=INK, loc='left')
    # ---------------------------------------------------------- (b) risk against tests
    b = ax[1]
    kx = np.linspace(-0.4, 12.6, 50)
    J0 = stat['vendi'][0] + kappa * stat['vendi'][2]
    for J in (J0 - 0.04, J0, J0 + 0.04, J0 + 0.08, J0 + 0.12, J0 + 0.16):
        b.plot(kx, J - kappa * kx, color=GRID, lw=0.8, zorder=0)
    b.annotate(f'lines of equal cost J = risk + {kappa:g} × tests', (6.3, J0 - kappa * 6.3), xytext=(0, 3), textcoords='offset points',
               fontsize=7.3, color=INK2, rotation=-3.2, ha='left', va='bottom')
    groups = {'earlier': (['prag_cells', 'prag_prior', 'prag_s0'], '#7a7975'),
              'learning': (['random', 'thompson', 'confirm', 'vendi_noS0'], BLUE),
              'vendi': (['vendi'], ORANGE)}
    offs = {'prag_cells': (-9, 1, 'right'), 'prag_prior': (-9, 0, 'right'), 'prag_s0': (-9, -2, 'right'),
            'random': (9, 0, 'left'), 'thompson': (-9, 0, 'right'), 'confirm': (-7, -17, 'right'),
            'vendi_noS0': (8, 13, 'left'), 'vendi': (9, -15, 'left'), 'oracle': (9, -2, 'left')}
    for g, (pols, col) in groups.items():
        for p in pols:
            mu, ci, k = stat[p]
            b.errorbar(k, mu, yerr=ci, fmt='o', ms=6 if p != 'vendi' else 8, color=col, mec=INK if p == 'vendi' else col,
                       ecolor=col, elinewidth=1, capsize=2, zorder=3)
            dx, dy, ha = offs[p]
            b.annotate(NAMES[p], (k, mu), xytext=(dx, dy), textcoords='offset points', fontsize=7.6,
                       color=INK, ha=ha, va='center', fontweight='bold' if p == 'vendi' else 'normal')
    mu, ci, k = stat['oracle']
    b.errorbar(k, mu, yerr=ci, fmt='D', ms=6, mfc='white', mec=INK, ecolor=INK, elinewidth=1, capsize=2, zorder=3)
    dx, dy, ha = offs['oracle']
    b.annotate(NAMES['oracle'], (k, mu), xytext=(dx, dy), textcoords='offset points', fontsize=7.6, color=INK, ha=ha, va='center')
    off = ', '.join(f"{NAMES[p]} {stat[p][0]:.2f}" for p in ('none', 'published_cells', 'area_cells'))
    b.text(0.02, 0.98, f'Above the frame: {off}', transform=b.transAxes, fontsize=7.3, color=INK2, va='top', ha='left')
    b.set_xlim(-0.6, 12.6); b.set_ylim(0.10, 0.40)
    b.set_xlabel('Mean number of pilot tests', color=INK2, fontsize=9)
    b.set_ylabel('Mean P(A1 or P10 intruded) over prior truths', color=INK2, fontsize=9)
    b.tick_params(colors=INK2, labelsize=8); b.grid(axis='y', color='#eceae6', lw=0.6); b.set_axisbelow(True)
    for s_ in ('top', 'right'): b.spines[s_].set_visible(False)
    for s_ in ('left', 'bottom'): b.spines[s_].set_color(GRID)
    b.set_title(f'(b) Risk against pilot tests, {len(T)} prior truths (95% intervals)', fontsize=10, color=INK, loc='left')
    fig.tight_layout()
    out = os.path.join(HERE, 'res', 'figV1_vendi.png')
    fig.savefig(out, dpi=200); print('wrote', out, 'example truth', tex)
    json.dump({'example_truth': tex, 'oracle_risk': float(by['oracle'][tex]['risk']), 'stat': {p: list(map(float, s)) for p, s in stat.items()}},
              open(os.path.join(HERE, 'res', 'fig_stats.json'), 'w'), indent=1)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'res', 'runs_0_200.json'))
