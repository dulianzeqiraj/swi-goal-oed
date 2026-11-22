#!/bin/bash
# Word versions with editable equations (OMML) and large type: four A4 landscape pages per diagram.
# Run ../run_all.sh first (it renders the PNGs whose schematics are cropped here). Needs docx (npm), pandoc 3, lxml.
# Diagram k follows the order of export_content.py: 1-4 the paradigms, 5 the introduction, 6 the stakeholder decisions,
# 7-8 the transfer routes R1 and R2.
set -e
cd "$(dirname "$0")"
python3 export_content.py
pngs=(d1_robust_design d2_causal_generative d3_deep_rl_theory d4_value_of_information d0_problem_statement d5_stakeholder_decisions
      d6_transfer_r1 d7_transfer_r2)
names=(ML_Paradigm_1_Robust_Bayesian_Design ML_Paradigm_2_Causal_Generative_Modelling ML_Paradigm_3_Deep_Reinforcement_Learning_Theory
       ML_Paradigm_4_Value_of_Information_Without_a_Prior Introduction_The_Problem_Statement Stakeholder_Decision_Making
       Transfer_Route_R1_A_Model_That_Can_Travel Transfer_Route_R2_A_Shared_Representation)
mkdir -p out
for k in 1 2 3 4 5 6 7 8; do
  python3 - "../${pngs[$((k-1))]}.png" "hero$k.png" <<'PY'
import sys
from PIL import Image
im = Image.open(sys.argv[1]); s = im.size[0] / 2400
im.crop((0, int(112 * s), int(1574 * s), int(842 * s))).save(sys.argv[2])
PY
  node paradigms_word.js $k draft$k.docx eq$k.json
  python3 omml.py draft$k.docx eq$k.json out/${names[$((k-1))]}.docx
done
