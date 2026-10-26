#!/bin/bash
# BASHKIMI-GO, review 55: the whole pipeline (about 3 minutes on four cores).
# Needs the Fushë-Kuqe model of ../prag_go_fushe_kuqe (imported through ../vendi_go/vendi.py).
set -e
cd "$(dirname "$0")"
python3 bashkimi.py calibrate 400                    # physics-informed CATE model: prior, discrepancy field
python3 bashkimi.py run 200                          # 200 aquifers: criteria, realised gains, privacy mechanisms
python3 bashkimi.py mpc 40                           # the decision value on secret shares, 40 aquifers
BASH_MODEL=poly python3 bashkimi.py calibrate 400    # generic polynomial CATE model (as the anchor paper)
BASH_MODEL=poly python3 bashkimi.py run 200
python3 bashkimi_summary.py 200 > res/summary_phys.txt
BASH_MODEL=poly python3 bashkimi_summary.py 200 > res/summary_poly.txt
python3 bashkimi_figs.py
