#!/bin/bash
# VENDI-GO (review 53): approximation-error ensemble and pumping, 200 prior truths with every policy, summary and
# figure. Needs numpy, scipy, matplotlib and the Fushë-Kuqe model in ../prag_go_fushe_kuqe; uses four processes.
set -e
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 bvn.py
python3 vendi.py setup
python3 vendi.py check
python3 vendi.py run 200 > res/run200.log
python3 vendi_summary.py res/runs_0_200.json
python3 vendi_figs.py res/runs_0_200.json
