"""Text of the review "Where does the chloride come from?" (English).  blocks(R) returns the block list; every number of the
experiment comes from res/zanafilla.json (R), every context reference from res/refs_context.json.  Conventions: $inline
math$, **bold**, *italic*, ==yellow placeholder==, [text](url) hyperlink, [[key]] equation number, {{key}} figure or table
number."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cards_zanafilla import CARDS, INST_ORDER  # noqa: E402

RES = os.path.join(HERE, 'res')
with open(os.path.join(RES, 'refs_context.json'), encoding='utf-8') as _fh:
    REFS = json.load(_fh)

# Crossref records that lack the author list (books and one article): the authors as printed on the work
AUTHOR_FIX = {'S9': 'Manski, C. F.', 'S11': 'Moon, H. R. & Schorfheide, F.', 'S16': 'Vovk, V., Gammerman, A. & Shafer, G.'}
YEAR_FIX = {'S5': 2005, 'S6': 2016}
JOURNAL_FIX = {'S5': 'CRC Press (2nd edition)', 'S9': 'Springer Series in Statistics, Springer',
               'S14': 'Applied Mathematical Sciences 160, Springer', 'S15': 'Mathematics and Its Applications 375, Kluwer',
               'S16': 'Springer', 'S20': 'In H. D. Holland & K. K. Turekian (eds), Treatise on Geochemistry, 2nd ed., '
                                        'vol. 11, Elsevier'}
OTHER = [
    dict(key='S22', text='Stuyfzand, P. J. (2008). Base exchange indices as indicators of salinization or freshening of '
                         '(coastal) aquifers. Proceedings of the 20th Salt Water Intrusion Meeting (SWIM 20), Naples, '
                         'Florida, 262–265.', url=None),
    dict(key='S23', text='Hadamard, J. (1902). Sur les problèmes aux dérivées partielles et leur signification physique. '
                         'Princeton University Bulletin 13, 49–52.', url=None),
    dict(key='S24', text='Romano, Y., Patterson, E. & Candès, E. (2019). Conformalized quantile regression. Advances in '
                         'Neural Information Processing Systems 32.', url=None),
]
OWN = [
    dict(key='D1', text='Zeqiraj, D. (2026). Goal-oriented Bayesian experimental design for variable-density seawater '
                        'intrusion: adjoint expected information gain for joint monitoring and managed-aquifer-recharge '
                        'placement. Journal of Hydrology 680, 136559.', url='https://doi.org/10.1016/j.jhydrol.2026.136559'),
    dict(key='D2', text='Zeqiraj, D. & Beqiraj, A. (in preparation). From sparse hydrochemistry to decision-relevant '
                        'information: probabilistic chloride mapping and goal-oriented monitoring design for seawater '
                        'intrusion in the Fushë-Kuqe coastal aquifer, Albania. Manuscript for Journal of Hydrology.', url=None),
    dict(key='D3', text='Earlier innovations in the same code base: PREJARDHJA-GO (decisions while the chloride source is '
                        'unknown), BURIMI-GO (which regimes identify hidden hydrochemical processes), GJURMA-GO (reaction '
                        'extents from departures from mixing). experiments/prejardhja_go, burimi_go, gjurma_go.', url=None),
    dict(key='D4', text='The code and results of this review: experiments/zanafilla_go/ (zanafilla_core.py, '
                        'zanafilla_exp.py, zanafilla_figs.py; results in res/).',
         url='https://github.com/dulianzeqiraj/swi-goal-oed/tree/claude/modest-rubin-i52w1f/experiments/zanafilla_go'),
]


def ref_text(key):
    r = REFS[key]
    if key in AUTHOR_FIX:
        s = AUTHOR_FIX[key]
    else:
        names = []
        for a in r['authors']:
            fam = a['family'].replace('‐', '-')
            fam = fam.title() if fam.isupper() and len(fam) > 2 else fam
            ini = ''.join(p[0] + '.' for p in a['given'].replace('-', ' ').replace('.', ' ').split() if p)
            names.append(f'{fam}, {ini}'.rstrip(', '))
        if len(names) > 8:
            names = names[:7] + ['… ' + names[-1]]
        s = (', '.join(names[:-1]) + ' & ' + names[-1]) if len(names) > 1 else names[0]
    title = r['title'].rstrip('.')
    if title.isupper():
        title = title.capitalize().replace('fushe kuqe', 'Fushë-Kuqe').replace('albania', 'Albania')
    j = JOURNAL_FIX.get(key, r['journal'] or r.get('publisher') or '')
    tail = j
    if r.get('volume') and key not in JOURNAL_FIX:
        tail += f" {r['volume']}"
        if r.get('issue'):
            tail += f"({str(r['issue']).replace('-', '–')})"
    if r.get('page') and key not in ('S9', 'S14', 'S15', 'S16'):
        tail += f", {str(r['page']).replace('-', '–')}"
    return f"{s} ({YEAR_FIX.get(key, r['year'])}). {title}. {tail}."


def card_ref(c):
    venue = re.sub(r'\s*\(\d{4}[^)]*\)$', '', c['venue'])
    return dict(key=c['id'], text=f"{c['authors']} ({c['year']}). {c['title']}. {venue}.", url=c['links'][0][1])


def all_refs():
    out = [card_ref(c) for c in CARDS]
    ctx = [dict(key=k, text=ref_text(k), url='https://doi.org/' + REFS[k]['doi']) for k in REFS] + OTHER
    out += sorted(ctx, key=lambda r: int(r['key'][1:]))
    return out + OWN


def pct(x, d=0):
    return f'{100 * x:.{d}f}%'


def num(x, d=2):
    return f'{x:.{d}f}'.replace('-', '−')


def ids(route):
    return ', '.join(c['id'] for c in CARDS if route in c['routes'])


# ------------------------------------------------------------------------------------------------- numbers of the test
def fill(R):
    s = {}
    E1 = {(r['level'], r['tracers']): r for r in R['E1']}
    s['today_w'] = num(E1[('none', 'Cl + major ions')]['width_mean'], 2)
    s['today_d'] = pct(E1[('none', 'Cl + major ions')]['decidable'])
    s['cl_w'] = num(E1[('none', 'Cl')]['width_mean'], 2)
    s['all_w'] = num(E1[('none', '+ B (all)')]['width_mean'], 2)
    s['all_d'] = pct(E1[('none', '+ B (all)')]['decidable'])
    s['rel_today_d'] = pct(E1[('relict', 'Cl + major ions')]['decidable'])
    s['rel_all_d'] = pct(E1[('relict', '+ B (all)')]['decidable'])
    s['rf_all_d'] = pct(E1[('relict + fresh', '+ B (all)')]['decidable'])
    s['rf_all_w'] = num(E1[('relict + fresh', '+ B (all)')]['width_mean'], 2)
    s['rfa_all_d'] = pct(E1[('relict + fresh + anthropogenic', '+ B (all)')]['decidable'])
    s['rf_iso_d'] = pct(E1[('relict + fresh', '+ d18O, d2H')]['decidable'])
    s['br_d'] = pct(E1[('none', '+ Br')]['decidable'])
    s['wrong_max'] = pct(max(r['wrong_when_decided'] for r in R['E1']), 1)
    s['cov_min'] = pct(min(r['coverage'] for r in R['E1']), 1)
    s['empty_max'] = pct(max(r['empty'] for r in R['E1']), 1)
    s['n_e1'] = str(E1[('none', 'Cl')]['n'])
    bc0 = E1[('none', '+ B (all)')]['by_class']; bc1 = E1[('relict + fresh', '+ B (all)')]['by_class']
    s['cl_coast_lo_0'] = pct(bc0['coast lower']['decidable']); s['cl_coast_lo_1'] = pct(bc1['coast lower']['decidable'])
    s['cl_inl_up_0'] = pct(bc0['inland upper']['decidable']); s['cl_inl_up_1'] = pct(bc1['inland upper']['decidable'])
    s['cl_mid_up_1'] = pct(bc1['middle upper']['decidable'])
    E3 = R['E3']
    for key, tag in (('Cl + major ions', 't'), ('+ B (all)', 'a')):
        for w, wt in (('training world', '0'), ('shifted world', '1')):
            r = E3[key]['worlds'][w]
            s[f'nn_cov_{tag}{wt}'] = pct(r['nn_coverage']); s[f'nn_w_{tag}{wt}'] = num(r['nn_width'], 2)
            s[f'nn_dec_{tag}{wt}'] = pct(r['nn_decidable']); s[f'nn_wrong_{tag}{wt}'] = pct(r['nn_wrong_when_decided'], 1)
            s[f'ce_cov_{tag}{wt}'] = pct(r['cert_coverage']); s[f'ce_w_{tag}{wt}'] = num(r['cert_width'], 2)
            s[f'ce_dec_{tag}{wt}'] = pct(r['cert_decidable'])
            s[f'nn_out_{tag}{wt}'] = pct(1 - r['nn_inside_certificate'], 1)
            s[f'nn_cov_out_{tag}{wt}'] = pct(r['nn_coverage_when_outside']) if r['nn_coverage_when_outside'] is not None else '—'
    s['nn_ntrain'] = f"{E3['+ B (all)']['n_train']:,}".replace(',', ' ')
    s['nn_ncal'] = f"{E3['+ B (all)']['n_cal']:,}".replace(',', ' ')
    E4 = R['E4']
    a = E4['no end-member sampled | + B (all)']; b = E4['relict + fresh sampled | + B (all)']
    s['miss_0'] = pct(a['with an unlisted brine']['empty_where_brine_above_half_percent'])
    s['miss_1'] = pct(b['with an unlisted brine']['empty_where_brine_above_half_percent'])
    s['false_0'] = pct(a['model complete']['empty'], 1); s['false_1'] = pct(b['model complete']['empty'], 1)
    s['n_brine'] = str(a['with an unlisted brine']['n_brine'])
    E5 = R['E5']
    s['ls_mae'] = num(E5['median_abs_error'], 2); s['ls_big'] = pct(E5['frac_error_above_0p25'])
    s['ls_side'] = pct(E5['wrong_side_of_half'], 1); s['ls_spread'] = num(E5['mean_spread'], 2)
    s['ls_out'] = pct(E5['truth_outside_ls_range']); s['set_out'] = pct(E5['truth_outside_set'])
    s['set_w5'] = num(E5['mean_set_width'], 2); s['n_e5'] = str(E5['n'])
    E6 = R['E6']
    s['e6_ok'] = all(r['mc_lo'] is None or (r['mc_lo'] >= r['lp_lo'] - 1e-6 and r['mc_hi'] <= r['lp_hi'] + 1e-6) for r in E6)
    s['e6_n'] = str(len(E6))
    s['e6_gap'] = num(max(r['lp_hi'] - r['mc_hi'] for r in E6 if r['mc_hi'] is not None), 3)
    s['e6_gap_lo'] = num(max(r['mc_lo'] - r['lp_lo'] for r in E6 if r['mc_lo'] is not None), 2)
    return s


def filled_cards(s):
    out = []
    for c in CARDS:
        c = dict(c)
        for k in ('does', 'route', 'gap', 'step'):
            c[k] = re.sub(r'<<(\w+)>>', lambda m: s[m.group(1)], c[k])
            assert '<<' not in c[k], (c['id'], k)
        out.append(c)
    return out


def blocks(R):
    s = fill(R)
    cards = filled_cards(s)
    B = []
    A = B.append
    A(('title', 'Where does the chloride come from?'))
    A(('subtitle', 'The origin of chloride in a coastal aquifer as an ill-posed inverse problem: the state of the art in '
                   'thirty papers of 2020–2026 from Oxford, Caltech, MIT, Princeton, the Max Planck Society, Harvard and '
                   'Berkeley, and a certified, goal-oriented answer (ZANAFILLA-GO) tested numerically'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation · code and results: '
                 'experiments/zanafilla_go/'))
    # -------------------------------------------------------------------------------------------- 1 the answer
    A(('h', '1. The answer in brief'))
    A(('bbox', [
        '**Is it a good question?** Yes, and it is the question on which the decisions turn. Chloride from the sea that '
        'is advancing now calls for less pumping near the coast; seawater trapped thousands of years ago and now being '
        'flushed calls for patience and monitoring; brine from halite or from depth calls for shallower screens; '
        'wastewater and fertiliser call for sanitation and land-use control. The same chloride concentration can mean '
        'any of these.',
        '**Why it is hard** (Section 2). The water of a well is a mixture of several sources whose signatures are known '
        'only as ranges, measured with a few tracers and with noise. Many mixtures reproduce the same analysis. In '
        'Hadamard\'s terms the inverse problem is ill-posed: a solution may not exist (a source is missing), it is not '
        'unique, and the usual least-squares answer changes with the signatures one happens to assume.',
        '**How others answer it** (Sections 3 and 8). Five routes: geochemical and isotopic tracers, unmixing of '
        'end-members, regularised or Bayesian inversion, identification and design, and machine learning. None of the '
        'thirty papers, nor the standard mixing tools IsoSource (S25) and MixSIAR (S26), returns an answer that holds '
        'for uncertain end-members without a prior and says plainly when the data cannot decide.',
        f'**Innovation: ZANAFILLA-GO** (Sections 5 and 6). Replace the point answer by the *identified set*: the exact '
        f'polytope of all mixtures and signatures that reproduce the data (Proposition 1); sharp bounds of the share of '
        f'chloride from each source by linear programming (Proposition 2); Hadamard\'s three conditions restored for the '
        f'set, with an empty set as a test that a source is missing and a Lipschitz bound for stability (Proposition 3); '
        f'coverage without a prior (Proposition 4); and a goal-oriented choice of the next tracer, well or end-member '
        f'sample (Proposition 5). A neural network trained on simulations screens fast, and is checked against the bounds.',
        f'**What the test shows.** In a synthetic coastal aquifer with five candidate sources, today\'s kind of data '
        f'(chloride and major ions) decide whether most of the chloride of a salinised sample is modern seawater in '
        f'{s["today_d"]} of the samples; seven tracers at the wells raise this only to {s["all_d"]}; sampling the relict '
        f'water and the fresh water as end-members raises it to {s["rf_all_d"]}, with no wrong decision in any case. A '
        f'least-squares answer misses the truth by more than 0.25 in {s["ls_big"]} of the samples. The network covers '
        f'{s["nn_cov_a0"]} of the truths in the world it was trained for and {s["nn_cov_a1"]} in a world with more relict '
        f'water; the identified intervals cover {s["ce_cov_a1"]} there.',
        '**For Fushë-Kuqe** (Section 7). The next campaign should sample the end-members (pore water of the silt–clay '
        'layers, upgradient fresh water) before it adds tracers at the wells, and add bromide, the stable isotopes of '
        'water and boron at the salinised wells. The base-exchange index computed from the major ions that already '
        'exist separates advancing from retreating salinity and should be part of the answer.']))
    # -------------------------------------------------------------------------------------------- 2 the question
    A(('h', '2. The question, stated precisely'))
    A(('h2', '2.1 Five candidate sources'))
    A(('p', 'In a coastal alluvial aquifer of the Adriatic type five sources of chloride are plausible (Table {{sources}}). '
            'They differ in what they imply for management, and they differ in their chemistry, but not in chloride '
            'alone: the ratio of chloride to bromide separates marine water from halite brine and from many '
            'anthropogenic sources (S1, S2), the stable isotopes of water separate water that has been at the sea '
            'surface from rain water, tritium separates water recharged after the 1950s from older water, and the '
            'exchange of cations with the clays records whether salinity is advancing or retreating (S5, S22).'))
    A(('table', ['Source', 'How it enters', 'Its signature (indicative)', 'What follows for management'], [
        ['Modern seawater', 'Lateral intrusion and upconing under pumping', 'Cl about 20 g/L; Cl/Br about 290 by mass; '
         'δ¹⁸O about +1‰ (Adriatic); a sodium deficit in the aquifer (BEX < 0)', 'Reduce or relocate pumping near the '
         'coast; barriers; recharge'],
        ['Relict seawater', 'Trapped in silt and clay during past high sea levels, now released by flushing',
         'Marine Cl/Br; δ¹⁸O shifted by mixing with old fresh water; no tritium; a sodium excess (BEX > 0)',
         'Monitor; the salinity declines by itself; pumping is not the cause'],
        ['Halite brine', 'Dissolution of evaporites at depth', 'Cl/Br in the thousands; Na/Cl about 1', 'Avoid deep '
         'screens; map the body'],
        ['Anthropogenic', 'Wastewater, fertiliser, irrigation return flow', 'Cl in the hundreds of mg/L; often higher '
         'boron and nitrate; tritium of recent water', 'Sanitation, land-use control'],
        ['Fresh recharge', 'Rain and rivers', 'Cl of tens of mg/L; meteoric isotopes', 'The diluting end-member'],
    ], [2.4, 3.6, 5.6, 4.4], 9.0))
    A(('cap', 'Table {{sources}}. Candidate sources of chloride in a coastal alluvial aquifer. The signatures are indicative '
              'ranges from the literature (S1, S2, S5, S20, S22); the numerical test of Section 6 uses the intervals of '
              'Table {{sig}}.'))
    A(('h2', '2.2 The mixing model'))
    A(('p', 'Let a sample be a mixture of $K$ sources with water fractions $f=(f_{1},\\dots,f_{K})$ on the simplex. Source '
            '$k$ brings chloride $\\mathrm{Cl}_{k}$, and for each further tracer $t$ either a ratio to chloride '
            '$\\rho_{tk}$ (bromide, boron, the base-exchange index per unit chloride) or a value carried by the water '
            '$\\sigma_{tk}$ (the isotopes of water, tritium). The measured values are'))
    A(('eq', 'mix', ['y_{\\mathrm{Cl}}=\\sum_{k=1}^{K}f_{k}\\,\\mathrm{Cl}_{k}+e_{\\mathrm{Cl}},\\qquad '
                     'y_{t}=\\sum_{k=1}^{K}\\rho_{tk}\\,f_{k}\\,\\mathrm{Cl}_{k}+e_{t}\\quad\\text{or}\\quad '
                     'y_{t}=\\sum_{k=1}^{K}\\sigma_{tk}\\,f_{k}+e_{t},',
                     'f_{k}\\ge 0,\\quad\\sum_{k}f_{k}=1,\\quad f_{k}\\le u_{k},\\qquad '
                     '\\mathrm{Cl}_{k}\\in[\\mathrm{Cl}_{k}^{-},\\mathrm{Cl}_{k}^{+}],\\ '
                     '\\rho_{tk}\\in[\\rho_{tk}^{-},\\rho_{tk}^{+}],\\ \\sigma_{tk}\\in[\\sigma_{tk}^{-},\\sigma_{tk}^{+}],']))
    A(('p', 'where the caps $u_{k}$ express site knowledge (no anthropogenic water in a deep screen, no halite brine in a '
            'shallow one) and the errors satisfy $|e_{t}|\\le\\varepsilon_{t}$ with a stated probability. The quantity a '
            'decision needs is the share of the chloride that comes from source $k$,'))
    A(('eq', 'share', 's_{k}=\\frac{f_{k}\\,\\mathrm{Cl}_{k}}{\\sum_{j}f_{j}\\,\\mathrm{Cl}_{j}},'))
    A(('p', 'for instance the share of modern seawater at a supply well, with the rule "reduce pumping if '
            '$s_{\\mathrm{MS}}>0.5$".'))
    A(('h2', '2.3 Why it is ill-posed'))
    A(('p', 'Hadamard called a problem well-posed when a solution exists, is unique and depends continuously on the data '
            '(S23). The unmixing problem [[mix]] fails all three. *Existence* fails when a real source is not in the '
            'list: then no mixture reproduces the data. *Uniqueness* fails because the unknowns outnumber the '
            'independent data: $K-1$ fractions and up to $K(1+T)$ signatures against $1+T$ measurements; even with '
            'signatures fixed, $K=5$ sources need at least four independent tracers besides the sum to one. '
            '*Stability* fails when two sources have similar signatures, as modern and relict seawater do: the '
            'least-squares answer then moves far for small changes of the data or of the assumed signatures. In the '
            f'test of Section 6, with seven tracers, the least-squares share of modern seawater changes on average by '
            f'{s["ls_spread"]} when the signatures are moved inside their intervals, and the answer with the central '
            f'signatures misses the truth by more than 0.25 in {s["ls_big"]} of the samples.'))
    A(('p', 'The classical remedies change the problem to make it well-posed: Tikhonov regularisation picks the smallest '
            'or smoothest solution (S15), the Bayesian approach picks a prior and reports a posterior (S13, S14), '
            'machine learning picks the solution that is typical of its training data (S17). Each choice is a prior in '
            'disguise. In the directions the data do not see, the answer is the prior. That is acceptable when the '
            'prior is right, and it is invisible when it is wrong.'))
    # -------------------------------------------------------------------------------------------- 3 routes
    A(('h', '3. How others answer it: five routes'))
    A(('p', 'The thirty papers of Section 8 (Figure {{map}}) and the context sources fall into five routes.'))
    A(('img', 'map', 16.5))
    A(('cap', 'Figure {{map}}. The thirty papers against the five routes. Colours mark the institutions; the short titles '
              'are ours.'))
    A(('p', f'**Tracers** ({ids("tracers")}). Geochemical and isotopic evidence is the oldest route and still the one '
            f'that decides most real cases: chloride-to-bromide ratios, the isotopes of water, of boron and of '
            f'strontium, noble gases and the ages of water. Krypton-81 ages separate old marine brines from younger water '
            f'that dissolved salt (O1); deep saline water is as voluminous as the fresh (O2) and human activity now moves '
            f'it (H1); isotope maps give the signature of local recharge (M2); radium isotopes measure the exchange with '
            f'the sea (M3); and the salinity of domestic wells has been traced to road salt, sewage and basin brines '
            f'(M1). The route explains by fingerprints. Its weakness is that fingerprints overlap and that the reasoning '
            f'from them is qualitative.'))
    A(('p', f'**Unmixing** ({ids("mixing")}). End-member mixing analysis turns fingerprints into fractions. Its theory '
            f'is the theory of nonnegative factorisation: fractions are identifiable when the end-members are known and '
            f'independent, or when the data contain nearly pure samples (S19). When the sources outnumber what the '
            f'tracers can separate, two tools set the standard. IsoSource enumerates, in small increments, every '
            f'combination of source proportions that satisfies the mass balance within a tolerance, and reports the '
            f'distribution of these feasible solutions, so that its range is a bound for fixed end-member values (S25). '
            f'MixSIAR, the current generation of Bayesian mixing models, returns a posterior of the proportions with '
            f'uncertain sources and covariates (S26); where the data do not identify the mixture, that posterior is '
            f'shaped by its prior (S11, S12). Bayesian unmixing now infers even the '
            f'number of end-members (B3); a second isotope with separated end-members narrows the answer (B4); ratios '
            f'cancel unknowns that samples share (C4); and source and path can be estimated jointly (C3). Uncertain '
            f'end-members remain the weak point.'))
    A(('p', f'**Ill-posed inversion** ({ids("inverse")}). Source identification in transport and the Bayesian theory of '
            f'inverse problems give the language of existence, uniqueness and stability, regularisation and posterior '
            f'consistency (S13–S15, S18, S21). Recent results bound how far a posterior moves when its prior moves '
            f'(C2), give contraction rates for Darcy flow (M4), prove stability for sparse identification (O5), compare '
            f'ensemble Kalman calibrations (C1), and use a second tracer to share transport errors (X1).'))
    A(('p', f'**Identification and design** ({ids("ident")}). Partial identification, developed in econometrics, '
            f'replaces a point by the set of values consistent with the data and the assumptions (S9–S12, H2); '
            f'assumption-free bounds are often wide, and their width measures what an answer owes to assumptions (H3). '
            f'Combining datasets collected under different conditions can restore identifiability (P4), and benchmarks '
            f'ask how sparse and noisy data may be (P3). Geophysics constrains where relict water can sit (O3).'))
    A(('p', f'**Learning** ({ids("learn")}). Neural networks and simulation-based inference learn the inverse map from '
            f'simulations, quickly and flexibly (S17): neural posterior estimation (X3), with adaptive priors (X4), for '
            f'water quality (O4) and for continental groundwater models (P2); physics-informed networks (M5, P3); field '
            f'inference (X2). Conformal methods give their intervals a finite-sample meaning in the world of the '
            f'simulations (S16, S24), and outside it learned intervals lose coverage (H4).'))
    A(('table', ['Route', 'What it delivers', 'What it assumes', 'What it does not deliver'], [
        ['Tracers', 'Fingerprints, qualitative attribution', 'Distinct end-members', 'Fractions with an error that is '
         'valid when fingerprints overlap'],
        ['Unmixing', 'Fractions of end-members; feasible ranges (IsoSource) or posteriors (MixSIAR)', 'Known, '
         'independent end-members, or a prior', 'An answer when the end-members are uncertain or too many that holds '
         'without a prior'],
        ['Ill-posed inversion', 'A regularised or posterior answer', 'A regulariser or a prior', 'A statement free of '
         'that choice'],
        ['Identification, design', 'Sets consistent with the data; informative data', 'A model of the data', 'Little '
         'used for chloride sources so far'],
        ['Learning', 'Fast inverse maps, calibrated in training', 'Training data that cover the truth', 'Validity in a '
         'world unlike the training set'],
    ], [3.0, 4.4, 4.2, 4.4], 9.0))
    A(('cap', 'Table {{routes}}. The five routes: what each gives and what each leaves out.'))
    # -------------------------------------------------------------------------------------------- 4 gap
    A(('h', '4. What remains open'))
    A(('b', '**An answer that is valid without a prior.** Bayesian and learned attributions are as good as their priors '
            'in the directions the data do not see, and for chloride sources those directions are the important ones '
            '(modern against relict seawater).'))
    A(('b', '**A plain statement that the data cannot decide**, sample by sample, and a test that a source is missing.'))
    A(('b', '**A rule for the next measurement** that values not only more tracers at the wells but also the sampling of '
            'the end-members themselves, for the decision at hand.'))
    A(('p', '**The nearest predecessors.** IsoSource (S25) already answers an underdetermined mixture with a range of '
            'feasible proportions, and is the closest relative of the identified set. It differs in four ways that '
            'matter here: the end-member values are fixed, so the range is valid only for the assumed signatures; the '
            'range is found by enumeration on a grid rather than exactly; the share of chloride, a ratio of '
            'contributions rather than a water fraction, is not bounded; and there is no coverage statement and no test '
            'for a missing source. MixSIAR (S26) treats the end-members as uncertain, but answers with a posterior whose '
            'credible intervals depend on the prior wherever the data do not identify the mixture (S11, S12). '
            'ZANAFILLA-GO keeps the range of IsoSource and the uncertain end-members of MixSIAR, and adds what neither '
            'gives: exact bounds over all signatures in their intervals, for the chloride share itself, with coverage '
            'that needs no prior and with an empty set as a falsification test.'))
    # -------------------------------------------------------------------------------------------- 5 ZANAFILLA-GO
    A(('h', '5. Our contribution: ZANAFILLA-GO'))
    A(('box', [
        '**Innovation.** ZANAFILLA-GO (*zanafilla* is Albanian for origin) answers "where does the chloride come from?" '
        'with the set of answers that the data and the stated assumptions allow, and with the measurement that would '
        'shrink it most for the decision. (1) *The identified set* of mixtures and signatures is an exact polytope, '
        'computed by linear programming, with sharp bounds on the share of each source. (2) *Well-posedness is restored '
        'by changing the object*: the set exists or proves a source missing, is unique, and is Lipschitz-stable in the '
        'data. (3) *Coverage needs no prior*. (4) *Goal-oriented design* compares tracers at wells with the sampling '
        'of end-members by the gain in decidability. (5) *Learning where it is safe*: an amortised network screens '
        'fast and is checked against the bounds.']))
    A(('h2', '5.1 The identified set'))
    A(('p', 'Write $c_{k}=f_{k}\\mathrm{Cl}_{k}$ for the chloride that source $k$ brings and $v_{tk}$ for its contribution '
            'to tracer $t$.'))
    A(('prop', 'Proposition 1 (the identified set is a polytope).',
       'The set of $(f,c,v)$ for which signatures in their intervals exist that reproduce the data within '
       '$\\varepsilon$ is'))
    A(('eq', 'poly', ['\\mathcal{P}(y)=\\Big\\{(f,c,v):\\ f\\ge 0,\\ \\textstyle\\sum_{k}f_{k}=1,\\ f\\le u,\\ '
                      '\\mathrm{Cl}_{k}^{-}f_{k}\\le c_{k}\\le\\mathrm{Cl}_{k}^{+}f_{k},',
                      '\\rho_{tk}^{-}c_{k}\\le v_{tk}\\le\\rho_{tk}^{+}c_{k}\\ \\text{or}\\ \\sigma_{tk}^{-}f_{k}\\le '
                      'v_{tk}\\le\\sigma_{tk}^{+}f_{k},\\ \\ \\Big|\\textstyle\\sum_{k}c_{k}-y_{\\mathrm{Cl}}\\Big|\\le'
                      '\\varepsilon_{\\mathrm{Cl}},\\ \\Big|\\textstyle\\sum_{k}v_{tk}-y_{t}\\Big|\\le\\varepsilon_{t}'
                      '\\Big\\}.']))
    A(('p', 'It is a convex polytope, exactly (not a relaxation), and the identified set of any quantity is its image.'))
    A(('proof', 'For a fixed $f_{k}\\ge 0$ the map $\\mathrm{Cl}_{k}\\mapsto f_{k}\\mathrm{Cl}_{k}$ sends the interval '
                '$[\\mathrm{Cl}_{k}^{-},\\mathrm{Cl}_{k}^{+}]$ onto $[\\mathrm{Cl}_{k}^{-}f_{k},\\mathrm{Cl}_{k}^{+}f_{k}]$; '
                'likewise for $\\rho_{tk}$ given $c_{k}\\ge 0$ and for $\\sigma_{tk}$ given $f_{k}\\ge 0$, also when '
                '$\\sigma_{tk}^{-}<0$. Different signatures enter different terms, so the attainable contributions form '
                'the product of these intervals, and the data constraints are linear in them. Conversely, a point of '
                '$\\mathcal{P}(y)$ with $f_{k}>0$ is produced by the signatures $\\mathrm{Cl}_{k}=c_{k}/f_{k}$, '
                '$\\rho_{tk}=v_{tk}/c_{k}$, $\\sigma_{tk}=v_{tk}/f_{k}$, which lie in their intervals; $f_{k}=0$ forces '
                '$c_{k}=v_{tk}=0$. When the signatures of one source are correlated across tracers (the meteoric water '
                'line, for example) $\\mathcal{P}(y)$ is an outer set: still valid, possibly wider.'))
    A(('h2', '5.2 Sharp bounds of a share'))
    A(('prop', 'Proposition 2 (sharp bounds by linear programming).',
       'Let $\\mathcal{P}(y)=\\{z: Az\\le b,\\ A_{\\mathrm{eq}}z=b_{\\mathrm{eq}}\\}$ and $y_{\\mathrm{Cl}}>'
       '\\varepsilon_{\\mathrm{Cl}}$. The identified interval of the share $s_{k}$ is $[s_{k}^{-},s_{k}^{+}]$ with'))
    A(('eq', 'cc', 's_{k}^{\\pm}=\\operatorname{opt}^{\\pm}\\Big\\{w_{c_{k}}:\\ Aw-b\\,\\tau\\le 0,\\ A_{\\mathrm{eq}}w-'
                   'b_{\\mathrm{eq}}\\tau=0,\\ \\textstyle\\sum_{j}w_{c_{j}}=1,\\ \\tau\\ge 0\\Big\\},'))
    A(('p', 'two linear programmes, and both bounds are attained by points of $\\mathcal{P}(y)$.'))
    A(('proof', 'On $\\mathcal{P}(y)$ the denominator $\\sum_{j}c_{j}\\ge y_{\\mathrm{Cl}}-\\varepsilon_{\\mathrm{Cl}}>0$. '
                'The change of variables $w=z/\\sum_{j}c_{j}$, $\\tau=1/\\sum_{j}c_{j}$ of Charnes and Cooper (S8) maps '
                '$\\mathcal{P}(y)$ one to one onto the feasible set of [[cc]] and the share onto the linear objective '
                '$w_{c_{k}}$. A bounded linear programme attains its optimum at a vertex.'))
    A(('h2', '5.3 Well-posedness restored'))
    A(('prop', 'Proposition 3 (Hadamard\'s conditions for the set).',
       '(i) *Existence.* If the source list is complete, the true signatures lie in their intervals, the caps hold and '
       'the errors are within $\\varepsilon$, the truth lies in $\\mathcal{P}(y)$, which is therefore non-empty. An '
       'empty set, certified by a Farkas certificate of the linear programme, proves that one of these assumptions is '
       'false: a falsification test, in particular of the source list. (ii) *Uniqueness.* $\\mathcal{P}(y)$ is a single '
       'set determined by the data, not a choice among minimisers. (iii) *Stability.* For data $y,y\'$ with non-empty '
       'sets, $d_{H}(\\mathcal{P}(y),\\mathcal{P}(y\'))\\le\\kappa\\,\\|y-y\'\\|$, with $\\kappa$ a Hoffman constant of '
       'the constraint matrix (S7), independent of the data; every bound of a linear functional moves by at most '
       '$\\kappa\\|g\\|\\,\\|y-y\'\\|$, and the bounds of a share are Lipschitz while $y_{\\mathrm{Cl}}-'
       '\\varepsilon_{\\mathrm{Cl}}$ stays away from zero.'))
    A(('proof', '(i) and (ii) are immediate from Proposition 1. For (iii), the data enter only the right-hand side, '
                '$b(y)=b_{0}+By$. For $z\\in\\mathcal{P}(y)$, Hoffman\'s bound gives $\\operatorname{dist}(z,\\mathcal{P}'
                '(y\'))\\le\\kappa\\,\\|(Az-b(y\'))_{+}\\|\\le\\kappa\\|B\\|\\,\\|y-y\'\\|$, and symmetrically. A '
                'linear-fractional function is Lipschitz on a set where its denominator is bounded below.'))
    A(('p', 'The point inverse has none of these properties. With fixed signatures its solution is unique only when the '
            'end-member matrix has full column rank, and its Lipschitz constant is the inverse of the smallest singular '
            'value, which is unbounded when two sources look alike. With uncertain signatures it is not even defined: '
            'each admissible choice gives another answer (Figure {{point}}). ZANAFILLA-GO restores well-posedness not '
            'by adding information that is not there, but by asking for the object the data do determine.'))
    A(('h2', '5.4 What a prior can and cannot add'))
    A(('prop', 'Proposition 4 (coverage without a prior).',
       'Under the assumptions of Proposition 3(i), with $P(|e_{t}|>\\varepsilon_{t})\\le\\alpha_{t}$ for each tracer, '
       '$P\\big(s_{k}\\in[s_{k}^{-},s_{k}^{+}]\\big)\\ge 1-\\sum_{t}\\alpha_{t}$ for every distribution of fractions and '
       'signatures. With $\\varepsilon_{t}=2.5\\,\\mathrm{sd}_{t}$ and Gaussian errors, $\\alpha_{t}=0.0124$ and the bound '
       'is at least 0.91 for seven tracers.'))
    A(('proof', 'On the event that every error is within its $\\varepsilon_{t}$ the truth is in $\\mathcal{P}(y)$, and the '
                'interval contains its share; the probability of the complement is at most $\\sum_{t}\\alpha_{t}$ by the '
                'union bound.'))
    A(('p', 'A Bayesian answer is different in kind. As the noise vanishes, the posterior of a partially identified '
            'quantity does not concentrate on its true value but on the prior restricted to the identified set (S12, '
            'S11): its credible interval is as right as the prior inside the set, and no amount of the same data '
            'corrects it. A network trained on simulations inherits the same property from its training distribution.'))
    A(('h2', '5.5 Which measurement next'))
    A(('prop', 'Proposition 5 (goal-oriented design of tracers and end-members).',
       'Adding a tracer, narrowing a signature interval by sampling an end-member, or adding a site constraint can only '
       'shrink $\\mathcal{P}(y)$. For the rule "act if $s_{k}>\\theta$" let $D=\\mathbf{1}\\{s_{k}^{-}>\\theta\\ '
       '\\text{or}\\ s_{k}^{+}<\\theta\\}$ mark a decidable sample. The value of an action $a$ is'))
    A(('eq', 'value', '\\Delta(a)=\\mathbb{E}_{\\pi}\\big[D_{a}\\big]-\\mathbb{E}_{\\pi}\\big[D_{0}\\big],'))
    A(('p', 'computed by simulation under a planning distribution $\\pi$, and the next action is the one with the largest '
            '$\\Delta(a)$ per unit cost. The prior enters the choice of what to measure, never the certificate itself: a '
            'wrong $\\pi$ makes the design less efficient, not the answer less valid. Monotonicity follows because each '
            'action adds or tightens linear constraints, so the new set is a subset of the old.'))
    A(('h2', '5.6 Learning, where it is safe'))
    A(('p', 'A neural network $q_{\\theta}(y)$ with three outputs is trained on simulated pairs (tracers, share) to '
            'predict the 5%, 50% and 95% quantiles of the share; the interval is then widened by conformalised quantile '
            'regression on fresh simulations (S24), which gives 90% coverage *in the world of the simulations*. The '
            'network answers in microseconds and is sharp. ZANAFILLA-GO uses it for screening and checks it against the '
            'certificate: an interval that leaves $[s_{k}^{-},s_{k}^{+}]$ is flagged, and the reported answer is the '
            'intersection. Simulation-based inference (S17) belongs here; so do neural operators and physics-informed '
            'networks as fast forward models in the design loop.'))
    A(('img', 'scheme', 15.5))
    A(('cap', 'Figure {{scheme}}. ZANAFILLA-GO. The data and the stated assumptions define a polytope; its bounds decide or '
              'say that the data cannot decide; the design loop chooses what to measure next; a learned estimator '
              'screens, checked against the bounds.'))
    A(('h2', '5.7 Why this is ours to do'))
    A(('p', 'The chloride study of Fushë-Kuqe (D2) found active salinisation at the coast and freshening in the centre of '
            'the plain from the base-exchange index, and the companion design paper (D1) chose monitoring for the '
            'decision rather than for the wedge. Earlier innovations of this code base asked which processes are '
            'identifiable from regimes and stoichiometry, and how to decide while the source is unknown (D3). '
            'ZANAFILLA-GO adds what was missing between them: an attribution that is honest about what the data cannot '
            'tell, and a design that knows when the next measurement should be at the source rather than at the well.'))
    # -------------------------------------------------------------------------------------------- 6 the test
    A(('h', '6. A numerical test'))
    A(('h2', '6.1 Setting'))
    A(('p', f'A synthetic coastal aquifer has twelve wells between 0.4 and 10 km from the coast, each with an upper screen '
            f'(40 m) and a lower screen (110 m) (Figure {{{{aquifer}}}}). In every random field a modern seawater wedge '
            f'with a mixing zone advances from the coast, a relict pocket of variable strength lies at depth further '
            f'inland, a halite body exists in one field in ten, and anthropogenic water reaches the upper screens under '
            f'a town. Signatures are drawn inside the intervals of Table {{{{sig}}}}, which are illustrative, chosen '
            f'from ranges of the literature: narrow for the sea and the upgradient fresh water, which can be sampled, '
            f'wide for the relict water and a halite brine, which usually are not. Tracers are measured with errors '
            f'(3% for chloride, 5% for bromide and boron, 0.1‰ for δ¹⁸O, 1‰ for δ²H, 0.3 TU and 5% for tritium, 2% '
            f'on the major ions for the base-exchange index), and the identified sets use $\\varepsilon_{{t}}=2.5$ '
            f'standard deviations. The decision rule is "most of the chloride is modern seawater" ($s_{{\\mathrm{{MS}}}}>'
            f'0.5$), evaluated at the {s["n_e1"]} salinised screens (chloride above 150 mg/L) of 40 fields.'))
    A(('img', 'aquifer', 16.0))
    A(('cap', 'Figure {{aquifer}}. The synthetic aquifer (schematic) and the screens of one field, coloured by the true '
              'share of chloride from modern seawater.'))
    sig = R['settings']['signatures']
    rows = []
    lab = {'Cl': 'Cl, mg/L', 'BrCl': 'Br/Cl (mass, ×10⁻³)', 'BCl': 'B/Cl (mass, ×10⁻⁴)', 'BEXCl': 'BEX/Cl (meq per g Cl)',
           'd18O': 'δ¹⁸O, ‰', 'd2H': 'δ²H, ‰', 'H3': 'tritium, TU'}
    scale = {'Cl': 1, 'BrCl': 1e3, 'BCl': 1e4, 'BEXCl': 1e3, 'd18O': 1, 'd2H': 1, 'H3': 1}
    for key in ('Cl', 'BrCl', 'BCl', 'BEXCl', 'd18O', 'd2H', 'H3'):
        def fmt(v):
            v = v * scale[key]
            return (f'{v:,.0f}'.replace(',', ' ') if abs(v) >= 100 else f'{v:.2f}'.rstrip('0').rstrip('.')).replace('-', '−')
        rows.append([lab[key]] + [f'{fmt(a)} to {fmt(b)}' for a, b in sig[key]])
    A(('table', ['Signature', 'Modern seawater', 'Relict seawater', 'Halite brine', 'Anthropogenic', 'Fresh recharge'],
       rows, [3.4, 2.6, 2.6, 2.6, 2.6, 2.6], 8.6))
    A(('cap', 'Table {{sig}}. Signature intervals of the five sources in the test (illustrative). Site caps: '
              'anthropogenic water at most 35% of an upper screen under the town, 8% elsewhere, 2% at depth; halite brine '
              'only at depth, at most 3%.'))
    A(('h2', '6.2 Checks'))
    A(('p', f'The linear programmes were checked against brute force on {s["e6_n"]} samples: fractions and signatures '
            f'drawn at random, the draws that reproduce the data kept, and their range of the share compared with the '
            f'bounds. The sampled range lies inside the bounds in every case. It reaches the upper bounds (largest gap '
            f'{s["e6_gap"]}) but not always the lower ones (largest gap {s["e6_gap_lo"]}): these are attained at '
            f'vertices of the polytope, which random draws rarely hit, and this is why the bounds are computed by '
            f'linear programming rather than by sampling. Over '
            f'all configurations the identified intervals contained the truth in at least {s["cov_min"]} of the '
            f'samples, above the guaranteed 91%, and no decidable sample was decided wrongly (largest share of wrong '
            f'decisions {s["wrong_max"]}).'))
    A(('h2', '6.3 What the test shows'))
    A(('p', f'**Today\'s kind of data cannot say where the chloride comes from.** With chloride alone the identified '
            f'interval of the modern-seawater share has a mean width of {s["cl_w"]}: nothing is identified. The major '
            f'ions, through the base-exchange index, narrow it to {s["today_w"]} and decide {s["today_d"]} of the '
            f'samples (Figure {{{{intervals}}}}a). This is the honest answer, and it is what a model that returns a '
            f'single number hides.'))
    A(('img', 'intervals', 16.5))
    A(('cap', 'Figure {{intervals}}. Identified intervals of the share of chloride from modern seawater at the salinised '
              'screens of one field, for three levels of information. Green: the interval excludes 0.5 and the decision '
              'can be taken; grey: the data cannot decide.'))
    A(('p', f'**More tracers at the wells help little; sampling the end-members helps much.** Seven tracers at every '
            f'well (adding bromide, δ¹⁸O, δ²H, tritium and boron) raise the decidable share only to {s["all_d"]} '
            f'(mean width {s["all_w"]}). The reason is the relict seawater: it shares the marine Cl/Br of the modern '
            f'sea, and its other signatures are wide because nobody has sampled it. Sampling the relict water raises '
            f'the decidable share to {s["rel_all_d"]} with the same seven tracers; sampling the fresh water too, to '
            f'{s["rf_all_d"]} (mean width {s["rf_all_w"]}); the anthropogenic end-member adds little more '
            f'({s["rfa_all_d"]}) (Figure {{{{value}}}}). The gain depends on the place: at the lower screens near the '
            f'coast decidability goes from {s["cl_coast_lo_0"]} to {s["cl_coast_lo_1"]}, at the upper screens inland '
            f'from {s["cl_inl_up_0"]} to {s["cl_inl_up_1"]}, where anthropogenic and fresh water dominate and the '
            f'question is rarely "modern seawater or not".'))
    A(('img', 'value', 16.5))
    A(('cap', 'Figure {{value}}. Share of the salinised samples whose identified interval excludes the threshold, for every '
              'combination of tracers at the wells (columns, cumulative) and of sampled end-members (rows); w is the '
              'mean width of the interval. This is the table from which Proposition 5 chooses the next action.'))
    A(('p', f'**The point inverse is unreliable in a way it cannot see.** Least squares with the central signatures '
            f'misses the true share by a median of {s["ls_mae"]} and by more than 0.25 in {s["ls_big"]} of the '
            f'{s["n_e5"]} samples, and puts {s["ls_side"]} on the wrong side of the threshold. Moving the signatures '
            f'inside their intervals moves its answer by {s["ls_spread"]} on average, and even the range of these '
            f'answers misses the truth in {s["ls_out"]} of the samples; the identified interval never does '
            f'({s["set_out"]}) (Figure {{{{point}}}}).'))
    A(('img', 'point', 16.5))
    A(('cap', 'Figure {{point}}. The least-squares answer against the identified interval for forty salinised samples '
              '(seven tracers, no end-member sampled), ordered by the true share.'))
    A(('p', f'**The network is sharp and right where it was trained, and wrong elsewhere.** Trained on '
            f'{s["nn_ntrain"]} simulated samples and calibrated on {s["nn_ncal"]}, the network with seven tracers covers '
            f'{s["nn_cov_a0"]} of the truths with intervals of mean width {s["nn_w_a0"]} in the world it was trained '
            f'for. In a world with more relict seawater and halite more often, with the same sources and signature '
            f'intervals, its coverage falls to {s["nn_cov_a1"]} and {s["nn_wrong_a1"]} of the decisions it takes are '
            f'wrong; with today\'s tracers the fall is from {s["nn_cov_t0"]} to {s["nn_cov_t1"]}, with '
            f'{s["nn_wrong_t1"]} wrong decisions. The identified intervals cover {s["ce_cov_a1"]} in the shifted world '
            f'(Figure {{{{nn}}}}). The check against the certificate flags the worst cases: where the network\'s interval '
            f'leaves the identified interval ({s["nn_out_a1"]} of the samples), its coverage is {s["nn_cov_out_a1"]}.'))
    A(('img', 'nn', 16.0))
    A(('cap', 'Figure {{nn}}. Coverage of the true share by the network\'s conformal intervals and by the identified '
              'intervals, in the world the network was trained for and in a shifted world; w is the mean width.'))
    A(('p', f'**A missing source is detected.** When a bromide-rich deep brine that is not in the list of sources '
            f'contributes more than 0.5% of the water ({s["n_brine"]} samples), the polytope is empty, and the source '
            f'list is thereby refuted, in {s["miss_0"]} of these samples with seven tracers, and in {s["miss_1"]} when '
            f'the relict and fresh water have been sampled. When the list is complete the set is empty in '
            f'{s["false_0"]} and {s["false_1"]} of the samples. A least-squares or a learned answer returns a number in '
            f'every case.'))
    A(('h2', '6.4 What the test does not show'))
    A(('b', 'The aquifer, the sources and the signature intervals are synthetic and illustrative. The numbers say how the '
            'method behaves, not how decidable the Fushë-Kuqe chloride is.'))
    A(('b', 'A first version of the test, with wide intervals also for the sea and the fresh water and without the '
            'site caps, identified nothing with any tracer set (mean width of the share above 0.9). The intervals of '
            'these two end-members were then narrowed, because they can be sampled, and the caps of land use and '
            'geology were added. The result is itself a finding: without end-member knowledge, more tracers do not '
            'decide.'))
    A(('b', 'Signatures of one source are treated as independent across tracers; correlated signatures would give '
            'smaller sets.'))
    A(('b', 'The design values are averages over a planning distribution; costs of the actions were not modelled.'))
    A(('b', 'The transport between sources and wells enters only through the site caps; an adjoint of a flow model '
            '(S18, D1) would add linear constraints across wells and is the next step.'))
    # -------------------------------------------------------------------------------------------- 7 Fushë-Kuqe
    A(('h', '7. What it means for Fushë-Kuqe'))
    A(('p', 'The data of Fushë-Kuqe today are chloride and the major ions at a few wells (S6, D2). The test says what to '
            'expect from them: a few samples decided, most not. It also says what the chloride study already found '
            'qualitatively: the coastal wells show a sodium deficit (base-exchange index about −2.7 meq/L) and the '
            'central well a sodium excess (+2.4 meq/L), so the coast is salinising and the centre is freshening (D2). '
            'In ZANAFILLA-GO these signs are not a story but linear constraints, and they bound the shares of modern '
            'and relict seawater from one side.'))
    A(('p', 'The next campaign, in the order of the test:'))
    A(('b', '**Sample the end-members first.** Pore water of the silt–clay layers (by coring or a dedicated piezometer) '
            'for the relict signature, and upgradient fresh water; Adriatic water for the sea. In the test this is what '
            'turns undecidable samples into decidable ones.'))
    A(('b', '**Then add bromide, δ¹⁸O and δ²H, and boron** at the salinised wells and at both depths where screens allow. '
            'They are inexpensive and they separate the marine sources from halite and from anthropogenic chloride.'))
    A(('b', '**Tritium only where the age of the water matters**, for instance to tell modern recharge from old water at '
            'the wells of the central field.'))
    A(('b', '**Report sets, not numbers.** For each well: the identified interval of the share of modern seawater, '
            'whether the decision is possible, and, when the set is empty, that a source is missing.'))
    # -------------------------------------------------------------------------------------------- 8 the papers
    A(('h', '8. The thirty papers'))
    A(('p', 'Thirty papers of 2020–2026 with authors at Oxford, Caltech, MIT, Princeton, the Max Planck Society, Harvard '
            'and Berkeley. Candidates were found through Crossref and web searches by topic and affiliation; each was '
            'confirmed by the Crossref record of its DOI, with the affiliation on the paper itself; none was used as a '
            'card in an earlier review of this series. Each card states what the paper does (from its abstract), how '
            'it bears on the origin of chloride, what it leaves open, and the innovation step for us.'))
    rname = dict(tracers='tracers', mixing='unmixing', inverse='ill-posed inversion', ident='identification, design',
                 learn='learning')

    def short_authors(c):
        fam = [a.strip().split(' ')[-1] for a in c['authors'].split(',')]
        return fam[0] + ' et al.' if len(fam) > 3 else (', '.join(fam[:-1]) + ' & ' + fam[-1] if len(fam) > 1 else fam[0])
    A(('table', ['', 'Paper', 'Journal', 'Route'],
       [[c['id'], f"{short_authors(c)} ({c['year']}). [{c['title']}]({c['links'][0][1]})",
         re.sub(r'\s*\(\d{4}[^)]*\)$', '', c['venue']), ', '.join(rname[r] for r in c['routes'])] for c in cards],
       [0.9, 9.1, 4.1, 2.9], 8.6, False))
    A(('cap', 'Table {{list}}. The thirty papers at a glance; the titles are links to the DOI.'))
    heads = {'Oxford': 'University of Oxford', 'Caltech': 'California Institute of Technology',
             'MIT': 'Massachusetts Institute of Technology', 'Princeton': 'Princeton University',
             'Max Planck': 'Max Planck Society', 'Harvard': 'Harvard University', 'Berkeley': 'University of California, Berkeley'}
    k = 0
    for inst in INST_ORDER:
        cs = [c for c in cards if c['inst'] == inst]
        if not cs:
            continue
        k += 1
        A(('h2', f'8.{k} {heads[inst]}'))
        for c in cs:
            A(('card', c))
    A(('refs',))
    return B, s, cards
