"""CERTAIN-COAST: request to a ministry for a letter of support, with the letter itself.

Page 1: the NPD's request to the ministry (Albanian, on the letterhead of the Faculty).
Page 2: the letter of support for the ministry to sign (English, as NATO requires), with yellow fields.
Page 3: an Albanian reading copy of page 2.
Two variants: 'mie', the Ministry of Infrastructure and Energy (a letter of support, sent by e-mail), and 'mod', the
Ministry of Defence (a letter of support and end-user commitment, delivered by hand, so page 1 leaves room for the
signature and a telephone number written by hand). The Ministry of Defence is the project's only end-user: staff time
in kind, no SPS funds, no financial obligation. The signatory, the contact person and the fields of responsibility are
left to the ministry.

usage: python build_ministry_letter.py OUT.docx [mie|mod]"""
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
MIN_EN = 'Ministry of Infrastructure and Energy of the Republic of Albania'
MIN_SQ = 'Ministria e Infrastrukturës dhe Energjisë e Republikës së Shqipërisë'
MOD_EN = 'Ministry of Defence of the Republic of Albania'
MOD_SQ = 'Ministria e Mbrojtjes e Republikës së Shqipërisë'

APPLICANT_EN = (
    'supports the application of the Polytechnic University of Tirana (Faculty of Geology and Mining), with Assoc. Prof. '
    'Dr. Dulian Zeqiraj as NATO-country Project Director and the Environmental Science Center of Qatar University (Prof. '
    'Jassim Al-Khayat) as partner-country institution, to the NATO Science for Peace and Security Programme for the '
    f'Multi-Year Project **CERTAIN-COAST: {TITLE}** (call 2027-1).')
APPLICANT_SQ = (
    'mbështet aplikimin e Universitetit Politeknik të Tiranës (Fakulteti i Gjeologjisë dhe i Minierave), me Prof. Asoc. '
    'Dr. Dulian Zeqiraj si drejtues i projektit nga vendi anëtar i NATO-s dhe me Qendrën e Shkencave Mjedisore të '
    'Universitetit të Katarit (Prof. Jassim Al-Khayat) si institucion i vendit partner, në Programin e NATO-s «Shkenca '
    'për Paqe dhe Siguri» për projektin shumëvjeçar **CERTAIN-COAST** (thirrja 2027-1): paralajmërim i hershëm i '
    'certifikuar për mbrojtjen e infrastrukturës së ujit, të portit dhe të energjisë në një bregdet që po ulet.')

EN = [
    f'The {MIN_EN} {APPLICANT_EN} The Ministry will take part in the project as its end-user.',
    'The project protects critical infrastructure on Albania\'s low Adriatic coast: the wellfields that supply drinking '
    'water and the Port of Durrës and, near Fier, the landfall of the Trans Adriatic Pipeline. The coast is subsiding '
    'and exposed to seawater intrusion, extreme sea levels and earthquakes, as the earthquake of 26 November 2019 '
    'showed. The project serves three of NATO\'s seven baseline requirements for national resilience (resilient food and '
    'water resources, resilient civil transportation systems and resilient energy supplies). Early warnings that state '
    'in advance how often they may be wrong are directly relevant to [the Ministry\'s responsibilities for water supply, '
    'energy and transport infrastructure and geological hazards].',
    'As end-user, the Ministry will designate a contact person and a small team, who will sit on the project\'s steering '
    'committee, agree with the project the warning thresholds of the bulletins it uses, review the bulletins during the '
    'twelve months of live operation and take part in the final workshop. The Ministry will use the results in its '
    'planning for water supply, energy and transport infrastructure and geological hazards. The model and the warning '
    'algorithm, built by the Project Director, will be released as open-source code; the Ministry\'s staff will be '
    'trained in its use, and the operating procedures will be handed over to the Ministry at the end of the project.',
    'We value the training of young Albanian researchers and the cooperation with Qatar, a NATO partner in the Istanbul '
    'Cooperation Initiative, that the project provides. The Ministry\'s contribution is staff time in kind; the Ministry '
    'receives no SPS funds, and this letter creates no financial obligation for it.',
]

SQ = [
    f'{MIN_SQ} {APPLICANT_SQ} Ministria do të marrë pjesë në projekt si përdoruesi fundor i tij.',
    'Projekti mbron infrastrukturë kritike në bregdetin e ulët adriatik të Shqipërisë: fushat e puseve që furnizojnë me '
    'ujë të pijshëm dhe Portin e Durrësit, si dhe, afër Fierit, pikën ku del në breg Gazsjellësi Trans-Adriatik. Bregu '
    'po ulet dhe është i ekspozuar ndaj depërtimit të ujit të detit, niveleve ekstreme të detit dhe tërmeteve, siç e '
    'tregoi tërmeti i 26 nëntorit 2019. Projekti u shërben tri nga shtatë kërkesave bazë të NATO-s për qëndrueshmërinë '
    'kombëtare (burime të qëndrueshme ushqimi dhe uji, sisteme të qëndrueshme të transportit civil dhe furnizim i '
    'qëndrueshëm me energji). Paralajmërimet që deklarojnë paraprakisht sa shpesh mund të gabojnë lidhen drejtpërdrejt '
    'me [përgjegjësitë e Ministrisë për furnizimin me ujë, infrastrukturën e energjisë dhe të transportit dhe rreziqet '
    'gjeologjike].',
    'Si përdorues fundor, Ministria do të caktojë një person kontakti dhe një grup të vogël, të cilët do të jenë pjesë e '
    'komitetit drejtues të projektit, do të bien dakord me projektin për pragjet e paralajmërimit në buletinet që përdor '
    'Ministria, do të shqyrtojnë buletinet gjatë dymbëdhjetë muajve të funksionimit dhe do të marrin pjesë në seminarin '
    'përmbyllës. Ministria do t\'i përdorë rezultatet në planifikimin e saj për furnizimin me ujë, infrastrukturën e '
    'energjisë dhe të transportit dhe rreziqet gjeologjike. Modeli dhe algoritmi i paralajmërimit, të ndërtuara nga '
    'drejtuesi i projektit, do të publikohen si kod i hapur (open source); stafi i Ministrisë do të trajnohet për '
    'përdorimin e tij, dhe procedurat e punës do t\'i dorëzohen Ministrisë në fund të projektit.',
    'Vlerësojmë trajnimin e kërkuesve të rinj shqiptarë dhe bashkëpunimin me Katarin, partner i NATO-s në Iniciativën e '
    'Bashkëpunimit të Stambollit, që ofron projekti. Kontributi i Ministrisë është koha e punës së stafit; Ministria nuk '
    'merr fonde nga NATO, dhe kjo letër nuk krijon asnjë detyrim financiar për të.',
]

EN_MOD = [
    f'The {MOD_EN} {APPLICANT_EN} The Ministry will take part in the project as its end-user.',
    'The project protects critical infrastructure on Albania\'s low Adriatic coast: the wellfields that supply drinking '
    'water and the Port of Durrës and, near Fier, the landfall where the Trans Adriatic Pipeline, an undersea gas '
    'pipeline between two Allies, Albania and Italy, leaves the shore. The coast is subsiding and exposed to seawater '
    'intrusion, extreme sea levels and earthquakes, as the earthquake of 26 November 2019 showed. The project serves three '
    'of NATO\'s seven baseline requirements for national resilience (resilient food and water resources, resilient civil '
    'transportation systems and resilient energy supplies), which also underpin civil support to the military, and the '
    'call\'s topic of protection of critical infrastructure and maritime and undersea infrastructure resilience. Early '
    'warnings that state in advance how often they may be wrong are directly relevant to [the Ministry\'s '
    'responsibilities for national resilience, civil emergency planning and the protection of critical infrastructure].',
    'As end-user, the Ministry will designate a contact person and a small team, who will sit on the project\'s steering '
    'committee, agree with the project the warning thresholds of the bulletins it uses, review the bulletins during the '
    'twelve months of live operation and take part in the final workshop. The Ministry will use the results in its '
    'planning for national resilience and the protection of critical infrastructure; its staff will be trained in the use '
    'of the bulletins and the open software, and the operating procedures will be handed over to the Ministry at the end '
    'of the project.',
    'We value the training of young Albanian researchers and the cooperation with Qatar, a NATO partner in the Istanbul '
    'Cooperation Initiative, that the project provides. The Ministry\'s contribution is staff time in kind; the Ministry '
    'receives no SPS funds, and this letter creates no financial obligation for it.',
]

SQ_MOD = [
    f'{MOD_SQ} {APPLICANT_SQ} Ministria do të marrë pjesë në projekt si përdoruesi fundor i tij.',
    'Projekti mbron infrastrukturë kritike në bregdetin e ulët adriatik të Shqipërisë: fushat e puseve që furnizojnë me '
    'ujë të pijshëm dhe Portin e Durrësit, si dhe, afër Fierit, pikën ku del në breg Gazsjellësi Trans-Adriatik, një '
    'gazsjellës nënujor midis dy vendeve aleate, Shqipërisë dhe Italisë. Bregu po ulet dhe është i ekspozuar ndaj '
    'depërtimit të ujit të detit, niveleve ekstreme të detit dhe tërmeteve, siç e tregoi tërmeti i 26 nëntorit 2019. '
    'Projekti u shërben tri nga shtatë kërkesave bazë të NATO-s për qëndrueshmërinë kombëtare (burime të qëndrueshme '
    'ushqimi dhe uji, sisteme të qëndrueshme të transportit civil dhe furnizim i qëndrueshëm me energji), mbi të cilat '
    'mbështetet edhe ndihma civile për forcat e armatosura, dhe bie në temën e thirrjes për mbrojtjen e infrastrukturës '
    'kritike dhe qëndrueshmërinë e infrastrukturës detare dhe nënujore. Paralajmërimet që deklarojnë paraprakisht sa '
    'shpesh mund të gabojnë lidhen drejtpërdrejt me [përgjegjësitë e Ministrisë për qëndrueshmërinë kombëtare, '
    'planifikimin civil të emergjencave dhe mbrojtjen e infrastrukturës kritike].',
    'Si përdorues fundor, Ministria do të caktojë një person kontakti dhe një grup të vogël, të cilët do të jenë pjesë e '
    'komitetit drejtues të projektit, do të bien dakord me projektin për pragjet e paralajmërimit në buletinet që përdor '
    'Ministria, do të shqyrtojnë buletinet gjatë dymbëdhjetë muajve të funksionimit dhe do të marrin pjesë në seminarin '
    'përmbyllës. Ministria do t\'i përdorë rezultatet në planifikimin e saj për qëndrueshmërinë kombëtare dhe mbrojtjen e '
    'infrastrukturës kritike; stafi i saj do të trajnohet për përdorimin e buletineve dhe të softuerit të hapur, dhe '
    'procedurat e punës do t\'i dorëzohen Ministrisë në fund të projektit.',
    'Vlerësojmë trajnimin e kërkuesve të rinj shqiptarë dhe bashkëpunimin me Katarin, partner i NATO-s në Iniciativën e '
    'Bashkëpunimit të Stambollit, që ofron projekti. Kontributi i Ministrisë është koha e punës së stafit; Ministria nuk '
    'merr fonde nga NATO, dhe kjo letër nuk krijon asnjë detyrim financiar për të.',
]

# Page 1: the request. Shared paragraphs, then the two variants.
APPLY = ('Universiteti Politeknik i Tiranës aplikon, nëpërmjet Fakultetit të Gjeologjisë dhe të Minierave, në thirrjen '
         '2027-1 të Programit të NATO-s «Shkenca për Paqe dhe Siguri» me projektin shumëvjeçar **CERTAIN-COAST** (36 '
         'muaj), në partneritet me Universitetin e Katarit. Drejtues i projektit për UPT-në jam unë. Afati i dorëzimit '
         'është **e diela, 15 nëntor 2026, ora 23:59**.')
WARN = ('Projekti jep paralajmërime të hershme për depërtimin e ujit të detit në puset e ujit të pijshëm, për '
        'lëngëzimin e tokës gjatë tërmeteve dhe për nivelet ekstreme të detit ')
RISIA = ('**Risia:** çdo paralajmërim deklaron paraprakisht sa shpesh mund të gabojë. Përdorues fundor është Shërbimi '
         'Gjeologjik Shqiptar, i cili në fund të projektit merr rrjetin e monitorimit, softuerin e hapur dhe stafin e '
         'trajnuar. NATO financon rreth €382,500.')
ASK = ('**Ju lutem për një letër mbështetjeje**, në letrën zyrtare të Ministrisë, të firmosur nga titullari ose nga një '
       'person i autorizuar, **mundësisht deri të premten, 13 nëntor 2026**')
EASE = ('Për t\'jua lehtësuar, bashkëngjis tekstin e propozuar të letrës në anglisht, siç e kërkon NATO, dhe përkthimin '
        'e saj në shqip vetëm për lexim; fushat me të verdhë plotësohen nga Ministria, dhe teksti mund të ndryshohet '
        'sipas gjykimit tuaj. Letra shpreh **mbështetje në parim** dhe **nuk krijon asnjë detyrim financiar ose '
        'ligjor** për Ministrinë.')
MEET = 'Jam në dispozicion për ta paraqitur projektin në një takim të shkurtër, në çdo orë që ju përshtatet.'

REQUEST = {
    'mie': dict(
        to='z. Enea Karakaçi, Ministër i Infrastrukturës dhe Energjisë', greeting='I nderuar z. Ministër,',
        by_hand=True, date='12.11.2026',
        subject='Kërkesë për letër mbështetjeje dhe angazhimi si përdorues fundor për aplikimin e UPT-së në Programin '
                'e NATO-s «Shkenca për Paqe dhe Siguri» (SPS), projekti CERTAIN-COAST',
        attach='Bashkëlidhur: 1. Teksti i propozuar i letrës së mbështetjes dhe angazhimit (anglisht); 2. Përkthimi në '
               'shqip, vetëm për lexim; 3. Shënimi i konceptit të projektit (5 faqe).',
        body=[APPLY,
              WARN + 'në dy pjesë të bregut: midis Durrësit dhe Fushë-Kuqes, ku ndodhen fushat e puseve dhe Porti i '
              'Durrësit, dhe afër Fierit, ku gazsjellësi TAP del në breg. **Risia:** çdo paralajmërim deklaron '
              'paraprakisht sa shpesh mund të gabojë. Modelimin e bën drejtuesi i projektit, i cili ndërton edhe '
              'algoritmin e paralajmërimit; në fund ato publikohen si **kod i hapur (open source)**, që Ministria dhe '
              'institucionet e tjera ta përdorin. NATO financon rreth €382,500.',
              'Meqë projekti lidhet drejtpërdrejt me fushat e përgjegjësisë së Ministrisë suaj (furnizimi me ujë, '
              'infrastruktura e energjisë dhe e transportit, rreziqet gjeologjike), ju propozojmë që Ministria e '
              'Infrastrukturës dhe Energjisë të jetë **përdoruesi fundor** i projektit. NATO kërkon që çdo projekt të ketë '
              'të paktën një përdorues fundor, i cili merr pjesë në projekt dhe përdor rezultatet e tij pa marrë fonde '
              'nga NATO. Ministria do të caktonte një person kontakti dhe një grup të vogël për komitetin drejtues, do të '
              'binte dakord për pragjet e paralajmërimit, do të shqyrtonte buletinet gjatë 12 muajve të funksionimit dhe '
              'në fund do të merrte kodin, procedurat e punës dhe trajnimin. Dr. Lusien Ismaili, nga Ministria, është '
              'pjesë e ekipit si lidhja me Ministrinë.',
              '**Ju lutem për një letër mbështetjeje dhe angazhimi si përdorues fundor**, në letrën zyrtare të '
              'Ministrisë, të firmosur nga titullari ose nga një person i autorizuar, **mundësisht deri të premten, 13 '
              'nëntor 2026**. Mund ta dërgoni të skanuar në PDF në adresën dulian.zeqiraj@fgjm.edu.al, ndërsa origjinalin '
              'mund ta tërheq vetë në Ministri. Bashkëngjis tekstin e propozuar të letrës në anglisht, siç e kërkon NATO, '
              'dhe përkthimin e saj në shqip vetëm për lexim; fushat me të verdhë plotësohen nga Ministria, dhe teksti '
              'mund të ndryshohet sipas gjykimit tuaj. Kontributi i Ministrisë është vetëm koha e punës së stafit: letra '
              '**nuk krijon asnjë detyrim financiar**. Informacioni i ndjeshëm për infrastrukturën trajtohet si i '
              'kufizuar, dhe çdo publikim kontrollohet para botimit.',
              MEET]),
    'mod': dict(
        to='Ministrisë së Mbrojtjes, Kabinetit të Ministrit', by_hand=True, date='11.11.2026',
        subject='Kërkesë për letër mbështetjeje dhe angazhimi si përdorues fundor për aplikimin e UPT-së në Programin '
                'e NATO-s «Shkenca për Paqe dhe Siguri» (SPS), projekti CERTAIN-COAST',
        attach='Bashkëlidhur: 1. Teksti i propozuar i letrës së mbështetjes dhe angazhimit (anglisht); 2. Përkthimi në '
               'shqip, vetëm për lexim; 3. Shënimi i konceptit të projektit (5 faqe).',
        body=[APPLY,
              WARN + 'në dy pjesë të bregut: midis Durrësit dhe Fushë-Kuqes, ku ndodhen fushat e puseve dhe Porti i '
              'Durrësit, dhe afër Fierit, ku gazsjellësi TAP del në breg dhe vazhdon nën det drejt Italisë. **Risia:** '
              'çdo paralajmërim deklaron paraprakisht sa shpesh mund të gabojë. NATO financon rreth €382,500.',
              'Projekti u shërben tri nga shtatë kërkesave bazë të NATO-s për qëndrueshmërinë kombëtare (resilience): '
              'ushqimi dhe uji, transporti civil dhe energjia, mbi të cilat mbështetet edhe ndihma civile për forcat e '
              'armatosura, dhe bie në temën e thirrjes 2027-1 për mbrojtjen e infrastrukturës kritike dhe '
              'qëndrueshmërinë e infrastrukturës detare dhe nënujore. Prandaj ju propozojmë që Ministria e Mbrojtjes të '
              'jetë **përdoruesi fundor** i projektit. NATO kërkon që çdo projekt të ketë të paktën një përdorues fundor, '
              'i cili merr pjesë në projekt dhe përdor rezultatet e tij pa marrë fonde nga NATO. Ministria do të caktonte '
              'një person kontakti dhe një grup të vogël për komitetin drejtues, do të binte dakord për pragjet e '
              'paralajmërimit, do të shqyrtonte buletinet gjatë 12 muajve të funksionimit dhe në fund do të merrte '
              'procedurat e punës dhe trajnimin.',
              '**Ju lutem për një letër mbështetjeje dhe angazhimi si përdorues fundor**, në letrën zyrtare të '
              'Ministrisë, të firmosur nga titullari ose nga një person i autorizuar, **mundësisht deri të mërkurën, 11 '
              'nëntor 2026**. Mund ta dërgoni të skanuar në PDF në adresën dulian.zeqiraj@fgjm.edu.al, ndërsa origjinalin '
              'mund ta tërheq vetë në Ministri. Bashkëngjis tekstin e propozuar të letrës në anglisht, siç e kërkon NATO, '
              'dhe përkthimin e saj në shqip vetëm për lexim; fushat me të verdhë plotësohen nga Ministria, dhe teksti '
              'mund të ndryshohet sipas gjykimit tuaj. Kontributi i Ministrisë është vetëm koha e punës së stafit: letra '
              '**nuk krijon asnjë detyrim financiar**. Informacioni i ndjeshëm për infrastrukturën trajtohet si i '
              'kufizuar, dhe çdo publikim kontrollohet para botimit.',
              MEET]),
}
SUPPORT = ('Letter of support', 'Letër mbështetjeje')
SUPPORT_EU = ('Letter of support and end-user commitment', 'Letër mbështetjeje dhe angazhimi si përdorues fundor')
LETTER = {'mie': (EN, SQ, MIN_EN, MIN_SQ, SUPPORT_EU), 'mod': (EN_MOD, SQ_MOD, MOD_EN, MOD_SQ, SUPPORT_EU)}


def setup(doc):
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.2); s.top_margin = Cm(1.6); s.bottom_margin = Cm(1.5)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10.5)


def request(doc, variant):
    r = REQUEST[variant]
    p = para(doc, 0); run(p, 'UNIVERSITETI POLITEKNIK I TIRANËS', bold=True, size=10, color=NAVY)
    p = para(doc, 10); run(p, 'Fakulteti i Gjeologjisë dhe i Minierave · Departamenti i Burimeve Energjetike', size=9,
                           color=GREY)
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; run(p, f"Tiranë, më {r['date']}", size=10.5)
    p = para(doc, 2); run(p, 'Drejtuar: ', bold=True, size=10.5)
    run(p, r['to'], size=10.5)
    p = para(doc, 8); run(p, 'Lënda: ', bold=True, size=10.5)
    run(p, r['subject'], bold=True, size=10.5, color=BLUE)
    p = para(doc, 5); run(p, r.get('greeting', 'Të nderuar zonja dhe zotërinj,'), size=10.5)
    for t in r['body']:
        p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; ph(p, t, size=10.5)
    p = para(doc, 10); run(p, 'Ju falënderoj për mbështetjen.', size=10.5)
    p = para(doc, 0); run(p, 'Me respekt,', size=10.5)
    if r['by_hand']:
        para(doc, 26)                                   # room for the signature
    p = para(doc, 0); run(p, 'Prof. Asoc. Dr. Dulian Zeqiraj', bold=True, size=10.5)
    lines = ['Drejtues i projektit CERTAIN-COAST (NATO-country Project Director)',
             'Fakulteti i Gjeologjisë dhe i Minierave, Universiteti Politeknik i Tiranës', 'dulian.zeqiraj@fgjm.edu.al']
    if r['by_hand']:
        lines.append('Tel.: ________________________')
    for t in lines:
        p = para(doc, 0); run(p, t, size=9, color=GREY)
    p = para(doc, 0, before=8)
    run(p, r['attach'], italic=True, size=8.5, color=GREY)


def support(doc, paras, ministry, en=True, kind=SUPPORT):
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
        run(p, f'{kind[0]} for the NATO SPS Multi-Year Project application CERTAIN-COAST: {TITLE}', bold=True,
            size=10.5)
    else:
        run(p, 'Lënda: ', bold=True, size=10.5)
        run(p, f'{kind[1]} për aplikimin e projektit shumëvjeçar NATO SPS CERTAIN-COAST', bold=True, size=10.5)
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


def main(out, variant='mie'):
    en, sq, name_en, name_sq, kind = LETTER[variant]
    doc = Document()
    setup(doc)
    request(doc, variant)
    support(doc, en, name_en, en=True, kind=kind)
    support(doc, sq, name_sq, en=False, kind=kind)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Letter_of_Support_Ministry.docx',
         sys.argv[2] if len(sys.argv) > 2 else 'mie')
