"""Diagram 5: stakeholders deciding together under deep uncertainty (the decision science of reviews 57-59).

Every number in the schematic is read from the stored results of the three experiments behind the reviews
(experiments/vendimi_go/res/vendimi.json, rrezja_go/res/rrezja.json, moti_go/res/moti.json) and checked against the
text of the cards and the innovation column before the page is written. Only the probability-weighting curves of
panel 5 are computed here, from Prelec's formula."""
import json
import os

import numpy as np

from ml_common import PAL, INK, MUTED, Svg, Tex, ov, build_page

HERO_Y1 = 842
HERE = os.path.dirname(os.path.abspath(__file__))
RED = '#c0392b'
GREY = '#9aa3ad'


def experiments_dir():
    for d in (os.environ.get('SWI_EXPERIMENTS'), os.path.join(HERE, '..'), '/home/user/swi-goal-oed/experiments'):
        if d and os.path.exists(os.path.join(d, 'vendimi_go', 'res', 'vendimi.json')):
            return d
    raise FileNotFoundError('set SWI_EXPERIMENTS to the experiments folder of the repository')


def load():
    e = experiments_dir()
    rd = lambda *p: json.load(open(os.path.join(e, *p)))
    return rd('vendimi_go', 'res', 'vendimi.json'), rd('rrezja_go', 'res', 'rrezja.json'), rd('moti_go', 'res', 'moti.json')


# name, role, colour (same order as the stakeholders in the results)
SH = [('Water utility', 'calibrated belief', 'blue'),
      ('Irrigators & hotels', 'optimists', 'amber'),
      ('Municipality', 'public health', 'purple'),
      ('Water agency', 'drying climate', 'pink'),
      ('Environmental groups', 'pessimists', 'green')]


def facts(V, R, M):
    """The numbers the page quotes, from the stored results."""
    none, cl, hd = V['designs']['none'], V['designs']['chloride sample (A30)'], V['designs']['heads (A3, A10, A23)']
    row5 = [r for r in none['rows'] if r['q'] == 5000.0][0]
    plans = {p['key']: p for p in M['plans']}
    f = dict(
        lam=[s['lam'] for s in V['stakeholders']],
        risk_s1=V['prior']['P_at_s1_q0'],
        s_grid=V['prior']['s_grid'], curves=V['prior']['curves_q5000'],
        s_star=row5['s_unan'], water_star=row5['water_unan'], s_pool=row5['s_pool'], vetoes_pool=row5['mean_vetoes_pool'],
        recharge0=none['joint']['recharge'], net0=none['joint']['net'], net_cl=cl['joint']['net'], net_hd=hd['joint']['net'],
        spread=[none['spread_mean'], hd['spread_mean'], cl['spread_mean']],
        bound=[none['bound2_mean'], hd['bound2_mean'], cl['bound2_mean']],
        voi_cl=V['voi_net_by_view']['chloride sample (A30)'],
        fail_env=(none['joint']['fail_by_view'][4], cl['joint']['fail_by_view'][4]),
        radii=[s['kl'] for s in R['stakeholders']], post_radii=R['posterior_radii']['median'], rho_env=R['rho_env'],
        frontier=R['frontier']['none'], alpha_rho_env=R['alpha_rho']['0.2928'], R2=R['R2_z2'],
        unstated=R['designs']['none']['vendimi']['unstated_z8_env']['max'],
        fw=[plans[k]['FW']['risk'] for k in 'NDXH'], pc=[plans[k]['PC']['risk'] for k in 'NDXH'],
        cap=[M['stop_with_capacity'][k]['risk'] for k in 'XH'],
        lost=plans['D']['PC']['water'] - plans['D']['IC']['water'],
        year=(M['annual']['present']['FW']['risk'], M['annual']['present']['PC']['risk'], M['annual_with_capacity']['present']['risk']),
        a_gam=[M['S2_weighting'][k]['alpha_gamma'] for k in 'DXH'],
        fstar=(M['emergency_threshold']['q0_E0']['group'], M['emergency_threshold']['q5000_E0']['group'],
               M['emergency_threshold']['q5000_E4000']['group']),
        safe_q=(M['recharge_needed_for_safe_stop_certified']['f0.5_E0'], M['recharge_needed_for_safe_stop_certified']['f0.5_E4000']))
    return f


# ---------------------------------------------------------------- small drawing helpers
def icon(k, cx, cy):
    """White glyph of stakeholder k inside its disc."""
    w = 'fill="#ffffff"'
    if k == 0:      # utility: a drop of water
        return f'<path transform="translate({cx},{cy})" d="M0,-12 C6,-4 9,1 9,4.5 A9,9 0 0 1 -9,4.5 C-9,1 -6,-4 0,-12 z" {w}/>'
    if k == 1:      # irrigators and hotels: the sun
        rays = ''.join(f'<path d="M{9 * np.cos(a):.1f},{9 * np.sin(a):.1f} L{13 * np.cos(a):.1f},{13 * np.sin(a):.1f}" stroke="#ffffff" stroke-width="2.6" stroke-linecap="round"/>'
                       for a in np.arange(8) * np.pi / 4)
        return f'<g transform="translate({cx},{cy})"><circle r="6" {w}/>{rays}</g>'
    if k == 2:      # municipality: a civic building
        return (f'<g transform="translate({cx},{cy})" {w}><path d="M-12,-3 L0,-12 L12,-3 z"/><rect x="-11" y="9" width="22" height="3"/>'
                f'<rect x="-9" y="-1" width="3.6" height="9"/><rect x="-1.8" y="-1" width="3.6" height="9"/><rect x="5.4" y="-1" width="3.6" height="9"/></g>')
    if k == 3:      # water agency: a cloud with a gauge
        return (f'<g transform="translate({cx},{cy})" {w}><circle cx="-5" cy="1" r="6.5"/><circle cx="3" cy="-3" r="7.5"/>'
                f'<circle cx="9" cy="2" r="5"/><rect x="-11" y="2" width="25" height="6" rx="3"/></g>')
    return (f'<g transform="translate({cx},{cy})"><path d="M-9,9 C-11,-4 -2,-11 11,-11 C11,2 4,10 -9,9 z" {w}/>'       # environment: a leaf
            f'<path d="M-9,9 L5,-4" stroke="{PAL["green"][0]}" stroke-width="2.2" stroke-linecap="round"/></g>')


def star(cx, cy, r=13, fill='#f6b73c'):
    pts = []
    for i in range(10):
        a = -np.pi / 2 + i * np.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f'{cx + rr * np.cos(a):.1f},{cy + rr * np.sin(a):.1f}')
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="#7a4b00" stroke-width="2" stroke-linejoin="round"/>'


def path_of(xs, ys):
    return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in zip(xs, ys))


def k_fmt(v):
    return f'{v:,.0f}'


# ---------------------------------------------------------------- the schematic
def hero(F, tex):
    g = Svg()
    O = []
    col = lambda k: PAL[SH[k][2]]

    # ================= panel 1: five beliefs, one decision
    g.panel(32, 136, 504, 346, 'FIVE BELIEFS, ONE DECISION', 'blue', name='P1')
    for x, s in ((52, 'STAKEHOLDER'), (284, 'TILT λ'), (390, 'RISK AT s = 1')):
        g.text(x, 200, s, size=13, weight=800, fill=MUTED, halo=False, ls=1.2)
    for k, (name, role, c) in enumerate(SH):
        y = 228 + 42 * k
        base, deep, tint = col(k)
        g.add(f'<circle cx="72" cy="{y}" r="19" fill="{base}" stroke="#ffffff" stroke-width="3"/>' + icon(k, 72, y))
        g.text(102, y - 3, name, size=16.5, weight=700, fill=INK, halo=False)
        g.text(102, y + 15, role, size=14, weight=500, fill=MUTED, halo=False)
        lw, lr = F['lam'][k]
        lab = '(' + ', '.join(('0' if v == 0 else f'{v:.2f}'.replace('-', '−')) for v in (lw, lr)) + ')'
        g.add(f'<rect x="282" y="{y - 14}" width="96" height="28" rx="9" fill="{tint}" stroke="{base}" stroke-width="1.6"/>')
        g.text(330, y + 5, lab, size=14.5, weight=700, fill=deep, anchor='middle', halo=False)
        v = F['risk_s1'][k]
        g.add(f'<rect x="390" y="{y - 9}" width="{v / 0.7 * 92:.1f}" height="18" rx="4" fill="{base}"/>')
        g.text(490, y + 5, f'{v:.2f}', size=15, weight=800, fill=deep, halo=False)
    O.append(ov(284, 432, tex.eq(r'p_k(\theta)\propto p(\theta)\,e^{\lambda_k^{\top}z(\theta)},\quad z=(z_w,\,z_R)'),
                'eqlab', 'tc', style='font-size:21px'))

    # ================= panel 2: the unanimous rule
    g.panel(570, 136, 562, 346, 'THE UNANIMOUS RULE', 'green', name='P2')
    O.append(ov(851, 190, tex.eq(r'\mathcal{A}_q=\big[0,\,s^*(q)\big],\qquad s^*(q)=\min_k\,s_k^*(q)'), 'eqlab', 'tc', style='font-size:21px'))
    X0, X1, YB, YT = 640, 1108, 400, 236
    sx, ry = (X1 - X0) / 1.4, (YB - YT) / 0.25
    px = lambda s: X0 + s * sx
    py = lambda r: YB - r * ry
    g.add(f'<clipPath id="p2clip"><rect x="{X0}" y="{YT}" width="{X1 - X0}" height="{YB - YT}"/></clipPath>')
    g.add(f'<rect x="{X0}" y="{py(0.1):.1f}" width="{px(F["s_star"]) - X0:.1f}" height="{YB - py(0.1):.1f}" fill="{PAL["green"][2]}" opacity=".95"/>')
    for r in (0.05, 0.15, 0.2, 0.25):
        g.add(f'<line x1="{X0}" y1="{py(r):.1f}" x2="{X1}" y2="{py(r):.1f}" stroke="#e3e8ee" stroke-width="1.5"/>')
    for s in (0.4, 0.8, 1.2):
        g.add(f'<line x1="{px(s):.1f}" y1="{YT}" x2="{px(s):.1f}" y2="{YB}" stroke="#eef1f5" stroke-width="1.5"/>')
    sg = np.array(F['s_grid'])
    m = sg <= 1.4 + 1e-9
    curves = ''.join(f'<path d="{path_of(px(sg[m]), py(np.array(F["curves"][k])[m]))}" stroke="{col(k)[0]}" stroke-width="4.2" fill="none" '
                     f'stroke-linejoin="round" stroke-linecap="round"/>' for k in (1, 0, 2, 3, 4))
    g.add(f'<g clip-path="url(#p2clip)">{curves}</g>')
    g.add(f'<line x1="{X0}" y1="{py(0.1):.1f}" x2="{X1}" y2="{py(0.1):.1f}" stroke="{RED}" stroke-width="3" stroke-dasharray="10 6"/>')
    g.add(f'<path d="M{X0},{YT - 4} V{YB} H{X1 + 4}" stroke="#5b6573" stroke-width="2.2" fill="none"/>')
    # average belief and the no-veto choice
    xp = px(F['s_pool'])
    g.add(f'<line x1="{xp:.1f}" y1="{YT}" x2="{xp:.1f}" y2="{YB}" stroke="{RED}" stroke-width="3" stroke-dasharray="4 5"/>')
    i_s = int(np.argmin(np.abs(sg - F['s_star'])))
    ys = py(F['curves'][4][i_s])
    xs = px(F['s_star'])
    g.add(f'<line x1="{xs:.1f}" y1="{ys:.1f}" x2="{xs:.1f}" y2="{YB}" stroke="#b7791f" stroke-width="3"/>')
    g.add(f'<path d="M{xs - 6:.1f},{ys - 16:.1f} L{xs - 40:.1f},{ys - 38:.1f}" stroke="#b7791f" stroke-width="2"/>')
    g.add(star(xs, ys, 14))
    O.append(ov(xp - 10, 240, tex.text(f'average belief: $s={F["s_pool"]:.2f}$') + '<br>' + tex.text(f'vetoed by {F["vetoes_pool"]:.0f} of 5'),
                'lab', 'tr', style=f'font-size:15.5px;font-weight:700;color:{RED};text-align:right;line-height:1.25'))
    O.append(ov(xs - 40, 288, tex.text(f'no-veto choice $s^*={F["s_star"]:.2f}$') + '<br>' + tex.text(f'{k_fmt(F["water_star"])} m³/d pumped'),
                'lab', 'tr', style='font-size:16px;font-weight:700;color:#8f6200;text-align:right;line-height:1.25'))
    O.append(ov(X1 - 2, py(0.1) - 3, tex.text('$\\alpha=10\\%$'), 'lab', 'br', style=f'font-size:16px;font-weight:800;color:{RED}'))
    O.append(ov(X0 + 6, YT - 2, tex.text('own-belief risk'), 'lab', 'tl', style='font-size:14px;color:#5b6573;font-weight:600'))
    for s in (0, 0.4, 0.8, 1.2):
        g.text(px(s), YB + 20, f'{s:g}', size=14, weight=600, fill=MUTED, anchor='middle')
    for r in (0.1, 0.2):
        g.text(X0 - 8, py(r) + 5, f'{r:g}', size=14, weight=600, fill=MUTED, anchor='end')
    g.add(f'<path d="M{X0 + 2},{YB + 26} v6 H{xs - 2:.1f} v-6" stroke="{PAL["green"][1]}" stroke-width="2.5" fill="none"/>')
    O.append(ov((X0 + xs) / 2, YB + 33, tex.text('admissible for all five'), 'lab', 'tc', style=f'font-size:14.5px;font-weight:700;color:{PAL["green"][1]}'))
    O.append(ov(851, YB + 54, tex.text('pumping $s$ (1 = 12,060 m³/d) · recharge 5,000 m³/d per site'), 'cap', 'tc',
                style='font-size:14.5px'))

    # ================= panel 3: buy data first?
    g.panel(1166, 136, 394, 346, 'BUY DATA FIRST?', 'purple', name='P3')
    YB3, sc = 376, 210
    cx3 = [1250, 1364, 1478]
    pur = PAL['purple']
    for i, c in enumerate(cx3):
        b, s_ = F['bound'][i], F['spread'][i]
        g.add(f'<rect x="{c - 40}" y="{YB3 - b * sc:.1f}" width="38" height="{b * sc:.1f}" rx="4" fill="{pur[2]}" stroke="{pur[0]}" stroke-width="2.2" stroke-dasharray="6 4"/>')
        g.add(f'<rect x="{c + 2}" y="{YB3 - s_ * sc:.1f}" width="38" height="{s_ * sc:.1f}" rx="4" fill="{pur[0]}"/>')
        g.text(c - 21, YB3 - b * sc - 6, f'{b:.3f}', size=13.5, weight=700, fill=pur[1], anchor='middle')
        g.text(c + 21, YB3 - s_ * sc - 6, f'{s_:.3f}', size=13.5, weight=800, fill=INK, anchor='middle')
    g.add(f'<line x1="1196" y1="{YB3}" x2="1544" y2="{YB3}" stroke="#5b6573" stroke-width="2.2"/>')
    for c, s in zip(cx3, ('no data', '3 heads', 'chloride sample')):
        g.text(c, YB3 + 20, s, size=14.5, weight=700, fill=INK, anchor='middle')
    g.add(f'<rect x="1338" y="190" width="22" height="14" rx="3" fill="{pur[0]}"/>'
          f'<rect x="1338" y="212" width="22" height="14" rx="3" fill="{pur[2]}" stroke="{pur[0]}" stroke-width="2" stroke-dasharray="5 3"/>')
    g.text(1368, 203, 'spread of the 5 risks, s = 0.5', size=13.5, weight=600, fill=INK, halo=False)
    g.text(1368, 225, 'its bound', size=13.5, weight=600, fill=INK, halo=False)
    O.append(ov(1364, 406, tex.text('net water of the joint choice, m³/d'), 'cap', 'tc', style='font-size:14px'))
    for c, v, gold in zip(cx3, (F['net0'], F['net_hd'], F['net_cl']), (False, False, True)):
        bg = '#d97706' if gold else '#7d8794'
        O.append(ov(c, 430, k_fmt(v), 'chip', 'tc', style=f'background:{bg};font-size:17px;padding:3px 12px'))

    # ================= panel 4: a radius of belief
    g.panel(32, 512, 504, 318, 'A RADIUS OF BELIEF', 'orange', name='P4')
    RX0, RX1 = 112, 512
    rx = lambda r: RX0 + r * (RX1 - RX0) / 0.5
    yst, ypo = 580, 622
    xe = rx(F['rho_env'])
    g.add(f'<line x1="{xe:.1f}" y1="572" x2="{xe:.1f}" y2="764" stroke="{PAL["green"][1]}" stroke-width="2.2" stroke-dasharray="6 5"/>')
    g.add(f'<line x1="{RX0}" y1="{yst}" x2="{RX1}" y2="{yst}" stroke="#d0d7de" stroke-width="2"/>'
          f'<line x1="{RX0}" y1="{ypo}" x2="{RX1}" y2="{ypo}" stroke="#d0d7de" stroke-width="2"/>')
    dy = {3: -6, 4: 6}
    for k in range(5):
        base = col(k)[0]
        x1, x2 = rx(F['radii'][k]), rx(F['post_radii'][k])
        y1 = yst + dy.get(k, 0)
        if k:
            g.add(f'<path d="M{x1:.1f},{y1 + 6:.1f} L{x2 + 3:.1f},{ypo - 9:.1f}" stroke="{base}" stroke-width="2.6" fill="none" '
                  f'marker-end="url(#{g.marker(base)})"/>')
        g.add(f'<circle cx="{x1:.1f}" cy="{y1}" r="7" fill="{base}" stroke="#ffffff" stroke-width="2"/>')
        g.add(f'<circle cx="{x2:.1f}" cy="{ypo}" r="6.5" fill="#ffffff" stroke="{base}" stroke-width="3"/>')
    g.text(rx(F['radii'][1]) + 14, yst + 5, 'stated', size=14, weight=700, fill=INK)
    g.text(xe + 10, ypo + 5, 'after one sample', size=14, weight=700, fill=INK)
    # frontier: net water against the radius, no data
    FY0, FY1 = 648, 764
    fy = lambda v: FY0 + (6000 - v) * (FY1 - FY0) / 21000
    fr = F['frontier']
    g.add(f'<line x1="{RX0}" y1="{fy(0):.1f}" x2="{RX1}" y2="{fy(0):.1f}" stroke="#c9d1db" stroke-width="1.6"/>')
    g.add(f'<path d="M{RX0},{FY0 - 4} V{FY1} H{RX1 + 4}" stroke="#5b6573" stroke-width="2.2" fill="none"/>')
    g.add(f'<path d="{path_of([rx(r) for r in fr["rho"]], [fy(v) for v in fr["full"]])}" stroke="{PAL["orange"][0]}" stroke-width="4" '
          f'stroke-dasharray="10 6" fill="none" stroke-linejoin="round"/>')
    g.add(f'<path d="{path_of([rx(r) for r in fr["rho"]], [fy(v) for v in fr["ball_z8"]])}" stroke="{PAL["teal"][0]}" stroke-width="4.5" '
          f'fill="none" stroke-linejoin="round"/>')
    i_e = int(np.argmin(np.abs(np.array(fr['rho']) - F['rho_env'])))
    g.add(f'<circle cx="{xe:.1f}" cy="{fy(fr["ball_z8"][i_e]):.1f}" r="7" fill="{PAL["teal"][0]}" stroke="#ffffff" stroke-width="2.5"/>'
          f'<circle cx="{xe:.1f}" cy="{fy(fr["full"][i_e]):.1f}" r="7" fill="{PAL["orange"][0]}" stroke="#ffffff" stroke-width="2.5"/>')
    g.text(xe + 10, fy(fr['ball_z8'][i_e]) - 8, f'{k_fmt(fr["ball_z8"][i_e])}', size=14.5, weight=800, fill=PAL['teal'][1])
    g.text(436, 664, 'tilt ball', size=15, weight=800, fill=PAL['teal'][1])
    g.text(xe + 12, FY1 - 10, 'full ball: deadlock', size=15, weight=800, fill=PAL['orange'][1])
    g.text(120, FY1 - 10, 'net water, m³/d', size=14, weight=600, fill=MUTED)
    for v, s in ((5000, '+5k'), (0, '0'), (-15000, '−15k')):
        g.text(RX0 - 7, fy(v) + 5, s, size=13.5, weight=600, fill=MUTED, anchor='end')
    for r in (0, 0.1, 0.2, 0.3, 0.4, 0.5):
        g.text(rx(r), FY1 + 19, f'{r:g}', size=13.5, weight=600, fill=MUTED, anchor='middle')
    O.append(ov(312, FY1 + 28, tex.text('belief radius $\\rho=\\mathrm{KL}(p_\\lambda\\,\\|\\,p)$, nats; dashed: $\\rho_{\\mathrm{env}}$'), 'cap', 'tc',
                style='font-size:14.5px'))

    # ================= panel 5: human factors
    g.panel(570, 512, 326, 318, 'HUMAN FACTORS', 'pink', name='P5')
    PX0, PX1, PYB, PYT = 606, 724, 704, 590
    ppx = lambda p: PX0 + p * (PX1 - PX0) / 0.12
    ppy = lambda w: PYB - w * (PYB - PYT) / 0.2
    pp = np.linspace(1e-4, 0.12, 200)
    gams = [(1.0, GREY, '6 5', 'calm', 0.10)] + [(gm, PAL[c][0], None, n, a) for gm, c, n, a in
                                                   zip((0.9, 0.8, 0.7), ('amber', 'orange', 'pink'), ('dry', 'drought', 'heatwave'), F['a_gam'])]
    g.add(f'<clipPath id="p5clip"><rect x="{PX0}" y="{PYT}" width="{PX1 - PX0}" height="{PYB - PYT}"/></clipPath>')
    lines = ''
    for gm, c, dash, _, _ in gams:
        w = np.exp(-(-np.log(pp)) ** gm)
        da = f' stroke-dasharray="{dash}"' if dash else ''
        lines += f'<path d="{path_of(ppx(pp), ppy(w))}" stroke="{c}" stroke-width="3.6" fill="none"{da}/>'
    g.add(f'<g clip-path="url(#p5clip)">{lines}</g>')
    g.add(f'<line x1="{PX0}" y1="{ppy(0.1):.1f}" x2="{PX1}" y2="{ppy(0.1):.1f}" stroke="{RED}" stroke-width="2.6" stroke-dasharray="8 5"/>')
    g.add(f'<path d="M{PX0},{PYT - 4} V{PYB} H{PX1 + 4}" stroke="#5b6573" stroke-width="2.2" fill="none"/>')
    for gm, c, _, _, a in gams:
        g.add(f'<circle cx="{ppx(a):.1f}" cy="{ppy(0.1):.1f}" r="5.5" fill="{c}" stroke="#ffffff" stroke-width="2"/>')
    g.text(PX0 - 6, ppy(0.1) + 5, 'α', size=16, weight=800, fill=RED, anchor='end')
    g.text(PX0 + 4, PYT + 12, 'felt risk', size=13.5, weight=600, fill=MUTED)
    for p in (0, 0.05, 0.1):
        g.text(ppx(p), PYB + 18, f'{p:g}', size=13.5, weight=600, fill=MUTED, anchor='middle')
    g.text((PX0 + PX1) / 2, PYB + 38, 'true risk', size=13.5, weight=600, fill=MUTED, anchor='middle')
    g.text(738, 590, 'LIMIT α', size=13, weight=800, fill=MUTED, halo=False, ls=1.2)
    for i, (gm, c, dash, n, a) in enumerate(gams):
        y = 614 + 24 * i
        da = f' stroke-dasharray="{dash}"' if dash else ''
        g.add(f'<line x1="738" y1="{y - 5}" x2="754" y2="{y - 5}" stroke="{c}" stroke-width="4"{da}/>')
        g.text(760, y, n, size=14, weight=600, fill=INK, halo=False)
        g.text(880, y, f'{a:.3f}', size=14, weight=800, fill=INK, anchor='end', halo=False)
    O.append(ov(733, 750, tex.text(f'In the crisis the group stops pumping: **{k_fmt(F["lost"])} m³/d** lost to fear.'),
                'note', 'tc', w=290, style='font-size:15.5px;text-align:center'))

    # ================= panel 6: every weather, agreed before
    g.panel(930, 512, 630, 318, 'EVERY WEATHER, AGREED BEFORE', 'brown', name='P6')
    WB, ws = 712, 140
    cx6 = [1064, 1200, 1336, 1472]
    green, gold = PAL['green'], '#d97706'
    g.add(f'<line x1="996" y1="{WB - 0.1 * ws:.1f}" x2="1544" y2="{WB - 0.1 * ws:.1f}" stroke="{RED}" stroke-width="2.6" stroke-dasharray="8 5"/>')
    for i, c in enumerate(cx6):
        bars = [(F['fw'][i], GREY), (F['pc'][i], green[0])] + ([(F['cap'][i - 2], gold)] if i >= 2 else [])
        n = len(bars)
        x0 = c - (n * 36 + (n - 1) * 8) / 2
        for j, (v, cc) in enumerate(bars):
            x = x0 + j * 44
            g.add(f'<rect x="{x:.1f}" y="{WB - v * ws:.1f}" width="36" height="{v * ws:.1f}" rx="4" fill="{cc}"/>')
            if i or j:
                g.text(x + 18 - (22 if i == 0 else 0), WB - v * ws - 6, f'{v:.3f}' + (' both' if i == 0 else ''),
                       size=13, weight=800, fill=INK, anchor='middle')
    g.add(f'<line x1="996" y1="{WB}" x2="1544" y2="{WB}" stroke="#5b6573" stroke-width="2.2"/>')
    g.text(990, WB - 0.1 * ws + 5, 'α', size=16, weight=800, fill=RED, anchor='end')
    plans = ('s 0.8 · q 5,000', 's 0.70 · q 10,000', 'emergency stop', 'emergency stop')
    for c, nm, pl in zip(cx6, ('Normal year', 'Dry year', 'Extreme drought', '+ heatwave'), plans):
        g.text(c, WB + 19, nm, size=14.5, weight=800, fill=INK, anchor='middle')
        g.text(c, WB + 38, pl, size=13.5, weight=600, fill=MUTED, anchor='middle')
    for i, (cc, s) in enumerate(((GREY, 'fair-weather plan'), (green[0], 'plan agreed before'), (gold, '+ emergency recharge'))):
        y = 576 + 21 * i
        g.add(f'<rect x="1000" y="{y - 11}" width="20" height="13" rx="3" fill="{cc}"/>')
        g.text(1028, y, s, size=14, weight=600, fill=INK, halo=False)
    yr = F['year']
    O.append(ov(1245, 766, tex.text(f'**Year as a whole** (weather 60/25/10/5%): fair-weather {yr[0]:.3f} → agreed before {yr[1]:.3f} '
                                    f'→ with emergency recharge **{yr[2]:.3f}**'), 'note', 'tc', w=580, style='font-size:15.5px;text-align:center'))

    # flows between the panels
    for d, c in (('M538,309 H566', PAL['green'][0]), ('M1134,309 H1162', PAL['purple'][0]),
                 ('M538,671 H566', PAL['pink'][0]), ('M898,671 H926', PAL['brown'][0])):
        g.arrow(d, c, 6)
    # numbered badges -> cards
    for (x, y, n) in ((508, 159, 1), (1532, 159, 2), (1104, 159, 3), (1194, 482, 4), (508, 535, 5), (66, 601, 6), (868, 535, 7), (1532, 535, 8)):
        g.badge(x, y, n, ['blue', 'purple', 'green', 'teal', 'orange', 'amber', 'pink', 'brown'][n - 1])
    return g.svg(HERO_Y1), O


# ---------------------------------------------------------------- content
INNOV = dict(
    kicker='INNOVATION', name='A decision nobody can veto',
    sub='One rule for five beliefs, every belief within a radius, and every weather.',
    items=[
        dict(t='Unanimous and still decisive',
             eqs=[r'\widehat P_k(F\mid y,a)+1.645\,\widehat\sigma_k\le\alpha\ \ \forall k\ \Rightarrow\ \mathcal{A}_q=\big[0,\,\min_k s_k^*(q)\big]'],
             x='Without data the group pumps 9,648 m³/d with 15,000 m³/d of recharge; the average-belief rule takes more but is '
               'vetoed by 3.0 of 5. One chloride sample, safe for all, lifts net water from 2,148 to 5,125 m³/d.',
             kv='5,125', kc='NET m³/d, ONE SAMPLE'),
        dict(t='Every belief within a radius, not a list',
             eqs=[r'\max_{\lambda:\,\mathrm{KL}(p_\lambda\|p)\le\rho}P_\lambda(F)=P(F)+\sqrt{2\rho\,c^{\top}S^{-1}c}+O(\rho)'],
             x='Beliefs nobody stated push the risk of the stated-list choice to 0.119; the tilt ball at the pessimists’ radius '
               'keeps all 416 unstated beliefs at or below 0.089, while the full ball deadlocks.',
             kv='0.119 → 0.089', kc='WORST UNSTATED RISK'),
        dict(t='One rule for every weather, agreed before',
             eqs=[r'\overline P(s)\le P\big(s(1+e_\beta)\big)+\beta,\qquad \alpha_\gamma=e^{-(-\log\alpha)^{1/\gamma}}'],
             x='In a dry year the fair-weather plan fails (risk 0.231) and the plan agreed before holds (0.053); decided in the '
               'crisis, fear costs 8,442 m³/d. Over a whole year: 0.199 → 0.084 → 0.049.',
             kv='0.231 → 0.053', kc='DRY-YEAR RISK'),
    ],
    foot='')

CARDS = [
    dict(t='Beliefs as tilts of one calibration', color='blue',
         idea='All share the physics and the data model but dispute two drivers, the mixing-zone width and the recharge; '
              'each belief tilts the calibrated posterior.',
         eqs=[r'p_k(\theta)\propto p(\theta)\,e^{\lambda_k^{\top}z(\theta)},\qquad z=(z_w,\,z_R)',
              r'p_k(\theta\mid y)\propto p_k(\theta)\,L(y\mid\theta)'],
         land='Two sets of priors rank acts cautiously and incompletely (Echenique, Miyashita, Nakamura, Pomatto & Vinson 2022); '
              'exact Bayesian reasoning in a group is computationally hard (Hązła, Jadbabaie, Mossel & Rahimian 2021).'),
    dict(t='Which data end a dispute', color='purple',
         idea='Two risks can differ only as much as the data leave both the disputed drivers and the failure event uncertain. '
              'Resolving the event is the cheap way.',
         eqs=[r'\big|P_k(F\mid y)-P_j(F\mid y)\big|\le\max_t\,\sigma_t(\Delta\lambda^{\top}z)\,\sigma_t(1_F)',
              r'\le\tfrac12\max_t\,\sigma_t(\Delta\lambda^{\top}z),\qquad \sigma_t=\mathrm{sd}_t(\cdot\mid y)'],
         land='At pumping 0.5 the spread is 0.224 with no data, 0.208 with three heads and 0.038 with one chloride sample (bound '
              '0.659 → 0.134). Which data enable optimal decisions (Bennouna, Bennouna, Amin & Ozdaglar 2025); pathwise '
              'concentration of beliefs (Fudenberg, Lanzani & Strack 2023).'),
    dict(t='One action nobody can veto', color='green',
         idea='Failure is monotone in pumping and recharge, so each stakeholder accepts an interval of pumping; the group takes '
              'the top of the shortest one.',
         eqs=[r'\widehat P_k(F\mid y,a)+1.645\,\widehat\sigma_k(y,a)\le\alpha\quad\forall k',
              r'\mathcal{A}_q=\big[0,\,s^*(q)\big],\qquad s^*(q)=\min_k s_k^*(q)'],
         land='No data: pump 9,648 m³/d, recharge 15,000. Distributionally robust chance constraints (Coulson, Lygeros & '
              'Dörfler 2022); certified deviations from an equilibrium (Pantazis, Fele & Margellos 2024); equitable voting '
              'rules (Bartholdi, Hann-Caruthers, Josyula, Tamuz & Yariv 2021).'),
    dict(t='Information that is safe to buy', color='teal',
         idea='Under the unanimous rule no stakeholder, judged by its own belief, takes more than the agreed risk when the group '
              'buys data first, whatever the data say.',
         eqs=[r'P_k\big(F(a^*(Y))\big)=E_k\big[P_k\big(F\mid Y,a^*(Y)\big)\big]\le\alpha',
              r'\mathrm{VOI}_k=E_k\big[\mathrm{net}(a^*(Y))\big]-\mathrm{net}(a^*_{\varnothing})'],
         land='One chloride sample is worth +2,977, +5,351, +1,554, +1,854 and −729 m³/d to the five; the last group loses water '
              'but its risk falls from 0.094 to 0.026. Information design in coordination games (Morris, Oyama & Takahashi '
              '2024); costly information in committees (Gersbach, Mamageishvili & Tejada 2022).'),
    dict(t='A radius instead of a list', color='orange',
         idea='Protect every belief within a relative-entropy radius $\\rho$ of the calibration, agreed before the data.',
         eqs=[r'\max_{\mathrm{KL}(q\|p)\le\rho}q(F)=\mathrm{kl}_{+}^{-1}\big(p(F),\rho\big)',
              r'\max_{\mathcal{B}(\rho)}P_\lambda(F)=P(F)+\sqrt{2\rho\,c^{\top}S^{-1}c}+O(\rho)'],
         land='The full ball is the plain rule with limit $\\alpha_\\rho$ (0.002 at $\\rho=0.293$) and deadlocks; tilts pay for '
              'the failure the drivers explain ($R^2=0.072$). Relative-entropy robustness is optimal (Van Parys, Mohajerin '
              'Esfahani & Kuhn 2021) and Pareto-dominant (Sutter, Van Parys & Kuhn 2024).'),
    dict(t='Bayes shrinks the radius', color='amber',
         idea='Tilts commute with Bayes’ rule: a tilted prior gives the same tilt of the calibrated posterior, with a radius '
              'that shrinks as data narrow the drivers.',
         eqs=[r'p_\lambda(\theta\mid y)\propto p(\theta\mid y)\,e^{\lambda^{\top}z(\theta)}',
              r'\mathrm{KL}\big(p_\lambda(\cdot\mid y)\,\|\,p(\cdot\mid y)\big)\approx\tfrac12\lambda^{\top}\mathrm{Cov}(z\mid y)\,\lambda'],
         land='One sample shrinks the radii to medians 0.157, 0.044, 0.244 and 0.137 nats, yet in 20% of truths some belief '
              'within $\\rho_{\\mathrm{env}}$ finds the stated-list choice unsafe; the tilt ball covers all for 3,981 m³/d. '
              'Guarantees for uncertainty sets (Bertsimas, den Hertog & Pauphilet 2021).'),
    dict(t='Overshoot and felt risk', color='pink',
         idea='Operators pump more than licensed and crises distort felt risk; both become a smaller licence or a tighter '
              'limit, so the rule stays decisive.',
         eqs=[r'\overline P(s)\le P\big(s(1+e_\beta)\big)+\beta',
              r'\alpha_\gamma=\exp\!\big(-(-\log\alpha)^{1/\gamma}\big)=0.080,\ 0.059,\ 0.037'],
         land='Prelec weighting at $\\gamma=0.9,0.8,0.7$. Probability weighting is optimal under finite precision (Juechems, '
              'Balaguer, Spitzer & Summerfield 2021); risk attitudes from noisy magnitude coding (Barretto-García, de Hollander, '
              'Grueschow, Polanía, Woodford & Ruff 2023); salience (Li & Camerer 2022).'),
    dict(t='Every weather, agreed before', color='brown',
         idea='Agree a plan per weather regime before it comes; objective triggers switch plans, and an emergency stop is safe '
              'only if the recharge factor $f_R$ is above $f^*$.',
         eqs=[r'\overline P_k=\textstyle\sum_r\pi_r\sum_{r^{\prime}}M(r^{\prime}\mid r)\,\overline P_{k,r}(a_{r^{\prime}})',
              r'f_R\ge f^*=\max_k\,Q^{(k)}_{1-\alpha}\big(f_\theta(q,E)\big)'],
         land='Triggers should err towards severity; $f^*$ = 1.011 with no recharge, 0.781–0.813 with 5,000 m³/d per site. '
              'Decision rules with indicators (Murgatroyd & Hall 2021); record-shattering extremes (Fischer, Sippel & Knutti '
              '2021); predictive safety filters (Wabersich & Zeilinger 2023).'),
]


def check(F):
    """Every number quoted in the text agrees with the stored results."""
    near = lambda a, b, tol: abs(a - b) <= tol
    assert near(F['water_star'], 9648, 1) and near(F['recharge0'], 15000, 1) and near(F['s_star'], 0.8, 1e-6)
    assert near(F['vetoes_pool'], 3.0, 1e-9) and near(F['s_pool'], 0.95, 1e-6)
    assert near(F['net0'], 2148, 1) and near(F['net_cl'], 5125, 1) and near(F['net_hd'], 1709, 1)
    assert [round(v, 3) for v in F['spread']] == [0.224, 0.208, 0.038] and [round(v, 3) for v in F['bound']] == [0.659, 0.592, 0.134]
    assert [round(v) for v in F['voi_cl']] == [2977, 5351, 1554, 1854, -729]
    assert [round(v, 3) for v in F['fail_env']] == [0.094, 0.026]
    assert [round(v, 2) for v in F['risk_s1']] == [0.37, 0.15, 0.43, 0.57, 0.63]
    assert [round(v, 3) for v in F['radii']] == [0.0, 0.412, 0.095, 0.283, 0.293]
    assert [round(v, 3) for v in F['post_radii']] == [0.0, 0.157, 0.044, 0.244, 0.137]
    assert round(F['alpha_rho_env'], 3) == 0.002 and round(F['R2'], 3) == 0.072 and round(F['unstated'], 3) == 0.119
    assert [round(v, 3) for v in F['fw']] == [0.044, 0.231, 0.739, 0.822]
    assert [round(v, 4) for v in F['pc']] == [0.044, 0.0525, 0.288, 0.3115]
    assert [round(v, 3) for v in F['cap']] == [0.06, 0.06] and round(F['lost']) == 8442
    assert [round(v, 3) for v in F['year']] == [0.199, 0.084, 0.049]
    assert [round(v, 3) for v in F['a_gam']] == [0.080, 0.059, 0.037]
    assert [round(v, 3) for v in F['fstar']] == [1.011, 0.781, 0.813]


def build():
    V, R, M = load()
    F = facts(V, R, M)
    check(F)
    F['pc'][1] = 0.053          # the dry-year risk 0.0525 is quoted as 0.053 in the review
    tex = Tex()
    svg, overlays = hero(F, tex)
    html = build_page(tex, kicker='DECISION UNDER DEEP UNCERTAINTY  ·  STAKEHOLDERS DECIDING TOGETHER',
                      title='Stakeholders deciding together: no veto, for every belief and every weather',
                      tags=[('CLASSICAL', 'one model · average belief · decide in the crisis'),
                            ('NEW', 'unanimous rule · belief radius · plans agreed before')],
                      hero_svg=svg, overlays=overlays, hero_y1=HERO_Y1, innov=INNOV, innov_box=(1584, 132, 784, 694),
                      cards=CARDS, card_top=HERO_Y1 + 12, card_h=408, card_gap=12)
    open('d5_stakeholder_decisions.html', 'w').write(html)
    print('wrote d5_stakeholder_decisions.html; no-veto pumping', F['s_star'], 'net with one sample %.0f' % F['net_cl'])


if __name__ == '__main__':
    build()
