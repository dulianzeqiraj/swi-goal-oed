# KANAL-GO: which pumping experiment best measures the causal information flow?

RRJEDHA-GO (`../rrjedha_go/`) measured how many bits pumping passes to the yearly change of the saltwater toe.
KANAL-GO asks how an experiment should be designed to measure that number.

**Model.** The well field is the RRJEDHA-GO model:
- The operator decides pumping A each year from the alarm level R (4 classes), a drought class D (3) and last
  year's decision.
- The outcome is the toe change ΔX (3 classes). Both potential outcomes are simulated for every well-year.
- 200 000 wells × 10 years.

**Goals.** The interventional information flow TE(π) of three pumping rules π(1 | r):
- `op`: the operator's own marginal rule, (0.45, 0.46, 0.34, 0.25) for R = 0, …, 3.
- `caut`: a cautious rule, (0.9, 0.6, 0.2, 0.05).
- `bal`: π = 1/2 at every level. For weak effects this equals the causal channel capacity of pumping.

**Designs.** A one-year pumping test on n well-years drawn from the field:

| Design | P(A = 1 \| R) |
|---|---|
| `natural` | Follows the rule being evaluated, q = π. |
| `balanced` | q = 1/2 at every alarm level. |
| `capped` | 1/2, except at the highest alarm level, where it is capped at the operator's own rate (0.25). |
| `obs` | Reference only: the operator's records, analysed with back-door adjustment for (D, A_prev). |

Every estimate is the plug-in TE with a multinomial-bootstrap bias correction and the basic 95% interval.

## Theory (small effects)

Let Δ_k = P(k | do 1, r) − P(k | do 0, r).

- The information flow of any rule at alarm level r is a fixed fraction of the causal channel capacity C_r:

  TE_r(π) ≈ 4π(1 − π)·C_r, with C_r ≈ χ²_r / (8 ln 2) and χ²_r = Σ_k Δ_k² / P̄_k.

- The variance-optimal (Neyman-type) allocation is q*(a | r) ∝ π(a | r)·sd_{a,r}. Since sd_{a,r} ∝ π(1 − a | r),
  this gives q* = 1/2 for every rule.
- The variance ratio between following the rule and 50/50 randomization is 1 / (4π(1 − π)) at each level.

## Files

| File | What it does |
|---|---|
| `kanal.py` | Model access, TE of a rule, capacity (grid search) and χ² approximation, designs, estimators, bootstrap. |
| `kanal_exp.py` | Population values, then 400 data sets of 500, 2 000 and 8 000 well-years for each design and goal (300 bootstrap resamples). Writes `kanal_results.json`. Needs `../rrjedha_go/`. |
| `kanal_figs.py` | `figN1_kanali.png` and `figN2_dizajni.png`. |

Run `python3 kanal_exp.py` and then `python3 kanal_figs.py`. The experiment takes about 1.5 minutes on 4 cores.

## Main results

**Population values.**
- The capacity C_r by alarm level is 11.5, 13.4, 15.2 and 18.4 millibits.
- The capacity-achieving pumping probability is 0.50 at every level.

| Rule | TE, exact (millibits) | 4π(1 − π)C (millibits) |
|---|---|---|
| Operator | 12.98 | 12.98 |
| Cautious | 6.40 | 6.39 |
| Balanced | 14.87 | 14.87 |

**Precision.** Bias / SD in millibits, then coverage of the 95% interval:

| Goal, design | 500 | 2 000 | 8 000 |
|---|---|---|---|
| operator rule, records + back-door | +7.1 / 14.1, 92% | +3.1 / 9.0, 90% | +0.0 / 4.7, 88% |
| operator rule, follow the rule | −0.5 / 10.1, 94% | −0.1 / 4.6, 94% | −0.1 / 2.3, 92% |
| operator rule, 50/50 | −0.3 / 9.3, 94% | +0.2 / 4.5, 92% | −0.0 / 2.1, 93% |
| cautious rule, records + back-door | +4.0 / 8.4, 90% | +1.5 / 5.0, 92% | −0.1 / 2.3, 92% |
| cautious rule, follow the rule | −0.0 / 8.5, 97% | −0.1 / 3.5, 93% | +0.1 / 1.5, 96% |
| cautious rule, 50/50 | −0.3 / 6.0, 94% | +0.1 / 2.6, 92% | −0.1 / 1.2, 94% |

- The 50/50 design has the smallest SD for every goal.
- **Variance relative to 50/50 at 8 000 well-years:**

  | Design | Operator rule | Cautious rule |
  |---|---|---|
  | Follow the rule | 1.24 | 1.57 |
  | Records + back-door | 5.1 | 3.8 |

- One 50/50 experiment estimates the flow of every rule. Following the rule needs a separate experiment for
  each rule.
- Capping high pumping at the highest alarm level costs little.
- The delta-method SD from the theory matches the simulated SD to within 7% at 8 000 well-years and within
  17% at 2 000. At 500 it is 14–40% too small.

The report is
`docs/literature/Literature_review_Information_Theory_Causality_II_2020-2026.docx` (section 9).
