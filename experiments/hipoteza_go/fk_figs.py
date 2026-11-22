"""Figures of the Fushe-Kuqe HIPOTEZA-GO note (English labels, smallest text 8.6 pt at 17 cm).
usage: python fk_figs.py OUT_DIR [section calib libs shares]   (needs res_fk/ensemble_fk.npz and fk_results_*.json)"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.colors import LogNorm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fk_core as F  # noqa: E402
import fk_infer as I  # noqa: E402
from hip_figs import style, INK, MUTED, GRID, FS, MM, COL  # noqa: E402

RES = os.path.join(HERE, 'res_fk')
GREY, BLUE, ORANGE = '#b8bec6', '#2a78d6', '#eb6834'


def load(variant='second'):
    R = json.load(open(os.path.join(RES, f'fk_results_{variant}.json')))
    z = np.load(os.path.join(RES, 'ensemble_fk.npz'))
    ok = z['ok'] & np.isfinite(z['h_lit'])
    n = len(ok)
    E = {k: (z[k][ok] if (z[k].ndim and z[k].shape[0] == n) else z[k]) for k in z.files}
    return R, E


def theta_of(E, j):
    return {k: (int(E['th_' + k][j]) if k == 'member' else float(E['th_' + k][j])) for k in F.THETA_FK}


# ------------------------------------------------------------------------------------------------ the section
def fig_section(out, R, E):
    calib = dict(np.load(os.path.join(HERE, '..', '..', 'chloride_fk', 'results', 'calib_ensemble.npz')))
    mem = np.array(R['union_members']); kap = np.array(R['union_kappa'])
    j = int(mem[np.argmin(kap)])
    th = theta_of(E, j)
    M = F.member(th, calib)
    s = M['sec']
    tg = s.tagged()
    if M['n_an'] == 0:
        tg['G_AN'] = np.zeros(s.N)
    xk = s.xc / 1000.0
    ext = [0, s.nx * s.dx / 1000.0, F.ZMAX, 0]
    fields = [('a  Seawater fraction (steady state with the calibrated pumping)', s.c, 'Blues', (1e-3, 1.0)),
              ('b  Legacy salinity: chloride per unit release (footprint)', tg['G_RS'], 'YlOrBr', None),
              ('c  Deep saline water: chloride per unit flux (footprint)', tg['G_DB'], 'Purples', None)]
    fig = plt.figure(figsize=(170 * MM, 178 * MM))
    H_ = 0.19
    for n, (title, f, cmap, lim) in enumerate(fields):
        ax = fig.add_axes([0.085, 0.75 - n * (H_ + 0.04), 0.80, H_])
        A = np.where(s.act, f.reshape(s.nz, s.nx), np.nan)
        if lim is None:
            v = np.nanmax(A); lim = (max(v * 1e-3, 1e-12), v)
        im = ax.imshow(np.clip(A, lim[0], None), extent=ext, aspect='auto', cmap=cmap,
                       norm=LogNorm(vmin=lim[0], vmax=lim[1]), interpolation='nearest')
        ax.plot(xk, M['top'], color=INK, lw=0.7); ax.plot(xk, M['bot'], color=INK, lw=0.7)
        # the bands of the four analysed wells (screen classes of the chloride manuscript)
        for (wid, _, b, q), cols in zip(I.WELLS, R['bands']):
            cols = np.array(cols)
            x0, x1 = s.xc[cols.min()] / 1000 - 0.05, s.xc[cols.max()] / 1000 + 0.05
            if q == 1:
                zc = 0.5 * (M['top'][cols] + M['bot'][cols]); z0, z1 = zc.mean() - 20, zc.mean() + 20
            else:
                z0, z1 = M['top'][cols].mean(), M['top'][cols].mean() + 40
            ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fill=False, ec=INK, lw=0.8, ls=(0, (3, 2))))
        wf = s.wf_cols
        ax.add_patch(Rectangle((s.xc[wf.min()] / 1000 - 0.05, M['top'][wf].mean()), (wf.max() - wf.min() + 1) * s.dx / 1000,
                               0.6 * (M['bot'][wf] - M['top'][wf]).mean(), fill=False, ec=ORANGE, lw=1.0))
        ax.set_ylim(F.ZMAX, 0); ax.set_xlim(0, ext[1])
        ax.set_ylabel('depth below sea level (m)'); ax.set_title(title, loc='left')
        if n == 2:
            ax.set_xlabel('distance from the shoreline of the section (km)')
        else:
            ax.set_xticklabels([])
        cax = fig.add_axes([0.895, 0.75 - n * (H_ + 0.04), 0.015, H_])
        cb = fig.colorbar(im, cax=cax); cb.ax.tick_params(labelsize=FS - 0.6)
        if n == 0:
            for (wid, _, b, q), cols in zip(I.WELLS, R['bands']):
                cols = np.array(cols)
                xm = s.xc[cols].mean() / 1000
                lab = {'sw': '503, 341 (second aquifer)', 'c': '340 (first aquifer)', 'ne': '193'}[b]
                if wid in ('341',):
                    continue
                ax.text(xm, 4, lab, ha='center', va='top', fontsize=FS - 0.6, color=INK)
            ax.text(s.xc[wf].mean() / 1000, M['top'][wf].mean() + 0.6 * (M['bot'][wf] - M['top'][wf]).mean() + 4,
                    'well field', ha='center', va='top', fontsize=FS - 0.6, color=ORANGE)
    # heads along the aquifer top
    ax = fig.add_axes([0.085, 0.065, 0.80, 0.125])
    h0, *_ = s.flow(s.c, Qw=0.0)
    ax.plot(xk, s.head_top(), color=BLUE, lw=1.4, label='with the calibrated pumping')
    ax.plot(xk, s.head_top(h0), color=INK, lw=1.0, ls='--', label='without pumping')
    ax.axhline(M['ground'], color=MUTED, lw=0.8, ls=':', label='ground (member)')
    xw = s.xc[s.wf_cols].mean() / 1000
    sw = (E['dist'] >= F.BANDS['sw'][0]) & (E['dist'] <= F.BANDS['sw'][1])
    ax.errorbar([np.median(s.xc[sw]) / 1000], [3.0], yerr=[2.5], fmt='s', color=INK, ms=4, capsize=2, lw=0.8)
    ax.errorbar([xw], [M['ground'] + 1.5], yerr=[2.5], fmt='o', color=BLUE, ms=4, capsize=2, lw=0.8)
    ax.errorbar([xw + 0.12], [M['ground'] + 8.0], yerr=[3.75], fmt='o', mfc='white', color=INK, ms=4, capsize=2, lw=0.8)
    ax.set_xlim(0, ext[1]); ax.set_ylabel('head (m a.s.l.)')
    ax.set_title('d  Head at the top of the aquifer, and the documented facts (tolerance bars)', loc='left')
    ax.set_xlabel('distance from the shoreline of the section (km)')
    ax.legend(loc='upper left', frameon=False, fontsize=FS - 0.6, ncol=1)
    style(ax, 'y')
    fig.savefig(os.path.join(out, 'fk_section.png'), dpi=300); plt.close(fig)
    return dict(member=j, theta=th, toe02=M['toe02'], Qw=M['Qw'], h_lit=M['h_lit'], h_wf=M['h_wf'],
                h_wf0=M['h_wf0'], ground=M['ground'])


# ------------------------------------------------------------------------------------------------ calibration
def fig_calib(out, R, E):
    kh = np.array(R['kappa_head']); kres = R['loo']['kappa_res']
    kf = np.array(R['kappa_full'])
    hv = I.head_values(E)
    ok_h = kh <= kres
    un = np.zeros(len(kh), bool); un[R['union_members']] = True
    fig = plt.figure(figsize=(170 * MM, 74 * MM))
    ax1 = fig.add_axes([0.075, 0.27, 0.39, 0.62]); ax2 = fig.add_axes([0.585, 0.27, 0.39, 0.62])
    for sel, col, ms, z, lab in ((~ok_h, GREY, 2.0, 1, 'all simulations'),
                                 (ok_h & ~un, BLUE, 3.2, 2, 'consistent with the three head facts'),
                                 (un, ORANGE, 4.0, 3, 'and with the chloride of the four wells')):
        ax1.plot(hv['h_wf0_ag'][sel], hv['h_wf_ag'][sel], 'o', ms=ms, color=col, alpha=0.8, mew=0, zorder=z, label=lab)
        ax2.plot(E['th_Qin'][sel], E['Qw'][sel], 'o', ms=ms, color=col, alpha=0.8, mew=0, zorder=z)
    ax2.plot([0, 80], [0, 0.95 * 80], color=MUTED, lw=0.8, ls=':', zorder=0)
    ax1.add_patch(Rectangle((8.0 - 2.5 * 1.5 * kres, 1.5 - 2.5 * kres), 2 * 2.5 * 1.5 * kres, 2 * 2.5 * kres, fill=False,
                            ec=INK, lw=0.8, ls='--', zorder=4))
    ax1.set_xlim(-2, 25); ax1.set_ylim(-6, 20)
    ax1.set_xlabel('well-field head above ground without pumping (m)')
    ax1.set_ylabel('with pumping (m)')
    ax1.set_title('a  The documented decline: 8.0 → 1.5 m', loc='left'); style(ax1, 'both')
    ax2.set_xlim(0, 82); ax2.set_ylim(0, 80)
    ax2.set_xlabel('inland inflow (m²/d per metre)'); ax2.set_ylabel('pumping (m²/d per metre)')
    ax2.set_title('b  Calibrated inflow and pumping', loc='left'); style(ax2, 'both')
    fig.legend(loc='lower center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.0), handletextpad=0.3,
               columnspacing=1.6, markerscale=1.6, *ax1.get_legend_handles_labels())
    fig.savefig(os.path.join(out, 'fk_calib.png'), dpi=300); plt.close(fig)


# ------------------------------------------------------------------------------------------------ the coupling
def fig_couple(out):
    """What the sea delivers to well 340 against what it leaves at wells 503 and 341, for the two screen
    assignments of wells 503 and 341."""
    fig = plt.figure(figsize=(170 * MM, 80 * MM))
    info = {}
    for n, (var, title) in enumerate((('second', 'a  503, 341 in the second aquifer (D2)'),
                                      ('shallow', 'b  503, 341 in the first aquifer'))):
        D = json.load(open(os.path.join(RES, f'fk_diag_{var}.json')))
        ax = fig.add_axes([0.095 + n * 0.49, 0.30, 0.39, 0.58])
        x0, y0 = D['need340_min'], D['need_sw_max']
        ax.add_patch(Rectangle((x0, 1e-4), 1.0 - x0, y0 - 1e-4, fc='#e8f0fb', ec='none', zorder=0))
        for key, mk, kw in (('unconverged', 'o', dict(mfc='none', color=MUTED, ms=3.4, mew=0.7)),
                            ('converged', 'o', dict(color=BLUE, ms=3.0, mew=0, alpha=0.85))):
            c = D[key]
            xv = np.clip(np.array(c['x']), 1e-6, None); yv = np.clip(np.array(c['y']), 1e-4, None)
            ax.plot(xv, yv, mk, lw=0, zorder=2, **kw)
        ax.axvline(x0, color=INK, lw=0.8, ls='--'); ax.axhline(y0, color=INK, lw=0.8, ls='--')
        ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlim(1e-6, 1.0); ax.set_ylim(1e-4, 1.0)
        ax.set_xlabel('most seawater the sea brings to the band of 340')
        if n == 0:
            ax.set_ylabel('least seawater it leaves at 503 and 341')
        nin = D['converged']['feasible_all'] + D['unconverged']['feasible_all']
        ax.text(0.03, 0.97, f'sea explains all four wells:\n{D["converged"]["feasible_all"]} of {D["converged"]["n"]} simulations',
                transform=ax.transAxes, ha='left', va='top', fontsize=FS - 0.6, color=INK)
        ax.set_title(title, loc='left', fontsize=9.0); style(ax, 'both')
        info[var] = nin
    hs = [Line2D([0], [0], marker='o', color=BLUE, lw=0, ms=4), Line2D([0], [0], marker='o', mfc='none', color=MUTED, lw=0, ms=4),
          Rectangle((0, 0), 1, 1, fc='#e8f0fb', ec='none'), Line2D([0], [0], color=INK, lw=0.8, ls='--')]
    fig.legend(hs, ['simulation reproducing the heads', 'not converged (discarded, shown as a check)',
                    'sea alone explains 340, 503 and 341', 'what the wells need'],
               loc='lower center', ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.0), fontsize=FS - 0.4, columnspacing=2.0)
    fig.savefig(os.path.join(out, 'fk_couple.png'), dpi=300); plt.close(fig)
    return info


# ------------------------------------------------------------------------------------------------ libraries
def fig_libs(out, R):
    kres = R['loo']['kappa_res']
    L = sorted(R['libraries'], key=lambda d: (len(d['lib']), d['kappa_min']))
    fig = plt.figure(figsize=(170 * MM, 92 * MM))
    ax = fig.add_axes([0.31, 0.14, 0.66, 0.80])
    for n, d in enumerate(L):
        v = d['kappa_min'] / kres
        col = BLUE if d['feasible'] else GREY
        ax.barh(n, v, color=col, height=0.7, zorder=2)
        txt = f'{v:.2f}' + (' (at least)' if d['censored'] else '')
        ax.text(v * 1.06, n, txt, va='center', fontsize=FS - 0.8, color=INK)
    ax.axvline(1.0, color=INK, lw=0.8, ls='--')
    ax.set_xscale('log'); ax.set_xlim(0.01, 40)
    ax.set_yticks(range(len(L))); ax.set_yticklabels([' + '.join(d['lib']) for d in L], fontsize=FS - 0.6)
    ax.invert_yaxis()
    ax.set_xlabel('smallest tolerance needed / threshold κ (falsified above 1)')
    style(ax, 'x')
    fig.savefig(os.path.join(out, 'fk_libs.png'), dpi=300); plt.close(fig)


# ------------------------------------------------------------------------------------------------ shares
def completed_shares(R, variant='second'):
    p = os.path.join(RES, f'fk_sparse_{variant}.json')
    if os.path.exists(p):
        d = json.load(open(p))
        if 'full' in d:
            return d['full']
    return R['shares']


def fig_shares(out, R, shares=None):
    shares = shares or R['shares']
    srcs = ['MS', 'LG', 'AN', 'RS', 'DB']
    fig = plt.figure(figsize=(170 * MM, 70 * MM))
    for n, (wid, yv, b, q) in enumerate(I.WELLS):
        ax = fig.add_axes([0.075 + n * 0.235, 0.24, 0.20, 0.62])
        d = shares[wid]
        for m_, k in enumerate(srcs):
            v = d.get(k)
            if v is None:
                continue
            lo, hi = v
            ax.add_patch(Rectangle((lo, m_ - 0.32), max(hi - lo, 0.012), 0.64, fc=COL[k], ec='none'))
        ax.set_xlim(0, 1); ax.set_ylim(len(srcs) - 0.5, -0.5)
        ax.set_yticks(range(len(srcs))); ax.set_yticklabels(srcs if n == 0 else [])
        ax.set_xticks([0, 0.5, 1]); ax.set_xticklabels(['0', '0.5', '1'])
        ax.set_title(f'{"abcd"[n]}  well {wid}, {yv:,.0f} mg/L', loc='left', fontsize=9.0)
        ax.set_xlabel('share of chloride'); style(ax, 'x')
    fig.savefig(os.path.join(out, 'fk_shares.png'), dpi=300); plt.close(fig)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, 'figs')
    os.makedirs(out, exist_ok=True)
    which = sys.argv[2:] or ['section', 'calib', 'libs', 'shares']
    R, E = load(os.environ.get('FK_VARIANT', 'second'))
    if 'section' in which:
        print(fig_section(out, R, E))
    if 'calib' in which:
        fig_calib(out, R, E)
    if 'couple' in which:
        print(fig_couple(out))
    if 'libs' in which:
        fig_libs(out, R)
    if 'shares' in which:
        fig_shares(out, R)
    print('figures in', out)
