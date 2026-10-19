# KUFI-GO: choosing a pumping threshold safely

A well-field manager chooses a pumping rule from the family d_x: "pump high until a toe reading
exceeds x, then pump low for good". The aim is the highest threshold x, i.e. the most high-rate
pumping, such that the risk of salinization within 8 years stays at or below α.

The risk ψ(x) has to be estimated from data. Choosing the threshold whose estimate looks safest is
itself a source of error.

These scripts compare selection rules on observational well-field records (as in TMLE-GO) with the
same rules on a designed experiment in which thresholds are randomized across wells.

**Model.** The KRAMERS-GO toe model (`../kramers_go/kramers2.py`) and the TMLE-GO well field (see
`../tmle_go/`):
- reviews at Poisson times;
- the operator's decisions depend on the toe reading and a drought index;
- informative drop-out from monitoring;
- horizon H = 8 yr.

`tmle_go.py` here is an extended copy of the TMLE-GO code. It adds:
- threshold regimes `dyn@x`;
- per-well thresholds for the experiment;
- pumped volume;
- returned influence curves.

The threshold grid is x = 0.62, 0.64, …, 0.80. True risk rises from 0.289 to 0.431 along the grid
(400 000 simulated wells per regime). Always-low pumping has risk 0.257.

For α = 0.35 the optimal threshold is 0.68; for α = 0.38 it is 0.72.

**Selection rules.** Each takes the largest x whose curve U(x) ≤ α. If none qualifies, the rule falls
back to always-low pumping.
- `naive`: followers' crude risk.
- `plugin`: TMLE point estimate.
- `point`: pointwise one-sided 95% upper bound.
- `band`: simultaneous one-sided 95% upper band. Its critical value is the 95% quantile of max_k Z_k,
  where Z ~ N(0, corr of the K influence curves).
- `band_first`: stops at the first crossing.
- `msm`: simultaneous band of a working marginal structural model, logit ψ(x) = b0 + b1 (x − 0.71)/0.1,
  fitted to the K TMLE estimates. Its influence curves come from the delta method.

**Experiment.** Each well gets a threshold uniformly at random from the grid. The operator follows it,
and the well stays monitored. Arm means and a pooled logistic MSM with sandwich influence curves are
used.

**Gain** is the share of the achievable increase in pumped volume over always-low pumping that the
chosen threshold realizes (1 = optimal threshold). Values above 1 mean a threshold above the optimum,
i.e. a violation.

| File | What it does |
|---|---|
| `tmle_go.py` | Simulator and estimators (extended copy). |
| `kufi_exp.py` | Observational study: truth, then 300 data sets each at 1 000, 2 000 and 4 000 wells, with and without the drought index. Writes `kufi_results.json`. |
| `kufi_rct.py` | Randomized-threshold experiment at the same sizes; adds `<n>|rct` entries. |
| `kufi_figs.py` | `figK1_curve.png` and `figK2_safety.png`. |

Run, in order (about 11 minutes on 4 cores):

```
python3 kufi_exp.py
python3 kufi_rct.py
python3 kufi_figs.py
```

## Main results (α = 0.35; P(violation) / gain / fall-back to always-low)

| Data, rule | 1 000 wells | 2 000 wells | 4 000 wells |
|---|---|---|---|
| observational, TMLE point estimate | 0.72 / 1.00 / 0.05 | 0.58 / 0.97 / 0.05 | 0.57 / 0.98 / 0.02 |
| observational, pointwise bound | 0.22 / 0.53 / 0.43 | 0.18 / 0.52 / 0.40 | 0.12 / 0.53 / 0.35 |
| observational, simultaneous band | 0.10 / 0.33 / 0.62 | 0.08 / 0.35 / 0.57 | 0.05 / 0.32 / 0.57 |
| observational, MSM band | 0.08 / 0.24 / 0.74 | 0.07 / 0.25 / 0.70 | 0.06 / 0.30 / 0.64 |
| experiment, simultaneous band | 0.02 / 0.18 / 0.76 | 0.00 / 0.29 / 0.58 | 0.00 / 0.47 / 0.32 |
| experiment, MSM band | 0.01 / 0.38 / 0.52 | 0.01 / 0.65 / 0.19 | 0.00 / 0.84 / 0.03 |

**Observational records:**
- Picking the threshold with the TMLE point estimate breaks the risk constraint in 57–72% of data sets.
- The simultaneous band brings this down to 5–10%. Its coverage is below the nominal 95% (64–80%)
  because positivity is weak.
- The price of safety is that the band rule mostly falls back to low pumping. It realizes about a third
  of the achievable gain, and this does not improve with more wells.

**Randomized-threshold experiment, with the MSM band:**
- Violations stay at 0–1%.
- It realizes 38%, 65% and 84% of the gain at 1 000, 2 000 and 4 000 wells.
- Band coverage is 90–94%; MSM band coverage is about 92%.

The experiment keeps every well monitored (no drop-out), which is part of its advantage.

The report is
`docs/literature/Literature_review_TMLE_II_Regimes_Policies_Designs_2020-2026.docx` (section 10).
