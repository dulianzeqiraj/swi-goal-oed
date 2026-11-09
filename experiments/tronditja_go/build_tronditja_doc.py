"""Builds the TRONDITJA-GO implementation report (English, Word, OMML equations, clickable links): the earthquake,
the aquifer and liquefaction as tested code, with the joint safe window and the daily bulletin.

usage: python build_tronditja_doc.py OUT.docx
Text: text_tronditja.py; figures: tronditja_figs.py; results: res/tronditja.json, res/tronditja_series.npz and
res/okada_checks.json. Needs pandoc (through ../ml_paradigms/word/omml.py)."""
import json
import os
import re
import sys
import tempfile

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', 'spiranca_go', 'certain_coast'))
sys.path.insert(3, os.path.join(HERE, '..', 'ml_paradigms', 'word'))
from build_sota import run, para, heading, table, shade, link  # noqa: E402
import omml  # noqa: E402
from build_gar_doc import (Eqs, borders, no_borders, fixed_widths, numref, mrich, display_eq, rich_cell,  # noqa: E402
                           cell_par)
import tronditja_figs as PF  # noqa: E402
from text_tronditja import blocks, all_refs  # noqa: E402

FIGS = ('chain', 'e1', 'e2', 'e3', 'e4', 'e5')


def cell_eq(cell, E, tex, number):
    """A numbered display equation inside a table cell (a borderless two-column table, as display_eq)."""
    t = cell.add_table(rows=1, cols=2)
    no_borders(t); fixed_widths(t, [14.9, 1.4])
    c0, c1 = t.rows[0].cells
    for c in (c0, c1):
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    lines = tex if isinstance(tex, (list, tuple)) else [tex]
    for k, line in enumerate(lines):
        p = c0.paragraphs[0] if k == 0 else c0.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2 if k == 0 else 0)
        p.paragraph_format.space_after = Pt(2 if k == len(lines) - 1 else 1)
        run(p, E.add(line, True))
    q = c1.paragraphs[0]; q.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run(q, f'({number})', size=11)
    tail = cell.paragraphs[-1]                     # Word needs a paragraph after a table in a cell
    tail.paragraph_format.space_before = Pt(0); tail.paragraph_format.space_after = Pt(0)
    return tail


def render_prop(doc, b, E, numbers):
    t = doc.add_table(rows=1, cols=1); borders(t, 'B9C6D6', 6); fixed_widths(t, [17.0])
    c = t.rows[0].cells[0]; shade(c, 'F2F5F9')
    parts = b[2] if isinstance(b[2], list) else [b[2]]
    spare = None
    for k, part in enumerate(parts):
        if isinstance(part, tuple) and part[0] == 'eq':
            spare = cell_eq(c, E, part[2], numbers[part[1]])
            continue
        p = spare if spare is not None else cell_par(c, k == 0)
        spare = None
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(2); p.paragraph_format.space_after = Pt(3)
        if k == 0:
            run(p, b[1] + ' ', bold=True, size=11, color='1F3864')
        mrich(p, part, E, size=11, numbers=numbers)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))      # a proposition is never split
    para(doc, 3)


def render_refs(doc):
    heading(doc, 'References', 14, before=12)
    groups = (('Published sources', lambda k: k.isdigit()),
              ('Notes of this series (in this repository)', lambda k: k.startswith('D')))
    for title, pred in groups:
        heading(doc, title, 11.5, color='2E6DB4', before=6)
        for r_ in all_refs():
            if pred(r_['key']):
                p = para(doc, 2, 0.5)
                run(p, f"[{r_['key']}] ", bold=True, size=9.5, color='3d4652')
                run(p, r_['text'] + ' ', size=9.5, color='3d4652')
                if r_['url']:
                    link(p, r_['url'], r_['url'], size=9.5)


def number_blocks(BL):
    numbers, n_eq, n_fig, n_tab = {}, 0, 0, 0
    for b in BL:
        eqs = []
        if b[0] == 'eq':
            eqs = [b[1]]
        elif b[0] == 'prop' and isinstance(b[2], list):
            eqs = [x[1] for x in b[2] if isinstance(x, tuple) and x[0] == 'eq']
        for key in eqs:
            n_eq += 1; numbers[key] = str(n_eq)
        if b[0] == 'img':
            n_fig += 1; numbers['#' + b[1]] = str(n_fig)
        elif b[0] == 'cap' and re.match(r'Table \{\{(\w+)\}\}', b[1]):
            n_tab += 1; numbers['#' + re.match(r'Table \{\{(\w+)\}\}', b[1]).group(1)] = str(n_tab)
    return numbers, n_eq, n_fig, n_tab


def main(out):
    with open(os.path.join(HERE, 'res', 'tronditja.json')) as fh:
        R = json.load(fh)
    with open(os.path.join(HERE, 'res', 'okada_checks.json')) as fh:
        C = json.load(fh)
    BL = blocks(R, C)
    numbers, n_eq, n_fig, n_tab = number_blocks(BL)
    E = Eqs()
    work = tempfile.mkdtemp()
    PF.main(work)
    figs = {k: os.path.join(work, f'fig_{k}.png') for k in FIGS}

    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
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
            if nxt in ('eq', 'eqn', 'prop'):
                p.paragraph_format.keep_with_next = True
        elif kind == 'b':
            p = para(doc, 3, 0.5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, '• ', bold=True); mrich(p, b[1], E, numbers=numbers)
            if nxt in ('eq', 'eqn'):
                p.paragraph_format.keep_with_next = True
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
                p.paragraph_format.space_after = Pt(4)
                mrich(p, item, E, size=10.5, numbers=numbers)
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            para(doc, 6)
        elif kind == 'prop':
            render_prop(doc, b, E, numbers)
        elif kind == 'proof':
            p = para(doc, 6, 0.4); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
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
        elif kind == 'pb':
            p = para(doc, 0); p.add_run().add_break(WD_BREAK.PAGE)
    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh, ensure_ascii=False)
    omml.main(draft, eq_json, out)
    print('saved', out, '|', n_eq, 'numbered equations,', len(E.items) - n_eq, 'inline |', n_fig, 'figures |', n_tab,
          'tables')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'TRONDITJA-GO.docx')
