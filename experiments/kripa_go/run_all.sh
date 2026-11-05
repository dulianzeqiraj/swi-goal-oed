#!/usr/bin/env bash
# KRIPA-GO: run the tests and build the eighth state-of-the-art review (Word, OMML equations, clickable links).
# Needs ../../chloride_fk (model, results/calib_ensemble.npz) and the figure helpers of ../garancia_go and ../rindertimi_go.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 kripa_exp.py > res/kripa_stdout.txt 2>&1      # T25-T28 -> res/kripa.json, res/kripa_maps.npz (about 3 min)
python3 build_kripa_doc.py ../../docs/literature/Literature_review_State_of_the_Art_VIII_Salinity_Counterfactuals_Dispersion_Inputs_Boundary_Conditions_KRIPA-GO_Oxford_Caltech_Berkeley_MIT_2022-2026.docx
