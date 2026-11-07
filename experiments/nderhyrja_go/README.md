# NDERHYRJA-GO: placing sensors that interfere

Code and results of the tenth state-of-the-art review, *State of the art X: placing sensors that interfere* (November
2026, English). The review does five things:
- it extracts the robust optimal design article of Chowdhary, Attia & Alexanderian (arXiv:2409.09137v2, 2025);
- it extracts the Certified OED framework (Zeqiraj, draft of 3 October 2026), both provided by the user;
- it gives the state of the art in sensor placement for the NATO proposal, with a paragraph for field 5.3;
- it draws who interferes with a CERTAIN-COAST piezometer;
- it presents and tests the NDERHYRJA-GO innovation ("ndërhyrja" = the interference).

It is the companion of reviews I–IX (`../garancia_go` … `../fshehta_go`).

**The question.** Where should the piezometers go when their errors are correlated by air pressure, logger drift, cable
cross-talk and model error? Should the network buy reference channels (a barometer, a sealed channel per logger hub)
that see only the error?

**The innovation.**
- Reference channels become design variables beside the piezometers.
- The correctable interference (air pressure × barometric efficiency, logger drift) is removed by marginalising its
  sources.
- The network is chosen against the worst plausible interference.
- Every network carries a certified optimality gap.

**The propositions.**
- **N1 (value of a reference channel).** It is worth zero alone, and exactly zero to the independent-noise and naive
  criteria. Its exact value is a closed-form ratio of Schur complements, and it can grow as piezometers are added, so
  the criterion is not submodular.
- **N2 (correction and ceiling).** The marginal posterior mean equals the interference-free formula applied to the
  corrected data. The information lost to the interference is I(m; c | y), and no choice of references can exceed the
  interference-free ceiling.
- **N3 (worst case).** The worst amplitudes are the upper ends. The gradient in the shape parameters (correlation
  length, loading errors) is an exact data-space trace formula.
- **N4 (robust certificate).** A certified upper bound on the robust optimum, from three layers:
  - the noise-inflation relaxation, with the inflation borrowed from the non-correctable part;
  - correction-ceiling cuts;
  - enumeration of the reference sets, solved as a cutting-plane linear programme.

**The test bed.** A linear-Gaussian coastal aquifer on a 30 × 30 grid. The candidates are:
- 48 piezometers in 16 nests of 3, served by 4 hubs;
- 1 barometer and 4 hub reference channels.

The error parameters lie in a box.

**Tests** (`nderhyrja_exp.py`).
- **Self-checks.** Every closed form agrees with direct computation, to between 1e-15 and 1e-8.
- **T33.** The barometer adds 0 nats alone, up to 0.64 after 5 piezometers and 0.46 after 16. A hub channel is worth 0
  until a piezometer of its hub is selected, then grows to 0.38. The naive and independent criteria value it at exactly 0.
- **T34.** Worst-case information at 12 sensors:

  | Design rule | Nats |
  |---|---|
  | interference ignored | 3.67 |
  | naive correlated weighting | 4.25 |
  | exact, no references | 4.36 |
  | robust, no references | 4.48 |
  | exact + references (nominal) | 5.48 |
  | NDERHYRJA-GO | 5.59 |

  NDERHYRJA-GO has the best worst case at every budget from 4 to 16.
- **T35.** Certified gap of the NDERHYRJA-GO network: 41% at 4 sensors, 18% at 12 and 12% at 16. On 14 candidates,
  greedy plus exchange equals the exhaustive optimum in 4 of 4 budgets, and the certificate is always above the optimum.
- **T36.** 2000 draws at 10 sensors.
  - Ignoring the interference gives 49–62% coverage of the 90% wellfield intervals; the correction gives 88–93%.
  - The forecast error is 25% lower than for the classical network.
  - The corrected heads have an error of 2.9 cm, against 7.6 cm raw.

**Files.**

| File | Content |
|---|---|
| `nderhyrja_exp.py` | The test bed, the criteria, NDERHYRJA-GO, the certificate, the self-checks and T33–T36 → `res/nderhyrja.json`, `res/nderhyrja_case.npz`, `res/nderhyrja_log.txt`. `python3 nderhyrja_exp.py quick` runs a short version (about 40 s; the full run takes about 10 min). |
| `nderhyrja_figs.py` | Figures: the interference scheme and the loop, the test bed with two networks, T33, T34–T35, T36. |
| `text_nderhyrja.py` | The text: the two documents extracted, the state of the art, our scheme, NDERHYRJA-GO with proofs, tests, NATO texts, limitations. |
| `build_nderhyrja_doc.py` | Builds the Word document (OMML equations, clickable links). |
| `run_all.sh` | Runs everything. |

**Output.** `docs/literature/Literature_review_State_of_the_Art_X_Sensor_Placement_Interference_Correction_Robust_Certified_OED_NDERHYRJA-GO.docx`
(17 pages in the LibreOffice render).

**Verification.**
- The robust OED article was read in full from the PDF provided, and the Certified OED framework from the Word file
  provided.
- References R and C are cited as those documents list them; they were not opened here.
- W1 and W2 (barometric correction of groundwater records) were checked against publisher and index records.
