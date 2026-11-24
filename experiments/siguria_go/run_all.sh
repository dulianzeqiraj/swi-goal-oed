#!/bin/bash
# SIGURIA-GO (review 54): scenario ensembles, certificate and figure. Needs numpy, scipy (HiGHS), matplotlib and the
# VENDI-GO setup and results in ../vendi_go/res; uses four processes.
set -e
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 siguria.py ensemble
python3 siguria.py analyse > res/siguria.log
python3 siguria_figs.py
