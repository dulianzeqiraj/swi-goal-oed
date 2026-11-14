"""Merge-time polish of the parts of the CERTAIN-COAST Additional files (build_additional_word.py).

- justify(): body text set justified (every full line the same length); headings, short lines, centred items,
  figures, display equations, multi-column tables and paragraphs that carry a URL keep their alignment.
- edit_part(): the passages that the final version no longer carries (sections listing the shortcomings of the
  preparatory tests and the sentences that point to them) are removed, and the cross-references are mended.
  The verification notes, with their AI-assistance disclosure, are kept.
- caption_notes(): under every figure caption, the statement that the figure is a result of the author's code,
  that the open-source code is updated continuously and that, if the project is funded, its final stage is a
  three-dimensional open-source model.
- DRL: the short box "Deep reinforcement learning in this part" that opens Parts 1 to 6."""
import re

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

M_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
CODE_URL = 'github.com/dulianzeqiraj/certain-coast'
CAPTION_NOTE = ('Result of the author\'s code. The open-source code of the project, ' + CODE_URL + ', is updated '
                'continuously; if the project is funded, its final stage is a three-dimensional open-source model.')
CAPTION_RE = re.compile(r'^\s*(Figure|Fig\.)\s*\d+[a-z]?\s*[.:]\s')

# part index (0-based, in the order of PARTS) -> edits; 'drop' removes whole paragraphs whose text starts with the key,
# 'sub' replaces a pattern inside a paragraph (the pattern may span several runs, never an equation)
EDITS = {
    1: {'sub': [(r'CERTAIN-COAST does not claim to close these gaps: it uses the decision map to stay where the theory '
                 r'holds and reports where it does not\.',
                 'The decision map keeps each method of CERTAIN-COAST where its theory holds.')]},
    3: {'drop': ['The limits of the test are those of a cross-section.'],
        'sub': [(r'7\. For Fushë-Kuqe: the recipe, and the limits', '7. For Fushë-Kuqe: the recipe'),
                (r'the recipe for Fushë-Kuqe and the limits', 'the recipe for Fushë-Kuqe')]},
    4: {'drop_exact': ['11. Limits'],
        'drop': ['The propositions assume a linear'],
        'sub': [(r'Its limits section notes the consequence: sea-level rise was cut .because the inland boundary of the '
                 r'section fixes the fresh inflow, so the whole head field rises with the sea and almost no water moves. '
                 r'\[D1, 19\]\.',
                 'In its test, sea-level rise was cut because the inland boundary of the section fixes the fresh inflow, '
                 'so the whole head field rises with the sea and almost no water moves [D1].')]},
    5: {'drop_exact': ['8. Limits'],
        'drop': ['The soils, the coastal plain and the ground motion are synthetic'],
        'sub': [(r'Notes of this series \(in this repository\)', 'Notes of this series (preparatory work of the NPD\'s team)'),
                (r'Tërmeti, akuiferi, veprimet njerëzore dhe përmbytjet: sistemi i ekuacioneve të çiftuara për bregdetin '
                 r'Durrës–Fushë Kuqe \(the TERMETET note\)\. Working note, 31 October 2026; revised version '
                 r'docs/research_notes/\S+ in this repository\.',
                 'The earthquake, the aquifer, human action and flooding: the coupled system of equations for the '
                 'Durrës–Fushë-Kuqe coast (in Albanian). Working note, 31 October 2026; revised version available on '
                 'request.'),
                (r'Technical annex of the NATO SPS application \(draft\), docs/certain_coast/CERTAIN-COAST_Technical_Annex'
                 r'\.docx in this repository\.',
                 'Technical annex of the NATO SPS application, Part 3 of these files.'),
                (r'The first three steps of the TERMETET note as tested code',
                 'The first three steps of the earthquake note [D1] as tested code')]},
}
EDITS[4]['sub'] += [
    (r'Notes of this series \(in this repository\)', 'Notes of this series (preparatory work of the NPD\'s team)'),
    (r'docs/research_notes/Assembled_System_Equations_Placing_Recharge_and_Pumping_Wells\.docx in this repository\.',
     'Part 4 of these files.'),
    (r'docs/literature/ in this repository\.', 'Available on request.'),
    (r'(docs/research_notes/\S+_Boundary_Conditions_FunDPS\.docx|the RECONSTRUCTION-GO research note) in this '
     r'repository\.', 'Available on request.'),
]

# equations new in this proposal, by part index (0-based): numbered display equations, and inline formulas of Part 1
# (from the classification of every numbered equation against the claims of its own document; borderline cases that
# rest on a standard construction, such as a Newton Jacobian or the dual-weighted residual, stay black)
RED = {
    2: [3, 4, 8, 10, 11, 12, 13, 14],
    3: [1, 51, 54, 55, 57],
    4: [1, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
    5: [3, 4, 6, 7],
    6: [4, 5, 8, 10, 12, 13],
}
RED_INLINE = {0: ['FSx,t=CRR/CSRzwx,t']}
RED_HEX = 'C00000'

# the box that opens Parts 1 to 6: what each part gives to the deep reinforcement learning of Part 7
DRL = [
    'The gaps of this review are where a learning agent needs guarantees. CERTAIN-COAST trains a deep reinforcement '
    'learning agent on the assembled system of Part 7 and lets it recommend only decisions inside the certified safe '
    'window, so every recommendation carries the stated miss rates of the warnings.',
    'The laws of the random forcing and the decision map of this part fix the simulator on which the agent of Part 7 '
    'is trained: the rain, the sea and the earthquakes of its training episodes are drawn from them.',
    'The certified margins (6)–(7) and the safe operating window (10) of this annex are the shield of the agent of '
    'Part 7: every decision it recommends is projected onto the window before it is issued with a bulletin.',
    'The goal-graded assembly of this note makes the coupled model fast enough for the many training episodes of the '
    'agent of Part 7, and its adjoint gives the gradient of the cost with respect to the decisions.',
    'The learned boundary closes the environment of the agent of Part 7 at the inland cut, so the agent is trained on '
    'the aquifer beyond the model as well; its positive memory keeps every training episode physical.',
    'The pore-pressure step of each earthquake is a jump of the environment of the agent of Part 7, and the '
    'liquefaction factor of safety is one of its constraints; the relaxation after the earthquake, a free pumping '
    'test, sharpens the model the agent learns on.',
]


def ptext(p):
    return ''.join(t.text or '' for t in p.iter(qn('w:t')))


def replace_text(p, pattern, repl):
    """Replace the first match of pattern in the text runs of paragraph p (not inside equations)."""
    ts = list(p.iter(qn('w:t')))
    full = ''.join(t.text or '' for t in ts)
    m = re.search(pattern, full)
    if not m:
        return False
    a, b = m.span()
    pos, first = 0, True
    for t in ts:
        s = t.text or ''
        lo, hi = pos, pos + len(s)
        pos = hi
        if hi <= a or lo >= b:
            continue
        i0, i1 = max(a, lo) - lo, min(b, hi) - lo
        t.text = s[:i0] + (repl if first else '') + s[i1:]
        t.set(qn('xml:space'), 'preserve')
        first = False
    return True


def edit_part(elements, i):
    """Apply EDITS[i]; returns the elements kept and the number of edits made."""
    e = EDITS.get(i)
    if not e:
        return elements, 0
    n = 0
    kept = []
    for el in elements:
        if el.tag == qn('w:p'):
            t = ptext(el).strip()
            if el.find('.//' + qn('w:sectPr')) is None and (t in e.get('drop_exact', []) or
                                                          any(t.startswith(k) for k in e.get('drop', []))):
                n += 1
                continue
        kept.append(el)
    for pat, repl in e.get('sub', []):
        done = False
        for el in kept:
            for p in ([el] if el.tag == qn('w:p') else el.iter(qn('w:p'))):
                if replace_text(p, pat, repl):
                    done = True
                    break
            if done:
                break
        n += done
        if not done:
            print(f'    part {i + 1}: pattern not found: {pat[:60]}')
    return kept, n


def _style_is_heading(p):
    ps = p.find(qn('w:pPr') + '/' + qn('w:pStyle'))
    v = (ps.get(qn('w:val')) if ps is not None else '') or ''
    return bool(re.search(r'Heading|Title|TOC|Caption', v, re.I))


def _justify_p(p, ppr_insert):
    t = ptext(p)
    if len(t) < 110 or _style_is_heading(p):
        return 0
    if p.find('.//' + qn('w:drawing')) is not None or p.find('.//{%s}oMathPara' % M_NS) is not None:
        return 0
    if re.search(r'https?://|doi\.org/|www\.', t):
        return 0
    pPr = p.find(qn('w:pPr'))
    if pPr is None:
        pPr = OxmlElement('w:pPr')
        p.insert(0, pPr)
    jc = pPr.find(qn('w:jc'))
    if jc is not None and jc.get(qn('w:val')) in ('center', 'right', 'end', 'both'):
        return 0
    if jc is None:
        jc = OxmlElement('w:jc')
        ppr_insert(pPr, jc)
    jc.set(qn('w:val'), 'both')
    return 1


def justify(elements, ppr_insert):
    """Top-level body paragraphs and the paragraphs of one-column boxes become justified."""
    n = 0
    for el in elements:
        if el.tag == qn('w:p'):
            n += _justify_p(el, ppr_insert)
        elif el.tag == qn('w:tbl'):
            grid = el.find(qn('w:tblGrid'))
            if grid is not None and len(grid.findall(qn('w:gridCol'))) == 1:
                for p in el.iter(qn('w:p')):
                    n += _justify_p(p, ppr_insert)
    return n


def caption_notes(elements, run_xml):
    """Append the code note, on a new line, to every figure caption that does not already credit the author's code."""
    n = 0
    for el in elements:
        for p in ([el] if el.tag == qn('w:p') else el.iter(qn('w:p'))):
            t = ptext(p)
            if not CAPTION_RE.match(t) or re.search(r"author[’']s (MATLAB )?code", t):
                continue
            br = OxmlElement('w:r')
            br.append(OxmlElement('w:br'))
            p.append(br)
            p.append(run_xml(CAPTION_NOTE))
            n += 1
    return n


def _wtext(el):
    return ''.join(t.text or '' for t in el.iter(qn('w:t')))


def _paint(omath):
    n = 0
    for r in omath.iter('{%s}r' % M_NS):
        rpr = r.find(qn('w:rPr'))
        if rpr is None:
            rpr = OxmlElement('w:rPr')
            mrpr = r.find('{%s}rPr' % M_NS)
            if mrpr is not None:
                mrpr.addnext(rpr)
            else:
                r.insert(0, rpr)
        c = rpr.find(qn('w:color'))
        if c is None:
            c = OxmlElement('w:color')
            rpr.append(c)
        c.set(qn('w:val'), RED_HEX)
        n += 1
    return n


def _in_row(el):
    a = el.getparent()
    while a is not None:
        if a.tag == qn('w:tr'):
            return True
        a = a.getparent()
    return False


def colour_equations(elements, i):
    """Set in red the equations new in this proposal (RED, RED_INLINE); the equation numbers stay black."""
    want = set(RED.get(i, []))
    inline = RED_INLINE.get(i, [])
    done = set()
    n_inline = 0
    for el in elements:
        if want:
            rows = [el] if el.tag == qn('w:tr') else list(el.iter(qn('w:tr')))
            paras = [p for p in ([el] if el.tag == qn('w:p') else el.iter(qn('w:p'))) if not _in_row(p)]
            for c in rows + paras:
                if c.find('.//{%s}oMath' % M_NS) is None:
                    continue
                m = re.search(r'\((\d+)\)\s*$', _wtext(c).strip())
                if m and int(m.group(1)) in want:
                    for om in c.iter('{%s}oMath' % M_NS):
                        _paint(om)
                    done.add(int(m.group(1)))
        for om in el.iter('{%s}oMath' % M_NS):
            if ''.join(t.text or '' for t in om.iter('{%s}t' % M_NS)) in inline:
                _paint(om)
                n_inline += 1
    missing = want - done
    if missing:
        print(f'    part {i + 1}: red equations not found: {sorted(missing)}')
    return len(done), n_inline
