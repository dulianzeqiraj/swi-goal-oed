# BARASPESHA-GO: augmented balancing weights when the outcome model is a complex aquifer simulator

Innovation of review 40, "Augmented balancing weights and complex models: 20 papers for the seawater-intrusion
problem" (2020–2026). *Baraspesha* is Albanian for balance.

**The problem.** The anchor paper of review 40 (Bruns-Smith, Dukes, Feller & Ogburn, "Augmented balancing weights as
linear regression", JRSS-B 2025, https://doi.org/10.1093/jrsssb/qkaf019) shows that augmented balancing weights
(automatic debiased machine learning) are one linear regression when the outcome and weighting models are linear in a
basis: ridge plus ridge is one undersmoothed ridge, and exact balance collapses to least squares.

In a coastal well field the outcome model is not linear. It is a complex simulator of the freshwater–seawater
interface, informative but biased: its parameters are uncertain and its physics is incomplete. BARASPESHA-GO asks:
* what augmentation does with such a model;
* how to build the balancing weights from the simulator's own physics;
* how to keep the intervals honest when the bias is not negligible;
* which wells to measure for the goal of the study.

**The model.**
* The field: a 10 km coast, an unconfined aquifer with its base 30 m below sea level, and 400 wells. Each well has:
  * a distance to the coast x_w (250 m to 4 km);
  * a position along the coast;
  * a baseline pumping rate Q_0 (around 300 m³/day);
  * a pumping-test log conductivity, biased by +0.2 and noisy (s.d. 0.25).
* Physics: Strack's (1976) single-potential solution. The stagnation point lies at x_s = x_w sqrt(1 − μ), with
  μ = Q / (π q x_w). The margin m = φ(x_s)/φ_toe − 1, with φ_toe = δ(1 + δ)d²/2.
* Chloride: log10 chloride = log10(C_f + C_s f_max Φ(−m/ω)) + noise (s.d. 0.08).
* Truth:
  * regional discharge q = 0.8 m²/day;
  * mixing width ω = 0.25 (Q/300)^0.3;
  * conductivity that varies along the coast and from well to well (s.d. 0.3);
  * in scenario S3, a base depth that varies along the coast by ±6 m.
* The complex model: the same solution with the pumping-test conductivity, q = 0.6, a constant ω = 0.4 and a
  constant base. Three global parameters θ (log multipliers of K, q, ω) can be calibrated.
* Treatment: a cut of pumping to 60%, adopted (30% of wells) where the agency's simulator predicts salt and near the
  coast.
* Target: ψ, the mean log chloride that the adopting wells would have had without the cut. Their effect is their
  observed mean minus ψ: −0.164 log units, a fall of about 31% in chloride.

**The theory (sections 1 and 8 of the review).**
* Theorem 5 (part I): ridge outcome model + ridge weights = one generalized ridge regression with penalty
  λδ(G + (λ + δ)I)⁻¹, smaller than λ and δ in every eigen-direction (undersmoothing).
* Corollary 7: with any complex outcome model, the augmented estimator is the simulator plus a ridge regression of its
  residuals. With exact balance it is least squares plus the part of the simulator outside the balanced span.
* Theorem M:
  * ridge weights on the simulator's sensitivities give one Levenberg–Marquardt step of the simulator, calibrated on the
    controls;
  * at the least-squares calibration, exact balance of the sensitivities reproduces the calibrated simulator
    (calibration is augmented balancing on the sensitivities);
  * the error splits into the imbalance of the sensitivities times the parameter error, plus the imbalance of the
    structural error.
* Lemma P: chloride depends on K and the base depth d only through K d², so a varying base is exactly a local
  log-conductivity error.
* Theorem N: the discrepancy class "parametric error within three calibration standard errors + a local log K field
  carried by the sensitivity s_K + a smooth remainder" is the unit ball of the physics kernel
  K_phys = S Γ Sᵀ + τ² (s_K s_Kᵀ) ∘ k_mod + B² k_gen.
  * The minimax weights (summing to one) equal the simulator plus kernel ridge regression of its residuals, with a
    free intercept.
  * The worst-case bias gives honest bias-aware intervals (Armstrong–Kolesár).
  * The noise model is the physics one: var(Y | X) = a + b s_K².
* Proposition O: V(D) = k11 − c_Dᵀ (K_DD + D_D)⁻¹ c_D is the worst-case mean squared error of the target for a set D of
  measured wells. It is computable before measuring and is minimized greedily by rank-one updates, batch-sequentially
  (pilot of 10, batches of 10, recalibrating between batches).

## Results

**Exactness checks (`baraspesha.json`, part A).** Largest absolute difference between the two sides of each identity on
one well field: ridge + ridge vs generalized ridge 2.7e-15; exact balance vs least squares + out-of-span part 7.1e-10;
sensitivity balance vs one Levenberg–Marquardt step 4.4e-16; exact sensitivity balance at the least-squares calibration
vs the calibrated simulator 1.1e-9; minimax physics-kernel weights vs simulator + kernel ridge 1.3e-15.

**Monte Carlo (part B).** Root mean squared error of ψ (log10 mg/L) · coverage of the nominal 95% interval; 1000 well
fields per scenario.

| Estimator | S1 baseline | S2 weak overlap | S3 structural error | S4 near-correct simulator | S5 small field |
|---|---|---|---|---|---|
| Mean of the control wells | 1.067 · – | 1.192 · – | 1.031 · – | 1.066 · – | 1.077 · – |
| Simulator, nominal parameters | 0.338 · – | 0.294 · – | 0.369 · – | 0.020 · – | 0.344 · – |
| Simulator, calibrated on the controls | 0.047 · 48% | 0.050 · 50% | 0.071 · 53% | 0.046 · 51% | 0.063 · 58% |
| Linear regression adjustment | 0.202 · 4% | 0.278 · 0% | 0.186 · 10% | 0.201 · 3% | 0.220 · 35% |
| Kernel balancing weights alone | 0.337 · 2% | 0.370 · 2% | 0.340 · 3% | 0.336 · 1% | 0.480 · 3% |
| AutoDML: kernel ridge + kernel weights | 0.095 · 52% | 0.118 · 52% | 0.128 · 59% | 0.105 · 55% | 0.186 · 52% |
| Calibrated simulator + kernel weights | 0.030 · 87% | 0.031 · 90% | 0.048 · 83% | 0.031 · 86% | 0.053 · 80% |
| **BARASPESHA-GO, bias-aware interval** | 0.030 · 98% | 0.031 · 99% | 0.041 · 96% | 0.033 · 98% | 0.052 · 98% |
| BARASPESHA-GO, Wald interval | 0.030 · 96% | 0.031 · 96% | 0.041 · 93% | 0.033 · 95% | 0.052 · 91% |

Without the simulator, weighting fails: the response is a steep sigmoid and the adopting wells sit near the coast,
where controls are few. Without the weights, the simulator fails: calibration absorbs the parametric error but not the
structural one, and its model-based intervals cover about half the time. The calibrated simulator augmented with
generic kernel weights is accurate but over-confident. BARASPESHA-GO is within 7% of its RMSE everywhere, 14% better
under structural error, and its bias-aware intervals cover 96–99% in all scenarios.

**Goal-oriented choice of the measured wells (`baraspesha_design.json`, part C).** RMSE of ψ from BARASPESHA-GO when
only some control wells are measured; 300 well fields per scenario.

| Design | S1: 40 wells | S1: 80 | S1: 120 | S3: 40 wells | S3: 80 | S3: 120 |
|---|---|---|---|---|---|---|
| Random | 0.195 | 0.055 | 0.046 | 0.216 | 0.084 | 0.076 |
| Space-filling (maximin) | 0.109 | 0.056 | 0.041 | 0.135 | 0.077 | 0.061 |
| Matching to the treated wells | 0.052 | 0.036 | 0.031 | 0.075 | 0.052 | 0.048 |
| Calibration-optimal (D) | 0.047 | 0.035 | 0.031 | 0.088 | 0.052 | 0.048 |
| **Goal-oriented (Proposition O)** | 0.040 | 0.031 | 0.030 | 0.062 | 0.047 | 0.047 |
| All control wells measured | 0.030 | 0.030 | 0.030 | 0.041 | 0.041 | 0.041 |

The goal-oriented design is the most accurate at every budget in both scenarios. With 80 wells it practically reaches
the accuracy of measuring all of about 280 controls.

## Files

| File | What it does |
|---|---|
| `baraspesha_model.py` | Strack physics, truth and simulator, sensitivities, data generation, regularized Levenberg–Marquardt calibration, kernel ridge, balancing weights, Riesz-loss cross-validation, bias-aware critical values |
| `baraspesha_est.py` | The eight estimators of ψ, the physics kernel, the physics noise model and the BARASPESHA estimator |
| `baraspesha_design.py` | The five designs (random, space-filling, matching, calibration-optimal, goal-oriented), batch-sequential with recalibration |
| `baraspesha_exp.py` | Part A (exactness checks), part B (Monte Carlo), part C (designs) |
| `baraspesha_figs.py` | `figB1_estimators.png` and `figB2_design.png` |
| `baraspesha.json`, `baraspesha_design.json` | Results used by review 40 |
| `run_all.sh` | Runs every stage in order |

## Run

```
bash experiments/baraspesha_go/run_all.sh
```

The whole script takes about 10 minutes on 4 cores (Python 3, NumPy, SciPy, Matplotlib).

## Limitations

* One family of physics, the steady sharp-interface solution. A transient variable-density simulator has costlier
  sensitivities (adjoint solves) but the same theory.
* The scales of the physics class (three calibration standard errors, τ = 0.35, B = 0.15) come from hydrogeological
  judgement, and the intervals are honest only for discrepancies inside the class. A missing process with another
  signature (upconing, a leaky layer) needs its own sensitivity or a larger B.
* Adoption depends only on what the analyst measures (no hidden confounding), and wells do not interfere.
* The design serves one goal; several goals need a joint criterion.
* The test is a simulation with known truth. Applying it to Fushë-Kuqe needs pumping records, pumping-test
  conductivities, chloride at a chosen subset of wells and the regional simulator.
