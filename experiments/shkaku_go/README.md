# SHKAKU-GO: guaranteed counterfactuals

Code and results of the seventh state-of-the-art review, *State of the art VII: what would have happened*. It covers
twenty more papers from Oxford, Caltech, Berkeley and MIT (all 2022–2026) on stochastic causality, counterfactual
inference, causal generative models and counterfactual attribution in the Earth system, and presents the SHKAKU-GO
innovation (November 2026, English). It is the companion of reviews I–VI (`../garancia_go`, `../matja_go`,
`../reshja_go`, `../ankora_go`, `../prirja_go`, `../dyshemeja_go`).

**The question.** Reviews I–VI guarantee bands for what happened. What would the recharge and the head at an
unmonitored well have been, in the same 64 weeks, had the rain been 40% lower or a month later, given the rain and a
few loggers? This is a counterfactual (rung 3) in the stochastic structural causal model of the test bed.

**The model.** Exogenous: the rain, the latent histories (sea level, inland inflow, recharge error, initial head), the
recharge coefficient κ and the vadose delay τ. A twin world shares the histories, κ and τ; its recharge error is
`e' = ρ e + sqrt(1 - ρ²) ξ` (ρ = 1 is Pearl's shared noise). Goals: the effects Δr, Δh and the counterfactual levels
r′, h′ at the pumping well (1.5 km).

**Results.**

- **Proposition K1.** With shared noise the effect is `κ·a_w`. It is free of the sea level, the inflow, the recharge
  error and the initial head. A band for κ alone therefore becomes a simultaneous guaranteed band for the whole effect
  path.
- **Proposition K2.** With rain alone the counterfactual law equals the interventional law. The value of abduction of a
  design is the ratio of the two floors, and it is at least 1.
- **Proposition K3.** No data identify the cross-world coupling ρ. The effect's variance falls as ρ grows. The union of
  the bands calibrated over a grid of ρ is valid for every ρ on the grid.
- **Proposition K4.** Anchor twins are the factual truth plus the effect computed with the simulator's mechanism. They
  make counterfactual bands checkable when the mechanism is right. When the mechanism is wrong, no number of anchors
  removes the error.

## Tests (`res/shkaku.json`, `res/shkaku_sign.json`)

There are 600 field cases per real law and 300 simulated twins, with 20 anchor twins drawn 300 times. The design
tests use 300 cases. All runs use four loggers except the design test (T22).

| Test | What it shows |
|---|---|
| T21 | **Drought, no shift.** All bands are valid within sampling error: 300 twins give 0.96–1.06 times the floor, 20 anchor twins 1.06–1.18 (risk 0.056–0.094). A 40% drought lowers the head at the well by 1.94 m; the floor half-width of that effect is 0.088 m. |
| T21 | **Drought, 35-day delay.** Twins fail (risk 0.77–0.91), and so do anchor twins for the effects (0.142–0.493). The enlarged law is valid (0.083–0.097) at 1.06–1.68 times the floor. |
| T21 | **Drought, shifted parameters.** Anchor twins are valid (0.058–0.097); twins and the enlarged law are not. |
| T22 | Four loggers narrow the counterfactual floors 7.7–15.7-fold against rain alone; both effects gain the same 8.6-fold, through κ only. |
| T23 | **Unshared recharge error (ρ = 0).** Floors widen 2.7–13.5-fold, and the shared-noise band fails (risk 0.64–0.92). The robust union stays valid in every case (at most 0.084), and costs 3.1–14 times the width when the noise is in fact shared. |
| T23 | **Monotonicity under ρ = 0.** The drought raises recharge in 12% of the weeks and the head in 0.008%. |
| T24 | **Late season (rain 30 days later).** The effect changes sign within the year. Under the 35-day delay, twins and anchor twins fail, while the enlarged law is valid (0.100–0.107) at 1.38–3.28 times the floor. |

## Files

- `shkaku_exp.py`: the twin network, the exact counterfactual laws (also with the delay unknown, 49 delays), floors, bands and T21–T24.
- `shkaku_sign.py`: side checks on the twins (sign of the drought effect under each coupling, mean effects, late-season sign changes).
- `shkaku_figs.py`: the scheme, T21, T22 and T23 figures; the map figure comes from `../garancia_go/gar_figs.py`.
- `cards_shkaku.py`: the twenty cards and the rows of the state-of-the-art table.
- `text_shkaku.py`: the text; every number is filled in from the result files.
- `build_shkaku_doc.py`: the Word document (OMML equations through `../ml_paradigms/word/omml.py`).
- `run_all.sh`: runs everything (about 50 min).
