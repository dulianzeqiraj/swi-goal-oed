"""Text of Stakeholder decisions V, a state-of-the-art review (English): stakeholder decisions when the source of chloride is unknown, thirty papers
and PREJARDHJA-GO. blocks(R) returns the block list; every number comes from res/prejardhja.json.
Conventions: $inline math$, **bold**, *italic*, [text](url) hyperlink, [[key]] equation number, {{key}} figure or table
number."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cards_prejardhja import CARDS, INST_ORDER  # noqa: E402

SRC_NAME = dict(SWI='lateral seawater intrusion', UP='upconing of deep saline water',
                DRY='drought (evapoconcentration and less dilution)', ANT='return flow and wastewater')
POL_NAME = dict(oracle='Oracle (knows the source)', assume_swi='Assume seawater intrusion', bayes_prior='Bayes, prior only',
                worst='Worst case, no tests', map='Most probable source after the tests',
                bayes_post='Bayes posterior after the tests', prejardhja='PREJARDHJA-GO')

BACKGROUND = [
    dict(key='B1', text='Wasserman, L., Ramdas, A., & Balakrishnan, S. (2020). Universal inference. Proceedings of the '
                        'National Academy of Sciences 117(29), 16880–16890.',
         url='https://doi.org/10.1073/pnas.1922664117'),
    dict(key='B2', text='Vovk, V., & Wang, R. (2021). E-values: Calibration, combination and applications. The Annals of '
                        'Statistics 49(3), 1736–1754.', url='https://doi.org/10.1214/20-AOS2020'),
    dict(key='B3', text='Grünwald, P., de Heide, R., & Koolen, W. (2024). Safe testing. Journal of the Royal Statistical '
                        'Society Series B: Statistical Methodology 86(5), 1091–1128.',
         url='https://doi.org/10.1093/jrsssb/qkae011'),
    dict(key='B4', text='Shafer, G. (2021). Testing by betting: A strategy for statistical and scientific communication. '
                        'Journal of the Royal Statistical Society Series A: Statistics in Society 184(2), 407–431.',
         url='https://doi.org/10.1111/rssa.12647'),
    dict(key='B5', text='Ville, J. (1939). Étude critique de la notion de collectif. Gauthier-Villars, Paris.', url=None),
    dict(key='B6', text='Davis, S. N., Whittemore, D. O., & Fabryka-Martin, J. (1998). Uses of chloride/bromide ratios in '
                        'studies of potable water. Groundwater 36(2), 338–350.',
         url='https://doi.org/10.1111/j.1745-6584.1998.tb01099.x'),
    dict(key='B7', text='Alcalá, F. J., & Custodio, E. (2008). Using the Cl/Br ratio as a tracer to identify the origin of '
                        'salinity in aquifers in Spain and Portugal. Journal of Hydrology 359(1–2), 189–207.',
         url='https://doi.org/10.1016/j.jhydrol.2008.06.028'),
]


def card_ref(c):
    return dict(key=c['id'], text=f"{c['authors']} ({c['year']}). {c['title']}. {c['venue']}.", url=c['links'][0][1])


def all_refs():
    return [card_ref(c) for c in CARDS] + BACKGROUND


def pc(x, d=0):
    v = 100 * x
    if 0 < v < 0.5 and d == 0:
        return '<1%'
    return f'{v:.{d}f}%'


def me(k):
    """kEUR -> 'x.xx M€'"""
    return f'{k / 1000:.2f} M€'


def ke(k):
    return f'{k:.0f} k€'


def q(d):
    return f"A {d['A']:g}, B {d['B']:g}, C {d['C']:g}, X {d['X']:g}"


def tests_str(ts):
    names = dict(T1='Br/Cl', T2='isotopes', T3='depth profiles', T4='nitrate–boron')
    return ' + '.join(f'{t} ({names[t]})' for t in ts) if ts else 'none'


def blocks(R):
    S = R['setup']; P0 = R['P0']; P1 = R['P1']; P2 = R['P2']; P2a = R['P2_upA']; P3 = R['P3']; P4 = R['P4']
    P5 = R['P5']; P6 = R['P6']; src = S['src']
    by = P1['by_source']; avg = P1['prior_avg']; mx = P1['max_exceed']
    pj = {s: by[s]['prejardhja'] for s in src}
    beta, alpha, delta = P1['beta'], P1['alpha'], S['delta']
    cover_min = min(pj[s]['cover'] for s in src)
    size_rng = (min(pj[s]['size'] for s in src), max(pj[s]['size'] for s in src))
    cross = P0['cross']
    wrong_max = max(cross[i][j] for i in range(4) for j in range(4) if i != j)
    swi_wrong = max(cross[i][0] for i in range(1, 4))
    mon = P4['by_source']
    ev_rng = (min(mon[s]['ever_out'] for s in src), max(mon[s]['ever_out'] for s in src))
    nv_rng = (min(mon[s]['naive_out'] for s in src), max(mon[s]['naive_out'] for s in src))
    mixes = P5['mixtures']
    camp = P5['campaigns']; tc = sum(S['tcost'])
    off0, off1 = P5['offset']['0.0'], P5['offset']['1.0']
    split = P3['split']; bsplit = min(split, key=lambda r: r['cost'])
    led = P3['ledger']; fr = R['P3b']
    best_row = P2['rows'][P2['best_index']]
    t1 = [r for r in P2['rows'] if r['tests'] == ['T1']][0]
    t3 = [r for r in P2['rows'] if r['tests'] == ['T3']][0]
    t1a = [r for r in P2a['rows'] if r['tests'] == ['T1']][0]
    t2a = [r for r in P2a['rows'] if r['tests'] == ['T2']][0]
    t3a = [r for r in P2a['rows'] if r['tests'] == ['T3']][0]
    B = []
    A = B.append

    A(('title', 'Stakeholder decisions V: deciding when nobody knows where the chloride comes from'))
    A(('subtitle', 'Stakeholder decisions that meet the water demand and the other demands when the salt may come from the '
                   'sea, from deep brine, from drought or from people — thirty papers from Oxford, Caltech (with JPL), '
                   'Harvard and MIT, 2020–2026, each with an innovation step, and PREJARDHJA-GO, a decision rule with a '
                   'stated risk whatever the source'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation · fifth review of '
                 'stakeholder decisions, after reviews I–IV'))

    # ------------------------------------------------------------------------------------------ 1 outcome
    A(('h', '1. Outcome'))
    A(('bbox', [
        '**The question.** The chloride of a coastal well field is rising. It may come from the sea, from deep saline '
        'water drawn up under the wells, from a drought that concentrates the recharge and removes the dilution, or from '
        'irrigation return flow and wastewater. Each source calls for a different action, and the wrong action can '
        'make things worse. How should the utility, the households and tourism, the farmers, the environment agency and '
        'the regulator decide, now, so that the water demand and the other demands are met, when nobody knows which '
        'source it is?',
        '**Thirty papers** (Sections 3–5, Figure {{map}}): twelve from Oxford, six from Caltech (with JPL), five from '
        'Harvard (one joint with MIT) and seven from MIT, 2020–2026, each verified by DOI and affiliation in Crossref, '
        'none of them used in the earlier reviews (ten first choices were replaced for that reason). Each card gives '
        'what the paper does and the state of the art it sets, what it cannot yet do for us, three lessons (diagnosing '
        'the source, meeting the demands, the stakeholders\' decision) and an **innovation step for our problem**.',
        '**State of the art** (Section 4, Table {{sota}}). We can now watch a drought propagate from the air to the '
        'groundwater with its lags (M2, C1), read salinity as a signal of the water cycle and of aridity (M1, C2, C3), '
        'plan water systems as control problems under deep uncertainty (M3, O6–O8), weigh drinking water against '
        'irrigation, hydropower, ecosystems and equity (O2, O7, O10, O11, H2), and explain why stakeholders accept limits '
        'or ignore models (M5, O12, H5). What none of the thirty gives is a rule that tells the stakeholders what to do '
        '*before* the cause of the salt is known, with a risk they can state and defend whatever the cause turns out to '
        'be.',
        '**Innovation: PREJARDHJA-GO** (Section 6; *prejardhja* is Albanian for provenance). C1: a *plausible-source '
        'set* built from e-values of the tracer data, which contains the true source with probability at least '
        '$1-\\beta$ for any sample size and without a prior. C2: an allocation of the pumping of the three well fields '
        'and of the alternative supply that keeps $P_k(\\text{blend}>250\\ \\text{mg/L})\\le\\alpha$ for every source left '
        'in the set, so the risk is at most $\\alpha+\\beta$ whatever the source. C3: tracer tests bought for their '
        'decision value, with a planning prior used only there. C4: monthly samples that multiply the e-values, so the '
        'stakeholders can look at the data at every meeting and act at any time without inflating the error. C5: a '
        'ledger of who pays for not knowing the source, and a risk budget $\\delta=\\alpha+\\beta$ set in public.',
        f'**Numbers** (Section 6.4; a synthetic test bed, {S["n_sim"]:,} data sets per case). Acting on the wrong source '
        f'gives an exceedance probability of up to {pc(wrong_max)}; "assume seawater intrusion" up to {pc(swi_wrong)}; '
        f'Bayes with the prior only up to {pc(mx["bayes_prior"])} and Bayes after the tests up to '
        f'{pc(mx["bayes_post"], 1)}, against a budget of {pc(delta)}. Being safe without tests costs {me(avg["worst"]["cost"])}. '
        f'PREJARDHJA-GO stays at or below {pc(mx["prejardhja"], 1)} for every true source at {me(avg["prejardhja"]["cost"])} '
        f'(the oracle that knows the source: {me(avg["oracle"]["cost"])}). Monthly monitoring drops the true source at '
        f'least once in {pc(ev_rng[0], 1)}–{pc(ev_rng[1], 1)} of the cases, ordinary repeated tests in '
        f'{pc(nv_rng[0])}–{pc(nv_rng[1])}. All {P6["cells"]} combinations of tests, risk split and true source keep the '
        f'guarantee.',
        '**Limits, tested** (Section 6.4.5): a truth that mixes two sources breaks the pure list when the two sources '
        'call for opposite actions; admitting mixtures restores safety at a price that more data bring down. Tracer '
        'signatures that drift towards a rival break the coverage; a robust e-value restores it.',
        '**How to use it in Durrës** (Section 6.6): agree the stories and their signatures with the hydrogeologists, let '
        'the regulator set $\\delta$, buy the tests with the highest decision value, publish the set, the allocation and '
        'the ledger every month.']))

    # ------------------------------------------------------------------------------------------ 2 the decision problem
    A(('h', '2. The decision problem'))
    A(('h2', '2.1 Four stories, one observation'))
    A(('p', 'A utility meets a dry-season demand of $D$ = ' + f'{S["D"]:g}' + ' hm³ from three well fields and one '
            'alternative source. A is a coastal well field: it is cheap, but a coastal wetland loses spring flow when A '
            'pumps more than ' + f'{S["wet_free"]:g}' + ' hm³. B is inland, in a farming area, and above '
            + f'{S["farm_free"]:g}' + ' hm³ the water it takes is water the farmers lose. C is deep and its energy is '
            'expensive. X is a mobile desalination unit or a transfer, at most ' + f'{S["cap"][3]:g}' + ' hm³ and much '
            'dearer. The delivered blend must stay below $L$ = 250 mg/L of chloride, the indicator value of the EU '
            'Drinking Water Directive. Today the chloride is ' + f'{S["cl_now"][0]:g}' + ', ' + f'{S["cl_now"][1]:g}'
            + ' and ' + f'{S["cl_now"][2]:g}' + ' mg/L at A, B and C, and rising.'))
    A(('p', 'Four stories explain today\'s chloride equally well, because each was fitted to it:'))
    for s_ in src:
        txt = dict(
            SWI='**SWI, lateral seawater intrusion.** The pumping of A, and to a lesser degree of B, lowers the outflow '
                'that holds the sea back; chloride at A rises with the pumping of A.',
            UP='**UP, upconing of deep saline water.** The pumping of the deep field C draws old saline water up '
               'from below; chloride at C rises steeply with the pumping of C.',
            DRY='**DRY, drought.** Less recharge, more evaporation and less dilution raise the chloride of the shallow '
                'fields A and B whatever the pumping; the deep field C is buffered.',
            ANT='**ANT, return flow and wastewater.** Irrigation return flow, fertiliser and wastewater reach the inland '
                'field B; chloride at B rises steeply with the pumping of B, which captures them.')[s_]
        A(('b', txt))
    A(('p', 'The stories differ in what they predict for a change of pumping, and in the chemistry they leave behind. A '
            'seawater origin keeps the marine Br/Cl ratio; deep brines that evaporated beyond halite saturation are '
            'richer in bromide; fertiliser, sewage and road salt lower it (B6, B7). Evaporation leaves a mark on the '
            'water isotopes that mixing with seawater does not. Salinity that increases with depth points to the sea or '
            'to upconing, salinity that decreases with depth to a source from above. Nitrate and boron go with return '
            'flow and wastewater. Four tests read these marks: T1 Br/Cl, T2 water isotopes (an evaporation index), T3 '
            'depth profiles from multilevel wells, and T4 nitrate and boron (Table {{tb}}).'))
    A(('h2', '2.2 What each story asks for'))
    A(('p', 'If the source were known, the cheapest allocation that keeps the probability of an exceedance in the dry '
            'season below $\\delta$ = ' + f'{delta:.2f}' + ' would be the one in Table {{orc}}: cut A and use B and C under '
            'SWI; keep A, use B and spare C under UP; pump the deep C hard and buy some X under DRY; cut B and pump A and '
            'C under ANT. The four answers are different, and so are their costs.'))
    rows = []
    for j, s_ in enumerate(src):
        d = P0['dec'][s_]
        rows.append([f'{s_}: {SRC_NAME[s_]}', f"{d['A']:g}", f"{d['B']:g}", f"{d['C']:g}", f"{d['X']:g}",
                     me(P0['cost'][s_]), pc(P0['today']['exceed'][j])])
    w = P0['worst']['dec']
    rows.append(['Safe for all four (no tests)', f"{w['A']:g}", f"{w['B']:g}", f"{w['C']:g}", f"{w['X']:g}",
                 me(P0['worst']['cost']), '—'])
    A(('cap', 'Table {{orc}}. The cheapest allocation (hm³ per dry season) that keeps the exceedance probability below '
              f'{delta:.2f} under each source, its social cost, and the exceedance probability of today\'s pumping '
              f'(A {S["q0"][0]:g}, B {S["q0"][1]:g}, C {S["q0"][2]:g}) under that source.'))
    A(('table', ['Source (if known)', 'A', 'B', 'C', 'X', 'Social cost', 'Today\'s pumping exceeds'],
       rows, [5.6, 1.2, 1.2, 1.2, 1.2, 2.6, 4.0], 9.5, True))
    A(('h2', '2.3 Acting on the wrong story'))
    A(('p', f'Figure {{{{wrong}}}} shows what happens when the allocation of one story meets the truth of another. The '
            f'most common belief on a coast, that the salt is the sea, leads to the allocation of the first column; if '
            f'the truth is upconing, drought or return flow, the blend exceeds 250 mg/L with probability '
            f'{pc(cross[1][0])}, {pc(cross[2][0])} or {pc(cross[3][0])}. Every wrong story is costly in the same way: the '
            f'off-diagonal cells run up to {pc(wrong_max)}. The allocation that is safe for all four stories at once '
            f'(fifth column) avoids this, but it costs {me(P0["worst"]["cost"])}, {me(P0["worst"]["cost"] - min(P0["cost"].values()))} '
            f'more than the cheapest story. A Bayesian average over a prior that believes the sea first (last column) '
            f'is cheaper but breaks the budget when the truth is a story the prior did not favour.'))
    A(('img', 'wrong', 17.0))
    A(('cap', 'Figure {{wrong}}. Probability that the delivered blend exceeds 250 mg/L in the dry season (colour and '
              'number) when the allocation of one story (column) meets the truth of another (row). Green squares: the '
              'right story. Bottom row: social cost of each allocation. The planning prior of the last column is '
              f'{", ".join(f"{s_} {p:.2f}" for s_, p in zip(src, S["prior"]))}.'))
    A(('h2', '2.4 Who decides, and what they need'))
    A(('p', 'The utility pays for the supply and is answerable for the chloride. Households and tourism need the volume '
            'and feel every interruption. Farmers share the aquifer at B and lose water when the utility pumps more '
            'there. The environment agency defends the springs of the wetland at A. The regulator sets the limit and, '
            'in practice, the accepted risk of breaking it. They do not need to agree on the source to agree on a '
            'decision: they need a rule whose risk they can state whatever the source is, a way to see what each '
            'test would buy them, the freedom to look at the data at every meeting, and an account of who pays for the '
            'uncertainty. Those four needs are the components C1–C5 of the innovation (Section 6).'))

    # ------------------------------------------------------------------------------------------ 3 search
    A(('h', '3. How the thirty papers were found and checked'))
    A(('p', 'The papers were found through the Crossref API with an affiliation filter (University of Oxford, Harvard '
            'University, California Institute of Technology, Massachusetts Institute of Technology), a date filter '
            '(2020–2026, journal articles) and forty-five topic queries: seawater intrusion and groundwater salinisation, '
            'salinity source attribution, drought and salinity, decisions under deep uncertainty, robust and adaptive '
            'water planning, multi-objective trade-offs between water uses, stakeholder engagement and groundwater '
            'governance, value of information and monitoring, causal inference with missing causes, and robust '
            'optimisation. A paper was kept only if an author affiliation string in its Crossref record names one of '
            'the four institutions (for Caltech, the Jet Propulsion Laboratory, which Caltech manages, counts and is '
            'named as such on each card), and if its abstract bears on diagnosing a salinity source, on meeting '
            'competing water demands under uncertainty, or on how stakeholders decide.'))
    A(('p', 'Every DOI was then searched for in the 72 earlier reviews of this series (docs/literature). Ten first '
            'choices had already been used there and were replaced, among them the Caltech study of climate-induced '
            'saltwater intrusion in 2100 and Oxford studies of the Blue Nile and of multi-hazard water-supply risk; the '
            'thirty cards of this review are new to the series. Each card quotes the affiliation strings it rests on. '
            'The "Result" and "State of the art" fields keep to the abstract (the label says so where only a '
            'significance statement or a catalogue excerpt was available); the gap, the three lessons and the '
            'innovation step are our reading.'))

    # ------------------------------------------------------------------------------------------ 4 state of the art
    A(('h', '4. State of the art and the gap'))
    A(('cap', 'Table {{sota}}. The state of the art (2020–2026) in four strands, what it cannot yet do when the source '
              'of chloride is unknown, and the step of PREJARDHJA-GO beyond it. Codes refer to the cards of Section 5.'))
    A(('table', ['Strand', 'State of the art', 'Its limit for our problem', 'Our step'], [
        ['Diagnosing the source of salt and drought',
         'Drought propagates from air to groundwater with measurable damping and delay (M2, C1); salinisation acts as an '
         'aridity enhancer (M1); coastal salinity tracks the water cycle (C2); barriers and drought change estuarine '
         'conditions (C3); irrigation can be read from weather records (H1); short in situ campaigns beat satellite '
         'proxies (O5); sparse wells can be mapped with calibrated uncertainty (C4); salinity sets effective coverage (O1).',
         'Each paper explains or maps one mechanism. None separates rival sources of chloride in one aquifer with a '
         'probability statement a decision can rest on.',
         'C1: a set of plausible sources with coverage $\\ge 1-\\beta$ from e-values of the tracers; drought-cascade '
         'lags, local heads, irrigation records and vegetation salt stress enter as likelihoods (M2, O5, H1, M1).'],
        ['Planning under deep uncertainty and trade-offs between demands',
         'Adaptation as a control problem (M3); drought losses priced across the economy (O7); spatial coherence of '
         'drought sets the reach of back-ups (O6); dynamic groundwater changes planned reliability (O8); productivity '
         'lowers stress (O9); upstream use, hydropower and ecosystems traded off (O10, O11); investment for the greater '
         'good against the greater need (O2); groundwater hazard turned into coastal risk (M4); satellite data that '
         'managers use (C5, C6).',
         'Uncertainty sits in the forcing, the parameters and the future; the cause of the degradation is taken as known. '
         'A discrete, decision-relevant unknown cause has no place in these frameworks.',
         'C2: an allocation that protects every source still plausible, with risk $\\le\\alpha+\\beta$; C5: the cost of '
         'not knowing the source, split by who pays, and equity caps (H2).'],
        ['Stakeholders, legitimacy and payment',
         'Users pay for reliability, not quality (O3); a price cut alone does not move behaviour (O4); engagement does '
         'not guarantee that tools are used (O12); scarcity is uneven by household (H2); self-imposed limits become '
         'legitimate through informal processes (M5); the decision unit is part of the problem (H5).',
         'All assume that what is wrong is agreed. None tells the parties how to act, or who should pay, while the '
         'diagnosis is contested.',
         'C5: a public risk budget and its split, rules tied to the plausible set (no limit, voluntary, binding: M5), '
         'a decision unit that follows the set (H5), a data sheet separate from the model (O12).'],
        ['Mathematics of deciding with an unknown cause',
         'Robust optimisation over scenarios of yes/no uncertainty (M6) and with uncertainty that depends on the decision '
         '(M7); causal effects with missing confounders (H3); causal graphs inside decision models (H4).',
         'Uncertainty sets and probabilities are given, not learned from data with a guarantee; the unknown cause is a '
         'nuisance to adjust for, not the object of the decision.',
         'C1–C4: sets learned from data with finite-sample coverage, a prior used only to choose tests, and anytime-valid '
         'monitoring; pumping that switches sources on or off (M7).'],
    ], [3.0, 5.6, 4.0, 4.4], 8.5, False))
    A(('p', '**The gap.** The papers give the pieces: the physics and the signals of each source, the planning machinery, '
            'the economics of the demands and the sociology of the decision. What is missing is the joint: a decision '
            'rule for the period before the source is known, which (i) states its risk for *every* source, not on '
            'average over a prior that the stakeholders do not share; (ii) costs less than protecting against '
            'everything; (iii) says which test is worth buying because of the decision it changes, not because of the '
            'information it carries; (iv) lets the stakeholders look at the data as often as they meet; and (v) shows '
            'who pays. PREJARDHJA-GO is built to close that gap.'))

    # ------------------------------------------------------------------------------------------ 5 the papers
    A(('h', '5. The thirty papers'))
    A(('p', 'Twelve papers from Oxford, six from Caltech (with JPL), five from Harvard (one of them joint with MIT) and '
            'seven from MIT. Figure {{map}} shows which component of PREJARDHJA-GO each paper informs. Each card gives '
            'the result, the state of the art it sets and what it cannot yet do for us, three lessons — for diagnosing '
            'the source, for meeting the water demand and the other demands, and for the stakeholders\' decision — and '
            'an innovation step for our problem, in green.'))
    A(('img', 'map', 16.0))
    A(('cap', 'Figure {{map}}. The thirty papers against the five components of PREJARDHJA-GO that they inform. Colour '
              'gives the institution.'))
    titles = dict(Oxford='5.1 Oxford', Caltech='5.2 Caltech (with the Jet Propulsion Laboratory)',
                  Harvard='5.3 Harvard', MIT='5.4 MIT')
    intros = dict(
        Oxford='Water security in salinised and drought-prone places, from coastal Bangladesh and rural Africa to the '
               'national water systems of England and the Nile: who gets water, who pays, what droughts cost, and why '
               'models are or are not used.',
        Caltech='The water cycle seen from space and from sparse wells: drought cascades, coastal salinity, estuarine '
                'barriers, subsidence and groundwater storage, made usable by water managers.',
        Harvard='Irrigation read from weather records, the lived experience of scarcity, causal estimation with missing '
                'causes, causal graphs inside decision models, and the decision unit for coastal adaptation.',
        MIT='Salinity and aridity, the observed drought cascade, adaptation as control, groundwater in coastal risk, '
            'legitimacy of self-imposed limits, and robust optimisation under discrete and decision-dependent '
            'uncertainty.')
    for inst in INST_ORDER:
        A(('h2', titles[inst]))
        A(('p', intros[inst]))
        for c in CARDS:
            if c['inst'] == inst:
                A(('card', c))

    # ------------------------------------------------------------------------------------------ 6 PREJARDHJA-GO
    A(('h', '6. PREJARDHJA-GO'))
    A(('h2', '6.1 The idea'))
    A(('box', [
        '**PREJARDHJA-GO** (*prejardhja*, provenance) decides how to meet the water demand and the other demands before '
        'the source of the chloride is known. It does not ask the stakeholders to agree on a prior, and it does not '
        'protect against everything. It keeps the sources that the data cannot yet exclude, protects against those, '
        'and states the risk that this leaves.',
        '**C1 Plausible-source set.** From the tracer data $y$, keep source $k$ while its e-value '
        '$E_k(y)=\\frac{1}{K-1}\\sum_{j\\ne k}p_j(y)/p_k(y)$ stays below $1/\\beta$. **C2 Robust allocation.** Choose '
        'the pumping of A, B, C and the use of X at least social cost subject to '
        '$P_k(\\text{blend}>L)\\le\\alpha$ for every $k$ in the set. **C3 Test choice.** Buy the tracer tests, and choose '
        'the split of the budget, by the expected cost of the decision that follows; a planning prior enters here and '
        'nowhere else. **C4 Monitoring.** Multiply the e-values of the monthly samples; act at any month. **C5 '
        'Stakeholders.** The regulator and the public set $\\delta=\\alpha+\\beta$; the ledger shows who pays.']))
    A(('img', 'method', 17.0))
    A(('cap', 'Figure {{method}}. PREJARDHJA-GO in one picture. The four stories all fit today\'s chloride; tracer tests '
              'bought for their decision value (C3) feed e-values that keep the plausible sources (C1); the allocation '
              'protects every plausible source (C2); monthly samples update the set at any time (C4); the stakeholders '
              'set the risk budget and see who pays (C5).'))
    A(('h2', '6.2 Guarantees'))
    A(('p', 'Let $p_1,\\dots,p_K$ be the densities of the tracer data $y$ under the $K$ source hypotheses, let '
            '$\\beta\\in(0,1)$, and define the e-values and the plausible-source set'))
    A(('eq', 'evalue', ['E_k(y)=\\frac{1}{K-1}\\sum_{j\\ne k}\\frac{p_j(y)}{p_k(y)},\\qquad S(y)=\\{k:\\ E_k(y)<1/\\beta\\}.']))
    A(('prop', 'Proposition 1 (plausible sources without a prior).',
       'For every source $k$ and every sample size, $P_k\\{k\\notin S(y)\\}\\le\\beta$. Moreover $k\\in S(y)$ if and only '
       'if the posterior of $k$ under a flat prior, $\\pi_k(y)=p_k(y)/\\sum_jp_j(y)$, exceeds $\\beta/(K-1+\\beta)$, and '
       '$S(y)$ is never empty.'))
    A(('proof', 'Under $p_k$, each ratio $p_j/p_k$ has expectation at most one, so $E_k$ is an e-value (B2) and, by '
                'Markov\'s inequality, $P_k\\{E_k\\ge 1/\\beta\\}\\le\\beta\\,E_{p_k}[E_k]\\le\\beta$. Writing '
                '$E_k=(1-\\pi_k)/((K-1)\\pi_k)$, the condition $E_k<1/\\beta$ becomes $\\pi_k>\\beta/(K-1+\\beta)$. The '
                'largest $\\pi_k$ is at least $1/K$, which exceeds $\\beta/(K-1+\\beta)$ whenever $\\beta<1$, so the most '
                'probable source is always kept.'))
    A(('p', 'The second statement makes the set easy to explain: keep every source that a neutral observer, who '
            'starts with no preference, would still give more than about ' + pc(beta / (3 + beta), 1) + ' (with $K$ = 4 '
            'and $\\beta$ = ' + f'{beta:.2f}' + '). The first statement is what makes it safe: it holds for each source '
            'separately, so no source can be "unlucky" because the prior did not favour it. If a hypothesis has free '
            'parameters (an end-member that is not known exactly), the denominator $p_k(y)$ is replaced by its '
            'supremum over those parameters, and the bound still holds for every value of them (universal inference, '
            'B1):'))
    A(('eq', 'ui', ['E_k^{\\text{rob}}(y)=\\frac{1}{K-1}\\sum_{j\\ne k}\\frac{p_j(y)}{\\sup_{\\theta\\in\\Theta_k}'
                    'p_{k,\\theta}(y)}.']))
    A(('p', 'The allocation $x=(q_A,q_B,q_C,q_X)$ is then chosen at least social cost, '
            'protecting every source in the set:'))
    A(('eq', 'robust', ['\\min_{x}\\ c(x)\\quad\\text{subject to}\\quad P_k\\{\\text{Cl}_{\\text{blend}}(x)>L\\}\\le\\alpha'
                        '\\quad\\text{for all }k\\in S(y),']))
    A(('p', 'with $c(x)$ the supply cost plus the cost of unmet demand, of the farmers\' lost water and of the wetland, '
            'given in [[cost]].'))
    A(('prop', 'Proposition 2 (the risk budget).',
       'If the dry-season variability of the chloride is independent of the tracer data given the source, the '
       'allocation of [[robust]] exceeds the limit with probability at most $\\alpha+\\beta$, whatever the true source '
       '$k^*$, the prior or the sample size:'))
    A(('eq', 'risk', ['P_{k^*}\\{\\text{exceed}\\}=E\\big[P_{k^*}\\{\\text{exceed given }x(y)\\}\\big]\\le P_{k^*}\\{k^*\\notin '
                      'S(y)\\}+\\alpha\\le\\alpha+\\beta.']))
    A(('proof', 'Given $y$, the exceedance probability under $k^*$ is at most $\\alpha$ when $k^*\\in S(y)$, because the '
                'constraint of [[robust]] then covers $k^*$, and at most one otherwise. Taking expectations and using '
                'Proposition 1 gives the bound.'))
    A(('p', 'Monthly samples $y_1,y_2,\\dots$, independent given the source, are combined by multiplying the likelihood '
            'ratios before averaging:'))
    A(('eq', 'mart', ['M_{k,t}=\\frac{1}{K-1}\\sum_{j\\ne k}\\prod_{s\\le t}\\frac{p_j(y_s)}{p_k(y_s)},\\qquad '
                      'S_t=\\{k:\\ M_{k,t}<1/\\beta\\}.']))
    A(('prop', 'Proposition 3 (look at the data at every meeting).',
       'Under source $k$, $M_{k,t}$ is a non-negative martingale with mean one, so $P_k\\{\\exists\\,t:\\ k\\notin '
       'S_t\\}\\le\\beta$ (Ville\'s inequality, B5; B3, B4). An allocation chosen by [[robust]] at any month, including a '
       'month chosen because of what the data showed, keeps the bound $\\alpha+\\beta$.'))
    A(('proof', 'Each product $\\prod_{s\\le t}p_j(y_s)/p_k(y_s)$ is a martingale with mean one under $p_k$, and so is '
                'their average. Ville\'s inequality bounds the probability that a non-negative martingale with mean '
                'one ever reaches $1/\\beta$ by $\\beta$. The argument of Proposition 2 then applies at any stopping '
                'time.'))
    A(('prop', 'Proposition 4 (what the prior is allowed to do).',
       'Choosing the tests $T$ and the split $\\beta$ before the data, by minimising the expected cost under a planning '
       'prior $w$,'))
    A(('eq', 'choice', ['(T^*,\\beta^*)=\\arg\\min_{T,\\beta}\\ \\sum_kw_k\\,E_k^T\\big[c\\big(x^*_{\\delta-\\beta}'
                        '(S_\\beta(y))\\big)\\big]+c_T,']))
    A(('p', 'where $E_k^T$ is the expectation over the data of the bundle $T$ under source $k$, leaves Propositions '
            '1–3 intact, because they hold for every fixed $(T,\\beta)$ and the choice does not look '
            'at the data. A wrong prior can make PREJARDHJA-GO more expensive; it cannot make it less safe. This is the '
            'division of labour that the stakeholders need: their beliefs decide what is worth measuring, not what is '
            'safe.'))
    A(('prop', 'Proposition 5 (mixtures).',
       'If the blend excess is linear in the mixture weights of the sources and its spread does not depend on the '
       'source (as in the test bed), an allocation that keeps $P_i\\le\\alpha$ and $P_j\\le\\alpha$ keeps '
       '$P_{\\lambda i+(1-\\lambda)j}\\le\\alpha$ for every $\\lambda\\in[0,1]$. Admitting the mixtures of a grid of '
       'weights as hypotheses therefore extends Propositions 1–3 to mixed sources on the grid, and protects the mixtures '
       'between neighbouring grid points that are both kept.'))
    A(('proof', 'With a common spread $\\sigma(x)$, $P_k\\le\\alpha$ is the linear condition $M_k(x)+z_{1-\\alpha}'
                '\\sigma(x)\\le 0$ in the mean excess $M_k(x)$, and the mean excess of a mixture is the same mixture of '
                'the mean excesses.'))

    # ---- 6.3 test bed
    A(('h2', '6.3 The test bed'))
    A(('p', 'The mean dry-season chloride of field $w$ under source $k$ is today\'s value plus the drift of the story at '
            'today\'s pumping plus a linear response to a change of pumping:'))
    A(('eq', 'model', ['m_{kw}(x)=c_w^{\\text{now}}+d_{kw}+\\sum_{v\\in\\{A,B,C\\}}G_{k,wv}\\,(q_v-q_v^0),']))
    d_, g_ = S['drift'], S['gain']
    A(('p', 'with drifts $d_k$ of (' + '; '.join(f'{s_} {d_[s_][0]}, {d_[s_][1]}, {d_[s_][2]}' for s_ in src)
            + ') mg/L at A, B and C and responses of ' + f'{g_["SWI"][0][0]}' + ' mg/L per hm³ at A to the pumping of A '
            'under SWI, ' + f'{g_["UP"][2][2]}' + ' at C to C under UP, ' + f'{g_["ANT"][1][1]}' + ' at B to B under ANT, '
            'and a few mg/L elsewhere. Within a story the dry-season chloride varies with a standard deviation of '
            + f'{S["sig"][0]:g}, {S["sig"][1]:g} and {S["sig"][2]:g}' + ' mg/L, and the chance constraint of the blend is '
            'exact for this Gaussian variability:'))
    A(('eq', 'chance', ['\\sum_{w}q_w\\,(m_{kw}(x)-L)+q_X\\,(c_X-L)+z_{1-\\alpha}\\Big(\\sum_wq_w^2\\sigma_w^2\\Big)^{1/2}'
                        '\\le 0.']))
    A(('p', 'The social cost adds the price of each source (' + ', '.join(f'{n} {p:g}' for n, p in zip('ABCX', S['price']))
            + ' k€ per hm³), unmet demand at ' + f'{S["c_unmet"]:g}' + ' k€ per hm³ (rationing and tourism losses), the '
            'farmers\' water above ' + f'{S["farm_free"]:g}' + ' hm³ at B at ' + f'{S["c_farm"]:g}' + ' k€ per hm³, and '
            'the wetland\'s loss above ' + f'{S["wet_free"]:g}' + ' hm³ at A at ' + f'{S["c_wet"]:g}' + ' k€ per hm³:'))
    A(('eq', 'cost', ['c(x)=\\sum_{w\\in\\{A,B,C,X\\}}p_wq_w+c_U\\Big(D-\\sum_wq_w\\Big)+c_F\\,(q_B-4)^{+}+c_W\\,(q_A-6)^{+}.']))
    A(('p', 'Allocations are searched exactly on a grid of ' + f'{S["grid"]:,}' + ' decisions (steps of 0.25 hm³). '
            'Each tracer test gives one campaign value with Gaussian noise (Table {{tb}}); the planning prior is '
            + ', '.join(f'{s_} {p:.2f}' for s_, p in zip(src, S['prior'])) + ', the belief that the sea comes first. '
            'All numbers are illustrative and must be calibrated for Durrës before any use.'))
    mu, sd = S['mu'], S['sd']
    A(('cap', 'Table {{tb}}. The tracer tests: mean signature under each source, campaign standard deviation and cost.'))
    A(('table', ['Test', 'What it reads', 'SWI', 'UP', 'DRY', 'ANT', 'sd', 'Cost'], [
        ['T1 Br/Cl', 'Br/Cl mass ratio ×1000 (marine ≈ 3.4)'] + [f'{v:g}' for v in mu[0]] + [f'{sd[0]:g}', ke(S['tcost'][0])],
        ['T2 isotopes', 'evaporation index, ‰ below the meteoric line'] + [f'{v:g}' for v in mu[1]] + [f'{sd[1]:g}', ke(S['tcost'][1])],
        ['T3 depth profiles', 'vertical salinity gradient (+ saltier at depth)'] + [f'{v:g}' for v in mu[2]] + [f'{sd[2]:g}', ke(S['tcost'][2])],
        ['T4 nitrate–boron', 'anthropogenic index'] + [f'{v:g}' for v in mu[3]] + [f'{sd[3]:g}', ke(S['tcost'][3])],
    ], [2.6, 5.4, 1.4, 1.4, 1.4, 1.4, 1.2, 1.8], 9.5, True))

    # ---- 6.4 results
    A(('h2', '6.4 Results'))
    A(('h2', '6.4.1 Seven policies, four true sources (P1)'))
    A(('p', f'Test choice (Section 6.4.2) buys {tests_str(P1["tests"])} with $\\beta$ = {beta:.2f} and $\\alpha$ = '
            f'{alpha:.2f}. Figure {{{{policies}}}} and Table {{{{pol}}}} compare seven policies for each true source. '
            f'The oracle keeps every source at its budget at an average cost of {me(avg["oracle"]["cost"])}. Assuming the '
            f'sea is cheap and safe only if the sea is the truth (up to {pc(mx["assume_swi"])}). The Bayesian rule with '
            f'the prior alone holds the budget on average ({pc(avg["bayes_prior"]["exceed"], 1)}) but not for drought '
            f'({pc(by["DRY"]["bayes_prior"]["exceed"])}) or upconing ({pc(by["UP"]["bayes_prior"]["exceed"])}), the '
            f'stories the prior did not favour. After the tests, acting on the most probable source breaks the budget '
            f'for three sources (up to {pc(mx["map"])}), because it ignores the {pc(by["UP"]["map"]["wrong"])} of cases in '
            f'which the most probable source is the wrong one when the truth is upconing. The Bayesian posterior is close '
            f'but still above the budget for drought ({pc(by["DRY"]["bayes_post"]["exceed"], 1)}) and upconing '
            f'({pc(by["UP"]["bayes_post"]["exceed"], 1)}). PREJARDHJA-GO stays at or below {pc(mx["prejardhja"], 1)} for '
            f'every source, at {me(avg["prejardhja"]["cost"])}: {me(avg["worst"]["cost"] - avg["prejardhja"]["cost"])} '
            f'less than protecting against everything and {me(avg["prejardhja"]["cost"] - avg["oracle"]["cost"])} more '
            f'than knowing the source, tests included.'))
    A(('img', 'policies', 17.0))
    A(('cap', 'Figure {{policies}}. (a) Probability that the blend exceeds 250 mg/L under each true source (one dot per '
              f'source) for seven policies; dashed: the budget $\\delta$ = {delta:.2f}. (b) Expected social cost under the '
              'planning prior, tests included.'))
    rows = []
    for p in ('oracle', 'assume_swi', 'bayes_prior', 'worst', 'map', 'bayes_post', 'prejardhja'):
        rows.append([POL_NAME[p]] + [pc(by[s_][p]['exceed'], 1) for s_ in src] + [me(avg[p]['cost'])])
    A(('cap', 'Table {{pol}}. Exceedance probability under each true source and expected social cost (planning prior). '
              f'Budget {pc(delta)}.'))
    A(('table', ['Policy', 'SWI', 'UP', 'DRY', 'ANT', 'Cost'], rows, [6.4, 1.9, 1.9, 1.9, 1.9, 3.0], 9.5, True))
    A(('p', f'The plausible set behaves as Proposition 1 says. It contains the true source in {pc(cover_min, 1)} or more '
            f'of the cases for every source (the bound is {pc(1 - beta)}; the e-value is conservative), it is never empty, '
            f'it coincides exactly with the flat-posterior threshold in all {4 * S["n_sim"]:,} data sets, and it holds '
            f'{size_rng[0]:.2f}–{size_rng[1]:.2f} sources on average after the four tests.'))

    A(('h2', '6.4.2 Which tests to buy (P2)'))
    A(('p', f'All sixteen bundles of the four tests were valued by the expected cost of the decision that follows them, '
            f'each at its best split of the budget. Without tests the set holds all four sources and the cost is '
            f'{me(P2["rows"][0]["best"]["cost"])}; the best bundle is {tests_str(P2["best"])}, which saves '
            f'{ke(best_row["net"])} net of its {ke(best_row["test_cost"])}. The cheapest test, Br/Cl at '
            f'{ke(t1["test_cost"])}, alone saves {ke(t1["net"])}; the deep profiles, the most informative single test '
            f'({t3["eig"]:.2f} bits against {t1["eig"]:.2f}), save {ke(t3["net"])} because they cost '
            f'{ke(t3["test_cost"])}. In this geometry the ranking by information gain and the ranking by decision value '
            f'agree closely (rank correlation {P2["spearman"]:.2f}; Figure {{{{tests}}}}a), because every pair of sources '
            f'calls for a different action, and the information ranking loses at most {ke(P2["gap"])} at equal budget.'))
    A(('p', f'The two rankings part when two sources call for the same action. If the deep brine rose under the coastal '
            f'field A rather than under C, upconing and seawater intrusion would both ask for a cut at A (Figure '
            f'{{{{tests}}}}b). Br/Cl still separates them well ({t1a["eig"]:.2f} bits) but is now worth only '
            f'{ke(t1a["net"])}, while the isotopes, which separate the drought from the rest, are worth {ke(t2a["net"])} '
            f'with less information ({t2a["eig"]:.2f} bits); the deep profiles, still the most informative single test '
            f'({t3a["eig"]:.2f} bits), are worth {ke(t3a["net"])}. The rank correlation falls to {P2a["spearman"]:.2f}, and '
            f'buying by information loses up to {ke(P2a["gap"])} at equal budget. Information about the source is worth '
            f'what it changes in the decision; C3 measures that directly.'))
    A(('img', 'tests', 17.0))
    A(('cap', 'Figure {{tests}}. The sixteen bundles of tests: expected information gain about the source (planning prior) '
              'against net decision value (expected cost saved, tests paid). (a) The deep brine rises under the deep '
              'field C (the test bed). (b) It rises under the coastal field A, so that upconing and seawater intrusion '
              'ask for the same action.'))

    A(('h2', '6.4.3 Who pays, and the price of safety (P3)'))
    A(('p', f'The risk budget can be split between not knowing the source ($\\beta$) and the variability within a source '
            f'($\\alpha$). With the four tests, $\\beta$ = 0 means the set always holds all four sources and costs '
            f'{me(split[0]["cost"])}; the best split is $\\beta$ = {bsplit["beta"]:.2f} ({me(bsplit["cost"])}), and the '
            f'cost rises again for large $\\beta$, which leaves too little for the variability. Every split keeps the '
            f'exceedance of every source below the budget (Table {{{{split}}}}).'))
    A(('cap', 'Table {{split}}. The split of the budget $\\delta$ = ' + f'{delta:.2f}' + ' between the two kinds of '
              'uncertainty, with the four tests: expected cost, worst exceedance over the sources, lowest coverage of the '
              'set and its average size.'))
    A(('table', ['β', 'α', 'Expected cost', 'Worst exceedance', 'Lowest coverage', 'Sources in the set'],
       [[f'{r["beta"]:.2f}', f'{r["alpha"]:.2f}', me(r['cost']), pc(max(r['exceed_k']), 1), pc(min(r['cover_k']), 1),
         f'{r["size"]:.2f}'] for r in split], [1.8, 1.8, 3.4, 3.4, 3.4, 3.2], 9.5, True))
    A(('p', f'The ledger (Figure {{{{ledger}}}}a) shows where the extra cost of not knowing the source goes. Against the '
            f'oracle, PREJARDHJA-GO spends {ke(led["prejardhja"]["utility"] - led["oracle"]["utility"])} more on supply, '
            f'{ke(led["prejardhja"]["farmers"] - led["oracle"]["farmers"])} more of the farmers\' water, '
            f'{ke(led["prejardhja"]["wetland"] - led["oracle"]["wetland"])} more of the wetland and '
            f'{ke(led["prejardhja"]["tests"])} on tests: {ke(P3["ignorance"])} in all, against '
            f'{ke(P3["ignorance_worst"])} for the worst-case allocation. Households lose no water under any policy in '
            f'this test bed; the price of not knowing falls on the utility\'s tariff and, through the use of B, on the '
            f'farmers, which is why the farmers have a stake in the tests (card O10).'))
    A(('p', 'The regulator\'s choice of $\\delta$ has a price that can now be shown (Figure {{ledger}}b): '
            + '; '.join(f'$\\delta$ = {f["delta"]:.2f}: oracle {me(f["oracle"])}, PREJARDHJA-GO {me(f["prejardhja"])}, '
                        f'worst case {me(f["worst"])}' for f in fr) + '. The gap between the green and the grey line is '
            'what the tests are worth at each level of safety.'))
    A(('img', 'ledger', 17.0))
    A(('cap', 'Figure {{ledger}}. (a) Expected social cost by who pays (planning prior). (b) Expected social cost against '
              'the risk budget accepted by the stakeholders, for the oracle, PREJARDHJA-GO (four tests, best split) and the '
              'worst-case allocation without tests.'))

    A(('h2', '6.4.4 Looking at the data every month (P4)'))
    A(('p', f'With one Br/Cl and one nitrate–boron sample a month (each twice as noisy as a campaign) and $\\beta$ = '
            f'{P4["beta"]:.2f}, the true source leaves the set at least once in twelve months in '
            f'{pc(ev_rng[0], 1)}–{pc(ev_rng[1], 1)} of the cases, within the bound of Proposition 3. A stakeholder who '
            f'instead repeats an ordinary test at the same level every month, as anyone would, drops the true source in '
            f'{pc(nv_rng[0])}–{pc(nv_rng[1])} of the cases (Figure {{{{monitor}}}}a): the error grows with every look. '
            f'The cost of deciding falls month by month (Figure {{{{monitor}}}}b). Upconing and return flow have clear '
            f'signatures in these two tests, and a rule that decides as soon as one source is left stops on average in '
            f'month {mon["UP"]["stop_mean"]:.1f} and {mon["ANT"]["stop_mean"]:.1f}; seawater intrusion and drought look '
            f'alike in Br/Cl and nitrate, and need the isotopes. At the stopping time the exceedance stays at '
            f'{pc(max(mon[s_]["stop_exceed"] for s_ in src), 1)} or less, although the month was chosen by the data.'))
    A(('img', 'monitor', 17.0))
    A(('cap', 'Figure {{monitor}}. (a) Probability that the true source is dropped at least once by each month: '
              'PREJARDHJA-GO e-values against an ordinary test repeated every month (average over the four sources). '
              '(b) Expected cost of the decision if it is taken in that month, by true source; dotted: the oracle.'))

    A(('h2', '6.4.5 Where it breaks, and how to mend it (P5)'))
    sp = mixes['SWI+UP']
    A(('p', f'**Mixed sources.** When the truth is half seawater and half drought, or half drought and half return flow, '
            f'the pure list still keeps the blend safe ({pc(mixes["SWI+DRY"]["prejardhja"]["exceed"], 1)} and '
            f'{pc(mixes["DRY+ANT"]["prejardhja"]["exceed"], 1)}), because the two remedies agree. When the truth is half '
            f'seawater and half upconing, the remedies conflict (seawater asks to move pumping from A to C, upconing '
            f'from C to A) and the pure list fails ({pc(sp["prejardhja"]["exceed"], 1)}); the Bayesian posterior and the '
            f'most probable source fail worse ({pc(sp["bayes_post"]["exceed"])} and {pc(sp["map"]["exceed"])}). '
            f'Admitting pairwise mixtures as hypotheses ({P5["n_hyp"]} in all, Proposition 5) restores safety in every '
            f'mixed case ({pc(max(m_["mixture_exact"]["exceed"] for m_ in mixes.values()), 1)} or less), but with one '
            f'campaign the set is then wide and the cost under pure sources rises to '
            f'{me(P5["mixture_exact_pure"]["prior_cost"])}. More data narrow it (Figure {{{{stress}}}}c): the decision '
            f'cost falls from {me(camp[0]["exact"] - camp[0]["n"] * tc)} with one campaign to '
            f'{me(camp[-1]["exact"] - camp[-1]["n"] * tc)} with {camp[-1]["n"]}, while the pure list, ever more '
            f'confident in a wrong pure source, exceeds the limit in {pc(camp[-1]["mix_exceed_pure"]["SWI+UP"])} of the '
            f'mixed cases (Figure {{{{stress}}}}d). More data do not cure a wrong list of hypotheses; they make it worse.'))
    A(('p', f'**Drifting signatures.** If every tracer signature drifts by one standard deviation towards the nearest '
            f'rival, the ordinary e-value keeps the true source in only {pc(min(v_["cover"] for k_, v_ in off0.items() if k_ != "prior_cost"), 1)}'
            f'–{pc(max(v_["cover"] for k_, v_ in off0.items() if k_ != "prior_cost"), 1)} of the cases, below '
            f'{pc(1 - beta)}, and the exceedance reaches {pc(max(v_["exceed"] for k_, v_ in off0.items() if k_ != "prior_cost"), 1)}. '
            f'The robust e-value of [[ui]], with the end-members allowed to drift by up to one standard deviation, keeps '
            f'the coverage at {pc(min(v_["cover"] for k_, v_ in off1.items() if k_ != "prior_cost"), 1)}–'
            f'{pc(max(v_["cover"] for k_, v_ in off1.items() if k_ != "prior_cost"), 1)} and the '
            f'exceedance at {pc(max(v_["exceed"] for k_, v_ in off1.items() if k_ != "prior_cost"), 1)} or less, at a '
            f'cost of {me(off1["prior_cost"])} instead of {me(off0["prior_cost"])} (Figure {{{{stress}}}}b). The width '
            f'of the drift allowed is a calibration question for the laboratory and the hydrogeologists.'))
    A(('img', 'stress', 17.0))
    A(('cap', 'Figure {{stress}}. (a) Exceedance when the truth mixes two sources: pure list, mixtures admitted, Bayesian '
              'posterior, most probable source. (b) Coverage of the true source when the signatures drift one standard '
              'deviation towards the nearest rival, with the ordinary and the robust e-value. (c) Decision cost (tests '
              'excluded) against the number of campaigns. (d) Exceedance with a half-seawater, half-upconing truth '
              'against the number of campaigns.'))
    A(('h2', '6.4.6 The guarantee on every cell (P6)'))
    A(('p', f'Over all {P6["cells"]} combinations of the sixteen test bundles, ten splits of the budget and four true '
            f'sources, no exceedance probability is above the budget and no coverage below $1-\\beta$ (largest '
            f'exceedance {pc(P6["max_exceed"], 1)}; {len(P6["violations"])} violations). The guarantee does not depend on '
            f'which tests are bought or how the budget is split, as Proposition 4 says.'))

    # ---- 6.5 limits
    A(('h2', '6.5 What it does not yet do'))
    for t in (
        '**The list of stories must contain the truth.** The guarantee is for the sources on the list. A fifth source '
        '(evaporite dissolution, a leaking sewer, geothermal water) is not covered; a goodness-of-fit check on the best '
        'story, and a fallback to the alternative supply when no story fits, belong in the protocol.',
        '**Mixtures are expensive.** Admitting them is safe but, with one campaign, almost as costly as protecting '
        'against everything; the remedy is more data, or tracers that read mixing fractions (isotope mass balances), '
        'which C3 can value.',
        f'**The e-value is conservative.** Coverage was {pc(cover_min, 1)} or more where {pc(1 - beta)} was promised. '
        'Sharper e-values (with '
        'numerators fitted on part of the data, B1) would shrink the set and lower the cost without losing the '
        'guarantee.',
        '**The test bed is linear and Gaussian, the numbers illustrative.** The response of chloride to pumping is '
        'nonlinear near a threshold (card M7), and the variability within a story is neither Gaussian nor the same for '
        'every story. The method needs only that each story give a probability of exceedance for each allocation; the '
        'flow-and-transport models of the earlier reviews can provide it.',
        '**One season.** The allocation is for one dry season. Over several years the monitoring of C4 and the control '
        'view of card M3 combine into a policy table, one allocation per plausible set.'):
        A(('b', t))

    # ---- 6.6 protocol
    A(('h2', '6.6 How to use it with the stakeholders of Durrës'))
    A(('bbox', [
        '**1. Agree the stories.** With the hydrogeologists, write each candidate source as a story with a chloride '
        'response to pumping and a tracer signature, including mixtures where two sources are physically possible '
        '(Proposition 5). Publish the list.',
        '**2. Set the risk budget.** The regulator, with the public, sets $\\delta$, the accepted probability that the '
        'blend exceeds 250 mg/L in a dry season (Figure {{ledger}}b shows its price).',
        '**3. Choose the tests by their decision value** (C3), letting each party bring its own prior (card C6); the '
        'priors decide what is measured, never what is safe.',
        '**4. Publish every month** the tracer results, the e-values, the plausible set, the allocation in force and the '
        'ledger of who pays (C1, C2, C4, C5), as a data sheet separate from the model (card O12).',
        '**5. Tie the rules to the set.** A limit on the farmers at B becomes voluntary while return flow is plausible '
        'and binding only when it is the only source left (card M5); emergency measures that help only some sources '
        'carry a sunset date (card C3).',
        '**6. Revise the list** when no story fits the new data, and calibrate the drift allowed for each signature with '
        'the laboratory.']))

    # ------------------------------------------------------------------------------------------ 7 conclusion
    A(('h', '7. Conclusion'))
    A(('p', 'The thirty papers show that the pieces exist: we can see droughts travel into the groundwater, read salinity '
            'as a signal, plan water systems under deep uncertainty, price the demands of households, farmers and '
            'ecosystems, and understand why stakeholders accept a limit. They do not give the stakeholders of a salinised '
            'coast a way to decide before they know where the salt comes from. PREJARDHJA-GO does: it keeps only the '
            'sources the data cannot exclude, protects against those, states a risk that holds whatever the source, '
            'buys the tests that change the decision, lets everyone look at the data whenever they meet, and shows who '
            f'pays. In the test bed it stays within the budget for every source at {me(avg["prejardhja"]["cost"])}, '
            f'where assuming the sea breaks the limit and protecting against everything costs '
            f'{me(avg["worst"]["cost"])}. Its weak point is the list of stories itself; the protocol of Section 6.6 '
            'makes that list a public, revisable object, which is where the stakeholders\' knowledge belongs.'))
    A(('refs',))
    return B
