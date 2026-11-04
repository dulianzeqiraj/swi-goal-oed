#!/usr/bin/env bash
# GARANCIA-GO: run the tests and build the review (Word, OMML equations, clickable links).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 gar_exp.py > res/run_stdout.txt 2>&1        # T1, T1A, T2, T3, T4  -> res/gar_exp.json, res/gar_case.npz
python3 gar_rcps.py > res/rcps_stdout.txt 2>&1      # T5 (high-probability control)  -> res/gar_rcps.json
python3 gar_rainc.py > res/rainc_stdout.txt 2>&1    # T1R (rain-conditional calibration)  -> res/gar_rainc.json
python3 build_gar_doc.py ../../docs/literature/Literature_review_Inputs_Dispersion_Boundary_Conditions_from_Rain_Oxford_Caltech_Berkeley_MIT_2020-2026.docx
