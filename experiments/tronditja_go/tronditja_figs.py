"""Figures of the TRONDITJA-GO note; English labels, every text at least 8.6 pt at the printed size.
usage: python tronditja_figs.py OUT_DIR

fig_chain    the method in one picture, with live mini-plots of the computed fields
fig_e1       E1: a CPT profile, CSR against CRR for three water tables, FS, the LPI integrand, LPI against the water table
fig_e2       E2: the head step of four published source models, their agreement, a transect, drainage, the natural test
fig_e3       E3: the 2019 hindcast designed on a synthetic coastal plain: map, ROC, power against the number of sites
fig_e4       E4: the joint window for liquefaction and intrusion at a low port, against sea level and acceleration
fig_e5       E4: the daily bulletin "if the earthquake happened today"
Numbers come from res/tronditja.json and res/tronditja_series.npz."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm, ListedColormap
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch
from matplotlib.ticker import FixedLocator, NullLocator
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', 'rindertimi_go'))
import gar_figs as GF  # noqa: E402
from rgo_figs import Canvas, INK, MUTED  # noqa: E402

RES = os.path.join(HERE, 'res')
MM, FS = GF.MM, GF.FS
BLUE, ORANGE, AQUA, VIOLET, REF = GF.BLUE, GF.ORANGE, GF.AQUA, GF.VIOLET, GF.REF
GREEN = '#1E6B35'
SAND, CLAY = '#e9d9a8', '#c9ccd3'
# diverging: head drop (blue) - neutral grey - head rise (orange-red); a rise brings the soil closer to liquefaction
DIV = LinearSegmentedColormap.from_list('dh', ['#163f73', '#2f6fb0', '#8fb8df', '#ececec', '#f4b183', '#df6a2e', '#9a3412'])
SEQ = LinearSegmentedColormap.from_list('win', ['#eef6f1', '#a7d7b8', '#4fa678', '#1e6b45', '#0f3d27'])
SRC_COL = dict(ganas=BLUE, matraku=ORANGE, govorcin=AQUA, vdheiden=VIOLET)
SRC_SHORT = dict(ganas='Ganas 2020', matraku='Matraku 2023', govorcin='Govorčin 2020', vdheiden='van der Heiden 2026')
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MSTART = np.cumsum([0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30])


def load():
    with open(os.path.join(RES, 'tronditja.json')) as fh:
        R = json.load(fh)
    return R, dict(np.load(os.path.join(RES, 'tronditja_series.npz')))


def fault_outline(src):
    st, dp = np.radians(src['strike']), np.radians(src['dip'])
    s = np.array([np.sin(st), np.cos(st)])
    d = np.array([np.cos(st), -np.sin(st)])                      # horizontal down-dip direction
    hw, hl = src['W_km'] * np.cos(dp) / 2, src['L_km'] / 2
    corners = np.array([-hl * s - hw * d, hl * s - hw * d, hl * s + hw * d, -hl * s + hw * d])
    return corners, corners[:2]                                  # rectangle, up-dip edge


def map_axes(ax, lim=30):
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect('equal')
    ax.set_xticks([-20, 0, 20]); ax.set_yticks([-20, 0, 20])
    for sp in ax.spines.values():
        sp.set_color('#8b949e'); sp.set_linewidth(0.6)
    ax.tick_params(length=2, labelsize=FS, colors=MUTED)


def draw_fault(ax, src, color=INK, lw=0.9):
    rect, top = fault_outline(src)
    ax.add_patch(Polygon(rect, closed=True, fill=False, ec=color, lw=lw, ls=(0, (3, 2)), zorder=6))
    ax.plot(top[:, 0], top[:, 1], color=color, lw=2.2, solid_capstyle='round', zorder=7)


# --------------------------------------------------------------------------------------------- chain
def fig_chain(out, R, Sx):
    from scipy.special import erf
    cv = Canvas(174, 96)
    boxes = [(2, 52, 54, 41, '1  Source ensemble', 'four published fault models'),
             (60, 52, 54, 41, '2  Coseismic head step', r'$\Delta h_0=-\kappa\,\Delta\varepsilon_a/\rho g$'),
             (118, 52, 54, 41, '3  Pressure during shaking', r'$u=\gamma_w(z-z_w)_+ + f\,\Delta p_0$'),
             (2, 3, 54, 41, '4  Safety factor and LPI', 'CSR and CRR (Boulanger–Idriss)'),
             (60, 3, 54, 41, '5  The joint window', 'liquefaction against intrusion'),
             (118, 3, 54, 41, '6  Daily bulletin', 'if the earthquake struck today')]
    for x, y, w, h, t, sub in boxes:
        cv.box(x, y, w, h, 'white', '#c3c8cf', lw=0.7, r=1.6, z=1)
        cv.text(x + 2.4, y + h - 3.4, t, ha='left', weight='bold', size=9.2)
        cv.text(x + 2.4, y + h - 8.0, sub, ha='left', size=FS, color=MUTED)
    for x0, x1, y in ((56.4, 59.6, 72), (114.4, 117.6, 72), (56.4, 59.6, 23), (114.4, 117.6, 23)):
        cv.arrow(x0, y, x1, y, c=MUTED, lw=1.1)
    cv.line([145, 145], [51.6, 48.0], c=MUTED, lw=1.1)
    cv.line([145, 29], [48.0, 48.0], c=MUTED, lw=1.1)
    cv.arrow(29, 48.0, 29, 44.6, c=MUTED, lw=1.1)
    srcs = R['E2']['sources']
    short = dict(ganas='Ganas', matraku='Matraku', govorcin='Govorčin', vdheiden='v. d. Heiden')
    a = cv.inset(3, 54, 25, 27)
    for s_ in srcs:
        draw_fault(a, s_, SRC_COL[s_['key']], lw=0.8)
    a.set_xlim(-15, 15); a.set_ylim(-14, 14); a.set_aspect('equal'); a.axis('off')
    cv.text(30, 80.0, 'model', ha='left', size=FS - 0.8, color=MUTED)
    cv.text(54, 80.0, 'dip', ha='right', size=FS - 0.8, color=MUTED)
    cv.line([30, 54], [78.0, 78.0], c='#d5d9de', lw=0.5)
    for k, s_ in enumerate(srcs):
        cv.text(30, 74.6 - 4.9 * k, short[s_['key']], ha='left', size=FS - 0.6, color=SRC_COL[s_['key']])
        cv.text(54, 74.6 - 4.9 * k, f"{s_['dip']:.0f}°", ha='right', size=FS - 0.6, color=SRC_COL[s_['key']])
    cv.text(30, 56.0, 'thick: top edge', ha='left', size=FS - 1.0, color=MUTED)
    a = cv.inset(61, 54, 29, 28)
    x = Sx['e2_x'] / 1e3
    a.imshow(Sx['e2_dh_mean'], extent=(x[0], x[-1], x[0], x[-1]), origin='lower', cmap=DIV, vmin=-0.8, vmax=0.8,
             interpolation='bilinear')
    a.contour(x, x, Sx['e2_dh_mean'], levels=[-0.25, 0.12], colors=[INK], linewidths=0.4)
    a.set_xlim(-30, 30); a.set_ylim(-30, 30); a.axis('off')
    cv.text(92, 76, 'mean of\nthe four', ha='left', size=FS - 0.3, color=INK, va='center')
    cv.text(92, 67.5, 'blue: falls', ha='left', size=FS - 0.6, color='#2f6fb0')
    cv.text(92, 62.5, 'orange: rises', ha='left', size=FS - 0.6, color='#c2410c')
    a = cv.inset(131, 62, 37, 18)
    L = np.linspace(0, 14, 200)
    a.plot(erf(L / (2 * np.sqrt(15.0))), L, color=BLUE, lw=1.4)
    a.axvline(1, color=ORANGE, lw=1.1, ls='--')
    a.set_ylim(14, 0); a.set_xlim(0, 1.08)
    GF.style(a, grid=None); a.tick_params(labelsize=FS - 0.8)
    a.set_xticks([0, 0.5, 1]); a.set_yticks([0, 7, 14])
    a.set_xlabel('share of Δp₀ left after 15 s', fontsize=FS - 0.8, labelpad=1)
    a.set_ylabel('m', fontsize=FS - 0.8, labelpad=1)
    a.legend(handles=[Line2D([], [], color=BLUE, lw=1.4), Line2D([], [], color=ORANGE, lw=1.1, ls='--')],
             labels=['connected sand', 'sealed by clay'], frameon=False, loc='lower left',
             fontsize=FS - 1.0, handlelength=1.3, borderaxespad=0.15, labelspacing=0.25, handletextpad=0.4)
    a = cv.inset(13, 12.5, 39, 18.5)
    zg = Sx['e1_zw_grid']
    for al, c in ((0.15, AQUA), (0.25, BLUE), (0.35, VIOLET)):
        a.plot(zg, Sx[f'e1_lpi_a{al}'], color=c, lw=1.3, label=f'{al:.2f} g')
    a.legend(frameon=False, loc='upper right', fontsize=FS - 1.0, handlelength=1.0, borderaxespad=0.1, labelspacing=0.2)
    a.axhline(5, color=REF, lw=0.7, ls='--')
    GF.style(a, grid=None); a.tick_params(labelsize=FS - 0.8); a.set_xlim(0.3, 6)
    a.set_xlabel('water table depth (m)', fontsize=FS - 0.8, labelpad=1); a.set_ylabel('LPI', fontsize=FS - 0.8, labelpad=1)
    a = cv.inset(72, 12.5, 38, 18.5)
    W = Sx['e4_width']; eta = Sx['e4_eta']; am = Sx['e4_amax']
    a.contourf(eta, am, np.clip(W.T, 0, None), levels=[0.3, 0.6, 0.9, 1.2, 1.5, 2.0], cmap=SEQ, extend='max')
    a.contourf(eta, am, W.T, levels=[-20, 0.3], colors=['#eceef1'])
    a.contour(eta, am, W.T, levels=[0.3], colors=[INK], linewidths=1.0)
    GF.style(a, grid=None); a.tick_params(labelsize=FS - 0.8); a.set_ylim(0.1, 0.3)
    a.set_xlabel('sea-level rise (m)', fontsize=FS - 0.8, labelpad=1); a.set_ylabel('PGA (g)', fontsize=FS - 0.8, labelpad=1)
    a.text(0.96, 0.82, 'closed', transform=a.transAxes, ha='right', fontsize=FS - 0.6, color=MUTED)
    a.text(0.05, 0.12, 'open', transform=a.transAxes, ha='left', fontsize=FS - 0.6, color='white', weight='bold')
    a = cv.inset(131, 12.5, 37, 18.5)
    d = Sx['e4_days']
    a.fill_between(d, 0, Sx['e4_pexc'], color='#f7d9c4', lw=0)
    a.plot(d, Sx['e4_pexc'], color=ORANGE, lw=1.4)
    GF.style(a, grid=None); a.tick_params(labelsize=FS - 0.8); a.set_xlim(0, 364); a.set_ylim(0, 0.32)
    a.set_xticks([MSTART[0], MSTART[3], MSTART[6], MSTART[9]]); a.set_xticklabels(['Jan', 'Apr', 'Jul', 'Oct'])
    a.set_ylabel('P(LPI > 5)', fontsize=FS - 0.8, labelpad=1)
    cv.fig.savefig(out, dpi=300); plt.close(cv.fig)


# --------------------------------------------------------------------------------------------- E1
def fig_e1(out, R, Sx):
    z = Sx['e1_z']; q = Sx['e1_q']; lq = Sx['e1_liq']
    fig = plt.figure(figsize=(174 * MM, 100 * MM))
    gs = fig.add_gridspec(1, 5, width_ratios=[0.85, 1, 1, 0.95, 1.5], wspace=0.30)
    cols = {0.8: ORANGE, 1.6: BLUE, 2.6: AQUA}
    ax = fig.add_subplot(gs[0])
    edges = np.flatnonzero(np.diff(lq.astype(int))) + 1
    starts = np.r_[0, edges]; ends = np.r_[edges, z.size]
    for a_, b_ in zip(starts, ends):
        ax.add_patch(Rectangle((0, z[a_] - 0.05), 220, z[b_ - 1] - z[a_] + 0.1, fc=SAND if lq[a_] else CLAY, ec='#9aa3ad' if not lq[a_] else 'none',
                               lw=0, alpha=0.6, zorder=0, hatch=None if lq[a_] else '///'))
    ax.plot(q, z, color=INK, lw=1.0)
    ax.set_ylim(20, 0); ax.set_xlim(0, 200)
    GF.style(ax, grid=None); ax.set_ylabel('depth (m)'); ax.set_xlabel(r'$q_{c1Ncs}$'); ax.set_xticks([0, 100])
    ax.set_title('(a) soil', fontsize=9.4)
    ax.text(185, 3.0, 'sand', fontsize=FS, color='#7a5d10', ha='right')
    ax.text(185, 0.62, 'crust', fontsize=FS, color=INK, ha='right', va='center',
            bbox=dict(fc='white', ec='none', pad=0.6, alpha=0.85))
    ax.text(185, 5.6, 'silty clay', fontsize=FS, color=INK, ha='right', bbox=dict(fc='white', ec='none', pad=0.6, alpha=0.85))
    ax2 = fig.add_subplot(gs[1], sharey=ax)
    for zw, c in cols.items():
        ax2.plot(np.where(z > zw, Sx[f'e1_csr_{zw}'], np.nan), z, color=c, lw=1.3)
    ax2.plot(np.where(lq, Sx['e1_crr_1.6'], np.nan), z, color=INK, lw=1.4)
    ax2.set_xlim(0, 0.42); GF.style(ax2, grid='x'); ax2.tick_params(labelleft=False); ax2.set_xticks([0, 0.2, 0.4])
    ax2.set_xlabel('cyclic stress ratio'); ax2.set_title('(b) CSR, CRR', fontsize=9.4)
    ax2.text(0.02, 5.7, 'CRR', fontsize=FS, color=INK, ha='left', weight='bold')
    ax2.text(0.235, 18.6, 'CSR', fontsize=FS, color=MUTED, ha='left', weight='bold')
    ax3 = fig.add_subplot(gs[2], sharey=ax)
    for zw, c in cols.items():
        fs = Sx[f'e1_fs_{zw}']
        ax3.plot(np.clip(fs, 0, 2.5), z, color=c, lw=1.2)
        ax3.fill_betweenx(z, np.clip(fs, 0, 1), 1, where=fs < 1, color=c, alpha=0.16, lw=0)
    ax3.axvline(1, color=INK, lw=0.8)
    ax3.set_xlim(0, 2.0); GF.style(ax3, grid='x'); ax3.tick_params(labelleft=False)
    ax3.set_xlabel('factor of safety'); ax3.set_title('(c) FS', fontsize=9.4)
    ax4 = fig.add_subplot(gs[3], sharey=ax)
    w = np.where(z <= 20, 10 - 0.5 * z, 0)
    for zw, c in cols.items():
        fs = Sx[f'e1_fs_{zw}']
        F = np.where(fs <= 1, 1 - fs, 0) * w
        ax4.fill_betweenx(z, 0, F, color=c, alpha=0.30, lw=0)
        ax4.plot(F, z, color=c, lw=0.9)
    ax4.set_xlim(0, 7); GF.style(ax4, grid='x'); ax4.tick_params(labelleft=False)
    ax4.set_xlabel('F(z) w(z)'); ax4.set_title('(d) LPI density', fontsize=9.4)
    lp = R['E1']['example']
    ax4.text(6.8, 13.0, 'LPI', fontsize=FS, color=INK, ha='right', weight='bold')
    for k, (zw, c) in enumerate(cols.items()):
        ax4.text(6.8, 14.6 + 1.5 * k, f'{zw:g} m: {lp[str(zw)]["lpi"]:.1f}', color=c, fontsize=FS, ha='right')
    ax5 = fig.add_subplot(gs[4])
    zg = Sx['e1_zw_grid']
    ax5.axhspan(5, 15, color='#fbeee3', lw=0, zorder=0); ax5.axhspan(15, 60, color='#f6dcc8', lw=0, zorder=0)
    for al, c in ((0.15, AQUA), (0.25, BLUE), (0.35, VIOLET)):
        ax5.plot(zg, Sx[f'e1_lpi_a{al}'], color=c, lw=1.6)
    ax5.plot(zg, Sx['e1_lpi_wrong'], color=BLUE, lw=1.2, ls=(0, (3, 2)))
    ax5.text(5.95, 33.5, 'very high', fontsize=FS, color='#a8461b', ha='right', va='top')
    ax5.text(5.95, 14.3, 'high', fontsize=FS, color='#a8461b', ha='right', va='top')
    ax5.set_xlim(0.3, 6); ax5.set_ylim(0, 36); GF.style(ax5)
    ax5.set_xlabel('water table depth (m)')
    ax5.set_title('(e) LPI vs water table', fontsize=9.4)
    hs = [Line2D([], [], color=c, lw=1.3) for c in cols.values()] + [Line2D([], [], color=INK, lw=1.4)]
    ls = [f'CSR, $z_w$ = {zw:g} m' for zw in cols] + ['CRR (sands)']
    hs += [Line2D([], [], color=c, lw=1.6) for c in (AQUA, BLUE, VIOLET)] + [Line2D([], [], color=BLUE, lw=1.2, ls=(0, (3, 2)))]
    ls += ['LPI, 0.15 g', 'LPI, 0.25 g', 'LPI, 0.35 g', 'LPI, 0.25 g, q re-normalised (wrong)']
    fig.legend(hs, ls, frameon=False, loc='lower center', ncol=4, bbox_to_anchor=(0.52, 0.0), handlelength=1.5,
               columnspacing=1.0, fontsize=FS - 0.3)
    fig.subplots_adjust(left=0.075, right=0.975, top=0.93, bottom=0.27)
    fig.savefig(out, dpi=300); plt.close(fig)


# --------------------------------------------------------------------------------------------- E2
def fig_e2(out, R, Sx):
    srcs = R['E2']['sources']
    x = Sx['e2_x'] / 1e3
    fig = plt.figure(figsize=(174 * MM, 180 * MM))
    outer = fig.add_gridspec(3, 1, height_ratios=[1.0, 1.05, 0.82], hspace=0.40)
    row1 = outer[0].subgridspec(1, 5, width_ratios=[1, 1, 1, 1, 0.06], wspace=0.08)
    im = None
    for k, s_ in enumerate(srcs):
        ax = fig.add_subplot(row1[k])
        dh = Sx[f'e2_dh_{s_["key"]}']; uz = Sx[f'e2_uz_{s_["key"]}']
        im = ax.imshow(dh, extent=(x[0], x[-1], x[0], x[-1]), origin='lower', cmap=DIV, vmin=-0.8, vmax=0.8,
                       interpolation='bilinear')
        ax.contour(x, x, dh, levels=[-0.5, -0.25, -0.1, 0.1, 0.25], colors=[INK], linewidths=0.45)
        ax.contour(x, x, uz, levels=[0.02, 0.05, 0.1], colors=['#ffffff'], linewidths=0.7, linestyles='--')
        draw_fault(ax, s_)
        map_axes(ax)
        if k:
            ax.tick_params(labelleft=False)
        else:
            ax.set_ylabel('km north')
        ax.set_xlabel('km east')
        ax.set_title(f'({"abcd"[k]}) ' + SRC_SHORT[s_['key']].replace('van der Heiden', 'v. d. Heiden'), fontsize=FS)
        ax.text(0.04, 0.04, f'dip {s_["dip"]:.0f}°, Mw {s_["mw"]:.2f}', transform=ax.transAxes, fontsize=FS - 0.4,
                color=INK, bbox=dict(fc='white', ec='none', alpha=0.85, pad=1.0))
    cax = fig.add_subplot(row1[4])
    cb = fig.colorbar(im, cax=cax, extend='both')
    cb.set_label('Δh₀ confined (m)', fontsize=FS); cb.ax.tick_params(labelsize=FS)
    row2 = outer[1].subgridspec(1, 2, width_ratios=[1, 1.55], wspace=0.22)
    ax = fig.add_subplot(row2[0])
    ax.imshow(Sx['e2_dh_mean'], extent=(x[0], x[-1], x[0], x[-1]), origin='lower', cmap=DIV, vmin=-0.8, vmax=0.8,
              interpolation='bilinear')
    plt.rcParams['hatch.color'] = '#5b6672'; plt.rcParams['hatch.linewidth'] = 0.5
    disagree = ((~Sx['e2_agree']) & Sx['e2_big']).astype(float)
    ax.contourf(x, x, disagree, levels=[0.5, 1.5], colors='none', hatches=['.....'])
    ax.contour(x, x, disagree, levels=[0.5], colors=['#5b6672'], linewidths=0.5)
    for s_ in srcs:
        draw_fault(ax, s_, SRC_COL[s_['key']], lw=0.8)
    map_axes(ax)
    ax.set_xlabel('km east of the centroid'); ax.set_ylabel('km north')
    ax.set_title('(e) mean; dotted: signs differ', fontsize=9.4)
    az = np.radians(340.0 + 90.0)
    st = Sx['e2_tr_s'] / 1e3
    ax.plot(st * np.sin(az), st * np.cos(az), color=INK, lw=0.9, ls=':')
    ax.text(25.6, 13.6, 'A′', fontsize=FS)
    ax.text(-28.6, -15.8, 'A', fontsize=FS)
    ax = fig.add_subplot(row2[1])
    trs = np.array([Sx[f'e2_tr_{s_["key"]}'] for s_ in srcs])
    kp = R['E2']['kappa_kPa']
    lo, hi = kp['confined_band']
    m = trs.mean(0)
    ax.fill_between(st, m * lo / kp['confined'], m * hi / kp['confined'], color='#e3e7ec', lw=0,
                    label='mean, G 0.25–1 GPa', zorder=0)
    ax.plot(st, Sx['e2_tr_soft_mean'], color=INK, lw=1.3, ls=(0, (4, 2)), label='soft sand (mean)', zorder=5)
    for s_ in srcs:
        ax.plot(st, Sx[f'e2_tr_{s_["key"]}'], color=SRC_COL[s_['key']], lw=1.4,
                label=SRC_SHORT[s_['key']].replace('van der Heiden', 'v. d. Heiden'))
    ax.axhline(0, color=INK, lw=0.6)
    GF.style(ax); ax.set_xlim(st[0], st[-1]); ax.set_ylim(-1.75, 0.55)
    ax.set_xlabel('distance along A–A′ (km)'); ax.set_ylabel('Δh₀ (m)')
    ax.set_title('(f) the step across the strike', fontsize=9.4)
    hh, ll = ax.get_legend_handles_labels()
    ax.legend(hh[2:] + hh[:2], ll[2:] + ll[:2], frameon=False, loc='lower right', fontsize=FS - 0.3, handlelength=1.6,
              ncol=1, borderaxespad=0.3, labelspacing=0.25)
    ax.text(-34, 0.43, 'head rises (squeezed)', fontsize=FS - 0.3, color='#c2410c', va='center')
    ax.text(-34, -1.62, 'head falls (dilated)', fontsize=FS - 0.3, color='#2f6fb0', va='center', ha='left')
    row3 = outer[2].subgridspec(1, 2, width_ratios=[1, 1.15], wspace=0.30)
    ax = fig.add_subplot(row3[0])
    from scipy.special import erf
    L = np.linspace(0, 14, 300)
    for t, c in ((5, AQUA), (15, BLUE), (40, VIOLET)):
        ax.plot(L, erf(L / (2 * np.sqrt(1.0 * t))), color=c, lw=1.5, label=f'{t} s of shaking')
    ax.axhline(1, color=ORANGE, lw=1.2, ls='--', label='sand sealed by clay')
    GF.style(ax); ax.set_xlim(0, 14); ax.set_ylim(0, 1.1)
    ax.set_xlabel('depth below the water table, through sand (m)'); ax.set_ylabel('share of Δp₀ left')
    ax.set_title('(g) drainage during shaking', fontsize=9.4)
    ax.legend(frameon=False, loc='lower right', fontsize=FS - 0.3, handlelength=1.4)
    ax = fig.add_subplot(row3[1])
    t = Sx['e2_relax_t']
    ax.plot(t, Sx['e2_relax_obs'], color='#b9c2cc', lw=0.5)
    ax.plot(t, Sx['e2_relax_fit'], color=BLUE, lw=1.7)
    ax.text(0.45, 0.335, 'fit: leakage time τ', fontsize=FS - 0.3, color=BLUE, va='center')
    ax.text(0.35, -0.04, 'logger, 2 cm noise', fontsize=FS - 0.3, color='#7d8792', va='center')
    nt = R['E2']['natural_test']
    GF.style(ax); ax.set_xlim(0, 14); ax.set_ylim(-0.06, 0.36)
    ax.set_xlabel('days after the earthquake'); ax.set_ylabel('head step (m)')
    ax.set_title('(h) a free pumping test', fontsize=9.4)
    ins = ax.inset_axes([0.44, 0.47, 0.53, 0.27])
    for k_, (lab, ci, c) in enumerate((('earthquake, 20 days', nt['ci95_quake_d'], BLUE),
                                        ('one year of seasons', nt['ci95_season_d'], REF))):
        ins.plot(ci, [k_, k_], color=c, lw=3.4, solid_capstyle='butt')
        ins.text(2.42, k_ + 0.45, lab, va='center', fontsize=FS - 0.6, color=c, ha='left')
    for y0, y1 in ((-0.22, 0.16), (0.78, 1.16)):                  # true tau, through the bars only
        ins.plot([nt['tau_true_d']] * 2, [y0, y1], color=INK, lw=0.8, ls=':')
    ins.set_ylim(-0.5, 1.9); ins.set_xlim(2.4, 3.6); ins.set_yticks([]); ins.set_xticks([2.5, 3.0, 3.5])
    for sp in ('top', 'right', 'left'):
        ins.spines[sp].set_visible(False)
    ins.set_facecolor('none')
    ins.tick_params(labelsize=FS - 0.8, length=2)
    ins.set_title('95% interval of τ (days)', fontsize=FS - 0.6, pad=3, color=INK)
    fig.subplots_adjust(left=0.085, right=0.92, top=0.965, bottom=0.06)
    fig.savefig(out, dpi=300); plt.close(fig)


# --------------------------------------------------------------------------------------------- E3
def fig_e3(out, R, Sx):
    E3 = R['E3']
    fig = plt.figure(figsize=(174 * MM, 140 * MM))
    outer = fig.add_gridspec(1, 2, width_ratios=[0.9, 1.6], wspace=0.24)
    ax = fig.add_subplot(outer[0])
    gx = Sx['e3_gx']
    ax.imshow(Sx['e3_field'], extent=(gx[0], gx[-1], gx[0], gx[-1]), origin='lower',
              cmap=LinearSegmentedColormap.from_list('g', ['#ffffff', '#eef4ea', '#cfe2c6', '#a3c7a6']), vmin=-2.5,
              vmax=2.5, interpolation='bilinear')
    yy = np.linspace(-30, 30, 50)
    cx = -10.0 - 0.364 * yy
    ax.fill_betweenx(yy, -30, cx, color='#dbe9f6', lw=0, zorder=1)
    ax.plot(cx, yy, color='#5b8fc7', lw=1.2, zorder=2)
    ax.text(-27, 20, 'sea', color='#2f6fb0', fontsize=9.2)
    draw_fault(ax, R['E2']['sources'][0], INK, lw=0.8)
    xs, ys, ob = Sx['e3_x'], Sx['e3_y'], Sx['e3_obs']
    lp = Sx['e3_lpi_true']
    ax.scatter(xs[ob == 0], ys[ob == 0], s=6, facecolors='white', edgecolors='#7d8792', linewidths=0.45, zorder=4)
    ax.scatter(xs[ob == 1], ys[ob == 1], s=8 + 1.0 * np.clip(lp[ob == 1], 0, 30), c=np.clip(lp[ob == 1], 0, 30),
               cmap=LinearSegmentedColormap.from_list('l', ['#f4b183', '#df6a2e', '#9a3412']), vmin=0, vmax=30,
               edgecolors='white', linewidths=0.3, zorder=5)
    ax.set_xlim(-28, 8); ax.set_ylim(-27, 27); ax.set_aspect('equal')
    GF.style(ax, grid=None); ax.set_xlabel('km east of the centroid'); ax.set_ylabel('km north')
    ax.set_title('(a) synthetic plain, 900 sites', fontsize=9.4)
    ax.legend(handles=[Line2D([], [], ls='', marker='o', ms=4, mfc='white', mec='#7d8792', label='no liquefaction'),
                       Line2D([], [], ls='', marker='o', ms=6, color='#df6a2e', label='liquefied (size: LPI)'),
                       Line2D([], [], color=INK, lw=2.2, label='fault, up-dip edge')],
              frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.12), fontsize=FS, ncol=1, handletextpad=0.4)
    right = outer[1].subgridspec(2, 2, height_ratios=[0.82, 1.0], hspace=0.40, wspace=0.42)
    ax = fig.add_subplot(right[0, 0])
    y = ob
    names = dict(M0='mean water table', M1='water table of the day', M2='+ step (ensemble)', M3='+ step (true source)')
    cols = dict(M0=REF, M1=AQUA, M2=BLUE, M3=ORANGE)
    for k in ('M0', 'M1', 'M2', 'M3'):
        s_ = Sx[f'e3_{k}']
        thr = np.unique(np.r_[s_, np.inf])[::-1]
        tpr = [(s_[y == 1] >= t).mean() for t in thr]; fpr = [(s_[y == 0] >= t).mean() for t in thr]
        ax.plot(fpr, tpr, color=cols[k], lw=1.3 if k != 'M3' else 1.1, ls='-' if k != 'M3' else (0, (3, 2)),
                label=names[k])
    ax.plot([0, 1], [0, 1], color='#d0d5db', lw=0.7)
    GF.style(ax); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect('equal')
    ax.set_xlabel('false alarm rate'); ax.set_ylabel('hit rate')
    ax.set_title('(b) ROC and AUC', fontsize=9.4)
    short = dict(M0='mean WT', M1='WT of the day', M2='+ step (ens.)', M3='+ step (true)')
    ax.text(0.97, 0.36, 'AUC', transform=ax.transAxes, ha='right', fontsize=FS - 0.4, weight='bold', color=INK)
    for j, k in enumerate(('M0', 'M1', 'M2', 'M3')):
        ax.text(0.97, 0.28 - 0.075 * j, f'{short[k]}  {E3["auc_full_pool"][k]:.3f}', transform=ax.transAxes,
                ha='right', fontsize=FS - 0.6, color=cols[k])
    ax = fig.add_subplot(right[0, 1])
    N = E3['n_sites']
    pc = {'season (M1 vs M0)': (AQUA, 'season'), 'step, ensemble source (M2 vs M1)': (BLUE, 'step, ensemble'),
          'step, true source (M3 vs M1)': (ORANGE, 'step, true')}
    for key, (c, lab) in pc.items():
        ax.plot(N, E3['power'][key], color=c, lw=1.6, marker='o', ms=3.8, label=lab)
    ax.axhline(0.8, color=REF, lw=0.8, ls='--'); ax.text(470, 0.82, '80%', fontsize=FS, color=MUTED, ha='right',
                                                         va='bottom')
    ax.set_xscale('log'); ax.set_xticks(N); ax.set_xticklabels([str(n) for n in N]); ax.xaxis.set_minor_locator(NullLocator())
    GF.style(ax); ax.set_ylim(0, 1); ax.set_xlabel('mapped sites with CPT'); ax.set_ylabel('power'); ax.set_box_aspect(1)
    ax.set_title('(c) power (upper bound)', fontsize=9.4)
    ax.legend(frameon=False, loc='upper left', bbox_to_anchor=(0.0, 0.77), fontsize=FS - 0.4, handlelength=1.3)
    ax = fig.add_subplot(right[1, :])
    ea = Sx['e3_ea'] * 1e6
    ax.scatter(ea, Sx['e3_M3'] - Sx['e3_M1'], s=6, c=ORANGE, lw=0, alpha=0.75)
    ax.scatter(ea, Sx['e3_M4'] - Sx['e3_M1'], s=6, c=BLUE, lw=0, alpha=0.9)
    ax.axhline(0, color=INK, lw=0.6); ax.axvline(0, color=INK, lw=0.6, ymin=0.2, ymax=0.88)
    GF.style(ax); ax.set_xlabel('areal strain at the site (microstrain; > 0 dilated)'); ax.set_yticks([-15, -10, -5, 0, 5])
    ax.set_ylabel('change of LPI from the step')
    ax.set_title('(d) what the static step does to LPI', fontsize=9.4)
    ax.set_ylim(-16.5, 5.5)
    ax.legend(handles=[Line2D([], [], ls='', marker='o', ms=3.6, mfc=ORANGE, mec='none'),
                       Line2D([], [], ls='', marker='o', ms=3.6, mfc=BLUE, mec='none')],
              labels=['(2.2) as written (upper bound)', 'soft surface sand (this note)'], loc='lower left',
              frameon=False, fontsize=FS - 0.3, handletextpad=0.2, borderaxespad=0.4)
    ax.text(0.02, 0.98, 'squeezed: LPI rises', transform=ax.transAxes, fontsize=FS, color='#c2410c', ha='left', va='top')
    ax.text(0.98, 0.98, 'dilated: LPI falls', transform=ax.transAxes, fontsize=FS, color='#2f6fb0', ha='right',
            va='top')
    fig.subplots_adjust(left=0.08, right=0.985, top=0.95, bottom=0.08)
    fig.savefig(out, dpi=300); plt.close(fig)


# --------------------------------------------------------------------------------------------- E4 window
def fig_e4(out, R, Sx):
    E4 = R['E4']
    eta, am, W = Sx['e4_eta'], Sx['e4_amax'], Sx['e4_width']
    fig = plt.figure(figsize=(174 * MM, 92 * MM))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1.0, 1.0], wspace=0.40)
    ax = fig.add_subplot(gs[0])
    lv = [0.3, 0.6, 0.9, 1.2, 1.5, 2.0]
    cf = ax.contourf(eta, am, W.T, levels=lv, cmap=SEQ, extend='max')
    ax.contourf(eta, am, W.T, levels=[-50, 0.0], colors=['#eceef1'])
    ax.contourf(eta, am, W.T, levels=[0.0, 0.3], colors=['#f6f0dc'])
    ax.contour(eta, am, W.T, levels=[0.3], colors=[INK], linewidths=1.4)
    ax.contour(eta, am, W.T, levels=[0.0], colors=[MUTED], linewidths=0.8, linestyles='--')
    rate = 0.009                                                   # m/yr: 4 mm/yr sea + 5 mm/yr subsidence (illustrative)
    sec = ax.secondary_xaxis('top', functions=(lambda e: 2026 + e / rate, lambda y: (y - 2026) * rate))
    sec.set_xticks([2040, 2080, 2120]); sec.tick_params(labelsize=FS - 0.4, colors=MUTED, length=2)
    sec.set_xlabel('year, at 9 mm/yr (illustrative)', fontsize=FS - 0.4, color=MUTED, labelpad=2)
    a_close = np.array([am[np.flatnonzero(W[i] >= 0.0).max()] if np.any(W[i] >= 0.0) else am[0] for i in range(eta.size)])
    for yr in (2040, 2080, 2120):                                  # time slices through the open part only
        e_ = (yr - 2026) * rate
        ax.plot([e_, e_], [0.10, np.interp(e_, eta, a_close)], color='#5b6672', lw=0.6, ls=':')
    ax.text(0.96, 0.80, 'closed', transform=ax.transAxes, ha='right', fontsize=9.0, color=MUTED, weight='bold')
    ax.legend(handles=[Rectangle((0, 0), 1, 1, fc='#f6f0dc', ec='none'), Line2D([], [], color=INK, lw=1.4),
                       Line2D([], [], color=MUTED, lw=0.8, ls='--')],
              labels=['open part of the year', 'width = seasonal swing', 'width = 0'], loc='upper right',
              bbox_to_anchor=(0.985, 0.765), frameon=False, fontsize=FS - 0.6, handlelength=1.3, labelspacing=0.3,
              borderaxespad=0.0)
    ax.text(0.04, 0.06, 'open all year', transform=ax.transAxes, fontsize=9.0, color='white', weight='bold')
    GF.style(ax, grid=None); ax.set_xlim(0, 1.2); ax.set_ylim(0.10, 0.30)
    ax.set_xlabel('relative sea-level rise η (m)'); ax.set_ylabel('design peak acceleration (g)')
    ax.set_title('(a) the joint safe window', fontsize=9.4, pad=26)
    cax = ax.inset_axes([0.05, 0.86, 0.42, 0.045])
    cb = fig.colorbar(cf, cax=cax, orientation='horizontal')
    cb.set_ticks([0.3, 0.9, 1.5]); cb.ax.tick_params(labelsize=FS - 0.6, length=2)
    cax.text(0.0, 1.5, 'window width (m of head)', transform=cax.transAxes, ha='left', va='bottom', fontsize=FS - 0.6)
    ax = fig.add_subplot(gs[1])
    zs = E4['z_s']
    zst = Sx['e4_zstar']; zc = Sx['e4_zstar_cert']
    ax.fill_between(am, zs - np.quantile(zst, 0.9, axis=0), zs - np.quantile(zst, 0.1, axis=0), color='#dfe7f3', lw=0)
    ax.plot(am, zs - zc, color=BLUE, lw=1.8)
    for e_, ls in ((0.0, '-'), (0.3, '--'), (0.6, ':')):
        ax.axhline(e_ + E4['m_int'], color=ORANGE, lw=1.2, ls=ls)
    ax.axhline(zs, color=INK, lw=0.6)
    ax.text(0.295, zs + 0.08, 'ground', fontsize=FS - 0.4, color=MUTED, ha='right')
    ax.text(0.105, -2.9, 'head must stay\nbelow the blue line\nand above the orange', fontsize=FS - 0.4, color=MUTED)
    GF.style(ax); ax.set_xlim(0.10, 0.30); ax.set_ylim(-3.6, 2.5)
    ax.set_xlabel('design peak acceleration (g)'); ax.set_ylabel('head at the port above sea level (m)')
    ax.set_title('(b) the two limits', fontsize=9.4, pad=26)
    hs = [Rectangle((0, 0), 1, 1, fc='#dfe7f3'), Line2D([], [], color=BLUE, lw=1.8),
          Line2D([], [], color=ORANGE, lw=1.2), Line2D([], [], color=ORANGE, lw=1.2, ls='--'),
          Line2D([], [], color=ORANGE, lw=1.2, ls=':')]
    ls_ = ['liquefaction limit, 10–90% of profiles', 'certified liquefaction limit (90%)', 'intrusion limit, η = 0',
           'intrusion limit, η = 0.3 m', 'intrusion limit, η = 0.6 m']
    fig.legend(hs, ls_, frameon=False, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 0.0), fontsize=FS - 0.4,
               handlelength=1.5, columnspacing=1.0)
    ax = fig.add_subplot(gs[2])
    for k in range(zst.shape[0]):
        ax.plot(am, zst[k], color='#c9d2dd', lw=0.5)
    ax.plot(am, zc, color=BLUE, lw=1.9)
    ax.plot(am, np.median(zst, axis=0), color=INK, lw=1.0, ls='--')
    ax.annotate('certified:\n90% of the\nprofiles safe', xy=(0.262, 3.05), xytext=(0.104, 5.85), va='top',
                fontsize=FS - 0.4, color=BLUE, arrowprops=dict(arrowstyle='-', color=BLUE, lw=0.6, shrinkB=1))
    ax.annotate('median\nprofile', xy=(0.268, 0.62), xytext=(0.104, 2.75), va='top', fontsize=FS - 0.4, color=INK,
                arrowprops=dict(arrowstyle='-', color=INK, lw=0.6, ls='--', shrinkB=1))
    GF.style(ax); ax.set_xlim(0.10, 0.30); ax.set_ylim(0, 6)
    ax.set_xlabel('design peak acceleration (g)'); ax.set_ylabel('water table needed for LPI ≤ 5 (m)')
    ax.set_title(f'(c) {zst.shape[0]} port profiles', fontsize=9.4, pad=26)
    fig.subplots_adjust(left=0.09, right=0.97, top=0.84, bottom=0.27)
    fig.savefig(out, dpi=300); plt.close(fig)


# --------------------------------------------------------------------------------------------- E4 bulletin
def fig_e5(out, R, Sx):
    d = Sx['e4_days']
    fig, axs = plt.subplots(3, 1, figsize=(174 * MM, 112 * MM), sharex=True,
                            gridspec_kw=dict(height_ratios=[0.8, 1.2, 1.0], hspace=0.14))
    for ax in axs:
        for k in range(0, 12, 2):
            ax.axvspan(MSTART[k], MSTART[k] + 31, color='#f5f6f8', lw=0, zorder=0)
    ax = axs[0]
    ax.plot(d, Sx['e4_zw_day'], color=BLUE, lw=1.8)
    ax.set_ylim(2.2, 0.6); GF.style(ax); ax.set_ylabel('water table\ndepth (m)')
    ax.set_title('The port in 2027, if the design earthquake (M 6.4, median 0.22 g) struck on that day', fontsize=9.4)
    ax = axs[1]
    ax.fill_between(d, Sx['e4_lpi_q05'], Sx['e4_lpi_q95'], color='#dfe7f3', lw=0)
    ax.plot(d, Sx['e4_lpi_q95'], color=BLUE, lw=0.9)
    ax.plot(d, Sx['e4_lpi_q50'], color=INK, lw=1.5)
    ax.axhline(5, color=ORANGE, lw=1.0, ls='--')
    ax.text(362, 5.6, 'LPI 5', fontsize=FS, color=ORANGE, ha='right')
    ax.text(150, Sx['e4_lpi_q95'][150] + 0.6, '95th percentile', fontsize=FS, color=BLUE)
    ax.text(150, Sx['e4_lpi_q50'][150] + 0.6, 'median', fontsize=FS, color=INK)
    GF.style(ax); ax.set_ylabel('LPI'); ax.set_ylim(0, 16)
    ax = axs[2]
    pe = Sx['e4_pexc']
    ax.fill_between(d, 0, pe, color='#f7d9c4', lw=0)
    ax.plot(d, pe, color=ORANGE, lw=1.8)
    b = R['E4']['bulletin']
    ax.annotate(f'{pe.max():.2f}', xy=(b['day_max'], pe.max()), xytext=(b['day_max'] + 22, pe.max() + 0.035),
                fontsize=FS, color=ORANGE, arrowprops=dict(arrowstyle='-', color=ORANGE, lw=0.6))
    ax.annotate(f'{pe.min():.2f}', xy=(b['day_min'], pe.min()), xytext=(b['day_min'] + 22, pe.min() - 0.07),
                fontsize=FS, color=ORANGE, arrowprops=dict(arrowstyle='-', color=ORANGE, lw=0.6))
    GF.style(ax); ax.set_ylim(0, 0.34); ax.set_ylabel('P(LPI > 5 |\nearthquake today)')
    ax.set_xlim(0, 364)
    ax.set_xticks(MSTART + 15); ax.set_xticklabels(MONTHS); ax.xaxis.set_minor_locator(NullLocator())
    ax.tick_params(axis='x', length=0)
    fig.subplots_adjust(left=0.11, right=0.985, top=0.93, bottom=0.07)
    fig.savefig(out, dpi=300); plt.close(fig)


def main(out):
    os.makedirs(out, exist_ok=True)
    R, Sx = load()
    fig_chain(os.path.join(out, 'fig_chain.png'), R, Sx)
    fig_e1(os.path.join(out, 'fig_e1.png'), R, Sx)
    fig_e2(os.path.join(out, 'fig_e2.png'), R, Sx)
    fig_e3(os.path.join(out, 'fig_e3.png'), R, Sx)
    fig_e4(os.path.join(out, 'fig_e4.png'), R, Sx)
    fig_e5(os.path.join(out, 'fig_e5.png'), R, Sx)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'figs'))
