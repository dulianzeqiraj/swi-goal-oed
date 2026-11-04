"""The twenty paper cards of the second state-of-the-art review (five per institution), from the verification notes of
four literature searches (November 2026). Landing pages were reached through search results only: doi.org, arxiv.org,
openreview.net and most publisher hosts were blocked in this environment, so every card is marked partly verified.
None of the twenty was a card of the first review (GARANCIA-GO) or of the earlier reviews of the series.

Fields: id, inst, year, short (for the map figure), title, authors, venue, links [(label, url)], evidence (who was at
the institution and where it was seen), does (what the paper does and finds), sota (the state of the art it sets),
gap (what it cannot yet do for our problem), inputs / dispersion / bcs (what we learn for the input parameters, the
dispersion coefficient and the boundary conditions when only the rain is known), step (the innovation step it gives
us), steps (steps of the synthesis it serves), informs (2 direct, 1 indirect lesson).
Text conventions: $math$, **bold**, *italic*."""

OXFORD = [
    dict(id='O1', inst='Oxford', year=2025, short='Seawater trapped by a moving boundary',
         title='Groundwater dynamics beneath a marine ice sheet',
         authors='Gabriel Cairns, Graham Benham, Ian Hewitt',
         venue='The Cryosphere 19, 3725–3747 (2025); arXiv:2409.11848',
         links=[('doi:10.5194/tc-19-3725-2025', 'https://doi.org/10.5194/tc-19-3725-2025'),
                ('The Cryosphere', 'https://tc.copernicus.org/articles/19/3725/2025/'),
                ('arXiv:2409.11848', 'https://arxiv.org/abs/2409.11848')],
         evidence='Mathematical Institute, University of Oxford (arXiv listing as quoted); Benham\'s affiliation at '
                  'publication was not confirmed.',
         does='A two-dimensional cross-section model of groundwater flow in a sedimentary basin beneath a '
              'marine-terminating ice stream, over geological time, with seawater intrusion (sharp interface), ice growth '
              'and retreat and the basin geometry. Seawater is trapped by cycles of grounding-line advance and retreat or '
              'in pockets of the basin geometry; water exfiltrates where the basin shoals and re-infiltrates where it '
              'deepens. The basin permeability is estimated by matching the salinity profiles measured beneath Whillans '
              'Ice Stream.',
         sota='Seawater-intrusion dynamics under a moving marine boundary, with a permeability inverted from a few '
              'salinity profiles.',
         gap='No transition-zone width or dispersivity, no uncertainty quantification, two-dimensional only.',
         inputs='A worked case of estimating permeability from a few salinity profiles: close to our handful of chloride '
                'facts, and the reason why salinity data are worth more than heads for some inputs.',
         dispersion='None: mixing is excluded by construction, so the model shows what a sharp interface can and cannot '
                    'explain.',
         bcs='Today\'s interface records past positions of the sea boundary, so the **initial** interface should not be '
             'assumed in equilibrium with today\'s sea level. The initial condition is an unknown with memory, to be '
             'put in the prior.',
         step='Draw the initial interface of the simulated aquifers from a past sea-level history instead of the present '
              'equilibrium. GARANCIA-GO then guarantees the initial condition too, and MATJA-GO prices one deep salinity '
              'profile against a logger for the initial interface.',
         steps=['prior', 'invert'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='O2', inst='Oxford', year=2024, short='British Groundwater Model, rain to heads',
         title='Simulation of national-scale groundwater dynamics in geologically complex aquifer systems: an example '
               'from Great Britain',
         authors='Marco Bianchi, Johanna Scheidegger, Andrew Hughes, Christopher Jackson, Jonathan Lee, Melinda Lewis, '
                 'Majdi Mansour, Andrew Newell, Brighid Ó Dochartaigh, Ashley Patton, Simon Dadson',
         venue='Hydrological Sciences Journal 69(5), 572–591 (2024)',
         links=[('doi:10.1080/02626667.2024.2320847', 'https://doi.org/10.1080/02626667.2024.2320847'),
                ('NORA record', 'https://nora.nerc.ac.uk/id/eprint/537253/'),
                ('BGS project', 'https://www.bgs.ac.uk/geology-projects/environmental-modelling/british-groundwater-model/')],
         evidence='Dadson: University of Oxford (Oxford ORA record and Oxford climate-network listing); his printed '
                  'affiliation was not seen.',
         does='The British Groundwater Model, built in MODFLOW 6 on an unstructured grid of 1 km or finer, is coupled to '
              'the ZOODRM recharge model, which computes daily recharge from rain and potential evaporation with land use '
              'and geology. Parameters are calibrated with PEST against groundwater levels and baseflow; the model '
              'reproduces the groundwater systems of Great Britain reasonably well, and the resilience to climate extremes '
              'differs by region with lithology and climate.',
         sota='National-scale, rain-driven, integrated groundwater modelling: the practitioner\'s state of the art.',
         gap='Deterministic calibration, no salt transport or density effects, no uncertainty bounds.',
         inputs='The standard route to transmissivity and storage, PEST against heads and baseflow; deterministic, so it '
                'gives one value where we need a guaranteed band.',
         dispersion='None (flow only).',
         bcs='The recharge boundary is derived from rain through a distributed recharge model: exactly our route, at '
             'national scale.',
         step='Wrap a model of this kind in GARANCIA-GO: draw its uncertain recharge and aquifer parameters from a prior '
              'given the rain, run the PEST-calibrated reconstructor on each simulated aquifer, and calibrate its bands. A '
              'national model then carries a guarantee per aquifer, and MATJA-GO ranks the national logger network.',
         steps=['prior', 'invert', 'guarantee'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='O3', inst='Oxford', year=2020, short='Handpumps as head sensors',
         title='Shallow aquifer monitoring using handpump vibration data',
         authors='A. Manandhar, H. Greeff, P. Thomson, R. Hope, D. A. Clifton',
         venue='Journal of Hydrology X 8, 100057 (2020)',
         links=[('doi:10.1016/j.hydroa.2020.100057', 'https://doi.org/10.1016/j.hydroa.2020.100057'),
                ('ORA record', 'https://ora.ox.ac.uk/objects/uuid:1eebb9e7-629c-4907-8ecb-4cdd1e0ea47b'),
                ('accepted manuscript', 'https://eng.ox.ac.uk/media/4797/2020_hydrology_am.pdf')],
         evidence='University of Oxford (ORA record; accepted manuscript hosted by Oxford Engineering Science).',
         does='Accelerometers on the handles of nine Kenyan handpumps record for a year; machine-learning models fitted to '
              'each pump track the water level relative to the bottom of the rising main, combining regression with '
              'novelty detection. The authors present it as cheap, scalable aquifer monitoring wherever handpumps already '
              'exist.',
         sota='Existing water infrastructure as hydrological sensors in data-scarce aquifers.',
         gap='The range is limited by the rising main; no salinity; no rule for which sites to choose.',
         inputs='Many cheap head series constrain transmissivity and recharge.',
         dispersion='None.',
         bcs='Head dynamics at existing wells constrain the timing of recharge and the inland inflow.',
         step='Existing pumps and wells are a cheap pool of candidate sites. Give each its own noise level (a vibration '
              'sensor is noisier than a logger) and let MATJA-GO choose among them: a noisy but free series can be worth '
              'more than a precise logger at the wrong place (Section 4 ranks the eight logger sites by their guaranteed '
              'value).',
         steps=['design'], informs=dict(inputs=2, dispersion=0, bcs=1)),
    dict(id='O4', inst='Oxford', year=2022, short='Does calibration reduce uncertainty?',
         title='Does model calibration reduce uncertainty in climate projections?',
         authors='Simon F. B. Tett, Jonathan M. Gregory, Nicolas Freychet, Coralia Cartis, Michael J. Mineter, '
                 'Lindon Roberts',
         venue='Journal of Climate 35(8), 2585–2602 (2022)',
         links=[('doi:10.1175/JCLI-D-21-0434.1', 'https://doi.org/10.1175/JCLI-D-21-0434.1'),
                ('Reading repository', 'https://centaur.reading.ac.uk/102092')],
         evidence='An Oxford ORA record exists; the Oxford author is most likely Cartis (Mathematical Institute), but the '
                  'byline was not seen.',
         does='The atmospheric model HadAM3 is tuned with the derivative-free optimiser DFO-LS using a limited number of '
              'runs. Several locally optimal parameter sets fit the observations about as well as the CMIP5/6 models; the '
              'spread of climate sensitivity among them is two to six times smaller than in CMIP; the remaining spread '
              'comes from sea-ice feedbacks the targets do not constrain, and structural uncertainty probably dominates.',
         sota='An empirical measure of what calibration with few runs can and cannot reduce.',
         gap='No method for choosing the next observation and no formal guarantee.',
         inputs='Equifinality: several parameter sets fit equally well. Calibrating to heads can leave $\\kappa$ and '
                '$\\tau$ unconstrained, so the band must be computed, not inferred from the fit.',
         dispersion='By analogy, a process the calibration targets do not see stays unconstrained: dispersivity under '
                    'heads-only data (first review, Proposition 6).',
         bcs='None directly.',
         step='Turn the question of the title into a number: the guaranteed width before and after each calibration '
              'target is MATJA-GO\'s value of that target. Here the answer can be negative: a target the model cannot use '
              'well widens the guaranteed band (Proposition M3).',
         steps=['invert', 'design'], informs=dict(inputs=2, dispersion=1, bcs=0)),
    dict(id='O5', inst='Oxford', year=2022, short='Generative rain downscaling',
         title='A generative deep learning approach to stochastic downscaling of precipitation forecasts',
         authors='Lucy Harris, Andrew T. T. McRae, Matthew Chantry, Peter D. Dueben, Tim N. Palmer',
         venue='Journal of Advances in Modeling Earth Systems 14(10), e2022MS003120 (2022); arXiv:2204.02028',
         links=[('doi:10.1029/2022MS003120', 'https://doi.org/10.1029/2022MS003120'),
                ('PMC9788314', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC9788314'),
                ('arXiv:2204.02028', 'https://arxiv.org/abs/2204.02028')],
         evidence='Harris, McRae and Palmer: University of Oxford (search results; ORA file).',
         does='Generative adversarial networks and VAE-GANs downscale ECMWF IFS rainfall over the UK by a factor of 10 and '
              'produce spatially coherent high-resolution maps. They match state-of-the-art pointwise post-processing and '
              'compare favourably on CRPS, power spectra and rank histograms.',
         sota='Generative stochastic downscaling of rainfall: an ensemble of plausible local rain fields from a coarse '
              'forecast.',
         gap='Trained on a radar-rich UK, short-range, and no coverage guarantee.',
         inputs='None.',
         dispersion='None.',
         bcs='When "the rain" is a coarse product, the rain itself is uncertain: stochastic local fields give an ensemble '
             'of recharge forcings, and so of boundary conditions.',
         step='Make the rain a random input of the simulated aquifers: draw it from a generative downscaler conditioned '
              'on the coarse product, so the guarantees of GARANCIA-GO and the values of MATJA-GO include the error of '
              'the rain. A local rain gauge then becomes one more candidate instrument.',
         steps=['prior'], informs=dict(inputs=0, dispersion=0, bcs=2)),
]

CALTECH = [
    dict(id='C1', inst='Caltech', year=2024, short='Global intrusion: recharge vs sea level',
         title='Climate-induced saltwater intrusion in 2100: recharge-driven severity, sea level-driven prevalence',
         authors='Kyra H. Adams, John T. Reager, Brett A. Buzzanga, Cédric H. David, Audrey H. Sawyer, '
                 'Benjamin D. Hamlington',
         venue='Geophysical Research Letters 51(22), e2024GL110359 (2024)',
         links=[('doi:10.1029/2024GL110359', 'https://doi.org/10.1029/2024GL110359'),
                ('PMC11583115', 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11583115/'),
                ('JPL news', 'https://www.jpl.nasa.gov/news/nasa-dod-study-saltwater-to-widely-taint-coastal-groundwater-by-2100/')],
         evidence='Adams and Hamlington: NASA Jet Propulsion Laboratory, managed by Caltech (JPL news release naming Adams '
                  'as lead author); the byline itself was not seen.',
         does='Ensembles of projected recharge and sea-level rise drive a global one-dimensional analytical model of the '
              'interface toe (Ghyben–Herzberg with Dupuit–Forchheimer flow, extended for coastline migration) in 60 638 '
              'coastal watersheds, each an unconfined, homogeneous aquifer. About 77% of the coastal areas below 60°N see '
              'intrusion by 2100. Falling recharge drives the severe cases, sea-level rise and coastline migration drive '
              'how widespread intrusion is, and sea-level rise matters more where the inland boundary is head-controlled '
              'rather than flux-controlled.',
         sota='The first global projection of seawater intrusion that separates the recharge driver from the sea-level '
              'driver and shows that the type of the inland boundary decides which one dominates.',
         gap='Steady, sharp-interface and homogeneous: no mixing zone, no data assimilation and no local guarantee; the '
             'boundary type is assumed for each watershed, not identified from data.',
         inputs='The closed-form toe $x_t(K,\\bar r,\\text{geometry})$ is the cheapest emulator there is, and its '
                'sensitivity to the mean recharge converts a guaranteed band on $\\kappa$ into metres of toe: the goal a '
                'stakeholder cares about.',
         dispersion='None (sharp interface). The toe of such models is the 50% isochlor; the width of the transition '
                    'zone has to come from chloride data (first review, Proposition 6).',
         bcs='Whether the inland boundary is a flux or a head is the boundary question that decides the risk. In our test '
             'bed the inland inflow is witnessed only by heads near the inland edge, and MATJA-GO chooses exactly such a '
             'logger first for $q_L$ (Section 4).',
         step='Put the boundary **type** in the prior, as a mixture of a flux and a head boundary, and let MATJA-GO price '
              'the instrument that tells them apart: the guaranteed width of the toe under the mixture, with and without '
              'an inland logger, is the value of settling the boundary type.',
         steps=['prior', 'emulate', 'design'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='C2', inst='Caltech', year=2022, short='Inland inflow from space geodesy',
         title='Subsurface water flux in California\'s Central Valley and its source watershed from space geodesy',
         authors='D. F. Argus, H. R. Martens, A. A. Borsa, et al. (16 authors)',
         venue='Geophysical Research Letters 49, e2022GL099583 (2022)',
         links=[('doi:10.1029/2022GL099583', 'https://doi.org/10.1029/2022GL099583'),
                ('ADS record', 'https://ui.adsabs.harvard.edu/abs/2022GeoRL..4999583A'),
                ('JPL news', 'https://www.jpl.nasa.gov/news/nasa-measures-underground-water-flowing-from-sierra-to-central-valley')],
         evidence='Argus: JPL/Caltech (JPL news release presenting the study as JPL work); the full author order was not '
                  'confirmed, hence the short author list.',
         does='GPS displacements, GRACE gravity, reservoir volumes and snowpack close the water budget of the Central '
              'Valley and its Sierra Nevada source. The valley lost 2.2 ± 0.7 km³/yr of groundwater over 2006–2021; '
              'storage swings 10.7 ± 1.1 km³ each year and peaks in April; inflows total about 50 km³/yr (28 from '
              'rivers, 17 from precipitation and 5 as deep mountain groundwater arriving in autumn and winter); about a '
              'third of the drought loss was recharged in the following wet years.',
         sota='Closing a basin water budget, including the mountain-block groundwater inflow, from space geodesy.',
         gap='Basin scale with a dense GPS network; the uncertainty is not carried into a flow model, and there is no '
             'salinity.',
         inputs='The storage budget constrains the effective storage and the share of the rain that becomes recharge: a '
                'basin-scale prior for $S$ and $\\kappa$.',
         dispersion='None.',
         bcs='The inland lateral inflow and its seasonal lag behind the rain are measured, not assumed. In our notation the '
             'geodetic storage signal is a spatial integral of $S\\,\\partial h/\\partial t$, linear in $q_L$ and $r$, so '
             'it is one more candidate instrument for the inland boundary.',
         step='Add "storage from geodesy" (a GNSS station or InSAR over the recharge zone) to the candidates of MATJA-GO: '
              'its guaranteed value for $q_L$ and $\\kappa$ is computed before a station is bought, with the same '
              'calibration on simulated aquifers as a head logger.',
         steps=['prior', 'design'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='C3', inst='Caltech', year=2025, short='Vertical land motion and sea level',
         title='Variable vertical land motion and its impacts on sea level rise projections',
         authors='Marin Govorcin, David Bekaert, Benjamin Hamlington, Simran Sangha, William Sweet',
         venue='Science Advances 11(5), eads8163 (2025)',
         links=[('doi:10.1126/sciadv.ads8163', 'https://doi.org/10.1126/sciadv.ads8163'),
                ('NASA news', 'https://www.nasa.gov/missions/nisar/nasa-led-study-pinpoints-areas-sinking-rising-along-california-coast')],
         evidence='Govorcin: JPL/Caltech scientist and lead author, in a JPL–NOAA team (NASA release as quoted); byline '
                  'not seen.',
         does='Vertical land motion along the California coast is mapped at 90 m for 2015–2023 from Sentinel-1 InSAR and '
              'GNSS. Regional estimates such as those of IPCC AR6 understate it; in the fastest-sinking areas local sea '
              'level could rise by more than 45 cm by 2050, human-driven land motion adds up to 40 cm of uncertainty, and '
              'the Santa Barbara groundwater basin is rising.',
         sota='The highest-resolution coastal land motion built into sea-level projections.',
         gap='Not coupled to aquifer flow or salinity; the land motion is not used to infer aquifer parameters.',
         inputs='Land motion driven by the aquifer carries information on storage changes, hence on the skeletal storage '
                'and on the recharge that refills it.',
         dispersion='None.',
         bcs='Our sea boundary $\\eta(t)$ is the **relative** sea level: the sea surface minus the land motion at the '
             'coast. A tide gauge far away is a biased witness unless the local motion is added; Sentinel-1 covers '
             'the Albanian coast.',
         step='Write $\\eta=\\eta_{sea}-v$ with the land motion $v$ from InSAR as a second sea-boundary instrument. MATJA-GO '
              'then decides whether a local tide gauge, InSAR land motion or both are worth having for the toe, and the '
              'field check of the first review (Proposition 5) flags a land-motion drift as a shift of the prior.',
         steps=['prior', 'check', 'design'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='C4', inst='Caltech', year=2026, short='ClimaLand: soil water with EKI',
         title='ClimaLand: a land surface model designed to enable data-driven parameterizations',
         authors='Katherine Deck, Renato K. Braghiere, Alexandre A. Renchon, Julia Sloan, Gabriele Bozzola, et al.',
         venue='Journal of Advances in Modeling Earth Systems 18(1), e2025MS005118 (2026)',
         links=[('doi:10.1029/2025MS005118', 'https://doi.org/10.1029/2025MS005118'),
                ('CaltechAUTHORS', 'https://authors.library.caltech.edu/records/dctqh-4aa10')],
         evidence='Braghiere and Renchon: Caltech (CaltechAUTHORS record); sources disagree on the length of the author '
                  'list, so only the first five authors are given.',
         does='Version 1.0 of the land model of the Climate Modeling Alliance, with soil, canopy and snow, running natively '
              'on GPUs. The soil solves the mixed-form Richards equation in the unsaturated and saturated zones, with '
              'freezing and thawing; an ensemble Kalman inversion pipeline is built in, and the worked example calibrates '
              'photosynthesis and stomatal conductance, a soil-moisture stress function and the snow albedo.',
         sota='An open, GPU-native land model designed from the start for ensemble Kalman calibration and learned '
              'closures.',
         gap='Calibrated on surface fluxes, not on recharge or heads; no lateral groundwater flow and no saline coupling.',
         inputs='A Richards-equation column driven by the rain gives a physical recharge coefficient and vadose delay '
                '(our $\\kappa$ and $\\tau$) with an ensemble, in place of the lognormal prior of the test bed.',
         dispersion='None.',
         bcs='It produces the recharge series $r(t)$, the upper boundary of the aquifer, from the rain and the soil '
             'properties, including the threshold behaviour of dry years (B1).',
         step='Use the ClimaLand ensemble as the generator of recharge for the simulated aquifers of GARANCIA-GO and '
              'MATJA-GO: the guarantees then cover the soil-physics uncertainty, and the same ensemble Kalman tooling '
              'inverts the heads.',
         steps=['prior', 'invert'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='C5', inst='Caltech', year=2024, short='SWOT wide-swath altimetry',
         title='The Surface Water and Ocean Topography mission: a breakthrough in radar remote sensing of the ocean and '
               'land surface water',
         authors='Lee-Lueng Fu, Tamlin Pavelsky, et al. (11 authors)',
         venue='Geophysical Research Letters 51(4), e2023GL107652 (2024)',
         links=[('doi:10.1029/2023GL107652', 'https://doi.org/10.1029/2023GL107652'),
                ('DOAJ record', 'https://doaj.org/article/f1da682e023445ee92b57cd16da3d7ce')],
         evidence='Fu: JPL/Caltech, SWOT project scientist (JPL press kit); the given names of the other co-authors were not '
                  'checked.',
         does='First results of SWOT, launched in December 2022, over oceans, rivers and lakes: two-dimensional sea '
              'surface elevation at the resolution of radar imagery, in all weather, and water levels of rivers and '
              'lakes.',
         sota='Wide-swath altimetry: two-dimensional water levels of the coastal sea and of inland waters from space.',
         gap='A repeat orbit gives a level every few weeks, not the continuous record of a tide logger; near-shore '
             'accuracy was not shown in the sources.',
         inputs='None.',
         dispersion='None.',
         bcs='Free levels of the coastal sea, of lagoons and of rivers, the water bodies that bound many Mediterranean '
             'coastal aquifers.',
         step='Add a SWOT-like instrument (one sea level every 21 days, larger noise) to the candidates and let MATJA-GO '
              'price free but sparse altimetry against a local tide gauge. Our test gives the answer for the recharge, '
              'the inflow and $\\kappa$ with rain only: a sea-level record is worth nothing there, and the raw ensemble '
              'even calls it useful (Proposition M3); it pays only when the goal is the sea boundary or the toe.',
         steps=['design'], informs=dict(inputs=0, dispersion=0, bcs=2)),
]

BERKELEY = [
    dict(id='B1', inst='Berkeley', year=2022, short='Rock moisture gates recharge',
         title='Bedrock vadose zone storage dynamics under extreme drought: consequences for plant water availability, '
               'recharge, and runoff',
         authors='W. Jesse Hahm, David N. Dralle, Maryn Sanders, Alexander B. Bryk, Kristen E. Fauria, et al. (13 authors, '
                 'with William E. Dietrich and Daniella M. Rempe)',
         venue='Water Resources Research 58(4), e2021WR031781 (2022)',
         links=[('doi:10.1029/2021WR031781', 'https://doi.org/10.1029/2021WR031781'),
                ('UC Berkeley PDF', 'https://angelo.berkeley.edu/wp-content/uploads/sites/59/hahm_bedrock_vadose_storage.pdf'),
                ('NSF PAR', 'https://par.nsf.gov/biblio/10420132')],
         evidence='Bryk and Fauria: UC Berkeley (preprint record); the PDF is hosted by UC Berkeley\'s Angelo reserve. The '
                  'author order is that of the preprint.',
         does='Deep boreholes track rock moisture under a Mediterranean oak savanna in California. In the wet water year '
              '2019 (647 mm of rain) the rock moisture refilled quickly to a characteristic storage capacity. In the '
              'drought of 2020–21 the winter gains were only about 54 and 20 mm: the rain never exceeded the capacity, so '
              'there was no recharge and no runoff, and the oaks rooted in the bedrock showed stress and dieback.',
         sota='Direct field evidence that the storage capacity of the vadose zone gates recharge in a Mediterranean '
              'climate.',
         gap='One hillslope in weathered bedrock, not an alluvial plain; no estimator of the capacity from rain alone and '
             'no link to a coastal aquifer.',
         inputs='The recharge coefficient is not a constant: recharge stays zero until the rain fills a storage deficit, '
                'so a capacity and a threshold should replace the fixed $\\kappa$, and part of the delay $\\tau$ is the '
                'time needed to fill the deficit.',
         dispersion='None.',
         bcs='A rain-only recharge law must allow zero recharge in a dry year. This explains why the first review found '
             '$\\kappa$ twice as hard to pin down in a dry year as in a wet one (T1R).',
         step='Replace the linear recharge law $r=\\kappa\\,(k_\\tau*P)+e$ by a threshold law $r=\\kappa\\,\\max(0,k_\\tau*P-\\delta)+e$ with an uncertain '
              'deficit $\\delta$ in the prior. The calibration on simulated aquifers then covers dry years, and MATJA-GO '
              'tells whether a soil-moisture probe, the witness of the deficit, is worth more than a head logger for the '
              'recharge goal.',
         steps=['prior', 'check'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='B2', inst='Berkeley', year=2020, short='250 000 coastal wells below sea level',
         title='Groundwater level observations in 250,000 coastal US wells reveal scope of potential seawater intrusion',
         authors='Scott Jasechko, Debra Perrone, Hansjörg Seybold, Ying Fan, James W. Kirchner',
         venue='Nature Communications 11, 3229 (2020)',
         links=[('doi:10.1038/s41467-020-17038-2', 'https://doi.org/10.1038/s41467-020-17038-2'),
                ('eScholarship PDF', 'https://escholarship.org/content/qt785598jv/qt785598jv.pdf'),
                ('ADS record', 'https://ui.adsabs.harvard.edu/abs/2020NatCo..11.3229J/abstract')],
         evidence='Kirchner: Department of Earth and Planetary Science, UC Berkeley (affiliation in the eScholarship PDF, '
                  'as quoted).',
         does='About 250 000 groundwater-level observations made since 2000 in wells within 10 km of the coast of the '
              'contiguous United States. Groundwater levels below sea level are common along more than 15% of the '
              'coastline, and landward hydraulic gradients affect more than 18% of the East Coast, more than 17% of the '
              'Gulf Coast and heavily pumped parts of the West Coast. Sea-level rise, subsidence and growing demand are '
              'expected to make this worse.',
         sota='The largest observational assessment of the potential for seawater intrusion from heads alone.',
         gap='A head below sea level is necessary but not sufficient for intrusion: no salinity, no density correction, '
             'no transition zone and no uncertainty quantification.',
         inputs='None.',
         dispersion='None.',
         bcs='The decisive observable is the head near the coast minus the sea level: its sign decides whether the sea '
             'boundary drives water inland. It needs well tops surveyed to the sea-level datum, possibly the cheapest '
             'high-value measurement there is.',
         step='A guaranteed sign test: with GARANCIA-GO bands for $h(x_c,t)-\\eta(t)$, declare a landward gradient only '
              'when the whole band is below zero. This is a calibrated version of the 250 000-well screening, and '
              'MATJA-GO decides whether surveying well tops or a tide gauge comes first.',
         steps=['check', 'design'], informs=dict(inputs=0, dispersion=0, bcs=2)),
    dict(id='B3', inst='Berkeley', year=2022, short='PyLEnM monitoring design',
         title='PyLEnM: a machine learning framework for long-term groundwater contamination monitoring strategies',
         authors='Aurelien O. Meray, Savannah Sturla, Masudur R. Siddiquee, Rebecca Serata, Sebastian Uhlemann, et al. '
                 '(11 authors, with Haruko M. Wainwright)',
         venue='Environmental Science & Technology 56(9), 5973–5983 (2022)',
         links=[('doi:10.1021/acs.est.1c07440', 'https://doi.org/10.1021/acs.est.1c07440'),
                ('eScholarship', 'https://escholarship.org/uc/item/45z6q6px'),
                ('code', 'https://github.com/ALTEMIS-DOE/pylenm')],
         evidence='Wainwright: Lawrence Berkeley National Laboratory; Sturla: UC Berkeley, Environmental Science, Policy '
                  'and Management (affiliation lines as quoted). A DSpace@MIT record also exists (Wainwright moved to MIT '
                  'in 2022).',
         does='An open Python pipeline for long-term groundwater monitoring: quality control, clustering of wells with '
              'similar dynamics, automatic choice of interpolation models (including proxy-based interpolation with '
              'spatial layers), and a well-optimisation algorithm that finds the subset of wells that best keeps the '
              'spatial-interpolation skill. It is demonstrated on the Savannah River Site F-Area (water table, pH, '
              'specific conductance, tritium, uranium).',
         sota='The open, practice-ready reference for the data-driven reduction of a groundwater monitoring network.',
         gap='It chooses among existing wells by interpolation skill, without physics, without a guarantee on the '
             'uncertainty removed, and it cannot value a new kind of instrument (a tide gauge, a salinity profile).',
         inputs='Clustering the head records by their dynamics separates zones of transmissivity and of recharge '
                'response.',
         dispersion='None: specific conductance is mapped, not read as dispersion.',
         bcs='None directly.',
         step='Keep the pipeline and change the score: replace the interpolation skill by the guaranteed half-width '
              '$W(D)$ of the goal (recharge, inflow, $\\kappa$, toe) and recalibrate on fresh simulated aquifers after the '
              'selection (Proposition M1). The keep-or-drop ranking then carries a finite-sample guarantee.',
         steps=['design'], informs=dict(inputs=1, dispersion=0, bcs=0)),
    dict(id='B4', inst='Berkeley', year=2022, short='Zonation that guides where to measure',
         title='Watershed zonation through hillslope clustering for tractably quantifying above- and below-ground '
               'watershed heterogeneity and functions',
         authors='H. M. Wainwright, S. Uhlemann, M. Franklin, N. Falco, N. J. Bouskill, et al. (11 authors, with S. S. '
                 'Hubbard)',
         venue='Hydrology and Earth System Sciences 26(2), 429–444 (2022)',
         links=[('doi:10.5194/hess-26-429-2022', 'https://doi.org/10.5194/hess-26-429-2022'),
                ('HESS article', 'https://hess.copernicus.org/articles/26/429/2022/'),
                ('OSTI record', 'https://www.osti.gov/pages/biblio/1842887')],
         evidence='Listed by the Watershed Function project of Lawrence Berkeley National Laboratory and in OSTI as '
                  'DOE-supported LBNL work; the affiliation lines were not seen.',
         does='Unsupervised clustering (K-means, hierarchical and Gaussian mixtures give similar zones) of airborne lidar, '
              'hyperspectral and airborne electromagnetic data, with satellite and streamflow data, for the East River '
              'watershed in Colorado. Hillslope-averaged metrics capture most of the variability; the resistivity of the '
              'top 20 m of bedrock follows the topography; the zones predict drought sensitivity and nitrogen export and '
              'are proposed for choosing where to measure and for model parameterisation.',
         sota='The reference method for zonation from airborne electromagnetics and remote sensing, used to guide where '
              'to measure.',
         gap='The zones are not optimised for a prediction goal; no salinity, no guarantee, and a mountain watershed.',
         inputs='It reduces the conductivity and recharge fields to a few zone parameters: the few unknowns that a '
                'small-data ensemble needs.',
         dispersion='Indirect: at a coast the resistivity is dominated by salinity (Archie\'s law), so an airborne survey '
                    'is a witness of the transition zone, not of the conductivity.',
         bcs='Recharge parameters per zone, $\\kappa_z$ and $\\tau_z$.',
         step='Make the zonation goal-oriented: merge two zones only if the guaranteed width of the goal does not grow, '
              'and take one candidate logger per zone. On a coast, treat the airborne survey as a candidate instrument for '
              'the width $w$ of the transition zone, priced by MATJA-GO like any other.',
         steps=['prior', 'design'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='B5', inst='Berkeley', year=2024, short='Hard PDE constraints, mixture of experts',
         title='Scaling physics-informed hard constraints with mixture-of-experts',
         authors='Nithin Chalapathi, Yiheng Du, Aditi S. Krishnapriyan',
         venue='International Conference on Learning Representations (ICLR 2024); arXiv:2402.13412',
         links=[('arXiv:2402.13412', 'https://arxiv.org/abs/2402.13412')],
         evidence='UC Berkeley (arXiv and ICLR listings as quoted; code under the ASK-Berkeley GitHub organisation).',
         does='Hard PDE constraints in neural solvers are costly in compute and memory. PI-HC-MoE splits the enforcement '
              'over sub-domains: each expert solves its part by differentiable optimisation, in parallel, and a router '
              'assembles the global solution. On one-dimensional diffusion–sorption and two-dimensional turbulent '
              'Navier–Stokes it has lower error than soft constraints and than one global hard constraint.',
         sota='Scalable exact enforcement of PDE constraints inside learned solvers.',
         gap='No variable-density coupling, no uncertainty quantification and no field data.',
         inputs='None directly.',
         dispersion='Diffusion–sorption is a solute-transport equation: a surrogate of salt transport that conserves mass '
                    'exactly, so that its errors cannot pose as extra dispersion.',
         bcs='Hard constraints can impose the boundary values exactly in a surrogate (our inference), so reconstructed '
             'sea levels and inflows enter it without leakage.',
         step='MATJA-GO needs hundreds of designs times hundreds of simulated aquifers, hence a fast solver. With a '
              'hard-constrained surrogate the calibration has to absorb only the remaining surrogate error, and that '
              'error is covered by the conformal step on simulated truths, so the guarantee survives the speed-up.',
         steps=['emulate'], informs=dict(inputs=0, dispersion=1, bcs=1)),
]

MIT = [
    dict(id='M1', inst='MIT', year=2025, short='Guaranteed spatial inference',
         title='Smooth sailing: Lipschitz-driven uncertainty quantification for spatial association',
         authors='David R. Burt, Renato Berlinghieri, Stephen Bates, Tamara Broderick',
         venue='Advances in Neural Information Processing Systems 38 (NeurIPS 2025); arXiv:2502.06067',
         links=[('arXiv:2502.06067', 'https://arxiv.org/abs/2502.06067')],
         evidence='All four authors at MIT LIDS (arXiv listing as quoted).',
         does='Frequentist confidence intervals for spatial associations (the regression effect of a spatial covariate) '
              'that assume only spatial smoothness (a Lipschitz condition) and homoskedastic Gaussian noise, and need '
              'neither a correct model nor overlap between the sampled and the target locations. The authors report it '
              'as the first method with nominal coverage in this setting, where existing methods fail under '
              'misspecification and non-random locations.',
         sota='The first coverage guarantee for spatial inference at locations without data.',
         gap='Linear associations, not predictions of a PDE simulator; Gaussian homoskedastic noise; no design step.',
         inputs='Honest intervals for the effect of a covariate (recharge, distance to the sea) on heads or chloride at '
                'unsampled sites.',
         dispersion='None.',
         bcs='None directly.',
         step='Its bias bound grows with the distance between sampled and target sites (our reading), which gives a '
              'design rule: put the next logger where the guaranteed interval shrinks most. MATJA-GO does this for a '
              'simulator instead of a regression, with the calibration on simulated aquifers in place of the Lipschitz '
              'constant.',
         steps=['guarantee', 'design'], informs=dict(inputs=1, dispersion=0, bcs=0)),
    dict(id='M2', inst='MIT', year=2026, short='Global recharge: satellites + emulator',
         title='Integrating satellite retrievals, numerical models, and machine learning for global groundwater recharge '
               'estimation',
         authors='M. E. Soylu, D. Entekhabi, R. L. Bras',
         venue='Water Resources Research 62(3), e2025WR040312 (2026)',
         links=[('doi:10.1029/2025WR040312', 'https://doi.org/10.1029/2025WR040312'),
                ('MIT Climate project', 'https://impactclimate.mit.edu/global-mapping-of-groundwater-recharge-and-sustainable-aquifer-water-withdrawals/')],
         evidence='Entekhabi: MIT faculty; the MIT Climate and Sustainability Consortium page lists his project mapping '
                  'global recharge from SMAP. The byline affiliations were not seen.',
         does='Hydrus-1D, a numerical model of the unsaturated zone, simulates the soil water fluxes; a Gaussian-process '
              'regression emulates it from SMAP soil moisture, GPM precipitation, ERA5 reanalysis and soil hydraulic '
              'properties; the recharge estimates are checked against GRACE storage changes. Rainfall, unsaturated '
              'conductivity and soil moisture are the strongest predictors, and the skill is weaker in arid and '
              'irrigated areas.',
         sota='Global diffuse recharge from satellites with unsaturated-zone physics and a learned emulator.',
         gap='No uncertainty guarantee, weaker skill in dry and irrigated land (the Fushë-Kuqe plain is irrigated), and a '
             'coarse scale.',
         inputs='A satellite-based prior for the recharge coefficient, with the unsaturated-zone physics giving the '
                'delay.',
         dispersion='None.',
         bcs='It turns rain plus SMAP soil moisture into a recharge series: exactly our boundary condition known only '
             'through rain, with a second, free witness (soil moisture).',
         step='Put the emulator\'s recharge in the prior and calibrate it on simulated aquifers (GARANCIA-GO), and add '
              'SMAP soil moisture as a free candidate instrument for MATJA-GO. A free instrument with a negative '
              'guaranteed value, possible by Proposition M3, should still be left out.',
         steps=['prior', 'emulate'], informs=dict(inputs=2, dispersion=0, bcs=2)),
    dict(id='M3', inst='MIT', year=2024, short='Value of local data in tank experiments',
         title='Direct comparison of numerical simulations and experiments of CO₂ injection and migration in geologic '
               'media: value of local data and forecasting capability',
         authors='L. Saló-Salgado, M. Haugen, K. Eikehaug, M. Fernø, J. M. Nordbotten, R. Juanes',
         venue='Transport in Porous Media 151(5), 1199–1240 (2024); arXiv:2301.08875',
         links=[('doi:10.1007/s11242-023-01972-y', 'https://doi.org/10.1007/s11242-023-01972-y'),
                ('arXiv:2301.08875', 'https://arxiv.org/abs/2301.08875')],
         evidence='Saló-Salgado and Juanes: MIT (DSpace@MIT record hdl 1721.1/154227, as quoted).',
         does='CO₂ is injected into metre-scale, quasi-two-dimensional tanks and the experiments are compared with '
              'history-matched simulations. The models reproduce plume migration and convective mixing qualitatively and '
              'are accurate during injection, but agreement falls with time; results are very sensitive to the effective '
              'permeability and the capillary pressure; local data shorten the history matching, but the forecast skill '
              'stays about the same.',
         sota='The most rigorous laboratory test of history matching for density-driven flow in porous media.',
         gap='Deterministic: no uncertainty quantification and no design of measurements; CO₂–brine, not seawater.',
         inputs='Permeability dominates the forecast, so it must be measured or tightly constrained.',
         dispersion='Density-driven convective mixing is the hardest part to forecast, and its errors grow after the '
                    'forcing stops.',
         bcs='None directly.',
         step='More local data did not buy a better forecast: data must be chosen by their value for the forecast, not '
              'for the fit. MATJA-GO makes this precise: the value of an instrument is the guaranteed width of the '
              'forecast goal it removes, and it can be zero or negative (Proposition M3).',
         steps=['check', 'design'], informs=dict(inputs=2, dispersion=1, bcs=0)),
    dict(id='M4', inst='MIT', year=2024, short='Forecasters are overconfident',
         title='Experimentally assessing the uncertainty of forecasts of geological carbon storage',
         authors='Jan M. Nordbotten, Martin A. Fernø, Bernd Flemisch, Ruben Juanes, Magne Jørgensen',
         venue='International Journal of Greenhouse Gas Control 135 (2024)',
         links=[('ScienceDirect', 'https://www.sciencedirect.com/science/article/pii/S1750583624001051'),
                ('MIT ERL', 'https://erlweb.mit.edu/announcements/experimentally-assessing-uncertainty-forecasts-geological-carbon-storage')],
         evidence='Juanes: MIT (Civil and Environmental Engineering, EAPS); announced by MIT\'s Earth Resources '
                  'Laboratory. The article number was not verified.',
         does='A five-day laboratory CO₂-storage experiment (FluidFlower) is the ground truth of a double-blind forecasting '
              'exercise. Expert groups forecast storage metrics on their own, then again after workshops and with other '
              'ways of framing uncertainty. The forecasts were unbiased, but their uncertainty intervals were too narrow '
              'to contain the truth; the participants\' written comments showed they knew the task was hard, yet their '
              'numbers did not reflect it.',
         sota='The first controlled measurement of whether forecast intervals in density-driven porous-media flow are '
              'calibrated.',
         gap='It diagnoses overconfidence but offers no remedy and no design of measurements.',
         inputs='Expert ranges for permeability, mixing and forcing are too narrow: priors elicited from experts need '
                'widening or calibration.',
         dispersion='Mixing-dominated metrics were among the forecasts whose intervals missed the truth.',
         bcs='The same overconfidence applies to boundary forcing chosen by judgment.',
         step='The remedy is the calibration on simulated truths of GARANCIA-GO, and its design version MATJA-GO: the '
              'factor $\\hat\\lambda_D/1.645$ is exactly the inflation that makes a design\'s band honest, measured '
              'rather than guessed (Remark M2). A FluidFlower-type benchmark with known truth is the ideal external test.',
         steps=['guarantee', 'check'], informs=dict(inputs=1, dispersion=1, bcs=1)),
    dict(id='M5', inst='MIT', year=2020, short='Dispersion is not a constant',
         title='Chemotaxis under flow disorder shapes microbial dispersion in porous media',
         authors='Pietro de Anna, Amir A. Pahlavan, Yutaka Yawata, Roman Stocker, Ruben Juanes',
         venue='Nature Physics (published online 14 September 2020)',
         links=[('doi:10.1038/s41567-020-1002-x', 'https://doi.org/10.1038/s41567-020-1002-x'),
                ('data (Zenodo)', 'https://zenodo.org/records/3926720')],
         evidence='Juanes: MIT faculty, paper listed on his MIT CV; the byline, the volume and the pages were not seen.',
         does='A microfluidic porous medium reproduces pore-scale flow disorder and chemical gradients. Tracking '
              '*Bacillus subtilis* shows that chemotaxis controls how long the bacteria stay in the low-flow pores, which '
              'doubles their dispersion coefficient.',
         sota='Pore-scale, experimentally resolved control of dispersion by flow disorder.',
         gap='Microscale and an active tracer; no link to the width of field transition zones or to inversion.',
         inputs='None.',
         dispersion='Dispersion is not a material constant: it depends on the low-velocity regions of the pore space and '
                    'on the flow. Chloride is passive, but the lesson stands: treat the dispersivity as uncertain and '
                    'scale-dependent, never as a fixed number.',
         bcs='None.',
         step='Give the simulated aquifers a dispersivity that varies with velocity and scale, not one value, so the '
              'guaranteed chloride bands carry the structural uncertainty of dispersion; MATJA-GO then prices a depth '
              'profile of conductivity, the only witness of it (first review, Proposition 6).',
         steps=['prior'], informs=dict(inputs=0, dispersion=2, bcs=0)),
]

INST_ORDER = ('Oxford', 'Caltech', 'Berkeley', 'MIT')


def all_cards():
    return OXFORD + CALTECH + BERKELEY + MIT


CARDS = all_cards()
