#!/bin/bash
# Chloride sufficiency (synth_cut.json) and the three new figures of the synthesis article.
set -e
cd "$(dirname "$0")"
python3 synth_cut.py > synth_cut.log
python3 synth_figs.py
echo "wrote synth_cut.json, figA1_system.png, figA2_atlas.png, figA3_cut.png"
