#!/bin/bash
# MOTI-GO (review 59): needs ../pusi_go/res/ens.npz (run ../pusi_go/pusi_run.py first) and ../vendimi_go/vendimi.py.
set -e
cd "$(dirname "$0")"
mkdir -p res
OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 python3 moti.py > res/run_log.txt 2>&1
python3 moti_figs.py
