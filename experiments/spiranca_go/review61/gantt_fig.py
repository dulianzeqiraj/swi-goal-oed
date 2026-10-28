"""Gantt chart (annex 3.D): Working Group activity, networking activities, milestones M1-M4 and deliverables across
Months 1-48. By default deliverables D1-D10 are marked (as in the e-COST text); with --all13 the training content,
publications and final report are also labelled D11-D13. Timing from the HALOMAR annex, sections 3.B and 3.C;
conference months are indicative. Writes res/figG1_gantt.png (or res/figG1_gantt_D13.png)."""
import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED, NAVY = '#1f2933', '#52606d', '#1f3864'
plt.rcParams.update({'font.family': 'DejaVu Sans'})
COL = {'WG1': '#c27c12', 'WG2': '#2e6db4', 'WG3': '#1e8a5a', 'WG4': '#b03a3a', 'WG5': '#52606d', 'NET': '#6a4fb3'}


def rows(all13):
    d11 = [(12, 'D11'), (30, 'D11'), (42, 'D11')] if all13 else []
    d1213 = [(48, 'D12, D13')] if all13 else []
    return [
        ('WG1', 'Quantities of interest; chloride screening rule', [(1, 24)], [(24, 'D1')]),
        ('WG1', 'Status protocol; two-team falsification test', [(13, 46)], [(42, 'D7'), (46, 'D10')]),
        ('WG2', 'Siting workflows for both method families', [(1, 30)], [(30, 'D2')]),
        ('WG2', 'Benchmark: blind application, certificates', [(13, 36)], [(36, 'D4, D5')]),
        ('WG3', 'Recharge formulation and identification', [(1, 24)], []),
        ('WG3', 'Joint siting of recharge and monitoring', [(19, 36)], [(36, 'D3')]),
        ('WG4', 'Pumping records; years of records needed', [(1, 30)], []),
        ('WG4', 'Test for misleading records; guidance', [(25, 40)], [(40, 'D6')]),
        ('WG5', 'Inventory, data terms, application profile', [(1, 44)], [(44, 'D8')]),
        ('WG5', 'Open minimal workflow and tutorials', [(19, 40)], [(40, 'D9')]),
        ('NET', 'MC and joint WG meetings (annual)', [(1, 1), (12, 12), (24, 24), (36, 36), (48, 48)], []),
        ('NET', 'Working Group meetings, twice a year', [(m, m) for m in range(6, 49, 6)], []),
        ('NET', 'Short-Term Scientific Mission calls', [(m, m + 1) for m in (5, 11, 17, 23, 29, 35, 41)], []),
        ('NET', 'Training Schools 1–3', [(10, 11), (29, 30), (41, 42)], d11),
        ('NET', 'Open seminar with the Advisory Panel', [(11, 11), (23, 23), (35, 35), (47, 47)], []),
        ('NET', 'ISMAR 2028, SWIM 2029, IAH, next SWIM', [(9, 12), (19, 24), (43, 48)], []),
        ('NET', 'Open-access papers and final report', [(24, 48)], d1213),
    ]


MILES = [(12, 'M1', 'inventory, workflows'), (24, 'M2', 'consensus statement'), (36, 'M3', 'benchmark; test run'), (48, 'M4', 'outputs; capacity')]


def main(all13=False):
    W, H = 14.6, 11.0
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    rng = 'D1 to D13' if all13 else 'D1 to D10'
    ax.text(W / 2, 10.72, f'Gantt chart: Working Group activity, networking, milestones M1–M4 and deliverables {rng}',
            ha='center', va='center', fontsize=15.5, fontweight='bold', color=INK)

    X0, X1 = 4.55, 14.3
    X = lambda m: X0 + (X1 - X0) * (m - 0.5) / 48.0      # month m occupies [X(m), X(m+1)]
    R = rows(all13)
    rh = 0.43
    top = 9.45
    # year band
    for k in range(4):
        fc = ['#c9daf2', '#8fb3e3', '#5b8fd0', '#2e5d9e'][k]
        ax.add_patch(Rectangle((X(12 * k + 1), top + 0.5), X(12 * k + 13) - X(12 * k + 1), 0.38, fc=fc, ec='white', lw=1.5))
        ax.text((X(12 * k + 1) + X(12 * k + 13)) / 2, top + 0.69, f'Year {k + 1}  ·  Months {12 * k + 1}–{12 * k + 12}',
                ha='center', va='center', fontsize=11, fontweight='bold', color=INK if k < 2 else 'white')
    # milestones on top
    for m, ml, t in MILES:
        xm = X(m + 1) - 0.01
        ax.plot([xm, xm], [top - len(R) * rh - 0.05, top + 0.02], color='#f2b134', lw=1.6, ls='--', zorder=1)
        ax.plot([xm], [top + 0.22], marker='D', ms=12, color='#f2b134', mec=INK, mew=1.0, zorder=5)
        ax.text(xm - 0.16, top + 0.22, ml, ha='right', va='center', fontsize=10.6, fontweight='bold', color=INK)
    ax.text(X0 - 0.1, top + 0.22, 'Milestones', ha='right', va='center', fontsize=11, fontweight='bold', color='#b7791f')

    prev = None
    for i, (g, lab, spans, dels) in enumerate(R):
        y1 = top - i * rh
        y0 = y1 - rh
        yc = (y0 + y1) / 2
        if i % 2 == 0:
            ax.add_patch(Rectangle((0.2, y0), X1 - 0.2, rh, fc='#f6f7f9', ec='none', zorder=0))
        if g == 'NET' and prev != 'NET':
            ax.plot([0.2, X1], [y1, y1], color=INK, lw=1.2, zorder=2)
        prev = g
        col = COL[g]
        ax.add_patch(FancyBboxPatch((0.25, yc - 0.15), 0.62, 0.3, boxstyle='round,pad=0.01,rounding_size=0.06', fc=col, ec='none', zorder=2))
        ax.text(0.56, yc, 'NET' if g == 'NET' else g, ha='center', va='center', fontsize=9.8, color='white', fontweight='bold', zorder=3)
        ax.text(0.98, yc, lab, ha='left', va='center', fontsize=10.8, color=INK)
        for a, b in spans:
            ax.add_patch(FancyBboxPatch((X(a) + 0.01, yc - 0.13), X(b + 1) - X(a) - 0.02, 0.26,
                                        boxstyle='round,pad=0.0,rounding_size=0.05', fc=col, ec='none', alpha=0.9, zorder=3))
        for m, code in dels:
            xm = X(m + 1) - 0.06
            ax.plot([xm], [yc], marker='v', ms=10, color=INK, mec='white', mew=1.0, zorder=5)
            ax.text(xm + (0.1 if m >= 47 else 0.0), yc + 0.13, code, ha='right' if m >= 47 else 'center', va='bottom', fontsize=10, fontweight='bold', color=INK, zorder=6,
                    bbox=dict(boxstyle='round,pad=0.08', fc='white', ec='none', alpha=0.85))
    ybot = top - len(R) * rh
    # month axis
    ax.plot([X(1), X(49)], [ybot, ybot], color=INK, lw=1.3)
    for m in (1, 6, 12, 18, 24, 30, 36, 42, 48):
        xm = X(m) + (X(m + 1) - X(m)) / 2
        ax.plot([xm, xm], [ybot - 0.06, ybot], color=INK, lw=1.1)
        ax.text(xm, ybot - 0.1, str(m), ha='center', va='top', fontsize=10.6, color=INK)
    ax.text((X0 + X1) / 2, ybot - 0.42, 'Month of the Action (conference months indicative)', ha='center', va='top', fontsize=10.6, color=MUTED)

    # legend
    yl = ybot - 0.84
    items = [('WG1', 'WG1 Goals, chemistry, status'), ('WG2', 'WG2 Observing the front'), ('WG3', 'WG3 Recharge'),
             ('WG4', 'WG4 Pumping'), ('WG5', 'WG5 Data, software, transfer'), ('NET', 'Networking activities')]
    xs = [0.3, 3.12, 5.62, 7.47, 9.27, 12.15]
    for (k, t), xx in zip(items, xs):
        ax.add_patch(FancyBboxPatch((xx, yl - 0.1), 0.38, 0.2, boxstyle='round,pad=0.0,rounding_size=0.04', fc=COL[k], ec='none'))
        ax.text(xx + 0.48, yl, t, fontsize=10.6, va='center', color=INK)
    yl2 = yl - 0.38
    ax.plot([0.49], [yl2], marker='v', ms=10, color=INK)
    ax.text(0.78, yl2, 'deliverable (due month)', fontsize=10.6, va='center', color=INK)
    ax.plot([3.24], [yl2], marker='D', ms=10, color='#f2b134', mec=INK, mew=1.0)
    ax.text(3.5, yl2, 'milestone:  ' + ';  '.join(f'{ml} {t}' for _, ml, t in MILES), fontsize=10.6, va='center', color=INK)

    # what is new
    ax.add_patch(FancyBboxPatch((0.2, 0.2), W - 0.4, 0.52, boxstyle='round,pad=0.01,rounding_size=0.1', fc=NAVY, ec='none'))
    ax.text(W / 2, 0.46, 'New: the two-team falsification test (by Month 36) is on the critical path, and its outcome is recorded whichever way it falls.',
            ha='center', va='center', fontsize=11.2, color='white')
    name = 'figG1_gantt_D13.png' if all13 else 'figG1_gantt.png'
    fig.savefig(os.path.join(OUT, name), dpi=220)
    plt.close(fig)
    print('ok', name)


if __name__ == '__main__':
    main(all13='--all13' in sys.argv)
