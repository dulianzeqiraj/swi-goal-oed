"""Text of the sixth state-of-the-art review (English). blocks(AJ, GE) returns the block list; every number comes from
res/dyshemeja.json. Conventions: $inline math$, **bold**, *italic*, ==yellow placeholder==, [text](url) hyperlink,
[[key]] equation number, {{key}} figure or table number."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(1, os.path.join(HERE, '..', 'matja_go'))
sys.path.insert(2, os.path.join(HERE, '..', 'reshja_go'))
sys.path.insert(3, os.path.join(HERE, '..', 'ankora_go'))
sys.path.insert(4, os.path.join(HERE, '..', 'prirja_go'))
from cards_dyshemeja import CARDS, INST_ORDER, SOTA_ROWS  # noqa: E402
import cards_gar  # noqa: E402
import cards_matja  # noqa: E402
import cards_reshja  # noqa: E402
import cards_ankora  # noqa: E402
import cards_prirja  # noqa: E402

ANCHORS = [
    dict(key='A1', text='Angelopoulos, A. N., Bates, S., Fisch, A., Lei, L., & Schuster, T. (2024). Conformal risk '
                        'control. The Twelfth International Conference on Learning Representations (ICLR 2024). '
                        'arXiv:2208.02814 (PDF provided by the user).',
         url='https://arxiv.org/abs/2208.02814'),
    dict(key='A2', text='Tibshirani, R. (2023). Conformal prediction. Lecture notes, Advanced Topics in Statistical '
                        'Learning, Spring 2023, University of California, Berkeley (PDF provided by the user).',
         url='https://www.stat.berkeley.edu/~ryantibs/statlearn-s23/'),
]

SYN = []

OTHER = [
    dict(key='D1', text='Zeqiraj, D. (2026). Inputs, dispersion and boundary conditions from rain alone; GARANCIA-GO '
                        '("review I"), docs/literature/ in this repository.', url=None),
    dict(key='D2', text='Zeqiraj, D. (2026). State of the art II; MATJA-GO, the guaranteed value of a measurement '
                        '("review II"), docs/literature/ in this repository.', url=None),
    dict(key='D3', text='Zeqiraj, D. (2026). State of the art III: when the rain itself is uncertain; RESHJA-GO '
                        '("review III"), docs/literature/ in this repository.', url=None),
    dict(key='D4', text='Zeqiraj, D. (2026). State of the art IV: when the simulator is wrong; ANKORA-GO ("review IV"), '
                        'docs/literature/ in this repository (Proposition A3 corrected on 5 November 2026).', url=None),
    dict(key='D5', text='Zeqiraj, D. (2026). State of the art V: when the world drifts; PRIRJA-GO ("review V"), '
                        'docs/literature/ in this repository.', url=None),
    dict(key='D6', text='Internal documents of the project: RINDËRTIMI-GO (test bed, ensemble smoother with the exact '
                        'solver, exact posterior); the code of this review in experiments/dyshemeja_go/.', url=None),
]


def card_ref(c):
    return dict(key=c['id'], text=f"{c['authors']} ({c['year']}). {c['title']}. {c['venue']}.", url=c['links'][0][1])


def all_refs():
    return ANCHORS + [card_ref(c) for c in CARDS] + SYN + OTHER


def L(key, label=None):
    for r in all_refs():
        if r['key'] == key:
            return f"[{label or key}]({r['url']})" if r['url'] else (label or key)
    raise KeyError(key)


def rng_(xs, d=2):
    a, b = f'{min(xs):.{d}f}', f'{max(xs):.{d}f}'
    return a if a == b else f'{a}–{b}'


G4 = ('r', 'qL', 'eta', 'kappa')
GL = dict(r='recharge r', qL='inflow qL', eta='sea level η', kappa='coefficient κ')
STEPS = (('prior', 'prior from rain'), ('emulate', 'emulate'), ('invert', 'invert'), ('guarantee', 'guarantee'),
         ('check', 'field check'), ('design', 'design, operate'))


def blocks(AJ, GE):
    R = AJ['laws']
    N = R['none']
    DS = AJ['designs']

    def ratio(Rg, key):
        return Rg[key]['halfwidth'] / Rg['floor']['halfwidth']
    shape = [N[g]['exact_z']['halfwidth'] / N[g]['floor']['halfwidth'] for g in G4]
    recon = [N[g]['ens_star']['halfwidth'] / N[g]['exact_z']['halfwidth'] for g in G4]
    slack20 = [N[g]['m20']['halfwidth'] / N[g]['ens_star']['halfwidth'] for g in G4]
    slack_s = [N[g]['sims']['halfwidth'] / N[g]['ens_star']['halfwidth'] for g in G4]
    m20_none = [ratio(N[g], 'm20') for g in G4]
    sims_none = [ratio(N[g], 'sims') for g in G4]
    central = [ratio(N[g], 'central') for g in G4]
    T_none = [ratio(N[g], 'exactT_m20') for g in G4]
    Tstar_none = [ratio(N[g], 'exactT_star') for g in G4]
    d_m20 = [ratio(R['delay'][g], 'm20') for g in G4]
    d_P = [ratio(R['delay'][g], 'exactP_m20') for g in G4]

    def rr_(law, key):
        return [ratio(R[law][g], key) for g in G4]
    d_T = [ratio(R['delay'][g], 'exactT_m20') for g in G4]
    d_Ts = [R['delay'][g]['exactT_sims']['risk_rb'] for g in G4]
    d_sims = [R['delay'][g]['sims']['risk_rb'] for g in G4]
    p_m20 = [ratio(R['params'][g], 'm20') for g in G4]
    p_T = [ratio(R['params'][g], 'exactT_m20') for g in G4]
    p_Ts = [R['params'][g]['exactT_sims']['risk_rb'] for g in G4]
    anc_risk = [R[s][g]['m20']['risk'] for s in R for g in G4]
    T_risk = [R[s][g]['exactT_m20']['risk'] for s in R for g in G4]
    CAL = ('sims', 'exactP_sims', 'exactT_sims', 'm10', 'm20', 'm40', 'exactP_m20', 'exactT_m20')

    def rk(v):
        return v.get('risk_rb', v.get('risk'))
    below = [(s, g, b) for s in R for g in G4 for b in CAL if R[s][g][b]['halfwidth'] < R[s][g]['floor']['halfwidth']]
    below_bad = all(rk(R[s][g][b]) > 0.105 for s, g, b in below)
    p_bad = [g for g in G4 if R['params'][g]['exactT_sims']['risk_rb'] > 0.105]
    names = list(DS.keys())
    rem = {g: 1 - DS['4 loggers'][g]['floor']['halfwidth'] / DS['rain only'][g]['floor']['halfwidth'] for g in G4}
    rem8 = {g: 1 - DS['8 loggers'][g]['floor']['halfwidth'] / DS['rain only'][g]['floor']['halfwidth'] for g in G4}
    remg = {g: 1 - DS['4 loggers + gauge'][g]['floor']['halfwidth'] / DS['rain only'][g]['floor']['halfwidth']
            for g in G4}
    NEST = (('rain only', '1 logger'), ('1 logger', '2 loggers'), ('2 loggers', '8 loggers'), ('rain only', '4 loggers'),
            ('4 loggers', '8 loggers'), ('4 loggers', '4 loggers + gauge'))
    mono = all(DS[b][g]['floor']['halfwidth'] <= DS[a][g]['floor']['halfwidth'] * 1.01 for a, b in NEST for g in G4)
    wider = [(a, b, g) for a, b in NEST for g in G4 if DS[b][g]['m20']['halfwidth'] > DS[a][g]['m20']['halfwidth']]
    d_ratio = [DS[n][g]['m20']['halfwidth'] / DS[n][g]['floor']['halfwidth'] for n in names for g in G4]
    B = []
    A = B.append
    A(('title', 'State of the art VI: how narrow can a guarantee be'))
    A(('subtitle', 'Twenty more papers from Oxford, Caltech, Berkeley and MIT (2020–2026) with theorem-level results on '
                   'inverse problems, the limits of uncertainty quantification, information and design, and transport; '
                   'the state of the art and the step beyond it; and DYSHEMEJA-GO, the floor below which no valid band '
                   'can go, and how close the bands of reviews I–V come to it'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation · companion to reviews '
                 'I–V (GARANCIA-GO, MATJA-GO, RESHJA-GO, ANKORA-GO, PRIRJA-GO)'))
    # ------------------------------------------------------------------------------------------- 1 outcome
    A(('h', '1. Outcome'))
    A(('bbox', [
        '**Twenty new papers, five per institution, 2020–2026, each with links and its main theorem** (Section 3, '
        'Figure {{map}}). None was a card of reviews I–V or of the earlier reviews. This batch is the most '
        'mathematical of the series: stability and rates for inverse problems, optimality and impossibility results '
        'for uncertainty quantification, information bounds for design, and rigorous transport theory. Each card gives '
        'the theorem, the state of the art it sets, what it cannot yet do for us, three lessons and an innovation step.',
        '**State of the art and beyond, for the proposal** (Section 2, Table {{sotab}}), and a map of all one hundred '
        'and twenty papers of reviews I–VI on the steps of the procedure (Section 5, Table {{all}}).',
        '**Innovation: DYSHEMEJA-GO** (Section 4). Reviews I–V proved that their bands are valid; this review asks how '
        'narrow a valid band can be. Proposition F1: under the real law, no band of any kind — Bayesian, conformal, '
        'machine-learned — with an expected share of weeks outside at most α can be narrower on average than the '
        'Neyman–Pearson band of the exact posterior, $\\{x:p(x\\mid y)\\ge\\tau^*\\}$ with one threshold for all weeks. '
        'Proposition F2 splits the excess width of any calibrated band into band shape, reconstructor and calibration. '
        'Proposition F3: the floor can only fall as data are added, and with rain alone the floors of the sea level and '
        'the inflow are their prior widths. Proposition F4: replacing each truth by draws from its exact posterior '
        'leaves every expected risk unchanged and lowers the noise, which makes these comparisons precise.',
        f'**Test without shift** (T18). The 20-anchor band of review IV is {rng_(m20_none)} times the floor, the '
        f'simulation band of review I {rng_(sims_none)} times. The excess splits into band shape {rng_(shape)}, '
        f'ensemble reconstructor {rng_(recon)} and calibration on 20 anchors {rng_(slack20)}: the reconstructor, not '
        f'the guarantee, is the largest single cost.',
        f'**Test under shift** (T19). With a 35-day field delay the anchor band stays valid but is {rng_(d_m20)} times '
        f'the floor of the real law. The exact posterior under the simulator\'s law closes the gap for the inflow and '
        f'the sea level ({rng_(d_P[1:3])}) but not for the recharge and $\\kappa$ ({d_P[0]:.2f}, {d_P[3]:.2f}); the '
        f'exact posterior of an *enlarged* law in which the delay is unknown closes it for all four ({rng_(d_T)} times '
        f'the floor with 20 anchors), and its simulation calibration becomes valid again (risk {rng_(d_Ts, 3)}). Calibration on anchors keeps every band valid (risk {rng_(anc_risk, 3)} for the ensemble, '
        f'{rng_(T_risk, 3)} for the enlarged law).',
        f'**What the data can buy** (T20). Four loggers remove {100 * rem["eta"]:.0f}% of the sea-level floor width '
        f'and {100 * rem["qL"]:.0f}% of the inflow floor width left by the rain alone, {100 * rem["r"]:.0f}% for the '
        f'recharge and {100 * rem["kappa"]:.0f}% for $\\kappa$; a tide gauge takes the sea level to '
        f'{100 * remg["eta"]:.0f}%. The anchor band stays {rng_(d_ratio)} times the floor across six designs.']))
    # ------------------------------------------------------------------------------------------- 2 SOTA and beyond
    A(('h', '2. State of the art and the step beyond it'))
    A(('p', 'Reviews I–V (D1–D5) guarantee bands for the boundary conditions, the recharge coefficient and the inputs of '
            'a coastal aquifer when only the rain is known: calibrated on simulations, valued by the width a measurement '
            'removes, robust to an uncertain rain, made independent of the simulator by real anchors and kept valid '
            'years ahead under drift. A guarantee says that a band is not too narrow. It does not say that the band is '
            'not needlessly wide, and a reviewer can always ask whether a better method would have given a narrower '
            'band from the same data. This review answers that question with a floor.'))
    A(('p', '**Text for the proposal.** The mathematics of inverse problems and of uncertainty quantification now gives '
            'sharp results on what data can and cannot determine: stability and contraction rates for PDE inverse '
            'problems, optimality and impossibility theorems for prediction sets, and information bounds for '
            'experimental design (Section 3). These results are rarely turned into a number for a specific aquifer and '
            'design. The project goes beyond the state of the art by computing, for each boundary function and each '
            'candidate monitoring design, the narrowest band that any valid method could achieve (DYSHEMEJA-GO); by '
            'reporting the efficiency of its own guaranteed bands against that floor; and by attributing the excess '
            'width to the reconstructor, the band shape and the calibration, so that effort goes where it narrows the '
            'band most.'))
    A(('cap', 'Table {{sotab}}. State of the art (2020–2026) and the step beyond it. Card numbers refer to Section 3; T '
              'numbers to the tests of Section 4.'))
    A(('table', ['Topic', 'State of the art', 'Its limit for our problem', 'Our step beyond', 'Evidence'],
       SOTA_ROWS(AJ), [2.6, 3.9, 3.2, 3.8, 3.5], 9, False))
    # ------------------------------------------------------------------------------------------- 3 the papers
    A(('h', '3. The twenty papers'))
    A(('p', 'Five papers per institution, all from 2020–2026 (Figure {{map}}). The rules of the earlier reviews apply: '
            'direct use, a link to the institution at the time of publication (JPL for Caltech, Lawrence Berkeley '
            'National Laboratory for Berkeley), a state-of-the-art contribution and no paper that was a card before. '
            'This batch asks for a precise theorem; each card states it as the search results quote or closely '
            'paraphrase it, with its assumptions. Preprints are marked as such on their venue line.'))
    A(('p', '**Verification.** The hosts doi.org, arxiv.org, openreview.net and most publisher pages were blocked in this '
            'environment, so the landing pages were reached through search results that quote them, and every card but '
            'B3 is marked partly verified; where an author list, a volume or the exact wording of a theorem could not be '
            'confirmed, the card says so. Six of the twenty are preprints (O5, C1, C2, C3, B1, M4).'))
    names_i = dict(Oxford='University of Oxford', Caltech='California Institute of Technology (with JPL)',
                   Berkeley='University of California, Berkeley (with Lawrence Berkeley National Laboratory)',
                   MIT='Massachusetts Institute of Technology')
    fill = {'q1': f'{100 * DS["1 logger"]["qL"]["floor"]["halfwidth"] / DS["rain only"]["qL"]["floor"]["halfwidth"]:.0f}%',
            'q4': f'{100 * DS["4 loggers"]["qL"]["floor"]["halfwidth"] / DS["rain only"]["qL"]["floor"]["halfwidth"]:.0f}%',
            'krain': f'{DS["rain only"]["kappa"]["floor"]["halfwidth"]:.3f}',
            'eta4': f'{100 * rem["eta"]:.0f}%', 'etag': f'{100 * remg["eta"]:.0f}%'}

    def filled(c):
        c = dict(c)
        for k_, v_ in c.items():
            if isinstance(v_, str) and '<<' in v_:
                for key_, val_ in fill.items():
                    v_ = v_.replace(f'<<{key_}>>', val_)
                c[k_] = v_
        return c
    for j, inst in enumerate(INST_ORDER, start=1):
        A(('h2', f'3.{j} {names_i[inst]}'))
        first = True
        for c in CARDS:
            if c['inst'] == inst:
                A(('card', filled(c)))
                if first and inst == 'Oxford':
                    A(('img', 'map', 17.0))
                    A(('cap', 'Figure {{map}}. The twenty papers against the step of the procedure they serve and the '
                              'unknown they inform. Colour gives the institution; a filled square is a direct lesson, an '
                              'open square an indirect one.'))
                first = False
    # ------------------------------------------------------------------------------------------- 4 DYSHEMEJA-GO
    A(('h', '4. Innovation: DYSHEMEJA-GO, the floor of a guarantee'))
    A(('h2', '4.1 The floor and the set-up'))
    A(('p', 'Let $x_w$ ($w$ = 1, …, $T$ weeks) be a boundary function or the recharge coefficient, $y$ the data (the '
            'rain is known; the heads of the loggers are observed with noise), and $p_w(\\cdot\\mid y)$ the exact '
            'posterior density of $x_w$ under the real law $Q$. A *band procedure* is any rule that maps the data, and '
            'anything independent of the field case (simulations, anchors, randomisation), to sets $C_w$; its risk is '
            'the expected share of weeks outside, $R(C)=\\frac{1}{T}\\sum_w\\Pr_Q(x_w\\notin C_w)$. For a threshold '
            '$\\tau$ the Neyman–Pearson sets and their common threshold are'))
    A(('eq', 'np', ['A_w^{\\tau}(y)=\\{x:p_w(x\\mid y)\\ge\\tau\\},\\qquad\\tau^*:\\ \\frac{1}{T}\\sum_{w=1}^{T}'
                    '\\mathbb{E}_Q\\left[1-\\int_{A_w^{\\tau^*}(y)}p_w(x\\mid y)\\,dx\\right]=\\alpha,',
                    'W^*=\\frac{1}{2T}\\sum_{w=1}^{T}\\mathbb{E}_Q\\left|A_w^{\\tau^*}(y)\\right|.']))
    A(('p', '$W^*$ is the *floor*: a mean half-width. In the test bed of reviews I–V (D6; 32 cells, 64 weeks, four '
            'loggers at 0.25, 1.25, 2.75 and 4.25 km) the latent fields are Gaussian given $\\kappa$ and $\\kappa$ is '
            'log-normal, so the exact posterior is a mixture over a 241-point grid of $\\log\\kappa$ of Gaussians in the '
            'latent fields, and $p_w$ is a Gaussian mixture computed to machine precision (checked against the test '
            'bed\'s own solver: largest difference 10⁻¹¹). $\\tau^*$ is found on a grid of 4000 thresholds. For a band '
            '$m_w\\pm\\lambda s_w$ (centre $m$ and scale $s$ from a reconstructor) let $\\lambda^*_s$ be the multiplier at '
            'which its risk under $Q$ is exactly $\\alpha$, $\\lambda^*_\\sigma$ the same for the exact posterior mean '
            '$\\pm\\lambda\\sigma_w$, and $\\bar s$, $\\bar\\sigma$ the mean scales. For any calibrated $\\hat\\lambda$:'))
    A(('eq', 'dec', '\\frac{\\hat\\lambda\\bar s}{W^*}=\\underbrace{\\frac{\\hat\\lambda}{\\lambda^*_s}}_{\\text{'
                    'calibration}}\\cdot\\underbrace{\\frac{\\lambda^*_s\\bar s}{\\lambda^*_\\sigma\\bar\\sigma}}_{\\text{'
                    'reconstructor}}\\cdot\\underbrace{\\frac{\\lambda^*_\\sigma\\bar\\sigma}{W^*}}_{\\text{band shape}}.'))
    A(('p', f'Three reconstructors are compared: the ensemble smoother of reviews I–V (128 members, joint update of '
            f'$\\kappa$); the exact posterior under the simulator\'s law $P$ (*exact under P*); and the exact posterior '
            f'of an *enlarged law* in which the vadose delay is unknown too (log-uniform on 7–56 d, on a grid of seven '
            f'delays). Only the response to $\\kappa$ changes with the delay, so one factorisation of the data covariance '
            f'serves all delays. Each band is calibrated either on {AJ["n_sim"]} simulated aquifers or on 10, 20 or 40 '
            f'anchors ({AJ["reps"]} draws). Real laws: no shift, a 35-day field delay, and shifted parameters '
            f'($\\kappa$ median 0.25 instead of 0.35, recharge error and inflow departures 1.5 times larger), as in '
            f'review IV; {AJ["n_q"]} field cases each.'))
    A(('img', 'scheme', 17.0))
    A(('cap', 'Figure {{scheme}}. The floor in one field case: the exact posterior of the recharge in a well-observed '
              'and in a poorly observed week, the one threshold $\\tau^*$ of [[np]] (dashed), the floor sets (blue) and '
              'the central 90% intervals (grey). The floor spends coverage where it is cheap: the narrow posterior gets '
              'more than 90% of its mass, the wide one less.'))
    A(('h2', '4.2 Guarantees'))
    A(('prop', 'Proposition F1 (the floor of every valid band).',
            'For every band procedure $C$ with $R(C)\\le\\alpha$ under $Q$, $\\frac{1}{2T}\\sum_w\\mathbb{E}_Q|C_w|\\ge '
            'W^*$, with equality for the sets [[np]]. The floor depends only on $Q$, the design and $\\alpha$.'))
    A(('proof', 'Fix $y$ and $w$, write $p=p_w(\\cdot\\mid y)$ and $A^*=A_w^{\\tau^*}(y)$. For any set $C$, '
                '$\\int_C(\\tau^*-p)\\,dx\\ge\\int_{C\\cap A^*}(\\tau^*-p)\\,dx\\ge\\int_{A^*}(\\tau^*-p)\\,dx$, because '
                'the integrand is non-negative outside $A^*$ and non-positive on it. So $\\tau^*|C|-P(C\\mid y)\\ge'
                '\\tau^*|A^*|-P(A^*\\mid y)$. Anchors, simulations and randomisation are independent of the field truth '
                'given $y$, so the inequality holds for $C_w$ and can be averaged over them, over $y$ and over $w$: '
                '$\\tau^*\\,\\mathbb{E}|C|\\ge\\tau^*\\,\\mathbb{E}|A^*|+(1-R(C))-(1-\\alpha)\\ge\\tau^*\\,\\mathbb{E}|A^*|$. '))
    A(('prop', 'Proposition F2 (where the excess width comes from).',
            'The identity [[dec]] holds for every calibrated band. Its last factor is at least 1, and so is the product '
            'of its last two factors; the first measures the calibration and tends to 1 as the number of calibration '
            'cases grows.'))
    A(('proof', 'The exact-posterior band with $\\lambda^*_\\sigma$ and the reconstructor band with $\\lambda^*_s$ both '
                'have risk exactly $\\alpha$, so Proposition F1 applies to each. The first factor is a ratio of an '
                'empirical to a population quantile of the same scores.'))
    A(('prop', 'Proposition F3 (what data can and cannot buy).',
            '(i) Adding observations never raises the floor. (ii) With rain alone, the floors of the sea level and of '
            'the inland inflow equal their prior floors: no method, however clever, can narrow those bands without heads '
            'or a gauge. (iii) The floor of a design can be computed before any field data exist, from the law and the '
            'design alone.'))
    A(('proof', '(i) A procedure that ignores the extra observations is a valid procedure of the larger design, so the '
                'minimum over the larger class is no larger (a Blackwell-type comparison). (ii) In the test bed the rain '
                'enters only the recharge; without heads the posterior of the sea level and of the inflow is their '
                'prior. (iii) [[np]] involves only expectations under $Q$.'))
    A(('prop', 'Proposition F4 (Rao–Blackwellised risk).',
            'For any band $C$, $R(C)=\\frac{1}{T}\\sum_w\\mathbb{E}_Q[\\Pr_Q(x_w\\notin C_w\\mid y)]$. Replacing each '
            'field truth by draws from its exact posterior gives an unbiased estimate of $R(C)$ whose variance is no '
            'larger than that of the estimate from the truths.'))
    A(('proof', 'The first statement is the tower property. Averaging the indicator over posterior draws estimates the '
                'conditional probability without bias, and $\\mathrm{Var}(\\mathbb{E}[X\\mid y])\\le\\mathrm{Var}(X)$ '
                'for the indicator $X$ of a miss. All population multipliers $\\lambda^*$ below use 40 draws per week and '
                'field case.'))
    A(('box', ['**What is new.** (1) A computable floor for guaranteed bands of boundary conditions and of the recharge '
               'coefficient from rain and a few heads: the width that no valid method can beat (Propositions F1, F3). '
               '(2) An exact decomposition of the excess width of a calibrated band into band shape, reconstructor and '
               'calibration (Proposition F2), measured with Rao–Blackwellised risks (Proposition F4). (3) The test that '
               'shows where the width of the earlier bands goes, and that putting a structural unknown (the vadose '
               'delay) into the simulator brings a valid band close to the floor. To our knowledge none of these appears '
               'in the one hundred and twenty papers of reviews I–VI.']))
    # ------------------------------------------------------------------------------------------- 4.3 tests
    A(('h2', '4.3 Tests'))
    A(('p', f'**T18: the floor without shift.** Figure {{{{ladder}}}} and Table {{{{t18}}}}. The central 90% posterior '
            f'interval is {rng_(central)} times the floor: in this test bed the exact posterior is close to Gaussian '
            f'with a spread that varies little between weeks, so the band shape costs little ({rng_(shape)} for the '
            f'exact posterior mean $\\pm\\lambda\\sigma$). The ensemble reconstructor costs {rng_(recon)}: 128 members '
            f'estimate the posterior spread, and above all the spread of $\\kappa$, with error. Calibration costs '
            f'nothing with 300 simulations ({rng_(slack_s)}) and {rng_(slack20)} with 20 anchors. The enlarged law costs little '
            f'when the delay is in fact the simulator\'s ({rng_(Tstar_none)} times the floor with $\\lambda$ known, '
            f'{rng_(T_none)} with 20 anchors).'))
    A(('img', 'ladder', 17.0))
    A(('cap', 'Figure {{ladder}}. T18: half-width of each band divided by the floor $W^*$ of [[np]], without shift (real '
              'law = simulator\'s law), for the four goals. "λ known" means the population multiplier, computed with '
              'Rao–Blackwellised risk; the anchor and simulation bands are calibrated as in reviews I and IV.'))
    t18 = []
    keys = (('floor', 'Floor W*'), ('central', 'Central 90%'), ('exact_z', 'Exact, λ known'),
            ('exactT_star', 'Enlarged, λ known'), ('ens_star', 'Ensemble, λ known'), ('sims', 'Ensemble, 300 sims'),
            ('m40', 'Ensemble, 40 anchors'), ('m20', 'Ensemble, 20 anchors'), ('m10', 'Ensemble, 10 anchors'),
            ('exactT_m20', 'Enlarged, 20 anchors'))
    for key, lab in keys:
        row = [lab]
        for g in G4:
            v = N[g][key]['halfwidth']
            row.append(f'{v:.4f}' if key == 'floor' else f'{v / N[g]["floor"]["halfwidth"]:.2f}')
        t18.append(row)
    A(('cap', 'Table {{t18}}. T18: the floor (mean half-width; recharge mm/d, inflow m²/d, sea level m, κ dimensionless) '
              'and every band as a multiple of it, without shift.'))
    A(('table', ['Band', 'Recharge r', 'Inflow qL', 'Sea level η', 'Coefficient κ'], t18, [5.0, 3.0, 3.0, 3.0, 3.0], 9))
    A(('p', f'**T19: the floor under shift.** Figure {{{{shift}}}}. The floor is that of the real law: it knows the '
            f'35-day delay or the shifted parameters. Under the delay the ensemble band calibrated on anchors is valid '
            f'but {rng_(d_m20)} times the floor, because its reconstructor misplaces the timing of recharge. The exact '
            f'posterior under the simulator\'s law, calibrated on anchors, repairs the inflow and the sea level '
            f'({rng_(d_P[1:3])}) but not the recharge and $\\kappa$ ({d_P[0]:.2f} and {d_P[3]:.2f}): exact inference in '
            f'the wrong structure is still wrong. The enlarged law removes most of the gap ({rng_(d_T)}), and its '
            f'simulation calibration becomes valid again because the 35-day delay lies inside its prior (risk '
            f'{rng_(d_Ts, 3)}, against {rng_(d_sims, 2)} for the ensemble calibrated on simulations). Under shifted '
            f'parameters, which the enlarged law does not contain, its simulation calibration is not repaired (risk '
            f'{rng_(p_Ts, 3)}, above 0.10 for {len(p_bad)} of the 4 goals), while the anchor bands stay valid at '
            f'{rng_(p_m20)} (ensemble) and {rng_(p_T)} (enlarged law) times the floor; here the exact posterior under '
            f'the simulator\'s law is already close ({rng_(rr_("params", "exactP_m20"))}): a wrong prior costs little once '
            f'anchors recalibrate, a wrong structure costs a lot. '
            + (f'Every calibrated band narrower than the floor was invalid, as Proposition F1 requires ({len(below)} '
               f'cases' + (', all calibrated on simulations).' if all(b.endswith('sims') for _, _, b in below) else ').')
               if below and below_bad else
               'No calibrated band fell below the floor.')))
    A(('img', 'shift', 17.0))
    A(('cap', 'Figure {{shift}}. T19: half-width divided by the floor of the real law, under the 35-day delay (left) '
              'and shifted parameters (right). Filled markers have risk at most 0.10 (Rao–Blackwellised for the '
              'simulation calibrations); open markers are invalid bands.'))
    A(('p', f'**T20: what the data can buy at best.** Figure {{{{design}}}}. The floor falls as loggers are added, as '
            f'Proposition F3 requires{"" if mono else " (up to sampling noise)"}. With rain alone the sea-level and inflow '
            f'floors are the prior widths; four loggers remove {100 * rem["eta"]:.0f}% and {100 * rem["qL"]:.0f}% of '
            f'them, eight {100 * rem8["eta"]:.0f}% and {100 * rem8["qL"]:.0f}%, and a tide gauge with four loggers '
            f'{100 * remg["eta"]:.0f}% for the sea level. For the recharge and $\\kappa$, which the rain already informs '
            f'through the recharge coefficient, four loggers remove {100 * rem["r"]:.0f}% and {100 * rem["kappa"]:.0f}%. '
            f'The 20-anchor band follows the floor at {rng_(d_ratio)} times its width across the six designs, and the ratio '
            f'grows with the data, from {rng_([DS["rain only"][g]["m20"]["halfwidth"] / DS["rain only"][g]["floor"]["halfwidth"] for g in G4])} '
            f'with rain alone to {rng_([DS["8 loggers"][g]["m20"]["halfwidth"] / DS["8 loggers"][g]["floor"]["halfwidth"] for g in G4])} '
            f'with eight loggers: the more the data say, the more the ensemble leaves unused. The floor '
            f'never rose when observations were added (Proposition F3), but the guaranteed band did in {len(wider)} of '
            f'{len(NEST) * 4} nested comparisons: '
            + (f'with one logger at 2 km the sea-level band widened from {DS["rain only"]["eta"]["m20"]["halfwidth"]:.3f} '
               f'to {DS["1 logger"]["eta"]["m20"]["halfwidth"]:.3f} m while its floor fell from '
               f'{DS["rain only"]["eta"]["floor"]["halfwidth"]:.3f} to {DS["1 logger"]["eta"]["floor"]["halfwidth"]:.3f} m. '
               if any(a == 'rain only' and b == '1 logger' and g == 'eta' for a, b, g in wider) else '')
            + 'That is the negative guaranteed value of review II seen from the floor: the data carried a little '
              'information, but the reconstructor turned it into a worse-shaped band, and the floor shows that the loss '
              'is the method\'s, not the instrument\'s.'))
    A(('img', 'design', 17.0))
    A(('cap', 'Figure {{design}}. T20: the floor of six designs relative to rain alone (left), and the 20-anchor band '
              'divided by the floor (right; dotted: the enlarged law). No shift.'))
    A(('h2', '4.4 Using the floor at Fushë-Kuqe'))
    A(('b', '**Before buying an instrument:** compute the floor of each candidate design under the working law; an '
            'instrument that does not lower the floor cannot lower any guaranteed band (Proposition F3).'))
    A(('b', '**When reporting a band:** report its ratio to the floor. A ratio near 1 means the data are exhausted; a '
            'large ratio means the reconstructor or the model structure, not the data, limits the band (Proposition '
            'F2).'))
    A(('b', '**Where to invest:** in this test bed the structural unknown (the vadose delay) is worth more than more '
            'anchors or more ensemble members; for Fushë-Kuqe the candidate structural unknowns are the vadose delay, '
            'the inland-inflow regime and the rain bias, whose plausible ranges are ==to be set with the local '
            'hydrogeologists==.'))
    A(('b', '**Caveat:** the floor is computed under a working law; it is a design and diagnostic tool. The guarantee in '
            'the field still comes from the anchors (review IV) and the horizon matching (review V).'))
    # ------------------------------------------------------------------------------------------- 5 synthesis
    A(('h', '5. Synthesis: one hundred and twenty papers in one procedure'))
    A(('p', 'Table {{all}} places the hundred and twenty papers of reviews I–VI on the steps of the procedure. Card '
            'numbers carry the review: I-O1 is card O1 of review I, VI-C2 card C2 of this review. Review VI adds the '
            'measure of how good a guarantee is: its distance from the floor.'))
    rows = []
    sets = (('I', cards_gar.CARDS), ('II', cards_matja.CARDS), ('III', cards_reshja.CARDS),
            ('IV', cards_ankora.CARDS), ('V', cards_prirja.CARDS), ('VI', CARDS))
    for key, lab_ in STEPS:
        row = [lab_]
        for rv, cs in sets:
            ids = [c['id'] for c in cs if key in c['steps']]
            row.append(', '.join(ids) if ids else '–')
        rows.append(row)
    A(('cap', 'Table {{all}}. The one hundred and twenty papers of reviews I–VI against the steps of the procedure (card '
              'numbers of each review; a paper can serve several steps).'))
    A(('table', ['Step', 'I', 'II', 'III', 'IV', 'V', 'VI'], rows, [2.5, 2.45, 2.45, 2.45, 2.45, 2.45, 2.45], 8.6))
    A(('p', '**Order of work.** (1) Build the simulated aquifers from the rain, with the rain product\'s errors '
            '(RESHJA-GO), and with every structural unknown that can be named (here the vadose delay) as a random '
            'quantity of the law. (2) Compute the floor of each candidate design (DYSHEMEJA-GO) and choose instruments '
            'by guaranteed value (MATJA-GO). (3) Use the exact posterior where the model allows it, the ensemble where '
            'it does not. (4) Calibrate on real anchors (ANKORA-GO), horizon-matched when the law drifts (PRIRJA-GO). '
            '(5) Report the band, its ratio to the floor, and the simulation-calibrated band alongside (GARANCIA-GO).'))
    # ------------------------------------------------------------------------------------------- 6 limitations
    A(('h', '6. Limitations'))
    A(('b', 'Every card but B3 (whose proceedings PDF was read) is partly verified: landing pages, and the exact wording '
            'of the theorems, were reached through search results only.'))
    A(('b', 'The floor is that of the working law; under a law outside the model it is not known, and only the anchors '
            'protect the guarantee.'))
    A(('b', 'The floor is for the average risk over weeks and cases (marginal coverage). Floors for conditional '
            'coverage, week by week, are higher and are not computed here.'))
    A(('b', 'Dispersion does not enter the test bed of these reviews; the floor of a dispersivity or transition-zone '
            'band needs the transport model of review I and is left for the next step.'))
    A(('b', 'The tests use the linear one-dimensional test bed of reviews I–V, two shifts and six designs.'))
    return B
