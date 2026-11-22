# QENDRESA-GO: a frugal model of salinization onset with a marginal structural hazard model

Innovation of review 38, "Specifying the causal effect and building the observational model III: 20 more
theorem-level papers" (2020–2026). *Qëndresa* is Albanian for endurance: how long a well holds out before it
salinizes.

**The problem.** Reviews 36 and 37 built and checked a frugal model (Evans & Didelez, JRSS-B 86(3), 535–568, 2024,
https://doi.org/10.1093/jrsssb/qkad058) in which the causal effect of pumping on chloride is a parameter. For a well
field the decisive outcome is often the season in which a well salinizes. This is where marginal structural models
are hardest to build and simulate from:
* hazard ratios are not collapsible;
* the wells at risk are selected by survival;
* the parametric g-formula cannot represent the null.

QENDRESA-GO is a frugal survival model whose causal margin is a marginal structural hazard model.

**The model.** Five seasons; dryness L_k = 0.5 L_{k−1} + 0.6 A_{k−1} + 0.8 W_k (pumping deepens next season's
deficit); managers pump hard with probability expit(0.4 − 0.9 L_k + 0.8 A_{k−1}); hazard MSM
cloglog λ(k; a) = α0 + α1 (k − 1) + β a_k + β_ℓ a_{k−1} with (α0, α1, β, β_ℓ) = (−2.8, 0.15, 0.5, 0.25); copula
V = ρ (W_1 + … + W_5) + sqrt(1 − 5ρ²) ε with ρ = 0.35, and T = min{k : Φ(V) > S(k; A)}.

**The theory (section 11 of the review).**
* Theorem I: the hazard MSM holds exactly for every static regime, pumping is sequentially ignorable, the three
  pieces are variation independent, and the risk of any dynamic rule is E[Φ((c_k(A^g) − m_K)/s_K)].
* Proposition J: the observed hazard is h_k = 1 − Φ((c_k − m_k)/s_k) / Φ((c_{k−1} − m_k)/s_k), and the dryness of
  the wells at risk is a tilted version of the latent law. Hence non-collapsibility, survivor selection and the
  g-null paradox, all in closed form.
* Theorem K: the likelihood in closed form. The pumping factor separates; the dryness factor does not, so fitting the
  dryness model to the survivors alone (the two-step shortcut) is inconsistent.
* The QENDRESA procedure: choose the dynamic rule A_k = 1{L_k < τ} with the largest yield whose upper 95% bound of
  the five-season risk stays within the budget.

## Results

Monte Carlo, 1000 data sets per row (`qendresa_mc.json`): root mean squared error and, in brackets, coverage of the
95% interval.

**β (current pumping; truth 0.5, 0 without effect)**

| Scenario | frugal MLE (joint) | two-step shortcut | IPW hazard MSM | parametric g-formula |
|---|---|---|---|---|
| correct model, n = 1000 | 0.095 (0.95) | 0.117 (0.88) | 0.125 (0.95) | 0.101 (0.95) |
| correct model, n = 4000 | 0.046 (0.95) | 0.082 (0.70) | 0.060 (0.95) | 0.048 (0.95) |
| weak overlap, n = 4000 | 0.050 (0.94) | 0.125 (0.37) | 0.145 (0.95) | 0.058 (0.93) |
| Student-t copula, n = 4000 | 0.050 (0.94) | 0.077 (0.74) | 0.063 (0.95) | 0.052 (0.93) |
| no effect, n = 4000 | 0.046 (0.96) | 0.089 (0.66) | 0.062 (0.96) | 0.050 (0.96) |
| no effect, n = 16 000 | 0.024 (0.94) | 0.079 (0.14) | 0.032 (0.95) | 0.026 (0.94) |

**β_ℓ (pumping in the previous season; truth 0.25, 0 without effect)**

| Scenario | frugal MLE (joint) | two-step shortcut | IPW hazard MSM | parametric g-formula |
|---|---|---|---|---|
| correct model, n = 1000 | 0.092 (0.95) | 0.104 (0.92) | 0.123 (0.97) | 0.230 (0.41) |
| correct model, n = 4000 | 0.047 (0.94) | 0.067 (0.85) | 0.064 (0.95) | 0.217 (0.01) |
| weak overlap, n = 4000 | 0.046 (0.95) | 0.090 (0.65) | 0.150 (0.95) | 0.278 (0.00) |
| Student-t copula, n = 4000 | 0.048 (0.94) | 0.073 (0.77) | 0.065 (0.95) | 0.229 (0.01) |
| no effect, n = 4000 | 0.049 (0.96) | 0.080 (0.78) | 0.070 (0.95) | 0.221 (0.01) |
| no effect, n = 16 000 | 0.025 (0.96) | 0.065 (0.36) | 0.034 (0.96) | 0.214 (0.00) |

**Rejection of a true null at the 5% level (the survival g-null paradox)**

| No effect | frugal MLE (joint) | two-step shortcut | IPW hazard MSM | parametric g-formula |
|---|---|---|---|---|
| β = 0, n = 4000 | 3.7% | 33.7% | 4.0% | 3.8% |
| β_ℓ = 0, n = 4000 | 3.9% | 22.0% | 4.8% | 98.8% |
| β = 0, n = 16 000 | 5.8% | 85.5% | 4.5% | 5.7% |
| β_ℓ = 0, n = 16 000 | 4.1% | 63.8% | 4.3% | 100.0% |

**Choosing the rule A_k = 1{L_k < τ} under a five-season risk budget of 0.45**: share of data sets whose chosen rule
truly breaks the budget (by more than 0.01) · true yield of the chosen rule (hard-pumping seasons per well before
salinization).

| Choice by | correct, n = 1000 | correct, n = 4000 | weak overlap | Student-t copula |
|---|---|---|---|---|
| frugal plug-in | 21.7% · 2.06 | 6.2% · 2.08 | 5.3% · 2.07 | 7.9% · 2.08 |
| **frugal upper bound (QENDRESA)** | 1.4% · 1.57 | 0.1% · 1.85 | 0.0% · 1.85 | 0.0% · 1.86 |
| IPW, artificial censoring | 51.4% · 2.27 | 31.2% · 2.10 | 24.9% · 2.05 | 28.7% · 2.08 |
| parametric g-formula | 32.1% · 2.11 | 17.0% · 2.13 | 6.0% · 2.05 | 16.8% · 2.12 |
| oracle | τ = 0.25 · 2.10 | τ = 0.25 · 2.10 | τ = 0.25 · 2.10 | τ = 0.25 · 2.09 |

Key findings:
* **Confounding reverses the effect.** Wells that always pumped hard stay fresh more often than wells that never did
  (58% vs 45% after five seasons). Causally it is the opposite
  (42% vs 66%), because managers spare the dry, vulnerable wells.
* **The joint frugal MLE is unbiased with honest intervals** (coverage 0.94–0.96).
  * It is more efficient than inverse weighting: the variance ratio for β is
    1.69 at n = 4000 and
    8.62 under weak overlap.
  * The ratio stays between 1.68 and 1.93 for ρ from 0 to 0.4 (`qendresa_curve.json`).
* **The two-step shortcut is wrong.** Fitting the dryness model to the survivors alone biases β and, with no effect,
  reports one in 86% of data sets at n = 16 000.
* **The parametric g-formula misses the lagged effect.** Its limit is β_ℓ = 0.047 instead of
  0.25, and -0.209 instead of 0. With no effect it rejects β_ℓ = 0 in
  100% of data sets.
* **The QENDRESA rule (upper 95% bound) keeps the budget.** It is broken in
  1.4% of data sets at n = 1000 and
  0.1% at n = 4000, against
  51% and 31%
  when choosing by IPW. The cost is 0.52 and
  0.24 hard-pumping seasons per well.

## Files

| File | What it does |
|---|---|
| `qendresa_model.py` | The frugal survival model: simulation (observed data, static regimes, dynamic rules; Gaussian or Student-t copula), exact counterfactual survival, the observed hazard of Proposition J, true risk and yield of the rules. |
| `qendresa_est.py` | Joint frugal MLE with analytic scores (Theorem K), the two-step shortcut, IPW for the hazard MSM, the parametric g-formula with delta-method errors, and the frugal, IPW and g-formula values of dynamic rules with delta-method bands. |
| `qendresa_exp.py` | Monte Carlo study (six scenario–size pairs × 1000 data sets) → `qendresa_mc.json` (about 2 hours on 4 cores; `python3 qendresa_exp.py weak` reruns one scenario). The rules are integrated with 2^14 scrambled Sobol points. |
| `qendresa_curve.py` | Limits on 400 000 wells, efficiency against the copula strength, non-collapsibility, survivor selection and the naive comparison → `qendresa_curve.json` (about 6 minutes). |
| `qendresa_figs.py` | Figures `figQ1_mechanism.png`, `figQ2_montecarlo.png`, `figQ3_design.png`. |
| `run_all.sh` | Runs the three stages. |

## Run

```bash
pip install numpy scipy matplotlib
bash run_all.sh
```

## Limitations

* The copula has one parameter, linking the failure rank to the sum of the dryness scores.
* Dryness is Gaussian, observed every season and the only confounder.
* Seasons are discrete, with no competing events.
* The frugal estimate assumes no unmeasured confounding of pumping given dryness.
* The numbers are synthetic, not calibrated to the Fushë-Kuqe wells.
