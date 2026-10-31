"""CERTAIN-COAST (NATO SPS proposal): Objectives. Aim; a figure of how the six objectives feed each other through the
evidence gates; objectives at a glance (key indicator, deadline, why achievable, fallback); each objective with targets,
deliverables, milestones, risks watched and the gaps and innovations it addresses; success at Month 36; what is new.
OBJ, AIM and SUCCESS are imported by other builders (introduction, results); keep their shape.

usage: python build_objectives.py OUT.docx"""
import os
import re
import sys
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_sota import run, para, heading, rich, table  # noqa: E402

TITLE = 'CERTAIN-COAST — Objectives'
FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')

AIM = ('**Aim.** To build, demonstrate and hand over an early-warning system for the Durrës coast in which the three hazards, '
       'seawater intrusion at the wellfields, liquefaction at the port and the energy landfall, and extreme sea levels at all '
       'three, come from one physical model of the coast; in which every warning is issued fast enough to act on; and in which '
       'every warning carries a stated, verifiable bound on how often it misses. The system protects three kinds of critical '
       'infrastructure on a NATO member\'s main port coast at once: water supply, port logistics and energy supply.')

OBJ = [
    ('O1', 'Measure the subsiding coast',
     'Build the relative-sea-level record R(t) = η(t) − u_z(t) at the wellfields, the port and the landfall: vertical land motion '
     'from the Sentinel-1 archive (2014 onwards) and GNSS, sea level from tide gauge and regional reconstruction, with the '
     'loading and ice-mass signals removed. Separate the elastic (seasonal, reversible) from the inelastic (permanent) '
     'compaction of the aquifer clays, and record the 2019 coseismic and postseismic motion.',
     ['Vertical-velocity maps of the three asset areas with stated uncertainty; target uncertainty of the order of 1–2 mm/yr at asset points',
      'Elastic and inelastic compaction separated at every wellfield, and the pumping rate the land can sustain without inelastic compaction',
      'Time series R(t) with uncertainty at each asset, ready to drive the hazard models'],
     'D1.1 Coastal motion atlas and R(t) series (Month 12)', 'Gap: land motion as a linear trend. Innovations P1, P4, M5'),
    ('O2', 'Build one coupled physical model of the coast and a certified fast copy of it',
     'Couple variable-density groundwater flow with salt memory in the clays, poroelastic compaction, the water-table-dependent '
     'liquefaction factor of safety FS(x, t) = CRR / CSR(z_w(x, t)), and the extreme water level at the coast (tide, surge and '
     'waves on top of R(t)). Calibrate it on heads, conductivity, chloride, InSAR and seismic data, and train a neural or '
     'kernel operator surrogate whose error is bounded for every forecast.',
     ['One model that outputs the three hazard indicators from one set of forcings: chloride at each production well, FS at the port and landfall, total water level at each asset',
      'Calibration reproduces held-out observations within their stated uncertainty',
      'Surrogate fast enough to run thousands of storylines per day, with an a-posteriori error bound attached to each forecast'],
     'D2.1 Calibrated coupled model (Month 18); D2.2 Certified surrogate (Month 22)', 'Gaps: hazards modelled separately; no per-forecast certificate. Innovations P2, P3, M4'),
    ('O3', 'Certify the warnings',
     'Design an alarm for each hazard k that fires when the forecast indicator exceeds its threshold minus a margin m_k made of '
     'three parts: the surrogate error bound, an online conformal risk-control term for nonstationary data, and an extreme-aware '
     'term that widens the margin when the forcing leaves the observed record. Control the probability that any of the three '
     'alarms is missed, and allocate the tolerances α_k by consequence.',
     ['Miss rate of each alarm at or below its target α_k (indicatively 5–10%) in back-testing over the historical record and in the live demonstration, reported with confidence intervals',
      'Joint miss probability of the three alarms at or below Σα_k, with the false-alarm rate reported alongside',
      'Under drought, storm and compound storylines beyond the record, miss rates within target where a static alarm fails (preparatory tests: 4–9% against 13–21%)'],
     'D3.1 Certified alarm algorithms and proofs (Month 24); D3.2 Back-testing report (Month 27)', 'Gap: no warning carries a guarantee. Innovations M1, M2'),
    ('O4', 'Design and install the monitoring network for the warnings',
     'Choose the sensors jointly, piezometers with conductivity loggers, chloride sampling, GNSS, seismic noise and temporary '
     'nodes, and fibre-optic sensing on existing telecom fibre where it is available, so as to maximise the expected reduction '
     'of the miss probability of the three alarms per unit cost. Install, operate and assimilate the network into the model.',
     ['Every candidate sensor ranked by its value for the three warnings; the installed network is the best-value set within the budget',
      'Network installed by Month 12 and operating with at least 90% data availability',
      'Seismic velocity changes calibrated against the water table at the port or landfall, as a pore-pressure sensor'],
     'D4.1 Network design report (Month 6); D4.2 Network installed and streaming (Month 12)', 'Gap: new sensors measured but not designed. Innovations M3, P5'),
    ('O5', 'Demonstrate the system in operation at the three assets',
     'Run the system live for at least 12 months, issuing bulletins to the water utility, the port authority, the landfall '
     'operator and civil protection. Evaluate every pumping rule and operating decision against all three hazards at once, so '
     'that no action moves the risk from one asset to another. Execute a post-event protocol after any strong earthquake or '
     'storm surge.',
     ['At least 12 months of continuous operation with bulletins logged and their outcomes verified',
      'A pumping rule for the wellfields that keeps the three alarms within target together, documented and agreed with the operator',
      'Post-event protocol executed for every event above the agreed magnitude or water level during the demonstration',
      'A guaranteed lower bound on the value of the warning reported for each user\'s own decision (innovation V1, Impact section)'],
     'D5.1 Live demonstration report (Month 34)', 'Gap: no early warning treats the hazards as one system. Innovations P3, M1, M2'),
    ('O6', 'Transfer the system and build lasting capacity',
     'Train early-career researchers and the staff of the operators and authorities; release the software and the protocols '
     'openly; and write the operating procedures and a policy brief in the form the operators and the national authorities '
     'can adopt.',
     ['Early-career researchers trained through the project (indicatively at least 6) and operator staff trained to run the system unaided (indicatively at least 20)',
      'Open software and data release with documentation',
      'Operating procedures adopted by the operators of the wellfields, the port and the landfall (at least one per asset), and a policy brief delivered to the national authorities'],
     'D6.1 Software and data release (Month 33); D6.2 Operating procedures and policy brief (Month 36)', 'Capacity and sustainability'),
]

SUCCESS = [
    'The relative sea level at every asset of the Durrës coast is known with uncertainty, and the land motion behind it is separated into what pumping can reverse and what it cannot.',
    'One calibrated model gives, from the same forcing, the chloride at the wells, the liquefaction factor of safety at the port and the landfall, and the extreme water level at all three.',
    'Each warning is issued with its margin and its certified miss rate, and the record of the live demonstration shows the rates were met.',
    'The monitoring network is the best-value set for the warnings, not a list of convenient sites.',
    'The operators run the system themselves, and the pumping rule they adopt keeps all three hazards within target together.',
]


SHORT = {'O1': 'Measure the\nsubsiding coast', 'O2': 'One coupled model\n+ certified copy', 'O3': 'Certify the\nwarnings',
         'O4': 'Network designed\nfor the warnings', 'O5': 'Operate live at\nthe three assets', 'O6': 'Transfer and\nlasting capacity'}

# objective -> key indicator, deadline (gate), achievable because, if it falls short
GLANCE = {
    'O1': ('Vertical-velocity uncertainty of the order of 1–2 mm/yr at asset points; InSAR and GNSS agree',
           'M12 (MS2)', 'Free Sentinel-1 archive since 2014; GNSS and corner reflectors installed by WP4',
           'GNSS and levelling where InSAR loses coherence (R4)'),
    'O2': ('Held-out data inside the 90% predictive intervals; surrogate bound met (coverage ≥ 1 − δ)',
           'M18 (gate MS3); M22 (gate MS4)', 'Preparatory coupled model; staged build from Month 7',
           'Two-dimensional sections and a larger bound (R5); full model on a reduced domain (R6)'),
    'O3': ('Miss rate of each alarm ≤ αₖ, joint miss ≤ Σαₖ, with Clopper–Pearson intervals',
           'M24 (D3.1); M27 (gate MS5)', 'Preparatory synthetic tests: 4–9% against 13–21% for a static alarm',
           'Margin widened until the target is met; staged alerts if false alarms are too many (R7)'),
    'O4': ('Every sensor ranked by value per unit cost; ≥ 90% data availability',
           'M6 (MS1); M12 (MS2)', 'Equipment budget of about half the grant; orders placed in Month 4',
           'Design re-run with the remaining budget; piezometers alone if seismic velocity fails (R9, R19)'),
    'O5': ('12 months of logged bulletins with outcomes; observed miss rates within targets; pumping rule agreed',
           'M34 (MS6)', 'End-users committed by letter; live operation starts only after gate MS4',
           'Verification by back-testing and storylines if no strong event occurs (R14)'),
    'O6': ('≥ 6 early-career researchers; ≥ 20 operator staff; ≥ 1 procedure adopted per asset; open release',
           'M33 (D6.1); M36 (MS7)', 'Training from Month 3; maintenance agreement by Month 33',
           'Extra training; procedures restated with the operator (R16, R18)'),
}
DEPS = [('O1', 'O2'), ('O4', 'O2'), ('O2', 'O3'), ('O3', 'O5'), ('O4', 'O5'), ('O5', 'O6')]
NEW = [
    '**Objectives as a chain with gates.** Figure 1 shows which objective feeds which and where the evidence gates sit, so a delay or a failed test can be traced to the objectives it affects.',
    '**An objective that measures reliability itself.** O3 is met only if each warning misses no more often than its certified rate; the target is a guarantee, checked on the record and in operation, not a delivered report.',
    '**Every objective has a fallback.** Each one names the risks that could stop it and what is delivered if it falls short, so no objective can fail silently.',
    '**Value to the user as a target.** O5 includes a guaranteed lower bound on what each warning is worth to each operator, set in their own terms before live operation.',
]


def fig_chain(path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    Wd, Ht = 10.0, 4.35
    fig = plt.figure(figsize=(6.7, 6.7 * Ht / Wd), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, Wd); ax.set_ylim(0, Ht); ax.axis('off')
    ax.add_patch(FancyBboxPatch((0.1, Ht - 0.72), Wd - 0.2, 0.6, boxstyle='round,pad=0,rounding_size=0.08', fc='#1F3864', ec='none'))
    ax.text(Wd / 2, Ht - 0.42, 'Aim: certified early warning for three hazards at three assets, from one model, run by the operators',
            ha='center', va='center', fontsize=9.2, color='white', fontweight='bold')
    pos = {'O1': (1.05, 2.75), 'O4': (1.05, 0.95), 'O2': (3.55, 1.85), 'O3': (6.05, 1.85), 'O5': (8.55, 1.85), 'O6': (8.55, 0.5)}
    col = {'O1': '#2e6db4', 'O2': '#6a4fb3', 'O3': '#b03a3a', 'O4': '#1e8a5a', 'O5': '#c27c12', 'O6': '#0e7490'}
    bw = 1.8
    hgt = {c: (0.8 if c == 'O6' else 0.95) for c in pos}
    for c, (x, y) in pos.items():
        h = hgt[c]
        ax.add_patch(FancyBboxPatch((x - bw / 2, y - h / 2), bw, h, boxstyle='round,pad=0,rounding_size=0.07', fc='white', ec=col[c], lw=1.6))
        if c == 'O6':
            ax.text(x, y + 0.17, 'O6', ha='center', va='center', fontsize=9.4, fontweight='bold', color=col[c])
            ax.text(x, y - 0.15, 'Transfer, capacity', ha='center', va='center', fontsize=8.6, color='#1f2328')
        else:
            ax.text(x, y + 0.25, c, ha='center', va='center', fontsize=9.6, fontweight='bold', color=col[c])
            ax.text(x, y - 0.14, SHORT[c], ha='center', va='center', fontsize=8.6, color='#1f2328', linespacing=1.1)

    def arr(p, q, lab=None, lab_xy=None, gate=False):
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=12, color='#52606D', lw=1.3, shrinkA=1, shrinkB=1))
        if lab:
            x, y = lab_xy
            if gate:
                ax.text(x, y, lab, ha='center', va='center', fontsize=8.6, color='#92400E', fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.15', fc='#FDE7C2', ec='none'))
            else:
                ax.text(x, y, lab, ha='center', va='center', fontsize=8.6, color='#52606D', style='italic',
                        bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none'))
    E = lambda c: pos[c][0] + bw / 2
    Wl = lambda c: pos[c][0] - bw / 2
    arr((E('O1'), 2.55), (Wl('O2'), 2.1), 'R(t), compaction', (1.05, 2.1))
    arr((E('O4'), 1.15), (Wl('O2'), 1.6))
    arr((E('O2'), 1.85), (Wl('O3'), 1.85), 'MS3, MS4', ((E('O2') + Wl('O3')) / 2, 2.55), gate=True)
    arr((E('O3'), 1.85), (Wl('O5'), 1.85), 'MS5', ((E('O3') + Wl('O5')) / 2, 2.55), gate=True)
    arr((E('O4'), 0.7), (Wl('O5') + 0.3, 1.85 - 0.475), 'data streams', (4.6, 1.0))
    arr((8.55, 1.85 - 0.475), (8.55, 0.5 + 0.4))
    fig.savefig(path, dpi=300); plt.close(fig)


def sym(t):
    return t.replace('α_k', 'αₖ').replace('m_k', 'mₖ')


def main(out):
    import tempfile
    from docx.oxml import OxmlElement
    from build_sota import shade
    import build_workplan as W
    import build_risk as BR
    import build_wps as WPS
    work = tempfile.mkdtemp(); f1 = os.path.join(work, 'fig_objectives.png'); fig_chain(f1)
    ms_by_del = {}
    for code, m, name, ev in W.MILESTONES:
        for d in re.findall(r'D\d\.\d', ev):
            ms_by_del.setdefault(d, []).append(f'{code} (M{m}' + (', gate' if code in ('MS3', 'MS4', 'MS5') else '') + ')')
    risks = {r[0]: r for r in BR.all_risks()}
    objwp = {v: k for k, v in WPS.OBJMAP.items() if v != '—'}

    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.7)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, TITLE, bold=True, size=18, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, AIM, size=10.5)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'The aim breaks into six specific objectives, delivered one to one by work packages WP1–WP6. O1 and O4 observe '
            'the coast, O2 models it, O3 certifies the warnings, O5 runs them live with the operators, and O6 makes them last '
            '(Figure 1). Months count from the start of the 36-month grant.', size=10.5)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(f1, width=Cm(16.0))
    p = para(doc, 4)
    run(p, 'Figure 1. How the objectives feed each other. Orange labels: the evidence gates that must be passed before the next '
           'objective can start.', italic=True, size=9.5, color='52606D')

    heading(doc, '1. Objectives at a glance', 13.5, before=6)
    rows = [[c, GLANCE[c][0], GLANCE[c][1], GLANCE[c][2], GLANCE[c][3]] for c, *_ in OBJ]
    t = table(doc, ['', 'Key indicator', 'Deadline', 'Achievable because', 'If it falls short'], rows,
              [1.0, 4.7, 2.4, 4.2, 4.7], size=8.8)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    for r_ in t.rows[1:]:
        shade(r_.cells[0], 'E8EDF5')

    h = heading(doc, '2. The six objectives', 13.5, before=0); h.paragraph_format.page_break_before = True
    for code, title, what, targets, deliv, link_ in OBJ:
        hh = heading(doc, f'{code}. {title}', 12.5, before=8); hh.paragraph_format.keep_with_next = True
        p = para(doc, 3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.keep_with_next = True
        rich(p, sym(what), size=10.5)
        p = para(doc, 1); p.paragraph_format.keep_with_next = True; run(p, 'Measurable targets', bold=True, size=10.5, color='1E8A5A')
        for tx in targets:
            q = para(doc, 1, 0.5); q.paragraph_format.keep_with_next = True; run(q, '• ', bold=True); rich(q, sym(tx), size=10)
        dels = re.findall(r'D\d\.\d', deliv)
        ms = sorted({m for d in dels for m in ms_by_del.get(d, [])})
        wp = objwp.get(code)
        rids = [r for r, v in risks.items() if v[7] == wp]
        kv = [['Delivered by', f'{wp}; ' + deliv], ['Milestones', '; '.join(ms) if ms else '—'],
              ['Risks watched', ', '.join(rids) if rids else '—'], ['Addresses', link_]]
        tt = table(doc, ['', ''], kv, [3.0, 14.0], size=9.5)
        tt._tbl.remove(tt.rows[0]._tr)
        n = len(tt.rows)
        for ri, row in enumerate(tt.rows):
            shade(row.cells[0], 'EEF2F8')
            for pp in row.cells[0].paragraphs:
                for rn in pp.runs:
                    rn.bold = True
            if ri < n - 1:
                for pp in row.cells[0].paragraphs + row.cells[1].paragraphs:
                    pp.paragraph_format.keep_with_next = True

    heading(doc, '3. What success looks like at Month 36', 13.5, before=10)
    for tx in SUCCESS:
        q = para(doc, 3, 0.5); run(q, '• ', bold=True); rich(q, tx, size=10.5)
    heading(doc, '4. What is new in these objectives', 13.5, before=8)
    for tx in NEW:
        q = para(doc, 3, 0.5); run(q, '• ', bold=True); rich(q, tx, size=10.5)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Objectives.docx')
