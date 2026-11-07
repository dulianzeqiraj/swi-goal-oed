"""CERTAIN-COAST (NATO SPS proposal): five-page concept note in English, for end-users and partners, built from the
texts of the application form (build_application.py), the work plan (build_workplan.py) and the budget (build_budget.py),
so it cannot drift from them. Text only, in a standard PDF font, so the file stays small enough to attach to e-mails.

usage: python build_concept_note.py OUT.pdf"""
import os
import re
import sys
from collections import defaultdict

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_application as A  # noqa: E402
import build_budget as BB  # noqa: E402
import build_workplan as W  # noqa: E402

NAVY, GREY, LINE = HexColor('#1F3864'), HexColor('#52606D'), HexColor('#C9CED6')
SUBS = {'≤': 'at most ', '≥': 'at least ', '→': 'to', '−': '-', 'α_k': 'alpha', 'α': 'alpha', 'Δ': 'Delta', '★': '*',
        'η': 'eta', ' ': ' ', ' ': ' ', '·': '-'}
END_USERS = [
    ('Water utility: Shoqëria Rajonale Ujësjellës Kanalizime Durrës sh.a.',
     'Access to production and monitoring wells for the loggers; records of heads, chloride and pumping under a data '
     'agreement; support for a yearly campaign of paired chloride samples; staff time for the chloride threshold, the '
     'pumping rule and safe pumping tests.',
     'Certified intrusion warnings (also for crossings between samples), a joint pumping rule, the certified safe '
     'operating window, the monitoring network and trained staff.'),
    ('Water resources agency: Agjencia e Menaxhimit të Burimeve Ujore (AMBU)',
     'Access to monitoring wells under its control (existing wells only); records of levels, chemistry and abstraction '
     'under a data agreement; staff time for the warning threshold and the pumping and drought rule.',
     'A monitoring design for its decisions, level and salinity sensors, a chloride early warning for each supply well, '
     'a pumping and drought rule, open software and training; no procurement, ownership or maintenance obligations.'),
    ('Port: Autoriteti Portual Durrës',
     'Access to agreed locations for sensors under its security rules; geotechnical records and quay design levels '
     'under a data agreement; staff time for the thresholds and the post-event protocol.',
     'Liquefaction and extreme-water-level warnings for the port, post-event reports and trained staff.'),
    ('Energy landfall operator',
     'Access to agreed locations near the landfall under its security rules; design levels and geotechnical data; '
     'staff time for the thresholds.',
     'Stability bulletins combining shaking, liquefaction, water level and subsidence.'),
    ('Civil protection: Agjencia Kombëtare e Mbrojtjes Civile',
     'A seat on the steering committee; the triggers of the post-event protocol and its co-design.',
     'One picture of water, port and energy after earthquakes or storms; post-event reports and procedures.'),
]


def clean(text):
    for k, v in SUBS.items():
        text = text.replace(k, v)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text.encode('cp1252')            # standard PDF fonts: every character must exist in WinAnsi
    return text


def styles():
    return dict(
        title=ParagraphStyle('t', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=NAVY, alignment=1),
        sub=ParagraphStyle('s', fontName='Helvetica', fontSize=10.5, leading=13.5, textColor=NAVY, alignment=1,
                           spaceAfter=3),
        meta=ParagraphStyle('m', fontName='Helvetica-Oblique', fontSize=8.6, leading=11, textColor=GREY, alignment=1,
                            spaceAfter=8),
        h=ParagraphStyle('h', fontName='Helvetica-Bold', fontSize=11.2, leading=14, textColor=NAVY, spaceBefore=7,
                         spaceAfter=3),
        p=ParagraphStyle('p', fontName='Helvetica', fontSize=10.4, leading=13.6, spaceAfter=4),
        b=ParagraphStyle('b', fontName='Helvetica', fontSize=10.4, leading=13.6, spaceAfter=2.5, leftIndent=10,
                         bulletIndent=1),
        cell=ParagraphStyle('c', fontName='Helvetica', fontSize=8.3, leading=10.2),
        cellb=ParagraphStyle('cb', fontName='Helvetica-Bold', fontSize=8.3, leading=10.2, textColor=HexColor('#FFFFFF')),
        note=ParagraphStyle('n', fontName='Helvetica-Oblique', fontSize=8.2, leading=10.4, textColor=GREY, spaceAfter=4),
    )


def text_blocks(S, text):
    """A form text with '\n' paragraphs; lines starting with a number, '•' or 'N.' become bullets."""
    out = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^(•|\d+\.)\s*(.*)$', line)
        if m:
            out.append(Paragraph(clean(m.group(2)), S['b'], bulletText='•' if m.group(1) == '•' else m.group(1)))
        else:
            out.append(Paragraph(clean(line), S['p']))
    return out


def grid(S, header, rows, widths):
    data = [[Paragraph(clean(h), S['cellb']) for h in header]] + \
           [[Paragraph(clean(str(c)), S['cell']) for c in r] for r in rows]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), NAVY), ('GRID', (0, 0), (-1, -1), 0.4, LINE),
                           ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('TOPPADDING', (0, 0), (-1, -1), 2),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
    return t


def footer(canvas, doc):
    canvas.saveState(); canvas.setFont('Helvetica', 7.6); canvas.setFillColor(GREY)
    canvas.drawString(2.0 * cm, 1.0 * cm, 'CERTAIN-COAST - concept note - NATO SPS Multi-Year Project, call 2027-1')
    canvas.drawRightString(A4[0] - 2.0 * cm, 1.0 * cm, f'page {doc.page}')
    canvas.restoreState()


def main(out):
    S = styles()
    rows = BB.compute()
    total = sum(r['tot'] for r in rows)
    by = defaultdict(float)
    for r in rows:
        by[A.sps_cat(r)] += r['tot']
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=2.0 * cm, rightMargin=2.0 * cm, topMargin=1.5 * cm,
                            bottomMargin=1.6 * cm, title='CERTAIN-COAST - concept note', author='CERTAIN-COAST applicants',
                            pageCompression=1)
    st = [Paragraph('CERTAIN-COAST - concept note', S['title']), Paragraph(clean(A.TITLE), S['sub']),
          Paragraph(clean(f'NATO Science for Peace and Security (SPS) Programme - Multi-Year Project, call 2027-1 - 36 '
                          f'months - about EUR {total:,.0f} requested from NATO - coordinator: Faculty of Geology and '
                          f'Mining, Polytechnic University of Tirana, Albania'), S['meta'])]
    st += [Paragraph('1. In short', S['h'])] + text_blocks(S, A.ABSTRACT)
    st += [Paragraph('2. The security challenge', S['h'])] + text_blocks(S, A.SECURITY)
    st += [Paragraph('3. Who uses it, and how', S['h'])] + text_blocks(S, A.RELEVANCE)
    st += [Paragraph('4. What the project will deliver, and what is new', S['h'])] + text_blocks(S, A.DELIVER)
    st += [Paragraph('5. How the project works', S['h'])] + text_blocks(S, A.HOW)
    st += [Paragraph('6. The end-users: what they give and what they gain', S['h']),
           grid(S, ['End-user', 'Contribution (in kind; no SPS funds)', 'What it gains'], END_USERS,
                [4.4 * cm, 6.3 * cm, 6.3 * cm]),
           Paragraph(clean('The bulletins are advisory: operational decisions stay with the operators, and any warning to '
                           'the public is issued only by the competent authorities. Data provided by end-users are '
                           'restricted, used under data agreements, and every publication is reviewed for sensitive '
                           'content before release; software and non-restricted data products are open, with a DOI.'),
                     S['note'])]
    wp = [[w[0], w[1], f'Months {w[3][0]}-{w[3][1]}'] for w in W.WPS]
    st += [Paragraph('7. Work plan and milestones', S['h']),
           grid(S, ['Work package', 'Title', 'Duration'], wp, [2.6 * cm, 11.0 * cm, 3.4 * cm]), Spacer(1, 4),
           grid(S, ['Milestone', 'Month', 'What is achieved'], [[m[0], str(m[1]), m[2]] for m in W.MILESTONES],
                [2.6 * cm, 1.6 * cm, 12.8 * cm])]
    brow = [[c, f'{by[c]:,.0f}'] for c in A.SPS_CATS if by.get(c)] + [['Total requested from NATO SPS', f'{total:,.0f}']]
    st += [Paragraph('8. Budget (EUR)', S['h']), grid(S, ['Category', 'EUR'], brow, [11.0 * cm, 6.0 * cm]),
           Paragraph(clean('Salaries, overheads and the in-kind contributions of the institutions and end-users are not '
                           'charged to NATO. The monitoring network bought by the project is handed over to the '
                           'operators.'), S['note'])]
    picks = ('• Alarms and operating window', '• Pumping and hidden drought demand', '• Sensors that interfere',
             '• Crossings between samples', '• Boundaries known only through rain')
    ev = [ln for ln in A.STATUS.split('\n') if ln.startswith(picks)]
    st += [Paragraph('9. Evidence from the preparatory work (2026)', S['h'])] + text_blocks(S, '\n'.join(ev)) + \
          [Paragraph(clean('These are tests on synthetic coasts and on the existing chloride model with illustrative '
                           'values, not results at Durrës; the project calibrates and verifies them on site.'), S['note'])]
    st += [Paragraph('10. Contact', S['h']),
           Paragraph(clean('Assoc. Prof. Dr. Dulian Zeqiraj, NATO-country Project Director - Department of Energy '
                           'Resources, Faculty of Geology and Mining, Polytechnic University of Tirana, Albania - '
                           'dulian.zeqiraj@fgjm.edu.al'), S['p'])]
    doc.build(st, onFirstPage=footer, onLaterPages=footer)
    print('saved', out, '| total', total)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Concept_Note.pdf')
