"""Transfer, route R2: a shared representation. A new aquifer from a few wells: one shared basis, the many give the prior.

Every picture in the schematic is a seeded computation (an illustration, not a field result):
  (a) response functions of a linear aquifer: the Theis pumping kernel at r = 100 m and the kernel of a fixed-head sea
      boundary at x = 300 m, for T 100-3,000 m2/d and S 0.01-0.2 (log-uniform), as daily pulse responses over 200 lags;
  (b) the POD of 2,000 such kernels (pumping block scaled by 1,000 m3/d, sea block by 0.2 m), k by the energy rule;
  (c) E-optimal choice of 12 training aquifers out of 300 candidates against 500 random sets of 12;
  (d) 40 training aquifers with two years of daily heads (noise sd 2 cm) give the coefficients and the prior; 300 new
      aquifers are fitted from n2 readings by least squares and by the Bayesian update with that prior, and judged on
      the noise-free heads of the following year; T and S are read by matching the posterior mean to a library of
      3,000 simulated responses (and, for comparison, by a linear map)."""
import numpy as np
from scipy.special import exp1, erfc

from ml_common import PAL, ORDER, INK, MUTED, Svg, Tex, ov, build_page

HERO_Y1 = 842
L, R_W, X_SEA, QS, ES, SIG = 200, 100.0, 300.0, 1000.0, 0.2, 0.02
LT, LSS = (np.log(100), np.log(3000)), (np.log(0.01), np.log(0.2))
EPS = 0.01
N2 = [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128]


# ---------------------------------------------------------------- computations
def stacked(T, S):
    t = np.arange(L + 1.0)
    tt = np.maximum(t, 1e-12)
    sq = np.where(t > 0, exp1(R_W ** 2 * S / (4 * T * tt)) / (4 * np.pi * T), 0.0)     # Theis step response
    se = np.where(t > 0, erfc(X_SEA / np.sqrt(4 * (T / S) * tt)), 0.0)                 # sea step response
    return np.concatenate([-np.diff(sq) * QS, np.diff(se) * ES])


def draw(rng, n):
    return np.c_[rng.uniform(*LT, n), rng.uniform(*LSS, n)]


def forcings(rng, n):
    nt = n + L
    q = np.repeat(rng.uniform(0, 2000, size=nt // 30 + 2), 30)[:nt]
    eta = np.zeros(nt)
    e = rng.normal(0, 0.1 * np.sqrt(1 - 0.9 ** 2), nt)
    for i in range(1, nt):
        eta[i] = 0.9 * eta[i - 1] + e[i]
    return q / QS, eta / ES


def design(q, e, days):
    idx = days[:, None] + L - 1 - np.arange(L)[None, :]
    return np.hstack([q[idx], e[idx]])


def compute():
    R = {}
    rng = np.random.default_rng(7)
    P = draw(rng, 2000)
    TH = np.array([stacked(*np.exp(p)) for p in P])
    _, s, Vt = np.linalg.svd(TH, full_matrices=False)
    tail = 1 - np.cumsum(s ** 2) / np.sum(s ** 2)
    K = int(np.argmax(tail <= EPS ** 2)) + 1
    B = Vt[:K].T
    R.update(K=K, sv=s[:12] / s[0], d=2 * L)
    # training aquifers: two years of daily heads -> coefficients -> prior
    M, n1 = 40, 730
    Ptr = draw(rng, M)
    W = []
    for p in Ptr:
        th = stacked(*np.exp(p))
        q, e = forcings(rng, n1)
        X = design(q, e, np.arange(n1))
        y = X @ th + rng.normal(0, SIG, n1)
        W.append(np.linalg.lstsq(X @ B, y, rcond=None)[0])
    W = np.array(W)
    wbar, SW = W.mean(0), np.cov(W.T)
    SWi = np.linalg.inv(SW)
    A_ = np.linalg.lstsq(np.c_[Ptr, np.ones(M)], W, rcond=None)[0]
    lib = draw(np.random.default_rng(11), 3000)
    libW = np.array([B.T @ stacked(*np.exp(p)) for p in lib])
    out = {n: dict(ls=[], by=[], cov=[], pT=[], pS=[]) for n in N2}
    prior = []
    for _ in range(300):
        p = draw(rng, 1)[0]
        th = stacked(*np.exp(p))
        q, e = forcings(rng, 730 + 365)
        Xho = design(q, e, np.arange(730, 730 + 365))
        tru = Xho @ th
        days = rng.permutation(730)
        Xall = design(q, e, days)
        yall = Xall @ th + rng.normal(0, SIG, 730)
        XhoB = Xho @ B
        prior.append(np.mean((XhoB @ wbar - tru) ** 2))
        for n in N2:
            X, y = Xall[:n] @ B, yall[:n]
            Cw = np.linalg.inv(SWi + X.T @ X / SIG ** 2)
            m = Cw @ (SWi @ wbar + X.T @ y / SIG ** 2)
            pr = XhoB @ m
            sd = np.sqrt(np.einsum('ij,jk,ik->i', XhoB, Cw, XhoB))
            out[n]['by'].append(np.mean((pr - tru) ** 2))
            out[n]['cov'].append(np.mean(np.abs(pr - tru) <= 1.645 * sd))
            if n >= K:
                wl = np.linalg.lstsq(X, y, rcond=None)[0]
                out[n]['ls'].append(np.mean((XhoB @ wl - tru) ** 2))
            j = np.argmin(np.sum((libW - m) ** 2, 1))
            out[n]['pT'].append(abs(lib[j, 0] - p[0]))
            out[n]['pS'].append(abs(lib[j, 1] - p[1]))
    cm = lambda v: 100 * np.sqrt(np.median(v))
    R['prior_cm'] = cm(prior)
    R['by'] = [cm(out[n]['by']) for n in N2]
    R['ls'] = [cm(out[n]['ls']) if out[n]['ls'] else None for n in N2]
    R['cov'] = [float(np.mean(out[n]['cov'])) for n in N2]
    R['pT'] = [float(np.exp(np.median(out[n]['pT'])) - 1) for n in N2]
    R['pS'] = [float(np.exp(np.median(out[n]['pS'])) - 1) for n in N2]
    # linear map from (ln T, ln S) to the coefficients, inverted on exact coefficients of 500 test aquifers
    Pt = draw(np.random.default_rng(5), 500)
    Wt = np.array([B.T @ stacked(*np.exp(p)) for p in Pt])
    ph = np.array([np.linalg.lstsq(A_[:2].T, w - A_[2], rcond=None)[0] for w in Wt])
    R['lin_T'] = float(np.exp(np.median(abs(ph[:, 0] - Pt[:, 0]))) - 1)
    R['lin_S'] = float(np.exp(np.median(abs(ph[:, 1] - Pt[:, 1]))) - 1)
    # E-optimal choice of 12 training aquifers out of 300 candidates
    rng = np.random.default_rng(21)
    pool = draw(rng, 300)
    TP = np.array([stacked(*np.exp(p)) for p in pool])
    WP = TP @ B
    test = draw(rng, 500)
    TT = np.array([stacked(*np.exp(p)) for p in test])

    def smin2(idx):
        return np.linalg.svd(WP[idx].T, compute_uv=False)[-1] ** 2

    def rep_err(idx):
        Ub = np.linalg.svd(TP[idx], full_matrices=False)[2][:K].T
        res = TT - (TT @ Ub) @ Ub.T
        return np.sum(res ** 2) / np.sum(TT ** 2)
    sel = []
    for _ in range(12):
        best = None
        for j in range(len(pool)):
            if j in sel:
                continue
            v = np.linalg.svd(WP[sel + [j]].T, compute_uv=False)
            val = v[-1] ** 2 if len(sel) + 1 >= K else np.prod(v ** 2)
            if best is None or val > best[0]:
                best = (val, j)
        sel.append(best[1])
    rs, re = [], []
    ex = None
    for i in range(500):
        idx = list(rng.choice(len(pool), 12, replace=False))
        rs.append(smin2(idx))
        re.append(rep_err(idx))
        if i == 0:
            ex = idx
    rs, re = np.array(rs), np.array(re)
    R.update(pool=pool, sel=sel, rand=ex, s_opt=smin2(sel), s_rand=float(np.median(rs)), s_beat=float(np.mean(rs >= smin2(sel))),
             e_opt=rep_err(sel), e_rand=float(np.median(re)), e_rand90=float(np.quantile(re, 0.9)))
    # kernels drawn in panel (a)
    R['curves'] = [(T, S, stacked(T, S)) for T, S in ((100, 0.2), (200, 0.05), (500, 0.1), (1000, 0.02), (3000, 0.05), (3000, 0.01))]
    return R


# ---------------------------------------------------------------- the schematic
def fmt_sci(v):
    e = int(np.floor(np.log10(v)))
    return '%.1f\\times10^{%d}' % (v / 10 ** e, e)


def hero(tex, R):
    g = Svg()
    O = []
    blue, purple, green, teal, orange, amber, pink, brown = (PAL[c] for c in ORDER)
    ramp = ['#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b']

    # ======== (a) response functions
    g.panel(32, 136, 500, 340, 'RESPONSE FUNCTIONS', 'blue', name='A')
    O.append(ov(282, 192, tex.text('illustration: daily pulse responses, $T$ 100–3,000 m²/d, $S$ 0.01–0.2'), 'cap', 'tc',
                style='font-size:14px'))
    charts = [('pumping, Theis, $r=100$ m', slice(0, L), 64, 'drawdown per 1,000 m³/d'),
              ('sea level, $x=300$ m', slice(L, 2 * L), 296, 'head per 0.2 m of sea')]
    for title, sl, x0, ylab in charts:
        w, y0, y1 = 210, 244, 384
        vmax = max(np.max(np.abs(c[2][sl])) for c in R['curves'])
        g.add(f'<line x1="{x0}" y1="{y1}" x2="{x0 + w}" y2="{y1}" stroke="#9aa3ad" stroke-width="2"/>'
              f'<line x1="{x0}" y1="{y0 - 4}" x2="{x0}" y2="{y1}" stroke="#9aa3ad" stroke-width="2"/>')
        O.append(ov(x0 + w / 2, 214, tex.text(title), 'note', 'tc', style='font-size:15px;font-weight:700'))
        lags = np.arange(1, L + 1)
        xs = x0 + np.log10(lags) / np.log10(L) * w
        for i, (T, S, th) in enumerate(R['curves']):
            v = np.abs(th[sl]) / vmax
            pts = ' '.join('%.1f,%.1f' % (a, y1 - b * (y1 - y0)) for a, b in zip(xs, v))
            g.add(f'<polyline points="{pts}" fill="none" stroke="{ramp[i]}" stroke-width="3" stroke-linejoin="round"/>')
        for d_ in (1, 10, 100):
            g.text(x0 + np.log10(d_) / np.log10(L) * w, y1 + 18, str(d_), size=13, weight=500, fill=MUTED, anchor='middle', halo=False)
        if x0 < 200:
            O.append(ov(x0 + w, y1 + 24, tex.text('lag, days (log scale)'), 'cap', 'tr', style='font-size:13px'))
        O.append(ov(x0 + 6, y0 - 2, tex.text(ylab), 'cap', 'tl', style='font-size:12.5px'))
    for i, c in enumerate(ramp):
        g.add(f'<rect x="{64 + 22 * i}" y="430" width="22" height="12" fill="{c}"/>')
    O.append(ov(64, 448, tex.text('low $T$ → high $T$'), 'cap', 'tl', style='font-size:13px'))
    O.append(ov(398, 418, tex.eq(r'\Theta_\eta(s;x)=\frac{x}{2\sqrt{\pi Ds^{3}}}\,e^{-x^{2}/(4Ds)}'), 'eqlab', 'tc', style='font-size:16px'))

    # ======== (b) one shared basis: POD spectrum
    g.panel(550, 136, 490, 340, 'ONE SHARED BASIS', 'purple', name='B')
    O.append(ov(795, 192, tex.text('illustration: POD of 2,000 simulated aquifers, $d=%d$ lags' % R['d']), 'cap', 'tc', style='font-size:14px'))
    X0, X1, Y0, Y1 = 616, 1016, 228, 388
    K = R['K']
    lo = -5.0

    def py(v):
        return Y1 - (np.log10(v) - lo) / (0 - lo) * (Y1 - Y0)
    xk = X0 + (K + 0.5) / 12.5 * (X1 - X0)
    g.add(f'<rect x="{X0}" y="{Y0}" width="{xk - X0:.1f}" height="{Y1 - Y0}" fill="{purple[2]}"/>')
    g.add(f'<line x1="{X0}" y1="{Y1}" x2="{X1}" y2="{Y1}" stroke="#9aa3ad" stroke-width="2"/>'
          f'<line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1}" stroke="#9aa3ad" stroke-width="2"/>')
    for e in (0, -2, -4):
        yy = py(10.0 ** e)
        g.add(f'<line x1="{X0}" y1="{yy:.1f}" x2="{X1}" y2="{yy:.1f}" stroke="#e3e8ee" stroke-width="1.2"/>')
    O.append(ov(X0 - 8, py(1.0), tex.eq('1'), 'eqbare', 'cr', style='font-size:14px'))
    O.append(ov(X0 - 8, py(1e-2), tex.eq('10^{-2}'), 'eqbare', 'cr', style='font-size:14px'))
    O.append(ov(X0 - 8, py(1e-4), tex.eq('10^{-4}'), 'eqbare', 'cr', style='font-size:14px'))
    for l, v in enumerate(R['sv'], start=1):
        x = X0 + l / 12.5 * (X1 - X0)
        col = purple[0] if l <= K else '#b9c0c9'
        g.add(f'<line x1="{x:.1f}" y1="{Y1}" x2="{x:.1f}" y2="{py(v):.1f}" stroke="{col}" stroke-width="3"/>'
              f'<circle cx="{x:.1f}" cy="{py(v):.1f}" r="6.5" fill="{col}" stroke="#ffffff" stroke-width="2"/>')
    g.add(f'<line x1="{xk:.1f}" y1="{Y0}" x2="{xk:.1f}" y2="{Y1}" stroke="{purple[1]}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    O.append(ov(xk + 8, Y0 + 4, tex.text('$k=%d$ kept' % K), 'lab', 'tl', style=f'font-size:16px;font-weight:800;color:{purple[1]}'))
    O.append(ov((X0 + X1) / 2, Y1 + 8, tex.text('index $l$ of the singular value $\\varsigma_l/\\varsigma_1$'), 'cap', 'tc', style='font-size:13.5px'))
    O.append(ov(795, 418, tex.eq(r'\mathbf{y}_t=X_t\,B\,\mathbf{w}_t+\boldsymbol{\varepsilon}_t,\qquad B\in\mathbb{R}^{%d\times %d}' % (R['d'], K)),
                'eqlab', 'tc', style='font-size:17px'))

    # ======== (c) choose diverse aquifers
    g.panel(1058, 136, 498, 340, 'CHOOSE DIVERSE AQUIFERS', 'green', name='C')
    O.append(ov(1307, 192, tex.text('illustration: 12 training aquifers out of 300 candidates'), 'cap', 'tc', style='font-size:14px'))
    CX0, CX1, CY0, CY1 = 1112, 1322, 226, 392

    def cxy(p):
        return (CX0 + (p[0] - LT[0]) / (LT[1] - LT[0]) * (CX1 - CX0), CY1 - (p[1] - LSS[0]) / (LSS[1] - LSS[0]) * (CY1 - CY0))
    g.add(f'<rect x="{CX0}" y="{CY0}" width="{CX1 - CX0}" height="{CY1 - CY0}" fill="#fbfcfd" stroke="#c9d1db" stroke-width="1.5"/>')
    for p in R['pool']:
        x, y = cxy(p)
        g.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="#b9c0c9"/>')
    for j in R['rand']:
        x, y = cxy(R['pool'][j])
        g.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.5" fill="none" stroke="{orange[0]}" stroke-width="2.5"/>')
    for j in R['sel']:
        x, y = cxy(R['pool'][j])
        g.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{green[0]}" stroke="#ffffff" stroke-width="2"/>')
    O.append(ov((CX0 + CX1) / 2, CY1 + 6, tex.text('$\\ln T$ →'), 'cap', 'tc', style='font-size:13.5px'))
    O.append(ov(CX0 - 6, (CY0 + CY1) / 2, tex.text('$\\ln S$'), 'cap', 'cr', style='font-size:13.5px'))
    lx = 1342
    g.add(f'<circle cx="{lx + 7}" cy="236" r="7" fill="{green[0]}"/>'
          f'<circle cx="{lx + 7}" cy="262" r="6.5" fill="none" stroke="{orange[0]}" stroke-width="2.5"/>'
          f'<circle cx="{lx + 7}" cy="288" r="3" fill="#b9c0c9"/>')
    O.append(ov(lx + 22, 236, tex.text('E-optimal 12'), 'note', 'cl', style='font-size:15px'))
    O.append(ov(lx + 22, 262, tex.text('a random 12'), 'note', 'cl', style='font-size:15px'))
    O.append(ov(lx + 22, 288, tex.text('candidates'), 'note', 'cl', style='font-size:15px'))
    O.append(ov(1432, 312, tex.eq(r'\sigma_k^{2}\left(W_{\mathcal S}\right):\ \times%.0f' % (R['s_opt'] / R['s_rand'])), 'eqlab', 'tc',
                style='font-size:17px'))
    O.append(ov(1432, 356, tex.text('against the median random set;'), 'cap', 'tc', style='font-size:13.5px'))
    O.append(ov(1432, 374, tex.text('no random set of 500 did as well'), 'cap', 'tc', style='font-size:13.5px'))
    O.append(ov(1307, 424, tex.text('40 training aquifers, two years of daily heads each,'), 'note', 'tc', style='font-size:14.5px'))
    O.append(ov(1307, 444, tex.text('give the coefficients $\\hat{\\mathbf w}_t$ and the prior'), 'note', 'tc', style='font-size:14.5px'))

    # ======== (d) a new aquifer from a few wells
    g.panel(32, 494, 840, 332, 'A NEW AQUIFER FROM A FEW WELLS', 'orange', name='D')
    O.append(ov(330, 550, tex.text('illustration: 300 new aquifers, heads of the next year, RMSE (median)'), 'cap', 'tc', style='font-size:14px'))
    DX0, DX1, DY0, DY1 = 112, 560, 584, 772
    ylo, yhi = np.log10(0.3), np.log10(100)

    def dxy(n, v):
        return DX0 + np.log10(n) / np.log10(128) * (DX1 - DX0), DY1 - (np.log10(v) - ylo) / (yhi - ylo) * (DY1 - DY0)
    g.add(f'<line x1="{DX0}" y1="{DY1}" x2="{DX1}" y2="{DY1}" stroke="#9aa3ad" stroke-width="2"/>'
          f'<line x1="{DX0}" y1="{DY0}" x2="{DX0}" y2="{DY1}" stroke="#9aa3ad" stroke-width="2"/>')
    for v in (1, 10, 100):
        yy = dxy(1, v)[1]
        g.add(f'<line x1="{DX0}" y1="{yy:.1f}" x2="{DX1}" y2="{yy:.1f}" stroke="#e3e8ee" stroke-width="1.2"/>')
        g.text(DX0 - 8, yy + 5, f'{v} cm', size=13, weight=500, fill=MUTED, anchor='end', halo=False)
    for n in (1, 4, 16, 64):
        g.text(dxy(n, 1)[0], DY1 + 18, str(n), size=13, weight=500, fill=MUTED, anchor='middle', halo=False)
    O.append(ov(DX1, DY1 + 22, tex.text('head readings $n_2$ of the new aquifer'), 'cap', 'tr', style='font-size:13.5px'))
    xk = dxy(R['K'], 1)[0]
    g.add(f'<line x1="{xk:.1f}" y1="{DY0}" x2="{xk:.1f}" y2="{DY1}" stroke="#8a93a0" stroke-width="2" stroke-dasharray="6 5"/>')
    O.append(ov(xk + 6, DY1 - 6, tex.text('$n_2=k$'), 'cap', 'bl', style='font-size:13.5px'))
    yp = dxy(1, R['prior_cm'])[1]
    g.add(f'<line x1="{DX0}" y1="{yp:.1f}" x2="{DX1}" y2="{yp:.1f}" stroke="{amber[1]}" stroke-width="2" stroke-dasharray="3 5"/>')
    O.append(ov(DX1 - 4, yp - 3, tex.text('prior alone: %.0f cm' % R['prior_cm']), 'cap', 'br', style=f'font-size:13.5px;color:{amber[1]}'))
    pts = ' '.join('%.1f,%.1f' % dxy(n, v) for n, v in zip(N2, R['ls']) if v)
    g.add(f'<polyline points="{pts}" fill="none" stroke="#5b6573" stroke-width="3.5" stroke-dasharray="9 6"/>')
    pts = ' '.join('%.1f,%.1f' % dxy(n, v) for n, v in zip(N2, R['by']))
    g.add(f'<polyline points="{pts}" fill="none" stroke="{orange[0]}" stroke-width="4.5" stroke-linejoin="round"/>')
    for n, v in zip(N2, R['by']):
        x, y = dxy(n, v)
        g.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{orange[0]}" stroke="#ffffff" stroke-width="1.5"/>')
    i8 = N2.index(8)
    xl, yl = dxy(8, R['ls'][i8])
    O.append(ov(xl + 10, yl - 4, tex.text('least squares'), 'lab', 'bl', style='font-size:15px;color:#3a4350'))
    xb, yb = dxy(2, R['by'][1])
    O.append(ov(xb + 10, yb + 6, tex.text('with the prior of the many'), 'lab', 'tl', style=f'font-size:15px;color:{orange[1]};font-weight:700'))
    # readouts
    i1, i4, i32 = N2.index(1), N2.index(4), N2.index(32)
    rx = 592
    rows = [('1 reading', '%.1f cm' % R['by'][i1]), ('4 readings', '%.1f cm' % R['by'][i4]),
            ('8 readings', '%.1f cm, least squares %.1f' % (R['by'][i8], R['ls'][i8]))]
    O.append(ov(rx, 572, tex.text('**prior fit, next-year heads**'), 'note', 'tl', style='font-size:15px'))
    for i, (a, b) in enumerate(rows):
        O.append(ov(rx, 600 + 24 * i, tex.text(f'{a}: **{b}**'), 'note', 'tl', style='font-size:14.5px'))
    cmin, cmax = min(R['cov']), max(R['cov'])
    O.append(ov(rx, 680, tex.text('90%% intervals cover %.2f–%.2f' % (cmin, cmax)), 'note', 'tl', style='font-size:14.5px'))
    O.append(ov(rx, 716, tex.text('**read the physics**'), 'note', 'tl', style='font-size:15px'))
    O.append(ov(rx, 742, tex.text('8 readings: $T$ ±%.0f%%, $S$ ±%.0f%%' % (100 * R['pT'][i8], 100 * R['pS'][i8])), 'note', 'tl', style='font-size:14.5px'))
    O.append(ov(rx, 766, tex.text('32 readings: $T$ ±%.0f%%, $S$ ±%.0f%%' % (100 * R['pT'][i32], 100 * R['pS'][i32])), 'note', 'tl', style='font-size:14.5px'))
    O.append(ov(rx, 790, tex.text('(median errors, library match)'), 'cap', 'tl', style='font-size:13px'))

    # ======== (e) which route for which quantity
    g.panel(890, 494, 666, 332, 'WHICH ROUTE FOR WHICH QUANTITY', 'brown', name='E')
    boxes = [(green, 'Heads and drawdowns  →  route R2', 'a few wells, a shared basis, the prior from the many'),
             (blue, 'The wedge, its toe, chloride  →  route R1', 'the dimensionless operator, its certificate, the alarm'),
             (orange, 'Both  →  R2 first, then R1', '$\\hat T$ and $\\hat S$ of R2 narrow the descriptor of R1')]
    for i, (c, t, x) in enumerate(boxes):
        y = 556 + 66 * i
        g.add(f'<rect x="914" y="{y}" width="618" height="56" rx="12" fill="{c[2]}" stroke="{c[0]}" stroke-width="2.5"/>')
        O.append(ov(932, y + 7, tex.text(f'**{t}**'), 'note', 'tl', style=f'font-size:16.5px;color:{c[1]}'))
        O.append(ov(932, y + 31, tex.text(x), 'note', 'tl', style='font-size:14.5px'))
    O.append(ov(1223, 762, tex.eq(r'\text{few heads}\Rightarrow\hat{\mathbf{w}}_{M+1}\Rightarrow\big(\hat T,\hat S\big)\Rightarrow u_T\downarrow\ \Rightarrow B_T\downarrow'),
                'eqlab', 'tc', style='font-size:17px'))

    for (x, y, n) in ((504, 159, 1), (1012, 159, 2), (1530, 159, 3), (1530, 448, 4), (286, 652, 5), (150, 748, 6), (842, 517, 7), (1530, 517, 8)):
        g.badge(x, y, n, ORDER[n - 1])
    return g.svg(HERO_Y1), O


# ---------------------------------------------------------------- content
def innov(R):
    i1, i4, i8, i32 = (N2.index(n) for n in (1, 4, 8, 32))
    return dict(
        kicker='INNOVATION', name='The many give the prior',
        sub='The training aquifers become the prior of a new one: a few head readings give its heads, $T$ and $S$.',
        items=[
            dict(t='A prior from the many, honest with few readings',
                 eqs=[r'C_w=\Big(\Sigma_W^{-1}+\tfrac{1}{\sigma^{2}}\hat B^{\top}X^{\top}X\hat B\Big)^{-1},\quad '
                      r'\mathbf m_w=C_w\Big(\Sigma_W^{-1}\bar{\mathbf w}+\tfrac{1}{\sigma^{2}}\hat B^{\top}X^{\top}\mathbf y\Big)'],
                 x='Exact when the basis is known; with fewer than $k$ readings the intervals stay honest, only wider. '
                   'Illustration ($k=%d$): next-year heads to %.1f cm from four readings, where least squares cannot start; '
                   '%.1f against %.1f cm from eight; 90%% intervals cover %.2f–%.2f.'
                   % (R['K'], R['by'][i4], R['by'][i8], R['ls'][i8], min(R['cov']), max(R['cov'])),
                 kv='%.1f cm' % R['by'][i4], kc='FROM FOUR READINGS'),
            dict(t='A few readings give $T$ and $S$',
                 eqs=[r'\hat{\mathbf p}=\arg\min_{\mathbf p}\big\|\mathbf m_w-\mathbf w(\mathbf p)\big\|\ \Rightarrow\ \big(\hat T,\hat S\big)_{M+1}'],
                 x='Amplitude fixes $T$, timing fixes $S/T$. Eight readings: $T$ within %.0f%%, $S$ within %.0f%% (medians); '
                   '32: %.0f%% and %.0f%%. A linear map $A\\mathbf p+\\mathbf a$ is cruder: %.0f%% and %.0f%% even with exact '
                   'coefficients.'
                   % (100 * R['pT'][i8], 100 * R['pS'][i8], 100 * R['pT'][i32], 100 * R['pS'][i32], 100 * R['lin_T'], 100 * R['lin_S']),
                 kv='±%.0f%%' % (100 * R['pT'][i8]), kc='T FROM EIGHT READINGS'),
            dict(t='Route R2 feeds route R1',
                 eqs=[r'B_T=\varepsilon_{\mathrm{tr}}+\big(L^{\dagger}+L_w\big)d_T+L^{\dagger}u_T,\qquad x_s=\sqrt{2T\tau/S}'],
                 x='$\\hat T$ and $\\hat S$ narrow the descriptor uncertainty $u_T$ of route R1 and its certificate $B_T$, '
                   'and set the skin distance $x_s$ and the slowest rate $\\omega_1$.',
                 kv='$u_T\\downarrow$', kc='R1 CERTIFICATE SHRINKS'),
        ],
        foot='')                    # where R2 stops: card 8


def cards(R):
    i8, i32, i128 = N2.index(8), N2.index(32), N2.index(128)
    return [
        dict(t='Response functions', color='blue',
             idea='A linear aquifer answers each forcing with a fixed response set by $T$, $S$ and the distances.',
             eqs=[r'h_t(\tau)=\sum_j\int_0^{\infty}\Theta_j\big(s;\mathbf p_t\big)\,F_{j,t}(\tau-s)\,ds',
                  r'\Theta_Q(s;r)=\frac{1}{4\pi Ts}\exp\Big(-\frac{r^{2}S}{4Ts}\Big),\qquad D=\frac{T}{S}'],
             pill='LITERATURE',
             land='Pumping: the point source of Theis (1935); sea: a fixed-head boundary. Heads as sums of responses: '
                  'Collenteur et al. (2019, Groundwater).'),
        dict(t='One shared basis', color='purple',
             idea='Over the range of $T$ and $S$ the responses lie near a $k$-dimensional space: one basis, $k$ coefficients '
                  'per aquifer.',
             eqs=[r'\Theta_j\big(s;\mathbf p_t\big)\approx\sum_{l=1}^{k}w_{t,l}\,b_{j,l}(s)',
                  r'k=\min\Big\{k:\ \sum_{l>k}\varsigma_l^{2}\le\varepsilon^{2}\sum_l\varsigma_l^{2}\Big\}'],
             pill='ILLUSTRATION',
             land='2,000 simulated aquifers, $\\varepsilon=%.2f$: $k=%d$ of $d=%d$ lag weights. Then '
                  '$\\mathbf y_t=X_tB\\mathbf w_t+\\boldsymbol\\varepsilon_t$, the multi-task model of Du, Hu, Kakade, Lee & '
                  'Lei (2021, ICLR).' % (EPS, R['K'], R['d'])),
        dict(t='Choose diverse aquifers', color='green',
             idea='Train on aquifers that span every direction of the basis: maximise the smallest singular value of their '
                  'coefficients.',
             eqs=[r'\mathcal S^{\star}=\arg\max_{|\mathcal S|=M}\ \sigma_k^{2}\big(W_{\mathcal S}\big),\quad W_{\mathcal S}=\big[\mathbf w(\mathbf p_t)\big]_{t\in\mathcal S}',
                  r'\sigma_k^{2}\big(W^{*}\big)\ge\Omega\Big(\frac{M}{k}\Big)'],
             pill='ILLUSTRATION',
             land='E-optimal 12 of 300: $\\sigma_k^2$ %.0f times the median random set. Its basis misses $%s$ of the response '
                  'energy (random sets: median $%s$, worst tenth above $%s$). Task diversity: Tripuraneni, Jordan & Jin '
                  '(2020, NeurIPS).' % (R['s_opt'] / R['s_rand'], fmt_sci(R['e_opt']), fmt_sci(R['e_rand']), fmt_sci(R['e_rand90']))),
        dict(t='Learn the basis from all wells', color='teal',
             idea='All $n_1M$ readings of the training aquifers learn the basis together; each then needs only $k$ '
                  'coefficients.',
             eqs=[r'\big(\hat B,\hat W\big)=\arg\min_{B,W}\frac{1}{2n_1M}\sum_{t=1}^{M}\big\|\mathbf y_t-X_tB\mathbf w_t\big\|^{2}',
                  r'n_1\gg\rho^{4}\Big(d+\log\frac{M}{\delta}\Big)'],
             pill='IN PRACTICE',
             land='Here the basis comes from simulated responses; 40 training aquifers with two years of daily heads give '
                  '$\\hat{\\mathbf w}_t$. Meta-learning: Fallah, Mokhtari & Ozdaglar (2020, AISTATS).'),
        dict(t='Fit the new aquifer from few wells', color='orange',
             idea='Only $k$ coefficients are unknown: about $k+\\log(1/\\delta)$ independent readings are needed, not $d$.',
             eqs=[r'\mathbb E\big[\mathrm{ER}_{M+1}\big]\le C\sigma^{2}\Big(\frac{kd\log(\kappa n_1)}{c\,n_1M}+\frac{k+\log(1/\delta)}{n_2}\Big)',
                  r'n_{\mathrm{eff}}\approx n_2\,\frac{1-\rho_{\varepsilon}}{1+\rho_{\varepsilon}}'],
             pill='ILLUSTRATION',
             land='Least squares needs $n_2\\ge%d$: next-year heads to %.1f cm with 8 readings, %.2f with 32, %.2f with 128. '
                  'Bound: Du et al. (2021); adaptive transfer: Reeve, Cannings & Samworth (2021, Annals of Statistics).'
                  % (R['K'], R['ls'][i8], R['ls'][i32], R['ls'][i128])),
        dict(t='The many give the prior', color='amber',
             idea='The coefficients of the training aquifers are the prior of the new one; the update is a small Bayesian fit.',
             eqs=[r'\mathbf w_{M+1}\sim\mathcal N\big(\bar{\mathbf w},\Sigma_W\big),\qquad \bar{\mathbf w}=\frac{1}{M}\sum_{t=1}^{M}\hat{\mathbf w}_t',
                  r'C_w=\Big(\Sigma_W^{-1}+\frac{1}{\sigma^{2}}\hat B^{\top}X^{\top}X\hat B\Big)^{-1}\preccurlyeq\Sigma_W'],
             pill='ILLUSTRATION',
             land='Exact when the basis is known; honest, only wider, with fewer than $k$ readings. Prior alone %.0f cm; one '
                  'reading %.1f cm; four %.1f cm; 90%% intervals cover %.2f–%.2f.'
                  % (R['prior_cm'], R['by'][0], R['by'][3], min(R['cov']), max(R['cov']))),
        dict(t='Read the physics, check', color='pink',
             idea='The fitted coefficients give $T$ and $S$ of the new site; the hold-out error and white residuals check the fit.',
             eqs=[r'\hat{\mathbf p}=\arg\min_{\mathbf p}\big\|\mathbf m_w-\mathbf w(\mathbf p)\big\|\ \Rightarrow\ \big(\hat T,\hat S\big)',
                  r'\text{hold-out error}(n_2)\propto\frac{1}{n_2},\qquad\text{white residuals}'],
             pill='ILLUSTRATION',
             land='Matched to a library of 3,000 simulated responses: $T$ within %.0f%%, $S$ within %.0f%% from 8 readings. A '
                  'linear map $\\mathbf w\\approx A\\mathbf p+\\mathbf a$, as in Blanke & Lelarge (2024, ICLR), is cruder here: '
                  '%.0f%% and %.0f%%.' % (100 * R['pT'][i8], 100 * R['pS'][i8], 100 * R['lin_T'], 100 * R['lin_S'])),
        dict(t='R1 and R2 together', color='brown',
             idea='Heads and drawdowns travel by R2; the wedge, its toe and chloride by route R1; R2 first narrows R1.',
             eqs=[r'\text{few heads}\Rightarrow\big(\hat T,\hat S\big)\Rightarrow u_T\downarrow\Rightarrow B_T\downarrow',
                  r'B_T=\varepsilon_{\mathrm{tr}}+\big(L^{\dagger}+L_w\big)d_T+L^{\dagger}u_T'],
             pill='WHERE R2 STOPS',
             land='Unconfined aquifers with large drawdown, seawater intrusion and strong small-scale heterogeneity break the '
                  'linear shared basis: there use route R1. Autocorrelated residuals count as fewer readings.'),
    ]


def build():
    R = compute()
    tex = Tex()
    svg, overlays = hero(tex, R)
    html = build_page(tex, kicker='TRANSFER  ·  ROUTE R2  ·  A SHARED REPRESENTATION',
                      title='A new aquifer from a few wells: one shared basis, the many give the prior',
                      tags=[('CLASSICAL', 'calibrate each aquifer alone, from its own long records'),
                            ('NEW', 'one basis for many aquifers · a few wells · the prior from the many')],
                      hero_svg=svg, overlays=overlays, hero_y1=HERO_Y1, innov=innov(R), innov_box=(1584, 132, 784, 694),
                      cards=cards(R), card_top=HERO_Y1 + 12, card_h=408, card_gap=12)
    open('d7_transfer_r2.html', 'w').write(html)
    print('wrote d7_transfer_r2.html')
    print('k', R['K'], 'sv', np.round(R['sv'][:7], 4))
    print('prior %.2f cm' % R['prior_cm'])
    for n, a, b, c, pT, pS in zip(N2, R['ls'], R['by'], R['cov'], R['pT'], R['pS']):
        print('n2 %3d  LS %s  prior-fit %.2f cm  cov %.3f  T %.3f  S %.3f' % (n, '%.2f' % a if a else '  -  ', b, c, pT, pS))
    print('linear map T %.3f S %.3f' % (R['lin_T'], R['lin_S']))
    print('E-opt sigma_k^2 %.3g random median %.3g ratio %.1f share random>=opt %.3f; rep err %.2e random median %.2e 90%% %.2e'
          % (R['s_opt'], R['s_rand'], R['s_opt'] / R['s_rand'], R['s_beat'], R['e_opt'], R['e_rand'], R['e_rand90']))


if __name__ == '__main__':
    build()
