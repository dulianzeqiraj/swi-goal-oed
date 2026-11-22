"""Builds the note "Hypotheses as terms of the differential equations" (HIPOTEZA-GO): English, Word, OMML equations.
usage: python build_hip_doc.py OUT.docx
Text: text_hip.py; figures: hip_figs.py; results: res/hipoteza.json, res/dyn.json.
Needs pandoc (through ../ml_paradigms/word/omml.py)."""
import json
import os
import re
import sys
import tempfile

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(EXP, 'garancia_go'))
sys.path.insert(2, os.path.join(EXP, 'word_tools'))
sys.path.insert(3, os.path.join(EXP, 'ml_paradigms', 'word'))
from build_sota import run, para, heading, table, link, shade  # noqa: E402
import omml  # noqa: E402
from build_gar_doc import Eqs, borders, fixed_widths, numref, mrich, display_eq, rich_cell, cell_par  # noqa: E402
import hip_figs as HF  # noqa: E402
from text_hip import blocks, REFS  # noqa: E402


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


VERIFY = ('Verification note. Every reference with a DOI was checked on Crossref. The statements about the three '
          'attached papers rest on their text as read for this note (G21: Sections 2, 4.4, 5.1 and 8.2; B16: '
          'the main text; F20: Sections 2 and 4); L26 and the two conference papers cited in the pasted note '
          'were not read. Every number of Section 6 is computed by the code in experiments/hipoteza_go; the '
          'aquifer is synthetic. Generative AI tools assisted with the reading, the code and the drafting of '
          'this note; the author checks the statements, numbers and references and is responsible for them.')


def main(out):
    R = json.load(open(os.path.join(HERE, 'res', 'hipoteza.json')))
    dpath = os.path.join(HERE, 'res', 'dyn.json')
    D = json.load(open(dpath)) if os.path.exists(dpath) else None
    work = tempfile.mkdtemp()
    F = HF.fig_fields(work)
    HF.fig_decide(work, R); F['example'] = HF.fig_example(work, R); HF.fig_terms(work, R)
    if D is not None:
        HF.fig_dyn(work)
    figs = {k: os.path.join(work, f'fig_{k}.png') for k in ('fields', 'decide', 'example', 'terms', 'dyn')}
    BL, s = blocks(R, D, F)
    render(BL, REFS, figs, out, VERIFY, work)


def render(BL, REFS, figs, out, verify, work):
    numbers, n_eq, n_fig, n_tab = number_blocks(BL)
    E = Eqs()
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.0); sec.top_margin = sec.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    for bi, b in enumerate(BL):
        k = b[0]
        nxt = BL[bi + 1][0] if bi + 1 < len(BL) else None
        if k == 'title':
            p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, b[1], bold=True, size=18, color='1F3864')
        elif k == 'subtitle':
            p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, b[1], size=11.5, color='1F3864')
        elif k == 'byline':
            p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, b[1], italic=True, size=10, color='52606D')
        elif k == 'h':
            heading(doc, b[1], 14, before=12)
        elif k == 'h2':
            heading(doc, b[1], 12, color='2E6DB4', before=6)
        elif k == 'p':
            p = para(doc, 5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; mrich(p, b[1], E, numbers=numbers)
            if nxt == 'eq':
                p.paragraph_format.keep_with_next = True
        elif k == 'b':
            p = para(doc, 3, 0.5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, '• ', bold=True); mrich(p, b[1], E, numbers=numbers)
        elif k == 'box':
            t = doc.add_table(rows=1, cols=1); borders(t, '7FB58E', 6); fixed_widths(t, [17.0])
            c = t.rows[0].cells[0]; shade(c, 'E6F4EA')
            for i, item in enumerate(b[1]):
                p = cell_par(c, i == 0); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.space_after = Pt(4)
                mrich(p, item, E, size=10.5, numbers=numbers)
            para(doc, 6)
        elif k == 'prop':
            t = doc.add_table(rows=1, cols=1); borders(t, 'B9C6D6', 6); fixed_widths(t, [17.0])
            c = t.rows[0].cells[0]; shade(c, 'F2F5F9')
            p = cell_par(c, True); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, b[1] + ' ', bold=True, size=11, color='1F3864'); mrich(p, b[2], E, size=11, numbers=numbers)
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            para(doc, 3)
        elif k == 'proof':
            p = para(doc, 6, 0.4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, 'Proof. ', italic=True, bold=True, size=10.5); mrich(p, b[1], E, size=10.5, numbers=numbers)
            run(p, '  □', size=10.5)
        elif k == 'eq':
            display_eq(doc, E, b[2], numbers[b[1]])
        elif k == 'table':
            rows = [[numref(c, numbers) for c in r_] for r_ in b[2]]
            hdr = [numref(c, numbers) for c in b[1]]
            t = table(doc, hdr, [[re.sub(r'\*\*|\*|\$|==', '', c) for c in r_] for r_ in rows], b[3], size=b[4])
            for i_, r_ in enumerate(rows, start=1):
                for j_, c in enumerate(r_):
                    if '$' in c or '==' in c or '**' in c:
                        rich_cell(t.rows[i_].cells[j_], c, E, numbers, b[4])
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            for r_ in t.rows:
                r_._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            if len(t.rows) <= 8:                               # a short table stays on one page
                for r_ in t.rows[:-1]:
                    for c_ in r_.cells:
                        for p_ in c_.paragraphs:
                            p_.paragraph_format.keep_with_next = True
            para(doc, 4)
        elif k == 'img':
            p = para(doc, 2, before=4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(figs[b[1]], width=Cm(b[2]))
        elif k == 'cap':
            p = para(doc, 7); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            mrich(p, b[1], E, size=10, numbers=numbers, italic=True)
        elif k == 'refs':
            heading(doc, 'References', 14, before=12)
            for key, text, url in REFS:
                p = para(doc, 2, 0.5)
                run(p, f'[{key}] ', bold=True, size=9.5, color='3d4652'); run(p, text + ' ', size=9.5, color='3d4652')
                if url:
                    link(p, url, url, size=9.5)
            p = para(doc, 2, before=6)
            run(p, verify, italic=True, size=9.5, color='52606D')
    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    json.dump(E.items, open(eq_json, 'w', encoding='utf-8'), ensure_ascii=False)
    omml.main(draft, eq_json, out)
    print('saved', out, '|', n_eq, 'numbered equations |', n_fig, 'figures |', n_tab, 'tables')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'HIPOTEZA-GO.docx')
