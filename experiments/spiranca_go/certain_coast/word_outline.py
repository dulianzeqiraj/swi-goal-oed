"""Headings without the collapse arrow of Word.

Word draws a small triangle to the left of every paragraph that has an outline level (the built-in Heading styles, and
any style or paragraph with w:outlineLvl), to fold the text under it. plain_headings keeps the look of the headings
and removes their outline level: every w:outlineLvl in the styles, the list numbering, the body, the headers and the
footers is dropped, and the built-in heading styles get a name and id of their own, because Word fixes the outline
level of a style called "heading 1" to level 1 whatever the file says. Fonts, sizes, colours, spacing and
keep-with-next are not touched, so the pages are the same.

The headings then no longer appear in the Navigation Pane of Word or as bookmarks of a PDF made from the file, so make
the PDF first, from the file with outline levels.

usage: python word_outline.py IN.docx [OUT.docx]"""
import os
import re
import shutil
import sys
import tempfile
import zipfile

from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
PARTS = re.compile(r'word/(document|styles|stylesWithEffects|numbering|header\d*|footer\d*|footnotes|endnotes)\.xml$')


def _w(tag):
    return f'{{{W}}}{tag}'


def plain_headings(src, dst=None):
    """Write SRC to DST (default: in place) with no outline levels; returns (outline levels removed, styles renamed)."""
    dst = dst or src
    with zipfile.ZipFile(src) as zin:
        entries = [(info, zin.read(info.filename)) for info in zin.infolist()]
    trees = {info.filename: etree.fromstring(data) for info, data in entries if PARTS.match(info.filename)}

    # the built-in heading styles become styles of their own: "heading 1" -> "Heading 1 (no outline)", id HeadingPlain1
    rename = {}
    styles = trees.get('word/styles.xml')
    if styles is not None:
        ids = {s.get(_w('styleId')) for s in styles.iter(_w('style'))}
        for s in styles.iter(_w('style')):
            name = s.find(_w('name'))
            m = re.fullmatch(r'(?i)heading ([1-9])', name.get(_w('val')) if name is not None else '')
            if s.get(_w('type')) != 'paragraph' or not m:
                continue
            new_id = f'HeadingPlain{m.group(1)}'
            while new_id in ids:
                new_id += 'x'
            ids.add(new_id)
            rename[s.get(_w('styleId'))] = new_id
            s.set(_w('styleId'), new_id)
            name.set(_w('val'), f'Heading {m.group(1)} (no outline)')
    effects = trees.get('word/stylesWithEffects.xml')          # the copy of the styles kept for Word 2010
    if effects is not None:
        for s in effects.iter(_w('style')):
            if s.get(_w('styleId')) in rename:
                k = re.sub(r'\D', '', rename[s.get(_w('styleId'))])
                s.set(_w('styleId'), rename[s.get(_w('styleId'))])
                if s.find(_w('name')) is not None:
                    s.find(_w('name')).set(_w('val'), f'Heading {k} (no outline)')

    n_lvl = 0
    for name, root in trees.items():
        for o in list(root.iter(_w('outlineLvl'))):
            o.getparent().remove(o)
            n_lvl += 1
        if rename:
            for tag in ('pStyle', 'basedOn', 'next', 'link'):
                for x in root.iter(_w(tag)):
                    if x.get(_w('val')) in rename:
                        x.set(_w('val'), rename[x.get(_w('val'))])

    fd, tmp = tempfile.mkstemp(suffix='.docx', dir=os.path.dirname(os.path.abspath(dst)))
    os.close(fd)
    with zipfile.ZipFile(tmp, 'w') as zout:
        for info, data in entries:
            if info.filename in trees:
                data = etree.tostring(trees[info.filename], xml_declaration=True, encoding='UTF-8', standalone=True)
            zout.writestr(info, data)
    shutil.move(tmp, dst)
    return n_lvl, len(rename)


if __name__ == '__main__':
    n, k = plain_headings(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(f'{n} outline levels removed, {k} built-in heading styles renamed')
