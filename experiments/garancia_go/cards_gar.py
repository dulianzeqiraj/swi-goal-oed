"""The twenty paper cards of the GARANCIA-GO review (five per institution), from the verification notes of the four
literature searches (November 2026). Every landing page was reached through search results only: doi.org, arxiv.org,
openreview.net and most publisher hosts were blocked in this environment, so every card is marked partly verified.

Fields: id, inst, year, short (for the map figure), title, authors, venue, links [(label, url)], evidence (who was at
the institution and where it was seen), does (what the paper does and finds), inputs / dispersion / bcs (what we learn
for the input parameters, the dispersion coefficient and the boundary conditions when only the rain is known), step
(the innovation step it gives us), steps (steps of the synthesis it serves), informs (2 direct, 1 indirect lesson).
Text conventions: $math$, **bold**, *italic*."""

CARDS = [
    # ------------------------------------------------------------------------------------------------ Oxford
    dict(id='O1', inst='Oxford', year=2021, short='ESEm emulator calibration',
         title='Model calibration using ESEm v1.1.0 – an open, scalable Earth system emulator',
         authors='Duncan Watson-Parris, Andrew Williams, Lucia Deaconu, Philip Stier',
         venue='Geoscientific Model Development 14(12), 7659–7672 (2021)',
         links=[('doi:10.5194/gmd-14-7659-2021', 'https://doi.org/10.5194/gmd-14-7659-2021'),
                ('arXiv:2108.10747', 'https://arxiv.org/abs/2108.10747'),
                ('ORA record', 'https://ora.ox.ac.uk/objects/uuid:730d5962-3c57-42cb-a18c-181d1bb80692')],
         evidence='Watson-Parris and Stier: Atmospheric, Oceanic and Planetary Physics, University of Oxford (article '
                  'summary); record in Oxford\'s ORA repository.',
         does='An open-source tool to build, validate and sample emulators of expensive Earth-system models for '
              'calibration and uncertainty quantification. The emulator can be a Gaussian process, a convolutional '
              'network or a random forest; inference ranges from rejection sampling to MCMC; model output is matched to '
              'observations with the Community Intercomparison Suite. Case studies reduce parametric uncertainty in a '
              'climate model, explore precipitation sensitivity in a cloud-resolving model and treat CMIP6 scenario '
              'uncertainty.',
         inputs='The scalar unknowns ($\\log T$, $\\kappa$, $\\tau$, the inflow mean, the initial interface) are '
                'emulated from a space-filling design of a few hundred runs and calibrated by rejection against the '
                'few heads; a calibration that would need $10^5$ runs needs $10^2$–$10^3$.',
         dispersion='Put the dispersivity in the design: if the emulated heads are flat in it, rejection returns the '
                    'prior. The emulator\'s sensitivity is the cheapest identifiability test; Proposition 6 shows the '
                    'heads are exactly flat in $w$ for the Fushë-Kuqe chloride model.',
         bcs='Time-varying boundaries are functions, so emulate them through a few coefficients (mean sea level, mean '
             'and amplitude of the inland inflow, $\\kappa$, $\\tau$) and leave the weekly departures to Gaussian fields.',
         step='Emulator error with a guarantee: calibrate the emulator itself by split conformal on held-out runs and '
              'add the calibrated radius to the discrepancy term, so the rejection step is honest about emulator '
              'error (the paper\'s posterior has no coverage guarantee).',
         steps=['emulate', 'invert'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='O2', inst='Oxford', year=2022, short='Signature ratio estimation',
         title='Amortised likelihood-free inference for expensive time-series simulators with signatured ratio '
               'estimation',
         authors='Joel Dyer, Patrick Cannon, Sebastian M. Schmon',
         venue='Proceedings of AISTATS 2022, PMLR 151, 11131–11144',
         links=[('PMLR v151', 'https://proceedings.mlr.press/v151/dyer22a.html'),
                ('arXiv:2202.11585', 'https://arxiv.org/abs/2202.11585')],
         evidence='Dyer: University of Oxford (paper\'s address; INET Oxford lists the paper). Cannon: Improbable; '
                  'Schmon: Improbable and Durham.',
         does='SignatuRE is a kernel classifier for sequential data, built on path signatures and the signature kernel, '
              'for likelihood-free density-ratio estimation. It targets time-series simulators too costly for the '
              'large simulation budgets of neural ratio estimators, and gives more accurate inference than competing '
              'ratio methods when the budget is small; tests include an Ornstein–Uhlenbeck process.',
         inputs='Once the recharge error and the vadose delay are stochastic, the chain rain → recharge → heads has no '
                'tractable likelihood. Signature features of the head series summarise it without hand-made '
                'statistics, and one trained classifier gives posteriors of $(T, \\kappa, \\tau)$ for any new record.',
         dispersion='For an electrical-conductivity or chloride series at a pumping well, the signature captures the '
                    'rise and tailing of a breakthrough, which carry the dispersivity information that heads lack.',
         bcs='Give the rain path to the signature as a channel: the classifier then learns the rain–head lag, i.e. '
             'the vadose filter, and posteriors of the boundary parameters conditioned on the observed rain.',
         step='Amortised posteriors are approximate. Their simulation-based coverage can be checked and corrected '
              'exactly as in our T4 (conformal on simulated truths), and amortisation makes the check cheap: no '
              'retraining per test case.',
         steps=['invert'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='O3', inst='Oxford', year=2024, short='FaIRGP physics-informed GP',
         title='FaIRGP: A Bayesian energy balance model for surface temperatures emulation',
         authors='Shahine Bouabid, Dino Sejdinovic, Duncan Watson-Parris',
         venue='Journal of Advances in Modeling Earth Systems 16(6), e2023MS003926 (2024)',
         links=[('arXiv:2307.10052', 'https://arxiv.org/abs/2307.10052'),
                ('doi:10.1029/2023MS003926', 'https://doi.org/10.1029/2023MS003926')],
         evidence='Bouabid: Department of Statistics, University of Oxford (arXiv byline). Sejdinovic: Adelaide; '
                  'Watson-Parris: Scripps/UCSD. Journal details from the author\'s BibTeX; the DOI was not resolved.',
         does='A Gaussian-process emulator that satisfies the temperature-response equations of the FaIR energy '
              'balance model: physics in the mean, a GP for what the physics misses. It emulates global and spatial '
              'surface temperatures across future scenarios, outperforms energy balance models, gives tractable '
              'uncertainty quantification and also estimates radiative forcing.',
         inputs='It is the structure of our recharge law, $r = \\kappa\\,(k_\\tau * P) + e$: a linear filter of a '
                'known forcing plus a GP. When the heads respond linearly, the posterior of $\\kappa$ and of $e(t)$ is '
                'closed form (in our test bed it is a one-dimensional mixture over $\\kappa$).',
         dispersion='Not treated (temperature). The lesson is structural: physics in the mean and the GP on the '
                    'residual keep the residual from absorbing a signal the physics should carry.',
         bcs='The recharge boundary becomes a physics-informed GP conditioned on the rain, updated by the heads through '
             'a linear operator, which is what our ensemble smoother with the exact solver does in ensemble form.',
         step='Learn the delay by marginal likelihood: in a linear head model the marginal likelihood of the heads '
              'given $\\tau$ is exact (a mixture over $\\kappa$), so $\\tau$ can be integrated as a hyperparameter. '
              'This is the analytic version of our T3 repair, which put $\\tau$ in the prior.',
         steps=['prior', 'emulate'], informs=dict(inputs=2, bcs=2)),
    dict(id='O4', inst='Oxford', year=2021, short='Conformal multi-horizon forecasts',
         title='Conformal time-series forecasting',
         authors='Kamilė Stankevičiūtė, Ahmed M. Alaa, Mihaela van der Schaar',
         venue='Advances in Neural Information Processing Systems 34 (NeurIPS 2021)',
         links=[('NeurIPS proceedings', 'https://proceedings.neurips.cc/paper/2021/hash/'
                                         '312f1ba2a72318edaaa995a67835fad5-Abstract.html')],
         evidence='Stankevičiūtė is listed at the University of Oxford and the University of Cambridge in the NeurIPS '
                  'PDF and the ACM record; the weakest Oxford link of the five.',
         does='Extends split conformal prediction to multi-horizon forecasting with recurrent networks: a light wrapper '
              'gives intervals with frequentist coverage for any multi-horizon forecaster, assuming that independent '
              'series are exchangeable; joint coverage of the horizon uses a Bonferroni correction. It is compared with '
              'other uncertainty methods on synthetic and real data.',
         inputs='The exchangeable units must be independent series. With one aquifer they can only be simulated '
                'aquifers drawn from the prior, which is exactly our calibration set.',
         dispersion='A multi-horizon chloride forecast at a pumping well is wrapped the same way; the dispersivity '
                    'uncertainty enters through the simulated series.',
         bcs='Each boundary function over 64 weeks is a 64-step horizon. Bonferroni at $\\alpha = 0.10$ needs each '
             'week at level $0.10/64$, which gives a finite band only with $n \\geq 639$ calibration series; the '
             'sup-norm score of GARANCIA-GO needs $n \\geq 9$ for any horizon (Remark 1).',
         step='Replace the Bonferroni correction by the maximum standardised residual over the horizon: exact for any '
              'dependence between weeks, finite from $n = 9$, and in T1 only 1.7–2.0 times the width of the exact '
              'pointwise band.',
         steps=['guarantee'], informs=dict(bcs=2, dispersion=1)),
    dict(id='O5', inst='Oxford', year=2020, short='Kwale coastal aquifer, Kenya',
         title='Evidence of groundwater vulnerability to climate variability and economic growth in coastal Kenya',
         authors='Nuria Ferrer, Albert Folch, Daniel Fernàndez-Garcia, Mike Lane, Mike Thomas, John Mwangi Gathenya, '
                 'Calvince Wara, Patrick Thomson, Emilio Custodio, Rob Hope',
         venue='Journal of Hydrology 586, 124920 (2020)',
         links=[('doi:10.1016/j.jhydrol.2020.124920', 'https://doi.org/10.1016/j.jhydrol.2020.124920'),
                ('ORA record', 'https://ora.ox.ac.uk/objects/uuid:b2ab0d4f-d40c-49e4-a146-9a999325cdfc')],
         evidence='Accepted manuscript in Oxford\'s ORA; the related BGS model record lists Rob Hope at the University '
                  'of Oxford. The paper\'s own affiliation list was not seen.',
         does='A previously calibrated flow model of the Kwale coastal aquifer (southern Kenya) is run for 2010–2017 and '
              'for eight scenarios over six hypothetical future years. Extra pumping from economic growth has a small '
              'effect compared with climate variability; shallow-aquifer levels can fall by up to 5 m in a drought and '
              'recover fairly quickly when a wet period follows.',
         inputs='In a data-scarce coastal aquifer recharge from rain is the dominant control, so rank the inputs by '
                'their effect on the decision quantity (levels in a drought) before calibrating all of them.',
         dispersion='The model is flow only (MODFLOW-2005): it shows how far a flow model goes (levels, drawdown) and '
                    'where salinity needs a transport model and salinity data.',
         bcs='Drought–recovery cycles expose the memory of the system, set by the vadose delay and the storativity; '
             'the scenarios build the recharge boundary from rain records of dry and wet years.',
         step='Turn the scenario set into a calibration set: draw the scenario years from the rain law, simulate, and '
              'give every scenario output a band with a stated miss rate (CRC over weeks).',
         steps=['prior', 'design'], informs=dict(inputs=1, bcs=2)),
    # ------------------------------------------------------------------------------------------------ Caltech
    dict(id='C1', inst='Caltech', year=2024, short='UQNO: conformal neural operator',
         title='Calibrated uncertainty quantification for operator learning via conformal prediction',
         authors='Ziqi Ma, David Pitt, Kamyar Azizzadenesheli, Anima Anandkumar',
         venue='Transactions on Machine Learning Research (2024)',
         links=[('OpenReview', 'https://openreview.net/forum?id=cGpegxy12T'),
                ('arXiv:2402.01960', 'https://arxiv.org/abs/2402.01960')],
         evidence='Anandkumar: Caltech (the paper is on her Caltech-hosted CV and the lab\'s 2024 highlights); Ma\'s '
                  'Caltech affiliation seen only in a search snippet. arXiv v2 lists Ma, Azizzadenesheli and '
                  'Anandkumar; the TMLR version adds Pitt.',
         does='UQNO is a risk-controlling quantile neural operator: a residual operator trained with a quantile loss '
              'gives a band around an operator prediction, and conformal calibration rescales it. The guarantee is '
              'distribution-free and finite-sample, on the expected fraction of domain points whose true value lies '
              'in the band. On 2D Darcy flow and 3D car-surface pressure the bands are calibrated and efficient; in 3D '
              'it was the only method to meet the 98% target.',
         inputs='For a neural-operator surrogate from ($K$ field, $\\kappa$, rain) to heads, UQNO certifies the '
                'surrogate-versus-simulator error over the domain, with simulator runs from the prior as calibration '
                'pairs.',
         dispersion='For a surrogate of the chloride field, the domain-fraction guarantee bounds the share of the '
                    'aquifer where the chloride band misses, the risk of misplacing the 250 mg/L zone.',
         bcs='In the inverse direction (data → boundary functions) the same fraction-of-points risk is our fraction '
             'of weeks outside the band.',
         step='GARANCIA-GO is UQNO turned around: the operator is the reconstructor of the boundary functions, not the '
              'forward surrogate, and the calibration truths are simulated aquifers because boundaries are never '
              'observed; the sup-norm variant adds whole-function coverage, which a fraction-of-points risk cannot give.',
         steps=['guarantee', 'emulate'], informs=dict(inputs=1, dispersion=1, bcs=2)),
    dict(id='C2', inst='Caltech', year=2025, short='EnKG: ensemble Kalman diffusion guidance',
         title='Ensemble Kalman diffusion guidance: a derivative-free method for inverse problems',
         authors='Hongkai Zheng, Wenda Chu, Austin Wang, Nikola Kovachki, Ricardo Baptista, Yisong Yue',
         venue='Transactions on Machine Learning Research (2025)',
         links=[('arXiv:2409.20175', 'https://arxiv.org/abs/2409.20175'),
                ('TMLR listing', 'https://mlanthology.org/tmlr/2025/zheng2025tmlr-ensemble')],
         evidence='Yue (Computing and Mathematical Sciences) and Baptista were at Caltech; affiliations not seen in '
                  'the byline. Venue from the TMLR listing and the arXiv notes.',
         does='EnKG solves inverse problems with a pre-trained diffusion prior using only forward-model evaluations, '
              'with no derivative or pseudo-inverse: an ensemble of particles estimates the guidance term by the '
              'statistical linearisation of ensemble Kalman methods. It is much more efficient than other '
              'derivative-free methods for expensive models such as Navier–Stokes, on imaging and scientific problems.',
         inputs='Most coastal codes have no adjoint. EnKG makes learned priors of $K$ fields usable with such codes '
                'as black boxes.',
         dispersion='Appended to the ensemble state, the dispersivity is updated only through its covariance with the '
                    'observed salinity; its covariance with heads is zero, so heads leave it alone (Proposition 6).',
         bcs='It is the derivative-free form of FunDPS. In our RINDËRTIMI-GO note plain gradient guidance missed the '
             'heads by 24.5 cm, while the ensemble update with the exact solver fitted them to 2.1 cm; EnKG is the '
             'principled bridge between the two.',
         step='Use the EnKG ensemble as the reconstructor inside GARANCIA-GO: its bands come from a statistical '
              'linearisation and are uncalibrated, and one batch of simulated aquifers fixes their coverage.',
         steps=['invert'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='C3', inst='Caltech', year=2022, short='Ensemble Kalman training from statistics',
         title='Training physics-based machine-learning parameterizations with gradient-free ensemble Kalman methods',
         authors='Ignacio Lopez-Gomez, Costa Christopoulos, Haakon Ludvig Langeland Ervik, Oliver R. A. Dunbar, '
                 'Yair Cohen, Tapio Schneider',
         venue='Journal of Advances in Modeling Earth Systems 14, e2022MS003105 (2022)',
         links=[('doi:10.1029/2022MS003105', 'https://doi.org/10.1029/2022MS003105'),
                ('CaltechAUTHORS', 'https://authors.library.caltech.edu/records/q40ve-64h03')],
         evidence='CaltechAUTHORS record; Schneider\'s climate dynamics group at Caltech.',
         does='Training a parameterisation is cast as an inverse problem, so it can use partial observations or '
              'statistics tied to the quantities of interest. Unscented and ensemble Kalman inversion are compared: '
              'parallel forward runs, fast convergence, no gradients. An eddy-diffusivity mass-flux scheme is '
              'calibrated; the methods take batching, are robust to noise and model failures, and train hybrid '
              'closures with neural networks.',
         inputs='Calibrate $T$ and $\\kappa$ against statistics rather than raw series (seasonal mean head, seasonal '
                'amplitude, lag of the head peak after the rain peak), which tolerate the gaps of sparse loggers.',
         dispersion='Robustness to model failures matters for variable-density codes that fail for extreme '
                    'dispersivity or $K$; unscented inversion gives a Gaussian estimate of how much salinity '
                    'statistics constrain the dispersivity.',
         bcs='The recharge closure (filter, coefficient, error) is a hybrid parameterisation, physics plus a learned '
             'part, and the paper shows how to train it from indirect data (heads), as recharge itself is never '
             'observed.',
         step='Calibrate on statistics, guarantee on functions: Kalman inversion for the parameters, then '
              'GARANCIA-GO bands for the boundary functions. The guarantee does not need the calibration to be '
              'exact, only the same reconstructor on simulated and field cases.',
         steps=['invert'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='C4', inst='Caltech', year=2022, short='EnsembleKalmanProcesses.jl',
         title='EnsembleKalmanProcesses.jl: derivative-free ensemble-based model calibration',
         authors='Oliver R. A. Dunbar, Ignacio Lopez-Gomez, Alfredo Garbuno-Iñigo, Daniel Zhengyu Huang, Eviatar Bach, '
                 'Jin-long Wu',
         venue='Journal of Open Source Software 7(80), 4869 (2022)',
         links=[('doi:10.21105/joss.04869', 'https://doi.org/10.21105/joss.04869'),
                ('code', 'https://github.com/CliMA/EnsembleKalmanProcesses.jl')],
         evidence='A package of the Climate Modeling Alliance (CliMA) at Caltech; the per-author affiliations were not '
                  'seen in the byline.',
         does='A Julia toolbox for black-box, gradient-free calibration of model parameters against data with ensemble '
              'Kalman processes (ensemble and unscented Kalman inversion and related samplers). A TOML-file interface '
              'lets models written in any language be calibrated without rewriting them.',
         inputs='The coastal model stays in Python, MATLAB or a compiled code: a calibration loop of a few hundred runs '
                'for $T$, $\\kappa$ and $\\tau$ around an unchanged simulator.',
         dispersion='The samplers give approximate posterior samples of the dispersivity; comparing them with the prior '
                    'shows whether the salinity data inform it at all.',
         bcs='Weekly boundary values can be the calibrated parameters themselves; the ensemble then plays the role of '
             'our smoother.',
         step='A two-line extension of any such workflow: take the ensemble mean and spread per quantity, simulate '
              '$n \\geq 20$ aquifers from the prior, and turn them into guaranteed bands (T2 shows the mean '
              'guarantee already holds at $n = 20$).',
         steps=['invert'], informs=dict(inputs=2, dispersion=1, bcs=1)),
    dict(id='C5', inst='Caltech', year=2022, short='Remote sensing of groundwater (JPL)',
         title='Remote sensing of groundwater: current capabilities and future directions',
         authors='Kyra H. Adams, John T. Reager, Paul Rosen, David N. Wiese, Tom G. Farr, Shanti Rao, Bruce J. Haines, '
                 'Donald F. Argus, Zhen Liu, Ryan Smith, James S. Famiglietti, Matthew Rodell',
         venue='Water Resources Research 58(10), e2022WR032219 (2022)',
         links=[('doi:10.1029/2022WR032219', 'https://doi.org/10.1029/2022WR032219'),
                ('NSF PAR', 'https://par.nsf.gov/biblio/10425899')],
         evidence='The corresponding author (Reager) has a jpl.nasa.gov address; the Jet Propulsion Laboratory is '
                  'managed by Caltech for NASA. The full affiliation list was not seen.',
         does='A review of remote sensing for groundwater from local to global scales, including proxies for '
              'extraction: gravity-based mass change (GRACE), surface-height change from InSAR, LiDAR and airborne '
              'electromagnetics, and satellite altimetry, used together with well heads, GNSS and numerical models. '
              'The authors argue that fusing these techniques gives better insight into groundwater use.',
         inputs='InSAR subsidence and GNSS add conditions on storage change, which constrains the storativity and, with '
                'the heads, the transmissivity; GRACE is too coarse for a 349 km² aquifer but bounds regional '
                'storage trends.',
         dispersion='Airborne electromagnetics maps resistivity, hence salinity at depth: the one remote technique '
                    'that sees the transition zone and so the dispersion width $w$.',
         bcs='Satellite altimetry and coastal gauges observe the sea-level boundary directly, so it need not be '
             'reconstructed: with a gauge or an altimeter $\\eta(t)$ becomes a datum instead of an unknown.',
         step='Rank the remote data by the guaranteed width they remove: add each source as an observation row of '
              'the reconstructor and recompute the calibrated band (our T1A against T1 does this for four loggers).',
         steps=['prior', 'design'], informs=dict(inputs=1, dispersion=2, bcs=2)),
    # ------------------------------------------------------------------------------------------------ Berkeley
    dict(id='B1', inst='Berkeley', year=2025, short='GeoFUSE seawater-intrusion surrogate (LBNL)',
         title='GeoFUSE: an efficient surrogate model for seawater intrusion prediction and uncertainty reduction',
         authors='Su Jiang, Chuyang Liu, Dipankar Dwivedi',
         venue='Water Resources Research 61(9), e2024WR038898 (2025)',
         links=[('doi:10.1029/2024WR038898', 'https://doi.org/10.1029/2024WR038898'),
                ('arXiv:2410.20118', 'https://arxiv.org/abs/2410.20118')],
         evidence='Lawrence Berkeley National Laboratory, Berkeley, for Jiang and Dwivedi (Wiley listing) and first '
                  'affiliation of Jiang and Liu (PDF); funded by an LBNL project on groundwater and salinity under '
                  'sea-level rise. LBNL is the national laboratory managed by the University of California.',
         does='A U-FNO surrogate, a PCA description of the geology and ES-MDA data assimilation. The surrogate is '
              'trained on 1,500 PFLOTRAN seawater-intrusion runs (100 more held out) of a 2D section of the Beaver '
              'Creek tidal stream and floodplain (Washington State); it cuts run time from hours to seconds (about '
              '360,000 times faster). Assimilating monitoring-well data over four steps reduces geological uncertainty '
              'and improves 20-year salinity predictions.',
         inputs='The closest template for Fushë-Kuqe: $K$ (PCA coefficients), $\\kappa$, the inland inflow and the '
                'initial interface in the prior ensemble, with the surrogate making the ensemble affordable.',
         dispersion='What could be read covers the geology only; check whether the dispersivity was varied. If not, '
                    'the salinity predictions inherit a fixed dispersivity, and by Proposition 6 only the salinity '
                    'data could have informed it.',
         bcs='Their tidal boundaries are prescribed; for us the sea level is uncertain ($\\eta$ mean and weekly '
             'departures) and belongs in the ensemble.',
         step='GeoFUSE + GARANCIA-GO: an ES-MDA ensemble has no coverage guarantee (in T1 the raw ensemble missed '
              '17–20% of the weeks at nominal 10%, and 67% for $\\kappa$). The 100 held-out PFLOTRAN runs are already '
              'a calibration set for guaranteed salinity bands.',
         steps=['emulate', 'invert'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='B2', inst='Berkeley', year=2020, short='Veridical data science (PCS)',
         title='Veridical data science',
         authors='Bin Yu, Karl Kumbier',
         venue='Proceedings of the National Academy of Sciences 117(8), 3920–3929 (2020)',
         links=[('arXiv:1901.08152', 'https://arxiv.org/abs/1901.08152'),
                ('author PDF', 'https://www.stat.berkeley.edu/~binyu/ps/papers2020/VDS20-YuKumbier.pdf')],
         evidence='Statistics Department, University of California, Berkeley (author affiliation in the PNAS record, as '
                  'summarised in search results); the PDF is on the Berkeley statistics server.',
         does='Three principles for the whole data-science life cycle: predictability (results are checked by '
              'prediction on held-out data), computability (computation, including simulation, is part of how data are '
              'produced and analysed) and stability (results must survive reasonable perturbations of the data and of '
              'the model and algorithm, including the human judgment calls). Together they form the PCS framework, with a '
              'workflow, documentation, and perturbation intervals that carry uncertainty beyond sampling to the judgment '
              'calls; it is demonstrated on a genomics case study.',
         inputs='With few conditions the inferred $T$, $\\kappa$ and $\\tau$ depend on judgment calls: which rain product '
                '(station, E-OBS, ERA5-Land), which vadose kernel, which prior widths. Report each conclusion with the '
                'spread it shows across these reasonable choices.',
         dispersion='The transition-zone width comes from a few chloride facts whose assignment to aquifer layers is '
                    'itself a judgment call (the chloride study also runs the alternative "shallow" assignment of the '
                    'mid-depth wells); the stability check reruns T4 with each assignment.',
         bcs='T3 is a stability failure found by simulation: a vadose delay 2.5 times longer breaks every guarantee. A '
             'perturbation analysis over the delay exposes it before the bands are used in the field.',
         step='PCS-calibrated GARANCIA-GO: draw the judgment calls themselves (rain product, kernel form, prior widths) in '
              'the simulated aquifers, so that the conformal guarantee covers them by construction; the T3 repair, which '
              'put $\\tau$ in the prior, is the first instance.',
         steps=['check', 'guarantee'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='B3', inst='Berkeley', year=2022, short='Image-to-image distribution-free UQ',
         title='Image-to-image regression with distribution-free uncertainty quantification and applications in imaging',
         authors='Anastasios N. Angelopoulos, Amit P. Kohli, Stephen Bates, Michael I. Jordan, Jitendra Malik, '
                 'Thayer Alshaabi, Srigokul Upadhyayula, Yaniv Romano',
         venue='Proceedings of ICML 2022, PMLR 162, 717–730',
         links=[('PMLR v162', 'https://proceedings.mlr.press/v162/angelopoulos22a.html'),
                ('arXiv:2202.05265', 'https://arxiv.org/abs/2202.05265')],
         evidence='UC Berkeley EECS and the UC Berkeley Advanced Bioimaging Center (author listing); Romano: Technion.',
         does='Per-pixel intervals around any image-to-image model: the model outputs a prediction and rough lower and '
              'upper lengths, and one scale factor is calibrated on held-out data so that, with probability at least '
              '$1 - \\delta$, the expected fraction of pixels outside their intervals is at most $\\alpha$. '
              'Pixel-wise quantile regression gave the best rough intervals; applications are phase microscopy, '
              'accelerated MRI and super-resolution electron microscopy.',
         inputs='$K$ and head maps are images: a map-to-map surrogate gets per-cell bands with a fraction-of-cells '
                'guarantee.',
         dispersion='A guaranteed probabilistic chloride map. The guarantee is on the share of cells, not on every '
                    'cell, so it does not bound the toe position by itself.',
         bcs='Our time-fraction CRC is the one-dimensional case, $m(t) \\pm \\lambda s(t)$ with one $\\lambda$. The '
             'paper shows that the heuristic scale decides efficiency; the ensemble spread is a good one here (CRC '
             'widths 1.11–1.36 times the exact posterior).',
         step='Calibrate one $\\lambda$ per boundary function, as we do, and one more for the whole head field '
              '$h(x, t)$: a guaranteed band for the head map from four loggers.',
         steps=['guarantee'], informs=dict(inputs=1, dispersion=2, bcs=2)),
    dict(id='B4', inst='Berkeley', year=2023, short='Outlier tests with conformal p-values',
         title='Testing for outliers with conformal p-values',
         authors='Stephen Bates, Emmanuel Candès, Lihua Lei, Yaniv Romano, Matteo Sesia',
         venue='Annals of Statistics 51(1), 149–178 (2023)',
         links=[('doi:10.1214/22-AOS2244', 'https://doi.org/10.1214/22-AOS2244'),
                ('arXiv:2104.08279', 'https://arxiv.org/abs/2104.08279')],
         evidence='The Annals record lists UC Berkeley among the affiliations (Bates), with Stanford, Technion and USC.',
         does='Outlier detection as multiple testing. Conformal p-values are marginally valid but dependent across test '
              'points; they are positively dependent, which allows exact false discovery rate control in a weaker '
              'marginal sense. The paper also gives p-values valid conditionally on the training data and independent '
              'across test points, and a uniform confidence bound on the false positive rate of any outlier detector.',
         inputs='The field check is an outlier test: is the field aquifer an outlier among the simulated ones? The '
                'conformal p-value of the held-out-head score answers with a valid false-alarm rate (0.10 under the '
                'prior in T3).',
         dispersion='The same test on salinity residuals detects a wrong dispersivity prior; on heads it cannot '
                    '(Proposition 6).',
         bcs='T3: a vadose delay 2.5 times longer in the field raises the alarm rate to 0.67, a parameter shift '
             '(inflow +0.8 m²/d, $\\kappa \\times 1.5$, sea level +0.1 m) only to 0.19.',
         step='One p-value per well and season, with the false-alarm rate controlled across them by the positive '
              'dependence result: a monitoring network that says which record conflicts with the prior.',
         steps=['check'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='B5', inst='Berkeley', year=2023, short='Calibrated multiple-output regions',
         title='Calibrated multiple-output quantile regression with representation learning',
         authors='Shai Feldman, Stephen Bates, Yaniv Romano',
         venue='Journal of Machine Learning Research 24(24), 1–48 (2023)',
         links=[('JMLR v24', 'https://www.jmlr.org/papers/v24/21-1280.html'),
                ('arXiv:2110.00816', 'https://arxiv.org/abs/2110.00816')],
         evidence='Bates: Departments of EECS and Statistics, UC Berkeley (arXiv byline, from the search summary); '
                  'Feldman and Romano: Technion.',
         does='A deep generative model learns a representation in which the multivariate response is unimodal; '
              'multiple-output quantile regression is run there and mapped back. A conformal extension to multivariate '
              'responses returns regions with a pre-specified coverage, guaranteed in finite samples for any '
              'distribution; the regions are significantly smaller than those of existing techniques.',
         inputs='Joint regions for $(T, \\kappa, \\tau)$ instead of three marginal intervals: the joint region shows '
                'the trade-off between $T$ and $\\kappa$ that the heads leave open.',
         dispersion='A joint region for (recharge, $w$) from chloride facts would show how a recharge error moves the '
                    'inferred dispersion width.',
         bcs='The boundary functions are dependent (recharge and inflow both raise the heads); a joint region over '
             '$(\\eta, q_L, r)$ is smaller than the product of separate bands.',
         step='Joint sup-norm bands: score each case by the largest standardised residual over all boundary '
              'functions together, which gives one guaranteed region for the whole set of boundary conditions.',
         steps=['guarantee'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    # ------------------------------------------------------------------------------------------------ MIT
    dict(id='M1', inst='MIT', year=2020, short='Rain partitioned with SMAP',
         title='Partitioning of historical precipitation into evaporation and runoff based on hydrologic dynamics '
               'identified with recent SMAP satellite measurements',
         authors='Ruzbeh Akbar, Daniel J. Short Gianotti, Guido D. Salvucci, Dara Entekhabi',
         venue='Water Resources Research 56(12), e2020WR027307 (2020)',
         links=[('doi:10.1029/2020WR027307', 'https://doi.org/10.1029/2020WR027307'),
                ('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/140939')],
         evidence='Author\'s final manuscript in DSpace@MIT; Entekhabi is MIT Civil and Environmental Engineering '
                  'faculty. Byline affiliations not seen.',
         does='SMAP brightness temperatures and gauge precipitation over the United States identify the soil-water loss '
              'function; with it, historical (1979–2019) evapotranspiration and drainage are reconstructed from '
              'precipitation alone. Drainage correlates with USGS streamflow at $R^2 > 0.6$ except in snowy and '
              'hyper-arid regions, and responds near-linearly to precipitation anomalies in parts of the Great Plains '
              'and nonlinearly in the southeastern US.',
         inputs='The recharge coefficient: a satellite-identified loss function turns a rainfall-only record into a '
                'drainage series, whose drainage fraction can replace our lognormal guess for $\\kappa$ (median 0.35, '
                'log-sd 0.25) as an informative prior.',
         dispersion='None directly.',
         bcs='The nonlinear responses warn that "constant $\\kappa$ × filtered rain" may misfit a wet-winter, '
             'dry-summer climate; a moisture-dependent coefficient is the next model. Caveats: US validation against '
             'streamflow, drainage is not recharge, and SMAP cells (about 36 km) are larger than the 349 km² polygon.',
         step='Use the satellite drainage as a second rain channel of the reconstructor and measure what it adds by '
              'the calibrated band of $\\kappa$, with and without it.',
         steps=['prior'], informs=dict(inputs=2, bcs=2)),
    dict(id='M2', inst='MIT', year=2021, short='Few-shot conformal, auxiliary tasks',
         title='Few-shot conformal prediction with auxiliary tasks',
         authors='Adam Fisch, Tal Schuster, Tommi Jaakkola, Regina Barzilay',
         venue='Proceedings of ICML 2021, PMLR 139, 3329–3339',
         links=[('PMLR v139', 'https://proceedings.mlr.press/v139/fisch21a.html'),
                ('arXiv:2102.08898', 'https://arxiv.org/abs/2102.08898')],
         evidence='DSpace@MIT files the paper under CSAIL.',
         does='With little data for the target task, conformal sets can be too large to be useful. The paper casts '
              'conformal prediction as meta-learning over exchangeable collections of auxiliary tasks, which train a '
              'few-shot model and a quantile predictor; the sets become substantially tighter while marginal coverage '
              'is kept, for any underlying model, on few-shot classification and regression in NLP, vision and '
              'chemistry.',
         inputs='The auxiliary tasks can be synthetic aquifers from the prior or other monitored aquifers; the target '
                'task is Fushë-Kuqe, and coverage holds if Fushë-Kuqe is exchangeable with the tasks.',
         dispersion='Pooled over aquifers with measured dispersivities, the meta-learned quantile predictor would give '
                    'calibrated intervals for a new site, again only under exchangeability.',
         bcs='With $n$ field-measured boundary values (a few months of a tide gauge), split conformal needs $n \\geq 9$ '
             'for a finite 90% interval; meta-learning shrinks the width at small $n$.',
         step='GARANCIA-GO is the special case in which every auxiliary task is simulated. The next step mixes '
              'simulated aquifers with real ones that have known boundaries, a route from "valid under the prior" '
              'towards "valid in the field".',
         steps=['guarantee'], informs=dict(inputs=2, dispersion=1, bcs=2)),
    dict(id='M3', inst='MIT', year=2021, short='Distributional conformal prediction',
         title='Distributional conformal prediction',
         authors='Victor Chernozhukov, Kaspar Wüthrich, Yinchu Zhu',
         venue='Proceedings of the National Academy of Sciences 118(48), e2107794118 (2021)',
         links=[('doi:10.1073/pnas.2107794118', 'https://doi.org/10.1073/pnas.2107794118'),
                ('arXiv:1909.07889', 'https://arxiv.org/abs/1909.07889'),
                ('DSpace@MIT', 'https://dspace.mit.edu/handle/1721.1/144455')],
         evidence='DSpace@MIT record; Chernozhukov is at MIT.',
         does='Prediction intervals from models of the conditional distribution (quantile or distribution regression), '
              'with the conditional rank (probability integral transform) as conformity score and permutation of the '
              'estimated ranks. They are conditionally valid if the model is correct and unconditionally valid under '
              'misspecification, overfitting and time-series data; a shape adjustment gives optimal intervals.',
         inputs='The rank of the truth under the posterior is what simulation-based calibration checks (our T4 '
                'coverage of the importance-sampling intervals); the paper turns that diagnostic into intervals with a '
                'guarantee.',
         dispersion='The T4 posterior of $w$ is a full distribution; its quantiles can be calibrated directly instead '
                    'of the $m \\pm q\\sigma$ on the log scale that we used.',
         bcs='Each week the ensemble gives a predictive distribution of $\\eta(t)$; ranks of the simulated truths '
             'calibrate the whole distribution, useful when users need different levels.',
         step='Distributional GARANCIA-GO: replace the score $|g - m|/s$ by the rank of the truth in the ensemble, so '
              'one set of simulated aquifers gives guaranteed bands at every level at once.',
         steps=['guarantee'], informs=dict(inputs=2, dispersion=2, bcs=2)),
    dict(id='M4', inst='MIT', year=2024, short='Online conformal, decaying steps',
         title='Online conformal prediction with decaying step sizes',
         authors='Anastasios N. Angelopoulos, Rina Foygel Barber, Stephen Bates',
         venue='Proceedings of ICML 2024, PMLR 235, 1616–1630',
         links=[('PMLR v235', 'https://proceedings.mlr.press/v235/angelopoulos24a.html'),
                ('arXiv:2402.01139', 'https://arxiv.org/abs/2402.01139')],
         evidence='Bates: MIT (arXiv byline); Angelopoulos: UC Berkeley; Barber: University of Chicago.',
         does='An online conformal method that updates the prediction threshold with decaying step sizes. Like earlier '
              'online methods it keeps a retrospective guarantee of long-run coverage for arbitrary sequences; unlike '
              'them it also estimates the population quantile when one exists, so that with a stable distribution the '
              'coverage is close to the target at every time point and not only on average, and the threshold is more '
              'stable than with fixed steps.',
         inputs='As head readings arrive week after week, the band around the reconstructed heads can be recalibrated '
                'online. In a stable regime the threshold settles, so a threshold that keeps drifting is itself a sign '
                'that the inputs ($T$, $\\kappa$, $\\tau$) have changed.',
         dispersion='For a chloride record at a pumping well, the online threshold of the chloride forecast keeps '
                    'long-run coverage while the transition zone moves.',
         bcs='The simulation-calibrated bands of GARANCIA-GO are fixed once. Online updating with the real readings '
             'adapts them after deployment: the route from "valid under the prior" to "valid over time in the field" '
             'for the observable heads.',
         step='Start the online threshold at the simulation-calibrated $\\hat\\lambda$ and let the decaying steps move '
              'it with the real readings: the prior gives the starting value, the record corrects it, and a threshold '
              'that keeps drifting is an alarm that complements the conformal p-value (B4).',
         steps=['check', 'design'], informs=dict(inputs=1, dispersion=1, bcs=2)),
    dict(id='M5', inst='MIT', year=2025, short='Consistent spatial validation',
         title='Consistent validation for predictive methods in spatial settings',
         authors='David R. Burt, Yunyi Shen, Tamara Broderick',
         venue='Proceedings of AISTATS 2025, PMLR 258, 820–828',
         links=[('PMLR v258', 'https://proceedings.mlr.press/v258/burt25a.html'),
                ('arXiv:2402.03527', 'https://arxiv.org/abs/2402.03527')],
         evidence='MIT LIDS and EECS (Broderick); MIT News covered the paper.',
         does='Standard validation can fail for spatial data. A validation method should become accurate as the '
              'validation data become denser; holdout and one-nearest-neighbour validation fail this, while the '
              'proposed spatial nearest-neighbour method meets it under infill asymptotics, on synthetic and real '
              'data.',
         inputs='Validating a $K$ or head map against clustered wells by random holdout is biased when the targets lie '
                'away from the wells; spatial nearest-neighbour weighting fixes the yardstick.',
         dispersion='For a chloride map from a few wells clustered along the coast, it corrects the optimism of '
                    'holdout for inland targets.',
         bcs='Our field check holds out readings at random from the same four loggers; for targets far from them '
             '(the inland inflow) a spatially matched holdout is the right yardstick.',
         step='A spatial field check: choose the held-out readings so that their locations match those of the '
              'decision, and the conformal p-value tests the prior where the decision is taken.',
         steps=['check'], informs=dict(inputs=2, dispersion=1, bcs=1)),
]

INST_ORDER = ('Oxford', 'Caltech', 'Berkeley', 'MIT')
