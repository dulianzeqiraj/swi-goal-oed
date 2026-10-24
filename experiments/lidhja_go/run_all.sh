#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 lidhja.py > lidhja.log
python3 lidhja_summary.py > /dev/null
python3 lidhja_figs.py
echo "wrote lidhja_results.json, lidhja_summary.json, figL1_leak.png"
