#!/usr/bin/env python3
"""Turn the LaTeX equations collected by build.js into native Word math (OMML)
with pandoc, and put them in place of the placeholders in the docx-js output.

usage: omml.py draft.docx equations.json final.docx
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common")); from lo_safe import lo_safe

from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
NS = {'w': W, 'm': M}


# pandoc writes some math property children out of schema order (e.g. m:sty before
# m:scr, m:endChr before m:sepChr); Word validates against this order.
PR_ORDER = {
    'rPr': ['lit', 'nor', 'scr', 'sty', 'brk', 'aln'],
    'dPr': ['begChr', 'sepChr', 'endChr', 'grow', 'shp', 'ctrlPr'],
    'naryPr': ['chr', 'limLoc', 'grow', 'subHide', 'supHide', 'ctrlPr'],
    'accPr': ['chr', 'ctrlPr'],
    'fPr': ['type', 'ctrlPr'],
    'barPr': ['pos', 'ctrlPr'],
    'groupChrPr': ['chr', 'pos', 'vertJc', 'ctrlPr'],
    'radPr': ['degHide', 'ctrlPr'],
    'sSubSupPr': ['alnScr', 'ctrlPr'],
    'mPr': ['baseJc', 'plcHide', 'rSpRule', 'cGpRule', 'rSp', 'cSp', 'cGp', 'mcs', 'ctrlPr'],
    'mcPr': ['count', 'mcJc'],
    'eqArrPr': ['baseJc', 'maxDist', 'objDist', 'rSpRule', 'rSp', 'ctrlPr'],
}


def fix_order(el):
    for pr in el.iter():
        if not isinstance(pr.tag, str) or not pr.tag.startswith('{%s}' % M):
            continue
        name = etree.QName(pr).localname
        if name == 'rPr' and pr.find('m:nor', NS) is not None:
            # \text{} comes out as m:nor + m:sty, but the schema allows nor OR (scr?, sty?)
            for k in pr.findall('m:sty', NS) + pr.findall('m:scr', NS):
                pr.remove(k)
        order = PR_ORDER.get(name)
        if not order:
            continue
        kids = list(pr)
        rank = {k: i for i, k in enumerate(order)}
        kids_sorted = sorted(kids, key=lambda k: rank.get(etree.QName(k).localname, len(order)))
        if kids_sorted != kids:
            for k in kids:
                pr.remove(k)
            for k in kids_sorted:
                pr.append(k)


def to_omml(eqs, workdir):
    """Convert every equation in one pandoc run; one paragraph per equation."""
    lines = []
    for e in eqs:
        tex = lo_safe(' '.join(e['tex'].split()))
        lines.append(f'$${tex}$$' if e['display'] else f'${tex}$')
        lines.append('')
    md = os.path.join(workdir, 'eqs.md')
    with open(md, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))
    out = os.path.join(workdir, 'eqs.docx')
    subprocess.run(['pandoc', md, '-f', 'markdown', '-o', out], check=True)
    with zipfile.ZipFile(out) as z:
        root = etree.fromstring(z.read('word/document.xml'))
    paras = root.find('w:body', NS).findall('w:p', NS)
    if len(paras) != len(eqs):
        sys.exit(f'pandoc returned {len(paras)} paragraphs for {len(eqs)} equations')
    frags = {}
    for e, p in zip(eqs, paras):
        el = p.find('m:oMathPara' if e['display'] else 'm:oMath', NS)
        if el is None or p.findall('w:r', NS):
            sys.exit(f"equation {e['id']} did not convert cleanly: {e['tex']}")
        fix_order(el)
        if e.get('size'):                       # inline math at the size of the text around it
            for r in el.iter('{%s}r' % M):
                rp = etree.Element('{%s}rPr' % W)
                etree.SubElement(rp, '{%s}sz' % W).set('{%s}val' % W, str(e['size']))
                etree.SubElement(rp, '{%s}szCs' % W).set('{%s}val' % W, str(e['size']))
                kids = list(r)
                r.insert(1 if kids and etree.QName(kids[0]).localname == 'rPr' and kids[0].tag.startswith('{%s}' % M) else 0, rp)
        s = etree.tostring(el, encoding='unicode')
        # the target document already declares these prefixes on its root
        s = re.sub(r'\s+xmlns:\w+="[^"]*"', '', s, count=0)
        frags[e['id']] = (e['display'], s)
    return frags


def inject(xml, frags):
    for i, (display, frag) in frags.items():
        ph = f'§§EQ{i}§§' if display else f'§§IQ{i}§§'
        idx = xml.find(ph)
        if idx < 0:
            sys.exit(f'placeholder {ph} not found')
        if xml.find(ph, idx + 1) >= 0:
            sys.exit(f'placeholder {ph} occurs twice')
        if display:
            start = max(xml.rfind('<w:p>', 0, idx), xml.rfind('<w:p ', 0, idx))
            end = xml.index('</w:p>', idx) + len('</w:p>')
            para = xml[start:end]
            ppr = re.search(r'<w:pPr>.*?</w:pPr>', para, re.S)
            xml = xml[:start] + '<w:p>' + (ppr.group(0) if ppr else '') + frag + '</w:p>' + xml[end:]
        else:
            start = max(xml.rfind('<w:r>', 0, idx), xml.rfind('<w:r ', 0, idx))
            end = xml.index('</w:r>', idx) + len('</w:r>')
            xml = xml[:start] + frag + xml[end:]
    if '§§' in xml:
        sys.exit('unreplaced placeholder left in document.xml')
    return xml


def set_language(styles_xml, lang='en-US'):
    """US English proofing language for the whole document."""
    if '<w:lang ' in styles_xml.split('</w:docDefaults>')[0]:
        return styles_xml
    return re.sub(r'(<w:rPrDefault>\s*<w:rPr>)', r'\1<w:lang w:val="%s" w:eastAsia="en-US" w:bidi="ar-SA"/>' % lang,
                  styles_xml, count=1)


def main(draft, eq_json, final):
    with open(eq_json, encoding='utf-8') as fh:
        eqs = json.load(fh)
    with tempfile.TemporaryDirectory() as work:
        frags = to_omml(eqs, work)
    with zipfile.ZipFile(draft) as zin:
        items = [(info, zin.read(info.filename)) for info in zin.infolist()]
    out_items = []
    for info, data in items:
        if info.filename == 'word/document.xml':
            data = inject(data.decode('utf-8'), frags).encode('utf-8')
            etree.fromstring(data)  # must still be well-formed
        elif info.filename == 'word/styles.xml':
            data = set_language(data.decode('utf-8')).encode('utf-8')
        out_items.append((info.filename, data))
    out_items.sort(key=lambda t: t[0] != '[Content_Types].xml')
    with zipfile.ZipFile(final, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, data in out_items:
            zout.writestr(name, data)
    print(f'{len(frags)} equations written as OMML -> {final}')


if __name__ == '__main__':
    main(*sys.argv[1:4])
