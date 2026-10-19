# RRJEDHA-GO: does transfer entropy from pumping to the saltwater toe measure causal information flow?

A well-field operator pumps more in droughts and less when the toe alarm is high. Drought also pushes the
toe inland, so it confounds the link from pumping to the toe.

These scripts ask how many bits of information pumping actually passes to the yearly toe change, and how to
measure that number from operating records.

**Model.** The KRAMERS-GO toe model (`../kramers_go/kramers2.py`) with stochastic recharge (s = 0.30):
- 200 000 wells, 10 years each.
- Each year the operator sees an alarm level R (noisy toe reading, 4 classes) and a drought class D
  (dry / normal / wet).
- The operator chooses high or low pumping A with `logit P(A=1) = b1 (2 A_prev − 1) + bR[R] + bD[D]`.
- The outcome is the toe change ΔX over the year, in 3 classes.
- The toe is deterministic given the recharge path. So each well-year is also run under A = 0 and A = 1 with
  the same recharge ("twin worlds"), which gives the interventional distributions P(ΔX | do(a), R) exactly.

**Quantities** (bits; the report uses millibits):

| Name | Definition | Meaning |
|---|---|---|
| `te_obs` | I(ΔX; A \| R) | Standard transfer entropy given the toe history. |
| `te_cond` | I(ΔX; A \| R, D, A_prev) | Transfer entropy conditioned on the decision log. |
| `te_do` | Σ_r p(r) Σ_a π(a\|r) KL(P(ΔX\|do a, r) ‖ mixture) | Interventional information flow (Ay–Polani type) for the operator's toe rule π(a\|r). This is the estimand. |
| `te_adj` | `te_do` with P(ΔX\|do a, r) from back-door adjustment for (D, A_prev) | Estimator of `te_do` from records. |
| `te_adj_noD` | the same, adjusting for A_prev only | What happens when drought is not recorded. |
| `_bc` suffix | bootstrap bias correction 2θ̂ − mean(θ̂*), with the basic interval | Removes the plug-in bias of the information estimate. |

**PID.** The partial information decomposition of I(ΔX; A, D) is computed with Williams–Beer I_min and with
BROJA (constrained optimization over the null space of the marginal constraints; checked on XOR, AND and
COPY). It is computed for the operator's pumping and for pumping assigned at random.

| File | What it does |
|---|---|
| `rrjedha.py` | Simulator, information measures, back-door estimator, I_min and BROJA PID. |
| `rrjedha_exp.py` | E1: population values and PID. E2: 200 data sets each with 200, 800 and 3 200 wells, with a 200-resample well bootstrap. Writes `rrjedha_results.json`. |
| `rrjedha_rct.py` | E3: a randomized pumping rotation. Pumping is drawn each year from the operator's own rule π(a\|R), independently of drought and of the previous decision. Adds `E3` to the json. |
| `rrjedha_figs.py` | `figR1_rrjedha.png` and `figR2_vleresimi.png`. |

Run, in order (about 2.5 minutes on 4 cores):

```
python3 rrjedha_exp.py
python3 rrjedha_rct.py
python3 rrjedha_figs.py
```

## Main results

**Population values** (millibits per well-year):

| Quantity | Value |
|---|---|
| `te_do` (truth) | 13.0 |
| `te_obs` | 24.9 |
| `te_cond` | 6.8 |
| `te_adj` | 12.5 |
| `te_adj_noD` | 35.9 |

- Transfer entropy overstates the causal flow 1.9-fold.
- Conditioning on the decision log answers a different question.
- Back-door adjustment recovers the estimand.
- Adjusting for the previous decision without drought makes things worse, 2.8-fold.

**PID.** Pumping gets almost no unique information:

| Pumping | I_min unique | BROJA unique |
|---|---|---|
| Operator's | 0.0 | 1.8 |
| Random | 0.0 | 0.2 |

This holds even when pumping is random and has an effect: I(ΔX; A) = 14.8 millibits. PID atoms are not causal
contributions.

**Estimation from records** (bias in millibits / coverage of the 95% bootstrap interval):

| Estimator | 200 wells | 800 wells | 3 200 wells |
|---|---|---|---|
| `te_obs` | 15.4 / 13% | 12.9 / 1% | 12.2 / 0% |
| `te_adj` | 9.6 / 48% | 4.6 / 68% | 1.2 / 89% |
| `te_adj_bc` | 4.1 / 93% | 1.9 / 92% | 0.4 / 96% |
| rotation, `te_obs_bc` | 0.6 / 95% | −0.1 / 93% | −0.1 / 93% |

Under the randomized rotation, standard transfer entropy is itself causal and no drought record is needed.
Its SD at 800 wells is 2.4 millibits, against 5.5 for `te_adj_bc` from observational records.

The report is
`docs/literature/Literature_review_Information_Theory_Causality_2020-2026.docx` (section 9).
