"""Parse Appendix A of USGS SIR 2004-5067 (Land et al., 2004) from pdftotext -bbox output.

Usage: python -I parse_appA.py appA_bbox.html out.csv
Pages in the bbox file: 1-4 = first well group (construction, field+cations, anions, isotopes),
5-8 = second well group (same order).
Superscript footnote markers (small single digits) are removed and recorded.
"""
import sys, re, csv, math

WORD = re.compile(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)<')
DATE = re.compile(r'^\d{2}/\d{2}/\d{4}$')
CODE = re.compile(r'^\((\d{5})\)$')
SWN = re.compile(r'^\d+S/\d+W-\w+$')

CODE_NAME = {
    '00300': 'DO', '00400': 'pH', '00095': 'SC', '00010': 'T',
    '00915': 'Ca', '00925': 'Mg', '00935': 'K', '00930': 'Na',
    '39036': 'Alk', '71870': 'Br', '00940': 'Cl', '71865': 'I', '00955': 'SiO2', '00945': 'SO4',
    '99118': 'Sulfide', '70301': 'TDS', '01005': 'Ba',
    '01020': 'B', '01080': 'Sr', '62648': 'd11B', '82081': 'd13C', '49933': 'C14', '82082': 'd2H',
    '82085': 'd18O', '75985': 'Sr87', '07000': 'H3',
}


def read_pages(path):
    pages, cur = [], None
    for line in open(path, encoding='utf-8'):
        if '<page' in line:
            cur = []
            pages.append(cur)
            continue
        m = WORD.search(line)
        if m and cur is not None:
            x0, y0, x1, y1 = map(float, m.groups()[:4])
            t = m.group(5).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            cur.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, t=t))
    return pages


def split_footnotes(words):
    """Remove superscript single-digit markers glued to the right of a value; return (words, notes)."""
    keep, notes = [], []
    for w in words:
        h = w['y1'] - w['y0']
        if re.fullmatch(r'[1-7]', w['t']) and h < 6.6:
            notes.append(w)
        else:
            keep.append(w)
    return keep, notes


def value(tok):
    t = tok.replace('−', '-').replace(',', '')
    if t in ('—', '-', ''):
        return None, ''
    cens = ''
    if t.startswith('<'):
        cens, t = '<', t[1:]
    if t.startswith('-.'):
        t = '-0' + t[1:]
    elif t.startswith('.'):
        t = '0' + t
    return float(t), cens


def rows_of(words):
    """Group words into rows anchored on a date word or on the end-member labels."""
    anchors = [w for w in words if DATE.match(w['t'])]
    anchors += [w for w in words if w['t'] in ('Seawater', 'Oil-field') and w['x0'] < 60]
    rows = []
    for a in sorted(anchors, key=lambda w: w['y0']):
        yc = a['y0']
        band = [w for w in words if yc - 3.2 <= w['y0'] <= yc + 4.0]
        rows.append((a, sorted(band, key=lambda w: w['x0'])))
    return rows


def parse_construction(words, out):
    words, notes = split_footnotes(words)
    for a, band in rows_of(words):
        if not DATE.match(a['t']):
            continue
        left = [w for w in band if w['x1'] <= a['x0'] + 0.5 and w is not a]
        right = [w for w in band if w['x0'] > a['x1']]
        swn = [w['t'] for w in left if SWN.match(w['t'])]
        src = [w['t'] for w in left if w['t'] in ('USGS', 'WRDSC', 'LACDPW')]
        name = ' '.join(w['t'] for w in left if not SWN.match(w['t']) and w['t'] not in ('USGS', 'WRDSC', 'LACDPW'))
        vals = [w['t'] for w in right]
        if len(vals) != 5:
            raise SystemExit(f'construction row {name}: {vals}')
        rec = dict(name=name, swn=swn[0] if swn else '', src=src[0] if src else '', date=a['t'])
        for k, v in zip(('depth_casing', 'perf_bottom', 'perf_top', 'wl', 'alt'), vals):
            x, _ = value(v)
            rec[k] = x
        rec['notes'] = ''
        out.append(rec)
    return notes


def parse_coded(words, out, page_tag):
    words, notes = split_footnotes(words)
    cols = [(0.5 * (w['x0'] + w['x1']), CODE_NAME[CODE.match(w['t']).group(1)])
            for w in words if CODE.match(w['t'])]
    cols.sort()
    recs = []
    for a, band in rows_of(words):
        if DATE.match(a['t']):
            left = [w for w in band if w['x1'] <= a['x0'] + 0.5 and w is not a]
            name = ' '.join(w['t'] for w in left)
            right = [w for w in band if w['x0'] > a['x1']]
            date = a['t']
        else:
            lab = [w for w in band if w['x0'] < 160]
            name = ' '.join(w['t'] for w in lab)
            right = [w for w in band if w['x0'] >= 160]
            date = ''
        rec = dict(name=name, date=date)
        used = {}
        for w in right:
            xc = 0.5 * (w['x0'] + w['x1'])
            d, c = min((abs(xc - c0), c) for c0, c in cols)
            if d > 24:
                raise SystemExit(f'{page_tag} {name}: token {w["t"]} far from columns ({d:.1f})')
            if c in used:
                raise SystemExit(f'{page_tag} {name}: two tokens in column {c}: {used[c]} and {w["t"]}')
            used[c] = w['t']
            x, cens = value(w['t'])
            rec[c] = x
            if cens:
                rec[c + '_cens'] = cens
        # footnotes belonging to this row
        fn = [n['t'] for n in notes if a['y0'] - 3.2 <= n['y0'] <= a['y0'] + 4.0]
        if fn:
            # attach to the column of the nearest value on the left
            tags = []
            for n in notes:
                if a['y0'] - 3.2 <= n['y0'] <= a['y0'] + 4.0:
                    xc = n['x0']
                    d, c = min((abs(xc - c0), c) for c0, c in cols)
                    tags.append(f'{c}:{n["t"]}')
            rec['notes'] = ';'.join(tags)
        recs.append(rec)
    out.extend(recs)
    return notes


def main(src, dst):
    pages = read_pages(src)
    assert len(pages) == 8, len(pages)
    cons, chem = [], {}
    for g in (0, 4):
        parse_construction(pages[g], cons)
        for k in (1, 2, 3):
            tmp = []
            parse_coded(pages[g + k], tmp, f'page{g + k + 1}')
            for r in tmp:
                key = (r['name'], r['date'])
                chem.setdefault(key, {}).update({kk: vv for kk, vv in r.items() if kk not in ('name', 'date', 'notes')})
                if r.get('notes'):
                    chem[key]['notes'] = (chem[key].get('notes', '') + ';' + r['notes']).strip(';')
    # merge construction and chemistry
    fields = ['name', 'swn', 'src', 'date', 'depth_casing', 'perf_bottom', 'perf_top', 'wl', 'alt'] + \
             list(CODE_NAME.values())
    fields += [c + '_cens' for c in CODE_NAME.values()] + ['notes']
    rows = []
    seen = set()
    for c in cons:
        key = (c['name'], c['date'])
        r = dict(c)
        r.update(chem.get(key, {}))
        if key not in chem:
            print('no chemistry for', key)
        seen.add(key)
        rows.append(r)
    for key, v in chem.items():
        if key not in seen:
            r = dict(name=key[0], date=key[1])
            r.update(v)
            rows.append(r)
            print('chemistry without construction row:', key)
    with open(dst, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: ('' if r.get(k) is None else r.get(k)) for k in fields})
    print('rows', len(rows))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
