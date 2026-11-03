#!/bin/bash
# SHIU-GO: numerical checks of the note on stochastic rain-recharge forcing (about 13 minutes on 4 cores).
set -e
cd "$(dirname "$0")"
mkdir -p res
# E1-E3 and identifiability over 12 twins (4 worker processes, about 11 minutes)
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 shiu_exp.py 12 > res/shiu_exp_log.txt 2>&1
# E4: the soil-water SDE discovered from soil-moisture data alone (route A on its own)
python3 shiu_km.py > res/shiu_km_log.txt 2>&1
# Word note with figures and OMML equations (needs pandoc); the build stops if a finding stated in the text no longer holds
python3 build_shiu_doc.py ../../docs/research_notes/SHIU-GO_Forcimi_Stokastik_Ekuacionet_Filtrimit_Transportit.docx
