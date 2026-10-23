#!/bin/bash
# BESA-GO: every stage in order (about 25 minutes on 4 cores).
set -e
cd "$(dirname "$0")"
python3 besa_exp.py            # Monte Carlo study, nine scenario-size pairs x 1000 data sets -> besa_mc.json
python3 besa_curve.py          # limits and power along a path of copulas -> besa_curve.json
python3 besa_figs.py           # figB1_path.png, figB2_scenarios.png
