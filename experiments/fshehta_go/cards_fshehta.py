"""The twenty paper cards of the ninth state-of-the-art review (five per institution, 2020-2026), around the Time Series
Deconfounder (Bica, Alaa & van der Schaar, ICML 2020), from the notes of four literature searches (November 2026), and the
rows of the state-of-the-art table. Landing pages were reached through search results only, so every card is partly
verified. None of the twenty was a card of reviews I-VIII or appears in the earlier reviews of the series (checked with
the repository-wide search).

Fields as in ../kripa_go/cards_kripa.py ('steps' here: substitute, outcome, check, physics, design). <<key>> is a number
filled in from res/fshehta.json by text_fshehta.py."""

OXFORD = [
    dict(id='O1', inst='Oxford', year=2020, short='Robustness audit of many interventions over time',
         title='How Robust are the Estimated Effects of Nonpharmaceutical Interventions against COVID-19?',
         authors='Mrinank Sharma, Sören Mindermann, Jan Markus Brauner, Gavin Leech, Anna B. Stephenson, Tomáš '
                 'Gavenčiak, Jan Kulveit, Yee Whye Teh, Leonid Chindelevitch, Yarin Gal',
         venue='Advances in Neural Information Processing Systems 33 (NeurIPS 2020), spotlight',
         links=[('NeurIPS proceedings', 'https://proceedings.neurips.cc/paper/2020/hash/'
                                        '8e3308c853e47411c761429193511819-Abstract.html'),
                ('arXiv:2007.13454', 'https://arxiv.org/abs/2007.13454'),
                ('OATML, Oxford', 'https://oatml.cs.ox.ac.uk/publications/202009_SharmaGal2020robustness.html')],
         evidence='Listed and hosted by the Oxford Applied and Theoretical Machine Learning group (Department of Computer '
                  'Science); the affiliation block of the NeurIPS version was not seen. The arXiv v1 title was "On the '
                  'robustness of effectiveness estimation of nonpharmaceutical interventions against COVID-19 '
                  'transmission".',
         does='**Result.** Two state-of-the-art models of the effect of nonpharmaceutical interventions are investigated '
              'and six variants with different structural assumptions are proposed. Generalisation is tested by holding '
              'out countries, and sensitivity to unobserved factors by letting interventions that were observed become '
              'unobserved ("NPI leave-outs"). Models that account for noise in the transmission compare favourably, and '
              'for them the policy conclusions are reported as remarkably robust; the authors also ground mathematically '
              'how the estimates should be read when common assumptions fail (abstract wording from search summaries).',
         sota='A structural-sensitivity protocol for the effects of many overlapping interventions in time series.',
         gap='No identification result or bound; unobserved factors are probed only through observed interventions.',
         inputs='Report the pumping effects across the plausible range of $S$, $\\kappa$ and $\\tau$; the vadose delay '
                'plays the role of the infection-to-report delay.',
         dispersion='Unresolved mixing is better carried as process noise than as a fixed dispersion coefficient, as '
                    'their noisy-transmission models suggest.',
         bcs='Leave-out tests for us: hide one well, or the sea level, and refit; hold out a well field as they hold out '
             'a country.',
         step='Their leave-out is a check that the analyst controls. FSHEHTA-GO adds one that physics controls: the '
              'reading of the recharge from the heads must be independent of the pumping given the substitute. It '
              'rejects every confounded scenario (power <<power>>) at its nominal size (<<size>> under no confounding), '
              'where the Time Series Deconfounder\'s own predictive check stays at <<tsd_p>>.',
         steps=['check'], informs=dict(inputs=1, dispersion=1, bcs=1)),
    dict(id='O2', inst='Oxford', year=2021, short='Kernel proxies for hidden confounders',
         title='Proximal Causal Learning with Kernels: Two-Stage Estimation and Moment Restriction',
         authors='Afsaneh Mastouri, Yuchen Zhu, Limor Gultchin, Anna Korba, Ricardo Silva, Matt Kusner, Arthur Gretton, '
                 'Krikamol Muandet',
         venue='Proceedings of the 38th International Conference on Machine Learning, PMLR 139, 7512–7523 (2021)',
         links=[('PMLR', 'https://proceedings.mlr.press/v139/mastouri21a.html'),
                ('arXiv:2105.04544', 'https://arxiv.org/abs/2105.04544')],
         evidence='The IP Paris research-portal record lists the University of Oxford among the affiliations (with UCL, '
                  'the Alan Turing Institute, ENSAE and MPI-IS); which author was at Oxford was not seen.',
         does='**Result.** Two kernel estimators of the average treatment effect in the proxy setting of Miao, Geng & '
              'Tchetgen Tchetgen — KPV (two-stage kernel regression) and PMMR (maximum moment restriction) — both with '
              'consistency guarantees; the outcome bridge function solves a Fredholm integral equation and is learned in '
              'a reproducing-kernel Hilbert space. The completeness and bridge-existence assumptions were not read '
              'verbatim.',
         sota='The first nonparametric (kernel) estimators for proximal causal inference with consistency guarantees.',
         gap='No time, no sequential proxies, no feedback from the outcome to the treatment.',
         inputs='An outcome-side proxy can be a head outside the cones of depression, a treatment-side proxy an irrigation '
                'index (crop evapotranspiration, farm electricity).',
         dispersion='Dispersion smooths the chloride response, which should make the bridge smoother (our inference).',
         bcs='The rain cannot be a proxy: it acts on chloride directly through the recharge.',
         step='The proxy route is the future work the Time Series Deconfounder names. FSHEHTA-GO takes it with a proxy '
              'whose bridge is known from physics: the heads, once the known drawdown is added back and the head kernel '
              'removed, are a linear reading of the recharge, the path through which every hidden cause acts. The '
              'bridge needs no kernel regression; the reading explains <<r2_phys>> of the hidden dryness in the case of '
              'Figure {{case}}, the history substitute <<r2_tsd>>.',
         steps=['substitute', 'physics'], informs=dict(inputs=1, dispersion=1, bcs=2)),
    dict(id='O3', inst='Oxford', year=2021, short='Synthetic twins from learned representations',
         title='SyncTwin: Treatment Effect Estimation with Longitudinal Outcomes',
         authors='Zhaozhi Qian, Yao Zhang, Ioana Bica, Angela Wood, Mihaela van der Schaar',
         venue='Advances in Neural Information Processing Systems 34 (NeurIPS 2021)',
         links=[('NeurIPS proceedings', 'https://proceedings.neurips.cc/paper/2021/hash/'
                                        '19485224d128528da1602ca47383f078-Abstract.html'),
                ('poster page', 'https://neurips.cc/virtual/2021/poster/27560')],
         evidence='A search summary of the paper header lists Ioana Bica at the University of Oxford and the Alan Turing '
                  'Institute; the other affiliations were not seen. The earlier arXiv title was "SyncTwin: Transparent '
                  'Treatment Effect Estimation under Temporal Confounding".',
         does='**Result.** Untreated outcomes follow a latent factor model with an individual latent factor and a '
              'time-varying latent trend. The method learns a time-constant representation from the pre-treatment '
              'history and builds a synthetic twin from a few weighted control units; Proposition 2 bounds the bias of '
              'the individual effect by how close the learned representation is to the true latent factor once the '
              'synthetic representation matches the target, and Proposition 1 justifies the supervised loss. The '
              'abstract reports that it reproduced the findings of a randomised trial from observational records (no '
              'numbers seen).',
         sota='Synthetic-control counterfactuals on learned representations, with a pre-treatment validity check.',
         gap='One treatment onset, a time-constant latent factor, no time-varying hidden confounder, no physics.',
         inputs='Time-constant well properties ($T$, $S$, screen depth, distance to the coast, $\\tau$) are the latent '
                'factor; donor wells with matching pre-change heads and chloride build the twin.',
         dispersion='A dispersion mismatch between target and donors shows as pre-treatment misfit: a free diagnostic.',
         bcs='A region-wide drought or sea-level trend is absorbed as the common trend; a drought demand that varies '
             'week by week and acts through pumping is not.',
         step='Same group, different factor: SyncTwin puts the factor in the outcomes, the Time Series Deconfounder in '
              'the treatments. FSHEHTA-GO shows why neither suffices for a fast confounder: a substitute built from the '
              'past misses the weekly innovations of the dryness (Proposition D1), and only a measurement of the path — '
              'the heads — recovers them.',
         steps=['substitute', 'outcome'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='O4', inst='Oxford', year=2022, short='Natural experiments against a common confounder',
         title='Opportunistic experiments to constrain aerosol effective radiative forcing',
         authors='Matthew W. Christensen and about twenty co-authors, among them Philip Stier (the full list was not '
                 'seen)',
         venue='Atmospheric Chemistry and Physics 22, 641–674 (2022), review article',
         links=[('doi:10.5194/acp-22-641-2022', 'https://doi.org/10.5194/acp-22-641-2022'),
                ('DOAJ record', 'https://doaj.org/article/b67802aa319b4f9ea1ad4a07bfa66e71')],
         evidence='A repository listing gives the first author at the Pacific Northwest National Laboratory and the '
                  'University of Oxford; Philip Stier is a co-author per DOAJ, his department was not seen.',
         does='**Result.** Correlational estimates of aerosol effects on clouds are confounded because meteorology drives '
              'both. The review assembles perturbations from well-defined sources — volcanic eruptions, ship tracks, '
              'wildfire plumes — as natural experiments; cloud albedo perturbations are found strongly sensitive to the '
              'background meteorology, strong increases of liquid water path are largely ruled out when the experiments '
              'are averaged, and the scaling to the global forcing remains unclear (wording of the abstract as quoted).',
         sota='A synthesis of natural-experiment constraints on aerosol–cloud forcing under a multi-cause confounder.',
         gap='Not a formal identification; extrapolation to the global scale.',
         inputs='Catalogue the opportunistic pumping shocks — power cuts, pump failures, new wells, bans — that are '
                'exogenous to the irrigation demand.',
         dispersion='A sharp pumping shock acts as a tracer test: the transient chloride response reads the dispersion.',
         bcs='Stratify the effect by the background state (wet or dry season, sea level, known rain) and average over '
             'events, as they stratify by meteorology.',
         step='Meteorology is to aerosol what dryness is to pumping: a multi-cause confounder. The idiosyncratic part '
              'of the pumping is our opportunistic experiment; Proposition D1 shows that it alone identifies the effect '
              'when the substitute leaves part of the common confounder, and that the share it buys shrinks as the '
              'number of wells grows (the bias of the summed effects tends to <<limit>>).',
         steps=['design'], informs=dict(inputs=1, dispersion=2, bcs=1)),
    dict(id='O5', inst='Oxford', year=2023, short='Panels with a smooth two-way latent structure',
         title='Linear panel regressions with two-way unobserved heterogeneity',
         authors='Hugo Freeman, Martin Weidner',
         venue='Journal of Econometrics 237, 105498 (2023)',
         links=[('doi:10.1016/j.jeconom.2023.105498', 'https://doi.org/10.1016/j.jeconom.2023.105498'),
                ('arXiv:2109.11911', 'https://arxiv.org/abs/2109.11911')],
         evidence='The 2021 CeMMAP working paper (CWP39/21) gives Martin Weidner at the Department of Economics and '
                  'Nuffield College, University of Oxford (search summary); the journal\'s affiliation block was not seen.',
         does='**Result.** The error of a linear panel regression is an unknown smooth function of two-way unobserved '
              'fixed effects, which generalises additive and interactive fixed effects. Two estimators are analysed: '
              'Bai\'s interactive fixed-effects estimator with a number of factors that grows asymptotically, and a '
              'two-step estimator that first groups the heterogeneity and then fits additive grouped effects; both come '
              'with asymptotic convergence results, Monte Carlo evidence and an application to UK house prices. A later '
              'paper states that the sieve estimator does not reach root-$NT$ asymptotic normality.',
         sota='Nonparametric two-way latent heterogeneity in linear panels, through growing-factor or grouped estimators.',
         gap='Linear in the regressors, no dynamics or treatment regimes; inference is not root-$NT$.',
         inputs='Chloride residuals plausibly look like $g(\\alpha_j,\\gamma_t)$: a well property and a time state.',
         dispersion='Smoother responses are closer to low rank, so fewer factors are needed (our inference).',
         bcs='A basin-wide drought acts through $\\gamma_t$; feedback from past chloride to pumping breaks the '
             'exogeneity.',
         step='Their answer to latent structure is double asymptotics in wells and weeks. Proposition D1 gives the '
              'warning for our case: if the latent state also drives the treatments, more wells do not help a '
              'substitute built from the past — the bias of the summed effects grows with $k$ toward <<limit>> '
              '(<<ideal8>> at 8 wells, <<ideal64>> at 64 for the best history substitute).',
         steps=['outcome'], informs=dict(inputs=2, dispersion=1, bcs=1)),
]

CALTECH = [
    dict(id='C1', inst='Caltech', year=2020, short='Lagged hidden states in a carbon budget',
         title='Lagged effects regulate the inter-annual variability of the tropical carbon balance',
         authors='A. A. Bloom, K. W. Bowman, J. Liu, A. G. Konings, J. R. Worden, N. C. Parazoo, V. Meyer, J. T. Reager, '
                 'H. M. Worden, Z. Jiang, G. R. Quetin, T. L. Smallman, J.-F. Exbrayat, Y. Yin, S. S. Saatchi, M. Williams, '
                 'D. S. Schimel (initials as seen)',
         venue='Biogeosciences 17, 6393–6422 (2020)',
         links=[('doi:10.5194/bg-17-6393-2020', 'https://doi.org/10.5194/bg-17-6393-2020'),
                ('NASA ESPO record', 'https://espo.nasa.gov/node/79683')],
         evidence='The first author is at JPL according to the ORNL record of a later CARDAMOM review and the CARDAMOM '
                  'code repository; NASA ESPO lists the paper; the per-author block of this paper was not seen.',
         does='**Result.** With the CARDAMOM Bayesian data–model fusion system (Markov chain Monte Carlo), concurrent and '
              'lagged effects both contribute substantially to the 2001–2015 inter-annual variability of the tropical '
              'net biome exchange; the lagged part acts mainly through net primary productivity, which depends on '
              'inter-annual variations in the foliar carbon and the plant-available water states. The discussion-paper '
              'title was "Lagged effects dominate…"; a lagged share quoted by one summary was not checked and is not '
              'used here.',
         sota='A data-constrained separation of concurrent and lagged drivers through hidden states.',
         gap='Model-based attribution of carbon fluxes; no formal causal identification.',
         inputs='The vadose delay $\\tau$ and the recharge coefficient $\\kappa$ are our lagged water state.',
         dispersion='Not covered.',
         bcs='Antecedent storage is a time-varying confounder: it shapes later irrigation demand and later recharge.',
         step='Their hidden state has memory; so has our dryness. Proposition D1 makes the memory the deciding '
              'parameter: with persistence 0.98 the best history substitute leaves <<ideal8_98>> of bias in the summed '
              'effects at 8 wells, with persistence 0.5 it leaves <<ideal8_50>>.',
         steps=['physics'], informs=dict(inputs=2, dispersion=0, bcs=1)),
    dict(id='C2', inst='Caltech', year=2020, short='False-discovery control for latent subspaces',
         title='False discovery and its control in low rank estimation',
         authors='Armeen Taeb, Parikshit Shah, Venkat Chandrasekaran',
         venue='Journal of the Royal Statistical Society Series B 82(4), 997–1027 (2020)',
         links=[('doi:10.1111/rssb.12387', 'https://doi.org/10.1111/rssb.12387'),
                ('CaltechAUTHORS', 'https://authors.library.caltech.edu/records/s635m-5y072'),
                ('arXiv:1810.08595', 'https://arxiv.org/abs/1810.08595')],
         evidence='CaltechAUTHORS record; Venkat Chandrasekaran is Caltech faculty and Armeen Taeb\'s Caltech PhD thesis '
                  'is dated 2020; the per-author affiliations were not seen.',
         does='**Result.** Discovery in low-rank estimation is reformulated geometrically, through row and column spaces, '
              'so that a false discovery is defined for a subspace. Subspace stability selection, a generalisation of '
              'stability selection, runs a low-rank estimator on subsamples and keeps the subspace close to most '
              'estimates, with control of false discoveries; factor analysis and latent-variable models are among the '
              'applications. The exact bound was not read.',
         sota='False-discovery control for the rank and subspace of factor and latent-variable models.',
         gap='Static; no causal or time-series semantics.',
         inputs='How many independent hydraulic combinations (for example the diffusivity $T/S$) the wells support.',
         dispersion='Not covered.',
         bcs='Keep a second common factor (the sea level, say) only if its subspace is stable.',
         step='The Time Series Deconfounder picks the latent dimension by a predictive check; a spurious direction soaks '
              'up treatment variation and destroys overlap. FSHEHTA-GO shows the extreme case: a substitute read from the '
              'current pumping makes the design near-singular (condition number <<cond>>), while a substitute read from '
              'another measurement — the heads — keeps it at <<cond_phys>>.',
         steps=['substitute', 'check'], informs=dict(inputs=1, dispersion=0, bcs=1)),
    dict(id='C3', inst='Caltech', year=2021, short='Latent confounders separated by interventions',
         title='Disentangling Observed Causal Effects from Latent Confounders using Method of Moments',
         authors='Anqi Liu, Hao Liu, Tongxin Li, Saeed Karimi-Bidhendi, Yisong Yue, Anima Anandkumar',
         venue='arXiv preprint 2101.06614 (2021); no peer-reviewed version was found',
         links=[('arXiv:2101.06614', 'https://arxiv.org/abs/2101.06614'),
                ('CaltechAUTHORS', 'https://authors.library.caltech.edu/records/b6a7k-k8085')],
         evidence='Deposited in CaltechAUTHORS ("Version Submitted"); Yisong Yue and Anima Anandkumar are Caltech faculty; '
                  'the per-author affiliations were not seen. A preprint: the only card of this review without a '
                  'peer-reviewed venue at Caltech.',
         does='**Result.** In a linear structural equation model whose latent confounders are independent sources and '
              'whose observed variables form a DAG, the method of moments establishes identifiability, and the '
              'identifiability and learnability guarantees hold when (soft) interventions are available; estimation '
              'uses a coupled tensor decomposition with linear constraints. The exact theorem was not read.',
         sota='Identifiability of the observed causal effects under independent latent confounders, given interventions.',
         gap='Independent units, linear, no time dynamics or sequential treatments; a preprint.',
         inputs='Pumping tests and scheduled cuts are soft interventions: they separate the response coefficients from '
                'the latent drought.',
         dispersion='Not covered; the model is linear.',
         bcs='Irrigation demand is a skewed, non-Gaussian common source of all pumping, which helps independent-source '
             'separation; the rain enters as an observed exogenous input.',
         step='Their interventions identify what observation cannot. Ours is the pumping test: it fixes the drawdown '
              'coefficients the physics branch needs. Proposition D4 prices what a wrong test costs — the bias is linear '
              'in the error, <<d4_10>> of $\\beta_1$ per 10% error of the drawdown, predicted to within <<d4_fit>>.',
         steps=['physics', 'design'], informs=dict(inputs=2, dispersion=0, bcs=1)),
    dict(id='C4', inst='Caltech', year=2021, short='Causal attribution through an adjoint model',
         title='Causal Mechanisms of Sea Level and Freshwater Content Change in the Beaufort Sea',
         authors='Ichiro Fukumori, Ou Wang, Ian Fenty (initials I., O., I. in the search results; the given names as in '
                 'card VII-C1)',
         venue='Journal of Physical Oceanography 51, 3217–3234 (2021)',
         links=[('doi:10.1175/jpo-d-21-0069.1', 'https://doi.org/10.1175/jpo-d-21-0069.1'),
                ('OSTST 2022 talk', 'https://ostst.aviso.altimetry.fr/fileadmin/user_upload/OSTST2022/Presentations/'
                                    'SC22022-Causal_Mechanism_of_Sea_Level_Change_in_the_Beaufort_Sea.pdf')],
         evidence='The companion dataset carries a JPL DOI prefix (10.48577/jpl.vsnuwe) and the work uses the ECCO '
                  'state estimate; the per-author affiliations were not seen.',
         does='**Result.** Causal relationships are quantified with the adjoint of the global, data-constrained ECCO '
              'ocean–sea-ice model over 1992–2017. The rise of the Beaufort Sea level is mostly halosteric, driven by a '
              'freshwater increase; seasonal change is dictated by the sea-ice variation and interannual change is mostly '
              'wind-driven through Ekman transport, while both forcings matter equally for decadal change. Wind-driven '
              'anomalies equilibrate within weeks, melt-driven changes persist for years.',
         sota='Adjoint-based causal attribution, split by forcing and by time scale, in a data-constrained geophysical '
              'model.',
         gap='The causal claims rest on the model structure; the adjoint is linearised; no identification or uncertainty '
             'statement.',
         inputs='An adjoint of the salinized-area functional gives its sensitivities to $T$, $S$, $\\kappa$ and $\\tau$.',
         dispersion='The adjoint sensitivity to the dispersion follows in the same way; their fast and slow responses are '
                    'our advective and storage-controlled ones.',
         bcs='Unknown sea-side forcing and recharge are control variables of a state estimate.',
         step='They separate forcings by their response times; so does FSHEHTA-GO. The head kernel (weeks) and the '
              'salinity kernel (months) differ, and the head kernel is identified from the salinity fit: profiling it '
              'removes the bias of a wrong kernel (<<kern_fixed>> of the 20% cut with the kernel 40% too short, '
              '<<kern_prof>> once profiled).',
         steps=['physics'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='C5', inst='Caltech', year=2021, short='Depletion of a Mediterranean plain',
         title='Groundwater Depletion Signals in the Beqaa Plain, Lebanon: Evidence from GRACE and Sentinel-1 Data',
         authors='Elias C. Massoud, Zhen Liu, Amin Shaban, Mhamad El Hage',
         venue='Remote Sensing 13(5), 915 (2021)',
         links=[('doi:10.3390/rs13050915', 'https://doi.org/10.3390/rs13050915'),
                ('MDPI', 'https://www.mdpi.com/2072-4292/13/5/915')],
         evidence='A search summary of the article places Zhen Liu and Elias C. Massoud at the Jet Propulsion Laboratory, '
                  'California Institute of Technology, with work carried out under a contract with NASA.',
         does='**Result.** Groundwater storage of the Beqaa Plain from GRACE (June 2002 – April 2017) is obtained by '
              'removing GLDAS soil moisture, snow and canopy water and the Qaraaoun reservoir from the total water '
              'storage; groundwater loss accounts for most of the decline, with trends of about +0.08 cm/yr in West '
              'Beqaa, −0.01 cm/yr in Rashaya and −1.10 cm/yr in Zahle, corroborated by Sentinel-1 subsidence and '
              'monitoring wells.',
         sota='Combined GRACE, InSAR and well detection of depletion in a data-poor Mediterranean plain.',
         gap='No causal separation of drought and pumping; no salinity; the satellite footprint is far larger than the '
             'plain.',
         inputs='Subsidence and heads together constrain the skeletal storage $S$.',
         dispersion='Not covered.',
         bcs='The residual "human" signal still contains the climate-driven loss of recharge: the confounding this '
             'review is about.',
         step='Budget attribution treats the residual as pumping; FSHEHTA-GO treats it as confounded. Without '
              'adjustment the summed well effects are overstated by <<naive8>> (in units of the salinity index per unit '
              'of pumping, true sum about 1); the physics substitute brings this to <<phys8>>.',
         steps=['physics'], informs=dict(inputs=2, dispersion=0, bcs=2)),
]

HARVARD = [
    dict(id='H1', inst='Harvard', year=2021, short='Instruments for a time-varying treatment',
         title='Instrumental variable estimation for a time-varying treatment and a time-to-event outcome via structural '
               'nested cumulative failure time models',
         authors='Joy Shi, Sonja A. Swanson, Peter Kraft, Bernard Rosner, Immaculata De Vivo, Miguel A. Hernán',
         venue='BMC Medical Research Methodology 21, 258 (2021)',
         links=[('doi:10.1186/s12874-021-01449-w', 'https://doi.org/10.1186/s12874-021-01449-w'),
                ('PMC8620657', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC8620657')],
         evidence='A search summary places the authors in the Department of Epidemiology, Harvard T.H. Chan School of '
                  'Public Health; a copy is held in Harvard\'s DASH repository; the data are from the Nurses\' Health '
                  'Study.',
         does='**Result.** g-estimation of structural nested cumulative failure time models is applied to instrumental '
              'variable analyses of time-varying treatments, and can use several measures of the treatment. The '
              'instrument conditions alone do not give a point estimate, so a homogeneity assumption is added. In '
              'simulations the instrumental estimates were close to the confounder-adjusted ones; in a Mendelian '
              'randomisation application the cumulative endometrial-cancer risk from age 45 to 72 was about 4.0% under '
              '"never drink" and 4.3% under "always half a drink per day".',
         sota='Instrumental g-estimation for time-varying treatments with failure-time outcomes.',
         gap='Homogeneity and one valid time-varying instrument; developed for epidemiology.',
         inputs='Instruments for pumping: power cuts, tariff changes, pump breakdowns, permits.',
         dispersion='The time until the chloride of a well exceeds a threshold is a natural failure time, and the '
                    'dispersion shapes how its risk builds up.',
         bcs='An instrument must be independent of the recharge and the sea-side state; homogeneity is doubtful near '
             'the sea boundary.',
         step='An instrument and a physics proxy are two answers to the same hidden confounder; the instrument needs '
              'exclusion, the proxy needs known physics. FSHEHTA-GO shows what the proxy buys when the hidden cause is '
              'local: crop stress at one farm biases the effect of that well by <<psi1_tsd>> with the history '
              'substitute and by <<psi1_phys>> with the reading of a logger next to it.',
         steps=['outcome', 'design'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='H2', inst='Harvard', year=2022, short='g-methods under parallel trends',
         title='Structural Nested Mean Models Under Parallel Trends Assumptions',
         authors='Zach Shahn, Oliver Dukes, Meghana G. Shamsunder, David Richardson, Eric Tchetgen Tchetgen, James '
                 'Robins',
         venue='arXiv preprint 2204.10291 (v1 April 2022, v8 August 2025); no journal version was found',
         links=[('arXiv:2204.10291', 'https://arxiv.org/abs/2204.10291v8')],
         evidence='A summary of the arXiv listing gives James Robins at the Harvard T.H. Chan School of Public Health '
                  '(the others at CUNY, Ghent, UC Irvine and Penn); the affiliation block of the PDF was not seen.',
         does='**Result.** Structural nested mean models, known to be identified under no unobserved confounding, are '
              'also identified under a conditional parallel-trends assumption of the kind used in time-varying '
              'difference-in-differences; a sensitivity analysis to violations of parallel trends is given, and optimal '
              'regimes follow under the added assumption of no effect modification by the unobserved confounders. The '
              'models carry lasting effects of a blip of treatment and sustained interventions on continuous or '
              'multi-dimensional treatments; worked examples include floods and flood insurance, temperature and crop '
              'yields.',
         sota='g-estimation for time-varying, continuous, multi-dimensional treatments without ignorability, under '
              'parallel trends.',
         gap='Parallel trends is doubtful for the nonlinear intrusion; a preprint.',
         inputs='The blip function over lags is the chloride response to a pumping pulse; the diffusivity $T/S$ and '
                '$\\tau$ set its shape.',
         dispersion='The dispersion sets how long a blip persists, and hence the lag window the model must cover.',
         bcs='A drought that shifts all wells alike satisfies parallel trends; one that acts more strongly near the sea '
             'boundary breaks it.',
         step='Parallel trends replace the absence of hidden confounders with an assumption about untreated trends. '
              'The physics substitute replaces it with a measurement: under correct physics it removes the multi-cause '
              'bias (the summed effects to <<phys8>>), and Proposition D4 says exactly how a wrong drawdown leaks back '
              '— a band the sensitivity analysis can carry.',
         steps=['outcome'], informs=dict(inputs=2, dispersion=2, bcs=1)),
    dict(id='H3', inst='Harvard', year=2023, short='Matching on treatment histories in panels',
         title='Matching Methods for Causal Inference with Time-Series Cross-Sectional Data',
         authors='Kosuke Imai, In Song Kim, Erik Wang (middle initial not confirmed)',
         venue='American Journal of Political Science 67(3), 587–605 (2023)',
         links=[('doi:10.1111/ajps.12685', 'https://doi.org/10.1111/ajps.12685'),
                ('author PDF', 'https://imai.sites.fas.harvard.edu/research/files/tscs.pdf')],
         evidence='Kosuke Imai, Departments of Government and Statistics, Harvard University; the paper is hosted on his '
                  'Harvard site. In Song Kim is at MIT; the third author\'s affiliation was not confirmed.',
         does='**Result.** Each treated observation is matched to control observations of other units in the same period '
              'with an identical treatment history over the previous $L$ periods; the matched sets are refined by '
              'matching or weighting on covariates, and a difference-in-differences estimator follows, equal to a '
              'weighted two-way fixed-effects estimator. The assumptions are no spillover, carryover limited to $L$ '
              'periods, and parallel trends given the treatment history and the covariates; standard errors by a block '
              'bootstrap; the PanelMatch R package implements it.',
         sota='A design-based matching and difference-in-differences method for time-series cross-sectional data, with '
              'diagnostics and software.',
         gap='No interference and finite carryover; treated versus control, so continuous pumping rates are not '
             'obviously covered (our inference).',
         inputs='The lag $L$ follows from $\\tau$ and the hydraulic response time $SL^2/T$.',
         dispersion='A slow dispersive tail stretches the carryover and forces a large $L$.',
         bcs='Wells sharing a cone of depression violate no-spillover; treatment may need defining at sector level.',
         step='Interference is the rule in an aquifer: the heads of one logger see every well. FSHEHTA-GO uses the '
              'interference instead of assuming it away — the known drawdown pattern is what lets the heads be read as '
              'recharge, and the reading is what the physics check tests.',
         steps=['outcome', 'check'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='H4', inst='Harvard', year=2023, short='Joint bounds under factor confounding',
         title='Partial identification and unmeasured confounding with multiple treatments and multiple outcomes',
         authors='Suyeon Kang, Alexander Franks, Michelle Audirac, Danielle Braun, Joseph Antonelli',
         venue='arXiv preprint 2311.12252 (v1 November 2023, v3 June 2025); no journal version was found',
         links=[('arXiv:2311.12252', 'https://arxiv.org/abs/2311.12252v3')],
         evidence='Danielle Braun is Principal Research Scientist, Department of Biostatistics, Harvard T.H. Chan School of '
                  'Public Health, and Michelle Audirac a data scientist of its NSAPH group (profile pages); the paper\'s '
                  'own affiliation block was not seen. The v1 title was "Sensitivity analysis with multiple treatments '
                  'and multiple outcomes with applications to air pollution mixtures".',
         does='**Result.** Under a factor confounding assumption, joint partial-identification regions for several '
              'estimands can be more informative than regions for each estimand alone; negative-control (null-effect) '
              'constraints enter as a special case of the sensitivity bound, and a constrained optimisation gives the '
              'regions under arbitrary negative-control constraints. In the Medicare application to air-pollution '
              'mixtures, the detrimental effect of black carbon is robust to the potential presence of unmeasured '
              'confounding (wording as quoted).',
         sota='Joint partial identification of multi-treatment, multi-outcome effects under factor confounding, with '
              'negative controls.',
         gap='Static: no time-varying treatment, no feedback; a preprint.',
         inputs='Bound the pumping effects jointly over several observation wells, under a shared drought factor.',
         dispersion='A well outside the capture zone of a piezometer is a physical null pair: a negative control whose '
                    'validity the dispersion decides.',
         bcs='Unknown boundary fluxes and recharge behave as a common factor across treatments and outcomes.',
         step='They accept the factor model of the Time Series Deconfounder and answer D\'Amour\'s non-identifiability '
              'with bounds. FSHEHTA-GO answers it with a second measurement: the static substitute is collinear with the '
              'treatments (condition number <<cond>>), the physics reading is not, and point identification returns.',
         steps=['substitute', 'check'], informs=dict(inputs=1, dispersion=1, bcs=2)),
    dict(id='H5', inst='Harvard', year=2024, short='Time order as a double negative control',
         title='Air pollution below US regulatory standards and cardiovascular diseases using a double negative control '
               'approach',
         authors='Yichen Wang, Mahdieh Danesh Yazdi, Yaguang Wei, Joel D. Schwartz',
         venue='Nature Communications 15, 8451 (2024)',
         links=[('doi:10.1038/s41467-024-52117-8', 'https://doi.org/10.1038/s41467-024-52117-8'),
                ('DOAJ record', 'https://doaj.org/article/04f124395c5e4e91805b251456e1a7f5')],
         evidence='A search summary lists Yichen Wang at the Harvard T.H. Chan School of Public Health (and Yale) and '
                  'Mahdieh Danesh Yazdi at Harvard Chan; Joel D. Schwartz is in its environmental epidemiology group.',
         does='**Result.** Preceding-year hospitalisations serve as a negative outcome control and subsequent-year exposure '
              'as a negative exposure control, their expected values as a proxy for the omitted confounders. In US '
              'Medicare beneficiaries aged 65 and over (2000–2016), PM2.5, NO2 and warm-season O3 were positively '
              'associated with hospitalisations for stroke, heart failure and atrial fibrillation even in areas below '
              'PM2.5 9 μg/m³, NO2 40 ppb and warm-season O3 45 ppb.',
         sota='A double negative control built from time order, in a national environmental panel.',
         gap='One treatment and a one-year lag; no multi-well or sequential strategies; no feedback.',
         inputs='Next-week pumping as a negative-control exposure and last-week chloride as a negative-control outcome, '
                'if the hidden demand persists over the lag (set by $\\tau$).',
         dispersion='Slow dispersive transport makes chloride strongly autocorrelated, so lagged chloride is itself '
                    'driven by past pumping.',
         bcs='Managers who cut pumping after a salinity rise make future pumping depend on the outcome — a violation to '
             'design around.',
         step='Time order makes their proxies; physics makes ours. The difference matters when the confounder is fast: '
              'with a dryness persistence of 0.5 the history-based substitute removes almost nothing (summed-effect '
              'bias <<tsd8_50>> against <<naive8_50>> unadjusted), the heads-based reading removes it all '
              '(<<phys8_50>>).',
         steps=['substitute'], informs=dict(inputs=1, dispersion=1, bcs=1)),
]

MIT = [
    dict(id='M1', inst='MIT', year=2021, short='Effects under history-dependent assignment',
         title='Learning Treatment Effects in Panels with General Intervention Patterns',
         authors='Vivek F. Farias, Andrew A. Li, Tianyi Peng',
         venue='Advances in Neural Information Processing Systems 34 (NeurIPS 2021), oral',
         links=[('NeurIPS proceedings', 'https://proceedings.neurips.cc/paper/2021/hash/'
                                        '7504adad8bb96320eb3afdd4df6e1f60-Abstract.html'),
                ('arXiv:2106.02780', 'https://arxiv.org/abs/2106.02780')],
         evidence='Tianyi Peng\'s CV gives an MIT PhD (Operations Research) advised by Vivek Farias; no result quoted '
                  'the MIT Sloan affiliation for this paper.',
         does='**Result.** The observed matrix is a low-rank baseline plus noise plus heterogeneous effects on the entries '
              'where a 0/1 treatment pattern is one; the pattern may depend on the history. A convex nuclear-norm '
              'penalised fit with a de-biasing step recovers the average effect at an optimal rate for general patterns, '
              'described as the first guarantees of their type in this setting. The exact rate was not read.',
         sota='Rate-optimal recovery of the average effect in panels with arbitrary intervention patterns.',
         gap='Binary treatment, an average effect only, no carryover.',
         inputs='The well × month baseline chloride, driven by the inputs and the rain, is plausibly low rank.',
         dispersion='Not covered.',
         bcs='Pumping decisions that react to past chloride are allowed by the history-dependent pattern.',
         step='A low-rank baseline absorbs the confounding only if the confounder is in the baseline. Our dryness also '
              'drives the treatment, week by week; FSHEHTA-GO reads it from the heads instead, and the summed effects '
              'come out unbiased (<<phys8>>) with a Monte Carlo spread of <<sd_phys8>>, against <<sd_tsd8>> with the '
              'history substitute.',
         steps=['outcome'], informs=dict(inputs=1, dispersion=0, bcs=1)),
    dict(id='M2', inst='MIT', year=2022, short='Debiased learning of dynamic effects',
         title='Automatic Debiased Machine Learning for Dynamic Treatment Effects and General Nested Functionals',
         authors='Victor Chernozhukov, Whitney Newey, Rahul Singh, Vasilis Syrgkanis',
         venue='arXiv preprint 2203.13887 (v5 June 2023); no journal version was found',
         links=[('arXiv:2203.13887', 'https://arxiv.org/abs/2203.13887')],
         evidence='The v2 PDF lists the first three authors at MIT and Vasilis Syrgkanis at Microsoft Research (search '
                  'summary).',
         does='**Result.** A dynamic treatment regime with discrete treatments is restated through a recursive Riesz '
              'representer of nested mean regressions; the representers are estimated by a sequence of loss '
              'minimisations whose minimisers are the multipliers of the de-biasing correction, so no auxiliary '
              'propensity model is needed; non-asymptotic rates hold for general machine learning. The assumptions are '
              'sequential conditional exogeneity, a surrogacy assumption for long-term effects and sequential '
              'positivity.',
         sota='Debiased machine-learning inference for dynamic regimes without hand-derived corrections.',
         gap='Discrete treatments; no hidden confounding given the history; a preprint.',
         inputs='Short-term heads or chloride as surrogates of the long-term salinized area.',
         dispersion='The surrogate horizon is set by the dispersive tail of the chloride response.',
         bcs='Needs the history to contain the confounders — exactly what the physics reading supplies.',
         step='It would replace the inverse-propensity weights of the Time Series Deconfounder, whose products explode '
              'over long horizons, but it inherits sequential exogeneity. Proposition D2 supplies it from physics: with '
              'the recharge reading in the history, the pumping is ignorable, and the physics check confirms it at its '
              'nominal size.',
         steps=['outcome'], informs=dict(inputs=1, dispersion=1, bcs=1)),
    dict(id='M3', inst='MIT', year=2024, short='Doubly robust inference with latent factors',
         title='Doubly Robust Inference in Causal Latent Factor Models',
         authors='Alberto Abadie, Anish Agarwal, Raaz Dwivedi, Abhin Shah',
         venue='Working paper, arXiv:2402.11652 (v3 October 2024; updated MIT version February 2026)',
         links=[('arXiv:2402.11652', 'https://arxiv.org/abs/2402.11652'),
                ('MIT Economics PDF (Feb 2026)', 'https://economics.mit.edu/sites/default/files/2026-02/Doubly%20Robust%20'
                                                 'Inference%20in%20Causal%20Latent%20Factor%20Models%20Feb%202026.pdf')],
         evidence='MIT Economics hosts the versions of 2024 and 2026; Abhin Shah\'s MIT thesis (DSpace 1721.1/158911) '
                  'describes the doubly robust estimator with black-box matrix completion.',
         does='**Result.** The average effect under unobserved confounding, with latent factors in both the outcomes and '
              'the assignment, is estimated by combining outcome imputation, inverse probability weighting and a new '
              'cross-fitting procedure for matrix completion; the error is asymptotically Gaussian at a parametric rate '
              'under provably valid matrix-completion error rates, irrespective of other properties of the completion '
              'algorithm. The exact rate conditions were not read.',
         sota='Doubly robust, parametric-rate inference for causal latent factor models.',
         gap='Static: no treatment–confounder feedback over time.',
         inputs='No need to estimate $T$, $S$ or $\\kappa$: their effect enters through the latent factors.',
         dispersion='Not covered.',
         bcs='A drought that drives pumping and recharge is covered if it acts through factors shared across wells and '
             'periods.',
         step='Double robustness protects against one wrong nuisance. FSHEHTA-GO has two substitutes that fail in '
              'different ways — the history one misses innovations, the physics one leaks a wrong drawdown — and the '
              'combination of both is unbiased whenever the physics is right (summed effects <<both8>>).',
         steps=['outcome', 'substitute'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='M4', inst='MIT', year=2026, short='Many treatments through a tensor factor model',
         title='Synthetic Interventions: Extending Synthetic Controls to Multiple Treatments',
         authors='Anish Agarwal, Devavrat Shah, Dennis Shen',
         venue='Operations Research 74(2), 840–859 (2026; online December 2025)',
         links=[('doi:10.1287/opre.2025.1590', 'https://doi.org/10.1287/opre.2025.1590'),
                ('arXiv:2006.07691', 'https://arxiv.org/abs/2006.07691')],
         evidence='The arXiv PDF lists Devavrat Shah at MIT EECS (Anish Agarwal at Columbia, Dennis Shen at USC). Earlier '
                  'versions had other authors and the title "Synthetic A/B Testing using Synthetic Interventions".',
         does='**Result.** Potential outcomes form a low-rank tensor over units, times and interventions; under linear '
              'span inclusion of the target unit\'s factor in the donors\' factors, all unit–intervention effects are '
              'recovered while each unit is seen under at most two interventions. One estimator is consistent and a '
              'bias-corrected one asymptotically normal; the estimator allows latent confounders that determine the '
              'assignment, and a subspace-inclusion test checks validity. Applications include simulations and '
              'California\'s Proposition 99.',
         sota='Counterfactuals under many treatments from panel data, with inference and a falsification test.',
         gap='One intervention per unit after the pre-period; no sequential regimes or carryover; discrete treatments.',
         inputs='Unit factors stand for well properties ($T$, $S$, distance to the coast, $\\tau$): their span is '
                'identified, not the parameters.',
         dispersion='Mixing-zone memory makes chloride depend on the pumping history, so an intervention must be a '
                    'regime, not a weekly rate.',
         bcs='Time factors shared by the wells carry the common forcings — rain, sea level, irrigation demand.',
         step='Their subspace-inclusion test and our physics check play the same role: falsify the assumption that makes '
              'the substitute valid. Ours is aimed at Assumption 3 and at the physics: it rejects a single-cause '
              'confounder at one well and a 30% drawdown error alike (power <<power>>).',
         steps=['check', 'substitute'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='M5', inst='MIT', year=2026, short='A categorical confounder from three proxies',
         title='Causal Inference with Categorical Unobserved Confounder via Mixture Learning',
         authors='Aytijhya Saha, Stephen Bates, Devavrat Shah',
         venue='arXiv preprint 2605.19006 (May 2026)',
         links=[('arXiv:2605.19006', 'https://arxiv.org/abs/2605.19006')],
         evidence='A search summary of the arXiv listing gives the authors at MIT EECS and LIDS. A preprint, six months '
                  'old.',
         does='**Result.** Causal effects with a categorical unobserved confounder are identified from a mixture-learning '
              'perspective when at least three proxies are conditionally independent given the confounder, without '
              'classifying the proxies by role (identifiability of the mixture after Allman et al. 2009); each unit\'s '
              'posterior over the latent class is recovered by tensor decomposition, then the effects, with '
              'non-asymptotic guarantees. The rank conditions were not read.',
         sota='Identification and estimation guarantees for a categorical confounder from role-free proxies.',
         gap='Independent units, no dynamics, a categorical confounder; unreviewed.',
         inputs='Proxies: a rain-based drought index, irrigated area from satellites, pump electricity.',
         dispersion='Not covered.',
         bcs='Dry, normal and wet regimes as a latent class acting on all wells and on the recharge; three wells whose '
             'pumping is independent given the regime are the three views.',
         step='Their three views are the multi-cause structure of the Time Series Deconfounder, made identifiable. The '
              'heads are a fourth, physical view, and the only one that sees a single-cause confounder near a logger: '
              'the well-1 check rejects it in <<rej1_single>> of the cases.',
         steps=['substitute', 'check'], informs=dict(inputs=1, dispersion=0, bcs=1)),
]

INST_ORDER = ('Oxford', 'Caltech', 'Harvard', 'MIT')


def all_cards():
    return OXFORD + CALTECH + HARVARD + MIT


CARDS = all_cards()


def SOTA_ROWS(s):
    """the rows of the state-of-the-art table; s holds the numbers of text_fshehta.py."""
    return [
        ['Substitutes for hidden confounders over time',
         'The Time Series Deconfounder (TSD); factor substitutes in outcomes (O3) and panels (O5, M1, M4); proxies '
         '(O2, M5); time-order negative controls (H5)',
         'Built from the past or from the treatments: misses fresh innovations, or is collinear with the treatments',
         'A substitute read from another measurement — the heads — through known physics (Proposition D2)',
         f'T29: summed-effect bias {s["naive8"]} unadjusted, {s["tsd8"]} TSD, {s["phys8"]} physics (8 wells)'],
        ['Many causes',
         'Multi-cause identification (TSD, M4, M5, C3); double asymptotics in units and times (O5)',
         'More causes are taken to help',
         'For substitutes built from the past, more wells make the summed bias worse (Proposition D1)',
         f'T29: best history substitute {s["ideal8"]} at 8 wells, {s["ideal64"]} at 64; limit {s["limit"]}'],
        ['Checking the assumptions',
         'Predictive checks (TSD); leave-outs (O1); subspace inclusion (M4); bounds (H4); parallel trends with '
         'sensitivity (H2)',
         'Blind to a common innovation; no check of the single-cause assumption',
         'A physics check of Assumption 3 and of the physics itself, calibrated by time shifts (Proposition D3)',
         f'T32: size {s["size"]}, power {s["power"]}; the TSD check p = {s["tsd_p"]} throughout'],
        ['Inference with hidden confounders',
         'Instruments over time (H1); double robustness (M3); debiased dynamic effects (M2); matching on histories (H3)',
         'Exclusion, homogeneity or no hidden confounding given the history',
         'A bias band for wrong physics, linear in the drawdown error; the head kernel identified (Proposition D4)',
         f'T31: {s["d4_10"]} of β₁ per 10% drawdown error; a 40% too short kernel {s["kern_fixed"]} → {s["kern_prof"]}'],
        ['Physical attribution',
         'Adjoint attribution (C4); lagged hidden states (C1); budget residuals (C5); natural experiments (O4)',
         'Model-dependent; no identification of the pumping effect',
         'Physics used only where it is known (drawdown), statistics where it is not (dryness, crop stress)',
         f'T30: local crop stress at well 1: β₁ bias {s["psi1_tsd"]} TSD, {s["psi1_phys"]} physics'],
    ]
