"""CERTAIN-COAST (NATO SPS proposal): Expected results. What will exist at the end; fifteen results by type; a results
table (objective proved, deliverable and month, measure of success, main users); a figure of which user uses which
result; the minimum each key result still delivers if a gate or field condition fails; impact over time; where the
results go next; what is new. Consistent with the Objectives (O1-O6), the Work Plan and the Impact section (V1 = R14).

usage: python build_results.py OUT.docx"""
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
        ('R9', 'Twelve months of live operation', 'Bulletins issued to the water utility, the water resources agency (AMBU), the port authority, the landfall operator and civil protection, each logged with its outcome, so that the certified miss rates can be checked in practice. (WP5, D5.1)'),
        ('R10', 'A pumping rule that is safe for all three hazards', 'An operating rule for the wellfields, agreed with the utility, inside the certified safe operating window and its closing year, that keeps the intrusion, liquefaction and extreme-sea-level alarms within their targets together. (WP5, T5.3)'),
        ('R15', 'Safe pumping tests that certify more years', 'Short pumping and dewatering tests on existing wells, approved by the utility and kept below a chloride test limit, chosen for the years they add to the certified closing year of the window; in a second synthetic test they raised it from 10.8 to 31.9 years. (WP5, T5.3)'),
        ('R11', 'A post-event protocol', 'Measurements of heads, conductivity, chloride, ground motion and seismic velocity within days of a strong earthquake or surge, turning each event into data for the system. (WP5, T5.4)'),
        ('R14', 'A certified value of the warning for each user', 'For the decision each operator takes on a warning, a guaranteed lower bound on its relative economic value, derived from the certified miss rate and the cost-loss ratio agreed with that operator, reported with the value actually observed. (WP5, T3.1, D5.1)'),
    ]),
    ('4. Capacity and policy results', [
        ('R12', 'People who can run and develop the system', 'Early-career researchers trained by doing the work, and staff of the operators and civil protection trained to run the system without the project team. (WP6, T6.1, T6.2)'),
        ('R13', 'Procedures and a policy brief', 'Operating procedures adopted by the operators of the wellfields, the port and the landfall, and a policy brief for the national authorities on coastal subsidence, water supply and critical-infrastructure protection. (WP6, D6.2)'),
    ]),
]

TABLE = [
    ['R1', 'Relative sea level and land motion at the assets', 'D1.1, M12', 'Vertical-velocity uncertainty of the order of 1–2 mm/yr at asset points', 'All operators; authorities'],
    ['R2', 'Coupled model of the three hazards', 'D2.1, M18', 'Held-out observations reproduced within stated uncertainty', 'Project; utility'],
    ['R3', 'Certified alarms with proofs', 'D3.1–D3.2, M24–27', 'Miss rate of each alarm ≤ αₖ (indicatively 5–10%) in back-testing; joint miss ≤ Σαₖ', 'All operators'],
    ['R4', 'Seismic velocity as pore-pressure sensor', 'T4.4, M24', 'Calibrated relation with stated uncertainty at the port or landfall', 'Port; landfall operator'],
    ['R5', 'Value of each sensor type', 'D4.1, M6', 'Ranked design adopted for the network', 'Project; operators'],
    ['R6', 'Monitoring network', 'D4.2, M12', '≥ 90% data availability; handed over at M36', 'Utility; AMBU; port; landfall operator'],
    ['R7', 'Certified surrogate', 'D2.2, M22', 'Error bound met on the test set; thousands of storylines per day', 'Project'],
    ['R8', 'Warning system, software and data', 'D6.1, M33', 'Open release with documentation', 'Operators; researchers'],
    ['R9', 'Twelve months of live operation', 'D5.1, M34', 'Bulletin log; observed miss rates within targets', 'Utility; AMBU; port; landfall operator; civil protection'],
    ['R10', 'Pumping rule safe for three hazards', 'T5.3, M33', 'Rule agreed with the utility and documented', 'Water utility'],
    ['R11', 'Post-event protocol', 'T5.4, M12–36', 'Executed for every triggering event', 'Civil protection; operators'],
    ['R12', 'Trained people', 'T6.1–T6.2, M36', 'Indicatively ≥ 6 early-career researchers and ≥ 20 operator staff', 'Partner institutions; operators'],
    ['R13', 'Procedures and policy brief', 'D6.2, M36', '≥ 1 procedure adopted per asset; brief delivered', 'Operators; national authorities'],
    ['R14', 'Certified value for each user', 'D5.1, M34', 'Lower bound reported for each user and compared with the observed value', 'All operators; civil protection'],
    ['R15', 'Safe pumping tests valued in years', 'T5.3, M24–33', 'Every test below its chloride test limit; years added reported with the window', 'Water utility; national authorities'],
]

SECURITY = [
    '**Water security.** The wellfields supply drinking water; an intrusion warning with a guaranteed miss rate protects supply before the wells turn saline, which takes years to reverse.',
    '**Port and logistics security.** The port is a national logistics node; a liquefaction and extreme-sea-level warning protects operations and the infrastructure behind them.',
    '**Energy security.** The landfall of the Trans Adriatic Pipeline near Fier is where gas for Italy and Europe leaves the Albanian shore; its stability under shaking, liquefaction, extreme water levels and subsidence is assessed in one framework.',
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


OBJ_OF = {'R1': 'O1', 'R2': 'O2', 'R3': 'O3', 'R4': 'O4', 'R5': 'O4', 'R6': 'O4', 'R7': 'O2', 'R8': 'O6', 'R9': 'O5',
          'R10': 'O5', 'R11': 'O5', 'R12': 'O6', 'R13': 'O6', 'R14': 'O5', 'R15': 'O5'}
SHORT = {'R1': 'Relative sea level, land motion', 'R2': 'Coupled model of three hazards', 'R3': 'Certified alarms, proofs',
         'R4': 'Seismic velocity as sensor', 'R5': 'Value of each sensor type', 'R6': 'Monitoring network',
         'R7': 'Certified surrogate', 'R8': 'Warning system, software, data', 'R9': '12 months live operation',
         'R10': 'Pumping rule, three hazards', 'R11': 'Post-event protocol', 'R12': 'Trained people',
         'R13': 'Procedures, policy brief', 'R14': 'Certified value per user', 'R15': 'Safe pumping tests'}
USERS = ['Water\nutility', 'Port\nauthority', 'Landfall\noperator', 'Civil\nprotection', 'National\nauthorities', 'Scientists']
# 2 = main user, 1 = also uses, 0 = not a direct user
USE = {'R1': [1, 2, 2, 1, 2, 2], 'R2': [2, 1, 1, 0, 0, 2], 'R3': [2, 2, 2, 2, 0, 2], 'R4': [0, 2, 2, 0, 0, 2],
       'R5': [2, 1, 1, 0, 1, 2], 'R6': [2, 2, 2, 1, 0, 1], 'R7': [1, 1, 1, 0, 0, 2], 'R8': [2, 2, 2, 2, 1, 2],
       'R9': [2, 2, 2, 2, 1, 1], 'R10': [2, 1, 1, 0, 1, 1], 'R11': [1, 2, 2, 2, 1, 1], 'R12': [2, 2, 2, 2, 0, 2],
       'R13': [2, 2, 2, 1, 2, 0], 'R14': [2, 2, 2, 2, 0, 1], 'R15': [2, 0, 0, 0, 1, 2]}
TYPE_COL = {'1': '#2e6db4', '2': '#6a4fb3', '3': '#c27c12', '4': '#0e7490'}

MINIMUM = [
    ['R2 Coupled model', 'Gate MS3 not passed (coverage below 80%)', 'Two-dimensional sections through each asset with a larger error bound; the limitation stated in every result'],
    ['R3 Certified alarms', 'A miss rate above αₖ in back-testing (gate MS5)', 'Alarms with widened margins that meet the miss target; the extra false alarms reported'],
    ['R4 Seismic velocity sensor', 'No significant relation with the water table', 'Water table from piezometers alone; seismic velocity kept for post-event damage assessment'],
    ['R6 Monitoring network', 'Prices above the budget lines or site access refused', 'Sensors installed in order of value within the remaining budget, on the nearest accessible ground'],
    ['R7 Certified surrogate', 'Error bound not met in part of the domain (gate MS4)', 'Full model on a reduced domain for the flagged forecasts; margin widened automatically'],
    ['R9 Live operation', 'No strong earthquake or surge in twelve months', 'Event-based guarantees verified by back-testing and storylines; bulletin log continued after hand-over'],
    ['R15 Safe pumping tests', 'The utility approves fewer tests, or chloride nears the test limit', 'Smaller and shorter tests; the window from routine records only, with fewer certified years'],
]

AFTER = [
    '**Security.** The results protect three of NATO\'s seven baseline requirements for civil preparedness: water, energy and civil transport (Security Relevance).',
    '**Impact.** Who benefits, indicators with baselines and targets three years after the project, and the value of a warning to each user (Impact).',
    '**Sustainability.** The operators own the network and the software and share a running cost of about €{cost:,.0f} per year (Sustainability).',
    '**Dissemination.** Open methods, software and aggregated data; asset-level results restricted to the operators and authorities (Dissemination Plan, Data Management Plan).',
]

NEW = [
    '**Every result has a user and a test.** Each of the 15 results names who uses it, the objective it proves, and the measure that shows it was reached.',
    '**Results that check themselves.** The live bulletin log (R9) is both a result and the evidence that the certified miss rates (R3) and the value to each user (R14) hold.',
    '**A guaranteed minimum.** Each result that depends on an evidence gate or a field condition has a stated minimum version, so a failed test still leaves the users with something they can use.',
    '**A result in the users\' own terms.** R14 states what each warning is at least worth for each operator\'s own decision, not only how accurate it is.',
]


def fig_users(path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    codes = [c for c, *_ in TABLE]
    group_of = {code: g[0] for g, items in GROUPS for code, *_ in items}
    n = len(codes)
    fig, ax = plt.subplots(figsize=(6.7, 5.3), dpi=300)
    for i, c in enumerate(codes):
        y = n - 1 - i
        col = TYPE_COL[group_of[c]]
        if i % 2 == 0:
            ax.axhspan(y - 0.5, y + 0.5, color='#F4F6F8', zorder=0)
        for j, v in enumerate(USE[c]):
            if v == 2:
                ax.plot(j, y, 'o', ms=10, color=col, zorder=3)
            elif v == 1:
                ax.plot(j, y, 'o', ms=9, mfc='white', mec=col, mew=1.6, zorder=3)
    ax.set_yticks(range(n)); ax.set_yticklabels([f'{c}  {SHORT[c]}' for c in reversed(codes)], fontsize=8.8)
    for t, c in zip(ax.get_yticklabels(), reversed(codes)):
        t.set_color(TYPE_COL[group_of[c]])
    ax.set_xticks(range(len(USERS))); ax.set_xticklabels(USERS, fontsize=8.8)
    ax.xaxis.tick_top()
    ax.set_xlim(-0.5, len(USERS) - 0.5); ax.set_ylim(-0.6, n - 0.4)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    h = [plt.Line2D([], [], marker='o', ls='', ms=9, color='#52606D', label='main user'),
         plt.Line2D([], [], marker='o', ls='', ms=9, mfc='white', mec='#52606D', mew=1.6, label='also uses')]
    names = {'1': 'scientific', '2': 'technological', '3': 'operational', '4': 'capacity and policy'}
    h += [plt.Line2D([], [], marker='s', ls='', ms=8, color=TYPE_COL[k], label=v) for k, v in names.items()]
    ax.legend(handles=h, loc='upper center', bbox_to_anchor=(0.38, -0.01), ncol=3, frameon=False, fontsize=8.8)
    fig.tight_layout(); fig.savefig(path, dpi=300); plt.close(fig)


def main(out):
    import tempfile
    from docx.oxml import OxmlElement
    from build_sota import shade
    import build_sustainability as BS
    cost = sum(float(c[1].replace(' ', '')) for c in BS.COSTS)
    work = tempfile.mkdtemp(); f1 = os.path.join(work, 'fig_users.png'); fig_users(f1)
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.7)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Expected Results', bold=True, size=18, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and energy landfall of a subsiding Adriatic coast', bold=True, size=12, color='1F3864')
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, LEAD, size=10.5)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, f'The project delivers **{len(TABLE)} results** of four kinds: scientific, technological, operational and capacity '
            'and policy. Each names who uses it, the objective it proves and the measure of success (Section 5).', size=10.5)
    for gtitle, items in GROUPS:
        heading(doc, gtitle, 13, before=6)
        for code, title, text in items:
            p = para(doc, 1); p.paragraph_format.keep_with_next = True
            run(p, f'{code}. ', bold=True, color=TYPE_COL[gtitle[0]].lstrip('#').upper(), size=10.5); run(p, title, bold=True, size=10.5)
            p = para(doc, 4, 0.5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, text.replace('α_k', 'αₖ'), size=10)

    h = heading(doc, '5. Results at a glance', 13.5, before=10); h.paragraph_format.keep_with_next = True
    rows = [[c, n, OBJ_OF[c], w, m, u] for c, n, w, m, u in TABLE]
    t = table(doc, ['', 'Result', 'Proves', 'Where and when', 'Measure of success', 'Main users'], rows,
              [1.1, 3.6, 1.55, 2.5, 4.75, 3.5], size=8.8)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    group_of = {code: g[0] for g, items in GROUPS for code, *_ in items}
    tint = {'1': 'E8EDF5', '2': 'EFEAF8', '3': 'FBF0DF', '4': 'E3F4F5'}
    for i, (c, *_r) in enumerate(TABLE, start=1):
        shade(t.rows[i].cells[0], tint[group_of[c]])

    heading(doc, '6. Who uses which result', 13.5, before=10)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(f1, width=Cm(15.5))
    p = para(doc, 4)
    run(p, 'Figure 1. Results and their users. Filled: main user; open: also uses. Every operator and civil protection receive '
           'operational results, not only reports.', italic=True, size=9.5, color='52606D')

    heading(doc, '7. The minimum each key result still delivers', 13.5, before=8)
    p = para(doc, 4); p.paragraph_format.keep_with_next = True
    rich(p, 'Where a result depends on an evidence gate or a field condition, a minimum version is stated in advance (Risk '
            'Assessment and Milestones).', size=10.5)
    t = table(doc, ['Result', 'If this happens', 'The users still receive'], MINIMUM, [3.6, 5.0, 8.4], size=9)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    for r_ in t.rows[1:]:
        shade(r_.cells[0], 'EEF2F8')
        for c in r_.cells:
            for pp in c.paragraphs:
                pp.paragraph_format.keep_with_next = True

    heading(doc, '8. Impact over time', 13.5, before=10)
    table(doc, ['Horizon', 'Expected impact'], IMPACT, [4.0, 13.0], size=9.5)

    heading(doc, '9. Where the results go next', 13.5, before=10)
    for x in AFTER:
        q = para(doc, 3, 0.5); run(q, '• ', bold=True); rich(q, x.format(cost=cost), size=10.5)
    heading(doc, '10. What is new in these results', 13.5, before=8)
    for x in NEW:
        q = para(doc, 3, 0.5); run(q, '• ', bold=True); rich(q, x, size=10.5)
    doc.save(out)
    print('saved', out, '| results', len(TABLE))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Expected_Results.docx')
