"""CERTAIN-COAST (NATO SPS proposal): Work plan. Structure and phases with the work-package links figure; seven work
packages (WP1-WP6 = objectives O1-O6, WP7 management) with leads, tasks, months and deliverables; milestones with the
evidence gates; critical path and buffers; the highest risks (from build_risk.py); management and monitoring; what is
new; Gantt chart on two landscape pages. WPS, MILESTONES, COL, SHORT and RISKS are imported by other builders.

usage: python build_workplan.py OUT.docx GANTT.png"""
import os
import re
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.enum.section import WD_ORIENT, WD_SECTION

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_sota import run, para, heading, rich, table  # noqa: E402

SHORT = {'T1.1': 'InSAR time series 2014 onwards', 'T1.2': 'GNSS, corner reflectors, tide-gauge tie',
         'T1.3': 'Elastic vs inelastic compaction; 2019 motion', 'T1.4': 'R(t) with uncertainty at each asset',
         'T2.1': 'Conceptual model and data assembly', 'T2.2': 'Coupled model (flow, salt, compaction, FS, sea level)',
         'T2.3': 'Calibration on all data', 'T2.4': 'Surrogate with a-posteriori error bound',
         'T3.1': 'Indicators and thresholds with the end-user', 'T3.2': 'Certified margin and proofs',
         'T3.3': 'Joint guarantee; α_k by consequence', 'T3.4': 'Back-testing (record and storylines)',
         'T3.5': 'Refinement with live outcomes',
         'T4.1': 'Goal-oriented network design', 'T4.2': 'Procurement and installation',
         'T4.3': 'Operation, QC, streaming, assimilation', 'T4.4': 'Seismic velocity vs water table',
         'T5.1': 'Bulletin protocol and interfaces', 'T5.2': 'Twelve months of live operation',
         'T5.3': 'Safe tests and joint pumping rule', 'T5.4': 'Post-event protocol (on trigger)',
         'T6.1': 'Early-career researchers', 'T6.2': 'Training of the end-user\'s staff and users',
         'T6.3': 'Open software and data', 'T6.4': 'Operating procedures and policy brief',
         'T7.1': 'Coordination and reporting', 'T7.2': 'Data plan and access agreements', 'T7.3': 'Risk and quality management'}

COL = {'WP1': '#2e6db4', 'WP2': '#6a4fb3', 'WP3': '#b03a3a', 'WP4': '#1e8a5a', 'WP5': '#c27c12', 'WP6': '#0e7490', 'WP7': '#52606d'}

WPS = [
    ('WP1', 'Coastal motion and relative sea level', 'O1', (1, 36),
     'Measure the vertical motion of the land at the wellfields, the port and the landfall, separate what pumping can reverse from what it cannot, and deliver the relative sea level R(t) that drives every hazard model.',
     [('T1.1', 'Sentinel-1 InSAR time series (2014 onwards) over the three asset areas', (1, 9)),
      ('T1.2', 'GNSS station(s) and corner reflectors at the assets; tie to the tide gauge', (3, 36)),
      ('T1.3', 'Elastic and inelastic compaction separated; pumping limit without inelastic compaction; 2019 coseismic and postseismic motion', (6, 12)),
      ('T1.4', 'R(t) series with uncertainty at each asset, updated through the demonstration', (10, 36))],
     [('D1.1', 'Coastal motion atlas and R(t) series', 12)]),
    ('WP2', 'One coupled model of the coast and its certified fast copy', 'O2', (4, 24),
     'Build and calibrate one physical model that gives, from the same forcing, the chloride at the wells, the liquefaction factor of safety at the port and the landfall, and the extreme water level at all three; and a fast surrogate with an error bound on every forecast.',
     [('T2.1', 'Conceptual model and data assembly: geology, wells, port and landfall geotechnical data', (4, 9)),
      ('T2.2', 'Coupled model: variable-density flow, salt memory, compaction, FS(x,t) = CRR/CSR(z_w), coastal water level on R(t)', (7, 15)),
      ('T2.3', 'Calibration on heads, conductivity, chloride, InSAR and seismic velocity', (12, 18)),
      ('T2.4', 'Neural or kernel operator surrogate with a-posteriori error bound', (15, 22))],
     [('D2.1', 'Calibrated coupled model', 18), ('D2.2', 'Certified surrogate', 22)]),
    ('WP3', 'Certified multi-hazard alarm', 'O3', (13, 34),
     'Turn the forecasts into alarms whose miss rates are bounded: a margin made of the surrogate error bound, an online conformal risk-control term and an extreme-aware term; a joint guarantee over the three hazards.',
     [('T3.1', 'Hazard indicators and thresholds agreed with the end-user (chloride limit, FS < 1, design water level)', (13, 15)),
      ('T3.2', 'Margin construction and proofs: error bound + online conformal risk control + extreme-aware term', (15, 24)),
      ('T3.3', 'Joint guarantee over the three alarms; tolerances α_k allocated by consequence', (18, 24)),
      ('T3.4', 'Back-testing on the historical record and on storylines beyond it', (22, 27)),
      ('T3.5', 'Alarm refinement with the outcomes of the live operation', (28, 34))],
     [('D3.1', 'Certified alarm algorithms and proofs', 24), ('D3.2', 'Back-testing report', 27)]),
    ('WP4', 'Monitoring network designed for the warnings', 'O4', (1, 36),
     'Choose the sensors jointly for their value to the three warnings, install them, keep them running and feed them into the model.',
     [('T4.1', 'Goal-oriented design across sensor types: piezometers with conductivity, chloride sampling, GNSS, seismic noise, nodes, fibre', (1, 6)),
      ('T4.2', 'Procurement and installation', (4, 12)),
      ('T4.3', 'Operation, quality control, data streaming and assimilation', (12, 36)),
      ('T4.4', 'Seismic velocity calibrated against the water table at the port or landfall', (12, 24))],
     [('D4.1', 'Network design report', 6), ('D4.2', 'Network installed and streaming', 12)]),
    ('WP5', 'Live demonstration at the wellfields, port and landfall', 'O5', (22, 36),
     'Run the system live for twelve months with the end-user, the Ministry of Infrastructure and Energy, evaluate every operating decision against all three hazards, sharpen the certified safe window with safe pumping tests, and execute the post-event protocol whenever it is triggered.',
     [('T5.1', 'Bulletin protocol and decision interfaces with the end-user', (22, 23)),
      ('T5.2', 'Twelve months of live operation, bulletins logged and outcomes verified', (23, 34)),
      ('T5.3', 'Safe pumping tests planned to sharpen the certified window; pumping rule evaluated against the three hazards together and prepared for the authorities that issue water-use permits', (24, 33)),
      ('T5.4', 'Post-event protocol after strong earthquakes or surges (on trigger)', (12, 36))],
     [('D5.1', 'Live demonstration report', 34)]),
    ('WP6', 'Training, transfer and dissemination', 'O6', (1, 36),
     'Build lasting capacity: early-career researchers trained by doing, the end-user\'s staff trained to use the bulletins, open software and data, and procedures the end-user and the authorities can adopt.',
     [('T6.1', 'Early-career researchers: exchanges, schools and supervised work in WP1–WP5', (3, 36)),
      ('T6.2', 'Training of the end-user\'s staff and of the intended users', (24, 36)),
      ('T6.3', 'Open software and data release with documentation', (30, 33)),
      ('T6.4', 'Operating procedures and policy brief', (30, 36))],
     [('D6.1', 'Software and data release', 33), ('D6.2', 'Operating procedures and policy brief', 36)]),
    ('WP7', 'Management, data and risk', 'all', (1, 36),
     'Coordinate the consortium, secure drilling permits and access to wells and data, manage risks and report.',
     [('T7.1', 'Coordination, steering committee, reporting', (1, 36)),
      ('T7.2', 'Data management, drilling permits and access agreements for existing wells', (1, 3)),
      ('T7.3', 'Risk and quality management', (1, 36))],
     [('D7.1', 'Data management plan and access agreements', 3), ('D7.2', 'Progress reports', 6), ('D7.2', 'Progress reports', 18), ('D7.2', 'Progress reports', 30), ('D7.3', 'Final report', 36)]),
]

MILESTONES = [
    ('MS1', 6, 'Network design agreed', 'D4.1 approved by the steering committee'),
    ('MS2', 12, 'Network streaming; coastal motion known', 'D4.2 (≥ 90% data availability over the first month) and D1.1 delivered'),
    ('MS3', 18, 'Coupled model calibrated', 'D2.1: held-out observations reproduced within their stated uncertainty'),
    ('MS4', 22, 'Go/no-go for live operation', 'D2.2 surrogate error bound met on the test set; alarm prototype passes a dry run'),
    ('MS5', 27, 'Miss-rate targets confirmed in back-testing', 'D3.2: each miss rate ≤ α_k with its confidence interval reported'),
    ('MS6', 34, 'Twelve months of live operation completed', 'D5.1 with the bulletin log and verified outcomes'),
    ('MS7', 36, 'Hand-over to the end-user', 'D6.2 procedures adopted; the end-user\'s staff use the bulletins with the project team only in support'),
]

RISKS = [
    ['Drilling permits or access to existing wells and records are delayed', 'Medium', 'High', 'Permits requested in Month 1 and access agreements signed by Month 3 (D7.1); public and remote-sensing data allow WP1 and the design in WP4 to start regardless'],
    ['InSAR loses coherence on vegetated plains or on new port works', 'Medium', 'Medium', 'Corner reflectors and GNSS at the assets (T1.2); persistent-scatterer processing on built structures'],
    ['Fibre-optic access not granted', 'Medium', 'Low', 'Seismic noise from stations and temporary nodes gives the same velocity signal at lower resolution'],
    ['No strong earthquake or surge during the demonstration', 'High', 'Medium', 'Guarantees are tested in back-testing over the historical record, including the 2019 earthquake, and on storylines beyond it (T3.4)'],
    ['Surrogate fails its error bound in part of the domain', 'Low', 'Medium', 'Bound triggers fall-back to the full model on a reduced domain for those forecasts; the alarm margin widens automatically'],
    ['Equipment procurement or customs delays', 'Medium', 'Medium', 'Orders placed in Month 4; installation window to Month 12 with priority given to the sensors ranked highest in D4.1'],
    ['Loss of trained staff at the end-user', 'Medium', 'Medium', 'At least four staff of the Ministry of Infrastructure and Energy trained; procedures and software documented for use without the project team'],
]


def gantt(path, wp_codes, part):
    rows = []
    for wp, title, obj, span, _, tasks, dels in WPS:
        if wp not in wp_codes:
            continue
        rows.append(('wp', wp, f'{wp}  {title}', [span], [(m, c) for c, _, m in dels], wp))
        for code, t, (a, b) in tasks:
            rows.append(('t', code, t, [(a, b)], [], wp))
    W, H = 10.4, 7.0
    fig = plt.figure(figsize=(W, H)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    X0, X1 = 4.0, 10.25
    X = lambda m: X0 + (X1 - X0) * (m - 1) / 36.0
    top = H - 0.75
    ax.text(0.1, H - 0.25, f'Gantt chart, part {part}', fontsize=12, fontweight='bold', color='#1f3864', va='center')
    for k in range(3):
        ax.add_patch(Rectangle((X(12 * k + 1), top + 0.08), X(12 * k + 13) - X(12 * k + 1), 0.3, fc=['#c9daf2', '#8fb3e3', '#5b8fd0'][k], ec='white', lw=1.5))
        ax.text((X(12 * k + 1) + X(12 * k + 13)) / 2, top + 0.23, f'Year {k + 1}', ha='center', va='center', fontsize=10.5, fontweight='bold', color='#1f2933')
    for m in (1, 6, 12, 18, 24, 30, 36):
        ax.text((X(m) + X(m + 1)) / 2, top + 0.43, str(m), ha='center', va='bottom', fontsize=9, color='#52606d')
    ax.text(X0 - 0.08, top + 0.43, 'Month', ha='right', va='bottom', fontsize=9, color='#52606d')
    rh = min(0.3, (top - 0.9) / len(rows))
    for m in range(1, 38):
        ax.plot([X(m), X(m)], [top - len(rows) * rh, top + 0.06], color='#eceff3', lw=0.6, zorder=0)
    for i, (kind, code, label, spans, dels, wp) in enumerate(rows):
        y = top - (i + 0.5) * rh
        col = COL[wp]
        if kind == 'wp':
            ax.add_patch(Rectangle((0.05, y - rh / 2), X1 - 0.05, rh, fc='#f3f5f8', ec='none', zorder=0))
            ax.text(0.1, y, label, fontsize=10.2, fontweight='bold', color=col, va='center')
            for a, b in spans:
                ax.add_patch(Rectangle((X(a), y - 0.05), X(b + 1) - X(a), 0.1, fc=col, ec='none', alpha=0.45))
            for m, c in dels:
                ax.plot([X(m + 1) - 0.03], [y + 0.01], marker='v', ms=7.5, color='#1f2933', zorder=5)
                ax.text(X(m + 1) - 0.03, y + 0.07, c, fontsize=8, ha='center', va='bottom', color='#1f2933', zorder=6)
        else:
            ax.text(0.25, y, f'{code}  {SHORT.get(code, label)}', fontsize=9.6, color='#1f2933', va='center')
            for a, b in spans:
                ax.add_patch(FancyBboxPatch((X(a) + 0.01, y - 0.09), X(b + 1) - X(a) - 0.02, 0.18, boxstyle='round,pad=0,rounding_size=0.04', fc=col, ec='none', alpha=0.9))
    ybot = top - len(rows) * rh
    for code, m, t, _ in MILESTONES:
        ax.plot([X(m + 1) - 0.01] * 2, [ybot, top + 0.06], color='#f2b134', lw=1.2, ls='--', zorder=1)
        ax.plot([X(m + 1) - 0.01], [ybot - 0.14], marker='D', ms=7.5, color='#f2b134', mec='#1f2933', zorder=5)
        ax.text(X(m + 1) - 0.01, ybot - 0.27, code, ha='center', va='top', fontsize=8.8, fontweight='bold')
    ax.plot([0.2], [0.2], marker='v', ms=8, color='#1f2933'); ax.text(0.35, 0.2, 'deliverable', fontsize=9.5, va='center')
    ax.plot([1.6], [0.2], marker='D', ms=8, color='#f2b134', mec='#1f2933'); ax.text(1.75, 0.2, 'milestone', fontsize=9.5, va='center')
    fig.savefig(path, dpi=220); plt.close(fig)


GATES = {'MS3', 'MS4', 'MS5'}
NEW = [
    '**Phases start on evidence, not on dates.** Calibration (MS3), the go/no-go for live operation (MS4) and the confirmation of the miss rates (MS5) are gates with go, go-with-conditions and no-go rules fixed in advance (Milestones).',
    '**Back-testing runs alongside live operation.** Live bulletins start in Month 23 while back-testing continues to Month 27, so twelve full months of operation fit even after a two-month slip at MS4.',
    '**Buffers where the risks are.** Slack is placed on procurement, calibration and the go/no-go gate, the steps the Risk Assessment scores highest, not spread evenly across the plan.',
    '**Every task has an owner, a deliverable and a watched risk.** The risks that score high before mitigation are tied to the work package that owns them and watched monthly through numeric triggers.',
    '**The hand-over is inside the plan.** The staff of the Ministry of Infrastructure and Energy use every bulletin in Months 34–36 with the project team only in support, so the end state is demonstrated before the grant ends.',
]


def main(out, fig_path):
    import tempfile
    from docx.oxml import OxmlElement
    from build_sota import shade
    import build_wps as BWP
    import build_risk as BR
    import build_timeline as BT
    fig_a = fig_path.replace('.png', '_a.png'); fig_b = fig_path.replace('.png', '_b.png')
    gantt(fig_a, ('WP1', 'WP2', 'WP3', 'WP4'), '1 of 2: WP1–WP4')
    gantt(fig_b, ('WP5', 'WP6', 'WP7'), '2 of 2: WP5–WP7')
    fig_l = os.path.join(tempfile.mkdtemp(), 'fig_links.png'); BWP.fig_links(fig_l)

    def hdr(t):
        t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
        return t

    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.7)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Work Plan', bold=True, size=18, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and energy landfall of a subsiding Adriatic coast', bold=True, size=12, color='1F3864')

    heading(doc, '1. Structure and logic', 13.5, before=2)
    p = para(doc, 5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, f'The project runs for 36 months in {len(WPS)} work packages with {sum(len(w[5]) for w in WPS)} tasks, '
            f'{len({(d[0], d[2]) for w in WPS for d in w[6]})} deliverables (each progress report counted) and {len(MILESTONES)} milestones. WP1 to WP6 deliver objectives '
            'O1 to O6 one to one, so the deliverable codes of the objectives are kept; WP7 manages the whole. The logic runs in '
            'three phases:', size=10.5)
    for t in ['**Measure and design (Months 1–12).** WP1 measures the coastal motion and WP4 designs and installs the monitoring network; both start at once because the network design needs only existing and remote-sensing data.',
              '**Model and certify (Months 4–30).** WP2 builds and calibrates the coupled model and its fast surrogate on the data of WP1 and WP4; WP3 turns the forecasts into certified alarms and tests them on the historical record and on storylines beyond it.',
              '**Operate and hand over (Months 22–36).** After the go/no-go gate MS4, WP5 runs the system live for twelve months with the Ministry of Infrastructure and Energy as end-user; WP6 trains the people who will use and run it after the project and releases the software and procedures.']:
        q = para(doc, 3, 0.5); run(q, '• ', bold=True); rich(q, t, size=10.5)
    p = para(doc, 2, before=4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(fig_l, width=Cm(15.0))
    p = para(doc, 4)
    run(p, 'Figure 1. How the work packages feed each other. Live operation (WP5) feeds outcomes back to the alarms (WP3), and '
           'the alarms tell the network (WP4) which sensors are worth most. The Gantt chart is on the last two pages.',
        italic=True, size=9.5, color='52606D')

    h = heading(doc, '2. Work packages and tasks', 13.5, before=0); h.paragraph_format.page_break_before = True
    for wp, title, obj, (a, b), goal, tasks, dels in WPS:
        hh = heading(doc, f'{wp}. {title}', 12, color=COL[wp].lstrip('#').upper(), before=8); hh.paragraph_format.keep_with_next = True
        p = para(doc, 2); p.paragraph_format.keep_with_next = True
        run(p, f'Months {a}–{b} · objective {obj} · lead ', size=9.5, color='52606D')
        for part in re.split(r'(\[[^\]]+\])', BWP.LEAD[wp]):
            if part:
                r_ = run(p, part, size=9.5, color='52606D')
                if part.startswith('['):
                    r_.font.highlight_color = WD_COLOR_INDEX.YELLOW
        p = para(doc, 3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.keep_with_next = True
        run(p, 'Objective: ', bold=True, size=10.5); rich(p, goal, size=10.5)
        rows = [[c, t.replace('α_k', 'αₖ'), f'M{x}–M{y}'] for c, t, (x, y) in tasks]
        t = hdr(table(doc, ['Task', 'Description', 'Months'], rows, [1.4, 13.0, 2.6], size=9.5))
        for r_ in t.rows[1:-1]:
            for c in r_.cells:
                for pp in c.paragraphs:
                    pp.paragraph_format.keep_with_next = True
        p = para(doc, 5, before=3); run(p, 'Deliverables: ', bold=True, size=10)
        grouped = {}
        for c, t, m in dels:
            grouped.setdefault((c, t), []).append(f'M{m}')
        run(p, '; '.join(f'{c} {t} ({", ".join(ms)})' for (c, t), ms in grouped.items()), size=10)

    heading(doc, '3. Milestones and evidence gates', 13.5, before=10)
    rows = [[c + ('\n(gate)' if c in GATES else ''), f'M{m}', t, v.replace('α_k', 'αₖ')] for c, m, t, v in MILESTONES]
    t = hdr(table(doc, ['', 'Month', 'Milestone', 'Means of verification'], rows, [1.5, 1.4, 4.8, 9.3], size=9.5))
    for i, (c, *_r) in enumerate(MILESTONES, start=1):
        shade(t.rows[i].cells[0], 'FDE7C2' if c in GATES else 'E8EDF5')
    p = para(doc, 4, before=3)
    run(p, 'Each gate has go, go-with-conditions and no-go rules fixed in advance; see the Milestones section.', italic=True, size=9.5, color='52606D')

    heading(doc, '4. Critical path and buffers', 13.5, before=8)
    t = hdr(table(doc, ['Step on the critical path', 'Months', 'Milestone', 'Buffer'], BT.CRITICAL, [4.6, 1.8, 2.2, 8.4], size=9.5))
    p = para(doc, 4, before=3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, BT.SLIP, size=10)

    heading(doc, '5. The highest risks to the plan', 13.5, before=8)
    top = [r for r in BR.all_risks() if BR.band(r[2] * r[3])[0] in ('High', 'Very high')]
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.keep_with_next = True
    rich(p, f'The Risk Assessment lists {len(BR.all_risks())} risks with owners and numeric triggers. The {len(top)} that score high '
            'or very high before mitigation are shown here with the work package that owns them; after mitigation none is high.',
         size=10.5)
    rows = [[r[0], r[1], r[7], r[4], r[6]] for r in top]
    t = hdr(table(doc, ['', 'Risk', 'Owner', 'Trigger', 'Contingency'], rows, [1.1, 4.8, 1.4, 4.2, 5.5], size=8.8))
    for r_ in t.rows[1:]:
        shade(r_.cells[0], 'FBE9E7')

    h = heading(doc, '6. Management and monitoring', 13.5, before=8); h.paragraph_format.keep_with_next = True
    t = hdr(table(doc, ['Body or process', 'When', 'Where described'], BT.GOVERN, [4.6, 8.0, 4.4], size=9.5))
    for r_ in t.rows[:-1]:
        for c in r_.cells:
            for pp in c.paragraphs:
                pp.paragraph_format.keep_with_next = True

    heading(doc, '7. What is new in this work plan', 13.5, before=10)
    for x in NEW:
        q = para(doc, 3, 0.5); run(q, '• ', bold=True); rich(q, x, size=10.5)

    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
    sec.left_margin = sec.right_margin = Cm(1.5); sec.top_margin = sec.bottom_margin = Cm(1.0)
    p = para(doc, 0); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(fig_a, width=Cm(26.4))
    p = para(doc, 0); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.page_break_before = True
    p.add_run().add_picture(fig_b, width=Cm(26.4))
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Work_Plan.docx', sys.argv[2] if len(sys.argv) > 2 else 'certain_coast_gantt.png')
