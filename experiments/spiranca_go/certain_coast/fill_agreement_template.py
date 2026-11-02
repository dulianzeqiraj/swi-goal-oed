"""CERTAIN-COAST: fill the official NATO template "SPS MYP Agreement for Joint Research".

The template (uploaded by the applicant) is kept as it is: its text, header, footer and table are not changed. Filled in:
one line naming the project above "Agreement", the NPD row (name and institution), the PPD row (yellow placeholders),
and, under each signature space, a line for the signatory's name, position and date. The template row "Add one row for
each Co-Director" is removed because the project has two Co-Directors. Yellow marks what the applicants still fill in.

usage: python fill_agreement_template.py TEMPLATE.docx OUT.docx"""
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.oxml.ns import qn
from docx.shared import Pt

TITLE = 'Certified early warning to protect water, port and energy infrastructure on a sinking Adriatic coast'
SIZE = 10


def add(p, text, bold=False, size=SIZE):
    """Runs in Arial; [placeholders] in yellow."""
    for part in re.split(r'(\[[^\]]+\])', text):
        if not part:
            continue
        r = p.add_run(part)
        r.font.name = 'Arial'; r.font.size = Pt(size); r.bold = bold
        r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'Arial')
        if part.startswith('['):
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW


def fill(cell, lines, size=SIZE):
    first = cell.paragraphs[0]
    for k, (text, bold) in enumerate(lines):
        p = first if k == 0 else cell.add_paragraph()
        p.paragraph_format.space_after = Pt(2); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        add(p, text, bold, size)


def main(tpl, out):
    d = Document(tpl)
    body = list(d.element.body.iterchildren())
    texts = [''.join(t.text or '' for t in el.iter(qn('w:t'))) for el in body]
    i_agr = texts.index('Agreement')
    # the project line goes into the empty paragraph just before "Agreement"
    target = next(p for p in d.paragraphs if p._p is body[i_agr - 1])
    add(target, 'Project: ', bold=True, size=11)
    add(target, f'CERTAIN-COAST — {TITLE} (NATO SPS Multi-Year Project, call 2027-1)', size=11)

    t = d.tables[0]
    assert [c.text for c in t.rows[0].cells] == ['Role', 'Name', 'Signature', 'Institution', 'Signature for Institution']
    npd, ppd, extra = t.rows[1], t.rows[2], t.rows[3]
    assert npd.cells[0].text == 'NPD' and ppd.cells[0].text == 'PPD' and extra.cells[0].text.startswith('Add one row')
    extra._tr.getparent().remove(extra._tr)

    sig = [('', False), ('', False), ('', False), ('Date: [ ]', False)]
    fill(npd.cells[1], [('Assoc. Prof. Dr. Dulian Zeqiraj', True), ('NATO-country Project Director', False)])
    fill(npd.cells[2], sig)
    fill(npd.cells[3], [('Polytechnic University of Tirana', True),
                        ('Faculty of Geology and Mining', False), ('Tirana, Albania', False)])
    fill(npd.cells[4], [('', False), ('', False), ('', False),
                        ('[Name], [Rector or authorised person]', False), ('Date: [ ]', False)])
    fill(ppd.cells[1], [('[Title, first name, family name]', True), ('Partner-country Project Director', False)])
    fill(ppd.cells[2], sig)
    fill(ppd.cells[3], [('[Institution]', True), ('[Faculty or department]', False), ('[City, country]', False)])
    fill(ppd.cells[4], [('', False), ('', False), ('', False),
                        ('[Name], [Head of institution or financial authority]', False), ('Date: [ ]', False)])
    d.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
