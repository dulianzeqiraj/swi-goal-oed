"""CERTAIN-COAST: short end-user letter of the Ministry of Infrastructure and Energy, for a quick signature.

The SPS call 2027-1 and the MYP Handbook list the end-user commitment among the documents that must be submitted with
the proposal (only the IPR agreement may follow after approval), so the letter cannot come after the deadline. This is
the shortest form that still gives what the Handbook asks: a statement of interest and the end-user's involvement.
Page 1: the letter in English, to sign (five fields: date, reference, signature and stamp, name, position).
Page 2: an Albanian reading copy. Any official authorised by the Ministry may sign.

usage: python build_ministry_letter_short.py OUT.docx"""
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

GREY = '52606D'
MIN_EN = 'Ministry of Infrastructure and Energy of the Republic of Albania'
MIN_SQ = 'Ministria e Infrastrukturës dhe Energjisë e Republikës së Shqipërisë'
CONTACT = 'Dr. Lusien Ismaili'

EN = dict(
    head='[LETTERHEAD OF THE MINISTRY]', place='Tirana, [date]', ref='Ref. [protocol number]',
    subject=('Subject: ', 'CERTAIN-COAST, application to the NATO SPS Programme for a Multi-Year Project (call '
                          '2027-1): end-user commitment'),
    greeting='Dear Sir or Madam,',
    body=[
        f'The {MIN_EN} supports the application of the Polytechnic University of Tirana (NATO-country Project Director: '
        'Assoc. Prof. Dr. Dulian Zeqiraj), with the Environmental Science Center of Qatar University, to the NATO Science '
        f'for Peace and Security Programme for the Multi-Year Project **CERTAIN-COAST: {TITLE}**.',
        'We are interested in its results: early warnings of seawater intrusion into drinking-water wells, of '
        'earthquake-induced liquefaction and of extreme sea levels on Albania\'s Adriatic coast at Durrës and near Fier, '
        'each stating in advance how often it may be wrong.',
        f'The Ministry will take part in the project as its end-user. Our contact person will be {CONTACT}. Our staff will '
        'take part in the project\'s steering meetings, agree the warning thresholds with the project team and review '
        'the warning bulletins, as our resources allow.',
        'The Ministry\'s contribution is staff time in kind; the Ministry receives no SPS funds, and this letter creates no '
        'financial obligation for it.'],
    close='Yours faithfully,', sign=['[Signature and stamp]', '[Name]', '[Position]', MIN_EN])

SQ = dict(
    note='PËRKTHIM PËR LEXIM. Letra që firmoset dhe i dërgohet NATO-s është versioni në anglisht.',
    head='[LETËR ZYRTARE E MINISTRISË]', place='Tiranë, [data]', ref='Nr. prot. [numri]',
    subject=('Lënda: ', 'CERTAIN-COAST, aplikim në Programin NATO SPS për projekt shumëvjeçar (thirrja 2027-1): '
                        'angazhim si përdorues fundor'),
    greeting='Të nderuar zonja dhe zotërinj,',
    body=[
        f'{MIN_SQ} mbështet aplikimin e Universitetit Politeknik të Tiranës (drejtues i projektit: Prof. Asoc. Dr. Dulian '
        'Zeqiraj), bashkë me Qendrën e Shkencave Mjedisore të Universitetit të Katarit, në Programin e NATO-s «Shkenca '
        'për Paqe dhe Siguri» për projektin shumëvjeçar **CERTAIN-COAST**: paralajmërim i hershëm i certifikuar për '
        'mbrojtjen e infrastrukturës së ujit, të portit dhe të energjisë në një bregdet që po ulet.',
        'Jemi të interesuar për rezultatet e tij: paralajmërime të hershme për depërtimin e ujit të detit në puset e ujit '
        'të pijshëm, për lëngëzimin e tokës gjatë tërmeteve dhe për nivelet ekstreme të detit në bregdetin adriatik të '
        'Shqipërisë, në Durrës dhe afër Fierit, ku secili paralajmërim deklaron paraprakisht sa shpesh mund të gabojë.',
        f'Ministria do të marrë pjesë në projekt si përdorues fundor i tij. Personi ynë i kontaktit do të jetë {CONTACT}. '
        'Stafi ynë do të marrë pjesë në mbledhjet drejtuese të projektit, do të bjerë dakord me ekipin e projektit për '
        'pragjet e paralajmërimit dhe do të shqyrtojë buletinet e paralajmërimit, sipas mundësive tona.',
        'Kontributi i Ministrisë është koha e punës së stafit; Ministria nuk merr fonde nga NATO, dhe kjo letër nuk krijon '
        'asnjë detyrim financiar për të.'],
    close='Me respekt,', sign=['[Firma dhe vula]', '[Emri]', '[Pozicioni]', MIN_SQ])


def letter(doc, L, first):
    if not first:
        p = para(doc, 4); p.paragraph_format.page_break_before = True; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run(p, L['note'], italic=True, size=9, color=GREY)
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, L['head'], bold=True, size=10, hl=True)
    p = para(doc, 0); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; ph(p, L['place'], size=10.5)
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; ph(p, L['ref'], size=10.5)
    for i, line in enumerate(ADDRESS):
        p = para(doc, 0 if i < len(ADDRESS) - 1 else 10); run(p, line, size=10.5)
    p = para(doc, 10); run(p, L['subject'][0], bold=True, size=10.5); run(p, L['subject'][1], bold=True, size=10.5)
    p = para(doc, 6); run(p, L['greeting'], size=10.5)
    for t in L['body']:
        p = para(doc, 7); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.line_spacing = 1.1
        ph(p, t, size=10.5)
    p = para(doc, 14, before=4); run(p, L['close'], size=10.5)
    for t in L['sign']:
        p = para(doc, 0); ph(p, t, size=10.5)


def main(out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.4); s.top_margin = Cm(2.0); s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10.5)
    letter(doc, EN, True)
    letter(doc, SQ, False)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_End-User_Letter_Ministry_Short.docx')
