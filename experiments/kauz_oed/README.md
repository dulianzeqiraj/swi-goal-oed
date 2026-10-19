# KAUZ-OED: numerical tests and their verification

KAUZ-OED is the proposed monitoring network for the causal effect R_gp of pumping at well p on mean
salinity in zone g. This folder holds the scripts behind the numbers in the KAUZ-OED section
(Part III, section 8 of the causal-modelling review), plus a verification and extension script.

## Original scripts

These were copied unchanged from the drafting scratchpad. Each one runs from this folder with `python3 <script>`.

| Script | Reproduces | Runtime |
|---|---|---|
| `causal_ou.py` | Test 1 on the true 30-cell transect (p = 8, g = 27, paleochannel 5 to 22): R_gp = 0.0564, naive regression 0.1047, full FDT 0.0564, FDT with S = {p, g} 1.1573, bias formula = direct bias = 1.100925. It also runs the **oracle** greedy selection, which uses the true model: k = 3 gives S = {7, 8, 9, 21, 27} with error 0.0004, against 0.0196 for the nearest neighbours. | < 1 s |
| `causal_prior.py` | The prior-greedy sets from the 60-model design ensemble, evaluated on the true model. These are the sets the KAUZ-OED criterion actually picks. Their error on the true model is not monotone in k: 0.0285 at k = 3 (50.6 %, worse than nearest), 0.0039 at k = 4 and 0.0157 at k = 6. | ~1 s |
| `causal_prior2.py` | The "honest" table: medians of the relative error over 200 independent test models for k = 1..6 (KAUZ, nearest, random), S = {p, g} gives 14.89 and naive regression 0.42. The random column uses only the first 40 test models and 20 random draws per k (median of medians). | ~2 s |
| `causal_l96.py` | Test 2 on Lorenz-96 (N = 20, F = 8, p = 0, g = 3). Direct response 0.0658 (forcing F_0 ± 1, 2 x 100 trajectories), quasi-Gaussian FDT with all nodes 0.1826, with S = {p, g} 0.2364, naive regression -0.1319. It also runs the **in-sample** greedy that minimises abs(FDT_S - FDT_full) on the same data: 0.0016 at k = 4, against 0.0475 for random sets. | ~55 s |
| `l96check.py` | Two independent replicates of the direct response row (0.060 and 0.062 at g = 3, noise sd 0.006), the full FDT row, row correlation 0.774 and the regression row. | ~95 s |

The rerun logs are `kauz_l96_rerun.log` and `kauz_l96check_rerun.log` in the drafting scratchpad. They agree with the numbers above.

## Verification and extensions

`kauz_verify.py` writes `../m_estimators_adaptive/results/kauz_verify.json`. Its sections:

1. **theorem**: checks on 1000 random stable systems (3 to 30 nodes, four families, cond(C0) <= 1e8):
   - the Lyapunov sign, using an independent Kronecker solve and Van Loan;
   - C(tau) = e^{A tau} C(0), checked against an Euler-Maruyama simulation that uses no closed form;
   - the partial-FDT bias formula, the integral formula and the exact FDT for H = {};
   - the exact semigroup-defect identity, and Taylor checks of B_S and D;
   - the necessary and sufficient condition for B_S == 0, with four counterexamples to the wording of the text;
   - symbolic checks with sympy, when sympy is importable.
2. **numbers**: reproduces every number of Test 1 (oracle and prior greedy) and extends the honest table to k = 0..8. It adds 10-90 % bands, bootstrap standard errors and a random baseline on all 200 test models. Optionally it runs a Lorenz-96 robustness check: an independent data set, truncation at 4 vs 8 time units, and the in-sample greedy set evaluated out of sample.
3. **chaos**: a 1-D double well (non-Gaussian but not chaotic). By quadrature it compares the exact score-FDT with the quasi-Gaussian FDT.
4. **pumping**: treats pumping as a parametric perturbation A(Q) = A + Q A1 (+ b Q) of the transect with a sea boundary. It checks d xbar/dQ = -A^{-1}(A1 xbar + b), compares the FDT with effective forcing against the FDT with additive forcing at p, and estimates the response from finite records.
5. **semigroup**: relates the semigroup defect D and the target-specific integrated defect Delta_gp to the (g, p) bias over 200 prior models and many sensor sets. It then runs parametric-bootstrap tests on finite records, sampled exactly from the OU process.
6. **mse**: finite-record variance of the integrated partial-FDT estimate, bias^2 + Var along the KAUZ sequence, and an MSE-greedy design compared with the bias-only design on independent test models.

`fig_kauz_verify.py` draws `../m_estimators_adaptive/figures/fig10_kauz_check.(png|pdf)` from the JSON.

Run (about 8-10 min on two shared cores; sympy is optional):

```
python3 kauz_verify.py            # all sections
python3 fig_kauz_verify.py
```
