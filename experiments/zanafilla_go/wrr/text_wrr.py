"""Text of the WRR draft "Certified attribution of chloride sources in coastal aquifers with uncertain end-members".
blocks(F, Y, Z) returns the block list.  F: res_field/field.json (field application), Y: res/wrr_synth.json
(synthetic comparison), Z: ../res/zanafilla.json (synthetic tests of the review).  Every number is computed from these
files.  Conventions as in the review: $inline math$, **bold**, *italic*, ==yellow placeholder==, [[key]] equation
number, {{key}} figure or table number."""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REFS = json.load(open(os.path.join(HERE, 'res', 'refs_wrr.json'), encoding='utf-8'))

SRC = ['N', 'S', 'I', 'B']


def pct(x, d=0):
    return f'{100 * x:.{d}f}%'


def num(x, d=2):
    return f'{x:.{d}f}'.replace('-', '−')


def words(n):
    w = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']
    return w[n] if 0 <= n < len(w) else str(n)


def wlist(xs):
    xs = list(xs)
    if len(xs) <= 1:
        return ''.join(xs)
    return ', '.join(xs[:-1]) + ' and ' + xs[-1]


# ------------------------------------------------------------------------------------------------ numbers
def fill(F, Y, Z):
    s = {}
    names, cl, F1, t2 = F['names'], np.array(F['cl']), F['F1'], F['table2']
    ts, tb = F['tau_s'], F['tau_b']
    s['n'] = len(names)
    hi = [i for i in range(len(names)) if cl[i] > 100]
    s['n_hi'] = len(hi)
    empty = [names[i] for i, b in enumerate(F1) if b is None]
    s['n_empty'] = len(empty); s['empty'] = empty
    s['diag'] = F['F3_diag']
    # decisions with all tracers, wells above 100 mg/L
    smain = [names[i] for i in hi if F1[i] is not None and F1[i][1][0] > ts]
    snot = [names[i] for i in hi if F1[i] is not None and F1[i][1][1] < ts]
    bpres = [names[i] for i in hi if F1[i] is not None and F1[i][3][0] > tb]
    babs = [names[i] for i in hi if F1[i] is not None and F1[i][3][1] < tb]
    s['smain'], s['snot'], s['bpres'], s['babs'] = smain, snot, bpres, babs
    bpos = [names[i] for i in hi if F1[i] is not None and F1[i][3][0] > 0.02]
    s['bpos'], s['n_bpos'] = bpos, len(bpos)
    s['n_smain'], s['n_snot'], s['n_bpres'], s['n_babs'] = len(smain), len(snot), len(bpres), len(babs)
    # agreement with the Cl/Br column of Table 2
    agree_s = [w for w in smain if 'S' in t2[w]['clbr']]
    agree_b = [w for w in bpres if 'B' in t2[w]['clbr']]
    s['agree_s'], s['agree_b'] = len(agree_s), len(agree_b)
    rep_s = [names[i] for i in hi if t2[names[i]]['clbr'] == 'S']
    rep_b = [names[i] for i in hi if t2[names[i]]['clbr'] == 'B']
    s['n_rep_s'], s['n_rep_b'] = len(rep_s), len(rep_b)
    s['rep_s_cert'] = len([w for w in rep_s if w in smain])
    s['rep_s_empty'] = len([w for w in rep_s if w in empty])
    s['rep_s_present'] = len([w for w in rep_s if w not in empty and F1[names.index(w)][1][0] > 0.25])
    s['rep_b_present'] = len([w for w in rep_b if w in bpres])
    s['rep_b_main'] = len([w for w in rep_b if F1[names.index(w)] is not None and F1[names.index(w)][3][0] > 0.5])
    rb_pos = [w for w in rep_b if F1[names.index(w)] is not None and F1[names.index(w)][3][0] > 0.02]
    s['n_rep_b_pos'] = len(rb_pos)
    s['rep_b_pos_lo'] = (min(F1[names.index(w)][3][0] for w in rb_pos), max(F1[names.index(w)][3][0] for w in rb_pos)) if rb_pos else (0, 0)
    s['rep_b_s_hi'] = np.median([F1[names.index(w)][1][1] for w in rep_b if F1[names.index(w)] is not None])
    s['rep_b_b_lo'] = (min(F1[names.index(w)][3][0] for w in rep_b if F1[names.index(w)] is not None),
                       max(F1[names.index(w)][3][0] for w in rep_b if F1[names.index(w)] is not None))
    contra = []
    for i in hi:
        b = F1[i]
        if b is None:
            continue
        code = t2[names[i]]['clbr']
        if code == 'S' and b[1][1] < ts:
            contra.append(names[i])
        if code == 'B' and b[3][1] < tb:
            contra.append(names[i])
    s['contra'] = contra
    # nested tracer sets
    dec = {}
    for key, S in F['F2'].items():
        d1 = sum(1 for i in hi if S[i] is not None and (S[i][1][0] > ts or S[i][1][1] < ts))
        d2 = sum(1 for i in hi if S[i] is not None and (S[i][3][0] > tb or S[i][3][1] < tb))
        ne = sum(1 for i in hi if S[i] is None)
        w = np.mean([S[i][1][1] - S[i][1][0] for i in hi if S[i] is not None])
        dec[key] = (d1, d2, ne, w)
    s['dec'] = dec
    # sensitivity
    sens = F['F3_sens']
    s['sens'] = {k: [names[i] for i, b in enumerate(v) if b is None] for k, v in sens.items()}
    # fixed signatures
    fx = F['F4_fixed']
    s['fx_empty'] = sum(1 for b in fx if b is None)
    s['fx_empty_hi'] = sum(1 for i in hi if fx[i] is None)
    # Bayes on the field
    B1, B2 = F['F4_bayes']['Dirichlet(1)'], F['F4_bayes']['Dirichlet(0.25)']
    claim = []
    for i in range(len(names)):
        b = F1[i]
        if b is None:
            continue
        for k, lab in ((1, 'S'), (3, 'B')):
            if b[k][0] <= 1e-6 and B1[i]['post'][k][1] > 0.02:
                claim.append((names[i], lab))
    s['claims'] = claim
    s['n_claim_wells'] = len({c[0] for c in claim})
    nat = [names[i] for i in range(len(names)) if all(t2[names[i]][c] == 'N' for c in ('clbr', 'cli', 'clb', 'iso'))]
    s['n_nat'] = len(nat)
    s['nat_claim'] = len({c[0] for c in claim if c[0] in nat})
    shift_s = [abs(B1[i]['post'][1][0] - B2[i]['post'][1][0]) for i in hi if F1[i] is not None]
    shift_b = [abs(B1[i]['post'][3][0] - B2[i]['post'][3][0]) for i in hi if F1[i] is not None]
    s['shift_s_mean'], s['shift_s_max'] = float(np.mean(shift_s)), float(np.max(shift_s))
    s['shift_b_mean'], s['shift_b_max'] = float(np.mean(shift_b)), float(np.max(shift_b))
    outside = 0; tot = 0
    for i in range(len(names)):
        b = F1[i]
        if b is None:
            continue
        for k in range(4):
            tot += 1
            p = B1[i]['post'][k]
            if p[1] < b[k][0] - 1e-3 or p[2] > b[k][1] + 1e-3:
                outside += 1
    s['bayes_outside'] = outside; s['bayes_tot'] = tot
    # design: retrospective
    retro = {}
    for key, rows in F['F5_retro'].items():
        base = np.array([r['base'] for r in rows], float).sum(0)
        pred = np.array([r['pred'] for r in rows], float).sum(0)
        real = np.array([r['real'] for r in rows], float).sum(0)
        n_re = sum(1 for r in rows if r['real_empty'] and not r['base_empty'])
        pe = sum(r['pred_empty'] for r in rows if not r['base_empty'])
        retro[key] = dict(n=len(rows), base=base, pred=pred, real=real, new_empty=n_re, pred_empty=pe)
    s['retro'] = retro
    acts = {}
    for key, a in F['F5_actions'].items():
        kept = a['kept']
        if kept:
            d = np.array([r['dec'] for r in kept], float)
            acts[key] = dict(consistent=a['consistent'], cand=a['candidates'], mean=d.mean(0), lo=d.min(0),
                             hi=d.max(0))
        else:
            acts[key] = dict(consistent=0, cand=a['candidates'], mean=None)
    s['acts'] = acts
    s['base_dec'] = F['F5_base']
    # intervals of the model
    s['iv'] = F['intervals']
    s['notes'] = F['notes']
    # synthetic comparison
    s['Y'] = Y
    # review synthetic tests
    E1 = {(r['level'], r['tracers']): r for r in Z['E1']}
    s['z_today_w'] = E1[('none', 'Cl + major ions')]['width_mean']
    s['z_today_d'] = E1[('none', 'Cl + major ions')]['decidable']
    s['z_all_w'] = E1[('none', '+ B (all)')]['width_mean']
    s['z_all_d'] = E1[('none', '+ B (all)')]['decidable']
    s['z_best_w'] = E1[('relict + fresh + anthropogenic', '+ B (all)')]['width_mean']
    s['z_best_d'] = E1[('relict + fresh + anthropogenic', '+ B (all)')]['decidable']
    s['z_cov_min'] = min(r['coverage'] for r in Z['E1'])
    s['z_wrong'] = max(r['wrong_when_decided'] for r in Z['E1'])
    e4 = Z['E4']['no end-member sampled | + B (all)']
    s['z_e4_empty'] = e4['with an unlisted brine']['empty_where_brine_above_half_percent']
    s['z_e4_false'] = e4['model complete']['empty']
    e5 = Z['E5']
    s['z_e5'] = e5
    s['z_n_fields'] = Z['settings']['n_fields_E1']
    from field_data import charge_balance
    s['cb'] = charge_balance()
    cov = [Y[k][m] for k in Y if '|' in k for m in ('bayes1_cover', 'bayes025_cover')]
    s['bayes_cov_min'], s['bayes_cov_max'] = min(cov), max(cov)
    s['fixed_cov_min'] = min(Y[k]['fixed_cover_all'] for k in Y if '|' in k)
    s['cert_cov_min'] = min(Y[k]['cert_cover'] for k in Y if '|' in k)
    lo_miss, hi_miss = [], []
    for k in Y:
        if '|' not in k:
            continue
        r = Y[k]['raw']; tr = np.array(r['truth']); b1 = np.array(r['bayes1'])
        lo_miss.append(float(np.mean(tr < b1[:, 0]))); hi_miss.append(float(np.mean(tr > b1[:, 1])))
    s['miss_below'] = (min(lo_miss), max(lo_miss)); s['miss_above'] = (min(hi_miss), max(hi_miss))
    return s


# ------------------------------------------------------------------------------------------------ references (AGU)
def _authors(a, maxn=20):
    out = []
    for x in a[:maxn]:
        fam = x['family'].replace('‐', '-')
        ini = ' '.join(p[0] + '.' for p in x['given'].replace('-', ' ').replace('.', ' ').split() if p)
        out.append(f'{fam}, {ini}'.strip(', '))
    if not out:
        return ''
    if len(out) == 1:
        return out[0]
    return ', '.join(out[:-1]) + ', & ' + out[-1]


FIX = {
    'piper1953': ('Piper, A. M., Garrett, A. A., & others', 1953, 'Native and contaminated ground waters in the Long '
                  'Beach–Santa Ana area, California', 'U.S. Geological Survey Water-Supply Paper 1136'),
    'hem1985': ('Hem, J. D.', 1985, 'Study and interpretation of the chemical characteristics of natural water (3rd ed.)',
                'U.S. Geological Survey Water-Supply Paper 2254'),
    'manski2003': ('Manski, C. F.', 2003, 'Partial identification of probability distributions', 'Springer'),
    'moon2012': ('Moon, H. R., & Schorfheide, F.', 2012, 'Bayesian and frequentist inference in partially identified '
                 'models', 'Econometrica, 80(2), 755–782'),
    'gustafson2015': ('Gustafson, P.', 2015, 'Bayesian inference for partially identified models: Exploring the limits '
                      'of limited data', 'Chapman and Hall/CRC'),
    'tarantola2005': ('Tarantola, A.', 2005, 'Inverse problem theory and methods for model parameter estimation',
                      'Society for Industrial and Applied Mathematics'),
    'dansgaard1964': ('Dansgaard, W.', 1964, 'Stable isotopes in precipitation', 'Tellus, 16(4), 436–468'),
    'farkas1902': ('Farkas, J.', 1902, 'Theorie der einfachen Ungleichungen',
                   'Journal für die reine und angewandte Mathematik, 124, 1–27'),
    'land2004': ('Land, M., Reichard, E. G., Crawford, S. M., Everett, R. R., Newhouse, M. W., & Williams, C. F.', 2004,
                 'Ground-water quality of coastal aquifer systems in the West Coast Basin, Los Angeles County, '
                 'California, 1999–2002', 'U.S. Geological Survey Scientific Investigations Report 2004-5067'),
    'izbicki1996': ('Izbicki, J. A.', 1996, 'Seawater intrusion in a coastal California aquifer',
                    'U.S. Geological Survey Fact Sheet 125-96'),
    'hoffman1952': ('Hoffman, A. J.', 1952, 'On approximate solutions of systems of linear inequalities',
                    'Journal of Research of the National Bureau of Standards, 49(4), 263–265'),
    'vengosh2014': ('Vengosh, A.', 2014, 'Salinization and saline environments', 'In H. D. Holland & K. K. Turekian '
                    '(Eds.), Treatise on geochemistry (2nd ed., Vol. 11, pp. 325–378). Elsevier'),
}
OTHER = {
    'hadamard1902': 'Hadamard, J. (1902). Sur les problèmes aux dérivées partielles et leur signification physique. '
                    'Princeton University Bulletin, 13, 49–52.',
    'code': 'Zeqiraj, D. (2026). ZANAFILLA-GO: certified chloride-source attribution (code for this paper) '
            '[Software]. ==Zenodo DOI to be minted at submission==. Development version: '
            'https://github.com/dulianzeqiraj/swi-goal-oed (experiments/zanafilla_go/wrr).',
}


def ref_line(key):
    if key in OTHER:
        return OTHER[key], None
    r = REFS[key]
    if key in FIX:
        au, y, title, tail = FIX[key]
    else:
        au, y, title = _authors(r['authors']), r['year'], r['title'].rstrip('.')
        tail = r['journal'] or r.get('publisher') or ''
        if r.get('volume'):
            tail += f", {r['volume']}"
            if r.get('issue'):
                tail += f"({r['issue']})"
        if r.get('page'):
            tail += f", {str(r['page']).replace('-', '–')}"
    return f'{au} ({y}). {title}. {tail}.', 'https://doi.org/' + r['doi']


def cite(*keys):
    """(Author, Year; ...) in AGU style from the Crossref records."""
    parts = []
    for k in keys:
        if k == 'hadamard1902':
            parts.append('Hadamard, 1902'); continue
        r = REFS[k]
        if k in FIX:
            fam = FIX[k][0].split(',')[0]
            many = FIX[k][0].count('&') and FIX[k][0].count(',') > 2
            two = FIX[k][0].count('&') and not many
            y = FIX[k][1]
            if two:
                fam2 = FIX[k][0].split('& ')[1].split(',')[0]
                parts.append(f'{fam} & {fam2}, {y}')
            elif many:
                parts.append(f'{fam} et al., {y}')
            else:
                parts.append(f'{fam}, {y}')
            continue
        a = r['authors']; y = r['year']
        if len(a) == 1:
            parts.append(f"{a[0]['family']}, {y}")
        elif len(a) == 2:
            parts.append(f"{a[0]['family']} & {a[1]['family']}, {y}")
        else:
            parts.append(f"{a[0]['family']} et al., {y}")
    return '(' + '; '.join(parts) + ')'


def cite_t(k):
    """Author (Year), textual."""
    c = cite(k)[1:-1]
    fam, y = c.rsplit(', ', 1)
    return f'{fam} ({y})'


# ------------------------------------------------------------------------------------------------ the text
def blocks(F, Y, Z):
    s = fill(F, Y, Z)
    A = []
    a = A.append
    iv = s['iv']
    yk = lambda w, t: Y[f'{w} | {t}']
    yp7, ys7 = yk('prior', 'all seven tracers'), yk('shift', 'all seven tracers')
    yp2, ys2 = yk('prior', 'Cl + major ions'), yk('shift', 'Cl + major ions')
    r_br = s['retro']['Br']; r_iso = s['retro']['d18O+d2H']; r_h3 = s['retro']['H3']
    d_all = s['dec']['+ boron (all)']; d_br = s['dec']['+ Br']; d_iod = s['dec']['+ iodide']
    d_trit = s['dec']['+ tritium']

    # ---------------------------------------------------------------- front matter
    a(('title', 'Certified Attribution of Chloride Sources in Coastal Aquifers With Uncertain End-Members'))
    a(('authors', 'Dulian Zeqiraj¹ ==[co-authors to be decided]=='))
    a(('affil', '¹Department of Energy Resources, Faculty of Geology and Mining, Polytechnic University of Tirana, '
                'Tirana, Albania'))
    a(('affil', 'Corresponding author: Dulian Zeqiraj (dulian.zeqiraj@fgjm.edu.al)'))
    a(('kp_h', 'Key Points:'))
    kp = ['With uncertain end-members, the mixtures consistent with tracer data form an exact polytope; '
          'linear programs bound each chloride share',
          'An empty set falsifies the source list: in 80 samples from a Los Angeles coastal basin it flagged local '
          'recharge and anomalous bromide',
          'Fixed-signature ranges often have no solution and Bayesian intervals follow their prior; certified bounds '
          'keep coverage without one']
    for k in kp:
        assert len(k) <= 140, (len(k), k)
        a(('kp', k))
    # ---------------------------------------------------------------- abstract
    a(('h', 'Abstract'))
    cov_txt = 'in every sample' if s['cert_cov_min'] >= 1.0 else f"in {pct(s['cert_cov_min'], 1)} or more of the samples"
    a(('p', f'High chloride in a coastal well can come from modern or old seawater, brines, wastewater or injected '
            f'water, and each source calls for a different response. With more candidate sources than independent '
            f'tracers and end-member compositions known only as ranges, the attribution is an ill-posed inverse '
            f'problem, and point estimates or Bayesian posteriors depend on assumed end-members or on priors. We replace '
            f'the point by the identified set: all source mixtures and end-member compositions within their ranges that '
            f'reproduce the data within their errors. Lifting the bilinear mixing terms to contributions makes this set '
            f'an exact polytope, also for coupled signatures, reactive tracers that can only be gained or lost, and '
            f'censored data. Sharp bounds of the share of chloride from each source follow from linear programs; an '
            f'empty set falsifies the source list; the set is stable and covers the truth without a prior. '
            f'In a synthetic aquifer the bounds covered the truth {cov_txt}, whereas fixed-signature ranges covered as '
            f'little as {pct(s["fixed_cov_min"])} and Bayesian 90% intervals {pct(s["bayes_cov_min"])}–'
            f'{pct(s["bayes_cov_max"])}. Applied to {s["n"]} samples from the West Coast Basin, Los Angeles, the bounds '
            f'certify seawater as the main chloride source in {s["n_smain"]} of {s["n_hi"]} samples above 100 mg/L and '
            f'a brine component in {s["n_bpos"]}, but never brine as the main source; {words(s["n_empty"])} empty sets '
            f'reveal local recharge and anomalous bromide. A goal-oriented '
            f'criterion ranks the next measurement by the decisions it would settle: characterizing the brine '
            f'end-member would nearly double the settled brine questions.'))
    # ---------------------------------------------------------------- plain language summary
    a(('h', 'Plain Language Summary'))
    a(('p', 'Salt in coastal groundwater can come from the sea, from old seawater trapped in sediments, from brines, '
            'or from human activity, and the remedy depends on which. Chemists tell the sources apart with tracers such '
            'as bromide or the isotopes of water, but the sources are many, the tracers few, and the chemistry of each '
            'source is known only roughly. Many different mixtures then fit the same analysis, and the usual methods '
            'pick one, either by assuming exact source compositions or by adding prior beliefs. We compute instead the '
            'full range of answers that the data and the stated ranges allow, sample by sample, with a guarantee that '
            'does not rest on prior beliefs. When no mixture fits, the method says so, which reveals a missing source '
            'or a doubtful measurement. Applied to a Los Angeles coastal basin, the method confirms seawater where the '
            'original study found it, shows where the evidence for an oil-field brine is firm and where it rests on '
            'judgement, and flags samples whose chemistry the listed sources cannot explain. It also tells which '
            'additional measurement would settle the most open questions.'))
    # ---------------------------------------------------------------- 1 introduction
    a(('h', '1 Introduction'))
    a(('p', f'Chloride is the first indicator of salinization in coastal aquifers, but chloride alone does not say '
            f'where the salt comes from. Modern seawater enters where pumping reverses the hydraulic gradient; old '
            f'seawater remains in fine-grained marine deposits; brines rise along faults or leak from oil fields; and '
            f'wastewater, fertilizers, road salt and injected water add chloride from the land side '
            f'{cite("werner2013", "vengosh2014")}. The response differs by source: a barrier or reduced pumping for '
            f'intrusion, well-construction measures for leakage from depth, and land-use control for anthropogenic '
            f'chloride. The attribution is therefore a decision problem, and an error in it has a cost.'))
    a(('p', f'Tracers narrow the choice. Chloride-to-bromide ratios separate seawater from halite dissolution and from '
            f'some wastewaters {cite("davis1998", "alcala2008", "panno2006", "katz2011")}; the stable isotopes of water '
            f'separate seawater, local recharge and imported water {cite("craig1961")}; tritium separates water '
            f'recharged after the 1950s from older water; and iodide, boron and their isotopes add evidence for marine '
            f'sediments and brines {cite("vengosh2005", "land2004")}. In practice the tracers are combined by expert '
            f'judgement on mixing diagrams, one pair at a time.'))
    a(('p', f'Mixing models make the combination quantitative. End-member mixing analysis computes source fractions '
            f'from known end-members {cite("christophersen1992", "hooper2003")}; its uncertainty grows quickly with the '
            f'uncertainty of the end-members {cite("genereux1998")}, and the number of tracers needed has been studied '
            f'directly {cite("barthold2011")}. When the sources outnumber the tracers, IsoSource '
            f'{cite("phillips2003")} enumerates every combination of proportions, in small increments, that satisfies '
            f'the mass balance within a tolerance and reports their range, for fixed end-member values. Bayesian mixing '
            f'models treat end-members and residual errors as uncertain and return a posterior '
            f'{cite("moore2008", "parnell2010", "stock2018")}; their users have noted that in underdetermined systems '
            f'the posterior reflects the prior {cite("phillips2014")}, which is the general behavior of posteriors in '
            f'partially identified models {cite("poirier1998", "moon2012", "gustafson2015")}.'))
    a(('p', f'The difficulty is structural. In Hadamard\'s sense {cite("hadamard1902")} the attribution problem is '
            f'ill-posed: a solution need not exist when a real source is missing from the list, it is not unique when '
            f'the sources outnumber the independent tracers, and a least-squares solution can move far when the assumed '
            f'end-members move a little. Geophysics answered such problems with strict bounds, the range of a quantity '
            f'over all models that fit the data {cite("oldenburg1983", "stark1992")}, and with the argument that '
            f'constraints can replace priors {cite("stark2015")}; econometrics developed the same idea as partial '
            f'identification {cite("manski2003", "tamer2010", "imbens2004")}. For chloride sources the idea has not been '
            f'worked out. Two obstacles stand in the way: the mixing equations are bilinear once the end-members are '
            f'uncertain, and the quantity of interest, the share of chloride from a source, is a ratio of contributions '
            f'rather than a water fraction.'))
    a(('p', 'This paper removes both obstacles and tests the result in a synthetic aquifer and on public field data. '
            'Our contributions are:'))
    for b in [
        '**an exact polytope** for the set of mixtures and end-member compositions that reproduce the data, obtained by '
        'lifting the bilinear terms to contributions, which holds for chloride-weighted and water-weighted tracers, '
        'coupled signatures, reactive tracers that can only be gained or only be lost, and censored values '
        '(Proposition 1);',
        '**sharp bounds of the chloride share** of every source by linear programming after the Charnes–Cooper '
        'transform (Proposition 2);',
        '**well-posedness for the set**: an empty set falsifies the source list at a controlled false-alarm rate, the '
        'set is unique, and it is Lipschitz-stable in the data (Proposition 3);',
        '**coverage without a prior** (Proposition 4), compared with fixed-signature ranges and with Bayesian '
        'credible intervals in a synthetic aquifer where the truth is known;',
        '**a goal-oriented rule for the next measurement**, which compares a new tracer at the wells with the '
        'sampling of an end-member by the decisions it would settle (Proposition 5), and a retrospective test of the '
        'rule on field data;',
        f'**an application** to {s["n"]} samples from the West Coast Basin, Los Angeles {cite("land2004")}, compared '
        'sample by sample with the original expert interpretation.']:
        a(('b', b))
    # ---------------------------------------------------------------- 2 theory
    a(('h', '2 Theory'))
    a(('h2', '2.1 The mixing model with uncertain end-members'))
    a(('p', 'A water sample is a mixture of $K$ candidate sources with water fractions $f\\in\\Delta_{K}$, the '
            'probability simplex, possibly restricted by site knowledge, $f\\le u$. Source $k$ has chloride '
            'concentration $\\mathrm{Cl}_{k}\\in[\\mathrm{Cl}_{k}^{-},\\mathrm{Cl}_{k}^{+}]$. Every other tracer $t$ '
            'belongs to one of two mixing classes. A *water-weighted* tracer (the isotopes of water, tritium) mixes as '
            '$y_{t}=\\sum_{k}f_{k}s_{tk}$ with signature $s_{tk}\\in[s_{tk}^{-},s_{tk}^{+}]$. A *chloride-weighted* '
            'tracer, given as a ratio to chloride (Br/Cl, I/Cl, B/Cl), mixes as '
            '$y_{t}=\\sum_{k}f_{k}\\mathrm{Cl}_{k}\\rho_{tk}$ with $\\rho_{tk}\\in[\\rho_{tk}^{-},\\rho_{tk}^{+}]$. The '
            'data are the measured $y_{t}$ with errors; we write $\\varepsilon_{t}$ for a tolerance chosen so that '
            '$\\Pr(|e_{t}|\\le\\varepsilon_{t})\\ge 1-\\alpha_{t}$.'))
    a(('p', 'Three features of real data enter the same frame. *Coupled signatures*: the two isotopes of water of '
            'one source are not independent; we bound the deuterium excess, '
            '$d_{k}=\\delta^{2}\\mathrm{H}_{k}-8\\,\\delta^{18}\\mathrm{O}_{k}\\in[d_{k}^{-},d_{k}^{+}]$ '
            f'{cite("dansgaard1964")}, in addition to each isotope. *Reactive tracers*: when a tracer can only be gained '
            'in the aquifer after mixing (iodide from marine sediments), the sources supply at most the observation; '
            'when it can only be lost (boron by sorption), they supply at least the observation. *Censored values*: '
            'a value below a detection limit $L$ is the interval $[0,L]$.'))
    a(('h2', '2.2 The identified set'))
    a(('p', 'Write $c_{k}=f_{k}\\mathrm{Cl}_{k}$ for the chloride that source $k$ brings, $v_{tk}=c_{k}\\rho_{tk}$ for '
            'its contribution to a chloride-weighted tracer and $w_{tk}=f_{k}s_{tk}$ for its contribution to a '
            'water-weighted tracer.'))
    a(('prop', 'Proposition 1 (the identified set is a polytope).',
       'The set of $(f,c,v,w)$ for which compositions within their intervals exist that reproduce the data is'))
    a(('eq', 'poly', ['\\mathcal{P}(y)=\\Big\\{(f,c,v,w):\\ f\\in\\Delta_{K},\\ f\\le u,\\ '
                      '\\mathrm{Cl}_{k}^{-}f_{k}\\le c_{k}\\le\\mathrm{Cl}_{k}^{+}f_{k},\\ '
                      '\\rho_{tk}^{-}c_{k}\\le v_{tk}\\le\\rho_{tk}^{+}c_{k},\\ '
                      's_{tk}^{-}f_{k}\\le w_{tk}\\le s_{tk}^{+}f_{k},',
                      'd_{k}^{-}f_{k}\\le w_{\\mathrm{H}k}-8\\,w_{\\mathrm{O}k}\\le d_{k}^{+}f_{k},\\ \\ '
                      '\\ell_{t}\\le\\textstyle\\sum_{k}x_{tk}\\le h_{t}\\Big\\},']))
    a(('p', 'where $x_{tk}$ is the contribution of source $k$ to tracer $t$ ($c_{k}$ for chloride) and '
            '$[\\ell_{t},h_{t}]$ is $[y_{t}-\\varepsilon_{t},y_{t}+\\varepsilon_{t}]$ for a conservative tracer, '
            '$(-\\infty,y_{t}+\\varepsilon_{t}]$ for a tracer that can only be gained, $[y_{t}-\\varepsilon_{t},\\infty)$ '
            'for a tracer that can only be lost, and $[-\\varepsilon_{t},L+\\varepsilon_{t}]$ for a value below $L$. '
            'The set is a convex polytope, exactly and not as a relaxation, and the identified set of any function of '
            'the mixture is the image of $\\mathcal{P}(y)$.'))
    a(('proof', 'For $f_{k}>0$ the change of variables $\\mathrm{Cl}_{k}=c_{k}/f_{k}$, '
                '$\\rho_{tk}=v_{tk}/c_{k}$, $s_{tk}=w_{tk}/f_{k}$ is a bijection, and each interval constraint on a '
                'composition becomes the stated pair of linear inequalities because $f_{k}$ and $c_{k}$ are '
                'nonnegative. The coupled pair: $d_{k}=(w_{\\mathrm{H}k}-8w_{\\mathrm{O}k})/f_{k}$, so its interval '
                'is linear in the same way; more generally, a composition vector in a polytope $\\{s: Gs\\le g\\}$ '
                'becomes $Gw_{k}\\le g f_{k}$, the perspective of the polytope, which is polyhedral. For $f_{k}=0$ '
                'the inequalities force $c_{k}=v_{tk}=w_{tk}=0$, and any composition is consistent. The data '
                'constraints are linear in the contributions. Every quantity of the model is therefore recovered '
                'from a point of $\\mathcal{P}(y)$ and conversely.'))
    a(('h2', '2.3 Sharp bounds of the chloride share'))
    a(('p', 'The share of the chloride of the sample that comes from source $j$ is '
            '$\\varphi_{j}=c_{j}/\\sum_{k}c_{k}$, a ratio of two linear functions.'))
    a(('prop', 'Proposition 2 (sharp bounds by linear programming).',
       'With $\\tau=1/\\sum_{k}c_{k}$ and $z=\\tau(f,c,v,w)$, the extremes of $\\varphi_{j}$ over $\\mathcal{P}(y)$ are'))
    a(('eq', 'cc', ['\\varphi_{j}^{\\mp}=\\min/\\max\\ \\Big\\{\\,z_{c_{j}}:\\ A z\\le b\\,\\tau,\\ \\ '
                    'E z=e\\,\\tau,\\ \\ \\textstyle\\sum_{k}z_{c_{k}}=1,\\ \\ \\tau\\ge 0\\Big\\},']))
    a(('p', 'where $Az\\le b$, $Ez=e$ is the description of $\\mathcal{P}(y)$. The bounds are attained, so they are '
            f'sharp {cite("charnes1962")}. For $K$ sources, the complete answer of a sample is $2K$ linear programs.'))
    a(('h2', '2.4 Well-posedness of the set'))
    a(('prop', 'Proposition 3 (existence, uniqueness, stability).',
       '(i) If the source list is complete and every composition lies in its interval, then $\\mathcal{P}(y)$ is '
       'non-empty with probability at least $1-\\sum_{t}\\alpha_{t}$; an empty set therefore falsifies the source '
       'list or the intervals at a false-alarm rate of at most $\\sum_{t}\\alpha_{t}$, and its emptiness is certified by '
       'a Farkas vector. (ii) The set is unique. (iii) If $\\mathcal{P}(y)$ and $\\mathcal{P}(y\')$ are non-empty, '
       'their Hausdorff distance is at most $H\\,\\|y-y\'\\|$, where $H$ is the Hoffman constant of the constraint '
       'matrix; the bounds of any linear function, and of $\\varphi_{j}$ where $\\sum_{k}c_{k}$ is bounded away from '
       'zero, are Lipschitz in the data.'))
    a(('proof', 'Under the hypotheses the true mixture lies in $\\mathcal{P}(y)$ whenever every error lies within its '
                'tolerance, an event of probability at least $1-\\sum_{t}\\alpha_{t}$ by the union bound. Emptiness of '
                f'a polyhedron is equivalent to the existence of a Farkas certificate {cite("farkas1902")}. The data '
                f'enter only the right-hand side, so Hoffman\'s bound {cite("hoffman1952")} applies to every point of '
                'one set and its distance to the other.'))
    a(('h2', '2.5 Coverage without a prior'))
    a(('prop', 'Proposition 4 (coverage).',
       'Under the hypotheses of Proposition 3(i), $\\Pr\\big(\\varphi_{j}\\in[\\varphi_{j}^{-},\\varphi_{j}^{+}]\\ '
       '\\text{for every } j\\big)\\ge 1-\\sum_{t}\\alpha_{t}$, whatever the distribution of the mixture.'))
    a(('p', f'With $\\varepsilon_{{t}}=2.5\\,\\sigma_{{t}}$ for Gaussian errors, $\\alpha_{{t}}=0.0124$ and the guarantee '
            f'is at least 0.91 for seven tracers. A Bayesian posterior concentrates, as data accumulate, on the '
            f'identified set and inside it follows the prior {cite("poirier1998", "moon2012")}; the width of the '
            f'identified set is the part of a credible interval that only the prior can fill. The two answers are '
            f'therefore complementary: the bounds state what the data and the stated ranges imply, and a posterior adds '
            f'what a prior assumes.'))
    a(('h2', '2.6 The value of the next action'))
    a(('p', 'A decision about source $j$ at threshold $\\theta$ (for example, seawater the main source, '
            '$\\varphi_{\\mathrm{S}}>1/2$) is *decided* by the data if $\\varphi_{j}^{-}>\\theta$ or '
            '$\\varphi_{j}^{+}<\\theta$. An action $a$ is a new tracer at the wells or the sampling of an end-member, '
            'which replaces its interval by a narrower one. Let $D_{a}$ be the number of decisions settled after $a$.'))
    a(('prop', 'Proposition 5 (goal-oriented value).',
       'Adding constraints or narrowing an interval that contains the truth shrinks $\\mathcal{P}(y)$, so a decision '
       'settled before stays settled while the set is non-empty, and the value '
       '$\\Delta(a)=\\mathbb{E}[D_{a}]-D_{0}\\ge 0$. The expectation is taken over the unknown outcome of the action, '
       'drawn from the identified set under a design distribution; the bounds themselves do not depend on it.'))
    a(('p', f'Proposition 5 compares actions of different kinds on one scale, the decisions they would settle, '
            f'following goal-oriented Bayesian design {cite("chaloner1995", "zeqiraj2026")}. Because the outcome must be '
            f'forecast, the design step needs a distribution; we use the posterior of the Bayesian mixing model of '
            f'Section 3 for this purpose only. Monotonicity fails when the action falsifies the model (the set becomes '
            f'empty), which is information of another kind.'))
    a(('h2', '2.7 Computation'))
    a(('p', f'The polytope has $K(2+n_{{t}})$ variables for $n_{{t}}$ tracers besides chloride. We solve the linear '
            f'programs with HiGHS {cite("huangfu2018")} through SciPy {cite("virtanen2020")}; the complete bounds of '
            f'one field sample with four sources and seven tracers take about 20 ms on one core. For the Bayesian '
            f'comparator we sample the posterior by sequential Monte Carlo with adaptive tempering and random-walk '
            f'Metropolis moves in unconstrained coordinates (additive log-ratio for the fractions, logit for every '
            f'bounded composition), which needs no tuning by hand and gives samples from the exact posterior of the '
            f'model.'))
    # ---------------------------------------------------------------- 3 synthetic
    a(('h', '3 Synthetic Test'))
    a(('h2', '3.1 Setting'))
    a(('p', f'The synthetic aquifer has twelve wells at 0.4 to 10 km from the coast, each with a shallow and a deep '
            f'screen, and five candidate sources: modern seawater, relict seawater, a halite brine, anthropogenic '
            f'chloride and fresh recharge. A sharp-interface wedge with a mixing zone, a relict pocket, an optional '
            f'halite body and a town near the coast generate the fractions; the compositions are drawn uniformly within '
            f'intervals taken from ranges reported in the literature; the seven tracers are chloride, a base-exchange '
            f'index per unit chloride, Br/Cl, B/Cl, the two isotopes of water and tritium, with Gaussian errors. Site '
            f'caps bound the anthropogenic fraction by land use and allow the brine only in deep screens. The target is '
            f'the share of chloride from modern seawater. A "shifted" world has more relict seawater and a halite '
            f'body more often, with the same sources and intervals. The setting and the first tests are described in '
            f'full in the review that introduced the method (==Zeqiraj, 2026, review document; cite or move to '
            f'Supporting Information==); here we summarize them and add the comparison with the two standard '
            f'alternatives.'))
    a(('h2', '3.2 What the tracers identify'))
    a(('p', f'With chloride and the major ions only, the mean width of the identified interval of the seawater share '
            f'is {num(s["z_today_w"])} and {pct(s["z_today_d"])} of the salinized samples are decided; with all seven '
            f'tracers the width is {num(s["z_all_w"])} ({pct(s["z_all_d"])} decided). Sampling the relict-water, '
            f'fresh-water and anthropogenic end-members, which narrows their intervals, brings the width to '
            f'{num(s["z_best_w"])} and the decided samples to {pct(s["z_best_d"])}: in this aquifer, characterizing '
            f'the end-members is worth more than adding tracers at the wells. The coverage of the bounds is at least '
            f'{num(s["z_cov_min"], 3)} in every configuration, and no decided sample is decided wrongly. When a deep '
            f'brine that is not in the source list is present, the set is empty in {pct(s["z_e4_empty"])} of the samples '
            f'where the brine supplies more than 0.5% of the water, and in {pct(s["z_e4_false"], 1)} of the samples '
            f'without it. The least-squares point inverse with central compositions misses the truth by more than 0.25 '
            f'in {pct(s["z_e5"]["frac_error_above_0p25"])} of the samples, and in {pct(s["z_e5"]["truth_outside_ls_range"])} '
            f'the truth lies outside the range of least-squares answers obtained by moving the assumed compositions '
            f'within their intervals; the identified set contained the truth in every sample.'))
    a(('h2', '3.3 Three answers to the same problem'))
    a(('p', f'We compare three answers on {yp7["n"]} samples per world ({Y["settings"]["n_fields"]} fields of '
            f'{Y["settings"]["samples_per_field"]} samples): the certified bounds; fixed-signature ranges in the manner '
            f'of IsoSource, with every composition at the midpoint of its interval and the same tolerances; and 90% '
            f'credible intervals of a Bayesian mixing model that is given every advantage but one: the true intervals '
            f'as uniform priors of the compositions, the true error model, the site caps, and a Dirichlet prior on the '
            f'fractions with concentration 1 or 0.25 (Figure {{{{synth}}}}). As a check of the code, the general '
            f'implementation reproduces the bounds of the review\'s code '
            f'{"exactly" if Y["check_max_diff"] == 0 else "to " + format(Y["check_max_diff"], ".0e")}.'))
    a(('img', 'synth', 16.5))
    a(('cap', f'Figure {{{{synth}}}}. Coverage (a) and mean width (b) of four answers for the share of chloride from '
              f'modern seawater, in the world of the synthetic test (A) and in a shifted world (B), with today\'s '
              f'tracers (chloride and major ions) and with all seven. Dashed: nominal level of the 90% credible intervals; the '
              f'guarantee of the certified bounds is at least 0.91 for seven tracers.'))
    a(('p', f'The certified bounds covered the truth {"in every sample" if s["cert_cov_min"] >= 1.0 else "in " + pct(s["cert_cov_min"], 1) + " or more of the samples"} '
            f'in all four cases. The fixed-signature ranges had no solution in '
            f'{pct(yp7["fixed_empty"])} of the samples with seven tracers (the midpoint compositions cannot reproduce '
            f'them) and covered the truth in {pct(yp7["fixed_cover_all"])} of all samples in the first world and '
            f'{pct(ys7["fixed_cover_all"])} in the shifted one. The Bayesian intervals are much narrower, but their '
            f'coverage depends on the prior and on how much the data say: with today\'s tracers it was '
            f'{pct(yp2["bayes1_cover"])} with the flat Dirichlet prior and {pct(yp2["bayes025_cover"])} with '
            f'concentration 0.25 in the first world, and with seven tracers {pct(yp7["bayes1_cover"])} and '
            f'{pct(yp7["bayes025_cover"])}. Where the data leave the seawater share undetermined (certified width above '
            f'0.5, {pct(yp2["share_wide"])} of the samples with today\'s tracers), the coverage of the flat-prior '
            f'intervals was {pct(yp2["bayes1_cover_wide"])}; there, the interval reports the prior. The misses fall '
            f'on both sides (the truth lies below the flat-prior interval in {pct(s["miss_below"][0])}–'
            f'{pct(s["miss_below"][1])} of the samples and above it in {pct(s["miss_above"][0])}–'
            f'{pct(s["miss_above"][1])}): the intervals are narrow because the prior fills the directions that the data '
            f'do not identify, not because the data pin the share down. The two priors '
            f'moved the posterior mean of the seawater share by {num(yp2["prior_shift_mean"])} on average and by up to '
            f'{num(yp2["prior_shift_max"])} with today\'s tracers.'))
    # ---------------------------------------------------------------- 4 field
    a(('h', '4 Field Application: The West Coast Basin, Los Angeles'))
    a(('h2', '4.1 Site and data'))
    a(('p', f'The West Coast Basin of Los Angeles County was intruded by seawater in the first half of the twentieth '
            f'century, and two barrier projects have since injected imported water to hold the sea back; oil fields '
            f'along the Newport–Inglewood structural zone add a third saline source {cite("land2004")}. '
            f'{cite_t("land2004")} sampled nested monitoring wells, production and observation wells between 1995 and '
            f'2002 and analyzed major ions, bromide, iodide, boron, the isotopes of water and tritium, among other '
            f'constituents. They considered four water types (native ground water, seawater from Santa Monica or San '
            f'Pedro Bays, imported water injected at the barriers, and oil-field brine) and interpreted every well '
            f'tracer by tracer in their Table 2, with notes on older seawater and on local recharge. These data are '
            f'public; we use Appendix A (chemistry) and Table 2 (interpretation) of the report, with three data rules '
            f'stated in advance: bromide (and iodide) values that the authors flag as affected by colorimetric '
            f'interference are treated as missing; values below the detection limit are intervals; and every tracer '
            f'measured in a sample is used, so the tracer set differs from sample to sample.'))
    a(('p', f'We extracted the tables from the published PDF with word coordinates and checked the extraction against '
            f'the report: {s["cb"]["lt4"]} of the {s["cb"]["n"]} samples with complete major ions have a charge '
            f'balance within 4% and {s["cb"]["b48"]} more within 8%, close to the report\'s statement for its 86 '
            f'samples (82 within 4%, 4 between 4 and 8%). For the six samples of the Hawthorne-1 site, the cation columns of the '
            f'printed Appendix A repeat the anion values; we do not use major ions in this paper, so this does not '
            f'affect the results. {s["n"]} samples have the isotopes of water and an interpretation in Table 2 and enter '
            f'the analysis; {s["n_hi"]} of them have more than 100 mg/L of chloride.'))
    a(('img', 'tracers', 16.5))
    a(('cap', 'Figure {{tracers}}. The samples of the West Coast Basin (dots) and the four end-member intervals '
              '(shaded) in two of the tracer planes: (a) chloride and the molar chloride-to-bromide ratio; (b) the '
              'stable isotopes of water, with the coupled interval of each source (deuterium excess). The brine '
              'isotopes are not defined in the basin and are drawn dashed. Crosses: samples whose identified set is '
              'empty (Section 4.4). Data: Land et al. (2004).'))
    a(('h2', '4.2 Sources and intervals'))
    a(('p', f'The four sources are those of {cite_t("land2004")}, and the intervals follow fixed rules (Table '
            f'{{{{iv}}}}). Native ground water is the range of the {s["n_nat"]} wells that the authors classify as '
            f'native by all four tracer columns, widened by two standard deviations of the measurement; seawater is '
            f'the composition listed in Appendix A; imported water spans the pipeline sample that feeds the Dominguez '
            f'Gap barrier and two wells the authors find to be at least 90% imported water; and the oil-field brine '
            f'takes its ranges from the report (a chloride-to-bromide molar ratio between 70 and 290, iodide of 30 to '
            f'80 mg/L, boron near 71 mg/L), with wide isotope ranges because its isotopic composition is "not well '
            f'defined" in the study area {cite("land2004")}. Iodide is treated as a tracer that can only be gained '
            f'(marine sediments release it), boron as one that can only be lost (sorption), and the other tracers as '
            f'conservative. The measurement errors are 3% for chloride and 5% for bromide, iodide and boron (our '
            f'assumption), 0.1‰ and 1‰ for δ¹⁸O and δ²H (the precision stated in the report read as two standard '
            f'deviations), and 5% plus 0.05 TU for tritium; the tolerance is 2.5 standard deviations.'))
    rows = []
    lab = {'N': 'Native ground water', 'S': 'Seawater', 'I': 'Imported water', 'B': 'Oil-field brine'}
    for k, sname in enumerate(SRC):
        rows.append([lab[sname], f'{iv["Cl"][k][0]:,.0f}–{iv["Cl"][k][1]:,.0f}',
                     f'{1e3 * iv["Br"][k][0]:.2f}–{1e3 * iv["Br"][k][1]:.2f}',
                     f'{1e3 * iv["I"][k][0]:.3f}–{1e3 * iv["I"][k][1]:.3f}',
                     f'{1e3 * iv["B"][k][0]:.2f}–{1e3 * iv["B"][k][1]:.2f}',
                     f'{iv["d18O"][k][0]:.1f} to {iv["d18O"][k][1]:.1f}'.replace('-', '−'),
                     f'{iv["d2H"][k][0]:.0f} to {iv["d2H"][k][1]:.0f}'.replace('-', '−'),
                     f'{iv["d"][0][k]:.0f} to {iv["d"][1][k]:.0f}'.replace('-', '−'),
                     f'{iv["H3"][k][0]:g}–{iv["H3"][k][1]:g}'])
    a(('table', ['Source', 'Cl (mg/L)', 'Br/Cl (×10⁻³)', 'I/Cl (×10⁻³)', 'B/Cl (×10⁻³)', 'δ¹⁸O (‰)', 'δ²H (‰)',
                 'd (‰)', 'H³ (TU)'], rows, [2.9, 1.9, 1.7, 1.7, 1.7, 1.9, 1.9, 1.6, 1.5], 8.5))
    a(('cap', 'Table {{iv}}. End-member intervals of the field application (mass ratios to chloride). Rules: native '
              'water, hull of the wells classified native by all four tracers in Table 2 of Land et al. (2004), padded '
              'by two standard deviations, with iodide from zero because it can only be gained; seawater, Appendix A '
              'of the report; imported water, hull of the pipeline sample WB #37 and of wells 351-E and 351-G; '
              'oil-field brine, ranges stated in the report, isotopes wide by assumption; seawater tritium is not '
              'measured and is assumed to lie between 0 and 3 TU; the upper end of the imported-water tritium allows '
              'decayed bomb-era injection water and is our assumption.'))
    a(('h2', '4.3 What the data certify'))
    a(('p', f'Figure {{{{field}}}} shows the identified intervals of the seawater and brine shares of chloride for the '
            f'{s["n_hi"]} samples above 100 mg/L. Chloride alone decides nothing. With all tracers, seawater is '
            f'certified as the main source (lower bound above 1/2) in {s["n_smain"]} samples '
            f'({wlist(s["smain"])}); in {"every one" if s["agree_s"] == s["n_smain"] else str(s["agree_s"])} of them the chloride-to-bromide interpretation of '
            f'{cite_t("land2004")} also names seawater. Of the {s["n_rep_s"]} samples above 100 mg/L that the report '
            f'attributes to seawater by the chloride-to-bromide ratio, {s["rep_s_cert"]} are certified as seawater '
            f'dominated, {s["rep_s_present"] - s["rep_s_cert"]} more have a certified seawater share above 1/4 without '
            f'reaching 1/2, and {s["rep_s_empty"]} have an empty set (Section 4.4). For the oil-field brine the picture '
            f'is different. A brine component (a lower bound of the brine share above 2%) is certified in '
            f'{s["n_bpos"]} samples. Of the {s["n_rep_b"]} samples that the report attributes to brine by the '
            f'chloride-to-bromide ratio, {s["n_rep_b_pos"]} are among them, with lower bounds from '
            f'{num(s["rep_b_pos_lo"][0])} to {num(s["rep_b_pos_lo"][1])}; for the other '
            f'{s["n_rep_b"] - s["n_rep_b_pos"]} the data allow no brine at all. The brine share is certified above 10% '
            f'in {words(s["n_bpres"])} sample{"s" if s["n_bpres"] != 1 else ""} and as the main source in {"none" if s["rep_b_main"] == 0 else words(s["rep_b_main"])}, '
            f'and seawater could supply up to {num(s["rep_b_s_hi"])} of the chloride of these samples (median upper '
            f'bound). The reason is the brine end-member itself: '
            f'with a chloride-to-bromide ratio anywhere between 70 and 290, a small amount of a bromide-rich brine '
            f'explains the bromide excess, and seawater can supply most of the chloride. The tracers establish that a '
            f'brine is present; that it dominates rests on information beyond the four tracers and the stated '
            f'ranges, such as the geophysical logs and the history of the wells that the authors also used. '
            f'{"No certified result contradicts the report." if not s["contra"] else "Certified results contradict the report in: " + wlist(s["contra"]) + "."}'))
    a(('img', 'field', 16.5))
    a(('cap', 'Figure {{field}}. Identified intervals of the share of chloride from seawater (a) and from oil-field '
              'brine (b) for the samples above 100 mg/L, sorted by chloride, with the chloride concentration and the '
              'source named by the chloride-to-bromide ratio in Table 2 of Land et al. (2004) (S seawater, B brine, N '
              'native, I imported; hyphens join alternatives). Dashed: the decision thresholds (seawater the main '
              'source; brine above 10%). Diamonds: decided.'))
    a(('h2', '4.4 Six samples the source list cannot explain'))
    diag = s['diag']
    culprits_br = [w for w, d in diag.items() if d.get('Br') and sum(d.values()) == 1]
    multi = [w for w, d in diag.items() if sum(d.values()) == 0]
    both = [w for w, d in diag.items() if sum(d.values()) >= 2]
    a(('p', f'For {words(s["n_empty"])} samples the identified set is empty: no mixture of the four sources, with '
            f'compositions in their intervals, reproduces the data within the tolerances. Proposition 3 makes this a '
            f'test with a false-alarm rate below 0.09 for seven tracers, and removing one tracer at a time shows which '
            f'measurement carries the contradiction. For {wlist(multi)}, no single tracer restores a solution; these '
            f'two wells carry isotopically heavy, low-chloride water that {cite_t("land2004")} attribute to local '
            f'recharge from the Palos Verdes Hills, a fifth water type that is not among the four sources. For '
            f'{wlist(culprits_br)}, removing bromide restores a solution: their chloride-to-bromide ratio is above that '
            f'of seawater at chloride concentrations that no listed bromide-poor source (only the imported water) can '
            f'reach, so either the bromide is low analytically or a bromide-poor saline water is present. For '
            f'{wlist(both)}, removing either bromide or boron restores a solution; the authors describe this deep sample '
            f'as old seawater "with distinct major-ion composition and trace-element ratios". In each case the empty '
            f'set says something specific and checkable that a point estimate would have hidden. With a tolerance of '
            f'3.5 standard deviations instead of 2.5 the empty sets fall to {words(len(s["sens"]["k=3.5"]))} '
            f'({wlist(s["sens"]["k=3.5"])}); with a native chloride range extended to 220 mg/L they are '
            f'{words(len(s["sens"]["native Cl to 220 mg/L"]))}.'))
    a(('table', ['Sample', 'Cl (mg/L)', 'Interpretation in Land et al. (2004)', 'Tracer whose removal restores a '
                 'solution'],
       [[w, f'{F["cl"][F["names"].index(w)]:,.0f}', F['table2'][w]['comment'].replace('- ', '-') or '—',
         ', '.join(k for k, v in diag[w].items() if v) or 'none (a missing source)'] for w in s['empty']],
       [3.0, 1.8, 8.0, 4.2], 9.0))
    a(('cap', 'Table {{empty}}. The samples with an empty identified set, the interpretation of the original study '
              '(comment column of its Table 2) and the diagnosis.'))
    a(('h2', '4.5 Which tracers decide'))
    a(('p', f'Adding the tracers one group at a time (Figure {{{{decide}}}}) shows where the decisions come from. '
            f'Bromide settles the seawater question in {d_br[0]} samples; the isotopes and tritium add little to it, '
            f'and their main effect is to expose the inconsistent samples. The brine question is settled by iodide: '
            f'treated as a tracer that can only be gained, a low iodide caps the brine share, and the brine decisions '
            f'rise from {d_trit[1]} to {d_iod[1]}. Boron, which can be lost by sorption and varies widely in native '
            f'water, settles nothing new; it makes {words(d_all[2] - d_iod[2])} more set empty (Long Beach-5 #1), '
            f'which leaves {d_all[1]} brine decisions with all tracers.'))
    a(('img', 'decide', 16.5))
    a(('cap', 'Figure {{decide}}. Decisions settled (a) and mean width of the seawater interval (b) for nested tracer '
              'sets, samples above 100 mg/L. Empty sets count as undecided and are shown separately.'))
    a(('h2', '4.6 Fixed signatures and priors on the same samples'))
    claims = s['claims']
    a(('p', f'With every composition held fixed, as IsoSource requires (the end-members reported by '
            f'{cite_t("land2004")}, with the Long Beach-2 reference wells for native water, and interval midpoints '
            f'where the report gives no value), {s["fx_empty"]} of the {s["n"]} samples have no feasible mixture at '
            f'all: real end-members vary, and one composition per source cannot represent them. The Bayesian posteriors (Figure '
            f'{{{{compare}}}}) are narrow, and for most samples they lie inside the identified intervals '
            f'({s["bayes_tot"] - s["bayes_outside"]} of {s["bayes_tot"]} source shares), as they should up to the '
            f'soft tails of a Gaussian likelihood. But their '
            f'location inside the interval comes from the prior: for brine-affected samples the posterior mean of the '
            f'seawater share moved by up to {num(s["shift_s_max"])} between the two Dirichlet priors (mean '
            f'{num(s["shift_s_mean"])}), and that of the brine share by up to {num(s["shift_b_max"])}. In '
            f'{s["n_claim_wells"]} samples, {s["nat_claim"]} of them classified native by every tracer, the 90% '
            f'interval of the flat-prior posterior excludes a zero share of seawater or brine although the data allow '
            f'it. A uniform prior on water fractions is not uniform on chloride shares, because a fraction of a '
            f'percent of seawater or brine carries much of the chloride of a fresh sample.'))
    a(('img', 'compare', 16.5))
    a(('cap', 'Figure {{compare}}. The share of chloride from seawater in nine samples: identified interval (this '
              'work), fixed-signature range (IsoSource-type; often no solution), and posterior mean and 90% interval '
              'of the Bayesian mixing model under two priors.'))
    a(('h2', '4.7 The next measurement'))
    rb, ri, rh = r_br, r_iso, r_h3
    a(('p', f'The design rule of Proposition 5 can be tested retrospectively: hold out a tracer that was measured, '
            f'predict from the remaining data how many decisions it would settle, and compare with what the actual '
            f'measurement settles (Figure {{{{next}}}}a). For bromide, the rule predicted {num(rb["pred"][0] - rb["base"][0], 1)} '
            f'more seawater decisions and {num(rb["pred"][1] - rb["base"][1], 1)} more brine decisions; the real '
            f'bromide settled {int(rb["real"][0] - rb["base"][0])} and {int(rb["real"][1] - rb["base"][1])}, and it '
            f'made {rb["new_empty"]} sets empty, against {num(rb["pred_empty"], 1)} expected. For the isotopes the '
            f'prediction was {num(ri["pred"][0] - ri["base"][0], 1)} and {num(ri["pred"][1] - ri["base"][1], 1)}, the '
            f'realization {int(ri["real"][0] - ri["base"][0])} and {int(ri["real"][1] - ri["base"][1])}, with '
            f'{ri["new_empty"]} new empty sets; for tritium {num(rh["pred"][0] - rh["base"][0], 1)} and '
            f'{num(rh["pred"][1] - rh["base"][1], 1)} against {int(rh["real"][0] - rh["base"][0])} and '
            f'{int(rh["real"][1] - rh["base"][1])}. The rule forecasts the gains of a model that is right; where the '
            f'real measurement reveals that the model is wrong, the gain turns into a falsification, which the rule '
            f'cannot forecast and which is worth having.'))
    acts = s['acts']
    lines = []
    for key, v in acts.items():
        if v['mean'] is None:
            lines.append(f'{key}: none of {v["cand"]} candidate compositions is consistent with all samples')
        else:
            lines.append(f'{key}: {v["consistent"]} of {v["cand"]} candidate compositions consistent with all samples; '
                         f'expected decisions {num(v["mean"][0], 1)} (seawater) and {num(v["mean"][1], 1)} (brine), '
                         f'against {int(s["base_dec"][0])} and {int(s["base_dec"][1])} today')
    a(('p', f'Characterizing an end-member is evaluated in the same way (Figure {{{{next}}}}b): a candidate '
            f'composition is drawn within the current interval, the interval is narrowed to the measurement error '
            f'around it ("point") or to a sub-interval of half its width ("half"), and candidates that would make a '
            f'currently consistent sample inconsistent are rejected by the data. ' + '; '.join(lines) + '. '
            f'Two results stand out. First, characterizing the oil-field brine is by far the most valuable action: '
            f'with its intervals halved around data-consistent values, the expected number of settled brine '
            f'decisions rises from {int(s["base_dec"][1])} to {num(acts["sample the brine (half)"]["mean"][1], 1)}, and '
            f'two to three seawater decisions are settled as well, whereas characterizing the imported water or the '
            f'tritium of seawater settles about one decision or none. This is the end-member that '
            f'{cite_t("land2004")} describe as not well defined. Second, no brine composition measured to analytical '
            f'precision was consistent with all samples, while some half-width intervals were: the samples do not '
            f'admit one brine of fixed composition, which suggests that more than one brine, or a brine that varies '
            f'between oil fields, reaches the wells. The retrospective test also shows the limits of the design rule. '
            f'It forecast the gain of tritium exactly, but it overstated the gain of bromide for the brine question, '
            f'because its design distribution, the flat-prior posterior, places more brine in the samples than the '
            f'data later supported; a design distribution needs the same scrutiny as a prior.'))
    a(('img', 'next', 16.5))
    a(('cap', 'Figure {{next}}. The next action. (a) Held-out tracers: decisions predicted by the design rule (light) '
              'and settled by the real measurement (dark). (b) Characterizing an end-member: expected decisions '
              'settled, with the 10–90% range over data-consistent candidate compositions; the number kept is shown '
              'below each bar.'))
    # ---------------------------------------------------------------- 5 discussion
    a(('h', '5 Discussion'))
    a(('p', f'**What the bounds add to an expert interpretation.** In the West Coast Basin the certified bounds '
            f'{"agree with the original interpretation wherever they decide" if not s["contra"] else "disagree with the original interpretation in " + wlist(s["contra"])}, and they separate two kinds of conclusion that '
            f'the original table presents alike: conclusions that the tracers and the stated end-member ranges force '
            f'(seawater in {s["n_smain"]} samples, a brine component in {s["n_bpos"]}), and conclusions that rest on '
            f'additional judgement (a brine as the main source). The same table also gains a column it did not have: '
            f'samples whose chemistry the four water types cannot produce. None of this replaces the hydrogeologist; '
            f'it shows the hydrogeologist which part of the interpretation is carried by the data.'))
    a(('p', f'**Relation to IsoSource and to Bayesian mixing models.** The identified set generalizes the feasible '
            f'range of IsoSource {cite("phillips2003")} in four ways: end-members are intervals rather than points, the '
            f'range is computed exactly rather than on a grid, the chloride share is bounded directly although it is a '
            f'ratio, and the range carries a coverage statement and a falsification test. Relative to Bayesian mixing '
            f'models {cite("moore2008", "stock2018")} the bounds give up a single best answer to gain independence from '
            f'the prior. We see the two as steps of one workflow: report the bounds first; where they decide, the '
            f'decision needs no prior; where they do not, a posterior may be used if its prior can be defended, and '
            f'the width of the bounds tells how much of the answer the prior supplies.'))
    a(('p', '**Assumptions.** The guarantee rests on three assumptions: the source list is complete, every '
            'composition lies in its interval, and the errors lie within the tolerances with the stated '
            'probabilities. The first two are exactly what the falsification test examines, but a test can only '
            'reject; a non-empty set does not prove the list complete. The intervals are the scientific input of the '
            'method, and they should be set by rules stated in advance, as here; where an interval is a guess (the '
            'brine isotopes, the tritium of seawater), the bounds are as wide as the guess. Mixing is assumed linear '
            'and instantaneous; reactions enter only as the sign of a gain or a loss; well-bore effects in long '
            'screens, which Land et al. (2004) discuss, are not modeled. Transport and the geometry of the aquifer '
            'enter only through site caps, and coupling the bounds to flow models is the natural next step.'))
    a(('p', '**Practical recommendations.** (1) Report identified intervals of source shares, not only point '
            'estimates, whenever the candidate sources outnumber the conservative tracers. (2) State the end-member '
            'intervals and the rules that set them. (3) Treat an empty set as a finding and diagnose it tracer by '
            'tracer. (4) Treat reactive tracers by the sign of their reaction; iodide treated in this way was the '
            'tracer that decided the brine question here. (5) Before the next campaign, compare tracers at the wells '
            'with the sampling of end-members by the decisions they would settle.'))
    # ---------------------------------------------------------------- 6 conclusions
    a(('h', '6 Conclusions'))
    a(('p', f'The attribution of chloride to its sources is ill-posed as a point problem and well-posed as a set '
            f'problem. With the bilinear mixing terms lifted to contributions, the set of mixtures and end-member '
            f'compositions consistent with the data is an exact polytope; sharp bounds of each chloride share are '
            f'linear programs; an empty set falsifies the source list; and the bounds cover the truth without a prior. '
            f'In a synthetic aquifer the bounds kept their coverage where fixed-signature ranges and Bayesian credible '
            f'intervals did not. In the West Coast Basin of Los Angeles they certified seawater in {s["n_smain"]} '
            f'samples and a brine component in {s["n_bpos"]}, located the evidence for brine in iodide, and flagged '
            f'{words(s["n_empty"])} samples whose chemistry the four water types cannot explain. The method is cheap '
            f'(a few dozen linear programs per sample), needs no tuning, and turns the question "where does the '
            f'chloride come from?" into a statement of what is known, what is not, and what to measure next.'))
    # ---------------------------------------------------------------- back matter
    a(('h', 'Open Research'))
    a(('p', f'The field data are public and were taken from Appendix A and Table 2 of {cite_t("land2004")}, '
            'https://doi.org/10.3133/sir20045067. The code that extracts them, all experiments, the figures and this '
            'manuscript\'s numbers are available at ==[Zenodo DOI to be minted at submission]== (development '
            'version: https://github.com/dulianzeqiraj/swi-goal-oed, folder experiments/zanafilla_go/wrr); the '
            'synthetic experiments are fully reproducible from the code. Software: Python with NumPy, SciPy '
            f'{cite("virtanen2020")} and the HiGHS solver {cite("huangfu2018")}.'))
    a(('h', 'Use of AI Tools'))
    a(('p', '==Generative AI (Claude Code, Anthropic) assisted with the literature search, the code and the drafting of '
            'this manuscript. The author checked every statement, number and reference and takes full responsibility '
            'for the content. Wording and placement to be checked against the current AGU policy before submission.=='))
    a(('h', 'Acknowledgments'))
    a(('p', '==[Funding, permissions and acknowledgments to be completed by the author.]== We thank the U.S. '
            'Geological Survey for making the West Coast Basin data public.'))
    a(('refs',))
    return A, s


ORDER = ['alcala2008', 'barthold2011', 'chaloner1995', 'charnes1962', 'christophersen1992', 'craig1961',
         'dansgaard1964', 'davis1998', 'farkas1902', 'genereux1998', 'gustafson2015', 'hadamard1902', 'hoffman1952',
         'hooper2003', 'huangfu2018', 'imbens2004', 'katz2011', 'land2004', 'manski2003', 'moon2012', 'moore2008',
         'oldenburg1983', 'panno2006', 'parnell2010', 'phillips2003', 'phillips2014', 'poirier1998', 'stark1992',
         'stark2015', 'stock2018', 'tamer2010', 'vengosh2005', 'vengosh2014', 'virtanen2020', 'werner2013', 'code',
         'zeqiraj2026']


def all_refs(text):
    """References cited in the text, in AGU order (alphabetical); every DOI from Crossref."""
    out = []
    for k in ORDER:
        line, url = ref_line(k)
        out.append(dict(key=k, text=line, url=url))
    out.sort(key=lambda r: r['text'].lower())
    return out
