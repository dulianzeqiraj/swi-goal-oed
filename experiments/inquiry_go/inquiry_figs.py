"""Figure of the INQUIRY-GO proof of concept: share of the truths with a certified verdict against the number of
questions, for the six rules. fig_poc(workdir, R) -> path of the PNG."""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

from inquiry_text import POL, stats  # noqa: E402

FS = 8.5
plt.rcParams.update({'font.size': FS, 'axes.labelsize': FS, 'xtick.labelsize': FS, 'ytick.labelsize': FS,
                     'legend.fontsize': FS, 'font.family': 'DejaVu Sans', 'axes.spines.top': False,
                     'axes.spines.right': False})
# fixed order of the categorical hues (palette of hip_figs.py); the random rule is the neutral reference
# (order checked with the palette validator of the dataviz skill: all checks pass; the green is below 3:1 on the
# surface, relieved by the markers, the legend and the table of the note)
STYLE = {'INQUIRY': ('#2a78d6', 'o', '-'), 'hybrid': ('#eb6834', 's', '-'), 'goal variance': ('#1baf7a', '^', '-'),
         'widest outcome': ('#c43e8f', 'D', '-'), 'D-optimal': ('#6250d6', 'v', '-'), 'random': ('#7a8591', 'X', '--')}


def fig_poc(work, R):
    s = stats(R)
    n = s['N']
    fig, ax = plt.subplots(figsize=(6.3, 3.3), dpi=220)
    x = list(range(0, R['maxq'] + 1))
    for p in ['INQUIRY', 'hybrid', 'goal variance', 'widest outcome', 'D-optimal', 'random']:
        col, mk, ls = STYLE[p]
        ax.plot(x, [0.0] + [100.0 * c / n for c in s[p]['cum']], ls, color=col, marker=mk, ms=5.5, lw=2.0,
                mec='white', mew=0.9, label=p, clip_on=False, zorder=3)
    ax.set_xlim(0, R['maxq']); ax.set_ylim(0, 100)
    ax.set_xlabel('questions asked'); ax.set_ylabel(f'truths with a certified verdict (% of {n})')
    ax.grid(axis='y', color='#e3e7ec', lw=0.7); ax.set_axisbelow(True)
    ax.tick_params(length=3, color='#9aa4af')
    for sp in ('left', 'bottom'):
        ax.spines[sp].set_color('#9aa4af')
    ax.legend(frameon=False, loc='center left', bbox_to_anchor=(1.01, 0.5), handlelength=2.4)
    fig.tight_layout()
    out = os.path.join(work, 'fig_poc.png')
    fig.savefig(out)
    plt.close(fig)
    return out
