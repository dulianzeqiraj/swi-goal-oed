#!/usr/bin/env bash
# NDERHYRJA-GO: run the tests and build the tenth state-of-the-art review (Word, OMML equations, clickable links).
# Needs numpy, scipy, matplotlib, python-docx, pandoc, and the helpers of ../garancia_go, ../rindertimi_go,
# ../spiranca_go/certain_coast and ../ml_paradigms/word.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 nderhyrja_exp.py > res/nderhyrja_stdout.txt 2>&1   # self-checks, T33-T36 -> res/ (about 10 min)
python3 build_nderhyrja_doc.py ../../docs/literature/Literature_review_State_of_the_Art_X_Sensor_Placement_Interference_Correction_Robust_Certified_OED_NDERHYRJA-GO.docx
