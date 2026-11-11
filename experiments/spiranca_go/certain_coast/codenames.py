"""English names of the preparatory experiments, for every document that goes to NATO.

The experiments of the repository keep their working names (Albanian words with the suffix -GO, for goal-oriented);
the submitted documents use the English word instead, e.g. SHTEGU-GO ("the path") -> PATH-GO.

english(text)                 the text with every working name replaced
english_docx(src, dst)        a copy of a Word file with every working name replaced (body, tables, headers, footers)
usage: python codenames.py IN.docx OUT.docx"""
import re
import sys

NAMES = {
    'SHTEGU': 'PATH', 'PËRTEJ': 'BEYOND', 'PERTEJ': 'BEYOND', 'TRONDITJA': 'SHOCK', 'MONTIMI': 'ASSEMBLY',
    'KUFIRI': 'BOUNDARY', 'GJURMA': 'TRACE', 'GARANCIA': 'GUARANTEE', 'RINDËRTIMI': 'RECONSTRUCTION',
    'RINDERTIMI': 'RECONSTRUCTION', 'PREJARDHJA': 'ORIGIN', 'PUSI': 'WELL', 'RITMI': 'RHYTHM', 'VENDI': 'SITE',
    'SPIRANCA': 'ANCHOR', 'ANKORA': 'MOORING', 'ASIMILIMI': 'ASSIMILATION', 'FILLIMI': 'START', 'LIDHJA': 'LINK',
    'PRAG': 'THRESHOLD', 'NDERHYRJA': 'INTERVENTION', 'NDËRHYRJA': 'INTERVENTION', 'DYSHEMEJA': 'FLOOR',
    'FSHEHTA': 'HIDDEN', 'KRIPA': 'SALT', 'MATJA': 'MEASURE', 'PRIRJA': 'TREND', 'RESHJA': 'PRECIPITATION',
    'SHIU': 'RAIN', 'SHKAKU': 'CAUSE', 'INFILTRIMI': 'INFILTRATION', 'OPERATORI': 'OPERATOR',
}
LOWER = {k.lower(): v for k, v in NAMES.items()}
_UP = '|'.join(sorted(NAMES, key=len, reverse=True))
_LOW = '|'.join(sorted(LOWER, key=len, reverse=True))
# a working name followed by -GO or -MAR, not part of a longer word and not a file name (followed by "_")
PATTERN = re.compile(r'(?<![A-Za-zËÇëç])(' + _UP + r')-(GO|MAR)(?![\w])')
RULES = [   # (pattern, replacement), applied in this order
    (re.compile(r' \((?:' + _LOW + r'): [^()]{1,40}\)'), lambda m: ''),                     # "(përtej: beyond)"
    (re.compile(r'docs/research_notes/(' + _UP + r')-GO_[\w.-]+\.docx'),
     lambda m: 'the ' + NAMES[m.group(1)] + '-GO research note'),
    (re.compile(r'experiments/(' + _LOW + r')_go/res\b/?'),
     lambda m: 'the results of the ' + LOWER[m.group(1)] + '-GO experiment'),
    (re.compile(r'experiments/(' + _LOW + r')_go/[\w./-]*[\w]'),
     lambda m: 'the ' + LOWER[m.group(1)] + '-GO code'),
    (re.compile(r'experiments/(' + _LOW + r')_go\b'), lambda m: 'the ' + LOWER[m.group(1)] + '-GO experiment'),
    (re.compile(r'res/(?:' + _LOW + r')\.json'), lambda m: 'its res folder'),
    (re.compile(r'\b(?:' + _LOW + r')_exp\.py'), lambda m: 'the main script'),
    (PATTERN, lambda m: NAMES[m.group(1)] + '-' + m.group(2)),
]


def english(text):
    for pat, rep in RULES:
        text = pat.sub(rep, text)
    return text


def _first(text):
    """Start and end of the earliest match of any rule, or None."""
    best = None
    for pat, _ in RULES:
        m = pat.search(text)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), m.end())
    return best


def _paragraphs(doc):
    def walk(container):
        for p in container.paragraphs:
            yield p
        for t in container.tables:
            for row in t.rows:
                for cell in row.cells:
                    yield from walk(cell)
    yield from walk(doc)
    for s in doc.sections:
        for part in (s.header, s.footer, s.first_page_header, s.first_page_footer):
            yield from walk(part)


def english_docx(src, dst):
    """Replace the working names run by run; a name split across runs is joined into the first run."""
    from docx import Document
    doc = Document(src)
    n = 0
    for p in _paragraphs(doc):
        if english(p.text) == p.text:
            continue
        runs = p.runs
        for r in runs:                                   # names inside one run
            new = english(r.text)
            if new != r.text:
                n += 1
                r.text = new
        while True:                                      # names split across runs
            full = ''.join(r.text for r in runs)
            m = _first(full)
            if m is None:
                break
            pos, starts = 0, []
            for r in runs:
                starts.append(pos)
                pos += len(r.text)
            i = max(k for k, s in enumerate(starts) if s <= m[0])
            j = max(k for k, s in enumerate(starts) if s < m[1])
            seg = ''.join(runs[k].text for k in range(i, j + 1))
            if english(seg) == seg:
                break
            runs[i].text = english(seg)
            for k in range(i + 1, j + 1):
                runs[k].text = ''
            n += 1
    doc.save(dst)
    return n


if __name__ == '__main__':
    print(english_docx(sys.argv[1], sys.argv[2]), 'names replaced')
