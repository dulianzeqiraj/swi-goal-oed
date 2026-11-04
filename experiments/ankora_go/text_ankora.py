"""Text of the fourth state-of-the-art review (English). blocks(AJ, GE) returns the block list; every number comes from
res/ankora.json and from the results of review I. Conventions: $inline math$, **bold**, *italic*, ==yellow
placeholder==, [text](url) hyperlink, [[key]] equation number, {{key}} figure or table number."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(1, os.path.join(HERE, '..', 'matja_go'))
sys.path.insert(2, os.path.join(HERE, '..', 'reshja_go'))
from cards_ankora import CARDS, INST_ORDER, SOTA_ROWS  # noqa: E402
import cards_gar  # noqa: E402
import cards_matja  # noqa: E402
import cards_reshja  # noqa: E402

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
    dict(key='S1', text='Barber, R. F., Candès, E. J., Ramdas, A., & Tibshirani, R. J. (2023). Conformal prediction beyond '
                        'exchangeability. Annals of Statistics 51(2), 816–845.', url='https://doi.org/10.1214/23-AOS2276'),
    dict(key='S2', text='Bates, S., Angelopoulos, A., Lei, L., Malik, J., & Jordan, M. I. (2021). Distribution-free, '
                        'risk-controlling prediction sets. Journal of the ACM 68(6), Article 43, 1–34.',
         url='https://doi.org/10.1145/3478535'),
    dict(key='S3', text='Angelopoulos, A. N., Bates, S., Fannjiang, C., Jordan, M. I., & Zrnic, T. (2023). '
                        'Prediction-powered inference. Science 382(6671), 669–674.', url='https://doi.org/10.1126/science.adi6000'),
]

OTHER = [
    dict(key='D1', text='Zeqiraj, D. (2026). Inputs, dispersion and boundary conditions from rain alone; GARANCIA-GO '
                        '("review I"), docs/literature/ in this repository.', url=None),
    dict(key='D2', text='Zeqiraj, D. (2026). State of the art II; MATJA-GO, the guaranteed value of a measurement '
                        '("review II"), docs/literature/ in this repository.', url=None),
    dict(key='D3', text='Zeqiraj, D. (2026). State of the art III: when the rain itself is uncertain; RESHJA-GO '
                        '("review III"), docs/literature/ in this repository.', url=None),
    dict(key='D4', text='Internal documents of the project: RINDËRTIMI-GO (test bed, ensemble smoother with the exact '
                        'solver); the code of this review in experiments/ankora_go/.', url=None),
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


def rng_(xs, d=3):
    a, b = f'{min(xs):.{d}f}', f'{max(xs):.{d}f}'
    return a if a == b else f'{a}–{b}'


SCEN = (('none', 'no shift'), ('delay', 'vadose delay 35 d'), ('params', 'shifted parameters'),
        ('rainbias', 'rain bias'))
G4 = ('r', 'qL', 'eta', 'kappa')
GL = dict(r='recharge r', qL='inflow qL', eta='sea level η', kappa='coefficient κ')
STEPS = (('prior', 'prior from rain'), ('emulate', 'emulate'), ('invert', 'invert'), ('guarantee', 'guarantee'),
         ('check', 'field check'), ('design', 'design, operate'))


def blocks(AJ, GE):
    R = AJ['res']
    ma, mc = AJ['min_anchors']['expectation'], AJ['min_anchors']['certificate']
    sims_shift = [R[s][g]['sims']['risk'] for s in ('delay', 'params', 'rainbias') for g in G4]
    sims_none = [R['none'][g]['sims']['risk'] for g in G4]
    anc = {m: [R[s][g][f'm{m}']['anchors']['risk'] for s, _ in SCEN for g in G4] for m in AJ['ms']}
    wid = {m: {s: [R[s][g][f'm{m}']['anchors']['halfwidth'] / R[s][g]['sims']['halfwidth'] for g in G4]
               for s, _ in SCEN} for m in AJ['ms']}
    plus = [R[s][g]['m20']['anchors_plus']['halfwidth'] / R[s][g]['m20']['anchors']['halfwidth'] - 1
            for s, _ in SCEN for g in ('r', 'qL', 'eta')]
    mix_none = [R['none'][g]['m20']['mix']['0.5']['risk'] for g in G4]
    mix_none_w = [R['none'][g]['m20']['mix']['0.5']['halfwidth'] / R['none'][g]['m20']['anchors']['halfwidth'] - 1
                  for g in G4]
    mix_shift = [R[s][g]['m20']['mix']['0.5']['risk'] for s in ('delay', 'params', 'rainbias') for g in G4]
    B = []
    A = B.append
    A(('title', 'State of the art IV: when the simulator is wrong'))
    A(('subtitle', 'Twenty more papers from Oxford, Caltech, Berkeley and MIT (2020–2026) on transferring knowledge between '
                   'sites, inference under shift, mixing and coastal boundaries; the state of the art and the step beyond '
                   'it; and ANKORA-GO, guarantees made independent of the simulator by a few real anchors'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation · companion to reviews '
                 'I–III (GARANCIA-GO, MATJA-GO, RESHJA-GO)'))
    # ------------------------------------------------------------------------------------------- 1 outcome
    A(('h', '1. Outcome'))
    A(('bbox', [
        '**Twenty new papers, five per institution, 2020–2026, each with links** (Section 3, Figure {{map}}). None was a '
        'card of reviews I–III or of the earlier reviews. They address the weak point the three earlier reviews share: '
        'every guarantee was calibrated on simulated aquifers and holds only if the simulator\'s prior is the real law. '
        'Each card gives the state of the art the paper sets, what it cannot yet do for us, three lessons and an '
        'innovation step.',
        '**State of the art and beyond, for the proposal** (Section 2, Table {{sotab}}), and a map of all eighty papers of '
        'reviews I–IV on the steps of the procedure (Section 5, Table {{eighty}}).',
        f'**Innovation: ANKORA-GO** (Section 4). A few *anchors*, sites or periods where a boundary function was actually '
        f'measured, calibrate the band instead of the simulations. Proposition A1: the guarantee then holds for whatever '
        f'the real law is. Proposition A2: at least {ma} anchors are needed for a guarantee on average and {mc} for a '
        f'certificate at 90% confidence, whatever method is used. Proposition A3: mixing simulations and anchors narrows '
        f'the band at the price of a bias proportional to the weight put on the simulations.',
        f'**Test: the simulation-calibrated guarantee breaks under every realistic shift** (T12, 600 field cases per '
        f'law). With a field vadose delay of 35 d, shifted parameters or an unrecognised rain bias, the share of weeks '
        f'outside the 90% bands is {rng_(sims_shift, 2)} instead of at most 0.10, up to {max(sims_shift):.2f} for '
        f'$\\kappa$. Calibrated on 20 real anchors it is {rng_(anc[20], 3)}, and on 40 anchors {rng_(anc[40], 3)}, '
        f'under all four laws.',
        f'**The price** (T13). Without shift, 20 anchors widen the band by {100 * (np.mean(wid[20]["none"]) - 1):.0f}% on '
        f'average against the simulations (40 anchors: {100 * (np.mean(wid[40]["none"]) - 1):.0f}%); under shift the '
        f'band widens by as much as the real errors demand, up to {max(max(v) for v in wid[20].values()):.1f} times for '
        f'$\\kappa$ under a rain bias. Ten anchors are valid but very conservative.',
        f'**Mixing** (T14). Putting half of the calibration weight on simulations keeps the guarantee when there is no '
        f'shift (risk {rng_(mix_none)}) and narrows the band by {-100 * np.mean(mix_none_w):.0f}%, but breaks it under '
        f'shift (risk {rng_(mix_shift, 2)}, above 0.10 in {sum(v > 0.1 for v in mix_shift)} of {len(mix_shift)} cases): '
        f'the anchors cannot tell which case they are in, so the safe rule is to '
        f'calibrate on anchors alone and use the simulations to choose instruments and to build the score.']))
    # ------------------------------------------------------------------------------------------- 2 SOTA and beyond
    A(('h', '2. State of the art and the step beyond it'))
    A(('p', 'Reviews I–III (D1–D3) guarantee bands for boundary conditions, choose instruments and handle an uncertain '
            'rain, always by calibrating on aquifers simulated from a prior. Their common limit is stated in each of '
            'them: the guarantee is marginal under that prior, and a wrong prior is detected by the field check only '
            'partly (review I, Proposition 5). This review asks how real data with known truth, which exist but are '
            'scarce, can make the guarantee hold for the real world.'))
    A(('p', '**Text for the proposal.** Hydrological and hydrogeological knowledge is increasingly transferred between '
            'sites through large-sample datasets, regionalisation and machine learning trained on many catchments, and '
            'simulation-based inference is calibrated on synthetic data (Section 3). Such transfers are judged by average '
            'skill, and their uncertainty statements hold only if the training sites, or the simulator, resemble the '
            'target. The project goes beyond the state of the art by calibrating its guarantees on a few real *anchors*, '
            'sites or periods where a boundary function was measured, so that they hold whatever the real law is '
            '(ANKORA-GO); by stating how many anchors any method needs (9 for an average guarantee, 22 for a certificate '
            'at 90% confidence); and by quantifying, with tests, what simulations still contribute and what mixing them '
            'with anchors costs.'))
    A(('cap', 'Table {{sotab}}. State of the art (2020–2026) and the step beyond it. Card numbers refer to Section 3; T '
              'numbers to the tests of Section 4.'))
    A(('table', ['Topic', 'State of the art', 'Its limit for our problem', 'Our step beyond', 'Evidence'],
       SOTA_ROWS(AJ), [2.6, 3.9, 3.2, 3.8, 3.5], 9, False))
    # ------------------------------------------------------------------------------------------- 3 the papers
    A(('h', '3. The twenty papers'))
    A(('p', 'Five papers per institution, all published in 2020–2026 (Figure {{map}}). The rules of the earlier reviews '
            'apply: direct use, a link to the institution at the time of publication (JPL for Caltech, Lawrence Berkeley '
            'National Laboratory for Berkeley), a state-of-the-art contribution, and no paper that was a card before. This '
            'batch gives priority to transferring knowledge between sites and to inference under shift, then to mixing '
            'and coastal boundaries.'))
    A(('p', '**Verification.** The hosts doi.org, arxiv.org, openreview.net and most publisher pages were blocked in this '
            'environment, so every landing page was reached through search results that quote it, and every card is '
            'marked partly verified; where an author list or a volume could not be confirmed, the card says so.'))
    names = dict(Oxford='University of Oxford', Caltech='California Institute of Technology (with JPL)',
                 Berkeley='University of California, Berkeley (with Lawrence Berkeley National Laboratory)',
                 MIT='Massachusetts Institute of Technology')
    for j, inst in enumerate(INST_ORDER, start=1):
        A(('h2', f'3.{j} {names[inst]}'))
        first = True
        for c in CARDS:
            if c['inst'] == inst:
                A(('card', c))
                if first and inst == 'Oxford':
                    A(('img', 'map', 17.0))
                    A(('cap', 'Figure {{map}}. The twenty papers against the step of the procedure they serve and the '
                              'unknown they inform. Colour gives the institution; a filled square is a direct lesson, an '
                              'open square an indirect one.'))
                first = False
    # ------------------------------------------------------------------------------------------- 4 ANKORA-GO
    A(('h', '4. Innovation: ANKORA-GO, guarantees that do not depend on the simulator'))
    A(('img', 'scheme', 17.0))
    A(('cap', 'Figure {{scheme}}. ANKORA-GO. Simulated aquifers come from the simulator\'s law $P$; anchors and the field '
              'come from the real law $Q$. Calibrating on the anchors makes the guarantee hold for any $Q$; mixing '
              'simulations in narrows the band but adds a bias proportional to their share $\\psi$ of the weight.'))
    A(('h2', '4.1 Anchors and the set-up'))
    A(('p', 'An **anchor** is a case in which the boundary function of interest was measured while the usual data were '
            'collected: a neighbouring coastal aquifer with a tide gauge and a dense logger network, a period in which a '
            'temporary tide gauge, lysimeter or stream gauge was operated, or a monitored benchmark site. The reconstructor '
            'is run on an anchor exactly as on the field (rain and the usual heads), and its error against the measured '
            'truth is scored. Anchors are few and costly; simulated aquifers are many and free, but come from the '
            'simulator\'s law $P$, while anchors and field come from the real law $Q$.'))
    A(('p', 'The test bed is that of reviews I–III (D4): 32 cells, 64 weekly steps, the ensemble smoother with the exact '
            'solver (128 members) and four loggers (0.25, 1.25, 2.75, 4.25 km). Four real laws $Q$ are compared: no shift; '
            'a vadose delay of 35 d in the field against 14 d in the simulator; shifted parameters (recharge coefficient '
            'median 0.25 instead of 0.35, recharge error and inland-inflow departures 1.5 times larger); and the rain bias '
            'of review III (a product with a 20% record bias and daily errors, treated as exact). With $L_j(\\lambda)$ the '
            'share of the 64 weeks of anchor $j$ outside the band $m\\pm\\lambda s$, the anchor calibration is'))
    A(('eq', 'anc', '\\hat\\lambda_A=\\inf\\left\\{\\lambda:\\frac{1}{m+1}\\left(\\sum_{j=1}^{m}L_j(\\lambda)+1\\right)\\le'
                    '\\alpha\\right\\}'))
    A(('p', 'and the mixed calibration gives weight $w$ to each of $n$ simulated aquifers:'))
    A(('eq', 'mix', ['\\hat\\lambda_\\psi=\\inf\\left\\{\\lambda:\\frac{w\\sum_{i=1}^{n}L_i^{sim}(\\lambda)+\\sum_{j=1}^{m}'
                     'L_j(\\lambda)+1}{wn+m+1}\\le\\alpha\\right\\}\\text{, with }\\psi=\\frac{wn}{wn+m+1}.']))
    A(('p', f'$\\psi$ = 0 is [[anc]], and $\\psi\\to1$ is the simulation calibration of review I. All calibrations are '
            f'computed exactly from the pooled scores (weighted quantiles, no grid). Each result averages {AJ["reps"]} '
            f'random draws of $m$ anchors from {AJ["n_q"]} field cases of each law; the risk is measured on the remaining '
            f'cases.'))
    A(('h2', '4.2 Guarantees'))
    A(('prop', 'Proposition A1 (anchors make the guarantee independent of the simulator).',
            'Let the anchors and the field case be exchangeable draws from the real law $Q$, whatever it is, and let the '
            'reconstructor and the score be fixed independently of the anchors (they may be designed, tuned or chosen '
            'with simulations from any law $P$). Then the band with $\\hat\\lambda_A$ of [[anc]] satisfies '
            '$\\mathbb{E}_Q[L_{field}(\\hat\\lambda_A)]\\le\\alpha$, and, for continuous scores, '
            '$\\mathbb{E}_Q[L_{field}(\\hat\\lambda_A)]\\ge\\alpha-2/(m+1)$.'))
    A(('proof', 'The losses of the $m+1$ cases are exchangeable under $Q$ and bounded by $B=1$, so Theorems 1 and 2 of '
                'conformal risk control (anchor A1) apply with $n=m$. The simulations enter only through the fixed map '
                'from data to band, which leaves exchangeability intact.'))
    A(('prop', 'Proposition A2 (how many anchors any method needs).',
            f'(i) [[anc]] has a finite solution for every law only if $m\\ge(1-\\alpha)/\\alpha$, that is {ma} anchors at '
            f'$\\alpha$ = 0.10. (ii) No procedure that is valid for every real law can certify $R_Q(\\lambda)\\le\\alpha$ '
            f'with confidence $1-\\delta$ from fewer than $\\log\\delta/\\log(1-\\alpha)$ anchors, that is {mc} at '
            f'$\\alpha=\\delta$ = 0.10.'))
    A(('proof', '(i) Since $L_j\\ge0$, the left side of [[anc]] is at least $1/(m+1)$ for every $\\lambda$, so it can '
                'reach $\\alpha$ only if $m+1\\ge1/\\alpha$. (ii) Take a law '
                'whose loss is 0 or 1, with $\\Pr(L=1)=\\alpha+\\epsilon$: all $m$ anchors show $L=0$ with probability '
                '$(1-\\alpha-\\epsilon)^{m}$, and a valid procedure must refuse to certify on that event unless this '
                'probability is at most $\\delta$; let $\\epsilon\\to0$.'))
    A(('prop', 'Proposition A3 (what mixing simulations with anchors costs).',
            'With the mixed calibration [[mix]], $\\mathbb{E}_Q[L_{field}(\\hat\\lambda_\\psi)]\\le\\alpha+\\psi\\,'
            '\\mathrm{TV}(\\rho_P,\\rho_Q)$, where $\\rho_P$, $\\rho_Q$ are the laws of the standardised residual vector '
            'under the two laws. The bias grows linearly with the share $\\psi$ of the weight on simulations, while the '
            'slack $1/(wn+m+1)$ of the calibration shrinks.'))
    A(('proof', f'This is the weighted, non-exchangeable form of conformal risk control ({L("S1", "Barber et al. 2023")}; '
                f'anchor A1): the coverage gap is at most the sum of the normalised weights times the total-variation '
                f'distance between each calibration case and the field case. It is zero for the anchors and at most '
                f'$\\mathrm{{TV}}(\\rho_P,\\rho_Q)$ for each simulation, and the simulations carry the share $\\psi$.'))
    A(('box', ['**What is new.** (1) Guarantees for boundary conditions that hold whatever the real law, by calibrating on '
               'a few measured cases while the simulator keeps its other roles (Proposition A1). (2) Distribution-free '
               'lower bounds on the number of such cases: 9 for an average guarantee and 22 for a 90% certificate at '
               '$\\alpha$ = 0.10 (Proposition A2), a planning number for any monitoring programme. (3) The exact cost of '
               'mixing simulations and anchors, and the test that shows the mix inherits the simulator\'s bias (Proposition '
               'A3, T14). To our knowledge none of these appears in the eighty papers of reviews I–IV.']))
    # ------------------------------------------------------------------------------------------- 4.3 tests
    A(('h2', '4.3 Tests'))
    A(('p', f'**T12: the simulation-calibrated band under shift.** Figure {{{{risk}}}} and Table {{{{t12}}}}. Without '
            f'shift the simulation calibration holds (risk {rng_(sims_none)}; one pool of 300 simulated aquifers, Monte '
            f'Carlo error about ±0.02). Under each shift it breaks: the share of weeks outside is {rng_(sims_shift, 2)}, '
            f'worst for $\\kappa$ ({R["delay"]["kappa"]["sims"]["risk"]:.2f} with the longer delay, '
            f'{R["rainbias"]["kappa"]["sims"]["risk"]:.2f} with the rain bias) and for the recharge '
            f'({R["delay"]["r"]["sims"]["risk"]:.2f}). Calibrated on anchors, the risk is at most 0.10 for every law and '
            f'goal: {rng_(anc[10], 3)} with 10 anchors, {rng_(anc[20], 3)} with 20 and {rng_(anc[40], 3)} with 40, '
            f'approaching 0.10 from below as Proposition A1 says.'))
    A(('img', 'risk', 17.0))
    A(('cap', 'Figure {{risk}}. T12: share of weeks outside the 90% band in the field, for the band calibrated on 300 '
              'simulated aquifers and on 10, 20 or 40 real anchors, under the four real laws (dashed: target 0.10).'))
    t12 = []
    for s, lab in SCEN:
        for g in G4:
            v = R[s][g]
            t12.append([lab if g == 'r' else '', GL[g],
                        f'**{v["sims"]["risk"]:.3f}**' if v['sims']['risk'] > 0.105 else f'{v["sims"]["risk"]:.3f}',
                        f'{v["m10"]["anchors"]["risk"]:.3f}', f'{v["m20"]["anchors"]["risk"]:.3f}',
                        f'{v["m40"]["anchors"]["risk"]:.3f}', f'{v["sims"]["halfwidth"]:.3f}',
                        f'{v["m20"]["anchors"]["halfwidth"]:.3f}'])
    A(('cap', 'Table {{t12}}. T12–T13: realized risk (share of weeks outside; bold above 0.105) of the band calibrated on '
              'simulations and on 10, 20 and 40 anchors, and the half-widths with simulations and with 20 anchors. Units: '
              'recharge mm/d, inflow m²/d, sea level m, κ dimensionless.'))
    A(('table', ['Real law', 'Goal', 'Sims', '10 anchors', '20 anchors', '40 anchors', 'hw sims', 'hw 20 anc.'], t12,
       [2.6, 2.6, 1.7, 1.9, 1.9, 1.9, 2.2, 2.2], 9))
    A(('p', f'**T13: the price of the guarantee.** Figure {{{{width}}}}. Without shift the anchor-calibrated band is '
            f'{100 * (np.mean(wid[10]["none"]) - 1):.0f}% wider than the simulation-calibrated one with 10 anchors, '
            f'{100 * (np.mean(wid[20]["none"]) - 1):.0f}% with 20 and {100 * (np.mean(wid[40]["none"]) - 1):.0f}% with '
            f'40: the slack $1/(m+1)$ of [[anc]]. Under shift the band widens much more, because the real errors are '
            f'larger than the simulator believes; that width is not a cost of the method but the honest size of the '
            f'uncertainty. Reshaping the score week by week on the simulations before calibrating on anchors did not '
            f'narrow the band (change {rng_([100 * v for v in plus], 0)}%): the ensemble\'s week-to-week spread already '
            f'has the right shape.'))
    A(('img', 'width', 17.0))
    A(('cap', 'Figure {{width}}. T13: half-width of the anchor-calibrated band divided by that of the '
              'simulation-calibrated band, for 10, 20 and 40 anchors and the four real laws.'))
    A(('p', f'**T14: mixing simulations and anchors.** Figure {{{{mix}}}}. With 20 anchors and a share $\\psi$ of the '
            f'weight on simulations, the band narrows steadily towards the simulation band as $\\psi\\to1$. Without shift '
            f'the risk stays below 0.10 (at $\\psi$ = 0.5: {rng_(mix_none)}); under shift it rises with $\\psi$, as '
            f'Proposition A3 predicts (at $\\psi$ = 0.5: {rng_(mix_shift, 2)}, above 0.10 in '
            f'{sum(v > 0.1 for v in mix_shift)} of {len(mix_shift)} cases). The anchors cannot distinguish the two '
            f'situations with 20 cases, so the safe rule is $\\psi$ = 0; a mix is defensible only when an independent '
            f'argument bounds the distance between simulator and reality.'))
    A(('img', 'mix', 17.0))
    A(('cap', 'Figure {{mix}}. T14: risk (top) and half-width (bottom) of the mixed calibration [[mix]] against the share '
              '$\\psi$ of the weight on simulations, for the recharge and for $\\kappa$, with 20 anchors.'))
    A(('h2', '4.4 Where anchors come from at a coastal aquifer'))
    A(('b', '**Sea level:** any period with a local tide gauge, or a neighbouring harbour gauge with land motion corrected '
            '(review II, C3); each year of record is one anchor for the sea-level boundary of that year.'))
    A(('b', '**Recharge and its coefficient:** a lysimeter or a soil-moisture station with drainage, or a dense '
            'head-monitoring campaign on a neighbouring plain; for $\\kappa$ the anchors must also carry a local rain '
            'gauge, or the floor of review III returns.'))
    A(('b', '**Inland inflow:** a gauged river reach or a well transect at the inland boundary in a neighbouring aquifer.'))
    A(('b', '**Exchangeability:** anchors from different years of one aquifer are only approximately exchangeable with '
            'the field year; anchors from similar neighbouring aquifers are closer to the assumption. For Fushë-Kuqe, the '
            'list of candidate anchors (Adriatic coastal aquifers with monitoring, years with gauges) is '
            '==to be compiled with the national monitoring agencies==.'))
    # ------------------------------------------------------------------------------------------- 5 synthesis
    A(('h', '5. Synthesis: eighty papers in one procedure'))
    A(('p', 'Table {{eighty}} places the eighty papers of reviews I–IV on the steps of the procedure. Card numbers carry '
            'the review: I-O1 is card O1 of review I, IV-C2 card C2 of this review. Review IV adds the step that turns '
            'every other one from a statement about the simulator into a statement about the world: calibration on real '
            'anchors.'))
    rows = []
    sets = (('I', cards_gar.CARDS), ('II', cards_matja.CARDS), ('III', cards_reshja.CARDS), ('IV', CARDS))
    for key, lab_ in STEPS:
        row = [lab_]
        for rv, cs in sets:
            ids = [c['id'] for c in cs if key in c['steps']]
            row.append(', '.join(ids) if ids else '–')
        rows.append(row)
    A(('cap', 'Table {{eighty}}. The eighty papers of reviews I–IV against the steps of the procedure (card numbers of '
              'each review; a paper can serve several steps).'))
    A(('table', ['Step', 'Review I', 'Review II', 'Review III', 'Review IV'], rows, [2.8, 3.55, 3.55, 3.55, 3.55], 9))
    A(('p', '**Order of work.** (1) Build the simulated aquifers from the rain, with the rain product\'s errors '
            '(RESHJA-GO). (2) Use them to design the reconstructor and to choose the instruments by guaranteed value '
            '(MATJA-GO). (3) Calibrate the final bands on real anchors (ANKORA-GO), at least 9 of them, 20 to 40 for a '
            'band within 10–20% of the simulation band when the simulator is right. (4) Report the simulation-calibrated '
            'band (GARANCIA-GO) alongside, as the narrow band that holds if the simulator is right; the gap between the '
            f'two is the measured cost of not knowing the real law. For several goals at once and a guarantee per '
            f'calibration set, the risk-controlling sets of {L("S2", "S2")} apply to the anchors unchanged; the few '
            f'anchors can also correct a large number of cheaper predictions by prediction-powered inference '
            f'({L("S3", "S3")}).'))
    # ------------------------------------------------------------------------------------------- 6 limitations
    A(('h', '6. Limitations'))
    A(('b', 'Every card is partly verified: landing pages were reached through search results only.'))
    A(('b', 'The guarantee of Proposition A1 needs the anchors to be exchangeable with the field; anchors from other '
            'years or other aquifers satisfy this only approximately, and the bound of Proposition A3 then applies to '
            'them as well.'))
    A(('b', 'Measured boundary functions are themselves uncertain (gauge errors, land motion); the anchors\' truth must be '
            'better than the band being calibrated.'))
    A(('b', 'The tests use the linear one-dimensional test bed of reviews I–III and three illustrative shifts.'))
    return B
