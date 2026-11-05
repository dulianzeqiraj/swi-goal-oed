"""Text of the fifth state-of-the-art review (English). blocks(AJ, GE) returns the block list; every number comes from
res/prirja.json. Conventions: $inline math$, **bold**, *italic*, ==yellow placeholder==, [text](url) hyperlink,
[[key]] equation number, {{key}} figure or table number."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(1, os.path.join(HERE, '..', 'matja_go'))
sys.path.insert(2, os.path.join(HERE, '..', 'reshja_go'))
sys.path.insert(3, os.path.join(HERE, '..', 'ankora_go'))
from cards_prirja import CARDS, INST_ORDER, SOTA_ROWS  # noqa: E402
import cards_gar  # noqa: E402
import cards_matja  # noqa: E402
import cards_reshja  # noqa: E402
import cards_ankora  # noqa: E402

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
]

OTHER = [
    dict(key='D1', text='Zeqiraj, D. (2026). Inputs, dispersion and boundary conditions from rain alone; GARANCIA-GO '
                        '("review I"), docs/literature/ in this repository.', url=None),
    dict(key='D2', text='Zeqiraj, D. (2026). State of the art II; MATJA-GO, the guaranteed value of a measurement '
                        '("review II"), docs/literature/ in this repository.', url=None),
    dict(key='D3', text='Zeqiraj, D. (2026). State of the art III: when the rain itself is uncertain; RESHJA-GO '
                        '("review III"), docs/literature/ in this repository.', url=None),
    dict(key='D4', text='Zeqiraj, D. (2026). State of the art IV: when the simulator is wrong; ANKORA-GO ("review IV"), '
                        'docs/literature/ in this repository (Proposition A3 corrected on 5 November 2026).', url=None),
    dict(key='D5', text='Internal documents of the project: RINDËRTIMI-GO (test bed, ensemble smoother with the exact '
                        'solver); the code of this review in experiments/prirja_go/.', url=None),
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


LAWS = (('none', 'no drift'), ('linear', 'linear drift'), ('accel', 'accelerating drift'), ('step', 'abrupt shift'))
G4 = ('r', 'qL', 'eta', 'kappa')
GL = dict(r='recharge r', qL='inflow qL', eta='sea level η', kappa='coefficient κ')
STEPS = (('prior', 'prior from rain'), ('emulate', 'emulate'), ('invert', 'invert'), ('guarantee', 'guarantee'),
         ('check', 'field check'), ('design', 'design, operate'))


def blocks(AJ, GE):
    R = AJ['res']
    HS = AJ['hs']
    K, Ll, Lt = AJ['K'], AJ['l_level'], AJ['l_trend']
    hm0, hm1 = AJ['h_max']['0'], AJ['h_max']['1']
    hc0 = AJ['h_cert']['0']

    def risks(law, m, gs=G4, hs=None):
        hs = HS if hs is None else hs
        return [R[law][g][m][str(h)]['risk'] for g in gs for h in hs if R[law][g][m][str(h)]['finite'] > 0.999]

    def hw(law, g, m, h):
        return R[law][g][m][str(h)]['halfwidth']

    drift = ('linear', 'accel', 'step')
    sims_d = [v for law in drift for v in risks(law, 'sims')]
    sims_r = [v for law in drift for v in risks(law, 'sims', ('r',))]
    sims_k = [v for law in drift for v in risks(law, 'sims', ('kappa',))]
    sims_qe = [v for law in drift for v in risks(law, 'sims', ('qL', 'eta'))]
    all_k = [v for law in drift for v in risks(law, 'all', ('kappa',))]
    all_r = [v for law in drift for v in risks(law, 'all', ('r',))]
    rec_k = [v for law in drift for v in risks(law, 'recent', ('kappa',))]
    rec_w = [v for law in LAWS for v in risks(law[0], 'recent', ('r', 'qL', 'eta'))]
    ls0_ok = [v for law in ('none', 'linear', 'step') for v in risks(law, 'ls0')]
    ls0_acc10 = risks('accel', 'ls0', hs=[h for h in HS if h <= 10])
    ls0_acc15k = R['accel']['kappa']['ls0']['15']['risk']
    loc0_step_r = max(risks('step', 'loc0', ('r',)))
    ls0_step_r = max(risks('step', 'ls0', ('r',)))
    ls1_k = [v for law in LAWS for v in risks(law[0], 'ls1', ('kappa',))]
    wk = ('r', 'qL', 'eta')
    w_all = [hw('none', g, 'ls0', h) / hw('none', g, 'all', h) - 1 for g in wk for h in HS if h <= 10]
    w_all15 = [hw('none', g, 'ls0', 15) / hw('none', g, 'all', 15) - 1 for g in wk]
    w_rec = [hw(law, g, 'ls0', h) / hw(law, g, 'recent', h) for law in ('none', 'linear') for g in wk for h in HS
             if h <= 10]
    w_k = [hw('none', 'kappa', 'ls0', h) / hw('none', 'kappa', 'all', h) for h in HS if h <= 15]
    B = []
    A = B.append
    A(('title', 'State of the art V: when the world drifts'))
    A(('subtitle', 'Twenty more papers from Oxford, Caltech, Berkeley and MIT (2020–2026) on forecasting through change, '
                   'calibration over time, a drying and warming water cycle and a moving coast; the state of the art and '
                   'the step beyond it; and PRIRJA-GO, guarantees that hold years ahead while the real law drifts'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation · companion to reviews '
                 'I–IV (GARANCIA-GO, MATJA-GO, RESHJA-GO, ANKORA-GO)'))
    # ------------------------------------------------------------------------------------------- 1 outcome
    A(('h', '1. Outcome'))
    A(('bbox', [
        '**Twenty new papers, five per institution, 2020–2026, each with links** (Section 3, Figure {{map}}). None was a '
        'card of reviews I–IV or of the earlier reviews. They address the weak point review IV left open: its anchors, '
        'past years in which a boundary function was measured, are exchangeable with a future year only if nothing '
        'changes, while rain, evapotranspiration, the water table and the sea all drift. Each card gives the state of '
        'the art the paper sets, what it cannot yet do for us, three lessons and an innovation step.',
        '**State of the art and beyond, for the proposal** (Section 2, Table {{sotab}}), and a map of all one hundred '
        'papers of reviews I–V on the steps of the procedure (Section 5, Table {{hundred}}).',
        f'**Innovation: PRIRJA-GO** (Section 4). *Horizon-matched calibration* scores every past year exactly as the '
        f'field year will be used: $h$ years after a window of $L$ years whose level and spread re-centre and re-scale '
        f'the band. Proposition P1: no weighting of past years removes a drift. Proposition P2: horizon matching removes '
        f'it exactly when its level is polynomial and its spread exponential in time. Proposition P3: with $K$ years of '
        f'record a guarantee reaches at most $K-L-8$ years ahead, a certificate $K-L-21$; for {K} years and $L$ = {Ll} '
        f'that is {hm0} and {hc0} years.',
        f'**Test: under drift both earlier calibrations break** (T15; 30 anchor years, a field year 1–20 years ahead, '
        f'three drift laws). Calibrated on simulations, the share of weeks outside the 90% band is {rng_(sims_r, 2)} '
        f'for the recharge and {rng_(sims_k, 2)} for $\\kappa$ instead of at most 0.10. Calibrated on all past years as in review IV it '
        f'is {rng_(all_k, 2)} for $\\kappa$ and up to {max(all_r):.2f} for the recharge.',
        f'**The matched band holds** (T16). With the level window ($L$ = {Ll}) the risk is {rng_(ls0_ok, 3)} for every '
        f'goal and horizon under no drift, linear drift and the abrupt shift, and {rng_(ls0_acc10, 3)} up to 10 years '
        f'under accelerating drift; beyond that it fails for $\\kappa$ ({ls0_acc15k:.2f} at 15 years), as Proposition P2 '
        f'predicts for a drift it does not cover. Matching the level alone is not enough: after the abrupt shift it '
        f'leaves up to {loc0_step_r:.2f} of the recharge weeks outside.',
        f'**The price** (T17). Without drift the matched band for the weekly goals is '
        f'{100 * min(w_all):.0f}–{100 * max(w_all):.0f}% wider than calibration on all past years up to 10 years ahead '
        f'and narrower than the only plain rule that is valid for them, the last nine years '
        f'({min(w_rec):.2f}–{max(w_rec):.2f} of its width). For the scalar $\\kappa$ it costs '
        f'{min(w_k):.1f}–{max(w_k):.1f} times the width, because its spread must be estimated from {Ll} values.']))
    # ------------------------------------------------------------------------------------------- 2 SOTA and beyond
    A(('h', '2. State of the art and the step beyond it'))
    A(('p', 'Reviews I–IV (D1–D4) guarantee bands for boundary conditions, choose instruments, handle an uncertain rain '
            'and, in review IV, make the guarantee independent of the simulator by calibrating on real anchors. Every one '
            'of those guarantees assumes that the calibration cases and the field are exchangeable. Across years they '
            'are not: the vadose delay grows as the water table falls, evaporative demand rises, the sea rises and land '
            'use changes. This review asks how long a band calibrated on the past stays valid, and how to make it valid '
            'for a stated number of years ahead.'))
    A(('p', '**Text for the proposal.** Forecasting under structural change, online calibration and attribution of '
            'hydrological trends have advanced quickly (Section 3): robust devices adapt after breaks, online risk '
            'control keeps a long-run error rate under arbitrary drift, and global analyses quantify how warming and '
            'pumping move the water balance. None of them gives a guarantee for a boundary condition a stated number of '
            'years ahead from a short record. The project goes beyond the state of the art with horizon-matched '
            'calibration (PRIRJA-GO), which removes polynomial drift exactly and makes the guarantee hold at the '
            'horizon of use; by stating how far ahead a record of a given length can guarantee and certify a band; and '
            'by testing both against the simulation and anchor calibrations of the earlier reviews under realistic '
            'drift.'))
    A(('cap', 'Table {{sotab}}. State of the art (2020–2026) and the step beyond it. Card numbers refer to Section 3; T '
              'numbers to the tests of Section 4.'))
    A(('table', ['Topic', 'State of the art', 'Its limit for our problem', 'Our step beyond', 'Evidence'],
       SOTA_ROWS(AJ), [2.6, 3.9, 3.2, 3.8, 3.5], 9, False))
    # ------------------------------------------------------------------------------------------- 3 the papers
    A(('h', '3. The twenty papers'))
    A(('p', 'Five papers per institution, all from 2020–2026 (Figure {{map}}). The rules of the earlier reviews apply: '
            'direct use, a link to the institution at the time of publication (JPL for Caltech, Lawrence Berkeley '
            'National Laboratory for Berkeley), a state-of-the-art contribution, and no paper that was a card before. '
            'This batch gives priority to calibration and forecasting under drift, then to measured drift of the water '
            'cycle and of the coast. Preprints, working papers and books are marked as such on their venue line. No '
            '2020–2026 paper on a transition-zone width or dispersivity that changes in time was found at the four '
            'institutions; dispersion is served indirectly.'))
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
    # ------------------------------------------------------------------------------------------- 4 PRIRJA-GO
    A(('h', '4. Innovation: PRIRJA-GO, guarantees for a stated number of years ahead'))
    A(('img', 'scheme', 17.0))
    A(('cap', 'Figure {{scheme}}. Horizon-matched calibration. Each past origin $o$ has a window of $L$ anchor years, '
              'whose centre $c_o$ and spread $\\sigma_o$ re-centre and re-scale the score of the year $o+h$. The field '
              'band for the year $K+h$ uses the last window. The score is computed with the same lag $h$ in calibration '
              'and in use.'))
    A(('h2', '4.1 Anchor years and the set-up'))
    A(('p', f'An **anchor year** is a year in which the boundary function of interest was measured while the usual data '
            f'were collected: a year of tide-gauge record for the sea level, a lysimeter or soil-moisture station for '
            f'the recharge, a gauged reach for the inflow. The reconstructor of reviews I–IV is run on each anchor year '
            f'(rain and the usual heads) and its standardised error $u_t(w)=(x_t(w)-m_t(w))/s_t(w)$ is kept for every '
            f'week $w$; $\\bar u_t$ is its mean over the weeks. Anchors are years $t$ = 1, …, $K$ ($K$ = {K}, one per year) '
            f'and the field is the year $K+h$.'))
    A(('p', 'The test bed is that of reviews I–IV (D5): 32 cells, 64 weekly steps, the ensemble smoother with the exact '
            'solver (128 members) and four loggers (0.25, 1.25, 2.75, 4.25 km); the simulator keeps the year-0 law. Four '
            'real histories are compared (Figure {{drift}}). Without drift, every year follows the simulator. Under '
            'linear drift the vadose delay grows by 0.42 d per year (14 d to 35 d over 50 years, as the water table '
            'falls), the recharge-coefficient median falls by 1% per year, the inflow mean by 0.01 m²/d per year and the '
            'sea-level mean rises by 5 mm per year. Accelerating drift reaches the same values at year 50 '
            'quadratically. The abrupt shift is a new well field in year 24: the delay jumps to 28 d, the inflow mean '
            'drops by 0.5 m²/d and the coefficient by 25%.'))
    A(('img', 'drift', 17.0))
    A(('cap', 'Figure {{drift}}. Left: the vadose delay of the four histories (the simulator keeps 14 d). Right: the mean '
              'standardised error of the $\\kappa$ reconstruction in the anchor years (lines, averaged over the '
              'draws) and in the field years (dots). The heads absorb the drifts of the means; the delay does not drop '
              'out and builds a growing error.'))
    A(('p', 'For an origin $o$ with window $W_o=\\{o-L+1,\\dots,o\\}$, let $c_o$ be the least-squares polynomial of degree '
            '$p$ through $(t,\\bar u_t)_{t\\in W_o}$ evaluated at $o+h$, and $\\sigma_o$ the spread of the window (the '
            'root-mean-square deviation of $u_t(w)$ from $\\bar u_t$ for weekly goals; the residual standard deviation of '
            'the fit for the scalar $\\kappa$). The horizon-matched score of origin $o$ is'))
    A(('eq', 'hm', 'S_o(w)=\\frac{|u_{o+h}(w)-c_o|}{\\sigma_o},\\qquad o=L,\\dots,K-h,'))
    A(('p', 'and, with $L_o(\\lambda)$ the share of the weeks of origin $o$ with $S_o(w)>\\lambda$,'))
    A(('eq', 'hcal', ['\\hat\\lambda_h=\\inf\\left\\{\\lambda:\\frac{1}{n(h)+1}\\left(\\sum_{o=L}^{K-h}L_o(\\lambda)+1'
                      '\\right)\\le\\alpha\\right\\}\\text{, with }n(h)=K-L-h+1,',
                      '\\text{field band: }m+s\\,(c_K\\pm\\hat\\lambda_h\\,\\sigma_K).']))
    A(('p', f'Degree 0 with $L$ = {Ll} is the *level* version, degree 1 with $L$ = {Lt} the *trend* version; the '
            f'location-only ablation drops $\\sigma_o$. The plain rules of T15 calibrate the unmodified scores '
            f'$|u_t(w)|$ on simulations (review I), on all {K} anchor years (review IV), on the last nine years, or on all '
            f'years with weights $0.9^{{K-t}}$ (weighted conformal prediction, {L("S1", "S1")}). All calibrations are exact '
            f'(weighted quantiles, no grid). Each result averages {AJ["reps"]} draws of one anchor per year from '
            f'{AJ["na"]} candidates; the risk is measured on {AJ["n_test"]} field cases of each target year.'))
    A(('h2', '4.2 Guarantees'))
    A(('prop', 'Proposition P1 (the past is a shifted anchor).',
            'Let the anchor years have score laws $\\rho_t$ and the field year $K+h$ the law $\\rho_{K+h}$, all cases '
            'independent, and calibrate with weights $w_t\\in[0,1]$. (i) The field risk is at most '
            '$\\alpha+\\sum_t\\tilde w_t\\,\\epsilon_t$, with $\\tilde w_t=w_t/(\\sum_s w_s+1)$ and $\\epsilon_t$ the '
            'distance created by swapping year $t$ with the field year, $\\epsilon_t\\le2\\,\\mathrm{TV}(\\rho_t,'
            '\\rho_{K+h})$. (ii) If $\\epsilon$ grows with the lag $l=K+h-t$, then among all weights that give a finite '
            'band at $\\alpha$ = 0.10 the bound is smallest for weight 1 on the last nine years, where it equals '
            '$\\alpha+\\frac{1}{10}\\sum_{l=h}^{h+8}\\epsilon(l)$; for $\\epsilon(l)=\\delta l$ this is '
            '$\\alpha+0.9\\,\\delta\\,(h+4)$, which grows with the horizon for every choice of weights.'))
    A(('proof', '(i) is the weighted, non-exchangeable bound of conformal risk control (anchor A1; '
                f'{L("S1", "Barber et al. 2023")}) with the loss bounded by 1; for independent cases the swap changes one '
                'pair from $\\rho_t\\otimes\\rho_{K+h}$ to $\\rho_{K+h}\\otimes\\rho_t$, at distance at most '
                '$2\\,\\mathrm{TV}(\\rho_t,\\rho_{K+h})$. (ii) A finite band needs $\\alpha(\\sum w+1)\\ge1$, that is '
                '$\\sum w\\ge9$. Minimising $\\sum w_t\\epsilon_t/(\\sum w+1)$ over $w\\in[0,1]^K$ with $\\sum w\\ge9$ is a '
                'linear-fractional problem whose optimum puts weight 1 on the nine smallest $\\epsilon_t$; adding '
                'weight on a tenth year raises the ratio, because its $\\epsilon$ exceeds the mean of the nine.'))
    A(('prop', 'Proposition P2 (horizon matching removes polynomial drift).',
            'Let $u_t(w)=\\mu(t)+\\sigma(t)\\,\\varepsilon_t(w)$, where the vectors $\\varepsilon_t$ are independent and '
            'identically distributed across years (any law over the weeks). (i) If $\\sigma$ is constant and $\\mu$ is a '
            'polynomial of degree at most $p+1$, the location-only scores $|u_{o+h}-c_o|$ have the same law at every '
            'origin and in the field year. (ii) If $\\sigma(t)=\\sigma_0e^{\\gamma t}$ and $\\mu$ has degree at most $p$, '
            'the scores [[hm]] have the same law at every origin and in the field year, whatever the coefficients of '
            '$\\mu$ and the rate $\\gamma$.'))
    A(('proof', 'Write $t=o+\\tau$. The least-squares fit of degree $p$ reproduces every polynomial of degree at most $p$ '
                'in $\\tau$, and the $\\tau^{p+1}$ term of $\\mu(o+\\tau)$ has a coefficient that does not depend on '
                '$o$; so in (i) $u_{o+h}-c_o$ is a constant plus a fixed linear combination of $\\varepsilon_{o-L+1},'
                '\\dots,\\varepsilon_o,\\varepsilon_{o+h}$, whose law does not depend on $o$. In (ii) the fit removes '
                '$\\mu$ entirely; numerator and $\\sigma_o$ are both $e^{\\gamma o}$ times a fixed function of the same '
                '$\\varepsilon$ (the spread is equivariant to scale and invariant to shifts), and $e^{\\gamma o}$ '
                'cancels.'))
    A(('p', 'The scores are therefore identically distributed, which removes the drift from the calibration. Their '
            'windows overlap, so they are dependent; Proposition A1 of review IV then holds only approximately, and T16 '
            'measures how well. Neither part covers an accelerating drift with the level version ($p$ = 0, quadratic '
            '$\\mu$), and T16 shows the consequence.'))
    A(('prop', 'Proposition P3 (how far ahead a record reaches).',
            f'Horizon-matched calibration at horizon $h$ has $n(h)=K-L-h+1$ scores. (i) [[hcal]] has a finite solution '
            f'only if $n(h)\\ge(1-\\alpha)/\\alpha$, that is $h\\le K-L-8$ at $\\alpha$ = 0.10. (ii) A certificate '
            f'$R\\le\\alpha$ at confidence $1-\\delta$ needs $n(h)\\ge\\log\\delta/\\log(1-\\alpha)$, that is '
            f'$h\\le K-L-21$ at $\\alpha=\\delta$ = 0.10. With $K$ = {K}: {hm0} and {hc0} years for the level version '
            f'($L$ = {Ll}), {hm1} years and no certificate for the trend version ($L$ = {Lt}). Each year of record adds '
            f'one year of horizon.'))
    A(('proof', 'Proposition A2 of review IV applied to the $n(h)$ scores: (i) the left side of [[hcal]] is at least '
                '$1/(n(h)+1)$; (ii) the same two-point law shows that fewer scores cannot certify.'))
    A(('box', ['**What is new.** (1) Horizon-matched location–scale calibration, which removes a drift exactly when its '
               'level is polynomial and its spread exponential in time (Proposition P2), so a band calibrated on past '
               'years holds in a future year. (2) A horizon limit: how many years ahead a record of $K$ years can '
               'guarantee or certify a band, $K-L-8$ and $K-L-21$ years at $\\alpha$ = 0.10 (Proposition P3), a planning '
               'number for the length of a monitoring record. (3) The proof that no weighting of past years removes a '
               'drift (Proposition P1), and the tests that show both the simulation and the anchor calibrations of the '
               'earlier reviews breaking under realistic drift while the matched band holds. To our knowledge none of '
               'these appears in the one hundred papers of reviews I–V.']))
    # ------------------------------------------------------------------------------------------- 4.3 tests
    A(('h2', '4.3 Tests'))
    A(('p', f'**T15: plain calibrations under drift.** Figure {{{{risk}}}} and Table {{{{t16}}}}. Calibrated on '
            f'simulations the band breaks under every drift: recharge {rng_(sims_r, 2)}, $\\kappa$ {rng_(sims_k, 2)}, '
            f'inflow and sea level {rng_(sims_qe, 2)}. Calibrated on all {K} past years, as review IV would, it breaks too, because the old '
            f'years carry less error than the field: $\\kappa$ {rng_(all_k, 2)}, recharge {rng_(all_r, 2)}. The last nine '
            f'years are valid for the weekly goals only by being extreme (risk {rng_(rec_w, 3)}: with nine anchors the '
            f'band is the largest score seen) and still fail for $\\kappa$ when the drift continues '
            f'({rng_(rec_k, 2)}); decaying weights behave the same way, as Proposition P1 says.'))
    A(('p', f'**T16: horizon-matched calibration.** With the level window the risk is {rng_(ls0_ok, 3)} for every goal '
            f'and every horizon with a band under no drift, linear drift and the abrupt shift. Under accelerating drift '
            f'it is {rng_(ls0_acc10, 3)} up to 10 years ahead and {ls0_acc15k:.2f} for $\\kappa$ at 15 years: a quadratic '
            f'level is outside Proposition P2 for $p$ = 0. The trend window covers that case in principle but is noisy '
            f'for the scalar $\\kappa$ ({rng_(ls1_k, 3)} across laws and horizons), so the level window with a horizon '
            f'of at most 10 years is the robust choice. Matching the level without the spread fails after the abrupt '
            f'shift (recharge up to {loc0_step_r:.2f}, against {ls0_step_r:.3f} with the spread), because the shift '
            f'widens the errors more than it moves them.'))
    A(('img', 'risk', 17.0))
    A(('cap', f'Figure {{{{risk}}}}. T15–T16: share of weeks outside the 90% band in the field year $K+h$, for the '
              f'recharge (top) and $\\kappa$ (bottom) under the three drift histories (dashed: target 0.10; dotted: the '
              f'horizon limit {hm0} years of the level version; a missing point means that no band exists).'))
    t16 = []
    for law, lab in LAWS:
        for g in G4:
            v = R[law][g]

            def cell(m, h):
                x = v[m][str(h)]
                if x['finite'] < 0.999:
                    return 'no band'
                s = f'{x["risk"]:.3f}'
                return f'**{s}**' if x['risk'] > 0.105 else s
            t16.append([lab if g == 'r' else '', GL[g], cell('sims', 10), cell('all', 10), cell('recent', 10),
                        cell('ls0', 1), cell('ls0', 5), cell('ls0', 10), cell('ls0', 15)])
    A(('cap', 'Table {{t16}}. T15–T16: realized risk (share of weeks outside; bold above 0.105). Plain rules at $h$ = 10 '
              'years; horizon-matched level version at $h$ = 1, 5, 10 and 15 years.'))
    A(('table', ['History', 'Goal', 'Sims', 'All 30', 'Last 9', 'Matched h=1', 'h=5', 'h=10', 'h=15'], t16,
       [2.4, 2.4, 1.5, 1.5, 1.5, 1.9, 1.5, 1.5, 1.5], 9))
    A(('p', f'**T17: the price and the reach.** Figure {{{{width}}}}. Without drift the matched band for the weekly goals '
            f'is {100 * min(w_all):.0f}–{100 * max(w_all):.0f}% wider than calibration on all past years up to 10 years '
            f'ahead and {100 * min(w_all15):.0f}–{100 * max(w_all15):.0f}% wider at 15 years, where only '
            f'{K - Ll - 15 + 1} scores remain; against the last nine years, the only valid plain rule for them, it is '
            f'{min(w_rec):.2f}–{max(w_rec):.2f} of the width. For $\\kappa$ the matched band is {min(w_k):.1f}–'
            f'{max(w_k):.1f} times wider than the all-years band, because the spread of a scalar must come from the '
            f'{Ll} values of the window. Under drift the band widens with the horizon as the errors do. The reach is '
            f'that of Proposition P3: no band beyond {hm0} years with the level window and {hm1} years with the trend '
            f'window, for a {K}-year record.'))
    A(('img', 'width', 17.0))
    A(('cap', 'Figure {{width}}. T17: half-width of the band against the horizon for the recharge (top) and $\\kappa$ '
              '(bottom), without drift (left) and under linear drift (right). Plain rules do not depend on the horizon; '
              'the matched bands widen as fewer scores remain and as the errors grow.'))
    A(('h2', '4.4 Where the anchor years come from at Fushë-Kuqe'))
    A(('b', '**Sea level:** each year of a tide-gauge record with land motion corrected is one anchor year; the length of '
            'the usable record of the nearest gauge is ==to be confirmed with the national hydrometeorological '
            'service==, and it sets the horizon of Proposition P3.'))
    A(('b', '**Recharge and its coefficient:** years with a lysimeter, a soil-moisture station with drainage, or a dense '
            'head campaign together with a local rain gauge; for $\\kappa$ the rain gauge is essential (review III). '
            'Existing records: ==to be compiled==.'))
    A(('b', '**What drifts:** the water table and with it the vadose delay (pumping), evaporative demand (O4, M5), the '
            'source of recharge under irrigation and pumping (M3), the relative sea level with subsidence, and land '
            'use. Each named driver gives a regressor that can replace time in the window fit of [[hm]].'))
    A(('b', f'**Planning rule:** a guarantee $h$ years ahead needs a record of at least $h+L+8$ years of anchors, '
            f'{10 + Ll + 8} years for a decade ahead with the level window; a certificate needs $h+L+21$.'))
    # ------------------------------------------------------------------------------------------- 5 synthesis
    A(('h', '5. Synthesis: one hundred papers in one procedure'))
    A(('p', 'Table {{hundred}} places the hundred papers of reviews I–V on the steps of the procedure. Card numbers carry '
            'the review: I-O1 is card O1 of review I, V-C2 card C2 of this review. Review V adds the time axis to the '
            'guarantee: the band is calibrated for the horizon at which it will be used.'))
    rows = []
    sets = (('I', cards_gar.CARDS), ('II', cards_matja.CARDS), ('III', cards_reshja.CARDS), ('IV', cards_ankora.CARDS),
            ('V', CARDS))
    for key, lab_ in STEPS:
        row = [lab_]
        for rv, cs in sets:
            ids = [c['id'] for c in cs if key in c['steps']]
            row.append(', '.join(ids) if ids else '–')
        rows.append(row)
    A(('cap', 'Table {{hundred}}. The one hundred papers of reviews I–V against the steps of the procedure (card numbers '
              'of each review; a paper can serve several steps).'))
    A(('table', ['Step', 'Review I', 'Review II', 'Review III', 'Review IV', 'Review V'], rows,
       [2.6, 2.9, 2.9, 2.9, 2.9, 2.9], 9))
    A(('p', f'**Order of work.** (1) Build the simulated aquifers from the rain, with the rain product\'s errors '
            f'(RESHJA-GO). (2) Use them to design the reconstructor and to choose the instruments by guaranteed value '
            f'(MATJA-GO). (3) Collect anchor years, at least $h+L+8$ of them for a band $h$ years ahead (PRIRJA-GO, '
            f'Proposition P3). (4) Calibrate the band by horizon matching [[hcal]], with the level window and $h$ at '
            f'most 10 years unless the drift is known to be linear; with no drift it reduces to the anchor calibration '
            f'of ANKORA-GO up to a small loss of width. (5) Report the simulation-calibrated band (GARANCIA-GO) and the '
            f'plain anchor band alongside: the gaps between the three are the measured costs of not knowing the real '
            f'law and of not knowing how it will drift.'))
    # ------------------------------------------------------------------------------------------- 6 limitations
    A(('h', '6. Limitations'))
    A(('b', 'Every card is partly verified: landing pages were reached through search results only.'))
    A(('b', 'Proposition P2 needs a polynomial level and an exponential spread; real drift can accelerate, saturate or '
            'jump. T16 shows a valid band for a jump and a failure for acceleration beyond 10 years.'))
    A(('b', 'The matched scores are dependent because the windows overlap; the guarantee is approximate, and T16 '
            'measures it in one test bed only.'))
    A(('b', 'One anchor per year is assumed; in practice anchor years can be missing, and each gap shortens the reach '
            'of Proposition P3.'))
    A(('b', 'The tests use the linear one-dimensional test bed of reviews I–IV and three illustrative drift histories.'))
    return B
