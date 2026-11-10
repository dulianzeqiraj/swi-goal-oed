"""CERTAIN-COAST (NATO SPS proposal): end-user form for the Ministry of Defence of the Republic of Albania.

The Ministry fills it in and returns it with its signed letter of support and end-user commitment by Wednesday
11 November 2026. Labels are in Albanian with the English field of the NATO SPS application form in grey, so the
answers can be copied to the platform as they are. Part 1 follows the "End-Users" section of the form; Part 2 the
"Project participants" table; Part 3 lists the commitments of the end-user with the months of the work plan; Part 4
is the in-kind contribution for the "Non-NATO funding" field; Part 5 the security of information; Part 6 the
signatory of the letter. Answer cells are shaded light yellow; known values are pre-filled.

usage: python build_mod_form.py OUT.docx"""
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
import build_workplan as W  # noqa: E402

NAVY, FILL, LABEL, GREY, HINT = '1F3864', 'FFF7CC', 'EEF2F8', '6B7280', '6B7280'
DUE = 'të mërkurën, 11 nëntor 2026'
MOD_EN = 'Ministry of Defence of the Republic of Albania'


def months(task):
    for wp in W.WPS:
        for t, _, (a, b) in wp[5]:
            if t == task:
                return f'Muajt {a}–{b}' if a != b else f'Muaji {a}'
    raise KeyError(task)


def head(doc, text, before=10):
    p = para(doc, 3, before=before); run(p, text, bold=True, size=12.5, color=NAVY)
    p.paragraph_format.keep_with_next = True


def note(doc, text, size=9.5):
    p = para(doc, 4, align=WD_ALIGN_PARAGRAPH.JUSTIFY); ph(p, text, size=size, color='374151')


def keep_rows(t):
    """No table row is split across pages."""
    for row in t.rows:
        tr = row._tr.get_or_add_trPr()
        el = OxmlElement('w:cantSplit'); el.set(qn('w:val'), 'true'); tr.append(el)


def label(cell, sq, en):
    cell_text(cell, sq, size=9.5, bold=True)
    p = cell.add_paragraph(); p.paragraph_format.space_after = Pt(0)
    run(p, en, size=8, color=GREY)
    shade(cell, LABEL)


def fields(doc, rows, ws=(6.2, 11.0), tall=()):
    """rows: (label in Albanian, NATO field in English, value or hint, prefilled?)."""
    t = doc.add_table(rows=0, cols=2); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for k, (sq, en, text, filled) in enumerate(rows):
        c = t.add_row().cells
        label(c[0], sq, en)
        cell_text(c[1], text, size=9.5 if filled else 8.8, color=None if filled else HINT)
        shade(c[1], FILL)
        if k in tall:
            for _ in range(3):
                c[1].add_paragraph()
    widths(t, list(ws))
    keep_rows(t)
    return t


def grid(doc, header, rows, ws, size=9.0, fill_cols=()):
    t = doc.add_table(rows=1, cols=len(header)); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c, h in zip(t.rows[0].cells, header):
        cell_text(c, h, size=size, bold=True, color='FFFFFF'); shade(c, NAVY)
    for r in rows:
        cells = t.add_row().cells
        for j, (c, v) in enumerate(zip(cells, r)):
            cell_text(c, v, size=size, color=HINT if (j in fill_cols and v) else None)
            if j in fill_cols:
                shade(c, FILL)
    widths(t, list(ws))
    keep_rows(t)
    return t


def main(out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(1.9); s.top_margin = Cm(1.4); s.bottom_margin = Cm(1.3)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)

    p = para(doc, 1); run(p, 'CERTAIN-COAST — Formulari i përdoruesit fundor', bold=True, size=17, color=NAVY)
    p = para(doc, 2); run(p, 'End-user form · Ministria e Mbrojtjes e Republikës së Shqipërisë', bold=True, size=11,
                           color=NAVY)
    p = para(doc, 6); run(p, f'Projekt shumëvjeçar i Programit të NATO-s «Shkenca për Paqe dhe Siguri», thirrja 2027-1 · '
                             f'ju lutem ktheni deri {DUE}', bold=True, size=10, color='B91C1C')
    note(doc, 'Ju lutem plotësoni qelizat me ngjyrë të verdhë të lehtë dhe ktheni këtë formular, bashkë me letrën e '
              'mbështetjes dhe të angazhimit të firmosur, të skanuar në PDF, në adresën dulian.zeqiraj@fgjm.edu.al, deri '
              f'{DUE}. Fushat ndjekin formularin e NATO-s: emrin e fushës në anglisht e gjeni me ngjyrë gri, dhe '
              'përgjigjet tuaja i hedhim në platformë ashtu siç i shkruani. Emrat, pozicionet dhe adresat shkruajini siç '
              'duhet të dalin në anglisht. Të dhënat përdoren vetëm për këtë aplikim. Si përdorues fundor, Ministria nuk '
              'merr fonde nga NATO dhe nuk merr asnjë detyrim financiar; kontributi i saj është koha e punës së stafit.')

    head(doc, 'Pjesa 1. Përfaqësuesi i përdoruesit fundor', before=4)
    note(doc, 'Personi që përfaqëson Ministrinë si përdorues fundor në aplikim (seksioni «End-Users» i formularit të NATO-s). '
              'Zakonisht është personi i kontaktit për projektin.')
    fields(doc, [
        ('Titulli', 'Title', 'p.sh. Mr, Ms, Dr, Col.', False),
        ('Emri', 'First name', '', False),
        ('Mbiemri', 'Family name', '', False),
        ('Pozicioni', 'Job title', 'p.sh. Director of …, Head of Unit', False),
        ('Institucioni', 'Institution', MOD_EN, True),
        ('Drejtoria ose njësia', 'Department / unit', 'p.sh. Directorate of …', False),
        ('Adresa postare', 'Postal address', 'Adresa e plotë e Ministrisë, Tiranë', False),
        ('Shteti', 'Country', 'Albania', True),
        ('Telefoni', 'Telephone', '+355 …', False),
        ('E-mail', 'E-mail', '', False),
    ])

    head(doc, 'Pjesa 2. Personi i kontaktit dhe grupi i Ministrisë')
    note(doc, 'NATO kërkon për çdo pjesëmarrës emrin, pozicionin, shtetësinë, detyrat dhe pjesën e kohës së punës '
              '(«Project participants»). Të gjithë duhet të jenë shtetas të një vendi anëtar ose partner i NATO-s. '
              'Propozimi ynë: 5% për personin e kontaktit (rreth 2 ditë në muaj) dhe 2–5% për të tjerët.')
    grid(doc, ['', 'Emri dhe mbiemri\nName', 'Pozicioni\nPosition', 'Shtetësia\nNationality', 'Detyrat në projekt\nTasks',
               '% e kohës\n% time'],
         [['1', '', '', 'Albanian', 'Personi i kontaktit: komiteti drejtues, pragjet (T3.1), shqyrtimi i buletineve (T5.2), '
                                    'marrja e procedurave (MS7)', '5%'],
          ['2', '', '', '', '', ''], ['3', '', '', '', '', ''], ['4', '', '', '', '', '']],
         [0.6, 3.6, 3.4, 2.2, 5.6, 1.8], fill_cols=(1, 2, 3, 4, 5))

    head(doc, 'Pjesa 3. Angazhimi si përdorues fundor')
    note(doc, 'Këto janë detyrat që propozojmë për Ministrinë, me muajt e planit të punës (muaji 1 është fillimi i '
              'projektit). Shënoni «Po» për ato që Ministria pranon, ose ndryshojini sipas nevojës.')
    rows = [['Pjesëmarrje në komitetin drejtues, çdo gjashtë muaj', 'Muajt 1–36'],
            ['Pragjet e paralajmërimit për buletinet që përdor Ministria (T3.1)', months('T3.1')],
            ['Protokolli i buletineve dhe prova e parë para funksionimit (T5.1)', months('T5.1')],
            ['Shqyrtimi i buletineve gjatë dymbëdhjetë muajve të funksionimit (T5.2)', months('T5.2')],
            ['Raportet pas një tërmeti ose stuhie të fortë (T5.4)', 'Sipas ngjarjeve'],
            ['Trajnimi i të paktën katër punonjësve të Ministrisë (T6.2)', months('T6.2')],
            ['Kontrolli i publikimeve për informacion të ndjeshëm para botimit (T7.2)', 'Muajt 1–36'],
            ['Seminari përmbyllës; marrja e softuerit dhe e procedurave të punës (MS7)', 'Muaji 36']]
    grid(doc, ['Detyra (commitment)', 'Kur (months)', 'Po / Jo'], [r + [''] for r in rows], [11.2, 3.6, 2.4],
         fill_cols=(2,))
    p = para(doc, 2, before=6)
    fields(doc, [
        ('Fushat e përgjegjësisë së Ministrisë që lidhen me projektin',
         'Text of the letter (yellow field)',
         'p.sh. qëndrueshmëria kombëtare, planifikimi civil i emergjencave, mbrojtja e infrastrukturës kritike', False),
        ('Si do t\'i përdorë Ministria rezultatet', 'Use of the results by the end-user',
         'p.sh. prioritetet pas një tërmeti ose stuhie, planifikimi për humbjen e puseve të ujit të pijshëm, '
         'planet e emergjencës', False),
        ('Si dëshiron t\'i marrë buletinet', 'Bulletin channel',
         'E-mail / platformë e mbrojtur / të dyja; personi ose zyra që i merr', False),
    ], tall=(0, 1))

    head(doc, 'Pjesa 4. Kontributi në natyrë')
    pm = 0.05 * 36
    note(doc, 'NATO kërkon vlerën e kontributeve që nuk paguhen nga NATO («Non-NATO funding»). Për Ministrinë ky është vetëm '
              f'koha e punës së stafit. Vlerësimi ynë për personin e kontaktit me 5% të kohës është rreth {pm:.1f} '
              'person-muaj në 36 muaj; shtoni grupin nëse ka.')
    fields(doc, [
        ('Koha e stafit gjithsej, 36 muaj', 'Staff time (person-months)', f'rreth {pm:.1f} person-muaj', False),
        ('Vlera e përafërt (opsionale)', 'Estimated value (EUR)', 'EUR … ose «not valued»', False),
        ('Të tjera që Ministria vë në dispozicion (opsionale)', 'Other in-kind contribution',
         'p.sh. ambiente për trajnimin; qasje në vende nën përgjegjësinë e Ministrisë sipas rregullave të sigurisë; '
         'ose «asnjë»', False),
    ])

    head(doc, 'Pjesa 5. Siguria e informacionit')
    note(doc, 'Rezultatet për çdo aset trajtohen si të kufizuara dhe ndahen vetëm me Ministrinë dhe autoritetet kombëtare '
              'kompetente; publikohen vetëm metodat, softueri dhe të dhëna të përgjithësuara, pas kontrollit.')
    fields(doc, [
        ('Personi ose zyra që kontrollon publikimet', 'Security review of publications', 'Emri, pozicioni, e-mail', False),
        ('Kërkesa të veçanta për sigurinë (opsionale)', 'Security requirements',
         'p.sh. niveli i klasifikimit, mënyra e shkëmbimit të të dhënave', False),
    ])

    head(doc, 'Pjesa 6. Letra e mbështetjes dhe e angazhimit')
    note(doc, 'Letra firmoset në letrën zyrtare të Ministrisë (teksti i propozuar është në faqen 2 të dokumentit '
              'bashkëlidhur) dhe i dërgohet NATO-s si «End-User(s) commitments».')
    fields(doc, [
        ('Kush e firmos letrën', 'Signatory (name and position)', 'Ministri / Zëvendësministri / Sekretari i Përgjithshëm',
         False),
        ('Numri i protokollit dhe data', 'Protocol number and date', 'Nr. prot. …, data …', False),
        ('Kontakti për çështje administrative', 'Administrative contact', 'Emri, e-mail, telefoni', False),
    ])
    p = para(doc, 0, before=10)
    run(p, 'Prof. Asoc. Dr. Dulian Zeqiraj', bold=True, size=9.5)
    p = para(doc, 0)
    run(p, 'Drejtues i projektit CERTAIN-COAST · Fakulteti i Gjeologjisë dhe i Minierave, Universiteti Politeknik i '
           'Tiranës · dulian.zeqiraj@fgjm.edu.al', size=8.5, color=GREY)
    doc.save(out)
    print('saved', out, '| person-months', pm)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_End_User_Form_Ministry_of_Defence.docx')
