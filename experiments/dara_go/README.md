# DARA-GO: certified design decisions from one order-preserving transport map

Innovation of the study edition of Koval, Herzog & Scheichl, "Tractable optimal experimental design using
transport maps" (*Inverse Problems* 40(12), 125002, 2024, https://doi.org/10.1088/1361-6420/ad8260; arXiv
2401.07971). *Dara* is Albanian for "the pincers": two jaws closing on the information from both sides.

**The article's idea, reimplemented.** A triangular (Knothe–Rosenblatt) map of the joint law of design, data
and inference variables, built as a squared tensor train (squared inverse Rosenblatt transport), gives the
evidence p(y | ξ) and the posteriors p(θ | y, ξ) for every design and every data set.

**The innovation.** Evaluate the map at exact prior-predictive samples (one model run each, no inner loop):

    L(ξ)  = E[ln p~(w | y, ξ) − ln p(w)]            ≤ I(θ; y | ξ)      (posterior bound)
    U(ξ)  = E[ln π(y | θ, ξ) − ln p~(y | ξ)]         ≥ I(θ; y | ξ)      (evidence bound)
    G(ξ)  = U − L = KL( p(y, w | ξ) ‖ p~(y, w | ξ) )                   (Theorem 3)
    Lq(ξ) = E[ln p~(q | y, ξ) − ln p(q)]  ≤  I(q; y | ξ)  ≤  Lq(ξ) + G(ξ)   (Theorem 4, goal first in the order)

The two bounds are those of Barber & Agakov (2003) and Foster et al. (2019); what is new is that one map gives
both for all designs, that their gap is exactly the map's Kullback–Leibler error at each design, and that the
same gap brackets the information about any goal placed first among the inference variables. A design whose
upper bound is below the best lower bound is provably not optimal (Proposition 4), so the decision is certified.

## Test problem

Confined coastal cross-section, coast at x = 0 (head 0), inland boundary at 5 km (head 5 m), three
conductivity zones (0–1, 1–2.5, 2.5–5 km), ln K_i = ln 20 + 0.5 z_i with z ~ N(0, I). The design is the
position ξ of one observation well (head error 0.1 m); the goal is the log toe position of the saltwater
wedge from Glover's solution, at resolution τ = 0.08. Exact information curves follow from quadrature
(`dara_ref.py`). The best well for the conductivities is at 2.5 km (1.97 nats); the best well for the toe
is at 1 km, the landward edge of the coastal zone (1.28 nats), where the conductivity-optimal well gives
only 0.19 nats.

The map is ordered (design, head, goal, z1, z2, z3) on 49 design nodes (100–4 900 m).

## Files

| File | What it does |
|---|---|
| `dara_model.py` | Heads, discharge and Glover toe of the three-zone cross-section; prior and constants. |
| `dara_ref.py` | Exact information about the parameters and about the goal, by binning four million prior draws on fine grids and convolving with the exact Gaussian kernels. |
| `dara_tt.py` | From-scratch tensor-train tools: maxvol, randomized SVD, two-site cross approximation, and the squared inverse Rosenblatt transport (exact marginals of leading blocks via mass matrices, conditional sampling by cubic inverse distribution functions, defensive mixture). |
| `dara_setup.py` | Grids, the square root of the joint density, exact samples, and the affine (Gaussian Knothe–Rosenblatt) preconditioning layer per design node. |
| `dara_exp.py` | Builds maps A–D, computes L, U, G, Lq and Lq + G at 47 well positions with 40 000 exact samples each, the pure-map estimates, certified sets and a nested Monte Carlo baseline; writes `dara_results.json` and `dara_maps.npz` (cores of map D, about 4 MB, not committed). About 8 minutes on 4 cores. |
| `dara_figs.py` | Figures `figD1_problem.png`, `figD2_map.png`, `figD3_dara.png`. |
| `run_all.sh` | Runs every stage. |

## Run

```bash
pip install numpy scipy matplotlib
bash run_all.sh
```

## Results

| Map | Preconditioning, max rank | Error of √p | Median gap (nats) | Certified wells, conductivities | Certified wells, toe |
|---|---|---|---|---|---|
| A | none, 20 | 37.6% | 2.11 | 300–4 500 m (43 of 47) | 200–4 600 m (45 of 47) |
| B | affine layer, 8 | 10.3% | 0.15 | 2 000–2 900 m | 800–1 300 m |
| C | affine layer, 20 | 3.5% | 0.036 | 2 400–2 600 m | 1 000–1 100 m |
| D | affine layer, 40 | 1.5% | 0.008 | 2 500 m | 1 000 m |

- The exact information lies inside both brackets at every position for every map within three standard
  errors (within two at 98% or more of the positions); a poor map gives a wide bracket, never a wrong one.
- One affine layer reduces the density error tenfold at equal rank (37.6% to 3.5%); this is the
  preconditioning mechanism the article uses across sequential stages.
- The gap follows the map error (2.11, 0.15, 0.036, 0.008 nats) and is computed without the exact answer;
  its paired Monte Carlo error is about 0.001 nats, against 0.005 for each bound.
- Pure-map estimates (samples drawn from the map) of maps C and D put the toe well at 0.8 km and 1.1 km,
  outside their certified sets. Nested Monte Carlo with 2 000 + 2 000 samples errs by up to 0.06 nats.
- Designing for the conductivities would place the well at 2.5 km and lose 85% of the information about the
  toe.

Caveats: a steady, confined, three-zone test bed with a sharp-interface toe, not the Fushë-Kuqe model; the
two-site cross approximation used 1.1·10⁷–2.2·10⁸ density evaluations, cheap here only because the model is
analytic; the affine preconditioner is simpler than the article's tensor-train preconditioning.
