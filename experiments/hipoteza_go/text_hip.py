"""Text of the note "Hypotheses as terms of the differential equations" (HIPOTEZA-GO), English.
blocks(R, D, F) returns the block list; R = res/hipoteza.json, D = res/dyn.json, F = info of the fields figure.
Every number of Section 6 is computed from these files.  Conventions: $inline math$, **bold**, *italic*,
==yellow placeholder==, [[key]] equation number, {{key}} figure or table number."""
import json
import os

import numpy as np

import hip_infer as I

HERE = os.path.dirname(os.path.abspath(__file__))


def pct(x, d=0):
    return f'{100 * x:.{d}f}%'


def disp(k):
    return k.replace('d18O', 'δ¹⁸O')


def num(x, d=2):
    return f'{x:.{d}f}'.replace('-', '−')


def agg(rows, key, scen):
    tot = lambda f: sum(f(r['scen'][scen][key]) for r in rows)
    n = tot(lambda m: m['n_sal'])
    w = sum((r['scen'][scen][key]['width'] for r in rows), [])
    return dict(n=n, identified=tot(lambda m: m['identified']), wrong_id=tot(lambda m: m['wrong_id']),
                excluded=tot(lambda m: m['excluded']), wrong_excl=tot(lambda m: m['wrong_excl']),
                pairs=tot(lambda m: m['pairs']), covered=tot(lambda m: m['covered']),
                width=float(np.mean(w)) if w else float('nan'),
                ms_decided=tot(lambda m: m['ms_decided']), ms_wrong=tot(lambda m: m['ms_wrong']))


def fill(R, D):
    s = {}
    scen = list(I.SCEN.keys())
    s['scen'] = scen
    s['kres'] = R['H1']['kappa_res']; s['delta'] = R['H1']['delta']; s['miss_raw'] = R['H1']['miss_rate_raw']
    s['ens'] = R['ensemble']
    H2 = R['H2']
    s['n_truth'] = len(H2)
    s['hip'] = {sc: agg(H2, 'hip', sc) for sc in scen}
    s['hip_raw'] = {sc: agg(H2, 'hip_raw', sc) for sc in scen}
    s['hip_exact'] = {sc: agg(H2, 'hip_exact', sc) for sc in scen}
    s['mix'] = {sc: agg(H2, 'mix', sc) for sc in scen}
    s['fals'] = {sc: float(np.mean([r['scen'][sc]['falsified'] for r in H2])) for sc in scen}
    s['n_fals'] = {sc: int(sum(r['scen'][sc]['falsified'] for r in H2)) for sc in scen}
    s['n_min'] = R['H1'].get('n_min', 39)
    s['max_miss'] = R['H1'].get('max_miss', {})
    s['n_loo'] = len(next(iter(R['H1']['kappa_loo'].values())))
    s['n_pairs_loo'] = R['H1']['n_pairs']
    opn = {sc: [r for r in H2 if not r['scen'][sc]['falsified']] for sc in scen}
    s['keff'] = {sc: float(np.median([r['scen'][sc]['kappa_eff'] for r in opn[sc]])) for sc in scen}
    s['nroy'] = {sc: float(np.median([r['scen'][sc]['n_nroy'] for r in opn[sc]])) for sc in scen}
    s['nres'] = {sc: float(np.median([r['scen'][sc]['n_res'] for r in opn[sc]])) for sc in scen}
    s['lowpop'] = {sc: int(sum(r['scen'][sc]['n_nroy'] < s['n_min'] for r in opn[sc])) for sc in scen}
    full = [r['hip_full'] for r in R.get('H2full', []) if 'hip_full' in r]
    s['full'] = dict(n=len(full), pairs=sum(m['pairs'] for m in full), covered=sum(m['covered'] for m in full))
    # term tests
    terms = {}
    for sc in scen:
        d = {}
        for key, k in (('k_noAN', 3), ('k_noRS', 4)):
            pres = [r['scen'][sc][key] > s['kres'][sc] for r in opn[sc] if r['S'][k] > 0]
            absn = [r['scen'][sc][key] > s['kres'][sc] for r in opn[sc] if r['S'][k] == 0]
            d[key] = dict(power=float(np.mean(pres)) if pres else float('nan'), n_pres=len(pres),
                          false=float(np.mean(absn)) if absn else float('nan'), n_abs=len(absn))
        terms[sc] = d
    s['terms'] = terms
    # missing source
    H4 = R['H4']
    s['n_w1'] = len(H4)
    s['detect'] = {sc: float(np.mean([r['scen'][sc]['falsified'] for r in H4])) for sc in scen}
    s['hip6'] = {sc: agg(H4, 'hip6', sc) for sc in scen}
    s['hip6_fals'] = {sc: float(np.mean([r['scen'][sc]['hip6_falsified'] for r in H4])) for sc in scen}
    sparse = {}
    for sc in scen:
        uniq = cont = inside = 0
        for r in H4:
            sub = r['scen'][sc]['subsets']
            feas = {k for k, v in sub.items() if v <= s['kres'][sc]}
            as_set = lambda k: frozenset() if k == 'none' else frozenset(k.split())
            fs = [as_set(k) for k in feas]
            minimal = [a for a in fs if not any(b < a for b in fs)]
            true = frozenset(n for n, k in (('AN', 3), ('RS', 4), ('DB', 5)) if r['S'][k] > 0)
            cont += int(true in fs)
            uniq += int(minimal == [true])
            inside += int(len(minimal) > 0 and all(a <= true for a in minimal))
        n4 = max(len(H4), 1)
        sparse[sc] = dict(unique=uniq / n4, feasible=cont / n4, inside=inside / n4, n_unique=uniq, n_feasible=cont,
                          n_inside=inside)
    s['sparse'] = sparse
    # model error
    H5 = R['H5']
    s['n_me'] = len(H5)
    s['me_fals'] = {sc: float(np.mean([r['scen'][sc]['falsified'] for r in H5])) for sc in scen}
    s['me_n_fals'] = {sc: int(sum(r['scen'][sc]['falsified'] for r in H5)) for sc in scen}
    me_open = {sc: [r for r in H5 if not r['scen'][sc]['falsified']] for sc in scen}
    s['me'] = {sc: agg(me_open[sc], 'hip', sc) for sc in scen}                 # the truths not falsified
    s['me_exact'] = {sc: agg(me_open[sc], 'hip_exact', sc) for sc in scen}
    s['D'] = D
    cpath = os.path.join(HERE, 'res', 'context.json')
    s['ctx'] = json.load(open(cpath)) if os.path.exists(cpath) else None
    return s


REFS = [
    ('B16', 'Brunton, S. L., Proctor, J. L. & Kutz, J. N. (2016). Discovering governing equations from data by sparse '
            'identification of nonlinear dynamical systems. Proceedings of the National Academy of Sciences 113(15), '
            '3932–3937.', 'https://doi.org/10.1073/pnas.1517384113'),
    ('C62', 'Charnes, A. & Cooper, W. W. (1962). Programming with linear fractional functionals. Naval Research '
            'Logistics Quarterly 9(3–4), 181–186.', 'https://doi.org/10.1002/nav.3800090303'),
    ('F20', 'Fantuzzi, G. & Goluskin, D. (2020). Bounding extreme events in nonlinear dynamics using convex '
            'optimization. SIAM Journal on Applied Dynamical Systems 19(3), 1823–1864 (arXiv:1907.10997).',
     'https://doi.org/10.1137/19M1277953'),
    ('G21', 'Ghattas, O. & Willcox, K. (2021). Learning physics-based models from data: perspectives from inverse '
            'problems and model reduction. Acta Numerica 30, 445–554.', 'https://doi.org/10.1017/S0962492921000064'),
    ('G25', 'Geranmehr, M., Bau, D., Mayer, A. S. & Yu, W. (2025). A reduced order model for sea water intrusion '
            'simulation using proper orthogonal decomposition. Groundwater 63(2), 205–219.',
     'https://doi.org/10.1111/gwat.13462'),
    ('H88', 'Handelman, D. (1988). Representing polynomials by positive linear functions on compact convex polyhedra. '
            'Pacific Journal of Mathematics 132(1), 35–62.', 'https://doi.org/10.2140/pjm.1988.132.35'),
    ('K21', 'Kaptanoglu, A. A., Callaham, J. L., Aravkin, A., Hansen, C. J. & Brunton, S. L. (2021). Promoting global '
            'stability in data-driven models of quadratic nonlinear dynamics. Physical Review Fluids 6(9), 094401.',
     'https://doi.org/10.1103/PhysRevFluids.6.094401'),
    ('L13', 'Li, X., Chen, X., Hu, B. X. & Navon, I. M. (2013). Model reduction of a coupled numerical model using '
            'proper orthogonal decomposition. Journal of Hydrology 507, 227–240.',
     'https://doi.org/10.1016/j.jhydrol.2013.09.011'),
    ('L26', 'Liu, Y.-D., Chen, X., Wang, Z.-T. & Dong, J. (2026). Operator inference for physical and generalized '
            'surrogate groundwater modeling. Water Resources Research 62(1), e2025WR039961.',
     'https://doi.org/10.1029/2025WR039961'),
    ('M21', 'Messenger, D. A. & Bortz, D. M. (2021). Weak SINDy for partial differential equations. Journal of '
            'Computational Physics 443, 110525.', 'https://doi.org/10.1016/j.jcp.2021.110525'),
    ('N99', 'Neupauer, R. M. & Wilson, J. L. (1999). Adjoint method for obtaining backward-in-time location and travel '
            'time probabilities of a conservative groundwater contaminant. Water Resources Research 35(11), 3389–3398.',
     'https://doi.org/10.1029/1999WR900190'),
    ('P16', 'Peherstorfer, B. & Willcox, K. (2016). Data-driven operator inference for nonintrusive projection-based '
            'model reduction. Computer Methods in Applied Mechanics and Engineering 306, 196–215.',
     'https://doi.org/10.1016/j.cma.2016.03.025'),
    ('R17', 'Rudy, S. H., Brunton, S. L., Proctor, J. L. & Kutz, J. N. (2017). Data-driven discovery of partial '
            'differential equations. Science Advances 3(4), e1602614.', 'https://doi.org/10.1126/sciadv.1602614'),
    ('S04', 'Simpson, M. J. & Clement, T. P. (2004). Improving the worthiness of the Henry problem as a benchmark for '
            'density-dependent groundwater flow models. Water Resources Research 40(1), W01504.',
     'https://doi.org/10.1029/2003WR002199'),
    ('S15', 'Schlegel, M. & Noack, B. R. (2015). On long-term boundedness of Galerkin models. Journal of Fluid Mechanics '
            '765, 325–352.', 'https://doi.org/10.1017/jfm.2014.736'),
    ('V10', 'Vernon, I., Goldstein, M. & Bower, R. G. (2010). Galaxy formation: a Bayesian uncertainty analysis. '
            'Bayesian Analysis 5(4), 619–669.', 'https://doi.org/10.1214/10-BA524'),
    ('W41', 'Wilks, S. S. (1941). Determination of sample sizes for setting tolerance limits. The Annals of '
            'Mathematical Statistics 12(1), 91–96.', 'https://doi.org/10.1214/aoms/1177731788'),
    ('D1', 'Zeqiraj, D. (2026). Goal-oriented Bayesian experimental design for variable-density seawater intrusion: '
           'adjoint expected information gain for joint monitoring and managed-aquifer-recharge placement. Journal of '
           'Hydrology 680, 136559.', 'https://doi.org/10.1016/j.jhydrol.2026.136559'),
    ('D2', 'Zeqiraj, D. (November 2026). Where does the chloride come from? Review and ZANAFILLA-GO; and Certified '
           'attribution of chloride sources in coastal aquifers with uncertain end-members (draft for Water Resources '
           'Research). experiments/zanafilla_go and experiments/zanafilla_go/wrr.', None),
    ('D3', 'The note pasted by the author on 22 November 2026: "7. Risia e propozuar — intruzioni detar si sistem '
           'kuadratik-bilinear" (R1: quadratic-bilinear structure and operator inference; R2: certified bound of the '
           'salinity at a well for every admissible pumping history).', None),
    ('D4', 'Code and results of this note: experiments/hipoteza_go (hip_core.py, hip_infer.py, hip_exp.py, hip_dyn.py, '
           'hip_figs.py; results in res/) of the repository swi-goal-oed.',
     'https://github.com/dulianzeqiraj/swi-goal-oed'),
]


def blocks(R, D, F):
    s = fill(R, D)
    A = []
    a = A.append
    sc = s['scen']
    sA, sB, sC, sD = sc
    hip, mix, ex = s['hip'], s['mix'], s['hip_exact']
    idp = lambda m: m['identified'] / max(m['n'], 1)
    cov = lambda m: m['covered'] / max(m['pairs'], 1)
    best = max(sc, key=lambda k: idp(hip[k]))
    a(('title', 'Hypotheses as terms of the differential equations'))
    a(('subtitle', 'HIPOTEZA-GO: finding the origin of chloride from the simulation of the saltwater toe, with the '
                   'physics as the link between the wells'))
    a(('byline', 'Dulian Zeqiraj · Department of Energy Resources, Faculty of Geology and Mining, Polytechnic '
                 'University of Tirana · 22 November 2026 · working note with a numerical test'))
    # ---------------------------------------------------------------- summary
    a(('box', [
        '**The question.** With tracers alone the origin of the chloride is often not identified: in the Los Angeles '
        'data 15 of 46 salinised samples stayed open, and with today\'s kind of data at Fushë-Kuqe almost all would. '
        'Can the equations of flow and transport, the simulation of the saltwater toe, supply the missing information?',
        '**The idea.** Every hypothesis about the origin is a term of the transport equation: the sea is a boundary '
        'condition, the lagoon a leakage through the top, the anthropogenic and legacy chloride source terms, the deep '
        'saline water a flux through the base. Pumping enters as a bilinear input, as in the note pasted by the '
        'author (D3); the sources enter as linear inputs. For given hydraulic parameters the tracers of *all* samples '
        'are then linear in a short vector of source strengths and signatures that the samples share. One identified '
        'set for the whole aquifer replaces one set per sample.',
        '**Innovation: HIPOTEZA-GO.** (1) The physics couples the wells: the strengths are common, the response of '
        'each well to each source comes from the equations. (2) The set of strengths and signatures that reproduce the '
        'data is an exact polytope for each hydraulic parameter vector, and the share of each source at each well has '
        'sharp bounds by linear programming; the hydraulic parameters are covered by an ensemble of simulations, of '
        'which only the members not ruled out by the data remain. (3) Hypotheses are tested inside the equations: '
        'dropping a term and finding every simulation ruled out falsifies the reduced library; the libraries that '
        'survive with the fewest terms are the sparsest explanations (the idea of SINDy, B16, moved from regression '
        'to certified feasibility). (4) A certified bound of what a source can deliver to a well under every '
        'admissible pumping history (F20, D3) becomes a test of the hypothesis "seawater only".',
        f'**What the test shows.** In a synthetic coastal section ({s["ens"]["converged"]:,} simulations of the '
        f'variable-density equations, {s["n_truth"]} independent truths), chloride and heads at four wells, the kind '
        f'of data available today, identified the dominant source in {pct(idp(hip[sA]))} of the salinised samples, '
        f'and at ten wells in {pct(idp(hip[sB]))}; without the physics the same data identified '
        f'{mix[sA]["identified"]} and {mix[sB]["identified"]} samples. No statement made with the physics was wrong: '
        f'{sum(hip[k]["wrong_id"] for k in sc)} of {sum(hip[k]["identified"] for k in sc):,} identifications and '
        f'{sum(hip[k]["wrong_excl"] for k in sc)} of {sum(hip[k]["excluded"] for k in sc):,} exclusions over four data '
        f'scenarios. A source missing from the library was detected in '
        + (f'all {s["n_w1"]} cases of every scenario. ' if min(s['detect'].values()) == 1.0 else
           f'{pct(min(s["detect"].values()))} to {pct(max(s["detect"].values()))} of the cases. ')
        + 'Adding bromide, δ¹⁸O and tritium did not sharpen the result further in this test, because a fixed ensemble '
          'forces wider tolerances as the data grow; that is the first thing to improve.',
        '**What it does not show.** The truths come from the same equations as the simulations (Section 6.6 tests one '
        'departure); the section is two-dimensional and steady; the certified bound of Section 5 is stated but not '
        'computed here, because it needs a sum-of-squares solver. Nothing in this note is a result about the real '
        'Fushë-Kuqe aquifer.']))
    # ---------------------------------------------------------------- 1 sources
    a(('h', '1. What the papers and the pasted note contribute'))
    a(('p', 'The folder on the author\'s computer could not be opened from this session. The three papers that were '
            'attached and the note that was pasted were read, and the note\'s mathematics and references were checked.'))
    a(('table', ['Source', 'What it gives', 'How it enters HIPOTEZA-GO', 'Where it stops'], [
        ['Ghattas & Willcox (G21), Acta Numerica 2021',
         'Why inverse problems governed by PDEs are ill-posed (Hadamard; the Picard criterion); adjoints for '
         'gradients and Hessian actions (Section 5, an advection–diffusion–reaction example); A- and D-optimal '
         'design and expected information gain from the low-rank Hessian (Section 4.4); operator inference '
         '(Section 8.2).',
         'The framing: "no amount of mathematical wizardry can recover the lost information" (p. 460), so information '
         'must be added, here by the physics. The adjoint of one sample gives its response to every possible source '
         'location (N99), which lets the library grow to hundreds of candidate zones. Design of the next measurement.',
         'Regularisation or a prior selects one answer; the set of all answers consistent with the data is not the '
         'object.'],
        ['Brunton, Proctor & Kutz (B16), PNAS 2016 (SINDy)',
         'Governing equations are sparse in a library of candidate terms; sparse regression finds the few active '
         'terms.',
         'Hypotheses about the origin form the library of candidate source terms; the aim is the sparsest library '
         'that explains the data.',
         'Needs time histories of the state and its derivatives; a few screens sampled a few times do not provide '
         'them. Selection by thresholded least squares has no error control. (The paper is by Brunton, Proctor and '
         'Kutz; the Gates Foundation appears only in the acknowledgements.)'],
        ['Fantuzzi & Goluskin (F20), SIADS 2020',
         'An auxiliary function $V$ with $\\partial_{t}V+f\\cdot\\nabla V\\le 0$ and $\\Phi\\le V$ bounds the largest '
         'value of an observable $\\Phi$ over all trajectories from a set of initial conditions, without computing '
         'trajectories; sharp for well-posed ODEs on compact sets (their Theorem 2.1); computable by sum-of-squares '
         'optimisation for polynomial systems.',
         'A bound of what one source can deliver to a well under every admissible pumping history: a test of the '
         'hypothesis "seawater only" (Section 5).',
         'Needs a low-order polynomial model and a semidefinite solver; the bound certifies the reduced model.'],
        ['The pasted note (D3): R1 and R2',
         'R1: with the Boussinesq approximation the stream function is linear in the salinity, so the transport '
         'equation is quadratic in the salinity and bilinear in pumping and salinity; an operator-inference model '
         'has exactly this form. R2: because the dynamics are affine in the pumping rate, the auxiliary-function '
         'conditions need to hold only at the two extreme rates.',
         'The same structure with sources: each tagged source obeys a linear equation in the flow field, so pumping '
         'is a bilinear input and the source strengths are linear inputs (Proposition 1). R2 gives the certificate of '
         'Section 5.',
         'It bounds the salinity of a well; it does not say where the chloride comes from. That step is this note.'],
    ], [3.1, 4.9, 5.0, 4.0], 8.6))
    a(('cap', 'Table {{src}}. The sources and their roles.'))
    a(('p', '**Checks of the pasted note.** (i) The derivation of R1 is correct: the curl of $q/K$ removes the head and '
            'gives $\\nabla\\cdot(K^{-1}\\nabla\\psi)=\\varepsilon\\,\\partial_{x}c$, linear in $c$ for any $K(x,z)$. '
            '(ii) One misprint: the decomposition should read $c=\\bar{c}+V_{r}\\hat{c}$ (mean plus modes), and likewise '
            '$\\Phi(\\hat{c})=\\ell^{\\top}(\\bar{c}+V_{r}\\hat{c})$. (iii) With a sea boundary that has inflow and '
            'outflow, the boundary condition of $\\psi$ is affine, not linear, in the boundary salinity; the reduced '
            'model keeps its form through the constant term. (iv) With a pumping sink inside the domain the flow has '
            'an extra part proportional to the pumping rate; the map from salinity and pumping to the flow stays '
            'affine. (v) The energy identity and the vertex argument of R2 are correct. (vi) All references with a DOI '
            'were found on Crossref with the stated data (L26, L13, G25, S04, S15, K21, F20, P16 and the two ECMOR '
            'papers); the one marked "verify" in the note (Olson et al., 2021, Physica D 415, 132748) is correct.'))
    # ---------------------------------------------------------------- 2 equations
    a(('h', '2. The equations, with one term per hypothesis'))
    a(('p', 'In a vertical section with equivalent freshwater head $h$, salinity $c$ (the fraction of seawater, which '
            'drives the density) and relative density difference $\\varepsilon$, the flow and the salinity obey'))
    a(('eq', 'flow', ['\\nabla\\cdot q=w_{L}-Q(t)\\,\\delta_{F},\\qquad q=-K\\,(\\nabla h+\\varepsilon\\,c\\,e_{z}),'
                      '\\qquad \\phi\\,\\partial_{t}c+\\nabla\\cdot(q\\,c)-\\nabla\\cdot(D\\nabla c)=0,']))
    a(('p', 'with $c=1$ on the inflowing part of the sea face, $Q(t)$ the pumping of the well field $F$ and $w_{L}$ '
            'the leakage of lagoon water through the top. For every candidate source $k$ a tagged concentration '
            '$c_{k}$ is carried by the same flow:'))
    a(('eq', 'tag', ['\\phi\\,\\partial_{t}c_{k}+\\nabla\\cdot(q\\,c_{k})-\\nabla\\cdot(D\\nabla c_{k})+\\phi\\lambda_{k}c_{k}'
                     '=S_{k}\\,s_{k}(x),\\qquad k=1,\\dots,K.']))
    a(('p', 'Here $S_{k}$ is the strength of the source (the chloride of the sea, of the lagoon and of the fresh '
            'recharge; the solute flux of the anthropogenic and of the deep source; the release rate of the legacy '
            'salinity), $s_{k}$ its place (a boundary segment or a zone) and $\\lambda_{k}$ a decay constant '
            '(tritium). Table {{lib}} lists the library of this note.'))
    a(('table', ['Hypothesis', 'Term of the equations', 'Strength (unknown, in an interval)', 'Response'], [
        ['MS  modern seawater', 'boundary value at the sea face', 'chloride of the sea, 19,500–21,500 mg/L',
         'water fraction $W_{\\mathrm{MS}}$: the wedge'],
        ['LG  lagoon water', 'leakage through the top, 0.4–2.4 km', 'chloride of the lagoon, 7,800–19,350 mg/L',
         'water fraction $W_{\\mathrm{LG}}$'],
        ['FW  fresh recharge', 'inflow at the inland boundary', 'chloride 10–25 mg/L', '$W_{\\mathrm{FW}}=1-W_{\\mathrm{MS}}-W_{\\mathrm{LG}}$'],
        ['AN  anthropogenic', 'solute flux through the top, 3–7.5 km', '0–0.25 g/m²/d', '$G_{\\mathrm{AN}}$ per unit flux'],
        ['RS  legacy salinity', 'release in the lower half, 5.5–9 km', '0–0.03 g/m³/d', '$G_{\\mathrm{RS}}$ per unit rate'],
        ['DB  deep saline water', 'solute flux through the base, 7–10 km', '0–1.5 g/m²/d', '$G_{\\mathrm{DB}}$ per unit flux'],
    ], [3.4, 5.0, 4.6, 4.0], 9.0))
    a(('cap', 'Table {{lib}}. The library of hypotheses. Zones and ranges are those of the synthetic test.'))
    a(('prop', 'Proposition 1 (structure).',
       '(i) For a given salinity the flow is affine in the salinity and in the pumping rate. (ii) In a given flow '
       'every tagged equation [[tag]] is linear in $c_{k}$ and in $S_{k}$, and the tagged fields do not act on the '
       'flow. Hence the state $(c,c_{1},\\dots,c_{K})$ obeys a system in which the pumping is a bilinear input and '
       'the strengths are linear inputs; with constant dispersion it is the quadratic-bilinear system of D3 extended '
       'by one linear input per hypothesis. (iii) For any hydraulic parameters $\\theta$ and any pumping history, the '
       'value of a tracer $t$ in sample $i$ is linear in the strengths:'))
    a(('eq', 'lin', ['y_{ti}=\\sum_{k}G_{ik}^{(t)}(\\theta,Q)\\,\\rho_{tk}\\,S_{k},']))
    a(('p', 'where $G_{ik}^{(t)}$ is the response of sample $i$ to a unit strength of source $k$ (for chloride and the '
            'ratios to chloride; for the isotopes of water the responses are the water fractions, for tritium the '
            'water fractions with decay) and $\\rho_{tk}$ the signature of the source.'))
    a(('proof', 'The head enters the flow through a linear elliptic equation whose right-hand side is linear in $c$ '
                'and in the sinks and sources of water; this is the stream-function argument of D3 written for the '
                'head. Equation [[tag]] contains $c_{k}$ and $S_{k}$ to the first power only, and $q$ and $D(q)$ do '
                'not depend on $c_{k}$ because only the seawater fraction enters the buoyancy term. Linearity in the '
                'strengths follows by superposition; it holds for the discrete equations as well, which is what the '
                'code uses (one factorisation of the transport operator serves all sources).'))
    a(('p', 'Two assumptions are made for the buoyancy: the lagoon water is carried as a passive tagged water, and the '
            'solute sources are too dilute to change the density. Where they fail, statement (iii) holds after a '
            'linearisation about the dominant density field.'))
    a(('img', 'fields', 16.5))
    a(('cap', f'Figure {{{{fields}}}}. The section of the test for one parameter vector (toe of the 2% line at '
              f'{F["toe02"] / 1000:.1f} km): chloride delivered by each candidate source. The footprints differ in '
              f'place and in depth, and that is what the wells see.'))
    # ---------------------------------------------------------------- 3 identified set
    a(('h', '3. One identified set for all wells'))
    a(('p', 'Collect the strengths and, for the ratio tracers, the products $B_{tk}=\\rho_{tk}S_{k}$ in a vector $u$. '
            'Because $\\rho_{tk}$ and $S_{k}$ are numbers shared by all samples, the lifting is exact.'))
    a(('prop', 'Proposition 2 (polytope and sharp bounds).',
       'For given $\\theta$ the set of strengths and signatures that reproduce the data within their tolerances is '
       'the polytope'))
    a(('eq', 'set', ['\\mathcal{P}_{\\theta}(y)=\\big\\{u:\\ |A_{\\theta}u-y|\\le\\varepsilon,\\ \\ '
                     '\\rho_{tk}^{-}S_{k}\\le B_{tk}\\le\\rho_{tk}^{+}S_{k},\\ \\ u^{-}\\le u\\le u^{+}\\big\\},']))
    a(('p', 'and the share of the chloride of sample $i$ that comes from source $k$,'))
    a(('eq', 'share', ['\\varphi_{ik}=\\frac{G_{ik}(\\theta)\\,S_{k}}{\\sum_{j}G_{ij}(\\theta)\\,S_{j}},']))
    a(('p', 'has sharp bounds over $\\mathcal{P}_{\\theta}(y)$ given by two linear programmes (Charnes–Cooper, C62). '
            'The identified set of the shares is the union over the parameters that the data do not rule out:'))
    a(('eq', 'union', ['[\\varphi_{ik}^{-},\\varphi_{ik}^{+}]=\\Big[\\min_{\\theta\\in\\Theta(y)}\\ \\min_{u\\in\\mathcal{P}_{\\theta}}'
                       '\\varphi_{ik},\\ \\ \\max_{\\theta\\in\\Theta(y)}\\ \\max_{u\\in\\mathcal{P}_{\\theta}}\\varphi_{ik}\\Big],'
                       '\\qquad \\Theta(y)=\\{\\theta\\in\\Theta:\\ \\mathcal{P}_{\\theta}(y)\\ne\\emptyset\\}.']))
    a(('p', 'If the truth lies in the class (its parameters in $\\Theta$, its strengths and signatures in their '
            'intervals, its sources in the library), the bounds contain the true shares with probability at least '
            '$1-\\sum_{t}\\alpha_{t}$, whatever the prior. Without the physics every sample has its own free '
            'fractions: $N(K-1)$ unknowns for $N$ samples. With the physics the unknowns are the strengths, the '
            'signatures and $\\theta$, a number that does not grow with $N$; each new well adds equations, not '
            'unknowns. This is how the physics turns many ill-posed problems into one that is better posed.'))
    a(('p', '**Computation.** The linear directions are handled exactly, by linear programming. The nonlinear '
            'directions $\\theta$ are covered by an ensemble of simulations; the members not ruled out play the role '
            'of the "not ruled out yet" set of history matching (V10). Three rules deal with the finite size of the '
            'ensemble. All three are calibrated by leaving members out (each in turn generates data and the others '
            'are fitted), so they are properties of the ensemble and of the measurement plan, not of the truth.'))
    for b_ in [
        '*Falsification threshold* $\\kappa$. A finite ensemble cannot reproduce data to within the measurement error '
        'alone. A library is declared falsified only when no member reproduces the data within $\\kappa$ times the '
        'tolerances, where $\\kappa$ is the 90% quantile of the factor needed in the leave-one-out trials when the '
        'others are fitted with the sources truly present. A larger library never needs more, so a true hypothesis '
        'is falsified in about one case in ten at most.',
        f'*Minimum population.* The union [[union]] is taken over the members within the factor $\\kappa$, and over '
        f'the {s["n_min"]} best members when they are fewer (up to 2.5 times the tolerances). The reason is '
        f'elementary: the range of $n$ values misses one more value drawn like them with probability $2/(n+1)$ '
        f'(W41), which is 5% for $n={s["n_min"]}$. A union that rests on a handful of simulations says more than the '
        f'ensemble knows.',
        '*Check and margin.* The share of the leave-one-out statements whose true value lies outside its interval is '
        'reported, and the 95% quantile $\\delta$ of the miss is added to both ends of every interval.']:
        a(('b', b_))
    a(('p', 'One safeguard belongs here as well: a linear programme that the solver does not finish is replaced by an '
            'outer bound computed from the intervals of the strengths, never by a guess, and a pair of sample and '
            'source for which no member returns a bound carries no statement.'))
    # ---------------------------------------------------------------- 4 hypotheses as terms
    a(('h', '4. Hypotheses as terms: tests inside the equations'))
    a(('prop', 'Proposition 3 (falsification and sparsest explanations).',
       'Let a hypothesis be a sub-library $\\mathcal{L}\'\\subset\\mathcal{L}$ (the strengths of the other sources are '
       'zero). (i) If the truth lies in the class with library $\\mathcal{L}\'$, then $\\Theta_{\\mathcal{L}\'}(y)$ is '
       'non-empty with probability at least $1-\\sum_{t}\\alpha_{t}$; an empty set therefore falsifies '
       '$\\mathcal{L}\'$ at that level. (ii) Feasibility is monotone: a library that contains a feasible library is '
       'feasible. The feasible libraries are therefore described by their minimal elements, the sparsest '
       'explanations, and a term that belongs to every sparsest explanation is necessary.'))
    a(('p', 'This is the place of SINDy (B16) in the algorithm. SINDy writes $\\dot{X}=\\Theta(X)\\,\\Xi$ and looks for '
            'a sparse $\\Xi$ by thresholded least squares, which needs the state and its derivative at many times. '
            'Here the state is seen at a few screens, so the library is not differentiated from the data but '
            'integrated through the equations: the columns of the library are the responses $G_{ik}$ of [[lin]], '
            'in the spirit of the weak forms (M21, R17). And the selection is not a regression: every sub-library is '
            'either falsified or not, with a stated error level, and all sparsest explanations are returned, not '
            'one.'))
    a(('p', 'Three tests follow. *Is a term necessary?* Drop it; if every member is ruled out, it is. *Is a source '
            'missing?* If the full library is falsified, yes: the analogue of the empty set of ZANAFILLA-GO, now for '
            'the whole aquifer. *Which is the simplest account?* The sparsest feasible libraries.'))
    # ---------------------------------------------------------------- 5 certified bound
    a(('h', '5. What a source can deliver: a certificate over all pumping histories'))
    a(('p', 'The ensemble of Section 3 varies the hydraulic parameters at a steady state. The pumping, however, has '
            'a history, and a hypothesis such as "the chloride of this well is modern seawater" should be tested '
            'against every history that the records allow. For the reduced quadratic-bilinear model '
            '$\\dot{x}=f(x,Q)$ of D3, with the observable $\\Phi_{i}(x)$ equal to the seawater fraction at well $i$, '
            'the method of auxiliary functions (F20) gives'))
    a(('eq', 'aux', ['\\partial_{t}V+f(x,Q)\\cdot\\nabla_{x}V\\le 0\\ \\ \\text{for}\\ Q\\in\\{Q_{\\min},Q_{\\max}\\},\\quad '
                     '\\Phi_{i}\\le V\\quad\\Longrightarrow\\quad \\Phi_{i}(x(t))\\le U_{i}:=\\sup_{x_{0}\\in X_{0}}V(t_{0},x_{0})']))
    a(('p', 'for every measurable $Q(t)\\in[Q_{\\min},Q_{\\max}]$; the two extreme rates suffice because $f$ is affine '
            'in $Q$ (D3). The bound turns into a test:'))
    a(('prop', 'Proposition 4 (a test of "seawater only").',
       'If the measured chloride of well $i$ satisfies $y_{i}-\\varepsilon_{i}>\\mathrm{Cl}_{\\mathrm{fw}}^{+}+'
       '\\mathrm{Cl}_{\\mathrm{sea}}^{+}\\,U_{i}$, then no admissible pumping history lets the sea and the fresh '
       'recharge alone produce it: another source is necessary at that well. The same holds for any source whose '
       'tagged concentration is taken as the observable.'))
    a(('p', '**Status.** The certificate needs a reduced polynomial model and a sum-of-squares solver, which this '
            'environment does not have; a linear-programming variant through Handelman\'s representation (H88) is '
            'possible for a few modes and is the next step. What is computed here is the Monte Carlo side that the '
            'pasted note asks for (its Step 2): trajectories of the full equations under random and bang-bang '
            'pumping histories, compared with the steady states of the two extreme rates (Section 6.5).'))
    # ---------------------------------------------------------------- 6 test
    a(('h', '6. Numerical test'))
    a(('h2', '6.1 Setting'))
    a(('p', f'A confined section 12 km long and 100 m thick, discretised as in the repository solver of the chloride '
            f'manuscript (finite volumes, 120 × 20 cells, upwind advection, velocity-dependent dispersion, hydrostatic '
            f'sea face), with a well field at 5 km and the six sources of Table {{{{lib}}}}. The new solver agrees with '
            f'the repository solver to $2\\times10^{{-7}}$ in the salinity for the case without pumping, and the '
            f'tagged water fractions sum to one to $10^{{-10}}$. The plain Picard iteration oscillates at the toe once '
            f'pumping lowers the seaward flux; Anderson acceleration removes the oscillation (under a second per '
            f'simulation on average). The class: horizontal conductivity 50–200 m/d, anisotropy 0.01–0.1, inland inflow 2.5–6 m²/d, '
            f'lagoon leakage 0 or 0.05–0.4 mm/d, dispersivities 20–80 m and 0.5–3 m; the pumping, 1.4 m²/d, is metered '
            f'and known. Of {s["ens"]["M"]:,} draws, {s["ens"]["converged"]:,} reached the steady state within the '
            f'iteration budget and form the ensemble; the others, long wedges close to the well field, were discarded. '
            f'The toe of the 2% line lies between {s["ens"]["toe02_q"][0] / 1000:.1f} and '
            f'{s["ens"]["toe02_q"][2] / 1000:.1f} km (5–95%).'))
    a(('p', 'Ten wells with an upper and a lower screen give twenty samples. Errors: chloride 3%, bromide 5%, δ¹⁸O '
            '0.1‰, tritium 5% + 0.3 TU, heads 0.5 m; tolerances 2.5 standard deviations. Signature intervals as in the '
            'review (D2). Truths are drawn independently of the ensemble; the anthropogenic and the legacy source are '
            'each absent in 30% of the truths. Four data scenarios: A, chloride at four wells and their heads (the '
            'kind of data Fushë-Kuqe has today); B, chloride and heads at the ten wells; C, plus bromide, δ¹⁸O and '
            'tritium; D, plus sampled end-members (sea, lagoon, fresh water, and the Br/Cl of the anthropogenic '
            'source). The comparison is ZANAFILLA-GO applied sample by sample with the same tracers and intervals and '
            'no physics.'))
    a(('h2', '6.2 The resolution of the ensemble'))
    a(('table', ['Scenario', 'Falsification threshold κ', 'Members within κ (median)',
                 'Members in the union (median); tolerance factor used', 'Leave-one-out: true share outside its interval',
                 'Margin δ'],
       [[disp(k), num(s['kres'][k]), f'{s["nres"][k]:.0f}', f'{s["nroy"][k]:.0f}; {num(s["keff"][k])}',
         f'{pct(s["miss_raw"][k], 1)} of {s["n_pairs_loo"][k]:,}', num(s['delta'][k], 3)] for k in sc],
       [4.2, 2.4, 2.4, 3.4, 3.0, 1.6], 9.0))
    a(('cap', f'Table {{{{res}}}}. Calibration by leaving members out ({s["n_loo"]} trials per scenario for κ). Columns '
              f'3 and 4: medians over the {s["n_truth"]} independent truths of Section 6.3 that were not falsified. '
              f'Column 5: of the statements made (a source identified or excluded).'))
    low = [f'{s["lowpop"][k]} ({k[0]})' for k in sc if s['lowpop'][k]]
    a(('p', 'The more informative the data, the fewer the members that reproduce them: the union would rest on a '
            f'median of {s["nres"][sA]:.0f} members in scenario A but of {s["nres"][sC]:.0f} in C and '
            f'{s["nres"][sD]:.0f} in D. The minimum-population rule widens the tolerance until {s["n_min"]} members '
            'are in'
            + (f'; in {", ".join(low)} truths fewer than {s["n_min"]} members lay within 2.5 times the tolerances and '
               f'the union rests on those. ' if low else '. ')
            + 'This is the price of a fixed ensemble; a denser or adaptive ensemble, or a reduced model, lowers it.'))
    a(('h2', '6.3 Attribution: with and without the physics'))
    rows = []
    for k in sc:
        h, m, e = hip[k], mix[k], ex[k]
        rows.append([disp(k), f'{h["n"]}', f'{pct(idp(h))} ({h["wrong_id"]} wrong)', f'{pct(idp(m))} ({m["wrong_id"]} wrong)',
                     f'{h["excluded"] / max(h["n"], 1):.1f} ({h["wrong_excl"]} wrong)',
                     f'{m["excluded"] / max(m["n"], 1):.1f}', pct(cov(e), 1) if e['pairs'] else '—'])
    a(('table', ['Scenario', 'Salinised samples', 'Origin identified, physics', 'Origin identified, mixing only',
                 'Sources excluded per sample, physics', 'mixing only', 'Coverage of the true shares, physics'], rows,
       [3.7, 1.7, 2.9, 2.6, 2.6, 1.6, 1.9], 8.6))
    a(('cap', f'Table {{{{att}}}}. {s["n_truth"]} truths. "Origin identified": the lower bound of the share of one '
              f'source exceeds 1/2. "Excluded": the upper bound of a source is below 0.1 (of the four sources MS, LG, '
              f'AN, RS). Coverage over the pairs whose union is complete.'))
    if s['ctx']:
        cB = s['ctx']['H2'][sB]
        a(('p', f'Of the {cB["n"]} salinised samples of scenario B, {cB["dom"]} have a source with a true share above '
                f'one half (legacy salinity {cB["by"]["RS"]}, seawater {cB["by"]["MS"]}, anthropogenic '
                f'{cB["by"]["AN"]}, lagoon {cB["by"]["LG"]}); with chloride and heads the physics identified '
                f'{hip[sB]["identified"]} of them, and the per-sample mixing {mix[sB]["identified"]}. The tracers of '
                f'scenarios C and D add little to this. The reason is the fixed ensemble: the more data, the fewer the '
                f'members that reproduce them, and the minimum-population rule widens the tolerances to a median of '
                f'{num(s["keff"][sB], 1)}, {num(s["keff"][sC], 1)} and {num(s["keff"][sD], 1)} times their nominal value '
                f'in B, C and D, which uses up the precision of the tracers. Without the physics the tracers are the '
                f'only information, and they identify {mix[sC]["identified"]} and {mix[sD]["identified"]} samples.'))
    if s['full']['n']:
        a(('p', f'Wrong statements with the physics, over the four scenarios: '
                f'{sum(hip[k]["wrong_id"] for k in sc)} of {sum(hip[k]["identified"] for k in sc):,} identifications '
                f'and {sum(hip[k]["wrong_excl"] for k in sc)} of {sum(hip[k]["excluded"] for k in sc):,} exclusions. '
                f'For the {s["full"]["n"]} truths of scenario B that were not falsified, the complete union of every '
                f'pair of sample and source was computed (all members, every pair by linear programming), decided or '
                f'not: the true share lay inside {s["full"]["covered"]:,} of {s["full"]["pairs"]:,} intervals. In '
                f'scenarios B to D, {s["n_fals"][sB]}, {s["n_fals"][sC]} and '
                f'{s["n_fals"][sD]} of the {s["n_truth"]} true libraries were declared falsified '
                f'({"none" if s["n_fals"][sA] == 0 else s["n_fals"][sA]} in A), in line with the level of one in ten '
                f'at which the threshold was set; for these '
                f'truths the method gives no attribution, and they count as "not identified" in the table.'))
    a(('img', 'decide', 16.5))
    a(('cap', 'Figure {{decide}}. (a) Share of the salinised samples whose dominant source is identified (the lower '
              'bound of its share exceeds 1/2). (b) Sources excluded per salinised sample (upper bound below 0.1).'))
    a(('img', 'example', 16.5))
    X = F.get('example') or {}
    a(('cap', 'Figure {{example}}. One truth'
              + (f' (toe of the 2% line at {X["toe02"] / 1000:.1f} km; anthropogenic flux {X["S"][3]:.2f} g/m²/d, legacy '
                 f'release {X["S"][4]:.3f} g/m³/d)' if X else '')
              + ', chloride and heads at the ten wells (scenario B)'
              + (f', union over {X["n_union"]} simulations' if X else '')
              + ': identified intervals of three shares with the physics (colour) and without it (grey), and the true '
                'shares (ticks).'))
    a(('h2', '6.4 Hypotheses as terms'))
    tb = []
    frac = lambda d: f'{round(d["power"] * d["n_pres"])} of {d["n_pres"]}'
    frab = lambda d: f'{round(d["false"] * d["n_abs"])} of {d["n_abs"]}'
    for k in sc:
        t = s['terms'][k]
        tb.append([disp(k), frac(t['k_noAN']), frab(t['k_noAN']), frac(t['k_noRS']), frab(t['k_noRS']),
                   f'{round(s["detect"][k] * s["n_w1"])} of {s["n_w1"]}',
                   f'{s["sparse"][k]["n_inside"]} of {s["n_w1"]}; {s["sparse"][k]["n_unique"]} of {s["n_w1"]}'])
    a(('table', ['Scenario', 'AN declared necessary when present', 'when absent', 'RS declared necessary when present',
                 'when absent', 'Missing source detected', 'Sparsest explanations: only true sources; exactly the truth'],
       tb, [3.7, 2.4, 1.8, 2.4, 1.8, 2.0, 2.9], 8.6))
    a(('cap', f'Table {{{{tabterms}}}}. Tests of terms. Columns 2–5: the library without the term is falsified '
              f'({s["n_truth"]} truths without deep saline water). Column 6: truths with deep saline water '
              f'({s["n_w1"]}), library without it. Column 7: the same truths, library with it, all eight sub-libraries '
              f'of the three solute sources tested: in how many truths every sparsest explanation contains only '
              f'sources that are present, and in how many the only sparsest explanation is the true library.'))
    tot = lambda key, f, n: (sum(round(s['terms'][k][key][f] * s['terms'][k][key][n]) for k in sc),
                             sum(s['terms'][k][key][n] for k in sc))
    an_p, rs_p = tot('k_noAN', 'power', 'n_pres'), tot('k_noRS', 'power', 'n_pres')
    an_a, rs_a = tot('k_noAN', 'false', 'n_abs'), tot('k_noRS', 'false', 'n_abs')
    a(('p', f'A term is declared necessary only when the data demand it. Over the four scenarios, the legacy source, '
            f'which sits below the wells it feeds, was declared necessary in {rs_p[0]} of the {rs_p[1]} cases in which '
            f'it was present; the anthropogenic source, whose footprint the wells see less sharply, in {an_p[0]} of '
            f'{an_p[1]}. A source that is present but weak is then simply not necessary, and the sparsest explanation '
            f'is sparser than the truth. That is the correct answer to give: the data do not demand the term. What '
            f'must not happen is the opposite, a term declared necessary when its source is absent: this occurred in '
            f'{an_a[0] + rs_a[0]} of {an_a[1] + rs_a[1]} cases.'))
    h6 = s['hip6']
    c4 = s['ctx']['H4'][sB] if s['ctx'] else None
    a(('p', 'With the deep source in the library the attribution itself becomes harder. '
            + (f'Of the {c4["n"]} salinised samples of these truths (scenario B), {c4["dom"]} have a dominant source '
               f'(deep water {c4["by"]["DB"]}, legacy salinity {c4["by"]["RS"]}, seawater {c4["by"]["MS"]}); '
               if c4 else '')
            + f'the dominant source was identified in {h6[sB]["identified"]} samples in scenario B, '
              f'{h6[sC]["identified"]} in C and {h6[sD]["identified"]} in D, with '
              f'{sum(h6[k]["wrong_id"] for k in sc)} wrong. The legacy and the deep source feed the same wells from '
              f'below, so their footprints do not separate them; their signatures could (the Br/Cl of the deep water '
              f'is higher), but with the widened tolerances they did not in this test.'))
    a(('img', 'terms', 16.5))
    a(('cap', 'Figure {{terms}}. (a) Tolerance needed by the library without the anthropogenic term (orange) or '
              'without the legacy term (yellow), relative to the calibrated tolerance; above the dashed line the '
              'reduced library is falsified. Dots: the source is present in the truth; crosses: absent. Values '
              'above 3 are lower bounds. (b) Truths with a deep saline source that the library lacks: tolerance '
              'needed by the library (lower bounds above 2.5).'))
    a(('h2', '6.5 Pumping histories and the steady states'))
    if D is not None:
        a(('p', f'For one parameter vector, {len(D["runs"])} pumping histories of {D["years"]:.0f} years were simulated '
                f'with the full equations: the two constant extremes, two bang-bang histories with periods of 20 and 40 '
                f'years, and random piecewise-constant histories between {D["rq"][0] * D["theta"]["Qin"]:.2f} and '
                f'{D["rq"][1] * D["theta"]["Qin"]:.2f} m²/d. The toe of the 2% line is at '
                f'{D["toe_lo"] / 1000:.1f} km for the lowest and {D["toe_hi"] / 1000:.1f} km for the highest steady '
                f'pumping. Over all histories, times and samples, the seawater fraction exceeded its steady value for '
                f'the highest pumping by at most {num(D["worst_excess"], 4)} and fell below its steady value for the '
                f'lowest pumping by at most {num(D["worst_shortfall"], 4)} (Figure {{{{dyn}}}}). In this test the steady '
                f'states of the extreme rates bracket every trajectory: the Monte Carlo lower bound of the certificate '
                f'of Section 5 coincides, to this accuracy, with the steady state of the highest pumping. This is '
                f'evidence, not a proof; the proof is what the auxiliary function would supply.'))
        a(('img', 'dyn', 16.5))
        a(('cap', 'Figure {{dyn}}. Seawater fraction at the two samples most sensitive to pumping (a, b) and the toe of '
                  'the wedge (c) under random, constant and bang-bang pumping histories, with the steady states of '
                  'the two extreme rates.'))
    a(('h2', '6.6 When the simulations are not the truth'))
    me, mx = s['me'], s['me_exact']
    nf = s['me_n_fals']
    a(('p', f'{s["n_me"]} truths were generated with a two-layer conductivity (contrast 3 to 6) that no member of the '
            f'ensemble has. The class was declared falsified in {nf[sA]}, {nf[sB]}, {nf[sC]} and {nf[sD]} of the '
            f'{s["n_me"]} cases (scenarios A to D): with heads and chloride at ten wells the method mostly answers '
            f'that no simulation of the class explains the data, which is the right answer. In the cases not '
            f'falsified it made {sum(me[k]["identified"] for k in sc)} identifications, '
            f'{sum(me[k]["wrong_id"] for k in sc)} of them wrong, and {sum(me[k]["excluded"] for k in sc)} exclusions, '
            f'{sum(me[k]["wrong_excl"] for k in sc)} of them wrong (four scenarios together); the true share lay '
            f'inside {sum(mx[k]["covered"] for k in sc)} of {sum(mx[k]["pairs"] for k in sc)} intervals with a '
            f'statement, so outside the class the intervals are too narrow more often than the nominal one in twenty, '
            f'even where the statements themselves hold. The guarantee of Section 3 is conditional on the class; this test shows how the method '
            f'behaves outside it, and why the class should be drawn wide (layering, here, belongs in it).'))
    # ---------------------------------------------------------------- 7 meaning
    a(('h', '7. What this means for Fushë-Kuqe'))
    for b in [
        '**The physics is data.** A calibrated variable-density model of the section turns chloride and heads at many '
        'wells into evidence about the origin, because each source has its own footprint in place and depth. The '
        'cheapest campaign item, chloride (or electrical conductivity) and heads at all accessible wells with their '
        'screen depths, becomes the first priority.',
        '**The library must be drawn before the data.** The places of the candidate sources (the lagoon stretch, the '
        'settled zone, the zone of clay intercalations, a deep source) are hypotheses; uncertain places enter as '
        'several terms, and the adjoint of each sample (G21, N99) gives its response to all of them at the cost of one '
        'solve.',
        '**Tracers remain necessary where footprints coincide.** Sources that feed the same wells (here the legacy '
        'and the deep source) can only be told apart by their signatures. In this test the fixed ensemble did not '
        'let the signatures do so (Section 6.4); an ensemble refined around the members that survive, so that the '
        'tolerances need not be widened, is the first improvement to make.',
        '**The pumping record is evidence.** With the history of the well field, the largest seawater fraction that '
        'each well can have received is bounded (Sections 5 and 6.5); a well with more chloride than that needs '
        'another source. For this the abstraction record of the Gorre–Fushë-Kuqe field is needed.',
        '**Order of work.** (1) Calibrate the section model of the chloride manuscript to heads; (2) add the tagged '
        'sources and compute the responses of the existing and planned wells; (3) run HIPOTEZA-GO on today\'s data to '
        'see which hypotheses are already falsified; (4) let the design rule of the campaign plan choose wells by '
        'their power to separate the remaining hypotheses.']:
        a(('b', b))
    # ---------------------------------------------------------------- 8 limits
    a(('h', '8. Limits'))
    for b in [
        'The truths and the ensemble share one solver and one geometry; Section 6.6 tests one departure only.',
        'Two-dimensional section, steady state for the attribution; the transient is used only in Section 6.5.',
        'The lagoon water is passive for buoyancy; dense leakage under a saline lagoon may be unstable and would need a '
        'transient treatment.',
        'The ensemble has a finite resolution. The threshold κ, the minimum-population rule and the margin δ '
        'account for it under the assumption that the truth resembles the members; they cost sharpness, and a denser '
        'or adaptive ensemble, or a reduced model (D3, P16), is the remedy.',
        'The places of the sources are taken as known; so is the pumping.',
        'The certificate of Section 5 is not computed.',
        'Nothing here uses data of the Fushë-Kuqe aquifer.']:
        a(('b', b))
    a(('refs',))
    return A, s
