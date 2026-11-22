#!/bin/bash
# VENDIMI-GO (review 57): needs ../pusi_go/res/ens.npz (run ../pusi_go/pusi_run.py first).
set -e
cd "$(dirname "$0")"
OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 python3 vendimi.py > res/run_log.txt 2>&1
python3 vendimi_figs.py
