# Four machine-learning paradigm diagrams

Four A3 landscape diagrams that teach one machine-learning paradigm each, built from four literature documents of the
project. Each has an illustrated schematic with computed pictures, a column with the innovation, and eight numbered
panels with the key equations of the 2020–2026 papers. English only. Word copies (one A3 page each) are in
`docs/research_notes/ML_Paradigm_*.docx`.

| Diagram | Source document | Paradigm | Innovation column |
|---|---|---|---|
| `d1_robust_design.py` | Robust optimal Bayesian design for infinite-dimensional inverse problems, 20 papers 2020–2026 | Learning where to measure: robust design as a game with nature, a design policy learned by REINFORCE, bounds you can optimise | Certified robust design: envelope design in one solve (loss 0.07%), the fixed-MAP utility is not the EIG (25% of designs change) and a function-space Barber–Agakov certificate, convexity in the noise covariance (saddle point, mixed-integer robust c-optimal design) |
| `d2_causal.py` | Review 49, causal generative modelling | Learning causes, not correlations: latent causal models, interventions, scores, counterfactuals, diffusion and transport | Known signatures replace interventions: fibre dimension (n−k)(n−1), one source regime identifies its counterfactual, query identifiability J_qN = 0 |
| `d3_deep_rl.py` | Review 52, the landmark theory of deep RL | Learning to act from data: TD as stochastic approximation, policy-gradient landscapes, offline pessimism, sample complexity | The years of data any learner needs: N_ε = tr(HI⁻¹)/(2εJ*), 20.9 years for 1% with near-optimal operators, what shortens them |
| `d4_value_info.py` | Value of information without a prior, 20 publications 2020–2026 | Learning what data are worth: Blackwell order, Wald's minimax regret, ambiguity, DEC/IDS, DRO, e-values | Minimax-regret value of a monitoring network and an alarm as an e-process (a proposal; open questions listed) |

**Computed pictures** (illustrations, not results of the source documents):
- **Diagram 1:** a prior field m ~ N(0, A⁻²) with 64 candidate sensors; 8 sensors chosen greedily under the noise envelope of result 1 (c = 0.783 over correlation lengths 0.02–0.25); the solution of −∇·(e^m∇u) = 1; the noise correlation; the posterior standard deviation and the information spectrum.
- **Diagram 2:** the test bed of review 49: three latent processes, seven ions, baseline and two regimes. Also the counterfactual of the sampled unit (seawater fraction halved, z_s = 0.0120), and an Ornstein–Uhlenbeck noising of the data.
- **Diagram 3:** linear TD on a 7-state chain (error 0.464, bound 1.484); softmax and natural policy gradient on a 10-state chain; greedy versus pessimistic choice from 300 logged decisions; the years-of-logs numbers of review 52, section 9.
- **Diagram 4:** regret curves of a two-action problem. Maximum regret is 1.00 with no data, 0.50 when randomising, and 0.054 with 10 samples, so the minimax-regret value of the data is 0.45. Maxmin welfare values the same data at 0. A simulated e-process alarm: 10 of 20,000 null paths alarmed at α = 0.001; the median delay after a shift of +0.6 was 60 months.

## Build
```
npm install          # once: KaTeX 0.16.11
./run_all.sh         # HTML -> PNG (3600 x 2546), vector PDF (A3 landscape) and a one-page Word copy for each diagram
```
Needs Python 3 with numpy, scipy, matplotlib and python-docx, and Node with Playwright and Chromium. `ml_common.py` holds
the page framework (header, schematic helpers, cards, innovation column, one KaTeX batch per page). `render.js <name>`
shrinks an equation wider than its box and fails if one falls below 18 px. It also fails if a panel or the innovation
column overflows, if the title meets the tags, or if a label overlaps another label, a badge or the innovation column,
crosses the edge of a stage panel, or leaves the schematic.
