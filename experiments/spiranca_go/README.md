# SPIRANCA-GO: a chloride alarm that survives the pumping decision

Experiment of the note *What the twenty chloride papers and anchor regression give the Fushë-Kuqe work: checks,
extractions and a chloride alarm that survives the decision* (October 2026). *Spiranca* is Albanian for the anchor.

The note reads two documents:
- the twenty-paper note of 19 October 2026 for the chloride manuscript, with its proposals N1–N3;
- Rothenhäusler, Meinshausen, Bühlmann & Peters (2021), *Anchor regression: heterogeneous data meet causality*,
  JRSSB 83(2), 215–246.

## The test bed (`sg_model.py`)
The areal model of the chloride study (`chloride_fk/python/fkcl_model.py`): steady Strack potential on the coastal
sector north of y = 24 km, prior draws of conductivity, geometry, mixing width and sea chloride, and the two supply
wells of PRAG-GO (A1, P10). The potential is linear in the sources, so every season is a combination of four unit
responses:
- recharge;
- the two supply wells;
- a hidden private abstraction over the coastal plain.

The goal is the chloride of the upper screen of A1 above 250 mg/L.

Seasons have recorded anchors and unrecorded parts:
- **anchors (recorded):** rainfall anomaly at the gauge, operator pumping of A1 and P10;
- **unrecorded:** recharge noise, private abstraction.

The future has three parts:
- **the decision:** known, outside the record;
- **a warming:** unrecorded, in the span of the rainfall anchor, one-sided;
- **an off-span stress test.**

## Scripts
- `sg_run.py [NT] [workers]`: 100 aquifers by default. It compares seven alarms (least squares on heads, anchor
  regression with cross-validated or decision-matched gamma, IV, least squares on heads and anchors with and without
  the certificate, SPIRANCA-GO) and three designs of three piezometers → `res/sg.json` (about a minute on two cores).
- `sg_checks.py`: numerical checks of N1–N3 of the twenty-paper note → `res/checks.json`.
- `sg_ltt.py`: what the fixed-sequence certificate (N2, Learn then Test) costs on the safe yields of MONTIMI-GO
  (reads `../montimi_go/res/qcrit_F_EVA.npz`) → `res/ltt.json`.
- `sg_figs.py`: `res/figS1_map.png`, `res/figS2_results.png`, `res/figS3_checks.png`.
- `sv_model.py`, `sv_run.py [NA] [workers]`: the same test on the variable-density section of MONTIMI-GO, with memory and
  nonlinear heads → `res/sv.json` (20 aquifers in about ten minutes on four cores). The note's Section 7 uses it.
  - **The section:** the goal-guided assembly of experiments/montimi_go, run season by season.
  - **Additions:** a seasonal inflow, a hidden private abstraction and per-season pumping.
  - **Anchors:** filtered over 2, 8 and 20 years.
  - **Goal:** −log10 of the screen sea fraction.
  - **Re-anchoring variant:** a yearly chloride sample at the supply screen.
- `run_all.sh`: all of it.

## Main results (100 aquifers)
Share of future seasons in which the alarm over-predicts by more than its margin, with 10 % allowed:

| Alarm | Worst unrecorded warming | Off-span stress |
|---|---|---|
| least squares on heads | 91 % | |
| least squares on heads and anchors | 36 % | |
| SPIRANCA-GO | 2.4 % | 10.2 % (outside its guarantee) |

- SPIRANCA-GO's margin is 68 % of the same certificate added to least squares.
- The SPIRANCA-GO design of three piezometers picks the inland well A13 in 94 of 100 aquifers.

On the variable-density section (20 aquifers, `res/sv.json`):
- The certificate held under the worst unrecorded warming in 18 of 20 aquifers.
- After the decision alone it failed in 9 of 20 (mean 26.3%). The failures are where the decision moved the screen into
  a regime the record had not seen.
- Re-anchored by one chloride sample a year at the supply screen, the alarm over-predicted in 3.4% of the
  seasons (1 aquifer above 10 %), with false alarms 54%.
- Least squares plus the certificate: 4.3%, with false alarms 79%.
- Re-anchoring without the certificate: 24.8%.

The note's builder reads every number from `res/` and checks each claim.
