"""CERTAIN-COAST (NATO SPS proposal): Security relevance. Why the hazards are a security problem, alignment with the SPS
Key Priorities (revised 2024), contribution to national resilience (baseline requirements, Warsaw 2016), critical
(undersea) infrastructure at the energy landfall, why certified warnings matter for security, asset-hazard-security
table, cooperation and transfer. NATO policy references checked against NATO pages (see the note at the end)."""
import os
import sys
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_sota import run, para, heading, rich, table, link  # noqa: E402

LEAD = ('The Durrës coast concentrates three kinds of critical infrastructure of a NATO member in a few kilometres: the wellfields '
        'that supply drinking water, the country\'s main port, and an energy landfall where supply arrives from the sea. All three '
        'stand on soft, subsiding coastal sediments next to active thrust faults, and the 26 November 2019 Mw 6.4 earthquake '
        'caused liquefaction along this coast. They are threatened slowly, by subsidence, rising relative sea level and the '
        'advance of seawater into the aquifer, and suddenly, by earthquakes and storm surges, and the slow threats make the sudden '
        'ones worse. CERTAIN-COAST protects them with warnings whose reliability is stated and verified, which is what a security '
        'decision needs.')

SECTIONS = [
    ('1. Alignment with the SPS Key Priorities', [
        ('b', '**Environment, Climate Change and Security.** Relative sea-level rise, coastal subsidence and seawater intrusion are '
              'climate-related threats to water supply and coastal infrastructure. CERTAIN-COAST measures them on a NATO member\'s '
              'coast and turns them into operational warnings, the step from climate risk to security action.'),
        ('b', '**Energy Security.** The energy landfall is the point where supply arriving from the sea meets the national system. '
              'Its stability under shaking, liquefaction, extreme water levels and subsidence is assessed in one framework and '
              'monitored continuously during the project.'),
        ('b', '**Innovation and Emerging and Disruptive Technologies.** The warnings rely on machine-learned surrogates of a '
              'physical model, but with certified error bounds and distribution-free guarantees on how often they miss. That makes '
              'the use of AI in a security-relevant decision chain reliable and traceable, rather than a black box.'),
    ]),
    ('2. Contribution to national resilience', [
        ('p', 'Allies committed at the 2016 Warsaw Summit to seven baseline requirements for civil preparedness, which reflect '
              'continuity of government, essential services to the population and civil support to the military. CERTAIN-COAST '
              'contributes directly to three of them:'),
        ('b', '**Resilient food and water resources.** The wellfields are protected against salinisation, which takes years to reverse '
              'once a well turns saline, by a certified intrusion warning and a pumping rule that is safe for all three hazards.'),
        ('b', '**Resilient energy supplies.** The energy landfall is protected against liquefaction, extreme water levels and '
              'subsidence-driven loss of elevation.'),
        ('b', '**Resilient civil transport.** The port, a national logistics node, receives liquefaction and extreme-sea-level warnings '
              'that protect operations and the infrastructure behind them.'),
        ('p', 'Ports and energy landfalls of Allies are also part of the infrastructure on which civil support to the military '
              'depends in a crisis. Knowing, with a stated reliability, whether they will function after an earthquake or a storm '
              'supports that function.'),
    ]),
    ('3. Critical infrastructure where it comes ashore', [
        ('p', 'NATO has given new attention to critical undersea infrastructure, including the NATO Maritime Centre for the Security '
              'of Critical Undersea Infrastructure launched at Allied Maritime Command in May 2024. An energy landfall is where '
              'that infrastructure comes ashore, and it is exposed to threats that maritime surveillance does not cover: the ground '
              'beneath it can liquefy in an earthquake, subside year by year, and be overtopped by extreme water levels. '
              'CERTAIN-COAST covers these natural threats at the landfall, complementing the protection of the subsea section.'),
    ]),
    ('4. Innovation for security: warnings with certified reliability', [
        ('b', '**Decisions need known error rates.** A warning used to shut a well, restrict a quay or inspect a landfall must say how '
              'often it misses and how often it raises a false alarm. CERTAIN-COAST states both and checks them in operation.'),
        ('b', '**Trust survives only if warnings are accountable.** Every bulletin is logged with its outcome, so operators and '
              'authorities can audit the system instead of trusting it blindly.'),
        ('b', '**Extremes are what security is about.** The guarantees are built to hold when forcing leaves the observed record, '
              'in droughts, compound storms and after earthquakes, where ordinary warnings fail most.'),
        ('b', '**One picture, not three.** After an earthquake or a storm, civil protection receives one consistent assessment of '
              'water, port and energy, from one model, instead of three separate ones that may contradict each other.'),
    ]),
]

TABLE = [
    ['Wellfields (drinking water)', 'Seawater intrusion; subsidence; earthquake-induced change in heads', 'Loss of water supply for years; salinised wells cannot be quickly restored', 'Certified intrusion alarm; pumping rule safe for all three hazards; post-event sampling'],
    ['Port (logistics)', 'Liquefaction; extreme sea levels and surges; subsidence', 'Loss of quay operations and of the logistics node; damage to adjacent infrastructure', 'Liquefaction factor of safety tracking the water table; certified extreme-water-level warning'],
    ['Energy landfall', 'Liquefaction; extreme water levels; subsidence; earthquake shaking', 'Interruption of energy supply arriving from the sea', 'Landfall stability check combining shaking, liquefaction, water level and subsidence; continuous monitoring'],
    ['All three (civil protection)', 'Compound events: earthquake plus storm plus long-term subsidence', 'Simultaneous failure of water, port and energy', 'One model and one bulletin for the three hazards; post-event protocol'],
]

COOP = [
    '**Cooperation of NATO and partner scientists.** The project joins geodesy, hydrogeology, geotechnics and applied mathematics from both sides around a shared security problem, as the SPS Programme intends.',
    '**Capacity that stays.** Early-career researchers and operator staff are trained to run and develop the system, so the capability remains in the country after the project.',
    '**Transfer to other coasts.** The approach needs only free satellite data, existing seismic stations and fibre, and a calibrated model; it transfers to other subsiding coasts with wellfields, ports and energy landfalls in the Adriatic and the wider Mediterranean.',
    '**Open results.** Software, procedures and data are released openly, so Allies and partners can apply them without licensing barriers.',
]

REFS = [
    ('NATO Science for Peace and Security Programme (overview and Key Priorities)', 'https://www.nato.int/cps/en/natohq/85291.htm'),
    ('NATO: Resilience, civil preparedness and Article 3 (baseline requirements)', 'https://www.nato.int/cps/en/natohq/topics_132722.htm'),
    ('NATO Allied Maritime Command: launch of the NATO Maritime Centre for Security of Critical Undersea Infrastructure (2024)', 'https://mc.nato.int/media-centre/news/2024/nato-officially-launches-new-nmcscui'),
]


def main(out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.5)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Security Relevance', bold=True, size=18, color='1F3864')
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and energy landfall of a subsiding Adriatic coast', bold=True, size=12, color='1F3864')
    p = para(doc, 6); rich(p, LEAD, size=11)
    for title, blocks in SECTIONS:
        heading(doc, title, 13.5, before=6)
        for kind, t in blocks:
            if kind == 'p':
                p = para(doc, 5); rich(p, t)
            else:
                p = para(doc, 3, 0.5); run(p, '• ', bold=True); rich(p, t)
    heading(doc, '5. Assets, hazards and security consequences', 13.5, before=8)
    table(doc, ['Asset', 'Hazards', 'Security consequence', 'CERTAIN-COAST contribution'], TABLE, [3.2, 4.2, 4.6, 5.0], size=10)
    para(doc, 4)
    heading(doc, '6. Cooperation, capacity and transfer', 13.5)
    for t in COOP:
        p = para(doc, 3, 0.5); run(p, '• ', bold=True); rich(p, t)
    p = para(doc, 2, before=6); run(p, 'NATO references used in this section', bold=True, size=10, color='52606D')
    for t, u in REFS:
        p = para(doc, 1, 0.5); run(p, t + ': ', size=9, color='52606D'); link(p, u, u.replace('https://', ''), 9)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Security_Relevance.docx')
