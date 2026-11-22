# SAFE-GO: SafeBayes learning rate for goal-oriented inference and data worth

Grünwald & van Ommen (2017, *Bayesian Analysis* 12(4), 1069–1103) show that Bayesian linear
regression with a homoscedastic Gaussian noise model becomes inconsistent when part of the data is
exact ("easy" points at x = 0, y = 0): the posterior underestimates the noise variance, moves to
ever more complex models (hypercompression) and becomes overconfident. Their repair is a generalized
posterior with learning rate η chosen by SafeBayes.

A coastal monitoring network has the same structure: shoreline readings are exact (freshwater
potential Φ = 0 at the coast) and numerous, while inland readings are noisy. These scripts test, on
the toe of the saltwater interface, (1) how standard Bayes behaves as exact coastal readings are
added, (2) whether SafeBayes repairs it, and (3) how each method values three monitoring additions.

- **Truth:** Strack (1976) potential on the coast–well axis. The well is at d = 2 km and pumps
  Q = 2 600 m³/d; δ = 0.025 and B = 30 m. K and q0 are uncertain (medians 100 m/d and 1.5 m²/d,
  with CV 30% and 20%). Only realisations with the toe between 600 and 1 600 m are kept.
- **Model:** Legendre polynomial of degree ≤ 12 for Φ, with a conjugate normal–inverse-gamma prior
  and Bayesian model averaging over the degree.
- **Data:** 30 inland wells (100–1 800 m, noise sd 0.7 m²) plus n_e exact coastal readings.

Requirements: Python 3 with NumPy, SciPy and matplotlib.

| File | What it does |
|---|---|
| `safego.py` | Model, conjugate η-posterior for all nested degrees from one Cholesky factor, R-log SafeBayes (optionally averaged over several random orders, with the first losses skipped), and posterior sampling of the toe. |
| `safego_exp.py` | Experiments E1 (n_e = 0…240) and E2 (three additions to a baseline with 60 coastal readings). Four methods: Bayes (η = 1); SafeBayes with one random order; SAFE-GO, i.e. SafeBayes averaged over 10 orders with the first 10 losses skipped; and an oracle that uses the coastal readings as one exact constraint. Writes `safego_runs.json` (about 1.3 MB; not committed). |
| `safego_results.py` | Aggregates the runs into `safego_results.json`. Coverage and width of the 90% interval, median and 90th-percentile toe error, mean degree, noise variance and η; also the decision pipeline (each method picks the addition with the largest width reduction). |
| `safego_figs.py` | The two figures of the report. |

## Run

```bash
python3 safego_exp.py 200   # ~12 min on 4 cores
python3 safego_results.py
python3 safego_figs.py
```

## Main numbers (200 realisations)

| Exact coastal readings | Method | Coverage of 90% interval | Width [m] | Median toe error [m] | Mean degree | η |
|---|---|---|---|---|---|---|
| 0 | Bayes | 0.91 | 73 | 13.0 | 2.5 | 1 |
| 0 | SAFE-GO | 0.91 | 81 | 14.7 | 2.4 | 1.00 |
| 240 | Bayes | 0.47 | 31 | 19.3 | 9.5 | 1 |
| 240 | SAFE-GO | 0.97 | 95 | 13.9 | 2.7 | 0.18 |
| 240 | oracle | 0.89 | 70 | 13.4 | 2.6 | 1 |

Bayes estimates the noise variance at 0.051 with 240 coastal readings (true 0.49). Its 90%
interval narrows from 73 to 31 m while coverage falls from 91% to 47%.

In the design test, Bayes values extra coastal readings most and picks them in 62% of
realisations. With that addition its coverage falls to 52% and its median error rises from 15.0 to
18.2 m. SAFE-GO gives coastal readings negative worth (its calibrated interval widens from 88 to
99 m) and picks wells near the toe in 63% of realisations. The final coverage is 88% for SAFE-GO
against 55% for Bayes, with median error 12.2 m against 15.2 m.
