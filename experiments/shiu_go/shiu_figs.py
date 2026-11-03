"""Figures of the SHIU-GO note (Albanian labels). usage: python shiu_figs.py OUT_DIR"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.ticker
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shiu_model as SM  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
INK, MUTED, GRID = '#1f2328', '#5b6672', '#e3e6ea'
COL = {'truth': INK, 'oracle': '#3d4652', 'M0': '#B45309', 'M1': '#8796a5', 'B': '#6a4fb3', 'A': '#2E8B57',
       'rain': '#9fb1c4', 'sat': '#C27C12'}
LAB = {'oracle': 'ligji i vërtetë', 'M0': 'M0: Gausian (OU)', 'M1': 'M1: transferim linear i shiut',
       'A': 'Rruga A: SDE me kërcime', 'B_ls': 'Rruga B: të gjitha termat', 'B_bic': 'Rruga B: BIC',
       'B_eills4': 'Rruga B: invariancë'}
FS = 8.6
plt.rcParams.update({'font.size': FS, 'axes.titlesize': 9.4, 'axes.labelsize': 8.8, 'xtick.labelsize': FS,
                     'ytick.labelsize': FS, 'legend.fontsize': FS, 'font.family': 'DejaVu Sans'})


def style(ax):
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    ax.grid(color=GRID, lw=0.7)
    ax.set_axisbelow(True)


# ------------------------------------------------------------------------------------------------ figure 1: the system
def fig_system(path):
    fig, ax = plt.subplots(figsize=(6.9, 4.9), dpi=300)
    ax.set_xlim(0, 100); ax.set_ylim(0, 70); ax.axis('off')

    def box(x, y, w, h, title, body, fc, ec):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.6,rounding_size=1.6', fc=fc, ec=ec, lw=1.1))
        ax.text(x + w / 2, y + h - 2.6, title, ha='center', va='top', fontsize=8.9, fontweight='bold', color=INK)
        ax.text(x + w / 2, y + h - 7.4, body, ha='center', va='top', fontsize=8.6, color=INK, linespacing=1.25)

    def arrow(x0, y0, x1, y1, c=MUTED, rad=0.0, ls='-'):
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='-|>', color=c, lw=1.2, shrinkA=2, shrinkB=2, ls=ls,
                                    connectionstyle=f'arc3,rad={rad}', mutation_scale=10))
    fa, ea = '#eaf3ee', '#2E8B57'
    box(1, 52, 22, 16, 'Shiu', 'proces Poisson\nme shenja\nλ(t), ā(t)', fa, ea)
    box(26, 52, 22, 16, 'Toka', 'SDE me kërcime\nET, kullim L(s)', fa, ea)
    box(51, 52, 22, 16, 'Zona e pangopur', 'kujtesë κ(u)\n(Erlang)', fa, ea)
    box(76, 52, 23, 16, 'Rimbushja', 'R(t)(1 + e(t))\ne: proces OU', fa, ea)
    arrow(23.6, 60, 25.4, 60); arrow(48.6, 60, 50.4, 60); arrow(73.6, 60, 75.4, 60)
    fb, eb = '#eef2fb', '#2E6DB4'
    box(8, 27, 36, 17, 'Ekuacioni i filtrimit (rrjedhjes)', 'h(x,t): Darcy + rimbushje + pompim\n+ mbyllje Σγ Ψ + kujtesë ∫κ h', fb, eb)
    box(56, 27, 36, 17, 'Ekuacioni i transportit', 'c(x,t): kujtesë, hollim nga rimbushja\n+ kërcime nga stuhitë (overwash)', fb, eb)
    arrow(87, 51.4, 30, 44.6, c=ea, rad=0.08)
    arrow(90, 51.4, 78, 44.6, c=ea, rad=-0.05)
    ax.annotate('', xy=(55.4, 37), xytext=(44.6, 37), arrowprops=dict(arrowstyle='<|-|>', color=eb, lw=1.2, mutation_scale=10))
    ax.text(50, 38.6, 'dendësia', ha='center', fontsize=8.6, color=MUTED)
    ax.text(1.0, 47.8, 'deti η(t): OU + stuhi (kërcime)\npompimi Q(t)', ha='left', va='center', fontsize=8.6,
            color=MUTED, linespacing=1.3)
    fo, eo = '#fbf4ea', '#C27C12'
    box(1, 2, 30, 18, 'Vëzhgimet', 'kohë të rastit t_i, maska M_i:\nngarkesa, klorur, shi,\nlagështi, niveli i detit', fo, eo)
    box(35, 2, 30, 18, 'Filtri', 'fizikë midis vëzhgimeve\n+ kërcim në vëzhgim\n→ E[X(t) | A(t)]', fo, eo)
    box(69, 2, 30, 18, 'Zbulimi', 'humbja e parashikimit:\nA, SDE veçmas;\nB, shtesë + zgjedhje shkakësore', fo, eo)
    arrow(31.6, 11, 34.4, 11); arrow(65.6, 11, 68.4, 11)
    arrow(26, 26.4, 26, 20.6, c=eb); arrow(74, 26.4, 74, 20.6, c=eb)
    arrow(99.5, 20.6, 99.5, 51.4, c=eo, ls='--')
    ax.text(98.2, 23.4, 'ligji i forcimit', ha='right', va='center', fontsize=8.6, color=eo)
    fig.tight_layout(pad=0.2)
    fig.savefig(path, dpi=300); plt.close(fig)


# ------------------------------------------------------------------------------------------------ figure 2: one twin
def fig_twin(path, run):
    aq = SM.aquifer()
    tw = SM.simulate_twin(run['seed'], aq)
    n = len(tw['t'])
    pa, p0 = run['A']['par'], run['M0']['par']
    RdA = SM.recharge_det(tw['P'], tw['Ep'], pa['sfc'], pa['kL'], pa['bL'], pa['tau'], nsub=6)[0]
    rA = SM.run_filter(aq, tw, RdA, 'mult', pa['sig_e'], pa['tau_e'])
    r0 = SM.run_filter(aq, tw, np.full(n, p0['Rbar']), 'add', p0['sig'], p0['tau'])
    lo, hi = 9 * SM.YEAR, 11 * SM.YEAR
    d = np.arange(lo, hi)
    yrs = (d - lo) / 365.0 + 9
    fig, axs = plt.subplots(3, 1, figsize=(6.9, 6.2), dpi=300, sharex=True,
                            gridspec_kw=dict(height_ratios=[0.8, 1.1, 1.6]))
    ax = axs[0]
    ax.bar(yrs, tw['P'][lo:hi], width=1 / 365.0, color=COL['rain'])
    ax.set_ylabel('shiu (mm/d)'); style(ax)
    ax.set_title('(a) Shiu ditor, vitet 9–10 të testit (viti 10: thatësirë)', loc='left', color=INK)
    ax = axs[1]
    m = lambda x: x[lo:hi].reshape(-1, 30 if (hi - lo) % 30 == 0 else 1)
    k = (hi - lo) // 30
    mm = lambda x: x[lo:lo + 30 * k].reshape(k, 30).mean(1)
    xm = yrs[:30 * k].reshape(k, 30).mean(1)
    ax.plot(xm, mm(tw['R']), color=COL['truth'], lw=2.0, label='e vërteta')
    ax.plot(xm, mm(RdA * (1 + rA['xm'])), color=COL['A'], lw=1.8, label=LAB['A'])
    ax.plot(xm, mm(p0['Rbar'] + r0['xm']), color=COL['M0'], lw=1.6, ls='--', label=LAB['M0'])
    ax.set_ylabel('rimbushja (mm/d)'); style(ax)
    ax.legend(frameon=False, loc='upper right', ncol=1)
    ax.set_title('(b) Rimbushja mesatare mujore e filtruar', loc='left', color=INK)
    ax = axs[2]
    j = 1
    ax.plot(yrs, tw['X'][lo:hi, j], color=COL['truth'], lw=1.4, label='ngarkesa e vërtetë')
    mu, sd = rA['hm'][lo:hi, j], np.sqrt(rA['hv'][lo:hi, j] + SM.SIG_O ** 2)
    ax.fill_between(yrs, mu - 1.645 * sd, mu + 1.645 * sd, color=COL['A'], alpha=0.18, lw=0)
    ax.plot(yrs, mu, color=COL['A'], lw=1.3, label='Rruga A: mesatarja e filtrit, 90%')
    ax.plot(yrs, r0['hm'][lo:hi, j], color=COL['M0'], lw=1.2, ls='--', label=LAB['M0'])
    ob = tw['mask'][lo:hi, j]
    ax.plot(yrs[ob], tw['y'][lo:hi, j][ob], 'o', ms=3.2, color='#2E6DB4', mec='white', mew=0.4,
            label='vëzhgime (kohë të rastit)')
    ax.set_ylabel('ngarkesa (m)'); ax.set_xlabel('viti i simulimit'); style(ax)
    ax.legend(frameon=False, loc='lower left', ncol=2)
    ax.set_title(f'(c) Ngarkesa në piezometrin në {int(aq["piezo"][j])} m nga deti', loc='left', color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=300); plt.close(fig)


# ------------------------------------------------------------------------------------------------ figure 3: results
def fig_results(path, J):
    runs = J['runs']
    models = [('M0', lambda r: r['M0']['test']['loss']), ('M1', lambda r: r['M1']['test']['loss']),
              ('B_ls', lambda r: r['B']['ls']['test']), ('B_bic', lambda r: r['B']['bic']['test']),
              ('B_eills4', lambda r: r['B']['eills4']['test']), ('A', lambda r: r['A']['test']['loss'])]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.9, 3.6), dpi=300, gridspec_kw=dict(width_ratios=[1.25, 1]))
    for i, (k, f) in enumerate(models):
        v = np.array([100 * (f(r) / r['oracle']['test']['loss'] - 1) for r in runs])
        c = COL['B'] if k.startswith('B') else COL[k]
        ax.scatter(np.full(len(v), i) + np.linspace(-0.12, 0.12, len(v)), v, s=11, color=c, alpha=0.55, lw=0)
        ax.plot([i - 0.28, i + 0.28], [np.median(v)] * 2, color=c, lw=2.4)
        # the median sits in one row above all clouds, so a label never runs into the next group
        ax.text(i, 1150, f'{np.median(v):.0f}%', ha='center', va='center', fontsize=FS, color=INK, fontweight='bold')
    ax.set_yscale('symlog', linthresh=10)
    ax.set_ylim(top=1900)
    ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.set_yticks([0, 10, 30, 100, 300]); ax.set_yticklabels(['0', '10', '30', '100', '300'])
    ax.set_xlim(-0.5, len(models) - 0.2)
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(['M0', 'M1', 'B: të\ngjitha', 'B:\nBIC', 'B: inva-\nriancë', 'A'], fontsize=FS)
    ax.set_ylabel('humbja e parashikimit mbi\nligjin e vërtetë, vitet e testit (%)')
    ax.set_title('(a) Sa larg nga parashikimi optimal', loc='left', color=INK)
    style(ax)
    gl = ['1–3', '4–7', '8–14', '>14']
    for k in ('M0', 'M1', 'A', 'oracle'):
        g = np.array([[r[k]['gap'][i] for i in range(4)] for r in runs])
        bx.plot(range(4), 1e4 * np.median(g, 0), marker='o', ms=4, color=COL[k], lw=1.6, label=LAB[k])
    bx.set_xticks(range(4)); bx.set_xticklabels(gl)
    bx.set_xlabel('ditë nga vëzhgimi i fundit')
    bx.set_ylabel('gabimi katror mesatar (cm²)')
    bx.set_title('(b) Gabimi sipas boshllëkut', loc='left', color=INK)
    style(bx); bx.legend(frameon=False, fontsize=FS, loc='upper left')
    fig.tight_layout()
    fig.savefig(path, dpi=300); plt.close(fig)


# ------------------------------------------------------------------------------------------------ figure 4: route B
def fig_routeB(path, J):
    S = J['summary']
    feats = J['params']['FEATS']
    names = {'P5': 'shi 5 d', 'P20': 'shi 20 d', 'P60': 'shi 60 d', 'P180': 'shi 180 d', 'E20': 'ET 20 d',
             'X40': 'tepricë', 'cos': 'cos', 'sin': 'sin', 'one': 'konst.'}
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.9, 3.5), dpi=300, gridspec_kw=dict(width_ratios=[1.35, 1]))
    x = np.arange(len(feats))
    for off, key, c, lab in ((-0.2, 'bic', '#9aa8b6', 'BIC'), (0.2, 'eills4', COL['B'], 'invariancë (γ = 4)')):
        ax.bar(x + off, [100 * S['B'][key]['freq'][f] for f in feats], width=0.38, color=c, label=lab)
    ax.axvspan(5.5, 8.5, color='#f5efe4', zorder=0)
    ax.text(7.0, 104, 'jo-shkaqe', ha='center', fontsize=FS, color=MUTED)
    ax.set_xticks(x); ax.set_xticklabels([names[f] for f in feats], rotation=45, ha='right')
    ax.set_ylim(0, 112); ax.set_ylabel('binjakë ku termi zgjidhet (%)')
    ax.set_title('(a) Termat e zgjedhur në Rrugën B', loc='left', color=INK)
    style(ax); ax.grid(axis='x', visible=False); ax.legend(frameon=False, loc='upper left', fontsize=FS)
    rows = [('M0', S['M0']['drought_rel_err']), ('M1', S['M1']['drought_rel_err']),
            ('B: BIC', S['B']['bic']['drought_rel_err']), ('B: invar.', S['B']['eills4']['drought_rel_err']),
            ('A', S['A']['drought_rel_err']), ('i vërtetë', S['oracle']['drought_rel_err'])]
    cs = [COL['M0'], COL['M1'], '#9aa8b6', COL['B'], COL['A'], COL['oracle']]
    for i, ((lab, v), c) in enumerate(zip(rows, cs)):
        bx.plot([100 * v['q25'], 100 * v['q75']], [i, i], color=c, lw=2.4, solid_capstyle='round')
        bx.plot(100 * v['med'], i, 'o', color=c, ms=6, mec='white')
    bx.axvline(0, color=INK, lw=0.8)
    bx.set_yticks(range(len(rows))); bx.set_yticklabels([r[0] for r in rows])
    bx.invert_yaxis()
    bx.set_xlabel('gabimi i rimbushjes në vitin\ne thatësirës (%, mediana, 25–75%)')
    bx.set_title('(b) Rimbushja në thatësirë', loc='left', color=INK)
    style(bx)
    fig.tight_layout()
    fig.savefig(path, dpi=300); plt.close(fig)


# ------------------------------------------------------------------------------------------------ figure 5: route A by Kramers-Moyal
def fig_km(path, K):
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.9, 3.4), dpi=300)
    mth = np.arange(1, 13)
    ax.plot(mth, [a for a, b in K['true_month']], color=INK, lw=1.8, label='e vërteta')
    pj = np.array([a for a, b, c in K['probe_jumps']], float)
    ax.plot(mth, pj, 'o', color=COL['A'], ms=5, label='sondë orare: kërcimet')
    sk = np.array([a for a, b, c in K['sat_km']], float)
    ok = np.isfinite(sk)
    ax.plot(mth[ok], np.clip(sk[ok], 0, 0.8), 'x', color=COL['sat'], ms=6, mew=1.6, label='satelit 3–6 d: KM')
    ax.set_xticks([1, 3, 5, 7, 9, 11]); ax.set_xticklabels(['jan', 'mar', 'maj', 'kor', 'sht', 'nën'])
    ax.set_ylabel('ngjarje shiu në ditë, λ'); ax.set_ylim(0, 0.8)
    ax.set_title('(a) Ligji i kërcimeve të shiut', loc='left', color=INK)
    style(ax); ax.legend(frameon=False, loc='upper center', fontsize=FS)
    sys.path.insert(0, HERE)
    import shiu_km as KM
    sg = np.linspace(20, 195, 120)
    pt = dict(cE=1.0, sw=120.0, sfc=130.0, kL=25.0, bL=3.0)
    for ep, ls in ((5.0, '-'), (0.6, ':')):
        bx.plot(sg, KM.drift_model(pt, sg, ep), color=INK, lw=1.8, ls=ls)
        bx.plot(sg, KM.drift_model(K['probe_drift'], sg, ep), color=COL['A'], lw=1.4, ls=ls)
        bx.plot(sg, KM.drift_model(K['satgauge_drift'], sg, ep), color=COL['sat'], lw=1.4, ls=ls)
    bx.plot([], [], color=INK, label='e vërteta'); bx.plot([], [], color=COL['A'], label='sondë orare')
    bx.plot([], [], color=COL['sat'], label='satelit + shimatës')
    bx.plot([], [], color=MUTED, ls='-', label='verë (ET 5 mm/d)'); bx.plot([], [], color=MUTED, ls=':', label='dimër (ET 0,6 mm/d)')
    bx.set_xlabel('lagështia e tokës s (mm)'); bx.set_ylabel('drifti (mm/d)')
    bx.set_title('(b) Drifti i SDE-së së tokës', loc='left', color=INK)
    style(bx); bx.legend(frameon=False, loc='lower left', fontsize=FS)
    fig.tight_layout()
    fig.savefig(path, dpi=300); plt.close(fig)


def main(od):
    os.makedirs(od, exist_ok=True)
    with open(os.path.join(HERE, 'res', 'shiu_exp.json')) as fh:
        J = json.load(fh)
    with open(os.path.join(HERE, 'res', 'shiu_km.json')) as fh:
        K = json.load(fh)
    fig_system(os.path.join(od, 'fig_system.png'))
    fig_twin(os.path.join(od, 'fig_twin.png'), J['runs'][0])
    fig_results(os.path.join(od, 'fig_results.png'), J)
    fig_routeB(os.path.join(od, 'fig_routeB.png'), J)
    fig_km(os.path.join(od, 'fig_km.png'), K)
    print('figures in', od)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'figs'))
