#!/bin/bash
# ZGJEDHJA-GO: every stage in order (about 25 minutes on 4 cores).
set -e
cd "$(dirname "$0")"
python3 zgjedhja_exp.py AB     # identified sets and the goal-oriented monitoring design -> zgjedhja.json
python3 zgjedhja_exp.py C      # finite-sample inference, 500 panels with bootstrap -> zgjedhja_mc.json
python3 zgjedhja_figs.py       # figZ1_identified.png, figZ2_design.png
