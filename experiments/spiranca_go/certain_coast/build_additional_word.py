"""CERTAIN-COAST (NATO SPS proposal): the "Additional files" upload as one Word document, and its PDF for the upload.

The document holds a cover, a contents page whose page numbers are live references (PAGEREF), a panel with what is
new in each part, a coloured banner at the start of each part, running headers with the part title, page numbers
"page X of Y", the English names of the preparatory experiments, and every equation as native Word math (OMML). The parts are the Word sources of the
technical annex, the three notes and the two CVs (the same as in build_additional_files.py), merged at the XML level
with their figures, hyperlinks, styles, list numbering and sections. Each part keeps its own body style (its
Normal style over its own document defaults), so its sizes and spacing are those of its source; the technical note
is set in Arial like the rest. The PDF is made while the headings still have outline levels, so it has bookmarks;
the Word file then loses them (word_outline.py), so that Word draws no collapse arrow beside the headings.
Only python-docx and lxml are used.

usage: python build_additional_word.py OUT.docx [OUT.pdf]
Needs LibreOffice (soffice) for the PDF and for the page numbers of the contents (two passes)."""
import copy
import io
import os
import re
import subprocess
import sys
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, HERE)
from codenames import english, english_docx  # noqa: E402
from word_outline import plain_headings  # noqa: E402
from build_additional_files import PARTS  # noqa: E402
from build_application import TITLE  # noqa: E402

FONT = 'Arial'
NAVY, BLUE, GREY, INK, LIGHT = '1F3864', '2E6DB4', '5A6573', '1F2328', 'EEF4FB'
ORANGE, CREAM = 'C55A11', 'FDF3EA'
REPO = 'https://github.com/dulianzeqiraj/certain-coast'           # the open-source code
DOI = '10.5281/zenodo.24148762'                                  # its archive on Zenodo (all versions)
COVER_FIG = os.path.join(HERE, 'guide', 'fig', 'fig01_system.png')
SHORT = ['Technical annex', 'Technical note: the assembled system and the placement of the wells',
         'Theory note: BEYOND-GO, the boundary where the model is cut',
         'Implementation report: SHOCK-GO, the earthquake in the aquifer',
         'CV of the NATO-country Project Director', 'CV of the partner-country Project Director']
# the line under the title of each part in the contents and in its banner
BLURB = [
    'How the methods work, the preparatory tests, the gates with their fallbacks and the nine new contributions.',
    'Assembling the equations of a coastal aquifer, with the placement of recharge and pumping wells as the final '
    'goal. Preparatory work of the NPD\'s team, October 2026; corrected 8 November 2026.',
    'The boundary condition the flow equation is missing: a learnable boundary where the model is cut, four '
    'propositions with proofs and six numerical checks. Preparatory work of the NPD\'s team, November 2026.',
    'The earthquake, the aquifer and liquefaction: the pore-pressure step of each layer, the earthquake as a free '
    'pumping test, the design of the 2019 hindcast and the joint safe window, with numerical checks. Preparatory '
    'work of the NPD\'s team, November 2026.',
    'Assoc. Prof. Dr. Dulian Zeqiraj, Faculty of Geology and Mining, Polytechnic University of Tirana.',
    'Prof. Jassim Al-Khayat, Environmental Science Center, Qatar University.']
# the running header of each part
HEADER = ['Technical annex', 'Technical note: the assembled system', 'Theory note: BEYOND-GO',
          'Implementation report: SHOCK-GO', 'CV of the NATO-country Project Director',
          'CV of the partner-country Project Director']
# what is new in each part, in the words of the part itself (its innovation box, or Table 3 of the annex)
NEW = [
    ('Nine contributions', 1,
     'Nine new contributions, each derived and tested before the project: from guarantees for quantities nobody '
     'measures and the value of a sensor to a boundary that learns the aquifer beyond the model and which aquifer '
     'feels an earthquake (Table 3 of the annex).'),
    ('ASSEMBLY-GO', 2,
     'The placement of the wells is stated first, and the adjoint of its constraint, the chloride at the supply '
     'screen, decides how the equations are assembled. On the test, the goal-graded assembly runs a 30-year forecast '
     '2.5 times faster than the complete one and ranks the 25 layouts as it does (rank correlation 0.997).'),
    ('BEYOND-GO', 3,
     'A boundary condition that learns what lies beyond the model. Every member of its class is a physical exterior '
     'and every linear exterior is a member, so the learned boundary cannot be unphysical, cannot destabilise the '
     'model and loses nothing in generality.'),
    ('SHOCK-GO', 4,
     'Which aquifer feels the earthquake: the static step of a layer under the free surface follows its own shear '
     'modulus, centimetres in soft surface sand and up to a metre in a confined aquifer. Its relaxation, a free '
     'pumping test, identifies the leakage time 5.8 times more sharply than a year of seasonal heads.'),
]
W14 = 'http://schemas.microsoft.com/office/word/2010/wordml'

# ------------------------------------------------------------------------------------------------ small helpers


def run(p, text, size=10.5, bold=False, italic=False, color=INK, caps=False, spacing=None):
    r = p.add_run(text)
    r.font.name = FONT
    r._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    r.font.size = Pt(size)
    r.bold, r.italic = bold, italic
    r.font.color.rgb = RGBColor.from_string(color)
    if caps:
        r.font.all_caps = True
    if spacing is not None:
        sp = OxmlElement('w:spacing')
        sp.set(qn('w:val'), str(spacing))
        rpr_insert(r._element.rPr, sp)
    return r


def para(container, after=4, before=0, align=None):
    p = container.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.space_before = Pt(before)
    if align is not None:
        p.alignment = align
    return p


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear')
    sh.set(qn('w:color'), 'auto')
    sh.set(qn('w:fill'), fill)
    tcPr.append(sh)


def borders(table, color=None, size=4):
    tblPr = table._tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{side}')
        if color is None:
            e.set(qn('w:val'), 'nil')
        else:
            e.set(qn('w:val'), 'single')
            e.set(qn('w:sz'), str(size))
            e.set(qn('w:color'), color)
        b.append(e)
    tblPr.append(b)


def widths(table, cm):
    table.autofit = False
    tbl = table._tbl
    grid = tbl.tblGrid
    for k, gc in enumerate(grid.findall(qn('w:gridCol'))):
        gc.set(qn('w:w'), str(int(cm[k] * 567)))
    for row in table.rows:
        for k, c in enumerate(row.cells):
            c.width = Cm(cm[k])


def field(p, code, cached, size=10.5, color=INK, bold=False):
    """A field (PAGE, NUMPAGES, PAGEREF ...) with a cached result."""
    def r_(child):
        r = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        f = OxmlElement('w:rFonts')
        for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
            f.set(qn(a), FONT)
        rPr.append(f)
        if bold:
            rPr.append(OxmlElement('w:b'))
        c = OxmlElement('w:color')
        c.set(qn('w:val'), color)
        rPr.append(c)
        for tag in ('w:sz', 'w:szCs'):
            s = OxmlElement(tag)
            s.set(qn('w:val'), str(int(size * 2)))
            rPr.append(s)
        r.append(rPr)
        r.append(child)
        p._p.append(r)
    b = OxmlElement('w:fldChar')
    b.set(qn('w:fldCharType'), 'begin')
    r_(b)
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = f' {code} '
    r_(it)
    s = OxmlElement('w:fldChar')
    s.set(qn('w:fldCharType'), 'separate')
    r_(s)
    t = OxmlElement('w:t')
    t.text = cached
    r_(t)
    e = OxmlElement('w:fldChar')
    e.set(qn('w:fldCharType'), 'end')
    r_(e)


def bookmark(p, name, bid):
    s = OxmlElement('w:bookmarkStart')
    s.set(qn('w:id'), str(bid))
    s.set(qn('w:name'), name)
    e = OxmlElement('w:bookmarkEnd')
    e.set(qn('w:id'), str(bid))
    pPr = p._p.find(qn('w:pPr'))
    if pPr is not None:
        pPr.addnext(s)
    else:
        p._p.insert(0, s)
    p._p.append(e)


def outline(p, level):
    pPr = p._p.get_or_add_pPr()
    o = OxmlElement('w:outlineLvl')
    o.set(qn('w:val'), str(level))
    ppr_insert(pPr, o)


def hyperlink(p, url, text, size=9.5, color=BLUE):
    rid = p.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement('w:hyperlink')
    h.set(qn('r:id'), rid)
    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    f = OxmlElement('w:rFonts')
    for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        f.set(qn(a), FONT)
    rPr.append(f)
    c = OxmlElement('w:color')
    c.set(qn('w:val'), color)
    rPr.append(c)
    for tag in ('w:sz', 'w:szCs'):
        s = OxmlElement(tag)
        s.set(qn('w:val'), str(int(size * 2)))
        rPr.append(s)
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)
    r.append(rPr)
    t = OxmlElement('w:t')
    t.text = text
    r.append(t)
    h.append(r)
    p._p.append(h)


# ------------------------------------------------------------------------------------------------ part preparation
RPR_ORDER = ['rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps', 'strike', 'dstrike', 'outline', 'shadow',
             'emboss', 'imprint', 'noProof', 'snapToGrid', 'vanish', 'webHidden', 'color', 'spacing', 'w', 'kern',
             'position', 'sz', 'szCs', 'highlight', 'u', 'effect', 'bdr', 'shd', 'fitText', 'vertAlign', 'rtl', 'cs',
             'em', 'lang', 'eastAsianLayout', 'specVanish', 'oMath']


PPR_ORDER = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl', 'numPr',
             'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap', 'overflowPunct',
             'topLinePunct', 'autoSpaceDE', 'autoSpaceDN', 'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind',
             'contextualSpacing', 'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection', 'textAlignment',
             'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange']


def ppr_insert(pPr, el):
    name = el.tag.split('}')[1]
    rank = PPR_ORDER.index(name)
    for child in list(pPr):
        cname = child.tag.split('}')[1]
        if cname in PPR_ORDER and PPR_ORDER.index(cname) > rank:
            child.addprevious(el)
            return
    pPr.append(el)


def rpr_insert(rPr, el):
    name = el.tag.split('}')[1]
    rank = RPR_ORDER.index(name)
    for k, child in enumerate(list(rPr)):
        cname = child.tag.split('}')[1]
        if cname in RPR_ORDER and RPR_ORDER.index(cname) > rank:
            child.addprevious(el)
            return
    rPr.append(el)


# the order of the children that the schema requires (WordprocessingML, ECMA-376 part 1)
SCHEMA_ORDER = {
    'pPr': ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl', 'numPr',
            'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap',
            'overflowPunct', 'topLinePunct', 'autoSpaceDE', 'autoSpaceDN', 'bidi', 'adjustRightInd', 'snapToGrid',
            'spacing', 'ind', 'contextualSpacing', 'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection',
            'textAlignment', 'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange'],
    'rPr': ['ins', 'del', 'moveFrom', 'moveTo', 'rStyle', 'rFonts', 'b', 'bCs', 'i', 'iCs', 'caps', 'smallCaps',
            'strike', 'dstrike', 'outline', 'shadow', 'emboss', 'imprint', 'noProof', 'snapToGrid', 'vanish',
            'webHidden', 'color', 'spacing', 'w', 'kern', 'position', 'sz', 'szCs', 'highlight', 'u', 'effect', 'bdr',
            'shd', 'fitText', 'vertAlign', 'rtl', 'cs', 'em', 'lang', 'eastAsianLayout', 'specVanish', 'oMath',
            'rPrChange'],
    'tblPr': ['tblStyle', 'tblpPr', 'tblOverlap', 'bidiVisual', 'tblStyleRowBandSize', 'tblStyleColBandSize', 'tblW',
              'jc', 'tblCellSpacing', 'tblInd', 'tblBorders', 'shd', 'tblLayout', 'tblCellMar', 'tblLook',
              'tblCaption', 'tblDescription', 'tblPrChange'],
    'tcPr': ['cnfStyle', 'tcW', 'gridSpan', 'hMerge', 'vMerge', 'tcBorders', 'shd', 'noWrap', 'tcMar',
             'textDirection', 'tcFitText', 'vAlign', 'hideMark', 'headers', 'cellIns', 'cellDel', 'cellMerge',
             'tcPrChange'],
    'sectPr': ['headerReference', 'footerReference', 'footnotePr', 'endnotePr', 'type', 'pgSz', 'pgMar', 'paperSrc',
               'pgBorders', 'lnNumType', 'pgNumType', 'cols', 'formProt', 'vAlign', 'noEndnote', 'titlePg',
               'textDirection', 'bidi', 'rtlGutter', 'docGrid', 'printerSettings', 'sectPrChange'],
}
SCHEMA_ORDER['sectPr_rank'] = {'headerReference': 0, 'footerReference': 0}


def normalize(root):
    """Put the children of every pPr, rPr, tblPr, tcPr and sectPr in the order of the schema, once each; some
    source files have them out of order or twice, which Word may report as unreadable content. Returns the number of
    property lists changed."""
    w = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    n = 0
    for tag, order in SCHEMA_ORDER.items():
        if tag.endswith('_rank'):
            continue
        rank = {name: k for k, name in enumerate(order)}
        rank.update(SCHEMA_ORDER.get(tag + '_rank', {}))
        for el in root.iter(w + tag):
            kids = [c for c in el if isinstance(c.tag, str)]
            wk = [c for c in kids if c.tag.startswith(w)]
            if any(c.tag[len(w):] not in rank for c in wk):
                continue
            last = {}
            for c in wk:                                        # a property given twice: the later one counts
                if c.tag[len(w):] not in ('headerReference', 'footerReference'):
                    last[c.tag] = c
            wk = [c for c in wk if c.tag[len(w):] in ('headerReference', 'footerReference') or last[c.tag] is c]
            want = sorted(wk, key=lambda c: rank[c.tag[len(w):]]) + [c for c in kids if not c.tag.startswith(w)]
            if want != kids:
                for c in kids:
                    el.remove(c)
                for c in want:
                    el.append(c)
                n += 1
    return n


def arial_runs(elements):
    """Set the technical note in Arial; its size, colour and spacing come from its own defaults (base_style)."""
    for el in elements:
        for r in el.iter(qn('w:r')):
            rPr = r.find(qn('w:rPr'))
            if rPr is None:
                rPr = OxmlElement('w:rPr')
                r.insert(0, rPr)
            f = rPr.find(qn('w:rFonts'))
            if f is None:
                f = OxmlElement('w:rFonts')
                rpr_insert(rPr, f)
            for a in list(f.attrib):
                if a.endswith('Theme'):
                    del f.attrib[a]
            for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
                f.set(qn(a), FONT)


def fix_text(elements):
    """A doubled semicolon in the source, also across two runs."""
    n = 0
    for el in elements:
        for p in el.iter(qn('w:p')):
            prev = None
            for t in p.iter(qn('w:t')):
                if t.text and ';;' in t.text:
                    n += t.text.count(';;')
                    t.text = t.text.replace(';;', ';')
                if prev is not None and t.text and t.text.startswith(';') and (prev.text or '').endswith(';'):
                    t.text = t.text[1:]
                    n += 1
                if t.text:
                    prev = t
    return n


def omml_subscript(base, sub):
    return parse_xml(f'<m:oMath {nsdecls("m", "w")}><m:sSub><m:e><m:r><m:t>{base}</m:t></m:r></m:e><m:sub><m:r>'
                     f'<m:t>{sub}</m:t></m:r></m:sub></m:sSub></m:oMath>')


def latex_leftovers(elements):
    """Text such as '$w_T$' left in a table heading becomes native math."""
    n = 0
    for el in elements:
        for t in list(el.iter(qn('w:t'))):
            m = re.search(r'\$([A-Za-z])_([A-Za-z0-9])\$', t.text or '')
            if not m:
                continue
            r = t.getparent()
            before, after = t.text[:m.start()], t.text[m.end():]
            t.text = before
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            math = omml_subscript(m.group(1), m.group(2))
            r.addnext(math)
            if after:
                r2 = copy.deepcopy(r)
                t2 = r2.find(qn('w:t'))
                t2.text = after
                math.addnext(r2)
            n += 1
    return n


def strip_noise(elements):
    """No comments, no tracked changes, no Word 2010 paragraph ids (they would repeat across the parts)."""
    for el in elements:
        for tag in ('w:commentRangeStart', 'w:commentRangeEnd'):
            for x in list(el.iter(qn(tag))):
                x.getparent().remove(x)
        for x in list(el.iter(qn('w:commentReference'))):
            r = x.getparent()
            r.getparent().remove(r)
        for x in list(el.iter(qn('w:del'))):
            x.getparent().remove(x)
        for x in list(el.iter(qn('w:ins'))):
            parent = x.getparent()
            idx = parent.index(x)
            for k, child in enumerate(list(x)):
                parent.insert(idx + k, child)
            parent.remove(x)
        for node in el.iter():
            for a in ('paraId', 'textId'):
                if node.get(f'{{{W14}}}{a}') is not None:
                    del node.attrib[f'{{{W14}}}{a}']


def remap_relationships(elements, src, dst):
    for el in elements:
        for node in el.iter():
            for att in (qn('r:embed'), qn('r:id'), qn('r:link')):
                rid = node.get(att)
                if not rid or node.tag in (qn('w:headerReference'), qn('w:footerReference')):
                    continue
                rel = src.part.rels[rid]
                if rel.is_external:
                    new = dst.part.relate_to(rel.target_ref, rel.reltype, is_external=True)
                elif rel.reltype == RT.IMAGE:
                    new, _ = dst.part.get_or_add_image(io.BytesIO(rel.target_part.blob))
                else:
                    raise RuntimeError(f'unhandled relationship {rel.reltype}')
                node.set(att, new)


SPACING_BUILTIN = {'before': '0', 'after': '0', 'line': '240', 'lineRule': 'auto'}


def _defaults(doc):
    dd = doc.styles.element.find(qn('w:docDefaults'))
    if dd is None:
        return None, None
    return dd.find(f"{qn('w:rPrDefault')}/{qn('w:rPr')}"), dd.find(f"{qn('w:pPrDefault')}/{qn('w:pPr')}")


def _set_fonts(rPr, font):
    f = rPr.find(qn('w:rFonts'))
    if f is None:
        f = OxmlElement('w:rFonts')
        rpr_insert(rPr, f)
    for a in list(f.attrib):
        if a.endswith('Theme'):
            del f.attrib[a]
    for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        f.set(qn(a), font)


def base_style(src, dst, prefix, font=None):
    """The style <prefix>Normal: the part's Normal style over the part's document defaults, kept where they differ
    from the master's, so that the body text of the part keeps its own font, size, colour and spacing."""
    s_r, s_p = _defaults(src)
    d_r, d_p = _defaults(dst)
    rPr, pPr = OxmlElement('w:rPr'), OxmlElement('w:pPr')
    for tag in ('w:rFonts', 'w:color', 'w:sz', 'w:szCs'):
        a = s_r.find(qn(tag)) if s_r is not None else None
        b = d_r.find(qn(tag)) if d_r is not None else None
        if a is not None and (b is None or dict(a.attrib) != dict(b.attrib)):
            rpr_insert(rPr, copy.deepcopy(a))
        elif a is None and b is not None and tag in ('w:sz', 'w:szCs'):
            x = OxmlElement(tag)
            x.set(qn('w:val'), '20')                            # Word's own default, 10 pt
            rpr_insert(rPr, x)
    a = s_p.find(qn('w:spacing')) if s_p is not None else None
    b = d_p.find(qn('w:spacing')) if d_p is not None else None
    sp = OxmlElement('w:spacing')
    for k, v in SPACING_BUILTIN.items():
        sv = a.get(qn(f'w:{k}')) if a is not None and a.get(qn(f'w:{k}')) is not None else v
        dv = b.get(qn(f'w:{k}')) if b is not None and b.get(qn(f'w:{k}')) is not None else v
        if sv != dv:
            sp.set(qn(f'w:{k}'), sv)
    if sp.get(qn('w:line')) is not None and sp.get(qn('w:lineRule')) is None:   # a line height needs its rule
        sp.set(qn('w:lineRule'), a.get(qn('w:lineRule')) if a is not None and a.get(qn('w:lineRule')) else 'auto')
    normal = next((s for s in src.styles.element.findall(qn('w:style'))
                   if s.get(qn('w:type')) == 'paragraph' and s.get(qn('w:default')) == '1'), None)
    if normal is not None:
        npPr, nrPr = normal.find(qn('w:pPr')), normal.find(qn('w:rPr'))
        for child in (list(npPr) if npPr is not None else []):
            if child.tag == qn('w:spacing'):
                for k, v in child.attrib.items():
                    sp.set(k, v)
                continue
            for x in pPr.findall(child.tag):
                pPr.remove(x)
            ppr_insert(pPr, copy.deepcopy(child))
        for child in (list(nrPr) if nrPr is not None else []):
            for x in rPr.findall(child.tag):
                rPr.remove(x)
            rpr_insert(rPr, copy.deepcopy(child))
    if len(sp.attrib):
        ppr_insert(pPr, sp)
    if font:
        _set_fonts(rPr, font)
    nid = prefix + 'Normal'
    st = parse_xml(f'<w:style {nsdecls("w")} w:type="paragraph" w:customStyle="1" w:styleId="{nid}">'
                   f'<w:name w:val="{prefix} Normal"/><w:qFormat/></w:style>')
    if len(pPr):
        st.append(pPr)
    if len(rPr):
        st.append(rPr)
    dst.styles.element.append(st)
    return nid


def copy_styles(elements, src, dst, prefix, normal_id, font=None):
    """The styles the part uses, and the styles they are based on, are copied under new ids. The part's Normal
    style becomes normal_id (base_style), and so does the style of every paragraph that names none."""
    src_styles = {}
    for s in src.styles.element.findall(qn('w:style')):
        src_styles[s.get(qn('w:styleId'))] = s                  # a later definition of a repeated id wins
    dst_ids = {s.get(qn('w:styleId')) for s in dst.styles.element.findall(qn('w:style'))}
    para_default = next((sid for sid, s in src_styles.items()
                         if s.get(qn('w:type')) == 'paragraph' and s.get(qn('w:default')) == '1'), 'Normal')
    keep = {sid for sid, s in src_styles.items() if s.get(qn('w:default')) == '1' and sid != para_default}
    keep |= {'TableGrid'} & dst_ids
    used = set()
    for el in elements:
        for tag in ('w:pStyle', 'w:rStyle', 'w:tblStyle'):
            for x in el.iter(qn(tag)):
                used.add(x.get(qn('w:val')))
    todo = list(used)
    while todo:                                                 # the styles they are based on
        s = src_styles.get(todo.pop())
        b = s.find(qn('w:basedOn')) if s is not None else None
        if b is not None and b.get(qn('w:val')) not in used:
            used.add(b.get(qn('w:val')))
            todo.append(b.get(qn('w:val')))
    rename = {para_default: normal_id, 'Normal': normal_id}
    for sid in sorted(used):
        if sid not in rename and sid not in keep and sid in src_styles:
            rename[sid] = prefix + sid
    for sid, nid in rename.items():
        if nid == normal_id:
            continue
        new = copy.deepcopy(src_styles[sid])
        new.set(qn('w:styleId'), nid)
        if new.get(qn('w:default')) is not None:
            del new.attrib[qn('w:default')]
        name = new.find(qn('w:name'))
        name.set(qn('w:val'), f'{prefix} {name.get(qn("w:val"))}')
        for k in ('w:basedOn', 'w:next', 'w:link'):
            x = new.find(qn(k))
            if x is None:
                continue
            v = x.get(qn('w:val'))
            if v in rename:
                x.set(qn('w:val'), rename[v])
            elif not (k == 'w:basedOn' and v in keep):
                new.remove(x)
        if font and new.find(qn('w:rPr')) is not None and new.find(qn('w:rPr')).find(qn('w:rFonts')) is not None:
            _set_fonts(new.find(qn('w:rPr')), font)
        nm = src_styles[sid].find(qn('w:name'))
        m = re.match(r'(?i)heading ([1-3])\b', (nm.get(qn('w:val')) or '') if nm is not None else '')
        lvl = int(m.group(1)) if m else None             # also 'Heading 1 (no outline)' (word_outline.py)
        if lvl is not None:                                     # under the level of the part banners
            pPr = new.find(qn('w:pPr'))
            if pPr is None:
                pPr = OxmlElement('w:pPr')
                rPr = new.find(qn('w:rPr'))
                if rPr is not None:
                    rPr.addprevious(pPr)
                else:
                    new.append(pPr)
            for x in pPr.findall(qn('w:outlineLvl')):
                pPr.remove(x)
            o = OxmlElement('w:outlineLvl')
            o.set(qn('w:val'), str(lvl))
            ppr_insert(pPr, o)
            if pPr.find(qn('w:keepNext')) is None:
                ppr_insert(pPr, OxmlElement('w:keepNext'))
        if nid not in dst_ids:
            dst.styles.element.append(new)
    for el in elements:
        for tag in ('w:pStyle', 'w:rStyle', 'w:tblStyle'):
            for x in el.iter(qn(tag)):
                if x.get(qn('w:val')) in rename:
                    x.set(qn('w:val'), rename[x.get(qn('w:val'))])
        for p in el.iter(qn('w:p')):
            pPr = p.find(qn('w:pPr'))
            if pPr is None:
                pPr = OxmlElement('w:pPr')
                p.insert(0, pPr)
            if pPr.find(qn('w:pStyle')) is None:
                ps = OxmlElement('w:pStyle')
                ps.set(qn('w:val'), normal_id)
                pPr.insert(0, ps)


def copy_numbering(elements, src, dst):
    used = sorted({int(x.get(qn('w:val'))) for el in elements for x in el.iter(qn('w:numId'))})
    used = [u for u in used if u != 0]
    if not used:
        return
    sn = src.part.numbering_part.element
    dn = dst.part.numbering_part.element
    abs_ids = [int(a.get(qn('w:abstractNumId'))) for a in dn.findall(qn('w:abstractNum'))]
    num_ids = [int(n.get(qn('w:numId'))) for n in dn.findall(qn('w:num'))]
    next_abs, next_num = max(abs_ids + [0]) + 1, max(num_ids + [0]) + 1
    remap, abs_map = {}, {}
    for nid in used:
        num = next(n for n in sn.findall(qn('w:num')) if int(n.get(qn('w:numId'))) == nid)
        aid = int(num.find(qn('w:abstractNumId')).get(qn('w:val')))
        if aid not in abs_map:
            a = copy.deepcopy(next(x for x in sn.findall(qn('w:abstractNum')) if int(x.get(qn('w:abstractNumId'))) == aid))
            a.set(qn('w:abstractNumId'), str(next_abs))
            for x in a.findall(qn('w:nsid')):
                a.remove(x)
            first_num = dn.find(qn('w:num'))
            if first_num is not None:
                first_num.addprevious(a)
            else:
                dn.append(a)
            abs_map[aid] = next_abs
            next_abs += 1
        n2 = copy.deepcopy(num)
        n2.set(qn('w:numId'), str(next_num))
        n2.find(qn('w:abstractNumId')).set(qn('w:val'), str(abs_map[aid]))
        dn.append(n2)
        remap[nid] = next_num
        next_num += 1
    for el in elements:
        for x in el.iter(qn('w:numId')):
            v = int(x.get(qn('w:val')))
            if v in remap:
                x.set(qn('w:val'), str(remap[v]))


def prefix_bookmarks(elements, prefix, id_offset):
    names = {}
    for el in elements:
        for b in el.iter(qn('w:bookmarkStart')):
            old = b.get(qn('w:name'))
            names[old] = f'{prefix}{old}'
            b.set(qn('w:name'), names[old])
        for tag in ('w:bookmarkStart', 'w:bookmarkEnd'):
            for b in el.iter(qn(tag)):
                b.set(qn('w:id'), str(int(b.get(qn('w:id'))) + id_offset))
    for el in elements:
        for h in el.iter(qn('w:hyperlink')):
            a = h.get(qn('w:anchor'))
            if a in names:
                h.set(qn('w:anchor'), names[a])
        for it in el.iter(qn('w:instrText')):
            for old, new in names.items():
                it.text = re.sub(rf'\b{re.escape(old)}\b', new, it.text or '')


def strip_section_refs(sectPr):
    for tag in ('w:headerReference', 'w:footerReference', 'w:titlePg'):
        for x in sectPr.findall(qn(tag)):
            sectPr.remove(x)
    return sectPr


# ------------------------------------------------------------------------------------------------ the document
def cover(doc):
    para(doc, 2, before=0)
    p = para(doc, 6)
    run(p, 'NATO Science for Peace and Security Programme  ·  Multi-Year Project  ·  Call 2027-1', size=8,
        color=GREY, caps=True, spacing=6)
    pPr = p._p.get_or_add_pPr()
    bdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="6" w:color="{NAVY}"/></w:pBdr>')
    ppr_insert(pPr, bdr)
    para(doc, 0, before=40)
    p = para(doc, 4)
    run(p, 'CERTAIN-COAST', size=40, bold=True, color=NAVY, spacing=20)
    p = para(doc, 26)
    run(p, TITLE, size=15, color=BLUE)
    p = para(doc, 4)
    run(p, 'Additional files', size=26, bold=True, color=INK)
    p = para(doc, 18)
    run(p, 'Technical annex  ·  three notes of the preparatory work  ·  CVs of the two Project Directors', size=11,
        color=GREY)
    if os.path.exists(COVER_FIG):
        p = para(doc, 18, align=WD_ALIGN_PARAGRAPH.CENTER)
        p.add_run().add_picture(COVER_FIG, width=Cm(14.5))
    t = doc.add_table(rows=3, cols=2)
    borders(t, None)
    widths(t, [5.2, 11.8])
    rows = [('NATO-country Project Director', 'Assoc. Prof. Dr. Dulian Zeqiraj',
             'Faculty of Geology and Mining, Polytechnic University of Tirana, Albania'),
            ('Partner-country Project Director', 'Prof. Jassim Al-Khayat',
             'Environmental Science Center, Qatar University, Qatar'),
            ('End-user', 'Ministry of Infrastructure and Energy', 'Republic of Albania')]
    for i, (role, name, inst) in enumerate(rows):
        c0, c1 = t.rows[i].cells
        p0 = c0.paragraphs[0]
        run(p0, role, size=9, color=GREY, caps=True)
        p1 = c1.paragraphs[0]
        run(p1, name, size=10.5, bold=True, color=INK)
        p2 = c1.add_paragraph()
        run(p2, inst, size=9.5, color=GREY)
        p2.paragraph_format.space_after = Pt(8)
    p = para(doc, 0, before=10)
    run(p, 'November 2026', size=10, color=GREY)


def contents(doc, pages):
    p = para(doc, 10)
    run(p, 'Contents', size=22, bold=True, color=NAVY)
    outline(p, 0)                                       # a bookmark of the PDF
    t = doc.add_table(rows=1, cols=3)
    borders(t, 'C9D3E0', 4)
    widths(t, [1.6, 13.4, 2.0])
    hdr = t.rows[0].cells
    for c, txt, al in zip(hdr, ('Part', 'Document', 'Page'), (WD_ALIGN_PARAGRAPH.CENTER, None, WD_ALIGN_PARAGRAPH.CENTER)):
        shade(c, NAVY)
        q = c.paragraphs[0]
        if al is not None:
            q.alignment = al
        run(q, txt, size=9.5, bold=True, color='FFFFFF')
    for i in range(len(PARTS)):
        row = t.add_row().cells
        if i % 2:
            for c in row:
                shade(c, 'F6F8FB')
        q = row[0].paragraphs[0]
        q.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run(q, str(i + 1), size=12, bold=True, color=BLUE)
        q = row[1].paragraphs[0]
        q.paragraph_format.space_after = Pt(1)
        run(q, english(SHORT[i]), size=10.5, bold=True, color=INK)
        q2 = row[1].add_paragraph()
        q2.paragraph_format.space_after = Pt(4)
        run(q2, BLURB[i], size=8.5, color=GREY)
        q = row[2].paragraphs[0]
        q.alignment = WD_ALIGN_PARAGRAPH.CENTER
        field(q, f'PAGEREF part{i + 1} \\h', str(pages[i]) if pages else '–', size=11, color=NAVY, bold=True)
    for row in t.rows:
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    innovations(doc)
    p = para(doc, 6, before=12)
    run(p, 'About these files', size=12, bold=True, color=NAVY)
    notes = [
        'The technical annex explains how the methods work, the preparatory tests, and the gates of the project with '
        'their fallbacks. Parts 2 to 4 give the equations, the proofs and the numerical checks behind it; every number '
        'in them is computed by the scripts of the preparatory work of the NPD\'s team.',
        'Every equation is set as native Word math. The names of the preparatory experiments are given in English '
        '(BEYOND-GO, SHOCK-GO, ASSEMBLY-GO, ...).',
        'The open-source code of the project (MATLAB, also runs in the free GNU Octave): ']
    for k, n_ in enumerate(notes):
        q = para(doc, 4)
        q.paragraph_format.left_indent = Cm(0.5)
        q.paragraph_format.first_line_indent = Cm(-0.4)
        run(q, '■  ', size=7, color=BLUE)
        run(q, n_, size=9.5, color=INK)
        if k == len(notes) - 1:
            hyperlink(q, REPO, REPO, size=9.5)
            run(q, ', archived on Zenodo with the DOI ', size=9.5, color=INK)
            hyperlink(q, f'https://doi.org/{DOI}', DOI, size=9.5)
            run(q, '.', size=9.5, color=INK)


def innovations(doc):
    """What is new in each part, in the words of the part itself."""
    p = para(doc, 2, before=12)
    run(p, 'Innovation  ', size=8, bold=True, color=ORANGE, caps=True, spacing=10)
    run(p, 'What is new in each part', size=12, bold=True, color=NAVY)
    t = doc.add_table(rows=0, cols=2)
    borders(t, None)
    tblPr = t._tbl.tblPr
    b = tblPr.find(qn('w:tblBorders'))
    for side in ('top', 'bottom', 'insideH'):
        e = b.find(qn(f'w:{side}'))
        e.set(qn('w:val'), 'single')
        e.set(qn('w:sz'), '4')
        e.set(qn('w:color'), 'F0C9A8')
    widths(t, [3.4, 13.6])
    for name, part, text in NEW:
        c0, c1 = t.add_row().cells
        shade(c0, CREAM)
        q = c0.paragraphs[0]
        q.paragraph_format.space_before = Pt(4)
        q.paragraph_format.space_after = Pt(0)
        run(q, name, size=9.5, bold=True, color=ORANGE)
        q = c0.add_paragraph()
        q.paragraph_format.space_after = Pt(4)
        run(q, f'Part {part}', size=8, color=GREY)
        q = c1.paragraphs[0]
        q.paragraph_format.space_before = Pt(4)
        q.paragraph_format.space_after = Pt(4)
        run(q, text, size=9, color=INK)
    for row in t.rows:
        row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))


def banner(doc_body_anchor, doc, i, bid):
    """The coloured block that opens part i, with the bookmark that the contents page refers to."""
    t = doc.add_table(rows=1, cols=2)
    borders(t, None)
    widths(t, [2.4, 14.6])
    c0, c1 = t.rows[0].cells
    shade(c0, NAVY)
    shade(c1, LIGHT)
    for c in (c0, c1):
        tcPr = c._tc.get_or_add_tcPr()
        va = OxmlElement('w:vAlign')
        va.set(qn('w:val'), 'center')
        tcPr.append(va)
    q = c0.paragraphs[0]
    q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    q.paragraph_format.space_before = Pt(4)
    q.paragraph_format.space_after = Pt(0)
    run(q, 'PART', size=8, bold=True, color='BFD3EA', spacing=20)
    q = c0.add_paragraph()
    q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    q.paragraph_format.space_after = Pt(4)
    run(q, str(i + 1), size=24, bold=True, color='FFFFFF')
    q = c1.paragraphs[0]
    q.paragraph_format.space_before = Pt(5)
    q.paragraph_format.space_after = Pt(2)
    q.paragraph_format.left_indent = Cm(0.2)
    run(q, english(SHORT[i]), size=13, bold=True, color=NAVY)
    outline(q, 0)
    bookmark(q, f'part{i + 1}', bid)
    q = c1.add_paragraph()
    q.paragraph_format.left_indent = Cm(0.2)
    q.paragraph_format.space_after = Pt(5)
    run(q, BLURB[i], size=8.5, color=GREY)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    gap = para(doc, 10)
    return [t._tbl, gap._p]


def header_footer(section, part_label, text_width_cm, clear_tabs=()):
    h = section.header
    h.is_linked_to_previous = False
    p = h.paragraphs[0]
    p.text = ''
    pPr = p._p.get_or_add_pPr()
    ppr_insert(pPr, parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="4" w:space="4" w:color="B8C4D4"/>'
                              f'</w:pBdr>'))
    cleared = ''.join(f'<w:tab w:val="clear" w:pos="{x}"/>' for x in clear_tabs)
    ppr_insert(pPr, parse_xml(f'<w:tabs {nsdecls("w")}>{cleared}<w:tab w:val="right" '
                              f'w:pos="{int(text_width_cm * 567)}"/></w:tabs>'))
    run(p, 'CERTAIN-COAST', size=8, bold=True, color=NAVY)
    run(p, '  ·  Additional files', size=8, color=GREY)
    run(p, '\t' + part_label, size=8, italic=True, color=GREY)


def footer(section):
    f = section.footer
    f.is_linked_to_previous = False
    p = f.paragraphs[0]
    p.text = ''
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'page ', size=8, color=GREY)
    field(p, 'PAGE', '1', size=8, color=GREY)
    run(p, ' of ', size=8, color=GREY)
    field(p, 'NUMPAGES', '1', size=8, color=GREY)


def build(out, pages):
    work = tempfile.mkdtemp()
    doc = Document()
    st = doc.styles['Normal']
    st.font.name = FONT
    st.font.size = Pt(10.5)
    st.element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), FONT)
    s0 = doc.sections[0]
    s0.page_width, s0.page_height = Cm(21.0), Cm(29.7)
    s0.left_margin = s0.right_margin = Cm(2.0)
    s0.top_margin, s0.bottom_margin = Cm(1.8), Cm(1.6)
    body = doc.element.body
    final = body.find(qn('w:sectPr'))

    cover(doc)
    p = para(doc, 0)
    p.add_run().add_break(WD_BREAK.PAGE)
    contents(doc, pages)
    # end of section 1 (cover and contents): a paragraph that holds a copy of its sectPr
    sect1 = copy.deepcopy(final)
    endp = OxmlElement('w:p')
    endpPr = OxmlElement('w:pPr')
    endpPr.append(sect1)
    endp.append(endpPr)
    final.addprevious(endp)

    part_sections = []                                  # index of the first section of each part
    n_sect = 1
    bid = 9000
    for i, (_, _, src_path) in enumerate(PARTS):
        if src_path.endswith('.pdf'):                   # the annex is listed by its PDF; its Word source sits beside it
            src_path = src_path[:-4] + '.docx'
        src_copy = os.path.join(work, f'part{i + 1}.docx')
        english_docx(src_path, src_copy)
        src = Document(src_copy)
        sbody = src.element.body
        elements = [copy.deepcopy(x) for x in sbody if x.tag != qn('w:sectPr')]
        src_final = copy.deepcopy(sbody.find(qn('w:sectPr')))
        strip_noise(elements)
        remap_relationships(elements, src, doc)
        font = FONT if i == 1 else None                 # the technical note: Cambria and Calibri become Arial
        normal_id = base_style(src, doc, f'P{i + 1}', font)
        copy_styles(elements, src, doc, f'P{i + 1}', normal_id, font)
        copy_numbering(elements, src, doc)
        prefix_bookmarks(elements, f'p{i + 1}_', id_offset=(i + 1) * 100000)
        fixed = latex_leftovers(elements)
        if fixed:
            print(f'  part {i + 1}: {fixed} equation(s) left as text set as native math')
        if i == 1:
            arial_runs(elements)
        n_fix = fix_text(elements)
        if n_fix:
            print(f'  part {i + 1}: {n_fix} doubled semicolon(s) removed')
        for el in elements:
            for s in el.iter(qn('w:sectPr')):
                strip_section_refs(s)
        # the banner, then the content of the part, then its own last section
        made = banner(None, doc, i, bid)
        bid += 1
        for el in made:
            final.addprevious(el)
        for el in elements:
            final.addprevious(el)
        part_sections.append(n_sect)
        n_sect += 1 + sum(1 for el in elements for _ in el.iter(qn('w:sectPr')))
        strip_section_refs(src_final)
        if i < len(PARTS) - 1:
            endp = OxmlElement('w:p')
            endpPr = OxmlElement('w:pPr')
            endpPr.append(src_final)
            endp.append(endpPr)
            final.addprevious(endp)
        else:
            final.getparent().replace(final, src_final)
            final = src_final

    # headers and footers: none on the cover; the part title in the header of each part
    secs = doc.sections
    secs[0].different_first_page_header_footer = True
    footer(secs[0])
    hstyle = next(s for s in doc.styles.element.findall(qn('w:style')) if s.get(qn('w:styleId')) == 'Header')
    clear_tabs = [t.get(qn('w:pos')) for t in hstyle.iter(qn('w:tab'))]
    for i, k in enumerate(part_sections):
        s = secs[k]
        text_w = (s.page_width - s.left_margin - s.right_margin) / 360000
        header_footer(s, f'Part {i + 1}  ·  {HEADER[i]}', text_w, clear_tabs)
    # unique drawing ids
    for k, d in enumerate(body.iter('{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr'),
                          start=1):
        d.set('id', str(k))
    for k, d in enumerate(body.iter('{http://schemas.openxmlformats.org/drawingml/2006/picture}cNvPr'), start=1):
        d.set('id', str(k))
    fixed = normalize(body) + normalize(doc.styles.element) + normalize(doc.part.numbering_part.element)
    for s in secs:
        for hf in (s.header, s.footer, s.first_page_header, s.first_page_footer):
            if not hf.is_linked_to_previous:
                fixed += normalize(hf._element)
    print(f'  {fixed} property lists put in schema order')
    doc.core_properties.title = 'CERTAIN-COAST: Additional files'
    doc.core_properties.author = 'Dulian Zeqiraj'
    doc.core_properties.subject = 'NATO SPS Multi-Year Project application, call 2027-1'
    doc.save(out)
    return len(secs)


def pdf_of(docx_path, outdir):
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', outdir, docx_path], check=True,
                   capture_output=True, timeout=900)
    return os.path.join(outdir, os.path.splitext(os.path.basename(docx_path))[0] + '.pdf')


def part_pages(pdf):
    """First page of each part in the PDF rendering (where its banner title stands)."""
    from pypdf import PdfReader
    rd = PdfReader(pdf)
    texts = [re.sub(r'\s+', ' ', (pg.extract_text() or '')) for pg in rd.pages]
    out, start = [], 2
    for i in range(len(PARTS)):
        key = re.sub(r'\s+', ' ', english(SHORT[i]))[:40]
        k = next(j for j in range(start, len(texts)) if key in texts[j])
        out.append(k + 1)
        start = k + 1
    return out, len(texts)


def main(out, pdf_out=None):
    work = tempfile.mkdtemp()
    first = os.path.join(work, 'pass1.docx')
    build(first, None)
    pages, n = part_pages(pdf_of(first, work))
    n_sec = build(out, pages)
    print('saved', out, '| sections', n_sec, '| parts start on pages', pages, '| pages', n)
    if pdf_out:
        pdf = pdf_of(out, work)                         # while the headings have outline levels: PDF bookmarks
        os.replace(pdf, pdf_out)
        print('saved', pdf_out)
    n_lvl, n_ren = plain_headings(out)
    print(f'  Word file: {n_lvl} outline levels removed, {n_ren} built-in heading styles renamed (no collapse arrows)')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Additional_Files.docx',
         sys.argv[2] if len(sys.argv) > 2 else None)
