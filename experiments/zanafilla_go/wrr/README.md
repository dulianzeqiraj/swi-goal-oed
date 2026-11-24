# ZANAFILLA-GO for Water Resources Research: certified chloride-source attribution with uncertain end-members

Code of the manuscript draft *Certified Attribution of Chloride Sources in Coastal Aquifers With Uncertain End-Members*
(November 2026). It extends ZANAFILLA-GO (the review in `..`) to general tracers and applies it to public field data.

**What is new relative to the review.**
1. A general identified set (`field_model.py`): any number of sources; chloride-weighted and water-weighted tracers;
   coupled signatures (deuterium excess) through the perspective of a polytope; reactive tracers as half-spaces
   (iodide may only be gained, boron may only be lost); censored values as intervals; site caps.
2. Two comparators on the same model: fixed signatures (IsoSource-type ranges) and a Bayesian mixing model with a
   Dirichlet prior, sampled exactly by sequential Monte Carlo (adaptive tempering, random-walk Metropolis in
   additive-log-ratio and logit coordinates).
3. A field application to the West Coast Basin, Los Angeles (Land et al., 2004, USGS SIR 2004-5067): identified
   intervals of the seawater, brine, imported-water and native shares of chloride for 80 samples, the falsification
   test with a tracer-by-tracer diagnosis, nested tracer sets, and a retrospective test of the design rule.

## Files

| file | what it does |
|---|---|
| `get_data.sh` | downloads the public report and runs the two parsers (data go to `data/`, not committed) |
| `parse_appA.py`, `parse_table2.py` | extract Appendix A (word coordinates of the PDF) and Table 2 of the report |
| `field_model.py` | the polytope, sharp share bounds (Charnes–Cooper), feasibility, fixed signatures, the SMC sampler |
| `field_data.py` | the four sources and the rules for their intervals; measurement errors; charge-balance check |
| `field_exp.py` | F1 bounds; F2 nested tracer sets; F3 falsification and sensitivity; F4 comparators; F5 next action → `res_field/field.json` (not committed) |
| `synth_compare.py` | E7 coverage of the three answers in the synthetic aquifer of the review → `res/wrr_synth.json` |
| `fetch_refs_wrr.py` | Crossref records of the references → `res/refs_wrr.json` |
| `wrr_figs.py`, `text_wrr.py`, `build_wrr_doc.py` | figures, text and the Word builder |

Run: `./get_data.sh`, then `python field_exp.py 4` (about eight minutes on four cores), `python synth_compare.py 15 4`
(about six minutes), `python build_wrr_doc.py OUT.docx`.

## Data policy

The field data are public (U.S. Geological Survey) but they are well data, so neither the data nor the per-well
results are committed (`.gitignore`: `data/`, `res_field/`). `get_data.sh` reproduces them from the public report.

## Protocol notes

- The extraction was checked by the charge balance of the samples with complete major ions. For the six Hawthorne-1
  samples the printed cation columns of Appendix A repeat the anion values; major ions are not used in the paper.
- Bromide and iodide values flagged in Table 2 as affected by colorimetric interference are treated as missing.
- Two interval rules were changed after a first run, and the change is stated in the paper: the native iodide
  interval starts at zero (iodide can only be gained, so the recharge may carry none), and the upper end of the
  imported-water tritium was raised from 30 to 100 TU (bomb-era injection water).
- A first Bayesian comparator by importance sampling from the prior degenerated (effective sample size near one); it
  was replaced by the SMC sampler.
