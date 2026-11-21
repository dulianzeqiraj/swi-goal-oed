#!/usr/bin/env bash
# KAOS-GO: run the pore-scale experiment and build the review "From chaos in the pores to Darcy's law"
# (Word, OMML equations, clickable links).  Needs numpy, numba, matplotlib, python-docx, pandoc and the helpers of
# ../garancia_go, ../rindertimi_go, ../spiranca_go/certain_coast and ../ml_paradigms/word.
# The simulations take about 2 hours on four cores; the raw runs (about 60 MB) go to RUNS and are not kept in the
# repository, the numbers of the review are in res/.
set -euo pipefail
cd "$(dirname "$0")"
RUNS=${RUNS:-/tmp/kaos_runs}
export NUMBA_NUM_THREADS=${NUMBA_NUM_THREADS:-4}
mkdir -p res "$RUNS/prod" "$RUNS/conv"
CELL="--L 288 --a 18 --n 16 --gap 6 --seed 3 --scale 1.5 --g 4e-6"

# 0. gates of the solver: Stokes drag of a square array, energy budget, independence of viscosity and force
python3 kaos_gates.py "$RUNS/gates.json"

# 1. resolution study: the same cell and dimensionless force G* = g a^3 / nu^2 on three lattices (two forces on two)
for spec in "1152 192 12 1.0 0.003 6e-6 1200" "1152 288 18 1.5 0.0045 4e-6 1800" "1152 384 24 2.0 0.006 3e-6 2400" \
            "648 192 12 1.0 0.004 6e-6 1200" "648 288 18 1.5 0.006 4e-6 1800"; do
  set -- $spec
  out="$RUNS/conv/G$1_a$3.0.npz"
  [ -f "$out" ] || python3 kaos_run.py --out "$out" --L $2 --a $3 --n 16 --gap $(python3 -c "print(4*$4)") --seed 3 \
      --scale $4 --nu $5 --g $6 --spin $((80*$7)) --samp $((200*$7)) --every 20 --lyap $((80*$7)) --fields
done

# 2. the sweep: steady chain (continuation in the viscosity), then the unsteady levels
prev=""
for nu in 0.45 0.15 0.075 0.045 0.03 0.021 0.015 0.012; do
  init=""; [ -n "$prev" ] && init="--init $prev"
  [ -f "$RUNS/prod/r_$nu.npz" ] || python3 kaos_run.py --out "$RUNS/prod/r_$nu.npz" $CELL --nu $nu --spin 120000 \
      --steady_tol 1e-9 --samp 2000 --every 20 --fields --state "$RUNS/prod/s_$nu.npz" $init
  prev="$RUNS/prod/s_$nu.npz"
done
for nu in 0.0105 0.009 0.0075 0.0052; do
  [ -f "$RUNS/prod/r_$nu.npz" ] || python3 kaos_run.py --out "$RUNS/prod/r_$nu.npz" $CELL --nu $nu --spin 153600 \
      --samp 384000 --every 20 --lyap 153600 --fields --state "$RUNS/prod/s_$nu.npz" --init $prev
  prev="$RUNS/prod/s_$nu.npz"
done

# 2b. control of the Lyapunov measurement at a steady level (the exponent must be negative)
[ -f "$RUNS/prod/lyapctl_0.015.npz" ] || python3 kaos_run.py --out "$RUNS/prod/lyapctl_0.015.npz" $CELL --nu 0.015 \
    --init "$RUNS/prod/s_0.015.npz" --spin 2000 --samp 2000 --every 20 --lyap 106400

# 3. finite-size study of the Darcy coefficient (4, 16 and 64 grains)
[ -f "$RUNS/prod/rev.json" ] || python3 kaos_rev.py "$RUNS/prod/rev.json"

# 4. long runs for the statistics of window means (1200 transit times)
for nu in 0.006 0.0045; do
  [ -f "$RUNS/prod/long_$nu.npz" ] || python3 kaos_run.py --out "$RUNS/prod/long_$nu.npz" $CELL --nu $nu --spin 153600 \
      --samp 2304000 --every 20 --init "$RUNS/prod/s_0.0075.npz"
done

# 5. gate of the statistics code, analysis -> res/kaos.json, res/kaos_fields.npz, res/kaos_series.npz; the document
python3 kaos_check_stats.py > res/stats_gate_stdout.txt
cp "$RUNS/gates.json" res/gates.json
python3 kaos_exp.py "$RUNS" > res/kaos_stdout.txt
python3 build_kaos_doc.py ../../docs/literature/Literature_review_Chaos_in_the_Pores_to_Darcy_Law_Upscaling_KAOS-GO_Caltech_Oxford_MIT_Harvard_Max_Planck_2020-2026.docx
