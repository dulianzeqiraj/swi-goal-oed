"""Objectives of the Action as a matrix: relevant to the main challenge, achievable in four years, concrete, ambitious.
Content from the HALOMAR annex, sections 1.B and 3.A. Writes res/figO1_objectives.png (large type)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED = '#1f2933', '#52606d'
plt.rcParams.update({'font.family': 'DejaVu Sans'})
HEAD = [('Objective', '#1f3864'), ('Relevant: part of the\nmain challenge', '#b03a3a'), ('Achievable: who and when\n(Years 1–4)', '#1e8a5a'),
        ('Concrete: deliverable', '#2e6db4'), ('Ambitious: what is new', '#6a4fb3')]
X = [(0.2, 3.65), (3.75, 6.0), (6.1, 9.0), (9.1, 11.65), (11.75, 14.4)]
ROWS = [
    ('RC1', 'Agree what an observation\nis for, and when chemistry\ncounts as evidence', 'reading the chemistry;\ncommon goals', 'WG1', 2,
     'consensus statement\nagreed by all countries', 'when chloride alone can\nforecast chloride, and\nat what price'),
    ('RC2', 'Site observation of the\nsaline front, with certified\nrankings', 'observing the front', 'WG2', 3,
     'joint protocol, open\nbenchmark, comparative\nreport', 'two method families run\nblind on karst, alluvial\nand deltaic aquifers'),
    ('RC3', 'Formulate and identify\nrecharge; site it jointly\nwith monitoring', 'recharging', 'WG3', 3,
     'recharge formulation and\njoint siting guideline', 'recharge and monitoring\ncompete for one budget'),
    ('RC4', 'Know when a pumping rule\nlearned from records can\nbe trusted', 'pumping', 'WG4', 4,
     'guidance on learning\npumping rules from\nrecords', 'years of records per well\nfield; a test that reveals\nmisleading records'),
    ('RC5', 'Make national status\nassessments comparable', 'status under the Water\nFramework Directive', 'WG1+5', 4,
     'reporting protocol and\nFAIR data profile', 'falsifiable: two national\nteams, working blind, must\nreturn the same class'),
    ('CB1–5', 'Build capacity where\nmonitoring is thinnest', 'uneven capacity across\ncountries', 'WG5', 0,
     '3 Training Schools, STSMs,\nbriefs for basin plans and\noperating procedures', '≥ half of WG leaders from\nITC, ≥ a third young\nresearchers, ≥ 40% women'),
]
CHIP = {'RC1': '#c27c12', 'RC2': '#2e6db4', 'RC3': '#1e8a5a', 'RC4': '#b03a3a', 'RC5': '#6a4fb3', 'CB1–5': '#52606d'}


def main():
    W, H = 14.6, 10.0
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    ax.text(W / 2, 9.7, 'Objectives: relevant, achievable, concrete and ambitious', ha='center', va='center', fontsize=16, fontweight='bold', color=INK)
    yh0, yh1 = 8.75, 9.35
    for (x0, x1), (t, c) in zip(X, HEAD):
        ax.add_patch(FancyBboxPatch((x0, yh0), x1 - x0, yh1 - yh0, boxstyle='round,pad=0.01,rounding_size=0.08', fc=c, ec='none'))
        ax.text((x0 + x1) / 2, (yh0 + yh1) / 2, t, ha='center', va='center', fontsize=11.5, color='white', fontweight='bold', linespacing=1.15)
    rh, y = 1.3, yh0 - 0.1
    for k, (code, obj, rel, wg, year, deliv, amb) in enumerate(ROWS):
        yt, yb = y - k * rh, y - (k + 1) * rh + 0.08
        ym = (yt + yb) / 2
        ax.add_patch(Rectangle((0.2, yb), 14.2, yt - yb, fc='#f6f7f9' if k % 2 == 0 else 'white', ec='#d9dee3', lw=0.8, zorder=0))
        c = CHIP[code]
        ax.add_patch(FancyBboxPatch((0.32, ym - 0.28), 0.82, 0.56, boxstyle='round,pad=0.01,rounding_size=0.08', fc=c, ec='none', zorder=2))
        ax.text(0.73, ym, code, ha='center', va='center', fontsize=12, color='white', fontweight='bold', zorder=3)
        ax.text(1.27, ym, obj, ha='left', va='center', fontsize=11.2, color=INK, linespacing=1.2)
        ax.text((X[1][0] + X[1][1]) / 2, ym, rel, ha='center', va='center', fontsize=11.2, color='#b03a3a', linespacing=1.2)
        # mini Gantt: four year cells
        gx0, gw = 6.2, 0.52
        ax.text(gx0 + 4 * gw + 0.22, ym, wg, ha='left', va='center', fontsize=10.8, color='#1e8a5a', fontweight='bold')
        for yr in range(4):
            ax.add_patch(Rectangle((gx0 + yr * gw, ym - 0.17), gw, 0.34, fc='white', ec='#9aa5b1', lw=0.8, zorder=1))
        end = 4 if year == 0 else year
        ax.add_patch(Rectangle((gx0, ym - 0.17), end * gw, 0.34, fc='#1e8a5a', ec='none', alpha=0.85, zorder=2))
        if year:
            xd = gx0 + year * gw - 0.05
            ax.add_patch(Polygon([(xd, ym + 0.27), (xd + 0.13, ym), (xd, ym - 0.27), (xd - 0.13, ym)], closed=True, fc='#f2b134', ec=INK, lw=0.8, zorder=3))
        ax.text((X[3][0] + X[3][1]) / 2, ym, deliv, ha='center', va='center', fontsize=11.2, color='#2e6db4', linespacing=1.2)
        ax.text((X[4][0] + X[4][1]) / 2, ym, amb, ha='center', va='center', fontsize=11.2, color='#6a4fb3', linespacing=1.2)
    # year labels under the header
    for yr in range(4):
        ax.text(6.2 + yr * 0.52 + 0.26, yh0 - 0.03, f'Y{yr + 1}', ha='center', va='top', fontsize=10, color=MUTED)
    # legend
    yl = y - len(ROWS) * rh - 0.18
    ax.add_patch(Rectangle((0.3, yl - 0.13), 0.5, 0.26, fc='#1e8a5a', ec='none', alpha=0.85))
    ax.text(0.9, yl, 'work period', fontsize=11, va='center', color=INK)
    ax.add_patch(Polygon([(2.75, yl + 0.2), (2.88, yl), (2.75, yl - 0.2), (2.62, yl)], closed=True, fc='#f2b134', ec=INK, lw=0.8))
    ax.text(3.0, yl, 'deliverable due', fontsize=11, va='center', color=INK)
    ax.text(14.35, yl, 'RC: research coordination   CB: capacity building   ITC: Inclusiveness Target Countries',
            fontsize=11, va='center', ha='right', color=MUTED)
    fig.savefig(os.path.join(OUT, 'figO1_objectives.png'), dpi=220)
    plt.close(fig)
    print('ok')


if __name__ == '__main__':
    main()
