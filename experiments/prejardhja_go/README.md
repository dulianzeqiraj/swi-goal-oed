# PREJARDHJA-GO: deciding how to meet the demand when nobody knows where the chloride comes from

Code and results of **State of the art V** (November 2026, English):
`docs/literature/Literature_review_Stakeholder_Decisions_V_Unknown_Chloride_Source_PREJARDHJA-GO_Oxford_Caltech_Harvard_MIT_2020-2026.docx`.
It is the fifth review of stakeholder decisions, after reviews I–IV. *Prejardhja* is Albanian for provenance.

The review does three things:
- it presents thirty papers from Oxford (12), Caltech with JPL (6), Harvard (5, one joint with MIT) and MIT (7),
  2020–2026, found and verified through Crossref (DOI, affiliation strings, abstract). None is used in the 72 earlier
  reviews; ten first choices were replaced for that reason. Each card ends with an innovation step for our problem
  (`cards_prejardhja.py`);
- it sets out the state of the art in four strands and the gap (`text_prejardhja.py`, Section 4);
- it presents and tests PREJARDHJA-GO (`prejardhja_exp.py`).

**The question.** The chloride of a coastal well field rises. The source may be:
- the sea (SWI);
- deep brine drawn up under the wells (UP);
- a drought (DRY);
- return flow and wastewater (ANT).

Each source calls for a different action. How should the utility, households and tourism, farmers, the environment
agency and the regulator decide before the source is known?

**Test bed** (illustrative numbers):
- **Supply.** Demand of 12 hm³ per dry season from a coastal field A (a wetland loses flow above 6 hm³), an inland
  field B (above 4 hm³ the water is taken from the farmers), a deep field C, and an alternative supply X (5 hm³ at most).
- **Limit.** The blend must stay below 250 mg/L.
- **Sources.** Four stories fit today's chloride exactly. Each has its own drift and linear response to pumping, with a
  Gaussian dry-season spread.
- **Tests.** Four tracer tests: T1 Br/Cl, T2 isotopes, T3 depth profiles, T4 nitrate–boron.
- **Search and prior.** Allocations are searched exactly on a 0.25 hm³ grid. The planning prior favours the sea
  (0.55 / 0.15 / 0.20 / 0.10).

**PREJARDHJA-GO.**
- C1: the plausible-source set from e-values, $E_k = \frac{1}{K-1}\sum_{j\ne k} p_j/p_k < 1/β$. It contains
  the true source with probability ≥ 1 − β for any sample size and with no prior. It equals a flat-posterior
  threshold β/(K − 1 + β) and is never empty.
- C2: the least-cost allocation with $P_k$(blend > 250) ≤ α for every source in the set, so the risk is ≤ α + β
  whatever the source.
- C3: tests and the split of δ = α + β chosen by the expected cost of the decision; the prior is used only here.
- C4: monthly e-values multiply, so the bound holds at any data-dependent month (Ville's inequality).
- C5: the stakeholders' ledger (utility, households, farmers, wetland, tests) and the price of safety.
- Robust e-value (universal inference) for drifting end-members; pairwise mixtures as hypotheses (Proposition 5).

## Results (`res/prejardhja.json`, 20,000 data sets per case)

P1, exceedance probability for each true source (budget δ = 0.10) and expected cost. PREJARDHJA-GO
buys T1 + T2 + T3 + T4 with β = 0.03, α = 0.07:

| Policy | SWI | UP | DRY | ANT | Cost |
|---|---|---|---|---|---|
| oracle (knows the source) | 8.3% | 9.7% | 9.8% | 5.4% | 2.87 M€ |
| assume seawater intrusion | 8.3% | 91.3% | 82.2% | 97.9% | 2.75 M€ |
| Bayes, prior only | 1.4% | 19.6% | 27.4% | 5.6% | 3.75 M€ |
| worst case, no tests | 0.1% | 1.2% | 8.9% | 1.3% | 4.16 M€ |
| most probable source after tests | 9.6% | 16.5% | 13.6% | 9.2% | 3.06 M€ |
| Bayes posterior after tests | 7.9% | 10.3% | 12.2% | 5.0% | 3.10 M€ |
| **PREJARDHJA-GO** | 4.8% | 6.1% | 6.8% | 4.2% | 3.31 M€ |

- **P0, acting on the wrong story.**
  - Exceedance reaches 100%.
  - Today's pumping exceeds the limit with probability SWI 99%, UP 60%, DRY 98%, ANT 78%.
- **C1 set.** Coverage is ≥ 99.8% (bound 97%). The set
  is never empty and equals the flat-posterior threshold in every data set.
- **P2, test choice.**
  - Best bundle T1 + T2 + T3 + T4; net value 854 k€.
  - Rank correlation between information gain and decision value: 0.99. If the brine rises under A, so
    that SWI and UP ask for the same action, it is 0.85.
  - At equal budget, choosing by information loses up to 47 k€ and 116 k€.
- **P3, risk split and ledger.**
  - Best β = 0.03.
  - The cost of not knowing the source (PREJARDHJA-GO minus oracle) is 436 k€, against
    1289 k€ for the worst case.
- **P4, monthly monitoring.**
  - The true source is ever dropped in 1.1%–1.4%
    of cases, against 21%–22% for an
    ordinary test repeated every month.
  - Exceedance at a data-dependent stopping month is ≤ 4.9%.
- **P5, mixtures.**
  - A half-sea, half-upconing truth breaks the pure list (16.8%); Bayes reaches
    35% and the most probable source 49%.
  - With mixtures admitted (22 hypotheses), exceedance is ≤ 1.2%.
    The cost is 4.15 M€ with one campaign, and it falls with more campaigns.
- **P5, drifted signatures.**
  - With signatures drifted 1 sd towards a rival, coverage drops to 91.6%.
  - The robust e-value restores ≥ 100.0%.
- **P6.** 640 cells (16 bundles × 10 splits × 4 sources), 0 violations; the largest
  exceedance is 8.9%.

## Files

| File | What it does |
|---|---|
| `prejardhja_exp.py` | P0–P6 → `res/prejardhja.json` (about 90 s) |
| `prejardhja_figs.py` | the eight figures |
| `cards_prejardhja.py` | the thirty paper cards |
| `text_prejardhja.py` | the text, with every number read from the results |
| `build_prejardhja_doc.py` | the Word document: OMML equations, links; needs pandoc and the helpers of `../garancia_go`, `../spiranca_go/certain_coast` and `../ml_paradigms/word` |
| `run_all.sh` | runs everything |
