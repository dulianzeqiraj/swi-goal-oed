#!/usr/bin/env bash
# RESHJA-GO: run the tests and build the third state-of-the-art review (Word, OMML equations, clickable links).
# Needs ../matja_go (test bed wrapper), ../garancia_go (CRC helpers, review I results) and ../rindertimi_go.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 reshja_exp.py > res/reshja_stdout.txt 2>&1      # T9, T10, T11  -> res/reshja.json (about 5 min)
python3 build_reshja_doc.py ../../docs/literature/Literature_review_State_of_the_Art_III_Rain_Uncertainty_Inputs_Dispersion_Boundary_Conditions_RESHJA-GO_Oxford_Caltech_Berkeley_MIT_2020-2026.docx
