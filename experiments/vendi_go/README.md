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
