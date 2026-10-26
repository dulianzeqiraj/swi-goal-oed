#!/bin/bash
# PUSI-GO: ensemble, analysis, exchange column and figures (about 10 minutes on 4 cores).
set -e
cd "$(dirname "$0")"
python3 pusi_run.py
OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 python3 pusi_analysis.py > res/analysis_log.txt 2>&1
python3 pusi_exchange.py > res/exchange_log.txt
python3 pusi_figs.py
