"""CERTAIN-COAST (NATO SPS proposal): Objectives. Aim, six specific objectives with targets, deliverables and months,
a table linking objectives to the gaps and innovations of the State of the Art, and success at the end of the project.
Reuses the Word helpers of build_sota.py. Assumes a 36-month project (adjust to the call)."""
import os
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
      'Post-event protocol executed for every event above the agreed magnitude or water level during the demonstration'],
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


def main(out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, TITLE, bold=True, size=18, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    p = para(doc, 8); rich(p, AIM, size=11.5)
    p = para(doc, 8); rich(p, 'The aim breaks into six specific objectives. O1 and O2 build the physical basis, O3 and O4 make the warnings '
                              'certified and well observed, O5 demonstrates them in operation, and O6 makes them last. Months assume a '
                              '36-month project.')
    for code, title, what, targets, deliv, link_ in OBJ:
        heading(doc, f'{code}. {title}', 13, before=8)
        p = para(doc, 4); rich(p, what)
        p = para(doc, 2); run(p, 'Measurable targets', bold=True, size=11, color='1E8A5A')
        for t in targets:
            p = para(doc, 2, 0.5); run(p, '• ', bold=True); rich(p, t)
        p = para(doc, 2, before=3); run(p, 'Deliverables: ', bold=True, size=10.5); run(p, deliv, size=10.5)
        p = para(doc, 6); run(p, 'Addresses: ', bold=True, size=10.5, color='52606D'); run(p, link_, size=10.5, color='52606D')
    heading(doc, 'Objectives at a glance', 13, before=10)
    rows = [[c, t, l, d] for c, t, _, _, d, l in OBJ]
    table(doc, ['', 'Objective', 'Gap and innovation (State of the Art)', 'Deliverable (month)'], rows, [1.1, 4.4, 5.8, 5.7], size=10)
    para(doc, 6)
    heading(doc, 'What success looks like at Month 36', 13, before=8)
    for t in SUCCESS:
        p = para(doc, 3, 0.5); run(p, '• ', bold=True); rich(p, t)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Objectives.docx')
