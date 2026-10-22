#!/bin/bash
# KURSIM-GO: every stage in order (about 8 minutes on 4 cores).
set -e
cd "$(dirname "$0")"
python3 kursim_exp.py          # Monte Carlo study of six estimators -> kursim_mc.json
python3 kursim_design.py       # policy grid, risk and asymptotic variances -> kursim_design.json
python3 kursim_figs.py         # figK1_estimators.png, figK2_design.png
