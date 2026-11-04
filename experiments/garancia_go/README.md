# GARANCIA-GO: guaranteed bands for inputs, dispersion and boundary conditions known only through the rain

Code and results of the review *Inputs, dispersion and boundary conditions from rain alone*. The review covers twenty
papers from Oxford, Caltech, Berkeley and MIT (2020–2026), a synthesis for the case of few conditions, and the
GARANCIA-GO innovation (November 2026, English). It is built to
`docs/literature/Literature_review_Inputs_Dispersion_Boundary_Conditions_from_Rain_Oxford_Caltech_Berkeley_MIT_2020-2026.docx`.

**The problem.** Boundary conditions are never observed: nobody measures the sea level, the inland inflow, the
recharge or the initial head week by week. Ordinary conformal prediction (Tibshirani 2023; Angelopoulos et al.,
ICLR 2024) therefore has no calibration pairs.

**The idea.**
- GARANCIA-GO simulates the calibration pairs from the physical prior given the rain.
- It runs the same reconstructor on every simulated aquifer and on the field. Here the reconstructor is the ensemble
  smoother with the exact solver of `../rindertimi_go`.
- It calibrates two scores:
  - the share of weeks outside the band, by conformal risk control;
  - the largest standardised residual, by split conformal, for whole-function coverage.
- A conformal p-value of held-out heads checks the prior against the field.

## Results (`res/gar_exp.json`, `res/gar_rcps.json`, `res/gar_rainc.json`)

| Test | What it shows |
|---|---|
| T1, 500 aquifers, rain + 4 loggers | The raw ensemble misses 17–20% of the weeks (κ: 67%). Calibrated: 0.095–0.100 of weeks outside, whole-function coverage 0.90. Widths are 1.11–1.36× (pointwise) and 1.71–2.04× (whole function) the exact posterior. |
| T1A, rain only | Guarantees hold, bands wide. Four loggers narrow the guaranteed band ×1.6 (sea level), ×4.8–4.9 (recharge, inflow), ×6.2 (κ), ×11.4 (initial head). |
| T1R, one shared rain record | The guarantee holds for that record, in a dry window (946 mm) and a wet one (2249 mm). κ is identified about twice as well in the wet year. |
| T2, n = 10–200 simulations | The mean guarantees hold for every n. CRC is conservative for n ≤ 20; the 10th percentile of sup-norm coverage rises from 0.79 to 0.86. |
| T3, field ≠ prior | **Parameter shift:** alarm 0.19 (null 0.10), coverage 0.81–0.86. **Delay error (35 d vs 14 d):** alarm 0.67, every guarantee breaks (recharge coverage 0.02). **Delay put in the prior:** coverage back to 0.86–0.91. |
| T4, Fushë-Kuqe chloride | **Littoral head alone:** w stays at its prior (rank correlation 0.00, as Proposition 6 says). **Chloride facts:** w = 16–65 m. **All facts:** 12.8–47.8 m, or 13.9–54.9 m after the conformal correction. |
| T5, one calibration set | **Plain CRC:** risk ≤ 10% in only 68–99% of sets (κ: 56–60%). **RCPS with the Hoeffding–Bentkus bound:** 100% (κ: 93–97%), at 1.26–1.87× the exact width. |

## Files

**Tests**
- `gar_exp.py`: T1, T1A, T2, T3 and T4. It writes `res/gar_exp.json`, `res/gar_exp_log.txt` and the example case
  `res/gar_case.npz`, and takes about 5 minutes.
- `gar_rcps.py`: T5, risk-controlling prediction sets with the Hoeffding–Bentkus bound, and the smallest n for a
  Bonferroni band. It writes `res/gar_rcps.json`.
- `gar_rainc.py`: T1R, rain-conditional calibration. It writes `res/gar_rainc.json`.

**Review**
- `cards_gar.py`: the twenty paper cards (links, affiliation evidence, lessons, innovation step).
- `text_gar.py`: the text. Every number comes from `res/`.
- `gar_figs.py`: the seven figures; every text is at least 8.6 pt at the printed size.
- `build_gar_doc.py`: the Word document with OMML equations and clickable links. It needs pandoc and uses
  `../ml_paradigms/word/omml.py` and `../spiranca_go/certain_coast/build_sota.py`.

The tests use the test bed of `../rindertimi_go/rgo_model.py` and the chloride ensemble
`../../chloride_fk/results/calib_ensemble.npz`.

Run everything with `bash run_all.sh`.

**Verification.** Every card is partly verified. In this environment doi.org, arxiv.org, openreview.net and most
publisher hosts could not be opened, so each landing page was reached through search results that quote it.
