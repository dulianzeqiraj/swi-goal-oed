# ZANAFILLA-GO: where does the chloride come from?

Code and results of the review *Where does the chloride come from?* (November 2026, English):
`docs/literature/Literature_review_Chloride_Origin_Ill-posed_Inverse_ZANAFILLA-GO_Oxford_Caltech_MIT_Princeton_MaxPlanck_Harvard_Berkeley_2020-2026.docx`.
*Zanafilla* is Albanian for origin.

**The question.** The chloride of a coastal well may come from modern seawater, relict seawater, a halite brine,
anthropogenic sources or fresh recharge, and each source calls for a different action. With a few tracers and
end-member signatures known only as ranges, the attribution is an ill-posed inverse problem: a solution may not exist
(a source is missing), it is not unique, and the least-squares answer depends on the signatures one assumes.

**The innovation.** ZANAFILLA-GO returns the *identified set* instead of a point:
1. the set of all fractions, chloride contributions and tracer contributions that reproduce the data within their
   errors, with signatures anywhere in their intervals and with site caps, is an exact polytope (Proposition 1);
2. the share of chloride from each source has sharp bounds given by two linear programmes after the Charnes–Cooper
   transform (Proposition 2);
3. for the set, Hadamard's conditions hold: an empty set is a falsification test (a source is missing), the set is
   unique, and it is Lipschitz-stable in the data by Hoffman's bound (Proposition 3);
4. the intervals cover the truth with probability at least 1 − Σ α_t whatever the prior (Proposition 4);
5. the next action (a tracer at the wells, or the sampling of an end-member) is chosen by the expected gain in
   decidability for the decision at hand (Proposition 5);
6. an amortised neural network (three quantile heads, conformalised) screens fast and is checked against the bounds.

## Files

| file | what it does |
|---|---|
| `zanafilla_core.py` | sources, signature intervals, noise, the synthetic aquifer, the polytope, the bounds (linear and linear-fractional programming), end-member characterisation, the least-squares point inverse, the quantile network and its conformal calibration |
| `zanafilla_exp.py` | E1 identification by tracer set and end-member knowledge; E2 value of actions; E3 network against certificate in the training world and a shifted world; E4 a missing source; E5 the point inverse against the set; E6 check of the bounds against brute force → `res/zanafilla.json` |
| `zanafilla_figs.py` | the seven figures |
| `cards_zanafilla.py`, `text_zanafilla.py`, `build_zanafilla_doc.py` | the cards, the text and the Word builder |
| `fetch_context_refs.py` | Crossref records of the context references → `res/refs_context.json` |
| `res/selected_papers.json` | the records of the thirty papers |

Run: `python zanafilla_exp.py 40 4` (about two minutes on four cores), then
`python build_zanafilla_doc.py OUT.docx`.

## Protocol notes

- The signature intervals and noise levels are illustrative, set from ranges reported in the literature; they are not
  data of Fushë-Kuqe or of any other site.
- A first version of the test, with wider intervals for the sea and the fresh water and without site caps, identified
  nothing with any tracer set (mean width of the modern-seawater share above 0.9 everywhere). The sea and the
  upgradient fresh water can be sampled, so their intervals were narrowed, and the caps of land use and geology were
  added; this is stated in the text. The relict water and the halite brine keep wide intervals.
- The tolerance is 2.5 standard deviations per tracer, so the coverage guarantee of Proposition 4 is at least 0.91 for
  seven tracers.

## Limits

Synthetic aquifer and illustrative signatures; signatures of one source treated as independent across tracers;
transport enters only through the site caps; costs of the actions not modelled.

## WRR draft (folder `wrr/`)

`wrr/` holds the code of the manuscript draft for Water Resources Research: the identified set for general tracers
(coupled signatures, reactive tracers as half-spaces, censored data), the fixed-signature and Bayesian (SMC)
comparators, the synthetic coverage comparison, and the application to the public West Coast Basin data of Land et al.
(2004, USGS SIR 2004-5067). The field data and per-well results are not committed; `wrr/get_data.sh` reproduces them.
