"""Deliverables D1-D13: a Month 0-48 timeline on Working Group lanes (marker = type), and a table with type, lead WG,
month and the objective each serves. Content from the HALOMAR annex, sections 1.B, 3.B and 3.C.
Writes res/figL1_deliverables.png (large type)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED, NAVY = '#1f2933', '#52606d', '#1f3864'
plt.rcParams.update({'font.family': 'DejaVu Sans'})

TYPES = {'document': ('o', '#2e6db4'), 'dataset': ('s', '#c27c12'), 'report': ('v', '#b03a3a'),
         'specification': ('^', '#0e7490'), 'software': ('D', '#6a4fb3'), 'training': ('p', '#1e8a5a'),
         'publications': ('h', '#52606d')}
LANES = [('WG1', '#c27c12', '#fff4e0'), ('WG2', '#2e6db4', '#e8f1fb'), ('WG3', '#1e8a5a', '#e6f5ee'),
         ('WG4', '#b03a3a', '#fdecec'), ('WG5', '#52606d', '#eceff3'), ('All / Action', NAVY, '#e9edf5')]
# (code, short title, type, lead, months, serves, lanes)
DEL = [('D1', 'Consensus statement: quantities of interest, chemical evidence, chloride screening rule', 'document', 'WG1', [24], 'RC1', [0]),
       ('D2', 'Joint protocol: both siting families as workflows; certificate; minimal version', 'document', 'WG2', [30], 'RC2', [1]),
       ('D3', 'Recharge formulation and joint siting guideline for recharge and monitoring', 'document', 'WG3', [36], 'RC3', [2]),
       ('D4', 'Open benchmark dataset: common aquifers, derived series, priors, design problems', 'dataset', 'WG2, WG5', [36], 'RC2–RC4', [1, 4]),
       ('D5', 'Comparative report on the siting families: thresholds, price, leak, certificates', 'report', 'WG2', [36], 'RC2', [1]),
       ('D6', 'Pumping guidance: years of records needed, what to log, test for misleading records', 'document', 'WG4', [40], 'RC4', [3]),
       ('D7', 'Status reporting protocol with a worked example and the falsification-test outcome', 'document', 'WG1', [42], 'RC5', [0]),
       ('D8', 'Application profile and metadata specification in existing standards', 'specification', 'WG5', [44], 'RC5', [4]),
       ('D9', 'Open minimal workflow with tutorials: screening, certificate, siting, years of records', 'software', 'WG5', [40], 'RC2–RC4, CB5', [4]),
       ('D10', 'Policy brief in the form a river basin plan can adopt; national-language versions', 'document', 'WG1, WG5', [46], 'RC5, CB4', [0, 4]),
       ('D11', 'Openly licensed training content from the three Training Schools', 'training', 'WG5', [12, 30, 42], 'CB1', [4]),
       ('D12', 'Open-access papers: benchmark, field tests, threshold distributions, falsification test', 'publications', 'all WGs', [24, 48], 'all', [5]),
       ('D13', 'Final report, with the closing capacity assessment against the Year 1 baseline', 'report', 'Action', [48], 'all; capacity', [5])]
# small horizontal nudges (months) where two markers share a lane and month
NUDGE = {('D4', 1): -0.8, ('D5', 1): 0.8, ('D9', 4): -0.6, ('D4', 4): 0.0}


def rbox(ax, x0, y0, w, h, fc, ec, lw=1.1, r=0.06, z=1):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle=f'round,pad=0.01,rounding_size={r}', fc=fc, ec=ec, lw=lw, zorder=z))


def main():
    W, H = 14.6, 11.0
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    ax.text(W / 2, 10.74, 'Deliverables: thirteen outputs, when each falls, who produces it, and what it serves',
            ha='center', va='center', fontsize=15.5, fontweight='bold', color=INK)

    # ---------- timeline ----------
    X0, X1 = 2.15, 14.15
    X = lambda m: X0 + (X1 - X0) * m / 48.0
    yh0, yh1 = 10.0, 10.36
    for k in range(4):
        fc = ['#c9daf2', '#8fb3e3', '#5b8fd0', '#2e5d9e'][k]
        ax.add_patch(Rectangle((X(12 * k), yh0), X(12 * k + 12) - X(12 * k), yh1 - yh0, fc=fc, ec='white', lw=1.5, zorder=2))
        ax.text((X(12 * k) + X(12 * k + 12)) / 2, (yh0 + yh1) / 2, f'Year {k + 1}', ha='center', va='center', fontsize=11,
                fontweight='bold', color=INK if k < 2 else 'white', zorder=3)
    lh, top = 0.5, 9.95
    for r, (lab, col, fill) in enumerate(LANES):
        y0 = top - (r + 1) * lh
        ax.add_patch(Rectangle((X(0), y0 + 0.03), X(48) - X(0), lh - 0.06, fc=fill, ec='none', zorder=0))
        rbox(ax, 0.2, y0 + 0.03, 1.85, lh - 0.06, col, col, lw=0)
        ax.text(1.125, y0 + lh / 2, lab, ha='center', va='center', fontsize=10.8, fontweight='bold', color='white')
    ybot = top - len(LANES) * lh
    for m, ml in ((12, 'M1'), (24, 'M2'), (36, 'M3'), (48, 'M4')):
        ax.plot([X(m), X(m)], [ybot, top], color='#f2b134', lw=1.6, ls='--', zorder=1)
    ax.plot([X(0), X(48)], [ybot, ybot], color=INK, lw=1.4, zorder=2)
    for m in range(0, 49, 6):
        ax.plot([X(m), X(m)], [ybot - 0.06, ybot], color=INK, lw=1.2, zorder=2)
        lab = f'M{m}' if m % 12 else f'Month {m}'
        ax.text(X(m), ybot - 0.1, lab, ha='center', va='top', fontsize=9.8 if m % 12 else 10.4, color=MUTED if m % 12 else INK,
                fontweight='normal' if m % 12 else 'bold')
    for m, ml in ((12, 'M1'), (24, 'M2'), (36, 'M3'), (48, 'M4')):
        ax.text(X(m) + (0.0 if m < 48 else -0.02), ybot - 0.36, ml, ha='center', va='top', fontsize=10, color='#b7791f', fontweight='bold')
    for code, title, typ, lead, months, serves, lanes in DEL:
        mk, col = TYPES[typ]
        for li in lanes:
            yc = top - li * lh - lh / 2
            if typ == 'publications':
                ax.add_patch(Rectangle((X(months[0]), yc - 0.09), X(months[1]) - X(months[0]), 0.18, fc=col, ec='none', alpha=0.85, zorder=3))
                ax.text((X(months[0]) + X(months[1])) / 2, yc + 0.12, code + '  (Months 24–48)', ha='center', va='bottom', fontsize=10, fontweight='bold', color=INK, zorder=5)
                continue
            for m in months:
                xm = X(m + NUDGE.get((code, li), 0.0))
                ax.plot([xm], [yc - 0.04], marker=mk, ms=11, color=col, mec='white', mew=1.2, zorder=4)
                ax.text(xm, yc + 0.08, code, ha='center', va='bottom', fontsize=10, fontweight='bold', color=INK, zorder=5)

    # ---------- table ----------
    cols = [(0.2, 0.85, 'D'), (0.9, 8.1, 'Deliverable'), (8.15, 10.05, 'Type'), (10.1, 11.35, 'Lead'), (11.4, 12.65, 'Month'), (12.7, 14.4, 'Serves')]
    th0, th1 = 5.9, 6.3
    for x0, x1, t in cols:
        rbox(ax, x0, th0, x1 - x0, th1 - th0, '#eceff3', '#9aa5b1', lw=1.0)
        ax.text((x0 + x1) / 2, (th0 + th1) / 2, t, ha='center', va='center', fontsize=11, fontweight='bold', color=INK)
    rh = 0.345
    for i, (code, title, typ, lead, months, serves, lanes) in enumerate(DEL):
        y1 = th0 - 0.04 - i * rh
        y0 = y1 - rh + 0.03
        ym = (y0 + y1) / 2
        ax.add_patch(Rectangle((0.2, y0), 14.2, y1 - y0, fc='#f6f7f9' if i % 2 == 0 else 'white', ec='none', zorder=0))
        mk, col = TYPES[typ]
        ax.text(0.525, ym, code, ha='center', va='center', fontsize=10.6, fontweight='bold', color=INK)
        ax.text(0.98, ym, title, ha='left', va='center', fontsize=10.4, color=INK)
        ax.plot([8.32], [ym], marker=mk, ms=10, color=col, mec='white', mew=1.0)
        ax.text(8.5, ym, typ, ha='left', va='center', fontsize=10.4, color=col, fontweight='bold')
        ax.text((10.1 + 11.35) / 2, ym, lead, ha='center', va='center', fontsize=10.4, color=INK)
        mt = 'M24–48' if typ == 'publications' else ', '.join(f'M{m}' for m in months)
        ax.text((11.4 + 12.65) / 2, ym, mt, ha='center', va='center', fontsize=10.4 if len(months) < 3 else 9.8, color=INK, fontweight='bold')
        ax.text((12.7 + 14.4) / 2, ym, serves, ha='center', va='center', fontsize=10.4, color=INK)

    # ---------- what is new ----------
    rbox(ax, 0.2, 0.2, W - 0.4, 0.92, NAVY, NAVY, lw=0, r=0.1)
    ax.text(W / 2, 0.66, 'New: every deliverable is something an authority can run or check: protocols with a worked example, open software\n'
            'with a minimal version, a falsification test reported whichever way it falls. All open; networking is the means, not a deliverable.',
            ha='center', va='center', fontsize=11.2, color='white', linespacing=1.35)
    fig.savefig(os.path.join(OUT, 'figL1_deliverables.png'), dpi=220)
    plt.close(fig)
    print('ok')


if __name__ == '__main__':
    main()
