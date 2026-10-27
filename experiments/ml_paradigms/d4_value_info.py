"""Diagram 4 of 4: the value of information without a prior (learning what data are worth).
Two pictures in the schematic are computed illustrations: (a) the worst-case regret of three rules in a two-action problem
(act: welfare theta, do not act: 0, theta in [-1, 1], n = 10 samples of N(theta, 1)); (d) a simulated e-process alarm with
a predictable plug-in alternative (mean of the last 20 readings, clipped at 0), N(0, 1) readings whose mean shifts by
0.6 after month 120, threshold log(1/alpha) with alpha = 0.001, and a Monte Carlo of its false-alarm rate and delay."""
import numpy as np
from scipy.stats import norm

from ml_common import PAL, ORDER, INK, MUTED, Svg, Tex, ov, build_page

HERO_Y1 = 842
SIG, NS = 1.0, 10                 # regret picture: noise sd and number of samples
ALPHA, SHIFT, T_CHANGE, T_END, WIN = 1e-3, 0.6, 120, 240, 20


# ---------------------------------------------------------------- computations
def regret_curves():
    th = np.linspace(-1, 1, 801)
    r_never = np.maximum(th, 0)
    r_half = np.abs(th) / 2
    r_thr = np.abs(th) * norm.cdf(-np.abs(th) * np.sqrt(NS) / SIG)
    w_thr = th * norm.cdf(th * np.sqrt(NS) / SIG)                       # welfare of the threshold rule (maxmin view)
    return th, r_never, r_half, r_thr, w_thr.min()


def eprocess_batch(Y):
    M, T = Y.shape
    c = np.concatenate([np.zeros((M, 1)), np.cumsum(Y, 1)], 1)
    t = np.arange(T)
    lo = np.maximum(0, t - WIN)
    mu = np.where(t > 0, (c[:, t] - c[:, lo]) / np.maximum(t - lo, 1), 0.0)
    mu = np.maximum(mu, 0.0)                                            # predictable: uses readings before month t only
    inc = mu * Y - mu ** 2 / 2                                          # log of N(mu,1)/N(0,1) at Y_t
    return np.concatenate([np.zeros((M, 1)), np.cumsum(inc, 1)], 1)


def eprocess():
    rng = np.random.default_rng(1)
    y = rng.standard_normal(T_END)
    y[T_CHANGE:] += SHIFT
    path = eprocess_batch(y[None, :])[0]
    thr = np.log(1 / ALPHA)
    alarm = int(np.argmax(path >= thr))
    rng = np.random.default_rng(2026)
    L0 = eprocess_batch(rng.standard_normal((20000, T_END)))
    fa = int((L0.max(1) >= thr).sum())
    Y1 = rng.standard_normal((5000, T_END)); Y1[:, T_CHANGE:] += SHIFT
    hit = eprocess_batch(Y1) >= thr
    first = np.where(hit.any(1), hit.argmax(1), 10 ** 6)
    delay = first[(first > T_CHANGE) & (first <= T_END)] - T_CHANGE
    return dict(path=path, thr=thr, alarm=alarm, fa=fa, n0=20000, med=float(np.median(delay)),
                det=float((first <= T_END).mean()))


# ---------------------------------------------------------------- the schematic
def hero(tex, rc, ep):
    g = Svg()
    O = []
    blue, purple, green, teal, orange, amber, pink, brown = (PAL[c] for c in ORDER)
    # ---- the decision pipeline and the two routes
    g.panel(32, 136, 1524, 268, 'THE DECISION PIPELINE', 'blue', name='P')
    nodes = [('EXPERIMENT', '$\\boldsymbol\\xi$: which sensors'), ('DATA', '$X_{\\xi}\\sim P_{\\theta,\\xi}$'),
             ('RULE', '$\\delta(X)$, may randomise'), ('ACTION', '$a$: e.g. a pumping rate'),
             ('WELFARE', '$W(a,\\theta)$')]
    for k, (name, line) in enumerate(nodes):
        cx = 175 + 300 * k
        g.add(f'<rect x="{cx - 115}" y="194" width="230" height="74" rx="14" fill="{blue[2]}" stroke="{blue[0]}" stroke-width="2.5"/>')
        g.text(cx, 216, name, size=16, weight=800, fill=blue[1], anchor='middle', halo=False, ls=1.4)
        O.append(ov(cx, 226, tex.text(line), 'note', 'tc', style='font-size:18.5px'))
        if k < 4:
            g.arrow(f'M{cx + 117},231 H{cx + 181}', blue[0], 6)
    g.add(f'<rect x="835" y="279" width="180" height="34" rx="17" fill="{pink[2]}" stroke="{pink[0]}" stroke-width="2.5"/>')
    O.append(ov(925, 296, tex.text('unknown state $\\theta$'), 'note', 'cc', style='font-size:17px;font-weight:700;color:#9b2c5e'))
    g.arrow('M835,296 C700,296 520,300 475,272', pink[0], 3.5, dash='9 7')
    g.arrow('M1015,296 C1150,296 1330,300 1375,272', pink[0], 3.5, dash='9 7')
    g.add('<rect x="52" y="324" width="720" height="66" rx="12" fill="#f4f5f7" stroke="#c4cad3" stroke-width="2"/>')
    g.text(68, 344, 'BAYESIAN ROUTE · AVERAGE OVER ONE PRIOR π', size=14, weight=800, fill='#5b6573', halo=False, ls=1)
    O.append(ov(412, 350, tex.eq('\\mathrm{VOI}_B(E)=\\mathbb E_\\pi\\big[\\max_a\\mathbb E[u(a,\\theta)\\mid X]\\big]-\\max_a\\mathbb E_\\pi[u(a,\\theta)]'),
                'eqbare', 'tc', style='font-size:19.5px'))
    g.add(f'<rect x="790" y="324" width="746" height="66" rx="12" fill="#ffffff" stroke="{blue[0]}" stroke-width="2.5"/>')
    g.text(806, 344, 'PRIOR-FREE ROUTES · JUDGE THE RULE AT EVERY θ', size=14, weight=800, fill=blue[1], halo=False, ls=1)
    O.append(ov(1163, 350, tex.eq('R(\\delta,\\theta)=\\mathbb E_\\theta[L(\\delta(X),\\theta)],\\quad \\mathrm{Reg}(\\delta,\\theta)=\\max_a u(a,\\theta)-\\mathbb E_\\theta[u(\\delta(X),\\theta)]'),
                'eqbare', 'tc', style='font-size:19.5px'))

    # ---- (a) Wald: worst-case regret (computed)
    th, r_never, r_half, r_thr, wmin = rc
    g.panel(32, 420, 430, 406, 'WALD: WORST-CASE REGRET', 'green', name='A')
    O.append(ov(247, 474, tex.text('illustration: act (welfare $\\theta$) or not (0), $\\theta\\in[-1,1]$'), 'cap', 'tc', style='font-size:15.5px'))
    X0, X1, Y0, Y1 = 92, 440, 506, 650

    def xy(t, r):
        return X0 + (t + 1) / 2 * (X1 - X0), Y1 - r / 1.05 * (Y1 - Y0)
    g.add(f'<line x1="{X0}" y1="{Y1}" x2="{X1}" y2="{Y1}" stroke="#9aa3ad" stroke-width="2"/>'
          f'<line x1="{X0}" y1="{Y0 - 4}" x2="{X0}" y2="{Y1}" stroke="#9aa3ad" stroke-width="2"/>'
          f'<line x1="{(X0 + X1) / 2}" y1="{Y0}" x2="{(X0 + X1) / 2}" y2="{Y1}" stroke="#d0d7de" stroke-width="1.5" stroke-dasharray="4 4"/>')
    for v in (0.5, 1.0):
        yy = xy(0, v)[1]
        g.add(f'<line x1="{X0}" y1="{yy:.1f}" x2="{X1}" y2="{yy:.1f}" stroke="#e3e8ee" stroke-width="1.2"/>')
        g.text(X0 - 8, yy + 5, f'{v:.1f}', size=14, weight=500, fill=MUTED, anchor='end', halo=False)
    g.text(X0 - 8, Y1 + 5, '0', size=14, weight=500, fill=MUTED, anchor='end', halo=False)
    for t in (-1, 0, 1):
        g.text(xy(t, 0)[0], Y1 + 20, str(t), size=14, weight=500, fill=MUTED, anchor='middle', halo=False)
    O.append(ov(X1, Y1 + 24, tex.eq('\\theta'), 'eqbare', 'tr', style='font-size:17px'))
    O.append(ov(X0 + 6, Y0 - 6, tex.text('regret'), 'cap', 'tl', style='font-size:14px'))
    cols = ('#8a93a0', purple[0], green[1])
    for r, ccol, dash in ((r_never, cols[0], '8 6'), (r_half, cols[1], None), (r_thr, cols[2], None)):
        pts = ' '.join('%.1f,%.1f' % xy(t, v) for t, v in zip(th, r))
        da = f' stroke-dasharray="{dash}"' if dash else ''
        g.add(f'<polyline points="{pts}" fill="none" stroke="{ccol}" stroke-width="4" stroke-linejoin="round"{da}/>')
    for r, ccol in ((r_never, cols[0]), (r_half, cols[1]), (r_thr, cols[2])):
        i = int(np.argmax(r))
        px, py = xy(th[i], r[i])
        g.add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="7" fill="#ffffff" stroke="{ccol}" stroke-width="3.5"/>')
    legend = [(cols[0], '8 6', 'no data, never act: max regret %.2f' % r_never.max()),
              (cols[1], None, 'no data, act with prob. ½: max %.2f' % r_half.max()),
              (cols[2], None, '$n=%d$, act if $\\bar X\\ge0$: max %.3f' % (NS, r_thr.max()))]
    for k, (ccol, dash, s) in enumerate(legend):
        yy = 688 + 23 * k
        da = f' stroke-dasharray="{dash}"' if dash else ''
        g.add(f'<line x1="58" y1="{yy}" x2="92" y2="{yy}" stroke="{ccol}" stroke-width="4"{da}/>')
        O.append(ov(102, yy, tex.text(s), 'note', 'cl', style='font-size:16px'))
    O.append(ov(247, 752, tex.eq('\\mathrm{VOI}_{\\mathrm{MMR}}=%.2f-%.3f=%.2f' % (r_half.max(), r_thr.max(), r_half.max() - r_thr.max())),
                'eqlab', 'tc', style='font-size:18px'))
    O.append(ov(247, 794, tex.text('maxmin welfare: never act, data worth 0'), 'note', 'tc', style='font-size:15px;color:#5b6573'))

    # ---- (b) Blackwell order
    g.panel(480, 420, 290, 406, 'BLACKWELL', 'purple', name='B')
    cx = 625
    g.add(f'<rect x="{cx - 100}" y="482" width="200" height="50" rx="12" fill="{purple[2]}" stroke="{purple[0]}" stroke-width="2.5"/>')
    O.append(ov(cx, 507, tex.text('experiment $E$: $P_\\theta$'), 'note', 'cc', style='font-size:18px'))
    g.arrow(f'M{cx},534 V560', purple[0], 5)
    K = np.array([[.7, .2, .1, 0], [.15, .6, .2, .05], [.05, .2, .6, .15], [0, .1, .25, .65]])
    for i in range(4):
        for j in range(4):
            g.add(f'<rect x="{cx - 46 + j * 23}" y="{566 + i * 23}" width="21" height="21" rx="3" fill="{purple[0]}" '
                  f'fill-opacity="{0.08 + 0.92 * K[i, j]:.2f}"/>')
    O.append(ov(cx + 58, 612, tex.text('garbling'), 'cap', 'cl', style='font-size:15px'))
    O.append(ov(cx - 58, 612, tex.eq('K'), 'eqbare', 'cr', style='font-size:21px'))
    g.arrow(f'M{cx},662 V686', purple[0], 5)
    g.add(f'<rect x="{cx - 100}" y="690" width="200" height="44" rx="12" fill="#ffffff" stroke="{purple[0]}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    O.append(ov(cx, 712, tex.text('$F$: $Q_\\theta=K\\,P_\\theta$'), 'note', 'cc', style='font-size:18px'))
    O.append(ov(cx, 744, tex.text('$F$ is worse for every prior'), 'note', 'tc', style='font-size:15.5px'))
    O.append(ov(cx, 770, tex.text('and every decision problem'), 'note', 'tc', style='font-size:15.5px'))
    O.append(ov(cx, 798, tex.text('large samples: Rényi order'), 'cap', 'tc', style='font-size:15px'))

    # ---- (c) ambiguity: a KL ball of models around the estimate
    g.panel(788, 420, 290, 406, 'AMBIGUITY', 'orange', name='C')
    cx, cy, rr = 933, 584, 100
    g.add(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="{orange[2]}" stroke="{orange[0]}" stroke-width="3" stroke-dasharray="10 6"/>')
    rng = np.random.default_rng(4)
    for _ in range(16):
        a, rad = rng.uniform(0, 2 * np.pi), rr * np.sqrt(rng.uniform(0.08, 0.85))
        g.add(f'<circle cx="{cx + rad * np.cos(a):.1f}" cy="{cy + rad * np.sin(a):.1f}" r="4.5" fill="#9aa3ad"/>')
    g.add(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{orange[1]}"/>')
    O.append(ov(cx + 10, cy - 8, tex.eq('\\hat P'), 'eqbare', 'bl', style='font-size:20px'))
    qa = np.deg2rad(38)
    qx, qy = cx + rr * np.cos(qa), cy + rr * np.sin(qa)
    g.add(f'<circle cx="{qx:.1f}" cy="{qy:.1f}" r="9" fill="#d23b33" stroke="#ffffff" stroke-width="2.5"/>')
    O.append(ov(qx - 12, qy + 12, tex.text('worst case'), 'lab', 'tr', style='font-size:15px;font-weight:700;color:#b42318'))
    g.add(f'<line x1="{cx}" y1="{cy}" x2="{cx - rr * 0.94:.1f}" y2="{cy - rr * 0.34:.1f}" stroke="{orange[1]}" stroke-width="2.5"/>')
    O.append(ov(cx - 52, cy - 32, tex.eq('r'), 'eqbare', 'bc', style='font-size:19px'))
    O.append(ov(cx, 712, tex.eq('\\sup_{P:\\ \\mathrm{KL}(\\hat P,P)\\le r}c(x,P)'), 'eqlab', 'tc', style='font-size:18px'))
    O.append(ov(cx, 770, tex.text('decide against every model'), 'note', 'tc', style='font-size:15.5px'))
    O.append(ov(cx, 796, tex.text('in the ball, or a set of priors'), 'note', 'tc', style='font-size:15.5px'))

    # ---- (d) anytime-valid alarm (simulated e-process)
    g.panel(1096, 420, 460, 406, 'ANYTIME-VALID ALARM', 'brown', name='D')
    X0, X1, Y0, Y1 = 1146, 1530, 482, 672
    lo, hi = -3.0, 12.0

    def ez(t, v):
        return X0 + t / T_END * (X1 - X0), Y1 - (v - lo) / (hi - lo) * (Y1 - Y0)
    g.add(f'<line x1="{X0}" y1="{Y1}" x2="{X1}" y2="{Y1}" stroke="#9aa3ad" stroke-width="2"/>'
          f'<line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1}" stroke="#9aa3ad" stroke-width="2"/>')
    y0 = ez(0, 0)[1]
    g.add(f'<line x1="{X0}" y1="{y0:.1f}" x2="{X1}" y2="{y0:.1f}" stroke="#e3e8ee" stroke-width="1.5"/>')
    g.text(X0 - 8, y0 + 5, '0', size=14, weight=500, fill=MUTED, anchor='end', halo=False)
    ythr = ez(0, ep['thr'])[1]
    g.add(f'<line x1="{X0}" y1="{ythr:.1f}" x2="{X1}" y2="{ythr:.1f}" stroke="#d23b33" stroke-width="2.5" stroke-dasharray="10 6"/>')
    O.append(ov(X0 + 8, ythr + 5, tex.text('threshold $\\log(1/\\alpha)$'), 'note', 'tl', style='font-size:15px;color:#b42318;font-weight:700'))
    xc = ez(T_CHANGE, 0)[0]
    g.add(f'<line x1="{xc:.1f}" y1="{Y0}" x2="{xc:.1f}" y2="{Y1}" stroke="#8a93a0" stroke-width="2" stroke-dasharray="5 5"/>')
    O.append(ov(xc + 6, Y1 - 6, tex.text('shift'), 'cap', 'bl', style='font-size:14px'))
    pts = ' '.join('%.1f,%.1f' % ez(t, v) for t, v in enumerate(ep['path']))
    g.add(f'<polyline points="{pts}" fill="none" stroke="{brown[0]}" stroke-width="3.5" stroke-linejoin="round"/>')
    ax_, ay_ = ez(ep['alarm'], ep['path'][ep['alarm']])
    g.add(f'<circle cx="{ax_:.1f}" cy="{ay_:.1f}" r="9" fill="#d23b33" stroke="#ffffff" stroke-width="3"/>')
    O.append(ov(ax_ - 12, ay_ - 12, tex.text('alarm, month %d' % ep['alarm']), 'note', 'br', style='font-size:15px;font-weight:700;color:#b42318'))
    for t in (0, 120, 240):
        g.text(ez(t, 0)[0], Y1 + 19, str(t), size=14, weight=500, fill=MUTED, anchor='middle', halo=False)
    O.append(ov(X1, Y1 + 24, tex.text('months'), 'cap', 'tr', style='font-size:14px'))
    O.append(ov(1326, 700, tex.eq('E_t=\\prod_{s\\le t}\\frac{\\hat q_s(Y_s\\mid Y_{1:s-1})}{p_0(Y_s\\mid Y_{1:s-1})}'), 'eqlab', 'tc', style='font-size:18px'))
    O.append(ov(1326, 760, tex.text('simulated: readings N(0,1), mean +0.6 after month %d' % T_CHANGE), 'cap', 'tc', style='font-size:14.5px'))
    O.append(ov(1326, 782, tex.text('null, $\\alpha=0.001$: %d of %s paths alarmed (%.2f%%)' % (ep['fa'], f"{ep['n0']:,}", 100 * ep['fa'] / ep['n0'])), 'cap', 'tc', style='font-size:14.5px'))
    O.append(ov(1326, 804, tex.text('after the shift: median delay %d months' % ep['med']), 'cap', 'tc', style='font-size:14.5px'))
    # ---- badges -> cards
    for (x, y, n) in ((1530, 159, 1), (744, 443, 2), (436, 443, 3), (886, 196, 4), (1052, 443, 5), (288, 268, 6),
                      (1046, 500, 7), (1530, 443, 8)):
        g.badge(x, y, n, ORDER[n - 1])
    return g.svg(HERO_Y1), O


# ---------------------------------------------------------------- content
def innov(ep):
    return dict(
        kicker='INNOVATION', name='Prior-free network value and alarm',
        sub='A proposal: a network’s value without a prior, and an alarm valid at any time.',
        items=[
            dict(t='What a network is worth, without a prior',
                 eqs=[r'\mathrm{VOI}_{\mathrm{MMR}}(\xi)=\min_a\max_{\theta\in\Theta_0}\mathrm{Reg}(a,\theta)-\min_\delta\max_{\theta\in\Theta_0}\mathrm{Reg}_\xi(\delta,\theta)'],
                 x='$\\Theta_0$: parameters consistent with the data; $W$: pumping benefit minus a chloride penalty. A subset of '
                   'sensors is a garbling of the full set, so adding a sensor never lowers the value.',
                 kv='monotone', kc='IN BLACKWELL ORDER'),
            dict(t='The criterion is not neutral',
                 eqs=[r'\mathrm{VOI}_{\mathrm{maxmin}}=0\qquad\text{but}\qquad\mathrm{VOI}_{\mathrm{MMR}}>0'],
                 x='If heads identify only $R/K$ (recharge over conductivity), maxmin gives them zero value and minimax regret a '
                   'positive one, with a fractional rule (proved in the Gaussian case, to be proved here). Salt gradients, temperature '
                   'and spring flow break the partial identification and gain value.',
                 kv='0 vs >0', kc='MAXMIN vs REGRET'),
            dict(t='One divergence for the alarm, the design and the cost',
                 eqs=[r'\xi^\star=\arg\max_{\mathrm{cost}(\xi)\le B}\ \min_{Q\in\mathcal H_1}D_{\mathrm{KL}}\big(Q_\xi\,\|\,P_{0,\xi}\big)'],
                 x='Under the null, $E_t$ passes $1/\\alpha$ with probability at most $\\alpha$ whenever checked. It grows at rate '
                   '$D_{\\mathrm{KL}}(Q_\\xi\\|P_{0,\\xi})$, the prior-free cost of information: put sentinels where it grows fastest.',
                 kv='%.2f%%' % (100 * ep['fa'] / ep['n0']), kc='SIMULATED, α = 0.1%'),
        ],
        foot='Open: the worst case by ensembles or surrogates, nonlinear flow, seasonal composite nulls.')


CARDS = [
    dict(t='Bayesian value, risk and regret', color='blue',
         idea='The classical value of information averages over one prior. Without a prior, judge how a rule behaves when the '
              'experiment is repeated with $\\theta$ fixed.',
         eqs=[r'\mathrm{VOI}_B(E)=\mathbb E_\pi\big[\max_a\mathbb E[u(a,\theta)\mid X]\big]-\max_a\mathbb E_\pi[u(a,\theta)]',
              r'\mathrm{Reg}(\delta,\theta)=\max_a u(a,\theta)-\mathbb E_\theta\big[u(\delta(X),\theta)\big]'],
         land='Five prior-free ways to summarise the risk function organise the field: Blackwell dominance, Wald’s maxmin and '
              'minimax regret, sets of priors and ambiguity, minimax learning bounds, and data quality with anytime-valid evidence.'),
    dict(t='Comparing experiments', color='purple',
         idea='Without a prior, $E$ beats $F$ for every prior and every decision exactly when $F$ is a garbling of $E$.',
         eqs=[r'Q_\theta=K\,P_\theta\ \ \forall\theta\quad\Longleftrightarrow\quad E\succcurlyeq F',
              r'C(\mu)=\textstyle\sum_{i,j}\beta_{ij}\,D_{\mathrm{KL}}(\mu_i\,\|\,\mu_j)'],
         land='In large samples Blackwell dominance equals dominance in every Rényi divergence (Mu, Pomatto, Strack & Tamuz '
              '2021); robust to side information it is “reveal or refine” (Brooks, Frankel & Kamenica 2024); the prior-free cost of '
              'information is a sum of KL divergences (Pomatto, Strack & Tamuz 2023).'),
    dict(t='Wald: maxmin or minimax regret', color='green',
         idea='The value of data is the drop of the worst-case regret; maxmin can give data zero value.',
         eqs=[r'\mathrm{VOI}_{\mathrm{MMR}}(E)=\min_a\max_\theta\mathrm{Reg}(a,\theta)-\min_\delta\max_\theta\mathrm{Reg}(\delta,\theta)',
              r'R(d,\theta)=U(\theta)\big\{\mathbf 1\{U(\theta)\ge0\}-\mathbb E_{m(\theta)}[d(Y)]\big\}'],
         land='Judge rules by maximum regret (Manski 2021); under partial identification maxmin ignores the data and minimax '
              'regret randomises (Montiel Olea, Qiu & Stoye, REStud, accepted); regret $\\sqrt{K/n}$ for quantile targets (Kock, '
              'Preinerstorfer & Veliyev 2023); policy learning at $\\sqrt{S_P\\mathrm{VC}(\\Pi)/n}$ (Athey & Wager 2021).'),
    dict(t='Experimenting for an audience', color='teal',
         idea='Readers hold different priors. Randomisation protects the reader with the worst prior; reports should let every '
              'reader update.',
         eqs=[r'\max_{\varrho,\alpha}\ \lambda\,\mathbb E_{h_0}[u]+(1-\lambda)\min_{h\in H}\mathbb E_{h}[u]',
              r'\Delta=\Sigma_{c\gamma}\Sigma_{\gamma\gamma}^{-1}\Sigma_{\gamma c}/\sigma_c^2,\qquad b_{RN}/b_N=\sqrt{1-\Delta}'],
         land='Randomised trials lose only about $\\sqrt{1/N}$ under every prior (Banerjee, Chassang, Montero & Snowberg 2020); '
              'communication versus decision risk (Andrews & Shapiro 2021); the informativeness $\\Delta$ of descriptive statistics '
              '(Andrews, Gentzkow & Shapiro 2020).'),
    dict(t='Ambiguity and misspecification', color='orange',
         idea='Replace one prior by a set of models, or by a penalty for leaving them (maxmin, robust control).',
         eqs=[r'V_Q(f)=\min_{p\in\Delta}\Big\{\textstyle\int u(f)\,dp+\min_{q\in Q}c(p,q)\Big\}',
              r'c=\lambda R:\quad V_Q(f)=\min_{q\in Q}\Big(-\lambda\log\textstyle\int e^{-u(f)/\lambda}\,dq\Big)'],
         land='Robust persuasion (Dworczak & Pavan 2022); Wald’s stopping with ambiguity (Auster, Che & Mierendorff 2024);'
              ' misspecified learners (Frick, Iijima & Ishii 2024); misspecification aversion (Cerreia-Vioglio, Hansen, '
              'Maccheroni & Marinacci 2026).'),
    dict(t='Interactive learning', color='amber',
         idea='Experiments chosen from past data: regret is bounded by how well the data tell models apart ($D_H$: Hellinger).',
         eqs=[r'\mathrm{dec}_\varepsilon=\inf_p\sup_{M}\big\{\mathbb E_p[f^M(\pi^M)-f^M(\pi)]:\,\mathbb E_p[D_H^2]\le\varepsilon^2\big\}',
              r'\mu_t=\arg\min_{\mu}\ \hat\Delta_t(\mu)^2/I_t(\mu)'],
         land='Lower and upper regret bounds that match up to the estimation error (Foster, Golowich & Han 2023); frequentist '
              'information-directed sampling, regret $O(\\sqrt n)$ or $O(n^{2/3})$ (Kirschner, Lattimore & Krause 2023).'),
    dict(t='Distributional robustness', color='pink',
         idea='Guard the decision against every distribution near the data; the radius buys a guarantee out of sample.',
         eqs=[r'\hat c_r(x,\hat P_T)=\sup_{P}\big\{c(x,P):\ I(\hat P_T,P)\le r\big\}',
              r'\mathcal R_f(\theta;P)=\sup_Q\big\{\mathbb E_Q[\ell(\theta;X)]:\ D_f(Q\,\|\,P)\le\rho\big\}'],
         land='The KL-ball predictor is admissible and strongly optimal: the probability of out-of-sample disappointment decays at '
              'rate $r$ (Van Parys, Mohajerin Esfahani & Kuhn 2021); minimax rates $\\max\\{n^{-1/2},n^{-1/k_*}\\}$ for '
              '$f$-divergence robustness (Duchi & Namkoong 2021).'),
    dict(t='Data quality and e-values', color='brown',
         idea='Quantity is not information: a small recording bias erases a large $n$. E-values stay valid whenever one looks.',
         eqs=[r'\bar Y_n-\bar Y_N=\hat\rho_{Y,R}\times\sqrt{(N-n)/n}\times\sigma_Y',
              r'\sup_{P\in\mathcal P}P\big(\exists t\ge1:\ E_t\ge1/\alpha\big)\le\alpha'],
         land='About 250,000 weekly survey answers were worth a random sample of about 10 people (Bradley, Kuriwaki, Isakov, '
              'Sejdinovic, Meng & Flaxman 2021); the growth-rate optimal e-value is $dQ/dP$, with rate $D_{\\mathrm{KL}}(Q\\|P)$ '
              '(Ramdas, Grünwald, Vovk & Shafer 2023).'),
]


def build():
    rc = regret_curves()
    ep = eprocess()
    tex = Tex()
    svg, overlays = hero(tex, rc, ep)
    html = build_page(tex, kicker='MACHINE LEARNING  ·  PARADIGM 4 OF 4  ·  LEARNING WHAT DATA ARE WORTH',
                      title='The value of information without a prior: regret, robustness, evidence',
                      tags=[('CLASSICAL', 'Bayesian VOI averaged over one prior'),
                            ('NEW', 'worst-case regret · ambiguity sets · e-values')],
                      hero_svg=svg, overlays=overlays, hero_y1=HERO_Y1, innov=innov(ep), innov_box=(1584, 132, 784, 694),
                      cards=CARDS, card_top=HERO_Y1 + 12, card_h=408, card_gap=12)
    open('d4_value_of_information.html', 'w').write(html)
    th, r_never, r_half, r_thr, wmin = rc
    print('wrote d4_value_of_information.html')
    print('regret maxima: never %.3f, half %.3f, threshold %.4f at |theta| %.3f; VOI_MMR %.4f; min welfare of threshold %.4f'
          % (r_never.max(), r_half.max(), r_thr.max(), abs(th[np.argmax(r_thr)]), r_half.max() - r_thr.max(), wmin))
    print('e-process: alarm month %d; null %d of %d crossed; median delay %.0f months; detected by month %d: %.3f'
          % (ep['alarm'], ep['fa'], ep['n0'], ep['med'], T_END, ep['det']))


if __name__ == '__main__':
    build()
