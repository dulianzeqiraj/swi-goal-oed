"""CERTAIN-COAST (NATO SPS proposal): mathematical state of the art for the four questions a stochastic coastal-aquifer
model must answer before its warnings can be trusted: the random forcing, the boundaries, the initial state and the
propagation of uncertainty. English, equations as native Word math (OMML), references checked in Crossref.

The numbers in Tables 2-4 are computed in closed form and checked numerically (scipy): the Gamma law of shot noise,
the slowest eigenvalue of a strip with a conductance boundary, and the correlation of block means of an
Ornstein-Uhlenbeck process. They are illustrative, not results at Fushe-Kuqe.

usage: python build_math_sota.py OUT.docx"""
import json
import os
import re
import sys
import tempfile

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', '..', 'ml_paradigms', 'word'))
from build_sota import run, para, heading, table  # noqa: E402
from build_methodology import Eqs, mrich, display_eq  # noqa: E402
from build_annex import field_run, two_columns  # noqa: E402
import omml  # noqa: E402

TITLE = ('Mathematical state of the art: random forcing, boundaries, initial state and propagation of uncertainty '
         'in a stochastic coastal aquifer')
SIZE = 10

from math_sota_refs import CITE, REFERENCES  # noqa: E402


def c(key):
    return CITE[key]


BL = [
    ('p', 'A model that issues warnings for a coastal aquifer must answer four mathematical questions before its '
          'probabilities can be trusted. Is the model, driven by random rain, sea level and pumping, well posed? How are '
          'the sea and the rivers represented when they are themselves uncertain? How much does the unknown initial '
          'state matter? And how are the probabilities of rare events computed at an affordable cost? This note '
          'summarises how the literature answers each question, with emphasis on 2023–2026, states what remains open, '
          'and gives the rule by which CERTAIN-COAST chooses a method for each question at Fushë-Kuqe (WP2, WP3). The '
          'numbers in Tables 2–4 come from closed-form results checked numerically; they are illustrative, not results '
          'at the site.'),
    ('cap', 'Table 1. The four questions, the mathematical tool that answers each, the number that decides the method, '
            'and the point that remains open.'),
    ('table', ['Question', 'Mathematical tool', 'Deciding number', 'Open point'],
     [['1. Random forcing', 'Pathwise and entropy solutions; shot-noise law of storm recharge', 'Π = λτ, storms per '
       'aquifer memory', 'Which law of the forcing to use'],
      ['2. Boundaries', 'Conductance (Robin) condition with coloured noise; boundary corrections in the state vector',
       'Γ = CL/T, boundary conductance number', 'Three-dimensional variable-density aquifer with a moving interface'],
      ['3. Initial state', 'Modal memory; ensemble Kalman filter; 4D-Var; Bayesian inversion in function space',
       't/τ₁, record length over aquifer memory', 'Assimilation theory for non-additive, non-Gaussian forcing'],
      ['4. Propagation', 'Multilevel Monte Carlo with smoothed indicators and surrogate control variates',
       'β − γ, variance decay against cost growth', 'Rates for threshold probabilities of coupled models']],
     [2.6, 6.2, 4.0, 4.6], 8.6),

    ('h', '1. The equations'),
    ('p', 'The water table $h$ of an unconfined coastal aquifer obeys the Boussinesq equation, and the unsaturated zone '
          'the Richards equation:'),
    ('eq', 'bous', r'S_y \frac{\partial h}{\partial t} = \nabla\cdot\left(K h \nabla h\right) + R(x,t) - Q(x,t)'),
    ('eq', 'rich', r'\frac{\partial \theta(\psi)}{\partial t} = \nabla\cdot\left(K(\psi)\nabla(\psi+z)\right) + R(x,t)'),
    ('p', 'Both are degenerate: the diffusion coefficient $Kh$ vanishes where the aquifer runs dry, and $K(\\psi)$ '
          'collapses in dry soil. With $u = h$ and $m = 2$, the Boussinesq equation is a porous-medium equation, and with '
          'random forcing it reads'),
    ('eq', 'pme', r'du = \Delta\left(u^{m}\right) dt + \sigma(u)\, dW_t + R\, dt, \quad m>1'),
    ('p', 'where $W$ is a noise in time: white, with long memory, or rough. The sea enters at the coast and the rivers '
          'along their beds; the interface between fresh and salt water is a moving boundary.'),

    ('h', '2. Random forcing'),
    ('h2', '2.1 Existence, uniqueness and stability'),
    ('p', 'For noise that is additive or linear in $u$, the substitution $u = e^{\\mu W_t} v$ turns the stochastic '
          'equation into a porous-medium equation with random coefficients, which can be solved path by path. '
          'Pathwise well-posedness is proved for stochastic porous-medium and fast-diffusion equations with conservative '
          'noise {@A1path}, and on bounded domains with Dirichlet data, where the solution depends continuously on the '
          'driving noise {@A1clini}. For nonlinear noise that is correlated in space, stochastic kinetic solutions give '
          'well-posedness {@A1entropy}. For a given path of the forcing, the porous-medium operator is accretive in $L^1$, '
          'so two solutions driven by the same forcing contract {@A1stab}:'),
    ('eq', 'l1', r'\left\| u_1(t)-u_2(t)\right\|_{L^1} \le \left\| u_1(0)-u_2(0)\right\|_{L^1},'),
    ('p', 'Together with the continuity in the driving noise, this means that an error in the forcing has a controlled '
          'effect on the heads. For forcing rougher than Brownian motion, Wong–Zakai regularisation and splitting give '
          'fully discrete schemes with error bounds {@A3}.'),
    ('h2', '2.2 Heads that stay nonnegative'),
    ('p', 'A finite-volume discretisation with two-point fluxes and implicit time steps gives an M-matrix, and the '
          'discrete maximum principle then keeps $h \\ge 0$ in cells that dry out. For multiplicative noise, splitting '
          'the noise step from the diffusion step and solving the noise step exactly preserves positivity {@A2split}; '
          'finite-element schemes that keep the stochastic porous-medium equation nonnegative converge {@A2fem}, and '
          'convergent schemes now cover singular-degenerate stochastic equations that include it {@A2deg}.'),
    ('h2', '2.3 The law of the forcing'),
    ('p', 'What the theory does not decide is the law of the forcing. Rain falls as storms: at the scale of an aquifer, '
          'recharge is a marked Poisson process with storm rate $\\lambda$ and storm sizes $Y_i$ of mean $\\mu$, written '
          'as the rise in head they cause. If the aquifer drains like a linear reservoir with response time $\\tau$, the '
          'head above its drainage level is shot noise:'),
    ('eq', 'shot', r'h(t) = \sum_{t_i \le t} Y_i\, e^{-(t-t_i)/\tau}'),
    ('p', 'For exponential storm sizes its stationary law is exactly a Gamma law, with shape $\\Pi = \\lambda\\tau$, '
          'the number of storms within one aquifer memory, and scale $\\mu$ (the Laplace transform of [[shot]] is '
          '$(1+s\\mu)^{-\\lambda\\tau}$; the same law describes soil moisture in ' + 'Rodriguez-Iturbe et al., 1999' +
          '{@A4}):'),
    ('eq', 'gamma', r'h \sim \text{Gamma}(\Pi,\mu), \quad \mathbb{E}[h]=\Pi\mu, \quad \text{Var}[h]=\Pi\mu^{2}, '
                    r'\quad \text{skewness}=2/\sqrt{\Pi}'),
    ('p', 'A Gaussian with the same mean and variance is exact only as $\\Pi \\to \\infty$. Table 2 shows how far it is '
          'from the exact law in the tails that warnings use. The Gaussian underestimates high levels by an order of '
          'magnitude when few storms fall within one aquifer memory, and still by a factor of two at $\\Pi = 100$; it '
          'overstates low levels, which matter for pumping limits. Means and variances are right at any $\\Pi$; tails '
          'are not. A search of the 2023–2026 literature for this note found no study that compares the two laws in '
          'the tails of groundwater levels.'),
    ('cap', 'Table 2. Tail probabilities of the head under the exact Gamma law and under a Gaussian with the same mean '
            'and variance (sd: standard deviation).'),
    ('table', ['Π = λτ', 'P[h > mean + 3 sd], exact', 'Gaussian', 'Ratio', 'P[h < mean − 2 sd], exact', 'Gaussian'],
     [['1', '1.83%', '0.135%', '13.6', '0', '2.28%'],
      ['2', '1.41%', '0.135%', '10.4', '0', '2.28%'],
      ['10', '0.67%', '0.135%', '5.0', '0.46%', '2.28%'],
      ['100', '0.28%', '0.135%', '2.0', '1.71%', '2.28%']],
     [2.0, 3.6, 2.2, 1.8, 3.8, 2.2], 8.6),

    ('h', '3. Boundaries'),
    ('h2', '3.1 The sea and the rivers as conductance boundaries'),
    ('p', 'The sea at the coast and the rivers along their beds are written as a Robin (conductance) condition,'),
    ('eq', 'robin', r'-T\,\frac{\partial h}{\partial n} = C\left(h - H_b(t)\right), \quad H_b(t) = \bar H + \delta + \xi(t),'),
    ('p', 'with transmissivity $T$, boundary conductance $C$, mean stage $\\bar H$, an unknown datum correction '
          '$\\delta$ and a fluctuation $\\xi$. The problem is well posed for $C \\ge 0$, because the bilinear form is '
          'coercive (Lax–Milgram), and the number $\\Gamma = CL/T$ decides how the boundary acts: for $\\Gamma \\to '
          '\\infty$ it is a fixed head, for $\\Gamma \\to 0$ a no-flow boundary. A stochastic porous-medium equation '
          'with Robin boundary conditions, gravity-driven infiltration and multiplicative noise is treated in {@A6robin}, '
          'and a rule for when boundary uncertainty must enter the estimation of aquifer properties is given in '
          '{@A6when}. For a strip of length $L$ '
          'with a conductance boundary at the coast and a divide inland, the slowest decay rate solves '
          '$k_1 L \\tan(k_1 L) = \\Gamma$, and the aquifer memory is $\\tau_1 = S/(T k_1^2)$. Table 3 shows that a sea '
          'or river boundary behaves as a fixed head within 2% only for $\\Gamma \\ge 100$.'),
    ('cap', 'Table 3. Memory of the aquifer with a conductance boundary, relative to a fixed head at the coast.'),
    ('table', ['Γ = CL/T', 'k₁L', 'τ₁ relative to a fixed head'],
     [['0.1', '0.311', '25.5'], ['1', '0.860', '3.33'], ['10', '1.429', '1.21'], ['100', '1.555', '1.02'],
      ['∞', 'π/2', '1']],
     [3.0, 3.0, 5.0], 8.6),
    ('p', 'White noise imposed directly as fixed-head data is too rough for classical solutions. The fluctuation of '
          'the sea is therefore taken as a coloured (Ornstein–Uhlenbeck) process, with correlation time $\\tau_\\xi$ '
          'and intensity $\\sigma_\\xi$ estimated from the tide gauge:'),
    ('eq', 'ou', r'd\xi = -\frac{\xi}{\tau_\xi}\,dt + \sigma_\xi\, dW_t'),
    ('h2', '3.2 The interface between fresh and salt water'),
    ('p', 'In the sharp-interface approximation, the depth of the interface below sea level is '
          '$\\zeta = \\rho_f h/(\\rho_s - \\rho_f) \\approx 40\\,h$ (Ghyben–Herzberg), and a single potential turns the '
          'regional interface problem into one equation over the whole aquifer (Strack, 1976). With random fluxes the '
          'interface is a stochastic free boundary of Stefan type. Such problems have local solutions after a '
          'transformation to a fixed domain {@A5local}, and maximal solutions up to stopping times {@A5max}; none of '
          'them yet covers a variable-density aquifer.'),
    ('h2', '3.3 A wrong boundary is read as wrong recharge'),
    ('p', 'Write the heads as $y = G_R r + G_B b + e$, with $r$ the recharge and $b$ the boundary data. If $b$ is fixed '
          'with an error $\\delta b$, the least-squares estimate of the recharge is shifted by'),
    ('eq', 'bias', r'\mathbb{E}[\hat r] - r = \left(G_R^{\top} G_R\right)^{-1} G_R^{\top} G_B\, \delta b,'),
    ('p', 'so a boundary error is read as a recharge error; a related non-uniqueness lets a wrong recharge field fit the heads {@A6bias}. The remedy is to put the datum and stage '
          'corrections into the state vector, $z = (h, r, \\delta_{sea}, \\delta_{river})$, and estimate them with the '
          'heads, as ensemble history matching already does for sea-level and recharge ensembles of an island aquifer '
          '{@A6da}. The boundary and recharge uncertainty that remains then sets the floor of the predictive '
          'uncertainty, which more head data alone do not remove.'),

    ('h', '4. Initial state'),
    ('h2', '4.1 How long the aquifer remembers'),
    ('p', 'In the linearised aquifer, the head is a sum of decaying modes plus the response to the forcing:'),
    ('eq', 'modes', r'h(x,t) = \sum_{k\ge 1} a_k\, e^{-t/\tau_k}\, \varphi_k(x) + h_{f}(x,t), \quad '
                    r'\tau_1 = \frac{4 S L^2}{\pi^2 T},'),
    ('p', 'for a fixed head at the coast and a divide at distance $L$. An error in the initial state decays as '
          '$e^{-t/\\tau_1}$, so a spin-up of $\\tau_1 \\ln 10 \\approx 2.3\\,\\tau_1$ leaves 10% of it. The same time '
          'scale limits what data can say about the initial state: with observation noise of intensity $\\sigma^2$, '
          'the Fisher information on $a_1$ from data after time $t$ is'),
    ('eq', 'fisher', r'I_{a_1}(t) = \frac{1}{\sigma^2}\int_t^{\infty} e^{-2s/\tau_1}\,ds = \frac{\tau_1}{2\sigma^2}\, '
                     r'e^{-2t/\tau_1},'),
    ('p', 'so the initial state is forgotten, and becomes unidentifiable, on the same time scale. Either the model is '
          'spun up for $2.3\\,\\tau_1$, or the initial heads are estimated from the first part of the record, shorter '
          'than $\\tau_1$.'),
    ('h2', '4.2 Ensemble Kalman filtering'),
    ('p', 'The ensemble Kalman filter (Evensen, 1994) updates each member of the ensemble with'),
    ('eq', 'enkf', r'x^{a} = x^{f} + K\left(y - H x^{f}\right), \quad K = P^{f} H^{\top}\left(H P^{f} H^{\top} + R\right)^{-1}.'),
    ('p', 'It is exact in the linear-Gaussian case as the ensemble grows, and recent mean-field analysis bounds its '
          'error when the forecast is close to Gaussian or the dynamics close to linear {@B1}, within a mean-field '
          'framework for ensemble Kalman methods {@B1frame}; non-asymptotic analysis explains when a small ensemble '
          'suffices {@B1small}. In practice its accuracy is '
          'monitored through the skewness and kurtosis of the forecast ensemble; transport-map filters extend it when '
          'the forecast is far from Gaussian (Spantini et al., 2022).'),
    ('h2', '4.3 Variational estimation'),
    ('p', '4D-Var estimates the initial state by minimising'),
    ('eq', 'var', r'J(x_0) = \tfrac{1}{2}\left\| x_0 - x_b\right\|^2_{B^{-1}} + \tfrac{1}{2}\sum_k \left\| y_k - H\, '
                  r'\mathcal{M}_k(x_0)\right\|^2_{R^{-1}},'),
    ('p', 'with the gradient from the adjoint model. For a nonlinear aquifer model, the Gauss–Newton iteration needs '
          'safeguards: plain Gauss–Newton may fail to converge from a poor starting point, line-search and '
          'regularised variants restore convergence {@B2}, and Levenberg–Marquardt methods with inexact steps converge '
          'globally {@B2lm}.'),
    ('h2', '4.4 Bayesian inversion in function space'),
    ('p', 'Bayesian inversion in function space (Stuart, 2010) gives posteriors for initial heads and parameters that '
          'do not degrade as the mesh is refined; Laplace approximations with low-rank or hierarchical Hessians make '
          'them scalable {@B3}, and goal-oriented real-time Bayesian inference now serves early warning, for tsunamis '
          '{@B3warn}.'),

    ('h', '5. Propagation of uncertainty'),
    ('h2', '5.1 Multilevel Monte Carlo'),
    ('p', 'The probabilities that warnings need, of heads below a pumping threshold or of chloride above a limit, are '
          'expectations of functionals $P$ of the solution. Multilevel Monte Carlo writes the expectation on the finest '
          'mesh as a telescoping sum over meshes $l = 0, \\dots, L$ (Giles, 2008):'),
    ('eq', 'mlmc', r'\mathbb{E}[P_L] = \mathbb{E}[P_0] + \sum_{l=1}^{L} \mathbb{E}\left[P_l - P_{l-1}\right].'),
    ('p', 'If the weak error decays as $2^{-\\alpha l}$, the variance of the corrections as $2^{-\\beta l}$ and the cost '
          'of one sample grows as $2^{\\gamma l}$, the cost of a root-mean-square accuracy $\\varepsilon$ is '
          '(Giles, 2015)'),
    ('eq', 'cost', r'\text{Cost}(\varepsilon) \propto \begin{cases} \varepsilon^{-2}, & \beta>\gamma, \\ '
                   r'\varepsilon^{-2}\left(\log\varepsilon\right)^{2}, & \beta=\gamma, \\ '
                   r'\varepsilon^{-2-(\gamma-\beta)/\alpha}, & \beta<\gamma, \end{cases}'),
    ('p', 'so when the corrections shrink faster than the cost grows, a probability on the finest mesh costs as much, '
          'in order, as an average of independent numbers {@B4}.'),
    ('h2', '5.2 Probabilities of crossing a threshold'),
    ('p', 'For a probability the functional is an indicator, $P = \\mathbf{1}\\{h < h_{\\min}\\}$, which is '
          'discontinuous and lowers $\\beta$. Smoothing the indicator, by a conditional expectation over the last step '
          'or by a kernel, restores the rate {@B4smooth}. Surrogates enter as control variates on the coarse levels '
          '{@B5}.'),
    ('h2', '5.3 Model error apart from forcing'),
    ('p', 'Model error is kept apart from the forcing by writing $x_{k+1} = \\mathcal{M}(x_k, r_k) + \\eta_k$, with '
          '$\\eta_k$ estimated apart from the recharge $r_k$; otherwise the filter attributes model bias to the rain. '
          'Weak-constraint 4D-Var estimates $\\eta_k$ as part of the control variable {@B6}, and its covariance can be '
          'chosen as a regularisation parameter {@B6cov}; but model error and initial state separate only under '
          'specific conditions {@B6limit}, and in hydrology rainfall and structural errors can be poorly identifiable '
          '{@B6hydro}.'),
    ('h2', '5.4 Sampling and averaging'),
    ('p', 'Averaging a process with correlation time $\\tau$ over intervals of length $\\Delta$ changes its '
          'correlation. For an Ornstein–Uhlenbeck process with variance $\\sigma^2$, the block means satisfy'),
    ('eq', 'avg', r'\text{Var}(\bar A) = 2\sigma^2 \frac{\tau}{\Delta}\left[1-\frac{\tau}{\Delta}\left(1-e^{-\Delta/\tau}'
                  r'\right)\right], \quad \text{Cov}(\bar A_k,\bar A_{k+1}) = \sigma^2 \frac{\tau^2}{\Delta^2}\left(1-'
                  r'e^{-\Delta/\tau}\right)^2,'),
    ('p', 'so the lag-one correlation of monthly means is not $e^{-\\Delta/\\tau}$, and a response time read from monthly '
          'means is biased upwards (Table 4). The bias of estimators for a time-integrated Ornstein–Uhlenbeck process '
          'is derived in econometrics {@B7}, and averaging recessions is known to bias recession parameters in '
          'hydrology {@B7hydro}, but we found no study that quantifies the effect on groundwater response times. '
          'Daily logger data avoid the bias.'),
    ('cap', 'Table 4. Response time of the aquifer estimated from monthly means (Δ = 30 days) against the true value.'),
    ('table', ['True response time τ (days)', 'Estimated from monthly means (days)', 'Overestimate'],
     [['2', '9.0', '4.5 ×'], ['5', '13.0', '2.6 ×'], ['10', '19.8', '2.0 ×'], ['30', '49.1', '1.6 ×'],
      ['90', '138.9', '1.5 ×']],
     [5.0, 5.4, 3.0], 8.6),

    ('h', '6. What is new: four numbers that choose the method'),
    ('p', 'The literature answers each question separately. CERTAIN-COAST joins the answers through four dimensionless '
          'numbers computed from the records of Fushë-Kuqe before any simulation (Table 5). Each number selects the '
          'method for one question, so the workflow is fixed by data rather than by habit, and each approximation comes '
          'with a stated error: the exact Gamma law of Section 2.3 is the reference against which the Gaussian forcing '
          'is checked (Table 2), and the averaging bias of Section 5.4 is the reason the network of WP4 records daily '
          '(Table 4). The individual results are known; their use as one decision map for a coastal aquifer is the '
          'contribution.'),
    ('cap', 'Table 5. The decision map: four numbers, computed from data, that choose the method for each question.'),
    ('table', ['Number', 'Computed from', 'Rule and method chosen'],
     [['Π = λτ', 'Storm rate from the rain gauge; response time from head recessions', 'Π ≥ 20 and only means and '
       'variances needed: Gaussian recharge noise. Otherwise shot-noise forcing; tail probabilities always from the '
       'exact Gamma law.'],
      ['Γ = CL/T', 'Conductance of the river beds and of the coast; transmissivity', 'Γ ≥ 100: fixed head with an '
       'uncertain datum. Γ ≤ 0.1: no flow. Between: conductance condition with the stage correction in the state '
       'vector.'],
      ['t/τ₁', 'Storage, transmissivity and length of the model; length of the record', 'Record before the forecast '
       '≥ 2.3 τ₁: spin-up. Otherwise: initial heads estimated from the first part of the record.'],
      ['β − γ', 'Pilot runs on three meshes', 'β > γ: standard multilevel Monte Carlo. β ≤ γ: smoothed indicators and '
       'surrogate control variates.']],
     [2.2, 5.6, 9.6], 8.6),

    ('h', '7. What remains open'),
    ('p', 'No well-posedness theorem covers a three-dimensional, variable-density coastal aquifer with random recharge, '
          'random sea level and a moving interface at once; most results are one-dimensional, periodic or with '
          'homogeneous Dirichlet conditions. Rainfall generators with temporal clustering have no theory for the '
          'aquifer response beyond the shot-noise case. The theorems on assimilation assume bounded dynamics and '
          'additive Gaussian forcing, so the multiplicative, heavy-tailed forcing of Section 2 lies outside them. '
          'CERTAIN-COAST does not claim to close these gaps: it uses the decision map to stay where the theory holds '
          'and reports where it does not.'),

    ('h', '8. Where this enters the work plan'),
    ('p', '**T2.3, calibration:** the law of the recharge chosen by $\\Pi$; datum and stage corrections in the state '
          'vector where $\\Gamma$ requires it; initial heads by spin-up or estimation according to $t/\\tau_1$. '
          '**T3.2, alarms:** tail probabilities from the exact law and multilevel Monte Carlo with smoothed indicators. '
          '**T4.1, network design:** daily loggers (Table 4), a local rain gauge for the storm rate, and the tide gauge '
          'for the fluctuation of the sea. **WP5, live operation:** the non-Gaussianity of the forecast ensemble is '
          'monitored at every update.'),
    ('refs', None),
]


def footer(section):
    p = section.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'CERTAIN-COAST · NATO SPS 2027-1 · Mathematical state of the art · page ', size=8, color='6B7785')
    field_run(p, 'PAGE', 8)
    run(p, ' of ', size=8, color='6B7785')
    field_run(p, 'NUMPAGES', 8)


def fill(text):
    text = re.sub(r'\{@(\w+)\}', lambda m: CITE[m.group(1)], text)
    return re.sub(r' +([.,;:)])', r'\1', text)


def main(out):
    numbers, n = {}, 0
    for b in BL:
        if b[0] == 'eq':
            n += 1; numbers[b[1]] = str(n)
    E = Eqs()
    work = tempfile.mkdtemp()
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = Cm(1.6); s.bottom_margin = Cm(1.6)
    s.footer_distance = Cm(0.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(SIZE)
    footer(s)

    p = para(doc, 1); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'CERTAIN-COAST — Mathematical state of the art', bold=True, size=16, color='1F3864')
    p = para(doc, 3); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, TITLE, bold=True, size=11, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'NATO SPS Multi-Year Project, call 2027-1. Supplement to the methods of WP2 and WP3. Equations are native Word '
           'math; references were checked in Crossref; Tables 2–4 are computed in closed form and checked numerically.',
        italic=True, size=8.8, color='52606D')

    for bi, b in enumerate(BL):
        kind = b[0]
        nxt = BL[bi + 1][0] if bi + 1 < len(BL) else None
        if kind == 'h':
            heading(doc, b[1], 12, before=8)
        elif kind == 'h2':
            heading(doc, b[1], 10.5, color='2E6DB4', before=4)
        elif kind == 'p':
            p = para(doc, 3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            text = re.sub(r'\[\[(\w+)\]\]', lambda m: f'({numbers[m.group(1)]})', fill(b[1]))
            mrich(p, text, E, size=SIZE)
            if nxt == 'eq':
                p.paragraph_format.keep_with_next = True
        elif kind == 'eq':
            display_eq(doc, E, b[2], numbers[b[1]])
        elif kind == 'cap':
            p = para(doc, 3, before=3); p.paragraph_format.keep_with_next = True
            run(p, b[1], italic=True, size=8.8, color='52606D')
        elif kind == 'table':
            t = table(doc, b[1], b[2], b[3], size=b[4])
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            for row in t.rows:
                row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            para(doc, 3)
        elif kind == 'refs':
            heading(doc, 'References', 11, before=6)
            sec = doc.add_section(WD_SECTION.CONTINUOUS)
            two_columns(sec)
            for r_ in REFERENCES:
                p = para(doc, 1.5); p.paragraph_format.left_indent = Cm(0.35)
                p.paragraph_format.first_line_indent = Cm(-0.35)
                run(p, r_, size=7.6, color='3D4752')

    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh, ensure_ascii=False)
    omml.main(draft, eq_json, out)
    words = sum(len(re.sub(r'\$[^$]*\$', 'x', fill(b[1])).split()) for b in BL if b[0] == 'p')
    print('saved', out, '|', n, 'numbered equations,', len(E.items) - n, 'inline |', words, 'words |',
          len(REFERENCES), 'references')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Mathematical_State_of_the_Art.docx')
