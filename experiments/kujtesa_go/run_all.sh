#!/usr/bin/env bash
# KUJTESA-GO: slow clay memory and deep temporal-difference learning (review 48). Part 1 (exact) takes seconds; the
# neural part 2 takes about 7 minutes on four cores.
set -e
cd "$(dirname "$0")"
python3 kujtesa.py
python3 kujtesa_policy.py
python3 kujtesa_figs.py
