# PASQYRA-GO: what a deep pumping agent learns from operators who knew more than they wrote down

Innovation of literature review 51, "Deep reinforcement learning at the frontier: 20 further papers 2020–2026 (Oxford,
Caltech, MIT, Harvard)". *Pasqyra* is Albanian for the mirror.

**Question.** A utility has decades of logs of the coastal head, the chloride at a sentinel well and the pumping its
operators chose. The obvious way to get a deep pumping agent is to train it on these logs: clone the operators, or learn
a world model and optimise a policy in it (model-based offline RL), or train a sequence model that writes the next
month's pumping. But the operators also knew things they never wrote down, such as complaints from private wells near
the saltwater toe, and cut pumping when salt was coming. What does a learner see in such logs?

**Model.** The monthly aquifer of reviews 48 and 50, state z = (m, h, X, c), open-loop unstable (largest eigenvalue
1.0127). Logged: y = (h + noise 0.05, X + 0.5 c + noise 0.3) and the pumping q. Private to the operators: s = X + noise
(sd 0.1). Operators: q = −K E[z | y, s, past q] + e (+ d), with e unrecorded variation (sd 0.1) and d a recorded dither
(zero unless stated). Near-optimal operators use the optimal gain K; timid operators 0.4 K. Cost per month
(X + 0.5 c)² + 0.5 q², the salinity of the supply wells' capture zone (recorded through y_Cl) plus pumping deficit.

**Theory (section 9 of the review, Proposition P).**
1. Without private information the logged predictor of y_{t+1} is the interventional one, for every operator rule.
2. *Mirror bias*: with it, the coefficient of q_t in the regression of y_{t+1} on the logged past is
   C B − C A P_Δ Kᵀ / (K P_Δ Kᵀ + sd_e²), P_Δ the covariance of the operators' information advantage.
3. *Observational equivalence*: an aquifer' (the innovations form of the logs, order 8) with operators' who use only
   the logs generates exactly the same law of the logs, but in it pumping has the wrong effect; no estimator using the
   logs alone can be consistent in both worlds.
4. *Instrument*: with a recorded dither, the prediction errors of the true model are uncorrelated with the dither at
   every lag; these moments identify the response to pumping, the likelihood the rest.
5. *Mirror test*: for a fixed world model, E[eps_{t+1} d_t] = sd_d² (true one-step effect − model's one-step effect);
   the test's power depends on the dither energy N sd_d².

## Results

Part A, exact (`pasqyra.log`), relative to the best rule that uses the logs alone, J* = 0.4270:

- Mirror bias: with near-optimal operators the logs say one extra unit of pumping changes next month's chloride by
  −0.462 (true 0; formula −0.462); the private reading drives 39 % of the pumping the logs cannot explain.
- Observational equivalence: aquifer' (order 8) and operators' who use only the logs reproduce all autocovariances of
  the logs to 3·10⁻¹⁶, but in aquifer' a sustained extra unit of pumping lowers the chloride (−1.45 after 60 months)
  where the true aquifer raises it (+22.9).

| Learner trained on the logs | Near-optimal operators (+0.3 %) | believed | Timid operators (+108.6 %) | believed |
|---|---|---|---|---|
| Physical model, 4 parameters | +0.1 % | −2.9 % | +0.0 % | −0.6 % |
| Physical model, 8 parameters | +0.1 % | −3.1 % | +0.0 % | −0.9 % |
| Black-box 4-state model (20 parameters) | unstable | −84.0 % | unstable | +55.0 % |
| Black-box ARX, 32 lags | unstable | −77.1 % | unstable | +61.4 % |
| World model of unlimited capacity | +2894 % | −76.2 % | +460.5 % | +83.7 % |
| Clone, unlimited window | +0.1 % | | +107.7 % | |
| Clone, 4 past rates + 5 observations | +20.5 % | | +195.7 % | |

Without private information every model-based learner is exact (+0.0 %).
- Behaviour-regularised offline RL in the world model of the logs: best +0.1 % (near-optimal operators) and +107.7 %
  (timid), never better than the operators.
- Recorded dither (sd 0.05 or 0.2): the physical model calibrated by dither moments is exact (parameter error 10⁻¹⁶);
  the black-box model needs moments + likelihood (+0.0 %; moments alone +106.5 %, because pumping never excites the
  soil-moisture mode).

Part B (mirror test) and part C (deep agents): see `pasqyra_dither.log` and `pasqyra_neural.log`.

## Files

| File | What it does |
|---|---|
| `pasqyra.py` | Part A, exact (population limits): mirror bias against formula (ii); the ladder of learners (physical models with 4 and 8 parameters, black-box 4-state model, ARX models, world model of unlimited capacity, clones) for near-optimal and timid operators, with and without private information; observational equivalence; behaviour-regularised offline RL; the dither as instrument; scan over private information. Writes `pasqyra_results.json`, `pasqyra.log` (about 4 minutes) |
| `pasqyra_dither.py` | Part B, the mirror test: a world model trained on long logs is tested on 5–30 years with a recorded dither; rejection rates (500 test periods per cell), and the extra cost of the dither. Writes `pasqyra_dither.json`, `pasqyra_dither.log` |
| `pasqyra_neural.py` | Part C, deep agents on 12,000 months of simulated logs: deep world model + neural policy trained through it, deep clones, and the remedy (physical model calibrated by dither moments + neural policy); deployment paired with the optimal rule. Writes `pasqyra_neural.json`, `pasqyra_neural.log` (about 50 minutes on four cores; needs `autograd`) |
| `pasqyra_figs.py` | Figure `figP1_mirror.png` (not committed: `*.png` is ignored; run the script) |
| `run_all.sh` | Runs everything |

Caveats: linear Gaussian model with four states, one pumping rate, one private signal and stationary operators; part A
is the limit of unlimited logs and part C uses two seeds and one log length; real operators know many things, some of
which also move the outcome directly; the real toe is nonlinear.
