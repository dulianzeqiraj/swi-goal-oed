"""CERTAIN-COAST: the state-of-the-art methodology for the NATO SPS Multi-Year Project form, drawn from reviews I-IX
(GARANCIA-GO ... FSHEHTA-GO), the SHIU-GO and RINDERTIMI-GO notes and CERTAIN-COAST Methodology v3.

It answers three questions for the applicants:
1. what the 2027-1 call, the official sample application form and the MYP Handbook require (checked on nato.int,
   6 November 2026), and how long each part may be (word limits per field; there is no page limit for the proposal);
2. which points of the current form text (build_application.py) disagree with the 2027-1 call;
3. the methodology itself, as ready-to-paste texts for the fields that carry it (word limits checked), with a figure of
   the method chain and a table that ties each innovation to its tested evidence and to its task.

The texts keep the work packages, task numbers, deliverables and milestones of the other CERTAIN-COAST documents, so the
Gantt chart and the deliverable list stay valid. The form text itself is not changed.

usage: python build_nato_method.py OUT.docx"""
import os
import re
import sys
import tempfile

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', '..', 'rindertimi_go'))
from build_sota import para, heading, table, shade, link  # noqa: E402
from build_application import words, put, answer, head_repeat, ph_cells, NAVY, GREY, SHORT  # noqa: E402
import build_budget as BB  # noqa: E402

CALL = 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/SPS-Call4proposals-2027-1.pdf'
FORM = 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/2023/sps-myp-sample-application-form.pdf'
HANDBOOK = 'https://www.nato.int/content/dam/nato/webready/documents/sps/grants/2023/SPS_MYP_Handbook.pdf'
MANAGING = ('https://www.nato.int/en/about-us/organization/nato-structure/science-for-peace-and-security-hub/'
            'managing-sps-grants')
PLATFORM = 'https://natosps.grantplatform.com/'

# ================================================================================================ the field texts
DELIVER = (
    'By the end of the 36 months the project will deliver:\n'
    '1. A coastal motion atlas and the relative sea level at each asset, from Sentinel-1 InSAR since 2014, corner reflectors '
    'and GNSS (D1.1).\n'
    '2. A monitoring network chosen for the warnings and handed over to the operators (D4.2): piezometers with conductivity '
    'loggers, a local rain gauge, GNSS, seismic nodes and, where access allows, fibre-optic sensing. Each sensor is bought '
    'only if its guaranteed value (band removed, years of safe operation added) is positive.\n'
    '3. One calibrated physical model of the coast that couples groundwater flow and salt, aquifer compaction, liquefaction '
    'under a moving water table and coastal water levels (D2.1), and a fast neural-operator copy with a certified error bound '
    'for every forecast (D2.2). The inputs and boundaries nobody measures (recharge coefficient, vadose delay, '
    'storage, sea-level and inland boundaries, dispersion width) are reconstructed from rain and heads, with '
    'bands that stay valid when the simulator or the rain product is wrong and when the climate drifts.\n'
    '4. Certified alarms for seawater intrusion, liquefaction and extreme water levels whose miss rate is bounded in advance '
    '(indicatively 5–10%), with a joint guarantee for the three assets, back-tested since 2014 and on '
    'storylines under a protocol published before the results (D3.1, D3.2).\n'
    '5. Decisions for the water utility: the effect of each wellfield\'s pumping on salinity with the hidden drought demand '
    'removed; the salinity under a drier recharge regime with conformal bands; the certified safe operating window and the '
    'year it closes; safe pumping tests that sharpen it; and a pumping rule agreed with the utility.\n'
    '6. Twelve months of live bulletins with the water utility, the port authority, the landfall operator and civil '
    'protection, with every outcome logged and the miss rates verified (D5.1); operating procedures and a policy brief '
    '(D6.2); open software and data with a DOI (D6.1).\n'
    'How this advances the state of the art. The alarms bring together methods published in 2023–2026 (online conformal '
    'calibration under shift, guarantees within regimes, extreme conformal prediction, anytime-valid verification) and apply '
    'them to coupled coastal hazards. Four contributions are new and were tested before the project. (i) Guarantees for '
    'quantities nobody measures: boundaries and inputs known only through rain, calibrated on simulated aquifers and on '
    'measured anchor periods, with a computable floor that shows how close each band is to the narrowest possible. (ii) The '
    'value of a sensor as the guaranteed band it removes and the years of safe operation it adds; in tests a tide gauge '
    'rated useful by a standard ensemble widened the guaranteed recharge band by 16–21%. (iii) Pumping effects free of '
    'hidden confounding: the heads, with the known drawdown added back, read the recharge, and removed the bias that '
    'drought-driven pumping causes, where substitutes built from the pumping history kept almost all of it. (iv) The '
    'certified safe operating window and safe pumping tests chosen for the years they add. The integrated system reaches '
    'TRL 6, demonstrated with the operators on site.')

HOW = (
    'The work is organised in seven work packages over 36 months, in three phases separated by evidence gates whose '
    'thresholds are fixed in advance. Every model output used for a decision carries a stated guarantee, checked before it '
    'is used.\n'
    'Observe and measure (Months 1–12). WP4 designs the network before buying it: each candidate sensor (piezometer with '
    'conductivity logger, local rain gauge, GNSS, seismic node) is ranked by the guaranteed width of warning band it removes '
    'and the years of safe operation it adds per euro, computed before field data exist (D4.1, '
    'Month 6); one logger is placed next to the wellfield most exposed to local demand. WP1 obtains vertical land motion and '
    'relative sea level at each asset from Sentinel-1 InSAR since 2014, corner reflectors and GNSS, and the head limit for '
    'pumping from aquifer compaction.\n'
    'Model and certify (Months 4–30). WP2 builds one coupled model in stages (flow and salt, then compaction and '
    'liquefaction). The inputs and boundaries nobody measures are reconstructed from the rain and the heads by a generative '
    'prior with an ensemble update. Their bands are calibrated on simulated aquifers that carry the errors of the rain '
    'product and on measured anchor periods, so they stay valid if the simulator is wrong; under drift the calibration is '
    'matched to the forecast horizon, and a computable floor shows how far each band is from the narrowest possible. Gate '
    'MS3 (Month 18) requires held-out heads, chloride, InSAR and seismic velocity inside the 90% intervals. A neural-operator '
    'copy with a certified error bound then serves the warnings. WP3 agrees thresholds and tolerable miss rates with the '
    'operators, builds the alarms and back-tests the chain since 2014 under a protocol registered before the results; gates '
    'MS4 (Month 22) and MS5 (Month 27) decide live operation and confirm the miss rates.\n'
    'Decide, operate and hand over (Months 18–36). WP5 estimates what each wellfield\'s pumping does to the salinity with the '
    'hidden drought demand removed: the heads, with the drawdown measured in pumping tests added back, read the recharge, '
    'and a calibrated check rejects any substitute that misses a confounder. It computes the salinity under a drier '
    'recharge regime with conformal bands, the certified safe operating window and its closing year, and safe pumping tests '
    'that sharpen it, and agrees a pumping rule with the utility. It runs the system live for twelve months and verifies the '
    'miss rates with anytime-valid tests. WP6 trains early-career researchers and operator staff, releases the open software '
    'and transfers the method to a coast in the partner country. WP7 manages data access, security classification, risks '
    'and reporting.\n'
    'Collaboration. The Albanian team leads WP1–WP5 and WP7; the partner-country team leads WP6, a transfer study on its own '
    'coast and a user-side review of the bulletins. Early-career researchers of both countries work across work '
    'packages, with two-month exchanges. End-users set thresholds, join a dry run and co-sign '
    'operational milestones; a steering committee with them meets every six months, and each gate has a named fallback.')

SOTA = (
    'Related research outside the project team (2020–2026):\n'
    '• Coastal groundwater under climate change and pumping. Rising sea level lifts the water table and extends flooding '
    'inland (Befus et al., 2020); 250,000 coastal wells in the US show where heads lie below sea level (Jasechko et al., 2020); '
    'by 2100 recharge sets the severity of intrusion and sea level its prevalence (Adams et al., 2024); ensemble-based '
    'pumping optimisation handles parameter and climate uncertainty (Coulon et al., 2024); machine-learned surrogates '
    'predict intrusion fast (Jiang, Liu and Dwivedi, 2025). These studies give scenarios without guarantees and treat the '
    'pumping as known and exogenous.\n'
    '• Inputs and boundaries from sparse data. Ensemble and diffusion-based inversion (Zheng et al., 2025; Yao et al., '
    '2025), global recharge from satellites and machine learning (Soylu, Entekhabi and Bras, 2026) and the evaluation of '
    'gridded rain products (Abbas et al., 2026) estimate what is not measured, but give no calibrated guarantee for it, and '
    'the errors of the rain product do not enter the uncertainty of the boundaries.\n'
    '• Guarantees for forecasts and surrogates. Conformal risk control (Angelopoulos et al., 2024), online calibration under '
    'shift (Gibbs and Candès, 2024; Feldman et al., 2023), robustness to distribution shift (Aolaritei et al., 2025), '
    'conformal neural operators (Ma et al., 2024), extreme conformal prediction (Pasche, Lam and Engelke, 2026), the expected '
    'size of conformal sets (Dhillon, Deligiannidis and Rainforth, 2024) and anytime-valid inference (Ramdas et al., 2023). '
    'They calibrate on observed outcomes; none gives a guarantee for a boundary that is never observed, asks how narrow such '
    'a guarantee can be, or how many years ahead it holds under drift.\n'
    '• Monitoring design. Machine-learning frameworks rank wells for long-term monitoring by predictive skill (Meray et '
    'al., 2022), not by the guaranteed band a sensor removes or the years of safe operation it adds.\n'
    '• Hidden confounding over time and counterfactuals. The Time Series Deconfounder infers substitutes for hidden '
    'confounders from many treatments over time (Bica, Alaa and van der Schaar, 2020); proxy methods (Mastouri et al., '
    '2021), synthetic interventions (Agarwal, Shah and Shen, 2026), conformal intervals for individual effects (Alaa, Ahmad '
    'and van der Laan, 2023), policy counterfactuals (McKay and Wolf, 2023), causal dose curves (Singh, Xu and Gretton, '
    '2024) and adjoint attribution in the ocean (Fukumori, Wang and Fenty, 2021) complete the picture. Their substitutes '
    'are built from the treatments or their history, so they cannot see the fresh weekly news of a confounder such as a '
    'heat wave that makes every farmer pump, the single-cause assumption cannot be tested, and none uses a physical '
    'measurement of the confounding path.\n'
    '• Vertical land motion and coastal exposure from InSAR and GNSS (Ohenhen et al., 2023); the 2019 earthquake at Durrës '
    'and its liquefaction (Mavroulis, Lekkas and Carydis, 2021).\n'
    'What none of these does. No study combines intrusion, liquefaction and extreme water levels in one model with warnings '
    'whose miss rate is stated in advance; gives guarantees for the boundaries and inputs of an aquifer known only through '
    'rain that stay valid when the simulator is wrong; values a sensor by the guaranteed band it removes and the years of '
    'safe operation it adds; estimates the effect of pumping on salinity with the hidden drought demand read from the heads; '
    'or computes when a safe way of operating the assets ends. A final check in bibliographic databases will be made before '
    'submission.\n'
    'Related activities of the project participants: [list proposed, ongoing or recently completed projects of the '
    'Co-Directors on related topics, with dates and budgets, or write "none"]. The preparatory technical work of the NPD\'s '
    'team in 2026 (nine reviews with tests, a calibrated chloride model of the Fushë-Kuqe aquifer) is the starting point of '
    'the project, not a separately funded activity.\n'
    'Other activities at the site known to the applicants: [list any national, EU or donor projects on subsidence, the port '
    'or the water supply of Durrës, or write "none known"].\n'
    'What makes CERTAIN-COAST stand out: one model for three hazards at three critical assets, warnings and pumping '
    'decisions whose error is stated in advance and verified in operation, and a certified planning horizon for the '
    'operators.')

STATUS = (
    'The approach has been tested in preparatory work by the NPD\'s team (2026), on synthetic coastal aquifers and on the '
    'calibrated chloride model of the Fushë-Kuqe aquifer, which supplies Durrës:\n'
    '• Boundaries known only through rain: on 500 simulated aquifers with rain and four loggers, the raw ensemble missed '
    '17–20% of the weeks (the recharge coefficient 67%); the calibrated bands met the 10% target (0.095–0.100) with '
    'whole-function coverage 0.90.\n'
    '• A wrong simulator: bands calibrated on simulations broke under a 35-day vadose delay, shifted parameters or a rain '
    'bias (risk 0.11–0.83); calibrated on 10–40 measured anchors they stayed at or below 10% under every law tested. At least '
    '9 anchors are needed for an average guarantee and 22 for a 90% certificate.\n'
    '• Drift: horizon-matched bands kept the risk at 0.003–0.082 up to 20 years ahead under no, linear and abrupt drift; '
    'with 30 anchor years a band exists only up to 17 years ahead.\n'
    '• The rain product: a local gauge with one logger identified the recharge coefficient better (error 0.045) than the '
    'product with eight loggers (0.108).\n'
    '• The floor: the guaranteed band with 20 anchors was 1.34–1.54 times the narrowest possible band; four loggers removed '
    '82–94% of the rain-only floor.\n'
    '• Value of a sensor: a tide gauge that a standard ensemble said would narrow the recharge band by 15% widened the '
    'guaranteed band by 16–21%; the sign of the guaranteed value was predicted for 36 of 36 instrument–goal pairs.\n'
    '• Counterfactual salinity at Fushë-Kuqe (calibrated model, documented facts): with 40% less recharge the shallow area '
    'above 250 mg/L chloride would grow from 31 to 65 km² (effect +33 km², conformal band 15–49 km²); the dispersion width '
    'carries 62% of the uncertainty of that effect; coverage on 300 simulated test sets was 0.887–0.900.\n'
    '• Pumping and hidden drought demand: in a linear coastal test bed with eight wells, the summed effect of pumping on '
    'salinity (true value 0.94) was overstated by 0.59 without adjustment, by 0.56 with a substitute built from the pumping '
    'history (as in the Time Series Deconfounder) and by 0.00 with the recharge read from the heads; the physics check had '
    'size 6% and power 99–100%.\n'
    '• Alarms and operating window: an alarm with an extreme-aware margin kept the share of seasons above the chloride limit '
    'at 4–9% across drought, human-feedback and compound storylines, where a static alarm allowed 13–21%; the certified safe '
    'operating window closed after 38 years, while plans that watch one hazard believed they had 43–97 years; safe pumping '
    'tests chosen for the years they add raised the certified closing year from 10.8 to 31.9 years (true value 45) with '
    'chloride below 123 mg/L in 95% of runs; the anytime-valid test wrongly flagged a correctly calibrated alarm in 2.2% of '
    'runs, against 68% for re-checking a 95% bound after every event.\n'
    'These are tests on synthetic coasts and on the existing chloride model with illustrative values, not results at Durrës; '
    'the project calibrates and verifies them on site.\n'
    'Starting data: Sentinel-1 radar images since 2014 (free and open), tide-gauge records, the wells and chemical records of '
    'the water utility, and the mapped liquefaction of the 2019 earthquake (Mavroulis et al., 2021).\n'
    'Team: [summarise the Co-Directors\' prior research on seawater intrusion, coastal geodesy, geotechnics and statistics, '
    'with 3–5 key publications].')

WORKPLAN = (
    'Sequencing: Phase 1, observe and measure (Months 1–12); Phase 2, model and certify (Months 4–30); Phase 3, decide, '
    'operate and hand over (Months 18–36). Gates MS3 (Month 18), MS4 (Month 22) and MS5 (Month 27) decide whether each next '
    'step starts. Every guarantee is checked on simulated test sets and on held-out field data before it is used.\n'
    'WP1, Coastal motion and relative sea level (Months 1–36; NATO-country team). Steps: Sentinel-1 InSAR time series since '
    '2014 (T1.1); corner reflectors and GNSS at the assets (T1.2); trajectory model including the 2019 earthquake and the '
    'relative sea level at each asset (T1.3); elastic and inelastic compaction and the head limit for pumping (T1.4). '
    'Risk: loss of radar coherence on soft ground; mitigation: corner reflectors and scatterers on structures. Milestone: '
    'MS2 (Month 12).\n'
    'WP2, One coupled model and its certified fast copy (Months 4–24; NATO-country team). Steps: model set-up (T2.1); '
    'coupling of flow, salt, compaction and liquefaction (T2.2); calibration (T2.3): the rain reaches the aquifer through a '
    'stochastic soil-water and vadose-delay model learned from irregular head records; the inputs and boundaries nobody '
    'measures (recharge coefficient, vadose delay, storage, sea level, inland inflow, initial head, dispersion width) are '
    'reconstructed by a function-space diffusion prior with an ensemble update through the exact solver; the errors of the '
    'rain product are simulated in the prior; bands are calibrated by conformal risk control on simulated aquifers and '
    'checked on measured anchor periods; neural-operator surrogate with a certified error bound (T2.4). Risk: the model '
    'fails validation; mitigation: build in stages and fall back to two-dimensional sections with a wider error bound. '
    'Risk: the anchors are too few (at least 9 are needed for an average guarantee, 22 for a 90% certificate); mitigation: '
    'anchors from the record since 2014 and from the new loggers, and a wider simulation-calibrated band reported as such. '
    'Milestones: MS3 (Month 18), MS4 (Month 22).\n'
    'WP3, Certified multi-hazard alarm (Months 13–34; NATO-country team). Steps: thresholds and tolerable miss rates with '
    'the operators (T3.1); alarm margins and proofs (T3.2), with anchor calibration so that the guarantee does not depend on '
    'the simulator, horizon matching under drift, and the floor that shows how far each band is from the narrowest '
    'possible; joint guarantee and allocation of tolerances (T3.3); back-testing (T3.4); verification in operation (T3.5). '
    'Risk: too many false alarms; mitigation: acceptable rates agreed in advance and tolerances allocated by consequence. '
    'Risk: drift faster than the record allows; mitigation: report the longest horizon for which a band exists. Milestone: '
    'MS5 (Month 27).\n'
    'WP4, Monitoring network designed for the warnings (Months 1–36; NATO-country team). Steps: design (T4.1), in which each '
    'candidate sensor is valued by the guaranteed band it removes, its floor and the years of safe operation it adds per '
    'euro, with a local rain gauge among the candidates and one logger next to the wellfield most exposed to local demand; '
    'procurement and installation (T4.2); operation and maintenance (T4.3); seismic velocity as a water-table gauge (T4.4). '
    'Risk: procurement delays and limited site access; mitigation: early orders, inductions with security officers. '
    'Milestones: MS1 (Month 6), MS2 (Month 12).\n'
    'WP5, Live demonstration and decisions (Months 18–36; NATO-country team). Steps: dry run (T5.1); twelve months of '
    'bulletins (T5.2); safe operating window and pumping rule (T5.3): the effect of each wellfield\'s pumping on salinity is '
    'estimated with the hidden drought demand removed, by reading the recharge from the heads after adding back the '
    'drawdown measured in the pumping tests, and a calibrated check of every substitute is run before any effect is '
    'reported; the salinity under a drier recharge regime is computed from the calibrated state with conformal bands; the '
    'certified window, its closing year and safe pumping tests that sharpen it follow, and the rule is agreed with the '
    'utility; post-event protocol (T5.4). Risk: no strong event occurs; mitigation: verification by back-testing and '
    'storylines. Risk: drawdown coefficients from the pumping tests are uncertain; mitigation: their uncertainty is carried '
    'into the effect as a stated bias band. Milestones: MS6 (Month 34), MS7 (Month 36).\n'
    'WP6, Training, transfer and dissemination (Months 1–36; partner-country team): early-career researchers and a training '
    'school (T6.1), operator training (T6.2), open release (T6.3), transfer to a second coast (T6.4).\n'
    'WP7, Management, data and risk (Months 1–36; coordinator): management and reporting (T7.1), data plan and access '
    'agreements (T7.2), risk register (T7.3).')

LIMITS = {'What will the project deliver': (DELIVER, 500), 'How will the project reach the planned end state': (HOW, 500)}

# ================================================================================================ references (S field)
REFS = [
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
]

# ================================================================================================ what NATO requires
RULES = [
    ['Submission', 'Only through the SPS grant platform; full proposals by **15 November 2026, 23:59 CET**; data of '
                   'incomplete applications are lost after the deadline; SPS advises against last-minute submission.',
     'Call 2027-1, pp. 3 and 5'],
    ['State of the art', '"Applicants must map the state-of-the art and identify how their idea innovates on existing '
                         'academic and industrial efforts", "clearly mention how they differ from ongoing work by the '
                         'project team and others, using appropriate and recent literature references"; mapping the state '
                         'of the art "may not be the objective of a proposed activity, nor a significant component of its '
                         'implementation".', 'Call 2027-1, p. 4'],
    ['Technology readiness', '"Project results should aim to reach Technology Readiness Levels 3-6, improving on the state of '
                             'the art, including upon commercial off-the-shelf solutions."', 'Call 2027-1, p. 4'],
    ['Duration', 'Typically 24 to 36 months; shorter if justified; procurement time must be in the timeline.',
     'Call 2027-1, p. 4'],
    ['Budget', 'No hard limit; 36-month projects are typically about €400,000 (the form: €250,000–400,000); each '
               'Co-Director\'s institution gets a part; co-financing up to one third of the grant is reasonable.',
     'Call 2027-1, p. 5; form, p. 4'],
    ['Eligibility', 'A NATO-country Project Director resident and employed in a NATO country, a Partner-country Project '
                    'Director resident and employed in an eligible partner country, non-profit institutions, one proposal '
                    'per Co-Director per call, no other ongoing SPS grant as Co-Director.', 'Call 2027-1, pp. 2 and 5'],
    ['Supporting documents', 'Project schedule (Gantt), an end-user commitment letter for each end-user, a brief overview of '
                             'the institutions, and the NATO templates: Detailed Budget (Excel), Acceptance of Funds, '
                             'Agreement for Joint Research, IPR agreement or waiver (the IPR may follow approval).',
     'Call 2027-1, p. 4; Handbook, p. 5'],
    ['Evaluation', 'The SPS office and the Independent Scientific Evaluation Group (ISEG); proposals it recommends go to the '
                   'Partnerships and Cooperative Security Committee; a decision can take up to nine months; overlap and '
                   'duplication are evaluation criteria.', 'Call 2027-1, pp. 3–4; form, p. 4'],
    ['Reporting', 'A milestone after the first six months and at least one milestone, with a progress report, every 12 '
                  'months.', 'Handbook, p. 7'],
]

FIELDS = [
    ['Project title', 'about 100 characters', 'understandable to non-experts', '≤ 100 characters'],
    ['Project short title', '80 characters', 'same as cell E2 of the budget workbook', '—'],
    ['What security challenge(s) would your project address?', '500 words', 'a clear link to security', '450–500 words'],
    ['What technical challenge(s) would your project address, if any?', '500 words', 'well-defined technical challenges',
     '450–500 words'],
    ['What will the project deliver or develop by the end of the grant?', '500 words',
     '"how the proposed solution will advance the state-of-the-art"', '**text 5.1** (495 words)'],
    ['How will the project reach the planned end state?', '500 words',
     '"methodology, approach, and how the different project teams will collaborate"', '**text 5.2** (498 words)'],
    ['State-of-the-art: Related Projects / Duplication', 'none stated',
     'related or competing external efforts; own related activities; overlap; references', '**text 5.3**; 600–900 words '
                                                                                            'and references'],
    ['Project abstract', '200 words', 'comprehensible to the non-expert', '≤ 200 words'],
    ['Current status', 'none stated', 'participants\' research and starting point, with references',
     '**text 5.4**; 300–600 words'],
    ['Impact', '500 words', 'quantitative where possible', '450–500 words'],
    ['Work-plan', 'none stated', 'steps, sequencing, methods per step, risks, milestones', '**text 5.5**; '
                                                                                            '700–1,500 words'],
    ['Key Performance Indicators (KPIs)', '500 words', 'deliverables and milestones that show success', '≤ 500 words'],
    ['Criteria for success', 'about 7 at most; weights sum to 100%', 'SMART, quantitative, results not preconditions',
     '≤ 7'],
    ['Research focus and expertise of the NPD and of the PPD', '500 words each', '—', '300–500 words'],
    ['Brief overview of participating institutions (upload)', '**1 page per institution**', 'capabilities, resources, '
                                                                                             'facilities, websites',
     '1 page each'],
    ['Project schedule (upload)', 'none stated', 'Gantt: duration, dependencies, milestones, deliverables', '1–2 pages'],
    ['File that helps to illustrate the project (optional upload)', 'none stated', '—', '≤ 6 pages, with figures'],
]

FIXES = [
    '**Technology readiness.** The current form text selects "TRL 7 or higher" and says the system "moves from technology '
    'readiness level 3 to 7". The 2027-1 call asks that results "aim to reach Technology Readiness Levels 3-6". The texts '
    'below therefore say TRL 6 ("Technology demonstrated in relevant environment"), from TRL 3 at the start (methods tested '
    'on synthetic coasts). [Your decision: keep TRL 7 with a justification, or select TRL 6 in the dropdown and change the '
    'TRL description.]',
    '**One round, full proposal.** The form text says that Multi-Year Projects are evaluated in two phases. The 2027-1 call '
    'states: "Full proposals must be submitted 15 November 2026 (23:59 CET)". Fill every field now; the handbook\'s mention '
    'of phase 1 and phase 2 reviews does not change this deadline.',
    '**Partner-country Project Director.** Without a PPD resident and employed in an eligible partner country the '
    'application is not eligible (call, p. 2). The form text still marks this as missing. Eligible partner countries '
    'include Bosnia and Herzegovina, Serbia, the Republic of Moldova, Georgia, Ukraine, Austria, Switzerland, Ireland, '
    'Malta, Israel, Jordan, Morocco, Tunisia and Egypt (full list in the call).',
    '**Budget.** The CERTAIN-COAST budget totals €{total:,.0f}, within the typical range; the call asks that each '
    'Co-Director\'s institution be allocated a part of it, so the PPD\'s institution needs its own lines in the Excel '
    'workbook.',
]

# the innovations and where they enter CERTAIN-COAST
MAP = [
    ['SHIU-GO note: stochastic rain–recharge forcing learned from irregular, incomplete head records',
     'The rain enters as a stochastic system (soil water, vadose delay, recharge error), not a fixed transfer',
     'Forecast loss above the optimum 9%, against 80% (linear transfer) and 262% (Gaussian forcing); 90% intervals cover 88%',
     'WP2, T2.3'],
    ['RINDËRTIMI-GO note: all boundary conditions from rain with a function-space diffusion prior',
     'Sea level, inflow, recharge and initial head reconstructed jointly; heads enter through an ensemble update with the '
     'exact solver', 'Rain only: error 0.97–1.11 times the exact posterior; plain guidance missed the heads by 24.5 cm, the '
                     'update fits them to 2.1 cm', 'WP2, T2.3'],
    ['Review I, GARANCIA-GO', 'Guaranteed bands for boundaries never observed: calibration pairs simulated from the physical '
                              'prior', 'Raw ensemble misses 17–20% of the weeks (recharge coefficient 67%); calibrated '
                                       '9.5–10%, whole-function coverage 0.90', 'WP2, T2.3; WP3, T3.2'],
    ['Review II, MATJA-GO', 'The guaranteed value of a measurement: the band it removes, with the choice recalibrated',
     'Tide gauge: −15% promised by the ensemble, +16–21% guaranteed widening; sign predicted for 36/36 pairs',
     'WP4, T4.1'],
    ['Review III, RESHJA-GO', 'Rain-product errors inside the guarantees; a floor for the recharge coefficient that loggers '
                              'cannot remove', 'Naive κ band misses 70–76%; aware 9.3–10.3%; gauge and one logger 0.045 '
                                               'against product and eight loggers 0.108', 'WP2, T2.3; WP4, T4.1'],
    ['Review IV, ANKORA-GO', 'Guarantees that hold for any real law, calibrated on measured anchors',
     'Simulation calibration breaks under shift (0.11–0.83); 10–40 anchors stay ≤ 0.10; at least 9 anchors (22 for a 90% '
     'certificate)', 'WP3, T3.2 and T3.4'],
    ['Review V, PRIRJA-GO', 'Guarantees for a stated number of years ahead under drift', 'Risk 0.003–0.082 up to 20 years; '
                                                                                         'with 30 anchor years a band exists '
                                                                                         'only to 17 years', 'WP3, T3.2; '
                                                                                                             'WP5, T5.3'],
    ['Review VI, DYSHEMEJA-GO', 'The floor: no valid band can be narrower; computable before field data', '20-anchor band '
                                                                                                         '1.34–1.54 times '
                                                                                                         'the floor; four '
                                                                                                         'loggers remove '
                                                                                                         '82–94% of the '
                                                                                                         'rain-only floor',
     'WP3, T3.2; WP4, T4.1'],
    ['Review VII, SHKAKU-GO', 'Guaranteed counterfactual bands (what would have happened under another rain)',
     '40% drought lowers the head at the well by 1.94 m (floor half-width 0.088 m); the robust union is valid in every case '
     '(≤ 0.084)', 'WP5, T5.3'],
    ['Review VIII, KRIPA-GO', 'Counterfactual salinity on the calibrated Fushë-Kuqe chloride model; the share of the '
                              'dispersion', '40% less recharge: shallow area > 250 mg/L 31 → 65 km² (+33, band 15–49); '
                                            'dispersion width 62% of the variance; coverage 0.887–0.900', 'WP5, T5.3; '
                                                                                                         'WP2, T2.2'],
    ['Review IX, FSHEHTA-GO', 'Pumping effects with hidden confounders read from the heads; a calibrated physics check',
     'Bias of the summed well effects +0.59 unadjusted, +0.56 history substitute, 0.00 physics; check size 6%, power '
     '99–100%', 'WP5, T5.3; WP4, T4.1'],
    ['CERTAIN-COAST Methodology v3 (C1–C3)', 'Certified safe operating window; years of safe operation per sensor; safe '
                                            'pumping tests chosen for the years they add', 'Window closed after 38 years '
                                                                                           '(single-hazard plans: 43–97); '
                                                                                           'tests raised the closing year '
                                                                                           'from 10.8 to 31.9 (true 45)',
     'WP4, T4.1; WP5, T5.3'],
]


# ================================================================================================ figure
def fig_chain(path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from rgo_figs import Canvas, INK, MUTED
    BLUE, ORANGE, AQUA, VIOLET = '#2a78d6', '#eb6834', '#1baf7a', '#6250d6'
    cv = Canvas(170, 100)

    def box(x, y, w, h, title, lines, foot, ec, fc):
        cv.box(x, y, w, h, fc, ec, lw=1.1, r=1.8)
        cv.text(x + 2.2, y + h - 3.8, title, ha='left', size=9.0, weight='bold', color=INK)
        for k, ln in enumerate(lines):
            cv.text(x + 2.2, y + h - 8.9 - 4.4 * k, ln, ha='left', color=INK)
        cv.text(x + 2.2, y + 2.6, foot, ha='left', color=MUTED)

    def arr(x0, y0, x1, y1, c, ls='-'):
        cv.ax.annotate('', xy=(x1, y1), xytext=(x0, y0), zorder=25, arrowprops=dict(
            arrowstyle='-|>', color=c, lw=1.1, ls=ls, shrinkA=0, shrinkB=0, mutation_scale=8))
    # data
    cv.text(2, 97, 'Data', ha='left', size=9.4, weight='bold', color=MUTED)
    data = [(88, 'rain, local gauge'), (77, 'head, salinity loggers'), (66, 'InSAR, GNSS, tide gauge'),
            (55, 'seismic nodes, chloride'), (17, 'pumping logs and tests')]
    for y, d in data:
        cv.box(2, y - 4, 40, 8, '#eef0f2', '#5b6672', lw=0.9, r=1.6)
        cv.text(22, y, d)
    # the three pillars
    box(48, 66, 80, 28, '1  Guaranteed reconstruction (WP2, WP3)',
        ['inputs and boundaries from rain and heads', 'valid with a wrong simulator or rain product',
         'and under drift; a floor shows the limit'], 'reviews I, III–VI; SHIU-GO, RINDËRTIMI-GO', BLUE, '#e3eefb')
    box(48, 38, 80, 22, '2  Value of a measurement (WP4)',
        ['guaranteed band removed, years added', 'network chosen before it is bought'], 'review II; CERTAIN-COAST C2',
        AQUA, '#e2f5ee')
    box(48, 2, 80, 30, '3  Causal and counterfactual (WP5)',
        ['pumping effects without hidden confounding', 'salinity under a drier recharge regime',
         'safe operating window, safe pumping tests'], 'reviews VII–IX; CERTAIN-COAST C1, C3', VIOLET, '#efecfb')
    # outputs
    cv.text(134, 97, 'For the operators', ha='left', size=9.4, weight='bold', color=MUTED)
    outs = [(84, 'certified alarms', 'miss rate stated'), (60, '12 months of', 'live bulletins'),
            (36, 'pumping rule', 'with the utility'), (12, 'open software', 'and hand-over')]
    for y, a, b in outs:
        cv.box(134, y - 7, 34, 14, '#fde9df', ORANGE, lw=1.0, r=1.6)
        cv.text(151, y + 2.4, a); cv.text(151, y - 2.6, b, color=MUTED)
    # arrows
    for y, _ in data[:4]:
        arr(42, y, 48, 80 + (y - 71) * 0.35, '#5b6672')
    arr(42, 17, 48, 17, '#5b6672')
    arr(88, 66, 88, 60, BLUE)
    arr(88, 38, 88, 32, AQUA)
    arr(128, 84, 134, 84, BLUE)
    arr(128, 72, 134, 62, BLUE)
    arr(128, 26, 134, 58, VIOLET)
    arr(128, 20, 134, 36, VIOLET)
    cv.fig.savefig(path, dpi=300)
    plt.close(cv.fig)


# ================================================================================================ document
def bullet(doc, text, size=10.5):
    p = para(doc, 3, 0.4)
    put(p, '• ' + text, size=size)
    return p


def main(out):
    rows = BB.compute()
    total = sum(r['tot'] for r in rows)
    for k, (t, lim) in LIMITS.items():
        assert words(t) <= lim, f'{k}: {words(t)} > {lim}'
    work = tempfile.mkdtemp()
    fpath = os.path.join(work, 'chain.png')
    fig_chain(fpath)

    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = s.bottom_margin = Cm(1.7)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(10.5)

    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    put(p, f'{SHORT} — the state-of-the-art methodology for the NATO SPS form', size=17, color=NAVY); p.runs[0].bold = True
    p = para(doc, 3); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    put(p, 'What the 2027-1 call and the official form require, how long each part may be, and the methodology drawn from '
           'reviews I–IX as texts ready to paste', size=11, color=GREY)
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    put(p, 'Dulian Zeqiraj · 6 November 2026 · Multi-Year Project, call 2027-1 · deadline 15 November 2026, 23:59 CET',
        size=9.5, color=GREY, italic=True)

    # ---------------------------------------------------------------------------------------------- 1 short answer
    heading(doc, '1. The short answer', 14, before=2)
    t = doc.add_table(rows=1, cols=1); t.style = 'Table Grid'
    c = t.rows[0].cells[0]; shade(c, 'EEF4FB'); c.width = Cm(17.0)
    items = [
        '**There is no page limit for the proposal.** It is an online form on the SPS grant platform; each long field has a '
        'word limit, and only the overview of the institutions has a page limit (one page per institution).',
        '**The methodology goes into two fields:** "How will the project reach the planned end state?" (500 words: '
        'methodology, approach, collaboration) and "Work-plan" (no stated limit: steps, methods, risks, milestones).',
        '**The state of the art goes into three fields:** "What will the project deliver…" (500 words; it must show how the '
        'project advances the state of the art), "State-of-the-art: Related Projects / Duplication" (no stated limit) and '
        '"Current status" (no stated limit). The call requires recent literature references and forbids making the mapping '
        'of the state of the art an objective of the project.',
        '**Recommended lengths** for the fields without a limit (ours, not NATO\'s): state of the art 600–900 words with '
        'references, current status 300–600, work-plan 700–1,500; an optional illustrative upload of at most six pages.',
        '**Section 5 gives the five texts ready to paste**, built from the nine reviews: deliverables (495 words), '
        'methodology (498 words), state of the art, current status and work-plan.']
    for k, it in enumerate(items):
        q = c.paragraphs[0] if k == 0 else c.add_paragraph()
        q.paragraph_format.space_after = Pt(4)
        put(q, '• ' + it, size=10.5)
    para(doc, 4)

    # ---------------------------------------------------------------------------------------------- 2 NATO requires
    heading(doc, '2. What NATO requires', 14, before=6)
    p = para(doc, 4)
    put(p, 'Checked on 6 November 2026 in the documents that the call itself names: the call for proposals 2027-1 '
           '(September 2026), the sample application form for Multi-Year Projects listed on the "Managing SPS grants" page '
           '(the current template), and the MYP Handbook (applicable to applications submitted from November 2023).')
    p = para(doc, 4)
    for k, (lab, url) in enumerate((('Call 2027-1', CALL), ('Sample application form', FORM), ('MYP Handbook', HANDBOOK),
                                    ('Managing SPS grants', MANAGING), ('SPS grant platform', PLATFORM))):
        if k:
            put(p, '  ·  ', size=10)
        link(p, url, lab, size=10)
    head_repeat(table(doc, ['Requirement', 'What the official text says', 'Source'], RULES, [3.0, 11.0, 3.0], size=9))
    para(doc, 4)
    heading(doc, 'The fields that carry the methodology and the state of the art, with their limits', 12, color='2E6DB4',
            before=6)
    tt = head_repeat(table(doc, ['Field of the form', 'Official limit', 'What the form asks', 'Recommended'], FIELDS,
                           [5.6, 3.0, 5.0, 3.4], size=8.8))
    for ri in (5, 6, 7, 9, 11):
        for cc in tt.rows[ri].cells:
            shade(cc, 'F2F7EC')
    q = para(doc, 3, before=3)
    put(q, 'Shaded rows: the fields of Section 5. The limits are those of the sample form; the platform\'s live form '
           'decides if it differs [check each word counter on the platform].', size=9, color=GREY, italic=True)

    # ---------------------------------------------------------------------------------------------- 3 fixes
    heading(doc, '3. Points of the current form text to align with the 2027-1 call', 14, before=8)
    for f in FIXES:
        bullet(doc, f.format(total=total))

    # ---------------------------------------------------------------------------------------------- 4 the method
    heading(doc, '4. The methodology in one picture', 14, before=8)
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    put(p, 'The nine reviews and the two notes add three pillars to the CERTAIN-COAST method. They keep its work packages, '
           'tasks, deliverables and gates, so the Gantt chart and the deliverable list stay valid: the new methods enter '
           'tasks T2.3, T3.2, T4.1 and T5.3.')
    p = para(doc, 2, before=4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(fpath, width=Cm(17.0))
    q = para(doc, 6)
    put(q, 'Figure 1. The method chain. (1) The inputs and boundaries that nobody measures are reconstructed from the rain '
           'and the heads with guarantees that survive a wrong simulator, a wrong rain product and drift. (2) Each sensor is '
           'valued by what it is guaranteed to buy before it is bought. (3) The decisions — what pumping does to the salt, '
           'what a drier climate would do, how long a safe operation lasts — are computed with the hidden confounding '
           'removed and with stated error.', size=9.5, italic=True)
    heading(doc, 'Where each innovation enters, and what was tested', 12, color='2E6DB4', before=6)
    head_repeat(table(doc, ['Innovation (source)', 'Step beyond the state of the art', 'Tested evidence (2026)', 'Task'],
                      MAP, [3.6, 5.2, 5.9, 2.3], size=8.6))
    q = para(doc, 3, before=3)
    put(q, 'The evidence comes from synthetic coastal test beds and, for review VIII, from the calibrated chloride model of '
           'Fushë-Kuqe with its documented facts; the code and results are in the repository (experiments/).', size=9,
        color=GREY, italic=True)

    # ---------------------------------------------------------------------------------------------- 5 texts
    heading(doc, '5. The texts, ready to paste', 14, before=8)
    p = para(doc, 4)
    put(p, 'Each text replaces the answer of the same field in CERTAIN-COAST_NATO_Application_Form_Text.docx. Yellow text is '
           'information only the applicants can give.')
    for num, name, text, lim in (('5.1', 'What will the project deliver or develop by the end of the grant?', DELIVER, 500),
                                 ('5.2', 'How will the project reach the planned end state?', HOW, 500),
                                 ('5.3', 'State-of-the-art: Related Projects / Duplication', SOTA, None),
                                 ('5.4', 'Current status', STATUS, None),
                                 ('5.5', 'Work-plan', WORKPLAN, None)):
        heading(doc, f'{num}  {name}', 12, color='2E6DB4', before=8)
        answer(doc, text, lim)
        if lim is None:
            q = para(doc, 2); put(q, f'{words(text)} words (no limit stated)', size=8.8, color='1E8A5A', italic=True)

    # ---------------------------------------------------------------------------------------------- 6 references
    heading(doc, '6. References for the state-of-the-art field', 14, before=10)
    p = para(doc, 4)
    put(p, 'Paste them at the end of text 5.3 (the form invites references). Most details come from the cards of reviews '
           'I–IX, which were checked through search results; check each one in a bibliographic database before '
           'submission.', size=10, color=GREY, italic=True)
    for txt, url in REFS:
        q = para(doc, 2, 0.4)
        put(q, txt + ' ', size=9.5)
        if url:
            link(q, url, url, size=9.5)
    doc.save(out)
    print('saved', out, '| words:', {k: words(t) for k, (t, _) in LIMITS.items()}, '| SOTA', words(SOTA), '| STATUS',
          words(STATUS), '| WORKPLAN', words(WORKPLAN), '| budget', total)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Methodology_for_the_NATO_Form.docx')
