# ANKORA-GO: guarantees that do not depend on the simulator

Code and results of the fourth state-of-the-art review, *State of the art IV: when the simulator is wrong*. It covers
twenty more papers from Oxford, Caltech, Berkeley and MIT (2020–2026), on transferring knowledge between sites,
inference under shift, mixing and coastal boundaries, and presents the ANKORA-GO innovation (November 2026, English).
It is the companion of reviews I–III (`../garancia_go`, `../matja_go`, `../reshja_go`).

**The question.** Every guarantee of reviews I–III is calibrated on simulated aquifers and holds only if the
simulator's prior is the real law. What happens when it is not?

**The idea.** Calibrate on a few *anchors* instead: sites or periods where a boundary function was measured. The
simulations keep their other roles, building the reconstructor and the score and choosing instruments.

**Results.**

- **Proposition A1.** The anchor-calibrated band satisfies `E_Q[L] ≤ α` for any real law `Q`, and `≥ α − 2/(m+1)` for
  continuous scores.
- **Proposition A2.** Any method needs at least `(1−α)/α` anchors, 9 at α = 0.10, for an average guarantee. A
  certificate at confidence `1−δ` needs `log δ / log(1−α)` anchors, 22 at α = δ = 0.10.
- **Proposition A3.** Mixing simulations with weight share `ψ` costs at most `ψ · TV(ρ_P, ρ_Q)`.

## Tests (`res/ankora.json`)

600 field cases per real law. Scores are averages over 300 draws of the anchors.

| Test | What it shows |
|---|---|
| T12 | **Calibrated on simulations:** the risk holds without shift (0.088–0.115). It breaks under a 35-d vadose delay, shifted parameters or a rain bias (0.11–0.83). **Calibrated on 10, 20 or 40 anchors:** the risk is ≤ 0.10 under every law. |
| T13 | **Without shift:** 20 anchors widen the band by about 15%, 40 anchors by about 6%. **Under shift:** the band widens by as much as the real errors demand. **Week-by-week score reshaping on simulations:** no gain. |
| T14 | **Mixing at ψ = 0.5:** safe without shift, but under shift the risk is 0.08–0.19, above 0.10 in 9 of the 12 cases. The safe rule is anchors alone. |

## Files

- `ankora_exp.py`: real laws, simulations, anchors, exact weighted conformal risk control, and tests T12–T14.
- `ankora_figs.py`: figures (scheme, risk, width, mix); the map figure comes from `../garancia_go/gar_figs.py`.
- `cards_ankora.py`: the twenty cards and the rows of the state-of-the-art table.
- `text_ankora.py`: the text.
- `build_ankora_doc.py`: the Word builder.
- `run_all.sh`: runs everything.

Every card is partly verified. Landing pages were reached through search results only.
