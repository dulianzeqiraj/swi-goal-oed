"""CERTAIN-COAST: one-page cover note in Albanian for the Rector of the Polytechnic University of Tirana, Prof. Dr. Akli
Fundo, sent with the two NATO templates the Rector signs (SPS MYP Acceptance of Funds; SPS MYP Agreement for Joint Research, already signed
by Qatar University). Figures follow the form and the budget (build_budget.py); nothing is claimed that the form does
not state.

usage: python build_rector_note.py OUT.docx"""
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

NAVY, BLUE, GREY, BOX = '1F3864', '1F4E99', '52606D', 'EEF4FC'
SIZE = 10


def run(p, text, bold=False, italic=False, size=SIZE, color=None):
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    r.font.name = 'Arial'; r.font.size = Pt(size)
    r._element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    return r


def rich(p, text, size=SIZE, color=None):
    for i, seg in enumerate(text.split('**')):
        if seg:
            run(p, seg, bold=i % 2 == 1, size=size, color=color)


def para(doc, after=4, before=0, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after); p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.line_spacing = 1.05
    p.alignment = align
    return p


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), fill)
    tcPr.append(sh)


def widths(t, ws):
    t.autofit = False
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); t._tbl.tblPr.append(lay)
    for gc, w in zip(t._tbl.tblGrid.findall(qn('w:gridCol')), ws):
        gc.set(qn('w:w'), str(int(w * 567)))
    for row in t.rows:
        for c, w in zip(row.cells, ws):
            c.width = Cm(w)


PROJECT = [
    '**Titulli:** CERTAIN-COAST — paralajmërim i hershëm i certifikuar për mbrojtjen e infrastrukturës së ujit, të portit '
    'dhe të energjisë në një bregdet që po ulet; 36 muaj.',
    '**Çfarë bën:** paralajmërime për depërtimin e ujit të detit në puset e ujit të pijshëm, për lëngëzimin e tokës gjatë '
    'tërmeteve dhe për nivelet ekstreme të detit në bregun Durrës–Fushë Kuqe, me një model të përbashkët dhe me '
    'inteligjencë artificiale që deklaron paraprakisht sa shpesh mund të gabojë.',
    '**Risia:** çdo alarm jepet me një garanci të deklaruar paraprakisht për shpeshtësinë e alarmeve të rreme dhe të '
    'humbura, që përdoruesi ta dijë sa t\'i besojë para se të veprojë.',
    '**Partnerët:** Qatar University (Environmental Science Center), nga një vend partner i NATO-s; përdorues fundor '
    'është Shërbimi Gjeologjik Shqiptar.',
    '**Buxheti:** NATO financon €382,500, nga të cilat rreth €313,500 i administron UPT (pajisje monitorimi, analiza, '
    'bursa për kërkues të rinj, trajnime, udhëtime dhe botime) dhe rreth €69,000 Qatar University. Buxheti mbulon vetëm '
    'shpenzime të projektit: pagat e rregullta të stafit dhe shpenzimet e përgjithshme mbeten kontribut në natyrë i '
    'UPT-së. Nuk kërkohet bashkëfinancim në para.',
]

SIGN = [
    ['1. SPS MYP Acceptance of Funds\n(formular zyrtar i NATO-s, 1 faqe)',
     'Që, nëse projekti fitohet, UPT i pranon dhe i administron fondet e NATO-s sipas buxhetit të miratuar dhe rregullave '
     'të Manualit SPS. Pa këtë dokument aplikimi nuk shqyrtohet.',
     'Drejtuesi i projektit dhe Rektori (ose Autoriteti Financiar)'],
    ['2. SPS MYP Agreement for Joint Research\n(formular zyrtar i NATO-s, 1 faqe)',
     'Bashkëpunimin me Qatar University, e cila e ka firmosur tashmë më 5 nëntor 2026. Firmat e UPT-së vendosen në të '
     'njëjtën faqe.',
     'Drejtuesi i projektit dhe Rektori'],
]


def main(out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.2); s.top_margin = Cm(1.6); s.bottom_margin = Cm(1.4)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(SIZE)

    p = para(doc, 0, align=WD_ALIGN_PARAGRAPH.LEFT)
    run(p, 'UNIVERSITETI POLITEKNIK I TIRANËS', bold=True, size=10, color=NAVY)
    p = para(doc, 8, align=WD_ALIGN_PARAGRAPH.LEFT)
    run(p, 'Fakulteti i Gjeologjisë dhe i Minierave · Departamenti i Burimeve Energjetike', size=9, color=GREY)
    p = para(doc, 6, align=WD_ALIGN_PARAGRAPH.RIGHT); run(p, 'Tiranë, më 10.11.2026')
    p = para(doc, 2, align=WD_ALIGN_PARAGRAPH.LEFT); run(p, 'Drejtuar: ', bold=True); run(p, 'Prof. Dr. Akli Fundo, Rektor i Universitetit Politeknik të Tiranës')
    p = para(doc, 8, align=WD_ALIGN_PARAGRAPH.LEFT)
    run(p, 'Lënda: ', bold=True)
    run(p, 'Kërkesë për firmë – aplikimi i UPT-së në Programin e NATO-s «Shkenca për Paqe dhe Siguri» (SPS), projekti '
           'CERTAIN-COAST', bold=True, color=BLUE)
    p = para(doc, 4); run(p, 'I nderuar z. Rektor,')
    p = para(doc, 6)
    rich(p, 'Universiteti Politeknik i Tiranës aplikon, nëpërmjet Fakultetit të Gjeologjisë dhe të Minierave, në thirrjen '
            '2027-1 të Programit të NATO-s «Science for Peace and Security» (SPS) për projekte shumëvjeçare. Afati i '
            'dorëzimit është **e diela, 15 nëntor 2026, ora 23:59 (CET)**. Drejtues i projektit për UPT-në (NATO-country '
            'Project Director) jam unë, Prof. Asoc. Dr. Dulian Zeqiraj.')

    t = doc.add_table(rows=1, cols=1); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.rows[0].cells[0]; shade(c, BOX); widths(t, [16.6])
    q = c.paragraphs[0]; q.paragraph_format.space_after = Pt(3)
    run(q, 'Projekti me pak fjalë', bold=True, size=10, color=NAVY)
    for x in PROJECT:
        q = c.add_paragraph(); q.paragraph_format.space_after = Pt(2); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        q.paragraph_format.left_indent = Cm(0.3)
        run(q, '• ', size=9.5); rich(q, x, size=9.5)
    para(doc, 4)

    p = para(doc, 3, align=WD_ALIGN_PARAGRAPH.LEFT); run(p, 'Çfarë ju lutem të firmosni', bold=True, size=10.5, color=NAVY)
    t = doc.add_table(rows=1, cols=3); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c, h in zip(t.rows[0].cells, ['Dokumenti', 'Çfarë konfirmon', 'Kush firmos']):
        shade(c, NAVY); q = c.paragraphs[0]; run(q, h, bold=True, size=9, color='FFFFFF')
    for row in SIGN:
        cells = t.add_row().cells
        for c, x in zip(cells, row):
            q = c.paragraphs[0]; q.paragraph_format.space_after = Pt(1)
            lines = x.split('\n')
            run(q, lines[0], bold=c is cells[0], size=9)
            for ln in lines[1:]:
                q2 = c.add_paragraph(); run(q2, ln, size=8.5, color=GREY)
    widths(t, [5.0, 7.6, 4.0])
    p = para(doc, 6, before=3)
    run(p, 'Rregullat financiare: sipas Drejtorisë së Financës (10.11.2026), UPT nuk ka rregullore të veçantë dhe zbaton '
           'kuadrin ligjor në fuqi, përfshirë Udhëzimin e Ministrisë së Financave nr. 10, datë 12.07.2024, për fondet e '
           'financimeve të huaja; këto citohen në aplikim bashkë me Statutin e UPT-së.', size=9, color=GREY, italic=True)

    p = para(doc, 6)
    rich(p, 'Ju lutem **firmën dhe vulën** në të dy dokumentet, nëse është e mundur **deri të enjten, 12 nëntor 2026**, '
            'dhe një kopje të skanuar në PDF në adresën dulian.zeqiraj@fgjm.edu.al, që të ngarkohet në platformën e NATO-s '
            'bashkë me aplikimin. Firma nuk krijon detyrim financiar për UPT-në përtej administrimit të fondeve të NATO-s, '
            'nëse projekti fitohet.')
    p = para(doc, 10); run(p, 'Ju falënderoj për mbështetjen.')
    p = para(doc, 0, align=WD_ALIGN_PARAGRAPH.LEFT); run(p, 'Me respekt,')
    p = para(doc, 0, align=WD_ALIGN_PARAGRAPH.LEFT); run(p, 'Prof. Asoc. Dr. Dulian Zeqiraj', bold=True)
    p = para(doc, 0, align=WD_ALIGN_PARAGRAPH.LEFT)
    run(p, 'Drejtues i projektit CERTAIN-COAST · Fakulteti i Gjeologjisë dhe i Minierave', size=9, color=GREY)
    p = para(doc, 0, align=WD_ALIGN_PARAGRAPH.LEFT); run(p, 'dulian.zeqiraj@fgjm.edu.al', size=9, color=GREY)
    p = para(doc, 0, before=6, align=WD_ALIGN_PARAGRAPH.LEFT)
    run(p, 'Bashkëlidhur: 1. SPS MYP Acceptance of Funds; 2. SPS MYP Agreement for Joint Research (e firmosur nga Qatar '
           'University).', size=8.5, color=GREY, italic=True)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Shenim_per_Rektorin.docx')
