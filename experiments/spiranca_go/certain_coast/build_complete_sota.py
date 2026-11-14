"""CERTAIN-COAST: the complete state of the art, one Word document with every paper of the author's state-of-the-art
series (reviews I-IX), the stakeholder review (all thirty papers), the review of dynamic data assimilation for missing
dynamics, reviews X and XI, the state of the art of the proposal and the review of networks that are optimal today.
Each paper is set in the author's card format: a header table (citation, link, affiliation, topic), "Summary.",
"Link to the anchor paper and to seawater intrusion" with the section it belongs to, "INNOVATION" and the step
CERTAIN-COAST takes beyond it. Each section opens with the equations of the author's MATLAB code (certain-coast) that
carry the method of that section, in red. Native Word math (pandoc), clickable links.

usage: python build_complete_sota.py OUT.docx
inputs: series cards (complete_sota_cards.py), sota_data.py, netsota_data.py and the JSON files in
        SCRATCH/complete_sota (cards_assimilation.json, cards_X_XI.json) and SCRATCH/matlab_eqs/matlab_equations.json."""
import json
import os
import re
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
from build_sota import run, para, heading, link, shade  # noqa: E402
from build_decisions_drl import box as _box, body, E_mrich  # noqa: E402


def box(doc, title, text, E, **kw):
    """A coloured box whose title never stands alone at the foot of a page and whose row is not split."""
    t = _box(doc, title, text, E, **kw)
    t.rows[0].cells[0].paragraphs[0].paragraph_format.keep_with_next = True
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    return t

SCRATCH = os.environ.get('CC_SCRATCH', '/tmp/claude-0/-home-user-swi-goal-oed/a8e15b43-f375-5d4c-96fe-0c14a3d537f0/'
                                       'scratchpad')
NAVY, BLUE, GREY, GREEN, ORANGE, RED = '1F3864', '2E6DB4', '52606D', '1E8A5A', 'C55A11', 'C00000'
CODE = 'https://github.com/dulianzeqiraj/certain-coast'


from codenames import english  # noqa: E402

GLOSS = re.compile(r'(-GO(?:\*\*)?)\s*\(\*[a-zçë]+\*,\s*[a-z ]+\)')   # "**ORIGIN-GO** (*prejardhja*, provenance)"


def en(t):
    if not isinstance(t, str):
        return t
    t = GLOSS.sub(r'\1', english(t)).replace('{{map}}', '').replace(' (Section 3, Figure )', '')
    t = t.replace('in the case of Figure {{case}}', 'in the simulated case shown in review IX')
    return re.sub(r'\{\{\w+\}\}', '', t)                      # figure tokens of the reviews' own builders


def norm(t):
    return re.sub(r'[^a-z0-9]+', ' ', (t or '').lower()).strip()[:70]


def first_sentence(t):
    t = re.sub(r'\*\*[^*]+\*\*\s*', '', t or '').strip()
    m = re.match(r'(.+?[.!?])(\s|$)', t)
    return m.group(1) if m else t


def links_of(c):
    ls = c.get('links') or []
    out = []
    for x in ls:
        if isinstance(x, (list, tuple)) and len(x) >= 2:
            lab, url = str(x[0]), str(x[1])
            if lab.strip().lower() == 'doi' and 'doi.org/' in url:          # show the DOI itself, as the other cards do
                lab = 'doi:' + url.split('doi.org/', 1)[1]
            elif lab.strip().lower() == 'arxiv' and 'arxiv.org/abs/' in url:
                lab = 'arXiv:' + url.split('arxiv.org/abs/', 1)[1]
            out.append((lab, url))
    return out


# ------------------------------------------------------------------------------------------------ the sections
SECTIONS = [
    ('asm', 'Dynamic data assimilation for missing dynamics',
     'How a known model is completed by a learned error term while the state is estimated from partial, noisy data: '
     'the approximation theory of the model error, the mean-field limit of ensemble Kalman methods, transport, '
     'particle and variational filters, robust filtering and the completion of computational graphs. This is the '
     'mathematical engine of the data assimilation of CERTAIN-COAST (WP2).', ['+recharge', '+model']),
    ('rain', 'Inputs, dispersion and boundary conditions from rain, with guarantees',
     'What can be learned about the recharge, the dispersion and the boundaries that nobody measures from rain, heads '
     'and a few chloride profiles, and with which guarantee (reviews I–III).', ['+boundary']),
    ('sbc', 'Stochastic boundary conditions and their deterministic approximation',
     'Partial differential equations whose boundaries are random (noisy sea level and river stage on Dirichlet or Robin '
     'boundaries, recharge and lateral inflow on Neumann boundaries) and how closely deterministic boundary conditions '
     'can stand in for them: random boundaries that become deterministic in a limit, averaging of fast random '
     'coefficients, effective and learned boundary conditions, and a ladder of seven deterministic approximations for '
     'a coastal aquifer.', []),
    ('drift', 'When the simulator is wrong or drifts: anchors, horizons and the floor',
     'Guarantees that survive a wrong simulator, a drifting climate and a long forecast horizon, and the floor below '
     'which no valid band can go (reviews IV–VI).', ['+alarms']),
    ('transfer', 'Transferring the model between sites',
     'When a model built where the aquifer is monitored can be carried to another coast with other characteristics: '
     'causal transportability, doubly and triply robust transfer, exact asymptotics of transfer, distributionally '
     'robust optimisation with optimal transport and transfer across many sites; the question behind carrying '
     'CERTAIN-COAST from the Albanian coast to the east coast of Qatar (WP6).', []),
    ('cf', 'Counterfactuals and the hidden causes of salinity',
     'What the salinity would have been under another recharge or pumping, and how hidden causes such as an unrecorded '
     'drought demand are kept out of the effect of pumping (reviews VII–IX).', []),
    ('causal', 'Causal inference and causal discovery with optimization',
     'Identification, impossibility results, optimal rates and consistent combinatorial algorithms for causal effects, '
     'and causal discovery by optimization with latent confounders, cycles and instrument validity: the tools that '
     'separate the effect of pumping on salinity from what merely accompanies it.', []),
    ('kauz', 'Causality under chaos and a monitoring network for the causal effect of pumping',
     'Structural causal models, potential outcomes, Granger causality and transfer entropy, Takens embedding, linear '
     'response and the fluctuation–dissipation theorem, kernel tests and structure discovery when the data come from '
     'chaotic dynamics; and CAUSAL-OED, a monitoring network designed for the causal effect of pumping, which corrects '
     'for hidden nodes and turns to interventional tests where chaos defeats observational data.', []),
    ('voi', 'The value of information without a prior',
     'The non-Bayesian value of information: comparison of experiments, the risk and regret of Wald, ambiguity, '
     'out-of-sample guarantees and anytime-valid testing; what a piezometer is worth when no one prior is agreed, and '
     'how a salinity alarm keeps its error rate however often the data are looked at.', []),
    ('net', 'The monitoring network: designed for the warnings, kept optimal in time',
     'Sensor placement that corrects its own interference, robust and certified design, and networks that must change '
     'as the coast changes (review X and the review of networks that are optimal today).', ['+network']),
    ('between', 'Warnings between samples',
     'Warnings for what happens between laboratory samples: neural jump ODEs, robust neural SDEs and certified bands for '
     'a crossing at any time in the season (review XI).', ['+betweensamples']),
    ('chem', 'Reactions away from equilibrium and modern hydrogeochemistry',
     'Theorem-level mathematics of real reacting systems (stoichiometry and reaction invariants, thermodynamic '
     'consistency, chemical reaction network theory, graphs and the matrix-tree theorem, operators and entropy methods) '
     'and the modern hydrogeochemistry of homogenised reactive transport, electrodiffusion and the electric double '
     'layer, dissolution and precipitation fronts, cation exchange and geochemical inversion, for the mixing zone of a '
     'coastal aquifer.', []),
    ('stake', 'Stakeholder decisions when the source of the chloride is unknown',
     'All thirty papers of the stakeholder review: how water utilities, regulators and users decide when the chloride '
     'may come from the sea, deep brine, drought or return flow, and how the decision is kept safe for every source '
     'that the evidence cannot exclude.', []),
    ('sota', 'Coastal hazards and certified warnings: the state of the art of the proposal',
     'The thirty-two key papers on subsidence and relative sea level, extreme sea levels and ports, liquefaction, '
     'continuous sensing, the mathematics of certified warning and causal structure, as in the proposal.', []),
]
SECNUM = {k: j + 1 for j, (k, _, _, _) in enumerate(SECTIONS)}
N_ALL = len(SECTIONS) + 1                 # the closing section: all the innovations

# the reviews added last: (file key, section, label if the file gives none)
NEW_REVIEWS = [
    ('SBC', 'sbc', 'Stochastic boundary conditions in PDE systems and their deterministic approximation'),
    ('TRANSFER', 'transfer', 'Transferring models between sites under distribution shift'),
    ('INF', 'causal', 'Causal inference with a mathematical and algorithmic emphasis'),
    ('ZBUL', 'causal', 'Discovering causal models with optimization: latent confounders, cycles and instrument validity'),
    ('KAUZ', 'kauz', 'When causality meets data under chaos'),
    ('VOI', 'voi', 'The value of information without a prior'),
    ('NEQ', 'chem', 'Reactions away from equilibrium in hydrogeochemistry: theorems, algebra and operators'),
    ('HGK', 'chem', 'Modern hydrogeochemistry with advanced mathematics'),
]
INNOV = {}            # review label -> (file key, the review's own innovation), set as a block with its equations in red

FIELD_LABELS = [('inputs', 'Inputs'), ('dispersion', 'Dispersion'), ('bcs', 'Boundary conditions'),
                ('source', 'Source of the chloride'), ('demand', 'Demand'), ('stake', 'Stakeholders')]


def split_first(t):
    """(first sentence, the rest) of a summary, bold labels removed; the rest is '' for a one-sentence summary."""
    t = re.sub(r'\*\*[^*]+\*\*\s*', '', t or '').strip()
    m = re.match(r'(.+?[.!?])\s+(\S.*)$', t, re.S)
    return (m.group(1), m.group(2)) if m else (t, '')


def norm_series(c, review):
    link_parts = []
    for k, lab in FIELD_LABELS:
        if c.get(k):
            link_parts.append(f'**{lab}.** {c[k]}')
    summary, innovation = c.get('does', ''), c.get('sota')
    if not innovation:                         # no innovation field: the first sentence states it, the rest summarises
        innovation, rest = split_first(summary)
        summary = rest or summary
    return dict(title=c['title'], authors=c.get('authors', ''), year=str(c.get('year', '')), venue=c.get('venue', ''),
                links=links_of(c), evidence=c.get('evidence', ''), short=c.get('short', ''), review=review,
                inst=c.get('inst', ''), summary=summary, innovation=innovation,
                link=' '.join(link_parts), gap=c.get('gap', ''), step=c.get('step', ''), extra=c.get('novel', ''),
                eqs=[])


def norm_json(c, review):
    eqs = [(c['eq'], 'the key equation of the paper:')] if c.get('eq') else []
    summary, innovation = c.get('does', ''), c.get('sota') or c.get('innovation')
    if not innovation:
        innovation, rest = split_first(summary)
        summary = rest or summary
    return dict(title=c.get('title', ''), authors=c.get('authors', ''), year=str(c.get('year', '')),
                venue=c.get('venue', ''), links=links_of(c), evidence=c.get('evidence', ''), short=c.get('short', ''),
                review=review, inst=c.get('inst', ''), summary=summary,
                innovation=innovation, link=c.get('link', ''), gap=c.get('gap', ''),
                step=c.get('step', ''), extra='', eqs=eqs)


def norm_cite(it, review, kind):
    m = re.match(r'(.+?)\s\((\d{4})[a-z]?\)\.\s*(.+?)\.\s(.+)$', it['cite'])
    authors, year, title, venue = (m.group(1), m.group(2), m.group(3), m.group(4)) if m else ('', '', it['cite'], '')
    links = [(it['doi'].replace('https://', ''), it['doi'])]
    if it.get('free') and it.get('free') != it.get('doi'):
        links.append((it.get('free_label', 'free copy'), it['free']))
    if kind == 'net':
        return dict(title=title, authors=authors, year=year, venue=venue, links=links, evidence=it['inst'],
                    short='', review=review, inst=it['inst'], summary=it['done'],
                    innovation=it.get('theorem') or first_sentence(it['done']), link=it.get('gap', ''), gap='',
                    step=it.get('beyond', ''), extra='', eqs=list(it.get('math', [])))
    from sota_innovations import INNOV
    return dict(title=title, authors=authors, year=year, venue=venue, links=links, evidence=it['inst'], short='',
                review=review, inst=it['inst'], summary=it['done'],
                innovation=INNOV.get(it.get('n')) or first_sentence(it['done']), link='',
                gap='', step=it.get('beyond', ''), extra='', eqs=[])


NOVELTY = {}          # review label -> its "what is new" paragraphs


def gather():
    """Section -> list of normalised cards, in the order of the document."""
    sec = {s[0]: [] for s in SECTIONS}
    p = os.path.join(SCRATCH, 'complete_sota', 'cards_assimilation.json')
    if os.path.exists(p):
        A = json.load(open(p, encoding='utf-8'))
        order = {c.get('id'): j + 1 for j, c in enumerate(A)}       # A1..A20 -> [1]..[20], the numbers of Section 1

        def renum(t):
            if not isinstance(t, str):
                return t
            parts = t.split('$')
            for j in range(0, len(parts), 2):                     # outside inline math only
                parts[j] = re.sub(r'\bA(\d{1,2})\b', lambda m: f'[{order.get("A" + m.group(1), m.group(1))}]'
                                  if 'A' + m.group(1) in order else m.group(0), parts[j])
            return '$'.join(parts)

        for c in A:
            c = {k: (renum(v) if k not in ('id', 'links', 'title', 'eq') else v) for k, v in c.items()}
            sec['asm'].append(norm_json(c, 'Dynamic data assimilation for missing dynamics (20 papers)'))
    S = json.load(open(os.path.join(SCRATCH, 'complete_sota', 'series_cards.json'), encoding='utf-8'))
    where = {'I': 'rain', 'II': 'rain', 'III': 'rain', 'IV': 'drift', 'V': 'drift', 'VI': 'drift', 'VII': 'cf',
             'VIII': 'cf', 'IX': 'cf', 'S': 'stake'}
    for k in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'S']:
        lab = (f'Review {k}: ' if k != 'S' else 'Stakeholder review: ') + S[k]['title']
        NOVELTY[en(lab)] = [en(x) for x in S[k].get('novelty', [])]
        for c in S[k]['cards']:
            sec[where[k]].append(norm_series(c, lab))
    p = os.path.join(SCRATCH, 'complete_sota', 'cards_X_XI.json')
    if os.path.exists(p):
        import xxi_novelty as XN
        J = json.load(open(p, encoding='utf-8'))
        lx = 'Review X: placing sensors that interfere (INTERVENTION-GO)'
        lxi = 'Review XI: warnings for what happens between samples (PATH-GO)'
        if J.get('X'):
            NOVELTY[lx] = [XN.X]
        if J.get('XI'):
            NOVELTY[lxi] = [XN.XI]
        for rk, key, lab in (('X', 'net', lx), ('XI', 'between', lxi)):
            for c in J.get(rk, []):
                if rk == 'X':
                    c = {f: (fix_x(v) if f not in ('id', 'links', 'title', 'eq') else v) for f, v in c.items()}
                d = norm_json(c, lab)
                d['_rk'], d['_rid'] = rk, c.get('id')
                sec[key].append(d)
    import netsota_data as ND
    for _, items in ND.GROUPS:
        for it in items:
            sec['net'].append(norm_cite(it, 'Networks that are optimal today and not tomorrow (20 papers)', 'net'))
    import sota_data as SD
    for _, items in SD.GROUPS:
        for it in items:
            sec['sota'].append(norm_cite(it, 'State of the art of the proposal (32 papers)', 'sota'))
    for key, where_to, fallback in NEW_REVIEWS:       # the reviews added last, each with its own innovation
        p = os.path.join(SCRATCH, 'complete_sota', f'cards_{key}.json')
        if not os.path.exists(p):
            continue
        J = json.load(open(p, encoding='utf-8'))
        inv = J.get('innovation') or {}
        lab = en(inv.get('label') or fallback)
        if inv.get('name') and inv['name'] not in lab:
            lab = f'{lab} ({en(inv["name"])})'
        if inv:
            INNOV[lab] = (key, inv)
        for c in J.get('cards', []):
            d = norm_json(c, lab)
            d['_rk'], d['_rid'] = key, c.get('id')
            sec[where_to].append(d)
    for k in sec:                                     # English names of the preparatory experiments
        for c in sec[k]:
            for f in ('title', 'summary', 'innovation', 'link', 'gap', 'step', 'extra', 'review', 'evidence', 'short'):
                c[f] = en(c.get(f, ''))
    # one full card per paper; a later occurrence becomes a cross-reference
    seen, n = {}, 0
    for k, _, _, _ in SECTIONS:
        for c in sec[k]:
            key = norm(c['title'])
            if key in seen:
                c['dup_of'] = seen[key]
            else:
                n += 1
                c['n'] = n
                seen[key] = (n, k)
    # reviews X, XI and the reviews added last cite their papers by labels (A1, R8, O5, BK2, T6): the card numbers
    idmap = {(c['_rk'], c['_rid']): (c['dup_of'][0] if c.get('dup_of') else c['n'])
             for k in sec for c in sec[k] if c.get('_rk') and c.get('_rid')}
    ids = {}
    for rk, rid in idmap:
        ids.setdefault(rk, []).append(rid)
    pats = {rk: re.compile(r'\[?\b(' + '|'.join(re.escape(x) for x in sorted(v, key=len, reverse=True)) + r')\b\]?')
            for rk, v in ids.items()}

    def renum(t, rk):
        if not isinstance(t, str) or rk not in pats:
            return t
        parts = t.split('$')
        for j in range(0, len(parts), 2):
            parts[j] = pats[rk].sub(lambda m: f'[{idmap[(rk, m.group(1))]}]', parts[j])
        return '$'.join(parts)

    for k in sec:
        for c in sec[k]:
            if c.get('_rk'):
                for f in ('summary', 'innovation', 'link', 'gap', 'step', 'extra'):
                    c[f] = renum(c.get(f, ''), c['_rk'])
    for lab, (rk, inv) in INNOV.items():
        for f in ('title', 'intro', 'in_cc', 'short'):
            inv[f] = en(renum(inv.get(f, ''), rk))
        for it in inv.get('items', []):
            for f in ('title', 'before', 'after'):
                it[f] = en(renum(it.get(f, ''), rk))
    return sec


def fix_x(t):
    """Review X: its Propositions N1-N4 named as review X's (Section 1.1 has its own N1-N3), and the Certified OED
    framework (A2 in the review, not a paper card) named."""
    if not isinstance(t, str):
        return t
    parts = t.split('$')
    for j in range(0, len(parts), 2):
        q = parts[j]
        q = re.sub(r'(Propositions? N\d(?:\([a-z]\))?(?:(?:–| and |, )N\d(?:\([a-z]\))?)*)', r'\1 of review X', q)
        q = re.sub(r'\s*\(A2\)', '', q)
        q = re.sub(r'\bof A2\b', 'of the Certified OED framework', q)
        q = re.sub(r'\bA2\b', 'the Certified OED framework', q)
        parts[j] = q
    return '$'.join(parts)


def _vlen(t):
    """Rough printed width of a LaTeX string, in characters."""
    t = re.sub(r'\\(left|right|big|Big|bigg|Bigg|mathrm|mathcal|boldsymbol|operatorname|text|tfrac|dfrac|frac)\b', '', t)
    t = re.sub(r'\\[a-zA-Z]+', 'x', t)
    return len(re.sub(r'[{}^_\s]|\\[,;:! ]', '', t))


def _top_splits(tex, sep):
    """Pieces of tex cut at each occurrence of the command sep that stands outside braces, environments and
    \\left...\\right pairs."""
    out, depth, start, i = [], 0, 0, 0
    while i < len(tex):
        ch = tex[i]
        if ch == '\\':
            m = re.match(r'\\([a-zA-Z]+|.)', tex[i:])
            name = m.group(1)
            if name in ('begin', 'left'):
                depth += 1
            elif name in ('end', 'right'):
                depth -= 1
            elif name == sep and depth == 0:
                out.append(tex[start:i].strip())
                start = i + len(m.group(0))
            i += len(m.group(0))
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        i += 1
    out.append(tex[start:].strip())
    return [p for p in out if p]


def split_long(tex, limit=72, first=80):
    """A long display equation as several lines, cut at its top-level \\qquad (then \\quad) and packed greedily."""
    if not isinstance(tex, str) or _vlen(tex) <= first:
        return tex
    for sep in ('qquad', 'quad'):
        parts = _top_splits(tex, sep)
        if len(parts) < 2:
            continue
        lines, cur = [], ''
        for p in parts:
            cand = (cur + r'\qquad ' + p) if cur else p
            if cur and _vlen(cand) > limit:
                lines.append(cur)
                cur = p
            else:
                cur = cand
        lines.append(cur)
        if len(lines) > 1:
            return lines
    return tex


def deq(doc, E, tex, number):
    from build_gar_doc import display_eq
    display_eq(doc, E, split_long(tex), number)


def matlab_items():
    p = os.path.join(SCRATCH, 'matlab_eqs', 'matlab_equations.json')
    if not os.path.exists(p):
        return []
    items = json.load(open(p, encoding='utf-8')).get('items', [])

    def plain(t):                                  # code-style text: no markdown markers, readable relations
        t = (t or '').replace('*', '·').replace('<=', '≤').replace('>=', '≥').replace('+-', '±')
        return t.replace('$', '')

    for it in items:
        it['purpose'] = plain(it.get('purpose', ''))
        for e in it.get('equations', []):
            e['what'] = plain(e.get('what', ''))
    return items


def kv_table(doc, rows, E):
    t = doc.add_table(rows=0, cols=2)
    t.autofit = False
    tblPr = t._tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for side in ('top', 'bottom', 'insideH'):
        e = OxmlElement(f'w:{side}')
        e.set(qn('w:val'), 'single')
        e.set(qn('w:sz'), '4')
        e.set(qn('w:color'), 'C9D3E0')
        b.append(e)
    tblPr.append(b)
    lay = OxmlElement('w:tblLayout')
    lay.set(qn('w:type'), 'fixed')
    tblPr.append(lay)
    for k, v in rows:
        c0, c1 = t.add_row().cells
        c0.width, c1.width = Cm(3.2), Cm(13.8)
        shade(c0, 'F3F6FA')
        q = c0.paragraphs[0]
        q.paragraph_format.space_after = Pt(1)
        run(q, k, bold=True, size=8.5, color=GREY)
        q = c1.paragraphs[0]
        q.paragraph_format.space_after = Pt(1)
        if isinstance(v, list):
            for j, (lab, url) in enumerate(v):
                if j:
                    run(q, '  ·  ', size=8.5, color=GREY)
                link(q, url, lab, 8.5)
        else:
            E_mrich(q, v, E, size=8.5)
    grid = t._tbl.tblGrid
    for gc, w in zip(grid.findall(qn('w:gridCol')), (3.2, 13.8)):
        gc.set(qn('w:w'), str(int(w * 567)))
    for row in t.rows:
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    para(doc, 2)


def labelled(doc, label, text, E, color, size=10):
    if not text:
        return
    q = para(doc, 3)
    q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run(q, label + ' ', bold=True, size=size, color=color)
    E_mrich(q, text, E, size=size)


def card(doc, c, sec_no, E, display_eq, num):
    if c.get('dup_of'):
        n0, s0 = c['dup_of']
        q = para(doc, 4, before=4)
        run(q, c['title'] + ' ', bold=True, size=10, color=NAVY)
        run(q, f'— see [{n0}] in Section {SECNUM[s0]}; it also belongs here ({c["review"]}).', italic=True, size=9.5,
            color=GREY)
        return
    p = para(doc, 2, before=8)
    p.paragraph_format.keep_with_next = True
    run(p, f'[{c["n"]}]  ', bold=True, size=11, color=NAVY)
    run(p, c['title'], bold=True, size=11, color=NAVY)
    cite = ', '.join(x for x in [c['authors'], f'({c["year"]})' if c['year'] else '', c['venue']] if x)
    rows = [('Citation', cite), ('DOI / link', c['links'] or c.get('evidence', '')), ('Affiliation', c['evidence']),
            ('Topic', ' · '.join(x for x in [c.get('short', ''), c['review']] if x))]
    kv_table(doc, [(k, v) for k, v in rows if v], E)
    labelled(doc, 'Summary.', c['summary'], E, NAVY)
    for tex, what in c.get('eqs', []):
        q = para(doc, 0)
        q.paragraph_format.keep_with_next = True
        run(q, 'Mathematics: ', bold=True, size=10, color=BLUE)
        E_mrich(q, what, E, size=10)
        num[0] += 1
        deq(doc, E, tex, num[0])
    lk = ' '.join(x for x in [c['link'], (f'**What it leaves open.** {c["gap"]}' if c['gap'] else '')] if x)
    labelled(doc, f'Link to the anchor paper and to seawater intrusion. Belongs to Section {sec_no}.', lk, E, BLUE)
    q = para(doc, 3)
    q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run(q, 'INNOVATION  ', bold=True, size=10, color=ORANGE)
    E_mrich(q, c['innovation'], E, size=10)
    labelled(doc, 'Step in CERTAIN-COAST.', ' '.join(x for x in [c['step'], c['extra']] if x), E, GREEN)


def asm_block(doc, E, num, red):
    """Section 1.1: the innovation of the data assimilation review (N1-N3), equations in red."""
    import asm_novelty as A
    heading(doc, f'{SECNUM["asm"]}.1 ' + A.TITLE, 12, color=RED, before=8)
    body(doc, A.INTRO, E, size=10.5)
    for title, before, tex, after in A.PROPOSALS:
        q = para(doc, 2, before=6)
        q.paragraph_format.keep_with_next = True
        run(q, title, bold=True, size=10.5, color=ORANGE)
        for txt in (before, None, after):
            if txt is None:
                num[0] += 1
                red.append(num[0])
                deq(doc, E, tex, num[0])
                continue
            q = para(doc, 3)
            q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            E_mrich(q, txt, E, size=10)
    box(doc, 'In CERTAIN-COAST', A.IN_CC.replace('(Section 6.0)', f'(Section {SECNUM["between"]}.0)'), E,
        fill='FDF3EA', bar=ORANGE)


def innov_block(doc, E, num, red, inv):
    """The innovation of one of the reviews added last, as the review states it; its equations in red."""
    heading(doc, inv.get('title') or 'What is new', 11.5, color=RED, before=6)
    if inv.get('intro'):
        body(doc, inv['intro'], E, size=10.5)
    for it in inv.get('items', []):
        if it.get('title'):
            q = para(doc, 2, before=6)
            q.paragraph_format.keep_with_next = True
            run(q, it['title'], bold=True, size=10.5, color=ORANGE)
        if it.get('before'):
            q = para(doc, 3)
            q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            E_mrich(q, it['before'], E, size=10)
        if it.get('tex'):
            num[0] += 1
            red.append(num[0])
            deq(doc, E, it['tex'], num[0])
        if it.get('after'):
            q = para(doc, 3)
            q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            E_mrich(q, it['after'], E, size=10)
    if inv.get('in_cc'):
        box(doc, 'In CERTAIN-COAST', inv['in_cc'], E, fill='FDF3EA', bar=ORANGE)


def all_innovations(doc, E, sec):
    """The closing section: every innovation of CERTAIN-COAST, with the result that tested it."""
    import sota_data as SD
    import netsota_data as ND
    from build_additional_word import NEW
    h = heading(doc, f'{N_ALL}. All the innovations of CERTAIN-COAST', 16, before=6)
    h.paragraph_format.page_break_before = True
    body(doc, 'This section gathers every innovation of the proposal and of its preparatory work in one place: the '
              'innovations of the proposal itself, those of each review of the state-of-the-art series with the test '
              'that supports it, and those of the technical notes and parts of the additional files. The equations '
              'new in this proposal are the red equations at the head of each section.', E, size=10.5)
    heading(doc, f'{N_ALL}.1 The innovations of the proposal', 12, color=BLUE, before=6)
    for t, items in SD.SECTIONS:
        if t.startswith('4.'):
            for kind, v in items:
                if kind == 'h':
                    heading(doc, v, 11, color=NAVY, before=6)
                elif kind == 'b':
                    q = para(doc, 3, 0.5)
                    q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    q.paragraph_format.first_line_indent = Cm(-0.4)
                    run(q, '•  ', bold=True, size=10, color=ORANGE)
                    E_mrich(q, en(v), E, size=10)
    heading(doc, f'{N_ALL}.2 The innovations of the state-of-the-art series', 12, color=BLUE, before=8)
    import asm_novelty as A
    q = para(doc, 2, before=4)
    run(q, f'Dynamic data assimilation for missing dynamics (Section {SECNUM["asm"]}.1)', bold=True, size=10.5,
        color=NAVY)
    q = para(doc, 3, 0.4)
    q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    E_mrich(q, A.SHORT, E, size=10)
    for r, txts in NOVELTY.items():
        if txts:
            q = para(doc, 2, before=4)
            run(q, r, bold=True, size=10.5, color=NAVY)
            for txt in txts[:1]:
                q = para(doc, 3, 0.4)
                q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                E_mrich(q, txt, E, size=10)
    for lab, (rk, inv) in INNOV.items():
        if inv.get('short'):
            q = para(doc, 2, before=4)
            run(q, lab, bold=True, size=10.5, color=NAVY)
            q = para(doc, 3, 0.4)
            q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            E_mrich(q, inv['short'], E, size=10)
    heading(doc, f'{N_ALL}.3 The innovations of the technical notes and parts', 12, color=BLUE, before=8)
    for name, part, text in NEW:
        q = para(doc, 3, 0.4)
        q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run(q, f'{en(name)} (Part {part} of the additional files). ', bold=True, size=10, color=ORANGE)
        E_mrich(q, en(text), E, size=10)
    q = para(doc, 3, 0.4)
    q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run(q, 'Network lifetime (review of networks that are optimal today). ', bold=True, size=10, color=ORANGE)
    E_mrich(q, ND.INNOVATION, E, size=10)


def main(out):
    from build_gar_doc import Eqs, display_eq
    import omml
    import polish_parts as PP
    E = Eqs()
    BS._EQ = E
    global N_ALL
    sec = gather()
    active = [t for t in SECTIONS if sec[t[0]]]             # a review whose cards are not there yet leaves no section
    SECNUM.clear()
    SECNUM.update({k: j + 1 for j, (k, _, _, _) in enumerate(active)})
    N_ALL = len(active) + 1
    M = matlab_items()
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0)
    s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']
    st.font.name = 'Arial'
    st.font.size = Pt(10.5)
    num, red = [0], []
    n_full = sum(1 for k in sec for c in sec[k] if not c.get('dup_of'))

    p = para(doc, 2, before=40)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'CERTAIN-COAST — The complete state of the art', bold=True, size=22, color=NAVY)
    p = para(doc, 6)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    years = [int(c['year'][:4]) for k in sec for c in sec[k] if not c.get('dup_of') and c['year'][:4].isdigit()]
    n_old = sum(1 for y in years if y < 2020)
    span = (f'{n_full} papers ({n_full - n_old} of 2020–2026 and {n_old} earlier works that the reviews build on)'
            if n_old else f'{n_full} papers of 2020–2026')
    run(p, f'{span} from the author\'s state-of-the-art series, each with its summary, its link '
           f'to the anchor and to seawater intrusion, its innovation and the step CERTAIN-COAST takes beyond it; the '
           f'equations of the author\'s MATLAB code in red', bold=True, size=12, color=NAVY)
    p = para(doc, 18)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Prof. Asoc. Dr. Dulian Zeqiraj · Faculty of Geology and Mining, Polytechnic University of Tirana · '
           'November 2026', italic=True, size=10, color=GREY)
    box(doc, 'How to read this document',
        'The anchor is CERTAIN-COAST itself: a coupled model of the coast whose warnings for seawater intrusion, '
        'liquefaction and extreme sea levels carry a stated miss rate, written as open-source MATLAB code '
        f'([{CODE.replace("https://", "")}]({CODE})). Each section opens with the equations of that code which carry '
        'the method of the section, in red, with the file they come from; then each paper follows in the same card: '
        'the header table, the summary, the link to the anchor and to seawater intrusion, the innovation of the paper '
        'and the step CERTAIN-COAST takes beyond it. A paper met in more than one review has one full card and a '
        'cross-reference where it appears again.', E)
    heading(doc, 'Contents', 14)
    for k, t, _, _ in active:
        n_k = sum(1 for c in sec[k] if not c.get('dup_of'))
        q = para(doc, 2)
        run(q, f'{SECNUM[k]}.  {t}', bold=True, size=10.5, color=NAVY)
        run(q, f'   ({n_k} papers)', size=10, color=GREY)
    q = para(doc, 2)
    run(q, f'{N_ALL}.  All the innovations of CERTAIN-COAST', bold=True, size=10.5, color=ORANGE)

    for k, t, intro, pkgs in active:
        h = heading(doc, f'{SECNUM[k]}. {t}', 16, before=6)
        h.paragraph_format.page_break_before = True
        body(doc, intro, E, size=10.5)
        mine = [it for it in M if any(f'/{pk}/' in it.get('file', '') or it.get('file', '').startswith(pk + '/')
                                      for pk in pkgs)]
        mine = [it for it in mine if any(e.get('status') == 'new' for e in it.get('equations', []))]
        if mine:
            heading(doc, f'{SECNUM[k]}.0 Our equations in the CERTAIN-COAST MATLAB code', 12, color=RED, before=6)
            body(doc, 'The equations below are those of the open-source MATLAB code of CERTAIN-COAST that are new in this '
                      'work (set in red), each with the file that computes it; the standard equations the same files use '
                      '(least squares, the split-conformal quantile, the Gaussian information gain) are not repeated.',
                 E, size=10)
            for it in mine:
                rel = it.get('file', '').split('certain-coast/')[-1]
                q = para(doc, 1, before=4)
                q.paragraph_format.keep_with_next = True
                link(q, f'{CODE}/blob/main/{rel}', rel, 9.5)
                if it.get('purpose'):
                    run(q, '  ', size=9.5)
                    E_mrich(q, it['purpose'], E, size=9.5)
                for e in it.get('equations', []):
                    if e.get('status') != 'new':
                        continue
                    q = para(doc, 0, 0.4)
                    q.paragraph_format.keep_with_next = True
                    run(q, 'New: ', bold=True, size=9.5, color=RED)
                    E_mrich(q, e.get('what', ''), E, size=9.5)
                    num[0] += 1
                    red.append(num[0])
                    deq(doc, E, e['latex'], num[0])
        if k == 'asm':
            asm_block(doc, E, num, red)
        reviews = []
        for c in sec[k]:
            if c['review'] not in reviews:
                reviews.append(c['review'])
        for r in reviews:
            heading(doc, r, 12, color=BLUE, before=10)
            for j, txt in enumerate(NOVELTY.get(r, [])):
                box(doc, 'What is new in this review' if j == 0 else 'The method', txt, E, fill='FDF3EA', bar=ORANGE)
            if r in INNOV:
                innov_block(doc, E, num, red, INNOV[r][1])
            for c in sec[k]:
                if c['review'] == r:
                    card(doc, c, SECNUM[k], E, display_eq, num)

    all_innovations(doc, E, sec)

    p = para(doc, 4, before=10)
    run(p, 'Verification note. Every card comes from the author\'s reviews, where each reference was checked against '
           'Crossref, arXiv, the proceedings or institutional repositories; the cards of the data assimilation review, '
           'of reviews X and XI and of the eight reviews added last (stochastic boundary conditions, transfer between '
           'sites, causal inference, causal discovery with optimization, causality under chaos, the value of information '
           'without a prior, reactions away from equilibrium and modern hydrogeochemistry) were translated or extracted from those reviews and their '
           'references checked again in Crossref in November 2026. The equations in red were checked against the MATLAB '
           'code of the package or are the author\'s own proposals as the reviews state them. The document was assembled '
           'with the help of an AI assistant.', italic=True, size=9, color=GREY)

    BS._EQ = None
    work = tempfile.mkdtemp()
    draft = os.path.join(work, 'draft.docx')
    doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh)
    omml.main(draft, eq_json, out)
    PP.RED[98] = red
    d = Document(out)
    n_red, _ = PP.colour_equations(list(d.element.body), 98)
    d.core_properties.title = 'CERTAIN-COAST: the complete state of the art'
    d.core_properties.author = 'Dulian Zeqiraj'
    d.save(out)
    print('saved', out, '|', n_full, 'papers |', len(E.items), 'equations |', n_red, 'in red')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Complete_State_of_the_Art.docx')
