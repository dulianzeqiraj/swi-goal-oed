# MONTIMI-GO: the assembled system, and an assembly set by the well-placement goal

Experiment of the technical note *Assembling the equations of a coastal aquifer, with the placement of recharge and
pumping wells as the final goal* (October 2026). *Montimi* is Albanian for the assembly.

The note writes every equation of the series in one notation:
- the flow equation with its two added terms (the memory of the lenses, with kernel κ_h and tail K_h, and a learned
  closure Ψ);
- the salt equations with immobile zones;
- the long seven-ion equation with exchange and reactions;
- the toe and its mobility;
- the wells, and every boundary and initial condition.

It assembles them into one differential-algebraic system with a block Jacobian and an exact discrete adjoint. MONTIMI-GO
lets the final goal decide the assembly. That goal is the placement of recharge and pumping wells under a chance
constraint on the chloride at the supply screen.

## The test bed (`mg_model.py`, `mg_setup.py`, `ions.py`)
A vertical section of a confined coastal aquifer, 4 km × 60 m (top 10 m below sea level), finite volumes, implicit Euler
with half-year steps:
- **flow:** variable-density flow with storage, hydraulic memory of silt and clay lenses (two compartments) and buoyancy;
- **salt:** sea fraction with two immobile zones and Bear–Scheidegger dispersion;
- **coupling:** flow and salt are solved monolithically by chord Newton with the exact Jacobian, or split (density lagged
  one step);
- **ions:** a seven-ion block with Gaines–Thomas exchange (GJURMA-GO routines), one-way coupled;
- **toe:** a diagnostic.

The scenario starts from the pre-development equilibrium. Fifty years of pumping 4 m²/d per metre of coast at 1.5 km
follow, then a 30-year decision. The decision has three parts:
- a supply well at 2.0, 2.5, 3.0 or 3.5 km;
- one recharge well of 1 m²/d at none, 0.5, 1.0, 1.5, 2.0, 2.5 or 3.0 km;
- the pumping rate.

The constraint is P(screen chloride > 250 mg/L at 30 years) ≤ 10%, which gives 25 layouts.

Uncertain parameters: K, regional inflow, dispersivity, slow immobile capacity and sea-level rise. There are 25 design
draws (the cheap assemblies choose) and 25 evaluation draws (the complete assembly judges). The two counter-example
assemblies (S and N) use the first 10 design draws only.

## Stages
- `mg_stage0_checks.py`: Newton against Picard, split against coupled for four steps, adjoint gradients against
  central differences → `res/checks.json`.
- `mg_stage1_assembly.py`: goal weights of every term from one forward and one adjoint run (four reference layouts), the
  rule (cut if |weight| < 2% of the limit), checks by actual removal or 10% reduction, closure sensitivity, the
  dual-weighted-residual indicator, the goal-graded mesh and the effectivity of the estimate → `res/stage1.json`,
  `res/grid_G.json`.
- `mg_stage3_place.py A SET W`: critical rates of all layouts for all draws of an assembly. The assemblies are:
  - F, complete (120 × 20);
  - G, goal-guided: graded 39 columns, terms cut by the rule;
  - U, uniform 40 columns with the same terms;
  - S, G with the density lagged;
  - N, G without immobile zones.
- `mg_stage5_calib.py`: calibration cases on the complete assembly for the conformal margin.
- `mg_stage4_extra.py`: the ion block run once, the toe relaxation law and the toe as a proxy, the cost of each assembly.
- `mg_analysis.py` → `res/montimi.json`; `mg_figs.py` → `res/figM1`–`figM4`.
- `run_all.sh`: the whole pipeline (about 4–5 hours on 4 cores; the complete assembly dominates).

## Results
All numbers are in `res/montimi.json` and the note
(docs/research_notes/Assembled_System_Equations_Placing_Recharge_and_Pumping_Wells.docx). The note's builder checks
every claim against these files. In short:
- **Goal weights:** the goal cut the hydraulic memory of the lenses and the sea-level rise (weights at most 2.1e-5).
  It kept the immobile zones, dispersion, buoyancy and the same-step coupling (3.0e-3 to 2.6e-2; the limit is 0.0109).
- **Complete assembly:** best layout S3.5-R3.0 at 6.36 m²/d per metre of coast (25 evaluation draws).
- **Goal-guided assembly:** chooses the same layout.
  - It is conservative at all 25 layouts and has rank correlation 0.997.
  - Without the margin it chooses 5.80 m²/d (risk 4% on the complete assembly).
  - With the calibrated margin (-0.154) it chooses 5.95 m²/d (risk 8%, 10% allowed).
- **Counter-examples (same 10 design draws):**
  - Lagging the density removes the conservative bias and is unsafe (risk 20%).
  - Removing the immobile zones is safe (risk 8%) but conservative.
- **Certified safe yield:** a Learn-then-Test certificate of the safe yield with 25 draws would cost 11.6% of the
  value (experiments/spiranca_go, sg_ltt.py).
