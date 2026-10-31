"""CERTAIN-COAST (NATO SPS proposal): Abstract. Main abstract (about 250 words), short abstract (about 150 words),
summary for non-experts, what is new, keywords, and two short titles of about 100 characters (the SPS sample form
asks for a title of about 100 characters). Word counts are computed and printed in the document. Consistent with the
State of the Art, Objectives, Work Plan, Expected Results and Security Relevance."""
import os
import sys
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_sota import run, para, heading, rich  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')

MAIN = [
    'The Durrës coast of Albania concentrates three kinds of critical infrastructure of a NATO member within a few kilometres: '
    'drinking-water wellfields, the country\'s main port and an energy landfall. All stand on soft, subsiding sediments near '
    'active thrust faults, and the 2019 Mw 6.4 earthquake caused liquefaction along this coast. Three hazards threaten them '
    'through the same variables, relative sea level and the water table: seawater intrusion, liquefaction and extreme sea '
    'levels. Today they are modelled separately, and no warning states how often it misses.',
    'CERTAIN-COAST will build, demonstrate and hand over one early-warning system for all three. InSAR, GNSS and sea-level data '
    'give the relative sea level at each asset. One calibrated physical model couples variable-density groundwater flow, aquifer '
    'compaction, the water-table-dependent liquefaction factor of safety and extreme water levels; a fast surrogate with a '
    'certified error bound runs it in real time. Each alarm adds online conformal risk control and an extreme-aware margin, so '
    'its miss rate stays below a set target even beyond the observed record. In preparatory synthetic tests this kept the share '
    'of seasons above the chloride limit at 4–9%, where a static alarm allowed 13–21%. The monitoring network is designed to '
    'reduce these miss rates at least cost.',
    'The system will run live for twelve months with the water utility, port, landfall operator and civil protection, and will '
    'be released as open software, transferable to other subsiding coasts.',
]

SHORT = ('The Durrës coast of Albania hosts, within a few kilometres, the drinking-water wellfields, main port and an energy '
         'landfall of a NATO member, on subsiding sediments where the 2019 earthquake caused liquefaction. Seawater intrusion, '
         'liquefaction and extreme sea levels threaten them through shared variables, yet are monitored separately, and no '
         'warning states how often it misses. CERTAIN-COAST couples the three hazards in one physical model driven by satellite, '
         'GNSS and sea-level data, runs it in real time through a surrogate with a certified error bound, and issues alarms whose '
         'miss rate is guaranteed below a set target, even beyond the observed record. A sensor network designed for these '
         'warnings, twelve months of live operation with the operators and civil protection, and open software make the '
         'capability lasting and transferable.')

LAY = ('Near Durrës, the drinking-water wells, the main port and an energy connection from the sea stand on low ground that is '
       'slowly sinking. Three dangers threaten them: sea water entering the wells, ground that turns almost liquid in an '
       'earthquake, and the sea flooding the land in storms. The dangers are linked, but today they are watched separately. '
       'CERTAIN-COAST will watch them together, from satellites and sensors on the ground, and send warnings that say in advance '
       'how often they can be wrong, and then check it. Local operators will run the system after the project.')

NEW = [
    '**One model for three hazards.** The first coupling of seawater intrusion, liquefaction and extreme sea level through '
    'their shared variables, the relative sea level R(t) = η(t) − u_z(t) and the water table. A pumping decision is judged '
    'against all three at once: more pumping raises intrusion and subsidence but lowers liquefaction susceptibility.',
    '**Warnings with a guarantee.** The first coastal early warning whose miss rate is certified for each hazard (≤ α_k) and '
    'jointly (≤ Σα_k), with a margin built to hold when droughts, storms or earthquakes push conditions beyond the record.',
    '**Sensors chosen for the warnings.** The first multi-hazard, goal-oriented design of a coastal monitoring network: each '
    'sensor, from piezometers and chloride samples to InSAR, seismic noise and fibre, is ranked by how much it reduces the miss '
    'probability per unit cost.',
    '**Seismic noise as a water-table gauge.** Seismic velocity changes calibrated as a pore-pressure sensor in saturated '
    'coastal sediments, where pore pressure decides liquefaction.',
]

KEYWORDS = ('seawater intrusion; liquefaction; relative sea-level rise; land subsidence; InSAR; multi-hazard early warning; '
            'conformal risk control; certified surrogate model; critical infrastructure; Adriatic coast')

TITLES = [
    'Certified early warning of seawater intrusion, liquefaction and sea extremes on a subsiding coast',
    'Certified multi-hazard warning for the water, port and energy assets of a subsiding Adriatic coast',
]

PRIORITIES = ('SPS Key Priorities: Environment, Climate Change and Security; Energy Security; Innovation and Emerging and '
              'Disruptive Technologies')


def words(t):
    return len(t.split())


def label(doc, title, n=None, before=8):
    p = heading(doc, title, 13.5, before=before)
    if n is not None:
        run(p, f'   ({n} words)', size=10, color='52606D')
    return p


def main(out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.6)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Abstract', bold=True, size=18, color='1F3864')
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, PRIORITIES, italic=True, size=10, color='52606D')

    n_main = sum(words(t) for t in MAIN)
    label(doc, 'Abstract', n_main, before=4)
    for t in MAIN:
        p = para(doc, 5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, t)

    label(doc, 'Short abstract (for a tight form field)', words(SHORT))
    p = para(doc, 5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, SHORT)

    label(doc, 'Summary for non-experts', words(LAY))
    p = para(doc, 5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, LAY)

    label(doc, 'What is new')
    for t in NEW:
        p = para(doc, 3, 0.5); run(p, '• ', bold=True); rich(p, t)

    label(doc, 'Keywords')
    p = para(doc, 5); rich(p, KEYWORDS)

    label(doc, 'Short title options (the SPS form asks for about 100 characters)')
    for t in TITLES:
        p = para(doc, 3, 0.5); run(p, '• ', bold=True); run(p, t); run(p, f'   ({len(t)} characters)', size=10, color='52606D')
    p = para(doc, 3, before=4)
    run(p, f'The full title has {len(FULL)} characters; use it as the subtitle or in the proposal text.', italic=True, size=10, color='52606D')
    doc.save(out)
    print('saved', out)
    print('main', n_main, '| short', words(SHORT), '| lay', words(LAY), '| titles', [len(t) for t in TITLES], '| full', len(FULL))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Abstract.docx')
