# GJURMA-GO: multi-species transport with a stoichiometric learned closure and memory, on the Fushë-Kuqe chemistry

Innovation of review 42, "Missing dynamics in coastal-aquifer flow and multi-species transport: 30 papers for a COST
candidate system of equations" (2020–2026). *Gjurma* is Albanian for the trace.

**The idea.** The chemistry of a salinising aquifer is a trace of the dynamics that the flow equation and a
single-salt transport equation leave out. GJURMA-GO reads this trace twice.
* In the field data it splits the departure of every ion from conservative mixing into named reactions.
* In a dynamic model it learns a reactive closure with memory that is confined to the span of the stoichiometric
  matrix N. Chloride, which no reaction touches, is closure-free and pins the transport (velocity, dispersion, mass
  transfer with the silt–clay layers).

The candidate transport equation (review 42, section 1.5) is

    phi dc/dt + int_0^t kappa(s) dc/dt(t - s) ds + div(q c) - div(phi D grad c) = N r_theta(c, history) + q_s c_s,

with a completely monotone memory kernel kappa (mobile–immobile mass transfer) and learned rates r_theta that are
limited by the availability of the ion they consume.

## Data

`data/Fushe_Kuqe_All_Data.xlsx` (repository root):
* sheet 5: major ions (Cl, Na, K, Ca, Mg, SO4, HCO3) at wells 193 (recharge zone), 340 (centre), 341 and 503
  (Adriatic sector), from Cenameri & Beqiraj (2016), Bull. Geol. Soc. Greece 50(2), 665–670,
  https://doi.org/10.12681/bgsg.11772;
* sheet 6: chloride at wells 341 and 503 in 1984, 1999 and 2001.

## Files

| file | content |
|---|---|
| `gjurma_field.py` | the field split: seawater fraction from Cl, departures from mixing, five reaction extents with 90% intervals → `gjurma_field.json` |
| `gjurma_model.py` | 1D flow-line simulator (seven species, mobile–immobile memory, sulfate reduction, Gaines–Thomas exchange solved by Newton's method) and the learned closures |
| `gjurma_exp.py` | B twin experiment (40 truths, five models, ES-MDA), C Fisher spectra, D non-Gaussianity of the forecast (proposal N2), E field data → `gjurma_twin.json`, `gjurma_real.json` |
| `gjurma_summary.py` | numbers quoted in review 42 → `gjurma_summary.json` |
| `gjurma_figs.py` | `figG1_field.png`, `figG2_twin.png`, `figG3_ident.png`, `figG4_real.png` |
| `run_all.sh` | everything in order (about 12 minutes on 4 cores) |

## The field split (sheet 5)

Seawater fraction f from Cl between the fresh end-member (well 193) and seawater; departures Δ = N ξ (meq/L);
uncertainty from a 3% analytical error, a 10% error of the fresh end-member and a seawater salinity between standard
seawater and the Adriatic (4000 draws). Seawater fraction with standard seawater (90% interval over all sources of
uncertainty) and reaction extents, median and 90% interval (meq/L):

| well | f | Na–Ca exch. | Na–Mg exch. | K–Ca exch. | sulfate red. | calcite |
|---|---|---|---|---|---|---|
| 503 | 5.4% [4.7, 5.4] | 4.7 [3.5, 6.0] | 5.8 [5.2, 6.5] | 0.47 [0.16, 0.77] | 3.6 [3.2, 4.1] | −1.9 [−2.8, −1.1] |
| 341 | 5.3% [4.7, 5.4] | 4.5 [3.2, 5.8] | 0.38 [−0.08, 0.85] | 0.43 [0.12, 0.73] | 1.7 [1.3, 2.2] | −2.3 [−3.2, −1.5] |
| 340 | 2.1% [1.8, 2.1] | −0.22 [−0.87, 0.45] | −1.8 [−2.2, −1.5] | 0.22 [0.03, 0.39] | 0.83 [0.55, 1.11] | −0.49 [−1.02, 0.02] |

On the six non-conservative ions N has rank 5 and its left null vector is the charge balance, so the residual of the
split is the charge imbalance of the departures (0.02–0.05 meq/L). The small residual is a consistency check, not a
proof that these reactions occurred. Read physically: the coastal wells show intrusion-type exchange (Na taken up,
Ca and Mg released) and sulfate reduction; well 340 shows the opposite sign of Na–Mg exchange (Na released, as in
freshening of a once-marine exchanger).

## The twin experiment (B)

A 15 km flow line, 75 cells, abstraction field at 6 km, wells at 1, 2, 4.5 and 12 km (assumed positions), pumping
history 1950–2045 (natural seaward flow, heavy pumping 1975–1990, a pause 1990–2000, renewed pumping). Each of 40
truths draws its own exchange capacity, selectivities, sulfate-reduction rate, mass-transfer rate and capacity,
dispersivity, velocity multiplier and coastal salinity. Data: the seven ions at the four wells in 2016 and Cl at wells
503 and 341 in 1984, 1999 and 2001 (34 numbers, 5% log-scale error). Fit: ES-MDA, 100 members, four iterations.
Goals in 2045: Cl at 5 km, Na and hardness (Ca + Mg) at 3 km, length of the strip with Cl > 250 mg/L.

| model (parameters) | Cl at 5 km | Na at 3 km | Ca + Mg at 3 km | strip | coverage of the 90% interval |
|---|---|---|---|---|---|
| classical (3) | 64.1 mg/L | 54.5 mg/L | 4.71 meq/L | 0.230 km | 8, 18, 0, 40% |
| free closure (40) | 23.7 | 31.5 | 1.83 | 0.088 | 100, 93, 85, 100% |
| GJURMA, joint (16) | 15.6 | 20.0 | 0.63 | 0.073 | 73, 50, 58, 95% |
| GJURMA, cut (16) | 15.3 | 20.8 | 0.51 | 0.049 | 98, 65, 78, 100% |
| oracle (10) | 9.1 | 9.6 | 0.28 | 0.048 | 95, 93, 90, 100% |

(Mean absolute error of the posterior mean.) GJURMA with the cut reduces the error of the free closure by 35%, 34%,
72% and 44%, with intervals 2–4 times narrower. The cut (transport and memory from the ten Cl data, then the closure
with transport fixed) restores the coverage of the Cl forecast (73% → 98%) and gives transport estimates closest to
the oracle. Na and hardness remain under-covered (65% and 78%): the learned exchanger has a structural error that
the posterior does not see.

**C, identifiability.** Fisher information of the 34 data in prior-standardised parameters: 17 of 40 directions
informed for the free closure, 13 of 16 for GJURMA, 8 of 10 for the oracle.

**D, proposal N2.** Distance (W2) between the 400-member forecast of log Cl in 2016 and its Gaussian fit. Scale-free,
it is largest 13.5 km inland, where the forecast is almost certain. Divided by the observation error, it exceeds 1
only between 1.9 and 7.3 km, around the front and the abstraction field (maximum 6.1 at 6.1 km): the zone where a
transport-map analysis would replace the ensemble Kalman analysis.

**E, the field data.** No model fits the four wells within the 5% error (RMS misfit 6.5–12.2 σ): the 1D flow line
with assumed positions and history is too simple. The cut fits the Cl history best (3.0 σ against 4.0–9.9 σ), as
Proposition 5 predicts, and the 2045 forecasts of the models differ by more than their intervals (Na at 3 km from
228 to 523 mg/L): structural uncertainty dominates and must be reported (proposal N3).

## Limitations

* 1D flow line with assumed well positions, pumping history and seawater salinity; density coupling is not solved.
* The truth uses the same mass-transfer memory as the learned models, so the memory structure is not tested against
  a different kernel; a relic marine exchanger (Mori–Zwanzig initial-state term) is available (`F_RELIC`) but off.
* ES-MDA with 100 members is approximate for 40 parameters; the free closure's wider intervals partly reflect this.
* The field split assumes five reactions; other reactions with the same stoichiometric signature cannot be told apart.

## Run

    bash run_all.sh
