"""CERTAIN-COAST: the state-of-the-art methodology for the NATO SPS Multi-Year Project form, drawn from reviews I-IX
(GARANCIA-GO ... FSHEHTA-GO), the SHIU-GO and RINDERTIMI-GO notes and CERTAIN-COAST Methodology v3.

It answers three questions for the applicants:
1. what the 2027-1 call, the official sample application form and the MYP Handbook require (checked on nato.int,
   6 November 2026), and how long each part may be (word limits per field; there is no page limit for the proposal);
2. which points of the current form text (build_application.py) disagree with the 2027-1 call;
3. the methodology itself, as the texts of the fields that carry it (word limits checked), with a figure of the method
   chain and a table that ties each innovation to its tested evidence and to its task.

The texts are imported from build_application.py, where they are the answers of the form (since 6 November 2026), so the
two documents cannot diverge. They keep the work packages, task numbers, deliverables and milestones of the other
CERTAIN-COAST documents, so the Gantt chart and the deliverable list stay valid.

usage: python build_nato_method.py OUT.docx"""
import os
import re
import sys
import tempfile

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', '..', 'rindertimi_go'))
from build_sota import para, heading, table, shade, link  # noqa: E402
from build_application import (words, put, answer, head_repeat, ph_cells, NAVY, GREY, SHORT,  # noqa: E402
                               DELIVER, HOW, SOTA_TEXT, SOTA_REFS, STATUS, WORKPLAN)

LIMITS = {'What will the project deliver': (DELIVER, 500), 'How will the project reach the planned end state': (HOW, 500)}
REFS = SOTA_REFS
import build_budget as BB  # noqa: E402

CALL = 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/SPS-Call4proposals-2027-1.pdf'
FORM = 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/2023/sps-myp-sample-application-form.pdf'
HANDBOOK = 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/2023/SPS_MYP_Handbook.pdf'
MANAGING = ('https://www.nato.int/en/about-us/organization/nato-structure/science-for-peace-and-security-hub/'
            'managing-sps-grants')
PLATFORM = 'https://natosps.grantplatform.com/'

# ================================================================================================ what NATO requires
RULES = [
    ['Submission', 'Only through the SPS grant platform; full proposals by **15 November 2026, 23:59 CET**; data of '
                   'incomplete applications are lost after the deadline; SPS advises against last-minute submission.',
     'Call 2027-1, pp. 3 and 5'],
    ['State of the art', '"Applicants must map the state-of-the art and identify how their idea innovates on existing '
                         'academic and industrial efforts", "clearly mention how they differ from ongoing work by the '
                         'project team and others, using appropriate and recent literature references"; mapping the state '
                         'of the art "may not be the objective of a proposed activity, nor a significant component of its '
                         'implementation".', 'Call 2027-1, p. 4'],
    ['Technology readiness', '"Project results should aim to reach Technology Readiness Levels 3-6, improving on the state of '
                             'the art, including upon commercial off-the-shelf solutions."', 'Call 2027-1, p. 4'],
    ['Duration', 'Typically 24 to 36 months; shorter if justified; procurement time must be in the timeline.',
     'Call 2027-1, p. 4'],
    ['Budget', 'No hard limit; 36-month projects are typically about €400,000 (the form: €250,000–400,000); each '
               'Co-Director\'s institution gets a part; co-financing up to one third of the grant is reasonable.',
     'Call 2027-1, p. 5; form, p. 4'],
    ['Eligibility', 'A NATO-country Project Director resident and employed in a NATO country, a Partner-country Project '
                    'Director resident and employed in an eligible partner country, non-profit institutions, one proposal '
                    'per Co-Director per call, no other ongoing SPS grant as Co-Director.', 'Call 2027-1, pp. 2 and 5'],
    ['Supporting documents', 'Project schedule (Gantt), an end-user commitment letter for each end-user, a brief overview of '
                             'the institutions, and the NATO templates: Detailed Budget (Excel), Acceptance of Funds, '
                             'Agreement for Joint Research, IPR agreement or waiver (the IPR may follow approval).',
     'Call 2027-1, p. 4; Handbook, p. 5'],
    ['Evaluation', 'The SPS office and the Independent Scientific Evaluation Group (ISEG); proposals it recommends go to the '
                   'Partnerships and Cooperative Security Committee; a decision can take up to nine months; overlap and '
                   'duplication are evaluation criteria.', 'Call 2027-1, pp. 3–4; form, p. 4'],
    ['Reporting', 'A milestone after the first six months and at least one milestone, with a progress report, every 12 '
                  'months.', 'Handbook, p. 7'],
]

FIELDS = [
    ['Project title', 'about 100 characters', 'understandable to non-experts', '≤ 100 characters'],
    ['Project short title', '80 characters', 'same as cell E2 of the budget workbook', '—'],
    ['What security challenge(s) would your project address?', '500 words', 'a clear link to security', '450–500 words'],
    ['What technical challenge(s) would your project address, if any?', '500 words', 'well-defined technical challenges',
     '450–500 words'],
    ['What will the project deliver or develop by the end of the grant?', '500 words',
     '"how the proposed solution will advance the state-of-the-art"', f'**text 5.1** ({words(DELIVER)} words)'],
    ['How will the project reach the planned end state?', '500 words',
     '"methodology, approach, and how the different project teams will collaborate"', f'**text 5.2** ({words(HOW)} words)'],
    ['State-of-the-art: Related Projects / Duplication', 'none stated',
     'related or competing external efforts; own related activities; overlap; references', '**text 5.3**; 600–900 words '
                                                                                            'and references'],
    ['Project abstract', '200 words', 'comprehensible to the non-expert', '≤ 200 words'],
    ['Current status', 'none stated', 'participants\' research and starting point, with references',
     '**text 5.4**; 300–600 words'],
    ['Impact', '500 words', 'quantitative where possible', '450–500 words'],
    ['Work-plan', 'none stated', 'steps, sequencing, methods per step, risks, milestones', '**text 5.5**; '
                                                                                            '700–1,500 words'],
    ['Key Performance Indicators (KPIs)', '500 words', 'deliverables and milestones that show success', '≤ 500 words'],
    ['Criteria for success', 'about 7 at most; weights sum to 100%', 'SMART, quantitative, results not preconditions',
     '≤ 7'],
    ['Research focus and expertise of the NPD and of the PPD', '500 words each', '—', '300–500 words'],
    ['Brief overview of participating institutions (upload)', '**1 page per institution**', 'capabilities, resources, '
                                                                                             'facilities, websites',
     '1 page each'],
    ['Project schedule (upload)', 'none stated', 'Gantt: duration, dependencies, milestones, deliverables', '1–2 pages'],
    ['File that helps to illustrate the project (optional upload)', 'none stated', '—', '≤ 6 pages, with figures'],
]

FIXES = [
    '**Technology readiness: done.** The form text now selects "TRL 6: Technology demonstrated in relevant environment", '
    'its TRL description goes from TRL 3 to TRL 6 and the deliverables text says TRL 6, as the 2027-1 call asks ("aim to '
    'reach Technology Readiness Levels 3-6"); the Innovation and Conclusion documents were aligned (decision of 6 November '
    '2026).',
    '**One round, full proposal: done.** The form text said that Multi-Year Projects are evaluated in two phases. The 2027-1 '
    'call states: "Full proposals must be submitted 15 November 2026 (23:59 CET)". The note now says to fill every field.',
    '**Partner-country Project Director: still open.** Without a PPD resident and employed in an eligible partner country the '
    'application is not eligible (call, p. 2). Eligible partner countries include Bosnia and Herzegovina, Serbia, the '
    'Republic of Moldova, Georgia, Ukraine, Austria, Switzerland, Ireland, Malta, Israel, Jordan, Morocco, Tunisia and Egypt '
    '(full list in the call).',
    '**Budget: check in the workbook.** The CERTAIN-COAST budget totals €{total:,.0f}, within the typical range; the call '
    'asks that each Co-Director\'s institution be allocated a part of it, so the PPD\'s institution needs its own lines in '
    'the Excel workbook.',
]

# the innovations and where they enter CERTAIN-COAST
MAP = [
    ['SHIU-GO note: stochastic rain–recharge forcing learned from irregular, incomplete head records',
     'The rain enters as a stochastic system (soil water, vadose delay, recharge error), not a fixed transfer',
     'Forecast loss above the optimum 9%, against 80% (linear transfer) and 262% (Gaussian forcing); 90% intervals cover 88%',
     'WP2, T2.3'],
    ['RINDËRTIMI-GO note: all boundary conditions from rain with a function-space diffusion prior',
     'Sea level, inflow, recharge and initial head reconstructed jointly; heads enter through an ensemble update with the '
     'exact solver', 'Rain only: error 0.97–1.11 times the exact posterior; plain guidance missed the heads by 24.5 cm, the '
                     'update fits them to 2.1 cm', 'WP2, T2.3'],
    ['Review I, GARANCIA-GO', 'Guaranteed bands for boundaries never observed: calibration pairs simulated from the physical '
                              'prior', 'Raw ensemble misses 17–20% of the weeks (recharge coefficient 67%); calibrated '
                                       '9.5–10%, whole-function coverage 0.90', 'WP2, T2.3; WP3, T3.2'],
    ['Review II, MATJA-GO', 'The guaranteed value of a measurement: the band it removes, with the choice recalibrated',
     'Tide gauge: −15% promised by the ensemble, +16–21% guaranteed widening; sign predicted for 36/36 pairs',
     'WP4, T4.1'],
    ['Review III, RESHJA-GO', 'Rain-product errors inside the guarantees; a floor for the recharge coefficient that loggers '
                              'cannot remove', 'Naive κ band misses 70–76%; aware 9.3–10.3%; gauge and one logger 0.045 '
                                               'against product and eight loggers 0.108', 'WP2, T2.3; WP4, T4.1'],
    ['Review IV, ANKORA-GO', 'Guarantees that hold for any real law, calibrated on measured anchors',
     'Simulation calibration breaks under shift (0.11–0.83); 10–40 anchors stay ≤ 0.10; at least 9 anchors (22 for a 90% '
     'certificate)', 'WP3, T3.2 and T3.4'],
    ['Review V, PRIRJA-GO', 'Guarantees for a stated number of years ahead under drift', 'Risk 0.003–0.082 up to 20 years; '
                                                                                         'with 30 anchor years a band exists '
                                                                                         'only to 17 years', 'WP3, T3.2; '
                                                                                                             'WP5, T5.3'],
    ['Review VI, DYSHEMEJA-GO', 'The floor: no valid band can be narrower; computable before field data', '20-anchor band '
                                                                                                         '1.34–1.54 times '
                                                                                                         'the floor; four '
                                                                                                         'loggers remove '
                                                                                                         '82–94% of the '
                                                                                                         'rain-only floor',
     'WP3, T3.2; WP4, T4.1'],
    ['Review VII, SHKAKU-GO', 'Guaranteed counterfactual bands (what would have happened under another rain)',
     '40% drought lowers the head at the well by 1.94 m (floor half-width 0.088 m); the robust union is valid in every case '
     '(≤ 0.084)', 'WP5, T5.3'],
    ['Review VIII, KRIPA-GO', 'Counterfactual salinity on the calibrated Fushë-Kuqe chloride model; the share of the '
                              'dispersion', '40% less recharge: shallow area > 250 mg/L 31 → 65 km² (+33, band 15–49); '
                                            'dispersion width 62% of the variance; coverage 0.887–0.900', 'WP5, T5.3; '
                                                                                                         'WP2, T2.2'],
    ['Review IX, FSHEHTA-GO', 'Pumping effects with hidden confounders read from the heads; a calibrated physics check',
     'Bias of the summed well effects +0.59 unadjusted, +0.56 history substitute, 0.00 physics; check size 6%, power '
     '99–100%', 'WP5, T5.3; WP4, T4.1'],
    ['CERTAIN-COAST Methodology v3 (C1–C3)', 'Certified safe operating window; years of safe operation per sensor; safe '
                                            'pumping tests chosen for the years they add', 'Window closed after 38 years '
                                                                                           '(single-hazard plans: 43–97); '
                                                                                           'tests raised the closing year '
                                                                                           'from 10.8 to 31.9 (true 45)',
     'WP4, T4.1; WP5, T5.3'],
]


# ================================================================================================ figure
def fig_chain(path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from rgo_figs import Canvas, INK, MUTED
    BLUE, ORANGE, AQUA, VIOLET = '#2a78d6', '#eb6834', '#1baf7a', '#6250d6'
    cv = Canvas(170, 100)

    def box(x, y, w, h, title, lines, foot, ec, fc):
        cv.box(x, y, w, h, fc, ec, lw=1.1, r=1.8)
        cv.text(x + 2.2, y + h - 3.8, title, ha='left', size=9.0, weight='bold', color=INK)
        for k, ln in enumerate(lines):
            cv.text(x + 2.2, y + h - 8.9 - 4.4 * k, ln, ha='left', color=INK)
        cv.text(x + 2.2, y + 2.6, foot, ha='left', color=MUTED)

    def arr(x0, y0, x1, y1, c, ls='-'):
        cv.ax.annotate('', xy=(x1, y1), xytext=(x0, y0), zorder=25, arrowprops=dict(
            arrowstyle='-|>', color=c, lw=1.1, ls=ls, shrinkA=0, shrinkB=0, mutation_scale=8))
    # data
    cv.text(2, 97, 'Data', ha='left', size=9.4, weight='bold', color=MUTED)
    data = [(88, 'rain, local gauge'), (77, 'head, salinity loggers'), (66, 'InSAR, GNSS, tide gauge'),
            (55, 'seismic nodes, chloride'), (17, 'pumping logs and tests')]
    for y, d in data:
        cv.box(2, y - 4, 40, 8, '#eef0f2', '#5b6672', lw=0.9, r=1.6)
        cv.text(22, y, d)
    # the three pillars
    box(48, 66, 80, 28, '1  Guaranteed reconstruction (WP2, WP3)',
        ['inputs and boundaries from rain and heads', 'valid with a wrong simulator or rain product',
         'and under drift; a floor shows the limit'], 'reviews I, III–VI; SHIU-GO, RINDËRTIMI-GO', BLUE, '#e3eefb')
    box(48, 38, 80, 22, '2  Value of a measurement (WP4)',
        ['guaranteed band removed, years added', 'network chosen before it is bought'], 'review II; CERTAIN-COAST C2',
        AQUA, '#e2f5ee')
    box(48, 2, 80, 30, '3  Causal and counterfactual (WP5)',
        ['pumping effects without hidden confounding', 'salinity under a drier recharge regime',
         'safe operating window, safe pumping tests'], 'reviews VII–IX; CERTAIN-COAST C1, C3', VIOLET, '#efecfb')
    # outputs
    cv.text(134, 97, 'For the operators', ha='left', size=9.4, weight='bold', color=MUTED)
    outs = [(84, 'certified alarms', 'miss rate stated'), (60, '12 months of', 'live bulletins'),
            (36, 'pumping rule', 'with the utility'), (12, 'open software', 'and hand-over')]
    for y, a, b in outs:
        cv.box(134, y - 7, 34, 14, '#fde9df', ORANGE, lw=1.0, r=1.6)
        cv.text(151, y + 2.4, a); cv.text(151, y - 2.6, b, color=MUTED)
    # arrows
    for y, _ in data[:4]:
        arr(42, y, 48, 80 + (y - 71) * 0.35, '#5b6672')
    arr(42, 17, 48, 17, '#5b6672')
    arr(88, 66, 88, 60, BLUE)
    arr(88, 38, 88, 32, AQUA)
    arr(128, 84, 134, 84, BLUE)
    arr(128, 72, 134, 62, BLUE)
    arr(128, 26, 134, 58, VIOLET)
    arr(128, 20, 134, 36, VIOLET)
    cv.fig.savefig(path, dpi=300)
    plt.close(cv.fig)


# ================================================================================================ document
def bullet(doc, text, size=10.5):
    p = para(doc, 3, 0.4)
    put(p, '• ' + text, size=size)
    return p


def main(out):
    rows = BB.compute()
    total = sum(r['tot'] for r in rows)
    for k, (t, lim) in LIMITS.items():
        assert words(t) <= lim, f'{k}: {words(t)} > {lim}'
    work = tempfile.mkdtemp()
    fpath = os.path.join(work, 'chain.png')
    fig_chain(fpath)

    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.7)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10.5)

    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    put(p, f'{SHORT} — the state-of-the-art methodology for the NATO SPS form', size=17, color=NAVY); p.runs[0].bold = True
    p = para(doc, 3); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    put(p, 'What the 2027-1 call and the official form require, how long each part may be, and the methodology drawn from '
           'reviews I–IX as texts ready to paste', size=11, color=GREY)
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    put(p, 'Dulian Zeqiraj · 6 November 2026 · Multi-Year Project, call 2027-1 · deadline 15 November 2026, 23:59 CET',
        size=9.5, color=GREY, italic=True)

    # ---------------------------------------------------------------------------------------------- 1 short answer
    heading(doc, '1. The short answer', 14, before=2)
    t = doc.add_table(rows=1, cols=1); t.style = 'Table Grid'
    c = t.rows[0].cells[0]; shade(c, 'EEF4FB'); c.width = Cm(17.0)
    items = [
        '**There is no page limit for the proposal.** It is an online form on the SPS grant platform; each long field has a '
        'word limit, and only the overview of the institutions has a page limit (one page per institution).',
        '**The methodology goes into two fields:** "How will the project reach the planned end state?" (500 words: '
        'methodology, approach, collaboration) and "Work-plan" (no stated limit: steps, methods, risks, milestones).',
        '**The state of the art goes into three fields:** "What will the project deliver…" (500 words; it must show how the '
        'project advances the state of the art), "State-of-the-art: Related Projects / Duplication" (no stated limit) and '
        '"Current status" (no stated limit). The call requires recent literature references and forbids making the mapping '
        'of the state of the art an objective of the project.',
        '**Recommended lengths** for the fields without a limit (ours, not NATO\'s): state of the art 600–900 words with '
        'references, current status 300–600, work-plan 700–1,500; an optional illustrative upload of at most six pages.',
        f'**The five texts of Section 5 are now in the form text** (CERTAIN-COAST_NATO_Application_Form_Text.docx), '
        f'built from the nine reviews: deliverables ({words(DELIVER)} words), methodology ({words(HOW)} words), state of the '
        f'art with references, current status and work-plan.']
    for k, it in enumerate(items):
        q = c.paragraphs[0] if k == 0 else c.add_paragraph()
        q.paragraph_format.space_after = Pt(4)
        put(q, '• ' + it, size=10.5)
    para(doc, 4)

    # ---------------------------------------------------------------------------------------------- 2 NATO requires
    heading(doc, '2. What NATO requires', 14, before=6)
    p = para(doc, 4)
    put(p, 'Checked on 6 November 2026 in the documents that the call itself names: the call for proposals 2027-1 '
           '(September 2026), the sample application form for Multi-Year Projects listed on the "Managing SPS grants" page '
           '(the current template), and the MYP Handbook (applicable to applications submitted from November 2023).')
    p = para(doc, 4)
    for k, (lab, url) in enumerate((('Call 2027-1', CALL), ('Sample application form', FORM), ('MYP Handbook', HANDBOOK),
                                    ('Managing SPS grants', MANAGING), ('SPS grant platform', PLATFORM))):
        if k:
            put(p, '  ·  ', size=10)
        link(p, url, lab, size=10)
    head_repeat(table(doc, ['Requirement', 'What the official text says', 'Source'], RULES, [3.0, 11.0, 3.0], size=9))
    para(doc, 4)
    heading(doc, 'The fields that carry the methodology and the state of the art, with their limits', 12, color='2E6DB4',
            before=6)
    tt = head_repeat(table(doc, ['Field of the form', 'Official limit', 'What the form asks', 'Recommended'], FIELDS,
                           [5.6, 3.0, 5.0, 3.4], size=8.8))
    for ri in (5, 6, 7, 9, 11):
        for cc in tt.rows[ri].cells:
            shade(cc, 'F2F7EC')
    q = para(doc, 3, before=3)
    put(q, 'Shaded rows: the fields of Section 5. The limits are those of the sample form; the platform\'s live form '
           'decides if it differs [check each word counter on the platform].', size=9, color=GREY, italic=True)

    # ---------------------------------------------------------------------------------------------- 3 fixes
    heading(doc, '3. The form text against the 2027-1 call: what was aligned, what is open', 14, before=8)
    for f in FIXES:
        bullet(doc, f.format(total=total))

    # ---------------------------------------------------------------------------------------------- 4 the method
    heading(doc, '4. The methodology in one picture', 14, before=8)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    put(p, 'The nine reviews and the two notes add three pillars to the CERTAIN-COAST method. They keep its work packages, '
           'tasks, deliverables and gates, so the Gantt chart and the deliverable list stay valid: the new methods enter '
           'tasks T2.3, T3.2, T4.1 and T5.3.')
    p = para(doc, 2, before=4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(fpath, width=Cm(17.0))
    q = para(doc, 6)
    put(q, 'Figure 1. The method chain. (1) The inputs and boundaries that nobody measures are reconstructed from the rain '
           'and the heads with guarantees that survive a wrong simulator, a wrong rain product and drift. (2) Each sensor is '
           'valued by what it is guaranteed to buy before it is bought. (3) The decisions — what pumping does to the salt, '
           'what a drier climate would do, how long a safe operation lasts — are computed with the hidden confounding '
           'removed and with stated error.', size=9.5, italic=True)
    heading(doc, 'Where each innovation enters, and what was tested', 12, color='2E6DB4', before=6)
    head_repeat(table(doc, ['Innovation (source)', 'Step beyond the state of the art', 'Tested evidence (2026)', 'Task'],
                      MAP, [3.6, 5.2, 5.9, 2.3], size=8.6))
    q = para(doc, 3, before=3)
    put(q, 'The evidence comes from synthetic coastal test beds and, for review VIII, from the calibrated chloride model of '
           'Fushë-Kuqe with its documented facts; the code and results are in the repository (experiments/).', size=9,
        color=GREY, italic=True)

    # ---------------------------------------------------------------------------------------------- 5 texts
    heading(doc, '5. The texts, ready to paste', 14, before=8)
    p = para(doc, 4)
    put(p, 'These texts are now the answers of the same fields in CERTAIN-COAST_NATO_Application_Form_Text.docx (6 November '
           '2026); copy them from there. Yellow text is information only the applicants can give.')
    for num, name, text, lim in (('5.1', 'What will the project deliver or develop by the end of the grant?', DELIVER, 500),
                                 ('5.2', 'How will the project reach the planned end state?', HOW, 500),
                                 ('5.3', 'State-of-the-art: Related Projects / Duplication', SOTA_TEXT, None),
                                 ('5.4', 'Current status', STATUS, None),
                                 ('5.5', 'Work-plan', WORKPLAN, None)):
        heading(doc, f'{num}  {name}', 12, color='2E6DB4', before=8)
        answer(doc, text, lim)
        if lim is None:
            q = para(doc, 2); put(q, f'{words(text)} words (no limit stated)', size=8.8, color='1E8A5A', italic=True)

    # ---------------------------------------------------------------------------------------------- 6 references
    heading(doc, '6. References for the state-of-the-art field', 14, before=10)
    p = para(doc, 4)
    put(p, 'In the form text they follow text 5.3 in the same field (the form invites references). Most details come from '
           'the cards of reviews I–IX, which were checked through search results; check each one in a bibliographic database '
           'before submission.', size=10, color=GREY, italic=True)
    for txt, url in REFS:
        q = para(doc, 2, 0.4)
        put(q, txt + ' ', size=9.5)
        if url:
            link(q, url, url, size=9.5)
    doc.save(out)
    print('saved', out, '| words:', {k: words(t) for k, (t, _) in LIMITS.items()}, '| SOTA', words(SOTA_TEXT), '| STATUS',
          words(STATUS), '| WORKPLAN', words(WORKPLAN), '| budget', total)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Methodology_for_the_NATO_Form.docx')
