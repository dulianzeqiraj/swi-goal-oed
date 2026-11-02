"""CERTAIN-COAST (NATO SPS proposal): two-page brief for a candidate partner-country institution, attached to the
invitation e-mails. What the project is, why it fits the call, what is new, the role and budget offered to the
partner, the eligibility rules for the partner-country Project Director, and what is needed by when.
The partner's budget share is computed from build_budget.LINES; roles from the Partnership section.

usage: python build_partner_brief.py OUT.pdf"""
import os
import subprocess
import sys
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, rich, table, shade  # noqa: E402
import build_budget as B  # noqa: E402

TITLE = 'Certified early warning to protect water, port and energy infrastructure on a sinking Adriatic coast'


def partner_lines():
    out, tot, ppd = [], 0, 0
    for cat, item, q, u, wps, ys, rec, just in B.LINES:
        t = q * u; tot += t
        s = {'PPD': t, 'Both': t / 2, 'NPD': 0}[rec]
        if s:
            ppd += s; out.append([item, f'€{s:,.0f}', 'partner' if rec == 'PPD' else 'shared equally'])
    return out, tot, ppd


def bullets(doc, items, size=9.8):
    for t in items:
        p = para(doc, 1.5, 0.45); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(-0.35)
        run(p, '•  ', bold=True, size=size, color='1F3864'); rich(p, t, size=size)


def head(doc, text, before=6):
    p = para(doc, 2, before=before); run(p, text, bold=True, size=11.5, color='1F3864')
    p.paragraph_format.keep_with_next = True


def build_docx(path):
    lines, tot, ppd = partner_lines()
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(1.9); s.top_margin = Cm(1.4); s.bottom_margin = Cm(1.3)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10)

    p = para(doc, 1); run(p, 'CERTAIN-COAST — brief for a partner-country team', bold=True, size=16, color='1F3864')
    p = para(doc, 2); run(p, TITLE, bold=True, size=10.5, color='374151')
    p = para(doc, 6)
    run(p, 'NATO Science for Peace and Security (SPS) Programme · Multi-Year Project · call 2027-1 · submission by '
           '15 November 2026, 23:59 CET · coordinated by the Faculty of Geology and Mining, Polytechnic University of '
           'Tirana, Albania', size=9.3, color='52606D')

    head(doc, 'The project in brief', before=0)
    p = para(doc, 3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'Near Durrës, the main port of Albania, the wellfields that supply drinking water, the port and an energy '
            'landfall stand on soft ground that is slowly sinking, close to active faults (the Mw 6.4 earthquake of 26 '
            'November 2019 struck there). Three hazards threaten them together: seawater entering the wells, liquefaction '
            'in an earthquake, and coastal flooding in storms. Sinking land and rising seas worsen all three. CERTAIN-COAST '
            'builds one model of the three hazards, a fast machine-learned copy of it whose error is bounded for every '
            'forecast, and warnings that state in advance how often they may miss a dangerous event. The warnings run live '
            'for twelve months with the water utility, the port, the energy operator and civil protection, and are then '
            'handed over to them. **36 months; about €382,500 requested from NATO.**', size=9.8)

    head(doc, 'Why it fits the call')
    p = para(doc, 3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'The 2027-1 call names among its topics of particular interest "protection of critical infrastructure, supplies '
            'and personnel; maritime and undersea infrastructure resilience". CERTAIN-COAST protects the water, port and '
            'energy infrastructure of a NATO Ally, and the method transfers to other subsiding coasts of Allies and '
            'partners, which is where the partner country comes in.', size=9.8)

    head(doc, 'What is new')
    bullets(doc, [
        '**Warnings with a stated miss rate**, verified during live operation with a test that stays valid however often '
        'the record is checked.',
        '**A certified safe operating window**: the pumping and dewatering decisions that keep all three hazards within '
        'limits at once, and the sea level or year at which this window closes. In our literature search we found no '
        'published method for this.',
        '**The value of a sensor in years of safe operation**, used to choose the monitoring network.',
    ])

    head(doc, 'The role we propose for the partner-country team')
    t = table(doc, ['Work package', 'What the partner team leads'], [
        ['WP2 Coupled model and certified surrogate', 'Coupled model of intrusion, compaction, liquefaction and sea level; calibration; a neural-operator or kernel surrogate with an error bound on every forecast'],
        ['WP3 Certified multi-hazard alarm', 'Alarm margins and their proofs; a joint guarantee over the three alarms; back-testing on the record and on storylines beyond it'],
        ['WP6 Training, transfer and dissemination', 'Training of early-career researchers; test of the method on a subsiding coast of the partner country; open software and data'],
    ], [5.2, 12.0], size=9.2)
    for r_ in t.rows[1:]:
        shade(r_.cells[0], 'EEF2F8')
    p = para(doc, 2, before=3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rich(p, 'The NATO-country team (Albania) leads coastal motion, the monitoring network, live operation and management '
            '(WP1, WP4, WP5, WP7). Joint papers, co-supervision of early-career researchers and shared open software are '
            'planned throughout.', size=9.8)

    head(doc, f'Budget for the partner institution in the current plan: €{ppd:,.0f} ({100 * ppd / tot:.0f}% of the total)')
    t = table(doc, ['Item', 'Partner share', 'Basis'], lines, [11.0, 2.8, 3.4], size=9.0)
    p = para(doc, 2, before=3)
    rich(p, 'The share can be raised, for example by placing more stipends or the transfer study at the partner '
            'institution; we will agree the final figures together before submission.', size=9.3)

    head(doc, 'Who can be the partner-country Project Director')
    bullets(doc, [
        'Employed and resident in an eligible partner country of the SPS Programme, at a university, public research '
        'institute or other non-profit institution (companies cannot be co-directors).',
        'Holds no other SPS grant at the time (one SPS grant per person).',
        'Gives about 30% of working time to the project; co-signs the SPS Agreement for Joint Research with a '
        'representative of the institution.',
    ])

    head(doc, 'What we need, and by when')
    t = table(doc, ['By', 'What'], [
        ['Thursday 5 November', 'A reply: interest in principle, the name of the proposed Project Director and institution'],
        ['Monday 9 November', 'Details for the application form: nationality, position and institution address, employment '
                              'history and education, recent publications, research focus (up to 500 words), other '
                              'grants; a one-page overview of the institution (capabilities, resources, facilities, websites)'],
        ['Thursday 12 November', 'The signed SPS MYP Agreement for Joint Research (NATO template, which we send)'],
        ['Sunday 15 November', 'Submission by the NATO-country Project Director'],
    ], [4.1, 13.1], size=9.2)
    for r_ in t.rows[1:]:
        shade(r_.cells[0], 'EEF2F8')
    p = para(doc, 2, before=4)
    rich(p, 'The full proposal text is shared as soon as you confirm interest. Contact: Dulian Zeqiraj, Faculty of '
            'Geology and Mining, Polytechnic University of Tirana (please reply to the e-mail that brought this brief).', size=9.3)
    doc.save(path)


def main(out):
    work = tempfile.mkdtemp()
    d = os.path.join(work, 'CERTAIN-COAST_Partner_Brief.docx'); build_docx(d)
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', work, d], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.replace(d.replace('.docx', '.pdf'), out)
    lines, tot, ppd = partner_lines()
    print('saved', out, '| partner share', ppd, f'{100 * ppd / tot:.1f}%')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Partner_Brief.pdf')
