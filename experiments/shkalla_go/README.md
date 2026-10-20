# SHKALLA-GO: rate laws from a surface graph and algebraic goal identifiability

Innovation of literature review 34 ("Reactions away from equilibrium in hydrogeochemistry: 20 theorem-level
papers with algebra and operators", 2020–2026; Oxford, Caltech, Princeton, Berkeley, Harvard).
*Shkalla* is Albanian for "the step", as on a crystal surface.

**Question.** Reactive-transport models write calcite rates in the saturation ratio Ω alone and calibrate them in
one water. A real surface mechanism is a graph of sites, and by the matrix-tree theorem its rate depends on the
activities of the ions that attach and of the ions that block sites. Does a rate law calibrated in today's mixing
zone transfer to the water of an injection barrier against seawater intrusion, and which laboratory experiments
make it transfer?

## Theory (section 10 of the review)

**Proposition 1 (rate law of a calcite kink).** A kink alternates between a carbonate-terminated state K and a
calcium-terminated state K′. Ca²⁺ attaches to K (rate kA·aCa) and detaches from K′ (b1); CO₃²⁻ attaches to K′
(kC·aCO3), completing one growth unit, and detaches backwards (b2). Mg²⁺ blocks K (constant KM) and SO₄²⁻ blocks K′
(constant KS). The matrix-tree theorem and detailed balance at Ω = 1 (b1·b2 = kA·kC·Ksp) give

    R = ρ (1 − Ω) / P(a),
    P(a) = (1 − w)(1 + ψ x_C)(1 + a_Mg/K_M) + w (1 + x_A/ψ)(1 + a_SO4/K_S),

with x_A = aCa/aCa*, x_C = aCO3/aCO3* (scaled by a calcite-saturated reference water) and five parameters: the
field prefactor ρ, the attachment ratio ψ, the weight w = b2/(b1 + b2) and the inhibition constants K_M, K_S. The
rate depends on Ω only if P is constant on the level sets of Ω, which fails as soon as the ion ratio or the
inhibitor levels vary.

**Theorem 2 (identifiability is linear algebra on monomials).** P(a) = c·φ(a) with

    φ(a) = (1, a_Mg, a_SO4, x_C, x_C a_Mg, x_A, x_A a_SO4),
    c    = (1, (1−w)/K_M, w/K_S, (1−w)ψ, (1−w)ψ/K_M, w/ψ, w/(ψ K_S)),

so c₁ = 1 and c₂c₃ = c₅c₇. Laboratory rates at compositions a₁ … a_N with an unknown laboratory prefactor fix c
up to the null space of V, the matrix with rows φ(a_j). A goal that integrates rates over compositions {a(x)} is
determined for every coefficient vector if and only if span{φ(a(x))} ⊆ row V. **Corollary:** a series that
varies Ω in one background electrolyte at a fixed ion ratio has rows φ₀ + √Ω φ₁, so rank V ≤ 2 however many
experiments it contains. The criterion is checked before any experiment is run.

## Setting

- **Chemistry.** PHREEQC (phreeqc.dat, 15 °C) through phreeqpython, tabulated once on (seawater fraction f,
  calcite dissolved) for two mixing lines: the natural line mixes calcite-saturated fresh groundwater
  (log pCO₂ −2.0, Mg and SO₄ 0.5 mmol/kgw) with calcite-saturated seawater (log pCO₂ −2.5); the barrier line mixes
  the same seawater with injected soft water (Ca 0.5, alkalinity 1.0 mmol/kgw, log pCO₂ −2.0, not stabilized).
  Along the barrier line the mixtures are far more undersaturated, Mg²⁺ and SO₄²⁻ are absent where the injected
  water dominates and the ion ratio aCa/aCO3 reaches about 3 600 instead of at most about 1 700 (Figure S1).
- **Transport.** Transverse mixing between a fresh (or injected) layer and a saline layer flowing in parallel
  over 1 km at 0.2 m/day with transverse dispersivity 0.05 m, as in TRETJA-GO (review 31).
- **Field data.** Ca excess at five depths of a multilevel well 500 m along today's mixing zone, error
  0.005 mmol/L (sensitivity runs: 0.0025 and 0.01).
- **Goal.** G, the calcite dissolved per year in the first kilometre of the barrier, in mol per m of coast
  (prior 10 / 50 / 90% quantiles 30 / 270 / 384; for today's mixing zone 0.72 / 11.2 / 67.8).
- **Laboratory.** 210 candidate solutions: 7 saturation ratios (0.1 to 0.95) × 5 ion ratios (30 to 3 000) × 6
  backgrounds (dilute, fresh groundwater, 20% seawater, seawater, MgCl₂, Na₂SO₄). Each experiment measures a rate
  with a 20% error and an unknown laboratory prefactor. Every design has eight experiments plus the field well.
- **Inference.** The truth is the graph law with a uniform prior on log₁₀ρ (−5 to −2 mmol/L/day), log₁₀ψ (−2 to 2),
  w (0.05 to 0.95) and log₁₀K_M, log₁₀K_S (−1 to 1.5, mmol). Posteriors of G for 400 synthetic truths by importance
  weighting over 60 000 prior draws; for the usual practice, an 81 × 36 grid of the law in Ω alone,
  R = κ(1 − Ω)ⁿ, is fitted to the same data.

## Files

| File | What it does |
|---|---|
| `shkalla.py` | Forward model: PHREEQC tables (`build_table`, run automatically when `shkalla_table.npz` is missing), interpolation of activities, the graph law and the law in Ω alone, and the transverse-mixing transport solver (batched over parameter sets). |
| `shkalla_exp.py` | The experiment: prior banks, laboratory candidates, the seven designs (greedy D-optimal and goal-optimal included), the algebra of Theorem 2 (rank of V, span defect of the goal, rank of the shape Jacobian) and the preposterior evaluation. Writes `shkalla_results.json` (or `shkalla_results_sf<error>.json` for another field error) and `shkalla_bank.npz` (about 8.5 MB, not committed). |
| `shkalla_figs.py` | Figures `figS1_chemistry.png` (mixing lines, activities, the same mechanism in four waters) and `figS2_design.png` (errors, ranks, coverage). |
| `shkalla_table.npz` | The PHREEQC tables (101 seawater fractions × 81 dissolved amounts per line). |
| `run_all.sh` | Runs every stage in order. |

## Run

```bash
pip install numpy scipy matplotlib phreeqpython
bash run_all.sh            # about 10 minutes on 4 cores
```

## Results (field error 0.005 mmol/L)

Error factor = 10^|Δlog₁₀G| over 400 synthetic truths; coverage of the 90% intervals. "Defect" is the largest
part of a goal direction outside the row space of V (0: the goal is identified for every law with these
monomials).

| Design | rank V | Defect | Graph law: error (median / 90%) | Graph law: coverage | Law in Ω alone: error (median / 90%) | Law in Ω alone: coverage |
|---|---|---|---|---|---|---|
| field well only | 0 | 1.00 | 1.20 / 3.15 | 90% | 1.37 / 8.49 | 69% |
| dilute series (r = 300) | 2 | 0.86 | 1.20 / 3.06 | 89% | 2.47 / 15.7 | 23% |
| seawater series (r = 1 000) | 2 | 0.86 | 1.19 / 3.14 | 89% | 2.40 / 16.0 | 25% |
| dilute + seawater (4 + 4) | 4 | 0.29 | 1.08 / 2.77 | 91% | 2.42 / 15.9 | 24% |
| scenario waters | 5 | 0.37 | 1.10 / 2.53 | 89% | 1.68 / 10.1 | 32% |
| parameter-optimal | 7 | 0.00 | 1.10 / 2.65 | 89% | 2.02 / 13.5 | 22% |
| goal-optimal | 7 | 0.00 | 1.08 / 2.67 | 89% | 2.20 / 14.9 | 25% |

- **One background does not help**, as the corollary predicts: the dilute and the seawater series have rank 2
  and leave the field-only error unchanged.
- **Two backgrounds identify the transfer**: rank 4 (enough for the four shape parameters) and the median error
  falls from a factor 1.20 to 1.08. With a field error of 0.0025 mmol/L the designs that identify the transfer
  reach 1.04–1.06 (field only 1.16); with 0.01 mmol/L, 1.22–1.25 (field only 1.30).
- **Full-rank designs are robust to the mechanism** (rank 7, defect 0). The goal-optimal design picks corner
  compositions: dilute (Ω 0.1, r 30), dilute (0.1, 3 000), seawater (0.95, 1 000), Na₂SO₄ (0.1, 30), Na₂SO₄
  (0.1, 3 000), dilute (0.95, 300), seawater (0.1, 3 000), MgCl₂ (0.1, 30). Median effective sample size 39–47 for
  these designs, so their coverage carries Monte Carlo error.
- **The law in Ω alone is confidently wrong**: calibrated on the field well alone it underestimates the barrier
  dissolution by a factor 1.97 on average; laboratory data make it worse (median error 1.68–2.47, coverage
  22–32%; 11–58% at the other field errors), while the graph law keeps 89–91% coverage.
- **Field data fix the scale**: even for the designs that identify the transfer, the 90th percentile of the
  error only falls from 3.15 to 2.53–2.77, because no laboratory experiment can supply the field prefactor.

## Limitations

One kink type and one inhibition state per site; Mg incorporation, other inhibitors and other step mechanisms
add monomials (Theorem 2 applies to the richer spanning-tree polynomial in the same way). phreeqc.dat is
approximate at seawater ionic strength. Laboratory solutions are idealized as prepared at given activities, and
the priors are wide but arbitrary.
