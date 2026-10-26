#!/bin/bash
# KOALICIONI-GO (review 56): both models on 200 plausible aquifers, summaries and Figure K1.
set -e
cd "$(dirname "$0")"
KOA_DRIFT=1 python3 koalicioni.py run 200 > res/run_log.txt
KOA_MODEL=local python3 koalicioni.py run 200 >> res/run_log.txt
KOA_DRIFT=1 python3 koalicioni_summary.py 200 > res/summary_drift.txt
KOA_MODEL=local python3 koalicioni_summary.py 200 > res/summary_local.txt
python3 koalicioni_figs.py
