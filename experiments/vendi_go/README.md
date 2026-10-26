# VENDI-GO: where to pilot-test and where to build managed-aquifer-recharge wells

Innovation of literature review 53, "Bandits and the value of information for siting managed aquifer recharge:
which pilot tests to make, when to stop and where to build". *Vendi* is Albanian for the place.

**Question.** Two supply wells of the Fushë-Kuqe sector model, A1 (A) and P10 (B), are pumped so that each would be
intruded (head below h_c = 1 m) with probability 1/2. Three MAR wells (design rate 5 000 m³/d, at least 6 km apart
in northing) are to be built. The aquifer is uncertain, the injectivity of a well is unknown until a pilot injection
test is made, every test costs money but informs other sites, and the future mean recharge is uncertain whatever one
measures. Which sites should be tested, in what order, when should testing stop, and where should the wells be built?

**Theory (section 9 of the review).**
1. *Proposition V1 (reciprocity).* The steady flow matrix is symmetric, so the head rise at supply well w per unit
   recharge at x equals the head rise at x per unit pumping change at w: a pilot test read at the supply wells measures
   the adjoint g_w(x) that ranks the site, and stopping the pumping of A and B (Stage 0) measures it at every existing
   well without drilling.
2. *Proposition V2 (Gaussian preposterior).* Under the linearised Gaussian belief (12 zonal log-conductivities plus
   approximation errors from 2 500 joint draws of zones and a sub-zonal field), the posterior covariance after a pilot
   test does not depend on its outcome, and the value of the test for the minimum posterior risk over designs of
   three wells is a three-dimensional Gaussian integral (45 Gauss–Hermite nodes); it vanishes when no outcome changes
   the best design.
3. *The function.* Stage 0; plan the best three-well design among tested and shortlisted untested sites (untested
   sites carry their unknown injectivity); test the site with the largest knowledge gradient while it exceeds
   kappa = cost of a test / loss if a supply well is intruded (0.01); then confirm the untested members of the plan;
   build only at tested sites.

**Test.** 200 prior truths (12 zones + sub-zonal Gaussian log-T field, sd 0.35, range 2 km; injectivity
c = c_ref (T/T_ref) exp(eta), sd(eta) = 0.5; future recharge (1 + xi) R, sd(xi) = 0.08), 226 candidate sites on a 1 km
lattice, 380 364 admissible triples; policies: published, area-adjoint and PRAG-MAR cells, PRAG-MAR on the lattice
(prior and after Stage 0), random tests, Thompson sampling, plan-and-confirm, VENDI-GO with and without Stage 0, and
the oracle (best lattice design for the true aquifer). Risk for a known aquifer is exact (the recharge change enters
linearly); cost J = risk + kappa × tests.

## Files

- `vendi.py` — model, truth generator, belief, Stage 0, pilot tests, knowledge gradient, all policies
  (`python3 vendi.py setup`, `python3 vendi.py run 200`, `python3 vendi.py check`).
- `bvn.py` — vectorised bivariate normal probabilities (port of Genz's algorithm; error 2e-16 against scipy).
- `vendi_summary.py` — paired comparisons, calibration and checks → `res/vendi_summary.json`.
- `vendi_figs.py` — Figure V1 → `res/figV1_vendi.png`.
- `run_all.sh` — the whole pipeline (about 50 minutes on four cores).

## Results (`res/vendi_summary.json`, 200 prior truths, kappa = 0.01)

| Policy | Pilot tests | P(A or B intruded) ± 95% | Cost J | J − J(VENDI-GO) ± 95% |
|---|---|---|---|---|
| No recharge | 0.00 | 0.609 ± 0.049 | 0.609 | +0.400 ± 0.041 |
| Published MAR cells | 3.00 | 0.593 ± 0.049 | 0.623 | +0.414 ± 0.040 |
| Area adjoint | 3.00 | 0.467 ± 0.051 | 0.497 | +0.288 ± 0.035 |
| PRAG-MAR cells | 3.00 | 0.250 ± 0.045 | 0.280 | +0.071 ± 0.020 |
| PRAG-MAR on the lattice | 3.00 | 0.228 ± 0.044 | 0.258 | +0.049 ± 0.015 |
| PRAG-MAR after Stage 0 | 3.00 | 0.213 ± 0.044 | 0.243 | +0.034 ± 0.013 |
| Random tests | 6.00 | 0.355 ± 0.050 | 0.415 | +0.206 ± 0.028 |
| Thompson sampling | 11.37 | 0.180 ± 0.042 | 0.293 | +0.085 ± 0.011 |
| Plan and confirm | 4.47 | 0.167 ± 0.040 | 0.212 | +0.003 ± 0.005 |
| VENDI-GO without Stage 0 | 5.53 | 0.172 ± 0.040 | 0.228 | +0.019 ± 0.007 |
| **VENDI-GO** | 4.96 | 0.159 ± 0.040 | 0.209 | — |
| Oracle (bound) | 0.00 | 0.145 ± 0.038 | 0.145 | -0.064 ± 0.006 |

- VENDI-GO closes 83% of the gap between PRAG-MAR on the lattice and the oracle; its design is within 0.005 of the oracle risk in 66% of the aquifers.
- Against plan-and-confirm (same planning, no value of information) it lowers the risk by 0.008 ± 0.005 with 0.48 more tests; the cost difference (+0.003 ± 0.005) is within the noise.
- Stage 0 (no drilling) lowers the cost by 0.019 ± 0.007; Thompson sampling reaches a similar risk but uses 11.4 tests.
- Calibration: mean posterior risk 0.157, realised 0.159; posterior 0–0.05: predicted 0.009, realised 0.009 (n = 115); posterior 0.05–0.3: predicted 0.125, realised 0.107 (n = 50); posterior 0.3–1: predicted 0.690, realised 0.727 (n = 35).
- Proposition V1 check: max |u − g| = 8.1e-20 (sensitivities up to 1.8e-04); the flow matrix is exactly symmetric.
- The oracle is the best lattice design: off-lattice PRAG-MAR cells beat it in 7.5% of the aquifers.
