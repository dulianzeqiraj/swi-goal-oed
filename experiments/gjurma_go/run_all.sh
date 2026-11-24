#!/bin/bash
# GJURMA-GO: every stage in order (about 12 minutes on 4 cores).
set -e
cd "$(dirname "$0")"
python3 gjurma_field.py          # the field split of sheet 5 -> gjurma_field.json
python3 gjurma_exp.py CD         # Fisher spectra and non-Gaussianity of the forecast -> gjurma_twin.json
python3 gjurma_exp.py B          # twin experiment: 40 truths, five models -> gjurma_twin.json
python3 gjurma_exp.py E          # the field data (sheets 5 and 6) -> gjurma_real.json
python3 gjurma_summary.py        # summary used by review 42 -> gjurma_summary.json
python3 gjurma_figs.py           # figG1_field.png ... figG4_real.png
