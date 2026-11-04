"""The twenty paper cards of the third state-of-the-art review (five per institution), from the verification notes of
four literature searches (November 2026), and the rows of its state-of-the-art table. Landing pages were reached through
search results only (doi.org, arxiv.org and most publisher hosts were blocked), so every card is marked partly verified.
None of the twenty was a card of reviews I or II or of the earlier reviews of the series.

Fields as in ../matja_go/cards_matja.py: id, inst, year, short, title, authors, venue, links, evidence, does, sota,
gap, inputs, dispersion, bcs, step, steps, informs. Text conventions: $math$, **bold**, *italic*; [[floor]], [[prod]],
[[neff]] refer to equations of Section 4."""

OXFORD = [
    dict(id='O1', inst='Oxford', year=2024, short='Rain products scored by hydrology',
         title='Global-scale evaluation of precipitation datasets for hydrological modelling',
         authors='Solomon H. Gebrechorkos et al. (with Dadson, Slater and Wortmann; the full author list and the other '
                 'given names were not confirmed)',
         venue='Hydrology and Earth System Sciences 28(14), 3099–3118 (2024)',
         links=[('doi:10.5194/hess-28-3099-2024', 'https://doi.org/10.5194/hess-28-3099-2024'),
                ('HESS article', 'https://hess.copernicus.org/articles/28/3099/2024/'),
                ('author page', 'https://www.geog.ox.ac.uk/staff/sgebrechorkos.html')],
         evidence='Gebrechorkos: corresponding author at the School of Geography and the Environment, University of Oxford '
                  '(article summary as quoted; his Oxford staff page lists the paper); Slater and Wortmann also Oxford.',
         does='Six global precipitation products (ERA5, CHIRPS, MSWEP, TerraClimate, CPCU and PERCCDR) force the WBMsed '
              'global hydrological model for 1983–2019, and the simulated discharge is scored at 1825 stations. MSWEP, '
              'then ERA5, has the highest correlation and KGE at more than half of the stations; PERCCDR is worst, with '
              'biases up to 99% and normalised RMSE up to 247%. No product is best everywhere, so the choice must be made '
              'basin by basin.',
         sota='The global, model-based evaluation of rainfall products for hydrology.',
         gap='It scores discharge, not heads or recharge, and gives a ranking, not an error law usable at one coastal '
             'site; no guarantee.',
         inputs='A product\'s bias is absorbed by the recharge coefficient (and by the transmissivity where heads scale '
                'with $r/T$): $\\kappa$ calibrated on one product does not carry over to another, as Proposition R1 says.',
         dispersion='None.',
         bcs='The spread between products at one pixel is a measured envelope of the rain, hence of the recharge in time.',
         step='Set the bias prior $s_b$ of RESHJA-GO from the spread of the products at the site (ERA5, MSWEP, CHIRPS …) '
              'and draw $b$ from it in the simulated aquifers. The floor [[floor]] of $\\kappa$ is then known before any '
              'model run, and so is the value of a local gauge.',
         steps=['prior'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='O2', inst='Oxford', year=2026, short='24 rain products, 18 428 catchments',
         title='Comprehensive global assessment of 24 gridded precipitation datasets across 18 428 catchments using '
               'hydrological modeling',
         authors='Ather Abbas, Yuan Yang, Ming Pan, et al. (16 authors, with Solomon H. Gebrechorkos and Hylke E. Beck; '
                 'author list from the preprint)',
         venue='Hydrology and Earth System Sciences 30(11), 3399–3423 (2026)',
         links=[('doi:10.5194/hess-30-3399-2026', 'https://doi.org/10.5194/hess-30-3399-2026'),
                ('HESS article', 'https://hess.copernicus.org/articles/30/3399/2026/'),
                ('preprint', 'https://egusphere.copernicus.org/preprints/2025/egusphere-2024-4194/')],
         evidence='Oxford link through Gebrechorkos, who is at the Oxford School of Geography and the Environment on his '
                  '2024 HESS paper (O1) and in a 2026 EGU abstract; his affiliation in this paper\'s author block was not '
                  'seen.',
         does='An HBV model is calibrated against daily streamflow in each of 18 428 catchments smaller than 10 000 km², '
              'once per product, for 24 satellite, reanalysis, gauge and merged products. MSWEP V2.8 is best overall '
              '(median KGE 0.78), GDAS the best reanalysis (0.72, ERA5 0.71) and GPM+SM2RAIN the best satellite-only '
              'product (0.64); skill and error characteristics differ strongly by region.',
         sota='The largest product-by-product hydrological test of rainfall.',
         gap='Skill is measured after calibration, which compensates the bias, and on streamflow, not groundwater; no '
             'error bound for one aquifer.',
         inputs='Calibrating once per product shows that the model parameters absorb the product bias: the trap of '
                'Proposition R1, at global scale.',
         dispersion='None.',
         bcs='The catchments have our scale, so the regional rankings guide which product should drive the recharge, and '
             'the KGE gaps between products measure how uncertain the rain is.',
         step='Skill after calibration is the wrong yardstick for recharge: two products with equal KGE can imply '
              'different $\\kappa$. Rank products instead by the guaranteed width they leave for the goal, computed with '
              'RESHJA-GO and each product\'s error law, which penalises the bias that calibration hides.',
         steps=['prior', 'check'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='O3', inst='Oxford', year=2026, short='MSWEP V3, hourly 0.1° rain',
         title='MSWEP V3: machine learning-powered global precipitation estimates at 0.1° hourly resolution (1979–present)',
         authors='Xuetong Wang, Raied S. Alharbi, Oscar M. Baez-Villanueva, et al. (15 authors, with Solomon H. '
                 'Gebrechorkos and Hylke E. Beck)',
         venue='arXiv:2602.01436 (preprint, February 2026)',
         links=[('arXiv:2602.01436', 'https://arxiv.org/abs/2602.01436'),
                ('EGU26 abstract', 'https://meetingorganizer.copernicus.org/EGU26/EGU26-9714.html'),
                ('MSWEP', 'https://www.gloh2o.org/mswep')],
         evidence='Gebrechorkos: School of Geography and the Environment, University of Oxford, and University of '
                  'Southampton (EGU26 abstract of the same work, as quoted); his affiliation in the arXiv PDF was not seen.',
         does='Hourly 0.1° rainfall from 1979 to near present with about two hours of latency. Stacked machine-learning '
              'models merge satellite and (re)analysis precipitation and temperature with static variables into a '
              'baseline, which is then corrected with daily and monthly gauge data (57 666 and 86 000 stations, EGU26 '
              'abstract). The baseline reaches a median daily KGE of 0.69, against 0.61 for ERA5.',
         sota='Machine-learning-merged, gauge-corrected global rainfall at hourly 0.1°.',
         gap='A preprint; no per-pixel uncertainty in what was seen; the gauge correction may reuse the gauges one would '
             'validate against; coastal Balkan cells not evaluated in what was seen.',
         inputs='The best candidate long rain series where local gauges are sparse.',
         dispersion='None.',
         bcs='47 years of hourly forcing allow a long spin-up, so the initial head and interface can be generated by the '
             'forcing history instead of guessed.',
         step='Use the product\'s daily skill to set $v$ in [[prod]] and its gauge density to set $s_b$. Proposition R2 '
              'then gives what survives the vadose filter, $v/n_{eff}$: the weekly forcing error of an MSWEP-class '
              'product at a site is known before any model run.',
         steps=['prior'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='O4', inst='Oxford', year=2024, short='Elasticity curves of flow to rain',
         title='Elasticity curves describe streamflow sensitivity to precipitation across the entire flow distribution',
         authors='Anderson, Brunner, Slater and Dadson (given names not confirmed)',
         venue='Hydrology and Earth System Sciences 28(7), 1567–1583 (2024)',
         links=[('doi:10.5194/hess-28-1567-2024', 'https://doi.org/10.5194/hess-28-1567-2024'),
                ('ORA record', 'https://ora.ox.ac.uk/objects/uuid:32dfe497-45fa-4f61-9810-7bb4b2924fa6')],
         evidence='First author, Slater and Dadson: School of Geography and the Environment, University of Oxford '
                  '(article summary as quoted; ORA record); Brunner\'s affiliation not seen.',
         does='The precipitation elasticity of streamflow is estimated at many flow percentiles instead of the mean only. '
              'These elasticity curves are computed for 805 US catchments and clustered by shape; the annual-median '
              'elasticity gives an incomplete picture, and available water storage is the likely control of the curve '
              'shape. The code is published.',
         sota='Precipitation sensitivity resolved over the whole flow distribution, with storage as its control.',
         gap='Streamflow in the US, not groundwater; elasticity from historical co-variation, not from product error; no '
             'uncertainty bounds.',
         inputs='How much a rain error moves the outputs depends on storage and on the state (low or high flow), hence on '
                '$S$ and $\\tau$.',
         dispersion='None.',
         bcs='Inland inflow and baseflow respond to rain through storage; a quantile-dependent elasticity is a compact way '
             'to build inflow scenarios from rain alone.',
         step='In our model the elasticity of the recharge to a rain bias is exactly one ($r\\propto\\kappa b$), and that of '
              'the heads is set by storage. An elasticity curve of heads to rain, computed on the simulated aquifers, tells '
              'in which states (drought, flood) a rain error does most damage, which is where the RESHJA-GO bands widen.',
         steps=['prior', 'check'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='O5', inst='Oxford', year=2024, short='Homogenised dispersion and sorption',
         title='A homogenised model for dispersive transport and sorption in a heterogeneous porous medium',
         authors='L. C. Auton, M. P. Dalwadi, I. M. Griffiths (initials as on the authors\' 2022 companion paper)',
         venue='arXiv:2410.11519 (2024); manuscript under review',
         links=[('arXiv:2410.11519', 'https://arxiv.org/abs/2410.11519'),
                ('manuscript', 'https://people.maths.ox.ac.uk/griffit4/papers/auton_siap_2025.pdf')],
         evidence='Manuscript hosted on Griffiths\' page at the Mathematical Institute, University of Oxford; the '
                  'affiliation block and the final venue were not seen.',
         does='Multiple-scales homogenisation of transport through an array of arbitrarily shaped obstacles whose '
              'microstructure varies slowly in space gives effective advection, dispersion and sorption coefficients. The '
              'effective diffusivity carries a dispersive part that follows a power law consistent with classical Taylor '
              'dispersion.',
         sota='A mathematically derived dispersion–sorption closure for slowly varying heterogeneous media.',
         gap='Idealised two-dimensional microstructure, no density coupling, no field data and no field identification.',
         inputs='Sorption enters as an effective retardation.',
         dispersion='Dispersion is velocity-dependent and varies in space, $D(x,|v|)=D_m+c(x)\\,|v|^{n}$, not a constant: '
                    'the width of the transition zone should depend on the flow, and the prefactor and exponent are the '
                    'unknowns to infer from the chloride facts.',
         bcs='None.',
         step='Give the simulated aquifers the closure $D=D_m+c\\,|v|^{n}$ with uncertain $(c,n)$ instead of one '
              'dispersivity. Heads never inform it (review I, Proposition 6), so the rain product cannot spoil it either, '
              'and its guaranteed band carries the uncertainty of the closure.',
         steps=['prior'], informs=dict(inputs=1, dispersion=2, bcs=0)),
]

CALTECH = [
    dict(id='C1', inst='Caltech', year=2022, short='InSAR + GRACE storage, Tulare',
         title='Using Sentinel-1 and GRACE satellite data to monitor the hydrological variations within the Tulare '
               'Basin, California',
         authors='Donald W. Vasco, Kyra H. Kim, Tom G. Farr, J. T. Reager, David Bekaert, Simran S. Sangha, Jonny '
                 'Rutqvist, Hiroko K. Beaudoing',
         venue='Scientific Reports 12, 3867 (2022)',
         links=[('doi:10.1038/s41598-022-07650-1', 'https://doi.org/10.1038/s41598-022-07650-1'),
                ('PMC8907331', 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8907331/')],
         evidence='NASA Jet Propulsion Laboratory, managed by Caltech (JPL/NASA coverage as quoted: a JPL research team; '
                  'Kim a JPL postdoctoral fellow); the per-author affiliation block was not seen.',
         does='Sentinel-1 InSAR deformation and GRACE/GRACE-FO water storage are fitted together with a simple two-layer '
              'model: an unconfined near-surface aquifer above a confined one, separated by the Corcoran clay. Once the '
              'long-term compaction trend (about 0.3 m/yr of subsidence) is removed, virtually all the month-to-month '
              'ground motion is explained by changes in the aquifers, and rain can raise the water table while the ground '
              'still sinks.',
         sota='Joint calibration of a minimal layered aquifer model on InSAR and GRACE, separating the rain-driven water '
              'table from the pumping-driven confined response.',
         gap='The GRACE footprint is far larger than one coastal plain, thick compressible clays give a deformation '
             'signal a small plain may lack, and there is no salinity and no rain uncertainty.',
         inputs='Two compartments with two time scales: a fast unconfined layer driven by rain (our $\\kappa$ and '
                '$\\tau$) and a slow confined layer driven by pumping, with storage identified from deformation and mass '
                'together; Sentinel-1 covers Albania.',
         dispersion='None.',
         bcs='Seasonal deformation constrains the storage state and the inland inflow.',
         step='Ground motion responds to the recharge, so like the heads it sees only $c=\\kappa b$ (Proposition R1): InSAR '
              'cannot remove the floor of $\\kappa$ under a rain bias. It is free, though, and MATJA-GO values it for the '
              'recharge function like a dense but noisy logger network.',
         steps=['prior', 'design'], informs=dict(inputs=2, dispersion=0, bcs=1)),
    dict(id='C2', inst='Caltech', year=2020, short='Observation-weighted rain projections',
         title='Bayesian model averaging of climate model projections constrained by precipitation observations over '
               'the contiguous United States',
         authors='Elias C. Massoud, H. Lee, P. Gibson, P. Loikith, D. Waliser',
         venue='Journal of Hydrometeorology 21(10), 2401–2418 (2020; volume and pages from a repository record)',
         links=[('doi:10.1175/JHM-D-19-0258.1', 'https://doi.org/10.1175/JHM-D-19-0258.1'),
                ('ORNL record', 'https://impact.ornl.gov/en/publications/bayesian-model-averaging-of-climate-model-projections-constrained/')],
         evidence='Listed on Massoud\'s JPL Science people page (search result); the article\'s affiliation block was not '
                  'seen.',
         does='Bayesian model averaging weights a multi-model climate ensemble by how well each model matches the observed '
              'precipitation over the contiguous US. The weighted estimate reproduces mean rainfall better than the '
              'ensemble mean (RMSE 0.49 against 0.65), and its uncertainty spread is about a third of the total spread '
              'of the multi-model ensemble.',
         sota='Observation-constrained averaging that narrows precipitation projections about threefold.',
         gap='The observations are treated as truth, so the error of the gauge or gridded product is not modelled; the '
             'narrower spread has no coverage guarantee.',
         inputs='Rain scenarios can be weighted by their fit to the short local record before they drive the calibration '
                'of $\\kappa$ and $\\tau$.',
         dispersion='None.',
         bcs='Weighted future recharge scenarios.',
         step='The observations the weights are fitted to are themselves a product with a bias, and by Proposition R1 a '
              'model can be up-weighted for matching that bias. Fit the weights on simulated products whose truth is known '
              'and recalibrate on a fresh pool (review II, Proposition M1), so the narrowed spread keeps its coverage.',
         steps=['prior', 'guarantee'], informs=dict(inputs=0, dispersion=0, bcs=2)),
    dict(id='C3', inst='Caltech', year=2023, short='Optimal-transport debiasing + diffusion',
         title='Debias coarsely, sample conditionally: statistical downscaling through optimal transport and '
               'probabilistic diffusion models',
         authors='Zhong Yi Wan, Ricardo Baptista, Anudhyan Boral, Yi-Fan Chen, John Anderson, Fei Sha, Leonardo '
                 'Zepeda-Núñez',
         venue='Advances in Neural Information Processing Systems 36 (NeurIPS 2023); arXiv:2305.15618',
         links=[('NeurIPS 2023', 'https://proceedings.neurips.cc/paper_files/paper/2023/hash/94d13c2401fe119e57ba325b6fe526e0-Abstract.html'),
                ('arXiv:2305.15618', 'https://arxiv.org/abs/2305.15618')],
         evidence='Baptista: California Institute of Technology (arXiv rendering, as quoted); the other authors at Google '
                  'Research.',
         does='A two-stage method for downscaling without paired data: an optimal-transport map removes the bias at the '
              'coarse scale, then a probabilistic diffusion model adds the small scales by conditional sampling. It is '
              'shown on one- and two-dimensional fluid flows at 8× and 16× upsampling and keeps the physical statistics '
              'even when the low-frequency content of input and output differs.',
         sota='Separating bias correction (optimal transport) from small-scale generation (diffusion) in unpaired '
              'downscaling.',
         gap='Not shown on precipitation, with its zeros and intermittency, in what was seen; needs a high-resolution '
             'training set; no coverage guarantee.',
         inputs='A principled way to turn a biased reanalysis into station-like rain samples that drive the ensemble of '
                '$\\kappa$ and $\\tau$.',
         dispersion='None.',
         bcs='An ensemble of recharge series from a coarse product.',
         step='Its two stages map onto the two error terms of [[prod]]: the transport map treats the bias $b$, the diffusion '
              'model the daily errors. Proposition R2 says the daily errors matter only through $v/n_{eff}$ and the bias '
              'fully, so the debiasing stage is the one that needs a guarantee: calibrate its residual bias on simulated '
              'pairs and feed it to RESHJA-GO as $s_b$.',
         steps=['prior', 'emulate'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='C4', inst='Caltech', year=2021, short='Satellite rain errors over land',
         title='Adapting passive microwave-based precipitation algorithms to variable microwave land surface emissivity '
               'to improve precipitation estimation from the GPM constellation',
         authors='F. Joseph Turk, S. E. Ringerud, Y. You, A. Camplani, D. Casella, et al. (12 authors, with C. Prigent and '
                 'C. Peters-Lidard)',
         venue='Journal of Hydrometeorology 22(7), 1755–1781 (2021)',
         links=[('doi:10.1175/JHM-D-20-0296.1', 'https://doi.org/10.1175/JHM-D-20-0296.1'),
                ('CNR repository', 'https://iris.cnr.it/retrieve/d75ce0cd-2724-4562-9353-e0f91ffa0a63/hydr-JHM-D-20-0296.1.pdf')],
         evidence='Turk: NASA Jet Propulsion Laboratory, Caltech, to our knowledge; the byline affiliation could not be '
                  'seen in this environment, so this card has the weakest affiliation evidence of the twenty.',
         does='Over land the surface-emissivity part of passive-microwave measurements is much more variable than over the '
              'ocean, with varying sensitivity to near-surface precipitation. More than six years of GPM coverage give new '
              'insight into emissivity over land, snow and ice, which is used to improve the physically and '
              'semi-physically based retrievals of the constellation.',
         sota='Emissivity-adaptive passive-microwave precipitation retrieval across the GPM constellation.',
         gap='Retrieval level only: no propagation into hydrology and no coast-specific error numbers in what was seen.',
         inputs='The error of a satellite product over a coastal plain depends on the surface state: wet soil changes the '
                'emissivity, so the rain error is correlated with the state that drives recharge.',
         dispersion='None.',
         bcs='A caution against using land–sea mixed pixels as the recharge forcing at a coast.',
         step='A state-dependent rain error breaks the independence assumed in Proposition R2. Simulate it in the aquifers '
              '(the daily error depending on antecedent wetness; Proposition R3 still holds) and expect a filtered error '
              'larger than $v/n_{eff}$, because the errors then cluster in the wet spells that make the recharge.',
         steps=['prior', 'check'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='C5', inst='Caltech', year=2023, short='GRACE water-cycle science',
         title='Water cycle science enabled by the GRACE and GRACE-FO satellite missions',
         authors='Matthew Rodell, John T. Reager',
         venue='Nature Water 1, 47–59 (2023)',
         links=[('doi:10.1038/s44221-022-00005-0', 'https://doi.org/10.1038/s44221-022-00005-0'),
                ('NTRS record', 'https://ntrs.nasa.gov/citations/20230001313')],
         evidence='Reager: NASA Jet Propulsion Laboratory, Caltech (NTRS preprint, as quoted); the byline of the journal '
                  'version was not seen.',
         does='A review of how satellite gravimetry moved from the fringes of hydrology to a core tool of water-cycle and '
              'water-resources science. Terrestrial water storage, an Essential Climate Variable, is observed only by '
              'these missions; high-profile groundwater-depletion studies drove the interest, GRACE-FO followed in 2018, '
              'and a further mission is in development.',
         sota='The reference synthesis of GRACE hydrology.',
         gap='Far too coarse for one coastal plain, and no method for rainfall uncertainty.',
         inputs='Gravimetry gives a regional prior or check on the storage budget, hence on the recharge coefficient.',
         dispersion='None.',
         bcs='Regional storage and inflow anomalies.',
         step='Storage change from gravimetry does not depend on the rain product, so a regional water-balance closure '
              '(product rain minus evaporation, runoff and storage change) tests the product\'s bias, the one thing heads '
              'can never test (Proposition R1). It gives a regional estimate of $s_b$ for RESHJA-GO.',
         steps=['prior', 'check'], informs=dict(inputs=1, dispersion=0, bcs=1)),
]

BERKELEY = [
    dict(id='B1', inst='Berkeley', year=2020, short='Forcing resolution and head bias',
         title='Sensitivity of meteorological-forcing resolution on hydrologic variables',
         authors='Fadji Z. Maina, Erica R. Siirila-Woodburn, Pouya Vahmani',
         venue='Hydrology and Earth System Sciences 24(7), 3451–3474 (2020)',
         links=[('doi:10.5194/hess-24-3451-2020', 'https://doi.org/10.5194/hess-24-3451-2020'),
                ('HESS article', 'https://hess.copernicus.org/articles/24/3451/2020/'),
                ('eScholarship', 'https://escholarship.org/uc/item/7jp3d4mz')],
         evidence='Maina and Siirila-Woodburn: Energy Geosciences Division; Vahmani: Climate and Ecosystem Sciences '
                  'Division, Lawrence Berkeley National Laboratory (preprint affiliation lines, as quoted).',
         does='The integrated model ParFlow-CLM is forced with WRF meteorology downscaled at 0.5 to 40.5 km over the '
              'undammed Cosumnes watershed in California. Errors in the spatial pattern of the forcing propagate through '
              'the land surface and appear later in time: localized groundwater-level biases reach 5–10 m and surface '
              'water about 3 m, depending on season and location, with "serious implications for model calibration".',
         sota='The first systematic tracing of how forcing resolution turns into metre-scale groundwater-head bias in an '
              'integrated model.',
         gap='A deterministic sensitivity study of one snow-affected watershed: no probabilistic rain-error model, no '
             'guarantee and no salinity.',
         inputs='Calibrating $T$, $\\kappa$ and $\\tau$ against a coarse rain field makes them absorb the forcing error; '
                'because the error is lagged, it is confounded with $\\tau$.',
         dispersion='None.',
         bcs='The resolution of the rain field is itself an error of the recharge-in-time condition, and an initial head '
             'obtained by spin-up inherits a delayed bias.',
         step='Their delayed bias is what Proposition R2 predicts: the filter turns forcing errors into lagged recharge '
              'errors with covariance $K\\,\\mathrm{diag}(P^{2})\\,K^{\\top}$. Use that covariance as the recharge-error prior '
              '(R2 prior) instead of letting $\\kappa$ and $\\tau$ absorb the error; in T10 it cut the guaranteed recharge '
              'band with eight loggers by a third.',
         steps=['prior', 'invert'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='B2', inst='Berkeley', year=2021, short='Extreme-preserving gridded rain',
         title='An extreme-preserving long-term gridded daily precipitation dataset for the conterminous United States',
         authors='David W. Pierce, Lu Su, Daniel R. Cayan, Mark D. Risser, Ben Livneh, Dennis P. Lettenmaier',
         venue='Journal of Hydrometeorology 22(7), 1883–1895 (2021)',
         links=[('doi:10.1175/JHM-D-20-0212.1', 'https://doi.org/10.1175/JHM-D-20-0212.1'),
                ('eScholarship', 'https://escholarship.org/uc/item/1zd6n03c'),
                ('OSTI record', 'https://www.osti.gov/biblio/1864540')],
         evidence='Risser: Lawrence Berkeley National Laboratory (author list as quoted; OSTI record).',
         does='Two widely used gauge-based gridded daily products for the conterminous US are compared with their station '
              'data: they reduce the annual 1-day maximum precipitation by 27%, increase the wet-day fraction by 25% and '
              'underestimate 20-year return values by 30%. The main cause is the time adjustment that puts gauge '
              'observations into a common time frame. The new 1/16° dataset omits it, and forcing a land-surface model '
              'with it raises the annual 1-day maximum runoff by 38%.',
         sota='It identifies a bias created by how a product is built, corrects it, and quantifies how far it carries '
              'into runoff.',
         gap='US only; a deterministic correction without day-by-day uncertainty; not carried into recharge or groundwater.',
         inputs='A $\\kappa$ calibrated on a product with smeared peaks is biased, so the recharge coefficient depends on '
                'which product was used.',
         dispersion='None.',
         bcs='Rain errors are systematic distortions of intensity and wet days, not white noise: the error law of the '
             'recharge condition must contain that structure.',
         step='Extend the error law [[prod]] of RESHJA-GO to an intensity-dependent bias and a wet-day inflation '
              '(drizzle). Proposition R3 needs only that the law be simulated, and Proposition R2 still gives the filtered '
              'error, now with a bias that varies with intensity, hence with the season.',
         steps=['prior', 'check'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='B3', inst='Berkeley', year=2023, short='Atmospheric rivers and recharge',
         title='The role of atmospheric rivers on groundwater: lessons learned from an extreme wet year',
         authors='Erica R. Siirila-Woodburn, P. James Dennedy-Frank, Alan Rhoades, Pouya Vahmani, Fadji Maina, Benjamin '
                 'Hatchett, Yang Zhou, Andrew Jones',
         venue='Water Resources Research 59(6), e2022WR033061 (2023)',
         links=[('doi:10.1029/2022WR033061', 'https://doi.org/10.1029/2022WR033061'),
                ('eScholarship', 'https://escholarship.org/uc/item/425063sk')],
         evidence='Siirila-Woodburn: Earth and Environmental Sciences Area, Lawrence Berkeley National Laboratory '
                  '(affiliation as quoted); the article number is taken from the DOI.',
         does='The Cosumnes watershed in the record-wet water year 2017: a high-resolution regional climate model is '
              'coupled to a land surface–groundwater model with lateral flow, and water parcels are tracked from the '
              'atmosphere into the subsurface. Atmospheric rivers delivered more precipitation than other storms, but less '
              'of their water was stored at the end of the year, snow-derived recharge from them was much lower, and '
              'groundwater still declined because of pumping.',
         sota='Tracking water from atmospheric moisture all the way into aquifer storage.',
         gap='One year and one watershed; no uncertainty quantification of the forcing; no coastal boundary.',
         inputs='$\\kappa$ and $\\tau$ depend on the type and intensity of the storm: one constant $\\kappa$ times the rain '
                'is misspecified for extremes.',
         dispersion='None.',
         bcs='Recharge partitioning depends on the type of event, and the year-end storage, the next year\'s initial '
             'condition, depends on pumping as much as on rain: record rain is not record recharge.',
         step='Make $\\kappa$ event-dependent in the prior (smaller for intense events). Proposition R1 then says the heads '
              'identify an intensity-weighted $\\kappa b$, and the simulated aquifers must carry both the product\'s bias '
              'and the intensity dependence, or the guarantee of the recharge fails in wet years.',
         steps=['prior'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='B4', inst='Berkeley', year=2021, short='Fresh SGD hotspots, Crete',
         title='Capturing hotspots of fresh submarine groundwater discharge using a coupled surface–subsurface model',
         authors='X. Yu, Z. Xu, D. Moraetis, N. P. Nikolaidis, F. W. Schwartz, Y. Zhang, L. Shu, C. J. Duffy, B. Liu',
         venue='Journal of Hydrology 598, 126356 (2021)',
         links=[('doi:10.1016/j.jhydrol.2021.126356', 'https://doi.org/10.1016/j.jhydrol.2021.126356'),
                ('eScholarship', 'https://escholarship.org/uc/item/85p1f9c3')],
         evidence='Z. Xu: Climate and Ecosystem Sciences Division, Lawrence Berkeley National Laboratory (open-science '
                  'record and conference poster, as quoted).',
         does='A coupled surface–subsurface model of Crete estimates the fresh submarine groundwater discharge at about '
              '2.3×10⁸ m³/yr, 31% of the river discharge and 14% of the precipitation. Local maxima sit at river mouths, '
              'where gradients are larger and the structures more permeable, and the discharge responds to episodic rain '
              'in a delayed and prolonged way; segment values were compared with point measurements.',
         sota='Spatially resolved, island-wide fresh discharge to the sea from a model driven by meteorology, on a '
              'Mediterranean coast.',
         gap='Freshwater only: no density, no mixing zone and no uncertainty quantification.',
         inputs='The delayed, prolonged response constrains $\\tau$, and 14% of the rain gives the order of magnitude of the '
                'effective recharge coefficient on a Mediterranean coast.',
         dispersion='None.',
         bcs='A rain-driven freshwater outflow at the shoreline, concentrated at river mouths (for Fushë-Kuqe, the Erzen '
             'and Ishëm mouths): a flux condition at the sea boundary.',
         step='The fresh outflow integrates $c\\,f$ over the catchment, so a seepage or salinity survey at river mouths '
              'informs the same identifiable combination $c=\\kappa b$ as the heads (Proposition R1); with a rain gauge it '
              'pins $\\kappa$ itself. Price both with MATJA-GO.',
         steps=['prior', 'design'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='B5', inst='Berkeley', year=2023, short='Tracer mixing with Bayesian UQ',
         title='Constraining bedrock groundwater residence times in a mountain system with environmental tracer '
               'observations and Bayesian uncertainty quantification',
         authors='Nicholas E. Thiros, Erica R. Siirila-Woodburn, P. James Dennedy-Frank, Kenneth H. Williams, W. Payton '
                 'Gardner',
         venue='Water Resources Research 59, e2022WR033282 (2023)',
         links=[('doi:10.1029/2022WR033282', 'https://doi.org/10.1029/2022WR033282'),
                ('eScholarship', 'https://escholarship.org/uc/item/0xd8r84x')],
         evidence='Authors from the University of Montana, Lawrence Berkeley National Laboratory and the Rocky Mountain '
                  'Biological Laboratory (search results); deposited in eScholarship.',
         does='CFC-12, SF6, ³H and ⁴He are measured in fractured-bedrock wells along a hillslope of the East River '
              'watershed. MCMC estimates the noble-gas recharge temperature, recharge elevation and excess air and '
              'propagates them into mean residence times from lumped-parameter models; every sample needs a binary '
              'mixture of young and old water, and the uncertainty is much larger than in the usual practice that '
              'propagates only analytical errors.',
         sota='Full Bayesian propagation of tracer-input uncertainty into residence-time distributions.',
         gap='Lumped-parameter models in mountain bedrock: no spatial transport, dispersivity or transition-zone width.',
         inputs='The delay is a young–old mixture distribution, not one number.',
         dispersion='A template for turning a handful of tracer facts into mixing fractions with honest uncertainty; not a '
                    'dispersivity estimate.',
         bcs='The tracer input itself is uncertain, as the chloride input of rain and sea is for us.',
         step='Treat the Fushë-Kuqe chloride facts like their tracers: a fresh–sea mixing fraction with uncertain end '
              'members inside the simulated aquifers, so the guaranteed band of the transition-zone width carries the '
              'end-member uncertainty together with the dispersion closure (O5).',
         steps=['prior', 'guarantee'], informs=dict(inputs=1, dispersion=2, bcs=1)),
]

MIT = [
    dict(id='M1', inst='MIT', year=2024, short='Downscaling rainfall extremes',
         title='Statistical-physical adversarial learning from data and models for downscaling rainfall extremes',
         authors='Anamitra Saha, Sai Ravela',
         venue='Journal of Advances in Modeling Earth Systems (2024; volume and article number not confirmed)',
         links=[('doi:10.1029/2023MS003860', 'https://doi.org/10.1029/2023MS003860'),
                ('MIT News', 'https://news.mit.edu/2024/making-climate-models-relevant-local-decision-makers-0611'),
                ('arXiv:2212.01446', 'https://arxiv.org/abs/2212.01446')],
         evidence='Both authors: MIT, Department of Earth, Atmospheric and Planetary Sciences (MIT News of 11 June 2024 and '
                  'the follow-up arXiv listing, as quoted).',
         does='Coarse climate-model rainfall (0.25°) is turned into high-resolution fields (0.01°) with uncertainty: an '
              'iterative Gaussian process explores the data on a manifold, a generative adversarial network adds the '
              'fine scales, and simplified physics is corrected with historical statistics. The fields match observed '
              'spatial patterns and risk distributions in Denver and Chicago, and training needs little data.',
         sota='Fast downscaling of rainfall extremes that combines physics, statistics and adversarial learning, with '
              'uncertainty.',
         gap='Extremes only; tested in the US and Bangladesh; no gauge-error model, no propagation to recharge and no '
             'coverage guarantee.',
         inputs='With an ensemble of local rain fields, $\\kappa$ and $\\tau$ can be conditioned on many plausible rain '
                'series instead of one.',
         dispersion='None.',
         bcs='Local rainfall ensembles, extremes included, from coarse data: a time-varying recharge input with '
             'uncertainty, past and future.',
         step='Use the downscaler as the generator of the rain of the simulated aquifers, so the rain is random and '
              'Proposition R3 applies, and check its ensemble against a gauge with the conformal p-value of review I: an '
              'ensemble that fails the check would break the guarantee of the recharge.',
         steps=['prior', 'check'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='M2', inst='MIT', year=2021, short='Why Mediterranean winters dry',
         title='Elements of the dynamical response to climate change over the Mediterranean',
         authors='Alexandre Tuel, Paul A. O\'Gorman, Elfatih A. B. Eltahir',
         venue='Journal of Climate 34(3), 1135– (2021; end page not confirmed)',
         links=[('doi:10.1175/JCLI-D-20-0429.1', 'https://doi.org/10.1175/JCLI-D-20-0429.1'),
                ('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/133828')],
         evidence='DSpace@MIT deposit; hosted by the Eltahir (Civil and Environmental Engineering) and O\'Gorman (EAPS) '
                  'groups at MIT.',
         does='Winter circulation changes over the Mediterranean are tied to the vertical structure of stationary waves and '
              'their zonal asymmetries. In winter the Mediterranean lies just north of the edge of the Hadley cell, which '
              'helps explain the stronger winter response, and a strong anomalous ridge drives the regional decline of '
              'precipitation.',
         sota='The mechanism of Mediterranean winter drying, from stationary waves and the edge of the Hadley cell.',
         gap='GCM scale: no Adriatic downscaling, no daily statistics and no hydrology.',
         inputs='None.',
         dispersion='None.',
         bcs='The recharge season (winter) loses rain mainly through circulation, so future recharge and inflow '
             'scenarios should sample circulation uncertainty, not scale the rain.',
         step='For future guarantees the rain law itself shifts: draw the rain of the simulated aquifers from a '
              'circulation-conditioned weather generator (a ridge index), and bound what is lost when the calibration law '
              'and the future one differ with the shift bound of review I (Proposition 4).',
         steps=['prior', 'check'], informs=dict(inputs=0, dispersion=0, bcs=2)),
    dict(id='M3', inst='MIT', year=2021, short='12 km Mediterranean drying',
         title='Understanding climate change over the southwestern Mediterranean using high-resolution simulations',
         authors='Alexandre Tuel, Kang, Elfatih A. B. Eltahir (the second author\'s given name was not seen)',
         venue='Climate Dynamics (published online 2020; volume, pages and DOI not confirmed)',
         links=[('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/129749'),
                ('Eltahir group', 'https://eltahir.mit.edu/journal/understanding-climate-change-over-the-southwestern-mediterranean-using-high-resolution-simulations')],
         evidence='DSpace@MIT deposit and the Eltahir group page; the MIT Regional Climate Model is used.',
         does='The MIT Regional Climate Model is run at 12 km, driven by three GCMs; forced by ERA-Interim it captures the '
              'space–time patterns of precipitation. Under RCP4.5 and RCP8.5 it projects significant winter and spring '
              'declines: even with strong mitigation the three main watersheds of Morocco dry by 34% in spring and 22% in '
              'winter, through circulation changes that advect dry Saharan air.',
         sota='A 12 km, multi-GCM regional projection of Mediterranean drying, with its mechanism.',
         gap='South-western, not Adriatic, Mediterranean; CMIP5 scenarios; no daily bias correction aimed at recharge; '
             'no groundwater.',
         inputs='None.',
         dispersion='None.',
         bcs='The size of the seasonal decline brackets the recharge stress scenarios.',
         step='A 20–30% seasonal decline acts on the recharge exactly like a bias $b<1$ that drifts in time, and by '
              'Proposition R1 the heads cannot tell a drying climate from a wet-biased product. Only a long record of a '
              'trusted gauge separates them: a design argument for keeping one rain gauge for decades.',
         steps=['prior', 'design'], informs=dict(inputs=0, dispersion=0, bcs=2)),
    dict(id='M4', inst='MIT', year=2025, short='Internal variability and emulators',
         title='The impact of internal variability on benchmarking deep learning climate emulators',
         authors='Björn Lütjens, R. Ferrari, D. Watson-Parris, N. E. Selin',
         venue='Journal of Advances in Modeling Earth Systems 17, e2024MS004619 (2025); arXiv:2408.05288',
         links=[('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/163594'),
                ('arXiv:2408.05288', 'https://arxiv.org/abs/2408.05288')],
         evidence='DSpace@MIT deposit and the MIT Center for Sustainability Science and Strategy publication page; '
                  'Ferrari and Selin are MIT faculty. The journal DOI was not seen printed.',
         does='On ClimateBench a simple linear regression, close to pattern scaling, beat a 100-million-parameter deep '
              'emulator on three of four regionally resolved variables. The cause is the large internal variability of '
              'the targets: with ensemble means of 50 runs per pathway instead of 3, a deep model could win for '
              'precipitation, while linear methods stayed better for temperature.',
         sota='It shows that emulator rankings, precipitation included, can be artefacts of internal variability.',
         gap='GCM scale, annual and regional fields; no daily rain and no groundwater.',
         inputs='Calibrating $\\kappa$ and $\\tau$ on one short record risks fitting its low-frequency noise; parsimonious '
                'recharge models are safer.',
         dispersion='None.',
         bcs='Future rain scenarios should come from large ensembles or sample internal variability explicitly.',
         step='Internal variability is to the climate what the daily error is to the product: a noise the vadose filter '
              'averages only over $n_{eff}$ events (Proposition R2). Calibrate on many simulated rain records, never on one, '
              'so the guarantee covers it.',
         steps=['emulate', 'check'], informs=dict(inputs=1, dispersion=0, bcs=1)),
    dict(id='M5', inst='MIT', year=2023, short='FluidFlower mixing benchmark',
         title='The FluidFlower validation benchmark study for the storage of CO₂',
         authors='B. Flemisch, J. M. Nordbotten, M. Fernø, R. Juanes, et al. (full author list not confirmed)',
         venue='Transport in Porous Media 151(5), 865–912 (2024; online 2023)',
         links=[('doi:10.1007/s11242-023-01977-7', 'https://doi.org/10.1007/s11242-023-01977-7'),
                ('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/152270')],
         evidence='Juanes: MIT (DSpace@MIT deposit; MIT Earth Resources Laboratory announcement).',
         does='Repeated CO₂ injections into a metre-scale laboratory rig give a physical ground truth. Nine research groups '
              'forecast the outcome, alone and together, from a detailed petrophysical characterization of the sands, for '
              'multiphase flow, capillarity, dissolution and convective mixing, and the forecasts are compared with each '
              'other and with the experiment.',
         sota='The first cross-group validation benchmark, with physical truth, for forecasts of density-driven mixing.',
         gap='CO₂–brine at metre scale, not seawater; no field dispersivity and no rainfall. It is the parent study of '
             'review II\'s cards M3 and M4.',
         inputs='Even a full characterization of the medium did not make the forecasts agree.',
         dispersion='Predicted dissolution and mixing depend strongly on each group\'s model and closure: dispersivity and '
                    'transition-zone width are uncertain inputs to infer and to test against known truth, not literature '
                    'values.',
         bcs='None.',
         step='A benchmark with physical truth is the ideal external test of a guarantee: calibrate GARANCIA-GO bands on '
              'simulations of the rig and score them against the measured outcome, the first test of simulation-'
              'calibrated bands against a real rather than simulated truth.',
         steps=['guarantee', 'check'], informs=dict(inputs=1, dispersion=2, bcs=0)),
]

INST_ORDER = ('Oxford', 'Caltech', 'Berkeley', 'MIT')


def all_cards():
    return OXFORD + CALTECH + BERKELEY + MIT


CARDS = all_cards()


def SOTA_ROWS(RJ):
    R = RJ['res']
    nk = [R['naive'][d]['kappa']['sup_cover'] for d in ('1 logger', '2 loggers', '4 loggers', '8 loggers')]
    F = RJ['filter']
    neff = 1.0 / sum(F['kernel_ratio']) * len(F['kernel_ratio'])
    return [
        ['Rainfall products for hydrology',
         'Global multi-product evaluations (O1, O2); machine-learning-merged rainfall (O3); extreme-preserving gridded '
         'data (B2); downscaling of extremes (M1)' + CALTECH_SOTA['products'],
         'Skill scored on discharge or after calibration, which hides the bias; no error law for one site',
         'The product\'s error law in the simulated aquifers (Proposition R3, RESHJA-GO)',
         f'T9: κ coverage {min(nk):.2f}–{max(nk):.2f} if the product is treated as exact; 0.90 with its errors'],
        ['How rain errors reach the aquifer',
         'Forcing resolution turns into metre-scale head bias (B1); elasticity curves (O4); atmospheric rivers and '
         'recharge (B3)' + CALTECH_SOTA['propagation'],
         'Deterministic sensitivities, no law that can be used as a prior',
         'Exact filter law with the effective number of rain days and a covariance computed from the product '
         '(Proposition R2, R2 prior)',
         f'T11: measured variance on v/n_eff; mean n_eff {neff:.1f} against 57 for steady rain'],
        ['Identifying the recharge coefficient',
         'Calibration per product (O2); parameters absorb forcing errors (B1)',
         'κ calibrated on one product does not transfer; the bias is undetectable',
         'κ has a floor under a rain bias; report c = κb (Proposition R1)',
         f'T10: κ {R["aware_r2"]["8 loggers"]["kappa"]["halfwidth"]:.3f} with eight loggers, floor '
         f'{RJ["floor"]["halfwidth"]:.3f}; c to {R["aware_r2"]["8 loggers"]["kappa_eff"]["halfwidth"]:.3f}'],
        ['Measuring the rain',
         'Gauge-corrected products (O3)' + CALTECH_SOTA['gauge'],
         'The value of a local gauge is not computed against that of head loggers',
         'The gauge as a candidate instrument of MATJA-GO, valued by the guaranteed width it removes',
         f'T10: a gauge and one logger give κ to {R["gauge"]["1 logger"]["kappa"]["halfwidth"]:.3f}, the product with '
         f'eight loggers {R["aware_r2"]["8 loggers"]["kappa"]["halfwidth"]:.3f}'],
        ['Future rain and the coast',
         'Mechanisms and 12 km projections of Mediterranean drying (M2, M3); fresh discharge hotspots at river mouths (B4)'
         + CALTECH_SOTA['coast'],
         'Scenarios without guarantees; a drying climate and a biased product look the same to heads',
         'Circulation-conditioned rain in the simulated aquifers; shift bound for the future law; a long gauge record',
         'Proposition R1 and review I, Proposition 4'],
        ['Dispersion and mixing',
         'Homogenised dispersion closures (O5); cross-group mixing benchmark with physical truth (M5); tracer mixing '
         'with Bayesian uncertainty (B5)',
         'No field identification of dispersivity; closures not tested against truth',
         'Velocity-dependent closure and uncertain end members in the simulated aquifers; bands scored against a '
         'physical benchmark',
         'Review I, Proposition 6 and T4'],
    ]


CALTECH_SOTA = dict(products='; observation-weighted projections (C2); optimal-transport debiasing (C3)',
                    propagation='; state-dependent satellite rain errors over land (C4)',
                    gauge='; regional water-balance closure from gravimetry (C5); InSAR and GRACE storage (C1)',
                    coast='')
