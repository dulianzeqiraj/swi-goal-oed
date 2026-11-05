# PRIRJA-GO: guarantees for a stated number of years ahead

Code and results of the fifth state-of-the-art review, *State of the art V: when the world drifts*. It covers twenty
more papers from Oxford, Caltech, Berkeley and MIT (2020–2026), on forecasting through change, calibration over time, a
drifting water cycle and a moving coast, and presents the PRIRJA-GO innovation (November 2026, English). It is the
companion of reviews I–IV (`../garancia_go`, `../matja_go`, `../reshja_go`, `../ankora_go`).

**The question.** Review IV calibrated guarantees on real *anchors*: past years in which a boundary function was
measured. Past years are exchangeable with a future year only if nothing drifts. What if the vadose delay grows as the
water table falls, evaporative demand rises and the sea rises?

**The idea.** Horizon-matched calibration. Score every past year as the future year will be used: `h` years after a
window of `L` anchor years, whose centre and spread re-centre and re-scale the band.

**Results.**

- **Proposition P1.** Weighted calibration on past years has risk at most `α + Σ w̃_t ε_t`. With a drift that grows with
  the lag, no weights that give a finite band do better than the last nine years, whose bound `α + 0.9 δ (h + 4)` still
  grows with the horizon.
- **Proposition P2.** If the level of the errors is polynomial of degree ≤ `p` and their spread exponential in time, the
  location–scale matched scores are identically distributed in every year (degree ≤ `p + 1` for a constant spread and
  location-only scores).
- **Proposition P3.** With `K` anchor years and a window `L`, a band exists only `h ≤ K − L − 8` years ahead and a 90%
  certificate only `h ≤ K − L − 21` (α = 0.10). With `K = 30`: 17 and 4 years for the level window `L = 5`.

## Tests (`res/prirja.json`)

30 anchor years (one per year, drawn from 20 candidates), 150 field cases per target year, horizons 1–20 years, 300
draws.

| Test | What it shows |
|---|---|
| T15 | Under linear, accelerating or abrupt drift the simulation-calibrated band breaks (recharge 0.30–0.34, κ 0.35–0.65), and so does calibration on all 30 past years (κ 0.20–0.59). The last nine years are valid for the weekly goals only by being extreme, and fail for κ (up to 0.45). |
| T16 | The level-matched band (L = 5) keeps the risk at 0.003–0.082 for every goal and horizon under no, linear and abrupt drift, and ≤ 0.10 up to 10 years under accelerating drift; it fails for κ at 15 years (0.17). Location-only matching fails after the abrupt shift (recharge 0.19). |
| T17 | Without drift the matched band is 1–14% wider than all-years calibration up to 10 years for the weekly goals, and 0.50–0.70 of the last-nine-years width; κ costs 1.6–2.4 times. No band beyond 17 (level) or 12 (trend) years. |

## Files

- `prirja_exp.py`: drift histories, anchor years, exact weighted conformal risk control, horizon matching; T15–T17.
- `prirja_figs.py`: figures (scheme, drift, risk, width); the map figure comes from `../garancia_go/gar_figs.py`.
- `cards_prirja.py`: the twenty cards and the rows of the state-of-the-art table.
- `text_prirja.py`: the text.
- `build_prirja_doc.py`: the Word builder.
- `run_all.sh`: runs everything.
