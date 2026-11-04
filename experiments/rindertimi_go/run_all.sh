#!/usr/bin/env bash
# RINDERTIMI-GO: train the prior, tune and evaluate the sampler, build the note.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p res
python3 rgo_net.py 7000 > res/rgo_train_log.txt 2>&1
python3 rgo_fundps.py tune > res/rgo_tune_log.txt 2>&1
python3 rgo_fundps.py eval > res/rgo_eval_log.txt 2>&1
python3 build_rgo_doc.py ../../docs/research_notes/RINDERTIMI-GO_Boundary_Conditions_FunDPS.docx
