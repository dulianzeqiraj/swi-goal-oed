#!/usr/bin/env bash
# DYSHEMEJA-GO: run the tests and build the sixth state-of-the-art review (Word, OMML equations, clickable links).
# Needs ../ankora_go, ../reshja_go, ../matja_go, ../garancia_go, ../prirja_go and ../rindertimi_go.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 dyshemeja_exp.py > res/dyshemeja_stdout.txt 2>&1      # T18, T19, T20 -> res/dyshemeja.json (about 40 min)
python3 build_dyshemeja_doc.py ../../docs/literature/Literature_review_State_of_the_Art_VI_Floor_Optimality_Inputs_Dispersion_Boundary_Conditions_DYSHEMEJA-GO_Oxford_Caltech_Berkeley_MIT_2020-2026.docx
