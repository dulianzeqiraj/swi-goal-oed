# KRAMERS-GO: return-period-safe pumping as a nonequilibrium escape problem

A pumping well below Strack's critical discharge Q_c is stable on average, but a run of dry years can
still push the toe of the saltwater interface to the well. These scripts compute the mean time to
well salinisation as a first-passage (escape) problem of a nonequilibrium Markov process, compare
it with the classical small-noise Kramers rule, and turn it into a safe pumping rate Q_T for a chosen
return period T.

- **Toe model:** Strack (1976) single-potential solution on the coast–well axis, X = x_toe/d, with
  F(X; λ) = X + (λ/2) ln((1−X)/(1+X)), μ = K δ B²/(2 q0 d) and λ = Q/(π q0 d). The toe relaxes toward
  equilibrium with time scale τ = 2 yr. Well at d = 2 km; K = 100 m/d, q0 = 1.5 m²/d, B = 30 m,
  δ = 0.025.
- **Recharge forcing:** the regional flow is scaled by a lognormal factor r = exp(ε − s²/2) with mean 1,
  where ε is an Ornstein–Uhlenbeck process with sd s = 0.2 and correlation time θ = 0.5 yr. The noise
  is coloured and multiplicative, and the pair (X, ε) has no detailed balance.
- **Escape:** the toe reaches the well (X ≥ 0.98). The mean first-passage time T(X, ε) solves the
  backward Kolmogorov equation A ∂_X T − (ε/θ) ∂_ε T + (s²/θ) ∂²_ε T = −1, discretised with upwind
  differences and solved with a sparse direct solver.

Requirements: Python 3 with NumPy, SciPy and matplotlib.

| File | What it does |
|---|---|
| `kramers2.py` | Model; stable and unstable toe positions; 2D Kolmogorov solver; 1D white-noise (Stratonovich) reduction; small-noise Kramers rule; Euler–Maruyama simulation with a censored exponential estimate of the mean escape time. |
| `kramers_exp.py` | E1: escape time vs Q/Q_c from simulation (2 000 paths, horizon 6 000 yr), the 2D solution (720 × 481 grid), the 1D reduction and the Kramers rule. E2: safe pumping Q_T for T = 10…500 yr. E3: Q_T under 60 prior draws of K (CV 30%) and q0 (CV 20%). E4: elasticities of Q_c and Q_100 to s, θ, τ, K and q0 (±20%). Writes `kramers_results.json`. |
| `kramers_figs.py` | The two figures of the report (`figR1_escape.png`, `figR2_safe.png`). |

## Run

```bash
python3 kramers_exp.py   # ~11 min on 4 cores
python3 kramers_figs.py
```

## Main numbers

Mean time to salinisation [yr]:

| Q/Q_c | Simulation | KRAMERS-GO (2D) | 1D reduction | Kramers rule |
|---|---|---|---|---|
| 0.65 | 5 609 (66% of paths escaped) | 4 855 | 23 347 | 469 749 |
| 0.70 | 1 290 | 1 200 | 2 775 | 54 701 |
| 0.75 | 386 | 360 | 512 | 7 966 |
| 0.80 | 132 | 132 | 142 | 1 482 |
| 0.85 | 60 | 59 | 55 | 363 |
| 0.90 | 31 | 31 | 27 | 123 |
| 0.95 | 18 | 18 | 15 | 64 |

- The 2D solution agrees with simulation within 8% wherever at least 99% of paths escape. The
  small-noise Kramers rule overestimates the time 3.7 to 84 times, because escape is driven by rare,
  long dry spells (coloured, multiplicative noise), not by small Gaussian kicks.
- Safe pumping at nominal parameters (Q_c = 3 651 m³/d): Q_50 = 0.86 Q_c and Q_100 = 0.82 Q_c. Under
  the prior on K and q0, Q_100/Q_c spans 0.62–0.89 (10–90%) and Q_100 spans 1 004–5 050 m³/d.
- Elasticities of Q_100: s −0.40, θ −0.10, τ +0.17, K −1.20, q0 +2.29. Q_c itself does not depend on
  s, θ or τ, so a static calibration cannot set a return-period-safe pumping rate.

The report is `docs/literature/Kerkim_artikujsh_Fizika_Statistikore_Jo-ekuiliber_2020-2026.docx`
(section 10).
