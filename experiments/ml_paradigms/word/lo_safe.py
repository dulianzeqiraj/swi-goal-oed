"""LaTeX rewrites that keep Word rendering and also import cleanly into LibreOffice (see the comment below)."""
import re

# ---------------------------------------------------------------------------------------------
# LibreOffice imports OMML through its own formula language, in which a script that ends in
# "*" or "+", a lone bracket that carries a script (\big]_g), a sized bar (\big|) and a
# half-open interval are syntax errors (drawn as an inverted question mark). Word draws all of
# them. lo_safe() rewrites the LaTeX into equivalent forms that both programs accept.
_SIZE = r'\\(?:big|Big|bigg|Bigg)[lrm]?'
_DELIM = r'(\\\{|\\\}|\\langle|\\rangle|\\lbrack|\\rbrack|[()\[\]])'
_OPEN = {'(', '[', '\\{', '\\langle', '\\lbrack'}
_NORM = {'\\lbrack': '[', '\\rbrack': ']'}


def _match_brace(s, i):
    """index of the '}' matching the '{' at s[i] (backslash-escaped braces are skipped)"""
    depth = 0; k = i
    while k < len(s):
        c = s[k]
        if c == '\\':
            k += 2; continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return k
        k += 1
    return -1


def _script_markers(s):
    out = []; k = 0
    while k < len(s):
        c = s[k]
        if c == '\\':
            m = re.match(r'\\[A-Za-z]+|\\.', s[k:]); out.append(m.group(0)); k += len(m.group(0)); continue
        if c in '^_':
            j = k + 1
            while j < len(s) and s[j] == ' ': j += 1
            if j < len(s) and s[j] == '*':
                out.append(c + '{\\star}'); k = j + 1; continue
            if j < len(s) and s[j] == '+':
                out.append(c + '{\\text{+}}'); k = j + 1; continue
            if j < len(s) and s[j] == '{':
                e = _match_brace(s, j)
                if e > 0:
                    inner = _script_markers(s[j + 1:e]).replace('*', '\\star ')
                    inner = re.sub(r'\+\s*$', r'\\text{+}', inner)
                    inner = re.sub(r'^(\s*)([<>=])', r'\1\\text{\2}', inner)
                    out.append(c + '{' + inner + '}'); k = e + 1; continue
        out.append(c); k += 1
    return ''.join(out)


def _sized_delims(s):
    toks = list(re.finditer(_SIZE + r'\s*' + _DELIM, s))
    stack, pairs = [], []
    for t in toks:
        d = _NORM.get(t.group(1), t.group(1))
        if d in _OPEN or d == '\\lbrack': stack.append((t, d))
        elif stack:
            o, od = stack.pop(); pairs.append((o, od, t, d))
    rep = {}
    for o, od, c, cd in pairs:
        if '[' in (od, cd) or ']' in (od, cd) or {od, cd} not in ({'(', ')'}, {'\\{', '\\}'}, {'\\langle', '\\rangle'}):
            rep[o.start()] = (o.end(), '\\left' + od)
            rep[c.start()] = (c.end(), '\\right' + cd)
    if not rep: return s
    out, k = [], 0
    for st in sorted(rep):
        en, txt = rep[st]; out.append(s[k:st]); out.append(txt + ' '); k = en
    out.append(s[k:])
    return ''.join(out)


def _sized_bars(s):
    bars = list(re.finditer(_SIZE + r'\s*\|', s))
    if not bars: return s
    if len(bars) == 2:
        a, b = bars
        return s[:a.start()] + '\\left|' + s[a.end():b.start()] + '\\right|' + s[b.end():]
    return re.sub(_SIZE + r'\s*\|', lambda m: ' \\mid ' if len(bars) == 1 else '|', s)



def _half_open(s):
    """Half-open intervals with plain brackets become left/right delimiters."""
    def sub(m):
        pre = s[:m.start()]
        if re.search(r'(\\left|\\right|\\(?:big|Big|bigg|Bigg)[lrm]?)\s*$', pre):
            return m.group(0)
        o, body, c = m.group(1), m.group(2), m.group(3)
        return '\\left' + o + body + '\\right' + c + ' '
    return re.sub(r'(\()([^()\[\]]*?)(\])|(\[)([^()\[\]]*?)(\))',
                  lambda m: sub(m) if m.group(1) else _sub2(m, s), s)


def _sub2(m, s):
    pre = s[:m.start()]
    if re.search(r'(\\left|\\right|\\(?:big|Big|bigg|Bigg)[lrm]?)\s*$', pre):
        return m.group(0)
    return '\\left[' + m.group(5) + '\\right) '


def lo_safe(tex):
    s = tex.replace('\\lvert', '|').replace('\\rvert', '|').replace('\\lVert', '\\|').replace('\\rVert', '\\|')
    s = s.replace('\\ast', '\\star')
    s = re.sub(r'\\setminus(?![A-Za-z])', r'\\smallsetminus ', s)
    s = s.replace('\\lbrack', '[').replace('\\rbrack', ']')
    s = _sized_bars(s)
    s = _sized_delims(s)
    # half-open intervals written with plain brackets
    s = _half_open(s)
    s = _script_markers(s)
    return s.strip()


