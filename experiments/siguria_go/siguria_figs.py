"""Figure S1 of review 54 (SIGURIA-GO): (a) uncertainty of the risk: law over plausible aquifers of the intrusion
probability of the scheme, before and after the pilot tests of VENDI-GO; (b) robustness: the Wasserstein bound on
CVaR against the radius, with the radius each scheme tolerates and the model error of the 12-zone model;
(c) uniqueness: how often each site belongs to the scheme that would be optimal if the aquifer were known, with the
optimal scheme and its deflated alternatives. Run after siguria.py analyse.
"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'vendi_go'))
import vendi as V

INK, INK2, GRID = '#0b0b0b', '#52514e', '#d9d8d4'
BLUE, ORANGE = '#2a78d6', '#eb6834'


def main():
    J = json.load(open(os.path.join(HERE, 'res', 'siguria.json')))
    Z = np.load(os.path.join(HERE, 'res', 'siguria_fig.npz'))
    alpha = 0.05
    fig = plt.figure(figsize=(12.0, 4.6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.05])
    # ---------------------------------------------------------------- (a) uncertainty of the risk
    a = fig.add_subplot(gs[0])
    for r, col, lab in ((Z['r_prior'], BLUE, 'before tests (prior)'), (Z['r_post'], ORANGE, 'after VENDI-GO tests (posterior)')):
        x = np.sort(r); y = np.arange(1, len(x) + 1) / len(x)
        a.step(x, y, where='post', color=col, lw=1.6, label=lab)
    a.axvline(float(Z['truth_risk']), color=INK, lw=1, ls=(0, (4, 3)))
    a.annotate('true aquifer', (float(Z['truth_risk']), 0.5), xytext=(4, 0), textcoords='offset points', fontsize=7.5, color=INK, rotation=90, va='center')
    a.set_xscale('symlog', linthresh=1e-3); a.set_xlim(0, 1)
    a.set_xlabel('Intrusion probability of the scheme for one aquifer', color=INK2, fontsize=8.5)
    a.set_ylabel('Fraction of plausible aquifers', color=INK2, fontsize=8.5)
    a.legend(loc='upper left', fontsize=7.2, frameon=False)
    a.set_title(f"(a) Uncertainty of the risk (truth {J['after_tests']['truth']})", fontsize=9.5, color=INK, loc='left')
    # ---------------------------------------------------------------- (b) certificates after the tests
    b = fig.add_subplot(gs[1])
    rows = J['after_tests_all']['rows']
    lo = 1e-5
    x = np.array([max(r_['post'], lo) for r_ in rows]); y = np.array([max(r_['truth_risk'], lo) for r_ in rows])
    c5 = np.array([r_['rho'] > 0 for r_ in rows]); c10 = np.array([r_['rho10'] > 0 for r_ in rows]) & ~c5
    no = ~(c5 | c10)
    b.plot([lo, 1], [lo, 1], color=GRID, lw=1, zorder=0)
    b.scatter(x[c5], y[c5], s=34, c=ORANGE, edgecolors=INK, lw=0.5, zorder=3, label=f'certified at 5% ({c5.sum()})')
    b.scatter(x[c10], y[c10], s=34, c=BLUE, edgecolors=INK, lw=0.5, zorder=3, label=f'certified at 10% only ({c10.sum()})')
    b.scatter(x[no], y[no], s=34, facecolors='white', edgecolors=INK2, lw=0.9, zorder=3, label=f'not certified ({no.sum()})')
    b.set_xscale('log'); b.set_yscale('log'); b.set_xlim(lo, 1.5); b.set_ylim(lo, 1.5)
    b.set_xlabel('Posterior risk of the built scheme (VENDI-GO belief)', color=INK2, fontsize=8.5)
    b.set_ylabel('Risk in the true aquifer', color=INK2, fontsize=8.5)
    b.legend(loc='upper left', fontsize=7.2, frameon=False)
    b.set_title(f"(b) Certificates after the tests, {len(rows)} aquifers", fontsize=9.5, color=INK, loc='left')
    # ---------------------------------------------------------------- (c) uniqueness map
    c = fig.add_subplot(gs[2]); m = V.m; v = m.valid
    tp = V.triples(); bd = Z['best_d']
    freq = np.zeros(V.K)
    for s in tp[bd].ravel():
        freq[s] += 1
    freq /= len(bd)
    c.scatter(m.cx[v], m.cy[v], s=1.0, c='#ecebe7', marker='s', lw=0, zorder=0)
    sc = c.scatter(m.cx[V.SITE], m.cy[V.SITE], s=6 + 90 * freq / max(freq.max(), 1e-9), c=freq, cmap='Blues', vmin=0, vmax=max(freq.max(), 1e-9),
                   edgecolors='none', zorder=2)
    for cc, lab in ((V.cA, 'A1'), (V.cB, 'P10')):
        c.scatter(m.cx[cc], m.cy[cc], s=50, marker='^', c=INK, zorder=5)
        c.annotate(lab, (m.cx[cc], m.cy[cc]), xytext=(-10, 3), textcoords='offset points', fontsize=7.5, ha='right', color=INK)
    for i, d in enumerate(J['uniqueness_siting']['deflation']):
        xy = np.array(d['xy'])
        c.scatter(xy[:, 0], xy[:, 1], s=40 if i else 60, marker='s' if i == 0 else 'o', facecolors=ORANGE if i == 0 else 'white',
                  edgecolors=INK, lw=0.8, zorder=6)
        for x_, y_ in xy:
            c.annotate(str(i + 1), (x_, y_), xytext=(4, 2), textcoords='offset points', fontsize=7, color=INK, zorder=7)
    cb = fig.colorbar(sc, ax=c, fraction=0.04, pad=0.02); cb.ax.tick_params(labelsize=7, colors=INK2)
    cb.set_label('share of aquifers whose own optimum uses the site', fontsize=7, color=INK2)
    c.set_aspect('equal'); c.set_xlim(m.cx[v].min() - 0.8, m.cx[v].max() + 0.8); c.set_ylim(m.cy[v].min() - 0.8, m.cy[v].max() + 0.8)
    c.set_xlabel('Easting (km)', color=INK2, fontsize=8.5); c.set_ylabel('Northing (km)', color=INK2, fontsize=8.5)
    c.set_title('(c) Uniqueness of the siting', fontsize=9.5, color=INK, loc='left')
    for ax_ in (a, b, c):
        ax_.tick_params(colors=INK2, labelsize=7.5)
        for s_ in ax_.spines.values(): s_.set_color(GRID)
    fig.tight_layout()
    out = os.path.join(HERE, 'res', 'figS1_siguria.png'); fig.savefig(out, dpi=200); print('wrote', out)


if __name__ == '__main__':
    main()
