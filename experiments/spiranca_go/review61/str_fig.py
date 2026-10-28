"""Implementation, 3.A Action structure: management (mandatory and created roles), five Working Groups with tasks,
deliverables and months, the interfaces between them, inclusive leadership and internal communication.
Content from the HALOMAR annex, sections 3.A, 3.B and 3.C. Writes res/figT1_structure.png (large type)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED, NAVY, RED = '#1f2933', '#52606d', '#1f3864', '#b03a3a'
plt.rcParams.update({'font.family': 'DejaVu Sans'})
C1, C2, C3, C4, C5 = '#c27c12', '#2e6db4', '#1e8a5a', '#b03a3a', '#52606d'
F1, F2, F3, F4, F5 = '#fff4e0', '#e8f1fb', '#e6f5ee', '#fdecec', '#eceff3'


def rbox(ax, x0, y0, w, h, fc, ec, lw=1.4, r=0.08, z=1, ls='-'):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle=f'round,pad=0.012,rounding_size={r}', fc=fc, ec=ec, lw=lw, zorder=z, ls=ls))


def arrow(ax, p0, p1, color=MUTED, lw=2.0, style='-|>'):
    ax.annotate('', xy=p1, xytext=p0, arrowprops=dict(arrowstyle=style, color=color, lw=lw, mutation_scale=16), zorder=4)


def chip(ax, x, y, text, col, ha='right'):
    t = ax.text(x, y, text, ha=ha, va='center', fontsize=10.2, color='white', fontweight='bold', zorder=5,
                bbox=dict(boxstyle='round,pad=0.28,rounding_size=0.15', fc=col, ec='none'))
    return t


def main():
    W, H = 14.6, 11.0
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    ax.text(W / 2, 10.74, 'Action structure: five Working Groups, explicit interfaces, and roles that make the benchmark a test',
            ha='center', va='center', fontsize=15.5, fontweight='bold', color=INK)

    # ---------- management band ----------
    rbox(ax, 0.2, 9.0, W - 0.4, 1.45, '#f6f7f9', '#9aa5b1', lw=1.1, z=0)
    ax.text(0.35, 10.33, 'Management (mandatory)', fontsize=11.6, fontweight='bold', color=MUTED, va='top')
    mand = ['Management\nCommittee', 'Chair and\nVice Chair', 'WG Leaders\n(WG1–WG5)', 'Science\nCommunication\nCoordinator', 'Grant\nAwarding\nCoordinator']
    bw, gx = 1.2, 0.08
    for k, t in enumerate(mand):
        x0 = 0.32 + k * (bw + gx)
        rbox(ax, x0, 9.1, bw, 0.9, 'white', MUTED, lw=1.2, z=2)
        ax.text(x0 + bw / 2, 9.55, t, ha='center', va='center', fontsize=10, color=INK, linespacing=1.08, zorder=3)
    ax.text(6.87, 10.33, 'Created for this Action', fontsize=11.6, fontweight='bold', color=RED, va='top')
    extra = [('Benchmark Referee', 'outside both method teams;\nallocates sites, releases data\nblind, scores against D1 goals'),
             ('Data Steward', 'records the sharing terms\nper contributor; only derived\nseries and metadata published'),
             ('Stakeholder Advisory Panel', 'chaired from a water authority\nor utility; reviews every\ndeliverable in draft')]
    ew = 2.45
    for k, (t, b) in enumerate(extra):
        x0 = 6.85 + k * (ew + 0.06)
        rbox(ax, x0, 9.1, ew, 0.9, '#fdecec', RED, lw=1.3, z=2)
        ax.text(x0 + 0.08, 9.93, t, fontsize=10.4, fontweight='bold', color=RED, va='top', zorder=3)
        ax.text(x0 + 0.08, 9.7, b, fontsize=9.9, color=INK, va='top', linespacing=1.06, zorder=3)

    # ---------- WG1 (top, wide) ----------
    y10, y11 = 7.48, 8.86
    rbox(ax, 0.2, y10, W - 0.4, y11 - y10, F1, C1, lw=1.8, z=1)
    ax.text(0.35, y11 - 0.1, 'WG1  Goals, hydrochemical evidence and status', fontsize=12.3, fontweight='bold', color=C1, va='top')
    ax.text(6.55, y11 - 0.115, 'RC1, RC5', fontsize=11, fontweight='bold', color=C1, va='top')
    chip(ax, 14.25, y11 - 0.24, 'D1 M24 · D7 M42 · D10 M46', C1)
    cols1 = ['fixes what an observation is for:\nfront position and advance rate,\nchloride at abstraction points',
             'turns the chloride theorems into\na screening rule (D1) that WG2\napplies at every benchmark site',
             'writes the status protocol and runs\nthe two-team falsification test;\nagencies and authorities sit here']
    for k, t in enumerate(cols1):
        ax.text(0.35 + k * 4.75, y11 - 0.5, t, fontsize=10.8, color=INK, va='top', linespacing=1.12)

    # ---------- middle row: WG3, WG2, WG4 ----------
    ym0, ym1 = 4.38, 6.82
    mids = [(0.2, 4.3, C3, F3, 'WG3  Recharge', 'RC3', '',
             'agrees how recharge is formulated\nin the models used; what heads,\nchemistry and forcing identify;\nwhich source drives uncertainty;\nsites recharge with monitoring', 'D3 M36'),
            (5.25, 9.35, C2, F2, 'WG2  Observing the saline front', 'RC2', 'analytical core; most missions',
             'both siting families as workflows,\nrun independently on common sites;\nat each: structure threshold,\nscreening class, price of a\nchloride-only design, leak', 'D2 M30 · D4, D5 M36'),
            (10.3, 14.4, C4, F4, 'WG4  Pumping', 'RC4', '',
             'pumping records from utilities and\npublic bodies; years of records\neach well field needs; the test for\nmisleading records; what\noperators should log', 'D6 M40')]
    centres = []
    for x0, x1, col, fill, title, rc, note, body, dl in mids:
        rbox(ax, x0, ym0, x1 - x0, ym1 - ym0, fill, col, lw=1.8, z=1)
        ax.text(x0 + 0.12, ym1 - 0.1, title, fontsize=12, fontweight='bold', color=col, va='top', zorder=3)
        ax.text(x1 - 0.12, ym1 - 0.11, rc, fontsize=11, fontweight='bold', color=col, va='top', ha='right', zorder=3)
        if note:
            ax.text(x0 + 0.12, ym1 - 0.42, note, fontsize=10.2, color=col, va='top', style='italic', zorder=3)
        ax.text(x0 + 0.12, ym1 - (0.72 if note else 0.48), body, fontsize=11, color=INK, va='top', linespacing=1.14, zorder=3)
        chip(ax, x1 - 0.14, ym0 + 0.24, dl, col)
        centres.append((x0 + x1) / 2)

    # WG1 <-> each group
    for cx, col in zip(centres, (C3, C2, C4)):
        arrow(ax, (cx - 0.35, y10 - 0.02), (cx - 0.35, ym1 + 0.03), color=C1)
        arrow(ax, (cx + 0.35, ym1 + 0.03), (cx + 0.35, y10 - 0.02), color=col)
        ax.text(cx - 0.45, (y10 + ym1) / 2, 'goals', ha='right', va='center', fontsize=10.2, color=C1, fontweight='bold')
        ax.text(cx + 0.45, (y10 + ym1) / 2, 'evidence for status', ha='left', va='center', fontsize=10.2, color=col, fontweight='bold')
    # WG3 <-> WG2: one budget
    arrow(ax, (4.33, 5.6), (5.22, 5.6), color=INK, style='<|-|>')
    ax.text(4.775, 5.78, 'one\nbudget', ha='center', va='bottom', fontsize=10, color=INK, fontweight='bold', linespacing=1.05)
    ax.text(4.775, 5.42, 'well vs\nrecharge\nsite', ha='center', va='top', fontsize=9.8, color=MUTED, linespacing=1.05)
    # WG2 <-> WG4
    arrow(ax, (9.38, 6.0), (10.27, 6.0), color=C2)
    ax.text(9.825, 6.1, 'observation\ndesign', ha='center', va='bottom', fontsize=9.8, color=C2, linespacing=1.05)
    arrow(ax, (10.27, 5.2), (9.38, 5.2), color=C4)
    ax.text(9.825, 5.1, 'records\nto keep', ha='center', va='top', fontsize=9.8, color=C4, linespacing=1.05)

    # ---------- WG5 (foundation) ----------
    y50, y51 = 2.96, 3.98
    rbox(ax, 0.2, y50, W - 0.4, y51 - y50, F5, C5, lw=1.8, z=1)
    ax.text(0.35, y51 - 0.1, 'WG5  Data, software and transfer', fontsize=12.3, fontweight='bold', color=C5, va='top')
    ax.text(4.95, y51 - 0.115, 'RC5 data side; CB1–CB5', fontsize=11, fontweight='bold', color=C5, va='top')
    chip(ax, 14.25, y51 - 0.24, 'D4 M36 · D9 M40 · D8 M44 · D11', C5)
    ax.text(0.35, y51 - 0.5, 'benchmark series in existing formats on each contributor\'s terms; application profile; minimal open workflow\n'
            'assembled from code members already maintain; Training Schools and mission calls, for every group',
            fontsize=10.8, color=INK, va='top', linespacing=1.12)
    for cx in centres:
        arrow(ax, (cx, y51 + 0.02), (cx, ym0 - 0.03), color=C5)

    # ---------- leadership + internal communication ----------
    yb0, yb1 = 1.36, 2.82
    rbox(ax, 0.2, yb0, 6.95, yb1 - yb0, '#e6f5ee', '#1e8a5a', lw=1.5)
    ax.text(0.35, yb1 - 0.1, 'Leadership inclusive by rule', fontsize=11.8, fontweight='bold', color='#1e8a5a', va='top')
    ax.text(0.35, yb1 - 0.45, '≥ half of WG leader and vice-leader posts from ITC\n≥ a third young researchers and innovators;  ≥ 40% women\n'
            'mobility and Virtual Mobility Grants: priority to ITC\nand early-career participants',
            fontsize=10.8, color=INK, va='top', linespacing=1.15)
    rbox(ax, 7.25, yb0, W - 0.2 - 7.25, yb1 - yb0, '#e8f1fb', '#2e6db4', lw=1.5)
    ax.text(7.4, yb1 - 0.1, 'Internal communication and rhythm', fontsize=11.8, fontweight='bold', color='#2e6db4', va='top')
    ax.text(7.4, yb1 - 0.45, 'annual Management Committee and joint WG meetings,\nwith a WG1 session with every other group\n'
            'each WG meets twice a year at participating sites in turn\nmission calls twice a year; annual open seminar with the Panel',
            fontsize=10.8, color=INK, va='top', linespacing=1.15)

    # ---------- what is new ----------
    rbox(ax, 0.2, 0.2, W - 0.4, 1.05, NAVY, NAVY, lw=0, r=0.1)
    ax.text(W / 2, 0.725, 'New in the structure: a Benchmark Referee outside both method teams makes the comparison a test, not a\n'
            'demonstration; WG1 meets every group each year, so the methods and the status protocol cannot drift apart.',
            ha='center', va='center', fontsize=11.6, color='white', linespacing=1.35)
    fig.savefig(os.path.join(OUT, 'figT1_structure.png'), dpi=220)
    plt.close(fig)
    print('ok')


if __name__ == '__main__':
    main()
