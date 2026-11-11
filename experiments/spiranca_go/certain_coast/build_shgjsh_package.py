"""CERTAIN-COAST: request to the Albanian Geological Survey (SHGJSH) for a letter of commitment as end-user, delivered by
hand, with the letter itself.

Page 1: the NPD's request (Albanian, on the letterhead of the Faculty), with room for the signature and a telephone
number written by hand. Page 2: the letter of commitment for SHGJSH to sign (English, as NATO requires), from
build_letters.py. Page 3: its Albanian reading copy. The concept note is not attached here, because its current
version names the Ministry of Defence as end-user.

usage: python build_shgjsh_package.py OUT.docx"""
import os
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import para  # noqa: E402
from build_letters import run, ph, LETTERS, SQ, letter, letter_sq, page_break  # noqa: E402
from build_ministry_letter import setup, APPLY, WARN, MEET, NAVY, BLUE, GREY  # noqa: E402

DATE = '11.11.2026'
DUE = 'të enjten, 12 nëntor 2026'
BODY = [
    APPLY,
    WARN + 'në dy pjesë të bregut: midis Durrësit dhe Fushë-Kuqes, ku ndodhen fushat e puseve dhe Porti i Durrësit, dhe '
    'afër Fierit, ku gazsjellësi TAP del në breg. **Risia:** çdo paralajmërim deklaron paraprakisht sa shpesh mund të '
    'gabojë. NATO financon rreth €382,500.',
    'NATO kërkon që çdo projekt të ketë të paktën një **përdorues fundor**, i cili merr pjesë në projekt dhe përdor '
    'rezultatet e tij pa marrë fonde nga NATO. Shërbimi Gjeologjik Shqiptar, që administron rrjetin kombëtar të monitorimit '
    'të ujërave nëntokësore dhe punon për rreziqet gjeologjike, është përdoruesi fundor i natyrshëm. Konkretisht, SHGJSH-ja '
    'do të jepte qasje në disa puse ekzistuese të rrjetit në bregun Durrës–Fushë-Kuqe për sensorët e projektit, që i '
    'blen projekti dhe i vendos bashkë me stafin tuaj; të dhënat e nivelit dhe të kimisë, me marrëveshje për të dhënat; '
    'dhe kohë pune të dy ekspertëve, rreth 10 ditë në vit, për vendosjen e sensorëve, pragjet e paralajmërimit dhe '
    'shqyrtimin e buletineve. Në fund të projektit SHGJSH-ja merr softuerin e hapur, projektimin e rrjetit dhe stafin e '
    'trajnuar, dhe mund t\'i mbajë sensorët në rrjetin e vet.',
    f'**Ju lutem për një letër angazhimi si përdorues fundor**, në letrën zyrtare të SHGJSH-së, të firmosur nga titullari '
    f'ose nga një person i autorizuar, **mundësisht deri {DUE}**. Mund ta dërgoni të skanuar në PDF në adresën '
    'dulian.zeqiraj@fgjm.edu.al, ndërsa origjinalin mund ta tërheq vetë. Bashkëngjis tekstin e propozuar të letrës në '
    'anglisht, siç e kërkon NATO, dhe përkthimin e saj në shqip vetëm për lexim; fushat me të verdhë plotësohen nga '
    'SHGJSH-ja, dhe teksti mund të ndryshohet sipas gjykimit tuaj. Pjesëmarrja **nuk krijon asnjë detyrim financiar**: '
    'kontributi është në natyrë dhe SHGJSH-ja nuk merr fonde nga NATO. Të dhënat që jepni trajtohen si të kufizuara dhe '
    'çdo publikim që i përdor ju dërgohet për kontroll para botimit.',
    MEET,
]


def request(doc):
    p = para(doc, 0); run(p, 'UNIVERSITETI POLITEKNIK I TIRANËS', bold=True, size=10, color=NAVY)
    p = para(doc, 10); run(p, 'Fakulteti i Gjeologjisë dhe i Minierave · Departamenti i Burimeve Energjetike', size=9,
                           color=GREY)
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; run(p, f'Tiranë, më {DATE}', size=10.5)
    p = para(doc, 2); run(p, 'Drejtuar: ', bold=True, size=10.5)
    run(p, 'Shërbimit Gjeologjik Shqiptar, Drejtorit të Përgjithshëm', size=10.5)
    p = para(doc, 8); run(p, 'Lënda: ', bold=True, size=10.5)
    run(p, 'Kërkesë për letër angazhimi si përdorues fundor për aplikimin e UPT-së në Programin e NATO-s «Shkenca për '
           'Paqe dhe Siguri» (SPS), projekti CERTAIN-COAST', bold=True, size=10.5, color=BLUE)
    p = para(doc, 5); run(p, 'Të nderuar zonja dhe zotërinj,', size=10.5)
    for t in BODY:
        p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; ph(p, t, size=10.5)
    p = para(doc, 10); run(p, 'Ju falënderoj për mbështetjen.', size=10.5)
    p = para(doc, 0); run(p, 'Me respekt,', size=10.5)
    para(doc, 26)                                       # room for the signature
    p = para(doc, 0); run(p, 'Prof. Asoc. Dr. Dulian Zeqiraj', bold=True, size=10.5)
    for t in ('Drejtues i projektit CERTAIN-COAST (NATO-country Project Director)',
              'Fakulteti i Gjeologjisë dhe i Minierave, Universiteti Politeknik i Tiranës', 'dulian.zeqiraj@fgjm.edu.al',
              'Tel.: ________________________'):
        p = para(doc, 0); run(p, t, size=9, color=GREY)
    p = para(doc, 0, before=8)
    run(p, 'Bashkëlidhur: 1. Teksti i propozuar i letrës së angazhimit (anglisht); 2. Përkthimi në shqip, vetëm për '
           'lexim.', italic=True, size=8.5, color=GREY)


def main(out):
    L = next(x for x in LETTERS if x['key'] == 'shgjsh')
    doc = Document()
    setup(doc)
    request(doc)
    page_break(doc)
    letter(doc, L)
    letter_sq(doc, L, SQ['shgjsh'])
    for par in doc.paragraphs:                          # the English letter is page 2 of this file
        for r in par.runs:
            if '(CERTAIN-COAST_Letters_of_Commitment.docx)' in r.text:
                r.text = r.text.replace('(CERTAIN-COAST_Letters_of_Commitment.docx)', '(faqja 2)')
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Letter_of_Commitment_SHGJSH.docx')
