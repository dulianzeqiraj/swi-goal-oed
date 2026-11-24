"""Figures of the FSHEHTA-GO review (English labels; every text at least 8.6 pt at the printed size, 17 cm wide).
usage: python fshehta_figs.py OUT_DIR

fig_dag      our analogue of Figure 1 of the Time Series Deconfounder: who confounds the effect of pumping on salinity
fig_arch     our analogue of Figure 2: the history factor model and the physics branch, the check and the outcome model
fig_case     one simulated case: the hidden dryness, the history substitute and the reading from the heads
fig_d1       T29: bias of the summed well effects against the number of wells (Proposition D1)
fig_checks   T30-T32: a single-cause confounder, wrong physics (Proposition D4), the two checks
fig_map      the twenty papers of this review against the steps and the unknowns they inform
Numbers come from res/fshehta.json and res/fshehta_case.npz."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

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
INST = dict(Oxford=BLUE, Caltech=ORANGE, Harvard=AQUA, MIT=VIOLET)
HID = '#6250d6'          # hidden causes
TRT = BLUE               # treatments (pumping)
OUT = ORANGE             # outcome (salinity)
OBS = '#5b6672'          # observed covariates
PHY = AQUA               # physics branch
SGL = '#c4563a'          # single-cause hidden confounder
NAME = dict(naive='no adjustment', tsd='TSD substitute (learned)', tsd_ideal='best history substitute',
            phys='physics substitute', phys_prof='physics, kernel profiled', oracle='true recharge')


def load():
    with open(os.path.join(RES, 'fshehta.json')) as fh:
        return json.load(fh)


# ----------------------------------------------------------------------------------------------- our Figure 1
def node(cv, x, y, w, h, label, kind, sub=None):
    st = dict(hid=('#efecfb', HID, '--'), trt=('#e3eefb', TRT, '-'), out=('#fde9df', OUT, '-'),
              obs=('#eef0f2', OBS, '-'), med=('#f4f1fb', HID, '--'), phy=('#e2f5ee', PHY, '-'),
              non=('white', REF, ':'))[kind]
    cv.box(x - w / 2, y - h / 2, w, h, st[0], st[1], lw=1.0, r=1.8, ls=st[2])
    if sub:
        cv.text(x, y + 1.6, label, color=INK)
        cv.text(x, y - 1.9, sub, color=MUTED)
    else:
        cv.text(x, y, label, color=INK)


def fig_dag(out):
    cv = Canvas(170, 120)
    t = cv.text

    def arr(x0, y0, x1, y1, c, lw=1.0, ls='-', rad=0.0):
        cv.ax.annotate('', xy=(x1, y1), xytext=(x0, y0), zorder=25,
                       arrowprops=dict(arrowstyle='-|>', color=c, lw=lw, ls=ls, shrinkA=0, shrinkB=0,
                                       connectionstyle=f'arc3,rad={rad}', mutation_scale=8))
    # ---- (a) the Time Series Deconfounder, after its Figure 1(b)
    t(2, 115, '(a) Time Series Deconfounder', ha='left', size=9.4, weight='bold')
    node(cv, 14, 103, 22, 8, r'history $\bar H_{t-1}$', 'obs')
    node(cv, 45, 103, 26, 8, r'substitute $Z_t$', 'hid')
    node(cv, 14, 86, 23, 8, r'covariates $X_t$', 'obs')
    for x, lab in ((35, r'$A_{t1}$'), (48, r'$A_{t2}$'), (64, r'$A_{tk}$')):
        node(cv, x, 86, 11, 8, lab, 'trt')
        arr(45 + (x - 45) * 0.3, 99, x, 90, HID)
        arr(x, 82, 46 + (x - 46) * 0.3, 64, TRT, lw=1.3)
    t(56, 86, '…', color=MUTED)
    arr(25.5, 86, 29.5, 86, OBS)
    node(cv, 46, 60, 22, 8, r'$Y(\bar a_{\geq t})$', 'out')
    node(cv, 15, 68, 12, 8, r'$V_t$', 'hid')
    node(cv, 73, 70, 9, 8, r'$L_t$', 'hid')
    arr(19, 72, 33, 82, HID)                                # V -> A_1
    arr(21, 72, 45, 82, HID)                                # V -> A_2
    arr(21, 66, 35, 61, HID)                                # V -> Y
    arr(71.5, 74, 67, 82, SGL, ls='--')                    # L -> A_k
    arr(68.5, 68, 57, 61.5, SGL, ls='--')                  # L -> Y
    arr(25, 103, 32, 103, INK)
    t(2, 50, 'Vₜ: multi-cause hidden confounder; the\nfactor model rules it out (d-separation).\n'
             'Lₜ: single-cause, not caught — excluded\nby Assumption 3.  Zₜ = g(H̄ₜ₋₁): from\n'
             'the past only.  Theorem 1: given\n(Z̄ₜ, X̄ₜ, Āₜ₋₁) the k treatments are\nsequentially ignorable.',
      ha='left', va='top', color=INK, linespacing=1.25)
    t(2, 4, 'Factor model Πⱼ p(aₜⱼ | zₜ, xₜ): a recurrent\nnetwork, checked with predictive p-values.',
      ha='left', va='bottom', color=MUTED, linespacing=1.25)
    cv.line([80, 80], [2, 118], c='#c9ced6', lw=0.6)
    # ---- (b) Fushe-Kuqe: pumping at k wells, salinity, hidden drought demand and local crop stress
    t(84, 115, '(b) Fushë-Kuqe: who confounds?', ha='left', size=9.4, weight='bold')
    node(cv, 104, 100, 38, 9, 'dryness Dₜ', 'hid', 'heat, irrigation demand')
    node(cv, 149, 100, 38, 9, 'crop stress Lₜ', 'hid', 'one farm, near well 1')
    for x, lab in ((92, r'$A_{t1}$'), (105, r'$A_{t2}$'), (123, r'$A_{tk}$')):
        node(cv, x, 78, 11, 8, lab, 'trt')
        arr(104 + (x - 104) * 0.3, 95.5, x, 82, HID)
        arr(x, 74, 110 + (x - 110) * 0.4, 56.5, TRT, lw=1.4)
    t(114, 78, '…', color=MUTED)
    node(cv, 153, 78, 30, 9, 'recharge Rₜ', 'med', 'regional + local')
    node(cv, 148, 58, 20, 8, 'rain fₜ', 'obs')
    node(cv, 110, 52, 38, 9, 'salinity Yₜ', 'out', 'chloride, salinized area')
    node(cv, 153, 34, 30, 9, 'heads Hₜ', 'phy', 'two loggers')
    node(cv, 106, 28, 26, 8, 'sea level', 'non')
    arr(120, 95.5, 141, 82.5, HID)                          # D -> R
    arr(136, 95.5, 95, 82, SGL, ls='--')                    # L -> A_1: the single cause
    arr(160, 95.5, 160, 82.5, SGL, ls='--')                 # L -> local recharge
    arr(148, 62, 148, 73.5, OBS)                            # rain -> recharge
    arr(140, 74, 127, 56.5, HID)                            # R -> Y
    arr(164, 73.5, 164, 38.5, PHY)                          # R -> heads
    arr(125, 74, 140, 38.5, PHY)                            # pumping -> heads (drawdown)
    arr(108, 32, 109, 47.5, REF, ls=':')                    # sea level -> Y only
    t(84, 1, 'Dₜ: multi-cause, confounds every well.\nLₜ: single-cause, breaks Assumption 3 at well 1.\n'
             'Sea level: a cause of Y only, not a confounder.\nBlue: the effect sought.  Green: what the heads see.',
          ha='left', va='bottom', color=MUTED, linespacing=1.25)
    cv.fig.savefig(os.path.join(out, 'fig_dag.png'), dpi=300)
    plt.close(cv.fig)


# ----------------------------------------------------------------------------------------------- our Figure 2
def fig_arch(out):
    cv = Canvas(170, 96)
    t = cv.text

    def blk(x, y, w, h, s, kind, sub=None):
        node(cv, x + w / 2, y + h / 2, w, h, s, kind, sub)

    def arr(x0, y0, x1, y1, c, lw=1.0, ls='-'):
        cv.ax.annotate('', xy=(x1, y1), xytext=(x0, y0), zorder=25, arrowprops=dict(
            arrowstyle='-|>', color=c, lw=lw, ls=ls, shrinkA=0, shrinkB=0, mutation_scale=8))
    t(2, 92, 'history branch (Time Series Deconfounder)', ha='left', size=9.4, weight='bold', color=HID)
    blk(2, 70, 34, 14, 'past pumping,', 'obs', 'rain, heads, chloride')
    blk(44, 70, 30, 14, 'recurrent', 'hid', 'factor model')
    blk(82, 70, 26, 14, r'substitute $\hat Z_t$', 'hid')
    blk(116, 70, 34, 14, 'p(aₜ | ẑₜ)', 'hid', 'predictive check')
    for x0, x1 in ((36, 44), (74, 82), (108, 116)):
        arr(x0, 77, x1, 77, HID)
    t(2, 57, 'physics branch (new)', ha='left', size=9.4, weight='bold', color=PHY)
    blk(2, 36, 34, 14, 'heads Hₜ at', 'phy', 'two loggers')
    blk(44, 36, 30, 14, 'add back the', 'phy', 'known drawdown')
    blk(82, 36, 26, 14, 'deconvolve kH', 'phy', 'τ profiled')
    blk(116, 36, 26, 14, r'reading $\hat R_t$', 'phy')
    for x0, x1 in ((36, 44), (74, 82), (108, 116)):
        arr(x0, 43, x1, 43, PHY)
    t(59, 32, 'g from a pumping test', color=MUTED)
    # the physics check, fed by both branches
    blk(150, 53, 18, 14, 'check', 'non', 'A ⊥ R̂ | Ẑ')
    cv.line([95, 95], [70, 60], c=HID, lw=1.0)
    arr(95, 60, 150, 60, HID)
    cv.line([142, 159], [43, 43], c=PHY, lw=1.0)
    arr(159, 43, 159, 53, PHY)
    # the outcome model and the decision
    blk(44, 4, 66, 16, 'outcome model', 'out', 'Yₜ on kS∗Aⱼ, kS∗f, kS∗R̂ (and Ẑ)')
    arr(124, 36, 100, 20, PHY)
    blk(118, 4, 50, 16, 'βⱼ and the policy effect', 'out', 'with the D4 error band')
    arr(110, 12, 118, 12, OUT)
    t(2, 12, 'a rejected check:\nẐ misses a confounder,\nor the physics is wrong', ha='left', color=MUTED,
      linespacing=1.25)
    cv.fig.savefig(os.path.join(out, 'fig_arch.png'), dpi=300)
    plt.close(cv.fig)


# ----------------------------------------------------------------------------------------------- results
def fig_case(out):
    z = np.load(os.path.join(RES, 'fshehta_case.npz'))
    D, zp, X, f = z['D'], z['zp'], z['X'], z['f']
    n = len(D)

    def proj(cols):
        M_ = np.column_stack([np.ones(n)] + cols)
        return M_ @ np.linalg.lstsq(M_, D, rcond=None)[0]
    dz = proj([zp]); dx = proj([X[:, 0], X[:, 1], f])
    r2z = 1 - np.var(D - dz) / np.var(D); r2x = 1 - np.var(D - dx) / np.var(D)
    fig = plt.figure(figsize=(170 * MM, 66 * MM))
    ax = fig.add_axes([0.075, 0.2, 0.9, 0.56])
    w = np.arange(n)
    s = slice(n - 104, n)
    ax.plot(w[s] - w[s][0], D[s], color=INK, lw=1.3, label='hidden dryness Dₜ')
    ax.plot(w[s] - w[s][0], dz[s], color=ORANGE, lw=1.2,
            label=f'read from past pumping (TSD), R² = {r2z:.2f}')
    ax.plot(w[s] - w[s][0], dx[s], color=AQUA, lw=1.2, ls='--',
            label=f'read from the heads and the rain, R² = {r2x:.2f}')
    ax.set_xlim(0, 103); ax.set_xlabel('week'); ax.set_ylabel('dryness (standard units)')
    ax.legend(loc='lower left', bbox_to_anchor=(0, 1.0), ncol=2, frameon=False, handlelength=1.6, columnspacing=1.2)
    GF.style(ax)
    fig.savefig(os.path.join(out, 'fig_case.png'), dpi=300)
    plt.close(fig)
    return dict(r2_tsd=float(r2z), r2_phys=float(r2x))


def fig_d1(out, E):
    ks = (2, 4, 8, 16, 32, 64)
    fig = plt.figure(figsize=(170 * MM, 74 * MM))
    for i, rho in enumerate((0.98, 0.9, 0.5)):
        ax = fig.add_axes([0.075 + i * 0.315, 0.17, 0.26, 0.6])
        R = [E['T29'][f'{rho}_{k}'] for k in ks]
        cf = [r['d1']['bound'] for r in R]
        ax.axhline(R[0]['naive_limit'], color=REF, lw=0.8, ls=':')
        ax.plot(ks, cf, color=VIOLET, lw=1.0, ls='--')
        for m, col, mk in (('naive', REF, 'o'), ('tsd', ORANGE, 's'), ('tsd_ideal', VIOLET, '^'), ('phys', AQUA, 'D')):
            y = [r[m]['bias_sum'] for r in R]
            e = [1.96 * r[m]['sd_sum'] / np.sqrt(E['nrep'] if k <= 16 else E['nrep'] // 2) for r, k in zip(R, ks)]
            ax.errorbar(ks, y, yerr=e, color=col, marker=mk, ms=4.2, lw=1.1, capsize=0, elinewidth=0.8)
        ax.set_xscale('log', base=2); ax.set_xticks(ks); ax.set_xticklabels([str(k) for k in ks])
        ax.set_ylim(-0.08, 0.72)
        ax.set_title(f'dryness memory ρ = {rho}')
        ax.set_xlabel('number of wells k')
        if i == 0:
            ax.set_ylabel('bias of Σⱼ βⱼ')
        else:
            ax.set_yticklabels([])
        GF.style(ax)
    h = [Line2D([], [], color=REF, marker='o', ms=4.2, lw=1.1), Line2D([], [], color=ORANGE, marker='s', ms=4.2, lw=1.1),
         Line2D([], [], color=VIOLET, marker='^', ms=4.2, lw=1.1), Line2D([], [], color=AQUA, marker='D', ms=4.2, lw=1.1),
         Line2D([], [], color=VIOLET, ls='--', lw=1.0), Line2D([], [], color=REF, ls=':', lw=0.8)]
    fig.legend(h, ['no adjustment', 'TSD, learned', 'best history substitute', 'physics substitute',
                   'D1 closed form', 'limit ρb/λ'], loc='upper left', bbox_to_anchor=(0.06, 0.995), ncol=3,
               frameon=False, handlelength=1.8, columnspacing=1.4)
    fig.savefig(os.path.join(out, 'fig_d1.png'), dpi=300)
    plt.close(fig)


def fig_checks(out, E):
    fig = plt.figure(figsize=(170 * MM, 118 * MM))
    # (a) single-cause confounder: bias of beta_1
    ax = fig.add_axes([0.085, 0.6, 0.38, 0.3])
    psis = ('0.0', '0.5', '1.0')
    ms = (('naive', REF), ('tsd', ORANGE), ('phys', AQUA), ('oracle', INK))
    wdt = 0.2
    for j, (m, col) in enumerate(ms):
        ax.bar(np.arange(3) + (j - 1.5) * wdt, [100 * E['T30'][p_][m]['rel_bias_b1'] for p_ in psis], wdt * 0.92,
               color=col, label=NAME[m] if m != 'tsd' else 'TSD substitute')
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_xticks(range(3)); ax.set_xticklabels([f'ψ = {p_}' for p_ in psis])
    ax.set_ylabel('bias of β₁ (%)'); ax.set_title('(a) crop stress at well 1 (single cause)')
    ax.legend(loc='upper right', ncol=2, frameon=False, handlelength=1.2, columnspacing=0.8)
    ax.set_ylim(-20, 310)
    GF.style(ax)
    # (b) wrong drawdown: D4
    ax = fig.add_axes([0.6, 0.6, 0.38, 0.3])
    gs = (-0.3, -0.15, 0.0, 0.15, 0.3)
    real = [E['T31'][f'g{g}']['phys']['bias_b1'] for g in gs]
    pred = [E['T31'][f'g{g}']['d4_pred_b1'] for g in gs]
    ax.plot([100 * g for g in gs], pred, color=VIOLET, lw=1.1, ls='--', label='Proposition D4')
    ax.plot([100 * g for g in gs], real, 'o', color=AQUA, ms=5, label='simulated')
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_xlabel('error of the drawdown coefficients (%)'); ax.set_ylabel('bias of β₁')
    ax.set_title('(b) wrong drawdown: linear bias')
    ax.legend(loc='upper left', frameon=False, handlelength=1.6)
    GF.style(ax)
    # (c) wrong head kernel: profiled vs fixed
    ax = fig.add_axes([0.085, 0.1, 0.38, 0.3])
    ts = ('0.6', '0.8', '1.25', '1.5')
    for j, (m, col) in enumerate((('phys', '#9fd8c2'), ('phys_prof', AQUA))):
        ax.bar(np.arange(4) + (j - 0.5) * 0.36, [100 * E['T31'][f't{x}'][m]['rel_bias_pol'] for x in ts], 0.33, color=col,
               label='kernel fixed at the wrong τ' if m == 'phys' else 'kernel profiled on the salinity fit')
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_xticks(range(4)); ax.set_xticklabels([f'τ × {x}' for x in ts])
    ax.set_ylabel('bias of the 20% cut (%)'); ax.set_title('(c) wrong head kernel')
    ax.set_ylim(-60, 34)
    ax.legend(loc='upper left', frameon=False, handlelength=1.2)
    GF.style(ax)
    # (d) the two checks
    ax = fig.add_axes([0.6, 0.1, 0.38, 0.3])
    sc = (('none', 'none'), ('multi_slow', 'multi,\nslow'), ('multi_fast', 'multi,\nfast'), ('single', 'single'),
          ('wrong_phys', 'wrong\nphysics'))
    rj = [100 * E['T32'][k]['reject'] for k, _ in sc]
    ax.bar(range(5), rj, 0.6, color=AQUA)
    for i, (k, _) in enumerate(sc):
        ax.text(i, rj[i] + 3, f"{rj[i]:.0f}%", ha='center', va='bottom', color=INK)
        ax.text(i, rj[i] + 15, f"p {E['T32'][k]['tsd_pval']:.2f}", ha='center', va='bottom', color=ORANGE)
    ax.set_xticks(range(5)); ax.set_xticklabels([s for _, s in sc])
    ax.set_ylim(0, 132); ax.set_yticks([0, 25, 50, 75, 100]); ax.set_ylabel('physics check rejects (%)')
    ax.set_title('(d) two checks; orange: TSD p')
    GF.style(ax)
    fig.savefig(os.path.join(out, 'fig_checks.png'), dpi=300)
    plt.close(fig)


def fig_map(out, cards):
    steps = [('substitute', 'substitute'), ('outcome', 'outcome model'), ('check', 'check'), ('physics', 'physics'),
             ('design', 'decide')]
    unk = [('inputs', 'inputs'), ('dispersion', 'dispersion'), ('bcs', 'boundaries')]
    n = len(cards)
    fig = plt.figure(figsize=(170 * MM, 150 * MM))
    left, bottom, top = 0.52, 0.07, 0.75
    ax = fig.add_axes([left, bottom, 0.975 - left, top - bottom])
    ncol = len(steps) + len(unk)
    ax.add_patch(Rectangle((len(steps) - 0.5, -0.5), len(unk), n, fc='#f4f1fb', ec='none', zorder=0))
    for i, cd in enumerate(cards):
        y = n - 1 - i
        col = INST[cd['inst']]
        if i % 5 == 0 and i:
            ax.axhline(y + 0.5, color='#c9ced6', lw=0.6)
        for j, (key, _) in enumerate(steps):
            if key in cd['steps']:
                ax.plot(j, y, 'o', color=col, ms=6.6, zorder=3)
            else:
                ax.plot(j, y, 'o', color='#e1e4e8', ms=2.4, zorder=2)
        for jj, (key, _) in enumerate(unk):
            j = len(steps) + jj
            lvl = cd['informs'].get(key, 0)
            if lvl == 2:
                ax.plot(j, y, 's', color=col, ms=6.2, zorder=3)
            elif lvl == 1:
                ax.plot(j, y, 's', color='white', mec=col, mew=1.3, ms=5.8, zorder=3)
            else:
                ax.plot(j, y, 's', color='#e1e4e8', ms=2.4, zorder=2)
        ax.text(-0.75, y, f"{cd['id']}  {cd['short']}", ha='right', va='center', color=INK, clip_on=False)
    ax.set_xlim(-0.6, ncol - 0.4); ax.set_ylim(-0.6, n - 0.4)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    for j, (_, lab) in enumerate(steps + unk):
        ax.text(j, n - 0.15, lab, ha='center', va='bottom', rotation=90, color=INK if j < len(steps) else '#4a3a8a',
                clip_on=False)
    ax.plot([-0.4, len(steps) - 0.6], [-1.0, -1.0], color=MUTED, lw=0.8, clip_on=False)
    ax.plot([len(steps) - 0.4, ncol - 0.6], [-1.0, -1.0], color='#4a3a8a', lw=0.8, clip_on=False)
    ax.text((len(steps) - 1) / 2, -1.25, 'step of the method', ha='center', va='top', color=MUTED, clip_on=False)
    ax.text(len(steps) + 1, -1.25, 'what it informs', ha='center', va='top', color='#4a3a8a', clip_on=False)
    x0 = 0.02
    for inst, col in INST.items():
        fig.text(x0, 0.975, '●', color=col, fontsize=FS + 1.5, va='center')
        fig.text(x0 + 0.022, 0.975, inst, color=INK, va='center')
        x0 += 0.12
    fig.text(0.02, 0.945, '■ direct lesson   □ indirect lesson   ● the step it serves', color=MUTED,
             va='center')
    fig.savefig(os.path.join(out, 'fig_map.png'), dpi=300)
    plt.close(fig)


def main(out, cards=None):
    os.makedirs(out, exist_ok=True)
    fig_dag(out)
    fig_arch(out)
    info = fig_case(out)
    if os.path.exists(os.path.join(RES, 'fshehta.json')):
        E = load()
        fig_d1(out, E)
        fig_checks(out, E)
    if cards is not None:
        fig_map(out, cards)
    return info


if __name__ == '__main__':
    print(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, 'figs')))
