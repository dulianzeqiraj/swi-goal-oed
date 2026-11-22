"""Shared Word helpers (python-docx): runs, links, paragraphs, headings, rich text, shaded cells and tables.
Used by the builders of the notes and reviews in experiments/*."""
import os
import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = 'Arial'


_EQ = None          # set by main(): text between $...$ becomes native Word math (OMML)


def run(p, text, bold=False, italic=False, size=11, color=None):
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    r.font.name = FONT; r.font.size = Pt(size)
    r._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    return r


def link(p, url, text, size=11):
    rid = p.part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    h = OxmlElement('w:hyperlink'); h.set(qn('r:id'), rid)
    r = OxmlElement('w:r'); rpr = OxmlElement('w:rPr')
    f = OxmlElement('w:rFonts'); f.set(qn('w:ascii'), FONT); f.set(qn('w:hAnsi'), FONT); rpr.append(f)
    c = OxmlElement('w:color'); c.set(qn('w:val'), '1F5FBF'); rpr.append(c)
    u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rpr.append(u)
    sz = OxmlElement('w:sz'); sz.set(qn('w:val'), str(int(size * 2))); rpr.append(sz)
    r.append(rpr)
    t = OxmlElement('w:t'); t.text = text; t.set(qn('xml:space'), 'preserve'); r.append(t)
    h.append(r); p._p.append(h)


def para(doc, after=4, indent=0, before=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after); p.paragraph_format.space_before = Pt(before)
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    return p


def heading(doc, text, size=14, color='1F3864', before=10):
    p = para(doc, 6, before=before); run(p, text, bold=True, size=size, color=color)
    p.paragraph_format.keep_with_next = True
    return p


def rich(p, text, size=11):
    """Text with [n] references kept as plain text; **bold** segments supported; $math$ while main() runs."""
    if _EQ is not None and '$' in text:
        for i, seg in enumerate(text.split('$')):
            if i % 2:
                run(p, _EQ.add(seg, False, size=int(size * 2)), size=size)
            elif seg:
                rich(p, seg.replace('$', ''), size)
        return
    parts = text.split('**')
    for i, seg in enumerate(parts):
        if seg:
            run(p, seg, bold=(i % 2 == 1), size=size)


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hexcolor)
    tcPr.append(sh)


def table(doc, header, rows, widths, size=10):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(header):
        c = t.rows[0].cells[j]; c.text = ''
        run(c.paragraphs[0], h, bold=True, size=size, color='FFFFFF'); shade(c, '1F3864')
    for r_ in rows:
        cells = t.add_row().cells
        for j, v in enumerate(r_):
            cells[j].text = ''
            rich(cells[j].paragraphs[0], v, size=size)
    t.autofit = False
    tblPr = t._tbl.tblPr
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); tblPr.append(lay)
    grid = t._tbl.tblGrid
    for j, gc in enumerate(grid.findall(qn('w:gridCol'))):
        gc.set(qn('w:w'), str(int(widths[j] * 567)))
    for j, w in enumerate(widths):
        t.columns[j].width = Cm(w)
    for row in t.rows:
        for j, w in enumerate(widths):
            row.cells[j].width = Cm(w)
        trPr = row._tr.get_or_add_trPr()
        cs = OxmlElement('w:cantSplit'); trPr.append(cs)
    return t

