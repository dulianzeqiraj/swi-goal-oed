# KURSIM-GO: frugal simulation, inference and safe policy design for pumping effects on chloride

Innovation of review 36, "Specifying the causal effect and building the observational model: 20 theorem-level
papers" (2020–2026). *Kursim* is Albanian for thrift, after the frugal parameterization of Evans & Didelez
("Parameterizing and simulating from causal models", *JRSS-B* 86(3), 535–568, 2024,
https://doi.org/10.1093/jrsssb/qkad058).

**The problem.** A marginal structural model (MSM) states the causal effect directly, here
Y | do(a1, a2) ~ N(θ0 + θ1 a1 + θ2 a2, s²) for the log chloride Y after two pumping seasons. The observational law
that matches it is hard to write down when a time-varying confounder is itself affected by earlier treatment:
here a chloride alarm L2 is raised by season-1 pumping and lowers season-2 pumping. A standard regression or
parametric g-formula with a linear outcome model then cannot contain the null θ = 0 (the g-null paradox).

**The model.** The frugal parameterization splits the joint law into three variation-independent pieces: the
past p(L1, A1, L2, A2), the causal margin p*(y | do(a)), and a copula between Y and the Rosenblatt scores of
the confounders. KURSIM-GO uses a Gaussian copula with W1 = L1 and W2 a truncated normal on the side of the
threshold t = Φ⁻¹(1 − π) that the alarm occupies:

    Y = θ0 + θ1 A1 + θ2 A2 + s (ρ1 W1 + ρ2 W2 + √(1 − ρ1² − ρ2²) ε).

The review proves four results for it (section 11):

* Theorem A: under do(a1, a2) the law of Y is exactly the MSM, for every past, policy and copula; θ = 0 gives
  data with no effect at all.
* Proposition B: E[Y | L1, A1, L2, A2] = θ0 + θ1 A1 + θ2 A2 + s ρ1 L1 + s ρ2 λ(L2, t), with the inverse Mills
  ratios λ(1, t) = φ(t)/π and λ(0, t) = −φ(t)/(1 − π).
* Theorem C: the joint density of the alarm and the outcome is
  p(l2, y | l1, a1, a2) = τ⁻¹ φ(r/τ) Φ(σ(l2)(μw − t)/σw), so maximum likelihood needs no model of the
  managers' decisions.
* Proposition D: the season-2 policy changes neither θ nor the copula, so the information about θ2 can be
  optimized over policies under a cap on the risk P(alarm and high pumping).

## Results

Monte Carlo, 1000 data sets per scenario (`kursim_mc.json`):

| Scenario | Estimator | bias θ1 / θ2 | RMSE θ1 / θ2 | 95% coverage | rejection of θ = 0 |
|---|---|---|---|---|---|
| effect, n = 1500 | OLS with the alarm | −0.141 / +0.003 | 0.143 / 0.025 | 0.00 / 0.95 | — |
| | OLS without the alarm | −0.005 / −0.158 | 0.026 / 0.160 | 0.95 / 0.00 | — |
| | g-formula (linear Y) | −0.006 / +0.003 | 0.026 / 0.025 | 0.94 / 0.95 | — |
| | IPW | +0.000 / +0.002 | 0.031 / 0.029 | 0.97 / 0.98 | — |
| | doubly robust (ICE-AIPW) | −0.000 / +0.002 | 0.031 / 0.028 | 0.94 / 0.95 | — |
| | **frugal MLE** | −0.000 / +0.001 | **0.026 / 0.024** | 0.96 / 0.95 | — |
| null, strong feedback, n = 6000 | OLS without the alarm | | | | 0.53 / 1.00 |
| | g-formula (linear Y) | −0.022 / +0.002 | | 0.63 / 0.96 | **0.37** / 0.04 |
| | IPW | | 0.016 / 0.017 | | 0.03 / 0.02 |
| | doubly robust | | 0.018 / 0.016 | | 0.05 / 0.04 |
| | **frugal MLE** | | **0.014 / 0.012** | 0.96 / 0.96 | 0.04 / 0.04 |

With a Student-t conditional for the outcome score (4 d.f., recalibrated so that the causal margin stays exact), where
the Gaussian frugal likelihood is misspecified, the frugal MLE still had bias −0.001 / −0.002, RMSE 0.025 / 0.024 and
coverage 0.95 / 0.96 at n = 1500.

Exactness (`kursim_check.json`, one million wells per regime): the causal means of the four regimes match the MSM to
within 1.7 standard errors and the standard deviations are 0.500 to within 0.001, for the baseline past, the
strong-feedback past and the Student-t copula; the residual of Proposition B has regression coefficients within 2.4
standard errors of zero on (1, A1, A2, L1, L2).

Policy design on a 11 × 15 grid of (b0, b3), 200 000 simulated well-seasons per policy (`kursim_design.json`),
n · Var(θ̂2) with production P(A2 = 1) ≥ 0.40:

| cap on P(alarm and high pumping) | frugal MLE | doubly robust | IPW |
|---|---|---|---|
| current policy (risk 0.111) | 0.86 | 1.21 | 1.72 |
| 0.05 | 1.18 | 2.20 | 3.13 |
| 0.02 | 1.34 | 3.97 | 5.81 |
| 0.01 | 1.44 | 9.39 | 14.62 |

Cutting the risk from 11% to 2% costs the frugal MLE a factor of 1.6 in variance and IPW a factor of 3.4; at a
1% cap IPW needs about 10 times as many well-seasons as the frugal MLE for the same precision.

## Files

| File | What it does |
|---|---|
| `kursim_model.py` | The frugal model: simulation (Gaussian or Student-t copula, observational or under intervention), the exact regression of Proposition B, and the log-likelihood of Theorem C. |
| `kursim_est.py` | Six estimators: OLS with and without the alarm, parametric g-formula (bootstrap SE), IPW with stabilized weights (sandwich SE), doubly robust iterated conditional expectations (influence-function SE) and the frugal MLE (observed-information SE). |
| `kursim_check.py` | Exactness checks of the causal margin (Theorem A) and of the observational regression (Proposition B); writes `kursim_check.json`. |
| `kursim_exp.py` | Monte Carlo study, seven scenario–size pairs × 1000 data sets; writes `kursim_mc.json` (about 8 minutes on 4 cores; `python3 kursim_exp.py effect_tcopula` reruns one scenario). |
| `kursim_design.py` | Asymptotic variances over the policy grid; writes `kursim_design.json` (under 1 minute on 4 cores). |
| `kursim_figs.py` | Figures `figK1_estimators.png` and `figK2_design.png`. |
| `run_all.sh` | Runs every stage. |

## Run

```bash
pip install numpy scipy matplotlib
bash run_all.sh
```

## Limitations

The model has two seasons, one binary alarm and binary pumping; the copula is Gaussian with fixed form, tested
against one misspecification (a Student-t conditional). The design variances are asymptotic (expected information and influence
functions at the true parameters), evaluated on a grid; finite-sample variances at extreme policies, where IPW
weights explode, will be worse than these figures. The numbers are synthetic and are not calibrated to
Fushë-Kuqe wells.
