"""Builds the GARANCIA-GO review (English, Word, OMML equations, clickable links) from the results in res/.

usage: python build_gar_doc.py OUT.docx
Text: text_gar.py and cards_gar.py; figures: gar_figs.py; results: res/gar_exp.json, res/gar_rcps.json,
res/gar_rainc.json. Needs pandoc (through ../ml_paradigms/word/omml.py)."""
import json
import os
import re
import sys
import tempfile

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_BREAK
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', 'spiranca_go', 'certain_coast'))
sys.path.insert(2, os.path.join(HERE, '..', 'ml_paradigms', 'word'))
from build_sota import run, para, heading, table, shade, link  # noqa: E402
import omml  # noqa: E402
import gar_figs as GF  # noqa: E402
from cards_gar import CARDS  # noqa: E402
from text_gar import blocks, all_refs  # noqa: E402

FIGS = ('map', 'scheme', 'case', 't1', 't2', 't3', 't4')
# card colours: darker steps of the figure hues, white text passes 4.5:1
CARD = dict(Oxford=('1D5FAE', 'EAF1FB'), Caltech=('A8441A', 'FCEEE7'), Berkeley=('0B6E4C', 'E6F5EE'),
            MIT=('4B3BB0', 'EEECFA'))
LINK_RE = re.compile(r'\[([^\]]+)\]\((https?://[^)\s]+)\)')


def upright(tex):
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


def borders(t, color, sz=6):
    tblPr = t._tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{side}'); e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), str(sz))
        e.set(qn('w:color'), color); b.append(e)
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


def plain(p, s, size, color=None, bold=False, italic=False):
    """**bold**, *italic*, ==yellow placeholder== inside a text segment (no math, no links)."""
    for j, seg in enumerate(s.split('==')):
        yellow = j % 2 == 1
        for k, s2 in enumerate(seg.split('**')):
            for l_, s3 in enumerate(s2.split('*')):
                if s3:
                    r_ = run(p, s3, bold=bold or (k % 2 == 1), italic=italic or (l_ % 2 == 1), size=size, color=color)
                    if yellow:
                        r_.font.highlight_color = WD_COLOR_INDEX.YELLOW


def mrich(p, text, E, size=11, numbers=None, color=None, bold=False, italic=False):
    """$math$, [text](url), **bold**, *italic*, ==yellow placeholder==."""
    if numbers:
        text = numref(text, numbers)
    for i, seg in enumerate(text.split('$')):
        if i % 2:
            run(p, E.add(seg, False, size=int(size * 2)), size=size)
            continue
        pos = 0
        for m in LINK_RE.finditer(seg):
            plain(p, seg[pos:m.start()], size, color, bold, italic)
            link(p, m.group(2), m.group(1), size=size)
            pos = m.end()
        plain(p, seg[pos:], size, color, bold, italic)


def display_eq(doc, E, tex, number):
    t = doc.add_table(rows=1, cols=2)
    no_borders(t); fixed_widths(t, [15.4, 1.6])
    c0, c1 = t.rows[0].cells
    for c in (c0, c1):
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    lines = tex if isinstance(tex, (list, tuple)) else [tex]
    for k, line in enumerate(lines):
        p = c0.paragraphs[0] if k == 0 else c0.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3 if k == 0 else 0)
        p.paragraph_format.space_after = Pt(3 if k == len(lines) - 1 else 1)
        run(p, E.add(line, True))
    q = c1.paragraphs[0]; q.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if number is not None:
        run(q, f'({number})', size=11)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))


def rich_cell(cell, text, E, numbers, size):
    p = cell.paragraphs[0]
    for r_ in list(p.runs):
        r_._r.getparent().remove(r_._r)
    mrich(p, text, E, size=size, numbers=numbers)


def cell_par(cell, first):
    p = cell.paragraphs[0] if first else cell.add_paragraph()
    p.paragraph_format.space_after = Pt(2); p.paragraph_format.space_before = Pt(1)
    return p


def render_card(doc, c, E):
    dark, light = CARD[c['inst']]
    t = doc.add_table(rows=4, cols=1)
    borders(t, dark, 8); fixed_widths(t, [17.0])
    # header
    h = t.rows[0].cells[0]; shade(h, dark)
    p = cell_par(h, True)
    run(p, f"{c['id']}  ·  {c['inst']}  ·  {c['year']}", bold=True, size=9.5, color='FFFFFF')
    p = cell_par(h, False)
    mrich(p, c['title'], E, size=11.5, color='FFFFFF', bold=True)
    # bibliographic row
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
    run(p, c['evidence'] + ' Status: partly verified (landing pages reached through search results only).',
        italic=True, size=9.5, color='52606D')
    # what it does and the three lessons
    w = t.rows[2].cells[0]; shade(w, light)
    p = cell_par(w, True); run(p, 'What it does. ', bold=True, size=10.5, color=dark)
    mrich(p, c['does'], E, size=10.5)
    for lab, key in (('Input parameters. ', 'inputs'), ('Dispersion coefficient. ', 'dispersion'),
                     ('Boundary conditions from rain alone. ', 'bcs')):
        p = cell_par(w, False); run(p, lab, bold=True, size=10.5, color=dark)
        mrich(p, c[key], E, size=10.5)
    s = t.rows[3].cells[0]; shade(s, 'E6F4EA')
    p = cell_par(s, True); run(p, 'Innovation step for our problem. ', bold=True, size=10.5, color='1E6B35')
    mrich(p, c['step'], E, size=10.5)
    for i_ in (0, 1, 3):
        t.rows[i_]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    for r_ in t.rows[:2]:
        for pp in r_.cells[0].paragraphs:
            pp.paragraph_format.keep_with_next = True
    para(doc, 6)


def main(out):
    with open(os.path.join(HERE, 'res', 'gar_exp.json')) as fh:
        E_ = json.load(fh)
    with open(os.path.join(HERE, 'res', 'gar_rcps.json')) as fh:
        R_ = json.load(fh)
    with open(os.path.join(HERE, 'res', 'gar_rainc.json')) as fh:
        RC_ = json.load(fh)
    BL = blocks(E_, R_, RC_)
    numbers, n_eq, n_fig, n_tab = {}, 0, 0, 0
    for b in BL:
        if b[0] == 'eq':
            n_eq += 1; numbers[b[1]] = str(n_eq)
        elif b[0] == 'img':
            n_fig += 1; numbers['#' + b[1]] = str(n_fig)
        elif b[0] == 'cap' and re.match(r'Table \{\{(\w+)\}\}', b[1]):
            n_tab += 1; numbers['#' + re.match(r'Table \{\{(\w+)\}\}', b[1]).group(1)] = str(n_tab)
    E = Eqs()
    work = tempfile.mkdtemp()
    GF.main(work, CARDS)
    figs = {k: os.path.join(work, f'fig_{k}.png') for k in FIGS}

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
            p = cell_par(c, True); mrich(p, b[1], E, size=10.5, numbers=numbers)
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
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
            t = table(doc, [re.sub(r'\$', '', h) for h in hdr], [[re.sub(r'\*\*|\$|==', '', c) for c in r_] for r_ in rows],
                      b[3], size=b[4])
            for j_, h in enumerate(hdr):
                if '$' in h:
                    cc = t.rows[0].cells[j_]
                    pp = cc.paragraphs[0]
                    for r_ in list(pp.runs):
                        r_._r.getparent().remove(r_._r)
                    mrich(pp, h, E, size=b[4], color='FFFFFF', bold=True)
            for i_, r_ in enumerate(rows, start=1):
                for j_, c in enumerate(r_):
                    if '$' in c or '**' in c or '==' in c:
                        rich_cell(t.rows[i_].cells[j_], c, E, numbers, b[4])
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            for r_ in t.rows[:-1]:                    # keep a short table on one page
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
            render_card(doc, b[1], E)
        elif kind == 'pb':
            p = para(doc, 0); p.add_run().add_break(WD_BREAK.PAGE)
    heading(doc, 'References', 14, before=12)
    groups = (('Anchors (provided by the user)', lambda k: k.startswith('A')),
              ('The twenty papers', lambda k: k[0] in 'OCBM'),
              ('Linked in the synthesis', lambda k: k.startswith('S')),
              ('Data and project documents', lambda k: k.startswith('D')))
    refs = all_refs()
    for title, pred in groups:
        heading(doc, title, 11.5, color='2E6DB4', before=6)
        for r_ in refs:
            if pred(r_['key']):
                p = para(doc, 2, 0.5)
                run(p, f"[{r_.get('label', r_['key'])}] ", bold=True, size=9.5, color='3d4652')
                run(p, r_['text'] + ' ', size=9.5, color='3d4652')
                if r_['url']:
                    link(p, r_['url'], r_['url'], size=9.5)
    p = para(doc, 2, before=6)
    run(p, 'Verification note. The bibliographic data of the twenty cards and of the works linked in the synthesis come '
           'from search results that quote the publisher, arXiv, proceedings or repository pages; doi.org, arxiv.org, '
           'openreview.net and most publisher hosts could not be opened directly in this environment. The anchors were '
           'read from the PDFs provided. Every number of Sections 1, 4 and 5 is computed by the code in '
           'experiments/garancia_go/.', italic=True, size=9.5, color='52606D')
    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh, ensure_ascii=False)
    omml.main(draft, eq_json, out)
    print('saved', out, '|', n_eq, 'numbered equations,', len(E.items) - n_eq, 'inline |', n_fig, 'figures |', n_tab,
          'tables')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'GARANCIA-GO.docx')
