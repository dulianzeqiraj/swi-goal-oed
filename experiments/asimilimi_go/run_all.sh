#!/bin/bash
# ASIMILIMI-GO: numerical checks of the data-assimilation note (about 3 minutes on 4 cores).
set -e
cd "$(dirname "$0")"
mkdir -p res
OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 python3 asimilimi.py > res/run_log.txt 2>&1
python3 asimilimi_figs.py
