#!/usr/bin/env bash
# PRIRJA-GO: run the tests and build the fifth state-of-the-art review (Word, OMML equations, clickable links).
# Needs ../ankora_go, ../reshja_go, ../matja_go, ../garancia_go and ../rindertimi_go.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 prirja_exp.py > res/prirja_stdout.txt 2>&1      # T15, T16, T17 -> res/prirja.json (about 2 min)
python3 build_prirja_doc.py ../../docs/literature/Literature_review_State_of_the_Art_V_Drift_Horizon_Guarantees_Inputs_Dispersion_Boundary_Conditions_PRIRJA-GO_Oxford_Caltech_Berkeley_MIT_2020-2026.docx
