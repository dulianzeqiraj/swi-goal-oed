"""Manuscript figures (Python reference rendering). The MATLAB scripts in ../matlab draw the same panels.

  fig1_framework   decision chain: questions, modules and the quantities they exchange
  fig2_site        study area, Adriatic contact, wells, cover depth, section A-A'
  fig3_hydrochem   mixing, ion-exchange deviations, BEX, chloride trend
  fig4_calib       prior and posterior of the calibration targets and the held-out check
  fig5_maps        posterior chloride at three depths: median and P(Cl > 250 mg/L)
  fig6_section     variable-density chloride section A-A' and the toe comparison
  fig7_design      goal-oriented chloride sampling design
  fig8_toolkit     decision modules: key results
  figS1_prag_mar_geo  PRAG-MAR with the geolocated sea boundary (needs experiments/prag_go_fushe_kuqe/res_geo)
Usage: python3 fkcl_figs.py [outdir]
"""
import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fkcl_model as M  # noqa: E402

RES = os.path.join(HERE, '..', 'results')
DER = os.path.join(HERE, '..', 'derived')
EXP = os.path.join(HERE, '..', '..', 'experiments')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'figures')

plt.rcParams.update({'font.family': 'FreeSans', 'font.size': 8, 'axes.titlesize': 8.5, 'axes.labelsize': 8,
                     'xtick.labelsize': 7, 'ytick.labelsize': 7, 'legend.fontsize': 7, 'axes.linewidth': 0.6,
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'savefig.dpi': 400,
                     'mathtext.fontset': 'stixsans', 'axes.spines.top': False, 'axes.spines.right': False})
OI = ['#0072B2', '#D55E00', '#009E73', '#CC79A7', '#E69F00', '#56B4E9', '#F0E442', '#000000']   # Okabe-Ito
MM = 1 / 25.4


def panel(ax, s, x=-0.02, y=1.02):
    ax.text(x, y, s, transform=ax.transAxes, fontweight='bold', fontsize=9, ha='right', va='bottom')


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, name + '.png'), bbox_inches='tight')
    fig.savefig(os.path.join(OUT, name + '.pdf'), bbox_inches='tight')
    plt.close(fig)


class Geo:
    def __init__(self):
        self.m = M.Model()
        m = self.m
        self.coast = pd.read_csv(os.path.join(DER, 'shoreline_polyline.csv'))
        self.places = pd.read_csv(os.path.join(DER, 'places.csv'))
        self.W = pd.read_excel(M.fk.default_xlsx(), sheet_name='2_All_Wells')
        self.W['x'] = (self.W.X_GaussKruger - m.base.x0) / 1000
        self.W['y'] = (self.W.Y_GaussKruger - m.base.y0) / 1000
        b = m.base
        self.xe = np.r_[b.xs - 0.5 * b.dx, b.xs[-1] + 0.5 * b.dx]
        self.ye = np.r_[b.ys - 0.5 * b.dx, b.ys[-1] + 0.5 * b.dx]

    def grid(self, v, mask=None):
        b = self.m.base
        G = np.full((b.ny, b.nx), np.nan)
        vv = np.asarray(v, float).copy()
        if mask is not None:
            vv[~mask] = np.nan
        G[b.aj, b.ai] = vv
        return G

    def outline(self, ax, sector=False, lw=0.7):
        m = self.m
        ax.plot(m.base.Bk[:, 0], m.base.Bk[:, 1], color='0.15', lw=lw, zorder=5)
        for _, g in self.coast.groupby('segment'):
            xs, ys = g.x_km.to_numpy(), g.y_km.to_numpy()
            k = 3
            if len(xs) > 2 * k:
                xs = np.convolve(np.r_[xs[:k][::-1], xs, xs[-k:][::-1]], np.ones(2 * k + 1) / (2 * k + 1), 'valid')
                ys = np.convolve(np.r_[ys[:k][::-1], ys, ys[-k:][::-1]], np.ones(2 * k + 1) / (2 * k + 1), 'valid')
            ax.plot(xs, ys, color=OI[0], lw=0.6, zorder=4)
        if sector:
            ax.axhline(M.Y_CUT, color='0.4', lw=0.5, ls=':', zorder=4)

    def sea_contact(self, ax, **kw):
        m = self.m
        sel = m.seac
        ys = m.cy[sel]; xs = m.cx[sel] - 0.5 * m.dx
        o = np.argsort(ys)
        ax.plot(xs[o], ys[o], **kw)


# ---------------------------------------------------------------- figure 1: framework
def fig1_framework():
    fig, ax = plt.subplots(figsize=(190 * MM, 84 * MM))
    ax.set_xlim(0, 190); ax.set_ylim(0, 84); ax.axis('off')
    cols = [('Where is the\nchloride now?', '#E8F1FA', OI[0],
             'Hydrochemistry: mixing,\nion exchange, BEX\nStrack interface with a\ntransition zone, calibrated\nto documented facts\nVariable-density section\nSAFE-GO, KALIB-GO:\nrobust learning rates'),
            ('Where should\nwe measure?', '#E9F6F1', OI[2],
             'Goal-oriented EIG with\nadjoint sensitivities\nPRAG-GO, PRAG-MAR:\nthreshold-risk design\nSINERGO: pairwise synergy\nKRITIK-GO: early warning\nChloride sampling design'),
            ('How much can\nwe pump?', '#FDF1E6', OI[4],
             'KRAMERS-GO: return-\nperiod-safe pumping\n(an escape problem)\nKUFI-GO: safe threshold\nwith simultaneous bands\nand randomized thresholds'),
            ('What caused a\nsalinization event?', '#F8EAF2', OI[3],
             'ATRIB-GO: probability of\nnecessity (twin worlds)\nTMLE-GO: targeted risk\nof pumping regimes from\noperating records'),
            ('Does information\nreach the decision?', '#FBEDE6', OI[1],
             'RRJEDHA-GO: causal\ninformation flow\nKANAL-GO: design of the\npumping experiment\nKTHIMI-GO: feedback\ninformation as a\nmonitoring criterion')]
    w, gap = 35.0, 2.75
    x0 = (190 - 5 * w - 4 * gap) / 2
    for k, (t, fc, ec, body) in enumerate(cols):
        x = x0 + k * (w + gap)
        ax.add_patch(FancyBboxPatch((x, 30), w, 46, boxstyle='round,pad=0.4,rounding_size=2', fc=fc, ec=ec, lw=0.9))
        ax.text(x + w / 2, 74.5, t, ha='center', va='top', fontweight='bold', fontsize=7.2, linespacing=1.15)
        ax.text(x + w / 2, 64.5, body, ha='center', va='top', fontsize=6.3, linespacing=1.3)
        ax.annotate('', xy=(x + w / 2, 20.5), xytext=(x + w / 2, 29.3), arrowprops=dict(arrowstyle='-|>', color=ec, lw=1.0))
    ax.add_patch(FancyBboxPatch((x0, 3), 5 * w + 4 * gap, 16.5, boxstyle='round,pad=0.4,rounding_size=2', fc='#F3F3F3', ec='0.35', lw=0.9))
    ax.text(95, 17.6, 'Management decision: monitoring network, sampling depth, pumping and recharge rules',
            ha='center', va='top', fontweight='bold', fontsize=7.2)
    ax.text(95, 11.6, 'Decision-relevant quantities: P(Cl > 250 mg/L), affected area, goal-oriented EIG (nats), safe pumping rate,\n'
            'probability of necessity, risk of a pumping regime, information that reaches the operator (bits)',
            ha='center', va='top', fontsize=6.3, linespacing=1.3)
    ax.text(95, 83, 'A decision chain for seawater-intrusion monitoring and management', ha='center', va='top', fontsize=8.5, fontweight='bold')
    save(fig, 'fig1_framework')


# ---------------------------------------------------------------- figure 2: site
def fig2_site(G):
    m = G.m
    fig = plt.figure(figsize=(190 * MM, 118 * MM))
    ax = fig.add_axes([0.06, 0.08, 0.42, 0.9]); ax2 = fig.add_axes([0.47, 0.08, 0.42, 0.9])
    for a in (ax, ax2):
        a.set_aspect('equal'); a.set_xlim(-6, 22); a.set_ylim(-1.5, 55)
        a.set_xlabel('Easting from x$_0$ [km]'); a.spines['top'].set_visible(True); a.spines['right'].set_visible(True)
    ax.set_ylabel('Northing from y$_0$ [km]')
    G.outline(ax, sector=True)
    ax.fill(m.base.Bk[:, 0], m.base.Bk[:, 1], color='#EAF2EA', zorder=1)
    G.sea_contact(ax, color=OI[1], lw=2.6, zorder=6, solid_capstyle='round')
    # inland western margin (used as a sea boundary by the companion model)
    b = m.base
    wx, wy = [], []
    for j in range(b.ny):
        ii = np.flatnonzero(b.inside[j])
        if len(ii) and not m.sea_row[j]:
            wx.append(b.xs[ii[0]] - 0.5 * b.dx - 0.45); wy.append(b.ys[j])
    ax.plot(wx, wy, color='0.2', lw=1.3, ls=(0, (2.2, 1.6)), zorder=6)
    W = G.W
    has = W.K_m_per_day.notna()
    cls = [(W.K_m_per_day >= 150), (W.K_m_per_day >= 75) & (W.K_m_per_day < 150), (W.K_m_per_day < 75)]
    mk = ['o', 's', '^']; lab = ['K $\\geq$ 150 m d$^{-1}$', '75 $\\leq$ K < 150', 'K < 75']
    ax.scatter(W.x[~has], W.y[~has], s=4, c='0.55', lw=0, zorder=7, label='other wells (DRASTIC survey)')
    for c, mm, l, col in zip(cls, mk, lab, ['#8C510A', OI[2], OI[0]]):
        ax.scatter(W.x[c & has], W.y[c & has], s=14, marker=mm, c=col, edgecolors='white', lw=0.4, zorder=8, label=l)
    import fkcl_section as SEC
    ysec = SEC.Y_SEC
    j = int(round(ysec / m.dx))
    cells = np.flatnonzero(m.valid & (m.aj == j))
    ax.plot([m.shore_row[j], m.cx[cells].max() + 0.125], [ysec, ysec], color='k', lw=1.0, zorder=9)
    ax.text(m.shore_row[j] - 0.4, ysec + 0.9, 'A', ha='right', va='center', fontweight='bold', fontsize=8, zorder=10)
    ax.text(m.cx[cells].max() + 0.5, ysec + 0.9, "A'", ha='left', va='center', fontweight='bold', fontsize=8, zorder=10)
    for _, r in G.places.iterrows():
        if r['name'].startswith('Durr'):
            continue
        ax.plot(r.x_km, r.y_km, marker='D', ms=2.6, color='0.1', zorder=9)
        dx_ = 0.6 if r['name'] not in ('Patok lagoon',) else -0.6
        ax.text(r.x_km + dx_, r.y_km, r['name'], ha='left' if dx_ > 0 else 'right', va='center', fontsize=6.4, zorder=9)
    ax.text(-5, 45, 'Adriatic\nSea', color=OI[0], fontsize=7.5, style='italic', ha='left')
    ax.text(-5.6, 24.4, 'chloride model\nsector: y $\\geq$ 24 km', fontsize=6.0, color='0.3', ha='left', va='bottom')
    h = [Line2D([], [], color=OI[1], lw=2.6, label='Adriatic contact (this study)'),
         Line2D([], [], color='0.35', lw=1.2, ls=(0, (2, 1.5)), label='inland margin, sea boundary\nin the companion model'),
         Line2D([], [], color=OI[0], lw=0.6, label='shoreline (GLOBE 1-km mask)')]
    hh, ll = ax.get_legend_handles_labels()
    fig.legend(handles=h + hh, loc='upper center', ncol=4, frameon=False, fontsize=6.2, bbox_to_anchor=(0.5, 0.0))
    panel(ax, 'a')
    # (b) aquifer-top depth
    Gd = G.grid(m.cover)
    pc = ax2.pcolormesh(G.xe, G.ye, Gd, cmap='cividis_r', vmin=0, vmax=55, shading='flat', zorder=2)
    G.outline(ax2)
    ok = W.Piezometric_Level_m.notna()
    sc = ax2.scatter(W.x[ok], W.y[ok], c=W.Piezometric_Level_m[ok], cmap='cividis_r', vmin=0, vmax=55, s=16,
                     edgecolors='k', lw=0.4, zorder=8)
    cs = ax2.contour(0.5 * (G.xe[1:] + G.xe[:-1]), 0.5 * (G.ye[1:] + G.ye[:-1]), Gd, levels=[10, 20, 30, 40],
                     colors='w', linewidths=0.5, zorder=3)
    ax2.clabel(cs, fmt='%d m', fontsize=5.5)
    cb = fig.colorbar(pc, ax=ax2, shrink=0.55, pad=0.02)
    cb.set_label('depth to the aquifer top (DRASTIC depth) [m]')
    ax2.set_yticklabels([])
    panel(ax2, 'b')
    save(fig, 'fig2_site')


# ---------------------------------------------------------------- figure 3: hydrochemistry
def hydrochem():
    x = pd.read_excel(M.fk.default_xlsx(), sheet_name='5_Cenameri2016_Chemistry', header=3).iloc[:4]
    sw35 = {'Cl': 19353, 'Na': 10781, 'Mg': 1284, 'Ca': 412, 'K': 399, 'SO4': 2712, 'HCO3': 145}
    sw = {k: v * 38.3 / 35 * 1.0285 for k, v in sw35.items()}
    Mw = {'Cl': 35.453, 'Na': 22.990, 'Ca': 40.078, 'Mg': 24.305, 'K': 39.098, 'HCO3': 61.017, 'SO4': 96.06}
    Z = {'Cl': 1, 'Na': 1, 'Ca': 2, 'Mg': 2, 'K': 1, 'HCO3': 1, 'SO4': 2}
    fr = x.iloc[3]
    out = []
    for _, r in x.iterrows():
        f = (r.Cl_mg_L - fr.Cl_mg_L) / (sw['Cl'] - fr.Cl_mg_L)
        d = {}
        for ion in ['Na', 'Ca', 'Mg', 'K', 'SO4']:
            mix = fr[ion + '_mg_L'] + f * (sw[ion] - fr[ion + '_mg_L'])
            d['d' + ion] = (r[ion + '_mg_L'] - mix) / Mw[ion] * Z[ion]
        meq = lambda ion: r[ion + '_mg_L'] / Mw[ion] * Z[ion]
        d.update(well=str(r.Well_no), f=f, Cl=r.Cl_mg_L, Na=r.Na_mg_L, TDS=r.Mp_TDS_mg_L,
                 NaCl=(r.Na_mg_L / Mw['Na']) / (r.Cl_mg_L / Mw['Cl']), revelle=meq('Cl') / meq('HCO3'),
                 BEX=meq('Na') + meq('K') + meq('Mg') - 1.0716 * meq('Cl'), pos=r.Transect_position)
        out.append(d)
    return pd.DataFrame(out), sw, fr


def fig3_hydrochem():
    H, sw, fr = hydrochem()
    tr = pd.read_excel(M.fk.default_xlsx(), sheet_name='6_Cenameri2016_Cl_Trend', header=3).iloc[:2]
    fig, axs = plt.subplots(1, 4, figsize=(190 * MM, 54 * MM), gridspec_kw=dict(wspace=0.62, width_ratios=[1, 1.15, 1, 0.9]))
    offa = {'503': (1.35, 0.62), '341': (1.35, 1.15), '340': (0.18, 1.25), '193': (1.3, 0.72)}
    offc = {'503': (0.15, -0.55), '341': (-0.95, 0.35), '340': (0.15, 0.3), '193': (0.15, 0.3)}
    col = {'503': OI[1], '341': OI[4], '340': OI[2], '193': OI[0]}
    # (a) Na vs Cl with the conservative mixing line
    ax = axs[0]
    f = np.logspace(-4, 0, 200)
    clm = fr.Cl_mg_L + f * (sw['Cl'] - fr.Cl_mg_L); nam = fr.Na_mg_L + f * (sw['Na'] - fr.Na_mg_L)
    keep = clm <= 3e4
    ax.loglog(clm[keep], nam[keep], color='0.3', lw=0.8, label='conservative mixing')
    for fm in (0.01, 0.05):
        c_ = fr.Cl_mg_L + fm * (sw['Cl'] - fr.Cl_mg_L)
        ax.plot(c_, fr.Na_mg_L + fm * (sw['Na'] - fr.Na_mg_L), 'o', ms=2, color='0.3')
        ax.text(c_ * 0.55, (fr.Na_mg_L + fm * (sw['Na'] - fr.Na_mg_L)) * 1.25, f'{100 * fm:.0f} %', fontsize=5.8, color='0.3', va='bottom')
    for _, r in H.iterrows():
        ax.plot(r.Cl, r.Na, 'o', ms=5, color=col[r.well], mec='k', mew=0.4)
        ax.text(r.Cl * offa[r.well][0], r.Na * offa[r.well][1], r.well, fontsize=6.2)
    ax.set_xlabel('Cl [mg L$^{-1}$]'); ax.set_ylabel('Na [mg L$^{-1}$]'); ax.set_xlim(8, 3e4); ax.set_ylim(8, 2e4)
    ax.legend(loc='upper left', frameon=False, fontsize=6)
    panel(ax, 'a')
    # (b) ion-exchange deviations
    ax = axs[1]
    ions = ['dNa', 'dCa', 'dMg', 'dK', 'dSO4']; lab = ['Na', 'Ca', 'Mg', 'K', 'SO$_4$']
    wl = ['503', '341', '340']
    wd = 0.25
    for k, w in enumerate(wl):
        r = H[H.well == w].iloc[0]
        ax.bar(np.arange(5) + (k - 1) * wd, [r[i] for i in ions], width=wd, color=col[w], label=f'well {w}', edgecolor='white', lw=0.3)
    ax.axhline(0, color='k', lw=0.5)
    ax.set_xticks(range(5)); ax.set_xticklabels(lab)
    ax.set_ylabel('observed $-$ mixing\n[meq L$^{-1}$]')
    ax.legend(frameon=False, loc='lower right')
    panel(ax, 'b')
    # (c) BEX vs seawater fraction
    ax = axs[2]
    ax.axhspan(0, 4, color='#E9F6F1', zorder=0); ax.axhspan(-4, 0, color='#FBEDE6', zorder=0)
    ax.text(0.2, 3.3, 'freshening', fontsize=6.2, color='0.25'); ax.text(0.2, -3.6, 'salinization', fontsize=6.2, color='0.25')
    for _, r in H.iterrows():
        ax.plot(100 * r.f, r.BEX, 'o', ms=5, color=col[r.well], mec='k', mew=0.4)
        ax.text(100 * r.f + offc[r.well][0], r.BEX + offc[r.well][1], r.well, fontsize=6.2)
    ax.axhline(0, color='k', lw=0.5)
    ax.set_xlim(-0.3, 5.8); ax.set_ylim(-4, 4)
    ax.set_xlabel('seawater fraction $f$ [%]'); ax.set_ylabel('BEX [meq L$^{-1}$]')
    panel(ax, 'c')
    # (d) chloride trend
    ax = axs[3]
    yrs = [1984, 1999, 2001]
    for _, r in tr.iterrows():
        w = str(r.Well_no)
        ax.plot(yrs, [r.Cl_1984_mg_L, r.Cl_1999_mg_L, r.Cl_2001_mg_L], '-o', ms=3.5, color=col[w], lw=1, label=f'well {w}')
    ax.set_xlabel('year'); ax.set_ylabel('Cl [mg L$^{-1}$]'); ax.set_ylim(900, 1200)
    ax.set_xticks([1985, 1995]); ax.set_xticks([1990, 2000], minor=True); ax.set_xlim(1982, 2003)
    ax.legend(frameon=False, loc='upper right')
    panel(ax, 'd')
    save(fig, 'fig3_hydrochem')
    return H


# ---------------------------------------------------------------- figure 4: calibration
def wquant(x, w, q):
    o = np.argsort(x); c = np.cumsum(w[o]); c /= c[-1]
    return x[o][np.minimum(np.searchsorted(c, q), len(x) - 1)]


def fig4_calib():
    E = np.load(os.path.join(RES, 'calib_ensemble.npz'))
    S, w = E['S'], E['weight']
    fig, axs = plt.subplots(2, 4, figsize=(190 * MM, 92 * MM), gridspec_kw=dict(hspace=0.85, wspace=0.3))
    spec = [(0, 'upper-layer area with\nCl > 250 mg L$^{-1}$ [% of aquifer]', 100, np.linspace(0, 45, 46), 15, 'T1: ~15 %'),
            (1, 'littoral head\n[m a.s.l.]', 1, np.linspace(0, 9, 46), 3.0, 'T2: ~3 m'),
            (10, 'seawater fraction, second\naquifer, 0.5-2.5 km [%]', 100, np.linspace(0, 40, 41), 4.7, 'T3a: 341, 503'),
            (4, 'upper-layer Cl, NE\nrecharge band [mg L$^{-1}$]', 1, np.linspace(12, 40, 29), None, 'T3c: < 30'),
            (3, 'seawater fraction, first\naquifer, 3-6 km [%]', 100, np.linspace(0, 2.4, 49), 1.86, 'well 340\n(held out)'),
            (14, 'seawater fraction, second\naquifer, 3-6 km [%]', 100, np.linspace(0, 2.4, 49), 1.86, 'well 340\n(held out)')]
    for k, (ci, xl, sc, bins, obs, ol) in enumerate(spec):
        ax = axs.flat[k]
        x = np.clip(S[:, ci] * sc, bins[0], bins[-1])
        ax.hist(x, bins=bins, density=True, color='0.8', label='prior')
        ax.hist(x, bins=bins, weights=w, density=True, color=OI[0], alpha=0.75, label='posterior')
        if obs is not None:
            ax.axvline(obs, color=OI[1], lw=1.2, label=ol)
        else:
            ax.axvline(30, color=OI[1], lw=1.2, ls='--', label=ol)
        ax.set_xlabel(xl); ax.set_yticks([])
        if k == 0:
            ax.legend(frameon=False, loc='upper right', fontsize=5.8)
        else:
            ax.legend(frameon=False, loc='upper right', fontsize=5.8, handles=ax.get_legend_handles_labels()[0][-1:])
        panel(ax, 'abcdefgh'[k])
    # parameters
    ax = axs.flat[6]
    R = E['R'] * 365.25 * 1000
    bins = np.linspace(0, 1000, 41)
    ax.hist(np.clip(R, 0, 1000), bins=bins, density=True, color='0.8')
    ax.hist(np.clip(R, 0, 1000), bins=bins, weights=w, density=True, color=OI[2], alpha=0.8)
    ax.axvline(5e-4 * 365.25 * 1000, color='k', lw=0.8, ls=':')
    ax.text(5e-4 * 365.25 * 1000 + 15, ax.get_ylim()[1] * 0.85, 'companion\nmodel', fontsize=5.8)
    ax.set_xlabel('net recharge R [mm yr$^{-1}$]'); ax.set_yticks([]); panel(ax, 'g')
    ax = axs.flat[7]
    bins = np.linspace(0, 100, 41)
    ax.hist(np.clip(E['w'], 0, 100), bins=bins, density=True, color='0.8')
    ax.hist(np.clip(E['w'], 0, 100), bins=bins, weights=w, density=True, color=OI[2], alpha=0.8)
    ax.set_xlabel('transition-zone half-width w [m]'); ax.set_yticks([]); panel(ax, 'h')
    save(fig, 'fig4_calib')


# ---------------------------------------------------------------- figure 5: chloride maps
def fig5_maps(G):
    m = G.m
    c = pd.read_csv(os.path.join(RES, 'post_cells.csv'))
    fig, axs = plt.subplots(2, 3, figsize=(190 * MM, 150 * MM), gridspec_kw=dict(wspace=0.06, hspace=0.12))
    names = [('sh', 'first aquifer (upper screens)'), ('mid', 'second aquifer (mid-depth)'), ('dp', 'aquifer base')]
    norm = mcolors.LogNorm(10, 21000)
    cmap = plt.get_cmap('viridis').copy(); cmap.set_bad('none')
    pmap = plt.get_cmap('magma_r').copy(); pmap.set_bad('none')
    xc = 0.5 * (G.xe[1:] + G.xe[:-1]); yc = 0.5 * (G.ye[1:] + G.ye[:-1])
    Pw = G.grid(c.P_wedge.to_numpy(), m.valid)
    for k, (lay, ttl) in enumerate(names):
        for r in range(2):
            ax = axs[r, k]
            if r == 0:
                pc = ax.pcolormesh(G.xe, G.ye, G.grid(c[f'Cl_{lay}_p50'].to_numpy(), m.valid), cmap=cmap, norm=norm, shading='flat')
                ax.set_title(ttl, fontsize=8)
            else:
                P = G.grid(c[f'P250_{lay}'].to_numpy(), m.valid)
                pp = ax.pcolormesh(G.xe, G.ye, P, cmap=pmap, vmin=0, vmax=1, shading='flat')
                ax.contour(xc, yc, np.nan_to_num(P, nan=0), levels=[0.5], colors='w', linewidths=0.8)
                if lay == 'dp':
                    ax.contour(xc, yc, np.nan_to_num(Pw, nan=0), levels=[0.05, 0.5, 0.95], colors=[OI[5], OI[0], OI[5]],
                               linewidths=[0.6, 1.0, 0.6], linestyles=['--', '-', '--'])
            G.outline(ax, sector=False)
            ax.set_aspect('equal'); ax.set_xlim(-2.5, 16.5); ax.set_ylim(23.5, 53.5)
            ax.spines['top'].set_visible(True); ax.spines['right'].set_visible(True)
            if k > 0:
                ax.set_yticklabels([])
            else:
                ax.set_ylabel('Northing from y$_0$ [km]')
            if r == 1:
                ax.set_xlabel('Easting from x$_0$ [km]')
            else:
                ax.set_xticklabels([])
            ax.text(0.03, 0.97, 'abcdef'[r * 3 + k], transform=ax.transAxes, fontweight='bold', fontsize=9, va='top')
    cb = fig.colorbar(pc, ax=axs[0, :], shrink=0.75, pad=0.015, aspect=25)
    cb.set_label('posterior median chloride [mg L$^{-1}$]')
    cb2 = fig.colorbar(pp, ax=axs[1, :], shrink=0.75, pad=0.015, aspect=25)
    cb2.set_label('P(Cl > 250 mg L$^{-1}$)')
    fig.legend(handles=[Line2D([], [], color='0.5', lw=0.8, label='P(Cl > 250 mg L$^{-1}$) = 0.5 (white line)'),
                        Line2D([], [], color=OI[0], lw=1.0, label='seawater wedge at the base: P = 0.5'),
                        Line2D([], [], color=OI[5], lw=0.6, ls='--', label='P = 0.05 and 0.95')],
               loc='upper center', ncol=3, fontsize=6.2, frameon=False, bbox_to_anchor=(0.45, 0.065))
    save(fig, 'fig5_maps')


# ---------------------------------------------------------------- figure 6: section
def fig6_section(G):
    import fkcl_section as SEC
    m = G.m
    S = np.load(os.path.join(RES, 'section_p50_fine.npz'))
    summ = json.load(open(os.path.join(RES, 'section_summary.json')))['runs']
    c = S['c']; Cl = M.CL_F + c * (float(S['Cl_s']) - M.CL_F)
    xe, ze = S['xe'] / 1000, S['ze']
    # areal sharp interface of the same member along the section row, through the cell centres
    E = np.load(os.path.join(RES, 'post_ensemble.npz'))
    p = SEC.member_params(E, summ['p50_fine']['index'])
    o = m.run(p)
    j = int(round(SEC.Y_SEC / m.dx))
    cells = np.flatnonzero(m.valid & (m.aj == j)); cells = cells[np.argsort(m.cx[cells])]
    xs_ = m.cx[cells] - m.shore_row[j]
    zt, zb, zz = o['d'][cells], o['d'][cells] + o['B'][cells], o['zeta'][cells]
    fig = plt.figure(figsize=(190 * MM, 70 * MM))
    ax = fig.add_axes([0.07, 0.17, 0.6, 0.72]); ax2 = fig.add_axes([0.79, 0.17, 0.19, 0.72])
    norm = mcolors.LogNorm(10, 21000)
    cmap = plt.get_cmap('viridis').copy(); cmap.set_bad('#EFEFEF')
    pc = ax.pcolormesh(xe, ze, np.ma.masked_invalid(Cl), cmap=cmap, norm=norm, shading='flat')
    xc = 0.5 * (xe[1:] + xe[:-1]); zc = 0.5 * (ze[1:] + ze[:-1])
    cs = ax.contour(xc, zc, np.nan_to_num(Cl, nan=0), levels=[250, 1000, 5000, 10000], colors='w', linewidths=0.6)
    ax.clabel(cs, fmt=lambda v: f'{v:.0f}', fontsize=5.6)
    ok = zz < zb
    if ok.any():
        last = np.flatnonzero(ok).max()
        xi = np.r_[xs_[:last + 1], xs_[last] + 0.5 * m.dx]
        zi = np.r_[zz[:last + 1], zb[last]]
        w = float(p['w'])
        ax.fill_between(xi, np.clip(zi - w, np.interp(xi, xs_, zt), None), np.minimum(zi + w, np.interp(xi, xs_, zb)),
                        color=OI[1], alpha=0.2, lw=0, label=f'$\\pm w$ = {w:.0f} m (calibrated)')
        ax.plot(xi, zi, color=OI[1], lw=1.1, label='sharp interface, areal model')
    ax.set_ylim(ze[-1], 0); ax.set_xlim(0, xe[-1])
    ax.set_xlabel("distance from the shoreline along A-A' [km]"); ax.set_ylabel('depth below sea level [m]')
    ax.text(0.15, 12, 'clay-silt cover (inactive)', fontsize=6.2, color='0.3')
    ax.legend(loc='lower right', fontsize=6, frameon=True, framealpha=0.9, edgecolor='none')
    cb = fig.colorbar(pc, ax=ax, pad=0.01, shrink=0.9); cb.set_label('chloride [mg L$^{-1}$]')
    panel(ax, 'a', x=-0.05)
    tags = [('p05', 'P5'), ('p50', 'P50'), ('p95', 'P95')]
    yv = np.arange(len(tags))
    ax2.plot([summ[t]['toe_strack_m'] / 1000 for t, _ in tags], yv, 's', color=OI[1], ms=4.5, label='sharp interface (areal)')
    ax2.plot([summ[t]['toe_vd_m'] / 1000 for t, _ in tags], yv, 'o', color=OI[0], ms=4.5, label='variable density')
    for aT, dy in (('0.1', -0.22), ('3.0', 0.22)):
        r = summ.get(f'p50_aT{aT}')
        if r:
            ax2.plot(r['toe_vd_m'] / 1000, 1 + dy, 'v' if dy < 0 else '^', color=OI[5], ms=3.5)
            ax2.text(r['toe_vd_m'] / 1000 + 0.12, 1 + dy, f'$\\alpha_T$ = {aT} m', fontsize=5.6, va='center')
    ax2.set_yticks(yv); ax2.set_yticklabels([f'{l} member' for _, l in tags])
    ax2.set_xlabel('toe distance from the shoreline [km]'); ax2.set_ylim(-0.6, 2.6)
    ax2.set_xlim(0, max(5.0, 1.15 * max(max(summ[t]['toe_strack_m'], summ[t]['toe_vd_m']) for t, _ in tags) / 1000))
    ax2.legend(loc='lower center', bbox_to_anchor=(0.45, 1.0), fontsize=5.8, frameon=False, ncol=1)
    panel(ax2, 'b', x=-0.3)
    save(fig, 'fig6_section')


# ---------------------------------------------------------------- figure 7: design
def fig7_design(G):
    m = G.m
    D = json.load(open(os.path.join(RES, 'design_summary.json')))['goals']
    cand = pd.read_csv(os.path.join(RES, 'design_candidates.csv'))
    fld = np.load(os.path.join(RES, 'eigfield_sh_sh.npy'))
    fig = plt.figure(figsize=(190 * MM, 96 * MM))
    ax = fig.add_axes([0.02, 0.08, 0.34, 0.86])
    pm = plt.get_cmap('YlGnBu').copy(); pm.set_bad('none')
    pc = ax.pcolormesh(G.xe, G.ye, G.grid(fld, m.valid), cmap=pm, vmin=0, vmax=1.4, shading='flat')
    G.outline(ax)
    c1 = cand[(cand.goal == 'sh') & (cand.depth == 'sh')]
    ax.scatter(c1.x_km, c1.y_km, s=5 + 18 * c1.eig_lin, c='0.2', lw=0, zorder=6, label='candidate wells')
    best3 = D['sh']['designs']['3']['exhaustive_top40']['sites']
    gr3 = D['sh']['designs']['3']['greedy']['sites']
    def xy(lbl):
        w_ = lbl.split(':')[0]; r = c1[c1.well == w_].iloc[0]; return r.x_km, r.y_km
    for s_ in best3:
        x, y = xy(s_); ax.plot(x, y, 'o', ms=8, mfc='none', mec=OI[1], mew=1.4, zorder=8)
        ax.text(x + 0.5, y, s_.split(':')[0], fontsize=6.2, color=OI[1], fontweight='bold', zorder=9)
    for s_ in gr3:
        x, y = xy(s_); ax.plot(x, y, 'x', ms=5, color=OI[4], mew=1.2, zorder=8)
    for wname in ('A13', 'A10'):
        r = G.W[G.W.Well_ID == wname].iloc[0]
        ax.plot(r.x, r.y, 'D', ms=4.5, mfc=OI[3], mec='k', mew=0.4, zorder=8)
        ax.text(r.x + 0.5, r.y, wname, fontsize=6, color=OI[3], zorder=9)
    ax.set_aspect('equal'); ax.set_xlim(-2.5, 16.5); ax.set_ylim(23.5, 53.5)
    ax.spines['top'].set_visible(True); ax.spines['right'].set_visible(True)
    ax.set_xlabel('Easting from x$_0$ [km]'); ax.set_ylabel('Northing from y$_0$ [km]')
    cb = fig.colorbar(pc, ax=ax, shrink=0.55, pad=0.02); cb.set_label('EIG of one upper-screen sample [nats]')
    ax.legend(handles=[Line2D([], [], marker='o', ls='', mfc='none', mec=OI[1], mew=1.4, ms=7, label='best triple (exhaustive)'),
                       Line2D([], [], marker='x', ls='', color=OI[4], mew=1.2, label='greedy triple'),
                       Line2D([], [], marker='D', ls='', mfc=OI[3], mec='k', mew=0.4, label='companion design, in sector')],
              loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2, fontsize=5.8, frameon=False)
    panel(ax, 'a')
    # (b) EIG vs number of samples
    ax = fig.add_axes([0.47, 0.58, 0.22, 0.36])
    ks = [1, 2, 3, 4, 5]
    for key, lab, col, mk in (('greedy', 'greedy', OI[4], 'x'), ('pair_greedy', 'pairwise greedy (SINERGO)', OI[2], 's'),
                              ('best_swap', 'best + swaps', OI[0], 'o')):
        ax.plot(ks, [D['sh']['designs'][str(k)][key]['eig_exact'] for k in ks], '-' + mk, color=col, ms=3.5, lw=0.9, label=lab)
    for k in (2, 3):
        ax.plot(k, D['sh']['designs'][str(k)]['exhaustive_top40']['eig_exact'], '*', color=OI[1], ms=7, zorder=5,
                label='exhaustive' if k == 2 else None)
    ax.axhline(D['sh']['published_in_sector_upper']['eig_exact'], color=OI[3], lw=0.8, ls='--')
    ax.text(5, D['sh']['published_in_sector_upper']['eig_exact'] + 0.05, 'A13 + A10', fontsize=6, color=OI[3], ha='right')
    ax.set_xlabel('number of samples'); ax.set_ylabel('exact EIG of the goal [nats]'); ax.set_xticks(ks)
    ax.set_ylim(0, 1.85); ax.legend(fontsize=5.6, frameon=False, loc='lower right')
    panel(ax, 'b', x=-0.18)
    # (c) depth value
    ax = fig.add_axes([0.77, 0.58, 0.21, 0.36])
    depths = ['sh', 'mid', 'dp']; dl = ['upper', 'middle', 'base']
    for g, col, off, lab in (('sh', OI[0], -0.18, 'goal: first-aquifer area'), ('mid', OI[1], 0.18, 'goal: second-aquifer area')):
        ax.bar(np.arange(3) + off, [D[g]['best_single_by_depth'][d]['eig_lin'] for d in depths], width=0.34, color=col, label=lab)
    ax.set_xticks(range(3)); ax.set_xticklabels(dl); ax.set_xlabel('sampled depth'); ax.set_ylabel('best single-sample EIG [nats]')
    ax.legend(fontsize=5.6, frameon=False, loc='upper right')
    panel(ax, 'c', x=-0.18)
    # (d) linear vs exact for the best singles (Spearman)
    ax = fig.add_axes([0.47, 0.08, 0.22, 0.34])
    for g, col in (('sh', OI[0]), ('mid', OI[1])):
        r = D[g]
        rows = [(r['designs'][str(k)][kk]['eig_lin'], r['designs'][str(k)][kk]['eig_exact'])
                for k in range(1, 6) for kk in ('greedy', 'pair_greedy', 'best_swap')]
        a = np.array(rows)
        ax.plot(a[:, 0], a[:, 1], 'o', ms=3, color=col, alpha=0.8, label=f"goal {'first' if g == 'sh' else 'second'} aquifer, "
                f"$\\rho_s$ = {r['spearman_single_linear_vs_exact']:.2f}")
    ax.plot([0, 2], [0, 2], color='0.5', lw=0.6, ls=':')
    ax.set_xlabel('linear (ensemble) EIG [nats]'); ax.set_ylabel('exact EIG [nats]'); ax.set_xlim(1, 2.05); ax.set_ylim(1, 2.05)
    ax.legend(fontsize=5.4, frameon=False, loc='upper left')
    panel(ax, 'd', x=-0.18)
    # (e) goal distribution
    ax = fig.add_axes([0.77, 0.08, 0.21, 0.34])
    E = np.load(os.path.join(RES, 'post_ensemble.npz'))
    A = ((E['Cl_sh'] > M.CL_LIMIT) & m.valid).sum(1) * m.area / 1e6
    Am = ((E['Cl_mid'] > M.CL_LIMIT) & m.valid).sum(1) * m.area / 1e6
    ax.hist(A, bins=np.linspace(0, 160, 41), color=OI[0], alpha=0.75, density=True, label='first aquifer')
    ax.hist(Am, bins=np.linspace(0, 160, 41), color=OI[1], alpha=0.6, density=True, label='second aquifer')
    ax.axvline(0.15 * 349.09, color='k', lw=0.8, ls='--')
    ax.text(0.15 * 349.09 + 2, ax.get_ylim()[1] * 0.9, '15 %', fontsize=6)
    ax.set_xlabel('area with Cl > 250 mg L$^{-1}$ [km$^2$]'); ax.set_yticks([])
    ax.set_ylim(0, ax.get_ylim()[1] * 1.35)
    ax.legend(fontsize=5.6, frameon=False, loc='upper right', ncol=2)
    panel(ax, 'e', x=-0.06)
    save(fig, 'fig7_design')


# ---------------------------------------------------------------- figure 8: toolkit
def fig8_toolkit():
    fig, axs = plt.subplots(2, 3, figsize=(190 * MM, 108 * MM), gridspec_kw=dict(hspace=0.75, wspace=0.5))
    ttl = lambda ax, t: ax.set_title(t, loc='left', fontsize=7.6, fontweight='bold')
    # (a) KRITIK-GO
    k2 = json.load(open(os.path.join(EXP, 'kritik_go', 'kritik2_results.json')))
    k1 = json.load(open(os.path.join(EXP, 'kritik_go', 'kritik_results.json')))
    ax = axs[0, 0]
    s = np.array(k2['S_POS']); Jio = np.array(k2['J_io']); J0 = np.array(k2['J0'])
    ax.axvspan(k1['xm_p10'], k1['xm_p90'], color='0.9', lw=0)
    ax.plot(s, Jio / Jio.max(), '-o', ms=3, color=OI[0], lw=1, label=f"KRITIK-GO ($\\rho_s$ = {k2['spearman_Jio_acc']:.2f})")
    ax.plot(s, J0 / J0.max(), '-s', ms=3, color='0.5', lw=1, label=f"status criterion ($\\rho_s$ = {k2['spearman_J0_acc']:.2f})")
    ax.axvline(k2['s_star'], color=OI[0], lw=0.6, ls='--'); ax.axvline(k2['s_status'], color='0.5', lw=0.6, ls='--')
    ax.text(np.mean([k1['xm_p10'], k1['xm_p90']]), 0.55, 'critical\ntoe', ha='center', fontsize=5.6, color='0.35')
    ax.set_xlabel('logger distance from the coast [m]'); ax.set_ylabel('criterion / max'); ax.set_ylim(0, 1.45)
    ax.legend(fontsize=5.4, frameon=False, loc='upper left'); ttl(ax, 'a  KRITIK-GO: early warning')
    # (b) KRAMERS-GO
    kr = json.load(open(os.path.join(EXP, 'kramers_go', 'kramers_results.json')))
    ax = axs[0, 1]
    T = np.array(kr['TS'])
    med = [kr['E2']['fsafe'][str(t)] for t in T]
    F3 = np.array([[d['fsafe'][str(t)] for t in T] for d in kr['E3']])
    ax.fill_between(T, np.quantile(F3, 0.1, 0), np.quantile(F3, 0.9, 0), color=OI[4], alpha=0.25, lw=0, label='10-90 % over K, q$_0$')
    ax.semilogx(T, med, '-o', color=OI[4], ms=3, lw=1, label='prior median parameters')
    ax.set_xlabel('return period T [yr]'); ax.set_ylabel('safe pumping Q$_T$ / Q$_c$'); ax.set_ylim(0.4, 1.0)
    ax.legend(fontsize=5.6, frameon=False, loc='lower left'); ttl(ax, 'b  KRAMERS-GO: safe pumping')
    # (c) SAFE-GO / KALIB-GO
    sg = json.load(open(os.path.join(EXP, 'safe_go', 'safego_results.json')))
    kg = json.load(open(os.path.join(EXP, 'kalib_go', 'kalibgo_results.json')))
    ax = axs[0, 2]
    ne = sorted(int(k) for k in sg['E1'])
    ax.axhline(0.9, color='0.6', lw=0.6, ls=':')
    ax.plot(ne, [sg['E1'][str(n)]['bayes']['cov'] for n in ne], '-o', ms=3, color='0.4', lw=1, label='Bayes')
    ax.plot(ne, [sg['E1'][str(n)]['safe10']['cov'] for n in ne], '-s', ms=3, color=OI[2], lw=1, label='SAFE-GO')
    ax.plot(ne, [kg['E1'][str(n)]['kalib']['cov'] for n in ne], '-^', ms=3, color=OI[0], lw=1, label='KALIB-GO')
    ax.set_xlabel('exact coastal readings'); ax.set_ylabel('coverage of the 90 % toe interval'); ax.set_ylim(0.4, 1.02)
    ax.set_ylabel('coverage of the 90 %\ntoe interval')
    ax.legend(fontsize=5.6, frameon=False, loc='lower left'); ttl(ax, 'c  SAFE-GO / KALIB-GO')
    # (d) ATRIB-GO
    at = json.load(open(os.path.join(EXP, 'atrib_go', 'atrib_results.json')))['A2']['designs']
    ax = axs[1, 0]
    keys = ['none', 'time', 'toe_100', 'toe_50', 'rain_y_0.10', 'rain_y_0.05', 'rain_y_0.02', 'rain_q_0.02']
    lab = ['event only', '+ date', 'toe, 100 m', 'toe, 50 m', 'recharge, yr, 10 %', 'recharge, yr, 5 %', 'recharge, yr, 2 %', 'recharge, qtr, 2 %']
    cols = ['0.6', '0.6', OI[0], OI[0], OI[2], OI[2], OI[2], OI[2]]
    ax.barh(np.arange(len(keys)), [100 * at[k]['conf'] for k in keys], color=cols)
    ax.set_yticks(range(len(keys))); ax.set_yticklabels(lab, fontsize=6); ax.invert_yaxis()
    ax.set_xlabel('events attributed with confidence [%]'); ttl(ax, 'd  ATRIB-GO: attribution')
    # (e) KUFI-GO
    ku = json.load(open(os.path.join(EXP, 'kufi_go', 'kufi_results.json')))['res']
    ax = axs[1, 1]
    rules = ['plugin', 'point', 'band', 'msm', 'band_first']; rl = ['plug-\nin', 'point-\nwise', 'simult.\nband', 'MSM\nband', 'first\ncross.']
    v_obs = [100 * ku['1000|op+D']['0.35'][r]['viol'] for r in rules]
    ax.bar(np.arange(len(rules)), v_obs, color=[OI[1], OI[4], OI[0], OI[5], OI[2]])
    ax.axhline(5, color='0.5', lw=0.6, ls=':')
    ax.set_xticks(range(len(rules))); ax.set_xticklabels(rl, fontsize=5.8)
    ax.set_ylabel('chosen threshold unsafe [%]'); ttl(ax, 'e  KUFI-GO: threshold choice')
    # (f) KTHIMI-GO
    kt = json.load(open(os.path.join(EXP, 'kthimi_go', 'kthimi_results.json')))
    ax = axs[1, 2]
    d = [x for x in kt['designs'] if not x['nomon']]
    nm = [x for x in kt['designs'] if x['nomon']][0]
    kap = sorted(set(x['kappa'] for x in d))
    for i, k in enumerate(kap):
        dd = [x for x in d if x['kappa'] == k]
        ax.plot([1000 * x['feedback'] for x in dd], [100 * x['risk'] for x in dd], 'o', ms=3.2, color=plt.get_cmap('Blues')(0.35 + 0.18 * i),
                label=f'$\\kappa$ = {k:g}')
    ax.plot(0, 100 * nm['risk'], 'D', color=OI[1], ms=4, label='no monitoring')
    ax.set_xlabel('feedback information [mbit per decision]'); ax.set_ylabel('10-yr salinization risk [%]')
    ax.text(0.97, 0.97, f"$\\rho_s$ = {kt['rho_feedback']:.2f}\n(sensor information: {kt['rho_sensor']:.2f})", transform=ax.transAxes,
            ha='right', va='top', fontsize=6)
    ax.legend(fontsize=5.4, frameon=False, loc='lower left'); ttl(ax, 'f  KTHIMI-GO: feedback')
    save(fig, 'fig8_toolkit')


# ---------------------------------------------------------------- figure S1: PRAG-MAR, geolocated boundary
def figS1_prag_mar(G):
    """PRAG-MAR recomputed with the geolocated sea boundary (experiments/prag_go_fushe_kuqe/fk_mar_geo.py)."""
    R = os.path.join(EXP, 'prag_go_fushe_kuqe', 'res_geo')
    J = json.load(open(os.path.join(R, 'mar_geo.json')))
    Je = json.load(open(os.path.join(R, 'mar_geo_equal.json')))
    F = np.load(os.path.join(R, 'mar_geo_fields.npz'))
    m = G.m; v = F['valid']
    fig = plt.figure(figsize=(190 * MM, 100 * MM))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.25], wspace=0.32, left=0.06, right=0.98, bottom=0.27, top=0.93)
    sup = [J['supply']['A'], J['supply']['B']]
    for p, (key, ttl, sites) in enumerate([('RISK_c', 'PRAG-MAR field', 'prag'), ('MAR_c', 'area-adjoint field', 'area')]):
        ax = fig.add_subplot(gs[0, p])
        f = F[key] / F[key][v].max()
        pc = ax.pcolormesh(G.xe, G.ye, G.grid(f, v), cmap='YlGnBu', vmin=0, vmax=1, shading='flat', rasterized=True)
        G.outline(ax, lw=0.6)
        G.sea_contact(ax, color=OI[1], lw=2.0, solid_capstyle='butt', zorder=6)
        ax.plot([s['x'] for s in sup], [s['y'] for s in sup], 'v', ms=6, mfc=OI[4], mec='k', mew=0.6, zorder=8)
        for s in J[sites]['sites']:
            ax.plot(s['x'], s['y'], 'o', ms=8, mfc='none', mec='k', mew=1.4, zorder=9)
        if p == 1:
            for s in J['published']['sites']:
                if s['in_sector']:
                    ax.plot(s['x'], s['y'], 's', ms=6, mfc='none', mec=OI[3], mew=1.3, zorder=9)
        ax.set_xlim(-2.5, 14); ax.set_ylim(23.5, 53.5); ax.set_aspect('equal')
        ax.set_xlabel('Easting from $x_0$ [km]'); ax.set_title(ttl, fontsize=8)
        if p == 0:
            ax.set_ylabel('Northing from $y_0$ [km]')
            for s, nm in zip(sup, ['A', 'B']):
                ax.annotate(f"{nm} ({s['id']})", (s['x'], s['y']), xytext=(7, 3 if nm == 'A' else -9),
                            textcoords='offset points', fontsize=6.5, zorder=10)
        else:
            ax.set_yticklabels([])
        panel(ax, 'ab'[p])
    cax = fig.add_axes([0.08, 0.075, 0.38, 0.016])
    cb = fig.colorbar(pc, cax=cax, orientation='horizontal'); cb.set_label('reduction per unit recharge (scaled to its maximum)', fontsize=6.5)
    cb.ax.tick_params(labelsize=6)
    ax = fig.add_subplot(gs[0, 2])
    lab = {'published': 'published sites', 'area': 'area adjoint', 'prag': 'PRAG-MAR', 'ens': 'exact optimum'}
    col = {'published': OI[3], 'area': OI[0], 'prag': OI[1], 'ens': OI[2]}
    for nm in ['published', 'area', 'prag', 'ens']:
        for JJ, ls, lw, mk in [(J, '-', 1.3, 'o'), (Je, '--', 0.9, None)]:
            x = [0] + [r['Q'] / 1000 for r in JJ[nm]['rows']]
            y = [JJ['none']['pAB']] + [r['pAB'] for r in JJ[nm]['rows']]
            ax.plot(x, y, ls=ls, lw=lw, marker=mk, ms=3.5, color=col[nm], label=lab[nm] if ls == '-' else None)
    ax.plot([], [], 'k-', lw=1.3, label='each well P = 1/2'); ax.plot([], [], 'k--', lw=0.9, label='equal pumping')
    ax.set_xlabel('recharge per site [10$^3$ m$^3$ d$^{-1}$]'); ax.set_ylabel('P(supply well A or B intruded)')
    ax.set_ylim(0, 0.8); ax.set_xlim(-0.3, 10.3)
    ax.legend(frameon=False, fontsize=6.3, loc='upper right')
    panel(ax, 'c')
    h = [Line2D([], [], marker='v', ls='', mfc=OI[4], mec='k', ms=6, label='supply wells'),
         Line2D([], [], marker='o', ls='', mfc='none', mec='k', mew=1.4, ms=7, label='recharge sites of the design'),
         Line2D([], [], marker='s', ls='', mfc='none', mec=OI[3], mew=1.3, ms=6, label='published site in the sector'),
         Line2D([], [], color=OI[1], lw=2, label='Adriatic contact')]
    fig.legend(handles=h, loc='lower right', bbox_to_anchor=(0.99, 0.0), ncol=2, frameon=False, fontsize=6.3)
    save(fig, 'figS1_prag_mar_geo')


if __name__ == '__main__':
    G = Geo()
    fig1_framework(); fig2_site(G); fig3_hydrochem(); fig4_calib(); fig5_maps(G); fig6_section(G); fig7_design(G); fig8_toolkit()
    if os.path.exists(os.path.join(EXP, 'prag_go_fushe_kuqe', 'res_geo', 'mar_geo.json')):
        figS1_prag_mar(G)
    print('figures written to', os.path.abspath(OUT))
