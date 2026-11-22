"""Shared helpers for native Word equations (OMML through omml.py): the equation register Eqs, text with inline
math, displayed and numbered equations, borderless fixed-width tables."""
import re

from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from build_sota import run

SUBWORDS = ('asc', 'dsc', 'LOS', 'eq', 'yr', 'TG', 'pc', 'ke', 'kv', 'skv', 'sea', 'tide', 'surge', 'wave', 'max',
            'c1Ncs', 'sat', 'im', 'obs', 'pr', 'toe', 'test', 'cert', 'phys', 'rob')


WORDS = ('CSR', 'FS', 'CRR', 'MSF', 'LPI', 'TWL', 'FAR', 'miss', 'cost')


def upright(tex):
    """Descriptive names and subscripts upright; separators between joined equations written as words, so that both
    Word and LibreOffice show them clearly."""
    tex = re.sub(r'([_^])\{(?:\\,)?(' + '|'.join(SUBWORDS) + r')\}', r'\1{\\text{\2}}', tex)
    tex = re.sub(r'(?<![\\A-Za-z])(' + '|'.join(WORDS) + r')(?![A-Za-z])', r'\\text{\1}', tex)
    tex = tex.replace(', \\qquad ', ' \\quad\\text{ and }\\quad ').replace(' \\quad s.t. \\quad ', ' \\quad\\text{ subject to }\\quad ')
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
    """[[key]] -> (equation number); {{key}} -> figure or table number, assigned in order of appearance."""
    text = re.sub(r'\[\[(\w+)\]\]', lambda m: f'({numbers[m.group(1)]})', text)
    return re.sub(r'\{\{(\w+)\}\}', lambda m: numbers['#' + m.group(1)], text)


def mrich(p, text, E, size=11, numbers=None):
    """Text with $inline math$, **bold** and [[key]] equation numbers."""
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
    p = c0.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3); p.paragraph_format.space_after = Pt(3)
    run(p, E.add(tex, True))
    q = c1.paragraphs[0]; q.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run(q, f'({number})', size=11)
    trPr = t.rows[0]._tr.get_or_add_trPr(); trPr.append(OxmlElement('w:cantSplit'))


def rich_cell(cell, text, E, numbers, size):
    p = cell.paragraphs[0]
    for r_ in list(p.runs):
        r_._r.getparent().remove(r_._r)
    mrich(p, text, E, size=size, numbers=numbers)

