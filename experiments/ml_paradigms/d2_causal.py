"""Diagram 2 of 4: causal generative modelling (learning hidden causes, interventions and counterfactuals).
The pictures are computed from the test bed of the source review: three latent processes in a known order (a source s,
then W, then X), observed as seven ions through a mixing G whose columns are stoichiometric signatures; baseline data and
two regimes that act as perfect interventions; the counterfactual of one sampled unit; a diffusion that noises the data."""
import numpy as np

from ml_common import PAL, ORDER, Svg, Tex, ov, png_of, build_page

HERO_Y1 = 842
RNG = np.random.default_rng(5)
IONS = ['Cl', 'Na', 'K', 'Ca', 'Mg', 'SO₄', 'HCO₃']
G = np.array([[565, 480, 10, 20, 108, 58, -2],                # source s (per unit fraction)
              [0, 0, 0, 1.0, 0.2, 0, 1.2],                     # W (per meq/L)
              [0, -1.0, -0.05, 0.60, 0.45, 0, 0]]).T           # X (per meq/L); G is 7 x 3
A = np.array([[0, 0, 0], [20, 0, 0], [120, -0.3, 0]])          # z = A z + eps (strictly lower triangular)
SD = np.array([0.01, 0.80, 0.50])
TAU = np.array([0.30, 0.30, 0.02, 0.10, 0.10, 0.05, 0.10])
DEV = np.array([6.78, 4.36, 0.05, 1.68, 2.05, 0.70, 0.70])    # deviation of the sampled unit (query Q1 of the source)


def sample(n, regime):
    A_, sd = A.copy(), SD.copy()
    if regime == 'source':
        sd[0] = 0.025
    elif regime == 'third':
        A_[2] = 0; sd[2] = 1.2
    eps = RNG.standard_normal((n, 3)) * sd
    z = np.linalg.solve(np.eye(3) - A_, eps.T).T
    return z @ G.T + RNG.standard_normal((n, 7)) * TAU


def compute():
    data = {r: sample(n, r) for r, n in (('base', 300), ('source', 150), ('third', 150))}
    L = np.linalg.inv(np.eye(3) - A)
    H = G @ L                                                   # total-effect signatures
    zs = np.linalg.pinv(H)[0] @ DEV                             # abduction of the source for the sampled unit
    change = (0.5 - 1) * zs * H[:, 0]                           # seawater fraction halved, other noises kept
    return dict(data=data, H=H, zs=zs, change=change)


def pictures(d):
    from matplotlib.patches import Ellipse

    def scatter(ax):
        cols = {'base': '#8a93a0', 'source': '#2a78d6', 'third': '#e4572e'}
        for r in ('base', 'third', 'source'):
            X = d['data'][r][:, [0, 3]]
            ax.scatter(X[:, 0], X[:, 1], s=26, c=cols[r], alpha=.55, edgecolors='none')
            C = np.cov(X.T); w, v = np.linalg.eigh(C)
            ang = np.degrees(np.arctan2(v[1, 1], v[0, 1]))
            ax.add_patch(Ellipse(X.mean(0), 2 * 2.2 * np.sqrt(w[1]), 2 * 2.2 * np.sqrt(w[0]), angle=ang, fill=False, lw=5, ec=cols[r]))
        hs = d['H'][:, 0]
        t = np.linspace(-0.05, 0.05, 2)
        ax.plot(t * hs[0], t * hs[3], color='#1b5fae', lw=3, ls=(0, (6, 4)))
        ax.set_xlim(-48, 48); ax.set_ylim(-9.5, 9.5)
        ax.axhline(0, color='#d0d7de', lw=2, zorder=0); ax.axvline(0, color='#d0d7de', lw=2, zorder=0)

    def mixing(ax):
        M = G / np.abs(G).max(0)
        ax.imshow(M, cmap='RdBu_r', vmin=-1.1, vmax=1.1, aspect='auto', interpolation='nearest')
        for i in range(7):
            for j in range(3):
                ax.add_patch(__import__('matplotlib.patches', fromlist=['Rectangle']).Rectangle((j - .5, i - .5), 1, 1, fill=False, ec='white', lw=4))

    def bars(ax):
        x = np.arange(7)
        cf = DEV + d['change']
        ax.bar(x - 0.2, DEV, 0.38, color='#5d35a3')
        ax.bar(x + 0.2, cf, 0.38, color='#c9b6ef')
        ax.axhline(0, color='#5b6573', lw=2)
        ax.set_xlim(-0.6, 6.6); ax.set_ylim(-0.3, 7.4)

    def diffusion(ax):
        X0 = np.vstack([d['data'][r][:, [0, 3]] for r in d['data']])
        X0 = (X0 - X0.mean(0)) / X0.std(0)
        Z = RNG.standard_normal(X0.shape)
        for k, t in enumerate((0.0, 0.25, 0.7, 2.5)):
            Xt = np.exp(-t) * X0 + np.sqrt(1 - np.exp(-2 * t)) * Z
            ax.scatter(Xt[:, 0] + 7.4 * k, Xt[:, 1], s=9, c='#7d4fc9' if t == 0 else ['#7d4fc9', '#8f74c9', '#a59ac2', '#8a93a0'][k],
                       alpha=.6, edgecolors='none')
        ax.set_xlim(-3.6, 3.6 + 7.4 * 3); ax.set_ylim(-3.6, 3.6)

    def transport(ax):
        a = d['data']['base'][:, [0, 3]]; b = d['data']['source'][:, [0, 3]]
        sa = (a - a.mean(0)) / np.array([20, 4]); sb = (b - b.mean(0)) / np.array([20, 4])
        ax.scatter(sa[:, 0] - 1.6, sa[:, 1], s=12, c='#8a93a0', alpha=.6, edgecolors='none')
        ax.scatter(sb[:, 0] + 1.6, sb[:, 1], s=12, c='#2a78d6', alpha=.6, edgecolors='none')
        ia = np.argsort(sa[:, 0])[::30][:6]; ib = np.argsort(sb[:, 0])[::15][:6]
        for i, j in zip(ia, ib):
            ax.annotate('', xy=(sb[j, 0] + 1.6, sb[j, 1]), xytext=(sa[i, 0] - 1.6, sa[i, 1]),
                        arrowprops=dict(arrowstyle='->', color='#11805a', lw=2.4, alpha=.85))
        ax.set_xlim(-3.2, 3.6); ax.set_ylim(-1.6, 1.6)
    return dict(scatter=png_of(scatter, 360, 268), mixing=png_of(mixing, 150, 252), bars=png_of(bars, 360, 170),
                diffusion=png_of(diffusion, 660, 156), transport=png_of(transport, 250, 150))


# ---------------------------------------------------------------- the schematic
def hero(d, pics, tex):
    g = Svg()
    O = []
    blue, purple, green, teal, orange, amber, pink, brown = (PAL[c] for c in ORDER)
    # S1: hidden causes (the latent SCM)
    g.panel(32, 136, 340, 380, 'HIDDEN CAUSES', 'blue', name='S1')
    nodes = {1: (110, 262), 2: (290, 262), 3: (200, 404)}
    names = {1: 'source', 2: 'process 2', 3: 'process 3'}
    for (a, b) in ((1, 2), (1, 3), (2, 3)):
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        v = np.array([x2 - x1, y2 - y1], float); v /= np.linalg.norm(v)
        g.arrow(f'M{x1 + 44 * v[0]:.0f},{y1 + 44 * v[1]:.0f} L{x2 - 50 * v[0]:.0f},{y2 - 50 * v[1]:.0f}', blue[1], 6)
    for k, (x, y) in nodes.items():
        g.add(f'<circle cx="{x}" cy="{y}" r="40" fill="{blue[2]}" stroke="{blue[0]}" stroke-width="5"/>')
        O.append(ov(x, y, tex.eq(f'z_{k}'), 'eqbare', 'cc', style='font-size:30px'))
        g.add(f'<circle cx="{x + 46}" cy="{y - 44}" r="14" fill="#ffffff" stroke="#8a93a0" stroke-width="2.5" stroke-dasharray="4 3"/>')
        O.append(ov(x + 46, y - 44, tex.eq(f'\\varepsilon_{k}'), 'eqbare', 'cc', style='font-size:17px'))
    O.append(ov(44, 196, tex.eq('do(\\cdot)'), 'chip', 'tl', style=f'background:{orange[0]};font-size:15px'))
    O.append(ov(200, 466, tex.eq('z_i=f_i(z_{\\mathrm{pa}(i)},\\varepsilon_i)'), 'eqlab', 'tc', style='font-size:21px'))
    O.append(ov(66, 312, tex.text('source'), 'cap', 'tc', style='font-size:15px'))
    # S2: mixing into data
    g.panel(404, 136, 238, 380, 'MIXING', 'purple', name='S2')
    g.image(470, 196, 150, 252, pics['mixing'], rx=6)
    for i, ion in enumerate(IONS):
        g.text(462, 196 + 36 * i + 24, ion, size=16, weight=700, fill='#3a4350', anchor='end', halo=False)
    for j in range(3):
        O.append(ov(470 + 25 + 50 * j, 448, tex.eq(f'z_{j + 1}'), 'eqbare', 'tc', style='font-size:17px'))
    g.add(f'<rect x="472" y="196" width="46" height="252" rx="4" fill="none" stroke="{amber[0]}" stroke-width="5"/>')
    O.append(ov(523, 478, tex.eq('\\mathbf x=\\mathbf x_0+G\\mathbf z+\\mathbf e'), 'eqlab', 'tc', style='font-size:19px'))
    # S3: data in regimes
    g.panel(674, 136, 400, 380, 'DATA IN THREE REGIMES', 'green', name='S3')
    g.image(694, 194, 360, 268, pics['scatter'])
    O.append(ov(874, 470, tex.text('ion 1 (Cl) against ion 4 (Ca), meq/L'), 'cap', 'tc', style='font-size:15px'))
    for k, (lab, col) in enumerate((('baseline', '#8a93a0'), ('do(source)', blue[0]), ('do(process 3)', orange[0]))):
        O.append(ov(706 + [0, 104, 228][k], 200, tex.text(lab), 'chip', 'tl', style=f'background:{col};font-size:13.5px'))
    O.append(ov(1040, 412, tex.eq('h_s'), 'eqbare', 'cc', style='font-size:20px;color:#1b5fae'))
    # S4: what if?
    g.panel(1106, 136, 450, 380, 'WHAT IF? A COUNTERFACTUAL', 'pink', name='S4')
    g.image(1126, 236, 410, 170, pics['bars'])
    for i, ion in enumerate(IONS):
        g.text(1126 + 410 * (i + 0.5 + 0.6) / 7.2, 424, ion, size=15, weight=700, fill='#3a4350', anchor='middle', halo=False)
    O.append(ov(1130, 194, tex.text('this unit'), 'chip', 'tl', style='background:#5d35a3;font-size:13.5px'))
    O.append(ov(1220, 194, tex.text('had its source been halved'), 'chip', 'tl', style='background:#b39ae6;font-size:13.5px'))
    O.append(ov(1331, 444, tex.eq('\\mathbf x^{\\mathrm{cf}}-\\mathbf x=(\\alpha-1)\\,z_s\\,h_s'), 'eqlab', 'tc', style='font-size:20px'))
    # S5: Pearl's ladder
    g.panel(32, 546, 400, 254, 'PEARL’S LADDER', 'teal', name='S5')
    rungs = [('3', 'IMAGINE', '\\mathbf x^{\\mathrm{cf}}\\ \\text{for this unit}', '#0b6d75'),
             ('2', 'DO', 'p(\\mathbf x\\mid do(z_j=c))', '#0f8f9a'),
             ('1', 'SEE', 'p(\\mathbf x)', '#5fb7bf')]
    for k, (n, word, tx, col) in enumerate(rungs):
        y = 606 + 62 * k
        g.add(f'<rect x="52" y="{y}" width="360" height="52" rx="10" fill="#ffffff" stroke="{col}" stroke-width="3"/>'
              f'<rect x="52" y="{y}" width="112" height="52" rx="10" fill="{col}"/>')
        g.text(108, y + 34, word, size=19, weight=800, fill='#ffffff', anchor='middle', halo=False, ls=1.5)
        O.append(ov(288, y + 26, tex.eq(tx), 'eqbare', 'cc', style='font-size:20px'))
    # S6: the generative engine
    g.panel(464, 546, 1092, 254, 'THE GENERATIVE ENGINE: DIFFUSION + TRANSPORT', 'amber', name='S6')
    g.image(484, 610, 660, 156, pics['diffusion'], border='#e5e9ef')
    for k, t in enumerate(('data', 't = 0.25', 't = 0.7', 'noise')):
        O.append(ov(484 + 165 * k + 82, 604, tex.text(t), 'cap', 'tc', style='font-size:14.5px'))
    g.arrow('M500,778 H1128', amber[1], 4)
    O.append(ov(814, 778, tex.text('noise forward · learn the score $\\nabla\\log p_t$ · generate backwards'), 'eqlab', 'cc', style='font-size:15px;font-weight:700;color:#8f6200'))
    g.image(1170, 610, 250, 150, pics['transport'], border='#e5e9ef')
    O.append(ov(1295, 604, tex.text('transport map between regimes'), 'cap', 'tc', style='font-size:14.5px'))
    O.append(ov(1488, 690, tex.eq('T=\\nabla\\varphi'), 'eqlab', 'cc', style='font-size:19px'))
    # flows
    g.arrow('M372,326 H400', purple[0], 7)
    g.arrow('M642,326 H670', green[0], 7)
    g.arrow('M1074,326 H1102', pink[0], 7)
    g.arrow('M874,516 V542', amber[1], 6)
    for (x, y, n) in ((348, 159, 1), (618, 159, 2), (1050, 159, 3), (1152, 776, 4), (720, 492, 5), (1532, 159, 6), (1532, 578, 7), (1488, 744, 8)):
        g.badge(x, y, n, ORDER[n - 1])
    return g.svg(HERO_Y1), O


INNOV = dict(
    kicker='INNOVATION', name='Known signatures replace interventions',
    sub='Example: three hidden processes behind the chemistry of a well, with their stoichiometric signatures partly known.',
    items=[
        dict(t='One scale for knowledge and experiments',
             eqs=[r'\dim(\text{fibre of equally good models})=(n-k)(n-1)'],
             x='Baseline data leave $n(n-1)$ free dimensions. Each known column of the mixing removes $n-1$, as much as one '
               'intervention: 6, 4, 2, 0 for three processes with 0–3 known signatures, at 20 random parameter values.',
             kv='6 → 0', kc='WITH 3 SIGNATURES'),
        dict(t='One regime on a source identifies its counterfactual',
             eqs=[r'\Sigma_k-\Sigma_0=(\sigma_k^2-1)\,h_sh_s^{\top},\qquad \mathbf x^{\mathrm{cf}}-\mathbf x=(\alpha-1)\,z_s\,h_s'],
             x='A period of different pumping identifies the chemistry of a well had its seawater fraction been halved, while four '
               'dimensions of the model stay free; median error 2.8% from simulated wells.',
             kv='2.8%', kc='MEDIAN ERROR'),
        dict(t='Identify the answer, not the model',
             eqs=[r'J_qN=0\ \Rightarrow\ q\ \text{is constant on the fibre},\qquad \text{share}=\frac{\|J_qN\|}{\|J_q\|}'],
             x='Identified queries have shares below $10^{-14}$, the others above $5\\cdot10^{-5}$. The exchange counterfactual needs '
               'a regime on exchange itself, and identified is not estimable: a rival optimum within the noise gave 169% error.',
             kv='10¹⁰', kc='SEPARATION'),
    ],
    foot='')

CARDS = [
    dict(t='Hidden causes: structural models', color='blue',
         idea='Latent causes follow their own mechanisms and the data mix them. An intervention replaces one mechanism and keeps '
              'the others.',
         eqs=[r'z_i=f_i(z_{\mathrm{pa}(i)},\varepsilon_i),\qquad \mathbf x=g(\mathbf z)+\mathbf e',
              r'p(\mathbf z\mid do(z_j=c))=\textstyle\prod_{i\ne j}p(z_i\mid z_{\mathrm{pa}(i)})\big|_{z_j=c}'],
         land='Causal hierarchy: data from a lower rung of the ladder do not fix the answers of a higher one. The field follows '
              'the survey of Komanduri, Wu, Wu & Chen (TMLR 2024).'),
    dict(t='Identifiability needs variability', color='purple',
         idea='With nonlinear mixing one condition cannot recover independent latents (Darmois); variation across regimes, '
              'domains or time restores them.',
         eqs=[r'p(\mathbf z\mid u)=\textstyle\prod_i\frac{Q_i(z_i)}{Z_i(u)}\exp\!\big(\sum_jT_{ij}(z_i)\lambda_{ij}(u)\big)',
              r'\Rightarrow\ \mathbf T(\mathbf z)=M\,\mathbf T(\hat{\mathbf z})+c,\qquad \hat{\mathbf z}_B=h_B(\mathbf z_{\pi(B)})'],
         land='iVAE (Khemakhem, Kingma, Monti & Hyvärinen 2020); additive decoders identify blocks (Lachapelle et al. 2023); '
              'graph layers from observational data (Welch, Zhang & Uhler 2024); partial views (Yao et al. 2024).'),
    dict(t='Interventions identify', color='green',
         idea='An intervention changes one mechanism, so it moves the data along a direction that reveals the mixing.',
         eqs=[r'\Theta_k=H^{\top}B_k^{\top}B_kH,\qquad B_k=\Omega_k^{-1/2}(I-A_k)',
              r'B_k-B_0\ne0\ \text{ only in the row of the intervened latent}'],
         land='One intervention per latent is sufficient and in the worst case necessary (Squires, Seigal, Bhate & Uhler 2023); '
              'soft ones leave ancestors mixed (Zhang et al. 2023); unknown targets need pairs (von Kügelgen et al. 2023) or '
              'graph conditions (Jiang & Aragam 2023).'),
    dict(t='Scores reveal the mixing', color='teal',
         idea='Under an intervention the score of the latent law changes only in the intervened variable and its parents.',
         eqs=[r'\nabla_{\mathbf z}\ln p^k-\nabla_{\mathbf z}\ln p^0=\nabla_{\mathbf z}\ln\frac{q_i^k(z_i\mid z_{\mathrm{pa}(i)})}{q_i^0(z_i\mid z_{\mathrm{pa}(i)})}',
              r'\nabla_{\mathbf x}\ln p^k_X-\nabla_{\mathbf x}\ln p^0_X=J_g^{-\top}\big(\nabla_{\mathbf z}\ln p^k-\nabla_{\mathbf z}\ln p^0\big)'],
         land='Score-based causal representation learning for linear and general mixing (Varıcı, Acartürk, Shanmugam, Kumar & '
              'Tajer 2025): the same score functions that diffusion models learn.'),
    dict(t='Time and hidden regimes', color='orange',
         idea='Latents independent given the past, with transitions that vary enough, are identified; a hidden regime can be '
              'inferred first and then used as the auxiliary variable.',
         eqs=[r'p(\mathbf z_t\mid\mathbf z_{t-1})=\textstyle\prod_ip(z_{t,i}\mid\mathbf z_{t-1},u_t)',
              r'\lfloor\log_2 n\rfloor+2\ \text{distinct actions identify } n\ \text{latents}'],
         land='BISCUIT: binary interactions of an agent with the system (Lippe et al. 2023); unknown nonstationarity as a hidden '
              'Markov regime (Song et al. 2023). Monitoring records with operating decisions are such sequences.'),
    dict(t='Counterfactuals for one unit', color='amber',
         idea='Abduction recovers the unit’s own noise, action changes a mechanism, prediction replays the model.',
         eqs=[r'\varepsilon_i=f_i^{-1}(x_i;\mathrm{pa}_i),\qquad x_i^{\mathrm{cf}}=f_i(\varepsilon_i;\mathrm{pa}_i^{\mathrm{cf}})',
              r'\mathbf x^{\mathrm{cf}}=\nabla\varphi(\mathbf x),\qquad (\nabla\varphi)_{\#}\,p(\mathbf x\mid\mathrm{pa})=p(\mathbf x\mid\mathrm{pa}^{\prime})'],
         land='Bijective models identify counterfactuals (Nasr-Esfahany, Alizadeh & Shah 2023); dynamic optimal transport (De '
              'Sousa Ribeiro, Santhirasekaram & Glocker 2025); fitting data does not fix the edits (Pan & Bareinboim 2024); '
              'bounds under hidden confounding (Jesson, Mindermann, Gal & Shalit 2021).'),
    dict(t='The generative engine: diffusion', color='pink',
         idea='Noise the data with an Ornstein–Uhlenbeck process and learn its score to run it backwards.',
         eqs=[r'd\mathbf X_t=-\mathbf X_t\,dt+\sqrt2\,d\mathbf W_t',
              r'd\mathbf Y_t=\big(\mathbf Y_t+2\nabla\ln p_{T-t}(\mathbf Y_t)\big)dt+\sqrt2\,d\overline{\mathbf W}_t'],
         land='KL bounds nearly linear in the dimension (Benton, De Bortoli, Doucet & Deligiannidis 2024), linear in the '
              'intrinsic dimension (Potaptchik, Azangulov & Deligiannidis 2025); denoising Markov models (Benton et al. 2024); '
              'Riemannian score models (De Bortoli et al. 2022).'),
    dict(t='Transport, rates and honest scores', color='brown',
         idea='Entropic optimal transport compares regimes at a rate free of the dimension; recovered latents are scored by '
              'matching them to the truth.',
         eqs=[r'\mathrm{OT}_\varepsilon(\mu,\nu)=\min_{\pi\in\Pi(\mu,\nu)}\textstyle\int c\,d\pi+\varepsilon\,\mathrm{KL}(\pi\,\|\,\mu\otimes\nu)',
              r'\mathbb E\big|\mathrm{OT}_\varepsilon(\hat\mu_n,\hat\nu_n)-\mathrm{OT}_\varepsilon(\mu,\nu)\big|\lesssim C_\varepsilon/\sqrt n'],
         land='Dimension-free sample complexity of entropic transport (Rigollet & Stromme 2025); the mean correlation '
              'coefficient after matching and the structural Hamming distance as benchmarks.'),
]


def build():
    d = compute()
    pics = pictures(d)
    tex = Tex()
    svg, overlays = hero(d, pics, tex)
    html = build_page(tex, kicker='MACHINE LEARNING  ·  PARADIGM 2 OF 4  ·  LEARNING CAUSES, NOT CORRELATIONS',
                      title='Causal generative modelling: hidden causes, interventions and “what if”',
                      tags=[('CLASSICAL', 'fit p(x) · factors up to a rotation · one condition'),
                            ('NEW', 'latent causal model · regimes as interventions · counterfactuals')],
                      hero_svg=svg, overlays=overlays, hero_y1=HERO_Y1, innov=INNOV, innov_box=(1584, 132, 784, 694),
                      cards=CARDS, card_top=HERO_Y1 + 12, card_h=408, card_gap=12)
    open('d2_causal_generative.html', 'w').write(html)
    print('wrote d2_causal_generative.html; z_s = %.4f; change =' % d['zs'], np.round(d['change'], 2))


if __name__ == '__main__':
    build()
