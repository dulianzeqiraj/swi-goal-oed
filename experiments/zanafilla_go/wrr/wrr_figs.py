"""Figures of the WRR draft (English labels, smallest text 8.6 pt at a printed width of 17 cm).
usage: python wrr_figs.py OUT_DIR
fig_tracers   the West Coast Basin samples in tracer space with the four end-member intervals
fig_synth     coverage and width of certified bounds, fixed-signature ranges and Bayesian intervals (synthetic)
fig_field     identified intervals of the seawater and brine shares of chloride, wells above 100 mg/L
fig_decide    what each added tracer decides (nested tracer sets)
fig_compare   the same wells under fixed signatures and two Bayesian priors
fig_next      the next action: predicted against realised gain, and characterising an end-member
Field figures read res_field/field.json (public data, not in the repository); fig_synth reads res/wrr_synth.json."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from field_data import load as load_data, build_model, _f  # noqa: E402

INK, MUTED, GRID = '#1f2328', '#5b6672', '#e3e6ea'
FS = 8.6
plt.rcParams.update({'font.size': FS, 'axes.titlesize': 9.4, 'axes.labelsize': FS, 'xtick.labelsize': FS,
                     'ytick.labelsize': FS, 'legend.fontsize': FS, 'font.family': 'DejaVu Sans',
                     'mathtext.fontset': 'dejavusans', 'axes.edgecolor': '#8b949e', 'axes.linewidth': 0.6,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6,
                     'axes.titlelocation': 'left', 'axes.titleweight': 'bold'})
MM = 1 / 25.4
# validated categorical palette (dataviz validator, light surface): sources N, S, I, B in this fixed order
SRC_COL = {'N': '#1baf7a', 'S': '#2a78d6', 'I': '#c43e8f', 'B': '#eb6834'}
SRC_LAB = {'N': 'native ground water', 'S': 'seawater', 'I': 'imported (injected) water', 'B': 'oil-field brine'}
# methods, validated in this order: certified, fixed signatures, Bayes Dirichlet(1), Bayes Dirichlet(0.25)
METH_COL = {'cert': '#2a78d6', 'fixed': '#eb6834', 'bayes1': '#1baf7a', 'bayes025': '#c43e8f'}
METH_LAB = {'cert': 'certified bounds (this work)', 'fixed': 'fixed signatures (IsoSource-type)',
            'bayes1': 'Bayesian, Dirichlet(1) prior', 'bayes025': 'Bayesian, Dirichlet(0.25) prior'}
REF = '#8a9099'
CLBR_MOLAR = 79.904 / 35.453          # Cl/Br molar = (Cl/Br mass) * 79.904 / 35.453


def style(ax, grid='y'):
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(length=2.5)


def save(fig, out, name):
    fig.savefig(os.path.join(out, name + '.png'), dpi=300)
    plt.close(fig)


def field_json():
    with open(os.path.join(HERE, 'res_field', 'field.json')) as fh:
        return json.load(fh)


# ------------------------------------------------------------------------------------------------ fig_tracers
def fig_tracers(out):
    appA, t2 = load_data()
    m, _ = build_model(appA, t2)
    F = field_json()
    empty = {n for n, s in zip(F['names'], F['F1']) if s is None}
    rows = [r for r in appA if r['date'] and r['name'] in t2]
    fig = plt.figure(figsize=(170 * MM, 78 * MM))
    ax1 = fig.add_axes([0.075, 0.15, 0.40, 0.70]); ax2 = fig.add_axes([0.585, 0.15, 0.40, 0.70])
    for k, s in enumerate(m.sources):
        col = SRC_COL[s]
        cl0, cl1 = m.cl[k]
        r0, r1 = m.tr['Br']['sig'][k]
        y0, y1 = CLBR_MOLAR / r1, CLBR_MOLAR / max(r0, 1e-9)
        ax1.add_patch(Rectangle((cl0, y0), cl1 - cl0, y1 - y0, fc=col, ec=col, alpha=0.18, lw=1.0, zorder=1))
        ax1.add_patch(Rectangle((cl0, y0), cl1 - cl0, y1 - y0, fc='none', ec=col, lw=1.2, zorder=2))
    for r in rows:
        x, br = _f(r, 'Cl'), _f(r, 'Br')
        if not np.isfinite(br) or t2[r['name']]['clbr'] == '*':
            continue
        y = CLBR_MOLAR * x / br
        if r['name'] in empty:
            ax1.plot(x, y, 'x', color=INK, ms=6.5, mew=1.4, zorder=4)
        else:
            ax1.plot(x, y, 'o', color='#3d4652', ms=3.6, mec='white', mew=0.5, zorder=3)
    ax1.set_xscale('log'); ax1.set_yscale('log')
    ax1.set_xlim(10, 60000); ax1.set_ylim(50, 8000)
    ax1.set_xlabel('chloride (mg/L)'); ax1.set_ylabel('Cl/Br (molar)')
    ax1.set_title('a  Chloride and the chloride-to-bromide ratio', loc='left')
    style(ax1, None)
    lab1 = {'N': (17, 170, 'left', 'top'), 'S': (19000, 520, 'center', 'top'), 'I': (125, 2500, 'left', 'center'),
            'B': (9000, 120, 'right', 'center')}
    for s, (x, y, ha, va) in lab1.items():
        ax1.text(x, y, SRC_LAB[s], color=INK, fontsize=FS, ha=ha, va=va)
    # isotopes: coupled boxes (d-excess) as polygons
    for k, s in enumerate(m.sources):
        col = SRC_COL[s]
        o0, o1 = m.tr['d18O']['sig'][k]; h0, h1 = m.tr['d2H']['sig'][k]
        d0, d1 = m.joint[0]['lo'][k], m.joint[0]['hi'][k]
        xs = np.linspace(o0, o1, 200)
        lo = np.maximum(h0, 8 * xs + d0); hi = np.minimum(h1, 8 * xs + d1)
        ok = lo <= hi
        if not ok.any():
            continue
        poly = np.r_[np.c_[xs[ok], lo[ok]], np.c_[xs[ok][::-1], hi[ok][::-1]]]
        ls = '--' if s == 'B' else '-'
        ax2.add_patch(Polygon(poly, closed=True, fc=col, ec='none', alpha=0.16 if s != 'B' else 0.08, zorder=1))
        ax2.add_patch(Polygon(poly, closed=True, fc='none', ec=col, lw=1.2, ls=ls, zorder=2))
    xx = np.array([-14, 5]); ax2.plot(xx, 8 * xx + 10, color=REF, lw=0.8, zorder=1)
    for r in rows:
        o, h = _f(r, 'd18O'), _f(r, 'd2H')
        if not np.isfinite(o):
            continue
        if r['name'] in empty:
            ax2.plot(o, h, 'x', color=INK, ms=6.5, mew=1.4, zorder=4)
        else:
            ax2.plot(o, h, 'o', color='#3d4652', ms=3.6, mec='white', mew=0.5, zorder=3)
    ax2.set_xlim(-14, 5); ax2.set_ylim(-116, 12)
    ax2.set_xlabel('$\\delta^{18}$O (per mil)'); ax2.set_ylabel('$\\delta^{2}$H (per mil)')
    ax2.set_title('b  Stable isotopes of water', loc='left')
    style(ax2, None)
    lab2 = {'N': (-13.8, -30, 'left'), 'S': (-0.6, 5, 'right'), 'I': (-13.8, -111, 'left'), 'B': (4.0, -72, 'right')}
    for s, (x, y, ha) in lab2.items():
        ax2.text(x, y, SRC_LAB[s], color=INK, fontsize=FS, ha=ha)
    fig.text(0.075, 0.955, 'Shaded: end-member intervals.  Dots: 80 samples.  x: empty identified set.', color=MUTED,
             fontsize=FS)
    save(fig, out, 'fig_tracers')


# ------------------------------------------------------------------------------------------------ fig_synth
def fig_synth(out):
    with open(os.environ.get('WRR_SYNTH_JSON', os.path.join(HERE, 'res', 'wrr_synth.json'))) as fh:
        R = json.load(fh)
    cases = [('prior | Cl + major ions', 'A\nCl + ions'), ('prior | all seven tracers', 'A\n7 tracers'),
             ('shift | Cl + major ions', 'B\nCl + ions'), ('shift | all seven tracers', 'B\n7 tracers')]
    meths = ['cert', 'fixed', 'bayes1', 'bayes025']
    fig = plt.figure(figsize=(170 * MM, 84 * MM))
    ax1 = fig.add_axes([0.075, 0.30, 0.42, 0.56]); ax2 = fig.add_axes([0.575, 0.30, 0.42, 0.56])
    w = 0.19
    for j, (key, _) in enumerate(cases):
        r = R[key]
        vals = [r['cert_cover'], r['fixed_cover_all'], r['bayes1_cover'], r['bayes025_cover']]
        wid = [r['cert_width'], r['fixed_width'] or 0.0, r['bayes1_width'], r['bayes025_width']]
        for i, mth in enumerate(meths):
            x = j + (i - 1.5) * w
            ax1.bar(x, vals[i], w * 0.9, color=METH_COL[mth], ec='white', lw=0.6, zorder=2)
            ax2.bar(x, wid[i], w * 0.9, color=METH_COL[mth], ec='white', lw=0.6, zorder=2)
    ax1.axhline(0.90, color=INK, lw=0.8, ls='--', zorder=3)
    ax1.set_ylim(0, 1.05); ax1.set_ylabel('coverage of the true seawater share')
    ax2.set_ylim(0, 1.0); ax2.set_ylabel('mean interval width')
    for ax, t in ((ax1, 'a  Coverage'), (ax2, 'b  Width')):
        ax.set_xticks(range(4)); ax.set_xticklabels([c[1] for c in cases], fontsize=FS)
        ax.set_title(t, loc='left'); style(ax, 'y')
        ax.set_xlim(-0.55, 3.55)
    from matplotlib.lines import Line2D
    hs = [Rectangle((0, 0), 1, 1, color=METH_COL[mth]) for mth in meths] + [Line2D([0], [0], color=INK, lw=0.8, ls='--')]
    labs = [METH_LAB['cert'], METH_LAB['fixed'], 'Bayesian, Dirichlet(1)', 'Bayesian, Dirichlet(0.25)', 'nominal 90%']
    fig.legend(hs, labs, loc='lower center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.0), fontsize=FS - 0.4)
    save(fig, out, 'fig_synth')


# ------------------------------------------------------------------------------------------------ fig_field
def fig_field(out):
    F = field_json()
    names, cl, F1, t2 = F['names'], np.array(F['cl']), F['F1'], F['table2']
    sel = [i for i in np.argsort(cl) if cl[i] > 100]
    n = len(sel)
    fig = plt.figure(figsize=(170 * MM, (34 + 4.1 * n) * MM))
    top = 1 - 16 / (34 + 4.1 * n); bot = 12 / (34 + 4.1 * n)
    axs = [fig.add_axes([0.37, bot, 0.285, top - bot]), fig.add_axes([0.70, bot, 0.285, top - bot])]
    for row, i in enumerate(sel):
        y = n - 1 - row
        sb = F1[i]
        code = t2[names[i]]['clbr']
        fig.text(0.012, bot + (y + 0.5) / n * (top - bot), f'{names[i]}', va='center', ha='left', color=INK, fontsize=FS)
        fig.text(0.255, bot + (y + 0.5) / n * (top - bot), f'{cl[i]:,.0f}', va='center', ha='right', color=MUTED,
                 fontsize=FS)
        fig.text(0.28, bot + (y + 0.5) / n * (top - bot), code, va='center', ha='left', color=MUTED, fontsize=FS)
        for ax, k, tau in ((axs[0], 1, F['tau_s']), (axs[1], 3, F['tau_b'])):
            if sb is None:
                ax.text(0.5, y, 'empty set: falsified', ha='center', va='center', color=INK, fontsize=FS - 0.2,
                        style='italic')
                continue
            lo, hi = sb[k]
            col = SRC_COL['S' if k == 1 else 'B']
            ax.add_patch(Rectangle((lo, y - 0.32), max(hi - lo, 0.006), 0.64, fc=col, ec='none', zorder=2))
            dec = lo > tau or hi < tau
            if dec:
                ax.plot(hi + 0.02 if hi < 0.95 else lo - 0.02, y, marker='D', color=INK, ms=3.2, zorder=3)
    for ax, k, tau, t in ((axs[0], 1, F['tau_s'], 'a  Seawater share'),
                          (axs[1], 3, F['tau_b'], 'b  Brine share')):
        ax.axvline(tau, color=INK, lw=0.8, ls='--', zorder=1)
        ax.set_xlim(0, 1); ax.set_ylim(-0.6, n - 0.4)
        ax.set_yticks([]); ax.set_title(t, loc='left', fontsize=9.0)
        ax.set_xlabel('identified interval'); style(ax, 'x')
    fig.text(0.012, top + 0.4 / n * (top - bot) + 0.006, 'well', color=MUTED, fontsize=FS, va='bottom')
    fig.text(0.255, top + 0.4 / n * (top - bot) + 0.006, 'Cl, mg/L', color=MUTED, fontsize=FS, va='bottom', ha='right')
    fig.text(0.28, top + 0.4 / n * (top - bot) + 0.006, 'code', color=MUTED, fontsize=FS, va='bottom')
    save(fig, out, 'fig_field')


# ------------------------------------------------------------------------------------------------ fig_decide
def fig_decide(out):
    F = field_json()
    cl = np.array(F['cl'])
    sel = cl > 100
    keys = list(F['F2'].keys())
    ds, db, ws, nfe = [], [], [], []
    for key in keys:
        S = F['F2'][key]
        d1 = d2 = 0; w = []; ne = 0
        for i in np.where(sel)[0]:
            sb = S[i]
            if sb is None:
                ne += 1; continue
            s_lo, s_hi = sb[1]; b_lo, b_hi = sb[3]
            d1 += (s_lo > F['tau_s'] or s_hi < F['tau_s']); d2 += (b_lo > F['tau_b'] or b_hi < F['tau_b'])
            w.append(s_hi - s_lo)
        ds.append(d1); db.append(d2); ws.append(np.mean(w)); nfe.append(ne)
    fig = plt.figure(figsize=(170 * MM, 80 * MM))
    ax1 = fig.add_axes([0.075, 0.34, 0.42, 0.56]); ax2 = fig.add_axes([0.575, 0.34, 0.42, 0.56])
    x = np.arange(len(keys))
    ax1.plot(x, ds, '-o', color=SRC_COL['S'], lw=2, ms=6, mec='white', mew=1.2, label='seawater the main source?')
    ax1.plot(x, db, '-o', color=SRC_COL['B'], lw=2, ms=6, mec='white', mew=1.2, label='brine more than 10%?')
    ax1.plot(x, nfe, '-o', color=INK, lw=1.2, ms=4.5, mec='white', mew=1.0, label='empty sets')
    ax1.set_ylabel(f'samples decided (of {int(sel.sum())})')
    ax1.set_title('a  Decisions', loc='left')
    fig.legend(frameon=False, loc='lower center', ncol=3, bbox_to_anchor=(0.30, -0.01))
    ax2.plot(x, ws, '-o', color=SRC_COL['S'], lw=2, ms=6, mec='white', mew=1.2)
    ax2.set_ylabel('mean width, seawater share'); ax2.set_ylim(0, 1)
    ax2.set_title('b  Width of the identified interval', loc='left')
    for ax in (ax1, ax2):
        ax.set_xticks(x); ax.set_xticklabels(keys, rotation=25, ha='right')
        style(ax, 'y')
    save(fig, out, 'fig_decide')


# ------------------------------------------------------------------------------------------------ fig_compare
def fig_compare(out, wells):
    F = field_json()
    names = F['names']
    idx = [names.index(w) for w in wells if w in names]
    n = len(idx)
    fig = plt.figure(figsize=(170 * MM, (30 + 7.2 * n) * MM))
    top = 1 - 14 / (30 + 7.2 * n); bot = 22 / (30 + 7.2 * n)
    ax = fig.add_axes([0.20, bot, 0.78, top - bot])
    for row, i in enumerate(idx):
        y = n - 1 - row
        sb = F['F1'][i]; fx = F['F4_fixed'][i]
        b1 = F['F4_bayes']['Dirichlet(1)'][i]['post'][1]; b2 = F['F4_bayes']['Dirichlet(0.25)'][i]['post'][1]
        if sb is not None:
            ax.add_patch(Rectangle((sb[1][0], y + 0.18), sb[1][1] - sb[1][0], 0.22, fc=METH_COL['cert'], ec='none'))
        if fx is not None:
            ax.add_patch(Rectangle((fx[1][0], y - 0.02), max(fx[1][1] - fx[1][0], 0.006), 0.12,
                                   fc=METH_COL['fixed'], ec='none'))
        else:
            ax.text(0.005, y + 0.04, 'fixed signatures: no solution', color='#b2461b', fontsize=FS - 1.0,
                    va='center')
        for b, col, dy in ((b1, METH_COL['bayes1'], -0.20), (b2, METH_COL['bayes025'], -0.36)):
            ax.plot([b[1], b[2]], [y + dy, y + dy], color=col, lw=2.0, solid_capstyle='butt')
            ax.plot(b[0], y + dy, 'o', color=col, ms=4.5, mec='white', mew=0.8)
        ax.text(-0.02, y, names[i], ha='right', va='center', color=INK, transform=ax.get_yaxis_transform())
    ax.set_xlim(0, 1); ax.set_ylim(-0.6, n - 0.4); ax.set_yticks([])
    ax.set_xlabel('share of chloride from seawater')
    ax.set_title('Same wells, four answers', loc='left')
    style(ax, 'x')
    hs = [Rectangle((0, 0), 1, 1, color=METH_COL[mth]) for mth in ('cert', 'fixed', 'bayes1', 'bayes025')]
    fig.legend(hs, [METH_LAB['cert'], METH_LAB['fixed'], METH_LAB['bayes1'] + ' (dot: mean; bar: 90%)',
                    METH_LAB['bayes025']], loc='lower center', ncol=2, frameon=False, bbox_to_anchor=(0.55, 0.0))
    save(fig, out, 'fig_compare')


# ------------------------------------------------------------------------------------------------ fig_next
def fig_next(out):
    F = field_json()
    fig = plt.figure(figsize=(170 * MM, 80 * MM))
    ax1 = fig.add_axes([0.075, 0.33, 0.36, 0.56]); ax2 = fig.add_axes([0.54, 0.33, 0.45, 0.56])
    keys = list(F['F5_retro'].keys())
    lab = {'Br': 'bromide', 'd18O+d2H': 'isotopes', 'H3': 'tritium'}
    w = 0.2
    for j, key in enumerate(keys):
        rows = F['F5_retro'][key]
        base = np.array([r['base'] for r in rows], float).sum(0)
        pred = np.array([r['pred'] for r in rows], float).sum(0)
        real = np.array([r['real'] for r in rows], float).sum(0)
        for d, col in ((0, SRC_COL['S']), (1, SRC_COL['B'])):
            x0 = j + (d - 0.5) * 2.2 * w
            ax1.bar(x0 - w / 2, pred[d] - base[d], w * 0.9, color=col, alpha=0.45, ec='white', zorder=2)
            ax1.bar(x0 + w / 2, real[d] - base[d], w * 0.9, color=col, ec='white', zorder=2)
    ax1.set_xticks(range(len(keys))); ax1.set_xticklabels([lab.get(k, k) for k in keys])
    ax1.axhline(0, color=INK, lw=0.6)
    ax1.set_ylabel('decisions gained')
    ax1.set_title('a  Held-out tracer', loc='left', fontsize=9.0)
    ax1.text(0.99, 0.97, 'light: predicted\ndark: realised', transform=ax1.transAxes, ha='right', va='top',
             color=MUTED, fontsize=FS - 0.4)
    style(ax1, 'y')
    order = ['sample the brine (half)', 'sample the brine (point)', 'sample the imported water (half)',
             'sample the imported water (point)', 'measure seawater tritium (point)']
    short = {'sample the brine (half)': 'brine\n½ width', 'sample the brine (point)': 'brine\nexact',
             'sample the imported water (half)': 'imported\n½ width',
             'sample the imported water (point)': 'imported\nexact', 'measure seawater tritium (point)': 'seawater\ntritium'}
    base = np.array(F['F5_base'])
    for j, a in enumerate(order):
        v = F['F5_actions'][a]
        kept = v['kept']
        if kept:
            dec = np.array([r['dec'] for r in kept], float)
            for d, col in ((0, SRC_COL['S']), (1, SRC_COL['B'])):
                x0 = j + (d - 0.5) * 0.36
                ax2.bar(x0, dec[:, d].mean() - base[d], 0.32, color=col, ec='white', zorder=2)
                ax2.plot([x0, x0], [np.percentile(dec[:, d], 10) - base[d], np.percentile(dec[:, d], 90) - base[d]],
                         color=INK, lw=1.0, zorder=3)
        else:
            ax2.text(j, 0.3, 'none\nconsistent', ha='center', va='bottom', color=MUTED, fontsize=FS - 1.0)
    ax2.set_xticks(range(len(order)))
    ax2.set_xticklabels([short[a] + f"\n{F['F5_actions'][a]['consistent']}/{F['F5_actions'][a]['candidates']}" for a in order],
                        fontsize=FS - 1.0)
    ax2.axhline(0, color=INK, lw=0.6)
    ax2.set_ylabel('expected decisions gained')
    ax2.set_title('b  Characterising an end-member', loc='left', fontsize=9.0)
    style(ax2, 'y')
    hs = [Rectangle((0, 0), 1, 1, color=SRC_COL['S']), Rectangle((0, 0), 1, 1, color=SRC_COL['B'])]
    fig.legend(hs, ['seawater the main source?', 'brine more than 10%?'], loc='lower center', ncol=2, frameon=False,
               bbox_to_anchor=(0.5, 0.0))
    save(fig, out, 'fig_next')


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'res_field', 'figs')
    os.makedirs(out, exist_ok=True)
    which = sys.argv[2:] or ['tracers', 'synth', 'field', 'decide', 'compare', 'next']
    if 'tracers' in which:
        fig_tracers(out)
    if 'synth' in which and os.path.exists(os.path.join(HERE, 'res', 'wrr_synth.json')):
        fig_synth(out)
    if 'field' in which:
        fig_field(out)
    if 'decide' in which:
        fig_decide(out)
    if 'compare' in which:
        fig_compare(out, ['340-L', '341-S', '868-HH', '898-AA', 'Long Beach-3 #5', 'Wilmington-2 #2', '331-A',
                          'Wilmington-1 #3', '351-M'])
    if 'next' in which:
        fig_next(out)
    print('figures in', out)
