"""CERTAIN-COAST: documents for the Municipality of Durrës as end-user (Albanian).

guide  one page for the staff: how to prepare, sign and send the letter (text, letterhead, fields, signatory,
       language, scan, deadline), with a checklist.
brief  two pages for the Mayor and her staff: what the project is, why Durrës, what the Municipality receives, what is
       asked of it (with the months of the work plan), the innovation, the deadlines and the contact.
form   the end-user form: the fields of the "End-Users" section and of the "Project participants" table of the NATO
       application form (English field names in grey, so the answers go to the platform as written), the commitments
       with their months, the in-kind contribution and the signatory of the letter. Answer cells are light yellow.
The letter itself (request, letter to sign, Albanian reading copy) is built by build_enduser_letter.py (variant durres).

usage: python build_durres_package.py OUTDIR"""
import os
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import shade  # noqa: E402
from build_institutions import run, ph, para, cell_text, widths  # noqa: E402
from build_mod_form import head, note, fields, grid, months  # noqa: E402

NAVY, BLUE, GREY, BOX = '1F3864', '1F4E99', '6B7280', 'EEF4FC'
DUE = 'të premten, 13 nëntor 2026'
DATE = '12.11.2026'
MUN_EN = 'Municipality of Durrës'
CODE = 'github.com/dulianzeqiraj/certain-coast; DOI 10.5281/zenodo.24148762'
PM = 0.05 * 36                                            # person-months of a contact person at 5% over 36 months


def setup():
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = Cm(1.5); s.bottom_margin = Cm(1.4)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)
    return doc


def letterhead(doc):
    p = para(doc, 0); run(p, 'UNIVERSITETI POLITEKNIK I TIRANËS', bold=True, size=10, color=NAVY)
    p = para(doc, 8); run(p, 'Fakulteti i Gjeologjisë dhe i Minierave · Departamenti i Burimeve Energjetike', size=9,
                          color=GREY)


def box(doc, title, text):
    t = doc.add_table(rows=1, cols=1); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.rows[0].cells[0]; shade(c, BOX); widths(t, [17.0])
    tcPr = c._tc.get_or_add_tcPr(); b = OxmlElement('w:tcBorders')
    for side in ('top', 'left', 'bottom', 'right'):
        e = OxmlElement(f'w:{side}'); e.set(qn('w:val'), 'nil'); b.append(e)
    b[1].set(qn('w:val'), 'single'); b[1].set(qn('w:sz'), '24'); b[1].set(qn('w:color'), NAVY)
    tcPr.insert(1, b)
    p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(2); run(p, title, bold=True, size=10.5, color=NAVY)
    q = c.add_paragraph(); q.paragraph_format.space_after = Pt(3); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    ph(q, text, size=10)
    para(doc, 4)


def bullets(doc, items, size=10):
    for t in items:
        p = para(doc, 2, indent=0.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        p.paragraph_format.first_line_indent = Cm(-0.35)
        run(p, '•  ', bold=True, size=size, color=NAVY); ph(p, t, size=size)


def brief(out):
    doc = setup(); letterhead(doc)
    p = para(doc, 2); run(p, 'CERTAIN-COAST: paralajmërim i hershëm i certifikuar për bregdetin e Durrësit', bold=True,
                          size=16, color=NAVY)
    p = para(doc, 8); run(p, 'Projekt shumëvjeçar i Programit të NATO-s «Shkenca për Paqe dhe Siguri» (SPS), thirrja '
                             f'2027-1 · përmbledhje për Bashkinë Durrës · {DATE}', size=9.5, color=GREY)

    head(doc, '1. Çfarë është projekti', before=2)
    note(doc, 'Universiteti Politeknik i Tiranës, nëpërmjet Fakultetit të Gjeologjisë dhe të Minierave, aplikon me partner '
              'Qendrën e Shkencave Mjedisore të Universitetit të Katarit për një projekt 36-mujor. Drejtues i projektit '
              'është Prof. Asoc. Dr. Dulian Zeqiraj. NATO financon rreth €382,500, nga të cilat €313,500 për UPT-në. '
              '**Bashkia nuk paguan asgjë dhe nuk merr asnjë detyrim financiar.**', size=10)

    head(doc, '2. Pse Durrësi')
    note(doc, 'Durrësi është në qendër të projektit. Bregu i ulët po ulet; porti, puset që e furnizojnë qytetin me ujë të '
              'pijshëm dhe banorët janë të ekspozuar ndaj depërtimit të ujit të detit, niveleve ekstreme të detit dhe '
              'tërmeteve, siç e tregoi tërmeti i 26 nëntorit 2019, që shkaktoi lëngëzim të tokës përgjatë bregut. Projekti i '
              'bashkon këto rreziqe në një model të vetëm të bregut dhe jep paralajmërime për to.', size=10)

    box(doc, 'Risia', 'Çdo paralajmërim deklaron **paraprakisht sa shpesh mund të gabojë** (alarme të rreme dhe të humbura), '
                      'dhe kjo verifikohet gjatë 12 muajve të funksionimit. Kështu Bashkia e di sa t\'i besojë një '
                      'paralajmërimi para se të veprojë. Modelin dhe algoritmin e paralajmërimeve i ndërton drejtuesi i '
                      f'projektit; ato publikohen si **kod i hapur** në MATLAB, që punon edhe në GNU Octave falas ({CODE}).')

    head(doc, '3. Çfarë merr Bashkia', before=2)
    bullets(doc, [
        '**Buletine paralajmërimi** për depërtimin e ujit të detit në puse, për lëngëzimin e tokës pas tërmeteve dhe për '
        'nivelet ekstreme të detit në bregun e Durrësit, secili me shkallën e gabimit të deklaruar paraprakisht.',
        '**Të dhënat** e rrjetit të monitorimit që ngre projekti në bregdet (piezometra, sensorë, GNSS).',
        '**Trajnim** për stafin e Bashkisë dhe **kodin e hapur**, që mund ta përdorë falas edhe pas projektit.',
        '**Procedurat e punës** dhe seminarin përmbyllës në muajin 36.'])

    head(doc, '4. Çfarë i kërkohet Bashkisë')
    note(doc, 'Vetëm koha e punës së stafit, «sipas mundësive». Propozimi ynë: një person kontakti me rreth 5% të kohës '
              f'(rreth 2 ditë në muaj, gjithsej rreth {PM:.1f} person-muaj në 36 muaj).', size=10)
    grid(doc, ['Detyra', 'Kur (muaji i projektit)'], [
        ['Letra e mbështetjes dhe e angazhimit, e firmosur (për aplikimin)', f'Tani, mundësisht deri {DUE}'],
        ['Pjesëmarrje në komitetin drejtues, çdo gjashtë muaj', 'Muajt 1–36'],
        ['Rënie dakord për pragjet e paralajmërimit (T3.1)', months('T3.1')],
        ['Protokolli i buletineve dhe prova e parë para funksionimit (T5.1)', months('T5.1')],
        ['Shqyrtimi i buletineve gjatë funksionimit (T5.2)', months('T5.2')],
        ['Trajnimi i stafit (T6.2)', months('T6.2')],
        ['Seminari përmbyllës; marrja e kodit dhe e procedurave', 'Muaji 36']], [12.0, 5.0], size=9.3)

    head(doc, '5. Afatet dhe hapat')
    bullets(doc, [
        f'Bashkia firmos letrën (faqja 2 e letrës bashkëngjitur, në anglisht) dhe e dërgon të skanuar, mundësisht deri {DUE}.',
        'UPT e ngarkon në platformën e NATO-s bashkë me aplikimin deri **të dielën, 15 nëntor 2026, ora 23:59**.',
        'NATO vendos brenda rreth nëntë muajve pas afatit; nëse projekti fitohet, Bashkia njoftohet për fillimin.',
        'Formularin e përdoruesit fundor (bashkëngjitur) e plotëson Bashkia, që të dhënat e saj të hidhen saktë në '
        'formularin e NATO-s.'])

    p = para(doc, 0, before=10); run(p, 'Kontakti: Prof. Asoc. Dr. Dulian Zeqiraj', bold=True, size=10)
    p = para(doc, 0); run(p, 'Drejtues i projektit CERTAIN-COAST · Fakulteti i Gjeologjisë dhe i Minierave, Universiteti '
                             'Politeknik i Tiranës · dulian.zeqiraj@fgjm.edu.al', size=9, color=GREY)
    doc.save(out)


def form(out):
    doc = setup()
    p = para(doc, 1); run(p, 'CERTAIN-COAST — Formulari i përdoruesit fundor', bold=True, size=17, color=NAVY)
    p = para(doc, 2); run(p, 'End-user form · Bashkia Durrës', bold=True, size=11, color=NAVY)
    p = para(doc, 6); run(p, 'Projekt shumëvjeçar i Programit të NATO-s «Shkenca për Paqe dhe Siguri», thirrja 2027-1 · '
                             f'ju lutem ktheni deri {DUE}', bold=True, size=10, color='B91C1C')
    note(doc, 'Ju lutem plotësoni qelizat me ngjyrë të verdhë të lehtë dhe ktheni këtë formular, bashkë me letrën e '
              'mbështetjes dhe të angazhimit të firmosur, të skanuar në PDF, në adresën dulian.zeqiraj@fgjm.edu.al, deri '
              f'{DUE}. Fushat ndjekin formularin e NATO-s: emrin e fushës në anglisht e gjeni me ngjyrë gri, dhe '
              'përgjigjet tuaja i hedhim në platformë ashtu siç i shkruani. Të dhënat përdoren vetëm për këtë aplikim. Si '
              'përdorues fundor, Bashkia nuk merr fonde nga NATO dhe nuk merr asnjë detyrim financiar; kontributi i saj është '
              'koha e punës së stafit.')

    head(doc, 'Pjesa 1. Përfaqësuesi i përdoruesit fundor', before=4)
    note(doc, 'Personi që përfaqëson Bashkinë si përdorues fundor në aplikim (seksioni «End-Users» i formularit të NATO-s). '
              'Zakonisht është personi i kontaktit për projektin.')
    fields(doc, [
        ('Titulli', 'Title', 'p.sh. Mr, Ms, Dr', False),
        ('Emri', 'First name', '', False),
        ('Mbiemri', 'Family name', '', False),
        ('Pozicioni', 'Job title', 'p.sh. Director of …, Head of …', False),
        ('Institucioni', 'Institution', MUN_EN, True),
        ('Drejtoria ose njësia', 'Department / unit', 'p.sh. Directorate of …', False),
        ('Adresa postare', 'Postal address', 'p.sh. Sheshi «Liria», 2000 Durrës', False),
        ('Shteti', 'Country', 'Albania', True),
        ('Telefoni', 'Telephone', '+355 …', False),
        ('E-mail', 'E-mail', '…@durres.gov.al', False),
    ])

    head(doc, 'Pjesa 2. Personi i kontaktit dhe grupi i Bashkisë')
    note(doc, 'NATO kërkon për çdo pjesëmarrës emrin, pozicionin, shtetësinë, detyrat dhe pjesën e kohës së punës '
              '(«Project participants»). Propozimi ynë: 5% për personin e kontaktit (rreth 2 ditë në muaj) dhe 2–5% për '
              'të tjerët, nëse ka.')
    grid(doc, ['', 'Emri dhe mbiemri\nName', 'Pozicioni\nPosition', 'Shtetësia\nNationality', 'Detyrat në projekt\nTasks',
               '% e kohës\n% time'],
         [['1', '', '', 'Albanian', 'Personi i kontaktit: komiteti drejtues, pragjet (T3.1), shqyrtimi i buletineve (T5.2), '
                                    'trajnimi (T6.2)', '5%'],
          ['2', '', '', '', '', ''], ['3', '', '', '', '', '']],
         [0.6, 3.6, 3.4, 2.2, 5.6, 1.8], fill_cols=(1, 2, 3, 4, 5))

    head(doc, 'Pjesa 3. Angazhimi si përdorues fundor')
    note(doc, 'Këto janë detyrat që propozojmë për Bashkinë, me muajt e planit të punës (muaji 1 është fillimi i '
              'projektit). Shënoni «Po» për ato që Bashkia pranon, ose ndryshojini sipas nevojës.')
    rows = [['Pjesëmarrje në komitetin drejtues, çdo gjashtë muaj', 'Muajt 1–36'],
            ['Pragjet e paralajmërimit për buletinet që përdor Bashkia (T3.1)', months('T3.1')],
            ['Protokolli i buletineve dhe prova e parë para funksionimit (T5.1)', months('T5.1')],
            ['Shqyrtimi i buletineve gjatë funksionimit (T5.2)', months('T5.2')],
            ['Raportet pas një tërmeti ose stuhie të fortë (T5.4)', 'Sipas ngjarjeve'],
            ['Trajnimi i stafit të Bashkisë (T6.2)', months('T6.2')],
            ['Seminari përmbyllës; marrja e kodit dhe e procedurave të punës', 'Muaji 36']]
    grid(doc, ['Detyra (commitment)', 'Kur (months)', 'Po / Jo'], [r + [''] for r in rows], [11.2, 3.6, 2.4],
         fill_cols=(2,))
    para(doc, 2, before=6)
    fields(doc, [
        ('Si do t\'i përdorë Bashkia rezultatet', 'Use of the results by the end-user',
         'p.sh. planet e emergjencave civile, planifikimi i zonës bregdetare, prioritetet pas një tërmeti ose stuhie', False),
        ('Si dëshiron t\'i marrë buletinet', 'Bulletin channel',
         'E-mail / platformë e mbrojtur / të dyja; personi ose zyra që i merr', False),
    ], tall=(0,))

    head(doc, 'Pjesa 4. Kontributi në natyrë')
    note(doc, 'NATO kërkon vlerën e kontributeve që nuk paguhen nga NATO («Non-NATO funding»). Për Bashkinë ky është vetëm '
              f'koha e punës së stafit: për personin e kontaktit me 5% të kohës, rreth {PM:.1f} person-muaj në 36 muaj.')
    fields(doc, [
        ('Koha e stafit gjithsej, 36 muaj', 'Staff time (person-months)', f'rreth {PM:.1f} person-muaj', False),
        ('Vlera e përafërt (opsionale)', 'Estimated value (EUR)', 'EUR … ose «not valued»', False),
        ('Të tjera që Bashkia vë në dispozicion (opsionale)', 'Other in-kind contribution',
         'p.sh. salla për trajnimin; të dhëna që Bashkia ka për bregun; ose «asnjë»', False),
    ])

    head(doc, 'Pjesa 5. Letra e mbështetjes dhe e angazhimit')
    note(doc, 'Letra firmoset në letrën zyrtare të Bashkisë (teksti i propozuar është në faqen 2 të letrës bashkëlidhur) '
              'dhe i dërgohet NATO-s si «End-User(s) commitments».')
    fields(doc, [
        ('Kush e firmos letrën', 'Signatory (name and position)', 'p.sh. Kryetarja e Bashkisë ose një zyrtar i autorizuar',
         False),
        ('Numri i protokollit dhe data', 'Protocol number and date', 'Nr. prot. …, data …', False),
        ('Kontakti për çështje administrative', 'Administrative contact', 'Emri, e-mail, telefoni', False),
    ])
    p = para(doc, 0, before=10); run(p, 'Prof. Asoc. Dr. Dulian Zeqiraj', bold=True, size=9.5)
    p = para(doc, 0)
    run(p, 'Drejtues i projektit CERTAIN-COAST · Fakulteti i Gjeologjisë dhe i Minierave, Universiteti Politeknik i '
           'Tiranës · dulian.zeqiraj@fgjm.edu.al', size=8.5, color=GREY)
    doc.save(out)


def guide(out):
    """One page for the staff of the Municipality: how to prepare, sign and send the letter."""
    doc = setup(); letterhead(doc)
    p = para(doc, 2); run(p, 'Si ta përgatisni letrën e mbështetjes dhe të angazhimit', bold=True, size=16, color=NAVY)
    p = para(doc, 8); run(p, 'Udhëzim për Bashkinë Durrës · CERTAIN-COAST, Programi i NATO-s «Shkenca për Paqe dhe '
                             f'Siguri», thirrja 2027-1 · {DATE}', size=9.5, color=GREY)
    steps = [
        ('Teksti', 'Përdorni faqen 2 të letrës bashkëngjitur (në anglisht, siç e kërkon NATO). Në Word fshini faqet 1 dhe 3 '
                   'dhe hidheni tekstin në shabllonin e letrës zyrtare të Bashkisë. Teksti mund të ndryshohet sipas asaj që '
                   'Bashkia mund të angazhohet, por duhet të mbeten katër gjëra: mbështetja për aplikimin, pjesëmarrja si '
                   'përdorues fundor, personi i kontaktit dhe fjalia që letra nuk krijon detyrim financiar.'),
        ('Letra zyrtare', 'Me kokën zyrtare të Bashkisë Durrës, me numër protokolli dhe datë nga protokolli i Bashkisë. '
                          'Adresa e NATO-s është tashmë në letër.'),
        ('Fushat', 'Plotësoni gjashtë fushat e verdha: data; numri i protokollit; personi i kontaktit (emri, pozicioni, '
                   'e-mail); emri dhe pozicioni i firmëtarit; firma dhe vula.'),
        ('Kush firmos', 'Kryetarja e Bashkisë ose një zyrtar i autorizuar prej saj, p.sh. një zëvendëskryetar. Firma me dorë '
                        'dhe vula e Bashkisë.'),
        ('Gjuha', 'Në anglisht, sepse vlerësuesit e NATO-s e lexojnë në anglisht. Nëse Bashkia preferon ta lëshojë në shqip, '
                  'mund të firmosë versionin shqip (faqja 3 e letrës); ne e ngarkojmë bashkë me përkthimin në anglisht.'),
        ('Dërgimi', 'Skanojeni letrën e firmosur në PDF, me ngjyra dhe të lexueshme, dhe dërgojeni në '
                    f'dulian.zeqiraj@fgjm.edu.al, **mundësisht deri {DUE}**. Afati i NATO-s është e diela, 15 nëntor 2026, '
                    'ora 23:59. Në platformën e NATO-s ngarkohet PDF-ja; origjinali mbetet në arkivin e Bashkisë.'),
        ('Formulari', 'Bashkë me letrën, plotësoni formularin e përdoruesit fundor, që të dhënat e personit të kontaktit të '
                      'hidhen saktë në formularin e NATO-s.'),
    ]
    for k, (title, text) in enumerate(steps, 1):
        p = para(doc, 5, indent=0.7, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        p.paragraph_format.first_line_indent = Cm(-0.7)
        run(p, f'{k}.  ', bold=True, size=10.5, color=NAVY)
        run(p, f'{title}. ', bold=True, size=10.5)
        ph(p, text, size=10.5)
    para(doc, 4)
    box(doc, 'Para se ta dërgoni', '☐ koka zyrtare e Bashkisë   ☐ numri i protokollit dhe data   ☐ personi i kontaktit   '
                                   '☐ emri dhe pozicioni i firmëtarit   ☐ firma   ☐ vula   ☐ PDF e lexueshme')
    p = para(doc, 0, before=6); run(p, 'Për çdo pyetje: Prof. Asoc. Dr. Dulian Zeqiraj', bold=True, size=10)
    p = para(doc, 0); run(p, 'Drejtues i projektit CERTAIN-COAST · Fakulteti i Gjeologjisë dhe i Minierave, Universiteti '
                             'Politeknik i Tiranës · dulian.zeqiraj@fgjm.edu.al', size=9, color=GREY)
    doc.save(out)


def main(outdir):
    for fn, name in [(guide, 'CERTAIN-COAST_Udhezim_per_Letren_Bashkia_Durres.docx'),
                     (brief, 'CERTAIN-COAST_Permbledhje_per_Bashkine_Durres.docx'),
                     (form, 'CERTAIN-COAST_Formulari_i_Perdoruesit_Fundor_Bashkia_Durres.docx')]:
        fn(os.path.join(outdir, name)); print('saved', name)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
