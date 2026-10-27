#!/bin/bash
# SPIRANCA-GO: about two minutes on two cores, plus ten minutes for the variable-density section (sg_ltt.py needs ../montimi_go/res/qcrit_F_EVA.npz).
set -e
cd "$(dirname "$0")"
mkdir -p res
python3 -W ignore sg_run.py 100 2 > res/sg_log.txt 2>&1     # alarms and designs on 100 aquifers
python3 -W ignore sg_checks.py > res/checks_log.txt 2>&1    # checks of N1-N3
python3 -W ignore sg_ltt.py > res/ltt_log.txt 2>&1          # Learn then Test on the MONTIMI-GO safe yields
python3 -W ignore sv_run.py 20 4 > res/sv_log.txt 2>&1     # variable-density section, 20 aquifers (about 10 min)
python3 -W ignore sg_figs.py map results checks section      # res/figS1..S4
