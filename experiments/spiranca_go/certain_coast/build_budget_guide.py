"""CERTAIN-COAST (NATO SPS proposal): guide for filling the "SPS MYP Detailed Budget" Excel workbook by hand.

The platform form warns that "using AI to fill out this budget file may corrupt the template, which will result in an
unreadable application and its automatic rejection". So the NATO workbook is not touched here. This guide gives, cell
by cell, what the applicants type into the unlocked input cells of its two tabs to fill (Info and Detail), taken from
the Budget document (build_budget.py): the budget lines are grouped into the rows the template offers for each
Co-Director and category, and split into the SPS reporting periods in whole euros (build_budget.director_lines, the same
split as the budget table of the application form). The cell map was read from the template of the "Managing SPS
grants" page of nato.int (2023 folder; sheets protected, input cells unlocked).

usage: python build_budget_guide.py OUT.docx"""
import os
import sys
from collections import defaultdict

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import para, heading, table, link  # noqa: E402
from build_application import put, ph_cells, head_repeat, sps_cat, TITLE, SHORT  # noqa: E402
import build_budget as BB  # noqa: E402

TEMPLATE = 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/2023/SPS_MYP_Detailed_Budget.xlsx'
FORM = 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/2023/sps-myp-sample-application-form.pdf'
MILESTONES = [('Milestone 1', 6, 'Initial progress report due (fixed in the template)'),
              ('Milestone 2', 18, 'Second technical and financial report'),
              ('Milestone 3', 30, 'Third technical and financial report'),
              ('Milestone 4', None, 'leave empty (optional)'),
              ('Final', 36, 'Final report due (computed from the duration)')]

# template rows of each block (NPD block starts at row 1, PPD block 53 rows lower); Communication & Publication has three
# fixed labels in column A, the other categories have free rows
CATS = [('Equipment', 8, 5), ('Training', 15, 2), ('Communication and Publications', 19, 3), ('Travel', 24, 2),
        ('Consumables', 28, 3), ('Other', 33, 6), ('Stipends', 41, 3), ('Co-financing of personnel', 46, 3)]
OFFSET = {'NPD': 0, 'PPD': 53}
COMM_LABELS = ['Books & Journals', 'Publication & IPR Protection', 'Communications & Publicity']

# grouping of the budget lines into template rows: (director, category) -> [(text for column A, item prefixes)]
GROUPS = {
    ('NPD', 'Equipment'): [
        ('Groundwater monitoring: boreholes, pressure/conductivity/temperature and barometric loggers, telemetry, spares',
         ['Monitoring boreholes', 'Pressure, conductivity', 'Barometric loggers', 'Telemetry units', 'Spare loggers']),
        ('Geodesy: GNSS stations and InSAR corner reflectors', ['GNSS stations', 'InSAR corner']),
        ('Seismic: stations, node rental (two campaigns), fibre-optic sensing campaign (conditional)',
         ['Seismic stations', 'Seismic node', 'Fibre-optic']),
        ('Field installation: power, enclosures and field chemistry instruments', ['Power and enclosures',
                                                                                    'Field chemistry']),
        ('Computing: GPU server, redundant data server and backup, software licences',
         ['Computing server', 'Redundant data server', 'Software licences'])],
    ('NPD', 'Training'): [
        ('Training school: venue, materials, trainee travel', ['Training school']),
        ('Training sessions for the end-user\'s staff and intended users', ['Training sessions for the end-user'])],
    ('NPD', 'Communication and Publications'): [
        ('Books & Journals', []), ('Publication & IPR Protection', ['Open-access']),
        ('Communications & Publicity', ['Website', 'Public and press'])],
    ('NPD', 'Travel'): [
        ('Consortium meetings and stakeholder workshops', ['Consortium meetings', 'Stakeholder workshops']),
        ('Conference presentations', ['Conference presentations'])],
    ('NPD', 'Consumables'): [
        ('Laboratory analyses: chloride and major ions', ['Laboratory analyses']),
        ('Sampling and field consumables', ['Sampling consumables', 'Field consumables']),
        ('Mobile data plans: 15 units over 36 months', ['Mobile data plans'])],
    ('NPD', 'Other'): [
        ('Shipping and customs for equipment', ['Shipping and customs']),
        ('Insurance of field equipment', ['Insurance of field equipment']),
        ('Open-source software: repository, testing, cloud computing, archiving', ['Open-source software']),
        ('Man-hours for the management of the project (NPD only, with time records)', ['Man-hours for the management'])],
    ('NPD', 'Stipends'): [('Stipends: {n} young researchers without a PhD, 30 months each', ['Stipends for young'])],
    ('PPD', 'Training'): [('Young-researcher exchanges, two months each', ['Young-researcher exchanges'])],
    ('PPD', 'Communication and Publications'): [
        ('Books & Journals', []), ('Publication & IPR Protection', ['Open-access']), ('Communications & Publicity', [])],
    ('PPD', 'Travel'): [('Consortium meetings', ['Consortium meetings']),
                        ('Conference presentations', ['Conference presentations'])],
    ('PPD', 'Stipends'): [('Stipends: {n} young researchers without a PhD, 30 months each', ['Stipends for young'])],
}
STIPEND_MONTH = 400   # rate used in the Budget document (2023 SPS presentation); confirm in the current Handbook


def blocks():
    """(director, category) -> list of (row, text, [M1, M2, M3, M4, Final], total); checks that every line is used once
    and that no category needs more rows than the template offers."""
    lines = BB.director_lines()
    used = [0] * len(lines)
    out = {}
    for d in ('NPD', 'PPD'):
        for cat, row0, nrows in CATS:
            groups = GROUPS.get((d, cat), [])
            assert len(groups) <= nrows, (d, cat, len(groups), nrows)
            rows = []
            for k, (text, prefixes) in enumerate(groups):
                per = [0, 0, 0, 0]
                for i, ln in enumerate(lines):
                    if ln['rec'] == d and sps_cat(ln) == cat and any(ln['item'].startswith(p) for p in prefixes):
                        used[i] += 1
                        per = [a + b for a, b in zip(per, ln['per'])]
                if '{n}' in text:
                    text = text.format(n=round(sum(per) / STIPEND_MONTH / 30))
                if cat == 'Communication and Publications':
                    assert text == COMM_LABELS[k]
                rows.append((row0 + OFFSET[d] + k, text, [per[0], per[1], per[2], None, per[3]], sum(per)))
            out[(d, cat)] = rows
    missing = [lines[i]['item'] for i, u in enumerate(used) if u != 1]
    assert not missing, missing
    return out


def fmt(v):
    return '' if v in (None, 0) else f'{v:,.0f}'.replace(',', '')


def main(out):
    B = blocks()
    tot_dir = {d: sum(r[3] for (dd, _), rows in B.items() if dd == d for r in rows) for d in ('NPD', 'PPD')}
    cat_tot = defaultdict(lambda: [0] * 5)
    for (_, cat), rows in B.items():
        for r in rows:
            for i, v in enumerate(r[2]):
                cat_tot[cat][i] += v or 0
    grand = sum(tot_dir.values())

    doc = Document()
    s = doc.sections[0]
    s.orientation = WD_ORIENT.LANDSCAPE
    s.page_width, s.page_height = Cm(29.7), Cm(21.0)
    s.left_margin = s.right_margin = Cm(1.6); s.top_margin = s.bottom_margin = Cm(1.4)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)

    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    put(p, '**CERTAIN-COAST — how to fill the SPS MYP Detailed Budget workbook (by hand)**', size=15, color='1F3864')
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    put(p, f'{TITLE} · total requested €{grand:,.0f} · NPD €{tot_dir["NPD"]:,.0f} · PPD €{tot_dir["PPD"]:,.0f}', size=10,
        color='52606D')
    p = para(doc, 4)
    put(p, '**Why by hand.** The platform form says: ')
    put(p, '"Please note that using AI to fill out this budget file may corrupt the template, which will result in an '
           'unreadable application and its automatic rejection."', italic=True)
    put(p, ' So the NATO workbook is not filled here. Download it, open it in Excel and type the values below into the '
           'input cells; the other cells are protected and calculate by themselves.')
    rules = [
        '**Only two tabs:** Info first, then Detail. The Summary tab fills in by itself; do not delete formulas or rows.',
        '**Numbers:** type whole euros without "€", spaces or separators (e.g. 30400). Leave a cell empty for zero.',
        '**Milestone 4** is optional and not used: leave column E of the Detail tab and cell C11 of the Info tab empty.',
        '**Row texts:** the descriptions in column A may be shortened; the amounts must stay as given, because they '
        'match the application form and the Budget document.',
        '**After typing**, check the totals in Section 4 before uploading the file on the platform (tab 8).',
    ]
    for r_ in rules:
        q = para(doc, 2, 0.3); put(q, '• ' + r_)
    q = para(doc, 4, before=2); put(q, 'Template: ', size=9, color='52606D', italic=True)
    link(q, TEMPLATE, 'SPS_MYP_Detailed_Budget.xlsx (nato.int, "Managing SPS grants")', size=9)
    put(q, '; instructions: ', size=9, color='52606D', italic=True); link(q, FORM, 'sample application form, tab 8', size=9)

    heading(doc, '1. Info tab', 12.5, before=6)
    info = [['A2', 'SPS Ref. No.', 'leave empty (assigned by SPS)'],
            ['C2', 'Approved Budget', 'leave empty (set after approval; the requested total is computed in Summary G15)'],
            ['D2', 'Project Title', TITLE],
            ['E2', 'Short Title (max. 80 characters)', f'{SHORT}  (must equal the "Project short title" of the platform form)'],
            ['B5', 'Project Duration (months)', '36'],
            ['C5', 'Start Date (Kickoff)', 'leave empty: the template says "Do not fill in Start Date at the time of application"'],
            ['C9 / D9', 'Milestone 2: months / description', '18 / Second technical and financial report'],
            ['C10 / D10', 'Milestone 3: months / description', '30 / Third technical and financial report'],
            ['C11 / D11', 'Milestone 4: months / description', 'leave empty (optional)'],
            ['B15 / C15 / D15 / E15', 'NPD: first / last name / institution / country',
             'Dulian / Zeqiraj / Polytechnic University of Tirana / Albania (choose from the list)'],
            ['B16 / C16 / D16 / E16', 'PPD: first / last name / institution / country',
             'Jassim / Al-Khayat / Qatar University / Qatar (choose from the list)']]
    t = head_repeat(table(doc, ['Cell', 'Field', 'Type'], info, [4.0, 7.0, 15.4], size=9))
    ph_cells(t)
    q = para(doc, 3, before=2)
    put(q, 'Milestone 1 (month 6) and the final report (month 36) are already in the template. Columns F (NATO/Partner) '
           'and the dates in column E fill in by themselves.', size=9, color='52606D', italic=True)

    for d, label in (('NPD', 'NATO-country Project Director (rows 1–52)'),
                     ('PPD', 'Partner-country Project Director (rows 54–105)')):
        heading(doc, f'{2 if d == "NPD" else 3}. Detail tab, block of the {label}', 12.5, before=8)
        rows = []
        for cat, _, _ in CATS:
            for row, text, per, tot in B[(d, cat)]:
                if tot == 0 and cat != 'Communication and Publications':
                    continue
                fixed = cat == 'Communication and Publications'
                rows.append([f'{row}', cat, ('(label already there) ' if fixed else '') + text] +
                            [fmt(v) for v in per] + [fmt(tot) or '0'])
            if not B[(d, cat)]:
                rows.append(['—', cat, 'nothing to enter', '', '', '', '', '', ''])
        rows.append(['', '', f'Grand total of this block (cell F{52 + OFFSET[d]})', '', '', '', '', '',
                     f'{tot_dir[d]:,.0f}'.replace(',', '')])
        head_repeat(table(doc, ['Row', 'Category', 'Column A: description',
                                'B: M1', 'C: M2', 'D: M3', 'E: M4', 'F: Final', 'Total'],
                          rows, [1.1, 3.6, 10.8, 1.8, 1.8, 1.8, 1.3, 1.8, 2.0], size=8.6))

    heading(doc, '4. Checks after typing', 12.5, before=8)
    chk = [['Detail F52', 'NPD grand total', f'{tot_dir["NPD"]:,.0f}'],
           ['Detail F105', 'PPD grand total', f'{tot_dir["PPD"]:,.0f}'],
           ['Summary G15', 'Total requested: must equal "Funding requested from NATO SPS" in the platform form',
            f'{grand:,.0f}']]
    head_repeat(table(doc, ['Cell', 'What', 'Must show (€)'], chk, [3.2, 17.0, 6.2], size=9))
    q = para(doc, 3, before=4)
    put(q, 'Summary tab by category and milestone (also the "Budget summary by item" table of the platform form):',
        size=9.5)
    rows = [[c] + [fmt(v) or '0' for v in cat_tot[c][:3]] + ['—'] + [fmt(cat_tot[c][4]) or '0',
                                                                         fmt(sum(cat_tot[c])) or '0']
            for c, _, _ in CATS]
    rows.append(['Total'] + [fmt(sum(cat_tot[c][i] for c, _, _ in CATS)) for i in range(3)] + ['—'] +
                [fmt(sum(cat_tot[c][4] for c, _, _ in CATS)), fmt(grand)])
    head_repeat(table(doc, ['Category', 'M1', 'M2', 'M3', 'M4', 'Final', 'Total'], rows,
                      [7.4, 3.2, 3.2, 3.2, 2.2, 3.2, 3.6], size=9))
    q = para(doc, 3, before=4)
    put(q, 'Reporting periods: M1 covers months 0–6, M2 months 6–18, M3 months 18–30, Final months 30–36; spending is '
           'spread evenly within each project year of the Budget document. The "Other" category, including the NPD\'s '
           f'management hours, is {100 * sum(cat_tot["Other"]) / grand:.1f}% of the total (ceiling 15%).', size=9,
        color='52606D', italic=True)
    doc.save(out)
    print('saved', out, '| NPD', tot_dir['NPD'], 'PPD', tot_dir['PPD'], 'total', grand,
          '| rows NPD', sum(len(v) for (d, _), v in B.items() if d == 'NPD'),
          'PPD', sum(len(v) for (d, _), v in B.items() if d == 'PPD'))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Budget_Workbook_Guide.docx')
