#!/bin/bash
# Build the four paradigm diagrams: HTML (KaTeX), PNG (3600 x 2546), vector PDF (A3 landscape) and a one-page Word copy.
# Needs: npm install (KaTeX 0.16.11), Python 3 with numpy, scipy, matplotlib, python-docx; Node with Playwright + Chromium.
set -e
cd "$(dirname "$0")"
python3 d1_robust_design.py && node render.js d1_robust_design 1.5
python3 d2_causal.py && node render.js d2_causal_generative 1.5
python3 d3_deep_rl.py && node render.js d3_deep_rl_theory 1.5
python3 d4_value_info.py && node render.js d4_value_of_information 1.5
for n in d1_robust_design d2_causal_generative d3_deep_rl_theory d4_value_of_information; do python3 make_docx.py $n.png $n.docx "$n"; done
