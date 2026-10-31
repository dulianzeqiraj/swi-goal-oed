"""CERTAIN-COAST (NATO SPS proposal): Deliverables. List at a glance, a timeline figure (by work package, access level and
evidence gates), counts by type and access, one description per deliverable (contents, acceptance test, format and
where it goes, reviewer, depends on, feeds), the quality-assurance process and what is new. Numbers, titles and months
are read from build_workplan.py; type, access level and leads from build_wps.py.

usage: python build_deliverables.py OUT.docx"""
import os
import re
import sys
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, heading, rich, table, shade  # noqa: E402
import build_workplan as W  # noqa: E402
import build_wps as WPS  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')

# code -> (contents, acceptance test, format and where it goes, reviewed by, depends on, feeds)
DESC = {
    'D1.1': ('Vertical and east velocity maps of the three asset areas from Sentinel-1 (2014 onward) and GNSS; elastic and inelastic compaction parameters and the head limit h_pc; the 2019 coseismic and postseismic motion; relative sea level R(t) with uncertainty at each asset.',
             'Vertical-velocity uncertainty of the order of 1–2 mm/yr at asset points; InSAR and GNSS agree within their uncertainty.',
             'Report and gridded data (GeoTIFF, NetCDF); regional maps in Zenodo, asset-point values to the operators.',
             'WP2 lead; operators for asset points', 'T1.1–T1.3; GNSS and corner reflectors (D4.2)', 'WP2 sea boundary; WP3 extremes; WP5 pumping limit'),
    'D2.1': ('Set-up of the coupled model (variable-density flow, salt memory, compaction, liquefaction factor of safety, coastal water level); calibrated parameters from ES-MDA; validation on held-out data.',
             'Held-out heads, chloride, InSAR and seismic velocity fall inside the 90% predictive intervals at close to the nominal rate (gate MS3).',
             'Model files and report; site version restricted, synthetic-coast version public.',
             'Steering committee; WP3 lead', 'D1.1; data from D4.2; operator records (D7.1)', 'D2.2; WP3; WP4 refinement'),
    'D2.2': ('Trained neural or kernel operator of the coupled model; adjoint-weighted error indicator; conformal quantile; test report on held-out full-model runs.',
             'Coverage of the error bound at least 1 − δ on test runs; thousands of storylines per day; alarm prototype passes a dry run (gate MS4).',
             'Software and report; site version restricted, synthetic-coast version public (ONNX).',
             'Steering committee; WP5 lead', 'D2.1', 'D3.1; live operation (WP5)'),
    'D3.1': ('Construction of the three-part margin; proofs of the miss-rate bound for each alarm and of the joint bound; allocation of tolerances by consequence; implementation with unit tests.',
             'Proofs checked by a reviewer outside WP3; implementation passes its tests and reproduces the synthetic examples.',
             'Report (public) and code (released with D6.1).',
             'Independent reviewer; steering committee', 'D2.2; thresholds agreed in T3.1', 'D3.2; WP5 bulletins'),
    'D3.2': ('Back-testing of the full chain over the record since 2014 and on storylines beyond it (drought, compound storm, 2019-type earthquake, increased pumping), under a protocol frozen before the results.',
             'Miss rate of each alarm at or below its target with Clopper–Pearson intervals; false-alarm rate reported (gate MS5).',
             'Report; protocol published with a DOI before the results; aggregated results public, asset annex restricted.',
             'Steering committee; operators', 'D3.1; D2.2; D1.1', 'WP5; D5.1; papers'),
    'D4.1': ('Ranking of every candidate sensor by its value for the three warnings per unit cost; the chosen network within budget; installation and access plan.',
             'Approved by the steering committee and the operators (MS1).',
             'Report, restricted (sensor locations inside sites).',
             'Steering committee; operators', 'Preliminary sensitivities (WP2); access (D7.1)', 'D4.2; procurement (T4.2)'),
    'D4.2': ('Installed piezometers and loggers, GNSS, corner reflectors and seismic stations, with telemetry, quality control and data streaming.',
             'At least 90% data availability over the first month (MS2).',
             'Demonstrator and installation report, restricted.',
             'WP7; operators', 'D4.1; procurement', 'D1.1; D2.1; WP5'),
    'D5.1': ('Twelve months of bulletins to the operators and civil protection; the bulletin log with outcomes; verification of the miss and false-alarm rates; the joint pumping rule; post-event protocol executions.',
             'Observed miss rates within targets with confidence intervals; bulletin log complete and reproducible (MS6).',
             'Report; verification statistics public, asset annex restricted.',
             'Steering committee; operators; civil protection', 'D3.1–D3.2; D4.2; D2.2', 'D6.2; D7.3; papers'),
    'D6.1': ('Open software (model, surrogate, alarms, network design) with documentation, tests and containers; the synthetic test coast; open datasets; verification statistics.',
             'Release with a DOI; installed and run on the synthetic coast by someone outside the project team.',
             'Software (Apache-2.0) and data (CC BY 4.0) in Zenodo and a public repository.',
             'External tester; WP2 and WP3 leads', 'D2.2; D3.1; D1.1', 'Transfer workshop; other coasts'),
    'D6.2': ('Operating procedures for the wellfields, the port and the landfall, and the post-event protocol; a policy brief for the national authorities.',
             'At least one procedure adopted per asset; policy brief delivered to the national authorities (MS7).',
             'Procedures restricted to the operators; public version of the policy brief.',
             'Operators; civil protection', 'D5.1', 'Hand-over; national policy'),
    'D7.1': ('Data management plan (version 1); signed access agreements with the operators; data classification for the release gate.',
             'Access agreements signed by the operators; data management plan approved by the steering committee.',
             'Report; data plan public, agreements restricted.',
             'Steering committee', 'Commitment letters', 'All work packages'),
    'D7.2': ('Progress, deliverables and milestones; risk register; indicators (results, dissemination, gender, ethics); spending against the budget.',
             'Submitted to the SPS Programme on time and accepted.',
             'Report to the SPS Programme, restricted.',
             'Steering committee', 'All work packages', 'NATO SPS'),
    'D7.3': ('Results, verification of the guarantees, hand-over and sustainability arrangements, spending, and lessons for other coasts.',
             'Submitted to the SPS Programme and accepted; public summary released.',
             'Report; public summary, full report restricted.',
             'Steering committee', 'All deliverables', 'NATO SPS; follow-up funding'),
}

QA = [
    '**Owner.** Each deliverable has a responsible author in the leading work package and a reviewer from another work package or outside the project.',
    '**Timing.** A complete draft is circulated four weeks before the due month and reviewed within two weeks.',
    '**Release gate.** Every deliverable is classified (public, restricted or both) and, if it uses operator data, sent to the operators for review of sensitive content before release.',
    '**Acceptance.** The steering committee checks the acceptance test of each deliverable; for D2.1, D2.2 and D3.2 the result decides the evidence gate (MS3, MS4, MS5).',
    '**Version control.** Deliverables, data and code are versioned; each public deliverable gets a persistent identifier.',
]

NEW = [
    '**Every deliverable has a pass test.** Each states in advance how it will be judged, and three of them decide whether the project moves on (gates at Months 18, 22 and 27).',
    '**The central claim is registered before it is tested.** The back-testing protocol of D3.2 is published with a DOI before the results are computed.',
    '**Open and restricted in one deliverable.** Mixed deliverables have a public part (methods, verification) and a restricted annex (asset-level results), so openness never exposes critical infrastructure.',
    '**A stranger can run it.** D6.1 is accepted only when someone outside the team installs the software and reproduces the synthetic coast.',
    '**Guarantees checked in public.** D5.1 publishes the observed miss and false-alarm rates of the live warnings, so anyone can check the certified rates.',
]


def access_class(a):
    al = a.lower()
    if 'public' in al and 'restricted' in al:
        return 'Public + restricted annex'
    return 'Public' if al.startswith('public') else 'Restricted'


def items():
    out = []
    for wp, title, obj, span, desc, tasks, dels in W.WPS:
        seen = set()
        for code, name, m in dels:
            if (code, m) in seen:
                continue
            seen.add((code, m))
            ty, acc = WPS.DTYPE[code]
            out.append(dict(code=code, name=name, month=m, wp=wp, type=ty, access=acc, cls=access_class(acc)))
    out.sort(key=lambda d: (d['month'], d['code']))
    return out


def ms_of(code):
    for c, m, n, ev in W.MILESTONES:
        if code in re.findall(r'D\d\.\d', ev):
            return c + (' (gate)' if c in ('MS3', 'MS4', 'MS5') else '')
    return '—'


def fig_deliv(path, its):
    Wd, Ht = 6.7, 3.6
    fig, ax = plt.subplots(figsize=(Wd, Ht), dpi=300)
    wps = [w[0] for w in W.WPS]
    ymap = {wp: len(wps) - i for i, wp in enumerate(wps)}
    style = {'Public': ('o', '#1e8a5a'), 'Restricted': ('s', '#9c6b30'), 'Public + restricted annex': ('D', '#6a4fb3')}
    for g, lab in ((18, 'MS3'), (22, 'MS4'), (27, 'MS5')):
        ax.vlines(g, 0.4, len(wps) + 0.62, color='#D97706', lw=1.2, ls=(0, (4, 3)), zorder=1)
        ax.text(g, len(wps) + 0.72, lab + ' gate', fontsize=8.6, color='#92400E', ha='center', va='bottom', fontweight='bold',
                zorder=4)
    placed = {}
    for d in its:
        y = ymap[d['wp']]; mk, col = style[d['cls']]
        ax.plot(d['month'], y, marker=mk, ms=9, color=col, mec='white', mew=1.0, zorder=3)
        k = placed.get((d['wp'], d['month']), 0); placed[(d['wp'], d['month'])] = k + 1
        ax.text(d['month'], y + 0.30, d['code'], fontsize=8.6, ha='center', va='bottom', color='#1f2328', zorder=4,
                bbox=dict(boxstyle='square,pad=0.08', fc='white', ec='none'))
    ax.set_yticks([ymap[w] for w in wps]); ax.set_yticklabels(wps, fontsize=10)
    for t, w in zip(ax.get_yticklabels(), wps):
        t.set_color(W.COL[w]); t.set_fontweight('bold')
    ax.set_xlim(0, 37.5); ax.set_ylim(0.4, len(wps) + 1.35)
    ax.set_xticks([1, 6, 12, 18, 24, 30, 36]); ax.set_xticklabels([f'M{m}' for m in (1, 6, 12, 18, 24, 30, 36)], fontsize=9.5)
    ax.grid(axis='y', color='#e3e6ea', lw=0.8); ax.set_axisbelow(True)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.spines['left'].set_color('#9aa3ad'); ax.spines['bottom'].set_color('#9aa3ad')
    handles = [plt.Line2D([], [], marker=m, color=c, ls='', ms=8, label=l) for l, (m, c) in style.items()]
    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.0, -0.10), ncol=3, frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def hl(t):
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    for r in t.rows[1:]:
        for c in r.cells:
            for p in c.paragraphs:
                for rn in p.runs:
                    if '[' in rn.text:
                        rn.font.highlight_color = WD_COLOR_INDEX.YELLOW
    return t


def main(out):
    its = items()
    work = tempfile.mkdtemp(); fig = os.path.join(work, 'fig_deliverables.png'); fig_deliv(fig, its)
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.7)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Deliverables', bold=True, size=18, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    n_pub = sum(d['cls'] == 'Public' for d in its); n_res = sum(d['cls'] == 'Restricted' for d in its)
    n_mix = sum(d['cls'] == 'Public + restricted annex' for d in its)
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, f'CERTAIN-COAST produces **{len(its)} deliverables** over 36 months: {n_pub} public, {n_res} restricted to the '
            f'operators, authorities or the SPS Programme, and {n_mix} with a public part and a restricted annex, following the '
            'two-tier dissemination plan. Each deliverable has an acceptance test stated in advance; three of them decide the '
            'evidence gates at Months 18, 22 and 27. Months count from the start of the grant.', size=10.5)

    heading(doc, '1. Deliverables at a glance', 13.5, before=4)
    rows = [[d['code'], d['name'], d['wp'], WPS.LEAD[d['wp']], d['type'], d['cls'], f'M{d["month"]}', ms_of(d['code'])] for d in its]
    t = hl(table(doc, ['No.', 'Deliverable', 'WP', 'Lead', 'Type', 'Access', 'Month', 'Milestone'], rows,
                 [1.1, 3.75, 1.25, 2.4, 2.35, 2.75, 1.35, 2.05], size=8.5))
    acc_col = {'Public': 'E6F4EC', 'Restricted': 'F6EFE6', 'Public + restricted annex': 'F1ECFA'}
    for i, d in enumerate(its, start=1):
        shade(t.rows[i].cells[5], acc_col[d['cls']])
    para(doc, 3)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(fig, width=Cm(15.5))
    p = para(doc, 4)
    run(p, 'Figure 1. Deliverables by month and work package. Marker shows the access level; dashed lines mark the three evidence '
           'gates.', italic=True, size=9.5, color='52606D')

    h = heading(doc, '2. Deliverable descriptions', 13.5, before=0); h.paragraph_format.page_break_before = True
    seen = []
    for d in its:
        if d['code'] in seen:
            continue
        seen.append(d['code'])
        months = [x['month'] for x in its if x['code'] == d['code']]
        mtxt = ('Month ' if len(months) == 1 else 'Months ') + ' and '.join(str(m) for m in months)
        c, a, f, r, dep, feeds = DESC[d['code']]
        p = para(doc, 2, before=6); p.paragraph_format.keep_with_next = True
        run(p, f'{d["code"]}  {d["name"]}', bold=True, size=11.5, color=W.COL[d['wp']].lstrip('#').upper())
        run(p, f'   {d["wp"]} · {mtxt} · {d["type"]} · {d["cls"]}', size=9.5, color='52606D')
        tt = table(doc, ['', ''], [['Contents', c], ['Acceptance test', a], ['Format and where', f], ['Reviewed by', r],
                                   ['Depends on', dep], ['Feeds', feeds]], [3.4, 13.6], size=9.5)
        tt._tbl.remove(tt.rows[0]._tr)
        nrow = len(tt.rows)
        for ri, row in enumerate(tt.rows):
            shade(row.cells[0], 'E8EDF5')
            for pp in row.cells[0].paragraphs:
                for rn in pp.runs:
                    rn.bold = True
            if ri < nrow - 1:
                for pp in row.cells[0].paragraphs + row.cells[1].paragraphs:
                    pp.paragraph_format.keep_with_next = True

    heading(doc, '3. Quality assurance', 13.5, before=10)
    for x in QA:
        q = para(doc, 3, 0.5); run(q, '• ', bold=True); rich(q, x, size=10.5)
    heading(doc, '4. What is new in these deliverables', 13.5, before=8)
    for x in NEW:
        q = para(doc, 3, 0.5); run(q, '• ', bold=True); rich(q, x, size=10.5)
    doc.save(out)
    print('saved', out, '|', len(its), 'deliverables', n_pub, n_res, n_mix)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Deliverables.docx')
