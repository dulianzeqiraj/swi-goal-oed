# SWI-Goal-OED

**Goal-oriented Bayesian optimal experimental design (OED) for variable-density
seawater intrusion**, with a discrete-adjoint information operator, a facies
poolability *phase boundary*, and a field application to the Fushë-Kuqe coastal
aquifer (Albania).

Reference code for:

> Zeqiraj, D. *Goal-Oriented Bayesian Experimental Design for Variable-Density
> Seawater Intrusion* (submitted to *Journal of Hydrology*, 2026).

The pipeline selects monitoring/managed-aquifer-recharge (MAR) locations that
maximize the expected information gain (EIG) about a scalar prediction goal
(e.g. salt mass near the intrusion toe), using two adjoint solves that share a
single Jacobian, a facies-conditioned log-conductivity prior, and a cost-aware
greedy design.

---

## Requirements

* **MATLAB R2019a or newer** (uses `readmatrix`). **Base MATLAB only — no
  toolboxes required.** Optional `exportgraphics` (R2020a+) degrades gracefully
  to `print`.
* GNU Octave runs the linear-Gaussian core and the phase-boundary demo;
  the variable-density solves are slow in Octave and the Fushë-Kuqe scripts need
  MATLAB's `readmatrix` for the `.xlsx` dataset.

No installation: add `src/` (and `demo/`) to the path, or just run from the
repository root.

---

## Reproducibility map

Every reported result maps to one script and a verified number. Numbers below
are the exact values printed by the scripts (linear-Gaussian results are exact;
PDE results are mesh-dependent and the figure-grid value is quoted).

| Manuscript item | Script | Verified output |
|---|---|---|
| **Gate 1**, discrete-adjoint gradient check, article value | `demo/gate1_production_solver.m` | min rel. error **4.38e-9** at delta = 3e-8, h in {1e-3,1e-4,1e-5} → PASS (tol 1e-5) |
| Gate 1 on the 11x6 prototype finite-element solver | `demo/gate1_henry_vd.m` | min rel. error 7.46e-6 (different solver and mesh) |
| Full pipeline + Gate 1 (validated solver) | `demo/demo_internal.m` | Gate 1 PASS (~7.6e-6) |
| **Gate 2**, Henry benchmark, article value | `figures/make_fig_henry.m` | toe **1.3918 m** (0.696·L) at 41x21; residual ‖R‖ = 3.5e-14 |
| Gate 2 on the finite-element solver, independent check | `demo/gate2_henry.m` | toe ≈ 1.3776 m (0.689·L); residual ‖R‖ ≈ 6.9e-8 |
| **Gate 3** — facies diagnostic (field) | `demo/gate3_field.m` | ρ_c = **0.762**, ρ_F = 0.805; facies-aware vs blind EIG **0.595 vs 0.537 nats** (≈10% gain); pooling loss **19.0%** |
| **Lemma 1** — EIG ≡ mutual information | `demo/demo_synthetic.m` | EIG = MI to machine precision |
| **Fig. 1** — conceptual workflow | drawn outside MATLAB; `figures/make_fig1_workflow.m` renders the same pipeline as a sketch | schematic |
| **Fig. 2** — poolability phase boundary | `demo/demo_phase_boundary.m` | ρ_c = **0.762**, L_max = **0.0769 nats** (19.0% of pooled EIG), dead zone = 0 |
| **Fig. 3** — structural invariance | `demo/demo_phase_boundary.m` | ρ_c = 0.762 invariant for n_k = 4, 8, 16 (data collapse) |
| **Fig. 4**, Henry benchmark and mesh refinement | `figures/make_fig_henry.m` | toe 1.4226, 1.3971, 1.3918, 1.3864, 1.3838 m at 16x8, 32x16, 41x21, 61x31, 81x41 |
| **Fig. 5**, hydrogeological cross-section of the field site | `figures/make_cross_section.m` | conceptual section plus measured K against distance from the coast, 32 wells inside the polygon |
| **Fig. 6**, well map and facies classes | `figures/make_fig_wellmap.m` | 43 wells with a K measurement, 32 inside the 349 km² polygon, classes 11 / 14 / 7 |
| **Fig. 7**, EIG and MAR effectiveness maps | `demo/fushe_kuqe_eig_map.m` | goal-oriented EIG and MAR fields on the shared grid |
| **Fig. 7**, selected design | `demo/fushe_kuqe_design.m` | 5 monitoring + 3 MAR sites; baseline intruded area ≈ 92.7 km² |
| PRAG-MAR checks (risk-oriented MAR, new) | `demo/prag_mar_selftest.m` | prints PASS or FAIL for five checks: bivariate normal CDF, published design unchanged, adjoint vs direct solves, closed-form gradient vs central difference, vectorized operator vs assembler |
| PRAG-MAR on the field (new) | `demo/fushe_kuqe_prag_mar.m` | supply wells A23, R16; PRAG-MAR sites A23, R16, P21 vs published A18, P21, P16; at 5 000 m³/day per site P(A or B intruded) 0.79 → 0.04 vs 0.62 (reference values from the Python port in `experiments/prag_go_fushe_kuqe`; Monte Carlo, 2 000 realizations) |
| PRAG-MAR with the geolocated sea boundary | `chloride_fk/matlab/fkcl_prag_mar.m` | sea contact only on the northern 23 km of the margin (chloride study): no well at risk without pumping; supply wells A1, P10 of the Fushë-Kuqe field pumped to P = ½ each; at 5 000 m³/day per site P(A or B intruded) 0.56 → 0.06 with PRAG-MAR vs 0.31 (area adjoint) and 0.53 (published sites); exact optimum 0.04 (Python `experiments/prag_go_fushe_kuqe/fk_mar_geo.py`, same numbers) |
| PRAG-GO with the geolocated sea boundary | `chloride_fk/matlab/fkcl_prag_go.m` (Python: `experiments/prag_go_fushe_kuqe/fk_prag_geo.py`) | same supply wells and pumping; 16 candidate wells, every 3- and 5-well design scored exactly: the PRAG-GO 3-well design is the exact optimum for 'A intruded' and 'A or B intruded'; the area design of the published pipeline reaches 74 % and 52 % of the optimal information (5 wells, re-estimated with 48 000 realizations: 99.6-99.7 % vs 48-69 %) |

> **The porosity factor in the diffusion coefficient.** `src/vd_params.m` used to hold `Dmol = 6.6e-6`, which is Henry’s TOTAL dispersion coefficient, in the slot that `src/vd_residual.m` multiplies by porosity. The coefficient actually in the transport operator was therefore 0.35 x 6.6e-6 = 2.31e-6 and the Henry number was 0.035 rather than 0.1, which put the toe at 1.19 m instead of 1.39 m. Voss (1984, USGS WRIR 84-4369, section 6.5) names this mistake and gives the pair that matches Henry (1964): D = 6.6e-6 m2/s total, Dm = 18.8571e-6 m2/s molecular, with D = phi·Dm. `Dmol` now holds 1.62925/86400 = 1.88571e-5, the same quantity `demo/gate2_henry.m` has always carried as `Dm = 1.62925` m2/day. If you are reading numbers from a checkout older than this commit, they carry the old coefficient.

The `revision_r2/` folder contains the additional analyses of the R2 revision (jackknife uncertainty of ρ_F, ρ_c configuration sweep, facies-threshold sensitivity, intruded-area consistency check, physics-based poolability boundary, Gate-1 robustness, toe refinement); each script writes to `revision_r2/r2_results/`.

Most of these run in seconds. Two do not: `r2_gate2_refine.m` (the mesh-refinement
ladder) takes about an hour, dominated by the 61x31 and 81x41 rungs, and
`r2_gate1_multidir.m` about 15 minutes. Both print what they are doing and write
their results incrementally, and their archived outputs are already in
`revision_r2/r2_results/`, so neither needs to be re-run to read the numbers.

Regenerate every main-text figure with `figures/make_all_figures.m`, or run the
individual scripts listed above; the data-dependent figures (5, 6, 7) are attempted
only if `data/Fushe_Kuqe_All_Data.xlsx` is present.

`demo/henry_benchmark_figure.m` and `demo/section8_design.m` are earlier prototypes
kept for reference. They use a coarser, different discretization and produce
different numbers (a Henry toe near 1.20 m and 1.40 m respectively); no figure or
number of the article comes from them.

> **Figure numbering.** The table follows the manuscript's final numbering;
> if you renumber figures, update the captions and this table together.

---

## Chloride study and decision modules

* `chloride_fk/` — probabilistic chloride maps of the Fushë-Kuqe coastal sector,
  a variable-density section and the goal-oriented chloride sampling design, in
  MATLAB R2026b (base MATLAB, `fkcl_run_all`, `fkcl_selftest`) and in Python. See
  [chloride_fk/README.md](chloride_fk/README.md).
* `experiments/` — numerical tests of the decision modules (PRAG-GO, KRITIK-GO,
  KRAMERS-GO, SAFE-GO, KALIB-GO, ATRIB-GO, TMLE-GO, KUFI-GO, RRJEDHA-GO,
  KANAL-GO, KTHIMI-GO), each with its own README.
* `docs/manuscript/` — the chloride manuscript and its Supplementary Material.

---

## Repository layout

```
src/    core (validated)
  eig_operator.m          goal-oriented information operator + EIG (Lemma 1)
  greedy_design.m         cost-aware greedy design
  facies_prior.m          facies prior  Gamma(rhoF) = D + rhoF*C
  phase_boundary.m        pooling loss L(rhoF), rho_c, dead zone
  adjoint_solve.m         two adjoints sharing J^T  ->  G_F, H_F
  gate1_gradcheck.m       discrete-adjoint gradient check
  assemble_jacobian_fd.m  coupled Jacobian  J = dR/du  (finite differences)
  vd_residual.m           variable-density coupled residual (validated)
  vd_solve_forward.m      tight Picard forward solve
  vd_params.m             physical parameters
  vd_jacobian_fd.m / make_grid.m
  fushe_kuqe_field_design.m   shared confined-flow field model + EIG/MAR fields
                          (optional P.supplyIDs adds the PRAG-MAR field and sites)
  prag_mar.m              PRAG-MAR: closed-form recharge field for the supply-well risk
  prag_mar_check.m        exact prior Monte Carlo evaluation of MAR site sets
  bvn_cdf.m               bivariate normal CDF (base MATLAB)
  my_solver_residual.m    TEMPLATE: wrap YOUR solver into the pipeline
demo/   reproducible entry points (see table above)
figures/
  make_fig1_workflow.m    Fig. 1 schematic
  make_all_figures.m      orchestrator
data/   Fushe_Kuqe_All_Data.xlsx  (field dataset; see data/README.txt)
LICENSE  CITATION.cff
```

Bring-your-own-solver: fill in `src/my_solver_residual.m`, then run
`demo/gate1_with_my_solver.m` to certify your physics on Gate 1.

---

## Data

The Fushë-Kuqe field dataset is **included** in `data/Fushe_Kuqe_All_Data.xlsx`.
These data are the property of the **Albanian Geological Survey** and of
**Arjan Beqiraj**, and are redistributed here **with their permission**.
Source: Albanian Geological Survey (2024); the water-chemistry sheets are
compiled from Cenameri & Beqiraj (2016). Please cite these sources when using
the data; see `data/README.txt` for full attribution and terms.

Sheets used by the scripts:

* `2_All_Wells`  — `ID`, `X_GaussKruger`, `Y_GaussKruger`, `K_m_per_day` (43 wells)
* `3_Boundary_Coords` — `X`, `Y` (aquifer-boundary polygon, 3411 vertices)
* `4_Inside_With_K` — interior nodes with `K`

(The workbook also carries `1_Summary` and the `5_*`/`6_*`/`7_*` Cenameri-2016
chemistry/SWI sheets.) Coordinates are Gauss–Krüger (Krasovsky-1940, zone 4).
Run the field scripts with the bundled file, e.g.

```matlab
fushe_kuqe_design('data/Fushe_Kuqe_All_Data.xlsx')
gate3_field('data/Fushe_Kuqe_All_Data.xlsx')
make_all_figures('figs')          % auto-finds data/Fushe_Kuqe_All_Data.xlsx
```


## Citation

If you use this code, please cite the article and the software (Zenodo DOI 10.5281/zenodo.21841208; see `CITATION.cff`).

## License

MIT — see [LICENSE](LICENSE).
