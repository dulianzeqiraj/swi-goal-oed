"""CERTAIN-COAST (NATO SPS proposal): non-NATO funding contribution, a draft for tab 8 of the platform form ("Budget
summary by item - Non NATO funding contribution" and the text field "Non-NATO funding"). It gives the text to paste,
the eight-category table next to the SPS amounts of the budget, a personnel worksheet (person-months from the time
shares of the Project Participants table) and the rules of the MYP Handbook (version of April 2026) on salary
co-financing and management hours.

No amount is invented: salaries, overhead rates and the value of existing equipment come from the institutions and
stay as yellow placeholders. Only the SPS amounts (from build_budget) and the person-months are computed.

usage: python build_nonnato.py OUT.docx"""
import os
import sys
from collections import defaultdict

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import para, heading, table, link  # noqa: E402
import build_budget as BB  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')
MONTHS = 36
HANDBOOK = 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/2023/SPS_MYP_Handbook.pdf'
FORM = 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/2023/sps-myp-sample-application-form.pdf'

# time shares as in the Project Participants table of the form text (placeholders there, to be confirmed)
PEOPLE = [
    ('NATO-country Project Director', '[NPD institution]', 30),
    ('Partner-country Project Director, Prof. Jassim Al-Khayat', 'Environmental Science Center, Qatar University', 20),
    ('Senior researcher (hydrogeology and groundwater chemistry), Prof. Dr. Arjan Beqiraj', 'Faculty of Geology and Mining, UPT', 10),
    ('Researcher, Dr. Bardhosh Seitaj [time to confirm]', 'Faculty of Geology and Mining, UPT', 10),
    ('Researcher, Dr. Esmeralda Zeqo [time to confirm]', 'Faculty of Geology and Mining, UPT', 10),
    ('Laboratory technician, Sonata Pregja [time to confirm]', 'Faculty of Geology and Mining, UPT', 10),
    ('Researcher, Dr. Lusien Ismaili [time to confirm]', 'Ministry of Infrastructure and Energy', 5),
    ('Research Professor, Prof. Fares AlMomani', 'Environmental Science Center, Qatar University', 5),
    ('Research Associate Professor, Dr. Oguz Yigiterhan', 'Environmental Science Center, Qatar University', 5),
    ('Research Associate Professor, Dr. Bruno Welter Giraldes', 'Environmental Science Center, Qatar University', 5),
    ('End-user representative', '[Ministry of Defence of the Republic of Albania]', 5),
]

N_STAFF = 10  # the first rows of PEOPLE are staff of the institutions; the rest are end-users

# platform categories of the non-NATO table -> SPS categories of the budget
NN_CATS = [
    ('Equipment', ['Equipment'],
     'Existing equipment used by the project: field instruments, laboratory instruments and servers of the institutions; '
     "existing wells whose owners agree to their use; existing seismic stations. Value: [share of the "
     'replacement value or depreciation over the 36 months].'),
    ('Training', ['Training'],
     'Venues, rooms and trainers\' time of the institutions for the training school and the training of the end-user\'s staff; '
     'the trainees\' staff time is under "Other".'),
    ('Communication & Publication', ['Communication and Publications'],
     '[Institutional open-access agreements or press offices, if any; otherwise 0].'),
    ('Travel', ['Travel'], '[Institutional travel funds used for the project, if any; otherwise 0].'),
    ('Consumables', ['Consumables'],
     '[Laboratory chloride and major-ion analyses done by an institution laboratory at its own '
     'cost, if agreed; otherwise 0].'),
    ('Stipends', ['Stipends'], 'None expected (stipends of the early-career researchers are requested from SPS).'),
    ('Co-financing', ['Co-financing of personnel'],
     'Personnel cost paid by the institutions: all salaries of the Co-Directors and researchers for their time on the '
     'project (Section 3). SPS co-finances no salary in this version.'),
    ('Other', ['Other'],
     'Overheads of the institutions (offices, administration, IT) at their own rates; staff time of the end-user (the Ministry of Defence); '
     'data provided under agreements (Durrës tide-gauge record of ASIG, records of the national seismic stations, records '
     "of existing wells shared by their owners)."),
]

TEXT = (
    'The SPS grant pays only project-specific costs. The participating institutions and the end-users contribute the '
    'rest:\n'
    '• Salaries of the Co-Directors and researchers, paid by their institutions for about {pm_staff:.1f} person-months '
    'over {months} months (NPD {pm_npd:.1f}, PPD {pm_ppd:.1f}, hydrogeologist of the Faculty of Geology and Mining {pm_hyd:.1f}, '
    'two researchers and a laboratory technician of the Faculty {pm_fac:.1f}, researcher of the Ministry of Infrastructure and '
    'Energy {pm_mie:.1f}, three researchers of Qatar University {pm_qa:.1f}): '
    '[€ amount]. No salary co-financing is requested from SPS.\n'
    '• Overheads of the institutions (offices, laboratories, IT, administration) at their own rates: [€ amount].\n'
    '• Existing equipment and facilities used by the project: [field and laboratory instruments, servers] of the '
    'institutions: [€ amount].\n'
    "• The end-user, which receives no SPS funds: staff time of the Ministry of Defence for the steering committee, "
    'thresholds, the dry run, the live bulletins and training (about {pm_eu:.1f} person-months): '
    '[€ amount].\n'
    '• Data at no cost to the project: Copernicus Sentinel-1 radar images (free and open), the Durrës tide-gauge record '
    'of ASIG and the records of the national seismic stations under data agreements [not valued / € amount].\n'
    '• [Other national or institutional co-funding, only if confirmed: source and amount].\n'
    'Total non-NATO contribution: [€ amount], [x]% of the SPS grant (€{sps_total:,.0f}).')


def put(p, text, size=10.5, color=None, italic=False):
    from build_application import put as _put
    _put(p, text, size=size, color=color, italic=italic)


def sps_by_cat():
    import build_application as A
    tot = defaultdict(float)
    for r in BB.compute():
        tot[A.sps_cat(r)] += r['tot']
    return tot


def numbers():
    pm = [MONTHS * s / 100 for _, _, s in PEOPLE]
    staff = pm[:N_STAFF]
    return dict(months=MONTHS, pm_npd=pm[0], pm_ppd=pm[1], pm_hyd=pm[2], pm_fac=sum(pm[3:6]), pm_mie=pm[6],
                pm_qa=sum(pm[7:10]), pm_staff=sum(staff),
                pm_eu=sum(pm[N_STAFF:]),
                sps_total=sum(sps_by_cat().values()))


def text():
    return TEXT.format(**numbers())


def ph_table(t):
    from build_application import ph_cells
    ph_cells(t)
    return t


def main(out):
    from build_application import head_repeat
    n = numbers()
    sps = sps_by_cat()
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10.5)

    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    put(p, '**CERTAIN-COAST — Non-NATO funding contribution (draft)**', size=17, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    put(p, FULL, size=11, color='1F3864')
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    put(p, 'For tab 8 ("Project Schedule & Budget") of the SPS grant platform. The form asks: ')
    put(p, '"As NATO SPS grants do not cover the totality of the research, the project Co-Directors have to leverage other '
           'sources of funding. Please estimate the non-NATO funding contribution to the project. This amount should take '
           'into account expenses like: salaries, overheads and existing equipment, which are not covered with this NATO '
           'SPS grant."', italic=True)
    put(p, ' Amounts in yellow come from the institutions and end-users; nothing is estimated here that only they know.')
    p = para(doc, 6); put(p, 'Sources: ', size=9.5, color='52606D', italic=True)
    link(p, FORM, 'sample application form', size=9.5); put(p, '; ', size=9.5, color='52606D')
    link(p, HANDBOOK, 'SPS MYP Handbook (version of April 2026)', size=9.5); put(p, '.', size=9.5, color='52606D')

    heading(doc, '1. Text for the field "Non-NATO funding"', 13)
    for line in text().split('\n'):
        q = para(doc, 3, 0.3 if line.startswith('•') else 0); put(q, line)

    heading(doc, '2. Table "Budget summary by item - Non NATO funding contribution (in EUR)"', 13)
    rows = [[c, f'€{sum(sps[k] for k in ks):,.0f}', what, '[€ amount]'] for c, ks, what in NN_CATS]
    rows.append(['Total', f'€{n["sps_total"]:,.0f}', '', '[€ total]'])
    t = head_repeat(table(doc, ['Category', 'SPS request (budget)', 'What the non-NATO amount covers', 'Non-NATO (€)'],
                          rows, [3.0, 2.6, 9.0, 2.4], size=9))
    ph_table(t)
    q = para(doc, 4, before=3)
    put(q, 'The SPS column is the budget of this proposal (Budget document); the NPD\'s management hours (€15,000) are in '
           '"Other", as the Handbook requires. Enter the non-NATO column on the platform only; the Detailed Budget Excel '
           'workbook is filled by hand (the form warns that AI use on that file leads to rejection).', size=9,
        color='52606D', italic=True)

    heading(doc, '3. Personnel worksheet (salaries paid by the institutions)', 13)
    put(para(doc, 4), f'Person-months = time share × {MONTHS} months. The time shares are those of the Project Participants '
                      'table in the form text and must be confirmed. Contribution = person-months × monthly gross salary '
                      '(plus employer charges if the institution counts them).', size=10)
    prow = [[role, inst, f'[{sh}%]', f'{MONTHS * sh / 100:.1f}', '[€/month]', '[€ = PM × salary]'] for role, inst, sh in PEOPLE]
    prow.append(['Early-career researchers (4, to be recruited)', 'NPD and PPD institutions', '[50%]', '—', '—',
                 'Stipends from SPS; not a salary contribution'])
    prow.append(['Total', '', '', f'{n["pm_staff"] + n["pm_eu"]:.1f}', '', '[€ total]'])
    t = head_repeat(table(doc, ['Role', 'Institution', 'Time', 'Person-months', 'Monthly gross salary', 'Contribution'],
                          prow, [4.4, 3.6, 1.4, 2.0, 2.6, 3.0], size=9))
    ph_table(t)
    q = para(doc, 4, before=3)
    put(q, f'Staff of the Co-Directors\' institutions: {n["pm_staff"]:.1f} person-months; end-users: {n["pm_eu"]:.1f} '
           'person-months (count the end-users under "Other", since they are not Co-Director institutions).', size=9,
        color='52606D', italic=True)

    heading(doc, '4. Rules to respect (MYP Handbook, version of April 2026)', 13)
    rules = [
        '**SPS pays no salaries or overheads** as such; they are the core of the non-NATO contribution.',
        '**Salary co-financing is optional.** If used, the maximum per person and month is the share of time on the project, '
        'capped at 25%, times the monthly gross salary (for example 12% of time and €1,000 gross → €120 per month). The '
        'remaining cost is covered by self-funding, national or other sources; a reasonable total is up to one third of the '
        'grant; a CV is needed for each recipient; stipend recipients cannot also receive co-financing.',
        '**Management hours of the NPD** are eligible only under "Other" (NPD institution only, with time records and an '
        'official statement of the hours at payment), and all "Other" costs together may not exceed 15% of the budget: '
        f'here €{sps["Other"]:,.0f}, that is {100 * sps["Other"] / n["sps_total"]:.1f}%.',
        '**Consistency.** The SPS amounts in the platform tables must match the Detailed Budget Excel workbook (Summary '
        'tab), and the total requested must equal cell G15.',
    ]
    for r_ in rules:
        q = para(doc, 3, 0.3); put(q, '• ' + r_)

    heading(doc, '5. What each institution must send', 13)
    asks = [
        '**Co-Directors\' institutions:** monthly gross salary of each staff member in the worksheet, the overhead rate they '
        'use, and the existing equipment the project will use with its value or depreciation.',
        '**End-users:** confirmation of access, data and staff time (as in their commitment letters), and whether they want '
        'their in-kind contribution valued in euros.',
        '**Any co-funder:** only confirmed co-funding is entered; otherwise leave the line out.',
    ]
    for a in asks:
        q = para(doc, 3, 0.3); put(q, '• ' + a)
    doc.save(out)
    print('saved', out, '| person-months staff %.1f, end-users %.1f | SPS total %.0f | Other %.0f (%.1f%%)' % (
        n['pm_staff'], n['pm_eu'], n['sps_total'], sps['Other'], 100 * sps['Other'] / n['sps_total']))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Non-NATO_Contribution.docx')
