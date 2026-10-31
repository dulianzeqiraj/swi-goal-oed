"""CERTAIN-COAST (NATO SPS proposal): Executive summary. Key facts, eight headline figures, the problem, what the project
does, what is new, security relevance, objectives and results, the three years with their gates, team and end-users,
budget, risks and sustainability, and why NATO should fund it. Figures are computed from the other builders (budget,
risk register, running cost, objectives, milestones) so that the summary cannot drift from the detailed sections.

usage: python build_exec_summary.py OUT.docx"""
import os
import sys

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, heading, rich, table, shade  # noqa: E402
import build_budget as BB  # noqa: E402
import build_risk as BR  # noqa: E402
import build_sustainability as BS  # noqa: E402
import build_objectives as BO  # noqa: E402
import build_workplan as W  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')


def eur(x):
    return '€' + f'{x:,.0f}'


def facts():
    rows = BB.compute()
    total = sum(r['tot'] for r in rows)
    eq = sum(r['tot'] for r in rows if r['cat'] == 'Equipment') / total
    ppd = sum(r['ppd'] for r in rows) / total
    before, after = BR.counts(2, 3), BR.counts(8, 9)
    run_cost = sum(int(c[1].replace(' ', '')) for c in BS.COSTS)
    return dict(total=total, eq=eq, ppd=ppd, before=before, after=after, nrisk=len(BR.all_risks()), run_cost=run_cost)


def tiles(doc, items):
    t = doc.add_table(rows=2, cols=4); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for j, gc in enumerate(t._tbl.tblGrid.findall(qn('w:gridCol'))):
        gc.set(qn('w:w'), str(int(4.25 * 567)))
    tblPr = t._tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{side}'); e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '18'); e.set(qn('w:color'), 'FFFFFF'); b.append(e)
    tblPr.append(b)
    for k, (big, label) in enumerate(items):
        c = t.rows[k // 4].cells[k % 4]; c.width = Cm(4.25); shade(c, 'EAF0F8'); c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(5); p.paragraph_format.space_after = Pt(1)
        run(p, big, bold=True, size=17, color='1F3864')
        q = c.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER; q.paragraph_format.space_after = Pt(5)
        run(q, label, size=9, color='3A4450')
    for row in t.rows:
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))


def bullets(doc, items, size=10.5):
    for t in items:
        p = para(doc, 2, 0.5); run(p, '• ', bold=True, size=size); rich(p, t, size=size)


def main(out):
    F = facts()
    gates = {c: m for c, m, n, e in W.MILESTONES}
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.6)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Executive Summary', bold=True, size=18, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')

    KEY = [
        ['Programme', 'NATO Science for Peace and Security (SPS), Multi-Year Project, call 2027-1'],
        ['SPS Key Priorities', 'Environment, Climate Change and Security; Energy Security; Innovation and Emerging and Disruptive Technologies'],
        ['Site', 'Durrës coast, Albania: drinking-water wellfields, main port, energy landfall'],
        ['Duration and budget', f'36 months; {eur(F["total"])} requested, no salaries or overheads'],
        ['Project Directors', 'NATO country: Albania ([institution to confirm]); partner country: [eligible partner country, institution]'],
        ['End-users', 'Water utility, Durrës Port Authority, energy landfall operator, National Civil Protection Agency'],
    ]
    t = table(doc, ['', ''], KEY, [4.0, 13.0], size=9.5)
    t._tbl.remove(t.rows[0]._tr)
    for r in t.rows:
        shade(r.cells[0], 'E8EDF5')
        for par in r.cells[0].paragraphs:
            for rn in par.runs:
                rn.bold = True
    para(doc, 4)
    tiles(doc, [
        ('36 months', 'duration'),
        (eur(F['total']), 'requested from NATO SPS'),
        ('3 hazards', 'intrusion, liquefaction, extreme sea level: one model'),
        ('3 assets', 'wellfields, port, energy landfall'),
        ('5–10%', 'certified miss rate per alarm (indicative)'),
        ('12 months', 'live operation with the operators'),
        ('20 + 6', 'operator staff and early-career researchers trained'),
        (f'≈{eur(round(F["run_cost"], -3))}/yr', 'running cost after hand-over'),
    ])

    heading(doc, 'The problem', 13, before=8)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'Within a few kilometres of the Durrës coast stand three kinds of critical infrastructure of a NATO member: the '
            'wellfields that supply drinking water, the country\'s main port and an energy landfall. The ground beneath them is '
            'soft and subsiding, next to active faults; the 26 November 2019 Mw 6.4 earthquake caused liquefaction along this '
            'coast. Seawater intrusion, liquefaction and extreme sea levels are driven by the same variables, the relative sea '
            'level and the water table, so pumping, subsidence and storms move all three at once. Yet they are monitored and '
            'modelled separately, and **no warning states how often it misses**, which is what a security decision needs.')

    heading(doc, 'What CERTAIN-COAST does', 13, before=6)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'The project builds, demonstrates and hands over **one early-warning system for the three hazards**. InSAR, GNSS '
            'and sea-level data give the relative sea level at each asset. One calibrated physical model couples '
            'variable-density groundwater flow, aquifer compaction, the liquefaction factor of safety under a moving water table '
            'and extreme water levels; a fast surrogate with a certified error bound runs it in real time. Each alarm carries a '
            'margin that guarantees its miss rate stays below an agreed target, even beyond the observed record. A monitoring '
            'network designed for these warnings feeds the system, which the operators run live for twelve months and then own.')

    heading(doc, 'What is new', 13, before=6)
    bullets(doc, [
        '**One model for three hazards.** Intrusion, liquefaction and extreme sea level are coupled through their shared variables, so every pumping decision is checked against all three: more pumping raises intrusion and subsidence but lowers liquefaction susceptibility.',
        '**Warnings with a certified miss rate.** Each margin adds a surrogate error bound, online conformal risk control and an extreme-aware term; the miss rate of each alarm is bounded, and the joint miss rate by the sum. In preparatory synthetic tests the share of seasons above the chloride limit stayed at 4–9%, where a static alarm allowed 13–21%.',
        '**Relative sea level where it matters**, at each asset, from the differential land motion between the tide gauge and the asset.',
        '**Sensors chosen for the warnings:** every sensor type, from a piezometer to a fibre, ranked by how much it shrinks the alarm margins per euro.',
        '**Seismic noise as a water-table gauge** in the saturated sediments where liquefaction is decided.',
    ])

    heading(doc, 'Why it matters for security', 13, before=6)
    bullets(doc, [
        'Protects an Ally\'s **water supply, main port and energy landfall** together, three of NATO\'s baseline requirements for national resilience (water, energy, transport).',
        'Covers the threats to critical undersea infrastructure **where it comes ashore**, which maritime surveillance does not see.',
        'Brings **machine learning into a security decision chain responsibly**: every forecast has an error bound, every bulletin is logged, and people decide, in line with NATO\'s principles of responsible use of AI.',
    ])

    heading(doc, 'Objectives and results', 13, before=6)
    rows = [[code, title, deliv] for code, title, _, _, deliv, _ in BO.OBJ]
    t = table(doc, ['', 'Objective', 'Deliverables (month)'], rows, [1.2, 7.6, 8.2], size=9.5)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    p = para(doc, 4, before=3)
    rich(p, 'Results include at least six open-access papers, open software and data (Month 33), operating procedures adopted '
            'by each operator and a policy brief for the national authorities (Month 36).', size=10)

    heading(doc, 'Three years, three evidence gates', 13, before=6)
    bullets(doc, [
        f'**Year 1, measure and build:** coastal motion and relative sea level at each asset; network designed (Month 6) and streaming (Month 12).',
        f'**Year 2, model and certify:** coupled model calibrated (gate MS3, Month {gates["MS3"]}); certified surrogate and go/no-go (gate MS4, Month {gates["MS4"]}); live bulletins from Month 23.',
        f'**Year 3, operate and hand over:** miss-rate targets confirmed in back-testing (gate MS5, Month {gates["MS5"]}); twelve months of live operation to Month 34; operators issue every bulletin in Months 34–36; hand-over in Month 36.',
    ])

    heading(doc, 'Team and end-users', 13, before=6)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'The NATO-country team in Albania coordinates the project and leads the network and the live demonstration; the '
            'partner-country team leads the coupled model, the certified alarms and the transfer, including a test of the method '
            'on a subsiding coast of its own country. The four end-users co-design the thresholds from the first year, receive the '
            'bulletins and run the system after the project; each confirms its role in a commitment letter.')

    heading(doc, 'Budget, risks and sustainability', 13, before=6)
    b, a = F['before'], F['after']
    bullets(doc, [
        f'**Budget:** {eur(F["total"])} over 36 months, within the typical SPS range; equipment {100 * F["eq"]:.0f}% because a monitoring network is installed and handed over; every line is quantity × unit cost.',
        f'**Risks:** {F["nrisk"]} risks with owners and numeric triggers; before mitigation {b["Very high"]} very high and {b["High"]} high, after mitigation none high or very high. The largest operational risk, a missed hazard, has a measured bound.',
        f'**Sustainability:** the operators own the network and software, have adopted procedures and share a running cost of about {eur(round(F["run_cost"], -3))} per year; the alarm margins keep recalibrating themselves from every logged outcome after the project.',
    ])

    heading(doc, 'Why NATO should fund CERTAIN-COAST', 13, before=6)
    bullets(doc, [
        '**A working service, not a report:** at Month 36 the operators issue certified warnings themselves.',
        '**A guarantee that can be checked:** the miss rate of every warning is stated in advance and verified against the bulletin log, and the verification statistics are published.',
        '**Security and openness together:** methods, code and verification are open; asset-level vulnerability stays with the operators and authorities.',
        '**Transferable:** free satellite data, existing stations and open software let other subsiding coasts with wellfields, ports and energy landfalls of Allies and partners repeat the approach.',
    ])
    p = para(doc, 2, before=6)
    run(p, 'Placeholders in square brackets are to be completed when the partner-country institution is named. The detailed '
           'sections (State of the Art to Timeline) give the evidence behind every statement.', italic=True, size=9, color='52606D')
    doc.save(out)
    print('saved', out, '| budget', F['total'], '| running', F['run_cost'], '| risks', F['before'], F['after'])


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Executive_Summary.docx')
