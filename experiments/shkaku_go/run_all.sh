#!/usr/bin/env bash
# SHKAKU-GO: run the tests and build the seventh state-of-the-art review (Word, OMML equations, clickable links).
# Needs ../dyshemeja_go, ../ankora_go, ../reshja_go, ../matja_go, ../garancia_go, ../prirja_go, ../shiu_go and ../rindertimi_go.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 shkaku_exp.py > res/shkaku_stdout.txt 2>&1      # T21-T24 -> res/shkaku.json (about 45 min)
python3 shkaku_sign.py                                   # side checks on the twins -> res/shkaku_sign.json
python3 build_shkaku_doc.py ../../docs/literature/Literature_review_State_of_the_Art_VII_Counterfactuals_Stochastic_Causality_Inputs_Dispersion_Boundary_Conditions_SHKAKU-GO_Oxford_Caltech_Berkeley_MIT_2022-2026.docx
