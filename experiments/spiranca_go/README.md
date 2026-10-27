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

The note's builder reads every number from `res/` and checks each claim.
