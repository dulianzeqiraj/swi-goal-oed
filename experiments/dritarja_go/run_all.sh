#!/usr/bin/env bash
# DRITARJA-GO: the memory window a deep pumping agent needs under partial observation (review 50). Needs numpy, scipy,
# matplotlib and autograd. Part A (exact) takes about 2 minutes; the neural parts B and B2 about 50 and 45 minutes on
# four cores.
set -e
cd "$(dirname "$0")"
python3 dritarja.py
python3 dritarja_neural.py
python3 dritarja_saa.py
python3 dritarja_saa_check.py
python3 dritarja_figs.py
