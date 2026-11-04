"""Text of the second state-of-the-art review (English). blocks(D, SP, GE, GR) returns the block list; every number comes
from res/ (matja.json, matja_single.json, matja_spur.json, matja_price.json) and from the GARANCIA-GO results
(../garancia_go/res/). Conventions: $inline math$, **bold**, *italic*, ==yellow placeholder==, [text](url) hyperlink,
[[key]] equation number, {{key}} figure or table number."""
import json
import os

import numpy as np

from cards_matja import CARDS, INST_ORDER

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')

ANCHORS = [
    dict(key='A1', text='Angelopoulos, A. N., Bates, S., Fisch, A., Lei, L., & Schuster, T. (2024). Conformal risk '
                        'control. The Twelfth International Conference on Learning Representations (ICLR 2024). '
                        'arXiv:2208.02814 (PDF provided by the user).',
         url='https://arxiv.org/abs/2208.02814'),
    dict(key='A2', text='Tibshirani, R. (2023). Conformal prediction. Lecture notes, Advanced Topics in Statistical '
                        'Learning, Spring 2023, University of California, Berkeley (PDF provided by the user).',
         url='https://www.stat.berkeley.edu/~ryantibs/statlearn-s23/'),
]

SYN = [
    dict(key='S1', text='Dunbar, O. R. A., Howland, M. F., Schneider, T., & Stuart, A. M. (2022). Ensemble-based '
                        'experimental design for targeting data acquisition to inform climate models. Journal of Advances '
                        'in Modeling Earth Systems 14(9), e2022MS002997.', url='https://doi.org/10.1029/2022MS002997'),
    dict(key='S2', text='Huan, X., Jagalur, J., & Marzouk, Y. (2024). Optimal experimental design: formulations and '
                        'computations. Acta Numerica 33, 715–840.', url='https://doi.org/10.1017/S0962492924000023'),
    dict(key='S3', text='Bates, S., Angelopoulos, A., Lei, L., Malik, J., & Jordan, M. I. (2021). Distribution-free, '
                        'risk-controlling prediction sets. Journal of the ACM 68(6), Article 43, 1–34.',
         url='https://doi.org/10.1145/3478535'),
    dict(key='S4', text='Angelopoulos, A. N., Bates, S., Candès, E. J., Jordan, M. I., & Lei, L. (2025). Learn then test: '
                        'calibrating predictive algorithms to achieve risk control. Annals of Applied Statistics 19(2), '
                        '1641–1662.', url='https://doi.org/10.1214/24-AOAS1998'),
    dict(key='S5', text='Fannjiang, C., Bates, S., Angelopoulos, A. N., Listgarten, J., & Jordan, M. I. (2022). Conformal '
                        'prediction under feedback covariate shift for biomolecular design. Proceedings of the National '
                        'Academy of Sciences 119(43), e2204569119.', url='https://doi.org/10.1073/pnas.2204569119'),
    dict(key='S6', text='Calvello, E., Reich, S., & Stuart, A. M. (2025). Ensemble Kalman methods: a mean-field '
                        'perspective. Acta Numerica 34, 123–291.', url='https://doi.org/10.1017/S0962492924000060'),
    dict(key='S7', text='Huang, D. Z., Schneider, T., & Stuart, A. M. (2022). Iterated Kalman methodology for inverse '
                        'problems. Journal of Computational Physics 463, 111262.',
         url='https://doi.org/10.1016/j.jcp.2022.111262'),
    dict(key='S8', text='Barber, R. F., Candès, E. J., Ramdas, A., & Tibshirani, R. J. (2023). Conformal prediction beyond '
                        'exchangeability. Annals of Statistics 51(2), 816–845.', url='https://doi.org/10.1214/23-AOS2276'),
    dict(key='S9', text='Lees, T., Buechel, M., Anderson, B., Slater, L., Reece, S., Coxon, G., & Dadson, S. J. (2021). '
                        'Benchmarking data-driven rainfall–runoff models in Great Britain. Hydrology and Earth System '
                        'Sciences 25, 5517–5534 (partly verified; subtitle not confirmed).',
         url='https://doi.org/10.5194/hess-25-5517-2021'),
    dict(key='S10', text='Angelopoulos, A. N., & Bates, S. (2023). Conformal prediction: a gentle introduction. '
                         'Foundations and Trends in Machine Learning 16(4), 494–591.',
         url='https://doi.org/10.1561/2200000101'),
]

OTHER = [
    dict(key='D1', text='Zeqiraj, D. (2026). Inputs, dispersion and boundary conditions from rain alone: twenty papers from '
                        'Oxford, Caltech, Berkeley and MIT (2020–2026) and GARANCIA-GO, guaranteed bands calibrated on '
                        'simulated aquifers ("review I"). docs/literature/Literature_review_Inputs_Dispersion_Boundary_'
                        'Conditions_from_Rain_Oxford_Caltech_Berkeley_MIT_2020-2026.docx in this repository.', url=None),
    dict(key='D2', text='Internal documents of the project: RINDËRTIMI-GO, "Reconstructing all boundary conditions of a '
                        'coastal aquifer from rain and the Fushë-Kuqe data" (November 2026; test bed and ensemble smoother '
                        'with the exact solver); SHIU-GO (rain law, Erlang-2 vadose filter); the code of this review in '
                        'experiments/matja_go/.', url=None),
]


def card_ref(c):
    lk = c['links'][0][1]
    return dict(key=c['id'], text=f"{c['authors']} ({c['year']}). {c['title']}. {c['venue']}.", url=lk)


def all_refs():
    return ANCHORS + [card_ref(c) for c in CARDS] + SYN + OTHER


def L(key, label=None):
    for r in all_refs():
        if r['key'] == key:
            return f"[{label or key}]({r['url']})" if r['url'] else (label or key)
    raise KeyError(key)


def load_extra():
    out = {}
    for k in ('single', 'price'):
        with open(os.path.join(RES, f'matja_{k}.json')) as fh:
            out[k] = json.load(fh)
    return out


def pc(x):
    """signed percentage change, typographic minus."""
    v = 100 * x
    s = f'{v:+.0f}'
    return s.replace('-', '−') if s not in ('+0', '-0') else '0'


def rng_(xs, d=3):
    a, b = f'{min(xs):.{d}f}', f'{max(xs):.{d}f}'
    return a if a == b else f'{a}–{b}'


SITE_KM = {f'L{j}': x for j, x in enumerate(('0.25', '0.75', '1.25', '2.0', '2.75', '3.5', '4.25', '4.75'))}


def dname(design):
    """'L3+L5+L7' -> 'loggers at 2.0, 3.5, 4.75 km'."""
    if not design:
        return 'rain only'
    parts = sorted(design, key=lambda c: (c == 'TG', float(SITE_KM.get(c, 99))))
    kms = [SITE_KM[c] for c in parts if c != 'TG']
    s = ('logger at ' if len(kms) == 1 else 'loggers at ') + ', '.join(kms) + ' km' if kms else ''
    if 'TG' in parts:
        s = (s + ' + ' if s else '') + 'tide gauge'
    return s


# ------------------------------------------------------------------------------------------------------------ blocks
def blocks(D, SP, GE, GR):
    X = load_extra()
    S, PR = X['single'], X['price']
    base = S['rain only']
    tg = S['TG']
    fr = D['fresh']
    G3 = ('r', 'qL', 'kappa')
    # T6: the tide gauge with rain only, fresh pool
    tgW = {g: tg[g]['halfwidth'] / base[g]['halfwidth'] - 1 for g in G3}
    tgE = {g: tg[g]['es_halfwidth'] / base[g]['es_halfwidth'] - 1 for g in G3}
    tgX = {g: tg[g]['exact_halfwidth'] / base[g]['exact_halfwidth'] - 1 for g in G3}
    l0q = {k: S['L0']['qL'][k] / base['qL'][k] - 1 for k in ('halfwidth', 'es_halfwidth', 'exact_halfwidth')}
    eta_tg = (base['eta']['halfwidth'], tg['eta']['halfwidth'])
    neg_eta = [c for c in S if not c.startswith('_') and c not in ('rain only', 'TG')
               and S[c]['eta']['halfwidth'] > base['eta']['halfwidth']]
    # T7: paths on the fresh pool
    P = D['paths']
    end = {}
    for g in G3:
        for cr in ('es', 'oracle', 'matja'):
            d = '+'.join(sorted(P[f'{g}/{cr}'][-1]['design']))
            end[g, cr] = dict(name=d, W=fr[d][g]['halfwidth'], E=fr[d][g]['es_halfwidth'], X=fr[d][g]['exact_halfwidth'],
                              risk=fr[d][g]['crc_risk'], cover=fr[d][g]['sup_cover'],
                              design=P[f'{g}/{cr}'][-1]['design'])
    allrisk = [fr[n][g]['crc_risk'] for n in fr for g in G3]
    allcov = [fr[n][g]['sup_cover'] for n in fr for g in G3]
    kap2 = {cr: fr['+'.join(sorted(P[f'kappa/{cr}'][1]['design']))]['kappa']['halfwidth'] for cr in ('es', 'oracle', 'matja')}
    cA, cB = '+'.join(sorted(P['r/matja'][1]['design'])), '+'.join(sorted(P['r/es'][1]['design']))
    tie = (D['criteria'][cA]['r']['matja'], D['criteria'][cB]['r']['matja'], fr[cA]['r']['halfwidth'],
           fr[cB]['r']['halfwidth'])
    ratio = D['ratio']
    rr = {g: (min(ratio[k][g] for k in ratio), max(ratio[k][g] for k in ratio)) for g in G3}
    # selection optimism: pool A against the fresh pool for the chosen designs
    opt = []
    for key, steps in P.items():
        g, cr_ = key.split('/')
        if cr_ != 'matja':
            continue
        for s_ in steps:
            n = '+'.join(sorted(s_['design']))
            opt.append(D['criteria'][n][g]['matja'] / fr[n][g]['halfwidth'] - 1)
    # T8: the law of the spurious value
    Ns = sorted(int(k) for k in SP['sizes'])
    sz = {n: SP['sizes'][str(n)] for n in Ns}

    def meas(n, kind):
        r_ = sz[n]
        if kind == 'spr':
            return [r_['tg'][g]['spr2'] / r_['base'][g]['spr2'] for g in G3]
        if kind == 'err':
            return [r_['tg'][g]['err2'] / r_['base'][g]['err2'] for g in G3]
        if kind == 'es':
            return [r_['tg'][g]['es'] / r_['base'][g]['es'] for g in G3]
        return [r_['tg'][g]['matja'] / r_['base'][g]['matja'] for g in G3]
    spr_dev = max(abs(v - sz[n]['pred_spread']) for n in Ns for v in meas(n, 'spr'))
    err_dev = max(abs(v / sz[n]['pred_error'] - 1) for n in Ns for v in meas(n, 'err'))
    n128, n512 = sz[128], sz[512]
    # review I numbers
    T1, HA, HB, T4 = GE['T1'], GE['T1A_halfwidth'], GE['T1_halfwidth'], GE['T4']
    BF = ('eta', 'qL', 'r', 'h0', 'kappa')
    r1_crc = rng_([T1[k]['split']['crc_risk'] for k in BF])
    r1_sup = rng_([T1[k]['split']['sup_cover'] for k in BF])
    r1_raw = rng_([T1[k]['raw']['frac_out'] for k in ('eta', 'qL', 'r', 'h0')], 2)
    S4 = T4['subsets']

    B = []
    A = B.append
    A(('title', 'State of the art II: inputs, dispersion and boundary conditions from rain'))
    A(('subtitle', 'Twenty more papers from Oxford, Caltech, Berkeley and MIT (2020–2026), chosen for direct use; the state '
                   'of the art and the step beyond it, in the form a NATO proposal asks for; and MATJA-GO, the guaranteed '
                   'value of a measurement'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation · companion to review I '
                 '(GARANCIA-GO)'))
    # ------------------------------------------------------------------------------------------- 1 outcome
    A(('h', '1. Outcome'))
    A(('bbox', [
        '**Twenty new papers, five per institution, 2020–2026, each with links** (Section 3, Figure {{map}}). None was a '
        'card of review I or of the earlier reviews. They were chosen for what we can use now: recharge from rain and '
        'satellites (C4, M2, B1, O2), the sea boundary as a relative sea level (C1, C3, C5, B2), the initial interface '
        '(O1), dispersion as a non-constant (M5), and the choice of where to measure (B3, B4, O3, M1). Every card states '
        'the state of the art the paper sets, what it cannot yet do for us, three lessons and an innovation step.',
        '**State of the art and beyond, ready for the proposal** (Section 2, Table {{sotab}}). Seven topics; for each, '
        'the best current work, its limit for a coastal aquifer known only through rain, our step beyond it and the test '
        'that backs the step.',
        '**Innovation: MATJA-GO, the guaranteed value of a measurement** (Section 4). The value of an instrument is the '
        'guaranteed band width it removes, calibrated on simulated aquifers that carry the instrument\'s data; the '
        'choice is made on one pool of simulations and the guarantee is re-established on a fresh pool, so it holds '
        'for the design that was chosen (Proposition M1). Proposition M3 gives the exact law of what a finite ensemble '
        'gets wrong: an instrument that knows nothing about the goal shrinks the ensemble spread by the factor '
        '$1-\\delta_N$ and grows the error by $1+\\varepsilon_N$, both about $d_s/(N-1)$.',
        f'**Test 1: the tide gauge with rain only** (T6, 300 fresh simulated aquifers). It carries no information on the '
        f'recharge, the inflow or $\\kappa$: the exact posterior does not move. The raw ensemble says it narrows their '
        f'bands by {pc(-tgE["r"]).lstrip("+")}%; the guaranteed band in fact widens by {pc(min(tgW.values())).lstrip("+")}–'
        f'{pc(max(tgW.values())).lstrip("+")}%. For the sea level itself it is worth a factor '
        f'{eta_tg[0] / eta_tg[1]:.0f}. Of the 36 pairs of instrument and goal, {PR["n_negative"]} have a negative '
        f'guaranteed value, and the price rule of Remark M3 predicts the sign of all {PR["sign_agree"]}.',
        f'**Test 2: choosing three instruments** (T7). For the recharge and the inflow the raw ensemble, the exact '
        f'posterior and MATJA-GO choose nearly the same loggers (final guaranteed half-widths within '
        f'{100 * (max(end["r", c]["W"] for c in ("es", "oracle", "matja")) / min(end["r", c]["W"] for c in ("es", "oracle", "matja")) - 1):.0f}%). '
        f'For $\\kappa$ the ensemble claims {end["kappa", "es"]["E"]:.3f} for its design, the exact posterior gives '
        f'{end["kappa", "es"]["X"]:.3f} and the guarantee {end["kappa", "es"]["W"]:.3f}: a factor '
        f'{end["kappa", "es"]["W"] / end["kappa", "es"]["E"]:.0f} of overconfidence, and a third logger buys nothing '
        f'that can be guaranteed. Every reported guarantee held on the fresh pool (share of weeks outside '
        f'{rng_(allrisk)}, whole-function coverage {rng_(allcov, 2)}).',
        f'**Test 3: the exact law** (T8). Over $N$ = {Ns[0]}–{Ns[-1]} members the measured spread factors match '
        f'$1-\\delta_N$ to within {spr_dev:.3f}, and the error factors match $1+\\varepsilon_N$ to within '
        f'{100 * err_dev:.0f}%. Even with {Ns[-1]} members a worthless tide gauge widens the guaranteed band by '
        f'{rng_([100 * (v - 1) for v in meas(512, "W")], 0)}%.',
        '**What to measure first when only the rain is known** (Section 4.4): a logger in the middle of the aquifer for '
        'the recharge and $\\kappa$, a logger near the inland edge for the inflow, a tide gauge only when the goal is '
        'the sea level or the toe, a deep salinity profile for dispersion; and, beyond two loggers, a larger ensemble '
        'before a third logger.']))
    # ------------------------------------------------------------------------------------------- 2 SOTA and beyond
    A(('h', '2. State of the art and the step beyond it'))
    A(('p', 'The problem is the one of review I (D1): a simulation of a coastal aquifer needs its input parameters '
            '(transmissivity, the recharge coefficient $\\kappa$, the vadose delay $\\tau$), its dispersion coefficient and '
            'its boundary and initial conditions (sea level $\\eta(t)$, inland inflow $q_L(t)$, recharge $r(t)$, initial '
            'head $h_0$), when the only series that is always there is the rain. Review I answered with guaranteed '
            'bands (GARANCIA-GO). This review asks the next question, the one a field campaign faces: **which measurement '
            'should be added first, and what is it guaranteed to buy?**'))
    A(('p', '**Text for the proposal.** Recharge and boundary forcing can now be estimated from rain, soil moisture and '
            'space geodesy at basin to global scale (C4, M2, C2, O2), and seawater-intrusion risk has been projected '
            'globally with the recharge and sea-level drivers separated (C1). Calibration with few model runs is routine '
            'with ensemble Kalman methods and derivative-free optimisers (C4, O4), and monitoring networks are reduced '
            'with machine-learning pipelines (B3) or guided by zonation (B4). Two limits remain. First, none of these '
            'methods gives a finite-sample guarantee for the boundary conditions it estimates, and controlled experiments '
            'show that forecast intervals in porous-media flow are too narrow (M4). Second, measurements are chosen by '
            'the model\'s own spread, by interpolation skill or by information gain under the model, so an instrument '
            'that is worthless, or worse, can be valued positively. The project goes beyond the state of the art with '
            'guaranteed bands for every boundary and initial condition, calibrated on aquifers simulated from the rain '
            '(GARANCIA-GO, review I), and with MATJA-GO, which values each candidate instrument by the guaranteed width '
            'it removes, keeps the guarantee after the choice, and has an exact law for the error of ensemble-based '
            'design. Both are tested numerically below and in review I.'))
    rows = [
        ['Recharge and forcing from rain',
         'Satellite + Hydrus emulator for global recharge (M2); Richards land model with EKI (C4); national rain-driven '
         'model (O2); rock moisture gates recharge (B1)',
         'No guarantee; deterministic or uncalibrated spreads; a constant coefficient fails in dry years',
         'Rain-conditional prior → simulated aquifers → guaranteed bands for $r$, $q_L$, $\\eta$, $h_0$; threshold law '
         'in the prior (B1)',
         f'Review I, T1: share of weeks outside {r1_crc}, whole-function coverage {r1_sup}'],
        ['Calibration with few runs',
         'Ensemble Kalman inversion and pipelines (C4; S6, S7); derivative-free tuning (O4); PEST (O2)',
         'The ensemble spread is not a guarantee; forecasters are overconfident (M4); equifinality (O4)',
         'The calibrated factor $\\hat\\lambda_D/1.645$ is a measured inflation, design by design',
         f'T7: ensemble half-width for $\\kappa$ up to {rr["kappa"][1]:.0f} times too narrow; after calibration all '
         f'guarantees hold (risk {rng_(allrisk)})'],
        ['Choosing measurements',
         'Ensemble-based design (S1); Bayesian design (S2); network reduction (B3); zonation (B4); guaranteed spatial '
         'inference (M1)',
         'Value judged by the model\'s own spread or by interpolation skill; no guarantee after selection',
         'MATJA-GO: value = guaranteed width removed; valid after selection (M1); exact law of the spurious value (M3)',
         f'T6: tide gauge {pc(min(tgE.values()))}% by the ensemble, {pc(min(tgW.values()))} to {pc(max(tgW.values()))}% '
         f'guaranteed; {PR["sign_agree"]}/{PR["n"]} signs predicted'],
        ['The sea boundary',
         'Global intrusion with recharge and sea-level drivers (C1); land motion at 90 m (C3); SWOT (C5); heads below '
         'sea level in 250 000 wells (B2)',
         'Sea level taken as absolute; not assimilated; no local guarantee; no sign test',
         '$\\eta$ as relative sea level with land motion as an instrument; guaranteed sign test of $h-\\eta$; '
         'altimetry against a tide gauge priced by MATJA-GO',
         f'T6: tide gauge cuts the sea-level half-width from {eta_tg[0]:.3f} to {eta_tg[1]:.3f} m and is worth nothing '
         f'for $r$, $q_L$, $\\kappa$'],
        ['Initial conditions',
         'Interface memory of past sea-level positions (O1)',
         'Elsewhere the initial interface is assumed in equilibrium with today\'s sea',
         'Initial interface drawn from a sea-level history in the prior; guaranteed $h_0$ band',
         f'Review I, T1A/T1: $h_0$ half-width {HA["h0"]["crc"]:.2f} m with rain only, {HB["h0"]["crc"]:.2f} m with four '
         f'loggers'],
        ['Dispersion coefficient',
         'Dispersion set by flow disorder (M5); mixing is the hardest part to forecast (M3); permeability from salinity '
         'profiles (O1)',
         'No field identification of dispersivity from rain or heads',
         'Ancillarity of dispersion to rain and heads (review I, Proposition 6); calibrated width $w$; depth profiles '
         'priced as instruments',
         f'Review I, T4: heads leave $w$ at its prior ({S4["heads"]["w"][0]:.1f}–{S4["heads"]["w"][2]:.1f} m); chloride '
         f'facts move it to {S4["chloride"]["w"][0]:.0f}–{S4["chloride"]["w"][2]:.0f} m'],
        ['Fast surrogates',
         'Hard-constrained mixture-of-experts solvers (B5); neural operators (review I, B1, C1)',
         'Surrogate error enters the band without a guarantee',
         'Conformal calibration on simulated truths absorbs the remaining surrogate error',
         'Review I, Propositions 1–2 (any reconstructor)'],
    ]
    A(('cap', 'Table {{sotab}}. State of the art (2020–2026) and the step beyond it. Card numbers refer to Section 3; S '
              'and D numbers to the references; T numbers to the tests of Section 4 and of review I.'))
    A(('table', ['Topic', 'State of the art', 'Its limit for our problem', 'Our step beyond', 'Evidence'], rows,
       [2.6, 3.9, 3.2, 3.8, 3.5], 9, False))
    # ------------------------------------------------------------------------------------------- 3 the papers
    A(('h', '3. The twenty papers'))
    A(('p', 'Five papers per institution, all published in 2020–2026 (Figure {{map}}). Four rules decided the selection: '
            'direct use for inferring inputs, dispersion or boundary conditions from rain with few data, or for choosing '
            'what to measure; a link to the institution at the time of publication (for Caltech this includes JPL, which '
            'Caltech manages; for Berkeley, Lawrence Berkeley National Laboratory); a contribution that is a state of the '
            'art in its field; and no paper that was a card in review I or in the earlier reviews of the series. The '
            'searches found no 2020–2026 paper from these institutions that identifies a field dispersivity from rain '
            'or heads, nor one that designs groundwater monitoring with a guarantee; both gaps are stated in Table '
            '{{sotab}}.'))
    A(('p', '**Verification.** The hosts doi.org, arxiv.org, openreview.net and most publisher pages were blocked in this '
            'environment, so every landing page was reached through search results that quote it, and every card is '
            'marked partly verified. Where an author list or a volume could not be confirmed, the card gives only what '
            'was seen and says so.'))
    names = dict(Oxford='University of Oxford', Caltech='California Institute of Technology (with JPL)',
                 Berkeley='University of California, Berkeley (with Lawrence Berkeley National Laboratory)',
                 MIT='Massachusetts Institute of Technology')
    for j, inst in enumerate(INST_ORDER, start=1):
        A(('h2', f'3.{j} {names[inst]}'))
        for c in CARDS:
            if c['inst'] == inst:
                A(('card', c))
                if c['id'] == 'O1':           # the overview figure after the first card: no half-empty page
                    A(('img', 'map', 17.0))
                    A(('cap', 'Figure {{map}}. The twenty papers against the step of the synthesis they serve and the '
                              'unknown they inform. Colour gives the institution; a filled square is a direct lesson, an '
                              'open square an indirect one.'))
    # ------------------------------------------------------------------------------------------- 4 MATJA-GO
    A(('h', '4. Innovation: MATJA-GO, the guaranteed value of a measurement'))
    A(('img', 'scheme', 17.0))
    A(('cap', 'Figure {{scheme}}. MATJA-GO. Each candidate design $D$ (rain plus a set of instruments) gets its own '
              'simulated aquifers, which carry the data that design would give; the same reconstructor runs on all of '
              'them; conformal risk control turns its spread into a guaranteed width $W(D)$; the instrument that '
              'removes most guaranteed width is added; and the chosen design is recalibrated on fresh simulated '
              'aquifers before its band is used.'))
    A(('h2', '4.1 The question and the set-up'))
    A(('p', 'The test bed is that of review I and RINDËRTIMI-GO (D2): a 5 km section of 32 cells and 64 weekly steps, '
            'transmissivity 1500 m²/d, storage 0.05, a recharge law $r=\\kappa\\,(k_\\tau*P)+e$ with the Erlang-2 vadose '
            'kernel ($\\tau$ = 14 d) and lognormal $\\kappa$ (median 0.35, log-sd 0.25), and Gaussian random fields for '
            'the sea level, the inland inflow, the recharge error and the initial head. The rain is always known. The '
            'candidates are an automatic logger at one of eight sites (0.25, 0.75, 1.25, 2.0, 2.75, 3.5, 4.25 and 4.75 km '
            'from the sea; weekly heads, noise 2 cm) and a tide gauge (weekly sea level, noise 1 cm). The reconstructor '
            'is the ensemble smoother with the exact solver (128 members), started from the same prior ensemble for '
            'every design (common random numbers), so differences between designs are not sampling noise of the prior. '
            'Because the test bed is linear given $\\kappa$, the exact posterior is available as an oracle; in the field '
            'it is not.'))
    A(('p', 'For a design $D$ and a goal (the weekly recharge, the weekly inflow, or $\\kappa$), let $\\bar s_D$ be the '
            'mean spread of the reconstruction on the simulated aquifers of $D$, $\\bar\\sigma_D$ the mean exact '
            'posterior standard deviation, and $\\hat\\lambda_D$ the conformal-risk-control multiplier of review I for '
            'the share of weeks outside the band $m\\pm\\lambda s$, equation [[lam]]. Three criteria are compared:'))
    A(('eq', 'crit', ['E(D)=1.645\\,\\bar s_D\\text{, the raw ensemble;}',
                      'X(D)=1.645\\,\\bar\\sigma_D\\text{, the exact posterior;}',
                      'W(D)=\\hat\\lambda_D\\,\\bar s_D\\text{, guaranteed: MATJA-GO;}']))
    A(('eq', 'lam', ['\\hat\\lambda_D=\\inf\\left\\{\\lambda:\\frac{n}{n+1}\\hat R_D(\\lambda)+\\frac{1}{n+1}\\le\\alpha\\right\\}'
                     '\\text{, with }\\hat R_D(\\lambda)=\\frac{1}{n}\\sum_{i=1}^{n}L_i^{D}(\\lambda),']))
    A(('p', 'where $L_i^D(\\lambda)$ is the share of the 64 weeks of simulated aquifer $i$ outside the band, and '
            '$\\alpha$ = 0.10. The value of an instrument and the greedy choice are'))
    A(('eq', 'value', ['V(c\\mid D)=W(D)-W(D\\cup\\{c\\}),', 'D_{k+1}=D_k\\cup\\left\\{\\arg\\max_c V(c\\mid D_k)\\right\\}']))
    A(('p', f'and the same with $E$ or $X$ in place of $W$ for the other two criteria. Selection uses pool A '
            f'({D["poolA"]} simulated aquifers); every chosen design is then recalibrated and scored on pool B '
            f'({D["poolB"]} fresh aquifers, split 300 times into calibration and test halves).'))
    A(('h2', '4.2 Guarantees, and what an ensemble gets wrong'))
    A(('prop', 'Proposition M1 (the guarantee holds for the design that was chosen).',
            'Let pool A, pool B and the field case be independent, and let pool B and the field case be draws from the '
            'physical prior given the rain. Let $\\hat D$ be chosen by any rule that uses pool A only (greedy on $W$, on '
            '$E$, by hand). If $\\hat\\lambda_{\\hat D}$ is computed by [[lam]] on pool B, the field band of design '
            '$\\hat D$ satisfies $\\mathbb{E}[L_{n+1}^{\\hat D}(\\hat\\lambda_{\\hat D})]\\le\\alpha$, and the sup-norm '
            'band of review I covers the whole function with probability at least $1-\\alpha$.'))
    A(('proof', 'Given pool A, $\\hat D$ is fixed. Pool B and the field case are independent of pool A, so given pool A '
                'they are still i.i.d. draws, and the reconstructor of design $\\hat D$ is one fixed map applied to each '
                'of them; conformal risk control (anchor A1, Theorem 1) and split conformal prediction (anchor A2) apply '
                'conditionally on pool A. Take the expectation over pool A.'))
    A(('prop', 'Remark M1 (why a fresh pool).',
            f'If pool A is used both to choose and to calibrate, the reported width is the minimum of several noisy '
            f'estimates and is biased low, and the guarantee is lost unless a correction for the number of candidates '
            f'is made (for example Learn-then-Test, {L("S4", "S4")}). Here the bias is small: for the designs MATJA-GO '
            f'chose, the pool-A width lies between {-100 * min(opt):.0f}% below and {100 * max(opt):.0f}% above the '
            f'fresh one, and the values below are all at the first step, where the best of nine candidates is taken. The '
            f'fresh pool removes the question.'))
    A(('prop', 'Remark M2 (when the ensemble ranks designs correctly).',
            'For large calibration pools $\\hat\\lambda_D\\to\\lambda_D^{\\ast}$, so $E(D)=(1.645/\\lambda_D^{\\ast})\\,W(D)$. '
            'The raw ensemble ranks two designs as MATJA-GO does if and only if their miscalibration factors '
            '$\\lambda_D^{\\ast}/1.645$ do not reverse the order of their spreads; in particular whenever the factor is '
            'the same for every design. The calibrated factor $\\hat\\lambda_D/1.645$ is therefore the inflation that '
            'makes design $D$ honest, measured on simulated aquifers instead of tuned by hand.'))
    A(('p', f'Remark M2 explains the two regimes of the tests. For the recharge and the inflow the factor lies within '
            f'{rr["r"][0]:.2f}–{rr["r"][1]:.2f} and {rr["qL"][0]:.2f}–{rr["qL"][1]:.2f} over the {len(ratio)} designs '
            f'evaluated, but differs by only a few percent among the leading candidates of each step, which their '
            f'spreads separate by more, so the rankings agree. For $\\kappa$ it ranges from {rr["kappa"][0]:.2f} to '
            f'{rr["kappa"][1]:.1f}, and the raw ensemble can be trusted neither to rank designs nor to report widths.'))
    A(('prop', 'Proposition M3 (an instrument that knows nothing about the goal).',
            'Let $\\theta$ be a scalar goal (one week of the recharge or of the inflow, or $\\kappa$) and $c$ an '
            'instrument whose data $y_c$ are independent of $\\theta$ under the prior given the rain, with no other '
            'data. Let $C$ be the prior covariance of $y_c$, $R$ its noise covariance, $\\hat C$ its sample covariance in '
            'an ensemble of $N$ prior members, and let the stochastic ensemble smoother update the ensemble with $y_c$. '
            'Then (i) the exact posterior of $\\theta$ is its prior, so the exact value of $c$ is zero; (ii) the expected '
            'ensemble variance $\\hat s^{2}$ of $\\theta$ falls, and (iii) the error $e=\\theta-m$ of the ensemble mean '
            'becomes $e_{+}=e-\\Delta$ with $\\mathbb{E}[\\Delta\\mid e]=0$, a mean-preserving spread of $e$, with'))
    A(('eq', 'm3', ['\\mathbb{E}\\,\\hat s_{+}^{2}=(1-\\delta_N)\\,\\mathbb{E}\\,\\hat s^{2},',
                    '\\mathbb{E}\\,e_{+}^{2}=(1+\\varepsilon_N)\\,\\mathbb{E}\\,e^{2},']))
    A(('eq', 'deps', ['\\delta_N=\\frac{1}{N-1}\\,\\mathbb{E}\\,\\mathrm{tr}\\left[\\hat C(\\hat C+R)^{-1}\\right],',
                      '\\varepsilon_N=\\frac{1}{N-1}\\,\\mathbb{E}\\,\\mathrm{tr}\\left[\\hat C(\\hat C+R)^{-1}(C+R)'
                      '(\\hat C+R)^{-1}\\right].']))
    A(('p', 'The factors do not depend on the goal. For large $N$, $\\hat C\\to C$ and'))
    A(('eq', 'first', '\\delta_N\\approx\\varepsilon_N\\approx\\frac{d_s}{N-1}\\text{, with }d_s=\\mathrm{tr}\\left[C(C+R)^{-1}\\right]'
                      '\\text{ the signal degrees of freedom of }c.'))
    A(('proof', 'Write the prior members as $(\\theta_j,Y_j)$, $j=1,\\dots,N$, with deviations $a_j=\\theta_j-\\bar\\theta$ '
                'and $b_j=Y_j-\\bar Y$, $B$ the matrix of the $b_j$. Independence makes $(\\theta,\\theta_j)$ independent '
                'of $(y_c,Y_j)$. The gain is $K=\\sum_j a_jb_j^{\\top}(B^{\\top}B+(N-1)R)^{-1}$ and the update '
                '$\\theta_{j+}=\\theta_j+K(y_c+\\epsilon_j-Y_j)$ with independent $\\epsilon_j\\sim N(0,R)$. (i) The '
                'likelihood of $y_c$ does not involve $\\theta$. (ii) Averaging the sample variance of $\\theta_{j+}$ over '
                'the $\\epsilon_j$ gives $\\hat s^{2}-\\hat C_{\\theta Y}(\\hat C+R)^{-1}\\hat C_{Y\\theta}$; since '
                '$\\mathbb{E}[aa^{\\top}]=\\sigma^{2}(I-\\mathbf{1}\\mathbf{1}^{\\top}/N)$ and $B^{\\top}\\mathbf{1}=0$, '
                'its expectation given $B$ is $\\sigma^{2}-\\sigma^{2}\\,\\mathrm{tr}[\\hat C(\\hat C+R)^{-1}]/(N-1)$, '
                'and $\\mathbb{E}\\,\\hat s^{2}=\\sigma^{2}$. (iii) The mean moves by $\\Delta=Kv$ with '
                '$v=y_c-\\bar Y+\\bar\\epsilon$; for Gaussian $y_c$ the sample mean $\\bar Y$ is independent of $B$, so $v$ '
                'is independent of $(a,B,\\theta)$ with mean 0 and covariance $(1+1/N)(C+R)$. Hence '
                '$\\mathbb{E}[\\Delta\\mid e]=0$ and $\\mathbb{E}\\Delta^{2}=(1+1/N)\\,\\mathbb{E}[K(C+R)K^{\\top}]$, which '
                'is $(1+1/N)\\sigma^{2}$ times the trace in [[deps]] divided by $N-1$; and '
                '$\\mathbb{E}\\,e^{2}=(1+1/N)\\sigma^{2}$. Replacing $\\hat C$ by $C$ gives [[first]].'))
    A(('p', f'Spurious covariances of small ensembles are well known in data assimilation, where they motivate '
            f'localisation and inflation. Proposition M3 states their consequence for design exactly: an ensemble-based '
            f'criterion ({L("S1", "S1")}) gives a worthless instrument the value $1-\\sqrt{{1-\\delta_N}}$ of the '
            f'half-width, while its guaranteed value is negative, about $1-\\sqrt{{1+\\varepsilon_N}}$. For the tide gauge '
            f'$d_s$ = {SP["d_s"]:.1f}; with $N$ = 128, $\\delta_N$ = {n128["delta"]:.3f} and $\\varepsilon_N$ = '
            f'{n128["eps"]:.3f} (Monte Carlo over 4000 ensembles), so the ensemble promises a '
            f'{100 * (1 - n128["pred_es"]):.0f}% narrower band and delivers a {100 * (n128["pred_matja"] - 1):.0f}% wider '
            f'one.'))
    A(('prop', 'Remark M3 (the price of an instrument, a first-order rule).',
            'An instrument that does inform the goal removes a fraction $\\rho_c$ of its exact posterior variance, and '
            'the finite ensemble adds about $\\varepsilon_N(c)\\approx d_s(c)/(N-1)$ through the data directions the goal '
            'does not share. To first order the guaranteed half-width is multiplied by $\\sqrt{(1-\\rho_c)(1+'
            '\\varepsilon_N)}$, so the guaranteed value of $c$ is negative when'))
    A(('eq', 'price', '\\rho_c<\\frac{\\varepsilon_N(c)}{1+\\varepsilon_N(c)}.'))
    A(('p', f'The rule needs only the exact information of the instrument and its signal degrees of freedom, both '
            f'computable before it is bought. On the fresh pool it predicts the sign of the guaranteed value for '
            f'{PR["sign_agree"]} of the {PR["n"]} pairs of instrument and goal, and the factor with a median error of '
            f'{100 * PR["median_rel_err"]:.1f}% (largest {100 * PR["max_rel_err"]:.1f}%).'))
    A(('box', ['**What is new.** (1) The value of a measurement defined as the guaranteed band width it removes, '
               'calibrated on simulated aquifers that carry the measurement\'s data, with the guarantee kept after the '
               'selection (Proposition M1). (2) The ensemble ranking as a special case, correct exactly when the '
               'miscalibration factor is constant across designs, and the calibrated factor as a measured inflation '
               '(Remark M2). (3) An exact law for the spread and error of a stochastic ensemble smoother updated with a '
               'worthless instrument, for any goal (Proposition M3), and a first-order price rule that tells in advance '
               'when an informative instrument still has a negative guaranteed value (Remark M3). To our knowledge none '
               'of these appears in the forty papers of reviews I and II or in the design literature they cite.']))
    # ------------------------------------------------------------------------------------------- 4.3 tests
    A(('h2', '4.3 Tests'))
    A(('p', '**T6** scores every single instrument added to the rain on the fresh pool; **T7** runs the greedy choice of '
            'three instruments with each criterion and scores the chosen designs on the fresh pool; **T8** measures the '
            'law of Proposition M3 for $N$ = 32 to 512 members on 300 further aquifers. Code and logs: '
            'experiments/matja_go/ (matja_exp.py, matja_single.py, matja_spur.py, matja_price.py).'))
    A(('p', f'**T6: one instrument at a time.** Figure {{{{single}}}} and Table {{{{t6}}}}. Every logger helps the recharge '
            f'and $\\kappa$, most in the middle of the aquifer; for the inflow the value grows towards the inland edge. '
            f'The coastal logger at 0.25 km is the exception: it mostly witnesses the sea level, its exact value for the '
            f'inflow is small ({pc(l0q["exact_halfwidth"])}%), the ensemble promises {pc(l0q["es_halfwidth"])}%, and the '
            f'guaranteed band widens by {pc(l0q["halfwidth"]).lstrip("+")}%. The tide gauge has no exact value for the '
            f'recharge, the inflow or $\\kappa$; the ensemble promises {pc(tgE["r"])}% and the guaranteed bands widen by '
            f'{pc(min(tgW.values())).lstrip("+")}–{pc(max(tgW.values())).lstrip("+")}%. For the sea level the roles turn: '
            f'the tide gauge cuts its guaranteed half-width from {eta_tg[0]:.3f} to {eta_tg[1]:.3f} m, while '
            f'{len(neg_eta)} of the 8 loggers widen it slightly. In all, {PR["n_negative"]} of the {PR["n"]} pairs have a '
            f'negative guaranteed value, and Remark M3 predicts every sign.'))
    A(('img', 'single', 17.0))
    A(('cap', 'Figure {{single}}. T6: the half-width removed by each instrument added to the rain, on the fresh pool, as '
              'the raw ensemble reports it (orange), as the exact posterior gives it (grey) and as it can be guaranteed '
              '(blue). Points left of zero widen the band.'))
    t6 = []
    labs = dict((c, f'logger {SITE_KM[c]} km') for c in SITE_KM)
    labs['TG'] = 'tide gauge'
    for c in list(SITE_KM) + ['TG']:
        row = [labs[c]]
        for g in ('r', 'qL', 'kappa', 'eta'):
            w = S[c][g]['halfwidth'] / base[g]['halfwidth'] - 1
            e = S[c][g]['es_halfwidth'] / base[g]['es_halfwidth'] - 1
            x = S[c][g]['exact_halfwidth'] / base[g]['exact_halfwidth'] - 1
            cell = f'{pc(w)} / {pc(e)} / {pc(x)}'
            row.append(f'**{cell}**' if w > 0 else cell)
        t6.append(row)
    A(('cap', 'Table {{t6}}. T6: change of the 90% half-width, in %, when one instrument is added to the rain: guaranteed '
              '/ raw ensemble / exact posterior (fresh pool, 300 aquifers). Bold: a negative guaranteed value. Rain-only '
              f'guaranteed half-widths: recharge {base["r"]["halfwidth"]:.3f} mm/d, inflow {base["qL"]["halfwidth"]:.3f} '
              f'm²/d, $\\kappa$ {base["kappa"]["halfwidth"]:.3f}, sea level {base["eta"]["halfwidth"]:.3f} m.'))
    A(('table', ['Instrument', 'Recharge r', 'Inflow qL', 'Coefficient κ', 'Sea level η'], t6, [3.4, 3.4, 3.4, 3.4, 3.4], 9.5))
    A(('p', f'**T7: three instruments chosen greedily.** Figure {{{{paths}}}} and Table {{{{t7}}}}. For the recharge the '
            f'raw ensemble and the exact posterior choose the {dname(end["r", "es"]["design"])}; MATJA-GO, after a tie at '
            f'the second step ({tie[0]:.3f} against {tie[1]:.3f} on pool A, {tie[2]:.3f} against {tie[3]:.3f} on the '
            f'fresh pool), takes the '
            f'{dname(end["r", "matja"]["design"])}, '
            f'{100 * (end["r", "matja"]["W"] / end["r", "es"]["W"] - 1):.0f}% wider at the end: a greedy path taken on '
            f'a tie, not a wrong criterion. For the inflow all three choose the {dname(end["qL", "es"]["design"])}. For '
            f'$\\kappa$ the criteria part: the raw ensemble chooses the {dname(end["kappa", "es"]["design"])} and claims '
            f'{end["kappa", "es"]["E"]:.3f}, against {end["kappa", "es"]["X"]:.3f} exact and {end["kappa", "es"]["W"]:.3f} '
            f'guaranteed; MATJA-GO chooses the {dname(end["kappa", "matja"]["design"])} and guarantees '
            f'{end["kappa", "matja"]["W"]:.3f}. After two loggers the guaranteed width of $\\kappa$ stops falling '
            f'({rng_(list(kap2.values()))} at two, {rng_([end["kappa", c]["W"] for c in ("es", "oracle", "matja")])} at '
            f'three) while the exact posterior is {end["kappa", "oracle"]["X"]:.3f}: the reconstructor, not the data, '
            f'limits $\\kappa$, and the next resource belongs to a larger ensemble (T8), not to a third logger.'))
    A(('img', 'paths', 17.0))
    A(('cap', 'Figure {{paths}}. T7: guaranteed 90% half-width on the fresh pool against the number of instruments chosen '
              'by each criterion (markers offset sideways where they coincide), and the half-width the raw ensemble '
              'claims for its own design (dashed). For $\\kappa$ the claim falls tenfold while nothing more can be '
              'guaranteed.'))
    t7 = []
    crn = dict(es='raw ensemble', oracle='exact posterior', matja='MATJA-GO')
    gl = dict(r='recharge r (mm/d)', qL='inflow qL (m²/d)', kappa='coefficient κ')
    for g in G3:
        for cr in ('es', 'oracle', 'matja'):
            e_ = end[g, cr]
            t7.append([gl[g] if cr == 'es' else '', crn[cr], dname(e_['design']), f'{e_["E"]:.3f}', f'{e_["X"]:.3f}',
                       f'{e_["W"]:.3f}', f'{e_["risk"]:.3f} / {e_["cover"]:.2f}'])
    A(('cap', 'Table {{t7}}. T7: the design each criterion chooses after three steps, and on the fresh pool its raw-'
              'ensemble half-width, exact half-width, guaranteed half-width, and the achieved share of weeks outside / '
              'whole-function coverage (targets ≤ 0.10 / ≥ 0.90).'))
    A(('table', ['Goal', 'Criterion', 'Design after 3 steps', 'Ensemble', 'Exact', 'Guaranteed', 'Risk / coverage'], t7,
       [2.3, 2.2, 4.0, 1.9, 1.4, 2.5, 2.7], 9))
    A(('p', f'**T8: the exact law of the spurious value.** Figure {{{{spur}}}} and Table {{{{t8}}}}. The tide gauge is '
            f'added to the rain with ensembles of {", ".join(str(n) for n in Ns[:-1])} and {Ns[-1]} members. The spread '
            f'factors of all three goals lie on $1-\\delta_N$ to within {spr_dev:.3f}, the error factors on '
            f'$1+\\varepsilon_N$ to within {100 * err_dev:.0f}% (the error is estimated from 300 aquifers and is '
            f'noisier), and the first-order value $d_s/(N-1)$ is close for $N\\ge128$. The damage falls like $1/N$ but '
            f'does not vanish: with {Ns[-1]} members the guaranteed band still widens by '
            f'{rng_([100 * (v - 1) for v in meas(512, "W")], 0)}%.'))
    A(('img', 'spur', 17.0))
    A(('cap', 'Figure {{spur}}. T8: a worthless tide gauge added to the rain. Left: spread and error variance factors '
              'against the ensemble size, with the exact factors $1-\\delta_N$ and $1+\\varepsilon_N$ of Proposition M3 '
              '(lines). Right: the half-width factors of the raw ensemble and of the guaranteed band; the exact posterior '
              'does not change.'))
    t8 = []
    for n in Ns:
        r_ = sz[n]
        t8.append([str(n), f'{r_["first_order"]:.3f}', f'{r_["delta"]:.3f}', rng_(meas(n, 'spr')), f'{r_["eps"]:.3f}',
                   rng_(meas(n, 'err'), 2), f'{r_["pred_es"]:.3f} / {rng_(meas(n, "es"))}',
                   f'{r_["pred_matja"]:.2f} / {rng_(meas(n, "W"), 2)}'])
    A(('cap', 'Table {{t8}}. T8: first-order value $d_s/(N-1)$, exact $\\delta_N$ and the measured spread-variance factor '
              '(range over the three goals); exact $\\varepsilon_N$ and the measured error-variance factor; predicted / '
              'measured half-width factors of the raw ensemble and of the guaranteed band.'))
    A(('table', ['N', 'ds/(N−1)', 'δN', 'Spread factor', 'εN', 'Error factor', 'Ensemble hw', 'Guaranteed hw'], t8,
       [1.2, 1.9, 1.6, 2.4, 1.6, 2.3, 3.0, 3.0], 9))
    A(('h2', '4.4 What to measure first when only the rain is known'))
    A(('b', f'**For the recharge and κ:** one logger in the middle of the aquifer (2.0 km here) removes '
            f'{-100 * (S["L3"]["r"]["halfwidth"] / base["r"]["halfwidth"] - 1):.0f}% of the guaranteed half-width of the '
            f'recharge and {-100 * (S["L3"]["kappa"]["halfwidth"] / base["kappa"]["halfwidth"] - 1):.0f}% of that of '
            f'$\\kappa$; a second logger far from it halves the recharge band again.'))
    A(('b', f'**For the inland inflow:** the logger nearest the inland boundary first '
            f'({-100 * (S["L7"]["qL"]["halfwidth"] / base["qL"]["halfwidth"] - 1):.0f}% of the half-width), then one at '
            f'about two thirds of the way inland; two such loggers cut it to '
            f'{fr["L5+L7"]["qL"]["halfwidth"] / base["qL"]["halfwidth"] * 100:.0f}% of the rain-only value.'))
    A(('b', '**For the sea level or the toe:** a tide gauge, or land motion plus altimetry (C3, C5). For anything else a '
            'tide gauge is worthless with rain only and harmful to an ensemble that does not calibrate (T6).'))
    A(('b', '**For dispersion:** a deep conductivity or chloride profile; no head logger or tide gauge informs it (review '
            'I, Proposition 6).'))
    A(('b', '**Beyond two loggers for κ:** enlarge the ensemble or localise it before buying a third logger (T7, '
            'T8); and always recalibrate the chosen design on fresh simulated aquifers before its band is reported '
            '(Proposition M1).'))
    # ------------------------------------------------------------------------------------------- 5 synthesis
    A(('h', '5. Synthesis: forty papers in one procedure'))
    A(('p', 'Reviews I and II together give forty papers from the four institutions. Review I built the guarantee; this '
            'review adds the choice of what to measure and the forcing data that make the prior realistic. The '
            'procedure of review I keeps its eight steps; this is what the new papers and MATJA-GO change in each.'))
    A(('p', '**Step 1, the prior from the rain.** Generate the recharge of the simulated aquifers with soil physics '
            '(ClimaLand, C4) or a satellite-trained emulator (M2), with a deficit threshold for dry years (B1); make the '
            'rain itself random when it comes from a coarse product (O5); write the sea boundary as a relative sea level '
            'with land motion (C3); draw the initial interface from a sea-level history (O1); give dispersion a '
            'velocity- and scale-dependent law (M5). Rain alone does not fix the response of a groundwater-dominated '
            f'system, as the failure of rainfall–runoff learners in such catchments shows ({L("S9", "S9")}).'))
    A(('p', '**Steps 2 and 3, few unknowns, fast inversion.** Zones from airborne data reduce the fields to a few '
            'parameters (B4); a hard-constrained surrogate keeps the salt mass exact (B5); the closed-form toe of C1 is '
            f'the cheapest emulator; ensemble Kalman inversion stays the workhorse ({L("S6", "S6")}, {L("S7", "S7")}), '
            'with the equifinality of O4 as a warning that a good fit does not mean a narrow band.'))
    A(('p', '**Steps 4 to 7, guarantee and check.** Calibrate on simulated aquifers (review I, anchors A1 and A2), '
            'because expert and ensemble intervals are too narrow (M4, T7); test landward gradients with a guaranteed '
            'sign test (B2); treat a drift of land motion or a change of boundary type (C1, C3) as a prior shift for '
            'the field check of review I.'))
    A(('p', f'**Step 8, the next measurement: MATJA-GO.** Rank loggers, tide gauges, land motion, soil moisture, '
            f'handpumps (O3) and existing wells (B3) by the guaranteed width they remove; compute the price rule '
            f'[[price]] before buying; choose on one pool and recalibrate on another (Proposition M1). When the model '
            f'itself chooses where to sample, conformal validity under the feedback shift ({L("S5", "S5")}) is the '
            f'route to keep the guarantee without a fresh pool; for several goals at once, Learn-then-Test '
            f'({L("S4", "S4")}); for a guarantee per calibration set, the risk-controlling sets of {L("S3", "S3")}.'))
    A(('p', '**For Fushë-Kuqe.** The site has rain, a few heads and a handful of chloride facts. The order that follows '
            'from Section 4.4 is: one logger mid-plain for recharge and $\\kappa$; one near the inland boundary for the '
            'inflow; a land-motion check of the coastal datum with Sentinel-1 (C3) before any tide gauge; and a deep '
            'conductivity profile across the transition zone for dispersion. The exact sites need the Fushë-Kuqe test '
            'bed in place of the 5 km section: ==to be run on the site geometry==.'))
    # ------------------------------------------------------------------------------------------- 6 limitations
    A(('h', '6. Limitations'))
    A(('b', 'Every card is partly verified: landing pages were reached through search results only and no full text was '
            'read; where author lists or volumes were not confirmed, the card says so.'))
    A(('b', 'The tests use a linear one-dimensional test bed with weekly steps; the exact posterior used as oracle is not '
            'available in the field, but MATJA-GO does not need it.'))
    A(('b', 'Proposition M3 is exact for an instrument independent of the goal with no other data; with data already in '
            'hand the batch update is not the sequential one, and Remark M3 is a first-order rule checked on 36 pairs, '
            'not a theorem.'))
    A(('b', 'The guarantees are marginal under the physical prior given the rain, as in review I; a wrong prior is '
            'caught only by the field check, and not always.'))
    A(('b', 'The greedy choice can follow a tie down a slightly worse branch (T7, recharge); a look-ahead of two steps '
            'or keeping near-ties would remove that at a higher cost.'))
    return B
