# VITET-GO: how many years of logs a pumping agent needs, and what shortens them

Innovation of literature review 52, "The landmark theory of deep reinforcement learning: value learning, policy
optimisation, offline learning and the limits of what data can teach a pumping agent". *Vitet* is Albanian for the
years.

**Question.** A utility wants to train a pumping agent, deep or not, on its logs of head, sentinel chloride and
pumping. How many years of logs does any learner need before its rule is within 1% of the best achievable cost, and
what can the utility change so that fewer years suffice: what the monitoring network records, how the operators pump,
or a small recorded random variation of the pumping (a dither)? The landmark sample-complexity rates of RL are worst
case and grow with the cube of the effective horizon; for clays that remember for 200 months that factor is eight
million. VITET-GO computes the local (instance-dependent) answer for the aquifer.

**Model.** The monthly aquifer of reviews 48, 50 and 51, state z = (m, h, X, c), open-loop unstable. Logged:
y = (h + noise 0.05, X + 0.5 c + noise 0.3) and the pumping q. Operators without private information (the mirror of
review 51 removed): q = −γ K E[z | y, past q] + e (+ d), e unrecorded variation (sd 0.1), d a recorded dither. Cost per
month (X + 0.5 c)² + 0.5 q². Learner: the physical model with 4 (or 8) uncertain parameters, calibrated by likelihood
with the pumping as forcing, and its optimal records-only (LQG) rule.

**Theory (section 9 of the review, Proposition V).**
1. For any stabilising records-only rule, J(π) − J* = average of (q − q*)ᵀ W (q − q*), W = R + BᵀPB (completion of
   squares).
2. *Local floor*: for every learner, N × (worst-case expected excess over a c/√N neighbourhood) ≥ ½ tr(H I⁻¹) as
   N → ∞ (Hájek–Le Cam), with I the Fisher information per month of the logs and H the Hessian of the true cost of the
   plug-in rule; attained by likelihood + plug-in.
3. *Years*: N_ε = tr(H I⁻¹) / (2 ε J*) months; the expected cost after N months with monitoring network m is
   G_N(m) = J*_m + tr(H_m I_m⁻¹) / (2N).
4. *A dither's cost is colour-blind*: for operators at the optimal gain, any recorded dither raises their cost by
   exactly W σ_d², whatever its spectrum; so at a fixed cost its spectrum is free and is chosen to minimise tr(H I⁻¹).

## Results

Part A, exact (`vitet.log`), J* = 0.4270:

| Operators | unrecorded variation | their cost | years for 1 % (4 par.) | 0.1 % | 1 % (8 par.) |
|---|---|---|---|---|---|
| near-optimal (γ = 1) | 0.1 | +1.9 % | 20.9 | 209 | 44.2 |
| timid (γ = 0.4) | 0.1 | +110.0 % | 10.8 | 108 | 18.5 |

- Good operators write uninformative logs; four more physical parameters more than double the years.
- Clay retention 0.95 → 0.998 (memory 20 → 500 months): 19.6 → 21.1 years. The floor of a model-based learner is set
  by information per month, not by the mixing time.
- Monitoring (years for 1 %; expected cost after 10 years G_120): baseline 20.9 (0.4359); operators' toe reading
  logged 10.2 (0.4244); sentinel chloride noise halved 13.7 (0.4246); second sentinel 16.9 (0.4254); head noise
  0.02 21.1 (0.4244); soil-moisture probe 29.8 (0.3122, because J* falls to 0.3032).
- Detuning the operators: γ 0.9 → 18.2 years (+1.2 % cost), 0.8 → 15.7 (+5.5 %), 0.6 → 12.1 (+30 %).
- Dither at 2 % of J*: white 20.64 years, AR(1) φ = 0.98 19.83; goal-oriented and D-optimal both choose φ = 0.98.
  At equal extra cost 5.5 %: detuning to γ = 0.8 gives 15.7 years, a slow dither 18.3.

Part B, Monte Carlo (`vitet_mc.log`, 100 logs per length, likelihood calibration from 0.9 θ*):

| Years of logs | floor | mean excess of the plug-in rule (SE) | ratio | unstable |
|---|---|---|---|---|
| 10 | 2.09 % | 10.74 % (4.15 %) | 5.14 | 13 / 100 |
| 30 | 0.70 % | 1.12 % (0.25 %) | 1.61 | 6 / 100 |
| 100 | 0.21 % | 0.29 % (0.05 %) | 1.37 | 0 / 100 |

The spread of the estimates is 0.8–1.4 times the Cramér–Rao bound. The floor is approached slowly from above.

Part C, deep agents (`vitet_deep.log`, two seeds per length; deployment 256 aquifers × 2,400 months):

| Years of logs | floor | physical model by likelihood, exact rule | neural policy trained in it | deep world model + neural policy |
|---|---|---|---|---|
| 10 | 2.09 % | +1.88 %; +1.61 % | +8.91 %; +5.47 % | +52.0 %; unstable (month 1,917) |
| 30 | 0.70 % | +2.28 %; +1.08 % | +6.60 %; +6.28 % | +16.3 %; +17,823 % |
| 100 | 0.21 % | +0.09 %; +0.21 % | +4.99 %; +6.76 % | +12.1 %; +9.4 % |

The physics learner with its exact rule sits at the floor; a neural policy trained in the same calibrated model stays
5–9 % above the optimum at every length (its own optimisation and approximation error); the deep world-model agent is
45–58 times the floor after 100 years. For deep agents the statistical floor is not what binds.

## Files

- `vitet_monitor.py`: general monitoring networks and records-only operators; Fisher information, cost Hessian and
  years for any network.
- `vitet.py`: part A (writes `vitet_results.json`, `vitet.log`); imports `../pasqyra_go/pasqyra.py`.
- `vitet_mc.py`: part B (writes `vitet_mc.json`, `vitet_mc.log`).
- `vitet_deep.py`: part C, deep agents on logs of 10, 30 and 100 years (writes `vitet_deep.json`, `vitet_deep.log`);
  imports `../pasqyra_go/pasqyra_neural.py`.
- `vitet_figs.py`: Figure 9.1 of the review (`figV1_years.png`, not tracked by git).
- `run_all.sh`: runs everything (numpy, scipy, matplotlib, autograd; parts B and C use four processes).

Limitations: a four-state linear test bed, not the full PDE model; the floor is local and asymptotic and short logs
approach it slowly; deep agents pay approximation and optimisation errors on top; operators here have no private
information (with it, the bias of review 51 adds to the variance computed here).
