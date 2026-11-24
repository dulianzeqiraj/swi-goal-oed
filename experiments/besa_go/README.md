# BESA-GO: two checks and a repair that keep the frugal model honest

Innovation of review 37, "Specifying the causal effect and building the observational model II: 20 more
theorem-level papers" (2020–2026). *Besa* is the Albanian word of honour, a promise that is kept.

**The problem.** KURSIM-GO (`../kursim_go/`, review 36) built a frugal model of pumping, salinity alarms and chloride
in which the causal effect of pumping is a parameter (Evans & Didelez, JRSS-B 86(3), 535–568, 2024,
https://doi.org/10.1093/jrsssb/qkad058). Its likelihood is efficient, but only if the copula between chloride and
the confounders is right. BESA-GO checks the model and repairs it within the frugal family, so that the simulator
survives.

**The theory (section 11 of the review).**
* Proposition E: the frugal model implies closed-form outcome regressions,
  Q2 = θ0 + θ1 a1 + θ2 a2 + s ρ1(a2) l1 + s ρ2(a2) λ(l2, t) and Q1 = θ0 + θ1 a1 + θ2 a2 + s ρ1(a2) l1
  (the alarm term averages to zero exactly).
* Theorem F: the augmented estimator built from these regressions is doubly robust; its bias is
  E[(g1⁰/g1 − 1)(Q1⁰ − Q1)] + E[(I1/g1)(g2⁰/g2 − 1)(Q2⁰ − Q2)].
* Theorem G (Hausman–Wu): with a correct model and correct propensities, √n(θ̂_DR − θ̂_MLE) → N(0, V_DR − V_MLE);
  the test uses the empirical covariance of the difference of the full influence functions.
* Proposition H: a copula that depends on season-2 pumping is still a frugal model with the same causal margin;
  the likelihood-ratio test of the common copula against it needs no propensity model.
* BESA procedure: likelihood-ratio check → working copula → Hausman check → working MLE, or the frugal-augmented
  doubly robust estimate if the check rejects.

## Results

Monte Carlo, 1000 data sets per row (`besa_mc.json`): root mean squared error of θ2 (truth 0.45) and, in
brackets, the coverage of the 95% interval; last column: rejection rates of the likelihood-ratio and Hausman checks.

| Scenario | frugal MLE, common | frugal MLE, pumping-dependent | frugal-augmented DR | DR, linear | IPW | **BESA** | LR / Hausman reject |
|---|---|---|---|---|---|---|---|
| correct model, n = 1500 | 0.024 (0.95) | 0.024 (0.95) | 0.028 (0.95) | 0.028 (0.95) | 0.030 (0.97) | 0.025 (0.95) | 6% / 4% |
| correct model, n = 6000 | 0.012 (0.95) | 0.012 (0.95) | 0.014 (0.95) | 0.015 (0.95) | 0.015 (0.97) | 0.013 (0.94) | 4% / 5% |
| pumping-dependent copula, n = 1500 | 0.035 (0.83) | 0.023 (0.95) | 0.027 (0.95) | 0.028 (0.95) | 0.029 (0.98) | 0.024 (0.95) | 100% / 30% |
| pumping-dependent copula, n = 6000 | 0.029 (0.40) | 0.011 (0.95) | 0.013 (0.95) | 0.013 (0.95) | 0.014 (0.98) | 0.012 (0.94) | 100% / 89% |
| same, no effect, n = 6000 | 0.029 (0.42) | 0.011 (0.96) | 0.013 (0.96) | 0.013 (0.96) | 0.014 (0.99) | 0.012 (0.96) | 100% / 91% |
| wrong propensity model, n = 1500 | 0.023 (0.95) | 0.023 (0.95) | 0.028 (0.95) | 0.030 (0.93) | 0.035 (0.94) | 0.024 (0.95) | 5% / 4% |
| wrong propensity model, n = 6000 | 0.012 (0.94) | 0.012 (0.94) | 0.014 (0.94) | 0.016 (0.90) | 0.025 (0.77) | 0.013 (0.93) | 5% / 6% |
| both wrong, n = 6000 | 0.027 (0.46) | 0.011 (0.95) | 0.013 (0.96) | 0.016 (0.88) | 0.039 (0.37) | 0.012 (0.95) | 100% / 5% |
| skewed dryness copula, n = 6000 | 0.012 (0.95) | 0.012 (0.95) | 0.014 (0.94) | 0.014 (0.94) | 0.015 (0.97) | 0.012 (0.95) | 36% / 5% |

* A copula that depends on pumping biases the usual (common-copula) frugal estimate of θ2 by −0.025 (6% of the
  effect); its coverage falls to 0.40 at n = 6000, and with no effect it declares one in 57.5% of data sets.
  BESA detects it, repairs it and brings false discoveries back to 4.3%.
* A wrong propensity model biases weighting (IPW coverage 0.77) but not the frugal estimators; the checks stay quiet.
* With both errors the Hausman check is blind (5%), as Theorem F predicts, but the likelihood-ratio check is not (100%).
* When the model is right, BESA costs almost nothing (RMSE 0.025 vs 0.024 at n = 1500).

`besa_curve.json` gives the limits of the estimators and the asymptotic power of both checks along a path of
copulas, ρ2 = 0.55 ∓ Δ/2 without and with pumping (one data set of 300 000 wells per point).

## Files

| File | What it does |
|---|---|
| `besa_model.py` | Data-generating processes (common, pumping-dependent and skewed-dryness copulas; correct and misspecified pumping rules) and the frugal likelihood with a copula that may depend on season-2 pumping. Imports `../kursim_go/kursim_model.py`. |
| `besa_est.py` | Frugal MLE (common, pumping-dependent) with influence functions, the frugal-augmented doubly robust estimator with its full influence function, the Hausman and likelihood-ratio checks and the BESA procedure; reuses `../kursim_go/kursim_est.py`. |
| `besa_exp.py` | Monte Carlo study (nine scenario–size pairs × 1000 data sets) → `besa_mc.json` (about 25 minutes on 4 cores; `python3 besa_exp.py both` reruns one scenario). |
| `besa_curve.py` | Limits and power along a path of copulas → `besa_curve.json` (about 6 minutes on 4 cores). |
| `besa_figs.py` | Figures `figB1_path.png` and `figB2_scenarios.png`. |
| `besa_quick.py` | One data set per scenario and size, all estimators and checks (about 3 minutes). |
| `run_all.sh` | Runs the three main stages. |

## Run

```bash
pip install numpy scipy matplotlib
bash run_all.sh
```

## Limitations

The checks look in two directions only (a copula that depends on season-2 pumping; misspecification that moves the
causal estimate when the propensity models are right). The procedure selects a model with the same data it uses for
inference, and its intervals are not adjusted for the selection (coverage 0.93–0.95 here). The variances are
asymptotic; the model has two seasons, one binary alarm and binary pumping; the numbers are synthetic, not calibrated
to Fushë-Kuqe wells.
