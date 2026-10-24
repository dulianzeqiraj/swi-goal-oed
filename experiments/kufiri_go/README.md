# KUFIRI-GO: a causal, horizon-resolved budget of every boundary and initial condition

Innovation of literature review 45, "All the boundary and initial conditions of the coastal aquifer system". *Kufiri* is
Albanian for the boundary.

**Question.** A coastal-aquifer forecast is driven by many boundary processes: sea level (interannual anomaly, storm
surge, sea-level rise of uncertain rate), the atmosphere (rain, temperature, a drying and a warming trend of uncertain
rate) filtered by soil moisture into recharge, a river with a Robin exchange, pumping, and the initial state (head,
aquitard legacy, toe position). Which of them controls the forecast at 1, 5 and 20 years? Which can be learned, which
must be lived with, and which can be controlled? The causal graph matters: drought lowers recharge and, under
current practice, raises pumping, so two boundary paths reinforce each other.

**Model.** Linear 1-D coastal aquifer (5 km, T = 1000 m²/d, S_y = 0.1, three aquitard rates), soil-moisture filter
(τ = 0.25 yr, recharge fraction 0.35), river at 3 km (stage driven by soil moisture plus noise), pumping at 1.5 km,
Q = Q_ε + k·(−m) with m the soil-moisture index, toe advance dX/dt = (−γ h(0.5 km) − X)/τ_X with γ = 1000 m/m and
τ_X = 8 yr. Every source is an Ornstein–Uhlenbeck process or a random rate; the goal variance splits exactly into
source contributions (independent sources, linear system), computed by exact (Van Loan) discretisation.

## Results (`kufiri.log`, `kufiri_regimes.log`)

| Horizon | toe sd | largest shares |
|---|---|---|
| 1 yr | 133 m | initial toe 99% |
| 5 yr | 108 m | initial toe 55%, rain anomaly 42% |
| 20 yr | 143 m | rain anomaly 60%, drying trend 33%, sea-level-rise rate 2.6%; initial state 0.8%; storm surges ≈ 0 |

- Monte Carlo check (3,000 paths, all sources together): 19,683 ± 508 m² against the budget's 20,358 m² at 20 yr.
- Causal paths of the atmosphere at 20 yr (variance, m²): recharge 10,351, pumping response 1,219, river 5, and a
  reinforcing cross term of 7,662: drought acting through recharge and through pumping adds up.
- Pumping as an intervention (variance is quadratic in the response k): status quo k = +500 gives sd 143 m and a mean
  advance of 69 m at 20 yr; do(k = 0) gives 109 m and 40 m; the variance-minimising rule k* ≈ −1,480 (cut pumping as
  soil moisture falls) gives 35 m and −46 m. k* is nearly the same at 5 and 20 years (−1,350 and −1,480).
- Discrete regimes (Monte Carlo, 4,000 paths): emergency pumping in drought gives 110 ± 134 m; restricted pumping in
  drought −33 ± 87 m; restricted in drought and extra pumping in wet periods −9 ± 77 m, with a mean pumping cut of only
  37 m²/yr per metre of coast.
- Soil-moisture sensing error barely matters: with an error of 30%, 61% and 121% of the index spread the toe sd of the
  optimal rule is 34.7, 36.5 and 42.8 m (34.1 m without error).

## Files

| File | What it does |
|---|---|
| `kufiri.py` | Model, exact budget by source and horizon, causal paths, policy curve, Monte Carlo check; `kufiri_results.json`, `kufiri.log` |
| `kufiri_regimes.py` | Monte Carlo of pumping regimes and of the optimal rule with sensing error; `kufiri_regimes.json`, `kufiri_regimes.log` |
| `kufiri_figs.py` | Figure `figK1_budget.png` (not committed: `*.png` is ignored; run the script) |
| `run_all.sh` | Runs everything (about 12 minutes on 4 cores) |

Caveats: linear and one-dimensional; the toe is a lagged linear function of the coastal head, not a transport solution;
parameter values are plausible for an Adriatic alluvial aquifer but not calibrated to Fushë-Kuqe; the optimal rule
minimises variance only (it also lowers the mean advance, at the price of pumping less in dry years).
