# ZBULIMI-GO: how to explore when several well fields share one coastal head

Innovation of literature review 47, "Reinforcement learning with deep mathematics II: 20 more papers 2020–2026
(Oxford, Caltech, MIT, Harvard)". *Zbulimi* is Albanian for discovery.

**Question.** Review 46 (MESIMI-GO) showed that one well field whose pumping rule reads soil moisture learns its own
effect on the coastal head without deliberate experiments. With several well fields this fails: how should an
operator perturb the wells so that the rule learns how they differ, at the lowest cost and without moving the toe?

**Model.** Monthly state z = (m, r, h, X) as in MESIMI-GO; three well fields with pumping anomalies q = (q₁, q₂, q₃):

    h' = 0.9 h + 0.5 r − β₁ q₁ − β₂ q₂ − β₃ q₃ + 0.1 w_h      (β = (0.25, 0.15, 0.05) unknown; first guess 0.15 each)

Cost per month X² + Σ λᵢ qᵢ² with λ = (0.3, 0.5, 0.8) (a well field far inland is dearer to run off plan). The
learner estimates the head row (a_h, b_r, β) by least squares and plays the certainty-equivalent Riccati rule,
re-solved every 50 months.

**Theory (section 9 of the review, Proposition Z).**
1. *Rank one.* Because the wells act on the state only through βᵀq, Sherman–Morrison gives
   K = −R⁻¹β (e_hᵀPA) / (1 + P_hh βᵀR⁻¹β): every well moves in the fixed proportion d ∝ R⁻¹β.
2. *Blind directions.* Along a certainty-equivalent path the data identify only (a_h, b_r, βᵀd); the p − 1
   directions of β orthogonal to d are never excited, and estimates that the data cannot refute under their own rule
   (a self-confirming set) can stop the learning.
3. *Cost of exploration.* A pumping perturbation e with covariance Σ costs exactly tr(MΣ) per month under the optimal
   rule, M = R + P_hh ββᵀ. For given information V'ΣV = G about the blind directions (V an orthonormal basis of d⊥),
   the cheapest Σ is M⁻¹V N G N VᵀM⁻¹ with N = (VᵀM⁻¹V)⁻¹, and it satisfies βᵀΣβ = 0: the cheapest exploration
   is head-neutral, so in the linear model it moves neither the head nor the toe.
4. *Regret.* With Σ_t = t^(−1/2) Σ*, the regret grows like C√T with C* = 2σ_h tr((N^½ H_V N^½)^½) for the optimal
   head-neutral design and C_iso = 2σ_h √(tr M · tr H_V) ≥ C* for isotropic exploration of every well (H_V the Hessian
   of the average cost in the blind directions). Exploring total pumping (along d) gives no information on the blind
   directions.

## Results (`zbulimi.log`, `zbulimi_theory.log`, `zbulimi_early.log`; 160 runs, 20,000 months, common random numbers)

| Check | Result |
|---|---|
| singular values of the optimal rule | 2.65, 0, 0 (rank one); direction d equals R⁻¹β/‖R⁻¹β‖ |
| exploration-cost identity tr(MΣ) | exact to 5·10⁻¹⁵ (20 random Σ) |
| head-neutrality of the optimal design | βᵀΣ*β / tr Σ* = 10⁻¹⁸ |
| self-confirming estimates | median excess 0.12 per month (19 % of the optimal cost), 90th percentile 0.90 |
| no exploration | regret 215 ± 14; β error stalls at 0.041; excess 0.0065 per month in the second half (linear regret) |
| exploring total pumping | regret 307 ± 18; β error stalls at 0.039 |
| isotropic exploration | regret 138 ± 3; β error 0.018; fitted √T constant 0.895 (predicted 1.072) |
| head-neutral exploration | regret 116 ± 3; β error 0.018; fitted √T constant 0.752 (predicted 0.846) |
| ratio of constants, isotropic / head-neutral | measured 1.19, predicted 1.27; predicted 1.22–1.42 as β is scaled from 0.5 to 3 |
| regret after 226 months (≈ 19 years) | none 78, total pumping 106, isotropic 23, head-neutral 20 |
| early swings without exploration | at month 150 the raw estimate leaves [0.01, 1] in 81 % of runs and the rule's excess cost is 0.79 per month (median) |

Meaning: a multi-well rule that does not explore never learns how its well fields differ, and its least-squares
estimate swings in the blind directions. Perturbing all wells together (the obvious experiment) does not help.
Head-neutral exploration, which shifts pumping between well fields at constant coastal drawdown, learns as much as
isotropic exploration at 16 % less regret, and it is also the safest exploration because it does not move the toe.
The √T constants are overpredicted by 11–16 % (the formula ignores the information supplied by the drift of the
estimates themselves); their ratio is predicted within 6 %.

## Files

| File | What it does |
|---|---|
| `zbulimi.py` | Model, plug-in exploration design, four certainty-equivalent learners and the oracle; writes `zbulimi_results.json`, `zbulimi.log` (about 9 minutes) |
| `zbulimi_theory.py` | Rank one, the cost identity, self-confirming estimates and the sensitivity of the constants; writes `zbulimi_theory.json`, `zbulimi_theory.log` |
| `zbulimi_early.py` | The first 400 months of the non-exploring learner (ill-conditioning in the blind directions); writes `zbulimi_early.json`, `zbulimi_early.log` |
| `zbulimi_figs.py` | Figure `figZ1_exploration.png` (not committed: `*.png` is ignored; run the script) |
| `run_all.sh` | Runs everything (about 10 minutes) |

Caveats: linear, monthly, one coastal head; the learner knows every equation except the head equation and the noise
level; estimates are clipped to [0.01, 1]; the design is recomputed every 500 months from the current estimate.
Related theory: task-optimal exploration in linear systems (Wagenmaker, Simchowitz & Jamieson, ICML 2021) solves the
general design problem; ZBULIMI-GO adds the rank-one structure of multi-well control, the head-neutrality of the
optimal design, closed-form constants and the hydrological reading.
