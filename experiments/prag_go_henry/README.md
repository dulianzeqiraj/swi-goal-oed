# PRAG-GO on the Henry problem

Threshold-risk goal-oriented design ("PRAG-GO") tested on the variable-density Henry
problem, with the same discretization as `src/vd_residual.m` / `src/vd_solve_forward.m`.

The question is whether the monitoring design that maximizes information about the salt
mass near the toe (the project's current goal) also informs the regulatory question
"does salinity at a supply well exceed 1% of seawater?". The scripts also test whether
the PRAG-GO closed form, evaluated with the discrete adjoint, finds the design that is
optimal under the exact, non-linearized expected information gain.

Requirements: Python 3 with NumPy and SciPy; matplotlib for `figs.py`.

## Files

| File | What it does |
|---|---|
| `henry.py` | Python port of the validated Henry solver: cell-centred FV, harmonic face K, upwind advection, Newton with a coloured finite-difference Jacobian. `python3 henry.py` reproduces the README toes 1.4226 / 1.3971 / 1.3918 m (16x8 / 32x16 / 41x21) and the 41x21 residual 3.5e-14. |
| `prag_henry.py` | Stage 1: 12 000 + 2 000 prior realizations (concentrations at 32 candidates, two supply wells, salt mass, toe). Stage 2: discrete-adjoint sensitivities at the prior mean, with a finite-difference check. |
| `designs.py` | Stage 3: all 4 960 three-well designs. Exact EIG of the threshold goals by likelihood re-weighting of the ensemble (common random numbers), against five criteria: linear EIG of the salt mass (Lemma 1), linear EIG of the concentration at well A, and the PRAG-GO closed form with adjoint moments, ensemble moments, and normal-score-transformed ensemble moments. |
| `conv.py` | Re-estimates the selected designs on independent halves of the ensemble with fresh noise. |
| `figs.py` | Figures (setup, selected designs, criterion against exact EIG). |
| `results_summary.csv` | The numbers reported in the note, per prior and criterion. |

## Run

```bash
python3 henry.py                          # solver check against the README numbers
python3 prag_henry.py res_gauss gauss     # ~8 min on 4 cores
python3 designs.py res_gauss gauss 0.01   # ~16 min on 4 cores
python3 conv.py res_gauss
python3 figs.py res_gauss fig_gauss
# other priors: local (sigma 0.7, lengths 0.2 / 0.1 m), facies (mean log-K -0.5 or +0.5)
python3 prag_henry.py res_local local && python3 designs.py res_local local 0.01
python3 prag_henry.py res_facies facies && python3 designs.py res_facies facies 0.01
```

## Set-up

- Prior: per-cell log-conductivity, Gaussian with exponential covariance, sigma 0.5, correlation lengths 0.5 m (x) and 0.2 m (z).
- Supply wells: A at (0.61, 0.12) m and B at (0.80, 0.60) m. Threshold tau = 0.01 (1% of seawater).
- Candidates: 32 points (x in {0.32, ..., 1.68} m, z in {0.12, 0.31, 0.50, 0.69} m), salinity noise sd 0.01, 3 points per design.
- Goals: risk at A, `1{c_A > tau}`, and risk at A or B, `1{max(c_A, c_B) > tau}`; the salt mass in 1.0 < x < 1.6 m is the project's current goal.
