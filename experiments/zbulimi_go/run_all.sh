#!/usr/bin/env bash
# ZBULIMI-GO: exploration design for several well fields with unknown responses (review 47). About 10 minutes.
set -e
cd "$(dirname "$0")"
python3 zbulimi.py
python3 zbulimi_theory.py
python3 zbulimi_early.py
python3 zbulimi_figs.py
