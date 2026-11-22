"""Rationale for choosing networking: why a pan-European network is the instrument that fits the challenge and objectives.
Content from the HALOMAR annex, section 1.D. Writes res/figN1_networking.png (large type)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED = '#1f2933', '#52606d'
plt.rcParams.update({'font.family': 'DejaVu Sans'})


def rbox(ax, x0, y0, w, h, fc, ec, lw=1.6, r=0.1):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle=f'round,pad=0.015,rounding_size={r}', fc=fc, ec=ec, lw=lw, zorder=1))


def arrow(ax, p0, p1, color=MUTED, lw=2.4):
    ax.annotate('', xy=p1, xytext=p0, arrowprops=dict(arrowstyle='-|>', color=color, lw=lw, mutation_scale=20), zorder=2)


CARDS = [
    ('1', 'Results must travel', 'each result was proved at one\naquifer; testing it needs karst,\nalluvial and deltaic systems whose\nrecords national bodies hold',
     'common sites, data on agreed terms', 'RC2, RC3', '#2e6db4'),
    ('2', 'Thresholds are distributions', 'structure threshold, price of a\nchloride-only design, chemical leak,\nyears of records: modest at each\nsite, impossible at one',
     'cross-site benchmark', 'RC1–RC4', '#c27c12'),
    ('3', 'Comparability is social', 'status differs by procedure, depth,\nindicator and convention; those\nwho judge must meet, disagree\nand settle',
     'Working Groups, meetings', 'RC5', '#1e8a5a'),
    ('4', 'The timing is institutional', 'authorities revise how they assess\ncoastal groundwater during the\nAction: amended Annex V, the 2031\nreview, the 2033 plans',
     'authorities as members', 'RC5', '#6a4fb3'),
    ('5', 'Capacity must move', 'thinnest monitoring goes with\nthinnest capacity, mostly in ITC;\na project concentrates capability,\na network spreads it',
     'Training Schools, STSMs, grants', 'CB1, CB2, CB5', '#b03a3a'),
    ('6', 'Not all are researchers', 'surveys, agencies, basin authorities\nand utilities hold the records and\ndecide; they join a network on\nequal terms, rarely a research grant',
     'open membership, policy briefs', 'CB3, CB4', '#52606d'),
]


def main():
    W, H = 14.6, 10.5
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    ax.text(W / 2, 10.2, 'Why a pan-European network is the instrument that fits', ha='center', va='center', fontsize=16, fontweight='bold', color=INK)

    # top: what exists vs what is missing
    rbox(ax, 0.2, 8.05, 6.9, 1.75, '#eceff3', '#52606d')
    ax.text(0.4, 9.65, 'Research: largely done, or funded elsewhere', fontsize=12.5, fontweight='bold', color='#52606d', va='top')
    ax.text(0.4, 9.2, 'variable-density flow is mature, with community codes;\nexperimental design is an established field;\n'
            'managed recharge has an engineering standard;\nthe preparatory results are proved and tested numerically',
            fontsize=11, color=INK, va='top', linespacing=1.25)
    rbox(ax, 7.5, 8.05, 6.9, 1.75, '#fdecec', '#b03a3a')
    ax.text(7.7, 9.65, 'Missing: an arrangement between countries', fontsize=12.5, fontweight='bold', color='#b03a3a', va='top')
    ax.text(7.7, 9.2, 'to observe, interpret and manage intrusion against\ncommon goals, test the results on each other\'s\n'
            'aquifers and report the consequences comparably:\nclosed by agreement and exchange, not new knowledge',
            fontsize=11, color=INK, va='top', linespacing=1.25)
    arrow(ax, (3.65, 8.02), (3.65, 7.72)); arrow(ax, (10.95, 8.02), (10.95, 7.72))
    rbox(ax, 0.2, 7.2, W - 0.4, 0.5, '#1f3864', '#1f3864', r=0.08)
    ax.text(W / 2, 7.45, 'Six features of the challenge make a distributed network the only instrument that fits',
            ha='center', va='center', fontsize=12.5, color='white', fontweight='bold')

    # six cards
    cw, ch, gx, gy = 4.6, 2.38, 0.2, 0.15
    for k, (num, title, body, tool, obj, col) in enumerate(CARDS):
        r_, c_ = divmod(k, 3)
        x0 = 0.2 + c_ * (cw + gx)
        y0 = 7.05 - (r_ + 1) * ch - r_ * gy
        rbox(ax, x0, y0, cw, ch, 'white', col, lw=1.8)
        ax.add_patch(FancyBboxPatch((x0 + 0.12, y0 + ch - 0.52), 0.42, 0.4, boxstyle='round,pad=0.01,rounding_size=0.08', fc=col, ec='none', zorder=2))
        ax.text(x0 + 0.33, y0 + ch - 0.32, num, ha='center', va='center', fontsize=12, color='white', fontweight='bold', zorder=3)
        ax.text(x0 + 0.66, y0 + ch - 0.32, title, ha='left', va='center', fontsize=12.2, color=col, fontweight='bold', zorder=3)
        ax.text(x0 + 0.15, y0 + ch - 0.68, body, ha='left', va='top', fontsize=10.8, color=INK, linespacing=1.22, zorder=3)
        ax.add_patch(FancyBboxPatch((x0 + 0.1, y0 + 0.1), cw - 0.2, 0.36, boxstyle='round,pad=0.01,rounding_size=0.06', fc='#f6f7f9', ec='none', zorder=2))
        ax.text(x0 + 0.18, y0 + 0.28, 'COST tool: ' + tool, ha='left', va='center', fontsize=10, color=MUTED, zorder=3)
        ax.text(x0 + cw - 0.18, y0 + 0.28, obj, ha='right', va='center', fontsize=10.5, color=col, fontweight='bold', zorder=3)

    # bottom: who funds what
    yb, hb = 0.2, 1.75
    rbox(ax, 0.2, yb, 6.9, hb, '#e8f1fb', '#2e6db4')
    ax.text(0.4, yb + hb - 0.14, 'Members fund the research', fontsize=12.5, fontweight='bold', color='#2e6db4', va='top')
    ax.text(0.4, yb + hb - 0.58, 'modelling, benchmark computation, laboratory\nmeasurements, software and any change to operation,\n'
            'from their own national and European funding', fontsize=11, color=INK, va='top', linespacing=1.25)
    rbox(ax, 7.5, yb, 6.9, hb, '#e6f5ee', '#1e8a5a')
    ax.text(7.7, yb + hb - 0.14, 'COST funds the networking', fontsize=12.5, fontweight='bold', color='#1e8a5a', va='top')
    ax.text(7.7, yb + hb - 0.58, 'meetings, Short-Term Scientific Missions, Training\nSchools, conference grants and dissemination:\n'
            'what makes the members\' work comparable', fontsize=11, color=INK, va='top', linespacing=1.25)
    ax.text(W / 2, yb + hb / 2, '+', ha='center', va='center', fontsize=26, color=MUTED, fontweight='bold')
    fig.savefig(os.path.join(OUT, 'figN1_networking.png'), dpi=220)
    plt.close(fig)
    print('ok')


if __name__ == '__main__':
    main()
