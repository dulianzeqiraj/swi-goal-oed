"""Text of the eighth state-of-the-art review (English), with a three-page summary of novelty at the end.
blocks(AJ) returns the block list; every number comes from res/kripa.json. Conventions: $inline math$, **bold**,
*italic*, ==yellow placeholder==, [text](url) hyperlink, [[key]] equation number, {{key}} figure or table number."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for k_, d_ in enumerate(('garancia_go', 'matja_go', 'reshja_go', 'ankora_go', 'prirja_go', 'dyshemeja_go',
                         'shkaku_go')):
    sys.path.insert(k_, os.path.join(HERE, '..', d_))
sys.path.insert(0, HERE)
from cards_kripa import CARDS, INST_ORDER, SOTA_ROWS  # noqa: E402
import cards_gar  # noqa: E402
import cards_matja  # noqa: E402
import cards_reshja  # noqa: E402
import cards_ankora  # noqa: E402
import cards_prirja  # noqa: E402
import cards_dyshemeja  # noqa: E402
import cards_shkaku  # noqa: E402

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
    dict(key='D1', text='Zeqiraj, D. (2026). Reviews I–VII of this series (GARANCIA-GO, MATJA-GO, RESHJA-GO, ANKORA-GO, '
                        'PRIRJA-GO, DYSHEMEJA-GO, SHKAKU-GO), docs/literature/ in this repository.', url=None),
    dict(key='D2', text='Zeqiraj, D. (in preparation). From sparse hydrochemistry to decision-relevant information: '
                        'probabilistic chloride mapping and goal-oriented monitoring design for seawater intrusion in the '
                        'Fushë-Kuqe coastal aquifer, Albania; the areal chloride model and its calibration ensemble '
                        '(chloride_fk/ in this repository).', url=None),
    dict(key='D3', text='Zeqiraj, D. (2026). Journal of Hydrology 680, 136559 (the companion study of the chloride model; '
                        'facies-conditional conductivity prior).', url=None),
    dict(key='D4', text='Cenameri, M., & Beqiraj, A. (2016). Documented seawater-intrusion facts and hydrochemical '
                        'analyses of the Fushë-Kuqe–Lezhë sector, as compiled in the project workbook (sheets 5 and 7).',
         url=None),
    dict(key='D5', text='The code of this review: experiments/kripa_go/ (with chloride_fk/python/).', url=None),
]


def card_ref(c):
    return dict(key=c['id'], text=f"{c['authors']} ({c['year']}). {c['title']}. {c['venue']}.", url=c['links'][0][1])


def all_refs():
    return ANCHORS + [card_ref(c) for c in CARDS] + SYN + OTHER


def rng_(xs, d=2):
    a, b = f'{min(xs):.{d}f}', f'{max(xs):.{d}f}'
    return a if a == b else f'{a}–{b}'


STEPS = (('prior', 'prior from rain'), ('emulate', 'emulate'), ('invert', 'invert'), ('guarantee', 'guarantee'),
         ('check', 'field check'), ('design', 'design, operate'))
GN = dict(A='shallow salinized area', T='toe area', F='mid-depth seawater fraction')
GU = dict(A='km²', T='km²', F='points')


def sci(x):
    """1.5e-11 -> 1.5×10⁻¹¹"""
    m, e = f'{x:.1e}'.split('e')
    sup = str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹')
    return f'{m}×10{str(int(e)).translate(sup)}'


def fill_numbers(AJ):
    G = AJ['T26']['goals']; D = AJ['T26']['dose']; C = AJ['T27']; T8 = AJ['T28']
    f = {}
    for g in 'ATF':
        e = G[g]
        for k in ('factual_post', 'cf_post', 'eff_post', 'eff_prior'):
            for q in ('med', 'lo', 'hi'):
                f[f'{g}_{k}_{q}'] = e[k][q]
        f[f'{g}_cp_lo'], f[f'{g}_cp_hi'] = C[g]['s']['real_conformal']
        f[f'{g}_share_w'] = T8['share'][g]['w']['post']
        f[f'{g}_share_R'] = T8['share'][g]['R']['post']
        f[f'{g}_share_LB'] = T8['share'][g]['L_B']['post']
        f[f'{g}_wlow'] = T8['w_cond'][g]['low']['med']; f[f'{g}_whigh'] = T8['w_cond'][g]['high']['med']
        for b in ('0', '0.25', '0.5'):
            f[f'{g}_beta{b}'] = T8['beta'][g][b]['med']
            f[f'{g}_beta{b}_hi'] = T8['beta'][g][b]['hi']
        wid = {s: T8['subsets'][s][g]['hi'] - T8['subsets'][s][g]['lo'] for s in T8['subsets']}
        f[f'{g}_r_heads'] = wid['heads'] / wid['none']; f[f'{g}_r_chl'] = wid['chloride'] / wid['none']
        f[f'{g}_r_all'] = wid['all'] / wid['none']
        f[f'{g}_dose05'] = D[g]['0.5']['post']['med']; f[f'{g}_dose15'] = D[g]['1.5']['post']['med']
        f[f'{g}_dose12'] = D[g]['1.2']['post']['med']
    f['cov_is'] = [C[g][k]['cover_is'] for g in 'ATF' for k in ('s', 'cf')]
    f['cov_cp'] = [C[g][k]['cover_conformal'] for g in 'ATF' for k in ('s', 'cf')]
    f['map_f'], f['map_cf'] = AJ['maps']['area_p50_fact'], AJ['maps']['area_p50_cf']
    f['phi_rel'], f['zeta_h'] = AJ['T25']['phi_rel'], AJ['T25']['zeta_from_heads_m']
    f['ess'] = AJ['ess_real']
    f['w_post'] = T8['subsets']['all']['w']; f['w_heads'] = T8['subsets']['heads']['w']
    f['w_prior'] = T8['subsets']['none']['w']
    # strings for the cards
    s = {}
    s['dA'] = f'{f["A_eff_post_med"]:.0f} km² (90% band {f["A_cp_lo"]:.0f}–{f["A_cp_hi"]:.0f})'
    s['dA_med'] = f'{f["A_eff_post_med"]:.0f}'
    s['A_fact'] = f'{f["A_factual_post_med"]:.0f}'; s['A_cf'] = f'{f["A_cf_post_med"]:.0f}'
    s['dT'] = f'{f["T_eff_post_med"]:.0f} km² ({f["T_cp_lo"]:.0f}–{f["T_cp_hi"]:.0f})'
    s['dF'] = f'{f["F_eff_post_med"]:.0f} points ({f["F_cp_lo"]:.0f}–{f["F_cp_hi"]:.0f})'
    s['share_wA'] = f'{100 * f["A_share_w"]:.0f}%'; s['share_wF'] = f'{100 * f["F_share_w"]:.0f}%'
    s['share_LB'] = f'{100 * f["T_share_LB"]:.0f}%'
    s['wlowA'] = f'{f["A_wlow"]:.0f}'; s['whighA'] = f'{f["A_whigh"]:.0f}'
    s['wlowF'] = f'{f["F_wlow"]:.0f}'; s['whighF'] = f'{f["F_whigh"]:.0f}'
    s['beta05'] = f'{f["A_beta0.5"]:.0f}'; s['beta025'] = f'{f["A_beta0.25"]:.0f}'
    s['rheads'] = f'{f["A_r_heads"]:.2f}'; s['rchl'] = f'{f["A_r_chl"]:.2f}'
    s['cov_cp'] = rng_(f['cov_cp'], 3); s['cov_is'] = rng_(f['cov_is'], 3)
    s['map_f'] = f'{f["map_f"]:.0f}'; s['map_cf'] = f'{f["map_cf"]:.0f}'
    s['zeta_h'] = sci(f['zeta_h'])
    s['dose15'] = f'{-f["A_dose15"]:.0f}'; s['dose05'] = f'{f["A_dose05"]:.0f}'
    s['A_cp_hi'] = f'{f["A_cp_hi"]:.0f}'
    s['va'] = f'{(f["A_eff_prior_hi"] - f["A_eff_prior_lo"]) / (f["A_cp_hi"] - f["A_cp_lo"]):.1f}'
    return f, s


def blocks(AJ):
    f, s = fill_numbers(AJ)
    G = AJ['T26']['goals']; T27 = AJ['T27']; T28 = AJ['T28']
    B = []
    A = B.append
    A(('title', 'State of the art VIII: what the salt would have done'))
    A(('subtitle', 'Twenty more papers from Oxford, Caltech, Berkeley and MIT (2022–2026) on dispersion and mixing, '
                   'counterfactuals in nonlinear systems, calibrated simulation-based inference and coastal aquifers '
                   'under climate scenarios; the state of the art and the step beyond it; KRIPA-GO, the counterfactual '
                   'salinity of the Fushë-Kuqe aquifer under a drier recharge regime and the role of the dispersion '
                   'coefficient; and a three-page summary of novelty'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation on the real Fushë-Kuqe '
                 'chloride model · companion to reviews I–VII'))
    # ------------------------------------------------------------------------------------------ 1 outcome
    A(('h', '1. Outcome'))
    A(('bbox', [
        '**Twenty new papers, five per institution, all from 2022–2026, each with links** (Section 3, Figure {{map}}), '
        'none of them a card of reviews I–VII. This batch turns to the nonlinear, salinity side of the problem and to '
        'the dispersion coefficient, the unknown the earlier reviews left open.',
        '**State of the art and beyond, for the proposal** (Section 2, Table {{sotab}}), a map of the one hundred and '
        'sixty papers of reviews I–VIII (Section 5) and a **three-page summary of novelty** (Section 7).',
        f'**Innovation: KRIPA-GO** (Section 4), on the real chloride model of Fushë-Kuqe (D2) and the documented facts. '
        f'Proposition L1: the potential is linear in the recharge, so the aquifer under a drier regime follows from the '
        f'factual state alone — even from the factual heads alone (checked to {s["zeta_h"]} m) — without the '
        f'conductivity or the recharge. Proposition L2: a drier regime never shrinks the salinized area, and the '
        f'dispersion width enters the salinity counterfactual but not the interface one. Proposition L3: whether the '
        f'transition zone itself would widen in the drier world is a cross-world question that no factual data answer. '
        f'Proposition L4: conformal calibration on simulated twins gives the counterfactual bands a guarantee.',
        f'**The Fushë-Kuqe counterfactual** (T26). With 40% less recharge the shallow area above 250 mg/L chloride would '
        f'have been {s["A_cf"]} km² instead of {s["A_fact"]} km² (posterior medians): an increase of {s["dA"]} km². The '
        f'toe of the wedge would have advanced over {s["dT"]}, and the mid-depth seawater fraction of the SW band would '
        f'have risen by {s["dF"]}.',
        f'**The dispersion coefficient decides the salinity counterfactual** (T28). The width $w$ carries {s["share_wA"]} '
        f'of the posterior variance of the area effect and {s["share_wF"]} of the fraction effect; the heads add nothing '
        f'(width ratio {s["rheads"]}), the chloride facts halve it. If the transition zone widened as $c^{{-1/2}}$ in the '
        f'drier world, the area effect would be {s["beta05"]} km² instead of {s["dA_med"]} km².',
        f'**Guarantee** (T27). On 300 simulated test data sets the conformal bands cover {s["cov_cp"]} for the six '
        f'counterfactual goals (importance sampling alone {s["cov_is"]}).']))
    # ------------------------------------------------------------------------------------------ 2 SOTA
    A(('h', '2. State of the art and the step beyond it'))
    A(('p', 'Reviews I–VII (D1) guarantee bands for the boundary conditions, the recharge coefficient and the inputs of '
            'a coastal aquifer when only the rain is known, measure their distance from the narrowest possible band, '
            'and, in review VII, extend the guarantees to counterfactuals of the recharge and the heads. Two gaps '
            'remained. All counterfactuals so far lived in a linear test bed, where effects are free of the latent '
            'boundaries; the quantity that matters at Fushë-Kuqe — where the chloride exceeds 250 mg/L — is nonlinear in '
            'the state. And the dispersion coefficient, one of the three families of unknowns of the whole series, had '
            'no counterfactual role yet.'))
    A(('p', '**Text for the proposal.** Mixing and dispersion in porous media, counterfactual attribution in nonlinear '
            'Earth systems and calibrated simulation-based inference have advanced rapidly (Section 3), but they meet '
            'rarely: attribution studies give no coverage, inference studies ask no counterfactual question, and '
            'dispersion studies do not say how the width of the mixing zone changes a scenario\'s answer. The project '
            'goes beyond the state of the art by computing, for the real Fushë-Kuqe aquifer, what the salinized area, the '
            'toe of the wedge and the seawater fraction of the wells would have been under a drier or a wetter recharge '
            'regime, with conformal guarantees (KRIPA-GO); by proving that this counterfactual needs the factual state '
            'but neither the conductivity nor the recharge; by measuring how much of its uncertainty is the dispersion '
            'coefficient, and which data can reduce it; and by naming the one cross-world assumption about dispersion '
            'that no data can test.'))
    A(('cap', 'Table {{sotab}}. State of the art (2022–2026) and the step beyond it. Card numbers refer to Section 3; T '
              'numbers to the tests of Section 4.'))
    A(('table', ['Topic', 'State of the art', 'Its limit for our problem', 'Our step beyond', 'Evidence'],
       SOTA_ROWS(AJ, f, s), [2.6, 3.9, 3.2, 3.8, 3.5], 9, False))
    # ------------------------------------------------------------------------------------------ 3 papers
    A(('h', '3. The twenty papers'))
    A(('p', 'Five papers per institution, all published 2022–2026 in the version cited (Figure {{map}}), with a link to '
            'the institution at the time of publication (JPL for Caltech, Lawrence Berkeley National Laboratory for '
            'Berkeley), a state-of-the-art contribution and no paper that was a card before. Each card states the main '
            'result as the search results quote or closely paraphrase it, what it cannot yet do for us, three lessons '
            '(inputs, dispersion, boundary conditions) and an innovation step tied to the numbers of Section 4.'))
    A(('p', '**Verification.** The hosts doi.org, arxiv.org, jmlr.org, proceedings.mlr.press, proceedings.neurips.cc and '
            'most publisher pages could not be opened in this environment; landing pages were reached through search '
            'results that quote them, and every card is marked partly verified, with what could not be confirmed.'))
    names_i = dict(Oxford='University of Oxford', Caltech='California Institute of Technology (with JPL)',
                   Berkeley='University of California, Berkeley (with Lawrence Berkeley National Laboratory)',
                   MIT='Massachusetts Institute of Technology')

    def filled(c):
        c = dict(c)
        for k_, v_ in c.items():
            if isinstance(v_, str) and '<<' in v_:
                for key_, val_ in s.items():
                    v_ = v_.replace(f'<<{key_}>>', val_)
                assert '<<' not in v_, (c['id'], v_)
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
    # ------------------------------------------------------------------------------------------ 4 KRIPA-GO
    A(('h', '4. Innovation: KRIPA-GO, the salt counterfactual'))
    A(('h2', '4.1 The aquifer and its twin'))
    A(('p', 'The areal chloride model of Fushë-Kuqe (D2, D3; 3545 active cells of 250 m in the coastal sector) is steady: '
            'the Strack potential $\\phi$ solves a Poisson problem with conductivity $K$ and recharge $R$, the sharp '
            'interface $\\zeta$ follows from $\\phi$ in two zones, and the chloride of a well screen is the screen '
            'average of a transition zone of width $w$, the dispersion coefficient of the model:'))
    A(('eq', 'pde', ['\\nabla\\cdot(K\\nabla\\phi)+R=0,\\qquad\\phi=0\\ \\text{at the shore},',
                     '\\zeta=d+\\sqrt{2\\phi/\\delta}\\ \\ \\text{if}\\ \\phi<\\delta B^2/2,\\qquad\\zeta=\\phi/(\\delta B)+'
                     'd+B/2\\ \\ \\text{otherwise},',
                     'Cl=Cl_f+(Cl_s-Cl_f)\\,\\frac{1}{z_2-z_1}\\int_{z_1}^{z_2}\\Phi\\left(\\frac{z-\\zeta}{w}\\right)dz.']))
    A(('p', f'$d$ is the depth of the aquifer top, $B$ the thickness, $\\delta$ = 0.025 the density contrast and $\\Phi$ '
            f'the standard normal distribution function. The unknowns are a facies-conditional conductivity field (12 '
            f'zones and a scale $\\eta$), $R$, three thickness parameters, a ground offset, $w$ and the seawater chloride; '
            f'the calibration ensemble holds {AJ["N"]} prior draws, and the four documented facts (shallow salinized '
            f'area, littoral head, mid-depth seawater fraction, NE chloride bound; D4) weight them (effective sample size '
            f'{f["ess"]:.0f}). The twin aquifer has the same conductivity, geometry and seawater, a recharge $cR$ '
            f'($c$ = 0.6 for a 40% drier regime; $c$ from 0.5 to 1.5 for the dose-response, $c>1$ standing for managed '
            f'recharge) and a transition-zone width $w\'$:'))
    A(('eq', 'twin', ["\\phi'=c\\,\\phi,\\qquad\\zeta'=\\zeta(\\phi'),\\qquad Cl'=Cl(\\zeta',w'),\\qquad w'=w\\ "
                      "\\text{shared, or}\\ w'=w\\,c^{-\\beta}."]))
    A(('p', 'The goals are the shallow area with chloride above 250 mg/L, the area of the wedge toe and the median '
            'seawater fraction of the mid-depth screens of the SW band, in the factual and the twin aquifer, and their '
            'differences (the effects). The factual heads also determine the potential, by inverting the state map:'))
    A(('eq', 'heads', ['\\phi=\\frac{(h-\\delta d)^2}{2\\delta}\\ \\ \\text{if}\\ h<\\delta(d+B),\\qquad\\phi=B\\,(h-\\delta'
                       '(d+B/2))\\ \\ \\text{otherwise}.']))
    A(('img', 'scheme', 17.0))
    A(('cap', f'Figure {{{{scheme}}}}. Left: the twin wedge in a schematic section; the interface of the drier aquifer is '
              f'$\\sqrt{{c}}$ times as deep below the aquifer top (Proposition L1) and the shading, set by the dispersion '
              f'$w$, decides how much of the shallow screens it salts (Proposition L2). Right: the posterior probability '
              f'that the shallow chloride exceeds 250 mg/L at Fushë-Kuqe given the documented facts, in the factual aquifer '
              f'and with 40% less recharge ({NMAP_TXT} posterior draws); the area with probability above one half grows '
              f'from {s["map_f"]} to {s["map_cf"]} km².'))
    A(('h2', '4.2 Guarantees'))
    A(('prop', 'Proposition L1 (state abduction).',
            'For every conductivity field and geometry, the potential of the aquifer with recharge $cR$ is $c\\phi$. '
            'Hence the twin interface, heads and chloride are functions of the factual potential, the geometry, $c$ and '
            '$w\'$; by [[heads]] they are functions of the factual heads and the geometry alone, without $K$ or $R$. In '
            'the inner zone, $\\zeta\'-d=\\sqrt{c}\\,(\\zeta-d)$.'))
    A(('proof', 'The discretised problem is $A(K)\\phi=R\\,a$ with $a$ the cell areas; the shore condition and the Robin '
                'link to the sea are homogeneous, so $A(K)(c\\phi)=cR\\,a$ and the solution is unique. The state map '
                '$\\phi\\mapsto(h,\\zeta)$ is continuous and strictly increasing in each cell (both branches agree at '
                '$\\phi=\\delta B^2/2$), so it can be inverted from $h$, which gives [[heads]]. For $c<1$ an inner-zone '
                'cell stays in the inner zone and $\\zeta\'-d=\\sqrt{2c\\phi/\\delta}=\\sqrt{c}(\\zeta-d)$.'))
    A(('prop', 'Proposition L2 (monotone salt; where the dispersion enters).',
            'For $c<1$ and $w\'=w$: (i) $\\zeta\'\\le\\zeta$ in every cell and the chloride of every screen rises, so the '
            'salinized area and the toe area cannot shrink, for every value of the unknowns — the probability that the '
            'drier regime increased the salt is one, and the probabilities of necessity and sufficiency of the '
            'counterfactual are identified; (ii) the toe area depends on $\\zeta\'$ only, so its counterfactual is free '
            'of $w$, while the chloride and the salinized area depend on $w$; (iii) the heads carry no information on '
            '$w$, which only chloride facts can reduce.'))
    A(('proof', '(i) $\\zeta(\\phi)$ is nondecreasing (Proposition L1) and $c\\phi\\le\\phi$; the screen average of '
                '$\\Phi((z-\\zeta)/w)$ decreases in $\\zeta$, because $\\Phi$ decreases in $\\zeta$ for every $z$. (ii) '
                'The toe is where $\\zeta<d+B$. (iii) The heads are functions of $\\phi$ and the geometry [[heads]], and $w$ '
                'enters neither $\\phi$ nor the geometry; under the prior $w$ is independent of them (review I found the '
                'rank correlation of $w$ with the littoral head to be 0.00).'))
    A(('prop', 'Proposition L3 (dispersion across worlds is not identified).',
            'Every factual quantity depends on $w$ and not on $w\'$; the counterfactual chloride depends on $w\'$. So the '
            'joint law of $(w,w\')$ is not identified by any factual data, however many: a counterfactual salinity band '
            'must state its assumption on $w\'$ (shared, or a law such as $w\'=w\\,c^{-\\beta}$).'))
    A(('proof', 'The factual model [[pde]] involves $w$ only; the twin [[twin]] involves $w\'$. Any coupling of $w\'$ to '
                '$w$ leaves the factual law unchanged (review VII, Proposition K3, for the recharge noise).'))
    A(('prop', 'Proposition L4 (guaranteed counterfactual bands).',
            'Let data sets be simulated from the prior ensemble, let $m$ and $s$ be the importance-weighted posterior mean '
            'and sd of a counterfactual goal computed without the simulated truth, and let $q$ be the '
            '$\\lceil(n+1)(1-\\alpha)\\rceil$-th smallest of $n$ calibration scores $|x-m|/s$. Under the model, including '
            'its assumption on $w\'$, the band $m\\pm qs$ covers the counterfactual goal of a new data set with '
            'probability at least $1-\\alpha$.'))
    A(('proof', 'The scores of the calibration sets and of the new set are exchangeable under the model; split conformal '
                'prediction (A2). The guarantee inherits the mechanism, as in review VII (Proposition K4).'))
    A(('box', ['**What is new.** (1) Counterfactual salinity for a real coastal aquifer — salinized area, toe, seawater '
               'fraction of wells — under drier and wetter recharge regimes, with conformal guarantees. (2) State '
               'abduction: the drier aquifer follows from the factual state, even from the factual heads alone, '
               'without the conductivity or the recharge (Proposition L1). (3) A monotone salt response that identifies '
               'the probabilities of causation (Proposition L2). (4) The first measurement of how much of a salinity '
               'counterfactual is the dispersion coefficient, and which data reduce it (T28). (5) The cross-world '
               'dispersion assumption made explicit and priced (Proposition L3). To our knowledge none of these appears in '
               'the one hundred and sixty papers of reviews I–VIII.']))
    # ------------------------------------------------------------------------------------------ 4.3 tests
    A(('h2', '4.3 Tests'))
    A(('p', f'**T25: exactness of state abduction.** Over 200 draws the re-solved twin potential differs from $c\\phi$ by '
            f'at most {sci(f["phi_rel"])} of its maximum, and the twin interface computed from the factual heads alone '
            f'[[heads]] differs from the re-solved one by at most {sci(f["zeta_h"])} m. Over all {AJ["N"]} draws, every cell '
            f'and every $c<1$, the shallow chloride never fell (smallest change {AJ["monotone_min_dCl"]:.0f} mg/L), as '
            f'Proposition L2 requires.'))
    A(('p', f'**T26: the Fushë-Kuqe counterfactual.** Table {{{{t26}}}} and Figure {{{{dose}}}}. With the documented facts, '
            f'the shallow salinized area is {s["A_fact"]} km² (posterior median; 90% band '
            f'{f["A_factual_post_lo"]:.0f}–{f["A_factual_post_hi"]:.0f}); with 40% less recharge it would have been '
            f'{s["A_cf"]} km², an effect of {s["dA"]} km² after the conformal correction. Without the facts (the '
            f'interventional answer) the effect band is {f["A_eff_prior_lo"]:.0f}–{f["A_eff_prior_hi"]:.0f} km², '
            f'{s["va"]} times wider: the value of abduction of the four facts. The toe would have advanced over {s["dT"]} '
            f'and the mid-depth seawater fraction of the SW band would have risen by {s["dF"]}. The dose-response is '
            f'smooth and asymmetric: half the recharge adds {s["dose05"]} km² of salinized area, while 50% more recharge '
            f'(a managed-recharge regime) removes {s["dose15"]} km².'))
    rows = []
    for g in 'ATF':
        e = G[g]
        rows.append([f'**{GN[g]}** ({GU[g]})', f'{e["factual_post"]["med"]:.1f} ({e["factual_post"]["lo"]:.1f}–'
                     f'{e["factual_post"]["hi"]:.1f})', f'{e["cf_post"]["med"]:.1f} ({e["cf_post"]["lo"]:.1f}–'
                     f'{e["cf_post"]["hi"]:.1f})', f'{e["eff_prior"]["med"]:.1f} ({e["eff_prior"]["lo"]:.1f}–'
                     f'{e["eff_prior"]["hi"]:.1f})', f'{e["eff_post"]["med"]:.1f} ({f[g + "_cp_lo"]:.1f}–'
                     f'{f[g + "_cp_hi"]:.1f})'])
    A(('cap', 'Table {{t26}}. T26: Fushë-Kuqe with the documented facts. Posterior median and 90% band of the factual '
              'and the counterfactual goal (40% less recharge, shared dispersion); the effect without facts (prior, '
              'interventional) and with the facts (conformal band, T27).'))
    A(('table', ['Goal', 'Factual', 'Counterfactual', 'Effect, no facts', 'Effect, facts (conformal)'], rows,
       [4.2, 3.2, 3.2, 3.2, 3.2], 9))
    A(('img', 'dose', 17.0))
    A(('cap', 'Figure {{dose}}. T26: the effect of a recharge factor $c$ on the three goals (median and 90% band); orange '
              'without the facts (interventional), blue with them (counterfactual). The dotted line marks the 40% drier '
              'regime of Table {{t26}}; $c>1$ is a wetter or managed-recharge regime.'))
    A(('p', f'**T27: coverage.** Figure {{{{cover}}}}, left. On 600 data sets simulated from the prior (300 for calibration, '
            f'300 for test) the importance-sampling bands already cover {s["cov_is"]}, and the conformal bands '
            f'{s["cov_cp"]}, for the effects and the counterfactual levels of the three goals; the conformal multipliers '
            f'are {rng_([T27[g]["s"]["q"] for g in "ATF"])} for the effects. The guarantee is model-based: it holds as long '
            f'as the mechanism, including the assumption on $w\'$, is the model\'s.'))
    A(('img', 'cover', 17.0))
    A(('cap', 'Figure {{cover}}. Left, T27: coverage of the 90% bands on 300 simulated test data sets (dashed: 0.90). '
              'Right, T28: the 90% width of the effect with each group of facts, relative to no facts.'))
    A(('p', f'**T28: what the counterfactual depends on.** Figures {{{{cover}}}} (right) and {{{{disp}}}}. The littoral head '
            f'does not narrow the salinity effects (width ratio {f["A_r_heads"]:.2f} for the area, {f["F_r_heads"]:.2f} for '
            f'the fraction); the chloride facts do ({f["A_r_chl"]:.2f} and {f["F_r_chl"]:.2f}). Under the posterior the '
            f'dispersion width $w$ alone carries {s["share_wA"]} of the variance of the area effect and {s["share_wF"]} of '
            f'the fraction effect, the recharge {100 * f["F_share_R"]:.0f}% of the latter; the toe effect is free of $w$ '
            f'(Proposition L2 (ii)) and is set mostly by the thinning length of the aquifer ({s["share_LB"]}). The sign of '
            f'the dispersion\'s influence depends on the goal: a wide transition zone makes the drought salt more of the '
            f'shallow area (effect {s["wlowA"]} km² for the narrowest tenth of $w$, {s["whighA"]} km² for the widest) but '
            f'less of the mid-depth screens ({s["wlowF"]} against {s["whighF"]} points). Finally the cross-world '
            f'assumption: if the transition zone widened in the drier world as $c^{{-1/4}}$ or $c^{{-1/2}}$, the area effect '
            f'would be {s["beta025"]} or {s["beta05"]} km² instead of {s["dA_med"]} km² (Proposition L3), while the toe '
            f'effect would not change.'))
    A(('img', 'disp', 17.0))
    A(('cap', 'Figure {{disp}}. T28: left, first-order shares of the posterior variance of the three effects; right, the '
              'effect on the salinized area for the narrowest and widest tenth of the posterior of $w$, and under three '
              'cross-world laws of the dispersion width (median and 90% band).'))
    A(('h2', '4.4 Using the salt counterfactual at Fushë-Kuqe'))
    A(('b', '**Scenarios without the unknowns that cannot be had:** the drier or the managed-recharge aquifer follows '
            'from the factual state; a good map of the factual heads replaces the conductivity field for the interface '
            'counterfactual (Proposition L1).'))
    A(('b', '**Measure chloride, not heads, for salinity scenarios:** the dispersion width decides most of the salinity '
            'counterfactual and only chloride data inform it (T28); the chloride-sampling design of D2 is the instrument.'))
    A(('b', '**State the dispersion assumption:** report the shared-width band and the widened-width band side by side; '
            'whether the mixing zone would widen under a drier regime is ==to be set with the local hydrogeologists from '
            'the tidal and pumping regime==.'))
    A(('b', '**Toe first:** the toe counterfactual is free of the dispersion and is the robust headline; the salinized '
            'area is the decision quantity and carries the dispersion uncertainty.'))
    # ------------------------------------------------------------------------------------------ 5 synthesis
    A(('h', '5. Synthesis: one hundred and sixty papers in one procedure'))
    A(('p', 'Table {{all}} places the hundred and sixty papers of reviews I–VIII on the steps of the procedure; card '
            'numbers carry the review (VIII-C2 is card C2 of this review).'))
    rows = []
    sets = (('I', cards_gar.CARDS), ('II', cards_matja.CARDS), ('III', cards_reshja.CARDS), ('IV', cards_ankora.CARDS),
            ('V', cards_prirja.CARDS), ('VI', cards_dyshemeja.CARDS), ('VII', cards_shkaku.CARDS), ('VIII', CARDS))
    for key, lab_ in STEPS:
        row = [lab_]
        for rv, cs in sets:
            ids = [c['id'] for c in cs if key in c['steps']]
            row.append(', '.join(ids) if ids else '–')
        rows.append(row)
    A(('cap', 'Table {{all}}. The one hundred and sixty papers of reviews I–VIII against the steps of the procedure (card '
              'numbers of each review; a paper can serve several steps).'))
    A(('table', ['Step', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'], rows,
       [2.2, 1.85, 1.85, 1.85, 1.85, 1.85, 1.85, 1.85, 1.85], 8.6))
    # ------------------------------------------------------------------------------------------ 6 limitations
    A(('h', '6. Limitations'))
    A(('b', 'Every card is partly verified: landing pages, and the exact wording of the results, were reached through '
            'search results only.'))
    A(('b', 'The chloride model is steady: the counterfactual is a regime counterfactual (a long-term drier or wetter '
            'recharge), not a year-by-year one; the transient version needs the variable-density section model.'))
    A(('b', 'The guarantee of Proposition L4 is model-based: it inherits the facies prior, the four facts and their error '
            'model, and the assumption on the cross-world dispersion; field anchors with measured chloride would make it '
            'model-free for the factual part (review IV).'))
    A(('b', 'The width $w$ is one number for the whole sector; a spatially varying dispersion, and its dependence on tides '
            'and pumping, would change the variance shares of T28.'))
    A(('refs',))
    # ------------------------------------------------------------------------------------------ 7 novelty
    novelty_blocks(A, AJ, f, s)
    return B


NMAP_TXT = '1000'


def novelty_blocks(A, AJ, f, s):
    """Section 7: the three-page summary of novelty."""
    A(('pb',))
    A(('h', '7. Summary of novelty'))
    A(('p', '**The step in one paragraph.** The eight reviews of this series turn one question — what can be known, with '
            'a guarantee, about the inputs, the dispersion and the boundary conditions of a coastal aquifer when only the '
            'rain is always known — into a procedure with proofs and tests. Reviews I–VI made the bands valid under '
            'calibration, measurement choice, an uncertain rain, a wrong simulator and a drifting world, and measured '
            'how close they come to the narrowest possible band. Review VII asked what would have happened under '
            'another rain, with a guarantee. This review asks the same of the salt itself, on the real Fushë-Kuqe model, '
            f'and finds that a 40% drier recharge regime would roughly double the salinized area ({s["A_fact"]} → '
            f'{s["A_cf"]} km²), that this answer needs the factual state but not the conductivity, and that the '
            f'dispersion coefficient — the unknown the series had left open — carries most of its uncertainty.'))
    A(('h2', '7.1 What is new in this review'))
    items = [
        ('A salinity counterfactual with a guarantee for a real aquifer',
         f'the drought effect on the salinized area is {s["dA"]} km², on the toe {s["dT"]}, on the seawater fraction of '
         f'the SW wells {s["dF"]} (T26, T27); no attribution study of Section 3 gives a coverage statement.'),
        ('State abduction',
         f'the drier aquifer is $\\phi\'=c\\phi$ of the factual one, and its interface follows from the factual heads alone '
         f'(error {sci(f["zeta_h"])} m): scenario questions no longer need the conductivity field (Proposition L1).'),
        ('Monotone salt and identified probabilities of causation',
         'a drier regime never lowers the chloride of any screen, for any value of the unknowns (Proposition L2; checked '
         'over all draws and cells).'),
        ('The dispersion coefficient, measured inside a counterfactual',
         f'{s["share_wA"]} of the posterior variance of the area effect and {s["share_wF"]} of the fraction effect; the '
         f'sign of its influence differs between the shallow and the mid-depth screens (T28).'),
        ('Which data reduce a salinity counterfactual',
         f'the head facts do not (width ratio {s["rheads"]}), the chloride facts do ({s["rchl"]}); the toe counterfactual '
         f'is free of the dispersion (T28).'),
        ('The cross-world dispersion assumption',
         f'not identified by any factual data (Proposition L3); it moves the area effect from {s["dA_med"]} to up to '
         f'{s["beta05"]} km², and must be reported (T28).'),
        ('Dose-response for planning',
         f'half the recharge adds {s["dose05"]} km² of salinized area; 50% more recharge (managed aquifer recharge) '
         f'removes {s["dose15"]} km² (T26).'),
    ]
    for t, d in items:
        A(('b', f'**{t}:** {d}'))
    A(('h2', '7.2 The novelty that each of the twenty papers brings to our problem'))
    rows = [[c['id'], c['short'], c['novel']] for c in CARDS]
    filled_rows = []
    for r in rows:
        v = r[2]
        for key_, val_ in s.items():
            v = v.replace(f'<<{key_}>>', val_)
        filled_rows.append([r[0], r[1], v])
    A(('cap', 'Table {{nov}}. The step beyond each card of Section 3, in one line.'))
    A(('table', ['Card', 'Paper', 'The step beyond it in this project'], filled_rows, [1.3, 5.2, 10.5], 8.6, False))
    A(('h2', '7.3 Eight reviews, one chain of innovations'))
    chain = [
        ['I', 'GARANCIA-GO', 'Are bands for the boundaries from rain valid?', 'simulation-calibrated conformal risk control',
         'raw ensemble misses 17–20% of weeks; calibrated 0.095–0.100'],
        ['II', 'MATJA-GO', 'What is an instrument worth?', 'the guaranteed value of a measurement',
         'a tide gauge is worth zero for recharge, a factor 14 for sea level'],
        ['III', 'RESHJA-GO', 'What if the rain is uncertain?', 'the rain product\'s errors inside the simulator',
         'κ misses 0.70–0.76 if ignored; risk 0.093–0.103 when modelled'],
        ['IV', 'ANKORA-GO', 'What if the simulator is wrong?', 'a few real anchors',
         'risk ≤ 0.10 under every law; simulation-calibrated up to 0.83'],
        ['V', 'PRIRJA-GO', 'What if the world drifts?', 'horizon-matched anchors',
         'risk 0.003–0.082 up to 10 years under drift'],
        ['VI', 'DYSHEMEJA-GO', 'How narrow can a guarantee be?', 'the Neyman–Pearson floor',
         'the 20-anchor band is 1.34–1.54 times the floor'],
        ['VII', 'SHKAKU-GO', 'What would have happened?', 'guaranteed counterfactual bands',
         'a 40% drought lowers the head at the well by 1.94 m; floor 0.088 m'],
        ['VIII', 'KRIPA-GO', 'What would the salt have done?', 'state abduction and the dispersion counterfactual',
         f'salinized area {s["A_fact"]} → {s["A_cf"]} km²; dispersion {s["share_wA"]} of the effect\'s variance'],
    ]
    A(('cap', 'Table {{chain}}. The innovations of reviews I–VIII (numbers from each review\'s tests).'))
    A(('table', ['', 'Innovation', 'Question', 'New answer', 'Key number'], chain, [1.0, 2.6, 4.0, 4.2, 5.2], 8.6))
    A(('h2', '7.4 What the proposal can now claim, and what stays open'))
    A(('b', '**Claim:** guaranteed bands for every family of unknowns — inputs, boundary conditions and, through the '
            'chloride facts, the dispersion width — from rain and a few heads, valid under a wrong simulator, an '
            'uncertain rain and drift, with their distance from the best possible band known.'))
    A(('b', '**Claim:** guaranteed answers to scenario questions — how the heads, the recharge and the salinized area '
            'would have differed under a drier or a managed-recharge regime — together with the assumptions no data can '
            'test, stated and priced.'))
    A(('b', '**Claim:** a design rule: heads for the boundaries and the recharge coefficient, chloride for the dispersion '
            'and the salinity scenarios, anchors for the guarantee in the field.'))
    A(('b', '**Open:** a transient, variable-density counterfactual of the transition zone; a spatially varying and '
            'flow-dependent dispersion; field anchors with measured chloride to make the salinity guarantee model-free.'))
    A(('h2', '7.5 Innovation statement for the proposal'))
    A(('p', f'*Ready to paste.* The project delivers, for the first time for a coastal aquifer, guaranteed answers to '
            f'"what would have happened" questions about its salt. From the rain, a few heads and a handful of chloride '
            f'facts, it computes how the salinized area, the toe of the seawater wedge and the salinity of the wells would '
            f'have differed under a drier or a managed-recharge regime, with bands that cover the truth at the stated '
            f'rate on simulated aquifers ({s["cov_cp"]} for 90% bands). Three results make this possible and are new. '
            f'First, the counterfactual aquifer follows from the observed state alone — the conductivity field and the '
            f'recharge are not needed — so a map of heads is enough for the interface. Second, the salt response to a '
            f'drier regime is monotone, so the direction of the effect is certain and only its size is uncertain. '
            f'Third, the dispersion coefficient is identified as the quantity that decides the size: it carries '
            f'{s["share_wA"]} of the uncertainty of the salinized-area effect, heads cannot reduce it and chloride '
            f'samples can. Applied to Fushë-Kuqe, a 40% drier regime would raise the salinized area from {s["A_fact"]} to '
            f'{s["A_cf"]} km²; managed recharge of +50% would lower it by {s["dose15"]} km². The one assumption no data '
            f'can test — whether the mixing zone itself would widen in the drier world — is stated and priced (up to '
            f'{s["beta05"]} km²), which turns a scientific caveat into a monitoring and design decision.'))
