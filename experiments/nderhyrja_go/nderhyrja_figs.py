"""Figures of the NDERHYRJA-GO review (English labels; every text at least 8.6 pt at the printed size, 17 cm wide).
usage: python nderhyrja_figs.py OUT_DIR

fig_scheme   (a) who interferes with a CERTAIN-COAST piezometer; (b) the NDERHYRJA-GO loop
fig_bed      the test bed and two 10-sensor designs (interference ignored; NDERHYRJA-GO)
fig_t33      reference channels: value against the number of piezometers; designs against the correction ceiling
fig_t34      worst-case information of six design rules and the certified upper bound (T34, T35)
fig_t36      the correction in operation: calibration, corrected heads, one season at one piezometer
Numbers come from res/nderhyrja.json and res/nderhyrja_case.npz."""
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
sys.path.insert(1, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', 'rindertimi_go'))
import gar_figs as GF  # noqa: E402
from rgo_figs import Canvas, INK, MUTED  # noqa: E402

RES = os.path.join(HERE, 'res')
MM = GF.MM
FS = GF.FS
BLUE, ORANGE, AQUA, VIOLET, REF = GF.BLUE, GF.ORANGE, GF.AQUA, GF.VIOLET, GF.REF
COR = VIOLET            # correctable interference
NCOR = '#c4563a'        # not correctable
SIGC = BLUE             # signal
REFC = AQUA             # reference channels
RULES = ['indep', 'naive', 'nominal_norefs', 'robust_norefs', 'nominal', 'nderhyrja']
NAME = dict(indep='interference ignored', naive='naive correlated weighting', nominal_norefs='exact, no references',
            robust_norefs='robust, no references', nominal='exact + references (nominal)',
            nderhyrja='NDERHYRJA-GO (robust + references)')
COL = dict(indep='#8a9099', naive='#b58a3c', nominal_norefs='#7aa7d8', robust_norefs='#2f5f99', nominal='#5fc79f',
           nderhyrja=ORANGE)
MARK = dict(indep='o', naive='v', nominal_norefs='s', robust_norefs='D', nominal='^', nderhyrja='*')


def load():
    with open(os.path.join(RES, 'nderhyrja.json')) as fh:
        R = json.load(fh)
    case = dict(np.load(os.path.join(RES, 'nderhyrja_case.npz'), allow_pickle=True))
    return R, case


def style(ax, grid='y'):
    GF.style(ax, grid)
    ax.tick_params(labelsize=FS)


def node(cv, x, y, w, h, label, kind, sub=None):
    st = dict(sig=('#e3eefb', SIGC, '-'), cor=('#efecfb', COR, '--'), ncor=('#fbe9e4', NCOR, '--'),
              ref=('#e2f5ee', REFC, '-'), obs=('#eef0f2', '#5b6672', '-'), step=('white', INK, '-'),
              key=('#fff4e8', ORANGE, '-'))[kind]
    cv.box(x - w / 2, y - h / 2, w, h, st[0], st[1], lw=1.0, r=1.8, ls=st[2])
    if sub:
        cv.text(x, y + 1.7, label, color=INK)
        cv.text(x, y - 1.9, sub, color=MUTED)
    else:
        cv.text(x, y, label, color=INK)


def fig_scheme(out):
    cv = Canvas(170, 128)
    t = cv.text

    def arr(x0, y0, x1, y1, c, lw=1.0, ls='-', rad=0.0):
        cv.ax.annotate('', xy=(x1, y1), xytext=(x0, y0), zorder=25,
                       arrowprops=dict(arrowstyle='-|>', color=c, lw=lw, ls=ls, shrinkA=0, shrinkB=0,
                                       connectionstyle=f'arc3,rad={rad}', mutation_scale=8))
    # ---- (a) who interferes
    t(2, 124, '(a) Who interferes with a reading?', ha='left', size=9.4, weight='bold')
    node(cv, 40, 109, 48, 9, 'aquifer state m', 'sig', 'recharge / salinity anomaly')
    node(cv, 40, 91, 34, 9, 'head h = Fm', 'sig', 'at the well screen')
    node(cv, 38, 64, 52, 10, 'piezometer reading y', 'obs', 'unvented transducer, metres')
    arr(40, 104.5, 40, 95.5, SIGC, lw=1.4)
    arr(40, 86.5, 40, 69, SIGC, lw=1.4)
    node(cv, 12.5, 42, 23, 9, 'air pressure', 'cor', 'all wells')
    node(cv, 39, 42, 23, 9, 'logger drift', 'cor', 'per hub')
    node(cv, 66, 42, 27, 9, 'cable cross-talk', 'ncor', 'per nest')
    node(cv, 68, 80, 23, 9, 'model error', 'ncor', 'correlated, ℓ')
    arr(15, 46.5, 26, 59, COR, ls='--')
    t(10, 54, 'BEᵢ + δᵢ', color=COR)
    arr(39, 46.5, 39, 59, COR, ls='--')
    arr(62, 46.5, 53, 59, NCOR, ls='--')
    arr(62, 75.5, 56, 69, NCOR, ls='--')
    node(cv, 12.5, 22, 23, 9, 'barometer', 'ref', 'reference')
    node(cv, 39, 22, 27, 9, 'hub channel', 'ref', 'sealed reference')
    arr(12.5, 37.5, 12.5, 26.5, COR, ls='--')
    arr(39, 37.5, 39, 26.5, COR, ls='--')
    t(2, 9, 'Violet: correctable — reference channels see the\nsources, which are marginalised (N1, N2).\n'
            'Red: not correctable — kept in Γ and in the box.',
      ha='left', va='center', color=MUTED, linespacing=1.25)
    cv.line([82, 82], [2, 124], c='#c9ced6', lw=0.6)
    # ---- (b) the loop
    t(86, 124, '(b) NDERHYRJA-GO', ha='left', size=9.4, weight='bold')
    steps = [(115, 'data space: K = FCFᵀ,  Γ(θ)', 'nₛ adjoint solves, once'),
             (103, 'amplitudes at their upper ends', 'Proposition N3 (monotone)'),
             (91, 'robust greedy over scenarios', 'max over j of min over θ'),
             (79, 'exchange (swap one in, one out)', 'while the worst case improves'),
             (67, 'adversary on (ℓ, δ)', 'exact data-space gradient (N3)'),
             (51, 'certificate Ū (Proposition N4)', 'relaxation + ceiling + references'),
             (37, 'deploy: correct the data', 'ĉ, y − Bĉ, calibrated forecast'),
             (24, 'check the residuals', 'cross-correlation after correction')]
    for y, a, b in steps:
        node(cv, 124, y, 60, 9, a, 'key' if y in (51, 37) else 'step', b)
    for (y0, _, _), (y1, _, _) in zip(steps[:-1], steps[1:]):
        arr(124, y0 - 4.5, 124, y1 + 4.5, INK)
    cv.line([154, 159], [67, 67], c=NCOR, lw=1.0)
    cv.line([159, 159], [67, 91], c=NCOR, lw=1.0)
    arr(159, 91, 154.2, 91, NCOR)
    t(160.5, 79, 'new\nθ*', ha='left', color=NCOR, size=FS)
    t(86, 2, 'Greedy and exchange: the "simple alternative"\nthat A1 proposes for its outer loop; the\n'
             'certificate: what neither source gives.', ha='left', va='bottom', color=MUTED, linespacing=1.25)
    cv.fig.savefig(os.path.join(out, 'fig_scheme.png'), dpi=300)
    plt.close(cv.fig)


def fig_bed(out, R, case):
    xy, kind, hub = case['xy'], case['kind'], case['hub']
    npz = int(np.sum(kind == 'piezo'))
    k = R['t36']['k']
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 92 * MM))
    x0, x1, y0, y1 = R['bed']['wellfield']
    for ax, rule in zip(axs, ('indep', 'nderhyrja')):
        S = set(R['t34'][str(k)][rule]['S'])
        ax.add_patch(Rectangle((0, 0), 1, 1, fc='#f7f9fb', ec=INK, lw=0.6))
        ax.add_patch(Rectangle((0, -0.06), 1, 0.06, fc='#cfe3f5', ec='none'))
        ax.text(0.5, -0.03, 'sea', ha='center', va='center', fontsize=FS, color=BLUE)
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc='#fff1e6', ec=ORANGE, lw=0.9, ls='--'))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, 'wellfield', ha='center', va='center', fontsize=FS, color=ORANGE)
        for h in range(4):
            ax.plot([0.5, 0.5], [0, 1], color='#d5dae0', lw=0.6, zorder=0)
            ax.plot([0, 1], [0.5, 0.5], color='#d5dae0', lw=0.6, zorder=0)
        for i in range(npz):
            on = i in S
            ax.plot(*xy[i], 'o', ms=5.2 if on else 3.2, mfc=SIGC if on else 'white', mec=SIGC, mew=0.8)
        for i in range(npz, len(xy)):
            on = i in S
            m = 'P' if kind[i] == 'baro' else 's'
            ax.plot(*xy[i], m, ms=7.5 if on else 5.5, mfc=REFC if on else 'white', mec=REFC, mew=1.0)
        nref = sum(1 for i in S if i >= npz)
        ev = R['t34'][str(k)][rule]
        ax.set_title(f"{NAME[rule]}\n{k} sensors, {nref} reference channels\nworst case {ev['worst']:.2f} nats",
                     fontsize=FS, loc='left')
        ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.08, 1.02); ax.set_aspect('equal'); ax.axis('off')
    handles = [Line2D([], [], marker='o', ls='', mfc=SIGC, mec=SIGC, label='piezometer, selected'),
               Line2D([], [], marker='o', ls='', mfc='white', mec=SIGC, label='piezometer, candidate'),
               Line2D([], [], marker='P', ls='', mfc=REFC, mec=REFC, ms=7, label='barometer'),
               Line2D([], [], marker='s', ls='', mfc=REFC, mec=REFC, ms=6, label='hub reference channel')]
    fig.legend(handles=handles, loc='lower center', ncol=4, fontsize=FS, frameon=False, columnspacing=1.0,
               handletextpad=0.3)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.82, bottom=0.10, wspace=0.05)
    fig.savefig(os.path.join(out, 'fig_bed.png'), dpi=300)
    plt.close(fig)


def fig_t33(out, R):
    cur = R['t33']['curve']
    n = [c['n'] for c in cur]
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 96 * MM))
    ax = axs[0]
    ax.plot(n, [c['baro'] for c in cur], '-o', ms=3, color=REFC, label='barometer, exact')
    ax.plot(n, [c['hub'] for c in cur], '-s', ms=3, color=VIOLET, label='one hub channel, exact')
    ax.plot(n, [c['naive'] for c in cur], '--', color='#b58a3c', label='barometer, naive weighting')
    ax.plot(n, [c['indep'] for c in cur], ':', color='#8a9099', lw=1.6, label='barometer, independent noise')
    ax.set_xlabel('piezometers already selected', fontsize=FS)
    ax.set_ylabel('information added (nats)', fontsize=FS)
    ax.set_title('(a) value of a reference channel (Prop. N1)', fontsize=FS, loc='left')
    ax.legend(fontsize=FS - 0.6, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.24), ncol=1)
    style(ax)
    ax = axs[1]
    ks = sorted(int(k) for k in R['t34'])
    for rule in ('indep', 'nominal_norefs', 'nderhyrja'):
        ax.plot(ks, [R['t34'][str(k)][rule]['nominal'] for k in ks], '-' + MARK[rule], ms=4, color=COL[rule],
                label=NAME[rule])
    ax.plot(ks, [R['t34'][str(k)]['nderhyrja']['ceiling'] for k in ks], '--', color=INK, lw=0.9,
            label='correction ceiling of its piezometers')
    ax.set_xlabel('sensors k (piezometers + references)', fontsize=FS)
    ax.set_ylabel('information at nominal θ (nats)', fontsize=FS)
    ax.set_title('(b) designs against the ceiling (Prop. N2)', fontsize=FS, loc='left')
    ax.legend(fontsize=FS - 0.6, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.24), ncol=1)
    style(ax)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.40, wspace=0.30)
    fig.savefig(os.path.join(out, 'fig_t33.png'), dpi=300)
    plt.close(fig)


def fig_t34(out, R):
    ks = sorted(int(k) for k in R['t34'])
    fig, axs = plt.subplots(1, 2, figsize=(170 * MM, 100 * MM), gridspec_kw=dict(width_ratios=[1.45, 1]))
    ax = axs[0]
    for rule in RULES:
        ax.plot(ks, [R['t34'][str(k)][rule]['worst'] for k in ks], '-' + MARK[rule], ms=5 if rule == 'nderhyrja' else 3.5,
                color=COL[rule], label=NAME[rule], lw=1.4 if rule == 'nderhyrja' else 1.0)
    ax.plot(ks, [R['t35'][str(k)]['ub_plain'] for k in ks], ':', color=MUTED, lw=1.0, label='bound: relaxation alone')
    ax.plot(ks, [R['t35'][str(k)]['ub_ceiling'] for k in ks], '-.', color=MUTED, lw=1.0, label='bound: + ceiling')
    ax.plot(ks, [R['t35'][str(k)]['ub'] for k in ks], '--', color=INK, lw=1.2, label='certified bound Ū (all layers)')
    ax.set_xlabel('sensors k', fontsize=FS)
    ax.set_ylabel('worst-case information (nats)', fontsize=FS)
    ax.set_title('(a) worst plausible interference (T34) and Ū (T35)', fontsize=FS, loc='left')
    h_, l_ = ax.get_legend_handles_labels()
    style(ax)
    ax = axs[1]
    sm = R['t35_small']
    x = np.arange(len(sm))
    ax.bar(x - 0.27, [s['greedy_exchange'] for s in sm], 0.27, color=ORANGE, label='greedy + exchange')
    ax.bar(x, [s['exhaustive'] for s in sm], 0.27, color='#5fc79f', label='exhaustive optimum')
    ax.bar(x + 0.27, [s['ub'] for s in sm], 0.27, color='#c9ced6', label='certificate Ū')
    ax.set_xticks(x); ax.set_xticklabels([f"k={s['k']}" for s in sm], fontsize=FS)
    ax.set_ylabel('robust information (nats)', fontsize=FS)
    ax.set_title(f"(b) {sm[0]['n']} candidates, all subsets", fontsize=FS, loc='left')
    ax.set_ylim(0, 3.9)
    ax.legend(fontsize=FS - 0.6, frameon=False, loc='upper left')
    style(ax)
    fig.legend(h_, l_, loc='lower center', ncol=3, fontsize=FS - 0.6, frameon=False, columnspacing=1.0)
    fig.tight_layout(w_pad=1.2, rect=(0, 0.17, 1, 1))
    fig.savefig(os.path.join(out, 'fig_t34.png'), dpi=300)
    plt.close(fig)


def fig_t36(out, R):
    T = R['t36']
    designs = ['indep', 'nominal_norefs', 'nderhyrja']
    models = [('ignore', 'interference ignored', '#c9ced6'), ('nominal', 'corrected, nominal model', '#7aa7d8'),
              ('robust', 'corrected, robust model', ORANGE)]
    TICKS = ['interference\nignored', 'exact, no\nreferences', 'NDERHYRJA-\nGO']
    fig = plt.figure(figsize=(170 * MM, 126 * MM))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.05], hspace=0.78, wspace=0.28)
    ax = fig.add_subplot(gs[0, 0])
    x = np.arange(len(designs))
    for j, (m, lab, c) in enumerate(models):
        ax.bar(x + (j - 1) * 0.26, [100 * T[d][m]['coverage'] for d in designs], 0.26, color=c, label=lab)
    ax.axhline(90, color=INK, lw=0.9, ls='--')
    ax.set_xticks(x); ax.set_xticklabels(TICKS, fontsize=FS)
    ax.set_ylabel('coverage of 90% intervals (%)', fontsize=FS)
    ax.set_ylim(40, 100)
    ax.set_title('(a) wellfield forecast: calibration', fontsize=FS, loc='left')
    hh, ll = ax.get_legend_handles_labels()
    style(ax)
    ax = fig.add_subplot(gs[0, 1])
    for j, (m, lab, c) in enumerate(models):
        ax.bar(x + (j - 1) * 0.26, [T[d][m]['rmse_q'] for d in designs], 0.26, color=c)
    ax.set_xticks(x); ax.set_xticklabels(TICKS, fontsize=FS)
    ax.set_ylabel('RMSE of the forecast (m)', fontsize=FS)
    ax.set_title(f"(b) forecast error (prior sd {T['sd_q_prior']:.2f} m)", fontsize=FS, loc='left')
    style(ax)
    ax = fig.add_subplot(gs[1, :])
    s = R['series']
    tt = np.arange(len(s['raw']))
    ax.plot(tt, 100 * np.array(s['raw']), color='#8a9099', lw=0.9, label='raw reading')
    ax.plot(tt, 100 * np.array(s['corrected']), color=ORANGE, lw=1.2, label='corrected (reference channels)')
    ax.plot(tt, 100 * np.array(s['true']), color=INK, lw=1.0, ls='--', label='true head anomaly')
    ax.set_xlabel('day', fontsize=FS)
    ax.set_ylabel('head anomaly (cm)', fontsize=FS)
    rr = np.sqrt(np.mean((np.array(s['raw']) - np.array(s['true'])) ** 2)) * 100
    rc = np.sqrt(np.mean((np.array(s['corrected']) - np.array(s['true'])) ** 2)) * 100
    ax.set_title(f"(c) one season at piezometer {s['sensor']}: error {rr:.1f} cm raw, {rc:.1f} cm corrected",
                 fontsize=FS, loc='left')
    ax.set_ylim(min(-18, 100 * min(s['raw']) - 2), 32)
    ax.legend(fontsize=FS - 0.6, frameon=False, ncol=3, loc='upper left')
    style(ax)
    fig.legend(hh, ll, loc='center', bbox_to_anchor=(0.53, 0.50), ncol=3, fontsize=FS - 0.6, frameon=False)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.95, bottom=0.095)
    fig.savefig(os.path.join(out, 'fig_t36.png'), dpi=300)
    plt.close(fig)


def main(out):
    os.makedirs(out, exist_ok=True)
    R, case = load()
    fig_scheme(out)
    fig_bed(out, R, case)
    fig_t33(out, R)
    fig_t34(out, R)
    fig_t36(out, R)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, 'figs'))
