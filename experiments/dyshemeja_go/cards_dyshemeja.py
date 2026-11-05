"""The twenty paper cards of the sixth state-of-the-art review (five per institution), from the verification notes of
four literature searches (November 2026), and the rows of its state-of-the-art table. Landing pages were reached through
search results only (doi.org, arxiv.org and most publisher hosts were blocked), so every card is marked partly verified
unless its status says otherwise. None of the twenty was a card of reviews I–V or of the earlier reviews of the series.

Fields as in ../matja_go/cards_matja.py, plus an optional 'status'. Text conventions: $math$, **bold**, *italic*;
[[np]], [[dec]] refer to equations of Section 4. The numbers in the innovation steps come from res/dyshemeja.json."""

OXFORD = [
    dict(id='O1', inst='Oxford', year=2024, short='Expected size of conformal sets',
         title='On the expected size of conformal prediction sets',
         authors='Guneet S. Dhillon, George Deligiannidis, Tom Rainforth',
         venue='Proceedings of the 27th International Conference on Artificial Intelligence and Statistics (AISTATS '
               '2024), PMLR 238, 1549–1557',
         links=[('PMLR 238', 'https://proceedings.mlr.press/v238/dhillon24a.html'),
                ('arXiv:2306.07254', 'https://arxiv.org/abs/2306.07254')],
         evidence='All three authors at the Department of Statistics, University of Oxford (search summary of the arXiv '
                  'and PMLR listings); the printed byline was not seen.',
         does='**Result (abstract wording).** The expected size of split-conformal prediction sets is quantified '
              'theoretically; because the exact quantity is usually not computable, point estimates and high-probability '
              'interval bounds that can be computed empirically are derived, and they need the data to be collected only '
              'once. The bounds are tested on real regression and classification datasets (numbers and exact '
              'assumptions not seen).',
         sota='The first finite-sample, data-computable account of the expected size, not only the coverage, of '
              'conformal sets.',
         gap='No comparison with an oracle set or lower bound; no risk control or drift.',
         inputs='Estimate, with an interval, the expected width of the bands for $T$, $S$, $\\kappa$ and $\\tau$ '
                'calibrated on simulations or anchors.',
         dispersion='The same for bands on the dispersivity and the transition-zone width.',
         bcs='The expected width of the sea-level, inflow and initial-interface bands with rain only, before a logger '
             'is installed.',
         step='Their size estimate is the numerator of the efficiency ratio of Proposition F2 and the floor of '
              'Proposition F1 its denominator: together they give an efficiency with error bars. Without shift the '
              '20-anchor band is 1.33–1.54 times the floor (T18); their interval bound says how much of that ratio is '
              'sampling noise of the anchors and how much is a lasting cost.',
         steps=['guarantee', 'check'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='O2', inst='Oxford', year=2025, short='Data-free bounds on target averages',
         title='Bridging the gap between SOLA and deterministic linear inferences in the context of seismic tomography',
         authors='Adrian Mag, Christophe Zaroli, Paula Koelemeijer',
         venue='Geophysical Journal International 242(1), ggaf131 (2025)',
         links=[('doi:10.1093/gji/ggaf131', 'https://doi.org/10.1093/gji/ggaf131'),
                ('Oxford ORA', 'https://ora.ox.ac.uk/objects/uuid:60db7bf5-7dbc-4adf-8e45-7d7a91f6ea28')],
         evidence='Deposited in Oxford\'s repository ORA; the printed affiliations were not seen.',
         does='**Result.** SOLA (subtractive optimally localized averages, a Backus–Gilbert method) is combined with '
              'deterministic linear inference, which bounds linear properties of a model under a norm-bound prior; the '
              'combined framework reads results through target kernels instead of imperfect resolving kernels while '
              'keeping the trade-offs between parameters. One case study shows that resolution and trade-off analysis can '
              'be done when no data values or errors are available. The method is for linear or linearised problems and '
              'the tests assume error-free data; no formal theorem statement was seen.',
         sota='Design-stage, data-free bounds on chosen target averages that unify two schools of linear inference.',
         gap='Linear; worst-case rather than probabilistic; noise-free tests; not applied to groundwater.',
         inputs='Linearise the map from ($\\log T$, $S$, $\\kappa$, $\\tau$) to the few heads: under a stated norm bound '
                'the bound on a zone average of $T$ is a deterministic floor, computable for candidate logger sites '
                'before they are installed.',
         dispersion='The same for a target average over the mixing zone, with chloride facts as linearised functionals.',
         bcs='The inland inflow as a linear property of rain-driven heads: the bound shows what rain alone and each '
             'added logger buy, without data.',
         step='Their bound is the worst-case, deterministic twin of the floor of Proposition F1, which is exact and '
              'probabilistic under a law. Both can be computed at the design stage (Proposition F3 (iii)); computed for '
              'the same target kernel, their difference separates what the norm bound and what the prior law contribute '
              'to the floor of a design.',
         steps=['design', 'invert'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='O3', inst='Oxford', year=2022, short='Only a time scale and a gain identifiable',
         title='Identifiability of lithium-ion battery electrolyte dynamics',
         authors='Luis D. Couto, Ross Drummond, Dong Zhang, Toby Kirk, David A. Howey',
         venue='2022 American Control Conference (ACC), 1087–1093',
         links=[('doi:10.23919/ACC53348.2022.9867154', 'https://doi.org/10.23919/ACC53348.2022.9867154'),
                ('Oxford ORA', 'https://ora.ox.ac.uk/objects/uuid:7e1e9962-2366-4821-ada3-3c7fc26db075')],
         evidence='Deposited in Oxford\'s repository ORA; the per-author affiliations were not seen.',
         does='**Result.** Assuming equal electrolyte volume fractions in electrode and separator, an analytic impedance '
              '(transfer function) is derived for the diffusion dynamics and tested for structural identifiability: only '
              'the diffusion time scale and a geometric coupling parameter are identifiable, and simulations show '
              'identifiability problems for symmetric cells.',
         sota='A closed-form structural-identifiability check for the impedance of a diffusion equation driven and '
              'observed at its boundaries.',
         gap='A battery model at a conference; the aquifer analogy is our inference.',
         inputs='The same structure as recharge in and heads out: the linear response identifies a diffusive time scale '
                '(about $L^2S/T$) and one gain (about $\\kappa/S$), not $T$ and $S$ separately (our inference); a pumping '
                'test, the tidal response or a known sea forcing is needed to separate them.',
         dispersion='None.',
         bcs='The inflow gain and the time scale trade off unless the boundary forcing is known.',
         step='Where a combination is not identifiable, the floor of Proposition F1 stays at the prior: no method can '
              'narrow a band for $T$ alone below its prior width from rain and heads, while a band for the identifiable '
              'time scale can shrink. Computing the floor of both gives a number for the identifiability gap of a design, '
              'and the design that closes it.',
         steps=['invert', 'design'], informs=dict(inputs=2, dispersion=0, bcs=1)),
    dict(id='O4', inst='Oxford', year=2025, short='Stable CUR with oversampling',
         title='Accuracy and stability of CUR decompositions with oversampling',
         authors='Taejun Park, Yuji Nakatsukasa',
         venue='SIAM Journal on Matrix Analysis and Applications 46(1), 780–810 (2025)',
         links=[('doi:10.1137/24M1660346', 'https://doi.org/10.1137/24M1660346'),
                ('arXiv:2405.06375', 'https://arxiv.org/abs/2405.06375')],
         evidence='Deposited in Oxford\'s repository ORA; the printed affiliations were not seen.',
         does='**Result.** The square cross-approximation CUR can be unstable because its core may be nearly singular; '
              'the authors prove error bounds for it and for an ε-pseudoinverse variant with oversampling, show that the '
              'oversampled variant is numerically stable under roundoff, and recommend oversampling in proportion to the '
              'target rank (the exact form of the bound was not seen).',
         sota='A stable, oversampled CUR with error guarantees.',
         gap='Deterministic; no posterior or coverage link.',
         inputs='Choose logger sites as rows of an ensemble head matrix: install somewhat more loggers than the number '
                'of modes to resolve, with the ε-truncation as the noise floor.',
         dispersion='The same row selection for chloride sampling points.',
         bcs='Reconstruct the modes of the sea boundary and the inflow from a few sites.',
         step='Use CUR to propose designs and the floor to price them. In T20 the floor of the inflow fell to '
              '<<q1>> of its rain-only width with one logger and <<q4>> with four; a CUR choice of four oversampled '
              'sites can be compared with the four fixed sites of reviews I–V by the same floor.',
         steps=['design'], informs=dict(inputs=1, dispersion=1, bcs=2)),
    dict(id='O5', inst='Oxford', year=2025, short='Conformal sets as scenario programs',
         title='Bridging conformal prediction and scenario optimization',
         authors='Niall O\'Sullivan, Licio Romao, Kostas Margellos',
         venue='arXiv:2503.23561 (preprint, 2025)',
         links=[('arXiv:2503.23561', 'https://arxiv.org/abs/2503.23561'),
                ('Oxford ORA', 'https://www.ora.ox.ac.uk/objects/uuid:a4d09400-714e-4216-bf14-9d8e71901964')],
         evidence='Deposited in Oxford\'s repository ORA. Preprint; no journal version was confirmed.',
         does='**Result.** With suitable score functions and set-predictor maps, plain conformal prediction recovers the '
              'known bounds on the probability of constraint violation of scenario programs; conversely, ranking the '
              'nonconformity scores is a one-dimensional scenario program with discarded constraints, which recovers '
              'conformal validity. Using the distribution of the violation probability, not only its mean, gives '
              'calibration-conditional bounds (their Theorem 6; the full assumptions were not seen).',
         sota='An exact two-way equivalence between conformal prediction and scenario optimisation, with '
              'calibration-conditional guarantees.',
         gap='Preprint; nothing on the size of the sets or on drift.',
         inputs='With a handful of anchors, their Theorem 6 gives the probability that the miscoverage exceeds a chosen '
                'level: how much the bands must be inflated and how many anchors are needed.',
         dispersion='The same for dispersivity bands.',
         bcs='Pumping or sea-level rules certified over sampled rain years and the conformal bands can share one '
             'certificate.',
         step='Their calibration-conditional bound is the certificate version of the calibration factor of '
              'Proposition F2: with 20 anchors that factor averages 1.10–1.17 (T18); their Theorem 6 says how large it '
              'must be for a 90% certificate rather than on average, the question Proposition A2 of review IV answers '
              'with 22 anchors.',
         steps=['guarantee'], informs=dict(inputs=2, dispersion=1, bcs=1)),
]

CALTECH = [
    dict(id='C1', inst='Caltech', year=2023, short='Constrained intervals; Burrus refuted',
         title='Optimization-based frequentist confidence intervals for functionals in constrained inverse problems: '
               'resolving the Burrus conjecture',
         authors='Pau Batlle, Pratik Patil, Michael Stanley, Houman Owhadi, Mikael Kuusela',
         venue='arXiv:2310.02461 (preprint, 2023; revised 2024)',
         links=[('arXiv:2310.02461', 'https://arxiv.org/abs/2310.02461'),
                ('project page', 'https://stat.cmu.edu/~mcstanle/publication/opt_based_conf')],
         evidence='H. Owhadi: Caltech; the work is part of P. Batlle\'s Caltech PhD thesis; one listing gives P. Patil at '
                  'UC Berkeley Statistics. The paper\'s own affiliation lines were not seen. Preprint.',
         does='**Theorem (as summarised).** Intervals for a functional of a constrained parameter are built by inverting '
              'a constrained likelihood-ratio test, which turns coverage into type I error control, non-asymptotically, '
              'one functional at a time. The Burrus conjecture — that a χ²(1)-quantile calibration gives valid intervals '
              'for possibly rank-deficient linear Gaussian models with positivity constraints — is refuted by a '
              'counterexample built on a stochastic-dominance argument, which also disproves a general form of it.',
         sota='Settles a decades-old conjecture and makes test inversion the correct construction for constrained '
              'linear-Gaussian inverse problems.',
         gap='Linear model with known Gaussian noise; no nonlinearity or model error; preprint.',
         inputs='$T$, $S$, $\\kappa$ and $\\tau$ carry positivity or box constraints: the construction gives valid '
                'frequentist intervals for linearised functionals of them, and warns that the χ²(1) shortcut can '
                'undercover.',
         dispersion='Dispersivity and transition-zone width are positive functionals once chloride is linearised.',
         bcs='Positive functionals of the rain-driven model, such as the annual inflow or recharge, get valid intervals; '
             'the constraints carry information the rain alone lacks.',
         step='Their intervals are valid for every parameter value; the floor of Proposition F1 is the narrowest band '
              'valid on average under a law. Both are needed and differ in what they promise: for $\\kappa$ with rain '
              'alone the floor is <<krain>> (T20), the prior width, and their constrained interval would show how much '
              'more a guarantee at every $\\kappa$ costs.',
         steps=['guarantee', 'invert'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='C2', inst='Caltech', year=2025, short='Simultaneous regions for many functionals',
         title='Simultaneous frequentist calibration of confidence regions for multiple functionals in constrained '
               'inverse problems',
         authors='Pau Batlle, Pratik Patil, Michael Stanley, Javier Ruiz Lupon, Houman Owhadi, Mikael Kuusela',
         venue='arXiv:2510.11708 (preprint, 2025)',
         links=[('arXiv:2510.11708', 'https://arxiv.org/abs/2510.11708')],
         evidence='H. Owhadi: Caltech; the affiliation lines were not seen. Preprint.',
         does='**Theorem (as summarised).** Test inversion is extended from one functional to several at once: optimal '
              'calibration constants are derived for several joint test statistics, and the resulting regions keep '
              'finite-sample frequentist coverage while being uniformly less conservative than classical simultaneous '
              'strict bounds. Algorithms include reductions for high dimension and a row–null splitting for '
              'rank-deficient models; experiments report nominal coverage with substantially smaller regions (volume '
              'ratios not seen).',
         sota='Optimal simultaneous calibration of confidence regions for several functionals of a constrained inverse '
              'problem.',
         gap='Linear Gaussian; preprint; numbers not seen.',
         inputs='A joint region for ($T$, $S$, $\\kappa$, $\\tau$): the right comparator for joint risk-controlling sets.',
         dispersion='The dispersivity can enter the same joint region.',
         bcs='Simultaneous bands over yearly recharge, inflow and initial interface.',
         step='Proposition F1 extends to joint sets with the same proof, the threshold now on the joint posterior '
              'density, so a joint floor for ($r$, $q_L$, $\\eta$, $\\kappa$) can be computed in our test bed. With their '
              'regions and a joint calibration of the four bands it gives a three-way comparison: Bayesian floor, '
              'frequentist optimum and conformal practice, on the same data.',
         steps=['guarantee'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='C3', inst='Caltech', year=2023, short='How far a posterior moves when inputs do',
         title='Bayesian posterior perturbation analysis with integral probability metrics',
         authors='Alfredo Garbuno-Iñigo, Tapio Helin, Franca Hoffmann, Bamdad Hosseini',
         venue='arXiv:2303.01512 (preprint, 2023)',
         links=[('arXiv:2303.01512', 'https://arxiv.org/abs/2303.01512v1')],
         evidence='F. Hoffmann: Caltech (search summary of the arXiv text). Preprint; no journal version found.',
         does='**Theorem (as summarised).** The posterior is stable under perturbations of the likelihood potential, the '
              'data and the prior, measured in new families of integral probability metrics (Wasserstein as a special '
              'case), for likelihoods that are only locally Lipschitz and without requiring the prior and its '
              'perturbation to be equivalent, which total-variation and Hellinger results need. The constants were not '
              'seen.',
         sota='Posterior stability beyond equivalent priors and globally Lipschitz likelihoods.',
         gap='Preprint; constants not seen; no lower bound.',
         inputs='An error budget for how far the exact posterior, and so the floor, moves when an emulator replaces the '
                'model or when the priors of $T$, $S$ and $\\kappa$ are learned.',
         dispersion='The posterior shift when literature dispersivity priors are swapped.',
         bcs='The data-perturbation part bounds the posterior shift caused by errors in the rain series.',
         step='The floor is computed under a working law, and their bound says how far it can move when that law is '
              'perturbed: it turns the main limitation of Proposition F1 into a number. In T19 the recharge floor moved '
              'from 0.0439 to 0.0491 mm/d (+12%) between the simulator\'s law and the shifted parameters; a stability '
              'bound of their kind would cap such moves before the real law is known.',
         steps=['invert', 'check'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='C4', inst='Caltech', year=2020, short='Randomized linear algebra, certified',
         title='Randomized numerical linear algebra: foundations and algorithms',
         authors='Per-Gunnar Martinsson, Joel A. Tropp',
         venue='Acta Numerica 29, 403–572 (2020)',
         links=[('doi:10.1017/S0962492920000021', 'https://doi.org/10.1017/S0962492920000021'),
                ('arXiv:2002.01387', 'https://arxiv.org/abs/2002.01387'),
                ('CaltechAUTHORS', 'https://resolver.caltech.edu/CaltechAUTHORS:20201217-104322985')],
         evidence='J. A. Tropp: Caltech (CaltechAUTHORS record); P.-G. Martinsson: UT Austin.',
         does='**Result.** A survey of the theory and algorithms of randomized linear algebra: error bounds for the '
              'randomized range finder and singular value decomposition, Nyström approximation, norm and trace '
              'estimation, and a posteriori error estimation. The standard range-finder bound states that with a '
              'Gaussian test matrix of $k+p$ columns the expected Frobenius error is at most $(1+k/(p-1))^{1/2}$ times '
              'the best rank-$k$ error (its exact form in the survey was not checked).',
         sota='The reference theorem base for randomized low-rank computation in uncertainty quantification and design.',
         gap='Not specific to design; linear or linearised posteriors.',
         inputs='With few heads the prior-preconditioned data-misfit Hessian has rank at most the number of '
                'observations; its randomized low-rank form, with a computable error certificate, gives the '
                'linear-Gaussian posterior at the cost of $k+p$ model solves.',
         dispersion='The same for the Hessian of the chloride facts.',
         bcs='The Hessian with respect to the boundary and recharge parameters shows which directions rain alone '
             'leaves unidentified.',
         step='The floor needs the exact posterior: one factorisation per case in our test bed, out of reach in a 2-D '
              'variable-density model. Their certified low-rank posterior makes the floor computable there, with the '
              'certificate entering as a known error, so that the ratio of a band to the floor is reported with a '
              'computable error and not an unknown one.',
         steps=['emulate', 'design'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='C5', inst='Caltech', year=2022, short='What subsampled averages can recover',
         title='Multiscale elliptic PDE upscaling and function approximation via subsampled data',
         authors='Yifan Chen, Thomas Y. Hou',
         venue='Multiscale Modeling & Simulation 20(1), 188–219 (2022)',
         links=[('doi:10.1137/20M1372214', 'https://doi.org/10.1137/20M1372214'),
                ('CaltechAUTHORS', 'https://authors.library.caltech.edu/records/yf0pe-cc844'),
                ('arXiv:2010.04199', 'https://arxiv.org/abs/2010.04199')],
         evidence='Caltech (CaltechAUTHORS record; T. Y. Hou is a Caltech professor; Y. Chen\'s Caltech thesis).',
         does='**Result.** Numerical upscaling of rough-coefficient elliptic equations and scattered-data approximation '
              'are treated as one recovery problem, the coarse variables corresponding to the sampled data. Shrinking '
              'the subsampled lengthscale of local-average data can make the error blow up when the target lacks '
              'regularity, and a singular weight function repairs this; a companion paper proves a subsampled Poincaré '
              'inequality optimal in the lengthscale (rates not seen).',
         sota='A rigorous link between upscaling and recovery from sparse local averages.',
         gap='Steady elliptic; no transport, noise or time dependence.',
         inputs='What a few loggers buy in heterogeneous transmissivity: near-point heads recover little unless '
                'weighted; the screen length and the spacing control the attainable error.',
         dispersion='None directly.',
         bcs='None.',
         step='The averaging scale of an observation matters as much as its position. In the floor of Proposition F1 a '
              'logger is a point head; replacing it by an average over a screen length changes the data operator, and '
              'the floor of each screen length can be computed before drilling — their question for elliptic recovery, '
              'asked for guaranteed bands.',
         steps=['design'], informs=dict(inputs=2, dispersion=0, bcs=0)),
]

BERKELEY = [
    dict(id='B1', inst='Berkeley', year=2026, short='Conformal optimality via Neyman–Pearson',
         title='Conformal prediction through the lens of hypothesis testing: universality, impossibility, and optimality',
         authors='Ryan J. Tibshirani, Rina Foygel Barber, Aaditya Ramdas',
         venue='arXiv:2608.27310 (preprint, 2026)',
         links=[('arXiv:2608.27310', 'https://arxiv.org/abs/2608.27310'),
                ('Berkeley copy', 'https://www.stat.berkeley.edu/~ryantibs/papers/cptesting.pdf')],
         evidence='Hosted on R. J. Tibshirani\'s UC Berkeley Statistics pages; the paper\'s affiliation line and the '
                  'posting date were not seen. Preprint.',
         does='**Theorem (as quoted).** "The optimal method for prediction sets, delivering the most efficient set among '
              'all methods with valid coverage for exchangeable distributions, is a conformal predictor whose score is '
              'the inverse conditional density of Y|X", for any joint law and any sample size, proved by Neyman–Pearson '
              'theory after recasting conformal prediction as the inversion of a permutation test of exchangeability. '
              'The universality and impossibility results (no distribution-free conditional coverage) are re-derived '
              'from classical testing theory; there are no experiments.',
         sota='A finite-sample, any-distribution optimality theorem for the efficiency of conformal prediction.',
         gap='The optimal score needs the true conditional density; no estimation theory, rates or experiments; '
             'preprint.',
         inputs='The optimal conformal score for $T$, $S$, $\\kappa$ and $\\tau$ is the inverse exact posterior '
                'density: the conformalised highest-density set.',
         dispersion='The same for the dispersivity and the transition-zone width.',
         bcs='With rain alone the optimal score is the inverse of $p$(boundary | rain): a flat posterior means no valid '
             'band can be narrow.',
         step='Their theorem and Proposition F1 are the same Neyman–Pearson argument seen from two sides: over all '
              'methods valid for every exchangeable law, and over all methods valid on average under one law. Together '
              'they say that conformalising the exact posterior reaches the floor as the calibration grows; T18 measures '
              'how close it is with 20 anchors: 1.07–1.20 times the floor, against 1.33–1.54 for the ensemble of '
              'reviews I–V.',
         steps=['guarantee'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='B2', inst='Berkeley', year=2024, short='Sharp minimax rates, random operators',
         title='Noisy recovery from random linear observations: sharp minimax rates under elliptical constraints',
         authors='Reese Pathak, Martin J. Wainwright, Lin Xiao',
         venue='The Annals of Statistics 52(6), 2816–2850 (2024); arXiv:2303.12613',
         links=[('doi:10.1214/24-AOS2446', 'https://doi.org/10.1214/24-AOS2446'),
                ('arXiv:2303.12613', 'https://arxiv.org/abs/2303.12613')],
         evidence='R. Pathak: UC Berkeley EECS (search summaries; the Annals version is hosted on his Berkeley page); '
                  'M. J. Wainwright: MIT from July 2022; L. Xiao: Meta. The journal affiliation block was not seen.',
         does='**Theorem (as summarised).** For observations from a random linear operator plus noise, with the '
              'parameter in an arbitrary compact elliptical set and the error in an elliptical norm, a functional of the '
              'noise level, the law of the operator and the two ellipses gives the minimax risk; the result is '
              'non-asymptotic, sharp up to an explicit universal constant and asymptotically exact as the radius of the '
              'set grows. Applications include parametric and non-parametric regression with covariate shift.',
         sota='The first constant-sharp, non-asymptotic minimax characterisation of linear inverse problems with random '
              'forward operators over arbitrary ellipses.',
         gap='Linear and elliptical; it bounds the risk of an estimator, not the length of a band with coverage.',
         inputs='Linearised heads are a random linear operator driven by the rain, applied to ($T$, $S$, $\\kappa$); '
                'the functional is the error floor no estimate of them can beat.',
         dispersion='Indirect: chloride linearised in the dispersivities, a strongly nonlinear problem.',
         bcs='Recharge in time under a smoothness ellipse is the non-parametric case; the covariate-shift case covers a '
             'rain law that differs between calibration and target years.',
         step='Their floor is for the error of a point estimate, Proposition F1 for a band with a risk guarantee, '
              'computed exactly instead of up to a constant. In the linear-Gaussian case the two meet: the band floor is '
              'the posterior spread times a quantile, and the ratio of a guaranteed band to the floor (1.33–1.54 for the '
              '20-anchor ensemble band, T18) plays the role of their constant.',
         steps=['invert', 'guarantee'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='B3', inst='Berkeley', year=2025, short='Conditional risk control, learned tilts',
         title='Automatically adaptive conformal risk control',
         authors='Vincent Blot, Anastasios N. Angelopoulos, Michael I. Jordan, Nicolas J-B. Brunel',
         venue='Proceedings of the 28th International Conference on Artificial Intelligence and Statistics (AISTATS '
               '2025), PMLR 258, 19–27; arXiv:2406.17819',
         links=[('PMLR 258', 'https://proceedings.mlr.press/v258/blot25a.html'),
                ('arXiv:2406.17819', 'https://arxiv.org/abs/2406.17819')],
         evidence='Title page of the proceedings PDF: A. N. Angelopoulos, University of California, Berkeley; M. I. '
                  'Jordan, University of California, Berkeley and INRIA Paris.',
         status='verified (the proceedings PDF was opened and read).',
         does='**Theorem 1 (as read).** For exchangeable data and a loss in [0, 1] that is left-continuous and '
              'non-increasing over nested sets, the set built from the minimiser of an augmented objective with a '
              'regulariser $R$ over a vector space Λ of functions $\\lambda(x,y)$ has, for every non-negative λ in Λ with '
              'positive mean, a λ-tilted risk at most α minus a term in the directional derivative of $R$. Λ = {1} gives '
              'marginal risk control, group indicators give group-conditional control with overlapping groups, and a '
              'learned embedding gives control over all covariate shifts linear in it. In a polyp-segmentation example '
              'the recall-controlled thresholds are 0.304 and 0.330, against 0.276 with plain conformal risk control.',
         sota='Conditional risk control over a learned class of tilts.',
         gap='The guarantee is loosened by the regulariser; class-conditional only; no efficiency theorem; '
             'exchangeability assumed.',
         inputs='Bands for the inputs that widen where rain-only inversion is weak and narrow elsewhere.',
         dispersion='Chloride losses controlled under every tilt of a learned embedding.',
         bcs='Tilts in a rain-feature embedding cover drought and wet regimes for boundary bands.',
         step='A conditional guarantee moves a band toward a conditional floor, which is higher than the marginal floor '
              'of Proposition F1. Both floors can be computed in our test bed (the conditional one replaces the single '
              'threshold of [[np]] by one per group of weeks), which prices conditional validity in width before their '
              'method is run.',
         steps=['guarantee'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='B4', inst='Berkeley', year=2024, short='Locally simultaneous inference',
         title='Locally simultaneous inference',
         authors='Tijana Zrnic, William Fithian',
         venue='The Annals of Statistics 52, 1227–1253 (2024); arXiv:2212.09009',
         links=[('doi:10.1214/24-AOS2391', 'https://doi.org/10.1214/24-AOS2391'),
                ('arXiv:2212.09009', 'https://arxiv.org/abs/2212.09009')],
         evidence='Both authors: University of California, Berkeley (search summary of the arXiv listing). The volume '
                  'was read from the DOI and year; the issue was not confirmed.',
         does='**Theorem (as quoted).** Any simultaneous inference method can be refined to be simultaneous only over '
              'the selections plausible given the data; the refinement stays valid for any selection rule and, "under '
              'mild conditions satisfied by common confidence intervals", strictly dominates the underlying simultaneous '
              'method: it can never give less power. The motivating case is an interval for the winning treatment of a '
              'trial when, in hindsight, only one could have won.',
         sota='Post-selection inference that dominates the simultaneous method it refines.',
         gap='Needs an underlying simultaneous method and a finite candidate set; no distribution-free version with few '
             'anchors.',
         inputs='After selecting the best-supported scenario of $T$, $S$ and $\\kappa$, report bands nearly as narrow as '
                'unadjusted ones when the choice is clear.',
         dispersion='The same when choosing among dispersivity models ranked by chloride fit.',
         bcs='Choosing the boundary scenario (sea-level trend, inflow) supported by rain and heads.',
         step='The enlarged law of T19 effectively selects a delay from the data, so reporting the band for the selected '
              'delay is a selection problem. Their refinement says the price is small when the choice is clear; in T19 '
              'the enlarged law reached 1.18–1.34 times the floor of the true 35-day delay, a sign that the data pick '
              'the delay well, and the floor under the selected delay is the target such a band should approach.',
         steps=['guarantee', 'check'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='B5', inst='Berkeley', year=2024, short='Self-calibrating conformal prediction',
         title='Self-calibrating conformal prediction',
         authors='Lars van der Laan, Ahmed M. Alaa',
         venue='Advances in Neural Information Processing Systems 37 (NeurIPS 2024); arXiv:2402.07307',
         links=[('NeurIPS 2024', 'https://proceedings.neurips.cc/paper_files/paper/2024/hash/'
                                 'c1c49aba08e6c90f2b1f85751f497a2f-Abstract.html'),
                ('arXiv:2402.07307', 'https://arxiv.org/abs/2402.07307')],
         evidence='A. M. Alaa: UC Berkeley and UCSF (search summary of the arXiv version); L. van der Laan: University '
                  'of Washington.',
         does='**Result (as summarised).** Venn–Abers calibration is extended from binary classification to regression '
              'by isotonic regression and combined with conformal prediction, giving calibrated point predictions and '
              'intervals with valid coverage conditional on the calibrated predictions in finite samples; the exact '
              'theorem text was not seen. The calibrator must be refitted for every candidate outcome.',
         sota='Finite-sample coverage conditional on the prediction, together with calibrated point predictions.',
         gap='Costly; conditions on the predicted value only; no efficiency result.',
         inputs='Bands on $T$ and $S$ that hold separately in zones of high and low prediction.',
         dispersion='Chloride and transition-zone bands valid conditionally on the predicted salinity level, which matters '
                    'near the 250 mg/L limit.',
         bcs='None.',
         step='Calibrating the centre as well as the band attacks the reconstructor factor of Proposition F2: in T18 the '
              'ensemble centre and spread cost 1.13–1.39 times against the exact posterior. A self-calibrated centre '
              'should recover part of that, and the floor says how much is left to recover.',
         steps=['guarantee', 'emulate'], informs=dict(inputs=2, dispersion=1, bcs=0)),
]

MIT = [
    dict(id='M1', inst='MIT', year=2025, short='Bernstein–von Mises with n ≫ d²',
         title='Improved dimension dependence in the Bernstein–von Mises theorem via a new Laplace approximation bound',
         authors='Anya Katsevich',
         venue='Information and Inference: A Journal of the IMA 14, iaaf020 (2025); arXiv:2308.06899',
         links=[('arXiv:2308.06899', 'https://arxiv.org/abs/2308.06899'),
                ('Duke Scholars record', 'https://scholars.duke.edu/publication/1690258')],
         evidence='MIT Mathematics postdoctoral fellow at the time (MIT e-mail on the arXiv version, as quoted; CV on '
                  'klein.mit.edu); now at Duke. The DOI 10.1093/imaiai/iaaf020 was built from the article number and '
                  'not seen.',
         does='**Theorem.** If $f$ is convex with a unique global minimiser, the total-variation distance between '
              '$e^{-nf}$ and its Laplace approximation is of order $d/\\sqrt{n}$, the tight dimension dependence; '
              'consequently, up to a model-dependent coefficient, $n\\gg d^2$ suffices for the Bernstein–von Mises '
              'theorem in generalized linear and multinomial models, improving the universal factor from '
              '$\\sqrt{d^3/n}$ to $\\sqrt{d^2/n}$.',
         sota='The tightest known dimension dependence of the Bernstein–von Mises theorem in generalized linear models.',
         gap='Convex, well-specified, GLM-type likelihoods; no PDE forward model and no misspecification.',
         inputs='A total-variation error ε moves the coverage of any set by at most ε, so Gaussian bands are near-valid '
                'only when $n\\gg d^2$: with 8–10 unknowns that is about a hundred informative observations, beyond a few '
                'heads, and the floor must come from the exact posterior.',
         dispersion='Dispersivities informed by a few chloride facts are outside the Gaussian regime.',
         bcs='A long rain series gives large $n$ only for the directions it informs.',
         step='A total-variation error becomes a risk error one for one, so their bound limits how far a Laplace floor '
              'can be from the exact floor of Proposition F1. In our test bed the exact posterior was nearly Gaussian: '
              'the central interval and the exact mean ± λσ were within 0–5% of the floor (T18), a measured instance of '
              'their regime that the ensemble bands of reviews I–V, 1.33–1.54 times the floor, do not exploit.',
         steps=['invert'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='M2', inst='MIT', year=2024, short='Accuracy of Gaussian variational inference',
         title='On the approximation accuracy of Gaussian variational inference',
         authors='Anya Katsevich, Philippe Rigollet',
         venue='The Annals of Statistics 52, 1384–1409 (2024); arXiv:2301.02168',
         links=[('arXiv:2301.02168', 'https://arxiv.org/abs/2301.02168'),
                ('Duke Scholars record', 'https://scholars.duke.edu/publication/1690262')],
         evidence='P. Rigollet: MIT Mathematics; A. Katsevich: MIT postdoctoral fellow (CV). The DOI 10.1214/24-AOS2393 '
                  'comes from one record and was not confirmed; the issue was not seen.',
         does='**Theorem (as summarised).** For posteriors proportional to $e^{-nv}$ on $\\mathbb{R}^d$, Gaussian '
              'variational inference approximates the mean with error of order $(d/\\sqrt{n})^3$, the covariance with '
              '$(d/\\sqrt{n})^2$ and the distribution in total variation with $d/\\sqrt{n}$, against $d/\\sqrt{n}$ for the '
              'mean of the Laplace method; the proof uses a Hermite-series expansion of the log-posterior.',
         sota='Sharp, dimension-explicit accuracy of Gaussian variational inference against the Laplace method.',
         gap='Log-concave-type, well-specified, large $n$; no PDE model.',
         inputs='When a Gaussian variational posterior can stand in for the exact one in computing the floor; with a few '
                'heads $n$ is small and the exact posterior is needed.',
         dispersion='None directly.',
         bcs='Rain-only posteriors are near-Gaussian only where the rain is informative.',
         step='A variational reconstructor is a cheap substitute for the exact posterior where the latter is out of '
              'reach, and Proposition F2 measures what it costs: replace the ensemble (1.13–1.39 times the '
              'exact-posterior band, T18) by a Gaussian variational posterior and read its reconstructor factor, which '
              'their rates predict falls as the informative observations grow.',
         steps=['invert', 'emulate'], informs=dict(inputs=2, dispersion=0, bcs=1)),
    dict(id='M3', inst='MIT', year=2025, short='Two-sided certified dimension reduction',
         title='Sharp detection of low-dimensional structure in probability measures via dimensional logarithmic Sobolev '
               'inequalities',
         authors='Matthew T. C. Li, Tiangang Cui, Fengyi Li, Youssef Marzouk, Olivier Zahm',
         venue='Information and Inference: A Journal of the IMA (2025), iaaf021; arXiv:2406.13036',
         links=[('doi:10.1093/imaiai/iaaf021', 'https://doi.org/10.1093/imaiai/iaaf021'),
                ('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/167023'),
                ('arXiv:2406.13036', 'https://arxiv.org/abs/2406.13036')],
         evidence='Deposited in DSpace@MIT; Marzouk, M. T. C. Li and F. Li at MIT. Volume and issue not confirmed.',
         does='**Theorem (as summarised).** The target is approximated as a perturbation of a reference measure along $r$ '
              'directions chosen to minimise an upper bound on the Kullback–Leibler divergence derived from the '
              'dimensional logarithmic Sobolev inequality. For Gaussian target and reference, minimising the bound is '
              'equivalent to minimising the divergence itself (the bound is sharp); for non-Gaussian targets the new '
              'majorants uniformly improve on earlier ones, the divergence is bracketed between a computable minorant '
              'and majorant, and the dimensional Poincaré inequality gives improved Hellinger bounds.',
         sota='The first sharp, two-sided certified detection of low-dimensional posterior structure.',
         gap='Needs gradients of the log-density; the certificate is not turned into band length or coverage.',
         inputs='Certifies how many directions of the parameters rain and heads inform, and the minorant how much '
                'structure is unavoidably lost.',
         dispersion='Tests whether $\\alpha_L$ and $\\alpha_T$ lie in the informed subspace; with rain and heads they '
                    'likely do not.',
         bcs='The same for directions of recharge in time and of the initial interface.',
         step='Pinsker\'s inequality turns their divergence majorant into a total-variation bound, hence a bound on the '
              'risk error of a reduced posterior, while their minorant says how much no reduction of dimension $r$ can '
              'avoid. That gives a principled choice of $r$: the smallest dimension whose certified loss keeps the '
              'reconstructor factor of Proposition F2 below a target such as 1.1.',
         steps=['invert', 'emulate'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='M4', inst='MIT', year=2024, short='Design by certified information bounds',
         title='Nonlinear Bayesian optimal experimental design using logarithmic Sobolev inequalities',
         authors='Fengyi Li, Ayoub Belhadji, Youssef Marzouk',
         venue='arXiv:2402.15053 (preprint, 2024)',
         links=[('arXiv:2402.15053', 'https://arxiv.org/abs/2402.15053')],
         evidence='Massachusetts Institute of Technology (affiliation on the ar5iv rendering of the preprint). Preprint; '
                  'no journal version found.',
         does='**Result.** To choose $k$ of $n$ candidate observations that maximise the mutual information with the '
              'parameters, logarithmic Sobolev inequalities give cheap lower bounds on the mutual information; the '
              'greedy algorithm on this bound needs two matrices and then only row and column selection and Schur '
              'complements, avoiding mutual-information estimates in non-Gaussian settings. It is reported to beat random '
              'selection, Gaussian approximations and nested Monte Carlo estimators (numbers not seen; no approximation '
              'ratio confirmed).',
         sota='Greedy nonlinear Bayesian design driven by a certified lower bound on mutual information, without nested '
              'Monte Carlo.',
         gap='Preprint; the guarantee is for the bound, not for the optimality of the design.',
         inputs='Ranks candidate logger sites by a guaranteed lower bound on the information about $T$, $S$, $\\kappa$ '
                'and $\\tau$.',
         dispersion='Ranks candidate chloride sampling points for the dispersivities.',
         bcs='The gain of each added logger over rain alone.',
         step='Information and the floor answer the same design question in different currencies. Use their bound to '
              'propose designs and the floor to price them: in T20 four loggers remove <<eta4>> of the rain-only '
              'sea-level floor and a tide gauge <<etag>>, a guaranteed-band currency that their ranking should '
              'reproduce.',
         steps=['design'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='M5', inst='MIT', year=2022, short='Sparse triangular transports converge fast',
         title='Sparse approximation of triangular transports, part I: the finite-dimensional case',
         authors='Jakob Zech, Youssef Marzouk',
         venue='Constructive Approximation (2022); arXiv:2006.06994',
         links=[('doi:10.1007/s00365-022-09569-2', 'https://doi.org/10.1007/s00365-022-09569-2'),
                ('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/141313'),
                ('arXiv:2006.06994', 'https://arxiv.org/abs/2006.06994')],
         evidence='Deposited in DSpace@MIT (Y. Marzouk, MIT). The journal was inferred from the DOI prefix; volume and '
                  'pages were not confirmed.',
         does='**Theorem (as summarised).** For analytic densities on $[-1,1]^d$, the error of approximating the '
              'Knothe–Rosenblatt transport decays exponentially in the size of the ansatz space, in the Hellinger, '
              'total-variation, Wasserstein and Kullback–Leibler distances; part II extends the result to posteriors on '
              'infinite-dimensional Banach spaces.',
         sota='Exponential convergence of sparse triangular transports for analytic densities.',
         gap='Analytic densities on bounded domains; approximation, not estimation from samples.',
         inputs='A transport-map reconstructor can approximate the exact posterior of $T$, $S$, $\\kappa$ and $\\tau$ '
                'with an error falling exponentially in its size: a route to the exact posterior where no closed form '
                'exists.',
         dispersion='The same for posteriors of the dispersivities, whose densities are smooth.',
         bcs='The same for low-dimensional parametrisations of boundary functions.',
         step='The reconstructor factor of Proposition F2 is the cost of not having the exact posterior. Their '
              'total-variation bound limits the risk error of a transport reconstructor, so a map of a given size has a '
              'certified distance to the floor; in a 2-D model, where the exact posterior is out of reach, the floor '
              'can be bracketed by maps of increasing size.',
         steps=['emulate', 'invert'], informs=dict(inputs=2, dispersion=1, bcs=1)),
]

INST_ORDER = ('Oxford', 'Caltech', 'Berkeley', 'MIT')


def all_cards():
    return OXFORD + CALTECH + BERKELEY + MIT


CARDS = all_cards()


def SOTA_ROWS(AJ):
    R = AJ['laws']
    N = R['none']
    G4 = ('r', 'qL', 'eta', 'kappa')

    def rr(law, key):
        return [R[law][g][key]['halfwidth'] / R[law][g]['floor']['halfwidth'] for g in G4]
    m20, exP = rr('none', 'm20'), rr('none', 'exactP_m20')
    dT, dE = rr('delay', 'exactT_m20'), rr('delay', 'm20')
    rec = [N[g]['ens_star']['halfwidth'] / N[g]['exact_z']['halfwidth'] for g in G4]
    f = lambda xs: f'{min(xs):.2f}–{max(xs):.2f}'  # noqa: E731
    return [
        ['Optimality of prediction sets',
         'Neyman–Pearson optimality of conformal sets with the inverse-density score (B1); expected size of conformal '
         'sets (O1); conformal sets as scenario programs (O5)',
         'Optimal score unknown in practice; no number for a given aquifer and design',
         'A computable floor for guaranteed bands of boundary functions (Proposition F1)',
         f'T18: 20-anchor ensemble band {f(m20)} times the floor'],
        ['Lower bounds for inverse problems',
         'Sharp minimax rates for random linear operators (B2); constrained frequentist intervals and the Burrus '
         'conjecture (C1); simultaneous regions (C2)',
         'Bounds for point estimates or worst cases, not for bands with a risk guarantee',
         'The floor of the band itself, exact under the working law',
         'Propositions F1, F3'],
        ['Accuracy of posterior approximations',
         'Bernstein–von Mises with n ≫ d² (M1); Gaussian variational inference (M2); two-sided certified dimension '
         'reduction (M3); sparse triangular transports (M5); posterior perturbation (C3)',
         'Distances between distributions, not widths of guaranteed bands',
         'The reconstructor factor of the decomposition [[dec]]',
         f'T18: ensemble {f(rec)} times the exact posterior; exact posterior with 20 anchors {f(exP)} times the floor'],
        ['Conditional and selective guarantees',
         'Conditional risk control over learned tilts (B3); locally simultaneous inference (B4); self-calibrating '
         'conformal prediction (B5)',
         'More validity at a price in width that is not measured',
         'Floors for marginal and conditional validity, priced before the method is run',
         'Proposition F2'],
        ['Identifiability and design',
         'Identifiability of diffusion impedance (O3); data-free bounds on target averages (O2); certified information '
         'bounds for design (M4); stable CUR selection (O4); randomized low-rank certificates (C4); subsampled averages '
         '(C5)',
         'Information or worst-case currencies; no guaranteed-band value of a design',
         'The floor of each candidate design, computable before field data (Proposition F3)',
         'T20'],
        ['Structural error',
         'Posterior stability under perturbed laws (C3)',
         'No account of how a wrong model structure widens a guaranteed band',
         'Enlarged law with the vadose delay unknown, calibrated on anchors',
         f'T19: with a 35-day delay {f(dE)} times the floor for the ensemble, {f(dT)} for the enlarged law'],
        ['Dispersion and mixing',
         'No 2020–2026 theorem-level paper on field dispersion at the four institutions beyond those already used',
         'Floors for dispersivity bands need a transport model',
         'Left for the next step, with the transport model of review I',
         '–'],
    ]
