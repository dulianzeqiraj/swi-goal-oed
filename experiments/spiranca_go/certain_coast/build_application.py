"""CERTAIN-COAST: the text for every field of the NATO SPS Multi-Year Project application form, in the order of the
official sample form (sps-myp-sample-application-form.pdf, platform https://natosps.grantplatform.com), with word limits
checked, budget tables mapped to the SPS budget categories and milestones, and a checklist of uploads and signatures.
This is the one document the applicants copy from; the other CERTAIN-COAST documents are background.

usage: python build_application.py OUT.docx"""
import os
import re
import sys
from collections import defaultdict

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_sota import para, heading, table, shade  # noqa: E402
import build_budget as BB  # noqa: E402
import build_risk as BR  # noqa: E402
import build_ethics as BEt  # noqa: E402

NAVY, GREY = '1F3864', '52606D'
TITLE = 'Certified early warning to protect water, port and energy infrastructure on a sinking Adriatic coast'
SHORT = 'CERTAIN-COAST'

# ------------------------------------------------------------------------------------------------- answers (English)
SECURITY = (
    'Three kinds of critical infrastructure of a NATO Ally stand on the same low Adriatic coastal plain of Albania, at two '
    'sites. At Durrës lie the wellfields that supply drinking water and the Port of Durrës, from which 93.6% of Albania\'s '
    'seaborne freight left in the second quarter of 2025 (INSTAT). Further south, near Fier, the Trans Adriatic Pipeline '
    '(TAP) leaves the shore for its 105 km crossing to Italy, carrying gas from Azerbaijan to Europe. The plain is built of '
    'soft sediments that settle slowly (Métois et al., 2020); at Durrës the ground is sinking close to active thrust faults, '
    'and the Mw 6.4 earthquake of 26 November 2019 caused liquefaction along the coast.\n'
    'The assets face three linked hazards. Seawater intrudes into the aquifer and can make wells unusable for years. In an '
    'earthquake, saturated sand can liquefy under quays, foundations and the landfall. Storm surges and extreme sea levels '
    'flood low ground. Land subsidence and sea-level rise worsen all three at once, because they raise the sea and the water '
    'table together. Pumping moves the hazards in opposite directions: it draws seawater towards the wells but lowers the '
    'water table and so strengthens the ground against liquefaction. Managing one hazard alone can increase another.\n'
    'Today these hazards are monitored by different institutions with different models, and no warning states how often it '
    'misses. For security decisions this is the critical gap: an operator who must cut pumping, restrict a quay or inspect '
    'the landfall needs to know how far a warning can be trusted, and civil protection needs one consistent picture of '
    'water, port and energy after an earthquake or a storm.\n'
    'The security challenge is therefore to keep three essential services of an Ally working, and to know in advance when '
    'they will stop being safe. The project serves three of NATO\'s seven baseline requirements for national resilience '
    '(resilient food and water resources, resilient civil transportation systems and resilient energy supplies) and the '
    'topic of particular interest of the 2027-1 call, "protection of critical infrastructure, supplies and personnel; '
    'maritime and undersea infrastructure resilience". NATO\'s 2022 Strategic Concept calls climate change "a crisis and '
    'threat multiplier"; on this coast the multiplication is physical and measurable.\n'
    'A second challenge is trust in machine-learned tools used in security decisions. CERTAIN-COAST uses artificial '
    'intelligence only with a certified error bound and a miss rate that is checked in operation, in line with NATO\'s '
    'Principles of Responsible Use of AI.')

TECHNICAL = (
    'Four technical problems stand between current science and a warning that operators can act on.\n'
    '1. The hazards are coupled but modelled apart. Seawater intrusion, aquifer compaction, liquefaction and coastal '
    'water levels depend on the same two variables, relative sea level and the water table, yet are computed by '
    'separate models. A pumping decision cannot be checked against all of them at once.\n'
    '2. Relative sea level must be known at each asset, not only at the tide gauge. The land at Durrës moves '
    'vertically by different amounts from place to place, including the 2019 coseismic step; this motion must be '
    'measured with satellite radar (InSAR) and GNSS and carried into every hazard model with its uncertainty.\n'
    '3. Physical models are too slow for warnings, and machine-learned copies come without a guarantee. '
    'Neural-operator surrogates make the thousands of daily runs possible, but a surrogate used for safety '
    'must state its error for each forecast.\n'
    '4. No warning in this field states how often it misses. Recent statistical methods (online, regime-wise and '
    'extreme conformal prediction, and anytime-valid verification) can provide such guarantees, but they have not been '
    'applied to coupled coastal hazards driven by slow physics, with dependent alarms and few extreme events.\n'
    'Six further problems have no published solution. There is no method to compute the set of pumping and dewatering '
    'decisions that keeps all the hazards within certified limits at once, nor the sea level or year at which this set '
    'disappears; tipping points exist for seawater intrusion alone, not for the coupled system. And monitoring '
    "networks are designed to reduce today's forecast errors; there is no criterion for how many years of safe "
    'operation a sensor buys. And routine pumping never shows how the aquifer responds near the onset of intrusion, '
    'which decides how long safe operation lasts; we found no pumping-test design that reveals it safely and values '
    'the test in years. And the source of rising chloride is often unknown: seawater, deep brine drawn up under the '
    'wells, a drought that concentrates the recharge, or irrigation return flow and wastewater. Each calls for a '
    'different action, and acting on the wrong one can make the salinity worse, yet no method lets the utility and its '
    'stakeholders decide before the source is known, with a risk that holds whatever it is. And every model of the '
    'aquifer is cut somewhere inland: a fixed head, a prescribed inflow or a general-head boundary does not respond to pumping or to the sea as the aquifer beyond does, and in tests this '
    'choice changed the fresh water lost to sea-level rise ninefold; no method learns the true boundary from data while '
    'keeping the model stable. And after an earthquake the pore-pressure step depends on each layer\'s stiffness; in '
    'tests the usual estimate overstated it 35 times in soft sand.\n'
    'All of this must work on a real coast with incomplete records, under security restrictions on data, and in a form '
    'that the operators can run themselves after the project.')

DELIVER = (
    'By Month 36 the project delivers:\n'
    '1. A coastal motion atlas from Durrës to Fier and relative sea level at each asset, from Sentinel-1 InSAR, '
    'reflectors and GNSS (D1.1).\n'
    '2. A monitoring network chosen for the warnings and handed over to the operators (D4.2): piezometers with '
    'conductivity loggers, a barometer and sealed hub channels that correct them, a local rain gauge, GNSS, seismic '
    'nodes and, where access allows, fibre-optic sensing.\n'
    '3. One calibrated model that couples groundwater flow and salt, aquifer compaction, liquefaction under a moving '
    'water table and coastal water levels, its inland boundary learned from the heads (D2.1), and a fast '
    'neural-operator copy with a certified error bound (D2.2).\n'
    '4. Certified alarms for seawater intrusion, liquefaction and extreme water levels whose miss rate is bounded in '
    'advance (indicatively 5–10%), with a joint guarantee for the three assets, back-tested since 2014 under a '
    'pre-registered protocol (D3.1, D3.2).\n'
    "5. Decisions for the water utility: the effect of each wellfield's pumping on salinity with the hidden drought "
    'demand removed; the salinity under drier recharge; the certified safe operating window and the year it closes; '
    'safe pumping tests that sharpen it; a pumping rule agreed with the utility; and pumping safe while the '
    'source of the chloride is unknown.\n'
    '6. Twelve months of live bulletins with the five end-users, every outcome logged and the miss rates verified '
    '(D5.1); operating procedures and a policy brief (D6.2); open software and data with a DOI (D6.1).\n'
    'How this advances the state of the art. The alarms apply conformal and anytime-valid methods of 2023–2026 to '
    'coupled coastal hazards. Nine new contributions were tested before the project. (i) Guarantees for quantities '
    'nobody measures: inputs and boundaries known only through rain, with bands valid when the simulator or rain '
    'product is wrong. (ii) The value of a sensor as the guaranteed band it removes and the years of safe operation it '
    'adds (in tests, a tide gauge rated useful by an ensemble widened the band by 16–21%). (iii) Pumping effects '
    'free of hidden confounding, read from the heads. (iv) The certified '
    'safe operating window and safe pumping tests chosen for the years they add. (v) A network that corrects its own '
    'sensors for air pressure and logger drift. (vi) Warnings between samples: a '
    'certified band for the chance that chloride crosses its limit at any time in the season (34 times the exceedance '
    'on sampling dates in tests). (vii) Decisions before the source of the salt is known: pumping safe for every source '
    'the tracers cannot exclude (in tests ≤6.9% risk for a 10% budget; assuming seawater intrusion: 98%). (viii) A '
    'boundary that learns the aquifer beyond the model: exact for any linear aquifer, stable by construction, learned '
    'from two piezometers (6 mm against 372 mm on an unseen drought in tests). (ix) Which layer feels an earthquake, '
    'and its step as a free pumping test (in tests the usual estimate overstated the soft-sand step 35 times). The '
    'integrated system reaches TRL 6 on site, with the operators.')


HOW = (
    'Seven work packages run over 36 months in three phases, separated by evidence gates with thresholds fixed in '
    'advance.\n'
    'Observe and measure (Months 1–12). WP4 designs the network before buying it: each candidate sensor (piezometers '
    'with conductivity loggers, a rain gauge, GNSS, seismic nodes, a barometer and hub channels that correct the '
    'loggers) is ranked by the guaranteed warning band it removes and the years of safe operation it adds per euro; '
    'the network is chosen against the worst plausible sensor error, with a certified optimality gap (D4.1, Month 6); '
    'a logger or samples paired a few days apart are added where sparse samples leave crossings between them open. WP1 '
    'obtains vertical land motion and relative sea level at each asset from Sentinel-1 InSAR since 2014 and GNSS, and '
    'the head limit for pumping from aquifer compaction.\n'
    'Model and certify (Months 4–30). WP2 builds one coupled model in stages (flow and salt, then compaction and '
    'liquefaction). The inputs and boundaries nobody measures are reconstructed from rain and heads by a generative '
    'prior with an ensemble update. Their bands, calibrated on simulated aquifers and measured anchor periods, stay '
    'valid if the simulator is wrong or the climate drifts. The inland boundary is learned from two piezometers as '
    'passive storage compartments. Gate MS3 (Month 18) requires held-out heads, chloride, InSAR and seismic velocity inside the 90% intervals. A '
    'neural-operator copy with a certified error bound then serves the warnings. WP3 agrees thresholds and tolerable '
    'miss rates with the operators, builds the alarms (crossings between samples included), back-tests them since 2014 '
    'under a protocol registered before the results; gates MS4 (Month 22) and MS5 (Month 27) decide live operation and '
    'confirm the miss rates.\n'
    'Operate, verify and hand over (Months 22–36). WP5 runs the system live for twelve months, logs every bulletin '
    'with its outcome, verifies the miss rates with anytime-valid tests and runs a post-event protocol. It estimates '
    "what each wellfield's pumping does to the salinity with the hidden drought demand removed, reading the recharge "
    'from the heads under a calibrated check. While the source of the chloride is uncertain, tracers chosen for the '
    'decisions they change keep only the sources the data cannot exclude, updated monthly, and the pumping stays safe '
    'for all of them. It computes the salinity under drier recharge, the certified safe operating window, its closing '
    'year and safe pumping tests that sharpen it, and agrees a pumping rule with the utility. WP6 trains early-career '
    'researchers and operators, releases open software and transfers the method to a partner coast. WP7 manages data '
    'access, security classification, risks and reporting.\n'
    'Collaboration. The Albanian team leads WP1–WP5 and WP7; the partner-country team leads WP6, a transfer study on '
    'its own coast and a user-side review of the bulletins. Early-career researchers of both countries work across '
    'work packages, with two-month exchanges. End-users set thresholds, join a dry run and co-sign operational '
    'milestones; a steering committee with them meets every six months, and each gate has a named fallback.')


SOTA_REFS = [
    ('Abbas, A., Yang, Y., Pan, M., et al. (2026). Comprehensive global assessment of 24 gridded precipitation datasets across '
     '18 428 catchments using hydrological modeling. Hydrology and Earth System Sciences 30(11), 3399–3423.',
     'https://doi.org/10.5194/hess-30-3399-2026'),
    ('Adams, K. H., Reager, J. T., Buzzanga, B. A., David, C. H., Sawyer, A. H., Hamlington, B. D. (2024). Climate-induced '
     'saltwater intrusion in 2100: recharge-driven severity, sea level-driven prevalence. Geophysical Research Letters '
     '51(22), e2024GL110359.', 'https://doi.org/10.1029/2024GL110359'),
    ('Agarwal, A., Shah, D., Shen, D. (2026). Synthetic interventions: extending synthetic controls to multiple treatments. '
     'Operations Research 74(2), 840–859.', 'https://doi.org/10.1287/opre.2025.1590'),
    ('Alaa, A. M., Ahmad, Z., van der Laan, M. (2023). Conformal meta-learners for predictive inference of individual '
     'treatment effects. Advances in Neural Information Processing Systems 36.',
     'https://proceedings.neurips.cc/paper_files/paper/2023/hash/94ab02a30b0e4a692a42ccd0b4c55399-Abstract-Conference.html'),
    ('Angelopoulos, A. N., Bates, S., Fisch, A., Lei, L., Schuster, T. (2024). Conformal risk control. 12th International '
     'Conference on Learning Representations (ICLR 2024).', 'https://arxiv.org/abs/2208.02814'),
    ('Aolaritei, L., Wang, Z. O., Zhu, J., Jordan, M. I., Marzouk, Y. (2025). Conformal prediction under Lévy–Prokhorov '
     'distribution shifts: robustness to local and global perturbations. Advances in Neural Information Processing '
     'Systems 38.', 'https://arxiv.org/abs/2502.14105'),
    ('Befus, K. M., Barnard, P. L., Hoover, D. J., Finzi Hart, J. A., Voss, C. I. (2020). Increasing threat of coastal '
     'groundwater hazards from sea-level rise in California. Nature Climate Change 10(10), 946–952.',
     'https://doi.org/10.1038/s41558-020-0874-1'),
    ('Bica, I., Alaa, A. M., van der Schaar, M. (2020). Time Series Deconfounder: estimating treatment effects over time in '
     'the presence of hidden confounders. Proceedings of the 37th International Conference on Machine Learning, PMLR 119.',
     'https://proceedings.mlr.press/v119/bica20a.html'),
    ('Coulon, C., White, J. T., Pryet, A., Gatel, L., Lemieux, J.-M. (2024). An ensemble-based approach for pumping '
     'optimization in an island aquifer considering parameter, observation and climate uncertainty. Hydrology and Earth '
     'System Sciences 28(1), 303–319.', 'https://doi.org/10.5194/hess-28-303-2024'),
    ('Dhillon, G. S., Deligiannidis, G., Rainforth, T. (2024). On the expected size of conformal prediction sets. '
     'Proceedings of AISTATS 2024, PMLR 238, 1549–1557.', 'https://proceedings.mlr.press/v238/dhillon24a.html'),
    ('Feldman, S., Ringel, L., Bates, S., Romano, Y. (2023). Achieving risk control in online learning settings. '
     'Transactions on Machine Learning Research.', 'https://arxiv.org/abs/2205.09095'),
    ('Fukumori, I., Wang, O., Fenty, I. (2021). Causal mechanisms of sea level and freshwater content change in the Beaufort '
     'Sea. Journal of Physical Oceanography 51, 3217–3234.', 'https://doi.org/10.1175/jpo-d-21-0069.1'),
    ('Gibbs, I., Candès, E. J. (2024). Conformal inference for online prediction with arbitrary distribution shifts. Journal '
     'of Machine Learning Research 25(162), 1–36.', None),
    ('Jasechko, S., Perrone, D., Seybold, H., Fan, Y., Kirchner, J. W. (2020). Groundwater level observations in 250,000 '
     'coastal US wells reveal scope of potential seawater intrusion. Nature Communications 11, 3229.',
     'https://doi.org/10.1038/s41467-020-17038-2'),
    ('Jiang, S., Liu, C., Dwivedi, D. (2025). GeoFUSE: an efficient surrogate model for seawater intrusion prediction and '
     'uncertainty reduction. Water Resources Research 61(9), e2024WR038898.', 'https://doi.org/10.1029/2024WR038898'),
    ('Ma, Z., Pitt, D., Azizzadenesheli, K., Anandkumar, A. (2024). Calibrated uncertainty quantification for operator '
     'learning via conformal prediction. Transactions on Machine Learning Research.',
     'https://openreview.net/forum?id=cGpegxy12T'),
    ('Mastouri, A., Zhu, Y., Gultchin, L., Korba, A., Silva, R., Kusner, M., Gretton, A., Muandet, K. (2021). Proximal causal '
     'learning with kernels: two-stage estimation and moment restriction. Proceedings of the 38th International Conference '
     'on Machine Learning, PMLR 139, 7512–7523.', 'https://proceedings.mlr.press/v139/mastouri21a.html'),
    ('Mavroulis, S., Lekkas, E., Carydis, P. (2021). Liquefaction phenomena induced by the 26 November 2019, Mw = 6.4 Durrës '
     '(Albania) earthquake and liquefaction susceptibility assessment in the affected area. Geosciences 11(5), 215.',
     'https://doi.org/10.3390/geosciences11050215'),
    ('Métois, M., Benjelloun, M., Lasserre, C., Grandin, R., Barrier, L., Dushi, E., Koçi, R. (2020). Subsidence associated '
     'with oil extraction, measured from time series analysis of Sentinel-1 data: case study of the Patos-Marinza oil field, '
     'Albania. Solid Earth 11, 363–378.', 'https://doi.org/10.5194/se-11-363-2020'),
    ('McKay, A., Wolf, C. K. (2023). What can time-series regressions tell us about policy counterfactuals? Econometrica '
     '91(5), 1695–1725.', 'https://doi.org/10.3982/ECTA21045'),
    ('Meray, A. O., Sturla, S., Siddiquee, M. R., Serata, R., Uhlemann, S., et al. (2022). PyLEnM: a machine learning '
     'framework for long-term groundwater contamination monitoring strategies. Environmental Science & Technology 56(9), '
     '5973–5983.', 'https://doi.org/10.1021/acs.est.1c07440'),
    ('Ohenhen, L. O., Shirzaei, M., Ojha, C., Kirwan, M. L. (2023). Hidden vulnerability of US Atlantic coast to sea-level '
     'rise due to vertical land motion. Nature Communications 14, 2038.', 'https://doi.org/10.1038/s41467-023-37853-7'),
    ('Pasche, O. C., Lam, H., Engelke, S. (2026). Extreme conformal prediction: reliable intervals for high-impact events. '
     'Extremes 29(2), 129–155.', 'https://doi.org/10.1007/s10687-026-00536-9'),
    ('Ramdas, A., Grünwald, P., Vovk, V., Shafer, G. (2023). Game-theoretic statistics and safe anytime-valid inference. '
     'Statistical Science 38(4), 576–601.', 'https://doi.org/10.1214/23-STS894'),
    ('Singh, R., Xu, L., Gretton, A. (2024). Kernel methods for causal functions: dose, heterogeneous and incremental '
     'response curves. Biometrika 111(2), 497–516.', 'https://doi.org/10.1093/biomet/asad042'),
    ('Soylu, M. E., Entekhabi, D., Bras, R. L. (2026). Integrating satellite retrievals, numerical models, and machine '
     'learning for global groundwater recharge estimation. Water Resources Research 62(3), e2025WR040312.',
     'https://doi.org/10.1029/2025WR040312'),
    ('Yao, J., Mammadov, A., Berner, J., Kerrigan, G., Ye, J. C., Azizzadenesheli, K., Anandkumar, A. (2025). Guided '
     'diffusion sampling on function spaces with applications to PDEs. Advances in Neural Information Processing Systems '
     '38 (NeurIPS 2025).', 'https://arxiv.org/abs/2505.17004'),
    ('Zheng, H., Chu, W., Wang, A., Kovachki, N., Baptista, R., Yue, Y. (2025). Ensemble Kalman diffusion guidance: a '
     'derivative-free method for inverse problems. Transactions on Machine Learning Research.',
     'https://arxiv.org/abs/2409.20175'),
    ('Alexanderian, A. (2021). Optimal experimental design for infinite-dimensional Bayesian inverse problems governed by '
     'PDEs: a review. Inverse Problems 37(4), 043001.', 'https://doi.org/10.1088/1361-6420/abe10c'),
    ('Attia, A., Constantinescu, E. (2022). Optimal experimental design for inverse problems in the presence of '
     'observation correlations. SIAM Journal on Scientific Computing 44(4), A2808–A2842.',
     'https://doi.org/10.1137/21M1418666'),
    ('Attia, A., Leyffer, S., Munson, T. (2023). Robust A-optimal experimental design for Bayesian inverse problems. '
     'arXiv:2305.03855.', 'https://arxiv.org/abs/2305.03855'),
    ('Chowdhary, A., Attia, A., Alexanderian, A. (2025). Robust optimal experimental design of infinite-dimensional '
     'Bayesian nonlinear inverse problems. arXiv:2409.09137.', 'https://arxiv.org/abs/2409.09137'),
    ('Krause, A., Singh, A., Guestrin, C. (2008). Near-optimal sensor placements in Gaussian processes: theory, efficient '
     'algorithms and empirical studies. Journal of Machine Learning Research 9, 235–284.',
     'https://jmlr.org/papers/v9/krause08a.html'),
    ('Liu, S., Chepuri, S. P., Fardad, M., Maşazade, E., Leus, G., Varshney, P. K. (2016). Sensor selection for estimation '
     'with correlated measurement noise. IEEE Transactions on Signal Processing 64(13), 3509–3522.',
     'https://doi.org/10.1109/TSP.2016.2550005'),
    ('Maio, S., Alexanderian, A., Koval, K., Nicholson, R. (2026). Multi-type sensor placement for PDE-based Bayesian '
     'inverse problems. arXiv:2607.08074.', 'https://arxiv.org/abs/2607.08074'),
    ('Rasmussen, T. C., Crawford, L. A. (1997). Identifying and removing barometric pressure effects in confined and '
     'unconfined aquifers. Ground Water 35(3), 502–511.', 'https://doi.org/10.1111/j.1745-6584.1997.tb00111.x'),
    ('Toll, N. J., Rasmussen, T. C. (2007). Removal of barometric pressure effects and earth tides from observed water '
     'levels. Ground Water 45(1), 101–105.', 'https://doi.org/10.1111/j.1745-6584.2006.00254.x'),
    ('Uciński, D. (2020). D-optimal sensor selection in the presence of correlated measurement noise. Measurement 164, '
     '107873.', 'https://doi.org/10.1016/j.measurement.2020.107873'),
    ('Venkat, S., Henneking, S., Ghattas, O. (2026). Sensor placement for tsunami early warning via large-scale Bayesian '
     'optimal experimental design. arXiv:2604.08812.', 'https://arxiv.org/abs/2604.08812'),
    ('Wu, K., Chen, P., Ghattas, O. (2023). A fast and scalable computational framework for large-scale high-dimensional '
     'Bayesian optimal experimental design. SIAM/ASA Journal on Uncertainty Quantification 11(1), 235–261.',
     'https://doi.org/10.1137/21M1466499'),
]
SOTA_REFS += [
    ('Beiglböck, M., Henry-Labordère, P., Penkner, F. (2013). Model-independent bounds for option prices—a mass transport '
     'approach. Finance and Stochastics 17(3), 477–501.', 'https://doi.org/10.1007/s00780-013-0205-8'),
    ('Gierjatowicz, P., Sabate-Vidales, M., Šiška, D., Szpruch, L., Žurič, Ž. (2020). Robust pricing and hedging via '
     'neural SDEs. Working paper, SSRN 3646241.', 'https://ssrn.com/abstract=3646241'),
    ('Herrera, C., Krach, F., Teichmann, J. (2021). Neural jump ordinary differential equations: consistent '
     'continuous-time prediction and filtering. International Conference on Learning Representations (ICLR 2021).',
     'https://arxiv.org/abs/2006.04727'),
    ('Hobson, D. G. (1998). Robust hedging of the lookback option. Finance and Stochastics 2(4), 329–347.',
     'https://doi.org/10.1007/s007800050044'),
    ('Krach, F., Nübel, M., Teichmann, J. (2026). Optimal estimation of generic dynamics by path-dependent neural jump '
     'ODEs. Stochastic Processes and their Applications.', 'https://doi.org/10.1016/j.spa.2026.105058'),
    ('Slepian, D. (1962). The one-sided barrier problem for Gaussian noise. Bell System Technical Journal 41(2), 463–501.',
     'https://doi.org/10.1002/j.1538-7305.1962.tb02419.x'),
]
SOTA_REFS += [  # decisions when the source of the chloride is unknown (State of the art V, PREJARDHJA-GO)
    ('Entekhabi, D. (2023). Propagation in the drought cascade: observational analysis over the continental US. Water Resources Research 59(9), e2022WR032608.',
     'https://doi.org/10.1029/2022WR032608'),
    ('Farahmand, A., Reager, J. T., Madani, N. (2021). Drought cascade in the terrestrial water cycle: evidence from remote sensing. Geophysical Research Letters 48(14), e2021GL093482.',
     'https://doi.org/10.1029/2021GL093482'),
    ('Herman, J. D., Quinn, J. D., Steinschneider, S., Giuliani, M., Fletcher, S. (2020). Climate adaptation as a control problem: review and perspectives on dynamic water resources planning under uncertainty. Water Resources Research 56(2), e24389.',
     'https://doi.org/10.1029/2019WR025502'),
    ("Jedd, T., Sixt, G. N., Schutz, A., Burbach, M. (2024). Legitimacy in polycentric groundwater governance: framework conditions identified in Nebraska's Natural Resources Districts. Environmental Policy and Governance 35(2), 187–200.",
     'https://doi.org/10.1002/eet.2132'),
    ('Perri, S., Suweis, S., Holmes, A., Marpu, P. R., Entekhabi, D., Molini, A. (2020). River basin salinization as a form of aridity. Proceedings of the National Academy of Sciences 117(30), 17635–17642.',
     'https://doi.org/10.1073/pnas.2005925117'),
    ('Roman, O., Hoque, S. F., Ford, L., Salehin, M., Alam, M. M., Hope, R., Hall, J. W. (2021). Optimizing rural drinking water supply infrastructure to account for spatial variations in groundwater quality and household welfare in coastal Bangladesh. Water Resources Research 57(8), e2021WR029621.',
     'https://doi.org/10.1029/2021WR029621'),
    ('Vovk, V., Wang, R. (2021). E-values: calibration, combination and applications. The Annals of Statistics 49(3), 1736–1754.',
     'https://doi.org/10.1214/20-AOS2020'),
    ('Wang, K., Aydemir, M., Jacquillat, A. (2024). Scenario-based robust optimization for two-stage decision making under binary uncertainty. INFORMS Journal on Optimization 6(2), 84–117.',
     'https://doi.org/10.1287/ijoo.2020.0038'),
    ('Wasserman, L., Ramdas, A., Balakrishnan, S. (2020). Universal inference. Proceedings of the National Academy of Sciences 117(29), 16880–16890.',
     'https://doi.org/10.1073/pnas.1922664117'),
]
SOTA_REFS += [  # the boundary where a model is cut (PERTEJ-GO theory note); all checked in Crossref, 9 November 2026
    ('Alpert, B., Greengard, L., Hagstrom, T. (2000). Rapid evaluation of nonreflecting boundary kernels for time-domain wave propagation. SIAM Journal on Numerical Analysis 37(4), 1138–1164.',
     'https://doi.org/10.1137/S0036142998336916'),
    ('Bakker, M., Schaars, F. (2019). Solving groundwater flow problems with time series analysis: you may not even need another model. Groundwater 57(6), 826–833.',
     'https://doi.org/10.1111/gwat.12927'),
    ('Engquist, B., Majda, A. (1977). Absorbing boundary conditions for the numerical simulation of waves. Mathematics of Computation 31(139), 629–651.',
     'https://doi.org/10.1090/S0025-5718-1977-0436612-4'),
    ('Gustavsen, B., Semlyen, A. (2001). Enforcing passivity for admittance matrices approximated by rational functions. IEEE Transactions on Power Systems 16(1), 97–104.',
     'https://doi.org/10.1109/59.910786'),
    ('Langevin, C. D., Hughes, J. D., Banta, E. R., Niswonger, R. G., Panday, S., Provost, A. M. (2017). Documentation for the MODFLOW 6 Groundwater Flow Model. U.S. Geological Survey Techniques and Methods 6-A55.',
     'https://doi.org/10.3133/tm6A55'),
    ('Michael, H. A., Russoniello, C. J., Byron, L. A. (2013). Global assessment of vulnerability to sea-level rise in topography-limited and recharge-limited coastal groundwater systems. Water Resources Research 49(4), 2228–2240.',
     'https://doi.org/10.1002/wrcr.20213'),
    ('von Asmuth, J. R., Bierkens, M. F. P., Maas, K. (2002). Transfer function-noise modeling in continuous time using predefined impulse response functions. Water Resources Research 38(12), 1287.',
     'https://doi.org/10.1029/2001WR001136'),
    ('Werner, A. D., Simmons, C. T. (2009). Impact of sea-level rise on sea water intrusion in coastal aquifers. Ground Water 47(2), 197–204.',
     'https://doi.org/10.1111/j.1745-6584.2008.00535.x'),
]
SOTA_REFS += [  # earthquakes in coastal aquifers (TRONDITJA-GO report); all checked in Crossref, 9 November 2026
    ('Boulanger, R. W., Idriss, I. M. (2016). CPT-based liquefaction triggering procedure. Journal of Geotechnical and Geoenvironmental Engineering 142(2), 04015065.',
     'https://doi.org/10.1061/(asce)gt.1943-5606.0001388'),
    ('Ganas, A., Elias, P., Briole, P., et al. (2020). Ground deformation and seismic fault model of the M6.4 Durres (Albania) Nov. 26, 2019 earthquake, based on GNSS/InSAR observations. Geosciences 10(6), 210.',
     'https://doi.org/10.3390/geosciences10060210'),
    ('Govorčin, M., Wdowinski, S., Matoš, B., Funning, G. J. (2020). Geodetic source modeling of the 2019 Mw 6.3 Durrës, Albania, earthquake: partial rupture of a blind reverse fault. Geophysical Research Letters 47(22), e2020GL088990.',
     'https://doi.org/10.1029/2020GL088990'),
    ('Matraku, K., Jouanne, F., Dushi, E., et al. (2023). The 26 November 2019 Durrës earthquake, Albania: coseismic displacements and occurrence of slow slip events in the year following the earthquake. Geophysical Journal International 234(2), 807–838.',
     'https://doi.org/10.1093/gji/ggad101'),
    ('Maurer, B. W., Green, R. A., Cubrinovski, M., et al. (2014). Evaluation of the liquefaction potential index for assessing liquefaction hazard in Christchurch, New Zealand. Journal of Geotechnical and Geoenvironmental Engineering 140(7), 04014032.',
     'https://doi.org/10.1061/(asce)gt.1943-5606.0001117'),
    ('Okada, Y. (1985). Surface deformation due to shear and tensile faults in a half-space. Bulletin of the Seismological Society of America 75(4), 1135–1154.',
     'https://doi.org/10.1785/BSSA0750041135'),
    ('van der Heiden, V., Schurr, B., Woollam, J., et al. (2026). Analysis of the 2019 Mw 6.4 Durrës, Albania, aftershock sequence: basement involved thrusting at the eastern Adriatic plate margin. Geophysical Journal International 246(2), ggag155.',
     'https://doi.org/10.1093/gji/ggag155'),
    ('Wang, C.-Y., Chia, Y. (2008). Mechanism of water level changes during earthquakes: near field versus intermediate field. Geophysical Research Letters 35(12).',
     'https://doi.org/10.1029/2008GL034227'),
]
SOTA_REFS.sort(key=lambda r: r[0].lower())

SOTA_TEXT = (
    'Related research outside the project team (2020–2026):\n'
    '• Coastal groundwater under climate change and pumping. Rising sea level lifts the water table and extends '
    'flooding inland (Befus et al., 2020); 250,000 US coastal wells show where heads lie below sea level (Jasechko et '
    'al., 2020); by 2100 recharge sets the severity of intrusion and sea level its prevalence (Adams et al., 2024); '
    'ensemble pumping optimisation handles parameter and climate uncertainty (Coulon et al., 2024); machine-learned '
    'surrogates predict intrusion fast (Jiang, Liu and Dwivedi, 2025). These give scenarios without guarantees and '
    'treat pumping as known and exogenous.\n'
    '• Inputs and boundaries from sparse data. Ensemble and diffusion-based inversion (Zheng et al., 2025; Yao et al., '
    '2025), satellite and machine-learning recharge (Soylu, Entekhabi and Bras, 2026) and evaluations of gridded rain '
    'products (Abbas et al., 2026) estimate what is not measured, without a calibrated guarantee and without carrying '
    'the rain-product errors into the boundaries.\n'
    '• Guarantees for forecasts and surrogates. Conformal risk control (Angelopoulos et al., 2024), online calibration '
    'under shift (Gibbs and Candès, 2024; Feldman et al., 2023), robustness to distribution shift (Aolaritei et al., '
    '2025), conformal neural operators (Ma et al., 2024), extreme conformal prediction (Pasche, Lam and Engelke, '
    '2026), the expected size of conformal sets (Dhillon, Deligiannidis and Rainforth, 2024) and anytime-valid '
    'inference (Ramdas et al., 2023) all calibrate on observed outcomes; none covers a boundary that is never '
    'observed, asks how narrow such a guarantee can be, or how long it holds under drift.\n'
    '• Monitoring design. Bayesian optimal design places sensors for PDE-governed inverse problems (Alexanderian, '
    '2021; Wu, Chen and Ghattas, 2023); greedy selection is near-optimal for submodular criteria (Krause, Singh and '
    'Guestrin, 2008), which correlated errors break (Liu et al., 2016; Uciński, 2020; Attia and Constantinescu, 2022); '
    'robust designs maximise the worst case over an uncertain error model (Attia, Leyffer and Munson, 2023; Chowdhary, '
    'Attia and Alexanderian, 2025); recent work places several sensor types (Maio et al., 2026), designs tsunami '
    'warning networks (Venkat, Henneking and Ghattas, 2026) or ranks wells by predictive skill (Meray et al., 2022). '
    'None values a sensor by the guaranteed band it removes or the years of safe operation it adds, or certifies a '
    "robust network's distance from the best one; all take correlated errors as given, although air pressure and "
    'logger drift are routinely removed with a nearby barometer (Rasmussen and Crawford, 1997; Toll and Rasmussen, '
    '2007), outside the design.\n'
    '• Forecasting from irregular records and robust bounds. Neural jump ODEs learn the optimal online forecast from '
    'irregular, incomplete records (Herrera, Krach and Teichmann, 2021; Krach, Nübel and Teichmann, 2026); robust '
    'finance bounds a path-dependent price over all models that fit the liquid prices (Hobson, 1998; Beiglböck, '
    'Henry-Labordère and Penkner, 2013), computed with neural SDEs (Gierjatowicz et al., 2020). Neither gives a '
    'finite-record guarantee or names the observation that would narrow the bound. Yet sampling pins the marginal law '
    'of chloride, not its time scale, so a crossing of the limit between samples is bounded only from below (Slepian, '
    '1962).\n'
    '• Hidden confounding over time. The Time Series Deconfounder infers substitutes for hidden confounders from many '
    'treatments (Bica, Alaa and van der Schaar, 2020); proxy methods (Mastouri et al., 2021), synthetic interventions '
    '(Agarwal, Shah and Shen, 2026), conformal intervals for individual effects (Alaa, Ahmad and van der Laan, 2023), '
    'policy counterfactuals (McKay and Wolf, 2023), causal dose curves (Singh, Xu and Gretton, 2024) and adjoint '
    'attribution in the ocean (Fukumori, Wang and Fenty, 2021) complete the picture. Substitutes built from the '
    'treatments cannot see the fresh news of a confounder such as a heat wave that makes every farmer pump, and none '
    'uses a physical measurement of the confounding path.\n'
    '• Decisions when the cause of the salt is unknown. Drought propagates into groundwater with measurable lags '
    '(Farahmand, Reager and Madani, 2021; Entekhabi, 2023); salinisation acts as an aridity enhancer (Perri et al., '
    '2020); water planning is framed as a control problem under deep uncertainty (Herman et al., 2020); drinking-water '
    'investment on a salinised coast trades total access against access for the poorest (Roman et al., 2021); '
    'scenario-based robust optimisation protects against discrete uncertainty (Wang, Aydemir and Jacquillat, 2024); '
    'legitimacy decides whether groundwater users accept limits (Jedd et al., 2024). None decides before the source of '
    'rising chloride is known with a risk stated for every source, although e-values (Vovk and Wang, 2021) and '
    'universal inference (Wasserman, Ramdas and Balakrishnan, 2020) give the tools.\n'
    '• The boundary where a model is cut. Groundwater models end inland at a fixed head, a prescribed flux or a '
    'general-head boundary (Langevin et al., 2017), and this choice decides how intrusion responds to sea-level rise '
    '(Werner and Simmons, 2009; Michael, Russoniello and Byron, 2013). Exact boundaries built from sums of exponentials '
    'are classical for waves (Engquist and Majda, 1977; Alpert, Greengard and Hagstrom, 2000); passive rational models '
    'of an external network are standard in power systems (Gustavsen and Semlyen, 2001); head time series are modelled '
    'with positive impulse responses (von Asmuth, Bierkens and Maas, 2002; Bakker and Schaars, 2019). None learns the '
    'boundary of a groundwater model from data with its stability and identifiability guaranteed.\n'
    '• Earthquakes in coastal aquifers. Fault models give the static strain near the source (Okada, 1985); undrained '
    'volumetric change explains abrupt water-level changes near the source, and earthquake-enhanced permeability the '
    'sustained ones farther away (Wang and Chia, 2008). The 2019 Durrës earthquake has four published source models '
    '(Ganas et al., 2020; Govorčin et al., 2020; Matraku et al., 2023; van der Heiden et al., 2026). CPT-based '
    'triggering (Boulanger and Idriss, 2016) and the liquefaction potential index (Maurer et al., 2014) take the water '
    'table as given. None decides which layer of a soft coastal plain feels the static step, or reads the leakage of a '
    'confined aquifer from the relaxation of that step.\n'
    '• Vertical land motion and coastal exposure from InSAR and GNSS (Ohenhen et al., 2023), and slow settling of the '
    'Albanian coastal plain near Fier (Métois et al., 2020); the 2019 Durrës earthquake and its liquefaction '
    '(Mavroulis, Lekkas and Carydis, 2021).\n'
    'What none of these does. No study combines intrusion, liquefaction and extreme water levels in one model with '
    'warnings whose miss rate is stated in advance; guarantees the inputs known only through rain when the simulator '
    'is wrong; values a sensor by the guaranteed band it removes and the years it adds; places the reference channels '
    'that correct the sensors; certifies crossings between samples; reads the hidden drought demand from the heads; '
    'decides how to pump before the source of the salt is known; learns the inland boundary of the model from data '
    'without putting its stability at risk; tells which layer an earthquake loads; or computes when a safe way of '
    'operating the assets ends. A final check in bibliographic databases will be made before submission.\n'
    'Related activities of the project participants: [list proposed, ongoing or recently completed projects of the '
    'Co-Directors on related topics, with dates and budgets, or write "none"]. The preparatory technical work of the '
    "NPD's team in 2026 (eleven reviews with tests, a calibrated chloride model of the Fushë-Kuqe aquifer) is the "
    'starting point of the project, not a separately funded activity.\n'
    'Other activities at the site known to the applicants: [list any national, EU or donor projects on subsidence, the '
    'port or the water supply of Durrës, or write "none known"].\n'
    'What makes CERTAIN-COAST stand out: one model for three hazards at three critical assets, warnings and pumping '
    'decisions whose error is stated in advance and verified in operation, and a certified planning horizon for the '
    'operators.')


def _ref_line(t, u):
    return t + (' ' + u if u else '')


SOTA = SOTA_TEXT + '\nReferences:\n' + '\n'.join(_ref_line(t, u) for t, u in SOTA_REFS)


ABSTRACT = (
    'On Albania\'s Adriatic coast, the drinking-water wells and port of Durrës and the landfall of a gas pipeline to Italy '
    'near Fier stand on low ground, which at Durrës is sinking, close to active faults. Three dangers threaten them: seawater '
    'entering the wells, ground that turns almost liquid in an earthquake, and the sea flooding the land in storms. The '
    'dangers are linked, because sinking land and rising seas worsen all three and pumping that protects against one can '
    'increase another, but today they are watched separately and no warning says how often it can be wrong.\n'
    'CERTAIN-COAST will watch them together. Satellites, GNSS and new ground sensors will feed one computer model of the '
    'coast, copied by a fast artificial-intelligence model whose error is stated for every forecast. Each warning will state '
    'in advance how often it may miss a dangerous event, and this will be checked in twelve months of live operation with the '
    'water utility, the water agency, the port, the pipeline operator and civil protection. The project will show how many '
    'years a safe way of operating the three assets remains, and sharpen that estimate with safe pumping tests. Local '
    'operators will run the system afterwards.')

RELEVANCE = (
    'Link to security. The project protects three essential services of a NATO Ally (drinking water, a port that '
    "handles most of the country's seaborne freight, and the landfall of the Trans Adriatic Pipeline near Fier) and "
    "serves three of NATO's seven baseline requirements for national resilience: resilient food and water resources, "
    'resilient civil transportation systems and resilient energy supplies, which also underpin civil support to the '
    'military. It falls under the 2027-1 topic "protection of critical infrastructure, supplies and personnel; '
    'maritime and undersea infrastructure resilience": the TAP landfall is where an undersea gas pipeline between two '
    'Allies, Albania and Italy, leaves the shore.\n'
    'Use cases:\n'
    '• Water utility: cut or shift pumping before chloride reaches drinking-water wells (weeks to months ahead), '
    'safely even while the source of the chloride is unknown.\n'
    '• Water Resources Management Agency (AMBU): use the monitoring design, the chloride early warning for each supply '
    'well and the pumping and drought rule in its monitoring and in support of water-use permits for the aquifer.\n'
    '• Port authority: restrict loads or operations and set inspection priorities after an earthquake; prepare for '
    'storm surges (hours to days ahead).\n'
    '• Pipeline operator (TAP): inspect, protect or isolate the landfall near Fier when the ground or the water level '
    'threatens it.\n'
    '• Civil protection: one consistent bulletin for water, port and energy after an earthquake or a storm.\n'
    '• National authorities and resilience planners: the certified year from which no operating plan keeps the three '
    'assets safe together, and the sensors and measures that delay it most.\n'
    'Each bulletin states its certified miss rate, so decision-makers know how far it can be trusted. The method uses '
    'free satellite data and transfers to other subsiding coasts of Allies and partners with wellfields, ports and '
    'energy landfalls.')

STATUS = (
    "The approach has been tested in preparatory work by the NPD's team (2026), on synthetic coastal aquifers and on "
    'the calibrated chloride model of the Fushë-Kuqe aquifer, which supplies Durrës:\n'
    '• Boundaries known only through rain: on 500 simulated aquifers with four loggers, the raw ensemble missed 17–20% '
    'of the weeks; the calibrated bands met the 10% target (0.095–0.100).\n'
    '• A wrong simulator: bands calibrated on simulations broke under a 35-day vadose delay, shifted parameters or a '
    'rain bias (risk 0.11–0.83); calibrated on 10–40 measured anchors they stayed at or below 10% under every law '
    'tested. At least 9 anchors are needed for an average guarantee and 22 for a 90% certificate.\n'
    '• Drift: horizon-matched bands kept the risk at 0.003–0.082 up to 20 years ahead under every drift tested; with '
    '30 anchor years a band exists only up to 17 years ahead.\n'
    '• The rain product and the floor: a local gauge with one logger identified the recharge coefficient better (error '
    '0.045) than the product with eight loggers (0.108); with 20 anchors the guaranteed band was 1.34–1.54 times the '
    'narrowest possible.\n'
    '• Value of a sensor: a tide gauge that a standard ensemble said would narrow the recharge band by 15% widened the '
    'guaranteed band by 16–21%; the sign of each guaranteed value was predicted for 36 of 36 instrument–goal pairs.\n'
    '• Counterfactual salinity at Fushë-Kuqe (calibrated model): with 40% less recharge the shallow area above 250 '
    'mg/L chloride would grow from 31 to 65 km² (effect +33 km², conformal band 15–49 km²), with coverage 0.887–0.900 '
    'on 300 simulated test sets.\n'
    '• Pumping and hidden drought demand: in a test bed with eight wells, the summed effect of pumping on salinity '
    '(true value 0.94) was overstated by 0.59 without adjustment, by 0.56 with a substitute built from the pumping '
    'history (as in the Time Series Deconfounder) and by 0.00 with the recharge read from the heads; the physics check '
    'had size 6% and power 99–100%.\n'
    '• Alarms and operating window: an alarm with an extreme-aware margin kept the share of seasons above the chloride '
    'limit at 4–9% across storylines, where a static alarm allowed 13–21%; the certified safe operating window closed '
    'after 38 years, while plans that watch one hazard believed they had 43–97 years; safe pumping tests chosen for '
    'the years they add raised the certified closing year from 10.8 to 31.9 years (true value 45) with chloride below '
    '123 mg/L in 95% of runs; the anytime-valid test wrongly flagged a correctly calibrated alarm in 2.2% of runs, '
    'against 68% for re-checking a 95% bound after every event.\n'
    '• Sensors that interfere: a 12-sensor network with a barometer and hub reference channels kept 52% more '
    'worst-case information than the classical design, certified within 18% of the best; ignoring the interference let '
    '90% intervals cover only 49–62% of cases, the correction 88–93%.\n'
    '• Crossings between samples: chloride with an 8-day time scale crossed 250 mg/L within a season with probability '
    '0.78, 34 times the exceedance on a sampling date; quarterly samples left this anywhere in 0.18–1, a daily logger '
    'in 0.76–0.80; a conformal margin restored 90.3% coverage for skewed chloride (74% without).\n'
    "• Unknown source of the chloride: four rival sources (seawater, deep brine, drought, return flow) fitted today's "
    'chloride equally well; acting on the wrong one let the blend exceed 250 mg/L with probability up to 100% (98% '
    'when seawater intrusion was assumed); keeping only the sources the tracers could not exclude, and protecting '
    'against all of them, held every source at or below 6.9% against a 10% budget, at €3.31 million against €4.16 '
    'million for protecting against all four; monthly updates dropped the true source in 1.2–1.5% of cases, against '
    'about 22% for an ordinary test repeated every month.\n'
    '• Boundary of the model: on a 10 km test aquifer cut at 2 km, a boundary of six positive storage compartments '
    'reproduced the head at the cut to 7.8 mm over 20 years, against 148 mm for the best calibrated general-head '
    'boundary; learned from two piezometers while the pumping varied, it predicted an unseen drought with doubled '
    'pumping to 6 mm (general-head boundary: 372 mm); under a 0.5 m sea-level rise it lost 160 m³ of fresh water per '
    'metre of coast against 154 in the full aquifer, where a prescribed inflow gave 49 and a fixed head 462; a '
    'negative conductance that was stable at 2 km grew without bound at 6 km.\n'
    '• Earthquake in the aquifer: with four published source models of the 2019 earthquake, the static pore-pressure '
    'step was 7–12 cm of head in soft surface sand and 0.6–1.0 m in a stiffer confined aquifer, where the usual '
    'estimate gives 35 times the soft-sand value; for liquefaction the water table of the day dominates (in an example '
    'profile the liquefaction potential index fell from 20.2 to 9.3 as the water table deepened from 0.8 to 2.6 m). '
    'After a 0.3 m step, 20 days of logger data pinned the leakage time of the confined aquifer 5.8 times more sharply '
    'than a year of seasonal heads; a hindcast of the 2019 liquefaction map had a power below 50% even with 480 sites. '
    'At a synthetic port the window between liquefaction and intrusion closed at 0.29 m of sea-level rise for a design '
    'acceleration of 0.20 g, and the chance of an index above 5 if the earthquake struck that day moved between 0.16 '
    'and 0.26 over the year.\n'
    'These are tests on synthetic coasts and on the existing chloride model with illustrative values, not results at '
    'Durrës; the project calibrates and verifies them on site.\n'
    'Starting data: Sentinel-1 radar images since 2014, tide-gauge records, the wells and chemical records of the '
    'water utility, and the mapped liquefaction of the 2019 earthquake (Mavroulis et al., 2021).\n'
    "Team: [summarise the Co-Directors' prior research on seawater intrusion, coastal geodesy, geotechnics and "
    'statistics, with 3–5 key publications].')


IMPACT = (
    'If the project succeeds, the following will change at Durrës, at the TAP landfall near Fier and beyond:\n'
    '• Three hazards covered by one warning with a stated miss rate, where today there is none: seawater intrusion at '
    'the wellfields, liquefaction at the port and the landfall, and extreme water levels at all three.\n'
    '• Each alarm misses dangerous events no more often than its certified rate (indicatively 5–10%), shown by '
    'back-testing over the record since 2014 and checked in twelve months of live operation; the joint miss rate for '
    'the three assets is bounded by the sum of the rates.\n'
    '• Each operator knows in advance the minimum value of the warning for its own decisions, computed from the '
    'certified miss rate and the cost-loss ratio agreed with it.\n'
    '• The water utility operates its wells within a certified safe window, sharpened by safe pumping tests on its own '
    'wells, which lowers the risk of salinising wells that take years to recover and avoids new permanent subsidence; '
    'planners know when the window closes and which measures extend it.\n'
    '• The Water Resources Management Agency (AMBU) gains a monitoring design for its decisions and a chloride early '
    'warning for each supply well, in support of its water-use permits for the aquifer that supplies Durrës, with no '
    'procurement, ownership or maintenance obligations.\n'
    '• The water utility, AMBU, the farmers and the regulator can act before the source of rising chloride is known: '
    'tracers are bought for the decision they change, the plausible sources and the pumping in force are published '
    'every month with a risk that holds whatever the source, and a ledger shows who bears the cost.\n'
    '• Models whose inland edge responds as the real aquifer does, learned from piezometers: sea-level rise and new '
    'pumping are then neither underestimated by a prescribed inflow nor overstated by a fixed head (in tests, by a '
    'factor of three either way).\n'
    '• After an earthquake, the operators know which layers\' pressure rose, and the wells measure the aquifer for '
    'free.\n'
    '• At least 20 operator and civil-protection staff (at least two per operator) trained and running the system; at '
    'least six early-career researchers trained in the NATO and partner countries.\n'
    '• A monitoring network of piezometers, GNSS, seismic stations and corner reflectors handed over to the operators, '
    'with a running cost of about €10,900 per year carried by them under a maintenance agreement.\n'
    '• Open software and data with a DOI, installed and reproduced by a group outside the consortium; at least six '
    'open-access papers; operating procedures adopted for each asset; a policy brief for the national authorities.\n'
    '• The method tested on a second coast in the partner country and ready for other subsiding coasts of the Adriatic '
    'and the Mediterranean.\n'
    'For NATO, the result is a tested capability for three baseline requirements of resilience at an Allied site, and '
    'a worked example of artificial intelligence used in a security decision chain with testing, evaluation, '
    'verification and validation built in.')

TRL_TEXT = (
    'Start: TRL 3. Each component has been shown in preparatory synthetic tests (alarm margins, safe operating window, '
    'verification, guaranteed reconstruction from rain, value of a sensor, pumping effects with the hidden confounding '
    'removed, counterfactual salinity on the calibrated chloride model of Fushë-Kuqe, a network that corrects its own '
    'sensors, warnings for crossings between samples, decisions before the source of the chloride is known, an inland '
    'boundary learned from piezometers, the pore-pressure step of each layer after an earthquake), and '
    'published methods exist for each element.\n'
    'End: TRL 6, as the 2027-1 call asks (results at TRL 3–6). The integrated system (network, coupled model, '
    'certified surrogate, alarms, pumping rule and safe operating window) is demonstrated in its relevant environment, '
    "the operators' own sites, through twelve months of live operation with the water utility, the water resources "
    'agency (AMBU), the port authority, the pipeline operator (TAP) and civil protection, before the operators take it '
    'over. Seismic velocity as a coastal water-table sensor and the pumping rule with its safe pumping tests are '
    'demonstrated at the site but not yet run for a full year.')

DATA = (
    'Data required and existing sources: Copernicus Sentinel-1 radar images since 2014 (free and open); GNSS records; the '
    'Durrës tide-gauge record of the State Authority for Geospatial Information (ASIG); heads, pumping and chloride records of the water utility; groundwater level, chemistry and abstraction records of AMBU; geotechnical records of the port and of '
    'TAP at its landfall; records of existing national seismic stations; meteorological and wave data.\n'
    'New data: continuous heads, conductivity and temperature in new and existing wells; GNSS and corner-reflector time series '
    'at the assets; continuous seismic noise from stations and temporary nodes, and fibre-optic sensing where access is '
    'agreed; laboratory chloride and major ions; the bulletin log with outcomes.\n'
    'Collection and management: a data management plan (D7.1, Month 3) following the FAIR principles; standard formats '
    '(miniSEED and StationXML for seismic data, NetCDF with CF conventions for time series) and DataCite metadata; storage '
    'on the partners\' servers with backup; open release of derived products and software with DOIs on Zenodo.\n'
    'Risks and mitigation: (1) access to operator data: letters of commitment now, signed access agreements by Month 3, and '
    'satellite and public data as a fallback; (2) security of critical-infrastructure information: every output is '
    'classified before release, asset-level vulnerability, thresholds and sensor locations inside sites stay with the '
    'operators and authorities, and open products are aggregated or anonymised; (3) privacy: personal data are limited to '
    'workshop and training participants, collected with informed consent, minimised and pseudonymised under Albania\'s Law '
    'No. 124/2024 on personal data protection, aligned with the GDPR; (4) data quality: quality flags, loggers calibrated '
    'against laboratory chloride, and record errors carried as uncertainty in the model.')

WORKPLAN = (
    'Sequencing: Phase 1, observe and measure (Months 1–12); Phase 2, model and certify (Months 4–30); Phase 3, '
    'operate, verify and hand over (Months 22–36). Gates MS3 (Month 18), MS4 (Month 22) and MS5 (Month 27) decide '
    'whether each next step starts. Every guarantee is checked on simulated test sets and on held-out field data '
    'before it is used.\n'
    'WP1, Coastal motion and relative sea level (Months 1–36; NATO-country team). Steps: Sentinel-1 InSAR time series '
    'since 2014 (T1.1); corner reflectors and GNSS at the assets (T1.2); trajectory model including the 2019 '
    'earthquake and the relative sea level at each asset (T1.3); elastic and inelastic compaction and the head limit '
    'for pumping (T1.4). Risk: loss of radar coherence on soft ground; mitigation: corner reflectors and scatterers on '
    'structures. Milestone: MS2 (Month 12).\n'
    'WP2, One coupled model and its certified fast copy (Months 4–24; NATO-country team). Steps: model set-up for the '
    'two sites, the Durrës wellfields and port and the TAP landfall near Fier, on one coastal motion field (T2.1); '
    'coupling of flow, salt, compaction and liquefaction, with the pore pressure of the day and the earthquake step of '
    'each layer from its shear modulus (T2.2); calibration (T2.3): the rain reaches the aquifer '
    'through a stochastic soil-water and vadose-delay model learned from irregular head records; the inputs and '
    'boundaries nobody measures (recharge coefficient, vadose delay, storage, sea level, inland inflow, initial head, '
    'dispersion width) are reconstructed by a function-space diffusion prior with an ensemble update through the exact '
    'solver; the errors of the rain product are simulated in the prior; bands are calibrated by conformal risk control '
    'on simulated aquifers and checked on measured anchor periods; the inland boundary, where the model is cut, is a '
    'conductance plus positive storage compartments on a fixed grid of time scales, passive by construction, learned '
    'from two piezometers between the wellfields and the cut, with a prior learned from simulated geology; '
    'neural-operator surrogate with a certified error '
    'bound (T2.4). Risk: the model fails validation; mitigation: build in stages and fall back to two-dimensional '
    'sections with a wider error bound. Risk: the anchors are too few (at least 9 are needed for an average guarantee, '
    '22 for a 90% certificate); mitigation: anchors from the record since 2014 and from the new loggers, and a wider '
    'simulation-calibrated band reported as such. Risk: the inland boundary is not identified (pumping too steady, or an '
    'unknown source near the cut); mitigation: changes of pumping rate over months to years agreed with the utility, '
    'the prior from simulated geology, and a general-head boundary with a widened band as fallback. Milestones: MS3 '
    '(Month 18), MS4 (Month 22).\n'
    'WP3, Certified multi-hazard alarm (Months 13–34; NATO-country team). Steps: thresholds and tolerable miss rates '
    'with the operators (T3.1); alarm margins and proofs (T3.2), with anchor calibration so that the guarantee does '
    'not depend on the simulator, horizon matching under drift, and the floor that shows how far each band is from the '
    'narrowest possible, and warnings for crossings between samples: the chance that chloride crosses its limit at any '
    'time in the season, as a band over all models that fit the records, widened by a conformal margin calibrated on '
    'simulated aquifers and anchor periods, and issued online as the conditional probability given the irregular '
    'samples and the daily heads; joint guarantee and allocation of tolerances (T3.3); back-testing (T3.4); '
    'verification in operation (T3.5). Risk: too many false alarms; mitigation: acceptable rates agreed in advance and '
    'tolerances allocated by consequence. Risk: drift faster than the record allows; mitigation: report the longest '
    'horizon for which a band exists. Risk: chloride more skewed than the model family; mitigation: the conformal '
    'margin, re-estimated each season. Milestone: MS5 (Month 27).\n'
    'WP4, Monitoring network designed for the warnings (Months 1–36; NATO-country team). Steps: design (T4.1), in '
    'which each candidate sensor is valued by the guaranteed band it removes, its floor and the years of safe '
    'operation it adds per euro, with a local rain gauge among the candidates and one logger next to the wellfield '
    'most exposed to local demand; the monitoring wells of AMBU (existing wells only) are candidate sites and the '
    "design also serves AMBU's monitoring decisions; a barometer and a sealed reference channel on each logger hub are "
    'candidates too, the error model carries the barometric efficiency of each well, the drift of each logger, cable '
    'cross-talk and model error within stated ranges, and the network is chosen against the worst plausible error and '
    'reported with its certified optimality gap; a conductivity logger in at least one production well of each '
    'wellfield and a yearly campaign of laboratory samples paired 1, 3 and 7 days apart measure the time scale that '
    'decides crossings between samples; a tracer campaign (Br/Cl, water isotopes, depth profiles from multilevel '
    'wells, nitrate and boron) is chosen by the value of the pumping decisions it changes; two piezometers between the '
    'wellfields and the inland cut, about one diffusion length apart, learn the boundary of the model (T2.3); '
    'procurement and '
    'installation (T4.2), with one GNSS station, two corner reflectors, a seismic station and a water-table logger at '
    "the TAP landfall, under TAP's security rules; operation and maintenance (T4.3), in which every reading is "
    'corrected for air pressure and logger drift before use and the corrected residuals are checked for remaining '
    'correlation; seismic velocity as a water-table gauge, and the shear-wave velocity of the soft layers for their '
    'earthquake step (T4.4). Risk: procurement delays and limited site access; '
    'mitigation: early orders, inductions with security officers. Risk: lagged or uncertain barometric responses; '
    'mitigation: response functions estimated from the first three months by regression deconvolution, with their '
    'error carried into the robust design. Milestones: MS1 (Month 6), MS2 (Month 12).\n'
    'WP5, Live demonstration (Months 22–36; NATO-country team). Steps: dry run (T5.1); twelve months of bulletins '
    "(T5.2); safe operating window and pumping rule (T5.3): the effect of each wellfield's pumping on salinity is "
    'estimated with the hidden drought demand removed, by reading the recharge from the heads after adding back the '
    'drawdown measured in the pumping tests, and a calibrated check of every substitute is run before any effect is '
    'reported; the salinity under a drier recharge regime is computed from the calibrated state with conformal bands; '
    'the certified window, its closing year and safe pumping tests that sharpen it follow, and the pumping and drought '
    'rule is agreed with the utility and AMBU; while the source of the chloride is uncertain (sea, deep brine, drought '
    'or return flow), the sources the tracers cannot exclude are kept in a set updated monthly with anytime-valid '
    'e-values, the pumping allocation is kept safe for every source in it, and a ledger shows the cost borne by the '
    'utility, the farmers and the wetland; post-event protocol (T5.4), in which the relaxation of the logged heads '
    'after a strong earthquake gives the leakage of the confined aquifer as a free pumping test. Risk: no strong event '
    'occurs; mitigation: verification by back-testing and storylines, and the well records of November 2019 where they '
    'exist. Risk: drawdown coefficients from the pumping tests are uncertain; '
    'mitigation: their uncertainty is carried into the effect as a stated bias band. Risk: the true source of the '
    'chloride is not among those considered, or mixes two of them; mitigation: a goodness-of-fit check at every '
    'update, mixtures admitted as hypotheses, and the alternative supply as fallback. Milestone: MS6 (Month 34).\n'
    'WP6, Training, transfer and dissemination (Months 1–36; partner-country team): early-career researchers and a '
    'training school (T6.1), operator training (T6.2), open release (T6.3), transfer to a second coast (T6.4). Risk: '
    'the operators rely on the bulletins alone, or trained operator staff leave; mitigation: the system stays advisory '
    "beside the operators' own procedures, the training explains what a certified miss rate means, and at least two "
    'people are trained per operator. Milestone: MS7 (Month 36), the operators own and run the system: an operating '
    'procedure adopted for each asset, every bulletin of Months 34–36 issued by the operators without the project '
    'team, and a maintenance agreement signed by Month 33 (D6.2).\n'
    'WP7, Management, data and risk (Months 1–36; coordinator): management and reporting (T7.1), data plan and access '
    'agreements (T7.2), risk register (T7.3). Risk: the operators delay access to well, port or landfall data; '
    'mitigation: access agreements by Month 3, with WP1 and the design of WP4 started on public and satellite data '
    'meanwhile. Risk: a release discloses sensitive information on critical infrastructure; mitigation: data '
    'classified in the data plan, asset-level results shared only with the operators and authorities, and publications '
    'reviewed by the operators before submission. Milestones: access agreements and data management plan (D7.1, Month '
    '3); progress reports at the SPS milestones (D7.2, Months 6, 18 and 30); final report (D7.3, Month 36); the risk '
    'register reviewed at every gate.')


AFTER = (
    'Implementation. The operators issue every bulletin themselves in Months 34–36, with at least two trained staff each, and '
    'sign a maintenance agreement (Month 33) that covers the running cost of about €10,900 per year for data, telemetry and '
    'spare sensors. Until it is in place, the Albanian university hosts the system. Operating procedures for each asset and '
    'a policy brief for the national authorities (D6.2) anchor the warnings in daily practice.\n'
    'Next steps: extend the warnings to the other wellfields and coastal assets of Albania; offer the open software to '
    'coasts of Allies and partners (tested on a second coast in the partner country during the project); seek national and '
    'European funding to keep the network and the verification ledger running.\n'
    'Role of the end-users. The water utility, the Water Resources Management Agency (AMBU), the port authority, the '
    'operator of the Trans Adriatic Pipeline (TAP) and the National Civil Protection Agency guide the project from the start: they give access to sites '
    'and records, agree the thresholds and tolerable miss rates (T3.1), take part in the dry run, co-sign the operational '
    'milestones and run the bulletins in live operation. The operators own the system after the hand-over; AMBU uses its '
    'results without procurement, ownership or maintenance obligations. End-users receive no SPS funds.')

COMMS = (
    'Activities: a public kick-off, a public start of live operation and a final event; a project website with public '
    'summaries in Albanian and English; a quarterly verification ledger showing, for each alarm type, events, misses, false '
    'alarms and the bound on the miss rate; at least six open-access papers and eight conference presentations; a policy '
    'brief for the national authorities; stakeholder workshops at kick-off, mid-term, end and for transfer.\n'
    'Presenting the project to the public: the start of live warnings, the training school (Month 14) and the hand-over to '
    'the operators are natural moments for press releases and local media.\n'
    'Likely photo and video subjects for the SPS Office (after security clearance by the operators): installing '
    'piezometers and GNSS stations, corner reflectors on the coast, the training school, a civil-protection exercise with '
    'the bulletins.\n'
    'Budget link: the heading "Communication and Publications" (€18,000) covers open-access fees (€12,000), the website, '
    'translation and printing (€5,000) and public events (€1,000). Asset-level information is never published; every output '
    'passes a release gate.')

KPIS = (
    'The project is on track when the following are achieved on time:\n'
    '• D4.1 network design approved by the steering committee and the operators, with a certified optimality gap of at '
    'most 25% for the chosen network (Month 6, MS1).\n'
    '• D4.2 network installed and streaming with at least 90% data availability, and the corrected heads within 3 cm '
    'root-mean-square of manual dips (at most half the raw error); D1.1 coastal motion atlas with a vertical velocity '
    'uncertainty of about 1–2 mm/yr at asset points (Month 12, MS2).\n'
    '• D2.1 calibrated coupled model: held-out heads, chloride, InSAR and seismic velocity inside the 90% predictive '
    'intervals at close to the nominal rate, and for each wellfield a certified band at most 0.25 wide for the chance '
    'that chloride crosses its limit within the season (Month 18, MS3).\n'
    '• D2.2 certified surrogate: error bound met on test runs; alarm prototype passes a dry run (Month 22, MS4, '
    'go/no-go for live operation).\n'
    "• D3.2 back-testing: each alarm's miss rate at or below its target with a 95% confidence bound, crossings between "
    'samples included, under a protocol published with a DOI before the results (Month 27, MS5).\n'
    '• D5.1 twelve months of live bulletins with every outcome logged, the miss rates consistent with their '
    'certificates, and the certified safe operating window reported for each asset, with every safe pumping test below '
    'its chloride test limit (Month 34, MS6).\n'
    '• Source of the chloride (T5.3): the tracer campaign chosen by decision value completed by Month 24, and the set '
    'of plausible sources with the pumping allocation published monthly from then on, keeping the true source in at '
    'least 95% of back-tested simulated cases.\n'
    '• Inland boundary (T2.3): learned from the two boundary piezometers and passive (all weights nonnegative), with '
    'held-out heads at both piezometers inside the 90% predictive intervals (Month 18, MS3).\n'
    '• Earthquake response (T4.4, T5.4): the shear-wave velocity of the soft layers at the port and the landfall '
    'measured by Month 18, giving the step coefficient of each layer; after any earthquake felt at the sites, the '
    'leakage of the confined aquifer read from the loggers within 30 days.\n'
    '• D6.1 open software and data with a DOI, reproduced by someone outside the team (Month 33); D6.2 operating '
    'procedures adopted and policy brief delivered (Month 36, MS7).\n'
    '• Capacity: at least 20 trained operator and civil-protection staff, at least six early-career researchers, at '
    'least six open-access papers and eight conference presentations.\n'
    '• Management: progress reports at each SPS milestone, spending within 10% of the plan per budget category, and '
    'the risk register reviewed at every gate.')

CRITERIA = [
    ['Each alarm\'s miss rate in back-testing over the record since 2014 is at or below its certified target (indicatively 5–10%), with a 95% confidence bound (D3.2, Month 27)', 25],
    ['Twelve months of live bulletins (Months 23–34) with every outcome logged and no verification test rejecting a certified miss rate (D5.1)', 20],
    ['Held-out heads, chloride, InSAR and seismic velocity fall inside the model\'s 90% predictive intervals at a rate of at least 85% (D2.1, Month 18)', 15],
    ['The operators issue all bulletins in Months 34–36 with at least two trained staff each, and the maintenance agreement is signed (MS7)', 15],
    ['The monitoring network reaches at least 90% data availability over twelve months of operation (D4.2, T4.3)', 10],
    ['The certified safe operating window and its closing year are reported for each asset and confirmed by the full model at the closing point, and every pumping test stays below its chloride test limit (T5.3)', 10],
    ['The open release is installed and reproduces the synthetic test coast for a group outside the consortium (D6.1, Month 33)', 5],
]

ABBREV = ('AI: artificial intelligence; CF: Climate and Forecast conventions; CPT: cone penetration test; D: deliverable; DOI: '
          'digital object identifier; dv/v: relative change of seismic velocity; EDT: emerging and disruptive technologies; '
          'FAIR: findable, accessible, interoperable, reusable; GDPR: General Data Protection Regulation; GNSS: global '
          'navigation satellite system; InSAR: interferometric synthetic aperture radar; KPI: key performance indicator; '
          'MS: milestone; MYP: Multi-Year Project; NPD: NATO-country Project Director; PPD: partner-country Project Director; '
          'SPS: Science for Peace and Security; T: task; TRL: technology readiness level; WP: work package.')

LIMITS = {'Security challenge': (SECURITY, 500), 'Technical challenge': (TECHNICAL, 500), 'Deliver': (DELIVER, 500),
          'End state': (HOW, 500), 'Abstract': (ABSTRACT, 200), 'Impact': (IMPACT, 500), 'KPIs': (KPIS, 500)}


# ------------------------------------------------------------------------------------------------- helpers
def words(t):
    return len(re.sub(r'\*\*', '', t).split())


def put(p, text, size=10.5, color=None, italic=False):
    """Text with **bold** and [placeholders] highlighted in yellow."""
    for k, seg in enumerate(re.split(r'(\[[^\]]+\])', text)):
        if not seg:
            continue
        hl = seg.startswith('[') and seg.endswith(']')
        for j, s in enumerate(seg.split('**')):
            if not s:
                continue
            r = p.add_run(s); r.font.size = Pt(size); r.bold = (j % 2 == 1); r.italic = italic
            if color:
                r.font.color.rgb = RGBColor.from_string(color)
            if hl:
                r.font.highlight_color = WD_COLOR_INDEX.YELLOW


def field(doc, name, note=None):
    p = para(doc, 1, before=7); p.paragraph_format.keep_with_next = True
    put(p, name, size=11, color=NAVY); p.runs[0].bold = True
    if note:
        q = para(doc, 2); q.paragraph_format.keep_with_next = True
        put(q, note, size=9, color=GREY, italic=True)


def answer(doc, text, limit=None, size=10.5):
    for line in text.split('\n'):
        p = para(doc, 3, 0.3 if line.startswith('•') else 0); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        put(p, line, size=size)
    if limit:
        n = words(text)
        q = para(doc, 2); put(q, f'{n} words (limit {limit})', size=8.8, color='1E8A5A', italic=True)


def head_repeat(t):
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    return t


def ph_cells(t):
    for row in t.rows[1:]:
        for c in row.cells:
            for p in c.paragraphs:
                for r in p.runs:
                    if re.fullmatch(r'\[[^\]]*\]', r.text.strip()) or (r.text.strip().startswith('[') and r.text.strip().endswith(']')):
                        r.font.highlight_color = WD_COLOR_INDEX.YELLOW


# ------------------------------------------------------------------------------------------------- budget
SPS_CATS = ['Equipment', 'Training', 'Communication and Publications', 'Travel', 'Consumables', 'Other', 'Stipends',
            'Co-financing of personnel']


def sps_cat(r):
    c, it = r['cat'], r['item']
    if c == 'Training and travel':
        return 'Training' if any(k in it for k in ('exchange', 'Training school', 'training sessions')) else 'Travel'
    return {'Equipment': 'Equipment', 'Consumables': 'Consumables', 'Stipends': 'Stipends',
            'Dissemination': 'Communication and Publications', 'Other direct costs': 'Other',
            'Management': 'Other'}[c]


def budget_tables():
    rows = BB.compute()
    by = defaultdict(lambda: [0] * 4)
    for ln in BB.director_lines():   # whole euros per period ending at M1 (6), M2 (18), M3 (30), final (36)
        for i, v in enumerate(ln['per']):
            by[sps_cat(ln)][i] += v
    total = sum(r['tot'] for r in rows)
    return rows, by, total


# ------------------------------------------------------------------------------------------------- document
def main(out):
    for k, (t, lim) in LIMITS.items():
        assert words(t) <= lim, f'{k}: {words(t)} > {lim}'
    assert len(TITLE) <= 105, len(TITLE)
    assert len(SHORT) <= 80
    assert sum(w for _, w in CRITERIA) == 100 and len(CRITERIA) <= 7
    rows, by, total = budget_tables()

    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.7)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10.5)

    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    put(p, 'CERTAIN-COAST — Text for the NATO SPS application form', size=17, color=NAVY); p.runs[0].bold = True
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    put(p, 'Multi-Year Project · call 2027-1 · every field in the order of the official form · '
           'apply on https://natosps.grantplatform.com', size=10.5, color=GREY)

    heading(doc, 'How to use this document', 13, before=2)
    for b in ['**This is the only document you need for the online form.** Go through it from top to bottom and copy each answer into the field with the same name on the platform. The other CERTAIN-COAST documents are background and are not uploaded.',
              '**Word limits are respected:** the green line under each long answer gives its length.',
              '**Yellow text** is information only you can give (names, dates, signatures, choices). Replace it before submitting.',
              '**Uploads and signatures** are listed in the checklist below; all uploads are PDF files.',
              '**Deadline:** 15 November 2026, 23:59 CET (call 2027-1, checked on nato.int on 6 November 2026). The call asks for full proposals in one round: fill every field now. Limits per field are in words; there is no page limit except one page per institution overview.']:
        q = para(doc, 3, 0.3); put(q, '• ' + b)

    heading(doc, 'Checklist: uploads and signatures', 13, before=8)
    chk = [['SPS MYP Acceptance of Funds (NATO template)', 'PDF', 'Filled in: CERTAIN-COAST_SPS_MYP_Acceptance_of_Funds.docx; the NPD and a representative of the NPD\'s institution (Head of Institution or Financial Authority) sign; upload in tab 4', '[to do]'],
           ['SPS MYP Agreement for Joint Research (NATO template)', 'PDF', 'Filled in: CERTAIN-COAST_SPS_MYP_Agreement_for_Joint_Research.docx; all Co-Directors and a representative of each institution sign', '[to do]'],
           ['SPS MYP Detailed Budget workbook (NATO Excel template, tabs "Info" and "Detail")', 'Excel', 'Fill by hand (the form warns that using AI on this file may corrupt it and lead to automatic rejection), typing the values of CERTAIN-COAST_Budget_Workbook_Guide.docx cell by cell', '[to do]'],
           ['Project schedule with a Gantt chart', 'PDF', 'Ready: CERTAIN-COAST_Project_Schedule.pdf', 'ready'],
           ['End-user commitments, all letters merged into one file', 'PDF', 'Each end-user on its own letterhead (drafts in the Letters of Commitment document)', '[to do]'],
           ['Brief overview of participating institutions (at most one page each)', 'PDF', 'Draft: CERTAIN-COAST_Institutions_Overview.docx; fill the yellow fields, save as PDF', '[to do]'],
           ['Financial rules of the NPD\'s institution', 'Link', 'Ready: the UPT Statute in English (Chapter IV, Articles 24–25), '
            'https://upt.edu.al/wp-content/uploads/2023/02/Statuti-PDF-English.pdf. If the UPT finance office provides its '
            'internal regulation on administration, finance and accounting, upload that PDF instead', 'ready'],
           ['Intellectual Property Rights agreement or waiver', 'PDF', 'Draft: CERTAIN-COAST_IPR_Agreement_Draft.docx; all Co-Directors, their institutions and the end-users sign; recommended now (listed in the 2027-1 call), allowed after approval', '[to do]'],
           ['Illustrative figures (optional, one PDF with a table of contents)', 'PDF', 'Ready: CERTAIN-COAST_Illustrative_Figures.pdf (6 pages, 12 figures)', 'ready'],
           ['Additional files (optional): technical annex and two notes, later with the CVs', 'PDF', 'Ready: CERTAIN-COAST_Additional_Files.pdf (49 pages, contents and bookmarks: the technical annex, 10 pages, with methods, preparatory tests, gates and fallbacks and the nine new contributions; the technical note on the assembled system and the placement of the wells, 22 pages; the PËRTEJ-GO theory note on the inland boundary of the model, 16 pages). When the CVs are filled in, they are added to the same PDF (build_additional_files.py)', 'ready']]
    t = head_repeat(table(doc, ['Upload', 'Format', 'Who signs or prepares it', 'Status'], chk, [6.4, 1.6, 6.8, 2.2], size=9.2))
    ph_cells(t)
    q = para(doc, 3, before=4)
    put(q, '**Still missing before you can submit:** [a partner-country Project Director, employed and resident in an eligible '
           'partner country] (without one the application is not eligible); [confirmation of the Albanian institution of the '
           'NPD]; [signed letters from the five end-users].', size=10.5)

    # 1 Start here
    heading(doc, '1. Start here', 14, before=10)
    field(doc, 'Project title', 'About 100 characters; understandable to non-experts; link to security and NATO.')
    answer(doc, TITLE); q = para(doc, 2); put(q, f'{len(TITLE)} characters', size=8.8, color='1E8A5A', italic=True)
    field(doc, 'Project short title', '80 characters; must match cell E2 ("Short Title") in the "Info" tab of the SPS MYP Detailed Budget workbook.')
    answer(doc, SHORT)
    field(doc, 'Confirmation that you have read the Multi-Year Project Handbook')
    answer(doc, '[Tick after reading the latest MYP Handbook.]')
    field(doc, 'How did you hear about this opportunity?')
    answer(doc, '[Your choice: word of mouth, journal, conference, online, SPS Information Day or other.]')
    field(doc, 'Is the proposal a resubmission of a previous unsuccessful application?')
    answer(doc, '[No] (unless you applied with this project before).')
    field(doc, 'Did you use any generative AI tools in the preparation of your research proposal?')
    answer(doc, '**Yes.** Parts of the text were drafted with an AI assistant and checked by the applicants. Answer honestly.')

    # 2 Eligibility
    heading(doc, '2. Eligibility', 14, before=10)
    for nm, a in [('Are the Co-Directors (including NPD and PPD) affiliated with a governmental, academic, or other non-profit institution?', 'Yes. [Both directors must be employed by a university, public institute or other non-profit body.]'),
                  ('Do any of the Co-Directors (including NPD and PPD) hold other ongoing SPS grants?', '[No] (an individual may hold only one SPS grant at a time).'),
                  ('Is the application developed jointly by one or more Co-Directors from NATO countries and one or more from eligible NATO partner countries?', 'Yes. [Requires the partner-country Project Director.] Then click "Check Eligibility".')]:
        field(doc, nm); answer(doc, a)

    # 3 Activity info
    heading(doc, '3. Activity Info', 14, before=10)
    field(doc, 'Primary Key Priority', 'Select one in the dropdown.')
    answer(doc, 'Environment, Climate Change and Security')
    field(doc, 'Additional key priorities (optional, at most three)')
    answer(doc, 'Resilience; Critical Underwater Infrastructure; Innovation and Emerging Disruptive Technologies (EDTs)')
    field(doc, 'What security challenge(s) would your project address?', '500 words.')
    answer(doc, SECURITY, 500)
    field(doc, 'What technical challenge(s) would your project address, if any?', '500 words.')
    answer(doc, TECHNICAL, 500)
    field(doc, 'What will the project deliver or develop by the end of the grant?', '500 words; show how it advances the state of the art.')
    answer(doc, DELIVER, 500)
    field(doc, 'How will the project reach the planned end state?', '500 words; methodology, approach and how the teams collaborate.')
    answer(doc, HOW, 500)
    field(doc, 'May your proposal raise any ethical issue?')
    answer(doc, '**Yes**, limited: personal data of workshop and training participants, and security-sensitive data about critical infrastructure. If a text box appears, use:')
    answer(doc, BEt.SHORT)
    field(doc, 'State-of-the-art: Related Projects / Duplication')
    answer(doc, SOTA)
    field(doc, 'Funding requested from NATO SPS (in EUR)', 'Must equal cell G15 of the "Summary" tab of the SPS MYP Detailed Budget workbook.')
    answer(doc, f'{total:,.0f}')

    # 4 NPD and PPD
    heading(doc, '4. NPD & PPD', 14, before=10)
    p = para(doc, 4); put(p, 'Fill these fields directly on the platform, once for the NATO-country Project Director (NPD) and once for the partner-country Project Director (PPD):')
    pers = [['First name, family name, date of birth, sex, title', '[personal data]'],
            ['Nationality (and other nationalities)', '[NPD: e.g. Albania; PPD: a NATO or eligible partner country]'],
            ['Telephone, mobile, personal and work e-mail; online profile (optional)', '[contact data]'],
            ['Current job title; name, country and postal address of the institution', '[NPD: institution in a NATO country; PPD: institution in an eligible partner country]'],
            ['Employment history, education (three rows each)', '[dates, positions, employers; dates, degrees, universities]'],
            ['Publications and honours (optional, up to three each)', '[recent and relevant to the project]'],
            ['Research focus and expertise (500 words)', '[how the director\'s research relates to the project: e.g. seawater intrusion and groundwater modelling, coastal geodesy, geotechnics, statistics]'],
            ['Other grants held (optional)', '[dates, donor, grant name, short description, results]'],
            ['SPS Acceptance of Funds (NPD only)', 'Upload the signed PDF of CERTAIN-COAST_SPS_MYP_Acceptance_of_Funds.docx (official NATO template, filled in): signature of the NPD and of a representative of the NPD\'s institution']]
    t = head_repeat(table(doc, ['Fields', 'What to enter'], pers, [7.2, 9.8], size=9.3)); ph_cells(t)

    # 5 Co-directors
    heading(doc, '5. Co-Directors (optional)', 14, before=10)
    answer(doc, 'Not required. If you add a Co-Director, for example [an additional NATO-country co-director], they must be at '
                'a different institution and have their own budget in the Excel workbook. The Institute of Geosciences belongs '
                'to UPT, like the NPD\'s faculty, so its staff take part as participants, not as a Co-Director. Otherwise skip '
                'this tab.')

    # 6 Participants
    heading(doc, '6. Project Participants', 14, before=10)
    p = para(doc, 4); put(p, 'Roles of Co-Directors and Participants (add rows as needed; all must be nationals of NATO or eligible partner countries):')
    part = [['[First name]', '[Family name]', '[NPD institution]', 'NATO-country Project Director', '[Albanian]', 'Coordination; WP1 coastal motion; WP4 monitoring network; WP5 live operation; WP7 management', '[30%]'],
            ['[First name]', '[Family name]', '[PPD institution]', 'Partner-country Project Director', '[nationality]', 'WP6 training, transfer and dissemination; transfer study on a partner-country coast; user-side review of the bulletins', '[20%]'],
            ['[First name]', '[Family name]', '[Institute of Geosciences, UPT]', 'Researcher', '[Albanian]', 'Seismic, GNSS and hydrometeorological data; WP1, WP4', '[15%]'],
            ['To be recruited', '(4 people)', 'NPD and PPD institutions', 'Early-career researchers (stipends)', '[NATO or partner]', 'InSAR and GNSS; modelling; alarms; network and live operation (WP1–WP5)', '[50%]'],
            ['[First name]', '[Family name]', '[Durrës water utility]', 'End-user representative', '[Albanian]', 'Thresholds (T3.1), dry run, live bulletins, pumping rule', '[5%]'],
            ['[First name]', '[Family name]', '[Water Resources Management Agency (AMBU)]', 'End-user representative', '[Albanian]', 'Thresholds (T3.1), monitoring design (T4.1), pumping and drought rule (T5.3)', '[5%]'],
            ['[First name]', '[Family name]', '[Durrës Port Authority]', 'End-user representative', '[Albanian]', 'Thresholds (T3.1), dry run, live bulletins', '[5%]'],
            ['[First name]', '[Family name]', '[Trans Adriatic Pipeline AG (TAP), Albania branch]', 'End-user representative', '[nationality]', 'Thresholds (T3.1), dry run, live bulletins', '[5%]'],
            ['[First name]', '[Family name]', '[National Civil Protection Agency]', 'End-user representative', '[Albanian]', 'Post-event protocol; live bulletins', '[5%]']]
    t = head_repeat(table(doc, ['First name', 'Family name', 'Affiliation', 'Position', 'Nationality', 'Task(s)', '% time'], part,
                          [1.9, 1.9, 2.6, 2.4, 2.1, 4.6, 1.5], size=8.8)); ph_cells(t)

    # 7 Project plan
    heading(doc, '7. Project plan', 14, before=10)
    field(doc, 'Project abstract', '200 words; understandable to non-experts.')
    answer(doc, ABSTRACT, 200)
    field(doc, 'Security relevance and real-world applications')
    answer(doc, RELEVANCE)
    field(doc, 'Current status')
    answer(doc, STATUS)
    field(doc, 'Impact', '500 words; quantitative where possible.')
    answer(doc, IMPACT, 500)
    field(doc, 'Technology Readiness Level (TRL)')
    answer(doc, 'TRL 6: Technology demonstrated in relevant environment')
    field(doc, 'Technology Readiness Level (TRL) description')
    answer(doc, TRL_TEXT)
    field(doc, 'Data exploitation plan')
    answer(doc, DATA)
    field(doc, 'Work-plan')
    answer(doc, WORKPLAN)
    field(doc, 'After the project ends: Sustainability and role of end-user(s)')
    answer(doc, AFTER)
    field(doc, 'Risks and mitigation strategies')
    lvl = lambda v: 'High' if v >= 4 else ('Medium' if v == 3 else 'Low')
    pick = ['R1', 'R3', 'R5', 'R7', 'R8', 'R14', 'R15', 'R20']
    rk = {r[0]: r for r in BR.all_risks()}
    rrows = [[rk[c][1], lvl(rk[c][2]), lvl(rk[c][3]), rk[c][5]] for c in pick]
    head_repeat(table(doc, ['Risk description', 'Likelihood', 'Impact', 'Mitigating action'], rrows, [6.0, 1.9, 1.7, 7.4], size=9))
    q = para(doc, 3, before=3); put(q, f'All {len(BR.all_risks())} risks, with owners and triggers, are in the Risk Assessment document.', size=9, color=GREY, italic=True)
    field(doc, 'Communication Plan')
    answer(doc, COMMS)
    field(doc, 'Key Performance Indicators (KPIs)', '500 words.')
    answer(doc, KPIS, 500)
    field(doc, 'Criteria for success', 'At most seven, SMART, weights summing to 100%.')
    head_repeat(table(doc, ['Criterion', 'Relative weight (%)'], [[c, str(w)] for c, w in CRITERIA], [14.0, 3.0], size=9.3))
    field(doc, 'List of abbreviations')
    answer(doc, ABBREV)
    field(doc, 'Optional upload: a file that helps to illustrate the project')
    answer(doc, 'Upload CERTAIN-COAST_Illustrative_Figures.pdf (ready): six pages, a table of contents and twelve figures '
                '(the coast as one system, the critical assets and NATO resilience, the method, the innovations in the '
                'warning chain, the gaps closed, the certified safe operating window, single-hazard horizons, the alarm '
                'margin, warnings between samples, the self-correcting network, milestones and gates, impact pathway).')

    # 8 Schedule and budget
    heading(doc, '8. Project Schedule & Budget', 14, before=10)
    field(doc, 'Project duration in months')
    answer(doc, '36')
    field(doc, 'Project schedule (upload)', 'PDF with a Gantt chart: duration and interdependence of each step, critical milestones, deliverables.')
    answer(doc, 'Upload CERTAIN-COAST_Project_Schedule.pdf (ready): Gantt chart with the duration of every task, the dependencies, the critical path, the milestones and the deliverables by SPS milestone. Project milestones: MS1 network design (Month 6), MS2 '
                'network streaming (Month 12), MS3 calibrated model (Month 18), MS4 go/no-go for live operation (Month 22), MS5 '
                'miss rates confirmed (Month 27), MS6 twelve months live (Month 34), MS7 hand-over (Month 36).')
    field(doc, 'Milestones overview', 'SPS reporting milestones; must match the "Info" tab of the budget workbook (at least one milestone every 12 months).')
    ms = [['Kick-off', 'Project kick-off meeting', '0'], ['Milestone 1 (required)', 'First technical and financial report', '6'],
          ['Milestone 2 (required)', 'Second technical and financial report', '18'], ['Milestone 3 (required)', 'Third technical and financial report', '30'],
          ['Milestone 4 (optional)', 'Fourth technical and financial report', 'leave blank'], ['Final report (required)', 'Final technical and financial report', '36']]
    head_repeat(table(doc, ['Event', 'Description', 'Months after kick-off'], ms, [4.5, 8.5, 4.0], size=9.3))

    field(doc, 'Budget summary by item: NATO SPS funding requested (in EUR)',
          'Indicative split by reporting period, assuming even spending within each project year (period ending at Milestone 1 = months 0–6, M2 = 6–18, M3 = 18–30, final = 30–36). '
          'Enter the final figures from your Excel workbook.')
    brow = []
    for c in SPS_CATS:
        v = by.get(c, [0, 0, 0, 0])
        brow.append([c] + [f'{x:,.0f}' for x in v[:3]] + ['—'] + [f'{v[3]:,.0f}', f'{sum(v):,.0f}'])
    tot = [sum(by.get(c, [0] * 4)[i] for c in SPS_CATS) for i in range(4)]
    brow.append(['Total'] + [f'{x:,.0f}' for x in tot[:3]] + ['—', f'{tot[3]:,.0f}', f'{sum(tot):,.0f}'])
    t = head_repeat(table(doc, ['Budget category', 'M1', 'M2', 'M3', 'M4 (opt.)', 'Final', 'Total'], brow,
                          [4.6, 2.1, 2.1, 2.1, 1.7, 2.1, 2.3], size=9))
    for c in t.rows[-1].cells:
        shade(c, 'EAF0F8')
        for p_ in c.paragraphs:
            for r_ in p_.runs:
                r_.bold = True
    assert abs(sum(tot) - total) < 1

    def items(cat):
        return [r for r in rows if sps_cat(r) == cat]

    def listing(cat):
        return '\n'.join(f'• {r["item"]}: €{r["tot"]:,.0f}. {r["just"]}' for r in items(cat))
    field(doc, 'Equipment', 'Major equipment, its role, approximate price, co-funding.')
    answer(doc, listing('Equipment') + '\nCo-funding: [existing equipment and facilities of the institutions; operators provide '
                                         'access to wells, port and landfall].')
    field(doc, 'Training', 'SPS does not fund fellowships; training periods are short.')
    answer(doc, listing('Training'))
    field(doc, 'Travel')
    answer(doc, listing('Travel'))
    field(doc, 'Co-financing of personnel', 'Up to 25% of the personnel cost.')
    answer(doc, 'None requested: the institutions pay all salaries (see Non-NATO funding). The management hours of the NPD '
                '(€15,000) are under "Other", as the MYP Handbook (April 2026) requires. [If salary co-financing is wanted '
                'after all: per person and month at most the share of time on the project, capped at 25%, times the monthly '
                'gross salary; in total up to about one third of the grant; a CV for each recipient.]')
    field(doc, 'Other major expenses (optional)')
    answer(doc, listing('Other') + '\nCommunication and Publications (€18,000) and Consumables (€22,700) are detailed in the '
                                   'budget workbook and the Communication Plan above.')
    field(doc, 'Budget summary by item: non-NATO funding contribution (in EUR)', 'Estimate what the institutions and nations contribute.')
    import build_nonnato as NN
    nn = [[c, what, '[€ amount]'] for c, _, what in NN.NN_CATS]
    t = head_repeat(table(doc, ['Budget category', 'What it covers', 'Amount from other funding sources'], nn,
                          [3.2, 10.4, 3.4], size=9)); ph_cells(t)
    q = para(doc, 2); put(q, 'Amounts, salaries and the personnel worksheet: CERTAIN-COAST_Non-NATO_Contribution.docx.',
                          size=9, color=GREY, italic=True)
    field(doc, 'Non-NATO funding')
    answer(doc, NN.text())
    field(doc, 'How do you want to share the financial rules of the NPD\'s institution?')
    answer(doc, 'Choose "Link to a website": https://upt.edu.al/wp-content/uploads/2023/02/Statuti-PDF-English.pdf '
                '(Statute of the Polytechnic University of Tirana, English version published by UPT: Chapter IV "Properties, '
                'financing and services", Articles 24–25; Article 10, the Board of Administration approves the financial '
                'regulation). [If the UPT finance office provides its internal regulation on administration, finance and '
                'accounting, choose "File upload" and upload that PDF instead.]')

    # 9 End-users
    heading(doc, '9. End-Users', 14, before=10)
    p = para(doc, 4); put(p, 'At least one end-user; all based in a NATO or eligible partner country; end-users receive no SPS funds.')
    eu = [[f'[First name]', '[Family name]', '[Title]', '[Job title]', inst, '[Postal address]', '[Country]', '[Telephone]', '[E-mail]']
          for inst in ['[Durrës water utility]', '[Water Resources Management Agency (AMBU)]', '[Durrës Port Authority]',
                       '[Trans Adriatic Pipeline AG (TAP), Albania branch]', '[National Civil Protection Agency]']]
    t = head_repeat(table(doc, ['First name', 'Family name', 'Title', 'Job title', 'Institution', 'Postal address', 'Country', 'Telephone', 'E-mail'],
                          eu, [1.7, 1.7, 1.2, 1.8, 2.6, 2.2, 1.6, 1.9, 2.3], size=8.2)); ph_cells(t)
    field(doc, 'End-User(s) commitments (upload)')
    answer(doc, 'One PDF with all signed letters, each on the end-user\'s letterhead (drafts in the Letters of Commitment document; '
                'the end-users sign their own letters). For governmental end-users, a letter of support from the ministry or agency.')

    # 10 Attachments
    heading(doc, '10. Project attachments', 14, before=10)
    for nm, a in [('Brief overview of participating institutions (upload)', 'One PDF, at most one page per institution: capabilities, resources, facilities, websites. Use CERTAIN-COAST_Institutions_Overview.docx: [fill the yellow fields, delete the pages of institutions that do not take part], then save it as PDF.'),
                  ('SPS MYP Agreement for Joint Research (upload)', 'NATO template, signed by all Co-Directors and a representative of each institution.'),
                  ('Do you want to include the Intellectual Property Rights (IPR) Agreement (or Waiver) now?', '**Yes** (recommended): upload the signed agreement as one PDF. Draft: CERTAIN-COAST_IPR_Agreement_Draft.docx (NATO sample, Option B, open release of software and data, security release check), with a one-page waiver as alternative. The form and the Handbook allow it after approval, but the 2027-1 call lists it among the documents of a complete proposal.'),
                  ('Additional files (optional)', 'Upload CERTAIN-COAST_Additional_Files.pdf (49 pages), one PDF with a table of contents at the start, as the form asks: the technical annex (10 pages: how the methods work, the preparatory tests, the gates with their fallbacks and the nine new contributions, consistent with this form), the technical note on the assembled system of equations and the placement of recharge and supply wells (22 pages; synthetic tests, illustrative values) and the PËRTEJ-GO theory note on the inland boundary of the model (16 pages; four propositions with proofs, synthetic tests). [When the CVs of the Co-Directors are filled in, they are added to the same PDF and the contents page is rebuilt.]'),
                  ('Additional information (optional)', 'The additional files open with the technical annex, which summarises the methods and their preparatory tests, followed by a technical note on the coupled model and the placement of recharge and supply wells and by a theory note on the inland boundary of that model, learned from piezometers; the full methodology, state of the art, work packages, risk assessment and data management plan are available on request.')]:
        field(doc, nm); answer(doc, a)

    doc.save(out)
    print('saved', out, '| total', total, '| words:', {k: words(t) for k, (t, _) in LIMITS.items()}, '| title chars', len(TITLE))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_NATO_Application_Form_Text.docx')
