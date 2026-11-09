#!/usr/bin/env bash
# PERTEJ-GO: run the six numerical checks and build the theory note (Word, OMML equations, clickable links).
# Needs numpy, scipy, matplotlib, python-docx, pandoc, and the helpers of ../garancia_go, ../rindertimi_go,
# ../spiranca_go/certain_coast and ../ml_paradigms/word.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 pertej_exp.py > res/pertej_stdout.txt 2>&1   # N1-N6 -> res/pertej.json, res/pertej_series.npz (about 2 min)
python3 build_pertej_doc.py ../../docs/research_notes/PERTEJ-GO_Transparent_Learnable_Boundary_Flow_Equation.docx
