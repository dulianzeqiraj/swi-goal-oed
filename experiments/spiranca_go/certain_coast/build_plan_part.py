"""CERTAIN-COAST (NATO SPS proposal): "The project at a glance", the part of the Additional files that shows the
work plan in five figures (structure, communication, team, deliverables, Gantt chart), drawn by plan_figs.py from
the builders of the work plan, so that nothing is typed twice.

usage: python build_plan_part.py FIGDIR OUT.docx"""
import os
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import run, para, heading, shade  # noqa: E402

NAVY, GREY = '1F3864', '52606D'
FIGS = [
    ('plan_fig1_structure.png',
     'Project structure: the management, the work packages with their leads, the interfaces between them and the '
     'deliverables they hand on.'),
    ('plan_fig2_dissemination.png',
     'Communication, dissemination and exploitation, audience by audience: the products, the months, the indicators '
     'and the licences.'),
    ('plan_fig3_team.png',
     'The team and its competences: the participants of the Polytechnic University of Tirana, Qatar University and '
     'the end-user, with their shares of time.'),
    ('plan_fig4_deliverables.png',
     'Deliverables: their timeline by work package, their type and access level, and what each one feeds.'),
    ('plan_fig5_gantt.png',
     'Gantt chart: the tasks, the milestones, the evidence gates with their fallbacks, the deliverables and the '
     'critical path over 36 months.'),
]


def main(figdir, out):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0)
    s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']
    st.font.name = 'Arial'
    st.font.size = Pt(11)

    p = para(doc, 2)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'CERTAIN-COAST — The project at a glance', bold=True, size=18, color=NAVY)
    p = para(doc, 10)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Structure, communication, team, deliverables and timeline of the work plan', italic=True, size=11,
        color=GREY)
    p = para(doc, 8)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run(p, 'The five figures show the work plan of the proposal: who leads each work package, what passes between '
           'them, how the results reach each audience, who does the work, when each deliverable is due and where the '
           'evidence gates stand on the critical path. They are drawn from the same tables as the form (work packages, '
           'tasks, deliverables, milestones, risks and participants), so the figures and the form cannot disagree.',
        size=11)
    t = doc.add_table(rows=1, cols=1)
    c = t.rows[0].cells[0]
    tcPr = c._tc.get_or_add_tcPr()
    b = OxmlElement('w:tcBorders')
    for side, val, sz, col in (('top', 'nil', '0', 'auto'), ('left', 'single', '24', 'C55A11'),
                               ('bottom', 'nil', '0', 'auto'), ('right', 'nil', '0', 'auto')):
        e = OxmlElement(f'w:{side}')
        e.set(qn('w:val'), val)
        e.set(qn('w:sz'), sz)
        e.set(qn('w:color'), col)
        b.append(e)
    tcPr.append(b)
    shade(c, 'FDF3EA')
    q = c.paragraphs[0]
    run(q, 'Innovation', bold=True, size=10.5, color='C55A11')
    q = c.add_paragraph()
    q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    q.paragraph_format.space_after = Pt(4)
    run(q, 'A work plan built around evidence gates: each certified result is tested at a gate with a stated pass test '
           'and a fallback before the next work package relies on it, and the gates stand on the critical path, so '
           'the plan shows where the project can fail early and what it does then.', size=10.5)
    para(doc, 6)
    for k, (fn, cap) in enumerate(FIGS, 1):
        path = os.path.join(figdir, fn)
        if not os.path.exists(path):
            print('missing', path)
            continue
        if k > 1:
            p = para(doc, 0)
            p.paragraph_format.page_break_before = True
        p = para(doc, 2)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(path, width=Cm(17.0))
        p = para(doc, 10)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run(p, f'Figure {k}. {cap}', italic=True, size=9.5, color=GREY)
    doc.save(out)
    print('saved', out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
