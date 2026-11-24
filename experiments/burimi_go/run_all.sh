#!/usr/bin/env bash
# BURIMI-GO: identifiable hydrochemical processes and counterfactual chemistry (review 49). Needs numpy, scipy,
# matplotlib and autograd (pip install autograd). About 20 minutes on four cores (burimi.py about 8, burimi_modes.py
# about 6).
set -e
cd "$(dirname "$0")"
python3 burimi.py
python3 burimi_theory.py
python3 burimi_precision.py
python3 burimi_modes.py
python3 burimi_figs.py
