"""Text of the note "HIPOTEZA-GO at Fushe-Kuqe" (English).  blocks(R, E, F) returns the block list; R =
res_fk/fk_results_second.json, E = the ensemble, F = info of the figures.  Every number is computed from these."""
import json
import os

import numpy as np

import fk_core as FC
import fk_infer as I

HERE = os.path.dirname(os.path.abspath(__file__))
HYD = os.path.join(HERE, '..', '..', 'chloride_fk', 'results', 'hydrochem.json')


def pct(x, d=0):
    return f'{100 * x:.{d}f}%'


def num(x, d=2):
    return f'{x:.{d}f}'.replace('-', '−')


def rng3(q, d=1, unit=''):
    return f'{num(q[1], d)} ({num(q[0], d)}–{num(q[2], d)}){unit}'


REFS = [
    ('CB16', 'Cenameri, S. & Beqiraj, A. (2016). Assessment of seawater intrusion in Fushë Kuqe aquifer, Albania. '
             'Bulletin of the Geological Society of Greece 50(2), 665–670.', 'https://doi.org/10.12681/bgsg.11772'),
    ('M13', 'Mollema, P. N., Antonellini, M., Dinelli, E., Gabbianelli, G., Greggio, N. & Stuyfzand, P. J. (2013). '
            'Hydrochemical and physical processes influencing salinization and freshening in Mediterranean low-lying '
            'coastal environments. Applied Geochemistry 34, 207–221.', 'https://doi.org/10.1016/j.apgeochem.2013.03.017'),
    ('W41', 'Wilks, S. S. (1941). Determination of sample sizes for setting tolerance limits. The Annals of '
            'Mathematical Statistics 12(1), 91–96.', 'https://doi.org/10.1214/aoms/1177731788'),
    ('C62', 'Charnes, A. & Cooper, W. W. (1962). Programming with linear fractional functionals. Naval Research '
            'Logistics Quarterly 9(3–4), 181–186.', 'https://doi.org/10.1002/nav.3800090303'),
    ('D1', 'Zeqiraj, D. (2026). Goal-oriented Bayesian experimental design for variable-density seawater intrusion: '
           'adjoint expected information gain for joint monitoring and managed-aquifer-recharge placement. Journal of '
           'Hydrology 680, 136559.', 'https://doi.org/10.1016/j.jhydrol.2026.136559'),
    ('D2', 'Zeqiraj, D. (in preparation). From sparse hydrochemistry to decision-relevant information: probabilistic '
           'chloride mapping and goal-oriented monitoring design for seawater intrusion in the Fushë-Kuqe coastal '
           'aquifer, Albania. Code: chloride_fk in the repository swi-goal-oed.', None),
    ('D3', 'Zeqiraj, D. (22 November 2026). Hypotheses as terms of the differential equations. HIPOTEZA-GO: finding '
           'the origin of chloride from the simulation of the saltwater toe (working note with a synthetic test).',
     None),
    ('D4', 'Zeqiraj, D. (November 2026). Fushë-Kuqe chloride-source campaign plan (internal).', None),
    ('DATA', 'Fushe_Kuqe_All_Data.xlsx: aquifer boundary, 43 wells with conductivity (Albanian Geological Survey, '
             '2024) and the chemistry sheets compiled from CB16; property of the Albanian Geological Survey and of '
             'A. Beqiraj, used with their permission.', None),
]


def load_all():
    """Results of both screen variants, the coupling diagnosis and the completed share bounds."""
    res = os.path.join(HERE, 'res_fk')
    j = lambda n: json.load(open(os.path.join(res, n))) if os.path.exists(os.path.join(res, n)) else None
    return dict(R2=j('fk_results_shallow.json'), D=j('fk_diag_second.json'), D2=j('fk_diag_shallow.json'),
                SP=j('fk_sparse_second.json'))


def lib_summary(libs):
    feas = [d for d in libs if d['feasible']]
    fset = [frozenset(d['lib']) - {'MS', 'FW'} for d in feas]
    minimal = sorted([s for s in fset if not any(t < s for t in fset)], key=lambda s: (len(s), sorted(s)))
    opt = ['LG', 'AN', 'RS', 'DB']
    groups = []                     # smallest sets of optional terms that every accepted library meets
    import itertools
    for r in range(1, 5):
        for T in itertools.combinations(opt, r):
            if all(set(T) & set(s) for s in fset) and not any(set(g) <= set(T) for g in groups):
                groups.append(T)
    return minimal, groups


def blocks(R, E, F):
    A = []
    a = A.append
    X = load_all()
    R2, D, D2, SP = X['R2'], X['D'], X['D2'], X['SP']
    hyd = json.load(open(HYD))
    kres = R['loo']['kappa_res']
    libs = R['libraries']
    minimal, groups = lib_summary(libs)
    base = next(d for d in libs if set(d['lib']) == {'MS', 'FW'})
    nm = lambda s: ' + '.join(['MS', 'FW'] + sorted(s, key=lambda k: I.SRC.index(k)))
    nmg = lambda g: ' or '.join(g)
    sh = SP['full'] if SP and 'full' in SP else R['shares']
    rH = R['ranges']['heads']
    fa = R['facts']
    c1, u1 = D['converged'], D['unconverged']
    c2 = D2['converged'] if D2 else None
    nh = R['sea_only']['n_heads']
    base2 = next(d for d in R2['libraries'] if set(d['lib']) == {'MS', 'FW'}) if R2 else None
    rej2 = [d for d in R2['libraries'] if not d['feasible']] if R2 else []
    toe340 = [v / 1000 for v in c1['toe02_when_340']]
    hcm = np.array(R['kappa_head']) <= kres
    n_lg = int((E['vL'][hcm] > 0).sum()); n_an = int((E['n_an'][hcm] > 0).sum())
    w = {d['well']: d for d in hyd['wells']}
    a(('title', 'Where does the chloride of Fushë-Kuqe come from?'))
    a(('subtitle', 'HIPOTEZA-GO on today\'s data: the variable-density section calibrated with the documented heads, '
                   'and the hypotheses that the four analyses already reject'))
    a(('byline', 'Dulian Zeqiraj · Department of Energy Resources, Faculty of Geology and Mining, Polytechnic '
                 'University of Tirana · 22 November 2026 · internal working note: the data belong to the Albanian '
                 'Geological Survey and to A. Beqiraj and are not to be distributed without their permission'))
    # ---------------------------------------------------------------- summary
    a(('box', [
        '**The question.** Four analyses (wells 503, 341, 340 and 193; CB16) show chloride from 13 to 1,048 mg/L '
        'along the transect from the Mat outlet to the Adriatic. Is it all seawater, or does part of it come from the '
        'Patok lagoon, from fertilisers and wastewater, from salinity left in the sediments, or from deeper saline '
        'water?',
        f'**What was done.** The variable-density section of the chloride manuscript (D2) was given the pumping of '
        f'the Gorre–Fushë-Kuqe field and the six hypotheses as terms of the transport equation (D3), and calibrated '
        f'with the three documented heads: about 3 m above sea level near the coast, and a head at the well field '
        f'that fell from 8.0 to 1.5 m above the ground. Of {R["M"]:,} simulations, {nh} reproduce the three heads. '
        f'HIPOTEZA-GO then asked which combinations of sources reproduce the four chloride values in those '
        f'simulations. The four wells have no coordinates, so their positions inside their transect bands enter as '
        f'discrete unknowns of a mixed-integer programme, the innovation of this note: no position is assumed.',
        f'**Result.** With wells 503 and 341 in the second aquifer, as their dissolved solids indicate, seawater '
        f'with fresh recharge alone is rejected (tolerance needed at least {num(base["kappa_min"] / kres)} times the '
        f'threshold), and so is any addition of lagoon water or of fertilisers and wastewater. Every accepted '
        f'combination contains {nmg(groups[0]) if groups else "—"}: a legacy salinity in the sediments or a deep '
        f'saline source must contribute. The reason is physical: a wedge long enough to give well 340 its 417 mg/L '
        f'(toe at {toe340[0]:.1f}–{toe340[2]:.1f} km) leaves at least {pct(c1["sw_min_when_340"])} seawater in the '
        f'second aquifer near the coast, where 503 and 341 have about 5%. '
        + (f'If only one source is added to the sea, it supplies most of the chloride of well 340 (legacy salinity '
           f'at least {pct(SP["sparse"]["MS + FW + RS"]["shares"]["340"]["RS"][0])}, or deep water at least '
           f'{pct(SP["sparse"]["MS + FW + DB"]["shares"]["340"]["DB"][0])}). '
           if SP and 'MS + FW + RS' in SP.get('sparse', {}) and 'MS + FW + DB' in SP.get('sparse', {}) else '')
        + 'The ions agree: well 340 is freshening, which is what a legacy salinity being washed out looks like.',
        f'**What would change it.** If 503 and 341 tap the first aquifer instead, seawater alone is accepted '
        f'(in {c2["feasible_all"] if c2 else "—"} of {nh} simulations, all with the wedge under the well field). '
        f'The screen depths of these two wells therefore decide the question, and they cost nothing to find out. '
        f'The lagoon cannot contribute while the aquifer heads stay above its level, and fertilisers and wastewater '
        f'give at most a few per cent at the coastal wells; which of the two remaining sources it is, and how much '
        f'reaches each well, today\'s data cannot tell.',
        '**What it does not show.** The section is two-dimensional and steady; the head facts are single values '
        'from the literature; the places of the candidate sources are hypotheses. The results are statements about '
        'this class of simulations and these data, to be tested by the campaign (D4).']))
    # ---------------------------------------------------------------- 1 data
    a(('h', '1. The data'))
    rows = []
    pos = hyd['positions']
    band = {'sw': '0.5–2.5', 'c': '3–6', 'ne': '≥ 7'}
    scr = {1: 'second aquifer, mid-depth', 0: 'first aquifer, top 40 m'}
    for (wid, yv, b, q) in I.WELLS:
        place = pos[wid].replace('Gorre - Fushe Kuqe', 'Gorre – Fushë-Kuqe')
        rows.append([wid, place, f'{yv:,.0f}', band[b], scr[q], num(w[wid]['NaCl']), num(w[wid]['BEX'])])
    a(('table', ['Well', 'Transect position (CB16)', 'Cl (mg/L)', 'Band (km from the shoreline)', 'Screen',
                 'Na/Cl (molar)', 'BEX (meq/L)'], rows, [1.2, 4.6, 1.6, 2.2, 3.2, 1.6, 1.6], 8.8))
    a(('cap', 'Table {{data}}. The four analyses. Bands and screens as in the chloride manuscript (D2): wells 341 and '
              '503 have more dissolved solids (2,331 and 2,452 mg/L) than the documented maximum of the first aquifer '
              '(1,500 mg/L), so they sample the second; Section 6 tests the other assignment. BEX: base-exchange '
              'index, negative for salinisation, positive for freshening (M13), as computed in D2.'))
    a(('p', 'Chloride error: 5% + 1 mg/L, which covers the variation of wells 341 and 503 between 1984 and 2001 '
            '(1,136 → 1,008 → 1,037 and 961 → 1,070 → 1,048 mg/L); tolerances are 2.5 errors. The heads (sheet 7 of '
            'the workbook, from CB16) are three facts: the littoral head, about 3 m above sea level between 0.5 and '
            '2.5 km from the shoreline (error 1 m); the head at the well field in 2001, 1.5 m above the ground (error '
            '1 m); and the head there before pumping, 8.0 m above the ground (error 1.5 m), the last two after '
            'Tartari (2001) as cited in CB16. No abstraction record was available.'))
    # ---------------------------------------------------------------- 2 section and library
    a(('h', '2. The section and the hypotheses'))
    a(('p', f'The section runs along the row y = 36.5 km of the areal model of the chloride manuscript (D2), '
            f'{E["xc"][-1] / 1000 + 0.05:.1f} km from the shoreline to the inland edge of the model; the Patok lagoon '
            f'lies at its western end. Each simulation takes the geometry and the conductivity of one calibrated member '
            f'of the areal model, drawn with its calibration weight: the aquifer top from the DRASTIC depths, under '
            f'20–35 m of silt and clay, and a thickness that thins inland from about 190 m. On this frame the '
            f'variable-density equations of D3 are solved with the pumping of the well field (a sink in the upper 60% '
            f'of the aquifer, 3.5–6 km from the shoreline) and with one tagged component per hypothesis.'))
    a(('table', ['Hypothesis', 'Term of the equations', 'Strength (unknown, in an interval)', 'Physics gate'], [
        ['MS  modern seawater', 'inflow through the sea face', 'chloride 20,500–22,000 mg/L', '—'],
        ['LG  Patok lagoon', 'leakage through the cover, first 1.5 km', 'chloride 5,000–22,000 mg/L',
         'only where the aquifer head is below the lagoon level'],
        ['FW  fresh recharge', 'inflow at the inland boundary (Mat)', 'chloride 5–25 mg/L', '—'],
        ['AN  fertilisers, wastewater', 'solute input through the cover, 2 km to the inland end', '0–0.25 g/m²/d',
         'only where the aquifer is not artesian'],
        ['RS  legacy salinity', 'release in the aquifer, 1–7 km (marine clays)', '0–0.03 g/m³/d', '—'],
        ['DB  deep saline water', 'flux through the base, 2–7 km', '0–3 g/m²/d', '—'],
    ], [3.6, 5.0, 4.2, 4.2], 8.8))
    a(('cap', 'Table {{lib}}. The library. Two hypotheses need water to move downward through the cover; the gate '
              'switches them off in a simulation whose heads say otherwise, so they are tested inside the equations.'))
    a(('p', '**Class of the section.** Conductivity multiplier 0.5–2 on the areal member, anisotropy 0.003–0.1, inland '
            'inflow 3–80 m²/d per metre, pumping 0–95% of it, well-field centre 3.5–6 km, dispersivities 10–80 m and '
            '0.1–3 m, vertical conductivity of the cover 10⁻⁴–10⁻² m/d (for the lagoon leakage). The inflow is not '
            'taken from the areal model, which was calibrated without pumping: with pumping, the same littoral head '
            'needs more inflow.'))
    if F.get('section'):
        a(('img', 'section', 16.5))
        Xs = F['section']
        a(('cap', f'Figure {{{{section}}}}. The simulation that fits best with the full library (inflow '
                  f'{Xs["theta"]["Qin"]:.1f} m²/d, pumping {Xs["Qw"]:.1f} m²/d per metre, toe of the 2% line at '
                  f'{Xs["toe02"] / 1000:.1f} km). (a) Seawater fraction; dashed boxes: the bands and screens of the '
                  f'four wells; orange: the well field. (b, c) Where a unit release of legacy salinity and a unit flux '
                  f'of deep water put their chloride. (d) Heads with and without pumping, and the three facts.'))
    # ---------------------------------------------------------------- 3 calibration
    a(('h', '3. Calibration with the heads'))
    a(('p', f'Of the {R["M"]:,} simulations that reached a steady state, each fact alone is reproduced within one '
            f'tolerance by {fa["h_lit"]["n_within"]:,}, {fa["h_wf_ag"]["n_within"]:,} and '
            f'{fa["h_wf0_ag"]["n_within"]:,} (littoral head, head at the well field in 2001, head before pumping), and '
            f'all three together by {nh}. In these the inland inflow is {rng3(rH["Qin"], 1, " m²/d")} and the pumping '
            f'{rng3(rH["Qw"], 1, " m²/d")} per metre of width (median, 5–95%); the 2% line of salinity reaches '
            f'{rng3([v / 1000 for v in rH["toe02"]], 1, " km")} from the shoreline at the base of the aquifer.'))
    a(('p', 'The decline of 6.5 m at the well field is what calibrates the pumping; without it the inflow and the '
            'pumping would trade against each other. The areal model of D2 reproduced the littoral head without '
            'pumping and therefore with a small inflow (about 5 m²/d); it cannot show the documented decline. With '
            'pumping in the section the three facts are reproduced together, but with a larger inflow, which the '
            'river-bed infiltration of the Mat would have to supply: a statement to check with a water balance.'))
    a(('p', f'Of the 2,400 simulations drawn, {2400 - R["M"]} did not reach a steady state, most of them with strong '
            f'pumping and a wedge under the well field, where dense water lies above fresh water. They were discarded; '
            f'Section 6 shows that they would not change the result.'))
    if F.get('calib'):
        a(('img', 'calib', 16.5))
        a(('cap', 'Figure {{calib}}. (a) Head at the well field with and without pumping in every simulation; dashed '
                  'box: the two facts within the threshold. (b) Inflow and pumping (dotted: pumping 95% of the inflow).'))
    # ---------------------------------------------------------------- 4 unknown positions
    a(('h', '4. Wells without coordinates: positions as discrete unknowns'))
    a(('p', 'CB16 gives the four wells by their place on the transect, not by coordinates or screen depths. For a given '
            'simulation and a given position, the chloride of a sample is linear in the source strengths $S$ (D3). '
            'With the position unknown inside a band, sample $i$ may sit at any column $p$ of its band (7 to 31 '
            'columns); the strengths are shared by the four samples, the positions are not. Whether some strengths '
            'and some positions reproduce the data within $\\kappa$ times their tolerances is then a mixed-integer '
            'linear programme with one binary variable $z_{ip}$ per candidate position:'))
    a(('eq', 'milp', ['|G_{ip}(\\theta)\\cdot S-y_{i}|\\le\\kappa\\,\\varepsilon_{i}+M_{i}(1-z_{ip}),\\qquad '
                      '\\sum_{p}z_{ip}=1,\\qquad z_{ip}\\in\\{0,1\\},\\qquad S^{-}\\le S\\le S^{+},']))
    a(('p', 'where $M_{i}$ is a bound on the misfit of sample $i$ that relaxes the rows of the positions not chosen. '
            'The share of a source at a well has sharp bounds by fixing the position of that well in turn and solving '
            'the Charnes–Cooper programme (C62) with the positions of the others as binaries. The answer is exact for '
            'the class: no position is averaged away, and no hypothesis is rejected because a well was assumed to be '
            'in the wrong place.'))
    # ---------------------------------------------------------------- 5 tests
    a(('h', '5. Which hypotheses do the data reject?'))
    a(('p', f'The threshold κ = {num(kres)} was calibrated by leaving simulations out ({len(R["loo"]["kmin"])} '
            f'trials: one simulation generates data with random strengths and random positions, the others are '
            f'fitted with the sources truly present; the 90% quantile of the tolerance needed was '
            f'{num(np.quantile(R["loo"]["kmin"], 0.9))}, below one). A combination of sources is rejected when no '
            f'simulation that reproduces the heads also reproduces the four chloride values within κ times their '
            f'tolerances.'))
    if F.get('libs'):
        a(('img', 'libs', 15.5))
        a(('cap', 'Figure {{libs}}. Every combination of the four optional sources with sea and fresh recharge: the '
                  'smallest tolerance needed by any simulation, relative to the threshold (wells 503 and 341 in the '
                  'second aquifer). Blue: accepted; grey: rejected.'))
    rej = [d for d in libs if not d['feasible']]
    a(('p', f'{len(rej)} of the {len(libs)} combinations are rejected: '
            + ', '.join(' + '.join(d['lib']) for d in rej) + '. '
            + (f'The sparsest accepted ones are {" and ".join(nm(s) for s in minimal)}, and every accepted combination '
               f'contains {nmg(groups[0])}. ' if groups else '')
            + (f'The lagoon term is zero in every simulation that reproduces the heads: under the lagoon the aquifer '
               f'head stays above the lagoon level, so water cannot leak down through the cover. ' if n_lg == 0 else
               f'The lagoon term is open in {n_lg} of the {nh} simulations that reproduce the heads. ')
            + f'The anthropogenic term is open only where the aquifer is not artesian, which the heads allow in '
              f'{n_an} of the {nh} simulations.'))
    # ---------------------------------------------------------------- 6 the coupling
    a(('h', '6. Why the sea alone fails: the physics links the wells'))
    a(('p', f'Each well alone can be explained by the sea in many simulations: wells 503 and 341 in '
            f'{c1["feasible_each"]["503"]} and {c1["feasible_each"]["341"]} of the {nh}, well 193 in all, well 340 in '
            f'{c1["feasible_each"]["340"]}. In those {c1["n340"]} the wedge reaches far inland (toe of the 2% line at '
            f'{toe340[0]:.1f}–{toe340[2]:.1f} km) and the second aquifer between 0.5 and 2.5 km holds at least '
            f'{pct(c1["sw_min_when_340"])} seawater (median {pct(c1["sw_median_when_340"])}) at every position, while '
            f'wells 503 and 341 need at most {pct(D["need_sw_max"], 1)}. A wedge that gives the coastal wells their '
            f'chloride does not reach the first aquifer at 340; a wedge that reaches it is too salty at the coast. '
            f'Chloride alone, sample by sample, could never show this; the physics does.'))
    if F.get('couple'):
        a(('img', 'couple', 16.5))
        a(('cap', 'Figure {{couple}}. For every simulation that reproduces the heads: the most seawater the sea brings '
                  'to the first aquifer in the band of well 340, against the least it leaves in the band and screen of '
                  'wells 503 and 341. The sea alone explains the three wells only in the shaded corner. (a) 503 and '
                  '341 in the second aquifer; (b) in the first.'))
    a(('p', f'**Check with the discarded simulations.** Of the {u1["n"]} unconverged simulations that reproduce the '
            f'heads, {u1["feasible_each"]["340"]} could give well 340 its chloride from the sea, and in those the '
            f'coastal second aquifer holds at least {pct(u1["sw_min_when_340"])} seawater; none explains all four '
            f'wells. Discarding them does not change the result.'))
    if R2:
        a(('p', f'**If 503 and 341 tap the first aquifer.** Then the sea alone explains all four wells in '
                f'{c2["feasible_all"]} of the {nh} simulations (Figure {{{{couple}}}}b), all with the wedge under the '
                f'well field, and the test rejects '
                + (f'{len(rej2)} of the {len(R2["libraries"])} combinations' if rej2 else 'none of the combinations')
                + f' (sea and fresh recharge alone: {num(base2["kappa_min"] / R2["loo"]["kappa_res"])} times the '
                  f'threshold). The conclusion of Section 5 therefore rests on the screens of these two wells.'))
    # ---------------------------------------------------------------- 7 shares
    a(('h', '7. Where the chloride of each well comes from'))
    a(('p', f'With the full library, the union over the {R["union"]["n"]} simulations that reproduce heads and '
            f'chloride gives the following bounds of the share of each source in the chloride of each well.'))
    rows = []
    for (wid, yv, b, q) in I.WELLS:
        d = sh[wid]
        f_ = lambda k: '—' if d.get(k) is None else f'{num(d[k][0])}–{num(d[k][1])}'
        rows.append([wid, f'{yv:,.0f}', f_('MS'), f_('LG'), f_('AN'), f_('RS'), f_('DB')])
    a(('table', ['Well', 'Cl (mg/L)', 'MS sea', 'LG lagoon', 'AN fertilisers, wastewater', 'RS legacy',
                 'DB deep'], rows, [1.3, 1.8, 2.6, 2.6, 3.0, 2.6, 2.6], 9.0))
    a(('cap', 'Table {{tabshares}}. Bounds of the share of the chloride of each well (union over the simulations not '
              'ruled out and over all positions in the band; wells 503 and 341 in the second aquifer). The rest is '
              'fresh recharge.'))
    if F.get('shares'):
        a(('img', 'shares', 16.5))
        a(('cap', 'Figure {{shares}}. The bounds of Table {{tabshares}}.'))
    sp_txt = ''
    if SP and SP.get('sparse'):
        parts = []
        for key, d in SP['sparse'].items():
            st = d.get('statements', {})
            src = [k for k in ('RS', 'DB', 'AN', 'LG') if k in key.split(' + ')][0]
            name = {'RS': 'legacy salinity', 'DB': 'deep water', 'AN': 'fertilisers and wastewater',
                    'LG': 'lagoon water'}[src]
            bits = []
            for wid in ('340', '503', '341'):
                dd = d['shares'][wid]
                if src in st.get(wid, {}) and dd[src][0] > 0.5:
                    t = f'at least {pct(dd[src][0])} at well {wid}'
                    if 'MS' in st.get(wid, {}) and dd['MS'][1] < 0.1:
                        t += f' (the sea at most {pct(dd["MS"][1], 1 if dd["MS"][1] < 0.01 else 0)})'
                    bits.append(t)
            if bits:
                parts.append(f'{name} {", ".join(bits)} in the {d["n_union"]} simulations of {key}')
        if parts:
            sp_txt = (' If only one source is added to the sea and the fresh recharge, that source supplies most of the '
                      'chloride of well 340: ' + '; or '.join(parts) + '.')
    an340 = sh['340']['AN'][1]
    a(('p', f'Well 193 is fresh water in every simulation. The lagoon contributes nothing anywhere, because the heads '
            f'keep it out. Fertilisers and wastewater give at most {pct(sh["503"]["AN"][1])} of the chloride of wells '
            f'503 and 341; at well 340 '
            + ('they cannot be excluded: in the few simulations whose heads fall below the water table near the well '
               'field, they could supply all of it. ' if an340 > 0.99 else f'at most {pct(an340)}. ')
            + 'Beyond that the shares are wide: the data say that a second source is needed in the aquifer, not how '
              'much of it each well receives.' + sp_txt))
    # ---------------------------------------------------------------- 8 geochemistry
    a(('h', '8. What the ions say'))
    a(('p', f'Cation exchange marks the direction of change (M13): water that salinises a fresh aquifer loses sodium to '
            f'the sediment (Na/Cl below the seawater value of 0.86, negative BEX), water that freshens a saline '
            f'aquifer gains it (Na/Cl above 0.86, positive BEX). Wells 503 and 341 salinise (Na/Cl '
            f'{num(w["503"]["NaCl"])} and {num(w["341"]["NaCl"])}, BEX {num(w["503"]["BEX"])} and '
            f'{num(w["341"]["BEX"])} meq/L). Well 340 freshens (Na/Cl {num(w["340"]["NaCl"])}, BEX '
            f'+{num(w["340"]["BEX"])} meq/L): the water around it was saltier before and is being flushed by fresh '
            f'water. That is what a legacy salinity being washed out looks like, and not what an advancing seawater '
            f'front looks like. The ions were not used in the tests, so they are an independent check, and they '
            f'favour the legacy salinity over the deep source at 340.'))
    # ---------------------------------------------------------------- 9 next
    a(('h', '9. What to measure next'))
    for b_ in [
        '**Screen depths and coordinates of wells 503, 341, 340 and 193**, and their heads. This decides the test of '
        'Section 6, removes the position unknowns of Section 4 and adds four heads to the calibration; it needs only '
        'the well records of the Albanian Geological Survey.',
        '**A deep and a shallow sample in the central band, under the well field.** Legacy salinity is released '
        'through the thickness of the aquifer, the deep source enters at its base (Figure {{section}} b, c); their '
        'profiles with depth differ.',
        '**Bromide, δ¹⁸O, δ²H and tritium** at the four wells and in the lagoon, the sea and the Mat: Br/Cl separates '
        'marine from other chloride, the water isotopes separate lagoon from sea water, tritium separates water '
        'younger than about 70 years from older.',
        '**The abstraction record of the well field**: with it the pumping is known, and the heads calibrate the '
        'inflow alone.']:
        a(('b', b_))
    # ---------------------------------------------------------------- 10 limits
    a(('h', '10. Limits'))
    for b_ in [
        'Two-dimensional section along one row; the well field is a line sink, so the pumping per metre of width is an '
        'equivalent that reproduces the head decline, not the abstraction of the field.',
        'Steady state with the present pumping. In the synthetic test of D3 the steady state of the highest pumping '
        'bracketed every pumping history, so a wedge that cannot reach a well at this steady state is unlikely to '
        'have reached it before; this is evidence, not a proof.',
        'The places of the candidate sources (Table {{lib}}) and the screens of the four wells are assumptions; the '
        'second is tested in Section 6.',
        'The three heads are single values from the literature, with assumed errors.',
        'The geometry comes from the calibration of D2, which used the chloride of wells 341 and 503; the two analyses '
        'are therefore not fully independent of the class.',
        'The results hold for this class of simulations and these four analyses: they are hypotheses for the '
        'campaign, not findings about the aquifer.']:
        a(('b', b_))
    a(('refs',))
    return A, dict(minimal=minimal, groups=groups, kres=kres)
