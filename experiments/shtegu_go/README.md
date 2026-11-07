# SHTEGU-GO: warnings for what happens between samples

Code and results of the eleventh state-of-the-art review, *State of the art XI: warnings for what happens between
samples* (November 2026, English). The review does four things:
- it extracts the path-dependent neural jump ODE article of Krach, Nübel & Teichmann (*Stochastic Processes and their
  Applications*, 2026; arXiv:2206.14284v7) and the robust pricing and hedging article with neural SDEs of Gierjatowicz,
  Sabate-Vidales, Šiška, Szpruch & Žurič (SSRN 3646241, 2020), both provided by the user;
- it gives the state of the art in forecasting from irregular records and in robust bounds, with a paragraph for field
  5.3 of the NATO proposal;
- it maps robust pricing onto a coastal wellfield: the chloride statistics at the sampling dates are the "liquid prices",
  and the crossing of the limit between two samples is the "lookback option";
- it presents and tests the SHTEGU-GO innovation ("shtegu" = the path).

It is the companion of reviews I–X (`../garancia_go` … `../nderhyrja_go`).

**The question.** Laboratory samples arrive every few weeks or months. Does the chloride cross 250 mg/L between two
samples, and what must be measured to know?

**The innovation.**
- The warning is the probability that the limit is crossed at any time in the season, not only at the sampling dates.
- It is reported as a band over all models consistent with the records (the robust price of A2).
- The band is certified for a single site by a conformal margin (which A2 lacks).
- The monitoring design buys the observation that closes the band (a logger, or pairs of samples a few days apart).
- Online, the warning is the conditional probability that A1 learns, with the observed path and a head logger as inputs.

**The propositions.**
- **S1 (marginals do not bound the crossing).** For a stationary Ornstein–Uhlenbeck chloride the crossing probability is
  non-decreasing in the mean-reversion rate κ (Slepian's inequality). Over all models consistent with the marginal law
  the band is 1 − Φ(z) ≤ p < 1: bounded below by the marginal tail, not at all from above.
- **S2 (information per pair of samples).** I_τ(κ) = τ²ρ²(1+ρ²)/(1−ρ²)², with ρ = e^{−κτ}. It tends to 1/(2κ²) as
  τ → 0 and decays as 2τ²e^{−2κτ}. A record of n transitions cannot give κ a relative standard error below √(2/n).
- **S3 (certified robust band).** The band over the consistent models, widened by the conformal margin δ (the k-th
  smallest distance of J calibration aquifers, k the smallest integer not below (J+1)(1−α)), covers the truth with
  probability at least 1 − α.
- **S4 (online warning).** The best forecast adapted to irregular, incomplete records is the conditional probability. It
  needs the whole observed path, and any coordinate that sees the slow part (a head logger), when chloride has memory.

**The test bed.** Seasons of 120 days simulated in steps of 0.25 day, with the exact maximum of a Brownian bridge inside
each step; records of 8 years; chloride mean 180 mg/L, standard deviation 35 mg/L, limit 250 mg/L (z = 2.0); four
designs: quarterly, monthly and weekly samples (±20% jitter of the dates) and a daily logger.

**Tests** (`shtegu_exp.py`).
- **Self-checks.** The bridge maximum adds the crossings between grid points (0.473 against 0.419 on the grid alone); a
  very slow chloride gives the marginal tail (0.0236 against 0.0228); the Fisher information agrees with the variance of
  the simulated score (14.642 against 14.641); its short-lag limit is 0.49999 in units of 1/κ².
- **T37.** With a correlation time of 8 days the chloride crosses the limit within the season with probability 0.78,
  34 times the marginal tail (0.023). Median bands (200 records per design; coverage 96–98%):

  | Design | Band | Samples see a crossing | Cramér–Rao rel. s.e. of κ |
  |---|---|---|---|
  | quarterly samples | 0.18–1.00 | 3.1% | 1376 |
  | monthly samples | 0.48–1.00 | 8.7% | 1.16 |
  | weekly samples | 0.71–0.84 | 27.8% | 0.103 |
  | daily logger | 0.76–0.80 | 57.1% | 0.028 |

- **T38.** Two-component chloride (true 0.80). The band over the consistent models: marginals only 0.07–1.00,
  quarterly 0.17–1.00, monthly 0.34–1.00, weekly 0.62–0.97, daily logger 0.64–0.88.
- **T39.** 400 aquifers with skewed chloride. With a logger the band of the Gaussian family covers the truth in 74% of
  them (62% for the most skewed). The conformal margin (median 0.068) restores 90.3% on average over 50 random splits
  (10–90%: 86–94%; target 90%); the median width goes from 0.32 to 0.45. Monthly and weekly bands are wide and cover
  about 97% without a margin.
- **T40.** Online warning for a crossing in the next 30 days, on 24,000 simulated records. Brier skill over
  climatology: 6.1% with Markov features (last sample), 6.9% with path features, 20.3% with path features and a head
  logger.

**Files.**

| File | Content |
|---|---|
| `shtegu_exp.py` | The simulator, the likelihood and Fisher information, the bands, the conformal certificate, the online warning, the self-checks and T37–T40 → `res/shtegu.json`, `res/shtegu_table.npz`, `res/shtegu_log.txt`. `python3 shtegu_exp.py quick` runs a short version; the full run takes about 70 s. |
| `shtegu_figs.py` | Figures: the analogy and one season, T37, T38, T39, T40. |
| `text_shtegu.py` | The text: the two documents extracted, what we learn, the state of the art, our scheme, SHTEGU-GO with proofs, tests, NATO texts, limitations. |
| `build_shtegu_doc.py` | Builds the Word document (OMML equations, clickable links). |
| `run_all.sh` | Runs everything. |

**Output.** `docs/literature/Literature_review_State_of_the_Art_XI_Warnings_Between_Samples_Neural_Jump_ODE_Robust_Neural_SDE_SHTEGU-GO.docx`
(13 pages in the LibreOffice render).

**Verification.**
- A1 and A2 were read in full from the PDFs provided.
- References R and B are cited as those documents list them; they were not opened here.
- W1 (Slepian 1962) was checked against publisher and index records.

**Limitations.** S1 and S2 are proved for a stationary Ornstein–Uhlenbeck chloride; T38 and T39 use a two-component
Gaussian family on a grid instead of neural SDEs; T40 uses logistic regression on hand-made path features as a stand-in
for a neural jump ODE; the certificate holds for the law of the calibration aquifers, so measured anchor periods are
needed for the site.
