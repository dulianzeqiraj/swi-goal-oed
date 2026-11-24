# BURIMI-GO: which regimes and which known stoichiometry identify the hidden hydrochemical processes

Innovation of literature review 49, "Causal generative modelling with very high mathematics: 20 papers 2020–2026
(MIT, Oxford, leading European and North American groups)", which follows the survey of Komanduri, Wu, Wu & Chen
(TMLR 2024). *Burimi* is Albanian for the source.

**Question.** The seven major ions of a coastal well are a mixture of hidden processes (seawater intrusion, carbonate
weathering, cation exchange) linked by a causal model. Pumping, irrigation and clay facies act as interventions, and
the stoichiometric signatures of the processes are partly known. Which combinations identify the processes, their
causal links and, separately, the counterfactual chemistry of a sampled well? And how precisely can it be estimated?

**Model.** Linear latent SCM in a known causal order s (seawater fraction) → W (weathering) → X (reverse exchange),
z = Az + ε with unit baseline noise variances (gauge), observed as x = x₀ + Gz + e with seven ions and diagonal
measurement noise. The columns of G are the signatures (meq/L per unit process; seawater minus fresh water per unit
fraction; calcite with some dolomite; Na uptake by the clays). Regimes are perfect interventions: pumping changes the
variance of s, irrigation cuts W from s, a clay facies cuts X from s and W. Queries: Q1, the chemistry of a sampled
well had its seawater fraction been halved; Q2, the same well without cation exchange, do(X = 0); Q3, the covariance
under an unobserved pumping regime.

**Theory (section 9 of the review, Proposition B).**
1. *Baseline fibre.* The baseline identifies HHᵀ and T (H = G(I − A)⁻¹; Anderson–Rubin row deletion, d ≥ 2n + 1), so
   the model is determined up to G' = HO(I − A'), O orthogonal, A' strictly lower triangular: dimension n(n − 1).
2. *Known signatures.* Each signature known up to scale imposes n − 1 conditions: the fibre has dimension (n − k)(n − 1).
3. *Source regime.* A perfect intervention on a source gives Σ_k − Σ₀ = (σ_k² − 1) h_s h_sᵀ, so the total-effect
   signature h_s and every counterfactual that scales the source, x^cf − x = (α − 1) z_s h_s with z_s = e_sᵀH⁺(x − x₀),
   are identified while the fibre keeps dimension n(n − 1) − (n − 1).
4. *Query identifiability.* A query is locally identified iff its derivative vanishes on the null space of the
   Jacobian of the parameter-to-covariance map; the share ‖J_qN‖/‖J_q‖ measures how far it is from identified.

## Results

| Check (file) | Result |
|---|---|
| fibre dimension, baseline only (`burimi_theory.log`) | 6, 4, 2, 0 with 0, 1, 2, 3 known signatures, = (n − k)(n − 1) at 20 random parameter values for every combination |
| genericity (`burimi_theory.log`) | the fibre of all 16 designs is the same at 20 random parameter values as at the true ones |
| source regime (`burimi_theory.log`) | Σ_pump − Σ₀ is rank one along h_s to 10⁻¹⁶ |
| queries (`burimi.log`) | shares below 10⁻¹⁴ (identified) or above 5·10⁻⁵; Q1 and Q3 identified by a pumping or an irrigation regime alone (fibre 4 or 2); Q2 only by a clay-facies regime or a fully identified model; complete designs: irrigation + clay facies, seawater known + pumping + clay facies, two signatures + clay facies, all three signatures |
| estimation, Q1 (`burimi.log`, 10 data sets per design, 300 baseline + 150 per regime samples) | median relative error 1.0–6.6 % in all six designs; spread over equally good fits 0.095 without regimes, 0.001 with the pumping regime |
| estimation, Q2 | median error 3.8–4.0 times the change where not identified (1.9 with two signatures); 15 % (90th pct 30 %) with seawater known + pumping + clay facies; exactly 0 with all signatures known; 169 % with irrigation + clay facies |
| delta method (`burimi_precision.log`) | predicted Q1 errors 0.037, 0.032, 0.011 against simulated medians 0.028, 0.032, 0.010; Q2 0.30 against median 0.15 / 90th pct 0.30; best Q1 design: two signatures + pumping (0.007) |
| local versus practical identification (`burimi_modes.log`) | irrigation + clay facies: in 4 of 10 data sets the best of six random starts lies in a distant optimum with a five-times-wrong Q2 and a likelihood 0.3–1.2 units higher than the fit started at the truth; at the population level no exact second solution exists, but distant optima have a Kullback–Leibler gap of only 2.6·10⁻³ per sample (< 0.8 log-likelihood units for 300 samples); with all three regimes the gap is at least 0.078 |

Meaning: a known stoichiometric signature is worth as much identification as a regime, and knowing all of them makes
the exchange counterfactual independent of every fitted parameter. A period of different pumping is enough for
seawater counterfactuals whatever else is unknown. Exchange counterfactuals need a clay-facies contrast or known
signatures. Local identification is necessary but not sufficient: compute the delta-method error of the query for
the design at hand, fit from many starts and report every equally good fit.

## Files

| File | What it does |
|---|---|
| `burimi.py` | Model, identifiability of 16 designs (Jacobian rank, query shares) and maximum-likelihood estimation for six designs (Pool(4), one thread per worker); writes `burimi_results.json`, `burimi.log` (about 8 minutes) |
| `burimi_theory.py` | Fibre formula and genericity at random parameters, rank-one source regime; writes `burimi_theory.json`, `burimi_theory.log` |
| `burimi_precision.py` | Delta-method (Fisher information) error of Q1 and Q2 for every design; writes `burimi_precision.json`, `burimi_precision.log` |
| `burimi_modes.py` | Distant optima for the irrigation + clay-facies design and population fits for five designs; writes `burimi_modes.json`, `burimi_modes.log` (about 6 minutes) |
| `burimi_figs.py` | Figure `figB1_identifiability.png` (not committed: `*.png` is ignored; run the script) |
| `run_all.sh` | Runs everything (needs `autograd`) |

Caveats: three processes, linear Gaussian model, known causal order and targets, perfect interventions, abduction
without measurement noise, signatures exactly right when known (a misspecified signature is not tested), simulated
wells. A first run without thread pinning took more than 90 minutes because numpy used several threads per worker; it
was stopped and rerun with one thread per worker (same code and seeds otherwise).
