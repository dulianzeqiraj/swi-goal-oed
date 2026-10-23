# RITMI-GO: what transient data identify in the augmented flow + multi-species system

Numerical test of the innovation of literature review 43 (*ritmi*, the rhythm): a record identifies the parts of
the system that its forcing excites, at the rates of that forcing, and a forecast needs the parts that its own future
forcing will excite. The experiment compares the two on the Fushë-Kuqe coastal flow line of GJURMA-GO
(`../gjurma_go`, review 42).

## Model (`ritmi_model.py`)

The GJURMA-GO flow line (15 km, abstraction at 6 km, wells 503, 341, 340 and 193 at assumed distances, the pumping
history of the coastal sector) with seven species (Cl, Na, K, Ca, Mg, SO4, HCO3) and:

- **two immobile zones** (silt: rate `a1`, capacity `b1`; clay: rate `a2`, capacity `b2`), each mobile–immobile pair
  updated exactly, so the memory kernel `kappa(s) = b1 a1 exp(-a1 s) + b2 a2 exp(-a2 s)` is completely monotone;
- **sulfate reduction inside the clay** of the coastal strip (rate `k_sr`), an irreversible reaction inside an
  immobile zone;
- **cation exchange** in local equilibrium (Gaines–Thomas, capacity `E`, three selectivities);
- quarterly steps to 2000, monthly steps 2000–2045, and a **pumping modulation** of the coastal velocity during
  2026–2031 (`const`, `sine`, `doublet`, `prbs`, `block` = pause or surge);
- a **steady mode** (constant forcing run for 3,000 years).

## Experiments (`ritmi_exp.py`, parts S, H, G, T, V)

| Part | What it computes |
|---|---|
| S | Fisher information of steady data (seven ions at four wells) against the transient history; the rank-one "reactive exception" of the clay memory seen through SO4 and HCO3, compared with the gradient of `log(b2 a2 k_sr / (a2 + k_sr))` |
| H (D) | History and five years of status-quo monitoring (monthly Cl, half-yearly major ions at 503, 341, 340); twelve pumping designs; the effective-velocity combination `log s_v - log(1 + b1 + b2)` and its alignment with the 2045 goals |
| G | Greedy goal-oriented choice of 12 sampling units among 210, against a routine schedule of 12 |
| T | Tides (M2, K1, MSf, Sa) at four wells for a two-rate storage kernel of the flow equation (analytic Jacob–Ferris solution with memory) |
| V | Nonlinear check: ES-MDA (100 members, 4 iterations) on 24 synthetic truths for history only, + routine 12, + goal-oriented 12, + all monitoring |

Fisher information uses central differences in prior-standardised parameters (step 0.05) and 5% errors on the log
scale; posterior standard deviations are Laplace approximations at the prior-mean truth.

## Main results

- Steady data leave the exchange capacity, the selectivities and the silt memory exactly at their prior; the clay
  memory and the sulfate-reduction rate are seen through a single combination (cosine 1.000 with the predicted
  direction).
- Five years of monitoring identify the clay memory and the exchange, not the fast silt zone; but the 2045 chloride
  goal is aligned at 94% with the effective-velocity combination, whose posterior sd falls from 0.33 to 0.025.
- Pumping rhythms add at most 0.26 nats (five-year doublet, +14 mg/L of chloride at the well field); the monitoring
  itself adds 21.7. Twelve goal-oriented samples (late ion campaigns at wells 340 and 341) reduce the 2045 chloride
  error from 17.7 mg/L (history) to 4.1 mg/L, against 7.5 mg/L for a routine schedule (nonlinear check).
- Tides: M2 pins the diffusivity; the fortnightly constituent identifies the fast storage rate; the slow rate needs
  forcing of months.

## Running

`./run_all.sh` (about 22 minutes on 4 cores) writes `ritmi_results.json`, `ritmi_summary.json` (used by the builder
of review 43) and `figR1_blind.png` … `figR4_check.png`. `python3 ritmi_exp.py S H G T` alone takes under a minute.
