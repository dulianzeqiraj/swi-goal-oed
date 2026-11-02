"""CERTAIN-COAST (NATO SPS proposal): Methodology, built around methods of the 2021-2026 research frontier and three new
contributions that were derived and tested numerically before the project:

  C1  the certified safe operating window for pumping and dewatering, and the sea level and year at which it closes;
  C2  the value of a sensor in years of certified safe operation;
  C3  safe, goal-oriented pumping tests that move the certified boundary of the window towards the true one, valued in
      years; built on active identification with guarantees (Mania, Jordan and Recht, 2022).

Version 2 also adds a generative copy of the model for long storylines (G-LED; Gao, Kaltenbach and Koumoutsakos, 2024)
and a test of what its statistics can and cannot certify (Section 4.2). Figure and table numbers are assigned in order
of appearance ({{key}} in the text); equation numbers as before ([[key]]).

Version 3 adds, from a review of 20 papers on priors (Oxford, Harvard, 2020-2026): priors that can be read and checked
in the calibration (Section 3), the prior assumption of the pumping tests with a prior-data conflict test (Section 6),
a ranking of sensors that does not hinge on one prior (Section 6, applied in T4.1), and a test of what a wrong prior
costs the pumping tests and what protection against it costs, in years (Section 7.7, method_prior.py).

Contents: the method chain (figure); the three hazards as one system; measuring the moving coast; the coupled model;
the certified surrogate; the certified alarms (online conformal calibration under shift, guarantees by regime, extreme
conformal prediction beyond the record, joint calibration by Learn then Test, extremes, back-testing, anytime-valid
verification with its simulation); goal-oriented network design with the years criterion; live operation with the
safe window, its multiplier and the preparatory test; software; pass tests and fallbacks; a ledger of standard,
adopted and new methods; Annex A with the standard working equations. Numbers in the text come from method_window.py,
method_verify.py, method_active.py, method_story.py and method_prior.py (JSON files next to this script). Section numbers 5, 5.4, 5.7, 6 and 7 are cited by other
CERTAIN-COAST documents and are kept.

usage: python build_methodology.py OUT.docx"""
import json
import os
import re
import sys
import tempfile

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', '..', 'ml_paradigms', 'word'))
from build_sota import run, para, heading, table, shade  # noqa: E402
import omml  # noqa: E402

FULL = ('Certified early warning for seawater intrusion, liquefaction and extreme sea levels at the wellfields, port and '
        'energy landfall of a subsiding Adriatic coast')
COL = {'WP1': '#2e6db4', 'WP2': '#6a4fb3', 'WP3': '#b03a3a', 'WP4': '#1e8a5a', 'WP5': '#c27c12'}

# ---------------------------------------------------------------------------------------------------- references
# Classic method references (cited in the Methodology; listed as [C] in the consolidated references).
REFS = [
    'Abbasi-Yadkori, Y., Pál, D., Szepesvári, C. (2011). Improved algorithms for linear stochastic bandits. Advances in Neural Information Processing Systems 24, 2312–2320.',
    'Becker, R., Rannacher, R. (2001). An optimal control approach to a posteriori error estimation in finite element methods. Acta Numerica 10, 1–102.',
    'Berger, J.O. (1994). An overview of robust Bayesian analysis. Test 3(1), 5–124. https://doi.org/10.1007/BF02562676',
    'Boulanger, R.W., Idriss, I.M. (2014). CPT and SPT based liquefaction triggering procedures. Report UCD/CGM-14/01, University of California, Davis.',
    'Clopper, C.J., Pearson, E.S. (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. Biometrika 26(4), 404–413.',
    'Coles, S. (2001). An Introduction to Statistical Modeling of Extreme Values. Springer.',
    'Emerick, A.A., Reynolds, A.C. (2013). Ensemble smoother with multiple data assimilation. Computers & Geosciences 55, 3–15.',
    'Evans, M., Moshonov, H. (2006). Checking for prior-data conflict. Bayesian Analysis 1(4), 893–914. https://doi.org/10.1214/06-BA129',
    'Gelman, A., Simpson, D., Betancourt, M. (2017). The prior can often only be understood in the context of the likelihood. Entropy 19(10), 555. https://doi.org/10.3390/e19100555',
    'Gibbs, I., Candès, E. (2021). Adaptive conformal inference under distribution shift. NeurIPS 34.',
    'Haasnoot, M., Kwakkel, J.H., Walker, W.E., ter Maat, J. (2013). Dynamic adaptive policy pathways: a method for crafting robust decisions for a deeply uncertain world. Global Environmental Change 23(2), 485–498. https://doi.org/10.1016/j.gloenvcha.2012.12.006',
    'Iwasaki, T., Tatsuoka, F., Tokida, K., Yasuda, S. (1978). A practical method for assessing soil liquefaction potential based on case studies at various sites in Japan. Proc. 2nd Int. Conf. on Microzonation, San Francisco.',
    'Kwadijk, J.C.J., Haasnoot, M., Mulder, J.P.M., et al. (2010). Using adaptation tipping points to prepare for climate change and sea level rise: a case study in the Netherlands. WIREs Climate Change 1(5), 729–740. https://doi.org/10.1002/wcc.64',
    'Mantoglou, A. (2003). Pumping management of coastal aquifers using analytical models of saltwater intrusion. Water Resources Research 39(12), 1335. https://doi.org/10.1029/2002WR001891',
    'Murphy, A.H. (1977). The value of climatological, categorical and probabilistic forecasts in the cost-loss ratio situation. Monthly Weather Review 105(7), 803.',
    'Pukelsheim, F. (1993). Optimal Design of Experiments. John Wiley & Sons, New York.',
    'Richardson, D.S. (2000). Skill and relative economic value of the ECMWF Ensemble Prediction System. Quarterly Journal of the Royal Meteorological Society 126, 649–667.',
    'Riley, F.S. (1969). Analysis of borehole extensometer data from central California. IASH Publication 89, 423–431.',
    'Seed, H.B., Idriss, I.M. (1971). Simplified procedure for evaluating soil liquefaction potential. Journal of the Soil Mechanics and Foundations Division, ASCE 97(SM9), 1249–1273.',
    'Sens-Schönfelder, C., Wegler, U. (2006). Passive image interferometry and seasonal variations of seismic velocities at Merapi Volcano, Indonesia. Geophysical Research Letters 33, L21302.',
    'Simpson, D., Rue, H., Riebler, A., Martins, T.G., Sørbye, S.H. (2017). Penalising model component complexity: a principled, practical approach to constructing priors. Statistical Science 32(1), 1–28. https://doi.org/10.1214/16-STS576',
    'Strack, O.D.L. (1976). A single-potential solution for regional interface problems in coastal aquifers. Water Resources Research 12(6), 1165–1174. https://doi.org/10.1029/WR012i006p01165',
    'Ville, J. (1939). Étude critique de la notion de collectif. Gauthier-Villars, Paris.',
    'Wagner, B.J. (1999). Evaluating data worth for ground-water management under uncertainty. Journal of Water Resources Planning and Management 125(5), 281–288. https://doi.org/10.1061/(ASCE)0733-9496(1999)125:5(281)',
    'Werner, A.D., Simmons, C.T. (2009). Impact of sea-level rise on sea water intrusion in coastal aquifers. Ground Water 47(2), 197–204. https://doi.org/10.1111/j.1745-6584.2008.00535.x',
]
# Frontier references 2018-2026 on which the methodology builds (each checked against publisher or index records).
FRONTIER = [
    'Andrews, I., Shapiro, J.M. (2021). A model of scientific communication. Econometrica 89(5), 2117–2142. https://doi.org/10.3982/ECTA18155',
    'Angelopoulos, A.N., Barber, R.F., Bates, S. (2024). Online conformal prediction with decaying step sizes. Proc. 41st International Conference on Machine Learning, PMLR 235, 1616–1630.',
    'Angelopoulos, A.N., Bates, S., Candès, E.J., Jordan, M.I., Lei, L. (2025). Learn then test: calibrating predictive algorithms to achieve risk control. Annals of Applied Statistics 19(2), 1641–1662. https://doi.org/10.1214/24-AOAS1998',
    'Angelopoulos, A.N., Bates, S., Fannjiang, C., Jordan, M.I., Zrnic, T. (2023). Prediction-powered inference. Science 382(6671), 669–674. https://doi.org/10.1126/science.adi6000',
    'Angelopoulos, A.N., Bates, S., Fisch, A., Lei, L., Schuster, T. (2024). Conformal risk control. 12th International Conference on Learning Representations (ICLR 2024).',
    'Arnold, S., Henzi, A., Ziegel, J.F. (2023). Sequentially valid tests for forecast calibration. Annals of Applied Statistics 17(3), 1909–1935. https://doi.org/10.1214/22-AOAS1697',
    'Attia, A., Alexanderian, A., Saibaba, A.K. (2018). Goal-oriented optimal design of experiments for large-scale Bayesian linear inverse problems. Inverse Problems 34(9), 095009. https://doi.org/10.1088/1361-6420/aad210',
    'Befus, K.M., Barnard, P.L., Hoover, D.J., Finzi Hart, J.A., Voss, C.I. (2020). Increasing threat of coastal groundwater hazards from sea-level rise in California. Nature Climate Change 10(10), 946–952. https://doi.org/10.1038/s41558-020-0874-1',
    'Carmona, C.U., Nicholls, G.K. (2020). Semi-modular inference: enhanced learning in multi-modular models by tempering the influence of components. Proc. 23rd International Conference on Artificial Intelligence and Statistics, PMLR 108, 4226–4235.',
    'Clements, T., Denolle, M.A. (2018). Tracking groundwater levels using the ambient seismic field. Geophysical Research Letters 45(13), 6459–6465. https://doi.org/10.1029/2018GL077706',
    'Coulon, C., White, J.T., Pryet, A., Gatel, L., Lemieux, J.-M. (2024). An ensemble-based approach for pumping optimization in an island aquifer considering parameter, observation and climate uncertainty. Hydrology and Earth System Sciences 28(1), 303–319. https://doi.org/10.5194/hess-28-303-2024',
    'Fuglstad, G.-A., Simpson, D., Lindgren, F., Rue, H. (2019). Constructing priors that penalize the complexity of Gaussian random fields. Journal of the American Statistical Association 114(525), 445–452. https://doi.org/10.1080/01621459.2017.1415907',
    'Gao, H., Kaltenbach, S., Koumoutsakos, P. (2024). Generative learning for forecasting the dynamics of high-dimensional complex systems. Nature Communications 15, 8904. https://doi.org/10.1038/s41467-024-53165-w',
    'Gibbs, I., Candès, E.J. (2024). Conformal inference for online prediction with arbitrary distribution shifts. Journal of Machine Learning Research 25(162), 1–36.',
    'Gibbs, I., Cherian, J.J., Candès, E.J. (2025). Conformal prediction with conditional guarantees. Journal of the Royal Statistical Society Series B 87(4), 1100–1126. https://doi.org/10.1093/jrsssb/qkaf008',
    'Gong, R., Meng, X.-L. (2021). Judicious judgment meets unsettling updating: dilation, sure loss and Simpson\'s paradox. Statistical Science 36(2), 169–190. https://doi.org/10.1214/19-STS765',
    'Gopakumar, V., Gray, A., Zanisi, L., et al. (2025). Calibrated physics-informed uncertainty quantification. Proc. 42nd International Conference on Machine Learning, PMLR 267, 20103–20141.',
    'Grant, A.R.R., Wein, A., Befus, K.M., et al. (2021). Changes in liquefaction severity in the San Francisco Bay Area with sea-level rise. Geo-Extreme 2021, Geotechnical Special Publication 329, 308–317. ASCE. https://doi.org/10.1061/9780784483695.030',
    'Haasnoot, M., van \'t Klooster, S., van Alphen, J. (2018). Designing a monitoring system to detect signals to adapt to uncertain climate change. Global Environmental Change 52, 273–285. https://doi.org/10.1016/j.gloenvcha.2018.08.003',
    'Huang, D., Stein, N., Rubin, D.B., Kou, S.C. (2020). Catalytic prior distributions with application to generalized linear models. Proceedings of the National Academy of Sciences 117(22), 12004–12010. https://doi.org/10.1073/pnas.1920913117',
    'Kallioinen, N., Paananen, T., Bürkner, P.-C., Vehtari, A. (2024). Detecting and diagnosing prior and likelihood sensitivity with power-scaling perturbations. Statistics and Computing 34, 57. https://doi.org/10.1007/s11222-023-10366-5',
    'Kičić, I., Vlachas, P.R., Arampatzis, G., Chatzimanolakis, M., Guibas, L., Koumoutsakos, P. (2023). Adaptive learning of effective dynamics for online modeling of complex systems. Computer Methods in Applied Mechanics and Engineering 415, 116204. https://doi.org/10.1016/j.cma.2023.116204',
    'Koller, T., Berkenkamp, F., Turchetta, M., Krause, A. (2018). Learning-based model predictive control for safe exploration. 2018 IEEE Conference on Decision and Control (CDC), 6059–6066. https://doi.org/10.1109/CDC.2018.8619572',
    'Lees, M., Knight, R., Smith, R. (2022). Development and application of a 1D compaction model to understand 65 years of subsidence in the San Joaquin Valley. Water Resources Research 58(6), e2021WR031390. https://doi.org/10.1029/2021WR031390',
    'Lekeufack, J., Angelopoulos, A.N., Bajcsy, A., Jordan, M.I., Malik, J. (2024). Conformal decision theory: safe autonomous decisions from imperfect predictions. 2024 IEEE International Conference on Robotics and Automation (ICRA), 11668–11675. https://doi.org/10.1109/ICRA57147.2024.10610041',
    'Li, Z., Kovachki, N., Azizzadenesheli, K., Liu, B., Bhattacharya, K., Stuart, A., Anandkumar, A. (2021). Fourier neural operator for parametric partial differential equations. 9th International Conference on Learning Representations (ICLR 2021).',
    'Lu, L., Jin, P., Pang, G., Zhang, Z., Karniadakis, G.E. (2021). Learning nonlinear operators via DeepONet based on the universal approximation theorem of operators. Nature Machine Intelligence 3, 218–229. https://doi.org/10.1038/s42256-021-00302-5',
    'Ma, Z., Pitt, D., Azizzadenesheli, K., Anandkumar, A. (2024). Calibrated uncertainty quantification for operator learning via conformal prediction. Transactions on Machine Learning Research.',
    'Mania, H., Jordan, M.I., Recht, B. (2022). Active learning for nonlinear system identification with guarantees. Journal of Machine Learning Research 23, 1–30. http://jmlr.org/papers/v23/20-807.html',
    'Mazi, K., Koussis, A.D., Destouni, G. (2013). Tipping points for seawater intrusion in coastal aquifers under rising sea level. Environmental Research Letters 8(1), 014001. https://doi.org/10.1088/1748-9326/8/1/014001',
    'Mieth, R., Morales, J.M., Poor, H.V. (2025). Data valuation from data-driven optimization. IEEE Transactions on Control of Network Systems 12(1), 954–966. https://doi.org/10.1109/TCNS.2024.3431415',
    'Ohenhen, L.O., Shirzaei, M., Ojha, C., Kirwan, M.L. (2023). Hidden vulnerability of US Atlantic coast to sea-level rise due to vertical land motion. Nature Communications 14, 2038. https://doi.org/10.1038/s41467-023-37853-7',
    'Pasche, O.C., Engelke, S. (2024). Neural networks for extreme quantile regression with an application to forecasting of flood risk. Annals of Applied Statistics 18(4), 2818–2839. https://doi.org/10.1214/24-AOAS1907',
    'Pasche, O.C., Lam, H., Engelke, S. (2026). Extreme conformal prediction: reliable intervals for high-impact events. Extremes 29(2), 129–155. https://doi.org/10.1007/s10687-026-00536-9',
    'Ramdas, A., Grünwald, P., Vovk, V., Shafer, G. (2023). Game-theoretic statistics and safe anytime-valid inference. Statistical Science 38(4), 576–601. https://doi.org/10.1214/23-STS894',
    'Rodríguez Tribaldos, V., Ajo-Franklin, J.B. (2021). Aquifer monitoring using ambient seismic noise recorded with distributed acoustic sensing (DAS) deployed on dark fiber. Journal of Geophysical Research: Solid Earth 126, e2020JB021004. https://doi.org/10.1029/2020JB021004',
    'Shen, C., Appling, A.P., Gentine, P., et al. (2023). Differentiable modelling to unify machine learning and physical models for geosciences. Nature Reviews Earth & Environment 4(8), 552–567. https://doi.org/10.1038/s43017-023-00450-9',
    'Vovk, V., Wang, R. (2021). E-values: calibration, combination and applications. Annals of Statistics 49(3), 1736–1754. https://doi.org/10.1214/20-AOS2020',
    'Wagenmaker, A., Jamieson, K. (2020). Active learning for identification of linear dynamical systems. Proc. 33rd Conference on Learning Theory, PMLR 125, 3487–3582.',
    'Zimmer, C., Meister, M., Nguyen-Tuong, D. (2018). Safe active learning for time-series modeling with Gaussian processes. Advances in Neural Information Processing Systems 31, 2730–2739.',
]

# ---------------------------------------------------------------------------------------------------- tables
INDICATORS = [
    ['Seawater intrusion (wellfields)', 'I₁: chloride cⱼ at each production well j', 'c* agreed with the utility (for example the drinking-water value of 250 mg/L)', 'Weeks to months; updated weekly', 'Chloride will exceed c* within the lead time unless pumping changes'],
    ['Liquefaction (port, energy landfall)', 'I₂: liquefaction potential index (LPI) under the design shaking at the current water table', 'Class boundary agreed with the operators', 'State updated daily; recomputed at once after an earthquake', 'If the design earthquake struck now, liquefaction would exceed the agreed level'],
    ['Extreme water level (all three)', 'I₃: total water level TWLₐ at asset a', 'Design or operational level of each asset', 'Hours to days for storms; return levels yearly', 'The water level will exceed the level the asset was built for'],
]

CHECKS = [
    ['Coastal motion (WP1)', 'Relative sea level and land motion at each asset; compaction parameters; preconsolidation head', 'Vertical-velocity uncertainty of the order of 1–2 mm/yr at asset points; InSAR and GNSS agree within uncertainty', 'Corner reflectors and GNSS at the assets; persistent scatterers on structures'],
    ['Coupled model (WP2)', 'I₁, I₂, I₃ from one forcing', 'Held-out heads, chloride, InSAR and seismic velocity fall inside the 90% predictive intervals at close to the nominal rate; no prior-data conflict; the closing year moves by less than an agreed amount when the prior is power-scaled', 'Two-dimensional sections through each asset; wider error bound Δₖ; wider prior and tempered modules'],
    ['Surrogate (WP2)', 'Îₖ with Δₖ', 'Coverage of Δₖ ≥ 1 − δ on test runs; thousands of storylines per day', 'Full model on a reduced domain for flagged forecasts'],
    ['Generative copy (T2.4)', 'Storyline statistics (yearly exceedance probabilities); choice of the storylines run with the full model', 'Generated fields keep the seawater fraction within 0–1 and close the water and salt balances within tolerance; on paired storylines the prediction-powered estimate lies inside the exact bound from full runs. Closing years are always certified from full runs (Eq. [[cp]])', 'Full model on fewer storylines, chosen without the copy'],
    ['Alarms (WP3)', 'Aₖ with αₖ', 'Back-tested miss rate ≤ αₖ overall and in each regime (Clopper–Pearson); no storyline exceeds the extrapolated margin', 'Margin widened: the miss target is kept and the extra false alarms are reported'],
    ['Network (WP4)', 'Installed sensor set', '≥ 90% data availability; forecast spread and closing year move as the design predicted', 'Design re-run with the remaining budget; seismic nodes if fibre is not available'],
    ['Seismic velocity (T4.4)', 'Calibrated δv/v–water-table relation', 'Relation significant against piezometers at the port or landfall', 'Piezometers alone for the water table; velocity kept for post-event damage'],
    ['Safe window (WP5)', 'Certified window and closing year for each asset', 'Window computed with the surrogate confirmed by the full model at the closing point', 'Window computed with the full model at monthly cadence'],
    ['Pumping tests (WP5, T5.3)', 'Certified boundary of the window; years added', 'Measured chloride stays below the test limit in every test; held-out weeks fall inside the confidence set (Eq. [[conf]]); no conflict between the prior and the physics-only confidence set (Eq. [[conflict]]); the certified closing year is reported for radius S and 2S; the utility approves each test', 'Radius S widened or the physics-only prior used (Section 7.7); smaller and shorter tests; window from routine records only'],
    ['Live operation (WP5)', 'Bulletin log; pumping rule', '12 months of logged bulletins; no e-process reaches 1/β (Eq. [[eproc]])', 'If no strong event occurs, guarantees rest on back-testing and storylines (T3.4)'],
]

LEDGER = [
    ['Coastal motion (WP1)', 'Line-of-sight decomposition, trajectory model, elastic and inelastic compaction (A1–A4)',
     'Relative sea level at each asset from InSAR land motion (Ohenhen et al., 2023); compaction models calibrated on long InSAR records (Lees et al., 2022)', '—'],
    ['Coupled model (WP2)', 'Variable-density flow, dual-domain salt, sea boundary, water level, liquefaction triggering, ES-MDA (A5–A12); prior-data conflict check (Evans and Moshonov, 2006)',
     'Differentiable model with adjoint gradients (Shen et al., 2023); groundwater rise as a driver of liquefaction (Grant et al., 2021) and flooding (Befus et al., 2020); penalised-complexity priors for the fields (Fuglstad et al., 2019); semi-modular inference (Carmona and Nicholls, 2020); power-scaling sensitivity (Kallioinen et al., 2024)',
     '— (one water table driving three hazards is an integration, not claimed as a new method)'],
    ['Surrogate (T2.4)', 'Dual-weighted residual (Becker and Rannacher, 2001)',
     'Neural operators (Li et al., 2021; Lu et al., 2021); conformal calibration of operators (Ma et al., 2024); residual-based conformal scores (Gopakumar et al., 2025); generative effective dynamics for storylines (Gao, Kaltenbach and Koumoutsakos, 2024) with switching to the full model (Kičić et al., 2023); prediction-powered inference (Angelopoulos et al., 2023)',
     'Goal-oriented normaliser of the score (a variant); a test of what a generative copy can certify (Section 4.2, Figure {{story}})'],
    ['Alarms (WP3)', 'Generalised Pareto extremes (A13–A14); union bound',
     'Online conformal calibration under arbitrary shift (Gibbs and Candès, 2024; Angelopoulos, Barber and Bates, 2024); guarantees by regime (Gibbs, Cherian and Candès, 2025); extreme conformal prediction (Pasche, Lam and Engelke, 2026); Learn then Test (Angelopoulos et al., 2025)',
     '—'],
    ['Verification (WP3, WP5)', 'Clopper–Pearson bound (Eq. [[cp]])',
     'Anytime-valid e-processes (Ramdas et al., 2023; Vovk and Wang, 2021; Arnold, Henzi and Ziegel, 2023)', '— (simulated for this project, Figure {{verify}})'],
    ['Network (WP4)', 'Bayesian linear design (Eq. [[sigma]]); worst case over a class of priors (Berger, 1994; Eq. [[robust]])',
     'Goal-oriented optimal design (Attia, Alexanderian and Saibaba, 2018); seismic velocity and fibre for groundwater (Clements and Denolle, 2018; Rodríguez Tribaldos and Ajo-Franklin, 2021)',
     '**C2: value of a sensor in years of certified safe operation** (Eqs. [[years]], [[mult]]; Figure {{sensors}})'],
    ['Operation (WP5)', 'Cost-loss value (Richardson, 2000); sharp-interface pumping limits (Strack, 1976; Mantoglou, 2003)',
     'Conformal decision theory (Lekeufack et al., 2024); adaptation tipping points and pathways (Kwadijk et al., 2010; Haasnoot et al., 2013)',
     '**C1: certified multi-hazard safe window, its closing sea level and closing year** (Eqs. [[window]]–[[mult]]; Figures {{window}}–{{closing}})'],
    ['Pumping tests (WP5)', 'Least squares; optimal design of experiments (Pukelsheim, 1993); self-normalised confidence sets (Abbasi-Yadkori, Pál and Szepesvári, 2011)',
     'Active identification of nonlinear dynamics with guarantees (Mania, Jordan and Recht, 2022) and of linear dynamics (Wagenmaker and Jamieson, 2020); safe exploration with learned models (Koller et al., 2018; Zimmer, Meister and Nguyen-Tuong, 2018); priors as classes (Gong and Meng, 2021) and as imaginary data from a model (Huang et al., 2020); reporting to readers with different priors (Andrews and Shapiro, 2021)',
     '**C3: safe, goal-oriented pumping tests valued in years, with the price of a wrong prior** (Eqs. [[ident]]–[[conflict]]; Figures {{active}}, {{prior}})'],
]


# ---------------------------------------------------------------------------------------------------- content
def blocks(W, V, A, ST, ST5, PR):
    """Blocks: ('h', t) ('h2', t) ('p', text) ('b', text) ('eq', key, tex) ('eqa', key, tex) ('table', hdr, rows, widths,
    size) ('img', key, width_cm) ('cap', text) ('pb',). Text: $inline math$, **bold**, [[key]] -> equation number,
    {{key}} -> figure or table number (in order of appearance), <<name>> -> value. A: method_active.json; ST, ST5:
    method_story.json with 100 and 500 paired storylines; PR: method_prior.json."""
    S = {s['sensor']: s for s in W['sensors']}
    sp, pp, gn, cr = S['Sentinel piezometer'], S['Port piezometer'], S['GNSS station at the port'], S['Two corner reflectors']
    pl = W['plans']
    fa = V['false_alarm']; en = V['events_needed']; up = V['zero_miss_upper']
    d25 = V['detect_0.25']; v03 = V['verify_p0.03']
    env = W['envelope']
    env_err = max(abs(e['first_order'] - e['exact']) for e in env)
    lin_rank = [s['sensor'] for s in sorted(W['sensors'], key=lambda s: -s['years_linear_median'])]
    ex_rank = [s['sensor'] for s in sorted(W['sensors'], key=lambda s: -s['years'])]
    same_rank = lin_rank == ex_rank
    n = lambda x, d=0: (str(int(x + 0.5)) if d == 0 else f'{x:.{d}f}')
    pc = lambda x, d=0: f'{100 * x:.{d}f}%'

    LEAD = ('CERTAIN-COAST builds one warning chain for three linked hazards from methods published at the research frontier '
            'in 2021–2026, and adds three contributions of its own that were derived and tested numerically before the project: '
            'a **certified safe operating window** for pumping and dewatering, with the sea level and the year at which it '
            'closes (C1, Section 7); the **value of a sensor in years of safe operation** (C2, Sections 6 and 7.4); and **safe, '
            'goal-oriented pumping tests** that move the certified boundary of the window towards the true one, valued in years '
            'in the same way, together with what a wrong prior costs them (C3, Sections 6, 7.6 and 7.7). The chain has six steps (Figure {{chain}}): observe what the warnings need '
            '(WP4), measure the moving coast (WP1), model the coast as one coupled system (WP2), copy the model fast with a '
            'certified error, for forecasts and for long storylines (WP2), certify each alarm (WP3), and operate, test, verify '
            'and hand over (WP5, WP6). Each step has a quantitative pass test and a fallback (Section 9). Section 10 states, '
            'step by step, which methods are standard, which are adopted from the frontier and which are new. The standard working '
            'equations (flow, transport, compaction, liquefaction triggering, extremes) are collected in Annex A, so the main text '
            'shows what goes beyond them.')

    B = [
        ('p', LEAD),
        ('img', 'chain', 17.0),
        ('cap', 'Figure {{chain}}. The CERTAIN-COAST method chain. Solid arrows: from data to bulletins. Dashed arrows: verified '
                'outcomes update the alarm margins, data from pumping tests update the model, and the safe window tells the '
                'network how many years each sensor is worth.'),

        ('h', '1. The three hazards as one system'),
        ('p', 'The three assets share two physical variables: the relative sea level $R_a(t)$ at asset $a$ and the water table '
              '$z_w(\\mathbf{x},t)$. Sea level enters the aquifer at its seaward boundary and sets how far seawater advances; the water '
              'table sets the effective stress in the sands and so their resistance to liquefaction; land subsidence raises the '
              'relative sea level at every asset. Pumping lowers the water table: it increases intrusion and, below the '
              'preconsolidation head, permanent subsidence, but it raises the factor of safety against liquefaction. No hazard can '
              'be managed alone. CERTAIN-COAST defines one indicator per hazard, oriented so that larger means more dangerous (Table {{tab_ind}}).'),
        ('cap', 'Table {{tab_ind}}. Hazard indicators, thresholds and lead times.'),
        ('table', ['Hazard (assets)', 'Indicator', 'Threshold τₖ', 'Lead time, cadence', 'What an alarm means'], INDICATORS,
         [2.9, 3.6, 3.4, 3.0, 4.1], 9.5),
        ('p', 'An alarm for hazard $k$ is missed when $I_k$ exceeds $\\tau_k$ within the lead time and no alarm was issued. The **miss '
              'rate** is the long-run fraction of issue times with a missed exceedance; it is the quantity certified in Section 5, and '
              'the miss rate per event is reported alongside it. Earthquakes are not forecast: the liquefaction alarm describes the '
              'current state, how the ground would respond if the design earthquake struck now, and that state changes with the water table.'),

        ('h', '2. Measuring the moving coast (WP1; T1.1–T1.4)'),
        ('p', '**State of the art.** Vertical land motion measured by InSAR changes coastal exposure assessments: along the US '
              'Atlantic coast, InSAR combined with 173 GNSS stations revealed widespread subsidence, a hidden vulnerability to '
              'sea-level rise (Ohenhen et al., 2023). CERTAIN-COAST applies this at the scale of single assets. Sentinel-1 ascending and '
              'descending time series from 2014 onwards give the vertical and east components of motion (Eq. [[los]]); a trajectory '
              'model separates trend, season, the 2019 coseismic step and the postseismic transient (Eq. [[traj]]); corner reflectors '
              'at the assets (T1.2) give stable radar targets on soft ground, and GNSS ties the solution to a global frame.'),
        ('p', '**Relative sea level at each asset.** The tide gauge records sea level $\\eta_{TG}(t)$ relative to its own benchmark, '
              'which also moves. The relative sea level at asset $a$ adds the differential land motion between the gauge and the asset; '
              'it is propagated with its full covariance, with a target vertical-velocity uncertainty of the order of 1–2 mm/yr:'),
        ('eq', 'rsl', 'R_a(t) = \\eta_{TG}(t) + u^{TG}_{z}(t) - u^{a}_{z}(t)'),
        ('p', '**Compaction and the head limit.** Elastic and inelastic compaction (Eq. [[comp]]) and the delayed drainage of clay '
              'interbeds (Eq. [[tau]]) are fitted to the InSAR and head records, following one-dimensional compaction models '
              'calibrated on long InSAR records, which showed that clays keep compacting for decades after heads stop falling '
              '(Lees et al., 2022). The output is the head limit $h_{pc}(\\mathbf{x})$ above which pumping causes no new permanent '
              'subsidence, a hard constraint of the safe window (Section 7).'),

        ('h', '3. One coupled model of the coast (WP2; T2.1–T2.3)'),
        ('p', 'The model couples variable-density flow (Eqs. [[darcy]]–[[mass]]), salt transport with memory in clays and lenses '
              '(Eq. [[salt]]), the sea as a moving boundary driven by the relative sea level (Eq. [[sea]]), the total water level at '
              'each asset (Eq. [[twl]]), compaction (Eq. [[comp]]) and liquefaction triggering with the water table taken from the '
              'flow model at every time step (Eqs. [[csr]]–[[fs]]).'),
        ('p', '**State of the art and where it stops.** Groundwater rise under sea-level rise is now recognised as a coastal hazard in '
              'its own right: it extends flooding inland (Befus et al., 2020) and raises liquefaction severity at sites with shallow '
              'water tables and artificial fill (Grant et al., 2021). Head-controlled coastal aquifers, such as drained lowlands, '
              'are far more sensitive to sea-level rise than flux-controlled ones (Werner and Simmons, 2009). What is missing is one '
              'model in which the same water table drives all three hazards, so that a pumping decision is checked against all of '
              'them at once: because $\\sigma\'_v$ grows as the water table falls, $\\partial FS/\\partial z_w > 0$, and the pumping '
              'that drives intrusion protects against liquefaction.'),
        ('p', '**Calibration and gradients (T2.3).** The parameters $\\boldsymbol{\\theta}$ (conductivity field, $S_{ke}$, $S_{kv}$, '
              'immobile porosity and $\\omega$, dispersivities, boundary fluxes and the stress exponent of Eq. [[dvv]]) are estimated '
              'jointly from heads, conductivity, chloride, InSAR and seismic velocity by an ensemble smoother with multiple data '
              'assimilation (Eq. [[esmda]]; Emerick and Reynolds, 2013). The model is written in differentiable form, so adjoint '
              'gradients of every indicator are available (Shen et al., 2023): they are used for calibration, for the error bound of '
              'Section 4, for network design (Section 6) and for the multiplier of the safe window (Section 7). The model passes when '
              'observations held out from calibration fall inside its 90% predictive intervals at close to the nominal rate.'),
        ('p', '**Priors that can be read and checked (T2.3).** Every calibration starts from a prior, and where data are few the '
              'prior decides part of the answer. The log-conductivity field gets a Matérn prior whose correlation length and '
              'standard deviation follow penalised-complexity priors, set from statements that an expert can read and dispute, '
              'for example the probability that the correlation length is shorter than a given distance (Simpson et al., 2017; '
              'Fuglstad et al., 2019). The modules of the model (flow and salt, compaction, liquefaction, seismic velocity) are '
              'joined by semi-modular inference, which tempers the influence of one module on the parameters it shares with the '
              'others, so that an empirical liquefaction relation or a mis-specified velocity–stress law cannot distort the '
              'hydraulic parameters (Carmona and Nicholls, 2020). After calibration the prior is checked against the data, by a '
              'prior-data conflict test (Evans and Moshonov, 2006) and by power-scaling the prior to see how far each hazard '
              'indicator and the closing year move (Kallioinen et al., 2024). The same check decides how far the prior of the '
              'pumping tests can be trusted (Section 7.7).'),

        ('h', '4. A fast copy of the model, with a certified error (T2.4)'),
        ('h2', '4.1 Forecasts: a neural operator with a certified error'),
        ('p', 'Warnings need thousands of model runs per day for storylines, pumping options and ensemble members. A neural operator '
              '(Li et al., 2021; Lu et al., 2021) $\\hat{I}_k(\\xi)$ is trained on runs of the coupled model, where $\\xi$ collects the '
              'forcing history, the pumping schedule and the parameters. **State of the art.** Conformal prediction now calibrates '
              'neural-operator outputs with finite-sample guarantees (Ma et al., 2024), and the residual of the governing equations at '
              'the surrogate solution can serve as the conformity score (Gopakumar et al., 2025). **What CERTAIN-COAST uses.** The '
              'score is normalised by a goal-oriented version of that residual, the dual-weighted residual $\\eta_k(\\xi)$, which '
              'weights the residual by the adjoint solution for the indicator $I_k$ (Becker and Rannacher, 2001), so the bound is '
              'tight where the surrogate is right about the quantity that triggers the alarm and wide where it is not. With '
              '$\\hat{q}_{1-\\delta}$ the conformal quantile of $|I_k - \\hat{I}_k|/\\eta_k$ on $n$ held-out runs of the full model:'),
        ('eq', 'cert', '\\Delta_k(\\xi) = \\hat{q}_{1-\\delta}\\,\\eta_k(\\xi), \\qquad \\Pr\\left[\\,|I_k(\\xi) - \\hat{I}_k(\\xi)| \\le \\Delta_k(\\xi)\\,\\right] \\ge 1 - \\delta'),
        ('p', 'The guarantee holds for any surrogate and requires only that new inputs are exchangeable with the held-out runs; '
              'forecasts whose $\\Delta_k$ is too large are recomputed with the full model on a reduced domain.'),

        ('h2', '4.2 Storylines: a generative copy, and what its statistics can certify'),
        ('p', '**State of the art.** Generative learning of effective dynamics (G-LED) forecasts the statistics of '
              'high-dimensional systems from runs of the full solver (Gao, Kaltenbach and Koumoutsakos, 2024). The state is '
              'downsampled to a coarse latent state, advanced by a multi-head auto-regressive attention model and mapped back '
              'to full resolution by a Bayesian diffusion model that works on batches of consecutive states and can take '
              'physical constraints as virtual observables. For a two-dimensional flow over a backward-facing step and a '
              'three-dimensional turbulent channel flow it reproduced the mean flow statistics of large-eddy simulations, '
              'about 5,000 and 73 times faster, respectively. The authors state its limits: the residuals of the constraints '
              'are minimised but not guaranteed to be zero, the size of the latent state is set in advance, and parametric '
              'systems are left to future work. Adaptive learning of effective dynamics switches online between a fast copy '
              'and the full solver, based on the accuracy and uncertainty of the copy (Kičić et al., 2023).'),
        ('p', '**What CERTAIN-COAST uses it for.** The safe window needs, for each future year, the probability that an '
              'indicator exceeds its threshold over storylines of sea-level rise, subsidence, droughts and pumping (Section 7). '
              'That is a statistic of many long runs, the task G-LED was built for, while the neural operator of Section 4.1 '
              'serves single forecasts. The copy is trained on runs of the coupled model; the storyline drivers and the '
              'calibrated parameters enter as conditioning inputs, the parametric extension that the authors list as future '
              'work and that T2.4 tests; and the virtual observables are the physical constraints of the coast: the seawater '
              'fraction stays between 0 and 1, the water and salt balances close, and the three hazards share one water table. '
              'Storylines on which the copy is uncertain are passed to the full model, as in adaptive learning of effective '
              'dynamics.'),
        ('p', '**What its statistics can certify (tested before the project).** A closing year is the first year in which the '
              'exceedance probability rises above $\\alpha$, so it is decided by rare events near the onset of intrusion, '
              'where a copy trained on today\'s states is least reliable. This was tested on the test system of Section 7.6 '
              '(weekly chloride driven by the head; droughts and wet years as an autoregressive head anomaly; relative '
              'sea-level rise of <<Lr>> ± <<Lrs>> mm/yr) over <<Lyr>> years under a fixed pumping plan, with two stand-in '
              'copies whose onset of intrusion is <<Lgo>>% or <<Lpo>>% weaker and whose flushing is <<Lgf>>% or <<Lpf>>% '
              'faster than in the full model: accurate in today\'s range, biased near the onset. The chloride limit is first '
              'exceeded in more than 5% of storylines in year <<Ltt>>. From <<LN>> runs of a copy alone the closing year came '
              'out as year <<Lcg>> (better copy) or <<Lcp>> (poorer copy), later than the truth in every draw: a copy that '
              'misses the onset promises years that do not exist. Prediction-powered inference (Angelopoulos et al., 2023) '
              'corrects the copy with $n$ storylines run with both models:'),
        ('eq', 'ppi', '\\hat{p}_k(t) = \\frac{1}{N}\\sum_{j=1}^{N}\\hat{Y}_k(t; \\tilde{\\xi}_j) - \\frac{1}{n}\\sum_{i=1}^{n}\\left[\\hat{Y}_k(t; \\xi_i) - Y_k(t; \\xi_i)\\right], \\qquad \\overline{p}_k(t) = \\hat{p}_k(t) + z_{1-\\delta}\\sqrt{\\frac{\\hat{\\sigma}^2_N}{N} + \\frac{\\hat{\\sigma}^2_n}{n}}'),
        ('p', 'where $Y_k(t;\\xi) = 1$ if the full model exceeds the threshold in year $t$ of storyline $\\xi$ and 0 otherwise, '
              '$\\hat{Y}_k$ is the same for the copy, $\\tilde{\\xi}_j$ are the $N$ storylines run with the copy alone, and '
              '$\\hat{\\sigma}^2_N$ and $\\hat{\\sigma}^2_n$ are the sample variances of the copy runs and of the corrections. '
              'The certified closing year is the first year with $\\overline{p}_k(t) > \\alpha$. Because the true closing year '
              'is one fixed year, a bound that is valid in that year makes the certified year no later than the truth with '
              'probability at least $1-\\delta$, without a correction over years. With <<Ln>> paired storylines '
              '(Figure {{story}}) the corrected bound gave year <<Lpg>> (better copy) or <<Lpp>> (poorer copy), against '
              'year <<Lfo>> from the same <<Ln>> full runs alone with the exact bound of Eq. [[cp]]. This gain rests on a '
              'normal approximation that fails for rare events: in the true closing year the bound lay below the true '
              'probability in <<Lucg>> (better copy) and <<Lucp>> (poorer copy) of the draws, instead of at most 5%. The '
              'certified year was still later than the truth in only <<Llg>> and <<Llp>> of the draws, because the true '
              'probability in that year (<<Lpt>>) lies above $\\alpha$, a margin that nothing guarantees. With <<Ln5>> paired '
              'storylines the shortfall shrank to <<Luc5>>, and the bound gave year <<Lp5g>> (better copy) and <<Lp5p>> '
              '(poorer copy) against <<Lf5>> from the full runs alone. An exact variant bounds the exceedance probability by the share of '
              'copy runs that exceed plus the share of paired storylines on which the full model exceeds and the copy does '
              'not, each with a Clopper–Pearson bound at $\\delta/2$. It held in at least <<Lexmin>> of the draws in every '
              'year, but it certified no more years than the full runs alone: year <<Lexg>> and <<Lex5g>> for the better copy '
              'with <<Ln>> and <<Ln5>> paired storylines, against <<Lfo>> and <<Lf5>>.'),
        ('p', '**Consequence for the design.** The generative copy is used where no certificate is needed: to run tens of '
              'thousands of storylines, to find the storylines and years near the closing point, and to choose on which of '
              'them the full model is run. Closing years are certified from full runs with the exact bound of Eq. [[cp]]; '
              'the prediction-powered value is reported beside them as the best estimate, not as the certificate (Table '
              '{{tab_checks}}). Whether a copy can add certified years with an exact guarantee is tested in T2.4 on the site '
              'model.'),
        ('img', 'story', 17.0),
        ('cap', 'Figure {{story}}. Certified storyline statistics from a generative copy, synthetic test. (a) Share of '
                'storylines with chloride above the limit in each year under a fixed pumping plan: full model (truth), the '
                'better copy alone, and the median 95% upper bounds from <<Ln>> full runs and from prediction-powered '
                'inference with <<LN>> copy runs and <<Ln>> paired storylines; a closing year is where a curve first rises '
                'above α = 5%. (b) Closing year from each method over <<Lrep>> repeated draws of the runs (median and '
                '5–95% range).'),

        ('h', '5. Certified alarms (WP3; T3.1–T3.5)'),
        ('h2', '5.1 The alarm rule'),
        ('p', 'Hazard $k$ is forecast at lead time $L_k$. The alarm fires when the forecast comes within a margin of the threshold. '
              'The margin has two parts: the certified surrogate error $\\Delta_k$ (Section 4) and the calibrated forecast error '
              '$\\gamma_k$, tracked online (Section 5.2), guaranteed in each regime and extended beyond the record (Section 5.3):'),
        ('eq', 'alarm', 'A_k(t) = \\mathbf{1}\\left\\{\\hat{I}_k(t + L_k) \\ge \\tau_k - m_k(t)\\right\\}, \\qquad m_k(t) = \\Delta_k(t) + \\gamma_k(t)'),
        ('h2', '5.2 Online calibration under distribution shift'),
        ('p', 'Conformal calibration assumes exchangeable data, but sea level, pumping and climate all trend. Online conformal methods '
              'drop that assumption: the margin rises after a miss and falls slightly otherwise, and the long-run miss rate stays at '
              'its target for any sequence of data (Gibbs and Candès, 2021). CERTAIN-COAST uses the two current refinements: step '
              'sizes chosen online among several candidates, so the margin adapts to how fast conditions change (Gibbs and Candès, '
              '2024), and decaying step sizes, which keep the long-run guarantee for arbitrary sequences and also converge to the '
              'correct quantile when conditions are stable (Angelopoulos, Barber and Bates, 2024). For a constant step $\\lambda$ the '
              'long-run error is bounded as shown, with $C_k$ depending on the range of the margin:'),
        ('eq', 'aci', '\\gamma_k(t+1) = \\gamma_k(t) + \\lambda_t\\,[\\,miss_k(t) - \\alpha_k\\,], \\qquad \\left|\\frac{1}{T}\\sum_{t=1}^{T} miss_k(t) - \\alpha_k\\right| \\le \\frac{C_k}{\\lambda\\,T}'),
        ('p', 'Outcomes arrive after the lead time; the update is applied with that delay.'),
        ('h2', '5.3 Guarantees by regime and beyond the record'),
        ('p', '**By regime.** A miss rate that is right on average can be wrong in droughts, in the storm season or after an '
              'earthquake, which is when it matters. Conformal prediction with conditional guarantees gives exact finite-sample '
              'coverage over every shift in a chosen class (Gibbs, Cherian and Candès, 2025). With the class spanned by the indicators '
              'of the regimes $G$ (drought, storm season, after an earthquake, each asset), the calibration of $\\gamma_k$ holds within '
              'each regime:'),
        ('eq', 'cond', '\\Pr\\left[\\,miss_k \\mid \\xi \\in G\\,\\right] \\le \\alpha_k \\quad \\text{for every regime } G'),
        ('p', '**Beyond the record.** When a certified rate concerns events rarer than the calibration record can resolve '
              '($\\alpha_k < 1/(n+1)$ for $n$ calibration cases), classical conformal margins become infinite. Extreme conformal '
              'prediction bridges extreme-value statistics and conformal prediction: it gives reliable intervals at such levels, can '
              'be built on any extreme quantile regression, has a weighted version for nonstationary data and was demonstrated on '
              'flood-risk forecasting (Pasche, Lam and Engelke, 2026). The margin then uses the peaks-over-threshold quantile of the '
              'calibration scores (Coles, 2001), with $n_u$ scores above the threshold $u_k$ and fitted scale $\\hat{\\sigma}_k$ and '
              'shape $\\hat{\\kappa}_k$:'),
        ('eq', 'ecp', '\\gamma_k = u_k + \\frac{\\hat{\\sigma}_k}{\\hat{\\kappa}_k}\\left[\\left(\\frac{n_u}{(n+1)\\,\\alpha_k}\\right)^{\\hat{\\kappa}_k} - 1\\right]'),
        ('p', '**Storylines test the extrapolation; they do not replace it.** Droughts deeper than any recorded, compound storm and '
              'high tide, a 2019-type earthquake at a high water table and increased pumping are run through the coupled model. If a '
              'storyline exceeds the extrapolated margin, the margin is widened and the case is reported.'),
        ('h2', '5.4 Joint guarantee and allocation of tolerances'),
        ('p', 'The three alarms share inputs, so their misses are dependent. The probability that any of them is missed is bounded '
              'by the sum of the tolerances, and the tolerances are allocated where tightening them costs least in false alarms '
              '(FAR), weighted by consequence $c_k$, within caps $\\alpha_k^{max}$ agreed with the operators:'),
        ('eq', 'union', '\\Pr\\left(\\bigcup_k miss_k\\right) \\le \\sum_k \\alpha_k \\le \\overline{\\alpha}'),
        ('eq', 'alloc', '\\min_{\\alpha_1, \\dots, \\alpha_K} \\sum_k c_k\\,FAR_k(\\alpha_k) \\quad s.t. \\quad \\sum_k \\alpha_k \\le \\overline{\\alpha}, \\;\\; \\alpha_k \\le \\alpha_k^{max} \\quad \\Rightarrow \\quad c_k\\,FAR\'_k(\\alpha^{*}_k) = -\\mu_\\alpha'),
        ('p', 'At the optimum the consequence-weighted marginal false-alarm cost is equal across hazards ($\\mu_\\alpha$ is the '
              'multiplier of the budget). The margins are then calibrated together by Learn then Test (Angelopoulos et al., 2025): '
              'each candidate setting $\\nu$ of the margin multipliers is a hypothesis that some miss rate exceeds its target, tested '
              'on the calibration data with family-wise error control; among the settings that pass, the one with the least '
              'consequence-weighted false alarms is used, and every certified rate holds at once with probability at least $1-\\beta$:'),
        ('eq', 'ltt', '\\Pr\\left[\\,\\text{risk}_k(\\hat{\\nu}) \\le \\alpha_k \\;\\text{ for all } k\\,\\right] \\ge 1 - \\beta'),
        ('p', 'Where the loss is graded rather than miss or no miss, conformal risk control bounds its expected value (Angelopoulos, '
              'Bates, Fisch, Lei and Schuster, 2024). The joint miss rate is also tracked directly with Eq. [[aci]] applied to the '
              'event "any alarm missed".'),
        ('h2', '5.5 Extremes on a sinking coast'),
        ('p', 'Still-water extremes follow a generalised Pareto distribution whose threshold moves with the relative sea level of '
              'Section 2 (Eqs. [[gpd]]–[[retl]]), so land motion from InSAR enters the return levels with its uncertainty. Where storm '
              'covariates such as wind, pressure and waves matter, the conditional tail is estimated with neural extreme quantile '
              'regression, which was developed for flood-risk forecasting (Pasche and Engelke, 2024). These distributions generate '
              'the storm storylines and the flood constraint of the safe window (Section 7).'),
        ('h2', '5.6 Back-testing (T3.4)'),
        ('p', 'The full chain is replayed over the InSAR era with the system frozen at each issue time, so no later data are used, '
              'and on storylines beyond the record. Miss and false-alarm rates are reported overall and in each regime, with '
              'Clopper–Pearson intervals and block resampling for serial dependence. In preparatory synthetic tests on a coupled '
              'variable-density model, an extreme-aware margin kept the share of seasons above the chloride limit at 4–9% across '
              'drought, human-feedback and compound storylines, where a static alarm allowed 13–21%.'),

        ('h2', '5.7 How many events are needed to verify a miss rate'),
        ('p', '**One planned look.** If $x$ of $n$ independent exceedance events were missed, the one-sided Clopper–Pearson upper '
              'bound on the miss rate at confidence $1-\\beta$ is the Beta quantile below; with no miss it has a closed form. The rate '
              '$\\alpha_k$ is verified when the bound falls to $\\alpha_k$ or below:'),
        ('eq', 'cp', '\\overline{p}_k(x, n) = \\text{Beta}^{-1}\\left(1-\\beta;\\; x+1,\\; n-x\\right), \\qquad \\overline{p}_k(0, n) = 1 - \\beta^{1/n}'),
        ('p', 'At 95% confidence, verifying $\\alpha_k = 10\\%$ needs 29 events with no miss, 46 with one or 61 with two; verifying '
              '$\\alpha_k = 5\\%$ needs 59, 93 or 124 (Figure {{verify}}a). Back-testing over the record since 2014 and on storylines (T3.4) is '
              'one pre-registered look, to which this bound applies; the number of events per alarm is counted first.'),
        ('p', '**Looking at every event.** The live ledger is published every quarter (Dissemination Plan), so each miss rate is looked '
              'at many times, and a fixed-sample bound recomputed at every look loses its guarantee. In a simulation of six calibrated '
              'alarms (miss rate exactly 10%) over 100 events each, recomputing the 95% bound after every event flagged at least one '
              'alarm as broken in <<fa_every>> of runs, and every tenth event in <<fa_q>> (Figure {{verify}}b). CERTAIN-COAST therefore monitors '
              'with test supermartingales (e-processes), the basis of safe anytime-valid inference (Ramdas et al., 2023), as used for '
              'sequential tests of forecast calibration (Arnold, Henzi and Ziegel, 2023). For alarm $k$, with $x_i = 1$ if the $i$-th '
              'event was missed and alternatives $q_j$ weighted by $\\pi_j$:'),
        ('eq', 'eproc', 'E_k(n) = \\sum_j \\pi_j \\prod_{i=1}^{n}\\left(\\frac{q_j}{\\alpha_k}\\right)^{x_i}\\left(\\frac{1-q_j}{1-\\alpha_k}\\right)^{1-x_i}, \\qquad \\Pr\\left(E_k(n) \\ge 1/\\beta \\;\\text{ for some } n\\right) \\le \\beta'),
        ('p', 'With alternatives above $\\alpha_k$, $E_k$ grows when the alarm misses more often than certified; when the true rate is '
              'at or below $\\alpha_k$ it is a nonnegative supermartingale, so by Ville\'s inequality (Ville, 1939) the chance that it '
              'ever reaches $1/\\beta$ is at most $\\beta$, however often it is checked. The average of the alarms\' e-processes is '
              'again one under any dependence between the alarms (Vovk and Wang, 2021), so one global check covers them all. With '
              'alternatives below $\\alpha_k$ the same construction verifies a good alarm.'),
        ('p', 'In the simulation the e-process flagged a calibrated alarm in <<fa_e>> of runs (at most 5% is guaranteed) and detected '
              'an alarm whose miss rate had risen to 25% in <<d25p>> of runs within 100 events (median <<d25m>> events). Anytime '
              'validity has a price: verifying $\\alpha_k = 10\\%$ needs <<e10>> events with no, one or two misses, against 29, 46 and '
              '61 for one planned look, and an alarm whose true miss rate is 3% was verified within 100 events in <<v03>> of runs. The '
              'ledger therefore publishes the anytime-valid bound (with no miss: <<u29>> after 29 events, <<u60>> after 60), '
              'verification rests mainly on back-testing and storylines, and the live year is a continuous consistency check: when '
              '$E_k$ reaches $1/\\beta$, the review of R15 and a recalibration of the margin are triggered.'),
        ('img', 'verify', 17.0),
        ('cap', 'Figure {{verify}}. (a) Upper 95% Clopper–Pearson bound on the miss rate against the number of exceedance events, for zero, '
                'one and two misses; dots: the number of events at which a 5% or 10% rate is verified with one planned look. '
                '(b) Share of simulated runs in which at least one of six calibrated alarms is wrongly flagged when the bound is '
                'recomputed often, and with the anytime-valid e-process (Eq. [[eproc]]).'),

        ('h', '6. A monitoring network designed for the warnings (WP4; T4.1, T4.4)'),
        ('p', '**Goal-oriented design.** Bayesian optimal experimental design can choose sensors to minimise the posterior '
              'uncertainty of a prediction rather than of all parameters (Attia, Alexanderian and Saibaba, 2018). In CERTAIN-COAST '
              'the predictions are the warning indicators. Candidate sensors $\\mathcal{C}$ (piezometers with conductivity loggers, '
              'chloride sampling points, GNSS, corner reflectors, seismic stations and nodes, fibre-optic sensing) are ranked by how '
              'much they narrow the forecast of each indicator: a narrower forecast needs a smaller margin for the same miss rate, '
              'and so gives fewer false alarms. With a linearised model, the forecast spread of indicator $k$ after observing set $S$ '
              'uses the adjoint gradient $\\mathbf{g}_k = \\partial I_k/\\partial\\boldsymbol{\\theta}$, the prior covariance '
              '$\\boldsymbol{\\Gamma}_{pr}$, the sensor Jacobian $\\mathbf{J}_S$ and the noise covariance $\\boldsymbol{\\Gamma}_S$; the '
              'network maximises the consequence-weighted reduction of margins within the budget $B$:'),
        ('eq', 'sigma', '\\sigma_k^2(S) = \\mathbf{g}_k^{\\top}\\left(\\boldsymbol{\\Gamma}_{pr}^{-1} + \\mathbf{J}_S^{\\top}\\boldsymbol{\\Gamma}_S^{-1}\\mathbf{J}_S\\right)^{-1}\\mathbf{g}_k'),
        ('eq', 'design', '\\max_{S \\subseteq \\mathcal{C}} \\sum_k w_k\\,z_{1-\\alpha_k}\\left[\\sigma_k(\\emptyset) - \\sigma_k(S)\\right] \\quad s.t. \\quad \\sum_{s \\in S} cost_s \\le B'),
        ('p', '**A second criterion: years of safe operation (new, C2).** The criterion above values a sensor by how much it narrows '
              'today\'s forecasts. The safe window of Section 7 adds the horizon that matters for adaptation: a sensor is also worth '
              'the years by which it delays the certified closing of the window. The value is computed before the sensor is '
              'installed, by averaging over the data $y_s$ it could return (preposterior analysis), and its first-order estimate '
              'needs only the multiplier of the closing constraint (Eq. [[mult]]), so all candidates can be ranked from one '
              'computation of the window:'),
        ('eq', 'years', '\\Delta t_s = \\text{E}_{y_s}\\left[\\,t^{*}_{\\alpha}(y_s)\\,\\right] - t^{*}_{\\alpha} \\;\\approx\\; \\mu\\;\\text{E}_{y_s}\\left[\\,\\Delta B_s - \\Delta A_s\\,\\right]'),
        ('p', 'Data worth in groundwater management has been measured in money or in safe production (Wagner, 1999), signals for '
              'adaptation have been designed for timely detection (Haasnoot, van \'t Klooster and van Alphen, 2018), and dual '
              'variables of chance-constrained problems have been read as the value of data in power systems (Mieth, Morales and '
              'Poor, 2025). In our search we found no work that values a sensor by the years it adds before an adaptation tipping '
              'point. In the test case the two criteria disagree where it matters (Section 7.4), so both are used: the first for '
              'the alarms, the second for the adaptation horizon. The selection is greedy by benefit per cost, checked against '
              'exhaustive search on small candidate sets, and repeated in Year 2 with the calibrated model.'),
        ('p', '**A ranking that does not hinge on one prior (T4.1).** The years a sensor adds come from a preposterior analysis, '
              'so they depend on the prior. Before the network is fixed, the ranking is recomputed over a class of priors: the '
              'hyperparameters $\\psi$ (correlation length, standard deviation, rates of subsidence and sea-level rise) are drawn '
              'from their penalised-complexity priors $\\pi$, and each sensor is valued by its worst mean over all distributions '
              'within a Kullback–Leibler distance $\\varepsilon$ of $\\pi$. The worst case has a one-dimensional dual form; '
              '$\\varepsilon = 0$ gives the Bayesian average and a large $\\varepsilon$ the worst case over the class (Berger, 1994):'),
        ('eq', 'robust', '\\Delta t^{rob}_s = \\text{inf}_{P:\\; \\text{KL}(P \\,\\|\\, \\pi) \\le \\varepsilon} \\text{E}_{\\psi \\sim P}\\left[\\Delta t_s(\\psi)\\right] = \\text{sup}_{\\tau > 0}\\left\\{-\\tau \\ln \\text{E}_{\\psi \\sim \\pi}\\left[e^{-\\Delta t_s(\\psi)/\\tau}\\right] - \\tau\\,\\varepsilon\\right\\}'),
        ('p', 'This step is applied in T4.1 with the calibrated model; it was not part of the preparatory tests.'),
        ('p', '**A third criterion: tests that move the certified boundary (new, C3).** Sensors observe; pumping tests excite. '
              'Routine operation keeps the water table in a narrow band, so the records say little about how chloride '
              'responds near the onset of intrusion, and that response sets the certified boundary of the window, the most '
              'dewatering $B$ that the wellfield tolerates (Section 7.2). A planned test lowers the water table for a few '
              'weeks, records the chloride response and recovers. Near the onset the response is nonlinear; it is written '
              'with features $\\boldsymbol{\\phi}$ that are linear in the unknown coefficients, with hinge functions of the '
              'head at fixed levels $k_1, \\dots, k_m$:'),
        ('eq', 'ident', 'c_{t+1} = \\boldsymbol{\\theta}^{\\top}\\boldsymbol{\\phi}(c_t, h_t) + w_t, \\qquad \\boldsymbol{\\phi}(c, h) = \\left[\\,c,\\; 1,\\; (k_1 - h)^{+},\\; \\dots,\\; (k_m - h)^{+}\\right]^{\\top}'),
        ('p', 'where $c_t$ is the weekly chloride at the wellfield, $h_t$ the head at the sentinel piezometer and $w_t$ noise '
              'of scale $\\sigma$. The coefficients are estimated by ridge regression around the prior from the calibrated '
              'model, with prior precision $\\boldsymbol{\\Lambda}$ and design matrix $\\mathbf{V}_t$, the prior precision '
              'plus the sum of $\\boldsymbol{\\phi}_s\\boldsymbol{\\phi}_s^{\\top}$ over past weeks. If the prior is wrong by at most $S$ in the '
              '$\\boldsymbol{\\Lambda}$-norm, the self-normalised bound of Abbasi-Yadkori, Pál and Szepesvári (2011) holds '
              'for all weeks at once, so it can be checked after every week of a test:'),
        ('eq', 'conf', '\\left\\|\\hat{\\boldsymbol{\\theta}}_t - \\boldsymbol{\\theta}\\right\\|_{\\mathbf{V}_t} \\le \\beta_t = \\sigma\\sqrt{2\\ln\\frac{\\det(\\mathbf{V}_t)^{1/2}}{\\delta\\,\\det(\\boldsymbol{\\Lambda})^{1/2}}} + S \\quad \\text{for all } t \\text{ with probability at least } 1 - \\delta'),
        ('p', 'The boundary is certified at the heads where the chloride level $L$ that the wellfield tolerates cannot be '
              'exceeded: started at $L$, next week\'s chloride stays at or below $L$ for every coefficient vector in the '
              'confidence set, that is, its upper confidence bound is at most $L$. The lowest head from which this holds at '
              'all higher heads is the certified boundary; it fixes $B$ and, with it, the closing year of Eq. [[closing]]:'),
        ('eq', 'inv', 'h^{cert}_t = \\min\\left\\{\\,h :\\; \\hat{\\boldsymbol{\\theta}}_t^{\\top}\\boldsymbol{\\phi}(L, h\') + \\beta_t\\left\\|\\boldsymbol{\\phi}(L, h\')\\right\\|_{\\mathbf{V}_t^{-1}} \\le L \\;\\;\\text{for all } h\' \\ge h\\right\\}'),
        ('p', 'A test $u$ (extra pumping and dewatering and its duration, from a set $\\mathcal{U}$ that the utility accepts) '
              'is chosen to maximise the certified closing year predicted with the current estimate and the smaller '
              'confidence set that its data would give, subject to the upper confidence bound of chloride, $\\overline{c}_s(u)$, '
              'staying below a test limit $c_{test}$ in every week $s$ of the test and the recovery:'),
        ('eq', 'select', 'u^{*} = \\arg\\max_{u \\in \\mathcal{U}}\\; \\hat{t}^{*}_{\\alpha}\\left(\\mathbf{V}_t + \\sum_{s \\in u}\\boldsymbol{\\phi}_s\\boldsymbol{\\phi}_s^{\\top}\\right) \\quad s.t. \\quad \\overline{c}_s(u) \\le c_{test} \\;\\;\\text{for every week } s \\text{ of } u'),
        ('p', '**State of the art and what is new.** Active identification chooses the inputs of a system so that its model '
              'is learned fastest. For nonlinear systems whose dynamics are linear in a known feature map, Mania, Jordan and '
              'Recht (2022) steer the system towards the least explored direction of the feature space, the eigenvector of '
              'the smallest eigenvalue of the design matrix (E-optimal design; Pukelsheim, 1993), or towards features of '
              'high uncertainty when that direction cannot be reached, and prove estimation at a parametric rate; in one of '
              'their examples, random inputs reach the region that must be explored only with a probability that is '
              'exponentially small in the dimension. For linear systems, E-optimal inputs estimate the dynamics at an '
              'optimal rate (Wagenmaker and Jamieson, 2020), and safe exploration learns a model while keeping the system '
              'within limits with high probability (Koller et al., 2018; Zimmer, Meister and Nguyen-Tuong, 2018). Mania et '
              'al. list as open whether a system can be estimated only in the directions that matter for prediction or '
              'control. CERTAIN-COAST takes this route for one decision: tests are chosen for the years they add to the '
              'certified closing of the window, not for the accuracy of all coefficients, and only tests whose chloride '
              'stays below the test limit with high probability are allowed. In our search we found no pumping-test design '
              'that does this with a finite-sample guarantee, or that values a test in years of safe operation.'),
        ('p', 'With probability at least $1-\\delta$ the certified boundary is on the safe side of the true one in every '
              'week. The tests stay below the test limit with high probability: the check carries the upper confidence '
              'bound along the planned test, with a margin for the head forecast and an allowance for the chloride noise '
              'that accumulates during a test. As in Mania et al. (2022), the guarantee assumes that the true response lies '
              'in the model class, which T5.3 checks on weeks held out from the fit. A test is valued in years through '
              'Eq. [[mult]], as a sensor is; the preparatory test is in Section 7.6.'),
        ('p', '**The prior of the tests.** The guarantee also assumes that the prior from the calibrated model is wrong by at '
              'most $S$ in the $\\boldsymbol{\\Lambda}$-norm. That prior can be read as imaginary data from the calibrated model '
              'with a set weight, as in catalytic priors (Huang et al., 2020), and, like any prior, it is better treated as a '
              'class than as a point (Berger, 1994; Gong and Meng, 2021). CERTAIN-COAST sets $S$ from the spread of the calibrated ensemble, states it as a readable bound and checks '
              'it during the campaign against the confidence set $\\mathcal{C}^{phys}_t$ of Eq. [[conf]] built with a wide prior '
              'that only encodes a physical box of admissible coefficients. The prior is in conflict with the data when its '
              'ball no longer meets that set; with a right prior this happens with probability at most $\\delta$:'),
        ('eq', 'conflict', '\\min_{\\boldsymbol{\\theta} \\in \\mathcal{C}^{phys}_t}\\left\\|\\boldsymbol{\\theta} - \\boldsymbol{\\theta}_0\\right\\|_{\\boldsymbol{\\Lambda}} > S'),
        ('p', 'Section 7.7 values in years both the prior and the protection against it being wrong, and shows what '
              'the test of Eq. [[conflict]] can and cannot detect.'),
        ('p', '**Seismic velocity as a water-table gauge (T4.4).** Ambient seismic noise tracks groundwater levels (Clements and '
              'Denolle, 2018), also on unused telecommunication fibre with distributed acoustic sensing (Rodríguez Tribaldos and '
              'Ajo-Franklin, 2021). A uniform relative change in velocity stretches the noise correlations in time (Sens-Schönfelder '
              'and Wegler, 2006); lowering the water table raises the effective stress, and grain-contact theory gives the physical '
              'prior of Eq. [[dvv]] for the calibration against piezometers. Once calibrated, velocity changes measure the water table '
              'between wells at the port and landfall, and a drop after an earthquake measures the softening of the ground.'),

        ('h', '7. Live operation, the certified safe window and the pumping rule (WP5)'),
        ('h2', '7.1 Operational cycle (T5.1, T5.2)'),
        ('p', 'Data are assimilated, indicators forecast and margins applied at the cadence of each hazard (Table {{tab_ind}}). Each bulletin '
              'states, per asset, the forecast, the margin, the alarm state, the certified miss rate and the distance to the closing '
              'of the safe window, and is logged with its inputs and code version so that it can be reproduced and audited. Outcomes '
              'are recorded when known and feed the margin update of Eq. [[aci]] and the e-processes of Eq. [[eproc]].'),
        ('h2', '7.2 The certified safe operating window (new, C1)'),
        ('p', 'Pumping moves the hazards in opposite directions, and sea-level rise and subsidence tighten all of them. CERTAIN-COAST '
              'therefore computes, at each bulletin and over the adaptation horizon, the set of operating decisions $u$ (wellfield '
              'pumping $Q_w$, port dewatering $Q_d$) that keeps every hazard within its certified limit while the wellfield meets the '
              'demand $D$ and no new permanent subsidence occurs:'),
        ('eq', 'window', 'W_{\\alpha}(R) = \\left\\{\\,u :\\; Q_w \\ge D,\\;\\; \\Pr_{\\theta}\\left[I_k(u, R; \\theta) > \\tau_k\\right] \\le \\alpha_k \\;\\, (k = 1, 2, 3),\\;\\; h(\\mathbf{x}, u, R) \\ge h_{pc}(\\mathbf{x})\\,\\right\\}'),
        ('p', 'Probabilities are taken over the calibrated parameter ensemble of Section 3, with the certified errors of Sections 4 '
              'and 5 added to each indicator. As the relative sea level $R$ rises the window shrinks. It closes at the certified '
              'closing sea level and, with the uncertain rate of relative sea-level rise $R(t)$, in the certified closing year:'),
        ('eq', 'closing', 'R^{*}_{\\alpha} = \\text{largest } R \\text{ with } W_{\\alpha}(R) \\neq \\emptyset, \\qquad t^{*}_{\\alpha} = \\text{first } t \\text{ with } W_{\\alpha}(R(t)) = \\emptyset'),
        ('p', 'The closing level is a certified, multi-hazard version of an adaptation tipping point, the moment from which a strategy '
              'no longer meets its objectives and another is needed (Kwadijk et al., 2010), as used in adaptive policy pathways '
              '(Haasnoot et al., 2013). It tells the operators how much rise the coast can absorb before no pumping and dewatering '
              'plan is safe for all three hazards, and which hazard closes the window. Single-hazard tipping points for seawater '
              'intrusion under rising sea level (Mazi, Koussis and Destouni, 2013) and ensemble-based pumping optimisation under '
              'sea-level rise (Coulon et al., 2024) exist; in our search we found no study that derives a joint intrusion, '
              'liquefaction and subsidence operating window with certified margins, or the sea level at which it closes.'),
        ('p', '**The multiplier.** At the closing point the least dewatering that keeps liquefaction within its limit, $A(t)$, meets '
              'the most dewatering the wellfield tolerates before seawater reaches it, $B(t)$, both at the certified levels. Writing '
              'the closing year as the solution of $\\max t$ subject to $A(t) \\le Q_d \\le B(t)$, the Karush–Kuhn–Tucker conditions '
              'give one multiplier $\\mu$ for both constraints, and by the envelope theorem a change of either margin moves the '
              'closing year by $\\mu$ times the change:'),
        ('eq', 'mult', '\\mu = -\\left[\\frac{d\\,(B - A)}{dt}\\right]^{-1}_{t = t^{*}_{\\alpha}}, \\qquad \\Delta t^{*}_{\\alpha} \\approx \\mu\\,(\\Delta B - \\Delta A)'),
        ('p', 'This turns any reduction of a margin, by a sensor, a better model, a tighter calibration or a pumping test '
              '(Section 7.6), into years.'),
        ('p', '**The pumping rule (T5.3).** Within the window, the utility\'s schedule $\\mathbf{Q}(t)$ supplies as much water as '
              'possible:'),
        ('eq', 'rule', '\\max_{\\mathbf{Q}(\\cdot)} \\sum_j \\int_0^{T} Q_j(t)\\,dt \\quad s.t. \\quad \\left(Q_w(t), Q_d(t)\\right) \\in W_{\\alpha}\\left(R(t)\\right) \\;\\; \\forall t'),
        ('p', 'The liquefaction constraint is also checked for a sudden pumping stop, after which the water table recovers and the '
              'factor of safety falls: the rule must stay safe in both directions. The problem is solved with the surrogate and the '
              'result is checked with the full model before it is proposed to the utility. Close to the closing point, live decisions '
              'are additionally safeguarded by conformal decision theory, which calibrates the decision itself so that its long-run '
              'risk stays below a set level without assumptions on the data (Lekeufack et al., 2024).'),

        ('h2', '7.3 Preliminary test on a synthetic coastal transect'),
        ('p', 'The window was tested before the project on a synthetic transect with the three hazards of Durrës but illustrative '
              'parameter values, not site values: an unconfined aquifer about 40 m deep; a wellfield 2 km from the shore that must '
              'supply 15,000 m³/d; port dewatering 600 m from the shore; an inland water level held fixed relative to the land 6 km '
              'inland (head-controlled); seawater intrusion from the sharp-interface single potential with image wells (Strack, '
              '1976; Eqs. [[strack]]–[[qhead]]); the liquefaction potential index at the port under a design shaking of 0.25 g and '
              'magnitude 6.5 (Eqs. [[csr]]–[[fs]]); and the 100-year still water level against the quay crest. Uncertain inputs are '
              'the conductivity, aquifer depth, inland level, cone resistance, the 100-year level and the rates of sea-level rise '
              '(4 ± 1 mm/yr) and land subsidence (6 ± 3 mm/yr); <<N>> ensemble members; $\\alpha_k$ = 5% for each hazard.'),
        ('b', '**The intrusion criterion is exact and cheap.** With the dewatering on the flow line of the wellfield, the stagnation '
              'points follow from one quadratic (Eq. [[qhead]]). In <<sc_n>> random cases the closed-form criterion agreed with a '
              'brute-force connectivity check on a fine grid in <<sc_a>>.'),
        ('b', '**The window shrinks and closes** (Figure {{window}}). The certified window closes at a relative sea level of <<Rs>> m (<<Rm>> m '
              'without margins). With the uncertain rate of relative sea-level rise (<<r5>>–<<r95>> mm/yr, 5–95%), the certified '
              'closing year is <<tc>> years from now (<<tm>> years without margins). In both cases the window is closed by the '
              'conflict between the two groundwater hazards: the dewatering that liquefaction needs exceeds what the wellfield '
              'tolerates.'),
        ('b', '**Plans that watch one hazard believe they have decades more** (Figure {{closing}}b). A plan that watches flooding alone believes '
              'the port is safe for <<pf>> years, and one that manages liquefaction by dewatering alone for <<plq>> years; managing '
              'intrusion alone gives <<psw>> years, but without dewatering liquefaction under the design shaking is no longer within '
              'its certified limit after <<tl0>> years. Only the joint window gives the true horizon: <<tc>> years.'),
        ('b', '**Uncertainty, not only sea level, closes the window.** The margins cost <<cost>> years against the window without '
              'margins; part of them can be bought back with sensors (Section 7.4).'),
        ('img', 'window', 17.0),
        ('cap', 'Figure {{window}}. The certified safe window (green) in the plane of wellfield pumping and port dewatering on the synthetic '
                'transect, today and at two higher relative sea levels. Red: the most dewatering before seawater reaches the '
                'wellfield (95%); blue: the least dewatering that keeps liquefaction within its limit (95%); dashed: the same limits '
                'without margins; dotted: the water demand.'),
        ('img', 'closing', 17.0),
        ('cap', 'Figure {{closing}}. (a) The certified bounds on port dewatering against time (solid; dashed without margins): the window is '
                'the band between them and closes where they cross. (b) Years of operation that single-hazard plans believe safe; '
                'hatched: the years they believe safe that are not.'),

        ('h2', '7.4 What a sensor is worth in years (new, C2)'),
        ('p', 'Four sensors from the Budget were valued on the same transect by preposterior analysis over <<M>> simulated outcomes '
              'each (Table {{tab_sens}}, Figure {{sensors}}): a piezometer at the port and a sentinel piezometer between the wellfield and the sea, each with '
              'borehole, logger and telemetry; a GNSS station at the port; and two corner reflectors for InSAR.'),
        ('cap', 'Table {{tab_sens}}. Value of four sensors on the synthetic transect: years added before the certified window closes, against '
                'the reduction of today\'s forecast spread (classical criterion). Costs from the Budget lines.'),
        ('sensors',),
        ('b', '**The two criteria disagree where it matters.** The GNSS station and the corner reflectors narrow none of today\'s '
              'forecasts, so the classical criterion values them at zero; they add <<gn>> and <<cr>> years of certified safe '
              'operation, because they narrow the rate at which the window approaches. The corner reflectors give <<crk>> years per '
              '€10,000, the GNSS station <<gnk>>.'),
        ('b', '**The sentinel piezometer is worth most on both criteria** (+<<sp>> years; <<spr>> narrower forecasts today), because it '
              'constrains the regional flow that holds seawater back from the wellfield.'),
        ('b', '**The multiplier is a usable shortcut.** Shifting one margin by ±100 to ±300 m³/d moved the closing year as Eq. [[mult]] '
              'predicts to within <<envr>> years. For the sensors, the first-order estimate <<rank>> and matched their median outcome '
              'to within <<medr>> years, but it understates the mean value of the GNSS station and the corner reflectors, which comes '
              'from occasional outcomes that reveal a slow subsidence rate. It is used to screen candidates; the preferred ones are '
              'recomputed exactly.'),
        ('img', 'sensors', 17.0),
        ('cap', 'Figure {{sensors}}. (a) Years of certified safe operation added by each sensor (preposterior mean ± 2 standard errors) and its '
                'cost. (b) Reduction of the spread of today\'s forecasts of the port water-table depth and the intrusion margin, the '
                'classical criterion.'),

        ('h2', '7.5 Post-event protocol and value of the warning for each user (T5.4; V1)'),
        ('p', '**Post-event protocol (T5.4).** When an earthquake, ground shaking or water level exceeds the triggers agreed with '
              'civil protection, heads, conductivity, chloride, GNSS and seismic velocity are measured within days, the next '
              'Sentinel-1 acquisitions are processed with priority, the model is updated, the alarms and the window are recomputed, '
              'and the event joins the back-testing record.'),
        ('p', '**Value of the warning for each user (V1; T3.1, D5.1).** In the cost-loss model of forecast value (Murphy, 1977; '
              'Richardson, 2000), a user who can act at cost $C$ to avoid a loss $L$ gains relative value $V$ from a warning with hit '
              'rate $H$ and false-alarm rate $F$ for an event of base rate $s$. Because $1-H \\le \\alpha_k$ is certified, the value has '
              'a guaranteed lower bound for every cost-loss ratio $r = C/L$, a direct corollary of the cost-loss model; the ratios are '
              'agreed with each operator in T3.1 and the bounds reported in D5.1:'),
        ('eq', 'vmin', 'V_k \\;\\ge\\; 1 - \\frac{r\\,F_k\\,(1-s_k) + \\alpha_k\\,s_k\\,(1-r)}{\\text{min}(r,\\,s_k) - r\\,s_k}'),

        ('h2', '7.6 What a pumping test is worth in years (new, C3)'),
        ('p', 'The safe tests of Section 6 were simulated before the project on a test system with illustrative values, not '
              'site values. The head at a sentinel piezometer between the wellfield and the sea falls with wellfield pumping '
              '(at least the demand of <<aD>> m³/d), port dewatering, the dry season and sea-level rise; weekly chloride at '
              'the wellfield (index 1 = 250 mg/L) rises once that head falls below 1.0 m and faster below 0.8 m, which puts '
              'the true boundary at <<ahc>> m. The prior from the calibrated model is deliberately wrong: it places the onset '
              'at 1.2 m and makes the response below 1.0 m and 0.8 m weaker. After <<ahy>> years of routine records, a '
              'campaign of <<acw>> weeks chooses tests of 2 to 8 weeks, each followed by <<arw>> weeks of recovery, from '
              '<<anc>> combinations of wellfield pumping (<<aqw0>>–<<aqw1>> m³/d), port dewatering (<<aqd0>>–<<aqd1>> m³/d) '
              'and duration, with a test limit of <<act>> mg/L and $\\delta$ = 5%. Five strategies were compared on the same '
              '<<anr>> histories (Figure {{active}}). Before the campaign the certified closing year is <<atb>> years; the '
              'true one is <<att>> years.'),
        ('b', '**Routine operation and random perturbations certify little:** <<atr>> and <<atrd>> years after the campaign.'),
        ('b', '**Unconstrained E-optimal tests certify many years, but unsafely.** The planner in the spirit of Mania et al. '
              '(2022) reached <<ate>> years, but chloride passed the test limit in every run and 250 mg/L in <<atel>> of the '
              'runs, as it drove the head down to <<ateh>> m (median), far below the true boundary.'),
        ('b', '**The safety filter removes the exceedances at almost no cost in years.** With the filter the E-optimal '
              'planner reached <<ates>> years, with no run above the test limit. The least explored directions are the '
              'deepest hinges, which no safe test can reach, so every safe test left the smallest eigenvalue unchanged; the '
              'planner could tell the safe tests apart only by the second rule of Mania et al., moving to the most uncertain '
              'features it can reach.'),
        ('b', '**The goal-oriented planner gets there sooner, with less extra pumping and lower chloride.** It reached '
              '<<atg>> years (<<atg10>>–<<atg90>>, 10–90% of runs), took the head down to <<atgh>> m (median), just above the '
              'true boundary, kept chloride below <<atgc>> mg/L in 95% of runs and needed <<atgw>> less extra pumping than the '
              'safe E-optimal planner. It certified 30 years after <<aw30g>> weeks of the campaign, against <<aw30s>> weeks '
              'with the filter and <<aw30e>> without; in the first months the E-optimal planner was ahead (<<aw26s>> against '
              '<<aw26g>> years after 26 weeks).'),
        ('b', '**The test limit the utility accepts matters more than the planner.** With a limit about 20% lower or higher '
              '(<<alo>> or <<ahi>> mg/L), the goal-oriented planner reached <<as055>> or <<as085>> years and the safe '
              'E-optimal planner <<ase055>> or <<ase085>>.'),
        ('b', '**The certificate held.** In all <<anall>> runs the true coefficients stayed inside the confidence set and the '
              'certified closing year was never later than the true one. The goal-oriented campaign raised the certified '
              'dewatering bound by <<adB>> m³/d, worth <<amu>> years per 1,000 m³/d by Eq. [[mult]]; with the certified '
              '5 cm error of the head forecast, no test could certify more than <<atbest>> years.'),
        ('p', 'In the project the tests use the existing wells and the port dewatering (T5.3): the utility approves each '
              'test, heads stay above the head limit $h_{pc}$, conductivity is logged and chloride sampled during the test '
              'and the recovery, and pumping returns to '
              'routine as soon as measured chloride reaches the test limit. The test system is replaced by the calibrated '
              'coupled model, and the years a campaign adds are reported with the safe window.'),
        ('img', 'active', 17.0),
        ('cap', 'Figure {{active}}. Safe, goal-oriented pumping tests, synthetic test. (a) Certified closing year of the window '
                'during the campaign (median of <<anr>> runs; shading: 10–90% for the goal-oriented planner and for the '
                'E-optimal planner without safety filter); dashed: the true closing year; dotted: the most a test can '
                'certify with the certified error of the head forecast. (b) Highest chloride reached during the campaign '
                '(box: quartiles; whiskers: 5–95% of runs).'),

        ('h2', '7.7 When the prior of the tests is wrong (new, C3)'),
        ('p', 'The certificate of Section 7.6 assumes that the prior from the calibrated model is wrong by at most $S$ in the '
              '$\\boldsymbol{\\Lambda}$-norm (Section 6). In Section 7.6 the prior was <<qe0>>$\\sigma$ from the true '
              'coefficients, inside $S$ = <<qS>>$\\sigma$, where $\\sigma$ is the noise of weekly chloride. Three optimistic '
              'priors were added, with the onset of intrusion <<qo1>>%, <<qo2>>% and <<qo3>>% weaker and flushing <<qf1>>%, '
              '<<qf2>>% and <<qf3>>% faster than in the truth; they lie <<qe1>>$\\sigma$, <<qe2>>$\\sigma$ and '
              '<<qe3>>$\\sigma$ from the truth, all outside $S$. Each prior was used in up to five ways: with the radius $S$ '
              'of Section 7.6; with $2S$ or $4S$; with $S$ and the conflict test of Eq. [[conflict]], which switches to the '
              'physics-only prior when it fires; and, for the prior of Section 7.6, with the physics-only prior alone. That '
              'prior allows any coefficients in a box of physically admissible values (flushing in 20 to 200 weeks; '
              'chloride that does not fall as the head falls). The goal-oriented, safe planner of Section 7.6 ran on the '
              'same <<qnr>> histories in every case (Figure {{prior}}). Two years serve as yardsticks: the true closing '
              'year, <<qtt>> years, and the most a correct certificate can give with the certified 5 cm error of the head '
              'forecast, <<qtb>> years. A certified year beyond <<qtb>> places the certified boundary below the true one.'),
        ('b', '**The prior is worth all of the certified years.** With the prior of Section 7.6 the campaign certified '
              '<<q0n>> years; with $2S$, <<q02>> years; with $4S$ or with the physics-only prior, none. The <<ahy>> years '
              'of records and <<acw>> weeks of tests cannot certify the boundary on their own at $\\delta$ = 5%.'),
        ('b', '**An optimistic prior inflates the certificate, and the tests go deeper.** With the radius $S$, the three '
              'optimistic priors certified <<q1n>>, <<q2n>> and <<q3n>> years, and the tests let chloride rise further: '
              'below <<qc3>> mg/L in 95% of runs, against <<qc0>> mg/L with the prior of Section 7.6, still under the test '
              'limit of <<act>> mg/L. With the prior <<qe2>>$\\sigma$ away, '
              'the confidence set missed the true coefficients in <<q2m>>, yet the certified boundary stayed above the true '
              'one. With the prior <<qe3>>$\\sigma$ away, the certified boundary fell below the true one in <<q3u>> of the '
              'runs, and the certified year passed even the true closing year in <<q3l>> of the runs.'),
        ('b', '**The conflict test raised no false alarm, and no alarm.** It never fired with the prior of Section 7.6, as '
              'it should not, nor with any optimistic prior. The data did see the error of the most optimistic prior, at '
              '<<q3d>>$\\sigma$ in the norm of the data (median of the runs), but the physics-only confidence set was about '
              'as wide, <<q3b>>$\\sigma$, because it must hold in every week and for every coefficient vector in the box. '
              'No prior came further than <<qdmax>>$\\sigma$ from that set in any week of any run, against the '
              '$S$ = <<qS>>$\\sigma$ the test needs. In a campaign of this length the test guards only against gross '
              'errors, and its silence is no evidence that the prior is right: a check sees the prior only through the '
              'data (Gelman, Simpson and Betancourt, 2017).'),
        ('b', '**Widening the radius protects, at a price in years.** With $2S$ or $4S$ the certified boundary never fell '
              'below the true one for any prior, but with $2S$ the prior of Section 7.6 lost <<qloss>> of its <<q0n>> '
              'years. The optimistic priors kept <<q12>>, <<q22>> and <<q32>> years with $2S$ (with the priors <<qe2>>$\\sigma$ and '
              '<<qe3>>$\\sigma$ away the confidence set still missed the truth <<q2x>>): at the same radius an '
              'optimistic centre keeps more years than a correct one, so a wide radius does not make the years '
              'independent of the prior.'),
        ('p', '**Consequence for the project.** The years that the tests certify are mostly a property of the prior, so the '
              'prior has to be justified before the campaign and its effect reported; it cannot be checked on the '
              'campaign data alone. CERTAIN-COAST sets $S$ from the spread of the calibrated ensemble and the prior checks '
              'of Section 3, which use every data type and not only chloride at one wellfield. It reports the certified '
              'closing year and the years each test adds for $S$ and for $2S$, so that a reader who trusts the model less '
              'can read the years they would accept (Andrews and Shapiro, 2021). It runs the conflict test during the '
              'campaign as a guard against gross errors only.'),
        ('img', 'prior', 17.0),
        ('cap', 'Figure {{prior}}. Pumping tests with a wrong prior, synthetic test (<<qnr>> runs for each case). (a) Certified '
                'closing year after the campaign, by prior and by use of the prior; dashed: the true closing year; dotted: '
                'the most a correct certificate can give with the certified 5 cm error of the head forecast. (b) Runs in '
                'which the confidence set missed the true coefficients in some week, and runs in which the certified '
                'boundary fell below the true one in some week.'),

        ('h', '8. Software, data and reproducibility (T6.3, T7.2)'),
        ('b', '**Open software.** The model, surrogate, generative copy, alarms, safe window, test planner and network design are released under an open licence, in containers, with tests and documentation.'),
        ('b', '**Data.** Operator data are used under the access agreements of T7.2; derived products, the bulletin log, the verification ledger and the project data are released openly following FAIR principles.'),
        ('b', '**Reproducibility.** Every bulletin and figure can be regenerated from the logged inputs and the code version; the preparatory tests of Sections 4.2, 5.7, 7.3–7.4, 7.6 and 7.7 are scripted and released with the software.'),

        ('h', '9. Pass tests and fallbacks for each step'),
        ('cap', 'Table {{tab_checks}}. What each step must achieve, and what happens if it does not.'),
        ('table', ['Step', 'Output', 'Pass test', 'Fallback'], CHECKS, [3.0, 3.4, 5.6, 5.0], 9.5),

        ('h', '10. Standard, frontier and new: what this methodology adds'),
        ('p', 'Table {{tab_ledger}} separates, for each step, the standard methods (Annex A), the methods adopted from the research frontier and '
              'the contributions of CERTAIN-COAST. Only the last column is claimed as new.'),
        ('cap', 'Table {{tab_ledger}}. Ledger of methods.'),
        ('table', ['Step', 'Standard (Annex A)', 'Adopted from the 2018–2026 frontier', 'New in CERTAIN-COAST, tested'], LEDGER,
         [2.6, 4.0, 6.4, 4.0], 9.0),
        ('h2', 'What is new'),
        ('b', '**C1. A certified safe operating window for three hazards, and the year it closes** (Section 7.2). The set of pumping '
              'and dewatering decisions that keeps seawater intrusion, liquefaction, flooding and new subsidence within certified limits '
              'at once; the sea level and the year at which it closes; and the multiplier that converts any margin into years. In the '
              'preparatory test the certified window closed after <<tc>> years, while plans that watch one hazard believed they had '
              '<<psw>> to <<plq>> years.'),
        ('b', '**C2. The value of a sensor in years of safe operation** (Sections 6 and 7.4). Each candidate sensor is valued by the '
              'years it adds before the certified window closes, from preposterior analysis with a first-order shortcut through the '
              'multiplier. In the test it valued GNSS and corner reflectors at <<gn>> and <<cr>> years, where the classical criterion '
              'gives zero, and the sentinel piezometer at <<sp>> years.'),
        ('b', '**C3. Safe, goal-oriented pumping tests valued in years** (Sections 6, 7.6 and 7.7). Short pumping and dewatering '
              'tests are chosen for the years they add to the certified closing of the window, with a confidence set that '
              'holds in every week and a safety filter on chloride. In the preparatory test they raised the certified closing '
              'year from <<atb>> to <<atg>> years with chloride below <<atgc>> mg/L in 95% of runs, where unconstrained '
              'E-optimal tests passed 250 mg/L in <<atel>> of the runs. The same test values the prior: the prior from the '
              'calibrated model was worth all <<q0n>> certified years, doubling its error bound cost <<qloss>> of them, '
              'and an optimistic prior <<qe3>>$\\sigma$ away inflated the certificate to <<q3n>> years while the conflict '
              'test stayed silent.'),
        ('b', '**Not claimed as new.** The alarms assemble published frontier methods: online conformal calibration under shift, '
              'guarantees by regime, extreme conformal prediction, Learn then Test and anytime-valid verification. Their joint use '
              'for coupled coastal hazards is an application of these methods. The generative copy and prediction-powered '
              'inference are adopted; the test of Section 4.2 shows what they can and cannot certify. So are the priors, the '
              'prior checks and the conflict test of Sections 3 and 6; Section 7.7 shows what the conflict test can and '
              'cannot detect. The novelty checks for '
              'C1, C2 and C3 rest on our literature search, to be repeated in bibliographic databases before submission.'),

        ('pb',),
        ('h', 'Annex A. Standard working equations'),
        ('p', 'These equations are standard; they are the physics on which the methods of Sections 2–7 operate. Their parameters are '
              'estimated from the site data (Section 3).'),
        ('p', '**InSAR line-of-sight decomposition** (ascending and descending geometries; the radar is nearly blind to north–south motion):'),
        ('eqa', 'los', 'd^{\\,asc}_{LOS} = n^{asc}_{E}\\,u_E + n^{asc}_{U}\\,u_z, \\qquad d^{\\,dsc}_{LOS} = n^{dsc}_{E}\\,u_E + n^{dsc}_{U}\\,u_z'),
        ('p', '**Trajectory model** with trend, season, the coseismic step of 26 November 2019 at $t_{eq}$ and a postseismic transient ($H$ the step function):'),
        ('eqa', 'traj', 'u_z(t) = u_0 + v\\,t + A\\sin\\left(\\frac{2\\pi t}{T_{yr}} + \\phi\\right) + \\left[\\Delta_{eq} + P\\ln\\left(1 + \\frac{t - t_{eq}}{\\tau_p}\\right)\\right] H(t - t_{eq})'),
        ('p', '**Elastic and inelastic compaction** below the preconsolidation head $h_{pc}$, with $S_{kv} \\gg S_{ke}$ and $u_z = -\\Delta b$ (Riley, 1969):'),
        ('eqa', 'comp', '\\Delta b(t) = \\begin{cases} S_{ke}\\,[h_0 - h(t)], & h(t) \\ge h_{pc}(t) \\\\ S_{ke}\\,[h_0 - h_{pc}(t)] + S_{kv}\\,[h_{pc}(t) - h(t)], & h(t) < h_{pc}(t) \\end{cases}'),
        ('p', '**Delayed drainage** of clay interbeds of thickness $b_0$:'),
        ('eqa', 'tau', '\\tau = \\frac{S_{skv}\\,(b_0/2)^2}{K_v}'),
        ('p', '**Variable-density flow** in equivalent freshwater head $h_f$, density rising linearly with the seawater fraction $c$, wells as sinks; $S_s$ contains the skeletal storage, which couples flow and compaction:'),
        ('eqa', 'darcy', '\\mathbf{q} = -\\mathbf{K}_f\\left(\\nabla h_f + \\frac{\\rho - \\rho_f}{\\rho_f}\\,\\nabla z\\right), \\qquad \\rho = \\rho_f + (\\rho_s - \\rho_f)\\,c'),
        ('eqa', 'mass', 'S_s\\,\\frac{\\partial h_f}{\\partial t} + \\nabla\\cdot\\mathbf{q} = -\\sum_j Q_j\\,\\delta(\\mathbf{x} - \\mathbf{x}_j)'),
        ('p', '**Salt with memory:** mobile and immobile domains exchanging salt at rate $\\omega$, which keeps wells saline for years after pumping is reduced:'),
        ('eqa', 'salt', '\\theta_m\\frac{\\partial c_m}{\\partial t} + \\theta_{im}\\frac{\\partial c_{im}}{\\partial t} = \\nabla\\cdot(\\theta_m\\mathbf{D}\\,\\nabla c_m) - \\mathbf{q}\\cdot\\nabla c_m, \\qquad \\theta_{im}\\frac{\\partial c_{im}}{\\partial t} = \\omega\\,(c_m - c_{im})'),
        ('p', '**The sea as a moving boundary,** where subsidence and sea-level rise enter the intrusion model:'),
        ('eqa', 'sea', 'h_f(\\mathbf{x}_{sea}, t) = \\frac{\\rho_s}{\\rho_f}\\left[R(t) + \\eta_{tide}(t) + \\eta_{surge}(t)\\right] - \\frac{\\rho_s - \\rho_f}{\\rho_f}\\,z'),
        ('p', '**Total water level** at asset $a$, with wave setup $\\eta_{wave}$:'),
        ('eqa', 'twl', 'TWL_a(t) = R_a(t) + \\eta_{tide}(t) + \\eta_{surge}(t) + \\eta_{wave}(t)'),
        ('p', '**Liquefaction triggering** with a moving water table (Seed and Idriss, 1971; CPT-based form of Boulanger and Idriss, 2014), with $\\sigma_v = \\gamma_m\\min(z, z_w) + \\gamma_{sat}(z - z_w)^{+}$, magnitude scaling factor MSF, overburden correction $K_\\sigma$, and the liquefaction potential index (Iwasaki et al., 1978):'),
        ('eqa', 'csr', 'CSR(z,t) = 0.65\\,\\frac{a_{max}}{g}\\,\\frac{\\sigma_v(z,t)}{\\sigma\'_v(z,t)}\\,r_d(z), \\qquad \\sigma\'_v = \\sigma_v - \\gamma_w\\,[z - z_w(\\mathbf{x},t)]^{+}'),
        ('eqa', 'fs', 'FS(z,t) = \\frac{CRR_{7.5}(q_{c1Ncs})\\;MSF\\;K_\\sigma}{CSR(z,t)}, \\qquad LPI(\\mathbf{x},t) = \\int_0^{20}\\left[1 - FS(z,t)\\right]^{+}(10 - 0.5\\,z)\\,dz'),
        ('p', '**Ensemble smoother with multiple data assimilation** (Emerick and Reynolds, 2013), inflation factors $\\beta_i$, members $j$:'),
        ('eqa', 'esmda', '\\boldsymbol{\\theta}^{a}_{j} = \\boldsymbol{\\theta}^{f}_{j} + \\mathbf{C}_{\\theta d}\\left(\\mathbf{C}_{dd} + \\beta_i\\mathbf{C}_D\\right)^{-1}\\left(\\mathbf{d}_{obs} + \\sqrt{\\beta_i}\\,\\mathbf{C}_D^{1/2}\\mathbf{z}_j - \\mathbf{g}(\\boldsymbol{\\theta}^{f}_{j})\\right), \\qquad \\sum_i \\beta_i^{-1} = 1'),
        ('p', '**Extremes with a moving threshold** (Coles, 2001); $\\lambda_u$ is the yearly rate of exceedances and $z_N$ the $N$-year level:'),
        ('eqa', 'gpd', '\\Pr\\left(Y > y \\mid Y > u(t)\\right) = \\left[1 + \\xi_g\\,\\frac{y - u(t)}{\\sigma_g(t)}\\right]^{-1/\\xi_g}, \\qquad u(t) = u_0 + R_a(t) - R_a(t_0)'),
        ('eqa', 'retl', 'z_N(t) = u(t) + \\frac{\\sigma_g(t)}{\\xi_g}\\left[(N\\lambda_u)^{\\xi_g} - 1\\right]'),
        ('p', '**Seismic velocity and effective stress:** stretching of noise correlations and the grain-contact prior $n \\approx 1/6$ ($\\Delta T$ temperature, $\\varepsilon$ noise):'),
        ('eqa', 'dvv', '\\frac{\\delta v}{v} = -\\frac{\\delta t}{t}, \\qquad \\frac{\\delta v}{v}(t) \\approx n\\,\\frac{\\Delta\\sigma\'_v(t)}{\\bar{\\sigma}\'_v} + b\\,\\Delta T(t) + \\varepsilon(t), \\qquad \\Delta\\sigma\'_v \\approx (\\gamma_w - \\gamma_{sat} + \\gamma_m)\\,\\Delta z_w'),
        ('p', '**Sharp-interface single potential** for an unconfined aquifer whose base lies at depth $d = d_0 + R$ below the sea, '
              '$\\delta = (\\rho_s - \\rho_f)/\\rho_f$, freshwater head $h$ above sea level; seawater lies below the aquifer where '
              '$\\phi < \\phi_{toe}$ (Strack, 1976; used in Section 7.3):'),
        ('eqa', 'strack', '\\phi = \\begin{cases} \\frac{1}{2}\\left[(h + d)^2 - (1+\\delta)\\,d^2\\right], & \\phi \\ge \\phi_{toe} \\\\ \\frac{1+\\delta}{2\\delta}\\,h^2, & \\phi < \\phi_{toe} \\end{cases}, \\qquad \\phi_{toe} = \\frac{1}{2}\\,\\delta(1+\\delta)\\,d^2'),
        ('p', '**Wells and image wells** along the coast $x = 0$ with regional discharge $q$, and the stagnation points on the flow '
              'line of a wellfield at $x_w$ and dewatering at $x_p$ ($u = x^2$, $a_i = Q_i x_i/(\\pi K)$); seawater reaches the '
              'wellfield when the higher of the two stagnation potentials falls below $\\phi_{toe}$:'),
        ('eqa', 'wells', '\\phi(x, y) = \\frac{q\\,x}{K} + \\sum_i \\frac{Q_i}{4\\pi K}\\,\\ln\\frac{(x - x_i)^2 + y^2}{(x + x_i)^2 + y^2}'),
        ('eqa', 'qhead', '\\frac{q}{K}\\,(u - x_p^2)(u - x_w^2) + a_p\\,(u - x_w^2) + a_w\\,(u - x_p^2) = 0, \\qquad q(R) = \\frac{K}{2L}\\left[(h_L + d_0)^2 - (1+\\delta)(d_0 + R)^2\\right]'),
        ('p', 'The second relation is the regional discharge when the inland water level $h_L$ is held fixed relative to the land at '
              'distance $L$ (head-controlled; Werner and Simmons, 2009).'),
    ]
    vals = {
        'fa_every': pc(fa['naive_every_event']), 'fa_q': pc(fa['naive_quarterly']), 'fa_e': pc(fa['eprocess_pooled'], 1),
        'd25p': pc(d25['pooled_power']), 'd25m': n(d25['pooled_median_events']),
        'e10': ', '.join(str(x) for x in en['0.10']['eprocess']), 'v03': pc(v03['share_verified_by_100']),
        'u29': pc(up['29']['anytime'], 1), 'u60': pc(up['60']['anytime'], 1),
        'N': f'{W["N"]:,}', 'sc_n': str(W['saddle_check']['cases']), 'sc_a': ('all' if W['saddle_check']['agree'] == W['saddle_check']['cases'] else str(W['saddle_check']['agree'])),
        'Rs': n(W['R_star'], 2), 'Rm': n(W['R_star_median'], 2), 'r5': n(W['r_p5_p95_mm'][0], 1), 'r95': n(W['r_p5_p95_mm'][1], 1),
        'tc': n(W['t_cert']), 'tm': n(W['t_median']), 'pf': n(pl['flood_only']['believed']), 'plq': n(pl['liq_only']['believed']),
        'psw': n(pl['swi_only']['believed']), 'tl0': n(W['tL0']), 'cost': n(W['t_median'] - W['t_cert']), 'M': str(W['M']),
        'gn': n(gn['years'], 1), 'cr': n(cr['years'], 1), 'gnk': n(gn['years_per_10k'], 1), 'crk': n(cr['years_per_10k'], 1),
        'sp': n(sp['years'], 1), 'spr': pc(sp['spread_reduction']), 'envr': n(env_err, 1),
        'medr': n(max(abs(x['years_linear_median'] - x['years_median']) for x in W['sensors']), 1),
        'rank': ('ranked the four sensors in the same order as the full computation' if same_rank else
                 'did not rank the four sensors in the same order as the full computation'),
    }

    # C3: safe, goal-oriented pumping tests (method_active.json)
    import method_active as MA
    K, Tr, Pa = A['kinds'], A['truth'], A['params']
    col = lambda k, f: np.array([r[f] for r in K[k]['runs']], float)
    wk = lambda k: np.median(np.array([r['weekly'] for r in K[k]['runs']]), 0)
    first = lambda k, y: int(np.argmax(wk(k) >= y)) + 1 if (wk(k) >= y).any() else None
    cm = lambda k: 250 * col(k, 'c_max')
    allk = list(K)
    covered = all(r['covered'] for k in allk for r in K[k]['runs'])
    never_late = all(r['t_after'] <= Tr['t_close'] and max(r['weekly']) <= Tr['t_close'] for k in allk for r in K[k]['runs'])
    if not (covered and never_late):
        raise SystemExit('C3 certificate failed in some run: revise the text of Section 7.6')
    dB = (np.median(col('goal_safe', 't_after')) - np.median(col('goal_safe', 't_before'))) / MA.MU
    sens = A['sensitivity']
    th = lambda x: f'{int(round(x, -3)):,}'
    vals.update({
        'aD': th(1000 * Pa['D']), 'ahc': n(Tr['h_crit'], 2), 'ahy': n(Pa['HIST'] / 52), 'acw': str(Pa['CAMP']),
        'arw': str(Pa['REC']), 'anc': str(len(MA.QW_C) * len(MA.QD_C) * len(MA.L_C)),
        'aqw0': th(1000 * MA.QW_C.min()), 'aqw1': th(1000 * MA.QW_C.max()),
        'aqd0': f'{int(round(1000 * MA.QD_C.min())):,}', 'aqd1': f'{int(round(1000 * MA.QD_C.max())):,}',
        'act': n(250 * Pa['C_TEST']), 'anr': str(Pa['NRUN']), 'anall': f'{len(allk) * Pa["NRUN"]:,}',
        'atb': n(np.median(col('goal_safe', 't_before')), 1), 'att': n(Tr['t_close']),
        'atr': n(np.median(col('routine', 't_after')), 1), 'atrd': n(np.median(col('random', 't_after')), 1),
        'ate': n(np.median(col('eopt', 't_after')), 1), 'atel': pc(np.mean(cm('eopt') > 250)),
        'ateh': n(np.median(col('eopt', 'h_min')), 2),
        'ates': n(np.median(col('eopt_safe', 't_after')), 1),
        'atg': n(np.median(col('goal_safe', 't_after')), 1),
        'atg10': n(np.percentile(col('goal_safe', 't_after'), 10), 1), 'atg90': n(np.percentile(col('goal_safe', 't_after'), 90), 1),
        'atgh': n(np.median(col('goal_safe', 'h_min')), 2), 'atgc': n(np.percentile(cm('goal_safe'), 95)),
        'atgw': pc(1 - np.median(col('goal_safe', 'extra_kQ_weeks')) / np.median(col('eopt_safe', 'extra_kQ_weeks'))),
        'aw30g': str(first('goal_safe', 30)), 'aw30s': str(first('eopt_safe', 30)), 'aw30e': str(first('eopt', 30)),
        'aw26s': n(wk('eopt_safe')[25], 1), 'aw26g': n(wk('goal_safe')[25], 1),
        'alo': n(250 * 0.55), 'ahi': n(250 * 0.85),
        'as055': n(sens['0.55']['goal_safe']['t_after_median'], 1), 'as085': n(sens['0.85']['goal_safe']['t_after_median'], 1),
        'ase055': n(sens['0.55']['eopt_safe']['t_after_median'], 1), 'ase085': n(sens['0.85']['eopt_safe']['t_after_median'], 1),
        'adB': f'{int(round(1000 * dB, -1)):,}', 'amu': n(MA.MU, 1), 'atbest': n(MA.closing(Tr['h_crit'])[0]),
    })
    ct = 250 * Pa['C_TEST']
    story = [not any(sens[c][k]['share_above_test'] > 0 for c in sens for k in sens[c]),
             np.mean(cm('eopt') > ct) == 1, np.mean(cm('eopt_safe') > ct) == 0, np.mean(cm('goal_safe') > ct) == 0,
             abs(np.median(col('eopt', 't_after')) - np.median(col('eopt_safe', 't_after'))) < 0.5,
             first('goal_safe', 30) < first('eopt_safe', 30) < first('eopt', 30),
             np.median(col('goal_safe', 'extra_kQ_weeks')) < np.median(col('eopt_safe', 'extra_kQ_weeks')),
             np.percentile(cm('goal_safe'), 95) < np.percentile(cm('eopt_safe'), 95),
             wk('eopt_safe')[25] > wk('goal_safe')[25],
             np.median(col('eopt', 'h_min')) < Tr['h_crit'] < np.median(col('goal_safe', 'h_min')),
             sens['0.55']['goal_safe']['t_after_median'] < np.median(col('goal_safe', 't_after')) < sens['0.85']['goal_safe']['t_after_median']]
    if not all(story):
        raise SystemExit(f'C3 findings changed ({story}): revise the text of Section 7.6')

    # Section 7.7: the prior of the tests (method_prior.json)
    PRr, PPa = PR['runs'], PR['params']
    t_close, t_best = PR['truth']['t_close'], PR['truth']['t_best']

    def pstat(key):
        rs = PRr[key]
        ta = np.array([r['t_after'] for r in rs], float)
        top = [max([r['t_before'], r['t_after']] + r['weekly']) for r in rs]
        return dict(med=float(np.median(ta)), miss=float(np.mean([not r['covered_all'] for r in rs])),
                    unsafe=float(np.mean([x > t_best + 1e-9 for x in top])), late=float(np.mean([x > t_close for x in top])),
                    sw=float(np.mean([r['switched'] is not None for r in rs])), dmax=max((r['dist_max'] or 0.0) for r in rs),
                    ddat=float(np.median([r['err_data_end'] for r in rs])), bbox=float(np.median([r['beta_box_end'] for r in rs])),
                    c95=float(np.percentile(250 * np.array([r['c_max'] for r in rs]), 95)),
                    over=float(np.mean([r['c_max'] > PPa['C_TEST'] for r in rs])))
    q = {k: pstat(k) for k in PRr}
    pe, WR = {k: v['nominal'] for k, v in PR['prior_error'].items()}, PPa['WRONG']
    yrs = lambda k: n(q[k]['med'], 1)
    ph = lambda x: 'every run' if x == 1 else pc(x) + ' of the runs'
    vals.update({
        'qe0': n(pe['right'], 1), 'qe1': n(pe['wrong1'], 1), 'qe2': n(pe['wrong2'], 1), 'qe3': n(pe['wrong3'], 1),
        'qS': n(PR['S_nominal_sigma']), 'qnr': str(PPa['NRUN']), 'qtt': n(t_close), 'qtb': n(t_best, 1),
        'qo1': n(100 * WR['wrong1'][0]), 'qo2': n(100 * WR['wrong2'][0]), 'qo3': n(100 * WR['wrong3'][0]),
        'qf1': n(100 * WR['wrong1'][1]), 'qf2': n(100 * WR['wrong2'][1]), 'qf3': n(100 * WR['wrong3'][1]),
        'q0n': yrs('right_nominal'), 'q02': yrs('right_wide2'),
        'q1n': yrs('wrong1_nominal'), 'q2n': yrs('wrong2_nominal'), 'q3n': yrs('wrong3_nominal'),
        'q12': yrs('wrong1_wide2'), 'q22': yrs('wrong2_wide2'), 'q32': yrs('wrong3_wide2'),
        'qc0': n(q['right_nominal']['c95']), 'qc3': n(q['wrong3_nominal']['c95']),
        'q2m': ph(q['wrong2_nominal']['miss']),
        'q2x': ('in some week of every run' if q['wrong2_wide2']['miss'] == 1 and q['wrong3_wide2']['miss'] == 1 else
                f"in some week of {pc(q['wrong2_wide2']['miss'])} and {pc(q['wrong3_wide2']['miss'])} of the runs"),
        'q3u': pc(q['wrong3_nominal']['unsafe']), 'q3l': pc(q['wrong3_nominal']['late'], 1),
        'q3d': n(q['wrong3_checked']['ddat'], 1), 'q3b': n(q['wrong3_checked']['bbox'], 1),
        'qdmax': n(max(q[k]['dmax'] for k in q if k.endswith('_checked')), 1),
        'qloss': n(q['right_nominal']['med'] - q['right_wide2']['med'], 1),
    })
    wrong = ('wrong1', 'wrong2', 'wrong3')
    qchk = [q['right_nominal']['miss'] == 0 and q['right_nominal']['unsafe'] == 0,
            q['right_wide4']['med'] == 0 and q['right_box']['med'] == 0,
            q['right_wide2']['med'] < q['right_nominal']['med'],
            q['right_nominal']['med'] < q['wrong1_nominal']['med'] < q['wrong2_nominal']['med'] < q['wrong3_nominal']['med'],
            q['right_nominal']['c95'] < q['wrong3_nominal']['c95'], all(q[k]['over'] == 0 for k in q),
            q['wrong2_nominal']['miss'] > 0.5 and q['wrong2_nominal']['unsafe'] == 0,
            q['wrong3_nominal']['unsafe'] > 0 and q['wrong3_nominal']['late'] > 0,
            all(q[k]['sw'] == 0 for k in q if k.endswith('_checked')),
            max(q[k]['dmax'] for k in q if k.endswith('_checked')) < PR['S_nominal_sigma'],
            all(q[k]['unsafe'] == 0 for k in q if k.endswith('_wide2') or k.endswith('_wide4')),
            all(q[w + '_wide2']['med'] > q['right_wide2']['med'] for w in wrong),
            q['wrong2_wide2']['miss'] > 0 and q['wrong3_wide2']['miss'] > 0,
            abs(q['wrong3_checked']['bbox'] - q['wrong3_checked']['ddat']) < 0.25 * q['wrong3_checked']['bbox'],
            all(pe[w] > PR['S_nominal_sigma'] > pe['right'] for w in wrong)]
    if not all(qchk):
        raise SystemExit(f'Section 7.7 findings changed ({qchk}): revise the text')

    # Section 4.2: generative copy (method_story.json, method_story_n500.json)
    g, p_, g5, p5 = ST['copies']['good'], ST['copies']['poor'], ST5['copies']['good'], ST5['copies']['poor']
    tt = g['t_true']; sp_ = ST['params']
    yr = lambda r, m: n(r[m]['median'])
    vals.update({
        'Lr': n(1000 * sp_['R_MEAN']), 'Lrs': n(1000 * sp_['R_SD'], 1), 'Lyr': str(sp_['YEARS']), 'Ltt': str(tt),
        'Lgo': n(100 * sp_['COPIES']['good'][0]), 'Lpo': n(100 * sp_['COPIES']['poor'][0]),
        'Lgf': n(100 * sp_['COPIES']['good'][1]), 'Lpf': n(100 * sp_['COPIES']['poor'][1]),
        'LN': f'{sp_["NCOPY"]:,}', 'Ln': str(sp_['NFULL']), 'Ln5': str(ST5['params']['NFULL']), 'Lrep': f'{sp_["REPS"]:,}',
        'Lcg': yr(g, 'copy_only'), 'Lcp': yr(p_, 'copy_only'), 'Lpg': yr(g, 'ppi'), 'Lpp': yr(p_, 'ppi'), 'Lfo': yr(g, 'full_only'),
        'Lucg': pc(1 - g['coverage_by_year']['ppi'][tt - 1]), 'Lucp': pc(1 - p_['coverage_by_year']['ppi'][tt - 1]),
        'Llg': pc(g['ppi']['later_than_true'], 1), 'Llp': pc(p_['ppi']['later_than_true'], 1),
        'Lpt': pc(g['p_true'][tt - 1], 1),
        'Luc5g': pc(1 - g5['coverage_by_year']['ppi'][tt - 1]), 'Luc5p': pc(1 - p5['coverage_by_year']['ppi'][tt - 1]),
        'Luc5': (pc(1 - g5['coverage_by_year']['ppi'][tt - 1]) + ' for both copies'
                 if pc(1 - g5['coverage_by_year']['ppi'][tt - 1]) == pc(1 - p5['coverage_by_year']['ppi'][tt - 1]) else
                 pc(1 - g5['coverage_by_year']['ppi'][tt - 1]) + ' (better copy) and ' + pc(1 - p5['coverage_by_year']['ppi'][tt - 1]) + ' (poorer copy)'),
        'Lp5g': yr(g5, 'ppi'), 'Lp5p': yr(p5, 'ppi'), 'Lf5': yr(g5, 'full_only'),
        'Lexmin': pc(min(min(c['coverage_by_year']['ppi_exact']) for c in (g, p_, g5, p5))),
        'Lexg': yr(g, 'ppi_exact'), 'Lex5g': yr(g5, 'ppi_exact'),
    })
    checks = [g['copy_only']['later_than_true'] == 1 and p_['copy_only']['later_than_true'] == 1,
              g['ppi']['median'] > g['full_only']['median'], 1 - g['coverage_by_year']['ppi'][tt - 1] > 0.05,
              1 - p_['coverage_by_year']['ppi'][tt - 1] > 0.05, g['p_true'][tt - 1] > sp_['ALPHA'],
              g['ppi_exact']['median'] <= g['full_only']['median'], g5['ppi_exact']['median'] <= g5['full_only']['median'],
              min(min(c['coverage_by_year']['ppi_exact']) for c in (g, p_, g5, p5)) >= 1 - sp_['DELTA'],
              g5['coverage_by_year']['ppi'][tt - 1] > g['coverage_by_year']['ppi'][tt - 1],
              p5['coverage_by_year']['ppi'][tt - 1] > p_['coverage_by_year']['ppi'][tt - 1]]
    if not all(checks):
        raise SystemExit(f'Section 4.2 findings changed ({checks}): revise the text')

    def fill(s):
        return re.sub(r'<<(\w+)>>', lambda m: vals[m.group(1)], s) if isinstance(s, str) else s
    return [tuple(fill(x) for x in b) for b in B], vals


# ---------------------------------------------------------------------------------------------------- figure
def fig_chain(path):
    W, H = 6.7, 5.43
    fig = plt.figure(figsize=(W, H), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    stages = [
        ('Observe', 'WP4 · T4.1–T4.4', COL['WP4'],
         'InSAR · GNSS · tide gauge · piezometers\nwith conductivity · chloride · seismic\nnoise · fibre-optic sensing',
         'Sensors ranked\nby years of safe\noperation'),
        ('Measure', 'WP1 · T1.1–T1.4', COL['WP1'],
         'Relative sea level at each asset from\nInSAR and GNSS; compaction and the\npreconsolidation head',
         '$R_a(t)$, $u_z(t)$,\n$h_{pc}(\\mathbf{x})$'),
        ('Model', 'WP2 · T2.1–T2.3', COL['WP2'],
         'Flow, salt memory, compaction and\nliquefaction on one water table;\ndifferentiable, adjoint gradients',
         '$I_1$ chloride\n$I_2$ liquefaction\n$I_3$ water level'),
        ('Fast copy', 'WP2 · T2.4', COL['WP2'],
         'Neural operator with a conformal,\ngoal-oriented error bound; generative\ncopy for storyline statistics',
         '$\\hat{I}_k \\pm \\Delta_k$\nin seconds'),
        ('Certify', 'WP3 · T3.1–T3.5', COL['WP3'],
         'Online conformal under shift; by\nregime; extreme conformal beyond\nthe record; Learn then Test',
         'Alarm $A_k$,\nmiss rate $\\leq \\alpha_k$'),
        ('Operate', 'WP5 · T5.1–T5.4', COL['WP5'],
         'Bulletins; certified safe window,\nclosing year; pumping rule; safe\ntests; anytime-valid verification',
         'Verified rates;\nyears of safe\noperation'),
    ]
    xL0, xT0, xT1, xM0, xM1, xO0, xO1 = 0.05, 0.42, 1.98, 2.06, 4.88, 4.96, 6.12
    bh, gap, top = 0.72, 0.17, H - 0.08
    ys = []
    for i, (name, wp, col, meth, out) in enumerate(stages):
        y1 = top - i * (bh + gap); y0 = y1 - bh; ym = (y0 + y1) / 2; ys.append((y0, y1, ym))
        ax.add_patch(FancyBboxPatch((xT0, y0), xT1 - xT0, bh, boxstyle='round,pad=0,rounding_size=0.08', fc=col, ec='none'))
        ax.text(xT0 + 0.13, ym + 0.13, f'{i + 1}', fontsize=15, fontweight='bold', color='white', va='center', ha='center')
        ax.text(xT0 + 0.32, ym + 0.13, name, fontsize=11.5, fontweight='bold', color='white', va='center', ha='left')
        ax.text(xT0 + 0.32, ym - 0.17, wp, fontsize=9, color='white', va='center', ha='left')
        ax.add_patch(FancyBboxPatch((xM0, y0), xM1 - xM0, bh, boxstyle='round,pad=0,rounding_size=0.08', fc='white', ec=col, lw=1.6))
        ax.text(xM0 + 0.10, ym, meth, fontsize=9.4, color='#1f2328', va='center', ha='left', linespacing=1.25)
        ax.add_patch(FancyBboxPatch((xO0, y0), xO1 - xO0, bh, boxstyle='round,pad=0,rounding_size=0.08', fc=col + '22', ec=col, lw=1.0))
        ax.text((xO0 + xO1) / 2, ym, out, fontsize=9.4, fontweight='bold', color='#1f2328', va='center', ha='center', linespacing=1.2)
        if i:
            ax.add_patch(FancyArrowPatch(((xT0 + xT1) / 2, ys[i - 1][0] - 0.01), ((xT0 + xT1) / 2, y1 + 0.01),
                                         arrowstyle='-|>', mutation_scale=13, color='#1f2328', lw=1.6))
            ax.add_patch(FancyArrowPatch(((xM0 + xM1) / 2, ys[i - 1][0] - 0.01), ((xM0 + xM1) / 2, y1 + 0.01),
                                         arrowstyle='-|>', mutation_scale=13, color='#9aa3ad', lw=1.3))

    def loop(x, i_from, i_to, label, side, dy=0.0):
        yf, yt = ys[i_from][2] + dy, ys[i_to][2]
        x_edge = xO1 if side == 'r' else xT0
        ax.plot([x_edge, x], [yf, yf], color='#1f2328', lw=1.3, ls=(0, (3, 2)))
        ax.plot([x, x], [yf, yt], color='#1f2328', lw=1.3, ls=(0, (3, 2)))
        ax.add_patch(FancyArrowPatch((x, yt), (x_edge + (0.01 if side == 'r' else -0.01), yt), arrowstyle='-|>',
                                     mutation_scale=12, color='#1f2328', lw=1.3))
        ax.text(x + (0.10 if side == 'r' else -0.11), (yf + yt) / 2, label, rotation=90, fontsize=8.8, va='center',
                ha='center', color='#1f2328', fontweight='bold')

    loop(6.22, 5, 4, 'margin update', 'r', dy=0.18)
    loop(6.48, 5, 2, 'new data assimilated', 'r', dy=-0.18)
    loop(0.24, 5, 0, 'years each sensor adds', 'l')
    fig.savefig(path, dpi=300)
    plt.close(fig)


# ---------------------------------------------------------------------------------------------------- Word
SUBWORDS = ('asc', 'dsc', 'LOS', 'eq', 'yr', 'TG', 'pc', 'ke', 'kv', 'skv', 'sea', 'tide', 'surge', 'wave', 'max',
            'c1Ncs', 'sat', 'im', 'obs', 'pr', 'toe', 'test', 'cert', 'phys', 'rob')
WORDS = ('CSR', 'FS', 'CRR', 'MSF', 'LPI', 'TWL', 'FAR', 'miss', 'cost')


def upright(tex):
    """Descriptive names and subscripts upright; separators between joined equations written as words, so that both
    Word and LibreOffice show them clearly."""
    tex = re.sub(r'([_^])\{(?:\\,)?(' + '|'.join(SUBWORDS) + r')\}', r'\1{\\text{\2}}', tex)
    tex = re.sub(r'(?<![\\A-Za-z])(' + '|'.join(WORDS) + r')(?![A-Za-z])', r'\\text{\1}', tex)
    tex = tex.replace(', \\qquad ', ' \\quad\\text{ and }\\quad ').replace(' \\quad s.t. \\quad ', ' \\quad\\text{ subject to }\\quad ')
    return tex


class Eqs:
    def __init__(self):
        self.items = []

    def add(self, tex, display, size=None):
        tex = upright(tex)
        i = len(self.items)
        d = {'id': i, 'tex': tex, 'display': display}
        if size:
            d['size'] = size
        self.items.append(d)
        return f'§§EQ{i}§§' if display else f'§§IQ{i}§§'


def no_borders(t):
    tblPr = t._tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{side}'); e.set(qn('w:val'), 'nil'); b.append(e)
    tblPr.append(b)


def fixed_widths(t, widths):
    t.autofit = False
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); t._tbl.tblPr.append(lay)
    for j, gc in enumerate(t._tbl.tblGrid.findall(qn('w:gridCol'))):
        gc.set(qn('w:w'), str(int(widths[j] * 567)))
    for row in t.rows:
        for j, w in enumerate(widths):
            row.cells[j].width = Cm(w)


def numref(text, numbers):
    """[[key]] -> (equation number); {{key}} -> figure or table number, assigned in order of appearance."""
    text = re.sub(r'\[\[(\w+)\]\]', lambda m: f'({numbers[m.group(1)]})', text)
    return re.sub(r'\{\{(\w+)\}\}', lambda m: numbers['#' + m.group(1)], text)


def mrich(p, text, E, size=11, numbers=None):
    """Text with $inline math$, **bold** and [[key]] equation numbers."""
    if numbers:
        text = numref(text, numbers)
    for i, seg in enumerate(text.split('$')):
        if i % 2:
            run(p, E.add(seg, False, size=int(size * 2)), size=size)
            continue
        for j, s in enumerate(seg.split('**')):
            if s:
                run(p, s, bold=(j % 2 == 1), size=size)


def display_eq(doc, E, tex, number):
    t = doc.add_table(rows=1, cols=2)
    no_borders(t); fixed_widths(t, [15.4, 1.6])
    c0, c1 = t.rows[0].cells
    for c in (c0, c1):
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = c0.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3); p.paragraph_format.space_after = Pt(3)
    run(p, E.add(tex, True))
    q = c1.paragraphs[0]; q.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run(q, f'({number})', size=11)
    trPr = t.rows[0]._tr.get_or_add_trPr(); trPr.append(OxmlElement('w:cantSplit'))


def rich_cell(cell, text, E, numbers, size):
    p = cell.paragraphs[0]
    for r_ in list(p.runs):
        r_._r.getparent().remove(r_._r)
    mrich(p, text, E, size=size, numbers=numbers)


def main(out):
    import method_figs as MF
    with open(os.path.join(HERE, 'method_window.json')) as fh:
        Wj = json.load(fh)
    with open(os.path.join(HERE, 'method_verify.json')) as fh:
        Vj = json.load(fh)
    with open(os.path.join(HERE, 'method_active.json')) as fh:
        Aj = json.load(fh)
    with open(os.path.join(HERE, 'method_story.json')) as fh:
        Sj = json.load(fh)
    with open(os.path.join(HERE, 'method_story_n500.json')) as fh:
        S5j = json.load(fh)
    with open(os.path.join(HERE, 'method_prior.json')) as fh:
        Pj = json.load(fh)
    BL, vals = blocks(Wj, Vj, Aj, Sj, S5j, Pj)
    numbers, n_main, n_ann, n_fig, n_tab = {}, 0, 0, 0, 0
    for b in BL:
        if b[0] == 'eq':
            n_main += 1; numbers[b[1]] = str(n_main)
        elif b[0] == 'eqa':
            n_ann += 1; numbers[b[1]] = f'A{n_ann}'
        elif b[0] == 'img':
            n_fig += 1; numbers['#' + b[1]] = str(n_fig)
        elif b[0] == 'cap' and re.match(r'Table \{\{(\w+)\}\}', b[1]):
            n_tab += 1; numbers['#' + re.match(r'Table \{\{(\w+)\}\}', b[1]).group(1)] = str(n_tab)
    E = Eqs()
    work = tempfile.mkdtemp()
    figs = {k: os.path.join(work, f'fig_{k}.png') for k in ('chain', 'story', 'verify', 'window', 'closing', 'sensors', 'active', 'prior')}
    fig_chain(figs['chain'])
    MF.fig_story(figs['story'], Sj)
    MF.fig_active(figs['active'], Aj)
    MF.fig_prior(figs['prior'], Pj)
    MF.fig_verify(figs['verify'], Vj)
    MF.fig_window(figs['window'], (0.0, 0.25, 0.45),
                  ('Today (R = 0)', 'R = 0.25 m', f'R = 0.45 m'))
    MF.fig_closing(figs['closing'], Wj)
    MF.fig_sensors(figs['sensors'], Wj)

    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(11)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, 'CERTAIN-COAST — Methodology', bold=True, size=18, color='1F3864')
    p = para(doc, 10); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; run(p, FULL, bold=True, size=12, color='1F3864')
    for bi, b in enumerate(BL):
        kind = b[0]
        nxt = BL[bi + 1][0] if bi + 1 < len(BL) else None
        if kind == 'h':
            heading(doc, b[1], 13.5, before=10)
        elif kind == 'h2':
            heading(doc, b[1], 12, color='2E6DB4', before=6)
        elif kind == 'p':
            p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; mrich(p, b[1], E, numbers=numbers)
            if nxt in ('eq', 'eqa'):
                p.paragraph_format.keep_with_next = True
        elif kind == 'b':
            p = para(doc, 3, 0.5); run(p, '• ', bold=True); mrich(p, b[1], E, numbers=numbers)
            if nxt == 'img':
                p.paragraph_format.keep_with_next = False
        elif kind in ('eq', 'eqa'):
            display_eq(doc, E, b[2], numbers[b[1]])
        elif kind == 'table':
            rows = [[numref(c, numbers) for c in r_] for r_ in b[2]]
            if b[1][0] == 'Step' and len(b[1]) == 4 and 'Standard (Annex A)' in b[1]:
                t = table(doc, b[1], [[re.sub(r'\*\*', '', c) for c in r_] for r_ in rows], b[3], size=b[4])
                for i_, r_ in enumerate(rows, start=1):
                    if '**' in r_[3]:
                        rich_cell(t.rows[i_].cells[3], r_[3], E, numbers, b[4])
                        shade(t.rows[i_].cells[3], 'E6F4EA')
            else:
                t = table(doc, b[1], rows, b[3], size=b[4])
            para(doc, 4)
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
        elif kind == 'sensors':
            hdr = ['Sensor', 'Cost (€)', 'Years added: mean ± 2 SE (median)', 'Years per €10,000', 'First-order estimate, median outcome (years)', 'Today\'s spread reduction']
            rows = [[x['sensor'], f'{x["cost"]:,}', f'{x["years"]:.1f} ± {2 * x["years_se"]:.1f} ({x["years_median"]:.1f})',
                     f'{x["years_per_10k"]:.1f}', f'{x["years_linear_median"]:.1f}', f'{100 * x["spread_reduction"]:.0f}%']
                    for x in Wj['sensors']]
            t = table(doc, hdr, rows, [3.6, 1.7, 3.3, 2.4, 3.3, 2.7], size=9.5)
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            para(doc, 4)
        elif kind == 'img':
            p = para(doc, 2, before=4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(figs[b[1]], width=Cm(b[2]))
        elif kind == 'cap':
            p = para(doc, 6); p.paragraph_format.keep_with_next = (b[1].startswith('Table'))
            run(p, numref(b[1], numbers), italic=True, size=10, color='52606D')
        elif kind == 'pb':
            p = para(doc, 0); p.add_run().add_break(__import__('docx').enum.text.WD_BREAK.PAGE)
    heading(doc, 'Method references', 12, color='2E6DB4', before=10)
    p = para(doc, 2); run(p, 'Frontier methods (2018–2026)', bold=True, size=10, color='1F3864')
    for r_ in FRONTIER:
        p = para(doc, 1, 0.5); run(p, r_, size=9.5, color='52606D')
    p = para(doc, 2, before=4); run(p, 'Classic methods', bold=True, size=10, color='1F3864')
    for r_ in REFS:
        p = para(doc, 1, 0.5); run(p, r_, size=9.5, color='52606D')
    p = para(doc, 2, before=4)
    run(p, 'Each reference was checked against publisher, proceedings or index records. The 30 key papers of 2020–2026 on '
           'which the innovations of the State of the Art build are listed there.', italic=True, size=9.5, color='52606D')

    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh, ensure_ascii=False)
    omml.main(draft, eq_json, out)
    od = os.path.dirname(os.path.abspath(out))
    for k in figs:
        os.replace(figs[k], os.path.join(od, f'fig_method_{k}.png'))
    print('saved', out, '|', n_main, 'numbered equations +', n_ann, 'in Annex A,', len(E.items) - n_main - n_ann, 'inline |', vals)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Methodology_v3.docx')
