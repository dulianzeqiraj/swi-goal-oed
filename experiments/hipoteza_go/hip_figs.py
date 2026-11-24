"""Figures of the HIPOTEZA-GO note (English labels, smallest text 8.6 pt at 17 cm).
usage: python hip_figs.py OUT_DIR
fig_fields   the section: seawater wedge and the footprint of every candidate source (one member of the class)
fig_decide   origin identified and sources excluded, by data scenario, with and without the physics
fig_example  one truth: identified intervals with the physics, without it, and the true shares
fig_terms    hypotheses as terms: tolerance needed by the reduced libraries
fig_dyn      pumping histories against the steady states of the extreme pumping rates"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hip_core as H  # noqa: E402
import hip_infer as I  # noqa: E402

INK, MUTED, GRID = '#1f2328', '#5b6672', '#e3e6ea'
FS = 8.6
plt.rcParams.update({'font.size': FS, 'axes.titlesize': 9.2, 'axes.labelsize': FS, 'xtick.labelsize': FS,
                     'ytick.labelsize': FS, 'legend.fontsize': FS, 'font.family': 'DejaVu Sans',
                     'mathtext.fontset': 'dejavusans', 'axes.edgecolor': '#8b949e', 'axes.linewidth': 0.6,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.titlelocation': 'left',
                     'axes.titleweight': 'bold'})
MM = 1 / 25.4
# validated categorical order (dataviz validator, light surface): blue, orange, green, magenta, yellow, violet
COL = {'MS': '#2a78d6', 'AN': '#eb6834', 'FW': '#1baf7a', 'LG': '#c43e8f', 'RS': '#eda100', 'DB': '#6250d6'}
HIP, MIX = '#2a78d6', '#8a9099'


def style(ax, grid='y'):
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(length=2.5)


def load():
    return json.load(open(os.path.join(HERE, 'res', 'hipoteza.json')))


# ------------------------------------------------------------------------------------------------ fig_fields
def fig_fields(out):
    th = dict(Kx=110.0, aniso=0.04, Qin=3.2, rQ=0.35, vL=1.5e-4, sL=0.6, aL=40.0, aT=1.5)
    s = H.section_of(th)
    for (m, beta, maxit) in ((8, 0.5, 250), (20, 0.2, 450)):
        s.solve_steady(m=m, beta=beta, maxit=maxit)
        if s.dc < 1e-6:
            break
    tg = s.tagged()
    S = dict(MS=20500.0, LG=12000.0, AN=0.10, RS=0.008, DB=0.5)
    fields = [('MS', 'a  Modern seawater (the wedge)', S['MS'] * tg['W_MS']),
              ('LG', 'b  Lagoon water (leakage through the top)', S['LG'] * tg['W_LG']),
              ('AN', 'c  Anthropogenic chloride (flux through the top)', S['AN'] * tg['G_AN']),
              ('RS', 'd  Legacy salinity (release in the lower central zone)', S['RS'] * tg['G_RS']),
              ('DB', 'e  Deep saline water (flux through the base)', S['DB'] * tg['G_DB'])]
    fig = plt.figure(figsize=(170 * MM, 132 * MM))
    x = np.linspace(0, H.L / 1000, H.NX + 1); z = np.linspace(0, H.B, H.NZ + 1)
    for n, (k, title, f) in enumerate(fields):
        ax = fig.add_axes([0.075, 0.825 - n * 0.183, 0.80, 0.125])
        F = np.maximum(f.reshape(H.NZ, H.NX), 1.0)
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list('c', ['#ffffff', COL[k]])
        pc = ax.pcolormesh(x, z, np.log10(F), cmap=cmap, vmin=1.0, vmax=4.3 if k in ('MS', 'LG') else 3.0, rasterized=True)
        ax.invert_yaxis(); ax.set_ylabel('depth (m)')
        ax.set_title(title, loc='left', fontsize=9.0, pad=3)
        for xw in H.WELL_X:
            for (z0, z1) in H.SCREENS:
                ax.plot([xw / 1000, xw / 1000], [z0, z1], color=INK, lw=1.6, solid_capstyle='butt')
        fz = H.ZONES['field']
        ax.add_patch(Rectangle((fz[0] / 1000, fz[2]), (fz[1] - fz[0]) / 1000, fz[3] - fz[2], fc='none', ec=INK, lw=0.9,
                               ls=':'))
        if n < len(fields) - 1:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel('distance from the sea (km)')
        cax = fig.add_axes([0.89, 0.825 - n * 0.183, 0.014, 0.125])
        cb = fig.colorbar(pc, cax=cax); cb.outline.set_visible(False)
        tk = [1, 2, 3, 4] if k in ('MS', 'LG') else [1, 2, 3]
        cb.set_ticks(tk); cb.set_ticklabels([f'{10 ** t:,.0f}' for t in tk])
        cb.ax.tick_params(labelsize=FS - 0.6, length=2)
        if n == 0:
            cax.set_title('Cl (mg/L)', fontsize=FS - 0.4, loc='left', pad=4, fontweight='normal')
    fig.savefig(os.path.join(out, 'fig_fields.png'), dpi=300); plt.close(fig)
    return dict(toe02=s.toe(0.02), toe50=s.toe(0.5), theta=th, strengths=S)


# ------------------------------------------------------------------------------------------------ fig_decide
def agg(rows, key, scen):
    num = lambda f: sum(f(r['scen'][scen][key]) for r in rows)
    n = num(lambda m: m['n_sal'])
    return dict(n=n, identified=num(lambda m: m['identified']), wrong_id=num(lambda m: m['wrong_id']),
                excluded=num(lambda m: m['excluded']), wrong_excl=num(lambda m: m['wrong_excl']),
                pairs=num(lambda m: m['pairs']), covered=num(lambda m: m['covered']),
                width=float(np.mean(sum((r['scen'][scen][key]['width'] for r in rows), []) or [np.nan])),
                ms_decided=num(lambda m: m['ms_decided']), ms_wrong=num(lambda m: m['ms_wrong']))


def fig_decide(out, R):
    scen = list(I.SCEN.keys())
    rows = R['H2']
    fig = plt.figure(figsize=(170 * MM, 84 * MM))
    ax1 = fig.add_axes([0.075, 0.37, 0.40, 0.53]); ax2 = fig.add_axes([0.575, 0.37, 0.40, 0.53])
    w = 0.36
    for j, sc in enumerate(scen):
        h, m = agg(rows, 'hip', sc), agg(rows, 'mix', sc)
        for (a, off, col) in ((h, -w / 2, HIP), (m, w / 2, MIX)):
            v1 = a['identified'] / max(a['n'], 1); v2 = a['excluded'] / max(a['n'], 1)
            ax1.bar(j + off, v1, w * 0.92, color=col, ec='white', lw=0.6, zorder=2)
            ax1.text(j + off, v1 + 0.02, f'{100 * v1:.0f}%', ha='center', va='bottom', color=INK, fontsize=FS - 0.6)
            ax2.bar(j + off, v2, w * 0.92, color=col, ec='white', lw=0.6, zorder=2)
            ax2.text(j + off, v2 + 0.05, f'{v2:.1f}', ha='center', va='bottom', color=INK, fontsize=FS - 0.6)
    lab = ['A\nCl,\n4 wells', 'B\nCl,\n10 wells', 'C\n+ Br, δ¹⁸O,\ntritium', 'D\n+ end-\nmembers']
    for ax, t, yl, ymax in ((ax1, 'a  Origin identified', 'share of salinised samples', 1.12),
                            (ax2, 'b  Sources excluded', 'per salinised sample (of 4)', 4.4)):
        ax.set_xticks(range(len(scen))); ax.set_xticklabels(lab)
        ax.set_title(t, loc='left'); ax.set_ylabel(yl); ax.set_ylim(0, ymax); style(ax, 'y')
    hs = [Rectangle((0, 0), 1, 1, color=HIP), Rectangle((0, 0), 1, 1, color=MIX)]
    fig.legend(hs, ['with the physics (HIPOTEZA-GO)', 'mixing only, sample by sample (ZANAFILLA-GO)'], loc='lower center',
               ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.savefig(os.path.join(out, 'fig_decide.png'), dpi=300); plt.close(fig)


# ------------------------------------------------------------------------------------------------ fig_example
def pick_example(R):
    """The truth shown: complete unions (scenario B), every source present, a full population of the union, and
    then the most salinised samples."""
    rows = [r for r in R.get('H2full', []) if 'example' in r]
    key = lambda r: (sum(v > 0 for v in r['S'][3:5]), r['n_nroy'] >= R['H1'].get('n_min', 39),
                     sum(c > 100 for c in r['cl']))
    return max(rows, key=key)


def fig_example(out, R):
    r = pick_example(R)
    ex = r['example']
    lo, hi, mlo, mhi, share = (np.array(ex[k]) for k in ('lo', 'hi', 'mlo', 'mhi', 'share'))
    cl = np.array(r['cl'])
    sal = [i for i in range(I.NS) if cl[i] > 100 and lo[i, 0] >= 0]
    srcs = [(0, 'MS'), (3, 'AN'), (4, 'RS')]
    n = len(sal)
    Hmm = 31 + 5.2 * n
    fig = plt.figure(figsize=(170 * MM, Hmm * MM))
    top = 1 - 10 / Hmm; bot = 19 / Hmm
    x0, wd, gap = 0.255, 0.215, 0.030
    for c, (k, name) in enumerate(srcs):
        ax = fig.add_axes([x0 + c * (wd + gap), bot, wd, top - bot])
        for rw, i in enumerate(sal):
            y = n - 1 - rw
            if mlo[i, k] >= 0:
                ax.add_patch(Rectangle((mlo[i, k], y - 0.36), max(mhi[i, k] - mlo[i, k], 0.006), 0.26, fc=MIX, ec='none'))
            ax.add_patch(Rectangle((lo[i, k], y + 0.02), max(hi[i, k] - lo[i, k], 0.006), 0.30, fc=COL[name], ec='none'))
            ax.plot([share[i, k]], [y + 0.17], marker='|', color=INK, ms=9, mew=1.4, zorder=5, clip_on=False)
            if c == 0:
                w_, s_ = divmod(i, 2)
                ax.text(-0.06, y, f'{H.WELL_X[w_] / 1000:.1f} km, {"upper" if s_ == 0 else "lower"}', ha='right',
                        va='center', transform=ax.get_yaxis_transform(), color=INK)
                ax.text(-0.78, y, f'{cl[i]:,.0f}', ha='right', va='center', transform=ax.get_yaxis_transform(),
                        color=MUTED)
        ax.set_xlim(0, 1); ax.set_ylim(-0.6, n - 0.4); ax.set_yticks([])
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_xticklabels(['0', '', '0.5', '', '1'])
        ax.set_title(f'{"abc"[c]}  {I.NAMES[name].capitalize()}', loc='left', fontsize=9.0)
        ax.set_xlabel('share of chloride'); style(ax, 'x')
        if c == 0:
            ax.text(-0.06, n - 0.35, 'well, screen', ha='right', va='bottom', transform=ax.get_yaxis_transform(),
                    color=MUTED)
            ax.text(-0.78, n - 0.35, 'Cl, mg/L', ha='right', va='bottom', transform=ax.get_yaxis_transform(),
                    color=MUTED)
    hs = [Rectangle((0, 0), 1, 1, color=COL['MS']), Rectangle((0, 0), 1, 1, color=COL['AN']),
          Rectangle((0, 0), 1, 1, color=COL['RS']), Rectangle((0, 0), 1, 1, color=MIX),
          Line2D([0], [0], marker='|', color=INK, lw=0, ms=9, mew=1.4)]
    fig.legend(hs, ['with the physics:  seawater', 'anthropogenic', 'legacy', 'mixing only', 'true share'],
               loc='lower center', ncol=5, frameon=False, bbox_to_anchor=(0.5, 0.0), columnspacing=1.2,
               handlelength=1.4)
    fig.savefig(os.path.join(out, 'fig_example.png'), dpi=300); plt.close(fig)
    return dict(truth=r['n'], S=r['S'], toe02=r['toe02'], n_union=r['n_nroy'], n_sal=n)


# ------------------------------------------------------------------------------------------------ fig_terms
def fig_terms(out, R, upto=3.0, cut=2.5):
    scen = list(I.SCEN.keys())
    kres = R['H1']['kappa_res']
    fig = plt.figure(figsize=(170 * MM, 88 * MM))
    ax1 = fig.add_axes([0.085, 0.37, 0.39, 0.54]); ax2 = fig.add_axes([0.585, 0.37, 0.39, 0.54])
    rng = np.random.default_rng(1)
    for j, sc in enumerate(scen):
        for (key, k, col, off) in (('k_noAN', 3, COL['AN'], -0.18), ('k_noRS', 4, COL['RS'], 0.18)):
            for r in R['H2']:
                if r['scen'][sc]['falsified']:
                    continue
                raw = r['scen'][sc][key]
                present = r['S'][k] > 0
                mk = 'x' if not present else ('^' if raw >= upto else 'o')
                ax1.plot(j + off + rng.uniform(-0.08, 0.08), min(raw / kres[sc], 30), mk, color=col,
                         ms=4.6 if mk == 'x' else 4.2, mew=1.0, mfc='none' if mk == 'x' else col, alpha=0.9, zorder=3)
    ax1.axhline(1.0, color=INK, lw=0.8, ls='--')
    ax1.set_yscale('log'); ax1.set_ylim(0.3, 40)
    ax1.set_ylabel('tolerance needed / threshold κ')
    ax1.set_title('a  Is the term necessary?', loc='left')
    lab = ['A', 'B', 'C', 'D']
    ax1.set_xticks(range(len(scen))); ax1.set_xticklabels(lab); ax1.set_xlabel('data scenario'); style(ax1, 'y')
    # missing source
    for j, sc in enumerate(scen):
        for r in R['H4']:
            raw = r['scen'][sc]['kappa_min']
            ax2.plot(j + rng.uniform(-0.14, 0.14), min(raw / kres[sc], 30), '^' if raw >= cut else 'o', color=COL['DB'],
                     ms=4.2, alpha=0.9, zorder=3)
    ax2.axhline(1.0, color=INK, lw=0.8, ls='--')
    ax2.set_yscale('log'); ax2.set_ylim(0.3, 40)
    ax2.set_xticks(range(len(scen))); ax2.set_xticklabels(lab); ax2.set_xlabel('data scenario'); style(ax2, 'y')
    ax2.set_title('b  Is a source missing?', loc='left')
    hs = [Line2D([0], [0], marker='o', color=COL['AN'], lw=0, ms=4.6), Line2D([0], [0], marker='o', color=COL['RS'], lw=0, ms=4.6),
          Line2D([0], [0], marker='o', color=COL['DB'], lw=0, ms=4.6),
          Line2D([0], [0], marker='^', color=MUTED, lw=0, ms=4.6), Line2D([0], [0], marker='x', color=MUTED, lw=0, mew=1.0, ms=4.8),
          Line2D([0], [0], color=INK, lw=0.8, ls='--')]
    fig.legend(hs, ['library without the anthropogenic term', 'library without the legacy term',
                    'library without the deep source', 'lower bound of the tolerance needed',
                    'the source is absent in the truth', 'the library is falsified above this line'],
               loc='lower center', ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.0), columnspacing=3.0,
               labelspacing=0.35)
    fig.savefig(os.path.join(out, 'fig_terms.png'), dpi=300); plt.close(fig)


# ------------------------------------------------------------------------------------------------ fig_dyn
def fig_dyn(out):
    D = json.load(open(os.path.join(HERE, 'res', 'dyn.json')))
    t = np.array(D['rec_years'])
    Wlo, Whi = np.array(D['W_lo']), np.array(D['W_hi'])
    # the two samples with the largest difference between the two steady states
    order = np.argsort(Whi - Wlo)[::-1][:2]
    fig = plt.figure(figsize=(170 * MM, 80 * MM))
    for c, i in enumerate(order):
        ax = fig.add_axes([0.075 + c * 0.335, 0.33, 0.27, 0.56])
        for r in D['runs']:
            W = np.array(r['W'])[:, i]
            special = r['seed'] < 0
            ax.plot(t, W, color=COL['AN'] if special else HIP, lw=1.3 if special else 0.7,
                    alpha=1.0 if special else 0.55, zorder=3 if special else 2)
        ax.axhline(Whi[i], color=INK, lw=0.9, ls='--'); ax.axhline(Wlo[i], color=INK, lw=0.9, ls=':')
        w_, s_ = divmod(int(i), 2)
        ax.set_title(f'{"ab"[c]}  {H.WELL_X[w_] / 1000:.1f} km, {"upper" if s_ == 0 else "lower"} screen', loc='left',
                     fontsize=9.0)
        ax.set_xlabel('years'); style(ax, 'y')
        if c == 0:
            ax.set_ylabel('seawater fraction')
    ax = fig.add_axes([0.075 + 2 * 0.335, 0.33, 0.235, 0.56])
    for r in D['runs']:
        special = r['seed'] < 0
        ax.plot(t, np.array(r['toe']) / 1000, color=COL['AN'] if special else HIP, lw=1.3 if special else 0.7,
                alpha=1.0 if special else 0.55)
    ax.axhline(D['toe_hi'] / 1000, color=INK, lw=0.9, ls='--'); ax.axhline(D['toe_lo'] / 1000, color=INK, lw=0.9, ls=':')
    ax.set_title('c  Toe (2% line), km', loc='left', fontsize=9.0); ax.set_xlabel('years')
    style(ax, 'y')
    hs = [Line2D([0], [0], color=HIP, lw=0.9), Line2D([0], [0], color=COL['AN'], lw=1.3),
          Line2D([0], [0], color=INK, lw=0.9, ls='--'), Line2D([0], [0], color=INK, lw=0.9, ls=':')]
    fig.legend(hs, ['random pumping histories', 'constant and bang-bang histories', 'steady state, highest pumping',
                    'steady state, lowest pumping'], loc='lower center', ncol=2, frameon=False,
               bbox_to_anchor=(0.5, 0.0), fontsize=FS)
    fig.savefig(os.path.join(out, 'fig_dyn.png'), dpi=300); plt.close(fig)
    return D


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'res', 'figs')
    os.makedirs(out, exist_ok=True)
    which = sys.argv[2:] or ['fields', 'decide', 'example', 'terms', 'dyn']
    R = load() if any(w in which for w in ('decide', 'example', 'terms')) else None
    if 'fields' in which:
        print(fig_fields(out))
    if 'decide' in which:
        fig_decide(out, R)
    if 'example' in which:
        print(fig_example(out, R))
    if 'terms' in which:
        fig_terms(out, R)
    if 'dyn' in which and os.path.exists(os.path.join(HERE, 'res', 'dyn.json')):
        fig_dyn(out)
    print('figures in', out)
