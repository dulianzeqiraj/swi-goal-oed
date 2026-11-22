"""Text of the seventh state-of-the-art review (English). blocks(AJ, SG) returns the block list; every number comes from
res/shkaku.json (AJ) and res/shkaku_sign.json (SG). Conventions: $inline math$, **bold**, *italic*, ==yellow
placeholder==, [text](url) hyperlink, [[key]] equation number, {{key}} figure or table number."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for k_, d_ in enumerate(('garancia_go', 'matja_go', 'reshja_go', 'ankora_go', 'prirja_go', 'dyshemeja_go')):
    sys.path.insert(k_, os.path.join(HERE, '..', d_))
sys.path.insert(0, HERE)
from cards_shkaku import CARDS, INST_ORDER, SOTA_ROWS  # noqa: E402
import cards_gar  # noqa: E402
import cards_matja  # noqa: E402
import cards_reshja  # noqa: E402
import cards_ankora  # noqa: E402
import cards_prirja  # noqa: E402
import cards_dyshemeja  # noqa: E402

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
                        'docs/literature/ in this repository.', url=None),
    dict(key='D5', text='Zeqiraj, D. (2026). State of the art V: when the world drifts; PRIRJA-GO ("review V"), '
                        'docs/literature/ in this repository.', url=None),
    dict(key='D6', text='Zeqiraj, D. (2026). State of the art VI: how narrow can a guarantee be; DYSHEMEJA-GO ("review '
                        'VI"), docs/literature/ in this repository.', url=None),
    dict(key='D7', text='Internal documents of the project: RINDËRTIMI-GO (test bed and exact posterior); ATRIB-GO '
                        '(probability that a pumping increase was necessary for a salinization event, with twin worlds; '
                        'experiments/atrib_go/); the code of this review in experiments/shkaku_go/.', url=None),
]


def card_ref(c):
    return dict(key=c['id'], text=f"{c['authors']} ({c['year']}). {c['title']}. {c['venue']}.", url=c['links'][0][1])


def all_refs():
    return ANCHORS + [card_ref(c) for c in CARDS] + SYN + OTHER


def rng_(xs, d=2):
    a, b = f'{min(xs):.{d}f}', f'{max(xs):.{d}f}'
    return a if a == b else f'{a}–{b}'


GOALS = ('dr', 'dh', 'rc', 'hc')
GL = dict(dr='recharge effect Δr', dh='head effect Δh', rc='counterfactual recharge r′', hc='counterfactual head h′')
STEPS = (('prior', 'prior from rain'), ('emulate', 'emulate'), ('invert', 'invert'), ('guarantee', 'guarantee'),
         ('check', 'field check'), ('design', 'design, operate'))


def fill_numbers(AJ, SG):
    D = AJ['cf']['drought']
    LT = AJ['cf']['late']
    C = AJ['coupling']
    DS = AJ['designs']

    def r3(v):
        return f'{v:.3f}'
    va = {g: DS['rain only'][g]['floor']['halfwidth'] / DS['4 loggers'][g]['floor']['halfwidth'] for g in GOALS}
    rob_cost = [C['1.0'][g]['robust']['halfwidth'] / C['1.0'][g]['shared']['halfwidth'] for g in GOALS]
    return dict(
        dh_none_anc=r3(D['none']['dh']['anc20']['risk']), dh_delay_anc=r3(D['delay']['dh']['anc20']['risk']),
        dh_delay_T=r3(D['delay']['dh']['T_sims']['risk']), dh_params_anc=r3(D['params']['dh']['anc20']['risk']),
        va_hc4=f'{va["hc"]:.1f}', va_dh4=f'{va["dh"]:.1f}', va_dr4=f'{va["dr"]:.1f}', va_rc4=f'{va["rc"]:.1f}',
        rc_rho0=f'{C["0.0"]["rc"]["floor"]["halfwidth"] / C["1.0"]["rc"]["floor"]["halfwidth"]:.1f}',
        rc_floor1=r3(C['1.0']['rc']['floor']['halfwidth']),
        robust_risk=r3(max(C[rt][g]['robust']['risk'] for rt in C for g in GOALS)),
        robust_cost=rng_(rob_cost),
        anc_none_rng=rng_([D['none'][g]['anc20']['risk'] for g in GOALS], 3),
        anc_delay_eff=rng_([D['delay'][g]['anc20']['risk'] for g in ('dr', 'dh')], 3),
        dh_mean=f'{-SG["drought"]["mean_dh"]:.2f}', dh_floor=r3(D['none']['dh']['floor']['halfwidth']),
        up_dr0=f'{100 * SG["drought"]["0.0"]["up_dr"]:.0f}%', up_dh0=f'{100 * SG["drought"]["0.0"]["up_dh"]:.3f}%',
        late_up_dh=f'{100 * SG["late"]["up_dh"]:.0f}%',
        late_delay_anc=r3(LT['delay']['dh']['anc20']['risk']),
        late_delay_T=rng_([LT['delay'][g]['T_sims']['risk'] for g in GOALS], 3),
        hc_none_anc=r3(D['none']['hc']['anc20']['risk']), hc_params_anc=r3(D['params']['hc']['anc20']['risk']),
        hc_none_ratio=f'{D["none"]["hc"]["anc20"]["halfwidth"] / D["none"]["hc"]["floor"]["halfwidth"]:.2f}')


def blocks(AJ, SG):
    D = AJ['cf']['drought']
    LT = AJ['cf']['late']
    C = AJ['coupling']
    DS = AJ['designs']
    fill = fill_numbers(AJ, SG)

    def ratio(Rg, key):
        return Rg[key]['halfwidth'] / Rg['floor']['halfwidth']

    def col(law, key, goals=GOALS, src=D):
        return [ratio(src[law][g], key) for g in goals]

    def risks(law, key, goals=GOALS, src=D):
        return [src[law][g][key]['risk'] for g in goals]
    names = list(DS.keys())
    va = {n: {g: DS['rain only'][g]['floor']['halfwidth'] / DS[n][g]['floor']['halfwidth'] for g in GOALS}
          for n in names}
    rho_fl = {rt: {g: C[rt][g]['floor']['halfwidth'] / C['1.0'][g]['floor']['halfwidth'] for g in GOALS} for rt in C}
    shared_risk = {rt: [C[rt][g]['shared']['risk'] for g in GOALS] for rt in C}
    right_risk = [C[rt][g]['right']['risk'] for rt in C for g in GOALS]
    rob_risk = [C[rt][g]['robust']['risk'] for rt in C for g in GOALS]
    rob_ratio = {rt: [C[rt][g]['robust']['halfwidth'] / C[rt][g]['floor']['halfwidth'] for g in GOALS] for rt in C}
    sims_delay_bad = all(r > 0.105 for r in risks('delay', 'sims'))
    below = [(s, g, b) for s in D for g in GOALS for b in ('sims', 'anc20', 'T_sims')
             if D[s][g][b]['halfwidth'] < D[s][g]['floor']['halfwidth']]
    below_bad = all(D[s][g][b]['risk'] > 0.105 for s, g, b in below)
    B = []
    A = B.append
    A(('title', 'State of the art VII: what would have happened'))
    A(('subtitle', 'Twenty more papers from Oxford, Caltech, Berkeley and MIT (2022–2026) on stochastic causality, '
                   'counterfactual inference, causal generative models and causal attribution in the Earth system; the '
                   'state of the art and the step beyond it; and SHKAKU-GO, guaranteed counterfactual bands for the '
                   'recharge and the heads of a coastal aquifer when the rain had been different'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation · companion to reviews '
                 'I–VI (GARANCIA-GO, MATJA-GO, RESHJA-GO, ANKORA-GO, PRIRJA-GO, DYSHEMEJA-GO)'))
    # ------------------------------------------------------------------------------------------- 1 outcome
    A(('h', '1. Outcome'))
    A(('bbox', [
        '**Twenty new papers, five per institution, all from 2022–2026, each with links** (Section 3, Figure {{map}}). '
        'None was a card of reviews I–VI, and none appears in the ten causal reviews written earlier for the project. '
        'They cover causal models of stochastic and dynamical systems, counterfactuals with identification theorems, '
        'counterfactual generators and digital twins, and counterfactual attribution of storms, rain, sea level and '
        'land water. Each card gives the main result, the state of the art it sets, what it cannot yet do for us, three '
        'lessons and an innovation step.',
        '**State of the art and beyond, for the proposal** (Section 2, Table {{sotab}}), and a map of all one hundred '
        'and forty papers of reviews I–VII on the steps of the procedure (Section 5, Table {{all}}).',
        '**Innovation: SHKAKU-GO** (Section 4). Reviews I–VI guaranteed bands for what *happened*. This review guarantees '
        'bands for what *would have happened*: the recharge and the head at an unmonitored well in the same 64 weeks had '
        'the rain been 40% lower (or a month later), given the rain and four loggers — Pearl\'s third rung, in the '
        'stochastic structural model of the aquifer. Proposition K1: the effect of the rain is free of every latent '
        'boundary condition, so a band for the recharge coefficient alone becomes a guaranteed band for the whole '
        'effect path. Proposition K2: with rain alone, counterfactual and interventional answers coincide; the value of '
        'abduction is a ratio of floors. Proposition K3: the coupling of the noise across the two worlds is not '
        'identified by any data; a band robust to it exists and has a price. Proposition K4: anchors make '
        'counterfactual guarantees checkable, but only as good as the mechanism.',
        f'**Test without shift** (T21). Every guaranteed band is valid and close to the floor: 20 anchor twins give risk '
        f'{fill["anc_none_rng"]} at {rng_(col("none", "anc20"))} times the floor; 300 simulated twins give '
        f'{rng_(col("none", "sims"))} times the floor. A 40% drought lowers the head at the well by {fill["dh_mean"]} m '
        f'on average; the narrowest valid band for that effect has a half-width of {fill["dh_floor"]} m.',
        f'**Test under shift** (T21). With a 35-day field delay the simulator\'s mechanism is wrong: simulated twins fail '
        f'(risk {rng_(risks("delay", "sims"))}), and so do anchor twins for the effects (risk {fill["anc_delay_eff"]}), '
        f'because anchors cannot see a counterfactual. The enlarged law, with the delay unknown, is valid for all four '
        f'goals (risk {rng_(risks("delay", "T_sims"), 3)}) at {rng_(col("delay", "T_sims"))} times the floor. Under '
        f'shifted parameters the anchor twins stay valid ({rng_(risks("params", "anc20"), 3)}).',
        f'**Value of abduction and price of the coupling** (T22, T23). Four loggers narrow the counterfactual floors '
        f'{rng_([va["4 loggers"][g] for g in GOALS], 1)}-fold against rain alone. If the recharge error is not shared '
        f'by the two worlds, the floors widen up to {max(rho_fl["0.0"].values()):.1f}-fold; the band robust to every '
        f'coupling keeps the risk at most {max(rob_risk):.3f}.']))
    # ------------------------------------------------------------------------------------------- 2 SOTA and beyond
    A(('h', '2. State of the art and the step beyond it'))
    A(('p', 'Reviews I–VI (D1–D6) guarantee bands for the boundary conditions, the recharge coefficient and the inputs '
            'of a coastal aquifer when only the rain is known, and measure how close those bands come to the narrowest '
            'possible one. Every one of those bands answers a question about the world as it was. The questions a '
            'water authority asks after a dry decade are different: how much lower would the heads have been had the '
            'rain been 40% less, or the wet season a month later, *in these same years, with this sea and this inflow*? '
            'That is a counterfactual, the third rung of the causal ladder. It cannot be observed, even in principle, '
            'and the literature gives it either without uncertainty (attribution with a model) or with uncertainty but '
            'no guarantee (ensembles, Bayesian twins).'))
    A(('p', '**Text for the proposal.** Causal inference for stochastic and dynamical systems now identifies '
            'counterfactual paths from impulse responses, abducts latent conditions with deep generative models, and '
            'attributes single storms and seasons with forecast systems (Section 3). None of these gives a guarantee '
            'that the counterfactual lies inside a stated band, and none says which unobserved boundary conditions '
            'matter for a counterfactual and which drop out. The project goes beyond the state of the art by giving '
            'distribution-free counterfactual bands for recharge and heads (SHKAKU-GO); by proving that the effect of '
            'a rain intervention is free of all latent boundary conditions, so that a guarantee on one coefficient '
            'becomes a guarantee on the whole effect path; by measuring the value of abduction of each monitoring '
            'design; and by stating openly the one assumption no data can test — the coupling of the noise across the '
            'two worlds — together with a band that is robust to it.'))
    A(('cap', 'Table {{sotab}}. State of the art (2022–2026) and the step beyond it. Card numbers refer to Section 3; T '
              'numbers to the tests of Section 4.'))
    A(('table', ['Topic', 'State of the art', 'Its limit for our problem', 'Our step beyond', 'Evidence'],
       SOTA_ROWS(AJ, fill), [2.6, 3.9, 3.2, 3.8, 3.5], 9, False))
    # ------------------------------------------------------------------------------------------- 3 the papers
    A(('h', '3. The twenty papers'))
    A(('p', 'Five papers per institution, all published 2022–2026 in the version cited (Figure {{map}}). The rules of '
            'the earlier reviews apply: direct use, a link to the institution at the time of publication (JPL for '
            'Caltech, Lawrence Berkeley National Laboratory for Berkeley), a state-of-the-art contribution and no paper '
            'that was a card before. The searches found that most theorem-level causal papers of the four institutions '
            'from these years are already in the ten causal reviews of the project; the batch therefore mixes theorems '
            '(O2–O5, C2, B1–B4, M1, M4, M5) with high-impact counterfactual attribution in the Earth system (O1, C1, C3, '
            'C4, C5, B5) and counterfactual systems (M2, M3). For Caltech no unused paper on causal generative models '
            'was found.'))
    A(('p', '**Verification.** The hosts doi.org, arxiv.org, jmlr.org, proceedings.mlr.press, proceedings.neurips.cc and '
            'most publisher pages could not be opened in this environment, so the landing pages were reached through '
            'search results that quote them, and every card is marked partly verified; where an author list, a volume '
            'or the wording of a theorem could not be confirmed, the card says so. The journal version of O4 lacks '
            'volume and year, and M4 is forthcoming in its journal.'))
    names_i = dict(Oxford='University of Oxford', Caltech='California Institute of Technology (with JPL)',
                   Berkeley='University of California, Berkeley (with Lawrence Berkeley National Laboratory)',
                   MIT='Massachusetts Institute of Technology')

    def filled(c):
        c = dict(c)
        for k_, v_ in c.items():
            if isinstance(v_, str) and '<<' in v_:
                for key_, val_ in fill.items():
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
    # ------------------------------------------------------------------------------------------- 4 SHKAKU-GO
    A(('h', '4. Innovation: SHKAKU-GO, guaranteed counterfactuals'))
    A(('h2', '4.1 The two worlds'))
    A(('p', 'The test bed of reviews I–VI (D7; 32 cells, 64 weeks, a pumping well at 1.5 km, loggers at 0.25, 1.25, '
            '2.75 and 4.25 km) is a structural causal model. Its exogenous variables are the daily rain $P$, the latent '
            'histories $z$ (sea level $\\eta$, inland inflow $q_L$, recharge error $e$, initial-head perturbation '
            '$\\delta h_0$), the recharge coefficient $\\kappa$ and the vadose delay $\\tau$; the rain is independent '
            'of the rest. Its mechanisms are'))
    A(('eq', 'scm', ['f_\\tau=E_\\tau\\ast P,\\qquad r=\\kappa\\,f_\\tau+e,\\qquad h=G\\,z+\\kappa\\,g(f_\\tau)+c_Q,']))
    A(('p', 'where $E_\\tau$ is the Erlang-2 vadose filter, $G$ the head response to the latent histories, $c_Q$ the '
            'response to the known pumping and $g$ the head response to recharge, including the steady initial head of '
            'the mean recharge. $g$ is linear: $g(f)=K_g f$ with a fixed matrix $K_g$, checked against the solver to '
            '10⁻¹⁴. The question "what if the rain had been $T(P)$?" is answered in a twin world that shares the '
            'histories, $\\kappa$ and $\\tau$:'))
    A(('eq', 'twin', ["f'_\\tau=E_\\tau\\ast T(P),\\qquad r'=\\kappa\\,f'_\\tau+e',\\qquad h'=G\\,z'+\\kappa\\,"
                      "g(f'_\\tau)+c_Q,",
                      "e'=\\rho\\,e+\\sqrt{1-\\rho^2}\\,\\xi,"]))
    A(('p', 'with $z\'$ equal to $z$ except that the recharge error is $e\'$, and $\\xi$ a fresh draw with the law of '
            '$e$. $\\rho=1$ is Pearl\'s shared noise: the unmodelled part of the recharge would have been the same. '
            '$\\rho<1$ says it would have been partly different. The goals are the weekly effects and the weekly '
            'counterfactual levels at the pumping well, where no logger stands:'))
    A(('eq', 'eff', ["\\Delta r=\\kappa\\,(f'_\\tau-f_\\tau)+(e'-e),\\qquad\\Delta h=\\kappa\\,g(f'_\\tau-f_\\tau)+"
                     "G_e\\,(e'-e),\\qquad r'=r+\\Delta r,\\qquad h'=h+\\Delta h,"]))
    A(('p', f'$G_e$ being the head response to the recharge error. Two interventions are tested: a drought '
            f'$T(P)=0.6P$ and a late season, the rain arriving 30 days later. Given the data $y$ the goals are linear in '
            f'the latent Gaussian histories for each $\\kappa$, so their exact counterfactual law under any working law '
            f'is a mixture over a 1201-point grid of $\\log\\kappa$ (49 delays × 1201 for the enlarged law with the delay '
            f'unknown, log-uniform on 7–56 d). Bands are 90% bands with an expected share of weeks outside at most '
            f'$\\alpha$ = 0.10 (review I); the floor $W^*$ is the Neyman–Pearson floor of review VI computed under the '
            f'real law. Methods: the exact counterfactual law under the simulator\'s law $P$ (centre $\\pm\\lambda$ '
            f'sd), with $\\lambda$ calibrated on {AJ["n_sim"]} simulated twins, on 20 anchor twins ({AJ["reps"]} draws; '
            f'Proposition K4), or set on the field cases themselves ("λ known"); and the enlarged law calibrated on '
            f'{AJ["n_sim"]} simulated twins of that law. Real laws as in reviews IV and VI: no shift, a 35-day field '
            f'delay, shifted parameters; {AJ["n_q"]} field cases each.'))
    A(('img', 'scheme', 17.0))
    A(('cap', 'Figure {{scheme}}. Left: the twin network of the aquifer. The rain is intervened on (dashed); the '
              'delay, the recharge coefficient and the histories of sea level, inflow and initial head are shared by '
              'the two worlds; the recharge errors are coupled by $\\rho$. Right: one field case. The factual head at '
              'the well (grey), the head the twin world would have had under a 40% drought (black), the exact '
              'counterfactual band given the rain and four loggers (blue) and the interventional band given the rain '
              'alone (orange), both mean ± 1.645 sd.'))
    A(('h2', '4.2 Guarantees'))
    A(('prop', 'Proposition K1 (the effect is free of the latent boundaries).',
            'Let $\\rho=1$. Then $\\Delta r=\\kappa\\,a^r$ and $\\Delta h=\\kappa\\,a^h$ with $a^r=f\'_\\tau-f_\\tau$ and '
            '$a^h=g(f\'_\\tau-f_\\tau)$: the effect does not depend on the sea level, the inland inflow, the recharge '
            'error or the initial head. Hence (i) its counterfactual law given any data is the push-forward of the '
            'posterior of $(\\kappa,\\tau)$, and for a known $\\tau$ the standardised score of the band '
            '"posterior mean $\\pm\\lambda$ sd" is the same in every week; (ii) if $\\tau$ is known and $C$ is a set for '
            '$\\kappa$ with $\\Pr(\\kappa\\notin C)\\le\\alpha$, then $\\{\\kappa a_w:\\kappa\\in C\\}$ contains the whole '
            'effect path, all weeks at once, with probability at least $1-\\alpha$, for every law of the rain and of '
            'the histories; (iii) with $m$ anchors exchangeable with the field case in which $\\kappa$ was measured, '
            'the conformal set for $\\kappa$ is such a $C$.'))
    A(('proof', 'Subtract [[scm]] from [[twin]]: $c_Q$ cancels, $G z\'-G z=G_e(e\'-e)$ vanishes at $\\rho=1$, and '
                '$\\kappa g(f\'_\\tau)-\\kappa g(f_\\tau)=\\kappa g(f\'_\\tau-f_\\tau)$ because $g$ is linear (its steady '
                'initial head is linear in the mean recharge). (i) The effect is a function of $(\\kappa,\\tau)$; for a '
                'known $\\tau$ its posterior mean and sd in week $w$ are $a_w\\hat\\kappa$ and $|a_w|\\sigma_\\kappa$, so '
                'the score is $|\\kappa-\\hat\\kappa|/\\sigma_\\kappa$. (ii) For each $w$, $\\kappa\\mapsto\\kappa a_w$ '
                'is monotone, so $\\kappa\\in C$ puts every $\\kappa a_w$ in the image. (iii) The conformal guarantee of '
                'an exchangeable sample (A2).'))
    A(('prop', 'Proposition K2 (rain alone gives only the interventional answer).',
            'Because the rain is independent of the other exogenous variables: (i) given the rain alone, the '
            'counterfactual law of every goal equals its interventional law under $do(P:=T(P))$; (ii) for every design, '
            'the floor of the counterfactual band is at most the floor of the interventional band, and their ratio '
            '$V=W^*_{int}/W^*_{cf}\\ge1$ is the *value of abduction* of the design; (iii) for the effects at '
            '$\\rho=1$, abduction acts only through the posterior of $\\kappa$ and $\\tau$.'))
    A(('proof', '(i) Given $P$ alone, the posterior of $(z,\\kappa,\\tau,\\xi)$ is its prior. (ii) The interventional '
                'band uses $P$ only; averaged over $y$, its coverage of the twin goal equals its interventional '
                'coverage, so it is a valid counterfactual procedure, and the floor over all procedures that may also use '
                '$y$ (review VI, F1) is no larger. (iii) Proposition K1 (i).'))
    A(('prop', 'Proposition K3 (the coupling across worlds is not identified).',
            '(i) The joint law of all factual quantities, and every interventional law, are the same for every '
            '$\\rho$; the counterfactual law of the goals is not. No data, observational or experimental, determine '
            '$\\rho$. (ii) For $\\rho<1$ the effect involves the recharge error, and given $y$ and $\\kappa$, '
            '$\\mathrm{Var}(e\'-e)=(1-\\rho)^2V+(1-\\rho^2)\\Sigma_e$ with $V=\\mathrm{Var}(e\\mid y,\\kappa)\\preceq'
            '\\Sigma_e$, which decreases in $\\rho$ on [0, 1]: at $\\rho=0$ the data cannot narrow the noise part at '
            'all. (iii) If $B_\\rho$ is calibrated on simulated twins with coupling $\\rho$ for each $\\rho$ in a grid '
            '$R$, the union $\\bigcup_{\\rho\\in R}B_\\rho$ has risk at most $\\alpha$ under every coupling in $R$.'))
    A(('proof', '(i) $\\rho$ enters only $e\'$, which appears in no factual quantity; in a single interventional world '
                '$e\'$ has the law of $e$ whatever $\\rho$. (ii) $e\'-e=(\\rho-1)e+\\sqrt{1-\\rho^2}\\,\\xi$ with $\\xi$ '
                'independent of $(y,e)$; the derivative of the variance is $-2(1-\\rho)V-2\\rho\\Sigma_e\\preceq0$. '
                '(iii) The union contains $B_{\\rho\'}$, whose guarantee holds when the twins have coupling '
                '$\\rho\'$.'))
    A(('prop', 'Proposition K4 (anchor twins).',
            'Let anchors be cases exchangeable with the field case in which the histories and $\\kappa$ were measured, '
            'and let the *anchor twin* of a goal be its factual value plus the effect computed with the simulator\'s '
            'mechanism (delay $\\tau_P$, $\\rho=1$). (i) If the real mechanism is the simulator\'s, anchor twins are true '
            'twins, and a band calibrated on $m$ of them by conformal risk control has risk at most $\\alpha$ for every '
            'law of the exogenous variables. (ii) If the real delay $\\tau_Q$ differs, the anchor twin of an effect is '
            'off by $\\kappa\\,(a_{\\tau_Q}-a_{\\tau_P})$, and no number of anchors removes this error: a '
            'counterfactual guarantee is only as good as its mechanism.'))
    A(('proof', '(i) The scores of anchor twins and of the field twin are exchangeable; apply conformal risk control '
                '(A1; review IV, A1). (ii) Subtract [[eff]] under the two delays.'))
    A(('box', ['**What is new.** (1) Distribution-free counterfactual bands for the recharge and the heads of an aquifer '
               'under a rain intervention, for the same years and given the data: rung-3 inference with a guarantee. '
               '(2) The cancellation theorem: the effect of the rain is free of every latent boundary condition, and an '
               'anchor band for the recharge coefficient becomes a simultaneous guarantee for the whole effect path '
               '(Proposition K1). (3) The value of abduction of a monitoring design as a ratio of floors, and the '
               'collapse of rung 3 to rung 2 with rain alone (Proposition K2). (4) The untestable coupling of noise across '
               'worlds made explicit, priced, and a band robust to it (Proposition K3). (5) Anchor twins, which make '
               'counterfactual guarantees checkable on real anchors, their failure under a wrong mechanism, and its '
               'repair by an enlarged law (Proposition K4). To our knowledge none of these appears in the one hundred '
               'and forty papers of reviews I–VII.']))
    # ------------------------------------------------------------------------------------------- 4.3 tests
    A(('h2', '4.3 Tests'))
    sims_none = risks('none', 'sims')
    A(('p', f'**T21: drought counterfactuals under three real laws.** Figure {{{{cf}}}} and Table {{{{t21}}}}, four '
            f'loggers. *No shift.* All bands are valid within sampling error and close to the floor: simulated twins '
            f'{rng_(col("none", "sims"))} times the floor (risk {rng_(sims_none, 3)}; one calibration set of 300 twins, '
            f'so a risk of 0.11 is within its sampling error), anchor twins {rng_(col("none", "anc20"))} (risk '
            f'{fill["anc_none_rng"]}), the enlarged law {rng_(col("none", "T_sims"))} (risk '
            f'{rng_(risks("none", "T_sims"), 3)}). The exact counterfactual law costs almost nothing in band shape: with '
            f'$\\lambda$ set on the field cases it is {rng_(col("none", "star"))} times the floor (an in-sample '
            f'multiplier, so a ratio a little below 1 is sampling noise). For the effects the anchor band is exactly the '
            f'push-forward of the conformal band for $\\kappa$ (Proposition K1): its score is the same in every week. '
            f'*Delay.* The simulator\'s mechanism is wrong: simulated twins give bands of '
            f'{rng_(col("delay", "sims"))} times the floor that are invalid (risk {rng_(risks("delay", "sims"))}){" — every band narrower than the floor was invalid, as review VI F1 requires" if below and below_bad else ""}. '
            f'Anchor twins remain wide but invalid for the effects (risk {fill["anc_delay_eff"]}) and for the levels '
            f'(risk {rng_(risks("delay", "anc20", ("rc", "hc")), 3)}), at {rng_(col("delay", "anc20"))} times the floor: '
            f'they are computed with the wrong delay (Proposition K4 (ii)). The enlarged law is valid for all goals '
            f'(risk {rng_(risks("delay", "T_sims"), 3)}) at {rng_(col("delay", "T_sims"))} times the floor. *Shifted '
            f'parameters.* The mechanism is right but the prior is wrong: simulated twins fail (risk '
            f'{rng_(risks("params", "sims"), 3)}), anchor twins are valid (risk {rng_(risks("params", "anc20"), 3)}) at '
            f'{rng_(col("params", "anc20"))} times the floor, while the enlarged law, whose prior does not contain this '
            f'shift, is ' + ('valid as well' if all(r <= 0.105 for r in risks('params', 'T_sims')) else 'not repaired')
            + f' (risk {rng_(risks("params", "T_sims"), 3)}). Anchor twins guard against a wrong prior, the enlarged law '
            f'against the structural error it was built for, and neither against the other\'s failure.'))
    A(('img', 'cf', 17.0))
    A(('cap', 'Figure {{cf}}. T21: half-width of each counterfactual band divided by the floor of the real law, for a '
              '40% drought: effects on recharge and on the head at the well, counterfactual recharge and head. Open '
              'markers are invalid bands (risk above 0.10).'))
    t21 = []
    keys = (('star', 'exact under P, λ known'), ('sims', 'exact under P, 300 twins'),
            ('anc20', 'exact under P, 20 anchor twins'), ('T_sims', 'enlarged law, 300 twins'))
    laws = (('none', 'No shift'), ('delay', 'Delay 35 d'), ('params', 'Shifted parameters'))
    for law, lab in laws:
        t21.append([f'**{lab}**: floor $W^*$'] + [f'{D[law][g]["floor"]["halfwidth"]:.4f}' for g in GOALS])
        for key, kl in keys:
            row = [kl]
            for g in GOALS:
                v = D[law][g][key]
                row.append(f'{ratio(D[law][g], key):.2f}' + ('' if key == 'star' else f' ({v["risk"]:.3f})'))
            t21.append(row)
    A(('cap', 'Table {{t21}}. T21: the floor (mean half-width; recharge mm/d, head m) and each band as a multiple of '
              'it, with its risk in brackets, for a 40% drought and four loggers.'))
    A(('table', ['Band', 'Effect Δr', 'Effect Δh', 'Level r′', 'Level h′'], t21, [5.4, 2.9, 2.9, 2.9, 2.9], 9))
    vr = [va['4 loggers'][g] for g in GOALS]
    v8 = [va['8 loggers'][g] for g in GOALS]
    v1 = [va['1 logger'][g] for g in GOALS]
    mono = all(DS[b][g]['floor']['halfwidth'] <= DS[a][g]['floor']['halfwidth'] * 1.01
               for a, b in (('rain only', '1 logger'), ('1 logger', '2 loggers'), ('2 loggers', '8 loggers'),
                            ('rain only', '4 loggers'), ('4 loggers', '8 loggers'), ('4 loggers', '4 loggers + gauge'))
               for g in GOALS)
    A(('p', f'**T22: the value of abduction.** Figure {{{{design}}}}. With rain alone the counterfactual floor is the '
            f'interventional floor (Proposition K2 (i)): the rung-3 question has no better answer than the rung-2 one. '
            f'One logger at 2 km already buys {rng_(v1, 1)}-fold, four loggers {rng_(vr, 1)}-fold and eight '
            f'{rng_(v8, 1)}-fold (effect on recharge, effect on the head, counterfactual recharge, counterfactual head '
            f'in that order: {", ".join(f"{v:.1f}" for v in vr)} with four loggers). The floors never rose when loggers '
            f'were added{"" if mono else " (up to sampling noise)"}. For the effects all of this value comes through '
            f'$\\kappa$ (Proposition K2 (iii)); a tide gauge, which informs the sea level only, multiplies the value of '
            f'abduction by {rng_([va["4 loggers + gauge"][g] / va["4 loggers"][g] for g in ("dr", "dh")], 2)} for the '
            f'effects and by {rng_([va["4 loggers + gauge"][g] / va["4 loggers"][g] for g in ("rc", "hc")], 2)} for '
            f'the levels.'))
    A(('img', 'design', 17.0))
    A(('cap', 'Figure {{design}}. T22: the counterfactual floor of six designs relative to the interventional floor '
              '(rain only; left) and its inverse, the value of abduction (right). 40% drought, no shift, shared noise. The two '
              'effects coincide (dashed over solid): both are the posterior of κ, scaled week by week (Proposition '
              'K1).'))
    A(('p', f'**T23: the coupling across worlds.** Figure {{{{coupling}}}}. If the recharge error of the twin world is '
            f'only partly the factual one, the counterfactual floors widen: at $\\rho$ = 0.6 by '
            f'{rng_(list(rho_fl["0.6"].values()), 1)}-fold, at $\\rho$ = 0 by {rng_(list(rho_fl["0.0"].values()), 1)}-fold '
            f'(effect on recharge, effect on the head, counterfactual recharge and head). The band that assumes shared '
            f'noise is then invalid (risk {rng_(shared_risk["0.6"], 3)} at $\\rho$ = 0.6, '
            f'{rng_(shared_risk["0.0"], 3)} at $\\rho$ = 0); bands calibrated with the right coupling are valid '
            f'({rng_(right_risk, 3)}), but the right coupling is never known (Proposition K3 (i)). The union over the '
            f'grid $\\rho$ ∈ {{0, 0.25, 0.5, 0.75, 0.9, 1}} is valid in every case (risk {rng_(rob_risk, 3)}, including '
            f'$\\rho$ = 0.6, which is not on the grid), at {rng_(rob_ratio["1.0"])} times the floor when the noise is in '
            f'fact shared and {rng_(rob_ratio["0.0"])} when it is independent. The coupling also decides monotonicity: '
            f'with shared noise a 40% drought lowers the recharge in every week; with independent noise it raises it in '
            f'{fill["up_dr0"]} of the weeks, while the head at the well, which smooths the noise, rises in '
            f'{fill["up_dh0"]} of them.'))
    A(('img', 'coupling', 17.0))
    A(('cap', 'Figure {{coupling}}. T23: the counterfactual floor for three couplings of the recharge error across '
              'worlds, relative to shared noise (left), and the risk of the band that assumes shared noise, of the band '
              'with the right coupling and of the band robust to every coupling on the grid (right; one marker per '
              'goal; dashed: α = 0.10). 40% drought, four loggers, no shift.'))
    t24 = []
    for law, lab in (('none', 'No shift'), ('delay', 'Delay 35 d')):
        t24.append([f'**{lab}**: floor $W^*$'] + [f'{LT[law][g]["floor"]["halfwidth"]:.4f}' for g in GOALS])
        for key, kl in keys[1:]:
            t24.append([kl] + [f'{ratio(LT[law][g], key):.2f} ({LT[law][g][key]["risk"]:.3f})' for g in GOALS])
    A(('p', f'**T24: a late wet season.** Table {{{{t24}}}}. With the rain 30 days later the effect changes sign within '
            f'the year (the head at the well is higher in {fill["late_up_dh"]} of the weeks) and depends strongly on the '
            f'delay. Without shift every guaranteed band is valid within the sampling error of one calibration set (risk '
            f'{rng_(risks("none", "sims", src=LT) + risks("none", "anc20", src=LT) + risks("none", "T_sims", src=LT), 3)}); '
            f'the enlarged law pays {rng_(col("none", "T_sims", src=LT))} times the floor for not knowing the delay, '
            f'much more than for the drought, because a shift in timing is what the delay controls. Under the 35-day '
            f'delay simulated twins and anchor twins fail (risk {rng_(risks("delay", "sims", src=LT), 3)} and '
            f'{rng_(risks("delay", "anc20", src=LT), 3)}), and the enlarged law gives {fill["late_delay_T"]} at '
            f'{rng_(col("delay", "T_sims", src=LT))} times the floor.'))
    A(('cap', 'Table {{t24}}. T24: late season (rain 30 days later), four loggers; floor and each band as a multiple of '
              'it, risk in brackets.'))
    A(('table', ['Band', 'Effect Δr', 'Effect Δh', 'Level r′', 'Level h′'], t24, [5.4, 2.9, 2.9, 2.9, 2.9], 9))
    A(('h2', '4.4 Using counterfactual bands at Fushë-Kuqe'))
    A(('b', '**Report the effect, not only the level:** the effect of a rain scenario is free of the sea level, the '
            'inflow and the initial head (Proposition K1), so it can be guaranteed with anchors that measured the '
            'recharge coefficient alone; a counterfactual level needs the histories.'))
    A(('b', '**Do not sell rung 3 with rain alone:** without heads the counterfactual is the interventional answer '
            '(Proposition K2); the loggers are what turns a scenario into a counterfactual for these years, and their '
            'value of abduction can be computed before they are installed.'))
    A(('b', '**State the coupling:** whether the unmodelled recharge would have been the same in a drier world is an '
            'assumption no data test (Proposition K3). Report the shared-noise band and the coupling-robust band side by '
            'side; the plausible range of the coupling is ==to be set with the local hydrogeologists and the soil '
            'scientists==.'))
    A(('b', '**Trust the mechanism, or enlarge it:** anchors check the factual part of a counterfactual, never the '
            'mechanism that carries it to the other world (Proposition K4). Name the structural unknowns (here the '
            'vadose delay) and put them in the law.'))
    # ------------------------------------------------------------------------------------------- 5 synthesis
    A(('h', '5. Synthesis: one hundred and forty papers in one procedure'))
    A(('p', 'Table {{all}} places the hundred and forty papers of reviews I–VII on the steps of the procedure. Card '
            'numbers carry the review: I-O1 is card O1 of review I, VII-C2 card C2 of this review. Review VII adds the '
            'counterfactual question: what the aquifer would have done under another rain, with a guarantee.'))
    rows = []
    sets = (('I', cards_gar.CARDS), ('II', cards_matja.CARDS), ('III', cards_reshja.CARDS),
            ('IV', cards_ankora.CARDS), ('V', cards_prirja.CARDS), ('VI', cards_dyshemeja.CARDS), ('VII', CARDS))
    for key, lab_ in STEPS:
        row = [lab_]
        for rv, cs in sets:
            ids = [c['id'] for c in cs if key in c['steps']]
            row.append(', '.join(ids) if ids else '–')
        rows.append(row)
    A(('cap', 'Table {{all}}. The one hundred and forty papers of reviews I–VII against the steps of the procedure (card '
              'numbers of each review; a paper can serve several steps).'))
    A(('table', ['Step', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII'], rows, [2.3, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1], 8.6))
    A(('p', '**Order of work.** (1) Build the simulated aquifers from the rain with its errors (RESHJA-GO) and every '
            'named structural unknown, such as the vadose delay, as a random quantity of the law. (2) Compute the floor '
            'of each candidate design (DYSHEMEJA-GO) and choose instruments by guaranteed value (MATJA-GO). (3) Use the '
            'exact posterior where the model allows it. (4) Calibrate on real anchors (ANKORA-GO), horizon-matched when '
            'the law drifts (PRIRJA-GO). (5) For scenario questions, build the twin world with shared histories, '
            'guarantee the effect through the recharge coefficient, and report the coupling-robust band beside the '
            'shared-noise band (SHKAKU-GO). (6) Report every band with its ratio to the floor and the '
            'simulation-calibrated band alongside (GARANCIA-GO).'))
    # ------------------------------------------------------------------------------------------- 6 limitations
    A(('h', '6. Limitations'))
    A(('b', 'Every card is partly verified: landing pages, and the exact wording of the theorems, were reached through '
            'search results only. Several cards are attribution studies with stated results rather than theorems.'))
    A(('b', 'The twin world keeps the histories of sea level and inflow. That is natural for the sea; for the inland '
            'inflow, which a drier climate would also lower, it is an assumption: if the inflow is a mediator of the '
            'rain it must be moved to the mechanism and the effect grows accordingly.'))
    A(('b', 'The coupling-robust band is valid on a grid of couplings; between grid points it is checked numerically '
            '(ρ = 0.6), not proved.'))
    A(('b', 'The enlarged law repairs the delay because the real delay lies inside its prior; it does not repair '
            'errors it does not contain' + (f', and under shifted parameters it is invalid (risk '
            f'{rng_(risks("params", "T_sims"), 3)}, T21); there only the anchors protect the guarantee.'
            if any(r > 0.105 for r in risks('params', 'T_sims')) else '.')))
    A(('b', 'Dispersion does not enter the test bed; counterfactual chloride needs the transport model of review I and '
            'is left for the next step, together with a nonlinear (threshold) recharge mechanism, for which '
            'Proposition K1 holds only to first order.'))
    return B
