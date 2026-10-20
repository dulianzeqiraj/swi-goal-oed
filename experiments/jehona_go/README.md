# JEHONA-GO: design-based effects of sustained pumping from switchback experiments

Innovation of literature review 33, after Bojinov, Rambachan & Shephard, "Panel experiments and dynamic
causal effects: A finite population perspective" (*Quantitative Economics* 12(4), 2021). *Jehona* is
Albanian for "the echo": the carryover of pumping in an aquifer.

## The idea

A well field must decide about **sustained** pumping, but experiments switch pumping on and off, and the
aquifer remembers. With fair, independent coins for the periods (or blocks) of an experiment, every
potential outcome has a Walsh–Fourier expansion over the assignment path, and:

1. **Proposition 1.** The effect of sustained pumping, Δ = Y(1,…,1) − Y(0,…,0), equals the sum of the
   design-averaged single-period effects θ_j plus **odd-order interactions only**:
   Δ = Σ_j θ_j + 2 Σ_{|S| odd ≥ 3} f̂(S). Even-order carryover never biases an impulse-response estimate;
   for a linear system the identity is exact.
2. **Proposition 2.** The impulse sum 2 (Y − c) Σ_j χ_j (χ_j = 2W_j − 1, c a fixed baseline) is unbiased
   over the randomization for Σ_j θ_j, with a variance that grows linearly in the number of coordinates,
   not like the 2^m weights of the path Horvitz–Thompson estimator.
3. **Proposition 3.** With any model M run on the realized path, Δ^M + 2[(Y − c) − (M − c^M)] Σ_j χ_j is
   unbiased up to the model's error in the odd-order interactions, and its variance is that of the
   residual Y − M. A weight on the model can be cross-fitted on the other units.

## The test

48 coastal aquifer compartments (transient 1-D sharp-interface model, seasonal and yearly inflow
forcing, a toe that advances in 20–60 days and retreats in 120–360 days), 36 months, outcomes head at
the supply well, toe position and salinization exposure (fraction of the month with the toe beyond the
supply well), measurement errors 0.05 m and 20 m. Goal: the sustained-pumping effect averaged over
months 25–36. The analyst's model is deliberately wrong (T × 0.8, Sy × 1.4, symmetric 90-day toe time
constant). Designs: fair-coin switchbacks with blocks of 1, 2, 3, 6, 12 and 36 months, 1 000
randomizations each.

| File | What it does |
|---|---|
| `jehona.py` | The compartment model, the surrogate, the fast Walsh–Hadamard transform and the designs. |
| `jehona_exp.py` | Exact Walsh analysis (all 2^10 paths, every unit), the goal, the designs and the estimators (impulse sum, model baseline, model-assisted with weight 1 and cross-fitted weight, path Horvitz–Thompson, model alone), and the harm of each design (exposure of the supply wells during the experiment, wells saline at the end). About 3 minutes on 4 cores. Writes `jehona_results.json` and `jehona_walsh.npz`. |
| `jehona_figs.py` | `figJ1_walsh.png` and `figJ2_design.png`. |

```bash
python3 jehona_exp.py && python3 jehona_figs.py
```

## Results

- **Walsh structure (month 10, all 2^10 paths).** Head: 100% of the randomization variance in single
  lags, identity exact. Toe: 96.0% in single lags; the odd-order remainder is −5.3% of the sustained
  effect. Salinization exposure: 21.4% in single lags, 56% in interactions of three months or more;
  the remainder is +40% of the sustained effect. The identity holds to within 5e-13.
- **Goal.** Sustained pumping moves the toe +394 m and raises the exposure by +0.232; the wrong model
  gives +285 m and +0.030.
- **Accuracy (toe, RMSE).** Impulse sum 144 / 117 / 107 / 101 / 91 / 25 m for blocks of 1 / 2 / 3 / 6 /
  12 / 36 months; model-assisted 93 / 70 / 60 / 47 / 35 / 15 m (35–61% lower in every switchback
  design); path Horvitz–Thompson 310 m (B = 6) and 129 m (B = 12). A 12-month memory window
  underestimates the effect by 131–250 m.
- **Thresholds.** For the exposure, 95% intervals cover in only 60–85% of randomizations with
  switchbacks; with parallel arms 97%.
- **Harm.** At the same mean pumping (50%), supply wells saline at the end of the experiment: 1.9%
  (monthly switching), 2.9, 3.7, 5.7, 7.8 and 11.4% (parallel arms). The designs that measure the
  sustained effect best are those that salinize most supply wells.
