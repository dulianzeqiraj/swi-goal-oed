"""Builds the WRR draft (Word, OMML equations, line numbers, AGU-style references).
usage: python build_wrr_doc.py OUT.docx
Text: text_wrr.py; figures: wrr_figs.py; results: res_field/field.json, res/wrr_synth.json, ../res/zanafilla.json;
references: res/refs_wrr.json (Crossref records).  Needs pandoc (through ../../ml_paradigms/word/omml.py)."""
import json
import os
import re
import sys
import tempfile

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(EXP, 'garancia_go'))
sys.path.insert(2, os.path.join(EXP, 'word_tools'))
sys.path.insert(3, os.path.join(EXP, 'ml_paradigms', 'word'))
from build_sota import run, para, heading, table, link  # noqa: E402
import omml  # noqa: E402
from build_gar_doc import Eqs, numref, mrich, display_eq, rich_cell  # noqa: E402
import wrr_figs as WF  # noqa: E402
from text_wrr import blocks, all_refs  # noqa: E402

FIGS = ('tracers', 'synth', 'field', 'decide', 'compare', 'next')


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


def line_numbers(sec):
    ln = OxmlElement('w:lnNumType')
    ln.set(qn('w:countBy'), '1'); ln.set(qn('w:restart'), 'continuous'); ln.set(qn('w:distance'), '284')
    sec._sectPr.append(ln)


def page_number_footer(sec):
    p = sec.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    for tag, txt in (('begin', None), (None, 'PAGE'), ('end', None)):
        if tag:
            fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), tag); r._r.append(fc)
        else:
            it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = txt; r._r.append(it)
    r.font.size = Pt(9)


def render_refs(doc):
    heading(doc, 'References', 13, before=12)
    for r_ in all_refs(None):
        p = para(doc, 3)
        p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.first_line_indent = Cm(-0.8)
        txt = r_['text']
        for part in re.split(r'(==[^=]+==)', txt):
            if part.startswith('=='):
                rr = run(p, part.strip('='), size=10)
                rr.font.highlight_color = 7
            elif part:
                run(p, part, size=10)
        if r_.get('url'):
            run(p, ' ', size=10)
            link(p, r_['url'], r_['url'], size=10)


def main(out):
    F = json.load(open(os.path.join(HERE, 'res_field', 'field.json')))
    Y = json.load(open(os.environ.get('WRR_SYNTH_JSON', os.path.join(HERE, 'res', 'wrr_synth.json'))))
    Z = json.load(open(os.path.join(os.path.dirname(HERE), 'res', 'zanafilla.json')))
    BL, s = blocks(F, Y, Z)
    numbers, n_eq, n_fig, n_tab = number_blocks(BL)
    E = Eqs()
    work = tempfile.mkdtemp()
    WF.fig_tracers(work); WF.fig_synth(work); WF.fig_field(work); WF.fig_decide(work)
    WF.fig_compare(work, ['340-L', '341-S', '868-HH', '898-AA', 'Long Beach-3 #5', 'Wilmington-2 #2', '331-A',
                          'Wilmington-1 #3', '351-M'])
    WF.fig_next(work)
    figs = {k: os.path.join(work, f'fig_{k}.png') for k in FIGS}

    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.2); sec.top_margin = sec.bottom_margin = Cm(2.0)
    line_numbers(sec); page_number_footer(sec)
    st = doc.styles['Normal']; st.font.name = 'Times New Roman'; st.font.size = Pt(12)
    st.paragraph_format.line_spacing = 1.5
    for bi, b in enumerate(BL):
        kind = b[0]
        nxt = BL[bi + 1][0] if bi + 1 < len(BL) else None
        if kind == 'refs':
            render_refs(doc)
        elif kind == 'title':
            p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run(p, b[1], bold=True, size=16)
        elif kind == 'authors':
            p = para(doc, 6)
            for part in re.split(r'(==[^=]+==)', b[1]):
                if part.startswith('=='):
                    rr = run(p, part.strip('='), size=12); rr.font.highlight_color = 7
                elif part:
                    run(p, part, size=12)
        elif kind == 'affil':
            p = para(doc, 3); run(p, b[1], size=11, italic=True)
        elif kind == 'kp_h':
            p = para(doc, 4, before=12); run(p, b[1], bold=True, size=12)
        elif kind == 'kp':
            p = para(doc, 3, 0.6); run(p, '• ', bold=True); mrich(p, b[1], E, numbers=numbers)
        elif kind == 'h':
            heading(doc, b[1], 13, before=14)
        elif kind == 'h2':
            heading(doc, b[1], 12, color='1F3864', before=8)
        elif kind == 'p':
            p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; mrich(p, b[1], E, numbers=numbers)
            if nxt in ('eq', 'eqn'):
                p.paragraph_format.keep_with_next = True
        elif kind == 'b':
            p = para(doc, 3, 0.6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, '• ', bold=True); mrich(p, b[1], E, numbers=numbers)
        elif kind == 'prop':
            p = para(doc, 4, before=4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, b[1] + ' ', bold=True); mrich(p, b[2], E, numbers=numbers, italic=True)
            if nxt in ('eq', 'eqn'):
                p.paragraph_format.keep_with_next = True
        elif kind == 'proof':
            p = para(doc, 6, 0.0); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, 'Proof. ', italic=True); mrich(p, b[1], E, numbers=numbers)
            run(p, '  □')
        elif kind == 'eq':
            display_eq(doc, E, b[2], numbers[b[1]])
        elif kind == 'table':
            rows = [[numref(c, numbers) for c in r_] for r_ in b[2]]
            hdr = [numref(c, numbers) for c in b[1]]
            t = table(doc, hdr, [[re.sub(r'\*\*|\*|\$|==|\[([^\]]+)\]\([^)]+\)', lambda m: m.group(1) or '', c)
                                  for c in r_] for r_ in rows], b[3], size=b[4])
            for i_, r_ in enumerate(rows, start=1):
                for j_, c in enumerate(r_):
                    if '$' in c or '==' in c:
                        rich_cell(t.rows[i_].cells[j_], c, E, numbers, b[4])
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            for r_ in t.rows:
                r_._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
                for c_ in r_.cells:
                    for pp in c_.paragraphs:
                        pp.paragraph_format.line_spacing = 1.0
            para(doc, 4)
        elif kind == 'img':
            p = para(doc, 2, before=6); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
            p.paragraph_format.line_spacing = 1.0
            p.add_run().add_picture(figs[b[1]], width=Cm(b[2]))
        elif kind == 'cap':
            p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.15
            mrich(p, b[1], E, size=10.5, numbers=numbers)
    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh, ensure_ascii=False)
    omml.main(draft, eq_json, out)
    print('saved', out, '|', n_eq, 'numbered equations,', len(E.items) - n_eq, 'inline |', n_fig, 'figures |', n_tab,
          'tables')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'WRR_draft.docx')
