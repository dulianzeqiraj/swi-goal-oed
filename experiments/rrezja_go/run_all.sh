#!/bin/bash
# RREZJA-GO (review 58): needs ../pusi_go/res/ens.npz (run ../pusi_go/pusi_run.py first) and ../vendimi_go/vendimi.py.
set -e
cd "$(dirname "$0")"
OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 python3 rrezja.py > res/run_log.txt 2>&1
python3 rrezja_expost.py > res/expost_log.txt 2>&1
python3 rrezja_figs.py
