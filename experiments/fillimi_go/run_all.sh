#!/usr/bin/env bash
# FILLIMI-GO: memory and the handover from initial to boundary conditions (review 44). About 2 minutes.
set -e
cd "$(dirname "$0")"
python3 fillimi.py
python3 fillimi_tails.py
python3 fillimi_figs.py
