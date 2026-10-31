"""CERTAIN-COAST (NATO SPS proposal): CV templates for the project team. Cover page (what SPS requires, team at a glance,
how to fill, what makes the CVs strong) and templates for the NATO-country Project Director, the partner-country
Project Director, an optional additional NATO co-director, and short profiles of early-career researchers.
Only facts known for certain are filled in (the applicant's name and e-mail); every other entry is a highlighted
placeholder, with grey guidance lines to delete before submission. Roles follow the Partnership document.

usage: python build_cv.py OUT.docx"""
import os
import sys

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_BREAK
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import para, heading, table, shade, link  # noqa: E402
from build_letters import run, ph  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')

RULES = [
    'Co-directors must be employed by governmental, academic or other non-profit institutions; the partner-country Project Director must be resident and employed in an eligible partner country.',
    'An individual co-director may not hold more than one SPS grant at a time, so each CV states other SPS grants held.',
    'No fixed CV format was found in the published SPS documents; these templates use at most two pages per person. Check the application form on the SPS grant platform for any required format before submission.',
]
SOURCES = [
    ('SPS call for proposals 2027-1', 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/SPS-Call4proposals-2027-1.pdf'),
    ('University of Calgary summary of the 2026-1 call', 'https://research.ucalgary.ca/opportunity/2026-nato-science-peace-and-security-call-proposals-2026-1'),
    ('NATO SPS: how to apply', 'https://nato.int/en/about-us/organization/nato-structure/science-for-peace-and-security-hub/how-to-apply'),
]

TEAM = [
    ['Dulian Zeqiraj', 'NATO-country Project Director', '[Albania; institution to confirm]', '[expertise]', 'Coordination; WP4, WP5, WP7; WP1'],
    ['[Name]', 'Partner-country Project Director', '[eligible partner country; institution]', '[expertise]', 'WP2, WP3, WP6'],
    ['[Name]', 'Additional NATO co-director (optional)', '[NATO member; institution]', '[expertise]', 'WP1; T4.4'],
    ['[Names]', 'Early-career researchers (at least 6)', '[institutions]', '[fields]', 'WP1–WP5'],
]

HOWTO = [
    'Each person fills in his or her own CV, replaces every yellow placeholder and deletes the grey guidance lines.',
    'Keep each CV to at most two pages, in English, and list only real, verifiable items: publications with DOIs, projects with funders and dates.',
    'Keep the section "Role in CERTAIN-COAST" as drafted, adjusted to the final work-package leadership agreed in the Partnership.',
    'Mark manuscripts that are not yet published with their status (submitted, under review), or leave them out.',
]

STRONG = [
    '**Every CV ends with the person\'s role in the project,** naming work packages, tasks and deliverables, so reviewers see a one-to-one map from people to work.',
    '**Expertise is written against the hazard chain** (relative sea level, intrusion, liquefaction, extremes, certified alarms), matching the expertise matrix of the Partnership.',
    '**Evidence of work with end-users and of training young researchers** has its own section, because SPS values security relevance and capacity building as much as publications.',
    '**The SPS rule on one grant at a time is answered in every CV,** so eligibility is clear without a question.',
]


def guide(doc, text):
    p = para(doc, 3, 0.3); run(p, 'Guidance: ' + text, italic=True, size=9, color='7A8590')


def sec(doc, text):
    p = para(doc, 3, before=7); run(p, text, bold=True, size=11.5, color='1F3864'); p.paragraph_format.keep_with_next = True
    pPr = p._p.get_or_add_pPr(); b = OxmlElement('w:pBdr'); bt = OxmlElement('w:bottom')
    for k, v in (('w:val', 'single'), ('w:sz', '6'), ('w:space', '1'), ('w:color', '9AA3AD')):
        bt.set(k if ':' not in k else '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}' + k.split(':')[1], v)
    b.append(bt); pPr.append(b)


def ph_table(doc, header, rows, widths, size=10):
    t = table(doc, header, rows, widths, size=size)
    for r in t.rows[1:]:
        for c in r.cells:
            for p in c.paragraphs:
                for rn in p.runs:
                    if rn.text.startswith('['):
                        rn.font.highlight_color = WD_COLOR_INDEX.YELLOW
    return t


def bullets_ph(doc, items, size=10.5):
    for t in items:
        p = para(doc, 2, 0.5); run(p, '• ', size=size); ph(p, t, size=size)


def page_break(doc):
    p = doc.add_paragraph(); p.add_run().add_break(WD_BREAK.PAGE)


def cv(doc, name, role, details, expertise_guide, role_text, partner=False):
    p = para(doc, 0); ph(p, name, size=16, bold=True)
    p = para(doc, 8); run(p, role + ', CERTAIN-COAST', bold=True, size=11, color='2E6DB4')
    sec(doc, '1. Personal details')
    t = ph_table(doc, ['Item', 'Details'], details, [4.6, 12.0], size=10)
    sec(doc, '2. Education')
    ph_table(doc, ['Year', 'Degree', 'Institution', 'Field'], [['[year]', '[PhD]', '[institution, country]', '[field]'],
                                                             ['[year]', '[MSc]', '[institution, country]', '[field]'],
                                                             ['[year]', '[BSc]', '[institution, country]', '[field]']],
             [2.0, 3.0, 6.6, 5.0], size=10)
    sec(doc, '3. Career')
    ph_table(doc, ['Years', 'Position', 'Institution'], [['[from–to]', '[position]', '[institution, country]'],
                                                        ['[from–to]', '[position]', '[institution, country]'],
                                                        ['[from–to]', '[position]', '[institution, country]']],
             [2.6, 5.6, 8.4], size=10)
    sec(doc, '4. Expertise relevant to CERTAIN-COAST')
    guide(doc, expertise_guide)
    bullets_ph(doc, ['[area of expertise and what you have done in it]', '[area of expertise and what you have done in it]',
                     '[area of expertise and what you have done in it]'])
    sec(doc, '5. Selected publications (up to 10, mainly the last five years)')
    guide(doc, 'Authors, year, title, journal, volume, pages, DOI; your name in bold. Put first the works closest to the project. '
               'Unpublished manuscripts only with their status.')
    for i in range(1, 6):
        p = para(doc, 2, 0.5); run(p, f'{i}. ', size=10.5); ph(p, '[Authors (year). Title. Journal, volume, pages. DOI]', size=10.5)
    sec(doc, '6. Projects and grants')
    ph_table(doc, ['Years', 'Project', 'Funder', 'Role'], [['[from–to]', '[title]', '[funder]', '[coordinator / partner / researcher]'],
                                                         ['[from–to]', '[title]', '[funder]', '[role]'],
                                                         ['[from–to]', '[title]', '[funder]', '[role]']],
             [2.4, 6.6, 3.8, 3.8], size=10)
    p = para(doc, 3, before=3); run(p, 'Other NATO SPS grants currently held: ', bold=True, size=10.5); ph(p, '[none / grant number]', size=10.5)
    sec(doc, '7. Work with end-users and international partners')
    guide(doc, 'Cooperation with water utilities, ports, energy operators, civil protection or ministries; international projects; '
               'advisory roles. Concrete and dated.')
    bullets_ph(doc, ['[organisation, what you did together, years]', '[organisation, what you did together, years]'])
    sec(doc, '8. Supervision and training')
    guide(doc, 'Doctoral and master students supervised, courses and training schools given, mentoring of early-career researchers.')
    bullets_ph(doc, ['[number] doctoral and [number] master students supervised; [courses taught]'])
    sec(doc, '9. Role in CERTAIN-COAST')
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; ph(p, role_text, size=10.5)
    sec(doc, '10. Other')
    bullets_ph(doc, ['Languages: [languages and levels]', 'Awards and memberships: [awards, professional bodies]'])


NPD_DETAILS = [
    ['Name', 'Dulian Zeqiraj'],
    ['Title and position', '[title, position]'],
    ['Institution and department', '[Faculty of Geology and Mining, Polytechnic University of Tirana: to confirm]'],
    ['Country', 'Albania (NATO member)'],
    ['E-mail', 'dulian.zeqiraj@fgjm.edu.al'],
    ['ORCID and researcher IDs', '[ORCID, Scopus ID]'],
]
PPD_DETAILS = [
    ['Name', '[Name]'], ['Title and position', '[title, position]'], ['Institution and department', '[institution]'],
    ['Country', '[eligible partner country]; resident and employed there'], ['E-mail', '[e-mail]'], ['ORCID and researcher IDs', '[ORCID, Scopus ID]'],
]
NCD_DETAILS = [
    ['Name', '[Name]'], ['Title and position', '[title, position]'], ['Institution and department', '[institution]'],
    ['Country', '[NATO member]'], ['E-mail', '[e-mail]'], ['ORCID and researcher IDs', '[ORCID, Scopus ID]'],
]

NPD_ROLE = ('As NATO-country Project Director, coordinates CERTAIN-COAST and is accountable for the SPS funds (WP7); leads the '
            'monitoring network designed for the warnings (WP4) and the live demonstration with the water utility, the port, '
            'the landfall operator and civil protection (WP5); contributes to the measurement of coastal motion and relative sea '
            'level (WP1). Chairs the steering committee, signs the access agreements with the operators (T7.2, Month 3) and '
            'oversees the hand-over at Month 36.')
PPD_ROLE = ('As partner-country Project Director, leads the coupled model of the coast and its certified surrogate (WP2), the '
            'certified multi-hazard alarm with its proofs and back-testing (WP3), and training, transfer and dissemination (WP6), '
            'including the transfer test on a subsiding coast of [eligible partner country]; supervises the partner-country '
            'early-career researchers and their exchanges to the Durrës coast.')
NCD_ROLE = ('As additional NATO co-director, supervises InSAR time-series processing and the separation of elastic and inelastic '
            'compaction (WP1) and the use of ambient seismic noise as a water-table gauge (T4.4); hosts early-career researchers '
            'for training visits.')

NPD_GUIDE = ('3 to 5 lines linking your work to the hazard chain, for example coastal hydrogeology and seawater intrusion, field '
             'monitoring, groundwater chemistry, work on a coastal aquifer such as Fushë-Kuqe. Keep only what is true.')
PPD_GUIDE = ('3 to 5 lines on modelling, applied mathematics, uncertainty quantification or machine learning, and on any work on '
             'a subsiding or intruded coast in your country.')
NCD_GUIDE = '3 to 5 lines on InSAR, geodesy or seismic interferometry, with the coasts or basins you have worked on.'


def ecr_profiles(doc):
    p = para(doc, 0); run(p, 'Early-career researchers', bold=True, size=16)
    p = para(doc, 8); run(p, 'Short profiles (one block per person; at least six researchers)', bold=True, size=11, color='2E6DB4')
    guide(doc, 'Researchers without a PhD, PhD students or recent PhDs who will receive stipends or take part in exchanges. '
               'Names may be added after selection through the open calls (Gender Balance plan).')
    for i in range(1, 4):
        sec(doc, f'Early-career researcher {i}')
        ph_table(doc, ['Item', 'Details'], [
            ['Name and institution', '[name, institution, country]'],
            ['Degree and year', '[degree, year / expected year]'],
            ['Field', '[field]'],
            ['Work in CERTAIN-COAST', '[work package and task, e.g. WP4, T4.4: seismic velocity and water table]'],
            ['Supervisor and mentor', '[supervisor]; [mentor]'],
        ], [4.6, 12.0], size=10)


def main(out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.2); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)

    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — CVs of the Project Team', bold=True, size=18, color='1F3864')
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Templates. Placeholders are ', italic=True, size=10, color='52606D'); run(p, '[highlighted]', italic=True, size=10, hl=True)
    run(p, '; grey guidance lines are deleted before submission.', italic=True, size=10, color='52606D')

    heading(doc, 'What SPS requires', 13, before=2)
    for t in RULES:
        q = para(doc, 3, 0.5); run(q, '• ', bold=True); ph(q, t, size=10.5)
    p = para(doc, 2, before=3); run(p, 'Sources: ', bold=True, size=9.5, color='52606D')
    for i, (t, u) in enumerate(SOURCES):
        link(p, u, t, 9.5)
        if i < len(SOURCES) - 1:
            run(p, '; ', size=9.5, color='52606D')
    heading(doc, 'The team at a glance', 13, before=8)
    ph_table(doc, ['Person', 'Role', 'Country and institution', 'Expertise', 'Work'], TEAM, [3.0, 3.6, 3.8, 2.8, 3.4], size=9.5)
    para(doc, 3)
    heading(doc, 'How to fill in the CVs', 13, before=6)
    for i, t in enumerate(HOWTO, start=1):
        q = para(doc, 3, 0.5); run(q, f'{i}. ', bold=True); ph(q, t, size=10.5)
    heading(doc, 'What makes these CVs strong', 13, before=6)
    for t in STRONG:
        q = para(doc, 3, 0.5); run(q, '• ', bold=True); ph(q, t, size=10.5)

    page_break(doc)
    cv(doc, 'Dulian Zeqiraj', 'NATO-country Project Director', NPD_DETAILS, NPD_GUIDE, NPD_ROLE)
    page_break(doc)
    cv(doc, '[Name of the partner-country Project Director]', 'Partner-country Project Director', PPD_DETAILS, PPD_GUIDE, PPD_ROLE)
    page_break(doc)
    cv(doc, '[Name of the additional NATO co-director]', 'Additional NATO co-director (optional)', NCD_DETAILS, NCD_GUIDE, NCD_ROLE)
    page_break(doc)
    ecr_profiles(doc)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_CVs.docx')
