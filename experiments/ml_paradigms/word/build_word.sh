#!/bin/bash
# Word versions with editable equations (OMML) and large type: four A4 landscape pages per diagram.
# Run ../run_all.sh first (it renders the PNGs whose schematics are cropped here). Needs docx (npm), pandoc 3, lxml.
set -e
cd "$(dirname "$0")"
python3 export_content.py
python3 - <<'PY'
from PIL import Image
for i, n in enumerate(['d1_robust_design', 'd2_causal_generative', 'd3_deep_rl_theory', 'd4_value_of_information']):
    im = Image.open('../%s.png' % n); s = im.size[0] / 2400
    im.crop((0, int(112 * s), int(1574 * s), int(842 * s))).save('hero%d.png' % (i + 1))
PY
mkdir -p out
names=(ML_Paradigm_1_Robust_Bayesian_Design ML_Paradigm_2_Causal_Generative_Modelling ML_Paradigm_3_Deep_Reinforcement_Learning_Theory ML_Paradigm_4_Value_of_Information_Without_a_Prior)
for k in 1 2 3 4; do
  node paradigms_word.js $k draft$k.docx eq$k.json
  python3 omml.py draft$k.docx eq$k.json out/${names[$((k-1))]}.docx
done
