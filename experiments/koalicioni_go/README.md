# KOALICIONI-GO: which coalition of well-record holders, in what order, and who deserves what

Innovation of literature review 56, "Is merging worth it? II. Which coalition of well-record holders, in what order,
and who deserves what: twenty more papers from Oxford, Caltech, MIT, Princeton and Harvard". *Koalicioni* is
Albanian for the coalition. It extends BASHKIMI-GO (review 55, `../bashkimi_go`) from one merge to coalitions of
five holders and reuses its truth generator, Bayesian CATE model and decision value. Anchor paper: Fawkes,
Ter-Minassian, Ivanova, Shalit & Holmes, "Is merging worth it? Securely evaluating the information gain for causal
dataset acquisition", AISTATS 2025 (PMLR 258).

**Question.** The Fushë-Kuqe water utility (60 records) can merge the well records of five holders: a monitoring
agency (300 records, half pumped high), private irrigators (120, 85%), coastal hotels (32, *all* pumped high in
summer), municipal coastal wells (40, *all* pumped low because the law caps them) and a research campaign (24,
designed). Which coalition should it form, in what order, when should it stop, and how should the value be shared,
all before any record is shared?

**Theory (section 9 of the review).**
1. *Proposition K1.* The value of any coalition depends on the records only through the sum of the holders' Gram
   matrices; one private release per holder (clipped whitened information plus Gaussian noise) gives all 31
   coalition values as post-processing, instead of a 16-fold composition.
2. *Proposition K2.* A holder that sees one pumping regime carries (almost) no CATE information alone, but its
   marginal information is never below its standalone information (superadditivity of the Schur complement); the
   decision value saturates, so information complementarity need not become value complementarity.
3. *Proposition K3.* With the utility as a veto player the core is never empty; Shapley is in the core if the game
   is convex; and paying each *block* of holders (e.g. a complementary pair) its marginal contribution to the
   grand coalition is in the core when the value is submodular over blocks.
4. *Proposition K4.* Adaptive merging (merge, update with the real records, re-value, stop when no merge pays its
   cost) needs only Gram matrices and the current posterior, and the best adaptive policy is never worse than the
   best fixed coalition.

## Files

- `koalicioni.py`: holders, the two models (`KOA_DRIFT=1`: physics-informed with a Gaussian field for the local
  coastal drift; `KOA_MODEL=local`: local statistical model without physics), coalition values, realised gains
  (20 outcome draws), merge policies, Shapley/Banzhaf, convexity and core, robustness, privacy.
- `koalicioni_summary.py` → `res/koalicioni_summary_drift.json`, `res/koalicioni_summary_local.json` (also the
  marginal and pair sharing rules); `koalicioni_figs.py` → `res/figK1_koalicioni.png`.
- `run_all.sh`: the whole pipeline.

## Results (200 aquifers; loss units)

- Municipal wells alone: physics-informed predicted 0.0067, realised -0.0001 ± 0.0051;
  local model predicted 0.0146, realised -0.095 ± 0.046 (harmful).
- Hotels + municipal is the only pair predicted complementary in most aquifers (96% physics,
  100% local); realised synergy +0.0235 ± 0.0151 and +0.105 ± 0.039.
- Net benefit of the merge policies (best single / greedy / optimal fixed / adaptive / all / hindsight oracle):

| model | cost | single | greedy | optimal | adaptive | all | oracle |
|---|---|---|---|---|---|---|---|
| physics | 0.00 | +0.0349 | +0.0552 | +0.0552 | +0.0552 | +0.0552 | +0.0756 |
| local | 0.00 | +0.2052 | +0.2509 | +0.2509 | +0.2509 | +0.2509 | +0.2902 |
| physics | 0.01 | +0.0252 | +0.0240 | +0.0237 | +0.0255 | +0.0052 | +0.0606 |
| local | 0.01 | +0.1952 | +0.2089 | +0.2035 | +0.2135 | +0.2009 | +0.2687 |
| physics | 0.02 | +0.0161 | +0.0154 | +0.0160 | +0.0145 | -0.0448 | +0.0513 |
| local | 0.02 | +0.1853 | +0.1870 | +0.1869 | +0.1908 | +0.1509 | +0.2540 |
| physics | 0.04 | +0.0057 | +0.0057 | +0.0057 | +0.0055 | -0.1448 | +0.0395 |
| local | 0.04 | +0.1655 | +0.1623 | +0.1619 | +0.1623 | +0.0509 | +0.2339 |

- Sharing (utility as veto player): Shapley share of the utility 63% / 62%;
  Shapley in the core in 2.5% / 2.0% of aquifers; each holder's own marginal
  contribution in the core in 4.0% / 0.0%; the hotels and municipal
  wells paid jointly (pair rule) in the core in 88.0% / 65.5%.
- Privacy, one release per holder: Kendall τ of the private Shapley ranking 0.39 → 0.73
  (physics) and 0.40 → 0.83 (local) for ε = 1 → 30; clipping never overstated a value.
- Banzhaf is not more robust than Shapley to noise in the coalition values (differences in τ below 0.01).

Limits: simulated aquifers and holders; linear-Gaussian models with known noise; binary treatment; equal merge cost;
stability checked on predicted values; the complementary pair is named from the predicted synergies.
