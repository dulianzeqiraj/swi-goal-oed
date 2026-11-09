"""CERTAIN-COAST (NATO SPS proposal): Project schedule, for the upload "Project schedule" of the MYP application form.

The form asks for "a detailed schedule, including a Gantt or other suitable chart, showing the estimated duration of
each step or sub-project and their interdependence, the critical milestones and, if applicable, the deliverables by
milestones". Page 1 is a vector Gantt chart: every task with its months and duration, the dependencies between tasks,
the critical path, the evidence gates and project milestones, the deliverables, the twelve months of live operation and
the SPS reporting periods. The following pages give every step with what it needs, the milestones and deliverables by
SPS reporting milestone, the critical path with its buffers, and what is new in the schedule.

Spans, deliverables and milestones are read from build_workplan.py, the critical path and buffers from
build_timeline.py; the SPS reporting milestones (Months 0, 6, 18, 30, 36) are those of the application form text.

usage: python build_schedule.py OUT.pdf"""
import os
import re
import subprocess
import sys
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt
from pypdf import PdfReader, PdfWriter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, heading, rich, table, shade  # noqa: E402
import build_workplan as W  # noqa: E402
import build_timeline as BT  # noqa: E402

TITLE = 'Certified early warning to protect water, port and energy infrastructure on a sinking Adriatic coast'
SPS = [(0, 'Kick-off', 'SPS kick-off meeting'),
       (6, 'Milestone 1', 'First technical and financial report'),
       (18, 'Milestone 2', 'Second technical and financial report'),
       (30, 'Milestone 3', 'Third technical and financial report'),
       (36, 'Final report', 'Final technical and financial report')]
WPLAB = {'WP1': 'Coastal motion and relative sea level', 'WP2': 'Coupled model and certified surrogate',
         'WP3': 'Certified multi-hazard alarm', 'WP4': 'Monitoring network for the warnings', 'WP5': 'Live demonstration',
         'WP6': 'Training, transfer and dissemination', 'WP7': 'Management, data and risk'}
TLAB = dict(W.SHORT)
TLAB.update({'T2.2': 'Coupled model of the three hazards', 'T3.3': 'Joint guarantee over the three alarms',
             'T4.3': 'Operation, QC, streaming, assimilation', 'T6.2': 'Training of Survey staff and users'})
CRIT = ['T4.1', 'T4.2', 'T2.3', 'T2.4', 'T5.2', 'T6.4']          # the chain of build_timeline.CRITICAL
# what each step needs (predecessor, what it passes on); starting conditions for steps without a predecessor
DEPS = {
    'T1.1': [], 'T1.2': [('T7.2', 'site access')], 'T1.3': [('T1.1', 'InSAR time series')],
    'T1.4': [('T1.2', 'GNSS tie to the tide gauge'), ('T1.3', 'compaction separated')],
    'T2.1': [('T7.2', 'Survey data')], 'T2.2': [('T2.1', 'conceptual model and data')],
    'T2.3': [('T2.2', 'model'), ('T4.2', 'data streaming'), ('T1.3', 'land motion')],
    'T2.4': [('T2.3', 'calibrated parameters; preliminary ones first')],
    'T3.1': [('T2.2', 'model outputs that define the indicators')],
    'T3.2': [('T3.1', 'thresholds'), ('T2.4', 'surrogate error bound')], 'T3.3': [('T3.2', 'margin of each alarm')],
    'T3.4': [('T3.3', 'joint guarantee'), ('T2.4', 'storylines from the surrogate')],
    'T3.5': [('T3.4', 'back-testing, MS5'), ('T5.2', 'live outcomes')],
    'T4.1': [], 'T4.2': [('T4.1', 'design; sensors sure to be needed ordered in Month 4')],
    'T4.3': [('T4.2', 'installed network')], 'T4.4': [('T4.2', 'installed seismic sensors and piezometers')],
    'T5.1': [('T3.1', 'thresholds'), ('T3.2', 'alarm margins')],
    'T5.2': [('T2.4', 'surrogate passes gate MS4'), ('T5.1', 'bulletin protocol')],
    'T5.3': [('T2.4', 'surrogate'), ('T5.2', 'live operation')], 'T5.4': [('T4.2', 'network installed')],
    'T6.1': [], 'T6.2': [('T5.1', 'bulletin protocol'), ('T5.2', 'live operation')],
    'T6.3': [('T3.4', 'back-tested algorithms'), ('T2.4', 'surrogate')], 'T6.4': [('T5.2', 'live operation')],
    'T7.1': [], 'T7.2': [], 'T7.3': [],
}
START = {'T1.1': 'Starts at kick-off (open Sentinel-1 archive)', 'T4.1': 'Starts at kick-off (existing and remote-sensing data)',
         'T6.1': 'Starts with recruitment; supervised work in WP1–WP5', 'T7.1': 'Runs throughout', 'T7.2': 'Starts at kick-off',
         'T7.3': 'Runs throughout'}
# dependencies drawn on the chart (the others are short or would cross many bars; all are in the table)
ARROWS = [('T1.1', 'T1.3'), ('T1.3', 'T1.4'), ('T2.1', 'T2.2'), ('T2.2', 'T2.3'), ('T3.1', 'T3.2'), ('T3.3', 'T3.4'),
          ('T3.4', 'T3.5'), ('T4.2', 'T4.3'), ('T5.1', 'T5.2'),
          ('T4.1', 'T4.2'), ('T4.2', 'T2.3'), ('T2.3', 'T2.4'), ('T2.4', 'T5.2'), ('T5.2', 'T6.4')]
# deliverable -> task that produces it
LEFT = {'D6.1'}
DTASK = {'D1.1': 'T1.3', 'D2.1': 'T2.3', 'D2.2': 'T2.4', 'D3.1': 'T3.2', 'D3.2': 'T3.4', 'D4.1': 'T4.1', 'D4.2': 'T4.2',
         'D5.1': 'T5.2', 'D6.1': 'T6.3', 'D6.2': 'T6.4', 'D7.1': 'T7.2', 'D7.2': 'T7.1', 'D7.3': 'T7.1'}
NEW = [
    '**Every SPS report carries a decision, not only progress.** The reports fall on the evidence: Month 6 on the agreed '
    'network design (MS1), Month 18 on the calibration gate (MS3), Month 30 after the go/no-go and miss-rate gates (MS4, '
    'MS5), Month 36 on the hand-over (MS7). NATO sees each pass test and its result when it is decided.',
    '**Gates, not only dates.** Live operation starts only after the coupled model passes its validation test (MS3) and the '
    'surrogate meets its error bound (MS4); the certified miss rates are confirmed in back-testing (MS5). Each gate has a '
    'pass test and a fallback fixed in advance.',
    '**A full year live, with slack.** Back-testing runs alongside live operation, so twelve full months of operation fit '
    'even after a two-month slip at MS4, and they include every season of the hazards.',
    '**The hand-over is inside the schedule.** Trained staff of the Albanian Geological Survey run the bulletins for its wells in Months 34–36, with the project team only in support, so the end state is '
    'demonstrated before the grant ends.',
]

NAVY, RED, GREY, GATE = '#1F3864', '#B91C1C', '#5B6470', '#D97706'
plt.rcParams.update({'font.family': 'Liberation Sans', 'pdf.fonttype': 42, 'font.size': 9})


def tasks():
    out = {}
    for wp, title, obj, span, goal, ts, dels in W.WPS:
        for code, text, (a, b) in ts:
            out[code] = dict(wp=wp, text=text, a=a, b=b)
    return out


def deliverables():
    seen, out = set(), []
    for wp, title, obj, span, goal, ts, dels in W.WPS:
        for code, name, m in dels:
            if (code, m) not in seen:
                seen.add((code, m)); out.append((code, name, m))
    return sorted(out, key=lambda d: (d[2], d[0]))


def gantt(path):
    T = tasks()
    Wd, Ht = 11.69, 8.27
    fig = plt.figure(figsize=(Wd, Ht))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, Wd); ax.set_ylim(0, Ht); ax.axis('off')
    xl, xm_r, xd_r, X0, X1 = 0.30, 3.60, 3.93, 4.12, 11.0
    mw = (X1 - X0) / 36.0
    X = lambda m: X0 + (m - 1) * mw          # left edge of month m; end of month m is X(m + 1)

    ax.text(xl, Ht - 0.36, 'CERTAIN-COAST — Project schedule (36 months)', fontsize=15, fontweight='bold', color=NAVY, va='center')
    ax.text(xl, Ht - 0.62, TITLE + '.  Months count from the SPS kick-off meeting (Month 0).', fontsize=9.5,
            color='#374151', va='center')

    # SPS reporting periods
    ys0, ys1 = Ht - 1.24, Ht - 0.86
    ax.text(xl, (ys0 + ys1) / 2, 'SPS reporting periods', fontsize=9.5, fontweight='bold', color=NAVY, va='center')
    ax.plot([X(1)], [(ys0 + ys1) / 2], marker='>', ms=8, color=NAVY, zorder=4)
    ax.text(X(1) - 0.10, (ys0 + ys1) / 2, 'Kick-off\nMonth 0', fontsize=8.6, color=NAVY, ha='right', va='center', linespacing=1.0)
    prev = 0
    for k, (m, name, _) in enumerate(SPS[1:]):
        ax.add_patch(Rectangle((X(prev + 1), ys0), X(m + 1) - X(prev + 1), ys1 - ys0, fc=['#DCE6F4', '#C5D5EC'][k % 2],
                               ec='white', lw=1.5, zorder=1))
        ax.text((X(prev + 1) + X(m + 1)) / 2, (ys0 + ys1) / 2 + 0.07, name, fontsize=8.8, fontweight='bold', color=NAVY,
                ha='center', va='center')
        ax.text((X(prev + 1) + X(m + 1)) / 2, (ys0 + ys1) / 2 - 0.08, f'report at Month {m}', fontsize=8.6, color='#1f2933',
                ha='center', va='center')
        prev = m

    # years and months
    yy0, yy1 = Ht - 1.50, Ht - 1.29
    for k in range(3):
        ax.add_patch(Rectangle((X(12 * k + 1), yy0), 12 * mw, yy1 - yy0, fc='#E5E7EB', ec='white', lw=1.5))
        ax.text(X(12 * k + 7), (yy0 + yy1) / 2, f'Year {k + 1}', fontsize=9.5, fontweight='bold', color='#1f2933', ha='center', va='center')
    ymo = Ht - 1.62
    for m in range(1, 37):
        ax.text(X(m) + mw / 2, ymo, str(m), fontsize=8.6, color='#4B5563', ha='center', va='center')
    ax.text(xl, ymo, 'Work package / task', fontsize=9, fontweight='bold', color='#1f2933', va='center')
    ax.text(xm_r, ymo, 'Months', fontsize=8.6, fontweight='bold', color='#1f2933', ha='right', va='center')
    ax.text(xd_r, ymo, 'Dur.', fontsize=8.6, fontweight='bold', color='#1f2933', ha='right', va='center')

    rows = []
    for wp, title, obj, span, goal, ts, dels in W.WPS:
        rows.append(('wp', wp, span))
        for code, text, (a, b) in ts:
            rows.append(('t', code, (a, b)))
    ytop = Ht - 1.74
    rh = 0.156
    bh = 0.62 * rh
    ybot = ytop - len(rows) * rh
    ypos = {}

    # grid, live band
    for m in range(1, 38):
        ax.plot([X(m)] * 2, [ybot, ytop], color='#C9CED6' if (m - 1) % 12 == 0 else '#EEF0F3', lw=0.8 if (m - 1) % 12 == 0 else 0.5, zorder=0)
    ax.add_patch(Rectangle((X(23), ybot), 12 * mw, ytop - ybot, fc='#FCEBD3', ec='none', zorder=0))

    for i, (kind, code, (a, b)) in enumerate(rows):
        y = ytop - (i + 0.5) * rh
        ypos[code] = y
        if kind == 'wp':
            col = W.COL[code]
            ax.add_patch(Rectangle((xl - 0.08, y - rh / 2), X1 + 0.62 - xl, rh, fc='#F3F5F8', ec='none', zorder=0.5))
            ax.text(xl, y, f'{code}  {WPLAB[code]}', fontsize=9, fontweight='bold', color=col, va='center', zorder=2)
            ax.text(xm_r, y, f'{a}–{b}', fontsize=8.6, fontweight='bold', color=col, ha='right', va='center')
            ax.text(xd_r, y, str(b - a + 1), fontsize=8.6, fontweight='bold', color=col, ha='right', va='center')
            ax.add_patch(Rectangle((X(a), y - 0.022), X(b + 1) - X(a), 0.044, fc=col, ec='none', zorder=2))
            for xx in (X(a), X(b + 1)):
                ax.plot([xx], [y - 0.03], marker='v', ms=4.5, color=col, zorder=2)
        else:
            t = T[code]; col = W.COL[t['wp']]; crit = code in CRIT
            ax.text(xl + 0.12, y, f'{code}  {TLAB[code]}', fontsize=8.8, color='#111827', va='center',
                    fontweight='bold' if crit else 'normal')
            ax.text(xm_r, y, f'{a}–{b}', fontsize=8.6, color='#374151', ha='right', va='center')
            ax.text(xd_r, y, str(b - a + 1), fontsize=8.6, color='#374151', ha='right', va='center')
            ax.add_patch(FancyBboxPatch((X(a) + 0.008, y - bh / 2), X(b + 1) - X(a) - 0.016, bh,
                                        boxstyle='round,pad=0,rounding_size=0.025', fc=col, alpha=0.92,
                                        ec=RED if crit else 'none', lw=1.5 if crit else 0, zorder=3))

    # milestones: dashed lines through the chart, diamonds below
    yms = ybot - 0.20
    ax.text(xl, yms, 'Project milestones', fontsize=9, fontweight='bold', color='#1f2933', va='center')
    ax.text(xl, yms - 0.16, '(orange: evidence gates)', fontsize=8.6, color='#4B5563', va='center')
    for code, m, name, _ in W.MILESTONES:
        g = code in BT.GATES
        xx = X(m + 1)
        ax.plot([xx, xx], [yms + 0.07, ytop], color=GATE if g else '#9AA3AE', lw=1.1 if g else 0.8, ls=(0, (3, 2)), zorder=1)
        ax.plot([xx], [yms], marker='D', ms=7.5, color=GATE if g else NAVY, mec='white', mew=1.0, zorder=5)
        ax.text(xx, yms - 0.16, code + (' gate' if g else ''), fontsize=8.6, fontweight='bold',
                color='#92400E' if g else NAVY, ha='center', va='center')

    # dependencies
    for p, s in ARROWS:
        tp, ts = T[p], T[s]
        crit = p in CRIT and s in CRIT
        xe = X(tp['b'] + 1)
        yp, ysu = ypos[p], ypos[s]
        yedge = ysu + bh / 2 if ysu < yp else ysu - bh / 2
        arr = FancyArrowPatch((xe - 0.004, yp), (xe + 0.045, yedge), connectionstyle='angle,angleA=0,angleB=90,rad=0',
                              arrowstyle='-|>', mutation_scale=7 if crit else 6, lw=1.35 if crit else 0.85,
                              color=RED if crit else GREY, shrinkA=0, shrinkB=0, zorder=6)
        arr.set_path_effects([pe.Stroke(linewidth=(1.35 if crit else 0.85) + 1.6, foreground='white'), pe.Normal()])
        ax.add_patch(arr)

    # deliverables at the end of the task that produces them
    for code, name, m in deliverables():
        tk = DTASK[code]
        y = ypos[tk]
        xx = X(m + 1)
        ax.plot([xx - 0.004], [y + bh / 2 + 0.018], marker='v', ms=5.2, color='#111827', zorder=7)
        left = code in LEFT
        ax.text(xx - 0.07 if left else xx + 0.085, y, code, fontsize=8.6, fontweight='bold', color='#111827',
                ha='right' if left else 'left', va='center', zorder=8, bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none'))

    # legend
    yl = 0.30
    xs = xl
    ax.add_patch(FancyBboxPatch((xs, yl - 0.045), 0.32, 0.09, boxstyle='round,pad=0,rounding_size=0.02', fc=W.COL['WP2'], ec='none'))
    ax.text(xs + 0.40, yl, 'Task (colour = work package)', fontsize=8.6, va='center'); xs += 2.05
    ax.add_patch(FancyBboxPatch((xs, yl - 0.045), 0.32, 0.09, boxstyle='round,pad=0,rounding_size=0.02', fc=W.COL['WP4'], ec=RED, lw=1.5))
    ax.text(xs + 0.40, yl, 'Critical path', fontsize=8.6, va='center'); xs += 1.15
    ax.add_patch(FancyArrowPatch((xs, yl), (xs + 0.34, yl), arrowstyle='-|>', mutation_scale=6, lw=0.85, color=GREY, shrinkA=0, shrinkB=0))
    ax.text(xs + 0.42, yl, 'Needs (red: on the critical path)', fontsize=8.6, va='center'); xs += 2.25
    ax.plot([xs + 0.05], [yl], marker='v', ms=5.5, color='#111827')
    ax.text(xs + 0.16, yl, 'Deliverable', fontsize=8.6, va='center'); xs += 0.95
    ax.plot([xs + 0.05], [yl], marker='D', ms=7, color=NAVY, mec='white')
    ax.plot([xs + 0.22], [yl], marker='D', ms=7, color=GATE, mec='white')
    ax.text(xs + 0.34, yl, 'Milestone / gate', fontsize=8.6, va='center'); xs += 1.35
    ax.add_patch(Rectangle((xs, yl - 0.06), 0.30, 0.12, fc='#FCEBD3', ec='none'))
    ax.text(xs + 0.38, yl, 'Live operation, Months 23–34', fontsize=8.6, va='center')
    ax.text(xl, 0.10, 'A task "12–18" runs from the start of Month 12 to the end of Month 18. Every dependency, with what it '
            'passes on, is listed on the next page; deliverables by SPS milestone and the buffers follow.',
            fontsize=8.6, style='italic', color='#4B5563', va='center')
    fig.savefig(path)
    plt.close(fig)


def tidy(t):
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(0); p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.line_spacing = Pt(10.2)
    return t


def tables_docx(path):
    T = tasks()
    doc = Document()
    s = doc.sections[0]
    s.orientation = WD_ORIENT.LANDSCAPE
    s.page_width, s.page_height = Cm(29.7), Cm(21.0)
    s.left_margin = s.right_margin = Cm(1.4); s.top_margin = s.bottom_margin = Cm(1.0)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(9.5)

    p = para(doc, 2); run(p, 'CERTAIN-COAST — Steps, durations and dependencies', bold=True, size=13.5, color='1F3864')
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, f'{len(W.WPS)} work packages, {len(T)} tasks, 36 months. "Needs" lists the tasks each step depends on and what '
            'they pass on; a step that needs one still running starts on its preliminary results. Tasks on the critical '
            'path, whose chain decides the end date, are in bold.', size=9.5)
    rows, kinds = [], []
    for wp, title, obj, span, goal, ts, dels in W.WPS:
        rows.append([wp, f'**{WPLAB[wp]}**', f'{span[0]}–{span[1]}', str(span[1] - span[0] + 1), '', '']); kinds.append(wp)
        for code, text, (a, b) in ts:
            need = '; '.join(f'{q} ({why})' for q, why in DEPS[code]) or START.get(code, '—')
            crit = code in CRIT
            rows.append([f'**{code}**' if crit else code, f'**{text}**' if crit else text, f'{a}–{b}', str(b - a + 1),
                         need, 'Yes' if crit else '']); kinds.append(None)
    t = tidy(table(doc, ['Task', 'Step', 'Months', 'Dur.', 'Needs (what it passes on)', 'Critical'],
                   [[c.replace('α_k', 'αₖ') for c in r] for r in rows], [1.2, 12.9, 1.45, 1.05, 8.7, 1.6], size=8.6))
    for i, k in enumerate(kinds, start=1):
        if k:
            for c in t.rows[i].cells:
                shade(c, 'EEF2F8')
        elif t.rows[i].cells[5].text == 'Yes':
            shade(t.rows[i].cells[5], 'FBE3E3')

    h = heading(doc, 'Milestones and deliverables by SPS reporting milestone', 13.5, before=0)
    h.paragraph_format.page_break_before = True
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'The SPS reporting milestones are those of the application form and of the Info tab of the budget workbook. '
            'Each report gives the project milestones reached in its period, with the result of their pass tests, and the '
            'deliverables due in it.', size=9.5)
    dl = deliverables()
    rows = [['**Kick-off**, Month 0', 'Project start; steering committee constituted; access agreements started (T7.2)', '—']]
    prev = 0
    for m, name, what in SPS[1:]:
        ms = [f'**{c}** (M{mm}) {n}' + (' (evidence gate)' if c in BT.GATES else '') + '. Pass: ' + re.sub(r'^(D\d\.\d):', r'\1 shows', v.replace('α_k', 'αₖ'))
              for c, mm, n, v in W.MILESTONES if prev < mm <= m]
        ds = [f'{c} (M{mm}) ' + ('Progress report to SPS' if c == 'D7.2' else n) for c, n, mm in dl if prev < mm <= m]
        rows.append([f'**{name}**, Month {m}\n{what.split(" and ")[0].replace("technical", "report")}'
                     f' on Months {prev + 1}–{m}', '\n'.join(ms), '\n'.join(ds)])
        prev = m
    t = tidy(table(doc, ['SPS milestone', 'Project milestones reached, with their pass tests', 'Deliverables due'], rows,
                   [4.9, 13.3, 8.7], size=8.8))
    for r_ in t.rows[1:]:
        shade(r_.cells[0], 'EEF2F8')

    heading(doc, 'Critical path and buffers', 13.5, before=8)
    tidy(table(doc, ['Step on the critical path', 'Months', 'Ends at', 'Buffer'], BT.CRITICAL, [6.0, 1.8, 2.3, 16.8], size=8.8))
    p = para(doc, 2, before=3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, BT.SLIP, size=9.3)

    heading(doc, 'What is new in this schedule', 13.5, before=6)
    for x in NEW:
        q = para(doc, 2, 0.4); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; run(q, '• ', bold=True, size=9.3); rich(q, x, size=9.3)
    doc.save(path)


def main(out):
    work = tempfile.mkdtemp()
    g = os.path.join(work, 'gantt.pdf'); gantt(g)
    d = os.path.join(work, 'schedule_tables.docx'); tables_docx(d)
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', work, d], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    w = PdfWriter()
    for f in (g, d.replace('.docx', '.pdf')):
        for pg in PdfReader(f).pages:
            w.add_page(pg)
    w.add_metadata({'/Title': 'CERTAIN-COAST — Project schedule', '/Subject': TITLE})
    with open(out, 'wb') as fh:
        w.write(fh)
    print('saved', out, '| pages', len(w.pages), '| tasks', len(tasks()), '| deliverables', len(deliverables()))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Project_Schedule.pdf')
