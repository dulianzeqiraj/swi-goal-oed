# VEGLA-GO: which measurements let causal discovery decide whether an instrument is valid?

*Vegla* means "the instrument". The base article (Eberhardt, Kaynar & Siddiq, *Management Science* 71(4), 2025)
discovers causal graphs with latent confounders and feedback cycles by optimization, and uses them to judge
whether an instrument is valid. VEGLA-GO asks the design question that comes first: **which extra variables
should be measured, and for how long, so that the discovery gives a correct verdict on the instrument?**

It ranks designs by the probability that a calibrated verdict on validity is correct. A generic design would
instead maximize the structural information about the graph. The test shows that the two criteria disagree.

**Model.** A linear structural model `X = B X + e` with correlated errors (latent confounders) and cycles
(feedback), over six variables of a coastal well field:

| Variable | Meaning | Observed |
|---|---|---|
| Z | candidate instrument: an exogenous shift of pumping (rotation schedule or tariff step) | always |
| Q | pumping of the well field | always |
| C | chloride at the supply well | always |
| H | head at a coastal observation well | candidate |
| A | agricultural pumping in the plain | candidate |
| R | recharge | candidate |

- **Fixed edges:** Z→Q, Q→H, H→C.
- **Optional edges:** 9 directed (including the feedback C→Q) and 5 bidirected, so the space has 2^14 = 16 384 graphs.
- **Validity of Z:** Z is d-separated from C after the edges out of Q are removed.
- **Priors:** a "physical" prior over the optional edges (P(valid) = 0.593) and a flat prior of 0.3 per edge (P(valid) = 0.367).

For linear models with cycles and correlated errors, d-separation is the global Markov property. Each graph
therefore has a signature: the d-separation status of all 240 statements over the six variables. The
implementation was checked against exact population partial correlations, with 0 mismatches over 72 000
statements in 300 random graphs.

**Discovery and decision.** Every graph is scored by its weighted agreement with Fisher-z tests (α = 0.05) of
all observable statements, with weight |log p − log α|. The optimum is found exactly by enumeration. Two
decision rules are compared:
- **Optimum rule** (implied by the base article): certify Z if all optimal graphs make it valid, refute it if
  all make it invalid, otherwise undetermined.
- **Calibrated rule:** the margin m = (best valid score) − (best invalid score).
  - Certify if m exceeds the 95% quantile of m over invalid instruments.
  - Refute if m is below the 5% quantile over valid instruments.
  - The thresholds are set on 1000 calibration draws at the planned record length, and the results are
    reported on 1000 independent test draws.

| File | What it does |
|---|---|
| `vegla.py` | Graph space, d-separation for mixed cyclic graphs, signatures, exact large-sample design values. |
| `vegla_exp.py` | Exact tables and finite-record simulations (n = 120, 240, 960; both priors). Writes `vegla_results.json`. Takes about 4 minutes; the graph space is cached in `vegla_space.npz` (not tracked, rebuilt in about 1 minute). |
| `vegla_figs.py` | `figV1_designs.png` and `figV2_rule.png`. |

```
python3 vegla_exp.py
python3 vegla_figs.py
```

## Main results

**Structure and decision part ways.** In the large-sample limit (physical prior), agricultural pumping with
recharge (A+R) gives the most structural information of any pair. Coastal head with recharge (H+R) gives more
information about validity:

| Pair | Structural information | Equivalence classes | Information about validity | Validity settled |
|---|---|---|---|---|
| A+R | 6.57 bit | 290 | 0.467 bit | 42.6% |
| H+R | 5.19 bit | 146 | 0.480 bit | 45.1% |

**With finite records the gap widens.** Correct verdicts of the calibrated rule (% of test draws):

| Pair | Physical prior, n = 240 | Physical prior, n = 960 | Flat prior, n = 240 |
|---|---|---|---|
| H+R (VEGLA-GO choice) | 39.6 | 56.0 | 46.5 |
| A+R (most structural information) | 32.4 | 40.2 | 38.7 |

- A+R is the worst or joint-worst pair for the verdict in all 6 settings (2 priors × 3 record lengths).
- H+R is the best pair in 5 of the 6. The exception is the flat prior at n = 120, where H+A is best.
- H+R with 960 records (56.0%) beats all three measurements with 240 records (53.2%).

**No extra measurement, no refutation.** With only Z, Q and C observed, no invalid instrument is ever refuted:
every independence pattern among the three is also produced by valid graphs.

**The optimum rule certifies too readily.** At n = 240 (physical prior):
- The optimum rule certifies 15–32% of invalid instruments, depending on the design.
- The calibrated rule holds false certification at 3.3–5.4%.
- Falsely certified instruments have a median IV bias of 0.44–0.86 times the effect itself.

The report is
`docs/literature/Literature_review_Causal_Discovery_Optimization_Instrument_Validity_2020-2026.docx` (section 10).
