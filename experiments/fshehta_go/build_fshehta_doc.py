"""Builds the ninth state-of-the-art review (English, Word, OMML equations, clickable links): the Time Series
Deconfounder extracted, twenty papers, our analogues of its Figures 1 and 2, and FSHEHTA-GO.

usage: python build_fshehta_doc.py OUT.docx
Text: text_fshehta.py and cards_fshehta.py; figures: fshehta_figs.py; results: res/fshehta.json and
res/fshehta_case.npz. Needs pandoc (through ../ml_paradigms/word/omml.py)."""
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
sys.path.insert(2, os.path.join(HERE, '..', 'spiranca_go', 'certain_coast'))
sys.path.insert(3, os.path.join(HERE, '..', 'ml_paradigms', 'word'))
from build_sota import run, para, heading, table, shade, link  # noqa: E402
import omml  # noqa: E402
from build_gar_doc import (Eqs, borders, fixed_widths, numref, mrich, display_eq, rich_cell, cell_par,  # noqa: E402
                           CARD)
import fshehta_figs as MF  # noqa: E402
from cards_fshehta import CARDS  # noqa: E402
from text_fshehta import blocks, all_refs  # noqa: E402

FIGS = ('map', 'dag', 'arch', 'case', 'd1', 'checks')
CARD['Harvard'] = ('0B6E4C', 'E6F5EE')


def render_card(doc, c, E, numbers=None):
    dark, light = CARD[c['inst']]
    t = doc.add_table(rows=5, cols=1)
    borders(t, dark, 8); fixed_widths(t, [17.0])
    h = t.rows[0].cells[0]; shade(h, dark)
    p = cell_par(h, True)
    run(p, f"{c['id']}  ·  {c['inst']}  ·  {c['year']}", bold=True, size=9.5, color='FFFFFF')
    p = cell_par(h, False)
    mrich(p, c['title'], E, size=11.5, color='FFFFFF', bold=True, numbers=numbers)
    b = t.rows[1].cells[0]
    p = cell_par(b, True); run(p, c['authors'], size=10)
    p = cell_par(b, False); run(p, c['venue'], italic=True, size=10)
    p = cell_par(b, False); run(p, 'Links: ', bold=True, size=10)
    for k, (lab, url) in enumerate(c['links']):
        if k:
            run(p, '  ·  ', size=10)
        link(p, url, lab, size=10)
    p = cell_par(b, False)
    run(p, 'Affiliation and verification: ', bold=True, size=9.5, color='52606D')
    run(p, c['evidence'] + ' Status: ' + c.get('status', 'partly verified (landing pages reached through search results '
                                                         'only).'), italic=True, size=9.5, color='52606D')
    # what it does, the state of the art it sets and what it cannot yet do for us
    w = t.rows[2].cells[0]; shade(w, light)
    p = cell_par(w, True); run(p, 'What it does. ', bold=True, size=10.5, color=dark)
    mrich(p, c['does'], E, size=10.5, numbers=numbers)
    p = cell_par(w, False); run(p, 'State of the art it sets. ', bold=True, size=10.5, color=dark)
    mrich(p, c['sota'], E, size=10.5, numbers=numbers)
    p = cell_par(w, False); run(p, 'What it cannot yet do for us. ', bold=True, size=10.5, color=dark)
    mrich(p, c['gap'], E, size=10.5, numbers=numbers)
    # the three lessons
    le = t.rows[3].cells[0]
    for k, (lab, key) in enumerate((('Input parameters. ', 'inputs'), ('Dispersion coefficient. ', 'dispersion'),
                                    ('Boundary conditions from rain alone. ', 'bcs'))):
        p = cell_par(le, k == 0); run(p, lab, bold=True, size=10.5, color=dark)
        mrich(p, c[key], E, size=10.5, numbers=numbers)
    s = t.rows[4].cells[0]; shade(s, 'E6F4EA')
    p = cell_par(s, True); run(p, 'Innovation step for our problem. ', bold=True, size=10.5, color='1E6B35')
    mrich(p, c['step'], E, size=10.5, numbers=numbers)
    for i_ in (0, 1, 4):
        t.rows[i_]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    for r_ in t.rows[:2]:
        for pp in r_.cells[0].paragraphs:
            pp.paragraph_format.keep_with_next = True
    para(doc, 6)


def render_refs(doc):
    heading(doc, 'References', 14, before=12)
    groups = (('The article and its supplement (provided by the user)', lambda k: k.startswith('A')),
              ('The twenty papers of this review', lambda k: k[0] in 'OCHM' and len(k) <= 3),
              ('Cited from the article (as listed in its references)', lambda k: k.startswith('S')),
              ('Data and project documents', lambda k: k.startswith('D')))
    refs = all_refs()
    for title, pred in groups:
        if not any(pred(r_['key']) for r_ in refs):
            continue
        heading(doc, title, 11.5, color='2E6DB4', before=6)
        for r_ in refs:
            if pred(r_['key']):
                p = para(doc, 2, 0.5)
                run(p, f"[{r_.get('label', r_['key'])}] ", bold=True, size=9.5, color='3d4652')
                run(p, r_['text'] + ' ', size=9.5, color='3d4652')
                if r_['url']:
                    link(p, r_['url'], r_['url'], size=9.5)
    p = para(doc, 2, before=6)
    run(p, 'Verification note. The bibliographic data of the twenty cards come from search results that quote the '
           'publisher, arXiv, proceedings or repository pages; doi.org, arxiv.org, proceedings.mlr.press, '
           'proceedings.neurips.cc and most publisher hosts could not be opened directly in this environment. The '
           'article and its supplement were read from the PDFs provided; the references marked S are cited as the '
           'article lists them. Every number of Sections 1, 3, 4 and 6 is computed by the code in experiments/fshehta_go/.',
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
    with open(os.path.join(HERE, 'res', 'fshehta.json')) as fh:
        RJ = json.load(fh)
    BL = blocks(RJ)
    numbers, n_eq, n_fig, n_tab = number_blocks(BL)
    E = Eqs()
    work = tempfile.mkdtemp()
    MF.main(work, CARDS)
    figs = {k: os.path.join(work, f'fig_{k}.png') for k in FIGS}

    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    done_refs = False
    for bi, b in enumerate(BL):
        kind = b[0]
        if kind == 'refs':
            render_refs(doc); done_refs = True
            continue
        nxt = BL[bi + 1][0] if bi + 1 < len(BL) else None
        if kind == 'title':
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
            p = para(doc, 3, 0.5); run(p, '• ', bold=True); mrich(p, b[1], E, numbers=numbers)
        elif kind == 'bbox':
            t = doc.add_table(rows=1, cols=1); borders(t, '9DB8DC', 6); fixed_widths(t, [17.0])
            c = t.rows[0].cells[0]; shade(c, 'EEF4FB')
            for k, item in enumerate(b[1]):
                p = cell_par(c, k == 0); p.paragraph_format.space_after = Pt(4)
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
            t = table(doc, hdr, [[re.sub(r'\*\*|\$|==|\[([^\]]+)\]\([^)]+\)', lambda m: m.group(1) or '', c)
                                  for c in r_] for r_ in rows], b[3], size=b[4])
            for i_, r_ in enumerate(rows, start=1):
                for j_, c in enumerate(r_):
                    if '$' in c or '**' in c or '==' in c or '](' in c:
                        rich_cell(t.rows[i_].cells[j_], c, E, numbers, b[4])
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
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
            p = para(doc, 6); p.paragraph_format.keep_with_next = b[1].startswith('Table')
            mrich(p, b[1], E, size=10, numbers=numbers, italic=True)
        elif kind == 'card':
            render_card(doc, b[1], E, numbers)
        elif kind == 'pb':
            p = para(doc, 0); p.add_run().add_break(WD_BREAK.PAGE)
    if not done_refs:
        render_refs(doc)
    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh, ensure_ascii=False)
    omml.main(draft, eq_json, out)
    print('saved', out, '|', n_eq, 'numbered equations,', len(E.items) - n_eq, 'inline |', n_fig, 'figures |', n_tab,
          'tables')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'FSHEHTA-GO.docx')
