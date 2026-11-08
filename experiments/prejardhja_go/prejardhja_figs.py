"""Figures of State of the art V (PREJARDHJA-GO); English labels, every text at least 8.6 pt at the printed size.
usage: python prejardhja_figs.py OUT_DIR

fig_method    the method in one picture: four stories, tracer tests, plausible-source set, robust allocation, stakeholders
fig_wrong     P0: probability that the blend exceeds 250 mg/L when one acts on the wrong story
fig_policies  P1: exceedance for each true source and expected cost of seven policies
fig_tests     P2: decision value against information gain of the 16 test bundles (two aquifer geometries)
fig_monitor   P4: anytime-valid monthly monitoring against repeated ordinary tests
fig_stress    P5: mixtures of sources, drifted tracer signatures, more campaigns
fig_ledger    P3: who pays for not knowing the source; the price of safety
fig_map       the thirty papers against the components C1-C5
Numbers come from res/prejardhja.json."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', 'rindertimi_go'))
import gar_figs as GF  # noqa: E402
from rgo_figs import Canvas, INK, MUTED  # noqa: E402

RES = os.path.join(HERE, 'res')
MM, FS = GF.MM, GF.FS
BLUE, ORANGE, AQUA, VIOLET, REF = GF.BLUE, GF.ORANGE, GF.AQUA, GF.VIOLET, GF.REF
GREEN, GREEN_L = '#1E6B35', '#E6F4EA'
SRC_COL = dict(SWI=BLUE, UP=VIOLET, DRY=ORANGE, ANT=AQUA)
SRC_LAB = dict(SWI='SWI  seawater intrusion', UP='UP  upconing', DRY='DRY  drought', ANT='ANT  return flow')
INST = dict(Oxford=BLUE, Caltech=ORANGE, Harvard=AQUA, MIT=VIOLET)
POL = [('oracle', 'oracle\n(source known)'), ('assume_swi', 'assume\nseawater'), ('bayes_prior', 'Bayes,\nprior only'),
       ('worst', 'worst case\n(no tests)'), ('map', 'most probable\nsource'), ('bayes_post', 'Bayes\nposterior'),
       ('prejardhja', 'PREJARDHJA\n-GO')]


def load():
    with open(os.path.join(RES, 'prejardhja.json')) as fh:
        return json.load(fh)


def save(fig, out, name):
    fig.savefig(os.path.join(out, f'fig_{name}.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ the method
def fig_method(out):
    cv = Canvas(170, 92)
    w, gap, y0, h = 39.4, 3.4, 41.0, 49.0
    xs = [1.0 + i * (w + gap) for i in range(4)]
    boxes = [
        ('Four stories', '#eef2f7', INK, '#5b6672',
         [('SWI', 'sea enters at A'), ('UP', 'brine rises at C'), ('DRY', 'drought: A and B'), ('ANT', 'return flow at B')],
         'all four fit\ntoday\'s chloride'),
        ('Tracer tests  (C3)', '#fff4e5', '#a66f00', '#c48a00',
         [('T1', 'Br/Cl ratio'), ('T2', 'water isotopes'), ('T3', 'depth profiles'), ('T4', 'nitrate, boron')],
         'bought for their\ndecision value'),
        ('Plausible set  (C1)', '#e8f0fb', BLUE, BLUE,
         [('', r'$E_k=\frac{1}{K-1}\sum_{j\neq k}\frac{p_j(y)}{p_k(y)}$'), ('', r'keep $k$ while $E_k<1/\beta$'),
          ('', r'$P(\mathrm{true}\in S)\geq 1-\beta$')], 'no prior,\nnever empty'),
        ('Robust allocation  (C2)', '#e8f0fb', BLUE, BLUE,
         [('', 'least social cost with'), ('', r'$P_k(\mathrm{blend}>250)\leq\alpha$'), ('', r'for every $k\in S(y)$'),
          ('', r'$\Rightarrow$ risk $\leq\alpha+\beta$')], 'whatever the\nsource is'),
    ]
    tagcol = dict(SWI=BLUE, UP=VIOLET, DRY=ORANGE, ANT=AQUA)
    for (title, fc, tc, ec, lines, foot), x in zip(boxes, xs):
        cv.box(x, y0, w, h, fc, ec, lw=1.0)
        cv.text(x + w / 2, y0 + h - 4.5, title, weight='bold', color=tc)
        yy = y0 + h - 12.0
        for tag, txt in lines:
            if tag:
                cv.text(x + 3.0, yy, tag, ha='left', weight='bold', color=tagcol.get(tag, INK))
                cv.text(x + 12.5, yy, txt, ha='left')
                yy -= 5.2
            else:
                tall = 'frac' in txt
                if tall:
                    yy -= 1.2
                cv.text(x + w / 2, yy, txt)
                yy -= 7.4 if tall else 5.4
        cv.text(x + w / 2, y0 + 6.2, foot, color=MUTED, style='italic')
    for i in range(3):
        cv.arrow(xs[i] + w + 0.2, y0 + h / 2, xs[i + 1] - 0.2, y0 + h / 2, lw=1.1)
    # bottom row
    cv.text(xs[0] + w / 2, 19.0, 'planning prior:\nused only to\nchoose the tests', color=MUTED, style='italic')
    cv.arrow(xs[0] + w - 3.0, 22.0, xs[1] + 8.0, y0 - 0.3, c='#c48a00', lw=0.9, rad=-0.2)
    bw = w + gap + 11.0
    cv.box(xs[1], 2.0, bw, 33.0, '#f4f1fb', VIOLET, lw=0.9)
    cx = xs[1] + bw / 2
    cv.text(cx, 30.5, 'Monthly samples  (C4)', weight='bold', color=VIOLET)
    cv.text(cx, 23.8, 'e-values multiply month')
    cv.text(cx, 19.0, 'by month: look at every')
    cv.text(cx, 14.2, 'meeting, act at any time')
    cv.text(cx, 7.6, r'$P(\exists\, t:\ \mathrm{true}\notin S_t)\leq\beta$')
    x5 = xs[1] + bw + 3.0
    bw5 = 169.0 - x5
    cv.box(x5, 2.0, bw5, 33.0, GREEN_L, GREEN, lw=0.9)
    cx = x5 + bw5 / 2
    cv.text(cx, 30.5, 'Stakeholders and decision  (C5)', weight='bold', color=GREEN)
    cv.text(cx, 23.8, r'regulator and public set $\delta=\alpha+\beta$')
    cv.text(cx, 19.0, 'decision: pumping of A, B, C, supply X')
    cv.text(cx, 14.2, 'ledger of who pays: utility, households,')
    cv.text(cx, 9.4, 'farmers, wetland, tests')
    cv.arrow(xs[1] + bw - 4.0, 35.2, xs[1] + bw - 4.0, y0 - 0.3, c=VIOLET, lw=1.0)
    cv.arrow(xs[3] + 8.0, 35.2, xs[3] + 8.0, y0 - 0.3, c=GREEN, lw=1.0)
    cv.text(xs[3] + 6.8, 38.0, r'$\delta$', color=GREEN, ha='right')
    cv.arrow(xs[3] + 20.0, y0 - 0.3, xs[3] + 20.0, 35.2, c=GREEN, lw=1.0)
    cv.text(xs[3] + 21.2, 38.0, 'decision', color=GREEN, ha='left')
    cv.fig.savefig(os.path.join(out, 'fig_method.png'), dpi=300)
    plt.close(cv.fig)


# ------------------------------------------------------------------------------------------------ P0
def fig_wrong(out, R):
    src = R['setup']['src']
    P1 = R['P1']['by_source']
    M = np.array(R['P0']['cross'])
    M = np.hstack([M, np.array([[P1[s]['worst']['exceed']] for s in src]),
                   np.array([[P1[s]['bayes_prior']['exceed']] for s in src])])
    costs = [R['P0']['cost'][s] for s in src] + [R['P0']['worst']['cost'], R['P0']['bayes_prior']['cost']]
    cols = [f'act as if\n{s}' for s in src] + ['safe for\nall four', 'Bayes,\nprior only']
    fig = plt.figure(figsize=(170 * MM, 72 * MM))
    ax = fig.add_axes([0.17, 0.08, 0.60, 0.66])
    cmap = LinearSegmentedColormap.from_list('exc', ['#ffffff', '#fbd3c2', '#eb6834', '#9c2f0e'])
    ax.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect='auto')
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            ax.text(j, i, f'{100 * v:.0f}%' if v >= 0.005 else '<1%', ha='center', va='center',
                    color='white' if v > 0.55 else INK, fontsize=FS + 0.6, fontweight='bold' if v > 0.1 else 'normal')
        ax.add_patch(Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False, ec=GREEN, lw=1.8))
    ax.axvline(3.5, color='white', lw=3)
    ax.set_xticks(range(M.shape[1])); ax.set_xticklabels(cols)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(src))); ax.set_yticklabels([f'true source: {s}' for s in src])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    for j, c in enumerate(costs):
        ax.text(j, len(src) - 0.35, f'{c / 1000:.2f} M€', ha='center', va='top', color=MUTED, fontsize=FS)
    ax.text(-0.62, len(src) - 0.35, 'social cost', ha='right', va='top', color=MUTED, fontsize=FS)
    fig.text(0.795, 0.72, 'probability that the\ndelivered blend\nexceeds 250 mg/L\nin the dry season', va='top',
             color=INK, fontsize=FS)
    fig.text(0.795, 0.42, f'budget δ = {R["setup"]["delta"]:.2f}', color=INK, fontsize=FS)
    fig.text(0.795, 0.34, '□ right story', color=GREEN, fontsize=FS, fontweight='bold')
    save(fig, out, 'wrong')


# ------------------------------------------------------------------------------------------------ P1
def fig_policies(out, R):
    src = R['setup']['src']; P1 = R['P1']; d = R['setup']['delta']
    fig = plt.figure(figsize=(170 * MM, 80 * MM))
    ax = fig.add_axes([0.25, 0.14, 0.42, 0.73])
    n = len(POL)
    for i, (p, lab) in enumerate(POL):
        y = n - 1 - i
        if p == 'prejardhja':
            ax.add_patch(Rectangle((-0.02, y - 0.45), 1.04, 0.9, fc=GREEN_L, ec='none', zorder=0))
        for j, s_ in enumerate(src):
            v = P1['by_source'][s_][p]['exceed']
            ax.plot(v, y + (1.5 - j) * 0.17, 'o', ms=5.0, color=SRC_COL[s_], mec='white', mew=0.5, zorder=3)
    ax.axvline(d, color=INK, lw=0.9, ls='--', zorder=2)
    ax.text(d + 0.015, n - 0.45, f'δ = {d:.2f}', ha='left', va='bottom', color=INK)
    ax.set_yticks(range(n)[::-1]); ax.set_yticklabels([lab.replace('\n', ' ').replace('PREJARDHJA -GO', 'PREJARDHJA-GO')
                                                     for _, lab in POL])
    ax.set_xlim(-0.02, 1.0); ax.set_ylim(-0.6, n - 0.2)
    ax.set_xlabel('P(blend > 250 mg/L) for each true source')
    GF.style(ax, grid='x')
    ax.set_title('a  Exceedance, one dot per true source', loc='left', fontsize=9.4)
    from matplotlib.lines import Line2D
    hs = [Line2D([], [], marker='o', ls='', color=SRC_COL[s_], ms=5.5, label=f'true source {s_}') for s_ in src]
    ax.legend(handles=hs, frameon=False, loc='lower right', bbox_to_anchor=(1.0, 0.16), handletextpad=0.2)
    ax2 = fig.add_axes([0.70, 0.14, 0.28, 0.73])
    vals = [P1['prior_avg'][p]['cost'] / 1000 for p, _ in POL]
    cols = [GREEN if p == 'prejardhja' else '#b8bec6' for p, _ in POL]
    ax2.barh(range(n)[::-1], vals, color=cols, height=0.6)
    for i, v in enumerate(vals):
        ax2.text(v + 0.06, n - 1 - i, f'{v:.2f}', va='center', color=INK)
    ax2.set_yticks([]); ax2.set_ylim(-0.6, n - 0.2)
    ax2.set_xlim(0, 5.0); ax2.set_xlabel('expected social cost, M€')
    GF.style(ax2, grid='x')
    ax2.set_title('b  Cost, tests included', loc='left', fontsize=9.4)
    save(fig, out, 'policies')


# ------------------------------------------------------------------------------------------------ P2
def place_labels(fig, ax, pts, labels, colors, obstacles=()):
    """Greedy placement: try sixteen offsets per label and keep the first whose box stays inside the axes and clear of
    the labels, points and obstacles already placed; otherwise the offset with the least overlap."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    ax_box = ax.get_window_extent(rend)
    taken = [ax.transData.transform(p) for p in pts]
    boxes = [o.get_window_extent(rend) for o in obstacles]
    offs = [(4, 3), (4, -10), (-4, 3), (-4, -10), (0, 8), (0, -14), (8, -3), (-8, -3), (10, 9), (-10, 9),
            (10, -16), (-10, -16), (0, 15), (0, -21), (14, 2), (-14, 2)]

    def area(bb, o):
        w = min(bb.x1, o.x1) - max(bb.x0, o.x0); h = min(bb.y1, o.y1) - max(bb.y0, o.y0)
        return max(w, 0) * max(h, 0)

    order = sorted(range(len(pts)), key=lambda i: -pts[i][1])
    for i in order:
        (x, y), lab, col = pts[i], labels[i], colors[i]
        best_t, best_bad = None, None
        for dx, dy in offs:
            t = ax.annotate(lab, (x, y), xytext=(dx, dy), textcoords='offset points', color=col,
                            ha='left' if dx > 0 else ('right' if dx < 0 else 'center'), fontsize=FS,
                            arrowprops=dict(arrowstyle='-', color='#c9ced6', lw=0.5, shrinkA=0, shrinkB=2)
                            if abs(dx) + abs(dy) > 14 else None)
            bb = t.get_window_extent(rend).expanded(1.03, 1.08)
            out_ = max(0, ax_box.x0 - bb.x0) + max(0, bb.x1 - ax_box.x1) + max(0, ax_box.y0 - bb.y0) + \
                max(0, bb.y1 - ax_box.y1)
            bad = 50 * out_ + sum(area(bb, o) for o in boxes) + \
                sum(400 for (px, py) in taken if bb.contains(px, py))
            if best_bad is None or bad < best_bad:
                if best_t is not None:
                    best_t.remove()
                best_t, best_bad, best_bb = t, bad, bb
            else:
                t.remove()
            if bad == 0:
                break
        boxes.append(best_bb)


def fig_tests(out, R):
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 96 * MM))
    fig.subplots_adjust(left=0.08, right=0.975, bottom=0.12, top=0.83, wspace=0.22)
    for ax, key, title, where in ((axs[0], 'P2', 'a  Deep brine under the deep wellfield C', (0.97, 0.05, 'right', 'bottom')),
                                  (axs[1], 'P2_upA', 'b  Deep brine under the coastal wellfield A',
                                   (0.97, 0.05, 'right', 'bottom'))):
        P2 = R[key]
        rows = P2['rows'][1:]
        pts, labs, cols = [], [], []
        for r in rows:
            is_best = r['tests'] == P2['best']
            ax.plot(r['eig'], r['net'], 'o', ms=6 if is_best else 4.6, color=GREEN if is_best else REF,
                    mec='white', mew=0.5, zorder=3)
            pts.append((r['eig'], r['net'])); labs.append('+'.join(t[1] for t in r['tests']))
            cols.append(GREEN if is_best else MUTED)
        ax.axhline(0, color='#c9ced6', lw=0.8)
        ax.set_xlabel('information gain about the source (bits)')
        ax.set_title(title, loc='left', fontsize=9.4)
        lo, hi = min(p[1] for p in pts), max(p[1] for p in pts)
        ax.set_ylim(min(0, lo) - 0.08 * (hi - lo), hi + 0.16 * (hi - lo))
        ax.set_xlim(0.28, 1.68)
        GF.style(ax, grid='both')
        x, y, ha, va = where
        st = ax.text(x, y, f'rank correlation {P2["spearman"]:.2f}\ninformation ranking loses\nup to {P2["gap"]:.0f} k€ '
                           'at equal budget', transform=ax.transAxes, ha=ha, va=va, color=INK)
        place_labels(fig, ax, pts, labs, cols, obstacles=[st])
    axs[0].set_ylabel('net decision value (k€)')
    fig.text(0.08, 0.965, 'Label = tests in the bundle: 1 Br/Cl, 2 isotopes, 3 depth profiles, 4 nitrate–boron.',
             color=MUTED)
    fig.text(0.08, 0.93, 'Green = bundle chosen by decision value (C3).', color=GREEN)
    save(fig, out, 'tests')


# ------------------------------------------------------------------------------------------------ P4
def fig_monitor(out, R):
    P4 = R['P4']; src = R['setup']['src']; months = np.arange(1, P4['months'] + 1)
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 70 * MM))
    fig.subplots_adjust(left=0.09, right=0.975, bottom=0.17, top=0.86, wspace=0.27)
    ax = axs[0]
    ev = np.mean([P4['by_source'][s]['out_t'] for s in src], 0)
    nv = np.mean([P4['by_source'][s]['naive_t'] for s in src], 0)
    ax.plot(months, nv, '-o', color=ORANGE, ms=3.5, lw=2, label='ordinary test, repeated')
    ax.plot(months, ev, '-o', color=BLUE, ms=3.5, lw=2, label='e-values (C4)')
    ax.axhline(P4['beta'], color=INK, ls='--', lw=0.9)
    ax.text(2.2, P4['beta'] - 0.004, f'β = {P4["beta"]:.2f}', ha='left', va='top')
    ax.set_xlabel('month'); ax.set_ylabel('P(true source ever dropped)')
    ax.set_ylim(0, 0.25); ax.set_xticks(months)
    ax.legend(frameon=False, loc='lower right', bbox_to_anchor=(1.0, 0.2))
    ax.set_title('a  Looking at the data every month', loc='left', fontsize=9.4)
    GF.style(ax)
    ax = axs[1]
    ends = sorted(((P4['by_source'][s]['cost_t'][-1] / 1000, s) for s in src))
    ypos, last = {}, -9.0
    for v, s in ends:                                  # keep the end labels at least 0.07 M€ apart
        ypos[s] = max(v, last + 0.07); last = ypos[s]
    for s in src:
        b = P4['by_source'][s]
        ax.plot(months, np.array(b['cost_t']) / 1000, '-', color=SRC_COL[s], lw=2)
        ax.plot([1, 12], [b['oracle_cost'] / 1000] * 2, ':', color=SRC_COL[s], lw=1.1)
        ax.text(12.25, ypos[s], s, color=SRC_COL[s], va='center', fontweight='bold')
    ax.set_xlabel('month'); ax.set_ylabel('cost of the decision, M€')
    ax.set_xticks(months); ax.set_xlim(0.7, 13.3)
    ax.text(0.98, 0.97, 'dotted: oracle', transform=ax.transAxes, ha='right', va='top', color=MUTED)
    ax.set_title('b  Cost of deciding in that month', loc='left', fontsize=9.4)
    GF.style(ax)
    save(fig, out, 'monitor')


# ------------------------------------------------------------------------------------------------ P5
def fig_stress(out, R):
    P5 = R['P5']; src = R['setup']['src']; d = R['setup']['delta']; beta = R['P1']['beta']
    fig, axs = plt.subplots(2, 2, figsize=(170 * MM, 128 * MM))
    fig.subplots_adjust(left=0.09, right=0.975, bottom=0.08, top=0.94, wspace=0.34, hspace=0.5)
    ax = axs[0, 0]
    names = list(P5['mixtures'])
    pols = [('prejardhja', 'pure list', BLUE), ('mixture_exact', 'mixtures', AQUA),
            ('bayes_post', 'Bayes', REF), ('map', 'most probable', ORANGE)]
    for j, (p, lab, col) in enumerate(pols):
        ax.bar(np.arange(len(names)) + (j - 1.5) * 0.19, [P5['mixtures'][n][p]['exceed'] for n in names], width=0.17,
               color=col, label=lab)
    ax.axhline(d, color=INK, ls='--', lw=0.9)
    ax.set_xticks(range(len(names))); ax.set_xticklabels([n.replace(' 0.4', '\n(40:60)') for n in names])
    ax.set_ylabel('P(blend > 250 mg/L)')
    ax.legend(frameon=False, ncol=2, loc='upper left', handlelength=1.0, columnspacing=1.0)
    ax.set_ylim(0, 0.8)
    ax.set_title('a  The truth is a mixture of two sources', loc='left', fontsize=9.4)
    GF.style(ax)
    ax = axs[0, 1]
    for j, s in enumerate(src):
        c0 = P5['offset']['0.0'][s]['cover']; c1 = P5['offset']['1.0'][s]['cover']
        ax.plot([j, j], [c0, c1], color='#c9ced6', lw=1.2, zorder=1)
        ax.plot(j, c0, 'o', color=ORANGE, ms=6, zorder=3, label='ordinary e-value' if j == 0 else None)
        ax.plot(j, c1, 'o', color=BLUE, ms=6, zorder=3, label='robust e-value (drift ≤ 1 sd)' if j == 0 else None)
    ax.axhline(1 - beta, color=INK, ls='--', lw=0.9)
    ax.text(2.5, 1 - beta + 0.002, f'1 − β = {1 - beta:.2f}', ha='center', va='bottom')
    ax.set_xticks(range(len(src)))
    ax.set_xticklabels([f'{s}\n→ {P5["offset"]["0.0"][s]["towards"]}' for s in src])
    ax.set_ylabel('P(true source kept)'); ax.set_ylim(0.88, 1.005)
    ax.legend(frameon=False, loc='lower left')
    ax.set_title('b  Signatures drift 1 sd towards a rival', loc='left', fontsize=9.4)
    GF.style(ax)
    camp = P5['campaigns']; n = [c['n'] for c in camp]; tc = sum(R['setup']['tcost'])
    ax = axs[1, 0]
    ax.plot(n, [(c['pure'] - c['n'] * tc) / 1000 for c in camp], '-o', color=BLUE, lw=2, ms=4, label='pure list')
    ax.plot(n, [(c['exact'] - c['n'] * tc) / 1000 for c in camp], '-o', color=AQUA, lw=2, ms=4, label='mixtures admitted')
    ax.axhline(R['P1']['prior_avg']['oracle']['cost'] / 1000, color=INK, ls=':', lw=1)
    ax.text(12.5, R['P1']['prior_avg']['oracle']['cost'] / 1000 - 0.015, 'oracle', ha='center', va='top')
    ax.set_ylim(2.72, 4.05)
    ax.set_xlabel('campaigns of the four tests'); ax.set_ylabel('decision cost, M€ (no tests)')
    ax.set_xticks(n); ax.legend(frameon=False)
    ax.set_title('c  More data narrow the mixtures', loc='left', fontsize=9.4)
    GF.style(ax)
    ax = axs[1, 1]
    ax.plot(n, [c['mix_exceed_pure']['SWI+UP'] for c in camp], '-o', color=BLUE, lw=2, ms=4, label='pure sources only')
    ax.plot(n, [c['mix_exceed_exact']['SWI+UP'] for c in camp], '-o', color=AQUA, lw=2, ms=4, label='mixtures admitted')
    ax.axhline(d, color=INK, ls='--', lw=0.9)
    ax.set_xlabel('campaigns of the four tests'); ax.set_ylabel('P(blend > 250), truth SWI+UP')
    ax.set_xticks(n); ax.set_ylim(0, 0.55); ax.legend(frameon=False, loc='lower right', bbox_to_anchor=(1.0, 0.24))
    ax.set_title('d  The pure list grows overconfident', loc='left', fontsize=9.4)
    GF.style(ax)
    save(fig, out, 'stress')


# ------------------------------------------------------------------------------------------------ P3
def fig_ledger(out, R):
    from matplotlib.ticker import NullFormatter
    led = R['P3']['ledger']
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 70 * MM), gridspec_kw=dict(width_ratios=[1.35, 1]))
    fig.subplots_adjust(left=0.17, right=0.975, bottom=0.31, top=0.9, wspace=0.32)
    ax = axs[0]
    pols = [('oracle', 'oracle'), ('prejardhja', 'PREJARDHJA-GO'), ('bayes_post', 'Bayes posterior'),
            ('worst', 'worst case')]
    parts = [('utility', 'utility (supply)', '#9db8dc'), ('farmers', 'farmers', AQUA), ('wetland', 'wetland', VIOLET),
             ('tests', 'tests', ORANGE)]
    for i, (p, lab) in enumerate(pols):
        left = 0.0
        for key, plab, col in parts:
            v = led[p][key] / 1000
            ax.barh(len(pols) - 1 - i, v, left=left, color=col, height=0.6, label=plab if i == 0 else None,
                    edgecolor='white', linewidth=1.0)
            left += v
        ax.text(left + 0.05, len(pols) - 1 - i, f'{left:.2f}', va='center')
    ax.set_yticks(range(len(pols))[::-1]); ax.set_yticklabels([lab for _, lab in pols])
    ax.set_xlabel('expected social cost, M€'); ax.set_xlim(0, 4.9)
    ax.legend(frameon=False, ncol=4, loc='upper left', bbox_to_anchor=(-0.3, -0.25), handlelength=1.0,
              columnspacing=0.9)
    ax.set_title('a  Who pays', loc='left', fontsize=9.4)
    GF.style(ax, grid='x')
    ax = axs[1]
    fr = R['P3b']
    dl = [f['delta'] for f in fr]
    series = [('worst', 'worst case (no tests)', REF, '-', 2.0), ('prejardhja', 'PREJARDHJA-GO', GREEN, '-', 2.0),
              ('oracle', 'oracle', INK, ':', 1.2)]
    for key, lab, col, ls, lw in series:
        yv = [f[key] / 1000 for f in fr]
        ax.plot(dl, yv, ls, color=col, lw=lw)
        ax.plot(dl, yv, 'o', color=col, ms=3.8)
        if key == 'oracle':
            ax.text(dl[0], yv[0] - 0.07, lab, ha='left', va='top', color=col, fontweight='bold')
        else:
            ax.text(dl[0], yv[0] + 0.08, lab, ha='left', va='bottom', color=col, fontweight='bold')
    ax.set_xscale('log'); ax.set_xticks(dl); ax.set_xticklabels([f'{v:.2f}' for v in dl])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel('risk budget δ'); ax.set_ylabel('expected social cost, M€')
    ax.set_ylim(2.6, 4.75)
    ax.set_title('b  The price of safety', loc='left', fontsize=9.4)
    GF.style(ax)
    save(fig, out, 'ledger')


# ------------------------------------------------------------------------------------------------ the thirty papers
def fig_map(out, cards):
    comps = [('C1', 'plausible set'), ('C2', 'robust allocation'), ('C3', 'test choice'), ('C4', 'monitoring'),
             ('C5', 'stakeholders')]
    n = len(cards)
    fig = plt.figure(figsize=(170 * MM, 175 * MM))
    left, bottom, top = 0.55, 0.035, 0.80
    ax = fig.add_axes([left, bottom, 0.95 - left, top - bottom])
    prev = None
    for i, cd in enumerate(cards):
        y = n - 1 - i
        col = INST[cd['inst']]
        if prev is not None and cd['inst'] != prev:
            ax.axhline(y + 0.5, color='#c9ced6', lw=0.6)
        prev = cd['inst']
        for j, (key, _) in enumerate(comps):
            if key in cd['comps']:
                ax.plot(j, y, 'o', color=col, ms=6.4, zorder=3)
            else:
                ax.plot(j, y, 'o', color='#e1e4e8', ms=2.4, zorder=2)
        ax.text(-0.75, y, f"{cd['id']}  {cd['short']}", ha='right', va='center', color=INK, clip_on=False)
    ax.set_xlim(-0.6, len(comps) - 0.4); ax.set_ylim(-0.6, n - 0.4)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    for j, (key, lab) in enumerate(comps):
        ax.text(j, n - 0.1, f'{key}  {lab}', ha='center', va='bottom', rotation=90, color=INK, clip_on=False)
    x0 = 0.02
    for inst, col in INST.items():
        fig.text(x0, 0.982, '●', color=col, fontsize=FS + 1.5, va='center')
        fig.text(x0 + 0.022, 0.982, inst, color=INK, va='center')
        x0 += 0.12
    fig.text(0.02, 0.957, '● component of PREJARDHJA-GO that the paper informs', color=MUTED, va='center')
    save(fig, out, 'map')


def main(out, cards=None):
    os.makedirs(out, exist_ok=True)
    R = load()
    fig_method(out)
    fig_wrong(out, R)
    fig_policies(out, R)
    fig_tests(out, R)
    fig_monitor(out, R)
    fig_stress(out, R)
    fig_ledger(out, R)
    if cards:
        fig_map(out, cards)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, 'figs'))
