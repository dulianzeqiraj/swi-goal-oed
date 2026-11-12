"""CERTAIN-COAST: PDF of a filled official NATO SPS template (e.g. the Acceptance of Funds) made with LibreOffice.

The header of the NATO templates holds the SPS logo behind the centred title. Word wraps the title round the logo;
LibreOffice draws the title over it, so "NATO" is half hidden in the PDF. This script converts a copy in which the
header lines are indented by 2.5 cm, clear of the logo; the Word file itself is not changed.

usage: python nato_template_pdf.py IN.docx OUT.pdf
Needs LibreOffice (soffice) and lxml."""
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
PPR_ORDER = ['pStyle', 'keepNext', 'keepLines', 'pageBreakBefore', 'framePr', 'widowControl', 'numPr',
             'suppressLineNumbers', 'pBdr', 'shd', 'tabs', 'suppressAutoHyphens', 'kinsoku', 'wordWrap', 'overflowPunct',
             'topLinePunct', 'autoSpaceDE', 'autoSpaceDN', 'bidi', 'adjustRightInd', 'snapToGrid', 'spacing', 'ind',
             'contextualSpacing', 'mirrorIndents', 'suppressOverlap', 'jc', 'textDirection', 'textAlignment',
             'textboxTightWrap', 'outlineLvl', 'divId', 'cnfStyle', 'rPr', 'sectPr', 'pPrChange']
INDENT = '1418'                                             # 2.5 cm in twentieths of a point


def _w(tag):
    return f'{{{W}}}{tag}'


def indent_header(xml):
    """Indent every header paragraph that has text; returns the new XML and the number of paragraphs changed."""
    root = etree.fromstring(xml)
    n = 0
    for p in root.iter(_w('p')):
        if not ''.join(t.text or '' for t in p.iter(_w('t'))).strip():
            continue
        pPr = p.find(_w('pPr'))
        if pPr is None:
            pPr = etree.Element(_w('pPr'))
            p.insert(0, pPr)
        for x in pPr.findall(_w('ind')):
            pPr.remove(x)
        ind = etree.Element(_w('ind'))
        ind.set(_w('left'), INDENT)
        rank = PPR_ORDER.index('ind')
        for child in list(pPr):
            name = child.tag.split('}')[1]
            if name in PPR_ORDER and PPR_ORDER.index(name) > rank:
                child.addprevious(ind)
                break
        else:
            pPr.append(ind)
        n += 1
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True), n


def main(src, pdf_out):
    work = tempfile.mkdtemp()
    copy = os.path.join(work, os.path.basename(src))
    changed = 0
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(copy, 'w', zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.startswith('word/header') and info.filename.endswith('.xml'):
                data, n = indent_header(data)
                changed += n
            zout.writestr(info, data)
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', work, copy], check=True,
                   capture_output=True, timeout=600)
    shutil.move(os.path.join(work, os.path.splitext(os.path.basename(src))[0] + '.pdf'), pdf_out)
    print(f'saved {pdf_out} | {changed} header lines moved clear of the logo')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
