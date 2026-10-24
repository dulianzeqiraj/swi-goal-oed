# FILLIMI-GO: when does the initial condition stop mattering, and what does memory do to that?

Innovation of literature review 44, "Boundary and initial conditions: 30 papers 2020–2026 (Oxford, Caltech,
Princeton, Berkeley, MIT)". *Fillimi* is Albanian for the beginning.

**Question.** A forecast of a linear(ised) dissipative system has two sources of uncertainty: the initial state and the
boundary forcing. Lorenz called them predictability of the first and second kind. The handover time t* is when the
boundary part of the goal variance overtakes the initial part. Without memory the initial part decays exponentially and
t* grows only like the logarithm of the variance ratio. FILLIMI-GO asks what a completely monotone memory (aquitards,
clay lenses, immobile zones) does to t*, and how the position of the goal relative to a fixed (Dirichlet) boundary
changes the answer.

**Theory (section 10 of the review, Theorem F, and Proposition G).** For a system that is self-adjoint in the storage-weighted inner product
(diffusion with symmetric exchange to storage compartments, Dirichlet/Neumann/Robin boundaries) and a prior that is a
function of the operator, P0 = φ(M):
1. the initial-condition variance of any linear goal is completely monotone in time, V_IC(t) = ∫ φ(λ) e^{-2λt} dν_g(λ);
2. it is never below the exponential at the goal-weighted mean rate λ̄ (Jensen), so t* ≥ ln(V_IC(0)/V_BC(∞)) / (2λ̄);
3. if the goal spectral measure has density c λ^{β-1} near zero, V_IC(t) ~ c Γ(β) (2t)^{-β}: algebraic, not exponential;
4. boundary screening: for a goal in the mobile domain held by a Dirichlet boundary at relaxation rate λ0, the slow
   storage modes are seen with weight (λ/λ0)², so a memory spectrum of index β appears as t^{-(β+2)}; for a goal inside
   the storage (a piezometer in the clay) it appears as t^{-β}.

**Test bed.** 1-D coastal aquifer, sea at x = 0 (stochastic sea level), no-flow at 5 km, T = 1000 m²/d, S_y = 0.1,
recharge anomaly (stochastic), 12 aquitard compartments with rates 10⁻³–1 /yr and a power-law capacity spectrum
(β = 0.5, total capacity 3 S_y). Exact goal variances by eigen-decomposition (initial part) and by the closed form
P(t) = P∞ + e^{At}(P(0) − P∞)e^{Aᵀt} (boundary part, Ornstein–Uhlenbeck forcing).

## Results (`fillimi.log`, `fillimi_tails.log`)

| Check | Result |
|---|---|
| eigen formula against direct propagation | agreement to 10⁻¹³ |
| V_IC decreasing and convex (all goals, both cases) | yes |
| Jensen bound V_IC(t) ≥ V_IC(0) e^{-2λ̄t} | holds everywhere |
| tail exponent, head goal, β = 0.3 / 0.5 / 0.7 | −2.34 / −2.55 / −2.76 (theory −2.30 / −2.50 / −2.70) |
| tail exponent, clay goal | −0.33 / −0.51 / −0.70 (theory −0.30 / −0.50 / −0.70) |
| handover, head 1 km from the sea | 0.3 yr without memory, 0.4 yr with memory |
| handover, piezometer in the clay | 105 yr (Jensen lower bound 5.3 yr) |
| initial-condition share at 20 years | < 1% for heads; 77% in the clay (operator prior), 12% for a 1 m legacy drawdown |

Meaning: memory makes the initial condition last for decades only for goals that live in the storage itself (clay
pore pressure, salt stored in clay); for goals in the transmissive aquifer near a fixed-head boundary the boundary
screens the memory and the forecast belongs to the boundary forcing within a year. The mean-rate (Jensen) bound is
valid but can be 20 times too short when memory is present; the tail formula gives the right order.

## Files

| File | What it does |
|---|---|
| `fillimi.py` | Model, exact initial and boundary variances, handover times, checks; writes `fillimi_results.json`, `fillimi.log` |
| `fillimi_tails.py` | Tail exponents for β = 0.3, 0.5, 0.7 over 10²–10⁴ yr with rates down to 10⁻⁷ /yr; writes `fillimi_tails.json`, `fillimi_tails.log` |
| `fillimi_figs.py` | Figure `figF1_handover.png` (not committed: `*.png` is ignored; run the script) |
| `run_all.sh` | Runs everything (about 2 minutes) |

Caveats: linear, one-dimensional, symmetric (no advection); the operator prior gives the clay compartments a large
variance (sd 2.6 m) by construction, so the 105-year figure illustrates the theorem; the legacy-drawdown prior gives the
practical number. Advection breaks the symmetry; review 45 (KUFIRI-GO) treats the advective, multi-boundary case.
