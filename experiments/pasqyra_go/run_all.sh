#!/bin/bash
# PASQYRA-GO (review 51): exact part A, mirror test (part B), deep agents (part C), figure. Needs numpy, scipy,
# matplotlib and autograd; uses four processes. Part A takes about 4 minutes, part B about 10, part C about 40.
set -e
cd "$(dirname "$0")"
python3 pasqyra.py
python3 pasqyra_dither.py
python3 pasqyra_neural.py
python3 pasqyra_figs.py
