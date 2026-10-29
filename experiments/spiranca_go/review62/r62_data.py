"""Data for review 62. Every paper was checked (authors, year, journal, DOI, institution) through search results that
index the publisher or institutional repository pages; gaps are stated in the entry itself."""

TITLE = 'Earthquakes, Groundwater and Surface Deformation in Coastal Aquifers'
SUBTITLE = ('Review 62: 30 papers from Caltech, MIT, Harvard and Oxford (2020–2026), what each adds to our coastal system, '
            'and the innovation that follows')

INTRO = [
    'A coastal aquifer is one coupled system. Pumping lowers the heads; the clay and silt layers compact; the land subsides; '
    'the sea rises relative to the land at the coastline; and the saline wedge advances. Earthquakes act on the same chain '
    'from the other side: they change pore pressure and permeability in seconds, move the land up or down, and their '
    'aftershocks and slow slip can go on for months. Fluids, in turn, change when and where earthquakes happen.',
    'This matters directly for the Adriatic coast. The Fushë-Kuqe plain lies near the epicentral area of the 26 November '
    '2019 Mw 6.4 Durrës earthquake, and its well field pumps from layered alluvium of exactly the kind that compacts. '
    'The 30 papers below (Caltech 12, MIT 7, Harvard 7, Oxford 4) are grouped by the four links of the chain. For each: '
    'where to download it, the key finding, and what is new for our coastal system. Links are clickable.',
]

GROUPS = [
    ('A. Groundwater → surface deformation: what InSAR and GNSS tell us about the aquifer', [
        dict(n=1, inst='Caltech (Seismological Laboratory)',
             cite='Zheng, Y. and Simons, M. (2025). Integrating long-term InSAR monitoring into local groundwater management: insights from the Hollywood Basin, California. Water Resources Research 61(11), e2024WR039161.',
             doi='https://doi.org/10.1029/2024WR039161', free='https://essopenarchive.org/doi/full/10.22541/essoar.173046635.57543794/v1', free_label='ESS Open Archive preprint',
             finding='About 30 years of InSAR (1992–2023) combined with pumping records give a sustainable yield of 1.44–1.67 million m³/yr, less than half the basin\'s current operating safe yield of 3.70 million m³/yr. The ground rebounds when pumping stops and subsides when it resumes; most of the aquifer is elastic, with permanent compaction near the production wells. ICA separates the deep and shallow aquifer signals, without water-level data.',
             new='A sustainable pumping limit can be set from satellites alone, which suits a well field with few piezometers. For us the limit has a second meaning: a pumping rate the land can sustain without permanent compaction is also a rate that does not add to relative sea-level rise at the coast.'),
        dict(n=2, inst='Caltech (Avouac group)',
             cite='Larochelle, S., Chanard, K., Dalaison, M., Fortin, J., et al., including Avouac, J.-P. (2026). Abrupt transition to irreversible damage in the overdrafted Sacramento Valley aquifer system. Proceedings of the National Academy of Sciences 123(31), e2526041123.',
             doi='https://doi.org/10.1073/pnas.2526041123', free='https://authors.library.caltech.edu/records/hjp15-k0645', free_label='CaltechAUTHORS record',
             finding='InSAR, GNSS and well data (2016–2022) show large parts of the valley switching abruptly from reversible to irreversible compaction during the 2020–2022 drought; in heavily pumped areas subsidence in 2021 exceeded the elastic rate by several decimetres per year, a permanent loss of storage. The well network alone did not reveal the switch; the authors propose space geodesy as an early warning.',
             new='Drought plus pumping can cross a threshold beyond which the clays are damaged for good. In our model the same clay layers hold the slow salt memory, so the threshold is also a candidate trigger for a change in how much salt the clays release. It gives the drought storylines of review 61 a physical tipping point to watch for.'),
        dict(n=3, inst='Caltech (GPS Division)',
             cite='Larochelle, S., Chanard, K., Fleitout, L., Fortin, J., Gualandi, A., Longuevergne, L., Rebischung, P., Violette, S. and Avouac, J.-P. (2022). Understanding the geodetic signature of large aquifer systems: example of the Ozark Plateaus in central United States. Journal of Geophysical Research: Solid Earth 127(3), e2021JB023097.',
             doi='https://doi.org/10.1029/2021JB023097', free='https://resolver.caltech.edu/CaltechAUTHORS:20211012-211827889', free_label='CaltechAUTHORS (PDF)',
             finding='The method separates poroelastic GNSS displacement caused by groundwater from the elastic response to the weight of water (hydrological loading): ICA of piezometer records, then projection of loading-corrected GNSS series onto the groundwater time functions. The aquifer shows significant, highly heterogeneous poroelastic motion and low elastic moduli, read as strongly fractured layers.',
             new='Before any GNSS or InSAR signal near the coast is used to calibrate the aquifer, the loading part must be removed. The method gives the recipe, and the elastic moduli it returns are the storage parameters our flow model needs.'),
        dict(n=4, inst='Caltech (Division of Geological and Planetary Sciences)',
             cite='Li, Y., Acosta, M., Sirorattanakul, K., Bourne, S. and Avouac, J.-P. (2025). Geodetic monitoring of elastic and inelastic deformation in compacting reservoirs due to subsurface operations. Journal of Geophysical Research: Solid Earth 130(3), e2024JB030794.',
             doi='https://doi.org/10.1029/2024JB030794', free='https://authors.library.caltech.edu/records/vbhry-09e90', free_label='CaltechAUTHORS record',
             finding='InSAR, GNSS and levelling (2009–2022) over the Groningen and Norg gas fields: Groningen shows decadal subsidence whose rate follows local compressibility, with inelastic compaction up to about 20% of the total by 2021; Norg shows a 20 mm seasonal cycle over 5×5 km that tracks gas-storage cycles, with no inelastic part.',
             new='A seasonal cycle of injection and withdrawal leaves an elastic, reversible signature; a long one-way withdrawal leaves a permanent one. Seasonal pumping at a coastal well field should therefore show up as a seasonal ground cycle, a cheap test of whether the field is still in the elastic range.'),
        dict(n=5, inst='Caltech (Avouac)',
             cite='Chanard, K., Métois, M., Rebischung, P. and Avouac, J.-P. (2020). A warning against over-interpretation of seasonal signals measured by the Global Navigation Satellite System. Nature Communications 11, 1375.',
             doi='https://doi.org/10.1038/s41467-020-15100-7', free='https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7070017/', free_label='PubMed Central (free)',
             finding='Seasonal GNSS transients attributed to hydrologically modulated slip on the Himalayan megathrust can also be produced by local non-tectonic sources: thermoelastic deformation of monuments and bedrock, poroelastic deformation where water tables swing strongly, and GNSS systematic errors.',
             new='On a sedimentary coastal plain, a seasonal GNSS signal is first a groundwater signal, not a tectonic one. Any attempt to read tectonic or slow-slip motion near Durrës from coastal GNSS has to model the aquifer first; the aquifer model is the correction.'),
    ]),
    ('B. Seismic and fibre-optic monitoring of groundwater', [
        dict(n=6, inst='MIT (EAPS)',
             cite='Mao, S., Lecointre, A., van der Hilst, R.D. and Campillo, M. (2022). Space-time monitoring of groundwater fluctuations with passive seismic interferometry. Nature Communications 13, 4643.',
             doi='https://doi.org/10.1038/s41467-022-32194-3', free='https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9360030/', free_label='PubMed Central (free)',
             finding='Ambient-noise interferometry gives space-time maps of seismic velocity change (dv/v) for basins near Los Angeles over 2000–2020. Velocity follows the water tables measured in wells and the satellite-measured deformation, with better time and depth resolution; neighbouring basins show opposite long-term trends tied to each district\'s pumping.',
             new='Seismic noise is a free, continuous, depth-resolved groundwater sensor. Where piezometers are sparse, dv/v from existing seismic stations can fill the gaps between wells, and it is an observation type our goal-oriented design can value like a new well.'),
        dict(n=7, inst='Harvard (Earth and Planetary Sciences)',
             cite='Clements, T. and Denolle, M.A. (2023). The seismic signature of California\'s earthquakes, droughts, and floods. Journal of Geophysical Research: Solid Earth 128(1), e2022JB025553.',
             doi='https://doi.org/10.1029/2022JB025553', free='https://eartharxiv.org/repository/view/4658/', free_label='EarthArXiv preprint',
             finding='dv/v at about 700 stations across California (1999–2021), from single-station noise at 2–4 Hz sampling roughly the top 500 m. The wet winter of 2004–05 gives the largest drop, droughts give multiyear rises (2011–2016 stands out), hydraulic diffusivity is high in mountains and low in basins, site variations match remote-sensed subsidence and uplift, and two large earthquakes leave a decade-long postseismic signal.',
             new='One seismic record carries three signals at once: recharge, drought and earthquake damage. Separating them gives the hydraulic diffusivity of the basin, a parameter we otherwise estimate only from a few pumping tests, and the earthquake part tells how long a coseismic change in the aquifer lasts.'),
        dict(n=8, inst='Caltech (Seismological Laboratory)',
             cite='Shen, Z., Yang, Y., Fu, X., Adams, K.H., Biondi, E. and Zhan, Z. (2024). Fiber-optic seismic sensing of vadose zone soil moisture dynamics. Nature Communications 15, 6432.',
             doi='https://doi.org/10.1038/s41467-024-50690-6', free='https://www.nature.com/articles/s41467-024-50690-6', free_label='open access (journal)',
             finding='Distributed acoustic sensing on about 10 km of unused telecom fibre at Ridgecrest uses traffic noise to track near-surface velocity changes from water over about 5 years, resolving wet-season recharge pulses and the 2019–2022 drought, when the vadose zone lost about 0.25 m/yr of water, consistent with nearby evapotranspiration measurements.',
             new='Recharge, the term heads alone cannot separate from model error, can be watched directly in the unsaturated zone along an existing fibre. A dark fibre along a coastal road would give a recharge sensor many kilometres long.'),
        dict(n=9, inst='MIT (Earth Resources Laboratory; Nakata)',
             cite='Qin, L., Steidl, J.H., Qiu, H., Nakata, N. and Ben-Zion, Y. (2022). Monitoring seasonal shear wave velocity changes in the top 6 m at Garner Valley in Southern California with borehole data. Geophysical Research Letters 49, e2022GL101189.',
             doi='https://doi.org/10.1029/2022GL101189', free='https://www.osti.gov/pages/biblio/1903071', free_label='OSTI record',
             finding='Borehole earthquake data (2005–2018) and cross-hole data (2015–2018) show shear-wave velocity varying by about 25% in the top 6 m and about 10% at 2–5 m, closely following the depth of the water table through pore pressure in the shallow soil.',
             new='The water table controls how strongly the ground shakes. On a coastal plain where pumping and the seasons move the water table, earthquake site response and liquefaction risk change with the season and with the pumping, a link between groundwater management and seismic hazard.'),
        dict(n=10, inst='MIT (EAPS; Frank group)',
             cite='Wang, Q.-Y., Cui, X., Frank, W.B., Lu, Y., Hirose, T. and Obara, K. (2024). Untangling the environmental and tectonic drivers of the Noto earthquake swarm in Japan. Science Advances 10, eado1469.',
             doi='https://doi.org/10.1126/sciadv.ado1469', free='https://par.nsf.gov/servlets/purl/10505998', free_label='NSF repository (PDF)',
             finding='Eleven years of seismic velocity changes show a long-term rise modulated by the seasons that dropped before the swarm began in late 2020. A 3-D hydromechanical model driven by snow, rain and sea level links the seasonal signal to pore pressure (stress sensitivity 6 × 10⁻⁹ Pa⁻¹); the drop tracks surface uplift, read as fluid rising from depth, and stress from unusually heavy snowfall appears to have helped trigger the swarm.',
             new='Sea level, rain and snow enter one poroelastic model of a coastal crust together with the seismic data. That is the same forcing our variable-density model already uses at the sea boundary, so the two models can share their boundary conditions.'),
        dict(n=11, inst='MIT (EAPS; Frank group)',
             cite='Bryan, Frank, W.B. and Audet (2025). Crustal stresses and damage evolve throughout the seismic cycle of the Ridgecrest fault zone. Science 389(6766), 1256–1260. (First names of Bryan and Audet not confirmed.)',
             doi='https://doi.org/10.1126/science.adu9116', free=None, free_note='paywalled, no free copy found',
             finding='Receiver functions analysed with optimal transport before and after the 2019 Ridgecrest earthquakes show shallow coseismic wavespeed drops recovering within months, but a deeper postseismic drop persisting for years without measurable recovery, read as accumulated damage.',
             new='It tells shallow, water-controlled velocity changes apart from deep, tectonic ones. Any dv/v monitoring of a coastal aquifer near an active fault needs exactly this separation, or an earthquake will be mistaken for a fall in the water table.'),
        dict(n=12, inst='Oxford (Department of Earth Sciences)',
             cite='Hudson, T.S., Kendall, J.-M., Blundy, J.D., Pritchard, M.E., MacQueen, P., Wei, S.S., et al. (2023). Hydrothermal fluids and where to find them: using seismic attenuation and anisotropy to map fluids beneath Uturuncu volcano, Bolivia. Geophysical Research Letters 50(5), e2022GL100974.',
             doi='https://doi.org/10.1029/2022GL100974', free='https://doi.org/10.1029/2022GL100974', free_label='open access (journal)',
             finding='1,356 earthquakes on 33 stations: P- and S-wave attenuation, their ratio and anisotropy separate partly from fully fluid-saturated crust, show fluids gathering along faults and fractures, and resolve dry zones, H₂O/brine zones and a deeper supercritical brine column.',
             new='Attenuation separates saturated from partly saturated rock and fresh water from brine. Applied at the scale of a coastal aquifer, the same attributes could map where the fractured or gravel layers carry saline water, a geophysical prior for the position of the wedge.'),
    ]),
    ('C. Fluids, pore pressure and earthquakes', [
        dict(n=13, inst='Caltech (Seismological Laboratory)',
             cite='Ross, Z.E. and Cochran, E.S. (2021). Evidence for latent crustal fluid injection transients in Southern California from long-duration earthquake swarms. Geophysical Research Letters 48(12), e2021GL092465.',
             doi='https://doi.org/10.1029/2021GL092465', free='https://resolver.caltech.edu/CaltechAUTHORS:20210610-133645643', free_label='CaltechAUTHORS (PDF)',
             finding='A deep-learning catalogue (2008–2020) finds 92 swarms lasting 6 months to 7 years, 26.4% of all seismicity, and about 53% migrate slowly and diffusively with back-fronts, consistent with natural fluid injection: transient fluid pulses are a major part of crustal fluid transport.',
             new='Fluids in the crust move in pulses, and the pulses leave a seismic trace that can be dated. Pore-pressure diffusion fronts give a diffusivity, the same quantity that sets how fast a pressure change at the coast travels inland.'),
        dict(n=14, inst='Caltech (Seismological Laboratory)',
             cite='Ross, Z.E., Cochran, E.S., Trugman, D.T. and Smith, J.D. (2020). 3D fault architecture controls the dynamism of earthquake swarms. Science 368(6497), 1357–1361.',
             doi='https://doi.org/10.1126/science.abb0779', free='https://authors.library.caltech.edu/103963', free_label='CaltechAUTHORS record',
             finding='More than 22,000 events of the 2016–2019 Cahuilla swarm image a fault zone about 50 m wide; seismicity migrated from a point source at about 5 m/day, read as natural fluid injection along channels, and a permeability barrier slowed upward migration until it was bypassed.',
             new='Seismicity can image a permeability barrier and the moment it is breached. A clay layer separating fresh from saline water is a barrier of the same kind; the paper shows how its failure would look in the data.'),
        dict(n=15, inst='Caltech (Avouac and Ross groups)',
             cite='Sirorattanakul, K., Ross, Z.E., Khoshmanesh, M., Cochran, E.S., Acosta, M. and Avouac, J.-P. (2022). The 2020 Westmorland, California earthquake swarm as aftershocks of a slow slip event sustained by fluid flow. Journal of Geophysical Research: Solid Earth 127(11), e2022JB024693.',
             doi='https://doi.org/10.1029/2022JB024693', free='https://par.nsf.gov/servlets/purl/10393048', free_label='NSF repository (PDF)',
             finding='More than 2,000 earthquakes in a week followed a shallow Mw 5.2 slow-slip event seen by GNSS and InSAR 2–15 hours earlier; a rate-and-state model attributes 45–65% of the seismicity to the slow slip, 10–35% to earthquake interactions and 10–30% to fluids.',
             new='The causes of a seismic sequence can be split into shares, as we split the uncertainty of a chloride forecast by source. The Durrës sequence also had slow slip after the mainshock (see the local section), so the same split is possible there.'),
        dict(n=16, inst='Caltech (Avouac group)',
             cite='Acosta, M., Avouac, J.-P., Smith, J.D., Sirorattanakul, K., Kaveh, H. and Bourne, S.J. (2023). Earthquake nucleation characteristics revealed by seismicity response to seasonal stress variations induced by gas production at Groningen. Geophysical Research Letters 50(19), e2023GL105455.',
             doi='https://doi.org/10.1029/2023GL105455', free='https://gmg.caltech.edu/documents/29764/Acosta_2023.pdf', free_label='Caltech PDF',
             finding='Seismicity began about three decades after production started and responds to the seasonal production cycle with a damped, delayed response; models match only with an initial strength excess, a finite nucleation time and the seasonal variations. The seasonal response is proposed as a metric to calibrate forecasts.',
             new='A seasonal forcing and the delayed, damped response to it identify the hidden parameters of a slow system. The coastal aquifer has the same structure: a seasonal pumping cycle and a delayed, damped chloride response that identifies the memory of the clays.'),
        dict(n=17, inst='Caltech (Avouac group)',
             cite='Kaveh, H., Batlle, P., Acosta, M., Kulkarni, P., Bourne, S.J. and Avouac, J.-P. (2023). Induced seismicity forecasting with uncertainty quantification: application to the Groningen gas field. Seismological Research Letters (volume not confirmed).',
             doi='https://doi.org/10.1785/0220230179', free='https://gmg.caltech.edu/documents/29763/Kaveh_et_al_2023.pdf', free_label='Caltech PDF',
             finding='Reservoir, geomechanical and stress-based earthquake models are coupled (2-D finite-element reservoir model, semianalytical poroelastic stresses, rate-and-state nucleation), and the uncertainty in forecast earthquake counts and magnitudes is estimated with Poisson and Gaussian likelihoods.',
             new='A full chain from pumping to pressure to stress to a forecast with uncertainty bands, the same chain we run from pumping to head to chloride. The likelihood comparison is directly reusable for counting-type targets such as the number of seasons above 250 mg/L.'),
        dict(n=18, inst='Caltech (Avouac)',
             cite='Im, K., Avouac, J.-P., Heimisson, E.R. and Elsworth, D. (2021). Ridgecrest aftershocks at Coso suppressed by thermal destressing. Nature 595(7865), 70–74.',
             doi='https://doi.org/10.1038/s41586-021-03601-4', free='https://personal.ems.psu.edu/~fkd/publications/journals/2021_j_nature_ridgecrest_thermal_destress_kj.pdf', free_label='author PDF',
             finding='The Coso geothermal field should have hosted Ridgecrest aftershocks but hosted none: about 30 years of heat and fluid production had removed shear stress by thermal contraction, first inducing seismicity, then suppressing aftershock triggering.',
             new='Long human operation of a reservoir changes how the ground responds to a natural earthquake. A long-pumped coastal aquifer is likewise not in its natural state when an earthquake strikes; its response must be computed from the pumped state, not the undisturbed one.'),
        dict(n=19, inst='MIT (Civil and Environmental Engineering; Juanes)',
             cite='Alghannam, M. and Juanes, R. (2020). Understanding rate effects in injection-induced earthquakes. Nature Communications 11, 3053.',
             doi='https://doi.org/10.1038/s41467-020-16860-y', free='https://pmc.ncbi.nlm.nih.gov/articles/PMC7298001', free_label='PubMed Central (free)',
             finding='A poroelastic spring-slider with rate-and-state friction shows that triggering depends mainly on the rate of pore-pressure increase, not its size: for the same injected volume, an abrupt high-rate injection raises seismic risk and a gradual step-up lowers it.',
             new='How fast, not only how much. The same question applies to pumping: a sudden increase in abstraction produces sharper drawdown and upconing than the same volume ramped up. A rate limit on pumping changes is a cheap rule to test in our model.'),
        dict(n=20, inst='MIT (EAPS; Hager, Juanes), with Harvard co-authors',
             cite='Hager, B.H., Dieterich, J., Frohlich, C., Juanes, R., Mantica, S., Shaw, J.H., et al. (2021). A process-based approach to understanding and managing triggered seismicity. Nature 595(7869), 684–689.',
             doi='https://doi.org/10.1038/s41586-021-03668-z', free='https://dash.harvard.edu/entities/publication/adc38979-b6e2-4497-8a24-1eb5f75757d3', free_label='Harvard DASH record',
             finding='Subsurface data calibrate geomechanical and earthquake-physics models that are then checked against later observations; at the Val d\'Agri field in seismically active southern Italy this became a process-based management of injection that reduced triggered seismicity.',
             new='A Mediterranean, tectonically active case where a calibrated model, not a fixed rule, sets the operation. It is the template for operating a coastal well field in a seismic zone: calibrate, operate, check, recalibrate.'),
        dict(n=21, inst='MIT (Juanes)',
             cite='Silva, J.A., Khosravi, M., Yoon, H., Fehler, M., Frailey, S. and Juanes, R. (2024). Mechanisms for microseismicity occurrence due to CO₂ injection at Decatur, Illinois: a coupled multiphase flow and geomechanics perspective. Bulletin of the Seismological Society of America (volume not confirmed).',
             doi='https://doi.org/10.1785/0120230160', free='https://www.osti.gov/pages/biblio/2530864', free_label='OSTI record',
             finding='Coupled multiphase-flow and geomechanics modelling shows that pore-pressure diffusion along faults linking the injection interval to the basement is needed to explain microseismicity of Mw −2 to 1; poroelastic stress alone would have stabilised those faults, which were already close to failure.',
             new='The decisive physics was a connection between layers that the layered model lacked. For a coastal aquifer the analogue is a hidden vertical pathway through the clay; when the model cannot explain the data, a missing connection is a hypothesis to test first.'),
        dict(n=22, inst='Oxford (Kendall)',
             cite='Kettlety, T., Verdon, J.P., Werner, M.J. and Kendall, J.-M. (2020). Stress transfer from opening hydraulic fractures controls the distribution of induced seismicity. Journal of Geophysical Research: Solid Earth 125(1), e2019JB018794.',
             doi='https://doi.org/10.1029/2019JB018794', free='https://www1.gly.bris.ac.uk/~gljpv/PDFS/Kettlety_etal_2020_JGR.pdf', free_label='author PDF',
             finding='At Preston New Road (UK, 2018) seismicity clustered where hydraulic-fracture opening raised the Coulomb stress and stayed absent where it lowered it: elastic stress transfer works alongside fluid pressure.',
             new='Pressure and stress travel by different routes and at different speeds. In a layered aquifer, a pumping change acts at once through stress and slowly through pressure; the fast part explains why some piezometers react before the water could have reached them.'),
        dict(n=23, inst='Oxford (Kettlety, Kendall)',
             cite='Kettlety, T., Kendall, J.-M. and Roman, D.C. (2022). Self-similarity of seismic moment release to volume change scaling for volcanoes: a comparison with injection-induced seismicity. Geophysical Research Letters 49(23), e2022GL099369.',
             doi='https://doi.org/10.1029/2022GL099369', free='https://ora.ox.ac.uk/objects/uuid:ba60a07b-e5dc-4207-9780-82b645ff92af', free_label='Oxford ORA (free)',
             finding='Cumulative seismic moment against injected or intruded volume: volcanic sequences scale in a strikingly similar way, unlike human-induced sequences, so intruded volume could be estimated from seismicity without geodesy.',
             new='A scaling law between a volume of fluid and a measured response replaces a full model. The coastal counterpart is a scaling between abstracted volume and the measured land or chloride response, a quick check of whether a well field behaves like its neighbours.'),
        dict(n=24, inst='Oxford (Hudson, Kettlety, Kendall)',
             cite='Hudson, T.S., Kettlety, T., Kendall, J.-M., et al. (2024). Seismic node arrays for enhanced understanding and monitoring of geothermal systems. The Seismic Record 4(3), 161–171.',
             doi='https://doi.org/10.1785/0320240019', free='https://ora.ox.ac.uk/objects/uuid:9a5713b8-cfed-4ad9-baed-9ff3af6ba6bf', free_label='Oxford ORA (free)',
             finding='450 low-cost seismic nodes at a geothermal prospect in Cornwall track induced seismicity and the stress state; fracture orientations at the injection site differ from the crust above and from the regional stress, and agree with well logs.',
             new='A dense, cheap, temporary array answers a local question that a sparse permanent network cannot. For a coastal plain, a few weeks of nodes after an earthquake, or during a planned pumping change, would map the shallow response at the scale of the well field.'),
        dict(n=25, inst='Harvard (Meade), with Google Research',
             cite='Zlydenko, O., Elidan, G., Hassidim, A., Kukliansky, D., Matias, Y., Meade, B., Molchanov, A., Nevo, S. and Bar-Sinai, Y. (2023). A neural encoder for earthquake rate forecasting. Scientific Reports 13, 12350.',
             doi='https://doi.org/10.1038/s41598-023-38033-9', free='https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10390553/', free_label='PubMed Central (free)',
             finding='Learned space and time embeddings replace the fixed forms of the standard aftershock model (ETAS): more than 4% information gain per earthquake, fault-like patterns learned unaided and about 1,000-fold faster short-term forecasts.',
             new='A learned model is judged by information gain over a physical baseline, not by fit. It is the right test for any learned pumping or chloride forecaster we build: report its gain over the physics-based forecast, per season.'),
    ]),
    ('D. The coast: vertical land motion and sea level', [
        dict(n=26, inst='Harvard (Mitrovica), with Tulane and others',
             cite='Dangendorf, S., Oelsmann, J., Mitrovica, J.X., Törnqvist, T.E., Piecuch, C.G., Creel, R., Coronel, W., Thompson, P.R., Ebinger, C. and Wahl, T. (2026). Variable contributions of vertical land motion to sea-level change inferred at tide gauges. Nature Geoscience 19, 814–821.',
             doi='https://doi.org/10.1038/s41561-026-02005-1', free=None, free_note='paywalled; a free copy is due at par.nsf.gov in June 2027',
             finding='Vertical land motion at tide gauges worldwide, found by subtracting a reconstruction of climate-driven sea level (1900–2021), changes its rate over time, linked to groundwater and hydrocarbon withdrawal and to seismic and volcanic processes. Treating land motion as a straight-line trend gives median errors in sea-level projections of up to 7.6 mm/yr at seismic or volcanic sites and 5.6 mm/yr elsewhere; Venice is among the cases shown.',
             new='This is the whole chain in one paper: groundwater withdrawal and earthquakes both change the land motion that sets relative sea level at the coast. For our model the sea boundary must be relative sea level, climate rise plus measured, time-varying land motion, not a fixed trend. Venice gives the Adriatic precedent.'),
        dict(n=27, inst='Harvard (Mitrovica)',
             cite='Dangendorf, S., Sun, Q., Wahl, T., Thompson, P., Mitrovica, J.X. and Hamlington, B. (2024). Probabilistic reconstruction of sea-level changes and their causes since 1900. Earth System Science Data 16, 3471–3494.',
             doi='https://doi.org/10.5194/essd-16-3471-2024', free='https://essd.copernicus.org/articles/16/3471/2024/', free_label='open access (journal)',
             finding='A near-global probabilistic reconstruction of relative sea level and its causes for 1900–2021 from tide gauges and physical priors; global mean rise 1.5 ± 0.19 mm/yr since 1900, agreeing with altimetry and tide gauges only once local vertical land motion is included.',
             new='A free, probabilistic sea-level history with uncertainty, ready to drive the sea boundary of a coastal model in hindcast. Its regional output gives the climate part; local InSAR gives the land part.'),
        dict(n=28, inst='Harvard (Coulson, Mitrovica)',
             cite='Coulson, S., Lubeck, M., Mitrovica, J.X., Powell, E., Davis, J.L. and Hoggard, M.J. (2021). The global fingerprint of modern ice-mass loss on 3-D crustal motion. Geophysical Research Letters 48(16), e2021GL095477.',
             doi='https://doi.org/10.1029/2021GL095477', free='https://repository.arizona.edu/handle/10150/661888', free_label='University of Arizona repository (free)',
             finding='Mass loss from Greenland, Antarctica and glaciers (2003–2018) moves the crust far from the ice: Greenland and high-latitude glaciers each drive about 0.1–0.4 mm/yr across much of the Northern Hemisphere, often more horizontally than vertically.',
             new='Even a distant ice sheet moves a Mediterranean GNSS station by a fraction of a millimetre per year. Small compared with pumping-induced subsidence, but it must be removed before slow tectonic or aquifer motion is read from coastal GNSS.'),
        dict(n=29, inst='Harvard (Mitrovica)',
             cite='Coulson, S., Dangendorf, S., Mitrovica, J.X., Tamisiea, M.E., Pan, L. and Sandwell, D.T. (2022). A detection of the sea level fingerprint of Greenland Ice Sheet melt. Science 377(6614), 1550–1554.',
             doi='https://doi.org/10.1126/science.abo0926', free=None, free_note='paywalled, no free copy confirmed',
             finding='About three decades of satellite sea-surface height around Greenland, cleaned of ocean dynamics, correlate significantly (p < 0.001) with the predicted fingerprint of ice loss: the first unambiguous observation of the near-field fingerprint of recent melt.',
             new='Sea-level rise is not uniform: each melt source has its own spatial pattern. The sea-level rise to impose at the Adriatic boundary should come from the fingerprint-aware regional projection, not from the global mean.'),
        dict(n=30, inst='Harvard (Pan, Mitrovica)',
             cite='Pan, L., Powell, E.M., Latychev, K., Mitrovica, J.X., Creveling, J.R., Gomez, N., Hoggard, M.J. and Clark, P.U. (2021). Rapid postglacial rebound amplifies global sea level rise following West Antarctic Ice Sheet collapse. Science Advances 7(18), eabf7787.',
             doi='https://doi.org/10.1126/sciadv.abf7787', free='https://pmc.ncbi.nlm.nih.gov/articles/PMC8087405/', free_label='PubMed Central (free)',
             finding='With 3-D mantle structure and low-viscosity mantle under West Antarctica, rebounding marine basins push water out much faster than earlier estimates, adding about 1 m within about 1,000 years for a Last Interglacial collapse and raising projected rise over the next century.',
             new='The upper tail of sea-level projections is fatter than assumed. For the storylines of our objective function, the high sea-level storyline should be wider than a simple trend, which tightens the margins of any pumping rule designed to hold the wedge.'),
    ]),
]

LOCAL = [
    'Govorčin, Wdowinski, Matoš and Funning (2020). Geophysical Research Letters. Sentinel-1 InSAR and GNSS source model of the 2019 Durrës earthquake: a steep SW-dipping fault and a shallow NE-dipping fault fit about equally; the authors favour the SW-dipping one. https://doi.org/10.1029/2020GL088990',
    'Ganas et al. (2020). Geosciences 10(6), 210. A low-angle (23°) east-dipping fault with centroid at 16.5 km depth. https://doi.org/10.3390/geosciences10060210',
    'Matraku, Jouanne, Dushi, Koçi, Kuka, Grandin and Bascou (2023). Geophysical Journal International 234(2). Blind thrust at about 15 km, maximum slip about 1.4 m, and slow-slip events about 200 and 300 days after the mainshock. https://doi.org/10.1093/gji/ggad101',
    'van der Heiden et al. (2026). Geophysical Journal International 246(2). 19,152 aftershocks over nine months on NE-dipping blind faults at 12–18 km. https://doi.org/10.1093/gji/ggag155',
]

SYN_TITLE = 'Innovation: TRUALLI-GO, one ground–water–quake observation of the coastal aquifer'
SYNTHESIS = [
    ('p', 'The 30 papers say the same thing from four sides: the land, the groundwater, the sea and the earthquakes are '
          'measured by different communities, but they are one system and constrain the same parameters. TRUALLI-GO '
          '(truall = the ground) turns that into five additions to our model of the coastal aquifer, each with a source.'),
    ('h', '1. A new sea boundary: relative sea level, not sea level'),
    ('p', 'The sea boundary of the variable-density model becomes climate sea level (regional, fingerprint-aware: papers 27, '
          '29, 30) plus measured, time-varying land motion (InSAR/GNSS: papers 1–4, 26), with the ice-loss and loading '
          'parts removed (3, 5, 28). The classical Ghyben–Herzberg rule shows why it matters: in a head-controlled coastal '
          'aquifer each centimetre of relative sea-level rise lowers the fresh head above sea level by about a centimetre and '
          'raises the interface by about 40 cm (in a flux-controlled aquifer the effect is smaller). If the plain subsides at a rate comparable to climatic rise, the relative rise '
          'doubles. The subsidence rate of the Fushë-Kuqe plain is not known; it is the first thing to measure.'),
    ('h', '2. Storage and clay memory from the satellites'),
    ('p', 'InSAR time series with pumping records give the elastic storage of the aquifer, the inelastic (permanent) '
          'compaction and a pumping limit the land can sustain (papers 1–4). The inelastic part comes from the same clay '
          'layers that hold the slow salt memory in our model. Hypothesis to test: the switch to irreversible compaction '
          '(paper 2) also changes the rate at which the clays release salt, so a drought can leave a lasting chloride signal.'),
    ('h', '3. Seismic noise as a groundwater sensor in the goal-oriented design'),
    ('p', 'Seismic velocity change from ambient noise or fibre tracks the water table, recharge and drought with depth '
          'resolution (papers 6–10), once the deep tectonic part is separated (7, 11). In our goal-oriented design it '
          'becomes a new observation type: its information value for the chloride forecast can be computed and compared '
          'with that of a new piezometer or a chloride sample, at a fraction of the cost.'),
    ('h', '4. Earthquakes as natural experiments, with a post-earthquake protocol'),
    ('p', 'A strong earthquake changes pore pressure and permeability at once and the change decays over months to years '
          '(papers 7, 11, 15, 18). That is a free, step-like experiment on the aquifer, the kind our identifiability work '
          'asks for and that no operator would run. The protocol: after an earthquake above an agreed magnitude within an '
          'agreed distance, measure heads, conductivity and chloride in the designated wells within days and repeat '
          'monthly, so the response and its recovery are recorded. The 2019 Durrës sequence, with slow slip after the '
          'mainshock (local section), shows such sequences last long enough to be measured.'),
    ('h', '5. Rate limits and calibrated operation of the well field'),
    ('p', 'Induced seismicity depends on how fast pressure changes, not only how much (paper 19), and is best managed by '
          'a model that is calibrated, used and recalibrated (20, 17). For the well field: test in our model whether a '
          'limit on the rate of pumping change reduces upconing and chloride peaks for the same seasonal volume, and run '
          'the field with the calibrate–operate–check loop, judged by information gain over the physics baseline (25).'),
    ('h', 'What we can do now, at low cost'),
    ('b', 'Process the free Sentinel-1 archive (2014 onwards) over the Fushë-Kuqe plain for vertical motion, separating seasonal (elastic) from long-term (inelastic) parts and checking for the 2019 coseismic and postseismic signal.'),
    ('b', 'Compute dv/v from the continuous records of the nearest seismic stations, including those installed for the Durrës aftershock sequence, and compare it with any piezometer record.'),
    ('b', 'Add relative sea level (climate + land motion) to the sea boundary of our variable-density model and compute how far the toe moves for the measured subsidence rate.'),
    ('b', 'Add dv/v as an observation type in the goal-oriented design and compute its information value against a new well.'),
    ('b', 'Write the post-earthquake protocol into the monitoring plan, so the next strong earthquake becomes data rather than an interruption.'),
]

NOTE = ('Verification: every entry was checked against the publisher or institutional repository record through web search; '
        'publisher sites could not be opened directly from this environment. Gaps are stated in the entry (the first names of '
        'two authors of paper 11; the volume of papers 17 and 21). Some free links are repository records whose full text was '
        'not checked. The local papers on the Durrës earthquake are not from the four universities and are given for context.')
