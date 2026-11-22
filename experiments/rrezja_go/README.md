# RREZJA-GO: a radius of belief instead of a list of beliefs (Fushë-Kuqe stakeholders)

Innovation of literature review 58 (deciding decisively under deep uncertainty II: 20 more papers of 2020–2026 from
Oxford, Caltech, MIT and ETH Zürich). *Rrezja* is Albanian for the radius.

**Idea.** VENDIMI-GO (review 57, `../vendimi_go`) protects five stated beliefs, exponential tilts of the calibrated
chloride ensemble of PUSI-GO along the mixing-zone width and the recharge. RREZJA-GO protects every belief within a
relative-entropy radius ρ of the calibrated ensemble, agreed before the data and updated by Bayes' rule with the common
likelihood: an action (pumping scale, recharge per site) is allowed only if the worst posterior risk over the ball,
plus 1.645 Monte Carlo standard errors, that A1 or P10 exceeds 250 mg/L is at most 10%.

**Propositions (section 9 of the review).**
1. *R1, full ball.* max over KL(q‖p) ≤ ρ of q(F) = klinv₊(p(F), ρ) (binary relative entropy); the full-ball rule is the
   nominal rule with the tighter limit α_ρ, kl(α‖α_ρ) = ρ.
2. *R2, tilt ball.* max over tilts within ρ of P_λ(F) = P(F) + sqrt(2ρ cᵀS⁻¹c) + O(ρ), c = Cov(z, 1_F), S = Cov(z):
   the price of robustness is the radius times the part of failure explained by the drivers (R_{F|z} ≤ 1).
3. *R3, Bayes.* Tilts commute with Bayes' rule; a stated belief's radius after data is about ½λᵀCov(z|y)λ, and the
   robust margin falls when data narrow the drivers, resolve the event, or decouple failure from the drivers.

## Files
- `rrezja.py` → `res/rrezja.json` (about 35 minutes on 4 cores; imports `../vendimi_go/vendimi.py`, which needs
  `../pusi_go/res/ens.npz`, made by `../pusi_go/pusi_run.py`).
- `rrezja_expost.py` → `res/expost.json` (about 1 minute): how often some belief within ρ_env judges the review-57
  choice unsafe after seeing the chloride sample.
- `rrezja_figs.py` → `res/figR1_rrezja.png`.
- `run_all.sh`.

## Results (same 2 000 truths, chloride sample and grid as VENDIMI-GO; α = 10%)
- Radii of the stated beliefs: utility 0, irrigators and hotels 0.412 (ρ_max), municipality 0.095, water agency 0.283,
  environmental groups 0.293 (ρ_env) nats; after the chloride sample, median 0.157, 0.044, 0.244 and 0.137.
- Without data the review-57 choice (net water 2 148 m³/d) exposes beliefs nobody stated at ρ_env to realised risks up
  to 0.119 ± 0.013 (the width pessimist, λ_w = 0.958, also 0.119); the tilt ball at ρ_env keeps all 416 unstated
  beliefs at or below 0.089 for net water 1 281 m³/d; the full ball deadlocks (no pumping, largest recharge).
- After the chloride sample the review-57 choice is safe for the unstated beliefs on average (0.065), but in 20% of
  truths some belief within ρ_env, updated with the same sample, judges it unsafe (worst posterior risk above 10%); the
  tilt ball (8 drivers) guarantees every belief in the ball for net water 3 981 m³/d (5 125 for VENDIMI-GO; 4 466 with
  the two disputed drivers only).
- R² of the failure indicator on the drivers at the review-57 choice: 0.072 (2 drivers), 0.076 (8 drivers); at ρ_env the
  exact tilt-ball margin is 0.071 against 0.216 for the full ball; the first-order formula of R2 understates the exact
  worst case at the stakeholders' radii (0.079 against 0.110).

Limits: beliefs are tilts of one calibrated ensemble (processes outside the model are not covered); the radius is
itself a stated number; a ball is symmetric; the exact worst case is found by a local ascent with an exact projection,
not certified; steady areal model; finite weighted ensemble.
