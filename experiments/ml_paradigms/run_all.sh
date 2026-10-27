#!/bin/bash
# Build the diagram series: HTML (KaTeX), PNG (3600 x 2546), vector PDF (A3 landscape) and a one-page Word copy.
# d0: introduction (the problem), d1-d4: the four machine-learning paradigms, d5: stakeholder decisions.
# Needs: npm install (KaTeX 0.16.11), Python 3 with numpy, scipy, matplotlib, python-docx; Node with Playwright + Chromium.
# d0 reads ../pusi_go/res/pusi.json; d5 reads ../vendimi_go, ../rrezja_go and ../moti_go results.
set -e
cd "$(dirname "$0")"
python3 d0_problem.py && node render.js d0_problem_statement 1.5
python3 d1_robust_design.py && node render.js d1_robust_design 1.5
python3 d2_causal.py && node render.js d2_causal_generative 1.5
python3 d3_deep_rl.py && node render.js d3_deep_rl_theory 1.5
python3 d4_value_info.py && node render.js d4_value_of_information 1.5
python3 d5_stakeholders.py && node render.js d5_stakeholder_decisions 1.5
for n in d0_problem_statement d1_robust_design d2_causal_generative d3_deep_rl_theory d4_value_of_information d5_stakeholder_decisions; do
  python3 make_docx.py $n.png $n.docx "$n"
done
