# ATRIB-GO: causal attribution of a well-salinization event to a pumping increase

A supply well has pumped at Q0 for a long time. Pumping is then raised to Q1, and within H = 30 years
the toe of the saltwater interface reaches the well. These scripts ask two questions:
- Was the pumping increase a *necessary* cause, or would a drought have salinized the well anyway?
- Which monitoring data make that attribution clear for one specific event?

**Model.** The toe model is the one in KRAMERS-GO (`../kramers_go/kramers2.py`):
- A Strack toe X = x_toe/d relaxes toward equilibrium with τ = 2 yr.
- Recharge enters as a lognormal factor r = exp(ε − s²/2), where ε is an Ornstein–Uhlenbeck process
  with s = 0.2 and θ = 0.5 yr.

**Twin worlds.** The factual world (Q1) and the counterfactual world (Q0) share the same recharge path,
following Pearl's abduction–action–prediction. For one path, both toes are deterministic. Define:
- E_q: salinization within H under pumping q.
- N = 1 − E_0, so N = 1 means the increase was necessary.
- PN(D) = P(N = 1 | E_1 = 1, D): the probability of necessity given the monitoring data D.
- W(D) = h(PN) − E[h(PN(D))], in bits, with h the binary entropy: the worth of a design D for the
  attribution goal.

Requirements: Python 3 with NumPy, SciPy and matplotlib. `kramers2.py` is imported from
`../kramers_go`.

| File | What it does |
|---|---|
| `atrib.py` | Model wrapper: stationary OU paths, vectorised twin-world runs, and exact Gaussian conditioning of the recharge path on noisy block means (Matheron's rule). |
| `atrib_exp.py` | Runs A1 and A2 and writes `atrib_results.json`. **A1:** population-level p1, p0, PN, PS for four pumping increases (200 000 paths), with the twin-world check of monotonicity. **A2:** event-level PN for 300 test events and these designs: event only, event date, and recharge block means (annual noise 0.10/0.05/0.02 and quarterly 0.02). It also writes a first toe design by ensemble importance sampling, which `atrib_toe.py` replaces (see below). |
| `atrib_toe.py` | Toe-monitoring designs: annual toe position with 50 m or 100 m noise. A bootstrap particle filter with 8 000 particles keeps the full recharge path of each particle. It overwrites the toe entries in `atrib_results.json`. |
| `atrib_figs.py` | The two figures of the report. |

## Run

```bash
python3 atrib_exp.py    # ~5 min on 4 cores
python3 atrib_toe.py    # ~4 min on 4 cores
python3 atrib_figs.py
```

## Main numbers

**Population level** (200 000 recharge histories). No path salinizes without the increase but not
with it, so the twin-world PN equals 1 − p0/p1 (= FAR) exactly.

| Q0/Qc → Q1/Qc | P(E) with increase | P(E) without | PN | PS |
|---|---|---|---|---|
| 0.70 → 0.85 | 34% | 1.7% | 0.95 | 0.32 |
| 0.75 → 0.90 | 57% | 6.0% | 0.90 | 0.55 |
| 0.80 → 0.90 | 58% | 17% | 0.72 | 0.50 |
| 0.85 → 0.95 | 80% | 36% | 0.55 | 0.69 |

**Event level** (0.80 → 0.90 Qc, 300 test events, prior uncertainty 0.86 bit):

| Data | Uncertainty [bit] | Worth W [bit] | Brier | Confident (PN ≥ 0.9 or ≤ 0.1) | Accuracy of confident |
|---|---|---|---|---|---|
| event only | 0.86 | 0 | 0.186 | 0% | – |
| + event date | 0.82 | 0.04 | 0.173 | 4% | 92% |
| + annual toe, 100 m | 0.82 | 0.04 | 0.167 | 4% | 75% |
| + annual toe, 50 m | 0.81 | 0.05 | 0.170 | 6% | 94% |
| + annual recharge, 0.10 | 0.49 | 0.38 | 0.105 | 50% | 99% |
| + annual recharge, 0.05 | 0.28 | 0.58 | 0.055 | 73% | 99% |
| + annual recharge, 0.02 | 0.12 | 0.74 | 0.022 | 89% | 100% |
| + quarterly recharge, 0.02 | 0.07 | 0.79 | 0.019 | 92% | 100% |

- **Event date:** early salinizations have low PN (0.38 in year 3), because they need droughts strong
  enough to salinize the well anyway. Late ones have high PN (0.97 in the last year).
- **What makes one event attributable** is the exogenous forcing (recharge) at a fine enough time
  resolution. Monitoring the toe itself adds almost nothing beyond the event date, even though it is
  the most valuable data for prediction.
- **Method note:** a first toe estimate by ensemble importance sampling had degenerate weights
  (median effective sample size about 3) and gave false confidence. The particle filter avoids this,
  with a median minimum effective sample size of 457.

The report is
`docs/literature/Kerkim_artikujsh_Modelimi_Kauzal_Sisteme_Komplekse_Stokastike_Deterministike_2020-2026.docx`
(section 10).
