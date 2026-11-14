"""CERTAIN-COAST (NATO SPS proposal): state of the art on monitoring networks that are optimal today and may not be
optimal tomorrow. Twenty key papers of 2020-2026 from Oxford, Caltech, UC Berkeley, MIT and Harvard, their
mathematics, what they leave open for a coastal multi-hazard network, the step CERTAIN-COAST takes beyond each one, a
computed one-dimensional illustration of the lifetime of a network, and a closing summary of the state of the art for
the CERTAIN-COAST case. Word, native OMML equations (pandoc), equations new in this proposal in red, clickable links.

usage: python build_network_sota.py OUT.docx"""
import json
import os
import sys
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', '..', 'ml_paradigms', 'word'))
import build_sota as BS  # noqa: E402
from build_sota import run, para, heading, table, link  # noqa: E402
from build_decisions_drl import box, body, bullet, figure, E_mrich  # noqa: E402
import netsota_data as D  # noqa: E402

NAVY, BLUE, GREY, GREEN, ORANGE = '1F3864', '2E6DB4', '52606D', '1E8A5A', 'C55A11'
CODE = 'https://github.com/dulianzeqiraj/certain-coast'
FIG = os.path.join(HERE, 'netsota', 'fig_lifetime.png')
FIG_JSON = os.path.join(HERE, 'netsota', 'fig_lifetime.json')


def card(doc, it, E, display_eq, num):
    """One paper: citation, links, what it did, its mathematics, theorem, what it leaves open, the step beyond it."""
    p = para(doc, 1, before=6)
    p.paragraph_format.keep_with_next = True
    run(p, f'[{it["n"]}]  ', bold=True, size=10.5, color=NAVY)
    run(p, it['cite'], bold=True, size=10.5)
    p = para(doc, 3, 0.4)
    p.paragraph_format.keep_with_next = True
    run(p, it['inst'] + '   ', italic=True, size=9.5, color=GREY)
    link(p, it['doi'], it['doi'].replace('https://', ''), 9.5)
    if it.get('free'):
        run(p, '   |   free: ', size=9.5, color=GREY)
        link(p, it['free'], it.get('free_label', 'free copy'), 9.5)
    for label, key, col in (('Done: ', 'done', NAVY),):
        q = para(doc, 2, 0.4)
        q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run(q, label, bold=True, size=10, color=col)
        E_mrich(q, it[key], E, size=10)
    for tex, what in it.get('math', []):
        q = para(doc, 0, 0.4)
        q.paragraph_format.keep_with_next = True
        run(q, 'Mathematics: ', bold=True, size=10, color=BLUE)
        E_mrich(q, what, E, size=10)
        num[0] += 1
        display_eq(doc, E, tex, num[0])
    for label, key, col in (('Result: ', 'theorem', BLUE), ('Open for a coastal network: ', 'gap', GREY),
                            ('Beyond it in CERTAIN-COAST: ', 'beyond', GREEN)):
        if not it.get(key):
            continue
        q = para(doc, 2, 0.4)
        q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run(q, label, bold=True, size=10, color=col)
        E_mrich(q, it[key], E, size=10)


def main(out):
    from build_gar_doc import Eqs, display_eq
    import omml
    import polish_parts as PP
    E = Eqs()
    BS._EQ = E
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0)
    s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']
    st.font.name = 'Arial'
    st.font.size = Pt(11)
    num = [0]
    red = []

    p = para(doc, 2)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'CERTAIN-COAST — A monitoring network that is optimal today may not be optimal tomorrow', bold=True,
        size=17, color=NAVY)
    p = para(doc, 4)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, D.SUBTITLE, bold=True, size=11.5, color=NAVY)
    p = para(doc, 10)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'NATO SPS Multi-Year Project, call 2027-1. Supplement to WP4 (the network designed for the warnings) and '
           'WP5 (live operation). Equations are native Word math; the equations new in this proposal are set in red. '
           'References were checked in Crossref or arXiv, November 2026.', italic=True, size=9.5, color=GREY)
    box(doc, 'Innovation', D.INNOVATION, E, fill='FDF3EA', bar=ORANGE)

    # 1 why the optimum moves
    heading(doc, '1. Why the optimal network moves', 14)
    body(doc, D.WHY, E)
    body(doc, 'A design $\\xi$ (where the sensors stand and of which type they are) is chosen to learn a goal $q$, '
              'here the position of the saline wedge at the supply wells, the water table under the foundations, or '
              'the alarm indicators. In the Bayesian, goal-oriented form the criterion is the expected information '
              'the data $y$ bring about $q$ [C1]:', E)
    num[0] += 1
    display_eq(doc, E, r'U(\xi)=\mathbb{E}_{y\mid\xi}\left[D_{\mathrm{KL}}\left(p(q\mid y,\xi)\,\|\,p(q)\right)\right]'
                       r'=I(q;y\mid\xi),\qquad \xi^{\star}=\underset{\xi\in\Xi}{\arg\max}\ U(\xi)', num[0])
    body(doc, 'The coast is not still. Its state $x_t$ (heads, salt, land motion, pore pressure) moves with the '
              'decisions $u_t$, the forcing and the parameters $\\theta$, and the network observes it through its '
              'own observation operator:', E)
    num[0] += 1
    display_eq(doc, E, r'x_{t+1}=F\left(x_t,u_t;\theta\right)+w_t,\qquad y_t=H_{\xi}\left(x_t\right)+\epsilon_t', num[0])
    body(doc, 'The criterion and its optimum therefore depend on time, and the network that was optimal when it was '
              'installed loses information as the goal moves away from it:', E)
    num[0] += 1
    display_eq(doc, E, r'U_t(\xi)=I\left(q_t;y_{0:t}\mid\xi\right),\qquad \xi^{\star}_t=\underset{\xi\in\Xi}{\arg\max}\ '
                       r'U_t(\xi),\qquad L_t(\xi)=U_t\left(\xi^{\star}_t\right)-U_t(\xi)\ge 0', num[0])
    body(doc, 'For a network designed by D-optimality on $p$ parameters with Fisher matrix $F_t$, the efficiency of a '
              'design and the lifetime of the network, the first time its efficiency falls below $1-\\varepsilon$, '
              'are', E)
    num[0] += 1
    red.append(num[0])
    display_eq(doc, E, r'e_t(\xi)=\left(\frac{\det F_t(\xi)}{\det F_t\left(\xi^{\star}_t\right)}\right)^{1/p},\qquad '
                       r'T_{\varepsilon}(\xi)=\inf\left\{t\ge t_0:\ e_t(\xi)<1-\varepsilon\right\}', num[0])
    with open(FIG_JSON, encoding='utf-8') as fh:
        r = json.load(fh)
    body(doc, D.ILLUSTRATION.format(**{
        't0': r['toe_m']['0'], 't20': r['toe_m']['20'], 't40': r['toe_m']['40'],
        'e10': r['eff_today']['10'], 'e20': r['eff_today']['20'], 'life': r['lifetime_years']['today'],
        'r0': r['eff_robust']['0'], 'ra': r['years_above']['robust'][0], 'mt': r['mean_eff']['today'],
        'mr': r['mean_eff']['robust']}), E)
    figure(doc, FIG, 'Figure 1. A network that is optimal today and not tomorrow (one-dimensional illustration, '
                     'illustrative values). (a) The sharp interface of a confined coastal aquifer today and after 20 and '
                     '40 years of relative sea-level rise of 12 mm/yr (sea level and subsidence), with five chloride '
                     'sensors at the base chosen by D-optimality for the toe and the width of the mixing zone: the '
                     'network optimal today (dots) and the network designed for the 40-year horizon (squares). '
                     '(b) Their D-efficiency against the network re-designed each year. Result of the author\'s code '
                     '(netsota_fig.py); the open-source code of the project, github.com/dulianzeqiraj/certain-coast, is '
                     'updated continuously and, if the project is funded, its final stage is a three-dimensional '
                     'open-source model.', width=16.0)

    # 2 the papers
    heading(doc, f'2. The {sum(len(g[1]) for g in D.GROUPS)} key papers (2020–2026)', 14)
    body(doc, D.PAPERS_INTRO, E)
    for title, items in D.GROUPS:
        heading(doc, title, 12, color=BLUE, before=8)
        for it in items:
            card(doc, it, E, display_eq, num)

    # 3 comparison
    heading(doc, '3. What the twenty papers cover', 14)
    body(doc, 'Each column is a property a coastal monitoring network needs. ✓ done, ~ partly, – not done.', E)
    t = table(doc, ['Paper', 'Re-designs in time', 'Model error or drift', 'Goal-oriented', 'Guarantee', 'Field network'],
              D.COVER, [5.2, 2.4, 2.4, 2.3, 2.2, 2.5], size=9)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    para(doc, 4)

    # 4 summary
    heading(doc, '4. The state of the art for the CERTAIN-COAST case', 14)
    heading(doc, '4.1 What is solved', 12, color=BLUE, before=6)
    for b in D.SOLVED:
        bullet(doc, b, E)
    heading(doc, '4.2 What is not solved for a coastal multi-hazard network', 12, color=BLUE, before=6)
    for b in D.OPEN:
        bullet(doc, b, E)
    heading(doc, '4.3 The step CERTAIN-COAST takes', 12, color=BLUE, before=6)
    body(doc, D.STEP_INTRO, E)
    num[0] += 1
    red.append(num[0])
    display_eq(doc, E, r'\underline{T}_{\varepsilon}(\xi)=\inf\left\{t\ge t_0:\ \underline{e}_t(\xi)<1-\varepsilon\right\},'
                       r'\qquad \Pr\left[e_t(\xi)\ge\underline{e}_t(\xi)\ \ \forall t\le\underline{T}_{\varepsilon}(\xi)'
                       r'\right]\ge 1-\delta', num[0])
    body(doc, D.STEP_LIFETIME, E)
    num[0] += 1
    red.append(num[0])
    display_eq(doc, E, r'\xi_{k+1}=\underset{\xi^{\prime}\in\Xi\left(\xi_k\right)}{\arg\max}\ \left[\sum_{t=t_k}^{t_{k+1}-1}'
                       r'V_t\left(\xi^{\prime}\right)-c\left(\xi_k\to\xi^{\prime}\right)\right]', num[0])
    body(doc, D.STEP_RULE, E)
    for b in D.STEP_BULLETS:
        bullet(doc, b, E)
    box(doc, 'In one sentence', D.ONE_SENTENCE, E)

    # references
    heading(doc, 'References', 14)
    allp = [it for _, items in D.GROUPS for it in items]
    for it in sorted(allp, key=lambda x: x['n']):
        p = para(doc, 3)
        p.paragraph_format.left_indent = Cm(0.7)
        p.paragraph_format.first_line_indent = Cm(-0.7)
        run(p, f'[{it["n"]}]  ', bold=True, size=9.5, color=NAVY)
        run(p, it['cite'] + ' ', size=9.5)
        link(p, it['doi'], it['doi'].replace('https://', ''), 9.5)
    for key, cite, url in D.OTHER:
        p = para(doc, 3)
        p.paragraph_format.left_indent = Cm(0.7)
        p.paragraph_format.first_line_indent = Cm(-0.7)
        run(p, f'[{key}]  ', bold=True, size=9.5, color=NAVY)
        run(p, cite + ' ', size=9.5)
        if url:
            link(p, url, url.replace('https://', ''), 9.5)
    p = para(doc, 4, before=6)
    run(p, D.NOTE, italic=True, size=9, color=GREY)

    BS._EQ = None
    work = tempfile.mkdtemp()
    draft = os.path.join(work, 'draft.docx')
    doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh)
    omml.main(draft, eq_json, out)
    PP.RED[99] = red                                  # the equations new in this proposal, in red
    d = Document(out)
    n_red, _ = PP.colour_equations(list(d.element.body), 99)
    d.core_properties.title = 'CERTAIN-COAST: a monitoring network that is optimal today may not be optimal tomorrow'
    d.core_properties.author = 'Dulian Zeqiraj'
    d.save(out)
    print('saved', out, '|', len(E.items), 'equations |', num[0], 'numbered |', n_red, 'in red |', len(allp), 'papers')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_SOTA_Network_Optimal_Today.docx')
