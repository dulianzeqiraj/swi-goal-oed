"""CERTAIN-COAST: fill the official NATO template "SPS MYP Acceptance of Funds".

The template (downloaded from the "Managing SPS grants" page of nato.int) is kept as it is: its text, header, footer and
table are not changed. Filled in: one line naming the project above "Agreement", the NPD row (name, job title and
institution, as in the Agreement for Joint Research), the row of the institution's representative (the Rector,
Prof. Dr. Akli Fundo), names centred in their cells, and under each signature space the date of signature. Two signatures are required: the NPD and a suitable
representative of the NPD's institution (Head of Institution and/or Financial Authority). Nothing is signed here.

usage: python fill_acceptance_template.py TEMPLATE.docx OUT.docx"""
import os
import sys

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT as VA, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fill_agreement_template import TITLE, add, fill  # noqa: E402

DATE = '10/11/2026'  # date of signature (day/month/year, as in the Agreement signed by Qatar University)


def centre(cell, lines, valign=VA.CENTER, size=10):
    """Fill a cell with its lines centred horizontally and vertically (or at the bottom, for signatures)."""
    for extra in cell.paragraphs[1:]:  # the template cells hold empty paragraphs that would skew the centring
        extra._p.getparent().remove(extra._p)
    first = cell.paragraphs[0]
    for r in list(first._p):
        if r.tag != qn('w:pPr'):
            first._p.remove(r)
    fill(cell, lines, size)
    for p in cell.paragraphs:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cell.vertical_alignment = valign


def main(tpl, out):
    d = Document(tpl)
    body = list(d.element.body.iterchildren())
    texts = [''.join(t.text or '' for t in el.iter(qn('w:t'))) for el in body]
    i_agr = texts.index('Agreement')
    target = next(p for p in d.paragraphs if p._p is body[i_agr - 1])
    assert not target.text.strip(), 'the paragraph before "Agreement" is expected to be empty'
    add(target, 'Project: ', bold=True, size=11)
    add(target, f'CERTAIN-COAST — {TITLE} (NATO SPS Multi-Year Project, call 2027-1)', size=11)
    target.paragraph_format.space_after = Pt(10)

    t = d.tables[0]
    assert [c.text.strip() for c in t.rows[0].cells] == ['Signatory', 'Name', 'Job title and institution', 'Signature']
    npd, rep = t.rows[1], t.rows[2]
    assert npd.cells[0].text.startswith('NATO country Project Director') and rep.cells[0].text.startswith('A suitable')
    sig = [('', False), ('', False), ('', False), (f'Date: {DATE}', False)]
    centre(npd.cells[1], [('Assoc. Prof. Dr. Dulian Zeqiraj', True)])
    centre(npd.cells[2], [('NATO-country Project Director', False),
                          ('Associate Professor, Department of Energy Resources', False),
                          ('Faculty of Geology and Mining, Polytechnic University of Tirana, Tirana, Albania', False)], size=9)
    centre(npd.cells[3], sig, VA.BOTTOM)
    centre(rep.cells[1], [('Prof. Dr. Akli Fundo', True)])
    centre(rep.cells[2], [('Rector (Head of Institution)', False),
                          ('Polytechnic University of Tirana, Tirana, Albania', False)], size=9)
    centre(rep.cells[3], sig, VA.BOTTOM)
    for row in (npd, rep):  # same height for both rows, room for a signature
        row.height, row.height_rule = Cm(2.6), WD_ROW_HEIGHT_RULE.AT_LEAST
    d.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
