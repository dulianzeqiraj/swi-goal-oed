"""Builds the review "Where does the chloride come from?" (English, Word, OMML equations, clickable links): the origin
of chloride in a coastal aquifer as an ill-posed inverse problem, thirty papers, ZANAFILLA-GO and its numerical test.

usage: python build_zanafilla_doc.py OUT.docx
Text: text_zanafilla.py and cards_zanafilla.py; figures: zanafilla_figs.py; results: res/zanafilla.json,
res/zanafilla_examples.npz; references: res/refs_context.json.  Needs pandoc (through ../ml_paradigms/word/omml.py)."""
import json
import os
import re
import sys
import tempfile

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
GAR = os.path.join(HERE, '..', 'garancia_go')
sys.path.insert(0, HERE)
sys.path.insert(1, GAR)
sys.path.insert(2, os.path.join(HERE, '..', 'word_tools'))
sys.path.insert(3, os.path.join(HERE, '..', 'ml_paradigms', 'word'))
from build_sota import run, para, heading, table, shade, link  # noqa: E402
import omml  # noqa: E402
from build_gar_doc import Eqs, borders, fixed_widths, numref, mrich, display_eq, rich_cell, cell_par  # noqa: E402
import zanafilla_figs as KF  # noqa: E402
from text_zanafilla import blocks, all_refs  # noqa: E402

FIGS = ('map', 'scheme', 'aquifer', 'intervals', 'value', 'point', 'nn')
# card colours: darker steps of the figure hues (white text passes 4.5:1), and their tints
CARD = {'Caltech': ('A8441A', 'FCEEE7'), 'Oxford': ('1D5FAE', 'EAF1FB'), 'MIT': ('0B6E4C', 'E6F5EE'),
        'Harvard': ('4B3BB0', 'EEECFA'), 'Max Planck': ('835600', 'FBF3DF'), 'Princeton': ('9A2E6E', 'F9EAF2'),
        'Berkeley': ('0E6F87', 'E5F4F8')}
ROUTE_NAME = dict(tracers='tracers', mixing='unmixing', inverse='ill-posed inversion', ident='identification, design',
                  learn='learning')


def render_card(doc, c, E, numbers=None):
    dark, light = CARD[c['inst']]
    t = doc.add_table(rows=4, cols=1)
    borders(t, dark, 8); fixed_widths(t, [17.0])
    h = t.rows[0].cells[0]; shade(h, dark)
    p = cell_par(h, True)
    run(p, f"{c['id']}  ·  {c['inst']}  ·  {c['year']}  ·  route: " + ', '.join(ROUTE_NAME[r] for r in c['routes']),
        bold=True, size=9.5, color='FFFFFF')
    p = cell_par(h, False)
    mrich(p, c['title'], E, size=11.5, color='FFFFFF', bold=True, numbers=numbers)
    b = t.rows[1].cells[0]
    p = cell_par(b, True); run(p, c['authors'], size=10)
    p = cell_par(b, False); run(p, c['venue'], italic=True, size=10)
    p = cell_par(b, False); run(p, 'Link: ', bold=True, size=10)
    for k, (lab, url) in enumerate(c['links']):
        if k:
            run(p, '  ·  ', size=10)
        link(p, url, lab, size=10)
    p = cell_par(b, False)
    run(p, 'Affiliation and verification: ', bold=True, size=9.5, color='52606D')
    run(p, c['evidence'] + ' Status: ' + c['status'], italic=True, size=9.5, color='52606D')
    w = t.rows[2].cells[0]; shade(w, light)
    for k, (lab, key) in enumerate((('What it does. ', 'does'), ('How it bears on the origin of chloride. ', 'route'),
                                    ('What it leaves open for us. ', 'gap'))):
        p = cell_par(w, k == 0); run(p, lab, bold=True, size=10.5, color=dark)
        mrich(p, c[key], E, size=10.5, numbers=numbers)
    s = t.rows[3].cells[0]; shade(s, 'E6F4EA')
    p = cell_par(s, True); run(p, 'Innovation step for our problem. ', bold=True, size=10.5, color='1E6B35')
    mrich(p, c['step'], E, size=10.5, numbers=numbers)
    for i_ in (0, 1, 3):
        t.rows[i_]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    for r_ in t.rows[:2]:
        for pp in r_.cells[0].paragraphs:
            pp.paragraph_format.keep_with_next = True
    para(doc, 6)


def render_refs(doc):
    heading(doc, 'References', 14, before=12)
    groups = (('The thirty papers of this review', lambda k: k[0] in 'COMPXHB' and k[1:].isdigit()),
              ('Context: sources from other groups', lambda k: k.startswith('S')),
              ('Project documents and code', lambda k: k.startswith('D')))
    refs = all_refs()
    for title, pred in groups:
        if not any(pred(r_['key']) for r_ in refs):
            continue
        heading(doc, title, 11.5, color='2E6DB4', before=6)
        for r_ in refs:
            if pred(r_['key']):
                p = para(doc, 2, 0.5)
                run(p, f"[{r_['key']}] ", bold=True, size=9.5, color='3d4652')
                run(p, r_['text'] + ' ', size=9.5, color='3d4652')
                if r_.get('url'):
                    link(p, r_['url'], r_['url'], size=9.5)
    p = para(doc, 2, before=6)
    run(p, 'Verification note. The bibliographic data of every reference with a DOI are the Crossref record of that '
           'DOI; the affiliation evidence of each card is stated on the card. The cards rest on the abstracts: publisher '
           'pages could not be opened from the build environment, so no full text was read, and statements that go '
           'beyond an abstract are marked as such. Every number of Section 6 is computed by the code in '
           'experiments/zanafilla_go/; the signatures of the test are illustrative. Generative AI tools assisted with '
           'the literature search, the code and the drafting of this document; the author checked the statements, '
           'numbers and references and is responsible for them.',
        italic=True, size=9.5, color='52606D')


def number_blocks(BL):
    numbers, n_eq, n_fig, n_tab = {}, 0, 0, 0
    for b in BL:
        if b[0] == 'eq':
            n_eq += 1; numbers[b[1]] = str(n_eq)
        elif b[0] == 'img':
            n_fig += 1; numbers['#' + b[1]] = str(n_fig)
        elif b[0] == 'cap' and re.match(r'Table \{\{(\w+)\}\}', b[1]):
            n_tab += 1; numbers['#' + re.match(r'Table \{\{(\w+)\}\}', b[1]).group(1)] = str(n_tab)
    return numbers, n_eq, n_fig, n_tab


def main(out):
    with open(os.path.join(HERE, 'res', 'zanafilla.json')) as fh:
        RJ = json.load(fh)
    BL, s, cards = blocks(RJ)
    numbers, n_eq, n_fig, n_tab = number_blocks(BL)

    E = Eqs()
    work = tempfile.mkdtemp()
    KF.main(work, cards)
    figs = {k: os.path.join(work, f'fig_{k}.png') for k in FIGS}

    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.0); sec.top_margin = sec.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    for bi, b in enumerate(BL):
        kind = b[0]
        nxt = BL[bi + 1][0] if bi + 1 < len(BL) else None
        if kind == 'refs':
            render_refs(doc)
        elif kind == 'title':
            p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run(p, b[1], bold=True, size=18, color='1F3864')
        elif kind == 'subtitle':
            p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run(p, b[1], size=11.5, color='1F3864')
        elif kind == 'byline':
            p = para(doc, 12); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run(p, b[1], italic=True, size=10, color='52606D')
        elif kind == 'h':
            heading(doc, b[1], 14, before=12)
        elif kind == 'h2':
            heading(doc, b[1], 12, color='2E6DB4', before=6)
        elif kind == 'p':
            p = para(doc, 5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; mrich(p, b[1], E, numbers=numbers)
            if nxt in ('eq', 'eqn'):
                p.paragraph_format.keep_with_next = True
        elif kind == 'b':
            p = para(doc, 3, 0.5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, '• ', bold=True); mrich(p, b[1], E, numbers=numbers)
        elif kind == 'bbox':
            t = doc.add_table(rows=1, cols=1); borders(t, '9DB8DC', 6); fixed_widths(t, [17.0])
            c = t.rows[0].cells[0]; shade(c, 'EEF4FB')
            for k, item in enumerate(b[1]):
                p = cell_par(c, k == 0); p.paragraph_format.space_after = Pt(4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                run(p, '• ', bold=True, size=10.5, color='1F3864'); mrich(p, item, E, size=10.5, numbers=numbers)
            para(doc, 6)
        elif kind == 'box':
            t = doc.add_table(rows=1, cols=1); borders(t, '7FB58E', 6); fixed_widths(t, [17.0])
            c = t.rows[0].cells[0]; shade(c, 'E6F4EA')
            for k, item in enumerate(b[1] if isinstance(b[1], (list, tuple)) else [b[1]]):
                p = cell_par(c, k == 0); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                mrich(p, item, E, size=10.5, numbers=numbers)
            para(doc, 6)
        elif kind == 'prop':
            t = doc.add_table(rows=1, cols=1); borders(t, 'B9C6D6', 6); fixed_widths(t, [17.0])
            c = t.rows[0].cells[0]; shade(c, 'F2F5F9')
            p = cell_par(c, True); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, b[1] + ' ', bold=True, size=11, color='1F3864'); mrich(p, b[2], E, size=11, numbers=numbers)
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            para(doc, 3)
        elif kind == 'proof':
            p = para(doc, 6, 0.4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, 'Proof. ', italic=True, bold=True, size=10.5); mrich(p, b[1], E, size=10.5, numbers=numbers)
            run(p, '  □', size=10.5)
        elif kind == 'eq':
            display_eq(doc, E, b[2], numbers[b[1]])
        elif kind == 'eqn':
            display_eq(doc, E, b[1], None)
        elif kind == 'table':
            rows = [[numref(c, numbers) for c in r_] for r_ in b[2]]
            hdr = [numref(c, numbers) for c in b[1]]
            t = table(doc, hdr, [[re.sub(r'\*\*|\*|\$|==|\[([^\]]+)\]\([^)]+\)', lambda m: m.group(1) or '', c)
                                  for c in r_] for r_ in rows], b[3], size=b[4])
            for i_, r_ in enumerate(rows, start=1):
                for j_, c in enumerate(r_):
                    if '$' in c or '*' in c or '==' in c or '](' in c:
                        rich_cell(t.rows[i_].cells[j_], c, E, numbers, b[4])
                if r_[0].startswith('**') and not any(r_[1:]):          # a block heading inside the table
                    m_ = t.rows[i_].cells[0].merge(t.rows[i_].cells[-1])
                    for pp in list(m_.paragraphs)[1:]:
                        pp._p.getparent().remove(pp._p)
                    shade(m_, 'EEF4FB')
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            for r_ in t.rows:
                r_._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            if len(b) < 6 or b[5]:                      # keep a short table on one page
                for r_ in t.rows[:-1]:
                    for c_ in r_.cells:
                        for pp in c_.paragraphs:
                            pp.paragraph_format.keep_with_next = True
            para(doc, 6)
        elif kind == 'img':
            p = para(doc, 2, before=4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(figs[b[1]], width=Cm(b[2]))
        elif kind == 'cap':
            p = para(doc, 6); p.paragraph_format.keep_with_next = b[1].startswith('Table') and False
            mrich(p, b[1], E, size=10, numbers=numbers, italic=True)
        elif kind == 'card':
            render_card(doc, b[1], E, numbers)
        elif kind == 'pb':
            p = para(doc, 0); p.add_run().add_break(WD_BREAK.PAGE)
    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh, ensure_ascii=False)
    omml.main(draft, eq_json, out)
    print('saved', out, '|', n_eq, 'numbered equations,', len(E.items) - n_eq, 'inline |', n_fig, 'figures |', n_tab,
          'tables |', len(cards), 'cards')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'ZANAFILLA-GO.docx')
