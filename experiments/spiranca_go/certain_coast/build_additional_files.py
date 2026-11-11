"""CERTAIN-COAST (NATO SPS proposal): the single PDF for the "Additional files (optional)" upload of the application
form. It holds a contents page, the technical annex, the technical note on the assembled system of equations and the
placement of recharge and supply wells, the BEYOND-GO theory note on the inland boundary, the SHOCK-GO
implementation report on the earthquake in the aquifer and the CV of the NATO-country Project Director (build_cv.py
--npd) and the CV of the partner-country Project Director (build_cv.py --ppd), with PDF bookmarks. New parts go
at the end, because the annex refers to the notes by their position. The form asks for one PDF with a table of contents at the start when several documents are uploaded.

usage: python build_additional_files.py OUT.pdf
Needs LibreOffice (soffice), python-docx and pypdf."""
import os
import subprocess
import sys
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from pypdf import PdfReader, PdfWriter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from codenames import english  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
PARTS = [
    ('Technical annex: how the methods work, the preparatory tests, the gates with their fallbacks and the nine new '
     'contributions', 'Technical annex', os.path.join(ROOT, 'docs', 'certain_coast', 'CERTAIN-COAST_Technical_Annex.pdf')),
    ('Technical note: assembling the equations of a coastal aquifer, with the placement of recharge and pumping wells '
     'as the final goal (preparatory work of the NPD\'s team, October 2026; corrected 8 November 2026)',
     'Technical note: the assembled system and the placement of the wells',
     os.path.join(ROOT, 'docs', 'research_notes', 'Assembled_System_Equations_Placing_Recharge_and_Pumping_Wells.docx')),
    ('Theory note: BEYOND-GO, the boundary condition the flow equation is missing — a learnable boundary where the '
     'model is cut, four propositions with proofs and six numerical checks (preparatory work of the NPD\'s team, '
     'November 2026)',
     'Theory note: BEYOND-GO, the boundary where the model is cut',
     os.path.join(ROOT, 'docs', 'research_notes', 'PERTEJ-GO_Transparent_Learnable_Boundary_Flow_Equation.docx')),
    ('Implementation report: SHOCK-GO, the earthquake, the aquifer and liquefaction — the pore-pressure step of '
     'each layer, the earthquake as a free pumping test, the design of the 2019 hindcast and the joint safe window, '
     'with numerical checks (preparatory work of the NPD\'s team, November 2026)',
     'Implementation report: SHOCK-GO, the earthquake in the aquifer',
     os.path.join(ROOT, 'docs', 'research_notes', 'TRONDITJA-GO_Earthquake_Aquifer_Liquefaction_Implementation.docx')),
    ('Curriculum vitae of the NATO-country Project Director, Assoc. Prof. Dr. Dulian Zeqiraj (Faculty of Geology and '
     'Mining, Polytechnic University of Tirana)',
     'CV of the NATO-country Project Director',
     os.path.join(ROOT, 'docs', 'certain_coast', 'CERTAIN-COAST_CV_NPD_Zeqiraj.docx')),
    ('Curriculum vitae of the partner-country Project Director, Prof. Jassim Al-Khayat (Environmental Science Center, '
     'Qatar University)',
     'CV of the partner-country Project Director',
     os.path.join(ROOT, 'docs', 'certain_coast', 'CERTAIN-COAST_CV_PPD_Al-Khayat.docx')),
]


def to_pdf(path, outdir):
    if path.endswith('.pdf'):
        return path
    if os.path.dirname(os.path.abspath(path)) != os.path.abspath(outdir):      # the English names of the experiments
        from codenames import english_docx
        copy = os.path.join(outdir, english(os.path.basename(path).replace('_', ' ')).replace(' ', '_'))
        english_docx(path, copy)
        path = copy
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', outdir, path], check=True,
                   capture_output=True, timeout=600)
    return os.path.join(outdir, os.path.splitext(os.path.basename(path))[0] + '.pdf')


def contents_pdf(rows, outdir):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.2); sec.top_margin = Cm(3.0)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)

    def para(text, size=11, bold=False, color='1F2328', after=6, align=None, italic=False):
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(after)
        if align is not None:
            p.alignment = align
        r = p.add_run(text); r.font.size = Pt(size); r.bold = bold; r.italic = italic
        r.font.color.rgb = RGBColor.from_string(color)

    para('CERTAIN-COAST', 20, True, '1F3864', 4, WD_ALIGN_PARAGRAPH.CENTER)
    para('Certified early warning to protect water, port and energy infrastructure on a sinking Adriatic coast', 12,
         False, '1F3864', 4, WD_ALIGN_PARAGRAPH.CENTER)
    para('NATO SPS Multi-Year Project, call 2027-1 · Additional files', 10.5, False, '5B6672', 30,
         WD_ALIGN_PARAGRAPH.CENTER, italic=True)
    para('Contents', 14, True, '1F3864', 10)
    widths = (1.0, 13.0, 2.4)
    t = doc.add_table(rows=1, cols=3)
    for j, h in enumerate(('', 'Document', 'Pages')):
        c = t.rows[0].cells[j]; c.text = ''
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(10.5)
    for row in rows:
        cells = t.add_row().cells
        for j, v in enumerate(row):
            cells[j].text = ''
            r = cells[j].paragraphs[0].add_run(v); r.font.size = Pt(10.5)
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); t._tbl.tblPr.append(lay)
    for gc, w in zip(t._tbl.tblGrid.findall(qn('w:gridCol')), widths):
        gc.set(qn('w:w'), str(int(w * 567)))
    for row in t.rows:
        for c, w in zip(row.cells, widths):
            c.width = Cm(w)
    para('', after=14)
    para('The application form is self-contained; these files give detail for readers who want it. The technical note '
         'is background on the coupled model of work package 2 and on the placement of recharge and supply wells. The '
         'theory note gives the proofs and the checks behind the inland boundary of that model (Section 4.3 of the '
         'annex), and the implementation report the code and the checks behind the earthquake in the aquifer (Section '
         '4.4). The tests are synthetic and their numbers illustrative, not results at Durrës. The CVs of the '
         'two Project Directors close the files.', 10,
         False, '5B6672', 6, italic=True)
    path = os.path.join(outdir, 'contents.docx')
    doc.save(path)
    return to_pdf(path, outdir)


def main(out):
    work = tempfile.mkdtemp()
    pdfs = [(full, short, to_pdf(src, work)) for full, short, src in PARTS]
    counts = [len(PdfReader(p).pages) for _, _, p in pdfs]
    rows, start = [], 2                                    # the contents take page 1
    for k, ((full, _, _), n) in enumerate(zip(pdfs, counts), start=1):
        rows.append((f'{k}.', full, f'{start}–{start + n - 1}'))
        start += n
    toc = contents_pdf(rows, work)
    assert len(PdfReader(toc).pages) == 1, 'the contents must fit on one page'
    w = PdfWriter()
    for pg in PdfReader(toc).pages:
        w.add_page(pg)
    w.add_outline_item('Contents', 0)
    page = 1
    for (_, short, p), n in zip(pdfs, counts):
        for pg in PdfReader(p).pages:
            w.add_page(pg)
        w.add_outline_item(short, page)
        page += n
    w.add_metadata({'/Title': 'CERTAIN-COAST — Additional files', '/Author': 'D. Zeqiraj'})
    with open(out, 'wb') as fh:
        w.write(fh)
    print('saved', out, '|', page, 'pages |', ', '.join(f'{s}: {n}' for (_, s, _), n in zip(pdfs, counts)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Additional_Files.pdf')
