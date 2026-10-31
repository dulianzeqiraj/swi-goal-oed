"""CERTAIN-COAST (NATO SPS proposal): Conclusion. What the project will achieve (with headline figures computed from the
other builders), why it matters for NATO and its partners, why it can be done, five promises that can be checked at
Month 36 (each with how, when and what happens if it is not met), the closing request and what is new.

usage: python build_conclusion.py OUT.docx"""
import os
import sys

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, heading, rich, table, shade  # noqa: E402
import build_exec_summary as BE  # noqa: E402
import build_workplan as W  # noqa: E402
import build_deliverables as BD  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')

PROMISES = [
    ['Each alarm misses no more often than its certified rate αₖ (indicatively 5–10%)',
     'Back-testing over the record since 2014 and storylines beyond it (D3.2); twelve months of live bulletins checked against outcomes (D5.1); Clopper–Pearson intervals',
     'M27 (gate MS5); M34',
     'The margin is widened until the target is met; the target is kept and the extra false alarms are reported'],
    ['One model gives consistent warnings for water, port and energy',
     'Held-out heads, chloride, InSAR and seismic velocity inside the 90% predictive intervals (D2.1)',
     'M18 (gate MS3)',
     'Two-dimensional sections through each asset and a larger error bound; the limitation is stated'],
    ['Each user knows in advance what the warning is at least worth',
     'Guaranteed lower bound on relative value reported for each user\'s own decision (D5.1), with cost-loss ratios agreed in T3.1',
     'M34',
     'Where the bound is not positive, the threshold or the action is revised with that user'],
    ['The operators run the system themselves',
     'Operators issue every bulletin in Months 34–36; at least two trained people per operator; maintenance agreement signed',
     'M33–M36 (MS7)',
     'Extra training; the university hosts the system until the agreement is in place'],
    ['Others can repeat it',
     'Open software and data with a DOI (D6.1), installed and run on the synthetic coast by someone outside the team',
     'M33',
     'The release is fixed and tested again before it is accepted'],
]

NEW = [
    '**The conclusion ends with promises, not adjectives.** Five claims are stated so that the SPS Programme can check each one at Month 36, with the deliverable and month that prove it.',
    '**Each promise has a failure path.** What happens if a promise is not met is written down now, so a shortfall still produces a usable, honest result.',
    '**The figures cannot drift.** Budget, shares, risk counts, deliverables, milestones and running cost are computed from the same data as the Budget, Risk Assessment, Work Plan and Sustainability sections.',
]


def head_repeat(t):
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    return t


def bullets(doc, items, size=10.5):
    for x in items:
        q = para(doc, 3, 0.5); run(q, '• ', bold=True); rich(q, x, size=size)


def main(out):
    F = BE.facts()
    eur = BE.eur
    n_del = len(BD.items())
    n_ms = len(W.MILESTONES)
    b, a = F['before'], F['after']
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.7)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)

    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Conclusion', bold=True, size=18, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')

    heading(doc, '1. What CERTAIN-COAST will achieve', 13.5, before=2)
    p = para(doc, 5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'On one subsiding stretch of the Adriatic coast, the wellfields that supply drinking water, Albania\'s main port and an '
            'energy landfall are threatened by seawater intrusion, liquefaction and extreme sea levels through the same variables: '
            'relative sea level and the water table. Today they are watched separately, and no warning states how often it misses.',
         size=10.5)
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'At the end of the project the coast will have **one early-warning system for the three hazards, driven by one '
            'physical model, whose miss rate is certified in advance and verified in twelve months of live operation**, run by '
            'the operators themselves and open for other coasts to use.', size=10.5)
    BE.tiles(doc, [
        (eur(F['total']), 'requested, 36 months'),
        ('3 × 3', 'assets × hazards, one model'),
        ('≤ αₖ', 'certified miss rate per alarm'),
        ('12 months', 'live operation with the operators'),
        (f'{n_del}', f'deliverables; {n_ms} milestones'),
        ('3 gates', 'evidence decides each phase'),
        ('TRL 3 → 7', 'proof of concept to operation'),
        (eur(F['run_cost']) + '/yr', 'running cost after the grant'),
    ])

    heading(doc, '2. Why it matters for NATO and its partners', 13.5, before=8)
    bullets(doc, [
        '**Resilience of an Ally.** It protects water, transport and energy, three of NATO\'s seven baseline requirements for civil preparedness, at assets an Ally depends on in a crisis.',
        '**SPS Key Priorities.** Environment, Climate Change and Security; Energy Security; and Innovation and Emerging and Disruptive Technologies.',
        '**Responsible use of AI.** Machine learning enters a security decision chain only with a certified error bound and a verified miss rate, so it is accountable rather than a black box.',
        f'**Partner capacity.** The partner-country team manages {100 * F["ppd"]:.0f}% of the budget, leads the coupled model and the certified alarms, and takes the methods and open software home.',
    ])

    heading(doc, '3. Why it can be done', 13.5, before=8)
    bullets(doc, [
        '**Evidence before the project.** In preparatory synthetic tests, the extreme-aware alarm kept the share of seasons above the chloride limit at 4–9%, where a static alarm allowed 13–21%.',
        '**Users on board from the start.** The water utility, the port authority, the landfall operator and civil protection confirm their roles in commitment letters, agree the thresholds before live operation (T3.1, Months 13–15) and co-sign the operational milestones.',
        '**Decisions by evidence.** Three gates (Months 18, 22 and 27) with thresholds fixed in advance decide whether each phase starts; each has a named fallback.',
        f'**Risks under control.** {F["nrisk"]} risks with owners and numeric triggers; before mitigation {b["Very high"]} very high and {b["High"]} high, after mitigation none high or very high.',
        f'**A realistic budget.** {eur(F["total"])} over 36 months, every line quantity × unit cost; equipment {100 * F["eq"]:.0f}% because a monitoring network is installed and handed over to the operators.',
    ])

    heading(doc, '4. Five promises to check at Month 36', 13.5, before=8)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.keep_with_next = True
    rich(p, 'The project can be judged on five promises. Each names how and when it will be checked, and what happens if it is '
            'not met.', size=10.5)
    rows = [[f'{i}. {pr[0]}'] + pr[1:] for i, pr in enumerate(PROMISES, start=1)]
    t = head_repeat(table(doc, ['Promise', 'How it is checked', 'When', 'If it is not met'], rows, [4.2, 5.9, 2.2, 4.7], size=9.2))
    for r_ in t.rows[1:]:
        shade(r_.cells[0], 'EAF0F8')
        for c in r_.cells:
            for pp in c.paragraphs:
                pp.paragraph_format.keep_with_next = True

    heading(doc, '5. Our request', 13.5, before=10)
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, f'We ask the NATO Science for Peace and Security Programme to support CERTAIN-COAST with {eur(F["total"])} over 36 '
            'months. In return, an Ally\'s drinking water, main port and energy landfall will be protected by warnings whose '
            'reliability is known before they are issued and checked after, operated by the people responsible for those '
            'assets, and open to every Ally and partner with a similar coast.', size=10.5)

    heading(doc, '6. What is new in this conclusion', 13.5, before=8)
    bullets(doc, NEW)
    doc.save(out)
    print('saved', out, '|', F)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Conclusion.docx')
