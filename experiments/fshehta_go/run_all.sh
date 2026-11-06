#!/usr/bin/env bash
# FSHEHTA-GO: run the tests and build the ninth state-of-the-art review (Word, OMML equations, clickable links).
# Needs numpy, scipy, matplotlib, python-docx, pandoc, and the helpers of ../garancia_go, ../rindertimi_go,
# ../spiranca_go/certain_coast and ../ml_paradigms/word.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 fshehta_exp.py > res/fshehta_stdout.txt 2>&1   # T29-T32 -> res/fshehta.json, res/fshehta_case.npz (about 6 min)
python3 build_fshehta_doc.py ../../docs/literature/Literature_review_State_of_the_Art_IX_Time_Series_Deconfounder_Hidden_Confounders_Pumping_Salinity_FSHEHTA-GO_Oxford_Caltech_Harvard_MIT_2020-2026.docx
