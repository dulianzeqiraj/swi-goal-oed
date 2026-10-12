# PRAG-GO and PRAG-MAR on the Fushë-Kuqe field model

Threshold-risk goal-oriented design ("PRAG-GO") on the project's Fushë-Kuqe design model
(`src/fushe_kuqe_field_design.m`), and its extension to managed aquifer recharge ("PRAG-MAR").

The project selects monitoring wells that are informative about the modelled intruded area,
and MAR sites that shrink it. These scripts ask whether the same wells and sites serve the
regulatory question "will a supply well be salinized?". The test uses the exact,
non-linearized expected information gain over every design. A supply well counts as intruded
when the Ghyben–Herzberg interface reaches the aquifer base beneath it, i.e. `h < delta * base = 1.0 m`.

Requirements: Python 3 with NumPy, SciPy, pandas and openpyxl; matplotlib for `fk_figs.py`.
Run from this folder. The scripts read the repository's `data/Fushe_Kuqe_All_Data.xlsx`, or a
copy placed in this folder. The data belong to the Albanian Geological Survey and A. Beqiraj;
see `data/README.txt` for attribution and terms.

## Files

| File | What it does |
|---|---|
| `fk.py` | Python port of `src/fushe_kuqe_field_design.m`. It covers the real polygon, IDW conductivity, the western coast at h = 0, confined flow, the 12 pilot zones with the facies prior, the marginal EIG and MAR fields, and top-k selection with snapping. `python3 fk.py` reproduces the published numbers: 5 589 active cells, intruded area 92.7 km², monitoring P21, A12, A13, A21, A10 and MAR A18, P21, P16. |
| `fk_ens.py` | Stage 1 builds 12 000 + 2 000 prior realizations of the heads at the 32 inside wells and of the intruded area. Stage 2 is the project's linearization at the prior mean. Priors: `base` (published), `rho805` (field cross-facies correlation) and `fine` (50 zones, correlation length 3 km). |
| `fk_designs.py` | Selects the supply wells A and B (rule in the docstring) and computes the exact EIG of three binary goals by likelihood re-weighting. It covers all 4 060 three-well designs. For five-well designs it scores all 142 506 with every criterion, then evaluates exactly a pool of 3 000 random designs plus each criterion's top 200, and runs greedy and swap searches on the exact EIG. |
| `fk_conv.py` | Re-estimates the three-well picks on independent halves of the ensemble. |
| `fk_check5.py` | Re-estimates the five-well picks with a 4x larger inner ensemble (48 000). |
| `fk_mar.py` | PRAG-MAR. It derives the closed-form risk gradient from two adjoint solves and compares, on 2 000 realizations, the published MAR sites, the PRAG-MAR sites and the greedy optimum of the exact ensemble risk. |
| `fk_figs.py`, `fk_results.py` | Figures and the summary table `results_summary.csv`. |

## Run

```bash
python3 fk.py                                   # reproduction check, ~4 s
python3 fk_ens.py res_base base                 # ~1 min on 4 cores
python3 fk_designs.py res_base                  # ~20 min on 4 cores
python3 fk_conv.py res_base; python3 fk_check5.py res_base base
python3 fk_mar.py                               # ~1 min
# other priors (after base, which fixes the supply wells): rho805, fine
python3 fk_results.py; python3 fk_figs.py fig
```
