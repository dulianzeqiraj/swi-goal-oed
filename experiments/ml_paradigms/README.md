# A diagram series: the problem, four machine-learning paradigms, stakeholder decisions, transfer to a new aquifer

Eight A3 landscape diagrams, English only. The introduction states the problem; four diagrams teach one
machine-learning paradigm each, built from four literature documents of the project; one shows how stakeholders decide
together; two show how the method moves to a new aquifer (routes R1 and R2).
Each has an illustrated schematic, a column with the innovation, and eight numbered panels with the key equations.
The Word versions in `docs/research_notes/` (`Introduction_The_Problem_Statement.docx`, `ML_Paradigm_*.docx`,
`Stakeholder_Decision_Making.docx`, `Transfer_Route_R1_A_Model_That_Can_Travel.docx`,
`Transfer_Route_R2_A_Shared_Representation.docx`) have large type on four A4 landscape pages per diagram: the schematic at full
width, the innovation, then the eight panels four to a page. Every equation in the innovation and the panels is native,
editable Word math (OMML).

| Diagram | Built from | What it shows | Innovation column |
|---|---|---|---|
| `d0_problem.py` (introduction) | `../pusi_go/res/pusi.json` (the test bed: 20,000 weighted draws of a calibrated coastal-aquifer model) | A schematic cross-section (sea, wedge, upconing under a supply well, recharge, head and chloride wells, the unknowns), the risk at the supply wells by head and by chloride, the pumping allowed at 10% risk by data set, and the decision loop with the diagram that answers each step | One goal event, one rule for everyone: the problem in one line (max E[W(a)] s.t. max_k P_k(F(a) given y) ≤ α), chemistry not head (0.044 vs 0.594), one chloride sample doubles the safe pumping (4,221 → 8,417 m³/d) |
| `d5_stakeholders.py` (stakeholder decisions) | `../vendimi_go`, `../rrezja_go`, `../moti_go` results and the 2020–2026 papers of reviews 57–59 | Five beliefs as tilts of one calibration, the unanimous rule and its no-veto choice, what data end a dispute, a belief radius, human factors, plans agreed before each weather | A decision nobody can veto: 5,125 m³/d net with one sample, worst unstated-belief risk 0.119 → 0.089, dry-year risk 0.231 → 0.053 |

| `d6_transfer_r1.py` (transfer, route R1) | the transfer diagrams of the project (route R1) and the assimilation note's test aquifer | The boundaries of a new aquifer T mapped onto the seven classes of the studied aquifer, the dimensionless family, a descriptor space with the certificate B_T, the coverage of a widened interval, the alarm, and three numbers to compute first | The certificate becomes model error: C^f + B_T² I keeps a 90% interval at ≥ 89.99% coverage for any bias (minimum 0.89998 at r ≈ 0.37); the descriptor is a state, so B_T shrinks with every datum; skin distance 200 m against a first piezometer at 250 m, heads alone saw 37% of surges |
| `d7_transfer_r2.py` (transfer, route R2) | the transfer diagrams of the project (route R2) | Seeded illustrations: Theis and sea response functions over T 100–3,000 m²/d and S 0.01–0.2, a shared POD basis (k = 6), an E-optimal set of training aquifers, a new aquifer fitted from n2 readings, and which route for which quantity | The many give the prior: next-year heads to 2.2 cm from four readings where least squares cannot start, 90% intervals cover 0.87–0.90; eight readings give T within 8% and S within 13%; T̂, Ŝ narrow the certificate of route R1 |

`d0` and `d5` read every number from the stored results (`d5_stakeholders.py` also asserts each quoted number against
them); `d6` and `d7` compute their illustrations in the builder from a fixed seed and print the numbers they quote.

The four paradigm diagrams:

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
./run_all.sh         # HTML -> PNG (3600 x 2546), vector PDF (A3 landscape) and a one-page picture copy in Word
./word/build_word.sh # Word versions with OMML equations and large type -> word/out/*.docx (eight diagrams)
```
`d0_problem.py` and `d5_stakeholders.py` look for the results in `../pusi_go`, `../vendimi_go`, `../rrezja_go` and
`../moti_go` (run those experiments first; `d5` also accepts the folder in `SWI_EXPERIMENTS`).
`word/build_word.sh` reads the text and equations of each diagram through `export_content.py` and crops the schematic from
the PNG. `paradigms_word.js` (docx-js) lays out the pages. `omml.py` converts all LaTeX with pandoc to OMML in one run;
`lo_safe.py` and the builder rewrite a few forms, such as \sup, so that LibreOffice also reads them. It needs pandoc 3
and Python with lxml.
Needs Python 3 with numpy, scipy, matplotlib and python-docx, and Node with Playwright and Chromium. `ml_common.py` holds
the page framework (header, schematic helpers, cards, innovation column, one KaTeX batch per page). `render.js <name>`
shrinks an equation wider than its box and fails if one falls below 18 px. It also fails if a panel or the innovation
column overflows, if the title meets the tags, or if a label overlaps another label, a badge or the innovation column,
crosses the edge of a stage panel, or leaves the schematic.
