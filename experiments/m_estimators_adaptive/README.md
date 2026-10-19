# M-estimators on adaptively collected data: simulations and figures

This folder holds the simulations and figure scripts behind the review
*Inference with M-estimators on adaptively collected data: 16 papers 2020–2026, theory, verification and innovations
for coastal-aquifer monitoring* (`docs/literature/Literature_review_M-estimators_Adaptive_Data_2020-2026.docx`).

Every simulation writes one JSON file to `results/`. Every figure script reads that file and writes a PNG and a PDF to
`figures/`. The figures use a white background, no black fills and the shared style in `common.py`. PNG and PDF files are
not tracked by git (see `.gitignore`), so run the figure scripts to regenerate them.

## Scripts, tests and figures

| Simulation | Figure script | Review section | What it shows | Runtime |
|---|---|---|---|---|
| — | `fig_landscape.py` | Fig. 1, Sect. 3 and 5 | Properties of the base paper and the 16 papers (route, setting, estimand, inference, guarantee). The property table in the script is the single source; it also writes `results/landscape.json`. | ~5 s |
| `sim_bandit.py` | `fig_bandit.py` | Figs. 2–3, Sect. 2.6 | Replication of the base paper's two-armed bandit: Wald failure without weights, recovery with the adaptive weights, the variance condition. | ~2 min |
| `sim_n1.py` | `fig_n1.py` | Fig. 4, Test 1 (Proposition 1) | Smoothed continuous design $q_t=(1-\gamma)q^{\mathrm{opt}}+\gamma q^{\mathrm{sta}}$: coverage, the price of stabilization and the pathwise Hessian bound. | ~3–4 min |
| `sim_cs.py` | `fig_cs.py` | Fig. 5, Test 2 (Proposition 2) | Score-martingale confidence sequences; the target of OLS, AW-LS and IPW under misspecification. | ~3 min |
| `sim_aquifer.py` | `fig_aquifer.py` | Fig. 6, Test 3 | Coverage after adaptive monitoring of a synthetic 1-D coastal transect; repeated looks; misspecification by a paleochannel trough. | 9–16 min (2 workers) |
| `sim_eki_conformal.py` | `fig_eki_conformal.py` | Fig. 7, Test 4 | EKI and ES-MDA ensembles in a 2-D zoned coastal aquifer, calibrated by split conformal prediction on held-out piezometers; weighted conformal for clustered calibration wells. | ~7.5 min (`--R 500`) |
| `sim_switchback_ou.py` | `fig_switchback_ou.py` | Fig. 8, Test 5 (Proposition 3) | Adaptive switchback pumping tests on the KAUZ-OED linear aquifer: IPW, naive difference, ARX, confidence sequences, seasonal background. | ~5.5 min |
| `sim_switchback_l96.py` | `fig_switchback_l96.py` | Fig. 9, Test 6 (Proposition 3) | Adaptive switchback tests on Lorenz-96 (chaos), with exact counterfactual branches; comparison with the FDT and regression. | ~13 min (2 workers) |
| `../kauz_oed/kauz_verify.py` | `../kauz_oed/fig_kauz_verify.py` | Fig. 10, Sect. 7 | Adversarial check of KAUZ-OED: theorem on 1000 random systems, oracle vs criterion, finite-record variance, semigroup test, pumping as a parametric perturbation. See `../kauz_oed/README.md`. | ~7 min |

Runtimes were measured on a shared 4-core machine and vary with load.

## How to run

```
cd experiments/m_estimators_adaptive
python3 fig_landscape.py
python3 sim_bandit.py            && python3 fig_bandit.py
python3 sim_n1.py                && python3 fig_n1.py
python3 sim_cs.py                && python3 fig_cs.py
python3 sim_aquifer.py --workers 2 && python3 fig_aquifer.py
python3 sim_eki_conformal.py --R 500 && python3 fig_eki_conformal.py
python3 sim_switchback_ou.py     && python3 fig_switchback_ou.py
OMP_NUM_THREADS=1 python3 sim_switchback_l96.py && python3 fig_switchback_l96.py
cd ../kauz_oed && python3 kauz_verify.py && python3 fig_kauz_verify.py
```

Requirements: Python 3 with NumPy, SciPy and Matplotlib (SymPy is optional, for the symbolic checks in `kauz_verify.py`).
All random seeds are fixed in the scripts, so the JSON files are reproducible up to floating-point differences
between BLAS builds.

## Naming

The script docstrings use the working names of the proposals: N1 (smoothed design, Proposition 1), N2 (confidence
sequences and misspecification, Proposition 2), N3 (adaptive monitoring on a transect) and N4 (EKI + conformal). In the
review these appear as Tests 1–4 of PESHA-GO, and the two switchback studies as Tests 5–6.
