#!/bin/bash
# HARTA-GO: run every stage in order (about 2 hours on 4 cores). Logs in *.log.
set -e
cd "$(dirname "$0")"
[ -f harta_ens.npz ] || python3 harta_ens.py > harta_ens.log 2>&1
[ -f harta_ref.npz ] || python3 harta_ref.py > harta_ref.log 2>&1
python3 harta_static.py > harta_static.log 2>&1
for g in rA rAB rArea; do python3 harta_seq.py $g > harta_seq_$g.log 2>&1; done
python3 harta_figs.py > harta_figs.log 2>&1 || true
