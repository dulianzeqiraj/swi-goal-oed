"""Introduction to the diagram series: the problem statement.

A coastal aquifer feeds supply wells; sea water lies under the fresh water and rises when the wells pump. The goal is the
drinking-water chloride standard in the well screen, not a head target. Pumping, recharge, monitoring and the alarm are
decided under uncertainty by several stakeholders. The numbers come from the test bed of the series: 20,000 weighted
draws of a calibrated areal chloride model of a coastal aquifer (single potential, dispersive mixing zone), two supply
wells each pumped to a 50% own risk. The cross-section is a schematic, not to scale."""
import json
import os

import numpy as np

from ml_common import PAL, ORDER, INK, MUTED, Svg, Tex, ov, build_page

HERO_Y1 = 842
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'pusi_go', 'res', 'pusi.json')          # results of the test bed (experiments/pusi_go)
if not os.path.exists(RES):
    RES = '/home/user/swi-goal-oed/experiments/pusi_go/res/pusi.json'

# ---------------------------------------------------------------- cross-section geometry (page pixels)
XL, XS, XR = 52, 840, 1080          # left edge, shoreline, right edge of the section
YSL, YB, YBR = 262, 540, 566        # sea level, aquifer base, bottom of the bedrock strip
XT = 180                            # toe of the wedge at the base
XW, XP, XC, XM = 440, 250, 620, 760  # supply well, head piezometer, chloride sensor, recharge well


def land(x):
    return 222 + (YSL - 222) * (x - XL) / (XS - XL)


def wt(x):
    return YSL - 16 * (XS - x) / (XS - XL) + 13 * np.exp(-((x - XW) / 50) ** 2) - 7 * np.exp(-((x - XM) / 40) ** 2)


def iface(x):
    base = YSL + (YB - YSL) * np.sqrt(np.clip((XS - x) / (XS - XT), 0, 1))
    return np.minimum(base - 80 * np.exp(-((x - XW) / 40) ** 2), YB)


def seabed(x):
    return YSL + (x - XS) * 0.28


def poly(pts):
    return ' '.join('%.1f,%.1f' % p for p in pts)


def numbers():
    d = json.load(open(RES))
    A, B, C = d['A'], d['B'], d['C']
    sy = C['safe_yield']
    greedy = [g['eig'] for g in C['greedy_heads']]
    return dict(p_proxy=A['P_proxy_any'], p_chem=A['P_chem_any'],
                p_rech_chem=B['designs']['swap_chem']['P_chem'], p_rech_proxy_sites=B['designs']['closed_proxy']['P_chem'],
                p_rech_proxy=B['designs']['swap_chem']['P_proxy'], p_rech_proxy_own=B['designs']['closed_proxy']['P_proxy'], q_needed=B['q_needed_chem'],
                H=C['H_prior'], eig_cl=C['greedy_all'][0]['eig'], eig_heads=max(greedy),
                y_none=sy['none']['yield_m3_d'], y_heads=sy['best_3_heads']['yield_m3_d'],
                y_cl=sy['best_1_cl']['yield_m3_d'], y_two=sy['best_2_all']['yield_m3_d'],
                y_proxy=C['proxy_rule']['yield_m3_d'], f_proxy=C['proxy_rule']['fail_rate_chem'],
                corr_w=A['tau_drivers']['w'][0], corr_phi=A['corr_tau_phi'][0], n=d['n_draws'])


# ---------------------------------------------------------------- the schematic
def hero(tex, N):
    g = Svg()
    O = []
    blue, purple, green, teal, orange, amber, pink, brown = (PAL[c] for c in ORDER)
    g.add('<defs><linearGradient id="saltg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6c4bd"/>'
          '<stop offset="1" stop-color="#e88a80"/></linearGradient>'
          '<linearGradient id="seag" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7fb2df"/>'
          '<stop offset="1" stop-color="#3f7fbf"/></linearGradient>'
          '<linearGradient id="skyg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eef6ff"/>'
          '<stop offset="1" stop-color="#ffffff"/></linearGradient>'
          '<pattern id="sand" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="3" cy="4" r="1.3" fill="#9c8455" opacity=".35"/>'
          '<circle cx="10" cy="10" r="1.1" fill="#9c8455" opacity=".3"/></pattern>'
          '<pattern id="rock" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
          '<line x1="0" y1="0" x2="0" y2="16" stroke="#8a8f98" stroke-width="3"/></pattern></defs>')

    # ======== panel A: the system
    g.panel(32, 136, 1068, 442, 'THE SYSTEM · A COASTAL AQUIFER UNDER PUMPING', 'blue', name='A')
    xs = np.linspace(XL, XS, 300)
    xsea = np.linspace(XS, XR, 60)
    # sky, unsaturated zone, fresh water, salt water, bedrock, sea
    g.add(f'<rect x="{XL}" y="186" width="{XR - XL}" height="{YSL - 186}" fill="url(#skyg)"/>')
    g.add(f'<polygon points="{poly([(x, land(x)) for x in xs] + [(x, wt(x)) for x in xs[::-1]])}" fill="#efe2c4"/>')
    fresh = [(x, wt(x)) for x in xs] + [(x, iface(x)) for x in xs[::-1]]
    g.add(f'<polygon points="{poly(fresh)}" fill="#cfe5f7"/>')
    xi = np.linspace(XT - 40, XS, 260)
    salt = [(x, iface(x)) for x in xi] + [(x, seabed(x)) for x in xsea] + [(XR, YB), (XT - 40, YB)]
    g.add(f'<polygon points="{poly(salt)}" fill="url(#saltg)"/>')
    g.add(f'<polygon points="{poly([(XL, land(XL))] + [(x, land(x)) for x in xs] + [(x, seabed(x)) for x in xsea] + [(XR, YB), (XL, YB)])}" fill="url(#sand)"/>')
    g.add(f'<rect x="{XL}" y="{YB}" width="{XR - XL}" height="{YBR - YB}" fill="#d9dce1"/>'
          f'<rect x="{XL}" y="{YB}" width="{XR - XL}" height="{YBR - YB}" fill="url(#rock)" opacity=".55"/>'
          f'<line x1="{XL}" y1="{YB}" x2="{XR}" y2="{YB}" stroke="#6b7280" stroke-width="2.5"/>')
    sea = [(XS, YSL)] + [(x, seabed(x)) for x in xsea] + [(XR, YSL)]
    g.add(f'<polygon points="{poly(sea)}" fill="url(#seag)" opacity=".92"/>')
    waves = ' '.join(f'q {9 if k % 2 == 0 else 9},{-6 if k % 2 == 0 else 6} 18,0' for k in range(12))
    g.add(f'<path d="M{XS + 8},{YSL - 3} {waves}" fill="none" stroke="#2a78d6" stroke-width="2.5"/>')
    # land surface, water table, mixing zone and interface
    g.add(f'<polyline points="{poly([(x, land(x)) for x in xs])}" fill="none" stroke="#7a5a2a" stroke-width="3"/>')
    g.add(f'<polyline points="{poly([(x, wt(x)) for x in xs])}" fill="none" stroke="#1b5fae" stroke-width="3" stroke-dasharray="10 6"/>')
    ipts = poly([(x, iface(x)) for x in xi if x >= XT])
    g.add(f'<polyline points="{ipts}" fill="none" stroke="#9b7fd0" stroke-width="26" stroke-opacity=".38" stroke-linejoin="round"/>')
    g.add(f'<polyline points="{ipts}" fill="none" stroke="#5d35a3" stroke-width="2.5" stroke-dasharray="6 5"/>')
    # heterogeneity lenses
    g.add('<ellipse cx="150" cy="430" rx="72" ry="14" fill="#c8a47e" opacity=".85"/>'
          '<ellipse cx="320" cy="352" rx="52" ry="11" fill="#9fb6c9" opacity=".9"/>')
    # rain
    for k in range(5):
        x0 = 150 + 18 * k
        g.add(f'<line x1="{x0}" y1="196" x2="{x0 - 6}" y2="212" stroke="#2a78d6" stroke-width="3" stroke-linecap="round"/>')

    # wells: casing from above ground to the bottom of the screen
    def well(x, top_screen, bot_screen, color, cap, w=12):
        yl = land(x)
        g.add(f'<rect x="{x - w / 2}" y="{yl - 18}" width="{w}" height="{top_screen - yl + 18}" fill="#ffffff" stroke="#4b5563" stroke-width="2.5"/>')
        g.add(f'<rect x="{x - w / 2}" y="{top_screen}" width="{w}" height="{bot_screen - top_screen}" fill="{color}" stroke="#4b5563" stroke-width="2.5"/>')
        for yy in np.arange(top_screen + 5, bot_screen - 2, 7):
            g.add(f'<line x1="{x - w / 2 + 2}" y1="{yy:.1f}" x2="{x + w / 2 - 2}" y2="{yy:.1f}" stroke="#ffffff" stroke-width="2"/>')
        g.add(f'<rect x="{x - 15}" y="{yl - 30}" width="30" height="14" rx="4" fill="{cap}" stroke="#ffffff" stroke-width="2"/>')
        return yl

    well(XP, 362, 386, '#8a93a0', '#5b6573', w=9)
    well(XW, 280, 322, blue[0], blue[1], w=16)
    well(XC, 336, 372, amber[0], amber[1], w=10)
    well(XM, 280, 318, green[0], green[1], w=14)
    # pumping arrows into the supply screen, upconing, recharge arrows
    g.arrow(f'M{XW - 44},356 L{XW - 14},322', blue[0], 4.5)
    g.arrow(f'M{XW + 44},356 L{XW + 14},322', blue[0], 4.5)
    g.arrow(f'M{XW},{iface(XW) - 14:.0f} V{336}', '#c0392b', 4, dash='8 6')
    g.arrow(f'M{XM - 12},300 H{XM - 62}', green[0], 4.5)
    g.arrow(f'M{XM + 12},300 H{XM + 62}', green[0], 4.5)
    # fresh water to the sea, salt water inland at depth
    g.arrow(f'M80,318 C130,316 160,312 196,310', '#1b5fae', 4)
    g.arrow(f'M{XR - 30},527 H{XT + 150}', '#b42318', 4.5)
    # goal ring around the supply screen
    g.add(f'<rect x="{XW - 24}" y="272" width="48" height="58" rx="12" fill="none" stroke="#d23b33" stroke-width="3.5" stroke-dasharray="7 5"/>')

    # labels above ground
    O.append(ov(62, 190, tex.text('rain $R$'), 'lab', 'tl', style='font-size:17px'))
    O.append(ov(XP + 20, land(XP) - 23, tex.text('head $h$'), 'lab', 'cl', style='font-size:17px'))
    O.append(ov(XW, land(XW) - 34, tex.text('supply well, rate $q$'), 'lab', 'bc', style='font-size:17px'))
    O.append(ov(XC, land(XC) - 34, tex.text('chloride sensor'), 'lab', 'bc', style='font-size:17px'))
    O.append(ov(XM, land(XM) - 34, tex.text('recharge $r$'), 'lab', 'bc', style='font-size:17px'))
    O.append(ov(990, 232, tex.text('SEA'), 'lab', 'bc', style='font-size:19px;font-weight:800;color:#1b5fae;letter-spacing:2px'))
    # labels inside the aquifer
    O.append(ov(62, 278, tex.text('fresh water'), 'lab', 'tl', style='font-size:16.5px;font-style:italic;color:#1b5fae'))
    O.append(ov(XW - 30, 301, tex.text('goal $F$:') + '<br>' + tex.text('Cl > 250 mg/L?'), 'note', 'cr',
                style='font-size:15.5px;font-weight:700;color:#b42318;background:rgba(255,255,255,.93);border:2px solid #d23b33;'
                      'border-radius:10px;padding:2px 8px;line-height:1.2;text-align:center'))
    O.append(ov(XW + 12, 394, tex.text('upconing'), 'lab', 'cl', style='font-size:15.5px;color:#b42318'))
    O.append(ov(150, 450, tex.text('$K(x)$ ?'), 'lab', 'tc', style='font-size:16px;color:#9b2c5e'))
    O.append(ov(662, 446, tex.text('mixing zone, width $w$ ?'), 'lab', 'cl', style='font-size:16px;color:#5d35a3'))
    O.append(ov(700, 506, tex.text('salt water wedge'), 'lab', 'cc', style='font-size:17px;font-style:italic;color:#7a1f16'))
    O.append(ov(962, 296, tex.text('sea contact ?'), 'lab', 'tc', style='font-size:15.5px;color:#9b2c5e'))
    O.append(ov(962, 360, tex.eq('\\zeta=h/\\delta\\approx40\\,h'), 'eqlab', 'tc', style='font-size:18px'))
    O.append(ov(962, 404, tex.text('1 m of head holds'), 'cap', 'tc', style='font-size:14.5px;color:#3a4350'))
    O.append(ov(962, 424, tex.text('the salt 40 m down'), 'cap', 'tc', style='font-size:14.5px;color:#3a4350'))
    O.append(ov(XR - 6, 572, tex.text('schematic, not to scale'), 'cap', 'br', style='font-size:13px'))

    # ======== panel B: the goal is chemistry
    g.panel(1118, 136, 438, 442, 'THE GOAL IS CHEMISTRY', 'green', name='B')
    LX, BX0, BW = 1290, 1302, 196            # label right edge, bar start, bar width for the full scale
    O.append(ov(1136, 192, tex.text('risk at the two supply wells'), 'cap', 'tl', style='font-size:15.5px;font-weight:700;color:#3a4350'))
    sc = BW / 0.7

    def bar(y, v, col, txt, lab, w_scale):
        w = max(v * w_scale, 2)
        g.add(f'<rect x="{BX0}" y="{y - 10}" width="{w:.1f}" height="20" rx="4" fill="{col}"/>')
        O.append(ov(BX0 + w + 6, y, tex.text(txt), 'lab', 'cl', style='font-size:15.5px;font-weight:800'))
        O.append(ov(LX, y, tex.text(lab), 'note', 'cr', style='font-size:15px'))

    bar(234, N['p_proxy'], '#8a93a0', '%.3f' % N['p_proxy'], 'head $h<1$ m', sc)
    bar(262, N['p_chem'], '#d23b33', '%.3f' % N['p_chem'], 'Cl $>250$ mg/L', sc)
    O.append(ov(1136, 288, tex.text('with recharge 3 × 5,000 m³/d'), 'cap', 'tl', style='font-size:14.5px'))
    bar(326, N['p_rech_proxy'], '#8a93a0', '%.3f' % N['p_rech_proxy'], 'head $h<1$ m', sc)
    bar(354, N['p_rech_chem'], '#e4572e', '%.3f' % N['p_rech_chem'], 'Cl $>250$ mg/L', sc)
    xa = BX0 + 0.10 * sc
    for ya, yb in ((222, 274), (314, 366)):
        g.add(f'<line x1="{xa:.1f}" y1="{ya}" x2="{xa:.1f}" y2="{yb}" stroke="#1f3864" stroke-width="2" stroke-dasharray="5 4"/>')
    O.append(ov(xa, 368, tex.text('limit 10%'), 'cap', 'tc', style='font-size:13px;color:#1f3864;font-weight:700'))
    g.add('<line x1="1136" y1="388" x2="1538" y2="388" stroke="#e3e8ee" stroke-width="2"/>')
    O.append(ov(1136, 398, tex.text('pumping allowed at risk ≤ 10%, m³/d'), 'cap', 'tl', style='font-size:15.5px;font-weight:700;color:#3a4350'))
    sy = BW / 10000
    bar(440, N['y_none'], '#8a93a0', '{:,.0f}'.format(N['y_none']), 'no data', sy)
    bar(468, N['y_heads'], '#7d9cc4', '{:,.0f}'.format(N['y_heads']), 'best three heads', sy)
    bar(496, N['y_cl'], green[0], '{:,.0f}'.format(N['y_cl']), 'one chloride sample', sy)
    bar(524, N['y_two'], green[1], '{:,.0f}'.format(N['y_two']), 'best two samples', sy)
    O.append(ov(1337, 552, tex.text('head rule: %s m³/d, fails in %d%% of aquifers'
                                    % ('{:,.0f}'.format(N['y_proxy']), round(100 * N['f_proxy']))),
                'cap', 'tc', style='font-size:14px;color:#b42318'))

    # ======== panel C: the decision loop
    g.panel(32, 596, 1524, 230, 'THE DECISION LOOP · WHO DECIDES, WITH WHICH DATA, FOR WHICH GOAL', 'pink', name='C')
    nodes = [('STAKEHOLDERS', '5 beliefs $P_1,\\dots,P_5$', pink, '→ STAKEHOLDER DIAGRAM'),
             ('DECIDE', '$a=(q,\\,r,\\,\\xi,\\,\\tau)$', orange, '→ PARADIGM 3: ACT'),
             ('THE AQUIFER RESPONDS', 'unknown $\\theta$, event $F(a)$', purple, '→ PARADIGM 2: CAUSES'),
             ('MEASURE', '$y_\\xi$: heads, chloride, EC', amber, '→ PARADIGM 1: WHERE'),
             ('LEARN', '$p(\\theta\\mid y_\\xi)$ and $P_k(F\\mid y_\\xi)$', teal, '→ PARADIGM 4: VALUE')]
    NW, GAP, NX0, NY0, NH = 248, 56, 62, 676, 66
    for k, (name, line, col, tab) in enumerate(nodes):
        x0 = NX0 + k * (NW + GAP)
        cx = x0 + NW / 2
        g.add(f'<rect x="{x0}" y="{NY0}" width="{NW}" height="{NH}" rx="14" fill="{col[2]}" stroke="{col[0]}" stroke-width="2.5"/>')
        g.add(f'<rect x="{cx - 104}" y="{NY0 - 26}" width="208" height="22" rx="11" fill="{col[0]}"/>')
        g.text(cx, NY0 - 10, tab, size=12.5, weight=800, fill='#ffffff', anchor='middle', halo=False, ls=0.8)
        g.text(cx, NY0 + 22, name, size=15, weight=800, fill=col[1], anchor='middle', halo=False, ls=1.2)
        O.append(ov(cx, NY0 + 30, tex.text(line), 'note', 'tc', style='font-size:17.5px'))
        if k < 4:
            g.arrow(f'M{x0 + NW + 4},{NY0 + NH / 2} H{x0 + NW + GAP - 6}', '#5b6573', 5)
    xr0 = NX0 + 4 * (NW + GAP) + NW / 2
    xr1 = NX0 + 1 * (NW + GAP) + NW / 2
    g.arrow(f'M{xr0},{NY0 + NH + 2} V{NY0 + NH + 46} H{xr1} V{NY0 + NH + 8}', '#c2417a', 4.5, dash='10 7')
    O.append(ov((xr0 + xr1) / 2, NY0 + NH + 46,
                tex.text('decide again as data arrive, keeping $\\max_k P_k\\big(F(a)\\mid y_\\xi\\big)\\le\\alpha$ for every stakeholder'),
                'note', 'cc', style='font-size:16.5px;background:#ffffff;border:2px solid #c2417a;border-radius:12px;padding:2px 12px'))

    # badges -> cards
    for (x, y, n) in ((1072, 159, 1), (590, 498, 2), (1530, 159, 3), (78, 404, 4), (868, 204, 5), (1530, 412, 6),
                      (NX0 - 4, NY0 + NH / 2, 7), (1530, 619, 8)):
        g.badge(x, y, n, ORDER[n - 1])
    return g.svg(HERO_Y1), O


# ---------------------------------------------------------------- content
def innov(N):
    return dict(
        kicker='INNOVATION', name='One goal event, one rule for everyone',
        sub='The problem is stated on the event that matters, the drinking-water standard in the screen, and on every '
            'stakeholder’s belief, not on a head target and one model.',
        items=[
            dict(t='The problem in one line',
                 eqs=[r'\max_{a,\,\xi}\ \mathbb E\big[W(a)\big]\quad\text{s.t.}\quad\max_{k}\,P_k\big(F(a)\mid y_\xi\big)\le\alpha'],
                 x='$W$: water delivered minus the cost of recharge and data; $P_k$: the belief of stakeholder $k$; '
                   '$\\alpha=10\\%$. Pumping, recharge, monitoring and the alarm are chosen together, for one event.',
                 kv='≤ 10%', kc='RISK FOR EVERYONE'),
            dict(t='Chemistry, not head, and still linear',
                 eqs=[r'\{\mathrm{Cl}_w>250\}=\{\varphi_w<\varphi^{*}_w\},\quad \varphi_w(a)=\varphi^{0}_w+\textstyle\sum_j G_{wj}\,a_j'],
                 x='The potential is linear in every rate, so the chloride goal keeps the cheap structure of a head target, '
                   'with a random threshold. Same aquifers, same pumping: the head says %.3f, chloride %.3f; with recharge '
                   'the head says %.3f, chloride %.3f.' % (N['p_proxy'], N['p_chem'], N['p_rech_proxy'], N['p_rech_chem']),
                 kv='×%.1f' % (N['p_chem'] / N['p_proxy']), kc='RISK THE HEAD MISSES'),
            dict(t='Measure what the goal needs',
                 eqs=[r'I(F;\mathrm{Cl}_{\text{1 sample}})=%.3f\ \gg\ \max I(F;h_{1,2,3})=%.3f\ \text{nats}' % (N['eig_cl'], N['eig_heads'])],
                 x='One shallow chloride sample tells more about the event than any three heads. It doubles the pumping '
                   'allowed at 10%% risk, from %s to %s m³/d.' % ('{:,.0f}'.format(N['y_none']), '{:,.0f}'.format(N['y_cl'])),
                 kv='×%.1f' % (N['y_cl'] / N['y_none']), kc='SAFE PUMPING'),
        ],
        foot='Test bed: %s draws of a calibrated coastal-aquifer model, two supply wells, each pumped to a 50%% own risk. '
             'The diagrams that follow answer the questions this one raises.' % '{:,}'.format(N['n']))


def cards(N):
    f0 = '{:,.0f}'.format
    return [
        dict(t='Flow: fresh water floats on the sea', color='blue',
             idea='Fresh water flows to the sea above denser sea water. Pressure and density together drive the flow.',
             eqs=[r'q=-\frac{k}{\mu}\big(\nabla p+\rho g\,\nabla z\big),\qquad \frac{\partial(n\rho)}{\partial t}+\nabla\cdot(\rho\,q)=\rho\,Q',
                  r'\zeta=\frac{h}{\delta},\qquad \delta=\frac{\rho_s-\rho_f}{\rho_f}\approx0.025\ \Rightarrow\ \zeta\approx40\,h'],
             pill='WHY IT IS HARD',
             land='Density couples flow to salt. One metre of fresh head at the coast holds the interface about 40 m down, '
                  'so a small drawdown near a well lets the salt rise beneath the screen (upconing). The response is '
                  'nonlinear and slow.'),
        dict(t='Salt: transport and mixing', color='purple',
             idea='Salt moves with the water and spreads by dispersion: the mixing zone reaches the screen first.',
             eqs=[r'\frac{\partial(nC)}{\partial t}+\nabla\cdot(q\,C)-\nabla\cdot(n\,\mathbf D\,\nabla C)=Q\,C_{\mathrm{in}}',
                  r'\mathbf D=\alpha_T|v|\,\mathbf I+(\alpha_L-\alpha_T)\frac{v\,v^{\top}}{|v|}+D_m\mathbf I'],
             pill='TEST BED',
             land='Chloride passes 250 mg/L at 1.09% sea water, sodium only at 1.50%. The sea contact is uncertain too: '
                  'the intruded area at the prior mean is 92.7 km² with the whole shoreline open, 10.1 km² with the '
                  'mapped contact.'),
        dict(t='The goal is chemistry in the screen', color='green',
             idea='The event that matters is the drinking-water standard in the well screen. Chloride there falls as the '
                  'potential rises, so the event is a threshold.',
             eqs=[r'F(a)=\{\mathrm{Cl}_w(a)>250\ \mathrm{mg/L}\}=\{\varphi_w(a)<\varphi^{*}_w\}',
                  r'\mathrm{Cl}_w=\mathrm{Cl}_f+\bar c_w(\mathrm{Cl}_s-\mathrm{Cl}_f),\qquad c(z)=\Phi\Big(\frac{z-\zeta}{w}\Big)'],
             pill='TEST BED',
             land='With each well pumped to a 50%% own risk, $P(h<1\\,\\mathrm m)=%.3f$ but $P(\\mathrm{Cl}>250)=%.3f$. The '
                  'threshold $\\varphi^{*}$ follows the width of the mixing zone (rank correlation %.5f), not the potential at '
                  'the well (%.3f).' % (N['p_proxy'], N['p_chem'], N['corr_w'], N['corr_phi'])),
        dict(t='What we do not know', color='teal',
             idea='Parameters, boundaries, the weather to come and the people who pump: each is uncertain, and only some '
                  'can be measured.',
             eqs=[r'\theta=\big(\log K(x),\,R,\,w,\,B,\,\mathrm{Cl}_s,\ \text{sea contact}\big)\sim p(\theta)',
                  r'\omega_i\propto p(d_{\mathrm{obs}}\mid\theta_i),\qquad \mathrm{ESS}=\frac{(\sum_i\omega_i)^2}{\sum_i\omega_i^2}'],
             pill='TEST BED',
             land='%s prior aquifers weighted by the documented facts keep an effective 3,249: the facts narrow the '
                  'uncertainty but do not remove it. Beyond the parameters: wet and dry years, and pumping that departs '
                  'from the plan.' % '{:,}'.format(N['n'])),
        dict(t='The decisions', color='orange',
             idea='Four levers: how much to pump and where, where to recharge, where to measure, and when to raise the alarm.',
             eqs=[r'a=\big(q_1,\dots,q_m;\ r_1,\dots,r_n;\ \xi;\ \tau\big)',
                  r'q^{\max}(y_\xi)=\max\big\{q:\ P\big(F(q)\mid y_\xi\big)\le\alpha\big\}'],
             pill='TEST BED',
             land='Recharge of 3 × 5,000 m³/d at sites chosen for chemistry lowers the risk from %.3f to %.3f (%.3f at '
                  'sites chosen for the head, where the head itself reports %.3f). Reaching 10%% needs %s m³/d per site.'
                  % (N['p_chem'], N['p_rech_chem'], N['p_rech_proxy_sites'], N['p_rech_proxy_own'], f0(N['q_needed']))),
        dict(t='Which data inform the goal', color='amber',
             idea='A measurement is worth what it tells about the event $F$ (entropy $H(F)=%.3f$ nats), not about the '
                  'parameters in general.' % N['H'],
             eqs=[r'\mathrm{EIG}(\xi)=I(F;y_\xi)=H(F)-\mathbb E_{y_\xi}\big[H(F\mid y_\xi)\big]',
                  r'I(F;\mathrm{Cl}_1)=%.3f\quad\text{vs}\quad I(F;h_{1,2,3})\le%.3f' % (N['eig_cl'], N['eig_heads'])],
             pill='TEST BED',
             land='Pumping allowed at 10%% posterior risk (20 m screens): %s m³/d without data, %s with the best three heads, '
                  '%s with one chloride sample, %s with the best two. The head rule pumps %s and fails the standard in %d%% '
                  'of aquifers.' % (f0(N['y_none']), f0(N['y_heads']), f0(N['y_cl']), f0(N['y_two']), f0(N['y_proxy']),
                                    round(100 * N['f_proxy']))),
        dict(t='Stakeholders: one aquifer, five beliefs', color='pink',
             idea='Utility, irrigators and hotels, municipality, water agency, environmental groups: one aquifer, five '
                  'beliefs.',
             eqs=[r'p_k(\theta\mid y)\ \propto\ p(\theta\mid y)\,e^{\lambda_k^{\top}z(\theta)}',
                  r'a\ \text{acceptable}\iff\max_k P_k\big(F(a)\mid y_\xi\big)\le\alpha'],
             pill='TEST BED',
             land='The same plan carries a risk of 0.37 for the utility, 0.15 for irrigators and hotels, 0.43 for the '
                  'municipality, 0.57 for the agency and 0.63 for environmental groups. At half the pumping, one chloride '
                  'sample cuts the disagreement from 0.224 to 0.038.'),
        dict(t='This series: one question per diagram', color='brown',
             idea='Each step of the loop is a machine-learning question with its own diagram.',
             eqs=[r'\xi\ \to\ y_\xi\ \to\ p(\theta\mid y_\xi)\ \to\ a\ \to\ F(a)',
                  r'a_{t+1}=\pi\big(p(\theta\mid y_{1:t})\big),\quad \max_k P_k(F)\le\alpha'],
             pill='IN THIS SERIES',
             land='**1** Robust design: where to measure when the noise model is uncertain. **2** Causal models: which process '
                  'made the salt. **3** Deep RL: how many years of data a pumping policy needs. **4** Value of data without a '
                  'prior. **Stakeholders**: a choice nobody can veto.'),
    ]


def build():
    N = numbers()
    tex = Tex()
    svg, overlays = hero(tex, N)
    html = build_page(tex, kicker='INTRODUCTION  ·  THE PROBLEM THE SERIES ANSWERS',
                      title='The problem: a safe coastal water supply under deep uncertainty',
                      tags=[('CLASSICAL', 'one model · a head target · decide, then measure'),
                            ('NEW', 'the chloride standard · every belief · decide and measure together')],
                      hero_svg=svg, overlays=overlays, hero_y1=HERO_Y1, innov=innov(N), innov_box=(1584, 132, 784, 694),
                      cards=cards(N), card_top=HERO_Y1 + 12, card_h=408, card_gap=12)
    open('d0_problem_statement.html', 'w').write(html)
    print('wrote d0_problem_statement.html')
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in N.items()})


if __name__ == '__main__':
    build()
