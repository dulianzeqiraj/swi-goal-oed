# SIGURIA-GO: a certificate of uncertainty, risk, robustness and uniqueness for a recharge scheme

Innovation of literature review 54, "Uncertainty, risk, robustness and uniqueness of a managed-aquifer-recharge
scheme: new methods from Caltech and Oxford". *Siguria* is Albanian for safety.

**Question.** A managed-aquifer-recharge scheme at Fushë-Kuqe (three injection sites and their rates) is meant to keep
the heads of the supply wells A1 and P10 above h_c = 1 m. How uncertain is its outcome, how large is the risk that a
supply well is still intruded, does it stay safe when the model or the prior is wrong, and are its optimal sites and
rates unique? The scheme is the one chosen by VENDI-GO (review 53, `../vendi_go`), whose model and truth generator are
used here: 12 zonal log-conductivities plus a sub-zonal field, injectivity c = c_ref (T/T_ref) exp(eta), future
recharge (1 + xi) R.

**Theory (section 9 of the review).**
1. *Proposition S1 (convexity).* For a fixed aquifer, H_w(q) = a_w + sum_k g_wk min(q_k, c_k) is concave in the rates,
   so the head deficit D(q) = max_w (h_c − H_w(q)) and its CVaR are convex; on scenarios, minimum-recharge and
   minimum-CVaR schemes are linear programmes (auxiliary delivered rates d_ik <= q_k, d_ik <= c_ik).
2. *Proposition S2 (scenario certificate).* With d = 3 rates, N scenarios and r scenarios discarded because no rate can
   save the wells (injectivity caps), the Campi–Garatti bound gives eps with P^N{violation > eps} <= beta = 1e-6;
   it needs a unique solution, which the face-range test checks.
3. *Proposition S3 (robustness radius in metres).* D is 1-Lipschitz in the two supply-well heads (sup-norm), so for
   every law of the heads within Wasserstein-1 distance rho of the scenario law, CVaR_alpha(D) <= CVaR_alpha + rho/alpha;
   the scheme keeps CVaR_alpha(D) <= 0 for rho <= rho* = alpha (−CVaR_alpha). The distance between the laws given by the
   12-zone model and by the truth generator is bounded by a coupling (same zones, injectivities and climate).
4. *Uniqueness.* Rates: the range of every rate over the optimal face of the LP. Siting: exhaustive search over all
   380 364 admissible lattice triples, the near-optimal set, a simultaneous confidence set for the best triple
   (paired comparisons, Bonferroni), discrete deflation (best triples sharing no well within 2 km), and the
   distribution of the triple that would be optimal for each plausible aquifer.

## Files

- `siguria.py` — scenario ensembles (`python3 siguria.py ensemble`: search 4 000, LP 4 000, validation 20 000,
  12-zone model 4 000, paired with the search set) and the certificate (`python3 siguria.py analyse` →
  `res/siguria.json`), including the certificate of the schemes VENDI-GO builds for prior truths 0–23 under its
  posterior after the pilot tests, and in full for the typical one (median posterior risk).
- `siguria_figs.py` — Figure S1 → `res/figS1_siguria.png`.
- `run_all.sh` — the whole pipeline (needs `../vendi_go/res/setup.npz` and `../vendi_go/res/fig_stats.json`).

## Results (`res/siguria.json`, log in `res/siguria.log`)

| | Best scheme, before tests | PRAG-MAR scheme, before tests | VENDI-GO scheme after tests (truth 18) |
|---|---|---|---|
| P(A or B intruded), 5 000 m³/d per well | 0.226 | 0.228 | 0.024 |
| risk for one aquifer: median / 90% | 0.06 / 0.82 | 0.06 / 0.83 | 0.022 / 0.044 |
| CVaR 5% / 10% of the head deficit (m) | +0.98 / +0.69 | +0.93 / +0.64 | +0.013 / -0.038 |
| robustness radius 5% / 10% (cm) | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.4 |
| P according to the 12-zone model alone | 0.098 | 0.098 | — |

- Before tests, 13.9% of scenarios cannot be saved by any rate up to 20 000 m³/d per well; the scenario programme discards 588 of 4000, needs 55689 m³/d and guarantees eps = 18.8% at beta = 1e-6 (fresh scenarios: 13.9%).
- CVaR split of 15 000 m³/d before tests: 5095, 4272, 5634 m³/d, rates unique to 5.3 m³/d. After tests (truth 18): 9479, 5431, 91 m³/d, posterior risk 0.0024 (equal split 0.024), true risk 0.0082 (equal split 0.051).
- After tests, over prior truths 0–23: certified at 5% in 12 (median radius 0.9 cm), at 10% in 16 (median 1.9 cm); mean posterior risk 0.187, true 0.195; scenario guarantee median 1.2%, held in the true aquifer in 22 of 24.
- Model error: the 12-zone model gives P = 0.098 where the generator with the finer field gives 0.232; coupling bound on W1 of the supply-well heads 43 cm.
- Siting: best 0.2318, PRAG-MAR (also the 12-zone optimum) rank 2 at 0.2319; 13 / 75 / 479 triples within 0.0025 / 0.01 / 0.02; 95% confidence set 3 triples (5 wells); deflation risks 0.232, 0.251, 0.270, 0.273, 0.284; the per-aquifer optimum equals the prior optimum in 1.5% of aquifers (1169 distinct optima, 8.9 bits).
