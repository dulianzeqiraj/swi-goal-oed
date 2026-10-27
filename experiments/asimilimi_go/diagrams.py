"""Diagrams of the assimilation note: (D1) every boundary and initial condition of the Fushe-Kuqe system, the data that
update it, the update and its behaviour in extreme events; (D2) the update cycle in normal and extreme conditions.
Writes res/diagram_bc.html and res/diagram_cycle.html; render_diagrams.js turns them into PNG (about 360 dpi at 17 cm).
1 unit = 0.1 mm at 17 cm width; the smallest text is 28 units = 8 pt."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
INK, MUTED, NAVY = '#1f2328', '#5b6573', '#1F3864'
F = "font-family:Inter,'Liberation Sans',Arial,sans-serif"
try:
    DETECT = int(json.load(open(os.path.join(RES, 'extreme.json')))['E8_E11']['heads + gauge + spikes / IMM + spike model']['drought_E_detect']['median'] + 0.5)
except Exception:
    DETECT = 'N'
C = dict(sea=('#2a78d6', '#1b5fae', '#eaf2fc'), top=('#1baf7a', '#11805a', '#e6f6ef'), riv=('#0f8f9a', '#0b6d75', '#e3f4f5'),
         drn=('#7d4fc9', '#5d35a3', '#f1ecfa'), land=('#6b7280', '#4b5563', '#f1f2f4'), base=('#9c6b30', '#7a5122', '#f6efe6'),
         well=('#eda100', '#8f6200', '#fdf3dc'), ic=('#c2417a', '#9b2c5e', '#fbeaf1'), clo=('#e4572e', '#b9471a', '#fdece7'))


class S:
    def __init__(self, W, H):
        self.W, self.H, self.o = W, H, []

    def add(self, s):
        self.o.append(s)

    def text(self, x, y, s, size=29, weight=400, fill=INK, anchor='start', ls=0, italic=False):
        st = ';font-style:italic' if italic else ''
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" letter-spacing="{ls}" style="{F}{st}">{s}</text>')

    def badge(self, cx, cy, lab, key, r=24):
        base, deep, tint = C[key]
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#ffffff" stroke="{deep}" stroke-width="5" filter="url(#soft)"/>')
        self.text(cx, cy + 10, lab, size=27 if len(lab) > 1 else 30, weight=700, fill=deep, anchor='middle')

    def svg(self):
        defs = '''<defs>
  <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bcd8ef"/><stop offset="1" stop-color="#8fb8e0"/></linearGradient>
  <linearGradient id="salt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7d9fcb"/><stop offset="1" stop-color="#5677a8"/></linearGradient>
  <linearGradient id="fresh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9f3fc"/><stop offset="1" stop-color="#d6e8f7"/></linearGradient>
  <linearGradient id="vadose" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f7f0e1"/><stop offset="1" stop-color="#efe4cc"/></linearGradient>
  <pattern id="sand" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="5" cy="6" r="1.7" fill="#b7a27a" opacity=".35"/><circle cx="16" cy="15" r="1.4" fill="#b7a27a" opacity=".3"/></pattern>
  <pattern id="hatch" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="14" stroke="#9aa1ab" stroke-width="3"/></pattern>
  <filter id="blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="9"/></filter>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#1f2328" flood-opacity=".18"/></filter>
  <filter id="card" x="-5%" y="-10%" width="110%" height="125%"><feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#1f2328" flood-opacity=".10"/></filter>
  <marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#5b6573"/></marker>
  <marker id="ahn" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#1F3864"/></marker>
  <marker id="ahr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#b9471a"/></marker>
  <marker id="ahg" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#11805a"/></marker>
</defs>'''
        body = '\n'.join(self.o)
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.W} {self.H}" width="{self.W}" height="{self.H}">{defs}<rect width="{self.W}" height="{self.H}" fill="#ffffff"/>{body}</svg>'


NARROW = set("il.,;:|()[]!'ftjr ₊")
WIDE = set('mwMWΨΦ—')


def width(t, size=28, weight=400):
    """Estimated width of rich text in units (Inter); subscripts at 0.72 em."""
    w, sub, i = 0.0, False, 0
    while i < len(t):
        if t.startswith('_{', i):
            sub = True; i += 2; continue
        if sub and t[i] == '}':
            sub = False; i += 1; continue
        ch = t[i]
        em = 0.29 if ch in NARROW else 0.86 if ch in WIDE else 0.66 if ch.isupper() or ch in 'ΓΔ→≈' else 0.6 if ch.isdigit() else 0.555
        w += em * size * (0.72 if sub else 1.0) * (1.04 if weight >= 600 else 1.0) * 1.06
        i += 1
    return w


def wrap(t, maxw, size=28):
    words, lines, cur = t.split(' '), [], ''
    for wd in words:
        trial = (cur + ' ' + wd).strip()
        if width(trial, size) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur); cur = wd
    lines.append(cur)
    return lines


def rich(s, x, y, t, size=28, weight=400, fill=INK, box=None, italic=False, anchor='start'):
    """Text with subscripts written as _{...}."""
    out, i, buf = [], 0, ''
    while i < len(t):
        if t.startswith('_{', i):
            j = t.index('}', i)
            if buf:
                out.append(buf); buf = ''
            out.append(f'<tspan font-size="{0.72 * size:.0f}" dy="7">{t[i + 2:j]}</tspan><tspan dy="-7"> </tspan>')
            i = j + 1
            continue
        buf += t[i]; i += 1
    if buf:
        out.append(buf)
    body = ''.join(out).replace('<tspan dy="-7"> </tspan>', '<tspan dy="-7">\u200a</tspan>')
    st = ';font-style:italic' if italic else ''
    db = f' data-box="{box[0]},{box[1]}"' if box else ''
    s.add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" style="{F}{st}"{db}>{body}</text>')


def write(name, s):
    os.makedirs(RES, exist_ok=True)
    svg = s.svg()
    open(os.path.join(RES, name + '.svg'), 'w').write(svg)
    open(os.path.join(RES, name + '.html'), 'w').write(
        '<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:#fff}svg{display:block}</style></head>'
        f'<body>{svg}</body></html>')


# ===================================================================== D1: the boundary and initial conditions
def diagram_bc():
    W, H = 1700, 1560
    s = S(W, H)
    BASE = 430
    land = 'M300,186 C520,180 800,170 1060,160 C1300,152 1500,146 1700,140'
    wt = 'M300,190 C600,188 900,186 990,184 C1030,183 1045,178 1060,178 C1075,178 1090,183 1130,184 C1300,185 1360,184 1390,188 C1420,200 1440,236 1460,238 C1480,236 1500,200 1530,188 C1600,182 1660,180 1700,180'
    inter = 'C420,250 600,360 790,430'
    s.add(f'<rect x="0" y="{BASE}" width="{W}" height="34" fill="#c9ced5"/><rect x="0" y="{BASE}" width="{W}" height="34" fill="url(#hatch)" opacity=".55"/>')
    s.add(f'<path d="{land} L1700,180 C1660,180 1600,182 1530,188 C1500,200 1480,236 1460,238 C1440,236 1420,200 1390,188 C1360,184 1300,185 1130,184 C1090,183 1075,178 1060,178 C1045,178 1030,183 990,184 C900,186 600,188 300,190 Z" fill="url(#vadose)"/>')
    s.add(f'<path d="{wt} L1700,{BASE} L790,{BASE} C600,360 420,250 300,190 Z" fill="url(#fresh)"/>')
    s.add(f'<path d="{wt} L1700,{BASE} L790,{BASE} C600,360 420,250 300,190 Z" fill="url(#sand)"/>')
    s.add(f'<path d="M0,280 L300,188 {inter} L0,{BASE} Z" fill="url(#salt)"/>')
    s.add(f'<clipPath id="aq"><path d="M0,280 L300,188 L300,190 {wt[9:]} L1700,{BASE} L0,{BASE} Z"/></clipPath>')
    s.add(f'<g clip-path="url(#aq)"><path d="M300,190 {inter}" stroke="#a8c3e3" stroke-width="44" fill="none" filter="url(#blur)"/></g>')
    s.add('<ellipse cx="900" cy="350" rx="130" ry="14" fill="#b9a27c" stroke="#9c845d" stroke-width="2"/>')
    s.add('<path d="M0,186 L300,186 L300,188 L0,280 Z" fill="url(#sea)"/>')
    for x0 in (40, 150):
        s.add(f'<path d="M{x0},180 q12,-8 24,0 t24,0 t24,0" stroke="#5f8fc4" stroke-width="3" fill="none" stroke-linecap="round"/>')
    # storm surge: a raised dashed sea level
    s.add('<path d="M0,150 L300,150" stroke="#1b5fae" stroke-width="3" stroke-dasharray="10 7"/>')
    s.text(20, 140, 'storm surge', size=28, fill=C['sea'][1], weight=600)
    s.add(f'<path d="{land}" stroke="#a88f63" stroke-width="7" fill="none"/>')
    s.add(f'<path d="{land}" stroke="#86b46f" stroke-width="3" fill="none" transform="translate(0,-4)"/>')
    s.add(f'<path d="{wt}" stroke="#3f7cc0" stroke-width="2.5" fill="none" stroke-dasharray="9 7"/>')
    s.text(50, 395, 'sea water', size=29, weight=600, fill='#ffffff')
    s.text(1690, 412, 'fresh groundwater', size=28, fill='#3f5f80', anchor='end')
    s.text(900, 392, 'clay (legacy)', size=28, fill='#6f5b3a', anchor='middle')
    # river (a channel cut into the surface at x = 640) and a coastal drain / lagoon at x = 420
    s.add('<path d="M600,174 Q640,206 680,172" fill="#7fb6e0" stroke="#0b6d75" stroke-width="3"/>')
    s.add('<path d="M380,183 L392,192 L448,191 L460,181 Z" fill="#9ec4e6" stroke="#5d35a3" stroke-width="2.5"/>')
    # recharge basin and rain
    s.add('<path d="M990,163 L1006,176 L1114,173 L1130,158 Z" fill="#9ec4e6" stroke="#5f8fc4" stroke-width="2"/>')
    for x in (1028, 1060, 1092):
        s.add(f'<path d="M{x},181 L{x},212" stroke="{C["top"][0]}" stroke-width="4.5" marker-end="url(#ahg)" stroke-linecap="round"/>')
    s.add('<g opacity=".9"><ellipse cx="1240" cy="68" rx="46" ry="26" fill="#e3e8ef"/><ellipse cx="1285" cy="58" rx="40" ry="30" fill="#e3e8ef"/>'
          '<ellipse cx="1322" cy="72" rx="34" ry="22" fill="#e3e8ef"/><rect x="1208" y="68" width="146" height="26" rx="13" fill="#e3e8ef"/></g>')
    for i, x in enumerate((1226, 1256, 1286, 1316, 1342)):
        s.add(f'<line x1="{x}" y1="{104 + (i % 2) * 6}" x2="{x - 7}" y2="{128 + (i % 2) * 6}" stroke="#8fb8e0" stroke-width="3" stroke-linecap="round"/>')
    # wells: supply well and a monitoring well
    d = C['well'][1]
    s.add(f'<line x1="1460" y1="150" x2="1460" y2="320" stroke="{d}" stroke-width="6" stroke-linecap="round"/>')
    s.add(f'<rect x="1442" y="124" width="36" height="24" rx="5" fill="{C["well"][0]}" stroke="{d}" stroke-width="3"/>')
    s.add('<line x1="760" y1="170" x2="760" y2="420" stroke="#8a8f98" stroke-width="4"/><rect x="751" y="156" width="18" height="14" rx="3" fill="#8a8f98"/>')
    for yy in (330, 400):
        s.add(f'<circle cx="760" cy="{yy}" r="6.5" fill="#ffffff" stroke="#8a8f98" stroke-width="3"/>')
    # inland margin and base arrows
    s.add(f'<line x1="1694" y1="182" x2="1694" y2="{BASE}" stroke="{C["land"][1]}" stroke-width="6" stroke-dasharray="4 8"/>')
    for x in (1150, 1300):
        s.add(f'<path d="M{x},{BASE + 30} L{x},{BASE + 4}" stroke="{C["base"][1]}" stroke-width="4" marker-end="url(#ah)"/>')
    # closure: a dashed box in the interior
    s.add(f'<rect x="1180" y="262" width="150" height="56" rx="10" fill="none" stroke="{C["clo"][1]}" stroke-width="3" stroke-dasharray="8 6"/>')
    s.text(1255, 298, 'Ψ, Φ ?', size=29, weight=700, fill=C['clo'][1], anchor='middle')
    # badges on the boundaries
    for lab, key, x, y in (('1', 'sea', 160, 230), ('2', 'top', 1060, 108), ('3', 'riv', 640, 132), ('4', 'drn', 420, 132),
                           ('5', 'land', 1650, 300), ('6', 'base', 1225, 500), ('7', 'well', 1520, 120), ('IC', 'ic', 560, 300), ('C', 'clo', 1385, 290)):
        s.badge(x, y, lab, key)
    s.text(26, 44, 'THE BOUNDARY AND INITIAL CONDITIONS OF THE SYSTEM, AND HOW EACH IS UPDATED', size=28, weight=600, fill=MUTED, ls=2.2)

    # ---------------------------------------------------------------- the matrix: one row per boundary
    rows = [
        ('1', 'sea', 'Sea face Γ_{sea}', 'head or Robin', 'sea level η_{0}, trend, anomaly η_{ia}(t); sea-bed g, sea Cl_{s}',
         'tide gauge (vital in surges), coastal heads, EC', 'η_{ia} as a state: filter; g, Cl_{s}: ensemble Kalman inversion',
         'surge: its own 2-day state opens (T8); needs the tide gauge (E10)'),
        ('2', 'top', 'Top Γ_{top}', 'flux (Neumann)', 'recharge R = R̄ + δR + ρ(t); law L(s)',
         'rain, soil moisture, Cl mass balance', 'ρ as a state: filter; graph completion for L(s)',
         'drought or flood: regime frees ρ (T8); saturated soil → seepage switch (L2)'),
        ('3', 'riv', 'Rivers Γ_{riv}', 'Robin, switching', 'stage h_{r}(t), conductance C_{r}',
         'river gauge, nearby heads', 'h_{r} as a state: filter; C_{r} by inversion',
         'dry bed: C_{r}(h_{r} − max(h, z_{b})) disconnects; stays Lipschitz (L2)'),
        ('4', 'drn', 'Drains, lagoon', 'one-sided Robin', 'drain level z_{d}, conductance C_{d}',
         'drain flow, lagoon level', 'filter on the level, inversion for C_{d}',
         'flood: C_{d}(h − z_{d})₊ switches on; ES-MDA over the active set (L2)'),
        ('5', 'land', 'Inland margin Γ_{in}', 'flux ≈ 0', 'lateral inflow q_{in}',
         'inland heads', 'smoother (slow and small)', 'unchanged; watched by the alarm (T9)'),
        ('6', 'base', 'Base Γ_{base}', 'leaky, with memory', 'leakage κ, base head h_{base}, memory kernel',
         'deep piezometers', 'smoother; memory lifted into extra states', 'slow: the extra states keep the trace of past events'),
        ('7', 'well', 'Wells', 'internal sink', 'metered Q_{w}(t), unlicensed E',
         'meters, heads near the wells', 'E as a state: filter; closure check (T5)',
         'drought: E jumps → drought regime frees E (T8); found in about DETECT days'),
        ('IC', 'ic', 'Initial conditions', 'fields at t_{0}', 'h_{0}, c_{0}, clay legacy h_{k,0}, exchanger β_{0}',
         'earliest heads, chloride, ions', 'smoother over the early data (T3); probit (T7); constraints (P6)',
         'a past extreme sits in the clay legacy; only slow modes remember it'),
        ('C', 'clo', 'Missing dynamics', 'closure term', 'Ψ(h; γ), Φ(c; ϑ)', 'all data together',
         'joint update with the boundaries; principal angles (T5)', 'coverage drop in a regime = missing dynamics'),
    ]
    head = ['Boundary and type', 'What is unknown', 'Data that inform it', 'Normal update', 'In an extreme event']
    cw = [352, 318, 284, 340, 374]
    X0 = 16
    cx = [X0]
    for w_ in cw:
        cx.append(cx[-1] + w_)
    Y0, HH, PAD, LH = 556, 58, 16, 38
    # header
    s.add(f'<rect x="{X0}" y="{Y0}" width="{cx[-1] - X0}" height="{HH}" rx="12" fill="{NAVY}"/>')
    s.add(f'<rect x="{cx[4]}" y="{Y0}" width="{cw[4]}" height="{HH}" rx="12" fill="{C["clo"][1]}"/><rect x="{cx[4]}" y="{Y0}" width="20" height="{HH}" fill="{C["clo"][1]}"/>')
    for j, hd in enumerate(head):
        s.text(cx[j] + PAD, Y0 + 38, hd, size=28, weight=700, fill='#ffffff')
    y = Y0 + HH + 8
    for lab, key, name, typ, unk, dat, upd, ext in rows:
        ext = ext.replace('DETECT', str(DETECT))
        cells = [wrap(unk, cw[1] - 2 * PAD), wrap(dat, cw[2] - 2 * PAD), wrap(upd, cw[3] - 2 * PAD), wrap(ext, cw[4] - 2 * PAD)]
        nl = max(2, max(len(c) for c in cells))
        rh = 20 + LH * nl
        base, deep, tint = C[key]
        dash = ' stroke-dasharray="10 6"' if key == 'clo' else ''
        s.add(f'<rect x="{X0}" y="{y}" width="{cx[-1] - X0}" height="{rh}" rx="12" fill="#ffffff" stroke="#d5dae1" stroke-width="2"{dash}/>')
        s.add(f'<rect x="{X0}" y="{y}" width="{cw[0]}" height="{rh}" rx="12" fill="{tint}"/><rect x="{cx[1] - 14}" y="{y}" width="14" height="{rh}" fill="{tint}"/>')
        s.add(f'<rect x="{cx[4]}" y="{y + 1}" width="{cw[4] - 1}" height="{rh - 2}" rx="11" fill="#fdf3ef"/><rect x="{cx[4]}" y="{y + 1}" width="14" height="{rh - 2}" fill="#fdf3ef"/>')
        s.add(f'<rect x="{X0}" y="{y}" width="8" height="{rh}" rx="4" fill="{base}"/>')
        s.badge(X0 + 46, y + rh / 2, lab, key, r=22)
        ty = y + rh / 2 - LH / 2 + 10
        rich(s, X0 + 82, ty, name, size=28, weight=700, fill=INK, box=(cx[0], cx[1]))
        rich(s, X0 + 82, ty + LH, typ, size=28, weight=400, fill=deep, box=(cx[0], cx[1]), italic=True)
        for j, lines in enumerate(cells):
            col = j + 1
            y1 = y + 10 + (rh - 20 - LH * len(lines)) / 2 + 26
            for k, ln in enumerate(lines):
                rich(s, cx[col] + PAD, y1 + LH * k, ln, size=28, fill=C['clo'][1] if col == 4 else INK, box=(cx[col], cx[col + 1]))
        y += rh + 8
    # the spike-or-event rule under the matrix
    y += 6
    s.add(f'<rect x="{X0}" y="{y}" width="{cx[-1] - X0}" height="104" rx="14" fill="#eef2f8" stroke="{NAVY}" stroke-width="2"/>')
    s.add(f'<rect x="{X0}" y="{y}" width="300" height="104" rx="14" fill="{NAVY}"/><rect x="{X0 + 280}" y="{y}" width="20" height="104" fill="{NAVY}"/>')
    s.text(X0 + 150, y + 46, 'Spike or event?', size=30, weight=700, fill='#ffffff', anchor='middle')
    s.text(X0 + 150, y + 82, 'for every sensor', size=28, fill='#dfe6f2', anchor='middle')
    rich(s, X0 + 326, y + 44, 'A jump at one sensor on one day may be either: the update keeps both (spike model, P10).',
         size=28, weight=600, fill=NAVY, box=(X0 + 300, cx[-1]))
    rich(s, X0 + 326, y + 82, 'The next reading, or a second sensor, decides; a lasting jump moves the regime weights (T8).',
         size=28, weight=400, fill=NAVY, box=(X0 + 300, cx[-1]))
    y += 104 - 64
    s.H = int(y + 64 + 16)
    write('diagram_bc', s)
    return s


# ===================================================================== D2: the update cycle
def diagram_cycle():
    W, H = 1700, 1060
    s = S(W, H)
    s.text(26, 44, 'ONE ASSIMILATION STEP, NORMAL AND EXTREME', size=28, weight=600, fill=MUTED, ls=2.2)

    def box(x, y, w, h, title, lines, key='sea', fill=None, dash=False, tsize=30):
        base, deep, tint = C[key]
        dd = ' stroke-dasharray="10 6"' if dash else ''
        s.add(f'<g filter="url(#card)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill or tint}" stroke="{base}" stroke-width="2.5"{dd}/></g>')
        s.text(x + 20, y + 42, title, size=tsize, weight=700, fill=deep)
        for k, ln in enumerate(lines):
            rich(s, x + 20, y + 82 + 38 * k, ln, size=28, fill=INK, box=(x, x + w))

    def arrow(d, col='#5b6573', mk='ah'):
        s.add(f'<path d="{d}" stroke="{col}" stroke-width="3.5" fill="none" marker-end="url(#{mk})"/>')

    # row 1
    y1, h1 = 92, 212
    box(16, y1, 520, h1, '1  Forecast, one per regime', ['Xᶠ_{r} = Ψ₀(X) + m(X; θ) + ξ_{r}', 'each regime carries the', 'event\'s own dynamics'], key='sea')
    box(590, y1, 520, h1, '2  Data arrive', ['heads, tide gauge, meters,', 'rain and soil moisture,', 'chloride and EC samples'], key='top')
    box(1164, y1, 520, h1, '3  Spike or event?', ['each reading may be a spike:', 'exact mixture of no spike and', 'spike at sensor i (P10)'], key='land')
    arrow(f'M536,{y1 + h1 / 2} L584,{y1 + h1 / 2}'); arrow(f'M1110,{y1 + h1 / 2} L1158,{y1 + h1 / 2}')
    # bus to the three regime lanes
    yb = y1 + h1 + 28
    s.add(f'<path d="M1424,{y1 + h1} L1424,{yb} L276,{yb}" stroke="#5b6573" stroke-width="3.5" fill="none"/>')
    for xx in (276, 850, 1424):
        arrow(f'M{xx},{yb} L{xx},{yb + 26}')
    # row 2: the regime lanes
    y2, h2 = yb + 32, 300
    lanes = [(16, 'Normal regime', 'top', ['boundaries as states: filter,', 'exact for heads (T1);', 'constants by inversion;', 'initial state by smoother (T3)']),
             (590, 'Surge regime', 'sea', ['the surge state opens and', 'decays in 2 days; the gauge', 'sees it at once, the heads', 'a day later (E10)']),
             (1164, 'Drought or flood regime', 'well', ['recharge and E free; river,', 'drain and seepage switch:', 'ES-MDA, and the update', 'stays stable (Lemma 2)'])]
    for (x, t, key, lines), wl in zip(lanes, ('normal', 'surge', 'drought')):
        box(x, y2, 520, h2, t, lines, key=key, fill='#ffffff')
        base, deep, tint = C[key]
        s.add(f'<rect x="{x + 1.5}" y="{y2 + 1.5}" width="517" height="10" rx="5" fill="{base}"/>')
        s.add(f'<rect x="{x + 20}" y="{y2 + h2 - 62}" width="250" height="44" rx="22" fill="{tint}" stroke="{base}" stroke-width="2"/>')
        rich(s, x + 145, y2 + h2 - 31, f'weight w_{{{wl}}}', size=28, weight=600, fill=deep, anchor='middle', box=(x + 20, x + 270))
    # row 3: merge
    y3, h3 = y2 + h2 + 40, 112
    for xx in (276, 850, 1424):
        arrow(f'M{xx},{y2 + h2} L{xx},{y3 - 6}')
    s.add(f'<g filter="url(#card)"><rect x="16" y="{y3}" width="1668" height="{h3}" rx="16" fill="#eef2f8" stroke="{NAVY}" stroke-width="2.5"/></g>')
    s.text(36, y3 + 44, '4  Merge the regimes (Theorem 8)', size=30, weight=700, fill=NAVY)
    rich(s, 36, y3 + 86, 'weight w_{r} ∝ prior of the regime × likelihood of the data; the posterior is the mixture, kept by its mean and covariance',
         size=28, fill=INK, box=(16, 1684))
    # row 4
    y4, h4 = y3 + h3 + 52, 212
    bw, gap = 394, 30
    xs = [16 + i * (bw + gap) for i in range(4)]
    arrow(f'M{xs[0] + bw / 2},{y3 + h3} L{xs[0] + bw / 2},{y4 - 6}')
    box(xs[0], y4, bw, h4, '5  Alarm (T9)', ['NIS > χ²(m, 0.999)', 'under every regime =', 'missing dynamics'], key='clo')
    box(xs[1], y4, bw, h4, '6  Chloride (T7)', ['probit of the sea', 'fraction; a saturated', 'sample is censored'], key='ic')
    box(xs[2], y4, bw, h4, '7  Constraints (P6)', ['linear ones kept:', 'charge, exchanger;', 'bounds by transform'], key='drn')
    box(xs[3], y4, bw, h4, '8  Calibration (T5)', ['90% coverage by', 'regime; a drop points', 'to a missing closure'], key='base')
    for i in range(3):
        arrow(f'M{xs[i] + bw},{y4 + h4 / 2} L{xs[i + 1] - 6},{y4 + h4 / 2}')
    # loop back
    s.add(f'<path d="M1684,{y4 + h4 / 2} L1694,{y4 + h4 / 2} L1694,72 L276,72 L276,{y1 - 6}" stroke="{NAVY}" stroke-width="3.5" fill="none" stroke-dasharray="10 8" marker-end="url(#ahn)"/>')
    s.text(1680, 60, 'next step: a wrong start is forgotten (T4)', size=28, weight=600, fill=NAVY, anchor='end')
    s.H = int(y4 + h4 + 24)
    write('diagram_cycle', s)
    return s


if __name__ == '__main__':
    diagram_bc()
    diagram_cycle()
    print('wrote res/diagram_bc.html and res/diagram_cycle.html')
