"""CERTAIN-COAST: the complete state of the art, one Word document with every paper of the author's state-of-the-art
series (reviews I-IX), the stakeholder review (all thirty papers), the review of dynamic data assimilation for missing
dynamics, reviews X and XI, the state of the art of the proposal and the review of networks that are optimal today.
Each paper is set in the author's card format: a header table (citation, link, affiliation, topic), "Summary.",
"Link to the anchor paper and to seawater intrusion" with the section it belongs to, "INNOVATION" and the step
CERTAIN-COAST takes beyond it. Each section opens with the equations of the author's MATLAB code (certain-coast) that
carry the method of that section, in red. Native Word math (pandoc), clickable links.

usage: python build_complete_sota.py OUT.docx
inputs: series cards (complete_sota_cards.py), sota_data.py, netsota_data.py and the JSON files in
        SCRATCH/complete_sota (cards_assimilation.json, cards_X_XI.json) and SCRATCH/matlab_eqs/matlab_equations.json."""
import json
import os
import re
import sys
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', '..', 'ml_paradigms', 'word'))
import build_sota as BS  # noqa: E402
from build_sota import run, para, heading, link, shade  # noqa: E402
from build_decisions_drl import box, body, E_mrich  # noqa: E402

SCRATCH = os.environ.get('CC_SCRATCH', '/tmp/work/'
                                       'scratchpad')
NAVY, BLUE, GREY, GREEN, ORANGE, RED = '1F3864', '2E6DB4', '52606D', '1E8A5A', 'C55A11', 'C00000'
CODE = 'https://github.com/dulianzeqiraj/certain-coast'


def norm(t):
    return re.sub(r'[^a-z0-9]+', ' ', (t or '').lower()).strip()[:70]


def first_sentence(t):
    t = re.sub(r'\*\*[^*]+\*\*\s*', '', t or '').strip()
    m = re.match(r'(.+?[.!?])(\s|$)', t)
    return m.group(1) if m else t


def links_of(c):
    ls = c.get('links') or []
    out = []
    for x in ls:
        if isinstance(x, (list, tuple)) and len(x) >= 2:
            out.append((str(x[0]), str(x[1])))
    return out


# ------------------------------------------------------------------------------------------------ the sections
SECTIONS = [
    ('1', 'Dynamic data assimilation for missing dynamics',
     'How a known model is completed by a learned error term while the state is estimated from partial, noisy data: '
     'the approximation theory of the model error, the mean-field limit of ensemble Kalman methods, transport, '
     'particle and variational filters, robust filtering and the completion of computational graphs. This is the '
     'mathematical engine of the data assimilation of CERTAIN-COAST (WP2).', ['+recharge', '+model']),
    ('2', 'Inputs, dispersion and boundary conditions from rain, with guarantees',
     'What can be learned about the recharge, the dispersion and the boundaries that nobody measures from rain, heads '
     'and a few chloride profiles, and with which guarantee (reviews I–III).', ['+boundary']),
    ('3', 'When the simulator is wrong or drifts: anchors, horizons and the floor',
     'Guarantees that survive a wrong simulator, a drifting climate and a long forecast horizon, and the floor below '
     'which no valid band can go (reviews IV–VI).', ['+alarms']),
    ('4', 'Counterfactuals and the hidden causes of salinity',
     'What the salinity would have been under another recharge or pumping, and how hidden causes such as an unrecorded '
     'drought demand are kept out of the effect of pumping (reviews VII–IX).', []),
    ('5', 'The monitoring network: designed for the warnings, kept optimal in time',
     'Sensor placement that corrects its own interference, robust and certified design, and networks that must change '
     'as the coast changes (review X and the review of networks that are optimal today).', ['+network']),
    ('6', 'Warnings between samples',
     'Warnings for what happens between laboratory samples: neural jump ODEs, robust neural SDEs and certified bands for '
     'a crossing at any time in the season (review XI).', ['+betweensamples']),
    ('7', 'Stakeholder decisions when the source of the chloride is unknown',
     'All thirty papers of the stakeholder review: how water utilities, regulators and users decide when the chloride '
     'may come from the sea, deep brine, drought or return flow, and how the decision is kept safe for every source '
     'that the evidence cannot exclude.', []),
    ('8', 'Coastal hazards and certified warnings: the state of the art of the proposal',
     'The thirty-two key papers on subsidence and relative sea level, extreme sea levels and ports, liquefaction, '
     'continuous sensing, the mathematics of certified warning and causal structure, as in the proposal.', []),
]

FIELD_LABELS = [('inputs', 'Inputs'), ('dispersion', 'Dispersion'), ('bcs', 'Boundary conditions'),
                ('source', 'Source of the chloride'), ('demand', 'Demand'), ('stake', 'Stakeholders')]


def norm_series(c, review):
    link_parts = []
    for k, lab in FIELD_LABELS:
        if c.get(k):
            link_parts.append(f'**{lab}.** {c[k]}')
    return dict(title=c['title'], authors=c.get('authors', ''), year=str(c.get('year', '')), venue=c.get('venue', ''),
                links=links_of(c), evidence=c.get('evidence', ''), short=c.get('short', ''), review=review,
                inst=c.get('inst', ''), summary=c.get('does', ''), innovation=c.get('sota') or first_sentence(c.get('does')),
                link=' '.join(link_parts), gap=c.get('gap', ''), step=c.get('step', ''), extra=c.get('novel', ''),
                eqs=[])


def norm_json(c, review):
    eqs = [(c['eq'], 'the key equation of the paper:')] if c.get('eq') else []
    return dict(title=c.get('title', ''), authors=c.get('authors', ''), year=str(c.get('year', '')),
                venue=c.get('venue', ''), links=links_of(c), evidence=c.get('evidence', ''), short=c.get('short', ''),
                review=review, inst=c.get('inst', ''), summary=c.get('does', ''),
                innovation=c.get('sota') or first_sentence(c.get('does')), link=c.get('link', ''), gap=c.get('gap', ''),
                step=c.get('step', ''), extra='', eqs=eqs)


def norm_cite(it, review, kind):
    m = re.match(r'(.+?)\s\((\d{4})[a-z]?\)\.\s*(.+?)\.\s(.+)$', it['cite'])
    authors, year, title, venue = (m.group(1), m.group(2), m.group(3), m.group(4)) if m else ('', '', it['cite'], '')
    links = [(it['doi'].replace('https://', ''), it['doi'])]
    if it.get('free') and it.get('free') != it.get('doi'):
        links.append((it.get('free_label', 'free copy'), it['free']))
    if kind == 'net':
        return dict(title=title, authors=authors, year=year, venue=venue, links=links, evidence=it['inst'],
                    short='', review=review, inst=it['inst'], summary=it['done'],
                    innovation=it.get('theorem') or first_sentence(it['done']), link=it.get('gap', ''), gap='',
                    step=it.get('beyond', ''), extra='', eqs=list(it.get('math', [])))
    return dict(title=title, authors=authors, year=year, venue=venue, links=links, evidence=it['inst'], short='',
                review=review, inst=it['inst'], summary=it['done'], innovation=first_sentence(it['done']), link='',
                gap='', step=it.get('beyond', ''), extra='', eqs=[])


def gather():
    """Section -> list of normalised cards, in the order of the document."""
    sec = {s[0]: [] for s in SECTIONS}
    p = os.path.join(SCRATCH, 'complete_sota', 'cards_assimilation.json')
    if os.path.exists(p):
        for c in json.load(open(p, encoding='utf-8')):
            sec['1'].append(norm_json(c, 'Dynamic data assimilation for missing dynamics (20 papers)'))
    S = json.load(open(os.path.join(SCRATCH, 'complete_sota', 'series_cards.json'), encoding='utf-8'))
    where = {'I': '2', 'II': '2', 'III': '2', 'IV': '3', 'V': '3', 'VI': '3', 'VII': '4', 'VIII': '4', 'IX': '4',
             'S': '7'}
    for k in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'S']:
        lab = (f'Review {k}: ' if k != 'S' else 'Stakeholder review: ') + S[k]['title']
        for c in S[k]['cards']:
            sec[where[k]].append(norm_series(c, lab))
    p = os.path.join(SCRATCH, 'complete_sota', 'cards_X_XI.json')
    if os.path.exists(p):
        J = json.load(open(p, encoding='utf-8'))
        for c in J.get('X', []):
            sec['5'].append(norm_json(c, 'Review X: sensor placement, interference correction, robust certified design'))
        for c in J.get('XI', []):
            sec['6'].append(norm_json(c, 'Review XI: warnings between samples'))
    import netsota_data as ND
    for _, items in ND.GROUPS:
        for it in items:
            sec['5'].append(norm_cite(it, 'Networks that are optimal today and not tomorrow (20 papers)', 'net'))
    import sota_data as SD
    for _, items in SD.GROUPS:
        for it in items:
            sec['8'].append(norm_cite(it, 'State of the art of the proposal (32 papers)', 'sota'))
    # one full card per paper; a later occurrence becomes a cross-reference
    seen, n = {}, 0
    for k, _, _, _ in SECTIONS:
        for c in sec[k]:
            key = norm(c['title'])
            if key in seen:
                c['dup_of'] = seen[key]
            else:
                n += 1
                c['n'] = n
                seen[key] = (n, k)
    return sec


def matlab_items():
    p = os.path.join(SCRATCH, 'matlab_eqs', 'matlab_equations.json')
    if not os.path.exists(p):
        return []
    return json.load(open(p, encoding='utf-8')).get('items', [])


def kv_table(doc, rows, E):
    t = doc.add_table(rows=0, cols=2)
    t.autofit = False
    tblPr = t._tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for side in ('top', 'bottom', 'insideH'):
        e = OxmlElement(f'w:{side}')
        e.set(qn('w:val'), 'single')
        e.set(qn('w:sz'), '4')
        e.set(qn('w:color'), 'C9D3E0')
        b.append(e)
    tblPr.append(b)
    lay = OxmlElement('w:tblLayout')
    lay.set(qn('w:type'), 'fixed')
    tblPr.append(lay)
    for k, v in rows:
        c0, c1 = t.add_row().cells
        c0.width, c1.width = Cm(3.2), Cm(13.8)
        shade(c0, 'F3F6FA')
        q = c0.paragraphs[0]
        q.paragraph_format.space_after = Pt(1)
        run(q, k, bold=True, size=8.5, color=GREY)
        q = c1.paragraphs[0]
        q.paragraph_format.space_after = Pt(1)
        if isinstance(v, list):
            for j, (lab, url) in enumerate(v):
                if j:
                    run(q, '  ·  ', size=8.5, color=GREY)
                link(q, url, lab, 8.5)
        else:
            E_mrich(q, v, E, size=8.5)
    grid = t._tbl.tblGrid
    for gc, w in zip(grid.findall(qn('w:gridCol')), (3.2, 13.8)):
        gc.set(qn('w:w'), str(int(w * 567)))
    for row in t.rows:
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    para(doc, 2)


def labelled(doc, label, text, E, color, size=10):
    if not text:
        return
    q = para(doc, 3)
    q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run(q, label + ' ', bold=True, size=size, color=color)
    E_mrich(q, text, E, size=size)


def card(doc, c, sec_no, E, display_eq, num):
    if c.get('dup_of'):
        n0, s0 = c['dup_of']
        q = para(doc, 4, before=4)
        run(q, c['title'] + ' ', bold=True, size=10, color=NAVY)
        run(q, f'— see [{n0}] in Section {s0}; it also belongs here ({c["review"]}).', italic=True, size=9.5, color=GREY)
        return
    p = para(doc, 2, before=8)
    p.paragraph_format.keep_with_next = True
    run(p, f'[{c["n"]}]  ', bold=True, size=11, color=NAVY)
    run(p, c['title'], bold=True, size=11, color=NAVY)
    cite = ', '.join(x for x in [c['authors'], f'({c["year"]})' if c['year'] else '', c['venue']] if x)
    rows = [('Citation', cite), ('DOI / link', c['links'] or c.get('evidence', '')), ('Affiliation', c['evidence']),
            ('Topic', ' · '.join(x for x in [c.get('short', ''), c['review']] if x))]
    kv_table(doc, [(k, v) for k, v in rows if v], E)
    labelled(doc, 'Summary.', c['summary'], E, NAVY)
    for tex, what in c.get('eqs', []):
        q = para(doc, 0)
        q.paragraph_format.keep_with_next = True
        run(q, 'Mathematics: ', bold=True, size=10, color=BLUE)
        E_mrich(q, what, E, size=10)
        num[0] += 1
        display_eq(doc, E, tex, num[0])
    lk = ' '.join(x for x in [c['link'], (f'**What it leaves open.** {c["gap"]}' if c['gap'] else '')] if x)
    labelled(doc, f'Link to the anchor paper and to seawater intrusion. Belongs to Section {sec_no}.', lk, E, BLUE)
    q = para(doc, 3)
    q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run(q, 'INNOVATION  ', bold=True, size=10, color=ORANGE)
    E_mrich(q, c['innovation'], E, size=10)
    labelled(doc, 'Step in CERTAIN-COAST.', ' '.join(x for x in [c['step'], c['extra']] if x), E, GREEN)


def main(out):
    from build_gar_doc import Eqs, display_eq
    import omml
    import polish_parts as PP
    E = Eqs()
    BS._EQ = E
    sec = gather()
    M = matlab_items()
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0)
    s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']
    st.font.name = 'Arial'
    st.font.size = Pt(10.5)
    num, red = [0], []
    n_full = sum(1 for k in sec for c in sec[k] if not c.get('dup_of'))

    p = para(doc, 2, before=40)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'CERTAIN-COAST — The complete state of the art', bold=True, size=22, color=NAVY)
    p = para(doc, 6)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, f'{n_full} papers of 2020–2026 from the author\'s state-of-the-art series, each with its summary, its link '
           f'to the anchor and to seawater intrusion, its innovation and the step CERTAIN-COAST takes beyond it; the '
           f'equations of the author\'s MATLAB code in red', bold=True, size=12, color=NAVY)
    p = para(doc, 18)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Prof. Asoc. Dr. Dulian Zeqiraj · Faculty of Geology and Mining, Polytechnic University of Tirana · '
           'November 2026', italic=True, size=10, color=GREY)
    box(doc, 'How to read this document',
        'The anchor is CERTAIN-COAST itself: a coupled model of the coast whose warnings for seawater intrusion, '
        'liquefaction and extreme sea levels carry a stated miss rate, written as open-source MATLAB code '
        f'([{CODE.replace("https://", "")}]({CODE})). Each section opens with the equations of that code which carry '
        'the method of the section, in red, with the file they come from; then each paper follows in the same card: '
        'the header table, the summary, the link to the anchor and to seawater intrusion, the innovation of the paper '
        'and the step CERTAIN-COAST takes beyond it. A paper met in more than one review has one full card and a '
        'cross-reference where it appears again.', E)
    heading(doc, 'Contents', 14)
    for k, t, _, _ in SECTIONS:
        n_k = sum(1 for c in sec[k] if not c.get('dup_of'))
        q = para(doc, 2)
        run(q, f'{k}.  {t}', bold=True, size=10.5, color=NAVY)
        run(q, f'   ({n_k} papers)', size=10, color=GREY)

    for k, t, intro, pkgs in SECTIONS:
        h = heading(doc, f'{k}. {t}', 16, before=6)
        h.paragraph_format.page_break_before = True
        body(doc, intro, E, size=10.5)
        mine = [it for it in M if any(f'/{pk}/' in it.get('file', '') or it.get('file', '').startswith(pk + '/')
                                      for pk in pkgs)]
        neqs = [(it, e) for it in mine for e in it.get('equations', []) if e.get('status') == 'new']
        if neqs:
            heading(doc, f'{k}.0 Our equations in the CERTAIN-COAST MATLAB code', 12, color=RED, before=6)
            for it, e in neqs:
                q = para(doc, 0)
                q.paragraph_format.keep_with_next = True
                run(q, it.get('file', '') + ': ', bold=True, size=9.5, color=RED)
                E_mrich(q, e.get('what', ''), E, size=9.5)
                num[0] += 1
                red.append(num[0])
                display_eq(doc, E, e['latex'], num[0])
        reviews = []
        for c in sec[k]:
            if c['review'] not in reviews:
                reviews.append(c['review'])
        for r in reviews:
            heading(doc, r, 12, color=BLUE, before=10)
            for c in sec[k]:
                if c['review'] == r:
                    card(doc, c, k, E, display_eq, num)

    p = para(doc, 4, before=10)
    run(p, 'Verification note. Every card comes from the author\'s reviews, where each reference was checked against '
           'Crossref, arXiv, the proceedings or institutional repositories; the cards of the data assimilation review '
           'and of reviews X and XI were translated or extracted from those reviews and their references checked again '
           'in Crossref in November 2026. The equations in red were checked against the MATLAB code of the package. The '
           'document was assembled with the help of an AI assistant.', italic=True, size=9, color=GREY)

    BS._EQ = None
    work = tempfile.mkdtemp()
    draft = os.path.join(work, 'draft.docx')
    doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh)
    omml.main(draft, eq_json, out)
    PP.RED[98] = red
    d = Document(out)
    n_red, _ = PP.colour_equations(list(d.element.body), 98)
    d.core_properties.title = 'CERTAIN-COAST: the complete state of the art'
    d.core_properties.author = 'Dulian Zeqiraj'
    d.save(out)
    print('saved', out, '|', n_full, 'papers |', len(E.items), 'equations |', n_red, 'in red')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Complete_State_of_the_Art.docx')
