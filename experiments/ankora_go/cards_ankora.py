"""The twenty paper cards of the fourth state-of-the-art review (five per institution), from the verification notes of
four literature searches (November 2026), and the rows of its state-of-the-art table. Landing pages were reached through
search results only (doi.org, arxiv.org and most publisher hosts were blocked), so every card is marked partly verified.
None of the twenty was a card of reviews I–III or of the earlier reviews of the series.

Fields as in ../matja_go/cards_matja.py. Text conventions: $math$, **bold**, *italic*; [[anc]], [[mix]] refer to
equations of Section 4."""

OXFORD = [
    dict(id='O1', inst='Oxford', year=2026, short='River model: simulations, then gauges',
         title='Global river forecasting with a topology-informed AI foundation model',
         authors='Hancheng Ren, Gang Zhao, Shuo Wang, Louise Slater, Dai Yamazaki, Shu Liu, Jingfang Fan, Shibo Cui, '
                 'Ziming Yu, Shengyu Kang, Depeng Zuo, Dingzhi Peng, Zongxue Xu, Bo Pang',
         venue='arXiv:2602.22293 (preprint, February 2026); companion abstract EGU26-22456',
         links=[('arXiv:2602.22293', 'https://arxiv.org/abs/2602.22293'),
                ('EGU26-22456', 'https://meetingorganizer.copernicus.org/EGU26/EGU26-22456.html')],
         evidence='L. Slater: School of Geography and the Environment, University of Oxford (search summary of the EGU26 '
                  'abstract); the other affiliations seen were Beijing Normal University and the University of Tokyo. '
                  'Preprint; no journal version was seen.',
         does='GraphRiverCast is a graph network that follows the river-network topology and simulates several river '
              'variables over the globe. It is pre-trained on physics-based CaMa-Flood simulations driven by bias-'
              'corrected runoff and then fine-tuned on sparse in-situ gauges. In a "ColdStart" mode it needs no past river '
              'states, and in 7-day global pseudo-hindcasts it reaches NSE ≈ 0.82. After fine-tuning it is reported to '
              'beat physics-based and locally trained baselines, and the gauge information spreads through the network '
              'to ungauged reaches.',
         sota='A global river model pre-trained on simulations and fine-tuned on observations, carrying sparse gauge '
              'information to ungauged reaches.',
         gap='No calibrated uncertainty and no guarantee after fine-tuning; no per-basin gains seen; surface water only.',
         inputs='The closest real-world template for this batch: learn from the simulated aquifers (the prior over $T$, '
                '$S$, $\\kappa$, $\\tau$), then correct with a few real heads; the connectivity of the aquifer plays the '
                'role of the river topology in carrying anchor information to unmonitored wells.',
         dispersion='None.',
         bcs='ColdStart maps the forcing history alone to the state, which bears on the unknown initial heads and '
             'interface; river inflow is the analogue of the inland boundary.',
         step='Fine-tuning changes the estimator, not its guarantee, so keep the two roles of the anchors apart: '
              'fine-tune on some anchors and calibrate [[anc]] on the others. The band then holds for the real law '
              'whatever the fine-tuning did (Proposition A1), and at least 9 anchors must be kept for the calibration '
              '(Proposition A2).',
         steps=['emulate', 'guarantee'], informs=dict(inputs=2, dispersion=0, bcs=1)),
    dict(id='O2', inst='Oxford', year=2021, short='Satellite-calibrated soil, field probes',
         title='Improving soil moisture prediction of a high-resolution land surface model by parameterising '
               'pedotransfer functions through assimilation of SMAP satellite data',
         authors='E. Pinnington, J. Amezcua, E. Cooper, S. Dadson, R. Ellis, J. Peng, E. Robinson, R. Morrison, '
                 'S. Osborne, T. Quaife (initials as seen)',
         venue='Hydrology and Earth System Sciences 25, 1617–1641 (2021)',
         links=[('doi:10.5194/hess-25-1617-2021', 'https://doi.org/10.5194/hess-25-1617-2021'),
                ('NORA copy', 'https://nora.nerc.ac.uk/id/eprint/528407/1/N528407JA.pdf')],
         evidence='The affiliation list includes the School of Geography and the Environment, University of Oxford '
                  '(search summary); Dadson and Peng each appear with two affiliations, but which author holds the Oxford '
                  'one was not seen.',
         does='SMAP satellite soil moisture is assimilated to calibrate the constants of the pedotransfer functions that '
              'give the soil parameters of the JULES land-surface model, run at 1 km over Great Britain. The calibrated '
              'model is judged against independent COSMOS-UK cosmic-ray probes, with an average 22% reduction of the '
              'root-mean-square error over 11 probes.',
         sota='Satellite-driven calibration of pedotransfer constants at 1 km, validated at independent field probes.',
         gap='The 11 field probes only validate: they neither correct the calibration nor certify its uncertainty, and '
             'no interval or coverage was seen.',
         inputs='Our structure exactly: a wide but biased proxy (for us the simulations) calibrates a few shared '
                'constants, the soil-to-recharge parameters behind $\\kappa$ and $\\tau$, and a handful of ground '
                'anchors test them.',
         dispersion='None.',
         bcs='The timing of recharge from rain, through a calibrated land-surface parameterisation.',
         step='Make the probes calibrate, not only validate. With 11 independent probes [[anc]] already has a finite '
              'solution (Proposition A2 needs 9), so the satellite-calibrated model could carry a band that holds for the '
              'real soils, not only an error score; a certificate at 90% confidence would need 22 probes.',
         steps=['prior', 'check'], informs=dict(inputs=2, dispersion=0, bcs=1)),
    dict(id='O3', inst='Oxford', year=2025, short='Fine-tuning a global flood model locally',
         title='Fine flood forecasts: incorporating local data into global models through fine-tuning',
         authors='Emil Ryd, Grey Nearing',
         venue='ICLR 2025 Workshop "Tackling Climate Change with Machine Learning" (papers track); arXiv:2504.12559',
         links=[('arXiv:2504.12559', 'https://arxiv.org/abs/2504.12559'),
                ('workshop page', 'https://www.climatechange.ai/papers/iclr2025/50')],
         evidence='Ryd: University of Oxford; Nearing: Google Research (search summary of the arXiv author block). '
                  'Workshop paper.',
         does='A global machine-learning streamflow model is pre-trained on the Caravan dataset (about 6000 basins) and '
              'then fine-tuned on single basins, a random sample of 159. It is compared with the pre-trained model and '
              'with single-basin models by mean and median NSE and KGE (the numbers were not seen). Fine-tuning helps, '
              'most where the global model was poor; code and a pre-trained model are open.',
         sota='Basin-level fine-tuning of a global large-sample model beats both global-only and single-basin training.',
         gap='No uncertainty or guarantee; it needs years of local flow, far more than a handful of heads; surface water '
             'only.',
         inputs='A recipe for moving a many-site prior to one site, and the lesson that local data help most where the '
                'prior is worst, that is, where the simulator is wrong.',
         dispersion='None.',
         bcs='Rain-to-flow learned over many basins, a route to the inland inflow from rain alone.',
         step='Their finding is what T13 shows as width: anchors widen the band little where the simulator is right '
              '(+14% with 20 anchors) and as much as needed where it is wrong (up to 8.4 times for $\\kappa$). Add the '
              'guarantee they lack: after fine-tuning to a site, calibrate the band on held-out local periods by [[anc]].',
         steps=['emulate', 'guarantee'], informs=dict(inputs=1, dispersion=0, bcs=1)),
    dict(id='O4', inst='Oxford', year=2020, short='Emergent constraint across ensembles',
         title='Constraining uncertainty in aerosol direct forcing',
         authors='Watson-Parris, Bellouin, Deaconu, Schutgens, Yoshioka, Regayre, Pringle, Johnson, Smith, Carslaw, Stier '
                 '(surnames in the published order; given names not seen)',
         venue='Geophysical Research Letters 47(9), e2020GL087141 (2020)',
         links=[('doi:10.1029/2020GL087141', 'https://doi.org/10.1029/2020GL087141'),
                ('Oxford ORA', 'https://ora.ox.ac.uk/objects/uuid:0aa0aef9-9190-4afd-a2c7-6b3277ffd990'),
                ('White Rose copy', 'https://eprints.whiterose.ac.uk/160614/1/2020GL087141.pdf')],
         evidence='Deposited in Oxford\'s repository ORA; Watson-Parris and Stier were at Oxford\'s Atmospheric, Oceanic and '
                  'Planetary Physics in 2020 (review I, card O1); the per-author affiliations of this paper were not seen.',
         does='Across CMIP5 fixed-SST aerosol runs, AeroCom Phase II and a 26-parameter perturbed-parameter ensemble of '
              'HadGEM3-UKCA, present-day aerosol optical depth tracks the anthropogenic share of aerosol, so satellite '
              'observations of total aerosol narrow that share and the direct forcing. Emulators sampled at 10⁶ parameter '
              'combinations give a clear-sky estimate of about −0.69 ± 0.14 W m⁻². The authors warn that emergent '
              'constraints must be physically based and observationally robust.',
         sota='An emergent constraint checked across three model ensembles and an emulated perturbed-parameter ensemble.',
         gap='No coverage guarantee; it assumes that the relation found across the ensembles holds in reality, which is '
             'exactly the weak point of this review.',
         inputs='Learn the relation between an observable (a few heads, chloride facts) and a target ($T$, $\\kappa$) '
                'across the simulated aquifers, then insert the real value; demanding that the relation hold across '
                'different simulator families is a practical check of the prior.',
         dispersion='The same logic for chloride against the transition-zone width or the dispersivity (our inference).',
         bcs='None.',
         step='Anchors test the assumption an emergent constraint makes. Fit the observable-to-target relation on '
              'simulations, then calibrate its band on anchors by [[anc]]: if the relation transfers, the band stays near '
              'the simulation width; if not, it widens until valid. Agreement between simulator families is necessary for '
              'the mixing of [[mix]] to be safe, not sufficient (T14: ψ = 0.5 fails under shift in 9 of 12 cases).',
         steps=['emulate', 'invert', 'check'], informs=dict(inputs=2, dispersion=1, bcs=0)),
    dict(id='O5', inst='Oxford', year=2021, short='Offshore fresh water, relict interfaces',
         title='Offshore freshened groundwater in continental margins',
         authors='Aaron Micallef (first author), with Christian Berndt, Claudia Bertoni, Denis Cohen and others (the full '
                 'list and its order were not confirmed)',
         venue='Reviews of Geophysics 59(1), e2020RG000706 (2021; online November 2020)',
         links=[('doi:10.1029/2020RG000706', 'https://doi.org/10.1029/2020RG000706'),
                ('GEOMAR repository', 'https://oceanrep.geomar.de/id/eprint/51183')],
         evidence='C. Bertoni: Department of Earth Science(s), University of Oxford (search summary of the affiliation '
                  'list); the byline itself was not seen. An early citation gives volume 58.',
         does='The review compiles more than 300 records of offshore freshened groundwater and estimates a global volume '
              'of about 10⁶ km³. Most known occurrences lie in water less than 100 m deep, within 55 km of the coast, '
              'in siliciclastic aquifers of passive margins. How the deposits are detected and modelled was not seen in '
              'detail.',
         sota='The first global synthesis and volume estimate of offshore freshened groundwater.',
         gap='An inventory, not a site inference: no method to infer the offshore interface from onshore heads and '
             'chloride.',
         inputs='Offshore extensions of confined layers change the effective $T$ and $S$ near the coast.',
         dispersion='Relict fresh water means the transition zone need not be in steady state (our inference).',
         bcs='The initial interface may not be in equilibrium with today\'s sea level and should be seeded from the '
             'sea-level history; the sea boundary may belong at the offshore outcrop, not at the shoreline (our '
             'inference for a siliciclastic coastal plain such as Fushë-Kuqe).',
         step='A relict interface is a shift of the initial condition that simulations started at equilibrium cannot '
              'represent, so a toe band calibrated on them risks failing as the simulation calibration fails under the '
              'delayed law of T12 (risk up to 0.83). Seed the simulated interfaces from sea-level history, and treat '
              'offshore surveys of freshened groundwater as anchors for the initial condition.',
         steps=['prior'], informs=dict(inputs=1, dispersion=1, bcs=2)),
]

CALTECH = [
    dict(id='C1', inst='Caltech', year=2021, short='Post hoc UQ from simulated truth',
         title='Post hoc uncertainty quantification for remote sensing observing systems',
         authors='Amy Braverman, Jonathan Hobbs, Joaquim Teixeira, Michael Gunson',
         venue='SIAM/ASA Journal on Uncertainty Quantification 9(3) (2021); pages not seen',
         links=[('doi:10.1137/19M1304283', 'https://doi.org/10.1137/19M1304283'),
                ('NASA NTRS', 'https://ntrs.nasa.gov/citations/37989509222619'),
                ('JPL copy', 'https://uq.jpl.nasa.gov/Papers/2021.BravermanEtAl.JUQ.pdf')],
         evidence='NASA Jet Propulsion Laboratory (NTRS record; the paper is hosted on JPL\'s uncertainty-quantification '
                  'site; a search summary places all four authors at JPL); the byline was not seen.',
         does='Operational retrieval code cannot be re-run for uncertainty quantification, so it is done after the fact: '
              'a Gaussian-mixture regression fitted to an ensemble of simulated pairs (true state, operational estimate) '
              'gives the distribution of the truth given the estimate, which is applied to each new retrieval. It is '
              'shown on four months of OCO-2 data and compared with TCCON ground stations, where the truth is measured. '
              'No coverage numbers were seen.',
         sota='Operational post hoc uncertainty trained on simulated truth and checked at an independent ground network.',
         gap='The conditional law is only as good as the simulated pairs; the ground stations check it but do not '
             'correct it, and nothing is guaranteed.',
         inputs='Learn the law of ($T$, $\\kappa$, $\\tau$ given our estimate from rain and a few heads) from the '
                'simulated aquifers, as they learn the truth given a retrieval, and use the anchor sites or periods as '
                'they use TCCON.',
         dispersion='The same post hoc law for $\\alpha_L$ and the transition-zone width, with the few chloride profiles as '
                    'the ground network.',
         bcs='A post hoc law for the initial interface and the inland inflow.',
         step='Turn their ground check into the calibration: score the post hoc band at the anchors and set $\\lambda$ by '
              '[[anc]]. The band is then valid where the simulated pairs are wrong (Proposition A1), and the ratio of '
              'anchor- to simulation-calibrated half-width says how wrong: about 1.14 without shift and up to 4.85 for '
              '$\\kappa$ with the vadose delay (T13, 20 anchors).',
         steps=['emulate', 'guarantee', 'check'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='C2', inst='Caltech', year=2022, short='Prior-free frequentist intervals',
         title='Objective frequentist uncertainty quantification for atmospheric CO2 retrievals',
         authors='Pratik Patil, Mikael Kuusela, Jonathan Hobbs',
         venue='SIAM/ASA Journal on Uncertainty Quantification 10(3), 827–859 (2022); arXiv:2007.14975',
         links=[('doi:10.1137/20M1356403', 'https://doi.org/10.1137/20M1356403'),
                ('arXiv:2007.14975', 'https://arxiv.org/abs/2007.14975v2')],
         evidence='Hobbs: Jet Propulsion Laboratory, California Institute of Technology (search summary of the paper '
                  'text); DOI and pages as quoted by two bibliographic listings; the DOI page was not opened.',
         does='The operational OCO-2 retrieval (Bayesian optimal estimation with a prior) gives intervals that are poorly '
              'calibrated in the frequentist sense, at single locations and over regions. The authors invert the target '
              'functional (XCO₂) directly under known physical constraints by convex programming; the intervals have '
              'guaranteed frequentist coverage if the forward model is right, with no prior, and reach the nominal '
              'coverage in tests. They also rank the nuisance variables that drive the interval length.',
         sota='Prior-free intervals with guaranteed frequentist coverage where prior-based operational intervals fail.',
         gap='The (linearised) forward model and the noise must be known; intervals can be wide; no real anchors are '
             'used.',
         inputs='Constraint-only intervals for goal functionals (mean $T$, $\\kappa$, toe position) whose coverage does '
                'not depend on the simulator\'s prior: the fallback when the anchors show the prior is wrong.',
         dispersion='Bounds such as $\\alpha_L>0$, $\\alpha_T\\le\\alpha_L$ and plausible ranges give dispersivity '
                    'intervals that survive a wrong prior.',
         bcs='Sign and bound constraints on the inland inflow give a prior-free interval for the toe.',
         step='Use their prior-free interval as the base band $m\\pm s$ of [[anc]] for $\\kappa$, the unknown that '
              'shifts most. The anchors keep the guarantee for any law (Proposition A1), and a base that does not come '
              'from the prior should shrink the widening of T13 under shifted parameters (1.58 times for $\\kappa$ with 20 '
              'anchors), a pure prior shift; under the delay and the rain bias the forward model itself is wrong and '
              'only the anchors help. To be tested.',
         steps=['invert', 'guarantee'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='C3', inst='Caltech', year=2020, short='GRACE, wells and models in 14 aquifers',
         title='Comparison of groundwater storage changes from GRACE satellites with monitoring and modeling of major '
               'U.S. aquifers',
         authors='Ashraf Rateb (first author), with Bridget R. Scanlon, Sean Swenson, David Wiese and others (the full '
                 'list and its order were not confirmed)',
         venue='Water Resources Research 56(12), e2020WR027556 (2020)',
         links=[('doi:10.1029/2020WR027556', 'https://doi.org/10.1029/2020WR027556'),
                ('ADS record', 'https://ui.adsabs.harvard.edu/abs/2020WRR....5627556R'),
                ('USGS record', 'https://www.usgs.gov/publications/comparison-groundwater-storage-changes-grace-'
                                'satellites-monitoring-and-modeling-major')],
         evidence='JPL only through D. Wiese, listed at the NASA Jet Propulsion Laboratory on the USGS Powell Center page '
                  'of the GRACE working group; the byline affiliations were not seen, so this is the weakest institutional '
                  'link of the review.',
         does='In 14 major U.S. aquifers over 2002–2017, with about 23,000 wells, GRACE storage changes agree with the '
              'well monitoring (r = 0.52–0.95), and six southwestern and south-central aquifers lost about 90 km³. '
              'Global hydrological models that include pumping overestimate the GRACE depletion by about 2.4 times; in '
              'the Mississippi Embayment the regional model\'s decline is about four times GRACE, with storage '
              'parameters, stream capture, pumping or recharge named as possible causes.',
         sota='The largest three-way test of models against measured truth (satellite, wells, models) across major '
              'aquifers.',
         gap='Basin scale, far coarser than a coastal plain; no salinity; no formal correction.',
         inputs='A measured size for the model-to-reality error in real aquifers, factors of 2.4–4, traced to storage '
                'coefficients and recharge, the inputs we estimate.',
         dispersion='None.',
         bcs='Recharge and pumping forcing are named as causes, so anchor periods with measured pumping are the ones to '
             'keep.',
         step='Use their factors to size the shifts of a stress test and report the simulation-calibrated risk against '
              'the shift factor. Our law with factor 1.5 already gives 0.11–0.25 (T12), so a factor of 2.4–4 is beyond '
              'what simulation calibration can certify, while the anchor calibration stays at most 0.10 at any factor '
              '(Proposition A1).',
         steps=['check'], informs=dict(inputs=2, dispersion=0, bcs=1)),
    dict(id='C4', inst='Caltech', year=2022, short='Withheld-truth validation at flux towers',
         title='CARDAMOM-FluxVal version 1.0: a FLUXNET-based validation system for CARDAMOM carbon and water flux '
               'estimates',
         authors='Yan Yang, A. Anthony Bloom, Shuang Ma, Paul Levine, Alexander Norton, Nicholas C. Parazoo and others '
                 '(the list may continue; not confirmed)',
         venue='Geoscientific Model Development 15(4), 1789–1802 (2022)',
         links=[('doi:10.5194/gmd-15-1789-2022', 'https://doi.org/10.5194/gmd-15-1789-2022'),
                ('code, Zenodo', 'https://doi.org/10.5281/zenodo.4904195')],
         evidence='NASA Jet Propulsion Laboratory (search summary; CARDAMOM is developed by Bloom\'s group at JPL); the '
                  'byline was not seen.',
         does='A benchmark of the Bayesian model–data fusion system CARDAMOM (with the intermediate-complexity model '
              'DALEC) against more than 200 FLUXNET2015 eddy-covariance sites for gross primary production, net '
              'ecosystem exchange and evapotranspiration. Skill is scored against assimilated and withheld '
              'observations, by land cover, by time scale and by the length of the assimilated record; assimilation '
              'improves the skill in several respects (numbers not seen).',
         sota='Many-site, withheld-truth validation of a Bayesian model–data fusion system, with skill against record '
              'length.',
         gap='Carbon and evapotranspiration, not groundwater; skill scores, not coverage; the sites do not correct the '
             'prior.',
         inputs='A protocol for anchors: assimilate part of an anchor record, withhold the rest and report skill against '
                'record length, which says how many years of heads are needed; the evapotranspiration skill bears on '
                'recharge.',
         dispersion='None.',
         bcs='Recharge in time, indirectly through evapotranspiration.',
         step='Replace their skill scores by the realised risk of [[anc]] at withheld anchors, against the number of '
              'anchors: T13 does this for 10, 20 and 40 anchors (risk 0.011–0.099; without shift a half-width 1.03–1.55 '
              'times the simulation band), and Proposition A2 gives the floor of 9 anchors below which no guarantee '
              'exists, however long each record.',
         steps=['check', 'guarantee'], informs=dict(inputs=1, dispersion=0, bcs=1)),
    dict(id='C5', inst='Caltech', year=2022, short='Observation-anchored sea level',
         title='Observation-based trajectory of future sea level for the coastal United States tracks near high-end '
               'model projections',
         authors='B. D. Hamlington, D. P. Chambers, T. Frederikse, S. Dangendorf, S. Fournier, B. Buzzanga, R. S. Nerem '
                 '(initials as seen)',
         venue='Communications Earth & Environment 3, 230 (2022)',
         links=[('doi:10.1038/s43247-022-00537-z', 'https://doi.org/10.1038/s43247-022-00537-z'),
                ('JPL news', 'https://www.jpl.nasa.gov/news/nasa-study-rising-sea-level-could-exceed-estimates-for-us-'
                             'coasts')],
         evidence='A "JPL-led team" (JPL news release of 15 November 2022, which quotes Hamlington as leader of NASA\'s Sea '
                  'Level Change Team); the byline was not seen.',
         does='Twenty-eight years of satellite altimetry (1993–2020) and NOAA tide gauges give the rate and acceleration '
              'of sea level along the U.S. coast, which are extrapolated to 2050 with two treatments of internal '
              'variability. The observation-based trajectories lie near or above the high-end model projections, up to '
              'about 30 cm above today along the contiguous coast and highest on the Gulf and Southeast coasts, with '
              'wide ranges.',
         sota='Observation-anchored near-term regional sea-level trajectories, checked against model projections.',
         gap='U.S. coasts only; sensitive to internal variability; no tides or surges.',
         inputs='None.',
         dispersion='None.',
         bcs='Build the sea boundary $\\eta(t)$ and its uncertainty from a local tide gauge and altimetry rather than from '
             'model projections alone; here the observed anchor moved the scenario to the high end.',
         step='A tide gauge is an anchor for $\\eta$ in the sense of [[anc]]: calibrate the band of the sea-level '
              'reconstruction on gauge years, not on simulated sea levels. In T12 the simulation-calibrated sea-level '
              'band left 0.11–0.17 of the weeks outside under the three shifts; calibrated on 20 anchors it left 0.056 '
              'under every law.',
         steps=['prior', 'check'], informs=dict(inputs=0, dispersion=0, bcs=2)),
]

BERKELEY = [
    dict(id='B1', inst='Berkeley', year=2023, short='PPI++: tuned prediction-powered inference',
         title='PPI++: efficient prediction-powered inference',
         authors='Anastasios N. Angelopoulos, John C. Duchi, Tijana Zrnic',
         venue='arXiv:2311.01453 (2023, revised 2024)',
         links=[('arXiv:2311.01453', 'https://arxiv.org/abs/2311.01453'),
                ('code', 'https://github.com/aangelopoulos/ppi_py')],
         evidence='Angelopoulos: UC Berkeley; Duchi and Zrnic: Stanford (arXiv listing, as quoted). No journal version was '
                  'seen.',
         does='Prediction-powered inference combines many model predictions with a small labelled set to give confidence '
              'sets for any estimand defined by a convex loss. A tuning parameter moves the estimator between classical '
              'inference on the labels alone and plain prediction-powered inference, and a plug-in "power tuning" chooses '
              'it from the data; the authors report that the result is essentially never worse than either extreme and '
              'helps most when the predictor is not very accurate.',
         sota='Inference that takes its power from predictions or simulations but never depends on them being right.',
         gap='The labelled cases must be a random sample of the target; no temporal or spatial dependence, and no guidance '
             'for single-digit samples chosen on purpose.',
         inputs='Treat simulator outputs for $T$, $S$, $\\kappa$ or $\\tau$ as the predictions and the few anchor sites or '
                'periods as the labels: the interval stays valid from the anchors even if the simulator is wrong, and the '
                'tuned weight measures what the simulation is worth.',
         dispersion='The same applies to the transition-zone width when a few chloride profiles exist; with three to ten '
                    'profiles the interval honestly falls back to near-classical width.',
         bcs='Estimands such as the mean bias of simulated heads under an assumed sea level or inflow can be corrected by '
             'anchors in the same way.',
         step='Its tuning parameter plays the role of our share $\\psi$ in [[mix]], but for a mean, not a band. Carry the '
              'power tuning over to risk control: choose $\\psi$ by a rule that is itself validated on the anchors, so the '
              'mix can never be worse than anchors alone; T14 shows why the untuned mix is unsafe.',
         steps=['guarantee', 'check'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='B2', inst='Berkeley', year=2022, short='Multiyear calibration at an observatory',
         title='Quantifying subsurface flow and solute transport in a snowmelt-recharged hillslope with multiyear water '
               'balance',
         authors='Tetsu K. Tokunaga, Anh Phuong Tran, Jiamin Wan, Wenming Dong, Alexander W. Newman, Curtis A. Beutler, '
                 'Wendy Brown, Amanda N. Henderson, Kenneth H. Williams',
         venue='Water Resources Research 58(12), e2022WR032902 (2022)',
         links=[('doi:10.1029/2022WR032902', 'https://doi.org/10.1029/2022WR032902'),
                ('eScholarship', 'https://escholarship.org/uc/item/58m5w5wb'),
                ('LBNL highlight', 'https://watershed.lbl.gov/highlights/quantifying-snowmelt-recharge-into-hillslope-soils-and-rocks-and-solute-export-to-rivers/')],
         evidence='Lawrence Berkeley National Laboratory (eScholarship deposit; Watershed Function project highlight; search '
                  'summary); the byline affiliations were not seen.',
         does='At an instrumented hillslope of the East River observatory, a transmissivity-feedback model calibrated on one '
              'year of water balance and measured conductivity profiles predicted later years poorly. A well-constrained '
              'field-scale conductivity came only from fitting the fluxes over years with very different recharge and '
              'from carrying excess recharge from one year to the next. Solute export in high-snowmelt years runs through '
              'shallow soil and weathered rock and goes quiet in snow-drought years.',
         sota='Multi-year, contrast-spanning calibration at an observatory as the remedy for one-period calibration.',
         gap='A mountain hillslope at one site, not a coast; no formal guarantee or uncertainty for transfer.',
         inputs='One calibration period gives an unreliable conductivity: anchor periods must span contrasting recharge, '
                'and the carry-over of storage between years is a recharge memory like the vadose delay.',
         dispersion='The active transport pathways, hence the effective mixing, change with the recharge regime.',
         bcs='The recharge in time carries interannual memory, so the initial state matters; a few water-table and '
             'chemistry measurements act as anchors.',
         step='Choose anchor periods to span the recharge contrast, a wet and a dry year at least, because Proposition A1 '
              'guarantees only on average over the law the anchors are drawn from: anchors from wet years alone would '
              'certify nothing for a drought.',
         steps=['invert', 'guarantee'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='B3', inst='Berkeley', year=2023, short='Site similarity for borrowed priors',
         title='Defining hydrogeological site similarity with hierarchical agglomerative clustering',
         authors='Nura Kawa, Karina Cucchi, Yoram Rubin, Sabine Attinger, Falk Heße',
         venue='Groundwater 61(4), 563–573 (2023)',
         links=[('doi:10.1111/gwat.13261', 'https://doi.org/10.1111/gwat.13261'),
                ('repository record', 'https://e-docs.geo-leo.de/entities/publication/a82575a1-29b8-4877-afb9-ce7ee7c11939')],
         evidence='Kawa (Statistics), Cucchi and Rubin (Civil and Environmental Engineering): UC Berkeley, as listed on the '
                  'team\'s EGU 2018 abstract of the same project; the journal byline was not seen.',
         does='Site similarity is defined from observable site traits (environment, rock type) by hierarchical '
              'agglomerative clustering, and groups of similar sampled sites supply "ex-situ" prior distributions for the '
              'Bayesian estimation of hydraulic conductivity at a site without data of its own. It replaces expert '
              'judgment about which sites belong together; code and database are public.',
         sota='Data-driven choice of donor sites for informative priors in hydrogeology.',
         gap='Conductivity only; no coverage check of the transferred priors at held-out sites.',
         inputs='A principled way to borrow transmissivity priors for a coastal plain from measured analogue sites: a prior '
                'anchored on real data instead of on judgment.',
         dispersion='The same pipeline could supply dispersivity priors if the database held them; not done.',
         bcs='None.',
         step='Use the similarity to choose the anchors, not only the prior: Proposition A1 needs anchors exchangeable '
              'with the field, and a cluster of similar aquifers is the closest practical version of that assumption. '
              'Score the clustering by the coverage of the anchor-calibrated band at held-out sites.',
         steps=['prior', 'guarantee'], informs=dict(inputs=2, dispersion=1, bcs=0)),
    dict(id='B4', inst='Berkeley', year=2023, short='Clustered conformal prediction',
         title='Class-conditional conformal prediction with many classes',
         authors='Tiffany Ding, Anastasios N. Angelopoulos, Stephen Bates, Michael I. Jordan, Ryan J. Tibshirani',
         venue='Advances in Neural Information Processing Systems 36 (NeurIPS 2023); arXiv:2306.09335',
         links=[('NeurIPS 2023', 'https://proceedings.neurips.cc/paper_files/paper/2023/hash/cb931eddd563f8d473c355518ce8601c-Abstract.html'),
                ('arXiv:2306.09335', 'https://arxiv.org/abs/2306.09335')],
         evidence='UC Berkeley (paper hosted on Tibshirani\'s Berkeley Statistics page; Jordan and Tibshirani Berkeley '
                  'faculty); the byline was not seen.',
         does='Class-conditional coverage is hard when there are many classes and few labelled examples per class, and the '
              'per-class method gives sets too large to use. Clustered conformal prediction groups classes whose score '
              'distributions look alike and calibrates per cluster; on four image datasets with up to 1000 classes it '
              'typically improves class-conditional coverage and set size.',
         sota='Pooling scarce labels across similar groups for near-conditional conformal guarantees.',
         gap='Built for classification with exchangeability inside clusters; no model of a simulation-to-reality shift.',
         inputs='When each kind of site has only a handful of anchors, pool them across hydrogeologically similar groups.',
         dispersion='Chloride or interface prediction errors can be calibrated per cluster of settings.',
         bcs='None.',
         step='With 20 anchors in total but several boundary types (sea level, inflow, recharge), calibrate per cluster of '
              'anchors with similar score laws: the guarantee becomes nearly conditional on the type of aquifer, which is '
              'what a stakeholder at one aquifer needs, and the minimum of Proposition A2 applies per cluster.',
         steps=['guarantee'], informs=dict(inputs=1, dispersion=1, bcs=1)),
    dict(id='B5', inst='Berkeley', year=2024, short='Network classification of catchments',
         title='A network approach for multiscale catchment classification using traits',
         authors='Fabio Ciulla, Charuleka Varadharajan',
         venue='Hydrology and Earth System Sciences 28(7), 1617–1651 (2024)',
         links=[('doi:10.5194/hess-28-1617-2024', 'https://doi.org/10.5194/hess-28-1617-2024'),
                ('eScholarship', 'https://escholarship.org/uc/item/1913s953')],
         evidence='Both authors: Lawrence Berkeley National Laboratory (search summary; eScholarship copy; DOE/OSTI dataset).',
         does='9067 catchments of the contiguous US are classified with 274 non-categorical traits (temperature, '
              'precipitation, land use, human interference) by network cluster detection instead of Euclidean clustering. '
              'At continental scale it finds 25 interpretable trait categories and 34 catchment clusters with distinct '
              'streamflow behaviour, and degree centrality picks a representative catchment for each cluster.',
         sota='Network-based, scale-adaptive regionalisation with explicit representative sites.',
         gap='Surface catchments only: no groundwater or coastal traits and no guarantee on transfer.',
         inputs='A recipe for deciding which measured sites a target belongs with before parameters are transferred.',
         dispersion='None.',
         bcs='The traits are rain- and climate-heavy, so similarity can be judged from what is known everywhere.',
         step='The representative catchment of each cluster is the natural site to instrument as an anchor: one well-'
              'measured site per cluster of similar coastal aquifers, until each cluster holds the 9 (or 22) anchors that '
              'Proposition A2 requires.',
         steps=['prior', 'design'], informs=dict(inputs=1, dispersion=0, bcs=1)),
]

MIT = [
    dict(id='M1', inst='MIT', year=2026, short='Anchors chosen in waves, then debiased',
         title='M-estimation under two-phase multiwave sampling with applications to prediction-powered inference',
         authors='Dan M. Kluger, Stephen Bates',
         venue='arXiv:2602.16933 (preprint, February 2026; revised March 2026)',
         links=[('arXiv:2602.16933', 'https://arxiv.org/abs/2602.16933')],
         evidence='Both authors at MIT (search summary; the paper acknowledges the MIT IDSS Michael Hammer Postdoctoral '
                  'Fellowship). Preprint; the arXiv page was not opened.',
         does='Cheap proxies (machine-learning or simulator predictions) exist for every unit, and expensive accurate '
              'measurements are taken in successive waves. A multiwave predict-then-debias estimator is shown to be '
              'asymptotically linear and normal, with asymptotically valid confidence intervals, and an approximately '
              'greedy rule chooses the units to measure in the next wave, more efficiently than uniform sampling; '
              'simulation studies support the theory.',
         sota='Adaptive, wave-by-wave choice of the real measurements, with valid debiased inference afterwards.',
         gap='Validity is asymptotic and needs many units; simulations only; a finite population with proxies for every '
             'unit; no spatial or temporal dependence.',
         inputs='Where and when to spend the next pumping test or head campaign, given simulator predictions everywhere, '
                'with the final interval still valid after the adaptive choice.',
         dispersion='Which wells get the chloride or conductivity profiles that anchor the transition-zone width.',
         bcs='Which periods to monitor (after storms, at low sea level, in dry spells) for recharge and inflow.',
         step='Combine their waves with weighted risk control: an adaptively chosen anchor enters [[anc]] with a weight '
              'inverse to its probability of being chosen, as in their estimator, so anchors can be placed where the '
              'simulator is most in doubt and still certify the field average. The finite-sample proof for risk control '
              'is open.',
         steps=['design', 'guarantee'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='M2', inst='MIT', year=2025, short='Guaranteed transfer error across domains',
         title='The transfer performance of economic models',
         authors='Isaiah Andrews, Drew Fudenberg, Lihua Lei, Annie Liang, Chaofeng Wu',
         venue='arXiv:2202.04796 (working paper, first posted 2022; version 5, March 2025)',
         links=[('arXiv:2202.04796', 'https://arxiv.org/abs/2202.04796'),
                ('RePEc record', 'https://ideas.repec.org/p/arx/papers/2202.04796.html')],
         evidence='Partly MIT: I. Andrews rejoined MIT Economics as a professor in September 2023 (MIT News), before the '
                  '2025 revision, and D. Fudenberg is listed at MIT in an earlier review of this series; the affiliation '
                  'block was not seen, and one version names a Harvard department for a co-author. Working paper.',
         does='Out-of-domain prediction is formalised, and a model\'s transfer error is its performance in a new domain. '
              'Finite-sample intervals cover the realised transfer error at a chosen level when domains are drawn '
              'independently from one family, generalising conformal inference. Predicting certainty equivalents of '
              'lotteries across subject pools, black-box algorithms slightly beat economic models within a pool, but '
              'across pools their intervals are wider and their upper bounds higher: the structured models transfer '
              'more reliably.',
         sota='Distribution-free, finite-sample guarantees on the error of a model moved to a new domain, from a modest '
              'number of domains.',
         gap='Domains must be independent draws from one family, which is questionable for one Albanian aquifer; coarse '
             'with few domains; no hydrological use.',
         inputs='Treat each aquifer, simulated or a measured benchmark site, as a domain: an interval for how much a '
                'rain-to-head calibration of $T$, $\\kappa$, $\\tau$ degrades when moved to Fushë-Kuqe, and an argument '
                'for physics-structured estimators over black boxes.',
         dispersion='A transfer-error interval for dispersivity–scale relations borrowed from other sites.',
         bcs='The same for inflow or recharge relations regionalised from analogue basins.',
         step='Their domains are our anchors one level up. When the anchors come from several aquifers, calibrate '
              '[[anc]] on one aquifer-level score per aquifer (its share of weeks outside the band), so the guarantee '
              'holds for a new aquifer of the same family; the minimum of Proposition A2 is then counted in aquifers, '
              'not in years.',
         steps=['guarantee'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='M3', inst='MIT', year=2020, short='Calibrating a mixing closure, exposing its error',
         title='Uncertainty quantification of ocean parameterizations: application to the K-Profile-Parameterization for '
               'penetrative convection',
         authors='Souza, Wagner, Ramadhan, Allen, Churavy, Schloss, R. Ferrari (surnames as matched; the other given '
                 'names were not seen)',
         venue='Journal of Advances in Modeling Earth Systems 12(12) (2020); article number not seen',
         links=[('doi:10.1029/2020MS002108', 'https://doi.org/10.1029/2020MS002108'),
                ('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/136064')],
         evidence='MIT (deposited in DSpace@MIT, handle 1721.1/136064); the byline was not seen.',
         does='A Bayesian approach to calibrating and checking turbulent-mixing parameterizations: the convective limit '
              'of the K-Profile Parameterization is calibrated against an ensemble of large-eddy simulations of '
              'penetrative convection in the ocean surface boundary layer, which gives the uncertainty of its '
              'parameters. The calibration exposes structural deficiencies of the closure, and the authors propose an '
              'alternative scaling that removes them; they state that the method applies to any parameterization.',
         sota='Bayesian calibration that both estimates a mixing closure and diagnoses its structural error.',
         gap='The truth is large-eddy simulation, not field data; ocean convection, not porous media.',
         inputs='A misspecification test: if the calibrated $T$ or $\\kappa$ drift with the forcing regime (wet against '
                'dry years), the model\'s structure is wrong, not only its parameters.',
         dispersion='The closest card to dispersion: a mixing closure calibrated with full uncertainty against '
                    'high-resolution truth, where regime-dependent posteriors reveal its form error; the same logic '
                    'applies to the dispersivity of the transition zone.',
         bcs='None.',
         step='Make their regime test an anchor test: calibrate $\\hat\\lambda$ separately on wet-season and dry-season '
              'anchors. If the two differ by more than their sampling spread, the simulator is wrong in a regime-'
              'dependent way, and only anchors from both regimes can certify the band (Proposition A1; card B2).',
         steps=['invert', 'check'], informs=dict(inputs=1, dispersion=2, bcs=0)),
    dict(id='M4', inst='MIT', year=2024, short='Climate-invariant machine learning',
         title='Climate-invariant machine learning',
         authors='Tom Beucler, Pierre Gentine, Janni Yuval, Ankitesh Gupta, Liran Peng, Jerry Lin, Sungduk Yu, Stephan '
                 'Rasp, Fiaz Ahmed, Paul A. O\'Gorman, J. David Neelin, Nicholas J. Lutsko, Michael Pritchard',
         venue='Science Advances 10(6), eadj7250 (2024); arXiv:2112.08440',
         links=[('doi:10.1126/sciadv.adj7250', 'https://doi.org/10.1126/sciadv.adj7250'),
                ('arXiv:2112.08440', 'https://arxiv.org/abs/2112.08440')],
         evidence='MIT through P. A. O\'Gorman (the paper\'s supplement is hosted on his MIT group site, pog.mit.edu); the '
                  'printed affiliations were not seen.',
         does='Machine-learning parameterizations trained in one climate fail in others. Physically rescaling their '
              'inputs and outputs makes "climate-invariant" networks that keep high offline accuracy across climates '
              'and configurations in three atmospheric models; in the arXiv version they predict well in test climates '
              '4 K and 8 K warmer than the training climate.',
         sota='Physics-guided rescaling as the main tool for making simulation-trained machine learning generalise out '
              'of distribution.',
         gap='Empirical, with no coverage guarantee; the invariances must be known; no real anchors; atmosphere, not '
             'groundwater.',
         inputs='Train the simulation-based reconstructor on dimensionless inputs and outputs (head scaled by '
                '$rL^2/T$, time by $SL^2/T$) so that it survives the move to the real site.',
         dispersion='Express the transition-zone width relative to the aquifer thickness, with Péclet numbers or '
                    'dispersivity ratios.',
         bcs='Scale rain, recharge and sea level by their climatology, so the reconstructor stays valid in a drier or '
             'higher-sea climate.',
         step='Rescaling and anchors do different jobs: rescaling shrinks the shift, anchors certify what is left. Measure '
              'the first with the second: a rescaled reconstructor should bring the anchor-to-simulation width ratio of '
              'T13 under shift (1.20–8.41 with 20 anchors) back toward its no-shift value (1.13–1.16). To be tested first '
              'on the delayed law, where the shift is a time scale.',
         steps=['emulate'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='M5', inst='MIT', year=2024, short='The noise floor of the measured truth',
         title='Physical variability in meter-scale laboratory CO2 injections in faulted geometries',
         authors='Malin Haugen, Lluís Saló-Salgado, Kristoffer Eikehaug, Benyamine Benali, Jakub W. Both, Erlend Storvik, '
                 'Olav Folkvord, Ruben Juanes, Jan Martin Nordbotten, Martin A. Fernø',
         venue='Transport in Porous Media 151, 1169–1197 (2024)',
         links=[('doi:10.1007/s11242-023-02013-4', 'https://doi.org/10.1007/s11242-023-02013-4'),
                ('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/153395'),
                ('arXiv:2301.07347', 'https://arxiv.org/abs/2301.07347')],
         evidence='MIT (deposited in DSpace@MIT; Saló-Salgado and Juanes at MIT); the byline was not seen. A companion of '
                  'card M3 of review II, not the same paper.',
         does='Meter-scale CO₂ injections in two faulted geometries (normal faults with and without clay smear) were '
              'repeated in the laboratory, 16 runs in all, to measure the run-to-run variability of the migration '
              'patterns, and the distance of history-matched simulation models to an experiment was judged against it: '
              'a measured noise floor for the truth itself.',
         sota='Replicate experiments that measure the variability of the truth alongside history-matched forecasts.',
         gap='Laboratory scale, multiphase CO₂, not a field or variable-density seawater.',
         inputs='Even a perfectly measured anchor carries irreducible variability, which an anchor-corrected guarantee '
                'must count as noise in the anchor, not as simulator bias.',
         dispersion='The variability of dissolution and convective mixing bounds how much one chloride snapshot can '
                    'reveal about the mixing parameters.',
         bcs='None (controlled in the laboratory).',
         step='Count anchor noise before reading the anchor correction as shift: replicate anchors (two loggers in one '
              'well, repeated chloride profiles) estimate the noise of the measured truth, and a gap between the anchor- '
              'and simulation-calibrated bands smaller than that noise is no evidence of a wrong simulator. The '
              'guarantee of Proposition A1 covers the measured boundary, not the true one (Section 6).',
         steps=['check'], informs=dict(inputs=1, dispersion=1, bcs=0)),
]

INST_ORDER = ('Oxford', 'Caltech', 'Berkeley', 'MIT')


def all_cards():
    return OXFORD + CALTECH + BERKELEY + MIT


CARDS = all_cards()

def SOTA_ROWS(AJ):
    R = AJ['res']
    G4 = ('r', 'qL', 'eta', 'kappa')
    sims = [R[s][g]['sims']['risk'] for s in ('delay', 'params', 'rainbias') for g in G4]
    anc = [R[s][g]['m20']['anchors']['risk'] for s in R for g in G4]
    anc_all = [R[s][g][f'm{m}']['anchors']['risk'] for s in R for g in G4 for m in AJ['ms']]
    mixs = [R[s][g]['m20']['mix']['0.5']['risk'] for s in ('delay', 'params', 'rainbias') for g in G4]
    eta_s = [R[s]['eta']['sims']['risk'] for s in ('delay', 'params', 'rainbias')]
    eta_a = [R[s]['eta']['m20']['anchors']['risk'] for s in R]
    ma, mc = AJ['min_anchors']['expectation'], AJ['min_anchors']['certificate']
    return [
        ['Transferring knowledge between sites',
         'Donor-site priors from site similarity (B3); network regionalisation with representative sites (B5); '
         'pre-training on simulations, fine-tuning on gauges (O1, O3); intervals for the transfer error across '
         'domains (M2)',
         'Judged by average skill, or guaranteed only for domains drawn from one family; nothing certifies the target '
         'site',
         'Calibrate the target\'s bands on anchors chosen by similarity (Proposition A1); aquifer-level scores when '
         'anchors come from several aquifers',
         f'T12: with 20 anchors risk {min(anc):.3f}–{max(anc):.3f} under every law'],
        ['Inference with few real labels',
         'Prediction-powered inference, power-tuned (B1) and with anchors chosen in waves (M1); clustered conformal '
         'prediction (B4)',
         'For means or classes, not for bands of boundary functions; asymptotic, with no minimum sample stated',
         f'Anchor-calibrated risk control; at least {ma} anchors on average, {mc} for a certificate (Proposition A2)',
         'Propositions A1–A2'],
        ['Simulators that may be wrong',
         'Post hoc uncertainty from simulated truth, checked at ground stations (C1); prior-free frequentist '
         'intervals (C2); emergent constraints across ensembles (O4); physics-guided rescaling for use out of '
         'distribution (M4); simulation-calibrated guarantees (reviews I–III)',
         'The ground truth only checks; or the forward model must be right; or no coverage is stated',
         'Anchors make the guarantee simulator-free; simulations keep the design roles and build the score',
         f'T12: simulation-calibrated risk {min(sims):.2f}–{max(sims):.2f} under shift'],
        ['Mixing simulations and real data',
         'Power-tuned prediction-powered inference (B1); proxy-calibrated parameters validated at field probes (O2)',
         'The mix inherits the simulator\'s bias in proportion to its weight',
         'Exact bias bound α + ψ·TV (Proposition A3); anchors alone as the safe rule',
         f'T14: ψ = 0.5 gives risk {min(mixs):.2f}–{max(mixs):.2f} under shift'],
        ['Benchmarks with measured truth',
         'Satellite, wells and models across 14 aquifers (C3); withheld-truth validation at flux towers (C4); '
         'replicate experiments that measure the noise of the truth (M5)',
         'Skill scores, not coverage; model-to-data factors of 2.4–4 left uncorrected',
         'Benchmark sites and periods as anchors that calibrate, with replicates for the anchors\' own noise',
         f'T13: risk {min(anc_all):.3f}–{max(anc_all):.3f} with 10, 20 or 40 anchors'],
        ['Calibration periods and regimes',
         'Multiyear, contrast-spanning calibration at an observatory (B2); regime-dependent calibration that exposes '
         'a closure\'s structural error (M3)',
         'One period or one regime gives unreliable parameters',
         'Anchor periods chosen to span wet and dry years; anchors calibrated per regime as a test of the simulator',
         'Proposition A1 (the law of the anchors is the law guaranteed)'],
        ['Dispersion and the coast',
         'Mixing closures calibrated with full uncertainty (M3); recharge-dependent transport pathways (B2); relict '
         'offshore fresh water (O5); observation-anchored sea level (C5)',
         'No field dispersivity with a guarantee; sea boundary and initial interface taken from models',
         'Tide-gauge years and chloride profiles as anchors for the sea boundary and the transition zone',
         f'T12: sea-level risk {min(eta_s):.2f}–{max(eta_s):.2f} from simulations under shift, '
         f'{min(eta_a):.3f}–{max(eta_a):.3f} with 20 anchors'],
    ]
