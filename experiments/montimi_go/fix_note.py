"""Fix points 1, 2 and 5 of the review of the MONTIMI-GO note, editing the author's Word file in place (text nodes
only; OMML equations are never touched). usage: python -I fix_note.py IN.docx OUT.docx
(8 November 2026: applied to docs/research_notes/Assembled_System_Equations_Placing_Recharge_and_Pumping_Wells.docx)"""
import copy
import sys

from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

IN, OUT = sys.argv[1], sys.argv[2]
doc = Document(IN)
body = doc.element.body
MATH = {qn('m:oMath'), qn('m:oMathPara')}


def paragraphs():
    return list(body.iter(qn('w:p')))


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(qn('w:t')))


def top_child(p, node):
    while node.getparent() is not p:
        node = node.getparent()
    return node


def replace_in(p, old, new):
    ts = list(p.iter(qn('w:t')))
    full = ''.join(t.text or '' for t in ts)
    i = full.find(old)
    if i < 0:
        return False
    j = i + len(old)
    pos, first, last = 0, None, None
    spans = []
    for k, t in enumerate(ts):
        a, b = pos, pos + len(t.text or '')
        spans.append((a, b))
        if first is None and b > i:
            first = k
        if a < j:
            last = k
        pos = b
    kids = list(p)
    i0, i1 = kids.index(top_child(p, ts[first])), kids.index(top_child(p, ts[last]))
    if any(c.tag in MATH for c in kids[i0:i1 + 1]):
        raise SystemExit(f'math inside the span of: {old[:60]}')
    for k in range(first, last + 1):
        a, b = spans[k]
        txt = ts[k].text or ''
        before = txt[:max(0, i - a)] if k == first else ''
        after = txt[j - a:] if k == last else ''
        ts[k].text = before + (new if k == first else '') + after
        ts[k].set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return True


def replace_all(old, new, expect):
    n = 0
    for p in paragraphs():
        while old in ptext(p):
            if not replace_in(p, old, new):
                break
            n += 1
            if new.find(old) >= 0:
                break
    if n != expect:
        raise SystemExit(f'{n} replacements (expected {expect}) for: {old[:70]}')
    print(f'{n}x  {old[:70]}')


# ---- point 1: the numbers of draws -----------------------------------------------------------------------------
replace_all('40 design draws (the cheap assemblies choose), 40 evaluation draws (the complete assembly judges)',
            '25 design draws (the cheap assemblies choose; 10 for the two counter-examples), 25 evaluation draws (the '
            'complete assembly judges) and 40 calibration cases for the margin (16 for the counter-examples)', 1)
replace_all('with and without the calibrated margin of Proposition M4 estimated from 40 calibration cases.',
            'with and without the calibrated margin of Proposition M4 estimated from 40 calibration cases (16 for the '
            'two counter-examples).', 1)

# ---- point 2: what 25 draws can and cannot show ---------------------------------------------------------------
replace_all('whose risk judged on 25 draws of the complete assembly is 8% against the 10% allowed.',
            'whose risk judged on 25 draws of the complete assembly is 8% (2 of 25; 95% interval 1–26%), against a target '
            'of 10% and a guarantee of 20%, the target plus the calibration level.', 2)
replace_all('(target 10%, guarantee 10% + ', '(target 10%; 1 of 25 draws is 4%, 95% interval 0.1–20%, and 2 of 25 is '
            '8%, 1–26%; guarantee 10% + ', 1)
replace_all('≤ 10% by construction', '≤ 10% on its own 25 draws; 11.5% expected on a new draw (Remark G2)', 1)
replace_all('The uniform assembly chooses the supply well at 3.5 km and recharge well at 3.0 km at 5.98 m²/d, with a '
            'risk of 8%.',
            'The uniform assembly chooses the supply well at 3.5 km and recharge well at 3.0 km at 5.98 m²/d, with a '
            'risk of 8%. These risks rest on 25 evaluation draws: 1 of 25 (4%) has a 95% interval of 0.1–20% and 2 of '
            '25 (8%) of 1–26%. They show that no assembly fails badly, not that the 10% target is met; the guarantee of '
            'Proposition M4 is 10% + β = 20%, and a few hundred evaluation draws of the chosen layouts would be needed to '
            'show the target itself.', 1)
# Remark G2 after the paragraph on monotonicity
anchor = [p for p in paragraphs() if ptext(p).startswith('Monotonicity holds in every run of the test')]
assert len(anchor) == 1
src = anchor[0]
new_p = copy.deepcopy(src)
for child in list(new_p):
    if child.tag != qn('w:pPr'):
        new_p.remove(child)
template = copy.deepcopy(src.find(qn('w:r')))
for t in template.findall(qn('w:t')):
    template.remove(t)
src.addnext(new_p)


def add_run(p_el, text, bold=False):
    r = copy.deepcopy(template)
    rpr = r.find(qn('w:rPr'))
    if bold:
        if rpr is None:
            rpr = r.makeelement(qn('w:rPr'), {})
            r.insert(0, rpr)
        rpr.append(rpr.makeelement(qn('w:b'), {}))
    t = r.makeelement(qn('w:t'), {})
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r.append(t)
    p_el.append(r)


add_run(new_p, 'Remark G2 (on the draws and beyond them). ', bold=True)
add_run(new_p, 'Constraint (50) holds on the draws used. For a new draw exchangeable with them, and without ties, the '
               'probability that its critical rate falls below Q_c,(m) is m/(N_θ + 1): 3/26 = 11.5% for N_θ = 25 and '
               'α = 10%, slightly above α. Taking m = ⌊α(N_θ + 1)⌋ instead keeps it at most α (2/26 = 7.7% here). A '
               'statement that holds with high probability, rather than on average over the draws, needs a binomial '
               'bound and more draws.')
print('1x  Remark G2 inserted')

# ---- point 5: the references --------------------------------------------------------------------------------------
REFS = {
    'Voss, C. I. & Souza, W. R. (1987).':
        'Voss, C. I. & Souza, W. R. (1987). Variable density flow and solute transport simulation of regional aquifers '
        'containing a narrow freshwater–saltwater transition zone. Water Resources Research, 23(10), 1851–1866. '
        'https://doi.org/10.1029/WR023i010p01851',
    'Haggerty, R. & Gorelick, S. M. (1995).':
        'Haggerty, R. & Gorelick, S. M. (1995). Multiple-rate mass transfer for modeling diffusion and surface reactions '
        'in media with pore-scale heterogeneity. Water Resources Research, 31(10), 2383–2400. '
        'https://doi.org/10.1029/95WR01583',
    'Bear, J. (1979).': 'Bear, J. (1979). Hydraulics of Groundwater. McGraw-Hill, New York (reprinted by Dover, 2007).',
    'Council of the European Union (1998).':
        'Council of the European Union (1998). Council Directive 98/83/EC of 3 November 1998 on the quality of water '
        'intended for human consumption. Official Journal of the European Communities, L 330, 5.12.1998, 32–54; Annex I, '
        'Part C, indicator parameters: chloride 250 mg/L, sodium 200 mg/L. Repealed with effect from 12 January 2023 by '
        'Directive (EU) 2020/2184 (Official Journal of the European Union, L 435, 23.12.2020); the values should be '
        'checked against Annex I, Part C of the recast.',
    'Gaines, G. L. & Thomas, H. C. (1953).':
        'Gaines, G. L. & Thomas, H. C. (1953). Adsorption studies on clay minerals. II. A formulation of the '
        'thermodynamics of exchange adsorption. The Journal of Chemical Physics, 21(4), 714–718. '
        'https://doi.org/10.1063/1.1698996',
    'Appelo, C. A. J. & Postma, D. (2005).':
        'Appelo, C. A. J. & Postma, D. (2005). Geochemistry, Groundwater and Pollution, second edition. A. A. Balkema, '
        'Leiden; CRC Press. https://doi.org/10.1201/9781439833544',
    'Plummer, L. N., Wigley, T. M. L. & Parkhurst, D. L. (1978).':
        'Plummer, L. N., Wigley, T. M. L. & Parkhurst, D. L. (1978). The kinetics of calcite dissolution in CO2–water '
        'systems at 5° to 60 °C and 0.0 to 1.0 atm CO2. American Journal of Science, 278(2), 179–216. '
        'https://doi.org/10.2475/ajs.278.2.179',
    'Davies, C. W. (1962).': 'Davies, C. W. (1962). Ion Association. Butterworths, London, 190 pp.',
    'Stuyfzand, P. J. (2008).':
        'Stuyfzand, P. J. (2008). Base exchange indices as indicators of salinization or freshening of (coastal) '
        'aquifers. In: Proceedings of the 20th Salt Water Intrusion Meeting (SWIM 20), 23–27 June 2008, Naples, '
        'Florida, USA (pages not checked).',
    'Vovk, V., Gammerman, A. & Shafer, G. (2005).':
        'Vovk, V., Gammerman, A. & Shafer, G. (2005). Algorithmic Learning in a Random World. Springer, New York. '
        'https://doi.org/10.1007/b106715',
    "Lei, J., G'Sell, M., Rinaldo, A., Tibshirani, R. J. & Wasserman, L. (2018).":
        "Lei, J., G'Sell, M., Rinaldo, A., Tibshirani, R. J. & Wasserman, L. (2018). Distribution-free predictive "
        "inference for regression. Journal of the American Statistical Association, 113(523), 1094–1111. "
        "https://doi.org/10.1080/01621459.2017.1307116",
}
for start, new in REFS.items():
    hits = [p for p in paragraphs() if start in ptext(p) and ('not verified' in ptext(p) or 'details not verified' in ptext(p))]
    if len(hits) != 1:
        raise SystemExit(f'{len(hits)} reference paragraphs for {start}')
    p = hits[0]
    full = ptext(p)
    old = full[full.index(start):]
    replace_all(old, new, 1)
replace_all('References marked "not verified" were not checked against the publisher.',
            'The references of other authors were checked against Crossref, the Official Journal or library catalogues '
            '(the eleven formerly marked "not verified" on 8 November 2026); the notes of the author\'s series ([2]–[12], '
            '[22], [23], [48]) are unpublished and available from the author.', 1)
left = [ptext(p)[:60] for p in paragraphs() if 'not verified' in ptext(p)]
print('paragraphs still saying "not verified":', left)
doc.save(OUT)
print('saved', OUT)
