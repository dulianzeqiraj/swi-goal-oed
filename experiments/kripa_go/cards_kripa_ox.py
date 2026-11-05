"""The five Oxford cards of the eighth review (see cards_kripa.py) and their entries in the state-of-the-art table."""

OXFORD = [
    dict(id='O1', inst='Oxford', year=2024, short='Coastal salinity depends on its history',
         title='Offshore freshened groundwater reservoirs controlled by submarine faults with a complex dependency on '
               'antecedent hydrogeological conditions',
         authors='A. Paldor, C. Bertoni, B. Penny, H. A. Michael',
         venue='Science of The Total Environment 952, 175834 (2024)',
         links=[('doi:10.1016/j.scitotenv.2024.175834', 'https://doi.org/10.1016/j.scitotenv.2024.175834'),
                ('Oxford ORA', 'https://ora.ox.ac.uk/objects/uuid:4bc81962-a2b6-479e-a8d6-920c0f54715c')],
         evidence='Listed on the Oxford Earth Sciences site and deposited in ORA; Bertoni has an Oxford Earth Sciences '
                  'profile. The affiliation printed on this paper was not seen (other sources also list her in Trieste).',
         does='**Result (abstract wording).** In a variable-density model of a faulted submarine confined aquifer in the '
              'Levant Basin, built from geological data, faults close to the coastline within the brackish zone control '
              'offshore salinities regardless of the initial conditions, while the influence of distal faults depends on '
              'antecedent conditions: they control the offshore freshened groundwater if the antecedent fresh–saltwater '
              'interface lies seaward of the fault, so that one geological system can be active or passive depending on '
              'its hydrological history. Manuscript snippets indicate that faster discharge raises the hydrodynamic '
              'dispersion; the dispersivity values were not seen.',
         sota='Path dependence of coastal and offshore salinity controlled by structural features, shown with '
              'variable-density models.',
         gap='No uncertainty quantification; one site; dispersivities and their sensitivity not seen.',
         inputs='The effect of a structural parameter on salinity cannot be identified without the initial interface: '
                'the same conductivity field can hold two salinity states.',
         dispersion='The transition zone widens where the flow is fast ($D=\\alpha|v|$): a drier regime with slower '
                    'discharge changes the width as well as the position of the interface (our inference).',
         bcs='The initial interface and the sea-level history are not ignorable: a drought counterfactual has to carry '
             'the antecedent interface as an unknown.',
         step='KRIPA-GO\'s counterfactual is a steady regime: it assumes the interface has come to equilibrium with the '
              'drier recharge, and its answer — a salinized area of <<A_fact>> → <<A_cf>> km² — is the limit of a '
              'lasting regime. Their path dependence names the first condition for that limit (no structure near the '
              'antecedent interface that could lock another state in); their flow-dependent dispersion names the second, '
              'the cross-world law of the width (Proposition L3). With purely mechanical dispersion the steady width '
              'scales with the dispersivity rather than the velocity, which supports the shared width $w\'=w$ (our '
              'inference).',
         novel='The antecedent interface and the flow dependence of dispersion as the two conditions under which the '
               'steady salinity counterfactual (<<A_fact>> → <<A_cf>> km²) holds.',
         steps=['prior', 'check'], informs=dict(inputs=1, dispersion=2, bcs=2)),
    dict(id='O2', inst='Oxford', year=2023, short='Geometry, not mixing, shapes the near field',
         title='The near-field shape and stability of a porous plume',
         authors='Graham P. Benham',
         venue='Journal of Fluid Mechanics 955, A13 (2023)',
         links=[('doi:10.1017/jfm.2022.1068', 'https://doi.org/10.1017/jfm.2022.1068'),
                ('arXiv:2204.13510', 'https://arxiv.org/abs/2204.13510')],
         evidence='The arXiv and journal versions list the Mathematical Institute, University of Oxford (search '
                  'summaries); the author was a Departmental Lecturer at Oxford in 2022–2023.',
         does='**Result (closely paraphrased).** Near the injection point a buoyant plume in a porous medium adjusts its '
              'cross-section to conserve mass, and these adjustments — rather than mixing with the ambient fluid, which '
              'acts over larger distances — control its near-field shape. At moderate injection rates the plume reaches '
              'a steady state and matches the buoyancy velocity within a few plume widths; the steady shape depends on '
              'one parameter, the inlet velocity over the buoyancy velocity, and a linear stability analysis shows the '
              'interface becomes unstable when that ratio is much smaller than one.',
         sota='A one-parameter theory of the near-field shape and stability of porous plumes.',
         gap='Homogeneous medium, no field data, no coastal geometry; mixing is left to the far field.',
         inputs='Only the ratio of the inlet to the buoyancy velocity (permeability times density contrast) is '
                'identifiable from the near-field shape.',
         dispersion='Near-field interface geometry carries almost no information on the dispersion; the dispersivity is '
                    'learned far from the source, which bears on where chloride samples should be placed (our '
                    'inference).',
         bcs='The inflow relative to the buoyancy velocity sets the stability: a drought that lowers the inflow could '
             'cross the threshold (our inference).',
         step='The same split between geometry and mixing runs through Proposition L2: the toe of the wedge is a '
              'sharp-interface (geometric) quantity and its counterfactual, <<dT>>, is free of the dispersion, while the '
              'shallow salinized area, set by the mixing zone, depends on the width $w$ for <<share_wA>> of its posterior '
              'variance (T28).',
         novel='Geometry versus mixing: the toe counterfactual (<<dT>>) is free of the dispersion, the salinized-area '
               'counterfactual is mostly dispersion (<<share_wA>>).',
         steps=['emulate'], informs=dict(inputs=1, dispersion=2, bcs=1)),
    dict(id='O3', inst='Oxford', year=2023, short='Global drought indices at 5 km',
         title='Global high-resolution drought indices for 1981–2022',
         authors='Solomon H. Gebrechorkos et al. (full author list not seen)',
         venue='Earth System Science Data 15(12), 5449–5466 (2023)',
         links=[('doi:10.5194/essd-15-5449-2023', 'https://doi.org/10.5194/essd-15-5449-2023'),
                ('Oxford ORA', 'https://ora.ox.ac.uk/objects/uuid:09b2a3ca-6f12-4014-8a74-e67a1dd1922b')],
         evidence='The ORA record lists the School of Geography and the Environment, University of Oxford.',
         does='**Result.** Four 5 km datasets of the Standardized Precipitation-Evapotranspiration Index for 1981–2022 '
              '(CHIRPS or MSWEP rain combined with GLEAM or hPET evaporation), at accumulation scales of 1 to 48 months, '
              'because existing global indices are coarser than 50 km; the data are archived at CEDA. It is likely the '
              'dataset behind a 2025 paper of the same group used in review V.',
         sota='The highest-resolution global multi-scale drought-index record.',
         gap='No groundwater; uncertainty only as the spread of four members; 5 km may be coarse for the coastal plain.',
         inputs='The accumulation scale that best tracks the heads estimates the vadose delay and the aquifer memory '
                '(our inference).',
         dispersion='None.',
         bcs='A drought counterfactual can be defined as an index percentile at a given accumulation scale, with the '
             'spread of the four members as forcing uncertainty.',
         step='The recharge factor $c$ of KRIPA-GO is a regime, not a year; their index at 12–48 months is the rain-side '
              'definition of such a regime from the rain alone. Mapping an index class at Fushë-Kuqe to $c$ turns the '
              'dose-response of T26 (half the recharge adds <<dose05>> km² of salinized area) into a salinity answer per '
              'drought class.',
         novel='Drought-index classes mapped to the recharge factor, which turns the dose-response into salinity per '
               'drought class.',
         steps=['prior'], informs=dict(inputs=1, dispersion=0, bcs=2)),
    dict(id='O4', inst='Oxford', year=2022, short='Extremes beyond the record from pooled forecasts',
         title='Extreme floods in Europe: going beyond observations using reforecast ensemble pooling',
         authors='Manuela I. Brunner, Louise J. Slater',
         venue='Hydrology and Earth System Sciences 26(2), 469–482 (2022)',
         links=[('doi:10.5194/hess-26-469-2022', 'https://doi.org/10.5194/hess-26-469-2022'),
                ('HESS', 'https://hess.copernicus.org/articles/26/469/2022/')],
         evidence='Slater at the University of Oxford (search result); Brunner at the University of Freiburg.',
         does='**Result (as summarized).** Pooling the reforecasts of the European Flood Awareness System across lead '
              'times and members gives 130 series instead of one, enough to analyse events rarer than about twice a '
              'century; over 234 Central European catchments the uncertainty bounds are on average about 80% narrower '
              'than from observations alone, while pooling can carry biases from the simulated meteorology.',
         sota='Regional frequency of extremes from pooled, physically consistent forecast ensembles.',
         gap='Wet extremes only; no groundwater; no coverage guarantee; tied to the model meteorology.',
         inputs='None.',
         dispersion='None.',
         bcs='Counterfactual forcing beyond the observed rain record can be drawn from pooled ensembles, with bias checks.',
         step='Pooled ensembles are a source of the recharge regimes the record does not contain, dry and wet. KRIPA-GO '
              'says what each regime would do to the salt — from +<<dose05>> km² of salinized area at half the recharge '
              'to −<<dose15>> km² at 1.5 times (T26) — and their bias check is the mechanism check of Proposition L4.',
         novel='Pooled forecast ensembles as the source of regimes beyond the record, for which KRIPA-GO gives the salt '
               'response.',
         steps=['prior', 'check'], informs=dict(inputs=0, dispersion=0, bcs=2)),
    dict(id='O5', inst='Oxford', year=2023, short='Large deviations of conservative transport',
         title='Non-equilibrium large deviations and parabolic-hyperbolic PDE with irregular drift',
         authors='Benjamin Fehrman, Benjamin Gess',
         venue='Inventiones Mathematicae (2023), 573–636 (volume not seen)',
         links=[('doi:10.1007/s00222-023-01207-3', 'https://doi.org/10.1007/s00222-023-01207-3'),
                ('arXiv:1910.11860', 'https://arxiv.org/abs/1910.11860')],
         evidence='Deposited in Oxford ORA; Fehrman at the Mathematical Institute, University of Oxford. The affiliation '
                  'printed on the paper was not seen.',
         does='**Result (quoted).** A robust well-posedness theory in energy-critical spaces for the skeleton equation, a '
              'degenerate parabolic-hyperbolic PDE with irregular drift, built on renormalized and kinetic solutions '
              '(a nonlinear extension of DiPerna–Lions and Ambrosio), with applications to the lower-semicontinuous '
              'envelopes of restricted rate functions and to zero-noise large deviations of conservative singular '
              'stochastic PDE; the authors state that it solves a long-standing open problem in the large deviations of '
              'zero-range processes and links macroscopic fluctuation theory with fluctuating hydrodynamics.',
         sota='A rigorous rare-event theory for conservative, diffusive particle systems.',
         gap='Lattice and particle systems, no Darcy advection; far from field use.',
         inputs='None directly.',
         dispersion='In macroscopic fluctuation theory the probability of a rare front is set by a rate function built '
                    'from the diffusivity and the mobility (the standard form, not quoted from this paper).',
         bcs='None.',
         step='KRIPA-GO gives the counterfactual of the typical salt front and a conformal band whose upper end is '
              '<<A_cp_hi>> km² of extra salinized area; large deviations are the route to the probability of a drought '
              'salinization far beyond that band — the tail a 90% guarantee leaves out — with the dispersion entering '
              'through the rate function.',
         novel='Rare-event theory for conservative transport, as the route from the counterfactual band to the '
               'probability of an extreme salinization beyond it.',
         steps=['guarantee'], informs=dict(inputs=0, dispersion=1, bcs=0)),
]

OX_SOTA = dict(cf='path dependence of coastal salinity (O1); drought indices and pooled ensembles (O3, O4)',
               disp='geometry versus mixing in porous plumes (O2); large deviations of conservative transport (O5)',
               sbi='rare events beyond the band (O5)')
