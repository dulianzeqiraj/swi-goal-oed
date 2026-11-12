"""CERTAIN-COAST: the filled "SPS MYP Agreement for Joint Research" with the names and dates of the version that was
signed (Qatar University on 5 November 2026, the NPD on 10 November 2026), so that the Word file matches the signed
scan. The signatures themselves are only on the scan, which stays out of the repository.

usage: python agreement_as_signed.py IN.docx OUT.docx      (IN: the output of fill_agreement_template.py)"""
import copy
import sys

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt

SIZE = 10
NPD_DATE, PPD_DATE = '10/11/2026', '5/11/2026'


def set_text(p, text, bold=False):
    """Replace the runs of paragraph p by one Arial run, without highlight."""
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    r = p.add_run(text)
    r.font.name = 'Arial'
    r.font.size = Pt(SIZE)
    r.bold = bold
    r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'Arial')


def insert_after(p, text, bold=False):
    new = copy.deepcopy(p._p)
    p._p.addnext(new)
    from docx.text.paragraph import Paragraph
    q = Paragraph(new, p._parent)
    set_text(q, text, bold)
    return q


def main(src, out):
    doc = Document(src)
    t = doc.tables[0]
    rows = {r.cells[0].text.strip(): r for r in t.rows}
    npd, ppd = rows['NPD'].cells, rows['PPD'].cells
    # NPD: own signature date; the Rector signs for the institution
    set_text(npd[2].paragraphs[-1], f'Date: {NPD_DATE}')
    p = npd[4].paragraphs[-2]
    set_text(p, 'Prof. Dr. Akli Fundo', bold=True)
    insert_after(p, 'Rector')
    set_text(npd[4].paragraphs[-1], f'Date: {NPD_DATE}')
    # PPD and Qatar University
    set_text(ppd[1].paragraphs[0], 'Prof. Jassim Al-Khayat', bold=True)
    set_text(ppd[2].paragraphs[-1], f'Date: {PPD_DATE}')
    lines = ['Qatar University', 'Manager of Research Vessel “Janan” at The Environmental Science Center',
             'Doha, Qatar']
    for k, (p, text) in enumerate(zip(ppd[3].paragraphs, lines)):
        set_text(p, text, bold=k == 0)
    set_text(ppd[4].paragraphs[-2], 'Fares AlMomani', bold=True)
    set_text(ppd[4].paragraphs[-1], f'Date: {PPD_DATE}')
    left = sum(1 for x in doc.element.body.iter(qn('w:highlight')))
    doc.save(out)
    print('saved', out, '| highlighted placeholders left:', left)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
