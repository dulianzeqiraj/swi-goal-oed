"""The twenty paper cards of the fifth state-of-the-art review (five per institution), from the verification notes of
four literature searches (November 2026), and the rows of its state-of-the-art table. Landing pages were reached through
search results only (doi.org, arxiv.org and most publisher hosts were blocked), so every card is marked partly verified.
None of the twenty was a card of reviews I–IV or of the earlier reviews of the series.

Fields as in ../matja_go/cards_matja.py. Text conventions: $math$, **bold**, *italic*; [[hm]], [[hcal]] refer to
equations of Section 4."""

OXFORD = [
    dict(id='O1', inst='Oxford', year=2022, short='Robust forecasts across horizons',
         title='Smooth robust multi-horizon forecasts',
         authors='Andrew B. Martinez, Jennifer L. Castle, David F. Hendry',
         venue='In: Essays in Honor of M. Hashem Pesaran, Advances in Econometrics 43A, Emerald, 143–165 (2022)',
         links=[('doi:10.1108/S0731-90532021000043A008', 'https://doi.org/10.1108/S0731-90532021000043A008'),
                ('INET Oxford', 'https://www.inet.ox.ac.uk/publications/smooth-robust-multi-horizon-forecasts')],
         evidence='Listed by the Institute for New Economic Thinking at Oxford and issued as Nuffield College (Oxford) '
                  'Economics Working Paper 2021-W01; Castle and Hendry are at Oxford colleges and Climate Econometrics '
                  '(card O2); Martinez\'s affiliation was not seen.',
         does='Robust forecasting devices, read as local estimators of a long-run relation, adapt quickly after a break '
              'at the price of extra forecast-error variance. Smoothing them keeps most of the adaptation and cuts the '
              'variance, most at long horizons. The bias and variance after a location shift are derived analytically '
              'and checked by simulation; on UK productivity and US 10-year yields the devices sharply reduce persistent '
              'forecast failure (no numbers in the abstract).',
         sota='An analytic account of how the post-break bias and variance of a forecast device evolve with the horizon.',
         gap='Point forecasts only, with no coverage statement; macroeconomic series.',
         inputs='Read the recharge coefficient as a level that can shift: re-estimate the local level instead of '
                'freezing the value of the anchor years; the bias–variance trade-off over the horizon is what sets how '
                'far ahead a band stays valid.',
         dispersion='None.',
         bcs='Sea-level trend, inland inflow and recharge in time as series with location shifts; the growth of the '
             'error with the horizon is the widening a band needs.',
         step='Their trade-off between adaptation and variance is our choice of the window $L$ in [[hm]]: a short '
              'window follows a break, a long one is less noisy. Horizon matching makes every $L$ valid under the '
              'conditions of Proposition P2, so $L$ can be chosen for width on an earlier stretch of the record without '
              'touching the guarantee; with $L$ = 5 the band held through the abrupt shift of T16 ($\\kappa$ risk at most '
              '0.054).',
         steps=['guarantee'], informs=dict(inputs=2, dispersion=0, bcs=1)),
    dict(id='O2', inst='Oxford', year=2022, short='Forecasting through breaks and trends',
         title='Forecasting facing economic shifts, climate change and evolving pandemics',
         authors='Jennifer L. Castle, Jurgen A. Doornik, David F. Hendry',
         venue='Econometrics 10(1), 2 (2022)',
         links=[('doi:10.3390/econometrics10010002', 'https://doi.org/10.3390/econometrics10010002'),
                ('INET Oxford', 'https://www.inet.ox.ac.uk/publications/forecasting-facing-economic-shifts-climate-'
                                'change-and-evolving-pandemics')],
         evidence='Castle: Magdalen College; Doornik and Hendry: Nuffield College; all with Climate Econometrics, University '
                  'of Oxford (journal listing as quoted in a search summary).',
         does='Economic, climate and pandemic series share a wide-sense non-stationarity: evolving stochastic trends, '
              'sudden location shifts, data revisions and changes of measurement. The paper examines what these do to '
              'the design and selection of forecasting models, covering stochastic trends, location shifts, broken '
              'trends and the forecasting of breaks, and uses trend-indicator saturation to detect a changing trend and '
              'forecast with the most recent one.',
         sota='Indicator-saturation model selection that detects breaks and trend changes and forecasts through them.',
         gap='No interval coverage; the power of break detection with 20–30 annual values is not addressed; no '
             'hydrology.',
         inputs='Detect broken trends in the rain–recharge relation from the records and keep the anchors after the '
                'last break, where exchangeability with the future year is defensible.',
         dispersion='None.',
         bcs='Detect and extrapolate the latest trend segment of sea level and recharge; a detected break date marks '
             'where past anchors stop being comparable.',
         step='Detection and horizon matching complement each other. Through the abrupt shift of T16 the level-matched '
              'band stayed valid but widened (recharge half-width 0.13–0.29 mm/d against 0.06–0.07 without drift), '
              'because origins before the break score the break itself. Dropping the pre-break origins found by '
              'indicator saturation would narrow it, as long as at least 9 scores remain (Proposition P3).',
         steps=['check', 'guarantee'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='O3', inst='Oxford', year=2020, short='A century of seasonal hindcasts',
         title='Seasonal forecasts of the twentieth century',
         authors='Antje Weisheimer, Daniel J. Befort, Dave MacLeod, Tim Palmer, Chris O\'Reilly, Kristian Strømmen',
         venue='Bulletin of the American Meteorological Society 101(8), E1413–E1426 (2020)',
         links=[('doi:10.1175/BAMS-D-19-0019.1', 'https://doi.org/10.1175/BAMS-D-19-0019.1'),
                ('Oxford ORA', 'https://ora.ox.ac.uk/objects/uuid:6594f740-7b45-4bc7-8654-2797701376e6'),
                ('hindcast data, CEDA', 'https://catalogue.ceda.ac.uk/uuid/6e1c3df49f644a0f812818080bed5e45/')],
         evidence='Deposited in Oxford\'s repository ORA and listed on Weisheimer\'s Oxford Physics publication page; the '
                  'per-author affiliations were not opened.',
         does='Coupled seasonal hindcasts for 1901–2010 agree with operational systems in the recent period, but the '
              'skill for extratropical circulation indices (NAO, PNA) drops markedly in the middle of the century, and '
              'ENSO forecasts, very skilful recently and early in the century, are less so in the 1920s–1930s. The '
              'hindcasts are public.',
         sota='A century-long coupled seasonal hindcast set that shows the multidecadal non-stationarity of forecast '
              'skill.',
         gap='Skill, not calibration or coverage; no hydrological variable; the causes of the changes are not settled.',
         inputs='A calibration fitted on recent decades, such as a rain-forecast-to-recharge map, need not hold in '
                'another: anchors from one era can mis-calibrate another.',
         dispersion='None.',
         bcs='The public 110-year archive is a ready test bed for the question of this review: calibrate on a rolling '
             'origin and measure how coverage decays with the lag.',
         step='Use the archive to test Propositions P2 and P3 on real forecasts: treat a seasonal rain forecast as the '
              'reconstructor and compare plain and horizon-matched bands across decades of changing skill. It would show '
              'whether a skill change of the size they report behaves like our abrupt shift, where the matched band held, '
              'or like the accelerating drift, where it failed for $\\kappa$ after 10 years.',
         steps=['check'], informs=dict(inputs=1, dispersion=0, bcs=1)),
    dict(id='O4', inst='Oxford', year=2025, short='Warming accelerates drought severity',
         title='Warming accelerates global drought severity',
         authors='Solomon H. Gebrechorkos, Justin Sheffield, Sergio M. Vicente-Serrano, Chris Funk, Diego G. Miralles, '
                 'Jian Peng, Ellen Dyer, Joshua Talib, Hylke E. Beck, Michael B. Singer, Simon J. Dadson',
         venue='Nature 642, 628–635 (2025)',
         links=[('doi:10.1038/s41586-025-09047-2', 'https://doi.org/10.1038/s41586-025-09047-2'),
                ('Oxford ORA', 'https://ora.ox.ac.uk/objects/uuid:9086844c-86d9-4559-b780-1e805e7caeee')],
         evidence='Gebrechorkos: School of Geography and the Environment, University of Oxford, also Southampton (search '
                  'results); deposited in ORA.',
         does='An ensemble of high-resolution global drought datasets for 1901–2022 shows drought severity rising '
              'worldwide. Atmospheric evaporative demand raised drought severity by 40% on average; dry regions get drier '
              'and wet regions also show drying; in 2018–2022 the land area in drought was 74% larger than in 1981–2017, '
              'and evaporative demand accounts for 58% of that increase.',
         sota='A global, high-resolution, 122-year attribution of drought-severity trends to evaporative demand against '
              'rain.',
         gap='Drought indices, not recharge or heads; no site-scale guarantee.',
         inputs='With rain as the only series, the effective recharge fraction drifts down as evaporative demand rises '
                'even at unchanged rain: the rain-to-recharge map behind $\\kappa$ is not stationary.',
         dispersion='None.',
         bcs='Anchors from the 1980s–2000s overstate recharge in future years; the gridded indices cover Albania and give '
             'a local drift per year.',
         step='Their evaporative demand is the natural regressor for the window centre of [[hm]]: a fit in demand instead '
              'of in time removes a drift linear in the demand even when the demand does not rise steadily (to be '
              'tested; Proposition P2 is exact for time only). Without such a correction, a $\\kappa$ band calibrated on '
              'all past years left 0.20–0.59 of the field outside in T15.',
         steps=['prior', 'guarantee'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='O5', inst='Oxford', year=2021, short='A benchmark of real shift in time',
         title='Shifts: a dataset of real distributional shift across multiple large-scale tasks',
         authors='Andrey Malinin, Neil Band, Yarin Gal and others (the full author list was not seen)',
         venue='NeurIPS 2021 Datasets and Benchmarks Track; arXiv:2107.07455',
         links=[('NeurIPS Datasets and Benchmarks', 'https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/'
                                                    'ad61ab143223efbc24c7d2583be69251-Abstract-round2.html'),
                ('arXiv:2107.07455', 'https://arxiv.org/abs/2107.07455v2'),
                ('OATML, Oxford', 'https://oatml.cs.ox.ac.uk/publications/20211021_MalininBand2021Shifts.html')],
         evidence='Listed as a publication of Oxford\'s OATML group (Y. Gal, Department of Computer Science); the byline '
                  'affiliations were not opened.',
         does='A benchmark of real shift for uncertainty and robustness in three tasks: tabular weather prediction, '
              'machine translation and vehicle motion prediction. The weather data (September 2018 to September 2019) '
              'are split by time and by climate type: in-domain data share the training period and climates, while the '
              'shifted development and evaluation sets lie in other months and in snow and polar climates. Uncertainty '
              'is scored by retention curves.',
         sota='A large benchmark of real temporal and climatic shift for evaluating uncertainty.',
         gap='Shifts of months, no physics; uncertainty scored by retention, not coverage.',
         inputs='A ready test of how calibrated bands degrade when the target period and climate differ from the '
                'calibration: the analogue of past anchors and a future year.',
         dispersion='None.',
         bcs='Shift in time and shift in climate type are separable, so a drift can be told apart from a change of '
             'regime in the forcing.',
         step='Score coverage, not retention: run plain and horizon-matched conformal bands on its weather task, where '
              'the time split and the climate split play the roles of our linear drift and abrupt shift. T15–T16 predict '
              'that plain calibration fails on both and the matched band holds on both, at a price in width for the '
              'second.',
         steps=['check'], informs=dict(inputs=1, dispersion=0, bcs=1)),
]

CALTECH = [
    dict(id='C1', inst='Caltech', year=2022, short='Sea level extrapolated, checked by hindcast',
         title='Extrapolating empirical models of satellite-observed global mean sea level to estimate future sea level '
               'change',
         authors='R. S. Nerem, T. Frederikse, B. D. Hamlington (initials as seen)',
         venue="Earth's Future 10(4), e2021EF002290 (2022)",
         links=[('doi:10.1029/2021EF002290', 'https://doi.org/10.1029/2021EF002290'),
                ('NOAA repository', 'https://repository.library.noaa.gov/view/noaa/54199')],
         evidence='Hamlington: leader of the NASA Sea Level Change Team at JPL (NASA/JPL article); the affiliations of '
                  'Frederikse and Nerem on this paper were not confirmed on the byline.',
         does='A quadratic trend plus interannual (mainly ENSO) variability is fitted to the satellite-altimetry global '
              'mean sea level of 1993–2020, with a formal error assessment of the coefficients, and extrapolated 30 '
              'years: 16.4 cm by 2050 relative to 2020 (90% interval 11.3–21.4 cm), in agreement with SROCC and AR6. A '
              'hindcast before 1993 agrees well with tide-gauge global mean sea level over the second half of the 20th '
              'century. Rate and acceleration are assumed constant.',
         sota='An observation-only sea-level band extrapolated 30 years and checked against held-out decades of tide '
              'gauges.',
         gap='Global mean only; Gaussian coefficient errors, no distribution-free coverage; the constant acceleration is '
             'assumed, not tested.',
         inputs='None.',
         dispersion='None.',
         bcs='A ready drift model for the sea boundary (trend, acceleration, ENSO term) with coefficient uncertainty; '
             'their hindcast is the template for testing how far ahead a band calibrated today stays valid.',
         step='Their hindcast is horizon matching done once; do it at every origin. Fit their quadratic model on each '
              'window of anchor years, score the year $h$ later and calibrate by [[hcal]]: the band then holds $h$ '
              'years ahead without Gaussian coefficients, and the location-only score of Proposition P2 (i) with $p$ = 2 '
              'removes even a drift of degree 3. The record sets the reach: 30 years of altimetry with a window of 10 '
              'support 12 years (Proposition P3), so their 30-year extrapolation lies beyond what this record can '
              'guarantee distribution-free.',
         steps=['prior', 'check'], informs=dict(inputs=0, dispersion=0, bcs=2)),
    dict(id='C2', inst='Caltech', year=2024, short='The rate of sea-level rise doubled',
         title='The rate of global sea level rise doubled during the past three decades',
         authors='B. D. Hamlington, A. Bellas-Manley, J. K. Willis, S. Fournier, N. Vinogradova, R. S. Nerem, '
                 'C. G. Piecuch, P. R. Thompson, R. Kopp (initials as seen)',
         venue='Communications Earth & Environment 5, 601 (2024)',
         links=[('doi:10.1038/s43247-024-01761-5', 'https://doi.org/10.1038/s43247-024-01761-5'),
                ('NASA Sea Level Change', 'https://sealevel.nasa.gov/news/280/rate-of-sea-level-rise-doubled-over-30-'
                                          'years-new-study-shows/')],
         evidence='Hamlington: Jet Propulsion Laboratory, California Institute of Technology (search summary of the '
                  'paper); the other affiliations were not seen.',
         does='Global mean sea level rose 111 mm from 1993 to the end of 2023, and the rate rose from about 2.1 mm per '
              'year in 1993 to about 4.5 mm per year in 2023; if the trajectory continues, a further 169 mm is expected '
              'over the next 30 years, comparable to the middle of the AR6 range.',
         sota='A 30-year satellite record showing that the rate of rise doubled, with an observation-based trajectory.',
         gap='Global only, no Adriatic value; the uncertainty of the acceleration was not seen.',
         inputs='None.',
         dispersion='None.',
         bcs='The rate of the sea boundary itself drifts: a band calibrated on the anchor years 1993–2008 would '
             'under-cover today.',
         step='A doubling rate is the accelerating history of T15–T16, where the all-years band failed for $\\kappa$ and the '
              'recharge at every horizon and the level window failed for $\\kappa$ beyond 10 years. For the sea boundary, '
              'whose error spread changes little in our test bed, the trend window removes a constant acceleration exactly from the location-only score '
              '(Proposition P2 (i), $p$ = 1); the choice between level and trend should follow the measured acceleration, '
              'not the convenience of the shorter window.',
         steps=['prior'], informs=dict(inputs=0, dispersion=0, bcs=2)),
    dict(id='C3', inst='Caltech', year=2024, short='Land water dropped and did not recover',
         title='An abrupt decline in global terrestrial water storage and its relationship with sea level change',
         authors='Matthew Rodell, Anne Barnoud, Franklin R. Robertson, Richard P. Allan, Ashley Bellas-Manley, Michael G. '
                 'Bosilovich, Don Chambers, Felix Landerer, Bryant Loomis, R. Steven Nerem, Mary Michael O\'Neill, '
                 'David Wiese, Sonia I. Seneviratne',
         venue='Surveys in Geophysics 45(6), 1875–1902 (2024)',
         links=[('doi:10.1007/s10712-024-09860-w', 'https://doi.org/10.1007/s10712-024-09860-w'),
                ('open copy, Reading', 'https://centaur.reading.ac.uk/119306'),
                ('JPL news', 'https://www.jpl.nasa.gov/news/nasa-satellites-reveal-abrupt-drop-in-global-freshwater-'
                             'levels')],
         evidence='Landerer and Wiese share an affiliation in the byline; Landerer is a JPL scientist (his JPL CV) and the '
                  'release is on jpl.nasa.gov, but the text of that affiliation was not seen. The lead author is at NASA '
                  'Goddard.',
         does='From GRACE and GRACE-FO, global land water storage (without glaciers and ice sheets) fell rapidly between '
              'May 2014 and March 2016 and had not recovered by 2023, its upper range staying about 1 cm water-equivalent '
              'below the earlier one. The early drop is attributed mainly to back-to-back El Niños, with a possible '
              'added net drying from warming; NASA\'s release notes that 13 of the 30 most intense droughts of the GRACE '
              'era occurred after January 2015.',
         sota='The first global record of an abrupt drop in land water storage that did not recover.',
         gap='Footprints of 300 km or more; the attribution is left open.',
         inputs='A documented regime shift without recovery: anchor years before 2014 and after 2016 are not '
                'exchangeable, and the recharge coefficient may have stepped.',
         dispersion='None.',
         bcs='Recharge in time and inland inflow can carry a step rather than a trend, and the initial head need not '
             'return to its pre-drought level.',
         step='Their step is our abrupt shift. In T16 the level-matched band stayed valid through it for every goal (risk '
              'at most 0.066) while the all-years band failed ($\\kappa$ 0.29–0.35, recharge 0.20–0.22), because the '
              'origins that straddle the step put the step itself into the calibration. The cost is width, which a '
              'detected break date can cut back (card O2).',
         steps=['check', 'guarantee'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='C4', inst='Caltech', year=2023, short='Land motion of a coastal city at 30 m',
         title='Localized uplift, widespread subsidence, and implications for sea level rise in the New York City '
               'metropolitan area',
         authors='Brett A. Buzzanga, David Bekaert, Benjamin D. Hamlington, Robert Kopp, Marin Govorcin, Miller (given '
                 'name not seen)',
         venue='Science Advances 9(39), eadi8259 (2023)',
         links=[('doi:10.1126/sciadv.adi8259', 'https://doi.org/10.1126/sciadv.adi8259'),
                ('JPL news', 'https://www.jpl.nasa.gov/news/nasa-led-study-pinpoints-areas-of-new-york-city-sinking-'
                             'rising/')],
         evidence='Written by a team from NASA JPL and Rutgers University (JPL release of 27 September 2023); the byline '
                  'was not seen.',
         does='InSAR (2016–2023) and GNSS give land-motion velocities with uncertainties at 30 m. The metropolitan area '
              'sinks about 1.6 mm per year on average, consistent with glacial isostatic adjustment, with local hotspots '
              '(landfill areas of Queens, the I-78 corridor, Rikers Island) and modest uplift in parts of Queens and '
              'Brooklyn, which a co-author links possibly to groundwater pumping and injection.',
         sota='Land motion at 30 m with uncertainties for a coastal metropolis.',
         gap='One city; the uplift mechanism is not resolved; seven years is short for a trend.',
         inputs='Indirect: deformation tied to groundwater use could constrain the history of pumping and storage.',
         dispersion='None.',
         bcs='Vertical land motion is a part of relative sea level that varies in space and time and can be switched on '
             'and off by groundwater management within a few years.',
         step='Land motion driven by pumping is a drift with a known driver: use the local InSAR velocity series as the '
              'regressor of the window centre of [[hm]] for the relative sea level, so that the band follows the '
              'subsidence of the coastal plain (to be tested; Proposition P2 is exact for time). Sentinel-1 covers the '
              'Albanian coast, so the record exists.',
         steps=['prior', 'check'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='C5', inst='Caltech', year=2025, short='Conformal sets shaped for the decision',
         title='End-to-end conformal calibration for optimization under uncertainty',
         authors='Christopher Yeh, Nicolas Christianson, Alan Wu, Adam Wierman, Yisong Yue',
         venue='Transactions on Machine Learning Research (December 2025); arXiv:2409.20534',
         links=[('arXiv:2409.20534', 'https://arxiv.org/abs/2409.20534'),
                ('code', 'https://github.com/chrisyeh96/e2e-conformal')],
         evidence='Caltech (the NeurIPS 2024 workshop page of an earlier version lists Yeh, Christianson, Wierman and Yue '
                  'at the California Institute of Technology; Wu uses a caltech.edu address).',
         does='The predictive model is trained jointly with the downstream robust-optimization objective, with a '
              'differentiable conformal calibration inside the training loop. General convex uncertainty sets are '
              'represented as sublevel sets of partially input-convex neural networks, coverage comes from conformal '
              'prediction, and the method beats two-stage estimate-then-optimize baselines on battery arbitrage and '
              'portfolio optimization.',
         sota='Decision-focused conformal calibration of learned convex uncertainty sets.',
         gap='Exchangeability assumed; no drift; no physics.',
         inputs='Calibrate a joint set for $T$, $S$, $\\kappa$ and sea level that covers and is shaped for the decision '
                'it feeds, such as a pumping cap or a warning.',
         dispersion='The same for the set of dispersivity and transition-zone width.',
         bcs='The same for the set of boundary functions.',
         step='Put horizon matching inside their training loop: the calibration step becomes [[hcal]] with the matched '
              'scores, so the decision set is shaped for the pumping decision and valid $h$ years ahead. Because their '
              'sets are trained end to end, the scores must come from anchor years not used in training, which lowers '
              '$n(h)$ and so the reach of Proposition P3.',
         steps=['design', 'guarantee'], informs=dict(inputs=2, dispersion=1, bcs=1)),
]

BERKELEY = [
    dict(id='B1', inst='Berkeley', year=2023, short='Rolling risk control online',
         title='Achieving risk control in online learning settings',
         authors='Shai Feldman, Liran Ringel, Stephen Bates, Yaniv Romano',
         venue='Transactions on Machine Learning Research (November 2023); arXiv:2205.09095',
         links=[('arXiv:2205.09095', 'https://arxiv.org/abs/2205.09095')],
         evidence='S. Bates: UC Berkeley; the other authors: Technion (search summary of the arXiv author listing). The '
                  'TMLR venue was seen in one text copy only.',
         does='Rolling risk control is a calibration wrapper around any online learner that keeps a user-chosen risk '
              '(miscoverage, false-negative rate and others) at a set level even when the data distribution shifts '
              'arbitrarily. It extends adaptive conformal inference from the 0–1 loss to general losses, can control '
              'several risks at once, and is shown on online depth estimation; a poor fixed step size delays '
              'adaptation.',
         sota='The first online procedure that controls a general risk, not only coverage, under arbitrary drift.',
         gap='The guarantee is a long-run average over periods with feedback; nothing is said about a band used years '
             'ahead without feedback.',
         inputs='The conformal risk control of reviews I–IV can be run as a yearly update: each new anchor year with '
                'measured heads or chloride updates the calibration of the bands for $T$, $S$, $\\kappa$ and $\\tau$.',
         dispersion='The controlled risk can be a loss on the position or width of the transition zone, such as a '
                    'misplaced isochlor.',
         bcs='The same rolling control applies to bands for recharge in time and inland inflow.',
         step='Rolling control needs the truth every period; a boundary band for year $K+h$ gets it only $h$ years '
              'later. Horizon matching is the delayed-feedback version: the score of each past year is computed with the '
              'information available $h$ years before it, so the band is calibrated for exactly the delay at which it '
              'will be used (Proposition P2), and Proposition P3 says how long a delay a record of $K$ years supports.',
         steps=['guarantee'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='B2', inst='Berkeley', year=2025, short='Gradient equilibrium under shift',
         title='Gradient equilibrium in online learning: theory and applications',
         authors='Anastasios N. Angelopoulos, Michael I. Jordan, Ryan J. Tibshirani',
         venue='Journal of Machine Learning Research 26, paper 25-0356, 1–68 (2025); arXiv:2501.08330',
         links=[('JMLR 26', 'https://www.jmlr.org/papers/v26/25-0356.html'),
                ('arXiv:2501.08330', 'https://arxiv.org/abs/2501.08330'),
                ('Berkeley copy', 'https://www.stat.berkeley.edu/~ryantibs/papers/geq.pdf')],
         evidence='UC Berkeley (the paper is hosted on Tibshirani\'s Berkeley Statistics page; Jordan and Tibshirani are '
                  'Berkeley faculty); the paper\'s affiliation lines were not seen.',
         does='A sequence of iterates reaches gradient equilibrium when the average of the loss gradients along it tends '
              'to zero, a property that neither implies nor is implied by sublinear regret. Plain gradient and mirror '
              'descent reach it with constant step sizes, where regret usually needs decaying ones. Applications are '
              'post hoc corrections of black-box predictors under arbitrary shift: debiasing, calibrating predicted '
              'quantiles, and unbiased Elo scores.',
         sota='A unifying theory of why constant-step online corrections stay calibrated under arbitrary shift.',
         gap='Average-type guarantees with feedback at every step; no statement for a fixed number of years ahead; no '
             'physics.',
         inputs='The rain-driven reconstructor can be debiased year by year with a constant step, so that the mean '
                'residual stays near zero while the law drifts.',
         dispersion='None directly; the quantile application could target a quantile of the transition-zone width.',
         bcs='Post hoc bias correction of recharge-in-time and inflow forecasts under drift.',
         step='Their constant-step correction is the online form of our window centre $c_o$: both track a drifting mean. '
              'Run it on the anchor years, then score each past year at lag $h$ after the correction, as in [[hm]]: the '
              'correction then removes the drift, and the calibration certifies what is left $h$ years ahead, which '
              'neither does alone.',
         steps=['invert', 'guarantee'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='B3', inst='Berkeley', year=2023, short='Snow-to-rain shift amplifies extremes',
         title='A warming-induced reduction in snow fraction amplifies rainfall extremes',
         authors='Mohammed Ombadi, Mark D. Risser, Alan M. Rhoades, Charuleka Varadharajan',
         venue='Nature 619(7969), 305–310 (2023)',
         links=[('doi:10.1038/s41586-023-06092-7', 'https://doi.org/10.1038/s41586-023-06092-7'),
                ('LBNL news', 'https://newscenter.lbl.gov/2023/06/28/mountains-vulnerable-to-extreme-rain-from-climate-'
                              'change/'),
                ('eScholarship', 'https://escholarship.org/content/qt21d3g5jt/qt21d3g5jt.pdf')],
         evidence='Lawrence Berkeley National Laboratory (Berkeley Lab news release; eScholarship copy).',
         does='In high-elevation regions of the Northern Hemisphere, rainfall extremes rise by about 15% per °C of '
              'warming, twice the rate expected from water vapour alone, because warming shifts precipitation from snow '
              'to rain; this is shown in reanalysis and projections, and differences in how models split snow and rain '
              'explain 25–40% of the spread of the projections.',
         sota='An attributed, quantified trend in rain extremes beyond the water-vapour scaling.',
         gap='Extremes only; no recharge or groundwater; snow regions.',
         inputs='When the phase of precipitation shifts, the recharge coefficient and the vadose delay of a mountain '
                'catchment cannot be taken as stationary.',
         dispersion='None.',
         bcs='A drift rate per degree for the rain extremes that feed the inland inflow from the mountains (for '
             'Fushë-Kuqe, the upper catchments of the rivers that reach the plain).',
         step='A drift rate per degree is what Proposition P1 needs to put a number on the bias of plain calibration: '
              'with a warming trajectory it gives a drift per year, and the bound $\\alpha+0.9\\,\\delta(h+4)$ then says how '
              'soon a band calibrated on past years of inflow stops being trustworthy. Horizon matching removes the need '
              'to know $\\delta$, but the rate tells which drift law to test.',
         steps=['prior'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='B4', inst='Berkeley', year=2024, short='Groundwater decline under warming',
         title='Declining groundwater storage expected to amplify mountain streamflow reductions in a warmer world',
         authors='Rosemary Carroll, Richard Niswonger, Craig Ulrich, Charuleka Varadharajan, Erica Siirila-Woodburn, '
                 'Kenneth Williams (as seen; the list and its order were not confirmed)',
         venue='Nature Water 2, 419–433 (2024)',
         links=[('doi:10.1038/s44221-024-00239-0', 'https://doi.org/10.1038/s44221-024-00239-0'),
                ('USGS record', 'https://pubs.usgs.gov/publication/70254449')],
         evidence='Ulrich, Varadharajan and Siirila-Woodburn: Lawrence Berkeley National Laboratory (Desert Research '
                  'Institute news release); the byline was not seen.',
         does='An integrated hydrological model reaching 400 m depth in the East River (Colorado headwaters) shows '
              'groundwater to be a large, steady source of streamflow. Under warming, greater forest water use cuts '
              'recharge and drains storage; the losses are largest in dry years and do not fully recover in simulated '
              'wet periods, and including the groundwater decline roughly doubles the annual streamflow reductions.',
         sota='A deep integrated projection of how groundwater storage feeds back on streamflow loss under warming.',
         gap='One snow-dominated watershed; a model projection only; no uncertainty guarantee.',
         inputs='The effective recharge coefficient drifts down with evapotranspiration, and storage keeps a memory of '
                'dry years: past anchor years are biased for future ones.',
         dispersion='None.',
         bcs='Inland groundwater inflow declines over time, and the initial head of a future year depends on the '
             'history of dry years.',
         step='A decline that does not recover is a drift in the level and, through dry-year memory, in the spread of '
              'the errors: the location–scale form of [[hm]] handles both, while location alone failed (recharge risk '
              'up to 0.19 after the abrupt shift of T16, against at most 0.066 with the scale). Their model is a ready '
              'generator of realistic drift laws for the test.',
         steps=['prior', 'guarantee'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='B5', inst='Berkeley', year=2022, short='Mediterranean basin in extreme years',
         title='Projecting end-of-century climate extremes and their impacts on the hydrology of a representative '
               'California watershed',
         authors='Fadji Z. Maina, Alan Rhoades, Erica R. Siirila-Woodburn, Peter-James Dennedy-Frank',
         venue='Hydrology and Earth System Sciences 26(13), 3589–3609 (2022)',
         links=[('doi:10.5194/hess-26-3589-2022', 'https://doi.org/10.5194/hess-26-3589-2022'),
                ('eScholarship', 'https://escholarship.org/uc/item/48q622jh')],
         evidence='Listed under Lawrence Berkeley National Laboratory publications on eScholarship (search summary); the '
                  'paper\'s affiliation lines were not seen.',
         does='The undammed Cosumnes basin, with a Mediterranean climate, is modelled with ParFlow-CLM driven by a '
              'variable-resolution climate model under RCP8.5, comparing dry, median and wet years of 2070–2100 with '
              'historical ones. In the extreme years temperature rises by more than 2.5 °C and precipitation by more '
              'than 38% while snowpack falls by more than 90%; peak surface and groundwater storage rise by up to 75% '
              'and 23% and come earlier, and higher evapotranspiration then drives faster summer declines, fastest for '
              'groundwater.',
         sota='An integrated surface–subsurface projection of extreme years, with groundwater, in a Mediterranean basin.',
         gap='One climate model and one scenario; few years per class; no observational check; no guarantee.',
         inputs='The seasonal timing of recharge (vadose delay, recharge coefficient) shifts with warming in a '
                'Mediterranean climate like that of Albania.',
         dispersion='None.',
         bcs='Recharge in time gets a larger seasonal amplitude (wetter winters, drier summers), and future initial '
             'heads differ from past ones.',
         step='A larger seasonal amplitude is a drift of the scale, not only of the level, of the reconstruction errors '
              'week by week: exactly the case where the scale of [[hm]] matters (T16). Their projected years can be '
              'used as the future field of a test at a Mediterranean aquifer, with the past record as anchors.',
         steps=['prior', 'check'], informs=dict(inputs=1, dispersion=0, bcs=2)),
]

MIT = [
    dict(id='M1', inst='MIT', year=2025, short='Conformal under Lévy–Prokhorov shift',
         title='Conformal prediction under Lévy–Prokhorov distribution shifts: robustness to local and global '
               'perturbations',
         authors='Liviu Aolaritei, Zheyu Oliver Wang, Julie Zhu, Michael I. Jordan, Youssef Marzouk (the first three '
                 'contributed equally; the order differs between listings)',
         venue='Advances in Neural Information Processing Systems 38 (NeurIPS 2025); arXiv:2502.14105',
         links=[('NeurIPS 2025', 'https://proceedings.neurips.cc/paper_files/paper/2025/hash/'
                                 '5c3760faa9de12a0ff5afb839581a09f-Abstract-Conference.html'),
                ('arXiv:2502.14105', 'https://arxiv.org/abs/2502.14105')],
         evidence='Wang, Zhu and Marzouk: MIT (arXiv version 2 as quoted; the department differs between the PDF and the '
                  'HTML); Aolaritei and Jordan: UC Berkeley.',
         does='The shift between calibration and test data is modelled as a Lévy–Prokhorov ambiguity set, which covers '
              'local perturbations (every point moves a little) and global ones (a fraction of the mass moves anywhere). '
              'Pushing the set through the score reduces a high-dimensional shift to a one-dimensional one, so the '
              'worst-case quantile and coverage are computed exactly; the two parameters map explicitly to interval '
              'width and confidence, and the intervals stay valid under the shift (numbers not seen).',
         sota='Exact worst-case conformal coverage under a two-parameter (local and global) shift ball.',
         gap='A static shift between calibration and test, with no model of how the shift grows with time.',
         inputs='Bands for $T$, $S$, $\\kappa$ and $\\tau$ can be inflated by an explicit shift budget instead of '
                'assuming past anchors are exchangeable with the future.',
         dispersion='The same robust quantile applies to scores for the dispersivity or the transition-zone width.',
         bcs='If the drift of rain, evapotranspiration or sea level is written as a radius growing with the lead time, '
             'the band is valid while the radius stays within the budget.',
         step='Their radius is what horizon matching measures without being told: the scores of [[hm]] at lag $h$ carry '
              'the shift accumulated over $h$ years, so the calibrated $\\hat\\lambda_h$ is a data-driven budget. Fit '
              'their two parameters to the matched scores at each $h$ to get an interpretable drift-per-year that can be '
              'extrapolated beyond the horizon limit of Proposition P3, with the guarantee then conditional on the '
              'extrapolation.',
         steps=['guarantee'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='M2', inst='MIT', year=2024, short='Weighted conformal theory, collected',
         title='Theoretical foundations of conformal prediction',
         authors='Anastasios N. Angelopoulos, Rina Foygel Barber, Stephen Bates',
         venue='arXiv:2411.11824 (book, version 5, March 2026; to be published by Cambridge University Press)',
         links=[('arXiv:2411.11824', 'https://arxiv.org/abs/2411.11824')],
         evidence='S. Bates: Department of EECS, MIT (arXiv PDF as quoted in a search summary); Angelopoulos: UC Berkeley; '
                  'Barber: University of Chicago. The publication year of the printed book was not confirmed.',
         does='A text that collects the core proofs of conformal and distribution-free inference, including a chapter on '
              'weighted variants (weighted quantiles, covariate shift, label shift, general training-to-test shift, '
              'and distribution shift against conditional coverage) and chapters on exchangeability and '
              'cross-validation methods.',
         sota='The reference text that gathers the guarantees, including those beyond exchangeability.',
         gap='Theory only; the guarantees under drift in time depend on knowing the weights or the distances.',
         inputs='The formal basis for reweighting past anchor years toward a target year, with weights from covariates '
                'such as rain or evapotranspiration.',
         dispersion='None specific.',
         bcs='Weighting by sea-level or rain covariates is the textbook route to a drift-aware band.',
         step='Proposition P1 is the weighted bound of their weighted chapter applied to anchor years, and it shows the '
              'limit of the weighting route: with a drift growing with the lag, no weights that give a finite band beat '
              'the last nine years, whose bound $\\alpha+0.9\\,\\delta(h+4)$ still grows with $h$. Horizon matching leaves '
              'the weights alone and changes the scores instead.',
         steps=['guarantee'], informs=dict(inputs=1, dispersion=0, bcs=1)),
    dict(id='M3', inst='MIT', year=2023, short='Recharge source shifts with pumping',
         title='Shift in groundwater recharge of the Bengal Basin from rainfall to surface water',
         authors='Yusuf Jameel, Mason Stahl, Holly Michael, Benjamin C. Bostick, Michael S. Steckler, Peter Schlosser, '
                 'Alexander van Geen, Charles Harvey',
         venue='Communications Earth & Environment 4, 14 (2023)',
         links=[('doi:10.1038/s43247-022-00650-z', 'https://doi.org/10.1038/s43247-022-00650-z'),
                ('DOAJ record', 'https://doaj.org/article/f55b350ce2bc440ea427616292197f6c')],
         evidence='Jameel: MIT (corresponding e-mail at mit.edu; funding from MIT\'s Abdul Latif Jameel Water and Food '
                  'Systems Lab); Harvey shares his affiliation; the affiliation line itself was truncated in the results.',
         does='Stable isotopes of groundwater, rain and surface water across Bangladesh and eastern West Bengal, run '
              'through a Monte Carlo mixing model with three end-members (rain, standing water, large rivers), show that '
              'the share of recharge from stagnant surface water rose by about 50% over about 70 years while direct rain '
              'infiltration fell in relative terms. Standing-water recharge enters mostly in the late dry season; the '
              'authors attribute the shift to irrigated rice fields, ponds and a steeper downward gradient from pumping.',
         sota='The first basin-scale isotope evidence that recharge sources shift over decades because of pumping.',
         gap='A delta far from the sea, no salinity link; the result depends on the end-member values.',
         inputs='A rain-to-recharge coefficient calibrated on past years drifts as pumping grows; the coefficient and '
                'its season must be time-varying or tied to pumping.',
         dispersion='None.',
         bcs='Recharge in time and inflow from rivers or canals are not a fixed function of rain under growing pumping; '
             'isotopes give a cheap anchor that detects the drift.',
         step='Pumping growth is a drift of the recharge law that comes from the operator, so its rate is known in '
              'advance. Use the pumping record as the regressor of the window centre in [[hm]], and isotope years as '
              'anchors for the source of recharge: the band for $\\kappa$ then follows the pumping plan, which matters '
              'because a plain calibration on past years left up to 0.40 of the field outside for $\\kappa$ under linear '
              'drift (T15).',
         steps=['prior', 'check'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='M4', inst='MIT', year=2023, short='Where water–energy coupling tips',
         title='Land surfaces at the tipping-point for water and energy balance coupling',
         authors='Jianzhi Dong, Ruzbeh Akbar, Andrew F. Feldman, Daniel Short Gianotti, Dara Entekhabi',
         venue='Water Resources Research 59(2), e2022WR032472 (2023)',
         links=[('doi:10.1029/2022WR032472', 'https://doi.org/10.1029/2022WR032472'),
                ('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/165480')],
         evidence='MIT (DSpace@MIT record; Entekhabi named at MIT); Dong\'s affiliation at the time was not seen; the DOI '
                  'was formed from the article number.',
         does='Soil-moisture drydowns are detected in global remote-sensing data without using precipitation, robustly to '
              'measurement noise, and each is classed as water-limited or energy-limited evaporation. A tipping-point '
              'metric measures how often a landscape switches between the two regimes; regions that switch often will '
              'see the largest change in water–energy coupling for a unit shift in soil moisture (no numbers quoted).',
         sota='A global, precipitation-free diagnosis of switching between evaporation regimes.',
         gap='Surface soil moisture only; no recharge or groundwater closure; no projection.',
         inputs='Near the switching threshold, evapotranspiration and so the recharge coefficient respond nonlinearly to '
                'drift: the metric flags where a linear drift model is unsafe.',
         dispersion='None.',
         bcs='The drift of recharge can be diagnosed from satellite soil moisture even with rain-only ground data.',
         step='Their metric is a prior test of which part of Proposition P2 applies: where a landscape switches regimes '
              'often, the drift of $\\kappa$ is likely to accelerate, and the level window, which failed for $\\kappa$ '
              'after 10 years of accelerating drift (risk 0.17 at 15 years in T16), should give way to a shorter horizon '
              'or the trend window.',
         steps=['prior', 'check'], informs=dict(inputs=2, dispersion=0, bcs=1)),
    dict(id='M5', inst='MIT', year=2021, short='Why southern Europe dries in summer',
         title='Mechanisms of European summer drying under climate change',
         authors='Alexandre Tuel, Elfatih A. B. Eltahir',
         venue='Journal of Climate 34(22), 8913–8931 (2021)',
         links=[('doi:10.1175/JCLI-D-20-0968.1', 'https://doi.org/10.1175/JCLI-D-20-0968.1'),
                ('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/148544')],
         evidence='MIT (DSpace@MIT record; listed on Eltahir\'s MIT group site); Tuel also has a Bern record, so his own '
                  'affiliation at publication was not confirmed. Not the same paper as cards III-M2 and III-M3.',
         does='Observations and CMIP5 show that the dynamical mechanisms behind the decline of Mediterranean winter '
              'rainfall carry the drying into southern Europe in spring, which depletes soil moisture and, through the '
              'soil moisture–precipitation feedback, sets up drier summers; in northwestern Europe an anticyclonic '
              'anomaly west of the British Isles pushes the low-level moisture flow north. The framework explains the '
              'spread of model projections (no numbers quoted).',
         sota='A mechanistic account linking winter dynamical drying to summer drying through soil-moisture feedback.',
         gap='No groundwater or recharge numbers; nothing specific to Albania.',
         inputs='The physical direction of the drift of the recharge season and the evaporative demand over the Balkans: '
                'a prior on the sign and season of the drift.',
         dispersion='None.',
         bcs='The recharge window shortens (spring loss) and summer evapotranspiration rises, so recharge in time should '
             'drift by season, not through one annual coefficient.',
         step='A drift that differs by season is a drift in the shape of the weekly errors, not only in their level: '
              'apply [[hm]] per season (separate centres and spreads for the wet and the dry half-year), which keeps '
              'Proposition P2 exact for each half while halving the weeks per score; the horizon limit of Proposition '
              'P3 is unchanged because it counts years, not weeks.',
         steps=['prior'], informs=dict(inputs=1, dispersion=0, bcs=2)),
]

INST_ORDER = ('Oxford', 'Caltech', 'Berkeley', 'MIT')


def all_cards():
    return OXFORD + CALTECH + BERKELEY + MIT


CARDS = all_cards()

CT = dict(guarantee='; decision-focused conformal sets (C5)', water='; an abrupt drop in land water that did not recover (C3)',
          coast=': quadratic extrapolation checked by hindcast (C1); a doubled rate of rise (C2); land motion at 30 m (C4)',
          check='')      # Caltech entries of the state-of-the-art rows


def SOTA_ROWS(AJ):
    R = AJ['res']
    G4 = ('r', 'qL', 'eta', 'kappa')
    HS = AJ['hs']

    def risks(laws, m, gs=G4):
        return [R[l][g][m][str(h)]['risk'] for l in laws for g in gs for h in HS
                if R[l][g][m][str(h)]['finite'] > 0.999]
    drift = ('linear', 'accel', 'step')
    sims = risks(drift, 'sims')
    allk = risks(drift, 'all', ('kappa',))
    ok = risks(('none', 'linear', 'step'), 'ls0')
    acc_k15 = R['accel']['kappa']['ls0']['15']['risk']
    loc_r = max(risks(('step',), 'loc0', ('r',)))
    K, Ll = AJ['K'], AJ['l_level']
    return [
        ['Forecasting through change',
         'Smoothed robust devices across horizons (O1); indicator saturation for breaks and trends (O2); a century of '
         'hindcasts with changing skill (O3)' + CT['check'],
         'Point forecasts or skill scores; no coverage statement for a boundary function',
         'Horizon-matched calibration: the band is calibrated at the lag at which it is used',
         'Proposition P2'],
        ['Calibration over time',
         'Rolling risk control (B1); gradient equilibrium with constant steps (B2); conformal prediction under '
         'Lévy–Prokhorov shift (M1); weighted conformal theory (M2)' + CT['guarantee'],
         'Long-run averages with feedback every period, or a static shift budget; no years-ahead guarantee',
         'A guarantee for the year K + h from K anchor years, with no feedback in between',
         f'T16: risk {min(ok):.3f}–{max(ok):.3f} under no, linear and abrupt drift'],
        ['Plain anchors under drift',
         'Anchor calibration of review IV; weighted calibration beyond exchangeability',
         'Old years carry less error than the future; weights cannot remove a drift',
         'Proposition P1: no weighting beats the last nine years, whose bound still grows with h',
         f'T15: κ risk {min(allk):.2f}–{max(allk):.2f} with all past years, up to {max(sims):.2f} with simulations'],
        ['A drifting water cycle',
         'Evaporative demand drives drought severity (O4); snow-to-rain shift (B3); groundwater decline under warming '
         '(B4); Mediterranean extremes (B5); recharge source shifts with pumping (M3); regime tipping (M4); '
         'European summer drying (M5)' + CT['water'],
         'Measured or projected drift, but no guarantee for a band that must hold under it',
         'The location–scale score: level and spread of the errors re-estimated in each window',
         f'T16: location only leaves up to {loc_r:.2f} of the recharge weeks outside after the abrupt shift'],
        ['The moving coast',
         'Sea-level boundary from observations' + CT['coast'],
         'Projections and records without a horizon of validity',
         'Tide-gauge years as anchor years; horizon limited by the record length',
         f'Proposition P3: {AJ["h_max"]["0"]} years ahead for a {K}-year record (L = {Ll}), certificate '
         f'{AJ["h_cert"]["0"]}'],
        ['Benchmarks of shift',
         'Real temporal and climatic shift for uncertainty (O5)',
         'Scored by retention, not coverage',
         'Coverage at stated horizons under drift, level and spread',
         f'T16: accelerating drift beyond 10 years breaks the level version (κ {acc_k15:.2f})'],
        ['Dispersion and the transition zone',
         'No 2020–2026 paper on a width that changes in time at the four institutions',
         'Transition-zone width assumed stationary',
         'Chloride-profile years as anchor years for the width, scored by horizon matching',
         'Review I, Proposition 6 and T4; Proposition P2'],
    ]
