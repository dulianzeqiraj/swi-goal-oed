"""The objective function of the stakeholder decision under extremes (Word, OMML via pandoc).
Numbers of the check are read from experiments/spiranca_go/res/sx.json."""
import json, os, subprocess
import numpy as np
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open('/home/user/swi-goal-oed/experiments/spiranca_go/res/sx.json'))
R, SC = D['rows'], D['scen']
NAME = {'none': 'ordinary', 'rain': 'intense rain', 'drought': 'drought', 'causal': 'causal change', 'compound': 'compound'}
EPS = 0.10

def stat(p):
    e = {s: np.mean([r['closed'][s][p]['exc'] for r in R]) for s in SC}
    w = {s: np.mean([r['closed'][s][p]['water'] for r in R]) for s in SC}
    n = np.mean([r['closed'][s][p]['nsamp'] for r in R for s in SC])
    se = max(e, key=e.get); sw = min(w, key=w.get)
    return e[se], se, w[sw], sw, n

md = []
A = md.append
A('---\ntitle: "The objective function of the stakeholder decision under extremes"\n'
  'subtitle: "Well site, pumping rule, certified alarm and chloride sampling, robust over intense rainfall, drought and causal change (MONTIMI-GO + SPIRANCA-GO + ROJA-GO)"\n'
  'author: "Dulian Zeqiraj"\n---\n')

A('## 1. What is decided\n')
A('| Symbol | Decision | Decided by | Part of the method |')
A('|---|---|---|---|')
A('| $x_s$ | position of the supply-well screen | utility and water agency | MONTIMI-GO |')
A('| $\\pi$ | pumping rule: $u_{t+1}=u_{\\mathrm{dec}}$ while the alarm is silent, $u_{\\mathrm{cut}}$ after it sounds | utility, agreed with the stakeholders | Section 4 |')
A('| $m$ | margin of the alarm (its certificate) | modeller | SPIRANCA-GO |')
A('| $\\sigma=(\\Delta,K,B)$ | sampling rule: interval, re-anchoring window, budget of extra samples | monitoring office | ROJA-GO |')
A('| $H_{\\max}$ | cap on private abstraction in a declared drought (optional lever) | water agency | Section 6 |')
A('')

A('## 2. The model the decision acts on (the equality constraints)\n')
A('The assembled system of the section, as in the assembled-system note: flow with hydraulic memory, Darcy with buoyancy, salt with two immobile zones, $k=1,2$:\n')
A('$$S_s\\frac{\\partial h}{\\partial t}+\\nabla\\cdot\\mathbf q=W(x_s,Q_t,H_t)-\\sum_{k}s_k a_k\\,(h-h_k),\\qquad \\frac{\\partial h_k}{\\partial t}=a_k\\,(h-h_k)\\qquad(1)$$\n')
A('$$\\mathbf q=-\\mathbf K\\,(\\nabla h+\\delta\\,c\\,\\mathbf e_z)\\qquad(2)$$\n')
A('$$n\\frac{\\partial c}{\\partial t}+\\nabla\\cdot(\\mathbf q c)-c\\,\\nabla\\cdot\\mathbf q-\\nabla\\cdot(n\\mathbf D\\nabla c)+\\sum_k n\\,b_k a_k\\,(c-c_k)=0,\\qquad \\frac{\\partial c_k}{\\partial t}=a_k\\,(c-c_k)\\qquad(3)$$\n')
A('Boundaries and sources, where the storyline $\\xi$ enters:\n')
A('$$h_{\\mathrm{sea}}=(1+\\delta)\\,\\eta_\\xi(t)-\\delta z,\\quad q_{n,\\mathrm{inland}}=q_{\\mathrm{in}}R_{\\xi,t},\\quad W=-\\overline{Q}(1+u_t)\\,e_Q(x_s)-\\overline{H} h_{\\xi,t}\\,e_P\\qquad(4)$$\n')
A('$$R_{\\xi,t}=1+0.2\\,r^{\\mathrm{eff}}_t+0.06\\,e^R_t,\\qquad h_{\\xi,t}=1-(0.25+\\phi_{\\xi,t})\\,r^{\\mathrm{eff}}_t+0.15\\,e^H_t\\qquad(5)$$\n')
A('The goal is the sea fraction over the screen $\\Gamma_s$ and its chloride:\n')
A('$$J_t=\\frac{1}{|\\Gamma_s|}\\int_{\\Gamma_s}c\\,\\mathrm dz,\\qquad \\mathrm{Cl}_t=C_f+J_t\\,(C_s-C_f),\\qquad \\mathrm{Cl}_t>250\\ \\mathrm{mg/L}\\iff J_t>\\varepsilon_{\\mathrm{lim}}=0.0109\\qquad(6)$$\n')
A('| Storyline $\\xi$ | Recorded gauge $r^{g}_t$ vs. effective $r^{\\mathrm{eff}}_t$ | Behaviour $\\phi_{\\xi,t}$ | Sea $\\eta_\\xi$ |')
A('|---|---|---|---|')
A('| ordinary | $r^g=r^{\\mathrm{eff}}$, AR(1), lag-one correlation 0.7 | 0 | trend |')
A('| intense rainfall | $r^g=r+2.5$, $r^{\\mathrm{eff}}=r+0.5$ for two years (runoff) | 0 | trend (+ surge) |')
A('| record drought | $r^g=r^{\\mathrm{eff}}=0.5r-2$ for six years | 0 | trend |')
A('| causal change | as the drought | 0.5 during the drought (pumping response ×3) | trend |')
A('| compound | drought, then intense rainfall | 0 | trend (+ surge) |')
A('')

A('## 3. The objective function\n')
A('Deliver as much water as possible in the worst storyline, while counting the days the supply is unfit and the samples spent. The three terms inside the sum are the water delivered, the customer disruption days and the cost of samples:\n')
A('$$\\max_{x_s,\\,\\pi,\\,m,\\,\\sigma}\\ \\min_{\\xi\\in\\Xi}\\ \\mathbb E_{\\omega}\\left[\\sum_{t=1}^{T}\\beta^{t}\\left(\\overline{Q}\\,(1+u_t)\\,\\Delta t-\\lambda_D\\,N_c\\,\\Delta t\\,\\mathbf{1}\\{J_t>\\varepsilon_{\\mathrm{lim}}\\}-c_s\\,n_t\\right)\\right]\\qquad(7)$$\n')
A('subject to (1)–(6) and\n')
A('$$\\frac{1}{T}\\sum_{t=1}^{T}\\mathbb P_\\xi(J_t>\\varepsilon_{\\mathrm{lim}})\\le\\varepsilon\\qquad\\text{for every }\\xi\\in\\Xi\\qquad(8)$$\n')
A('$$\\mathbb P_\\xi(\\hat Y_t-b_t-Y_t>m)\\le\\alpha,\\qquad Y_t=-\\log_{10}J_t\\qquad(9)$$\n')
A('$$u_{t+1}=\\begin{cases}u_{\\mathrm{cut}}, & A_t=1\\\\ u_{\\mathrm{dec}}, & A_t=0\\end{cases},\\qquad A_t=\\mathbf{1}\\{\\hat Y_t-b_t\\le y_{\\ell}+m\\},\\quad y_{\\ell}=-\\log_{10}\\varepsilon_{\\mathrm{lim}}\\qquad(10)$$\n')
A('$$n_t=\\mathbf{1}\\{t\\ \\text{ends a year}\\}+\\mathbf{1}\\{F_t\\},\\qquad \\sum_{t\\in\\text{year}}\\mathbf{1}\\{F_t\\}\\le B,\\qquad b_t=\\frac{1}{K_t}\\sum_{j=1}^{K_t}e_{(j)}\\qquad(11)$$\n')
A('$$m=q_{1-\\alpha}(\\mathbf b)+\\overline{\\delta}\\,\\max\\{0,\\ell(\\mathbf b)\\}\\qquad(12)$$\n')
A('| Term | Meaning | Source |')
A('|---|---|---|')
A('| $\\min_{\\xi}$ | the worst of the five storylines; the decision must hold in all | storylines and UNSEEN (Kelder et al. 2020) |')
A('| $\\overline{Q}(1+u_t)\\Delta t$ | water pumped in season $t$ | utility |')
A('| $\\lambda_D N_c\\Delta t\\,\\mathbf{1}\\{\\cdot\\}$ | customer disruption days, $N_c$ customers, value $\\lambda_D$ per day | Becher et al. (2023) |')
A('| $c_s n_t$ | cost of chloride samples; $B$ caps the extra ones | Considine et al. (2025) |')
A('| (8) | exceedance share at most $\\varepsilon$ in every storyline | chance constraint |')
A('| (9), (12) | the alarm under-warns at most a share $\\alpha$; $\\overline{\\delta}$ is the certified shift radius | SPIRANCA-GO, Theorem S2 |')
A('| (10) | cut pumping in the season after an alarm | risk threshold (Schneider et al. 2022) |')
A('| (11) | yearly sample, extra sample when the watch fires ($F_t$), re-anchoring on the last $K_t$ sample errors $e_{(j)}$ | ROJA-GO |')
A('')

A('## 4. Three equivalent forms for the stakeholders\n')
A('**(a) Constrained form (recommended).** Drop the penalty in (7) and keep (8): the most water in the worst storyline, with the exceedance share at most $\\varepsilon$ everywhere.\n')
A('$$\\max_{x_s,\\pi,m,\\sigma}\\ \\min_{\\xi}\\ \\mathbb E[\\sum_t\\overline{Q}(1+u_t)\\Delta t]\\quad\\text{s.t. (1)–(6), (8)–(12)}\\qquad(13)$$\n')
A('**(b) Weighted form.** Keep the penalty and drop (8); $\\lambda_D$ is the shadow price of (8): the water the stakeholders accept to lose to avoid one disruption day.\n')
A('**(c) Minimax regret.** $\\min_{\\pi}\\max_{\\xi}[V^{\\mathrm{best}}_\\xi-V_\\xi(\\pi)]$, where $V_\\xi$ is the value (7) in storyline $\\xi$ and $V^{\\mathrm{best}}_\\xi$ the best value attainable if $\\xi$ were known (Xu et al. 2021). It is less conservative than (13) when one storyline is much harder than the others.\n')

A('## 5. Innovation: the inner constraints are met by construction\n')
A('Problem (7)–(12) looks large, but two of its parts have closed forms, so the outer search runs over a handful of numbers.\n')
A('- **The margin** (12) satisfies (9) for every shift of size up to $\\overline{\\delta}$ in the span of the anchors (SPIRANCA-GO, Theorem S2), with $\\overline{\\delta}$ taken from an UNSEEN-type ensemble instead of the short record.')
A('- **The window** $K_t$ in (11) minimises the error bound of re-anchoring (Proposition R1 of review 61):\n')
A('$$K_t=\\arg\\min_{K\\ge1}[\\sigma^2(1+\\frac1K)+\\frac{\\rho_t^2\\Delta^2(K+1)^2}{4}],\\qquad K_t^2(K_t+1)=\\frac{2\\sigma^2}{(\\rho_t\\Delta)^2},\\qquad K_t=1\\ \\text{if}\\ \\rho_t\\Delta\\ge\\sigma\\qquad(14)$$\n')
A('- **What is left** is the outer search over $(x_s,u_{\\mathrm{dec}},u_{\\mathrm{cut}},B,H_{\\max})$, evaluated with the simulator over the storylines; only (8) needs simulation, because (9) and (11) hold by construction.\n')

A('## 6. Check on the variable-density section\n')
A(f'Each tested rule is scored on the two numbers of the constrained form (13): the exceedance share in the worst storyline (constraint (8), $\\varepsilon={int(EPS*100)}\\%$) and the water delivered in the worst storyline (the objective), mean over {len(R)} aquifers and {D["ntraj"]} weather sequences each, 30 years after the decision.\n')
A('| Rule | Worst-storyline exceedance (8) | Worst-storyline water (13) | Samples in 30 years | Feasible for $\\varepsilon=10\\%$ |')
A('|---|---|---|---|---|')
best = None
for p, lab in (('none', 'No action'), ('spir', 'Static alarm'), ('spir_ra', 'Yearly sample (S5)'), ('oracle', 'Screen sensor at 89% of the standard'), ('spir_roja', 'ROJA-GO')):
    e, se, w, sw, n = stat(p)
    feas = e <= EPS
    if feas and (best is None or w > best[1]): best = (lab, w, e, se)
    A(f'| {lab} | {100*e:.1f}% ({NAME[se]}) | {100*w:.1f}% ({NAME[sw]}) | {n:.0f} | {"yes" if feas else "no"} |')
A('')
if best:
    A(f'Only **{best[0]}** satisfies (8) with $\\varepsilon=10\\%$, so among the tested rules it is the solution of (13): it delivers {100*best[1]:.0f}% of the planned water in the worst storyline, the {NAME[best[3]]}, where the exceedance share is {100*best[2]:.1f}%. ')
A('To tighten to $\\varepsilon=5\\%$ the binding storyline is the causal change, so the next lever is the cap $H_{\\max}$ on private abstraction in a declared drought, or a lower $u_{\\mathrm{dec}}$; the objective (13) tells how much water each costs.\n')
SHP = '/home/user/swi-goal-oed/experiments/spiranca_go/res/sh.json'
if os.path.exists(SHP):
    import sys
    sys.path.insert(0, '/home/user/swi-goal-oed/experiments/spiranca_go')
    import sh_figs as HF
    SH = HF.summary(); CF = HF.CF; NAq = len(HF.rows)
    def lab(c):
        u, h = c.split('_'); u = u[1:]; h = h[1:]
        return (f'Cap $H_{{\\max}}={float(h):.2f}$' if h != 'none' else ('No cap (as in Section 6)' if u == '0.3' else 'No cap')) + f', $u_{{\\mathrm{{dec}}}}={u}$'
    A('## 7. The cap on private abstraction for $\\varepsilon=5\\%$\n')
    A('A drought is declared when the two-year filtered gauge anomaly known at the start of the season, $\\tilde r^{g}_{t-1}$, is below $-1$ sd. While it lasts, private abstraction is capped:\n')
    A('$$H_t=\\overline{H}\\,\\min(h_{\\xi,t},H_{\\max})\\quad\\text{if}\\ \\tilde r^{g}_{t-1}<-1,\\qquad H_t=\\overline{H}\\,h_{\\xi,t}\\quad\\text{otherwise}\\qquad(15)$$\n')
    A('$H_{\\max}=1$ lets the farmers pump their normal mean in a drought, but not more; without a cap they pump about 1.5 times it in the record drought and 2.5 times under the causal change. The other lever, a lower decided pumping $u_{\\mathrm{dec}}$, is tested for comparison. Everything runs with ROJA-GO and the rule (10). Water is given as the share of what each user would have pumped without the measure, in the worst storyline.\n')
    A(f'Table 3. The measures on {NAq} aquifers, {HF.D["ntraj"]} weather sequences each, five storylines, 30 years after the decision.\n')
    A('| Measure | Worst-storyline exceedance | Aquifers above 5% | Utility water | Farmers\' water | Total water | Seasons declared (ordinary / drought) | Meets $\\varepsilon=5\\%$ |')
    A('|---|---|---|---|---|---|---|---|')
    for c in CF:
        v = SH[c]
        A(f"| {lab(c)} | {100*v['exc']:.1f}% ({NAME[v['exc_sc']]}) | {v['n10']} of {NAq} | {100*v['water']:.1f}% | {100*v['priv']:.1f}% | {100*v['total']:.1f}% | {100*v['decl_none']:.0f}% / {100*v['decl_dry']:.0f}% | {'yes' if v['exc'] <= 0.05 else 'no'} |")
    A('')
    feas = [c for c in CF if SH[c]['exc'] <= 0.05]
    capf = [c for c in feas if not c.endswith('Hnone')]
    uf = [c for c in feas if c.endswith('Hnone')]
    if feas:
        best = max(feas, key=lambda c: SH[c]['total'])
        v = SH[best]
        A(f"**Solution of (13) with $\\varepsilon=5\\%$.** Among the measures that meet the limit in every storyline, the one that keeps the most total water in the worst storyline is **{lab(best)}**: exceedance {100*v['exc']:.1f}% in the worst storyline ({NAME[v['exc_sc']]}), utility water {100*v['water']:.1f}%, farmers' water {100*v['priv']:.1f}%, total {100*v['total']:.1f}%.")
        if capf:
            loosest = max(capf, key=lambda c: float(c.split('_H')[1]))
            A(f" The least restrictive cap that meets 5% is $H_{{\\max}}={float(loosest.split('_H')[1]):.2f}$.")
        if uf:
            ub = max(uf, key=lambda c: SH[c]['total'])
            A(f" Lowering the decided pumping also meets 5% ({lab(ub)}), but it costs utility water in every year, not only in declared droughts: utility water {100*SH[ub]['water']:.1f}% against {100*v['water']:.1f}%.")
        else:
            ul = [c for c in CF if c.endswith('Hnone') and not c.startswith('u0.3')]
            if ul:
                ub = min(ul, key=lambda c: SH[c]['exc'])
                A(f" Lowering the decided pumping alone does not meet 5%: the best tested ({lab(ub)}) leaves {100*SH[ub]['exc']:.1f}% in the {NAME[SH[ub]['exc_sc']]} storyline, because it does not touch the abstraction that the drought and the farmers add.")
        A('\n')
    else:
        best = min(CF, key=lambda c: SH[c]['exc'])
        A(f"No tested measure meets 5% in every storyline; the closest is **{lab(best)}** with {100*SH[best]['exc']:.1f}% ({NAME[SH[best]['exc_sc']]}).\n")
    A('![Figure 1. Each measure in the plane of the constrained objective (13): exceedance in the worst storyline (constraint) against total water delivered in the worst storyline (objective). The best measure is the highest point left of the red line.](/home/user/swi-goal-oed/experiments/spiranca_go/res/figH1_hmax.png){width=14cm}\n')

A('*Caveat:* synthetic aquifers on a 2-D section; $\\lambda_D$, $c_s$ and $\\varepsilon$ are for the stakeholders to set. Code: experiments/spiranca_go/sx_run.py and sh_run.py; results res/sx.json and res/sh.json.')

mdp = os.path.join(HERE, 'objective.md')
open(mdp, 'w').write('\n'.join(md))
raw = os.path.join(HERE, 'objective_raw.docx')
subprocess.run(['pandoc', mdp, '-o', raw], check=True)

doc = Document(raw)
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
st = {x.name: x for x in doc.styles}
for nm, size in (('Normal', 12), ('Body Text', 12), ('First Paragraph', 12), ('Compact', 10.5), ('Image Caption', 10.5)):
    if nm in st: st[nm].font.size = Pt(size); st[nm].font.name = 'Calibri'
for nm, size, col in (('Title', 21, '1F3864'), ('Subtitle', 13, '2E5597'), ('Heading 2', 15, '1F3864')):
    if nm in st: st[nm].font.size = Pt(size); st[nm].font.color.rgb = RGBColor.from_string(col); st[nm].font.name = 'Calibri'
for t in doc.tables:
    b = OxmlElement('w:tblBorders')
    for e in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement(f'w:{e}'); el.set(qn('w:val'), 'single'); el.set(qn('w:sz'), '4'); el.set(qn('w:color'), '9DB2D6'); b.append(el)
    t._tbl.tblPr.append(b)
    for i, row in enumerate(t.rows):
        for c in row.cells:
            for p in c.paragraphs:
                for rn in p.runs:
                    rn.font.size = Pt(10.5)
                    if i == 0: rn.font.bold = True
            if i == 0:
                sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:fill'), 'DCE6F2'); c._tc.get_or_add_tcPr().append(sh)
out = os.path.join(HERE, 'Objective_Function_Stakeholder_Decision_Under_Extremes.docx')

# image widths (pandoc caps them at the portrait text width)
_W = [15.0]
for _i, _shp in enumerate(doc.inline_shapes):
    _w = _W[min(_i, len(_W) - 1)]
    _r = _shp.height / _shp.width
    _shp.width = Cm(_w); _shp.height = Cm(_w * _r)
doc.save(out)
print(out, best)
