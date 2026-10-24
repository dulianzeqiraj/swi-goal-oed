# LIDHJA-GO: how much error of the reactive closure leaks into chloride through ion coupling

*Lidhja* = the coupling. Numerical test of Theorem 2 of the note *The electrodiffusive leak of the cut*: when ions
diffuse at different rates, the zero-current electric field couples chloride to the cations, so an error of the
reactive closure (here the cation exchanger) can reach chloride even though no reaction acts on it.

## Model (`lidhja.py`)
Seven ions (Cl, Na, K, Ca, Mg, SO4, HCO3) in 1-D: common mechanical dispersion `D_mech`, molecular diffusion
`tau * D_i` (free-water values of Li & Gregory 1974, to be verified), electromigration under zero current, and cation
exchange in local equilibrium (Gaines–Thomas, solver of `../gjurma_go`). True and wrong closures differ only in the
exchanger. Each case is run with equal diffusivities, with Fick diffusion without the electric field, and with
Nernst–Planck.

- **Part L, clay lens** (no flow, half-thickness 1 m, tau 0.3, E = 500 meq/L, 100 years): salinisation (fresh -> 5 %
  sea water at the edge) and freshening; wrong closures: E -30 %, or K(Na\Ca) and K(Na\Mg) x 1.5.
- **Part P, flow regime**: the same mixing at Pe = D_mech / D_Cl = 0 ... 300, run to the same mixing depth (0.2 m).

## Results (`lidhja_summary.json`)
| Result | Value |
|---|---|
| Equal diffusivities, or no electric field | leak exactly 0 (all cases) |
| Lens, salinisation: largest Cl difference inside the lens | 14–16 mg/L |
| Lens: change of the chloride taken up after 50 / 100 years | 0.7 % / 1.0 % |
| Lens, freshening | below 0.1 % |
| Leak against 1 + Pe (Part P) | slope -1.02 |
| Bound of Theorem 2 / actual leak | about 4 (all salinisation and flow-regime cases) |
| Fushë-Kuqe mobile zone, Pe = alpha_L v / D_Cl | about 2.3 x 10^5 (leak suppressed by about 4 x 10^-6) |
| Shift of the 2045 Cl goal at 5 km through the clay memory (RITMI-GO, dg/dlog b2 = -92.8 mg/L) | 0.6–1.0 mg/L, against posterior sd 1.09 (joint) and 1.25 (cut) |

## Running
`./run_all.sh` (about 10 minutes): `lidhja.py`, `lidhja_summary.py` (needs `../ritmi_go`, `../synthesis`),
`lidhja_figs.py` -> `figL1_leak.png`.
