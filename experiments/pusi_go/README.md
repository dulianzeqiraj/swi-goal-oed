# PUSI-GO: well placement with the hydrochemistry in the objective

Innovation of the complete-system document of the Fushë-Kuqe coastal aquifer ("The Fushë-Kuqe system in full",
October 2026). *Pusi* is Albanian for the well. The well-placement objectives of the repository (PRAG-GO, PRAG-MAR,
VENDI-GO) judge salinisation of a supply well by the head proxy h < 1 m. PUSI-GO uses the drinking-water standard in
the well screen instead (chloride 250 mg/L; sodium 200 mg/L is checked) and keeps the linear structure that makes
placement cheap.

**Model.** The areal chloride model of `chloride_fk` (Strack single potential, dispersive interface, geolocated sea
boundary, sector y ≥ 24 km) with the 20 000 prior draws and calibration weights of
`chloride_fk/results/calib_ensemble.npz` (ESS 3 249). Even draws design, odd draws evaluate. Supply wells A1 and P10
(shallow 40 m screens), pumped at 366 and 11694 m³/d so that each well's own
P(Cl > 250 mg/L) = 1/2 (the PRAG-MAR rule, now on chemistry).

**Propositions (section 8 of the document).**
1. *P1, threshold form.* phi is linear in every well rate and screen chloride is non-increasing in phi at the well,
   so {Cl_w > 250} = {phi_w < phi*_w}: the same functional as the head proxy, with a random threshold that carries
   the chemistry.
2. *P2, shared threshold.* For a screen at the top of the aquifer inside the wedge zone,
   phi* = (delta/2) w^2 s*(L/w, eps_L)^2 does not depend on the well: one random threshold, set by the width w of the
   mixing zone, for every supply well.
3. *P3, which standard binds.* With Fushë-Kuqe end-members chloride reaches its limit first under intrusion (sea
   fraction 1.09 % against 1.50 % for sodium by mixing, and exchange only delays sodium); behind a recharge well the
   dissolved sodium cannot exceed the cation equivalents of the recharge water (exchange swaps charge equivalent for
   equivalent): 4.47 meq/L = 103 mg/L for well 193.

## Files
- `pusi_run.py`: runs the 20 000 draws once (phi and the two unit responses at the supply, monitoring and recharge
  candidate cells; the operator is symmetric, so these are also the adjoints) → `res/ens.npz` (122 MB, not committed).
- `pusi_analysis.py`: parts A (thresholds), B (recharge designs), C (monitoring information and safe yield),
  E (screen length) → `res/pusi.json`, log `res/analysis_log.txt`.
- `pusi_exchange.py`: part D, Gaines–Thomas column with GJURMA-GO's exchange solver → `res/exchange.json`.
- `pusi_figs.py` → `res/figP1_map.png`, `res/figP2_pusi.png`.
- `run_all.sh`: the whole pipeline (about 10 minutes on 4 cores).

## Results
- At the supply wells the head proxy sees no risk (median head 3.2 m under pumping; P(h < 1 m) = 0.044) while
  P(shallow Cl > 250 mg/L at A1 or P10) = 0.594. The chemistry threshold is set by the mixing-zone width
  (rank correlation 0.99997) and is uncorrelated with the potential at the well (0.011); a head threshold tuned
  to the same risk agrees with the chloride outcome in 49 % (A1) and 71 % (P10) of aquifers.
- Recharge (3 × 5 000 m³/d): P(A1 or P10 fails) 0.594 → 0.270 with the head-proxy (PRAG-MAR) sites and
  0.247 with the PUSI-GO sites (difference 0.023 ± 0.002); the proxy reports 0.000.
  Reaching 10 % needs 8,516 m³/d per site; the proxy says none.
- Monitoring (entropy of the event 0.669 nats): three heads give at most 0.089 nats (PRAG-GO's heads 0.038);
  one shallow chloride sample at A30 gives 0.312.
- Safe yield (20 m screens, posterior risk ≤ 10 %): no data 4,221 m³/d; PRAG-GO heads 5,349;
  one chloride sample 8,417; best two observations 9,324. The head-proxy rule pumps
  13,869 m³/d and fails the chloride standard in 46 % of aquifers.
- Exchange (E = 60 meq/L, sea fraction 5 %): when Cl reaches 250 mg/L, Na is 56 mg/L; after freshening Na stays ≤ 95 mg/L
  but the water is soft (Ca + Mg down to 0.25 meq/L) for 2.7 pore volumes.

Limits: steady areal model, sharp interface with a Gaussian mixing zone, posterior from likelihood weighting on the
documented facts, binary standard at two supply wells, mixing-cell column without calcite or sulfate reduction.
