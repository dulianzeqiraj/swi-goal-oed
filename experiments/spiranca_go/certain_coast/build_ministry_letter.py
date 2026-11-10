"""CERTAIN-COAST: request to the responsible ministry for a letter of support, with the letter itself.

Page 1: the NPD's request to the minister (Albanian, on the letterhead of the Faculty).
Page 2: the letter of support for the ministry to sign (English, as NATO requires), with yellow fields.
Page 3: an Albanian reading copy of page 2.
A letter of support expresses support in principle; it is not an end-user commitment and creates no financial or legal
obligation. The ministry's name, the signatory and the fields of responsibility are placeholders to be checked.

usage: python build_ministry_letter.py OUT.docx"""
import os
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import para  # noqa: E402
from build_letters import run, ph, ADDRESS  # noqa: E402
from fill_agreement_template import TITLE  # noqa: E402

NAVY, BLUE, GREY = '1F3864', '1F4E99', '52606D'
MIN_EN = '[Ministry of Infrastructure and Energy of the Republic of Albania]'
MIN_SQ = '[Ministria e Infrastrukturës dhe Energjisë e Republikës së Shqipërisë]'

EN = [
    f'The {MIN_EN} supports the application of the Polytechnic University of Tirana (Faculty of Geology and Mining), '
    'with Assoc. Prof. Dr. Dulian Zeqiraj as NATO-country Project Director and the Environmental Science Center of Qatar '
    'University (Prof. Jassim Al-Khayat) as partner-country institution, to the NATO Science for Peace and Security '
    f'Programme for the Multi-Year Project **CERTAIN-COAST: {TITLE}** (call 2027-1).',
    'The coastal plain between Durrës and Fushë Kuqe concentrates assets of national importance: wellfields that supply '
    'drinking water, the Port of Durrës and energy infrastructure, on a low coast that is subsiding and exposed to '
    'seawater intrusion, extreme sea levels and earthquakes, as the earthquake of 26 November 2019 showed. Early warnings '
    'that state in advance how often they may be wrong are directly relevant to [the Ministry\'s responsibilities for '
    'water supply, energy and transport infrastructure and geological hazards].',
    'We welcome the role of the Albanian Geological Survey as the project\'s end-user, which will receive the monitoring '
    'network, the open software and trained staff at the end of the project, and we value the training of young '
    'Albanian researchers that the project provides.',
    'The Ministry will follow the project through a designated contact person, receive its results and bulletins, and '
    'take part in its final workshop. This letter expresses support in principle and creates no financial or legal '
    'obligation for the Ministry.',
]

SQ = [
    f'{MIN_SQ} mbështet aplikimin e Universitetit Politeknik të Tiranës (Fakulteti i Gjeologjisë dhe i Minierave), me '
    'Prof. Asoc. Dr. Dulian Zeqiraj si drejtues i projektit nga vendi anëtar i NATO-s dhe me Qendrën e Shkencave '
    'Mjedisore të Universitetit të Katarit (Prof. Jassim Al-Khayat) si institucion i vendit partner, në Programin e '
    'NATO-s «Shkenca për Paqe dhe Siguri» për projektin shumëvjeçar **CERTAIN-COAST** (thirrja 2027-1): paralajmërim i '
    'hershëm i certifikuar për mbrojtjen e infrastrukturës së ujit, të portit dhe të energjisë në një bregdet që po ulet.',
    'Fusha bregdetare midis Durrësit dhe Fushë Kuqes përqendron asete me rëndësi kombëtare: fushat e puseve që furnizojnë '
    'me ujë të pijshëm, Portin e Durrësit dhe infrastrukturën e energjisë, në një breg të ulët që po ulet dhe që është i '
    'ekspozuar ndaj depërtimit të ujit të detit, niveleve ekstreme të detit dhe tërmeteve, siç e tregoi tërmeti i 26 '
    'nëntorit 2019. Paralajmërimet që deklarojnë paraprakisht sa shpesh mund të gabojnë lidhen drejtpërdrejt me '
    '[përgjegjësitë e Ministrisë për furnizimin me ujë, infrastrukturën e energjisë dhe të transportit dhe rreziqet '
    'gjeologjike].',
    'Mirëpresim rolin e Shërbimit Gjeologjik Shqiptar si përdorues fundor i projektit, i cili në fund të projektit do të '
    'marrë rrjetin e monitorimit, softuerin e hapur dhe stafin e trajnuar, dhe vlerësojmë trajnimin e kërkuesve të rinj '
    'shqiptarë që ofron projekti.',
    'Ministria do ta ndjekë projektin përmes një personi kontakti të caktuar, do të marrë rezultatet dhe buletinet e tij '
    'dhe do të marrë pjesë në seminarin përmbyllës. Kjo letër shpreh mbështetje në parim dhe nuk krijon asnjë detyrim '
    'financiar ose ligjor për Ministrinë.',
]


def setup(doc):
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.2); s.top_margin = Cm(1.6); s.bottom_margin = Cm(1.5)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10.5)


def request(doc):
    p = para(doc, 0); run(p, 'UNIVERSITETI POLITEKNIK I TIRANËS', bold=True, size=10, color=NAVY)
    p = para(doc, 10); run(p, 'Fakulteti i Gjeologjisë dhe i Minierave · Departamenti i Burimeve Energjetike', size=9,
                           color=GREY)
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; run(p, 'Tiranë, më 10.11.2026', size=10.5)
    p = para(doc, 2); run(p, 'Drejtuar: ', bold=True, size=10.5)
    ph(p, '[Ministrit / Ministres së Infrastrukturës dhe Energjisë], [emri]', size=10.5)
    p = para(doc, 8); run(p, 'Lënda: ', bold=True, size=10.5)
    run(p, 'Kërkesë për letër mbështetjeje për aplikimin e UPT-së në Programin e NATO-s «Shkenca për Paqe dhe Siguri» '
           '(SPS), projekti CERTAIN-COAST', bold=True, size=10.5, color=BLUE)
    p = para(doc, 5); ph(p, '[I nderuar zoti Ministër / E nderuar zonja Ministre],', size=10.5)
    body = [
        'Universiteti Politeknik i Tiranës aplikon, nëpërmjet Fakultetit të Gjeologjisë dhe të Minierave, në thirrjen '
        '2027-1 të Programit të NATO-s «Shkenca për Paqe dhe Siguri» me projektin shumëvjeçar **CERTAIN-COAST** (36 '
        'muaj), në partneritet me Universitetin e Katarit. Drejtues i projektit për UPT-në jam unë. Afati i dorëzimit '
        'është **e diela, 15 nëntor 2026, ora 23:59**.',
        'Projekti jep paralajmërime të hershme për depërtimin e ujit të detit në puset e ujit të pijshëm, për '
        'lëngëzimin e tokës gjatë tërmeteve dhe për nivelet ekstreme të detit në bregun Durrës–Fushë Kuqe, ku ndodhen '
        'edhe Porti i Durrësit dhe infrastruktura e energjisë. **Risia:** çdo paralajmërim deklaron paraprakisht sa '
        'shpesh mund të gabojë. Përdorues fundor është Shërbimi Gjeologjik Shqiptar, i cili në fund të projektit merr '
        'rrjetin e monitorimit, softuerin e hapur dhe stafin e trajnuar. NATO financon rreth €382,500.',
        'Meqë projekti lidhet drejtpërdrejt me fushat e përgjegjësisë së Ministrisë suaj (furnizimi me ujë, '
        'infrastruktura e energjisë dhe e transportit, rreziqet gjeologjike), një letër mbështetjeje nga Ministria do '
        'ta forconte ndjeshëm aplikimin. **Ju lutem për një letër mbështetjeje**, në letrën zyrtare të Ministrisë, të '
        'firmosur nga ju ose nga një person i autorizuar, **mundësisht deri të premten, 13 nëntor 2026**, të skanuar në '
        'PDF në adresën dulian.zeqiraj@fgjm.edu.al.',
        'Për t\'jua lehtësuar, bashkëngjis tekstin e propozuar të letrës në anglisht, siç e kërkon NATO, dhe përkthimin '
        'e saj në shqip vetëm për lexim; fushat me të verdhë plotësohen nga Ministria, dhe teksti mund të ndryshohet '
        'sipas gjykimit tuaj. Letra shpreh **mbështetje në parim** dhe **nuk krijon asnjë detyrim financiar ose '
        'ligjor** për Ministrinë.',
        'Jam në dispozicion për ta paraqitur projektin në një takim të shkurtër, në çdo orë që ju përshtatet.',
    ]
    for t in body:
        p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; ph(p, t, size=10.5)
    p = para(doc, 10); run(p, 'Ju falënderoj për mbështetjen.', size=10.5)
    p = para(doc, 0); run(p, 'Me respekt,', size=10.5)
    p = para(doc, 0); run(p, 'Prof. Asoc. Dr. Dulian Zeqiraj', bold=True, size=10.5)
    for t in ('Drejtues i projektit CERTAIN-COAST (NATO-country Project Director)',
              'Fakulteti i Gjeologjisë dhe i Minierave, Universiteti Politeknik i Tiranës', 'dulian.zeqiraj@fgjm.edu.al'):
        p = para(doc, 0); run(p, t, size=9, color=GREY)
    p = para(doc, 0, before=8)
    run(p, 'Bashkëlidhur: 1. Teksti i propozuar i letrës së mbështetjes (anglisht); 2. Përkthimi në shqip, vetëm për '
           'lexim; 3. Shënimi i konceptit të projektit (5 faqe).', italic=True, size=8.5, color=GREY)


def support(doc, paras, ministry, en=True):
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.page_break_before = True
    if not en:
        run(p, 'PËRKTHIM PËR LEXIM. Letra që firmoset dhe i dërgohet NATO-s është versioni në anglisht.', italic=True,
            size=9, color=GREY)
        p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, ('[LETTERHEAD OF THE MINISTRY]' if en else '[LETËR ZYRTARE E MINISTRISË]'), bold=True, size=10, hl=True)
    p = para(doc, 0); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    ph(p, '[Tirana], [date]' if en else '[Tiranë], [data]', size=10.5)
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    ph(p, 'Ref. [protocol number]' if en else 'Nr. prot. [numri]', size=10.5)
    for i, line in enumerate(ADDRESS):
        p = para(doc, 0 if i < len(ADDRESS) - 1 else 8); run(p, line, size=10.5)
    p = para(doc, 8)
    if en:
        run(p, 'Subject: ', bold=True, size=10.5)
        run(p, f'Letter of support for the NATO SPS Multi-Year Project application CERTAIN-COAST: {TITLE}', bold=True,
            size=10.5)
    else:
        run(p, 'Lënda: ', bold=True, size=10.5)
        run(p, 'Letër mbështetjeje për aplikimin e projektit shumëvjeçar NATO SPS CERTAIN-COAST', bold=True, size=10.5)
    p = para(doc, 6); run(p, 'Dear Sir or Madam,' if en else 'Të nderuar zonja dhe zotërinj,', size=10.5)
    for t in paras:
        p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; ph(p, t, size=10.5)
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    ph(p, 'Our contact person for the project is [name, position, e-mail, telephone].' if en else
       'Personi ynë i kontaktit për projektin është [emri, pozicioni, e-mail, telefoni].', size=10.5)
    p = para(doc, 12); run(p, 'Yours faithfully,' if en else 'Me respekt,', size=10.5)
    for t in (('[Signature and stamp]', '[Name]', '[Minister / Deputy Minister / Secretary General]', ministry) if en else
              ('[Firma dhe vula]', '[Emri]', '[Ministri / Zëvendësministri / Sekretari i Përgjithshëm]', ministry)):
        p = para(doc, 0); ph(p, t, size=10.5)


def main(out):
    doc = Document()
    setup(doc)
    request(doc)
    support(doc, EN, MIN_EN, en=True)
    support(doc, SQ, MIN_SQ, en=False)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Letter_of_Support_Ministry.docx')
