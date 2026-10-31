"""CERTAIN-COAST (NATO SPS proposal): Timeline. From application to start; a one-page master timeline (work packages,
deliverables, milestones, evidence gates, live-operation band, governance and key events); milestone and deliverable
tables; key dates month by month; the project year by year; critical path, gates and buffers; governance and
reporting calendar; what is new. All work-package spans, deliverables and milestones are read from build_workplan.py,
and events from the Dissemination, Risk, Sustainability, Data Management and Gender documents.

usage: python build_timeline.py OUT.docx"""
import os
import sys
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, heading, rich, table, shade  # noqa: E402
import build_workplan as W  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')
SHORTWP = {'WP1': 'Coastal motion', 'WP2': 'Coupled model + surrogate', 'WP3': 'Certified alarms', 'WP4': 'Monitoring network',
           'WP5': 'Live demonstration', 'WP6': 'Training, transfer, dissem.', 'WP7': 'Management, data, risk'}
GATES = {'MS3', 'MS4', 'MS5'}
EVENTS = [(2, 'Kick-off workshop'), (14, 'Training school'), (18, 'Mid-term workshop'), (35, 'Transfer workshop'), (36, 'Final workshop')]

LEAD = ('CERTAIN-COAST runs for 36 months. Year 1 measures the coast and builds the network, Year 2 builds the model, '
        'certifies the alarms and opens the live service, and Year 3 operates it for twelve months and hands it over. The '
        'timeline is driven by evidence rather than dates alone: three gates (MS3, MS4, MS5) must be passed before the next '
        'stage starts, and buffers sit where the Risk Assessment places the risks. Months count from the start date of '
        'the grant; all dates below are consistent with the Work Plan.')

BEFORE = [
    ['Now', 'Name the partner-country institution; collect the signed commitment letters; finalise budget and CVs', 'Applicants'],
    ['[15 November 2026: confirm on nato.int]', 'Submit the application for the SPS call 2027-1 (in the phase the call specifies)', 'NATO-country Project Director'],
    ['[per the call]', 'Evaluation by the Independent Scientific Evaluation Group; funding decision by the NATO Allies', 'NATO'],
    ['[after approval]', 'Grant letter; acceptance of the award by the co-directors', 'All co-directors'],
    ['Before Month 1', 'Draft consortium agreement and access agreements; plan ethics approvals; update equipment quotes', 'Consortium'],
    ['Month 1', 'Project start', 'Consortium'],
]

YEARS = [
    ('Year 1 (Months 1–12): measure and build', [
        'Access agreements and data management plan by Month 3 (D7.1); kick-off workshop with the operators in Month 2.',
        'Network designed for the warnings by Month 6 (D4.1, MS1); equipment ordered in Month 4; installed and streaming by Month 12 (D4.2).',
        'InSAR from 2014 onward, GNSS and corner reflectors; elastic and inelastic compaction separated; relative sea level at each asset by Month 12 (D1.1, MS2).',
        'Coupled model set up from Month 4; post-event protocol on standby from Month 12.',
    ]),
    ('Year 2 (Months 13–24): model, certify, open the service', [
        'Thresholds and acceptable false-alarm rates agreed with the operators (Months 13–15); training school in Month 14.',
        'Coupled model calibrated by Month 18 (D2.1, gate MS3); mid-term workshop in Month 18.',
        'Certified surrogate by Month 22 (D2.2); go/no-go for live operation in Month 22 (gate MS4); live bulletins from Month 23.',
        'Certified alarm algorithms and proofs by Month 24 (D3.1); first progress report in Month 12, second in Month 24.',
    ]),
    ('Year 3 (Months 25–36): operate, verify, hand over', [
        'Back-testing report and miss-rate targets confirmed by Month 27 (D3.2, gate MS5); joint pumping rule agreed with the utility by Month 33.',
        'Maintenance agreement signed by the operators by Month 33; open software and data released in Month 33 (D6.1).',
        'Twelve months of live operation completed in Month 34 (D5.1, MS6); operators issue every bulletin in Months 34–36.',
        'Transfer workshop in Month 35; procedures and policy brief, final workshop and hand-over in Month 36 (D6.2, MS7, D7.3).',
    ]),
]

CRITICAL = [
    ['Network design (T4.1)', 'M1–6', 'MS1', 'Equipment ordered in Month 4, before the design is final, for sensors certain to be needed'],
    ['Procurement and installation (T4.2)', 'M4–12', 'MS2', 'Installation window of 8 months; highest-value sensors installed first'],
    ['Calibration of the coupled model (T2.3)', 'M12–18', 'MS3 (gate)', 'Model built in stages from Month 7, so calibration starts as soon as data stream'],
    ['Certified surrogate (T2.4)', 'M15–22', 'MS4 (gate)', 'Starts before calibration ends, on preliminary parameters'],
    ['Live operation (T5.2)', 'M23–34', 'MS6', 'Back-testing (to Month 27) runs in parallel, not before'],
    ['Hand-over (T6.4)', 'M30–36', 'MS7', 'Operators issue all bulletins from Month 34; procedures drafted from Month 30'],
]
SLIP = ('A slip of up to two months at the go/no-go gate (MS4) is absorbed: live operation then runs from Month 25 to Month 36, '
        'still twelve months, and the operators still issue the bulletins in the final months. A longer slip triggers the '
        'fallbacks of the Risk Assessment (R5, R6) and is decided by the steering committee.')

GOVERN = [
    ['Steering committee', 'Months 2 (kick-off), 6, 12, 18, 24, 30, 36, and at each gate', 'Partnership; T7.1'],
    ['Risk review', 'Every month; escalation within two weeks when a trigger is crossed', 'Risk Assessment; T7.3'],
    ['Progress reports to NATO SPS', 'Months 12 and 24 (D7.2); final report Month 36 (D7.3)', 'Work Plan'],
    ['Data management plan', 'Version 1 Month 3 (D7.1); version 2 Month 18; final Month 36', 'Data Management Plan'],
    ['Gender and ethics review', 'Yearly: Months 12, 24, 36; ethics at every steering committee', 'Gender Balance; Ethics'],
    ['Maintenance and hand-over agreements', 'Month 33 and Month 36', 'Sustainability'],
]

NEW = [
    '**Gates, not only dates.** Live operation starts only when the model passes its validation test (MS3) and the surrogate meets its error bound (MS4), and the guarantees are confirmed in back-testing (MS5); each gate has a stated pass test and a fallback.',
    '**A full year of hazards.** Twelve consecutive months of live operation include every season, the dry months that drive intrusion and the storm months that drive extreme sea levels, whatever the start date.',
    '**Ready for the unexpected event.** The post-event protocol is on standby from Month 12, so a strong earthquake or storm at any time after the network is installed becomes data rather than a disruption.',
    '**Buffers where the risks are.** Slack is placed on procurement, calibration and the go/no-go gate, the steps the Risk Assessment scores highest, not spread evenly.',
    '**The hand-over is in the timeline, not after it.** Operators issue every bulletin in the last three months, so the end state is demonstrated within the project.',
]


def x_of(m, x0, x1):
    return x0 + (m - 0.5) * (x1 - x0) / 36.0


def fig_master(path):
    Wd, Ht = 10.4, 7.0
    fig = plt.figure(figsize=(Wd, Ht), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, Wd); ax.set_ylim(0, Ht); ax.axis('off')
    x0, x1 = 2.35, 10.25
    X = lambda m: x_of(m, x0, x1)
    mw = (x1 - x0) / 36.0
    top = Ht - 0.12
    # year bands and month axis
    for y in range(3):
        xa, xb = x0 + y * 12 * mw, x0 + (y + 1) * 12 * mw
        ax.add_patch(Rectangle((xa, 0.10), xb - xa, top - 0.10 - 0.02, fc='#f3f5f8' if y % 2 == 0 else 'white', ec='none', zorder=0))
        ax.text((xa + xb) / 2, top - 0.12, f'Year {y + 1}', fontsize=11, fontweight='bold', ha='center', va='center', color='#1F3864')
    for m in (1, 6, 12, 18, 24, 30, 36):
        ax.text(X(m), top - 0.42, f'M{m}', fontsize=9, ha='center', va='center', color='#52606D')
    # live-operation band
    yb_top = top - 0.62
    ax.add_patch(Rectangle((X(23) - mw / 2, 0.10), 12 * mw, yb_top - 0.10, fc='#c27c12', alpha=0.10, ec='none', zorder=0))
    # milestones row
    ym = yb_top - 0.25
    ax.text(0.10, ym, 'Milestones', fontsize=10.5, fontweight='bold', va='center', color='#1f2328')
    for code, m, name, _ in W.MILESTONES:
        gate = code in GATES
        ax.plot([X(m)], [ym], marker='D', ms=10 if gate else 8, color='#D97706' if gate else '#1F3864', mec='white', mew=1.2, zorder=4)
        ax.text(X(m), ym + 0.24, code + (' gate' if gate else ''), fontsize=8.8, ha='center', va='center', fontweight='bold',
                color='#92400E' if gate else '#1F3864')
    # work packages
    row_h = 0.58
    y = ym - 0.50
    for wp, title, obj, span, _, tasks, dels in W.WPS:
        col = W.COL[wp]
        ax.text(0.10, y, wp, fontsize=10.5, fontweight='bold', color=col, va='center')
        ax.text(0.62, y, SHORTWP[wp], fontsize=9.4, color='#1f2328', va='center')
        a, b = span
        ax.add_patch(FancyBboxPatch((X(a) - mw / 2, y - 0.13), (b - a + 1) * mw, 0.26, boxstyle='round,pad=0,rounding_size=0.05',
                                    fc=col, ec='none', alpha=0.88, zorder=2))
        seen = set()
        for code, name, m in dels:
            if (code, m) in seen:
                continue
            seen.add((code, m))
            ax.plot([X(m)], [y], marker='o', ms=7, color='white', mec='#1f2328', mew=1.2, zorder=3)
            ax.text(X(m), y + 0.27, code, fontsize=8.6, ha='center', va='center', color='#1f2328')
        if wp == 'WP2':
            ax.text(X(30.5), y, 'Live operation: 12 months (M23–M34)', fontsize=9.8, fontweight='bold', color='#9a610c',
                    ha='center', va='center')
        y -= row_h
    # governance row
    ax.text(0.10, y, 'Governance', fontsize=10.5, fontweight='bold', va='center', color='#1f2328')
    for m in (2, 6, 12, 18, 24, 30, 36):
        ax.plot([X(m)], [y], marker='s', ms=6.5, color='#52606D', zorder=3)
    ax.text(0.10, y - 0.22, '(steering committee)', fontsize=8.6, va='center', color='#52606D')
    y -= 0.80
    # events row
    ax.text(0.10, y, 'Key events', fontsize=10.5, fontweight='bold', va='center', color='#1f2328')
    for i, (m, lab) in enumerate(EVENTS):
        ax.plot([X(m)], [y], marker='^', ms=8, color='#0e7490', zorder=3)
        dy = 0.22 if i % 2 == 0 else 0.42
        ha = 'left' if m < 4 else ('right' if m > 33 else 'center')
        ax.text(X(m) + (0.05 if ha == 'left' else -0.05 if ha == 'right' else 0), y + dy, lab, fontsize=8.6, ha=ha, va='center', color='#0e7490')
    fig.savefig(path, dpi=300)
    plt.close(fig)


def tidy(t):
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    keep = t.rows[:-1] if len(t.rows) <= 7 else (t.rows[0], t.rows[1], t.rows[-2])
    for row in keep:
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.keep_with_next = True
    return t


def bullets(doc, items, size=11):
    for t in items:
        p = para(doc, 3, 0.5); run(p, '• ', bold=True, size=size); rich(p, t, size=size)


def key_dates():
    ev = []
    for code, m, name, _ in W.MILESTONES:
        ev.append((m, 0, code, name, 'Gate' if code in GATES else 'Milestone'))
    for wp, title, obj, span, _, tasks, dels in W.WPS:
        seen = set()
        for code, name, m in dels:
            if (code, m) not in seen:
                seen.add((code, m)); ev.append((m, 1, code, name, 'Deliverable'))
    for m, lab in EVENTS:
        ev.append((m, 2, '', lab, 'Event'))
    extra = [(4, 'Equipment ordered (T4.2)'), (12, 'Post-event protocol on standby (T5.4)'), (13, 'Thresholds agreed with operators begin (T3.1)'),
             (23, 'Live bulletins start (T5.2)'), (33, 'Maintenance agreement signed; joint pumping rule agreed (T5.3)'),
             (34, 'Operators issue every bulletin (to Month 36)')]
    for m, lab in extra:
        ev.append((m, 2, '', lab, 'Event'))
    ev.sort(key=lambda e: (e[0], e[1]))
    return [[f'M{m}', (code + ': ' if code else '') + name, kind] for m, _, code, name, kind in ev]


def main(out):
    work = tempfile.mkdtemp(); fig = os.path.join(work, 'fig_master_timeline.png'); fig_master(fig)
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Timeline', bold=True, size=18, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, LEAD, size=11)

    heading(doc, '1. From application to start', 13.5, before=2)
    tidy(table(doc, ['When', 'What', 'Who'], BEFORE, [4.4, 9.2, 3.4], size=9.5))
    p = para(doc, 4, before=2)
    run(p, 'Dates in brackets depend on the call and on NATO\'s evaluation; confirm them on nato.int.', italic=True, size=9.5, color='52606D')

    heading(doc, '2. The project year by year', 13.5, before=6)
    for title, items in YEARS:
        p = para(doc, 2, before=3); run(p, title, bold=True, size=11, color='2E6DB4'); p.paragraph_format.keep_with_next = True
        bullets(doc, items, size=10)

    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    sec.orientation = WD_ORIENT.LANDSCAPE; sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
    sec.left_margin = sec.right_margin = Cm(1.5); sec.top_margin = sec.bottom_margin = Cm(1.3)
    p = para(doc, 2); run(p, '3. Master timeline', bold=True, size=13.5, color='1F3864')
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(fig, width=Cm(24.2))
    p = para(doc, 2)
    run(p, 'Figure 1. Master timeline. Bars: work packages; circles: deliverables; diamonds: milestones, with the three evidence '
           'gates in orange; shaded band: twelve months of live operation; squares: steering committee; triangles: key events.',
        italic=True, size=9.5, color='52606D')

    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    sec.orientation = WD_ORIENT.PORTRAIT; sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(2.0); sec.top_margin = sec.bottom_margin = Cm(1.8)
    heading(doc, '4. Milestones and gates', 13.5, before=0)
    rows = [[c, f'M{m}', n, ev] for c, m, n, ev in W.MILESTONES]
    t = tidy(table(doc, ['', 'Month', 'Milestone', 'Evidence'], rows, [1.4, 1.6, 5.4, 8.6], size=10))
    for i, (c, m, n, ev) in enumerate(W.MILESTONES, start=1):
        if c in GATES:
            shade(t.rows[i].cells[0], 'FDE7C2')
    para(doc, 4)
    heading(doc, '5. Key dates month by month', 13.5, before=8)
    kd = key_dates()
    t = tidy(table(doc, ['Month', 'What', 'Type'], kd, [1.8, 12.4, 2.8], size=9.5))
    tint = {'Gate': 'FDE7C2', 'Milestone': 'E8EDF5', 'Deliverable': 'EEF2F8', 'Event': 'E3F4F5'}
    for i, r in enumerate(kd, start=1):
        shade(t.rows[i].cells[2], tint[r[2]])
    para(doc, 4)

    h = heading(doc, '6. Critical path, gates and buffers', 13.5, before=0)
    h.paragraph_format.page_break_before = True
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'The chain that decides the end date runs from the network design to the hand-over. Each link has a buffer placed '
            'where the Risk Assessment scores the risk highest:')
    tidy(table(doc, ['Link', 'Months', 'Ends at', 'Buffer'], CRITICAL, [4.6, 1.8, 2.2, 8.4], size=10))
    p = para(doc, 6, before=6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, SLIP)

    heading(doc, '7. Governance and reporting calendar', 13.5, before=8)
    tidy(table(doc, ['Activity', 'When', 'Source'], GOVERN, [4.6, 8.4, 4.0], size=10))
    para(doc, 4)
    heading(doc, '8. What is new in this timeline', 13.5, before=8)
    bullets(doc, NEW)
    doc.save(out)
    print('saved', out, '| key dates', len(kd))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Timeline.docx')
