"""Communication, dissemination and valorisation: five audiences, what each receives, the channel it already uses,
when, and why it is attainable; a Year 1-4 timeline of venues and outputs; valorisation as adoption.
Content from the HALOMAR annex, sections 2.A, 2.C, 3.B and 3.C. Writes res/figD1_dissemination.png (large type)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED, NAVY, GREEN = '#1f2933', '#52606d', '#1f3864', '#1e8a5a'
plt.rcParams.update({'font.family': 'DejaVu Sans'})


def rbox(ax, x0, y0, w, h, fc, ec, lw=1.2, r=0.08, z=1):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle=f'round,pad=0.012,rounding_size={r}', fc=fc, ec=ec, lw=lw, zorder=z))


COLS = [(0.2, 2.3), (2.4, 5.5), (5.6, 9.65), (9.75, 11.3), (11.4, 14.4)]
HEAD = ['Audience', 'What they receive', 'Channel they already use', 'When', 'Attainable because']

ROWS = [
    ('Research\ncommunity', '#0e7490', '#e3f4f7',
     'benchmark, cross-site tests,\nthreshold distributions and the\nfalsification test (D4, D5, D12)',
     'SWIM, the field\'s venue since 1968: own\nsession in Bari 2029; ISMAR, Eurokarst,\nIAH Congress; maths results to probability,\nUQ and inverse-problem venues',
     'Y1  ISMAR 2028\nY2  SWIM 2029\nY4  next SWIM',
     'the venues exist; Bari falls in\nYear 2, inside the Action\'s\ngeography; all papers open'),
    ('Record holders\nand authorities', GREEN, '#e6f5ee',
     'status protocol, chloride rule,\nrecharge guideline, pumping\nguidance (D1, D3, D6, D7)',
     'short procedural documents with a\nworked example, brought to each country\nby its own WG member; Training School 3\nteaches the workflow to their staff',
     'M24–M42',
     'the form they already work in:\nadoption needs no translation\nstep'),
    ('Policymakers', '#2e6db4', '#e8f1fb',
     'policy brief in the register of a\nriver basin management plan\n(D10), in national languages',
     'national reporting to WISE (European\nCommission and EEA) through the Eionet\nCentral Data Repository; the protocol is\ndocumented against these structures',
     'M46, for the\n2033 plans',
     'no new legal instrument; the\nAction improves what is fed\nin, not the reporting system'),
    ('Public and\nwater users', '#c27c12', '#fff4e0',
     'plain-language summary of every\ndeliverable; explainers on why a\nwell is placed where it is',
     'Action website; national-language versions\nby each country\'s members; an annual\nopen web seminar with the Advisory Panel',
     'with each\ndeliverable;\nseminar yearly',
     'a Science Communication\nCoordinator owns it; members\nwrite the national versions'),
    ('Practitioners\nand data users', '#6a4fb3', '#f1ecfa',
     'open minimal workflow with\ntutorials (D9); benchmark series\n(D4); application profile (D8)',
     'GroundWaterML 2 (OGC WaterML 2: Part 4);\nINSPIRE Geology and Environmental\nMonitoring Facilities; IGRAC Global\nMAR Inventory; FAIR, open licences',
     'M36–M44',
     'built from code members\nalready maintain; standards\nalready adopted'),
]

YEARS = [('Year 1', 'ISMAR 2028: recruit recharge\nschemes; Training School 1'),
         ('Year 2', 'SWIM 2029, Bari: own session;\nconsensus statement D1 (M24)'),
         ('Year 3', 'benchmark D4, comparative\nreport D5 (M36); Training School 2'),
         ('Year 4', 'next SWIM, IAH Congress; workflow,\nprotocol, brief (M40–M46)')]


def main():
    W, H = 14.6, 11.0
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    ax.text(W / 2, 10.74, 'Communication, dissemination and valorisation: the right channel for each audience',
            ha='center', va='center', fontsize=16, fontweight='bold', color=INK)
    rbox(ax, 0.2, 9.98, W - 0.4, 0.46, NAVY, NAVY, lw=0)
    ax.text(W / 2, 10.21, 'Each audience is reached through a channel it already uses: no new portal, journal or conference beyond the Action website',
            ha='center', va='center', fontsize=11.6, color='white', fontweight='bold')

    # timeline: four years as chevrons, events above
    yb0, yb1 = 8.88, 9.2
    seg = (W - 0.4) / 4
    shades = ['#c9daf2', '#8fb3e3', '#5b8fd0', '#2e5d9e']
    for k, ((yl, ev), fc) in enumerate(zip(YEARS, shades)):
        x0, x1 = 0.2 + k * seg, 0.2 + (k + 1) * seg
        n = 0.0 if k == 0 else 0.14
        tip = 0.14 if k < 3 else 0.0
        ym = (yb0 + yb1) / 2
        pts = [(x0, yb0), (x1 - tip, yb0), (x1, ym), (x1 - tip, yb1), (x0, yb1), (x0 + n, ym)]
        ax.add_patch(Polygon(pts, closed=True, fc=fc, ec='white', lw=1.5, zorder=2))
        ax.text((x0 + x1) / 2, ym, yl, ha='center', va='center', fontsize=10.8, fontweight='bold', color=INK if k < 2 else 'white', zorder=3)
        ax.text(x0 + 0.12, 9.3, ev, ha='left', va='bottom', fontsize=10.8, color=INK, linespacing=1.12)

    # header
    yh0, yh1 = 8.3, 8.72
    for (x0, x1), t in zip(COLS, HEAD):
        rbox(ax, x0, yh0, x1 - x0, yh1 - yh0, '#eceff3', '#9aa5b1', lw=1.0)
        ax.text((x0 + x1) / 2, (yh0 + yh1) / 2, t, ha='center', va='center', fontsize=11.5, fontweight='bold', color=INK)

    rh, gy, top = 1.05, 0.07, 8.22
    for r, (name, col, fill, rec, chan, when, why) in enumerate(ROWS):
        y0 = top - (r + 1) * rh - r * gy
        ym = y0 + rh / 2
        x0, x1 = COLS[0]
        rbox(ax, x0, y0, x1 - x0, rh, col, col, lw=0)
        ax.text((x0 + x1) / 2, ym, name, ha='center', va='center', fontsize=11.2, fontweight='bold', color='white', linespacing=1.08)
        for k, txt, fc, tc, ha in ((1, rec, fill, INK, 'left'), (2, chan, 'white', INK, 'left'), (3, when, fill, col, 'center'), (4, why, fill, INK, 'left')):
            cx0, cx1 = COLS[k]
            rbox(ax, cx0, y0, cx1 - cx0, rh, fc, col, lw=1.0)
            xt = cx0 + 0.1 if ha == 'left' else (cx0 + cx1) / 2
            ax.text(xt, ym, txt, ha=ha, va='center', fontsize=10.3, color=tc, linespacing=1.12, zorder=3,
                    fontweight='bold' if k == 3 else 'normal')

    # valorisation + measure
    yv0, yv1 = 1.38, 2.6
    rbox(ax, 0.2, yv0, 9.45, yv1 - yv0, '#f6f7f9', MUTED, lw=1.4)
    ax.text(0.35, yv1 - 0.1, 'Valorisation means adoption, not licensing', fontsize=12, fontweight='bold', color=INK, va='top')
    ax.text(0.35, yv1 - 0.45, 'no intellectual property to protect, and none created: workflows, benchmark, protocols,\n'
            'software and training material under open licences. One exception, data ownership: contributed\n'
            'records stay their owners\'; only derived series, metadata and results are published, never an archive.',
            fontsize=10.4, color=INK, va='top', linespacing=1.15)
    rbox(ax, 9.75, yv0, W - 0.2 - 9.75, yv1 - yv0, '#e6f5ee', GREEN, lw=1.6)
    ax.text(9.9, yv1 - 0.1, 'How we know it worked (Month 48)', fontsize=12, fontweight='bold', color=GREEN, va='top')
    ax.text(9.9, yv1 - 0.45, '≥ 5 institutions outside the network use\na protocol or the workflow; ≥ 10 national\nnetworks or operating rules reviewed',
            fontsize=10.4, color=INK, va='top', linespacing=1.15)

    # what is new
    rbox(ax, 0.2, 0.2, W - 0.4, 1.06, NAVY, NAVY, lw=0, r=0.1)
    ax.text(W / 2, 0.73, 'New: results travel as procedures, not only as papers, each issued with a worked example and timed to\n'
            'SWIM 2029 and the 2033 plans; the falsification test is published whichever way it falls.',
            ha='center', va='center', fontsize=11.6, color='white', linespacing=1.35)
    fig.savefig(os.path.join(OUT, 'figD1_dissemination.png'), dpi=220)
    plt.close(fig)
    print('ok')


if __name__ == '__main__':
    main()
