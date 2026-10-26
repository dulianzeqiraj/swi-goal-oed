# VENDIMI-GO: how the Fushë-Kuqe stakeholders reach a decisive joint choice under deep uncertainty

Innovation of literature review 57 (decisive stakeholder decisions under stochastic and deep uncertainty: 20 papers of
2020–2026 from Oxford, Caltech, MIT and ETH Zürich). *Vendimi* is Albanian for the decision.

**Setting.** The calibrated chloride ensemble of PUSI-GO (`../pusi_go`; Strack potential with a dispersive mixing zone,
20 000 weighted draws). Supply wells A1 and P10 with 20-m screens; failure = screen chloride above 250 mg/L at either
well. Decisions: pumping scale s (units of the PUSI-GO rates, 12 060 m³/d in total), recharge q per site at the three
PUSI-GO sites (0, 2 500, 5 000 or 10 000 m³/d), and whether to buy information first (one shallow chloride sample at
A30, or the three PRAG-GO heads). Five stakeholders hold different beliefs, each an exponential tilt of the calibrated
posterior along the disputed drivers (standardised log mixing width and log recharge): the utility (no tilt),
irrigators and hotels (optimists), the municipality, the regional water agency (drying climate) and environmental
groups (pessimists).

**Propositions (section 9 of the review).**
1. *V1, disagreement bound.* |P_k(F|y) − P_j(F|y)| ≤ max_t sd(Δλ·z | y) · sd(1_F | y) ≤ ½ max_t sd(Δλ·z | y): data end a
   dispute when they resolve the event, not only the disputed parameter.
2. *V2, decisiveness.* Failure is monotone in pumping and recharge, so the admissible pumping under the unanimous rule
   (every stakeholder's certified posterior risk ≤ 10%) is an interval; its largest point is the unique action that no
   stakeholder can veto and none can improve on. Deadlock only if even zero pumping is unsafe for someone, which
   recharge removes.
3. *V3, safe information.* Under the rule each stakeholder's own expected risk stays ≤ 10% with or without data, so
   the group can agree to buy information whenever each member gains in water or in safety.

## Files
- `vendimi.py` → `res/vendimi.json` (about 2 minutes; needs `../pusi_go/res/ens.npz`, made by `../pusi_go/pusi_run.py`).
- `vendimi_figs.py` → `res/figV1_vendimi.png`.
- `run_all.sh`.

## Results (2 000 truths; α = 10%; certified margin 1.645 standard errors; recharged water priced at 0.5)
- Prior risk at the planned pumping (s = 1, no recharge), by stakeholder: 0.37, 0.15, 0.43, 0.57, 0.63; the environmental
  groups cannot accept even zero pumping without recharge.
- Disagreement at s = 0.5: 0.224 without data, 0.208 with three heads, 0.038 with one chloride sample
  (bound of V1 0.659 → 0.134; never violated).
- Decisive joint choice without data: recharge 15,000 m³/d, pumping 9,648 m³/d, net 2,148; with the chloride sample:
  recharge 5,392, pumping 7,821, net 5,125 (deadlock in 4.4% of truths); with three heads: net 1,709.
- The average-belief rule nets more (3,957 and 7,024 m³/d) but is vetoed by 3.0 and 1.8 stakeholders on average.
- Realised failure under each stakeholder's own belief: unanimous rule 0.045, 0.021, 0.079, 0.044, 0.094 (no data) and
  0.024, 0.016, 0.026, 0.056, 0.026 (chloride sample); with the three heads the environmental groups reach 0.107 ± 0.013,
  within one Monte Carlo standard error of the limit (standard errors in `fail_se_by_view`, at least 835 effective truths
  per stakeholder in `view_ess`).
- Value of the chloride sample in net water, by each stakeholder's own expectation: +2,977, +5,351, +1,554, +1,854 and
  −729 m³/d (the environmental groups lose water but their risk falls from 0.094 to 0.026); the heads lower everyone's net water.

Limits: beliefs are tilts of one calibrated ensemble along two drivers; the model is steady and areal; the stakeholders'
utilities are reduced to water, recharge cost and a common 10% risk limit; the information estimates rest on a finite
weighted ensemble (median minimum inner sample size 215 for the chloride sample, 46 for the heads).
