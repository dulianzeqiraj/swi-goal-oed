# KTHIMI-GO: does the monitoring information reach the pumping decision?

A monitoring network is useful only if what it measures changes what the operator does. Massey's conservation
law splits the information between the pumping history and the toe history into two parts:
- the **forward** directed information, from pumping to the toe;
- the **feedback** directed information, from the toe to the decisions.

KTHIMI-GO uses the per-decision feedback term as a design criterion for monitoring. It compares that term with
the sensor information alone, using the goal itself: the salinization risk at equal supply.

**Model.** The RRJEDHA-GO well field (`../rrjedha_go/`), 200 000 wells × 10 years:
- Each year the operator pumps high or low, with
  `logit P(A=1) = b0 + B1 (2 A_prev − 1) + κ·BR[R] + BD[D]`.
- R is the toe reading X + σ·noise, in 4 alarm levels. D is the drought class.

**Designs.** 24 monitoring designs plus a no-monitoring reference:
- reading noise σ ∈ {0, 0.01, 0.02, 0.04, 0.08, 0.16};
- operator responsiveness κ ∈ {0.5, 1, 2, 3};
- **no monitoring:** the alarm level is drawn independently of the toe.

For every design the intercept b0 is calibrated so that mean pumping equals that of the reference design
(σ = 0.02, κ = 1). Supply is matched to within ±0.003.

**Quantities.** All are exact given the model, in bits per decision:

| Quantity | Definition |
|---|---|
| Sensor information | I(X; R) |
| Feedback information | I(X; A \| A_prev, D) = H(A \| A_prev, D) − E[h(P(A = 1 \| X, A_prev, D))] |

**Goal.** The probability that the toe reaches the escape point within 10 years.

| File | What it does |
|---|---|
| `kthimi.py` | Simulator with configurable monitoring, exact information quantities, supply calibration. |
| `kthimi_exp.py` | The 25 designs. Writes `kthimi_results.json`. Needs `../rrjedha_go/`. Takes about 2.5 minutes on 4 cores. |
| `kthimi_figs.py` | `figK1_kthimi.png` and `figK2_rrjeta.png`. |

## Main results

**Ranking designs.** At matched supply, the 10-year risk falls from 45.2% without monitoring to 37.5% with the
best design. The Spearman correlation of risk with each criterion over the 24 monitoring designs:

| Criterion | Spearman ρ |
|---|---|
| Feedback information | −0.97 |
| Sensor information | −0.16 |

Sensor information ranks sensors, but it cannot tell a precise sensor whose readings the operator ignores from
a cruder sensor the operator acts on.

**Responsiveness versus precision.** Raising the operator's response at the reference sensor (σ = 0.02) helps far
more than perfecting the sensor:

| Change | Risk reduction vs. no monitoring | Feedback information |
|---|---|---|
| Reference: σ = 0.02, κ = 1 | 3.3 points | 65 millibits |
| Response raised: σ = 0.02, κ = 3 | 7.6 points | 265 millibits |
| Sensor perfected: σ = 0, κ = 1 | 3.7 points | 68 millibits |

**Diminishing returns.**

| Feedback information | Risk reduction |
|---|---|
| ~19 millibits | ~1.7 points |
| ~295 millibits | 7.7 points |

Equal feedback information does not guarantee equal risk:

| Design | Feedback information | Risk |
|---|---|---|
| σ = 0.16, κ = 3 | 72 millibits | 40.1% |
| σ = 0, κ = 1 | 68 millibits | 41.6% |

So the criterion is a ranking tool, not a complete substitute for the risk computation.

The report is
`docs/literature/Kerkim_artikujsh_Teoria_Informacionit_Kauzaliteti_III_2020-2026.docx` (section 9).
