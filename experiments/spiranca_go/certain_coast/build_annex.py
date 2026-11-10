"""CERTAIN-COAST (NATO SPS proposal): short technical annex for the "Additional files (optional)" upload of the
application form. It supplements the fields "How will the project reach the planned end state?" and "Work-plan":
how the methods work, what was tested before the project and what is new, for the two sites (Durrës wellfields and
port; the TAP landfall near Fier), with the Ministry of Defence of Albania as the end-user. Work packages, tasks, months and milestones are those of the application form
(build_application.py); equations are those of the Methodology (build_methodology.py); every number comes from the
preparatory tests reported in the Methodology and Innovation documents; references are those already checked there.

usage: python build_annex.py OUT.docx"""
import json
import os
import re
import sys
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, '..', '..', 'ml_paradigms', 'word'))
from build_sota import run, para, heading, table  # noqa: E402
from build_methodology import Eqs, mrich, display_eq, COL  # noqa: E402
import omml  # noqa: E402

TITLE = 'Certified early warning to protect water, port and energy infrastructure on a sinking Adriatic coast'
SIZE = 10

# ------------------------------------------------------------------------------------------------- content
# kinds: h (section), h2 (subsection), p (paragraph with $math$ and **bold**), eq (numbered display equation),
# img, cap (caption), table (header, rows, widths, size), refs
BL = [
    ('h', '1. Two sites, three coupled hazards'),
    ('p', 'The project protects two sites on the Albanian Adriatic coastal plain: at Durrës, the wellfields that supply '
          'drinking water and the port; near Fier, the landfall of the Trans Adriatic Pipeline (TAP). The demonstration runs '
          'on the project\'s monitoring network on the coast of Durrës and Fushë-Kuqe, with the Ministry of Defence of Albania '
          'as the end-user, which uses the warnings to protect critical infrastructure; the '
          'port and the landfall are assessed from satellite radar, GNSS and public data only. Both sites stand on low '
          'ground near active faults, and at Durrës the land is sinking; the earthquake of 26 November 2019 caused '
          'liquefaction near the coast (Mavroulis, Lekkas and Carydis, 2021). Three hazards threaten these assets, and they '
          'are coupled through two variables, the relative sea level and the water table. Sea level enters the aquifer at its '
          'seaward boundary and sets how far seawater advances; the water table sets the effective stress in the sands and '
          'so their resistance to liquefaction; subsidence raises the relative sea level at every asset. Pumping lowers the '
          'water table: it increases seawater intrusion and, below the preconsolidation head, permanent subsidence, but it '
          'raises the factor of safety against liquefaction. No hazard can be managed alone, so one indicator is defined per '
          'hazard, oriented so that larger means more dangerous (Table 1).'),
    ('cap', 'Table 1. Hazard indicators, thresholds and lead times.'),
    ('table', ['Hazard (assets)', 'Indicator', 'Threshold', 'Lead time, cadence'],
     [['Seawater intrusion (Durrës wellfields)', 'I₁: chloride at the monitoring wells next to each wellfield',
       'From the drinking-water standard, agreed with the end-user (for example 250 mg/L)', 'Weeks to months; weekly'],
      ['Liquefaction (Durrës port; TAP landfall)', 'I₂: liquefaction potential index under the design shaking at the '
       'current water table', 'Class boundary of the design codes, agreed with the end-user', 'Daily; recomputed at once after an earthquake'],
      ['Extreme water level (all assets)', 'I₃: total water level at each asset', 'Design or operational level of '
       'each asset', 'Hours to days for storms; return levels yearly']],
     [4.0, 5.4, 4.6, 3.4], 8.5),
    ('p', 'An alarm is missed when the indicator exceeds its threshold within the lead time and no alarm was issued; the '
          'long-run miss rate is the quantity the project certifies. Earthquakes are not forecast: the liquefaction alarm '
          'states how the ground would respond if the design earthquake struck now, a state that changes with the water table. '
          'In a preparatory test at a synthetic port, the chance that the liquefaction potential index exceeded 5 if the '
          'design earthquake struck on a given day moved between 0.16 in late July and 0.26 in early February.'),

    ('h', '2. The method chain'),
    ('p', 'Six steps turn data into bulletins (Figure 1). Each step has a pass test and a fallback (Section 7). Three loops '
          'close the chain: verified outcomes update the alarm margins, new data are assimilated into the model, and the '
          'certified safe window of Section 6 tells the network how many years of safe operation each sensor adds.'),
    ('img', 'chain', 12.6),
    ('cap', 'Figure 1. The CERTAIN-COAST method chain for the Durrës wellfields and port and the TAP landfall near Fier. '
            'Solid arrows: from data to bulletins. Dashed arrows: the three feedback loops.'),

    ('h', '3. Observe and measure (WP1, WP4)'),
    ('h2', '3.1 Relative sea level at each asset (WP1, T1.1–T1.4)'),
    ('p', 'Sentinel-1 ascending and descending time series since 2014 give the vertical and east components of land '
          'motion; a trajectory model separates trend, season, the coseismic step of 26 November 2019 and the postseismic '
          'transient. Corner reflectors and GNSS at the assets (T1.2) give stable radar targets on soft ground and tie the '
          'solution to a global frame. The tide gauge records sea level $\\eta_{TG}$ relative to its own benchmark, which also '
          'moves, so the relative sea level at asset $a$ adds the differential vertical land motion $u_z$, propagated with its '
          'full covariance (target vertical-velocity uncertainty 1–2 mm/yr; Ohenhen et al., 2023):'),
    ('eq', 'rsl', 'R_a(t) = \\eta_{TG}(t) + u^{TG}_{z}(t) - u^{a}_{z}(t)'),
    ('p', 'Elastic and inelastic compaction fitted to the InSAR and head records give the head limit $h_{pc}$ above which '
          'pumping causes no new permanent subsidence (Lees, Knight and Smith, 2022). The same $R_a(t)$ drives all three '
          'hazard models, so the warnings cannot disagree about where the sea is.'),
    ('h2', '3.2 A network designed for the warnings, which corrects its own sensors (WP4, T4.1–T4.4)'),
    ('p', 'The network is designed before it is bought (D4.1, Month 6). Candidates are piezometers with conductivity '
          'loggers, a local rain gauge, GNSS, corner reflectors, seismic nodes and, where access allows, fibre-optic sensing; '
          'the candidate sites are boreholes on public land and existing wells whose owners agree. Each candidate is valued by goal-oriented '
          'Bayesian design (Attia, Alexanderian and Saibaba, 2018) in two currencies: the guaranteed width it removes from '
          'the warning bands, and the years of certified safe operation it adds (Eq. (mult)). A sensor is bought only if its '
          'guaranteed value is positive: in a preparatory test, a tide gauge that a standard ensemble rated as narrowing the '
          'recharge band by 15% widened the guaranteed band by 16–21%.'),
    ('p', 'Loggers respond to air pressure (Rasmussen and Crawford, 1997) and drift. A barometer and a sealed reference '
          'channel on each logger hub are therefore design candidates beside the piezometers; their errors are removed by '
          'marginalisation, and the network is chosen against the worst plausible error model, with a certified distance '
          'from the best network (robust design; Chowdhary, Attia and Alexanderian, 2025). In a preparatory test with 12 '
          'sensors the worst-case information was 5.59 nats against 3.67 for the classical design (+52%), with a certified '
          'optimality gap of 18%; 90% forecast intervals covered 88–93% of outcomes after correction and 49–62% without, and '
          'corrected heads were within 2.9 cm root-mean-square against 7.6 cm raw.'),
    ('p', "Near the port and the TAP landfall, T4.2 places corner reflectors, a GNSS station and a seismic station on "
          "public land. Ambient seismic noise tracks the water table (Clements and Denolle, 2018), also "
          "on unused telecommunication fibre (Rodríguez Tribaldos and Ajo-Franklin, 2021); once calibrated against "
          "piezometers (T4.4), velocity changes measure the water table between wells, also near the port and the landfall, and a "
          "drop after an earthquake measures the softening of the ground."),

    ('h', '4. Model and certify (WP2)'),
    ('h2', '4.1 One coupled model (T2.1–T2.3)'),
    ('p', 'One model, set up for the two sites on one coastal motion field (T2.1), couples variable-density flow, salt '
          'transport with memory in clays, the sea as a moving boundary driven by $R_a(t)$, compaction, the total water '
          'level at each asset, and liquefaction triggering with the water table taken from the flow model at every time '
          'step (Seed and Idriss, 1971; Boulanger and Idriss, 2014). Groundwater rise under sea-level rise is a hazard in its '
          'own right (Befus et al., 2020) and raises liquefaction severity where water tables are shallow (Grant et al., '
          '2021); here one water table drives all three hazards, so a pumping decision is checked against all of them at '
          'once. Parameters are estimated jointly from heads, conductivity, chloride, InSAR and seismic velocity by an '
          'ensemble smoother (Emerick and Reynolds, 2013); the model is differentiable, so adjoint gradients of every '
          'indicator are available (Shen et al., 2023). Priors are stated so that an expert can read and dispute them '
          '(Simpson et al., 2017; Fuglstad et al., 2019) and are checked after calibration for prior-data conflict (Evans '
          'and Moshonov, 2006).'),
    ('h2', '4.2 Guarantees for the inputs and boundaries nobody measures (T2.3)'),
    ('p', 'Recharge, vadose delay, storage, the sea-level and inland boundaries, the initial head and the dispersion width '
          'are never measured, yet every warning depends on them. They are reconstructed from rain and heads by a '
          'function-space diffusion prior with an ensemble update through the exact solver, with the errors of the rain '
          'product simulated in the prior. Their bands are calibrated by conformal risk control (Angelopoulos, Bates, '
          'Fisch, Lei and Schuster, 2024) on simulated aquifers that carry these errors, and checked on measured anchor '
          'periods, so the guarantee does not depend on the simulator. With a loss $L_i(\\lambda)$ between 0 and 1 for '
          'calibration case $i$ and its mean $\\hat{R}_n(\\lambda)$ over $n$ cases:'),
    ('eq', 'crc', '\\hat{\\lambda} = \\text{inf}\\left\\{\\lambda :\\; \\frac{n}{n+1}\\hat{R}_n(\\lambda) + \\frac{1}{n+1} \\le '
                  '\\alpha\\right\\}, \\qquad \\text{E}\\left[L_{n+1}(\\hat{\\lambda})\\right] \\le \\alpha'),
    ('p', 'For $\\alpha$ = 10%, at least 9 anchor periods give the average guarantee and 22 a 90% certificate. Under drift '
          'the calibration is matched to the forecast horizon, and a computable floor shows how far each band is from the '
          'narrowest valid one. In the preparatory test the raw ensemble missed 17–20% of the weeks and the calibrated bands '
          '9.5–10% (target 10%); the risk stayed at 0.003–0.082 up to 20 years ahead under drift.'),
    ('h2', '4.3 The boundary where the model is cut (T2.3, T4.1)'),
    ('p', 'Every model of the aquifer ends somewhere inland, at a cut that geology does not mark. A fixed head, a '
          'prescribed inflow or a general-head boundary does not respond to pumping or to the sea as the aquifer beyond '
          'does, and the choice decides the answers. In the preparatory test, the fresh water lost to a 0.5 m rise of the '
          'sea over 20 years was 49 m³ per metre of coast with a prescribed inflow, 462 with a fixed head and 154 in the '
          'full aquifer (Werner and Simmons, 2009). For any linear aquifer beyond the cut, heterogeneous, leaky or '
          'closed, the exact boundary is a conductance plus positive storage compartments. With $u = h - \\bar{h}$ the '
          'head at the cut above its reference and $q_{in}$ the inflow from rain, the outward flux is'),
    ('eq', 'pertej', 'q_n = -q_{in}(t) + C\\,u + \\sum_{m=1}^{M} w_m \\left(u - y_m\\right), \\qquad \\dot{y}_m = '
                     '\\mu_m \\left(u - y_m\\right), \\qquad C,\\ w_m \\ge 0'),
    ('p', 'Conversely, every such network is the exact boundary of some physical aquifer, so a learned boundary cannot '
          'be unphysical; the same positive memory describes diffusion into the silt and clay lenses inside the model '
          '(Haggerty and Gorelick, 1995). With $C, w_m \\ge 0$ the boundary is passive: the model loses energy whatever '
          'its other parameters, as passive models of an external electrical network do (Gustavsen and Semlyen, 2001). '
          'A negative conductance that was stable in a 2 km test grew without bound in a 6 km model. The rates $\\mu_m$ '
          'sit on a fixed logarithmic grid, three to four per decade of period. The weights are learned from two '
          'piezometers between the wellfields and the cut (T4.1), which separate the boundary from everything else in '
          'the model, on the band of periods that changes of pumping excite. A neural network may supply $q_{in}$ from '
          'rain and monotone conductances, never the storages, and a prior learned from simulated geology fills the '
          'periods the data do not reach. In the test, six compartments reproduced the full aquifer to 7.8 mm '
          'root-mean-square over 20 years (best general-head boundary: 148 mm). Learned from the two piezometers while '
          'the pumping varied, the boundary predicted an unseen drought with doubled pumping to 6 mm (372 mm), and the '
          'fresh water lost to the sea-level rise within 4%. The proofs and the six checks are in the PËRTEJ-GO theory '
          'note, the third document of these files.'),
    ('h2', '4.4 The earthquake in the aquifer (T2.2, T4.4, T5.4)'),
    ('p', 'An earthquake changes the pore pressure at once, so the liquefaction indicator uses the pore pressure of that '
          'moment: below the water table of the day, $u = \\gamma_w (z - z_w)_+ + f\\,\\Delta p_0$, where $f$ is the share '
          'of the step left at the end of the shaking (close to zero in sand within a few metres of the water table, one '
          'in sand below clay). The static step follows from the published fault models of the 2019 earthquake (Ganas et '
          'al., 2020; Govorčin et al., 2020; Matraku et al., 2023; van der Heiden et al., 2026) through the horizontal '
          'strain at the surface (Okada, 1985). A soft layer under the free surface takes that strain and adjusts '
          'vertically, so for an undrained layer with shear modulus $G$, Skempton coefficient $B$ and undrained Poisson '
          'ratio $\\nu_u$'),
    ('eq', 'kappa', '\\Delta p_0 = -\\kappa\\,\\left(\\Delta\\varepsilon_{xx} + \\Delta\\varepsilon_{yy}\\right), \\qquad '
                    '\\kappa = \\frac{2GB}{3}\\,\\frac{1+\\nu_u}{1-\\nu_u}'),
    ('p', 'A soft saturated sand ($\\nu_u$ near 1/2) deforms at almost constant volume, so its step scales with $G$, which '
          'the seismic nodes measure as shear-wave velocity (T4.4). With the four source models the step was 7–12 cm of '
          'head in soft surface sand ($G$ = 50 MPa) and 0.6–1.0 m in a stiffer confined aquifer ($G$ = 0.5 GPa); the usual '
          'estimate, $B K_u$ times the volumetric strain of the half-space, gave 35 times the soft-sand value. For '
          'liquefaction the water table of the day dominates: in an example profile the index fell from 20.2 to 9.3 as '
          'the water table deepened from 0.8 to 2.6 m. The cone-penetration resistance keeps the value it had when it was '
          'measured; re-normalising it with the stress of the day understated that slope by 33%. The step matters in the '
          'confined aquifer, and its '
          'relaxation is a free pumping test: 20 days of logger data after a 0.3 m step pinned the leakage time 5.8 times '
          'more sharply than a year of seasonal heads. The post-event protocol (T5.4) therefore reads the leakage of the '
          'confined aquifer from the loggers, and well records of November 2019 are sought where they exist. The mapped '
          'liquefaction of 2019 (Mavroulis, Lekkas and Carydis, 2021) cannot test the step: on a synthetic plain even 480 '
          'sites gave a power below 50%. The code and the checks are in the TRONDITJA-GO report, the fourth document of '
          'these files.'),
    ('h2', '4.5 A fast copy with a certified error (T2.4)'),
    ('p', 'Warnings need thousands of model runs a day. A neural operator (Li et al., 2021; Lu et al., 2021) is trained on '
          'runs of the coupled model, and its error on each forecast is bounded conformally (Ma et al., 2024), with the '
          'score normalised by the goal-oriented dual-weighted residual $\\eta_k$ (Becker and Rannacher, 2001), so the bound '
          'is tight where the copy is right about the quantity that triggers the alarm:'),
    ('eq', 'cert', '\\Delta_k(\\xi) = \\hat{q}_{1-\\delta}\\,\\eta_k(\\xi), \\qquad \\Pr\\left[\\,|I_k(\\xi) - '
                   '\\hat{I}_k(\\xi)| \\le \\Delta_k(\\xi)\\,\\right] \\ge 1 - \\delta'),
    ('p', 'Forecasts whose bound is too wide are recomputed with the full model on a reduced domain. A generative copy '
          '(Gao, Kaltenbach and Koumoutsakos, 2024) explores long storylines of sea-level rise, subsidence, droughts and '
          'pumping and chooses which of them the full model runs; in a preparatory test its statistics alone put the closing '
          'year of the safe window 2–8 years too late, so closing years are always certified from full runs with the exact '
          'binomial bound (Clopper and Pearson, 1934).'),

    ('h', '5. Certified alarms (WP3)'),
    ('h2', '5.1 Alarm rule, calibration under shift and beyond the record (T3.1–T3.2)'),
    ('p', 'Thresholds $\\tau_k$ and tolerable miss rates $\\alpha_k$ are agreed with the end-user (T3.1). Alarm $k$ fires when '
          'the forecast at lead time $L_k$ comes within a margin $m_k$ of its threshold. The margin adds the certified copy '
          'error to a forecast error $\\gamma_k$ that rises after a miss and falls slightly otherwise; with a constant step '
          '$\\lambda$ the long-run miss rate stays within $C_k/(\\lambda T)$ of its target for any sequence of data (Gibbs and '
          'Candès, 2021, 2024; Angelopoulos, Barber and Bates, 2024):'),
    ('eq', 'alarm', 'A_k(t) = \\mathbf{1}\\left\\{\\hat{I}_k(t + L_k) \\ge \\tau_k - m_k(t)\\right\\}, \\qquad m_k(t) = '
                    '\\Delta_k(t) + \\gamma_k(t)'),
    ('eq', 'aci', '\\gamma_k(t+1) = \\gamma_k(t) + \\lambda_t\\,[\\,miss_k(t) - \\alpha_k\\,], \\qquad '
                  '\\left|\\frac{1}{T}\\sum_{t=1}^{T} miss_k(t) - \\alpha_k\\right| \\le \\frac{C_k}{\\lambda\\,T}'),
    ('p', 'The guarantee also holds within each regime (drought, storm season, after an earthquake, each asset) by '
          'conformal prediction with conditional guarantees (Gibbs, Cherian and Candès, 2025), and for events rarer than '
          'the record by extreme conformal prediction (Pasche, Lam and Engelke, 2026). Still-water extremes use a '
          'generalised Pareto tail (Coles, 2001) whose threshold moves with the measured relative sea level of Eq. (rsl). In '
          'preparatory tests on a coupled variable-density model, an extreme-aware margin kept the share of seasons above '
          'the chloride limit at 4–9% across drought, human-feedback and compound storylines, where a static alarm allowed '
          '13–21%.'),
    ('h2', '5.2 One guarantee for the three assets (T3.3)'),
    ('p', 'The alarms share inputs, so their misses are dependent. The probability that any alarm is missed is bounded by '
          'the sum of the tolerances, which are allocated where tightening them costs least in consequence-weighted false '
          'alarms, within caps agreed with the users. The margins are calibrated together by Learn then Test '
          '(Angelopoulos, Bates, Candès, Jordan and Lei, 2025), so every certified rate holds at once with probability at '
          'least $1-\\beta$. The national authorities receive one joint guarantee for the wellfields, the port and the landfall.'),
    ('h2', '5.3 Warnings for what happens between samples (T3.2)'),
    ('p', 'Chloride is sampled weeks or months apart. Sparse samples pin the distribution of chloride on the sampling '
          'dates but not its time scale, so a well can turn salty between two samples that both look safe. The warning is '
          'therefore the probability that chloride crosses its limit $c^{*}$ at any time in the season $T$, reported as a '
          'band over the set $\\mathcal{M}$ of all models consistent with the records, in the spirit of robust bounds over '
          'calibrated models (Gierjatowicz et al., 2020) and of online forecasts from irregular records (Krach, Nübel and '
          'Teichmann, 2026):'),
    ('eq', 'band', '\\underline{p} = \\text{inf}_{P \\in \\mathcal{M}} P\\left[\\max_{t \\in T} c(t) > c^{*}\\right], \\qquad '
                   '\\overline{p} = \\text{sup}_{P \\in \\mathcal{M}} P\\left[\\max_{t \\in T} c(t) > c^{*}\\right]'),
    ('p', 'The band is widened by a conformal margin calibrated on simulated aquifers and anchor periods and issued online '
          'as the conditional probability given the irregular samples and the daily heads; the network design adds the '
          'observation that closes it (a logger, or samples paired 1, 3 and 7 days apart). In the preparatory test the '
          'chance of a crossing within the season was 0.78, against 0.023 on a sampling date (34 times); the band was '
          '0.18–1 with quarterly samples and 0.76–0.80 with a daily logger; for skewed chloride the margin restored 90.3% '
          'coverage (74% without), and a head logger raised the warning skill from 7% to 20%.'),
    ('h2', '5.4 Back-testing and verification in operation (T3.4–T3.5)'),
    ('p', 'The chain is replayed over the record since 2014 with the system frozen at each issue time, under a protocol '
          'published with a DOI before the results (D3.2, Month 27). At 95% confidence, verifying a 10% miss rate needs 29 '
          'exceedance events with no miss, 46 with one or 61 with two; a 5% rate needs 59, 93 or 124. In operation the '
          'ledger is published every quarter, so each miss rate is looked at many times, and a fixed-sample bound '
          'recomputed at every look loses its guarantee: in a simulation of six calibrated alarms it flagged at least one as '
          'broken in 68% of runs. Verification therefore uses e-processes, which stay valid however often they are checked '
          '(Ville, 1939; Vovk and Wang, 2021; Ramdas et al., 2023), with $x_i = 1$ if event $i$ was missed:'),
    ('eq', 'eproc', 'E_k(n) = \\sum_j \\pi_j \\prod_{i=1}^{n}\\left(\\frac{q_j}{\\alpha_k}\\right)^{x_i}\\left(\\frac{1-q_j}'
                    '{1-\\alpha_k}\\right)^{1-x_i}, \\qquad \\Pr\\left(E_k(n) \\ge 1/\\beta \\;\\text{ for some } n\\right) '
                    '\\le \\beta'),
    ('p', 'In the simulation the e-process flagged a calibrated alarm in 2.2% of runs (at most 5% is guaranteed) and '
          'detected an alarm whose miss rate had risen to 25% in 84% of runs within 100 events.'),

    ('h', '6. Operate and decide (WP5)'),
    ('p', 'Twelve months of live bulletins (T5.2) follow a dry run (T5.1). Each bulletin states, per asset, the forecast, '
          'the margin, the alarm state, the certified miss rate and the distance to the closing of the safe window, and is '
          'logged with its inputs and code version so that it can be reproduced and audited. A post-event protocol agreed '
          'with the end-user (T5.4) remeasures heads, chloride, GNSS and seismic velocity within days of a strong '
          'earthquake or storm, updates the model and recomputes the alarms and the window.'),
    ('h2', '6.1 The effect of pumping without the hidden drought demand (T5.3)'),
    ('p', 'In droughts the wellfields pump more while recharge falls, so a hidden cause drives both the pumping and the '
          'salinity, and substitutes for hidden confounders inferred from the treatment history (Bica, Alaa and van der '
          'Schaar, 2020) can miss it. CERTAIN-COAST measures the confounding path instead: the heads, after the drawdown '
          'estimated from the abstraction records is added back, read the recharge, and a calibrated physics check rejects any '
          'substitute that misses a confounder before an effect is reported. In the preparatory test the bias of the summed '
          'well effects was 0.59 unadjusted, 0.56 with a history substitute and 0.00 with the heads; the check had a size of '
          '6% and a power of 99–100%. On the calibrated chloride model of Fushë-Kuqe, 40% less recharge would grow the '
          'shallow area above 250 mg/L from 31 to 65 km² (effect +33 km², conformal band 15–49 km²).'),
    ('h2', '6.2 The certified safe operating window and the year it closes (T5.3)'),
    ('p', 'Pumping moves the hazards in opposite directions, and sea-level rise and subsidence tighten all of them. At each '
          'bulletin and over the adaptation horizon the project computes the set of decisions $u$ (wellfield pumping $Q_w$, '
          'port dewatering) that meets the demand $D$, keeps every hazard within its certified limit and causes no new '
          'permanent subsidence, and the relative sea level and year at which this set becomes empty:'),
    ('eq', 'window', 'W_{\\alpha}(R) = \\left\\{\\,u :\\; Q_w \\ge D,\\;\\; \\Pr_{\\theta}\\left[I_k(u, R; \\theta) > '
                     '\\tau_k\\right] \\le \\alpha_k \\;\\, (k = 1, 2, 3),\\;\\; h(\\mathbf{x}, u, R) \\ge '
                     'h_{pc}(\\mathbf{x})\\,\\right\\}'),
    ('eq', 'closing', 'R^{*}_{\\alpha} = \\text{largest } R \\text{ with } W_{\\alpha}(R) \\neq \\emptyset, \\qquad '
                      't^{*}_{\\alpha} = \\text{first } t \\text{ with } W_{\\alpha}(R(t)) = \\emptyset'),
    ('p', 'This is a certified, multi-hazard adaptation tipping point (Kwadijk et al., 2010; Haasnoot et al., 2013); '
          'tipping points exist for seawater intrusion alone (Mazi, Koussis and Destouni, 2013). At the closing point the '
          'least dewatering that keeps liquefaction within its limit, $A$, meets the most dewatering the wellfield tolerates, '
          '$B$, and one multiplier $\\mu$ converts any change of a margin, from a sensor, a better model or a pumping test, '
          'into years:'),
    ('eq', 'mult', '\\mu = -\\left[\\frac{d\\,(B - A)}{dt}\\right]^{-1}_{t = t^{*}_{\\alpha}}, \\qquad '
                   '\\Delta t^{*}_{\\alpha} \\approx \\mu\\,(\\Delta B - \\Delta A)'),
    ('p', 'On a synthetic transect with the three hazards of Durrës and illustrative values, the certified window closed at '
          'a relative sea level of 0.41 m, after 38 years; plans that watch one hazard believed they had 43 to 97 years, and '
          'the margins cost 84 years against the window without them. Valued in years by preposterior analysis, with Eq. '
          '(mult) as a first-order shortcut, a sentinel piezometer between the wellfield and the sea added 21.6 years, and a '
          'GNSS station and two corner reflectors 5.6 and 5.0 years, where the classical criterion values them at zero '
          'because they narrow none of today\'s forecasts. For one managed head the window between liquefaction and '
          'intrusion has a closed form, $\\eta + m_{int} \\le h \\le z_s - z^{*}(a)$, with $z^{*}(a)$ the water-table depth '
          'that keeps the index below 5 for 90% of the profiles under the design acceleration $a$ and $m_{int}$ the fresh '
          'head that keeps the interface 20 m deep. At a synthetic port it closed at 0.29 m of relative sea-level rise for '
          '0.20 g and was already closed at 0.22 g, so the design acceleration chosen for the port decides the '
          'closing year.'),
    ('h2', '6.3 Safe pumping tests chosen for the years they add (T5.3)'),
    ('p', 'Routine pumping keeps the water table in a narrow band, so the records say little about how chloride responds '
          'near the onset of intrusion, which decides when the window closes. Short pumping and dewatering tests, each '
          'approved by the operator of the wells and by the permitting authority, would approach that onset safely; within the project they are '
          'planned and checked on the model, and run only where the well operator agrees. The response is linear in unknown coefficients of hinge '
          'features of the head, with a confidence set that holds in every week (Abbasi-Yadkori, Pál and Szepesvári, 2011). '
          'A test is chosen for the years it adds to the certified closing year, as in active identification with '
          'guarantees (Mania, Jordan and Recht, 2022) but for the decision, and only if the upper confidence bound of '
          'chloride stays below a test limit in every week of the test and the recovery (Koller et al., 2018). In the '
          'preparatory test the campaign raised the certified closing year from 10.8 to 31.9 years (true value 45) with '
          'chloride below 123 mg/L in 95% of runs, whereas tests chosen for parameter accuracy alone passed 250 mg/L in 42% '
          'of runs; the certificate held in all 1,000 runs. The years rest on the prior from the calibrated model, so the '
          'certified year is reported for the prior error radius $S$ and for $2S$ (doubling it cost 17.3 of the 31.9 '
          'years), for readers who trust the model less (Andrews and Shapiro, 2021).'),
    ('h2', '6.4 Pumping rule and the value of the warning for each user (T5.3, D5.1)'),
    ('p', 'Within the window, the pumping and drought rule supplies as much water as possible; it is checked for a sudden '
          'pumping stop, after which the water table recovers and the factor of safety falls, computed with the fast copy, '
          'confirmed with the full model and prepared for the authorities that issue water-use permits. Because each miss rate is certified, the value '
          'of a warning to each user in the cost-loss model (Murphy, 1977; Richardson, 2000) has a guaranteed lower bound '
          'for every cost-loss ratio agreed in T3.1, reported in D5.1.'),

    ('h2', '6.5 Pumping before the source of the chloride is known (T4.1, T5.3)'),
    ('p', 'Rising chloride at a wellfield need not be seawater. Deep brine drawn up under the wells, a drought that '
          'concentrates the recharge, or irrigation return flow and wastewater fit the same chloride record, and each calls '
          'for a different change of pumping. On a synthetic test bed with three wellfields and an alternative supply, '
          'acting on the wrong source let the blend exceed 250 mg/L with probability up to 100%, and the usual assumption '
          'of seawater intrusion up to 98%. CERTAIN-COAST therefore decides before the source is known. Tracer data $y$ '
          '(Br/Cl ratios, water isotopes, depth profiles from multilevel wells, nitrate and boron; Davis, Whittemore and '
          'Fabryka-Martin, 1998) give each candidate source $k$ an e-value. The sources that the data cannot exclude form '
          'a set that contains the true source with probability at least $1-\\beta$, for any sample size and without a '
          'prior (Vovk and Wang, 2021):'),
    ('eq', 'evset', 'E_k(y) = \\frac{1}{K-1}\\sum_{j \\neq k}\\frac{p_j(y)}{p_k(y)}, \\qquad S(y) = \\{\\,k :\\; '
                    'E_k(y) < 1/\\beta\\,\\}, \\qquad \\Pr_k\\left[\\,k \\notin S(y)\\,\\right] \\le \\beta'),
    ('p', 'The set keeps every source whose posterior under a flat prior exceeds $\\beta/(K-1+\\beta)$, and it is never '
          'empty. Where the end-member signatures are uncertain, the denominator is replaced by its supremum over them '
          '(universal inference; Wasserman, Ramdas and Balakrishnan, 2020). The pumping of the wellfields and the use of '
          'the alternative supply are then chosen at least social cost, safe for every source left in the set:'),
    ('eq', 'srcalloc', '\\min_{u}\\; c(u) \\quad \\text{s.t.} \\quad \\Pr_k\\left[\\,\\text{Cl}_{\\text{blend}}(u) > '
                       '250\\ \\text{mg/L}\\,\\right] \\le \\alpha \\;\\text{ for every } k \\in S(y) \\quad '
                       '\\Rightarrow \\quad \\Pr\\left[\\,\\text{exceed}\\,\\right] \\le \\alpha + \\beta'),
    ('p', 'The bound holds whatever the true source is. The prior of experts and users is used only to choose which '
          'tracers to buy, by the cost of the decision they change (T4.1). Monthly samples multiply the e-values, so the set '
          'can be read at every steering meeting and acted on at any time without losing the guarantee (Ville, 1939). A '
          'ledger shows what not knowing the source costs the water supply, the farmers and the wetland. In the preparatory test '
          'the rule kept every source at or below 6.9% against a 10% budget, at €3.31 million. Pumping safe for all '
          'sources without tests cost €4.16 million, and €2.87 million if the source were known. Bayesian rules after the '
          'same tests reached 12.3% for the sources the prior did not favour. Monthly updates dropped the true source in '
          '1.2–1.5% of cases, against 22% for an ordinary test repeated every month. A truth that mixes seawater and '
          'upconing breaks a list of pure sources (16.8%); admitting mixtures as hypotheses restores safety at a higher '
          'cost.'),

    ('h', '7. Gates, pass tests and fallbacks'),
    ('cap', 'Table 2. What each step must achieve before the next starts, and what happens if it does not.'),
    ('table', ['Step and gate', 'Pass test', 'Fallback'],
     [['Network design (WP4; MS1, Month 6)', 'Approved by the steering committee; certified optimality '
       'gap of at most 25%', 'Design re-run with the remaining budget; seismic nodes if fibre is not available'],
      ['Network and coastal motion (WP4, WP1; MS2, Month 12)', 'At least 90% data availability; corrected heads within '
       '3 cm root-mean-square of manual dips; vertical-velocity uncertainty of about 1–2 mm/yr at asset points',
       'Corner reflectors and scatterers on structures where radar coherence is lost'],
      ['Coupled model and unmeasured inputs (WP2; MS3, Month 18)', 'Held-out heads, chloride, InSAR and seismic velocity '
       'inside the 90% predictive intervals at close to the nominal rate; band for crossings at most 0.25 wide for each '
       'wellfield; the learned inland boundary passive', 'Model built in stages; two-dimensional sections through each '
       'asset with a wider error bound; a wider simulation-calibrated band, reported as such, if anchors are too few; a '
       'general-head boundary with a widened band if the inland boundary is not identified'],
      ['Certified copy and alarm prototype (WP2, WP3; MS4, Month 22, go/no-go)', 'Error bound met on test runs; the '
       'prototype passes a dry run with the end-user', 'Full model on a reduced domain for flagged forecasts'],
      ['Back-testing (WP3; MS5, Month 27)', 'Each miss rate at or below its target with a 95% confidence bound, crossings '
       'between samples included, under the pre-registered protocol', 'Margin widened: the miss target is kept and the '
       'extra false alarms are reported'],
      ['Live operation (WP5; MS6, Month 34)', 'Twelve months of logged bulletins; no e-process reaches 1/β; safe window '
       'reported for each asset with a plan of safe pumping tests and the years it would add; the plausible chloride sources and the '
       'pumping in force published every month', 'If no strong event occurs, '
       'verification rests on back-testing and storylines; the window from routine records and the post-earthquake relaxation'],
      ['Hand-over (WP6, WP7; MS7, Month 36)', 'An operating procedure for the bulletins agreed with the Ministry of Defence; its '
       'trained staff use the bulletins in Months 34–36 with the project team only in support; at least four of its '
       'staff trained; agreement on keeping and maintaining the sensors '
       'signed by Month 33 (D6.2); open software and data with a DOI reproduced outside the team (D6.1, Month 33)',
       'Extra training and tasks reassigned within the consortium; procedures restated jointly with the end-user; the '
       'university hosts the system until the agreement on the sensors is in place']],
     [4.4, 7.0, 6.0], 8.5),

    ('h', '8. What is new beyond the state of the art'),
    ('p', 'The alarms assemble published methods of 2021–2026 (online and conditional conformal prediction, extreme '
          'conformal prediction, Learn then Test and anytime-valid verification); their joint use for coupled coastal '
          'hazards is an application and is not claimed as new. Nine contributions were derived and tested before the '
          'project (Table 3); the novelty statements rest on our literature search to date.'),
    ('cap', 'Table 3. The nine new contributions, the result of their preparatory test and where they are used.'),
    ('table', ['Contribution', 'What is new', 'Preparatory test', 'Where'],
     [['(i) Guarantees for quantities nobody measures', 'Bands for recharge, vadose delay, boundaries and dispersion that '
       'stay valid when the simulator or the rain product is wrong, with a computable floor', 'Raw ensemble missed 17–20% '
       'of weeks; calibrated bands 9.5–10% (target 10%)', 'T2.3; D2.1, MS3'],
      ['(ii) The value of a sensor', 'The guaranteed band a sensor removes and the years of safe operation it adds',
       'GNSS and corner reflectors: 5.6 and 5.0 years, where the classical criterion gives zero; a tide gauge rated '
       'useful widened the band by 16–21%', 'T4.1; D4.1, MS1'],
      ['(iii) Pumping effects free of hidden confounding', 'The confounding path measured by the heads, with a calibrated '
       'check of every substitute', 'Bias 0.00 with the heads, against 0.56–0.59; check size 6%, power 99–100%',
       'T5.3'],
      ['(iv) Certified safe window and safe pumping tests', 'One window for three hazards and the year it closes; tests '
       'chosen for the years they add, with a chloride safety filter', 'Window closes after 38 years where single-hazard '
       'plans assume 43–97; tests: 10.8 to 31.9 years, chloride below 123 mg/L in 95% of runs', 'T5.3; D5.1, MS6'],
      ['(v) A network that corrects its own sensors', 'Barometer and reference channels placed by design; robust choice '
       'with a certified optimality gap', '+52% worst-case information; gap 18%; interval coverage 88–93% against '
       '49–62%', 'T4.1–T4.3; D4.1'],
      ['(vi) Warnings for what happens between samples', 'A certified band for a crossing at any time in the season, and '
       'the observation that closes it', 'Crossing 0.78 against 0.023 on a sampling date (34 times); band 0.18–1, '
       'narrowed to 0.76–0.80 by a logger', 'T3.2; D2.1, D3.2'],
      ['(vii) Pumping before the source of the chloride is known', 'The sources that tracer e-values cannot exclude, '
       'kept without a prior; pumping safe for all of them; tracers bought for the decision they change; monthly '
       'updates valid at any time', 'Every source at or below 6.9% against a 10% budget (assuming seawater: up to 98%); '
       '€3.31 million against €4.16 million without tests; true source dropped in 1.2–1.5% of cases against 22%',
       'T4.1, T5.3; MS6'],
      ['(viii) A boundary that learns the aquifer beyond the model', 'A conductance plus positive storage compartments: '
       'exact for any linear aquifer beyond the cut, passive whatever the rest of the model, learned from two '
       'piezometers while the pumping varies', 'Six compartments 7.8 mm against 148 mm for the best general-head '
       'boundary; unseen drought with doubled pumping 6 mm against 372 mm; fresh water lost to sea-level rise within '
       '4% (prescribed inflow: 3.1 times too little)', 'T2.3, T4.1; D2.1, MS3'],
      ['(ix) Which aquifer feels an earthquake', 'The pore-pressure step of each layer from its own stiffness, in the '
       'liquefaction indicator with the pore pressure of the day; the step of the confined aquifer used as a free '
       'pumping test', 'Step 7–12 cm in soft sand and 0.6–1.0 m in a confined aquifer, where the usual estimate is 35 '
       'times the soft-sand value; leakage time 5.8 times sharper than from a year of seasons', 'T2.2, T4.4, T5.4; '
       'D2.1']],
     [3.6, 5.4, 5.6, 2.8], 8.5),
    ('p', 'Together they answer questions that no current coastal warning answers for its users: how often a warning '
          'will be missed and so what silence means; how many years of safe pumping and dewatering remain as the sea rises '
          'and the land sinks; which sensor or pumping test buys more of them; how the aquifer beyond the model answers '
          'new pumping and a rising sea; which layer an earthquake loads and what its relaxation reveals; and how to pump '
          'safely before anyone knows where the salt comes from. The system starts at TRL 3, each '
          'component shown in preparatory tests, and ends at TRL 6, demonstrated through twelve months of live operation on '
          'the project\'s monitoring network with the Ministry of Defence as end-user; at the port '
          'and the landfall the warnings run on satellite, GNSS and public data.'),
    ('p', '**Software and data.** The model, fast copies, alarms, safe window, test planner and network design are released '
          'under an open licence with containers and tests (D6.1). Data shared by the owners of wells and records are used under '
          'the access agreements of T7.2; derived products, the bulletin log and the verification ledger are '
          'released openly following FAIR principles, and the preparatory tests are scripted and released with the software.'),
    ('refs', None),
]

REFERENCES = [
    'Abbasi-Yadkori, Y., Pál, D., Szepesvári, C. (2011). Improved algorithms for linear stochastic bandits. Advances in Neural Information Processing Systems 24, 2312–2320.',
    'Andrews, I., Shapiro, J.M. (2021). A model of scientific communication. Econometrica 89(5), 2117–2142. https://doi.org/10.3982/ECTA18155',
    'Angelopoulos, A.N., Barber, R.F., Bates, S. (2024). Online conformal prediction with decaying step sizes. Proc. 41st International Conference on Machine Learning, PMLR 235, 1616–1630.',
    'Angelopoulos, A.N., Bates, S., Candès, E.J., Jordan, M.I., Lei, L. (2025). Learn then test: calibrating predictive algorithms to achieve risk control. Annals of Applied Statistics 19(2), 1641–1662. https://doi.org/10.1214/24-AOAS1998',
    'Angelopoulos, A.N., Bates, S., Fisch, A., Lei, L., Schuster, T. (2024). Conformal risk control. 12th International Conference on Learning Representations (ICLR 2024).',
    'Attia, A., Alexanderian, A., Saibaba, A.K. (2018). Goal-oriented optimal design of experiments for large-scale Bayesian linear inverse problems. Inverse Problems 34(9), 095009. https://doi.org/10.1088/1361-6420/aad210',
    'Becker, R., Rannacher, R. (2001). An optimal control approach to a posteriori error estimation in finite element methods. Acta Numerica 10, 1–102.',
    'Befus, K.M., Barnard, P.L., Hoover, D.J., Finzi Hart, J.A., Voss, C.I. (2020). Increasing threat of coastal groundwater hazards from sea-level rise in California. Nature Climate Change 10(10), 946–952. https://doi.org/10.1038/s41558-020-0874-1',
    'Bica, I., Alaa, A.M., van der Schaar, M. (2020). Time Series Deconfounder: estimating treatment effects over time in the presence of hidden confounders. Proc. 37th International Conference on Machine Learning, PMLR 119.',
    'Boulanger, R.W., Idriss, I.M. (2014). CPT and SPT based liquefaction triggering procedures. Report UCD/CGM-14/01, University of California, Davis.',
    'Chowdhary, A., Attia, A., Alexanderian, A. (2025). Robust optimal experimental design of infinite-dimensional Bayesian nonlinear inverse problems. arXiv:2409.09137.',
    'Clements, T., Denolle, M.A. (2018). Tracking groundwater levels using the ambient seismic field. Geophysical Research Letters 45(13), 6459–6465. https://doi.org/10.1029/2018GL077706',
    'Clopper, C.J., Pearson, E.S. (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. Biometrika 26(4), 404–413.',
    'Coles, S. (2001). An Introduction to Statistical Modeling of Extreme Values. Springer.',
    'Davis, S. N., Whittemore, D. O., Fabryka-Martin, J. (1998). Uses of chloride/bromide ratios in studies of potable water. Groundwater 36(2), 338–350. https://doi.org/10.1111/j.1745-6584.1998.tb01099.x',
    'Emerick, A.A., Reynolds, A.C. (2013). Ensemble smoother with multiple data assimilation. Computers & Geosciences 55, 3–15.',
    'Evans, M., Moshonov, H. (2006). Checking for prior-data conflict. Bayesian Analysis 1(4), 893–914. https://doi.org/10.1214/06-BA129',
    'Fuglstad, G.-A., Simpson, D., Lindgren, F., Rue, H. (2019). Constructing priors that penalize the complexity of Gaussian random fields. Journal of the American Statistical Association 114(525), 445–452. https://doi.org/10.1080/01621459.2017.1415907',
    'Gao, H., Kaltenbach, S., Koumoutsakos, P. (2024). Generative learning for forecasting the dynamics of high-dimensional complex systems. Nature Communications 15, 8904. https://doi.org/10.1038/s41467-024-53165-w',
    'Gibbs, I., Candès, E. (2021). Adaptive conformal inference under distribution shift. Advances in Neural Information Processing Systems 34.',
    'Gibbs, I., Candès, E.J. (2024). Conformal inference for online prediction with arbitrary distribution shifts. Journal of Machine Learning Research 25(162), 1–36.',
    'Ganas, A., Elias, P., Briole, P., et al. (2020). Ground deformation and seismic fault model of the M6.4 Durres (Albania) Nov. 26, 2019 earthquake, based on GNSS/InSAR observations. Geosciences 10(6), 210. https://doi.org/10.3390/geosciences10060210',
    'Gibbs, I., Cherian, J.J., Candès, E.J. (2025). Conformal prediction with conditional guarantees. Journal of the Royal Statistical Society Series B 87(4), 1100–1126. https://doi.org/10.1093/jrsssb/qkaf008',
    'Gierjatowicz, P., Sabate-Vidales, M., Šiška, D., Szpruch, L., Žurič, Ž. (2020). Robust pricing and hedging via neural SDEs. Working paper, SSRN 3646241.',
    'Grant, A.R.R., Wein, A., Befus, K.M., et al. (2021). Changes in liquefaction severity in the San Francisco Bay Area with sea-level rise. Geo-Extreme 2021, Geotechnical Special Publication 329, 308–317. https://doi.org/10.1061/9780784483695.030',
    'Govorčin, M., Wdowinski, S., Matoš, B., Funning, G.J. (2020). Geodetic source modeling of the 2019 Mw 6.3 Durrës, Albania, earthquake: partial rupture of a blind reverse fault. Geophysical Research Letters 47(22), e2020GL088990. https://doi.org/10.1029/2020GL088990',
    'Gustavsen, B., Semlyen, A. (2001). Enforcing passivity for admittance matrices approximated by rational functions. IEEE Transactions on Power Systems 16(1), 97–104. https://doi.org/10.1109/59.910786',
    'Haasnoot, M., Kwakkel, J.H., Walker, W.E., ter Maat, J. (2013). Dynamic adaptive policy pathways: a method for crafting robust decisions for a deeply uncertain world. Global Environmental Change 23(2), 485–498. https://doi.org/10.1016/j.gloenvcha.2012.12.006',
    'Haggerty, R., Gorelick, S. M. (1995). Multiple-rate mass transfer for modeling diffusion and surface reactions in media with pore-scale heterogeneity. Water Resources Research 31(10), 2383–2400. https://doi.org/10.1029/95WR10583',
    'Koller, T., Berkenkamp, F., Turchetta, M., Krause, A. (2018). Learning-based model predictive control for safe exploration. 2018 IEEE Conference on Decision and Control, 6059–6066. https://doi.org/10.1109/CDC.2018.8619572',
    'Krach, F., Nübel, M., Teichmann, J. (2026). Optimal estimation of generic dynamics by path-dependent neural jump ODEs. Stochastic Processes and their Applications. https://doi.org/10.1016/j.spa.2026.105058',
    'Kwadijk, J.C.J., Haasnoot, M., Mulder, J.P.M., et al. (2010). Using adaptation tipping points to prepare for climate change and sea level rise: a case study in the Netherlands. WIREs Climate Change 1(5), 729–740. https://doi.org/10.1002/wcc.64',
    'Lees, M., Knight, R., Smith, R. (2022). Development and application of a 1D compaction model to understand 65 years of subsidence in the San Joaquin Valley. Water Resources Research 58(6), e2021WR031390. https://doi.org/10.1029/2021WR031390',
    'Li, Z., Kovachki, N., Azizzadenesheli, K., Liu, B., Bhattacharya, K., Stuart, A., Anandkumar, A. (2021). Fourier neural operator for parametric partial differential equations. 9th International Conference on Learning Representations (ICLR 2021).',
    'Lu, L., Jin, P., Pang, G., Zhang, Z., Karniadakis, G.E. (2021). Learning nonlinear operators via DeepONet based on the universal approximation theorem of operators. Nature Machine Intelligence 3, 218–229. https://doi.org/10.1038/s42256-021-00302-5',
    'Ma, Z., Pitt, D., Azizzadenesheli, K., Anandkumar, A. (2024). Calibrated uncertainty quantification for operator learning via conformal prediction. Transactions on Machine Learning Research.',
    'Mania, H., Jordan, M.I., Recht, B. (2022). Active learning for nonlinear system identification with guarantees. Journal of Machine Learning Research 23, 1–30.',
    'Matraku, K., Jouanne, F., Dushi, E., et al. (2023). The 26 November 2019 Durrës earthquake, Albania: coseismic displacements and occurrence of slow slip events in the year following the earthquake. Geophysical Journal International 234(2), 807–838. https://doi.org/10.1093/gji/ggad101',
    'Mavroulis, S., Lekkas, E., Carydis, P. (2021). Liquefaction phenomena induced by the 26 November 2019, Mw = 6.4 Durrës (Albania) earthquake and liquefaction susceptibility assessment in the affected area. Geosciences 11(5), 215. https://doi.org/10.3390/geosciences11050215',
    'Mazi, K., Koussis, A.D., Destouni, G. (2013). Tipping points for seawater intrusion in coastal aquifers under rising sea level. Environmental Research Letters 8(1), 014001. https://doi.org/10.1088/1748-9326/8/1/014001',
    'Murphy, A.H. (1977). The value of climatological, categorical and probabilistic forecasts in the cost-loss ratio situation. Monthly Weather Review 105(7), 803.',
    'Ohenhen, L.O., Shirzaei, M., Ojha, C., Kirwan, M.L. (2023). Hidden vulnerability of US Atlantic coast to sea-level rise due to vertical land motion. Nature Communications 14, 2038. https://doi.org/10.1038/s41467-023-37853-7',
    'Okada, Y. (1985). Surface deformation due to shear and tensile faults in a half-space. Bulletin of the Seismological Society of America 75(4), 1135–1154. https://doi.org/10.1785/BSSA0750041135',
    'Pasche, O.C., Lam, H., Engelke, S. (2026). Extreme conformal prediction: reliable intervals for high-impact events. Extremes 29(2), 129–155. https://doi.org/10.1007/s10687-026-00536-9',
    'Ramdas, A., Grünwald, P., Vovk, V., Shafer, G. (2023). Game-theoretic statistics and safe anytime-valid inference. Statistical Science 38(4), 576–601. https://doi.org/10.1214/23-STS894',
    'Rasmussen, T.C., Crawford, L.A. (1997). Identifying and removing barometric pressure effects in confined and unconfined aquifers. Ground Water 35(3), 502–511. https://doi.org/10.1111/j.1745-6584.1997.tb00111.x',
    'Richardson, D.S. (2000). Skill and relative economic value of the ECMWF Ensemble Prediction System. Quarterly Journal of the Royal Meteorological Society 126, 649–667.',
    'Rodríguez Tribaldos, V., Ajo-Franklin, J.B. (2021). Aquifer monitoring using ambient seismic noise recorded with distributed acoustic sensing (DAS) deployed on dark fiber. Journal of Geophysical Research: Solid Earth 126, e2020JB021004. https://doi.org/10.1029/2020JB021004',
    'Seed, H.B., Idriss, I.M. (1971). Simplified procedure for evaluating soil liquefaction potential. Journal of the Soil Mechanics and Foundations Division, ASCE 97(SM9), 1249–1273.',
    'Shen, C., Appling, A.P., Gentine, P., et al. (2023). Differentiable modelling to unify machine learning and physical models for geosciences. Nature Reviews Earth & Environment 4(8), 552–567. https://doi.org/10.1038/s43017-023-00450-9',
    'Simpson, D., Rue, H., Riebler, A., Martins, T.G., Sørbye, S.H. (2017). Penalising model component complexity: a principled, practical approach to constructing priors. Statistical Science 32(1), 1–28. https://doi.org/10.1214/16-STS576',
    'van der Heiden, V., Schurr, B., Woollam, J., et al. (2026). Analysis of the 2019 Mw 6.4 Durrës, Albania, aftershock sequence: basement involved thrusting at the eastern Adriatic plate margin. Geophysical Journal International 246(2), ggag155. https://doi.org/10.1093/gji/ggag155',
    'Ville, J. (1939). Étude critique de la notion de collectif. Gauthier-Villars, Paris.',
    'Vovk, V., Wang, R. (2021). E-values: calibration, combination and applications. Annals of Statistics 49(3), 1736–1754. https://doi.org/10.1214/20-AOS2020',
    'Wang, C.-Y., Chia, Y. (2008). Mechanism of water level changes during earthquakes: near field versus intermediate field. Geophysical Research Letters 35(12). https://doi.org/10.1029/2008GL034227',
    'Wasserman, L., Ramdas, A., Balakrishnan, S. (2020). Universal inference. Proceedings of the National Academy of Sciences 117(29), 16880–16890. https://doi.org/10.1073/pnas.1922664117',
    'Werner, A. D., Simmons, C. T. (2009). Impact of sea-level rise on sea water intrusion in coastal aquifers. Ground Water 47(2), 197–204. https://doi.org/10.1111/j.1745-6584.2008.00535.x',
]


# ------------------------------------------------------------------------------------------------- figure
def fig_chain(path):
    W, H = 6.7, 4.12
    fig = plt.figure(figsize=(W, H), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')
    stages = [
        ('Observe', 'WP4 · T4.1–T4.4', COL['WP4'],
         'Piezometers with conductivity loggers, rain\ngauge, GNSS, reflectors, seismic nodes;\nbarometer and reference channels',
         'Robust network,\ncertified gap'),
        ('Measure', 'WP1 · T1.1–T1.4', COL['WP1'],
         'InSAR since 2014 and GNSS: land motion\nand relative sea level at each asset;\ncompaction and the head limit',
         '$R_a(t)$, $h_{pc}$'),
        ('Model', 'WP2 · T2.1–T2.3', COL['WP2'],
         'Flow, salt, compaction, liquefaction on\none water table; unmeasured inputs\nfrom rain, with guaranteed bands',
         '$I_1$ chloride\n$I_2$ liquefaction\n$I_3$ water level'),
        ('Fast copy', 'WP2 · T2.4', COL['WP2'],
         'Neural operator with a certified error;\ngenerative copy for storylines;\nclosing years from full runs',
         '$\\hat{I}_k \\pm \\Delta_k$\nin seconds'),
        ('Certify', 'WP3 · T3.1–T3.5', COL['WP3'],
         'Online and regime-wise conformal; beyond\nthe record; one joint guarantee;\ncrossings between samples',
         'Alarm $A_k$,\nmiss rate $\\leq \\alpha_k$'),
        ('Operate', 'WP5 · T5.1–T5.4', COL['WP5'],
         'Bulletins; pumping effects without hidden\ndemand; safe window and closing year;\nsafe tests; anytime-valid verification',
         'Verified rates;\nyears of safe\noperation'),
    ]
    xT0, xT1, xM0, xM1, xO0, xO1 = 0.42, 1.98, 2.06, 4.88, 4.96, 6.12
    bh, gap, top = 0.56, 0.11, H - 0.08
    ys = []
    for i, (name, wp, col, meth, out) in enumerate(stages):
        y1 = top - i * (bh + gap); y0 = y1 - bh; ym = (y0 + y1) / 2; ys.append((y0, y1, ym))
        ax.add_patch(FancyBboxPatch((xT0, y0), xT1 - xT0, bh, boxstyle='round,pad=0,rounding_size=0.08', fc=col, ec='none'))
        ax.text(xT0 + 0.13, ym + 0.13, f'{i + 1}', fontsize=15, fontweight='bold', color='white', va='center', ha='center')
        ax.text(xT0 + 0.32, ym + 0.13, name, fontsize=11.5, fontweight='bold', color='white', va='center', ha='left')
        ax.text(xT0 + 0.32, ym - 0.17, wp, fontsize=9, color='white', va='center', ha='left')
        ax.add_patch(FancyBboxPatch((xM0, y0), xM1 - xM0, bh, boxstyle='round,pad=0,rounding_size=0.08', fc='white', ec=col, lw=1.6))
        ax.text(xM0 + 0.09, ym, meth, fontsize=8.6, color='#1f2328', va='center', ha='left', linespacing=1.25)
        ax.add_patch(FancyBboxPatch((xO0, y0), xO1 - xO0, bh, boxstyle='round,pad=0,rounding_size=0.08', fc=col + '22', ec=col, lw=1.0))
        ax.text((xO0 + xO1) / 2, ym, out, fontsize=9.2, fontweight='bold', color='#1f2328', va='center', ha='center', linespacing=1.2)
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


# ------------------------------------------------------------------------------------------------- Word helpers
def field_run(p, instr, size):
    """A PAGE or NUMPAGES field in the footer."""
    r = p.add_run(); r.font.size = Pt(size)
    for kind, text in (('begin', None), (None, instr), ('separate', None), (None, '1'), ('end', None)):
        if kind:
            e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), kind); r._r.append(e)
        elif text == instr:
            e = OxmlElement('w:instrText'); e.set(qn('xml:space'), 'preserve'); e.text = f' {instr} '; r._r.append(e)
        else:
            e = OxmlElement('w:t'); e.text = text; r._r.append(e)


def footer(section):
    p = section.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'CERTAIN-COAST · NATO SPS 2027-1 · Technical annex · page ', size=8, color='6B7785')
    field_run(p, 'PAGE', 8)
    run(p, ' of ', size=8, color='6B7785')
    field_run(p, 'NUMPAGES', 8)


def two_columns(section):
    cols = section._sectPr.find(qn('w:cols'))
    if cols is None:
        cols = OxmlElement('w:cols'); section._sectPr.append(cols)
    cols.set(qn('w:num'), '2'); cols.set(qn('w:space'), str(int(0.6 * 567)))


def numref(text, numbers):
    return re.sub(r'Eq\. \((\w+)\)', lambda m: f'Eq. ({numbers.get(m.group(1), m.group(1))})', text)


# ------------------------------------------------------------------------------------------------- build
def main(out):
    numbers, n = {}, 0
    for b in BL:
        if b[0] == 'eq':
            n += 1; numbers[b[1]] = str(n)
    E = Eqs()
    work = tempfile.mkdtemp()
    figs = {'chain': os.path.join(work, 'fig_chain.png')}
    fig_chain(figs['chain'])

    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(1.9); s.top_margin = Cm(1.5); s.bottom_margin = Cm(1.5)
    s.footer_distance = Cm(0.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(SIZE)
    footer(s)

    p = para(doc, 1); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'CERTAIN-COAST — Technical annex', bold=True, size=16, color='1F3864')
    p = para(doc, 3); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, TITLE, bold=True, size=11, color='1F3864')
    p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'How the methods work, what was tested before the project, and what is new. This annex supplements the fields '
           '"How will the project reach the planned end state?" and "Work-plan" of the application form; work packages (WP), '
           'tasks (T), deliverables (D), months and milestones (MS) are those of the form. Test results come from synthetic '
           'test systems and preparatory models, not from measurements made by the project at the sites.',
        italic=True, size=8.8, color='52606D')

    for bi, b in enumerate(BL):
        kind = b[0]
        nxt = BL[bi + 1][0] if bi + 1 < len(BL) else None
        if kind == 'h':
            heading(doc, b[1], 12, before=8)
        elif kind == 'h2':
            heading(doc, b[1], 10.5, color='2E6DB4', before=4)
        elif kind == 'p':
            p = para(doc, 3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            mrich(p, numref(b[1], numbers), E, size=SIZE)
            if nxt == 'eq':
                p.paragraph_format.keep_with_next = True
        elif kind == 'eq':
            display_eq(doc, E, b[2], numbers[b[1]])
        elif kind == 'img':
            p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(figs[b[1]], width=Cm(b[2]))
        elif kind == 'cap':
            p = para(doc, 3); p.paragraph_format.keep_with_next = b[1].startswith('Table')
            run(p, b[1], italic=True, size=8.8, color='52606D')
        elif kind == 'table':
            t = table(doc, b[1], b[2], b[3], size=b[4])
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            for row in t.rows:
                row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            para(doc, 3)
        elif kind == 'refs':
            heading(doc, 'References', 11, before=6)
            sec = doc.add_section(WD_SECTION.CONTINUOUS)
            two_columns(sec)
            for r_ in REFERENCES:
                p = para(doc, 1.5); p.paragraph_format.left_indent = Cm(0.35)
                p.paragraph_format.first_line_indent = Cm(-0.35)
                run(p, r_, size=7.4, color='3D4752')

    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh, ensure_ascii=False)
    omml.main(draft, eq_json, out)
    words = sum(len(re.sub(r'\$[^$]*\$', 'x', b[1]).split()) for b in BL if b[0] == 'p')
    print('saved', out, '|', n, 'numbered equations,', len(E.items) - n, 'inline |', words, 'words of text |',
          len(REFERENCES), 'references')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Technical_Annex.docx')
