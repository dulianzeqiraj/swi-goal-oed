"""Work plan (tasks, activities and timeframe): Working Groups x Years 1-4 with tasks and deliverables, milestones M1-M4,
networking tools, and risks with contingency. Content from the HALOMAR annex, sections 3.B and 3.C (and 1.E for the
Month 12 recruitment). Writes res/figP1_workplan.png (large type)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED, NAVY, RED, GREEN = '#1f2933', '#52606d', '#1f3864', '#b03a3a', '#1e8a5a'
plt.rcParams.update({'font.family': 'DejaVu Sans'})


def rbox(ax, x0, y0, w, h, fc, ec, lw=1.1, r=0.07, z=1):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle=f'round,pad=0.01,rounding_size={r}', fc=fc, ec=ec, lw=lw, zorder=z))


ROWS = [
    ('WG1  Goals,\nchemistry, status', '#c27c12', '#fff4e0', [
        'drafts the quantities of interest;\ncirculates them for objection,\nnot approval',
        'consensus statement and chloride\nscreening rule published (D1);\nbegins the status protocol',
        'completes the draft protocol;\ntwo-team falsification test\non ≥ 2 coastal bodies',
        'protocol revised after the test,\nissued with a worked example\n(D7); policy brief (D10)']),
    ('WG2  Observing\nthe front', '#2e6db4', '#e8f1fb', [
        'documents both siting families\nas workflows: data needs and\nfailure modes',
        'selects sites by contrast; the\nReferee allocates them; independent\napplication, with missions',
        'benchmark completed (D4, D5):\nthresholds, screening class,\ncertificates; protocol D2 (M30)',
        'benchmark and comparison at the\nIAH Congress and the next\nintrusion meeting']),
    ('WG3  Recharge', GREEN, '#e6f5ee', [
        'surveys how recharge is\nformulated in the models\nin use',
        'what each site\'s data constrain\nabout recharge and clay-layer\nmemory',
        'joint siting of recharge and\nmonitoring at sites with, or\nplanning, a scheme (D3)',
        'joint siting comparison\npresented at the IAH Congress']),
    ('WG4  Pumping', RED, '#fdecec', [
        'asks utilities and public bodies\nwhich records exist and how\npumping is decided',
        'compares the years of records\nneeded at the first well fields',
        'test for misleading records on\nrecorded pumping changes; plans\nvariations with willing utilities',
        'guidance on learning pumping\nrules from records finalised\n(D6, M40)']),
    ('WG5  Data,\nsoftware, transfer', '#52606d', '#eceff3', [
        'inventory of holdings and release\nconditions; data-sharing terms;\nTraining School 1',
        'mission calls; laboratory missions\nfor exchange-capacity\nmeasurements',
        'benchmark dataset deposited\n(D4); Training School 2 at an\noperating recharge scheme',
        'open workflow (D9), application\nprofile (D8); Training School 3\nfor authority and utility staff']),
    ('Network-wide', NAVY, '#e9edf5', [
        'recruit ≥ 3 maths groups and\n≥ 2 utilities by Month 12;\nrecharge schemes at ISMAR 2028',
        'inventory and first cross-site\ntests: own session at the 2029\nintrusion meeting',
        'falsification test executed;\noutcome recorded whichever\nway it falls',
        'closing capacity assessment\nagainst the Year 1 baseline\n(D13, M48)']),
]
MILES = [('M1', 'Month 12', 'inventory complete, workflows\nspecified, first sharing terms'),
         ('M2', 'Month 24', 'consensus statement published;\nbenchmark under way at all sites'),
         ('M3', 'Month 36', 'benchmark published, report\nissued; falsification test run'),
         ('M4', 'Month 48', 'D6–D10 issued; capacity\nre-measured against Year 1')]
RISKS = [('Records are not released', 'medium', 'high',
          'derived series, not archives;\nagreements held by the Data\nSteward; minimum six sites'),
         ('A result fails at some sites', 'medium', 'low',
          'an outcome, not a failure:\nreported with its measured\ndomain of validity'),
         ('Authorities participate weakly', 'high', 'high',
          'timed to the transposition\ntimetable; light asks; national\ndeliverables they need anyway'),
         ('Method capacity too thin', 'high', 'medium',
          '≥ 3 maths groups by Month 12;\nTraining Schools; missions;\na minimal version'),
         ('Utilities withhold records', 'high', 'medium',
          'aggregated records; recorded\nchanges; operator logs; models\ncalibrated to public data')]
LEVEL = {'low': '#1e8a5a', 'medium': '#c27c12', 'high': '#b03a3a'}


def main():
    W, H = 14.6, 11.0
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    ax.text(W / 2, 10.74, 'Work plan: tasks and activities by Working Group and year, four milestones, and named risks',
            ha='center', va='center', fontsize=15.5, fontweight='bold', color=INK)

    lx0, lx1 = 0.2, 2.0
    cx0, gap = 2.08, 0.07
    cw = (14.4 - cx0 - 3 * gap) / 4
    XS = [cx0 + k * (cw + gap) for k in range(4)]

    # year header (chevrons)
    yh0, yh1 = 9.98, 10.44
    ym = (yh0 + yh1) / 2
    shades = [('#c9daf2', INK), ('#8fb3e3', INK), ('#5b8fd0', 'white'), ('#2e5d9e', 'white')]
    for k, (fc, tc) in enumerate(shades):
        x0, x1 = XS[k], XS[k] + cw
        n = 0.0 if k == 0 else 0.13
        tip = 0.13 if k < 3 else 0.0
        pts = [(x0, yh0), (x1 - tip, yh0), (x1 + (0.0 if k == 3 else 0.0), ym), (x1 - tip, yh1), (x0, yh1), (x0 + n, ym)]
        ax.add_patch(Polygon(pts, closed=True, fc=fc, ec='white', lw=1.5, zorder=2))
        ax.text((x0 + x1) / 2, ym, f'Year {k + 1}   ·   Months {12 * k + 1}–{12 * k + 12}', ha='center', va='center',
                fontsize=11.2, fontweight='bold', color=tc, zorder=3)
    rbox(ax, lx0, yh0, lx1 - lx0, yh1 - yh0, '#eceff3', '#9aa5b1')
    ax.text((lx0 + lx1) / 2, ym, 'Who', ha='center', va='center', fontsize=11.2, fontweight='bold', color=INK)

    # grid
    rh, gy, top = 0.9, 0.05, 9.9
    for r, (lab, col, fill, cells) in enumerate(ROWS):
        y0 = top - (r + 1) * rh - r * gy
        rbox(ax, lx0, y0, lx1 - lx0, rh, col, col, lw=0)
        ax.text((lx0 + lx1) / 2, y0 + rh / 2, lab, ha='center', va='center', fontsize=10.6, fontweight='bold', color='white', linespacing=1.08)
        for k, t in enumerate(cells):
            rbox(ax, XS[k], y0, cw, rh, fill, col, lw=1.0)
            ax.text(XS[k] + 0.09, y0 + rh / 2, t, ha='left', va='center', fontsize=10.7, color=INK, linespacing=1.1, zorder=3)
    ybot = top - len(ROWS) * rh - (len(ROWS) - 1) * gy

    # milestones
    my0, my1 = 3.42, ybot - 0.08
    rbox(ax, lx0, my0, lx1 - lx0, my1 - my0, '#f2b134', '#f2b134', lw=0)
    ax.text((lx0 + lx1) / 2, (my0 + my1) / 2, 'Milestones', ha='center', va='center', fontsize=11, fontweight='bold', color=INK)
    for k, (m, mon, t) in enumerate(MILES):
        x0 = XS[k]
        rbox(ax, x0, my0, cw, my1 - my0, '#fff8e6', '#f2b134', lw=1.2)
        xd, yd = x0 + 0.3, (my0 + my1) / 2
        ax.add_patch(Polygon([(xd, yd + 0.27), (xd + 0.22, yd), (xd, yd - 0.27), (xd - 0.22, yd)], closed=True, fc='#f2b134', ec=INK, lw=0.9, zorder=3))
        ax.text(xd, yd, m, ha='center', va='center', fontsize=9.6, fontweight='bold', color=INK, zorder=4)
        ax.text(x0 + 0.62, my1 - 0.07, mon, fontsize=10.4, fontweight='bold', color=INK, va='top')
        ax.text(x0 + 0.62, my1 - 0.3, t, fontsize=10, color=INK, va='top', linespacing=1.08)

    # networking tools
    rbox(ax, 0.2, 2.9, W - 0.4, 0.42, '#e8f1fb', '#2e6db4', lw=1.2)
    ax.text(0.35, 3.11, 'Throughout:', fontsize=10.8, fontweight='bold', color='#2e6db4', va='center')
    ax.text(1.65, 3.11, 'annual MC and joint WG meetings · each WG meets twice a year at sites in turn · mission calls twice a year ·\n'
            'ITC conference grants · Virtual Mobility Grants · annual open seminar with the Stakeholder Advisory Panel',
            fontsize=10, color=INK, va='center', linespacing=1.1)

    # risks
    ry0, ry1 = 1.1, 2.8
    ax.text(0.22, ry1 - 0.02, 'Risks and contingency', fontsize=11.6, fontweight='bold', color=RED, va='top')
    rw = (W - 0.4 - 4 * 0.08) / 5
    for k, (t, lik, imp, cont) in enumerate(RISKS):
        x0 = 0.2 + k * (rw + 0.08)
        rbox(ax, x0, ry0, rw, ry1 - ry0 - 0.32, 'white', RED, lw=1.1)
        yt = ry1 - 0.42
        ax.text(x0 + 0.1, yt, t, fontsize=10.4, fontweight='bold', color=INK, va='top')
        for j, (lab, lv) in enumerate((('likelihood', lik), ('impact', imp))):
            yy = yt - 0.29 - j * 0.25
            ax.text(x0 + 0.1, yy, lab, fontsize=9.8, color=MUTED, va='top')
            ax.text(x0 + 0.95, yy, lv, fontsize=9.8, color='white', va='top', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.16', fc=LEVEL[lv], ec='none'))
        ax.text(x0 + 0.1, ry0 + 0.06, cont, fontsize=9.9, color=GREEN, va='bottom', linespacing=1.08)

    # what is new
    rbox(ax, 0.2, 0.2, W - 0.4, 0.82, NAVY, NAVY, lw=0, r=0.1)
    ax.text(W / 2, 0.61, 'New: the plan is built to be falsifiable. The two-team test runs in Year 3 and is recorded whichever way it falls;\n'
            'a result that fails at a site is reported with its measured domain of validity, and the procedures carry that domain.',
            ha='center', va='center', fontsize=11.2, color='white', linespacing=1.35)
    fig.savefig(os.path.join(OUT, 'figP1_workplan.png'), dpi=220)
    plt.close(fig)
    print('ok')


if __name__ == '__main__':
    main()
