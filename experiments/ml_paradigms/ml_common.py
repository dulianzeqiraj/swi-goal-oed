"""Shared page framework for the four machine-learning paradigm diagrams (A3 landscape, 2400 x 1697 px).

A page has a header band, a hero (an SVG schematic on the left, with HTML labels and KaTeX equations placed over it, and
an innovation column on the right) and eight numbered cards with equations. Every equation is typeset by KaTeX in one
batch. render.js turns the page into PNG and a vector PDF and checks the layout."""
import base64
import io
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 2400, 1697
BAND = 112
FONT = "Inter,'Liberation Sans',Arial,sans-serif"
INK, MUTED, NAVY = '#1f2328', '#5b6573', '#1F3864'
PAL = dict(blue=('#2a78d6', '#1b5fae', '#eaf2fc'), purple=('#7d4fc9', '#5d35a3', '#f1ecfa'),
           green=('#1baf7a', '#11805a', '#e6f6ef'), teal=('#0f8f9a', '#0b6d75', '#e3f4f5'),
           orange=('#e4572e', '#b9471a', '#fdece7'), amber=('#eda100', '#8f6200', '#fdf3dc'),
           pink=('#c2417a', '#9b2c5e', '#fbeaf1'), brown=('#9c6b30', '#7a5122', '#f6efe6'))
ORDER = ['blue', 'purple', 'green', 'teal', 'orange', 'amber', 'pink', 'brown']      # colours of cards 1..8
GOLD = ('#D97706', '#92400E', '#fff6e3')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class Tex:
    """Collects every equation of a page and typesets them in one KaTeX run."""

    def __init__(self):
        self.items = []

    def eq(self, tex, display=False):
        self.items.append({'tex': tex, 'display': display})
        return f'@@TEX{len(self.items) - 1}@@'

    def text(self, s):
        """Text with $inline math$ and **bold**."""
        parts = s.split('$')
        out = []
        for i, p in enumerate(parts):
            if i % 2:
                out.append(self.eq(p))
            else:
                out.append(re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', esc(p)))
        return ''.join(out)

    def render(self, html):
        html = re.sub(r'(@@TEX\d+@@)([.,;:)]+)', r'<span style="white-space:nowrap">\1\2</span>', html)
        p = subprocess.run(['node', os.path.join(HERE, 'katex_render.js')], input=json.dumps(self.items),
                           capture_output=True, text=True, cwd=HERE)
        if p.returncode:
            raise RuntimeError(p.stderr[-3000:])
        res = json.loads(p.stdout)
        return re.sub(r'@@TEX(\d+)@@', lambda m: res[int(m.group(1))], html)


# ---------------------------------------------------------------- SVG helpers (hero coordinates = page coordinates)
class Svg:
    def __init__(self):
        self.o, self.markers = [], {}

    def add(self, s):
        self.o.append(s)

    def marker(self, color):
        mid = 'm' + color.strip('#')
        if mid not in self.markers:
            self.markers[mid] = (f'<marker id="{mid}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4.2" markerHeight="4.2" '
                                 f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')
        return mid

    def text(self, x, y, s, size=22, weight=600, fill=INK, anchor='start', halo=True, italic=False, ls=0, cls=''):
        h = ' paint-order="stroke" stroke="#ffffff" stroke-width="6" stroke-linejoin="round"' if halo else ''
        it = ';font-style:italic' if italic else ''
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
                 f'letter-spacing="{ls}" style="font-family:{FONT}{it}"{h} data-svg="1" class="{cls}">{esc(s)}</text>')

    def badge(self, x, y, n, color, r=25):
        base = PAL[color][0]
        self.add(f'<g filter="url(#shadow)"><circle cx="{x}" cy="{y}" r="{r}" fill="{base}" stroke="#ffffff" stroke-width="5" data-badge="1"/></g>')
        self.add(f'<text x="{x}" y="{y + 9.5}" font-size="27" font-weight="800" fill="#ffffff" text-anchor="middle" '
                 f'style="font-family:{FONT}" data-svg="1" data-own="1">{n}</text>')

    def panel(self, x, y, w, h, title=None, color='blue', name='', fill='#ffffff', strip=46):
        """A white stage panel with a coloured title strip; labels that touch it must lie inside it."""
        base, deep, tint = PAL[color]
        self.add(f'<g filter="url(#softshadow)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" '
                 f'data-stage="{name or title}"/></g>')
        if title:
            self.add(f'<path d="M{x},{y + 18} a18,18 0 0 1 18,-18 h{w - 36} a18,18 0 0 1 18,18 v{strip - 18} h{-w} z" fill="{base}"/>')
            self.text(x + 20, y + strip / 2 + 8, title, size=21, weight=800, fill='#ffffff', halo=False, ls=1.2)

    def arrow(self, d, color='#5b6573', width=6, dash=None, head=True, opacity=1, start=False):
        m = self.marker(color)
        da = f' stroke-dasharray="{dash}"' if dash else ''
        me = f' marker-end="url(#{m})"' if head else ''
        ms = f' marker-start="url(#{m})"' if start else ''
        self.add(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="none" stroke-linecap="round" '
                 f'stroke-linejoin="round"{da}{me}{ms} opacity="{opacity}"/>')

    def image(self, x, y, w, h, png, rx=10, border='#d0d7de'):
        b64 = base64.b64encode(png).decode()
        cid = f'clip{len(self.o)}'
        self.add(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath>'
                 f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none" clip-path="url(#{cid})" '
                 f'href="data:image/png;base64,{b64}"/>'
                 f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="none" stroke="{border}" stroke-width="2"/>')

    def defs(self):
        return ('<defs>'
                '<filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#1f2328" flood-opacity=".28"/></filter>'
                '<filter id="softshadow" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="3" stdDeviation="6" flood-color="#1f3864" flood-opacity=".14"/></filter>'
                '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
                '<linearGradient id="herobg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eef4fb"/><stop offset="1" stop-color="#f7f9fc"/></linearGradient>'
                '<pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.6" fill="#c9d6e6"/></pattern>'
                + ''.join(self.markers.values()) + '</defs>')

    def svg(self, y1):
        body = '\n'.join(self.o)
        return (f'<svg id="hero" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{y1}" viewBox="0 0 {W} {y1}">'
                f'{self.defs()}<rect x="0" y="{BAND}" width="{W}" height="{y1 - BAND}" fill="url(#herobg)"/>'
                f'<rect x="0" y="{BAND}" width="{W}" height="{y1 - BAND}" fill="url(#dots)" opacity=".55"/>{body}</svg>')


def ov(x, y, html, cls='lab', anchor='tl', w=None, style=''):
    """An HTML label placed over the hero at page coordinates (x, y); anchor t/c/b + l/c/r."""
    tx = {'l': '0', 'c': '-50%', 'r': '-100%'}[anchor[1]]
    ty = {'t': '0', 'c': '-50%', 'b': '-100%'}[anchor[0]]
    ws = f'width:{w}px;' if w else ''
    return f'<div class="ov ovl {cls}" style="left:{x}px;top:{y}px;transform:translate({tx},{ty});{ws}{style}">{html}</div>'


def png_of(fig_fn, w_px, h_px, dpi=100):
    """Render a matplotlib drawing function to PNG bytes of the given pixel size (twice the size for sharpness)."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(2 * w_px / dpi, 2 * h_px / dpi), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    fig_fn(ax)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi)
    plt.close(fig)
    return buf.getvalue()


# ---------------------------------------------------------------- page
CSS = """
html,body{margin:0;padding:0;background:#fff}
#page{position:relative;width:%(W)dpx;height:%(H)dpx;overflow:hidden;font-family:%(F)s;color:%(INK)s;background:#f6f8fb}
#band{position:absolute;left:0;top:0;width:%(W)dpx;height:%(B)dpx;background:linear-gradient(100deg,#13284d 0%%,#1F3864 55%%,#2a4f8a 100%%)}
#band .kick{position:absolute;left:40px;top:16px;font-size:22px;font-weight:800;letter-spacing:3px;color:#f6b73c;white-space:nowrap}
#band .title{position:absolute;left:40px;top:46px;font-size:%(TS)dpx;font-weight:800;color:#ffffff;letter-spacing:.2px;white-space:nowrap}
#band .rows{position:absolute;right:40px;top:18px;display:flex;flex-direction:column;align-items:flex-end;gap:10px}
#band .row{display:flex;align-items:center;gap:12px;font-size:20px;color:#dbe6f5;white-space:nowrap}
#band .tag{font-size:15px;font-weight:800;letter-spacing:1.5px;border-radius:10px;padding:3px 10px;color:#13284d}
#band .t0{background:#c9d3e0} #band .t1{background:#f6b73c}
#hero{position:absolute;left:0;top:0}
.ov{position:absolute;white-space:nowrap}
.lab{font-size:21px;font-weight:600;color:%(INK)s;text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 4px #fff,0 0 5px #fff}
.cap{font-size:18px;font-weight:500;color:%(MUTED)s}
.eqlab{font-size:23px;background:rgba(255,255,255,.94);border:1.5px solid #d0d7de;border-radius:10px;padding:2px 10px;box-shadow:0 1px 4px rgba(31,35,40,.10)}
.eqlab .katex-display{margin:2px 0}
.eqbare{font-size:23px}
.chip{font-size:16px;font-weight:800;letter-spacing:1px;border-radius:12px;padding:3px 10px;color:#fff}
.note{font-size:18.5px;line-height:1.3;color:%(INK)s;white-space:normal}
#cards{position:absolute;left:32px;display:grid;grid-template-columns:repeat(4,1fr);gap:%(CG)dpx 20px;width:%(CW)dpx}
.card{background:#fff;border-radius:16px;box-shadow:0 3px 10px rgba(31,35,40,.12);border-top:8px solid var(--b);padding:12px 20px 10px;display:flex;flex-direction:column;overflow:hidden}
.head{display:flex;align-items:center;gap:12px;margin-bottom:5px}
.num{display:inline-flex;align-items:center;justify-content:center;width:42px;height:42px;border-radius:50%%;background:var(--b);color:#fff;font-weight:800;font-size:24px;flex:none}
.title{font-size:26px;font-weight:800;color:var(--d);line-height:1.12}
.idea{font-size:19px;color:%(INK)s;margin:2px 0 6px;line-height:1.32}
.pill{display:inline-block;font-size:14px;font-weight:800;letter-spacing:1.5px;color:#fff;background:#8a93a0;border-radius:10px;padding:2px 8px;margin-right:8px;vertical-align:2px}
.pk{background:var(--d)}
.eqs{background:var(--t);border-radius:12px;padding:3px 10px;margin:2px 0 8px}
.eq{font-size:22px;overflow:hidden;white-space:nowrap}
.eq .katex-display{margin:5px 0}
.land{font-size:17.5px;line-height:1.33;color:#3a4350}
.land i{color:%(MUTED)s}
.idea .katex,.land .katex{font-size:1.05em}
#innov{position:absolute;background:%(G2)s;border:3px solid %(G0)s;border-radius:20px;box-sizing:border-box;padding:14px 22px 12px;box-shadow:0 4px 14px rgba(146,64,14,.18);display:flex;flex-direction:column;overflow:hidden}
#innov .ih{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
#innov .ik{font-size:22px;font-weight:800;letter-spacing:2px;color:%(G1)s}
#innov .in{font-size:28px;font-weight:800;color:#5a2a06}
#innov .isub{font-size:18.5px;color:#6b4a2a;margin:4px 0 6px;line-height:1.3}
.item{display:flex;gap:14px;margin-top:6px;padding-top:7px;border-top:1.5px dashed #e7c08a}
.item .n{flex:none;width:38px;height:38px;border-radius:50%%;background:%(G0)s;color:#fff;font-weight:800;font-size:21px;display:flex;align-items:center;justify-content:center;margin-top:2px}
.item .b{flex:1;min-width:0}
.item .t{font-size:21.5px;font-weight:800;color:#5a2a06;line-height:1.2}
.item .e{font-size:20px;background:#fffdf8;border:1.5px solid #f0d3a6;border-radius:10px;padding:1px 10px;margin:5px 0;overflow:hidden;white-space:nowrap}
.item .e .katex-display{margin:4px 0}
.item .x{font-size:17px;line-height:1.3;color:#3d2b1a}
.item .x .katex{font-size:1.04em}
.kn{float:right;margin:2px 0 4px 12px;text-align:center;background:#fff;border:2px solid %(G0)s;border-radius:12px;padding:3px 10px;min-width:96px}
.kn .v{font-size:25px;font-weight:800;color:%(G1)s;line-height:1.1}
.kn .c{font-size:13px;font-weight:700;color:#8a5a2a;letter-spacing:.5px;line-height:1.15}
#innov .foot{margin-top:auto;font-size:16.5px;color:#6b4a2a;line-height:1.3;padding-top:6px}
"""


def build_page(tex, *, kicker, title, tags, hero_svg, overlays, hero_y1, innov, innov_box, cards, card_top, card_h,
               card_gap=14, title_size=36):
    """Assemble the page. innov = dict(kicker, name, sub, items=[dict(t, eqs, x, kv, kc)], foot); innov_box = (x, y, w, h).
    cards = [dict(t, color, idea, eqs, land)] (8 of them)."""
    css = CSS % dict(W=W, H=H, F=FONT, INK=INK, MUTED=MUTED, B=BAND, TS=title_size, CG=card_gap, CW=W - 64,
                     G0=GOLD[0], G1=GOLD[1], G2=GOLD[2])
    rows = ''.join(f'<div class="row"><span class="tag t{i}">{esc(a)}</span>{tex.text(b)}</div>' for i, (a, b) in enumerate(tags))
    band = (f'<div id="band"><div class="kick">{esc(kicker)}</div><div class="title">{tex.text(title)}</div>'
            f'<div class="rows">{rows}</div></div>')
    x0, y0, w0, h0 = innov_box
    items = []
    for i, it in enumerate(innov['items']):
        eqs = ''.join(f'<div class="e">{tex.eq(e, True)}</div>' for e in it['eqs'])
        kn = (f'<div class="kn"><div class="v">{tex.text(it["kv"])}</div><div class="c">{esc(it["kc"])}</div></div>'
              if it.get('kv') else '')
        items.append(f'<div class="item"><div class="n">{i + 1}</div><div class="b"><div class="t">{tex.text(it["t"])}</div>'
                     f'{eqs}<div class="x">{kn}{tex.text(it["x"])}</div></div></div>')
    foot = f'<div class="foot">{tex.text(innov["foot"])}</div>' if innov.get('foot') else ''
    innov_html = (f'<div id="innov" style="left:{x0}px;top:{y0}px;width:{w0}px;height:{h0}px">'
                  f'<div class="ih"><span class="ik">{esc(innov["kicker"])}</span><span class="in">{tex.text(innov["name"])}</span></div>'
                  f'<div class="isub">{tex.text(innov["sub"])}</div>{"".join(items)}{foot}</div>')
    cc = []
    for i, c in enumerate(cards):
        base, deep, tint = PAL[c['color']]
        eqs = ''.join(f'<div class="eq">{tex.eq(e, True)}</div>' for e in c['eqs'])
        cc.append(f'<div class="card" style="--b:{base};--d:{deep};--t:{tint}">'
                  f'<div class="head"><span class="num">{i + 1}</span><span class="title">{tex.text(c["t"])}</span></div>'
                  f'<div class="idea"><span class="pill">IDEA</span>{tex.text(c["idea"])}</div>'
                  f'<div class="eqs">{eqs}</div>'
                  f'<div class="land"><span class="pill pk">2020–2026</span>{tex.text(c["land"])}</div></div>')
    cards_html = (f'<div id="cards" style="top:{card_top}px;grid-auto-rows:{card_h}px">{"".join(cc)}</div>')
    katex_css = os.path.join(HERE, 'node_modules', 'katex', 'dist', 'katex.min.css')
    html = (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file://{katex_css}">'
            f'<style>{css}</style></head><body><div id="page" data-hero-y1="{hero_y1}">{hero_svg}{"".join(overlays)}{band}'
            f'{innov_html}{cards_html}</div></body></html>')
    return tex.render(html)
