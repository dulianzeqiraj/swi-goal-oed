"""CERTAIN-COAST (NATO SPS proposal): Security relevance. Key facts; the security chain from coastal threats through the
assets of Durrës to NATO resilience (figure); alignment with NATO priorities (SPS Key Priorities revised 2024, the 2027-1
call, the 2022 Strategic Concept, the Climate Change and Security Action Plan, resilience commitments 2016-2023); the
three baseline requirements served, with evidence; critical infrastructure where it comes ashore; the security decisions
the project supports and their stated reliability; the planning horizon (certified safe window and its closing year,
from method_window.json; figure); AI testing, evaluation, verification and validation; assets, hazards and consequences;
protection of sensitive results; cooperation and transfer; what is new; NATO and national sources with links.
NATO texts were checked through web search of NATO pages and official copies (nato.int could not be opened directly
from the build environment).

usage: python build_security.py OUT.docx"""
import json
import os
import sys
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, heading, rich, table, link, shade  # noqa: E402
import build_exec_summary as BE  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')
INK, MUTED = '#1f2328', '#5b6672'
C_W, C_P, C_E, C_N = '#2E6DB4', '#1F3864', '#C27C12', '#1E8A5A'   # water, port, energy, NATO resilience

LEAD = ('The Durrës coast concentrates three kinds of critical infrastructure of a NATO Ally within a few kilometres: the '
        'wellfields that supply drinking water, the country\'s main port, and an energy landfall where supply arrives from the '
        'sea. All three stand on soft, subsiding coastal sediments near active thrust faults, and the 26 November 2019 Mw 6.4 '
        'earthquake caused liquefaction along this coast [L1]. They are threatened slowly, by subsidence, rising relative sea '
        'level and the advance of seawater into the aquifer, and suddenly, by earthquakes and storm surges, and the slow threats '
        'make the sudden ones worse. CERTAIN-COAST gives the people responsible for these assets warnings whose reliability is '
        'stated in advance and verified in operation, and a second number that security planning lacks: **how long a safe way '
        'of operating the three assets together will still exist**.')

TILES = [
    ('1 April 2009', 'Albania becomes a NATO Ally [S1]'),
    ('93.6%', 'of Albania\'s seaborne freight left from Durrës, Q2 2025 [S2]'),
    ('Mw 6.4', '26 Nov 2019 earthquake; liquefaction on this coast [L1]'),
    ('3 of 7', 'NATO baseline requirements served: water, energy, transport [S3]'),
    ('≤ αₖ', 'certified miss rate of each warning, verified live'),
    ('12 months', 'live operation with the operators and civil protection'),
    ('38 vs 43–97', 'years: certified safe window vs single-hazard plans (synthetic test)'),
    ('2 tiers', 'open methods; asset-level vulnerability kept restricted'),
]

PRIORITIES = [
    '**SPS Key Priorities (revised 2024) [S4].** The project addresses **Environment, Climate Change and Security** (relative '
    'sea-level rise, subsidence and salinisation turned into operational warnings), **Energy Security** (the stability of an '
    'energy landfall) and **Emerging and Disruptive Technologies** (machine-learned surrogates and conformal guarantees used in '
    'a security decision chain).',
    '**The 2027-1 call [S5].** Among its areas of particular interest the call names **critical infrastructure protection**, '
    '**energy resilience** and **artificial intelligence**; CERTAIN-COAST combines the three at one Allied site.',
    '**The 2022 Strategic Concept [S6]:** "Climate change is a defining challenge of our time, with a profound impact on Allied '
    'security. It is a crisis and threat multiplier." On this coast the multiplication is physical: sea-level rise and '
    'subsidence raise the water table, which weakens the ground in an earthquake and brings seawater closer to the wells.',
    '**The Climate Change and Security Action Plan (2021) [S7]** commits NATO to an annual Climate Change and Security Impact '
    'Assessment, published since 2022. CERTAIN-COAST provides measured, asset-level evidence of the kind such assessments use, '
    'and the NATO Climate Change and Security Centre of Excellence in Montreal, accredited in 2024 [S8], is a natural channel '
    'for its open results.',
    '**Resilience commitments.** The seven baseline requirements agreed at Warsaw in 2016 [S3], the Strengthened Resilience '
    'Commitment of 2021 [S9] and the Alliance Resilience Objectives agreed at Vilnius in 2023, which guide national resilience '
    'goals and plans [S10], all treat essential services as part of deterrence and defence. The project delivers a tested '
    'capability for three of those services.',
]

BASELINE = [
    ['Resilient food and water resources', 'Wellfields (drinking water)', 'Seawater intrusion, which takes years to reverse once a well turns saline; subsidence',
     'Certified intrusion alarm; pumping kept inside the certified safe window', 'D3.2 back-testing; D5.1 live verification'],
    ['Resilient civil transportation systems', 'Port of Durrës', 'Liquefaction of quay backlands in an earthquake; storm surge; subsidence',
     'Liquefaction state that follows the water table; certified water-level warning; post-event bulletin', 'D5.1; operating procedures D6.2'],
    ['Resilient energy supplies', 'Energy landfall', 'Liquefaction; extreme water levels; subsidence; shaking',
     'Landfall stability check combining the four; continuous monitoring; post-event bulletin', 'D5.1; operating procedures D6.2'],
    ['Civil support to the military (purpose of the requirements)', 'Port and landfall', 'Loss of a logistics or energy node just when it is needed',
     'A stated and verified answer to "will it function after the earthquake or the storm?"', 'D5.1 verification ledger'],
]

DECISIONS = [
    ['Water utility', 'Reduce or shift pumping; take a well out of service', 'Weeks to months', 'Intrusion alarm; safe pumping window', 'Miss rate ≤ α₁, verified'],
    ['Port authority', 'Restrict operations or loads; inspect quays after an earthquake; prepare for a surge', 'Hours to days', 'Liquefaction state; water-level warning; post-event bulletin', 'Miss rates ≤ α₂, α₃'],
    ['Energy landfall operator', 'Inspect, protect or isolate the landfall', 'Hours to days', 'Landfall stability check; water-level warning', 'Miss rates ≤ α₂, α₃'],
    ['Civil protection', 'Set priorities across water, port and energy after an event', 'Hours to days', 'One bulletin for the three assets from one model', 'Joint miss ≤ Σαₖ'],
    ['National authorities; resilience and defence planners', 'Plan adaptation and investment; set the planning horizon', 'Years to decades',
     'Certified closing year of the safe window; years added by each sensor', 'Certified at the stated level; recomputed yearly'],
]

TEVV = [
    ['Testing', 'The full chain is replayed over the record since 2014 and on storylines beyond it, under a protocol published with a DOI before the results (D3.2)'],
    ['Evaluation', 'Miss and false-alarm rates are reported for each alarm, each asset and each regime (drought, storm season, after an earthquake)'],
    ['Verification', 'During live operation an anytime-valid test runs on every outcome and the verification ledger is published every quarter (Methodology, Section 5.7)'],
    ['Validation', 'Thresholds and the value of each warning are agreed with the operators (T3.1); live use starts only after the go/no-go gate MS4'],
]

ASSETS = [
    ['Wellfields (drinking water)', 'Seawater intrusion; subsidence; earthquake-induced change in heads', 'Loss of water supply for years; salinised wells cannot be quickly restored', 'Certified intrusion alarm; pumping within the safe window; post-event sampling'],
    ['Port (logistics)', 'Liquefaction; extreme sea levels and surges; subsidence', 'Loss of quay operations and of the logistics node; damage to adjacent infrastructure', 'Liquefaction state tracking the water table; certified extreme-water-level warning'],
    ['Energy landfall', 'Liquefaction; extreme water levels; subsidence; earthquake shaking', 'Interruption of energy supply arriving from the sea', 'Landfall stability check combining shaking, liquefaction, water level and subsidence; continuous monitoring'],
    ['All three (civil protection)', 'Compound events: earthquake plus storm plus long-term subsidence', 'Simultaneous failure of water, port and energy', 'One model and one bulletin for the three hazards; safe window for the three assets together; post-event protocol'],
]

PROTECT = [
    '**Two tiers.** Methods, software and the verification ledger are open; thresholds, bulletin contents, asset-level vulnerability and sensor locations inside sites stay with the operators and authorities (Dissemination Plan).',
    '**A release gate.** Every output is classified before release, and sensitive content is aggregated or anonymised ("a port", "an energy landfall") or kept in a restricted annex.',
    '**Open verification of a restricted service.** The observed miss and false-alarm rates are published with confidence bounds, so anyone can check the guarantee without seeing a vulnerable location.',
]

COOP = [
    '**Allies and partners on one security problem.** Geodesy, hydrogeology, geotechnics and applied mathematics from the NATO and the partner country work on the same assets, as the SPS Programme intends.',
    '**A twin coast.** The partner country brings a second subsiding coast, on which transfer is tested within the project (Partnership).',
    '**Capacity that stays.** Early-career researchers and operator staff learn to run and develop the system, so the capability remains in the country after the project.',
    '**Transfer to other Allied coasts.** The method needs free satellite data, existing seismic stations and a calibrated model, and transfers to subsiding coasts with wellfields, ports and energy landfalls in the Adriatic and the wider Mediterranean.',
    '**A measured baseline.** Ground motion, water levels and seismic velocity are recorded continuously at the assets; after an incident this baseline helps authorities separate natural damage from other causes.',
]

NEW = [
    '**A planning horizon that can be certified.** Beyond warnings, the project gives resilience planners the year at which no pumping and dewatering plan is any longer safe for water, port and energy together, at a stated confidence (Methodology, Section 7).',
    '**Single-hazard planning shown to overestimate the horizon.** In the preparatory synthetic test, plans that watch one hazard believed they had 43 to 97 years; the certified joint horizon was 38 years.',
    '**Monitoring priced in years of resilience.** Each sensor is valued by the years of safe operation it adds before the window closes (for example a sentinel piezometer about 22 years in the test), so equipment buys security time, not only data.',
    '**A worked example of AI testing, evaluation, verification and validation** for a civil-security warning, in the direction set by NATO\'s revised AI Strategy (2024) [S11], with each step tied to a deliverable.',
    '**Decisions, not only hazards.** For each decision-maker the section states the decision, its time scale, the input and the reliability attached to it.',
]

SOURCES = [
    ('S1', 'NATO (2009). Ceremony marks the accession of Albania and Croatia to NATO.', 'https://www.nato.int/cps/en/natohq/news_52902.htm'),
    ('S2', 'INSTAT, Institute of Statistics of Albania (2025). Maritime Transport Statistics, Q2 2025.', 'https://www.instat.gov.al/en/themes/industry-trade-and-services/transport-accidents-and-characteristics-of-road-vehicles/publikimet/2025/maritime-transport-statistics-q2-2025/'),
    ('S3', 'NATO. Resilience, civil preparedness and Article 3 (baseline requirements for national resilience).', 'https://www.nato.int/cps/en/natohq/topics_132722.htm'),
    ('S4', 'NATO (2024). Science for Peace and Security Programme: overview and Key Priorities.', 'https://www.nato.int/cps/en/natohq/85291.htm'),
    ('S5', 'NATO SPS (2026). Call for proposals 2027-1.', 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/SPS-Call4proposals-2027-1.pdf'),
    ('S6', 'NATO (2022). NATO 2022 Strategic Concept, adopted at the Madrid Summit, 29 June 2022.', 'https://www.act.nato.int/wp-content/uploads/2023/05/290622-strategic-concept.pdf'),
    ('S7', 'NATO (2021). NATO Climate Change and Security Action Plan.', 'https://www.nato.int/cps/en/natohq/official_texts_185174.htm'),
    ('S8', 'NATO Allied Command Transformation (2024). NATO Climate Change and Security Centre of Excellence.', 'https://www.act.nato.int/article/ccascoe-2024/'),
    ('S9', 'NATO (2021). Strengthened Resilience Commitment.', 'https://www.nato.int/cps/en/natohq/official_texts_185340.htm'),
    ('S10', 'NATO (2023). Vilnius Summit Communiqué, 11 July 2023 (Alliance Resilience Objectives).', None),
    ('S11', 'NATO (2024). Summary of NATO\'s revised Artificial Intelligence (AI) Strategy, 10 July 2024.', 'https://www.nato.int/en/about-us/official-texts-and-resources/official-texts/2024/07/10/summary-of-natos-revised-artificial-intelligence-ai-strategy'),
    ('S12', 'NATO Allied Maritime Command (2024). NATO officially launches new Maritime Centre for Security of Critical Undersea Infrastructure.', 'https://mc.nato.int/media-centre/news/2024/nato-officially-launches-new-nmcscui'),
    ('L1', 'Mavroulis, S., Lekkas, E. and Carydis, P. (2021). Liquefaction phenomena induced by the 26 November 2019, Mw = 6.4 Durrës (Albania) earthquake and liquefaction susceptibility assessment in the affected area. Geosciences 11(5), 215.', 'https://doi.org/10.3390/geosciences11050215'),
]


# ------------------------------------------------------------------------------------------------- figures
def fig_chain(path):
    """The assets of Durrës with the threats to each, the NATO resilience requirements they serve, and what CERTAIN-COAST
    adds."""
    W, H = 6.9, 4.45
    fig = plt.figure(figsize=(W, H), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    xa, aw, xc, cw = 0.08, 3.55, 4.55, 2.27

    def box(x, y, w, h, ec, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.07', fc=fc, ec=ec, lw=1.5))
    ax.text(xa + aw / 2, H - 0.16, 'Critical assets at Durrës and the threats to each', ha='center', va='center',
            fontsize=10.2, fontweight='bold', color=INK)
    ax.text(xc + cw / 2, H - 0.16, 'NATO resilience', ha='center', va='center', fontsize=10.2, fontweight='bold', color=INK)
    # shared drivers
    box(xa, H - 0.80, aw, 0.46, '#9aa3ad', '#f1f3f5')
    ax.text(xa + aw / 2, H - 0.57, 'Land subsidence and sea-level rise raise\nthe sea and the water table at all three',
            ha='center', va='center', fontsize=8.9, color=INK, style='italic', linespacing=1.15)
    assets = [('Wellfields: drinking water', 'seawater intrusion  ·  storm surge  ·  subsidence', C_W),
              ('Port of Durrës: 93.6% of seaborne freight', 'liquefaction  ·  storm surge  ·  subsidence', C_P),
              ('Energy landfall: supply from the sea', 'liquefaction  ·  shaking  ·  storm surge', C_E)]
    ah, gap, top = 0.70, 0.20, H - 0.98
    assert top - 3 * ah - 2 * gap >= 0.93
    ays = [top - ah - i * (ah + gap) for i in range(3)]
    for (t, thr, c), y in zip(assets, ays):
        box(xa, y, aw, ah, c, c + '16')
        ax.text(xa + 0.14, y + ah * 0.66, t, ha='left', va='center', fontsize=9.6, fontweight='bold', color=INK)
        ax.text(xa + 0.14, y + ah * 0.28, 'threats: ' + thr, ha='left', va='center', fontsize=8.9, color=INK)
    res = ['Resilient food and\nwater resources', 'Resilient civil\ntransportation systems', 'Resilient energy\nsupplies',
           'Civil support to\nthe military']
    rh = 0.50
    span_top, span_bot = ays[0] + ah, ays[2]
    rgap = (span_top - span_bot - 4 * rh) / 3
    rys = [span_top - rh - i * (rh + rgap) for i in range(4)]
    for t, y in zip(res, rys):
        box(xc, y, cw, rh, C_N, C_N + '14')
        ax.text(xc + cw / 2, y + rh / 2, t, ha='center', va='center', fontsize=9.0, color=INK, linespacing=1.12)
    am = [y + ah / 2 for y in ays]; rm = [y + rh / 2 for y in rys]
    # (asset, requirement, vertical offset at the asset end, at the requirement end)
    links = [(0, 0, 0.0, 0.0), (1, 1, 0.08, 0.0), (1, 3, -0.08, 0.08), (2, 2, 0.08, 0.0), (2, 3, -0.08, -0.08)]
    for j, k, da, dr in links:
        ax.add_patch(FancyArrowPatch((xa + aw, am[j] + da), (xc, rm[k] + dr), arrowstyle='-|>', mutation_scale=10,
                                     color=[C_W, C_P, C_E][j], lw=1.4, shrinkA=1, shrinkB=1))
    # CERTAIN-COAST band
    by, bh = 0.08, 0.66
    ax.add_patch(FancyBboxPatch((xa, by), xc + cw - xa, bh, boxstyle='round,pad=0,rounding_size=0.08', fc='#1F3864', ec='none'))
    ax.text(xa + 0.15, by + bh / 2, 'CERTAIN-COAST adds', ha='left', va='center', fontsize=10, fontweight='bold', color='white')
    ax.text(xa + 1.85, by + bh / 2,
            'one model for the three assets  ·  alarms with a certified, verified miss rate\n'
            'a certified safe operating window and the year it closes  ·  one post-event bulletin',
            ha='left', va='center', fontsize=9, color='white', linespacing=1.35)
    for dx in (-1.0, 0.0, 1.0):
        ax.add_patch(FancyArrowPatch((xa + aw / 2 + dx, by + bh + 0.02), (xa + aw / 2 + dx, ays[-1] - 0.02),
                                     arrowstyle='-|>', mutation_scale=9, color='#1F3864', lw=1.2))
    fig.savefig(path, dpi=300); plt.close(fig)


def fig_horizon(path, W):
    P = W['plans']
    rows = [('Joint, certified', P['joint']), ('Flooding only', P['flood_only']),
            ('Seawater intrusion only', P['swi_only']), ('Liquefaction only', P['liq_only'])]
    fig, ax = plt.subplots(figsize=(6.9, 2.55), dpi=300)
    for i, (lab, pl) in enumerate(rows):
        y = len(rows) - 1 - i
        b, u = pl['believed'], pl['unsafe_from']
        if i == 0:
            ax.barh(y, b, color='#2E8B57', height=0.56)
            ax.text(b + 2, y, f'{int(b + 0.5)} years', va='center', fontsize=9, color=INK, fontweight='bold')
            continue
        ax.barh(y, min(u, b), color='#c9d3dc', height=0.56)
        if b > u:
            ax.barh(y, b - u, left=u, color='white', edgecolor='#B03A3A', hatch='////', height=0.56, lw=0.8)
        ax.text(b + 2, y, f'believes {int(b + 0.5)}; unsafe after {int(u + 0.5)}', va='center', fontsize=8.8, color=INK)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=9)
    ax.set_xlim(0, 150); ax.set_xlabel('Years of operation the plan believes safe (synthetic transect, illustrative values)', fontsize=8.8)
    ax.tick_params(labelsize=8.8)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    ax.grid(axis='x', color='#e3e6ea', lw=0.7); ax.set_axisbelow(True)
    hs = [Patch(fc='#2E8B57', label='certified joint horizon'), Patch(fc='#c9d3dc', label='safe'),
          Patch(fc='white', ec='#B03A3A', hatch='////', label='believed safe, in fact not')]
    ax.legend(handles=hs, loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=8.6, frameon=False)
    fig.tight_layout(); fig.savefig(path, dpi=300); plt.close(fig)


# ------------------------------------------------------------------------------------------------- Word
def head_repeat(t):
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    return t


def bullets(doc, items, size=10.5):
    for x in items:
        q = para(doc, 3, 0.5); run(q, '• ', bold=True, size=size); rich(q, x, size=size)


def caption(doc, text, keep=False):
    p = para(doc, 6); p.paragraph_format.keep_with_next = keep
    run(p, text, italic=True, size=9.5, color='52606D')


def main(out):
    with open(os.path.join(HERE, 'method_window.json')) as fh:
        Wj = json.load(fh)
    work = tempfile.mkdtemp()
    f1, f2 = os.path.join(work, 'sec_chain.png'), os.path.join(work, 'sec_horizon.png')
    fig_chain(f1); fig_horizon(f2, Wj)

    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.6)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Security Relevance', bold=True, size=18, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, LEAD, size=10.5)
    BE.tiles(doc, TILES)

    heading(doc, '1. From coastal threat to Alliance resilience', 13.5, before=8)
    p = para(doc, 2, before=2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(f1, width=Cm(15.2))
    caption(doc, 'Figure 1. The threats to each asset at Durrës, the NATO resilience requirements the assets serve, and what '
                 'CERTAIN-COAST adds. Land subsidence and sea-level rise drive all three assets at once.')

    heading(doc, '2. Alignment with NATO priorities', 13.5, before=6)
    bullets(doc, PRIORITIES)

    heading(doc, '3. The baseline requirements served, and how it is shown', 13.5, before=8)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.keep_with_next = True
    rich(p, 'Allies committed at the 2016 Warsaw Summit to seven baseline requirements for civil preparedness, which serve '
            'continuity of government, essential services to the population and civil support to the military [S3]. '
            'CERTAIN-COAST contributes directly to three of them, and each contribution is checked by a deliverable (Table 1).',
         size=10.5)
    caption(doc, 'Table 1. Baseline requirements served by CERTAIN-COAST.', keep=True)
    t = head_repeat(table(doc, ['Baseline requirement', 'Asset', 'Threat', 'CERTAIN-COAST delivers', 'Shown by'], BASELINE,
                          [3.2, 2.4, 3.9, 4.6, 2.9], size=9.3))
    for r_ in t.rows[1:]:
        shade(r_.cells[0], 'E6F4EC')

    heading(doc, '4. Critical infrastructure where it comes ashore', 13.5, before=10)
    p = para(doc, 5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'NATO has given new attention to critical undersea infrastructure, including the NATO Maritime Centre for the Security '
            'of Critical Undersea Infrastructure launched at Allied Maritime Command in May 2024 [S12]. An energy landfall is where '
            'that infrastructure comes ashore, and it is exposed to threats that maritime surveillance does not cover: the ground '
            'beneath it can liquefy in an earthquake, subside year by year and be overtopped by extreme water levels. CERTAIN-COAST '
            'covers these natural threats at the landfall, complementing the protection of the subsea section.', size=10.5)

    heading(doc, '5. Security decisions the project supports', 13.5, before=8)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.keep_with_next = True
    rich(p, 'A warning matters for security only if someone acts on it. Table 2 names, for each decision-maker, the decision, its '
            'time scale, the input from CERTAIN-COAST and the reliability stated with it (miss rates αₖ, indicatively 5–10%, '
            'agreed with the operators in T3.1).', size=10.5)
    caption(doc, 'Table 2. Decisions, inputs and the reliability attached to them.', keep=True)
    t = head_repeat(table(doc, ['Decision-maker', 'Decision', 'Time scale', 'Input from CERTAIN-COAST', 'Stated reliability'], DECISIONS,
                          [3.1, 4.4, 2.1, 4.4, 3.0], size=9.3))
    for r_ in t.rows[1:]:
        shade(r_.cells[0], 'EAF0F8')

    heading(doc, '6. The planning horizon: how long the coast stays defensible', 13.5, before=10)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'Pumping moves the hazards in opposite directions: it draws seawater towards the wells and, below a limit, causes '
            'permanent subsidence, but it lowers the water table and so strengthens the ground against liquefaction. Sea-level '
            'rise and subsidence tighten all of them. CERTAIN-COAST therefore computes the **certified safe operating window**, the '
            'pumping and dewatering decisions that keep every hazard within its certified limit at once, and **the year in which '
            'it closes** (Methodology, Section 7). For a resilience planner this is the date from which no operating plan keeps '
            'water, port and energy safe together, and a new adaptation step is needed.', size=10.5)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.keep_with_next = True
    rich(p, f'In the preparatory synthetic test, with illustrative values rather than Durrës data, the certified window closed after '
            f'**{Wj["t_cert"]:.0f} years**. Plans that watch one hazard believed they had '
            f'{Wj["plans"]["swi_only"]["believed"]:.0f} to {Wj["plans"]["liq_only"]["believed"]:.0f} years (Figure 2): a '
            'flood-only plan misses the groundwater hazards, and managing one groundwater hazard alone pushes risk onto the other. '
            'The same analysis values each sensor by the years it adds before the window closes, so monitoring can be bought '
            'as security time.', size=10.5)
    p = para(doc, 2, before=2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(f2, width=Cm(15.4))
    caption(doc, 'Figure 2. Years of safe operation believed by plans that watch one hazard, against the certified joint '
                 'horizon; hatched: years believed safe that are not. Synthetic transect with illustrative values (Methodology, '
                 'Section 7.3).')

    heading(doc, '7. Responsible AI in a security decision chain', 13.5, before=8)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.keep_with_next = True
    rich(p, 'The warnings run on machine-learned surrogates of a physical model. NATO\'s revised AI Strategy (2024) reaffirms the '
            'six Principles of Responsible Use and calls for an Alliance-wide landscape for testing, evaluation, verification and '
            'validation of AI [S11]. CERTAIN-COAST is a worked example of all four steps for a civil-security warning (Table 3); '
            'the six principles are mapped one by one in the Ethics section.', size=10.5)
    caption(doc, 'Table 3. Testing, evaluation, verification and validation of the AI-assisted warnings.', keep=True)
    t = head_repeat(table(doc, ['Step', 'How CERTAIN-COAST does it'], TEVV, [3.0, 14.0], size=9.5))
    for r_ in t.rows[1:]:
        shade(r_.cells[0], 'EAF0F8')
    p = para(doc, 4, before=4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, '**Extremes are where security is decided.** Margins are extended beyond the observed record by extreme-value '
            'statistics and stress-tested on droughts, compound storms and earthquakes, and the guarantees hold separately in each '
            'regime, so the warning is not reliable only on average.', size=10.5)

    heading(doc, '8. Assets, hazards and security consequences', 13.5, before=8)
    caption(doc, 'Table 4. What is at stake at each asset and what CERTAIN-COAST contributes.', keep=True)
    t = head_repeat(table(doc, ['Asset', 'Hazards', 'Security consequence', 'CERTAIN-COAST contribution'], ASSETS,
                          [3.2, 4.2, 4.6, 5.0], size=9.5))
    for r_ in t.rows[1:]:
        shade(r_.cells[0], 'EAF0F8')

    heading(doc, '9. Protecting sensitive results', 13.5, before=10)
    bullets(doc, PROTECT)

    heading(doc, '10. Cooperation, capacity and transfer', 13.5, before=8)
    bullets(doc, COOP)

    heading(doc, '11. What is new in this section', 13.5, before=8)
    bullets(doc, NEW)

    heading(doc, 'Sources', 12, color='2E6DB4', before=8)
    for code, text, url in SOURCES:
        q = para(doc, 1); q.paragraph_format.left_indent = Cm(0.9); q.paragraph_format.first_line_indent = Cm(-0.9)
        run(q, f'[{code}]  ', bold=True, size=9, color='1F3864'); run(q, text + (' ' if url else ''), size=9, color='3A4450')
        if url:
            link(q, url, url.replace('https://', ''), 8.6)
    p = para(doc, 0, before=2)
    run(p, 'NATO texts checked by web search; confirm the wording of the SPS Key Priorities in the 2027-1 call text before submission.',
        italic=True, size=8.6, color='52606D')
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Security_Relevance.docx')
