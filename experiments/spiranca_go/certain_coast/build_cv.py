"""CERTAIN-COAST (NATO SPS proposal): CV templates for the project team. Cover page (what SPS requires, team at a glance,
how to fill, what makes the CVs strong) and templates for the NATO-country Project Director, the partner-country
Project Director, an optional additional NATO co-director, and short profiles of early-career researchers.
The CV of the NATO-country Project Director is filled in from his CV of 2021 and from his publications as registered in
Crossref (each with its DOI); facts that could not be checked stay as highlighted placeholders. The other CVs are
templates with grey guidance lines to delete before submission. Roles follow the application form.

usage: python build_cv.py OUT.docx             (all CVs and templates, with the cover page)
       python build_cv.py --npd OUT.docx       (the CV of the NATO-country Project Director alone, two pages, for the
                                                Additional files PDF)
       python build_cv.py --ppd OUT.docx       (the CV of the partner-country Project Director alone, from the partner
                                                form of Qatar University)"""
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
    ['Dulian Zeqiraj', 'NATO-country Project Director', 'Albania; Faculty of Geology and Mining, Polytechnic University of Tirana', 'Seawater intrusion, monitoring design, stochastic flow and transport modelling', 'Coordination; WP1–WP5, WP7'],
    ['Arjan Beqiraj', 'Senior researcher (Prof. Dr.)', 'Albania; Faculty of Geology and Mining, Polytechnic University of Tirana', 'Hydrogeology, groundwater chemistry', 'T2.3, T4.1, T5.3'],
    ['Jassim Al-Khayat', 'Partner-country Project Director', 'Qatar; Environmental Science Center, Qatar University', 'Coastal and marine ecology, coastal monitoring', 'WP6; transfer study on the east coast of Qatar'],
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
            'monitoring network designed for the warnings (WP4) and the live '
            'demonstration with the Ministry of Defence, the end-user (WP5); contributes to the coupled '
            'model (WP2) and to the measurement of coastal motion and relative sea level (WP1). Chairs the steering committee, '
            'signs the access agreements for the wells (T7.2, Month 3) and oversees the hand-over to the Ministry of Defence at '
            'Month 36.')

# ---------------------------------------------------------------------- the CV of the NATO-country Project Director
# Sources: his CV of February 2021 (education, career, courses, programming) and Crossref records of his publications.
NPD = dict(
    name='Dulian Zeqiraj',
    details=[
        ['Name', 'Dulian Zeqiraj'],
        ['Title and position', 'Assoc. Prof. Dr., Faculty of Geology and Mining (FGJM), Polytechnic University of Tirana'],
        ['Department', '[Department of Energy Resources: confirm]'],
        ['Country', 'Albania (NATO member)'],
        ['E-mail', 'dulian.zeqiraj@fgjm.edu.al'],
        ['ORCID and researcher IDs', '[ORCID, Scopus ID]'],
    ],
    education=[
        ['[year]', 'Doctor of Sciences (Dr.)', '[institution, country]', '[field]'],
        ['1991–1996', 'University diploma (five years)', 'Faculty of Geology and Mining, University of Tirana, Albania',
         'Drilling and production wells'],
    ],
    career=[
        ['[year]–', 'Associate Professor', 'Faculty of Geology and Mining, Polytechnic University of Tirana'],
        ['2008–[year]', 'Lecturer, Department of Reservoir Engineering (now Energy Resources)',
         'Faculty of Geology and Mining, Polytechnic University of Tirana'],
        ['2006–2008', '[position]', 'Albanian Geological Survey (Shërbimi Gjeologjik Shqiptar), Tirana'],
        ['1996–2006', '[position]', 'Albpetrol, the national oil company, Albania'],
    ],
    expertise=[
        '**Seawater intrusion and monitoring design:** goal-oriented Bayesian design of monitoring networks and of '
        'managed-aquifer-recharge wells for variable-density seawater intrusion (Journal of Hydrology, 2026).',
        '**Inference and uncertainty in alluvial aquifers:** Bayesian porosity inference with dependent errors; '
        'groundwater vulnerability (DRASTIC) coupled with numerical transport models (2026).',
        '**Stochastic modelling of flow and transport:** coupled geomechanical, geochemical and flow models of fractured '
        'and karst media; fracture initiation and propagation under fluid injection (2021–2022).',
        '**Optimisation under uncertainty:** placement and rates of wells; scheduling of field projects.',
        '**Modelling software and field background:** C++, Python and MATLAB; ten years in oil production (Albpetrol) and '
        'two years at the Albanian Geological Survey.',
    ],
    pubs=[
        ('**Zeqiraj, D.** (2026). Goal-oriented Bayesian experimental design for variable-density seawater intrusion: '
         'Adjoint expected information gain for joint monitoring and managed-aquifer-recharge placement. Journal of '
         'Hydrology 680, 136559.', 'https://doi.org/10.1016/j.jhydrol.2026.136559'),
        ('**Zeqiraj, D.**, Beqiraj, A. (2026). Adaptive stacked ensemble fusion: Bayesian porosity inference in alluvial '
         'aquifers when the errors are not independent. Journal of Contaminant Hydrology 283, 105086.',
         'https://doi.org/10.1016/j.jconhyd.2026.105086'),
        ('**Zeqiraj, D.**, Beqiraj, A., Jahja, A., Seitaj, B., Progni, F., Zeqo, E. (2026). Physical, biophysical, and '
         'chemical mechanisms of bidirectional coupling between DRASTIC vulnerability assessment and numerical transport '
         'modeling in heterogeneous aquifer systems. Journal of Hazardous Materials Advances 23, 101261.',
         'https://doi.org/10.1016/j.hazadv.2026.101261'),
        ('**Zeqiraj, D.** (2022). 3D stochastic modeling of flow and solute transport in karst vadose zone. Case Studies '
         'in Chemical and Environmental Engineering 6, 100217.', 'https://doi.org/10.1016/j.cscee.2022.100217'),
        ('**Zeqiraj, D.** (2022). Stochastic modeling of fracture initiation and propagation during fluid flow in '
         'carbonate reservoir. Results in Applied Mathematics 13, 100244.', 'https://doi.org/10.1016/j.rinam.2022.100244'),
        ('**Zeqiraj, D.** (2022). Stochastic modeling of fluid flow in the simulation and quantification of fracture '
         'initiation and propagation in the oil carbonate reservoirs during water injection. Results in Control and '
         'Optimization 7, 100131.', 'https://doi.org/10.1016/j.rico.2022.100131'),
        ('**Zeqiraj, D.** (2021). Fully coupled stochastic geomechanical - geochemical - reservoir modeling for fracture '
         'reservoirs. Results in Engineering 11, 100242.', 'https://doi.org/10.1016/j.rineng.2021.100242'),
    ],
    preprints=[
        ('**Zeqiraj, D.** (2026). Physics-informed deep learning for joint hydraulic conductivity–porosity mapping with '
         'Wasserstein optimal experimental design in alluvial aquifers. SSRN preprint.',
         'https://doi.org/10.2139/ssrn.7528503'),
        ('**Zeqiraj, D.**, Beqiraj, A. (2026). Class probabilities for groundwater nitrate vulnerability maps: hierarchical '
         'Bayesian calibration of DRASTIC against monitoring data, and the value of new stations. SSRN preprint.',
         'https://doi.org/10.2139/ssrn.7511860'),
    ],
    projects=[['2025–', 'Modelling, simulation and optimisation of formation treatment methods to maximise the net profit of the massive carbonate reservoir of the Amonicë oil field (with Albpetrol Sh.A.)', 'National Agency for Scientific Research and Innovation (AKKSHI), Albania', 'Project leader']],
    sps='[none]',
    users=[
        'Albanian Geological Survey (SHGJSH): staff member, 2006–2008.',
        'Albpetrol, the national oil company: production wells and reservoirs, 1996–2006; since 2025 partner of his AKKSHI '
        'project, with field data, well records and the validation of a 3D reservoir model (MATLAB-MRST).',
        'Preparatory work for CERTAIN-COAST (2026): reviews with numerical tests and a calibrated chloride model of the '
        'Fushë-Kuqe aquifer, which supplies Durrës.',
    ],
    teaching=[
        'Master courses: Reservoir Engineering (well stimulation and enhanced oil recovery); Energy Resources (fossil and '
        'renewable); Physics of Energy Resources.',
        '[number] doctoral and [number] master students supervised.',
    ],
    other=['Languages: Albanian (native); English [level]; [other languages]', 'Programming: C++, Python, MATLAB'],
)


def cv_filled(doc, d, role, role_text):
    # a CV with known facts filled in and no guidance lines; unknown facts stay highlighted
    p = para(doc, 0); ph(p, d['name'], size=15, bold=True)
    p = para(doc, 5); run(p, role + ', CERTAIN-COAST', bold=True, size=10.5, color='2E6DB4')
    sz = 9.2
    sec(doc, '1. Personal details')
    ph_table(doc, ['Item', 'Details'], d['details'], [4.2, 12.4], size=sz)
    sec(doc, '2. Education')
    ph_table(doc, ['Year', 'Degree', 'Institution', 'Field'], d['education'], [2.2, 3.8, 6.4, 4.2], size=sz)
    sec(doc, '3. Career')
    ph_table(doc, ['Years', 'Position', 'Institution'], d['career'], [2.2, 6.4, 8.0], size=sz)
    sec(doc, '4. Expertise relevant to CERTAIN-COAST')
    bullets_ph(doc, d['expertise'], size=sz + 0.3)
    sec(doc, '5. Selected publications (peer-reviewed, with DOI)')
    for i, (t, u) in enumerate(d['pubs'], start=1):
        p = para(doc, 1.5, 0.5); run(p, f'{i}. ', size=sz); ph(p, t + ' ', size=sz); link(p, u, u, sz)
    if d.get('preprints'):
        p = para(doc, 1.5, before=2); run(p, 'Preprints (2026):', bold=True, size=sz)
        for t, u in d['preprints']:
            p = para(doc, 1.5, 0.5); run(p, '• ', size=sz); ph(p, t + ' ', size=sz); link(p, u, u, sz)
    sec(doc, '6. Projects and grants')
    if d.get('projects'):
        ph_table(doc, ['Years', 'Project', 'Funder', 'Role'], d['projects'], [2.4, 6.6, 3.8, 3.8], size=sz)
    else:
        bullets_ph(doc, d['projects_bullets'], size=sz + 0.3)
    p = para(doc, 2, before=2); run(p, 'Other NATO SPS grants currently held: ', bold=True, size=sz); ph(p, d['sps'], size=sz)
    sec(doc, '7. Work with end-users and in the field')
    bullets_ph(doc, d['users'], size=sz + 0.3)
    sec(doc, '8. Teaching and supervision')
    bullets_ph(doc, d['teaching'], size=sz + 0.3)
    sec(doc, '9. Role in CERTAIN-COAST')
    p = para(doc, 3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; ph(p, role_text, size=sz + 0.3)
    sec(doc, '10. Other')
    bullets_ph(doc, d['other'], size=sz + 0.3)


def main_one(out, d, role, role_text):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.5)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)
    cv_filled(doc, d, role, role_text)
    doc.save(out)
    print('saved', out)


def main_npd(out):
    main_one(out, NPD, 'NATO-country Project Director', NPD_ROLE)


def main_ppd(out):
    main_one(out, PPD_CV, 'Partner-country Project Director', PPD_ROLE)
PPD_ROLE = ('As partner-country Project Director, leads training, transfer and dissemination (WP6) for the team of the '
            'Environmental Science Center of Qatar University: the transfer study on the east coast of Qatar (selection and '
            'characterisation of the site, local environmental knowledge and public data, and the interpretation of the '
            'outputs with the Tirana team), the two-month exchanges of early-career researchers to the Durrës coast, a '
            'regional workshop, and a user-side review of the bulletins and operating procedures.')

# ---------------------------------------------------------------------- the CV of the partner-country Project Director
# Source: Part 1 and Part 4 of the partner form returned by Qatar University on 9 November 2026 (professional data only;
# date of birth and contact data stay out of the repository). The DOI of the 2025 review was checked in Crossref.
PPD_CV = dict(
    name='Jassim Al-Khayat',
    details=[
        ['Name', 'Prof. Jassim Abdulla Al-Khayat'],
        ['Title and position', 'Research Professor and Manager of the research vessel Janan'],
        ['Institution', 'Environmental Science Center, Qatar University, Doha'],
        ['Country', 'Qatar (NATO partner country, Istanbul Cooperation Initiative)'],
        ['Nationality', 'Qatari'],
    ],
    education=[
        ['1993–1996', 'PhD, Marine Biology', 'University of Wales, United Kingdom', 'Marine biology'],
        ['1991–1992', 'MSc, Marine Biology and Fisheries', 'University of Aberdeen, United Kingdom', 'Marine biology and fisheries'],
        ['1979–1983', 'BSc, Marine Science / Geology', 'Qatar University', 'Marine science and geology'],
    ],
    career=[
        ['2021–', 'Research Professor and Manager of the research vessel Janan', 'Environmental Science Center, Qatar University'],
        ['2007–2021', 'Associate Professor and Coordinator of the Marine Sciences Program; Research Associate Professor',
         'Qatar University'],
        ['1996–2007', 'Assistant Professor, then Associate Professor and Head of the Marine Sciences Department',
         'Qatar University'],
    ],
    expertise=[
        '**Coastal and marine ecology:** mangroves, intertidal habitats, marine biodiversity and benthic communities; '
        'mangrove loss, restoration and adaptation to climate change.',
        '**Coastal sediments and carbon:** carbon storage and cycling in the sabkhas and mudflats of Qatar; microbial '
        'processes in carbonate mineral formation; carbon mineralisation in sabkhas.',
        '**Coastal pollution and monitoring:** oil residues, metals in mangrove sediments, microplastics in beach sediments; '
        'satellite-based assessment of suspended sediments and shorelines.',
        '**Field research and leadership:** head of the Marine Sciences Department, coordinator of the marine science '
        'programmes and manager of the research vessel Janan.',
    ],
    pubs=[
        ('Haseeba, K. P., Vethamony, P., Veerasingam, S., Aboobacker, V. M., **Al-Khayat, J. A.** (2025). A comprehensive '
         'review of oil residues in the world oceans: types, characteristics, sources and distribution. Marine Pollution '
         'Bulletin 217, 118106.', 'https://doi.org/10.1016/j.marpolbul.2025.118106'),
        ('Backer, S. A., Sankaran, R., Maruthavanan, R., **Al-Khayat, J.**, Vethamony, P., et al. (2026). The shoreline '
         'shifts: a comprehensive review of change analysis focusing Arabian Gulf within global context. Regional Studies '
         'in Marine Science 102, 105433.', 'https://doi.org/10.1016/j.rsma.2026.105433'),
        ('Ibrahim, S. B. M., Sankaran, R., Backer, S. J., Al Absi, R., Mohammed, A. V., **Al-Khayat, J. A.**, et al. (2026). '
         'Evaluation of mangrove ecosystem dynamics in the arid environment: for restoration on the Qatar coast using '
         'satellite data and hyperspectral imaging. Marine Pollution Bulletin 231, 119961.',
         'https://doi.org/10.1016/j.marpolbul.2026.119961'),
        ('Backer, S. J., Sankaran, R., **Al-Khayat, J. A.**, Vethamony, P., Rahman, M. M., Aravinth, J. (2026). Multi-decadal '
         'Landsat monitoring of shoreline dynamics in an enclosed arid gulf: comparison of 3-year and 10-year sampling '
         'designs. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing.',
         'https://doi.org/10.1109/JSTARS.2026.3747055'),
        ('**Al-Khayat, J.**, Veerasingam, S., Aboobacker, V. M., Vethamony, P. (2021). Hitchhiking of encrusting organisms on '
         'floating marine debris along the west coast of Qatar, Arabian/Persian Gulf. Science of the Total Environment 776, '
         '145985.', 'https://doi.org/10.1016/j.scitotenv.2021.145985'),
        ('**Al-Khayat, J. A.**, Vethamony, P., Nanajkar, M. (2021). Molluscan diversity influenced by mangrove habitat in '
         'the Khors of Qatar. Wetlands 41, 45.', 'https://doi.org/10.1007/s13157-021-01441-6'),
    ],
    preprints=[],
    projects=None,
    projects_bullets=[
        'Leads a five-year mangrove restoration project that assesses its environmental and socio-economic benefits.',
        'Has led a project on carbon mineralisation in sabkhas (microbial mats, minerals and carbon sequestration).',
        'Has led marine turtle conservation and monitoring programmes, and collaborative research with international '
        'institutions.',
    ],
    sps='None',
    users=[
        'Manager of the research vessel Janan of Qatar University: field campaigns, research teams and institutional '
        'collaboration.',
        'Environmental monitoring, conservation and habitat restoration on the coasts of Qatar.',
    ],
    teaching=[
        'Head of the Marine Sciences Department (to 2007) and Coordinator of the Marine Sciences Program (2007–2021), '
        'Qatar University.',
    ],
    other=['Honours: Outstanding Teaching Award, Qatar University (2015); National Incentive Award for Research, Qatar (2026).'],
)
NCD_ROLE = ('As additional NATO co-director, supervises InSAR time-series processing and the separation of elastic and inelastic '
            'compaction (WP1) and the use of ambient seismic noise as a water-table gauge (T4.4); hosts early-career researchers '
            'for training visits.')

NPD_GUIDE = ('3 to 5 lines linking your work to the hazard chain, for example coastal hydrogeology and seawater intrusion, field '
             'monitoring, groundwater chemistry, work on a coastal aquifer such as Fushë-Kuqe. Keep only what is true.')
PPD_GUIDE = ('3 to 5 lines on coastal geoscience, hydrogeology or water management in your country, on teaching and '
             'training, and on any work on a subsiding or intruded coast.')
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
    cv_filled(doc, NPD, 'NATO-country Project Director', NPD_ROLE)
    page_break(doc)
    cv_filled(doc, PPD_CV, 'Partner-country Project Director', PPD_ROLE)
    page_break(doc)
    cv(doc, '[Name of the additional NATO co-director]', 'Additional NATO co-director (optional)', NCD_DETAILS, NCD_GUIDE, NCD_ROLE)
    page_break(doc)
    ecr_profiles(doc)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--npd':
        main_npd(sys.argv[2])
    elif len(sys.argv) > 2 and sys.argv[1] == '--ppd':
        main_ppd(sys.argv[2])
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_CVs.docx')
