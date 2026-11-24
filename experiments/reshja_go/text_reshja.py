"""Text of the third state-of-the-art review (English). blocks(RJ, GE) returns the block list; every number comes from
res/reshja.json and from the results of reviews I and II. Conventions: $inline math$, **bold**, *italic*,
==yellow placeholder==, [text](url) hyperlink, [[key]] equation number, {{key}} figure or table number."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(1, os.path.join(HERE, '..', 'matja_go'))
from cards_reshja import CARDS, INST_ORDER, SOTA_ROWS  # noqa: E402
import cards_gar  # noqa: E402
import cards_matja  # noqa: E402

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
    dict(key='S3', text='Calvello, E., Reich, S., & Stuart, A. M. (2025). Ensemble Kalman methods: a mean-field '
                        'perspective. Acta Numerica 34, 123–291.', url='https://doi.org/10.1017/S0962492924000060'),
]

OTHER = [
    dict(key='D1', text='Zeqiraj, D. (2026). Inputs, dispersion and boundary conditions from rain alone: twenty papers and '
                        'GARANCIA-GO ("review I"). docs/literature/Literature_review_Inputs_Dispersion_Boundary_'
                        'Conditions_from_Rain_Oxford_Caltech_Berkeley_MIT_2020-2026.docx in this repository.', url=None),
    dict(key='D2', text='Zeqiraj, D. (2026). State of the art II: inputs, dispersion and boundary conditions from rain; '
                        'MATJA-GO, the guaranteed value of a measurement ("review II"). docs/literature/Literature_review_'
                        'State_of_the_Art_II_Inputs_Dispersion_Boundary_Conditions_from_Rain_MATJA-GO_Oxford_Caltech_'
                        'Berkeley_MIT_2020-2026.docx in this repository.', url=None),
    dict(key='D3', text='Internal documents of the project: RINDËRTIMI-GO (test bed, ensemble smoother with the exact '
                        'solver); SHIU-GO (rain law, Erlang-2 vadose filter); the code of this review in '
                        'experiments/reshja_go/.', url=None),
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


DES = ('rain only', '1 logger', '2 loggers', '4 loggers', '8 loggers')
NLOG = dict(zip(DES, (0, 1, 2, 4, 8)))
STEPS = (('prior', 'prior from rain'), ('emulate', 'emulate'), ('invert', 'invert'), ('guarantee', 'guarantee'),
         ('check', 'field check'), ('design', 'design, operate'))


# ------------------------------------------------------------------------------------------------------------ blocks
def blocks(RJ, GE):
    R = RJ['res']
    F = RJ['filter']
    G4 = ('r', 'qL', 'eta', 'kappa')
    LOGD = DES[1:]
    nv = [R['naive'][d] for d in LOGD]
    nk = [v['kappa']['crc_risk'] for v in nv]
    nkc = [v['kappa']['sup_cover'] for v in nv]
    nrc = [v['r']['sup_cover'] for v in nv]
    nqc = [v['qL']['sup_cover'] for v in nv]
    nec = [v['eta']['sup_cover'] for v in nv]
    ok = [R[s][d][g] for s in ('exact', 'aware', 'aware_r2', 'gauge') for d in DES for g in G4 + ('kappa_eff',)]
    okr, okc = [v['crc_risk'] for v in ok], [v['sup_cover'] for v in ok]
    kap = {s: [R[s][d]['kappa']['halfwidth'] for d in DES] for s in R}
    keff = [R['aware_r2'][d]['kappa_eff']['halfwidth'] for d in DES]
    rr = {s: [R[s][d]['r']['halfwidth'] for d in DES] for s in R}
    floor = RJ['floor']['halfwidth']
    neff = 1.0 / np.array(F['kernel_ratio'])
    meas, pred = np.array(F['measured']), np.array(F['predicted'])
    rel = np.abs(meas / pred - 1)
    sbd = RJ['sig_b']
    B = []
    A = B.append
    A(('title', 'State of the art III: when the rain itself is uncertain'))
    A(('subtitle', 'Twenty more papers from Oxford, Caltech, Berkeley and MIT (2020–2026) on rainfall products, recharge, '
                   'mixing and coastal boundaries; the state of the art and the step beyond it; and RESHJA-GO, guaranteed '
                   'boundary conditions when the rain is known only through a product'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation · companion to reviews I '
                 '(GARANCIA-GO) and II (MATJA-GO)'))
    # ------------------------------------------------------------------------------------------- 1 outcome
    A(('h', '1. Outcome'))
    A(('bbox', [
        '**Twenty new papers, five per institution, 2020–2026, each with links** (Section 3, Figure {{map}}). None was a '
        'card of reviews I or II or of the earlier reviews. This batch looks at the one input the two first reviews '
        'took as exact: the rain. Every card states the state of the art the paper sets, what it cannot yet do for us, '
        'three lessons (inputs, dispersion, boundary conditions) and an innovation step.',
        '**State of the art and beyond, for the proposal** (Section 2, Table {{sotab}}), and a map of all sixty papers of '
        'reviews I–III against the eight steps of the procedure (Section 5, Table {{sixty}}).',
        '**Innovation: RESHJA-GO** (Section 4). "Knowing only the amount of rain" usually means knowing a product '
        '(satellite, reanalysis, a distant station) with a bias and daily errors. Proposition R1: a rain bias is '
        'invisible to every check made with heads, and $\\kappa$ has a floor that no logger removes. Proposition R2: '
        'the vadose filter averages the daily errors over $n_{eff}$ effective rain days and passes the bias untouched; '
        'the covariance of the filtered error can be computed from the product itself. Proposition R3: the guarantees of '
        'review I hold again when the simulated aquifers carry the product\'s errors.',
        f'**Test: calibrating as if the product were exact breaks every guarantee** (T9, 400 simulated aquifers per '
        f'setting, {int(100 * sbd)}% bias, daily errors of relative variance {F["daily_rel_var"]:.2f}). With loggers, '
        f'the band of $\\kappa$ misses in {rng_(nk, 2)} of the cases, the whole-function coverage of the recharge falls '
        f'to {rng_(nrc, 2)}, of the inflow to {rng_(nqc, 2)} and of the sea level to {rng_(nec, 2)}; more loggers make it '
        f'worse. Calibrated with the product\'s errors, every guarantee holds (share of weeks outside {rng_(okr)}, '
        f'coverage {rng_(okc, 2)}).',
        f'**The floor and the gauge** (T10). With the product, eight loggers bring the guaranteed half-width of $\\kappa$ '
        f'only to {kap["aware_r2"][-1]:.3f}, against the floor {floor:.3f} of Proposition R1 and {kap["exact"][-1]:.3f} '
        f'with exact rain, while $c=\\kappa b$ shrinks to {keff[-1]:.3f}. A local rain gauge with one logger gives '
        f'$\\kappa$ to {R["gauge"]["1 logger"]["kappa"]["halfwidth"]:.3f}, which the product does not reach with '
        f'eight; with two loggers it gives the recharge to {R["gauge"]["2 loggers"]["r"]["halfwidth"]:.3f} mm/d against '
        f'{R["aware_r2"]["2 loggers"]["r"]["halfwidth"]:.3f} with the product. The first instrument to buy is a rain '
        f'gauge.',
        f'**The filter law** (T11). On 300 rain records the measured variance of the filtered error matches $v/n_{{eff}}$ '
        f'to a median of {100 * np.median(rel):.1f}%; the mean $n_{{eff}}$ is {np.mean(neff):.1f} rain days, not the '
        f'{F["four_tau"] + 1:.0f} of steady rain, so a product with poor daily skill still leaves a weekly forcing error '
        f'of about {100 * np.sqrt(np.mean(pred)):.0f}%. Using that covariance in the recharge prior (R2 prior) cuts the '
        f'guaranteed recharge half-width with eight loggers from {rr["aware"][-1]:.3f} to {rr["aware_r2"][-1]:.3f} mm/d.']))
    # ------------------------------------------------------------------------------------------- 2 SOTA and beyond
    A(('h', '2. State of the art and the step beyond it'))
    A(('p', 'Reviews I and II (D1, D2) treated the rain as exact and asked which bands can be guaranteed and which '
            'measurement buys most. In practice the rain of a coastal aquifer is rarely measured on site: it comes from a '
            'reanalysis such as ERA5-Land, a gridded product such as E-OBS, a satellite product such as IMERG, or a station '
            'tens of kilometres away. This review asks what the guarantees become when the rain itself is uncertain, and '
            'what to do about it.'))
    A(('p', '**Text for the proposal.** Rainfall products are now available everywhere at daily or finer resolution and are '
            'routinely corrected, downscaled or blended with gauges (Section 3), and recharge, groundwater and coastal '
            'boundary conditions are increasingly estimated from them. Their errors are known to be large at the scale of '
            'one aquifer, but they are carried into groundwater models, if at all, as a scenario or an ensemble without a '
            'guarantee. The project goes beyond the state of the art in three ways: it proves that a rain bias cannot be '
            'detected or corrected with heads and sets the floor it imposes on the recharge coefficient (Proposition R1); '
            'it gives the exact law by which the unsaturated zone averages daily rain errors, and uses it as a '
            'data-driven prior for the recharge error (Proposition R2); and it restores finite-sample guarantees for every '
            'boundary function when only a rain product is known (Proposition R3, RESHJA-GO), with a rule for when a '
            'local rain gauge is worth more than further head loggers. All three are tested numerically below.'))
    A(('cap', 'Table {{sotab}}. State of the art (2020–2026) and the step beyond it. Card numbers refer to Section 3; T '
              'numbers to the tests of Section 4.'))
    A(('table', ['Topic', 'State of the art', 'Its limit for our problem', 'Our step beyond', 'Evidence'],
       SOTA_ROWS(RJ), [2.6, 3.9, 3.2, 3.8, 3.5], 9, False))
    # ------------------------------------------------------------------------------------------- 3 the papers
    A(('h', '3. The twenty papers'))
    A(('p', 'Five papers per institution, all published in 2020–2026 (Figure {{map}}). The rules of reviews I and II '
            'apply: direct use, a link to the institution at the time of publication (JPL for Caltech, Lawrence Berkeley '
            'National Laboratory for Berkeley), a state-of-the-art contribution, and no paper that was a card in an '
            'earlier review. This batch gives priority to rainfall products and their errors, then to recharge from '
            'rain, mixing and dispersion, and coastal boundaries.'))
    A(('p', '**Verification.** The hosts doi.org, arxiv.org, openreview.net and most publisher pages were blocked in this '
            'environment, so every landing page was reached through search results that quote it, and every card is '
            'marked partly verified; where an author list or a volume could not be confirmed, the card gives only what '
            'was seen and says so. The search budget of the session ran out before every affiliation could be seen; '
            'card C4 gives its author\'s institution from our own knowledge and says so.'))
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
    # ------------------------------------------------------------------------------------------- 4 RESHJA-GO
    A(('h', '4. Innovation: RESHJA-GO, guarantees when the rain itself is uncertain'))
    A(('img', 'scheme', 17.0))
    A(('cap', 'Figure {{scheme}}. RESHJA-GO. The model sees a rain product with daily errors and a bias; the vadose filter '
              'averages the daily errors over a few effective rain days and passes the bias; the heads see only the '
              'product of the recharge coefficient and the bias. Bottom: what can be guaranteed. Insets: one simulated '
              'record, daily rain (true and product) and the filtered series.'))
    A(('h2', '4.1 The rain product and the set-up'))
    A(('p', 'The test bed is that of reviews I and II (D3): a 5 km section, 32 cells, 64 weekly steps, the recharge law '
            '[[rech]] with the Erlang-2 vadose kernel $k_\\tau$ ($\\tau$ = 14 d) and lognormal $\\kappa$ (median 0.35, '
            'log-sd 0.25), Gaussian random fields for the sea level, the inland inflow, the recharge error and the initial '
            'head, and the ensemble smoother with the exact solver (128 members) as reconstructor. The model now sees the '
            'rain through a product [[prod]]:'))
    A(('eq', 'rech', 'r(t)=\\kappa\\,(k_\\tau*P)(t)+e(t)'))
    A(('eq', 'prod', ['P_{obs}(d)=\\frac{P(d)}{b}\\,\\epsilon(d)\\text{, with }\\log b\\sim N(0,s_b^{2})\\text{ for the record,}',
                      '\\epsilon(d)\\text{ independent, }\\mathbb{E}\\,\\epsilon=1\\text{, }\\mathrm{Var}\\,\\epsilon=v\\text{, day by day.}']))
    A(('p', f'Here $s_b$ = {sbd:.2f} (a 20% bias of the record, typical of a gridded product at one site) and the daily '
            f'errors are lognormal with log-sd {RJ["sig_e"]:.2f} ($v$ = {F["daily_rel_var"]:.2f}); a local gauge has '
            f'$s_b$ = {RJ["gauge"][0]:.2f} and log-sd {RJ["gauge"][1]:.2f}. Writing $f=k_\\tau*P$ and '
            f'$f_{{obs}}=k_\\tau*P_{{obs}}$ for the weekly filtered rain, the heads respond to $r$, and'))
    A(('eq', 'ident', 'r=\\kappa\\,f+e=c\\,f_{obs}-c\\,\\delta+e\\text{, with }c=\\kappa b\\text{ and }\\delta=f_{obs}-f/b.'))
    A(('p', 'Five settings are compared: **exact** (the reconstructor sees $P$, as in reviews I and II); **naive** '
            '(calibrated on simulated aquifers with exact rain, used where the rain comes from the product); **aware** '
            '(the simulated aquifers carry the product\'s errors, and the members\' coefficient $c$ has log-sd '
            '$\\sqrt{0.25^{2}+s_b^{2}}$); **aware + R2** (also the filtered error $\\delta$ in the recharge prior, with the '
            'covariance of Proposition R2 computed from the product); and **gauge** (a local rain gauge). Designs: rain '
            'only, one logger (2.0 km), two (2.0 and 4.75 km), four (0.25, 1.25, 2.75, 4.25 km) and all eight sites of '
            'review II. Scores average 300 random draws of 200 calibration and 200 test aquifers from pools of 400.'))
    A(('h2', '4.2 Guarantees'))
    A(('prop', 'Proposition R1 (a rain bias is invisible to the heads, and κ has a floor).',
            'Let the daily errors be absent ($\\epsilon\\equiv1$). (i) For any data $y$ that do not measure rain (heads, '
            'sea level, chloride under the flow model), the likelihood depends on $\\kappa$ and $b$ only through '
            '$c=\\kappa b$: no statistic of such data can detect $b$, and the field check of review I has power $\\alpha$ '
            'against any rain bias. (ii) If $\\log\\kappa\\sim N(\\mu_\\kappa,s_\\kappa^{2})$ and $\\log b\\sim N(0,s_b^{2})$ '
            'are independent of each other and of the other unknowns, then for every number of heads'))
    A(('eq', 'floor', '\\mathrm{Var}(\\log\\kappa\\mid y)\\ge s_\\ast^{2}=\\frac{s_\\kappa^{2}\\,s_b^{2}}{s_\\kappa^{2}+s_b^{2}},'))
    A(('p', 'with equality when $c$ is known exactly, so the 90% half-width of $\\kappa$ cannot fall below about '
            '$\\kappa_{med}\\,\\sinh(1.645\\,s_\\ast)$. (iii) The coefficient $c$ and the recharge function $r(t)$ are '
            'informed exactly as with exact rain, with prior log-sd $\\sqrt{s_\\kappa^{2}+s_b^{2}}$ for $c$.'))
    A(('proof', 'Substituting [[ident]] with $\\delta=0$ shows (i) and (iii). For (ii), by the law of total variance, '
                '$\\mathrm{Var}(\\log\\kappa\\mid y)\\ge\\mathbb{E}[\\mathrm{Var}(\\log\\kappa\\mid c,y)\\mid y]$; by (i), given $c$ '
                'the data carry no further information on $\\kappa$, so $\\mathrm{Var}(\\log\\kappa\\mid c,y)='
                '\\mathrm{Var}(\\log\\kappa\\mid\\log\\kappa+\\log b)$, which is $s_\\ast^{2}$ for independent Gaussians.'))
    A(('p', f'With $s_\\kappa$ = 0.25 and $s_b$ = {sbd:.2f}, $s_\\ast$ = {RJ["floor"]["sd_log"]:.3f} and the floor of the '
            f'half-width is {floor:.3f}, six times the {kap["exact"][3]:.3f} that four loggers give with exact rain. A '
            f'bias of the rain is the one error that more heads cannot repair.'))
    A(('prop', 'Proposition R2 (what the vadose filter averages, and what it passes).',
            'Let $f(t)=\\sum_u K(t,u)P(u)$ be the weekly filtered rain, $K$ the weekly average of the Erlang-2 operator. '
            'Then $\\mathbb{E}[f_{obs}(t)\\mid P,b]=f(t)/b$: the bias passes untouched. Given $P$ and $b$, the filtered '
            'error $\\delta$ has covariance $\\mathrm{Cov}(\\delta)=v\\,K\\,\\mathrm{diag}(P^{2})\\,K^{\\top}/b^{2}$, and in '
            'relative terms'))
    A(('eq', 'neff', ['\\frac{\\mathrm{Var}[f_{obs}(t)\\mid P,b]}{(f(t)/b)^{2}}=\\frac{v}{n_{eff}(t)}\\text{, with }'
                      'n_{eff}(t)=\\frac{\\left(\\sum_u K(t,u)P(u)\\right)^{2}}{\\sum_u K(t,u)^{2}P(u)^{2}}.']))
    A(('p', 'For steady rain $n_{eff}=1/\\sum_uK(t,u)^{2}\\approx4\\tau+1$; for intermittent rain it counts the rain days '
            'inside the memory of the filter, weighted by $K\\,P$. The covariance is estimated without bias from the '
            'product itself by $\\frac{v}{1+v}\\,K\\,\\mathrm{diag}(P_{obs}^{2})\\,K^{\\top}$.'))
    A(('proof', 'The filter is linear: $f_{obs}(t)-f(t)/b=\\sum_uK(t,u)P(u)(\\epsilon(u)-1)/b$ with independent zero-mean '
                'terms of variance $vP(u)^{2}/b^{2}$; and $\\mathbb{E}[P_{obs}^{2}]=(1+v)P^{2}/b^{2}$.'))
    A(('prop', 'Proposition R3 (the guarantee with a rain product).',
            'If the simulated aquifers draw the true rain, the bias and the daily errors from the error law of the product, '
            'and the reconstructor sees only $P_{obs}$ in every simulation as in the field, Propositions 1 and 2 of review '
            'I hold for $r$, $q_L$, $\\eta$, $h_0$, $\\kappa$ and $c$, whatever the reconstructor. If the error law is '
            'ignored, the guarantee is off by at most the total-variation distance between the residual laws with exact '
            'and with product rain (review I, Proposition 4), which T9 shows to be large.'))
    A(('proof', 'Each simulated case (rain, bias, daily errors, unknowns, data) is an i.i.d. draw from one joint law, and '
                'the reconstructor is one fixed map of $(P_{obs},y)$; apply exchangeability as in review I.'))
    A(('box', ['**What is new.** (1) The non-identifiability of the recharge coefficient under a rain bias, with the '
               'exact floor [[floor]], and the fact that no check made with heads can detect the bias (Proposition R1). '
               '(2) The exact law of how the unsaturated zone averages daily rain errors, with the effective number of rain '
               'days $n_{eff}$ and a covariance computable from the product alone, used as a prior for the recharge error '
               '(Proposition R2). (3) Finite-sample guarantees for every boundary function when the rain is known only '
               'through a product, and the measured cost of ignoring the product\'s errors (Proposition R3, T9). To our '
               'knowledge, none of these appears in the sixty papers of reviews I–III.']))
    # ------------------------------------------------------------------------------------------- 4.3 tests
    A(('h2', '4.3 Tests'))
    A(('p', f'**T9: coverage.** Figure {{{{cover}}}} and Table {{{{t9}}}}. With exact rain every guarantee holds. Calibrated '
            f'as if the product were exact, the guarantees collapse as soon as there are heads: the band of $\\kappa$ '
            f'misses in {rng_(nk, 2)} of the cases (coverage {rng_(nkc, 2)}), the whole-function coverage of the recharge '
            f'is {rng_(nrc, 2)}, of the inflow {rng_(nqc, 2)} and of the sea level {rng_(nec, 2)}. The heads make the '
            f'reconstructor confident about the wrong forcing, so more loggers make it worse, not better. With the '
            f'product\'s errors in the simulated aquifers (aware, aware + R2) and with a local gauge, every guarantee '
            f'holds again: share of weeks outside {rng_(okr)}, coverage {rng_(okc, 2)}.'))
    A(('img', 'cover', 17.0))
    A(('cap', 'Figure {{cover}}. T9: whole-function coverage of the 90% bands against the number of loggers, for the five '
              'rain settings (dashed: target).'))
    t9 = []
    lab = dict(exact='exact rain', naive='naive', aware='aware', aware_r2='aware + R2', gauge='gauge')
    for s in ('exact', 'naive', 'aware', 'aware_r2', 'gauge'):
        for d in ('rain only', '2 loggers', '8 loggers'):
            v = R[s][d]
            row = [lab[s] if d == 'rain only' else '', d]
            for g in ('r', 'qL', 'eta', 'kappa'):
                cell = f'{v[g]["halfwidth"]:.3f} / {v[g]["sup_cover"]:.2f}'
                row.append(f'**{cell}**' if v[g]['sup_cover'] < 0.85 else cell)
            t9.append(row)
    A(('cap', 'Table {{t9}}. T9: guaranteed 90% half-width / whole-function coverage (bold: coverage below 0.85). Units: '
              'recharge mm/d, inflow m²/d, sea level m, κ dimensionless.'))
    A(('table', ['Setting', 'Design', 'Recharge r', 'Inflow qL', 'Sea level η', 'Coefficient κ'], t9,
       [2.4, 2.4, 3.05, 3.05, 3.05, 3.05], 9))
    A(('p', f'**T10: the floor of κ and the value of a rain gauge.** Figure {{{{floor}}}}. With the product the guaranteed '
            f'half-width of $\\kappa$ goes from {kap["aware_r2"][0]:.3f} with rain only to {kap["aware_r2"][-1]:.3f} with '
            f'eight loggers and approaches the floor {floor:.3f} of Proposition R1 (the floor bounds the exact posterior; '
            f'the guaranteed band of a finite ensemble sits a little above it), while the coefficient the heads can see, '
            f'$c=\\kappa b$, shrinks to {keff[-1]:.3f}, as with exact rain ({kap["exact"][-1]:.3f}). A local gauge, '
            f'with its 5% bias, lowers the floor and gives $\\kappa$ to {kap["gauge"][-1]:.3f}. For the recharge the '
            f'product costs a factor {rr["aware"][-1] / rr["exact"][-1]:.1f} in guaranteed width with eight loggers '
            f'({rr["aware"][-1]:.3f} against {rr["exact"][-1]:.3f} mm/d); the R2 prior recovers part of it '
            f'({rr["aware_r2"][-1]:.3f}; with one logger it also cuts the inflow band from '
            f'{R["aware"]["1 logger"]["qL"]["halfwidth"]:.2f} to {R["aware_r2"]["1 logger"]["qL"]["halfwidth"]:.2f} m²/d), '
            f'the gauge almost all ({rr["gauge"][-1]:.3f}). At equal numbers of loggers the '
            f'gauge gives the narrower band for every goal, and for $\\kappa$ the product with eight loggers does not '
            f'reach what the gauge gives with one ({kap["gauge"][1]:.3f}).'))
    A(('img', 'floor', 17.0))
    A(('cap', 'Figure {{floor}}. T10: guaranteed 90% half-width of $\\kappa$ (left) and of the recharge (right) against '
              'the number of loggers; dotted, the floor of Proposition R1; dashed, the coefficient $c=\\kappa b$ that the '
              'heads see.'))
    A(('p', f'**T11: the filter law.** Figure {{{{filter}}}}. For 300 rain records of the rain law, the variance of the '
            f'weekly filtered error measured over 200 draws of daily errors matches $v/n_{{eff}}$ with a median relative '
            f'difference of {100 * np.median(rel):.1f}% (largest {100 * np.max(rel):.1f}%, Monte Carlo error). The '
            f'effective number of rain days averages {np.mean(neff):.1f} ({np.percentile(neff, 10):.1f}–'
            f'{np.percentile(neff, 90):.1f} over the records), far from the {F["four_tau"] + 1:.0f} of steady rain: rain '
            f'comes in few events, so the unsaturated zone averages few errors. A product with daily relative error '
            f'{100 * np.sqrt(F["daily_rel_var"]):.0f}% leaves about {100 * np.sqrt(np.mean(pred)):.0f}% in the weekly '
            f'forcing; its bias stays whole.'))
    A(('img', 'filter', 17.0))
    A(('cap', 'Figure {{filter}}. T11: left, measured against predicted relative variance of the weekly filtered product '
              'error, one point per rain record; right, the effective number of rain days $n_{eff}$ of Proposition R2.'))
    A(('h2', '4.4 What to do when the only rain is a product'))
    A(('b', '**Never calibrate as if the product were exact.** With heads, every guarantee collapses (T9).'))
    A(('b', '**Put the product\'s error law in the simulated aquifers** (Proposition R3), and the filtered-error covariance '
            'of Proposition R2 in the recharge prior; both need only the product and an estimate of its bias and daily '
            'skill.'))
    A(('b', '**Report $c=\\kappa b$, not $\\kappa$,** unless the rain is measured on site: $\\kappa$ alone has the floor '
            '[[floor]] whatever the number of heads, and a rain bias is invisible to every head-based check.'))
    A(('b', '**Buy a rain gauge first.** In T10 a gauge and one logger give $\\kappa$ more narrowly than the product '
            'with eight loggers, and at equal loggers the gauge gives the narrower band for every goal; with MATJA-GO '
            '(review II) its value is computed like that of any instrument.'))
    A(('b', '**For Fushë-Kuqe**, estimate $s_b$ and $v$ by comparing the product (ERA5-Land, E-OBS or IMERG) with the '
            'nearest station over the common period: ==to be computed with the station record==.'))
    # ------------------------------------------------------------------------------------------- 5 synthesis
    A(('h', '5. Synthesis: sixty papers in one procedure'))
    A(('p', 'Table {{sixty}} places the sixty papers of reviews I–III on the steps of the procedure (review I, Section '
            '5.2). Card numbers carry the review: I-O1 is card O1 of review I, III-C2 card C2 of this review. The '
            'reading is simple: reviews I and II are strong on inversion, guarantees and design; this review fills the '
            'first step, the prior from the rain, which every guarantee depends on.'))
    rows = []
    sets = (('I', cards_gar.CARDS), ('II', cards_matja.CARDS), ('III', CARDS))
    for key, lab_ in STEPS:
        row = [lab_]
        for rv, cs in sets:
            ids = [c['id'] for c in cs if key in c['steps']]
            row.append(', '.join(f'{rv}-{i}' for i in ids) if ids else '–')
        rows.append(row)
    A(('cap', 'Table {{sixty}}. The sixty papers of reviews I–III against the steps of the procedure (a paper can serve '
              'several steps).'))
    A(('table', ['Step', 'Review I', 'Review II', 'Review III'], rows, [3.0, 4.6, 4.7, 4.7], 9))
    A(('p', '**Order of work for a site known only through a rain product.** (1) Estimate the product\'s bias and daily '
            'skill against any station, and build the simulated aquifers with them (RESHJA-GO). (2) Calibrate the '
            'guaranteed bands on those aquifers (GARANCIA-GO). (3) Choose the next instrument by the guaranteed width it '
            'removes, the rain gauge among the candidates (MATJA-GO). (4) Recalibrate the chosen design on fresh '
            'aquifers, and check the prior against the field with the heads, knowing that a rain bias will not show.'))
    A(('p', f'Three tools of the earlier reviews carry over unchanged: weighted conformal prediction when the rain law of '
            f'the calibration and of the field drift apart ({L("S1", "S1")}), risk-controlling sets for a guarantee per '
            f'calibration set ({L("S2", "S2")}), and ensemble Kalman methods as the reconstructor that the simulated '
            f'aquifers calibrate ({L("S3", "S3")}).'))
    # ------------------------------------------------------------------------------------------- 6 limitations
    A(('h', '6. Limitations'))
    A(('b', 'Every card is partly verified: landing pages were reached through search results only and no full text was '
            'read.'))
    A(('b', 'The rain-error law is simple: one bias for the record and independent daily errors. Real products also have '
            'timing errors, missed and false events and errors that depend on intensity; the guarantee of Proposition R3 '
            'holds for whatever law is simulated, so the law must be estimated, not assumed.'))
    A(('b', 'Proposition R1 is exact without daily errors; with them the floor holds approximately (T10).'))
    A(('b', 'The test bed is linear and one-dimensional, as in reviews I and II.'))
    return B
