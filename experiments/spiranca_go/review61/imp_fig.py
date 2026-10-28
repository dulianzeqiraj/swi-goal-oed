"""Impact related to objectives: five impact areas x three horizons, an indicator column (realistic),
and the three breakthrough outcomes (innovative). Content from the HALOMAR annex, sections 2.A and 3.C.
Writes res/figI1_impact.png (large type)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED, NAVY, GREEN = '#1f2933', '#52606d', '#1f3864', '#1e8a5a'
plt.rcParams.update({'font.family': 'DejaVu Sans'})


def rbox(ax, x0, y0, w, h, fc, ec, lw=1.4, r=0.08, z=1):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle=f'round,pad=0.012,rounding_size={r}', fc=fc, ec=ec, lw=lw, zorder=z))


# columns: label, short, medium, long, indicator
COLS = [(0.2, 2.3), (2.4, 5.3), (5.4, 8.3), (8.4, 11.3), (11.4, 14.4)]
HORIZONS = [('Short term\nduring the Action', '#c9daf2', INK), ('Medium term\nAction end, 2033 plans', '#5b8fd0', 'white'),
            ('Long term\nbeyond the Action', NAVY, 'white')]

ROWS = [
    ('Science', 'RC1–RC4', '#2e6db4', '#e8f1fb',
     'first cross-site distributions:\nstructure threshold, price of a\nchloride-only design, chemical\nleak, years of records (D5, M36)',
     'open benchmark (D4): later\nmethods measured on the same\naquifers; each result confirmed\nor its domain of validity measured',
     'coastal groundwater becomes a\ntesting ground where theorems\nmeet real records; draws maths\nand statistics into hydrogeology',
     '≥ 6 sites by M24, ≥ 8 by M36,\nin ≥ 3 settings; each result\ntested at ≥ 3 sites'),
    ('Technology\nand method', 'RC2–RC4', '#6a4fb3', '#f1ecfa',
     'both siting families as\nreproducible workflows, with\na minimal version (D2, M30)',
     'open minimal workflow (D9, M40):\nchloride screening, certified\nranking, years-of-records\ncalculator; no adjoint solver\nor geochemical model needed',
     'consultancies, which design\nmost networks, gain a stated\ncriterion they can apply\nand defend',
     '≥ 5 institutions outside the\nnetwork use a protocol or\nthe workflow'),
    ('Policy', 'RC5, RC1', GREEN, '#e6f5ee',
     'status protocol drafted with\nauthorities while the first\nassessments under amended\nAnnex V are prepared',
     'protocol (D7, M42) and policy\nbrief (D10, M46) enter the 2033\nplans: two authorities, same\nbody, same class',
     'Europe\'s published groundwater\nstatus figures mean the same\nthing everywhere, with no\nnew legal instrument',
     'two-team falsification test\non ≥ 2 bodies by M36; outcome\npublished either way'),
    ('Society and\neconomy', 'RC2–RC4', '#c27c12', '#fff4e0',
     'national networks and well-field\nrules reviewed against a stated\ncriterion, not convenience',
     'guidance on learning pumping\nrules from records (D6, M40):\nwhat operators should log',
     'well fields not lost; recharge\nschemes shown to work; drinking\nwater and irrigation kept for\ncoastal communities',
     '≥ 10 national networks or\noperating rules reviewed\nagainst the criterion'),
    ('Coordination\nand capacity', 'CB1–CB5', '#b03a3a', '#fdecec',
     'common vocabulary and quantities\nof interest (D1, M24); Training\nSchools; missions to ITC',
     'open training content (D11);\ncapacity re-measured against\nthe Year 1 baseline (D13, M48)',
     'early-career researchers carry\nthe methods home and stay\nlong after the Action ends',
     '≥ 10 countries run the workflow\nunaided; ≥ half of trainees\nfrom ITC; ≥ 40% women'),
]

BREAK = [('Chloride-only design at a known price', 'goal-oriented design for institutions\nthat will never run a geochemical model'),
         ('A certificate on well rankings', 'two teams, or two countries, tell real\ndisagreement from numerical noise'),
         ('Years of records, and a test for\nmisleading records', 'data-driven and AI operation of well\nfields auditable before it is trusted')]


def main():
    W, H = 14.6, 11.0
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    ax.text(W / 2, 10.72, 'Impact related to objectives: realistic, measured, and innovative', ha='center', va='center',
            fontsize=16, fontweight='bold', color=INK)

    # header row
    yh0, yh1 = 9.6, 10.32
    ym = (yh0 + yh1) / 2
    rbox(ax, COLS[0][0], yh0, COLS[0][1] - COLS[0][0], yh1 - yh0, '#eceff3', '#9aa5b1', lw=1.0)
    ax.text((COLS[0][0] + COLS[0][1]) / 2, ym, 'Impact area\n(objectives)', ha='center', va='center', fontsize=11.5, fontweight='bold', color=INK, linespacing=1.1)
    for k, (t, fc, tc) in enumerate(HORIZONS):
        x0, x1 = COLS[k + 1]
        n = 0.0 if k == 0 else 0.22
        pts = [(x0, yh0), (x1 - 0.06, yh0), (x1 + 0.16, ym), (x1 - 0.06, yh1), (x0, yh1), (x0 + n, ym)]
        ax.add_patch(Polygon(pts, closed=True, fc=fc, ec='white', lw=1.5, zorder=2))
        ax.text((x0 + x1) / 2 + 0.08, ym, t, ha='center', va='center', fontsize=11.5, fontweight='bold', color=tc, linespacing=1.1, zorder=3)
    x0, x1 = COLS[4]
    rbox(ax, x0 + 0.12, yh0, x1 - x0 - 0.12, yh1 - yh0, GREEN, GREEN, lw=0)
    ax.text((x0 + x1) / 2 + 0.06, ym, 'Realistic: indicator\n(by Month 48)', ha='center', va='center', fontsize=11.5, fontweight='bold', color='white', linespacing=1.1)

    # rows
    rh, gy, top = 1.2, 0.08, 9.48
    for r, (area, rc, col, fill, s, m, l, ind) in enumerate(ROWS):
        y0 = top - (r + 1) * rh - r * gy
        x0, x1 = COLS[0]
        rbox(ax, x0, y0, x1 - x0, rh, col, col, lw=0)
        ax.text((x0 + x1) / 2, y0 + rh / 2 + 0.17, area, ha='center', va='center', fontsize=12.2, fontweight='bold', color='white', linespacing=1.05)
        ax.text((x0 + x1) / 2, y0 + 0.2, rc, ha='center', va='center', fontsize=10.6, color='white', fontweight='bold')
        for k, txt in enumerate((s, m, l)):
            cx0, cx1 = COLS[k + 1]
            rbox(ax, cx0, y0, cx1 - cx0, rh, fill, col, lw=1.1)
            ax.text(cx0 + 0.1, y0 + rh / 2, txt, ha='left', va='center', fontsize=10.9, color=INK, linespacing=1.12, zorder=3)
        cx0, cx1 = COLS[4]
        rbox(ax, cx0 + 0.12, y0, cx1 - cx0 - 0.12, rh, 'white', GREEN, lw=1.3)
        ax.text(cx0 + 0.22, y0 + rh / 2, ind, ha='left', va='center', fontsize=10.9, color=INK, linespacing=1.12, zorder=3)

    # breakthrough band (innovative)
    yb0, yb1 = 1.38, 3.0
    rbox(ax, 0.2, yb0, W - 0.4, yb1 - yb0, '#f1ecfa', '#6a4fb3', lw=1.6)
    ax.text(0.4, yb1 - 0.12, 'Innovative: three outcomes that would change practice', fontsize=13, fontweight='bold', color='#6a4fb3', va='top')
    bw = (W - 0.4 - 0.4 - 0.2) / 3
    for k, (t, b) in enumerate(BREAK):
        x0 = 0.4 + k * (bw + 0.1)
        rbox(ax, x0, yb0 + 0.12, bw, 1.0, 'white', '#6a4fb3', lw=1.2, z=2)
        ax.text(x0 + 0.12, yb0 + 1.04, t, fontsize=11.2, fontweight='bold', color=INK, va='top', linespacing=1.08, zorder=3)
        ax.text(x0 + 0.12, yb0 + 0.2, b, fontsize=11, color=MUTED, va='bottom', linespacing=1.12, zorder=3)

    # bottom band
    rbox(ax, 0.2, 0.2, W - 0.4, 1.0, NAVY, NAVY, lw=0, r=0.1)
    ax.text(W / 2, 0.7, 'Realistic by design: every impact has an indicator measured by Month 48; no new law is needed;\n'
            'outputs come in the forms authorities already use; everything is open; a negative result is published too.',
            ha='center', va='center', fontsize=11.6, color='white', linespacing=1.35)
    fig.savefig(os.path.join(OUT, 'figI1_impact.png'), dpi=220)
    plt.close(fig)
    print('ok')


if __name__ == '__main__':
    main()
