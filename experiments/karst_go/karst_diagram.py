"""One diagram: what changes when the aquifer is karstic, and how a coastal karst aquifer is modelled.
Canvas 2400 x 1697 (A3 landscape ratio). Illustrated cross-section in SVG; eight panels in HTML with KaTeX equations.
Writes karst_diagram.html; render.js turns it into PNG and a vector PDF and checks overlaps."""
import json
import os
import random
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 2400, 1697
HERO_Y0, HERO_Y1 = 112, 866
CARD_TOP, CARD_H, CARD_GAP = 880, 351, 16
INNOV_TOP, INNOV_H = 1610, 70
INK, MUTED, NAVY = '#1f2328', '#5b6573', '#1F3864'
C = dict(sea=('#2a78d6', '#1b5fae', '#eaf2fc'), top=('#1baf7a', '#11805a', '#e6f6ef'), riv=('#0f8f9a', '#0b6d75', '#e3f4f5'),
         drn=('#7d4fc9', '#5d35a3', '#f1ecfa'), base=('#9c6b30', '#7a5122', '#f6efe6'), well=('#eda100', '#8f6200', '#fdf3dc'),
         ic=('#c2417a', '#9b2c5e', '#fbeaf1'), clo=('#e4572e', '#b9471a', '#fdece7'))
FONT = "Inter,'Liberation Sans',Arial,sans-serif"
random.seed(7)

# ---------------------------------------------------------------- geometry of the cross-section
LAND = ('M640,382 C700,360 760,338 860,318 C960,300 1020,292 1090,290 L1100,290 C1120,290 1130,318 1150,320 '
        'C1170,318 1180,290 1200,288 C1300,284 1380,282 1450,280 C1470,280 1480,312 1500,314 C1520,312 1530,280 1550,278 '
        'C1650,276 1720,274 1770,272 C1790,272 1800,300 1820,302 C1840,300 1850,272 1870,270 C1940,268 1990,268 2030,272 '
        'C2045,290 2060,300 2090,300 L2290,300 C2320,300 2340,280 2360,266 L2400,262')
SEABED_UP = 'M0,768 C40,762 90,752 150,735 C260,700 350,655 430,610 C500,570 560,520 612,470'
SEABED_DOWN = 'C560,520 500,570 430,610 C350,655 260,700 150,735 C90,752 40,762 0,768'
LIMESTONE = SEABED_UP + ' L640,382 ' + LAND[len('M640,382 '):] + ' L2400,852 L0,852 Z'
SEA = 'M0,470 L612,470 ' + SEABED_DOWN + ' Z'
WT = 'M612,470 C900,462 1300,452 1700,445 C2000,440 2200,436 2400,432'
SAT = WT + ' L2400,852 L0,852 L0,768 ' + SEABED_UP[len('M0,768 '):] + ' Z'
WEDGE = 'M430,610 C600,690 860,790 1150,852 L0,852 L0,768 C40,762 90,752 150,735 C260,700 350,655 430,610 Z'

TRUNK = ('M1980,478 C1900,490 1840,476 1820,482 C1700,500 1600,486 1500,492 C1400,500 1300,515 1150,505 '
         'C1000,498 900,520 800,505 C720,494 660,480 612,472')
TRUNK_COAST = 'M800,505 C720,494 660,480 612,472'
SHAFTS = ['M1150,322 C1145,360 1160,400 1150,440 C1145,470 1160,490 1150,505',
          'M1500,316 C1505,350 1490,390 1500,430 C1505,455 1495,480 1500,492',
          'M1820,304 C1815,340 1830,380 1820,420 C1815,445 1825,470 1820,482',
          'M2090,302 C2080,340 2060,380 2040,420 C2020,450 2000,470 1980,478']
DEEP = 'M1000,500 C950,560 880,620 780,660 C700,690 600,690 520,660 C470,640 440,625 425,612'
DEEP_BRACKISH = 'M780,660 C700,690 600,690 520,660 C470,640 440,625 425,612'
LINK = 'M780,660 C745,600 700,540 660,486'
INLET = 'M178,728 C260,736 360,726 450,713 C520,703 560,697 600,689'
OVERFLOW = 'M800,505 C760,470 700,440 632,422'
UNKNOWN = ['M1300,512 C1330,580 1400,640 1500,680 C1600,712 1700,700 1800,650',
           'M1150,505 C1200,600 1250,680 1350,742', 'M1700,700 C1750,745 1810,768 1860,768']


def tube(d, outer='#17487f', inner='#5aa6ee', w=20):
    return (f'<path d="{d}" stroke="{outer}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" stroke="{inner}" stroke-width="{w * 0.42:.1f}" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>')


def txt(x, y, s, size=24, weight=500, fill=INK, anchor='start', halo=True, italic=False, ls=0):
    h = ' paint-order="stroke" stroke="#ffffff" stroke-width="7" stroke-linejoin="round"' if halo else ''
    it = ';font-style:italic' if italic else ''
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'letter-spacing="{ls}" style="font-family:{FONT}{it}"{h} data-svg="1">{s}</text>')


def badge(x, y, n, key, r=27):
    base, deep, tint = C[key]
    return (f'<g filter="url(#shadow)"><circle cx="{x}" cy="{y}" r="{r}" fill="{base}" stroke="#ffffff" stroke-width="5" data-badge="1"/></g>'
            + txt(x, y + 10, n, size=29, weight=800, fill='#ffffff', anchor='middle', halo=False))


def hero():
    o = []
    o.append('''<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfe2f6"/><stop offset=".65" stop-color="#eef5fc"/><stop offset="1" stop-color="#fbfdff"/></linearGradient>
  <linearGradient id="seaG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5c9fdc"/><stop offset=".5" stop-color="#2f6fb5"/><stop offset="1" stop-color="#173f73"/></linearGradient>
  <linearGradient id="lime" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#efe7d6"/><stop offset=".5" stop-color="#e2d6bf"/><stop offset="1" stop-color="#cfbf9f"/></linearGradient>
  <linearGradient id="ridge" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b9c8da"/><stop offset="1" stop-color="#dfe7f0"/></linearGradient>
  <linearGradient id="plume" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#bfe3ff" stop-opacity=".95"/><stop offset="1" stop-color="#bfe3ff" stop-opacity=".15"/></linearGradient>
  <radialGradient id="sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#fff6c7"/><stop offset="1" stop-color="#fff6c7" stop-opacity="0"/></radialGradient>
  <radialGradient id="brack" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#b79be8" stop-opacity=".85"/><stop offset="1" stop-color="#b79be8" stop-opacity="0"/></radialGradient>
  <pattern id="blocks" width="120" height="70" patternUnits="userSpaceOnUse"><path d="M0,35 H120 M60,0 V35 M30,35 V70 M90,35 V70" stroke="#c7b896" stroke-width="1.6" opacity=".55" fill="none"/></pattern>
  <pattern id="hatch" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="16" stroke="#8d8577" stroke-width="3"/></pattern>
  <clipPath id="limeClip"><path d="''' + LIMESTONE + '''"/></clipPath>
  <clipPath id="seaClip"><path d="''' + SEA + '''"/></clipPath>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#1f2328" flood-opacity=".28"/></filter>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="10"/></filter>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <marker id="ab" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#0b6d75"/></marker>
</defs>''')
    # sky, sun, distant ridges
    o.append(f'<rect x="0" y="{HERO_Y0}" width="{W}" height="{HERO_Y1 - HERO_Y0}" fill="url(#sky)"/>')
    o.append('<circle cx="1000" cy="190" r="120" fill="url(#sun)"/>')
    o.append('<path d="M640,380 L820,250 L960,292 L1130,208 L1320,262 L1500,196 L1690,248 L1880,186 L2080,236 L2250,190 L2400,224 L2400,300 L640,382 Z" fill="url(#ridge)" opacity=".75"/>')
    # sea, the plume of the submarine spring, the brackish fan of the coastal spring
    o.append(f'<path d="{SEA}" fill="url(#seaG)"/>')
    o.append('<g clip-path="url(#seaClip)"><path d="M400,612 C388,560 372,520 352,470 L498,470 C480,520 466,560 452,612 Z" fill="url(#plume)"/>')
    for i in range(14):
        x = 404 + random.uniform(-26, 46); y = random.uniform(482, 600)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{random.uniform(2.5, 5.5):.1f}" fill="#e8f5ff" opacity=".85"/>')
    o.append('<ellipse cx="600" cy="478" rx="44" ry="16" fill="url(#brack)"/>')
    o.append('</g>')
    o.append('<ellipse cx="425" cy="471" rx="70" ry="8" fill="none" stroke="#e8f5ff" stroke-width="3" opacity=".9"/>')
    for x0 in (40, 170):
        o.append(f'<path d="M{x0},466 q14,-9 28,0 t28,0 t28,0" stroke="#d6e9fb" stroke-width="3" fill="none" stroke-linecap="round"/>')
    # limestone with blocks, bedding, fractures; saturated zone; seawater wedge
    o.append(f'<path d="{LIMESTONE}" fill="url(#lime)"/>')
    o.append('<g clip-path="url(#limeClip)">')
    o.append(f'<rect x="0" y="250" width="{W}" height="610" fill="url(#blocks)"/>')
    for y in (540, 610, 680, 750, 820):
        o.append(f'<path d="M0,{y + 18} L{W},{y - 18}" stroke="#bda97f" stroke-width="2.2" stroke-dasharray="26 10" opacity=".7"/>')
    for _ in range(70):
        x = random.uniform(0, W); y = random.uniform(300, 840); L = random.uniform(30, 70); a = random.uniform(-0.5, 0.5)
        o.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + a * L:.0f}" y2="{y + L:.0f}" stroke="#a9966f" stroke-width="2" opacity=".55"/>')
    o.append(f'<path d="{SAT}" fill="#7fb6e8" opacity=".30"/>')
    o.append(f'<path d="{WEDGE}" fill="#e9898a" opacity=".42"/>')
    o.append('<path d="M430,610 C600,690 860,790 1150,852" stroke="#f2b7b6" stroke-width="40" fill="none" opacity=".55" filter="url(#soft)"/>')
    # epikarst: a darker, densely fractured band under the surface
    o.append(f'<path d="{LAND}" stroke="#bfa77c" stroke-width="58" fill="none" opacity=".55"/>')
    for _ in range(140):
        x = random.uniform(650, W)
        ysurf = 262 + (300 - 262) * max(0, (2400 - x) / 2400) if x > 1900 else 280
        o.append(f'<line x1="{x:.0f}" y1="{ysurf + random.uniform(4, 10):.0f}" x2="{x + random.uniform(-6, 6):.0f}" y2="{ysurf + random.uniform(22, 34):.0f}" stroke="#8f7a52" stroke-width="2" opacity=".55"/>')
    o.append('</g>')
    # impervious base
    o.append(f'<rect x="0" y="852" width="{W}" height="{HERO_Y1 - 852}" fill="#b9b2a5"/><rect x="0" y="852" width="{W}" height="{HERO_Y1 - 852}" fill="url(#hatch)" opacity=".5"/>')
    # land surface line with soil
    o.append(f'<path d="{LAND}" stroke="#9c8358" stroke-width="5" fill="none"/>')
    o.append(f'<path d="{LAND}" stroke="#7fae5e" stroke-width="3" fill="none" transform="translate(0,-3)"/>')
    # water table
    o.append(f'<path d="{WT}" stroke="#2f6fb5" stroke-width="3" fill="none" stroke-dasharray="14 9"/>')
    # cave in the vadose zone
    o.append('<path d="M1530,392 C1545,368 1600,364 1622,380 C1640,394 1615,410 1575,410 C1545,410 1520,404 1530,392 Z" fill="#4a3f30" opacity=".78"/>')
    for x in range(1548, 1612, 12):
        o.append(f'<path d="M{x},372 l4,12 l4,-12 z" fill="#e7dcc6" opacity=".9"/>')
    # conduits not yet mapped (dotted)
    for d in UNKNOWN:
        o.append(f'<path d="{d}" stroke="#6b5aa8" stroke-width="7" fill="none" stroke-dasharray="4 14" stroke-linecap="round" opacity=".9"/>')
    # conduits: shafts, trunk, deep branch, link, overflow, seawater inlet
    for d in SHAFTS:
        o.append(tube(d, w=15))
    o.append(tube(TRUNK, w=24))
    o.append(tube(DEEP, w=18))
    o.append(tube(DEEP_BRACKISH, outer='#4b2a86', inner='#a07be0', w=18))
    o.append(tube(LINK, outer='#4b2a86', inner='#a07be0', w=14))
    o.append(tube(TRUNK_COAST, outer='#4b2a86', inner='#a07be0', w=24))
    o.append(f'<path d="{OVERFLOW}" stroke="#17487f" stroke-width="10" fill="none" stroke-dasharray="14 10" stroke-linecap="round"/>')
    o.append(tube(INLET, outer='#8f1d1d', inner='#f08a80', w=16))
    # flow chevrons along the trunk and along the seawater inlet
    for (x, y) in ((1700, 492), (1350, 506), (950, 506)):
        o.append(f'<path d="M{x + 9},{y - 9} L{x - 5},{y} L{x + 9},{y + 9}" stroke="#ffffff" stroke-width="4" fill="none" stroke-linecap="round"/>')
    for (x, y) in ((280, 731), (420, 716)):
        o.append(f'<path d="M{x - 9},{y - 9} L{x + 5},{y} L{x - 9},{y + 9}" stroke="#ffffff" stroke-width="4" fill="none" stroke-linecap="round"/>')
    # tracer: injected at the ponor, recovered at the coastal spring
    o.append(f'<path d="{SHAFTS[3]}" stroke="#18c08a" stroke-width="6" fill="none" stroke-dasharray="1 13" stroke-linecap="round" filter="url(#glow)"/>')
    o.append(f'<path d="{TRUNK}" stroke="#18c08a" stroke-width="6" fill="none" stroke-dasharray="1 13" stroke-linecap="round" filter="url(#glow)" transform="translate(0,-1)"/>')
    # sinking stream on the polje, clouds and rain
    o.append('<path d="M2290,297 C2230,296 2160,298 2100,299" stroke="#3f8fd6" stroke-width="7" fill="none" marker-end="url(#ab)" stroke-linecap="round"/>')
    o.append('<path d="M2108,288 C2098,300 2094,306 2090,318" stroke="#3f8fd6" stroke-width="7" fill="none" stroke-linecap="round"/>')
    for cx, cy in ((1330, 172), (1700, 160), (2200, 175)):
        o.append(f'<g opacity=".95"><ellipse cx="{cx}" cy="{cy}" rx="70" ry="28" fill="#ffffff"/><ellipse cx="{cx + 55}" cy="{cy - 14}" rx="55" ry="32" fill="#ffffff"/>'
                 f'<ellipse cx="{cx - 60}" cy="{cy + 4}" rx="45" ry="22" fill="#ffffff"/></g>')
        for i in range(7):
            x = cx - 70 + i * 24
            o.append(f'<line x1="{x}" y1="{cy + 32 + (i % 2) * 8}" x2="{x - 9}" y2="{cy + 70 + (i % 2) * 8}" stroke="#7fb0e0" stroke-width="3" stroke-linecap="round"/>')
    # exchange arrows between the matrix and the conduit
    o.append('<path d="M1235,560 C1238,545 1240,535 1240,524" stroke="#5d35a3" stroke-width="4" fill="none"/><path d="M1232,532 L1240,520 L1248,532" stroke="#5d35a3" stroke-width="4" fill="none"/>')
    o.append('<path d="M1275,520 C1275,532 1277,542 1280,556" stroke="#5d35a3" stroke-width="4" fill="none"/><path d="M1272,546 L1280,558 L1288,546" stroke="#5d35a3" stroke-width="4" fill="none"/>')
    # ---- labels
    o.append(txt(46, 528, 'SEA', size=30, weight=800, fill='#ffffff', halo=False, ls=3))
    o.append(txt(352, 572, 'submarine', size=22, weight=600, fill='#ffffff', anchor='end', halo=False))
    o.append(txt(352, 598, 'spring', size=22, weight=600, fill='#ffffff', anchor='end', halo=False))
    o.append(txt(600, 428, 'overflow spring', size=21, weight=600, fill='#17487f', anchor='end'))
    o.append(txt(600, 456, 'coastal spring', size=21, weight=700, fill='#4b2a86', anchor='end'))
    o.append(txt(66, 812, 'seawater enters the conduits', size=23, weight=700, fill='#b42318'))
    o.append(txt(470, 836, 'seawater wedge in the matrix', size=22, weight=600, fill='#9b2c2c'))
    o.append(txt(1150, 272, 'doline', size=21, weight=600, fill='#6f5b3a', anchor='middle'))
    o.append(txt(2190, 280, 'polje: the stream sinks', size=21, weight=600, fill='#1b5fae', anchor='middle'))
    o.append(txt(2110, 344, 'ponor', size=21, weight=700, fill='#1b5fae'))
    o.append(txt(2110, 372, 'tracer in', size=21, weight=700, fill='#11805a'))
    o.append(txt(1860, 360, 'vadose shaft', size=21, weight=600, fill='#17487f'))
    o.append(txt(1640, 432, 'cave', size=21, weight=600, fill='#4a3f30'))
    o.append(txt(960, 320, 'epikarst', size=22, weight=700, fill='#7a5122', italic=True))
    o.append(txt(2380, 424, 'water table', size=21, weight=600, fill='#2f6fb5', anchor='end'))
    o.append(txt(1036, 476, 'conduit', size=21, weight=700, fill='#17487f'))
    o.append(txt(2380, 849, 'impervious base', size=19, weight=600, fill='#4b4b4b', anchor='end'))
    o.append(txt(1500, 764, 'conduits not yet mapped', size=21, weight=600, fill='#5d35a3', anchor='middle'))
    for (x, y) in ((1425, 640), (1262, 652), (1770, 802)):
        o.append(txt(x, y, '?', size=34, weight=800, fill='#5d35a3', anchor='middle'))
    o.append(hydrograph(24, 126, 520, 272))
    o.append(legend(1876, 646, 504, 178))
    for (x, y, n, key) in ((1585, 530, '1', 'sea'), (1228, 590, '2', 'drn'), (1500, 247, '3', 'top'), (548, 505, '4', 'riv'),
                           (150, 690, '5', 'clo'), (2262, 358, '6', 'well'), (1560, 640, '7', 'ic'), (712, 405, '8', 'base')):
        o.append(badge(x, y, n, key))
    return '\n'.join(o)


def hydrograph(x0, y0, w, h):
    """Inset: rain, spring discharge (fast peak, two-slope recession) and EC dipping as new water arrives."""
    o = [f'<g filter="url(#shadow)"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="16" fill="#ffffff" opacity=".97"/></g>']
    o.append(txt(x0 + 20, y0 + 34, 'At a karst spring: discharge Q and EC', size=22, weight=800, fill=NAVY, halo=False))
    px0, pw = x0 + 58, w - 58 - 22
    qy0, qh = y0 + 52, 104
    ey0, eh = qy0 + qh + 10, 58
    for (yy, hh) in ((qy0, qh), (ey0, eh)):
        o.append(f'<rect x="{px0}" y="{yy}" width="{pw}" height="{hh}" fill="#f3f6fa"/>')
    o.append(f'<line x1="{px0}" y1="{ey0 + eh}" x2="{px0 + pw}" y2="{ey0 + eh}" stroke="#9aa3ad" stroke-width="2"/>')
    o.append(txt(px0 - 12, qy0 + qh / 2 + 8, 'Q', size=21, weight=800, fill='#1b5fae', anchor='end', halo=False))
    o.append(txt(px0 - 12, ey0 + eh / 2 + 8, 'EC', size=19, weight=800, fill='#c2410c', anchor='end', halo=False))
    for i, hgt in enumerate((10, 24, 34, 16, 6)):                       # rain, hanging from the top
        o.append(f'<rect x="{px0 + (0.13 + 0.02 * i) * pw:.1f}" y="{qy0}" width="{0.016 * pw:.1f}" height="{hgt}" fill="#7fb0e0"/>')
    o.append(txt(px0 + 0.13 * pw - 8, qy0 + 18, 'rain', size=18, weight=600, fill='#3f7fbf', anchor='end', halo=False))
    q, e = [], []
    for i in range(0, 201):
        t = i / 200
        r = 0.0 if t < 0.2 else min(1.0, (t - 0.2) / 0.03)
        qq = 0.1 + 0.85 * r * (0.55 * 2.718 ** (-max(t - 0.2, 0) / 0.05) + 0.45 * 2.718 ** (-max(t - 0.2, 0) / 0.35))
        q.append(f'{px0 + t * pw:.1f},{qy0 + qh - qq * qh:.1f}')
        s = 0.0 if t < 0.24 else min(1.0, (t - 0.24) / 0.04)
        ee = 0.85 - 0.6 * s * 2.718 ** (-max(t - 0.24, 0) / 0.18)
        e.append(f'{px0 + t * pw:.1f},{ey0 + eh - ee * eh:.1f}')
    o.append(f'<polyline points="{" ".join(q)}" fill="none" stroke="#1b5fae" stroke-width="4" stroke-linejoin="round"/>')
    o.append(f'<polyline points="{" ".join(e)}" fill="none" stroke="#eb6834" stroke-width="3.5" stroke-linejoin="round"/>')
    o.append(txt(px0 + 0.25 * pw, qy0 + 22, 'fast peak: conduits', size=19, weight=700, fill='#1b5fae', halo=False))
    o.append(txt(px0 + 0.52 * pw, qy0 + 66, 'slow tail: matrix', size=19, weight=600, fill='#1b5fae', halo=False))
    o.append(txt(px0 + 0.36 * pw, ey0 + eh - 6, 'EC drops: new water', size=19, weight=700, fill='#c2410c', halo=False))
    o.append(txt(px0 + pw, ey0 + eh + 22, 'time', size=18, fill=MUTED, anchor='end', halo=False))
    return '<g data-panel="inset">' + '\n'.join(o) + '</g>'


def legend(x0, y0, w, h):
    """Key to the line and area styles of the section."""
    o = [f'<g filter="url(#shadow)"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="14" fill="#ffffff" opacity=".95"/></g>']
    rows = [y0 + 32 + 38 * i for i in range(4)]
    cols = [x0 + 20, x0 + 264]

    def item(c, r, swatch, label):
        x, y = cols[c], rows[r]
        o.append(swatch(x, y))
        o.append(txt(x + 64, y + 7, label, size=19, weight=600, fill=INK, halo=False))

    item(0, 0, lambda x, y: tube(f'M{x},{y} L{x + 50},{y}', w=14), 'fresh conduit')
    item(0, 1, lambda x, y: tube(f'M{x},{y} L{x + 50},{y}', outer='#4b2a86', inner='#a07be0', w=14), 'brackish conduit')
    item(0, 2, lambda x, y: tube(f'M{x},{y} L{x + 50},{y}', outer='#8f1d1d', inner='#f08a80', w=14), 'seawater inflow')
    item(0, 3, lambda x, y: f'<path d="M{x + 2},{y} L{x + 50},{y}" stroke="#6b5aa8" stroke-width="7" stroke-dasharray="4 14" stroke-linecap="round"/>', 'unmapped conduit')
    item(1, 0, lambda x, y: ''.join(f'<circle cx="{x + 6 + 13 * i}" cy="{y}" r="7" fill="#18c08a" opacity=".3"/><circle cx="{x + 6 + 13 * i}" cy="{y}" r="3.2" fill="#18c08a"/>' for i in range(4)), 'tracer test')
    item(1, 1, lambda x, y: f'<path d="M{x},{y} L{x + 50},{y}" stroke="#2f6fb5" stroke-width="3" stroke-dasharray="14 9"/>', 'water table')
    item(1, 2, lambda x, y: (f'<rect x="{x}" y="{y - 12}" width="50" height="24" rx="4" fill="url(#lime)" stroke="#bda97f"/>'
                             f'<path d="M{x + 14},{y - 10} l-4,20 M{x + 32},{y - 11} l5,21 M{x},{y} h50" stroke="#a9966f" stroke-width="2"/>'), 'fractured matrix')
    item(1, 3, lambda x, y: f'<rect x="{x}" y="{y - 12}" width="50" height="24" rx="4" fill="#efb3b0" stroke="#d98583"/>', 'seawater wedge')
    return '<g data-panel="legend">' + '\n'.join(o) + '</g>'


# ---------------------------------------------------------------- the eight panels
PANELS = [
    ('1', 'sea', 'Flow in the conduits', 'Darcy everywhere: $\\mathbf{q}=-K\\nabla h$',
     [r'Q=\frac{\pi\rho g\,r^{4}}{8\mu}\,\frac{\Delta h}{\ell}\quad(\mathrm{Re}<2000)',
      r'\Delta h=f\,\frac{\ell}{D}\,\frac{v^{2}}{2g},\quad \frac{1}{\sqrt{f}}=-2\log_{10}\!\left(\frac{\epsilon/D}{3.7}+\frac{2.51}{\mathrm{Re}\sqrt{f}}\right)'],
     'Monotone in $\\Delta h$, so updates stay stable; laminar flow near $\\Delta h=0$ keeps the slope finite.'),
    ('2', 'drn', 'Two media that exchange', 'one continuum (plus the clay compartments)',
     [r'S_m\partial_t h_m=\nabla\!\cdot\!\left(K_m\nabla h_m\right)-\alpha_{\mathrm{ex}}\left(h_m-h_c\right)+R_{\mathrm{diff}}',
      r'S_c\partial_t h_c=\nabla\!\cdot\!\left(K_c\nabla h_c\right)+\alpha_{\mathrm{ex}}\left(h_m-h_c\right)+R_{\mathrm{conc}}-Q_s'],
     'Two heads per cell, as for the clay compartments of the porous model; the exchange coefficient $\\alpha_{\\mathrm{ex}}$ is a new unknown.'),
    ('3', 'top', 'Recharge through the epikarst', 'diffuse recharge $R(t)$ over the whole top',
     [r'\frac{dS_e}{dt}=P-ET-\frac{S_e}{\tau_e}',
      r'R_{\mathrm{conc}}=\beta\,\frac{S_e}{\tau_e},\qquad R_{\mathrm{diff}}=(1-\beta)\,\frac{S_e}{\tau_e}'],
     'Water enters at points (dolines, ponors); $\\beta$ and $\\tau_e$ join the boundary unknowns.'),
    ('4', 'riv', 'Springs are the outlets', 'the sea face and drains are the outlets',
     [r'Q_s=C_s\left(h_c-z_s\right)_+',
      r'Q(t)=\sum_i Q_{0,i}\,e^{-\alpha_i t},\qquad \alpha_{\mathrm{fast}}\gg\alpha_{\mathrm{slow}}'],
     'A spring is a one-sided drain, a monotone switch; its recession rates $\\alpha_i$ come from the hydrograph.'),
    ('5', 'clo', 'Seawater in the conduits', 'a wedge in the matrix: interface at depth $h/\\delta$, $\\delta=(\\rho_s-\\rho_f)/\\rho_f$',
     [r'Q_{\mathrm{sea}}=C_i\left(h_f^{\mathrm{sea}}(z_i)-h_c(z_i)\right)_+',
      r'h_f^{\mathrm{sea}}(z)=\eta+\delta\,(\eta-z),\qquad c_{\mathrm{spring}}=\frac{Q_{\mathrm{sea}}}{Q_{\mathrm{sea}}+Q_{\mathrm{fresh}}}'],
     'The spring turns brackish in droughts and surges. A fresh spring is a censored observation: $h_c(z_i)\\ge h_f^{\\mathrm{sea}}(z_i)$.'),
    ('6', 'well', 'Fast and slow transport', 'advection–dispersion, short tails',
     [r'\theta_m\partial_t c_m+\theta_{im}\partial_t c_{im}=-q\,\partial_x c_m+\theta_m D\,\partial_x^{2}c_m',
      r'\theta_{im}\,\partial_t c_{im}=\omega\left(c_m-c_{im}\right)'],
     'Tracer curves have long tails: immobile zones (matrix, pools) store the tracer and release it slowly.'),
    ('7', 'ic', 'The network is an unknown', 'a conductivity field $K(\\mathbf{x})$',
     [r'\mathcal{N}=\left(V,\,E,\,\{D_e,\epsilon_e\}\right),\qquad \mathcal{D}=\{\text{tracer},\,Q_s,\,\text{EC}\}',
      r'p\left(\mathcal{N}\mid\mathcal{D}\right)\propto p\left(\mathcal{D}\mid\mathcal{N}\right)\,p(\mathcal{N})'],
     'An ensemble of stochastic networks from geology, fractures and base level, weighted by tracer tests and spring records.'),
    ('8', 'base', 'Floods: a regime of their own', 'drains and seepage switch on',
     [r'Q_{\max}=\frac{\pi D^{2}}{4}\sqrt{\frac{2gD\,\Delta h}{f\,\ell}}',
      r'Q>Q_{\max}\ \Rightarrow\ \text{overflow springs, estavelles}'],
     'A flood regime with its own dynamics; an alarm flags any flood that no regime explains.'),
]


def katex_render(items):
    p = subprocess.run(['node', os.path.join(HERE, 'katex_render.js')], input=json.dumps(items), capture_output=True, text=True, cwd=HERE, check=True)
    return json.loads(p.stdout)


def inline_math(s):
    """Turn $...$ in a short text into KaTeX inline HTML."""
    parts = s.split('$')
    texs = [{'tex': parts[i], 'display': False} for i in range(1, len(parts), 2)]
    html = katex_render(texs) if texs else []
    out, k = [], 0
    for i, part in enumerate(parts):
        if i % 2:
            out.append(html[k]); k += 1
        else:
            out.append(part.replace('&', '&amp;'))
    return ''.join(out)


def panels_html():
    eqs = [{'tex': t, 'display': True} for p in PANELS for t in p[4]]
    rendered = katex_render(eqs)
    k = 0
    cards = []
    for (n, key, title, porous, tex, impact) in PANELS:
        base, deep, tint = C[key]
        eq_html = ''.join(f'<div class="eq">{rendered[k + i]}</div>' for i in range(len(tex)))
        k += len(tex)
        cards.append(f'''<div class="card" style="--b:{base};--d:{deep};--t:{tint}">
  <div class="head"><span class="num">{n}</span><span class="title">{title}</span></div>
  <div class="porous"><span class="pill">POROUS</span>{inline_math(porous)}</div>
  <div class="eqs">{eq_html}</div>
  <div class="impact"><span class="pill pk">IN THE MODEL</span>{inline_math(impact)}</div>
</div>''')
    return '\n'.join(cards)


def build():
    katex_css = os.path.join(HERE, 'node_modules', 'katex', 'dist', 'katex.min.css')
    innovation = inline_math('The conduit network itself is assimilated: stochastic networks from geology, fractures and base level are weighted by tracer tests, the spring hydrograph and its EC. Every pipe law, exchange and outlet is monotone in the head, so each update stays stable (30 random karst networks: at most 0.33 of the bound). The EC of a coastal spring observes the conduit head at the sea inlet.')
    html = f'''<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="file://{katex_css}">
<style>
html,body{{margin:0;padding:0;background:#fff}}
#page{{position:relative;width:{W}px;height:{H}px;overflow:hidden;font-family:{FONT};color:{INK};background:#f6f8fb}}
#band{{position:absolute;left:0;top:0;width:{W}px;height:{HERO_Y0}px;background:linear-gradient(100deg,#13284d 0%,#1F3864 55%,#2a4f8a 100%)}}
#band .kick{{position:absolute;left:40px;top:16px;font-size:22px;font-weight:800;letter-spacing:3px;color:#f6b73c}}
#band .title{{position:absolute;left:40px;top:46px;font-size:38px;font-weight:800;color:#ffffff;letter-spacing:.2px;white-space:nowrap}}
#band .rows{{position:absolute;right:40px;top:18px;display:flex;flex-direction:column;align-items:flex-end;gap:10px}}
#band .row{{display:flex;align-items:center;gap:12px;font-size:20px;color:#dbe6f5;white-space:nowrap}}
#band .tag{{font-size:15px;font-weight:800;letter-spacing:1.5px;border-radius:10px;padding:3px 10px;color:#13284d}}
#band .tp{{background:#c9d3e0}} #band .tk{{background:#f6b73c}}
#hero{{position:absolute;left:0;top:0}}
#cards{{position:absolute;left:32px;top:{CARD_TOP}px;width:{W - 64}px;display:grid;grid-template-columns:repeat(4,1fr);grid-auto-rows:{CARD_H}px;gap:{CARD_GAP}px 20px}}
.card{{background:#fff;border-radius:16px;box-shadow:0 3px 10px rgba(31,35,40,.12);border-top:8px solid var(--b);padding:12px 20px 10px;display:flex;flex-direction:column;overflow:hidden}}
.head{{display:flex;align-items:center;gap:12px;margin-bottom:5px}}
.num{{display:inline-flex;align-items:center;justify-content:center;width:42px;height:42px;border-radius:50%;background:var(--b);color:#fff;font-weight:800;font-size:24px;flex:none}}
.title{{font-size:27px;font-weight:800;color:var(--d)}}
.porous{{font-size:19px;color:{MUTED};margin:2px 0 6px;line-height:1.3}}
.pill{{display:inline-block;font-size:14px;font-weight:800;letter-spacing:1.5px;color:#fff;background:#8a93a0;border-radius:10px;padding:2px 8px;margin-right:8px;vertical-align:2px}}
.pk{{background:var(--d)}}
.eqs{{background:var(--t);border-radius:12px;padding:3px 10px;margin:2px 0 8px}}
.eq{{font-size:23px;overflow:hidden;white-space:nowrap}}
.eq .katex-display{{margin:5px 0}}
.impact{{font-size:19.5px;line-height:1.33;color:{INK}}}
.impact .katex,.porous .katex{{font-size:1.05em}}
#innov{{position:absolute;left:32px;top:{INNOV_TOP}px;width:{W - 64}px;height:{INNOV_H}px;border-radius:14px;background:#fff5e1;border-left:12px solid #D97706;box-sizing:border-box;padding:8px 24px;font-size:20px;line-height:1.38;color:{INK};display:flex;align-items:center;box-shadow:0 3px 10px rgba(31,35,40,.10)}}
#innov b{{color:#92400E;letter-spacing:1px;margin-right:18px;white-space:nowrap;font-size:21px}}
</style></head><body><div id="page">
<svg id="hero" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HERO_Y1}" viewBox="0 0 {W} {HERO_Y1}">{hero()}</svg>
<div id="band"><div class="kick">KARST AQUIFERS  ·  WHAT CHANGES IN THE MODEL</div>
<div class="title">From a porous aquifer to a karst aquifer: how a coastal karst massif is modelled</div>
<div class="rows"><div class="row"><span class="tag tp">POROUS</span>one continuum · Darcy flow · diffuse recharge · a sea face</div>
<div class="row"><span class="tag tk">KARST</span>matrix + conduits · pipe flow · point recharge · springs and sea inlets</div></div></div>
<div id="cards">{panels_html()}</div>
<div id="innov"><b>INNOVATION · KARST-GO</b><span>{innovation}</span></div>
</div></body></html>'''
    open(os.path.join(HERE, 'karst_diagram.html'), 'w').write(html)
    print('wrote karst_diagram.html')


if __name__ == '__main__':
    build()
