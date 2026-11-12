"""CERTAIN-COAST: request for a letter of support and end-user commitment, with the letter itself, for one end-user.

Variants:
  environment  the Ministry of Environment of Albania, addressed to the Minister, Sofjan Jaupaj (as listed on the
               Ministry's website and on Wikipedia, checked on 12 November 2026);
  durres       the Municipality of Durrës, addressed to the Mayor, Emiriana Sako (as listed on the Municipality's
               website, checked on 12 November 2026);
  ukd          Ujësjellës Kanalizime Durrës sh.a., the water supply and sewerage company of Durrës, addressed to its
               head (no name: we have no named contact there);
  tirana       the Municipality of Tirana, addressed to the office of the Mayor (no name: the press reports in 2026 that
               the elected mayor is detained and who leads the Municipality is disputed); a weaker link than Durrës.
Page 1: the NPD's request (Albanian, on the letterhead of the Faculty), with room for a signature in ink, so that it can
        be sent by e-mail or delivered by hand.
Page 2: the letter for the end-user to sign (English, as NATO requires): one page, six fields (date, reference, contact
        person, signature and stamp, name, position); any authorised person may sign.
Page 3: an Albanian reading copy of page 2.
The SPS call 2027-1 and the MYP Handbook list the end-user commitment among the documents submitted with the proposal,
and the Handbook counts state organisations, regional authorities and companies among the possible end-users.

usage: python build_enduser_letter.py OUT.docx [environment|durres|ukd|tirana]"""
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
CODE = 'github.com/dulianzeqiraj/certain-coast; DOI 10.5281/zenodo.24148762'
SUBJECT_SQ = 'Kërkesë për letër mbështetjeje dhe angazhimi si përdorues fundor – projekti NATO SPS «CERTAIN-COAST»'
ATTACH = ('Bashkëlidhur: letra e mbështetjes dhe e angazhimit si përdorues fundor (anglisht, për firmë) dhe përkthimi i saj '
          'në shqip.')
NOTE = 'PËRKTHIM PËR LEXIM. Letra që firmoset dhe i dërgohet NATO-s është versioni në anglisht.'

# --- paragraphs shared by the requests (page 1) ---------------------------------------------------------------------
APPLY = ('Universiteti Politeknik i Tiranës aplikon, nëpërmjet Fakultetit të Gjeologjisë dhe të Minierave, në thirrjen '
         '2027-1 të Programit të NATO-s «Shkenca për Paqe dhe Siguri» (SPS) me projektin shumëvjeçar **CERTAIN-COAST** (36 '
         'muaj), me partner Qendrën e Shkencave Mjedisore të Universitetit të Katarit. Drejtues i projektit jam unë, Prof. '
         'Asoc. Dr. Dulian Zeqiraj. Afati i dorëzimit në NATO është **e diela, 15 nëntor 2026, ora 23:59**.')
WHAT = ('Projekti jep paralajmërime të hershme për depërtimin e ujit të detit në akuiferët që furnizojnë me ujë të pijshëm, '
        'për lëngëzimin e tokës gjatë tërmeteve dhe për nivelet ekstreme të detit në bregdetin e ulët adriatik, në Durrës '
        'dhe afër Fierit, një bregdet që po ulet. **Risia:** çdo paralajmërim deklaron paraprakisht sa shpesh mund të '
        'gabojë, dhe kjo verifikohet gjatë 12 muajve të funksionimit. Modelimin dhe algoritmin e paralajmërimeve i bën '
        f'drejtuesi i projektit; ato publikohen si kod i hapur ({CODE}).')
NATO_ASKS = 'NATO kërkon një letër angazhimi nga çdo përdorues fundor, e cila dorëzohet bashkë me aplikimin.'
ROLE_SQ = ('{who} do të caktojë një person kontakti; stafi i saj do të marrë pjesë në mbledhjet drejtuese, do të bjerë '
           'dakord me ekipin për pragjet e paralajmërimit, do të shqyrtojë buletinet dhe do të trajnohet për përdorimin e '
           'kodit.')
FREE = 'Pjesëmarrja nuk krijon asnjë detyrim financiar; kontributi është vetëm koha e stafit.'
MEET = 'Jam në dispozicion për ta paraqitur projektin në një takim të shkurtër, në çdo orë që ju përshtatet.'


def ask(letterhead, signer):
    return ('**Ju lutem për letrën e mbështetjes dhe të angazhimit** që gjeni bashkëngjitur: faqja 2 është në anglisht, siç e '
            'kërkon NATO, dhe faqja 3 është përkthimi në shqip, vetëm për lexim. Ju lutem ta hidhni në letrën zyrtare të '
            f'{letterhead}, ta plotësoni (data, numri i protokollit, personi i kontaktit) dhe ta firmosni e vulosni {signer}. '
            f'Teksti mund të ndryshohet sipas asaj që {letterhead_short(letterhead)} mund të angazhohet. Kopjen e skanuar '
            'në PDF ju lutem ta dërgoni në adresën dulian.zeqiraj@fgjm.edu.al, **mundësisht deri të premten, 13 nëntor '
            '2026**, që të ngarkohet në platformën e NATO-s bashkë me aplikimin.')


def letterhead_short(letterhead):
    return {'Ministrisë': 'Ministria', 'Bashkisë': 'Bashkia', 'shoqërisë': 'shoqëria'}[letterhead]


# --- paragraphs shared by the letters (pages 2 and 3) ---------------------------------------------------------------
def supports_en(org):
    return (f'{org} supports the application of the Polytechnic University of Tirana (NATO-country Project Director: '
            'Assoc. Prof. Dr. Dulian Zeqiraj), with the Environmental Science Center of Qatar University, to the NATO '
            f'Science for Peace and Security Programme for the Multi-Year Project **CERTAIN-COAST: {TITLE}**.')


def supports_sq(org):
    return (f'{org} mbështet aplikimin e Universitetit Politeknik të Tiranës (drejtues i projektit: Prof. Asoc. Dr. Dulian '
            'Zeqiraj), bashkë me Qendrën e Shkencave Mjedisore të Universitetit të Katarit, në Programin e NATO-s «Shkenca '
            'për Paqe dhe Siguri» për projektin shumëvjeçar **CERTAIN-COAST**: paralajmërim i hershëm i certifikuar për '
            'mbrojtjen e infrastrukturës së ujit, të portit dhe të energjisë në një bregdet që po ulet.')


def letter_en(head, place, org, body, signed_by):
    return dict(head=head, place=place, ref='Ref. [protocol number]',
                subject=('Subject: ', 'CERTAIN-COAST, application to the NATO SPS Programme for a Multi-Year Project (call '
                                      '2027-1): letter of support and end-user commitment'),
                greeting='Dear Sir or Madam,', body=[supports_en(org)] + body,
                close='Yours faithfully,', sign=['[Signature and stamp]', '[Name]', '[Position]', signed_by])


def letter_sq(head, place, org, body, signed_by):
    return dict(note=NOTE, head=head, place=place, ref='Nr. prot. [numri]',
                subject=('Lënda: ', 'CERTAIN-COAST, aplikim në Programin NATO SPS për projekt shumëvjeçar (thirrja 2027-1): '
                                    'letër mbështetjeje dhe angazhimi si përdorues fundor'),
                greeting='Të nderuar zonja dhe zotërinj,', body=[supports_sq(org)] + body,
                close='Me respekt,', sign=['[Firma dhe vula]', '[Emri]', '[Pozicioni]', signed_by])


# --- the Ministry of Environment ------------------------------------------------------------------------------------
MOE_EN = 'Ministry of Environment of the Republic of Albania'
MOE_SQ = 'Ministria e Mjedisit e Republikës së Shqipërisë'
ENVIRONMENT = dict(
    out='CERTAIN-COAST_Letter_of_Support_Ministry_of_Environment.docx',
    request=dict(
        to='Z. Sofjan Jaupaj, Ministër i Mjedisit', greeting='I nderuar z. Ministër,',
        body=[APPLY, WHAT,
              'Kripëzimi i ujërave nëntokësore, ulja e bregut dhe nivelet ekstreme të detit janë çështje të mjedisit '
              'bregdetar. Prandaj do të ishte shumë e rëndësishme që **Ministria e Mjedisit të marrë pjesë në projekt si '
              f'përdorues fundor (end-user)**. {NATO_ASKS} {ROLE_SQ.format(who="Ministria")} {FREE}',
              ask('Ministrisë', 'ju ose një zyrtar i autorizuar'), MEET]),
    en=letter_en('[LETTERHEAD OF THE MINISTRY]', 'Tirana, [date]', f'The {MOE_EN}', [
        'The project addresses threats to the environment of Albania\'s low Adriatic coast at Durrës and near Fier: '
        'seawater intrusion into the aquifers that supply drinking water, subsidence of the coast, extreme sea levels and '
        'earthquake-induced liquefaction. Its warnings state in advance how often they may be wrong, and its model and '
        'warning algorithm will be released as open-source code. The project is relevant to the Ministry\'s '
        'responsibilities for the protection of the environment.',
        'The Ministry will take part in the project as an end-user. Our contact person will be [name, position, e-mail]. '
        'Our staff will take part in the project\'s steering meetings, agree the warning thresholds with the project team, '
        'review the warning bulletins and take part in the training, as our resources allow.',
        'The Ministry\'s contribution is staff time in kind; the Ministry receives no SPS funds, and this letter creates no '
        'financial obligation for it.'], MOE_EN),
    sq=letter_sq('[LETËR ZYRTARE E MINISTRISË]', 'Tiranë, [data]', MOE_SQ, [
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
        'asnjë detyrim financiar për të.'], MOE_SQ))

# --- the Municipality of Durrës -------------------------------------------------------------------------------------
DURRES = dict(
    out='CERTAIN-COAST_Letter_of_Support_Municipality_of_Durres.docx',
    request=dict(
        to='Znj. Emiriana Sako, Kryetare e Bashkisë Durrës', greeting='E nderuar znj. Kryetare,',
        body=[APPLY, WHAT,
              'Durrësi është në qendër të projektit: bregu i tij i ulët po ulet, dhe porti, puset që e furnizojnë me ujë të '
              'pijshëm dhe banorët e tij janë të ekspozuar ndaj depërtimit të ujit të detit, niveleve ekstreme të detit dhe '
              'tërmeteve, siç e tregoi tërmeti i 26 nëntorit 2019. Prandaj do të ishte shumë e rëndësishme që **Bashkia '
              f'Durrës të marrë pjesë në projekt si përdorues fundor (end-user)**. {NATO_ASKS} '
              f'{ROLE_SQ.format(who="Bashkia")} {FREE}',
              ask('Bashkisë', 'ju ose një zyrtar i autorizuar'), MEET]),
    en=letter_en('[LETTERHEAD OF THE MUNICIPALITY]', 'Durrës, [date]', 'The Municipality of Durrës', [
        'Durrës is at the centre of the project. Its low coast is subsiding, and its port, the wells that supply it with '
        'drinking water and its citizens are exposed to seawater intrusion, extreme sea levels and earthquakes, as the '
        'earthquake of 26 November 2019 showed. The project\'s warnings state in advance how often they may be wrong, '
        'and its model and warning algorithm will be released as open-source code. The project is relevant to the '
        'Municipality\'s responsibilities for the safety of its citizens and of its coast.',
        'The Municipality will take part in the project as an end-user. Our contact person will be [name, position, '
        'e-mail]. Our staff will take part in the project\'s steering meetings, agree the warning thresholds with the '
        'project team, review the warning bulletins and take part in the training, as our resources allow.',
        'The Municipality\'s contribution is staff time in kind; the Municipality receives no SPS funds, and this letter '
        'creates no financial obligation for it.'], 'Municipality of Durrës'),
    sq=letter_sq('[LETËR ZYRTARE E BASHKISË]', 'Durrës, [data]', 'Bashkia Durrës', [
        'Durrësi është në qendër të projektit. Bregu i tij i ulët po ulet, dhe porti, puset që e furnizojnë me ujë të '
        'pijshëm dhe qytetarët e tij janë të ekspozuar ndaj depërtimit të ujit të detit, niveleve ekstreme të detit dhe '
        'tërmeteve, siç e tregoi tërmeti i 26 nëntorit 2019. Paralajmërimet e projektit deklarojnë paraprakisht sa shpesh '
        'mund të gabojnë, dhe modeli e algoritmi i paralajmërimeve do të publikohen si kod i hapur. Projekti lidhet me '
        'përgjegjësitë e Bashkisë për sigurinë e qytetarëve dhe të bregut të saj.',
        'Bashkia do të marrë pjesë në projekt si përdorues fundor. Personi ynë i kontaktit do të jetë [emri, pozicioni, '
        'e-mail]. Stafi ynë do të marrë pjesë në mbledhjet drejtuese të projektit, do të bjerë dakord me ekipin e '
        'projektit për pragjet e paralajmërimit, do të shqyrtojë buletinet e paralajmërimit dhe do të marrë pjesë në '
        'trajnime, sipas mundësive tona.',
        'Kontributi i Bashkisë është koha e punës së stafit; Bashkia nuk merr fonde nga NATO, dhe kjo letër nuk krijon '
        'asnjë detyrim financiar për të.'], 'Bashkia Durrës'))

# --- Ujësjellës Kanalizime Durrës sh.a. -----------------------------------------------------------------------------
UKD_NAME = 'Ujësjellës Kanalizime Durrës sh.a.'
UKD = dict(
    out='CERTAIN-COAST_Letter_of_Support_UKD_Durres.docx',
    request=dict(
        to=f'Drejtuesit të shoqërisë {UKD_NAME}', greeting='Të nderuar,',
        body=[APPLY, WHAT,
              'Depërtimi i ujit të detit është rrezik për puset bregdetare që furnizojnë me ujë të pijshëm, prandaj '
              'shoqëria juaj është përdoruesi më i drejtpërdrejtë i paralajmërimeve të projektit. Do të ishte shumë e '
              f'rëndësishme që **{UKD_NAME} të marrë pjesë në projekt si përdorues fundor (end-user)**. {NATO_ASKS} '
              f'{ROLE_SQ.format(who="Shoqëria")} Të dhënat e puseve, nëse i jepni, ndahen sipas një marrëveshjeje dhe '
              f'trajtohen si të kufizuara. {FREE}',
              ask('shoqërisë', 'ju ose personi i autorizuar'), MEET]),
    en=letter_en('[LETTERHEAD OF THE COMPANY]', 'Durrës, [date]',
                 f'{UKD_NAME}, the water supply and sewerage company of Durrës,', [
        'Seawater intrusion is a threat to coastal wells that supply drinking water. The project will issue early '
        'warnings of seawater intrusion into the wells, of earthquake-induced liquefaction and of extreme sea levels on '
        'the coast of Durrës, each stating in advance how often it may be wrong, and will release its model and warning '
        'algorithm as open-source code. These warnings are relevant to the operation of our wells.',
        'We will take part in the project as an end-user. Our contact person will be [name, position, e-mail]. Our staff '
        'will take part in the project\'s steering meetings, agree with the project team the warning thresholds for the '
        'salinity of the wells, review the warning bulletins and take part in the training, as our resources allow. Data '
        'on our wells that we may provide will be shared under a data agreement and treated as restricted.',
        'Our contribution is staff time in kind; we receive no SPS funds, and this letter creates no financial '
        'obligation for us.'], UKD_NAME),
    sq=letter_sq('[LETËR ZYRTARE E SHOQËRISË]', 'Durrës, [data]',
                 f'{UKD_NAME}, shoqëria e furnizimit me ujë dhe e kanalizimeve të Durrësit,', [
        'Depërtimi i ujit të detit është rrezik për puset bregdetare që furnizojnë me ujë të pijshëm. Projekti do të japë '
        'paralajmërime të hershme për depërtimin e ujit të detit në puse, për lëngëzimin e tokës gjatë tërmeteve dhe për '
        'nivelet ekstreme të detit në bregdetin e Durrësit, ku secili paralajmërim deklaron paraprakisht sa shpesh mund të '
        'gabojë, dhe do ta publikojë modelin dhe algoritmin e paralajmërimeve si kod të hapur. Këto paralajmërime lidhen '
        'me funksionimin e puseve tona.',
        'Do të marrim pjesë në projekt si përdorues fundor. Personi ynë i kontaktit do të jetë [emri, pozicioni, e-mail]. '
        'Stafi ynë do të marrë pjesë në mbledhjet drejtuese të projektit, do të bjerë dakord me ekipin e projektit për '
        'pragjet e paralajmërimit për kripëzimin e puseve, do të shqyrtojë buletinet e paralajmërimit dhe do të marrë '
        'pjesë në trajnime, sipas mundësive tona. Të dhënat e puseve që mund të japim do të ndahen sipas një marrëveshjeje '
        'për të dhënat dhe do të trajtohen si të kufizuara.',
        'Kontributi ynë është koha e punës së stafit; nuk marrim fonde nga NATO, dhe kjo letër nuk krijon asnjë detyrim '
        'financiar për ne.'], UKD_NAME))

# --- the Municipality of Tirana -------------------------------------------------------------------------------------
# The project's sites are on the coast, so the link is weaker than for Durrës: the capital is served by the port and the
# infrastructure of the Durrës coast, the 2019 earthquake struck it too, and it can use the open methods for its own
# hazards. The request names no person: in November 2026 the press reports that the elected mayor is detained and who
# leads the Municipality is disputed.
TIRANA = dict(
    out='CERTAIN-COAST_Letter_of_Support_Municipality_of_Tirana.docx',
    request=dict(
        to='Kryetarit të Bashkisë Tiranë', greeting='Të nderuar,',
        body=[APPLY, WHAT,
              'Tirana dhe Durrësi janë zona kryesore urbane dhe ekonomike e vendit: Porti i Durrësit dhe infrastruktura e '
              'bregut i shërbejnë drejtpërdrejt kryeqytetit, dhe tërmeti i 26 nëntorit 2019 goditi edhe Tiranën. Metodat '
              'e projektit dhe kodi i hapur mund të përdoren edhe për rreziqet e vetë kryeqytetit. Prandaj do të ishte '
              f'shumë e rëndësishme që **Bashkia Tiranë të marrë pjesë në projekt si përdorues fundor (end-user)**. '
              f'{NATO_ASKS} Bashkia do të caktojë një person kontakti; stafi i saj do të marrë pjesë në mbledhjet '
              'drejtuese, do të shqyrtojë buletinet, do të vlerësojë si mund të përdoren metodat për Tiranën dhe do të '
              f'trajnohet për përdorimin e kodit. {FREE}',
              ask('Bashkisë', 'ju ose një zyrtar i autorizuar'), MEET]),
    en=letter_en('[LETTERHEAD OF THE MUNICIPALITY]', 'Tirana, [date]', 'The Municipality of Tirana', [
        'Tirana and Durrës form the main urban and economic area of Albania. The Port of Durrës and the infrastructure of '
        'the Durrës coast serve the capital directly, and the earthquake of 26 November 2019 also struck Tirana. The '
        'project\'s warnings state in advance how often they may be wrong, and its model and warning algorithm will be '
        'released as open-source code, which the Municipality can use for the capital\'s own hazards.',
        'The Municipality will take part in the project as an end-user. Our contact person will be [name, position, '
        'e-mail]. Our staff will take part in the project\'s steering meetings, review the warning bulletins, assess how '
        'the methods can be used for Tirana and take part in the training, as our resources allow.',
        'The Municipality\'s contribution is staff time in kind; the Municipality receives no SPS funds, and this letter '
        'creates no financial obligation for it.'], 'Municipality of Tirana'),
    sq=letter_sq('[LETËR ZYRTARE E BASHKISË]', 'Tiranë, [data]', 'Bashkia Tiranë', [
        'Tirana dhe Durrësi janë zona kryesore urbane dhe ekonomike e Shqipërisë. Porti i Durrësit dhe infrastruktura e '
        'bregut të Durrësit i shërbejnë drejtpërdrejt kryeqytetit, dhe tërmeti i 26 nëntorit 2019 goditi edhe Tiranën. '
        'Paralajmërimet e projektit deklarojnë paraprakisht sa shpesh mund të gabojnë, dhe modeli e algoritmi i '
        'paralajmërimeve do të publikohen si kod i hapur, të cilin Bashkia mund ta përdorë për rreziqet e vetë '
        'kryeqytetit.',
        'Bashkia do të marrë pjesë në projekt si përdorues fundor. Personi ynë i kontaktit do të jetë [emri, pozicioni, '
        'e-mail]. Stafi ynë do të marrë pjesë në mbledhjet drejtuese të projektit, do të shqyrtojë buletinet e '
        'paralajmërimit, do të vlerësojë si mund të përdoren metodat për Tiranën dhe do të marrë pjesë në trajnime, sipas '
        'mundësive tona.',
        'Kontributi i Bashkisë është koha e punës së stafit; Bashkia nuk merr fonde nga NATO, dhe kjo letër nuk krijon '
        'asnjë detyrim financiar për të.'], 'Bashkia Tiranë'))

VARIANTS = {'environment': ENVIRONMENT, 'durres': DURRES, 'ukd': UKD, 'tirana': TIRANA}


def request(doc, r):
    p = para(doc, 0); run(p, 'UNIVERSITETI POLITEKNIK I TIRANËS', bold=True, size=10, color=NAVY)
    p = para(doc, 10); run(p, 'Fakulteti i Gjeologjisë dhe i Minierave · Departamenti i Burimeve Energjetike', size=9,
                           color=GREY)
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; run(p, f'Tiranë, më {DATE}', size=SIZE)
    p = para(doc, 3); run(p, 'Drejtuar: ', bold=True, size=SIZE); run(p, r['to'], size=SIZE)
    p = para(doc, 8); run(p, 'Lënda: ', bold=True, size=SIZE); run(p, SUBJECT_SQ, bold=True, size=SIZE, color=BLUE)
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
    p = para(doc, 0, before=8); run(p, ATTACH, italic=True, size=8.5, color=GREY)


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


def main(out, variant='environment'):
    V = VARIANTS[variant]
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.3); s.top_margin = Cm(1.8); s.bottom_margin = Cm(1.6)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(SIZE)
    request(doc, V['request'])
    letter(doc, V['en'], True)
    letter(doc, V['sq'], False)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    var = sys.argv[2] if len(sys.argv) > 2 else 'environment'
    main(sys.argv[1] if len(sys.argv) > 1 else VARIANTS[var]['out'], var)
