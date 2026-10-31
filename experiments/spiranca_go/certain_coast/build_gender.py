"""CERTAIN-COAST (NATO SPS proposal): Gender balance. Policy context (NATO Women, Peace and Security policy 2024; SPS
openness without gender bias; Sendai Framework), aims, measurable targets, measures (recruitment, working conditions,
field safety, mentoring, visibility, code of conduct), the gender dimension of the warning service, responsibilities
and monitoring, institutional context, what is new, and a short paragraph for the application form.
Targets are indicative and voluntary; SPS sets no quota.

usage: python build_gender.py OUT.docx"""
import os
import sys

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, heading, rich, table, link  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')

LEAD = ('CERTAIN-COAST treats gender balance as part of the quality of the project, measured with the same care as its '
        'warnings. Geoscience, engineering and the operation of critical infrastructure have long been fields where women '
        'are under-represented in leadership and field work. The project therefore sets targets where balance matters most '
        '(leadership, stipends, first authorship, speaking roles and field work), removes practical barriers, and reports '
        'its gender indicators in every progress report next to its scientific ones. It also asks a question about the '
        'service itself: do the warnings reach and serve women and men, and other groups, equally well?')

CONTEXT = [
    'NATO SPS activities are open to scientists and experts from NATO member and partner countries **without gender bias**; the Programme sets no quota.',
    'At the Washington Summit (July 2024) Allies endorsed a **new NATO policy on Women, Peace and Security**, which implements UN Security Council Resolution 1325 and includes increasing women\'s participation at all levels and gender-responsive leadership and accountability among its objectives; it also treats climate change as a defining challenge.',
    'The **Sendai Framework for Disaster Risk Reduction** recognises women\'s participation as critical to managing disaster risk, and asks that a gender, age, disability and cultural perspective be integrated in disaster risk policies and practices.',
]
SOURCES = [
    ('NATO: new policy on Women, Peace and Security (2024)', 'https://www.nato.int/en/news-and-events/articles/news/2024/07/10/allies-endorse-a-new-nato-policy-on-women-peace-and-security-at-the-summit-in-washington'),
    ('NATO: women and girls in science (SPS)', 'https://www.nato.int/en/news-and-events/articles/news/2021/02/11/nato-supports-women-and-girls-in-science'),
    ('Sendai Framework 2015–2030', 'https://www.undrr.org/publication/sendai-framework-disaster-risk-reduction-2015-2030'),
]

AIMS = [
    '**A balanced team** at every level, from early-career researchers to the Project Directors and work-package leaders.',
    '**Equal access to what builds a career:** stipends, field work, first authorship, conference talks and leadership roles.',
    '**Safe and fair working conditions** in the office, the laboratory and the field.',
    '**Inclusive warnings** that are understood by, and reach, all the people who must act on them.',
]

TARGETS = [
    ['Early-career researchers trained', 'At least half women (at least 3 of 6)', 'Training records', 'Month 36'],
    ['Stipend holders', 'At least 2 of 4 women', 'Stipend list', 'Month 6, then yearly'],
    ['Leadership', 'At least 3 of 7 work packages led or co-led by women', 'Work-package list', 'Month 3'],
    ['Steering committee', 'At least 40% women; each end-user invited to nominate with balance in mind', 'Membership list', 'Month 3, then yearly'],
    ['Training school', 'At least 40% women among trainers and among trainees', 'School records', 'Month 14'],
    ['Operator and civil-protection staff trained', 'At least one woman per operator; numbers reported by sex', 'Training records', 'Month 36'],
    ['Publications', 'At least 40% of papers with a woman as first or corresponding author', 'Publication list', 'Month 36'],
    ['Conferences and workshops', 'At least 40% women among presenters; no all-male panels', 'Programmes', 'Each event'],
    ['Field work', 'Women and men in every field campaign', 'Campaign logs', 'Each campaign'],
    ['Code of conduct', 'Signed by all partners at the kick-off', 'Signed copies', 'Month 2'],
]

MEASURES = [
    ('Recruitment', [
        'Open calls for stipends and exchanges in Albanian and English, with gender-neutral wording and an explicit invitation to women in geoscience, engineering and mathematics.',
        'Selection panels that include women and men, with written criteria agreed before the call.',
    ]),
    ('Working conditions', [
        'Meetings within working hours, with online participation always possible.',
        'Exchanges of two months can be split into shorter visits for researchers with caring responsibilities.',
        'Deadlines planned around the project calendar so that no one is disadvantaged by part-time work or leave.',
    ]),
    ('Field work for everyone', [
        'The field safety plan (Risk Assessment, R13) includes the two-person rule, safe transport and accommodation, and induction at each site, so that field work is open to all researchers.',
        'Equipment and protective clothing in sizes that fit all team members.',
    ]),
    ('Mentoring and visibility', [
        'Each early-career researcher has a senior mentor; women early-career researchers can choose a mentor among senior women scientists across the partner institutions.',
        'First authorship and conference talks are planned in the publication plan so that early-career women lead papers and present results.',
        'Women scientists and operator staff are visible in project communication, including the final workshop and press events.',
    ]),
    ('Respect and safety', [
        'A code of conduct against harassment and discrimination, signed by all partners at the kick-off.',
        'A confidential contact person for gender and conduct issues, outside the line management of early-career researchers.',
    ]),
]

DIMENSION = [
    '**Who takes part.** Participation in workshops, training and the post-event protocol is recorded by sex, so the project knows whose voice shapes the thresholds and the procedures.',
    '**Warnings that are understood.** Bulletins and public summaries are tested for clarity with a mixed group of users (operator staff, civil-protection officers and community representatives), and the meaning of the certified miss rate is explained in plain language.',
    '**Who is reached after an event.** The post-event protocol invites civil protection to record, where it already collects such data, whom the warnings reached, by sex and age, so that gaps can be closed.',
    '**Effects of disruption.** The policy brief considers how disruption of water supply or of port and energy services affects different groups, including women and men, older people and people with disabilities.',
]

MONITOR = [
    '**Gender contact point.** A member of the steering committee is named as gender contact point and reports on the indicators at each committee meeting.',
    '**Yearly review.** The indicators in Table 1 are reviewed every year; if a target is missed, the committee agrees a corrective action, for example a targeted call, a mentoring offer or a change in speaker selection.',
    '**Reporting.** The gender indicators are reported in every progress report to the SPS Programme, next to the scientific indicators and the certified miss rates.',
    '**Data protection.** Data on participants are collected only in aggregated form and with consent.',
]

INSTITUTIONS = [
    'Partner institutions apply their own equality policies and, where they exist, their Gender Equality Plans; the project aligns its measures with them.',
    'A Gender Equality Plan is an eligibility condition for public bodies, research organisations and higher-education institutions in Horizon Europe, so these measures also prepare the partners for the follow-up funding foreseen in the Sustainability section.',
]

NEW = [
    '**Balance measured where careers are made.** The targets cover leadership, stipends, first authorship, speaking roles and field work, not only the number of people on the team.',
    '**Field work opened by design.** The safety plan that protects everyone in the field also removes practical barriers that keep researchers out of field campaigns.',
    '**Warnings checked for who they reach.** The service records who takes part and whom the warnings reach, and tests the bulletins with a mixed group of users, so inclusiveness is verified rather than assumed.',
    '**Gender reported like science.** The gender indicators appear in the same progress report as the certified miss rates, with the same rule: if a target is missed, a corrective action follows.',
    '**A cross-country mentoring network.** The partnership between the NATO-country and partner-country teams gives early-career women access to mentors in both countries.',
]

SHORT = ('CERTAIN-COAST sets measurable gender targets where careers are made: at least half of the early-career researchers '
         'trained are women, at least two of four stipend holders, at least three of seven work packages led or co-led by '
         'women, at least 40% women among presenters and first authors, and women and men in every field campaign. Open, '
         'gender-neutral calls with mixed selection panels, flexible exchanges, a field safety plan that opens field work to '
         'everyone, mentoring across the partner countries and a signed code of conduct support these targets. The service '
         'itself is checked for inclusiveness: participation is recorded by sex, bulletins are tested with a mixed group of '
         'users, and the post-event protocol records whom the warnings reach. A gender contact point reports the indicators to '
         'the steering committee and in every progress report, in line with NATO\'s 2024 policy on Women, Peace and Security.')


def tidy(t):
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    keep = t.rows[:-1] if len(t.rows) <= 6 else (t.rows[0], t.rows[1], t.rows[-2])
    for row in keep:
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.keep_with_next = True
    return t


def bullets(doc, items, size=11, indent=0.5):
    for t in items:
        p = para(doc, 3, indent); run(p, '• ', bold=True, size=size); rich(p, t, size=size)


def main(out):
    n_short = len(SHORT.split())
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Gender Balance', bold=True, size=18, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, LEAD, size=11.5)

    heading(doc, 'Policy context', 13, before=4)
    bullets(doc, CONTEXT, size=10.5)
    p = para(doc, 2, before=3); run(p, 'Sources: ', bold=True, size=9.5, color='52606D')
    for i, (t, u) in enumerate(SOURCES):
        link(p, u, t, 9.5)
        if i < len(SOURCES) - 1:
            run(p, '; ', size=9.5, color='52606D')

    heading(doc, '1. Aims', 13.5, before=10)
    bullets(doc, AIMS)

    heading(doc, '2. Targets', 13.5, before=8)
    p = para(doc, 4); rich(p, 'Targets are indicative and voluntary; they are reviewed every year (Section 5).')
    p = para(doc, 3); run(p, 'Table 1. Gender targets.', italic=True, size=10, color='52606D'); p.paragraph_format.keep_with_next = True
    tidy(table(doc, ['Area', 'Target', 'Evidence', 'When'], TARGETS, [4.2, 6.6, 3.4, 2.8], size=9.5))
    para(doc, 4)

    heading(doc, '3. Measures', 13.5, before=8)
    for title, items in MEASURES:
        p = para(doc, 2, before=3); run(p, title, bold=True, size=11, color='2E6DB4'); p.paragraph_format.keep_with_next = True
        bullets(doc, items)

    heading(doc, '4. The gender dimension of the warning service', 13.5, before=8)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'A warning is only as good as its reach. CERTAIN-COAST therefore asks who shapes the warnings, who understands '
            'them and who they reach:')
    bullets(doc, DIMENSION)

    heading(doc, '5. Responsibility and monitoring', 13.5, before=8)
    bullets(doc, MONITOR)

    heading(doc, '6. Institutional context', 13.5, before=8)
    bullets(doc, INSTITUTIONS)

    heading(doc, '7. What is new in this gender plan', 13.5, before=8)
    bullets(doc, NEW)

    heading(doc, f'8. Short paragraph for the application form ({n_short} words)', 13.5, before=8)
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, SHORT)
    doc.save(out)
    print('saved', out, '| short paragraph', n_short, 'words')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Gender_Balance.docx')
