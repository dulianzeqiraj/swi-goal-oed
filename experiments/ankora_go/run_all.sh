#!/usr/bin/env bash
# ANKORA-GO: run the tests and build the fourth state-of-the-art review (Word, OMML equations, clickable links).
# Needs ../reshja_go, ../matja_go, ../garancia_go and ../rindertimi_go.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 ankora_exp.py > res/ankora_stdout.txt 2>&1      # T12, T13, T14  -> res/ankora.json (about 1 min)
python3 build_ankora_doc.py ../../docs/literature/Literature_review_State_of_the_Art_IV_Simulator_Shift_Anchors_Inputs_Dispersion_Boundary_Conditions_ANKORA-GO_Oxford_Caltech_Berkeley_MIT_2020-2026.docx
