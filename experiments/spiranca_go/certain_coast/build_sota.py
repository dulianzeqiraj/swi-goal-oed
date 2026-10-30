"""CERTAIN-COAST (NATO SPS proposal): State of the Art. Builds a Word document (Arial, large type, clickable links):
the coupled hazard chain, state of the art per pillar, gap table, mathematical and physical innovations, and 30
annotated papers 2020-2026 (Caltech, MIT, Harvard, Oxford). Content in sota_data.py."""
import os
import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sota_data as D  # noqa: E402

FONT = 'Arial'


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
    """Text with [n] references kept as plain text; **bold** segments supported."""
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
    return t


def main(out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = FONT; st.font.size = Pt(11)

    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, D.TITLE, bold=True, size=18, color='1F3864')
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, D.FULL_TITLE, bold=True, size=12, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, D.SUBTITLE, italic=True, size=11, color='52606D')

    for sec_title, blocks in D.SECTIONS:
        heading(doc, sec_title, 14)
        for kind, content in blocks:
            if kind == 'p':
                p = para(doc, 6); rich(p, content)
            elif kind == 'h':
                heading(doc, content, 12, color='2E6DB4', before=6)
            elif kind == 'b':
                p = para(doc, 3, 0.5); run(p, '• ', bold=True); rich(p, content)
            elif kind == 'table':
                header, rows, widths = content
                table(doc, header, rows, widths)
                para(doc, 6)

    heading(doc, D.PAPERS_TITLE, 14)
    p = para(doc, 6); rich(p, D.PAPERS_INTRO)
    for grp, items in D.GROUPS:
        heading(doc, grp, 12.5, color='2E6DB4', before=6)
        for it in items:
            p = para(doc, 2); p.paragraph_format.keep_with_next = True
            run(p, f"[{it['n']}] ", bold=True, size=11, color='1F3864'); run(p, it['cite'], bold=True, size=10.5)
            p = para(doc, 2, 0.5)
            run(p, it['inst'] + '   ', size=10, color='52606D', italic=True)
            link(p, it['doi'], it['doi'].replace('https://', ''), 10)
            if it.get('free'):
                run(p, '   |   free: ', size=10); link(p, it['free'], it['free_label'], 10)
            else:
                run(p, '   |   ' + it.get('free_note', 'paywalled'), italic=True, size=10, color='52606D')
            p = para(doc, 2, 0.5); run(p, 'Done: ', bold=True, size=10.5); run(p, it['done'], size=10.5)
            p = para(doc, 8, 0.5); run(p, 'Beyond it in CERTAIN-COAST: ', bold=True, size=10.5, color='1E8A5A'); run(p, it['beyond'], size=10.5)

    heading(doc, 'Local study (not from the four universities)', 12.5, color='2E6DB4', before=6)
    for code, cite, url in D.LOCAL:
        p = para(doc, 3); run(p, f'[{code}] ', bold=True, size=11, color='1F3864'); run(p, cite + '  ', size=10.5); link(p, url, url.replace('https://', ''), 10)
    if getattr(D, 'NOTE', None):
        p = para(doc, 4, before=8); run(p, D.NOTE, italic=True, size=9.5, color='52606D')
    doc.save(out)
    print('saved', out, sum(len(i) for _, i in D.GROUPS), 'papers')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_State_of_the_Art.docx')
