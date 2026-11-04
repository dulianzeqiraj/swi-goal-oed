"""Text of the GARANCIA-GO review (English). blocks(E, R, RC) returns the block list; every number comes from res/
(gar_exp.json, gar_rcps.json, gar_rainc.json). Conventions: $inline math$, **bold**, *italic*, ==yellow placeholder==,
[text](url) hyperlink, [[key]] equation number, {{key}} figure or table number."""
import numpy as np

from cards_gar import CARDS, INST_ORDER

ANCHORS = [
    dict(key='A1', text='Angelopoulos, A. N., Bates, S., Fisch, A., Lei, L., & Schuster, T. (2024). Conformal risk '
                        'control. The Twelfth International Conference on Learning Representations (ICLR 2024). '
                        'arXiv:2208.02814 (PDF provided by the user).',
         url='https://arxiv.org/abs/2208.02814'),
    dict(key='A2', text='Tibshirani, R. (2023). Conformal prediction. Lecture notes, Advanced Topics in Statistical '
                        'Learning, Spring 2023, University of California, Berkeley (PDF provided by the user).',
         url='https://www.stat.berkeley.edu/~ryantibs/statlearn-s23/'),
]

# works linked in the synthesis; most were cards of earlier reviews of the series (see Section 3)
SYN = [
    dict(key='S1', text='Cleary, E., Garbuno-Inigo, A., Lan, S., Schneider, T., & Stuart, A. M. (2021). Calibrate, emulate, '
                        'sample. Journal of Computational Physics 424, 109716.', url='https://doi.org/10.1016/j.jcp.2020.109716'),
    dict(key='S2', text='Huang, D. Z., Schneider, T., & Stuart, A. M. (2022). Iterated Kalman methodology for inverse '
                        'problems. Journal of Computational Physics 463, 111262.', url='https://doi.org/10.1016/j.jcp.2022.111262'),
    dict(key='S3', text='Calvello, E., Reich, S., & Stuart, A. M. (2025). Ensemble Kalman methods: a mean-field '
                        'perspective. Acta Numerica 34, 123–291.', url='https://doi.org/10.1017/S0962492924000060'),
    dict(key='S4', text='Dunbar, O. R. A., Howland, M. F., Schneider, T., & Stuart, A. M. (2022). Ensemble-based '
                        'experimental design for targeting data acquisition to inform climate models. Journal of Advances '
                        'in Modeling Earth Systems 14(9), e2022MS002997.', url='https://doi.org/10.1029/2022MS002997'),
    dict(key='S5', text='Wu, J.-L., Levine, M. E., Schneider, T., & Stuart, A. M. (2024). Learning about structural errors '
                        'in models of complex dynamical systems. Journal of Computational Physics 513, 113157.',
         url='https://doi.org/10.1016/j.jcp.2024.113157'),
    dict(key='S6', text='Wen, G., Li, Z., Azizzadenesheli, K., Anandkumar, A., & Benson, S. M. (2022). U-FNO—An enhanced '
                        'Fourier neural operator-based deep-learning model for multiphase flow. Advances in Water '
                        'Resources 163, 104180.', url='https://doi.org/10.1016/j.advwatres.2022.104180'),
    dict(key='S7', text='Ramgraber, M., Baptista, R., McLaughlin, D., & Marzouk, Y. (2023). Ensemble transport smoothing. '
                        'Part I: unified framework. Journal of Computational Physics: X 17, 100134.',
         url='https://doi.org/10.1016/j.jcpx.2023.100134'),
    dict(key='S8', text='Spantini, A., Baptista, R., & Marzouk, Y. (2022). Coupling techniques for nonlinear ensemble '
                        'filtering. SIAM Review 64(4), 921–953.', url='https://doi.org/10.1137/20M1312204'),
    dict(key='S9', text='Zahm, O., Cui, T., Law, K., Spantini, A., & Marzouk, Y. (2022). Certified dimension reduction in '
                        'nonlinear Bayesian inverse problems. Mathematics of Computation 91(336), 1789–1835.',
         url='https://doi.org/10.1090/mcom/3737'),
    dict(key='S10', text='Huan, X., Jagalur, J., & Marzouk, Y. (2024). Optimal experimental design: formulations and '
                         'computations. Acta Numerica 33, 715–840.', url='https://doi.org/10.1017/S0962492924000023'),
    dict(key='S11', text='Angelopoulos, A. N., Bates, S., Fannjiang, C., Jordan, M. I., & Zrnic, T. (2023). '
                         'Prediction-powered inference. Science 382(6671), 669–674.', url='https://doi.org/10.1126/science.adi6000'),
    dict(key='S12', text='Angelopoulos, A. N., Candès, E., & Tibshirani, R. J. (2023). Conformal PID control for time '
                         'series prediction. Advances in Neural Information Processing Systems 36.',
         url='https://proceedings.neurips.cc/paper_files/paper/2023/hash/47f2fad8c1111d07f83c91be7870f8db-Abstract-Conference.html'),
    dict(key='S14', text='Fannjiang, C., Bates, S., Angelopoulos, A. N., Listgarten, J., & Jordan, M. I. (2022). Conformal '
                         'prediction under feedback covariate shift for biomolecular design. Proceedings of the National '
                         'Academy of Sciences 119(43), e2204569119.', url='https://doi.org/10.1073/pnas.2204569119'),
    dict(key='S15', text='Angelopoulos, A. N., Bates, S., Candès, E. J., Jordan, M. I., & Lei, L. (2025). Learn then test: '
                         'calibrating predictive algorithms to achieve risk control. Annals of Applied Statistics 19(2), '
                         '1641–1662.', url='https://doi.org/10.1214/24-AOAS1998'),
    dict(key='S16', text='Fong, E., & Holmes, C. (2021). Conformal Bayesian computation. Advances in Neural Information '
                         'Processing Systems 34.',
         url='https://proceedings.neurips.cc/paper/2021/hash/97785e0500ad16c18574c64189ccf4b4-Abstract.html'),
    dict(key='S17', text='Barber, R. F., Candès, E. J., Ramdas, A., & Tibshirani, R. J. (2023). Conformal prediction beyond '
                         'exchangeability. Annals of Statistics 51(2), 816–845.', url='https://doi.org/10.1214/23-AOS2276'),
    dict(key='S18', text='Chau, S. L., Bouabid, S., & Sejdinovic, D. (2021). Deconditional downscaling with Gaussian '
                         'processes. Advances in Neural Information Processing Systems 34.',
         url='https://arxiv.org/abs/2105.12909'),
    dict(key='S19', text='Angelopoulos, A. N., & Bates, S. (2023). Conformal prediction: a gentle introduction. Foundations '
                         'and Trends in Machine Learning 16(4), 494–591.', url='https://doi.org/10.1561/2200000101'),
    dict(key='S20', text='Yao, J., Mammadov, A., Berner, J., Kerrigan, G., Ye, J. C., Azizzadenesheli, K., & Anandkumar, A. '
                         '(2025). Guided diffusion sampling on function spaces with applications to PDEs. NeurIPS 2025; '
                         'arXiv:2505.17004.', url='https://arxiv.org/abs/2505.17004'),
    dict(key='S22', text='Chernozhukov, V., Wüthrich, K., & Zhu, Y. (2021). An exact and robust conformal inference '
                         'method for counterfactual and synthetic controls. Journal of the American Statistical '
                         'Association 116(536), 1849–1864.', url='https://doi.org/10.1080/01621459.2021.1920957'),
    dict(key='S23', text='Bates, S., Angelopoulos, A., Lei, L., Malik, J., & Jordan, M. I. (2021). Distribution-free, '
                         'risk-controlling prediction sets. Journal of the ACM 68(6), Article 43, 1–34.',
         url='https://doi.org/10.1145/3478535'),
    dict(key='S21', text='Krishnapriyan, A. S., Gholami, A., Zhe, S., Kirby, R. M., & Mahoney, M. W. (2021). Characterizing '
                         'possible failure modes in physics-informed neural networks. Advances in Neural Information '
                         'Processing Systems 34, 26548–26560.', url='https://neurips.cc/virtual/2021/poster/26497'),
]

OTHER = [
    dict(key='D1', text='Cenameri, S., & Beqiraj, A. (2016). Assessment of seawater intrusion in Fushë-Kuqe aquifer, '
                        'Albania. Bulletin of the Geological Society of Greece 50(2), 665–670.',
         url='https://doi.org/10.12681/bgsg.11772'),
    dict(key='D2', text='Strack, O. D. L. (1976). A single-potential solution for regional interface problems in coastal '
                        'aquifers. Water Resources Research 12(6), 1165–1174.', url='https://doi.org/10.1029/WR012i006p01165'),
    dict(key='D3', text='Internal documents of the project: RINDËRTIMI-GO, "Reconstructing all boundary conditions of a '
                        'coastal aquifer from rain and the Fushë-Kuqe data" (November 2026; test bed, ensemble smoother '
                        'with the exact solver); SHIU-GO (rain law, Erlang-2 vadose filter); the Fushë-Kuqe chloride study '
                        '(chloride_fk/: Strack areal model and the 20 000-draw calibration ensemble); the code of this '
                        'review in experiments/garancia_go/.', url=None),
]


def card_ref(c):
    lk = c['links'][0][1]
    return dict(key=c['id'], text=f"{c['authors']} ({c['year']}). {c['title']}. {c['venue']}.", url=lk)


def all_refs():
    syn = [dict(r, label=f'S{i}') for i, r in enumerate(SYN, start=1)]
    return ANCHORS + [card_ref(c) for c in CARDS] + syn + OTHER


def L(key, label=None):
    """inline link to a reference of the list."""
    for r in all_refs():
        if r['key'] == key:
            return f"[{label or key}]({r['url']})"
    raise KeyError(key)


# ------------------------------------------------------------------------------------------------------------ values
def values(E, R, RC):
    f2 = lambda x: f'{x:.2f}'
    f3 = lambda x: f'{x:.3f}'
    T1, T1A, HB, HA = E['T1'], E['T1A'], E['T1_halfwidth'], E['T1A_halfwidth']
    BF = ('eta', 'qL', 'r', 'h0')
    v = {}
    rng = lambda xs, f=f2: f'{f(min(xs))}–{f(max(xs))}'
    v['raw_out'] = rng([T1[k]['raw']['frac_out'] for k in BF])
    v['raw_k'] = f2(T1['kappa']['raw']['frac_out'])
    v['raw_wid'] = rng([T1[k]['raw']['width_vs_exact'] for k in BF])
    v['raw_wk'] = f2(T1['kappa']['raw']['width_vs_exact'])
    v['crc_all'] = rng([T1[k]['split']['crc_risk'] for k in BF + ('kappa',)], f3)
    v['sup_all'] = rng([T1[k]['split']['sup_cover'] for k in BF + ('kappa',)], f3)
    v['crc_w'] = rng([T1[k]['split']['crc_width'] for k in BF + ('kappa',)])
    v['sup_w'] = rng([T1[k]['split']['sup_width'] for k in BF])
    v['ex_sim_eta'] = f'{100 * T1["eta"]["exact"]["simultaneous"]:.0f}%'
    v['ex_sim_r'] = f'{100 * T1["r"]["exact"]["simultaneous"]:.0f}%'
    v['ex_out'] = rng([T1[k]['exact']['frac_out'] for k in BF + ('kappa',)], f3)
    v['A_raw'] = rng([T1A[k]['raw']['frac_out'] for k in BF + ('kappa',)])
    v['A_crc'] = rng([T1A[k]['split']['crc_risk'] for k in BF + ('kappa',)], f3)
    v['A_sup'] = rng([T1A[k]['split']['sup_cover'] for k in BF + ('kappa',)], f3)
    ratio = {k: HA[k]['crc'] / HB[k]['crc'] for k in BF + ('kappa',)}
    v['ratio'] = {k: f'{x:.1f}' for k, x in ratio.items()}
    v['hw'] = (HA, HB)
    T2 = E['T2']
    v['T2'] = T2
    T3 = E['T3']; v['T3'] = T3
    v['T4'] = E['T4']
    v['R'] = R; v['RC'] = RC
    return v


def fm(x, d=2):
    return f'{x:.{d}f}'


def pc(x):
    return f'{100 * x:.0f}%'


def span(xs, f=lambda x: f'{x:.2f}'):
    a, b = f(min(xs)), f(max(xs))
    return a if a == b else f'{a}–{b}'


# ------------------------------------------------------------------------------------------------------------ blocks
def blocks(E, R, RC):
    V = values(E, R, RC)
    T1, T1A, T2, T3, T4 = E['T1'], E['T1A'], V['T2'], V['T3'], V['T4']
    HA, HB = V['hw']
    rt = V['ratio']
    BF = ('eta', 'qL', 'r', 'h0')
    S4 = T4['subsets']
    mmyr = lambda x: x * 365.25e3
    B = []
    A = B.append
    A(('title', 'Inputs, dispersion and boundary conditions from rain alone'))
    A(('subtitle', 'Twenty papers from Oxford, Caltech, Berkeley and MIT (2020–2026), with links and what each one '
                   'teaches; a synthesis of how to solve the problem when the conditions are few; and GARANCIA-GO, '
                   'guaranteed bands calibrated on simulated aquifers'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation'))
    # ------------------------------------------------------------------------------------------- 1 outcome
    A(('h', '1. Outcome'))
    A(('bbox', [
        f'**Twenty papers, five per institution, 2020–2026, each with its links** (Section 3, Figure {{{{map}}}}). None '
        f'was a card in the earlier reviews of this series; the best-known works that were (calibrate–emulate–sample, '
        f'Kalman inversion, transport-map smoothers, prediction-powered inference and others) are linked in the '
        f'synthesis of Section 5. Every card says what the paper teaches for the input parameters, the dispersion '
        f'coefficient and the boundary conditions when only the rain is known, and ends with an innovation step.',
        '**Three facts decide the problem** (Section 5.1). Rain fixes when recharge arrives, not how much; every '
        'boundary needs its own witness; and dispersion has no witness in rain or heads at all (Proposition 6): only '
        'chloride data move it.',
        '**Innovation: GARANCIA-GO** (Section 4). Boundary conditions are never observed, so conformal prediction has '
        'nothing to calibrate on. GARANCIA-GO calibrates on aquifers simulated from the physical prior given the rain, '
        'with the same reconstructor that is used in the field. It gives finite-sample guarantees for the share of '
        'weeks a boundary function leaves its band and for the whole function, a field check by conformal p-value, a '
        'shift bound that does not grow with the number of simulations, and a version that holds with high '
        'probability for one calibration set.',
        f'**Test on 500 simulated aquifers (rain + 4 head loggers).** The raw ensemble left {V["raw_out"]} of the weeks '
        f'outside its nominal 90% band and missed $\\kappa$ in {V["raw_k"]} of the cases. Calibrated, the share of weeks '
        f'outside is {V["crc_all"]} (target ≤ 0.10) and the whole-function coverage {V["sup_all"]} (target ≥ 0.90), at '
        f'widths {V["crc_w"]} (pointwise) and {V["sup_w"]} (whole function) times the exact posterior. The guarantees '
        f'hold on average from $n = 20$ simulations; with the Hoeffding–Bentkus bound they hold for 93–100% of the '
        f'calibration sets.',
        f'**Rain only, or a wrong model.** With rain alone the guarantees still hold but the bands are wide: four '
        f'loggers make them {rt["eta"]} times narrower for the sea level, {rt["r"]}–{rt["qL"]} for inflow and recharge, '
        f'{rt["kappa"]} for $\\kappa$ and {rt["h0"]} for the initial head. Calibrating with the field\'s own rain keeps '
        f'the guarantee for that record (a dry and a wet year). A vadose delay 2.5 times longer in the field breaks '
        f'every guarantee (whole-function coverage of the recharge {fm(T3["delay"]["r"]["sup"])}) and raises the alarm '
        f'in {fm(T3["delay"]["alarm"])} of the cases; putting the delay in the prior restores coverage to '
        f'{fm(min(T3["delay_repaired"][k]["sup"] for k in BF))}–{fm(max(T3["delay_repaired"][k]["sup"] for k in BF))}.',
        f'**Fushë-Kuqe dispersion.** The littoral head alone leaves the transition-zone width at its prior '
        f'({S4["heads"]["w"][0]:.1f}–{S4["heads"]["w"][2]:.1f} m against {T4["w"]["prior"][0]:.1f}–'
        f'{T4["w"]["prior"][2]:.1f} m); the chloride facts move it to {S4["chloride"]["w"][0]:.0f}–'
        f'{S4["chloride"]["w"][2]:.0f} m; all facts give {S4["all"]["w"][0]:.1f}–{S4["all"]["w"][2]:.1f} m, and '
        f'{T4["w"]["real_conformal"][0]:.1f}–{T4["w"]["real_conformal"][2]:.1f} m after the conformal calibration of '
        f'the 90% interval.']))
    # ------------------------------------------------------------------------------------------- 2 problem, anchors
    A(('h', '2. The problem and the two anchors'))
    A(('h2', '2.1 What must be found, and what is known'))
    A(('p', 'A simulation of a coastal aquifer needs three groups of inputs that are rarely measured:'))
    A(('b', '**input parameters**: the transmissivity $T$ (or the conductivity $K$), the recharge coefficient $\\kappa$ '
            'and the delay $\\tau$ of the unsaturated zone;'))
    A(('b', '**the dispersion coefficient** of the salt-transport equation, through the dispersivities $\\alpha_L$ and '
            '$\\alpha_T$ and their field signature, the width $w$ of the transition zone;'))
    A(('b', '**boundary and initial conditions**: the sea level $\\eta(t)$, the inflow $q_L(t)$ through the inland '
            'boundary, the recharge $r(t)$ and the initial head $h_0(x)$.'))
    A(('p', 'The one time series that is always there is the rain $P(t)$ (a station, E-OBS or ERA5-Land), with a few '
            'heads and, at Fushë-Kuqe, a handful of chloride facts. The test bed of the RINDËRTIMI-GO note is the flow '
            'problem [[flow]] on a 5 km section (32 cells, 64 weekly steps), driven by the recharge law [[rech]]:'))
    A(('eq', 'flow', ['S\\,\\frac{\\partial h}{\\partial t}=T\\,\\frac{\\partial^{2}h}{\\partial x^{2}}+r(t)-Q\\,'
                      '\\delta(x-x_w),',
                      'h(0,t)=\\eta(t)\\text{ at the sea,  }T\\,\\frac{\\partial h}{\\partial x}(L,t)=q_L(t)\\text{ inland,  }h(x,0)=h_0(x)']))
    A(('eq', 'rech', 'r(t)=\\kappa\\,(k_\\tau * P)(t)+e(t)\\text{, with }k_\\tau(s)=\\frac{s}{\\tau^{2}}\\,e^{-s/\\tau}'))
    A(('p', 'Here $k_\\tau$ is the Erlang-2 kernel of two linear reservoirs in series ($\\tau$ = 14 d), $\\kappa$ is '
            'lognormal (median 0.35, log-sd 0.25), and $e$, $\\eta$, $q_L$ and $h_0$ are Gaussian random fields around '
            'random means; $T$ = 1500 m²/d, $S$ = 0.05 and the pumping $Q$ is known. Given the rain and $\\kappa$ every '
            'unknown is Gaussian and the heads are affine in them, so the exact posterior is a one-dimensional mixture '
            'over $\\kappa$: it is the reference against which every band below is scored. Salt enters through the '
            'advection–dispersion equation [[ade]], whose dispersion tensor holds the dispersion coefficient:'))
    A(('eq', 'ade', ['\\frac{\\partial(\\phi c)}{\\partial t}+\\nabla\\cdot(\\mathbf{q}\\,c)=\\nabla\\cdot(\\phi\\,'
                     '\\mathbf{D}\\,\\nabla c),',
                     '\\mathbf{D}=\\left(D_m+\\alpha_T|\\mathbf{v}|\\right)\\mathbf{I}+(\\alpha_L-\\alpha_T)\\,'
                     '\\frac{\\mathbf{v}\\mathbf{v}^{\\top}}{|\\mathbf{v}|}']))
    A(('p', f'At Fushë-Kuqe the calibrated areal model of the chloride study replaces [[ade]] by a sharp interface at '
            f'depth $\\zeta$ (Strack\'s single potential, {L("D2", "Strack 1976")}) with a dispersive transition zone of '
            f'width $w$:'))
    A(('eq', 'cz', 'c(z)=\\Phi\\left(\\frac{z-\\zeta}{w}\\right)\\text{,  }\\mathrm{Cl}=\\mathrm{Cl}_f+\\bar c\\,'
                    '(\\mathrm{Cl}_s-\\mathrm{Cl}_f)'))
    A(('p', f'so $w$ is the field footprint of the transverse dispersion and $\\bar c$ is $c$ averaged over a well screen. '
            f'The prior of $w$ is lognormal (median 20 m, log-sd 0.6), with the recharge $R$ and the conductivity scale '
            f'$\\eta_g$ among the other unknowns. The facts ({L("D1", "Cenameri & Beqiraj 2016")}) are the area whose '
            f'shallow chloride exceeds 250 mg/L (15% of the 349 km² polygon), the littoral head (about 3 m), the '
            f'seawater fraction of the mid-depth screens (4.7%) and chloride below 30 mg/L in the north-eastern '
            f'recharge band.'))
    A(('h2', '2.2 Anchor 1: split conformal prediction'))
    A(('p', f'For any score (large means a poor fit) and exchangeable scores $S_1,\\dots,S_{{n+1}}$, the empirical quantile '
            f'[[cp]] covers the next score ({L("A2", "Tibshirani 2023")}):'))
    A(('eq', 'cp', ['\\hat q=S_{(\\lceil(1-\\alpha)(n+1)\\rceil)},',
                    '1-\\alpha\\le\\mathbb{P}\\left(S_{n+1}\\le\\hat q\\right)\\le1-\\alpha+\\frac{1}{n+1}']))
    A(('p', 'The lower bound needs only exchangeability; the upper bound holds when the scores are almost surely '
            'distinct. Nothing is assumed about the model that produced the scores: a poor model gives wide bands, not '
            'a wrong coverage. If $n<(1-\\alpha)/\\alpha$ the quantile is infinite, so at $\\alpha$ = 0.10 at least nine '
            'calibration cases are needed.'))
    A(('h2', '2.3 Anchor 2: conformal risk control'))
    A(('p', f'Conformal risk control ({L("A1", "Angelopoulos, Bates, Fisch, Lei & Schuster, ICLR 2024")}) replaces the '
            f'indicator of non-coverage by any loss $L_i(\\lambda)$ that is non-increasing and right-continuous in '
            f'$\\lambda$, bounded by $B$, with $L_i(\\lambda_{{\\max}})\\le\\alpha$. With '
            f'$\\hat R_n(\\lambda)=\\frac{{1}}{{n}}\\sum_{{i\\le n}}L_i(\\lambda)$,'))
    A(('eq', 'crc', ['\\hat\\lambda=\\inf\\left\\{\\lambda:\\ \\frac{n}{n+1}\\hat R_n(\\lambda)+\\frac{B}{n+1}\\le\\alpha'
                     '\\right\\},',
                     '\\alpha-\\frac{2B}{n+1}\\le\\mathbb{E}\\left[L_{n+1}(\\hat\\lambda)\\right]\\le\\alpha']))
    A(('p', 'The upper bound is their Theorem 1 (exchangeable losses); the lower bound is their Theorem 2 (i.i.d. losses '
            'with no jump at a fixed $\\lambda$) and cannot be improved in general (their Proposition 1). For an '
            'arbitrary sequence $Z_1,\\dots,Z_{n+1}$ their Proposition 4 adds $B\\sum_{i=1}^{n}\\mathrm{TV}(Z_i,Z_{n+1})$ '
            'to the upper bound.'))
    A(('h2', '2.4 Why the anchors cannot be applied as they stand'))
    A(('p', 'Both anchors need calibration cases whose truth is known. For boundary conditions there are none: nobody '
            'measures the inflow through the inland boundary week by week, nor the recharge, nor the initial head '
            'field, and the dispersion width is measured at no well. Calibration pairs can only be simulated. '
            'GARANCIA-GO (Section 4) makes this precise: the guarantee becomes a guarantee under the physical prior '
            'given the rain; a field check says whether the field contradicts that prior, and a shift bound says what is '
            'lost if it does.'))
    # ------------------------------------------------------------------------------------------- 3 the papers
    A(('h', '3. The twenty papers'))
    A(('p', 'Five papers per institution, all published in 2020–2026 (Figure {{map}}). Three rules decided the '
            'selection: relevance to inferring inputs, dispersion and boundary conditions from rain and few data with '
            'calibrated uncertainty; a link to the institution at the time of publication; and no paper that was already '
            'a card in an earlier review of this series (those are linked in Section 5 instead). Each card gives the '
            'links, the evidence of affiliation, what the paper does, three lessons (input parameters, dispersion '
            'coefficient, boundary conditions from rain alone) and an innovation step for our problem.'))
    A(('p', '**Verification.** The hosts doi.org, arxiv.org, openreview.net and most publisher pages were blocked in this '
            'environment, so every landing page was reached through search results that quote it. No card could be '
            'checked against the full text, and all are marked partly verified; the evidence line of each card says what '
            'was seen.'))
    A(('img', 'map', 17.0))
    A(('cap', 'Figure {{map}}. The twenty papers against the step of the synthesis they serve (Section 5.2) and the '
              'unknown they inform. Colour gives the institution; a filled square is a direct lesson, an open square '
              'an indirect one.'))
    names = dict(Oxford='University of Oxford', Caltech='California Institute of Technology (with JPL)',
                 Berkeley='University of California, Berkeley (with Lawrence Berkeley National Laboratory)',
                 MIT='Massachusetts Institute of Technology')
    for j, inst in enumerate(INST_ORDER, start=1):
        A(('h2', f'3.{j} {names[inst]}'))
        for c in CARDS:
            if c['inst'] == inst:
                A(('card', c))
    # ------------------------------------------------------------------------------------------- 4 GARANCIA-GO
    A(('h', '4. Innovation: GARANCIA-GO, guaranteed bands for conditions that are never observed'))
    A(('img', 'scheme', 17.0))
    A(('cap', 'Figure {{scheme}}. GARANCIA-GO. The rain is the only series; the physical prior given the rain generates '
              'simulated aquifers whose truth is known; the same reconstructor is run on each of them and on the field; '
              'the scores of the simulated cases calibrate $\\hat\\lambda$ and $\\hat q$; the field check tests the prior '
              'before the bands are used. Dispersion is a separate branch, informed only by chloride. Thumbnails are '
              'real fields: rain and prior draws of the test bed, and one test case of T1 (inflow).'))
    A(('h2', '4.1 Set-up'))
    A(('p', 'Let the physical prior $\\mathcal{P}$ be the joint law of the rain $P$, the unknowns $u=(\\theta,g)$ (static '
            'inputs $\\theta$ such as $\\kappa$, $\\tau$ and $w$, and boundary functions $g$ on an index set '
            '$\\mathcal{T}$: 64 weeks, or 32 cells for $h_0$) and the data $y$ (head readings, chloride facts). A '
            'reconstructor $\\mathcal{R}$ maps $(P,y)$ to a centre $m(t)$ and a scale $s(t)>0$ for each target; here it '
            'is the ensemble smoother with the exact solver of RINDËRTIMI-GO (128 members), but any method can be used. '
            'Calibration cases $(P_i,u_i,y_i)$, $i=1,\\dots,n$, are independent draws from $\\mathcal{P}$, so their truth '
            '$g_i$ is known; the field is case $n+1$. With the standardised residuals '
            '$\\hat s_i(t)=(g_i(t)-m_i(t))/s_i(t)$ two scores are used:'))
    A(('eq', 'scores', ['L_i(\\lambda)=\\frac{1}{|\\mathcal{T}|}\\sum_{t\\in\\mathcal{T}}\\mathbf{1}\\left\\{|\\hat s_i(t)|'
                        '>\\lambda\\right\\},', 'S_i=\\max_{t\\in\\mathcal{T}}|\\hat s_i(t)|']))
    A(('p', '$L_i(\\lambda)$ is the share of weeks outside the band $m_i\\pm\\lambda s_i$; it is non-increasing and '
            'right-continuous in $\\lambda$, with $B=1$ and $L_i(\\infty)=0$. $S_i$ is the smallest multiple of $s_i$ '
            'that contains the whole function. Figure {{scheme}} shows the loop.'))
    A(('h2', '4.2 Guarantees'))
    A(('prop', 'Proposition 1 (whole-function band).',
            'If the calibration cases and the field case are independent draws from $\\mathcal{P}$ and $\\hat q$ is the '
            '$\\lceil(1-\\alpha)(n+1)\\rceil$-th smallest of $S_1,\\dots,S_n$, then '
            '$\\mathbb{P}\\{|g_{n+1}(t)-m_{n+1}(t)|\\le\\hat q\\,s_{n+1}(t)$ for every $t\\in\\mathcal{T}\\}\\ge1-\\alpha$, '
            'and this probability is at most $1-\\alpha+1/(n+1)$ when the $S_i$ are almost surely distinct.'))
    A(('proof', 'The reconstructor is the same map for every case, so $S_1,\\dots,S_{n+1}$ are i.i.d., hence '
                'exchangeable, and the event is $\\{S_{n+1}\\le\\hat q\\}$; apply [[cp]].'))
    A(('prop', 'Proposition 2 (share of weeks outside the band).',
            'Under the same conditions, with $\\hat\\lambda$ from [[crc]] with $B=1$ and $\\Lambda=[0,\\infty]$, '
            '$\\mathbb{E}[L_{n+1}(\\hat\\lambda)]\\le\\alpha$: on average over calibration sets and field cases, the band '
            '$m\\pm\\hat\\lambda s$ misses at most a fraction $\\alpha$ of the weeks. If the residuals have continuous '
            'distributions, $\\mathbb{E}[L_{n+1}(\\hat\\lambda)]\\ge\\alpha-2/(n+1)$.'))
    mx = max(T1[k]['max_score'] for k in T1)
    A(('proof', f'The losses [[scores]] satisfy the conditions of Theorem 1 of the CRC paper, with $L_i(\\infty)=0\\le'
                f'\\alpha$ (our code searches $\\lambda$ on a grid of step 0.01 up to 40, beyond every simulated score: '
                f'the largest in T1 is {mx:.1f}, for $\\kappa$). A continuous residual puts no jump at a fixed $\\lambda$, '
                f'which gives the lower bound by their Theorem 2.'))
    A(('prop', 'Proposition 3 (calibrated for the rain that fell).',
            'If every calibration case is simulated with the field\'s own rain record $P^{\\ast}$ (unknowns drawn from '
            '$\\mathcal{P}(\\cdot\\mid P^{\\ast})$, data from the observation model given $P^{\\ast}$) and the field '
            'unknowns are a draw from the same conditional law, Propositions 1 and 2 hold conditionally on $P^{\\ast}$.'))
    A(('proof', 'Given $P^{\\ast}$ the cases are i.i.d.; the arguments of Propositions 1 and 2 apply conditionally.'))
    A(('p', 'This is the form that answers "knowing only the rain": the band is calibrated for the rain that fell, not '
            'for an average rain. T1R checks it on a dry and a wet record.'))
    A(('prop', 'Remark 1 (Bonferroni against the sup-norm score).',
            f'A band built point by point with a Bonferroni correction, as in multi-horizon conformal forecasting (O4), '
            f'takes the $\\lceil(1-\\alpha/H)(n+1)\\rceil$-th smallest residual at each of $H$ points. It is finite only '
            f'if $n\\ge H/\\alpha-1$: {R["bonferroni_min_n"]["weeks"]} simulated aquifers for 64 weeks and '
            f'{R["bonferroni_min_n"]["cells"]} for 32 cells at $\\alpha$ = 0.10. The sup-norm score of Proposition 1 needs '
            f'$n\\ge(1-\\alpha)/\\alpha$ = 9 for any $H$ and is exact for any dependence between the points.'))
    A(('proof', 'For an integer $n$, $\\lceil x\\rceil\\le n$ if and only if $x\\le n$, and $(1-\\alpha/H)(n+1)\\le n$ '
                'is $n+1\\ge H/\\alpha$.'))
    A(('prop', 'Proposition 4 (when the field is not the prior).',
            'Let the calibration cases be independent draws from $\\mathcal{P}$ and the field case an independent draw '
            'from another law $\\mathcal{Q}$, and let $\\rho_{\\mathcal{P}}$, $\\rho_{\\mathcal{Q}}$ be the laws of the '
            'standardised residual vector $\\hat s=(\\hat s(t))_{t\\in\\mathcal{T}}$ of the field case under the two. Then'))
    A(('eq', 'shift', ['\\mathbb{E}\\left[L_{n+1}(\\hat\\lambda)\\right]\\le\\alpha+\\mathrm{TV}(\\rho_{\\mathcal{P}},'
                       '\\rho_{\\mathcal{Q}}),',
                       '\\mathbb{P}\\left(S_{n+1}\\le\\hat q\\right)\\ge1-\\alpha-\\mathrm{TV}(\\rho_{\\mathcal{P}},'
                       '\\rho_{\\mathcal{Q}})']))
    A(('proof', '$\\hat\\lambda$ and $\\hat q$ depend only on the calibration cases, which are independent of the field '
                'case. Given them, $L_{n+1}(\\hat\\lambda)$ and $\\mathbf{1}\\{S_{n+1}\\le\\hat q\\}$ are functions of '
                '$\\hat s$ with values in $[0,1]$, so their conditional expectations under $\\rho_{\\mathcal{Q}}$ and '
                '$\\rho_{\\mathcal{P}}$ differ by at most the TV distance; average over the calibration cases and apply '
                'Propositions 2 and 1 to the $\\mathcal{P}$ terms.'))
    A(('p', 'Two consequences. (i) Proposition 4 of the CRC paper, written for arbitrary sequences, gives '
            '$\\alpha+\\sum_{i\\le n}\\mathrm{TV}(Z_i,Z_{n+1})=\\alpha+n\\,\\mathrm{TV}(\\mathcal{P},\\mathcal{Q})$ here; '
            'with field and calibration cases independent, the penalty does not grow with $n$. (ii) What matters is '
            'not how far the field parameters are from the prior but how far the law of the standardised residuals '
            'moves: a reconstructor whose residuals are nearly pivotal keeps its guarantee under a parameter shift, '
            'while a structural error that it cannot follow moves the residual law far (T3).'))
    A(('prop', 'Proposition 5 (the field check).',
            'Let $C$ be a statistic of observable quantities only (here the mean standardised residual of the held-out '
            'head readings), $C_1,\\dots,C_n$ its values on the calibration cases and '
            '$p=(1+|\\{i:C_i\\ge C_{n+1}\\}|)/(n+1)$. If the field case is a draw from $\\mathcal{P}$, '
            '$\\mathbb{P}(p\\le\\alpha)\\le\\alpha$. If it is a draw from $\\mathcal{Q}$, the alarm rate satisfies'))
    A(('eq', 'alarm', '\\mathbb{P}_{\\mathcal{Q}}(p\\le\\alpha)-\\alpha\\le\\mathrm{TV}\\left(\\rho^{C}_{\\mathcal{P}},'
                      '\\rho^{C}_{\\mathcal{Q}}\\right)'))
    A(('p', 'so an alarm rate above $\\alpha$ is a lower bound on how far the field is from the prior, in the law of $C$.'))
    A(('proof', f'The first claim is the validity of conformal p-values under exchangeability '
                f'({L("B4", "Bates et al. 2023")}). For the second, given the calibration cases the alarm region '
                f'$A=\\{{c:p(c)\\le\\alpha\\}}$ is fixed and $\\mathcal{{Q}}(A)-\\mathcal{{P}}(A)\\le\\mathrm{{TV}}$; '
                f'average over the calibration cases and use $\\mathbb{{E}}[\\mathcal{{P}}(A)]\\le\\alpha$.'))
    A(('p', f'The converse fails. The TV distance that controls the guarantee in [[shift]] is that of the residuals of '
            f'unobserved functions, which the check cannot see, so the absence of an alarm proves nothing (T3, parameter '
            f'shift: alarm rate {fm(T3["parameters"]["alarm"])}, whole-function coverage down to '
            f'{fm(min(T3["parameters"][k]["sup"] for k in BF))}).'))
    A(('prop', 'Proposition 6 (dispersion is ancillary to rain and heads).',
            'Suppose the heads $y_h$ solve a flow problem whose coefficients do not involve the dispersion parameters '
            '$\\vartheta_D$ (the dispersivities, or $w$): constant density, or the sharp-interface model [[cz]], in which '
            'the head and the interface depend on $K$, $R$ and the geometry while $w$ enters only the chloride profile. If '
            'the prior factorises as $\\pi(\\vartheta_D)\\,\\pi(\\text{rest}\\mid P)$, then'))
    A(('eq', 'anc', 'p(\\vartheta_D\\mid P,y_h)=\\pi(\\vartheta_D)'))
    A(('p', 'for any rain record and any number of head readings: only data that depend on $\\vartheta_D$ (chloride or '
            'conductivity profiles, transition-zone widths, salinity series at wells) can inform it.'))
    A(('proof', 'The likelihood of $(P,y_h)$ does not depend on $\\vartheta_D$, so Bayes\' rule returns the prior.'))
    A(('p', f'Under variable density the heads depend on $\\vartheta_D$ only through the density coupling '
            f'$\\rho=\\rho_f(1+\\delta c)$, $\\delta$ = 0.025; the information is then bounded by the Fisher information '
            f'$J^{{\\top}}\\Sigma^{{-1}}J$ with $J=\\partial y_h/\\partial\\vartheta_D$, which is small away from the '
            f'interface. T4 checks [[anc]] on the Fushë-Kuqe facts: in the 20 000 prior draws the rank correlation between '
            f'$w$ and the littoral head is {T4["rank_corr"]["w"]["hlit"]:+.2f}, against '
            f'{T4["rank_corr"]["w"]["area"]:+.2f} with the salinised area and {T4["rank_corr"]["w"]["cl_ne"]:+.2f} with '
            f'the NE chloride.'))
    A(('prop', 'Remark 2 (a guarantee for the calibration set at hand).',
            f'Proposition 2 holds on average over calibration sets. For the one set at hand, choose $\\lambda$ by the '
            f'risk-controlling prediction sets of {L("S23", "Bates et al. (2021)")}: $\\hat\\lambda_{{\\delta}}$ is the '
            f'smallest $\\lambda$ whose Hoeffding–Bentkus p-value '
            f'$\\min\\{{e^{{-n\\,h_1(\\hat R_n\\wedge\\alpha,\\,\\alpha)}},\\ e\\,\\mathbb{{P}}(\\mathrm{{Bin}}(n,\\alpha)\\le'
            f'\\lceil n\\hat R_n\\rceil)\\}}$ is below $\\delta$, with '
            f'$h_1(a,b)=a\\log\\frac{{a}}{{b}}+(1-a)\\log\\frac{{1-a}}{{1-b}}$. Then the conditional risk given the '
            f'calibration set is at most $\\alpha$ with probability at least $1-\\delta$ (T5).'))
    A(('box', '**What is new.** (1) Conformal calibration of boundary and initial conditions that are never observed, '
              'on aquifers simulated from the physical prior given the rain, with the same reconstructor as in the field '
              '(Propositions 1–3). (2) A shift bound in terms of the law of the standardised residuals, with no factor '
              '$n$ (Proposition 4). (3) A field check whose alarm rate is a lower bound on the prior–field distance '
              '(Proposition 5). (4) Dispersion ancillarity, with its check on the Fushë-Kuqe facts (Proposition 6, T4). '
              '(5) The sample sizes that the few-conditions problem needs: 9 simulated aquifers for a finite '
              'whole-function band against 639 for Bonferroni over 64 weeks, about 20 for the mean guarantee, and the '
              'Hoeffding–Bentkus version for one calibration set.'))
    # ------------------------------------------------------------------------------------------- 4.3 tests
    A(('h2', '4.3 Tests'))
    A(('p', 'All tests are reproducible from experiments/garancia_go with fixed seeds (gar_exp.py, gar_rcps.py, '
            'gar_rainc.py):'))
    A(('b', '**T1**: 500 simulated aquifers of scenario B (rain + 4 loggers, each read with probability 0.25 per week, '
            'noise 2 cm; one reading in four held out for the field check), 1000 random splits into 200 calibration and '
            '300 test cases; **T1A**: the same with rain only; **T1R**: calibration with one shared rain record, a dry '
            'and a wet window (400 cases each).'))
    A(('b', '**T2**: calibration sets of $n$ = 10 to 200; **T5**: the high-probability version of Remark 2 for $n$ = 50, '
            '100 and 200, $\\delta$ = 0.10.'))
    A(('b', '**T3**: the field drawn from another law, a parameter shift (inflow mean +0.8 m²/d, $\\kappa\\times1.5$, '
            'sea-level mean +0.1 m) and a structural error (vadose delay 35 d against 14 d), 300 field cases each; then '
            'the delay put in the prior (log-sd 0.5).'))
    A(('b', '**T4**: the Fushë-Kuqe chloride ensemble (20 000 prior draws): simulation-based coverage of the '
            'importance-sampling intervals on 600 synthetic truths with the conformal correction, and the real facts '
            'taken in groups.'))
    # T1
    A(('p', f'**T1: the guarantee on simulated aquifers.** The exact posterior misses {V["ex_out"]} of the weeks, as it '
            f'should. The raw ensemble, read as mean ± 1.645 spread, misses {V["raw_out"]} because its spread is too small '
            f'({V["raw_wid"]} of the exact width), and misses $\\kappa$ in {V["raw_k"]} of the cases (spread '
            f'{V["raw_wk"]} of the exact). After calibration the share of weeks outside is {V["crc_all"]} for every '
            f'target, at {V["crc_w"]} times the exact width (Table {{{{t1tab}}}}). Pointwise 90% bands, even exact ones, '
            f'contain the whole function rarely (sea level {V["ex_sim_eta"]}, recharge {V["ex_sim_r"]}); the sup-norm '
            f'band contains it in 90% of the cases at {V["sup_w"]} times the exact pointwise width (Figure {{{{t1}}}}b). '
            f'Figure {{{{case}}}} shows one test case: the raw interval of $\\kappa$ misses the truth and the calibrated '
            f'one covers it.'))
    rows = []
    for k, lab in (('eta', 'sea level $\\eta$'), ('qL', 'inflow $q_L$'), ('r', 'recharge $r$'), ('h0', 'initial head $h_0$'),
                   ('kappa', 'coefficient $\\kappa$')):
        t = T1[k]; s = t['split']
        rows.append([lab, f"{t['exact']['frac_out']:.3f} / {t['exact']['simultaneous']:.2f}",
                     f"{t['raw']['frac_out']:.3f} / {t['raw']['simultaneous']:.2f} / {t['raw']['width_vs_exact']:.2f}",
                     f"{s['crc_risk']:.3f} ({s['crc_risk_p10']:.3f}–{s['crc_risk_p90']:.3f}) / {s['crc_width']:.2f}",
                     f"{s['sup_cover']:.3f} ({s['sup_cover_p10']:.3f}–{s['sup_cover_p90']:.3f}) / {s['sup_width']:.2f}",
                     f"{T1A[k]['split']['crc_risk']:.3f} / {T1A[k]['split']['sup_cover']:.3f}"])
    A(('cap', 'Table {{t1tab}}. T1 and T1A. Share of weeks outside the band / share of cases with the whole function '
              'inside, and width relative to the exact 90% band. CRC and sup-norm: mean over 1000 calibration sets of '
              '200 cases, with the 10th–90th percentile range. Targets: risk ≤ 0.10, coverage ≥ 0.90.'))
    A(('table', ['Target', 'Exact posterior', 'Raw ensemble', 'CRC: risk / width', 'Sup-norm: coverage / width',
                 'Rain only: CRC / sup'], rows, [2.2, 2.2, 3.0, 3.6, 3.6, 2.4], 9))
    A(('img', 'case', 17.0))
    A(('cap', 'Figure {{case}}. One test case of T1, the one with the median whole-function score for the recharge. '
              'Black: truth. Dotted grey: exact 90% band. Dashed orange: raw ensemble ± 1.645 spread. Blue: CRC band '
              '$m\\pm\\hat\\lambda s$. Aqua: sup-norm band $m\\pm\\hat q s$. Panel (e) shows the initial head minus the '
              'ensemble mean so that the bands are visible; panel (f) the intervals of $\\kappa$.'))
    A(('img', 't1', 17.0))
    A(('cap', 'Figure {{t1}}. (a) Share of weeks outside the band, (b) share of cases with the whole function inside, '
              'for the exact posterior, the raw ensemble and the calibrated bands (T1, rain + 4 loggers). (c) The '
              'guaranteed (CRC) half-width with rain only divided by that with the four loggers (T1A against T1).'))
    A(('p', f'**T1A: rain only.** With no head reading the reconstructor is the prior given the rain, which is already '
            f'calibrated (share outside {V["A_raw"]}). The calibrated bands keep the guarantees (CRC risk {V["A_crc"]}, '
            f'coverage {V["A_sup"]}) but are wide. Table {{{{hwtab}}}} gives the guaranteed half-widths in physical units: '
            f'four loggers narrow the CRC band {rt["eta"]} times for the sea level, {rt["r"]}–{rt["qL"]} for the recharge '
            f'and the inflow, {rt["kappa"]} for $\\kappa$ and {rt["h0"]} for the initial head (Figure {{{{t1}}}}c). The '
            f'sea level gains least: its weekly departures are correlated over only two weeks, each logger is read in one '
            f'week out of four, and the readings mix the sea level with the recharge and the inflow.'))
    rows = []
    for k, lab in (('eta', 'sea level $\\eta$'), ('qL', 'inflow $q_L$'), ('r', 'recharge $r$'), ('h0', 'initial head $h_0$'),
                   ('kappa', 'coefficient $\\kappa$')):
        u = HA[k]['units'].replace('m2/d', 'm²/d')
        rows.append([lab, u, f"{HA[k]['exact']:.3f} / {HA[k]['crc']:.3f} / {HA[k]['sup']:.3f}",
                     f"{HB[k]['exact']:.3f} / {HB[k]['crc']:.3f} / {HB[k]['sup']:.3f}", f"×{HA[k]['crc'] / HB[k]['crc']:.1f}"])
    A(('cap', 'Table {{hwtab}}. Mean 90% half-widths in physical units: exact posterior / CRC band / sup-norm band, with '
              'rain only (T1A) and with rain and four loggers (T1); last column, the ratio of the CRC half-widths.'))
    A(('table', ['Target', 'Units', 'Rain only', 'Rain + 4 loggers', 'Ratio'], rows, [3.3, 1.6, 4.6, 4.6, 1.6], 9.5))
    RCd = RC['records']
    A(('p', f'**T1R: calibrated for the rain that fell.** With every case sharing one rain record (Proposition 3), the '
            f'dry window ({RCd["dry"]["window_rain_mm"]:.0f} mm in 64 weeks; the median of 40 draws is '
            f'{RC["median_window_rain_mm"]:.0f} mm) gives CRC risk '
            f'{min(v["crc_risk"] for v in RCd["dry"]["targets"].values()):.3f}–'
            f'{max(v["crc_risk"] for v in RCd["dry"]["targets"].values()):.3f} and coverage '
            f'{min(v["sup_cover"] for v in RCd["dry"]["targets"].values()):.3f}–'
            f'{max(v["sup_cover"] for v in RCd["dry"]["targets"].values()):.3f}, and the wet window '
            f'({RCd["wet"]["window_rain_mm"]:.0f} mm) {min(v["crc_risk"] for v in RCd["wet"]["targets"].values()):.3f}–'
            f'{max(v["crc_risk"] for v in RCd["wet"]["targets"].values()):.3f} and '
            f'{min(v["sup_cover"] for v in RCd["wet"]["targets"].values()):.3f}–'
            f'{max(v["sup_cover"] for v in RCd["wet"]["targets"].values()):.3f}. The guaranteed half-width of $\\kappa$ is '
            f'{RCd["dry"]["targets"]["kappa"]["halfwidth_crc"]:.3f} in the dry window and '
            f'{RCd["wet"]["targets"]["kappa"]["halfwidth_crc"]:.3f} in the wet one: a wet year identifies the recharge '
            f'coefficient almost twice as well, because the recharge is larger against its error. The boundary functions '
            f'keep similar widths (recharge {RCd["dry"]["targets"]["r"]["halfwidth_crc"]:.3f} and '
            f'{RCd["wet"]["targets"]["r"]["halfwidth_crc"]:.3f} mm/d).'))
    # T2 + T5
    n10, n200 = T2['10'], T2['200']
    Rt = R['targets']
    okc = [Rt[k][n]['crc_ok'] for k in BF for n in ('50', '100', '200')]
    okr = [Rt[k][n]['rcps_ok'] for k in BF for n in ('50', '100', '200')]
    okck = [Rt['kappa'][n]['crc_ok'] for n in ('50', '100', '200')]
    okrk = [Rt['kappa'][n]['rcps_ok'] for n in ('50', '100', '200')]
    wr = [Rt[k][n]['rcps_width'] for k in BF for n in ('50', '100', '200')]
    wrk = [Rt['kappa'][n]['rcps_width'] for n in ('50', '100', '200')]
    A(('p', f'**T2 and T5: how many simulations.** The CRC band is conservative for small $n$ because of the '
            f'$B/(n+1)$ term (risk {n10["r"]["crc_risk"]:.3f}–{n10["qL"]["crc_risk"]:.3f} at $n$ = 10, i.e. bands wider '
            f'than needed) and reaches {n200["r"]["crc_risk"]:.3f} at $n$ = 200; the sup-norm coverage is 0.90–0.91 for '
            f'every $n\\ge10$, but its 10th percentile over calibration sets rises from {n10["qL"]["sup_cover_p10"]:.2f} '
            f'at $n$ = 10 to {n200["qL"]["sup_cover_p10"]:.2f}–{n200["r"]["sup_cover_p10"]:.2f} at $n$ = 200 (Figure '
            f'{{{{t2}}}}). For $\\kappa$, a 0/1 loss, CRC is split conformal: mean '
            f'{min(T2[n]["kappa"]["crc_risk"] for n in T2):.3f}–{max(T2[n]["kappa"]["crc_risk"] for n in T2):.3f} for '
            f'every $n$, with a 90th percentile of {n10["kappa"]["crc_risk_p90"]:.2f} at $n$ = 10. T5 makes this precise '
            f'for one calibration set: with plain CRC the realised risk stays below 10% in only '
            f'{span(okc, pc)} of the calibration sets for the boundary functions and {span(okck, pc)} for $\\kappa$; '
            f'the Hoeffding–Bentkus choice keeps it below 10% in {span(okr, pc)} and {span(okrk, pc)} of the sets, at '
            f'{span(wr)} and {span(wrk)} times the exact width (Table {{{{t5tab}}}}).'))
    A(('img', 't2', 17.0))
    A(('cap', 'Figure {{t2}}. (a) CRC risk and (b) sup-norm coverage against the number of simulated aquifers $n$ (mean '
              'and the 90th or 10th percentile over 1000 calibration sets). (c) Share of calibration sets whose realised '
              'risk is at most 0.10, for CRC and for RCPS with the Hoeffding–Bentkus bound (T5; the RCPS lines of $q_L$ '
              'and $r$ coincide at 1.00).'))
    rows = []
    for k, lab in (('eta', '$\\eta$'), ('qL', '$q_L$'), ('r', '$r$'), ('h0', '$h_0$'), ('kappa', '$\\kappa$')):
        cells = [lab]
        for n in ('50', '100', '200'):
            d = Rt[k][n]
            cells.append(f"{d['crc_ok']:.2f} / {d['rcps_ok']:.2f}")
        cells.append(' / '.join(f"{Rt[k][n]['crc_width']:.2f}" for n in ('50', '100', '200')))
        cells.append(' / '.join(f"{Rt[k][n]['rcps_width']:.2f}" for n in ('50', '100', '200')))
        rows.append(cells)
    A(('cap', 'Table {{t5tab}}. T5. Share of calibration sets with realised risk ≤ 0.10, CRC / RCPS ($\\delta$ = 0.10), '
              'for $n$ = 50, 100 and 200, and the band widths relative to the exact posterior for the three $n$.'))
    A(('table', ['Target', 'n = 50', 'n = 100', 'n = 200', 'CRC width', 'RCPS width'], rows,
       [1.8, 2.4, 2.4, 2.4, 3.8, 3.8], 9.5))
    # T3
    P_, D_, Rp = T3['parameters'], T3['delay'], T3['delay_repaired']
    A(('img', 't3', 17.0))
    A(('cap', 'Figure {{t3}}. T3. (a) Alarm rate of the field check (conformal p-value ≤ 0.10). (b) CRC risk and (c) '
              'sup-norm coverage in the field, with the bands calibrated under the prior: P under the prior (T1), S '
              'parameter shift, D delay error, R delay put in the prior and recalibrated.'))
    A(('p', f'**T3: when the field is not the prior.** Under the parameter shift the alarm rate is {P_["alarm"]:.2f} '
            f'({P_["alarm_null"]:.2f} under the prior), the CRC risk rises to {min(P_[k]["crc"] for k in BF):.3f}–'
            f'{max(P_[k]["crc"] for k in BF):.3f} and the whole-function coverage falls to '
            f'{min(P_[k]["sup"] for k in BF):.2f}–{max(P_[k]["sup"] for k in BF):.2f} ($\\kappa$: {P_["kappa"]["sup"]:.2f}): '
            f'moderate damage, partly visible to the check. Under the delay error the reconstructor filters the rain '
            f'with the wrong kernel, the residual law moves far, the alarm rate is {D_["alarm"]:.2f} and every guarantee '
            f'breaks (recharge: CRC risk {D_["r"]["crc"]:.2f}, coverage {D_["r"]["sup"]:.2f}; $\\kappa$: '
            f'{D_["kappa"]["crc"]:.2f} and {D_["kappa"]["sup"]:.2f}). Putting the delay in the prior of the reconstructor '
            f'and of the simulated aquifers (log-sd 0.5) brings the alarm rate back to {Rp["alarm"]:.2f} and the boundary '
            f'functions back to CRC {min(Rp[k]["crc"] for k in BF):.3f}–{max(Rp[k]["crc"] for k in BF):.3f} and coverage '
            f'{min(Rp[k]["sup"] for k in BF):.2f}–{max(Rp[k]["sup"] for k in BF):.2f}, with bands '
            f'{min(Rp[k]["width_ratio"] for k in BF):.2f}–{max(Rp[k]["width_ratio"] for k in BF):.2f} times as wide. '
            f'$\\kappa$ stays wrong (CRC {Rp["kappa"]["crc"]:.2f}, coverage {Rp["kappa"]["sup"]:.2f}, width '
            f'×{Rp["kappa"]["width_ratio"]:.2f}): with an uncertain delay the coefficient that multiplies a given filtered '
            f'rain is no longer the same quantity in every member, so the recharge function, not $\\kappa$, is the '
            f'quantity to report.'))
    # T4
    cov = {k: (T4[k]['cover_is'], T4[k]['cover_conformal'], T4[k]['q'], T4[k]['width_ratio']) for k in ('w', 'R', 'eta')}
    A(('p', f'**T4: Fushë-Kuqe, and which fact informs which unknown.** Over 300 synthetic truths the 90% '
            f'importance-sampling intervals cover {cov["w"][0]:.2f} ($w$), {cov["R"][0]:.2f} ($R$) and {cov["eta"][0]:.2f} '
            f'($\\eta_g$) of the cases (median effective sample size {T4["ess_median"]:.0f}); the conformal correction on '
            f'the log scale ($m\\pm\\hat q\\sigma$ with $\\hat q$ = {cov["w"][2]:.2f}, {cov["R"][2]:.2f}, '
            f'{cov["eta"][2]:.2f}) gives {cov["w"][1]:.2f}, {cov["R"][1]:.2f} and {cov["eta"][1]:.2f} at '
            f'{min(c[3] for c in cov.values()):.2f}–{max(c[3] for c in cov.values()):.2f} times the width. Taken one group '
            f'at a time (Figure {{{{t4}}}}, Table {{{{t4tab}}}}), the littoral head alone leaves $w$ at its prior, as '
            f'Proposition 6 says; the chloride facts move it to {S4["chloride"]["w"][0]:.1f}–{S4["chloride"]["w"][2]:.1f} '
            f'm; all facts give {S4["all"]["w"][0]:.1f}–{S4["all"]["w"][2]:.1f} m, {T4["w"]["real_conformal"][0]:.1f}–'
            f'{T4["w"]["real_conformal"][2]:.1f} m after the correction, with a central value of '
            f'{T4["w"]["real_conformal"][1]:.1f} m. The littoral head and the chloride facts pull the recharge in '
            f'opposite directions ({mmyr(S4["heads"]["R"][0]):.0f}–{mmyr(S4["heads"]["R"][2]):.0f} against '
            f'{mmyr(S4["chloride"]["R"][0]):.0f}–{mmyr(S4["chloride"]["R"][2]):.0f} mm/yr) and together give '
            f'{mmyr(S4["all"]["R"][0]):.0f}–{mmyr(S4["all"]["R"][2]):.0f} mm/yr; the conductivity scale is hardly informed '
            f'by any of them ({S4["all"]["eta"][0]:.2f}–{S4["all"]["eta"][2]:.2f} against a prior '
            f'{T4["eta"]["prior"][0]:.2f}–{T4["eta"]["prior"][2]:.2f}).'))
    rows = []
    for lab, key in (('prior', None), ('littoral head only', 'heads'), ('chloride facts only', 'chloride'),
                     ('all facts', 'all')):
        src = (lambda k: T4[k]['prior']) if key is None else (lambda k, key=key: S4[key][k])
        ess = '20 000' if key is None else f"{S4[key]['ess']:,.0f}".replace(',', ' ')
        rows.append([lab, ess, f"{src('w')[0]:.1f}–{src('w')[2]:.1f}",
                     f"{mmyr(src('R')[0]):.0f}–{mmyr(src('R')[2]):.0f}", f"{src('eta')[0]:.2f}–{src('eta')[2]:.2f}"])
    rows.append(['all facts, conformal', '', f"{T4['w']['real_conformal'][0]:.1f}–{T4['w']['real_conformal'][2]:.1f}",
                 f"{mmyr(T4['R']['real_conformal'][0]):.0f}–{mmyr(T4['R']['real_conformal'][2]):.0f}",
                 f"{T4['eta']['real_conformal'][0]:.2f}–{T4['eta']['real_conformal'][2]:.2f}"])
    rows.append(['simulated coverage, IS → conformal', '', f"{cov['w'][0]:.2f} → {cov['w'][1]:.2f}",
                 f"{cov['R'][0]:.2f} → {cov['R'][1]:.2f}", f"{cov['eta'][0]:.2f} → {cov['eta'][1]:.2f}"])
    A(('cap', 'Table {{t4tab}}. T4. 90% intervals at Fushë-Kuqe by group of facts (ESS: effective sample size of the '
              'importance weights), and the coverage of the intervals over 300 synthetic truths.'))
    A(('table', ['Facts used', 'ESS', 'Width w (m)', 'Recharge R (mm/yr)', 'K scale (–)'], rows, [5.2, 1.8, 3.0, 3.6, 2.6], 9.5))
    A(('img', 't4', 17.0))
    A(('cap', 'Figure {{t4}}. T4, Fushë-Kuqe. 90% intervals (dot: central value) of the transition-zone width $w$, the '
              'recharge $R$ and the conductivity scale $\\eta_g$ from the 20 000 prior draws weighted by the facts taken '
              'one group at a time, and the conformal 90% interval with all facts.'))
    # ------------------------------------------------------------------------------------------- 5 synthesis
    A(('h', '5. Synthesis: how to solve the problem when the conditions are few'))
    A(('p', 'This section puts the twenty papers, the earlier ones linked here and the GARANCIA-GO tests into one '
            'procedure. Card numbers (O1–M5) point to Section 3; every other link is to the work itself.'))
    A(('h2', '5.1 Three facts that decide the problem'))
    A(('b', f'**Rain fixes when recharge comes, not how much.** Through the vadose filter the rain gives the shape of '
            f'$r(t)$; its size is $\\kappa$, which the rain cannot tell. With rain only the guaranteed 90% half-width of '
            f'$\\kappa$ is {HA["kappa"]["crc"]:.2f} around a median of 0.35, and that of the recharge '
            f'{HA["r"]["crc"]:.2f} mm/d; four loggers cut them to {HB["kappa"]["crc"]:.3f} and {HB["r"]["crc"]:.2f} mm/d '
            f'(Table {{{{hwtab}}}}). A satellite-identified drainage fraction (M1) is the best prior for $\\kappa$ when '
            f'there are no heads.'))
    A(('b', f'**Every boundary needs a witness.** Heads inland witness the inflow ({HA["qL"]["crc"]:.2f} → '
            f'{HB["qL"]["crc"]:.2f} m²/d), any early reading witnesses the initial head ({HA["h0"]["crc"]:.1f} → '
            f'{HB["h0"]["crc"]:.2f} m), and heads witness the sea level only weakly ({HA["eta"]["crc"]:.2f} → '
            f'{HB["eta"]["crc"]:.2f} m). A tide gauge or satellite altimetry turns the sea level from an unknown into a '
            f'datum (C5).'))
    A(('b', f'**Dispersion has no witness in rain or heads.** Under constant density, or in the sharp-interface model of '
            f'Fushë-Kuqe, the heads do not depend on the dispersion parameters, so their posterior is their prior '
            f'whatever the number of heads (Proposition 6; T4: the littoral head alone gives '
            f'{S4["heads"]["w"][0]:.1f}–{S4["heads"]["w"][2]:.1f} m against a prior of {T4["w"]["prior"][0]:.1f}–'
            f'{T4["w"]["prior"][2]:.1f} m). Only chloride or conductivity data move it.'))
    A(('h2', '5.2 The procedure in eight steps'))
    A(('p', f'**Step 1. Write the physical prior from the rain.** The rain law and the vadose filter give the timing '
            f'(SHIU-GO); a lognormal $\\kappa$, or better a drainage fraction identified from satellite soil moisture '
            f'(M1); Gaussian fields for the sea level, the inflow and the initial head; the dispersion width from the '
            f'chloride study. If the rain comes from a coarse grid, downscale it with error bars '
            f'({L("S18", "Chau, Bouabid & Sejdinovic 2021")}). Put the physics in the mean and a Gaussian process on the '
            f'rest (O3), check the prior against drought–recovery scenarios (O5), and add the remote-sensing conditions '
            f'that exist (C5).'))
    A(('p', f'**Step 2. Keep the unknowns few.** A few numbers per boundary (mean, amplitude, $\\kappa$, $\\tau$) and '
            f'Gaussian departures; a certified reduction to the directions the data inform '
            f'({L("S9", "Zahm et al. 2022")}); an emulator when the simulator is slow (O1), or a neural-operator surrogate '
            f'for seawater intrusion (B1) built on U-FNO ({L("S6", "Wen et al. 2022")}). Physics-informed networks are a '
            f'poor choice for advection-dominated transport, where they are known to fail '
            f'({L("S21", "Krishnapriyan et al. 2021")}).'))
    A(('p', f'**Step 3. Invert with few runs and no derivatives.** Ensemble Kalman inversion and its unscented form '
            f'({L("S2", "Huang, Schneider & Stuart 2022")}; {L("S3", "Calvello, Reich & Stuart 2025")}), trained on '
            f'statistics (C3) with a ready toolbox (C4); calibrate–emulate–sample when runs are expensive '
            f'({L("S1", "Cleary et al. 2021")}); the ensemble smoother with the exact solver for the boundary functions '
            f'(RINDËRTIMI-GO); nonlinear transport-map smoothers when Gaussian updates fail '
            f'({L("S7", "Ramgraber et al. 2023")}; {L("S8", "Spantini, Baptista & Marzouk 2022")}); learned priors with '
            f'ensemble guidance (C2) or function-space diffusion ({L("S20", "Yao et al. 2025")}); amortised '
            f'likelihood-free inference on signatures of the series (O2).'))
    A(('p', f'**Step 4. Admit the structural error before it shows up.** The recharge closure error and the vadose delay '
            f'belong in the prior, and learned corrections belong inside the model component '
            f'({L("S5", "Wu, Levine, Schneider & Stuart 2024")}; C3). T3: a field delay 2.5 times the model\'s breaks every '
            f'guarantee (whole-function coverage of the recharge {D_["r"]["sup"]:.2f}), and putting $\\tau$ in the prior '
            f'restores it ({Rp["r"]["sup"]:.2f}).'))
    A(('p', f'**Step 5. Calibrate on simulated aquifers (GARANCIA-GO).** CRC for the share of weeks '
            f'({L("A1", "anchor A1")}), the sup-norm score for whole functions ({L("A2", "anchor A2")}), '
            f'Hoeffding–Bentkus for a guarantee per calibration set ({L("S23", "Bates et al. 2021")}), stability under the judgment calls (B2); the same calibration for maps (B3) and neural '
            f'operators (C1), joint regions (B5), full distributions (M3), multi-horizon forecasts (O4), and strength '
            f'borrowed from other aquifers (M2). With 64 weeks Bonferroni needs 639 simulations and the sup-norm score 9 '
            f'(Remark 1); the mean guarantee holds from about 20 (T2). A tutorial is '
            f'{L("S19", "Angelopoulos & Bates 2023")}.'))
    A(('p', f'**Step 6. Check the prior against the field.** The conformal p-value of held-out heads (B4), a permutation '
            f'test on the record itself ({L("S22", "Chernozhukov, Wüthrich & Zhu 2021")}), held-out readings placed like '
            f'the decision (M5), and an online threshold that keeps recalibrating with the real readings (M4). An alarm rate above '
            f'$\\alpha$ is a lower bound on how far the field is from the prior (Proposition 5); the absence of an alarm '
            f'is not a proof.'))
    A(('p', f'**Step 7. If the check fires, widen and recalibrate.** Add the suspect law to the prior (T3); before the '
            f'repair the damage is bounded by the TV distance of the residual laws (Proposition 4). For several risks at '
            f'once use Learn-then-Test ({L("S15", "Angelopoulos et al. 2025")}); for posterior samples, conformal '
            f'Bayesian computation ({L("S16", "Fong & Holmes 2021")}); for weighted or drifting calibration sets, '
            f'conformal prediction beyond exchangeability ({L("S17", "Barber et al. 2023")}).'))
    A(('p', f'**Step 8. Choose the next measurement, then operate.** Rank candidate data by the guaranteed width they '
            f'remove (T1A against T1: four loggers are worth a factor {rt["eta"]}–{rt["h0"]}); ensemble experimental '
            f'design ({L("S4", "Dunbar et al. 2022")}) and its theory ({L("S10", "Huan, Jagalur & Marzouk 2024")}); when '
            f'the model chooses where to measure, keep conformal validity under the feedback shift '
            f'({L("S14", "Fannjiang et al. 2022")}); in operation, online conformal control '
            f'({L("S12", "Angelopoulos, Candès & Tibshirani 2023")}; M4); and '
            f'combine the few real measurements with many model predictions ({L("S11", "Angelopoulos et al. 2023")}).'))
    A(('h2', '5.3 Dispersion with few conditions'))
    A(('b', '**What informs it**: depth profiles of electrical conductivity or chloride across the transition zone (two or '
            'three boreholes are worth more than any number of heads), depth-specific screens such as the mid-depth '
            'seawater fraction of 4.7% at Fushë-Kuqe, salinity time series at pumping wells (the shape of a breakthrough, '
            'O2), and airborne electromagnetics (C5).'))
    A(('b', '**What does not**: rain, heads, inflow, sea level (Proposition 6). Under variable density the heads carry '
            'information only through the density coupling, which is weak away from the interface.'))
    A(('b', f'**What can be guaranteed**: the width of the transition zone, not the dispersivity at a point. At '
            f'Fushë-Kuqe, {T4["w"]["real_conformal"][0]:.1f}–{T4["w"]["real_conformal"][2]:.1f} m (90%, calibrated). A '
            f'dispersivity follows from $w$ only through a model of the mixing zone, whose error must be simulated as '
            f'well.'))
    A(('b', '**How to use it**: give the simulated aquifers of GARANCIA-GO the calibrated interval of $w$ as prior, so that '
            'the guaranteed chloride bands carry the dispersion uncertainty.'))
    A(('h2', '5.4 Boundary conditions and inputs with few conditions'))
    A(('p', 'Table {{laddertab}} gives, for each unknown, its witness and the guaranteed half-width with the data at hand.'))
    rows = [['sea level $\\eta(t)$', 'tide gauge, altimetry (C5); heads near the coast',
             f"{HA['eta']['crc']:.2f} m", f"{HB['eta']['crc']:.2f} m"],
            ['inland inflow $q_L(t)$', 'a logger near the inland edge', f"{HA['qL']['crc']:.2f} m²/d",
             f"{HB['qL']['crc']:.2f} m²/d"],
            ['recharge $r(t)$', 'rain for the timing, heads for the size; satellite drainage (M1)',
             f"{HA['r']['crc']:.2f} mm/d", f"{HB['r']['crc']:.2f} mm/d"],
            ['initial head $h_0(x)$', 'any early reading; spin-up from the mean forcing', f"{HA['h0']['crc']:.1f} m",
             f"{HB['h0']['crc']:.2f} m"],
            ['recharge coefficient $\\kappa$', 'heads (a wet year identifies it about twice as well, T1R)',
             f"{HA['kappa']['crc']:.2f}", f"{HB['kappa']['crc']:.3f}"],
            ['transition-zone width $w$', 'chloride facts and profiles only (Proposition 6)',
             f"{T4['w']['prior'][0]:.0f}–{T4['w']['prior'][2]:.0f} m (prior)",
             f"heads: no change; chloride: {T4['w']['real_conformal'][0]:.0f}–{T4['w']['real_conformal'][2]:.0f} m"]]
    A(('cap', 'Table {{laddertab}}. The guarantee ladder: the witness of each unknown and its guaranteed 90% half-width '
              'with rain only and with rain and four loggers (T1A, T1); for $w$, the 90% interval from the prior and from '
              'the Fushë-Kuqe facts (T4).'))
    A(('table', ['Unknown', 'Its witness', 'Rain only', 'Rain + 4 loggers'], rows, [3.4, 6.4, 3.1, 4.1], 9.5))
    A(('h2', '5.5 What stays impossible with few conditions'))
    A(('b', 'A guarantee against the real aquifer without real ground truth: GARANCIA-GO guarantees under the prior given '
            'the rain, and the field check can refute that prior but never confirm it.'))
    A(('b', f'Structural errors outside the prior are invisible to the guarantee and only partly visible to the check '
            f'(T3: the parameter shift raised the alarm rate only to {P_["alarm"]:.2f} while the whole-function coverage '
            f'fell to {min(P_[k]["sup"] for k in BF):.2f}).'))
    A(('b', 'The dispersivity at a point: only the width of the transition zone is constrained.'))
    A(('b', 'Extremes outside the simulated range: the rain law must contain them for the guarantee to cover them.'))
    # ------------------------------------------------------------------------------------------- 6 limitations
    A(('h', '6. Limitations'))
    A(('b', 'Every card is partly verified: the landing pages were reached through search results only, and no full text '
            'was read.'))
    A(('b', 'The guarantees are marginal under the physical prior (or conditional on the rain record); they are not '
            'conditional on the field aquifer.'))
    A(('b', 'The test bed is a linear one-dimensional section and the Fushë-Kuqe chloride model is steady and '
            'sharp-interface; Proposition 6 holds exactly there and approximately under variable density.'))
    A(('b', 'The T4 correction uses a Gaussian score on the log scale; the distributional version (M3) would calibrate '
            'the whole posterior.'))
    A(('b', 'When the delay is uncertain, $\\kappa$ is not a well-defined target (T3); the recharge function is.'))
    return B
