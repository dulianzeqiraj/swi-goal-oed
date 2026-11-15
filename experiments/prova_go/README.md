# PROVA-GO: TRIAL-GO, a robust calibration bandit over model structures, on the Fushë-Kuqe model

TRIAL-GO treats calibration under model misspecification as a multi-armed bandit. The arms are five competing
structures of the real Fushë-Kuqe coastal aquifer model, built by `src/fushe_kuqe_field_design.m` (used unchanged).
A play of an arm is one Levenberg–Marquardt (PEST-like) iteration on the heads plus the check of one new validation
item: a metered Stage-0 head change (stop the pumping at supply well A or B, read the J wells). The cost of the play is 1
if the item falls outside the arm's current 90 % predictive interval. Arms are allocated by the robust Gittins index of
Cohen & Treetanthiploet (2022, *Gittins' theorem under uncertainty*, Electron. J. Probab. 27, paper 17), Section 5 /
Appendix D. The arm finally selected is conditioned on all data and gives the goal: the future heads at the two supply
wells under the planned pumping and the intrusion risk P(A or B intruded), with h_c = P.base·P.delta = 1.0 m.

Everything is MATLAB code (R2021+). It was run here with GNU Octave 8.4.

## How to run

MATLAB (reads `Fushe_Kuqe_All_Data.xlsx` directly with its own `readmatrix`/`readtable`):

```matlab
cd experiments/prova_go
out = prova_go_run(200, 1);   % 200 truths, seeds 1..200 (+ 100 supplementary truths without the sub-zonal field)
make_prova_figures            % figures P1..P7 in res/
```

GNU Octave 8.4 (no io package, so no `.xlsx` reader):

```bash
cd experiments/prova_go
python3 export_fk_csv.py      # once: sheets 3_Boundary_Coords and 2_All_Wells -> data/fk_boundary.csv, data/fk_wells.csv
octave --no-gui --eval "prova_go_setup(); prova_go_run(200, 1, 4, 100)"   # 4 parallel Octave processes
xvfb-run -a octave --no-gui --eval "make_prova_figures"                     # qt graphics toolkit
```

`prova_go_run(nTruths, seed0, nWorkers, nSupp, budgetAlt)`: truths use seeds `seed0 .. seed0+nTruths-1` (even seeds
carry the coastal low-K strip); the first `nSupp` seeds (default 100) are rerun without the sub-zonal field and with the
bandit budget `budgetAlt` (default 380 runs, an equal-cost comparison with all arms + BIC). In this session the main and
no-ζ runs were made by `prova_go_run(200, 1, 4, 100)` and the equal-cost run by the same worker with
`struct('budget', 380)`; an end-to-end test of the final `prova_go_run(4, 1, 2, 2)` in a scratch copy passed.

**The only non-MATLAB step** is `export_fk_csv.py`: a file-format conversion of the two sheets the builder reads
(all columns, header kept; openpyxl). It is needed only in Octave. `prova_go_setup.m` adds `octave_compat/` to the path
**only when running in Octave** (`exist('OCTAVE_VERSION','builtin')`), so MATLAB keeps its built-ins. The shims serve
exactly the calls of the builder:

| shim | why |
|---|---|
| `readmatrix.m`, `readtable.m` (+ `@fkcsvtable`, `fk_csv_file.m`, `fk_csv_read.m`) | read the CSV exports; `T{:,c}` gives a numeric column or a cell array of IDs |
| `string.m`, `strings.m` | Octave has no string class: cell arrays of char are returned and used through `cellstr`/`strcmp` |
| `sort.m` | adds the MATLAB option `'MissingPlacement'` used by `pick_topk` of the builder; otherwise calls the built-in |

With them, `R = fushe_kuqe_field_design(xlsx, P)` runs unchanged in Octave: Nc = 5589 active cells, grid 210 × 84
(dx = 0.25 km), Nz = 12 pilot zones, 43 wells with K (180 in the well list, 132 with an active cell); it reproduces the
published outputs (MAR A18, P21, P16; monitoring P21, A12, A13, A21, A10; baseline intruded area 92.7 km²; PRAG-MAR
sites A23, R16, P21).

Runtime (4 cores, Octave): preparation 59 s (model, checks, pumping design, index tables, budget pilot); main run
(200 truths) 2533 s CPU ≈ 11 min wall; supplementary run (100 truths) ≈ 6 min wall; index checks 58 s; figures ≈ 1 min.
Total ≈ 20 min wall.

## Files

| file | role |
|---|---|
| `prova_go_run.m` | main: prepare → parallel truth runs → merge → demonstration truth → MAR → report |
| `prova_go_prepare.m`, `prova_settings.m` | model, checks, pumping design, robust Gittins tables, run budget; all fixed settings |
| `fk_model_setup.m` | builder output + face lists, coast distance and strip, supply and observation wells |
| `fk_assemble.m`, `fk_solve.m`, `fk_forward.m`, `fk_checks.m` | assembly mirroring the builder (cell-wise log-K field, any recharge), SPD solver, outputs of one run, checks |
| `fk_arms.m`, `arm_run.m` | the five structures A1–A5 |
| `make_truth.m`, `zeta_factor.m`, `pumping_design.m` | synthetic truths and their data; Cholesky factor of the sub-zonal field; planned pumping |
| `lm_init.m`, `lm_iter.m`, `lm_obj.m`, `lm_predict.m`, `lm_restart.m` | LM/Gauss–Newton MAP with Tikhonov prior, FD Jacobian, Laplace predictive |
| `robust_gittins_table.m`, `gittins_lookup.m`, `prova_index_check.m` | robust Gittins index (Appendix D) and its checks |
| `policy_replay.m`, `beta_rand.m` | the bandit policies (TRIAL-GO, UCB, Thompson, greedy) |
| `goal_predict.m`, `goal_score.m`, `prova_truth.m`, `prova_metrics.m`, `prova_go_report.m` | goal predictive, scores, per-truth driver, metrics, log + JSON |
| `prova_demo.m`, `prova_mar.m`, `mar_sites.m`, `mar_fields.m`, `mar_goal_predict.m` | demonstration truth; MAR process (PRAG-MAR sites, fields, risks, section) |
| `make_prova_figures.m` | figures P1–P7 |
| `res/prova_go_log.txt`, `res/prova_go_results.json` | every number; all numbers for a paper (JSON written by Octave without pretty-printing) |
| `res/figP1_model` … `res/figP7_section` (.png 300 dpi, .pdf vector) | figures |

## Settings (fixed before the runs)

* **Model**: builder defaults (b = 30 m, R = 5e-4 m/d, base 40 m, delta 0.025, h_c = 1.0 m, legacy facies rule; with it
  the zones fall in facies classes 1 and 2 only, so A3 has an unidentified third multiplier that stays at its prior).
* **Supply wells**: A23 and R16 of the PRAG-MAR demo have baseline heads 0.98 and 0.88 m < h_c, so no extraction can make
  P(intruded) ≈ 1/2. Rule: for each of them, the nearest inside well ≥ 3 km from the coast with baseline head ≥ 2 m:
  **A = A11** (E 5.00, N 30.25 km, 3.2 km from the coast), **B = H140** (E 12.00, N 15.25 km, 3.8 km).
* **Pumping**: planned Q_A = 5165, Q_B = 3450 m³/d, chosen (prior ensemble of 300 truths, as VENDI-GO) so that the median
  future head at A and at B is h_c (P = 0.50 each, P(A or B) = 0.58); current Q_A0 = 2582, Q_B0 = 1725 m³/d (half).
* **Observation wells** (J = 25, farthest-point sample of the well list, ≥ 0.5 km from A and B): P10 R13 A3 A10 A18 L93
  L97 L103 L117 V8 H16 H44 H81' H419 V35 V28 V331 B382 B389 E60 H259 H182 H407 V332 V94/87.
* **Truths**: log K = log K0c + θ_zone (GamF) + ζ (sd 0.35, exp(−d/2 km), exact Cholesky over the 5589 cells) + strip
  (−1.0 within 1.5 km of the coast, even seeds); recharge 5e-4·exp(ξ_R), ξ_R ~ N(0, 0.3²); future recharge (1 + ξ_f),
  ξ_f ~ N(0, 0.08²). Data: heads at J wells under current pumping (sd 0.05 m); 2J Stage-0 items (sd 0.01 m).
* **Arms**: A1 zones, R fixed (12 par.); A2 uniform + R (2); A3 facies + R (4); A4 zones + R (13); A5 zones + strip + R (14).
* **LM**: forward differences (step 1e-3 in the log-multipliers), λ0 = 0.01 (×1/4 on success, ×8 on failure), converged
  when the relative objective change < 1e-4 or after 15 iterations; one run = one assembly + factorisation (the pumping
  states are extra right-hand sides). Predictive: Laplace at the iterate with the latest FD Jacobian, no structural error.
* **Index**: k = 0.5, β = 0.95, remaining horizon H = 60, p grid 101, n = 1..80, γ grid 401; sensitivity k = 0.2, 0.8 on all truths.
* **Budget**: 2.5 × the median cost of calibrating A4 on the heads over 10 pilot truths (seeds 100001–100010):
  [85 133 71 172 71 85 133 57 144 71] → **213 runs**. Final selection: smallest posterior-mean miss rate among arms with
  ≥ 5 items, then conditioned on all data (runs counted).
* **Demonstration truth** (rule on the truth only, fixed before looking at any method): first even seed with true risk in
  [0.2, 0.8] and |ξ_R| ≥ 0.15 → seed 48.

Implementation note (exact, not an approximation): the LM path of an arm on the heads does not depend on the policy, so
it is computed once per truth and replayed by every bandit policy (`policy_replay.m`); the final conditioning on all data
is run for each distinct starting iterate. Plays of a converged arm cost no runs, so converged arms can use up their 2J
items; an arm is playable while its next iteration fits in the remaining budget.

## Checks (res/prova_go_log.txt)

* Assembly: `fk_assemble` and `R.operator(theta)` are bitwise identical (max |ΔA| = 0, |Δrhs| = 0, 5 random θ); the SPD
  solver matches A\rhs to 1.1e-13 (relative).
* Sign of pumping: +Q in the right-hand side lowers the head; 5165 m³/d at A: 2.431 → 0.307 m.
* Reciprocity: g_A(j) = g_j(A) to 7e-17 (relative) over the 25 wells (symmetric interior block).
* Flux-scale invariance, all K and R × 1.5: recharge-driven heads change by ≤ 6.7e-13 m (max head 11 m); every metered
  Stage-0 response scales by 0.666667 = 1/1.5. Heads under the current metered pumping change only through the pumping
  term (max 0.164 m, rms 0.040 m): the heads carry only weak scale information, the metered responses carry it fully.
* Robust index: γ − p → 0 as 1/√n → 0 (p = 0.3, k = 0.5, β = 0.95: −0.141 at n = 1, +0.020 at n = 20, +0.005 at
  n = 1000); larger k raises γ − p (n = 5: −0.152, −0.107, −0.013, +0.152 for k = 0, 0.2, 0.5, 0.8); larger β lowers it
  (n = 5, k = 0.5: +0.019, −0.013, −0.057 for β = 0.90, 0.95, 0.99). For k = 0.5 the approach to 0 is not monotone
  (exploration bonus at small n, ambiguity premium ∝ 1/√n at larger n).

## Results (200 truths; full tables, intervals and paired differences in the log and JSON)

| method | cov. A | cov. B | CRPS [m] | |risk err| | decision err. | runs |
|---|---|---|---|---|---|---|
| TRIAL-GO (k = 0.5) | 0.72 [0.65, 0.78] | 0.59 [0.52, 0.66] | 0.354 | 0.092 | 0.075 [0.046, 0.120] | 261 |
| PEST standard (A1, heads) | 0.49 | 0.35 | 0.730 | 0.167 | 0.230 | 76 |
| PEST + recharge (A4, heads) | 0.65 | 0.77 | 0.462 | 0.123 | 0.115 | 95 |
| PEST all data (A4) | 0.76 | 0.57 | 0.317 | 0.100 | 0.060 | 82 |
| all arms + BIC, then all data | 0.76 | 0.68 | 0.277 | 0.062 | 0.055 | 380 |
| UCB / Thompson / greedy | 0.70 / 0.75 / 0.73 | 0.56 / 0.58 / 0.59 | 0.433 / 0.328 / 0.352 | 0.113 / 0.099 / 0.090 | 0.095 / 0.085 / 0.070 | ≈ 260 |
| oracle arm (hindsight) | 0.72 | 0.74 | 0.289 | 0.059 | 0.045 | 521 |

* TRIAL-GO vs PEST standard: coverage +0.235 [0.169, 0.301], CRPS −0.377 [−0.477, −0.277] m, decision error −0.155
  [−0.212, −0.098]: a large and clear gain over standard practice.
* TRIAL-GO vs PEST on all data (A4): no significant difference (CRPS +0.037 [−0.017, 0.091]) at 3× the runs.
  vs BIC + all data: TRIAL-GO is worse (coverage −0.060 [−0.105, −0.015], CRPS +0.076 [0.021, 0.131]) but uses 119 fewer runs.
  vs UCB: better CRPS (−0.079 [−0.153, −0.005]) and risk error; vs Thompson and greedy: no difference; k = 0.2 / 0.8: no difference.
* Validation miss rate at convergence on the heads (nominal 0.10): A1 0.22, A2 0.33, A3 0.33, A4 0.21, A5 0.14
  (strip truths 0.28 / 0.39 / 0.39 / 0.30 / 0.17; no strip 0.17 / 0.27 / 0.27 / 0.11 / 0.11).
* TRIAL-GO selects A1/A2/A3/A4/A5 in 27/11/4/82/76 of 200 truths (strip truths: A5 48 of 100; no strip: A4 55 of 100).
* Supplementary run without the sub-zonal field (100 truths): TRIAL-GO coverage 0.89 (A) / 0.74 (B), decision error
  0.09; PEST standard 0.58 / 0.33, 0.32; PEST all data 0.90 / 0.69, 0.08; BIC 0.89 / 0.78, 0.04.
* Supplementary equal-cost run (bandit budget 380 runs ≈ the mean cost of all arms + BIC, 100 truths): TRIAL-GO
  coverage 0.70 / 0.66, CRPS 0.299 m, decision error 0.11, 349 runs; BIC 0.70 / 0.71, 0.272 m, 0.06, 379 runs.
  TRIAL-GO − BIC: coverage −0.025 [−0.072, 0.022], CRPS +0.027 [−0.007, 0.062] (not significant), |risk error|
  +0.021 [0.004, 0.037], decision error +0.05 [0.007, 0.093].
* Why TRIAL-GO does not win everywhere: (i) every arm misses the sub-zonal field ζ, whose effect on the future head in
  the pumped cells is large (sd ≈ 0.8 m at A and 0.4 m at B over the prior) and invisible to the J wells, so all
  conditioned arms are over-confident at the goal; (ii) most of the gain comes from conditioning on the metered Stage-0
  items, which PEST-all-data also does; (iii) a play is evaluated with the arm's current, not yet converged, iterate,
  so early misses penalise expensive arms (non-stationary costs, outside the Gittins theorem); (iv) converged arms play
  for free, so the robust index changes little relative to greedy.
* MAR on the demonstration truth (seed 48): planned pumping raises the true risk to 0.45; 3 PRAG-MAR wells of the
  TRIAL-GO model (A5; 5000 m³/d each) bring it to 0.001 (6 wells: < 0.001) and the intruded area from 48.8 to 43.4 km²
  (40.8 km²). The PEST-standard model (A1) predicts risk 0.05 for its own 3 sites; the truth is 0.35. Toe along
  N = 30.25 km: 1.70 (current), 1.78 (planned), 1.66 km (planned + MAR) from the coast; head at A 2.85 / 1.05 / 2.16 m.
  The interface is the sharp-interface (Ghyben–Herzberg) reading of the steady confined model, not a variable-density simulation.
