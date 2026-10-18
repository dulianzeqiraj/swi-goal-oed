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
| `fk_geo.py` | The same model with the geolocated sea boundary of the chloride study (`chloride_fk/`): sea contact only on the 92 rows north of y = 29.5 km, through a link over the GLOBE shoreline gap, on the coastal sector y ≥ 24 km. Physics unchanged. `python3 fk_geo.py`: intruded area 10.1 km² (92.7 km² with the full-margin boundary). |
| `fk_prag_geo.py`, `fk_prag_geo_check.py` | PRAG-GO recomputed on `fk_geo.py` with the supply wells and pumping of `fk_mar_geo.py`: every 2-, 3- and 5-well design of the 16 sector candidates scored exactly; the check re-estimates the 5-well results with 48 000 inner realizations. Writes `res_geo/prag_*`. `fk_prag_geo_export.py` writes the prior draws and noise of the run to `res_geo/prag_draws_<prior>.bin` for the MATLAB port `chloride_fk/matlab/fkcl_prag_go.m`. |
| `fk_mar_geo.py` | PRAG-MAR recomputed on `fk_geo.py` with two pumped supply wells of the Fushë-Kuqe well field (rules in the docstring). Writes `res_geo/`. `python3 fk_mar_geo.py equal` runs the pumping-rule sensitivity. MATLAB port: `chloride_fk/matlab/fkcl_prag_mar.m`. |

## Run

```bash
python3 fk.py                                   # reproduction check, ~4 s
python3 fk_ens.py res_base base                 # ~1 min on 4 cores
python3 fk_designs.py res_base                  # ~20 min on 4 cores
python3 fk_conv.py res_base; python3 fk_check5.py res_base base
python3 fk_mar.py                               # ~1 min
# other priors (after base, which fixes the supply wells): rho805, fine
python3 fk_results.py; python3 fk_figs.py fig
python3 fk_mar_geo.py; python3 fk_mar_geo.py equal   # geolocated boundary, ~30 s each
python3 fk_prag_geo.py base; python3 fk_prag_geo.py rho805; python3 fk_prag_geo_check.py base   # ~10 + 10 + 4 min
```

## PRAG-MAR with the geolocated sea boundary

The companion model treats the whole western margin as the sea. Geolocated against the GLOBE
shoreline, only its northern 23 km touch the Adriatic (see `chloride_fk/`). With that boundary and
the same physics, the intruded area is 10.1 km², confined to the northern coast, and no inside well
is at risk without pumping. The old supply well R16 and two of the three published recharge sites
(A18, P21) lie in the southern plain, which has no sea contact. The full-margin numbers above
(0.79 → 0.04 vs 0.62) therefore do not carry over.

`fk_mar_geo.py` poses the question where the risk now is: two wells of the Fushë-Kuqe well field
(A1 and P10, the inside K-wells with the lowest prior-mean head north and south of section A–A′),
pumped so that each well's own prior intrusion probability is ½. Recharge sites must be at least
1 km from both supply wells; the full-margin run had put two of its three sites in the supply-well
cells themselves. Exact results on 2 000 prior realizations, P(A or B intruded) at 5 000 m³/day per
site:

| Design | Sites | P(A or B) | Mean intruded area (km²) |
|---|---|---|---|
| no recharge | – | 0.559 | 12.9 |
| published sites | A18, P21 (outside the sector), P16 | 0.525 | 11.0 |
| area adjoint, recomputed | northern coast and A3 | 0.305 | 9.2 |
| **PRAG-MAR** | P9, A25, A3 | **0.058** | 11.0 |
| exact optimum (greedy) | A30, A25, A13 | 0.035 | 11.3 |

With one pumping rate at both wells (`equal`), the probability falls from 0.476 to 0.017 with
PRAG-MAR, the same as the exact optimum, against 0.226 for the area design and 0.448 for the
published sites. Each goal calls for its own sites: the area design recharges the northern coast,
where the intrusion is; PRAG-MAR recharges next to the well field.

## PRAG-GO with the geolocated sea boundary

`fk_prag_geo.py` repeats the monitoring test on the same setting: supply wells A1 and P10 pumped as
in `fk_mar_geo.py`; goals "A intruded" (prior probability 0.49), "A or B intruded" (0.57) and
"intruded area of the sector above 12 km²" (its prior median, 0.50); the 16 other inside K-wells of
the sector as candidates, read with a head error of 0.2 m. With 16 candidates every design is scored
exactly. Exact EIG of each criterion's best design, % of the exact optimum (base prior):

| Criterion | A, 3 wells | A or B, 3 wells | A, 5 wells* | A or B, 5 wells* |
|---|---|---|---|---|
| area (published pipeline) | 74 | 52 | 69 | 48 |
| head at A | 100 | 100 | 99.7 | 99.6 |
| PRAG-GO, linearized | 100 | 100 | 99.7 | 99.6 |
| PRAG-GO, normal scores | 100 | 100 | 98.9 | 99.3 |

\* re-estimated with 48 000 inner realizations (`fk_prag_geo_check.py`). The best three-well design
for both supply-well goals is A3, A10, A23, and for the intruded area A3, A10, A13; with five wells
the supply-well optimum is P17, A3, A10, A13, A23 and the area optimum takes A28 in place of P17. With rho_F = 0.805 the numbers change by a few percent. Unlike the full-margin test, the head at A
alone also finds the optimum here: the two pumped wells of the same field are strongly correlated
(r = 0.875), so what matters is aiming the design at the supply wells rather than at the area. For
the area goal every criterion reaches 93-99 %.
