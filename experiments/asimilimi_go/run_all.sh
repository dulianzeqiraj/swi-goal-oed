#!/bin/bash
# ASIMILIMI-GO: numerical checks of the data-assimilation note (about 3 minutes on 4 cores).
set -e
cd "$(dirname "$0")"
mkdir -p res
OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 python3 asimilimi.py > res/run_log.txt 2>&1
python3 asimilimi_figs.py
# Extreme events (E8-E12), about 15 minutes on 4 cores; then the variance-only variant, one trace, figure A3 and diagrams.
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 asimilimi_extreme.py > res/extreme_log.txt 2>&1
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 ONLY=E8b python3 asimilimi_extreme.py >> res/extreme_log.txt 2>&1
ONLY=TRACE TRACE_TW=0 python3 asimilimi_extreme.py >> res/extreme_log.txt 2>&1
python3 asimilimi_extreme_figs.py
python3 diagrams.py && node render_diagrams.js
