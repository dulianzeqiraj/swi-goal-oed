# BASHKIMI-GO: which institution's well records to merge, before any record is shared

Innovation of literature review 55, "Is merging worth it? Valuing, privately, the well records of other institutions
for the effect of pumping on chloride". *Bashkimi* is Albanian for the merger. Anchor paper: Fawkes, Ter-Minassian,
Ivanova, Shalit & Holmes, "Is merging worth it? Securely evaluating the information gain for causal dataset
acquisition", AISTATS 2025 (PMLR 258).

**Question.** The effect of high summer pumping on the seasonal change of chloride at a Fushë-Kuqe well is a
conditional average treatment effect (CATE): it grows near the saltwater toe. The records are held by five
institutions (water utility = host, monitoring agency, private irrigators, coastal hotels, research campaign) that
cannot simply pool them. Which merge should the utility make first, to decide which of 40 target wells may keep
pumping hard, and is it worth its cost? Can that be computed without anybody revealing a record?

**Truth generator.** The Fushë-Kuqe sector model with 12 zonal log-conductivities and a finer Gaussian field (as in
`../vendi_go`); effect of pumping tau(x) = gam DQ [A^-1]_xx exp(-(h_n(x) - h_c)/lam) with uncertain chemistry
(gam, lam, drift); covariates distance to the sea and pumping-test log T; treatment probability set by the holder.

**Theory (section 9 of the review).**
1. *Proposition B1.* In a Gaussian linear model every merge criterion (EIG of all parameters, of the CATE
   parameters, of the target CATEs, and the decision value) needs only the candidate's weighted Gram matrix.
2. *Proposition B2.* The CATE information is a Schur complement (a parallel sum of the treated and untreated Gram
   matrices when the features coincide); it is concave and positively homogeneous, so merging is superadditive.
3. *Proposition B3.* Closed-form decision value: the expected fall of the Bayes risk of the cap / allow decision,
   computed by Gauss-Hermite quadrature from the preposterior variances; non-negative, Blackwell-monotone, in loss units.
4. *Proposition B4.* With each record's whitened information clipped at lambda, one record moves every target's
   preposterior variance by at most kappa (v0 - u), kappa = lambda / (1 + lambda); this bounds the sensitivity of the
   value, and clipping never overstates it.

## Files

- `bashkimi.py` — truth generator, the physics-informed (and, with `BASH_MODEL=poly`, polynomial) Bayesian CATE model
  with a calibrated discrepancy field (87-node predictive process), the four criteria, realised gains (30 outcome
  draws per merge), the three privacy mechanisms (`calibrate`, `run 200`, `mpc 40`).
- `mpc.py` — two-party additive secret sharing in Z_2^64 (20 fractional bits): Beaver products, Newton-Schulz inverse,
  Newton inverse square root, a 43-term Chebyshev series of phi + z Phi; truncation and comparisons dealer-assisted.
- `bashkimi_summary.py` → `res/bashkimi_summary.json` (and `_poly`); `bashkimi_figs.py` → `res/figB1_bashkimi.png`.
- `run_all.sh` — the whole pipeline (about 3 minutes on four cores).

## Results (200 aquifers; gains in loss units, expected over 30 outcome draws)

| Criterion | Physics model: gain | minus BASHKIMI-GO ± 95% | P(best) | Polynomial model: gain | minus BASHKIMI-GO ± 95% | P(best) |
|---|---|---|---|---|---|---|
| Largest dataset | 0.0295 | -0.0068 ± 0.0042 | 0.24 | 0.1260 | -0.0280 ± 0.0074 | 0.19 |
| EIG of all parameters | 0.0352 | -0.0012 ± 0.0038 | 0.28 | 0.1490 | -0.0050 ± 0.0034 | 0.45 |
| EIG of the CATE parameters (anchor) | 0.0373 | +0.0010 ± 0.0044 | 0.28 | 0.1551 | +0.0011 ± 0.0047 | 0.53 |
| Mean EIG of the target CATEs | 0.0339 | -0.0025 ± 0.0036 | 0.28 | 0.1563 | +0.0023 ± 0.0045 | 0.54 |
| **BASHKIMI-GO decision value** | 0.0363 | — | 0.34 | 0.1540 | — | 0.56 |

- Physics first: the host's own records give a mean loss of 0.502 with the physics-informed CATE basis,
  0.711 with the polynomial basis, and 0.542 with the polynomial basis after the best merge chosen with hindsight.
- Go / no-go (physics model): merging only when the value exceeds the cost gives +0.0144 at cost 0.03
  (always merging +0.0063) and +0.0058 at cost 0.06 (always merging -0.0237).
- Overlap: merged CATE information exceeds the sum of the separate ones in every aquifer; the coastal hotels create
  the most (0.45 nats).
- Privacy (clip 0.3, delta 1e-6): DP alone (noisy Gram matrix) agrees with the non-private choice in at most
  33% of aquifers up to eps = 3; MPC with noise on the clipped whitened information agrees in
  76% at eps = 1 (polynomial model) and keeps 97% of the gain at eps = 3 (physics model).
- Secure computation: max |error| 1.4e-04, same choice in 40 of 40 aquifers, about 21 MB and 262 Beaver rounds per candidate.
