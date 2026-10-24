#!/usr/bin/env bash
# KUFIRI-GO: a causal, horizon-resolved budget of all boundary and initial conditions (review 45). About 12 minutes.
set -e
cd "$(dirname "$0")"
python3 kufiri.py
python3 kufiri_regimes.py
python3 kufiri_figs.py
