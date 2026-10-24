#!/usr/bin/env bash
# MESIMI-GO: certainty-equivalent learning of a pumping rule; regret and the log T constant (review 46). About 6 minutes.
set -e
cd "$(dirname "$0")"
python3 mesimi.py
python3 mesimi_theory.py
python3 mesimi_figs.py
