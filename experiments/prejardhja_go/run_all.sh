#!/usr/bin/env bash
# PREJARDHJA-GO: run the tests and build State of the art V (Word, OMML equations, clickable links).
# Needs numpy, scipy, matplotlib, python-docx, pandoc, and the helpers of ../garancia_go, ../rindertimi_go,
# ../spiranca_go/certain_coast and ../ml_paradigms/word.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 prejardhja_exp.py > res/prejardhja_stdout.txt 2>&1   # P0-P6 -> res/prejardhja.json (about 90 s)
python3 build_prejardhja_doc.py ../../docs/literature/Literature_review_Stakeholder_Decisions_V_Unknown_Chloride_Source_PREJARDHJA-GO_Oxford_Caltech_Harvard_MIT_2020-2026.docx
