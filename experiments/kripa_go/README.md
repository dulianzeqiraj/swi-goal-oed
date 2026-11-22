# KRIPA-GO: what the salt would have done

Code and results of the eighth state-of-the-art review, *State of the art VIII: what the salt would have done*. It
covers twenty more papers from Oxford, Caltech, Berkeley and MIT (all 2022–2026) on dispersion and mixing,
counterfactuals in nonlinear systems, calibrated simulation-based inference and coastal aquifers under climate
scenarios. It presents the KRIPA-GO innovation (November 2026, English) and ends with a three-page summary of novelty.
It is the companion of reviews I–VII (`../garancia_go` … `../shkaku_go`).

**The question.** What would the salinized area, the toe of the wedge and the seawater fraction of the wells of
Fushë-Kuqe have been under a drier or a wetter recharge regime, given the documented facts? And how does the
dispersion coefficient enter that answer?

**The model.** It is the areal chloride model of `../../chloride_fk` with its 20 000-draw calibration ensemble:
- a steady Strack potential;
- a sharp interface with a dispersive transition zone of width `w`;
- screen-averaged chloride.

The twin aquifer has recharge `c·R`.

**Results.**

- **Proposition L1 (state abduction).**
  - The potential is linear in `R`, so `φ' = c φ`.
  - The twin interface and chloride follow from the factual state, or from the factual heads alone, without the conductivity or the recharge.
- **Proposition L2.**
  - For `c < 1` the chloride of every screen rises: the salt response is monotone.
  - The toe counterfactual is free of `w`.
  - The salinity counterfactual depends on `w`, which the heads do not inform.
- **Proposition L3.** The cross-world law of the dispersion width (`w'` versus `w`) is not identified by any factual data.
- **Proposition L4.** Conformal calibration on simulated data sets gives model-based guaranteed counterfactual bands.

## Tests (`res/kripa.json`, `res/kripa_maps.npz`)

| Test | What it shows |
|---|---|
| T25 | `φ(cR) = c φ(R)` to 1.1·10⁻¹⁵. The twin interface computed from the heads alone matches a re-solve to 1.5·10⁻¹¹ m. Shallow chloride never falls under `c < 1` (all draws, all cells). |
| T26 | Fushë-Kuqe with the facts, 40% less recharge. **Shallow area above 250 mg/L:** 31 → 65 km², an effect of +33 km² (conformal band 15–49). **Toe:** +33 km² (27–40). **Mid-depth seawater fraction, SW band:** +24 points (15–37). **Without the facts**, the effect band is 1.4–59 km². **Dose-response:** half the recharge adds 48 km² of salinized area; 50% more recharge removes 15 km². |
| T27 | On 300 simulated test sets, conformal coverage is 0.887–0.900 and importance-sampling coverage 0.883–0.923. |
| T28 | **Which facts narrow the area effect:** the heads do not (width ratio 1.04); the chloride facts do (0.60). **Share of the posterior variance carried by `w`:** 62% for the area effect and 74% for the fraction effect. The toe effect is free of `w`; 54% of its variance comes from the thinning length. **Effect of a wide versus narrow `w`:** the area effect rises from 13 to 43 km², while the fraction effect falls from 42 to 17 points. **Cross-world widening `w' = w c^-β` (β = 0.25, 0.5):** the area effect rises from 33 to 48 and 64 km². |

## Files

- `kripa_exp.py`: state abduction, the twins of the 20 000 draws, the real-fact posterior, simulated data sets, variance shares and cross-world dispersion, i.e. T25–T28 (about 3 min on 4 cores).
- `kripa_figs.py`: figures (scheme with maps, dose-response, coverage, dispersion). The map figure comes from `../garancia_go/gar_figs.py`.
- `cards_kripa.py`: the twenty cards, the rows of the state-of-the-art table and a one-line novelty per card.
- `text_kripa.py`: the text, including the three-page summary of novelty (Section 7). Every number is filled in from the results.
- `build_kripa_doc.py`: the Word document (OMML equations through `../ml_paradigms/word/omml.py`).
- `run_all.sh`: runs everything.
