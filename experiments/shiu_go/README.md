# SHIU-GO: rain, recharge and the stochastic conditions of the coastal-aquifer equations, discovered from irregular and incomplete observations

Numerical checks of the note *Shiu, rimbushja dhe kushtet stokastike në ekuacionet e akuiferit bregdetar* (November 2026,
Albanian, `docs/research_notes/SHIU-GO_Forcimi_Stokastik_Ekuacionet_Filtrimit_Transportit.docx`). The note builds one
system of equations for the coastal aquifer from three materials:

- Krach, Nübel & Teichmann (2026, *Stochastic Processes and their Applications*), path-dependent neural jump ODEs.
  Observations come at random times with random masks. The optimal forecast is the conditional expectation given what
  was observed, and it is learned by minimising a masked prediction loss.
- The author's review on causal discovery by optimization: invariance across environments (EILLS) and exact MIQP selection.
- The author's review on assimilating missing dynamics: N1, a learned closure with memory in the flow equation; N2, a
  switch between the EnKF and a transport-map filter; N3, a robust band.

*Shiu* is Albanian for rain.

**Two routes for the forcing.**
- **Route A** treats the forcing as a stochastic system of its own. Rain is a marked Poisson process. Soil water follows
  a jump SDE: a bucket with evapotranspiration and threshold drainage. The delay through the unsaturated zone is an
  Erlang-2 memory (two linear reservoirs). The recharge error is a multiplicative Ornstein–Uhlenbeck process (1 + e).
- **Route B** adds a term to the flow equation instead. The term is built from a library of rain and evapotranspiration
  features plus an OU residual, and its terms are chosen by invariance across wet, normal and dry years.

Both routes are fitted by minimising the PD-NJ-ODE prediction loss on heads observed on random days with random masks.
The note also gives new forms of three equations:
- the flow equation: N1 plus stochastic recharge, storm-overwash jumps, and a closure with memory;
- the transport equation: immobile-zone memory, a recharge source c_R, overwash salt jumps, and a sea boundary that
  switches with the flow direction;
- the filter: a PD-NJ-ODE with physics between observations and a Kalman or transport-map jump at each observation.

**Test bed.**
- *Aquifer:* the linear coastal aquifer of ASIMILIMI-GO. It is 5 km long in 25 cells, with the sea as a Dirichlet
  boundary at x = 0, T = 1000 m²/d, Sy = 0.1, a well at 1.5 km, and piezometers at 250, 1250, 2750 and 4250 m.
- *Forcing:* 13 years of daily rain from a seasonal marked Poisson law, with yearly multipliers for wet, normal and dry
  years. Test year 10 is a drought with 40% of normal rain.
- *True law:* s̄ = 200 mm, s_w = 120 mm, s_fc = 130 mm, k_L = 25 mm/d, b_L = 3, τ = 20 d, σ_e = 0.25, τ_e = 90 d.
- *Observations:* heads on random days (p = 0.15), each piezometer with p = 0.6, noise sd 2 cm.
- *Split:* years 4–9 for training, years 10–13 for testing, repeated over 12 twins.

With the true law the Kalman filter gives the exact optimal forecast (Proposition 4 of the note), so each model's
distance from the optimum is measured exactly.

## Results (`shiu_exp.py` → `res/shiu_exp.json`, `res/shiu_exp_log.txt`; medians over 12 twins)
- **E1, prediction loss above the optimum (test years).**

  | Model | Loss above optimum | RMS distance from optimal forecast (Proposition 1) |
  |---|---|---|
  | Route A | 9% (IQR 5–15%) | 1.1 cm |
  | M1, linear rain transfer | 80% | 4.3 cm |
  | M0, Gaussian OU forcing of the assimilation note | 262% | 7.6 cm |

- **E3, long gaps.** More than 14 days after the last head reading, the squared error is 8.9 times the optimum for M0
  (171 against 19 cm²), 3.2 times for M1 and 1.4 times for Route A.
- **Calibration.** 90% intervals cover 89% of the observations with the true law and 88% with Route A. M1 covers 93% and
  M0 95%; M0 inflates its noise to explain forcing it does not know, so its intervals are safe but wide.
- **Monthly recharge.** Correlation of the filtered monthly recharge with the truth: 0.997 (true law), 0.996 (Route A),
  0.991 (M1), 0.975 (M0).
- **What heads identify** (median, IQR, true value in brackets).
  - Identified: τ = 19.6 d, 18.9–20.2 (20); σ_e = 0.23, 0.20–0.30 (0.25); s_fc = 133 mm, 120–145 (130).
  - Not identified: k_L = 15.9 mm/d, 13.2–17.2 (25) and b_L = 2.0, 1.0–3.4 (3) offset each other, and
    τ_e = 72 d, 49–127 (90) stays wide.
- **Rain law** fitted to the gauge by maximum likelihood: c0 −1.670 (−1.667), c1 0.795 (0.8), d0 2.562 (2.526),
  d1 0.309 (0.3).
- **E2, Route B.** Loss above the optimum: 92% with all nine features, 89% with BIC selection and 97% with invariance
  (γ = 4 and 16). A linear library cannot reproduce the drainage threshold.
  - Invariance drops the terms that are not causes. The seasonal cos term is chosen in 67% of twins with BIC, 42% with
    γ = 4 and 25% with γ = 16. The sin term falls from 42% to 17% and the constant from 58% to 42%.
  - The nonlinear excess-rain feature is chosen in 92% of twins.
  - In the drought year, a climate not seen in training, the loss with γ = 16 is 8% lower than with BIC.
- **Identifiability (Proposition 3).**
  - A multiplicative recharge error and a uniform closure move the heads in almost the same way. The cosine between
    the two responses is 0.993 without the filter and 0.991 through it, which inflates the variance about 75 times.
  - A closure confined to the first km from the sea is easier to separate: cosine 0.918, inflation 6.4 times.
- **Drought carry-over.** In the drought year rain is 42% of normal but recharge is 75% of normal. In the first twin,
  34% of that year's recharge (median over twins 33%) is drainage from the year before, still crossing the unsaturated
  zone.

## Route A alone (`shiu_km.py` → `res/shiu_km.json`, `res/shiu_km_log.txt`)
Soil moisture is simulated hourly for ten years and observed in three designs:
- **Hourly probe** (25% of readings missing, noise sd 0.3 mm).
  - Rain law: jumps above 2 mm give the monthly rain intensity with a median relative error of 9% (8–65 jumps per
    month), and the summer mean depth within 16%. In winter the depth is underestimated, because a soil near saturation
    truncates the jumps.
  - Drift law: c_E 0.98 (1), s_fc 135 mm (130), k_L 24.7 mm/d (25), b_L 2.64 (3), with a drift mean absolute error of
    0.04–0.09 mm/d.
- **Kramers–Moyal moment ratios** (equation 16 of the note) are biased by the same truncation. In winter they give
  λ = 0.88 against 0.36 and ā = 7.4 against 15.9 mm; in summer λ = 0.15 against 0.10.
- **Satellite every 3–6 days.** Here λΔ ≈ 1, so the Kramers–Moyal estimate has no meaning: λ ranges from 0.001 to
  0.72 over the 7 months where it can be computed.
- **Satellite plus rain gauge.** The drift is learned from the forecast error between revisits, with a mean absolute
  error of 0.35–0.37 mm/d. The individual parameters are not identified: s_fc = 100 mm and b_L = 7.0 end up at the
  search bounds.

Monitoring rule: the rain gauge gives the jumps, an hourly probe gives the drift, satellite plus gauge gives the drift
function, and heads give the vadose delay and the error scale. The soil run is deterministic: a second run reproduces
`res/shiu_km.json` exactly.

## Files
- `shiu_model.py`: the forcing chain (rain, soil bucket, Erlang delay, OU error, sea level, pumping), the aquifer, the
  twin simulator and the Kalman filter (numba).
- `shiu_exp.py`: E1–E3 and identifiability over 12 twins (about 11 minutes with 4 worker processes).
- `shiu_km.py`: E4, the soil SDE from soil-moisture data (under 10 seconds).
- `shiu_figs.py`: the five figures.
- `text_shiu.py`: the Albanian text. Its numbers are filled in from `res/`, and guards stop the build if a finding stated
  in the text no longer holds.
- `build_shiu_doc.py`: the Word document with OMML equations. It needs pandoc and uses
  `../ml_paradigms/word/omml.py` and `../spiranca_go/certain_coast/build_sota.py`.

Run everything with `bash run_all.sh`.
