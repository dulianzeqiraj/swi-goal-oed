"""CERTAIN-COAST (NATO SPS proposal): Decisions in extreme events. The decisions the operators and the end-user must take
when an extreme event comes, the equations of the project written as one final assembled system with the decisions in
it, and deep reinforcement learning that searches the decisions only inside the certified safe set. Word, native OMML
equations (pandoc), clickable links. Figures, when given, are results of the author's open-source MATLAB code.

usage: python build_decisions_drl.py OUT.docx [FIGDIR]"""
import json
import os
import sys
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', '..', 'ml_paradigms', 'word'))
import build_sota as BS  # noqa: E402
from build_sota import run, para, heading, table, shade, link  # noqa: E402

NAVY, BLUE, GREY, GREEN = '1F3864', '2E6DB4', '52606D', '1E8A5A'
CODE = 'https://github.com/dulianzeqiraj/certain-coast'

REFS = [
    ('Altman, E. (2021). Constrained Markov Decision Processes. Routledge (first published 1999).',
     'https://doi.org/10.1201/9781315140223'),
    ('Alshiekh, M., Bloem, R., Ehlers, R., Könighofer, B., Niekum, S. and Topcu, U. (2018). Safe reinforcement learning '
     'via shielding. Proceedings of the AAAI Conference on Artificial Intelligence 32(1).',
     'https://doi.org/10.1609/aaai.v32i1.11797'),
    ('Coughlan de Perez, E., van den Hurk, B., van Aalst, M.K., Jongman, B., Klose, T. and Suarez, P. (2015). '
     'Forecast-based financing: an approach for catalyzing humanitarian action based on extreme weather and climate '
     'forecasts. Natural Hazards and Earth System Sciences 15(4), 895–904.', 'https://doi.org/10.5194/nhess-15-895-2015'),
    ('Coulson, J., Lygeros, J. and Dörfler, F. (2022). Distributionally robust chance constrained data-enabled '
     'predictive control. IEEE Transactions on Automatic Control 67(7), 3289–3304.',
     'https://doi.org/10.1109/TAC.2021.3097706'),
    ('Haasnoot, M., Kwakkel, J.H., Walker, W.E. and ter Maat, J. (2013). Dynamic adaptive policy pathways: a method for '
     'crafting robust decisions for a deeply uncertain world. Global Environmental Change 23(2), 485–498.',
     'https://doi.org/10.1016/j.gloenvcha.2012.12.006'),
    ('Mnih, V., Kavukcuoglu, K., Silver, D., Rusu, A.A., Veness, J., Bellemare, M.G. et al. (2015). Human-level control '
     'through deep reinforcement learning. Nature 518(7540), 529–533.', 'https://doi.org/10.1038/nature14236'),
    ('Murgatroyd, A., Gavin, H., Becher, O., Coxon, G., Hunt, D., Fallon, E. et al. (2022). Strategic analysis of the '
     'drought resilience of water supply systems. Philosophical Transactions of the Royal Society A 380(2238), 20210292.',
     'https://doi.org/10.1098/rsta.2021.0292'),
    ('Nemirovski, A. and Shapiro, A. (2007). Convex approximations of chance constrained programs. SIAM Journal on '
     'Optimization 17(4), 969–996.', 'https://doi.org/10.1137/050622328'),
    ('Shah, D., Xie, Q. and Xu, Z. (2022). Nonasymptotic analysis of Monte Carlo tree search. Operations Research '
     '70(6), 3234–3260.', 'https://doi.org/10.1287/opre.2021.2239'),
    ('Shepherd, T.G., Boyd, E., Calel, R.A., Chapman, S.C., Dessai, S., Dima-West, I.M. et al. (2018). Storylines: an '
     'alternative approach to representing uncertainty in physical aspects of climate change. Climatic Change '
     '151(3–4), 555–571.', 'https://doi.org/10.1007/s10584-018-2317-9'),
    ('Sirignano, J. and Spiliopoulos, K. (2022). Asymptotics of reinforcement learning with neural networks. Stochastic '
     'Systems 12(1), 2–29.', 'https://doi.org/10.1287/stsy.2021.0072'),
    ('Van Parys, B.P.G., Mohajerin Esfahani, P. and Kuhn, D. (2021). From data to decisions: distributionally robust '
     'optimization is optimal. Management Science 67(6), 3387–3402.', 'https://doi.org/10.1287/mnsc.2020.3678'),
    ('Wabersich, K.P. and Zeilinger, M.N. (2023). Predictive control barrier functions: enhanced safety mechanisms for '
     'learning-based control. IEEE Transactions on Automatic Control 68(5), 2638–2651.',
     'https://doi.org/10.1109/TAC.2022.3175628'),
    ('Wicker, M., Laurenti, L., Patane, A., Paoletti, N., Abate, A. and Kwiatkowska, M. (2024). Probabilistic '
     'reach-avoid for Bayesian neural networks. Artificial Intelligence 334, 104132.',
     'https://doi.org/10.1016/j.artint.2024.104132'),
    ('Zscheischler, J., Westra, S., van den Hurk, B.J.J.M., Seneviratne, S.I., Ward, P.J., Pitman, A. et al. (2018). '
     'Future climate risk from compound events. Nature Climate Change 8(6), 469–477.',
     'https://doi.org/10.1038/s41558-018-0156-3'),
]
R = {k: i + 1 for i, k in enumerate(['altman', 'shield', 'fbf', 'coulson', 'pathways', 'mnih', 'drought', 'chance',
                                       'mcts', 'storylines', 'sirignano', 'dro', 'cbf', 'reachavoid', 'compound'])}


def c(*keys):
    return '[' + ', '.join(str(R[k]) for k in keys) + ']'


DECISIONS = [
    ['Water utility, wellfields of Durrës–Fushë-Kuqe', 'Cut or shift pumping between wells and fields; switch part of '
     'the supply to other sources; order a chloride sampling campaign', 'Drought with a storm surge; an earthquake that '
     'moves the heads', 'Less pumping protects the aquifer but leaves people short of water; chloride is seen weeks late, '
     'between two samples'],
    ['Port of Durrës', 'Restrict berths and heavy loads; inspect the quay walls; dewater behind them', 'Earthquake; '
     'extreme sea level', 'The liquefaction risk depends on the water table of that day; every hour of a closed berth '
     'costs'],
    ['Energy landfall near Fier (Trans Adriatic Pipeline)', 'Inspect and protect the landfall; adapt the operation',
     'Storm surge; earthquake; subsidence', 'The event may be rarer than the record; a failure has international '
     'consequences'],
    ['Institute of Geosciences (IGJEO), end-user', 'Issue, escalate or lift a warning bulletin for each asset',
     'All three hazards at once', 'A false alarm erodes trust and a missed alarm costs most; the three hazards share one '
     'water table'],
]

USES = [
    ['Wellfield operation in a drought with a storm surge', 'Weekly pumping of every well and field',
     'Chloride at the supply screens below the limit (intrusion alarm)', 'Water utility'],
    ['Port after an earthquake', 'Which berths to restrict, where to dewater, the order of the inspections',
     'Factor of safety of the quay foundations (liquefaction alarm)', 'Port of Durrës'],
    ['Energy landfall in a storm or an earthquake', 'Inspection and protection schedule',
     'Extreme water level and liquefaction at the landfall', 'Pipeline operator'],
    ['Warning bulletins', 'Issue, escalate or lift each bulletin', 'Joint miss rate at most $\\sum\\nolimits_{k}\\alpha_k$',
     'IGJEO'],
    ['Monitoring', 'Which well to sample next, which logger to read', 'The certified band of the warning between samples',
     'IGJEO and the utility'],
]

PROTOCOL = [
    ['Before the season, once a year', 'IGJEO with the operators of the wellfields, the port and the landfall',
     'The tolerances $\\alpha_k$, the thresholds $\\tau_k$, the priorities $\\omega_k$ of (13) and the action '
     'agreed for each alarm', 'The certified miss rates, the value of the warning for each user and the closing year of '
     'the safe window (Part 3)'],
    ['When an alarm fires', 'Each operator', 'The action agreed in advance for that alarm, taken on the forecast and '
     f'not after the damage {c("fbf")}', 'The recommended decision (12) with the margins (7) and the lead time'],
    ['When the safe window is empty', 'The operators concerned, convened by IGJEO', 'Which hazard to accept above its '
     'tolerance, and for how long', 'The decision (13), the trade-off between the hazards and the storylines of the '
     'event'],
    ['After the event', 'IGJEO with the project (post-event protocol, T5.4)', 'New tolerances and actions; the record of '
     'the decisions and their outcomes', 'The recalibrated margins (7), the earthquake read as a free pumping test '
     '(Part 6) and the decisions compared with the recommendations'],
]

PARTS = [
    ['1. State of the art', 'The gaps the agent closes: decisions taken from one physical model, each with a stated miss '
     'rate (innovations M1, M2, P3 and V1).'],
    ['2. Mathematical state of the art', 'The laws of the random forcing and the decision map that fix the simulator on '
     'which the agent is trained.'],
    ['3. Technical annex', 'The certified margins (6)–(7) of the annex and the safe operating window (10), which the '
     'shield enforces.'],
    ['4. The assembled system', 'The environment itself: the goal-graded assembly makes it fast enough for many training '
     'episodes, and its adjoint gives the gradients.'],
    ['5. The learned boundary', 'It closes the environment at the inland cut, so the agent is trained on the aquifer '
     'beyond the model as well.'],
    ['6. The earthquake in the aquifer', 'The jump of pore pressure at each earthquake and the liquefaction constraint; '
     'the earthquake as a free pumping test sharpens the model the agent learns on.'],
]


def box(doc, title, text, E, fill='EEF4FB', bar=NAVY):
    t = doc.add_table(rows=1, cols=1)
    cell = t.rows[0].cells[0]
    tcPr = cell._tc.get_or_add_tcPr()
    b = OxmlElement('w:tcBorders')
    for side, val, sz, color in (('left', 'single', '24', bar), ('top', 'nil', '0', 'auto'), ('bottom', 'nil', '0', 'auto'),
                                 ('right', 'nil', '0', 'auto')):
        e = OxmlElement(f'w:{side}'); e.set(qn('w:val'), val); e.set(qn('w:sz'), sz); e.set(qn('w:color'), color)
        b.append(e)
    tcPr.append(b)
    shade(cell, fill)                              # w:shd after w:tcBorders (schema order)
    p = cell.paragraphs[0]; p.paragraph_format.space_before = Pt(3); p.paragraph_format.space_after = Pt(2)
    run(p, title, bold=True, size=10.5, color=NAVY)
    q = cell.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; q.paragraph_format.space_after = Pt(4)
    E_mrich(q, text, E, size=10.5)
    para(doc, 4)
    return t


def E_mrich(p, text, E, size=11):
    from build_gar_doc import mrich
    mrich(p, text, E, size=size)


def body(doc, text, E, size=11, after=6):
    p = para(doc, after); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    E_mrich(p, text, E, size=size)
    return p


def bullet(doc, text, E, size=11):
    p = para(doc, 3, 0.5); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(-0.4)
    run(p, '•  ', bold=True, size=size, color=BLUE)
    E_mrich(p, text, E, size=size)
    return p


def figure(doc, path, caption, width=16.0):
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Cm(width))
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run(p, caption, italic=True, size=9.5, color=GREY)


def main(out, figdir=None):
    from build_gar_doc import Eqs, display_eq
    import omml
    E = Eqs()
    BS._EQ = E                                     # table cells written by build_sota.table also get native math
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)

    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'CERTAIN-COAST — Decisions in extreme events', bold=True, size=18, color=NAVY)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'The decisions the operators must take, the final assembled system of equations, and deep reinforcement '
           'learning kept inside the certified limits', bold=True, size=12, color=NAVY)
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'NATO SPS Multi-Year Project, call 2027-1. Supplement to WP2, WP3 and WP5. Equations are native Word math; '
           'references were checked in Crossref.', italic=True, size=10, color=GREY)

    body(doc, 'When an extreme event comes, a drought with a storm surge, an earthquake or a sea level higher than any on '
              'record, the operators of the wellfields, the port and the energy landfall, and the Institute of '
              'Geosciences (IGJEO) that issues the bulletins, must decide quickly, with incomplete data, and with '
              'decisions that pull the hazards in opposite directions. This part states those decisions, writes the '
              'equations of the project as one final assembled system in which the decisions are part of the state '
              'equations, and shows how deep reinforcement learning turns that system into recommended decisions that '
              'never leave the certified limits.', E)
    box(doc, 'Innovation', 'The decision is part of the assembled system: one set of equations carries the hazards, the '
             'certified warnings and the decisions of every operator, and a deep reinforcement learning agent searches '
             'the decisions only inside the set that the certified margins keep safe, so its recommendations carry the '
             'same stated miss rate as the warnings.', E, fill='FDF3EA', bar='C55A11')

    heading(doc, '1. The decisions in an extreme event', 14)
    t = table(doc, ['Who decides', 'Decision', 'Extreme events', 'Why it is hard'], DECISIONS, [3.6, 4.6, 3.6, 5.2], size=9.5)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    para(doc, 4)
    body(doc, 'Five features make these decisions hard. **Compound events:** the drivers act at once, a surge on a '
              f'drought, an earthquake on a high water table {c("compound")}. **One lever, opposite effects:** pumping '
              'lowers liquefaction susceptibility but draws the saline wedge inland and compacts the clays (Part 1). '
              '**Beyond the record:** the event that matters may never have been observed, so it is represented by '
              f'storylines {c("storylines")} and by the extreme-value margins of the alarms (Part 3). **Time and '
              'irreversibility:** a salinised well or an inelastic compaction step does not come back. **Many '
              'decision-makers on one aquifer:** each operator acts on its own objective, while the warnings and the '
              'water table are shared; adaptive pathways, forecast-based action and drought resilience analysis address '
              f'parts of this {c("pathways", "fbf", "drought")}, but none takes the decision from one physical model with '
              'a stated miss rate.', E)

    heading(doc, '2. The final assembled system', 14)
    body(doc, 'The equations of Parts 2 to 6 are assembled into one system with one state. The state collects the heads '
              '$h$, the salt concentration $c$, the land motion $u_z$ from the compaction of the clays, the pore pressure '
              '$p$ of the layers under the free surface, and the memory states of the learned boundary. Flow and salt '
              'transport with variable density:', E)
    display_eq(doc, E, r'S_s\,\frac{\partial h}{\partial t}-\nabla\cdot\left[K\left(\nabla h+\frac{\rho-\rho_0}{\rho_0}\,'
                       r'\mathbf{e}_z\right)\right]=\sum_{w}Q_w(t)\,\delta\left(\mathbf{x}-\mathbf{x}_w\right)+r(\mathbf{x},t)', 1)
    display_eq(doc, E, r'\phi\,\frac{\partial c}{\partial t}+\nabla\cdot\left(\mathbf{q}\,c-\phi\,\mathbf{D}\,\nabla c\right)=0,'
                       r'\qquad \mathbf{q}=-K\left(\nabla h+\frac{\rho-\rho_0}{\rho_0}\,\mathbf{e}_z\right)', 2)
    body(doc, 'The compaction of each clay layer $\\ell$ of thickness $b_\\ell$ lowers the land, with the elastic skeletal '
              'storage $S_{ke,\\ell}$ above the preconsolidation head and the much larger inelastic one $S_{kv,\\ell}$ '
              'below it; the land motion sets the relative sea level, and the relative sea level sets the seaward '
              'boundary as an equivalent fresh head:', E)
    display_eq(doc, E, r'\frac{\partial u_z}{\partial t}=-\sum_{\ell}b_\ell\,S_{k,\ell}\left(h_\ell\right)\,'
                       r'\frac{\partial h_\ell}{\partial t},\qquad R(t)=\eta(t)-u_z(t),\qquad '
                       r'h\big|_{\mathrm{sea}}=\frac{\rho_s}{\rho_0}\left(R(t)-z\right)+z', 3)
    body(doc, 'At the inland cut the model ends, and the aquifer beyond it is represented by the learned boundary of Part 5 '
              '(Proposition 1 there): in the Laplace variable $s$, the flux through the cut is', E)
    display_eq(doc, E, r'\hat{q}(s)=Z(s)\,\hat{u}(s),\qquad Z(s)=C+\sum_{n=1}^{N}w_n\,\frac{s}{s+\mu_n},\qquad C\ge 0,'
                       r'\ w_n\ge 0,\ \mu_n>0', 4)
    body(doc, 'An earthquake at time $\\tau_j$ is a jump of the state: the pore pressure of each layer under the free '
              'surface steps by Proposition 2 of Part 6, with the shear modulus $G$, the Skempton coefficient $B$ and '
              'the undrained Poisson ratio $\\nu_u$ of the layer and the horizontal strain $\\Delta\\varepsilon_a$ of '
              'the crust beneath it. The liquefaction factor of safety then follows the water table of that day:', E)
    display_eq(doc, E, r'p\left(\tau_j^{+}\right)=p\left(\tau_j^{-}\right)-\kappa\,\Delta\varepsilon_a\left(\tau_j\right),\qquad '
                       r'\kappa=\frac{2GB}{3}\,\frac{1+\nu_u}{1-\nu_u}', 5)
    display_eq(doc, E, r'\mathrm{FS}(\mathbf{x},t)=\frac{\mathrm{CRR}(\mathbf{x})}{\mathrm{CSR}\left(z_w(\mathbf{x},t)\right)},'
                       r'\qquad \mathrm{CSR}=0.65\,\frac{a_{\max}}{g}\,\frac{\sigma_v}{\sigma^{\prime}_v}\,r_d', 6)
    body(doc, 'The certified alarm $k$ (intrusion, liquefaction, extreme water level) fires when the forecast of its '
              'indicator at lead time $L_k$ comes within the margin $m_k$ of its threshold $\\tau_k$; the margin adds '
              'the certified error $\\Delta_k$ of the fast copy to the forecast error $\\gamma_k$ calibrated online '
              '(Eqs. (6)–(7) of Part 3):', E)
    display_eq(doc, E, r'A_k(t)=\mathbf{1}\left\{\hat{I}_k\left(t+L_k\right)\ge\tau_k-m_k(t)\right\},\qquad '
                       r'm_k(t)=\Delta_k(t)+\gamma_k(t)', 7)
    body(doc, 'Written together, Eqs. (1)–(7) are one controlled stochastic system. The rain, the sea and the pumping '
              'demand drive it continuously ($\\mathbf{W}_t$), earthquakes and storm surges act as jumps ($N_j$), the '
              'decisions $\\mathbf{u}_t$ of the operators enter as sources and boundary values, and the monitoring network '
              'designed for the warnings (WP4, Part 3) observes it:', E)
    display_eq(doc, E, r'd\mathbf{x}_t=F\left(\mathbf{x}_t,\mathbf{u}_t,\theta\right)dt+G\left(\mathbf{x}_t\right)d\mathbf{W}_t'
                       r'+\sum_{j}J_j\left(\mathbf{x}_{t^-}\right)dN_j(t),\qquad \mathbf{y}_t=H\left(\mathbf{x}_t\right)'
                       r'+\boldsymbol{\epsilon}_t', 8)
    body(doc, 'The decision problem of the operators is a constrained Markov decision process '
              f'{c("altman")}: keep the cost of the decisions (unmet water demand, closed berths, protective works, '
              'damage) as low as possible while the probability that any hazard crosses its threshold within the '
              'horizon stays within the tolerance $\\alpha_k$ agreed with the end-user:', E)
    display_eq(doc, E, r'\min_{\pi}\ \mathbb{E}_{\pi}\left[\sum_{t=0}^{T}\gamma^{t}\,c\left(\mathbf{x}_t,\mathbf{u}_t\right)\right]'
                       r'\quad\text{subject to}\quad \mathbb{P}_{\pi}\left(\exists\,t\le T:\ I_k\left(\mathbf{x}_t\right)>'
                       r'\tau_k\right)\le\alpha_k,\quad k=1,2,3', 9)
    body(doc, 'Its feasible decisions at each bulletin form the certified safe operating window of Part 3 (Eq. (10) '
              'there): the decisions that meet the demand $D$, keep every hazard within its certified limit and cause no '
              'new permanent subsidence,', E)
    display_eq(doc, E, r'W_{\alpha}(R)=\left\{\mathbf{u}:\ Q_w\ge D,\ \ \Pr_{\theta}\left[I_k(\mathbf{u},R;\theta)>\tau_k\right]'
                       r'\le\alpha_k\ (k=1,2,3),\ \ h(\mathbf{x},\mathbf{u},R)\ge h_{\mathrm{pc}}(\mathbf{x})\right\}', 10)
    body(doc, 'Eqs. (1), (2), the compaction law of (3), (6) and the alarm (7), built from published conformal methods, are '
              'standard. Eqs. (4), (5) and (10) carry results of the preparatory work of this proposal (Parts 5, 6 and 3), '
              'and the assembly (8), with the shield (12) and the rule (13) for an empty window, is new here: the hazards, '
              'the certified warnings and the decisions in one system. The equations new in this proposal are set in red.', E)

    heading(doc, '3. Deep reinforcement learning on the assembled system', 14)
    heading(doc, '3.1 The agent and its environment', 12, color=BLUE, before=6)
    body(doc, f'Deep reinforcement learning {c("mnih")} trains a neural policy $\\pi_\\varphi$ that maps what is known '
              'at a bulletin, the assimilated state and its uncertainty $b_t$, to a decision $\\mathbf{u}_t$. Its '
              'environment is the fast copy of the assembled system (8) with its certified error (Part 3, T2.4), driven '
              'by the forcing laws of Part 2 and by storylines of extremes: droughts, surges, earthquakes and their '
              'combinations. The reward is the negative cost $-c(\\mathbf{x}_t,\\mathbf{u}_t)$. Training runs on the '
              'model, never on the real wellfields; the theory of reinforcement learning with neural networks '
              f'{c("sirignano")} and of tree search for rare, high-stakes choices {c("mcts")} supports the two '
              'learning modes used, policy optimisation for routine operation and search for the extreme event.', E)
    heading(doc, '3.2 Training with the constraints', 12, color=BLUE, before=6)
    body(doc, 'The chance constraints of (9) enter the training through Lagrange multipliers $\\lambda_k\\ge 0$, one per '
              f'hazard: the policy descends and the multipliers ascend {c("altman", "chance")},', E)
    display_eq(doc, E, r'\mathcal{L}\left(\varphi,\boldsymbol{\lambda}\right)=\mathbb{E}_{\pi_{\varphi}}\left[\sum_{t}\gamma^{t}'
                       r'\,c\left(\mathbf{x}_t,\mathbf{u}_t\right)\right]+\sum_{k}\lambda_k\left(\mathbb{P}_{\pi_{\varphi}}\left('
                       r'\text{miss}_k\right)-\alpha_k\right)', 11)
    body(doc, 'and the model uncertainty is met by training over the ensemble of parameters $\\theta$ and storylines with '
              f'a distributionally robust objective {c("dro", "coulson")}.', E)
    heading(doc, '3.3 The certified shield', 12, color=BLUE, before=6)
    body(doc, 'A trained network can still propose a decision outside the safe set. The shield removes that risk: every '
              'proposed decision is projected onto the certified safe operating window (10) before it is recommended '
              f'{c("shield", "cbf")},', E)
    display_eq(doc, E, r'\mathbf{u}_t=\underset{\mathbf{u}\in W_{\alpha}\left(R(t)\right)}{\arg\min}\left\|\mathbf{u}-'
                       r'\pi_{\varphi}\left(b_t\right)\right\|', 12)
    body(doc, 'Because the window is built from the certified margins, every recommended decision keeps each hazard '
              'within its stated miss rate, whatever the network has learned; the network only chooses the best decision '
              'among the safe ones. Where the window is empty, the agent reports it, and that is the closing point of '
              'the window that Part 3 computes for planning. The reach-avoid probability of the neural policy is checked '
              f'independently before live use {c("reachavoid")}.', E)
    heading(doc, '3.4 When no decision is safe: the hardest decision', 12, color=BLUE, before=6)
    body(doc, 'In the worst events the window (10) is empty: no decision keeps every hazard within its tolerance, and '
              'every choice moves one hazard above its limit to protect another. The agent then does not choose '
              'silently. It returns the decision that exceeds the tolerances least, weighted by priorities $\\omega_k$ '
              'that the end-user and the operators agree before the season, over the set $U$ of decisions the wells, '
              'the berths and the landfall can physically carry out:', E)
    display_eq(doc, E, r'\mathbf{u}_t^{\dagger}=\underset{\mathbf{u}\in U}{\arg\min}\ \sum_{k=1}^{3}\omega_k\left['
                       r'\Pr_{\theta}\left(I_k(\mathbf{u},R;\theta)>\tau_k\right)-\alpha_k\right]_{+},\qquad '
                       r'\omega_k>0,\quad [z]_{+}=\max(z,0)', 13)
    body(doc, 'With it the bulletin shows, for each hazard, by how much its tolerance is exceeded and for how long, under '
              '$\\mathbf{u}_t^{\\dagger}$ and under the other decisions on the trade-off between the hazards. The '
              'decision itself stays with the people: IGJEO convenes the operators concerned, they choose which hazard to '
              'accept above its tolerance, and the choice is logged with the bulletin so that it can be audited. Storylines '
              f'of the event {c("storylines")} make the trade-off concrete for the people who decide.', E)

    heading(doc, '3.5 Who decides what, and when', 12, color=BLUE, before=6)
    t = table(doc, ['Phase', 'Who decides', 'What is decided', 'What the system gives'], PROTOCOL, [3.0, 3.6, 5.0, 5.4],
              size=9.5)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    para(doc, 4)

    heading(doc, '3.6 Applications', 12, color=BLUE, before=6)
    t = table(doc, ['Application', 'Decision of the agent', 'Kept by the shield', 'Used by'], USES, [4.2, 4.6, 5.0, 3.2],
              size=9.5)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    para(doc, 4)
    body(doc, 'In live operation (WP5) the recommendations are issued with each bulletin beside the certified margins and '
              'the value of the warning for that user, and are compared with the decisions the operators actually take; '
              'at the hand-over (WP6, WP7) the procedure goes to IGJEO with its trained staff. The agent and the shield are released in the open-source '
              f'code of the project, [{CODE.replace("https://", "")}]({CODE}).', E)

    heading(doc, '4. Deep reinforcement learning in each part of these files', 14)
    t = table(doc, ['Part', 'What it gives to the deep reinforcement learning agent'], PARTS, [4.4, 12.6], size=9.5)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    para(doc, 4)

    figs = []
    if figdir and os.path.exists(os.path.join(figdir, 'figures.json')):
        with open(os.path.join(figdir, 'figures.json'), encoding='utf-8') as fh:
            figs = json.load(fh)
    if figs:
        heading(doc, '5. Results of the author\'s MATLAB code', 14)
        body(doc, 'The figures below are computed with the author\'s open-source MATLAB package CERTAIN-COAST, version 0.1.0 '
                  f'([{CODE.replace("https://", "")}]({CODE}), DOI 10.5281/zenodo.24148762); they show the physics of the '
                  'environment, the certified alarm and the observation network on which the agent is trained. The code '
                  'is updated continuously; if the project is funded, its final stage is a three-dimensional open-source '
                  'model.', E)
        for k, f in enumerate(figs, 1):
            figure(doc, os.path.join(figdir, f['file']), f'Figure {k}. ' + f['caption'])

    heading(doc, 'References', 14)
    for i, (cite, url) in enumerate(REFS, 1):
        p = para(doc, 3); p.paragraph_format.left_indent = Cm(0.7); p.paragraph_format.first_line_indent = Cm(-0.7)
        run(p, f'[{i}]  ', bold=True, size=10, color=NAVY); run(p, cite + ' ', size=10); link(p, url, url.replace('https://', ''), 10)
    p = para(doc, 4, before=6)
    run(p, 'Verification note. The references were checked in Crossref (DOI, authors, title, venue), November 2026.',
        italic=True, size=9.5, color=GREY)

    BS._EQ = None
    work = tempfile.mkdtemp()
    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh)
    omml.main(draft, eq_json, out)
    import polish_parts as PP                      # the equations new in this proposal in red, as in the merged files
    d = Document(out)
    n_red, _ = PP.colour_equations(list(d.element.body), 6)
    d.save(out)
    print('saved', out, '|', len(E.items), 'equations |', n_red, 'in red |', len(figs), 'figures')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Decisions_DRL.docx', sys.argv[2] if len(sys.argv) > 2 else None)
