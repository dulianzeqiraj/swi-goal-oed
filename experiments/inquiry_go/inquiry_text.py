"""Text of the proposal "INQUIRY-GO: the decisive question" (English).
blocks(R, ION) returns the block list. R = res/inquiry_poc.json (synthetic test) or None; ION = the output of
fk_ions.py (field chemistry, not in the public repository) or None. Every number is computed from these."""
import numpy as np

try:                                   # field statements: a private module, not in the public repository
    import fk_private_text as P
except ImportError:
    P = None

POL = ['random', 'D-optimal', 'goal variance', 'widest outcome', 'INQUIRY', 'hybrid']
SRC_NAME = {'MS': 'the sea', 'RS': 'legacy salinity', 'DB': 'deep water', 'AN': 'the anthropogenic load',
            'LG': 'the lagoon'}
TR_NAME = {'Cl': 'chloride', 'Br': 'bromide', 'd18O': 'oxygen-18', 'H3': 'tritium'}

REFS = [
    ('KN25', 'Koval, K. & Nicholson, R. (2025). Non-intrusive optimal experimental design for large-scale nonlinear '
             'Bayesian inverse problems using a Bayesian approximation error approach. Journal of Scientific '
             'Computing 104(3), 98.', 'https://doi.org/10.1007/s10915-025-03008-7'),
    ('G26', 'Gruhlke, R., Hanu, M., Schillings, C. & Wacker, P. (2026). Gradient-free sequential Bayesian '
            'experimental design via interacting particle systems. SIAM/ASA Journal on Uncertainty Quantification '
            '14(2), 415–455.', 'https://doi.org/10.1137/25M1771946'),
    ('S25', 'Hedman, M., Ivanova, D. R., Guan, C. & Rainforth, T. (2025). Step-DAD: semi-amortized policy-based '
            'Bayesian experimental design. Proceedings of the 42nd International Conference on Machine Learning, '
            'PMLR 267.', 'https://arxiv.org/abs/2507.14057'),
    ('HMR', 'Helin, T., Marzouk, Y. & Rojo-Garcia, J. R. (2026). Bayesian optimal experimental design with '
            'Wasserstein information criteria. Preprint arXiv:2504.10092v2.', 'https://arxiv.org/abs/2504.10092'),
    ('B22', 'Bartuska, A., Espath, L. & Tempone, R. (2022). Small-noise approximation for Bayesian optimal '
            'experimental design with nuisance uncertainty. Computer Methods in Applied Mechanics and Engineering '
            '399, 115320.', 'https://doi.org/10.1016/j.cma.2022.115320'),
    ('C26', 'Chowdhary, A., Attia, A. & Alexanderian, A. (2026). Robust optimal experimental design of '
            'infinite-dimensional Bayesian nonlinear inverse problems. SIAM Journal on Scientific Computing 48(2), '
            'B262–B288.', 'https://doi.org/10.1137/24M1693921'),
    ('H24', 'Huan, X., Jagalur, J. & Marzouk, Y. (2024). Optimal experimental design: formulations and computations. '
            'Acta Numerica 33, 715–840.', 'https://doi.org/10.1017/S0962492924000023'),
    ('A21', 'Alexanderian, A. (2021). Optimal experimental design for infinite-dimensional Bayesian inverse problems '
            'governed by PDEs: a review. Inverse Problems 37(4), 043001.', 'https://doi.org/10.1088/1361-6420/abe10c'),
    ('ZT21', 'Zhou, Z. & Tartakovsky, D. M. (2021). Markov chain Monte Carlo with neural network surrogates: '
             'application to contaminant source identification. Stochastic Environmental Research and Risk '
             'Assessment 35(3), 639–651.', 'https://doi.org/10.1007/s00477-020-01888-9'),
    ('SF14', 'Scott, J. K., Findeisen, R., Braatz, R. D. & Raimondo, D. M. (2014). Input design for guaranteed fault '
             'diagnosis using zonotopes. Automatica 50(6), 1580–1589.', 'https://doi.org/10.1016/j.automatica.2014.03.016'),
    ('PW89', 'Pronzato, L. & Walter, E. (1989). Experiment design in a bounded-error context: comparison with '
             'D-optimality. Automatica 25(3), 383–391.', 'https://doi.org/10.1016/0005-1098(89)90006-X'),
    ('PT23', 'Pham, H. V. & Tsai, F. T.-C. (2023). A robust experimental design for conceptual model discrimination '
             'based on information theory. Advances in Water Resources 178, 104485.',
     'https://doi.org/10.1016/j.advwatres.2023.104485'),
    ('PT16', 'Pham, H. V. & Tsai, F. T.-C. (2016). Optimal observation network design for conceptual model '
             'discrimination and uncertainty reduction. Water Resources Research 52(2), 1245–1264.',
     'https://doi.org/10.1002/2015WR017474'),
    ('K15', 'Kikuchi, C. P., Ferré, T. P. A. & Vrugt, J. A. (2015). On the optimal design of experiments for '
            'conceptual and predictive discrimination of hydrologic system models. Water Resources Research 51(6), '
            '4454–4481.', 'https://doi.org/10.1002/2014WR016795'),
    ('KV89', 'Knopman, D. S. & Voss, C. I. (1989). Multiobjective sampling design for parameter estimation and model '
             'discrimination in groundwater solute transport. Water Resources Research 25(10), 2245–2258.',
     'https://doi.org/10.1029/WR025i010p02245'),
    ('NG16', 'Nowak, W. & Guthke, A. (2016). Entropy-based experimental design for optimal model discrimination in '
             'the geosciences. Entropy 18(11), 409.', 'https://doi.org/10.3390/e18110409'),
    ('C15', 'Chen, Y., Javdani, S., Karbasi, A., Bagnell, J. A., Srinivasa, S. & Krause, A. (2015). Submodular '
            'surrogates for value of information. Proceedings of the AAAI Conference on Artificial Intelligence '
            '29(1).', 'https://doi.org/10.1609/aaai.v29i1.9694'),
    ('F26', 'Fotias, S.-P. (2026). Resolution-aware experimental design under partial identifiability. Preprint '
            'arXiv:2609.03686 (not read; known from a search summary).', 'https://arxiv.org/abs/2609.03686'),
    ('Fa18', 'Fadili, A., Malaurent, P., Najib, S., Mehdi, K., Riss, J. & Makan, A. (2018). Groundwater hydrodynamics '
             'and salinity response to oceanic tide in coastal aquifers: case study of Sahel Doukkala, Morocco. '
             'Hydrogeology Journal 26(7), 2459–2473.', 'https://doi.org/10.1007/s10040-018-1812-4'),
    ('RG87', 'Reilly, T. E. & Goodman, A. S. (1987). Analysis of saltwater upconing beneath a pumping well. Journal of '
             'Hydrology 89(3–4), 169–204.', 'https://doi.org/10.1016/0022-1694(87)90179-X'),
    ('At25', 'Attia, M., Tsai, F. T.-C., Yang, S., Minsley, B. J. & Kress, W. H. (2025). Airborne geophysical analysis '
             'to decipher salinization for coastal Louisiana. Water Research 275, 123215.',
     'https://doi.org/10.1016/j.watres.2025.123215'),
    ('Mi26', 'Minsley, B. J., Michael, H. A., Lindaman, M. A., Ball, L. B., James, S. R., Rigby, J., Kress, W. H. & '
             'Tsai, F. T.-C. (2026). The saline groundwater legacy of a large buried coastal paleo-estuary. Nature '
             'Communications 17, 9119.', 'https://doi.org/10.1038/s41467-026-76005-5'),
    ('Ba17', 'Bardsley, E. (2017). A nonparametric approach toward upper bounds to transit time distribution '
             'functions. Hydrology and Earth System Sciences Discussions (preprint).',
     'https://doi.org/10.5194/hess-2017-404'),
    ('Ma14', 'Massoudieh, A., Visser, A., Sharifi, S. & Broers, H. P. (2014). A Bayesian modeling approach for '
             'estimation of a shape-free groundwater age distribution using multiple tracers. Applied Geochemistry '
             '50, 252–264.', 'https://doi.org/10.1016/j.apgeochem.2013.10.004'),
    ('Ju21', 'Ju, Y., Massoudieh, A., Green, C. T., Lee, K.-K. & Kaown, D. (2021). Complexity of groundwater age '
             'mixing near a seawater intrusion zone based on multiple tracers and Bayesian inference. Science of the '
             'Total Environment 753, 141994.', 'https://doi.org/10.1016/j.scitotenv.2020.141994'),
    ('St25', 'Stuyfzand, P. J., Nienhuis, P. R. & Post, V. E. A. (2025). Radiocarbon age dating and quality evolution '
             'of seawater intruding beneath a freshwater lens. Applied Geochemistry 193, 106564.',
     'https://doi.org/10.1016/j.apgeochem.2025.106564'),
    ('Li17', 'Li, J., Liang, X., Zhang, Y., Liu, Y., Chen, N., Abubakari, A. & Jin, M. (2017). Salinization of '
             'porewater in a multiple aquitard-aquifer system in Jiangsu coastal plain, China. Hydrogeology Journal '
             '25(8), 2377–2390.', 'https://doi.org/10.1007/s10040-017-1622-0'),
    ('Av04', 'Avisar, D., Rosenthal, E., Shulman, H., Zilberbrand, M., Flexer, A., Kronfeld, J., Ben Avraham, Z. & '
             'Fleischer, L. (2004). The Pliocene Yafo Formation in Israel: hydrogeologically inert or active? '
             'Hydrogeology Journal 12(3), 291–304.', 'https://doi.org/10.1007/s10040-004-0322-8'),
    ('AF75', 'Atkinson, A. C. & Fedorov, V. V. (1975). The design of experiments for discriminating between two rival '
             'models. Biometrika 62(1), 57–70.', 'https://doi.org/10.1093/biomet/62.1.57'),
    ('R21', 'Rothenhäusler, D., Meinshausen, N., Bühlmann, P. & Peters, J. (2021). Anchor regression: heterogeneous '
            'data meet causality. Journal of the Royal Statistical Society Series B 83(2), 215–246.',
     'https://doi.org/10.1111/rssb.12398'),
    ('PW84', 'Protter, M. H. & Weinberger, H. F. (1984). Maximum principles in differential equations. Springer, '
             'New York.', 'https://doi.org/10.1007/978-1-4612-5282-5'),
    ('E02', 'Edelsbrunner, H., Letscher, D. & Zomorodian, A. (2002). Topological persistence and simplification. '
            'Discrete & Computational Geometry 28(4), 511–533.', 'https://doi.org/10.1007/s00454-002-2885-2'),
    ('BP05', 'Bertsimas, D. & Popescu, I. (2005). Optimal inequalities in probability theory: a convex optimization '
             'approach. SIAM Journal on Optimization 15(3), 780–804.', 'https://doi.org/10.1137/S1052623401399903'),
    ('V13', 'Visser, A., Broers, H. P., Purtschert, R., Sültenfuß, J. & de Jonge, M. (2013). Groundwater age '
            'distributions at a public drinking water supply well field derived from multiple age tracers (85Kr, '
            '3H/3He, and 39Ar). Water Resources Research 49(11), 7778–7796.', 'https://doi.org/10.1002/2013WR014012'),
    ('S05', 'Sivan, O., Yechieli, Y., Herut, B. & Lazar, B. (2005). Geochemical evolution and timescale of seawater '
            'intrusion into the coastal aquifer of Israel. Geochimica et Cosmochimica Acta 69(3), 579–592.',
     'https://doi.org/10.1016/j.gca.2004.07.023'),
    ('L17', 'Levanon, E., Yechieli, Y., Gvirtzman, H. & Shalev, E. (2017). Tide-induced fluctuations of salinity and '
            'groundwater level in unconfined aquifers: field measurements and numerical model. Journal of Hydrology '
            '551, 665–675.', 'https://doi.org/10.1016/j.jhydrol.2016.12.045'),
    ('D86', 'Desaulniers, D. E., Kaufmann, R. S., Cherry, J. A. & Bentley, H. W. (1986). 37Cl–35Cl variations in a '
            'diffusion-controlled groundwater system. Geochimica et Cosmochimica Acta 50(8), 1757–1764.',
     'https://doi.org/10.1016/0016-7037(86)90137-7'),
    ('SKF18', 'Smith, R., Knight, R. & Fendorf, S. (2018). Overpumping leads to California groundwater arsenic '
              'threat. Nature Communications 9, 2089.', 'https://doi.org/10.1038/s41467-018-04475-3'),
    ('E13', 'Erban, L. E., Gorelick, S. M., Zebker, H. A. & Fendorf, S. (2013). Release of arsenic to deep '
            'groundwater in the Mekong Delta, Vietnam, linked to pumping-induced land subsidence. Proceedings of the '
            'National Academy of Sciences 110(34), 13751–13756.', 'https://doi.org/10.1073/pnas.1300503110'),
    ('WJ12', 'Wang, Y. & Jiao, J. J. (2012). Origin of groundwater salinity and hydrogeochemical processes in the '
             'confined Quaternary aquifer of the Pearl River Delta, China. Journal of Hydrology 438–439, 112–124.',
     'https://doi.org/10.1016/j.jhydrol.2012.03.008'),
    ('Mi08', 'Millero, F. J., Feistel, R., Wright, D. G. & McDougall, T. J. (2008). The composition of Standard '
             'Seawater and the definition of the Reference-Composition Salinity Scale. Deep-Sea Research Part I '
             '55(1), 50–72.', 'https://doi.org/10.1016/j.dsr.2007.10.001'),
    ('M13', 'Mollema, P. N., Antonellini, M., Dinelli, E., Gabbianelli, G., Greggio, N. & Stuyfzand, P. J. (2013). '
            'Hydrochemical and physical processes influencing salinization and freshening in Mediterranean low-lying '
            'coastal environments. Applied Geochemistry 34, 207–221.', 'https://doi.org/10.1016/j.apgeochem.2013.03.017'),
    ('J25', 'Jahn, E., Eberhardt, F. & Schulman, L. J. (2025). Lower bounds on the size of Markov equivalence '
            'classes. Proceedings of the 41st Conference on Uncertainty in Artificial Intelligence (UAI 2025), '
            'PMLR 244, 1819–1836.', None),
    ('T23', 'Tibshirani, R. (2023). Conformal prediction. Lecture notes, Advanced Topics in Statistical Learning, '
            'Spring 2023 (file provided by the author of this note).', None),
    ('CB16', 'Cenameri, S. & Beqiraj, A. (2016). Assessment of seawater intrusion in Fushë Kuqe aquifer, Albania. '
             'Bulletin of the Geological Society of Greece 50(2), 665–670.', 'https://doi.org/10.12681/bgsg.11772'),
    ('N', 'Zeqiraj, D. (October–November 2026). Notes and code in the repository swi-goal-oed, folder experiments: '
          'ORIGIN-GO (review "Where does the chloride come from?"), HYPOTHESIS-GO ("Hypotheses as terms of the '
          'differential equations", and its application "Where does the chloride of Fushë-Kuqe come from?", '
          'internal), TRACE-GO (multi-species transport with a stoichiometric closure), ANCHOR-GO (a chloride alarm '
          'built on anchor regression), PROVENANCE-GO (decisions under an unknown chloride source) and the review '
          '"State of the art IV: when the simulator is wrong".',
     'https://github.com/dulianzeqiraj/swi-goal-oed'),
    ('DATA', 'Fushe_Kuqe_All_Data.xlsx: the chemistry sheets compiled from CB16; property of the Albanian Geological '
             'Survey and of A. Beqiraj, used with their permission.', None),
]


def num(x, d=2):
    return f'{x:.{d}f}'.replace('-', '−')


def sgn(x, d=2):
    return ('+' if x > 0 else '') + num(x, d)


def stats(R):
    runs = [r for r in R['runs'] if not r['skip']]
    out = dict(N=len(runs), skip=len(R['runs']) - len(runs), fits=sum(r['truth_fits'] for r in runs),
               n0=[r['n0'] for r in runs], goal={}, first={})
    for r in runs:
        out['goal'][r['goal'][1]] = out['goal'].get(r['goal'][1], 0) + 1
        if r['pol']['INQUIRY']['asked']:
            t = r['pol']['INQUIRY']['asked'][0][0]
            out['first'][t] = out['first'].get(t, 0) + 1
    out['d1'] = [r['pol']['INQUIRY']['info'][0] or 0.0 for r in runs if r['pol']['INQUIRY']['info']]
    out['dec1'] = sum(1 for v in out['d1'] if v >= 1 - 1e-9)
    out['allopen'] = sum(1 for r in runs if all(r['pol'][p]['verdict'] not in ('yes', 'no') for p in POL))
    for p in POL:
        dec = [r['pol'][p]['n'] if r['pol'][p]['verdict'] in ('yes', 'no') else None for r in runs]
        out[p] = dict(cum=[sum(1 for d in dec if d is not None and d <= k) for k in range(1, R['maxq'] + 1)],
                      wrong=sum(1 for r in runs if r['pol'][p]['verdict'] in ('yes', 'no')
                                and r['pol'][p]['verdict'] != r['true_verdict']),
                      empty=sum(1 for r in runs if r['pol'][p]['verdict'] == 'empty'))
    return out


ROOTS = {'MS': 'sea', 'LG': 'lagoon', 'AN': 'surface', 'DB': 'base', 'RS': 'none'}


def root_stats(RP):
    runs = [r for r in RP['runs'] if r['ok']]
    out = dict(n=len(runs), n_rs=sum(r['rs'] for r in runs), cases={})
    for name in RP['cases']:
        pts = [p for r in runs for p in r['cases'][name]['points']]
        bod = [b for r in runs for b in r['cases'][name]['bodies']]
        nl = [p for r in runs if not r['rs'] for p in r['cases'][name]['points']]
        nb = [b for r in runs if not r['rs'] for b in r['cases'][name]['bodies']]
        rs = [p for p in pts if p[0] == 'RS']; ms = [p for p in pts if p[0] == 'MS']
        out['cases'][name] = dict(
            n=len(pts), asc=sum(ROOTS[p[0]] == p[3] for p in pts) / len(pts),
            near=sum(ROOTS[p[0]] == p[2] for p in pts) / len(pts),
            sea=sum(p[3] == 'sea' for p in ms) / max(len(ms), 1), rs=sum(p[3] == 'none' for p in rs) / max(len(rs), 1),
            n_rs=len(rs), nl=len(nl), nl_none=sum(p[3] == 'none' for p in nl), nb=len(nb),
            nb_none=sum(b[1] == 'none' for b in nb), core=sum(ROOTS[b[0]] == b[1] for b in bod) / len(bod), n_bod=len(bod))
    return out


def blocks(R=None, ION=None, RP=None):
    BL = []
    a = BL.append
    s = stats(R) if R else None
    N = s['N'] if s else 0

    def of(n):
        return f'{n} of {N}'

    a(('title', 'INQUIRY-GO: the decisive question'))
    a(('subtitle', 'A proposal: choosing, with a guarantee, the next measurement that tells where the chloride comes '
                   'from. With four companion ideas and a finding in the chemistry of Fushë-Kuqe'))
    a(('byline', 'Dulian Zeqiraj · Department of Energy Resources, Faculty of Geology and Mining, Polytechnic '
                 'University of Tirana · internal working note, 24 November 2026'))

    brief = [
        '**The question.** ORIGIN-GO and HYPOTHESIS-GO return the set of origins of the chloride that the data '
        'allow. When that set still holds rival explanations, which measurement should be made next?',
        '**The proposal.** INQUIRY-GO computes, for every candidate measurement, the outcomes '
        'that each rival verdict can produce. A measurement whose outcome sets do not overlap is *decisive*: '
        'whatever it returns, one verdict is ruled out (Proposition 1). When no measurement is decisive, the one '
        'with the largest decisive share of outcomes is made.',
        '**Anchors.** The candidates include anchors, quantities fixed by nature or by the experimenter and not by '
        'the model: the composition of the sea, the lunar tide, a planned change of the pumping rate, radioactive '
        'decay, the compaction of the ground.',
        '**The design literature.** The twenty papers of the folder on optimal experimental design give sample '
        'pairs in place of adjoints and a term for the model error [KN25], a search without gradients [G26] and '
        'policies refined after each outcome [S25]. They do not give a criterion for a target that is a set and a '
        'verdict.',
        '**Novelty, after a search.** The idea of a guaranteed discriminating experiment exists in set-based fault '
        'diagnosis [SF14] and worst-case designs exist for groundwater models [PT23]. Nothing was found for the '
        'origin of chloride. The contribution is the transfer to that problem, with the physics, the unknown well '
        'positions and the anchors (Section 1).']
    if RP:
        c0 = root_stats(RP)['cases']['clean image']
        brief.append(f'**A negative result.** ROOT-GO, one of the four companion ideas, was tested on '
                     f'{root_stats(RP)["n"]} synthetic truths. Its proposition holds, but as a rule for telling the '
                     f'source of the salt at a point it does no better than taking the nearest source zone '
                     f'({100 * c0["asc"]:.0f}% against {100 * c0["near"]:.0f}%). It is kept only as a necessary '
                     f'condition.')
    if s:
        h, g, d, r_ = s['INQUIRY']['cum'], s['goal variance']['cum'], s['D-optimal']['cum'], s['random']['cum']
        brief.append(f'**First test.** On the synthetic section of HYPOTHESIS-GO ({N} truths with an open verdict), '
                     f'INQUIRY-GO certified the verdict within two questions in {of(h[1])} cases; a goal-oriented '
                     f'variance rule built as in [KN25] did so in {of(g[1])}, D-optimality for the source strengths '
                     f'in {of(d[1])} and random questions in {of(r_[1])}. No certified verdict was wrong.'
                     if all(s[p]['wrong'] == 0 for p in POL) else
                     f'**First test.** On the synthetic section of HYPOTHESIS-GO ({N} truths with an open verdict), '
                     f'INQUIRY-GO certified the verdict within two questions in {of(h[1])} cases; a goal-oriented '
                     f'variance rule built as in [KN25] did so in {of(g[1])}, D-optimality for the source strengths '
                     f'in {of(d[1])} and random questions in {of(r_[1])}. Wrong certified verdicts are reported in '
                     f'Section 3.')
    if ION and P is not None:
        brief.append(P.brief(ION, num))
    a(('box', brief))

    # ---------------------------------------------------------------- 1
    a(('h', '1. Why a further step is needed'))
    a(('p', 'Two earlier notes answer the question of the origin with a set instead of a point [N]. ORIGIN-GO '
            'takes tracers and the intervals of the end-member signatures and returns sharp bounds on the share of '
            'each source. HYPOTHESIS-GO writes each source as a term of the variable-density transport equations, so '
            'that the chloride of a sample is linear in the unknown source strengths for every simulation of an '
            'ensemble, and returns the union of the sets over the simulations that the data do not rule out.' + (P.FIELD if P is not None else '')))
    a(('p', 'Both notes stop where the practical question starts: what should be measured next? ORIGIN-GO chooses '
            'a tracer by the expected gain in decidability, in a mixing model without transport, and PROVENANCE-GO '
            'chooses a test for a decision. Neither chooses among measurements of different kinds in space, depth '
            'and time through the transport model, and neither gives a guarantee on what the measurement will '
            'settle.'))
    a(('p', '**What data alone cannot tell.** The theory of causal graphs characterises which causal relations can be '
            'learned from observational data without experiments: those shared by all graphs of a Markov equivalence '
            'class. Jahn, Eberhardt and Schulman [J25] show that this class is large as soon as the usual assumptions '
            'are relaxed. Its expected size grows almost exponentially in the inverse of the edge density for sparse '
            'acyclic graphs, and super-exponentially when unobserved common causes or feedback loops are allowed. '
            'They conclude that discovery from data must be supplemented with stronger, possibly parametric, '
            'assumptions or with interventions. A pumped coastal aquifer has both features: abstraction that nobody '
            'records acts on the heads and on the salinity together, and operators react to the salinity they '
            'measure. The identified set of the origin plays the role of that class, and the two remedies are the '
            'ones named in [J25]: the differential equations are the parametric assumption (HYPOTHESIS-GO), and the '
            'decisive question is the intervention.'))
    a(('p', 'The twenty papers of the folder on optimal experimental design choose the experiment that maximises an '
            'expected utility of the posterior distribution: A- or D-optimality and the expected information gain '
            '[A21, H24], or the expected Wasserstein distance between prior and posterior [HMR]. Six are close to '
            'our needs. Koval and Nicholson [KN25] build an A-optimal objective from pairs of parameter and data '
            'samples alone and absorb the model error with the Bayesian approximation error. Bartuska and '
            'co-authors [B22] treat parameters that matter only as a nuisance. Chowdhary and co-authors [C26] make '
            'the design robust against uncertain parameters. Gruhlke and co-authors [G26] optimise the design with '
            'ensemble Kalman inversion when gradients are not available. Hedman and co-authors [S25] train a policy '
            'before the experiment and refine it after each outcome. Zhou and Tartakovsky [ZT21] identify a '
            'contaminant source by Markov chain Monte Carlo with a neural surrogate.'))
    a(('p', 'All of them need a prior distribution of the unknown, and their utility is an average. For the origin '
            'of chloride the prior of the source strengths is the weakest part of the analysis: the chloride of '
            'legacy pore water or of deep water at a site is known only as a wide interval. The answer wanted is a '
            'verdict, such as "the sea supplies most of this chloride", with a statement of how sure it is. '
            'INQUIRY-GO keeps the set and asks for a guarantee. Its classical relative is the design for '
            'discriminating between rival models [AF75], which maximises the lack of fit of the rival model at its '
            'best parameters; the decisive question is that idea for sets, with the aquifer unknown.'))

    a(('p', '**What a search of the literature found (24 November 2026).** The decisive question is not new as an '
            'idea. In control engineering, set-based active fault diagnosis designs an input whose outputs are '
            'guaranteed to be consistent with at most one of several models [SF14]; this is Proposition 1 below with '
            'an input in place of a measurement, and experiment design with bounded errors is older still [PW89]. In '
            'groundwater hydrology the design of sampling for discriminating conceptual models is established '
            '[KV89, K15, PT16, NG16], and Pham and Tsai [PT23] already design for the worst case, maximising the '
            'information that an experiment is guaranteed to give. In machine learning, tests are chosen so that the '
            'remaining hypotheses fall into one decision region, with a prior over the hypotheses [C15]. A preprint '
            'of 2026 [F26], which could not be opened and is known here only from a search summary, chooses '
            'experiments by the size of the set of candidate structures they leave, with a control of the '
            'probability of excluding the true one, and reports subsurface-flow tests; it must be read before any '
            'claim is made. No work was found that designs measurements for the origin of chloride or of salinity, '
            'or that ranks tracers for a mixing analysis by a formal criterion.'))
    a(('p', 'What remains particular to INQUIRY-GO, as far as this search goes, is a transfer and a combination, not '
            'a new principle. The target is a verdict on shares, linear in the source strengths through the tagged '
            'terms of the transport equations. The aquifer enters as a union over simulations, with well positions '
            'that may be unknown. The decisive share grades the questions that are not decisive and states the '
            'outcomes that would certify each answer. And the questions include anchors of different kinds.'))

    # ---------------------------------------------------------------- 2
    a(('h', '2. INQUIRY-GO'))
    a(('h2', '2.1 What is known after n measurements'))
    a(('p', 'Let $\\theta$ index the simulations of the ensemble (conductivity, anisotropy, inflow, dispersivities). '
            'For each $\\theta$ the tagged components of HYPOTHESIS-GO give the row $a_{i}(\\theta)$ with which '
            'measurement $i$ depends on the unknown vector $u$. The vector holds the source strengths $S_{k}\\ge 0$ '
            'and, for tracers, the products of strengths and signatures; their intervals confine it to a polyhedron '
            '$U$. After $n$ measurements with values $y_{i}$ and tolerances $\\varepsilon_{i}$,'))
    a(('eq', 'set', ['\\mathcal{P}_{n}(\\theta)=\\big\\{u\\in U:\\ |a_{i}(\\theta)\\cdot u-y_{i}|\\le\\varepsilon_{i},'
                     '\\ i=1,\\dots,n\\big\\},\\qquad \\mathcal{I}_{n}=\\big\\{(\\theta,u):\\ u\\in\\mathcal{P}_{n}'
                     '(\\theta)\\big\\}.']))
    a(('p', '$\\mathcal{I}_{n}$ is the identified set. The *coverage assumption* (A) is that the truth is in it: one '
            'simulation reproduces the true responses, and every error is within its tolerance. HYPOTHESIS-GO '
            'calibrates the tolerance so that (A) holds with a stated probability.'))
    a(('h2', '2.2 Verdicts'))
    a(('p', 'A verdict is a statement about the origin that a decision needs, for instance "source $k$ supplies at '
            'least the share $\\tau$ of the chloride of sample $w$". The chloride of the sample is '
            '$\\sum_{j}G_{wj}(\\theta)S_{j}$, so the verdict is linear in $u$ for every $\\theta$:'))
    a(('eq', 'verdict', ['C_{\\text{yes}}=\\big\\{(\\theta,u):\\ G_{wk}(\\theta)\\,S_{k}-\\tau\\sum_{j}G_{wj}(\\theta)'
                         '\\,S_{j}\\ge 0\\big\\},\\qquad C_{\\text{no}}=\\big\\{(\\theta,u):\\ G_{wk}(\\theta)\\,S_{k}'
                         '-\\tau\\sum_{j}G_{wj}(\\theta)\\,S_{j}\\le 0\\big\\}.']))
    a(('p', 'The verdict *yes* is certified when $\\mathcal{I}_{n}\\cap C_{\\text{no}}$ is empty, and *no* when '
            '$\\mathcal{I}_{n}\\cap C_{\\text{yes}}$ is empty. Each test is one linear programme per simulation.'))
    a(('h2', '2.3 Questions, outcome sets and the decisive question'))
    a(('p', 'A question $\\xi$ is a measurement not yet made, with row $a_{\\xi}(\\theta)$ and tolerance '
            '$\\varepsilon_{\\xi}(y)$. The outcomes that verdict $c$ can produce are'))
    a(('eq', 'outcome', ['O_{c}(\\xi)=\\big\\{y:\\ \\exists\\,(\\theta,u)\\in\\mathcal{I}_{n}\\cap C_{c}\\ \\ '
                         '\\text{with}\\ \\ |a_{\\xi}(\\theta)\\cdot u-y|\\le\\varepsilon_{\\xi}(y)\\big\\}.']))
    a(('p', 'For each simulation the predictions $a_{\\xi}(\\theta)\\cdot u$ over the polytope '
            '$\\mathcal{P}_{n}(\\theta)\\cap C_{c}$ fill an interval, found by two linear programmes. '
            '$O_{c}(\\xi)$ is the union of these intervals, widened by the tolerance.'))
    a(('prop', 'Proposition 1 (decisive question).',
       'Let (A) hold and let the error of the answer $y_{\\xi}$ be within $\\varepsilon_{\\xi}(y_{\\xi})$. '
       '(i) If $y_{\\xi}\\notin O_{\\text{no}}(\\xi)$, the verdict *yes* is certified after the measurement and it is '
       'the true one; likewise with the two verdicts exchanged. (ii) If $O_{\\text{yes}}(\\xi)\\cap '
       'O_{\\text{no}}(\\xi)=\\emptyset$, the question $\\xi$ certifies the true verdict whatever its answer.'))
    a(('proof', 'After the measurement, $\\mathcal{I}_{n+1}\\cap C_{c}$ is the part of $\\mathcal{I}_{n}\\cap C_{c}$ '
                'that reproduces $y_{\\xi}$ within the tolerance, and it is non-empty exactly when $y_{\\xi}\\in '
                'O_{c}(\\xi)$. By (A) the truth stays in $\\mathcal{I}_{n+1}$, so the set of its own verdict is never '
                'emptied and $y_{\\xi}$ lies in the outcome set of the true verdict. If $y_{\\xi}$ is outside the '
                'other outcome set, the other verdict is emptied: this is the certificate. If the two outcome sets '
                'are disjoint, it happens for every answer.'))
    a(('p', 'When the outcome sets overlap, an answer in the overlap leaves both verdicts standing. The *decisive '
            'share* of a question is the part of its possible outcomes that certify a verdict,'))
    a(('eq', 'share', ['\\delta(\\xi)=1-\\frac{|O_{\\text{yes}}(\\xi)\\cap O_{\\text{no}}(\\xi)|}{|O_{\\text{yes}}(\\xi)'
                       '\\cup O_{\\text{no}}(\\xi)|},']))
    a(('p', 'with $|\\cdot|$ the length on the axis of the outcome; $\\delta(\\xi)=1$ is the decisive question of '
            'Proposition 1. INQUIRY-GO asks the question with the largest decisive share (per unit cost when the '
            'costs differ), measures, updates the set and repeats until the verdict is certified or the budget ends. '
            'No prior distribution of the strengths enters. The length is a convention for ranking the questions '
            'that are not decisive; the guarantee does not depend on it.'))
    a(('h2', '2.4 Anchors as questions'))
    a(('p', 'The word anchor is used as in anchor regression [R21]: a variable that is exogenous and recorded. '
            'ANCHOR-GO used anchors to make a chloride alarm robust; here an anchor is a question whose answer '
            'does not lean on the weakest parts of the model. Table {{anchors}} lists six, with the measurement each '
            'one suggests. The first two can be evaluated with the ensembles that exist; the others need one more '
            'response of the tagged components to be stored.'))
    a(('table', ['Anchor', 'What fixes it', 'The question', 'What it separates', 'Ready today'], [
        ['The sea', 'constant proportions of the major ions; δ³⁷Cl is zero by definition of the standard',
         'Br/Cl, δ³⁷Cl, boron or strontium isotopes at a well',
         'marine salt from halite or wastewater; diffusion from advection [D86]', 'yes (signature intervals)'],
        ['Depth and position', 'the geometry of the tagged components', 'chloride at another screen or well',
         'salt from below, from above or from the side', 'yes (stored ensembles)'],
        ['The Moon', 'the lunar tide, period 12.42 h, known in advance', 'phase of the salinity oscillation in a '
         'logger record', 'salt on the sea side or on the land side of the well', 'no (tidal response needed)'],
        ['The pump', 'a planned change of the pumping rate', 'change of chloride after the step',
         'a reservoir (sea, lagoon) from a source limited by its flux (clays, surface load)',
         'no (ensemble at two rates needed)'],
        ['Clocks', 'radioactive decay; the bomb peak in rain', 'tritium, carbon-14',
         'chloride that entered after pumping began from older chloride', 'partly (tritium rows)'],
        ['The ground', 'compaction equals expelled pore water', 'subsidence from InSAR',
         'a cap on the chloride squeezed out of clays', 'no'],
    ], [2.4, 4.0, 3.6, 4.3, 2.7], 8.5))
    a(('cap', 'Table {{anchors}}. Anchors as questions. Each question is a row of the same linear programmes, because '
              'its prediction is linear in the source strengths for a fixed simulation.'))
    a(('h2', '2.5 Three links to the design literature'))
    a(('p', '**The strengths enter linearly.** This gives the origin problem a property that the general theory lacks.'))
    a(('prop', 'Proposition 2 (exact information given the simulation).',
       'For a fixed simulation $\\theta$, Gaussian errors with covariance $\\Gamma$ and a Gaussian prior of $u$ with '
       'covariance $\\Gamma_{0}$, the posterior of $u$ is Gaussian with precision $H_{\\theta}(\\xi)=\\Gamma_{0}^{-1}'
       '+A_{\\xi}(\\theta)^{\\top}\\Gamma^{-1}A_{\\xi}(\\theta)$, which does not depend on the data. Hence '
       '$I(u;y\\,|\\,\\theta)=\\tfrac{1}{2}\\,\\mathbb{E}_{\\theta}\\log\\det\\big(\\Gamma_{0}H_{\\theta}(\\xi)\\big)$ '
       'exactly, and when the simulation is unknown $I(u;y)=I(u;y\\,|\\,\\theta)-I(u;\\theta\\,|\\,y)$.'))
    a(('proof', 'The model is linear in $u$ for fixed $\\theta$, which gives the Gaussian posterior and the first '
                'formula. For the second, the chain rule gives $I(u;y,\\theta)=I(u;\\theta)+I(u;y\\,|\\,\\theta)='
                'I(u;y)+I(u;\\theta\\,|\\,y)$, and $I(u;\\theta)=0$ because the two priors are independent.'))
    a(('p', 'So the sequential D-optimal design applies to the origin problem without the linearisation error that '
            '[KN25] must correct; what is left is the treatment of the hydraulic parameters, the nuisance of [B22]. '
            'The term $I(u;\\theta\\,|\\,y)$ is what the unknown aquifer takes away. D-optimality stays a criterion '
            'for all strengths together, while a verdict depends on one direction; Section 3 shows the difference.'))
    a(('p', '**Model error and anchors.** The tolerance $\\varepsilon$ carries the model error. [KN25] estimate its '
            'mean and covariance from sample pairs of an accurate and a cheap model. No accurate model of a real '
            'aquifer exists; as in the review of the wrong simulator [N], the inflation of the tolerance is to be calibrated on real '
            'observations, each left out in turn and predicted from the others. The rule is that of split conformal '
            'prediction [T23]: with $n$ left-out observations the inflation is the $\\lceil(1-\\alpha)(n+1)\\rceil$-th '
            'smallest of their $n$ scores, and the truth is then inside the set with probability at least '
            '$1-\\alpha$ if the observations are exchangeable. The level cannot exceed $n/(n+1)$: four observations '
            'support 80%, nine are needed for 90% and nineteen for 95%. For one given set of observations the '
            'coverage that is realised follows a Beta law [T23], so with few anchors it can lie far from the nominal '
            'value. The tolerance can also be made to adapt, by dividing each score by the spread of the ensemble at '
            'the question (studentized scores [T23]): wider where the simulations disagree, narrower elsewhere.'))
    a(('p', '**Searching and repeating.** The decisive share is the value of linear programmes and has no gradient '
            'in the position, depth or time of a measurement. The ensemble Kalman search of [G26] needs none. The '
            'loop of measuring, updating and choosing is the semi-amortised policy of [S25]: the outcome sets of '
            'all questions are computed in advance on the ensemble, and after each answer only the programmes of '
            'the surviving simulations are solved again.'))

    # ---------------------------------------------------------------- 3
    if s:
        a(('h', '3. Proof of concept on a synthetic section'))
        gl = ', '.join(f'{SRC_NAME[k]} in {v}' for k, v in sorted(s['goal'].items(), key=lambda kv: -kv[1]))
        a(('p', 'The test uses the synthetic coastal section and the library of HYPOTHESIS-GO: 3,776 simulations with '
                'six tagged sources (modern seawater, lagoon water, fresh recharge, an anthropogenic load, legacy '
                'salinity, deep saline water) and ten wells with two screens each. The truth is one simulation of the '
                'library, with strengths and signatures drawn in their intervals; deep water is present in half of '
                'the truths. Chloride at four wells (eight samples) and four heads are known at the start. The '
                'verdict asks whether one source supplies at least half of the chloride of a saline sample; it is '
                'taken at the most saline sample, and for the first source in the order sea, legacy, deep, '
                'anthropogenic, lagoon, for which the starting data leave it open. A question is chloride, bromide, '
                f'oxygen-18 or tritium at one of the twenty samples (72 candidates of equal cost). Of {N + s["skip"]} '
                f'truths, {s["skip"]} had no open verdict at a saline sample and were left out. In the other {N} '
                f'the open verdict concerned {gl}; between {min(s["n0"])} and {max(s["n0"])} simulations (median '
                f'{int(np.median(s["n0"]))}) reproduced the starting data.'))
        a(('p', 'Six rules choose the next question. All stop with the same certificate (Section 2.2), so they '
                'differ only in what they ask.'))
        a(('b', '*Random*: any question not yet asked.'))
        a(('b', '*D-optimal*: the smallest determinant of the posterior covariance of the six strengths, from 4,000 '
                'sample pairs with a linear-Gaussian fit, the non-intrusive construction of [KN25].'))
        a(('b', '*Goal variance*: the same construction for the variance of the share named in the verdict.'))
        a(('b', '*Widest outcome*: the question whose predicted outcomes span the most tolerances.'))
        a(('b', '*INQUIRY*: the largest decisive share [[share]], ties to the widest outcome.'))
        a(('b', '*Hybrid*: the five best questions by goal variance, then the largest decisive share among them.'))
        rows = []
        for p in POL:
            c = s[p]['cum']
            rows.append([('**' + p + '**') if p in ('INQUIRY', 'hybrid') else p, str(c[0]), str(c[1]), str(c[2]),
                         str(c[-1]), str(N - c[-1] - s[p]['empty']), str(s[p]['wrong'])])
        a(('table', ['Rule', 'Certified after 1 question', 'within 2', 'within 3', f'within {R["maxq"]}',
                     f'Open after {R["maxq"]}', 'Wrong verdicts'], rows, [3.4, 3.0, 2.0, 2.0, 2.0, 2.4, 2.2], 9))
        a(('cap', f'Table {{{{poc}}}}. Number of truths, out of {N}, in which the verdict was certified within the '
                  'stated number of questions, for six rules of choosing the question.'))
        a(('img', 'poc', 13.5))
        a(('cap', f'Figure {{{{poc}}}}. Share of the {N} truths with a certified verdict against the number of '
                  'questions asked.'))
        h, g, hy, d, wd, rn = (s[p]['cum'] for p in ('INQUIRY', 'goal variance', 'hybrid', 'D-optimal',
                                                     'widest outcome', 'random'))
        fl = ', '.join(f'{TR_NAME[k]} in {v}' for k, v in sorted(s['first'].items(), key=lambda kv: -kv[1]))
        txt = f'INQUIRY certified the verdict with one question in {of(h[0])} truths and within two in {of(h[1])}. '
        if s['dec1'] > 0:
            txt += (f'In {of(s["dec1"])} truths its first question was decisive in the sense of Proposition 1, so the '
                    f'verdict was guaranteed before the measurement was made. ')
        else:
            txt += (f'No first question was decisive in the sense of Proposition 1: the decisive share of the question '
                    f'asked first lay between {num(min(s["d1"]))} and {num(max(s["d1"]))} (median '
                    f'{num(float(np.median(s["d1"])))}), and it was the answer that settled the verdict. ')
        txt += f'Its first question was {fl}. '
        if abs(h[1] - g[1]) <= max(1, round(0.08 * N)):
            txt += (f'The goal-variance rule did about as well ({of(g[0])} and {of(g[1])}): a goal-oriented criterion '
                    f'from sample pairs already finds most of the informative questions, at a fraction of the cost. ')
        elif h[1] > g[1]:
            txt += (f'The goal-variance rule needed more questions ({of(g[0])} and {of(g[1])}). ')
        else:
            txt += (f'The goal-variance rule did better within two questions ({of(g[0])} and {of(g[1])}); the '
                    f'decisive share is not the most frugal rule in this test. ')
        txt += (f'The hybrid, which solves linear programmes for five questions only, reached {of(hy[0])} and '
                f'{of(hy[1])}. D-optimality for the strengths ({of(d[1])} within two) and the widest outcome '
                f'({of(wd[1])}) ask about what is most uncertain, which is often not what the verdict turns on; '
                f'random questions reached {of(rn[1])}.')
        a(('p', txt))
        a(('p', f'Two things follow. The rule to use is the hybrid: rank the questions by the cheap goal-oriented '
                f'criterion and compute the decisive share, which is the part that carries the guarantee, for the few '
                f'best. And in {of(s["allopen"])} truths no rule certified the verdict within {R["maxq"]} questions; '
                f'whether more questions of the same kinds would do it, or a question of another kind is needed '
                f'(Table {{{{anchors}}}}), this test does not say.'))
        wr = {p: s[p]['wrong'] for p in POL}
        em = {p: s[p]['empty'] for p in POL}
        a(('p', f'Coverage. The truth reproduced the starting data within the tolerance in {of(s["fits"])} cases. '
                + ('No certified verdict was wrong under any rule'
                   if not any(wr.values()) else
                   'Wrong certified verdicts: ' + ', '.join(f'{p} {v}' for p, v in wr.items() if v))
                + ('.' if not any(em.values()) else
                   '; the set became empty (no simulation left) in ' + ', '.join(f'{v} cases for {p}'
                                                                               for p, v in em.items() if v) + '.')
                + ' What the test does not cover: the truth is a member of the library, so there is no model error; '
                  'the tolerance is not inflated; the costs are equal; one verdict is tested per truth.'))
    k = 4 if s else 3

    # ---------------------------------------------------------------- companions
    a(('h', f'{k}. Four companion ideas'))
    a(('p', 'Each of the four is a question, or a term, that INQUIRY-GO can use. ROOT-GO has been tested, with a '
            'negative result, and SQUEEZE-GO has had a first test on the field section, reported in an internal note; the other two have not. What a search of the literature found is said with each.'))
    a(('h2', f'{k}.1 PHASE-GO: the Moon and the pump as anchors'))
    a(('p', 'A conductivity logger in a well records the salinity every few minutes. The sea tide moves the '
            'groundwater to and fro along the sea–land axis by a displacement $\\zeta(t)$. If the salinity has a '
            'gradient along that axis, the logger sees'))
    a(('eq', 'tide', ['\\Delta c(t)\\approx-\\frac{\\partial c}{\\partial x}\\,\\zeta(t),']))
    a(('p', 'with $x$ pointing inland. The lunar semi-diurnal line, of period 12.42 h, is '
            'exogenous, known in advance, and shared with no pump schedule and no daily temperature cycle. Its '
            'amplitude in the record measures the gradient, and its phase relative to the head gives the sign: salt '
            'on the sea side of the well, as a wedge has it, or on the land side. A planned step of the pumping rate '
            'is the second anchor: a reservoir such as the sea supplies more chloride when the well draws more, '
            'while a source limited by its flux $M$ (diffusion out of clays, a surface load) is diluted, '
            '$c\\approx M/Q$. Both become rows of the linear programmes once the ensemble stores the response of '
            'each tagged component to the tide and to the rate. Tide-induced fluctuations of salinity in wells have '
            'been measured and modelled [L17, Fa18], and the discharge rate of a well and the salinity of its water '
            'are known to be related when salt water cones up from below [RG87]. The search found no work that uses '
            'the phase of the tidal salinity signal to tell on which side the salt lies, or a change of the rate to '
            'tell the kind of source. Open point: the tide of the Adriatic is small, so the power of the test must '
            'be computed before a logger is installed.'))
    a(('h2', f'{k}.2 ROOT-GO: where the saline body is rooted'))
    a(('prop', 'Proposition 3 (rooted salt).',
       'Let the chloride obey $\\phi\\,\\partial_{t}c+q\\cdot\\nabla c-\\nabla\\cdot(D\\nabla c)=\\sum_{j}w_{j}\\,'
       '(c_{j}-c)$ in the aquifer, the sum running over the waters that enter inside the domain with concentrations '
       '$c_{j}$ (a well that extracts adds no term). Let $a$ exceed every $c_{j}$, and let $B$ be a connected '
       'component of the set where $c>a$ at time $T$. Then the connected component of $\\{(x,t):\\ c>a,\\ t\\le T\\}$ '
       'that contains $B$ reaches the initial time, or a point of the boundary through which water with $c>a$ '
       'entered. In a steady state $B$ itself touches such a boundary.'))
    a(('proof', 'On that space–time component $c>a$ inside and $c=a$ on its lateral surface. The operator has no '
                'zero-order term and its right-hand side is negative where $c>a$, so by the weak maximum principle '
                '[PW84] the maximum of $c$ over the closure is attained at the initial time or on the boundary of the '
                'aquifer. A value above $a$ there is initial salt, or inflowing water above $a$.'))
    a(('p', 'A saline body at a well is therefore rooted at the sea, under the lagoon or at the base, or else it is '
            'legacy salt or the product of an internal source such as clays. Which holds can be '
            'read from an image of the salinity (conductivity logs in the existing wells, an electrical or '
            'electromagnetic profile) without a flow model, by following the set above the level found at the well. '
            'Topological persistence [E02] says which components survive the noise of the image. Airborne electromagnetic '
            'surveys already tell saline bodies tied to the present sea from relict ones, by their shape and their '
            'geological setting [At25, Mi26]; the search found no use of the maximum principle or of topological '
            'persistence for this, and no use of persistence for groundwater salinity at all. Three cautions. Clay '
            'and salt water look alike to an electrical instrument. The '
            'set must be followed in depth, because a wedge is rooted along the base of the aquifer. And a body that '
            'was fed from the boundary and later cut off looks like legacy salt; a history of steadily falling heads '
            'makes that unlikely.'))
    if RP:
        rs_ = root_stats(RP)
        a(('p', f'**Test.** The rule was tried on {rs_["n"]} truths of the synthetic section of HYPOTHESIS-GO '
                f'({rs_["n_rs"]} with legacy salinity), on images of the chloride field of 20 by 120 cells: clean, '
                'with multiplicative noise of 10% and 30%, and coarsened fourfold with 10% noise. Every cell is '
                'given to the maximum that steepest ascent reaches; maxima whose persistence is below one standard '
                'deviation of the noise are merged; the root of a point is the place of the maximum of its body '
                '(sea face, top, base, or interior). It is compared with the source that supplies most of the '
                'chloride at the point, for points above 250 mg/L with one source above half, and with a naive '
                'rule: the nearest source zone.'))
        rows = []
        for name in RP['cases']:
            c = rs_['cases'][name]
            rows.append([name, f'{100 * c["asc"]:.0f}%', f'{100 * c["near"]:.0f}%', f'{100 * c["sea"]:.0f}%',
                         f'{100 * c["rs"]:.0f}%', f'{c["nl_none"]} of {c["nl"]}', f'{c["nb_none"]} of {c["nb"]}',
                         f'{100 * c["core"]:.0f}%'])
        a(('table', ['Image', 'Root agrees with the main source of the point', 'Nearest zone agrees',
                     'Sea points rooted at the sea', 'Legacy points rootless',
                     'Rootless points in truths without legacy', 'Rootless bodies in truths without legacy',
                     'Root agrees with the source at the core of the body'], rows,
           [3.0, 2.3, 1.7, 1.8, 1.7, 2.4, 2.2, 1.9], 8))
        a(('cap', f'Table {{{{root}}}}. ROOT-GO on {rs_["n"]} synthetic truths. Columns 6 and 7 test Proposition 3: '
                  'without an internal source no point and no body may be rootless.'))
        c0, c1, c3 = (rs_['cases'][n_] for n_ in ('clean image', 'noise 10%', 'noise 30%'))
        a(('p', f'The proposition holds on clean images: no rootless point among {c0["nl"]} and no rootless body '
                f'among {c0["nb"]} when there is no legacy salinity. As a rule for the origin the result is negative, '
                f'for three reasons. First, the root agrees with the main source of a point in {100 * c0["asc"]:.0f}% '
                f'of the cases, against {100 * c0["near"]:.0f}% for the nearest zone: a weaker source on the flank of '
                'a stronger body has no maximum of its own, because the field is a sum, so its points are given to '
                f'the stronger body. Second, legacy salinity is never rootless here ({100 * c0["rs"]:.0f}% of '
                f'{c0["n_rs"]} points): its release zone lies against the base, so its maximum sits on a boundary. '
                f'Third, noise makes rootless bodies that are not legacy: {c1["nb_none"]} of {c1["nb"]} bodies at 10% '
                f'noise and {c3["nb_none"]} of {c3["nb"]} at 30% in truths without legacy, and the certificate is '
                f'then wrong. What works is the sea: every point fed by the wedge is rooted at the sea face in clean '
                f'and in coarse images, and the root agrees with the source at the core of a body in '
                f'{100 * c0["core"]:.0f}% of the bodies.'))
        a(('p', 'ROOT-GO is therefore set aside as a way of telling the origin at a well. What remains is a necessary '
                'condition that costs nothing: a body that is rooted nowhere in a clean and complete image cannot be '
                'fed from a boundary. A fair second test would need a geometry in which the legacy salt lies away '
                'from the base.'))
    a(('h2', f'{k}.3 TIME-GO: where and when'))
    a(('p', 'ORIGIN-GO mixes sources. Each source also has an age at the sample. Let $g_{k}$ be '
            'the measure of the water of source $k$ over its age $\\tau$, in a sample taken at time $T$. Every '
            'tracer $t$ of that sample is linear in these measures,'))
    a(('eq', 'age', ['y_{t}=\\sum_{k}\\int_{0}^{\\infty}s_{tk}(T-\\tau)\\,e^{-\\lambda_{t}\\tau}\\,g_{k}(d\\tau),\\qquad '
                     'g_{k}\\ge 0,\\qquad \\sum_{k}g_{k}\\big([0,\\infty)\\big)=1,']))
    a(('p', 'where $s_{tk}$ is the known history of the tracer in source $k$ (a constant for the chloride of the sea, '
            'the bomb peak for the tritium of rain) and $\\lambda_{t}$ its decay constant. These are the anchors: '
            'clocks set by physics. The share of the chloride that entered after pumping began is a ratio of two '
            'linear functionals of the measures, so its sharp bounds are a linear-fractional programme over '
            'measures, of the kind solved for moment problems [BP05]. With the ages in classes it is the programme '
            'of ORIGIN-GO with each pair of source and age class as an end-member. No flow model and no shape of '
            'the age distribution is assumed. The bound has a precedent: Bardsley [Ba17], in a discussion paper, '
            'obtains upper bounds of the fraction of water younger than a given age by linear programming over '
            'discrete age distributions, for one water, and notes that such bounds come out near one unless the '
            'shape is constrained. Shape-free fits also exist [V13, Ma14] and have been used next to a zone of '
            'seawater intrusion [Ju21]; tritium and carbon-14 have dated intruded seawater [S05, St25]. What '
            'TIME-GO adds is the source as a second dimension and the chloride share as the quantity bounded. '
            'Whether its bounds are informative with the tracers at hand must be tested first. Needs: tritium '
            'and carbon-14 at the saline wells.'))
    a(('h2', f'{k}.4 SQUEEZE-GO: a seventh term of the equations'))
    a(('p', 'When the head of a confined aquifer falls, its clay layers compact and expel pore water into the '
            'aquifer. If the clays are marine or lagoonal, that water is saline. The '
            'source term and its cap are'))
    a(('eq', 'squeeze', ['\\sigma_{\\text{sq}}(x,t)=c_{\\text{clay}}\\,S\'_{sk}\\,b\'\\,\\big(-\\partial_{t}h\\big)_{+},'
                         '\\qquad \\int_{0}^{T}\\sigma_{\\text{sq}}\\,dt\\le c_{\\text{clay}}^{\\max}\\,\\Delta b(x),']))
    a(('p', 'with $S\'_{sk}$ the skeletal specific storage of the clays, $b\'$ their thickness and $\\Delta b$ their '
            'compaction. For scale: 0.1 m of compaction of clays whose pore water holds 10 g/L of chloride releases '
            '1 kg of chloride per square metre. Two properties make it a useful hypothesis term. Its strength has a '
            'cap that can be measured from space, the subsidence, which the InSAR tools of certain-coast read. And '
            'its signature in time is the rate of the head decline: it acts while the heads fall and stops when '
            'they settle, whereas a wedge keeps advancing. The mechanism is known. Saline pore water squeezed out of '
            'compacting clays is described for the Jiangsu coastal plain [Li17], was judged of secondary importance '
            'in the Israeli coastal plain [Av04], and is documented with InSAR for arsenic [SKF18, E13]; diffusion '
            'out of marine clays is a known source of salinity in confined delta aquifers [WJ12]. The search found '
            'no work that bounds the salt released by the measured subsidence, or that carries the mechanism as a '
            'term with a cap in an analysis of the origin. At Fushë-Kuqe the head fell from 8.0 to 1.5 m above the surface in the sector of '
            'the pumping stations [CB16].'))
    k += 1

    # ---------------------------------------------------------------- finding
    if ION and P is not None:
        k = P.finding(a, ION, k, num, sgn)

    # ---------------------------------------------------------------- plan
    a(('h', f'{k}. Plan, and what would refute the proposal'))
    a(('table', ['Step', 'What is done', 'Needs'], [
        ['1', 'INQUIRY-GO on the stored Fushë-Kuqe ensemble: decisive share of a chloride sample at every position '
              'and screen, and of conservative tracers, for the open verdict at well 340 (legacy salinity or deep '
              'water)', 'no new simulation'],
        ['2', 'Read [F26], [PT23] and [Ba17] in full and compare. A lower bound on the number of '
              'questions from the number of explanations that remain, in the spirit of [J25]',
         'Crossref, the reference lists'],
        ['3', 'Model error: truths outside the library; tolerance calibrated on left-out observations by the '
              'conformal rule, with studentized scores; costs', 'the synthetic library'],
        ['4', 'PHASE-GO: tidal and two-rate responses of the tagged components; power of the lunar test at the '
              'Adriatic tide', 'new runs of the section'],
        ['5', 'SQUEEZE-GO as a seventh term of the Fushë-Kuqe section: a first steady test is done (internal '
              'note); next a transient run, and a cap from the measured subsidence (ROOT-GO was tested and set '
              'aside, Section 4.2)', 'new runs; certain-coast'],
        ['6', 'Field: bromide (and δ³⁷Cl) at wells 340 and 503; a conductivity logger at a coastal well',
         'two to four analyses; one logger'],
    ], [1.2, 11.6, 4.2], 9))
    a(('cap', 'Table {{plan}}. Steps in the order proposed.'))
    a(('p', 'The proposal would be refuted, or cut back, by any of three results. First, if on the Fushë-Kuqe '
            'ensemble no question has a decisive share above that of a question taken at random. Second, if with '
            'truths outside the library the certified verdicts are wrong more often than the stated level. Third, '
            'for PHASE-GO, if the tidal signal at the wells is below the noise of a logger.'))
    k += 1

    a(('h', f'{k}. Limits'))
    a(('b', 'Proposition 1 rests on the coverage assumption. With a wrong model the guarantee is void; the '
            'calibration on left-out observations is proposed here and not yet tested.'))
    a(('b', 'The guarantee holds on average over truths of the kind used for the calibration. No method free of '
            'assumptions on the distribution can give it for one given site [T23].'))
    if s:
        a(('b', 'The test of Section 3 has no model error, equal costs and one verdict per truth.'))
    a(('b', 'The decisive share measures outcomes by their length; another weighting would rank the questions that '
            'are not decisive differently.'))
    a(('b', 'The searches of Section 1 and of the companion ideas were web searches of one day. Every reference '
            'was checked on Crossref and is known from its abstract or record; [F26] was not read.'))
    a(('b', 'Of the four companion ideas, ROOT-GO failed its first test, SQUEEZE-GO has had a first steady test '
            'on the field section (internal note), and PHASE-GO and TIME-GO are untested.'))
    if ION and P is not None:
        a(('b', 'The finding rests on four analyses published in 2016, one per well.'))
    a(('refs',))
    return BL, s
