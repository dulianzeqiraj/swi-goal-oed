"""The twenty-five paper cards of the review "From chaos in the pores to Darcy's law" (five per institution, 2020-2026):
Caltech, Oxford, MIT, Harvard and the Max Planck Society.

Bibliographic data: the Crossref record of each DOI.  Affiliations: the OpenAlex record of each DOI (looked up by DOI,
November 2026).  Content: the abstract of each paper (Crossref or OpenAlex; for H5 and P1 the abstract returned by a web
search of the publisher and arXiv pages).  The full texts could not be opened from the build environment, so no card
states more than its abstract supports; where a card adds general knowledge it says so.  The records are stored in
res/selected_papers.json.

Fields: id, inst, year, short, title, authors, venue, links, evidence, does, route (how the passage from the small to the
large scale is explained), gap (what it leaves open for our question), step (innovation step for our problem), routes (keys
of the explanation routes of Section 3: 'see' experiments and resolved simulations, 'hom' homogenisation, 'stat' statistical
physics and probability, 'diss' dissipation budgets, 'learn' learned closures).  <<key>> is a number filled in from
res/kaos.json by text_kaos.py."""

STATUS = ('verified through the Crossref and OpenAlex records of the DOI; the abstract was read, the full text could not '
          'be opened from this environment.')


def doi(d):
    return [('doi:' + d, 'https://doi.org/' + d)]


CALTECH = [
    dict(id='C1', inst='Caltech', year=2026, short='Where the instability is born in a 3-D medium',
         title='Stagnation points at grain contacts generate an elastic flow instability in 3-D porous media',
         authors='Emily Y. Chen, Christopher A. Browne, Simon J. Haward, Amy Q. Shen, Sujit S. Datta',
         venue='Journal of Fluid Mechanics 1034, A4 (2026)', links=doi('10.1017/jfm.2026.11458'),
         evidence='OpenAlex lists S. S. Datta at the California Institute of Technology and Princeton University, E. Y. '
                  'Chen and C. A. Browne at Princeton University, S. J. Haward and A. Q. Shen at the Okinawa Institute '
                  'of Science and Technology. This is the group of the Princeton article of Section 2; its head moved '
                  'to Caltech in 2024 (faculty page of the Caltech Division of Chemistry and Chemical Engineering).',
         does='Polymer-solution flow is imaged directly in microfabricated three-dimensional ordered media: '
              'simple-cubic and body-centred cuboid arrays of spherical grains. In both, the instability is generated '
              'at stagnation points at the **contacts between grains**, not at the upstream and downstream poles of '
              'the grains as for an isolated grain. In the simple-cubic packing it appears as fluctuating '
              'three-dimensional eddies, in the body-centred packing as fluctuating "wobbles" and crossing pathlines. '
              'The transition from steady to unsteady flow has common features in both, and the data indicate that '
              'extensional polymeric stresses generated at the contact stagnation points are the primary contributor '
              'to the macroscopic resistance.',
         route='Mechanism: geometry (grain contacts) → stagnation points → stretched polymers → unsteady flow; the '
               'macroscopic resistance is attributed to the stresses at those points.',
         gap='Ordered media and two unit cells; no statistical law for a disordered medium, no error bar on the '
             'upscaled resistance. Note the nuance with the 2021 article: there the excess resistance is the '
             'dissipation of the fluctuations, here it is tied to extensional stresses at fixed points.',
         step='KAOS-GO keeps both readings in one identity: the resistance is the total dissipation, split into the '
              'part of the time-mean flow and the part of the fluctuations (Proposition 1). In our Newtonian '
              'experiment both parts grow: at the highest Reynolds number the mean-flow part is <<Fmean_hi>> times the '
              'Darcy resistance and the fluctuations add <<Ffluct_hi>> times.',
         routes=['see', 'diss']),
    dict(id='C2', inst='Caltech', year=2025, short='Pores that remember each other',
         title='Influence of fluid rheology on multistability in the unstable flow of polymer solutions through pore '
               'constriction arrays',
         authors='Emily Y. Chen, Sujit S. Datta',
         venue='Journal of Rheology 69(2), 235–249 (2025)', links=doi('10.1122/8.0000896'),
         evidence='OpenAlex lists S. S. Datta at the California Institute of Technology and Princeton University and '
                  'E. Y. Chen at Princeton University.',
         does='In one-dimensional ordered arrays of pore constrictions, the unsteady flow above the elastic '
              'instability undergoes a second transition, to **multistability**: distinct pores show distinct unsteady '
              'flow states at the same time. Experiments with polymer solutions of systematically varied shear '
              'thinning and elasticity, in arrays of different geometry, show that the onset of multistability is '
              'described by one dimensionless parameter, given sufficient elasticity: the streamwise Deborah number, '
              'the stress relaxation time of the solution over the time of advection between constrictions.',
         route='A dimensionless number for memory between pores: when the polymers do not relax between two '
               'constrictions, neighbouring pores are coupled and the medium is not a sum of independent pores.',
         gap='One-dimensional arrays; no macroscopic law. Coupled pores break the independence on which every simple '
             'averaging argument rests.',
         step='KAOS-GO does not assume independent pores or independent time windows: the fluctuation term uses the '
              'measured correlation (the integral of the autocovariance), and a conformal multiplier protects the '
              'interval when that correlation is misjudged. In our experiment the memory of the flux is longest just '
              'above the onset of chaos (<<slow_tau>> pore transit times at Re = <<slow_re>>), and intervals that '
              'assume one pore transit of memory cover <<cov_naive>> instead of 90%.',
         routes=['see', 'stat']),
    dict(id='C3', inst='Caltech', year=2024, short='Learning the cell problem of homogenisation',
         title='Learning Homogenization for Elliptic Operators',
         authors='Kaushik Bhattacharya, Nikola B. Kovachki, Aakila Rajan, Andrew M. Stuart, Margaret Trautner',
         venue='SIAM Journal on Numerical Analysis 62(4), 1844–1873 (2024)', links=doi('10.1137/23M1585015'),
         evidence='OpenAlex lists K. Bhattacharya, A. Rajan, A. M. Stuart and M. Trautner at the California Institute '
                  'of Technology and N. B. Kovachki at NVIDIA.',
         does='Homogenised constitutive laws rarely have an analytic form and can show phenomena absent at the small '
              'scale, so learning them from data has been proposed. The paper studies the unexplored difficulty of '
              '**discontinuities and corner interfaces** in the material, which reduce the smoothness of the '
              'solutions: it gives approximation theory for learning the solution operator of the cell problem of '
              'elliptic homogenisation, and numerical experiments that validate the theory.',
         route='Homogenisation plus operator learning: the map from the microstructure to the effective coefficient '
               '(for groundwater: from a conductivity field to the conductivity of a block) is learned, with '
               'approximation guarantees.',
         gap='Linear, static, elliptic: the mean coefficient only. No fluctuation, no time-dependent small scale, and '
             'the guarantee is on the operator, not on a decision.',
         step='A learned cell problem is the fast map from facies or pore geometry to conductivity that a design loop '
              'needs. KAOS-GO adds the fluctuation of that map for a finite block (Fig. {{rev}}) and tests the '
              'learned closure with experiments predicted before they are run.',
         routes=['hom', 'learn']),
    dict(id='C4', inst='Caltech', year=2024, short='A learned pore-scale solver inside the Darcy model',
         title='A Learning-Based Multiscale Model for Reactive Flow in Porous Media',
         authors='Mina Karimi, Kaushik Bhattacharya',
         venue='Water Resources Research 60(9), e2023WR036303 (2024)', links=doi('10.1029/2023WR036303'),
         evidence='OpenAlex lists both authors at the California Institute of Technology.',
         does='Solute-laden flow reacts with the medium, changes its morphology and properties, and these change the '
              'flow. A **recurrent neural operator** is trained once, off-line, on repeated solutions of the '
              'lower-scale problem, and then replaces it in application-scale calculations: the accuracy of '
              'concurrent multiscale methods at a cost comparable to classical models. Examples follow the evolution '
              'of morphology, properties and flow conditions in geological formations.',
         route='Concurrent multiscale modelling with a learned small-scale solver that carries memory: the upscaled '
               'law is an operator with an internal state, not a formula.',
         gap='Laminar small-scale problems; no uncertainty of the surrogate at the decision; the training runs are not '
             'chosen for a goal.',
         step='The same architecture with two additions: a noise term for the part of the small scale that is '
              'chaotic, and an adjoint-weighted choice of the small-scale runs (Proposition 3), which in our example '
              'cuts the variance of the decision by <<alloc_gain>> for the same computing time.',
         routes=['learn', 'hom']),
    dict(id='C5', inst='Caltech', year=2021, short='Stochastic closures from time averages',
         title='Learning stochastic closures using ensemble Kalman inversion',
         authors='Tapio Schneider, Andrew M. Stuart, Jin-Long Wu',
         venue='Transactions of Mathematics and Its Applications 5(1), tnab003 (2021)', links=doi('10.1093/imatrm/tnab003'),
         evidence='OpenAlex lists the three authors at the California Institute of Technology.',
         does='Stochastic differential equations are fitted to **sufficient statistics computed from time averages** '
              'of the data, not to trajectories, which removes the inconsistency between such models and data at short '
              'time scales. The fit is an inverse problem solved by ensemble Kalman inversion; drift and diffusion '
              'are learned non-parametrically with hierarchical Gaussian-process parameterisations. Examples: a noisy '
              'Lorenz 63 model, dimension reduction of deterministic chaotic systems from the atmospheric sciences, '
              'large-scale climate patterns, and observables of molecular dynamics.',
         route='A deterministic chaotic small scale is replaced, at the large scale, by a stochastic model that is '
               'identified from statistics: "the large scale is the statistics of the small scale".',
         gap='No spatial averaging, no conservation laws of flow in a porous medium, no finite-sample guarantee.',
         step='KAOS-GO takes "learn from time averages" to porous flow: the data of the closure are time-averaged '
              'fluxes and dissipations. The noise amplitude is not a free fit: it is the Green–Kubo integral of the '
              'flux, checked by conformal scores.',
         routes=['learn', 'stat']),
]

OXFORD = [
    dict(id='O1', inst='Oxford', year=2022, short='Darcy from Stokes when the microstructure varies',
         title='A homogenised model for flow, transport and sorption in a heterogeneous porous medium',
         authors='Lucy C. Auton, Satyajit Pramanik, Mohit P. Dalwadi, Christopher W. MacMinn, Ian M. Griffiths',
         venue='Journal of Fluid Mechanics 932, A34 (2022; online December 2021)', links=doi('10.1017/jfm.2021.938'),
         evidence='OpenAlex lists all five authors at the University of Oxford (S. Pramanik also at IIT Gandhinagar, '
                  'M. P. Dalwadi also at University College London).',
         does='A two-dimensional microstructure of obstacles of smooth but arbitrary shape, whose size and spacing '
              'vary along the medium, is upscaled by the method of multiple scales with cells of varying area. The '
              'macroscale equations are characterised by the local porosity, a local **anisotropic permeability**, an '
              'effective anisotropic diffusivity and an effective adsorption rate, which depend on obstacle size and '
              'on spacing separately: the same porosity can give different permeability and diffusivity. Circular '
              'obstacles on a rectangular lattice are computed.',
         route='The classical route, asymptotic homogenisation: Darcy\'s law is the solvability condition of the '
               'Stokes problem on the cell, and the permeability is an average of the cell solution.',
         gap='Steady Stokes flow in a deterministic, nearly periodic geometry: no fluctuation, no unsteadiness. A '
             'follow-up of the group (SIAM J. Appl. Math. 2025) adds dispersion.',
         step='This is the mean law in its cleanest form. KAOS-GO starts where the cell problem stops having a steady '
              'solution: the cell problem is averaged in time, and its fluctuation becomes a term of the upscaled law.',
         routes=['hom']),
    dict(id='O2', inst='Oxford', year=2024, short='A theorem with the noise term in it',
         title='Stochastic homogenization with space-time ergodic divergence-free drift',
         authors='Benjamin Fehrman', venue='The Annals of Probability 52(1), 350–380 (2024)',
         links=doi('10.1214/23-AOP1663'),
         evidence='OpenAlex lists the author at the University of Oxford.',
         does='Diffusion equations with a space-time stationary and ergodic, divergence-free drift are proved to '
              'homogenise in law to a deterministic **stochastic partial differential equation with Stratonovich '
              'transport noise**. Without spatial ergodicity the drift is only partly absorbed into the '
              'skew-symmetric part of the flux, through a stream matrix; what is left is a time-dependent, spatially '
              'homogeneous transport which, for mildly decorrelating fields, converges to a Brownian noise with '
              'deterministic covariance.',
         route='Rigorous probability: a time-dependent, ergodic velocity field gives at large scale an effective '
               'diffusion **and a noise term** whose covariance is deterministic. It is the mathematical template of '
               '"mean law plus fluctuation".',
         gap='A transport equation, not the momentum balance that gives Darcy\'s law; the velocity field is given, '
             'stationary and ergodic; no data and no computation.',
         step='The fluctuating Darcy law of Section 5 is the momentum-side analogue: a mean resistance plus a Brownian '
              'term whose covariance is computed at the pore scale. The theorem also says what a solute sees in such '
              'a flow: transport noise, not only dispersion.',
         routes=['stat', 'hom']),
    dict(id='O3', inst='Oxford', year=2023, short='Rare deviations from a macroscopic law',
         title='Non-equilibrium large deviations and parabolic-hyperbolic PDE with irregular drift',
         authors='Benjamin Fehrman, Benjamin Gess', venue='Inventiones mathematicae 234(2), 573–636 (2023)',
         links=doi('10.1007/s00222-023-01207-3'),
         evidence='OpenAlex lists B. Fehrman at the University of Oxford and B. Gess at Bielefeld University and the '
                  'Max Planck Institute for Mathematics in the Sciences (Leipzig): the paper also counts for the Max '
                  'Planck Society.',
         does='Large deviations of conservative interacting particle systems, such as the zero range process, about '
              'their hydrodynamic limit lead to the skeleton equation, a degenerate parabolic-hyperbolic equation '
              'with irregular drift. The paper builds a well-posedness theory for it in energy-critical spaces and '
              'applies it to rate functions, to zero-noise large deviations of conservative stochastic PDE and to '
              'the Γ-convergence of rate functions. It solves a long-standing open problem for zero range processes '
              'and makes rigorous an informal link between **macroscopic fluctuation theory and fluctuating '
              'hydrodynamics**.',
         route='Statistical mechanics: the macroscopic equation is the law of large numbers of a microscopic random '
               'dynamics; rare deviations from it have a rate function, and a stochastic PDE with conservative noise '
               'reproduces them.',
         gap='The small scale is a stochastic particle system, not deterministic chaos in a pore space; the '
             'macroscopic equation is a nonlinear diffusion; nothing on finite samples.',
         step='Three levels organise KAOS-GO: the mean law (law of large numbers), the Gaussian fluctuation (central '
              'limit) and rare events (large deviations). Alarms are tail events, so the certificate may not rest on '
              'Gaussian tails: it takes its multiplier from observed scores.',
         routes=['stat']),
    dict(id='O4', inst='Oxford', year=2024, short='A nonlinear Darcy law from a network',
         title='Homogenization of Nonlinear Blood Flow in Periodic Networks: The Limit of Small Haematocrit '
               'Heterogeneity',
         authors='Y. Ben-Ami, B. D. Wood, J. M. Pitt-Francis, P. K. Maini, H. M. Byrne',
         venue='Multiscale Modeling & Simulation 22(4), 1498–1533 (2024)', links=doi('10.1137/24M1632425'),
         evidence='OpenAlex lists Y. Ben-Ami, J. Pitt-Francis, P. K. Maini and H. M. Byrne at the University of Oxford '
                  'and B. D. Wood at Oregon State University.',
         does='Blood flow in the microcirculation is upscaled from resolved vessels to the tissue. The flow and the '
              'concentration of red cells (haematocrit) are coupled nonlinearly; the analysis is carried out in the '
              'limit of small haematocrit differences between neighbouring vessels. The result is a system of coupled '
              'nonlinear equations in which a **nonlinear Darcy-type law** relates flow and pressure gradient through '
              'a haematocrit-dependent permeability tensor, and haematocrit is purely advected at the macroscale. '
              'Permeability tensors are computed for periodic networks in two and three dimensions, with the effect '
              'of the distribution of vessel lengths and diameters.',
         route='Homogenisation of a network with a nonlinear constitutive law: the Darcy form survives, with a '
               'permeability that depends on an internal state.',
         gap='Periodic networks, small heterogeneity, steady states; no fluctuation.',
         step='It is the structure of the Princeton result seen from the mean side: a Darcy law whose coefficient '
              'depends on a state (haematocrit there, the fraction of unsteady pores here). KAOS-GO adds the '
              'statistics of that state: in our cell the grains with an unsteady wake go from <<grains_lo>> of '
              '<<grains_n>> at Re = <<re_uns_lo>> to all of them at Re = <<grains_full_re>>.',
         routes=['hom']),
    dict(id='O5', inst='Oxford', year=2026, short='Elastic and shear-thinning effects, resolved',
         title='How Viscoelastic Effects Impact Polymer Fluid Flow in Porous Media',
         authors='Yongxin Wang, Si Suo, Callum Cuttle, Christopher W. MacMinn, Martin J. Blunt, Catherine O’Sullivan',
         venue='Transport in Porous Media 153, 65 (2026)', links=doi('10.1007/s11242-026-02312-6'),
         evidence='OpenAlex lists C. Cuttle and C. W. MacMinn at the University of Oxford and Y. Wang, S. Suo, M. J. '
                  'Blunt and C. O’Sullivan at Imperial College London.',
         does='Direct pore-scale simulations compare a viscoelastic model (FENE-P) with a model that only thins under '
              'shear (Carreau). Elasticity induces **recirculation upstream of constrictions** and lowers the '
              'conductance; the extent of the recirculation is proportional to the excess pressure gradient over the '
              'equivalent Carreau fluid. A two-dimensional channel, a quasi-three-dimensional one, an axisymmetric '
              'constricted tube and an ordered packing of spheres are compared. Strong shear thinning suppresses the '
              'effects of elasticity.',
         route='Resolved simulation: the extra macroscopic pressure gradient is linked to a pore-scale structure and '
               'to the energy lost in it.',
         gap='Simple and ordered geometries; the abstract reports no unsteady or chaotic regime; no upscaled law with '
             'an error bar.',
         step='"Excess pressure gradient proportional to the recirculation" is a closure for the mean-flow part of '
              'the dissipation. KAOS-GO places it next to the fluctuation part and gives each its uncertainty.',
         routes=['see', 'diss']),
]

MIT = [
    dict(id='M1', inst='MIT', year=2022, short='The map of the field',
         title='Perspectives on viscoelastic flow instabilities and elastic turbulence',
         authors='Sujit S. Datta, Arezoo M. Ardekani, Paulo E. Arratia, Antony N. Beris, Irmgard Bischofberger, Gareth '
                 'H. McKinley, Jens G. Eggers, J. Esteban López-Aguilar, Suzanne M. Fielding, Anna Frishman, Michael D. '
                 'Graham, Jeffrey S. Guasto, Simon J. Haward, Amy Q. Shen, Sarah Hormozi, Alexander Morozov, Robert J. '
                 'Poole, V. Shankar, Eric S. G. Shaqfeh, Holger Stark, Victor Steinberg, Ganesh Subramanian, Howard A. '
                 'Stone',
         venue='Physical Review Fluids 7, 080701 (2022)', links=doi('10.1103/PhysRevFluids.7.080701'),
         evidence='OpenAlex lists I. Bischofberger and G. H. McKinley at the Massachusetts Institute of Technology, '
                  'among 23 authors of 20 institutions (S. S. Datta and H. A. Stone at Princeton University).',
         does='A perspective that integrates the input of the speakers of an international workshop: historical '
              'remarks, the characterisation of fluids and flows, experimental and simulation tools, and the modern '
              'questions and puzzles of viscoelastic flow instabilities and elastic turbulence.',
         route='The community view of what is established and what is open. Its authors include the groups whose '
               'porous-media experiments this review cites (Datta, Guasto, Haward and Shen).',
         gap='A perspective: no upscaled law and no statement of its error.',
         step='We use it as the list of open questions and place ours in it: the macroscopic law of an unstable '
              'pore-scale flow, with the size of what it leaves out.',
         routes=['see']),
    dict(id='M2', inst='MIT', year=2021, short='Regimes of displacement from the pore scale',
         title='Wettability and Lenormand\'s diagram',
         authors='Bauyrzhan K. Primkulov, Amir A. Pahlavan, Xiaojing Fu, Benzhong Zhao, Christopher W. MacMinn, Ruben '
                 'Juanes',
         venue='Journal of Fluid Mechanics 923, A34 (2021)', links=doi('10.1017/jfm.2021.579'),
         evidence='OpenAlex lists B. K. Primkulov and R. Juanes at the Massachusetts Institute of Technology, C. W. '
                  'MacMinn at the University of Oxford, A. A. Pahlavan at Yale University and B. Zhao at McMaster '
                  'University.',
         does='Lenormand\'s phase diagram of fluid–fluid displacement (capillary number, viscosity ratio) is extended '
              'with wettability, using dynamic and quasi-static pore-network models. With the fractal dimension and '
              'the ratio of characteristic viscous and capillary pressures, **five regimes** are delineated: stable '
              'displacement, viscous fingering, invasion percolation, cooperative pore filling and corner flow.',
         route='A regime diagram: pore-scale mechanisms and disorder give macroscopic invasion patterns that are '
               'classified by a few dimensionless numbers.',
         gap='Regimes, not laws with error bars; two-phase displacement, where the burst-like pore events are '
             'capillary, not chaotic.',
         step='An upscaled law needs its domain of validity drawn in the same way. KAOS-GO draws it for Darcy\'s law: '
              'in Reynolds number, cell size and averaging time (Fig. {{macro}}, Fig. {{clt}}).',
         routes=['see', 'stat']),
    dict(id='M3', inst='MIT', year=2024, short='Chaotic fingers, reproducible flux',
         title='Direct comparison of density-driven convective mixing in a three-dimensional porous medium using '
               'experiments and simulation',
         authors='Rebecca Liyanage, Xiaojing Fu, Ronny Pini, Ruben Juanes',
         venue='Physical Review Fluids 9, 043802 (2024)', links=doi('10.1103/PhysRevFluids.9.043802'),
         evidence='OpenAlex lists R. Juanes at the Massachusetts Institute of Technology, X. Fu at the California '
                  'Institute of Technology, R. Pini at Imperial College London and R. Liyanage at the Université de '
                  'Pau et des Pays de l\'Adour.',
         does='Density-driven convective mixing in a three-dimensional porous medium is compared between experiment '
              'and simulation. They agree in the patterns and the speed of mixing; columnar plumes self-organise into '
              'a reticular pattern seen before only in simulations; concentration, variance, scalar dissipation rate '
              'and dissolution flux match in time. A **new relation between dissipation rate and flux** is '
              'established, and the flux is 30% higher in three dimensions than in two.',
         route='Chaos one scale up: the fingers of an unstable Darcy flow are irregular, yet integral quantities are '
               'reproducible and tied by a dissipation–flux relation.',
         gap='One system; no error bar on the flux law; the individual fingers are not predicted.',
         step='It is Proposition 1 at the next scale: a macroscopic flux fixed by a dissipation rate. For coastal '
              'aquifers it suggests a certified flux law for salinisation from above (overwash, storm surge) in '
              'variable-density models.',
         routes=['see', 'diss']),
    dict(id='M4', inst='MIT', year=2023, short='Hydrodynamic equations learned from particles',
         title='Learning hydrodynamic equations for active matter from particle simulations and experiments',
         authors='Rohit Supekar, Boya Song, Alasdair Hastewell, Gary P. T. Choi, Alexander Mietke, Jörn Dunkel',
         venue='Proceedings of the National Academy of Sciences 120(7), e2206994120 (2023)',
         links=doi('10.1073/pnas.2206994120'),
         evidence='OpenAlex lists the six authors at the Massachusetts Institute of Technology.',
         does='A framework that uses spectral basis representations and **sparse regression** to discover partial '
              'differential equations from microscopic simulation and experimental data, with the relevant physical '
              'symmetries built in. Applied to a chiral active particle model, to microroller experiments and to '
              'schooling fish, it learns hydrodynamic equations that reproduce the observed collective dynamics, and '
              'measures many hydrodynamic parameters in parallel from video data.',
         route='Data-driven coarse-graining: trajectories → coarse fields → sparse regression → macroscopic equation.',
         gap='No guarantee on the learned coefficients or on predictions, and no design of the next experiment; not '
             'flow in a porous medium.',
         step='SC-PDE-FIND adds stability selection, conformal intervals and c- and T-optimal design to this '
              'pipeline. In KAOS-GO the library of candidate laws is tested on held-out forcing levels: a '
              'Forchheimer law fitted to the steady levels misses the unsteady ones by up to <<forch_err>>, which is '
              'how the certificate learns its width.',
         routes=['learn']),
    dict(id='M5', inst='MIT', year=2024, short='Sixteen runs of the same experiment',
         title='Physical Variability in Meter-Scale Laboratory CO2 Injections in Faulted Geometries',
         authors='Malin Haugen, Lluís Saló-Salgado, Kristoffer Eikehaug, Benyamine Benali, Jakub W. Both, Erlend '
                 'Storvik, Olav Folkvord, Ruben Juanes, Jan Martin Nordbotten, Martin A. Fernø',
         venue='Transport in Porous Media 151, 1169–1197 (2024)', links=doi('10.1007/s11242-023-02047-8'),
         evidence='OpenAlex lists L. Saló-Salgado and R. Juanes at the Massachusetts Institute of Technology; the '
                  'other authors at the University of Bergen and NORCE.',
         does='In the FluidFlower rig, meter-scale multiphase flow is studied in two geological geometries with '
              'normal faults. The experimental protocols behind the input parameters of simulations are given, and '
              'the **variability of CO2 migration patterns is quantified between 16 repeated laboratory runs**, and '
              'between history-matched models and an injection experiment. The predictive capability of a '
              'history-matched model is then evaluated in a different geological setting.',
         route='Empirical: repeat the same experiment; what differs between runs is irreducible, what does not is '
               'what a Darcy-scale model can be asked to predict.',
         gap='The variability is described, not turned into a predictive error bar; no link to the pore scale.',
         step='Repeated runs are the calibration set of a conformal certificate: each run is predicted from the '
              'others. KAOS-GO does this with time windows of the pore-scale flow and, in the field, with repeated '
              'pump stops.',
         routes=['see', 'stat']),
]

HARVARD = [
    dict(id='H1', inst='Harvard', year=2020, short='Local flow changes move the oil',
         title='Origin of anomalous polymer-induced fluid displacement in porous media',
         authors='Shima Parsa, Enric Santanach-Carreras, Lizhi Xiao, David A. Weitz',
         venue='Physical Review Fluids 5, 022001(R) (2020)', links=doi('10.1103/PhysRevFluids.5.022001'),
         evidence='OpenAlex lists all four authors at Harvard University (with further affiliations).',
         does='Confocal microscopy shows the displacement of oil in a three-dimensional micromodel while the local '
              'velocities of the displacing fluid are measured. The extra displacement obtained with polymer comes '
              'from a counter-intuitive effect, **polymer retention** and the local changes in flow that it causes: '
              'large, heterogeneous changes of the local flow give viscous forces at the fluid–fluid interface that '
              'are large enough to displace more oil.',
         route='What counts for the macroscopic outcome is the redistribution of the pore-scale velocities, not their '
               'mean.',
         gap='A mechanism, not a law; no unsteadiness.',
         step='A warning for every upscaling: the mean flux can stay while the distribution under it changes. '
              'KAOS-GO therefore carries the distribution (the fluctuation term) and tests thresholds on it.',
         routes=['see']),
    dict(id='H2', inst='Harvard', year=2021, short='The bulk permeability scales the pore velocities',
         title='Unexpected scaling of interstitial velocities with permeability due to polymer retention in porous '
               'media',
         authors='Shima Parsa, Ahmad Zareei, Enric Santanach-Carreras, Eliza J. Morris, Ariel Amir, Lizhi Xiao, David '
                 'A. Weitz',
         venue='Physical Review Fluids 6, L082302 (2021)', links=doi('10.1103/PhysRevFluids.6.L082302'),
         evidence='OpenAlex lists S. Parsa, A. Zareei, E. J. Morris, A. Amir, L. Xiao and D. A. Weitz at Harvard '
                  'University (some with further affiliations) and E. Santanach-Carreras at Total and CNRS.',
         does='The flow and retention of polymer reduce the permeability of the medium. Experiment and simulation '
              'show that the changes follow directly from pore blockage and the diversion of flow. Despite the '
              'complex changes, a **simple scaling of the distribution of pore-level velocities with the bulk '
              'permeability** is found.',
         route='Statistics: the distribution of pore-scale velocities collapses when scaled with the Darcy-scale '
               'coefficient. The large scale controls the statistics of the small scale.',
         gap='Steady flow; a scaling, not a derivation; no fluctuation in time.',
         step='Read backwards it is our inverse problem: Darcy-scale data carry information on the pore-scale '
              'distribution. With Bayesian design we would choose the flow rates of a column test that reveal it.',
         routes=['see', 'stat']),
    dict(id='H3', inst='Harvard', year=2022, short='When a network homogenises and when it channels',
         title='Temporal Evolution of Erosion in Pore Networks: From Homogenization to Instability',
         authors='Ahmad Zareei, Deng Pan, Ariel Amir', venue='Physical Review Letters 128, 234501 (2022)',
         links=doi('10.1103/PhysRevLett.128.234501'),
         evidence='OpenAlex lists the three authors at Harvard University.',
         does='Two- and three-dimensional pore-network models evolve under erosion laws that depend on the flow rate, '
              'the local velocity or the wall shear stress (single phase, no deposition, no reactions, fixed '
              'topology). Depending on the law, the flow becomes uniform and **homogenised**, or unstable with '
              '**channels**. An order parameter shows a phase transition, and a simple model gives quantitative '
              'criteria that predict the fate of the network.',
         route='Statistical physics of networks: a medium becomes more or less "Darcy-like" by its own dynamics, with '
               'a phase transition between the two fates.',
         gap='Slow evolution of the solid, not fast chaos of the fluid; no error bar for Darcy\'s law on the way.',
         step='Their order parameter is a ready diagnostic of whether a representative volume exists. KAOS-GO uses '
              'the analogous quantity, the spatial concentration of the dissipation, to decide whether a certificate '
              'may assume short-range correlation.',
         routes=['stat']),
    dict(id='H4', inst='Harvard', year=2024, short='Gradients through a pore-scale simulation',
         title='Engineering of polydisperse porous media for enhanced fluid flows through systematic topology tuning '
               'via differentiable direct numerical simulation',
         authors='Mohammed G. Alhashim, Michael P. Brenner', venue='Physical Review Fluids 9, 054103 (2024)',
         links=doi('10.1103/PhysRevFluids.9.054103'),
         evidence='OpenAlex lists both authors at Harvard University (M. G. Alhashim also at Saudi Aramco).',
         does='Automatic differentiation through a direct numerical simulation is used to optimise the packing of a '
              'polydisperse system of periodically arranged circular rods so that the **pressure drop** across the '
              'medium is minimal; the optimal topology changes with the packing fraction.',
         route='Differentiable simulation: the derivative of a Darcy-scale quantity with respect to the pore '
               'geometry, obtained through the resolved flow.',
         gap='Optimisation in a laminar regime, not uncertainty. In a chaotic regime the derivative of a trajectory '
             'grows without bound, a known obstacle to adjoints (S39) that the abstract does not '
             'address.',
         step='A division of labour for our adjoints: at the pore scale where the flow is steady, at the Darcy scale '
              'where it is chaotic. KAOS-GO differentiates the Darcy model with respect to its closure and never '
              'differentiates through the chaos.',
         routes=['learn']),
    dict(id='H5', inst='Harvard', year=2022, short='Alternating between the scales',
         title='Multiscale simulations of complex systems by learning their effective dynamics',
         authors='Pantelis R. Vlachas, Georgios Arampatzis, Caroline Uhler, Petros Koumoutsakos',
         venue='Nature Machine Intelligence 4, 359–366 (2022)', links=doi('10.1038/s42256-022-00464-w'),
         evidence='OpenAlex lists P. R. Vlachas, G. Arampatzis and P. Koumoutsakos at Harvard University and ETH Zurich '
                  'and C. Uhler at the Massachusetts Institute of Technology. Paper H4 of the equation-learning file '
                  'of the author.',
         does='As summarised by the publisher\'s abstract: the framework "learning the effective dynamics" joins '
              'machine learning with equation-free computation. **Autoencoders** map between the fine and the coarse '
              'description and **recurrent networks** advance the coarse one; the method reduces the computational '
              'effort by up to two orders of magnitude while keeping the accuracy of the full dynamics. The preprint '
              'shows the FitzHugh–Nagumo model, the Kuramoto–Sivashinsky equation and flow past a cylinder.',
         route='Equation-free: the large-scale "law" is a learned latent dynamics, refreshed by short bursts of the '
               'small-scale solver.',
         gap='The latent variables are not fluxes and heads; no conservation, no guarantee.',
         step='The alternation between scales is what KAOS-GO schedules by design: the pore scale is run only at the '
              'flux levels, and for as long, as the certificate of the closure requires for the decision.',
         routes=['learn']),
]

MAXPLANCK = [
    dict(id='P1', inst='Max Planck', year=2020, short='All fluctuations from one local object',
         title='The Structure of Fluctuations in Stochastic Homogenization',
         authors='Mitia Duerinckx, Antoine Gloria, Felix Otto',
         venue='Communications in Mathematical Physics 377, 259–306 (2020)', links=doi('10.1007/s00220-020-03722-3'),
         evidence='OpenAlex lists F. Otto at the Max Planck Institute for Mathematics in the Sciences (Leipzig) and M. '
                  'Duerinckx and A. Gloria at CNRS, Université Libre de Bruxelles and Paris.',
         does='As summarised by the abstract of the arXiv version: in the homogenisation of elliptic equations with '
              'random coefficients four quantities matter, the field and the flux of the solution and of the '
              'corrector. The paper identifies a fifth, a random tensor field called the **homogenisation '
              'commutator**, and shows that it drives, at leading order, the fluctuations of the other four; the '
              'authors describe it as the first complete theory of fluctuations in stochastic homogenisation. A '
              'companion paper (Probab. Theory Relat. Fields, 2020) proves asymptotic normality and identifies the '
              'limiting covariance.',
         route='A rigorous central limit theorem for upscaled flow in a random medium: every macroscopic fluctuation '
               'comes from one local object, transported by the homogenised solution.',
         gap='Disorder, not chaos: static random coefficients, a linear elliptic equation, a model setting; no time.',
         step='This is the spatial half of the fluctuating Darcy law, and it gives certificates their geometry: the '
              'error of any decision is an adjoint-weighted integral of a local noise. In our cells the conductivity '
              'of a finite block scatters by <<rev_cv16>> for 16 grains and <<rev_cv64>> for 64. KAOS-GO adds the '
              'temporal half and the calibration by experiments.',
         routes=['stat', 'hom']),
    dict(id='P2', inst='Max Planck', year=2024, short='How wrong is a representative volume',
         title='Bias in the Representative Volume Element method: Periodize the Ensemble Instead of Its Realizations',
         authors='Nicolas Clozeau, Marc Josien, Felix Otto, Qiang Xu',
         venue='Foundations of Computational Mathematics 24, 1305–1387 (2024; online 2023)',
         links=doi('10.1007/s10208-023-09613-y'),
         evidence='OpenAlex lists F. Otto at the Max Planck Institute for Mathematics in the Sciences (Leipzig), N. '
                  'Clozeau at the Institute of Science and Technology Austria, M. Josien at CEA Cadarache and Q. Xu at '
                  'Lanzhou University.',
         does='The representative-volume method infers the effective coefficient of a stationary random medium from a '
              'finite box with periodic boundary conditions. The message is in the title: sample from a periodised '
              'ensemble, do not periodically extend a piece of one realisation. The **systematic error** is '
              'generically of order $L^{-1}$ in the box size for the second strategy (heuristic argument) and of '
              'order $L^{-d}$ for a suitable periodisation of the ensemble (rigorous, for ensembles of Gaussian '
              'type); the leading term is characterised in both cases.',
         route='Quantitative homogenisation: the error of "the" representative volume has a random part, which decays '
               'like $L^{-d/2}$, and a systematic part that depends on how the box is closed.',
         gap='Linear, static, Gaussian-type ensembles.',
         step='Our cells are periodic boxes of randomly placed grains, generated directly on the torus, as the paper '
              'recommends. We measure both errors for the Darcy coefficient (Fig. {{rev}}): the scatter decays with '
              'exponent <<rev_slope>> in the number of grains (central limit: −0.5).',
         routes=['hom', 'stat']),
    dict(id='P3', inst='Max Planck', year=2020, short='Where the pore scale shows through',
         title='From Rayleigh–Bénard convection to porous-media convection: how porosity affects heat transfer and '
               'flow structure',
         authors='Shuang Liu, Linfeng Jiang, Kai Leong Chong, Xiaojue Zhu, Zhen-Hua Wan, Roberto Verzicco, Richard J. '
                 'A. M. Stevens, Detlef Lohse, Chao Sun',
         venue='Journal of Fluid Mechanics 895, A18 (2020)', links=doi('10.1017/jfm.2020.309'),
         evidence='OpenAlex lists D. Lohse at the Max Planck Institute for Dynamics and Self-Organization (Göttingen) '
                  'and the Max Planck – University of Twente Center for Complex Fluid Dynamics; S. Liu, L. Jiang and C. '
                  'Sun at Tsinghua University.',
         does='Pore-resolved simulations of Rayleigh–Bénard convection in porous media made of circular obstacles on '
              'a square lattice, with the porosity as the parameter. A **scaling crossover** occurs when the thermal '
              'boundary layer and the pore scale are comparable. The effects of the porous structure on temperature '
              'and velocity fluctuations, on the convective heat flux and on the energy dissipation rates are '
              'analysed; the structure can enhance or reduce the heat transfer.',
         route='Resolved simulation across the transition: a Darcy-type description holds while the smallest active '
               'structure of the flow is larger than a pore, and fails when it becomes thinner.',
         gap='Thermal convection in regular arrays; the limit of validity is described, not certified.',
         step='A physical criterion for a Darcy-scale closure: compare the smallest dynamically active length with '
              'the pore. KAOS-GO makes it a tested statement: the certificate widens as the criterion is approached.',
         routes=['see', 'diss']),
    dict(id='P4', inst='Max Planck', year=2024, short='A transport law from exact dissipation relations',
         title='Transport scaling in porous media convection',
         authors='Xiaojue Zhu, Yifeng Fu, Marco De Paoli', venue='Journal of Fluid Mechanics 991, A4 (2024)',
         links=doi('10.1017/jfm.2024.528'),
         evidence='OpenAlex lists X. Zhu and Y. Fu at the Max Planck Institute for Solar System Research (Göttingen) '
                  'and M. De Paoli at TU Wien and the University of Twente.',
         does='A theory for the Nusselt number (heat or mass flux) as a function of the Rayleigh–Darcy number in '
              'convective porous-media flows. **Exact relations** are derived for the kinetic energy and the thermal '
              'dissipation rate; the thermal dissipation is split into boundary layer and bulk, in the spirit of '
              'Grossmann and Lohse; a scaling relation follows that explains the empirical ones, including why two '
              'and three dimensions differ. The agreement with simulations is excellent.',
         route='Dissipation budgets: an exact identity, then a split of the dissipation into regions, give the '
               'macroscopic transport law of a chaotic flow.',
         gap='The chaos is at the Darcy scale (the pores are already averaged); no statement on fluctuations.',
         step='Proposition 1 is the momentum analogue at the pore scale: an exact identity and a split, into mean '
              'flow and fluctuations instead of boundary layer and bulk. Their result names our next step: a scaling '
              'law for each part.',
         routes=['diss']),
    dict(id='P5', inst='Max Planck', year=2021, short='Fluctuations cross a threshold the mean cannot',
         title='Effect of elastic instability on mobilization of capillary entrapments',
         authors='Pegah Shakeri, Michael Jung, Ralf Seemann', venue='Physics of Fluids 33, 113102 (2021)',
         links=doi('10.1063/5.0071556'),
         evidence='OpenAlex lists the three authors at the Max Planck Institute for Dynamics and Self-Organization '
                  '(Göttingen) and Saarland University.',
         does='A microfluidic design isolates elastic forces: one capillary entrapment connected to two symmetric '
              'serpentine channels. After the onset of the purely elastic instability the base flow in the channels '
              'is unstable; the **pressure fluctuations** create an instantaneous imbalance between the two ends of '
              'the entrapment, which provides the pressure to overcome the capillary threshold and displace the '
              'trapped oil. The displacement coincides with a fully developed elastic turbulent state.',
         route='A threshold is crossed by the fluctuating pressure, not by its average: fluctuations do what the mean '
               'cannot.',
         gap='One entrapment; no statistics of the crossing, no Darcy-scale law of mobilisation.',
         step='Thresholds are what makes the fluctuation term of a Darcy law matter for decisions. Ours are alarms '
              '(chloride, the head at a well). KAOS-GO predicts the probability of crossing, not only the mean.',
         routes=['see', 'stat']),
]

CARDS = CALTECH + OXFORD + MIT + HARVARD + MAXPLANCK
for c_ in CARDS:
    c_['status'] = STATUS
INST_ORDER = ('Caltech', 'Oxford', 'MIT', 'Harvard', 'Max Planck')
ROUTES = (('see', 'Seeing it: experiments and resolved simulations'), ('hom', 'Homogenisation'),
          ('stat', 'Statistical physics and probability'), ('diss', 'Dissipation budgets'),
          ('learn', 'Learned closures'))
