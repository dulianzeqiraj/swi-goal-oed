"""The thirty paper cards of the review "Where does the chloride come from?" (2020-2026): Oxford, Caltech, MIT,
Princeton, the Max Planck Society, Harvard and Berkeley.

Bibliographic data and affiliations: the Crossref record of each DOI (author[].affiliation[].name), checked twice.
Content: the abstract of each paper (Crossref); for M1 Crossref has no abstract and the card says so.  No card states more
than its abstract supports.  None of the thirty DOIs is used in an earlier review of this series.  The records are in
res/selected_papers.json.  Fields: id, inst, year, short, title, authors, venue, links, evidence, does, route (how it bears
on the origin of chloride), gap, step (innovation step for us), routes (tracers, mixing, inverse, ident, learn), status.
<<key>> is a number filled in from res/zanafilla.json by text_zanafilla.py."""

INST_ORDER = ['Oxford', 'Caltech', 'MIT', 'Princeton', 'Max Planck', 'Harvard', 'Berkeley']

CARDS = [{'id': 'O1',
  'inst': 'Oxford',
  'year': 2022,
  'short': 'Kr-81 ages of brines and flushing',
  'title': 'Krypton‐81 Dating Constrains Timing of Deep Groundwater Flow Activation',
  'authors': 'Ji‐Hyun Kim, Grant Ferguson, Mark Person, Wei Jiang, Zheng‐Tian Lu, Florian Ritterbusch, Guo‐Min Yang, '
             'Rebecca Tyne, Lydia Bailey, Chris Ballentine, Peter Reiners, Jennifer McIntosh',
  'venue': 'Geophysical Research Letters 49(11), e2021GL097618 (2022)',
  'links': [('doi:10.1029/2021gl097618', 'https://doi.org/10.1029/2021gl097618')],
  'evidence': 'Crossref lists Rebecca Tyne at Department of Earth Sciences University of Oxford Oxford UK; Chris '
              'Ballentine at Department of Earth Sciences University of Oxford Oxford UK.',
  'does': 'Krypton-81 ages of formation waters in the Paradox Basin (Colorado Plateau) separate remnant Paleozoic '
          'seawater-derived brines, preserved below evaporites and older than the 1.2 Ma range of the method, from '
          'meteoric water that recharged since the Late Pleistocene, partly flushed the brines and dissolved '
          'evaporites. The age distributions record the activation of deep flow by recent denudation.',
  'route': 'An age tracer separates old marine salinity from younger water that dissolved salt: the distinction that '
           'chloride, bromide and the stable isotopes cannot make between relict and modern seawater.',
  'gap': 'A deep basin and million-year scales; the ages are interpreted, not carried into a quantified attribution '
         'with bounds.',
  'step': 'In ZANAFILLA-GO an age tracer is one more water-weighted contribution with interval signatures. Our test '
          'shows that the relict end-member limits the attribution: characterising it, which is what an age '
          'measurement of relict pore water does, raised decidability from <<all_d>> to <<rel_all_d>>.',
  'routes': ['tracers'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'O2',
  'inst': 'Oxford',
  'year': 2021,
  'short': 'How much deep saline water exists',
  'title': 'Crustal Groundwater Volumes Greater Than Previously Thought',
  'authors': 'Grant Ferguson, Jennifer C. McIntosh, Oliver Warr, Barbara Sherwood Lollar, Christopher J. Ballentine, '
             'James S. Famiglietti, Ji‐Hyun Kim, Joseph R. Michalski, John F. Mustard, Jesse Tarnas, Jeffrey J. '
             'McDonnell',
  'venue': 'Geophysical Research Letters 48(16), e2021GL093549 (2021)',
  'links': [('doi:10.1029/2021gl093549', 'https://doi.org/10.1029/2021gl093549')],
  'evidence': 'Crossref lists Christopher J. Ballentine at Department of Earth Sciences University of Oxford Oxford '
              'UK.',
  'does': 'Estimates the groundwater stored in the upper 10 km of the continental crust from the depth distribution '
          'of sedimentary and crystalline rocks and porosity–depth relations: the 2–10 km zone, largely saline and '
          'non-potable, holds a volume comparable to that of the upper 2 km.',
  'route': 'Deep saline water is not a rarity but a reservoir as large as the fresh one: a deep brine is a candidate '
           'source of chloride wherever pumping can draw from depth.',
  'gap': 'Global volumes, not the chemistry or the connections that decide whether a given well receives it.',
  'step': 'A deep brine belongs in the source list, or its absence must be tested. ZANAFILLA-GO tests it: when an '
          'unlisted Br-rich brine supplied more than 0.5% of the water, the identified set was empty in <<miss_0>> '
          'of the samples, so the data themselves flagged the missing source.',
  'routes': ['tracers'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'O3',
  'inst': 'Oxford',
  'year': 2020,
  'short': 'Offshore groundwater from seismic data',
  'title': 'Seismic Reflection Methods in Offshore Groundwater Research',
  'authors': 'Claudia Bertoni, Johanna Lofi, Aaron Micallef, Henning Moe',
  'venue': 'Geosciences 10(8), 299 (2020)',
  'links': [('doi:10.3390/geosciences10080299', 'https://doi.org/10.3390/geosciences10080299')],
  'evidence': 'Crossref lists Claudia Bertoni at Department of Earth Sciences, University of Oxford, South Parks '
              'Road, Oxford OX1 3AN, UK.',
  'does': 'Reviews how marine seismic reflection data, including untapped industrial surveys, characterise offshore '
          'hydrogeological systems: aquifer architecture, permeability barriers, palaeo-environments, sea-level '
          'changes and conduits for flow in passive-margin sediments that host fresh and brackish water of meteoric '
          'origin.',
  'route': 'Past sea levels and buried barriers are what trap relict seawater on land and fresh water offshore; '
           'geophysics constrains where relict pockets can be.',
  'gap': 'Geometry, not chemistry; no attribution of the salinity of a well.',
  'step': 'Geophysics enters ZANAFILLA-GO as site caps: where seismic or resistivity data exclude a clay-hosted '
          'relict pocket, the relict fraction of that screen is capped, a linear constraint that shrinks the '
          'identified set without any prior.',
  'routes': ['ident'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'O4',
  'inst': 'Oxford',
  'year': 2025,
  'short': 'Simulation-based inference of water quality',
  'title': 'Simulation-based inference advances water quality mapping in shallow coral reef environments',
  'authors': 'Pirta Palola, Varunan Theenathayalan, Cornelius Schröder, Victor Martinez-Vicente, Antoine Collin, '
             'Rosalie Wright, Melissa Ward, Eleanor Thomson, Patricia Lopez-Garcia, Eric J. Hochberg, Yadvinder '
             'Malhi, Lisa M. Wedding',
  'venue': 'Royal Society Open Science 12(5), 241471 (2025)',
  'links': [('doi:10.1098/rsos.241471', 'https://doi.org/10.1098/rsos.241471')],
  'evidence': 'Crossref lists Pirta Palola at School of Geography and the Environment, University of Oxford; Rosalie '
              'Wright at School of Geography and the Environment, University of Oxford.',
  'does': 'Treats the interpretation of remote-sensing reflectance over coral reefs as an ill-posed inverse problem, '
          'since several combinations of water constituents, depth and bottom reflectance give similar signals, and '
          'solves it by simulation-based inference: a physics-based model with approximate Bayesian inference and '
          'machine learning gives posterior ranges of phytoplankton, suspended minerals, coloured dissolved organic '
          'matter, wind and depth, applied to in situ and drone data.',
  'route': 'The same structure as chloride attribution: a mixture of constituents, a forward model, and many '
           'combinations that fit; the answer is a posterior range, not a point.',
  'gap': 'The posterior range is as valid as the simulated prior; the authors note that mixtures of several bottom '
         'types are not yet handled.',
  'step': 'ZANAFILLA-GO keeps the learned posterior for speed but checks it against prior-free bounds. In our test '
          'the network covered <<nn_cov_a0>> of the truths in its own world and <<nn_cov_a1>> in a shifted one; the '
          'bounds covered <<ce_cov_a1>>.',
  'routes': ['learn', 'inverse'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'O5',
  'inst': 'Oxford',
  'year': 2025,
  'short': 'Sparse identification with stability',
  'title': 'Sparse identification of nonlocal interaction kernels in nonlinear gradient flow equations via partial '
           'inversion',
  'authors': 'José A. Carrillo, Gissell Estrada-Rodriguez, László Mikolás, Sui Tang',
  'venue': 'Mathematical Models and Methods in Applied Sciences 35(05), 1073–1131 (2025)',
  'links': [('doi:10.1142/s0218202525500137', 'https://doi.org/10.1142/s0218202525500137')],
  'evidence': 'Crossref lists José A. Carrillo at Mathematical Institute, University of Oxford, Woodstock Road, '
              'Oxford OX2 6GG, UK; László Mikolás at Mathematical Institute, University of Oxford, Woodstock Road, '
              'Oxford OX2 6GG, UK.',
  'does': 'Identifies nonlocal interaction potentials in aggregation–diffusion equations from noisy trajectory data '
          'by a regularised variational problem with a sparsity-enhancing penalty, solved by a partial-inversion '
          'algorithm akin to CoSaMP; proves a stability estimate in which the error functional controls the '
          '2-Wasserstein distance between true and estimated solutions, and analyses discretisation and observation '
          'errors.',
  'route': 'How an ill-posed identification is made stable: a stability estimate tied to the data functional, and '
           'sparsity as the principle that selects among explanations that fit.',
  'gap': 'A point estimate selected by a sparsity prior; the set of explanations that fit equally well is not '
         'described.',
  'step': "Proposition 3 is the set-valued counterpart: Hoffman's bound makes the identified set Lipschitz-stable in "
          'the data without selecting a sparse member. A sparsity rule can still be applied inside the set, reported '
          'as a selection.',
  'routes': ['inverse'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'C1',
  'inst': 'Caltech',
  'year': 2026,
  'short': 'Which ensemble Kalman inversion is fastest',
  'title': 'The Ensemble Kalman Inversion Race',
  'authors': 'Rebecca Gjini, Matthias Morzfeld, Oliver R. A. Dunbar, Tapio Schneider',
  'venue': 'Journal of Advances in Modeling Earth Systems 18(9), e2025MS005629 (2026)',
  'links': [('doi:10.1029/2025ms005629', 'https://doi.org/10.1029/2025ms005629')],
  'evidence': 'Crossref lists Oliver R. A. Dunbar at California Institute of Technology Pasadena CA USA; Tapio '
              'Schneider at California Institute of Technology Pasadena CA USA.',
  'does': 'Compares ensemble Kalman methods and a derivative-based method in a "race" to a given accuracy when '
          'calibrating parameters of Lorenz-type models, some with neural-network parameterisations, to statistics '
          'of their output, and studies how prior information and the dimensions of parameters and data set the '
          'cost.',
  'route': 'Derivative-free calibration to statistics is the practical engine for inverse problems whose forward '
           'model is a simulator, as a variable-density aquifer model is.',
  'gap': 'Point calibration with Gaussian-type uncertainty; no identified set and no check against model error.',
  'step': 'When ZANAFILLA-GO couples the attribution to a flow model (the site caps replaced by transport '
          'constraints), ensemble Kalman inversion is the tool for the hydraulic parameters, while the chloride '
          'shares keep their prior-free bounds.',
  'routes': ['inverse'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'C2',
  'inst': 'Caltech',
  'year': 2026,
  'short': 'How stable is a posterior to its prior',
  'title': 'Bayesian Posterior Perturbation Analysis with Integral Probability Metrics',
  'authors': 'Alfredo Garbuno-Iñigo, Tapio Helin, Franca Hoffmann, Bamdad Hosseini',
  'venue': 'Bayesian Analysis, advance publication (2026)',
  'links': [('doi:10.1214/26-ba1608', 'https://doi.org/10.1214/26-ba1608')],
  'evidence': 'Crossref lists Franca Hoffmann at Computing and Mathematical Sciences, California Institute of '
              'Technology, Pasadena, CA, USA.',
  'does': 'Analyses the robustness of Bayesian inference for large inverse problems by bounding how posterior '
          'measures change under perturbations of the likelihood potential and of the prior, with new families of '
          'integral probability metrics adapted to the problem and likelihoods that are only locally Lipschitz.',
  'route': 'It measures what matters most for chloride attribution: how far the answer moves when the prior moves.',
  'gap': 'Stability between posteriors, not an answer that is free of the prior where the data are silent.',
  'step': 'Inside the identified set any posterior is the prior. ZANAFILLA-GO reports the set, so the reach of the '
          'prior becomes visible: a mean width of <<all_w>> with seven tracers in our test is how far a prior could '
          'move the share.',
  'routes': ['inverse', 'ident'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'C3',
  'inst': 'Caltech',
  'year': 2025,
  'short': 'Source and path, separated by Bayes',
  'title': "DeepGEM‐EGF: A Bayesian Strategy for Joint Estimates of Source‐Time Functions and Empirical Green's "
           'Functions',
  'authors': 'Théa Ragon, Angela F. Gao, Zachary E. Ross',
  'venue': 'Journal of Geophysical Research: Solid Earth 130(12), e2025JB031260 (2025)',
  'links': [('doi:10.1029/2025jb031260', 'https://doi.org/10.1029/2025jb031260')],
  'evidence': 'Crossref lists Théa Ragon at Seismological Laboratory California Institute of Technology Pasadena CA '
              'USA; Angela F. Gao at Computing and Mathematical Sciences Department California Institute of '
              'Technology Pasadena CA USA.',
  'does': 'Isolating an earthquake source from a record is an ill-posed inverse problem in which source and path '
          'trade off. DeepGEM-EGF, a Bayesian framework built on an unsupervised generalised '
          'expectation–maximisation method, estimates the source-time function and its uncertainty jointly with the '
          "best empirical Green's function, to separate source variability from biases of modelling assumptions.",
  'route': 'The analogue of estimating mixing fractions jointly with uncertain end-member signatures: when both are '
           'unknown, their trade-off is the ill-posedness.',
  'gap': "The joint posterior depends on the prior Green's functions; the trade-off is propagated, not bounded.",
  'step': 'ZANAFILLA-GO treats the signatures as unknowns in intervals jointly with the fractions (Proposition 1), '
          "and shows when measuring the end-member (the Green's function of the analogy) is worth more than more "
          'data at the wells: decidability <<all_d>> with seven tracers, <<rf_all_d>> with two end-members sampled.',
  'routes': ['mixing', 'learn'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'C4',
  'inst': 'Caltech',
  'year': 2022,
  'short': 'Ratios remove shared unknowns',
  'title': 'Bayesian differential moment tensor inversion: theory and application to the North Korea nuclear tests',
  'authors': 'Zhe Jia, Zhongwen Zhan, Donald Helmberger',
  'venue': 'Geophysical Journal International 229(3), 2034–2046 (2022)',
  'links': [('doi:10.1093/gji/ggac053', 'https://doi.org/10.1093/gji/ggac053')],
  'evidence': 'Crossref lists Zhe Jia at Seismological Laboratory, California Institute of Technology , Pasadena, CA '
              '91125, USA; Zhongwen Zhan at Seismological Laboratory, California Institute of Technology , Pasadena, '
              'CA 91125, USA.',
  'does': 'A differential moment-tensor inversion uses amplitude ratios between clustered events to remove the path '
          'effects they share, and samples the posterior by Markov chain Monte Carlo with regular inversions as '
          'prior; for three North Korean nuclear tests it reduces the uncertainties substantially.',
  'route': 'Ratios cancel what is common and unknown: the principle behind Cl/Br and B/Cl, which cancel dilution by '
           'fresh water.',
  'gap': 'Bayesian with an informative prior from earlier inversions; no prior-free statement.',
  'step': 'ZANAFILLA-GO uses ratio tracers in exactly this sense (contributions proportional to the chloride of each '
          'source in Proposition 1), and two screens of one well, or two dates, share signatures: a differential '
          'constraint that would tighten the set without a prior.',
  'routes': ['inverse', 'mixing'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'M1',
  'inst': 'MIT',
  'year': 2022,
  'short': 'Road salt, sewage or basin brine',
  'title': 'Natural and Anthropogenic Processes Affecting Domestic Groundwater Quality within the Northwestern '
           'Appalachian Basin',
  'authors': 'H. G. Siegel, M. A. Soriano, C. J. Clark, N. P. Johnson, H. G. Wulsin, N. C. Deziel, D. L. Plata, T. '
             'H. Darrah, J. E. Saiers',
  'venue': 'Environmental Science & Technology 56(19), 13761–13773 (2022)',
  'links': [('doi:10.1021/acs.est.2c04011', 'https://doi.org/10.1021/acs.est.2c04011')],
  'evidence': 'Crossref lists D. L. Plata at Department of Civil and Environmental Engineering, Massachusetts '
              'Institute of Technology, Cambridge, Massachusetts 02139, United States.',
  'does': 'Studies the natural and anthropogenic processes that control domestic well water in the north-western '
          'Appalachian Basin (Ohio and West Virginia). The abstract could not be read; a search summary of the '
          'PubMed record describes 216 well samples and an attribution linking upland salinity to road salt and '
          'sewage, and valley groundwater to mixing with long-residence basin brines and a small share of '
          'mine-discharge-like water.',
  'route': 'The closest analogue among the thirty to our question: chloride from several anthropogenic and natural '
           'end-members, attributed from multi-solute well chemistry.',
  'gap': 'As far as the summary shows, the attribution is categorical; its uncertainty under uncertain end-members '
         'is not reported.',
  'step': 'ZANAFILLA-GO turns such categories into identified intervals per well and says which wells are decidable; '
          'the halite brine and the unlisted deep brine of our test play the parts of road salt and basin brine.',
  'routes': ['tracers', 'mixing'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); Crossref has no '
            'abstract, and the description rests on a search summary of the PubMed record, not on the abstract '
            'itself.'},
 {'id': 'M2',
  'inst': 'MIT',
  'year': 2020,
  'short': 'A groundwater isoscape by random forest',
  'title': 'Isotopic variation in groundwater across the conterminous United States – Insight into hydrologic '
           'processes',
  'authors': 'Mason O. Stahl, Jaclyn Gehring, Yusuf Jameel',
  'venue': 'Hydrological Processes 34(16), 3506–3523 (2020)',
  'links': [('doi:10.1002/hyp.13832', 'https://doi.org/10.1002/hyp.13832')],
  'evidence': 'Crossref lists Yusuf Jameel at Department of Civil and Environmental Engineering Massachusetts '
              'Institute of Technology Cambridge Massachusetts USA.',
  'does': 'Builds a random-forest model of shallow groundwater δ²H and δ¹⁸O for the conterminous United States from '
          'environmental predictors (temperature, elevation, precipitation isotopes), maps the first groundwater '
          'isoscape and describes the hydrological processes behind its patterns.',
  'route': 'An isoscape is a prior for the fresh-water end-member: the isotopic signature of local recharge where it '
           'was not measured.',
  'gap': 'A predicted map, without a guaranteed interval at a given site.',
  'step': 'In ZANAFILLA-GO a learned isoscape can give the interval of the fresh end-member where it was not '
          "sampled, widened by the model's calibrated error. In our test sampling the fresh end-member added little "
          'once the relict water was known (<<rel_all_d>> to <<rf_all_d>>): a good isoscape may be enough for the '
          'fresh water.',
  'routes': ['tracers', 'learn'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'M3',
  'inst': 'MIT',
  'year': 2024,
  'short': 'Radium budget of coastal exchange',
  'title': 'Seasonality of submarine groundwater discharge to an Arctic coastal lagoon',
  'authors': 'Emma J. Bullock, Isabel V. Schaal, M. Bayani Cardenas, James W. McClelland, Paul B. Henderson, Matthew '
             'A. Charette',
  'venue': 'Limnology and Oceanography 69(6), 1429–1438 (2024)',
  'links': [('doi:10.1002/lno.12585', 'https://doi.org/10.1002/lno.12585')],
  'evidence': 'Crossref lists Emma J. Bullock at MIT‐WHOI Joint Program in Oceanography/Applied Ocean Science and '
              'Engineering Cambridge and Woods Hole Massachusetts USA; Isabel V. Schaal at MIT‐WHOI Joint Program in '
              'Oceanography/Applied Ocean Science and Engineering Cambridge and Woods Hole Massachusetts USA.',
  'does': 'Quantifies supra-permafrost submarine groundwater discharge to an Arctic lagoon (Simpson Lagoon, Alaska) '
          'with a radium-isotope mass balance over five periods in 2021–2023: none under spring ice, and between '
          'about 6 and 79 million m³ per day otherwise, driven by wind-driven changes of lagoon level rather than by '
          'tides.',
  'route': 'Exchange across the coast runs both ways and varies with forcing; radium isotopes measure it, and with '
           'it the recirculation of seawater through coastal sediments.',
  'gap': 'A coastal flux budget, not the attribution of the chloride of inland wells.',
  'step': 'Short-lived radium isotopes are candidate tracers of recent contact with seawater, the very distinction '
          'between modern and relict seawater on which our test turns; in ZANAFILLA-GO they enter as one more '
          'water-weighted contribution, near zero for the relict end-member.',
  'routes': ['tracers'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'M4',
  'inst': 'MIT',
  'year': 2024,
  'short': 'Posterior contraction for Darcy flow',
  'title': 'Laplace priors and spatial inhomogeneity in Bayesian inverse problems',
  'authors': 'Sergios Agapiou, Sven Wang',
  'venue': 'Bernoulli 30(2), 878–910 (2024)',
  'links': [('doi:10.3150/22-bej1563', 'https://doi.org/10.3150/22-bej1563')],
  'evidence': 'Crossref lists Sven Wang at Institute for Data, Systems and Society, Massachusetts Institute of '
              'Technology, Cambridge, USA.',
  'does': 'Proves frequentist posterior contraction rates for Besov (Laplace) priors in nonlinear inverse problems '
          'with Gaussian white noise, under a local Lipschitz condition on the forward map that is verified for the '
          'Darcy flow model and a Schrödinger model, with new concentration inequalities for penalised least '
          'squares.',
  'route': 'The rigorous side of the Bayesian route: when the parameter is identified, the posterior concentrates on '
           'the truth at a known rate.',
  'gap': 'Identification is assumed; for overlapping end-members there is no single truth to contract to.',
  'step': 'ZANAFILLA-GO marks the boundary of such theorems: what contracts is the identified set, as tracers and '
          "end-member samples are added (mean width <<today_w>> with today's data, <<rf_all_w>> with seven tracers "
          'and two end-members sampled).',
  'routes': ['inverse'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'M5',
  'inst': 'MIT',
  'year': 2022,
  'short': 'Physics-informed networks find hidden structure',
  'title': 'Analyses of internal structures and defects in materials using physics-informed neural networks',
  'authors': 'Enrui Zhang, Ming Dao, George Em Karniadakis, Subra Suresh',
  'venue': 'Science Advances 8(7), eabk0644 (2022)',
  'links': [('doi:10.1126/sciadv.abk0644', 'https://doi.org/10.1126/sciadv.abk0644')],
  'evidence': 'Crossref lists Ming Dao at Department of Materials Science and Engineering, Massachusetts Institute '
              'of Technology, Cambridge, MA 02139, USA.',
  'does': 'Uses physics-informed neural networks with a differentiable, mesh-free parameterisation of geometry to '
          'identify the size, shape and location of internal voids or inclusions and their elastic modulus, for '
          'linear elastic, hyperelastic and plastic materials.',
  'route': 'Physics-informed learning locates hidden structure from boundary data: the task of locating a relict '
           'pocket or a halite body from well data and a flow model.',
  'gap': 'One recovered structure; the non-uniqueness of the inverse problem is not quantified.',
  'step': 'A physics-informed or adjoint flow model would give ZANAFILLA-GO the transport constraints it lacks (now '
          'only site caps); the attribution stays set-valued, with the learned field generating constraints rather '
          'than being the answer.',
  'routes': ['learn', 'inverse'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'P1',
  'inst': 'Princeton',
  'year': 2026,
  'short': 'Groundwater discharge and estuary salinity',
  'title': 'Impact of Groundwater‐Surface Water Interaction on the Chesapeake Bay Density, Stratification and Mixing '
           'Under Normal and Extreme Weather Conditions',
  'authors': 'Seyedeh Fardis Pourreza Ahmadi, Bishnupriya Sahoo, Chen Yang, Reed Maxwell, Meng Xia',
  'venue': 'Journal of Geophysical Research: Oceans 131(8), e2026JC024172 (2026)',
  'links': [('doi:10.1029/2026jc024172', 'https://doi.org/10.1029/2026jc024172')],
  'evidence': 'Crossref lists Chen Yang at Princeton University Princeton NJ USA; Reed Maxwell at Princeton '
              'University Princeton NJ USA.',
  'does': 'Couples a groundwater model (ParFlow) one way to an estuarine circulation model (FVCOM) to quantify how '
          'the submarine discharge of meteoric groundwater changes salinity, density, stratification and mixing in '
          'Chesapeake Bay: the effects vary in space and season, grow at low river flow, and during Hurricane Ida '
          'the elevated discharge reduced salinity by 20%; sensitivity experiments address the uncertain discharge '
          'volume.',
  'route': 'Salinity at a point is the outcome of mixing between land and sea waters whose proportions are set by '
           'flow; a coupled model gives those proportions physically.',
  'gap': 'Forward modelling with sensitivity runs; no inversion of the sources from observed chemistry.',
  'step': 'A coupled groundwater model would supply ZANAFILLA-GO with transport constraints that link the fractions '
          'of neighbouring screens, the piece missing from our test (Section 6.4); an uncertain discharge volume '
          'becomes an interval, not a scenario.',
  'routes': ['mixing'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'P2',
  'inst': 'Princeton',
  'year': 2025,
  'short': 'Deep-learning inversion of a continental model',
  'title': 'A Deep‐Learning Based Parameter Inversion Framework for Large‐Scale Groundwater Models',
  'authors': 'Amanda Triplett, Andrew Bennett, Laura E. Condon, Peter Melchior, Reed M. Maxwell',
  'venue': 'Geophysical Research Letters 52(8), e2024GL114285 (2025)',
  'links': [('doi:10.1029/2024gl114285', 'https://doi.org/10.1029/2024gl114285')],
  'evidence': 'Crossref lists Peter Melchior at Department of Astrophysical Sciences Princeton University Princeton '
              'NJ USA; Reed M. Maxwell at Integrated Groundwater Modeling Center Princeton University Princeton NJ '
              'USA.',
  'does': 'Trains an inversion network that learns the relation between water-table depth and hydraulic conductivity '
          'from a small number of physical simulations, and produces a reliable conductivity field for a '
          '31-million-cell model of the United States from 30 training simulations; limitations remain for '
          'parameters outside the training sample.',
  'route': 'Learned inversion makes very large aquifer models calibratable; the authors flag the limit outside the '
           'training sample.',
  'gap': 'Validity outside the training sample, the failure that our shifted world exposes.',
  'step': 'ZANAFILLA-GO pairs such learned inversions with a prior-free check: in our test the learned attribution '
          'covered <<nn_cov_a0>> in its training world and <<nn_cov_a1>> out of it, and the check flagged the worst '
          'cases.',
  'routes': ['learn', 'inverse'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'P3',
  'inst': 'Princeton',
  'year': 2026,
  'short': 'How sparse, how noisy: inverse PINNs',
  'title': 'How sparse and how noisy? Systematic benchmarking of inverse physics-informed neural networks for '
           'Manning friction estimation in shallow water equations',
  'authors': 'Soheil Radfar',
  'venue': 'Physics of Fluids 38(8), 086611 (2026)',
  'links': [('doi:10.1063/5.0349054', 'https://doi.org/10.1063/5.0349054')],
  'evidence': 'Crossref lists Soheil Radfar at Department of Civil and Environmental Engineering, Princeton '
              'University , Princeton, New Jersey 08544,.',
  'does': 'Benchmarks inverse physics-informed neural networks that recover the Manning friction coefficient of the '
          'shallow-water equations under controlled sparsity and noise of the observations and different observed '
          'variables, on a one-dimensional channel with an analytical reference and a two-dimensional channel '
          'computed with a finite-volume solver.',
  'route': 'A systematic answer to "how much data, how noisy, which variable" for a learned inversion: the design '
           'question of Proposition 5 asked of a network.',
  'gap': 'One identified scalar; non-identified cases are not treated.',
  'step': 'Asked of the chloride attribution, the same question has a different answer: not more data at the wells '
          '(<<all_d>> decidable with seven tracers) but the end-members (<<rf_all_d>> with two sampled).',
  'routes': ['learn', 'ident'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'P4',
  'inst': 'Princeton',
  'year': 2026,
  'short': 'Two datasets make it identifiable',
  'title': 'Two datasets are better than one: method of double moments for 3D reconstruction in cryo-EM',
  'authors': 'Joe Kileel, Oscar Mickelin, Amit Singer, Sheng Xu',
  'venue': 'Inverse Problems 42(7), 075016 (2026)',
  'links': [('doi:10.1088/1361-6420/ae7fb2', 'https://doi.org/10.1088/1361-6420/ae7fb2')],
  'evidence': 'Crossref lists Amit Singer at Princeton University; Sheng Xu at Princeton University.',
  'does': 'Reconstructs molecular structures in cryo-electron microscopy from the second-order moments of two '
          'datasets taken under different orientation distributions, one uniform and one unknown; proves that these '
          'moments generically determine the structure up to rotation and reflection, and gives a convex-relaxation '
          'algorithm.',
  'route': 'Identifiability gained by combining datasets collected under different conditions: the logic of sampling '
           'an end-member in addition to the wells.',
  'gap': 'Generic uniqueness; the set when uniqueness fails is not treated.',
  'step': 'ZANAFILLA-GO makes the same point quantitatively for chloride: a dataset of a different kind (the '
          'end-members themselves) turns undecidable samples into decidable ones, and Proposition 5 values each '
          'dataset by its gain in decidability.',
  'routes': ['ident', 'inverse'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'X1',
  'inst': 'Max Planck',
  'year': 2026,
  'short': 'A second tracer that shares the error',
  'title': 'Can radon help to improve methane emission estimates? Results from a dual-tracer inversion',
  'authors': 'Fabian Maier, Christian Rödenbeck, Ute Karstens, Frank-Thomas Koch, Maksym Gachkivskyi, Andrew '
             'Smerald, Christoph Gerbig',
  'venue': 'Atmospheric Chemistry and Physics 26(20), 14699–14723 (2026)',
  'links': [('doi:10.5194/acp-26-14699-2026', 'https://doi.org/10.5194/acp-26-14699-2026')],
  'evidence': 'Crossref lists Fabian Maier at Max Planck Institute for Biogeochemistry (Jena, Germany).',
  'does': 'Uses radon, a natural tracer of vertical mixing, jointly with methane in an inversion of methane '
          'emissions, exploiting the correlation of transport-model errors between the two gases at 17 European '
          'sites in 2021; the dual-tracer inversion gives country totals a few percent lower than the methane-only '
          'inversion, with a dependence on the assumed uncertainty of the radon fluxes.',
  'route': 'A tracer chosen not for the source but for the error it shares with the target: the part bromide or '
           'boron play in separating dilution from origin.',
  'gap': 'A Bayesian inversion whose result depends on prior flux uncertainties, as the authors note.',
  'step': 'In ZANAFILLA-GO a second tracer is a constraint on shared contributions, its value is judged by the gain '
          'in decidability, and its prior uncertainty becomes an interval, so the answer cannot depend on it more '
          'than the interval allows.',
  'routes': ['tracers', 'inverse'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'X2',
  'inst': 'Max Planck',
  'year': 2022,
  'short': 'Field inference and generative networks',
  'title': 'Information Field Theory and Artificial Intelligence',
  'authors': 'Torsten Enßlin',
  'venue': 'Entropy 24(3), 374 (2022)',
  'links': [('doi:10.3390/e24030374', 'https://doi.org/10.3390/e24030374')],
  'evidence': 'Crossref lists Torsten Enßlin at Max Planck Institute for Astrophysics, Karl-Schwarzschild-Strasse 1, '
              '85748 Garching, Germany.',
  'does': 'Relates information field theory, a Bayesian framework for signal reconstruction and non-parametric '
          'inverse problems for fields, to artificial intelligence and machine learning: reconstructing a signal '
          'with information field theory is a computational problem similar to training a generative neural network.',
  'route': 'A common language for the spatial side of the problem: the shares of the sources are fields over the '
           'aquifer, not numbers at wells.',
  'gap': 'Prior-driven reconstruction of fields; identifiability is not separated from the prior.',
  'step': 'ZANAFILLA-GO treats each screen on its own; coupling the screens through a field model would add '
          'constraints across wells, and the set-valued answer would still show what remains undetermined.',
  'routes': ['learn', 'inverse'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'X3',
  'inst': 'Max Planck',
  'year': 2020,
  'short': 'Neural posterior estimation for mechanistic models',
  'title': 'Training deep neural density estimators to identify mechanistic models of neural dynamics',
  'authors': 'Pedro J Gonçalves, Jan-Matthis Lueckmann, Michael Deistler, Marcel Nonnenmacher, Kaan Öcal, Giacomo '
             'Bassetto, Chaitanya Chintaluri, William F Podlaski, Sara A Haddad, Tim P Vogels, David S Greenberg, '
             'Jakob H Macke',
  'venue': 'eLife 9, e56261 (2020)',
  'links': [('doi:10.7554/elife.56261', 'https://doi.org/10.7554/elife.56261')],
  'evidence': 'Crossref lists Pedro J Gonçalves at Max Planck Research Group Neural Systems Analysis, Center of '
              'Advanced European Studies and Research (caesar), Bonn, Germany; Jan-Matthis Lueckmann at Max Planck '
              'Research Group Neural Systems Analysis, Center of Advanced European Studies and Research (caesar), '
              'Bonn, Germany.',
  'does': 'Trains deep neural density estimators on model simulations to perform Bayesian inference and retrieve the '
          'full space of parameters compatible with data or data features; amortised for new data and demonstrated '
          'on receptive fields, ion channels, Hodgkin–Huxley models and the stomatogastric ganglion, where many '
          'circuit configurations give the same rhythm.',
  'route': 'The tool that made amortised Bayesian inference practical, aimed explicitly at the whole space of '
           'compatible parameters: the degeneracy that is our ill-posedness.',
  'gap': 'Compatibility is weighted by the prior; parts of the compatible set with little prior mass are '
         'under-represented.',
  'step': 'Our network is a simple member of this route; ZANAFILLA-GO pairs it with the exact compatible set '
          '(Proposition 1), so a degenerate direction is reported in full and not in proportion to its prior mass.',
  'routes': ['learn'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'X4',
  'inst': 'Max Planck',
  'year': 2025,
  'short': 'Amortised inference with adaptive priors',
  'title': 'Fast and reliable probabilistic reflectometry inversion with prior-amortized neural posterior estimation',
  'authors': 'Vladimir Starostin, Maximilian Dax, Alexander Gerlach, Alexander Hinderhofer, Álvaro Tejero-Cantero, '
             'Frank Schreiber',
  'venue': 'Science Advances 11(11), eadr9668 (2025)',
  'links': [('doi:10.1126/sciadv.adr9668', 'https://doi.org/10.1126/sciadv.adr9668')],
  'evidence': 'Crossref lists Maximilian Dax at Max Planck Institute for Intelligent Systems, Tübingen, Germany.',
  'does': 'Prior-amortised neural posterior estimation combines simulation-based inference with adaptive priors that '
          'encode known structural properties and controllable experimental conditions, and finds all realistic '
          'thin-film structures compatible with reflectometry data in seconds, where standard algorithms report a '
          'single solution.',
  'route': 'It attacks the "single solution" failure of inversion with a learned posterior conditioned on the prior '
           'itself, so that the prior can be changed without retraining.',
  'gap': 'Reliability still rests on the family of priors used in training.',
  'step': 'Prior-amortisation would let ZANAFILLA-GO compute posteriors under many priors at once; the envelope of '
          'those posteriors approaches the identified set, which the linear programmes give exactly.',
  'routes': ['learn', 'ident'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'H1',
  'inst': 'Harvard',
  'year': 2024,
  'short': 'Deep fluid fluxes in the Anthropocene',
  'title': 'Acceleration of Deep Subsurface Fluid Fluxes in the Anthropocene',
  'authors': 'Grant Ferguson, Lydia R. Bailey, Ji‐Hyun Kim, Magdalena R. Osburn, Peter W. Reiners, Henrik Drake, '
             'Bradley S. Stevenson, Jennifer C. McIntosh',
  'venue': "Earth's Future 12(4), e2024EF004496 (2024)",
  'links': [('doi:10.1029/2024ef004496', 'https://doi.org/10.1029/2024ef004496')],
  'evidence': 'Crossref lists Lydia R. Bailey at Department of Earth & Planetary Sciences Harvard University '
              'Cambridge MA USA.',
  'does': 'Shows that fluid fluxes from extraction and injection in oil and gas production and from inflow into '
          'mines likely exceed background flow rates in deep (>500 m) groundwater systems globally, and that carbon '
          'storage, geothermal energy and lithium extraction will need larger fluid production still; natural '
          'analogues and geochemical modelling suggest the changes will be recorded in rocks.',
  'route': 'Human activity now moves deep saline fluids faster than nature: brine from depth becomes a plausible '
           'source of chloride where it was not.',
  'gap': 'Global fluxes, not attribution at a well.',
  'step': 'A source list that ignores such movement can be refuted by the existence test of ZANAFILLA-GO, which '
          'flagged an unlisted brine in <<miss_0>> to <<miss_1>> of the affected samples of our test.',
  'routes': ['tracers'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'H2',
  'inst': 'Harvard',
  'year': 2023,
  'short': 'Partial identification, reviewed',
  'title': 'Recent Developments in Partial Identification',
  'authors': 'Brendan Kline, Elie Tamer',
  'venue': 'Annual Review of Economics 15(1), 125–150 (2023)',
  'links': [('doi:10.1146/annurev-economics-051520-021124',
             'https://doi.org/10.1146/annurev-economics-051520-021124')],
  'evidence': 'Crossref lists Elie Tamer at Department of Economics, Harvard University, Cambridge, Massachusetts, '
              'USA.',
  'does': 'Reviews partial identification: what can be learned about a parameter from the data and the model '
          'assumptions when its exact value cannot be, typically as an identified set; surveys the general '
          'frameworks and recent results.',
  'route': 'The mathematical core of our answer: when the data cannot point-identify the share of a source, the '
           'right object is the identified set.',
  'gap': 'Developed for econometric models; not applied to hydrochemical unmixing.',
  'step': 'ZANAFILLA-GO brings partial identification to chloride attribution and shows that for unmixing with '
          'interval end-members the identified set is an exact polytope (Proposition 1) with sharp bounds by linear '
          'programming (Proposition 2).',
  'routes': ['ident'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'H3',
  'inst': 'Harvard',
  'year': 2024,
  'short': 'Assumption-free bounds, and their width',
  'title': 'Partial Identification of the Effects of Sustained Treatment Strategies',
  'authors': 'Elizabeth W. Diemer, Joy Shi, Sonja A. Swanson',
  'venue': 'Epidemiology 35(3), 308–312 (2024)',
  'links': [('doi:10.1097/ede.0000000000001721', 'https://doi.org/10.1097/ede.0000000000001721')],
  'evidence': 'Crossref lists Elizabeth W. Diemer at CAUSALab, Harvard T.H. Chan School of Public Health, Boston, '
              'MA; Joy Shi at CAUSALab, Harvard T.H. Chan School of Public Health, Boston, MA.',
  'does': 'Derives assumption-free bounds for the effects of static and dynamic sustained interventions, under '
          'consistency and the data alone, relates them to clone-censor-weight estimation, and notes that the bounds '
          'are often wide, which shows how much an analysis depends on unverifiable assumptions.',
  'route': 'Wide bounds are information: they measure how much an answer owes to assumptions, the message of our '
           "wide intervals with today's data.",
  'gap': 'Causal effects in epidemiology; no design to narrow the bounds.',
  'step': "ZANAFILLA-GO adds the next step: when the bounds are wide (mean width <<today_w>> with today's data), "
          'Proposition 5 chooses the measurement that narrows them most for the decision.',
  'routes': ['ident'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'H4',
  'inst': 'Harvard',
  'year': 2021,
  'short': 'Deep-learning intervals lose coverage',
  'title': 'Empirical Frequentist Coverage of Deep Learning Uncertainty Quantification Procedures',
  'authors': 'Benjamin Kompa, Jasper Snoek, Andrew L. Beam',
  'venue': 'Entropy 23(12), 1608 (2021)',
  'links': [('doi:10.3390/e23121608', 'https://doi.org/10.3390/e23121608')],
  'evidence': 'Crossref lists Benjamin Kompa at Department of Biomedical Informatics, Harvard Medical School, '
              'Boston, MA 02115, USA; Andrew L. Beam at Department of Biomedical Informatics, Harvard Medical '
              'School, Boston, MA 02115, USA.',
  'does': 'Evaluates the empirical frequentist coverage and the width of prediction intervals of common '
          'uncertainty-quantification methods for deep learning on regression and classification tasks: some reach '
          'good coverage in distribution, but coverage is not maintained on out-of-distribution data and degrades as '
          'the shift grows.',
  'route': 'The general finding behind our network test: learned intervals are valid in the training world and fail '
           'under shift.',
  'gap': 'A diagnosis, not a remedy that keeps coverage under shift.',
  'step': 'ZANAFILLA-GO supplies a remedy for chloride attribution: a prior-free bound that kept <<ce_cov_a1>> '
          'coverage where the network fell to <<nn_cov_a1>>.',
  'routes': ['learn'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'B1',
  'inst': 'Berkeley',
  'year': 2022,
  'short': 'Transit times, reviewed',
  'title': 'Transit Time Estimation in Catchments: Recent Developments and Future Directions',
  'authors': 'Paolo Benettin, Nicolas B. Rodriguez, Matthias Sprenger, Minseok Kim, Julian Klaus, Ciaran J. Harman, '
             'Ype van der Velde, Markus Hrachowitz, Gianluca Botter, Kevin J. McGuire, James W. Kirchner, Andrea '
             'Rinaldo, Jeffrey J. McDonnell',
  'venue': 'Water Resources Research 58(11), e2022WR033096 (2022)',
  'links': [('doi:10.1029/2022wr033096', 'https://doi.org/10.1029/2022wr033096')],
  'evidence': 'Crossref lists James W. Kirchner at Department of Earth and Planetary Science University of '
              'California Berkeley CA USA.',
  'does': 'Reviews water transit time estimation in catchments since the last comprehensive review: '
          'water-age-balance approaches (StorAge Selection functions, mixed compartments, age tracking in '
          'distributed models) and data-based approaches (controlled experiments, young water fractions, ensemble '
          'hydrograph separation), unifying the literature and listing open questions.',
  'route': 'Age is the variable that separates modern from relict water; this review is the toolbox for turning '
           'tracer data into ages.',
  'gap': 'Catchments and fresh water; sources of salinity are not its subject.',
  'step': 'Young-water fractions are linear mixing quantities and enter ZANAFILLA-GO directly as water-weighted '
          'contributions; an age tracer at the relict end-member is the kind of action that raised decidability most '
          'in our test.',
  'routes': ['tracers', 'mixing'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'B2',
  'inst': 'Berkeley',
  'year': 2021,
  'short': 'Recycled-water recharge against the sea',
  'title': 'Groundwater Recharge to Address Seawater Intrusion and Supply in an Urban Coastal Aquifer',
  'authors': 'Michael Kiparsky, Kathleen Miller, William Blomquist, Annapurna Holtzapple, Anita Milman',
  'venue': 'Case Studies in the Environment 5(1), 1223118 (2021)',
  'links': [('doi:10.1525/cse.2021.1223118', 'https://doi.org/10.1525/cse.2021.1223118')],
  'evidence': 'Crossref lists Michael Kiparsky at Center for Law, Energy & the Environment, University of '
              'California, Berkeley School of Law, Berkeley, CA, USA; Kathleen Miller at Center for Law, Energy & '
              'the Environment, University of California, Berkeley School of Law, Berkeley, CA, USA.',
  'does': 'A case study of the Orange County Water District, which fights seawater intrusion and secures supply by '
          'recharging treated recycled wastewater through injection barriers and infiltration ponds (Water Factory '
          '21 from 1975, the Groundwater Replenishment System from 2008), and of the arrangements that pay for it.',
  'route': 'Once recycled water is injected to stop the sea, chloride at a well can come from the sea or from the '
           'barrier: attribution decides whether the barrier works.',
  'gap': 'Governance and finance; the chemistry of attribution is not addressed.',
  'step': 'ZANAFILLA-GO would add the injected water as an end-member with a sampled, narrow signature and report '
          'per well the share of chloride from the sea with prior-free bounds: the monitoring a barrier needs.',
  'routes': ['mixing'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'B3',
  'inst': 'Berkeley',
  'year': 2025,
  'short': 'Bayesian unmixing of impact glass',
  'title': 'Inferences of Source Lithologies for Chicxulub Microtektites Using a Bayesian Approach',
  'authors': 'Jack Carter, Paolo Sanchez, Anthony J. Fuentes, Paul R. Renne, Dale H. Burns, Hermann D. Bermúdez',
  'venue': 'Geochemistry, Geophysics, Geosystems 26(3), e2024GC011924 (2025)',
  'links': [('doi:10.1029/2024gc011924', 'https://doi.org/10.1029/2024gc011924')],
  'evidence': 'Crossref lists Jack Carter at Department of Earth and Planetary Science University of California '
              'Berkeley Berkeley CA USA; Paolo Sanchez at Department of Earth and Planetary Science University of '
              'California Berkeley Berkeley CA USA.',
  'does': 'Uses 521 electron-probe analyses of 90 unaltered Chicxulub microtektites from Gorgonilla Island and a '
          'reversible-jump Bayesian mixture model to infer a six-component end-member mixture of target lithologies '
          '(granitoid about 70%, limestone 14%, mafic igneous 10%, shale 4%, anhydrite 0.3%, halite 0.1%) and lower '
          'bounds of volatile budgets.',
  'route': 'Bayesian unmixing with an unknown number of end-members, halite among them, from compositional data: '
           'methodologically the closest of the thirty to our problem.',
  'gap': 'The end-member compositions and their number rest on the prior and the model; directions the data do not '
         'identify are not reported as such.',
  'step': 'For the same kind of model ZANAFILLA-GO computes the prior-free identified interval of each component; '
          'reversible jump answers "how many sources", our existence test answers "is a source missing".',
  'routes': ['mixing', 'inverse'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'},
 {'id': 'B4',
  'inst': 'Berkeley',
  'year': 2020,
  'short': 'A second isotope narrows a mixing model',
  'title': 'Combined use of radiocarbon and stable carbon isotopes for the source mixing model in a stream food web',
  'authors': 'Naoto F. Ishikawa, Jacques C. Finlay, Hiromi Uno, Nanako O. Ogawa, Naohiko Ohkouchi, Ichiro Tayasu, '
             'Mary E. Power',
  'venue': 'Limnology and Oceanography 65(11), 2688–2696 (2020)',
  'links': [('doi:10.1002/lno.11541', 'https://doi.org/10.1002/lno.11541')],
  'evidence': 'Crossref lists Hiromi Uno at Department of Integrative Biology University of California Berkeley '
              'California USA; Mary E. Power at Department of Integrative Biology University of California Berkeley '
              'California USA.',
  'does': 'Measures radiocarbon (Δ¹⁴C) of stream invertebrates in the South Fork Eel River watershed, California: '
          'algae grazers carry old carbon (−43 ± 22‰), leaf shredders contemporary carbon (22 ± 32‰), predators lie '
          'in between; in a Bayesian mixing model Δ¹⁴C gives more realistic terrestrial and aquatic source '
          'contributions, with narrower credible intervals than δ¹³C alone.',
  'route': 'A source-mixing problem in which a tracer with well separated end-members narrows the answer: the design '
           'logic of Proposition 5, shown in the field.',
  'gap': 'Credible intervals that depend on the prior of a Bayesian mixing model; the value of the tracer is shown '
         'after the fact, not planned.',
  'step': 'ZANAFILLA-GO plans the value of a tracer before it is measured, by its expected gain in decidability, and '
          'reports prior-free intervals. In our test bromide added little on its own (<<today_d>> to <<br_d>>), '
          'while sampling the end-members added much.',
  'routes': ['mixing', 'tracers'],
  'status': 'verified through the Crossref record of the DOI (title, year, journal, affiliation); the abstract was '
            'read, the full text could not be opened from this environment.'}]
