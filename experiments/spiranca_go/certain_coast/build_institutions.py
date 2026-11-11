"""CERTAIN-COAST (NATO SPS proposal): Brief overview of participating institutions, for the upload of the same name.

The form asks for "an overview of participating institutions' relevant capabilities, resources, and facilities" with
"any relevant websites of the institutions and the research teams", no more than one page per institution. One page per
institution: role in the project, at a glance, capabilities, resources and facilities, relevant projects and
publications, what it brings that is new, and the sources of every fact. Facts come only from the sources listed on
each page; what only the applicants know is a [placeholder] highlighted in yellow. The applicants fill the placeholders,
delete the page of any institution that does not take part, and save the file as PDF.

usage: python build_institutions.py OUT.docx"""
import os
import re
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import shade  # noqa: E402
from institutions_data import INST  # noqa: E402

NAVY = '1F3864'


def run(p, text, bold=False, italic=False, size=10, color=None, hl=False):
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    r.font.name = 'Arial'; r.font.size = Pt(size)
    r._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    if hl:
        r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    return r


def link(p, url, text=None, size=10):
    rid = p.part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    h = OxmlElement('w:hyperlink'); h.set(qn('r:id'), rid)
    r = OxmlElement('w:r'); rpr = OxmlElement('w:rPr')
    f = OxmlElement('w:rFonts'); f.set(qn('w:ascii'), 'Arial'); f.set(qn('w:hAnsi'), 'Arial'); rpr.append(f)
    c = OxmlElement('w:color'); c.set(qn('w:val'), '1F5FBF'); rpr.append(c)
    u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rpr.append(u)
    sz = OxmlElement('w:sz'); sz.set(qn('w:val'), str(int(size * 2))); rpr.append(sz)
    r.append(rpr)
    t = OxmlElement('w:t'); t.text = text or url; t.set(qn('xml:space'), 'preserve'); r.append(t)
    h.append(r); p._p.append(h)


def ph(p, text, size=10, bold=False, color=None):
    """Text with [placeholders] in yellow, **bold** segments and <url> links."""
    for part in re.split(r'(\[[^\]]+\]|<https?://[^>]+>)', text):
        if not part:
            continue
        if part.startswith('['):
            run(p, part, size=size, bold=bold, hl=True, color='000000')
        elif part.startswith('<http'):
            link(p, part[1:-1], size=size)
        else:
            for j, seg in enumerate(part.split('**')):
                if seg:
                    run(p, seg, size=size, bold=bold or j % 2 == 1, color=color)


def para(doc, after=3, before=0, indent=0, align=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(after); pf.space_before = Pt(before); pf.line_spacing = 1.08
    if indent:
        pf.left_indent = Cm(indent); pf.first_line_indent = Cm(-0.35)
    if align:
        p.alignment = align
    return p


def section(doc, title):
    p = para(doc, 1.5, before=5); run(p, title, bold=True, size=11, color=NAVY)
    p.paragraph_format.keep_with_next = True


def bullets(doc, items, size=9.8):
    for t in items:
        p = para(doc, 1.5, indent=0.45, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        run(p, '•  ', bold=True, size=size, color=NAVY); ph(p, t, size=size)


def cell_text(cell, text, size=9.5, bold=False, color=None):
    cell.text = ''
    p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
    ph(p, text, size=size, bold=bold, color=color)


def widths(t, ws):
    t.autofit = False
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); t._tbl.tblPr.append(lay)
    for j, gc in enumerate(t._tbl.tblGrid.findall(qn('w:gridCol'))):
        gc.set(qn('w:w'), str(int(ws[j] * 567)))
    for row in t.rows:
        for j, w in enumerate(ws):
            row.cells[j].width = Cm(w)


def page(doc, k, n, I):
    p = para(doc, 2)
    run(p, 'CERTAIN-COAST — Brief overview of participating institutions', size=8.8, color='52606D')
    run(p, f'      Institution {k} of {n}', size=8.8, color='52606D')
    band = doc.add_table(rows=1, cols=1); band.alignment = WD_TABLE_ALIGNMENT.CENTER
    widths(band, [17.4]); shade(band.rows[0].cells[0], NAVY)
    cell_text(band.rows[0].cells[0], I['role'], size=10, bold=True, color='FFFFFF')
    p = para(doc, 0, before=6); ph(p, I['name'], size=15, bold=True, color=NAVY)
    p = para(doc, 4); ph(p, I['local'], size=9.8, color='374151')
    if I.get('intro'):
        p = para(doc, 4, align=WD_ALIGN_PARAGRAPH.JUSTIFY); ph(p, I['intro'], size=9.6)
    if I.get('units'):
        u = doc.add_table(rows=1, cols=len(I['units'])); u.style = 'Table Grid'; u.alignment = WD_TABLE_ALIGNMENT.CENTER
        for c, U in zip(u.rows[0].cells, I['units']):
            cell_text(c, U['title'], size=9.6, bold=True, color=NAVY)
            q = c.add_paragraph(); q.paragraph_format.space_after = Pt(2); ph(q, U['sub'], size=8.8, color='374151')
            for line in U['lines']:
                q = c.add_paragraph(); q.paragraph_format.space_after = Pt(1.5)
                q.paragraph_format.left_indent = Cm(0.3); q.paragraph_format.first_line_indent = Cm(-0.3)
                run(q, '• ', bold=True, size=8.9, color=NAVY); ph(q, line, size=8.9)
        widths(u, [17.4 / len(I['units'])] * len(I['units']))
        para(doc, 2)
    g = doc.add_table(rows=0, cols=2); g.style = 'Table Grid'; g.alignment = WD_TABLE_ALIGNMENT.CENTER
    for lab, val in I['glance']:
        cells = g.add_row().cells
        cell_text(cells[0], lab, size=9.3, bold=True); shade(cells[0], 'EEF2F8')
        cell_text(cells[1], val, size=9.3)
    widths(g, [3.9, 13.5])
    for title, key in (('Relevant capabilities', 'capabilities'), ('Resources and facilities', 'resources'),
                       ('Relevant projects and publications', 'projects'), ('Role in CERTAIN-COAST', 'role_text'),
                       ('What it brings that is new', 'new')):
        if I.get(key):
            section(doc, title)
            bullets(doc, I[key])
    if I.get('sources'):
        p = para(doc, 0, before=5)
        run(p, 'Sources: ', bold=True, size=8.6, color='52606D')
        for j, (lab, url) in enumerate(I['sources']):
            if j:
                run(p, '; ', size=8.6, color='52606D')
            link(p, url, lab, size=8.6)
        run(p, '. Checked on 1 November 2026.', size=8.6, color='52606D')


def main(out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(1.8); s.top_margin = Cm(1.3); s.bottom_margin = Cm(1.2)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)
    for k, I in enumerate(INST, start=1):
        if k > 1:
            p = para(doc, 0); p.paragraph_format.page_break_before = True
        page(doc, k, len(INST), I)
    doc.save(out)
    print('saved', out, '| institutions', len(INST))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Institutions_Overview.docx')
