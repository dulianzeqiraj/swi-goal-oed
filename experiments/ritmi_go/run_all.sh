#!/bin/bash
# RITMI-GO: every stage in order (about 22 minutes on 4 cores; part V takes 20 of them).
set -e
cd "$(dirname "$0")"
python3 ritmi_exp.py S H G T V   # steady blindness, designs, sampling design, tides, nonlinear check -> ritmi_results.json
python3 ritmi_summary.py         # summary used by review 43 -> ritmi_summary.json
python3 ritmi_figs.py            # figR1_blind.png ... figR4_check.png
