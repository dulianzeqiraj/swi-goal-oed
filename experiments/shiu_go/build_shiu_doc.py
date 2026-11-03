"""Builds the SHIU-GO note (Albanian, Word, OMML equations) from the results in res/.

usage: python build_shiu_doc.py OUT.docx"""
import json
import os
import re
import sys
import tempfile

import numpy as np
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'spiranca_go', 'certain_coast'))
sys.path.insert(2, os.path.join(HERE, '..', 'ml_paradigms', 'word'))
from build_sota import run, para, heading, table, shade  # noqa: E402
import omml  # noqa: E402
import shiu_figs as SF  # noqa: E402
from text_shiu import blocks, REFS  # noqa: E402

SUBWORDS = ('tot', 'det', 'ia', 'surge', 'tide', 'fc', 'w', 'pred', 'phys', 'obs', 'E', 'L', 'R', 'e', 's', 'c',
            'ow', 'm', 'h', 'max', 'min', 'p', 'n', 'K', 'x')
WORDS = ()


def upright(tex):
    tex = re.sub(r'([_^])\{(tot|det|ia|surge|tide|fc|pred|phys|obs|ow|max|min|sea|top|res|true|ET)\}', r'\1{\\text{\2}}', tex)
    # \bar is an accent (U+203E) that LibreOffice draws like an acute; \overline draws as a bar in both programs
    tex = re.sub(r'\\bar\s*\{([^{}]*)\}', r'\\overline{\1}', tex)
    tex = re.sub(r'\\bar\s*(\\[A-Za-z]+|[A-Za-z])', r'\\overline{\1}', tex)
    return tex


class Eqs:
    def __init__(self):
        self.items = []

    def add(self, tex, display, size=None):
        tex = upright(tex)
        i = len(self.items)
        d = {'id': i, 'tex': tex, 'display': display}
        if size:
            d['size'] = size
        self.items.append(d)
        return f'§§EQ{i}§§' if display else f'§§IQ{i}§§'


def no_borders(t):
    tblPr = t._tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{side}'); e.set(qn('w:val'), 'nil'); b.append(e)
    tblPr.append(b)


def fixed_widths(t, widths):
    t.autofit = False
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); t._tbl.tblPr.append(lay)
    for j, gc in enumerate(t._tbl.tblGrid.findall(qn('w:gridCol'))):
        gc.set(qn('w:w'), str(int(widths[j] * 567)))
    for row in t.rows:
        for j, w in enumerate(widths):
            row.cells[j].width = Cm(w)


def numref(text, numbers):
    text = re.sub(r'\[\[(\w+)\]\]', lambda m: f'({numbers[m.group(1)]})', text)
    return re.sub(r'\{\{(\w+)\}\}', lambda m: numbers['#' + m.group(1)], text)


def mrich(p, text, E, size=11, numbers=None):
    if numbers:
        text = numref(text, numbers)
    for i, seg in enumerate(text.split('$')):
        if i % 2:
            run(p, E.add(seg, False, size=int(size * 2)), size=size)
            continue
        for j, s in enumerate(seg.split('**')):
            if s:
                run(p, s, bold=(j % 2 == 1), size=size)


def display_eq(doc, E, tex, number):
    t = doc.add_table(rows=1, cols=2)
    no_borders(t); fixed_widths(t, [15.4, 1.6])
    c0, c1 = t.rows[0].cells
    for c in (c0, c1):
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    # a long equation is given as a tuple of lines: one math paragraph per line, one number
    lines = tex if isinstance(tex, (list, tuple)) else [tex]
    for k, line in enumerate(lines):
        p = c0.paragraphs[0] if k == 0 else c0.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3 if k == 0 else 0)
        p.paragraph_format.space_after = Pt(3 if k == len(lines) - 1 else 1)
        run(p, E.add(line, True))
    q = c1.paragraphs[0]; q.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if number is not None:                      # 'eqn' blocks are displayed without a number
        run(q, f'({number})', size=11)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))


def rich_cell(cell, text, E, numbers, size):
    p = cell.paragraphs[0]
    for r_ in list(p.runs):
        r_._r.getparent().remove(r_._r)
    mrich(p, text, E, size=size, numbers=numbers)


def main(out):
    with open(os.path.join(HERE, 'res', 'shiu_exp.json')) as fh:
        J = json.load(fh)
    with open(os.path.join(HERE, 'res', 'shiu_km.json')) as fh:
        K = json.load(fh)
    BL, vals = blocks(J, K)
    numbers, n_eq, n_fig, n_tab = {}, 0, 0, 0
    for b in BL:
        if b[0] == 'eq':
            n_eq += 1; numbers[b[1]] = str(n_eq)
        elif b[0] == 'img':
            n_fig += 1; numbers['#' + b[1]] = str(n_fig)
        elif b[0] == 'cap' and re.match(r'Tabela \{\{(\w+)\}\}', b[1]):
            n_tab += 1; numbers['#' + re.match(r'Tabela \{\{(\w+)\}\}', b[1]).group(1)] = str(n_tab)
    E = Eqs()
    work = tempfile.mkdtemp()
    SF.main(work)
    figs = {k: os.path.join(work, f'fig_{k}.png') for k in ('system', 'twin', 'results', 'routeB', 'km')}

    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    for bi, b in enumerate(BL):
        kind = b[0]
        nxt = BL[bi + 1][0] if bi + 1 < len(BL) else None
        if kind == 'title':
            p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run(p, b[1], bold=True, size=17, color='1F3864')
        elif kind == 'subtitle':
            p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run(p, b[1], bold=False, size=11.5, color='1F3864')
        elif kind == 'byline':
            p = para(doc, 12); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run(p, b[1], italic=True, size=10, color='52606D')
        elif kind == 'h':
            heading(doc, b[1], 13.5, before=10)
        elif kind == 'h2':
            heading(doc, b[1], 12, color='2E6DB4', before=6)
        elif kind == 'p':
            p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; mrich(p, b[1], E, numbers=numbers)
            if nxt in ('eq', 'eqn'):
                p.paragraph_format.keep_with_next = True
        elif kind == 'box':
            t = doc.add_table(rows=1, cols=1); t.style = 'Table Grid'
            c = t.rows[0].cells[0]; shade(c, 'E6F4EA')
            p = c.paragraphs[0]; mrich(p, b[1], E, size=10.5, numbers=numbers)
            para(doc, 4)
        elif kind == 'b':
            p = para(doc, 3, 0.5); run(p, '• ', bold=True); mrich(p, b[1], E, numbers=numbers)
        elif kind == 'eq':
            display_eq(doc, E, b[2], numbers[b[1]])
        elif kind == 'eqn':
            display_eq(doc, E, b[1], None)
        elif kind == 'table':
            rows = [[numref(c, numbers) for c in r_] for r_ in b[2]]
            t = table(doc, b[1], [[re.sub(r'\*\*|\$', '', c) for c in r_] for r_ in rows], b[3], size=b[4])
            for i_, r_ in enumerate(rows, start=1):
                for j_, c in enumerate(r_):
                    if '$' in c or '**' in c:
                        rich_cell(t.rows[i_].cells[j_], c, E, numbers, b[4])
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            para(doc, 4)
        elif kind == 'img':
            p = para(doc, 2, before=4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(figs[b[1]], width=Cm(b[2]))
        elif kind == 'cap':
            p = para(doc, 6); p.paragraph_format.keep_with_next = b[1].startswith('Tabela')
            run(p, numref(b[1], numbers), italic=True, size=10, color='52606D')
        elif kind == 'pb':
            p = para(doc, 0); p.add_run().add_break(__import__('docx').enum.text.WD_BREAK.PAGE)
    heading(doc, 'Referencat', 13.5, before=10)
    for r_ in REFS:
        p = para(doc, 2, 0.5); run(p, r_, size=9.5, color='3d4652')
    p = para(doc, 2, before=4)
    run(p, 'Të gjitha referencat janë marrë nga tri materialet e dhëna (PDF-ja e ETH dhe dy rishikimet tuaja, me të '
           'dhënat e kontrolluara atje), përveç Rodriguez-Iturbe et al. (1999) dhe Anvari et al. (2016), të kontrolluara '
           'më 3 nëntor 2026 në indekse bibliografike.', italic=True, size=9.5, color='52606D')
    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh, ensure_ascii=False)
    omml.main(draft, eq_json, out)
    print('saved', out, '|', n_eq, 'numbered equations,', len(E.items) - n_eq, 'inline |', n_fig, 'figures |', vals)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'SHIU-GO.docx')
