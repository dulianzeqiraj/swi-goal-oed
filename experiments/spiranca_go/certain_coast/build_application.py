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
    'Durrës, on the Adriatic coast of Albania, concentrates three kinds of critical infrastructure of a NATO Ally within a few '
    'kilometres: the wellfields that supply drinking water, the Port of Durrës, from which 93.6% of Albania\'s seaborne freight '
    'left in the second quarter of 2025 (INSTAT), and an energy landfall where supply arrives from the sea. All three stand on '
    'soft coastal sediments that are sinking, close to active thrust faults, and the Mw 6.4 earthquake of 26 November 2019 '
    'caused liquefaction along this coast.\n'
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
    '1. The hazards are coupled but modelled apart. Seawater intrusion, aquifer compaction, liquefaction and coastal water '
    'levels depend on the same two variables, relative sea level and the water table, yet are computed by separate models. '
    'A pumping decision cannot be checked against all of them at once.\n'
    '2. Relative sea level must be known at each asset, not only at the tide gauge. The land at Durrës moves vertically by '
    'different amounts from place to place, including the 2019 coseismic step; this motion must be measured with satellite '
    'radar (InSAR) and GNSS and carried into every hazard model with its uncertainty.\n'
    '3. Physical models are too slow for warnings, and machine-learned copies come without a guarantee. Warnings need '
    'thousands of model runs a day. Neural-operator surrogates make this possible, but a surrogate used for safety must '
    'state its error for each forecast.\n'
    '4. No warning in this field states how often it misses. Recent statistical methods (online conformal prediction under '
    'distribution shift, guarantees that hold within regimes such as droughts, extreme conformal prediction for events rarer '
    'than the record, and anytime-valid verification) can provide such guarantees, but they have not been applied to coupled '
    'coastal hazards driven by slow physics, with dependent alarms and few extreme events.\n'
    'Two further problems have no published solution. There is no method to compute the set of pumping and dewatering '
    'decisions that keeps all the hazards within certified limits at once, nor the sea level or year at which this set '
    'disappears; tipping points exist for seawater intrusion alone, not for the coupled system. And monitoring networks are '
    'designed to reduce today\'s forecast errors; there is no criterion for how many years of safe operation a sensor buys.\n'
    'All of this must work on a real coast with incomplete records, under security restrictions on data, and in a form that '
    'the operators can run themselves after the project.')

DELIVER = (
    'By the end of the 36 months the project will deliver:\n'
    '1. A coastal motion atlas and the relative sea level at each asset, from Sentinel-1 InSAR since 2014, corner reflectors '
    'and GNSS (D1.1).\n'
    '2. A monitoring network chosen for the warnings (piezometers with conductivity loggers, GNSS, seismic stations and '
    'nodes, and fibre-optic sensing where access allows), installed, streaming and handed over to the operators (D4.2).\n'
    '3. One calibrated physical model of the coast that couples groundwater flow and salt, aquifer compaction, liquefaction '
    'under a moving water table and coastal water levels (D2.1), and a fast neural-operator copy with a certified error bound '
    'for every forecast (D2.2).\n'
    '4. Certified alarms for seawater intrusion, liquefaction and extreme water levels whose miss rate is bounded in advance '
    '(indicatively 5–10%), with a joint guarantee for the three assets, back-tested on the record since 2014 and on '
    'storylines beyond it under a protocol published before the results (D3.1, D3.2).\n'
    '5. A certified safe operating window: the pumping and dewatering decisions that keep all hazards within their limits at '
    'once, the year at which this window closes, and a pumping rule agreed with the water utility.\n'
    '6. Twelve months of live bulletins with the water utility, the port authority, the landfall operator and civil '
    'protection, with every outcome logged and the miss rates verified (D5.1); operating procedures and a policy brief '
    '(D6.2); open software and data with a DOI (D6.1).\n'
    'How this advances the state of the art. The alarms bring together methods published in 2023–2026 (online conformal '
    'calibration under shift, guarantees within regimes, extreme conformal prediction, joint calibration of several risks, '
    'anytime-valid verification) and apply them to coupled coastal hazards. Two contributions are new and were tested before '
    'the project: the certified safe operating window with its closing year (in a synthetic test it closed after 38 years, '
    'while plans that watch one hazard believed they had 43 to 97 years), and the value of a sensor in years of safe '
    'operation, which valued a GNSS station and corner reflectors at about five years each where the usual criterion gives '
    'zero. The integrated system moves from technology readiness level 3 to 7.')

HOW = (
    'The work is organised in seven work packages over 36 months, in three phases separated by evidence gates whose '
    'thresholds are fixed in advance.\n'
    'Observe and measure (Months 1–12). WP4 designs the network by ranking candidate sensors by how much they narrow the '
    'hazard forecasts and how many years of safe operation they add per euro (D4.1, Month 6), then installs it (Month 12). '
    'WP1 processes Sentinel-1 radar since 2014 with corner reflectors and GNSS to obtain the vertical land motion and the '
    'relative sea level at each asset, and fits aquifer compaction to find the head below which pumping causes permanent '
    'subsidence.\n'
    'Model and certify (Months 4–30). WP2 builds the coupled model in stages (flow, then salt, then compaction and '
    'liquefaction), calibrates it on heads, chloride, InSAR and seismic velocity with an ensemble smoother, and passes gate '
    'MS3 (Month 18) only if held-out observations fall inside the model\'s 90% intervals. It then trains a neural-operator '
    'copy whose error is certified for each forecast. WP3 agrees thresholds and tolerable miss rates with the operators, '
    'builds the alarms and back-tests the whole chain over the record since 2014 and on storylines, under a protocol '
    'registered with a DOI before the results. Gate MS4 (Month 22) decides live operation; gate MS5 (Month 27) confirms the '
    'miss rates.\n'
    'Operate, verify and hand over (Months 22–36). WP5 runs the system live for twelve months with the operators and civil '
    'protection, logs every bulletin with its outcome, verifies the miss rates with anytime-valid tests, computes the '
    'certified safe operating window, agrees a pumping rule with the utility and runs the post-event protocol after any '
    'earthquake or storm. WP6 trains early-career researchers and operator staff, releases the open software and transfers '
    'the method to a second coast in the partner country. WP7 manages data access, security classification, risks and '
    'reporting.\n'
    'Collaboration. The NATO-country team in Albania leads coastal motion, the network and live operation (WP1, WP4, WP5, '
    'WP7); the partner-country team leads the coupled model, the certified alarms and the transfer (WP2, WP3, WP6). '
    'Early-career researchers from both countries work across the work packages and spend two-month exchanges on site. The '
    'end-users set thresholds, take part in a dry run and co-sign the operational milestones. A steering committee with the '
    'end-users meets every six months, and each gate has a named fallback.')

SOTA = (
    'Related research outside the project team:\n'
    '• Groundwater rise as a coastal hazard: rising sea level lifts the water table, extending flooding inland (Befus et al., '
    '2020, Nature Climate Change) and raising liquefaction severity where the water table is shallow (Grant et al., 2021, ASCE '
    'Geo-Extreme 2021).\n'
    '• Seawater intrusion under sea-level rise: tipping points for intrusion (Mazi, Koussis and Destouni, 2013, Environmental '
    'Research Letters) and ensemble-based pumping optimisation under sea-level rise (Coulon et al., 2024, Hydrology and Earth '
    'System Sciences). Both treat intrusion alone.\n'
    '• Vertical land motion and coastal exposure from InSAR and GNSS (Ohenhen et al., 2023, Nature Communications).\n'
    '• Statistical guarantees for forecasts: online conformal prediction under distribution shift (Gibbs and Candès, 2024, '
    'Journal of Machine Learning Research), extreme conformal prediction (Pasche, Lam and Engelke, 2026, Extremes) and '
    'anytime-valid inference (Ramdas et al., 2023, Statistical Science).\n'
    '• The 2019 earthquake at Durrës and its liquefaction (Mavroulis, Lekkas and Carydis, 2021, Geosciences).\n'
    'None of these combines the three hazards in one model, issues warnings with a certified miss rate, or computes when a '
    'safe way of operating the assets ends. In our literature search we found no study that derives a joint intrusion, '
    'liquefaction and subsidence operating window with certified margins, or values a sensor in years of safe operation; a '
    'final check in bibliographic databases will be made before submission.\n'
    'Related activities of the project participants: [list proposed, ongoing or recently completed projects of the '
    'Co-Directors on related topics, with dates and budgets, or write "none"].\n'
    'Other activities at the site known to the applicants: [list any national, EU or donor projects on subsidence, the port '
    'or the water supply of Durrës, or write "none known"].\n'
    'What makes CERTAIN-COAST stand out: one model for three hazards at three critical assets, warnings whose miss rate is '
    'stated in advance and verified in operation, and a certified planning horizon for the operators.')

ABSTRACT = (
    'Near Durrës, Albania\'s main port, the wells that supply drinking water, the port itself and an energy connection from '
    'the sea stand on low ground that is slowly sinking, close to active faults. Three dangers threaten them: seawater '
    'entering the wells, ground that turns almost liquid in an earthquake, and the sea flooding the land in storms. The '
    'dangers are linked, because sinking land and rising seas worsen all three and pumping that protects against one can '
    'increase another, but today they are watched separately and no warning says how often it can be wrong.\n'
    'CERTAIN-COAST will watch them together. Satellites, GNSS and new ground sensors will feed one computer model of the '
    'coast, copied by a fast artificial-intelligence model whose error is stated for every forecast. Each warning will state '
    'in advance how often it may miss a dangerous event, and this will be checked in twelve months of live operation with the '
    'water utility, the port, the energy operator and civil protection. The project will also show how many years a safe '
    'way of operating the three assets together remains. Local operators will run the system afterwards.')

RELEVANCE = (
    'Link to security. The project protects three essential services of a NATO Ally (drinking water, a port that handles '
    'most of the country\'s seaborne freight, and an energy landfall) and serves three of NATO\'s seven baseline requirements '
    'for national resilience: resilient food and water resources, resilient civil transportation systems and resilient '
    'energy supplies, which also underpin civil support to the military. It falls under the 2027-1 topic "protection of '
    'critical infrastructure, supplies and personnel; maritime and undersea infrastructure resilience", and the energy '
    'landfall is where undersea infrastructure comes ashore.\n'
    'Use cases:\n'
    '• Water utility: cut or shift pumping before chloride reaches drinking-water wells (weeks to months ahead).\n'
    '• Port authority: restrict loads or operations and set inspection priorities after an earthquake; prepare for storm '
    'surges (hours to days ahead).\n'
    '• Energy landfall operator: inspect, protect or isolate the landfall when the ground or the water level threatens it.\n'
    '• Civil protection: one consistent bulletin for water, port and energy after an earthquake or a storm.\n'
    '• National authorities and resilience planners: the certified year from which no operating plan keeps the three assets '
    'safe together, and the sensors and measures that delay it most.\n'
    'Each bulletin states its certified miss rate, so decision-makers know how far it can be trusted. The method uses free '
    'satellite data and transfers to other subsiding coasts of Allies and partners with wellfields, ports and energy '
    'landfalls.')

STATUS = (
    'The approach has been tested in preparatory work on synthetic coasts:\n'
    '• On a coupled variable-density model of a coastal aquifer, an alarm with an extreme-aware margin kept the share of '
    'seasons above the chloride limit at 4–9% across drought, human-feedback and compound storylines, where a static alarm '
    'allowed 13–21%.\n'
    '• On a synthetic coastal transect, the certified safe operating window closed after 38 years, while plans that watch '
    'one hazard believed they had 43–97 years; a closed-form test for seawater reaching the wellfield agreed with a '
    'brute-force check in 200 of 200 cases.\n'
    '• In a simulation of live verification, re-checking a 95% bound after every event wrongly flagged at least one of six '
    'correctly calibrated alarms in 68% of runs; the anytime-valid test used by the project did so in 2.2%.\n'
    'These are tests on synthetic coasts with illustrative values, not results at Durrës; the project calibrates and '
    'verifies them on site.\n'
    'Starting data: Sentinel-1 radar images since 2014 (free and open), tide-gauge records, the wells and chemical records of '
    'the water utility, and the mapped liquefaction of the 2019 earthquake (Mavroulis et al., 2021).\n'
    'Team: [summarise the Co-Directors\' prior research on seawater intrusion, coastal geodesy, geotechnics and statistics, '
    'with 3–5 key publications].\n'
    'Key references: Gibbs and Candès (2024), JMLR 25(162); Pasche, Lam and Engelke (2026), Extremes 29(2); Befus et al. '
    '(2020), Nature Climate Change 10; Mazi, Koussis and Destouni (2013), Environmental Research Letters 8; Mavroulis, Lekkas '
    'and Carydis (2021), Geosciences 11(5).')

IMPACT = (
    'If the project succeeds, the following will change at Durrës and beyond:\n'
    '• Three hazards covered by one warning with a stated miss rate, where today there is none: seawater intrusion at the '
    'wellfields, liquefaction at the port and the landfall, and extreme water levels at all three.\n'
    '• Each alarm misses dangerous events no more often than its certified rate (indicatively 5–10%), shown by back-testing '
    'over the record since 2014 and checked in twelve months of live operation; the joint miss rate for the three assets is '
    'bounded by the sum of the rates.\n'
    '• Each operator knows in advance the minimum value of the warning for its own decisions, computed from the certified '
    'miss rate and the cost-loss ratio agreed with it.\n'
    '• The water utility operates its wells within a certified safe window, which lowers the risk of salinising wells that '
    'take years to recover and avoids new permanent subsidence; planners know the year from which the window closes and '
    'which measures extend it.\n'
    '• At least 20 operator and civil-protection staff (at least two per operator) trained and running the system; at least '
    'six early-career researchers trained in the NATO and partner countries.\n'
    '• A monitoring network of piezometers, GNSS, seismic stations and corner reflectors handed over to the operators, with '
    'a running cost of about €10,900 per year carried by them under a maintenance agreement.\n'
    '• Open software and data with a DOI, installed and reproduced by a group outside the consortium; at least six '
    'open-access papers; operating procedures adopted for each asset; a policy brief for the national authorities.\n'
    '• The method tested on a second coast in the partner country and ready for other subsiding coasts of the Adriatic and '
    'the Mediterranean.\n'
    'For NATO, the result is a tested capability for three baseline requirements of resilience at an Allied site, and a '
    'worked example of artificial intelligence used in a security decision chain with testing, evaluation, verification and '
    'validation built in.')

TRL_TEXT = (
    'Start: TRL 3. Each component has been shown in preparatory synthetic tests (alarm margins, safe operating window, '
    'verification), and published methods exist for each element.\n'
    'End: TRL 7. The integrated system (network, coupled model, certified surrogate, alarms and safe operating window) is '
    'demonstrated in its operational environment through twelve months of live operation with the water utility, the port '
    'authority, the landfall operator and civil protection.\n'
    'Two components end at TRL 6: seismic velocity as a coastal water-table sensor, and the pumping rule within the safe '
    'window, which are demonstrated at the site and agreed with the utility but not yet run for a full year.')

DATA = (
    'Data required and existing sources: Copernicus Sentinel-1 radar images since 2014 (free and open); GNSS records; the '
    'Durrës tide-gauge record of the State Authority for Geospatial Information (ASIG); heads, pumping and chloride records of the water utility; geotechnical records of the port and the landfall '
    'operator; records of existing national seismic stations; meteorological and wave data.\n'
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
    'Sequencing: Phase 1, observe and measure (Months 1–12); Phase 2, model and certify (Months 4–30); Phase 3, operate, '
    'verify and hand over (Months 22–36). Gates MS3 (Month 18), MS4 (Month 22) and MS5 (Month 27) decide whether each next '
    'step starts.\n'
    'WP1, Coastal motion and relative sea level (Months 1–36; NATO-country team). Steps: Sentinel-1 InSAR time series since '
    '2014 (T1.1); corner reflectors and GNSS at the assets (T1.2); trajectory model including the 2019 earthquake and the '
    'relative sea level at each asset (T1.3); elastic and inelastic compaction and the head limit for pumping (T1.4). '
    'Risk: loss of radar coherence on soft ground; mitigation: corner reflectors and scatterers on structures. Milestone: '
    'MS2 (Month 12).\n'
    'WP2, One coupled model and its certified fast copy (Months 4–24; partner-country team). Steps: model set-up (T2.1); '
    'coupling of flow, salt, compaction and liquefaction (T2.2); calibration with an ensemble smoother (T2.3); '
    'neural-operator surrogate with a certified error bound (T2.4). Risk: the model fails validation; mitigation: build in '
    'stages and fall back to two-dimensional sections with a wider error bound. Milestones: MS3 (Month 18), MS4 (Month 22).\n'
    'WP3, Certified multi-hazard alarm (Months 13–34; partner-country team). Steps: thresholds and tolerable miss rates with '
    'the operators (T3.1); alarm margins and proofs (T3.2); joint guarantee and allocation of tolerances (T3.3); '
    'back-testing (T3.4); verification in operation (T3.5). Risk: too many false alarms; mitigation: acceptable rates agreed '
    'in advance and tolerances allocated by consequence. Milestone: MS5 (Month 27).\n'
    'WP4, Monitoring network designed for the warnings (Months 1–36; NATO-country team). Steps: design (T4.1); procurement '
    'and installation (T4.2); operation and maintenance (T4.3); seismic velocity as a water-table gauge (T4.4). Risk: '
    'procurement delays and limited site access; mitigation: early orders, inductions with security officers. Milestones: '
    'MS1 (Month 6), MS2 (Month 12).\n'
    'WP5, Live demonstration (Months 22–36; NATO-country team). Steps: dry run (T5.1); twelve months of bulletins (T5.2); '
    'safe operating window and pumping rule (T5.3); post-event protocol (T5.4). Risk: no strong event occurs; mitigation: '
    'verification by back-testing and storylines. Milestones: MS6 (Month 34), MS7 (Month 36).\n'
    'WP6, Training, transfer and dissemination (Months 1–36; partner-country team): early-career researchers and a training '
    'school (T6.1), operator training (T6.2), open release (T6.3), transfer to a second coast (T6.4).\n'
    'WP7, Management, data and risk (Months 1–36; coordinator): management and reporting (T7.1), data plan and access '
    'agreements (T7.2), risk register (T7.3).')

AFTER = (
    'Implementation. The operators issue every bulletin themselves in Months 34–36, with at least two trained staff each, and '
    'sign a maintenance agreement (Month 33) that covers the running cost of about €10,900 per year for data, telemetry and '
    'spare sensors. Until it is in place, the Albanian university hosts the system. Operating procedures for each asset and '
    'a policy brief for the national authorities (D6.2) anchor the warnings in daily practice.\n'
    'Next steps: extend the warnings to the other wellfields and coastal assets of Albania; offer the open software to '
    'coasts of Allies and partners (tested on a second coast in the partner country during the project); seek national and '
    'European funding to keep the network and the verification ledger running.\n'
    'Role of the end-users. The water utility, the port authority, the energy landfall operator and the National Civil '
    'Protection Agency guide the project from the start: they give access to sites and records, agree the thresholds and '
    'tolerable miss rates (T3.1), take part in the dry run, co-sign the operational milestones, run the bulletins in live '
    'operation and own the system after the hand-over. End-users receive no SPS funds.')

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
    '• D4.1 network design approved by the steering committee and the operators (Month 6, MS1).\n'
    '• D4.2 network installed and streaming with at least 90% data availability; D1.1 coastal motion atlas with a vertical '
    'velocity uncertainty of about 1–2 mm/yr at asset points (Month 12, MS2).\n'
    '• D2.1 calibrated coupled model: held-out heads, chloride, InSAR and seismic velocity inside the 90% predictive '
    'intervals at close to the nominal rate (Month 18, MS3).\n'
    '• D2.2 certified surrogate: error bound met on test runs; alarm prototype passes a dry run (Month 22, MS4, go/no-go '
    'for live operation).\n'
    '• D3.2 back-testing: each alarm\'s miss rate at or below its target with a 95% confidence bound, under a protocol '
    'published with a DOI before the results (Month 27, MS5).\n'
    '• D5.1 twelve months of live bulletins with every outcome logged, the miss rates consistent with their certificates, and '
    'the certified safe operating window reported for each asset (Month 34, MS6).\n'
    '• D6.1 open software and data with a DOI, reproduced by someone outside the team (Month 33); D6.2 operating procedures '
    'adopted and policy brief delivered (Month 36, MS7).\n'
    '• Capacity: at least 20 trained operator and civil-protection staff, at least six early-career researchers, at least six '
    'open-access papers and eight conference presentations.\n'
    '• Management: progress reports at each SPS milestone, spending within 10% of the plan per budget category, and the risk '
    'register reviewed at every gate.')

CRITERIA = [
    ['Each alarm\'s miss rate in back-testing over the record since 2014 is at or below its certified target (indicatively 5–10%), with a 95% confidence bound (D3.2, Month 27)', 25],
    ['Twelve months of live bulletins (Months 23–34) with every outcome logged and no verification test rejecting a certified miss rate (D5.1)', 20],
    ['Held-out heads, chloride, InSAR and seismic velocity fall inside the model\'s 90% predictive intervals at a rate of at least 85% (D2.1, Month 18)', 15],
    ['The operators issue all bulletins in Months 34–36 with at least two trained staff each, and the maintenance agreement is signed (MS7)', 15],
    ['The monitoring network reaches at least 90% data availability over twelve months of operation (D4.2, T4.3)', 10],
    ['The certified safe operating window and its closing year are reported for each asset and confirmed by the full model at the closing point (T5.3)', 10],
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
            'Management': 'Co-financing of personnel'}[c]


def budget_tables():
    rows = BB.compute()
    by = defaultdict(lambda: [0.0] * 4)
    for r in rows:
        y1, y2, y3 = r['y']
        per = [y1 / 2, y1 / 2 + y2 / 2, y2 / 2 + y3 / 2, y3 / 2]   # periods ending at M1 (6), M2 (18), M3 (30), final (36)
        for i, v in enumerate(per):
            by[sps_cat(r)][i] += v
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
              '**Deadline:** 15 November 2026, 23:59 CET (call 2027-1; confirm on the platform). Multi-Year Projects are evaluated in two phases: fill what the platform asks for now; the rest is ready if you are invited to the full proposal.']:
        q = para(doc, 3, 0.3); put(q, '• ' + b)

    heading(doc, 'Checklist: uploads and signatures', 13, before=8)
    chk = [['SPS MYP Acceptance of Funds (NATO template)', 'PDF', 'NATO-country Project Director + a representative of the NPD\'s institution', '[to do]'],
           ['SPS MYP Agreement for Joint Research (NATO template)', 'PDF', 'All Co-Directors + a representative of each institution', '[to do]'],
           ['SPS MYP Detailed Budget workbook (NATO Excel template, tabs "Info" and "Detail")', 'Excel', 'Fill by hand: the form warns that using AI on this file may corrupt it and lead to automatic rejection', '[to do]'],
           ['Project schedule with a Gantt chart', 'PDF', 'Ready: CERTAIN-COAST_Project_Schedule.pdf', 'ready'],
           ['End-user commitments, all letters merged into one file', 'PDF', 'Each end-user on its own letterhead (drafts in the Letters of Commitment document)', '[to do]'],
           ['Brief overview of participating institutions (at most one page each)', 'PDF', 'Draft: CERTAIN-COAST_Institutions_Overview.docx; fill the yellow fields, save as PDF', '[to do]'],
           ['Financial rules of the NPD\'s institution', 'PDF or link', 'NPD\'s institution', '[to do]'],
           ['Intellectual Property Rights agreement or waiver', 'PDF', 'Can be submitted later, once the project is approved', 'later'],
           ['Illustrative figures (optional, one PDF with a table of contents)', 'PDF', '—', 'optional']]
    t = head_repeat(table(doc, ['Upload', 'Format', 'Who signs or prepares it', 'Status'], chk, [6.4, 1.6, 6.8, 2.2], size=9.2))
    ph_cells(t)
    q = para(doc, 3, before=4)
    put(q, '**Still missing before you can submit:** [a partner-country Project Director, employed and resident in an eligible '
           'partner country] (without one the application is not eligible); [confirmation of the Albanian institution of the '
           'NPD]; [signed letters from the four end-users].', size=10.5)

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
            ['SPS Acceptance of Funds (NPD only)', 'Upload the signed PDF: signature of the NPD and of a representative of the NPD\'s institution']]
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
            ['[First name]', '[Family name]', '[PPD institution]', 'Partner-country Project Director', '[nationality]', 'WP2 coupled model and certified surrogate; WP3 certified alarms; WP6 training and transfer', '[30%]'],
            ['[First name]', '[Family name]', '[Institute of Geosciences, UPT]', 'Researcher', '[Albanian]', 'Seismic, GNSS and hydrometeorological data; WP1, WP4', '[15%]'],
            ['To be recruited', '(4 people)', 'NPD and PPD institutions', 'Early-career researchers (stipends)', '[NATO or partner]', 'InSAR and GNSS; modelling; alarms; network and live operation (WP1–WP5)', '[50%]'],
            ['[First name]', '[Family name]', '[Durrës water utility]', 'End-user representative', '[Albanian]', 'Thresholds (T3.1), dry run, live bulletins, pumping rule', '[5%]'],
            ['[First name]', '[Family name]', '[Durrës Port Authority]', 'End-user representative', '[Albanian]', 'Thresholds (T3.1), dry run, live bulletins', '[5%]'],
            ['[First name]', '[Family name]', '[energy landfall operator]', 'End-user representative', '[nationality]', 'Thresholds (T3.1), dry run, live bulletins', '[5%]'],
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
    answer(doc, 'TRL 7 or higher')
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
    q = para(doc, 3, before=3); put(q, 'All 21 risks, with owners and triggers, are in the Risk Assessment document.', size=9, color=GREY, italic=True)
    field(doc, 'Communication Plan')
    answer(doc, COMMS)
    field(doc, 'Key Performance Indicators (KPIs)', '500 words.')
    answer(doc, KPIS, 500)
    field(doc, 'Criteria for success', 'At most seven, SMART, weights summing to 100%.')
    head_repeat(table(doc, ['Criterion', 'Relative weight (%)'], [[c, str(w)] for c, w in CRITERIA], [14.0, 3.0], size=9.3))
    field(doc, 'List of abbreviations')
    answer(doc, ABBREV)
    field(doc, 'Optional upload: a file that helps to illustrate the project')
    answer(doc, 'Optional. One PDF with a table of contents and three figures: the method chain, the security chain of the '
                'assets, and the certified safe operating window ([ask for it if you want it prepared]).')

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
    answer(doc, listing('Co-financing of personnel') + '\n[Confirm with the current MYP Handbook: the Budget document lists this '
                                                        'amount as a management allowance for the NPD; in this form it fits under '
                                                        'co-financing of personnel, with the remaining personnel cost paid by the '
                                                        'institution.]')
    field(doc, 'Other major expenses (optional)')
    answer(doc, listing('Other') + '\nCommunication and Publications (€18,000) and Consumables (€22,700) are detailed in the '
                                   'budget workbook and the Communication Plan above.')
    field(doc, 'Budget summary by item: non-NATO funding contribution (in EUR)', 'Estimate what the institutions and nations contribute.')
    nn = [[c, '[€ amount]'] for c in ['Equipment', 'Training', 'Communication & Publication', 'Travel', 'Consumables', 'Stipends', 'Co-financing', 'Other']]
    t = head_repeat(table(doc, ['Budget category', 'Amount from other funding sources'], nn, [9.0, 8.0], size=9.3)); ph_cells(t)
    field(doc, 'Non-NATO funding')
    answer(doc, 'Salaries of all researchers and project directors, paid by their institutions [€ estimate]; the operators\' '
                'access to wells, port and landfall, their records and staff time for workshops and training [€ estimate]; free '
                'data (Copernicus Sentinel-1 radar images) and existing data under agreements (ASIG tide gauge, national seismic stations); offices, laboratories '
                'and existing field equipment of the partner institutions [€ estimate].')
    field(doc, 'How do you want to share the financial rules of the NPD\'s institution?')
    answer(doc, '[File upload or link to the website of the NPD\'s institution.]')

    # 9 End-users
    heading(doc, '9. End-Users', 14, before=10)
    p = para(doc, 4); put(p, 'At least one end-user; all based in a NATO or eligible partner country; end-users receive no SPS funds.')
    eu = [[f'[First name]', '[Family name]', '[Title]', '[Job title]', inst, '[Postal address]', '[Country]', '[Telephone]', '[E-mail]']
          for inst in ['[Durrës water utility]', '[Durrës Port Authority]', '[energy landfall operator]', '[National Civil Protection Agency]']]
    t = head_repeat(table(doc, ['First name', 'Family name', 'Title', 'Job title', 'Institution', 'Postal address', 'Country', 'Telephone', 'E-mail'],
                          eu, [1.7, 1.7, 1.2, 1.8, 2.6, 2.2, 1.6, 1.9, 2.3], size=8.2)); ph_cells(t)
    field(doc, 'End-User(s) commitments (upload)')
    answer(doc, 'One PDF with all signed letters, each on the end-user\'s letterhead (drafts in the Letters of Commitment document; '
                'the end-users sign their own letters). For governmental end-users, a letter of support from the ministry or agency.')

    # 10 Attachments
    heading(doc, '10. Project attachments', 14, before=10)
    for nm, a in [('Brief overview of participating institutions (upload)', 'One PDF, at most one page per institution: capabilities, resources, facilities, websites. Use CERTAIN-COAST_Institutions_Overview.docx: [fill the yellow fields, delete the pages of institutions that do not take part], then save it as PDF.'),
                  ('SPS MYP Agreement for Joint Research (upload)', 'NATO template, signed by all Co-Directors and a representative of each institution.'),
                  ('Do you want to include the Intellectual Property Rights (IPR) Agreement (or Waiver) now?', 'No. It can be submitted after approval; the software is released under an open licence.'),
                  ('Additional files (optional)', 'Not needed.'),
                  ('Additional information (optional)', 'The full technical annex (methodology with its preparatory tests, state of the art, work packages, risk assessment, data management plan) is available on request.')]:
        field(doc, nm); answer(doc, a)

    doc.save(out)
    print('saved', out, '| total', total, '| words:', {k: words(t) for k, (t, _) in LIMITS.items()}, '| title chars', len(TITLE))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_NATO_Application_Form_Text.docx')
