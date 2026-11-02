"""CERTAIN-COAST (NATO SPS proposal): content for the "SPS MYP Agreement for Joint Research".

The agreement itself is a NATO Word template, downloaded from the SPS grant platform or the "Managing SPS grants" page,
and signed by all Co-Directors and a representative of each institution. This file does not replace it. Part A gives
what to enter in the template; Part B gives optional principles of joint research that the two institutions can sign
for themselves (the consortium agreement foreseen in the Partnership section). Roles, budget split, reporting months,
data and publication rules are read from or kept consistent with the other CERTAIN-COAST builders.

usage: python build_agreement.py OUT.docx"""
import os
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import shade  # noqa: E402
from build_institutions import run, ph, para, cell_text, widths  # noqa: E402
import build_budget as B  # noqa: E402
import build_workplan as W  # noqa: E402

NAVY = '1F3864'
TITLE = 'Certified early warning to protect water, port and energy infrastructure on a sinking Adriatic coast'
# what the partner-country team does in each work package (the NATO-country team leads all but WP6)
PARTNER = {'WP1': '—', 'WP2': 'Its early-career researchers join on exchange', 'WP3': '—', 'WP4': '—',
           'WP5': 'User-side review of the bulletins', 'WP6': 'Leads: transfer study on its own coast, exchanges, '
           'regional workshop, review of the procedures', 'WP7': 'Steering committee; input to the SPS reports'}


def split():
    tot = npd = ppd = 0
    for cat, item, q, u, wps, ys, rec, just in B.LINES:
        t = q * u; tot += t
        a, b = {'NPD': (t, 0), 'PPD': (0, t), 'Both': (t / 2, t / 2)}[rec]
        npd += a; ppd += b
    return tot, npd, ppd


def head(doc, text, size=12, before=8):
    p = para(doc, 3, before=before); run(p, text, bold=True, size=size, color=NAVY)
    p.paragraph_format.keep_with_next = True


def grid(doc, rows, ws, size=9.5, header=None):
    t = doc.add_table(rows=0, cols=len(ws)); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    if header:
        cells = t.add_row().cells
        for c, h in zip(cells, header):
            cell_text(c, h, size=size, bold=True, color='FFFFFF'); shade(c, NAVY)
    for r in rows:
        cells = t.add_row().cells
        for j, (c, v) in enumerate(zip(cells, r)):
            cell_text(c, v, size=size, bold=(j == 0 and not header))
            if j == 0 and not header:
                shade(c, 'EEF2F8')
    widths(t, ws)
    return t


def clauses(doc, items, size=10):
    for k, (title, text) in enumerate(items, start=1):
        p = para(doc, 3, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        run(p, f'{k}. {title}. ', bold=True, size=size); ph(p, text, size=size)


def main(out):
    tot, npd, ppd = split()
    wpname = {w[0]: w[1] for w in W.WPS}
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = Cm(1.6); s.bottom_margin = Cm(1.5)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)

    p = para(doc, 2); run(p, 'CERTAIN-COAST — Agreement for Joint Research', bold=True, size=17, color=NAVY)
    p = para(doc, 8); run(p, 'Content for the NATO template "SPS MYP Agreement for Joint Research" and optional principles '
                             'of joint research', size=10.5, color='374151')

    head(doc, 'How to use this file', before=0)
    for t in [
        '**The official NATO template is already filled in:** CERTAIN-COAST_SPS_MYP_Agreement_for_Joint_Research.docx '
        '(project line, names, institutions and signature lines; the template has no other fields). That file is the one '
        'signed and uploaded; this file is not uploaded.',
        '**Part A** gives what to type into the template. **Part B** is optional: principles the two institutions can sign '
        'between themselves now, so that the consortium agreement foreseen before the start is already agreed. If the '
        'template has a free-text field on the division of work, copy the table of Part A there.',
        '**Signatures:** every Co-Director and a representative of each institution (for UPT, [the Rector or a person '
        'authorised by the Rector]). Collect them on one copy or on copies scanned into a single PDF; upload it as '
        '"SPS MYP Agreement for Joint Research". Ask the legal or project office of each institution to read Part B '
        'before signing it.',
        '**Yellow** marks what only the applicants can fill in.',
    ]:
        q = para(doc, 3, indent=0.45, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
        run(q, '•  ', bold=True, color=NAVY); ph(q, t, size=10)

    head(doc, 'Part A. What to enter in the NATO template', size=13.5, before=10)
    grid(doc, [
        ['Project title', TITLE],
        ['Short title', 'CERTAIN-COAST'],
        ['Programme and call', 'NATO Science for Peace and Security Programme, Multi-Year Project, call 2027-1'],
        ['Duration', '36 months from the SPS kick-off meeting; SPS reporting milestones at Months 6, 18, 30 and the final '
                     'report at Month 36'],
        ['NATO funding requested', f'€{tot:,.0f} in total: NATO-country institution €{npd:,.0f} ({100 * npd / tot:.0f}%), '
                                   f'partner-country institution €{ppd:,.0f} ({100 * ppd / tot:.0f}%) in the current plan '
                                   '[update if the split changes]'],
        ['NATO-country Project Director (NPD)', '[Name, title, position], Faculty of Geology and Mining, Polytechnic '
                                                'University of Tirana, Albania'],
        ['NPD institution and representative', 'Polytechnic University of Tirana, Sheshi "Nënë Tereza" Nr. 4, 1001 '
                                               'Tirana, Albania; [name and position of the authorised representative]'],
        ['Partner-country Project Director (PPD)', '[Name, title, position], [institution], [country]'],
        ['PPD institution and representative', '[Institution, postal address]; [name and position of the authorised '
                                               'representative]'],
        ['Other Co-Directors', 'None [or name, institution and representative of each additional Co-Director]'],
    ], [5.2, 11.8])

    p = para(doc, 3, before=8); run(p, 'Division of work', bold=True, size=10.5, color=NAVY)
    rows = [[wp, wpname[wp], 'PPD team' if wp == 'WP6' else 'NPD team', PARTNER[wp]] for wp in sorted(PARTNER)]
    grid(doc, rows, [1.3, 6.6, 2.4, 6.7], size=9.3, header=['WP', 'Work package', 'Lead', 'Partner-country team'])
    p = para(doc, 3, before=4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    ph(p, 'The NPD coordinates the project, is accountable to the SPS Programme for the funds and submits the reports. '
          'The model, the surrogate and the certified-alarm algorithm are built and run by the NATO-country team. The PPD '
          'leads the partner-country team and manages the partner-country share of the budget. The end-users '
          '(water utility, port, energy landfall operator, civil protection) contribute in kind and are not parties to '
          'this agreement.', size=10)

    h = para(doc, 3, before=0); h.paragraph_format.page_break_before = True
    run(h, 'Part B. Principles of joint research (optional, signed by the two institutions)', bold=True, size=13.5, color=NAVY)
    p = para(doc, 5, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    ph(p, 'Between the **Polytechnic University of Tirana**, represented by [name, position] (the NATO-country '
          'institution), and [partner-country institution], represented by [name, position] (the partner-country '
          'institution), together "the parties", for the project CERTAIN-COAST submitted to the NATO Science for Peace '
          'and Security Programme. These principles apply together with the grant terms of the SPS Programme and the SPS '
          'MYP Handbook; where they differ, the SPS terms prevail.', size=10)
    clauses(doc, [
        ('Purpose', 'The parties carry out CERTAIN-COAST jointly, as described in the application, with the division of '
                    'work in Part A.'),
        ('Coordination', 'The NPD coordinates the project and is the contact of the SPS Programme. A steering committee of '
                         'the Project Directors and one representative of each end-user meets every six months and at '
                         'each milestone; decisions are taken by consensus where possible, otherwise by the Project '
                         'Directors, with the NPD accountable for the funds.'),
        ('Funds', 'Each party manages its share of the budget under its own financial rules and the SPS rules, keeps the '
                  'records and receipts, and spends only on the items approved by the SPS Programme. Changes between '
                  'budget categories follow the SPS rules.'),
        ('Reporting', 'Each party sends its technical and financial input for the SPS reports at Months 6, 18 and 30 and '
                      'for the final report at Month 36 within [two weeks] of the NPD\'s request.'),
        ('Data', 'Data of the water utility, the port and the energy landfall operator are used only for the project, '
                 'under the data access agreements (T7.2) and the data management plan. Open data are released under '
                 'CC BY 4.0 and metadata under CC0; restricted data stay restricted.'),
        ('Publications', 'Results are published open access. Authorship follows contribution, and early-career '
                         'researchers are authors of the work they do. A party informs the other [30] days before '
                         'submitting a publication; an operator reviews any manuscript that uses its data within an '
                         'agreed period (indicatively 30 days) and may remove sensitive content but not block the '
                         'publication. Every output acknowledges the support of the NATO Science for Peace and Security '
                         'Programme.'),
        ('Misses are published', 'The parties publish the verification ledger of the certified warnings, misses '
                                 'included, every quarter during live operation, and report failed tests and limitations, '
                                 'not only successes.'),
        ('Intellectual property', 'Knowledge each party brings remains its own. Results belong to the party that '
                                  'produces them, and jointly to the parties that produce them together, in shares that '
                                  'reflect their contributions. Software is released under the Apache-2.0 licence. The '
                                  'parties conclude the SPS Intellectual Property Rights agreement or waiver when the SPS '
                                  'Programme asks for it.'),
        ('Confidentiality', 'Each party keeps confidential the restricted data and any information the other marks as '
                            'confidential, during the project and for [three] years after it.'),
        ('Equipment', 'Equipment bought with the grant is used for the project and its ownership and use after the '
                      'project follow the SPS rules and the sustainability plan.'),
        ('Changes and withdrawal', 'Changes to roles or budget are agreed in writing and notified to the SPS Programme. '
                                   'A party that cannot continue informs the other at once, and both work with the SPS '
                                   'Programme to complete or reassign its tasks.'),
        ('Duration and language', 'These principles apply from signature until the SPS Programme accepts the final '
                                  'report; the confidentiality and publication clauses continue afterwards. They are '
                                  'written in English; disagreements are settled amicably between the parties.'),
    ])

    p = para(doc, 3, before=8); run(p, 'Signatures', bold=True, size=10.5, color=NAVY)
    sig = doc.add_table(rows=1, cols=2); sig.style = 'Table Grid'; sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c, (who, inst) in zip(sig.rows[0].cells, [
            ('NATO-country Project Director', 'Polytechnic University of Tirana'),
            ('Partner-country Project Director', '[Partner-country institution]')]):
        cell_text(c, who, size=9.5, bold=True)
        for line in ['Name: [ ]', 'Date: [ ]', 'Signature:', '', f'For {inst}:', 'Name and position: [ ]', 'Date: [ ]',
                     'Signature and stamp:', '']:
            q = c.add_paragraph(); q.paragraph_format.space_after = Pt(2); ph(q, line, size=9.5)
    widths(sig, [8.5, 8.5])
    doc.save(out)
    print('saved', out, '| total', tot, 'NPD', npd, 'PPD', ppd)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Agreement_for_Joint_Research_Content.docx')
