"""Diagram 1 of 4: robust Bayesian optimal design (learning where to measure when the noise is uncertain).
The pictures in the schematic are computed: a prior field m ~ N(0, A^-2) on the unit square, 64 candidate sensors, an
envelope design of 8 sensors chosen greedily, the PDE solution, the noise correlation, the posterior standard deviation
and the information spectrum of the chosen design."""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

from ml_common import PAL, ORDER, GOLD, INK, MUTED, Svg, Tex, ov, png_of, build_page, W

HERO_Y1 = 842
N = 64                      # grid of the field
RNG = np.random.default_rng(11)


# ---------------------------------------------------------------- the computed pictures
def prior_spectrum(gamma=0.012, delta=1.0):
    k = np.fft.fftfreq(N, d=1.0 / N)
    kx, ky = np.meshgrid(k, k, indexing='ij')
    a = gamma * (2 * np.pi) ** 2 * (kx ** 2 + ky ** 2) + delta        # symbol of A = -gamma Laplacian + delta
    return 1.0 / a                                                      # A^-1 (covariance A^-2 = (A^-1)^2)


def compute():
    s = prior_spectrum()
    w = RNG.standard_normal((N, N))
    m = np.real(np.fft.ifft2(np.fft.fft2(w) * s))
    cov = np.real(np.fft.ifft2(s ** 2))                                 # covariance function c(dx, dy), periodic
    sd = np.sqrt(cov[0, 0]); m /= np.sqrt(np.mean(m ** 2)); cov /= cov[0, 0]
    cand = [(i, j) for i in range(8) for j in range(8)]
    idx = [(4 + 8 * i, 4 + 8 * j) for (i, j) in cand]
    xy = np.array([((i + 0.5) / 8, (j + 0.5) / 8) for (i, j) in cand])

    def C(p, q):
        return cov[(p[0] - q[0]) % N, (p[1] - q[1]) % N]
    K = np.array([[C(p, q) for q in idx] for p in idx])
    D = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1))
    sig, ell = 0.35, 0.25                                               # upper bounds of the noise level and correlation length
    R = np.exp(-D / ell)
    # envelope (result 1): c = largest eigenvalue of R(l) - R(l_bar) over the allowed lengths, so Gbar >= Gamma(theta) for all theta
    c_env = max(np.linalg.eigvalsh(np.exp(-D / l) - R)[-1] for l in np.linspace(0.02, 0.25, 47))
    Gbar = sig ** 2 * (R + c_env * np.eye(64))

    def eig_of(S):
        KS, GS = K[np.ix_(S, S)], Gbar[np.ix_(S, S)]
        lam = np.linalg.eigvalsh(np.linalg.solve(GS, KS))
        return 0.5 * np.sum(np.log1p(np.maximum(lam, 0))), np.sort(np.maximum(lam, 0))[::-1]
    S = []
    for _ in range(8):                                                  # greedy envelope design, budget 8
        best = max((c for c in range(64) if c not in S), key=lambda c: eig_of(S + [c])[0])
        S.append(best)
    info, lam = eig_of(S)
    # posterior standard deviation on the grid for the chosen design under the envelope noise
    G = np.array([[cov[(a - p[0]) % N, (b - p[1]) % N] for p in [idx[i] for i in S]] for a in range(N) for b in range(N)])
    M = K[np.ix_(S, S)] + Gbar[np.ix_(S, S)]
    post_var = 1.0 - np.einsum('ij,ij->i', G, np.linalg.solve(M, G.T).T)
    post_sd = np.sqrt(np.maximum(post_var, 0)).reshape(N, N)
    # PDE: -div(e^m grad u) = 1 on the unit square, u = 0 on the boundary (5-point scheme, harmonic means)
    km = np.exp(0.9 * m)
    n = N - 2
    h = 1.0 / (N - 1)
    ii = lambda a, b: (a - 1) * n + (b - 1)
    rows, cols, vals = [], [], []
    for a in range(1, N - 1):
        for b in range(1, N - 1):
            diag = 0.0
            for (da, db) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                kf = 2 * km[a, b] * km[a + da, b + db] / (km[a, b] + km[a + da, b + db])
                diag += kf
                if 1 <= a + da <= N - 2 and 1 <= b + db <= N - 2:
                    rows.append(ii(a, b)); cols.append(ii(a + da, b + db)); vals.append(-kf)
            rows.append(ii(a, b)); cols.append(ii(a, b)); vals.append(diag)
    A = sp.csr_matrix((vals, (rows, cols)), shape=(n * n, n * n)) / h ** 2
    u = np.zeros((N, N)); u[1:-1, 1:-1] = spl.spsolve(A, np.ones(n * n)).reshape(n, n)
    return dict(m=m, post_sd=post_sd, u=u, km=km, xy=xy, S=S, lam=lam, info=info, R=R, sig=sig, ell=ell, c_env=c_env)


def pictures(d):
    import matplotlib.pyplot as plt  # noqa: F401  (png_of selects the backend)

    def field(ax):
        ax.imshow(d['m'].T, origin='lower', cmap='RdBu_r', vmin=-2.6, vmax=2.6, extent=(0, 1, 0, 1), interpolation='bicubic')
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    def post(ax):
        ax.imshow(d['post_sd'].T, origin='lower', cmap='magma', vmin=0.25, vmax=1.0, extent=(0, 1, 0, 1), interpolation='bicubic')
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    def pde(ax):
        x = np.linspace(0, 1, N)
        ax.imshow(np.log(d['km']).T, origin='lower', cmap='YlGnBu', vmin=-3, vmax=3, extent=(0, 1, 0, 1), interpolation='bicubic')
        ax.imshow(np.ones((2, 2)), cmap='Greys', vmin=0, vmax=8, extent=(1.08, 2.08, 0, 1))
        ax.contourf(x + 1.08, x, d['u'].T, levels=14, cmap='viridis', alpha=.9)
        ax.contour(x + 1.08, x, d['u'].T, levels=14, colors='white', linewidths=1.2)
        ax.set_xlim(0, 2.08); ax.set_ylim(0, 1); ax.set_aspect('auto')

    def corr(ax):
        ax.imshow(d['R'], cmap='Purples', vmin=0, vmax=1, interpolation='nearest')
    return dict(field=png_of(field, 380, 380), post=png_of(post, 300, 300), pde=png_of(pde, 300, 144), corr=png_of(corr, 150, 150))


# ---------------------------------------------------------------- the schematic
def hero(d, pics, tex):
    g = Svg()
    O = []
    blue, purple, green, teal, orange, amber, pink, brown = (PAL[c] for c in ORDER)
    # stage 1: the unknown field with candidate and chosen sensors
    g.panel(32, 136, 420, 528, 'THE UNKNOWN FIELD', 'blue', name='S1')
    X0, Y0, L = 52, 196, 380
    g.image(X0, Y0, L, L, pics['field'])
    for k, (x, y) in enumerate(d['xy']):
        px, py = X0 + x * L, Y0 + (1 - y) * L
        if k in d['S']:
            g.add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="15" fill="none" stroke="#ffd166" stroke-width="5" filter="url(#glow)"/>'
                  f'<circle cx="{px:.1f}" cy="{py:.1f}" r="8" fill="#ffb703" stroke="#1f2328" stroke-width="2.5"/>')
        else:
            g.add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#ffffff" stroke="#1f2328" stroke-width="2"/>')
    O.append(ov(242, 588, tex.text('prior $\\ \\mu_{\\mathrm{pr}}=\\mathcal{N}(m_{\\mathrm{pr}},\\,\\mathcal{A}^{-2})$'), 'eqlab', 'tc', style='font-size:20px'))
    O.append(ov(242, 630, tex.text('64 candidate sites · 8 chosen (gold)'), 'cap', 'tc'))
    # stage 2: physics and data
    g.panel(500, 136, 350, 330, 'PHYSICS + DATA', 'teal', name='S2')
    g.image(525, 194, 300, 144, pics['pde'])
    O.append(ov(600, 340, tex.text('conductivity $e^{m}$'), 'cap', 'tc', style='font-size:15px'))
    O.append(ov(752, 340, tex.text('solution $u$'), 'cap', 'tc', style='font-size:15px'))
    O.append(ov(675, 366, tex.eq('-\\nabla\\!\\cdot\\!\\left(e^{m}\\nabla u\\right)=f'), 'eqlab', 'tc'))
    O.append(ov(675, 414, tex.eq('\\mathbf{y}=\\mathcal{Q}(u)+\\boldsymbol{\\eta},\\ \\ \\boldsymbol{\\eta}\\sim\\mathcal{N}\\!\\left(0,\\Gamma(\\theta)\\right)'), 'eqbare', 'tc', style='font-size:21px'))
    # stage 3: nature picks the noise
    g.panel(500, 498, 350, 288, 'NATURE’S NOISE', 'pink', name='S3')
    g.image(520, 556, 150, 150, pics['corr'], rx=6)
    O.append(ov(595, 716, tex.text('noise correlation'), 'cap', 'tc', style='font-size:16px'))
    O.append(ov(686, 562, tex.eq('\\theta=(\\boldsymbol{\\sigma},\\ell)'), 'eqbare', 'tl', style='font-size:22px'))
    for k, line in enumerate(('noise levels and', 'correlation length,', 'chosen by nature', 'to hurt the design')):
        O.append(ov(686, 606 + 25 * k, tex.text(line), 'note', 'tl', style='font-size:16.5px'))
    O.append(ov(675, 744, tex.eq('\\Gamma(\\boldsymbol{\\sigma},\\ell)=D_{\\boldsymbol{\\sigma}}R(\\ell)D_{\\boldsymbol{\\sigma}}'), 'eqlab', 'tc', style='font-size:20px'))
    # stage 4: posterior and information
    g.panel(898, 136, 340, 528, 'POSTERIOR', 'purple', name='S4')
    g.image(918, 194, 300, 236, pics['post'])
    for k, (x, y) in enumerate(d['xy']):
        if k in d['S']:
            px, py = 918 + x * 300, 194 + (1 - y) * 236
            g.add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6" fill="#ffb703" stroke="#ffffff" stroke-width="2"/>')
    O.append(ov(1068, 438, tex.text('posterior s.d.: low near the sensors'), 'cap', 'tc', style='font-size:16.5px'))
    lam = d['lam']
    bx0, by0, bw, bh = 930, 472, 276, 92                                # eigenvalue bars, log scale
    lmax = np.log10(lam[0] * 1.2)
    lmin = -1.0
    g.add(f'<line x1="{bx0}" y1="{by0 + bh}" x2="{bx0 + bw}" y2="{by0 + bh}" stroke="#9aa3ad" stroke-width="2"/>')
    for i, l in enumerate(lam):
        hgt = bh * (np.log10(max(l, 10 ** lmin)) - lmin) / (lmax - lmin)
        g.add(f'<rect x="{bx0 + 8 + i * 33}" y="{by0 + bh - hgt:.1f}" width="24" height="{hgt:.1f}" rx="3" fill="{purple[0]}" opacity="{0.95 - 0.07 * i:.2f}"/>')
    O.append(ov(bx0 + bw, by0 - 4, tex.eq('\\lambda_n'), 'eqbare', 'tr', style='font-size:20px'))
    O.append(ov(1052, 574, tex.eq('\\mathrm{EIG}\\approx\\tfrac12\\sum_n\\log(1+\\lambda_n)'), 'eqlab', 'tc', style='font-size:21px'))
    # stage 5: the game
    g.panel(1286, 136, 274, 650, 'THE GAME', 'orange', name='S5')
    cx = 1423
    g.add(f'<circle cx="{cx}" cy="262" r="46" fill="{amber[2]}" stroke="{amber[0]}" stroke-width="5"/>'
          f'<circle cx="{cx}" cy="262" r="20" fill="none" stroke="{amber[1]}" stroke-width="4"/>'
          f'<path d="M{cx - 34},262 H{cx + 34} M{cx},228 V296" stroke="{amber[1]}" stroke-width="4"/>')
    g.text(cx, 336, 'DESIGNER', size=20, weight=800, fill=amber[1], anchor='middle', halo=False, ls=1.5)
    O.append(ov(cx, 346, tex.text('maximises over designs $\\boldsymbol{\\xi}$'), 'note', 'tc', style='font-size:16.5px'))
    g.add(f'<path d="M{cx},372 V396" stroke="{amber[1]}" stroke-width="5" marker-end="url(#{g.marker(amber[1])})"/>')
    O.append(ov(cx, 452, tex.eq('\\max_{\\boldsymbol{\\xi}}\\min_{\\theta}\\ \\mathcal{U}(\\boldsymbol{\\xi},\\theta)'), 'eqlab', 'tc', style='font-size:23px'))
    g.add(f'<path d="M{cx},556 V530" stroke="{pink[1]}" stroke-width="5" marker-end="url(#{g.marker(pink[1])})"/>')
    g.add(f'<g transform="translate({cx},630)"><ellipse cx="-16" cy="0" rx="34" ry="24" fill="{pink[2]}" stroke="{pink[0]}" stroke-width="4"/>'
          f'<ellipse cx="18" cy="-8" rx="30" ry="26" fill="{pink[2]}" stroke="{pink[0]}" stroke-width="4"/>'
          f'<path d="M2,8 L-8,30 L4,30 L-6,52" stroke="{pink[1]}" stroke-width="5" fill="none" stroke-linejoin="round"/></g>')
    g.text(cx, 718, 'NATURE', size=20, weight=800, fill=pink[1], anchor='middle', halo=False, ls=1.5)
    O.append(ov(cx, 728, tex.text('minimises over noise $\\theta$'), 'note', 'tc', style='font-size:16.5px'))
    # flows between the stages
    g.arrow('M452,300 H496', teal[0], 7)
    g.arrow('M675,498 V470', pink[0], 7)
    g.arrow('M850,300 H894', purple[0], 7)
    g.arrow('M1238,452 H1282', orange[0], 7)
    # inner loop: worst noise -> nature; outer loop: policy gradient back to the field
    g.arrow('M1286,722 H858', pink[1], 6, dash='14 9')
    O.append(ov(1070, 722, tex.text('inner loop: worst noise (L-BFGS-B)'), 'eqlab', 'cc', style='font-size:16.5px;font-weight:700;color:#9b2c5e'))
    g.arrow('M1423,786 V814 H242 V668', amber[1], 6, dash='14 9')
    O.append(ov(860, 814, tex.text('outer loop: a Bernoulli design policy learned by policy gradient (REINFORCE)'), 'eqlab', 'cc', style='font-size:16.5px;font-weight:700;color:#8f6200'))
    # numbered badges -> cards
    for (x, y, n) in ((424, 159, 1), (1212, 159, 2), (1214, 650, 3), (1534, 159, 4), (242, 740, 5), (424, 548, 6), (824, 521, 7), (824, 159, 8)):
        g.badge(x, y, n, ORDER[n - 1])
    return g.svg(HERO_Y1), O


# ---------------------------------------------------------------- content
INNOV = dict(
    kicker='INNOVATION', name='Certified robust design',
    sub='Three proven results that fix the weak points of the max–min design.',
    items=[
        dict(t='One ordinary design solve gives a certified robust design',
             eqs=[r'\mathcal U(\boldsymbol\xi_{\mathrm{env}};\overline\Gamma)\le\min_\theta\mathcal U(\boldsymbol\xi_{\mathrm{env}},\theta)\le V^\star\le\min_{\hat\theta}\max_{\boldsymbol\xi}\mathcal U(\boldsymbol\xi,\hat\theta)'],
             x='Information falls as the noise grows (Loewner order), so an envelope $\\overline\\Gamma\\succcurlyeq\\Gamma(\\theta)$ '
               'replaces the max–min loop by one design solve. Correlated noise can make two sensors worth one '
               '($\\sigma_1^\\star=\\sigma_2/\\rho$) and breaks submodularity.',
             kv='0.07%', kc='LOSS, ONE SOLVE'),
        dict(t='The usual utility is not the information, but a bound is',
             eqs=[r'\mathrm{EIG}(\boldsymbol\xi,\theta)\ \ge\ \mathbb{E}_{m\sim\mu_{\mathrm{pr}},\,\mathbf y\mid m}\Big[\log\frac{d\nu_{\mathbf y}}{d\mu_{\mathrm{pr}}}(m)\Big]\quad\forall\,\nu_{\mathbf y}\ll\mu_{\mathrm{pr}}'],
             x='The fixed-MAP utility, $\\mathrm{EIG}-\\tfrac12\\mathrm{tr}\\big(\\widetilde{\\mathcal H}(\\mathcal I+\\widetilde{\\mathcal H})^{-1}\\big)$, '
               'changed the best design in 25% of 300 random problems. This Barber–Agakov bound holds in function space for every '
               'design: optimise with Laplace, certify with the bound.',
             kv='25%', kc='DESIGNS CHANGE'),
        dict(t='Nature’s problem is convex: a saddle point exists',
             eqs=[r'\mathrm{EIG}(\boldsymbol\xi,\Gamma)=\tfrac12\big[\log\det(\Gamma_{\mathcal S}+K_{\mathcal S})-\log\det\Gamma_{\mathcal S}\big]\ \text{ is convex in }\Gamma'],
             x='With $\\Gamma(\\theta)=\\sum_k\\theta_k\\Gamma_k$ the worst noise is found globally and max–min equals min–max. '
               'For one goal quantity the robust design is a mixed-integer quadratic program with certified gaps; designs for a '
               'single noise model had 18% and 63% more worst-case variance.',
             kv='0.6442', kc='MAX–MIN = MIN–MAX'),
    ],
    foot='')

CARDS = [
    dict(t='An unknown that is a whole field', color='blue',
         idea='The parameter is a function $m(x)$. A Gaussian prior built from an elliptic operator keeps the design meaningful '
              'as the mesh is refined.',
         eqs=[r'\mathcal C_{\mathrm{pr}}=\mathcal A^{-2},\qquad \mathcal A=-\gamma\nabla\!\cdot\!(\mathbf K\nabla)+\delta',
              r'\frac{d\mu_{\mathrm{post}}^{\mathbf y}}{d\mu_{\mathrm{pr}}}\propto\exp\!\Big(-\tfrac12\big\|\mathbf y-\mathcal F(m)\big\|^2_{\Gamma(\theta)^{-1}}\Big)'],
         land='Base paper: Chowdhary, Attia & Alexanderian, SIAM J. Sci. Comput. 2026: robust design of nonlinear inverse '
              'problems in infinite dimensions; 64 candidates, budget 8, five outer iterations.'),
    dict(t='What a design is worth', color='purple',
         idea='The expected information gain: how far, on average, the data move the posterior away from the prior.',
         eqs=[r'\mathrm{EIG}(\boldsymbol\xi)=\mathbb E_{\mathbf y}\big[D_{\mathrm{KL}}(\mu^{\mathbf y}_{\mathrm{post}}\,\|\,\mu_{\mathrm{pr}})\big]',
              r'\mathrm{EIG}\approx\tfrac12\textstyle\sum_{n\le r}\log(1+\lambda_n)',
              r'\lambda_n=\mathrm{eig}\big(\mathcal C_{\mathrm{pr}}^{1/2}\mathbf J^{*}\Gamma^{-1}\mathbf J\,\mathcal C_{\mathrm{pr}}^{1/2}\big)'],
         land='Laplace is asymptotically exact even for a wrong model, with a sandwich covariance (Miller 2021); unbiased MCMC '
              'from coupled chains for checks (Jacob, O’Leary & Atchadé 2020).'),
    dict(t='Bounds you can optimise', color='green',
         idea='Variational and contrastive bounds turn the nested information into a stochastic-gradient objective.',
         eqs=[r'I_{\mathrm{ACE}}(\boldsymbol\xi,\phi,L)\le I(\boldsymbol\xi)\le I_{\mathrm{VNMC}}(\boldsymbol\xi,\phi,L)',
              r'I_{\mathrm{BA}}(\boldsymbol\xi,\phi)=\mathbb E\big[\log q_\phi(\theta\mid y)\big]+H[p(\theta)]\ \le\ I(\boldsymbol\xi)'],
         land='The bounds bracket the EIG; BA is ACE without contrastive samples (Foster et al. 2020). Unbiased multilevel '
              'gradients (Goda et al. 2022); transport-map errors become KL errors (Baptista et al. 2025); multimodal posteriors by '
              'Fisher–Rao flows (Chen et al. 2024).'),
    dict(t='Robust design is a game with nature', color='teal',
         idea='The designer maximises, nature picks the worst noise level and correlation. The solution is a local minimax point, '
              'not a Nash point.',
         eqs=[r'\max_{\boldsymbol\xi\in\{0,1\}^{N_d},\ \sum\xi_i=N_b}\ \min_{\theta\in\Theta}\ \mathcal U(\boldsymbol\xi,\theta)',
              r'\nabla^2_{yy}f\prec0,\quad \nabla^2_{xx}f-\nabla^2_{xy}f\,(\nabla^2_{yy}f)^{-1}\nabla^2_{yx}f\succ0'],
         land='Local minimax optimality and a gradient error floor $4\\ell\\epsilon$ (Jin, Netrapalli & Jordan 2020); mean robust '
              'optimisation with finite-sample guarantees (Wang, Becker, Van Parys & Stellato 2025).'),
    dict(t='A learned design policy', color='orange',
         idea='Relax the binary choice to a Bernoulli policy $\\mathbf p$ given the budget and climb its worst-case utility '
              '$\\mathcal U^{\\min}_k=\\min_\\theta\\mathcal U(\\boldsymbol\\xi_k,\\theta)$ by REINFORCE.',
         eqs=[r'\max_{\mathbf p\in[0,1]^{N_d}}\ \mathbb E_{\boldsymbol\xi\sim\mathbb P(\cdot\mid\mathbf p,\,Z=N_b)}\Big[\min_\theta\mathcal U(\boldsymbol\xi,\theta)\Big]',
              r'\nabla_{\mathbf p}\approx\tfrac{1}{N}\textstyle\sum_k\big(\mathcal U^{\min}_k-b\big)\,\nabla_{\mathbf p}\log\mathbb P(\boldsymbol\xi_k\mid\mathbf p,Z=N_b)'],
         land='Hidden convexity: stationary points of a policy can be global (Zhang, Koppel, Bedi, Szepesvári & Wang 2020); an '
              'Ising law over sensor subsets learned with the reconstruction (Sun, Dalca & Bouman 2020); semi-amortised design '
              'policies (Hedman et al. 2025).'),
    dict(t='Discrete designs with guarantees', color='amber',
         idea='Choosing $k$ of $N$ sensors is combinatorial; sampling and convex hulls certify the quality.',
         eqs=[r'\Pr(S)=\frac{\det(X_S^{\top}X_S+A)}{\det\big(\sum_i p_ix_ix_i^{\top}+A\big)}\prod_{i\in S}p_i\prod_{i\notin S}(1-p_i)',
              r'd_A(\Sigma)=\mathrm{tr}\big(\Sigma(\Sigma+A)^{-1}\big)\le d,\qquad \frac{(a_T^{\top}\beta)^2}{z(T)}\le t'],
         land='Regularised DPPs: $(1+\\epsilon)$-optimal designs with the effective dimension $d_A$ (Dereziński, Liang & Mahoney '
              '2020); rank-one convex hulls (Atamtürk & Gómez 2025); secant greedy where linear criteria fail (Otto & Rowley 2022).'),
    dict(t='When the model itself is wrong', color='pink',
         idea='Robustness has to cover model error and designs that depend on the data, not only the noise.',
         eqs=[r'P(\mathbf u,\theta)=\tfrac1Z\exp\big(-\beta\,L_{\mathrm{PDE}}(\mathbf u,\theta)\big)\,P(\theta)',
              r'v(X;D)=\tilde p_{X;D}(X)\,/\,p_X(X)'],
         land='A physics prior tempered by $\\beta$ for PDE model error (Amoudruz, Litvinov, Papadimitriou & Koumoutsakos 2026); '
              'conformal sets reweighted by $v$ stay valid when the design depends on the data (Fannjiang, Bates, Angelopoulos, '
              'Listgarten & Jordan 2022); an optimal-transport design criterion (Kerrigan, Naesseth & Rainforth 2026).'),
    dict(t='Making it scale', color='brown',
         idea='A design loop needs thousands of utility evaluations, about $4N_bN_{\\mathrm{SAA}}$ PDE solves each; randomised '
              'linear algebra and emulators make them cheap.',
         eqs=[r'\widehat{\mathrm{tr}}_{\mathrm{XN}}=\tfrac1m\textstyle\sum_i\big[\mathrm{tr}\,A\langle\Omega_{-i}\rangle+\omega_i^{*}(A-A\langle\Omega_{-i}\rangle)\omega_i\big]',
              r'\mathrm{DOFS}=\mathrm{tr}\,\big(S_AK^{\top}(KS_AK^{\top}+S_O)^{-1}K\big)'],
         land='XTrace: variance $O(1/m^2)$ with an error bar (Epperly, Tropp & Webber 2024); a reduced-rank Jacobian keeps 69% '
              'of the DOFS at ¼ of the cost (Nesser et al. 2021); emulators need $10^2$ runs instead of $10^5$ (Dunbar et al. 2022).'),
]


def build():
    d = compute()
    pics = pictures(d)
    tex = Tex()
    svg, overlays = hero(d, pics, tex)
    html = build_page(tex, kicker='MACHINE LEARNING  ·  PARADIGM 1 OF 4  ·  LEARNING WHERE TO MEASURE',
                      title='Robust Bayesian design: sensors that stay informative whatever the noise',
                      tags=[('CLASSICAL', 'one noise model · Laplace utility · greedy choice'),
                            ('NEW', 'a game with nature · a learned design policy · certified bounds')],
                      hero_svg=svg, overlays=overlays, hero_y1=HERO_Y1, innov=INNOV, innov_box=(1584, 132, 784, 694),
                      cards=CARDS, card_top=HERO_Y1 + 12, card_h=408, card_gap=12)
    open('d1_robust_design.html', 'w').write(html)
    print('wrote d1_robust_design.html; design', sorted(d['S']), 'info %.2f nat, c_env %.3f' % (d['info'], d['c_env']))


if __name__ == '__main__':
    build()
