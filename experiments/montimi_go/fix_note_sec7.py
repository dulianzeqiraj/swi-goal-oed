"""Second correction of the MONTIMI-GO note (8 November 2026): the limits in Section 7 on the cut of the sea-level
rise and on reading chloride as seawater, three new references [49]-[51], and the reference formatting (italic
journal, DOI as a hyperlink) restored for the eleven references completed in the first correction.
usage: python -I fix_note_sec7.py IN.docx OUT.docx"""
import copy
import sys

from docx import Document
from docx.oxml.ns import qn

IN, OUT = sys.argv[1], sys.argv[2]
doc = Document(IN)
body = doc.element.body
RT_LINK = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink'
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'


def paragraphs():
    return list(body.iter(qn('w:p')))


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(qn('w:t')))


def one(pred, what):
    hits = [p for p in paragraphs() if pred(ptext(p))]
    if len(hits) != 1:
        raise SystemExit(f'{len(hits)} paragraphs for {what}')
    return hits[0]


# ---------------------------------------------------------------- Section 7: the limits
lim = one(lambda t: t.startswith('The limits of the test are those of a cross-section.'), 'limits paragraph')
OLD = 'The prices of conveyance and recharge are illustrative.'
NEW = (OLD + ' The sea-level rise was cut because the inland boundary of the section fixes the fresh inflow, so the whole '
       'head field rises with the sea and almost no water moves [49]. Where drains or a low land surface cap the water '
       'table, as on the plain of Durrës, where subsidence adds to the rise, or where pumping holds the heads below sea '
       'level, the rise steepens the gradients towards the wells and can move the wedge inland [49, 50]. The cut is '
       'therefore a property of this goal, this boundary and this horizon, not of the coast: in the three-dimensional '
       'model the relative sea level measured at each wellfield (InSAR and GNSS) stays in the assembly until its weight '
       'has been recomputed there. In the same way the sea fraction is read from chloride, which is right only where all '
       'the chloride is seawater; where it may also come from a drought that concentrates the recharge or from '
       'irrigation return flow, the ions that Theorem M1 cuts (Br/Cl, Na/Cl, nitrate, boron) carry the evidence about '
       'the source, and the placement must hold for every source that tracers cannot exclude [51].')
done = False
for t in lim.iter(qn('w:t')):
    if t.text and OLD in t.text:
        t.text = t.text.replace(OLD, NEW, 1); t.set(XML_SPACE, 'preserve'); done = True
        break
if not done:
    raise SystemExit('the sentence on prices is split across runs')
print('Section 7: limits added')

# ---------------------------------------------------------------- references
tmpl = one(lambda t: t.startswith('[25]'), 'template [25]')
runs = tmpl.findall(qn('w:r'))
LABEL, PLAIN, ITALIC = runs[0], runs[1], runs[2]
LINK = tmpl.find(qn('w:hyperlink'))


def clone_run(src, text):
    r = copy.deepcopy(src)
    for t in r.findall(qn('w:t')):
        r.remove(t)
    tab = r.find(qn('w:tab'))
    t = r.makeelement(qn('w:t'), {})
    t.text = text; t.set(XML_SPACE, 'preserve')
    if tab is not None:
        tab.addprevious(t)
    else:
        r.append(t)
    return r


def fill(p, label, plain, italic, rest, url=None):
    for child in list(p):
        if child.tag != qn('w:pPr'):
            p.remove(child)
    p.append(clone_run(LABEL, label + '\t'))
    p.append(clone_run(PLAIN, plain))
    p.append(clone_run(ITALIC, italic))
    p.append(clone_run(PLAIN, rest))
    if url:
        h = copy.deepcopy(LINK)
        h.set(qn('r:id'), doc.part.relate_to(url, RT_LINK, is_external=True))
        hr = h.findall(qn('w:r'))
        for extra in hr[1:]:
            h.remove(extra)
        for t in hr[0].findall(qn('w:t')):
            hr[0].remove(t)
        t = hr[0].makeelement(qn('w:t'), {}); t.text = url; hr[0].append(t)
        p.append(h)


REFS = [
    ('[13]', 'Voss, C. I. & Souza, W. R. (1987). Variable density flow and solute transport simulation of regional '
             'aquifers containing a narrow freshwater–saltwater transition zone. ', 'Water Resources Research',
     ', 23(10), 1851–1866. ', 'https://doi.org/10.1029/WR023i010p01851'),
    ('[15]', 'Haggerty, R. & Gorelick, S. M. (1995). Multiple-rate mass transfer for modeling diffusion and surface '
             'reactions in media with pore-scale heterogeneity. ', 'Water Resources Research', ', 31(10), 2383–2400. ',
     'https://doi.org/10.1029/95WR01583'),
    ('[16]', 'Bear, J. (1979). ', 'Hydraulics of Groundwater', '. McGraw-Hill, New York (reprinted by Dover, 2007).', None),
    ('[17]', 'Council of the European Union (1998). Council Directive 98/83/EC of 3 November 1998 on the quality of water '
             'intended for human consumption. ', 'Official Journal of the European Communities',
     ', L 330, 5.12.1998, 32–54; Annex I, Part C, indicator parameters: chloride 250 mg/L, sodium 200 mg/L. Repealed '
     'with effect from 12 January 2023 by Directive (EU) 2020/2184 (Official Journal of the European Union, L 435, '
     '23.12.2020); the values should be checked against Annex I, Part C of the recast.', None),
    ('[18]', 'Gaines, G. L. & Thomas, H. C. (1953). Adsorption studies on clay minerals. II. A formulation of the '
             'thermodynamics of exchange adsorption. ', 'The Journal of Chemical Physics', ', 21(4), 714–718. ',
     'https://doi.org/10.1063/1.1698996'),
    ('[19]', 'Appelo, C. A. J. & Postma, D. (2005). ', 'Geochemistry, Groundwater and Pollution',
     ', second edition. A. A. Balkema, Leiden; CRC Press. ', 'https://doi.org/10.1201/9781439833544'),
    ('[20]', 'Plummer, L. N., Wigley, T. M. L. & Parkhurst, D. L. (1978). The kinetics of calcite dissolution in '
             'CO2–water systems at 5° to 60 °C and 0.0 to 1.0 atm CO2. ', 'American Journal of Science',
     ', 278(2), 179–216. ', 'https://doi.org/10.2475/ajs.278.2.179'),
    ('[21]', 'Davies, C. W. (1962). ', 'Ion Association', '. Butterworths, London, 190 pp.', None),
    ('[24]', 'Stuyfzand, P. J. (2008). Base exchange indices as indicators of salinization or freshening of (coastal) '
             'aquifers. In: ', 'Proceedings of the 20th Salt Water Intrusion Meeting (SWIM 20)',
     ', 23–27 June 2008, Naples, Florida, USA (pages not checked).', None),
    ('[41]', 'Vovk, V., Gammerman, A. & Shafer, G. (2005). ', 'Algorithmic Learning in a Random World',
     '. Springer, New York. ', 'https://doi.org/10.1007/b106715'),
    ('[42]', "Lei, J., G'Sell, M., Rinaldo, A., Tibshirani, R. J. & Wasserman, L. (2018). Distribution-free predictive "
             "inference for regression. ", 'Journal of the American Statistical Association', ', 113(523), 1094–1111. ',
     'https://doi.org/10.1080/01621459.2017.1307116'),
]
for label, plain, italic, rest, url in REFS:
    p = one(lambda t, l=label: t.startswith(l), label)
    fill(p, label, plain, italic, rest, url)
print('references re-formatted:', len(REFS))
NEW_REFS = [
    ('[49]', 'Werner, A. D. & Simmons, C. T. (2009). Impact of sea-level rise on sea water intrusion in coastal aquifers. ',
     'Groundwater', ', 47(2), 197–204. ', 'https://doi.org/10.1111/j.1745-6584.2008.00535.x'),
    ('[50]', 'Michael, H. A., Russoniello, C. J. & Byron, L. A. (2013). Global assessment of vulnerability to sea-level '
             'rise in topography-limited and recharge-limited coastal groundwater systems. ', 'Water Resources Research',
     ', 49(4), 2228–2240. ', 'https://doi.org/10.1002/wrcr.20213'),
    ('[51]', 'Zeqiraj, D. (2026). ', 'Stakeholder decisions V: deciding when nobody knows where the chloride comes from',
     '. Thirty papers from Oxford, Caltech, Harvard and MIT and the innovation PREJARDHJA-GO. Review of the author\'s '
     'series (8 November 2026).', None),
]
last = one(lambda t: t.startswith('[48]'), '[48]')
for label, plain, italic, rest, url in NEW_REFS:
    p = copy.deepcopy(last)
    fill(p, label, plain, italic, rest, url)
    last.addnext(p)
    last = p
print('references added: [49]-[51]')

# ---------------------------------------------------------------- the closing note on the references
close = one(lambda t: 'the notes of the author\'s series ([2]–[12], [22], [23], [48])' in t, 'closing note')
for t in close.iter(qn('w:t')):
    if t.text and '[48])' in t.text:
        t.text = t.text.replace('[22], [23], [48])', '[22], [23], [48], [51])'); t.set(XML_SPACE, 'preserve')
        break
doc.save(OUT)
print('saved', OUT)
