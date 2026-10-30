"""CERTAIN-COAST State of the Art: content. Every cited paper was checked (authors, year, venue, DOI or official URL,
institution) against publisher, proceedings or institutional-repository records found by web search; gaps are stated
in the entry. Paper numbers [n] in the text refer to the annotated list."""

TITLE = 'CERTAIN-COAST — State of the Art'
FULL_TITLE = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, '
              'port and energy landfall of a subsiding Adriatic coast')
SUBTITLE = ('What has been done (30 key papers, 2020–2026, Caltech, MIT, Harvard, Oxford), what has not been done, '
            'and what CERTAIN-COAST brings in mathematics and physics')

GAP_ROWS = [
    ['Seawater intrusion at the wellfields', 'Variable-density models, management optimisation and monitoring design exist, but our searches found no 2020–2026 intrusion paper from the four universities; the preparatory work of this proposal (coupled model, goal-oriented design, extreme-aware alarm) covers it',
     'No intrusion warning with a guaranteed miss rate; subsidence and earthquakes absent from the seaward boundary', '**Certified intrusion alarm** on the coupled model, with the relative-sea-level boundary R(t)'],
    ['Land subsidence and vertical land motion', 'Measured from InSAR/GNSS; sustainable pumping set from 30 years of InSAR; abrupt switch to irreversible compaction detected [1–3]; land motion at tide gauges shown to vary in time with fluid withdrawal and earthquakes [4]',
     'Measured subsidence is not used as a time-varying boundary condition in intrusion, flooding and liquefaction models at the same site', '**One relative sea level R(t) = η(t) − u_z(t)** from InSAR/GNSS drives all three hazard models'],
    ['Extreme sea levels', 'Probabilistic sea-level reconstructions with causes and land motion [5]; extremes attributed to relative sea-level rise [6]; physics-based compound flooding [7]; compound and multi-hazard risk to ports [8, 9]',
     'Land motion enters local extremes as a straight-line trend; port risk is expected annual damage, not a warning; earthquake and flood pathways added, not coupled', '**Nonstationary extremes with InSAR land motion as covariate**, calibrated by conformal risk control'],
    ['Liquefaction', 'Spatially correlated, data-driven liquefaction maps [10]; sub-kilometre site effects imaged by fibre [11]; water table shown to control near-surface stiffness [12]; Durrës 2019 liquefaction mapped [L1]',
     'Susceptibility is static and scenario-based; the water table, which pumping and the sea move, is fixed', '**Factor of safety FS(t) driven by the modelled, time-varying water table**, updated by seismic sensing'],
    ['Port and landfall foundations', 'Validated 1-D design models for piles in clay, sand and layered soils, and lifetime ratcheting under storms [13–15]',
     'No seismic shaking, pore-pressure build-up, liquefaction or subsidence; no monitoring or warning', '**Stability check of the landfall combining shaking, liquefaction, scour-free water level and subsidence**'],
    ['Groundwater sensing', 'Groundwater levels mapped from ambient seismic noise [16]; soil moisture from telecom fibre [17]; droughts, floods and earthquakes separated in 20 years of dv/v [18]',
     'Never used to warn of intrusion or liquefaction; not part of any sensor-design problem', '**dv/v and fibre as observation types** in a goal-oriented design and as liquefaction-susceptibility sensors'],
    ['Certified uncertainty and alarms', 'Distribution-free risk control [19]; online and adaptive conformal prediction with long-run guarantees [20–22]; conformal coverage for neural-operator surrogates [23]; conformal Bayes [24]',
     'Guarantees assume exchangeable data or hold only on time average; never applied to slow physics models of coastal hazards; nothing for states beyond the record', '**Certified multi-hazard alarm**: surrogate error bound + online conformal margin + extreme-aware margin'],
    ['Fast models and assimilation', 'Neural operators with universal approximation [25]; kernel/GP solvers for nonlinear PDEs [26]; optimal UQ by minimum enclosing ball [27]; ensemble Kalman theory [28]; certified dimension reduction [29]; experimental design review [30]',
     'Approximation guarantees, not per-forecast certificates, for coupled variable-density and poroelastic models', '**Error-certified surrogate of the coupled model**, with sensors chosen jointly for the three warnings'],
]

SECTIONS = [
    ('1. The problem: three hazards, two shared variables, one lever', [
        ('p', 'On a subsiding coast, seawater intrusion at the wellfields, liquefaction at the port and the energy landfall, '
              'and extreme sea levels at both are usually studied by different communities with different models. '
              'Physically they are one system, because they share two state variables:'),
        ('b', '**Relative sea level** R(t) = η(t) − u_z(t), the sea level η minus the vertical motion of the land u_z. It sets the '
              'seaward boundary of the aquifer, and therefore the position of the saline wedge (by the Ghyben–Herzberg relation the '
              'interface lies about 40 times deeper than the fresh head above sea level, so each centimetre of R raises it by up to about '
              '40 cm), and it sets the base of every extreme water level at the port and the landfall.'),
        ('b', '**Pore pressure and water-table depth** z_w(x, t). It drives intrusion (the fresh head), compaction (the change in '
              'effective stress σ′ = σ − p compacts the clays and lowers the land) and liquefaction: in the simplified procedure the '
              'cyclic stress ratio CSR = 0.65 (a_max/g)(σ_v/σ′_v) r_d grows as the water table rises, so the factor of safety '
              'FS = CRR/CSR falls when the ground is wetter.'),
        ('p', 'Pumping is the lever that moves all three at once, and in opposite directions. Lowering the water table thickens the '
              'unsaturated crust and reduces liquefaction susceptibility, but it draws the saline wedge inland and compacts the clays; '
              'the compaction lowers the land, raises R(t), and so raises both the intrusion boundary and every extreme sea level. '
              'Sea-level rise works the other way round: it lifts the coastal water table, which brings liquefiable sand back into '
              'saturation. A warning system that treats one hazard at a time will recommend actions that worsen the others. '
              'This coupled chain is the object of CERTAIN-COAST.'),
        ('p', 'The setting is concrete. The Durrës coast, the main port area of a NATO member, combines wellfields in layered alluvium, '
              'a port and an energy landfall on a coast of soft deltaic and lagoonal sediments, active thrust faults (the 26 November 2019 Mw 6.4 '
              'earthquake caused liquefaction along this coast [L1]) and the Adriatic exposure to storm surges. Water supply, port '
              'logistics and energy supply are critical infrastructure; their joint exposure is a security question, not only an '
              'environmental one.'),
    ]),
    ('2. State of the art', [
        ('p', 'Seawater intrusion itself is notable by its absence: the searches behind this review found no 2020–2026 paper on intrusion '
              'from Caltech, MIT, Harvard or Oxford. The intrusion component of CERTAIN-COAST therefore rests on the preparatory work of '
              'the consortium, a coupled variable-density model with salt memory in clay layers, ion exchange, goal-oriented monitoring '
              'design and an extreme-aware alarm, and on the methods reviewed below.'),
        ('h', '2.1 Subsidence and relative sea level: the amplifier'),
        ('p', 'Space geodesy now measures what pumping does to the land. Thirty years of InSAR in the Hollywood Basin, combined with pumping '
              'records, gave a sustainable yield of 1.44–1.67 million m³/yr, less than half the operating safe yield, without any '
              'water-level data [1]. In the Sacramento Valley the 2020–2022 drought caused an abrupt switch from reversible to '
              'irreversible compaction, decimetres per year above the elastic rate, that the well network alone did not reveal [2]. '
              'Groningen showed how elastic seasonal cycles and inelastic long-term compaction can be separated in geodetic data [3]. '
              'At the coast, land motion at tide gauges is not a constant trend: it changes with groundwater and hydrocarbon '
              'withdrawal and with earthquakes, and treating it as linear gives median projection errors of up to 7.6 mm/yr at seismic '
              'sites [4]. Probabilistic reconstructions now separate the causes of relative sea-level change since 1900 [5].'),
        ('h', '2.2 Extreme sea levels'),
        ('p', 'Human-driven sea-level rise has already made the historical 1-in-100-year extreme a 1-in-8-year event at the median '
              'tide gauge, and the driver is mean relative sea level, not surge or tide [6]. Physics-based compound models of rainfall and '
              'surge show the same dominance of sea-level rise for a major port city [7]. For ports, a third of expected annual losses in '
              'Europe come from compound events, and ignoring hazard interactions underestimates them [8]; worldwide, flooding and '
              'earthquakes are the main threats to port assets and trade [9]. What is missing at the scale of one port is the step from '
              'a return period to an operational warning whose miss rate is guaranteed, with measured, time-varying land motion inside it '
              'and with the earthquake and groundwater pathways coupled rather than added.'),
        ('h', '2.3 Liquefaction and the foundations of port and landfall'),
        ('p', 'Liquefaction hazard is mapped statistically: a latent Gaussian process now gives spatially correlated maps of liquefaction '
              'manifestation conditioned on a regional proxy [10]. Fibre-optic sensing images shallow shear-wave velocity along '
              '10 km of telecom cable and shows ground motion varying at sub-kilometre scale with soft sediments [11]. Borehole data '
              'show near-surface shear-wave velocity changing by about 25% in the top 6 m with the water table [12], the physical '
              'link between groundwater and liquefaction. For offshore and landfall foundations, the PISA programme produced validated '
              '1-D design models in clay, sand and layered soils and a lifetime model of ratcheting under storms [13–15]; its one '
              'failing case, very soft clay over dense sand, is the typical deltaic sequence of the Adriatic coast [14]. After the 2019 '
              'Durrës earthquake, liquefaction was mapped at lagoons, estuaries and the southern Durrës coast [L1].'),
        ('h', '2.4 Continuous sensing of groundwater and soil'),
        ('p', 'Ambient seismic noise tracks groundwater: space-time maps of velocity change near Los Angeles follow well water tables and '
              'InSAR deformation over 2000–2020 [16]. Telecom fibre resolves recharge pulses and a drought loss of about 0.25 m/yr '
              'of water in the unsaturated zone [17]. Twenty years of velocity changes at about 700 stations separate wet winters, '
              'droughts and decade-long postseismic signals [18]. These sensors are cheap, continuous and depth-resolved.'),
        ('h', '2.5 The mathematics of certified warning'),
        ('p', 'Distribution-free methods now control more than coverage: conformal risk control bounds the expected value of any '
              'monotone loss, such as a false-negative rate, at a chosen level α [19]. Online conformal methods keep long-run '
              'coverage for arbitrary, even adversarial, sequences [20], and discounted adaptive learning forgets the past at the '
              'right speed under nonstationarity [21]; adaptive conformal sets have been embedded in control loops [22]. For physics '
              'surrogates, a risk-controlling quantile neural operator gives a finite-sample guarantee on the fraction of the domain '
              'outside its band [23], and conformal Bayesian computation gives frequentist coverage even for misspecified models [24]. '
              'On the modelling side, neural operators approximate solution operators of PDEs universally [25], Gaussian-process '
              'solvers treat nonlinear PDEs and inverse problems with convergence guarantees [26], optimal uncertainty quantification '
              'gives worst-case risk as the radius of a minimum enclosing ball [27], ensemble Kalman methods have a mean-field theory '
              '[28], dimension reduction can be certified by a computable bound [29], and optimal experimental design has a unified '
              'theory [30].'),
    ]),
    ('3. What has not been done', [
        ('p', 'The table sets out, for each component, what the literature has achieved, what it has not, and the step CERTAIN-COAST takes.'),
        ('table', (['Component', 'Done (papers)', 'Not done', 'CERTAIN-COAST'], GAP_ROWS, [2.6, 5.4, 4.6, 4.4])),
        ('p', 'Three gaps cut across the table. First, **no early warning treats the three hazards as one system**, although they '
              'share relative sea level and pore pressure and are moved by the same pumping lever. Second, **no warning for any of '
              'them carries a guarantee**: the certified methods of [19–24] assume exchangeable data or hold on time average, and none '
              'has been applied to a slow physics model of a coastal hazard or to states outside the observed record. Third, '
              '**the new sensors (InSAR time series, seismic noise, fibre) are measured but not designed**: no study chooses them '
              'jointly with wells and chemical samples to minimise the miss probability of the warnings.'),
    ]),
    ('4. What CERTAIN-COAST brings', [
        ('h', 'Mathematical innovations'),
        ('b', '**M1. Certified multi-hazard alarm.** For each hazard k (intrusion at a wellfield, liquefaction at the port or landfall, '
              'extreme water level) the alarm fires when the forecast indicator exceeds its threshold minus a margin m_k. The margin '
              'adds three certified parts: the a-posteriori error bound of the fast surrogate [23, 27], an online conformal risk-control '
              'term that keeps the long-run miss rate below α_k under nonstationarity [19–21], and an extreme-aware term that widens the '
              'margin when the forcing leaves the observed record. In our preparatory synthetic tests on a coupled variable-density model, '
              'an extreme-aware margin kept the share of seasons above the chloride limit at 4–9% across drought, human-feedback and '
              'compound storylines, where a static alarm allowed 13–21%.'),
        ('b', '**M2. A joint guarantee across hazards.** Because the three alarms share inputs, their miss events are dependent; '
              'CERTAIN-COAST controls the probability that any of them is missed (at most Σ α_k by a union bound, tightened by joint '
              'calibration) and allocates the α_k by consequence, so that a water-supply alarm and a landfall alarm are not held to the '
              'same tolerance by accident.'),
        ('b', '**M3. Multi-hazard goal-oriented sensor design.** InSAR, GNSS, piezometers, chloride samples, seismic noise, fibre and '
              'temporary nodes are chosen together to maximise the expected reduction in the miss probability of the three alarms, '
              'extending goal-oriented design [30] from one quantity and one sensor type to several hazards and sensor types.'),
        ('b', '**M4. An error-certified surrogate of the coupled model.** A neural or kernel operator of the coupled variable-density, '
              'poroelastic model [25, 26], whose error is bounded a posteriori and calibrated conformally [23], makes thousands of '
              'storylines and real-time updates affordable without losing the guarantee.'),
        ('b', '**M5. Nonstationary extremes with measured land motion.** Extreme water levels are modelled with InSAR/GNSS land motion as '
              'a time-varying covariate of the location parameter, instead of a linear trend [4, 5].'),
        ('h', 'Physical innovations'),
        ('b', '**P1. One relative-sea-level boundary for all three hazards**, R(t) = η(t) − u_z(t), with u_z from InSAR/GNSS after removal '
              'of loading signals [1–5].'),
        ('b', '**P2. A time-varying liquefaction factor of safety**, FS(x, t) = CRR / CSR(z_w(x, t)), with the water table z_w taken '
              'from the calibrated groundwater model and checked by seismic velocity [12, 16–18], instead of a fixed design water table.'),
        ('b', '**P3. The pumping lever made explicit**: every pumping rule is evaluated against all three hazards at once '
              '(intrusion and subsidence rise, liquefaction susceptibility falls), so the warning recommends actions that do not shift '
              'the risk from one asset to another.'),
        ('b', '**P4. The compaction tipping point as a warning in itself**: the switch from elastic to inelastic compaction [2, 3] '
              'is irreversible and permanently raises R(t); detecting it early is a warning for all three hazards.'),
        ('b', '**P5. Seismic velocity as a pore-pressure sensor in saturated coastal sediments** at the port and the landfall, '
              'transferring [11, 16–18] from dry or inland basins to the coastal setting where it matters for liquefaction.'),
        ('p', 'Together these give what no study has delivered: warnings for the wellfields, the port and the energy landfall that '
              'come from one physical model, are issued fast enough to act on, and carry a stated, verifiable bound on how often '
              'they miss.'),
    ]),
]

PAPERS_TITLE = '5. The 30 key papers (2020–2026)'
PAPERS_INTRO = ('Caltech 12, MIT 7, Harvard 5, Oxford 6. For each: where to download it, what it did, and the step CERTAIN-COAST '
                'takes beyond it. [L1] is a local study, not from the four universities.')

GROUPS = [
    ('A. Subsidence and relative sea level', [
        dict(n=1, inst='Caltech', cite='Zheng, Y. and Simons, M. (2025). Integrating long-term InSAR monitoring into local groundwater management: insights from the Hollywood Basin, California. Water Resources Research 61(11), e2024WR039161.',
             doi='https://doi.org/10.1029/2024WR039161', free='https://essopenarchive.org/doi/full/10.22541/essoar.173046635.57543794/v1', free_label='ESS Open Archive',
             done='About 30 years of InSAR with pumping records give a sustainable yield of 1.44–1.67 million m³/yr against an operating safe yield of 3.70 million m³/yr; ICA separates deep and shallow aquifer signals without water-level data.',
             beyond='The sustainable yield becomes one constraint among three: CERTAIN-COAST sets pumping so that subsidence, intrusion and liquefaction alarms stay within their certified miss rates together.'),
        dict(n=2, inst='Caltech', cite='Larochelle, S., Chanard, K., Dalaison, M., Fortin, J., et al., including Avouac, J.-P. (2026). Abrupt transition to irreversible damage in the overdrafted Sacramento Valley aquifer system. PNAS 123(31), e2526041123.',
             doi='https://doi.org/10.1073/pnas.2526041123', free='https://authors.library.caltech.edu/records/hjp15-k0645', free_label='CaltechAUTHORS record',
             done='InSAR, GNSS and wells (2016–2022) show an abrupt switch to irreversible compaction during the 2020–2022 drought, decimetres per year above the elastic rate; space geodesy proposed as early warning.',
             beyond='The switch is turned into a formal alarm (P4) and its consequence, a permanent rise of relative sea level, is propagated into the intrusion and flooding warnings.'),
        dict(n=3, inst='Caltech', cite='Li, Y., Acosta, M., Sirorattanakul, K., Bourne, S. and Avouac, J.-P. (2025). Geodetic monitoring of elastic and inelastic deformation in compacting reservoirs due to subsurface operations. Journal of Geophysical Research: Solid Earth 130(3), e2024JB030794.',
             doi='https://doi.org/10.1029/2024JB030794', free='https://authors.library.caltech.edu/records/vbhry-09e90', free_label='CaltechAUTHORS record',
             done='Over Groningen and Norg (2009–2022), inelastic compaction reaches about 20% of the total at Groningen, while a 20 mm seasonal storage cycle at Norg is purely elastic.',
             beyond='The elastic/inelastic split is applied to a coastal wellfield, where seasonal pumping should leave an elastic cycle; its loss is the early sign of the tipping point.'),
        dict(n=4, inst='Harvard', cite='Dangendorf, S., Oelsmann, J., Mitrovica, J.X., Törnqvist, T.E., Piecuch, C.G., Creel, R., Coronel, W., Thompson, P.R., Ebinger, C. and Wahl, T. (2026). Variable contributions of vertical land motion to sea-level change inferred at tide gauges. Nature Geoscience 19, 814–821.',
             doi='https://doi.org/10.1038/s41561-026-02005-1', free=None, free_note='paywalled; free copy due at par.nsf.gov in June 2027',
             done='Vertical land motion at tide gauges changes its rate with fluid withdrawal and earthquakes; treating it as linear gives median projection errors up to 7.6 mm/yr at seismic sites. Venice is among the cases.',
             beyond='Land motion enters as a measured, time-varying input (P1, M5), at the scale of a port, instead of a linear trend at a tide gauge.'),
        dict(n=5, inst='Harvard', cite='Dangendorf, S., Sun, Q., Wahl, T., Thompson, P., Mitrovica, J.X. and Hamlington, B. (2024). Probabilistic reconstruction of sea-level changes and their causes since 1900. Earth System Science Data 16, 3471–3494.',
             doi='https://doi.org/10.5194/essd-16-3471-2024', free='https://essd.copernicus.org/articles/16/3471/2024/', free_label='open access',
             done='Near-global probabilistic reconstruction of relative sea level and its causes, 1900–2021; global mean rise 1.5 ± 0.19 mm/yr, consistent with observations only once local land motion is included.',
             beyond='Its regional climate component supplies η(t) with uncertainty; CERTAIN-COAST adds the local u_z(t) from InSAR to obtain R(t) at the assets.'),
    ]),
    ('B. Extreme sea levels, compound flooding and ports', [
        dict(n=6, inst='Harvard (Mitrovica)', cite='Dangendorf, S., Sun, Q., Maduwantha, P., Wahl, T., Marcos, M., Marzeion, B., Slangen, A.B.A. and Mitrovica, J.X. (2026). Human-driven sea-level rise has quadrupled the frequency of coastal sea-level extremes since 1900. Nature Climate Change 16(7), 796–803.',
             doi='https://doi.org/10.1038/s41558-026-02659-0', free='https://publications.marum.de/5800/', free_label='MARUM repository record',
             done='Long tide-gauge records with climate-model attribution (1900–2005): the median historical 1-in-100-year extreme is now about a 1-in-8-year event; human forcing alone made such events about four times more likely; the driver is mean relative sea level, not surge or tide.',
             beyond='Since the driver is relative sea level, a subsiding coast moves its extremes faster than the global attribution shows; CERTAIN-COAST puts the measured land motion into the local extreme-value model (M5).'),
        dict(n=7, inst='MIT (Emanuel)', cite='Sarhadi, A., Rousseau-Rizzi, R., Mandli, K., Neal, J., Wiper, M.P., Feldmann, M. and Emanuel, K. (2024). Climate change contributions to increasing compound flooding risk in New York City. Bulletin of the American Meteorological Society 105(2), E337–E356.',
             doi='https://doi.org/10.1175/BAMS-D-23-0177.1', free='https://dspace.mit.edu/handle/1721.1/169800', free_label='DSpace@MIT (open access)',
             done='Physics-based coupled rainfall and surge models driven by synthetic tropical and extratropical cyclones: a Sandy-scale compound flood (about 1-in-150 years now) becomes about 1-in-60 by mid-century and 1-in-30 by 2100; sea-level rise alone raises the hazard more than changes in storms.',
             beyond='The same physics-based compound approach, with Adriatic storms instead of tropical cyclones, plus the two terms it lacks for a subsiding coast: land motion and the groundwater rise that the surge pushes inland.'),
        dict(n=8, inst='Oxford (Hall)', cite='Fernandez-Perez, A., Verschuur, J., Lara, J.L., Losada, I.J. and Hall, J.W. (2025). Compound climate risks to European ports. Environmental Research: Climate 5(1), 015005.',
             doi='https://doi.org/10.1088/2752-5295/ae26bc', free='https://ora.ox.ac.uk/objects/uuid:d97b8693-4357-416e-aa2b-6e12136d97ae', free_label='Oxford ORA (open access)',
             done='A compound-event risk framework for 406 European ports: expected annual losses about €1.05 bn, more than one third from compound events; ignoring hazard interactions underestimates losses by about €100 M, more so for extreme events.',
             beyond='Hazard interactions matter at the continental scale; CERTAIN-COAST resolves them physically at one port, including the interactions this framework does not carry: subsidence, groundwater and liquefaction.'),
        dict(n=9, inst='Oxford (Hall)', cite='Verschuur, J., Koks, E.E., Li, S. and Hall, J.W. (2023). Multi-hazard risk to global port infrastructure and resulting trade and logistics losses. Communications Earth & Environment 4, 5.',
             doi='https://doi.org/10.1038/s43247-022-00656-7', free='https://doi.org/10.1038/s43247-022-00656-7', free_label='open access (journal)',
             done='An asset-level analysis of about 1,340 ports for cyclone wind, coastal, river and pluvial flooding and earthquakes: port-specific risk US$7.5 bn per year, 58.6% physical damage, 22.2% logistics losses, 19.2% damage to nearby infrastructure; US$63.1 bn of trade at risk per year.',
             beyond='Earthquakes and flooding are counted side by side but not coupled; CERTAIN-COAST couples them at the port through the water table and relative sea level, and turns expected annual damage into a warning.'),
    ]),
    ('C. Liquefaction and the foundations of port and landfall', [
        dict(n=10, inst='Caltech (Asimaki)', cite='Bullock, Z., Zimmaro, P., Lavrentiadis, G., Wang, P., Ojomo, O., Asimaki, D., Rathje, E.M. and Stewart, J.P. (2023). A latent Gaussian process model for the spatial distribution of liquefaction manifestation. Earthquake Spectra 39(2), 1189–1213.',
             doi='https://doi.org/10.1177/87552930231163894', free='https://escholarship.org/uc/item/2f93p946', free_label='eScholarship',
             done='A latent Gaussian process adds spatial correlation to a geospatial liquefaction proxy fitted to observed liquefaction and generates random maps conditioned on the areal fraction that liquefied; developed for regional gas-system risk.',
             beyond='The statistical field is conditioned on physics: the water table from the groundwater model and the seismic velocity from fibre or noise, so susceptibility changes with the season, the pumping and the sea (P2).'),
        dict(n=11, inst='Caltech (Zhan)', cite='Yang, Y., Atterholt, J.W., Shen, Z., Muir, J.B., Williams, E.F. and Zhan, Z. (2022). Sub-kilometer correlation between near-surface structure and ground motion measured with distributed acoustic sensing. Geophysical Research Letters 49(1), e2021GL096503.',
             doi='https://doi.org/10.1029/2021GL096503', free='https://resolver.caltech.edu/CaltechAUTHORS:20220120-890594000', free_label='CaltechAUTHORS record',
             done='About three months of traffic noise on a telecom fibre image shallow shear-wave velocity along about 10 km; aftershock shaking varies at sub-kilometre scale and is stronger in soft-sediment micro-basins.',
             beyond='The same fibre principle is moved to saturated port and landfall sediments and used continuously, so that site amplification and the water table are monitored together (P5).'),
        dict(n=12, inst='MIT (Nakata)', cite='Qin, L., Steidl, J.H., Qiu, H., Nakata, N. and Ben-Zion, Y. (2022). Monitoring seasonal shear wave velocity changes in the top 6 m at Garner Valley in Southern California with borehole data. Geophysical Research Letters 49, e2022GL101189.',
             doi='https://doi.org/10.1029/2022GL101189', free='https://www.osti.gov/pages/biblio/1903071', free_label='OSTI record',
             done='Borehole earthquake and cross-hole data show shear-wave velocity varying by about 25% in the top 6 m and about 10% at 2–5 m, following the water-table depth.',
             beyond='The measured link between water table and stiffness becomes the bridge from the groundwater model to the liquefaction factor of safety, and a check on it.'),
        dict(n=13, inst='Oxford (Byrne, Houlsby, Burd, Martin)', cite='Byrne, B.W., Houlsby, G.T., Burd, H.J., Gavin, K.G., Igoe, D.J.P., Jardine, R.J., et al. (2020). PISA design model for monopiles for offshore wind turbines: application to a stiff glacial clay till. Géotechnique 70(11), 1030–1047.',
             doi='https://doi.org/10.1680/jgeot.18.P.255', free='https://research.tudelft.nl/en/publications/pisa-design-model-for-monopiles-for-offshore-wind-turbines-applic', free_label='TU Delft portal',
             done='A 1-D pile design model calibrated on 3-D finite-element analyses and field tests, matching 3-D results at a fraction of the cost within its calibration space.',
             beyond='A fast, validated foundation model is the template; CERTAIN-COAST adds what it lacks for a landfall on a seismic, subsiding coast: shaking, pore-pressure build-up and a changing water level.'),
        dict(n=14, inst='Oxford', cite='Burd, H.J., Abadie, C.N., Byrne, B.W., Houlsby, G.T., Martin, C.M., McAdam, R.A., et al. (2020). Application of the PISA design model to monopiles embedded in layered soils. Géotechnique 70(11), 1067–1082.',
             doi='https://doi.org/10.1680/jgeot.20.PISA.009', free='https://spiral.imperial.ac.uk/entities/publication/ae22661c-46e4-4710-ac7a-7b44a602fa47', free_label='Imperial Spiral',
             done='Soil-reaction curves from uniform soils work for layered profiles, except some combinations of very soft clay and very dense sand.',
             beyond='The failing case is the deltaic and lagoonal sequence of the Adriatic coast; the landfall check of CERTAIN-COAST is built for it, with liquefaction of the sand layers included.'),
        dict(n=15, inst='Oxford', cite='Abadie, C.N., Beuckelaers, W.J.A.P., Byrne, B.W., Burd, H.J. and McAdam, R.A. (2023). Modeling lifetime performance of monopile foundations for offshore wind applications. Journal of Geotechnical and Geoenvironmental Engineering 149(8), 04023051.',
             doi='https://doi.org/10.1061/JGGEFK.GTENG-9833', free='https://ora.ox.ac.uk/objects/uuid:5077c91e-daec-48a8-ad24-de711938f81d', free_label='Oxford ORA',
             done='Couples the PISA model with a ratcheting model to predict permanent rotation over a short storm, a 35-hour storm and the full lifetime.',
             beyond='Storm loading is joined by the other two hazards of the landfall, seismic liquefaction and the rising relative sea level, in one assessment with stated uncertainty.'),
    ]),
    ('D. Continuous sensing of groundwater and soil', [
        dict(n=16, inst='MIT', cite='Mao, S., Lecointre, A., van der Hilst, R.D. and Campillo, M. (2022). Space-time monitoring of groundwater fluctuations with passive seismic interferometry. Nature Communications 13, 4643.',
             doi='https://doi.org/10.1038/s41467-022-32194-3', free='https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9360030/', free_label='PubMed Central',
             done='Ambient-noise velocity changes map groundwater fluctuations over 2000–2020 near Los Angeles, following well water tables and InSAR, with better time and depth resolution.',
             beyond='Seismic noise becomes a designed observation (M3) and a pore-pressure sensor at the port and landfall (P5), not only a hydrogeological map.'),
        dict(n=17, inst='Caltech (Zhan, Fu)', cite='Shen, Z., Yang, Y., Fu, X., Adams, K.H., Biondi, E. and Zhan, Z. (2024). Fiber-optic seismic sensing of vadose zone soil moisture dynamics. Nature Communications 15, 6432.',
             doi='https://doi.org/10.1038/s41467-024-50690-6', free='https://www.nature.com/articles/s41467-024-50690-6', free_label='open access',
             done='Traffic noise on about 10 km of telecom fibre resolves recharge pulses and a drought loss of about 0.25 m/yr of water in the unsaturated zone over about 5 years.',
             beyond='Moved from an arid vadose zone to a shallow coastal water table, the fibre becomes a recharge and liquefaction-susceptibility sensor along the coast road.'),
        dict(n=18, inst='Harvard', cite='Clements, T. and Denolle, M.A. (2023). The seismic signature of California\'s earthquakes, droughts, and floods. Journal of Geophysical Research: Solid Earth 128(1), e2022JB025553.',
             doi='https://doi.org/10.1029/2022JB025553', free='https://eartharxiv.org/repository/view/4658/', free_label='EarthArXiv',
             done='dv/v at about 700 stations (1999–2021) separates wet winters, multiyear droughts and decade-long postseismic signals; diffusivity is low in basins; site variations match subsidence and uplift.',
             beyond='The separation of hydrological and earthquake signals is what a coastal warning needs after the next earthquake, when the water table and the soil both change.'),
    ]),
    ('E. Mathematics of certified warning', [
        dict(n=19, inst='MIT (Bates, Fisch)', cite='Angelopoulos, A.N., Bates, S., Fisch, A., Lei, L. and Schuster, T. (2024). Conformal risk control. International Conference on Learning Representations (ICLR 2024).',
             doi='https://proceedings.iclr.cc/paper_files/paper/2024/hash/f3549ef9b5ff520a7e41ff3cc306ab2b-Abstract-Conference.html', free='https://arxiv.org/abs/2208.02814', free_label='arXiv',
             done='Extends split conformal prediction to any monotone bounded loss: the calibrated threshold guarantees E[L(λ̂)] ≤ α under exchangeability, tight to O(B/n); a false-negative (miss) rate is a special case.',
             beyond='The miss rate of each alarm is the controlled loss; CERTAIN-COAST removes the exchangeability assumption by the online and extreme-aware terms of M1.'),
        dict(n=20, inst='MIT (Bates)', cite='Angelopoulos, A.N., Barber, R.F. and Bates, S. (2024). Online conformal prediction with decaying step sizes. Proceedings of the 41st International Conference on Machine Learning, PMLR 235, 1616–1630.',
             doi='https://proceedings.mlr.press/v235/angelopoulos24a.html', free='https://arxiv.org/abs/2402.01139', free_label='arXiv',
             done='Online quantile tracking with decaying steps keeps long-run coverage for arbitrary sequences and converges to the true quantile when the data are i.i.d.',
             beyond='Long-run coverage is not enough for rare, clustered extremes; it is combined with a margin that widens when forcing leaves the record.'),
        dict(n=21, inst='Harvard (Yang)', cite='Zhang, Z., Bombara, D. and Yang, H. (2024). Discounted adaptive online learning: towards better regularization. Proceedings of the 41st International Conference on Machine Learning, PMLR 235, 58631–58661.',
             doi='https://proceedings.mlr.press/v235/zhang24e.html', free='https://arxiv.org/abs/2402.02720', free_label='arXiv',
             done='An adaptive algorithm for discounted regret that forgets history gracefully in nonstationary environments; applied to online conformal prediction it gives instance-dependent coverage guarantees.',
             beyond='The forgetting rate is tied to physics: it is set by the memory time of the aquifer and the clays, not tuned on generic benchmarks.'),
        dict(n=22, inst='Caltech (Burdick)', cite='Dixit, A., Lindemann, L., Wei, S.X., Cleaveland, M., Pappas, G.J. and Burdick, J.W. (2023). Adaptive conformal prediction for motion planning among dynamic agents. Proceedings of the 5th Learning for Dynamics and Control Conference, PMLR 211, 300–314.',
             doi='https://proceedings.mlr.press/v211/dixit23a.html', free='https://arxiv.org/abs/2212.00278', free_label='arXiv',
             done='Online adaptive conformal sets for multistep-ahead predictions, without exchangeability, feed a model-predictive controller.',
             beyond='The same closed loop, prediction set to action, is built for pumping and port operations, with sets from a physics surrogate instead of a data-driven predictor.'),
        dict(n=23, inst='Caltech (Anandkumar)', cite='Ma, Z., Pitt, D., Azizzadenesheli, K. and Anandkumar, A. (2024). Calibrated uncertainty quantification for operator learning via conformal prediction. Transactions on Machine Learning Research, August 2024.',
             doi='https://openreview.net/forum?id=cGpegxy12T', free='https://arxiv.org/abs/2402.01960', free_label='arXiv',
             done='A risk-controlling quantile neural operator gives, with probability at least 1 − δ, an expected fraction of domain points outside the band of at most α; it alone reached the 98% target on a 3-D task.',
             beyond='The surrogate guarantee is the first of the three margin terms of M1; CERTAIN-COAST extends it from a fraction of the domain to the asset points where the alarms are issued.'),
        dict(n=24, inst='Oxford (Holmes)', cite='Fong, E. and Holmes, C. (2021). Conformal Bayesian computation. Advances in Neural Information Processing Systems 34 (NeurIPS 2021).',
             doi='https://proceedings.neurips.cc/paper/2021/hash/97785e0500ad16c18574c64189ccf4b4-Abstract.html', free='https://proceedings.nips.cc/paper_files/paper/2021/file/97785e0500ad16c18574c64189ccf4b4-Paper.pdf', free_label='proceedings PDF',
             done='Full conformal prediction for Bayesian models from existing posterior samples, with finite-sample coverage even under misspecification; extends to hierarchical data.',
             beyond='The Bayesian calibration of the coupled model keeps its posterior, and conformal Bayes turns it into intervals with frequentist coverage; hierarchical data match several wells and sites.'),
        dict(n=25, inst='Caltech (Stuart, Anandkumar)', cite='Kovachki, N., Li, Z., Liu, B., Azizzadenesheli, K., Bhattacharya, K., Stuart, A. and Anandkumar, A. (2023). Neural operator: learning maps between function spaces with applications to PDEs. Journal of Machine Learning Research 24(89), 1–97.',
             doi='https://www.jmlr.org/papers/v24/21-1524.html', free='https://arxiv.org/abs/2108.08481', free_label='arXiv',
             done='Defines discretisation-invariant neural operators and proves universal approximation of continuous nonlinear operators.',
             beyond='The coupled variable-density, poroelastic model is learned as an operator from forcing to hazard indicators, with the a-posteriori certificate approximation theory does not give.'),
        dict(n=26, inst='Caltech (Owhadi, Stuart)', cite='Chen, Y., Hosseini, B., Owhadi, H. and Stuart, A.M. (2021). Solving and learning nonlinear PDEs with Gaussian processes. Journal of Computational Physics 447, 110668.',
             doi='https://doi.org/10.1016/j.jcp.2021.110668', free='https://arxiv.org/abs/2103.12959', free_label='arXiv',
             done='Nonlinear PDEs solved as the MAP of a Gaussian process conditioned at collocation points, with Gauss–Newton in a few iterations and convergence guarantees; inverse problems solved jointly.',
             beyond='The kernel route gives the coupled model an alternative surrogate with built-in uncertainty, for the small, data-poor coastal domains where neural operators are hard to train.'),
        dict(n=27, inst='Caltech (Owhadi, Scovel)', cite='Hamze Bajgiran, H., Batlle, P., Owhadi, H., Samir, M., Scovel, C., Shirdel, M., Stanley, M. and Tavallali, P. (2022). Uncertainty quantification of the 4th kind; optimal posterior accuracy-uncertainty tradeoff with the minimum enclosing ball. Journal of Computational Physics 471, 111608. (DOI not confirmed.)',
             doi='https://arxiv.org/abs/2108.10517', free='https://authors.library.caltech.edu/records/v0cp5-ykc35/preview/2108.10517.pdf', free_label='CaltechAUTHORS PDF',
             done='Combines robust optimisation, Bayesian inference and hypothesis testing: the optimal estimate and its worst-case risk are the centre and radius of the minimum enclosing ball of a likelihood region mapped to the quantity of interest.',
             beyond='The worst-case radius gives the extreme-aware margin a rigorous form: the alarm margin for states beyond the record is the enclosing-ball radius over the plausible forcing set.'),
        dict(n=28, inst='Caltech (Stuart)', cite='Calvello, E., Reich, S. and Stuart, A.M. (2025). Ensemble Kalman methods: a mean-field perspective. Acta Numerica 34, 123–291.',
             doi='https://doi.org/10.1017/S0962492924000060', free='https://arxiv.org/abs/2209.11371', free_label='arXiv',
             done='A unifying analysis of ensemble Kalman methods for filtering, inversion and sampling as particle approximations of mean-field models, exact in the linear-Gaussian case.',
             beyond='Ensemble Kalman assimilation of heads, chloride, InSAR and dv/v updates the coupled state; its non-Gaussian error is absorbed by the conformal layer rather than ignored.'),
        dict(n=29, inst='MIT (Marzouk)', cite='Zahm, O., Cui, T., Law, K., Spantini, A. and Marzouk, Y. (2022). Certified dimension reduction in nonlinear Bayesian inverse problems. Mathematics of Computation 91(336), 1789–1835.',
             doi='https://www.ams.org/journals/mcom/2022-91-336/S0025-5718-2022-03737-6/', free='https://arxiv.org/abs/1807.03712', free_label='arXiv',
             done='Approximates the likelihood by a ridge function chosen to minimise a computable upper bound on the KL divergence between exact and approximate posteriors, which certifies the approximation.',
             beyond='The certified reduction makes calibration of the coupled model tractable and gives the error budget that enters the alarm margin.'),
        dict(n=30, inst='MIT (Marzouk)', cite='Huan, X., Jagalur, J. and Marzouk, Y. (2024). Optimal experimental design: formulations and computations. Acta Numerica 33, 715–840.',
             doi='https://doi.org/10.1017/S0962492924000023', free=None, free_note='free version: check the authors\' pages or arXiv',
             done='A unified review of optimal experimental design, Bayesian and goal-oriented criteria, and their computation.',
             beyond='Extended in M3 from one goal and one sensor type to the joint miss probability of three warnings and seven sensor types.'),
    ]),
]

LOCAL = [
    ('L1', 'Mavroulis, S., Lekkas, E. and Carydis, P. (2021). Liquefaction phenomena induced by the 26 November 2019, Mw = 6.4 Durrës (Albania) earthquake and liquefaction susceptibility assessment in the affected area. Geosciences 11(5), 215.',
     'https://doi.org/10.3390/geosciences11050215'),
]

NOTE = ('Verification: each entry was checked against publisher, proceedings or institutional-repository records through web search; '
        'publisher sites could not be opened directly from this environment. Gaps are stated in the entry (the DOI of [27]). '
        'Some free links are repository records whose full text was not checked. No 2020–2026 paper on seawater intrusion with an author '
        'at the four universities was found; the intrusion state of the art rests on the preparatory work and is itself a gap.')
