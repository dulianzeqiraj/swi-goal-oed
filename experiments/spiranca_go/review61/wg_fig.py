"""Organisation of the Action: four Working Groups, their exchanges, the management structure and the two additional roles.
Writes res/figW1_working_groups.png (large type)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'res')
INK, MUTED = '#1f2933', '#52606d'
plt.rcParams.update({'font.family': 'DejaVu Sans'})
COL = {'wg1': ('#fff4e0', '#c27c12'), 'wg2': ('#e8f1fb', '#2e6db4'), 'wg3': ('#e6f5ee', '#1e8a5a'), 'wg4': ('#f1ecfa', '#6a4fb3'),
       'mgmt': ('#eceff3', '#52606d'), 'role': ('#fdecec', '#b03a3a'), 'out': ('#ffffff', '#1f2933'), 'inst': ('#f7f7f2', '#7b6f4a')}
FB, FT = 12.0, 13.5


def box(ax, x, y, w, h, title, body='', kind='wg1', fs=FB, tfs=FT, lw=1.8, ls='-'):
    fc, ec = COL[kind]
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0.02,rounding_size=0.12', fc=fc, ec=ec, lw=lw, ls=ls, zorder=2))
    if body:
        ax.text(x, y + h / 2 - 0.12, title, ha='center', va='top', fontsize=tfs, fontweight='bold', color=ec, zorder=3, linespacing=1.2)
        ax.text(x, y - 0.18, body, ha='center', va='center', fontsize=fs, color=INK, zorder=3, linespacing=1.35)
    else:
        ax.text(x, y, title, ha='center', va='center', fontsize=fs, color=INK, zorder=3, linespacing=1.3)


def arrow(ax, pts, color=MUTED, lw=1.9, label=None, lpos=None, ha='center', va='center', fs=11, style='-|>', ls='-'):
    for (x0, y0), (x1, y1) in zip(pts[:-2], pts[1:-1]):
        ax.plot([x0, x1], [y0, y1], color=color, lw=lw, zorder=1, ls=ls, solid_capstyle='round')
    ax.annotate('', xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle=style, color=color, lw=lw, mutation_scale=17, ls=ls), zorder=1)
    if label:
        ax.text(*lpos, label, fontsize=fs, color=color, ha=ha, va=va, zorder=4, linespacing=1.25,
                bbox=dict(fc='white', ec='none', pad=1.0, alpha=0.95))


def main():
    W, H = 14.6, 9.6
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')

    # management band (mandatory structure)
    fc, ec = COL['mgmt']
    ax.add_patch(FancyBboxPatch((0.15, 7.85), W - 0.3, 1.6, boxstyle='round,pad=0.02,rounding_size=0.14', fc='#f6f7f9', ec=ec, lw=1.4, zorder=0))
    ax.text(W / 2, 9.22, 'Management (mandatory structure)', ha='center', va='center', fontsize=FT, fontweight='bold', color=ec)
    roles = ['Management\nCommittee', 'Action Chair\nand Vice Chair', 'Working Group\nLeaders (WG1–WG4)', 'Science Communication\nCoordinator', 'Grant Awarding\nCoordinator']
    bw, gap = 2.6, 0.18
    x0 = (W - (5 * bw + 4 * gap)) / 2 + bw / 2
    for k, t in enumerate(roles):
        box(ax, x0 + k * (bw + gap), 8.45, bw, 0.95, t, kind='mgmt', fs=11.5, lw=1.4)

    # working groups
    box(ax, 1.95, 4.45, 3.4, 2.75, 'WG1  Quantities of\ninterest and common\ndefinitions',
        'saline-front position and\nadvance rate; chloride at\nabstraction points; confidence\nof a status class\nfront-loaded: years 1–2', kind='wg1', fs=11.2, tfs=12.5)
    box(ax, 6.35, 6.15, 3.7, 2.0, 'WG2  Siting methodology\nand benchmark',
        'both method families as workflows,\nrun independently on common aquifers\nanalytical core; most STSMs', kind='wg2', fs=11.2, tfs=12.5)
    box(ax, 6.35, 2.65, 3.7, 2.0, 'WG3  Status reporting\nprotocol',
        'legal judgement → written procedure;\ntwo-team falsification test\nmostly water agencies and\nriver basin authorities', kind='wg3', fs=11.2, tfs=12.5)
    box(ax, 10.6, 4.45, 3.3, 2.75, 'WG4  Data, standards\nand exchange',
        'benchmark series in existing\nformats, on each institution\'s\nterms; application profile;\nmetadata that make a series\nreadable abroad', kind='wg4', fs=11.2, tfs=12.5)
    box(ax, 13.45, 4.45, 2.0, 2.75, 'Publishable\noutputs', 'benchmark\nseries\n\napplication\nprofile\n\nmetadata', kind='out', fs=11.2, tfs=12.5, lw=1.4)

    # additional roles
    box(ax, 10.6, 6.75, 3.3, 1.25, 'Benchmark Referee', 'assigns sites to method teams;\nreleases data blind to the\nother team\'s assignment', kind='role', fs=10.8, tfs=12.5)
    box(ax, 10.6, 2.05, 3.3, 1.25, 'Data Steward', 'release terms per institution;\npublishes derived series and\nmetadata, not national archives', kind='role', fs=10.8, tfs=12.5)
    box(ax, 10.6, 0.6, 3.3, 0.8, 'Contributing institutions\n(surveys, agencies, record holders)', kind='inst', fs=11)

    # exchanges
    c1, c2, c3, c4 = COL['wg1'][1], COL['wg2'][1], COL['wg3'][1], COL['wg4'][1]
    arrow(ax, [(3.65, 5.25), (4.05, 5.25), (4.05, 6.15), (4.5, 6.15)], color=c1)
    arrow(ax, [(3.65, 3.65), (4.05, 3.65), (4.05, 2.65), (4.5, 2.65)], color=c1)
    ax.text(4.12, 4.45, 'definitions', rotation=90, ha='center', va='center', fontsize=11, color=c1)
    arrow(ax, [(5.55, 5.15), (5.55, 3.65)], color=c2, label='evidence\nfor status\njudgements', lpos=(5.47, 4.4), ha='right', fs=10.5)
    arrow(ax, [(7.15, 3.65), (7.15, 5.15)], color=c3, label='the decision\nthe design\nserves', lpos=(7.25, 4.4), ha='left', fs=10.5)
    ax.add_patch(FancyBboxPatch((5.75, 3.98), 1.2, 0.84, boxstyle='round,pad=0.02,rounding_size=0.1', fc='#ffffff', ec=MUTED, lw=1.2, ls='--', zorder=2))
    ax.text(6.35, 4.4, 'joint session\nat each\nannual meeting', ha='center', va='center', fontsize=9.2, color=MUTED, zorder=3, linespacing=1.15)
    arrow(ax, [(8.2, 5.55), (8.6, 5.55), (8.6, 5.0), (8.95, 5.0)], color=c2)
    arrow(ax, [(8.2, 3.25), (8.6, 3.25), (8.6, 3.9), (8.95, 3.9)], color=c3)
    arrow(ax, [(12.25, 4.45), (12.45, 4.45)], color=c4)
    arrow(ax, [(8.95, 6.75), (8.2, 6.75)], color=COL['role'][1])
    arrow(ax, [(10.6, 2.675), (10.6, 3.075)], color=COL['role'][1], style='<|-|>')
    arrow(ax, [(10.6, 1.0), (10.6, 1.425)], color=COL['inst'][1], label='records', lpos=(10.7, 1.2), ha='left', fs=10.5)
    # legend
    ax.add_patch(FancyBboxPatch((0.35, 0.95), 0.45, 0.32, boxstyle='round,pad=0.02,rounding_size=0.06', fc=COL['role'][0], ec=COL['role'][1], lw=1.6))
    ax.text(0.95, 1.11, 'additional roles, beyond the\nmandatory structure', fontsize=11, color=INK, va='center', linespacing=1.2)
    ax.add_patch(FancyBboxPatch((0.35, 0.3), 0.45, 0.32, boxstyle='round,pad=0.02,rounding_size=0.06', fc='white', ec=MUTED, lw=1.2, ls='--'))
    ax.text(0.95, 0.46, 'joint WG2–WG3 session at\neach annual meeting', fontsize=11, color=INK, va='center', linespacing=1.2)
    fig.savefig(os.path.join(OUT, 'figW1_working_groups.png'), dpi=220)
    plt.close(fig)
    print('ok')


if __name__ == '__main__':
    main()
