# TMLE-GO: targeted estimation of a well's salinization risk under pumping regimes

A well-field operator reviews each supply well at irregular times. At each review the operator reads the
toe of the saltwater interface, sees a drought index, and sets pumping to high or low. Drought raises both
pumping (demand) and the salinization risk, so the confounding varies over time. Pumping also moves the
toe, which feeds back into later decisions.

These scripts ask two questions:
- From such observational records, what is the risk that a well salinizes within H years under a pumping
  regime: always high, always low, or "high until a toe reading exceeds a threshold, then low for good"?
- Which records must the monitoring keep for that causal estimate to be right?

The estimator follows the idea of Rytgaard, Gerds & van der Laan (2022, *Ann. Statist.* 50:2469–2491):
sequential regressions and the targeting step are done only at the times when something happens. Here
those are the operator's reviews, which fall at different continuous times for each well. No time grid
is used.

**Model.** The toe model is the one in KRAMERS-GO (`../kramers_go/kramers2.py`):
- A Strack toe X = x_toe/d relaxes toward equilibrium with τ = 2 yr.
- Recharge enters as a lognormal factor r = exp(ε − s²/2), where ε is an Ornstein–Uhlenbeck process
  with s = 0.3 and θ = 0.5 yr.
- Pumping is 0.95 Qc when high and 0.80 Qc when low.
- Salinization means X ≥ 0.98, and Y = 1{salinized within H = 8 yr}.

**Data.**
- Reviews occur at Poisson times with rate 1 per year, plus t = 0.
- The toe reading has 40 m noise.
- The drought index is the mean of ε over the last half year.
- The operator's choice of pumping is logistic in: previous status, reading, drought index, and a
  well-level covariate W.
- Wells leave monitoring more often when the reading is high (informative censoring).

**Estimators** of ψ_d = E[Y^d], computed by sequential regression over the review index j with the
review time as a covariate:
- naive (followers of the regime);
- IPW (Hajek);
- ICE g-computation;
- TMLE with weighted logistic fluctuation and influence-curve standard errors.

The outcome model is either "poor" (time to horizon only) or "flexible" (reading, its square, time,
drought and interactions). The treatment and censoring models are pooled logistic regressions.

Requirements: Python 3 with NumPy, SciPy and matplotlib. `kramers2.py` is imported from
`../kramers_go`.

| File | What it does |
|---|---|
| `tmle_go.py` | Simulator (observational data and regimes), nuisance models, and estimators. |
| `tmle_exp.py` | Writes `tmle_results.json`. **T1:** six estimators for three regimes over 500 data sets of 2 000 wells; truth from 400 000 simulated wells per regime. **T2:** TMLE of the risk difference ψ_hi − ψ_lo for four recording designs (operator reading; precise 10 m sensor; each with or without the drought index) at 500–8 000 wells, 200 data sets each. |
| `tmle_figs.py` | The two figures of the report (`figT1_estimators.png`, `figT2_design.png`). |

Run (about 4 minutes on 4 cores):

```
python3 tmle_exp.py
python3 tmle_figs.py
```

## Main results

True risks within 8 years: 0.516 (always high), 0.256 (always low) and 0.375 (dynamic rule); the risk
difference is 0.260.

**T1 (2 000 wells; bias, Monte Carlo SD, 95% CI coverage):**

| Estimator | Always high | Dynamic rule |
|---|---|---|
| naive | +0.141, 0.025 | +0.157, 0.035 |
| IPW | −0.000, 0.051 | −0.001, 0.070 |
| g-computation, poor model | −0.085, 0.027 | −0.133, 0.029 |
| g-computation, flexible | −0.039, 0.029 | −0.018, 0.042 |
| TMLE, poor outcome model | −0.009, 0.050, 91% | −0.009, 0.072, 86% |
| TMLE, flexible | −0.010, 0.047, 88% | −0.006, 0.068, 85% |

For always-low pumping, TMLE coverage is 95%. Coverage is lower when the regime asks for decisions the
operator rarely takes, because the cumulative weights 1/G_j grow large (weak positivity).

**T2 (TMLE of the risk difference; bias and RMSE):**

| Records kept | Bias, 1 000 wells | RMSE, 1 000 wells | Bias, 8 000 wells | RMSE, 8 000 wells | Coverage, 8 000 wells |
|---|---|---|---|---|---|
| operator reading | +0.052 | 0.078 | +0.069 | 0.073 | 5% |
| precise 10 m sensor | +0.047 | 0.075 | +0.065 | 0.068 | 7% |
| operator reading + drought index | −0.009 | 0.076 | −0.002 | 0.026 | 95% |
| precise sensor + drought index | −0.007 | 0.079 | −0.002 | 0.026 | 94% |

Without the drought index, bias stays near 0.07 however many wells are added. A more precise toe sensor
does not fix this. Recording what the operator based decisions on (a decision log) makes the effect
identifiable. With 2 000 wells, the decision log already reaches an error (RMSE 0.050) that the design
without it does not reach even with 8 000 wells (RMSE 0.073).

The report is
`docs/literature/Literature_review_TMLE_Continuous_Time_Outcome_Means_Under_Intervention_2020-2026.docx`
(section 10).
