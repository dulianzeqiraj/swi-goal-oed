"""Critical mass of the network: the eleven competences and how well each is held, the network today,
the three stated gaps with targets, and the rules that make membership meaningful.
Content from the HALOMAR annex, sections 1.E, 3.A and 3.B. Writes res/figC1_critical_mass.png (large type)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED, RED, NAVY = '#1f2933', '#52606d', '#b03a3a', '#1f3864'
plt.rcParams.update({'font.family': 'DejaVu Sans'})


def rbox(ax, x0, y0, w, h, fc, ec, lw=1.6, r=0.1, z=1):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle=f'round,pad=0.015,rounding_size={r}', fc=fc, ec=ec, lw=lw, zorder=z))


def dots(ax, x, y, level, col):
    for k in range(3):
        on = k < level
        ax.add_patch(Circle((x + k * 0.17, y), 0.058, fc=col if on else 'white', ec=col, lw=1.3, zorder=4))


# (group title, colour, fill, [(name, coverage level 1-3, objectives, growth note)])
GROUPS = [
    ('Physics, chemistry, method', '#2e6db4', '#e8f1fb', [
        ('Variable-density flow\nand transport modelling', 3, 'RC2–RC4', ''),
        ('Hydrogeochemistry\nof intrusion', 3, 'RC1, RC2', ''),
        ('Bayesian inversion, design,\nlearning from records', 3, 'RC2–RC4', '+3 maths groups'),
        ('Multi-criteria decision\nanalysis (rival family)', 3, 'RC2, RC3', '')]),
    ('The aquifers', '#c27c12', '#fff4e0', [
        ('Coastal karst\nhydrogeology', 2, 'RC2–RC4', ''),
        ('Alluvial and deltaic\nsystems', 2, 'RC2–RC4', ''),
        ('Geophysical imaging of\nthe fresh–saline interface', 2, 'RC2', '')]),
    ('Practice and custody', '#1e8a5a', '#e6f5ee', [
        ('Managed aquifer recharge\n(operating schemes)', 1, 'RC3', ''),
        ('Long-term monitoring\nrecords (geological surveys)', 1, 'RC2, RC5', ''),
        ('Well fields and pumping\nrecords (water utility)', 1, 'RC4', '+2 utilities'),
        ('Status classification\n(agencies, basin authorities)', 1, 'RC1, RC5', '')]),
]

METERS = [('from Inclusiveness Target Countries', 0.60, 'about 60%'),
          ('young researchers and innovators', 0.50, 'over 50%'),
          ('women', 0.40, 'close to 40%'),
          ('universities and research organisations', 0.90, 'about 90%')]

GAPS = [('Applied mathematics\nand statistics',
         'no proposer has it as core\nfield; the certificate and the\nyears-of-records rule need it',
         'invite from the first MC\nmeeting; Training Schools', '≥ 3 groups by Month 12'),
        ('Water utilities and\nprivate firms',
         'one utility is a proposer; no\nconsultancies or instrument\nmakers yet',
         'compare years of records\nacross well fields', '≥ 2 utilities in WG4 by\nMonth 12; firms in the SAP'),
        ('Operating recharge\nschemes',
         'scarce in Europe: cannot be\nenlarged by recruitment',
         'light hosting role; the\nanalysis is brought to them', 'recruited at the 2028\nrecharge symposium')]

ENGAGE = ['every institution has a defined role in a\nWorking Group deliverable: an obligation\nand a return, not a listing',
          'leadership by rule: ≥ half of WG leader\nposts from ITC, ≥ a third young\nresearchers, ≥ 40% women',
          'mobility grants give priority to ITC and\nearly-career participants',
          'record holders and authorities join as\nmembers; a Stakeholder Advisory Panel,\nchaired from an authority or utility,\nreviews every deliverable in draft']


def main():
    W, H = 14.6, 11.0
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    ax.text(W / 2, 10.72, 'Critical mass: eleven competences, 58 proposers, and a dated plan for the gaps',
            ha='center', va='center', fontsize=16, fontweight='bold', color=INK)

    # ---------- row 1, left: range of expertise ----------
    rbox(ax, 0.2, 5.55, 9.35, 4.85, '#f6f7f9', '#9aa5b1', lw=1.3, z=0)
    ax.text(0.38, 10.27, 'Range of expertise: the eleven competences the challenge needs',
            fontsize=13, fontweight='bold', color=INK, va='top')
    cw, gx, ch, gy = 2.95, 0.1, 0.82, 0.08
    for g, (gt, col, fill, items) in enumerate(GROUPS):
        x0 = 0.35 + g * (cw + gx)
        rbox(ax, x0, 9.5, cw, 0.36, col, col, lw=0, r=0.07, z=2)
        ax.text(x0 + cw / 2, 9.68, f'{gt} ({len(items)})', ha='center', va='center', fontsize=11.2, color='white', fontweight='bold', zorder=3)
        for k, (name, lvl, rc, grow) in enumerate(items):
            y0 = 9.4 - (k + 1) * ch - k * gy
            rbox(ax, x0, y0, cw, ch, fill, col, lw=1.3, r=0.07, z=2)
            ax.text(x0 + 0.1, y0 + ch - 0.07, name, ha='left', va='top', fontsize=10.6, color=INK, linespacing=1.12, zorder=3)
            dots(ax, x0 + 0.17, y0 + 0.13, lvl, col)
            if grow:
                ax.text(x0 + 0.66, y0 + 0.13, grow, ha='left', va='center', fontsize=9.8, color=RED, fontweight='bold', zorder=3)
            ax.text(x0 + cw - 0.1, y0 + 0.13, rc, ha='right', va='center', fontsize=10, color=col, fontweight='bold', zorder=3)
    # legend, in the empty slot under the aquifers
    lx0, ly0, lw_, lh = 0.35 + cw + gx, 5.68, cw, 1.02
    rbox(ax, lx0, ly0, lw_, lh, 'white', '#9aa5b1', lw=1.0, r=0.07, z=2)
    rows = [(3, 'several independent groups'), (2, 'present'), (1, 'few bodies: asks kept light'), (0, 'growth target by Month 12')]
    for k, (lvl, t) in enumerate(rows):
        yy = ly0 + lh - 0.15 - k * 0.24
        if lvl:
            dots(ax, lx0 + 0.17, yy, lvl, MUTED)
        else:
            ax.text(lx0 + 0.34, yy, '+', ha='center', va='center', fontsize=12, color=RED, fontweight='bold', zorder=4)
        ax.text(lx0 + 0.66, yy, t, fontsize=10, va='center', color=RED if lvl == 0 else INK, zorder=4)

    # ---------- row 1, right: the network today ----------
    xr, wr = 9.75, 4.65
    rbox(ax, xr, 5.55, wr, 4.85, 'white', NAVY, lw=1.6, z=0)
    ax.text(xr + 0.18, 10.27, 'The network today', fontsize=13, fontweight='bold', color=NAVY, va='top')
    ax.text(xr + 1.0, 9.42, '58', ha='center', va='center', fontsize=32, fontweight='bold', color=NAVY)
    ax.text(xr + 1.0, 8.92, 'proposers', ha='center', va='center', fontsize=11, color=INK)
    ax.text(xr + 3.25, 9.42, '> 20', ha='center', va='center', fontsize=32, fontweight='bold', color=NAVY)
    ax.text(xr + 3.25, 8.92, 'COST countries', ha='center', va='center', fontsize=11, color=INK)
    bx, bw = xr + 0.2, wr - 0.4
    for k, (lab, frac, val) in enumerate(METERS):
        yt = 8.42 - k * 0.56
        ax.text(bx, yt, lab, fontsize=10.6, color=INK, va='center')
        ax.add_patch(Rectangle((bx, yt - 0.29), bw, 0.15, fc='#e4e7eb', ec='none', zorder=1))
        ax.add_patch(Rectangle((bx, yt - 0.29), bw * frac, 0.15, fc='#2e6db4', ec='none', zorder=2))
        ax.text(bx + bw * frac + 0.06, yt - 0.215, val, fontsize=10.2, color=INK, va='center', ha='left', fontweight='bold', zorder=3) \
            if frac < 0.7 else ax.text(bx + bw * frac - 0.06, yt - 0.215, val, fontsize=10.2, color='white', va='center', ha='right', fontweight='bold', zorder=3)
    ax.text(bx, 6.12, 'the rest: governmental bodies and one water\nutility (pumping records, operators\' logs)',
            fontsize=10.2, color=MUTED, va='top', linespacing=1.18)

    # ---------- row 2, left: plan to grow ----------
    rbox(ax, 0.2, 1.3, 9.35, 4.05, '#fdf6f6', RED, lw=1.3, z=0)
    ax.text(0.38, 5.22, 'Plan to grow: three stated gaps, each with a target', fontsize=13, fontweight='bold', color=RED, va='top')
    for g, (title, now, act, tgt) in enumerate(GAPS):
        x0 = 0.35 + g * (cw + gx)
        y0, hc = 2.3, 2.5
        rbox(ax, x0, y0, cw, hc, 'white', RED, lw=1.3, r=0.07, z=2)
        ax.text(x0 + 0.1, y0 + hc - 0.08, title, ha='left', va='top', fontsize=11.2, color=RED, fontweight='bold', linespacing=1.1, zorder=3)
        ax.text(x0 + 0.1, y0 + hc - 0.6, now, ha='left', va='top', fontsize=10.2, color=INK, linespacing=1.15, zorder=3)
        ax.text(x0 + 0.1, y0 + 1.02, act, ha='left', va='bottom', fontsize=10.2, color='#1e8a5a', linespacing=1.15, zorder=3, style='italic')
        rbox(ax, x0 + 0.08, y0 + 0.08, cw - 0.16, 0.5, '#1e8a5a', '#1e8a5a', lw=0, r=0.06, z=3)
        ax.text(x0 + cw / 2, y0 + 0.33, tgt, ha='center', va='center', fontsize=10.4, color='white', fontweight='bold', linespacing=1.1, zorder=4)
    # recruitment rule strip
    rbox(ax, 0.35, 1.42, 9.05, 0.76, 'white', '#9aa5b1', lw=1.0, r=0.06, z=2)
    ax.text(0.47, 2.07, 'Recruited for contrast in hydrogeological setting, not convenience. First targets:',
            fontsize=10.6, fontweight='bold', color=INK, va='top', zorder=3)
    firsts = ['record holders with no\nresearch capacity', 'labs measuring exchange\ncapacity of fine sediments', 'utilities willing to share\npumping records']
    for k, t in enumerate(firsts):
        xx = 0.5 + k * 3.03
        ax.add_patch(Circle((xx + 0.13, 1.66), 0.13, fc=RED, ec='none', zorder=3))
        ax.text(xx + 0.13, 1.66, str(k + 1), ha='center', va='center', fontsize=10, color='white', fontweight='bold', zorder=4)
        ax.text(xx + 0.34, 1.66, t, ha='left', va='center', fontsize=10, color=INK, linespacing=1.08, zorder=3)

    # ---------- row 2, right: meaningful engagement ----------
    rbox(ax, xr, 1.3, wr, 4.05, '#e6f5ee', '#1e8a5a', lw=1.6, z=0)
    ax.text(xr + 0.18, 5.22, 'Meaningful engagement', fontsize=13, fontweight='bold', color='#1e8a5a', va='top')
    ys = [4.85, 4.0, 3.15, 2.5]
    for y, t in zip(ys, ENGAGE):
        ax.text(xr + 0.2, y, '•', fontsize=12, color='#1e8a5a', va='top', fontweight='bold')
        ax.text(xr + 0.42, y, t, fontsize=11, color=INK, va='top', linespacing=1.18)

    # ---------- bottom band: what is new ----------
    rbox(ax, 0.2, 0.2, W - 0.4, 0.92, NAVY, NAVY, lw=0, r=0.1, z=0)
    ax.text(W / 2, 0.66, 'New in how this network is built: assembled against the eleven competences, not availability; both rival siting\n'
            'families inside, so the benchmark is a test, not a demonstration; record holders and authorities are members with deliverables.',
            ha='center', va='center', fontsize=11.3, color='white', linespacing=1.35)
    fig.savefig(os.path.join(OUT, 'figC1_critical_mass.png'), dpi=220)
    plt.close(fig)
    print('ok')


if __name__ == '__main__':
    main()
