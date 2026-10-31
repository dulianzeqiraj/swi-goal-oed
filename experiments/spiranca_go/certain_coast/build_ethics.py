"""CERTAIN-COAST (NATO SPS proposal): Ethics. Frameworks (SPS civil science, Albanian Law No. 124/2024 on personal data
protection, GDPR where applicable, NATO Principles of Responsible Use of AI, European Code of Conduct for Research
Integrity, EU AI Act for reference), an ethics self-assessment, responsible use of AI mapped to the six NATO
principles, the ethics of issuing warnings, data protection, environment, health and safety, research integrity,
governance, what is new, and a short paragraph for the application form.

usage: python build_ethics.py OUT.docx"""
import os
import sys

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, heading, rich, table, shade, link  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')

LEAD = ('CERTAIN-COAST raises no ethical issues of the kind that involve animals, human tissue or clinical research. Its '
        'ethical questions are of a different kind and are central to the project: it works with people and their data, '
        'with security-sensitive information about critical infrastructure, with machine learning used in safety '
        'decisions, with field work and drilling on the coast, and above all with warnings that people will act on. The '
        'project handles these with the same discipline as its science: each issue has a named measure, a responsible '
        'person and a check, and the most important one, the honesty of a warning, is made measurable.')

FRAMEWORKS = [
    '**NATO SPS** supports security-related civilian science; grants may carry additional conditions recommended by the Independent Scientific Evaluation Group or by NATO, which the project will apply.',
    '**Albania, Law No. 124/2024 "On Personal Data Protection"**, aligned with the EU General Data Protection Regulation and supervised by the Information and Data Protection Commissioner; the **GDPR** applies to any partner in the EU, and the partner country\'s own law to the partner-country team.',
    '**NATO Principles of Responsible Use of Artificial Intelligence** (2021 AI Strategy): lawfulness; responsibility and accountability; explainability and traceability; reliability; governability; bias mitigation.',
    '**The European Code of Conduct for Research Integrity** (ALLEA, revised 2023) for all research practice.',
    '**For reference, the EU AI Act** (Regulation (EU) 2024/1689) lists AI used as a safety component in the supply of water, gas, heating or electricity among high-risk uses; although it does not apply in Albania, the project follows its main requirements voluntarily.',
]
SOURCES = [
    ('Law No. 124/2024 (Albanian Commissioner)', 'https://idp.al/wp-content/uploads/2025/03/Law-no.124-2024.pdf'),
    ('Summary of the NATO AI Strategy (2021)', 'https://www.nato.int/en/about-us/official-texts-and-resources/official-texts/2021/10/22/summary-of-the-nato-artificial-intelligence-strategy'),
    ('European Code of Conduct for Research Integrity', 'https://allea.org/code-of-conduct/'),
    ('EU AI Act, Regulation (EU) 2024/1689', 'https://eur-lex.europa.eu/eli/reg/2024/1689/oj'),
]

SELF = [
    ['People taking part (workshops, training, interviews, tests of the bulletins)', 'Yes',
     'Voluntary participation with informed consent and the right to withdraw; approval of the institutional ethics committee before any interview or survey; no vulnerable groups are targeted', 'T3.1, T5.1, T6.2'],
    ['Personal data', 'Yes',
     'Only what is needed (names, contacts, role, participation by sex); pseudonymised for analysis; stored on partner servers with access control; deleted at the end of the retention period', 'T7.2'],
    ['Confidential operator data', 'Yes',
     'Access agreements; restricted tier; encrypted storage; no transfer outside the consortium without the operator\'s consent', 'T7.2; R20'],
    ['Security-sensitive results and misuse', 'Yes',
     'Two-tier dissemination and release gate; asset-level vulnerability shared only with operators and authorities', 'Dissemination Plan'],
    ['Dual use and export control', 'To check',
     'Civilian aims only; export classification of GNSS, seismic and fibre-sensing equipment and of software checked with suppliers and national authorities before purchase and shipment', 'T4.2'],
    ['Artificial intelligence in safety decisions', 'Yes',
     'Six NATO principles applied (Section 2); human oversight; full logs', 'WP2, WP3, WP5'],
    ['Environment, health and safety', 'Yes',
     'Permits for drilling and installation; boreholes sealed and logged; field safety plan; removal or hand-over of all equipment at the end', 'WP4; R12, R13'],
    ['Partner outside NATO', 'Yes',
     'Equal partnership; data transfer agreements; local ethics approval and data law respected in each country', 'Partnership'],
    ['Animals, human tissue, clinical research', 'No', '—', '—'],
    ['Military applications', 'No',
     'The project is civilian; its results protect critical civilian infrastructure and are not designed for weapons or targeting', '—'],
]

AI = [
    ['Lawfulness', 'Used only within the operators\' legal mandates and in line with data protection law.'],
    ['Responsibility and accountability', 'Every decision stays with named operator staff; each bulletin is logged with its inputs, model version, margin and outcome; roles are written into the bulletin protocol (T5.1).'],
    ['Explainability and traceability', 'Each bulletin shows the forecast, the margin and its three parts, and the certified miss rate; any bulletin can be reproduced from the log and the open code.'],
    ['Reliability', 'An error bound for every forecast of the surrogate; miss rates certified, back-tested and checked in operation; data integrity checks against tampering.'],
    ['Governability', 'Operators can override, pause or return to manual procedures at any time; if the error bound fails, the system falls back to the full model or a wider margin; live use only after the go/no-go milestone (MS4).'],
    ['Bias mitigation', 'Miss and false-alarm rates are checked separately for each asset, season and type of event, so that no area or condition is served worse; gaps in the data are quantified, not hidden.'],
]

WARN = [
    '**Honesty about uncertainty.** No bulletin claims more certainty than it has: each states how often such warnings miss, and that rate is checked against the log.',
    '**Who bears the error is decided openly.** The trade-off between misses and false alarms is agreed with the operators before the alarms are designed, and tolerances are allocated by consequence, not by convenience (Methodology, Section 5.4).',
    '**Official warnings stay with the authorities.** CERTAIN-COAST bulletins go to the operators and civil protection; any warning to the public is issued only by the competent authorities through their own channels.',
    '**Misses are reviewed, not hidden.** Every missed exceedance is reviewed within a week, and the findings are shared with the operators and civil protection.',
    '**No false reassurance.** When conditions leave the observed record, the bulletin says so and the margin widens, rather than presenting a forecast as reliable where it is not.',
]

DATA = [
    '**What is collected:** names, contact details and roles of participants; participation by sex and age band for the gender and inclusion indicators; notes from interviews and tests of the bulletins.',
    '**Legal basis:** consent for interviews and tests; the partners\' legitimate interest for project contact data; information sheets in Albanian and English.',
    '**Protection:** pseudonymisation for analysis; storage on partner servers in the partner countries with access control and encryption; no personal data in published datasets.',
    '**Rights:** participants can access, correct or delete their data and withdraw consent at any time; each partner\'s data protection officer is the contact point.',
    '**Retention:** personal data are kept only as long as needed for the project and its reporting, then deleted; breaches are reported to the competent authority as the law requires.',
]

EHS = [
    '**Permits and consent of owners** for drilling, installation and access, obtained before any field work.',
    '**Protection of the aquifer:** boreholes designed and sealed so that they do not connect fresh and saline layers, with conductivity logged before and after (R12).',
    '**Safety of people:** field safety plan, inductions at each site, two-person rule and no field work during active warnings (R13).',
    '**Clean exit:** equipment not handed over is removed at the end; batteries and electronic waste are disposed of through licensed channels.',
]

INTEGRITY = [
    '**A fixed test before the results.** The back-testing protocol (data, issue times, metrics) is written down and frozen before the results are seen, so the reported miss rates cannot be tuned after the fact.',
    '**Negative results reported.** Misses, failed tests and limitations are reported in the papers and progress reports, not only successes.',
    '**Authorship and credit** agreed in the publication plan, with contributions stated for each paper; early-career researchers credited for their work.',
    '**Conflicts of interest declared:** the operators are both partners and users of the system; their role in thresholds and publication review is limited to their own assets and to sensitive content.',
    '**Open methods and data** in line with the two-tier dissemination plan.',
]

GOVERN = [
    '**Ethics contact point and independent advisor.** A member of the steering committee is the ethics contact point; an independent ethics advisor, not involved in the research, reviews the ethics and data plan and any issue raised.',
    '**Approvals before activities.** Ethics committee approvals, permits and export checks are obtained before the activity they concern, and recorded.',
    '**Data management and ethics plan** delivered with the access agreements in Month 3 (T7.2) and updated each year.',
    '**Review and reporting.** Ethics is a standing item at each steering-committee meeting and a section of each progress report to the SPS Programme.',
]

NEW = [
    '**The ethics of a warning made measurable.** Honesty about uncertainty is not a promise but a number: every bulletin carries its certified miss rate, and the log shows whether it held.',
    '**Responsible AI by construction.** The machine-learned surrogate never acts alone: each forecast carries its own error bound, the system falls back automatically when the bound fails, and a person decides.',
    '**The burden of error shared openly.** Who bears the cost of a miss and who bears the cost of a false alarm is agreed with the operators in advance, rather than hidden in a threshold.',
    '**Integrity protected by a frozen test.** The back-testing protocol is fixed before the results are seen, so the central claim of the project cannot be tuned after the fact.',
    '**Openness without harm.** The release gate lets the project publish its methods and its verification openly while keeping asset-level vulnerability away from those who could misuse it.',
]

SHORT = ('CERTAIN-COAST involves no animals, human tissue or clinical research. Its ethical issues are people and their data, '
         'security-sensitive information about critical infrastructure, machine learning in safety decisions, field work and '
         'the responsibility of issuing warnings. Participants in workshops, interviews and tests of the bulletins take part '
         'voluntarily with informed consent, after institutional ethics approval; personal data are minimised, pseudonymised '
         'and protected under Albania\'s Law No. 124/2024, aligned with the GDPR. Asset-level vulnerability results are shared '
         'only with operators and authorities through a release gate. The machine-learned surrogate follows NATO\'s six '
         'principles of responsible AI: every forecast carries an error bound, every bulletin is logged and reproducible, and '
         'operators keep the decision. Each bulletin states its certified miss rate, the miss-false-alarm trade-off is agreed '
         'with the operators in advance, public warnings remain with the authorities, and the back-testing protocol is frozen '
         'before results are seen. An independent ethics advisor and a yearly review oversee these measures.')


def tidy(t):
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    keep = t.rows[:-1] if len(t.rows) <= 6 else (t.rows[0], t.rows[1], t.rows[-2])
    for row in keep:
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.keep_with_next = True
    return t


def bullets(doc, items, size=11):
    for t in items:
        p = para(doc, 3, 0.5); run(p, '• ', bold=True, size=size); rich(p, t, size=size)


def main(out):
    n_short = len(SHORT.split())
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Ethics', bold=True, size=18, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, LEAD, size=11.5)

    heading(doc, 'Rules and frameworks applied', 13, before=4)
    bullets(doc, FRAMEWORKS, size=10.5)
    p = para(doc, 2, before=3); run(p, 'Sources: ', bold=True, size=9.5, color='52606D')
    for i, (t, u) in enumerate(SOURCES):
        link(p, u, t, 9.5)
        if i < len(SOURCES) - 1:
            run(p, '; ', size=9.5, color='52606D')

    heading(doc, '1. Ethics self-assessment', 13.5, before=10)
    p = para(doc, 3); run(p, 'Table 1. Ethical issues, whether they apply, and how they are handled.', italic=True, size=10, color='52606D')
    p.paragraph_format.keep_with_next = True
    t = tidy(table(doc, ['Issue', 'Applies', 'How it is handled', 'Where'], SELF, [4.4, 1.6, 8.4, 2.6], size=9.5))
    colors = {'Yes': 'FFF1C2', 'No': 'DCEFE3', 'To check': 'F9D3B4'}
    for i, r in enumerate(SELF, start=1):
        shade(t.rows[i].cells[1], colors[r[1]])
    para(doc, 4)

    heading(doc, '2. Responsible use of artificial intelligence', 13.5, before=8)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'A machine-learned surrogate of the physical model produces the forecasts behind safety decisions at critical '
            'infrastructure. Each of NATO\'s six principles is met by a concrete measure:')
    p = para(doc, 3); run(p, 'Table 2. NATO Principles of Responsible Use and how CERTAIN-COAST meets them.', italic=True, size=10, color='52606D')
    p.paragraph_format.keep_with_next = True
    tidy(table(doc, ['Principle', 'Measure in CERTAIN-COAST'], AI, [4.4, 12.6], size=10))
    para(doc, 4)

    heading(doc, '3. The ethics of issuing warnings', 13.5, before=8)
    bullets(doc, WARN)
    heading(doc, '4. Data protection', 13.5, before=8)
    bullets(doc, DATA)
    heading(doc, '5. Environment, health and safety', 13.5, before=8)
    bullets(doc, EHS)
    heading(doc, '6. Research integrity', 13.5, before=8)
    bullets(doc, INTEGRITY)
    heading(doc, '7. Ethics governance', 13.5, before=8)
    bullets(doc, GOVERN)
    heading(doc, '8. What is new in this ethics approach', 13.5, before=8)
    bullets(doc, NEW)
    heading(doc, f'9. Short paragraph for the application form ({n_short} words)', 13.5, before=8)
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, SHORT)
    doc.save(out)
    print('saved', out, '| short paragraph', n_short, 'words')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Ethics.docx')
