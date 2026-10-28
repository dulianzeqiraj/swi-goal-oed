"""Main challenge of the Action, relevant and timely: pressure, four separate decisions, consequences, why now, main aim.
Writes res/figM1_main_challenge.png (large type). Dates and legal references as stated in the HALOMAR annex, section 1.A."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED = '#1f2933', '#52606d'
plt.rcParams.update({'font.family': 'DejaVu Sans'})
COL = {'press': ('#fdecec', '#b03a3a'), 'dec': ('#e8f1fb', '#2e6db4'), 'cons': ('#fff4e0', '#c27c12'), 'now': ('#e6f5ee', '#1e8a5a'),
       'sci': ('#f1ecfa', '#6a4fb3'), 'aim': ('#1f3864', '#1f3864'), 'band': ('#f6f7f9', '#9aa5b1')}
FB, FT = 12.0, 13.5


def panel(ax, x0, y0, w, h, title, kind):
    fc, ec = COL[kind]
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle='round,pad=0.02,rounding_size=0.14', fc=fc, ec=ec, lw=1.8, zorder=1))
    ax.text(x0 + w / 2, y0 + h - 0.14, title, ha='center', va='top', fontsize=FT, fontweight='bold', color=ec, zorder=3)


def bullets(ax, x, y, lines, fs=FB, dy=0.5, color=INK):
    for k, t in enumerate(lines):
        ax.text(x, y - k * dy, '•', fontsize=fs, color=color, va='top', zorder=3)
        ax.text(x + 0.22, y - k * dy, t, fontsize=fs, color=color, va='top', zorder=3, linespacing=1.25)


def arrow(ax, p0, p1, color=MUTED, lw=2.2):
    ax.annotate('', xy=p1, xytext=p0, arrowprops=dict(arrowstyle='-|>', color=color, lw=lw, mutation_scale=20), zorder=2)


def main():
    W, H = 14.6, 10.2
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    ax.text(W / 2, 9.9, 'Main challenge: why it is relevant, and why now', ha='center', va='center', fontsize=16, fontweight='bold', color=INK)

    # row 1: pressure -> four separate decisions -> consequences
    y0, h = 6.0, 3.5
    panel(ax, 0.2, y0, 4.3, h, 'Pressure on coastal aquifers', 'press')
    bullets(ax, 0.42, y0 + h - 0.7, ['Mediterranean, Adriatic, Black Sea\nand Atlantic aquifers supply drinking\nwater and irrigation',
                                       'saline intrusion: abstraction, rising\nsea level, longer droughts',
                                       'not reversible within a planning\ncycle: prevention, not recovery'], dy=0.98, fs=11.5)
    panel(ax, 5.05, y0, 4.5, h, 'Four decisions, taken separately', 'dec')
    for (xx, yy, t) in ((6.15, 8.25, 'Where to\nobserve'), (8.45, 8.25, 'How to read\nthe chemistry'), (6.15, 7.15, 'Where and how\nto recharge'), (8.45, 7.15, 'How much\nto pump')):
        ax.add_patch(FancyBboxPatch((xx - 1.0, yy - 0.42), 2.0, 0.84, boxstyle='round,pad=0.02,rounding_size=0.1', fc='white', ec='#2e6db4', lw=1.5, zorder=2))
        ax.text(xx, yy, t, ha='center', va='center', fontsize=11.5, color=INK, zorder=3, linespacing=1.2)
    ax.text(7.3, 6.35, 'different institutions, different implicit\ngoals; no stated value of an observation,\na recharge site or a pumping rule',
            ha='center', va='center', fontsize=10.8, color='#2e6db4', linespacing=1.25)
    panel(ax, 10.1, y0, 4.3, h, 'Consequences', 'cons')
    bullets(ax, 10.32, y0 + h - 0.7, ['monitoring sited for convenience\ncannot see the saline front',
                                        'recharge cannot be shown to work',
                                        'pumping rules learned from records,\nwith no stated record length;\nrecords can mislead',
                                        'status is a legal judgement, not a\nthreshold: "undetermined" or\nclassified differently'], dy=0.68, fs=11)
    arrow(ax, (4.55, 7.75), (5.0, 7.75)); arrow(ax, (9.6, 7.75), (10.05, 7.75))

    # row 2: science ready but untested + why now (timeline)
    y1, h1 = 2.3, 3.45
    panel(ax, 0.2, y1, 4.3, h1, 'Science is ready, but untested', 'sci')
    bullets(ax, 0.42, y1 + h1 - 0.7, ['computable rules for each of the four\ndecisions, proved and checked at\none alluvial aquifer',
                                        'whether they hold in karst, alluvial\nand deltaic systems is open: no\nsingle site can answer'], dy=1.12, fs=11.2)
    panel(ax, 5.05, y1, 9.35, h1, 'Why now: the legal calendar', 'now')
    X = lambda yr: 5.75 + (yr - 2026) * 1.08
    ya = 3.85
    ax.plot([X(2025.85), X(2033.45)], [ya, ya], color=INK, lw=2, zorder=2)
    for yr in range(2026, 2034):
        ax.plot([X(yr), X(yr)], [ya - 0.07, ya + 0.07], color=INK, lw=1.5, zorder=2)
        ax.text(X(yr), ya - 0.16, str(yr), ha='center', va='top', fontsize=11, color=MUTED)
    # the Action (four years from the end of 2027)
    ax.add_patch(FancyBboxPatch((X(2027.95), 3.05), X(2031.95) - X(2027.95), 0.32, boxstyle='round,pad=0.01,rounding_size=0.08', fc='#1e8a5a', ec='none', zorder=2))
    ax.text((X(2027.95) + X(2031.95)) / 2, 3.21, 'the Action, four years', ha='center', va='center', fontsize=11, color='white', fontweight='bold', zorder=3)
    events = [(2026.25, 4.75, 'Mar 2026: Directive (EU) 2026/805\nreplaces Annex V 2.3.2; keeps the\nintrusion condition and conductivity', 'left'),
              (2027.97, 4.1, 'Dec 2027: transposition due', 'center'),
              (2031.0, 4.75, '2031: review of the\ncharacterisation of\ngroundwater bodies', 'center'),
              (2033.0, 4.1, '2033: first river basin\nmanagement plans under\nthe amended text', 'right')]
    for yr, top, t, ha in events:
        ax.plot([X(yr)], [ya], 'o', ms=9, color='#1e8a5a', mec='white', mew=1.5, zorder=4)
        ax.plot([X(yr), X(yr)], [ya + 0.08, top - 0.03], color='#1e8a5a', lw=1.3, zorder=1)
        xt = X(yr) - 0.05 if ha == 'left' else (X(yr) + 0.05 if ha == 'right' else X(yr))
        ax.text(xt, top, t, ha=ha, va='bottom', fontsize=10.5, color=INK, linespacing=1.2, zorder=3)
    ax.text(9.72, 2.6, 'the status protocol is timed for the 2031 review and the 2033 plans',
            ha='center', va='center', fontsize=11, color='#1e8a5a', style='italic')

    # row 3: main aim
    fc, ec = COL['aim']
    ax.add_patch(FancyBboxPatch((0.2, 0.2), W - 0.4, 1.75, boxstyle='round,pad=0.02,rounding_size=0.14', fc=fc, ec=ec, lw=1.8, zorder=1))
    ax.text(W / 2, 1.58, 'Main aim', ha='center', va='center', fontsize=FT, fontweight='bold', color='white')
    ax.text(W / 2, 0.9, 'a common, mathematically grounded and field-tested basis for the four decisions,\n'
            'and a status test for saline intrusion that two authorities applying it independently will agree on',
            ha='center', va='center', fontsize=12.5, color='white', linespacing=1.35)
    arrow(ax, (2.35, 2.27), (2.35, 1.99)); arrow(ax, (9.72, 2.27), (9.72, 1.99))
    arrow(ax, (12.25, 5.98), (12.25, 5.78))
    fig.savefig(os.path.join(OUT, 'figM1_main_challenge.png'), dpi=220)
    plt.close(fig)
    print('ok')


if __name__ == '__main__':
    main()
