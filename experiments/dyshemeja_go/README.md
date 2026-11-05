# DYSHEMEJA-GO: the floor of a guarantee

Code and results of the sixth state-of-the-art review, *State of the art VI: how narrow can a guarantee be*. It covers
twenty more papers from Oxford, Caltech, Berkeley and MIT (2020–2026) with theorem-level results on inverse problems,
the limits of uncertainty quantification, information and design, and presents the DYSHEMEJA-GO innovation (November
2026, English). It is the companion of reviews I–V (`../garancia_go`, `../matja_go`, `../reshja_go`, `../ankora_go`,
`../prirja_go`).

**The question.** Reviews I–V proved that their bands for the boundary conditions and the recharge coefficient are
valid. How narrow could a valid band be, with the same rain and the same few heads?

**The idea.** Under a working law the exact posterior of the test bed is a mixture over the recharge coefficient of
Gaussians. Among all bands with an expected share of weeks outside at most α, the narrowest on average is the
Neyman–Pearson band `{x : p(x | y) >= tau*}` with one threshold for all weeks: the *floor*.

**Results.**

- **Proposition F1.** No band procedure of any kind with risk at most α is narrower on average than the floor.
- **Proposition F2.** The excess width of a calibrated band `m ± λ s` splits exactly into calibration × reconstructor ×
  band shape; the last factor and the product of the last two are at least 1.
- **Proposition F3.** Adding observations never raises the floor; with rain alone the sea-level and inflow floors are
  their prior widths; the floor of a design is computable before field data exist.
- **Proposition F4.** Replacing truths by exact posterior draws keeps every expected risk and lowers its variance
  (Rao–Blackwell); all population multipliers use 40 draws per week.

## Tests (`res/dyshemeja.json`)

600 field cases per real law, 300 simulated aquifers, 300 anchor draws; designs with 300 cases.

| Test | What it shows |
|---|---|
| T18 | Without shift, the central posterior interval is 1.00–1.04 times the floor; the ensemble of reviews I–V costs 1.13–1.39 and 20 anchors a further 1.10–1.17, so its 20-anchor band is 1.34–1.54 times the floor. The exact posterior with 20 anchors is 1.07–1.20 times. |
| T19 | Under a 35-day field delay the 20-anchor ensemble band is valid but 1.66–5.83 times the floor; the exact posterior under the simulator's law repairs inflow and sea level but not recharge and κ; an enlarged law with the delay unknown gives 1.18–1.34 times the floor and valid simulation calibration. Under shifted parameters the exact posterior with anchors is 1.17–1.26. Every calibrated band below the floor was invalid. |
| T20 | Four loggers remove 82–94% of the rain-only floor width; the floor never rises when data are added, while the guaranteed band widened in 7 of 24 nested comparisons (one logger at 2 km widens the sea-level band). |

## Files

- `dyshemeja_exp.py`: exact posteriors (also with the delay unknown), floor, Rao–Blackwellised risks, bands; T18–T20.
- `dyshemeja_figs.py`: figures (scheme, ladder, shift, design); the map figure comes from `../garancia_go/gar_figs.py`.
- `cards_dyshemeja.py`: the twenty cards and the rows of the state-of-the-art table.
- `text_dyshemeja.py`: the text.
- `build_dyshemeja_doc.py`: the Word builder.
- `run_all.sh`: runs everything (about 40 minutes).
