"""CERTAIN-COAST (NATO SPS proposal): Dissemination plan. Aims, audiences (needs, products, channels), two-tier
dissemination (open methods, restricted asset-level results) with a release gate, products and events with months and
tasks, a 36-month timeline figure, indicators, acknowledgement, licences and ownership, and what is new. Consistent with
the Work Plan (WP6: T6.1-T6.4; D6.1 Month 33, D6.2 Month 36), the Expected Results (at least six open-access papers)
and the Risk Assessment (R20: security of information).

usage: python build_dissemination.py OUT.docx"""
import os
import sys
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, heading, rich, table, shade  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')

LEAD = ('CERTAIN-COAST produces two kinds of results: methods that any coast can reuse, and warnings about specific critical '
        'infrastructure. The dissemination plan treats them differently. Methods, software, verification statistics and '
        'policy conclusions are made as open and as widely used as possible; asset-level vulnerability results go only to the '
        'operators and authorities who must act on them. Every output passes a release gate before it leaves the project. The '
        'plan reaches seven audiences with products timed to the project\'s decisions, and is measured by indicators reported '
        'to the SPS Programme. It is delivered through WP6 (T6.1–T6.4), with D6.1 (open software and data, Month 33) and D6.2 '
        '(operating procedures and policy brief, Month 36).')

AIMS = [
    '**Use.** The operators of the wellfields, the port and the energy landfall run the system and adopt procedures for it, and civil protection uses its bulletins after events.',
    '**Policy.** National authorities receive evidence on coastal subsidence, relative sea level and critical-infrastructure protection in a form they can use for planning.',
    '**Science.** The coupled model, the certified alarms and the network design are published openly and can be tested and reused by others.',
    '**Transfer.** Other subsiding coasts with wellfields, ports and energy landfalls, in the Adriatic and beyond, can repeat the analysis with the open software and training material.',
    '**Protection.** Nothing released helps an adversary find where critical infrastructure is most vulnerable.',
]

AUDIENCES = [
    ['Water utility, port authority, energy landfall operator', 'Warnings they can act on, with known reliability', 'Bulletins with certified miss rates; joint pumping rule; operating procedures; training (restricted tier)', 'Bulletin interface; workshops; on-site training'],
    ['Civil protection and national authorities', 'One consistent picture after events; numbers for planning', 'Post-event reports; relative sea level at each asset; policy brief', 'Briefings; workshops; policy brief'],
    ['NATO SPS Programme, Allies and partners', 'Evidence of security value and a capability others can adopt', 'Progress and final reports; project summary for SPS communication; transfer workshop', 'Reports; final event; SPS channels'],
    ['Scientific community', 'Methods, data and code to test and reuse', 'Open-access papers; open software; synthetic test coast; verification statistics', 'Journals; conferences; open repository'],
    ['Operators and agencies of other coasts', 'A way to repeat the analysis on their coast', 'Coast kit: software, test case and training material', 'Transfer workshop; webinars'],
    ['Students and early-career researchers', 'Skills across geoscience, data science and security', 'Training school; supervised work; co-authorship', 'School; exchanges'],
    ['Public and media in Durrës and Albania', 'Clear information on coastal risks and what is being done', 'Plain-language summaries in Albanian and English; news at key moments (screened)', 'Website; local media; public event'],
]

TIERS = [
    ['Methods and software', 'All algorithms, code, documentation and a synthetic test coast', '—'],
    ['Coastal motion', 'Regional land-motion maps; the relative-sea-level method', 'Values at named asset points'],
    ['Model and hazards', 'Model structure, calibration method, results aggregated or anonymised', 'Asset-level intrusion, liquefaction and flooding maps'],
    ['Alarms', 'Verification statistics: observed miss and false-alarm rates with intervals', 'Thresholds, bulletin contents, sensor locations inside sites'],
    ['Procedures and policy', 'Generic procedure template; public version of the policy brief', 'Operator-specific procedures; annex with asset details'],
]

GATE = [
    '**Classify.** The author classifies each output as open or restricted using the data plan (T7.2).',
    '**Review.** Operators review any manuscript or dataset that uses their data within an agreed period (indicatively 30 days); the review may remove sensitive content but cannot block the publication of methods.',
    '**Adapt.** Sensitive content is aggregated, anonymised ("a port", "an energy landfall") or moved to the restricted annex.',
    '**Sign off.** The coordinator records the decision in the release log.',
]

PRODUCTS = [
    ['Website and visual identity', 'Public summary, news and non-sensitive results in English and Albanian', 'All; public', '3, updated', 'WP6'],
    ['Kick-off stakeholder workshop', 'Needs, thresholds, data access and the acceptable false-alarm rate', 'Operators; civil protection', '2', 'T3.1, T7.2'],
    ['Open-access papers (at least six)', 'Coastal motion; coupled model; certified surrogate; certified alarms; network design and seismic velocity; verification in operation', 'Science', '15–36', 'WP1–WP5'],
    ['Conference presentations', 'For example EGU General Assembly, AGU Fall Meeting, Salt Water Intrusion Meeting, SIAM Conference on Uncertainty Quantification', 'Science', 'Each year', 'WP6'],
    ['Training school', 'Hands-on work with the coast kit', 'Early-career researchers; students', '14', 'T6.1'],
    ['Mid-term workshop', 'Model and network results; dry run of the bulletins', 'Operators; civil protection', '18', 'WP2, WP4'],
    ['Live bulletins', 'Twelve months of certified warnings, logged with outcomes', 'Operators; civil protection', '23–34', 'T5.2'],
    ['Operator training', 'Running the system; what a miss rate means', 'Operator and civil-protection staff', '24–36', 'T6.2'],
    ['Open software and data (D6.1)', 'Code, documentation, synthetic test coast, open data, verification statistics', 'Science; other coasts', '33', 'T6.3'],
    ['Transfer workshop', 'Coast kit for other Adriatic and Mediterranean coasts', 'Other coasts; Allies and partners', '35', 'T6.3'],
    ['Policy brief and procedures (D6.2)', 'Subsidence, water supply, critical-infrastructure protection; operator procedures', 'National authorities; operators', '36', 'T6.4'],
    ['Final workshop and live demonstration', 'The system in operation; results; hand-over', 'All', '36', 'WP5, WP6'],
    ['Press releases', 'Kick-off, network installed, start of live bulletins, final event', 'Public; media', '2, 12, 23, 36', 'WP6'],
    ['Reports to NATO SPS', 'Progress and final reports with the risk register and indicators', 'NATO SPS', '12, 24, 36', 'T7.1'],
]

KPIS = [
    ['Open-access peer-reviewed papers', 'At least 6', 'Publication list with open links'],
    ['Conference presentations', 'At least 8', 'Presentation list'],
    ['Open software and data release with documentation', '1 release with a persistent identifier (D6.1)', 'Repository'],
    ['Groups testing the software on another coast', 'At least 2', 'Transfer workshop; repository records'],
    ['Operator and civil-protection staff trained', 'At least 20', 'Training records'],
    ['Early-career researchers trained', 'At least 6', 'Training records'],
    ['Operating procedures adopted', 'At least 1 per asset', 'D6.2'],
    ['Stakeholder workshops', '3, plus 1 transfer workshop', 'Agendas and participant lists'],
    ['Policy brief delivered to national authorities', 'Delivered (D6.2)', 'Delivery record'],
    ['Outputs screened before release', '100%; no sensitive disclosure', 'Release log'],
]

RULES = [
    '**Acknowledgement.** Every output acknowledges the support of the NATO Science for Peace and Security Programme, as the grant requires.',
    '**Licences.** Software under an OSI-approved open-source licence (for example Apache-2.0); open data under CC BY 4.0; papers open access.',
    '**Ownership.** Operator data remain the property of the operators and are used under the access agreements of T7.2.',
    '**Publication rules.** The consortium agreement sets the review period and limits review to sensitive content and confidential data.',
    '**Languages.** Public and operator materials in Albanian and English; scientific outputs in English.',
]

NEW = [
    '**Open verification of a restricted service.** The observed miss and false-alarm rates of the live warnings are published with their confidence intervals, so anyone can check the certified guarantee without seeing a single vulnerable location.',
    '**Security-screened open science.** A two-tier plan and a release gate make the methods fully open and keep asset-level vulnerability closed, so openness and protection of critical infrastructure do not conflict.',
    '**Uncertainty as a number each audience can act on.** Operators receive a miss rate with every bulletin; planners receive relative sea level at each asset instead of a regional trend; the public receives plain-language summaries.',
    '**A coast kit, not only papers.** Software, a synthetic test coast and training material let another coast repeat the analysis without the project team.',
    '**Products timed to decisions.** Workshops, training and live bulletins follow the project\'s decision points: thresholds before design, a dry run before operation, procedures before hand-over.',
]

# ---------------------------------------------------------------------------------------------------- timeline figure
LANES = [
    ('Operators and\ncivil protection', '#c27c12',
     [(2, 'Kick-off workshop'), (6, 'Network design'), (18, 'Mid-term workshop'), (27, 'Back-testing report'), (36, 'Hand-over')],
     [(23, 34, 'Live bulletins'), (24, 36, 'Operator training')]),
    ('Science and\ntraining', '#6a4fb3',
     [(8, 'Conference'), (14, 'Training school'), (20, 'Conference'), (32, 'Conference')],
     [(15, 36, 'Open-access papers (at least six)')]),
    ('Policy and\nNATO SPS', '#1F3864',
     [(12, 'SPS report'), (24, 'SPS report'), (30, 'Briefing to authorities'), (36, 'Policy brief')],
     []),
    ('Public', '#0e7490',
     [(2, 'Press: kick-off'), (12, 'Press: network'), (23, 'Press: live start'), (36, 'Final event')],
     [(3, 36, 'Website and news in Albanian and English')]),
    ('Transfer and\nopen release', '#1e8a5a',
     [(12, 'Open regional land motion'), (33, 'Software + data (D6.1)'), (35, 'Transfer workshop')],
     []),
]


def fig_timeline(path):
    W, H = 6.7, 5.6
    fig = plt.figure(figsize=(W, H), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    x0, x1 = 1.45, 6.45
    X = lambda m: x0 + m * (x1 - x0) / 36.0
    lane_h, top = 0.98, H - 0.10
    cw = 0.067                                    # approximate width per character at 8.8 pt (inches)
    for i, (name, col, points, bars) in enumerate(LANES):
        yt = top - i * lane_h; yb = yt - lane_h + 0.06
        ax.add_patch(FancyBboxPatch((0.05, yb), x1 + 0.2, yt - yb - 0.02, boxstyle='round,pad=0,rounding_size=0.06',
                                    fc=col + '12', ec='none'))
        ax.text(0.14, (yt + yb) / 2, name, fontsize=9.8, fontweight='bold', color=col, va='center', ha='left', linespacing=1.15)
        yline = yb + 0.42 if bars else yb + 0.30
        ax.plot([x0, x1], [yline, yline], color='#c9ced6', lw=1.0, zorder=1)
        # bars under the line
        for j, (a, b, lab) in enumerate(bars):
            yy = yline - 0.16 - j * 0.20
            ax.add_patch(FancyBboxPatch((X(a), yy - 0.075), X(b) - X(a), 0.15, boxstyle='round,pad=0,rounding_size=0.04',
                                        fc=col, ec='none', alpha=0.85))
            txt_w = len(lab) * cw * 0.95
            if txt_w < X(b) - X(a) - 0.08:
                ax.text(X(a) + 0.06, yy, lab, fontsize=8.4, color='white', va='center', ha='left', fontweight='bold')
            else:
                ax.text(X(a) - 0.05, yy, lab, fontsize=8.4, color=col, va='center', ha='right', fontweight='bold')
        # point labels: above the line; if that collides, below the line (when no bar is there); else a second row
        # above, with a leader line that must not cross a first-row label
        placed = []                                   # (centre, width, slot)
        bar_spans = [(X(a), X(b)) for a, b, _ in bars]

        def free(cx, w, slot):
            return all(not (ps == slot and abs(pcx - cx) < (pw + w) / 2 + 0.05) for pcx, pw, ps in placed)

        for m, lab in points:
            ax.plot([X(m)], [yline], marker='D', ms=6.5, color=col, mec='white', mew=1.0, zorder=3)
            w = len(lab) * cw
            cx = min(max(X(m), x0 + w / 2 - 0.05), x1 + 0.15 - w / 2)
            below_ok = free(cx, w, 'b') and all(cx + w / 2 < a or cx - w / 2 > b for a, b in bar_spans)
            line_ok = all(not (ps == 'a0' and abs(pcx - X(m)) < pw / 2 + 0.04) for pcx, pw, ps in placed)
            if free(cx, w, 'a0'):
                slot = 'a0'
            elif below_ok:
                slot = 'b'
            elif line_ok:
                slot = 'a1'
            else:
                slot = 'a1'
            placed.append((cx, w, slot))
            if slot == 'a0':
                ly = yline + 0.16
            elif slot == 'b':
                ly = yline - 0.17
            else:
                ly = yline + 0.38
                ax.plot([X(m), X(m)], [yline + 0.06, ly - 0.07], color=col, lw=0.8)
            ax.text(cx, ly, lab, fontsize=8.8, color='#1f2328', va='center', ha='center')
    # month axis
    ya = top - len(LANES) * lane_h + 0.02
    for m in range(0, 37, 6):
        ax.plot([X(m), X(m)], [ya, top - 0.02], color='#e3e6ea', lw=0.8, zorder=0)
        ax.text(X(m), ya - 0.10, f'M{m}' if m else 'M0', fontsize=9, ha='center', va='top', color='#52606D')
    ax.text((x0 + x1) / 2, ya - 0.34, 'Project month', fontsize=9.5, ha='center', va='top', color='#1f2328', fontweight='bold')
    fig.savefig(path, dpi=300)
    plt.close(fig)


def tidy(t):
    """Repeat the header row on a new page and never leave the last row alone on a page."""
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    for row in (t.rows[0], t.rows[-2]):
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.keep_with_next = True
    return t


def bullets(doc, items):
    for t in items:
        p = para(doc, 3, 0.5); run(p, '• ', bold=True); rich(p, t)


def main(out):
    work = tempfile.mkdtemp(); fig = os.path.join(work, 'fig_dissemination_timeline.png'); fig_timeline(fig)
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Dissemination Plan', bold=True, size=18, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, LEAD, size=11.5)

    heading(doc, '1. Aims', 13.5, before=4)
    bullets(doc, AIMS)

    heading(doc, '2. Audiences and what each receives', 13.5, before=8)
    tidy(table(doc, ['Audience', 'What they need', 'What CERTAIN-COAST gives them', 'Main channels'], AUDIENCES,
               [3.6, 3.8, 5.8, 3.8], size=9.5))
    para(doc, 4)

    h = heading(doc, '3. Two tiers: open methods, restricted vulnerability', 13.5, before=0)
    h.paragraph_format.page_break_before = True
    p = para(doc, 5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'A map of where a port would liquefy or where an energy landfall would flood is valuable to its operator and to an '
            'adversary. CERTAIN-COAST therefore separates what is published from what is shared only with those who must act '
            '(Risk Assessment, R20):')
    t = tidy(table(doc, ['Result', 'Open (public)', 'Restricted (operators and authorities)'], TIERS, [3.4, 7.2, 6.4], size=9.5))
    for i in range(1, len(TIERS) + 1):
        shade(t.rows[i].cells[1], 'E6F4EC'); shade(t.rows[i].cells[2], 'FBEAEA')
    para(doc, 4)
    p = para(doc, 3); run(p, 'Release gate for every output', bold=True, size=11, color='1F3864')
    bullets(doc, GATE)

    heading(doc, '4. Products and events', 13.5, before=8)
    tidy(table(doc, ['Product or event', 'Content', 'Audience', 'Month', 'Task'], PRODUCTS, [3.7, 6.3, 3.3, 1.9, 1.8], size=9.5))
    para(doc, 4)

    heading(doc, '5. Timeline', 13.5, before=8)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(fig, width=Cm(17.0))
    p = para(doc, 6)
    run(p, 'Figure 1. Dissemination over the 36 months by audience. Diamonds: events and deliverables; bars: continuous '
           'activities. Conference months are indicative and depend on the start date.', italic=True, size=10, color='52606D')

    heading(doc, '6. Indicators', 13.5, before=8)
    p = para(doc, 4); rich(p, 'Targets are indicative and are reported in each progress report to the SPS Programme.')
    tidy(table(doc, ['Indicator', 'Target', 'Evidence'], KPIS, [7.4, 5.0, 4.6], size=10))
    para(doc, 4)

    heading(doc, '7. Acknowledgement, licences and ownership', 13.5, before=8)
    bullets(doc, RULES)

    heading(doc, '8. What is new in this dissemination plan', 13.5, before=8)
    bullets(doc, NEW)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Dissemination_Plan.docx')
