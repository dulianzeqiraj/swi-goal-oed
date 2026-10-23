#!/bin/bash
# BARASPESHA-GO: every stage in order (about 10 minutes on 4 cores).
set -e
cd "$(dirname "$0")"
python3 baraspesha_exp.py A     # exactness checks of the equivalences and an example field -> baraspesha.json
python3 baraspesha_exp.py B     # Monte Carlo of the estimators, 5 scenarios x 1000 well fields -> baraspesha.json
python3 baraspesha_exp.py C     # goal-oriented choice of the measured wells, 2 scenarios x 300 fields -> baraspesha_design.json
python3 baraspesha_figs.py      # figB1_estimators.png, figB2_design.png
