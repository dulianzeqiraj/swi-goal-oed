# RESHJA-GO: guaranteed boundary conditions when the rain itself is uncertain

Code and results of the third state-of-the-art review, *State of the art III: when the rain itself is uncertain*. It
covers twenty more papers from Oxford, Caltech, Berkeley and MIT (2020–2026), on rainfall products, recharge, mixing
and coastal boundaries, and presents the RESHJA-GO innovation (November 2026, English). It is the companion of reviews
I (`../garancia_go`) and II (`../matja_go`). It is built to
`docs/literature/Literature_review_State_of_the_Art_III_Rain_Uncertainty_Inputs_Dispersion_Boundary_Conditions_RESHJA-GO_Oxford_Caltech_Berkeley_MIT_2020-2026.docx`.

**The question.** "Knowing only the amount of rain" usually means knowing a product: a reanalysis, a gridded or
satellite product, or a distant station. The product has a bias over the record and daily errors. What happens to
the guarantees of review I then, and what should be done?

**Results.**

- **Proposition R1.** A rain bias `b` is invisible to every check made with heads: the data depend on `κ` and `b`
  only through `c = κb`.
  - `κ` has a floor that no number of loggers removes: `Var(log κ | y) ≥ s_κ² s_b² / (s_κ² + s_b²)`.
- **Proposition R2.** The vadose filter passes the bias untouched. It averages daily errors of relative variance `v`
  down to `v / n_eff`, where `n_eff = (Σ K P)² / Σ K² P²` is the effective number of rain days in its memory.
  - This is about 57 days for steady rain, but 5.7 on average for the rain law of the test bed.
  - The covariance of the filtered error, `(v/(1+v)) K diag(P_obs²) Kᵀ`, can be computed from the product alone. It
    serves as the "R2 prior" for the recharge error.
- **Proposition R3.** The guarantees hold again when the simulated aquifers carry the product's errors.

## Tests (`res/reshja.json`)

400 simulated aquifers per setting. Scores are averages over 300 random 200/200 calibration/test draws.

| Test | What it shows |
|---|---|
| T9, coverage | **Calibrated as if the product were exact:** with loggers, the κ band misses in 0.70–0.76 of the cases. Whole-function coverage falls to 0.02–0.21 for the recharge, 0.49–0.82 for the inflow and 0.72–0.76 for the sea level. **With the product's errors in the simulated aquifers, or a local gauge:** risk 0.093–0.103, coverage 0.90. |
| T10, floor and gauge | **κ with the product:** 0.146 → 0.108 with 8 loggers. The floor is 0.091; with exact rain it is 0.023. `c = κb` shrinks to 0.028. **Recharge with 8 loggers:** 0.104 mm/d with the product, 0.069 with the R2 prior, 0.044 with a gauge, 0.041 with exact rain. **Gauge:** with one logger it gives κ 0.045, better than the product with 8 loggers. |
| T11, filter law | Over 300 records, the measured relative variance matches `v/n_eff`. The mean `n_eff` is 5.7, against 57 for steady rain. |

## Files

- `reshja_exp.py`: rain product, settings exact / naive / aware / aware+R2 / gauge, and tests T9–T11.
- `reshja_figs.py`: figures (scheme, cover, floor, filter); the map figure comes from `../garancia_go/gar_figs.py`.
- `cards_reshja.py`: the twenty cards and the rows of the state-of-the-art table.
- `text_reshja.py`: the text.
- `build_reshja_doc.py`: the Word builder.
- `run_all.sh`: runs everything.

Every card is partly verified. Landing pages were reached through search results only.
