#!/bin/bash
# VITET-GO (review 52): exact part A, Monte Carlo check (part B), deep agents (part C), figure. Needs numpy, scipy,
# matplotlib and autograd, and the PASQYRA-GO code in ../pasqyra_go; parts B and C use four processes.
set -e
cd "$(dirname "$0")"
python3 vitet.py
python3 vitet_mc.py
python3 vitet_deep.py
python3 vitet_figs.py
