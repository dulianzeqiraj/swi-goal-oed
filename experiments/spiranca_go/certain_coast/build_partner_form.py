"""CERTAIN-COAST (NATO SPS proposal): form for a candidate partner-country team, attached to the invitation e-mails.

The partner fills it in and returns it by Thursday 5 November 2026. Part 1 follows the fields the NATO SPS application
form asks about the partner-country Project Director (PPD), so the answers can be copied to the platform as they are;
Part 2 lists the partner team; Part 3 describes the coast for the transfer study; Part 4 is the one-page overview of the
institution that NATO asks as an upload; Part 5 names who signs the Agreement for Joint Research for the institution.
Answer cells are shaded light yellow.

usage: python build_partner_form.py OUT.docx"""
import os
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import shade  # noqa: E402
from build_institutions import run, ph, para, cell_text, widths  # noqa: E402

NAVY, FILL, LABEL = '1F3864', 'FFF7CC', 'EEF2F8'
DUE = 'Thursday 5 November 2026'


def head(doc, text, before=10):
    p = para(doc, 3, before=before); run(p, text, bold=True, size=12.5, color=NAVY)
    p.paragraph_format.keep_with_next = True


def note(doc, text, size=9.5):
    p = para(doc, 4, align=WD_ALIGN_PARAGRAPH.JUSTIFY); ph(p, text, size=size, color='374151')


def fields(doc, rows, ws=(6.0, 11.2), size=9.5, tall=()):
    t = doc.add_table(rows=0, cols=2); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for k, (lab, hint) in enumerate(rows):
        c = t.add_row().cells
        cell_text(c[0], lab, size=size, bold=True); shade(c[0], LABEL)
        cell_text(c[1], hint, size=8.8, color='6B7280'); shade(c[1], FILL)
        if k in tall:
            for _ in range(6):
                c[1].add_paragraph()
    widths(t, list(ws))
    return t


def grid(doc, header, n, ws, size=9.3):
    t = doc.add_table(rows=1, cols=len(header)); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c, h in zip(t.rows[0].cells, header):
        cell_text(c, h, size=size, bold=True, color='FFFFFF'); shade(c, NAVY)
    for i in range(n):
        cells = t.add_row().cells
        for j, c in enumerate(cells):
            cell_text(c, str(i + 1) if j == 0 else '', size=size)
            if j:
                shade(c, FILL)
    widths(t, list(ws))
    return t


def main(out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(1.9); s.top_margin = Cm(1.5); s.bottom_margin = Cm(1.4)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)

    p = para(doc, 2); run(p, 'CERTAIN-COAST — Partner form', bold=True, size=17, color=NAVY)
    p = para(doc, 6); run(p, f'For the partner-country team of a NATO SPS Multi-Year Project · please return by {DUE}',
                           bold=True, size=10.5, color='B91C1C')
    note(doc, 'Please fill in the light-yellow cells (in English) and return this file by e-mail by ' + DUE + ', together '
              'with the signed Agreement for Joint Research. Part 1 uses the same fields as the NATO SPS application form, '
              'so we can enter your answers on the platform exactly as you write them. The data are used only for this '
              'application.')

    head(doc, 'Part 1. Partner-country Project Director', before=6)
    note(doc, 'The Project Director must be employed by a university, public institute or other non-profit institution in '
              'an eligible partner country, be resident in that country, hold the nationality of a NATO or eligible partner '
              'country, and hold no other ongoing SPS grant.')
    fields(doc, [
        ('Title', 'e.g. Prof., Dr., Ms, Mr'),
        ('First name', ''), ('Family name', ''),
        ('Date of birth', 'DD/MM/YYYY'),
        ('Sex', 'Man / Woman / Prefer not to say'),
        ('Nationality', ''), ('Other nationalities (optional)', ''),
        ('Telephone; mobile phone', ''),
        ('Work e-mail; personal e-mail', ''),
        ('Professional online profile (optional)', 'e.g. Google Scholar, ResearchGate, ORCID'),
        ('Current job title', 'e.g. Professor, Head of Department'),
        ('Other current employment (optional)', ''),
        ('Name of the institution', 'In full, without acronyms'),
        ('Country of the institution', ''),
        ('Postal address of the institution', 'In full'),
        ('Ongoing SPS grants', 'None / [give details]'),
        ('Other grants held (optional)', 'Dates, donor, grant name, short description, results'),
        ('Share of working time on the project', 'About 20%'),
    ])
    p = para(doc, 2, before=6); run(p, 'Relevant employment history (up to three)', bold=True, size=10, color=NAVY)
    grid(doc, ['', 'Start and end dates', 'Position', 'Employer'], 3, [0.7, 3.8, 5.8, 6.9])
    p = para(doc, 2, before=6); run(p, 'Education (up to three)', bold=True, size=10, color=NAVY)
    grid(doc, ['', 'Start and end dates', 'Degree', 'University'], 3, [0.7, 3.8, 5.8, 6.9])
    p = para(doc, 2, before=6); run(p, 'Recent publications relevant to the project (up to three) and honours (optional)',
                                    bold=True, size=10, color=NAVY)
    grid(doc, ['', 'Publication or honour (authors, year, title, journal, DOI)'], 3, [0.7, 16.5])
    p = para(doc, 2, before=6); run(p, 'Research focus and expertise (up to 500 words)', bold=True, size=10, color=NAVY)
    fields(doc, [('Research focus', 'Your research and how it relates to the project: coastal geoscience, '
                                    'hydrogeology, water management, hazards, training')], ws=(3.4, 13.8), tall=(0,))

    head(doc, 'Part 2. Partner team')
    note(doc, 'Everyone who will work on the project from your side, including early-career researchers if already known.')
    grid(doc, ['', 'Name', 'Position', 'Nationality', 'Role in the project', '% time'], 5, [0.7, 4.0, 3.4, 2.6, 4.9, 1.6])

    head(doc, 'Part 3. The coast for the transfer study')
    note(doc, 'The partner team leads the transfer study on a coast of its own country: it brings public data and local '
              'knowledge, and the Albanian team runs the model and the algorithm with it.')
    fields(doc, [
        ('Coast or site proposed', 'Name and location'),
        ('Assets at risk', 'Wells or wellfields, ports, energy facilities, settlements'),
        ('Hazards observed', 'Seawater intrusion, subsidence, coastal flooding, earthquakes, other'),
        ('Data available or accessible', 'Maps, wells and salinity, sea level, satellite data, reports'),
        ('Contacts with operators or authorities', 'For the regional workshop'),
    ])

    head(doc, 'Part 4. One-page overview of your institution (NATO upload)')
    note(doc, 'NATO asks for an overview of each participating institution\'s relevant capabilities, resources and '
              'facilities, with websites of the institution and the research team, no more than one page.')
    fields(doc, [
        ('Institution (English and national language)', ''),
        ('Type', 'University / public research institute / other non-profit'),
        ('Website of the institution; web page of the research team', ''),
        ('Relevant capabilities', 'Departments, expertise and staff relevant to the project'),
        ('Resources and facilities', 'Laboratories, computing, field equipment, data'),
        ('Relevant projects and publications', 'Title, funder, years, role; key publications with DOI'),
    ], tall=(3, 4))

    head(doc, 'Part 5. Signature of the Agreement for Joint Research')
    note(doc, 'The NATO Agreement for Joint Research (attached) is signed by the Project Director and by the Head of '
              'Institution and/or the Financial Authority of your institution. Please return it signed and scanned by '
              + DUE + '.')
    fields(doc, [('Name and position of the person who signs for the institution', ''),
                 ('Contact for administrative and financial questions', 'Name, e-mail')])
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Partner_Form.docx')
