"""CERTAIN-COAST (NATO SPS proposal): Partnership. SPS partnership rules used (with sources), consortium at a glance,
structure diagram, complementarity of expertise, choice of the partner country (options and criteria), roles by work
package, end-users and their commitment letters, governance, added value, a checklist before submission and what is
new. Institution names in square brackets are placeholders to be filled by the applicants; nothing is invented.

usage: python build_partnership.py OUT.docx"""
import os
import sys
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, heading, rich, table, shade, link  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')

LEAD = ('The CERTAIN-COAST partnership is built around the decision chain it serves: scientists who measure and model the '
        'coast, the operators who run the wellfields, the port and the energy landfall, and the civil-protection authority '
        'that acts after an earthquake or a storm. The NATO-country team works where the critical infrastructure is; the '
        'partner-country team leads the modelling, the certified alarms and the transfer, and brings a second subsiding '
        'coast on which the method is tested for transfer within the project; the end-users co-design the thresholds and '
        'run the system after hand-over. Names in square brackets are placeholders for the applicants to fill.')

RULES = [
    'Each proposal is developed jointly by experts from at least one NATO member country and at least one eligible NATO partner country, with a NATO-country Project Director and a partner-country Project Director employed in an eligible partner country.',
    'Additional co-directors from NATO or eligible partner countries may be included.',
    'Co-directors must belong to government, academic or non-profit institutions; for-profit companies cannot be co-directors.',
    'End-users should be based in a NATO or eligible partner country, and the call requires a commitment letter from each end-user.',
    'Albania is on the list of NATO member countries; eligible partner countries in the 2027-1 call include, among others, Algeria, Armenia, Australia, Austria, Azerbaijan, Bahrain, Bosnia and Herzegovina, Colombia, Egypt, Georgia, Iraq, Ukraine and Uzbekistan (check the full list in the call).',
]
SOURCES = [
    ('SPS call for proposals 2027-1', 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/SPS-Call4proposals-2027-1.pdf'),
    ('SPS Multi-Year Project Handbook (2023)', 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/2023/SPS_MYP_Handbook.pdf'),
    ('Sample application form, MYP Phase 1', 'https://nato.int/content/dam/nato/webready/documents/sps/grants/2023/Sample-Application-Form-for-MYP-Phase-1.pdf'),
    ('SPS call for proposals 2024', 'https://research-authority.tau.ac.il/sites/resauth.tau.ac.il/files/NATO-SPS-call-for-proposals-2024.pdf'),
    ('University of Calgary summary of the 2026 call', 'https://research.ucalgary.ca/opportunity/2026-nato-science-peace-and-security'),
    ('Summary of the 2027-1 call (Sept. 2026)', 'https://opportunitiesforyouth.org/2026/09/14/nato-science-for-peace-and-security-programme-2027-call-for-proposals-funding-for-multi-year-projects-and-scientific-events/'),
]

GLANCE = [
    ['NATO-country Project Director (NPD)', 'Albania', '[Faculty of Geology and Mining, Polytechnic University of Tirana: to confirm]',
     'Hydrogeology, geodesy, geotechnics; knowledge of the Durrës coast and access to the operators', 'Coordination; WP1, WP4, WP5, WP7'],
    ['Partner-country Project Director (PPD)', '[Eligible partner country]', '[University or research institute]',
     'Numerical modelling, applied mathematics, uncertainty quantification and machine learning; a subsiding coast for the transfer test', 'WP2, WP3, WP6'],
    ['Additional NATO co-director (optional)', '[NATO member]', '[Institute with InSAR and seismology]',
     'InSAR time-series processing; ambient-noise seismic interferometry', 'WP1; T4.4'],
    ['Albanian research partner (candidate)', 'Albania', '[e.g. a national geoscience or seismological institute]',
     'Seismic network, hydrometeorological and tide-gauge data', 'WP1, WP4; T5.4'],
    ['End-users (commitment letters)', 'Albania', '[Durrës water utility]; [Durrës Port Authority]; [energy landfall operator]; [National Civil Protection Agency]',
     'Thresholds, site access, data, operation of the system after hand-over', 'T3.1; WP5; T6.2, T6.4'],
]

EXPERTISE = ['Hydrogeology and seawater intrusion', 'Geodesy and InSAR', 'Geotechnics and liquefaction',
             'Seismology and ambient noise', 'Applied mathematics, uncertainty and machine learning',
             'Sea level and extremes', 'Operation of the assets', 'Civil protection and emergency response']
#                NPD  PPD  NCD  ARP  EU
MATRIX = [
    ['●', '○', '', '', ''],
    ['●', '', '●', '○', ''],
    ['●', '○', '', '', ''],
    ['', '', '●', '●', ''],
    ['○', '●', '', '', ''],
    ['○', '●', '', '○', ''],
    ['', '', '', '', '●'],
    ['', '', '', '○', '●'],
]

OPTIONS = [
    ['Egypt', 'Nile Delta: a low, subsiding delta coast with seawater intrusion into a heavily used aquifer, major ports and energy facilities',
     'The strongest scientific analogue: every part of the method (relative sea level, intrusion, extremes, alarms) transfers directly',
     'Distance from the Adriatic; data access in the Delta'],
    ['Georgia', 'Black Sea coast with the port of Poti on the Rioni delta and oil terminals on the coast',
     'Port and energy infrastructure on a delta coast; strong security relevance in the Black Sea region',
     'Size of subsidence and availability of groundwater data to check'],
    ['Bosnia and Herzegovina', 'A short Adriatic coast at Neum; Western Balkan neighbour of Albania',
     'Regional cooperation in the Western Balkans; a partner team can lead modelling and the certified alarms',
     'Few coastal assets of the same type; the transfer test would be desk-based'],
    ['Algeria', 'Mediterranean coast with coastal aquifers affected by seawater intrusion and large ports',
     'Seawater intrusion and port infrastructure on the same sea',
     'Data access and language of operator materials'],
]
CRITERIA = [
    '**An existing working relationship** with the Albanian team matters more than anything else: a partnership that has already published or worked together is credible to reviewers.',
    '**A coast that shares the problem** (subsidence, intrusion, ports or energy at the coast), so the transfer test in WP6 is real.',
    '**Strength in the methods the partner leads** (modelling, applied mathematics, machine learning), so the partner has a substantive scientific role.',
    '**Eligibility in the current call**, checked on the official list, and a Project Director employed in that country.',
]

ROLES = [
    ['WP1', 'Coastal motion and relative sea level', '[NPD] or [additional NATO co-director]', 'PPD; Albanian research partner'],
    ['WP2', 'Coupled model and certified surrogate', '[PPD]', 'NPD'],
    ['WP3', 'Certified multi-hazard alarm', '[PPD]', 'NPD; end-users (thresholds, T3.1)'],
    ['WP4', 'Monitoring network', '[NPD]', 'Albanian research partner; additional NATO co-director (T4.4)'],
    ['WP5', 'Live demonstration', '[NPD]', 'End-users; civil protection; PPD'],
    ['WP6', 'Training, transfer and dissemination', '[PPD]', 'All partners; end-users (T6.2, T6.4)'],
    ['WP7', 'Management, data and risk', '[NPD]', 'Steering committee'],
]

ENDUSERS = [
    ['Water utility of the Durrës wellfields', 'Agrees the chloride threshold and the joint pumping rule; receives intrusion bulletins',
     'Access to wells and records; staff time', 'Certified intrusion warnings; pumping rule; trained staff'],
    ['Durrës Port Authority', 'Agrees liquefaction and water-level thresholds; receives bulletins for the port',
     'Site access for sensors; geotechnical records', 'Liquefaction and water-level warnings; post-event reports'],
    ['Operator of the energy landfall', 'Agrees thresholds for the landfall; receives bulletins',
     'Site access under its security rules; design levels', 'Stability checks combining shaking, liquefaction and water level'],
    ['National Civil Protection Agency', 'Receives one picture of water, port and energy after events; co-designs the post-event protocol',
     'Triggers for the post-event protocol; participation in workshops', 'Post-event reports; procedures; policy brief'],
]
LETTER = [
    'the end-user\'s interest in certified warnings for its asset and the problem they address;',
    'what it will provide (site access, data, staff time for thresholds, workshops and training);',
    'its intention to use the system during the live demonstration and to adopt procedures for it;',
    'the contact person and the security conditions for access and data.',
]

GOVERN = [
    '**Steering committee.** The Project Directors and one representative of each end-user; meets every six months and at each milestone, decides on escalated risks within two weeks and approves the go/no-go for live operation (MS4).',
    '**Work-package leaders.** Each work package has one lead institution (Table 4); leaders meet monthly with the coordinator to review progress and the risk indicators (T7.3).',
    '**Consortium agreement.** Signed before the start: roles, budget sharing, ownership and open licences of results, access to operator data (T7.2), and the publication review set out in the Dissemination Plan.',
    '**Decisions.** By consensus where possible; otherwise by majority of the Project Directors, with the NATO-country Project Director accountable for the funds.',
    '**People.** Balanced participation of women and early-career researchers in leadership, exchanges and authorship is monitored and reported.',
]

VALUE = [
    '**For the Alliance:** protection of an Ally\'s water supply, port and energy landfall, with a method that can be applied to other coasts of Allies and partners.',
    '**For the partner country:** leadership of the modelling, the certified alarms and the transfer, training of its young researchers, and a tested method for its own coast.',
    '**For the end-users:** a warning system they help design, run and own, with trained staff and procedures.',
    '**For science:** a joint team that combines field geoscience at critical infrastructure with the mathematics of certified prediction.',
]

CHECK = [
    'Name the partner-country institution and Project Director, and check the country on the official eligible list of the call.',
    'Confirm the NATO-country institution and, if wanted, an additional NATO co-director.',
    'Obtain a commitment letter from each end-user (water utility, port authority, energy landfall operator, civil protection).',
    'Agree the work-package leadership in Table 4 and update the Budget split by recipient accordingly.',
    'Draft the consortium agreement, including data access and the publication review.',
    'Confirm the call deadline and phase on nato.int: a third-party summary lists 15 November 2026 for the 2027-1 call.',
]

NEW = [
    '**A partnership built on the decision chain.** Scientists, operators and civil protection are partners from the first month, so the thresholds are agreed before the alarms are designed and the users own the system at the end.',
    '**A twin-coast design.** The partner country brings a second subsiding coast, on which the method is tested for transfer within the project, not only promised after it.',
    '**Leadership, not only participation, for the partner.** The partner-country team leads the mathematics, the certified alarms and the transfer, the parts of the project that are most portable.',
    '**Security built into the partnership.** End-users set the security conditions for access and data in their commitment letters, consistent with the two-tier dissemination plan.',
]


def fig_structure(path):
    W, H = 6.7, 5.0
    fig = plt.figure(figsize=(W, H), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')

    def box(x, y, w, h, fc, ec, title, lines, tcol='white', lcol='white', ts=10.5, ls=9.2):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.08', fc=fc, ec=ec, lw=1.4))
        ax.text(x + w / 2, y + h - 0.20, title, fontsize=ts, fontweight='bold', color=tcol, ha='center', va='center')
        ax.text(x + w / 2, y + h - 0.36 - 0.17 * len(lines) / 2 - 0.05, '\n'.join(lines), fontsize=ls, color=lcol, ha='center',
                va='center', linespacing=1.3)

    def arrow(x0, y0, x1, y1, both=False):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='<|-|>' if both else '-|>', mutation_scale=12,
                                     color='#1f2328', lw=1.3))

    box(2.15, 4.30, 2.40, 0.62, '#e9ecf1', '#9aa3ad', 'NATO SPS Programme', ['grant, reviews, reports'], '#1f2328', '#52606D')
    ax.add_patch(FancyBboxPatch((0.08, 3.52), W - 0.16, 0.52, boxstyle='round,pad=0,rounding_size=0.08', fc='#1F3864', ec='none'))
    ax.text(W / 2, 3.78, 'Steering committee: Project Directors + one representative of each end-user',
            fontsize=10, fontweight='bold', color='white', ha='center', va='center')
    arrow(W / 2, 4.30, W / 2, 4.05, both=True)

    bw, bh, by = 1.96, 1.12, 2.02
    xs = (0.08, 2.37, 4.66)
    box(xs[0], by, bw, bh, '#c27c12', '#c27c12', 'NATO-country PD', ['Albania', 'coordination', 'WP1, WP4, WP5, WP7'])
    box(xs[1], by, bw, bh, '#6a4fb3', '#6a4fb3', 'Partner-country PD', ['[eligible partner country]', 'models, alarms, transfer', 'WP2, WP3, WP6'])
    box(xs[2], by, bw, bh, '#2e6db4', '#2e6db4', 'NATO co-director', ['[NATO member], optional', 'InSAR, seismic noise', 'WP1, T4.4'])
    for x in xs:
        arrow(x + bw / 2, 3.52, x + bw / 2, by + bh + 0.02)
    arrow(xs[0] + bw + 0.01, by + bh / 2, xs[1] - 0.01, by + bh / 2, both=True)
    arrow(xs[1] + bw + 0.01, by + bh / 2, xs[2] - 0.01, by + bh / 2, both=True)

    box(xs[0], 1.10, bw, 0.78, '#fbefdc', '#c27c12', 'Albanian research partner', ['candidate; seismic and', 'sea-level data'],
        '#1f2328', '#52606D', ts=9.6, ls=8.8)

    ax.add_patch(FancyBboxPatch((0.08, 0.08), W - 0.16, 0.90, boxstyle='round,pad=0,rounding_size=0.08', fc='#e6f4ec', ec='#1e8a5a', lw=1.4))
    ax.text(0.22, 0.80, 'End-users (commitment letters)', fontsize=10, fontweight='bold', color='#1e8a5a', ha='left', va='center')
    names = ['Water utility', 'Port authority', 'Energy landfall\noperator', 'Civil protection']
    ew = (W - 0.16 - 0.30 - 0.12 * 3) / 4
    for i, n in enumerate(names):
        x = 0.23 + i * (ew + 0.12)
        ax.add_patch(FancyBboxPatch((x, 0.16), ew, 0.50, boxstyle='round,pad=0,rounding_size=0.06', fc='white', ec='#1e8a5a', lw=1.0))
        ax.text(x + ew / 2, 0.41, n, fontsize=9.4, color='#1f2328', ha='center', va='center', fontweight='bold', linespacing=1.1)
    arrow(xs[1] + 0.45, by - 0.02, xs[1] + 0.45, 0.99, both=True)
    ax.text(xs[1] + 0.55, 1.50, 'thresholds, bulletins,\ntraining, hand-over', fontsize=8.8, color='#1f2328', ha='left',
            va='center', linespacing=1.2)
    fig.savefig(path, dpi=300)
    plt.close(fig)


def tidy(t):
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    keep = t.rows[:-1] if len(t.rows) <= 9 else (t.rows[0], t.rows[-2])
    for row in keep:
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.keep_with_next = True
    return t


def bullets(doc, items, size=11):
    for t in items:
        p = para(doc, 3, 0.5); run(p, '• ', bold=True, size=size); rich(p, t, size=size)


def main(out):
    work = tempfile.mkdtemp(); fig = os.path.join(work, 'fig_partnership.png'); fig_structure(fig)
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Partnership', bold=True, size=18, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, LEAD, size=11.5)

    heading(doc, 'SPS partnership rules used', 13, before=4)
    bullets(doc, RULES, size=10.5)
    p = para(doc, 2, before=3); run(p, 'Sources: ', bold=True, size=9.5, color='52606D')
    for i, (t, u) in enumerate(SOURCES):
        link(p, u, t, 9.5)
        if i < len(SOURCES) - 1:
            run(p, '; ', size=9.5, color='52606D')

    heading(doc, '1. The consortium at a glance', 13.5, before=10)
    tidy(table(doc, ['Role', 'Country', 'Institution', 'What it brings', 'Main work'], GLANCE, [3.3, 2.0, 3.9, 4.6, 3.2], size=9.5))
    para(doc, 4)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(fig, width=Cm(17.0))
    p = para(doc, 6); run(p, 'Figure 1. Structure of the partnership. PD: Project Director.', italic=True, size=10, color='52606D')

    heading(doc, '2. Complementary expertise', 13.5, before=8)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'No single team covers the coupled problem. The expertise is spread so that every hazard and every step of the '
            'warning chain has a lead (●) and a second team that contributes (○):')
    rows = [[e] + m for e, m in zip(EXPERTISE, MATRIX)]
    t = tidy(table(doc, ['Expertise', 'NATO-country PD', 'Partner-country PD', 'NATO co-director', 'Albanian research partner', 'End-users'],
                   rows, [5.5, 2.3, 2.3, 2.3, 2.3, 2.3], size=9.5))
    for r in t.rows[1:]:
        for c in r.cells[1:]:
            c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            if c.text.strip() == '●':
                shade(c, 'DCE6F2')
    para(doc, 4)

    heading(doc, '3. Choosing the partner country', 13.5, before=8)
    p = para(doc, 4); rich(p, 'The partner country is chosen on four criteria:')
    bullets(doc, CRITERIA)
    p = para(doc, 4, before=4); rich(p, 'Options that fit the problem, all on the eligible list of the 2027-1 call:')
    tidy(table(doc, ['Country', 'Coast', 'Why it fits', 'To check'], OPTIONS, [2.6, 5.4, 5.2, 3.8], size=9.5))
    p = para(doc, 6, before=3)
    run(p, 'Recommendation: choose the partner with whom the Albanian team already works; among new partners, the Nile Delta '
           'gives the strongest scientific analogue for the transfer test.', italic=True, size=10, color='52606D')

    heading(doc, '4. Roles by work package', 13.5, before=8)
    tidy(table(doc, ['', 'Work package', 'Lead', 'Contributors'], ROLES, [1.3, 5.6, 4.6, 5.5], size=10))
    p = para(doc, 6, before=3)
    run(p, 'With the partner-country team leading WP2, WP3 and WP6, the Budget split by recipient should be updated to match.',
        italic=True, size=10, color='52606D')

    heading(doc, '5. End-users and their commitment', 13.5, before=8)
    tidy(table(doc, ['End-user', 'Role in the project', 'Provides', 'Receives'], ENDUSERS, [3.6, 5.2, 4.0, 4.2], size=9.5))
    p = para(doc, 3, before=6); rich(p, 'Each **commitment letter** states:')
    bullets(doc, LETTER)

    heading(doc, '6. Governance', 13.5, before=8)
    bullets(doc, GOVERN)
    heading(doc, '7. Added value of the partnership', 13.5, before=8)
    bullets(doc, VALUE)
    heading(doc, '8. Checklist before submission', 13.5, before=8)
    for i, t in enumerate(CHECK, start=1):
        p = para(doc, 3, 0.5); run(p, f'{i}. ', bold=True); rich(p, t)
    heading(doc, '9. What is new in this partnership', 13.5, before=8)
    bullets(doc, NEW)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Partnership.docx')
