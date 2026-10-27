# ASIMILIMI-GO: updating boundary and initial conditions by data assimilation, and why the update is right

Numerical checks of the technical note *Updating the boundary and initial conditions of the Fushë-Kuqe system by data
assimilation: the expanded equations, and why the update is right* (October 2026,
`docs/research_notes/Fushe_Kuqe_Data_Assimilation_Boundary_Initial_Conditions_Theorems.docx`). The note puts the twenty
papers of the author's document on dynamic data assimilation for missing dynamics into the equations of the complete
Fushë-Kuqe system (augmented state: initial fields, aquitard legacy as internal variables of a Markovian memory,
boundary forcings as stochastic processes, closure for missing dynamics) and proves seven results. *Asimilimi* is
Albanian for the assimilation.

**Test bed.** The linear coastal aquifer of FILLIMI-GO and KUFIRI-GO (5 km, 50 cells, sea Dirichlet at x = 0, no flow
inland, T = 1000 m²/d, Sy = 0.1, aquitard compartments with rates 0.05, 0.5, 2 /yr, well at 1.5 km). Unknowns: initial
head and legacy (fastest compartment in equilibrium: a linear constraint), interannual sea level and recharge anomaly
(Ornstein–Uhlenbeck), sea-level offset η0, unlicensed pumping E, closure on four hat functions. Data: heads at 250,
1250, 2750, 4250 m, monthly for 10 years, sd 0.02 m. Exact discretisation (matrix exponential; forcing covariance by a
block exponential on a small step and doubling); exact posteriors by Gaussian conditioning on all 480 data.

## Results (`res/asimilimi.json`, `res/run_log.txt`)
- **Theorem 1 (head block exact).** Ensemble smoother error of the posterior mean, in exact posterior sd: 1.1–7.0 with
  25 members, 0.13–0.27 with 1,600; slopes −0.61 (mean) and −0.79 (sd) against log N.
- **Theorem 3 (initial conditions saturate, boundary parameters accumulate).** Initial head (first km): prior sd 0.172,
  posterior 0.105 m after 3 months and 0.104 m after 30 years; lower bound of the theorem 0.097 m. Unlicensed pumping
  E: 26.0, 5.9, 3.1 m³/d per km after 1, 10, 30 years (prior 150). Half of the information about the initial head comes
  from the first year.
- **Theorem 4 (forgetting, bounded missing source).** Two filters started 0.5 m apart: largest head gap 7e-4 m after one
  year, 1e-4 m after ten; Lyapunov function monotone. A missing source of 0.08 m/yr at 3 km: free drift 0.57 m, filter
  error at most 0.075 m.
- **Theorem 5 (boundary vs closure).** Uniform recharge error and uniform closure: cosine 1, the difference keeps its
  prior sd (0.0283 m/yr). Unlicensed pumping vs a closure bump at the well: cosine 0.989; including the closure raises
  the sd of E from 5.9 to 60 m³/d per km, a meter brings it to 27. Coverage of 90% intervals for E over 400 twins: 91%
  (correct model), 11% (missing sources, no closure), 91% (closure added).
- **Theorem 7 (chloride).** One sample at the mean interface depth: RMSE of the head update (prior sd units) exact 0.16,
  censored probit 0.17, EnKF 0.37, plain probit 0.54; EnKF distance from exact grows with the non-Gaussianity of the
  predicted chloride (correlation 0.99 over nine screen depths).
- **Proposition 6.** The equilibrium constraint survives the ensemble update exactly; an EnKF on the sea fraction
  leaves 10.5% of members outside [0, 1].

## Files
- `asimilimi.py` → `res/asimilimi.json` (about 75 s on 4 cores).
- `asimilimi_figs.py` → `res/figA1_asimilimi.png`, `res/figA2_asimilimi.png`.
- `run_all.sh`.
