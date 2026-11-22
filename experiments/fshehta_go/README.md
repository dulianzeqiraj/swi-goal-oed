# FSHEHTA-GO: hidden confounders over time

Code and results of the ninth state-of-the-art review, *State of the art IX: hidden confounders over time* (November
2026, English). The review does four things:
- it extracts the Time Series Deconfounder (Bica, Alaa & van der Schaar, ICML 2020) and its supplement;
- it adds twenty papers from Oxford, Caltech (with JPL), Harvard and MIT (2020–2026) on hidden confounding in time
  series;
- it draws our analogues of the article's Figures 1 and 2, showing who confounds the effect of pumping on salinity at
  Fushë-Kuqe;
- it presents and tests the FSHEHTA-GO innovation ("fshehtë" = hidden).

It is the companion of reviews I–VIII (`../garancia_go` … `../kripa_go`).

**The question.** The pumping of the wells responds to the same dryness that lowers the recharge. What does a cut in
pumping do to the salinity once that hidden confounding is removed?

**Who confounds.**
- The treatments are the pumping rates of the `k` wells; the outcome is the salinity.
- The hidden multi-cause confounder is the dryness (heat, irrigation demand), which raises all pumping and lowers the
  recharge.
- The hidden single-cause confounder is the crop stress of one farm, which raises one well and lowers the local
  recharge.
- The recharge is the path through which both reach the salt.
- Rain and past chloride are observed. The sea level causes the salinity only, so it is not a confounder.

**The test bed.** A linear-response coastal aquifer in weekly steps:
- the dryness is AR(1) and the rain is seasonal;
- recharge = κ·rain − b·dryness;
- the pumping of each well = μ + λ·dryness (+ ψ·crop stress at well 1) + noise;
- the salinity responds to the pumping and the recharge through a 10-week kernel;
- two head loggers respond to them through a 4-week kernel, with known drawdown coefficients.

**The innovation.** The Time Series Deconfounder builds its substitute from the past, `Z_t = g(H_{t-1})`. FSHEHTA-GO
adds a second substitute read from another measurement. It takes the heads, adds back the known drawdown of the
pumping, and deconvolves the head kernel; what remains reads the recharge.

- **Proposition D1 (curse of many causes).**
  - It gives the closed-form bias of the summed well effects left by any substitute.
  - For substitutes built from the past, the bias is at least `kλρb v / (v_ε + kλ² v)`, with `v = (1−a_S)²(1−ρ_D²)`.
  - This bound grows with `k` to the unadjusted limit `ρb/λ`.
  - A substitute built from the current pumping makes the design singular.
- **Proposition D2.** With known drawdown and head kernel, and loggers whose recharge footprints have full rank, the
  physics substitute removes the confounding. The single-cause assumption becomes a rank condition, met by placing
  loggers.
- **Proposition D3.** The physics check: given the substitute, the pumping must be independent of the reading. It is
  calibrated by circular time shifts. The article's predictive check cannot see a common innovation.
- **Proposition D4.**
  - A wrong drawdown leaks a bias that is linear in its error and invisible to the fit; the check catches it.
  - A wrong head kernel is identified by the salinity fit and corrected by profiling.

**Tests** (`fshehta_exp.py`, 400 replications; 200 for 32 and 64 wells).
- **T29:** many wells, with slow and fast dryness. At 8 wells the bias of the summed effects (true sum 0.94) is:

  | Estimator | Bias |
  |---|---|
  | unadjusted | +0.59 |
  | learned history substitute | +0.56 |
  | best history substitute | +0.15 (+0.53 at 64 wells) |
  | physics substitute | 0.00 (spread 0.05 against 0.32) |

- **T30:** a single-cause confounder at well 1 biases its effect by +97% with the history substitute and by +7% with
  the physics one.
- **T31:** a wrong drawdown biases β₁ by 19% per 10% of error, as D4 predicts (within 2%). A head kernel 0.6–1.5 times
  off biases the cut by −38% to −48% when fixed, and by at most 1.0% when profiled.
- **T32:** the physics check has size 6.0% and power 99–100%. The article's predictive check gives p = 0.49–0.55 in every
  scenario.

**Files.**

| File | Content |
|---|---|
| `fshehta_exp.py` | The test bed, the estimators, T29–T32 → `res/fshehta.json`, `res/fshehta_case.npz`, `res/fshehta_log.txt`. `python3 fshehta_exp.py quick` runs 60 replications; `python3 fshehta_exp.py T32` re-runs the checks alone on top of an existing `res/fshehta.json`. |
| `fshehta_figs.py` | Figures: our analogues of Figures 1 and 2 (`fig_dag`, `fig_arch`), the case, T29, T30–T32, the map of the twenty papers. |
| `cards_fshehta.py` | The twenty cards (five per institution) and the rows of the state-of-the-art table. |
| `text_fshehta.py` | The text: the article extracted, state of the art, our schemes, FSHEHTA-GO with proofs, synthesis. |
| `build_fshehta_doc.py` | Builds the Word document (OMML equations, clickable links). |
| `run_all.sh` | Runs everything. |

**Output.** `docs/literature/Literature_review_State_of_the_Art_IX_Time_Series_Deconfounder_Hidden_Confounders_Pumping_Salinity_FSHEHTA-GO_Oxford_Caltech_Harvard_MIT_2020-2026.docx`
(30 pages in the LibreOffice render).

**Verification.** All twenty cards are partly verified: their landing pages were reached through search results only.
The article and its supplement were read from the PDFs the user provided.
