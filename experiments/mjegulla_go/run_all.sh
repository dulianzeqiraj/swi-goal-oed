#!/bin/bash
# MJEGULLA-GO: every stage in order (about 30 minutes on 4 cores).
set -e
cd "$(dirname "$0")"
python3 mjegulla_exp.py A       # exactness of the per-well decomposition and one example field -> mjegulla.json
python3 mjegulla_exp.py B       # Monte Carlo: 300 well fields, 7 designs for goal M and 6 for goal P -> mjegulla.json
python3 mjegulla_exp.py C       # budget: 2, 4 and 8 measurements per season, 150 fields each -> mjegulla_budget.json
python3 mjegulla_summary.py     # summary used by review 41 -> mjegulla_summary.json
python3 mjegulla_figs.py        # figM1_robust.png, figM2_design.png
