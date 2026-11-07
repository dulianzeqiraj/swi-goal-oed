#!/usr/bin/env bash
# SHTEGU-GO: run the tests and build the eleventh state-of-the-art review (Word, OMML equations, clickable links).
# Needs numpy, scipy, matplotlib, python-docx, pandoc, and the helpers of ../garancia_go, ../spiranca_go/certain_coast
# and ../ml_paradigms/word.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 shtegu_exp.py > res/shtegu_stdout.txt 2>&1   # self-checks, T37-T40 -> res/ (about 70 s)
python3 build_shtegu_doc.py ../../docs/literature/Literature_review_State_of_the_Art_XI_Warnings_Between_Samples_Neural_Jump_ODE_Robust_Neural_SDE_SHTEGU-GO.docx
