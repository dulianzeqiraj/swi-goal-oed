#!/bin/bash
# QENDRESA-GO: every stage in order (about 3 hours on 4 cores).
set -e
cd "$(dirname "$0")"
python3 qendresa_exp.py        # Monte Carlo study, six scenario-size pairs x 1000 data sets -> qendresa_mc.json
python3 qendresa_curve.py      # large-sample limits, efficiency vs copula strength, non-collapsibility -> qendresa_curve.json
python3 qendresa_figs.py       # figQ1_mechanism.png, figQ2_montecarlo.png, figQ3_design.png
