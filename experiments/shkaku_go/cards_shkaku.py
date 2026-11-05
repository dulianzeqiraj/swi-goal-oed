"""The twenty paper cards of the seventh state-of-the-art review (five per institution, all 2022-2026), from the
verification notes of four literature searches (November 2026), and the rows of its state-of-the-art table. Landing
pages were reached through search results only (doi.org, arxiv.org, jmlr.org, proceedings.mlr.press,
proceedings.neurips.cc and most publisher hosts did not resolve), so every card is partly verified. None of the twenty
was a card of reviews I-VI or appears in the earlier reviews of the series (checked with the repository-wide search).

Fields as in ../dyshemeja_go/cards_dyshemeja.py. Text conventions: $math$, **bold**, *italic*; <<key>> is a number
filled in from res/shkaku.json by text_shkaku.py."""

OXFORD = [
    dict(id='O1', inst='Oxford', year=2024, short='Counterfactual storm in an operational forecast',
         title='Event attribution of a midlatitude windstorm using ensemble weather forecasts',
         authors='Shirin Ermis, Nicholas J Leach, Fraser C Lott, Sarah N Sparrow, Antje Weisheimer',
         venue='Environmental Research: Climate 3(3), 035001 (2024)',
         links=[('doi:10.1088/2752-5295/ad4200', 'https://doi.org/10.1088/2752-5295/ad4200'),
                ('Oxford ORA', 'https://ora.ox.ac.uk/objects/uuid:05b2f140-9547-435d-8f5a-6151b3ca27ca')],
         evidence='Oxford ORA journal-article record; listed on the Oxford Physics pages of Ermis, Weisheimer and Leach '
                  '(search summaries); the printed byline was not seen.',
         does='**Result (abstract wording).** Using modified greenhouse-gas concentrations and changed initial conditions '
              'for ocean temperatures, the authors create two counterfactual scenarios of storm Eunice (February 2022) '
              'with the ECMWF operational ensemble, besides the forecast for the current climate. The results robustly '
              'indicate that Eunice became more intense with climate change and that similar storms will intensify with '
              'further forcing, consistently across lead times; the mechanism is more vorticity production through '
              'higher humidity in the warm conveyor belt. Methods to adjust the atmospheric initial conditions are named '
              'as an open problem. A storyline result, not a theorem; no wind or pressure numbers were seen.',
         sota='Counterfactual attribution of one observed event inside an operational forecast system, conditioned on '
              'the event\'s own synoptic state, with lead-time consistency as the robustness check.',
         gap='No guarantee on the counterfactual; no principled rule for which parts of the initial state to keep.',
         inputs='None.',
         dispersion='None.',
         bcs='A template for "the same years, a different forcing": keep the abducted state, change the boundary forcing '
             '(the rain; by analogy the sea level) and keep only the parts of the initial state that are consistent '
             'with the counterfactual forcing — the initial-head question of the aquifer.',
         step='SHKAKU-GO answers their open problem for the aquifer: the initial head splits into a part in '
              'equilibrium with the forcing, recomputed in the twin, and a shared perturbation, and Proposition K1 shows '
              'that the perturbation, the sea level and the inflow all cancel in the effect. The counterfactual then '
              'carries a guarantee: 20 anchors bracket the drought effect on the head at the well with risk '
              '<<dh_none_anc>> (T21).',
         steps=['prior', 'emulate'], informs=dict(inputs=0, dispersion=0, bcs=2)),
    dict(id='O2', inst='Oxford', year=2023, short='Collider independence as a provable gain',
         title='Returning The Favour: When Regression Benefits From Probabilistic Causal Knowledge',
         authors='Shahine Bouabid, Jake Fawkes, Dino Sejdinovic',
         venue='Proceedings of the 40th International Conference on Machine Learning (ICML 2023, oral), PMLR 202, '
               '2885–2913',
         links=[('arXiv:2301.11214', 'https://arxiv.org/abs/2301.11214'),
                ('ICML 2023 poster', 'https://icml.cc/virtual/2023/poster/24885')],
         evidence='Bouabid and Fawkes at the Department of Statistics, University of Oxford; Sejdinovic at the '
                  'University of Adelaide (search summary of the arXiv author block).',
         does='**Result (closely paraphrased).** When the causal graph contains a collider, the independences it '
              'implies are an inductive bias for regression ("collider regression"). For RKHS hypothesis classes the '
              'authors prove a strictly positive generalisation benefit under mild assumptions and give closed-form '
              'estimators of the empirical risk minimiser, obtained by projecting the regressor onto the subspace that '
              'respects the independence; gains are shown on synthetic and climate-model data. The exact collider '
              'configuration and assumptions were not seen verbatim.',
         sota='The first generalisation guarantee for using collider independence in supervised learning.',
         gap='Independent samples and a known graph; no time series and no counterfactuals.',
         inputs='None directly.',
         dispersion='None.',
         bcs='Rain and sea level (or inland inflow) are independent causes and the head is their collider: a '
             'regression of a latent boundary signal on rain and head must have a constant mean given the rain, which '
             'gives a provable variance gain.',
         step='The same independence is the hypothesis of Proposition K2: because the rain is independent of the latent '
              'histories, the rain alone gives only the interventional answer, and every gain of rung 3 over rung 2 '
              'comes from the heads, the colliders. Measured as the value of abduction, four loggers narrow the floor of '
              'the counterfactual head <<va_hc4>>-fold and that of the head effect <<va_dh4>>-fold (T22).',
         steps=['invert'], informs=dict(inputs=0, dispersion=0, bcs=2)),
    dict(id='O3', inst='Oxford', year=2026, short='Identifiable parameters of dynamical systems',
         title='Disentangling Dynamical Systems: Causal Representation Learning Meets Local Sparse Attention',
         authors='Markus W. Baumgartner, Anson Lei, Joe Watson, Ingmar Posner',
         venue='Proceedings of the Fifth Conference on Causal Learning and Reasoning (CLeaR 2026), PMLR 323, 119–165',
         links=[('PMLR 323', 'https://proceedings.mlr.press/v323/baumgartner26a.html'),
                ('arXiv:2603.14483', 'https://arxiv.org/abs/2603.14483')],
         evidence='Posner at the Applied AI Lab, Oxford Robotics Institute; author e-mails at robots.ox.ac.uk (search '
                  'summary); the other affiliations were not confirmed one by one.',
         does='**Result.** A theorem establishes the identifiability of system parameters for local causal predictors, '
              'culminating in a graphical criterion: enforcing sparse causal relations between parameters and system '
              'components in a one-step-prediction decoder provably disentangles the representation of the system '
              'parameters, and the global causal structure gives only a lower bound on what local, state-dependent '
              'structure can guarantee. The assumptions build on mechanism-sparsity results; experiments on four '
              'synthetic domains (Dual Particle, Local Particle, Springs, Bounce) find local causal structure often '
              'necessary for full identifiability.',
         sota='The first identifiability theorem for system parameters under local, state-dependent causal structure in '
              'dynamical systems.',
         gap='Synthetic benchmarks; deterministic decoders; no uncertainty guarantee.',
         inputs='A graphical criterion for when $T$, $S$, $\\kappa$ and $\\tau$ are identifiable from few trajectories: '
                'each must act on a local, state-dependent part of the state.',
         dispersion='It suggests that the dispersivity is identifiable only where it drives the state locally, in the '
                    'transition zone while the interface moves (our inference).',
         bcs='None directly.',
         step='Proposition K1 is a sharp instance for counterfactuals: the effect of a rain intervention depends on '
              '$\\kappa$ and $\\tau$ only, so only those two must be identifiable and the latent histories may stay '
              'unidentified without harm. When $\\tau$ is wrong, anchors do not repair the effect band (risk '
              '<<dh_delay_anc>> under a 35-day delay, T21); making $\\tau$ part of the law is the identifiability fix '
              '(risk <<dh_delay_T>>).',
         steps=['invert', 'emulate'], informs=dict(inputs=2, dispersion=1, bcs=0)),
    dict(id='O4', inst='Oxford', year=2024, short='Duality of causal robust optimization',
         title='Duality of Causal Distributionally Robust Optimization',
         authors='Yifan Jiang',
         venue='SIAM Journal on Control and Optimization, doi:10.1137/25M1803954 (volume, pages and year of the journal '
               'version not seen); first version arXiv:2401.16556 (2024)',
         links=[('doi:10.1137/25M1803954', 'https://doi.org/10.1137/25M1803954'),
                ('arXiv:2401.16556', 'https://arxiv.org/abs/2401.16556'),
                ('Oxford ORA thesis', 'https://ora.ox.ac.uk/objects/uuid:b895f22a-b223-479d-8a93-ac7172776662')],
         evidence='Oxford Mathematical Institute CV of the author and his Oxford DPhil thesis (2025) on adapted '
                  'Wasserstein distances; the journal author block was not seen.',
         does='**Result (paraphrased).** For distributionally robust optimization in a dynamic setting, where each '
              'candidate model is penalised by its adapted ("causal", non-anticipative) Wasserstein distance from a '
              'reference model, a dynamic duality formula reduces the discrete-time problem to a sequence of '
              'single-step problems; the paper is described as giving the first duality result for causal DRO in '
              'continuous time, with extensions to expected shortfall and optimal stopping. The exact assumptions were '
              'not seen.',
         sota='Duality for causal (adapted-Wasserstein) distributionally robust optimization in discrete and continuous '
              'time.',
         gap='Decision-theoretic rather than counterfactual; the radius of the ball is not calibrated from data.',
         inputs='None.',
         dispersion='None.',
         bcs='A computable worst case of a recharge or head functional over all rain-process laws near the observed one '
             'that respect the flow of information (future rain cannot act on the past): a drought stress test that '
             'knows the filtration.',
         step='Their ball of rain laws is a natural set of interventions $P\'$ for SHKAKU-GO, and in the linear test '
              'bed each counterfactual costs one matrix product (the map $g=K_g f$, Section 4.1), so the adapted worst '
              'case can carry a guaranteed band. Proposition K3 adds what no ball of rain laws contains: the band must '
              'also be robust to the coupling of the noise across worlds.',
         steps=['design'], informs=dict(inputs=0, dispersion=0, bcs=1)),
    dict(id='O5', inst='Oxford', year=2023, short='Neural SDEs with proper path scores',
         title='Non-adversarial training of Neural SDEs with signature kernel scores',
         authors='Zacharia Issa, Blanka Horvath, Maud Lemercier, Cristopher Salvi',
         venue='Advances in Neural Information Processing Systems 36 (NeurIPS 2023)',
         links=[('NeurIPS 2023', 'https://proceedings.neurips.cc/paper_files/paper/2023/hash/'
                                 '2460396f2d0d421885997dd1612ac56b-Abstract.html'),
                ('arXiv:2305.16274', 'https://arxiv.org/abs/2305.16274')],
         evidence='Horvath and Lemercier at the Mathematical Institute, University of Oxford (search summary of the '
                  'arXiv author block); Issa at King\'s College London; Salvi\'s affiliation not confirmed.',
         does='**Result (abstract wording).** Neural SDEs are trained as continuous-time generative models with '
              'signature-kernel scoring rules instead of adversarial objectives; by showing strict properness of the '
              'kernel scores and consistency of the estimators, the authors give existence and uniqueness guarantees '
              'for the minimiser. Evaluation reduces to linear path-dependent PDEs with adjoint backpropagation, and the '
              'scores are defined for paths valued in infinite-dimensional spaces, so spatio-temporal data are covered. '
              'Experiments: rough volatility, conditional forecasts given an observed past (exchange rates), limit-order '
              'books (no numbers seen).',
         sota='The first strictly proper, non-adversarial training objective for neural SDEs, with existence and '
              'uniqueness of the minimiser.',
         gap='No causal or interventional semantics; no coverage guarantee.',
         inputs='A consistent way to fit the drift and diffusion of a stochastic head or recharge model from few paths.',
         dispersion='None directly.',
         bcs='A structural stochastic generator of rain and inflow paths conditioned on the observed past; keeping the '
             'abducted noise path and changing the forcing gives a rung-3 generator (our construction, not theirs).',
         step='That construction is the twin of SHKAKU-GO with a learned generator, and Proposition K3 names what such '
              'a generator must also learn but cannot from data: the coupling of the noise across worlds. With the '
              'recharge error shared ($\\rho$ = 1) the floor of the counterfactual recharge is <<rc_floor1>> mm/d; with '
              'an independent twin noise ($\\rho$ = 0) it is <<rc_rho0>> times wider (T23), whatever the generator.',
         steps=['emulate', 'prior'], informs=dict(inputs=1, dispersion=0, bcs=1)),
]

CALTECH = [
    dict(id='C1', inst='Caltech', year=2022, short='Adjoint causal attribution of coastal sea level',
         title='Local and Remote Forcing of Interannual Sea-Level Variability at Nantucket Island',
         authors='Ou Wang, Tong Lee, Christopher G. Piecuch, Ichiro Fukumori, Ian Fenty, Thomas Frederikse, Dimitris '
                 'Menemenlis, Rui M. Ponte, Hong Zhang',
         venue='Journal of Geophysical Research: Oceans 127(6), e2021JC018275 (2022)',
         links=[('doi:10.1029/2021JC018275', 'https://doi.org/10.1029/2021JC018275'),
                ('PMC9285510', 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9285510/')],
         evidence='Fukumori at the Jet Propulsion Laboratory, Caltech (search summaries of this record and of the 2022 '
                  'JPO article page); the byline of this paper and the JPL affiliations of the other authors were not '
                  'seen.',
         does='**Result.** Adjoint sensitivities of the ECCO ocean state estimate are used to establish causality for '
              'interannual sea level at Nantucket: wind forcing explains about 67% of the variance and wind plus '
              'buoyancy forcing about 97%. The wind effect is mostly local, from the New England shelf; remote subpolar '
              'North Atlantic buoyancy forcing acts years later through slow advection, with a faster wave response '
              'within weeks; the hypothesis that Labrador Sea wind stress is a major driver is not supported. The '
              'response is linear, to first order about the state estimate.',
         sota='Adjoint-based causal attribution of coastal sea level inside a dynamically consistent state estimate: fit '
              'the world (abduction), then propagate each forcing.',
         gap='Linear and deterministic; no uncertainty bands or coverage; no density-driven response.',
         inputs='The adjoint of the aquifer model about an assimilated state gives lagged sensitivity kernels of the '
                'heads to $T$, $S$ and $\\kappa$; the lag of the peak rain sensitivity estimates $\\tau$ (our inference).',
         dispersion='None.',
         bcs='The sea-level boundary splits into a local, predictable part and a remote part with long lags; additive '
             'forcings drop out of a factual-minus-counterfactual difference when the response is linear.',
         step='Proposition K1 makes their linear attribution a guaranteed one: in the test bed the kernel of the heads '
              'to recharge is exact ($g=K_g f$), the effect is its product with $\\kappa\\Delta f$, and the anchor band '
              'for $\\kappa$ brackets the whole effect path with risk <<dh_none_anc>> (T21). Their "fit the world" step '
              'is the abduction whose value for the head effect is <<va_dh4>> with four loggers (T22).',
         steps=['invert', 'guarantee'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='C2', inst='Caltech', year=2024, short='Non-Gaussian Markov structure by transport',
         title='Learning Non-Gaussian Graphical Models via Hessian Scores and Triangular Transport',
         authors='Ricardo Baptista, Rebecca Morrison, Olivier Zahm, Youssef Marzouk',
         venue='Journal of Machine Learning Research 25(85), 1–46 (2024)',
         links=[('JMLR 25(85)', 'https://jmlr.org/papers/v25/21-0022.html'),
                ('arXiv:2101.03093', 'https://arxiv.org/abs/2101.03093')],
         evidence='Baptista with a caltech.edu address in the JMLR version (search summary); the earlier arXiv version '
                  'lists MIT.',
         does='**Result (closely paraphrased).** A conditional-independence score matrix $\\Omega$, built from '
              'integrated Hessian information of the log-density, scores whether $X_i$ and $X_j$ are independent given '
              'all other variables; $\\Omega$ bounds the conditional mutual information from above under stated '
              'assumptions, and the sparsity of the graph is explicitly linked to the sparsity of triangular '
              '(Knothe–Rosenblatt) transport maps. The SING algorithm estimates the density with a triangular map, '
              'thresholds $\\Omega$ and refits; the graph estimator is consistent; demonstrated on a chaotic system with '
              'local interactions. Exact assumptions and rates were not read.',
         sota='Consistent nonparametric Markov-structure learning for continuous non-Gaussian laws, with an '
              'information-theoretic guarantee.',
         gap='An undirected graph (no causal direction); independent samples; no time-series version.',
         inputs='On a simulated joint ensemble of rain, recharge, heads, chloride, $T$, $S$ and $\\tau$, it shows which '
                'observations inform which parameters.',
         dispersion='It can test whether the dispersivity is independent of the heads given the chloride; if so, only '
                    'chloride facts constrain the width of the transition zone (our inference).',
         bcs='It can test whether inflow and sea level are separated from the rain by the heads, i.e. which latent '
             'boundary conditions need abduction.',
         step='In the test bed that test has a closed-form answer, which SHKAKU-GO uses: given $\\kappa$ and $\\tau$ '
              'the effect is independent of every latent history (Proposition K1), so its Markov blanket is '
              '$\\{\\kappa,\\tau\\}$; the counterfactual level needs the histories, and four loggers narrow its floor '
              '<<va_hc4>>-fold against rain alone (T22). Their score matrix computed on simulated twins would recover '
              'that blanket from samples.',
         steps=['invert', 'design'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='C3', inst='Caltech', year=2022, short='Sources of Mediterranean sea-level change',
         title='The Sources of Sea-Level Changes in the Mediterranean Sea since 1960',
         authors='Francisco M. Calafat, Thomas Frederikse, Kevin Horsburgh',
         venue='Journal of Geophysical Research: Oceans 127(9), e2022JC019061 (2022)',
         links=[('doi:10.1029/2022JC019061', 'https://doi.org/10.1029/2022JC019061'),
                ('Zenodo data record', 'https://zenodo.org/records/7046702')],
         evidence='The Zenodo record of the reconstruction lists the Jet Propulsion Laboratory among three affiliations '
                  '(with the National Oceanography Centre and the Green Climate Fund); which author holds it was not '
                  'shown.',
         does='**Result.** A spatial Bayesian reconstruction that combines tide gauges, altimetry and sea-level '
              'fingerprints splits Mediterranean sea level since 1960 into sterodynamic, contemporary '
              'gravitation–rotation–deformation, glacial isostatic adjustment and short-term components. Sea level fell '
              'by −0.3 ± 0.5 mm/yr over 1960–1989, because rising atmospheric pressure offset the sterodynamic rise, '
              'and rose by 3.6 ± 0.3 mm/yr over 2000–2018 through sterodynamic change and land-ice loss; since 2000 the '
              'Adriatic, Aegean and Levantine have risen fastest.',
         sota='The first basin-wide Mediterranean sea-level reconstruction since 1960 with attribution by source.',
         gap='Coarse at the Albanian coast; vertical land motion uncertain; Bayesian credible intervals without a '
             'coverage guarantee.',
         inputs='None.',
         dispersion='None directly.',
         bcs='Component priors and rates for the Adriatic boundary of Fushë-Kuqe; in the structural model the sea level '
             'is an exogenous root not caused by the local rain, so a rain counterfactual keeps it at its factual value.',
         step='That is the shared-history assumption under which the sea level cancels from the effect (Proposition K1). '
              'Their components also define the natural sea-level counterfactual (no pressure offset), for which the '
              'same twin construction applies with the sea level, not the rain, as the intervened cause.',
         steps=['prior'], informs=dict(inputs=0, dispersion=0, bcs=2)),
    dict(id='C4', inst='Caltech', year=2022, short='Twin experiments on pressure loading',
         title='Low-Frequency Dynamic Ocean Response to Barometric-Pressure Loading',
         authors='Christopher G. Piecuch, Ichiro Fukumori, Rui M. Ponte, Michael Schindelegger, Ou Wang, Mengnan Zhao',
         venue='Journal of Physical Oceanography 52(11), 2627–2641 (2022)',
         links=[('doi:10.1175/JPO-D-22-0090.1', 'https://doi.org/10.1175/JPO-D-22-0090.1')],
         evidence='Fukumori at the Jet Propulsion Laboratory, Caltech (search summary of the article page).',
         does='**Result.** Twin model experiments with and without atmospheric-pressure loading, an intervention on one '
              'forcing, show that at periods of a month or longer and scales of about 300 km or more pressure loading '
              'drives basin-scale dynamic manometric sea-level variability of a few centimetres, largest over abyssal '
              'plains, shelves and marginal seas; on average it departs from the inverted-barometer response by about '
              '10% or less at monthly and about 1% or less at annual periods.',
         sota='Global interventional quantification of the dynamic (non-inverted-barometer) ocean response to pressure '
              'at satellite-gravimetry scales.',
         gap='Model only, without uncertainty quantification; no coupling to an aquifer; the Adriatic not studied '
             'specifically.',
         inputs='Indirectly: the barometric efficiency of a confined aquifer depends on storage (our inference).',
         dispersion='None.',
         bcs='At an annual step the inverted-barometer correction is good to about 1%, so pressure is a latent sea '
             'boundary that cancels from annual rain contrasts; at monthly steps in a marginal sea it may not, and '
             'should stay a nuisance.',
         step='Their twin experiment is the interventional design; SHKAKU-GO adds the counterfactual one, in which the '
              'data abduct the shared histories. The difference matters for levels, not for effects: with four loggers '
              'the value of abduction is <<va_hc4>> for the counterfactual head, while for the effect it acts through '
              '$\\kappa$ alone (Proposition K1, T22).',
         steps=['emulate', 'prior'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='C5', inst='Caltech', year=2025, short='Continental drying and groundwater loss',
         title='Unprecedented continental drying, shrinking freshwater availability, and increasing land contributions '
               'to sea level rise',
         authors='Hrishikesh A. Chandanpurkar, James S. Famiglietti, Kaushik Gopalan, David N. Wiese, Yoshihide Wada, '
                 'Kaoru Kakinuma, John T. Reager, Fan Zhang',
         venue='Science Advances 11, eadx0298 (2025)',
         links=[('doi:10.1126/sciadv.adx0298', 'https://doi.org/10.1126/sciadv.adx0298'),
                ('PMC12292907', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12292907')],
         evidence='Wiese at the Jet Propulsion Laboratory (university news release); Reager\'s JPL affiliation not '
                  'shown.',
         does='**Result.** GRACE and GRACE-FO data since 2002 show continental drying (land outside Greenland and '
              'Antarctica) at unprecedented rates, the drying area growing each year by about twice the area of '
              'California; groundwater depletion accounts for 68% of the loss of terrestrial water storage over '
              'non-glaciated regions; four Northern Hemisphere "mega-drying" regions are identified, and the continents '
              'are reported to contribute more to sea-level rise than the ice sheets (a press framing to be checked '
              'against the paper).',
         sota='A global attribution of continental drying to groundwater depletion inside the sea-level budget.',
         gap='About 300 km resolution; an accounting decomposition, not a causal identification of pumping against '
             'climate; no counterfactual.',
         inputs='A large-scale prior on the groundwater share of storage change (whether Albania lies in a mega-drying '
                'region was not checked).',
         dispersion='None.',
         bcs='Regional drying trends constrain a long-term decline of the inland inflow; the land-water term feeds the '
             'sea boundary.',
         step='Their accounting says what was lost; SHKAKU-GO says what would have been lost in a drier climate, with a '
              'band: in the test bed a 40% drought lowers the head at the well by <<dh_mean>> m on average, and four '
              'loggers bracket that effect with a floor half-width of <<dh_floor>> m (T21, T22).',
         steps=['prior', 'check'], informs=dict(inputs=1, dispersion=0, bcs=2)),
]

BERKELEY = [
    dict(id='B1', inst='Berkeley', year=2025, short='Dynamic mediation with carryover',
         title='Multivariate dynamic mediation analysis under a reinforcement learning framework',
         authors='Lan Luo, Chengchun Shi, Jitao Wang, Zhenke Wu, Lexin Li',
         venue='The Annals of Statistics 53(1), 400–425 (2025)',
         links=[('doi:10.1214/24-AOS2475', 'https://doi.org/10.1214/24-AOS2475'),
                ('arXiv:2310.16203', 'https://arxiv.org/abs/2310.16203')],
         evidence='Listed in the CV of Lexin Li (Biostatistics, UC Berkeley) on the Berkeley domain as "Annals of '
                  'Statistics, 53, 400–425 (2025)"; the affiliation lines of the paper were not seen.',
         does='**Result.** In a "Markov mediation process" with time-varying linear structural equations and '
              'multivariate, conditionally dependent mediators observed over many time points, an individual mediation '
              'effect is defined for each mediator through simultaneous interventions and split into an immediate effect '
              'and a delayed effect, the carryover through past treatments and mediators; a closed form, an iterative '
              'estimator with bootstrap inference and its asymptotics are given, and the method is applied to a 26-week '
              'randomized mobile-health trial. The exact conditions of the theorems were not seen.',
         sota='The first definition, closed form and inference for multivariate dynamic mediation with carryover in a '
              'Markov process.',
         gap='Linear structural equations; interventional (rung 2) only; asymptotic; no distribution-free bands.',
         inputs='Rain → recharge (mediator) → head: $\\kappa$ and $\\tau$ become the lagged path coefficients of the '
                'delayed effect, $T$ and $S$ the autoregression of the head.',
         dispersion='Chloride as a second mediator (head → interface → chloride); the dispersivity sits in the '
                    'coefficients of that equation.',
         bcs='Rain is exogenous, like their randomized treatment; forcings that the rain does not affect enter '
             'additively and cancel in a contrast of two rain interventions (our inference).',
         step='SHKAKU-GO gives the finite-sample, guaranteed version for the aquifer: the effect through recharge is '
              '$\\kappa\\,g(\\Delta f)$ (Proposition K1) and its anchor band holds for any law of the histories (risk '
              '<<dh_params_anc>> under shifted parameters, T21). Their immediate and delayed parts are visible in the '
              'late-season counterfactual: rain 30 days later raises the head at the well in <<late_up_dh>> of the weeks '
              'and lowers it in the others.',
         steps=['emulate', 'guarantee'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='B2', inst='Berkeley', year=2025, short='Counterfactual likelihood with noise abduction',
         title='Counterfactual generative modeling with variational causal inference',
         authors='Yulun Wu, Louie McConnell, Claudia Iriondo',
         venue='The Thirteenth International Conference on Learning Representations (ICLR 2025)',
         links=[('ICLR 2025 poster', 'https://iclr.cc/virtual/2025/poster/28343'),
                ('arXiv:2410.12730', 'https://arxiv.org/abs/2410.12730')],
         evidence='Wu at the University of California, Berkeley (search summary of the arXiv listing); McConnell at '
                  'Genentech.',
         does='**Result.** Theorem 1 gives a variational lower bound on the individual counterfactual log-likelihood '
              '$\\log p(Y\'\\mid Y,X,T,T\')$ for variables that follow a twin-network Bayesian network, in which the '
              'factual and counterfactual outcomes and treatments are separate variables; aligning distributions on '
              'matched pairs enforces a disentangled abduction of the exogenous noise. The method beats the baselines '
              '"by a wide margin" in mean squared error on Morpho-MNIST, where true counterfactuals exist, and improves '
              '$R^2$ on single-cell perturbation data (numbers not seen).',
         sota='A lower bound on the individual counterfactual likelihood, with noise abduction, inside a deep generative '
              'model.',
         gap='No coverage guarantee; identifiability conditions not seen; images and cells, not dynamical systems.',
         inputs='The abducted latent carries the aquifer-specific unknowns unchanged from the factual to the drought '
                'world.',
         dispersion='None.',
         bcs='Initial head, sea-level and inflow paths as exogenous noise abducted from heads and chloride; their target '
             '$p(Y\'\\mid Y,X,T,T\')$ rather than $p(Y\'\\mid X,T\')$ is the value of abduction.',
         step='In the linear test bed both laws are exact, so the value of abduction is a number: the floor of the '
              'counterfactual head falls <<va_hc4>>-fold from rain alone, where rung 3 collapses to rung 2 (Proposition '
              'K2), to four loggers (T22). Their twin network takes the noise as shared across worlds; Proposition K3 '
              'shows that no data test this, and an independent twin noise widens the counterfactual recharge floor '
              '<<rc_rho0>>-fold (T23).',
         steps=['emulate', 'invert'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='B3', inst='Berkeley', year=2023, short='Conformal intervals for individual effects',
         title='Conformal meta-learners for predictive inference of individual treatment effects',
         authors='Ahmed M. Alaa, Zaid Ahmad, Mark van der Laan',
         venue='Advances in Neural Information Processing Systems 36 (NeurIPS 2023, oral)',
         links=[('NeurIPS 2023', 'https://proceedings.neurips.cc/paper_files/paper/2023/hash/'
                                 '94ab02a30b0e4a692a42ccd0b4c55399-Abstract-Conference.html'),
                ('arXiv:2308.14895', 'https://arxiv.org/abs/2308.14895')],
         evidence='Listed on the Berkeley site of Alaa\'s lab and on the Berkeley Center for Targeted Machine Learning '
                  'site; van der Laan is in Biostatistics, UC Berkeley.',
         does='**Result (close to the abstract).** Split conformal prediction on the pseudo-outcomes of a CATE '
              'meta-learner gives intervals for individual treatment effects; inference is marginally valid if the '
              'pseudo-outcome conformity scores stochastically dominate the "oracle" scores evaluated on the unobserved '
              'individual effects, and common meta-learners such as the doubly robust learner satisfy a model- and '
              'distribution-free stochastic (convex) dominance condition that gives validity at practically relevant '
              'coverage levels (the exact range of $\\alpha$ was not confirmed).',
         sota='The first general conformal wrapper for individual effects across meta-learners, with a checkable '
              'condition for validity.',
         gap='Marginal validity; exchangeable units rather than time series; overlap needed.',
         inputs='A distribution-free band for a unit-level drought effect from doubly robust pseudo-outcomes.',
         dispersion='None.',
         bcs='The propensity of a drought-level rain regime is known from the rain law, so the pseudo-outcomes need no '
             'treatment model (our inference).',
         step='Anchor twins are the aquifer\'s pseudo-outcomes: factual truth plus the effect of the simulator\'s '
              'mechanism (Proposition K4). Where the mechanism is right they equal the oracle twin and the band is '
              'valid (risk <<anc_none_rng>> without shift); under a 35-day delay they no longer dominate the oracle '
              'scores and validity fails for the effects (risk <<anc_delay_eff>>): the dominance condition, measured.',
         steps=['guarantee', 'check'], informs=dict(inputs=1, dispersion=0, bcs=1)),
    dict(id='B4', inst='Berkeley', year=2024, short='Probabilities of causation as desiderata',
         title='Desiderata for representation learning: a causal perspective',
         authors='Yixin Wang, Michael I. Jordan',
         venue='Journal of Machine Learning Research 25, paper 275, 1–65 (2024)',
         links=[('JMLR 25', 'https://jmlr.org/papers/v25/21-107.html'),
                ('arXiv:2109.03795', 'https://arxiv.org/abs/2109.03795')],
         evidence='Jordan at UC Berkeley (EECS and Statistics) in the JMLR version; Wang at the University of Michigan '
                  '(search summary).',
         does='**Result.** Non-spuriousness, efficiency and disentanglement of representations are defined as rung-3 '
              'quantities: non-spuriousness as the probability of sufficiency, efficiency as the probability of '
              'necessity, and both together as the probability of necessity and sufficiency of the representation for '
              'the label; they are made measurable through counterfactual quantities and their observable implications, '
              'which leads to the CAUSAL-REP algorithm for non-spurious representations of image and text data. The '
              'identification theorem itself was not seen.',
         sota='A formal account of representation desiderata as probabilities of causation, in a top journal.',
         gap='Binary indicators; no time series; no bands.',
         inputs='None directly.',
         dispersion='None.',
         bcs='"Was the drought necessary and sufficient for the head drop, or for chloride crossing a threshold?" Under '
             'monotonicity (less rain never raises the head with the boundaries fixed) the probabilities of causation '
             'are identified (our inference).',
         step='Monotonicity is exactly what Proposition K3 puts at risk: with the recharge error shared, a 40% drought '
              'lowers the recharge in every week; with an independent twin noise it raises it in <<up_dr0>> of the weeks, '
              'while the head at the well, which smooths the noise, almost never rises (<<up_dh0>>). Probabilities of '
              'causation for recharge thus depend on the untestable coupling, those for heads hardly.',
         steps=['check'], informs=dict(inputs=0, dispersion=0, bcs=1)),
    dict(id='B5', inst='Berkeley', year=2022, short='Counterfactual rain for an observed season',
         title='Attribution of 2020 hurricane season extreme rainfall to human-induced climate change',
         authors='Kevin A. Reed, Michael F. Wehner, Colin M. Zarzycki',
         venue='Nature Communications 13, 1905 (2022); an Author Correction exists',
         links=[('doi:10.1038/s41467-022-29379-1', 'https://doi.org/10.1038/s41467-022-29379-1'),
                ('Author Correction', 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9072538/')],
         evidence='Wehner at Lawrence Berkeley National Laboratory (search summary); the paper is indexed by the US '
                  'Department of Energy (OSTI 1869672).',
         does='**Result (quoted figures).** Human-induced climate change increased the extreme 3-hourly rainfall rates '
              'of the 2020 North Atlantic storms of at least tropical-storm strength by 10% and their extreme 3-day '
              'accumulations by 5% (11% and 8% for hurricane strength), with sea-surface temperatures 0.4–0.9 °C warmer '
              'in the season. Hindcasts start every 3 days from 1 June 2020; the counterfactual removes the '
              'anthropogenic signal from the initial temperature, humidity and sea-surface temperature fields (design as '
              'in the related Dorian study). What the Author Correction changed was not checked.',
         sota='Whole-season, observation-conditioned (hindcast) attribution of extreme tropical-cyclone rainfall.',
         gap='Model-based; ensemble spread is not a calibrated band; Atlantic tropical cyclones, not Mediterranean rain.',
         inputs='None.',
         dispersion='None.',
         bcs='A recipe for a counterfactual rain series for the same years, conditioned on the observed weather: the '
             'forcing that a rung-3 question for Fushë-Kuqe needs.',
         step='Their counterfactual rain is the $P\'$ of SHKAKU-GO. Fed into the twin it gives the aquifer\'s answer '
              'with a guarantee; but Proposition K2 says that the rain alone gives only the interventional answer, and '
              'Proposition K4 that the answer is as good as the mechanism: for a season shifted by 30 days, a wrong '
              'delay makes the anchor band for the head effect fail (risk <<late_delay_anc>>), while the enlarged law '
              'gives <<late_delay_T>> (T24).',
         steps=['prior', 'emulate'], informs=dict(inputs=0, dispersion=0, bcs=2)),
]

MIT = [
    dict(id='M1', inst='MIT', year=2023, short='Policy counterfactuals from impulse responses',
         title='What Can Time-Series Regressions Tell Us About Policy Counterfactuals?',
         authors='Alisdair McKay, Christian K. Wolf',
         venue='Econometrica 91(5), 1695–1725 (2023)',
         links=[('doi:10.3982/ECTA21045', 'https://doi.org/10.3982/ECTA21045'),
                ('Econometric Society', 'https://www.econometricsociety.org/publications/econometrica/2023/09/01/'
                                        'What-Can-Time-Series-Regressions-Tell-Us-About-Policy-Counterfactuals'),
                ('NBER w30358', 'https://www.nber.org/papers/w30358')],
         evidence='Wolf listed as "MIT and NBER" (search summaries); McKay at the Federal Reserve Bank of Minneapolis.',
         does='**Result (paraphrased from the abstract).** In a general class of linearised structural dynamic models, '
              'the impulse responses to contemporaneous and news shocks to the prevailing policy rule — causal effects '
              'that can be estimated from time series — suffice to construct the counterfactual paths of all outcomes '
              'under an alternative rule: a sequence of shocks to the old rule is chosen so that, as the private sector '
              'perceives it, the instrument follows the path the new rule would imply. Under the assumption that policy '
              'affects private behaviour only through the expected path of the instrument (paraphrased), the '
              'counterfactuals are robust to the Lucas critique; with few identified shocks only rules whose deviations '
              'lie in their span can be evaluated.',
         sota='The identification theorem for rule counterfactuals in dynamic structural models from estimable impulse '
              'responses alone.',
         gap='Linear; responses at all horizons needed; no uncertainty band for the counterfactual path; nothing on the '
             'coupling of noise across worlds.',
         inputs='$T$, $S$, $\\kappa$ and $\\tau$ matter for a rain counterfactual only through the impulse response of '
                'the heads to rain; the response, not the parameters, is the sufficient statistic.',
         dispersion='None (linear); the transition zone enters only if linearised about the present interface.',
         bcs='In a linear aquifer the sea level, the inflow and the initial head enter additively and cancel in the '
             'counterfactual contrast; the analogue of their span condition is that a rain counterfactual needs only '
             'the response to the counterfactual rain.',
         step='Proposition K1 is their theorem for the aquifer, with uncertainty: the drought effect is '
              '$\\kappa\\Delta g$, the push-forward of the posterior of $\\kappa$, and 20 anchors make the whole effect '
              'path a guaranteed band (risk <<dh_none_anc>> without shift, T21). The span condition has a sharp '
              'analogue: under a wrong delay the band of the right $\\kappa$ fails (risk <<dh_delay_anc>>).',
         steps=['emulate', 'guarantee'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='M2', inst='MIT', year=2023, short='A counterfactual simulator from traces',
         title='CausalSim: A Causal Framework for Unbiased Trace-Driven Simulation',
         authors='Abdullah Alomar, Pouya Hamadanian, Arash Nasr-Esfahany, Anish Agarwal, Mohammad Alizadeh, Devavrat '
                 'Shah',
         venue='20th USENIX Symposium on Networked Systems Design and Implementation (NSDI 2023), 1115–1147; Best Paper '
               'Award',
         links=[('USENIX NSDI 2023', 'https://www.usenix.org/conference/nsdi23/presentation/alomar'),
                ('arXiv:2201.01811', 'https://arxiv.org/abs/2201.01811'),
                ('MIT LIDS news', 'https://lids.mit.edu/node/2400')],
         evidence='Authors at MIT CSAIL, IDSS and LIDS (search summaries); MIT LIDS news item on the Best Paper Award.',
         does='**Result.** Trace-driven simulators are biased because the traces depend on the algorithm in use when '
              'they were collected. CausalSim learns a causal model of the system dynamics together with latent factors '
              'per trace and replays each trace under another algorithm with the same latent conditions; unbiased '
              'simulation becomes tensor completion with extremely sparse observations, made possible by the '
              'distributional invariance of the latent factors across the arms of a randomized trial. On ten months of '
              'video-streaming data and on synthetic data it cuts the error by 53% and 61% on average against '
              'expert-designed and supervised-learning baselines. The formal theorem was not seen.',
         sota='The first systems-scale counterfactual simulator: abduction of latent conditions per trace, then replay '
              'under a new intervention.',
         gap='Needs randomized and diverse interventions and low rank; no guaranteed bands; the noise coupling across '
             'worlds is fixed, not questioned.',
         inputs='$T$, $S$ and $\\kappa$ belong to the shared mechanism learned once across years; each year\'s latent '
                'aquifer state is abducted and replayed with drought rain.',
         dispersion='None directly.',
         bcs='Sea level and initial head as latent per-year conditions held fixed in the twin; their invariance '
             'condition becomes "rain as-if random with respect to those conditions", the independence assumed in '
             'Proposition K2.',
         step='Their replay is the abduction step of SHKAKU-GO, and Proposition K3 is the warning their benchmark cannot '
              'see: the replay holds the latent noise fixed ($\\rho$ = 1); if the recharge error is not shared across '
              'worlds the counterfactual recharge floor widens <<rc_rho0>>-fold (T23), and no trace, however long, says '
              'which coupling is true.',
         steps=['emulate', 'invert'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='M3', inst='MIT', year=2025, short='Response-function emulation of forced scenarios',
         title='Rapid Emulation of Spatially Resolved Temperature Response to Effective Radiative Forcing',
         authors='Christopher B. Womack, Paolo Giani, Sebastian D. Eastham, Noelle E. Selin',
         venue='Journal of Advances in Modeling Earth Systems 17(1), e2024MS004523 (2025)',
         links=[('doi:10.1029/2024MS004523', 'https://doi.org/10.1029/2024MS004523'),
                ('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/166624')],
         evidence='Deposited in DSpace@MIT and listed by the MIT Center for Sustainability Science and Strategy; '
                  'per-author affiliations were not seen.',
         does='**Result.** Spatially resolved impulse-response functions of near-surface temperature to effective '
              'radiative forcing are obtained by direct deconvolution of CMIP6 output; the emulator reproduces five '
              'CMIP6 experiments with a mean global relative error of 1.49% at mid-century and 1.25% at the end of the '
              'century and runs a 1000-member ensemble in under a second. The remaining error is attributed to '
              'state-dependent feedbacks such as nonlinear Arctic sea-ice melt. No formal theorem.',
         sota='Fast, spatially resolved linear-response emulation of forced scenarios, with the limits of superposition '
              'located.',
         gap='Deterministic, without bands or observation noise; linear.',
         inputs='Deconvolving rain against heads gives the response whose lag encodes $\\tau$ and whose size encodes '
                '$\\kappa$, $T$ and $S$.',
         dispersion='None.',
         bcs='Sea-level and inflow contributions stay in the baseline and cancel between scenarios; state-dependent '
             'feedback is the warning for a moving interface.',
         step='The map $g=K_g f$ of the test bed is such a response function, exact to 10⁻¹⁴ (Section 4.1), so every '
              'counterfactual of SHKAKU-GO costs one matrix product. What their emulator lacks is the band: a 40% '
              'drought lowers the head at the well by <<dh_mean>> m on average, and with four loggers the narrowest '
              'valid band for that effect has a half-width of <<dh_floor>> m (T21).',
         steps=['emulate'], informs=dict(inputs=2, dispersion=0, bcs=1)),
    dict(id='M4', inst='MIT', year=2022, short='Omitted-variable bias of causal machine learning',
         title='Long Story Short: Omitted Variable Bias in Causal Machine Learning',
         authors='Victor Chernozhukov, Carlos Cinelli, Whitney K. Newey, Amit Sharma, Vasilis Syrgkanis',
         venue='The Review of Economics and Statistics, forthcoming, doi:10.1162/REST.a.1705 (volume and year not '
               'confirmed); NBER Working Paper 30302 (2022)',
         links=[('doi:10.1162/REST.a.1705', 'https://doi.org/10.1162/REST.a.1705'),
                ('NBER w30302', 'https://www.nber.org/papers/w30302'),
                ('arXiv:2112.13398', 'https://arxiv.org/abs/2112.13398')],
         evidence='Chernozhukov and Newey at the Department of Economics, MIT (search summaries).',
         does='**Result (gist).** For causal parameters that are linear functionals of the outcome regression (average '
              'effects, average derivatives, policy effects), the omitted-variable bias between the "short" parameter '
              'with the observed confounders and the "long" one with latent confounders is bounded through the long and '
              'short Riesz representers. The bound depends only on how much the latent variables add to the variation '
              'of the outcome regression and of the Riesz representer, and its identifiable parts are estimated by '
              'debiased machine learning with valid inference; plausibility judgments on the explanatory power of the '
              'omitted variables then give sharp bias bounds.',
         sota='The general nonparametric sensitivity analysis and partial identification for debiased machine-learning '
              'causal functionals.',
         gap='Independent, static data and linear functionals; neither time series nor unit-level (rung-3) '
             'counterfactuals.',
         inputs='Unobserved heterogeneity of $T$, $S$ or $\\kappa$ when estimating rain-to-head effects across wells '
                'gives bounds instead of points.',
         dispersion='None.',
         bcs='Latent inflow or sea level as omitted confounders: a latent with no link to the rain adds no bias, the '
             'regression analogue of Proposition K1.',
         step='Proposition K3 is a sensitivity analysis of the same spirit on rung 3. Its sensitivity parameter is the '
              'cross-world coupling $\\rho$, which no data identify; the coupling-robust band is the union over a grid '
              'of $\\rho$ in [0, 1], valid for every $\\rho$ on the grid (largest risk <<robust_risk>>, T23), at '
              '<<robust_cost>> times the width of the shared-noise band when the noise is in fact shared.',
         steps=['check', 'guarantee'], informs=dict(inputs=1, dispersion=0, bcs=1)),
    dict(id='M5', inst='MIT', year=2023, short='Counterfactual entries with a central limit theorem',
         title='Causal Matrix Completion',
         authors='Anish Agarwal, Munther Dahleh, Devavrat Shah, Dennis Shen',
         venue='Proceedings of the Thirty Sixth Conference on Learning Theory (COLT 2023), PMLR 195, 3821–3826 (extended '
               'abstract; full paper arXiv:2109.15154)',
         links=[('PMLR 195', 'https://proceedings.mlr.press/v195/agarwal23c.html'),
                ('arXiv:2109.15154', 'https://arxiv.org/abs/2109.15154')],
         evidence='Agarwal, Dahleh and Shah at MIT (LIDS) and Shen at UC Berkeley (talk page and LIDS listing in search '
                  'summaries).',
         does='**Result.** In a low-rank latent-factor potential-outcomes model where missingness may depend on the '
              'latent factors (missing not at random) and under a linear-span-inclusion condition, the Synthetic Nearest '
              'Neighbours estimator — synthetic controls combined with nearest neighbours over anchor rows and columns — '
              'is finite-sample consistent and asymptotically normal for every missing counterfactual entry; this gives '
              'entry-wise consistency and a central limit theorem for matrix completion under missing-not-at-random '
              'data. The theorem is in the arXiv version; the COLT version is an extended abstract.',
         sota='The first entry-wise central limit theorem for counterfactual entries under missing-not-at-random data.',
         gap='Asymptotic in units and periods; a fully observed anchor block is needed; Fushë-Kuqe has few heads.',
         inputs='In a wells × years matrix of heads, $T$ and $S$ become latent row factors that are never identified; '
                'the counterfactual head of a well in a drought year it did not see is borrowed from wells and years '
                'that did.',
         dispersion='Chloride entries likewise, but only if low rank, which is doubtful near the front.',
         bcs='Year-specific sea level and inflow are absorbed in latent column factors; monitoring gaps caused by them '
             'are allowed.',
         step='SHKAKU-GO gives the finite-sample counterpart for the head at an unmonitored well (1.5 km, between two '
              'loggers): its counterfactual band calibrated on 20 anchor twins is valid without shift (risk '
              '<<hc_none_anc>>) and under shifted parameters (<<hc_params_anc>>), at <<hc_none_ratio>> times the floor '
              '(T21).',
         steps=['invert', 'guarantee'], informs=dict(inputs=1, dispersion=1, bcs=1)),
]

INST_ORDER = ('Oxford', 'Caltech', 'Berkeley', 'MIT')


def all_cards():
    return OXFORD + CALTECH + BERKELEY + MIT


CARDS = all_cards()


def SOTA_ROWS(AJ, fill):
    """the rows of the state-of-the-art table; fill holds the numbers of text_shkaku.py."""
    return [
        ['Counterfactuals in dynamical systems',
         'Policy counterfactuals from impulse responses (M1); response-function emulators (M3); adjoint attribution of '
         'sea level (C1); dynamic mediation with carryover (B1)',
         'Linear and point-valued: no band for the counterfactual path, no account of what the latent boundaries do',
         'Effects are free of all latent boundary conditions and carry an anchor guarantee for the whole path '
         '(Proposition K1)',
         f'T21: head-effect band of 20 anchors, risk {fill["dh_none_anc"]} (no shift), {fill["dh_params_anc"]} '
         f'(shifted parameters)'],
        ['Abduction and counterfactual generators',
         'Counterfactual likelihood with noise abduction (B2); trace replay with latent factors (M2); neural SDE '
         'generators (O5); counterfactual weather and storms (O1, B5)',
         'The gain of abduction over intervention is not measured; rain-only counterfactuals are not recognised as '
         'interventional',
         'Value of abduction as a ratio of floors; rung 3 collapses to rung 2 with rain alone (Proposition K2)',
         f'T22: four loggers narrow the counterfactual-head floor {fill["va_hc4"]}-fold, the head-effect floor '
         f'{fill["va_dh4"]}-fold'],
        ['Identification and its limits',
         'Collider independence (O2); local causal identifiability of system parameters (O3); non-Gaussian Markov '
         'structure (C2); mixtures and latent factors (M5)',
         'Rung-2 identification; the cross-world coupling of noise is fixed by assumption',
         'The coupling is not identified by any data; a band robust to every coupling on a grid (Proposition K3)',
         f'T23: independent twin noise widens the counterfactual-recharge floor {fill["rc_rho0"]}-fold; robust band, '
         f'largest risk {fill["robust_risk"]}'],
        ['Guarantees for individual effects',
         'Conformal meta-learners (B3); sensitivity of causal machine learning (M4); probabilities of causation (B4); '
         'causal robust optimization (O4)',
         'Exchangeable units; validity rests on conditions about unobserved counterfactuals',
         'Anchor twins: anchors make counterfactual bands checkable, valid when the mechanism is right (Proposition K4)',
         f'T21: anchor risk {fill["anc_none_rng"]} without shift; {fill["anc_delay_eff"]} for the effects under a '
         f'35-day delay'],
        ['Mechanism error',
         'Counterfactual attribution assumes the model mechanism (O1, B5, C1)',
         'A wrong mechanism (here the vadose delay) is invisible to the counterfactual',
         'Enlarged law with the delay unknown, calibrated on simulated twins',
         f'T21, T24: enlarged-law risk {fill["dh_delay_T"]} (drought), {fill["late_delay_T"]} (late season) under the '
         f'35-day delay'],
        ['Coastal boundary in the causal model',
         'Sources of Mediterranean sea level (C3); pressure loading (C4); continental drying (C5)',
         'Attribution of the boundary itself, not of the aquifer\'s response',
         'The sea level as an exogenous shared history that cancels from rain effects (Proposition K1)',
         'Section 4.1'],
        ['Dispersion and mixing',
         'No 2022–2026 causal paper on dispersion at the four institutions beyond those already used',
         'Counterfactual chloride needs a transport model',
         'Left for the next step, with the transport model of review I',
         '–'],
    ]
