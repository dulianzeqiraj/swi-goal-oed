"""Working document: boundary conditions as operators, a cost-accuracy rule for the deterministic-first treatment of
boundary conditions, after the operator-learning study of de Hoop, Huang, Qian and Stuart (2022). English, equations
as native Word math (OMML), references checked in Crossref, tables filled from operatori_results.json.

usage: python build_operatori_doc.py RESULTS.json FIGDIR OUT.docx"""
import json
import os
import re
import sys
import tempfile

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.path.join(HERE, '..', 'spiranca_go', 'certain_coast')
sys.path.insert(0, CC)
sys.path.insert(1, os.path.join(HERE, '..', 'ml_paradigms', 'word'))
from build_sota import run, para, heading, table  # noqa: E402
from build_methodology import Eqs, mrich, display_eq  # noqa: E402
from build_annex import field_run, two_columns  # noqa: E402
import omml  # noqa: E402

SIZE = 10
GREY = '52606D'

REFERENCES = [
    'Bhattacharya, K., Hosseini, B., Kovachki, N. B. & Stuart, A. M. (2021). Model reduction and neural networks for '
    'parametric PDEs. The SMAI Journal of Computational Mathematics 7: 121–157. https://doi.org/10.5802/smai-jcm.74',
    'de Hoop, M. V., Huang, D. Z., Qian, E. & Stuart, A. M. (2022). The cost-accuracy trade-off in operator learning '
    'with neural networks. Journal of Machine Learning 1(3): 299–341. https://doi.org/10.4208/jml.220509',
    'de Hoop, M. V., Kovachki, N. B., Nelsen, N. H. & Stuart, A. M. (2023). Convergence rates for learning linear '
    'operators from noisy data. SIAM/ASA Journal on Uncertainty Quantification 11(2): 480–513. '
    'https://doi.org/10.1137/21M1442942',
    'Eckart, C. & Young, G. (1936). The approximation of one matrix by another of lower rank. Psychometrika 1(3): '
    '211–218. https://doi.org/10.1007/BF02288367 (classical)',
    'Halko, N., Martinsson, P. G. & Tropp, J. A. (2011). Finding structure with randomness: probabilistic algorithms '
    'for constructing approximate matrix decompositions. SIAM Review 53(2): 217–288. https://doi.org/10.1137/090771806 '
    '(classical)',
    'Lanthaler, S., Mishra, S. & Karniadakis, G. E. (2022). Error estimates for DeepONets: a deep learning framework in '
    'infinite dimensions. Transactions of Mathematics and Its Applications 6(1): tnac001. '
    'https://doi.org/10.1093/imatrm/tnac001',
    'Lanthaler, S. & Stuart, A. M. (2026). The parametric complexity of operator learning. IMA Journal of Numerical '
    'Analysis 46: 647–712. https://doi.org/10.1093/imanum/draf028',
    'Lu, L., Meng, X., Cai, S., Mao, Z., Goswami, S., Zhang, Z. & Karniadakis, G. E. (2022). A comprehensive and fair '
    'comparison of two neural operators (with practical extensions) based on FAIR data. Computer Methods in Applied '
    'Mechanics and Engineering 393: 114778. https://doi.org/10.1016/j.cma.2022.114778',
    'Slepian, D. (1976). On bandwidth. Proceedings of the IEEE 64(3): 292–300. https://doi.org/10.1109/PROC.1976.10110 '
    '(classical)',
    'Townley, L. R. (1995). The response of aquifers to periodic forcing. Advances in Water Resources 18(3): 125–146. '
    'https://doi.org/10.1016/0309-1708(95)00008-7 (classical)',
]


def blocks(r):
    c1, c2, c3, c4, site = r['check1'], r['check2'], r['check3'], r['check4'], r['site']
    rows1 = {round(x['x'], 3): x for x in c1['rows']}
    lr = {x['N']: x for x in c2['learned']}
    k3 = {k: {x['N']: x for x in v} for k, v in c3['results'].items()}
    g4 = {x['case']: x for x in c4['rows']}
    amp = next(k for k in g4 if k.startswith('amplitude'))
    pc = lambda v: f'{100 * v:.2f}'
    B = []
    a = B.append

    a(('status', 'Status. This working document revises the boundary part (Sections 4 and 6) of the companion document '
                 '"A deterministic-first treatment of boundary and initial conditions in groundwater models" in the light '
                 'of the operator-learning study of de Hoop, Huang, Qian and Stuart (2022). Propositions A–E are proved '
                 'here. Proposition B rests on the classical mean of an inverse Wishart matrix, Proposition C on the '
                 'Eckart–Young theorem and Proposition E(i) on the Cauchy–Schwarz inequality; they are stated because the '
                 'revised procedure depends on them. All numbers come from the dimensionless strip of the companion '
                 'document or from its illustrative Fushë Kuqe–Mat parameters; no observed well data are used.'))
    a(('h', 'Summary'))
    a(('p', '**The question.** The study compares four ways of learning a map between functions (PCA-Net, DeepONet, '
            'PARA-Net and the Fourier neural operator, FNO) on four problems, one of which maps a load applied on a '
            'boundary to the field inside the domain. Three of its messages matter here. Maps with smooth outputs are '
            'learned at close to the Monte Carlo rate, $N^{-1/2}$ in the number of training runs $N$, while maps with '
            'jumps or kinks are learned more slowly, level off and overfit. A data-derived (PCA) output basis can beat '
            'one learned by the network. Inputs from outside the training distribution raise the error. We ask what '
            'this changes in the deterministic-first treatment, where every uncertain boundary condition is replaced '
            'by a deterministic object except in a computed stochastic shell next to the boundary.'))
    a(('p', '**The answer: four rules.**'))
    a(('ul', ['**R1. Compute linear boundary maps, do not learn them.** Sea level or river stage on a confined layer, '
              'fixed-conductance river beds and prescribed fluxes act linearly on the heads. $r$ model runs give the '
              'reduced operator exactly; learning it from $N$ runs adds an excess mean-square error of exactly '
              '$r/(N-r-1)$ times the truncation error (Proposition B).',
              '**R2. Represent the boundary record by the modes the aquifer transmits.** The modes that carry most of '
              'the variance of the record are the wrong ones. In the test strip, 2–3 operator-weighted modes replace '
              '89–219 input PCA modes for the heads in the shell (Proposition C), and the number of modes needed at a '
              'well falls with its distance from the boundary (Proposition A).',
              '**R3. Move pointwise nonlinearities to the input.** A capped recharge, a rating curve or an abstraction '
              'cap is applied to the record before the linear operator. This is exact and removes the kinked maps that '
              'the study finds hard to learn (Proposition D). Switches that depend on the head itself (seepage face, '
              'river disconnection, drying cells) stay in the stochastic shell.',
              '**R4. Guard every reduced boundary operator.** A certified bound and a sharp alarm, both from one '
              'adjoint run per guarded well, detect records outside the range used to build the operator '
              '(Proposition E).']))
    a(('p', f'**Verification.** On the dimensionless strip with a rough sea-level residual and the tolerance δ = 0.25 s '
            f'of the companion\'s illustrative values: the usual input PCA keeps {c1["d99_input_pca"]} of 1200 modes to '
            f'retain 99 % of the variance of the record, while the head at x = 0.1 needs '
            f'{rows1[0.1]["modes_needed"]} modes and the heads beyond the shell edge (x ≥ {c1["shell_width"]:.2f}) need '
            f'none. The learned operator follows Proposition B to within 0.1 % from 460 runs and needs 230 runs to come '
            f'within 11 % of what {c2["du"]} runs compute. With a capped recharge, learned maps level off at '
            f'{pc(k3["capped recharge"][20000]["linear_pca_net"])} % (linear) or decay like $N^{{-0.16}}$ (ReLU, '
            f'{pc(k3["capped recharge"][20000]["relu_pca_net"])} % after 20 000 runs), while applying the cap to the '
            f'input is exact. The alarm fires for {100 * g4["in distribution"]["alarm"]:.1f} % of in-distribution '
            f'records and for {100 * g4[amp]["alarm"]:.2f} % of records with doubled '
            f'amplitude.'))

    a(('h', '1. What the study shows, and what it does not'))
    a(('p', 'de Hoop, Huang, Qian and Stuart (2022) learn maps $\\Psi^{\\dagger}:\\mathcal{U}\\to\\mathcal{V}$ between '
            'spaces of functions from samples $(u_n,\\Psi^{\\dagger}(u_n))$, $n=1,\\dots,N$, and measure the relative '
            'test error against the training volume $N$, the network size and the evaluation cost. In the study\'s '
            'implementation, PCA-Net and DeepONet both project the input on its leading PCA modes (the original '
            'DeepONet used point values). PCA-Net then maps these coefficients, through a '
            'neural network, to the coefficients of the leading PCA modes of the output (Bhattacharya et al., 2021); '
            'DeepONet learns the output basis as a second, "trunk" network, and a PCA output basis inside DeepONet '
            'was proposed by Lu et al. (2022). PARA-Net evaluates one network at every output point; the FNO acts on '
            'the Fourier coefficients of the whole field. Table 1 lists the findings that bear on boundary conditions.'))
    a(('cap', 'Table 1. Findings of the study that bear on boundary conditions (section numbers of the study).'))
    a(('table', ['Finding', 'Where', 'Consequence for boundary conditions'], [
        ['Smooth outputs (Navier–Stokes, Helmholtz): error falls close to N^(-1/2). Non-smooth outputs (boundary load '
         'to stress across a material interface; advected discontinuities): slower decay, errors level out, overfitting',
         '4.3.1–4.3.2', 'Sort boundaries by the smoothness of their map; learn only smooth maps, and only when many '
         'queries justify it (R1, R3)'],
        ['Boundary load to interior stress: the four networks give qualitatively similar predictions and error fields; '
         'PCA-Net, DeepONet and PARA-Net overfit at all data volumes', '4.2.3, 4.3.2', 'A boundary-to-interior map is learnable but costly; for a '
         'linear aquifer layer it can be computed (Proposition B)'],
        ['PCA-Net beats DeepONet on Helmholtz; 40–70 % of the trained trunk functions are identically zero and the '
         'others are local', '4.3.5', 'Use data-derived output modes; for linear boundaries they are optimal '
         '(Proposition C)'],
        ['Input is represented by its PCA modes, "not well-adapted to discontinuous inputs"', '3.2, 4.2.4',
         'Choose input modes by the operator, not by the variance of the record (R2)'],
        ['Inputs drawn from 4C instead of C: higher errors that fall more slowly with N, most of all for the '
         'non-smooth problem', '4.3.4', 'Guard every reduced operator against records outside its range (R4)'],
        ['PARA-Net not competitive; FNO has the lowest errors in 1D and 2D on uniform grids, at a cost that grows with '
         'the retained Fourier modes and hence with dimension; fitted exponents p of error ∝ cost^(-p): 1.129, '
         '0.7254, 0.0926, 0.002506', '4.3.3, 5', 'For non-smooth maps, more cost buys almost no accuracy: exploit '
         'structure instead'],
    ], [6.6, 1.8, 8.6], 8.6))
    a(('p', 'The authors stress that their study is computational and that conclusions about a preferred method are '
            'premature. Theory published since then points the same way. For linear operators, sample complexity '
            'depends on the smoothness of the data and on the decay of the operator\'s eigenvalues, and bounds hold '
            'under distribution shift (de Hoop et al., 2023); DeepONet has explicit error estimates (Lanthaler, Mishra '
            'and Karniadakis, 2022); and for operators characterised only by their $C^{r}$ or Lipschitz regularity, '
            'PCA-Net, DeepONet and FNO suffer a "curse of parametric complexity" that can be overcome only by '
            'exploiting additional structure (Lanthaler and Stuart, 2026). In the deterministic-first treatment that '
            'structure is known: the linearity of a confined layer (Theorem 1 of the companion document), the transfer '
            'function of the strip (Theorem 4) and the pointwise form of some boundary nonlinearities. The rules '
            'below exploit it.'))

    a(('h', '2. The boundary operator and four classes of boundaries'))
    a(('p', 'Let $g\'$ be a boundary residual record over a window of length $T$ (sea level after removing the tide, '
            'river stage after removing the seasonal cycle), and let $\\Psi_{B}$ map it to the boundary part $u_{B}$ '
            'of the head at the forecast time, at the wells or on the shell. By Theorem 1 of the companion document, '
            '$\\Psi_{B}$ is linear for a confined layer. In the coastal strip its action at angular frequency '
            '$\\omega$ is the transfer function $H(\\omega,x)=\\cosh\\kappa(L-x)/\\cosh\\kappa L$, '
            '$\\kappa=(i\\omega/D)^{1/2}$ (Townley, 1995). Table 2 sorts the boundaries of a coastal model by the form '
            'of their map, which decides how they are treated.'))
    a(('cap', 'Table 2. Four classes of boundaries and their treatment.'))
    a(('table', ['Class', 'Boundaries', 'Form of the map', 'Treatment'], [
        ['L, linear', 'Sea level and river stage on confined layers; river and lagoon beds of fixed conductance; '
         'prescribed lateral flux; recharge below the infiltration capacity', 'Linear in the record',
         'Compute with operator-weighted modes (Propositions B, C); guard (Proposition E)'],
        ['P, pointwise nonlinearity of the data', 'Recharge capped by the infiltration capacity, min(q, Ic); flux from '
         'a rating curve; capped abstraction', 'Class-L operator after a known pointwise map φ',
         'Apply φ to the record, then the class-L operator (Proposition D)'],
        ['B, smooth nonlinearity of the state', 'Sea boundary of a phreatic (Boussinesq) layer',
         'Smooth, mildly nonlinear', 'Kirchhoff-mean core (Theorem 5); fluctuation linearised about it and treated '
         'as class L; learn only with many queries'],
        ['S, switch of the state', 'Seepage face; river disconnection; drying and rewetting cells; moving toe of the '
         'salt–fresh interface', 'Non-smooth (kinks, jumps)', 'Keep in the shell; model runs or Monte Carlo restricted '
         'to the shell; a learned surrogate only with a guard and a demonstrated rate'],
    ], [2.6, 5.4, 3.0, 6.0], 8.6))

    a(('h', '3. Five propositions'))
    a(('pi', '**Proposition A (aquifer-filtered input dimension).** In the strip of Theorem 4 of the companion document, '
             'let the boundary residual be stationary with a spectral density $S_{g}$ that does not increase with '
             'frequency. In the stationary regime, the part of the head variance at $x$ produced by boundary '
             'frequencies above $\\Omega\\ge\\omega_{L}=D(\\ln 4)^{2}/(2L^{2})$ satisfies'))
    a(('eq', 'A', r'V_{x}(\Omega)=\frac{1}{\pi}\int_{\Omega}^{\infty}S_{g}(\omega)\,|H(\omega,x)|^{2}\,d\omega\le'
                  r'\frac{16\,S_{g}(\Omega)}{\pi}\,e^{-a\sqrt{\Omega}}\left(\frac{\sqrt{\Omega}}{a}+\frac{1}{a^{2}}\right),'
                  r'\qquad a=x\sqrt{2/D}.'))
    a(('pi', 'Let $\\Omega_{x}(\\delta)$ be the frequency at which the right side equals $\\delta^{2}$. Removing '
             'the frequencies above $\\Omega_{x}$ from the record changes the head at $x$ by a standard deviation of at '
             'most δ. A record of length $T$ restricted to frequencies below $\\Omega_{x}$ has about '
             '$n_{x}=T\\Omega_{x}/\\pi$ degrees of freedom (Slepian, 1976), which is the number of modes to keep. '
             'Because the bound decays with $x\\sqrt{\\Omega}$, $\\Omega_{x}$ and $n_{x}$ '
             'fall roughly like $x^{-2}$ inland, up to a logarithmic factor, and no mode is needed where the whole '
             'boundary variance at $x$ is below $\\delta^{2}$, that is outside the shell.'))
    a(('pi', '**Proof.** With $b=L(2\\omega/D)^{1/2}$ and $b\'=b(1-x/L)$, the squared modulus of the transfer function '
             'is $(\\cosh b\'+\\cos b\')/(\\cosh b+\\cos b)$ (proof of Theorem 4(iv) of the companion document). The '
             'numerator is at most $\\cosh b\'+1\\le 2e^{b\'}$; the denominator is at least $\\cosh b-1\\ge e^{b}/4$ '
             'when $b\\ge\\ln 4$, that is when $\\omega\\ge\\omega_{L}$. Hence $|H|^{2}\\le 8e^{-x(2\\omega/D)^{1/2}}$. '
             'Since $S_{g}(\\omega)\\le S_{g}(\\Omega)$ for $\\omega\\ge\\Omega$, the integral is at most '
             '$8S_{g}(\\Omega)/\\pi$ times $\\int_{\\Omega}^{\\infty}e^{-a\\sqrt{\\omega}}d\\omega='
             '2e^{-a\\sqrt{\\Omega}}(\\sqrt{\\Omega}/a+1/a^{2})$, obtained with $\\omega=s^{2}$. The count of degrees '
             'of freedom is the time–bandwidth product of a record of length $T$ and angular bandwidth Ω (Slepian, '
             '1976). ∎'))
    a(('p', 'Reading. The bound is sufficient, not sharp: in Check 1 it overstates the number of modes by a factor of '
            '4–7, because it replaces $|H|^{2}$ by its envelope and the spectrum by its value at Ω. It is a first '
            'estimate; the exact count comes from Theorem 4(i) of the companion document on the actual geometry and '
            'spectrum, and the smallest count from Proposition C.'))

    a(('pi', '**Proposition B (compute, do not learn).** Let $\\Psi_{B}$ be linear (class L), let the record $g$ be '
             'Gaussian with independent coefficients $c_{k}$ on its Karhunen–Loève (PCA) modes $\\varphi_{k}$, and '
             'keep $r$ modes. (i) The restriction of $\\Psi_{B}$ to the first $r$ modes follows exactly from $r$ model '
             'runs, one forced by each mode, and its mean-square error is the truncation error '
             '$E_{r}=\\mathbb{E}\\|\\Psi_{B}(g-P_{r}g)\\|^{2}$, which no training data can reduce. (ii) If instead '
             'the map from $(c_{1},\\dots,c_{r})$ to the heads is learned by least squares from $N>r+1$ independent '
             'runs (a PCA-Net with a linear map), its expected mean-square test error is'))
    a(('eq', 'B', r'\mathbb{E}\,\|\Psi_{B}\,g-\widehat{\Psi}_{N}\,g\|^{2}=E_{r}\left(1+\frac{r}{N-r-1}\right).'))
    a(('pi', 'Hence learning needs $N\\ge r(1+1/\\eta)+1$ runs to come within a factor $1+\\eta$ of what $r$ runs '
             'compute ($11r$ runs for $\\eta=0.1$), and the error grows without bound as $N$ approaches $r+1$ from '
             'above.'))
    a(('pi', '**Proof.** (i) is linearity: the response to $\\sum_{k\\le r}c_{k}\\varphi_{k}$ is '
             '$\\sum_{k\\le r}c_{k}\\Psi_{B}\\varphi_{k}$. (ii) At one output point write '
             '$y=c^{\\top}\\beta+\\varepsilon$, where $c$ are the kept coefficients, '
             '$\\beta_{k}=(\\Psi_{B}\\varphi_{k})(x)$ and ε is the response to the discarded modes. For a Gaussian '
             'record the coefficients are independent, so ε is independent of $c$, with mean zero and variance '
             '$\\sigma^{2}$, the truncation error at that point. The least-squares estimate satisfies '
             '$\\widehat{\\beta}-\\beta=(C^{\\top}C)^{-1}C^{\\top}\\varepsilon$, with $C$ the $N\\times r$ matrix of '
             'training coefficients, so for a new record the excess error is '
             '$\\mathbb{E}[(c^{\\top}(\\widehat{\\beta}-\\beta))^{2}]=\\sigma^{2}\\,\\text{tr}(\\Lambda\\,'
             '\\mathbb{E}(C^{\\top}C)^{-1})$, Λ being the covariance of $c$. $C^{\\top}C$ is Wishart with $N$ degrees '
             'of freedom and scale Λ, so $\\mathbb{E}(C^{\\top}C)^{-1}=\\Lambda^{-1}/(N-r-1)$ and the excess is '
             '$\\sigma^{2}r/(N-r-1)$. Summing over the output points gives (B). ∎'))

    a(('pi', '**Proposition C (operator-weighted modes).** Let $\\Psi_{B}$ be linear and the record Gaussian with '
             'covariance $\\mathcal{C}$. Among all linear maps $A$ of rank at most $r$, the mean-square error '
             '$\\mathbb{E}\\|\\Psi_{B}g-Ag\\|^{2}$ is minimised by the truncated singular value decomposition of '
             '$\\Psi_{B}\\mathcal{C}^{1/2}$: with singular triplets $(\\sigma_{k},u_{k},v_{k})$, '
             '$A_{r}g=\\sum_{k\\le r}\\sigma_{k}u_{k}\\langle v_{k},\\mathcal{C}^{-1/2}g\\rangle$, and'))
    a(('eq', 'C', r'\min_{\mathrm{rank}\,A\le r}\mathbb{E}\,\|\Psi_{B}\,g-A\,g\|^{2}=\sum_{k>r}\sigma_{k}^{2}'
                  r'\left(\Psi_{B}\,\mathcal{C}^{1/2}\right).'))
    a(('pi', 'The output modes $u_{k}$ are the PCA modes of the heads, so the PCA-Net output basis is optimal for class '
             'L. The input modes $\\mathcal{C}^{1/2}v_{k}$ are not the PCA modes of the record, which are optimal only '
             'for reproducing the record itself.'))
    a(('pi', '**Proof.** Write $g=\\mathcal{C}^{1/2}\\xi$ with ξ standard Gaussian. Then '
             '$\\mathbb{E}\\|(\\Psi_{B}-A)\\mathcal{C}^{1/2}\\xi\\|^{2}$ is the squared Hilbert–Schmidt norm of '
             '$(\\Psi_{B}-A)\\mathcal{C}^{1/2}$, and $A\\mathcal{C}^{1/2}$ ranges over all operators of rank at most '
             '$r$ on the range of $\\mathcal{C}^{1/2}$. The Eckart–Young theorem (Eckart and Young, 1936) gives the '
             'minimiser and the error. The covariance of the output is $\\Psi_{B}\\mathcal{C}\\Psi_{B}^{*}$, whose '
             'eigenvectors are the $u_{k}$. ∎'))
    a(('p', 'Computation. The leading $r$ triplets come from a randomised singular value decomposition (Halko, '
            'Martinsson and Tropp, 2011) with about $r+10$ forward runs of the model, forced by random records with '
            'covariance $\\mathcal{C}$, and as many adjoint runs. In the shell of the test strip $r=2$–3.'))

    a(('pi', '**Proposition D (kink on the input side).** If the boundary data enter a linear layer through a known '
             'pointwise map φ, the head is $h=\\Psi_{L}(\\varphi\\circ q)$ exactly, and its mean is '
             '$\\Psi_{L}\\,\\mathbb{E}\\,\\varphi(q)$. The composite map $q\\mapsto h$ carries the kinks of φ: for '
             '$\\varphi(q)=\\min(q,I_{c})$ it is Lipschitz but not differentiable wherever the record crosses the cap, '
             'which places it in the non-smooth regime of the study. Applying φ to the record and then the class-L '
             'operator removes the learning problem.'))
    a(('pi', '**Proof.** The first statement is the definition of class P; the mean follows from the linearity of '
             '$\\Psi_{L}$ and of the expectation. For the cap it gives the deterministic-equivalent flux '
             '$\\mathbb{E}\\min(q,I_{c})$ of Remark 4 of the companion document. ∎'))

    a(('pi', '**Proposition E (certified guard and sharp alarm).** Let $A_{r}$ keep the first $r$ modes of a class-L '
             'operator and split the discarded modes into bands $P_{b}$ of $n_{b}$ modes. At a guarded point $x$, let '
             '$\\gamma_{x,b}=\\|(\\Psi_{B})_{x}P_{b}\\|$ and let $e_{x}$ be the error of $A_{r}$. (i) For every record,'))
    a(('eq', 'E', r'|e_{x}|\le\sum_{b}\gamma_{x,b}\,\|P_{b}^{\top}g\|,\qquad\widehat{s}_{x}^{\,2}=\sum_{b}'
                  r'\frac{\gamma_{x,b}^{2}}{n_{b}}\,\|P_{b}^{\top}g\|^{2}.'))
    a(('pi', '(ii) If the coefficients of the record are uncorrelated and of equal variance within each band, '
             '$\\widehat{s}_{x}^{\\,2}$ is an unbiased estimate of $\\mathbb{E}e_{x}^{2}$. The row '
             '$(\\Psi_{B})_{x}$, and with it every $\\gamma_{x,b}$, comes from one adjoint run per guarded point.'))
    a(('pi', '**Proof.** $e_{x}=\\sum_{b}(\\Psi_{B})_{x}P_{b}P_{b}^{\\top}g$, and the Cauchy–Schwarz inequality on '
             'each band gives (i). For (ii), $\\mathbb{E}e_{x}^{2}=\\sum_{k}m_{k}^{2}\\sigma_{k}^{2}$ with '
             '$m_{k}=(\\Psi_{B}\\varphi_{k})(x)$; if $\\sigma_{k}^{2}=\\sigma_{b}^{2}$ within band $b$ this is '
             '$\\sum_{b}\\sigma_{b}^{2}\\gamma_{x,b}^{2}$, and $\\|P_{b}^{\\top}g\\|^{2}/n_{b}$ is an unbiased estimate '
             'of $\\sigma_{b}^{2}$. ∎'))
    a(('p', 'Reading. The certificate always holds but is loose, by a factor of 14–20 in Check 4, because it adds '
            'the contributions of the bands without their signs; the estimate is sharp. We use the certificate where a '
            'guarantee is required and the estimate as the alarm. When $2.576\\,\\widehat{s}_{x}>\\delta$, the reduced '
            'operator is no longer within tolerance at the 99 % level: the full model, or the exact adjoint row, is used '
            'at that well, and the "forecast outside the record" trigger of the NATO framework is raised. For a linear '
            'operator, records drawn from 4C, the study\'s out-of-distribution test, double the error in absolute terms '
            'but not in relative terms; a change of noise memory moves energy between bands, and the alarm sees it.'))

    a(('h', '4. The revised treatment procedure'))
    a(('p', 'The rules change Steps 3–4 and add to Step 6 of the procedure in Figure 2 of the companion document; the '
            'other steps are unchanged.'))
    a(('ul', ['**Step 3 (unchanged).** Boundary test with $F(\\tau_{int}/\\tau_{1})$ and the shell width $w(\\delta)$.',
              '**Step 3a (new).** Classify every boundary of the model (Table 2).',
              '**Step 3b (new).** For classes L and P, compute the reduced boundary operator on the shell with '
              'operator-weighted modes (Proposition C), with $r$ set by the tolerance. Proposition A gives a quick '
              'sufficient count of boundary modes at each well.',
              '**Step 3c (new).** For class P, apply the pointwise map to each record before the operator (Proposition '
              'D). For class B, use the Kirchhoff-mean core (Theorem 5) with the fluctuation treated as class L. For '
              'class S, build no surrogate by default: use model runs or Monte Carlo restricted to the shell (Step 6).',
              '**Step 4 (unchanged).** Effective boundary maps for the deterministic core.',
              '**Step 6a (new).** Guard each supply and monitoring well in the shell with one adjoint run (Proposition '
              'E). For each new record compute its band energies; on alarm, use the full model at that well and raise '
              'the "outside the record" trigger.']))
    a(('cap', 'Table 3. When to compute and when to learn.'))
    a(('table', ['Class', 'Compute', 'Learn', 'Choice'], [
        ['L', 'About r + 10 forward and r + 10 adjoint runs (r = 2–3 in the shell of the test strip)',
         'At least r(1 + 1/η) + 1 runs for a linear map (Proposition B); more for a nonlinear network', 'Compute'],
        ['P', 'As L, plus the pointwise map', 'Kinked map: slow rates (about N^(-0.16) in Check 3)', 'Compute'],
        ['B', 'Kirchhoff core; linearised fluctuation as L', 'Smooth map: close to N^(-1/2) in the study',
         'Compute; learn only with many queries'],
        ['S', 'Model or Monte Carlo in the shell', 'Non-smooth map: slow, levels off, overfits (study)',
         'Model in the shell; learn only with a guard and a demonstrated rate'],
    ], [1.4, 6.0, 6.2, 3.4], 8.6))

    a(('h', '5. Synthetic verification'))
    a(('p', f'The companion script OPERATORI-GO (operatori_exp.py; numpy; about 15 seconds) uses the strip of the '
            f'companion document, $L=1$, $D=1$, $\\tau_{{1}}=4/\\pi^{{2}}=0.405$, discretised with 100 nodes and '
            f'implicit time steps of 0.001 over a window $T=1.2$, about $3\\tau_{{1}}$. The sea-level residual is an '
            f'Ornstein–Uhlenbeck process with $s=1$ and $\\tau_{{int}}=0.02\\,\\tau_{{1}}$. The tolerance is δ = 0.25, '
            f'the ratio of the companion\'s illustrative values (5 cm and 0.2 m); the stochastic shell then ends at '
            f'x = {c1["shell_width"]:.2f}.'))
    rows = rows1
    xs = [0.02, 0.05, 0.1, 0.2]
    pr = c1['shell_profile_ranks']
    Ns = [x['N'] for x in c2['learned']]
    t4 = [
        ['1. Input dimension (Proposition A)',
         'Modes needed for a head s.d. error ≤ δ at x = ' + ', '.join(f'{v:g}' for v in xs) + ': '
         + ', '.join(str(rows[v]['modes_needed']) for v in xs) + f'; none for x ≥ {c1["shell_width"]:.2f}. '
         'Proposition A: ' + ', '.join(f'{rows[v]["prop_a_modes"]:.0f}' for v in xs)
         + f'. Usual input PCA (99 % of variance): {c1["d99_input_pca"]} of 1200',
         'The input dimension is set by the aquifer; Proposition A is sufficient within a factor of 4–7'],
        ['2. Operator-weighted modes (Proposition C)',
         'Heads in the shell (0.05 ≤ x < ' + f'{c1["shell_width"]:.2f}), RMS tolerance '
         + ', '.join(f'{p["rms_tolerance"]:g}' for p in pr) + ': input PCA '
         + ', '.join(str(p['input_kl_modes']) for p in pr) + ' modes; optimal '
         + ', '.join(str(p['optimal_rank']) for p in pr),
         '40 to 70 times fewer modes'],
        ['3. Compute or learn (Proposition B)',
         f'r = {c2["du"]} modes, heads at x ≥ 0.1. Computed from {c2["du"]} runs: RMS {c2["computed_rms_error"]:.4f}. '
         'Learned with N = ' + ', '.join(str(n) for n in Ns) + ': '
         + ', '.join(f'{lr[n]["rms_error"]:.4f}' for n in Ns) + '. Proposition B: '
         + ', '.join('–' if lr[n]['proposition_b_rms'] != lr[n]['proposition_b_rms'] else f'{lr[n]["proposition_b_rms"]:.4f}'
                     for n in Ns),
         'Formula exact to 0.1 % from N = 460; error spike at N = r'],
        ['4. Kinked map (Proposition D)',
         f'Recharge capped at {c3["cap"]:g} (exceeded {100 * c3["fraction_of_time_capped"]:.1f} % of the time), '
         f'{c3["du"]} PCA input modes. Relative error at N = 100, 1000, 20 000. Linear map: linear PCA-Net '
         + ', '.join(pc(k3['linear (no cap)'][n]['linear_pca_net']) for n in (100, 1000, 20000)) + ' %; ReLU '
         + ', '.join(pc(k3['linear (no cap)'][n]['relu_pca_net']) for n in (100, 1000, 20000)) + ' %. Capped map: '
         'linear ' + ', '.join(pc(k3['capped recharge'][n]['linear_pca_net']) for n in (100, 1000, 20000))
         + ' %; ReLU ' + ', '.join(pc(k3['capped recharge'][n]['relu_pca_net']) for n in (100, 1000, 20000))
         + ' %. Cap applied to the input: exact',
         'A kink removes the Monte Carlo rate (about N^(-0.16)); structure removes the problem'],
        ['5. Guard (Proposition E)',
         f'Well at x = {c4["x"]:g}, r = {c4["du"]} modes, bands of {c4["band"]} modes. RMS error / estimate / alarm: '
         + '; '.join(f'{k} {v["rms_error"]:.3f} / {v["median_sd_estimate"]:.3f} / {100 * v["alarm"]:.2f} %'
                     for k, v in g4.items())
         + '. The certificate held for all 16 000 records, at about 14–20 times the error',
         'Sharp alarm; rigorous but loose certificate'],
    ]
    a(('cap', 'Table 4. Results of the synthetic checks.'))
    a(('table', ['Check', 'Result', 'Reading'], t4, [3.2, 10.0, 3.8], 8.4))
    a(('fig', 'operatori_fig1.png', 'Figure 1. (a) Boundary modes needed for the head at distance x to within δ, '
                                    'exact and from Proposition A, against the usual 99 %-variance PCA of the record; '
                                    'no mode is needed beyond the edge of the stochastic shell. (b) Modes needed for '
                                    'the heads in the shell: input PCA against operator-weighted modes (Proposition C).'))
    a(('fig', 'operatori_fig2.png', 'Figure 2. (a) A linear boundary operator computed from r = 46 model runs against a '
                                    'PCA-Net with a linear map learned from N runs; the learned error follows '
                                    'Proposition B and spikes at N = r. (b) Learning a linear boundary map and a '
                                    'capped-recharge map with linear and ReLU PCA-Nets: the kink removes the Monte Carlo '
                                    'rate, while applying the cap to the input is exact.'))

    a(('h', '6. Application: the Fushë Kuqe–Mat coastal aquifer (illustrative)'))
    a(('p', 'With the illustrative parameters of the companion document (coast-normal length 5 km, transmissivity '
            '500 m²/day, specific yield 0.1 or storage coefficient $10^{-4}$, sea-level residual with $s=0.2$ m and '
            '$\\tau_{int}=1$ day, a 90-day window and a tolerance of 5 cm), Proposition A gives the shortest '
            'sea-level period that must be kept at each distance from the coast (Table 5).'))
    t5 = [[x['layer'].capitalize(), f'{x["x_m"]:,} m'.replace(',', ' '), f'{x["period_hours"]:.1f} h',
           f'{x["modes_90_days"]:.0f}'] for x in site]
    a(('cap', 'Table 5. Sea-level variations that a well must see (Proposition A, sufficient; illustrative parameters).'))
    a(('table', ['Layer', 'Distance from the coast', 'Shortest period to keep', 'Modes of a 90-day record'], t5,
       [3.4, 4.4, 4.6, 4.6], 9))
    a(('p', 'Reading. In the phreatic layer a supply well 100 m from the coast does not need sea-level variations '
            'faster than about 2.5 days, and a well 200 m inland none faster than about 9 days; the hourly tide-gauge '
            'record can be reduced accordingly before it enters the operator. In the confined layer, where the shell '
            'covers the whole aquifer, even the inland end needs periods down to about 5 days. Proposition A is '
            'sufficient within a factor of 4–7 (Check 1), so the operator-weighted count of Proposition C, computed '
            'on the calibrated model, will be much smaller. These numbers must be recomputed with the calibrated '
            'parameters.'))

    a(('h', '7. Innovation'))
    a(('p', 'The building blocks are classical: the transfer function of a strip, the Eckart–Young theorem, the mean '
            'of an inverse Wishart matrix, the time–bandwidth product and the Cauchy–Schwarz inequality. What this '
            'document adds, to our knowledge (to be verified against the literature before submission):'))
    a(('ul', ['**Operator-weighted boundary modes.** The input of a boundary operator is represented by the modes that '
              'the aquifer transmits, $\\mathcal{C}^{1/2}v_{k}$ from the singular value decomposition of '
              '$\\Psi_{B}\\mathcal{C}^{1/2}$, computed with forward and adjoint runs, instead of the input PCA used by '
              'PCA-Net and DeepONet in the study. In the shell of the test strip this replaces 89–219 modes by 2–3.',
              '**An input-dimension law for boundaries (Proposition A).** A closed-form sufficient count of boundary '
              'modes at distance $x$, falling roughly like $x^{-2}$ inland and vanishing outside the shell. It joins '
              'the shell of the companion document to the input dimension of an operator.',
              '**The exact price of learning a linear boundary operator (Proposition B).** The excess mean-square '
              'error is $r/(N-r-1)$ times the truncation error, so learning needs at least $r(1+1/\\eta)+1$ runs to '
              'come within $1+\\eta$ of what $r$ runs compute, and it spikes at $N=r$. The formula matched the '
              'experiment to 0.1 %.',
              '**The kink-on-input rule (Proposition D).** Boundary nonlinearities that act pointwise on the data are '
              'moved before the linear operator. This removes, exactly, the non-smooth regime in which the study and '
              'Check 3 find slow learning.',
              '**A certified guard and a sharp alarm (Proposition E).** One adjoint run per well gives a bound that '
              'always holds and an estimate that matches the realised error. It tells, for each new record, whether '
              'the reduced boundary operator can be trusted, and it feeds the "outside the record" trigger of the NATO '
              'framework.']))

    a(('h', '8. Limitations'))
    a(('ul', ['Proposition A and Checks 1–4 use a one-dimensional strip with uniform properties and Gaussian, '
              'stationary boundary residuals. Proposition A is a sufficient count, conservative by a factor of 4–7 '
              'in Check 1.',
              'Propositions B, C and E(i) hold for any linear layer, but their numbers were checked only in the strip. '
              'Class S was not tested: seepage faces, river disconnection and the moving interface need a '
              'two-dimensional model.',
              'The study\'s trained deep networks and FNO were not re-run; Check 3 uses a linear map and a random-feature '
              'ReLU map on PCA coefficients. Its rate of about $N^{-0.16}$ belongs to this learner and this kink; it '
              'is not a general law.',
              'The alarm assumes a spectrum that is nearly constant within each band; spectral peaks (seiches, '
              'imperfectly removed tides) need narrower bands.']))
    a(('p', '**Use now.** This document is for after the NATO submission. At most one sentence may enter the methods: '
            '"Boundary operators of linear layers are computed with operator-weighted modes, pointwise boundary '
            'nonlinearities are applied to the data, and every reduced operator is guarded by one adjoint run per '
            'well."'))
    a(('refs',))
    a(('note', 'Six of the ten references are from 2021 or later. The four earlier ones are classical results used '
               'directly: Eckart and Young (1936) behind Proposition C, Slepian (1976) behind the count of Proposition '
               'A, Halko, Martinsson and Tropp (2011) for the randomised decomposition, and Townley (1995) for the '
               'transfer function. Companion document, not counted: "A deterministic-first treatment of boundary and '
               'initial conditions in groundwater models" (10 November 2026).'))
    a(('note', 'Appendix. operatori_exp.py (Python 3; numpy; about 15 seconds) reproduces every number of Sections 5 '
               'and 6 and writes operatori_results.json; operatori_figs.py draws Figures 1 and 2; this document is '
               'built by build_operatori_doc.py (folder experiments/operatori_go).'))
    return B


def footer(section):
    p = section.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Boundary conditions as operators · working document · page ', size=8, color='6B7785')
    field_run(p, 'PAGE', 8)
    run(p, ' of ', size=8, color='6B7785')
    field_run(p, 'NUMPAGES', 8)


def main(res, figdir, out):
    r = json.load(open(res))
    BL = blocks(r)
    numbers, n = {}, 0
    for b in BL:
        if b[0] == 'eq':
            n += 1; numbers[b[1]] = str(n)
    E = Eqs()
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = Cm(1.7); s.bottom_margin = Cm(1.6)
    s.footer_distance = Cm(0.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(SIZE)
    footer(s)
    p = para(doc, 0); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'POLYTECHNIC UNIVERSITY OF TIRANA', bold=True, size=10, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Faculty of Geology and Mining — Department of Energy Resources', size=9, color=GREY)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Boundary conditions as operators', bold=True, size=16, color='1F3864')
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'A cost–accuracy rule for the deterministic-first treatment of boundary conditions, after the '
           'operator-learning study of de Hoop, Huang, Qian and Stuart (2022): propositions with proofs, a revised '
           'procedure and synthetic checks (OPERATORI-GO)', bold=True, size=10.5, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'D. Zeqiraj, Faculty of Geology and Mining, Polytechnic University of Tirana · Working document, companion '
           'to "A deterministic-first treatment of boundary and initial conditions in groundwater models" · '
           '10 November 2026', italic=True, size=8.8, color=GREY)

    for bi, b in enumerate(BL):
        kind = b[0]
        nxt = BL[bi + 1][0] if bi + 1 < len(BL) else None
        if kind == 'h':
            heading(doc, b[1], 12, before=8)
        elif kind == 'status':
            p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, b[1], italic=True, size=9, color=GREY)
        elif kind in ('p', 'pi'):
            p = para(doc, 3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            if kind == 'pi':
                p.paragraph_format.left_indent = Cm(0.6)
            mrich(p, b[1], E, size=SIZE)
            if nxt == 'eq':
                p.paragraph_format.keep_with_next = True
        elif kind == 'ul':
            for item in b[1]:
                p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.left_indent = Cm(0.6); p.paragraph_format.first_line_indent = Cm(-0.35)
                run(p, '•  ', size=SIZE)
                mrich(p, item, E, size=SIZE)
            para(doc, 1)
        elif kind == 'eq':
            display_eq(doc, E, b[2], numbers[b[1]])
        elif kind == 'cap':
            p = para(doc, 3, before=3); p.paragraph_format.keep_with_next = True
            run(p, b[1], italic=True, size=8.8, color=GREY)
        elif kind == 'table':
            t = table(doc, b[1], b[2], b[3], size=b[4])
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            for i, row in enumerate(t.rows):
                row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
                if i < len(t.rows) - 1:          # keep the table on one page
                    for cell in row.cells:
                        for cp in cell.paragraphs:
                            cp.paragraph_format.keep_with_next = True
            para(doc, 3)
        elif kind == 'fig':
            p = para(doc, 2, before=4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(os.path.join(figdir, b[1]), width=Cm(16.8))
            p = para(doc, 6)
            run(p, b[2], italic=True, size=8.8, color=GREY)
        elif kind == 'refs':
            heading(doc, 'References', 11, before=6)
            sec = doc.add_section(WD_SECTION.CONTINUOUS)
            two_columns(sec)
            for r_ in REFERENCES:
                p = para(doc, 1.5); p.paragraph_format.left_indent = Cm(0.35)
                p.paragraph_format.first_line_indent = Cm(-0.35)
                run(p, r_, size=7.6, color='3D4752')
            sec = doc.add_section(WD_SECTION.CONTINUOUS)
            cols = sec._sectPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cols')
            if cols is not None:
                cols.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}num', '1')
        elif kind == 'note':
            p = para(doc, 3, before=3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, b[1], italic=True, size=8.2, color=GREY)

    work = tempfile.mkdtemp()
    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh, ensure_ascii=False)
    omml.main(draft, eq_json, out)
    words = sum(len(re.sub(r'\$[^$]*\$', 'x', b[1] if isinstance(b[1], str) else ' '.join(b[1])).split())
                for b in BL if b[0] in ('p', 'pi', 'ul'))
    print('saved', out, '|', n, 'numbered equations,', len(E.items) - n, 'inline |', words, 'words |',
          len(REFERENCES), 'references')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
