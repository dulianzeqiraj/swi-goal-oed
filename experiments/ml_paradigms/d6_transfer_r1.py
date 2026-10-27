"""Transfer, route R1: a model that can travel from the studied aquifer S to a new coastal aquifer T.

One dimensionless operator is learnt once on simulations of the family of coastal aquifers; at every new aquifer the
transfer is certified, the certificate enters the filter as model error, and an alarm watches the transfer.
Pictures: (a) the seven boundary classes on S and on T (schematic); (b) the descriptor space and the certificate
(illustration, no data); (c) the coverage of a 90% interval when the forecast is biased by at most B_T, plain and
widened by B_T (computed: coverage(r) = Phi(1.645 sqrt(1 + r^2) - r) - Phi(-1.645 sqrt(1 + r^2) - r), r = B_T / sigma);
(d) a simulated NIS alarm (chi-square, m = 4 readings, alpha = 1%); (e) the damping exp(-x / x_s) of a boundary event
with the skin distance x_s = sqrt(2 T tau / S) of the test aquifer of the assimilation note (T = 1000 m2/d, S = 0.1,
tau = 2 days: x_s = 200 m)."""
import numpy as np
from scipy.stats import chi2, ncx2, norm

from ml_common import PAL, ORDER, INK, MUTED, Svg, Tex, ov, build_page

HERO_Y1 = 842
RED = '#c0392b'
BC = dict(sea='#2a78d6', top='#1baf7a', riv='#0f8f9a', drn='#7d4fc9', inflow='#e4572e', base='#9c6b30', well='#eda100')


# ---------------------------------------------------------------- computations
def coverage():
    r = np.linspace(0, 3, 601)
    s = 1.645 * np.sqrt(1 + r ** 2)
    wide = norm.cdf(s - r) - norm.cdf(-s - r)
    plain = norm.cdf(1.645 - r) - norm.cdf(-1.645 - r)
    rf = np.linspace(0, 3, 300001)
    sf = 1.645 * np.sqrt(1 + rf ** 2)
    wf = norm.cdf(sf - rf) - norm.cdf(-sf - rf)
    i = int(np.argmin(wf))
    return r, wide, plain, float(wf[i]), float(rf[i])


def nis_series(m=4, alpha=0.01, n=160, brk=100, lam=14.0):
    thr = chi2.ppf(1 - alpha, m)
    for seed in range(200):                          # an illustration: the first seed with no alarm before the break
        rng = np.random.default_rng(seed)
        x = np.concatenate([chi2.rvs(m, size=brk, random_state=rng), ncx2.rvs(m, lam, size=n - brk, random_state=rng)])
        if (x[:brk] <= thr).all() and (x[brk:] > thr).any():
            return x, thr, brk, int(brk + np.argmax(x[brk:] > thr)), seed
    raise RuntimeError('no seed')


def x_skin(T=1000.0, S=0.1, tau=2.0):
    return np.sqrt(2 * T * tau / S)


# ---------------------------------------------------------------- the schematic
def section(g, O, tex, x0, x1, ytop, ybot, sea_w, labels):
    """A coastal cross-section with its seven boundary classes drawn in their colours."""
    ysl = ytop + 40
    xc = x0 + sea_w
    land = lambda x: ysl - (ysl - ytop) * (x - xc) / (x1 - xc)
    xt = xc + 0.34 * (x1 - xc)
    # aquifer, wedge, sea, base
    g.add(f'<polygon points="{x0},{ysl + 46} {xc},{ysl} {x1},{ytop} {x1},{ybot} {x0},{ybot}" fill="#f1e5c8"/>')
    g.add(f'<path d="M{xc},{ysl} C{xc + 30},{ysl + 50} {xt - 40},{ybot - 20} {xt},{ybot} L{x0},{ybot} L{x0},{ysl + 46} Z" fill="#f6c4bd" opacity=".9"/>')
    g.add(f'<polygon points="{x0},{ysl} {xc},{ysl} {x0},{ysl + 46}" fill="#7fb2df"/>')
    g.add(f'<rect x="{x0}" y="{ybot}" width="{x1 - x0}" height="14" fill="#d8c3a2"/>')
    g.add(f'<path d="M{xc},{ysl} L{x1},{ytop + 14}" stroke="#1b5fae" stroke-width="2" stroke-dasharray="7 5"/>')
    g.add(f'<path d="M{xc},{ysl} L{x1},{ytop}" stroke="#7a5a2a" stroke-width="2.5" fill="none"/>')
    # 1 sea face
    g.add(f'<path d="M{x0},{ysl + 46} L{xc},{ysl}" stroke="{BC["sea"]}" stroke-width="6" stroke-linecap="round"/>')
    # 2 recharge on top
    for f in (0.62, 0.74, 0.86):
        x = xc + f * (x1 - xc)
        g.arrow(f'M{x},{land(x) - 24} V{land(x) - 4}', BC['top'], 3.5)
    # 3 river, 4 drain
    xr = xc + 0.30 * (x1 - xc)
    g.add(f'<path d="M{xr - 13},{land(xr - 13) + 1} Q{xr},{land(xr) + 12} {xr + 13},{land(xr + 13) + 1}" stroke="{BC["riv"]}" stroke-width="6" fill="none" stroke-linecap="round"/>')
    xd = xc + 0.47 * (x1 - xc)
    g.add(f'<path d="M{xd - 16},{land(xd) + 14} H{xd + 16}" stroke="{BC["drn"]}" stroke-width="5" stroke-dasharray="5 3"/>')
    # 5 inland inflow, 6 base with aquitards, 7 well
    ym = (ytop + ybot) / 2 + 14
    g.arrow(f'M{x1 + 2},{ym} H{x1 - 34}', BC['inflow'], 4.5)
    g.add(f'<path d="M{x0},{ybot} H{x1}" stroke="{BC["base"]}" stroke-width="5"/>')
    xw = xc + 0.60 * (x1 - xc)
    g.add(f'<path d="M{xw},{land(xw) - 10} V{ym - 4}" stroke="{BC["well"]}" stroke-width="5"/>'
          f'<rect x="{xw - 4}" y="{ym - 24}" width="8" height="20" fill="#ffffff" stroke="{BC["well"]}" stroke-width="2.5"/>')
    if labels:
        st = 'font-size:14.5px;font-weight:700;'
        O.append(ov(x0 + 6, ysl - 6, tex.text('sea'), 'lab', 'bl', style=st + f'color:{BC["sea"]}'))
        O.append(ov(xr, land(xr) + 14, tex.text('river'), 'lab', 'tc', style=st + f'color:{BC["riv"]}'))
        O.append(ov(xd, land(xd) + 22, tex.text('drain'), 'lab', 'tc', style=st + f'color:{BC["drn"]}'))
        O.append(ov(xc + 0.74 * (x1 - xc), land(xc + 0.74 * (x1 - xc)) - 28, tex.text('recharge'), 'lab', 'bc', style=st + 'color:#11805a'))
        O.append(ov(xw + 10, ym + 6, tex.text('well'), 'lab', 'tl', style=st + 'color:#8f6200'))
        O.append(ov(x1 - 40, ym - 6, tex.text('inflow'), 'lab', 'br', style=st + f'color:{BC["inflow"]}'))
        O.append(ov((x0 + x1) / 2 + 40, ybot + 7, tex.text('base, aquitards'), 'lab', 'cc', style=st + 'color:#7a5122'))
        O.append(ov(x0 + 40, ybot - 22, tex.text('wedge'), 'lab', 'bl', style='font-size:13.5px;font-style:italic;color:#9b2c2c'))


def hero(tex, cov, nis):
    g = Svg()
    O = []
    blue, purple, green, teal, orange, amber, pink, brown = (PAL[c] for c in ORDER)

    # ======== A: the family, S -> T
    g.panel(32, 136, 968, 334, 'MAP THE BOUNDARIES OF T ONTO THE CLASSES OF S', 'blue', name='A')
    section(g, O, tex, 56, 436, 206, 352, 90, False)
    section(g, O, tex, 566, 966, 198, 366, 112, True)
    O.append(ov(246, 382, tex.text('studied aquifer **S**'), 'lab', 'tc', style='font-size:16px'))
    O.append(ov(766, 390, tex.text('new aquifer **T**: other metres and days'), 'lab', 'tc', style='font-size:16px'))
    g.arrow('M448,292 H548', '#1F3864', 6)
    O.append(ov(498, 280, tex.text('same seven<br>classes').replace('&lt;br&gt;', '<br>'), 'lab', 'bc',
                style='font-size:13.5px;font-weight:700;color:#1F3864;text-align:center;line-height:1.15'))
    O.append(ov(600, 412, tex.eq(r'\mathbf{x}^{*}=\frac{\mathbf{x}}{d},\qquad t^{*}=\frac{q_b\,t}{\phi\,d},\qquad h^{*}=\frac{K_G\,h}{q_b\,d}'),
                'eqlab', 'tc', style='font-size:20px'))
    O.append(ov(330, 440, tex.text('one family in dimensionless units'), 'cap', 'cr', style='font-size:14.5px'))

    # ======== B: certify the transfer (illustration)
    g.panel(1018, 136, 538, 334, 'CERTIFY T  ·  ILLUSTRATION', 'orange', name='B')
    rng = np.random.default_rng(3)
    pts = np.column_stack([1150 + 42 * rng.standard_normal(46), 312 + 38 * rng.standard_normal(46)])
    pts = pts[(pts[:, 0] > 1052) & (pts[:, 0] < 1290) & (pts[:, 1] > 214) & (pts[:, 1] < 412)]
    g.add('<rect x="1040" y="200" width="262" height="222" rx="10" fill="#fbfcfe" stroke="#d0d7de" stroke-width="1.5"/>')
    for x, y in pts:
        g.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="#8a93a0"/>')
    cands = [((1176, 334), 15, 'T'), ((1266, 232), 30, 'T′')]
    Bs = []
    for (cx, cy), u, nm in cands:
        dd = np.hypot(pts[:, 0] - cx, pts[:, 1] - cy)
        j = int(np.argmin(dd))
        g.add(f'<circle cx="{cx}" cy="{cy}" r="{u}" fill="{orange[2]}" fill-opacity=".7" stroke="{orange[0]}" stroke-width="2" stroke-dasharray="5 4"/>')
        g.add(f'<line x1="{cx}" y1="{cy}" x2="{pts[j, 0]:.1f}" y2="{pts[j, 1]:.1f}" stroke="{orange[1]}" stroke-width="2.5"/>')
        g.add(f'<circle cx="{cx}" cy="{cy}" r="6.5" fill="{orange[1]}" stroke="#ffffff" stroke-width="2"/>')
        Bs.append((0.15, 2.0 * dd[j] / 100, 1.0 * u / 100))
    O.append(ov(1184, 342, tex.eq(r'\hat{\mathbf{z}}_T'), 'eqbare', 'tl', style='font-size:17px'))
    O.append(ov(1256, 262, tex.eq(r'\hat{\mathbf{z}}_{T^{\prime}}'), 'eqbare', 'tr', style='font-size:17px'))
    O.append(ov(1171, 428, tex.text('descriptor space: training aquifers $\\mathbf{z}_i$'), 'cap', 'tc', style='font-size:14px'))
    # certificate bars
    YB0, sc = 418, 112
    eps_star = 0.8
    seg_c = ('#8a93a0', blue[0], purple[0])
    for k, (x, parts) in enumerate(zip((1360, 1470), Bs)):
        y = YB0
        for v, c in zip(parts, seg_c):
            g.add(f'<rect x="{x - 22}" y="{y - v * sc:.1f}" width="44" height="{v * sc:.1f}" fill="{c}"/>')
            y -= v * sc
    ye = YB0 - eps_star * sc
    g.add(f'<line x1="1326" y1="{ye:.1f}" x2="1508" y2="{ye:.1f}" stroke="{RED}" stroke-width="2.6" stroke-dasharray="8 5"/>')
    O.append(ov(1512, ye, tex.eq(r'\varepsilon_{\star}'), 'eqbare', 'cl', style=f'font-size:17px;color:{RED}'))
    g.add(f'<line x1="1326" y1="{YB0}" x2="1530" y2="{YB0}" stroke="#5b6573" stroke-width="2"/>')
    O.append(ov(1360, 426, tex.text('**T**: transfer'), 'lab', 'tc', style='font-size:14px;color:#11805a'))
    O.append(ov(1470, 426, tex.text('**T′**: simulate'), 'lab', 'tc', style=f'font-size:14px;color:{RED}'))
    O.append(ov(1470, 444, tex.text('or measure'), 'lab', 'tc', style=f'font-size:14px;color:{RED}'))
    for i, (c, t) in enumerate(zip(seg_c, (r'\varepsilon_{\mathrm{tr}}', r'(L^{\dagger}+L_w)\,d_T', r'L^{\dagger}u_T'))):
        y = 198 + 22 * i
        g.add(f'<rect x="1328" y="{y - 7}" width="16" height="14" rx="3" fill="{c}"/>')
        O.append(ov(1350, y, tex.eq(t), 'eqbare', 'cl', style='font-size:15px'))
    O.append(ov(1440, 268, tex.eq(r'B_T'), 'eqbare', 'cc', style='font-size:17px'))

    # ======== C: the certificate as model error (computed)
    g.panel(32, 488, 508, 338, 'THE CERTIFICATE AS MODEL ERROR', 'amber', name='C')
    r, wide, plain, cmin, rmin = cov
    X0, X1, Y0, Y1 = 92, 512, 586, 742
    px = lambda v: X0 + v / 3 * (X1 - X0)
    py = lambda c: Y1 - c * (Y1 - Y0)
    for c in (0.5, 1.0):
        g.add(f'<line x1="{X0}" y1="{py(c):.1f}" x2="{X1}" y2="{py(c):.1f}" stroke="#e3e8ee" stroke-width="1.5"/>')
    g.add(f'<line x1="{X0}" y1="{py(0.9):.1f}" x2="{X1}" y2="{py(0.9):.1f}" stroke="#1f3864" stroke-width="1.8" stroke-dasharray="5 4"/>')
    g.add(f'<path d="M{X0},{Y0 - 6} V{Y1} H{X1 + 4}" stroke="#5b6573" stroke-width="2" fill="none"/>')
    pl = ' '.join('%.1f,%.1f' % (px(a), py(b)) for a, b in zip(r, plain))
    wl = ' '.join('%.1f,%.1f' % (px(a), py(b)) for a, b in zip(r, wide))
    g.add(f'<polyline points="{pl}" fill="none" stroke="{RED}" stroke-width="3.6" stroke-dasharray="9 6"/>')
    g.add(f'<polyline points="{wl}" fill="none" stroke="{green[1]}" stroke-width="4.2"/>')
    g.add(f'<circle cx="{px(rmin):.1f}" cy="{py(cmin):.1f}" r="6" fill="#ffffff" stroke="{green[1]}" stroke-width="3"/>')
    for c, s in ((0.5, '0.5'), (0.9, '0.9'), (1.0, '1')):
        g.text(X0 - 8, py(c) + 5, s, size=13.5, weight=600, fill=MUTED, anchor='end', halo=False)
    for v in (0, 1, 2, 3):
        g.text(px(v), Y1 + 19, str(v), size=13.5, weight=600, fill=MUTED, anchor='middle', halo=False)
    O.append(ov(X1, Y1 + 24, tex.text('bias / noise, $r=B_T/\\sigma$'), 'cap', 'tr', style='font-size:14px'))
    O.append(ov(X0 + 6, Y0 - 4, tex.text('coverage of a 90% interval'), 'cap', 'tl', style='font-size:14px'))
    O.append(ov(px(1.7), py(0.9) + 8, tex.text('widened: $C^f+B_T^2I$'), 'lab', 'tc', style=f'font-size:15px;font-weight:700;color:{green[1]}'))
    O.append(ov(px(2.2), py(0.30), tex.text('plain interval'), 'lab', 'cl', style=f'font-size:15px;font-weight:700;color:{RED}'))
    O.append(ov(286, 790, tex.text('computed: widened never below %.5f ($r\\approx%.2f$)' % (cmin, rmin)), 'cap', 'tc', style='font-size:14px'))

    # ======== D: watch the transfer (simulated)
    g.panel(558, 488, 488, 338, 'WATCH THE TRANSFER', 'pink', name='D')
    x, thr, brk, alarm, seed = nis
    X0, X1, Y0, Y1 = 604, 1024, 570, 742
    top = 40.0
    qx = lambda t: X0 + t / len(x) * (X1 - X0)
    qy = lambda v: Y1 - min(v, top) / top * (Y1 - Y0)
    g.add(f'<rect x="{qx(brk):.1f}" y="{Y0}" width="{X1 - qx(brk):.1f}" height="{Y1 - Y0}" fill="{pink[2]}"/>')
    g.add(f'<path d="M{X0},{Y0 - 6} V{Y1} H{X1 + 4}" stroke="#5b6573" stroke-width="2" fill="none"/>')
    bars = ''.join(f'<line x1="{qx(t + 0.5):.1f}" y1="{Y1}" x2="{qx(t + 0.5):.1f}" y2="{qy(v):.1f}" stroke="{pink[0] if v > thr else "#8a93a0"}" stroke-width="2"/>'
                   for t, v in enumerate(x))
    g.add(bars)
    g.add(f'<line x1="{X0}" y1="{qy(thr):.1f}" x2="{X1}" y2="{qy(thr):.1f}" stroke="{RED}" stroke-width="2.6" stroke-dasharray="8 5"/>')
    O.append(ov(X0 + 6, qy(thr) - 4, tex.eq(r'\chi^{2}_{m,1-\alpha}'), 'eqbare', 'bl', style=f'font-size:16px;color:{RED}'))
    g.add(f'<circle cx="{qx(alarm + 0.5):.1f}" cy="{qy(x[alarm]):.1f}" r="8" fill="{RED}" stroke="#ffffff" stroke-width="2.5"/>')
    O.append(ov(qx(brk) + 6, Y0 + 4, tex.text('transfer broken'), 'lab', 'tl', style=f'font-size:14px;font-weight:700;color:{pink[1]}'))
    O.append(ov(X1, Y1 + 8, tex.text('time step'), 'cap', 'tr', style='font-size:14px'))
    O.append(ov(X0 + 6, Y0 - 4, tex.eq(r'\mathrm{NIS}_n=\boldsymbol{\nu}_n^{\top}S_n^{-1}\boldsymbol{\nu}_n'), 'eqbare', 'bl', style='font-size:16px'))
    O.append(ov(802, 768, tex.text('before the break: false alarms at rate $\\alpha$ in any aquifer'), 'cap', 'tc', style='font-size:14px'))
    O.append(ov(802, 790, tex.text('simulated: $m=4$ readings, $\\alpha=1\\%$; coverage target 0.90'), 'cap', 'tc', style='font-size:14px'))

    # ======== E: three numbers first
    g.panel(1064, 488, 492, 338, 'THREE NUMBERS FIRST', 'brown', name='E')
    xs = x_skin()
    X0, X1, Y0, Y1 = 1104, 1346, 580, 700
    xx = np.linspace(0, 600, 241)
    ex = lambda v: X0 + v / 600 * (X1 - X0)
    ey = lambda a: Y1 - a * (Y1 - Y0)
    g.add(f'<path d="M{X0},{Y0 - 6} V{Y1} H{X1 + 4}" stroke="#5b6573" stroke-width="2" fill="none"/>')
    g.add(f'<polyline points="{" ".join("%.1f,%.1f" % (ex(a), ey(np.exp(-a / xs))) for a in xx)}" fill="none" stroke="{brown[0]}" stroke-width="4"/>')
    g.add(f'<line x1="{ex(xs):.1f}" y1="{Y0}" x2="{ex(xs):.1f}" y2="{Y1}" stroke="{brown[1]}" stroke-width="2" stroke-dasharray="5 4"/>')
    g.add(f'<line x1="{ex(250):.1f}" y1="{Y0}" x2="{ex(250):.1f}" y2="{Y1}" stroke="{blue[0]}" stroke-width="2.5"/>')
    O.append(ov(ex(xs) - 4, Y0 - 2, tex.text('$x_s=%d$ m' % round(xs)), 'lab', 'br', style=f'font-size:14px;font-weight:700;color:{brown[1]}'))
    O.append(ov(ex(250) + 4, Y0 - 2, tex.text('first piezometer, 250 m'), 'lab', 'bl', style=f'font-size:14px;font-weight:700;color:{blue[1]}'))
    O.append(ov(ex(250) + 8, Y0 + 30, tex.text('surge amplitude, $e^{-x/x_s}$'), 'cap', 'tl', style='font-size:13.5px'))
    O.append(ov(X1, Y1 + 6, tex.text('distance from the sea, m'), 'cap', 'tr', style='font-size:13.5px'))
    O.append(ov(1452, 612, tex.text('**37%**'), 'lab', 'cc', style=f'font-size:34px;color:{RED}'))
    O.append(ov(1452, 646, tex.text('of surges seen'), 'cap', 'cc', style='font-size:14px;color:#3a4350'))
    O.append(ov(1452, 664, tex.text('by heads alone;'), 'cap', 'cc', style='font-size:14px;color:#3a4350'))
    O.append(ov(1452, 682, tex.text('all with a tide gauge'), 'cap', 'cc', style='font-size:14px;color:#3a4350'))
    O.append(ov(1080, 738, tex.text('$\\omega_1=\\pi^2T/(4SL^2)$: the slowest rate sets the record length'), 'note', 'tl', style='font-size:15px'))
    O.append(ov(1080, 764, tex.text('$B_T\\le\\varepsilon_{\\star}$: can the operator be used at all?'), 'note', 'tl', style='font-size:15px'))
    O.append(ov(1310, 792, tex.text('test aquifer: transmissivity 1000 m²/d, storativity 0.1, a 2-day surge'), 'cap', 'tc', style='font-size:13.5px'))

    # flows between the panels
    g.arrow('M1002,300 H1014', '#5b6573', 6)
    g.arrow('M1300,472 V484', '#5b6573', 6)
    g.arrow('M542,656 H554', '#5b6573', 6)
    # badges -> cards
    for (xb, yb, n) in ((976, 159, 1), (908, 440, 2), (1062, 222, 3), (1112, 398, 4), (1532, 159, 5), (516, 511, 6),
                        (1022, 511, 7), (1532, 511, 8)):
        g.badge(xb, yb, n, ORDER[n - 1])
    return g.svg(HERO_Y1), O


# ---------------------------------------------------------------- content
def innov(cov):
    r, wide, plain, cmin, rmin = cov
    return dict(
        kicker='INNOVATION', name='The certificate becomes model error',
        sub='Not a yes or a no: the certificate enters the filter of the new aquifer, narrows with every datum and is '
            'watched.',
        items=[
            dict(t='A certificate the filter can use',
                 eqs=[r'C^{f}\ \leftarrow\ C^{f}+B_T^{2}I,\qquad B_T=\varepsilon_{\mathrm{tr}}+(L^{\dagger}+L_w)\,d_T+L^{\dagger}u_T'],
                 x='For a Gaussian forecast with bias within $B_T$, the widened 90%% interval covers the truth with '
                   'probability at least 89.99%% for every bias-to-noise ratio (minimum %.5f at $r\\approx%.2f$).' % (cmin, rmin),
                 kv='≥ 89.99%', kc='COVERAGE, ANY BIAS'),
            dict(t='The descriptor is a state',
                 eqs=[r'\mathbf{X}_T=\big(\mathbf{v},\,\mathbf{b},\,\boldsymbol{\gamma},\,\hat{\mathbf{z}}_T\big)\ \Rightarrow\ u_T\downarrow\ \Rightarrow\ B_T\downarrow'],
                 x='Every datum of T updates $\\hat{\\mathbf{z}}_T$ with the rest of the state, so the certificate narrows '
                   'as the record grows.',
                 kv='$B_T$ ↓', kc='WITH EVERY DATUM'),
            dict(t='Three numbers before using the model',
                 eqs=[r'x_s=\sqrt{2T\tau/S},\qquad \omega_1=\pi^{2}T/(4SL^{2}),\qquad B_T\le\varepsilon_{\star}'],
                 x='In the test aquifer of the assimilation note (transmissivity 1000 m²/d, storativity 0.1, a 2-day surge) $x_s=200$ m, short of '
                   'the first piezometer at 250 m: heads alone recognised only 37% of the surges, a tide gauge all of them.',
                 kv='37%', kc='SURGES SEEN BY HEADS'),
        ],
        foot='R1 stops at a boundary of T with no class, and near a change of regime (small $a$).')


CARDS = [
    dict(t='Map the boundaries of T', color='blue',
         idea='Every boundary of the new aquifer must fall into one of the seven classes: sea, recharge, rivers, drains, '
              'inland inflow, base with aquitards, wells.',
         eqs=[r'\partial\Omega_T=\Gamma_{\mathrm{sea}}\cup\Gamma_{\mathrm{top}}\cup\Gamma_{\mathrm{riv}}\cup\Gamma_{\mathrm{drn}}\cup\Gamma_{\mathrm{in}}\cup\Gamma_{\mathrm{base}}\cup\Gamma_{w}',
              r'h_f=\frac{\rho_s}{\rho_f}\,\eta(t)-\frac{\rho_s-\rho_f}{\rho_f}\,z\quad\text{on}\ \Gamma_{\mathrm{sea}}'],
         pill='CHECK AT T',
         land='A boundary with no class (a karst conduit, a tidal river, a sealing fault) means the family does not cover T: '
              'add that class to the simulations first. Rivers and drains are monotone switches, such as $q_d=-C_d(h-z_d)_+$, '
              'stable in any aquifer.'),
    dict(t='Make the problem dimensionless', color='purple',
         idea='Scale by thickness $d$, inflow from land $q_b$ and conductivity $K_G$: aquifers in other metres and days '
              'become one family.',
         eqs=[r'\mathbf{x}^{*}=\frac{\mathbf{x}}{d},\qquad t^{*}=\frac{q_b\,t}{\phi\,d},\qquad h^{*}=\frac{K_G\,h}{q_b\,d}',
              r'a=\frac{q_b\rho_0}{K_G\Delta\rho},\qquad b=\frac{D_m\phi}{q_b d},\qquad s=\frac{S_s q_b d}{\phi K_G}'],
         pill='IN PRACTICE',
         land='Groups of Abarca, Carrera, Sánchez-Vila & Dentz (2007, Advances in Water Resources), with $r_K=K_z/K_x$ and '
              '$\\xi=L/d$; $s$: storage number, for tides, surges and pumping.'),
    dict(t='One point per aquifer', color='green',
         idea='An aquifer becomes one point: its dimensionless groups and its log-conductivity in Karhunen–Loève '
              'coordinates.',
         eqs=[r'\mathbf{z}=\big(\boldsymbol{\theta},\,Y^{*}\big),\qquad Y^{*}=\ln\frac{K_x}{K_G}=\sum_k\zeta_k\,\psi_k(\mathbf{x}^{*})',
              r'\boldsymbol{\theta}=\big(a,\,b,\,r_K,\,\xi,\,\alpha_L/d,\,\alpha_T/d,\,\sigma_Y^{2},\,\lambda/d,\,s\big)'],
         pill='IN PRACTICE',
         land='The operator maps a descriptor to the salinity field, $\\mathcal{G}^{\\dagger}:\\mathbf{z}\\mapsto c(\\mathbf{x}^{*},t^{*})$. '
              'Aquifers that differ in metres and days can share $\\boldsymbol{\\theta}$; with the same geometry and '
              'boundary classes the transfer is then exact.'),
    dict(t='Learn the operator once', color='teal',
         idea='Train one neural operator on simulations; keep its training error and local Lipschitz constants.',
         eqs=[r'\varepsilon_{\mathrm{tr}}=\max_i\big\|\mathcal{G}^{\dagger}(\mathbf{z}_i)-\mathcal{G}_w(\mathbf{z}_i)\big\|,\qquad N\approx C\,d_{\mathrm{eff}}^{\,1+4\alpha}\log\frac{1}{\delta}',
              r'L^{\dagger}\approx\max_{i,j\ \text{near}\ \mathbf{z}}\frac{\|\mathcal{G}^{\dagger}(\mathbf{z}_i)-\mathcal{G}^{\dagger}(\mathbf{z}_j)\|}{\|\mathbf{z}_i-\mathbf{z}_j\|_{\mathcal{Z}}}'],
         pill='IN PRACTICE',
         land='A Fourier neural operator (Li et al. 2021, ICLR) or DeepONet (Lu, Jin, Pang, Zhang & Karniadakis 2021, Nature '
              'Machine Intelligence). $d_{\\mathrm{eff}}$: PCA dimension of the simulated fields; $N$ is a starting point, '
              'the learning curve decides.'),
    dict(t='Place T and certify', color='orange',
         idea='Estimate the descriptor of T from its data, measure its distance to the training aquifers and bound the '
              'error of the transferred model.',
         eqs=[r'd_T=\min_i\|\hat{\mathbf{z}}_T-\mathbf{z}_i\|_{\mathcal{Z}},\qquad u_T=\|\mathbf{z}_T-\hat{\mathbf{z}}_T\|_{\mathcal{Z}}',
              r'\|\mathcal{G}^{\dagger}(\mathbf{z}_T)-\mathcal{G}_w(\hat{\mathbf{z}}_T)\|\le B_T=\varepsilon_{\mathrm{tr}}+(L^{\dagger}+L_w)d_T+L^{\dagger}u_T'],
         pill='DECISION',
         land='$B_T\\le\\varepsilon_{\\star}$: transfer. Otherwise add simulations near $\\hat{\\mathbf{z}}_T$, or measure the '
              'group $j$ with the largest $L^{\\dagger}_ju_{T,j}$. $L^{\\dagger}$ is large near a change of regime (small $a$: '
              'the toe moves fast inland); there the transfer is risky.'),
    dict(t='Assimilate at T', color='amber',
         idea='The descriptor joins the state of the filter, and the certificate becomes model error.',
         eqs=[r'\mathbf{X}_T=\big(\mathbf{v},\,\mathbf{b},\,\boldsymbol{\gamma},\,\hat{\mathbf{z}}_T\big),\qquad C^{f}\leftarrow C^{f}+B_T^{2}I',
              r'\mathbf{X}^{a}=\mathbf{X}^{f}+C^{Xy}\big(C^{yy}+\Gamma\big)^{-1}\big(\mathbf{y}+\mathbf{e}-\mathcal{Y}\big)'],
         pill='IN PRACTICE',
         land='Every datum of T shrinks $u_T$ and with it $B_T$. Boundary priors, regimes (normal, surge, drought, flood) and '
              'the initial state are re-learned at T.'),
    dict(t='Watch the transfer', color='pink',
         idea='While the model runs at T, an alarm and a coverage count say whether the transfer still holds.',
         eqs=[r'\mathrm{NIS}_n=\boldsymbol{\nu}_n^{\top}S_n^{-1}\boldsymbol{\nu}_n>\chi^{2}_{m,1-\alpha}\ \ \text{under every regime}',
              r'\frac{1}{M}\sum_{j=1}^{M}\mathbf{1}\big\{|x_j-\hat{x}_j|\le1.645\,\hat{\sigma}_j\big\}\approx0.90'],
         pill='CHECK AT T',
         land='False alarms occur at exactly the rate $\\alpha$ in any aquifer (the assimilation note). An alarm under every '
              'regime, or a drop in coverage on twins of T: the transfer is broken; certify again with the updated '
              '$\\hat{\\mathbf{z}}_T$, or add a regime or a closure.'),
    dict(t='Carried over, rescaled, re-learned', color='brown',
         idea='Each boundary keeps its type of condition, is rescaled into the units of T and re-learned from its records.',
         eqs=[r'\eta^{*}=\frac{K_G\eta}{q_b d},\quad R^{*}=\frac{R}{q_b},\quad Q^{*}=\frac{Q}{q_b d^{2}},\quad \tau^{*}=\frac{q_b\tau}{\phi d}',
              r'x_s=\sqrt{2T\tau/S},\qquad \omega_1=\pi^{2}T/(4SL^{2})'],
         pill='CHECK AT T',
         land='$T$, $S$: transmissivity, storativity. A boundary event decays inland over $x_s$ (Ferris 1951); a first '
              'piezometer beyond $x_s$ misses it: add a tide gauge. $\\omega_1$ sets the record length; mode $j$ is learnt '
              'within $t\\approx1/(2\\omega_j)$.'),
]


def build():
    cov = coverage()
    nis = nis_series()
    tex = Tex()
    svg, overlays = hero(tex, cov, nis)
    html = build_page(tex, kicker='TRANSFER  ·  ROUTE R1  ·  A MODEL THAT CAN TRAVEL',
                      title='One operator for every coastal aquifer: certify, assimilate, watch',
                      tags=[('CLASSICAL', 'rebuild and recalibrate the model at every site'),
                            ('NEW', 'one operator · a certificate · the certificate as model error')],
                      hero_svg=svg, overlays=overlays, hero_y1=HERO_Y1, innov=innov(cov), innov_box=(1584, 132, 784, 694),
                      cards=CARDS, card_top=HERO_Y1 + 12, card_h=408, card_gap=12)
    open('d6_transfer_r1.html', 'w').write(html)
    r, wide, plain, cmin, rmin = cov
    x, thr, brk, alarm, seed = nis
    print('wrote d6_transfer_r1.html; coverage min %.6f at r = %.4f; plain at r = 3: %.3f; NIS seed %d, alarm at step %d '
          '(break %d); x_s = %.1f m' % (cmin, rmin, plain[-1], seed, alarm, brk, x_skin()))


if __name__ == '__main__':
    build()
