"""CERTAIN-COAST: fill the official NATO template "SPS MYP Acceptance of Funds".

The template (downloaded from the "Managing SPS grants" page of nato.int) is kept as it is: its text, header, footer and
table are not changed. Filled in: one line naming the project above "Agreement", the NPD row (name, job title and
institution, as in the Agreement for Joint Research), the row of the institution's representative (the Rector,
Prof. Dr. Akli Fundo), and under each signature space a line for the date. Two signatures are required: the NPD and a suitable
representative of the NPD's institution (Head of Institution and/or Financial Authority). Nothing is signed here.

usage: python fill_acceptance_template.py TEMPLATE.docx OUT.docx"""
import os
import sys

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fill_agreement_template import TITLE, add, fill  # noqa: E402


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
    sig = [('', False), ('', False), ('', False), ('Date: [ ]', False)]
    fill(npd.cells[1], [('Assoc. Prof. Dr. Dulian Zeqiraj', True)])
    fill(npd.cells[2], [('NATO-country Project Director; Associate Professor, Department of Energy Resources', False),
                        ('Faculty of Geology and Mining, Polytechnic University of Tirana, Tirana, Albania', False)])
    fill(npd.cells[3], sig)
    fill(rep.cells[1], [('Prof. Dr. Akli Fundo', True)])
    fill(rep.cells[2], [('Rector (Head of Institution)', False),
                        ('Polytechnic University of Tirana, Tirana, Albania', False)])
    fill(rep.cells[3], sig)
    d.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
