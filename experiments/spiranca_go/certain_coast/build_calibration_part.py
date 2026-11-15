"""CERTAIN-COAST, Additional Files: calibration when the model is wrong.

The state of the art of calibration and of bandits (from the author's two reviews of November 2026), the
invariance-first calibration of the calibration review, and TRIAL-GO: a robust bandit over model structures whose
plays are calibration iterations checked against metered pumping stops, allocated by the robust Gittins index of
Cohen and Treetanthiploet (2022). The demonstration on the Fushë-Kuqe aquifer is computed by the MATLAB code in
experiments/prova_go (run in GNU Octave 8.4) and read from its results file and figures; the algorithm itself is
released in the open-source code of the project, package certaincoast.calibration of dulianzeqiraj/certain-coast.

usage: python3 build_calibration_part.py OUT.docx [RESULTS_DIR]
"""
import json
import os
import re
import sys
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', '..', 'garancia_go'))
sys.path.insert(2, os.path.join(HERE, '..', '..', 'ml_paradigms', 'word'))
import build_sota as BS  # noqa: E402
from build_sota import run, para, heading, table, link  # noqa: E402
from build_decisions_drl import body, bullet, figure, box  # noqa: E402

NAVY, BLUE, GREY = '1F3864', '2E6DB4', '52606D'
CODE = 'https://github.com/dulianzeqiraj/certain-coast/tree/nato-sps-2027'   # certaincoast.calibration
PART_INDEX = 9                 # position of this part in the Additional Files (0-based): its red equations

# ------------------------------------------------------------------------------------------------ references
REFS = [
    ('baptista', 'Baptista, R., Hosseini, B., Kovachki, N.B. and Marzouk, Y.M. (2024). Conditional sampling with monotone '
                 'GANs: from generative models to likelihood-free inference. SIAM/ASA Journal on Uncertainty '
                 'Quantification 12(3), 868–900.', 'https://doi.org/10.1137/23M1581546'),
    ('carmona', 'Carmona, C.U. and Nicholls, G.K. (2020). Semi-modular inference: enhanced learning in multi-modular '
                'models by tempering the influence of components. Proceedings of AISTATS 2020, PMLR 108, 4226–4235.',
     'https://arxiv.org/abs/2003.06804'),
    ('cartis', 'Cartis, C. and Roberts, L. (2023). Scalable subspace methods for derivative-free nonlinear least-squares '
               'optimization. Mathematical Programming 199(1–2), 461–524.', 'https://doi.org/10.1007/s10107-022-01836-1'),
    ('chick', 'Chick, S.E., Gans, N. and Yapar, Ö. (2022). Bayesian sequential learning for clinical trials of multiple '
              'correlated medical interventions. Management Science 68(7), 4919–4938.',
     'https://doi.org/10.1287/mnsc.2021.4137'),
    ('cleary', 'Cleary, E., Garbuno-Inigo, A., Lan, S., Schneider, T. and Stuart, A.M. (2021). Calibrate, emulate, '
               'sample. Journal of Computational Physics 424, 109716.', 'https://doi.org/10.1016/j.jcp.2020.109716'),
    ('ct22', 'Cohen, S.N. and Treetanthiploet, T. (2022). Gittins\' theorem under uncertainty. Electronic Journal of '
             'Probability 27, paper 17, 1–48.', 'https://doi.org/10.1214/22-EJP742'),
    ('doherty', 'Doherty, J. (2015). Calibration and Uncertainty Analysis for Complex Environmental Models. Watermark '
                'Numerical Computing, Brisbane.', None),
    ('dunbar', 'Dunbar, O.R.A., Howland, M.F., Schneider, T. and Stuart, A.M. (2022). Ensemble-based experimental design '
               'for targeting data acquisition to inform climate models. Journal of Advances in Modeling Earth Systems '
               '14(9), e2022MS002997.', 'https://doi.org/10.1029/2022MS002997'),
    ('fong', 'Fong, E., Holmes, C. and Walker, S.G. (2023). Martingale posterior distributions. Journal of the Royal '
             'Statistical Society Series B 85(5), 1357–1391.', 'https://doi.org/10.1093/jrsssb/qkad005'),
    ('foster', 'Foster, A., Ivanova, D.R., Malik, I. and Rainforth, T. (2021). Deep adaptive design: amortizing '
               'sequential Bayesian experimental design. Proceedings of ICML 2021, PMLR 139, 3384–3395.',
     'https://arxiv.org/abs/2103.02438'),
    ('giordano', 'Giordano, R., Meager, R. and Broderick, T. (2026). An automatic finite-sample robustness metric: when '
                 'can dropping a little data change conclusions? Part II: theory and intuition. Philosophical '
                 'Transactions of the Royal Society A 384(2321), 20240614.', 'https://doi.org/10.1098/rsta.2024.0614'),
    ('gupta', 'Gupta, A. and Lermusiaux, P.F.J. (2023). Bayesian learning of coupled biogeochemical–physical models. '
              'Progress in Oceanography 216, 103050.', 'https://doi.org/10.1016/j.pocean.2023.103050'),
    ('hall', 'Hall, T., Scheidt, C., Wang, L., Yin, Z., Mukerji, T. and Caers, J. (2022). Sequential value of '
             'information for subsurface exploration drilling. Natural Resources Research 31(5), 2413–2434.',
     'https://doi.org/10.1007/s11053-022-10078-z'),
    ('huang1', 'Huang, D.Z., Schneider, T. and Stuart, A.M. (2022). Iterated Kalman methodology for inverse problems. '
               'Journal of Computational Physics 463, 111262.', 'https://doi.org/10.1016/j.jcp.2022.111262'),
    ('huang2', 'Huang, D.Z., Huang, J., Reich, S. and Stuart, A.M. (2022). Efficient derivative-free Bayesian inference '
               'for large-scale inverse problems. Inverse Problems 38(12), 125006.',
     'https://doi.org/10.1088/1361-6420/ac99fa'),
    ('huangd', 'Huang, D., Stein, N., Rubin, D.B. and Kou, S.C. (2020). Catalytic prior distributions with application to '
               'generalized linear models. Proceedings of the National Academy of Sciences 117(22), 12004–12010.',
     'https://doi.org/10.1073/pnas.1920913117'),
    ('huggins', 'Huggins, J.H. and Miller, J.W. (2024). Reproducible parameter inference using bagged posteriors. '
                'Electronic Journal of Statistics 18(1), 1549–1585.', 'https://doi.org/10.1214/24-EJS2237'),
    ('jacob', 'Jacob, P.E., O\'Leary, J. and Atchadé, Y.F. (2020). Unbiased Markov chain Monte Carlo methods with '
              'couplings. Journal of the Royal Statistical Society Series B 82(3), 543–600.',
     'https://doi.org/10.1111/rssb.12336'),
    ('kasprzak', 'Kasprzak, M.J., Giordano, R. and Broderick, T. (2025). How good is your Laplace approximation of the '
                 'Bayesian posterior? Finite-sample computable error bounds for a variety of useful divergences. Journal '
                 'of Machine Learning Research 26(87), 1–81.', 'https://arxiv.org/abs/2209.14992'),
    ('ko', 'Kennedy, M.C. and O\'Hagan, A. (2001). Bayesian calibration of computer models. Journal of the Royal '
           'Statistical Society Series B 63(3), 425–464.', 'https://doi.org/10.1111/1467-9868.00294'),
    ('kochkov', 'Kochkov, D., Yuval, J., Langmore, I., Norgaard, P., Smith, J., Mooers, G. et al. (2024). Neural general '
                'circulation models for weather and climate. Nature 632(8027), 1060–1066.',
     'https://doi.org/10.1038/s41586-024-07744-y'),
    ('miller', 'Miller, J.W. (2021). Asymptotic normality, concentration, and coverage of generalized posteriors. Journal '
               'of Machine Learning Research 22(168), 1–53.', 'https://arxiv.org/abs/1907.09611'),
    ('prescott', 'Prescott, T.P., Warne, D.J. and Baker, R.E. (2024). Efficient multifidelity likelihood-free Bayesian '
                 'inference with adaptive computational resource allocation. Journal of Computational Physics 496, '
                 '112577.', 'https://doi.org/10.1016/j.jcp.2023.112577'),
    ('russo', 'Russo, D. and Van Roy, B. (2022). Satisficing in time-sensitive bandit learning. Mathematics of Operations '
              'Research 47(4), 2815–2839.', 'https://doi.org/10.1287/moor.2021.1229'),
    ('vrugt', 'Vrugt, J.A. (2016). Markov chain Monte Carlo simulation using the DREAM software package: theory, '
              'concepts, and MATLAB implementation. Environmental Modelling & Software 75, 273–316.',
     'https://doi.org/10.1016/j.envsoft.2015.08.013'),
    ('wang', 'Wang, Y., Zechner, M., Mern, J.M., Kochenderfer, M.J. and Caers, J.K. (2022). A sequential decision-making '
             'framework with uncertainty quantification for groundwater management. Advances in Water Resources 166, '
             '104266.', 'https://doi.org/10.1016/j.advwatres.2022.104266'),
    ('white', 'White, J.T. (2018). A model-independent iterative ensemble smoother for efficient history-matching and '
              'uncertainty quantification in very high dimensions. Environmental Modelling & Software 109, 191–201.',
     'https://doi.org/10.1016/j.envsoft.2018.06.009'),
    ('wu', 'Wu, J.-L., Levine, M.E., Schneider, T. and Stuart, A.M. (2024). Learning about structural errors in models of '
           'complex dynamical systems. Journal of Computational Physics 513, 113157.',
     'https://doi.org/10.1016/j.jcp.2024.113157'),
    ('zahm', 'Zahm, O., Cui, T., Law, K., Spantini, A. and Marzouk, Y. (2022). Certified dimension reduction in nonlinear '
             'Bayesian inverse problems. Mathematics of Computation 91(336), 1789–1835.',
     'https://doi.org/10.1090/mcom/3737'),
    ('zeqiraj', 'Zeqiraj, D. (2026). Goal-oriented Bayesian experimental design for variable-density seawater intrusion: '
                'adjoint expected information gain for joint monitoring and managed-aquifer-recharge placement. Journal '
                'of Hydrology 680, 136559.', 'https://doi.org/10.1016/j.jhydrol.2026.136559'),
    ('ziomek1', 'Ziomek, J., Adachi, M. and Osborne, M.A. (2024). Bayesian optimisation with unknown hyperparameters: '
                'regret bounds logarithmically closer to optimal. Advances in Neural Information Processing Systems 37 '
                '(NeurIPS 2024).', 'https://proceedings.neurips.cc/paper_files/paper/2024/hash/'
                                   '9cf904c86cc5f9ac95646c07d2cfa241-Abstract-Conference.html'),
    ('ziomek2', 'Ziomek, J., Adachi, M. and Osborne, M.A. (2025). Time-varying Gaussian process bandits with unknown '
                'prior. Proceedings of AISTATS 2025, PMLR 258, 4294–4302.',
     'https://proceedings.mlr.press/v258/ziomek25a.html'),
]
R = {k: i + 1 for i, (k, _, _) in enumerate(REFS)}


def c(*keys):
    return '[' + ', '.join(str(R[k]) for k in keys) + ']'


# Table 1 of the calibration review: seven implicit assumptions and what replaces them
ASSUMPTIONS = [
    ['Derivatives come from finite differences and regularisation from a penalty; an ensemble update has no known '
     'limit', 'Kalman iterations whose fixed point is a Tikhonov solution or the posterior; Gauss–Newton steps in '
     'random subspaces', c('huang1', 'huang2', 'cartis')],
    ['Every likelihood evaluation needs a run of the full model', 'Emulators trained where the posterior is; posterior '
     'maps learned once; exactly unbiased multifidelity allocation', c('cleary', 'baptista', 'prescott')],
    ['The likelihood is the correct model of the data, and the prior acts on the parameters', 'Generalised posteriors '
     'with a coverage condition; bagged posteriors; martingale posteriors; priors on predictions',
     c('miller', 'huggins', 'fong', 'huangd')],
    ['Every data stream feeds back into every parameter', 'Cut and semi-modular inference with a tuned degree of '
     'feedback, computed without bias', c('carmona', 'jacob')],
    ['Structural error lives outside the model, as a discrepancy on the outputs', 'Error models inside the equations; '
     'model form as parameters; end-to-end calibration of hybrid models', c('wu', 'gupta', 'kochkov')],
    ['The data are given', 'Nonlinear design for all candidate networks from one ensemble; sequential design by a '
     'trained policy', c('dunbar', 'foster')],
    ['The linearised posterior, the chosen rank and the conclusions are trusted as computed', 'Certified subspaces; '
     'finite-sample bounds on the Laplace approximation; worst-case data-dropping audits',
     c('zahm', 'kasprzak', 'giordano')],
]

PEST_VS = [
    ['Structures', 'One, chosen in advance', 'Several competing structures, each an arm'],
    ['What is fitted and checked', 'The weighted misfit of all observations, plus a regularisation penalty',
     'The heads are fitted; each arm is checked against readings it has not seen, the sensitivity of the decision'],
    ['Flux scale', 'Fixed silently by the regulariser or by a flux held at an assumed value',
     'Fixed by metered pumping stops (Proposition 2)'],
    ['Model runs', '$N+1$ per iteration, all on the one structure', '$N_m+1$ per play, on the arm of smallest robust '
     'index; none on refuted structures'],
    ['Misspecification', 'Absorbed into the parameters: a good fit and an interval that is too narrow',
     'Raises the miss rate of the arm, which then loses its runs'],
    ['Uncertainty', 'Linear analysis that assumes the structure right', 'The Laplace interval of the kept structure, '
     'checked against held-out readings; the miss rate of every structure is reported'],
]
GITTINS_VS = [
    ['Arms', 'Abstract independent bandits', 'Competing structures of one physical model of the aquifer'],
    ['Cost of a play', 'A given Bernoulli process', 'The miss of a metered-stop reading by the arm\'s 90% predictive '
     'interval'],
    ['Meaning of the unknown probability', 'The rate of a bad outcome', 'A misspecification index of the structure, '
     'measured on the sensitivity of the decision'],
    ['Independence of the arms', 'Assumed', 'Built: each arm has its own runs and its own sequence of readings'],
    ['Objective', 'Discounted cumulative cost', 'Discounted misses within a budget of model runs, then one structure '
     'conditioned on all data'],
    ['Physics', 'None', 'Reciprocity (the reading is the sensitivity of the decision) and flux-scale invariance (the '
     'metered reading fixes the scale)'],
    ['Demonstrated on', 'Bernoulli bandits with 50 arms and 10⁴ plays', 'The Fushë-Kuqe aquifer model, in MATLAB'],
]


def main(out, resdir=None):
    from build_gar_doc import Eqs, display_eq
    import omml
    E = Eqs()
    BS._EQ = E
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    neq = [0]

    def eq(tex):
        neq[0] += 1
        display_eq(doc, E, tex, neq[0])

    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'CERTAIN-COAST — Calibration when the model is wrong', bold=True, size=18, color=NAVY)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Invariance-first calibration and TRIAL-GO, a robust bandit over model structures, demonstrated in MATLAB '
           'on the Fushë-Kuqe coastal aquifer', bold=True, size=12, color=NAVY)
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'NATO SPS Multi-Year Project, call 2027-1. Supplement to WP2 and WP4. Equations are native Word math; '
           'references were checked in Crossref.', italic=True, size=10, color=GREY)

    body(doc, 'Every forecast of CERTAIN-COAST rests on calibrated models, and every calibrated model is wrong in some way: '
              'the zones are coarser than the aquifer, a clay strip or a boundary is missing, a flux is fixed at a value '
              'nobody measured. This part asks what calibration should do when the model is misspecified. It summarises '
              'the 2020–2026 literature on calibration and on bandits, states the structural fact that heads alone '
              'cannot fix the flux scale, and proposes TRIAL-GO, a bandit whose arms are competing model structures, '
              'whose plays are calibration iterations checked against metered pumping stops, and whose allocation is '
              f'the robust Gittins index of Cohen and Treetanthiploet {c("ct22")}. The method is demonstrated in MATLAB '
              f'on the model of the Fushë-Kuqe coastal aquifer of the author\'s published design {c("zeqiraj")}.', E)
    box(doc, 'Innovation', 'TRIAL-GO turns calibration under misspecification into a bandit over model structures. A '
             'pumping stop at a supply well, at a metered rate, measures by reciprocity exactly the sensitivity on which '
             'the decision rests, and because the rate is metered it fixes the flux scale that heads cannot. The '
             'probability that a calibrated structure misses such readings therefore measures how wrong the structure '
             'is where it matters. The robust Gittins index, computed for that probability, decides which structure '
             'receives the next model runs, and the structure kept at the end is conditioned on all data. To our '
             'knowledge no published calibration method, PEST included, allocates its model runs between competing '
             'structures by such a misspecification index, and no Gittins-type bandit has arms tied to a physical model '
             'in this way; this is to be verified before any claim of priority.', E, fill='FDF3EA', bar='C55A11')

    # ---------------------------------------------------------------------------------------------- 1
    heading(doc, '1. The question: calibration when the model is wrong', 14)
    body(doc, 'Calibration estimates the parameters $\\theta$ of a groundwater model from heads, discharges and '
              'concentrations. With a model structure $m$ (a zonation, a set of boundaries, the fluxes left free) the '
              'data are', E, after=2)
    eq(r'd=G_m\left(\theta_m\right)+\delta_m+\varepsilon,\qquad \varepsilon\sim\mathcal{N}\left(0,\Gamma\right)')
    body(doc, 'where $\\delta_m$ is the structural error of structure $m$. Practice rests on four approaches: '
              f'regularised least squares with linear uncertainty analysis, PEST {c("doherty")}, which minimises', E,
         after=2)
    eq(r'\Phi_m(\theta)=\left\lVert\Gamma^{-1/2}\left(d-G_m(\theta)\right)\right\rVert^2+\mu\left\lVert R\left(\theta-'
       r'\theta_0\right)\right\rVert^2')
    body(doc, 'by Gauss–Levenberg–Marquardt with finite-difference Jacobians; iterative ensemble smoothers, PESTPP-IES '
              f'{c("white")}; Bayesian sampling with the full model, DREAM {c("vrugt")}; and an external model '
              f'discrepancy {c("ko")}. All four calibrate one structure and take for granted that it is right, or that '
              'its error is a stationary random field. Four kinds of misspecification are common in coastal aquifers:',
         E)
    for t in ['**M1, zonation too coarse:** heterogeneity below the scale of the zones, which no zone multiplier can '
              'represent.',
              '**M2, a missing feature:** a low-permeability coastal strip of lagoon clays, a leaky layer, or a boundary '
              'of the wrong type.',
              '**M3, a flux fixed at a wrong value:** recharge or abstraction held fixed during calibration, as is common '
              'to remove non-uniqueness; the heads are then fitted by compensating the conductivities.',
              '**M4, a wrong error model:** errors correlated in space and time treated as independent.']:
        bullet(doc, t, E)
    body(doc, 'In all four the fit to the heads can be good while the forecast of a new stress, more pumping or new '
              'recharge wells, is biased and its interval too narrow. In the synthetic check of the author\'s review of '
              'calibration (November 2026), a wrong single-zone structure covered the head at the divide in 0% of 200 '
              'data sets with its nominal 90% interval; tempering widened the interval twentyfold without covering it, a '
              f'Kennedy–O\'Hagan discrepancy {c("ko")} covered 48% with intervals 7 m wide, and the right structure '
              'covered 94%. Rescaling corrects the width of an interval, not its position: when the structure is wrong, '
              'only a better structure restores coverage.', E)

    # ---------------------------------------------------------------------------------------------- 2
    heading(doc, '2. The state of the art, 2020–2026', 14)
    body(doc, 'The author\'s review of twenty papers of 2020–2026 with authors at Oxford, Harvard, Caltech and MIT shows '
              'how each of seven implicit assumptions of standard calibration has been replaced by a mathematical result '
              '(Table 1).', E)
    p = para(doc, 2); run(p, 'Table 1. Seven implicit assumptions of standard calibration and what the 2020–2026 '
                             'literature puts in their place.', italic=True, size=9.5, color=GREY)
    t = table(doc, ['Implicit assumption', 'What replaces it', 'Papers'], ASSUMPTIONS, [6.2, 8.0, 2.8], size=9)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    para(doc, 4)
    body(doc, 'A second review by the author, on bandits and the value of information for siting managed aquifer '
              'recharge, gathered twenty papers of 2020–2026: bandit algorithms from Harvard and Oxford, the value of '
              'information in theory and in the subsurface. Correlated arms and stopping rules '
              f'{c("chick", "russo")}, priors and kernels that are themselves uncertain {c("ziomek1", "ziomek2")} and '
              f'sequential information in the subsurface {c("hall", "wang")} meet three open problems there: arms coupled '
              'through physics, a stop-and-build action and a test that informs many sites. Its innovation, SITE-GO, '
              'decides where to pilot-test and where to build recharge wells at Fushë-Kuqe; on 200 synthetic aquifers it '
              'lowered the probability that a supply well is intruded from 0.23 with the earlier closed form to 0.16, '
              'with about five pilot tests.', E)
    body(doc, 'For calibration under misspecification the key result is the robust Gittins index of Cohen and '
              f'Treetanthiploet {c("ct22")} (Oxford). For independent arms whose costs are evaluated by a nonlinear '
              'expectation, which encodes uncertainty about the law of each arm (Knightian uncertainty), they prove that '
              'always playing the arm of smallest robust index is optimal in a sense they call C-optimality, and they '
              'give a numerical algorithm for Bernoulli costs with a credible set from a Beta posterior. Their index is '
              'optimistic or pessimistic depending on the regime: a larger credible level makes it more conservative, '
              'so it favours exploiting over exploring. None of the works of the two reviews calibrates a groundwater '
              'model by a bandit, and none has arms that are competing model structures checked against the data the '
              'decision depends on.', E)

    # ---------------------------------------------------------------------------------------------- 3
    heading(doc, '3. Invariance-first calibration', 14)
    body(doc, 'Before any method is chosen, one property of groundwater models limits what calibration can achieve '
              '(the author\'s review of calibration). For flow with storage $S$, transmissivity $T$, recharge $r$, '
              'abstraction $Q_w$ and boundary conductances $C$,', E, after=2)
    eq(r'S\,\partial_t h=\nabla\cdot\left(T\nabla h\right)+r-\sum_w Q_w\,\delta_{x_w},\qquad -T\nabla h\cdot n=C\,'
       r'\left(h-H\right)\ \text{on }\Gamma_R')
    body(doc, '**Proposition 1 (flux-scale invariance).** If the problem has a unique solution, multiplying all '
              'flux-type parameters by any $c>0$ leaves the head field unchanged, steady or transient; in logarithmic '
              'parameters the Jacobian of any set of heads annihilates the direction $\\mathbf{1}$ of the flux-type '
              'parameters:', E, after=2)
    eq(r'h\left(\cdot\,;c\,\theta_{\mathrm{flux}}\right)=h\left(\cdot\,;\theta_{\mathrm{flux}}\right),\qquad J\,'
       r'\mathbf{1}=0')
    body(doc, 'so heads alone never fix the flux scale; only a measured flux, or prior knowledge of one flux-type '
              'parameter, does (multiplying the equation and its flux conditions by $c$ gives the same problem for the '
              'same heads). **Corollary 1.** With prior variance $\\sigma_t^2$ of the common scale and one log flux '
              'measured with error $s$,', E, after=2)
    eq(r'\mathrm{EIG}(Q)\ge\tfrac12\,\log\left(1+\frac{\sigma_t^2}{s^2}\right),\qquad \mathrm{Var}\left(t\mid'
       r'\text{heads},Q\right)\ge\left(\sigma_t^{-2}+s^{-2}\right)^{-1}')
    body(doc, 'with equality when the heads determine the other parameters; no number of additional heads reduces this '
              'variance. In the review\'s synthetic check one discharge measured to 10% gave 1.77 nats and reduced the '
              'variance of log recharge by 97%, where the best additional head gave 0.32 nats and nothing for the scale. '
              'The protocol that follows: list the invariances before calibrating (multiply a candidate family by 2 and '
              'compare the heads), measure fluxes before adding piezometers, calibrate with a method of known limit '
              f'{c("huang1", "huang2")}, upgrade the structure where a data-dropping audit points {c("giordano")}, '
              f'and certify what can be certified {c("zahm", "kasprzak")}. TRIAL-GO is the step of this protocol that '
              'chooses the structure.', E)

    # ---------------------------------------------------------------------------------------------- 4
    heading(doc, '4. TRIAL-GO: a robust calibration bandit over model structures', 14)
    heading(doc, '4.1 The arms, the plays and the readings', 12, color=BLUE, before=6)
    body(doc, 'TRIAL-GO keeps several structures $m=1,\\dots,M$ in play, each with its parameters $\\theta_m$, its '
              'prior $\\mathcal{N}(0,\\Gamma_m)$ and its Laplace posterior. A play of arm $m$ buys one '
              'Levenberg–Marquardt iteration of its calibration on the heads, $N_m+1$ model runs for the '
              'finite-difference Jacobian as in PEST, and checks the arm against one reading it has not seen. The '
              'readings come from a **metered pumping stop**: the pumping of supply well $w$ is stopped at a metered '
              'rate $\\Delta Q_w$ and the change of head is read at observation well $j$,', E, after=2)
    eq(r'y_{wj}=\Delta Q_w\,g_w(j)+\varepsilon_{wj},\qquad g_w(j)=e_w^{\top}A_\theta^{-1}e_j=e_j^{\top}A_\theta^{-1}e_w')
    body(doc, '**Proposition 2 (what a metered stop measures).** (i) The steady flow matrix $A_\\theta$ is symmetric, so '
              'the response at $j$ to a pumping change at $w$ equals the change of head at $w$ per unit recharge at $j$: '
              'the reading measures the very sensitivity that ranks recharge sites and sets the risk of the supply well. '
              '(ii) Under the flux-scale invariance of Proposition 1, which leaves every head unchanged, the reading '
              'changes as', E, after=2)
    eq(r'y_{wj}\left(c\,\theta_{\mathrm{flux}}\right)=\frac{1}{c}\,y_{wj}\left(\theta_{\mathrm{flux}}\right)')
    body(doc, 'because $\\Delta Q_w$ is metered and does not scale, so the readings fix the flux scale that the heads '
              'cannot. *Proof.* (i) Each face conductance enters the two rows of its cells with the same value, so '
              '$A_\\theta=A_\\theta^{\\top}$. (ii) Scaling the flux-type parameters multiplies the equations of the '
              'active cells, recharge included, by $c$ and leaves the fixed-head rows unchanged, so the heads are the '
              'same; the response to the unscaled $\\Delta Q_w$ is divided by $c$. ∎ The readings are Stage 0 of '
              'SITE-GO: two pumping stops of a few days at the supply wells, read by pressure loggers in the existing '
              'wells, with no drilling.', E)
    heading(doc, '4.2 The misspecification index', 12, color=BLUE, before=6)
    body(doc, 'The cost of a play is a miss: $h=1$ if the reading falls outside the arm\'s 90% predictive interval, '
              'computed from its Laplace posterior and the reading noise, and $h=0$ otherwise. The probability of a miss',
         E, after=2)
    eq(r'p_m=\Pr\left[\,y\notin I_m^{0.9}\,\right]')
    body(doc, 'is the nominal 0.1 for a structure that is right (exactly so in the linear-Gaussian case); a wrong '
              'structure that is confident where it is wrong misses more often. $p_m$ is therefore a misspecification '
              'index of the structure, measured on the sensitivity of the decision rather than on the fit to all heads. '
              'TRIAL-GO learns it from the misses of each arm.', E)
    heading(doc, '4.3 The robust Gittins index', 12, color=BLUE, before=6)
    body(doc, f'Cohen and Treetanthiploet {c("ct22")} define, for costs $h(t)$ evaluated by a nonlinear expectation, the '
              'robust Gittins index of an arm at time $s$, and show (their Theorem 4.2) that', E, after=2)
    eq(r'\gamma(s)=\underset{\tau}{\mathrm{ess\,inf}}\ \underset{\mathbb{Q}\in\mathcal{Q}}{\mathrm{ess\,sup}}\ '
       r'\frac{\mathbb{E}^{\mathbb{Q}}\left[\sum_{t=1}^{\tau}\beta^{t}h(s+t)\mid\mathcal{F}_s\right]}{\mathbb{E}^{'
       r'\mathbb{Q}}\left[\sum_{t=1}^{\tau}\beta^{t}\mid\mathcal{F}_s\right]}')
    body(doc, 'with $\\beta$ a discount factor; playing always the arm of smallest index is C-optimal for independent '
              'arms (their Theorem 4.3). For Bernoulli costs they evaluate the next step by the data-driven robust '
              'expectation', E, after=2)
    eq(r'\mathcal{E}_{(t)}(f)=\sup_{\vartheta\in\left[p^-,\,p^+\right]}\left[\vartheta f(1)+(1-\vartheta)f(0)\right],'
       r'\qquad p^{\pm}=I^{-1}_{\left(p_t n_t,\,(1-p_t)n_t\right)}\left(\tfrac12\pm\tfrac{k}{2}\right)')
    body(doc, 'where $I^{-1}$ is the quantile function of the Beta law and $k$ the credible level, which sets the '
              'aversion to uncertainty, and compute the index by backward induction on a grid of $\\gamma$ (their '
              'Appendix D):', E, after=2)
    eq(r'V_t^{\gamma}=\min\left\{0,\ \mathcal{E}_{(t)}\left[(h-\gamma)+\beta V_{t+1}^{\gamma}\right]\right\},\qquad '
       r'\gamma_{k,\beta,T}\left(p,\tfrac{1}{\sqrt{n}}\right)=\min\left\{\gamma:\ U\left(\gamma,p,\tfrac{1}{\sqrt{n}}'
       r'\right)\le 0\right\}')
    body(doc, 'with $U$ the value of the first, forced play. TRIAL-GO uses this algorithm as written, implemented in '
              'MATLAB, with the miss of a reading as the Bernoulli cost.', E)
    heading(doc, '4.4 The algorithm', 12, color=BLUE, before=6)
    for t in ['**Set up.** Choose the candidate structures (zonations, coastal features, which fluxes are free) and '
              'their priors; take the heads and the metered pumping stops read at the observation wells; fix a budget '
              '$B$ of model runs and the parameters $k$, $\\beta$ and $H$ of the index.',
              '**Start.** Play every arm once.',
              '**Index.** For each arm, from its $s_m$ misses in $n_m$ readings, $p_m=(s_m+\\tfrac12)/(n_m+1)$ and '
              '$\\gamma_m=\\gamma_{k,\\beta,H}\\left(p_m,1/\\sqrt{n_m+1}\\right)$.',
              '**Play.** Play the arm of smallest index: one calibration iteration ($N_m+1$ runs, none once it has '
              'converged) and one new reading from its own random sequence; record the miss.',
              '**Stop and condition.** When the budget is spent, keep the arm of lowest miss rate among those with at '
              'least five readings, calibrate it on all data (heads and every reading) and give its forecast of the '
              'decision quantity with its interval.']:
        bullet(doc, t, E)
    eq(r'm_{t+1}=\underset{m}{\arg\min}\ \gamma_{k,\beta,H}\left(\frac{s_m+\frac12}{n_m+1},\ \frac{1}{\sqrt{n_m+1}}'
       r'\right),\qquad \sum_t\left(N_{m_t}+1\right)\le B')
    heading(doc, '4.5 Why the index theorem applies, and where it is approximate', 12, color=BLUE, before=6)
    body(doc, 'The robust Gittins theorem needs independent arms. TRIAL-GO makes them independent by construction: each '
              'arm\'s calibration uses only its own runs and each arm draws its readings from its own random sequence, '
              'so the cost stream of one arm does not depend on the plays of another. The approximation is that misses '
              'are not identically distributed while an arm is still converging: its miss probability falls during the '
              'first iterations and then settles at the level its structure allows. The index treats the misses as '
              f'Bernoulli with a fixed unknown probability, the same model as the numerical study of {c("ct22")}.', E)
    heading(doc, '4.6 How it works in the system', 12, color=BLUE, before=6)
    nfig = [0]
    scheme = os.path.join(HERE, 'matlab_figs', 'fig_trial_go_scheme.png')
    if os.path.exists(scheme):
        nfig[0] += 1
        body(doc, f'Figure {nfig[0]} shows the loop and where it sits in the system.', E)
        figure(doc, scheme, f'Figure {nfig[0]}. How TRIAL-GO works in the CERTAIN-COAST system: the data (heads and '
               'metered pumping stops), the competing model structures (arms), the loop of the robust calibration '
               'bandit, the stop with the conditioning of the kept structure, and the decisions it feeds. Drawn with '
               'the author\'s MATLAB code (trial_go_scheme.m).')
    for t in ['**WP2, the coupled model.** The calibration of the flow and transport model of each site runs through '
              'TRIAL-GO: the zonations, coastal features and free fluxes proposed by the hydrogeologists are the arms, '
              'and no runs are spent on structures that the readings refute.',
              '**WP4, the network.** The metered pumping stops at the supply wells enter the monitoring plan (Stage 0, no '
              'drilling): the same readings test the structures, fix the flux scale and give the sensitivities that '
              'rank recharge sites and monitoring wells (Part 7, Section 6).',
              '**WP5, live operation.** When new readings arrive the arms are re-indexed; a structure whose miss rate '
              'rises is replaced before its forecasts mislead the warnings and the recommended decisions.',
              '**Decisions.** The kept structure gives the risk at the supply wells, the recharge sites of SITE-GO and '
              'the environment of the deep reinforcement learning agent of Part 7 an interval that has been checked '
              'against the readings that matter.']:
        bullet(doc, t, E)
    heading(doc, '4.7 What it gives', 12, color=BLUE, before=6)
    for t in ['Model runs go where the structure is plausible: a structure that misses the readings stops consuming runs.',
              'Misspecification is measured where it matters, on the sensitivities of the supply wells, not on the fit '
              'to all heads.',
              'The flux scale is fixed by metered stops at no drilling cost (Proposition 2), which heads cannot do '
              '(Proposition 1).',
              'The miss rate of every structure is reported, so the decision-maker sees which structures the data refute '
              'and why the kept one was kept.',
              'The allocation has a guarantee: the robust Gittins theorem holds for it, within the approximation of '
              'Section 4.5.']:
        bullet(doc, t, E)
    heading(doc, '4.8 What changes against PEST and against the robust Gittins index', 12, color=BLUE, before=6)
    p = para(doc, 2); run(p, 'Table 2. PEST and TRIAL-GO.', italic=True, size=9.5, color=GREY)
    t = table(doc, ['', 'PEST (Gauss–Levenberg–Marquardt)', 'TRIAL-GO'], PEST_VS, [3.2, 6.6, 7.2], size=9)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    para(doc, 6)
    p = para(doc, 2); run(p, f'Table 3. The robust Gittins index of Cohen and Treetanthiploet {c("ct22")} and '
                             'TRIAL-GO.', italic=True, size=9.5, color=GREY)
    t = table(doc, ['', 'Robust Gittins index (2022)', 'TRIAL-GO'], GITTINS_VS, [3.2, 6.0, 7.8], size=9)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    para(doc, 4)

    # ---------------------------------------------------------------------------------------------- 5
    txt_path = os.path.join(HERE, 'matlab_figs', 'trial_go_text.json')
    if resdir and os.path.exists(txt_path):
        with open(txt_path, encoding='utf-8') as fh:
            TX = json.load(fh)
        heading(doc, '5. Demonstration on the Fushë-Kuqe coastal aquifer (MATLAB)', 14)
        def refs(t):                               # {ref:key} -> the number of the reference in this part
            return re.sub(r'\{ref:(\w+)\}', lambda m: c(m.group(1)), t)
        for blk in TX['blocks']:
            if 'text' in blk:
                blk = dict(blk, text=refs(blk['text']))
            kind = blk['kind']
            if kind == 'heading':
                heading(doc, blk['text'], 12, color=BLUE, before=6)
            elif kind == 'text':
                body(doc, blk['text'], E)
            elif kind == 'bullet':
                bullet(doc, blk['text'], E)
            elif kind == 'eq':
                eq(blk['tex'])
            elif kind == 'figure':
                nfig[0] += 1
                src = blk['file'] if os.path.isabs(blk['file']) else os.path.join(resdir, blk['file'])
                figure(doc, src, f'Figure {nfig[0]}. ' + blk['caption'], width=blk.get('width', 16.0))
            elif kind == 'table':
                p = para(doc, 2); run(p, blk['title'], italic=True, size=9.5, color=GREY)
                t = table(doc, blk['header'], blk['rows'], blk['widths'], size=9)
                t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
                para(doc, 4)
        heading(doc, '6. Conclusions', 14)
        for t in TX['conclusions']:
            bullet(doc, refs(t), E)
        body(doc, f'The repository [github.com/dulianzeqiraj/certain-coast]({CODE}) (branch nato-sps-2027) holds '
                  'TRIAL-GO as the package certaincoast.calibration of the open-source MATLAB code of the project: the '
                  'robust Gittins index, the Levenberg–Marquardt calibration of each structure with its prior and the '
                  'bandit with its checks against metered pumping stops, with an example on a synthetic coastal aquifer '
                  'and tests that pass in MATLAB and in GNU Octave. The Fushë-Kuqe data of the demonstration are '
                  'restricted and are not published there.', E)

    heading(doc, 'References', 14)
    for i, (_, cite, url) in enumerate(REFS, 1):
        p = para(doc, 3); p.paragraph_format.left_indent = Cm(0.7); p.paragraph_format.first_line_indent = Cm(-0.7)
        run(p, f'[{i}]  ', bold=True, size=10, color=NAVY); run(p, cite + ' ', size=10)
        if url:
            link(p, url, url.replace('https://', ''), 10)
    p = para(doc, 4, before=6)
    run(p, 'Verification note. The references come from the author\'s reviews of calibration and of bandits (November '
           '2026), where they were checked against Crossref, publisher pages and arXiv; Cohen and Treetanthiploet '
           '(2022), Kennedy and O\'Hagan (2001), White (2018) and Zeqiraj (2026) were checked in Crossref for this part. '
           'Propositions 1 and 2 and Corollary 1 are the author\'s analysis. The part was drafted with the help of an '
           'AI assistant.', italic=True, size=9.5, color=GREY)

    BS._EQ = None
    work = tempfile.mkdtemp()
    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh)
    omml.main(draft, eq_json, out)
    import polish_parts as PP
    d = Document(out)
    n_red, _ = PP.colour_equations(list(d.element.body), PART_INDEX)
    d.save(out)
    print('saved', out, '|', len(E.items), 'equations |', neq[0], 'numbered |', n_red, 'in red |', nfig[0], 'figures')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Calibration_TRIAL-GO.docx',
         sys.argv[2] if len(sys.argv) > 2 else None)
