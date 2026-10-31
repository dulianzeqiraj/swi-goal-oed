"""CERTAIN-COAST (NATO SPS proposal): Sustainability. End state at Month 36, what remains and who owns it, a staged
hand-over (figure), indicative running cost after the project and who pays, institutional and human capacity,
environmental sustainability and policy alignment (SDGs, Sendai Framework, Early Warnings for All), threats and
safeguards, indicators, what is new, and a short version (at most 500 words) for the application form question on the
project's end state. Consistent with the Work Plan, Expected Results, Risk Assessment, Budget, Dissemination Plan and
Partnership.

usage: python build_sustainability.py OUT.docx"""
import os
import sys
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyBboxPatch
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, heading, rich, table, shade, link  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')

LEAD = ('CERTAIN-COAST is designed to end with a working service, not a report. At Month 36 the operators of the wellfields, '
        'the port and the energy landfall run the warning system themselves, on a network they own, with open software, '
        'trained staff and procedures they have adopted, and civil protection uses its bulletins after events. The running '
        'cost is small and known in advance, because the system uses free satellite data, existing stations and open '
        'software. The guarantees keep holding after the project team leaves, because the alarms recalibrate themselves '
        'from every logged outcome.')

END_STATE = [
    '**A service in operation.** In the last three months (Months 34–36) every bulletin is issued by operator staff, with the project team only observing (MS7).',
    '**Owned infrastructure.** The monitoring network, the servers and the software are handed over to the operators under a written agreement.',
    '**Adopted procedures.** At least one operating procedure per asset is adopted, and civil protection has a post-event protocol (D6.2).',
    '**Trained people.** At least 20 operator and civil-protection staff and at least 6 early-career researchers can run and develop the system.',
    '**Agreed running cost.** The three operators have signed an agreement on maintenance and running costs (by Month 33).',
    '**A method others use.** The open software, the coast kit and the twin-coast transfer test let other coasts repeat the analysis.',
]

REMAINS = [
    ['Monitoring network (wells, loggers, GNSS, seismic stations, reflectors)', 'Operators, by asset', 'Operators\' technicians; university support for GNSS and seismic stations', 'Hand-over agreement (Month 36); maintenance agreement (Month 33)'],
    ['Warning software, surrogate and alarms', 'Open source; operators run their instance', 'University maintains the repository; users report issues', 'Open licence, tests and containers (D6.1)'],
    ['Calibrated coupled model', 'University and operators', 'University updates it every year with new data', 'Model and data release (D6.1)'],
    ['Data and bulletin log', 'Operators (restricted); open aggregated statistics', 'Operators; university for analysis', 'Data plan (T7.2); two-tier dissemination'],
    ['Procedures and post-event protocol', 'Operators; civil protection', 'Reviewed every year by operators and civil protection', 'D6.2 adopted by each operator'],
    ['Trained people and training material', 'Operators; university', 'Refresher course every year; manuals in Albanian and English', 'T6.1, T6.2; coast kit'],
]

COSTS = [
    ['Mobile data for telemetry (15 units)', '900', 'Operators, shared'],
    ['Laboratory analyses (about 60 samples per year)', '2 400', 'Water utility'],
    ['Batteries, consumables, minor repairs', '1 500', 'Operators, shared'],
    ['Sensor replacement fund (loggers renewed about every 6 years)', '2 400', 'Operators, shared'],
    ['Upkeep of GNSS and seismic stations', '1 500', 'University or research partner'],
    ['Server hosting, backup and security updates', '1 200', 'University (in kind) or operators'],
    ['Insurance of field equipment', '1 000', 'Operators'],
]

FUNDING = [
    '**Operators\' own budgets.** The running cost is shared by three operators, of the order of €3,000–4,000 each per year, and is written into the maintenance agreement.',
    '**National sources.** The policy brief (D6.2) asks the national authorities to include coastal monitoring at critical infrastructure in their programmes.',
    '**Follow-up research funding.** At least one follow-up proposal (for example to Horizon Europe or the Interreg IPA ADRION programme for the Adriatic-Ionian region) is submitted by Month 36 to extend the method to other coasts.',
    '**Free data.** Copernicus Sentinel-1 radar images remain free, so the most expensive observation of land motion costs nothing to continue.',
]

CAPACITY = [
    '**Several people per role.** At least two trained people per operator, so the service survives staff turnover (R18).',
    '**Train the trainer.** Senior operator staff are trained to train new staff; the university gives a refresher course every year.',
    '**Manuals in Albanian and English.** Every procedure, the software and the training material are documented in both languages.',
    '**Embedded in institutions.** Procedures are part of each operator\'s own operating rules and of the civil-protection protocol, not of the project.',
    '**A research line that continues.** The early-career researchers continue the work in theses and follow-up projects, keeping the scientific team in place.',
]

ENV = [
    '**Groundwater used within reversible limits.** The joint pumping rule keeps heads above the preconsolidation head, so pumping causes no new permanent subsidence and the aquifer is used within the range in which it recovers (Methodology, Eq. 25).',
    '**Freshwater protected before it is lost.** The certified intrusion alarm acts before wells turn saline, which takes years to reverse.',
    '**Low-footprint equipment.** Field stations run on solar power; satellite data replace much field surveying.',
]

POLICY = [
    ['UN Sustainable Development Goals', 'Target 6.4 (sustainable withdrawals of freshwater); 9.1 (resilient infrastructure); 11.5 (fewer losses from disasters); 13.1 (resilience to climate-related hazards)'],
    ['Sendai Framework for Disaster Risk Reduction 2015–2030', 'Target G: more multi-hazard early warning systems and risk information available to people'],
    ['UN Early Warnings for All', 'Everyone protected by early warning systems by 2027'],
    ['NATO resilience', 'Water, energy and transport among the baseline requirements for national resilience (Security Relevance)'],
]

THREATS = [
    ['Trained staff leave (R18)', 'Two or more trained people per operator; train-the-trainer; yearly refresher; manuals'],
    ['No money for running costs', 'Small, known cost shared by three operators; agreement signed by Month 33; follow-up funding'],
    ['Software no longer maintained', 'Open repository with tests and containers; university as maintainer; users on the twin coast'],
    ['Equipment fails or is damaged (R11, R21)', 'Spares; replacement fund; the D4.1 ranking shows which sensors to replace first'],
    ['Guarantees drift as conditions change (R8)', 'Margins keep updating from logged outcomes; the bulletin log shows any drift; yearly review'],
    ['Over-reliance on the bulletins (R16)', 'Procedures keep the operators\' own checks; training on what a miss rate means'],
    ['Institutional change at an operator', 'Agreements signed at institution level; policy brief to national authorities; civil-protection protocol'],
]

KPIS = [
    ['Bulletins issued by operator staff in Months 34–36', '100%, project team only observing', 'Month 36'],
    ['Maintenance and running-cost agreement', 'Signed by the three operators', 'Month 33'],
    ['Hand-over agreement for network, servers and software', 'Signed', 'Month 36'],
    ['Operating procedures adopted', 'At least 1 per asset', 'Month 36'],
    ['Trained people', 'At least 20 operator staff; at least 6 early-career researchers', 'Month 36'],
    ['Follow-up funding application', 'At least 1 submitted', 'Month 36'],
    ['Network data availability after hand-over', 'At least 90%', 'One year after the project'],
    ['Observed miss rates after hand-over', 'Within targets, from the operators\' bulletin log', 'One year after the project'],
]

NEW = [
    '**A guarantee that maintains itself.** The online conformal term updates the margins from every logged outcome, without the developers and without assuming that conditions stay the same, so the certified miss rate keeps holding after the project.',
    '**A system that warns about itself.** The bulletin log compares observed miss rates with their targets; if a guarantee starts to drift, the operators see it and trigger recalibration before trust is lost.',
    '**Better with use.** Every year of data narrows the forecasts and shrinks the margins, so the service gives fewer false alarms the longer it runs.',
    '**Environmental limits as hard constraints.** The pumping rule never lets heads fall below the preconsolidation head, so the aquifer is used within the range in which it recovers.',
    '**A hand-over that is measured.** Operators issue every bulletin in the last three months, so sustainability is demonstrated before the project ends, not assumed after it.',
]

SHORT = ('At the end of CERTAIN-COAST, the operators of the Durrës wellfields, port and energy landfall run a certified early '
         'warning service themselves, and civil protection uses its bulletins after earthquakes and storms. Sustainability '
         'is built in from the start rather than added at the end.\n\n'
         'Ownership. The monitoring network, servers and software are handed over to the operators under a written agreement '
         'at Month 36. The operators set the alarm thresholds in the first year and adopt operating procedures by the end, so '
         'the system is theirs from the start. In the last three months every bulletin is issued by operator staff, with the '
         'project team only observing: the hand-over is demonstrated before the project ends.\n\n'
         'Low and known running cost. The system uses free Copernicus Sentinel-1 data, existing seismic stations, solar-powered '
         'field stations and open-source software. The running cost is about €11,000 per year, shared by three operators under a '
         'maintenance agreement signed by Month 33, with the university supporting the geodetic and seismic stations and the '
         'software.\n\n'
         'People. At least 20 operator and civil-protection staff and at least 6 early-career researchers are trained, with at '
         'least two trained people per operator, a train-the-trainer scheme, a yearly refresher course and manuals in Albanian '
         'and English.\n\n'
         'Guarantees that last. The alarm margins recalibrate themselves from every logged outcome, without assuming that '
         'conditions stay the same, so the certified miss rates keep holding after the developers leave. The bulletin log shows '
         'the operators at once if a guarantee starts to drift, and every year of data makes the forecasts sharper and the false '
         'alarms fewer.\n\n'
         'Environment and policy. The joint pumping rule keeps groundwater heads above the level at which permanent subsidence '
         'begins, so the aquifer is used within the range in which it recovers. The project contributes to the Sendai Framework '
         'target on multi-hazard early warning, to the UN Early Warnings for All initiative and to NATO\'s baseline requirements '
         'for resilient water, energy and transport.\n\n'
         'Beyond Durrës. The open software, a coast kit and a transfer test on a partner-country coast let other subsiding coasts '
         'in the Adriatic and beyond repeat the analysis, and at least one follow-up proposal is submitted by Month 36.')

SOURCES = [
    ('UN Sustainable Development Goals', 'https://sdgs.un.org/goals'),
    ('Sendai Framework for Disaster Risk Reduction 2015–2030', 'https://www.undrr.org/publication/sendai-framework-disaster-risk-reduction-2015-2030'),
    ('UN Early Warnings for All', 'https://www.un.org/en/climatechange/early-warnings-for-all'),
    ('SPS Multi-Year Project sample application form', 'https://nato.int/content/dam/nato/webready/documents/sps/grants/2023/sps-myp-sample-application-form.pdf'),
]

STAGES = [
    ('Co-design', 'M1–M12', 'Design the\nnetwork; install;\nagree data', 'Set thresholds;\ngive access\nand records'),
    ('Build and\ntest', 'M13–M22', 'Model,\nsurrogate, alarms;\ndry run', 'Join the\ndry run; review\nbulletins'),
    ('Operate\ntogether', 'M23–M33', 'Run the system;\ntrain staff', 'Receive\nbulletins; learn\nto issue them'),
    ('Operators\nlead', 'M34–M36', 'Observe\nand fix', 'Issue every\nbulletin; adopt\nprocedures'),
    ('After the\nproject', 'M37 onward', 'Maintain\nsoftware; yearly\nrefresher', 'Own and run\nthe service; pay\nrunning cost'),
]


def fig_handover(path):
    W, H = 6.7, 3.75
    fig = plt.figure(figsize=(W, H), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    x0, lab_w = 0.05, 0.40
    n = len(STAGES); cw = (W - x0 - lab_w - 0.05) / n
    proj, oper = '#6a4fb3', '#1e8a5a'
    # colour shifts from project (purple) to operators (green) as ownership moves
    mix = lambda a, b, t: '#%02x%02x%02x' % tuple(int(int(a[i:i + 2], 16) * (1 - t) + int(b[i:i + 2], 16) * t) for i in (1, 3, 5))
    yt, ch = H - 0.06, 0.92
    for i, (name, months, p, o) in enumerate(STAGES):
        xl = x0 + lab_w + i * cw
        pts = [(xl, yt), (xl + cw - 0.13, yt), (xl + cw, yt - ch / 2), (xl + cw - 0.13, yt - ch), (xl, yt - ch),
               (xl + (0.13 if i else 0), yt - ch / 2)]
        ax.add_patch(Polygon(pts, closed=True, fc=mix(proj, oper, i / (n - 1)), ec='white', lw=2))
        cx = xl + cw / 2 + (0.05 if i else 0)
        ax.text(cx, yt - 0.33, name, fontsize=9.6, fontweight='bold', color='white', ha='center', va='center', linespacing=1.05)
        ax.text(cx, yt - 0.74, months, fontsize=8.6, color='white', ha='center', va='center')
        for j, (txt, col) in enumerate(((p, proj), (o, oper))):
            yb = 1.40 - j * 1.32
            ax.add_patch(FancyBboxPatch((xl + 0.04, yb), cw - 0.08, 1.20, boxstyle='round,pad=0,rounding_size=0.06',
                                        fc=col + ('1f' if (j == 0) == (i < 3) else '0d'), ec=col, lw=1.0))
            ax.text(xl + cw / 2, yb + 0.60, txt, fontsize=8.8, color='#1f2328', ha='center', va='center', linespacing=1.25)
    ax.text(x0 + 0.17, 2.00, 'Project team', fontsize=10, fontweight='bold', color=proj, ha='center', va='center', rotation=90)
    ax.text(x0 + 0.17, 0.68, 'Operators', fontsize=10, fontweight='bold', color=oper, ha='center', va='center', rotation=90)
    fig.savefig(path, dpi=300)
    plt.close(fig)


def tidy(t, total=False):
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    keep = t.rows[:-1] if len(t.rows) <= 9 else (t.rows[0], t.rows[-2])
    for row in keep:
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.keep_with_next = True
    if total:
        for c in t.rows[-1].cells:
            shade(c, 'E8EDF5')
            for p in c.paragraphs:
                for r in p.runs:
                    r.bold = True
    return t


def bullets(doc, items, size=11):
    for t in items:
        p = para(doc, 3, 0.5); run(p, '• ', bold=True, size=size); rich(p, t, size=size)


def main(out):
    work = tempfile.mkdtemp(); fig = os.path.join(work, 'fig_handover.png'); fig_handover(fig)
    total_cost = sum(int(c[1].replace(' ', '')) for c in COSTS)
    n_short = len(SHORT.split())
    assert n_short <= 500, n_short
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Sustainability', bold=True, size=18, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; rich(p, LEAD, size=11.5)

    heading(doc, '1. The end state at Month 36', 13.5, before=4)
    bullets(doc, END_STATE)

    heading(doc, '2. What remains, who owns it and how it is kept', 13.5, before=8)
    tidy(table(doc, ['What remains', 'Owner', 'Kept up by', 'Secured by'], REMAINS, [4.6, 3.6, 4.6, 4.2], size=9.5))
    para(doc, 4)

    heading(doc, '3. A staged hand-over', 13.5, before=8)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'Responsibility moves from the project team to the operators in five stages, so that the operators are already '
            'running the service before the project ends (Figure 1).')
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(fig, width=Cm(17.0))
    p = para(doc, 6); run(p, 'Figure 1. Staged hand-over from the project team to the operators. The colour shifts as ownership moves.',
                          italic=True, size=10, color='52606D')

    heading(doc, '4. Running cost after the project', 13.5, before=8)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, f'The cash cost of keeping the service running is indicatively **€{total_cost:,} per year**'.replace(',', ' ')
            + ', excluding staff time, which the operators and the university provide in kind (about one third of a technician '
              'at the operators and analyst support at the university).')
    rows = COSTS + [['Total per year', f'{total_cost:,}'.replace(',', ' '), '']]
    tidy(table(doc, ['Item', '€ per year', 'Paid by'], rows, [9.2, 2.6, 5.2], size=10), True)
    p = para(doc, 4, before=6); run(p, 'How it is paid', bold=True, size=11, color='1F3864')
    bullets(doc, FUNDING)

    heading(doc, '5. People and institutions', 13.5, before=8)
    bullets(doc, CAPACITY)

    heading(doc, '6. Environmental sustainability and policy alignment', 13.5, before=8)
    bullets(doc, ENV)
    para(doc, 3)
    tidy(table(doc, ['Framework', 'Contribution of CERTAIN-COAST'], POLICY, [5.4, 11.6], size=10))
    para(doc, 4)

    heading(doc, '7. Threats to sustainability and safeguards', 13.5, before=8)
    tidy(table(doc, ['Threat', 'Safeguard'], THREATS, [5.4, 11.6], size=10))
    para(doc, 4)

    heading(doc, '8. Sustainability indicators', 13.5, before=8)
    tidy(table(doc, ['Indicator', 'Target', 'When'], KPIS, [7.0, 6.2, 3.8], size=10))
    para(doc, 4)

    heading(doc, '9. What is new in this sustainability plan', 13.5, before=8)
    bullets(doc, NEW)

    h = heading(doc, f'10. Short version for the application form ({n_short} words)', 13.5, before=0)
    h.paragraph_format.page_break_before = True
    p = para(doc, 6); run(p, 'For the question on how the project reaches its end state (500 words maximum in the sample form).',
                          italic=True, size=10, color='52606D')
    for chunk in SHORT.split('\n\n'):
        p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        head, _, rest = chunk.partition('. ') if chunk.split('. ')[0] in ('Ownership', 'Low and known running cost', 'People',
                                                                          'Guarantees that last', 'Environment and policy',
                                                                          'Beyond Durrës') else ('', '', chunk)
        if head:
            run(p, head + '. ', bold=True); run(p, rest)
        else:
            run(p, chunk)
    p = para(doc, 2, before=8); run(p, 'Sources: ', bold=True, size=9.5, color='52606D')
    for i, (t, u) in enumerate(SOURCES):
        link(p, u, t, 9.5)
        if i < len(SOURCES) - 1:
            run(p, '; ', size=9.5, color='52606D')
    doc.save(out)
    print('saved', out, '| running cost', total_cost, '| short version', n_short, 'words')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Sustainability.docx')
