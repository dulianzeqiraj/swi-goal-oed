# Chloride in the Fushë-Kuqe coastal aquifer

Code for the paper *From sparse hydrochemistry to decision-relevant information:
probabilistic chloride mapping and goal-oriented monitoring design for seawater
intrusion in the Fushë-Kuqe coastal aquifer, Albania* (D. Zeqiraj, in preparation),
the companion of Zeqiraj (2026), *J. Hydrol.* 680, 136559.

The study builds a probabilistic chloride map of the coastal sector from four
hydrochemical analyses, two chloride series and documented facts, checks it with a
variable-density section, and selects where and at which depth to sample chloride
next. Everything is implemented twice: in MATLAB (base MATLAB, written for R2026b)
and in Python. Given the same random draws, the two agree to round-off.

## Run it in MATLAB R2026b

```matlab
cd chloride_fk/matlab
ok = fkcl_selftest();   % six checks, about one minute; prints PASS or FAIL for each
R  = fkcl_run_all();    % everything: about 4 min, plus 10-20 min for the six sections
```

* `fkcl_run_all(struct('sections', 'quick'))` solves only the median section;
  `'none'` skips the sections.
* Outputs go to `chloride_fk/results_matlab/` (MAT file, `hydrochem.csv`,
  `post_cells.csv`, `report.txt` with the Python numbers alongside) and to
  `chloride_fk/figures_matlab/` (Figs. 1-8 as PNG at 600 dpi and as PDF).
* To redraw the figures without rerunning:
  `fkcl_figures(load('../results_matlab/fkcl_results.mat'))`.
* By default the random inputs come from `results/calib_prior_draws.csv` and
  `results/post_idx.csv` (the draws of the Python run), so the numbers match the
  paper. `fkcl_run_all(struct('src', 7))` draws its own with seed 7.
* `out = fkcl_boundary_figure()` draws Fig. 9 (the full-margin and the geolocated sea boundary of the
  design model) to `figures_matlab/fig9_boundary` in a few seconds and prints the three intruded areas of
  Section 4.7 (92.7, 10.1 and 11.6 km²). It reads the pumping rates of `fkcl_prag_mar` from
  `experiments/prag_go_fushe_kuqe/res_geo/mar_geo.json` (or `struct('QA', ..., 'QB', ...)`).
* `out = fkcl_prag_mar()` recomputes PRAG-MAR (risk-oriented recharge siting) with the
  geolocated sea boundary, in about a minute; it reproduces
  `experiments/prag_go_fushe_kuqe/fk_mar_geo.py` exactly from the same prior draws and draws
  Supplementary Fig. S1 to `figures_matlab/`.
* `out = fkcl_prag_go()` recomputes PRAG-GO (threshold-risk monitoring design) with the
  same boundary, supply wells and pumping: every 2-, 3- and 5-well design of the 16 sector
  candidates is ranked by the eight criteria and scored by its exact EIG. With the prior draws
  exported by `experiments/prag_go_fushe_kuqe/fk_prag_geo_export.py`
  (`res_geo/prag_draws_base.bin`, used by default) it reproduces `fk_prag_geo.py` and prints
  the largest difference (4.4e-6, from single-precision sums); it draws Supplementary Fig. S2 to
  `figures_matlab/`. In GNU Octave 8.4 on one core it takes about 8 minutes for 2 and 3 wells and
  about 55 more for the 4 368 five-well designs (`struct('budgets', [2 3])` skips them); MATLAB
  is faster. About 2 GB of memory.
* `out = fkcl_prag_go(struct('prior', 'rho805'))` repeats it with the field cross-facies
  correlation rho_F = 0.805 (the robustness columns of Supplementary Table S12): it reads
  `res_geo/prag_draws_rho805.bin`, compares with `res_geo/prag_rho805.json` and writes
  `figures_matlab/figS2_prag_go_geo_rho805`. No 48 000-realization re-check exists for this
  prior, so the five-well marks of that figure come from the run itself (12 000 realizations).
  The prior name is checked ('base' or 'rho805'); double-quoted MATLAB strings are accepted.
* Only base MATLAB is used: no toolboxes. `fkcl_prag_mar` also uses `src/prag_mar.m` and
  `src/bvn_cdf.m` from the repository.

**GNU Octave 8** runs the same code. Octave has no `readcell`, so first export the
workbook sheets to TSV, from the repository root (the code looks in `chloride_fk/tsv`
by default; another folder can be given as `struct('tsvdir', ...)`):

```bash
python3 chloride_fk/python/fkcl_export.py --tsv chloride_fk/tsv
```
```matlab
R = fkcl_run_all();
```

## Run it in Python

Python 3.10+ with numpy, scipy, pandas, openpyxl and matplotlib; `fkcl_geo.py`
also needs pyproj and global-land-mask.

| Step | Script | Writes |
|---|---|---|
| 1 shoreline and places (GLOBE land mask) | `fkcl_geo.py` | `derived/*.csv` |
| 2 hydrochemistry | `fkcl_hydrochem.py` | `results/hydrochem.json` |
| 3 calibration (20 000 draws) | `fkcl_calib.py` (`FKCL_VARIANT=shallow` for the variant) | `results/calib_ensemble.npz`, `calib_summary.json` |
| 4 posterior ensemble (2000 members) | `fkcl_post.py` | `results/post_ensemble.npz` (146 MB, not in git), `post_cells.csv`, `post_summary.json` |
| 5 shared draws for MATLAB | `fkcl_export.py` | `results/calib_prior_draws.csv`, `post_idx.csv` |
| 6 sampling design | `fkcl_design.py` | `results/design_summary.json`, `design_candidates.csv`, `eigfield_*.npy` |
| 7 variable-density sections | `fkcl_section.py` | `results/section_*.npz`, `section_summary.json` |
| 8 sensitivity of the calibration | `fkcl_sensitivity.py` | `results/calib_sensitivity.json` |
| 9 figures | `fkcl_figs.py` | `figures/fig1-8` (PNG, PDF) |
| 10 Fig. 9 (sea boundaries; needs `res_geo/mar_geo.json`) | `../../experiments/prag_go_fushe_kuqe/fk_geo_figs.py ../figures --paper` | `figures/fig9_boundary` (PNG, PDF), `res_geo/boundary_areas.json` |

Run the scripts from `chloride_fk/python/` in this order. Step 4 needs step 3, and
steps 6-7 need step 4.

## Where each result comes from

| Paper | MATLAB | Python |
|---|---|---|
| Sea contact (Section 2.3, Fig. 2a) | `fkcl_model_init.m` | `fkcl_geo.py`, `fkcl_model.py` |
| Hydrochemistry (Table 3, Fig. 3) | `fkcl_hydrochem.m` | `fkcl_hydrochem.py` |
| Calibration (Table 2, Fig. 4) | `fkcl_calibrate.m`, `fkcl_loglik.m`, `fkcl_summaries.m` | `fkcl_calib.py` |
| Sensitivity (Supplementary Table S4) | not ported | `fkcl_sensitivity.py` |
| Chloride maps and areas (Fig. 5) | `fkcl_posterior.m` | `fkcl_post.py` |
| Variable-density section (Fig. 6) | `fkcl_section.m`, `fkcl_vd_*.m`, `fkcl_henry_check.m` | `fkcl_section.py`, `fkcl_vd.py` |
| Sampling design (Table 4, Fig. 7) | `fkcl_design.m` | `fkcl_design.py` |
| Decision modules (Table 5, Fig. 8) | `fkcl_figures.m` reads the module results | `../experiments/*` |
| Sea boundaries and threshold risk at the well field (Section 4.7, Fig. 9, Tables 6-7) | `fkcl_boundary_figure.m`, `fkcl_prag_go.m`, `fkcl_prag_mar.m` | `../experiments/prag_go_fushe_kuqe/fk_geo_figs.py --paper`, `fk_prag_geo.py`, `fk_prag_geo_check.py`, `fk_mar_geo.py` |
| PRAG-MAR, geolocated boundary (Supplementary Fig. S1, Tables S9-S10) | `fkcl_prag_mar.m` | `../experiments/prag_go_fushe_kuqe/fk_mar_geo.py` |
| PRAG-GO, geolocated boundary (Supplementary Fig. S2, Tables S11-S12) | `fkcl_prag_go.m` | `../experiments/prag_go_fushe_kuqe/fk_prag_geo.py`, `fk_prag_geo_check.py` |

## The model in brief

* **Sea contact.** Only rows whose western edge lies within 5 km of the GLOBE
  shoreline drain to the Adriatic: 92 cells (23 km) north of y = 29.5 km. The
  southern western margin is inland.
* **Areal model.** Strack single potential with recharge, φ = 0 at the shoreline
  through a Robin link over the shoreline gap; a sharp interface with a dispersive
  transition zone of half-width w; chloride averaged over three 40 m screens (top,
  mid-thickness, base). Sector y ≥ 24 km, 3545 cells of 0.25 km.
* **Calibration.** Importance weighting of 20 000 prior draws against four
  documented facts; the central analysis (well 340) is held out.
* **Section.** Steady variable-density flow and transport in the
  equivalent-freshwater-head form; reproduces the repository's Henry ladder.
* **Design.** Linear (ensemble) and exact (binned mutual information) EIG of
  log10 chloride samples about the area with chloride above 250 mg/L; greedy,
  pairwise-greedy (SINERGO), swap and exhaustive searches.

## Data

The workbook `data/Fushe_Kuqe_All_Data.xlsx` belongs to the Albanian Geological
Survey and A. Beqiraj and is redistributed with their permission; the chemistry
sheets come from Cenameri and Beqiraj (2016), *Bull. Geol. Soc. Greece* 50(2),
665-670. The column labelled piezometric level is read as the DRASTIC depth to the
top of the confined aquifer (Section 2.4 of the paper). The four analysed wells have
no coordinates in the workbook; they enter the calibration as band averages.

## License

MIT, as the rest of the repository.
