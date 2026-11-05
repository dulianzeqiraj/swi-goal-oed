"""The twenty paper cards of the eighth state-of-the-art review (five per institution, all 2022-2026), from the
verification notes of four literature searches (November 2026), the rows of its state-of-the-art table, and a one-line
novelty per card for the summary of novelty. Landing pages were reached through search results only, so every card is
partly verified. None of the twenty was a card of reviews I-VII or appears in the earlier reviews of the series
(checked with the repository-wide search).

Fields as in ../shkaku_go/cards_shkaku.py, plus 'novel'. <<key>> is a number filled in from res/kripa.json by
text_kripa.py."""
from cards_kripa_ox import OXFORD, OX_SOTA  # noqa: F401  (the Oxford cards, kept in their own file)

CALTECH = [
    dict(id='C1', inst='Caltech', year=2023, short='Unbiased effective coefficients from multiscale data',
         title='Drift Estimation of Multiscale Diffusions Based on Filtered Data',
         authors='Assyr Abdulle, Giacomo Garegnani, Grigorios A. Pavliotis, Andrew M. Stuart, Zanoni (given name not '
                 'seen)',
         venue='Foundations of Computational Mathematics 23, 33–84 (2023)',
         links=[('doi:10.1007/s10208-021-09541-9', 'https://doi.org/10.1007/s10208-021-09541-9'),
                ('CaltechAUTHORS', 'https://resolver.caltech.edu/CaltechAUTHORS:20201109-141017891'),
                ('arXiv:2009.13457', 'https://arxiv.org/abs/2009.13457')],
         evidence='CaltechAUTHORS record (Stuart, Computing and Mathematical Sciences); the per-author affiliations were '
                  'not seen. The DOI suggests online-first publication in 2021; the 2023 volume is cited.',
         does='**Result.** For overdamped Langevin dynamics with two scales and a homogenized single-scale surrogate, the '
              'maximum-likelihood estimator of the homogenized drift computed from the raw multiscale data is '
              'asymptotically biased, while the estimator computed from data smoothed by a linear time-invariant filter '
              'of the exponential family is asymptotically unbiased, in both the homogenized and the multiscale regime. '
              'Sharp estimates of the minimal filter width relative to the multiscale parameter are given, with an '
              'estimator of the effective diffusion coefficient and Bayesian uncertainty quantification (theorem numbers '
              'from a search summary; the statements were not read).',
         sota='Provably unbiased estimation of homogenized (effective) coefficients from multiscale data, without '
              'subsampling.',
         gap='Gradient-type diffusions with a periodic fast scale and continuous paths; no sparse data, no counterfactual '
             'change of forcing.',
         inputs='Fitting $T$, $S$, $\\kappa$ or $\\tau$ of a coarse aquifer model to head series with fast tidal or '
                'pumping cycles is biased; the series should be filtered first, with a width above the fast scale.',
         dispersion='An effective dispersion coefficient is a homogenized diffusion coefficient: estimated naively from '
                    'fine-scale chloride fluctuations it is biased, with a filtered estimator it is consistent. Dispersion '
                    'from data must be scale-aware.',
         bcs='The tide is the fast scale to filter out of the sea boundary.',
         step='In KRIPA-GO the width $w$ is such an effective coefficient, and it decides the salinity counterfactual: it '
              'carries <<share_wA>> of the posterior variance of the drought effect on the salinized area (T28). Their '
              'filtered estimator is the principled way to turn chloride series into the $w$ the counterfactual needs; the '
              'toe counterfactual, free of $w$ (Proposition L2), needs no such step.',
         novel='The effective dispersion coefficient as the quantity that decides a salinity counterfactual '
               '(<<share_wA>> of its variance), estimated with scale-aware filtering.',
         steps=['invert'], informs=dict(inputs=1, dispersion=2, bcs=1)),
    dict(id='C2', inst='Caltech', year=2024, short='A mixing closure learned online and tested under new forcing',
         title='Online Learning of Entrainment Closures in a Hybrid Machine Learning Parameterization',
         authors='Costa Christopoulos, Ignacio Lopez-Gomez, Tom Beucler, Yair Cohen, Charles Kawczynski, Oliver R. A. '
                 'Dunbar, Tapio Schneider',
         venue='Journal of Advances in Modeling Earth Systems 16(11), e2024MS004485 (2024)',
         links=[('doi:10.1029/2024MS004485', 'https://doi.org/10.1029/2024MS004485'),
                ('CaltechAUTHORS', 'https://authors.library.caltech.edu/records/2x0kp-pkz30')],
         evidence='CaltechAUTHORS record; PDF hosted by CliMA at Caltech; the work is part of the first author\'s 2025 '
                  'Caltech PhD dissertation.',
         does='**Result.** The lateral entrainment and detrainment (mixing) closure of an eddy-diffusivity/mass-flux scheme '
              'is made data-driven and trained online, through the single-column solver, against large-eddy simulations '
              'forced by GCM-simulated Pacific conditions. Ensemble Kalman inversion calibrates the physical and the '
              'data-driven mixing parameters jointly, without derivatives, and the calibrated scheme outperforms existing '
              'schemes, especially in the tropics and subtropics. One summary reports that it stays accurate under 4 K '
              'warmer sea-surface temperatures; this was not reconfirmed, and no numbers were seen.',
         sota='Online, derivative-free learning of a mixing closure inside the solver, tested under a changed forcing.',
         gap='No coverage guarantee; one distribution shift; abundant simulated targets.',
         inputs='$T$, $S$ and $\\kappa$ calibrated jointly with a learned closure, without derivatives, against output '
                'statistics only.',
         dispersion='A dispersion law $D(v,\\nabla c)$ learned as a closure inside the variable-density solver from '
                    'salinity outputs, then tested under a drier forcing.',
         bcs='The large-scale forcing varies across training cases; the warmer climate is the template for "the same '
             'closure, a counterfactual forcing".',
         step='Proposition L3 says what their out-of-distribution test cannot: whether the closure itself changes under '
              'the new forcing is a cross-world question for any single factual climate. In KRIPA-GO, letting the '
              'transition zone widen as $c^{-1/2}$ under a 40% drier regime moves the salinized-area effect from '
              '<<dA_med>> to <<beta05>> km² (T28); a closure trained across forcings is how that law could be learned '
              'instead of assumed.',
         novel='A closure learned across forcings as the way to learn the cross-world dispersion law, which moves the '
               'drought effect from <<dA_med>> to <<beta05>> km².',
         steps=['emulate', 'invert'], informs=dict(inputs=1, dispersion=2, bcs=1)),
    dict(id='C3', inst='Caltech', year=2026, short='Regime-invariant mixing coefficients with uncertainty',
         title='Online learning of eddy-viscosity and backscattering closures for geophysical turbulence using ensemble '
               'Kalman inversion',
         authors='Yifei Guan, Pedram Hassanzadeh, Tapio Schneider, Oliver Dunbar, Daniel Zhengyu Huang, Jinlong Wu, '
                 'Ignacio Lopez-Gomez',
         venue='Physical Review Research 8, 023215 (2026)',
         links=[('doi:10.1103/mnbm-3g56', 'https://doi.org/10.1103/mnbm-3g56'),
                ('CaltechAUTHORS', 'https://authors.library.caltech.edu/records/avera-s5s35'),
                ('arXiv:2409.04985', 'https://arxiv.org/abs/2409.04985')],
         evidence='CaltechAUTHORS record ("Published May 27, 2026"), listed in the library feeds of Schneider and Dunbar; '
                  'the per-author affiliations were not seen.',
         does='**Result.** Ensemble Kalman inversion tunes one parameter each of the Smagorinsky and Leith eddy-viscosity '
              'closures and two of the Jansen–Held backscatter closure, so that the energy spectrum of large-eddy '
              'simulations matches direct numerical simulation in eight cases of two-dimensional geophysical turbulence. '
              'The optimized parameters are constant across broad flow regimes, the backscatter closure performs best a '
              'priori and a posteriori, only spectra are needed, and calibrate–emulate–sample quantifies the parametric '
              'uncertainty.',
         sota='Spectrum-matched closure coefficients that are regime-invariant, with Bayesian uncertainty.',
         gap='Two-dimensional turbulence, not porous media; eight cases; Bayesian, not distribution-free.',
         inputs='With scarce data, calibrate on statistics, such as variances or spectra of the heads against the rain.',
         dispersion='A one- or two-parameter mixing closure can be regime-invariant, which supports carrying a '
                    'dispersivity unchanged into a drier regime; the backscatter term warns that a purely Fickian closure '
                    'can be insufficient.',
         bcs='None.',
         step='Regime invariance is the shared-width assumption $w\'=w$ of KRIPA-GO. Their test is a way to check it '
              'across regimes; KRIPA-GO prices its failure: under $w\'=w\\,c^{-1/4}$ the salinized-area effect rises '
              'from <<dA_med>> to <<beta025>> km², while the toe effect does not change (T28).',
         novel='Regime invariance of a mixing coefficient as a testable form of the shared-dispersion assumption, whose '
               'failure KRIPA-GO prices.',
         steps=['invert', 'check'], informs=dict(inputs=1, dispersion=2, bcs=0)),
    dict(id='C4', inst='Caltech', year=2025, short='Daily satellite view of the drought cascade',
         title='Revisiting Sub-Surface Drought Cascades With Daily Satellite Observations of Soil Moisture and '
               'Terrestrial Water Storage',
         authors='Daniel Blank, Annette Eicker, John T. Reager, Andreas Güntner',
         venue='Water Resources Research 61(8), e2024WR039321 (2025)',
         links=[('doi:10.1029/2024WR039321', 'https://doi.org/10.1029/2024WR039321'),
                ('HCU research portal', 'https://forschungsportal.hcu-hamburg.de/en/publications/revisiting-sub-surface-'
                                        'drought-cascades-with-daily-satellite-obse/')],
         evidence='Reager is described as JPL\'s in the search summary of his 2025 GRACE-FO Science Team presentation; '
                  'the JPL affiliation was not confirmed from the paper\'s own author block.',
         does='**Result.** Daily GRACE and GRACE-FO total water storage, combined with SMOS, SMAP and ESA CCI surface and '
              'root-zone soil moisture over 2015–2022, are analysed through the rates of change of de-seasonalized '
              'anomalies. Surface soil moisture fluctuates fast and recovers quickly, the root zone more slowly and the '
              'whole column slowest, so drought signals are damped and delayed as they propagate downward. Recovery '
              'times of days per layer appear in presentation slides and were not checked against the paper.',
         sota='The first global, daily, satellite-only quantification of the drought cascade from the surface to deep '
              'storage.',
         gap='About 300 km resolution; groundwater not separated; descriptive, without causal analysis or guarantees.',
         inputs='Layer-by-layer recovery times and lags as priors or bounds for the vadose delay and the recharge '
                'coefficient.',
         dispersion='None.',
         bcs='The shape of the recharge response to a rain deficit (damping plus delay): what is needed to build "the '
             'recharge had the rain been a drought" from the rain series alone.',
         step='The steady KRIPA-GO counterfactual is the end point of their cascade: a lasting 40% recharge deficit '
              'raises the salinized area from <<A_fact>> to <<A_cf>> km² (T26). Their damping and delay give the transient '
              'path towards that end point, and the dose-response of T26 gives its size for every deficit.',
         novel='Satellite drought cascades as the transient path to the steady salinity counterfactual (<<A_fact>> → '
               '<<A_cf>> km²).',
         steps=['prior'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='C5', inst='Caltech', year=2022, short='Local plus non-local stochastic transport',
         title='Augmenting the Double-Gaussian Representation of Atmospheric Turbulence and Convection via a Coupled '
               'Stochastic Multi-Plume Mass-Flux Scheme',
         authors='Mikael K. Witte, Adam Herrington, Joao Teixeira, Marcin J. Kurowski, Maria J. Chinita, Rachel L. '
                 'Storer, Kay Suselj, Georgios Matheou, Julio Bacmeister',
         venue='Monthly Weather Review 150(9), 2339–2355 (2022); DOI not seen',
         links=[('UCAR record', 'https://impacts.ucar.edu/en/publications/augmenting-the-double-gaussian-representation-'
                                'of-atmospheric-turb/'),
                ('JPL CV citing it', 'https://science.jpl.nasa.gov/documents/798/CV_Kurowski_2022.pdf')],
         evidence='Teixeira, Kurowski and Suselj are listed at "JPL, California Institute of Technology" on 2023 CESM '
                  'workshop slides, and Kurowski\'s JPL CV cites the paper; the paper\'s header was not seen.',
         does='**Result.** Multiple stochastic mass-flux plumes, with stochastic lateral entrainment, are coupled at '
              'little extra cost to the double-Gaussian probability-density closure of subgrid turbulence, because the '
              'double-Gaussian closure alone cannot reproduce key features of shallow cumulus convection; transport is '
              'split into a local eddy-diffusivity part and a non-local, stochastic plume part.',
         sota='A coupled stochastic multi-plume and probability-density closure of turbulent transport.',
         gap='Atmospheric; no data-driven calibration, uncertainty quantification or theory.',
         inputs='None.',
         dispersion='A single local dispersion coefficient can miss non-local, stochastic transport: preferential '
                    'pathways that shift or widen the transition zone could be represented by a stochastic mass-flux-like '
                    'term.',
         bcs='None.',
         step='KRIPA-GO uses one local width $w$ for the whole sector and shows how much rides on it: the drought effect '
              'on the salinized area is <<wlowA>> km² for the narrowest tenth of $w$ and <<whighA>> km² for the widest '
              '(T28). A non-local stochastic transport term would turn this single number into a spatial field, the '
              'limitation named in Section 6.',
         novel='Non-local stochastic transport as the next model of the transition zone, beyond a single width that '
               'already spans <<wlowA>>–<<whighA>> km² of drought effect.',
         steps=['emulate'], informs=dict(inputs=0, dispersion=2, bcs=0)),
]

BERKELEY = [
    dict(id='B1', inst='Berkeley', year=2025, short='Matrix diffusion and the storage inferred from tracers',
         title='Matrix Diffusion Controls Mountain Hillslope Groundwater Ages and Inferred Storage Dynamics',
         authors='N. E. Thiros, E. R. Woodburn, W. P. Gardner, J. P. Dennedy-Frank, K. H. Williams',
         venue='Groundwater 63(3), 306–318 (2025)',
         links=[('doi:10.1111/gwat.13475', 'https://doi.org/10.1111/gwat.13475'),
                ('PMC12049175', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12049175/'),
                ('LBNL Watershed Function', 'https://watershed.lbl.gov/publications/matrix-diffusion-controls-mountain-'
                                            'hillslope-groundwater-ages-and-inferred-storage-dynamics/')],
         evidence='Listed with a research highlight on the Lawrence Berkeley National Laboratory Watershed Function site; '
                  'DOE OSTI record 2543161. The per-author affiliations were not seen.',
         does='**Result.** With an integrated hydrologic model and particle tracking of a montane hillslope (East River, '
              'Colorado), a Monte Carlo analysis over uncertain matrix and fracture parameters shows that matrix '
              'diffusion is necessary to predict tritium and helium-4 at two wells jointly. The best scenario is a '
              'dynamic bedrock reservoir that loses considerable storage in low-snow periods; high terrigenic helium, '
              'read as old ages, can largely be a product of matrix diffusion, and ignoring it when assimilating tracers '
              'into advection-dominated models can overestimate the drainable storage. No numbers were seen.',
         sota='The first demonstration that diffusion controls the storage inferred from multiple tracers in a hillslope.',
         gap='Fractured bedrock, not coastal; no variable density; a Monte Carlo fit without a guarantee.',
         inputs='A storage calibrated on a handful of tracer or chloride facts with a single-porosity advective model is '
                'biased high, which makes the drought response look damped: a bias towards optimism.',
         dispersion='Matrix diffusion (mass transfer) and mechanical dispersion leave similar marks on ages and '
                    'concentrations; one effective dispersion parameter absorbs both, and a few facts cannot separate '
                    'them. Slow exchange adds memory, so a transition zone does not simply rescale under drought.',
         bcs='The dry-period storage loss comes from the recharge in time; there is no sea boundary in the paper.',
         step='Their result is a warning for the chloride facts of KRIPA-GO: a few concentrations interpreted with one '
              'effective width $w$ absorb any slow exchange. The facts narrow the counterfactual area effect to '
              '<<rchl>> of its prior width (T28); a mass-transfer process would change what that width means, and '
              'with it the cross-world law of Proposition L3.',
         novel='Mass transfer and dispersion leave the same mark on a few facts: the chloride facts that narrow the '
               'counterfactual to <<rchl>> of its prior width must be read with that ambiguity.',
         steps=['invert', 'check'], informs=dict(inputs=2, dispersion=2, bcs=1)),
    dict(id='B2', inst='Berkeley', year=2022, short='Recharge scenarios for a reactive plume',
         title='Reactive transport modeling for supporting climate resilience at groundwater contamination sites',
         authors='Zexuan Xu, Rebecca Serata, Haruko Wainwright, Miles Denham, Sergi Molins, Hansell Gonzalez-Raymat, '
                 'Konstantin Lipnikov, J. David Moulton, Carol Eddy-Dilek',
         venue='Hydrology and Earth System Sciences 26(3), 755–773 (2022)',
         links=[('doi:10.5194/hess-26-755-2022', 'https://doi.org/10.5194/hess-26-755-2022'),
                ('eScholarship', 'https://escholarship.org/uc/item/9g57r0p1')],
         evidence='The eScholarship record is filed under Lawrence Berkeley National Laboratory (search summary); Xu '
                  'appears with an LBNL affiliation in a related 2022 preprint. The per-author affiliations were not seen.',
         does='**Result.** Two-dimensional reactive transport of uranium, tritium and nitrate at the Savannah River Site '
              'F-Area (Amanzi), under perturbed infiltration, cap failure and downscaled CMIP5 projections to 2100, shows '
              'that the competing effects of dilution and remobilization change the pH and hence the sorption of uranium. '
              'For cap failure at +10% to +50% recharge, +50% gives the earliest peak and +20% the highest; the −10% and '
              '−20% recharge scenarios diverge strongly around 2040 and converge by 2100.',
         sota='The reference DOE/LBNL workflow for climate-scenario reactive transport at a contaminated site.',
         gap='Deterministic scenarios without uncertainty bands; no variable density and no salinity.',
         inputs='The map from the recharge coefficient to a reactive concentration is not monotone, so a guaranteed '
                'recharge band cannot simply be propagated to a guaranteed concentration band.',
         dispersion='Dilution (mixing) competes with chemistry; no dispersivity sensitivity was seen.',
         bcs='Precipitation → infiltration → recharge-in-time scenarios; the counterfactual gap depends on the horizon, '
             'so bands should be indexed by time.',
         step='KRIPA-GO\'s salt response is monotone (Proposition L2: a drier regime never lowers the chloride of any '
              'screen), which is what makes the salinity counterfactual sign-identified for every value of the unknowns. '
              'Their non-monotone uranium response shows where that property ends: salinity is conservative, reactive '
              'ions are not.',
         novel='The monotonicity that identifies a salinity counterfactual (Proposition L2) holds for a conservative '
               'tracer and fails for reactive ones, as their uranium response shows.',
         steps=['emulate', 'design'], informs=dict(inputs=1, dispersion=1, bcs=2)),
    dict(id='B3', inst='Berkeley', year=2024, short='Surrogate uncertainty fails out of domain',
         title='Using Uncertainty Quantification to Characterize and Improve Out-of-Domain Learning for PDEs',
         authors='S. Chandra Mouli, Maddix, Alizadeh, Gupta, Stuart, Mahoney, Wang (other given names not seen)',
         venue='Proceedings of the 41st International Conference on Machine Learning (ICML 2024), PMLR 235, 36372–36418',
         links=[('PMLR 235', 'https://proceedings.mlr.press/v235/mouli24a.html'),
                ('arXiv:2403.10642', 'https://arxiv.org/abs/2403.10642')],
         evidence='Mahoney is in Statistics at UC Berkeley, at ICSI and at Lawrence Berkeley National Laboratory (his '
                  'Berkeley page); the paper\'s own header was not seen.',
         does='**Result (abstract wording).** Several uncertainty-quantification methods for neural operators fail for '
              'test inputs that are even moderately out of domain, even when the model approximates the solution well '
              'in domain. A cheap diverse ensemble (DiverseNO) and an update that enforces conservation laws '
              '(Operator-ProbConserv) improve out-of-domain accuracy and calibration. The test families include the heat '
              'equation with the diffusion constant trained on [1, 5] and tested on [6, 7], the porous-medium equation, '
              'the Stefan problem and linear advection.',
         sota='The reference study of out-of-domain uncertainty of neural operators when a PDE coefficient shifts.',
         gap='No distribution-free guarantee; one- and two-dimensional benchmarks; no variable-density coupling.',
         inputs='None directly.',
         dispersion='A drier regime lowers velocities and hence mechanical dispersion, which can push a surrogate outside '
                    'its trained coefficient range, where its own error bars are unreliable.',
         bcs='None on the rain; the Stefan problem is a moving-interface analogue of the toe.',
         step='State abduction (Proposition L1) avoids the out-of-domain problem for the interface: the drier aquifer is '
              'computed exactly as $c\\phi$, not extrapolated by a surrogate (error <<zeta_h>> m from the heads alone, '
              'T25). Where a surrogate is unavoidable — a transient section model — their result says its error bars '
              'must be recalibrated, for example on simulated twins (Proposition L4).',
         novel='Exact state abduction removes the out-of-domain error of a surrogate for the interface counterfactual; '
               'where a surrogate is unavoidable, twins recalibrate it.',
         steps=['emulate', 'guarantee'], informs=dict(inputs=0, dispersion=2, bcs=0)),
    dict(id='B4', inst='Berkeley', year=2023, short='Same counterfactual, different randomness',
         title='Same Root Different Leaves: Time Series and Cross-Sectional Methods in Panel Data',
         authors='Dennis Shen, Peng Ding, Jasjeet Sekhon, Bin Yu',
         venue='Econometrica 91(6), 2125–2154 (2023)',
         links=[('doi:10.3982/ECTA21248', 'https://doi.org/10.3982/ECTA21248'),
                ('arXiv:2207.14481', 'https://arxiv.org/abs/2207.14481')],
         evidence='Yu at the Departments of Statistics and EECS, UC Berkeley (journal listing); Shen a postdoctoral '
                  'fellow at the Simons Institute, UC Berkeley, 2021–2023, hosted by Ding, Sekhon and Yu (his CV).',
         does='**Result (quoted).** Without any assumptions, horizontal regression (unconfoundedness, using time-series '
              'patterns) and vertical regression (synthetic controls, using cross-sectional patterns) yield algebraically '
              'equivalent point estimates for several standard estimators; but the source of randomness assumed by each '
              'leads to a distinct estimand and quantification of uncertainty even for the same point estimate, and a '
              'confidence interval built for one estimand may have incorrect coverage for another.',
         sota='The equivalence theory of synthetic-control and unconfoundedness estimators for panel counterfactuals.',
         gap='Linear estimators; no spatial dependence or nonlinear (salinity) outcomes.',
         inputs='None directly.',
         dispersion='None.',
         bcs='Two ways to build the drought counterfactual of a well: its own rain-driven history, or other wells in the '
             'same year. The point estimate can coincide while the band does not.',
         step='KRIPA-GO\'s guarantee states its source of randomness: data sets simulated from the prior ensemble, so '
              'the coverage <<cov_cp>> (T27) is over aquifers of the prior, not over years or wells. A field guarantee '
              'over wells would be a different estimand with a different band — their theorem in the salinity setting.',
         novel='A salinity counterfactual band must state its source of randomness (here aquifers of the prior); over '
               'wells or years it is a different estimand.',
         steps=['guarantee', 'check'], informs=dict(inputs=0, dispersion=0, bcs=1)),
    dict(id='B5', inst='Berkeley', year=2026, short='Warming makes the groundwater older',
         title='Warming and snow loss increase reliance on old groundwater in a Colorado River headwater',
         authors='Erica R. Siirila-Woodburn, Nicholas Thiros, Michelle Newcomer and colleagues (full author list not '
                 'confirmed)',
         venue='Nature Geoscience 19(5), 549–555 (2026)',
         links=[('doi:10.1038/s41561-026-01945-y', 'https://doi.org/10.1038/s41561-026-01945-y'),
                ('LBNL highlight', 'https://watershed.lbl.gov/highlights/warming-and-snow-loss-increase-reliance-on-old-'
                                   'groundwater-in-a-colorado-river-headwater/')],
         evidence='Berkeley Lab Watershed Function highlight; OSTI record whose PDF is headed "UC Berkeley Previously '
                  'Published Works". The per-author affiliations were not seen.',
         does='**Result (quoted).** As streamflow declines with warming, the age of the groundwater supporting it gets '
              'older, in part because intermediate-aged (1–3 year) groundwater declines twice as fast; old groundwater '
              'may be buffering the streamflow response, especially in low-snow years. Integrated hydrologic modelling '
              'with particle tracking over water years 2015–2021. A Berkeley Lab summary gives 15% more reliance on old '
              'groundwater per degree of warming; this number was not seen in the paper.',
         sota='A 2026 model-based attribution of warming effects on the age of the groundwater that feeds streams.',
         gap='A mountain, snow-dominated setting; no salinity; no uncertainty bands seen.',
         inputs='Transit-time and vadose-delay distributions are not invariant under a climate intervention, so a delay '
                'calibrated in wet years mis-predicts a drought.',
         dispersion='None seen (ages from advective particle tracking).',
         bcs='Perturbing the meteorological forcing is the counterfactual design; at a coast, drought shifts reliance to '
             'older, possibly more saline, water.',
         step='Their counterfactual climate is the transient analogue of the steady recharge counterfactual of KRIPA-GO. '
              'At the coast the old, slow water a drought leaves behind is the advancing wedge: a 40% drier regime would '
              'extend the toe over <<dT>> (T26), a counterfactual free of the dispersion (Proposition L2).',
         novel='Drought shifts reliance to old water; at the coast that is the advancing wedge, whose counterfactual toe '
               '(<<dT>>) is free of the dispersion.',
         steps=['prior', 'emulate'], informs=dict(inputs=2, dispersion=0, bcs=2)),
]

MIT = [
    dict(id='M1', inst='MIT', year=2025, short='A state-dependent, calibrated mixing coefficient',
         title='Formulation and calibration of CATKE, a one-equation parameterization for microscale ocean mixing',
         authors='Wagner, Hillier, Constantinou, Silvestri, Souza, Burns and colleagues (given names and the full list '
                 'not seen)',
         venue='Journal of Advances in Modeling Earth Systems 17, e2024MS004522 (2025)',
         links=[('doi:10.1029/2024MS004522', 'https://doi.org/10.1029/2024MS004522'),
                ('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/163179'),
                ('arXiv:2306.13204', 'https://arxiv.org/abs/2306.13204')],
         evidence='Deposited in DSpace@MIT and listed in the MIT EAPS publication database of John Marshall; the '
                  'per-author affiliations were not seen.',
         does='**Result.** Turbulent kinetic energy is a prognostic variable and a diagnostic mixing length carries a '
              'dynamic convective-adjustment component, so the scheme estimates both the depth of convective plumes and '
              'the time scale of convective mixing, which static convective-adjustment schemes cannot. The free '
              'parameters are fitted by ensemble Kalman inversion to minimise the error between 21 large-eddy simulations '
              'and the single-column predictions at three vertical resolutions; the scheme predicts idealized and '
              'realistic simulations accurately compared with parameterizations common in climate models.',
         sota='A calibrated, regime-aware mixing closure with validation on held-out scenarios.',
         gap='Ocean turbulence, not Darcy flow; ensemble or point estimates, no coverage guarantee.',
         inputs='A template for calibrating a few closure parameters by ensemble Kalman inversion against a refined '
                'variable-density simulator run over many forcing scenarios.',
         dispersion='Write the dispersion coefficient as a closure — a velocity scale times a mixing length — that depends '
                    'on the regime, including density-driven convection; calibrate on some scenarios, validate on others.',
         bcs='None directly; the calibration library must contain the counterfactual forcing regime.',
         step='CATKE\'s mixing coefficient changes with the flow state; in the aquifer the transition-zone width would '
              'change with the flow when the recharge drops — the cross-world dispersion of Proposition L3. KRIPA-GO '
              'prices its range: from <<dA_med>> to <<beta05>> km² of drought effect on the salinized area (T28). A '
              'state-dependent closure calibrated across forcings is the way to narrow that range.',
         novel='A flow-state-dependent mixing coefficient as the physical form of the cross-world dispersion law, which '
               'moves the drought effect up to <<beta05>> km².',
         steps=['emulate', 'invert'], informs=dict(inputs=1, dispersion=2, bcs=0)),
    dict(id='M2', inst='MIT', year=2024, short='Counterfactual dose curves with uniform rates',
         title='Kernel methods for causal functions: dose, heterogeneous and incremental response curves',
         authors='Rahul Singh, Liyuan Xu, Arthur Gretton',
         venue='Biometrika 111(2), 497–516 (2024)',
         links=[('doi:10.1093/biomet/asad042', 'https://doi.org/10.1093/biomet/asad042'),
                ('arXiv:2010.04855', 'https://arxiv.org/abs/2010.04855')],
         evidence='A search summary lists "Rahul Singh (MIT Economics)"; the printed byline was not seen, and the '
                  'affiliation at the time of the 2024 publication is not confirmed.',
         does='**Result (quoted).** Kernel ridge regression estimators of dose, heterogeneous and incremental response '
              'curves have closed-form solutions and uniform consistency with finite-sample rates; the rates depend on '
              'the smoothness of the causal estimand and the spectral decay of the covariance operator, not on the '
              'dimension of the data. The identification assumptions (selection on observables) were not re-read.',
         sota='Uniform finite-sample rates for nonparametric counterfactual dose curves.',
         gap='No unmeasured confounding assumed; independent data; no dynamics or delays.',
         inputs='The incremental response is the elasticity of recharge or heads to the rain, a handle on the recharge '
                'coefficient.',
         dispersion='None.',
         bcs='The rain amount as the dose and the recharge as the outcome: the curve at a drought dose is the '
             'counterfactual recharge boundary, and uniform rates support a band over every drought severity at once.',
         step='The KRIPA-GO dose-response is the aquifer\'s counterfactual dose curve over the recharge factor $c$: half '
              'the recharge adds <<dose05>> km² of salinized area, 50% more removes <<dose15>> km² (T26). Their uniform '
              'rates are the statistical counterpart for a curve learned from data rather than computed from a model.',
         novel='The recharge factor as a dose: a counterfactual dose curve of the salinized area, from +<<dose05>> km² '
               'at half the recharge to −<<dose15>> km² at 1.5 times.',
         steps=['emulate', 'guarantee'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='M3', inst='MIT', year=2025, short='Amortized conditional transport for inference',
         title='Efficient neural network approaches for conditional optimal transport with applications in Bayesian '
               'inference',
         authors='Zheyu Oliver Wang, Ricardo Baptista, Youssef Marzouk, Lars Ruthotto, Deepanshu Verma',
         venue='SIAM Journal on Scientific Computing 47(4), C979–C1005 (2025)',
         links=[('arXiv:2310.16975', 'https://arxiv.org/abs/2310.16975'),
                ('NSF PAR', 'https://par.nsf.gov/biblio/10638341')],
         evidence='Marzouk is at MIT (MIT addresses in his contemporaneous papers); the byline of this paper and its DOI '
                  'were not seen.',
         does='**Result.** Two methods for conditional optimal transport: PCP-Map writes the conditional map as the '
              'gradient of a partially input-convex neural network, with a faster implementation; COT-Flow uses a '
              'regularized neural-ODE flow, slower to train but faster to sample. Both perform sampling and conditional '
              'density estimation for simulation-based Bayesian inverse problems and are benchmarked there.',
         sota='Efficient, structured neural conditional optimal transport for amortized simulation-based inference.',
         gap='No coverage or error guarantee.',
         inputs='An amortized joint posterior of $T$, $S$, $\\kappa$ and $\\tau$ for every realization of the data.',
         dispersion='Dispersivities and the transition-zone width can be added to the parameter vector at no extra cost '
                    'per data set.',
         bcs='Conditioning on the rain gives posteriors of the boundary conditions; on a hypothetical drought rain, '
             'counterfactual posteriors.',
         step='KRIPA-GO weights a 20 000-draw ensemble (effective sample size about 3250 with the real facts); their '
              'amortized maps are the scalable replacement when facts multiply. Proposition L4 then supplies the '
              'missing coverage layer, calibrated on simulated data sets (<<cov_cp>>, T27).',
         novel='Amortized conditional transport for the counterfactual posterior, with the coverage layer of '
               'Proposition L4 on top.',
         steps=['invert', 'guarantee'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='M4', inst='MIT', year=2024, short='Rates for flow-based generators',
         title='Distribution learning via neural differential equations: a nonparametric statistical perspective',
         authors='Youssef Marzouk, Zhi (Robert) Ren, Sven Wang, Jakob Zech',
         venue='Journal of Machine Learning Research 25(232), 1–61 (2024)',
         links=[('JMLR 25(232)', 'https://jmlr.org/papers/v25/23-1280.html'),
                ('arXiv:2309.01043', 'https://arxiv.org/abs/2309.01043')],
         evidence='MIT addresses for Marzouk, Ren and Wang in the arXiv version (search summary); Zech at Heidelberg.',
         does='**Result (closely paraphrased).** The first general nonparametric convergence analysis of ODE-based '
              'distribution learning trained by maximum likelihood: a convergence theorem for any class of velocity fields '
              'that satisfies simple boundary constraints, with the complexity measured by the $C^1$ metric entropy of '
              'the class; for smooth target densities it gives nearly minimax-optimal rates for $C^k$ and for '
              'neural-network velocity fields.',
         sota='The first nonparametric rate theory for neural-ODE density learning.',
         gap='Unconditional densities only; smoothness assumptions.',
         inputs='Rates for learning the prior or the posterior of the parameters with flows.',
         dispersion='None directly.',
         bcs='A guarantee for a learned generator of rain or recharge regimes used to draw drought scenarios.',
         step='A learned generator of recharge regimes would feed the KRIPA-GO dose-response with realistic drier regimes '
              'instead of one factor $c$; their rates say how many simulations it needs, and the linearity of the '
              'potential in the recharge (Proposition L1) makes each generated regime a linear combination of a few '
              'precomputed solves.',
         novel='Rates for learned regime generators; with the potential linear in the recharge (Proposition L1), each '
               'generated regime costs a linear combination of precomputed solves.',
         steps=['prior', 'emulate'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='M5', inst='MIT', year=2024, short='Certified principal features',
         title='Principal feature detection via ϕ-Sobolev inequalities',
         authors='Matthew T. C. Li, Youssef Marzouk, Olivier Zahm',
         venue='Bernoulli (2024), doi:10.3150/23-BEJ1702 (volume and pages not seen)',
         links=[('doi:10.3150/23-BEJ1702', 'https://doi.org/10.3150/23-BEJ1702'),
                ('arXiv:2305.06172', 'https://arxiv.org/abs/2305.06172')],
         evidence='Marzouk is at MIT; the affiliation of the first author was not seen.',
         does='**Result.** A high-dimensional target is approximated as a low-dimensional update of a reference measure, a '
              'feature map composed with a profile function; error bounds come from ϕ-Sobolev inequalities, which '
              'interpolate between the log-Sobolev and Poincaré inequalities, and the same features certify the error for '
              'all Amari α-divergences with α in (0, 1]. Linear features are eigenvectors of a matrix of log-density '
              'gradients; no normalizing constants are needed.',
         sota='Dimension reduction certified across a whole family of divergences.',
         gap='A close relative of dimension-reduction results used in review VI; linear features only.',
         inputs='Shows which combinations of $T$, $S$, $\\kappa$ and $\\tau$ the data inform.',
         dispersion='Tests whether the dispersivity and the transition-zone width lie in the informed subspace or stay '
                    'prior-driven.',
         bcs='The same test for the boundary and initial parameters.',
         step='The variance shares of T28 are a crude version of their certified features: for the salinized-area effect '
              'one direction, the dispersion width, carries <<share_wA>> of the posterior variance; for the toe, the '
              'thinning length carries <<share_LB>>. Their certificates would bound the error of a counterfactual '
              'computed in that reduced space.',
         novel='The dispersion width as the principal feature of the salinity counterfactual (<<share_wA>> of its '
               'variance), with certified error for a reduced counterfactual.',
         steps=['invert', 'design'], informs=dict(inputs=2, dispersion=2, bcs=1)),
]

INST_ORDER = ('Oxford', 'Caltech', 'Berkeley', 'MIT')


def all_cards():
    return OXFORD + CALTECH + BERKELEY + MIT


CARDS = all_cards()


def SOTA_ROWS(AJ, f, s):
    """the rows of the state-of-the-art table; f and s hold the numbers of text_kripa.py."""
    return [
        ['Counterfactuals of salinity',
         'Climate-scenario reactive transport (B2); warming and groundwater age (B5); drought cascades (C4); '
         + OX_SOTA['cf'],
         'Scenarios without coverage; the unknowns that matter for the salt not identified',
         'Guaranteed counterfactual salinity of a real aquifer, from the factual state (Propositions L1, L4)',
         f'T26: salinized area {s["A_fact"]} → {s["A_cf"]} km² under 40% less recharge; conformal effect band '
         f'{f["A_cp_lo"]:.0f}–{f["A_cp_hi"]:.0f} km²'],
        ['Dispersion and mixing coefficients',
         'Unbiased effective coefficients from multiscale data (C1); learned and regime-invariant mixing closures (C2, C3, '
         'M1); non-local stochastic transport (C5); matrix diffusion (B1); ' + OX_SOTA['disp'],
         'Coefficients estimated or learned, but never asked how they change a scenario\'s answer',
         'The share of a counterfactual that is the dispersion, and which data reduce it',
         f'T28: $w$ carries {s["share_wA"]} (area) and {s["share_wF"]} (fraction) of the effect\'s variance; heads '
         f'{s["rheads"]}, chloride {s["rchl"]} of the prior width'],
        ['Cross-world assumptions',
         'Out-of-distribution closures (C2); regime invariance (C3); state-dependent mixing (M1)',
         'Whether a coefficient changes under the counterfactual forcing is untestable from one climate',
         'The cross-world dispersion law made explicit and priced (Proposition L3)',
         f'T28: area effect {s["dA_med"]} → {s["beta025"]} → {s["beta05"]} km² for β = 0, 1/4, 1/2'],
        ['Calibrated inference and surrogates',
         'Amortized conditional transport (M3); rates for flow generators (M4); certified features (M5); out-of-domain '
         'surrogate uncertainty (B3); ' + OX_SOTA['sbi'],
         'No coverage for counterfactual quantities; surrogates extrapolate under scenarios',
         'Exact state abduction instead of extrapolation; conformal bands on simulated twins',
         f'T25: twin interface from the heads to {s["zeta_h"]} m; T27: coverage {s["cov_cp"]}'],
        ['Counterfactual estimands',
         'Panel counterfactuals and their randomness (B4); counterfactual dose curves (M2)',
         'Linear, independent units; no physics',
         'A monotone salt response that identifies the probabilities of causation; dose-response over the recharge '
         'factor (Proposition L2)',
         f'T26: +{s["dose05"]} km² at half the recharge, −{s["dose15"]} km² at 1.5 times'],
    ]

