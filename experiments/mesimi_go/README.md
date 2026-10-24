# MESIMI-GO: learning a pumping rule online, and when exploration comes for free

Innovation of literature review 46, "Reinforcement learning with deep mathematics: 20 papers 2020–2026 (Oxford,
Caltech, MIT, Harvard)". *Mesimi* is Albanian for learning.

**Question.** A well-field operator must set the monthly pumping q without knowing β, the response of the coastal
head to pumping. Certainty equivalence (estimate β by least squares, then play the rule that would be optimal if the
estimate were true) is the simplest reinforcement-learning scheme for linear–quadratic control. Its classical weakness
is that a feedback rule makes q collinear with the state, so the data never separate β from the head's own dynamics,
and exploration noise must be injected (regret ~ √T). MESIMI-GO asks when the physics of the aquifer supplies the
exploration for free.

**Model.** Monthly state z = (m, r, h, X): soil-moisture index m (exogenous, drives irrigation demand), recharge r
(m filtered by the unsaturated zone), coastal head h, landward toe advance X.

    m' = 0.8 m + 0.6 w_m
    r' = 0.7 r + 0.3 m
    h' = 0.9 h + 0.5 r − β q + 0.1 w_h        (true β = 0.3, initial guess 0.45)
    X' = 0.95 X − 0.5 h + 0.1 w_X

Cost per month X² + 0.5 q². The learner knows the structure and estimates the head row (a_h, b_r, β) from the
regressors (h, r, q), re-solving the rule every 50 months.

**Theory (section 10 of the review, Proposition M).** The estimate of β is consistent without injected exploration
iff the policy's variation of q orthogonal to the other regressors of the head row (h, r) has positive variance. A
drought-aware rule q = −Kz loads on m, which is excluded from the head row, so m acts as an instrument: the
estimation error decays like t^(−1/2) and the regret of certainty equivalence grows like c ln T with
c = ½ tr(H σ_h² Σ_x⁻¹), H the Hessian of the average cost in the head-row parameters. A head-only rule q = −kh has
zero orthogonal variance; without exploration the estimate stalls and the regret is linear, with exploration ~ √T.

## Results (`mesimi.log`, `mesimi_theory.log`; 160 seeds, T = 20 000 months, common random numbers)

| Check | Result |
|---|---|
| optimal drought-aware rule K* (on m, r, h, X) | (−0.388, −1.275, −1.708, 0.877); average cost 0.875 |
| optimal head-only rule | k* = −5.47; average cost 2.735 |
| orthogonal variance of q in the head row | 0.102 (drought-aware) vs 0 (head-only) |
| regret at T = 20 000, drought-aware, no exploration | 10.0 ± 0.5; log–log slope 0.04 (logarithmic) |
| regret, head-only, no exploration | 901 ± 178; β error stalls at RMSE 0.041; tail excess 0.038 per month (linear) |
| regret, head-only, exploration ∝ t^(−1/4) | 1024 ± 10; log–log slope 0.49 (√T); tail excess 0.029 per month |
| β RMSE, drought-aware, at 10² / 10³ / 10⁴ / 2·10⁴ months | 0.034 / 0.0098 / 0.0031 / 0.0021 (slope −½) |
| constant c = ½ tr(H σ_h² Σ_x⁻¹) | 0.336 (Hessian eigenvalues 0.15, 0.70, 41.5) |
| regret increments from T0 = 104 / 275 / 1075 / 2848 / 9172 to 20 000 | measured 1.73 / 1.41 / 0.95 / 0.66 / 0.24; predicted 1.77 / 1.44 / 0.98 / 0.66 / 0.26 |

Meaning: a pumping rule that also reads the soil-moisture index learns the aquifer's response to pumping on its own,
with no deliberate perturbation of the well field, and pays only about ten months' worth of excess cost over 1 700
years of simulated operation. A rule that reads only the head must perturb the wells, or it can lock onto a wrong β.
The ln T constant is predicted within 2–8 % from the Hessian alone; the absolute regret also contains a burn-in of
about 8 cost units from the first 100 months, which the asymptotic formula does not cover.

## Files

| File | What it does |
|---|---|
| `mesimi.py` | Model, oracles (DARE and bounded head-only search), three certainty-equivalent learners, regret on a log grid, β RMSE; writes `mesimi_results.json`, `mesimi.log` (about 5 minutes) |
| `mesimi_theory.py` | Hessian of the average cost in (a_h, b_r, β) by finite differences, constant c, predicted vs measured increments, tail excess; writes `mesimi_theory.json`, `mesimi_theory.log` |
| `mesimi_figs.py` | Figure `figM1_learning.png` (not committed: `*.png` is ignored; run the script) |
| `run_all.sh` | Runs everything (about 6 minutes) |

Caveats: linear, monthly, one coastal cell; the learner knows the structure of the model and the other rows; β̂ is
clipped to [0.1, 2] and the head-only search keeps k ≥ −6 so that every played rule is stable. The result is the
excluded-instrument mechanism, not a calibrated forecast for a real aquifer. Related theory: Simchowitz & Foster
(2020, √T lower bound for online LQR with unknown A and B), Cassel, Cohen & Koren (2020, log T when one of A or B is
known), and Bastani, Bayati & Khosravi (2021, greedy bandits under covariate diversity).
