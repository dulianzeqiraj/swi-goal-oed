"""CERTAIN-COAST: request to the Ministry of Environment of Albania for a letter of support and end-user commitment.

Page 1: the NPD's request (Albanian, on the letterhead of the Faculty), addressed to the Minister of Environment, with
        room for a signature in ink, so that it can be sent by e-mail or delivered by hand.
Page 2: the letter for the Ministry to sign (English, as NATO requires): one page, six fields (date, reference, contact
        person, signature and stamp, name, position); any official authorised by the Ministry may sign.
Page 3: an Albanian reading copy of page 2.
The SPS call 2027-1 and the MYP Handbook list the end-user commitment among the documents submitted with the proposal,
so the signed letter is needed before the deadline. The Minister (Sofjan Jaupaj, in office since September 2025) is
named as listed on the Ministry's website and on Wikipedia, checked on 12 November 2026.

usage: python build_environment_letter.py OUT.docx"""
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
SIZE = 10.5
DATE = '12.11.2026'
MIN_EN = 'Ministry of Environment of the Republic of Albania'
MIN_SQ = 'Ministria e Mjedisit e Republikës së Shqipërisë'
CODE = 'github.com/dulianzeqiraj/certain-coast; DOI 10.5281/zenodo.24148762'

REQUEST = dict(
    to='Z. Sofjan Jaupaj, Ministër i Mjedisit',
    subject='Kërkesë për letër mbështetjeje dhe angazhimi si përdorues fundor – projekti NATO SPS «CERTAIN-COAST»',
    greeting='I nderuar z. Ministër,',
    body=[
        'Universiteti Politeknik i Tiranës aplikon, nëpërmjet Fakultetit të Gjeologjisë dhe të Minierave, në thirrjen '
        '2027-1 të Programit të NATO-s «Shkenca për Paqe dhe Siguri» (SPS) me projektin shumëvjeçar **CERTAIN-COAST** (36 '
        'muaj), me partner Qendrën e Shkencave Mjedisore të Universitetit të Katarit. Drejtues i projektit jam unë, Prof. '
        'Asoc. Dr. Dulian Zeqiraj. Afati i dorëzimit në NATO është **e diela, 15 nëntor 2026, ora 23:59**.',
        'Projekti jep paralajmërime të hershme për depërtimin e ujit të detit në akuiferët që furnizojnë me ujë të pijshëm, '
        'për lëngëzimin e tokës gjatë tërmeteve dhe për nivelet ekstreme të detit në bregdetin e ulët adriatik, në Durrës '
        'dhe afër Fierit, një bregdet që po ulet. **Risia:** çdo paralajmërim deklaron paraprakisht sa shpesh mund të '
        'gabojë, dhe kjo verifikohet gjatë 12 muajve të funksionimit. Modelimin dhe algoritmin e paralajmërimeve i bën '
        f'drejtuesi i projektit; ato publikohen si kod i hapur ({CODE}).',
        'Kripëzimi i ujërave nëntokësore, ulja e bregut dhe nivelet ekstreme të detit janë çështje të mjedisit bregdetar. '
        'Prandaj do të ishte shumë e rëndësishme që **Ministria e Mjedisit të marrë pjesë në projekt si përdorues fundor '
        '(end-user)**. NATO kërkon një letër angazhimi nga çdo përdorues fundor, e cila dorëzohet bashkë me aplikimin. '
        'Ministria do të caktojë një person kontakti; stafi i saj do të marrë pjesë në mbledhjet drejtuese, do të bjerë '
        'dakord me ekipin për pragjet e paralajmërimit, do të shqyrtojë buletinet dhe do të trajnohet për përdorimin e '
        'kodit. Pjesëmarrja nuk krijon asnjë detyrim financiar; kontributi është vetëm koha e stafit.',
        '**Ju lutem për letrën e mbështetjes dhe të angazhimit** që gjeni bashkëngjitur: faqja 2 është në anglisht, siç e '
        'kërkon NATO, dhe faqja 3 është përkthimi në shqip, vetëm për lexim. Ju lutem ta hidhni në letrën zyrtare të '
        'Ministrisë, ta plotësoni (data, numri i protokollit, personi i kontaktit) dhe ta firmosni e vulosni ju ose një '
        'zyrtar i autorizuar. Teksti mund të ndryshohet sipas asaj që Ministria mund të angazhohet. Kopjen e skanuar në '
        'PDF ju lutem ta dërgoni në adresën dulian.zeqiraj@fgjm.edu.al, **mundësisht deri të premten, 13 nëntor 2026**, '
        'që të ngarkohet në platformën e NATO-s bashkë me aplikimin.',
        'Jam në dispozicion për ta paraqitur projektin në një takim të shkurtër, në çdo orë që ju përshtatet.'],
    attach='Bashkëlidhur: letra e mbështetjes dhe e angazhimit si përdorues fundor (anglisht, për firmë) dhe përkthimi '
           'i saj në shqip.')

EN = dict(
    head='[LETTERHEAD OF THE MINISTRY]', place='Tirana, [date]', ref='Ref. [protocol number]',
    subject=('Subject: ', 'CERTAIN-COAST, application to the NATO SPS Programme for a Multi-Year Project (call '
                          '2027-1): letter of support and end-user commitment'),
    greeting='Dear Sir or Madam,',
    body=[
        f'The {MIN_EN} supports the application of the Polytechnic University of Tirana (NATO-country Project Director: '
        'Assoc. Prof. Dr. Dulian Zeqiraj), with the Environmental Science Center of Qatar University, to the NATO Science '
        f'for Peace and Security Programme for the Multi-Year Project **CERTAIN-COAST: {TITLE}**.',
        'The project addresses threats to the environment of Albania\'s low Adriatic coast at Durrës and near Fier: '
        'seawater intrusion into the aquifers that supply drinking water, subsidence of the coast, extreme sea levels and '
        'earthquake-induced liquefaction. Its warnings state in advance how often they may be wrong, and its model and '
        'warning algorithm will be released as open-source code. The project is relevant to the Ministry\'s '
        'responsibilities for the protection of the environment.',
        'The Ministry will take part in the project as an end-user. Our contact person will be [name, position, e-mail]. '
        'Our staff will take part in the project\'s steering meetings, agree the warning thresholds with the project team, '
        'review the warning bulletins and take part in the training, as our resources allow.',
        'The Ministry\'s contribution is staff time in kind; the Ministry receives no SPS funds, and this letter creates no '
        'financial obligation for it.'],
    close='Yours faithfully,', sign=['[Signature and stamp]', '[Name]', '[Position]', MIN_EN])

SQ = dict(
    note='PËRKTHIM PËR LEXIM. Letra që firmoset dhe i dërgohet NATO-s është versioni në anglisht.',
    head='[LETËR ZYRTARE E MINISTRISË]', place='Tiranë, [data]', ref='Nr. prot. [numri]',
    subject=('Lënda: ', 'CERTAIN-COAST, aplikim në Programin NATO SPS për projekt shumëvjeçar (thirrja 2027-1): '
                        'letër mbështetjeje dhe angazhimi si përdorues fundor'),
    greeting='Të nderuar zonja dhe zotërinj,',
    body=[
        f'{MIN_SQ} mbështet aplikimin e Universitetit Politeknik të Tiranës (drejtues i projektit: Prof. Asoc. Dr. Dulian '
        'Zeqiraj), bashkë me Qendrën e Shkencave Mjedisore të Universitetit të Katarit, në Programin e NATO-s «Shkenca '
        'për Paqe dhe Siguri» për projektin shumëvjeçar **CERTAIN-COAST**: paralajmërim i hershëm i certifikuar për '
        'mbrojtjen e infrastrukturës së ujit, të portit dhe të energjisë në një bregdet që po ulet.',
        'Projekti trajton kërcënime për mjedisin e bregdetit të ulët adriatik të Shqipërisë, në Durrës dhe afër Fierit: '
        'depërtimin e ujit të detit në akuiferët që furnizojnë me ujë të pijshëm, uljen e bregut, nivelet ekstreme të '
        'detit dhe lëngëzimin e tokës gjatë tërmeteve. Paralajmërimet e tij deklarojnë paraprakisht sa shpesh mund të '
        'gabojnë, dhe modeli e algoritmi i paralajmërimeve do të publikohen si kod i hapur. Projekti lidhet me '
        'përgjegjësitë e Ministrisë për mbrojtjen e mjedisit.',
        'Ministria do të marrë pjesë në projekt si përdorues fundor. Personi ynë i kontaktit do të jetë [emri, pozicioni, '
        'e-mail]. Stafi ynë do të marrë pjesë në mbledhjet drejtuese të projektit, do të bjerë dakord me ekipin e '
        'projektit për pragjet e paralajmërimit, do të shqyrtojë buletinet e paralajmërimit dhe do të marrë pjesë në '
        'trajnime, sipas mundësive tona.',
        'Kontributi i Ministrisë është koha e punës së stafit; Ministria nuk merr fonde nga NATO, dhe kjo letër nuk krijon '
        'asnjë detyrim financiar për të.'],
    close='Me respekt,', sign=['[Firma dhe vula]', '[Emri]', '[Pozicioni]', MIN_SQ])


def request(doc, r):
    p = para(doc, 0); run(p, 'UNIVERSITETI POLITEKNIK I TIRANËS', bold=True, size=10, color=NAVY)
    p = para(doc, 10); run(p, 'Fakulteti i Gjeologjisë dhe i Minierave · Departamenti i Burimeve Energjetike', size=9,
                           color=GREY)
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; run(p, f'Tiranë, më {DATE}', size=SIZE)
    p = para(doc, 3); run(p, 'Drejtuar: ', bold=True, size=SIZE); run(p, r['to'], size=SIZE)
    p = para(doc, 8); run(p, 'Lënda: ', bold=True, size=SIZE); run(p, r['subject'], bold=True, size=SIZE, color=BLUE)
    p = para(doc, 5); run(p, r['greeting'], size=SIZE)
    for t in r['body']:
        p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.line_spacing = 1.05
        ph(p, t, size=SIZE)
    p = para(doc, 8); run(p, 'Ju falënderoj për mbështetjen.', size=SIZE)
    p = para(doc, 0); run(p, 'Me respekt,', size=SIZE)
    para(doc, 22)                                         # room for a signature in ink
    p = para(doc, 0); run(p, 'Prof. Asoc. Dr. Dulian Zeqiraj', bold=True, size=SIZE)
    for t in ['Drejtues i projektit CERTAIN-COAST (NATO-country Project Director)',
              'Fakulteti i Gjeologjisë dhe i Minierave, Universiteti Politeknik i Tiranës', 'dulian.zeqiraj@fgjm.edu.al']:
        p = para(doc, 0); run(p, t, size=9, color=GREY)
    p = para(doc, 0, before=8); run(p, r['attach'], italic=True, size=8.5, color=GREY)


def letter(doc, L, en):
    p = para(doc, 4 if not en else 10); p.paragraph_format.page_break_before = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if not en:
        run(p, L['note'], italic=True, size=9, color=GREY)
        p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, L['head'], bold=True, size=10, hl=True)
    p = para(doc, 0); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; ph(p, L['place'], size=SIZE)
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; ph(p, L['ref'], size=SIZE)
    for i, line in enumerate(ADDRESS):
        p = para(doc, 0 if i < len(ADDRESS) - 1 else 10); run(p, line, size=SIZE)
    p = para(doc, 10); run(p, L['subject'][0], bold=True, size=SIZE); run(p, L['subject'][1], bold=True, size=SIZE)
    p = para(doc, 6); run(p, L['greeting'], size=SIZE)
    for t in L['body']:
        p = para(doc, 7); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.line_spacing = 1.1
        ph(p, t, size=SIZE)
    p = para(doc, 14, before=4); run(p, L['close'], size=SIZE)
    for t in L['sign']:
        p = para(doc, 0); ph(p, t, size=SIZE)


def main(out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.3); s.top_margin = Cm(1.8); s.bottom_margin = Cm(1.6)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(SIZE)
    request(doc, REQUEST)
    letter(doc, EN, True)
    letter(doc, SQ, False)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Letter_of_Support_Ministry_of_Environment.docx')
