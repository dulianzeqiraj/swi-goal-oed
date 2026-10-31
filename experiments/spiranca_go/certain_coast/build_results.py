"""CERTAIN-COAST (NATO SPS proposal): Expected results. What will exist at the end, results by type with measures of
success, a results table (deliverable, month, indicator, end user), security contribution, impact over time,
sustainability and dissemination. Consistent with the Objectives (O1-O6) and the Work Plan (WP1-WP7, 36 months)."""
import os
import sys
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_sota import run, para, heading, rich, table  # noqa: E402

LEAD = ('At the end of the project the Durrës coast will have something no coast has today: one early-warning system for '
        'seawater intrusion at the wellfields, liquefaction at the port and the energy landfall, and extreme sea levels at all three, '
        'driven by one physical model of the coast, issued fast enough to act on, and carrying a stated, verified bound on how often '
        'each warning misses. It will be run by the operators themselves, and the methods behind it will be open and transferable '
        'to other subsiding coasts.')

GROUPS = [
    ('1. Scientific results', [
        ('R1', 'The relative sea level of a subsiding Adriatic coast, measured', 'Time series R(t) = η(t) − u_z(t) with uncertainty at every asset, the vertical land motion separated into elastic (reversible) and inelastic (permanent) compaction, the pumping rate the land can sustain, and the coseismic and postseismic motion of 2019. (WP1, D1.1)'),
        ('R2', 'The first coupled model of intrusion, liquefaction and extreme sea level through their shared variables', 'One calibrated model in which relative sea level and the water table drive all three hazards, including the water-table-dependent factor of safety FS(x, t) = CRR / CSR(z_w(x, t)); the first quantification, at one site, of how pumping moves the three hazards in opposite directions. (WP2, D2.1)'),
        ('R3', 'Certified alarms with proofs', 'Alarm margins combining a surrogate error bound, online conformal risk control and an extreme-aware term, with proofs that the miss rate of each alarm and the joint miss rate are bounded, and back-testing over the historical record and storylines beyond it. (WP3, D3.1, D3.2)'),
        ('R4', 'Seismic velocity as a pore-pressure sensor in saturated coastal sediments', 'A calibrated relation between seismic velocity change and water-table depth at the port or landfall, moving a method proven in dry and inland basins to the coastal setting where it matters for liquefaction. (WP4, T4.4)'),
        ('R5', 'The value of each sensor type for the warnings', 'A ranking of piezometers, chloride samples, GNSS, InSAR, seismic noise, nodes and fibre by how much each reduces the miss probability of the three warnings per unit cost, the first such multi-hazard design. (WP4, D4.1)'),
    ]),
    ('2. Technological results', [
        ('R6', 'A monitoring network designed for the warnings', 'Piezometers with conductivity loggers, chloride sampling points, GNSS and corner reflectors, seismic sensors and, where access is granted, fibre-optic sensing, installed, streaming and handed over to the operators. (WP4, D4.2)'),
        ('R7', 'A certified fast surrogate of the coupled model', 'A neural or kernel operator that runs thousands of storylines per day with an error bound attached to each forecast. (WP2, D2.2)'),
        ('R8', 'The CERTAIN-COAST warning system', 'The operational chain from data to bulletin: assimilation, surrogate forecast, certified margin, alarm and bulletin to each end user, released as open software with documentation and the project data. (WP5, WP6, D6.1)'),
    ]),
    ('3. Operational results for the end users', [
        ('R9', 'Twelve months of live operation', 'Bulletins issued to the water utility, the port authority, the landfall operator and civil protection, each logged with its outcome, so that the certified miss rates can be checked in practice. (WP5, D5.1)'),
        ('R10', 'A pumping rule that is safe for all three hazards', 'An operating rule for the wellfields, agreed with the utility, that keeps the intrusion, liquefaction and extreme-sea-level alarms within their targets together. (WP5, T5.3)'),
        ('R11', 'A post-event protocol', 'Measurements of heads, conductivity, chloride, ground motion and seismic velocity within days of a strong earthquake or surge, turning each event into data for the system. (WP5, T5.4)'),
    ]),
    ('4. Capacity and policy results', [
        ('R12', 'People who can run and develop the system', 'Early-career researchers trained by doing the work, and staff of the operators and civil protection trained to run the system without the project team. (WP6, T6.1, T6.2)'),
        ('R13', 'Procedures and a policy brief', 'Operating procedures adopted by the operators of the wellfields, the port and the landfall, and a policy brief for the national authorities on coastal subsidence, water supply and critical-infrastructure protection. (WP6, D6.2)'),
    ]),
]

TABLE = [
    ['R1', 'Relative sea level and land motion at the assets', 'D1.1, M12', 'Vertical-velocity uncertainty of the order of 1–2 mm/yr at asset points', 'All operators; authorities'],
    ['R2', 'Coupled model of the three hazards', 'D2.1, M18', 'Held-out observations reproduced within stated uncertainty', 'Project; utility'],
    ['R3', 'Certified alarms with proofs', 'D3.1–D3.2, M24–27', 'Miss rate of each alarm ≤ α_k (indicatively 5–10%) in back-testing; joint miss ≤ Σα_k', 'All operators'],
    ['R4', 'Seismic velocity as pore-pressure sensor', 'T4.4, M24', 'Calibrated relation with stated uncertainty at the port or landfall', 'Port; landfall operator'],
    ['R5', 'Value of each sensor type', 'D4.1, M6', 'Ranked design adopted for the network', 'Project; operators'],
    ['R6', 'Monitoring network', 'D4.2, M12', '≥ 90% data availability; handed over at M36', 'Utility; port; landfall operator'],
    ['R7', 'Certified surrogate', 'D2.2, M22', 'Error bound met on the test set; thousands of storylines per day', 'Project'],
    ['R8', 'Warning system, software and data', 'D6.1, M33', 'Open release with documentation', 'Operators; researchers'],
    ['R9', 'Twelve months of live operation', 'D5.1, M34', 'Bulletin log; observed miss rates within targets', 'Utility; port; landfall operator; civil protection'],
    ['R10', 'Pumping rule safe for three hazards', 'T5.3, M33', 'Rule agreed with the utility and documented', 'Water utility'],
    ['R11', 'Post-event protocol', 'T5.4, M12–36', 'Executed for every triggering event', 'Civil protection; operators'],
    ['R12', 'Trained people', 'T6.1–T6.2, M36', 'Indicatively ≥ 6 early-career researchers and ≥ 20 operator staff', 'Partner institutions; operators'],
    ['R13', 'Procedures and policy brief', 'D6.2, M36', '≥ 1 procedure adopted per asset; brief delivered', 'Operators; national authorities'],
]

SECURITY = [
    '**Water security.** The wellfields supply drinking water; an intrusion warning with a guaranteed miss rate protects supply before the wells turn saline, which takes years to reverse.',
    '**Port and logistics security.** The port is a national logistics node; a liquefaction and extreme-sea-level warning protects operations and the infrastructure behind them.',
    '**Energy security.** The energy landfall connects supply to the national system; its stability under shaking, liquefaction, extreme water levels and subsidence is assessed in one framework.',
    '**Civil protection and resilience.** One system for three hazards, with a post-event protocol, gives civil protection a consistent picture after an earthquake or a storm, instead of three separate ones.',
    '**Transferability.** The methods need only free satellite data, existing fibre and seismic stations, and a calibrated model; they transfer to other subsiding coasts with wellfields, ports and energy landfalls, in the Adriatic and beyond.',
]

IMPACT = [
    ['During the project (M1–M36)', 'Coastal motion known; network and model in place; certified warnings issued to the operators for twelve months; staff trained'],
    ['After hand-over (1–3 years)', 'Operators run the system and the pumping rule; the network continues to stream; the record of warnings and outcomes grows and keeps the guarantees checked'],
    ['Longer term', 'Coastal planning and civil protection use relative sea level instead of a fixed trend; the approach is adopted on other subsiding coasts; certified warning becomes the expected standard for critical coastal infrastructure'],
]

SUSTAIN = [
    '**Low running cost.** Satellite data are free; fibre and seismic stations already exist or are installed by the project; the surrogate runs on ordinary computers.',
    '**Ownership.** The network and the system are handed over to the operators, who are trained to run them and adopt the procedures (R12, R13).',
    '**Open licences.** Software, documentation and project data are released openly, so the system does not depend on any single partner (R8).',
    '**Self-checking.** Every bulletin is logged with its outcome, so the operators can see whether the certified miss rates still hold, and recalibrate if they do not.',
]

DISSEM = [
    'Peer-reviewed open-access publications on the coupled model, the certified alarms, the seismic sensing of the water table and the coastal motion (indicatively at least six).',
    'A final workshop with the operators, civil protection and national authorities, and a demonstration of the system in operation.',
    'Presentations at international conferences on geohazards, coastal groundwater and uncertainty quantification.',
    'Open software, data and training material, so that others can repeat the analysis on their own coasts.',
]


def main(out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Expected Results', bold=True, size=18, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and energy landfall of a subsiding Adriatic coast', bold=True, size=12, color='1F3864')
    p = para(doc, 8); rich(p, LEAD, size=11.5)
    for gtitle, items in GROUPS:
        heading(doc, gtitle, 13.5, before=6)
        for code, title, text in items:
            p = para(doc, 2); p.paragraph_format.keep_with_next = True
            run(p, f'{code}. ', bold=True, color='1F3864'); run(p, title, bold=True)
            p = para(doc, 5, 0.5); rich(p, text)
    heading(doc, '5. Results at a glance', 13.5, before=8)
    table(doc, ['', 'Result', 'Where and when', 'Measure of success', 'End user'], TABLE, [1.1, 4.0, 2.7, 5.2, 4.0], size=9.5)
    para(doc, 4)
    heading(doc, '6. Contribution to security', 13.5)
    for t in SECURITY:
        p = para(doc, 3, 0.5); run(p, '• ', bold=True); rich(p, t)
    heading(doc, '7. Impact over time', 13.5, before=8)
    table(doc, ['Horizon', 'Expected impact'], IMPACT, [4.0, 13.0], size=10)
    para(doc, 4)
    heading(doc, '8. Sustainability after the project', 13.5)
    for t in SUSTAIN:
        p = para(doc, 3, 0.5); run(p, '• ', bold=True); rich(p, t)
    heading(doc, '9. Dissemination of the results', 13.5, before=8)
    for t in DISSEM:
        p = para(doc, 3, 0.5); run(p, '• ', bold=True); rich(p, t)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Expected_Results.docx')
