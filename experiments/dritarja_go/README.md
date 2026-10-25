# DRITARJA-GO: how much memory a deep pumping agent needs when it does not see the state

Innovation of literature review 50, "Deep reinforcement learning with deep mathematics II: 20 further papers
2020–2026 (Oxford, Caltech, MIT, Harvard)". *Dritarja* is Albanian for the window.

**Question.** Deep RL agents that do not see their state are given a memory: deep Q-networks stack the last four
frames, recurrent and state-space networks carry a hidden state, transformers attend to a context. A pumping agent
for the coastal aquifer sees only the coastal head and the chloride at a sentinel well; the toe and the salt stored in
the clays are hidden. How long a window, and of what, does it need?

**Model.** The monthly aquifer of KUJTESA-GO (review 48), state z = (m, h, X, c), with partial observation:

    y_h  = h + noise (sd 0.05)                 coastal head
    y_Cl = X + 0.5 c + noise (sd 0.3)          chloride at a sentinel well (toe and clay salt mixed)

Soil moisture, the toe and the clay salt are not measured. Cost X² + 0.5 q² per month (average cost). The toe–clay
loop is unstable without pumping control (largest open-loop eigenvalue 1.0127).

**Theory (section 9 of the review, Proposition D).** The optimal rule is the Kalman filter with the LQ gain, an LTI
controller ξ' = Fξ + Gy, q = Hξ + Dy of order n = 4, impulse response h₀ = D, h_k = H F^(k−1) G.
1. *Past actions close the window.* With det(zI − F) = zⁿ + d₁zⁿ⁻¹ + … + dₙ,
   q_t = −Σ_{k=1..n} d_k q_{t−k} + Σ_{k=0..n−1} N_k y_{t−k}, N_k = Σ_{j≤k} d_j h_{k−j}; N_k = 0 for k ≥ n
   (Cayley–Hamilton, and H F⁻¹ G = D for k = n). Four past pumping rates and four observations are exactly enough.
2. *Observations alone need an infinite window.* Truncating to w observations costs O(ρ_c^(2w)) whenever it
   stabilises (ρ_c the spectral radius of F); the best linear rule for the window costs no more.
3. *Short windows can lose stability* when the open loop is unstable.

## Results

Part A, exact (`dritarja.log`):

| Window | Optimal rule truncated | Best linear rule |
|---|---|---|
| 1 month of observations | unstable | +13.8 % |
| 2 | unstable | +5.7 % |
| 4 (frame stack of a deep Q-network) | unstable | +1.67 % |
| 8 | +8.0 % | +0.61 % |
| 16 | +1.3 % | +0.29 % |
| 32 | +0.29 % | +0.077 % |
| 1 past pumping rate + 2 observations (ARX) | | +0.87 % |
| 2 past rates + 3 observations | | +0.024 % |
| 4 past rates + 4 observations | exact (4·10⁻¹³) | exact |

- The truncated rule first stabilises the aquifer with 7 months; 20 months for 1 % excess, 48 for 0.1 %.
- Decay of the excess between 48 and 128 months: 0.9369 per month against ρ_c² = 0.9391.
- The slowest controller pole (0.969, about 32 months) is the slowest Kalman-filter pole: the time needed to
  separate the clay salt from the toe in the chloride record.
- Sentinel-well scan (κ = weight of clay salt in the chloride, noise sd): the shortest stabilising observation window
  runs from 1 to 48 months and the window for 1 % excess from 4 to 64 months; the ARX window stays at four.

Part B, neural agents (tanh networks 2 × 32, trained by backpropagation through 120-month rollouts of the simulator):

- Stochastic gradients (`dritarja_neural.log`, Adam, batch 512, 2000 steps, Polyak averaging, 2 seeds): with 1, 2
  and 4 months of observations the networks cost 14.7 %, 6.2 % and 2.2 % more than the optimum, close to and never
  below the best linear rule; for all longer windows and all ARX windows they stall at 1.3–1.6 %, the level of the
  gradient noise.
- Full-batch training (`dritarja_saa.log`, L-BFGS on a fixed set of 2048 rollouts, 1000 iterations, one seed):
  observation windows of 1, 2, 4, 8, 16 and 32 months cost 14.7, 6.0, 1.96, 0.92, 0.73 and 0.91 %; ARX windows with
  1, 2 and 4 past pumping rates 1.31, 0.45 and 0.34 %, so two to four past rates beat every observation window.
- Overfitting (`dritarja_saa_check.log`): on their own training rollouts the networks with 16 and 32 months of
  observations, and the ARX network with four rates, score 0.08, 0.69 and 0.13 % below the exactly optimal rule; a
  longer observation window brings more weights (3,169 for 32 months against 1,569 for the four-rate ARX network).

## Files

| File | What it does |
|---|---|
| `dritarja.py` | Part A: optimal LQG rule, truncated and optimised windows, ARX windows, decay rate, sentinel-well scan; writes `dritarja_results.json`, `dritarja.log` (about 2 minutes) |
| `dritarja_neural.py` | Part B: neural agents trained by stochastic gradients through the simulator, paired evaluation; writes `dritarja_neural.json`, `dritarja_neural.log` (about 50 minutes on four cores) |
| `dritarja_saa.py` | Part B2: the same agents trained without gradient noise; writes `dritarja_saa.json`, `dritarja_saa.log` (about 45 minutes) |
| `dritarja_saa_check.py` | In-sample loss of the optimal rule on each fixed training set (overfitting check); writes `dritarja_saa_check.json`, `dritarja_saa_check.log` |
| `dritarja_figs.py` | Figure `figD1_window.png` (not committed: `*.png` is ignored; run the script) |
| `run_all.sh` | Runs everything (needs `autograd`) |

Caveats: linear Gaussian model with four states and one pumping rate, so the optimal rule is linear and the network's
nonlinearity cannot help; one sentinel well; the real toe is nonlinear and a PDE model has many more modes, so the
ARX window grows with the order of a reduced model.
