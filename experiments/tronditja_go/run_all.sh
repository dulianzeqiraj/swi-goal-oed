#!/usr/bin/env bash
# TRONDITJA-GO: Okada checks, experiments E1-E4, figures and the Word report (about 30 s plus the Word build).
# The revision of the TERMETET note needs the author's file: python3 -I fix_termetet.py IN.docx OUT.docx
set -euo pipefail
cd "$(dirname "$0")"
python3 okada_checks.py
python3 tronditja_exp.py | tee res/tronditja_stdout.txt
python3 build_tronditja_doc.py ../../docs/research_notes/TRONDITJA-GO_Earthquake_Aquifer_Liquefaction_Implementation.docx
