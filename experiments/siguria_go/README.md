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
  `res/siguria.json`), including the certificate of the scheme VENDI-GO builds for one prior truth, under its
  posterior after the pilot tests.
- `siguria_figs.py` — Figure S1 → `res/figS1_siguria.png`.
- `run_all.sh` — the whole pipeline (needs `../vendi_go/res/setup.npz` and `../vendi_go/res/fig_stats.json`).
