#!/bin/bash
# SHKALLA-GO: every stage in order (about 10 minutes on 4 cores).
set -e
cd "$(dirname "$0")"
python3 shkalla_exp.py            # builds shkalla_table.npz with PHREEQC if it is missing, then banks and designs
python3 shkalla_exp.py 0.0025     # sensitivity to the field error (reuses shkalla_bank.npz)
python3 shkalla_exp.py 0.01
python3 shkalla_figs.py           # figS1_chemistry.png, figS2_design.png
