# KALIB-GO: learning rate calibrated on the goal by bootstrap

SAFE-GO (`../safe_go`) repairs Bayesian inference for the toe of the saltwater interface when the
monitoring network mixes exact coastal readings with noisy inland readings (the Grünwald & van Ommen
2017 failure). It picks the learning rate η with SafeBayes, which targets the predictive log loss of
all readings. With many exact readings this is too cautious: coverage rises above 90% and the toe
interval is much wider than the oracle's.

KALIB-GO instead calibrates η on the goal itself, following Syring & Martin (2019, *Biometrika*
106(2), 479–486). For each η on the grid {1, 2^-1/2, …, 2^-6}, the η-posterior 90% interval of the
toe is recomputed on B = 60 bootstrap resamples. KALIB-GO then takes the largest η whose bootstrap
intervals contain the full-data toe estimate at least 90% of the time, interpolating in log η.
BayesBag (the bagged η = 1 posterior over the same resamples) is reported as a comparator.

The test is the SAFE-GO test, with the same 200 truths and data:
- Strack toe on the coast–well axis.
- A Legendre polynomial model of degree ≤ 12 with a conjugate prior and homoskedastic noise.
- 30 inland wells with noise sd 0.7 m², plus n_e exact coastal readings.

Requirements: Python 3 with NumPy, SciPy and matplotlib. `safego.py` and `safego_exp.py` are
imported from `../safe_go`.

| File | What it does |
|---|---|
| `kalibgo.py` | Toe draws from the η-posterior given sufficient statistics; bootstrap coverage ĉ(η) of the toe interval; calibrated η; BayesBag draws. |
| `kalibgo_exp.py` | E1 (n_e = 0…240) and E2 (three monitoring additions to a baseline with 60 coastal readings). Five methods: Bayes, SAFE-GO, BayesBag, KALIB-GO, oracle. Writes `kalibgo_runs.json` (about 1.7 MB; not committed). |
| `kalibgo_results.py` | Aggregates the runs into `kalibgo_results.json`: coverage, width, median and 90th-percentile toe error, η, median bootstrap-coverage curves. It also runs the design-decision pipelines, in which each method picks the addition that narrows its own interval most. |
| `kalibgo_figs.py` | The two figures of the report. |

## Run

```bash
python3 kalibgo_exp.py 200   # ~43 min on 4 cores
python3 kalibgo_results.py
python3 kalibgo_figs.py
```

## Main numbers (200 realisations)

| Exact coastal readings | Method | Coverage of 90% interval | Width [m] | Median toe error [m] | P90 error [m] | η |
|---|---|---|---|---|---|---|
| 0 | Bayes | 0.91 | 73 | 13.0 | 50 | 1 |
| 0 | SAFE-GO | 0.91 | 81 | 14.7 | 50 | 1.00 |
| 0 | KALIB-GO | 0.91 | 78 | 15.5 | 54 | 1.00 |
| 240 | Bayes | 0.48 | 31 | 19.2 | 54 | 1 |
| 240 | BayesBag | 0.94 | 128 | 20.5 | 55 | 1 |
| 240 | SAFE-GO | 0.96 | 95 | 14.3 | 46 | 0.18 |
| 240 | KALIB-GO | 0.87 | 68 | 13.8 | 45 | 0.25 |
| 240 | oracle | 0.91 | 69 | 13.8 | 44 | 1 |

- **Coverage:** KALIB-GO stays at 87–91% for every n_e. Its interval is close to the oracle's and 29%
  narrower than SAFE-GO's at n_e = 240.
- **BayesBag:** it covers, but its interval is twice as wide. Every bootstrap posterior has η = 1, so
  its error stays as large as Bayes's.

**Design test**, starting from a baseline of 60 coastal readings:

| Method | Apparent worth of +120 coastal readings | Picks them | Final coverage | Median error | P90 error |
|---|---|---|---|---|---|
| Bayes | +11.5 m | 62% | 0.52 | 14.9 m | 47 m |
| SAFE-GO | −9.2 m | 4% | 0.87 | 12.6 m | 40 m |
| KALIB-GO | −0.7 m | 14% | 0.85 | 11.8 m | 37 m |

KALIB-GO gives the redundant exact coastal readings a worth close to zero. Its pipeline has the
smallest final error, with a 53 m interval against 60 m for SAFE-GO. After the design choice,
coverage falls slightly below nominal for both calibrated methods (85% and 87%). This is a selection
effect: picking the addition that narrows the interval most favours realisations where the interval
is optimistic.

The report is
`docs/literature/Kerkim_artikujsh_Bayes_i_Keqspecifikuar_II_Princeton_Oxford_Caltech_ETH_Berkeley_2020-2026.docx`
(section 10).
