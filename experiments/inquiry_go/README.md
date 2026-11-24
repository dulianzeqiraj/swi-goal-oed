# INQUIRY-GO: the decisive question

Code of the proposal *INQUIRY-GO: the decisive question* (24 November 2026, English).

**The question.** ORIGIN-GO (`../zanafilla_go`) and HYPOTHESIS-GO (`../hipoteza_go`) return the set of origins of the
chloride that the data allow. When that set still holds rival explanations, which measurement should be made next?

**The idea.** For every candidate measurement (a *question*) and every rival *verdict* (for instance "the sea supplies at
least half of the chloride of this sample"), compute the outcomes that the verdict can produce: for each simulation of
the ensemble the predictions fill an interval, found by two linear programmes, and the outcome set is the union of
these intervals widened by the tolerance.
- If the outcome sets of the two verdicts do not overlap, the question is *decisive*: whatever it returns, one verdict
  is ruled out (Proposition 1 of the note; it needs the truth to be inside the identified set).
- Otherwise the *decisive share* is the part of the possible outcomes that certify a verdict, and the question with
  the largest share is asked.
- No prior distribution of the source strengths enters.

## Files

| file | what it does |
|---|---|
| `inquiry_poc.py` | proof of concept on the synthetic library of HYPOTHESIS-GO (`../hipoteza_go/res/ensemble.npz`, built by `../hipoteza_go/hip_ensemble.py`): six rules of choosing the next question, one certificate to stop → `res/inquiry_poc.json` |
| `inquiry_figs.py` | the figure of the test |
| `inquiry_text.py`, `build_inquiry_doc.py` | the text and the Word builder (uses `../hipoteza_go/build_hip_doc.py` and `../word_tools`) |
| `fk_inquiry.py`, `fk_inquiry_sum.py` | INQUIRY-GO on the stored Fushë-Kuqe ensemble of HYPOTHESIS-GO (`../hipoteza_go/res_fk`, not committed): mixed-integer programmes with the well positions as binary variables; outcome sets, decisive shares and sharp share bounds by bisection (`python fk_inquiry.py 4`, about half an hour on four cores; `python fk_inquiry.py shares`; `python fk_inquiry_sum.py`). The results are field results and are not committed |
| `root_poc.py` | test of the companion idea ROOT-GO on the synthetic section: basins of the chloride image under steepest ascent with a persistence threshold, the root of each body, comparison with the main source of each point and with the nearest source zone → `res/root_poc.json` (`python root_poc.py 200 4 2027`, three minutes). The result is negative: see the note |
| `fk_squeeze.py` | the companion idea SQUEEZE-GO as a seventh term of the Fushë-Kuqe section: chloride expelled from the compacting cover, with the pattern cover thickness × head decline and one strength; new solves of the head-consistent simulations for its response (`python fk_squeeze.py resp`), then the mixed-integer inference with seven sources (`python fk_squeeze.py infer`). The results are field results and are not committed |
| `fk_ions.py` | two readings of the major ions of four wells (seawater mixing; fresh water plus sodium chloride). It reads the workbook of the chloride manuscript; its output holds field data and is not committed |

Run: `python inquiry_poc.py 40 4 4000 2027` (40 truths, four workers, the whole library; about a quarter of an hour),
then `python build_inquiry_doc.py OUT.docx [IONS.json]`.

## The test

- Truth: one simulation of the library, strengths and signatures drawn in their intervals; deep saline water present
  in half of the truths.
- Known at the start: chloride at four wells (eight samples) and four heads.
- Verdict: does one source supply at least half of the chloride of a saline sample? Taken at the most saline sample
  and for the first source (sea, legacy, deep, anthropogenic, lagoon) for which the starting data leave it open.
- Questions: chloride, bromide, oxygen-18 or tritium at one of the twenty samples (72 candidates, equal cost).
- Rules: random; D-optimal for the six strengths and the variance of the goal share, both from sample pairs with a
  linear-Gaussian fit (the non-intrusive construction of Koval & Nicholson 2025); the widest outcome; INQUIRY (largest
  decisive share); hybrid (the five best by goal variance, then the largest decisive share).

## Limits

The truth is a member of the library (no model error) and the tolerance is not inflated; equal costs; one verdict per
truth. The decisive share measures outcomes by their length. The text of the field sections of the notes is kept
in private modules that are not committed; without them the builder leaves those sections out. Of the companion ideas of the note, ROOT-GO is tested by `root_poc.py` and SQUEEZE-GO by
`fk_squeeze.py`; PHASE-GO and TIME-GO are not implemented.
