"""Figures of the review "From chaos in the pores to Darcy's law" (English labels; every text at least 8.6 pt at the
printed size, 17 cm wide).  usage: python kaos_figs.py OUT_DIR

fig_map      the twenty-five papers against the five routes of explanation
fig_scheme   the KAOS-GO loop
fig_fields   the cell: speed in the Darcy regime and in the chaotic regime, and the energy of the fluctuations
fig_macro    the large-scale law: resistance split into mean flow and fluctuations, Lyapunov exponent, unsteady share
fig_rev      the Darcy coefficient of finite cells: scatter and its decay with the number of grains
fig_clt      the flux in time: series, variance of window means, coverage of three kinds of interval
fig_design   the weights of a decision and the allocation of the pore-scale effort
Numbers come from res/kaos.json, res/kaos_fields.npz and res/kaos_series.npz."""
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
from rgo_figs import Canvas, INK, MUTED, GRID  # noqa: E402

RES = os.path.join(HERE, 'res')
MM, FS = GF.MM, GF.FS
BLUE, ORANGE, AQUA, VIOLET, YELLOW, REF = GF.BLUE, GF.ORANGE, GF.AQUA, GF.VIOLET, '#eda100', GF.REF
# the order Caltech, Oxford, MIT, Harvard, Max Planck passes the palette validator (adjacent pairs, light surface)
INST = {'Caltech': ORANGE, 'Oxford': BLUE, 'MIT': AQUA, 'Harvard': VIOLET, 'Max Planck': YELLOW}
BLUES = LinearSegmentedColormap.from_list('blues', ['#f3f8fe', '#cde2fb', '#86b6ef', '#3987e5', '#1c5cab', '#0d366b'])
ORANGES = LinearSegmentedColormap.from_list('oranges', ['#fdf5f0', '#f9d6c5', '#f3a480', '#eb6834', '#b8451a', '#6e2a10'])
SOLID = '#d9dce1'


def style(ax, grid='y'):
    GF.style(ax, grid)


def load():
    with open(os.path.join(RES, 'kaos.json')) as fh:
        return json.load(fh)


# ------------------------------------------------------------------------------------------------- the map of papers
def fig_map(out, cards, routes):
    n = len(cards)
    short = dict(see='seeing it', hom='homogenisation', stat='statistics', diss='dissipation', learn='learning')
    fig = plt.figure(figsize=(170 * MM, 150 * MM))
    left, bottom, top = 0.575, 0.02, 0.865
    ax = fig.add_axes([left, bottom, 0.985 - left, top - bottom])
    for i, cd in enumerate(cards):
        y = n - 1 - i
        col = INST[cd['inst']]
        if i % 5 == 0 and i:
            ax.axhline(y + 0.5, color='#c9ced6', lw=0.6)
        for j, (key, _) in enumerate(routes):
            if key in cd['routes']:
                ax.plot(j, y, 'o', color=col, ms=7.0, zorder=3)
            else:
                ax.plot(j, y, 'o', color='#e1e4e8', ms=2.4, zorder=2)
        ax.text(-0.72, y, f"{cd['id']}  {cd['short']}", ha='right', va='center', color=INK, clip_on=False)
    ax.set_xlim(-0.6, len(routes) - 0.4); ax.set_ylim(-0.6, n - 0.4)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    for j, (key, _) in enumerate(routes):
        ax.text(j - 0.12, n - 0.25, short[key], ha='left', va='bottom', rotation=42, rotation_mode='anchor', color=INK,
                clip_on=False)
    x0 = 0.015
    for inst, col in INST.items():
        fig.text(x0, 0.975, '●', color=col, fontsize=FS + 1.5, va='center')
        fig.text(x0 + 0.02, 0.975, inst, color=INK, va='center')
        x0 += {'Caltech': 0.105, 'Oxford': 0.10, 'MIT': 0.075, 'Harvard': 0.11}.get(inst, 0.1)
    fig.text(0.015, 0.94, '● the paper serves this route of explanation', color=MUTED, va='center')
    fig.savefig(os.path.join(out, 'fig_map.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------- the loop
def fig_scheme(out):
    cv = Canvas(170, 84)
    t = cv.text
    B1, B2, B3 = '#e3eefb', '#fde9df', '#e2f5ee'

    def box(x, y, w, h, fc, ec, head, lines):
        cv.box(x, y, w, h, fc, ec, lw=1.0, r=1.8)
        t(x + 2.2, y + h - 4.2, head, ha='left', weight='bold', color=INK)
        for k, ln in enumerate(lines):
            t(x + 2.2, y + h - 9.0 - 4.1 * k, ln, ha='left', color=MUTED)

    box(4, 52, 50, 27, B1, BLUE, 'Pore scale, resolved', ['steady or chaotic flow;', 'forcing levels, long windows,',
                                                         'realisations of the grains'])
    box(60, 60.5, 50, 18.5, 'white', BLUE, 'Dissipation split', ['mean flow + fluctuations', '→ resistance F(Re)'])
    box(60, 37.5, 50, 18.5, 'white', BLUE, 'Statistics of the flux', ['correlation time, long-run', 'variance, scatter of cells'])
    box(116, 52, 50, 27, B2, ORANGE, 'Fluctuating Darcy closure', ['mean law + noise term;', 'scores of cases predicted',
                                                                  'in advance → multiplier'])
    box(116, 6, 50, 27, B3, AQUA, 'Darcy scale, with adjoint', ['decision J with its interval;', 'weights w(q): where the',
                                                                'decision listens'])
    box(4, 6, 50, 27, 'white', AQUA, 'Design of the small scale', ['which levels, how long,', 'how many cells; which law',
                                                                   'to discriminate next'])
    cv.arrow(54, 70, 60, 70, BLUE); cv.arrow(54, 57, 60, 50, BLUE)
    cv.arrow(110, 70, 116, 70, BLUE); cv.arrow(110, 49, 116, 57, BLUE)
    cv.arrow(141, 52, 141, 33, ORANGE)
    cv.arrow(116, 19.5, 54, 19.5, AQUA)
    cv.arrow(29, 33, 29, 52, AQUA)
    t(85, 22.8, 'adjoint weights', color='#0f7a55')
    t(85, 15.6, 'never through the chaos', color=MUTED)
    t(144, 42.5, 'closure', ha='left', color='#b8451a')
    t(32, 42.5, 'next runs', ha='left', color='#0f7a55')
    cv.fig.savefig(os.path.join(out, 'fig_scheme.png'), dpi=300)
    plt.close(cv.fig)


# ------------------------------------------------------------------------------------------------- the fields
def fig_fields(out):
    z = np.load(os.path.join(RES, 'kaos_fields.npz'))
    solid = z['solid']
    fig, axs = plt.subplots(1, 3, figsize=(170 * MM, 72 * MM), gridspec_kw=dict(left=0.01, right=0.99, top=0.90, bottom=0.24, wspace=0.05))
    panels = (('darcy_speed', BLUES, 'mean speed / pore velocity', f"(a) Darcy regime, Re = {float(z['darcy_Re']):.2f}"),
              ('chaotic_speed', BLUES, 'mean speed / pore velocity', f"(b) chaotic regime, Re = {float(z['chaotic_Re']):.0f}"),
              ('chaotic_tke', ORANGES, 'energy of fluctuations / (pore velocity)²/2', '(c) the same run: fluctuations'))
    for ax, (key, cmap, lab, title) in zip(axs, panels):
        a = z[key].astype(float)
        vmax = np.percentile(a[~solid], 99.5)
        a = np.ma.masked_where(solid, a)
        cm = cmap.copy(); cm.set_bad(SOLID)
        im = ax.imshow(a, origin='lower', cmap=cm, vmin=0, vmax=vmax, interpolation='bilinear')
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor('#8b949e'); sp.set_linewidth(0.6)
        ax.set_title(title, color=INK)
        cax = ax.inset_axes([0.08, -0.13, 0.84, 0.045])
        cb = fig.colorbar(im, cax=cax, orientation='horizontal')
        cb.outline.set_linewidth(0.4); cb.ax.tick_params(length=2, labelsize=FS)
        cb.set_ticks(np.round(np.linspace(0, vmax, 4), 2 if vmax < 3 else 1))
        ax.text(0.5, -0.30, lab, transform=ax.transAxes, ha='center', va='top', color=MUTED)
    fig.savefig(os.path.join(out, 'fig_fields.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------- the large-scale law
def fig_macro(out, R):
    lev = R['levels']
    Re = np.array([r['Re'] for r in lev]); F = np.array([r['F'] for r in lev])
    Fm = np.array([r['F_mean'] for r in lev]); Ff = np.array([r['F_fluct'] for r in lev])
    fig = plt.figure(figsize=(170 * MM, 128 * MM))
    xlim = (Re[0] * 0.8, Re[-1] * 3.6)
    ax = fig.add_axes([0.07, 0.50, 0.915, 0.40])
    ax.fill_between(Re, 0, Fm, color=BLUE, alpha=0.30, lw=0)
    ax.fill_between(Re, Fm, Fm + Ff, color=ORANGE, alpha=0.55, lw=0)
    ax.plot(Re, Fm, color=BLUE, lw=2)
    ax.plot(Re, F, color=INK, lw=1.2, marker='o', ms=4.2, mfc='white', mec=INK, mew=1.0, zorder=5)
    ax.axhline(1, color=REF, lw=0.9, ls=(0, (4, 3)))
    ax.set_xscale('log'); ax.set_xlim(*xlim); ax.set_ylim(0, F[-1] * 1.08)
    style(ax)
    ax.set_title('resistance over its Darcy value, split by the dissipation', pad=18)
    ax.text(Re[0] * 0.9, 1.07, 'Darcy\'s law', color=MUTED, ha='left', va='bottom')
    k = len(Re) - 1
    ax.text(Re[k] * 1.12, 0.5 * Fm[k], 'mean flow', color=BLUE, ha='left', va='center')
    ax.text(Re[k] * 1.12, Fm[k] + 0.5 * Ff[k], 'fluctuations', color='#b8451a', ha='left', va='center')
    j = max(k - 4, 1)
    ax.annotate('measured', xy=(Re[j], F[j]), xytext=(Re[j] * 0.55, F[j] + 0.16 * F[-1]), color=INK, ha='right', va='center',
                arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.7, shrinkA=1, shrinkB=3))
    on = R['onset_unsteady']
    edges = [1.0, np.sqrt(on[0] * on[1])]
    oc = R.get('onset_chaos')
    if oc and oc[1] > on[1]:
        edges.append(np.sqrt(oc[0] * oc[1]))
    names = ['Darcy', 'steady, inertial', 'periodic', 'chaotic'][:len(edges) + 1]
    if oc and oc[1] <= on[1]:
        names[-1] = 'unsteady, chaotic'
    xs = [xlim[0]] + edges + [Re[-1] * 1.05]
    for j_, nm in enumerate(names):
        if len(names) == 4 and j_ == 2:                      # two narrow bands: anchor their labels at the common edge
            ax.text(xs[3] * 0.95, F[-1] * 1.10, nm, ha='right', va='bottom', color=MUTED, clip_on=False)
        elif len(names) == 4 and j_ == 3:
            ax.text(xs[3] * 1.06, F[-1] * 1.10, nm, ha='left', va='bottom', color=MUTED, clip_on=False)
        else:
            ax.text(np.sqrt(xs[j_] * xs[j_ + 1]), F[-1] * 1.10, nm, ha='center', va='bottom', color=MUTED, clip_on=False)
    ax.tick_params(labelbottom=False)
    a2 = fig.add_axes([0.07, 0.275, 0.915, 0.135])
    ly = [r for r in lev if 'lyap_T' in r]
    x = [r['Re'] for r in ly]; y = [r['lyap_T'] for r in ly]; e = [2 * r['lyap_T_se'] for r in ly]
    a2.axhline(0, color=REF, lw=0.9, ls=(0, (4, 3)))
    a2.errorbar(x, y, yerr=e, fmt='o', color=ORANGE, ms=5, mfc=ORANGE, mec='white', mew=0.8, elinewidth=1.2, capsize=0)
    a2.set_xscale('log'); a2.set_xlim(*xlim); style(a2)
    a2.set_title('largest Lyapunov exponent, per pore transit time (bars: two standard errors)')
    a2.tick_params(labelbottom=False)
    a3 = fig.add_axes([0.07, 0.085, 0.915, 0.105])
    ng = max((len(r['grain_tke']) for r in lev if 'grain_tke' in r), default=16)
    xs_ = [r['Re'] for r in lev]; ys_ = [r.get('grains_unsteady', 0) for r in lev]
    a3.plot(xs_, ys_, color=BLUE, lw=2, marker='o', ms=4.2, mfc=BLUE, mec='white', mew=0.8)
    a3.set_xscale('log'); a3.set_xlim(*xlim); a3.set_ylim(-1, ng + 1.5); a3.set_yticks([0, ng // 2, ng]); style(a3)
    a3.set_title(f'grains with strongly fluctuating flow around them, of {ng}')
    a3.set_xlabel('Reynolds number (grain diameter, Darcy velocity)')
    for a_ in (ax, a2, a3):
        for e_ in edges:
            a_.axvline(e_, color='#c9ced6', lw=0.8, zorder=0)
    fig.savefig(os.path.join(out, 'fig_macro.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------- finite cells
def fig_rev(out, R):
    rows = R['rev']['rows']
    fig, (ax, a2) = plt.subplots(1, 2, figsize=(170 * MM, 64 * MM), gridspec_kw=dict(left=0.085, right=0.985, top=0.9, bottom=0.2, wspace=0.28, width_ratios=[1.25, 1]))
    rng = np.random.default_rng(0)
    big = rows[-1]['mean']
    for j, r in enumerate(rows):
        k = np.array(r['K'])
        ax.plot(j + rng.uniform(-0.16, 0.16, len(k)), k, 'o', color=BLUE, ms=4.2, alpha=0.55, mec='none')
        ax.plot([j - 0.3, j + 0.3], [r['mean']] * 2, color=INK, lw=1.6)
        ax.text(j, 0.69, f"mean {r['mean']:.3f}\nscatter {100 * r['cv']:.0f}%", va='bottom', ha='center', color=INK)
    ax.axhline(big, color=REF, lw=0.9, ls=(0, (4, 3)), zorder=0)
    ax.set_xticks(range(len(rows))); ax.set_xticklabels([f"{r['n']} grains\n{r['m']} cells" for r in rows])
    ax.set_xlim(-0.5, len(rows) - 0.5); ax.set_ylabel('Darcy coefficient  K / a²'); style(ax)
    ax.set_title('(a) one coefficient per cell')
    n = np.array([r['n'] for r in rows]); cv = np.array([r['cv'] for r in rows])
    a2.plot(n, 100 * cv, 'o', color=BLUE, ms=6.5, mec='white', mew=0.8, zorder=3)
    xx = np.array([n[0] * 0.7, n[-1] * 1.4])
    a2.plot(xx, 100 * cv[0] * (xx / n[0]) ** -0.5, color=REF, lw=1.2, ls=(0, (4, 3)))
    a2.text(0.04, 0.06, 'dashed: central limit,\nslope −1/2', transform=a2.transAxes, ha='left', va='bottom', color=MUTED)
    a2.text(0.97, 0.95, f"fitted slope {R['rev']['slope']:.2f}".replace('-', '−'), transform=a2.transAxes, ha='right', va='top',
            color=INK)
    a2.set_xscale('log'); a2.set_yscale('log'); a2.set_xticks(n); a2.set_xticklabels([str(v) for v in n])
    a2.set_yticks([2, 5, 10, 20]); a2.set_yticklabels(['2', '5', '10', '20']); a2.minorticks_off()
    a2.set_xlabel('grains in the cell'); a2.set_ylabel('scatter between cells, %'); style(a2)
    a2.set_title('(b) how the scatter decays')
    fig.savefig(os.path.join(out, 'fig_rev.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------- flux in time
def fig_clt(out, R):
    z = np.load(os.path.join(RES, 'kaos_series.npz'))
    longs = R['long']
    cols = (BLUE, ORANGE); tint = ('#86b6ef', '#f3a480'); dark = ('#1c5cab', '#b8451a')
    nl = len(longs)
    fig = plt.figure(figsize=(170 * MM, 140 * MM))
    # (a) one strip per level: the whole record
    top, bot, gap = 0.945, 0.565, 0.022
    h = (top - bot - gap * (nl - 1)) / nl
    strips, ymax = [], 0.0
    for k, r in enumerate(longs):
        ax = fig.add_axes([0.075, top - (k + 1) * h - k * gap, 0.905, h])
        u = z[f"U_{r['nu']}"].astype(float); dt = float(z[f"dt_{r['nu']}"])
        nb = max(int(round(0.25 / dt)), 1); n = len(u) // nb
        thin = 100 * (u[:n * nb].reshape(n, nb).mean(1) - 1); t = (np.arange(n) + 0.5) * nb * dt
        w = int(round(20 / dt)); c = np.cumsum(np.insert(u, 0, 0.0))
        run = 100 * ((c[w:] - c[:-w]) / w - 1); tr = (np.arange(len(run)) + w / 2) * dt
        ax.plot(t, thin, color=tint[k], lw=0.45)
        ax.plot(tr, run, color=dark[k], lw=1.7)
        ax.axhline(0, color=INK, lw=0.7, ls=(0, (4, 3)))
        ymax = max(ymax, np.abs(thin).max())
        ax.set_xlim(0, max(r_['transits'] for r_ in longs)); style(ax)
        ax.text(0.008, 0.90, f"Re = {r['Re_level']:.0f}:  correlation time {r['tau_int']:.1f} transit times", transform=ax.transAxes,
                ha='left', va='top', color=INK, bbox=dict(boxstyle='square,pad=0.15', fc='white', ec='none', alpha=0.85))
        if k < nl - 1:
            ax.set_xticklabels([])
        strips.append(ax)
    lim = float(np.ceil(ymax))
    tk = 2 if lim <= 5 else (4 if lim <= 9 else 6)
    for ax in strips:
        ax.set_ylim(-lim, lim); ax.set_yticks([-tk, 0, tk]); ax.set_yticklabels([f'\u2212{tk}', '0', f'{tk}'])
    strips[-1].set_xlabel('time, pore transit times')
    strips[0].set_title('(a) Darcy flux of the cell, % from its mean; thick line: mean over 20 transit times', loc='left')
    # (b) scatter of window means
    a2 = fig.add_axes([0.075, 0.085, 0.36, 0.355])
    lo, hi = 1e9, 0
    for k, r in enumerate(longs):
        W = np.array([s_['W'] for s_ in r['scaling']]); v = 100 * np.sqrt(np.array([s_['var_rel'] for s_ in r['scaling']]))
        pred = 100 * np.sqrt(np.array([s_['var_pred_rel'] for s_ in r['scaling']]))
        Wl = np.geomspace(2.5, 80, 30); asy = 100 * np.sqrt(r['lrv_rel'] / Wl)
        a2.plot(Wl, asy, color=cols[k], lw=1.2, ls=(0, (4, 3)))
        a2.plot(W, pred, color=cols[k], lw=1.6)
        a2.plot(W, v, 'o', color=cols[k], ms=6, mec='white', mew=0.9, zorder=3)
        lo, hi = min(lo, v.min(), pred.min()), max(hi, v.max(), pred.max(), asy.max() * 1.25)
    a2.set_xscale('log'); a2.set_yscale('log'); style(a2, grid='both')
    a2.set_xlabel('window $T$, transit times')
    a2.set_title('(b) scatter of window means, %', loc='left')
    a2.set_xticks([2.5, 5, 10, 20, 40, 80]); a2.set_xticklabels(['2.5', '5', '10', '20', '40', '80'])
    yt = [t for t in (0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10) if lo * 0.8 <= t <= hi * 1.25]
    a2.set_ylim(lo * 0.36, hi * 1.3); a2.set_yticks(yt); a2.set_yticklabels([f'{t:g}' for t in yt]); a2.minorticks_off()
    from matplotlib.lines import Line2D
    key = [Line2D([], [], marker='o', ls='', color=INK, ms=6, mec='white', mew=0.9, label='measured'),
           Line2D([], [], color=INK, lw=1.6, label='from the autocovariance'),
           Line2D([], [], color=INK, lw=1.2, ls=(0, (4, 3)), label='central limit, $\\sigma_\\infty/\\sqrt{T}$')]
    lg = a2.legend(handles=key, loc='lower left', frameon=False, handlelength=1.9, handletextpad=0.5, borderaxespad=0.25,
                   labelspacing=0.3, labelcolor=INK)
    a2.add_artist(lg)
    for k, r in enumerate(longs):                       # the level is named at the left end of its dashed line
        a2.text(2.75, 100 * np.sqrt(r['lrv_rel'] / 2.5) * 1.06, f"Re = {r['Re_level']:.0f}", ha='left', va='bottom', color=INK)
    # (c) coverage of the three kinds of interval, by level; the values stand in a column at the right, in ink
    a3 = fig.add_axes([0.645, 0.085, 0.335, 0.355])
    labs = [('naive_200', 'memory of one\ntransit assumed'), ('gk_200', 'with the measured\ncorrelation'),
            ('conformal_200', 'certified\n(conformal)'), ('gk_50', 'correlation from\na short record'),
            ('conformal_50', 'certified, same\nshort record')]
    ys = np.arange(len(labs))[::-1].astype(float)
    bh = 0.72 / nl
    for k, r in enumerate(longs):
        C = r['coverage']
        for y, (key, lab) in zip(ys, labs):
            if key not in C:
                continue
            v = 100 * C[key]['cov']
            yy = y + (0.36 - bh / 2) - k * bh
            a3.barh(yy, v, height=bh - 0.04, color=cols[k])
            a3.text(119, yy, f'{v:.0f}%', va='center', ha='right', color=INK)
    a3.axvline(90, color=INK, lw=0.9, ls=(0, (4, 3)))
    from matplotlib.patches import Patch
    a3.legend(handles=[Patch(color=cols[k], label=f"Re = {r['Re_level']:.0f}") for k, r in enumerate(longs)], loc='upper left',
              ncol=nl, frameon=False, handlelength=0.9, handleheight=0.8, handletextpad=0.4, columnspacing=1.2,
              borderaxespad=0.0, bbox_to_anchor=(0.0, 1.0), labelcolor=INK)
    a3.set_yticks(ys); a3.set_yticklabels([l for _, l in labs]); a3.set_xlim(0, 120); a3.set_ylim(-0.6, len(labs) + 0.15)
    a3.set_xticks([0, 30, 60, 90]); style(a3, grid='x')
    a3.set_xlabel('coverage of nominal 90% intervals, %', loc='left')
    a3.set_title('(c) predicting the next window', loc='left')
    fig.savefig(os.path.join(out, 'fig_clt.png'), dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------- the design
def fig_design(out, R):
    lev = R['levels']; d = R['decision']
    Re = np.array([r['Re'] for r in lev])
    w = np.array(d['weights']) * np.array([r['F'] for r in lev])
    fig, (ax, a2) = plt.subplots(1, 2, figsize=(170 * MM, 62 * MM), gridspec_kw=dict(left=0.085, right=0.985, top=0.88, bottom=0.21, wspace=0.3))
    x = np.arange(len(Re))
    ax.bar(x, 100 * w / w.sum(), width=0.62, color=BLUE)
    ax.set_xticks(x); ax.set_xticklabels([f'{v:.0f}' if v >= 10 else (f'{v:.2g}' if v >= 1 else f'{v:.1g}') for v in Re], rotation=0)
    for lab in ax.get_xticklabels()[1::2]:
        lab.set_visible(False)
    ax.set_xlabel('Reynolds number of the level'); ax.set_ylabel('share of the well loss, %'); style(ax)
    ax.set_title('(a) where the decision listens')
    uns = [i for i, v in enumerate(d.get('W_opt', [])) if v > 0]
    if uns:
        xx = np.arange(len(uns))
        a2.bar(xx - 0.2, [d['W_equal'][i] for i in uns], width=0.36, color=REF, label='equal split')
        a2.bar(xx + 0.2, [d['W_opt'][i] for i in uns], width=0.36, color=ORANGE, label='Proposition 3')
        a2.set_xticks(xx); a2.set_xticklabels([f'{Re[i]:.0f}' for i in uns])
        a2.set_xlabel('Reynolds number of the unsteady level'); a2.set_ylabel('sampling, transit times'); style(a2)
        top = max(max(d['W_opt']), max(d['W_equal']))
        a2.set_ylim(0, top * 1.32)
        a2.legend(frameon=False, loc='upper left', handlelength=1.2, ncol=2, columnspacing=1.2)
        a2.set_title('(b) how long to run each level')
    fig.savefig(os.path.join(out, 'fig_design.png'), dpi=300)
    plt.close(fig)


def main(out, cards=None, routes=None):
    os.makedirs(out, exist_ok=True)
    if cards is None:
        from cards_kaos import CARDS as cards, ROUTES as routes
    fig_map(out, cards, routes)
    fig_scheme(out)
    R = load()
    fig_fields(out)
    fig_macro(out, R)
    if 'rev' in R:
        fig_rev(out, R)
    if R.get('long'):
        fig_clt(out, R)
    fig_design(out, R)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'figs')
