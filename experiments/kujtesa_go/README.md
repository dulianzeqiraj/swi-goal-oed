# KUJTESA-GO: the slow memory of the clays and deep temporal-difference learning

Innovation of literature review 48, "Deep reinforcement learning with deep mathematics: 20 further papers 2020–2026
(Oxford, Caltech, MIT, Harvard)". *Kujtesa* is Albanian for memory.

**Question.** A neural pumping agent learns its value function by temporal-difference learning with a target network.
The aquifer has a slow memory: salt pushed into the clays leaks back over decades. What does that memory do to deep
TD learning, which part of the value is learned last, does the pumping rule suffer, and what helps?

**Model.** Monthly linear closed loop under the optimal (discounted LQR) rule, state z = (m, h, X, c):

    m' = 0.7 m + 0.5 w_m                      soil-moisture index
    h' = 0.85 h + 0.3 m − 0.3 q + 0.1 w_h     coastal head
    X' = 0.9 X − 0.5 h + 0.1 c + 0.1 w_X      landward toe advance
    c' = 0.995 c + 0.02 X + 0.02 w_c          salt stored in the clays (memory 200 months ≈ 17 years)

Cost X² + 0.5 q² per month, discount γ = 0.99. Closed-loop eigenvalues 0.995 (clay), 0.70 (soil moisture),
0.659 ± 0.224i (head and toe).

**Theory (section 9 of the review, Proposition U).** For fitted value iteration with a function class that contains
the quadratics (the target-network loop of deep Q-learning), with A_K = V Λ V⁻¹ and Ẽ = Vᵀ E V (plain transpose):

1. *Modal law.* ẽᵢⱼ(k) = (γ μᵢ μⱼ)ᵏ ẽᵢⱼ(0); the slow–slow part needs ln(1/ε)/(−ln γμ_s²) ≈ ln(1/ε)/((1−γ) + 2(1−μ_s))
   updates: a slow memory counts twice, as much as the discount.
2. *λ-returns* change the factor to (1−λ)γμᵢμⱼ / (1 − λγμᵢμⱼ).
3. *Physics shaping.* Learning V − Φ with the shaped cost c + γΦ(z') − Φ(z) keeps the fixed point and the rate and
   replaces the initial error by Φ − V (shaping is initialisation; the optimal rule is unchanged).
4. *The rule sees little of the slow error.* The greedy gain has first-order error γ(R + γBᵀP*B)⁻¹ (V⁻¹B)ᵀ Ẽ Λ V⁻¹: the
   slow–slow error enters only through ℓ_sᵀB, the controllability of the slow mode by pumping.
5. *Regression errors accumulate in the slow mode.* ẽ_ss(k+1) = f ẽ_ss(k) + r̃_ss(k), so the slow error is
   1/√(1−f²) (uncorrelated errors) to 1/(1−f) (persistent errors) times the per-update regression error.

## Results (`kujtesa.log`, `kujtesa_policy.log`)

| Check | Result |
|---|---|
| modal law, exact iteration | max deviation of the measured factors from γμᵢμⱼ: 6·10⁻¹⁵ |
| updates to 1 % error | clay × clay 230 (predicted 230); clay × other modes 13; other pairs 7 |
| λ-returns (λ = 0.9) | clay factor 0.980 → 0.832, 25 updates to 1 % |
| exact error of P_cc after 25 / 50 / 100 updates | plain 0.341 / 0.207 / 0.076; λ-returns 0.006 / 0.000 / 0.000; physics shaping 0.064 / 0.039 / 0.014 |
| physics potential (clay memory 0.993 instead of 0.995) | starts with 19 % of the slow error, worth 83 updates |
| value slow, rule fast | greedy gain within 1 % on every state after 7 updates while P_cc is still 48 % wrong; the slow mode's head component is 0.06, its controllability 0.018 against 0.235 for the head–toe pair |
| Riccati Q-iteration | gains within 1 % after 7–8 iterations; tail of the gain on c contracts by 0.9802 = γμ_s² |
| neural, plain (5 seeds) | P_cc error 0.234 / 0.258 / 0.074 / 0.097 after 25 / 50 / 100 / 200 updates; below 10 % from update 89 (exact 87); second-half mean 6.7 % although the whole value matrix is within 0.7 %; slow-mode amplification of regression errors 19 (bounds 5.0–50) |
| neural, λ-returns | 0.175 / 0.025 / 0.006 / 0.006; second-half mean 0.7 %; amplification 2.3 (bounds 1.8–5.9) |
| neural, physics shaping | 0.066 / 0.037 / 0.015 / 0.004; below 10 % from update 4; second-half mean 0.8 %; regression error 8.5 times smaller than plain |

Meaning: a neural pumping agent learns the value of the salt stored in the clays last, after about 230 target
refreshes for 1 % accuracy, whatever the network, and its error there is the noisiest because the slow mode
accumulates regression errors. Its pumping rule is nevertheless right early, because pumping barely reaches the clay
mode, so the slowness hides in the predicted cost. A physics value used as shaping potential, or λ-returns, removes
most of the delay; shaping keeps the optimal rule unchanged even when the physics is wrong.

**First version of the neural test.** `kujtesa_v1_stationary.py` (results in `kujtesa_results_v1_stationary.json`,
`kujtesa_v1_stationary.log`) drew the regression states from twice the stationary spread and used noisy one-step
targets. There the clay term is a few per cent of the value, below the accuracy of the network, and after 200 updates
the clay coefficient was still 63–73 % wrong for all three learners. The current version draws states with standard
deviation 1/√P_ii (each coordinate contributes equally to the value) and uses the expected next state. The first
version also ran slowly because numpy used several threads per process; `kujtesa.py` sets one thread per worker.

## Files

| File | What it does |
|---|---|
| `kujtesa.py` | Part 1 (exact modal law, λ-returns, shaping, Riccati Q-iteration) and part 2 (neural fitted value iteration, 3 learners × 5 seeds on 4 processes); writes `kujtesa_results.json`, `kujtesa.log` (about 7 minutes) |
| `kujtesa_policy.py` | Part (iv): greedy gain against value error, slow-mode eigenvectors and controllability; writes `kujtesa_policy.json`, `kujtesa_policy.log` |
| `kujtesa_figs.py` | Figure `figU1_memory.png` (not committed: `*.png` is ignored; run the script) |
| `kujtesa_v1_stationary.py` | First version of the neural test, kept for the record |
| `run_all.sh` | Runs `kujtesa.py`, `kujtesa_policy.py` and `kujtesa_figs.py` |

Caveats: linear closed loop with four states, quadratic value, exact regression in part 1; a small tanh network,
5 seeds and training states chosen to resolve the slow mode in part 2; the physics potential differs from the truth
only in the clay memory. Related work: error propagation in fitted value iteration (Munos & Szepesvári 2008),
potential-based shaping (Ng, Harada & Russell 1999) and its equivalence to initialisation (Wiewiora 2003).
