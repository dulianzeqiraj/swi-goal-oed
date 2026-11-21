# KAOS-GO: from chaos in the pores to Darcy's law

Code and results of the review *From chaos in the pores to Darcy's law* (November 2026, English):
`docs/literature/Literature_review_Chaos_in_the_Pores_to_Darcy_Law_Upscaling_KAOS-GO_Caltech_Oxford_MIT_Harvard_Max_Planck_2020-2026.docx`.
*Kaos* is Albanian for chaos.

The review does five things:
- it identifies the Princeton article behind the question (Browne & Datta, *Science Advances* 2021: chaotic flow of a
  polymer solution in the pores, anomalous resistance at the large scale) and states what it says about Darcy's law;
- it explains the passage from a chaotic small scale to a deterministic large-scale law in three statements
  (Propositions 1 and 2 below);
- it presents twenty-five papers of 2020–2026 from Caltech, Oxford, MIT, Harvard and the Max Planck Society (five each),
  sorted into five routes of explanation, each card with its link, its affiliation evidence and an innovation step;
- it proposes and tests **KAOS-GO**, an upscaling in which the large-scale law carries its own tested error;
- it lists possible partners, tied to verified papers.

## The three propositions

**Proposition 1 (the resistance is the dissipation).** For a statistically stationary flow of a Newtonian fluid through
a periodic cell under a uniform force G, with U the Darcy velocity, `G U = Φ[mean flow] + mean Φ[fluctuations]`, where
Φ is the viscous dissipation per unit volume. The resistance R = G/U is therefore the sum of a mean-flow part and a
fluctuation part, and R ≥ μ/K: the Darcy permeability is an upper bound of the apparent permeability of any flow of a
Newtonian fluid through the same medium (Helmholtz's minimum-dissipation theorem).

**Proposition 2 (law of large numbers and central limit).** The mean of the flux over a window T has variance
σ∞²/T, with σ∞² the integral of the autocovariance of the flux; in a random medium at rest the conductivity of a block
of N grains scatters as N^(-1/2).

**Proposition 3 (where to spend the small-scale effort).** For a decision J = Σ a_j F_j over the levels of the closure,
with variance σ_j²/T_j at level j, a fixed budget is best spent as T_j ∝ |a_j| σ_j / √c_j (c-optimal design).

## The experiment

A periodic two-dimensional cell with 16 circular grains placed at random (solid fraction 0.2), a Newtonian fluid driven
by a uniform force, solved with a lattice-Boltzmann method (`lbm.py`: D2Q9, two relaxation times, force after Guo,
halfway bounce-back; numba). The viscosity is lowered through 14 levels, from the Darcy regime to a chaotic one. It is
not the Princeton system: the chaos here is inertial, not elastic; the balance and the statistics have the same form.

| file | what it does |
|---|---|
| `lbm.py` | the solver; strain rate and dissipation from the non-equilibrium populations |
| `kaos_gates.py` | gates: Stokes drag of a square array against Sangani & Acrivos (1982), energy budget, independence of viscosity and force |
| `kaos_run.py` | one run: spin-up, sampling of cell means and time-averaged fields, largest Lyapunov exponent by a twin run |
| `kaos_rev.py` | Darcy coefficient of 64, 32 and 12 cells with 4, 16 and 64 grains |
| `kaos_check_stats.py` | gate of the statistics: the window-mean intervals on synthetic series with a known correlation time |
| `kaos_exp.py` | analysis: regimes, dissipation split, Lyapunov exponents, finite-size scatter, window-mean statistics and coverage, closures, the well-loss decision and the allocation |
| `kaos_figs.py` | the seven figures |
| `cards_kaos.py`, `text_kaos.py`, `build_kaos_doc.py` | the cards, the text and the Word builder |
| `fetch_refs.py` | Crossref records of the references → `res/refs.json` |
| `run_all.sh` | everything, in order (about 2 hours on four cores) |

Results kept in `res/`: `kaos.json` (every number of the review), `kaos_fields.npz` and `kaos_series.npz` (for the
figures), `refs.json`, `selected_papers.json` (Crossref and OpenAlex records of the twenty-five papers), `gates.json`.
The raw runs are not kept.

## Protocol notes

- The gates were run before any result was read. The coarsest lattice (12 nodes per grain radius) passes the gates for
  the flux and the Lyapunov exponent but fails the energy budget in the chaotic regime (dissipation 22% above the power
  of the force); it was not used. All results are for 18 nodes per radius; a run with 24 nodes checks them at the
  highest Reynolds number.
- The statistics code was checked on synthetic series of known correlation time (`kaos_check_stats.py`,
  `res/stats_gate.json`) before the long runs were analysed.
- The levels, the window lengths (5, 10 and 20 transit times) and the burn-in lengths of the coverage test were fixed
  in `run_all.sh` and `kaos_exp.py` before the sweep was run. A window of 40 transit times was added after the sweep
  showed a correlation time of about 12 transit times at one level, before the long runs were analysed; it is reported
  separately. Every level and every window is reported.
- The twin-run measurement of the Lyapunov exponent was checked at a steady level (Re = 26), where a perturbation must
  decay: it gives a negative exponent (`lyap_control` in `res/kaos.json`).
- In the allocation of Proposition 3 the noise of each level is taken from its longest record (the long run where one
  exists, the sweep run otherwise); this was fixed before the long runs were analysed.
- The first long run showed a memory of tens of transit times at the level nearest to the onset of chaos. Three things
  were added after that and are labelled as additions in the text: the coverage is reported level by level (the pooled
  figure, fixed in advance, is kept); the scatter of window means is compared with the prediction of the measured
  autocovariance for a finite window, not only with the central-limit line; and the statistics gate received a case
  with a correlation time of 30 transit times and the spread of the coverage between single records. The long memory
  was not repeated on another lattice.
- The certificate is tested on window means of the flux of one cell, where the truth is known. Its transfer to a field
  decision is not tested here.

## Limits

Two dimensions; one arrangement of 16 grains in the unsteady regime; inertial, not elastic, chaos; the scatter between
cells measured in the Darcy regime only; the Lyapunov exponent is that of the lattice-Boltzmann dynamics.
