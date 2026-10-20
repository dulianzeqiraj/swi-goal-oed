#!/bin/bash
# DARA-GO: every stage in order (about 15 minutes on 4 cores).
set -e
cd "$(dirname "$0")"
python3 dara_ref.py            # exact information curves by quadrature (printout only)
python3 dara_exp.py            # four maps, bounds, certified sets, nested Monte Carlo -> dara_results.json, dara_maps.npz
python3 dara_figs.py           # figD1_problem.png, figD2_map.png, figD3_dara.png
