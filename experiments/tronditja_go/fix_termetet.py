"""Revision of the TERMETET note (Albanian) after TRONDITJA-GO, editing the author's Word file: existing text and
equations are kept unless a change below replaces them; new equations are written as OMML through pandoc.
usage: python -I fix_termetet.py IN.docx OUT.docx

Changes (9 November 2026): a revision note; 2.2 the step in a layer under the free surface (2.2a) and the mechanism;
2.4 the constant; 3.3 the CSUB package; (4.1)-(4.2) the step enters the pore pressure, with the drainage share (4.2a);
4.5 the full derivative (4.10) and the re-normalisation bias; 5.6 settlement; 6 the earthquake step of the sequence;
7 what the implementation adds; 8 a row for the shear modulus; five references."""
import copy
import os
import re
import sys
import tempfile

from docx import Document
from docx.oxml.ns import qn
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ml_paradigms', 'word'))
import omml  # noqa: E402

IN, OUT = sys.argv[1], sys.argv[2]
doc = Document(IN)
body = doc.element.body
P = list(body.iterchildren())
MATH = {qn('m:oMath'), qn('m:oMathPara')}
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'


def text_of(el):
    return ''.join(t.text or '' for t in el.iter(qn('w:t')) if not any(a.tag in MATH for a in t.iterancestors()))


def expect(i, start):
    assert text_of(P[i]).startswith(start), (i, text_of(P[i])[:80])


# the anchors this script relies on (the note of 31 October 2026)
expect(1, 'Shënim pune')
expect(3, 'Shenjat.')
expect(25, 'Niveli ngrihet aty ku toka ngjeshet')
expect(29, '2.4 Energjia sizmike')
expect(46, '3.3 Kompaktimi elastik')
expect(53, 'prandaj ulja e tokës vazhdon')
expect(61, '4.1 Niveli i ujit')
expect(64, 'Termi i fundit vlen')
expect(65, '4.2 Stresi i shkaktuar')
expect(82, 'Relacioni u kontrollua me diferenca')
expect(97, '5.6 Lëngëzimi dhe përmbytja.')
expect(101, 'Ngjarja tërmet')
expect(106, 'Çdo bllok më sipër')
expect(123, 'Hsieh')
expect(130, 'Mavroulis')
expect(137, 'Wang, C.-Y. (2007)')
expect(141, 'Werner')
expect(142, 'Zeqiraj')
assert P[63].find(qn('m:oMathPara')) is not None and P[66].find(qn('m:oMathPara')) is not None
assert P[108].tag == qn('w:tbl')

# ------------------------------------------------------------------------------------------------ new text
REV = (r'**Rishikimi i 9 nëntorit 2026.** Pasi hapat 1–3 të zbatimit u shkruan në kod dhe u provuan numerikisht '
       r'(TRONDITJA-GO, experiments/tronditja_go), u korrigjuan ose u shtuan: 2.2 (hapi në një shtresë nën sipërfaqen e '
       r'lirë dhe mekanizmi), 2.4 (konstantja), 3.3 (paketa CSUB), 4.1–4.2 (hapi hyn te presioni i porit, me pjesën që '
       r'mbetet pas drenimit), 4.5 (derivati i plotë i FS), 5.6 (ulja nga lëngëzimi), 6 (ngjarja tërmet), 7 (çfarë '
       r'shton zbatimi), 8 (moduli i prerjes) dhe referencat. Paragrafët e rinj fillojnë me një titull të shkurtër me '
       r'shkronja të trasha.')
S22A = (r'**Shtresa nën sipërfaqen e lirë.** Ekuacioni (2.2), me $\Delta\varepsilon_{v}$ të gjysmëhapësirës nga (2.1), '
        r'vlen për një akuifer po aq të fortë sa korja. Sedimentet e fushës bregdetare janë shumë më të buta dhe formojnë '
        r'një shtresë të hollë krahasuar me fushën e deformimit, që ndryshon në kilometra. Shtresa merr deformimin '
        r'horizontal të kores poshtë saj, që në sipërfaqe e jep zgjidhja e Okada (1985), ndërsa sipërfaqja e saj është e '
        r'lirë, $\sigma_{zz} = 0$. Nga (1.1)–(1.2), me $\zeta = 0$ dhe $\sigma_{zz} = 0$, nxjerrim:')
EQ22A = (r'\Delta p_{0} = - \kappa\,\Delta\varepsilon_{a},\quad\quad\Delta\varepsilon_{a} = \Delta\varepsilon_{xx} + '
         r'\Delta\varepsilon_{yy},\quad\quad\kappa = \frac{2GB}{3}\,\frac{1 + \nu_{u}}{1 - \nu_{u}}\quad\quad(2.2a)')
S22B = (r'me $G$, $B$ dhe $\nu_{u}$ të shtresës. Kjo është e njëjta me $-BK_{u}\Delta\varepsilon_{v}$, por me deformimin '
        r'vëllimor të shtresës, $\Delta\varepsilon_{v} = \Delta\varepsilon_{a}(1 - 2\nu_{u})/(1 - \nu_{u})$, jo me atë të '
        r'gjysmëhapësirës. Një shtresë e butë dhe e ngopur ($\nu_{u} \to 1/2$) deformohet pothuajse pa ndryshuar vëllim, '
        r'dhe $\kappa \to 2GB$: hapi varet nga moduli i prerjes së shtresës, jo nga ngurtësia e ujit në pore. Me katër '
        r'modelet e burimit, në rërën e butë sipërfaqësore ($G \approx 50$ MPa) niveli bie 7–12 cm mbi krahun e varur '
        r'dhe ngrihet 3–4 cm në zonat e ngjeshura anash tij; në një akuifer të mbyllur më të fortë ($G \approx 0.5$ GPa) '
        r'bie 0.6–1.0 m dhe ngrihet 0.2–0.3 m. Forma (2.2) me $\Delta\varepsilon_{v}$ të gjysmëhapësirës dhe '
        r'$BK_{u} = 5$ GPa jep rreth 35 herë vlerën e rërës së butë. Barazia (2.2a) u kontrollua numerikisht kundrejt '
        r'(1.1)–(1.2) deri në $10^{-16}$. Vlerat e $G$ janë supozime derisa të maten (seksioni 8).')
S22C = (r'**Mekanizmi.** Wang dhe Chia (2008) i lidhin ndryshimet e menjëhershme të nivelit në zonën e afërt me '
        r'ndryshimin vëllimor pa drenim, duke përdorur edhe të dhëna laboratorike për sedimente të ngopura nën ngarkim '
        r'ciklik; ndryshimet më graduale dhe të qëndrueshme në zonën e ndërmjetme i lidhin me rritjen e përshkueshmërisë. '
        r'Ndryshimi vëllimor mund të vijë nga deformimi statik (2.2a) ose nga vetë lëkundja. Pjesa ciklike është tashmë '
        r'brenda krahasimit CSR–CRR (4.3)–(4.8); prandaj te presioni i porit në (4.2) hyn vetëm hapi statik, që efekti të '
        r'mos numërohet dy herë. Ngritjet prej metrash në rërë të butë nuk mund të vijnë nga deformimi statik; ato '
        r'tregojnë mekanizmin ciklik.')
S24 = (r'**Kontrolli i konstantes.** Nga $e = 3E/(4\pi r^{3})$ (ek. 6.9 e librit) dhe relacioni i Båth-it '
       r'$\log_{10}E = 5.24 + 1.44M$, me $r$ në km, konstantja del $-4.38$ dhe jo $-4.62$; ndryshimi është 0.24 në '
       r'$\log_{10}e$. Për $M = 6.4$ kufiri $e = 0.1$ J/m³ bie në $r \approx 88$ km me $-4.38$ dhe në $r \approx 73$ km '
       r'me $-4.62$. Sipas abstraktit të tyre, Wang dhe Chia (2008) e paraqesin relacionin si të ri, prandaj konstantja e '
       r'shtypur duhet lexuar atje para se (2.4) të përdoret me numra. Për bregun Durrës–Fushë Kuqe të dy rrezet janë më '
       r'të mëdha se largësia nga burimi i vitit 2019 (disa dhjetëra kilometra), prandaj asnjë vendim atje nuk varet nga '
       r'ky ndryshim.')
S33 = (r'**Zbatimi në MODFLOW 6.** Ekuacionet (3.3)–(3.6), me kujtesën e stresit të parakonsolidimit dhe me vonesën në '
       r'shtresat e trasha argjilore, i zbaton paketa CSUB e MODFLOW 6 (Hughes et al., 2022), që zëvendëson SUB-WT. Ajo '
       r'është zgjedhja për modelin e projektit.')
EQ41 = r'h_{wt}(\mathbf{x},t_{eq}^{+}) = h_{wt}(\mathbf{x},t_{eq}^{-})\quad\quad(4.1)'
S41 = (r'**Korrigjim.** Niveli i ujit, ku $u = 0$, nuk lëviz gjatë sekondave të lëkundjes, prandaj hapi $\Delta h_{0}$ '
       r'hiqet nga (4.1). Hapi pa drenim hyn te presioni i porit në thellësi, në (4.2), me pjesën $f$ që mbetet në fund '
       r'të lëkundjes (4.2a). Në tërmetin e Chi-Chi, vendet e lëngëzuara përkonin me zonat ku tërmeti e ngriti nivelin e '
       r'ujit në akuiferin e sipërm mbi 2 m (Wang dhe Manga, 2021, kap. 11); sipas (2.2a), ngritje të tilla në rërë të '
       r'butë vijnë nga vetë lëkundja dhe jo nga deformimi statik.')
EQ42 = (r"\sigma_{v}(z) = \int_{0}^{z}\gamma_{t}\, dz^{'},\quad\quad u(z) = \gamma_{w}\left( z - z_{w} \right)_{+} + "
        r"f(z)\,\Delta p_{0}(z),\quad\quad\sigma_{v}^{'} = \sigma_{v} - u\quad\quad(4.2)")
S42A = (r'ku $\Delta p_{0}$ jepet nga (2.2a) me vetitë e shtresës dhe $f$ është pjesa e hapit që mbetet pas lëkundjes. '
        r'Për difuzion një-dimensional nga niveli i ujit, me $L$ thellësinë nën nivelin, $D$ difuzivitetin hidraulik dhe '
        r'$t_{s}$ kohëzgjatjen e lëkundjes, për rërë të lidhur me nivelin vetëm përmes rëre:')
EQ42A = (r'f(L) = \mathrm{erf}\left( \frac{L}{2\sqrt{D\, t_{s}}} \right)\ \text{për rërë të lidhur me nivelin},'
         r'\quad\quad f = 1\ \text{për rërë nën argjilë}\quad\quad(4.2a)')
S42B = (r'Me $D = 1$ m²/s dhe $t_{s} = 15$ s mbetet 7% e hapit në 0.5 m, 28% në 2 m dhe 64% në 5 m: rërat e cekëta, që '
        r'mbajnë pjesën më të madhe të LPI-së, e humbin hapin brenda sekondave, ndërsa rëra nën argjilë e mban.')
S45A = (r'**Derivati i plotë.** $q_{c1Ncs}$ është tregues dendësie, i normalizuar me stresin efektiv në kohën e CPT-së, '
        r'dhe nuk ndryshon kur niveli i ujit lëviz më vonë. Niveli i ditës hyn vetëm përmes CSR dhe $K_{\sigma}$. Nga '
        r'(4.3), (4.7) dhe (4.9) nxjerrim:')
EQ410 = (r"\frac{\partial\ln FS}{\partial z_{w}} = \frac{\gamma_{w}}{\sigma_{v}^{'}}\left( 1 - \frac{C_{\sigma}}"
         r"{K_{\sigma}} \right)\ \text{kur}\ K_{\sigma} < 1.1,\quad\quad\frac{\partial\ln FS}{\partial z_{w}} = "
         r"\frac{\gamma_{w}}{\sigma_{v}^{'}}\ \text{kur}\ K_{\sigma} = 1.1\quad\quad(4.10)")
S45B = (r'Relacioni (4.10) u kontrollua me diferenca të fundme (gabimi relativ $3\times10^{-10}$). Rinormalizimi i '
        r'$q_{c1Ncs}$ me stresin e ditës (përmes $C_{N}$) përzien gjendjen e rërës me gjendjen e ujit: në profilin shembull '
        r'të TRONDITJA-GO e nënvlerëson pjerrësinë e LPI-së ndaj nivelit me 33% (4.1 në vend të 6.0 për metër). ')
S56 = (r'Ulja nga lëngëzimi për tokë të sheshtë llogaritet si integrali mbi thellësi i deformimit vëllimor pas '
       r'lëkundjes, $\Delta z_{s} = -\int_{0}^{z_{\max}}\varepsilon_{v}\left( FS, q_{c1Ncs} \right) dz$, ku '
       r'$\varepsilon_{v}$ jepet nga FS dhe $q_{c1Ncs}$ sipas Zhang et al. (2002); koeficientët merren nga ai artikull '
       r'dhe nuk përsëriten këtu. Ky hap nuk është zbatuar ende.')
S6 = (r'**Ngjarja tërmet** në $t_{eq}$: (2.1) jep $\Delta\varepsilon_{a}$ dhe $U_{z}^{ko}$; (2.2a) jep $\Delta p_{0}$ në '
      r'secilën shtresë; (2.5) kërcimin e $k$; (4.2)–(4.8), me presionin e porit (4.2) dhe pjesën $f$ (4.2a), japin FS '
      r'dhe LPI; pastaj relaksimi (2.3) dhe rikthimi i $k$.')
S7 = (r'**Çfarë shton zbatimi (TRONDITJA-GO, nëntor 2026).** (i) Dritarja e përbashkët e sigurisë: lëngëzimi kërkon '
      r'nivel të thellë, ndërhyrja e kripur kërkon ngarkesë të lartë të ujit të ëmbël, dhe të dyja veprojnë mbi të '
      r'njëjtën ngarkesë të menaxhuar, $\eta + m_{int} \le h \le z_{s} - z^{*}(a)$, ku $z^{*}(a)$ është thellësia e '
      r'nivelit që mban LPI ≤ 5 për nxitimin $a$ dhe $m_{int} = 20/40$ m e mban kufirin e kripur 20 m thellë (3.7). '
      r'Dritarja mbyllet për gjithë vitin te $\eta_{close}(a) = z_{s} - z^{*}(a) - m_{int} - A$, me $A$ lëkundjen '
      r'sezonale. Në portin sintetik ajo mbyllet në 0.29 m ngritje relative të detit për 0.20 g dhe është e mbyllur qysh '
      r'tani për 0.22 g. (ii) Buletini ditor «nëse tërmeti do të ndodhte sot»: probabiliteti që LPI > 5, nga niveli i '
      r'ujit i asaj dite; në portin sintetik lëviz nga 0.16 (fund korriku) në 0.26 (fillim shkurti). (iii) Tërmeti si '
      r'provë pompimi falas: relaksimi i hapit në akuiferin e mbyllur e ngushton intervalin e kohës së rrjedhjes 5.8 '
      r'herë krahasuar me një vit stinësh. (iv) Koeficienti (2.2a), që tregon cili akuifer e ndien hapin. Në burimet e '
      r'lexuara nuk e gjetëm dritaren e përbashkët, nivelin e detit ku ajo mbyllet, as buletinin ditor.')
ROW8 = [r'$G$ i shtresave', '(2.2a)', r'Shpejtësia e valëve tërthore, $G = \rho V_{s}^{2}$ (CPT sizmike ose valë '
                                      r'sipërfaqësore)']
REFS = {  # anchor paragraph -> new reference inserted after it: (plain, italic, plain)
    123: ('Hughes, J. D., Leake, S. A., Galloway, D. L., White, J. T. (2022). Documentation for the Skeletal Storage, '
          'Compaction, and Subsidence (CSUB) Package of MODFLOW 6. ', 'Techniques and Methods',
          ' 6-A62, U.S. Geological Survey. doi:10.3133/tm6A62.'),
    130: ('Okada, Y. (1985). Surface deformation due to shear and tensile faults in a half-space. ',
          'Bulletin of the Seismological Society of America', ' 75, 1135–1154. doi:10.1785/BSSA0750041135.'),
    137: ('Wang, C.-Y., Chia, Y. (2008). Mechanism of water level changes during earthquakes: Near field versus '
          'intermediate field. ', 'Geophysical Research Letters', ' 35(12). doi:10.1029/2008GL034227.'),
    142: [('Zeqiraj, D. (2026). TRONDITJA-GO: the earthquake, the aquifer and liquefaction, implemented. Raport zbatimi '
           'me kontrolle numerike, nëntor 2026; docs/research_notes/TRONDITJA-GO_Earthquake_Aquifer_Liquefaction_'
           'Implementation.docx në këtë repozitor.', '', ''),
          ('Zhang, G., Robertson, P. K., Brachman, R. W. I. (2002). Estimating liquefaction-induced ground settlements '
           'from CPT for level ground. ', 'Canadian Geotechnical Journal', ' 39, 1168–1180. doi:10.1139/t02-047.')],
}

# ------------------------------------------------------------------------------------------------ OMML for all math
TOKEN = re.compile(r'(\*\*.+?\*\*|\$[^$]+\$)')


def tokens(s):
    out = []
    for part in TOKEN.split(s):
        if not part:
            continue
        if part.startswith('**'):
            out.append(('b', part[2:-2]))
        elif part.startswith('$'):
            out.append(('m', part[1:-1]))
        else:
            out.append(('t', part))
    return out


RICH = [REV, S22A, S22B, S22C, S24, S33, S41, S42A, S42B, S45A, S45B, S56, S6, S7] + ROW8
DISPLAY = [EQ22A, EQ41, EQ42, EQ42A, EQ410]
eqs, key = [], {}
for s in RICH:
    for kind, v in tokens(s):
        if kind == 'm' and ('i', v) not in key:
            key[('i', v)] = str(len(eqs)); eqs.append(dict(id=key[('i', v)], tex=v, display=False))
for d in DISPLAY:
    key[('d', d)] = str(len(eqs)); eqs.append(dict(id=key[('d', d)], tex=d, display=True))
with tempfile.TemporaryDirectory() as work:
    FR = omml.to_omml(eqs, work)


def frag(kind, tex):
    s = FR[key[(kind, tex)]][1]
    return etree.fromstring(f'<x xmlns:w="{omml.W}" xmlns:m="{omml.M}">{s}</x>')[0]


def add_rich(p, s):
    for kind, v in tokens(s):
        if kind == 'm':
            p.append(frag('i', v))
            continue
        r = etree.SubElement(p, qn('w:r'))
        if kind == 'b':
            rpr = etree.SubElement(r, qn('w:rPr'))
            etree.SubElement(rpr, qn('w:b')); etree.SubElement(rpr, qn('w:bCs'))
        t = etree.SubElement(r, qn('w:t')); t.text = v; t.set(XMLSPACE, 'preserve')


def new_p(style, s=None):
    p = etree.Element(qn('w:p'))
    ppr = etree.SubElement(p, qn('w:pPr'))
    etree.SubElement(ppr, qn('w:pStyle')).set(qn('w:val'), style)
    if s:
        add_rich(p, s)
    return p


def eq_p(tex, style='BodyText'):
    p = new_p(style)
    p.append(frag('d', tex))
    return p


def after(anchor, *new):
    for el in reversed(new):
        anchor.addnext(el)


def clear(p):
    for c in list(p):
        if c.tag != qn('w:pPr'):
            p.remove(c)


def replace_eq(p, tex):
    for c in list(p):
        if c.tag == qn('m:oMathPara'):
            p.remove(c)
    p.append(frag('d', tex))


def set_run_text(p, old, new):
    for t in p.iter(qn('w:t')):
        if t.text and old in t.text:
            t.text = t.text.replace(old, new); t.set(XMLSPACE, 'preserve')
            return
    raise SystemExit(f'not found: {old[:60]}')


# ------------------------------------------------------------------------------------------------ the edits
r = etree.SubElement(P[1], qn('w:r')); t = etree.SubElement(r, qn('w:t'))
t.text = ' Rishikuar më 9 nëntor 2026.'; t.set(XMLSPACE, 'preserve')
after(P[3], new_p('BodyText', REV))
after(P[25], new_p('BodyText', S22A), eq_p(EQ22A), new_p('FirstParagraph', S22B), new_p('BodyText', S22C))
# 2.4: the open point becomes the check
p31 = P[31]
kids = list(p31)
start = next(i for i, c in enumerate(kids) if c.tag == qn('w:r') and 'Pikë për t' in text_of(c))
for c in kids[start:]:
    p31.remove(c)
add_rich(p31, S24)
after(P[53], new_p('BodyText', S33))
replace_eq(P[63], EQ41)
clear(P[64]); add_rich(P[64], S41)
replace_eq(P[66], EQ42)
after(P[66], new_p('FirstParagraph', S42A), eq_p(EQ42A), new_p('FirstParagraph', S42B))
# 4.5: split the paragraph at the sentence on the full derivative
p82 = P[82]
kids = list(p82)
i0 = next(i for i, c in enumerate(kids) if c.tag == qn('w:r') and 'Derivati i plotë i FS' in text_of(c))
i1 = next(i for i, c in enumerate(kids) if c.tag == qn('w:r') and 'Pompimi e thellon' in text_of(c))
t0 = kids[i0].find(qn('w:t')); t0.text = t0.text[:t0.text.index('Derivati i plotë i FS')].rstrip() + ''
for c in kids[i0 + 1:i1]:
    p82.remove(c)
t1 = kids[i1].find(qn('w:t')); t1.text = t1.text[t1.text.index('Pompimi e thellon'):]
tail = kids[i1:]
for c in tail:
    p82.remove(c)
pC = new_p('FirstParagraph', S45B)
for c in tail:
    pC.append(c)
set_run_text(pC, 'rimbushja, ngritja e detit (Befus et al., 2020; Grant et al., 2021) dhe hapi koseizmik (4.1) e ngrenë.',
             'rimbushja dhe ngritja e detit (Befus et al., 2020; Grant et al., 2021) e ngrenë, po ashtu hapi koseizmik '
             '(4.2) aty ku toka ngjeshet.')
after(p82, new_p('FirstParagraph', S45A), eq_p(EQ410), pC)
# 5.6
p97 = P[97]
last = [c for c in p97 if c.tag == qn('w:r')][-1]
assert 'Modeli i uljes nga lëngëzimi nuk jepet këtu.' in text_of(last)
p97.remove(last)
add_rich(p97, S56)
# 6: the earthquake step of the sequence (a list item: its numbering is kept in pPr)
clear(P[101]); add_rich(P[101], S6)
# 7
after(P[106], new_p('BodyText', S7))
# 8: a row for the shear modulus of the layers, after the row of B, K_u, nu_u, gamma
rows = P[108].findall(qn('w:tr'))
new_row = copy.deepcopy(rows[1])
for tc, s in zip(new_row.findall(qn('w:tc')), ROW8):
    p = tc.find(qn('w:p'))
    clear(p); add_rich(p, s)
rows[1].addnext(new_row)
# references
tmpl = P[124]


def ref_p(plain, ital, rest):
    p = copy.deepcopy(tmpl)
    clear(p)
    for txt, it in ((plain, False), (ital, True), (rest, False)):
        if not txt:
            continue
        r = etree.SubElement(p, qn('w:r'))
        if it:
            rpr = etree.SubElement(r, qn('w:rPr'))
            etree.SubElement(rpr, qn('w:i')); etree.SubElement(rpr, qn('w:iCs'))
        t = etree.SubElement(r, qn('w:t')); t.text = txt; t.set(XMLSPACE, 'preserve')
    return p


for i, spec in REFS.items():
    specs = spec if isinstance(spec, list) else [spec]
    after(P[i], *[ref_p(*s) for s in specs])

doc.save(OUT)
print('saved', OUT, '|', len(eqs), 'new equations (', len(DISPLAY), 'display )')
