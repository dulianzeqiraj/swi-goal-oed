#!/bin/bash
# MONTIMI-GO: the assembled system and an assembly set by the well-placement goal.
# Whole pipeline about 3-4 hours on 4 cores (the placement on the complete assembly dominates).
set -e
cd "$(dirname "$0")"
mkdir -p res
python3 -W ignore mg_stage0_checks.py > res/stage0_log.txt 2>&1          # solver checks (Newton, Picard, split, gradients)
python3 -W ignore mg_stage1_assembly.py > res/stage1_log.txt 2>&1        # goal weights, rule, goal-graded mesh, DWR
python3 -W ignore mg_stage3_place.py F EVA 4 > res/stage3_F_EVA_log.txt 2>&1   # referee: complete assembly
python3 -W ignore mg_stage3_place.py G DES 4 > res/stage3_G_DES_log.txt 2>&1   # goal-guided assembly
python3 -W ignore mg_stage3_place.py U DES 4 > res/stage3_U_DES_log.txt 2>&1   # uniform coarse mesh, same terms
python3 -W ignore mg_stage3_place.py S DES 4 > res/stage3_S_DES_log.txt 2>&1   # counter-example: lagged density
python3 -W ignore mg_stage3_place.py N DES 4 > res/stage3_N_DES_log.txt 2>&1   # counter-example: no immobile zones
python3 -W ignore mg_stage5_calib.py 4 > res/stage5_log.txt 2>&1         # calibration cases for the margin
python3 -W ignore mg_stage4_extra.py > res/stage4_log.txt 2>&1           # ions, toe law, costs
python3 -W ignore mg_analysis.py > res/analysis_log.txt 2>&1             # margins, choices, risks -> res/montimi.json
python3 -W ignore mg_figs.py                                              # res/figM1..M4
