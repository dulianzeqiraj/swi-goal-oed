"""Figure 1 of the research note "PRAG-GO and PRAG-MAR at Fushe-Kuqe" (version 2): the sea boundary.

(a) The companion model (fk.py): the whole western margin drains to the sea. Intruded zone at the
    prior mean, the supply wells of the first version (A23, R16) and the published MAR sites.
(b) The geolocated boundary (fk_geo.py): sea contact only on the northern 23 km, coastal sector
    y >= 24 km. Intruded zone at the prior mean without pumping and with the two supply wells
    A1 and P10 pumped as in fk_mar_geo.py (res_geo/mar_geo_fields.npz, field h0p).
Figures 2 and 3 of the note are Supplementary Figs. S2 and S1 of the chloride study
(chloride_fk/python/fkcl_figs.py), drawn from res_geo/.
With --paper the same figure is drawn as Fig. 9 of the chloride paper (panel titles without the
note's version dates, file fig9_boundary); MATLAB: chloride_fk/matlab/fkcl_boundary_figure.m.

Usage: python3 fk_geo_figs.py [outdir] [--paper]      (default: fig/; ~10 s)
       python3 fk_geo_figs.py ../../chloride_fk/figures --paper     (Fig. 9 of the paper)
"""
import os
import sys
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'chloride_fk', 'python'))
PAPER = '--paper' in sys.argv[1:]
_pos = [a for a in sys.argv[1:] if not a.startswith('--')]
OUTDIR = _pos[0] if _pos else os.path.join(HERE, 'fig')
NAME = 'fig9_boundary' if PAPER else 'fig1_boundary'
_argv, sys.argv = sys.argv, sys.argv[:1]          # fkcl_figs reads sys.argv at import
import fkcl_figs as CF                             # noqa: E402  style, Okabe-Ito colours, shoreline
sys.argv = _argv
import matplotlib.pyplot as plt                    # noqa: E402
from matplotlib import colors as mcolors           # noqa: E402
from matplotlib.lines import Line2D                # noqa: E402
from matplotlib.patches import Patch               # noqa: E402
from fk import FK, default_xlsx                    # noqa: E402
from fk_geo import FKGeo                           # noqa: E402

OI, MM, HC = CF.OI, CF.MM, 1.0
C_LAND, C_OUT, C_SALT, C_PUMP = '#EEF3EA', '#E4E4E4', '#0072B2', '#9CCBEA'


def grid(m, v):
    G = np.full((m.ny, m.nx), np.nan)
    G[m.aj, m.ai] = v
    return G


def edges(m):
    return (np.r_[m.xs - 0.5 * m.dx, m.xs[-1] + 0.5 * m.dx], np.r_[m.ys - 0.5 * m.dx, m.ys[-1] + 0.5 * m.dx])


def well_xy(m, wid):
    i = int(np.flatnonzero(m.wellID.astype(str) == wid)[0])
    return m.Wk[i, 0], m.Wk[i, 1]


def main():
    full = FK(default_xlsx()).design_fields()
    geo = FKGeo()
    F = np.load(os.path.join(HERE, 'res_geo', 'mar_geo_fields.npz'))
    J = json.load(open(os.path.join(HERE, 'res_geo', 'mar_geo.json')))
    xe, ye = edges(full)
    fig, axs = plt.subplots(1, 2, figsize=(128 * MM, 150 * MM))
    fig.subplots_adjust(left=0.1, right=0.99, bottom=0.2, top=0.9, wspace=0.06)
    lab = dict(textcoords='offset points', fontsize=6.5, zorder=10, bbox=dict(fc='white', ec='none', alpha=0.75, pad=0.4))

    # (a) full margin
    ax = axs[0]
    cls = np.where(full.h0 < HC, 2, 0).astype(float)
    ax.pcolormesh(xe, ye, grid(full, cls), cmap=mcolors.ListedColormap([C_LAND, C_PUMP, C_SALT]), vmin=0, vmax=2,
                  shading='flat', rasterized=True)
    sel = full.coastc
    o = np.argsort(full.cy[sel])
    ax.plot(full.cx[sel][o] - 0.5 * full.dx, full.cy[sel][o], color=OI[1], lw=1.6, zorder=6)
    for w, off, ha in (('A23', (7, 1), 'left'), ('R16', (-7, -3), 'right')):
        x, y = well_xy(full, w)
        ax.plot(x, y, 'v', ms=7, mfc=OI[4], mec='k', mew=0.6, zorder=9)
        ax.annotate(w, (x, y), xytext=off, ha=ha, **lab)
    for c, w in zip(full.marCell, full.marID):
        ax.plot(full.cx[c], full.cy[c], 'D', ms=5.5, mfc='white', mec='k', mew=1.0, zorder=9)
        ax.annotate(w, (full.cx[c], full.cy[c]), xytext=(6, -8), **lab)
    head_a = 'a  Companion model (Zeqiraj, 2026)' if PAPER else 'a  First version (12 Oct)'
    ax.set_title(f'{head_a}\nwhole western margin as sea\nintruded area {full.baseArea:.1f} km$^2$, no pumping',
                 loc='left', fontsize=7.5)

    # (b) geolocated boundary
    ax = axs[1]
    v = geo.valid
    cls = np.where(~v, 3, np.where(geo.h0 < HC, 2, np.where(F['h0p'] < HC, 1, 0))).astype(float)
    ax.pcolormesh(xe, ye, grid(geo, cls), cmap=mcolors.ListedColormap([C_LAND, C_PUMP, C_SALT, C_OUT]), vmin=0, vmax=3,
                  shading='flat', rasterized=True)
    sel = geo.seac
    o = np.argsort(geo.cy[sel])
    ax.plot(geo.cx[sel][o] - 0.5 * geo.dx, geo.cy[sel][o], color=OI[1], lw=1.6, zorder=6)
    ax.axhline(24.0, xmin=0.0, xmax=1.0, color='0.35', lw=0.6, ls=':', zorder=4)
    ax.text(-2.2, 23.6, 'sector limit\ny = 24 km', fontsize=6, ha='left', va='top', color='0.25')
    for s in ('A', 'B'):
        sp = J['supply'][s]
        ax.plot(sp['x'], sp['y'], 'v', ms=7, mfc=OI[4], mec='k', mew=0.6, zorder=9)
        ax.annotate(sp['id'], (sp['x'], sp['y']), xytext=(7, 3 if s == 'A' else -9), **lab)
    for c, w in zip(full.marCell, full.marID):
        inside = bool(v[c])
        ax.plot(full.cx[c], full.cy[c], 'D', ms=5.5, mfc='white' if inside else 'none', mec='k' if inside else '0.45',
                mew=1.0, zorder=9)
        ax.annotate(w + ('' if inside else '\n(no sea contact)'), (full.cx[c], full.cy[c]), xytext=(6, -12 if not inside else -8),
                    color='k' if inside else '0.35', **lab)
    a_p = float(geo.goalA(F['h0p']))                 # the model's intruded-area measure, as geo.baseArea
    head_b = 'b  This study (Section 2.3)' if PAPER else 'b  This version (19 Oct)'
    ax.set_title(f'{head_b}\ngeolocated Adriatic contact, 23 km\nintruded area {geo.baseArea:.1f} km$^2$; '
                 f'{a_p:.1f} km$^2$ with pumping', loc='left', fontsize=7.5)
    ax.set_yticklabels([])

    for ax in axs:
        ax.plot(full.Bk[:, 0], full.Bk[:, 1], color='0.15', lw=0.6, zorder=5)
        ax.set_xlim(-2.5, 17); ax.set_ylim(-1.5, 54.5); ax.set_aspect('equal')
        ax.set_xlabel('Easting from $x_0$ [km]')
    axs[0].set_ylabel('Northing from $y_0$ [km]')
    h = [Patch(fc=C_SALT, label='intruded at the prior mean ($h$ < 1 m)'),
         Patch(fc=C_PUMP, label='intruded only with the supply wells pumped'),
         Patch(fc=C_OUT, label='outside the model sector (b)'),
         Line2D([], [], color=OI[1], lw=1.6, label='sea boundary of the model'),
         Line2D([], [], marker='v', ls='', mfc=OI[4], mec='k', ms=7, label='supply wells'),
         Line2D([], [], marker='D', ls='', mfc='white', mec='k', ms=5.5, label='published MAR sites')]
    fig.legend(handles=h, loc='lower center', bbox_to_anchor=(0.5, 0.0), ncol=2, frameon=False, fontsize=6.3, columnspacing=1.0, handlelength=1.6)
    with open(os.path.join(HERE, 'res_geo', 'boundary_areas.json'), 'w') as fh:   # quoted in Section 4.7 of the paper
        json.dump({'full_margin_km2': float(full.baseArea), 'geolocated_km2': float(geo.baseArea),
                   'geolocated_pumped_km2': a_p, 'supply': [J['supply']['A']['id'], J['supply']['B']['id']],
                   'QA': J['pumping']['QA'], 'QB': J['pumping']['QB'],
                   'note': 'smoothed intrusion indicator of the companion code (s = 0.15 m), prior mean'}, fh, indent=1)
    os.makedirs(OUTDIR, exist_ok=True)
    for ext in ('png', 'pdf'):
        fig.savefig(os.path.join(OUTDIR, NAME + '.' + ext), dpi=400 if PAPER else 300, bbox_inches='tight')
    plt.close(fig)
    print(f'full margin {full.baseArea:.1f} km2; geolocated {geo.baseArea:.1f} km2, {a_p:.1f} km2 with pumping;'
          f' MAR sites {full.marID}; written to {os.path.abspath(OUTDIR)}')


if __name__ == '__main__':
    main()
