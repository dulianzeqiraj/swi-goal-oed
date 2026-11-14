#!/usr/bin/env python3
"""Typeset the OMML equations of a Word file as pictures, for the PDF only.

LibreOffice draws native Word equations (OMML) poorly when it makes a PDF from a .docx: it converts them
to its own formula objects, so parentheses become thin bars, the spacing is odd and the fonts are not
Word's Cambria Math. render_equations() writes a separate .docx, used only to make the PDF, in which
every equation is a high-resolution picture of the same equation typeset by matplotlib's mathtext in the
STIX fonts (a Times-like math font, as in a LaTeX or Word document), sitting on the text baseline. The
Word file itself keeps its OMML.

    render_equations(src_docx, dst_docx, red=None, dpi=600, display_pt=11.0, default_inline_pt=10.5,
                     workdir=None) -> dict of statistics
    python omml_render.py SRC.docx DST.docx [--pdf OUTDIR] [--dpi 600] [--display-pt 11] [--inline-pt 10.5]

Pipeline
  1. Every m:oMathPara (display) and every m:oMath outside an m:oMathPara (inline) of word/document.xml,
     tables included, is collected.
  2. OMML -> LaTeX with pandoc: the distinct equations (cached by a hash of their OMML) are put, one per
     paragraph after a numbered marker, into one minimal .docx, which `pandoc -f docx -t json` converts in
     a single call; the math of each paragraph is read back from the JSON. Before that, the OMML is
     prepared so that pandoc keeps what it otherwise drops: upright (m:sty p) letters such as the "eq" of
     X_eq or a differential d, bold italic, operator names of m:func, and m:limLow over a function name,
     are marked with private-use characters in m:nor runs; linear fractions become a/b.
  3. The LaTeX is translated into what mathtext accepts (\\mspace, \\left.\\parallel, empty scripts,
     \\widehat of one letter, \\text with superscript characters, \\limits, environments matrix, pmatrix,
     cases, aligned ...) and typeset by mathtext (fontset 'stix') at `dpi`, in black, or in dark red #C00000
     when red(element) is true. Display equations use display style: \\dfrac at the top level, larger sums
     and products with limits below and above, larger integrals; inline equations use text style, with
     limits beside the operator. Matrices and cases are laid out by this module inside mathtext's box model.
     An equation that mathtext cannot typeset keeps its OMML (fallback); the list of such LaTeX strings is
     returned.
  4. Inline equations are typeset at the size of the neighbouring text run (w:sz of the run, else of its
     character style, paragraph style or the document defaults; with no text beside it, the size of the
     equation's own runs; else default_inline_pt); display equations at display_pt, smaller if the equation
     is wider than its text column or table cell (Word would break the line). The picture has exactly the
     typeset width, height and depth (descent); ink beyond that box widens it. The colour is black, dark red
     when red(element) is true, an explicit colour of the equation's runs, or, among light text (white on
     a dark table header), the colour of that text so that it stays readable.

Baseline
  Word lowers an inline picture with <w:position w:val="-N"/> (N in half-points) on its run. LibreOffice
  24.2 ignores w:position for pictures (it turns it into an escapement of text only) and puts the bottom of
  an inline picture on the baseline. So each inline equation is written in an <mc:AlternateContent>:
    * mc:Choice Requires="wp14", taken by Word 2010 and later: the inline picture lowered by w:position
      (its depth is rounded up to whole half-points, so the lowering is exact);
    * mc:Fallback, taken by LibreOffice (it takes only a Choice that requires wps, wpg, wpc or w14): an
      invisible inline DrawingML rectangle of no width, the picture anchored at the next character
      (positionH relative to the character, positionV relative to the line, no wrap), and an invisible
      rectangle as wide as the equation; both rectangles are as high as the equation above the baseline.
      With proportional line spacing LibreOffice puts a picture anchored relative to the line at the top
      of the character rectangle at the anchor: that of the rectangle before it, or at the start of a line
      that of the one after it. The equation's baseline lands on the text baseline to 0.1 pt, in justified
      text and in tables, and its place in the line is exactly its width. (Measured in 24.2: inline VML
      shapes there add height to the lines of a paragraph with direct space after and move the anchored
      picture; a transparent picture cannot be narrower than 1.15 pt.)
  With single, exact or at-least line spacing LibreOffice takes the top of the line instead. A paragraph
  with single spacing (w:line 240, auto, in itself, its style or its table's style) that holds inline
  equations gets 101 % (w:line 243), which looks the same; with exact or at-least spacing the equation is a
  plain inline picture there (lowered for Word only; counted in the statistics).
  In a paragraph without text (an equation alone in a table cell) Word's line is as high as the paragraph
  mark's font, so the rectangles are made that high (and the picture goes down by the difference).
  LibreOffice reserves no room below the baseline for the anchored picture; inline equations are at most
  about half an em deep, which the line spacing takes.
  A display equation alone in its paragraph is a plain inline picture (lowered for Word); the paragraph
  takes the equation's justification (m:jc, else the document's m:defJc, centred) since a picture does not
  follow m:jc. A display equation with other content in its paragraph (tabs, an equation number "(6)") is
  written like an inline equation, so that the number sits on its baseline; the other content stays.

Nothing else in the document changes: the m:oMath / m:oMathPara elements are replaced in place, the
pictures are added under word/media with their relationships, [Content_Types].xml gets a png default if it
lacks one, the paragraph of a display equation may get w:jc and a single-spaced paragraph with inline
equations w:line 243, as said. All other parts of the package are copied byte for byte.

Make the PDF with lossless pictures:
  soffice --headless --convert-to 'pdf:writer_pdf_Export:{"UseLosslessCompression":{"type":"boolean","value":"true"},"ReduceImageResolution":{"type":"boolean","value":"false"}}' --outdir OUT file.docx
(export_pdf() below does this.) The pictures are 8-bit palette PNGs whose palette is one colour with 256
levels of transparency (tRNS), so they are small and sit on shaded table cells without a white box;
LibreOffice stores identical pictures once in the PDF.

Only python-docx, lxml, numpy, matplotlib (mathtext; its Pillow dependency writes the PNG files), pandoc
and fontconfig's fc-match (the ascent of a paragraph's font, for an equation alone in its paragraph) are
used.
"""
import argparse
import copy
import hashlib
import io
import json
import logging
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from collections import Counter

import numpy as np
from lxml import etree

__all__ = ['render_equations', 'export_pdf', 'omml_to_tex', 'tex_to_mathtext', 'typeset']

# --------------------------------------------------------------------------------------------- namespaces
W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
WP_NS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
PIC_NS = 'http://schemas.openxmlformats.org/drawingml/2006/picture'
MC_NS = 'http://schemas.openxmlformats.org/markup-compatibility/2006'
WP14_NS = 'http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing'
PR_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT_NS = 'http://schemas.openxmlformats.org/package/2006/content-types'
IMAGE_REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'
WPS_NS = 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape'

_NSDECL = (f'xmlns:w="{W_NS}" xmlns:r="{R_NS}" xmlns:wp="{WP_NS}" xmlns:a="{A_NS}" xmlns:pic="{PIC_NS}" '
           f'xmlns:mc="{MC_NS}" xmlns:wp14="{WP14_NS}"')


def _w(tag):
    return '{%s}%s' % (W_NS, tag)


def _m(tag):
    return '{%s}%s' % (M_NS, tag)


W_P, W_R, W_T, W_RPR, W_PPR, W_SZ, W_COLOR, W_RSTYLE, W_PSTYLE, W_JC = (
    _w('p'), _w('r'), _w('t'), _w('rPr'), _w('pPr'), _w('sz'), _w('color'), _w('rStyle'), _w('pStyle'), _w('jc'))
M_OMATH, M_OMATHPARA, M_R, M_T, M_RPR = _m('oMath'), _m('oMathPara'), _m('r'), _m('t'), _m('rPr')
M_VAL = _m('val')
W_VAL = _w('val')

EMU_PER_PT = 12700
EMU_PER_INCH = 914400
RED = 'C00000'
PDF_FILTER = ('pdf:writer_pdf_Export:{"UseLosslessCompression":{"type":"boolean","value":"true"},'
              '"ReduceImageResolution":{"type":"boolean","value":"false"}}')

# Bump when the OMML preparation for pandoc changes (keys of the LaTeX cache).
_PREP_VERSION = 'omml-prep-3'
# Private-use characters that carry, through pandoc, what its OMML reader would otherwise drop.
_UPRIGHT, _BOLDITALIC, _OPNAME = '\ue000', '\ue001', '\ue002'
# Placeholders for arrays (matrices, cases, aligned) inside a mathtext string.
_PLACEHOLDER0 = 0xE100
# Put before an operator, relation or comma in a script (or a text-style fraction): no spaces around it,
# as TeX and Word set them; mathtext would space them as in the main line.
_TIGHT = '\ue0ff'

# Function names that pandoc's OMML reader turns into \ln, \max ... and that mathtext knows.
_TEX_FUNCS = set('arccos arcsin arctan arg cos cosh cot coth csc deg det dim exp gcd hom inf ker lg lim '
                 'liminf limsup ln log max min Pr sec sin sinh sup tan tanh'.split())
# Functions whose limits TeX puts below in display style (mathtext does it for all but inf, always).
_LIMIT_FUNCS = set('lim liminf limsup sup inf max min Pr det gcd'.split())
_MT_OVERUNDER_FUNCS = set('lim liminf limsup sup max min'.split())
_BIG_OPS = set(r'\sum \prod \coprod \bigcup \bigcap \bigsqcup \bigvee \bigwedge \bigodot \bigotimes '
               r'\bigoplus \biguplus'.split())
_INTEGRALS = set(r'\int \oint \iint \oiint \iiint \oiiint \iiiint'.split())
_BARS = {'|', r'\vert', r'\|', r'\Vert', '‖'}

_log = logging.getLogger('omml_render')


# ============================================================================================ OMML -> TeX
def _strip_formatting(el):
    """Drop the WordprocessingML run formatting inside OMML (sizes, fonts): it does not change the TeX."""
    for e in list(el.iter(_w('rPr'), _m('ctrlPr'))):
        e.getparent().remove(e)
    return el


def omml_key(om):
    """Hash of an m:oMath element without its run formatting (the key of the LaTeX cache)."""
    c = _strip_formatting(copy.deepcopy(om))
    xml = etree.tostring(c, method='c14n', exclusive=True)
    return hashlib.sha1(_PREP_VERSION.encode() + xml).hexdigest()


def _run_text(r):
    return ''.join(t.text or '' for t in r.iter(M_T))


def _mark_run(r, marker):
    """Make an m:r a normal-text run whose text starts with a private-use marker (survives pandoc)."""
    rpr = r.find(M_RPR)
    if rpr is None:
        rpr = etree.Element(M_RPR)
        r.insert(0, rpr)
    for e in list(rpr):
        if e.tag in (_m('sty'), _m('scr'), _m('nor')):
            rpr.remove(e)
    lit = rpr.find(_m('lit'))
    nor = etree.Element(_m('nor'))
    if lit is not None:
        lit.addnext(nor)
    else:
        rpr.insert(0, nor)
    ts = r.findall(M_T)
    if ts:
        ts[0].text = marker + (ts[0].text or '')


def _has_letters(s):
    return re.search(r'[A-Za-z\u03b1-\u03c9\u03d1\u03d5\u03d6\u03f0\u03f1\u03f5]', s) is not None


def _prepare_for_pandoc(om):
    """Copy of an m:oMath with the information pandoc's OMML reader drops carried by markers."""
    c = _strip_formatting(copy.deepcopy(om))
    # linear and skewed fractions: a/b, as Word shows them
    for f in list(c.iter(_m('f'))):
        t = f.find(f'{_m("fPr")}/{_m("type")}')
        if t is not None and t.get(M_VAL) in ('lin', 'skw'):
            num, den = f.find(_m('num')), f.find(_m('den'))
            slash = etree.fromstring(f'<m:r xmlns:m="{M_NS}"><m:rPr><m:sty m:val="p"/></m:rPr><m:t>/</m:t></m:r>')
            new = (list(num) if num is not None else []) + [slash] + (list(den) if den is not None else [])
            parent = f.getparent()
            i = parent.index(f)
            parent.remove(f)
            for k, e in enumerate(new):
                parent.insert(i + k, e)
    marked = set()

    def merge_runs(runs):
        """Put the text of several m:r into the first one (a name split over runs)."""
        first = runs[0]
        ts = first.findall(M_T)
        if not ts:
            ts = [etree.SubElement(first, M_T)]
        ts[0].text = ''.join(_run_text(r) for r in runs)
        for t in ts[1:]:
            first.remove(t)
        for r in runs[1:]:
            r.getparent().remove(r)
        return first

    # operator names of m:func that TeX does not know (diag, tr, erf ...): \operatorname
    for fn in list(c.iter(_m('fName'))):
        runs = [r for r in fn if r.tag == M_R]
        if len(runs) == len(fn) and runs:
            name = ''.join(_run_text(r) for r in runs).strip()
            if name and name not in _TEX_FUNCS and re.fullmatch(r'[A-Za-z]+', name):
                r = merge_runs(runs)
                _mark_run(r, _OPNAME)
                marked.add(r)
            else:
                marked.update(runs)
    # m:limLow / m:limUpp over a function name: keep the limit below/above (pandoc would write \Pr_{x})
    for tag in ('limLow', 'limUpp'):
        for ll in list(c.iter(_m(tag))):
            e = ll.find(_m('e'))
            runs = [r for r in e] if e is not None else []
            if runs and all(r.tag == M_R for r in runs) and ''.join(_run_text(r) for r in runs).strip() in _TEX_FUNCS:
                r = merge_runs(runs)
                _mark_run(r, _OPNAME)
                marked.add(r)
    # upright (m:sty p) letters and bold italic runs
    for r in list(c.iter(M_R)):
        if r in marked:
            continue
        rpr = r.find(M_RPR)
        if rpr is None or rpr.find(_m('nor')) is not None or rpr.find(_m('scr')) is not None:
            continue
        sty = rpr.find(_m('sty'))
        val = sty.get(M_VAL) if sty is not None else None
        text = _run_text(r)
        if val == 'p' and _has_letters(text) and text.strip() not in _TEX_FUNCS:
            _mark_run(r, _UPRIGHT)
        elif val == 'bi' and text.strip():
            _mark_run(r, _BOLDITALIC)
    return c


def _pandoc_batch(items, tmpdir, pandoc='pandoc'):
    """items: list of (key, prepared m:oMath). Returns {key: tex} for those pandoc converted."""
    from docx import Document  # python-docx: a valid minimal .docx to hold the equations
    doc = Document()
    body = doc.element.body
    sect = body[-1] if len(body) and body[-1].tag == _w('sectPr') else None
    for i, (_, om) in enumerate(items):
        p = etree.SubElement(body, W_P)
        r = etree.SubElement(p, W_R)
        t = etree.SubElement(r, W_T)
        t.text = 'QZEQ%06d' % i
        p.append(copy.deepcopy(om))
    if sect is not None:
        body.remove(sect)
        body.append(sect)
    path = os.path.join(tmpdir, 'omml_batch_%d.docx' % len(items))
    doc.save(path)
    res = subprocess.run([pandoc, '-f', 'docx', '-t', 'json', path], capture_output=True, timeout=900)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.decode('utf8', 'replace')[:500])
    js = json.loads(res.stdout)
    out = {}

    def walk(blocks):
        for b in blocks:
            if not isinstance(b, dict):
                continue
            if b.get('t') in ('Para', 'Plain'):
                mk, maths = None, []
                for x in b['c']:
                    if x.get('t') == 'Str' and re.fullmatch(r'QZEQ\d{6}', x.get('c', '')):
                        mk = int(x['c'][4:])
                    elif x.get('t') == 'Math':
                        maths.append(x['c'][1])
                if mk is not None and mk < len(items) and maths:
                    out[items[mk][0]] = ' '.join(maths)
            elif isinstance(b.get('c'), list):  # Div, BlockQuote ...: look inside
                for sub in b['c']:
                    if isinstance(sub, list):
                        walk(sub)
    walk(js.get('blocks', []))
    return out


def omml_to_tex(elements, cache=None, workdir=None, batch=400, pandoc='pandoc'):
    """LaTeX of m:oMath elements with pandoc. Returns ({key: tex}, [key of each element], number of pandoc
    calls).

    Equal equations (same OMML without run formatting) are converted once; `cache` maps keys to LaTeX
    from earlier runs and is updated."""
    cache = {} if cache is None else cache
    keyed = {}
    keys = []
    for om in elements:
        k = omml_key(om)
        keys.append(k)
        keyed.setdefault(k, om)
    todo = [(k, _prepare_for_pandoc(om)) for k, om in keyed.items() if k not in cache]
    calls = 0
    tmp = tempfile.mkdtemp(prefix='omml_pandoc_', dir=workdir)
    try:
        def run(chunk):
            nonlocal calls
            calls += 1
            try:
                got = _pandoc_batch(chunk, tmp, pandoc)
            except Exception as err:  # one bad equation must not lose the others: split the batch
                if len(chunk) == 1:
                    _log.warning('pandoc failed on one equation: %s', err)
                    return
                h = len(chunk) // 2
                run(chunk[:h])
                run(chunk[h:])
                return
            cache.update(got)
            missing = [it for it in chunk if it[0] not in got]
            if missing and len(chunk) > 1:   # isolate equations whose output could not be split off
                for it in missing:
                    run([it])
        for s in range(0, len(todo), batch):
            run(todo[s:s + batch])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return {k: cache[k] for k in keyed if k in cache}, keys, calls


# ========================================================================================= TeX -> mathtext
_TOKEN = re.compile(r'\\[A-Za-z]+|\\.|[{}]|\s+|[^\\{}\s]', re.S)


class _G(list):
    """A {...} group of the token tree."""


def _tree(s):
    root = _G()
    stack = [root]
    for t in _TOKEN.findall(s):
        if t == '{':
            g = _G()
            stack[-1].append(g)
            stack.append(g)
        elif t == '}':
            if len(stack) > 1:
                stack.pop()
        else:
            stack[-1].append(t)
    return root


def _ser(nodes):
    out = []
    for n in nodes:
        out.append('{' + _ser(n) + '}' if isinstance(n, _G) else n)
    return ''.join(out)


def _skip_ws(nodes, i):
    while i < len(nodes) and isinstance(nodes[i], str) and nodes[i].isspace():
        i += 1
    return i


def _arg(nodes, i):
    """Next argument (a group, or one token) after position i: (node or None, next index)."""
    i = _skip_ws(nodes, i)
    if i >= len(nodes):
        return None, i
    return nodes[i], i + 1


def _as_list(node):
    if node is None:
        return _G()
    return node if isinstance(node, _G) else _G([node])


def _primes(node):
    """Number of primes if the node is a superscript made only of primes (\\prime, ', ′, ″, ‴), else 0."""
    toks = [x for x in _as_list(node) if not (isinstance(x, str) and x.isspace())]
    n = 0
    for x in toks:
        if isinstance(x, _G):
            m = _primes(x)
            if not m:
                return 0
            n += m
        elif x in (r'\prime', "'", '′'):
            n += 1
        elif x == '″':
            n += 2
        elif x == '‴':
            n += 3
        else:
            return 0
    return n


def _empty(node):
    if node is None:
        return True
    if isinstance(node, _G):
        return all(isinstance(x, str) and x.isspace() for x in node) or not node
    return False


_SUPERSCRIPTS = dict(zip('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ', '0123456789+-=()ni'))
_SUBSCRIPTS = dict(zip('₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎', '0123456789+-=()'))
# mathtext's \text{} takes its content literally and cannot hold braces
_TEXT_ESCAPES = [(r'\textbackslash', '∖'), (r'\%', '%'), (r'\&', '&'), (r'\#', '#'), (r'\_', '_'),
                 (r'\{', ''), (r'\}', ''), (r'\$', '$'), ('{', ''), ('}', ''), ('~', ' ')]
_DELIM_MAP = {r'\lbrack': '[', r'\rbrack': ']', r'\lbrace': r'\{', r'\rbrace': r'\}', r'\|': r'\Vert',
              r'\lVert': r'\Vert', r'\rVert': r'\Vert', r'\Vert': r'\Vert', r'\vert': '|', r'\lvert': '|',
              r'\rvert': '|', r'\parallel': r'\Vert', r'\mid': '|'}
_SYMBOL_MAP = {r'\lbrack': '[', r'\rbrack': ']', r'\lbrace': r'\{', r'\rbrace': r'\}', r'\dots': r'\ldots',
               r'\lVert': r'\Vert', r'\rVert': r'\Vert', r'\|': r'\Vert', r'\lvert': '|', r'\rvert': '|',
               r'\vert': '|', r'\colon': ':', r'\ne': r'\neq', r'\le': r'\leq', r'\ge': r'\geq',
               r'\to': r'\rightarrow', r'\gets': r'\leftarrow', r'\land': r'\wedge', r'\lor': r'\vee',
               r'\lnot': r'\neg', r'\owns': r'\ni', r'\bm': r'\boldsymbol', r'\textbf': r'\mathbf',
               r'\varnothing': r'\emptyset', r'\smallsetminus': r'\setminus'}
_DROP = set(r'\limits \nolimits \displaystyle \textstyle \scriptstyle \scriptscriptstyle \nonumber \notag '
            r'\mathrel \mathbin \mathord \mathpunct \mathinner \mathopen \mathclose \strut \relax'.split())
_FONTS = set(r'\mathbf \mathit \mathsf \mathtt \mathcal \mathbb \mathfrak \mathscr \boldsymbol \mathrm'.split())
_ACCENTS = set(r'\hat \bar \dot \ddot \tilde \vec \check \breve \acute \grave \mathring \overline \underline '
               r'\widehat \widetilde \overrightarrow \overleftarrow'.split())
_ENVS = {  # name: (left delimiter, right delimiter, column alignment, gap between columns in em, stretch)
    'matrix': ('', '', 'c', 1.0, 1.0), 'smallmatrix': ('', '', 'c', 0.6, 1.0),
    'pmatrix': ('(', ')', 'c', 1.0, 1.0), 'bmatrix': ('[', ']', 'c', 1.0, 1.0),
    'Bmatrix': (r'\{', r'\}', 'c', 1.0, 1.0), 'vmatrix': ('|', '|', 'c', 1.0, 1.0),
    'Vmatrix': (r'\Vert', r'\Vert', 'c', 1.0, 1.0), 'cases': (r'\{', '.', 'l', 1.0, 1.2),
    'array': ('', '', 'c', 1.0, 1.0), 'aligned': ('', '', 'rl', 0.0, 1.25), 'align': ('', '', 'rl', 0.0, 1.25),
    'align*': ('', '', 'rl', 0.0, 1.25), 'alignedat': ('', '', 'rl', 0.0, 1.25), 'split': ('', '', 'rl', 0.0, 1.25),
    'gathered': ('', '', 'c', 1.0, 1.25), 'gather': ('', '', 'c', 1.0, 1.25), 'eqnarray': ('', '', 'rcl', 0.3, 1.25),
}


class _Translator:
    """Pandoc's LaTeX -> a string mathtext typesets, plus the arrays it refers to by placeholders."""

    def __init__(self, display, size_pt=10.0):
        self.display = display
        self.size_pt = size_pt
        self.arrays = {}  # placeholder character -> (rows of cell strings, alignment, gap em, stretch)

    # -- helpers -------------------------------------------------------------------------------------
    def _text(self, raw):
        """\\text{raw} (raw is the LaTeX inside the braces) -> mathtext."""
        marker = raw[:1]
        if marker in (_UPRIGHT, _BOLDITALIC, _OPNAME):
            raw = raw[1:]
        for a, b in _TEXT_ESCAPES:
            raw = raw.replace(a, b)
        raw = re.sub(r'\\([A-Za-z]+)\s*', r'\1', raw)       # leftover commands: keep their letters
        raw = raw.replace('\\', '')
        if marker == _OPNAME and re.fullmatch(r'[A-Za-z]+', raw.strip()):
            return r'\operatorname{%s}' % raw.strip()
        if marker == _BOLDITALIC:
            return r'\boldsymbol{%s}' % self._mathletters(raw)
        if marker == _UPRIGHT and not re.search(r'\s', raw.strip()) and re.fullmatch(r'[0-9A-Za-z.,\'+\-*/=]+', raw.strip()):
            return r'\mathrm{%s}' % raw.strip().replace('-', '{-}')
        # split off superscript / subscript characters (s⁻¹), which the STIX text font lacks
        out = []
        for part in re.split(r'([%s]+|[%s]+)' % (''.join(_SUPERSCRIPTS), ''.join(_SUBSCRIPTS)), raw):
            if not part:
                continue
            if part[0] in _SUPERSCRIPTS:
                out.append('^{%s}' % ''.join(_SUPERSCRIPTS[c] for c in part))
            elif part[0] in _SUBSCRIPTS:
                out.append('_{%s}' % ''.join(_SUBSCRIPTS[c] for c in part))
            else:
                out.append(r'\text{%s}' % part)
        if out and out[0][0] in '^_':
            out.insert(0, '{}')
        return ''.join(out) if out else ''

    @staticmethod
    def _mathletters(s):
        return ''.join(ch for ch in s if not ch.isspace())

    def _delim(self, nodes, i):
        """The delimiter after \\left, \\right or \\middle: (mathtext delimiter, next index)."""
        d, j = _arg(nodes, i)
        if d is None:
            return '.', j
        if isinstance(d, _G):
            d = _ser(d).strip() or '.'
        if d == '.':
            k = _skip_ws(nodes, j)
            if k < len(nodes) and nodes[k] in (r'\parallel', r'\|', r'\Vert'):  # pandoc's \left. \parallel
                return r'\Vert', k + 1
            return '.', j
        if d == '<':
            d = r'\langle'
        elif d == '>':
            d = r'\rangle'
        return _DELIM_MAP.get(d, d), j

    def _env(self, nodes, i, name, prev_out):
        """\\begin{name} ... \\end{name}: (mathtext text, next index)."""
        # collect the content up to the matching \end{name}
        depth = 0
        j = i
        content = []
        while j < len(nodes):
            t = nodes[j]
            if t == r'\begin':
                depth += 1
            elif t == r'\end':
                if depth == 0:
                    _, j2 = _arg(nodes, j + 1)
                    j = j2
                    break
                depth -= 1
            content.append(t)
            j += 1
        spec = _ENVS.get(name.rstrip('*'), _ENVS.get(name, ('', '', 'c', 1.0, 1.0)))
        left, right, align, gap, stretch = spec
        if name == 'array' and content:           # column spec {lcr}
            colspec, k = _arg(content, 0)
            align = ''.join(ch for ch in _ser(_as_list(colspec)) if ch in 'lcr') or 'c'
            content = content[k:]
        if name == 'matrix' and prev_out.rstrip().endswith(r'\left\{'):
            align, stretch = 'l', 1.2               # pandoc writes cases as \left\{ matrix \right.
        rows, row, cell = [], [], []
        for t in content:
            if t == '\\\\':
                row.append(cell)
                rows.append(row)
                row, cell = [], []
            elif t == '&':
                row.append(cell)
                cell = []
            else:
                cell.append(t)
        if cell or row:
            row.append(cell)
            rows.append(row)
        rows = [r for r in rows if any(_ser(c).strip() for c in r)]
        if not rows:
            return '', j
        sub = _Translator(False, self.size_pt)          # cells are in text style, as in TeX arrays
        cells = []
        for r in rows:
            cr = []
            for c in r:
                txt = sub.emit(_G(c), 1).strip()
                if sub.arrays:
                    raise ValueError('nested arrays')
                cr.append(txt)
            cells.append(cr)
        ph = chr(_PLACEHOLDER0 + len(self.arrays))
        self.arrays[ph] = (cells, align, gap, stretch)
        if left or right:
            return r'\left%s %s \right%s' % (left or '.', ph, right or '.'), j
        return ph, j

    # -- main walk --------------------------------------------------------------------------------------
    def emit(self, nodes, lvl=0, script=False):
        """Walk a token list. lvl counts fraction and script levels (\\dfrac only at the top of a
        display equation); script is true in scripts and in text-style fractions."""
        out = []
        i = 0
        n = len(nodes)
        spaced = _spaced_symbols()
        while i < n:
            t = nodes[i]
            if isinstance(t, _G):
                out.append('{' + self.emit(t, lvl, script) + '}')
                i += 1
                continue
            if t.isspace():
                out.append(' ')
                i += 1
                continue
            if t in ('^', '_'):
                a, j = _arg(nodes, i + 1)
                if _empty(a):                       # empty limits of n-ary operators: \sum_{x}^{}
                    i = j
                    continue
                nprimes = _primes(a) if t == '^' else 0
                if nprimes:
                    # A^{\prime}: the STIX prime is drawn raised already; as a superscript it would be tiny
                    # and too high. Put it beside the base, before a subscript: {A′}_{e}, {f″}.
                    glyph = {1: r'\prime', 2: '″', 3: '‴'}.get(nprimes, r'\prime' * nprimes)
                    k = len(out) - 1
                    while k >= 0 and out[k] == ' ':
                        k -= 1
                    sub = k >= 1 and out[k].startswith('_{')
                    if sub:
                        k -= 1
                        while k >= 0 and out[k] == ' ':
                            k -= 1
                    nk = _skip_ws(nodes, j)
                    sub = sub or (nk < n and nodes[nk] == '_')
                    if k >= 0:
                        out[k] = '{' + out[k] + glyph + (r'\!' if sub else '') + '}'
                    else:
                        out.append(glyph)
                    i = j
                    continue
                out.append(t + '{' + self.emit(_as_list(a), lvl + 1, True) + '}')
                i = j
                continue
            if t == '\\\\':                          # a line break outside an environment: mathtext has none
                out.append(r'\quad ')
                i += 1
                continue
            if t in _SUPERSCRIPTS or t in _SUBSCRIPTS:   # 10⁻⁴ in math: a script
                table, op = (_SUPERSCRIPTS, '^') if t in _SUPERSCRIPTS else (_SUBSCRIPTS, '_')
                chars = []
                while i < n and isinstance(nodes[i], str) and nodes[i] in table:
                    chars.append(table[nodes[i]])
                    i += 1
                out.append('%s{%s}' % (op, ''.join(chars)))
                continue
            if t == ',' and i + 1 < n and isinstance(nodes[i + 1], str) and nodes[i + 1][:1].isdigit() \
                    and ''.join(out).rstrip()[-1:].isdigit():
                out.append('{,}')                    # a digit-group comma (1,000): no space after it
                i += 1
                continue
            if not t.startswith('\\'):
                out.append((_TIGHT + t) if script and t in spaced else t)
                i += 1
                continue
            # ---- commands
            if t in _DROP:
                i += 1
                continue
            if t in (r'\left', r'\right', r'\middle'):
                d, j = self._delim(nodes, i + 1)
                out.append(t + d + ' ')
                i = j
                continue
            if t == r'\begin':
                a, j = _arg(nodes, i + 1)
                name = _ser(_as_list(a)).strip()
                txt, j = self._env(nodes, j, name, ''.join(out))
                out.append(txt)
                i = j
                continue
            if t in (r'\mspace', r'\hspace', r'\kern', r'\mkern', r'\hskip'):
                a, j = _arg(nodes, i + 1)
                m = re.match(r'\s*(-?[0-9.]+)\s*(mu|em|ex|pt|bp|mm|cm|in)?', _ser(_as_list(a)))
                if m:
                    v = float(m.group(1))
                    unit = m.group(2) or ('mu' if t in (r'\mspace', r'\mkern') else 'pt')
                    em = {'mu': 1 / 18, 'em': 1.0, 'ex': 0.43, 'pt': 1 / self.size_pt, 'bp': 1.00375 / self.size_pt,
                          'mm': 2.84528 / self.size_pt, 'cm': 28.4528 / self.size_pt, 'in': 72.27 / self.size_pt}[unit]
                    out.append(r'\hspace{%.4f}' % (v * em))
                i = j
                continue
            if t in (r'\text', r'\textrm', r'\textnormal', r'\mbox', r'\textup', r'\textit', r'\textsf', r'\texttt'):
                a, j = _arg(nodes, i + 1)
                out.append(self._text(_ser(_as_list(a))))
                i = j
                continue
            if t == r'\operatorname' or t == r'\mathop':
                a, j = _arg(nodes, i + 1)
                name = re.sub(r'\\[A-Za-z]+\s*|[{}\s]', '', _ser(_as_list(a))).lstrip(_OPNAME + _UPRIGHT)
                out.append(r'\operatorname{%s}' % name if name else '')
                i = j
                continue
            if t in (r'\frac', r'\dfrac', r'\tfrac', r'\cfrac', r'\binom', r'\dbinom', r'\tbinom'):
                a, j = _arg(nodes, i + 1)
                b, j = _arg(nodes, j)
                disp = (self.display and lvl == 0 and t not in (r'\tfrac', r'\tbinom')) or t in (r'\dfrac', r'\dbinom', r'\cfrac')
                na = self.emit(_as_list(a), lvl + 1, script or not disp)
                nb = self.emit(_as_list(b), lvl + 1, script or not disp)
                if 'binom' in t:
                    out.append(r'\genfrac{(}{)}{0}{%s}{%s}{%s}' % ('0' if disp else '', na, nb))
                else:
                    out.append((r'\dfrac{%s}{%s}' if disp else r'\frac{%s}{%s}') % (na, nb))
                i = j
                continue
            if t == r'\sqrt':
                j = _skip_ws(nodes, i + 1)
                root = ''
                if j < n and nodes[j] == '[':      # optional index
                    k = j + 1
                    idx = []
                    while k < n and nodes[k] != ']':
                        idx.append(nodes[k])
                        k += 1
                    root = '[' + self.emit(_G(idx), lvl + 2, True) + ']'
                    j = k + 1
                a, j = _arg(nodes, j)
                out.append(r'\sqrt%s{%s}' % (root, self.emit(_as_list(a), lvl, script)))
                i = j
                continue
            if t in (r'\overset', r'\underset', r'\stackrel'):
                a, j = _arg(nodes, i + 1)
                b, j = _arg(nodes, j)
                ann, body = self.emit(_as_list(a), lvl + 1, True), self.emit(_as_list(b), lvl, script)
                fname = self._funcname(body)
                if t == r'\underset' and fname and not self.display:      # inline: limit beside
                    out.append(r'{\operatorname{%s}}_{%s}' % (fname, ann))
                elif t == r'\underset' and fname and fname in _MT_OVERUNDER_FUNCS:
                    out.append(r'\%s_{%s}' % (fname, ann))
                else:
                    out.append(r'\%s{%s}{%s}' % ('overset' if t == r'\stackrel' else t[1:], ann, body))
                i = j
                continue
            if t in _ACCENTS:
                a, j = _arg(nodes, i + 1)
                body = self.emit(_as_list(a), lvl, script)
                single = (not isinstance(a, _G) or len([x for x in a if not (isinstance(x, str) and x.isspace())]) == 1) \
                    and not (isinstance(a, _G) and a and isinstance(a[0], _G))
                cmd = t
                if t == r'\widehat' and single:
                    cmd = r'\hat'
                elif t == r'\widetilde' and single:
                    cmd = r'\tilde'
                elif t == r'\overrightarrow' and single:
                    cmd = r'\vec'
                elif t == r'\overleftarrow':
                    cmd = r'\overline'
                out.append(r'%s{%s}' % (cmd, body))
                i = j
                continue
            if t in _FONTS or t == r'\bm':
                a, j = _arg(nodes, i + 1)
                cmd = _SYMBOL_MAP.get(t, t)
                inner = _as_list(a)
                if cmd == r'\mathit' and len(inner) == 1 and isinstance(inner[0], str) and inner[0][1:] in _TEX_FUNCS:
                    out.append(r'\mathit{%s}' % inner[0][1:])
                else:
                    out.append(r'%s{%s}' % (cmd, self.emit(inner, lvl, script)))
                i = j
                continue
            if t == r'\boxed':
                a, j = _arg(nodes, i + 1)
                out.append('{' + self.emit(_as_list(a), lvl, script) + '}')
                i = j
                continue
            if t in _BIG_OPS:
                k = _skip_ws(nodes, i + 1)
                if not self.display and k < n and nodes[k] in ('_', '^'):
                    out.append('{%s}' % t)            # inline: limits beside the operator
                else:
                    out.append(t + ' ')
                i += 1
                continue
            if t[1:] in _MT_OVERUNDER_FUNCS:
                # \max_{t} from pandoc is a plain subscript in the OMML (m:sSub; a limit below, m:limLow,
                # arrives as \underset): keep it beside the name, which mathtext would not do.
                k = _skip_ws(nodes, i + 1)
                if k < n and nodes[k] in ('_', '^'):
                    out.append(r'{\operatorname{%s}}' % t[1:])
                    i += 1
                    continue
                out.append(t + ' ')
                i += 1
                continue
            t = _SYMBOL_MAP.get(t, t)
            if script and t in spaced:
                t = _TIGHT + t
            out.append(t + (' ' if t[-1:].isalpha() else ''))
            i += 1
        return ''.join(out)

    @staticmethod
    def _funcname(body):
        m = re.fullmatch(r'\s*(?:\\operatorname\{([A-Za-z]+)\}|\\([A-Za-z]+)|\\mathrm\{([A-Za-z]+)\}|'
                         r'\\text\{([A-Za-z]+)\})\s*', body)
        if not m:
            return None
        name = next(g for g in m.groups() if g)
        return name if (name in _LIMIT_FUNCS or m.group(1) or m.group(3) or m.group(4)) else None


_SPACED = []


def _spaced_symbols():
    """The operators, relations, arrows and punctuation that mathtext spaces."""
    if not _SPACED:
        from matplotlib import _mathtext as mt
        P = mt.Parser
        _SPACED.append(set(P._binary_operators) | set(P._relation_symbols) | set(P._arrow_symbols)
                       | {',', ';', '-', '+', '='})
    return _SPACED[0]


def _tidy(s):
    """Collapse spaces (keeping control spaces), drop trailing spaces, merge \\mathrm{a}\\mathrm{b}."""
    s = re.sub(r'(?<!\\)\s+', ' ', s)
    while True:
        t = re.sub(r'(\\ |\s)+$', '', s).strip()
        if t == s:
            break
        s = t
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r'\\mathrm\{([^{}]*)\}\s*\\mathrm\{([^{}]*)\}', r'\\mathrm{\1\2}', s)
    return s


def tex_to_mathtext(tex, display=False, size_pt=10.0):
    """Pandoc's LaTeX -> (mathtext string without $, {placeholder: array spec})."""
    tr = _Translator(display, size_pt)
    s = _tidy(tr.emit(_tree(tex.replace('\n', ' '))))
    for ph, (cells, align, gap, stretch) in tr.arrays.items():
        for row in cells:
            row[:] = [_tidy(c) for c in row]
    return s, tr.arrays


# ================================================================================================= typeset
_MT = {}


def _mathtext():
    """matplotlib internals, loaded once: a parser subclass with display-style operators and arrays."""
    if _MT:
        return _MT
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    from matplotlib import _mathtext as mt
    from matplotlib.font_manager import FontProperties
    from matplotlib.ft2font import LoadFlags

    class BarRule(mt.Rule):
        """A vertical rule from `height` above to `depth` below the baseline (mathtext draws a rule in a
        horizontal list only `height` tall, ending `depth` below the baseline)."""

        def render(self, output, x, y, w, h):
            self.fontset.render_rect_filled(output, x, y - self.height - self.depth, w, self.height + self.depth)

    class ShiftedChar(mt.Char):
        """A character moved down by `shift` pixels (a big operator centred on the math axis). It is still a
        Char, so mathtext still puts the limits of a sum below and above it."""

        def __init__(self, c, state, shift):
            self._shift = shift
            super().__init__(c, state)

        def _update_metrics(self):
            super()._update_metrics()
            self.height -= self._shift
            self.depth += self._shift

        def shrink(self):
            before = self.fontsize
            super().shrink()
            self._shift *= self.fontsize / before if before else 1.0

        def render(self, output, x, y):
            super().render(output, x, y + self._shift)

    unary_before = re.compile(r'(?:^\$|[{(\[,;:=<>]|\\quad|\\qquad|\\left\S*|\\(?:leq|geq|neq|le|ge|ne|approx|'
                              r'sim|simeq|equiv|propto|in|ni|ll|gg|to|rightarrow|leftarrow|Rightarrow|'
                              r'Leftrightarrow|mapsto|mid|times|cdot|pm|mp))\s*$')

    class Parser(mt.Parser):
        """mathtext's parser with display-size big operators, laid-out arrays (by placeholder), tall bars
        drawn as rules rather than stretched glyphs, and a unary minus after a comma or a quad."""
        display = False
        arrays = {}
        base_size = 10.0

        def _auto_sized_delimiter(self, front, middle, back):
            boxes = [x for x in middle if not isinstance(x, str)]
            if boxes and (front in _BARS or back in _BARS):
                h = max(x.height for x in boxes)
                d = max(x.depth for x in boxes)
                left = self._bar(front, h, d) if front in _BARS else None
                right = self._bar(back, h, d) if back in _BARS else None
                if left is not None or right is not None:
                    inner = super()._auto_sized_delimiter('.' if left is not None else front, middle,
                                                          '.' if right is not None else back)
                    return mt.Hlist(([left] if left is not None else []) + [inner] +
                                    ([right] if right is not None else []))
            return super()._auto_sized_delimiter(front, middle, back)

        def _bar(self, c, h, d):
            """A | or ‖ around content, drawn as rules of the glyph's stem width, at least as tall as a
            parenthesis and as tall as the content: STIX has one size of these glyphs, which mathtext would
            scale to the content, into a heavy bar for a tall one and a tiny bar for a short one."""
            state = self.get_state().copy()
            state.font = '0'
            double = c in (r'\|', r'\Vert', '‖')
            glyph = mt.Char('‖' if double else '|', state)
            paren = mt.Char('(', state)
            single = mt.Char('|', state)._metrics
            m = glyph._metrics
            t = single.xmax - single.xmin
            h, d = max(h, paren.height), max(d, paren.depth)
            parts = [mt.Kern(m.xmin), BarRule(t, h, d, state)]
            if double:
                parts += [mt.Kern((m.xmax - m.xmin) - 2 * t), BarRule(t, h, d, state)]
            parts.append(mt.Kern(m.advance - m.xmax))
            return mt.Hlist(parts)

        def symbol(self, s, loc, toks):
            c = toks['sym']
            spec = self.arrays.get(c)
            if spec is not None:
                return [self._array(spec)]
            if c == _TIGHT:
                return [mt.Hbox(0)]
            if s[loc - 1:loc] == _TIGHT or (c in ('-', '+', '−', r'\pm', r'\mp')
                                             and unary_before.search(s[:loc])):
                # in a script, or a sign after a comma, a quad or at the start: no spaces (as TeX, Word)
                try:
                    return [mt.Char('−' if c == '-' else c, self.get_state())]
                except ValueError:
                    pass
            if self.display and (c in _BIG_OPS or c in _INTEGRALS):
                state = self.get_state()
                if state.fontsize >= self.base_size * 0.99:            # not in a script
                    st = state.copy()
                    if c in _BIG_OPS:
                        alts = st.fontset.get_sized_alternatives_for_symbol(st.font, c)
                        if len(alts) > 1:
                            st.font = str(alts[1][0])
                        else:
                            st.fontsize *= 1.4
                    else:
                        st.fontsize *= 1.5
                    try:
                        ch = mt.Char(c, st)
                        # centre the operator on the math axis, as TeX does with display operators
                        axis = state.fontset.get_axis_height(state.font, state.fontsize, state.dpi)
                        shift = (ch.height - ch.depth) / 2 - axis
                        return [ShiftedChar(c, st, shift)]
                    except Exception:
                        return super().symbol(s, loc, toks)
            return super().symbol(s, loc, toks)

        def _array(self, spec):
            cells, align, gap, stretch = spec
            state = self.get_state()
            fs, size, dpi = state.fontset, state.fontsize, state.dpi
            cp = _MT['cell_parser']
            boxes = [[cp.parse('$%s$' % c if c.strip() else r'$\hspace{0}$', fs, size, dpi) for c in r]
                     for r in cells]
            ncol = max(len(r) for r in boxes)
            colw = [max((r[k].width for r in boxes if k < len(r)), default=0.0) for k in range(ncol)]
            em = size * dpi / 72.0
            skip = 1.2 * em * stretch
            sh, sd = 0.7 * skip, 0.3 * skip
            rows = []
            for r in boxes:
                items = []
                for k in range(ncol):
                    b = r[k] if k < len(r) else mt.Hlist([])
                    pad = colw[k] - b.width
                    a = align[k % len(align)] if align else 'c'
                    if a == 'l':
                        items += [b, mt.Kern(pad)]
                    elif a == 'r':
                        items += [mt.Kern(pad), b]
                    else:
                        items += [mt.Kern(pad / 2), b, mt.Kern(pad / 2)]
                    if k < ncol - 1:
                        g = gap
                        if align == 'rl' or (len(align) == 2 and align == 'rl'):
                            g = 0.0 if k % 2 == 0 else 2.0
                        items.append(mt.Kern(g * em))
                items.append(mt.Box(0, sh, sd))
                rows.append(mt.Hlist(items))
            vl = mt.Vlist(rows)
            axis = fs.get_axis_height(state.font, size, dpi)
            total = vl.height + vl.depth
            vl.shift_amount = vl.height - (axis + total / 2)
            return mt.Hlist([vl])

    _MT.update(mt=mt, Parser=Parser, FontProperties=FontProperties, LoadFlags=LoadFlags,
               parser=Parser(), cell_parser=Parser())
    return _MT


class _GlyphWarnings(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def typeset(mtex, arrays, size_pt, dpi, display):
    """Typeset a mathtext string. Returns (coverage uint8 array, baseline row) or raises ValueError.

    The image is the typeset box (width, height and depth of mathtext's layout, in pixels at `dpi`),
    widened only where ink reaches outside it; the baseline falls on a pixel boundary and the depth is
    rounded up to whole half-points (the unit of Word's w:position)."""
    mtx = _MT or _mathtext()
    mt = mtx['mt']
    parser = mtx['parser']
    parser.display = display
    parser.arrays = arrays
    parser.base_size = size_pt
    mtx['cell_parser'].display = False
    mtx['cell_parser'].arrays = {}
    mtx['cell_parser'].base_size = size_pt
    prop = mtx['FontProperties'](size=size_pt, math_fontfamily='stix')
    fontset = mt.StixFonts(prop, mtx['LoadFlags'].NO_HINTING)
    handler = _GlyphWarnings()
    mlog = logging.getLogger('matplotlib.mathtext')
    mlog2 = logging.getLogger('matplotlib._mathtext')
    mlog.addHandler(handler)
    mlog2.addHandler(handler)
    try:
        box = parser.parse('$%s$' % mtex, fontset, size_pt, dpi)
    except Exception as err:
        raise ValueError(str(err).strip().splitlines()[-1] if str(err).strip() else repr(err))
    finally:
        mlog.removeHandler(handler)
        mlog2.removeHandler(handler)
        parser.arrays = {}
    if handler.messages:
        raise ValueError('missing glyph: ' + handler.messages[0])
    out = mt.ship(box)
    W, H, D = box.width, box.height, box.depth
    xs0 = [ox + info.metrics.xmin for ox, oy, info in out.glyphs] + [x for x, y, w, h in out.rects]
    xs1 = [ox + info.metrics.xmax for ox, oy, info in out.glyphs] + [x + w for x, y, w, h in out.rects]
    ys0 = [oy - info.metrics.ymax for ox, oy, info in out.glyphs] + [y for x, y, w, h in out.rects]
    ys1 = [oy - info.metrics.ymin for ox, oy, info in out.glyphs] + [y + h for x, y, w, h in out.rects]
    if not xs0 or W <= 0:
        raise ValueError('empty equation')
    left = min(0.0, math.floor(min(xs0)) - 1)
    right = max(W, math.ceil(max(xs1)) + 1)
    top = min(0.0, math.floor(min(ys0)) - 1)
    bottom = max(H + D, math.ceil(max(ys1)) + 1)
    # baseline on a pixel boundary: shift the drawing down by the fraction
    base = H - top                                   # baseline row (float) from the top of the image
    dy = math.ceil(base) - base
    base_px = int(round(base + dy))
    depth_px = (bottom - top) - base                 # from the baseline down
    hp = dpi / 144.0                                 # pixels per half-point
    depth_px = math.ceil(round(depth_px / hp, 6)) * hp if depth_px > 0.01 else 0.0
    min_px = 1.2 * dpi / 72.0                        # LibreOffice's smallest frame is 1.15 pt
    asc_px = max(base_px, math.ceil(min_px))
    pad_top = asc_px - base_px
    height_px = int(asc_px + round(depth_px))
    width_px = max(int(math.ceil(right - left)), int(math.ceil(min_px)))
    img = np.zeros((height_px, width_px), np.uint8)
    shipped = mt.ship(box, (-left, -top + dy + pad_top))
    for ox, oy, info in shipped.glyphs:
        info.font.draw_glyph_to_bitmap(img, int(ox), int(oy - info.metrics.iceberg), info.glyph,
                                       antialiased=True)
    for x, y, bw, bh in shipped.rects:          # fraction bars, root bars: as matplotlib's to_raster
        hh = max(int(bh) - 1, 0)
        if hh == 0:
            y0 = int(y + bh / 2 - (hh + 1) / 2)
        else:
            y0 = int(y)
        x1, x2 = math.floor(x), math.ceil(x + bw)
        img[max(y0, 0):y0 + hh + 1, max(x1, 0):x2 + 1] = 0xff
    return img, asc_px


def _png(cov, color):
    """8-bit palette PNG: one colour, 256 levels of transparency."""
    from PIL import Image
    r, g, b = (int(color[k:k + 2], 16) for k in (0, 2, 4))
    im = Image.frombytes('P', (cov.shape[1], cov.shape[0]), np.ascontiguousarray(cov).tobytes())
    im.putpalette([r, g, b] * 256)
    buf = io.BytesIO()
    im.save(buf, format='PNG', transparency=bytes(range(256)), optimize=True)
    return buf.getvalue()


# ============================================================================================ document side
class _Styles:
    """Font size, colour and line spacing of paragraph, character and table styles (with basedOn) and of
    the document defaults."""

    def __init__(self, styles_xml):
        self.styles = {}
        self.spacing = {}            # style id -> (w:line, w:lineRule) of its w:pPr, if it sets w:line
        self.cell_mar_raw = {}       # table style id -> {'left': twips, 'right': twips}
        self.fonts = {}              # style id -> w:rFonts/@w:ascii
        self.doc_font = None
        self.default_para = None
        self.doc_sz = None
        self.doc_color = None
        self.doc_line = None
        if not styles_xml:
            return
        root = etree.fromstring(styles_xml)
        dd = root.find(f'{_w("docDefaults")}/{_w("rPrDefault")}/{W_RPR}')
        if dd is not None:
            self.doc_sz = self._sz(dd)
            self.doc_color = self._color(dd)
            rf = dd.find(_w('rFonts'))
            self.doc_font = rf.get(_w('ascii')) if rf is not None else None
        dp = root.find(f'{_w("docDefaults")}/{_w("pPrDefault")}/{W_PPR}')
        if dp is not None:
            self.doc_line = _line_of(dp)
        for s in root.findall(_w('style')):
            sid = s.get(_w('styleId'))
            based = s.find(_w('basedOn'))
            rpr = s.find(W_RPR)
            self.styles[sid] = (based.get(W_VAL) if based is not None else None,
                                self._sz(rpr) if rpr is not None else None,
                                self._color(rpr) if rpr is not None else None)
            ppr = s.find(W_PPR)
            if ppr is not None and _line_of(ppr):
                self.spacing[sid] = _line_of(ppr)
            rf = rpr.find(_w('rFonts')) if rpr is not None else None
            if rf is not None and rf.get(_w('ascii')):
                self.fonts[sid] = rf.get(_w('ascii'))
            if s.get(_w('type')) == 'table':
                mar = s.find(f'{_w("tblPr")}/{_w("tblCellMar")}')
                d = {}
                if mar is not None:
                    for side, alt in (('left', 'start'), ('right', 'end')):
                        e = mar.find(_w(side))
                        if e is None:
                            e = mar.find(_w(alt))
                        if e is not None:
                            d[side] = _twips(e, 'w')
                self.cell_mar_raw[sid] = d
            if s.get(_w('type')) == 'paragraph' and s.get(_w('default')) in ('1', 'true', 'on'):
                self.default_para = sid

    def tbl_cell_mar(self, sid):
        """Left/right cell margins (twips) of a table style, following basedOn."""
        seen = set()
        while sid and sid not in seen and sid in self.cell_mar_raw:
            seen.add(sid)
            if self.cell_mar_raw[sid]:
                return self.cell_mar_raw[sid]
            sid = self.styles.get(sid, (None,))[0]
        return {}

    def font_chain(self, sid):
        seen = set()
        while sid and sid not in seen and sid in self.styles:
            seen.add(sid)
            if sid in self.fonts:
                return self.fonts[sid]
            sid = self.styles[sid][0]
        return None

    def line_chain(self, sid):
        seen = set()
        while sid and sid not in seen and sid in self.styles:
            seen.add(sid)
            if sid in self.spacing:
                return self.spacing[sid]
            sid = self.styles[sid][0]
        return None

    @staticmethod
    def _sz(rpr):
        e = rpr.find(W_SZ)
        try:
            return int(e.get(W_VAL)) if e is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _color(rpr):
        e = rpr.find(W_COLOR)
        v = e.get(W_VAL) if e is not None else None
        return v if v and re.fullmatch(r'[0-9A-Fa-f]{6}', v) else None

    def chain(self, sid, idx):
        seen = set()
        while sid and sid not in seen and sid in self.styles:
            seen.add(sid)
            based, sz, col = self.styles[sid]
            v = (sz, col)[idx]
            if v is not None:
                return v
            sid = based
        return None


def _line_of(ppr):
    sp = ppr.find(_w('spacing'))
    if sp is None or sp.get(_w('line')) is None:
        return None
    try:
        return int(sp.get(_w('line'))), sp.get(_w('lineRule')) or 'auto'
    except ValueError:
        return None


def _line_spacing(p, styles):
    """(w:line, w:lineRule) in force for a paragraph: direct, paragraph style, table style, defaults."""
    ppr = p.find(W_PPR)
    v = _line_of(ppr) if ppr is not None else None
    if v:
        return v
    v = styles.line_chain(_para_style(p, styles))
    if v:
        return v
    tbl = next((a for a in p.iterancestors() if a.tag == _w('tbl')), None)
    if tbl is not None:
        ts = tbl.find(f'{_w("tblPr")}/{_w("tblStyle")}')
        if ts is not None:
            v = styles.line_chain(ts.get(W_VAL))
            if v:
                return v
    return styles.doc_line or (240, 'auto')


def _para_style(p, styles):
    ps = p.find(f'{W_PPR}/{W_PSTYLE}')
    return ps.get(W_VAL) if ps is not None else styles.default_para


def _run_prop(run, p, styles, idx):
    """Size (half-points, idx 0) or colour (idx 1) of a run: direct, character style, paragraph style,
    document defaults."""
    rpr = run.find(W_RPR) if run is not None else None
    if rpr is not None:
        v = (styles._sz(rpr), styles._color(rpr))[idx]
        if v is not None:
            return v
        rs = rpr.find(W_RSTYLE)
        if rs is not None:
            v = styles.chain(rs.get(W_VAL), idx)
            if v is not None:
                return v
    if p is not None:
        v = styles.chain(_para_style(p, styles), idx)
        if v is not None:
            return v
    return (styles.doc_sz, styles.doc_color)[idx]


def _neighbour_run(el, p):
    """The text run nearest before the element in its paragraph, else the nearest after it."""
    prev = nxt = None
    seen = False
    for e in p.iter(W_R, M_OMATH, M_OMATHPARA):
        if e is el:
            seen = True
            continue
        if e.tag != W_R:
            continue
        if not any((t.text or '').strip() for t in e.iter(W_T)):
            continue
        if not seen:
            prev = e
        else:
            nxt = e
            break
    return prev if prev is not None else nxt


def _omml_size(el):
    """The commonest w:sz (half-points) of the runs of an OMML element, or None."""
    szs = Counter()
    for e in el.iter(W_SZ):
        try:
            szs[int(e.get(W_VAL))] += 1
        except (TypeError, ValueError):
            pass
    return szs.most_common(1)[0][0] if szs else None


_ASCENT = {}


def _font_ascent(family):
    """Ascent of a font family as LibreOffice lays out text (hhea ascender + line gap, per em), from the
    font file fontconfig picks for it; 0.94 (Arial, Liberation Sans) when it cannot be read."""
    if family in _ASCENT:
        return _ASCENT[family]
    ratio = 0.94
    try:
        path = subprocess.run(['fc-match', '-f', '%{file}', family or 'Liberation Serif'], capture_output=True,
                              text=True, timeout=20).stdout.strip()
        if path:
            from matplotlib import ft2font
            f = ft2font.FT2Font(path)
            hh = f.get_sfnt_table('hhea')
            if hh and f.units_per_EM:
                ratio = (hh['ascent'] + max(hh.get('lineGap', 0), 0)) / f.units_per_EM
    except Exception:
        pass
    _ASCENT[family] = ratio
    return ratio


def _para_has_text(p):
    """True if the paragraph has text of its own (w:t outside equations) or a tab."""
    for t in p.iter(W_T, _w('tab'), _w('sym')):
        if t.tag != W_T or (t.text or '').strip():
            if not any(a.tag in (M_OMATH, M_OMATHPARA) for a in t.iterancestors()):
                return True
    return False


def _mark_ascent_pt(p, styles):
    """Ascent (pt) of the font of the paragraph mark, as LibreOffice lays out a line."""
    rpr = p.find(f'{W_PPR}/{W_RPR}')
    sz = styles._sz(rpr) if rpr is not None else None
    fam = None
    if rpr is not None:
        rf = rpr.find(_w('rFonts'))
        fam = rf.get(_w('ascii')) if rf is not None else None
    sid = _para_style(p, styles)
    sz = sz or styles.chain(sid, 0) or styles.doc_sz or 20
    fam = fam or styles.font_chain(sid) or styles.doc_font or 'Liberation Serif'
    return _font_ascent(fam) * sz / 2.0


def _omml_color(el):
    cols = Counter()
    for c in el.iter(W_COLOR):
        v = c.get(W_VAL)
        if v and re.fullmatch(r'[0-9A-Fa-f]{6}', v):
            cols[v.upper()] += 1
    return cols.most_common(1)[0][0] if cols else None


def _luminance(hexcol):
    r, g, b = (int(hexcol[k:k + 2], 16) / 255 for k in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


_PPR_ORDER = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl', 'numPr',
              'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap',
              'overflowPunct', 'topLinePunct', 'autoSpaceDE', 'autoSpaceDN', 'bidi', 'adjustRightInd',
              'snapToGrid', 'spacing', 'ind', 'contextualSpacing', 'mirrorIndents', 'suppressOverlap', 'jc',
              'textDirection', 'textAlignment', 'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr',
              'sectPr', 'pPrChange']


def _set_jc(p, val):
    ppr = p.find(W_PPR)
    if ppr is None:
        ppr = etree.Element(W_PPR)
        p.insert(0, ppr)
    jc = ppr.find(W_JC)
    if jc is not None:
        if jc.get(W_VAL) == val:
            return False
        jc.set(W_VAL, val)
        return True
    jc = etree.Element(W_JC)
    jc.set(W_VAL, val)
    pos = _PPR_ORDER.index('jc')
    for k, child in enumerate(ppr):
        name = etree.QName(child).localname if isinstance(child.tag, str) else ''
        if name in _PPR_ORDER and _PPR_ORDER.index(name) > pos:
            ppr.insert(k, jc)
            return True
    ppr.append(jc)
    return True


def _twips(e, name):
    if e is None:
        return 0
    v = e.get(_w(name))
    try:
        return int(float(v)) if v is not None else 0
    except ValueError:
        return 0


def _cell_margins(tc, tbl, styles_tbl_mar):
    """Left + right inner margins of a table cell (twips): the cell's, the table's, its style's, 108 each."""
    total = 0
    for side, alt in (('left', 'start'), ('right', 'end')):
        v = None
        for holder in (tc.find(f'{_w("tcPr")}/{_w("tcMar")}'), tbl.find(f'{_w("tblPr")}/{_w("tblCellMar")}')):
            if holder is not None:
                e = holder.find(_w(side))
                if e is None:
                    e = holder.find(_w(alt))
                if e is not None and e.get(_w('type'), 'dxa') == 'dxa':
                    v = _twips(e, 'w')
                    break
        if v is None:
            v = styles_tbl_mar.get(side, 108)
        total += v
    return total


def _text_widths(root, styles):
    """Width (pt) available to the text of each paragraph: its column in the section, or its table cell
    (from the table grid), less the cell margins and the paragraph indents."""
    out = {}
    body = root.find(_w('body'))
    if body is None:
        return out
    # the section of each top-level block: sections end at a paragraph with w:sectPr, the last at the body's
    sect_w = []
    pending = []
    def section_width(sp):
        if sp is None:
            return None
        pg, mar = sp.find(_w('pgSz')), sp.find(_w('pgMar'))
        w = _twips(pg, 'w') - _twips(mar, 'left') - _twips(mar, 'right') - _twips(mar, 'gutter')
        cols = sp.find(_w('cols'))
        n = int(cols.get(_w('num'), '1')) if cols is not None and (cols.get(_w('num')) or '1').isdigit() else 1
        if n > 1:
            w = (w - _twips(cols, 'space') * (n - 1)) / n
        return w if w > 0 else None
    for blk in body:
        pending.append(blk)
        sp = blk.find(f'{W_PPR}/{_w("sectPr")}') if blk.tag == W_P else (blk if blk.tag == _w('sectPr') else None)
        if sp is not None:
            w = section_width(sp)
            sect_w.extend((b, w) for b in pending)
            pending = []
    final = body.find(_w('sectPr'))
    fw = section_width(final)
    sect_w.extend((b, fw) for b in pending)
    for blk, w in sect_w:
        for p in ([blk] if blk.tag == W_P else blk.iter(W_P)):
            tc = next((a for a in p.iterancestors() if a.tag == _w('tc')), None)
            avail = w
            if tc is not None:
                tbl = next(a for a in tc.iterancestors() if a.tag == _w('tbl'))
                tr = tc.getparent()
                grid = [_twips(g, 'w') for g in tbl.findall(f'{_w("tblGrid")}/{_w("gridCol")}')]
                col = 0
                gb = tr.find(f'{_w("trPr")}/{_w("gridBefore")}')
                if gb is not None:
                    col += int(gb.get(W_VAL, '0') or 0)
                cw = None
                for c in tr.findall(_w('tc')):
                    span_e = c.find(f'{_w("tcPr")}/{_w("gridSpan")}')
                    span = int(span_e.get(W_VAL, '1')) if span_e is not None else 1
                    if c is tc:
                        cw = sum(grid[col:col + span]) if grid[col:col + span] else None
                        break
                    col += span
                if not cw:
                    tw = tc.find(f'{_w("tcPr")}/{_w("tcW")}')
                    cw = _twips(tw, 'w') if tw is not None and tw.get(_w('type')) == 'dxa' else None
                if not cw:
                    continue
                ts = tbl.find(f'{_w("tblPr")}/{_w("tblStyle")}')
                avail = cw - _cell_margins(tc, tbl, styles.tbl_cell_mar(ts.get(W_VAL) if ts is not None else None))
            if not avail:
                continue
            ind = p.find(f'{W_PPR}/{_w("ind")}')
            if ind is not None:
                avail -= (_twips(ind, 'left') or _twips(ind, 'start')) + (_twips(ind, 'right') or _twips(ind, 'end'))
                avail -= _twips(ind, 'firstLine')
            out[p] = avail / 20.0
    return out


def _set_line(p, line):
    """Give the paragraph direct proportional line spacing w:line (keeping its other w:spacing)."""
    ppr = p.find(W_PPR)
    if ppr is None:
        ppr = etree.Element(W_PPR)
        p.insert(0, ppr)
    sp = ppr.find(_w('spacing'))
    if sp is None:
        sp = etree.Element(_w('spacing'))
        pos = _PPR_ORDER.index('spacing')
        for k, child in enumerate(ppr):
            name = etree.QName(child).localname if isinstance(child.tag, str) else ''
            if name in _PPR_ORDER and _PPR_ORDER.index(name) > pos:
                ppr.insert(k, sp)
                break
        else:
            ppr.append(sp)
    sp.set(_w('line'), str(line))
    sp.set(_w('lineRule'), 'auto')


def _direct_jc(p):
    jc = p.find(f'{W_PPR}/{W_JC}')
    return jc.get(W_VAL) if jc is not None else None


def _alone_in_paragraph(el, p):
    """True if the paragraph shows nothing but this element (runs without text, bookmarks ... aside)."""
    for e in p.iter():
        if e is el:
            continue
        if any(a is el for a in e.iterancestors()):
            continue
        if not isinstance(e.tag, str):
            continue
        if e.tag in (W_T, _w('tab'), _w('br'), _w('drawing'), _w('pict'), _w('object'), _w('sym'), _w('ptab'),
                     _w('fldChar'), _w('instrText'), M_OMATH, M_OMATHPARA) and not (e.tag == W_T and not (e.text or '').strip()):
            return False
    return True


# ------------------------------------------------------------------------------------------- picture XML
def _pic_xml(rid, cx, cy, pid, name, descr):
    return (f'<a:graphic xmlns:a="{A_NS}"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic xmlns:pic="{PIC_NS}"><pic:nvPicPr><pic:cNvPr id="{pid}" name="{name}" descr="{descr}"/>'
            f'<pic:cNvPicPr><a:picLocks noChangeAspect="1" noChangeArrowheads="1"/></pic:cNvPicPr></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr bwMode="auto"><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></pic:spPr></pic:pic></a:graphicData></a:graphic>')


def _inline_xml(rid, cx, cy, pid, name, descr):
    return (f'<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
            f'<wp:docPr id="{pid}" name="{name}" descr="{descr}"/>'
            f'<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="{A_NS}" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            + _pic_xml(rid, cx, cy, pid, name, descr) + '</wp:inline></w:drawing>')


def _anchor_xml(rid, cx, cy, pid, name, descr, zorder, yoff=0):
    """The equation picture anchored at the next character: at its left edge, `yoff` EMU below the top of
    the line (LibreOffice: the top of the character rectangle, see the module doc), no wrap."""
    return (f'<w:drawing><wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="{zorder}" '
            f'behindDoc="0" locked="0" layoutInCell="1" allowOverlap="1">'
            f'<wp:simplePos x="0" y="0"/>'
            f'<wp:positionH relativeFrom="character"><wp:posOffset>0</wp:posOffset></wp:positionH>'
            f'<wp:positionV relativeFrom="line"><wp:posOffset>{yoff}</wp:posOffset></wp:positionV>'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:wrapNone/>'
            f'<wp:docPr id="{pid}" name="{name}" descr="{descr}"/>'
            f'<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="{A_NS}" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            + _pic_xml(rid, cx, cy, pid, name, descr) + '</wp:anchor></w:drawing>')


def _shape_spacer_xml(cx, cy, pid):
    """An invisible inline DrawingML rectangle (no fill, no line) of cx x cy EMU, on the baseline: it keeps
    the place of an equation in the line and gives the anchor its reference (see the module doc). Unlike
    a picture it may have no width, and unlike a VML shape it does not change the line height."""
    return (f'<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
            f'<wp:docPr id="{pid}" name="Equation space {pid}"/><wp:cNvGraphicFramePr/>'
            f'<a:graphic xmlns:a="{A_NS}"><a:graphicData uri="{WPS_NS}">'
            f'<wps:wsp xmlns:wps="{WPS_NS}"><wps:cNvSpPr/><wps:spPr><a:xfrm><a:off x="0" y="0"/>'
            f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/>'
            f'<a:ln><a:noFill/></a:ln></wps:spPr><wps:bodyPr/></wps:wsp></a:graphicData></a:graphic>'
            f'</wp:inline></w:drawing>')


def _xml_attr(s):
    return (s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('\n', ' '))


# ================================================================================================== main
def render_equations(src_docx, dst_docx, red=None, dpi=600, display_pt=11.0, default_inline_pt=10.5,
                     workdir=None):
    """Write dst_docx: a copy of src_docx in which every OMML equation is a picture (see the module doc).

    red: None, or a function called with each equation's element (the m:oMath of an inline equation, the
        m:oMathPara of a display one, still in the document) that returns True for an equation to be drawn
        in dark red #C00000 (as revised text) instead of black.
    dpi: resolution of the pictures; display_pt: size of display equations; default_inline_pt: size of an
        inline equation whose text size cannot be found. workdir: folder for temporary files and the cache
        of pandoc's LaTeX (omml_tex_cache.json); a temporary folder by default.

    Returns statistics: counts of inline and display equations found and converted, the fallbacks (OMML
    kept) with their LaTeX and the reason, the pictures, sizes and times."""
    t0 = time.time()
    own_tmp = workdir is None
    work = tempfile.mkdtemp(prefix='omml_render_') if own_tmp else os.path.abspath(workdir)
    os.makedirs(work, exist_ok=True)
    try:
        return _render(src_docx, dst_docx, red, dpi, display_pt, default_inline_pt, work, t0)
    finally:
        if own_tmp:
            shutil.rmtree(work, ignore_errors=True)


def _render(src_docx, dst_docx, red, dpi, display_pt, default_inline_pt, work, t0):
    with zipfile.ZipFile(src_docx) as z:
        infos = z.infolist()
        data = {i.filename: z.read(i.filename) for i in infos}
    parser = etree.XMLParser(huge_tree=True, remove_blank_text=False, resolve_entities=False)
    doc_name = 'word/document.xml'
    root = etree.fromstring(data[doc_name], parser)
    styles = _Styles(data.get('word/styles.xml'))
    def_jc = 'centerGroup'
    if 'word/settings.xml' in data:
        sroot = etree.fromstring(data['word/settings.xml'], parser)
        dj = sroot.find(f'{_m("mathPr")}/{_m("defJc")}')
        if dj is not None and dj.get(M_VAL):
            def_jc = dj.get(M_VAL)

    # ---- equations
    displays = list(root.iter(M_OMATHPARA))
    inlines = [om for om in root.iter(M_OMATH)
               if not any(a.tag == M_OMATHPARA for a in om.iterancestors())]
    units = []          # (element replaced, kind, paragraph, [m:oMath], alone)
    for el in displays:
        p = next((a for a in el.iterancestors() if a.tag == W_P), None)
        oms = [c for c in el if c.tag == M_OMATH]
        units.append((el, 'display', p, oms, p is not None and _alone_in_paragraph(el, p)))
    for el in inlines:
        p = next((a for a in el.iterancestors() if a.tag == W_P), None)
        units.append((el, 'inline', p, [el], False))

    # ---- LaTeX (pandoc), cached by a hash of the OMML
    cache_path = os.path.join(work, 'omml_tex_cache.json')
    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, encoding='utf8') as f:
                cache = json.load(f)
        except (OSError, ValueError):
            cache = {}
    t1 = time.time()
    all_oms = [om for u in units for om in u[3]]
    tex_by_key, all_keys, calls = omml_to_tex(all_oms, cache=cache, workdir=work)
    key_of = {id(om): k for om, k in zip(all_oms, all_keys)}
    try:
        with open(cache_path, 'w', encoding='utf8') as f:
            json.dump(cache, f, ensure_ascii=False)
    except OSError:
        pass
    t_pandoc = time.time() - t1

    # ---- picture of each (equation, size, colour, style)
    t2 = time.time()
    renders = {}        # (key, size, color, display) -> dict or exception text
    media = {}          # png sha1 -> (part name, rId)
    rels_root = etree.fromstring(data['word/_rels/document.xml.rels'], parser)
    rids = {r.get('Id') for r in rels_root}
    existing = set(data)
    pid = [max([int(x) for x in root.xpath('//wp:docPr/@id', namespaces={'wp': WP_NS})
                if str(x).isdigit()] + [0]) + 1]
    zorder = [251660000]
    new_parts = {}
    images_meta = []
    stats = Counter()
    fallback = []
    colors = Counter()
    sizes = Counter()
    jc_set = 0
    spaced_paras = set()
    para_text = {}

    def add_media(png):
        h = hashlib.sha1(png).hexdigest()
        if h in media:
            return media[h][1]
        k = len(media) + 1
        name = 'word/media/omml_eq_%04d.png' % k
        while name in existing:
            k += 1
            name = 'word/media/omml_eq_%04d.png' % k
        existing.add(name)
        rid = 'rIdOmmlEq%d' % k
        while rid in rids:
            rid += 'x'
        rids.add(rid)
        rel = etree.SubElement(rels_root, '{%s}Relationship' % PR_NS)
        rel.set('Id', rid)
        rel.set('Type', IMAGE_REL)
        rel.set('Target', name[len('word/'):])
        new_parts[name] = png
        media[h] = (name, rid)
        return rid

    def render(key, size, color, display):
        rk = (key, size, color, display)
        if rk in renders:
            return renders[rk]
        tex = tex_by_key.get(key)
        if tex is None:
            res = {'error': 'pandoc gave no LaTeX', 'tex': None}
        else:
            try:
                mtex, arrays = tex_to_mathtext(tex, display, size)
                cov, asc_px = typeset(mtex, arrays, size, dpi, display)
                png = _png(cov, color)
                emu_px = EMU_PER_INCH / dpi
                h_px, w_px = cov.shape
                res = {'tex': tex, 'mathtext': mtex, 'rid': add_media(png),
                       'cx': int(round(w_px * emu_px)), 'cy': int(round(h_px * emu_px)),
                       'asc_emu': int(round(asc_px * emu_px)),
                       'w_pt': w_px * 72.0 / dpi, 'h_pt': h_px * 72.0 / dpi,
                       'asc_pt': asc_px * 72.0 / dpi, 'depth_pt': (h_px - asc_px) * 72.0 / dpi,
                       'px': (w_px, h_px), 'alpha_sha1': hashlib.sha1(np.ascontiguousarray(cov).tobytes()).hexdigest()}
            except Exception as err:   # mathtext could not typeset it: keep the OMML
                res = {'error': str(err)[:300], 'tex': tex}
        renders[rk] = res
        return res

    def new_id():
        pid[0] += 1
        return pid[0] - 1

    widths = _text_widths(root, styles)
    for el, kind, p, oms, alone in units:
        stats[kind + '_found'] += 1
        # colour
        color = '000000'
        if red is not None and red(el):
            color = RED
        else:
            oc = _omml_color(el)
            if oc and _luminance(oc) > 0.05:
                color = oc
            elif p is not None:
                nb = _neighbour_run(el, p)
                nc = _run_prop(nb, p, styles, 1) if nb is not None else None
                if nc and _luminance(nc) > 0.6:     # light text (white on a dark cell): keep it readable
                    color = nc.upper()
        # size
        if kind == 'display':
            size = float(display_pt)
        else:
            size = None
            if p is not None:
                nb = _neighbour_run(el, p)
                hs = _run_prop(nb, p, styles, 0) if nb is not None else None
                if hs is None:       # no text beside it: the size of its own runs, as Word uses
                    hs = _omml_size(el)
                if hs is None:
                    hs = styles.chain(_para_style(p, styles), 0) or styles.doc_sz
                if hs:
                    size = hs / 2.0
            if size is None:
                size = float(default_inline_pt)
        keys = [key_of[id(om)] for om in oms]
        results = [render(k, size, color, kind == 'display') for k in keys]
        if kind == 'display' and p is not None and all('error' not in r for r in results):
            # a display equation wider than its column is set smaller, to fit (as Word would break it)
            avail = widths.get(p)
            widest = max(r['w_pt'] for r in results)
            if avail and widest > avail:
                small = max(size * avail / widest * 0.995, 0.6 * size)
                small = math.floor(small * 4) / 4.0
                results = [render(k, small, color, True) for k in keys]
                stats['display_shrunk'] += 1
                size = small
        bad = [r for r in results if 'error' in r]
        if bad or not results:
            stats[kind + '_fallback'] += 1
            for r in bad:
                fallback.append({'kind': kind, 'tex': r.get('tex'), 'reason': r['error']})
            continue
        # ---- the replacement runs
        # LibreOffice's construct needs proportional line spacing (see the module doc): a paragraph with
        # single spacing (w:line 240, auto) gets 101 % (243); with exact or at-least spacing the equation is
        # a plain inline picture there (lowered for Word only).
        anchored = not (kind == 'display' and alone)
        if anchored and p is not None:
            line, rule = _line_spacing(p, styles)
            if rule in ('exact', 'atLeast'):
                anchored = False
                stats['not_aligned_in_libreoffice'] += 1
            elif 236 <= line <= 241 and id(p) not in spaced_paras:
                _set_line(p, 243)
                spaced_paras.add(id(p))
        new_runs = []
        for k, res in enumerate(results):
            if k:
                new_runs.append(etree.fromstring(f'<w:r {_NSDECL}><w:br/></w:r>'))
            depth_hp = int(round(res['depth_pt'] * 2))
            rpr = f'<w:rPr><w:position w:val="{-depth_hp}"/></w:rPr>' if depth_hp else ''
            descr = _xml_attr(res['tex'] or '')
            i1 = new_id()
            name = 'Equation %d' % i1
            if not anchored:
                xml = f'<w:r {_NSDECL}>{rpr}' + _inline_xml(res['rid'], res['cx'], res['cy'], i1, name, descr) + '</w:r>'
            else:
                i2, i3 = new_id(), new_id()
                zorder[0] += 1
                choice = _inline_xml(res['rid'], res['cx'], res['cy'], i1, name, descr)
                # In a paragraph without text, Word's line still has the height of the paragraph mark's
                # font; LibreOffice's line would be only as high as the spacers. Make them that high (the
                # picture then goes down by the difference) so the baseline is where Word puts it.
                h_emu = res['asc_emu']
                if p is not None and not para_text.setdefault(id(p), _para_has_text(p)):
                    t_emu = int(math.ceil(_mark_ascent_pt(p, styles) * 20)) * 635
                    h_emu = max(h_emu, t_emu)
                fb = (_shape_spacer_xml(0, h_emu, i3)
                      + _anchor_xml(res['rid'], res['cx'], res['cy'], i2, name, descr, zorder[0],
                                    h_emu - res['asc_emu'])
                      + _shape_spacer_xml(res['cx'], h_emu, new_id()))
                xml = (f'<w:r {_NSDECL}>{rpr}<mc:AlternateContent><mc:Choice Requires="wp14">{choice}</mc:Choice>'
                       f'<mc:Fallback>{fb}</mc:Fallback></mc:AlternateContent></w:r>')
            new_runs.append(etree.fromstring(xml))
            images_meta.append({'kind': kind, 'px': res['px'], 'alpha_sha1': res['alpha_sha1'],
                                'asc_pt': round(res['asc_pt'], 4), 'depth_pt': round(res['depth_pt'], 4),
                                'w_pt': round(res['w_pt'], 3), 'size_pt': size, 'tex': res['tex']})
        # replace the element; a display element keeps the non-math children of m:oMathPara in place
        parent = el.getparent()
        idx = parent.index(el)
        tail = el.tail
        parent.remove(el)
        for k, nr in enumerate(new_runs):
            parent.insert(idx + k, nr)
        if tail:
            new_runs[-1].tail = (new_runs[-1].tail or '') + tail
        if kind == 'display' and alone and p is not None:
            mjc = el.find(f'{_m("oMathParaPr")}/{_m("jc")}')
            val = mjc.get(M_VAL) if mjc is not None else def_jc
            val = {'center': 'center', 'centerGroup': 'center', 'left': 'left', 'right': 'right'}.get(val, 'center')
            cur = _direct_jc(p)
            if cur is None or cur in ('center', 'left', 'right', 'start', 'end', 'both'):
                if cur != val and _set_jc(p, val):
                    jc_set += 1
        stats[kind + '_converted'] += 1
        colors[color] += 1
        if kind == 'inline':
            sizes[size] += 1
    t_render = time.time() - t2

    # ---- write the package: every other part byte for byte
    data[doc_name] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    data['word/_rels/document.xml.rels'] = etree.tostring(rels_root, xml_declaration=True, encoding='UTF-8',
                                                          standalone=True)
    ct = etree.fromstring(data['[Content_Types].xml'], parser)
    if not any(d.get('Extension', '').lower() == 'png' for d in ct.findall('{%s}Default' % CT_NS)):
        dflt = etree.Element('{%s}Default' % CT_NS)
        dflt.set('Extension', 'png')
        dflt.set('ContentType', 'image/png')
        ct.insert(0, dflt)
        data['[Content_Types].xml'] = etree.tostring(ct, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp_out = dst_docx + '.tmp'
    with zipfile.ZipFile(tmp_out, 'w', zipfile.ZIP_DEFLATED) as z:
        for info in infos:
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            z.writestr(zi, data[info.filename])
        stamp = next((i.date_time for i in infos if i.filename == doc_name), (1980, 1, 1, 0, 0, 0))
        for name in sorted(new_parts):       # PNG data is compressed already; same stamp: reproducible file
            zi = zipfile.ZipInfo(name, date_time=stamp)
            zi.compress_type = zipfile.ZIP_STORED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, new_parts[name])
    os.replace(tmp_out, dst_docx)

    seen_tex = set()
    fb_unique = []
    for f in fallback:
        k = (f['tex'], f['reason'])
        if k not in seen_tex:
            seen_tex.add(k)
            fb_unique.append(f)
    return {
        'inline_found': stats['inline_found'], 'display_found': stats['display_found'],
        'inline_converted': stats['inline_converted'], 'display_converted': stats['display_converted'],
        'inline_fallback': stats['inline_fallback'], 'display_fallback': stats['display_fallback'],
        'fallback': stats['inline_fallback'] + stats['display_fallback'],
        'fallback_tex': fb_unique,
        'unique_omml': len(set(key_of.values())),
        'unique_pictures': len(media),
        'pictures_bytes': sum(len(v) for v in new_parts.values()),
        'pandoc_calls': calls, 'paragraph_jc_set': jc_set, 'paragraph_line_243': len(spaced_paras),
        'display_shrunk_to_fit': stats['display_shrunk'],
        'not_aligned_in_libreoffice': stats['not_aligned_in_libreoffice'],
        'colors': dict(colors), 'inline_sizes_pt': dict(sorted(sizes.items())), 'dpi': dpi,
        'seconds_pandoc': round(t_pandoc, 2), 'seconds_typeset': round(t_render, 2),
        'seconds_total': round(time.time() - t0, 2),
        'images': images_meta,
    }


# ===================================================================================================== PDF
def export_pdf(docx, outdir, soffice='soffice', timeout=1800):
    """PDF of a .docx with LibreOffice, pictures lossless and not downsampled. Returns the PDF path."""
    os.makedirs(outdir, exist_ok=True)
    subprocess.run([soffice, '--headless', '--convert-to', PDF_FILTER, '--outdir', outdir, docx],
                   check=True, capture_output=True, timeout=timeout)
    pdf = os.path.join(outdir, os.path.splitext(os.path.basename(docx))[0] + '.pdf')
    if not os.path.exists(pdf):
        raise RuntimeError('LibreOffice made no PDF for ' + docx)
    return pdf


def main(argv=None):
    ap = argparse.ArgumentParser(description='Replace the OMML equations of a .docx by pictures typeset in '
                                             'STIX (for a LibreOffice PDF); the source keeps its OMML.')
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--dpi', type=int, default=600)
    ap.add_argument('--display-pt', type=float, default=11.0)
    ap.add_argument('--inline-pt', type=float, default=10.5, help='size when the text size is unknown')
    ap.add_argument('--workdir', default=None, help='folder for temporary files and the LaTeX cache')
    ap.add_argument('--pdf', metavar='OUTDIR', default=None, help='also make the PDF with LibreOffice')
    ap.add_argument('--json', action='store_true', help='print all statistics as JSON')
    a = ap.parse_args(argv)
    st = render_equations(a.src, a.dst, dpi=a.dpi, display_pt=a.display_pt, default_inline_pt=a.inline_pt,
                          workdir=a.workdir)
    if a.json:
        print(json.dumps(st, indent=1, ensure_ascii=False))
    else:
        print(f"inline: {st['inline_converted']}/{st['inline_found']} converted, display: "
              f"{st['display_converted']}/{st['display_found']} converted, fallback (OMML kept): {st['fallback']}")
        for f in st['fallback_tex']:
            print(f"  fallback {f['kind']}: {f['tex']!r}  ({f['reason']})")
        print(f"{st['unique_omml']} distinct equations, {st['unique_pictures']} pictures "
              f"({st['pictures_bytes'] / 1e6:.1f} MB), pandoc calls: {st['pandoc_calls']}, "
              f"time: {st['seconds_total']} s")
        print('wrote', a.dst)
    if a.pdf:
        pdf = export_pdf(a.dst, a.pdf)
        print('PDF:', pdf, f'({os.path.getsize(pdf) / 1e6:.1f} MB)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
