"""Diagram 3 of 4: the landmark theory of deep reinforcement learning (learning to act from data).
The four mini-plots of the schematic are computed or taken from the source review:
(a) linear TD on a 7-state reflecting random walk (gamma = 0.95) converging to its projected Bellman fixed point;
(b) exact softmax policy gradient and natural policy gradient on a 10-state chain (gamma = 0.9);
(c) an offline pessimism illustration: 300 logged decisions, greedy on the estimate versus a lower confidence bound;
(d) the excess cost of learners trained on years of logs against the local floor (numbers of section 9 of the review)."""
import numpy as np

from ml_common import PAL, ORDER, INK, MUTED, Svg, Tex, ov, build_page, esc, FONT

HERO_Y1 = 842


# ---------------------------------------------------------------- computations
def td_chain():
    n, g = 7, 0.95
    P = np.zeros((n, n))
    for i in range(n):
        P[i, max(i - 1, 0)] += 0.5
        P[i, min(i + 1, n - 1)] += 0.5
    r = np.zeros(n); r[-1] = 1.0
    V = np.linalg.solve(np.eye(n) - g * P, r)
    w, v = np.linalg.eig(P.T)
    D = np.real(v[:, np.argmin(abs(w - 1))]); D /= D.sum()
    Phi = np.c_[np.ones(n), np.arange(n) / (n - 1)]
    Dm = np.diag(D)
    Amat, bvec = Phi.T @ Dm @ (np.eye(n) - g * P) @ Phi, Phi.T @ Dm @ r
    th_td = np.linalg.solve(Amat, bvec)
    mean = [np.zeros(2)]                                   # mean dynamics d(theta)/dt = b - A theta
    for _ in range(4000):
        mean.append(mean[-1] + 0.05 * (bvec - Amat @ mean[-1]))
    M = Phi.T @ Dm @ Phi
    th_pi = np.linalg.solve(M, Phi.T @ Dm @ V)
    err = lambda th: float(np.sqrt(D @ (Phi @ th - V) ** 2))
    rng = np.random.default_rng(1)
    th = np.zeros(2); s = 3; path = [th.copy()]
    for k in range(40000):
        s2 = rng.choice(n, p=P[s])
        a = 0.6 / (1 + k / 300)
        th = th + a * (r[s] + g * Phi[s2] @ th - Phi[s] @ th) * Phi[s]
        s = s2
        if k % 150 == 0:
            path.append(th.copy())
    return dict(th_td=th_td, th_pi=th_pi, M=M, path=np.array(path), mean=np.array(mean), e_td=err(th_td), e_pi=err(th_pi),
                bound=err(th_pi) / np.sqrt(1 - g * g), g=g)


def pg_chain():
    S, gam = 10, 0.9
    Pt = np.zeros((S, 2, S)); R = np.zeros((S, 2))
    for s in range(S):
        Pt[s, 0, min(s + 1, S - 1)] = 1.0          # move on
        Pt[s, 1, 0] = 1.0                          # back to the start
    R[S - 1, 0] = 1.0
    rho = np.zeros(S); rho[0] = 1
    mu = np.ones(S) / S

    def evalp(pi):
        Ppi = np.einsum('sa,sat->st', pi, Pt)
        Vp = np.linalg.solve(np.eye(S) - gam * Ppi, (pi * R).sum(1))
        return Vp, R + gam * Pt @ Vp, Ppi
    pistar = np.zeros((S, 2)); pistar[:, 0] = 1
    Vs = evalp(pistar)[0] @ rho

    def run(npg, T, eta):
        th = np.zeros((S, 2)); th[:, 1] = 2.0
        out = np.empty(T)
        for t in range(T):
            pi = np.exp(th - th.max(1, keepdims=True)); pi /= pi.sum(1, keepdims=True)
            Vp, Q, Ppi = evalp(pi)
            Adv = Q - Vp[:, None]
            out[t] = Vs - Vp @ rho
            if npg:
                th = th + eta / (1 - gam) * Adv
            else:
                d = (1 - gam) * np.linalg.solve(np.eye(S) - gam * Ppi.T, mu)
                th = th + eta / (1 - gam) * d[:, None] * pi * Adv
        return out
    return dict(pg=run(False, 200000, 0.5), npg=run(True, 60, 0.5), gam=gam, S=S)


def offline():
    A = np.arange(20)
    Q = 1 - ((A - 11) / 8.0) ** 2
    mu = np.exp(-0.5 * ((A - 7) / 2.6) ** 2); mu /= mu.sum()
    rng = np.random.default_rng(49)
    n = rng.multinomial(300, mu)
    est = np.array([rng.normal(Q[a], 1.0, n[a]).mean() if n[a] else np.nan for a in A])
    bonus = np.where(n > 0, 1.2 / np.sqrt(np.maximum(n, 1)), np.nan)
    lcb = est - bonus
    return dict(A=A, Q=Q, n=n, est=est, bonus=bonus, lcb=lcb, greedy=int(np.nanargmax(est)), pess=int(np.nanargmax(lcb)),
                astar=int(np.argmax(Q)), C=float(1 / mu[int(np.argmax(Q))]))


# ---------------------------------------------------------------- a small SVG axes helper
class Ax:
    def __init__(self, g, x, y, w, h, xr, yr, xlog=False, ylog=False):
        self.g, self.x, self.y, self.w, self.h = g, x, y, w, h
        self.xr, self.yr, self.xlog, self.ylog = xr, yr, xlog, ylog
        self.cid = f'axclip{x}_{y}'
        g.add(f'<clipPath id="{self.cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>')

    def clip(self, svg):
        return f'<g clip-path="url(#{self.cid})">{svg}</g>'

    def X(self, v):
        a, b = self.xr
        f = (np.log10(v) - np.log10(a)) / (np.log10(b) - np.log10(a)) if self.xlog else (v - a) / (b - a)
        return self.x + f * self.w

    def Y(self, v):
        a, b = self.yr
        f = (np.log10(v) - np.log10(a)) / (np.log10(b) - np.log10(a)) if self.ylog else (v - a) / (b - a)
        return self.y + self.h - f * self.h

    def frame(self, grid_x=(), grid_y=()):
        g = self.g
        g.add(f'<rect x="{self.x}" y="{self.y}" width="{self.w}" height="{self.h}" fill="#fbfcfe" stroke="#d0d7de" stroke-width="1.5"/>')
        for v in grid_x:
            g.add(f'<line x1="{self.X(v):.1f}" y1="{self.y}" x2="{self.X(v):.1f}" y2="{self.y + self.h}" stroke="#e6ebf1" stroke-width="1.2"/>')
        for v in grid_y:
            g.add(f'<line x1="{self.x}" y1="{self.Y(v):.1f}" x2="{self.x + self.w}" y2="{self.Y(v):.1f}" stroke="#e6ebf1" stroke-width="1.2"/>')

    def xt(self, vals, labels, size=14):
        for v, s in zip(vals, labels):
            self.g.text(round(self.X(v), 1), self.y + self.h + 17, s, size=size, weight=500, fill=MUTED, anchor='middle', halo=False)

    def yt(self, vals, labels, size=14):
        for v, s in zip(vals, labels):
            self.g.text(self.x - 6, round(self.Y(v) + 5, 1), s, size=size, weight=500, fill=MUTED, anchor='end', halo=False)

    def line(self, xs, ys, color, width=3.5, dash=None, opacity=1):
        pts = ' '.join(f'{self.X(a):.1f},{self.Y(b):.1f}' for a, b in zip(xs, ys))
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.g.add(self.clip(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" '
                             f'stroke-linecap="round" opacity="{opacity}"{da}/>'))


def star(cx, cy, r, fill, stroke='#ffffff'):
    pts = []
    for k in range(10):
        ang = -np.pi / 2 + k * np.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append(f'{cx + rr * np.cos(ang):.1f},{cy + rr * np.sin(ang):.1f}')
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'


def net(g, xs, sizes, y0, y1, color, node_r=7):
    """A small multilayer network: nodes in columns xs with the given layer sizes, centred between y0 and y1."""
    cols = []
    for x, n in zip(xs, sizes):
        ys = np.linspace(y0, y1, n + 2)[1:-1] if n > 1 else [0.5 * (y0 + y1)]
        cols.append([(x, y) for y in ys])
    for a, b in zip(cols[:-1], cols[1:]):
        for (x1, y1_) in a:
            for (x2, y2) in b:
                g.add(f'<line x1="{x1}" y1="{y1_:.1f}" x2="{x2}" y2="{y2:.1f}" stroke="{color}" stroke-width="1.3" opacity=".35"/>')
    for c in cols:
        for (x, y) in c:
            g.add(f'<circle cx="{x}" cy="{y:.1f}" r="{node_r}" fill="#ffffff" stroke="{color}" stroke-width="3"/>')
    return cols


# ---------------------------------------------------------------- the schematic
def hero(td, pg, off, tex):
    g = Svg()
    O = []
    blue, purple, green, teal, orange, amber, pink, brown = (PAL[c] for c in ORDER)

    # ---- (a) value learning: TD in the parameter plane
    g.panel(32, 136, 450, 334, 'VALUE LEARNING · TD', 'purple', name='Sa')
    ax = Ax(g, 96, 196, 362, 170, (-1.2, 2.6), (-0.6, 5.6))
    ax.frame(grid_x=(0, 1, 2), grid_y=(0, 2, 4))
    Mi = np.linalg.inv(td['M'])
    w_, U = np.linalg.eigh(Mi)
    for c in (0.15, 0.35, 0.6, 0.9, 1.25):
        t = np.linspace(0, 2 * np.pi, 120)
        pts = td['th_pi'][:, None] + c * (U @ np.diag(np.sqrt(w_)) @ np.vstack([np.cos(t), np.sin(t)]))
        ax.line(pts[0], pts[1], purple[0], width=1.6, opacity=.45)
    for (a_, b_) in td['path'][1:]:
        if -1.2 < a_ < 2.6 and -0.6 < b_ < 5.6:
            g.add(f'<circle cx="{ax.X(a_):.1f}" cy="{ax.Y(b_):.1f}" r="2.6" fill="#3a4350" opacity=".45"/>')
    m = td['mean']
    ax.line(m[:, 0], m[:, 1], purple[1], width=4)
    g.add(f'<circle cx="{ax.X(0):.1f}" cy="{ax.Y(0):.1f}" r="6" fill="#3a4350"/>')
    g.add(star(ax.X(td['th_td'][0]), ax.Y(td['th_td'][1]), 12, amber[0], '#1f2328'))
    ax.xt((-1, 0, 1, 2), ('−1', '0', '1', '2')); ax.yt((0, 2, 4), ('0', '2', '4'))
    g.text(ax.X(0) + 12, ax.Y(0) + 20, 'start', size=15, weight=600, fill='#3a4350')
    g.text(ax.X(td['th_td'][0]) + 16, ax.Y(td['th_td'][1]) + 5, 'TD fixed point', size=15, weight=700, fill=amber[1])
    g.text(ax.X(1.1), ax.Y(1.6), 'mean dynamics', size=15, weight=700, fill=purple[1])
    g.text(ax.X(-1.1), ax.Y(3.0), 'TD iterates', size=15, weight=600, fill='#3a4350')
    g.text(ax.x + ax.w - 6, ax.y + ax.h - 8, 'θ₁ (level)', size=14, weight=600, fill=MUTED, anchor='end', halo=True)
    g.text(ax.x + 8, ax.y + 18, 'θ₂ (slope)', size=14, weight=600, fill=MUTED, halo=True)
    O.append(ov(257, 388, tex.eq(r'\|\Phi\theta^\star-V\|_D\le\|\Pi_DV-V\|_D\,/\sqrt{1-\gamma^2}'), 'eqlab', 'tc', style='font-size:19px'))
    O.append(ov(257, 458, tex.text(f'illustration: 7-state chain, γ = {td["g"]}: error {td["e_td"]:.2f} ≤ bound {td["bound"]:.2f}'),
                'cap', 'bc', style='font-size:14.5px'))

    # ---- (b) policy optimisation: softmax PG vs natural PG
    g.panel(1090, 136, 466, 334, 'POLICY GRADIENT', 'orange', name='Sb')
    ax = Ax(g, 1150, 196, 384, 196, (1, 2e5), (1e-4, 40), xlog=True, ylog=True)
    ax.frame(grid_x=(10, 100, 1e3, 1e4, 1e5), grid_y=(1e-3, 1e-2, 1e-1, 1))
    t = np.unique(np.round(np.logspace(0, np.log10(len(pg['pg']) - 1), 300)).astype(int))
    ax.line(t, np.maximum(pg['pg'][t], 1e-4), orange[0], width=4)
    tn = np.arange(1, len(pg['npg']))
    yn = np.maximum(pg['npg'][tn], 1e-4)
    k = int(np.argmax(yn <= 1e-4)) + 1
    ax.line(tn[:k], yn[:k], amber[1], width=4)
    tt = np.array([2e3, 2e5])
    ax.line(tt, pg['pg'][2000] * 2e3 / tt, MUTED, width=2, dash='6 6')
    ax.xt((1, 10, 100, 1e3, 1e4, 1e5), ('1', '10', '10²', '10³', '10⁴', '10⁵'))
    ax.yt((1e-4, 1e-2, 1), ('10⁻⁴', '10⁻²', '1'))
    g.text(ax.X(20), ax.Y(pg['pg'][20]) - 12, 'softmax PG: a plateau…', size=15, weight=700, fill=orange[1])
    g.text(ax.X(6e3), ax.Y(2e-3) - 14, '…then O(1/t)', size=15, weight=700, fill=orange[1])
    g.text(ax.X(13), ax.Y(1e-3) + 4, 'natural PG: linear', size=15, weight=700, fill=amber[1])
    g.text(ax.X(2.5e4), ax.y + ax.h - 8, 'iteration t', size=14, weight=600, fill=MUTED, anchor='middle', halo=True)
    O.append(ov(1323, 418, tex.eq(r'V^\star(\rho)-V^{\pi_{\theta_t}}(\rho)'), 'eqbare', 'tc', style='font-size:19px'))
    O.append(ov(1323, 463, tex.text(f'illustration: {pg["S"]}-state chain, γ = {pg["gam"]}, exact gradients'), 'cap', 'bc', style='font-size:14.5px'))

    # ---- (c) offline: coverage and pessimism
    g.panel(32, 494, 450, 334, 'OFFLINE · PESSIMISM', 'pink', name='Sc')
    ax = Ax(g, 96, 556, 362, 152, (-0.6, 19.6), (-1.4, 3.1))
    ax.frame(grid_y=(-1, 0, 1, 2))
    A, Q = off['A'], off['Q']
    xs = np.linspace(-0.4, 19.4, 120)
    ax.line(xs, 1 - ((xs - 11) / 8.0) ** 2, '#8a93a0', width=3)
    for a in A:
        if off['n'][a] == 0:
            continue
        e, b = off['est'][a], off['bonus'][a]
        top, bot = min(e + b, 3.1), max(e - b, -1.4)
        g.add(ax.clip(f'<line x1="{ax.X(a):.1f}" y1="{ax.Y(top):.1f}" x2="{ax.X(a):.1f}" y2="{ax.Y(bot):.1f}" stroke="{pink[0]}" stroke-width="2" opacity=".55"/>'
                      f'<circle cx="{ax.X(a):.1f}" cy="{ax.Y(e):.1f}" r="4.5" fill="{pink[0]}"/>'
                      f'<line x1="{ax.X(a) - 6:.1f}" y1="{ax.Y(max(e - b, -1.4)):.1f}" x2="{ax.X(a) + 6:.1f}" y2="{ax.Y(max(e - b, -1.4)):.1f}" stroke="{green[1]}" stroke-width="3"/>'))
    nb = ax.y + ax.h + 8                                         # logged counts below the plot
    for a in A:
        hh = 30 * off['n'][a] / off['n'].max()
        g.add(f'<rect x="{ax.X(a) - 7:.1f}" y="{nb + 30 - hh:.1f}" width="14" height="{max(hh, 0.8):.1f}" fill="#9aa3ad"/>')
    gr, pe, st = off['greedy'], off['pess'], off['astar']
    g.add(f'<circle cx="{ax.X(gr):.1f}" cy="{ax.Y(off["est"][gr]):.1f}" r="11" fill="none" stroke="#b42318" stroke-width="3.5"/>')
    g.add(f'<circle cx="{ax.X(pe):.1f}" cy="{ax.Y(off["lcb"][pe]):.1f}" r="11" fill="none" stroke="{green[1]}" stroke-width="3.5"/>')
    g.add(star(ax.X(st), ax.Y(Q[st]) - 1, 11, amber[0], '#1f2328'))
    g.text(ax.X(gr) + 16, ax.Y(2.78), 'greedy: logged once, the worst', size=15, weight=700, fill='#b42318')
    g.text(ax.X(pe) - 2, ax.Y(off['lcb'][pe]) + 30, 'pessimistic (LCB)', size=15, weight=700, fill=green[1], anchor='middle')
    g.add(f'<line x1="{ax.X(st) + 6:.1f}" y1="{ax.Y(Q[st]) - 10:.1f}" x2="{ax.X(14.6):.1f}" y2="{ax.Y(2.15):.1f}" stroke="{amber[1]}" stroke-width="2"/>')
    g.text(ax.X(14.8), ax.Y(2.15) + 5, 'best action', size=15, weight=700, fill=amber[1])
    g.text(ax.x + ax.w - 4, nb + 26, 'logged actions', size=14, weight=600, fill=MUTED, anchor='end', halo=True)
    O.append(ov(257, 778, tex.text('illustration: 300 logged decisions; grey: true value,'), 'cap', 'tc', style='font-size:14.5px'))
    O.append(ov(257, 800, tex.text(f'dots: estimates ± bonus, green: LCB; coverage $C^\\star={off["C"]:.0f}$'), 'cap', 'tc', style='font-size:14.5px'))

    # ---- (d) how many years of logs (source, section 9)
    g.panel(1090, 494, 466, 334, 'HOW MANY YEARS OF LOGS', 'brown', name='Sd')
    ax = Ax(g, 1150, 552, 384, 176, (6, 160), (0.1, 100), xlog=True, ylog=True)
    ax.frame(grid_x=(10, 30, 100), grid_y=(1, 10))
    N = np.array([6, 160])
    ax.line(N, 2.09 * 10 / N, '#3a4350', width=3)
    ax.line(N, [1, 1], MUTED, width=1.6, dash='5 5')
    g.add(f'<circle cx="{ax.X(20.9):.1f}" cy="{ax.Y(1):.1f}" r="6" fill="#3a4350"/>')
    g.text(1158, ax.Y(1) + 24, '20.9 years for 1%', size=15, weight=800, fill='#3a4350')
    for (yr, v) in ((10, 10.74), (30, 1.12), (100, 0.29)):
        g.add(f'<circle cx="{ax.X(yr) - 10:.1f}" cy="{ax.Y(v):.1f}" r="6.5" fill="{blue[0]}" stroke="#fff" stroke-width="2"/>')
    for (yr, vs) in ((10, (8.91, 5.47)), (30, (6.60, 6.28)), (100, (4.99, 6.76))):
        for v in vs:
            g.add(f'<rect x="{ax.X(yr) + 4:.1f}" y="{ax.Y(v) - 6:.1f}" width="12" height="12" fill="{green[0]}" stroke="#fff" stroke-width="2" transform="rotate(45 {ax.X(yr) + 10:.1f} {ax.Y(v):.1f})"/>')
    for (yr, v) in ((10, 52.03), (30, 16.28), (100, 12.11), (100, 9.43)):
        g.add(f'<path d="M{ax.X(yr):.1f},{ax.Y(v) - 7:.1f} l7,12 h-14 z" fill="{orange[0]}" stroke="#fff" stroke-width="1.5"/>')
    for yr, lab in ((10, 'unstable'), (30, '+17 823%')):            # unstable / off-scale runs
        g.arrow(f'M{ax.X(yr) + 14:.1f},{ax.Y(30):.1f} V{ax.y + 6}', orange[1], 3)
        g.text(round(ax.X(yr) + 24, 1), round(ax.Y(55), 1), lab, size=13.5, weight=700, fill=orange[1])
    ax.xt((10, 30, 100), ('10', '30', '100'))
    ax.yt((0.1, 1, 10, 100), ('0.1%', '1%', '10%', '100%'))
    g.text(ax.x + 8, ax.y + ax.h - 8, 'years of logs', size=14, weight=600, fill=MUTED, halo=True)
    g.text(ax.X(50), ax.Y(0.40) - 6, 'floor ∝ 1/N', size=15, weight=800, fill='#3a4350', halo=True)
    lx, ly = 1110, 760                                             # legend
    for i, (shape, col, lab) in enumerate((('c', blue[0], 'physical model, exact rule'), ('d', green[0], 'neural policy'),
                                           ('t', orange[0], 'deep world model'))):
        x = lx + i * 150
        if shape == 'c':
            g.add(f'<circle cx="{x + 8}" cy="{ly}" r="6.5" fill="{col}"/>')
        elif shape == 'd':
            g.add(f'<rect x="{x + 2}" y="{ly - 6}" width="12" height="12" fill="{col}" transform="rotate(45 {x + 8} {ly})"/>')
        else:
            g.add(f'<path d="M{x + 8},{ly - 7} l7,12 h-14 z" fill="{col}"/>')
    g.text(lx + 20, ly + 5, 'physical model', size=14, weight=600, fill=INK, halo=False)
    g.text(lx + 170, ly + 5, 'neural policy', size=14, weight=600, fill=INK, halo=False)
    g.text(lx + 320, ly + 5, 'deep world model', size=14, weight=600, fill=INK, halo=False)
    O.append(ov(1323, 778, tex.text('source test bed; arrows: unstable or off-scale runs'), 'cap', 'tc', style='font-size:14.5px'))
    O.append(ov(1323, 800, tex.text('memory ×25: worst case ×15 625, floor 19.6 → 21.1 years'), 'cap', 'tc', style='font-size:14.5px'))

    # ---- centre: the agent and the environment
    g.panel(506, 136, 560, 284, 'THE AGENT: CRITIC + ACTOR', 'blue', name='Sg')
    net(g, [585, 635, 685, 735], [4, 6, 6, 1], 196, 306, purple[0])
    for i, h_ in enumerate((10, 22, 34, 26, 14)):                  # the return law of the critic, with quantile ticks
        g.add(f'<rect x="{754 + i * 9}" y="{292 - h_}" width="8" height="{h_}" fill="{teal[0]}" opacity=".8"/>')
    for i in range(4):
        g.add(f'<line x1="{760 + i * 11}" y1="{294}" x2="{760 + i * 11}" y2="{302}" stroke="{teal[1]}" stroke-width="2.5"/>')
    g.add(f'<path d="M744,251 H752" stroke="{purple[0]}" stroke-width="2.5"/>')
    cols = net(g, [850, 900, 950, 1000], [4, 6, 6, 3], 196, 306, orange[0])
    for (x, y), hgt in zip(cols[-1], (0.25, 0.6, 0.15)):            # policy probabilities
        g.add(f'<rect x="{x + 12}" y="{y - 6:.1f}" width="{34 * hgt:.1f}" height="12" rx="3" fill="{orange[0]}" opacity=".85"/>')
    O.append(ov(660, 316, tex.text('critic $Q_w(s,a)$'), 'lab', 'tc', style='font-size:18px'))
    O.append(ov(925, 316, tex.text('actor $\\pi_\\theta(a\\mid s)$'), 'lab', 'tc', style='font-size:18px'))
    g.text(536, 366, 'excess cost of a deep agent =', size=16, weight=700, fill=INK, halo=False)
    segs = (('approximation', blue[1], 0.36), ('estimation', purple[1], 0.30), ('optimisation', orange[1], 0.34))
    x = 536
    for lab, col, fr in segs:
        wseg = 500 * fr
        g.add(f'<rect x="{x:.1f}" y="374" width="{wseg - 4:.1f}" height="30" rx="7" fill="{col}"/>')
        g.text(round(x + (wseg - 4) / 2, 1), 395, lab, size=15, weight=800, fill='#ffffff', anchor='middle', halo=False)
        x += wseg
    g.panel(506, 560, 560, 268, 'THE ENVIRONMENT: AN MDP', 'teal', name='Se')
    xs_ = [580, 680, 780, 880, 980]
    for i, x in enumerate(xs_):
        if i < 4:
            g.arrow(f'M{x + 28},646 H{xs_[i + 1] - 31}', teal[1], 4)
        g.add(f'<circle cx="{x}" cy="646" r="26" fill="{teal[2]}" stroke="{teal[0]}" stroke-width="4"/>')
        g.text(x, 653, f's{"₁₂₃₄₅"[i]}', size=19, weight=800, fill=teal[1], anchor='middle', halo=False)
    g.arrow('M980,673 C960,712 620,712 590,676', '#8a93a0', 3, dash='7 6')
    g.add(star(1018, 618, 13, amber[0], '#1f2328'))
    g.text(1030, 650, '+r', size=17, weight=800, fill=amber[1], halo=False)
    O.append(ov(786, 724, tex.eq(r'Q^\star(s,a)=r(s,a)+\gamma\,\mathbb E\big[\max_{a\prime}Q^\star(s\prime,a\prime)\big]'), 'eqlab', 'tc', style='font-size:19px'))
    O.append(ov(786, 776, tex.text('e.g. a pumping agent: state = heads and salinity, action = monthly'), 'cap', 'tc', style='font-size:15px'))
    O.append(ov(786, 797, tex.text('pumping, reward = minus the cost of salinity and deficit'), 'cap', 'tc', style='font-size:15px'))
    # the loop: action down, state and reward up, logs offline
    g.arrow('M1006,420 V556', orange[1], 5)
    O.append(ov(994, 470, tex.text('action $a_t$'), 'lab', 'cr', style='font-size:18px'))
    g.arrow('M566,560 V424', teal[1], 5)
    O.append(ov(578, 470, tex.text('$s_{t+1},\\ r_t$'), 'lab', 'cl', style='font-size:18px'))
    g.add(f'<g transform="translate(786,444)"><ellipse cx="0" cy="0" rx="26" ry="8" fill="{pink[2]}" stroke="{pink[0]}" stroke-width="3"/>'
          f'<path d="M-26,0 V34 A26,8 0 0 0 26,34 V0" fill="{pink[2]}" stroke="{pink[0]}" stroke-width="3"/>'
          f'<path d="M-26,12 A26,8 0 0 0 26,12 M-26,23 A26,8 0 0 0 26,23" fill="none" stroke="{pink[0]}" stroke-width="2"/></g>')
    O.append(ov(786, 500, tex.text('offline: logs $\\mathcal D=\\{(s,a,r,s\\prime)\\}$ written by operators'), 'lab', 'tc', style='font-size:16px'))
    g.arrow('M786,436 V426', pink[1], 4)
    g.arrow('M484,520 C560,522 690,470 752,462', pink[1], 3, dash='7 6')
    g.arrow('M484,300 H502', purple[1], 4)
    g.arrow('M1088,300 H1070', orange[1], 4)
    for (x, y, n) in ((1040, 583, 1), (456, 159, 2), (538, 214, 3), (788, 222, 4), (1530, 159, 5), (1262, 300, 6), (456, 517, 7),
                      (1530, 517, 8)):
        g.badge(x, y, n, ORDER[n - 1])
    return g.svg(HERO_Y1), O


# ---------------------------------------------------------------- content
INNOV = dict(
    kicker='INNOVATION', name='The years of data any learner needs',
    sub='A local floor, for every learner, deep or not, trained on closed-loop logs.',
    items=[
        dict(t='The excess cost of a learned rule is a distance',
             eqs=[r'J(\pi)-J^\star=\overline{\mathbb E}\big[(q_t-q_t^\star)^{\top}W\,(q_t-q_t^\star)\big],\qquad W=R+B^{\top}PB'],
             x='For a linear–quadratic system with partial observation, the loss of any records-only rule is its weighted '
               'distance from the optimal action $q_t^\\star=-K\\,\\mathbb E[z_t\\mid y_{\\le t},q_{<t}]$, whatever the learner.'),
        dict(t='A local floor, in years of logs',
             eqs=[r'\liminf_{N\to\infty}N\,\mathcal R_{c,N}(\hat\pi)\ \ge\ \tfrac12\,\mathrm{tr}\big(HI^{-1}\big),\qquad N_\varepsilon=\frac{\mathrm{tr}(HI^{-1})}{2\,\varepsilon\,J^\star}'],
             x='$H$: curvature of the cost in the physical parameters; $I$: Fisher information per month of the logs. A '
               'coastal-aquifer pumping agent needs 20.9 years of logs to come within 1% of the optimum with 4 parameters, 44.2 '
               'with 8; worst-case rates would grow with the cube of the memory.',
             kv='20.9 yr', kc='FOR 1%, ANY LEARNER'),
        dict(t='What shortens the years, and where deep agents land',
             eqs=[r'd_t=\phi\,d_{t-1}+\sigma_d\sqrt{1-\phi^2}\,\eta_t\ \Rightarrow\ \Delta J_{\mathrm{op}}=W\sigma_d^2\ \ \text{for every }\phi'],
             x='Good operators write uninformative logs (timid ones: 10.8 years); logging their own toe reading halves the years '
               '(10.2); a recorded dither costs the same whatever its colour. Deep agents land far above the floor: a neural '
               'policy +5–9%, a deep world model 45–58 times it.',
             kv='10.2 yr', kc='OWN READING LOGGED'),
    ],
    foot='')

CARDS = [
    dict(t='The MDP and the three errors', color='blue',
         idea='A deep agent errs because its network cannot represent the right function, its data are finite and its training '
              'stops short, and data from one policy judge another.',
         eqs=[r'\mathcal TQ(s,a)=r(s,a)+\gamma\,\mathbb E\big[\max_{a\prime}Q(s\prime,a\prime)\big]',
              r'V^{\pi}(\rho)-V^{\pi\prime}(\rho)=\tfrac{1}{1-\gamma}\,\mathbb E_{s\sim d^{\pi}_{\rho},\,a\sim\pi}\big[A^{\pi\prime}(s,a)\big]'],
         land='Error split explicit for deep fitted Q-iteration (Fan, Wang, Xie & Yang 2020) and neural actor–critic (Wang, Cai, '
              'Yang & Wang 2020); the shift costs a concentrability $C^\\pi=\\max d^\\pi/\\mu$ (Rashidinejad et al. 2022).'),
    dict(t='TD as stochastic approximation', color='purple',
         idea='TD follows no gradient, yet its mean dynamics are stable; one Markovian trajectory is enough, at the price of '
              'the mixing time.',
         eqs=[r'\theta_{k+1}=\theta_k+\alpha_k\big(r_k+\gamma\phi(s_{k+1})^{\top}\theta_k-\phi(s_k)^{\top}\theta_k\big)\phi(s_k)',
              r'\mathbb E M(x_{k+1}-x^\star)\le(1-c_1\alpha_k)\,\mathbb E M(x_k-x^\star)+c_2\alpha_k^2t_{\alpha_k}'],
         land='Finite-time bounds for linear TD with Markovian data (Bhandari, Russo & Singal 2021); a Lyapunov theory built on a '
              'generalised Moreau envelope $M$ that covers Q-learning (Chen, Maguluri, Shakkottai & Shanmugam 2024).'),
    dict(t='Deep Q-learning', color='green',
         idea='Fitted Q-iteration is the clean model of DQN: the network enters only through a one-step regression error, '
              'plus a term that vanishes geometrically.',
         eqs=[r'\|Q^\star-Q^{\pi_K}\|_{1,\rho}\lesssim\frac{C_{\rho,\mu}^{1/2}}{(1-\gamma)^2}\max_{k<K}\|\mathcal TQ_k-Q_{k+1}\|_\mu',
              r'\partial_t\rho_t=-\eta\,\mathrm{div}\big(\rho_t\,g(\cdot\,;\rho_t)\big)'],
         land='Deep ReLU FQI: a vanishing algorithmic error plus a nonparametric statistical error (Fan, Wang, Xie & Yang 2020); '
              'in the mean-field regime neural TD converges while its features move (Zhang, Cai, Yang, Chen & Wang 2020).'),
    dict(t='Distributional value learning', color='teal',
         idea='Learn the law of the return, not only its mean: what a water utility fears is the tail, a salinity limit '
              'exceeded in a dry decade.',
         eqs=[r'\theta_i\leftarrow\theta_i+\alpha_k\Big(\tau_i-\tfrac1m\textstyle\sum_{j}\mathbf 1\{r+\gamma\theta_j(x\prime)<\theta_i\}\Big)',
              r'\tau_i=\frac{2i-1}{2m},\qquad \rho_\tau(u)=u\big(\tau-\mathbf 1\{u<0\}\big)'],
         land='Quantile TD converges although its update is discontinuous and may have several fixed points, proved with '
              'differential inclusions (Rowland, Munos, Azar et al. 2024).'),
    dict(t='The landscape of policy gradients', color='orange',
         idea='The objective is not concave, yet gradient ascent finds the global optimum: gradient domination bounds the gap '
              'by a first-order quantity.',
         eqs=[r'\nabla_\theta V^{\pi_\theta}(\rho)=\tfrac{1}{1-\gamma}\,\mathbb E_{s\sim d^{\pi_\theta}_\rho,\,a\sim\pi_\theta}\big[\nabla_\theta\ln\pi_\theta(a\mid s)\,A^{\pi_\theta}(s,a)\big]',
              r't_\varepsilon\ \ge\ \tfrac1\eta\,|\mathcal S|^{2^{\Omega(1/(1-\gamma))}}'],
         land='Softmax PG converges at rate $O(1/t)$ (Mei, Xiao, Szepesvári & Schuurmans 2020) but can take time exponential '
              'in the horizon (Li, Wei, Chi & Chen 2023); no spurious stationary points when the class is closed under policy '
              'improvement, as in LQ control (Bhandari & Russo 2024).'),
    dict(t='Natural gradients and mirror descent', color='amber',
         idea='Precondition by the Fisher information: for softmax policies the step is multiplicative, a mirror-descent step '
              'in KL; TRPO, PPO and soft actor–critic are relatives.',
         eqs=[r'\pi_{k+1}(a\mid s)\ \propto\ \pi_k(a\mid s)\,\exp\big(\eta_k\,Q^{\pi_k}(s,a)\big)',
              r'\|Q_\tau^\star-Q_\tau^{(t+1)}\|_\infty\le C_1\gamma\,(1-\eta\tau)^t'],
         land='Entropy-regularised natural PG converges linearly at a nearly dimension-free rate (Cen, Cheng, Chen, Wei & Chi '
              '2022); neural natural PG with a neural critic reaches a global optimum (Wang, Cai, Yang & Wang 2020).'),
    dict(t='Offline: coverage and pessimism', color='pink',
         idea='Logs written by others teach only what they cover; acting on a lower confidence bound makes coverage of one good '
              'policy enough.',
         eqs=[r'\hat\pi=\arg\max_{\pi}\ \min_{f\in\mathcal F:\ \mathcal E(f,\pi;\mathcal D)\le\varepsilon_0}f(s_0,\pi)',
              r'J(\pi^\star)-\mathbb E\,J(\hat\pi_{\mathrm{LCB}})\lesssim\mathrm{poly}\big(\tfrac1{1-\gamma}\big)\sqrt{SC^\star/N}'],
         land='Pessimism at minimax rates (Rashidinejad, Zhu, Ma, Jiao & Russell 2022); Bellman-consistent pessimism (Xie et al. '
              '2021); adversarially trained actor–critic (Cheng et al. 2022); one trajectory (Yan et al. 2023); limits of '
              'realizability (Jia et al. 2024).'),
    dict(t='How many samples', color='brown',
         idea='Worst-case rates are settled and grow with the cube of the horizon; for a physical system the local '
              '(Hájek–Le Cam) answer is the useful one.',
         eqs=[r'N^\star(\varepsilon)\asymp\frac{|\mathcal S||\mathcal A|}{(1-\gamma)^{3}\varepsilon^{2}},\qquad N_{\text{Q-learning}}\asymp\frac{|\mathcal S||\mathcal A|}{(1-\gamma)^{4}\varepsilon^{2}}',
              r'\mathrm{Regret}(K)\lesssim\sqrt{SAH^3K},\qquad Z\sim\mathcal N\big(0,\nabla\psi\,I^{-1}\nabla\psi^{\top}\big)'],
         land='Minimax model-based planning for every accuracy (Li, Wei, Chi & Chen 2024); Q-learning one horizon factor worse '
              '(Li, Cai et al. 2024); online regret without burn-in (Zhang, Chen, Lee & Du 2025); a good representation is not '
              'sufficient (Du, Kakade, Wang & Yang 2020).'),
]


def build():
    td, pg, off = td_chain(), pg_chain(), offline()
    tex = Tex()
    svg, overlays = hero(td, pg, off, tex)
    html = build_page(tex, kicker='MACHINE LEARNING  ·  PARADIGM 3 OF 4  ·  LEARNING TO ACT FROM DATA',
                      title='Deep reinforcement learning theory: why it learns, how fast, what logs teach',
                      tags=[('CLASSICAL', 'tabular · asymptotic · worst case'),
                            ('NEW', 'finite-time theorems · pessimism from logs · local limits')],
                      hero_svg=svg, overlays=overlays, hero_y1=HERO_Y1, innov=INNOV, innov_box=(1584, 132, 784, 694),
                      cards=CARDS, card_top=HERO_Y1 + 12, card_h=408, card_gap=12)
    open('d3_deep_rl_theory.html', 'w').write(html)
    print('wrote d3_deep_rl_theory.html; TD error %.3f (bound %.3f), greedy %d pess %d, C* %.1f' %
          (td['e_td'], td['bound'], off['greedy'], off['pess'], off['C']))


if __name__ == '__main__':
    build()
