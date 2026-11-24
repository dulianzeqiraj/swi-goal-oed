# MJEGULLA-GO: robust filtering of the hidden salinity states of a well field, and the monitoring that serves the decision

Innovation of review 41, "Filtering hidden Markov models under uncertainty: 20 papers for the seawater-intrusion
problem" (2020–2026). *Mjegulla* is Albanian for the fog.

**The problem.** The anchor paper of review 41 (S. N. Cohen, "Uncertainty and filtering of hidden Markov models in
discrete time", Probability, Uncertainty and Quantitative Risk 5, 2020, https://doi.org/10.1186/s41546-020-00046-x)
filters a hidden Markov chain when the parameters of the model are uncertain. Each parameter value is penalized
through its log-likelihood ratio to the maximum-likelihood estimate, and the robust filter is a nonlinear (convex)
expectation, computed recursively in time.

In a coastal well field the hidden chain is the salinity class of every well (fresh, brackish, saline). The
observations are sparse, noisy conductivity measurements. The uncertain parameters are the rates at which the front
advances and retreats. MJEGULLA-GO asks:
* how wide the robust interval of a management goal is, for every choice of the penalty;
* how to compute it for a whole field;
* whether decisions taken on it are safe;
* which wells to measure each season so that the interval of the decision at hand shrinks fastest.

**The model.**
* The field: 40 wells between 0.3 and 3 km from the coast. Half of them pump hard (u = 1). Six municipal wells
  between 0.8 and 2.2 km, which also pump hard, are the targets.
* Hidden state of well i in season t: 0 fresh, 1 brackish, 2 saline. With a_i = α + β u_i − κ (d_i − 1) and
  r_i = ρ − η u_i:
  * a fresh well becomes brackish with probability σ(a_i), with σ the logistic function;
  * a saline well recovers with probability σ(r_i);
  * a brackish well moves up with probability e^a/(1 + e^a + e^r) and down with probability e^r/(1 + e^a + e^r).
* Observation of a measured well: Y = m_X + 0.6 ε, with m = (0, 1, 2).
* Known: κ = 1 per km, η = 0.8, the observation model and the initial distribution (more salt near the coast).
* Unknown: θ = (α, β, ρ). Each simulated field draws its own true values, uniformly in
  [−3.2, −2.0] × [0.8, 2.0] × [−2.8, −1.6].
* Monitoring: 20 seasons. Season 0 is a baseline survey of all wells; after that, 4 wells are measured per season.
  The maximum-likelihood estimate is updated every season.
* Goal M: the expected number of saline municipal wells 4 seasons after the end of monitoring.
* Goal P: the expected number of saline wells at four planned sites (0.9–2.1 km from the coast, hard pumping)
  8 seasons after they are drilled. It depends on θ alone, because the sites have no data.

**The theory (sections 1 and 8 of the review).**
* Proposition 1 (part I): the forward filter and the likelihood. Proposition 5: the likelihood-penalized robust filter
  needs, at each time, only the family of filters and one log-likelihood per parameter value.
* Theorem Q: for the penalty (α_t/k)^γ with γ > 1/2, the robust upper expectation of a smooth goal exceeds the plug-in
  value by (2γ − 1)(A √(k/2)/γ)^{2γ/(2γ − 1)} (1 + o(1)), where A² = aᵀ J⁻¹ a, a is the gradient of the goal and J the
  observed information.
  * γ → ∞ (the hard penalty) gives the half-width A √(2k); γ = 1 gives (k/2) A².
  * Corollary: a design step that compares candidate measurements by the predicted width chooses the same set for
    every penalty, the c-optimal set for the goal.
  * With the hard penalty and k = χ²₁(0.95)/2 = 1.92 the interval is the profile-likelihood interval of the goal;
    k = χ²₃(0.95)/2 = 3.91 gives intervals that are valid for all goals at once.
* Proposition R: given θ, the wells are independent chains. The filter of the field is the product of the well filters
  and its log-likelihood the sum of theirs, so the cost grows linearly with the number of wells.
* Proposition S: the expected squared error of the plug-in estimate of goal M splits into a state part (the variance of
  the saline indicators of the municipal wells given the data) and a parameter part aᵀ J⁻¹ a.
  * The goal criterion picks wells greedily, maximizing the sum of the two reductions. The information of one
    measurement is the Fisher information of its predictive density (Proposition 8). For goal P the state part is
    zero, and the criterion is the greedy c-optimal design.
  * A c-optimal design is often singular (Elfving), which leaves flat ridges in the likelihood. The MJEGULLA rule
    therefore chooses three of the season's four wells by the goal criterion and the fourth by the D criterion
    (largest gain in log det of the information): one defensive measurement that keeps the information nonsingular.

## Results

**Checks (`mjegulla.json`, part A; `mjegulla_summary.json`).**
* Proposition R: three wells filtered as one chain on 27 states against the product of three filters (20 random cases).
  The largest differences are 3.6e-15 in the log-likelihood and 8.9e-16 in the goal.
* Theorem Q, over the 2694 of 4500 fits that lie inside the parameter set Θ: exact half-width over the
  prediction A√(2k), median 0.96 (10–90% range 0.88–1.01). With γ = 1 the
  median is 0.94 (0.72–1.13); with γ = 2 it is 0.95
  (0.74–1.13).
* Corollary: the rank correlation across designs between the mean of A² and the mean width is
  0.98 (goal M) and 1.00 (goal P).
* The robust interval was checked in spot checks against the extremes of the goal over 200,000 random points of the
  likelihood region; they agreed to within 0.005.

**Goal M, saline municipal wells (part B, 300 well fields).**

| Design | Width, k = 1.92 | Coverage | Width, k = 3.91 | Coverage | RMSE of the plug-in | Fits at the edge of Θ | Nearly singular information |
|---|---|---|---|---|---|---|---|
| Round robin | 2.385 | 94% | 3.261 | 99% | 0.702 | 22% | 29% |
| Random | 2.496 | 93% | 3.373 | 99% | 0.764 | 24% | 26% |
| Municipal wells in turn | 2.008 | 97% | 2.783 | 100% | 0.537 | 26% | 100% |
| Most uncertain wells | 2.456 | 95% | 3.327 | 100% | 0.958 | 65% | 73% |
| D-optimal | 2.071 | 93% | 2.941 | 100% | 0.655 | 34% | 38% |
| c-optimal (parameter part only) | 1.882 | 95% | 2.659 | 99% | 0.605 | 56% | 62% |
| Goal criterion only | 1.782 | 96% | 2.524 | 100% | 0.544 | 60% | 70% |
| **MJEGULLA (3 goal + 1 defensive)** | 1.766 | 96% | 2.540 | 100% | 0.551 | 45% | 47% |

**Goal P, saline wells at the planned sites (part B, 300 well fields).**

| Design | Width, k = 1.92 | Coverage | Width, k = 3.91 | Coverage | RMSE of the plug-in | Fits at the edge of Θ | Nearly singular information |
|---|---|---|---|---|---|---|---|
| Round robin | 1.403 | 93% | 1.928 | 99% | 0.386 | 22% | 29% |
| Random | 1.561 | 95% | 2.122 | 99% | 0.445 | 24% | 26% |
| Wells similar to the sites | 1.611 | 94% | 2.184 | 99% | 0.447 | 23% | 100% |
| Most uncertain wells | 1.390 | 96% | 1.893 | 100% | 0.511 | 65% | 73% |
| D-optimal | 1.358 | 93% | 1.879 | 98% | 0.397 | 34% | 38% |
| Goal criterion only | 1.188 | 92% | 1.656 | 98% | 0.343 | 51% | 83% |
| **MJEGULLA (3 goal + 1 defensive)** | 1.215 | 93% | 1.688 | 99% | 0.342 | 48% | 51% |

For goal M, MJEGULLA gives the narrowest intervals: 29% narrower than random monitoring and 15% narrower than D-optimal
monitoring, with 96% coverage. For goal P, the goal criterion alone is narrowest; MJEGULLA is 2% wider and well ahead of
the other designs. Coverage of the goal-specific interval is 93–97% (goal M) and 92–96% (goal P), close to the nominal
95% (the Monte Carlo standard error is about 1.3 points).

The defensive measurement roughly halves the share of fields with nearly singular information. It costs at most 3% in
width, and coverage is unchanged within the Monte Carlo error.

**Decisions (Proposition 7).** Act at the municipal wells if three or more are expected to be saline. Approve the planned
wells if at most one of the four is expected to be saline.

| Design | M: missed actions, robust / plug-in | M: needless actions, robust / plug-in | P: unsafe sites approved, robust / plug-in | P: safe sites approved, robust |
|---|---|---|---|---|
| Round robin | 0.4% / 12.9% | 68.7% / 19.4% | 0.5% / 11.6% | 14.7% |
| Random | 0.4% / 14.3% | 74.0% / 28.6% | 0.0% / 17.7% | 19.6% |
| D-optimal | 0.0% / 7.1% | 58.1% / 20.3% | 1.0% / 14.6% | 17.6% |
| Goal criterion only | 0.0% / 4.8% | 52.2% / 17.4% | 1.0% / 11.6% | 27.5% |
| **MJEGULLA (3 goal + 1 defensive)** | 0.0% / 5.6% | 53.7% / 19.4% | 1.0% / 11.6% | 22.5% |

The robust rules are safe for every design. The price is caution, and monitoring for the goal lowers it.

**Budget (part C, goal P, 150 well fields per budget).** Mean width of the robust interval (coverage):

| Measurements per season | Random | D-optimal | Goal criterion only | MJEGULLA |
|---|---|---|---|---|
| 2 | 1.914 (95%) | 1.675 (93%) | 1.420 (93%) | 1.558 (97%) |
| 4 | 1.513 (95%) | 1.323 (94%) | 1.177 (95%) | 1.200 (96%) |
| 8 | 1.275 (95%) | 1.142 (97%) | 1.039 (95%) | 1.046 (96%) |

MJEGULLA with four measurements per season beats random monitoring with eight. With only two measurements per season,
the defensive measurement takes half the budget.

## Files

| File | What it does |
|---|---|
| `mjegulla_model.py` | The well field, transition and observation models, simulation, the batched forward filter, the two goals, maximum likelihood with observed information, the robust interval over the likelihood region, the finite-penalty robust expectations, Theorem Q and the 27-state check of Proposition R |
| `mjegulla_design.py` | The monitoring designs (round robin, random, municipal or similar wells, most uncertain, D-optimal, c-optimal, MJEGULLA) with the Fisher information of one measurement and the preposterior state variance |
| `mjegulla_exp.py` | Part A (exactness check and one example field), part B (Monte Carlo over 300 fields), part C (budget) |
| `mjegulla_summary.py` | Widths, coverage, decision errors, allocation and the accuracy of Theorem Q -> `mjegulla_summary.json` |
| `mjegulla_figs.py` | `figM1_robust.png` and `figM2_design.png` |
| `mjegulla.json`, `mjegulla_budget.json`, `mjegulla_summary.json` | Results used by review 41 |
| `run_all.sh` | Runs every stage in order |

## Run

```
bash experiments/mjegulla_go/run_all.sh
```

The whole script takes about 17 minutes on 4 cores (Python 3, NumPy, SciPy, Matplotlib).

## Limitations

* Three salinity classes and a Markov chain per well. A physical simulator of the interface would give the transition
  probabilities, and the theory carries over with the simulator's parameters in place of θ.
* Wells are independent given θ. Shared drawdown couples neighbouring wells; the joint chain is then not a product
  (Proposition R fails) and needs particle or factored filters.
* The penalty is the likelihood ratio of a correctly specified family. If the family is wrong, the interval covers the
  best approximation within it, not the truth; structural error needs a wider family or a discrepancy term.
* The robust interval is computed along 160 rays in the metric of the observed information, with the eigenvalues
  floored at 2k/81 (9 is the widest side of Θ), each ray stopped at the boundary of the region or of Θ, and the extremes
  refined by a local pattern search. Without the floor, a search along the axes of a nearly singular information matrix
  runs along the flat ridges and can understate the width by up to a third.
* The χ² calibration of k is asymptotic; a parametric bootstrap of the likelihood ratio would calibrate k for the data at
  hand. With two measurements per season the defensive measurement takes half the budget; its share should then be
  smaller.
* Greedy one-season look-ahead; batch or multi-season designs may do better.
* The test is a simulation with known truth. Applying it to Fushë-Kuqe needs conductivity series at the wells, pumping
  records and the classification thresholds of the agency.
