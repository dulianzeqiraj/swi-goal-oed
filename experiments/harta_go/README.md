# HARTA-GO: transport-map goal-oriented design on the Fushë-Kuqe model

Innovation of literature review 32, after Koval, Herzog & Scheichl, "Tractable optimal experimental
design using transport maps" (*Inverse Problems* 40(12), 2024, https://doi.org/10.1088/1361-6420/ad8260).
*Harta* is Albanian for "the map".

The project's design model of Fushë-Kuqe (geolocated sea boundary, `../prag_go_fushe_kuqe/fk_geo.py`)
with the supply wells and pumping of PRAG-GO is used as it is: 12 uncertain zonal log-conductivities,
16 candidate monitoring wells in the coastal sector read for head (noise sd 0.2 m), and three binary
goals: supply well A reached by seawater (`rA`, h_A < 1 m), A or B reached (`rAB`), and the intruded
area of the sector above its prior median (`rArea`, > 12 km²).

The map. Every reading and goal is sent to a normal score by a monotone one-dimensional map fitted on
the ensemble (the diagonal part of the transport). The lower block of a triangular (Knothe–Rosenblatt)
map then gives each goal variable given the readings of a design,
`z_g = m(z_d) + s(z_d) xi`, with `m` quadratic and `log s` linear in the readings (for `rAB` the second
goal head also depends on the first). Every design's map is fitted from sub-blocks of one Gram matrix,
so one pass over the ensemble serves all 4 368 five-well designs. The expected information gain is
estimated by the Barber–Agakov bound with two-fold cross-fitting. Ablations: `gauss` (raw variables,
linear, constant spread: the ensemble Kalman conditional) and `ns` (normal scores, linear, constant
spread: the Gaussian copula).

## Files

| File | What it does |
|---|---|
| `harta.py` | Library: marginal maps, global quadratic features, per-design triangular map components, goal probabilities (Gauss–Legendre over the first goal head for `rAB`), cross-fitted Barber–Agakov EIG, and the nested Monte Carlo (re-weighting) EIG. |
| `harta_ens.py` | Prior ensembles: 12 000 training runs (the same draws as the PRAG-GO inner ensemble), 48 000 reference runs, 4 000 outer runs and 1 000 test truths. About 3 minutes on 4 cores; writes `harta_ens.npz` (about 10 MB, not committed). |
| `harta_ref.py` | Reference EIG of every 3- and 5-well design and goal by re-weighting the 48 000 reference runs (4 000 / 1 000 outer samples, common random numbers). About 1 hour on 4 cores; writes `harta_ref.npz`. |
| `harta_static.py` | Scores all designs with N = 250 … 4 000 training runs (8 random subsets each) by nested Monte Carlo and by the three map families, and compares with the reference: share of the optimum, share of the constrained optimum (each well available with probability 1/2, 300 patterns) and Spearman correlation. Writes `harta_static.json`. |
| `harta_seq.py` | Sequential choice of three wells for 1 000 synthetic truths, by the Gaussian map, the HARTA map (12 000 and 1 000 runs) and re-weighting (12 000 runs), against the best fixed 3-well design and the design of the project's linearized criterion; every final posterior is computed with the 48 000 reference runs. Writes `harta_seq_<goal>.json`. |
| `harta_figs.py` | Figures `figH1_static.png` and `figH2_seq.png`. |
| `run_all.sh` | Runs every stage in order (about 2 hours on 4 cores). |

## Run

```bash
pip install numpy scipy matplotlib pandas openpyxl     # as for prag_go_fushe_kuqe
bash run_all.sh
```

## Results

- **Exact reference** (48 000 runs). Best 3-well design A3, A10, A23 for `rA` and `rAB` (0.425 and
  0.380 nats), A3, A10, A28 for `rArea`; best 5-well design P17, A3, A10, A13, A23 for `rA` and `rAB`,
  P17, A3, A13, A23, A28 for `rArea`. Mean effective sample size 1 526 (3 wells) and 503 (5 wells).
- **Static designs, three wells** (share of the optimum reached, mean over goals and 8 ensembles).
  Nested Monte Carlo 86.6 / 89.9 / 89.9 / 93.3 / 99.7% with 250 / 500 / 1 000 / 2 000 / 4 000 runs;
  every map family reaches at least 98.6% from 500 runs. The maps need about ten times fewer runs.
- **Static designs, five wells.** All methods are within a few per cent of the optimum (nested Monte
  Carlo 97.7–99.8%, maps 95–98%); the best five-well designs differ by only a few per cent of their
  information, which the simple map families do not resolve. Rank correlation with the exact
  criterion over all 4 368 designs at 1 000 runs: maps 0.94–0.95, nested Monte Carlo 0.64. With 250
  runs the HARTA map ranks poorly (0.49 against 0.82 for the Gaussian map): it needs about 1 000 runs.
- **Cost.** Scoring all 5-well designs for one goal from 4 000 runs: about 20 s with a map, about
  2 000 s with nested Monte Carlo (3 wells: 3 s and 197 s).
- **The project's linearized criterion** (no ensemble) picks the exact optimum for every 3-well goal
  (98.7% on average with five wells).
- **Sequential policies** (three wells chosen one at a time, 1 000 synthetic truths; information
  relative to the best fixed 3-well design in millinats, ± standard error, number of distinct well
  sets in parentheses):

| Goal | Gaussian map | HARTA (12 000 runs) | HARTA (1 000 runs) | Re-weighting (12 000 runs) |
|---|---|---|---|---|
| `rA` | 0.0 ± 0.0 (2) | +4.7 ± 6.4 (16) | −3.8 ± 8.1 (12) | −3.0 ± 7.8 (63) |
| `rAB` | −2.9 ± 6.3 (7) | +7.1 ± 6.6 (9) | −4.0 ± 8.7 (12) | −17.5 ± 8.2 (73) |
| `rArea` | +0.5 ± 3.4 (1) | +0.8 ± 4.3 (17) | −2.0 ± 4.4 (20) | −2.3 ± 5.2 (90) |

  The Gaussian policy hardly adapts; the HARTA policy adapts and never loses against the best fixed
  design; re-weighting adapts most and loses (significantly for `rAB`). Adaptivity gains under 2% of
  the information at Fushë-Kuqe, so a fixed design suffices there.
