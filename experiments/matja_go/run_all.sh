#!/usr/bin/env bash
# MATJA-GO: run the tests and build the second state-of-the-art review (Word, OMML equations, clickable links).
# Needs ../garancia_go/res/ (run ../garancia_go/run_all.sh first) and ../rindertimi_go (test bed).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 matja_exp.py > res/matja_stdout.txt 2>&1      # T7 greedy paths, fresh scores  -> res/matja.json (about 16 min)
python3 matja_single.py > res/single_stdout.txt 2>&1  # T6 single instruments, signal dof  -> res/matja_single.json
python3 matja_spur.py > res/spur_stdout.txt 2>&1      # T8 law of the spurious value  -> res/matja_spur.json
python3 matja_price.py > res/price_stdout.txt 2>&1    # Remark M3 price rule  -> res/matja_price.json
python3 build_matja_doc.py ../../docs/literature/Literature_review_State_of_the_Art_II_Inputs_Dispersion_Boundary_Conditions_from_Rain_MATJA-GO_Oxford_Caltech_Berkeley_MIT_2020-2026.docx
