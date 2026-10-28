# Caltech (and JPL-labelled) mathematical decision tools for stakeholders under uncertainty and climate extremes, 2020–2026: six verified candidates for the Fushë-Kuqe coastal-aquifer review

## Which six papers qualify, how were they screened, and how far could they be verified?

### Takeaway
I found six papers that meet the rules: 2020–2026, peer-reviewed, at least one Caltech author (or one clearly labelled "Jet Propulsion Laboratory, California Institute of Technology"), and none in `_already_covered_references.txt`. They cover the four themes as follows. Theme 1 (decision under uncertainty): Yu et al. 2020 and Schneider et al. 2022. Theme 2 (intense rainfall and emulators of extremes): Kurth et al. 2023. Theme 3 (drought): Farahmand et al. 2021, plus Humphrey et al. 2021. Theme 4 (causal and counterfactual attribution): Humphrey et al. 2021, plus Frederikse et al. 2020. Theme 2 is the thinnest; no Caltech paper on extreme-precipitation statistics as such survived the exclusion list.

### Cited Findings
- **Already covered, so excluded.** Several obvious Caltech candidates appear in the covered list:
  - Dunbar, Garbuno-Inigo, Schneider & Stuart (2021), JAMES, convective-parameter UQ in an idealized GCM;
  - Dunbar et al. (2022), ensemble-based experimental design;
  - Howland, Dunbar & Schneider (2022);
  - Cleary et al. (2021), calibrate–emulate–sample;
  - Hamze Bajgiran, Batlle, Owhadi et al. (2022), "UQ of the 4th kind";
  - Bourdais et al. (2024), PNAS, graph discovery;
  - Eberhardt, Kaynar & Siddiq (2025), and Eberhardt & Lee (2022);
  - Ahmadi et al. (2024), risk-averse decision making;
  - Li et al. (2022), untrusted predictions in LQ control;
  - Christianson et al. (COLT 2022 and COLT 2024);
  - Nakka et al. (2021), chance-constrained trajectory optimisation;
  - Lopez-Gomez et al. (2025), PNAS;
  - Liu, Famiglietti et al. (2022), Nat. Commun.;
  - Zheng & Simons (2025), WRR.

  All were found by grep of `/home/user/swi-goal-oed/research_notes/Stakeholder decisions under climate extremes/_already_covered_references.txt`.
- **Exclusion check for the six kept papers.** I grepped the first-author surname and a title keyword for each. All returned 0 hits: Yu / "power of predictions"; Schneider / "Epidemic management" / "risk-dependent"; Kurth / "FourCastNet"; Farahmand / "Drought cascade"; Humphrey; Frederikse / "causes of sea-level". The covered-list file was the source for this check.
- **Verification limits.**
  - WebFetch could not resolve feeds.library.caltech.edu or ntrs.nasa.gov (DNS blocked in this session).
  - The proxy log shows `api.crossref.org` refused with 403.
  - DOIs and affiliations were therefore confirmed from publisher, PubMed Central, CaltechAUTHORS, NSF-PAR, IDEAS/RePEc and ADS pages as returned by web search, not from Crossref. Each item states which page confirmed it.

### Inferences
- **Suggested pick of five:** Yu 2020 (1), Kurth 2023 (2), Farahmand 2021 (3), Humphrey 2021 (4, with 3), and one of Schneider 2022 (1) or Frederikse 2020 (4, sea boundary).
- Schneider 2022 gives the most directly transferable decision rule (a threshold on posterior risk).
- Frederikse 2020 is the only one acting on our sea boundary.

### Gaps
- No Caltech-campus, peer-reviewed 2020–2026 paper on extreme-precipitation statistics or scaling (e.g. Clausius–Clapeyron scaling, GEV/GPD fits) or on rare-event sampling of rainfall was found that is not already covered. The best CliMA candidate (Dunbar et al. 2021, JAMES, which calibrates on precipitation statistics) is already in the covered list.
- No uncovered Caltech causal-discovery paper on climate or hydrology was found. Eberhardt's causal-feature-learning climate work found here is 2016 (UAI) or software (cfl package, 2022), not a 2020–2026 peer-reviewed paper — [Caltech SASE project page](https://www.sase.caltech.edu/projects/causal.html); [cfl docs](https://cfl.readthedocs.io/en/latest/getting_started/cfl_intro.html).
- Reserve, not counted: "Bayesian Model Averaging of Climate Model Projections Constrained by Precipitation Observations over the Contiguous United States", J. Hydrometeorology 21(10), 2401–2418 (2020), DOI 10.1175/JHM-D-19-0258.1. It reports BMA RMSE 0.49 vs 0.65 for the ensemble mean. The search did not confirm the author list or the JPL affiliation, and the five precipitation metrics may not be extremes. Treat it as **unverified** — [ORNL record](https://impact.ornl.gov/en/publications/bayesian-model-averaging-of-climate-model-projections-constrained/).

## Paper 1 — Yu, Shi, Chung, Yue & Wierman (2020), "The Power of Predictions in Online Control" (Theme 1; normal operation and drought forecasting)

### Takeaway
This is a regret theory for linear-quadratic control when the controller sees k future disturbances. Greedy MPC is near-optimal, and only O(log T) predictions are needed for O(1) dynamic regret. For us, this tells how many years of recharge or rainfall forecast a pumping controller actually needs.

### Cited Findings
- **Citation.** Chenkai Yu, Guanya Shi, Soon-Jo Chung, Yisong Yue, Adam Wierman (2020). "The Power of Predictions in Online Control." Advances in Neural Information Processing Systems 33 (NeurIPS 2020); arXiv:2006.07569 (v1 13 Jun 2020, v4 8 Jan 2021).
  - NeurIPS proceedings carry no DOI. The proceedings URL was confirmed.
  - Page numbers were not confirmed (**unverified**).
  - Sources: [NeurIPS proceedings](https://proceedings.neurips.cc/paper/2020/hash/155fa09596c7e18e50b58eb7e0c6ccb4-Abstract.html); [arXiv](https://arxiv.org/abs/2006.07569).
- **Caltech authors.** The NSF-PAR copy prints Chenkai Yu at IIIS, Tsinghua University and Guanya Shi at CMS, Caltech. The paper is deposited in CaltechAUTHORS (record 104236). Chung, Yue and Wierman are Caltech faculty, but their printed affiliation lines were not shown in the snippet I saw — [NSF-PAR PDF](https://par.nsf.gov/servlets/purl/10208783); [CaltechAUTHORS](https://authors.library.caltech.edu/104236).
- **Problem.** The paper studies predictions in online LQR control with both stochastic and adversarial disturbances. It derives the optimal policy and bounds on cost and dynamic regret in both settings — [NeurIPS abstract](https://proceedings.neurips.cc/paper/2020/hash/155fa09596c7e18e50b58eb7e0c6ccb4-Abstract.html).
- **Main result.** "For length-T problems, MPC requires only O(log T) predictions to reach O(1) dynamic regret, which matches (up to lower-order terms) our lower bound on the required prediction horizon for constant regret." Greedy MPC is near-optimal in both settings — [arXiv abstract](https://arxiv.org/abs/2006.07569).
- **Regret decay.** A NeurIPS reviewer summarises the result as regret decaying exponentially in the prediction horizon — [NeurIPS review page](https://proceedings.neurips.cc/paper/2020/file/155fa09596c7e18e50b58eb7e0c6ccb4-Review.html).

### Inferences
- **The tool in math.** This is the standard form of the setting, written by me; check the exact theorem constants in the paper.
  - Dynamics: x_{t+1} = A x_t + B u_t + w_t.
  - Cost: J = Σ_t (x_tᵀQx_t + u_tᵀRu_t).
  - At time t the controller knows w_t,…,w_{t+k−1}.
  - Dynamic regret: Reg_k = J(MPC_k) − J(OPT_offline).
  - The weight on the i-th future disturbance decays like powers of the closed-loop matrix F = A − BK. So Reg_k shrinks geometrically in k, and k ≈ c·log T suffices for Reg = O(1).
- **How it changes MONTIMI-GO.** Linearise the vertical-section model around the operating pumping. Take:
  - state x = a few slow modes, namely the sea-fraction profile at the screen plus the immobile-zone (silt/clay) concentrations;
  - control u = utility pumping anomaly;
  - disturbance w = inland-inflow anomaly (recharge factor) + private-abstraction anomaly + sea-level anomaly.

  The clay immobile zones give closed-loop eigenvalues close to 1. The geometric decay is then slow, so the required forecast horizon k grows. That argues for multi-year drought outlooks, not just seasonal rainfall, before committing pumping schedules.
- **AR(1) rainfall as free predictions.** With AR(1) rainfall (φ = 0.7), E[r_{t+j} | r_t] = 0.7^j r_t: 0.343 at j = 3 and 0.168 at j = 5 (my arithmetic). These conditional means are "free predictions" for the stochastic case. An MPC that uses them should cut pumping earlier and more conservatively during the first drought year than a myopic rule does.
- **Innovation: a forecast-horizon certificate for the chloride goal.** Define k*(ε) as the smallest horizon at which MPC_k's probability of exceeding 250 mg/L at the screen is within ε of the clairvoyant planner's.
  - Bound k* using the spectral radius of the linearised MONTIMI-GO closed loop together with φ.
  - Test numerically: run MPC_k for k = 0…10 years on the 2-D model with AR(1) recharge, and check whether exceedance saturates at the predicted k*.
  - Feed the residual regret into SPIRANCA's margin as an extra term added to m(b), so the alarm accounts for forecast truncation.

### Gaps
- The exact regret constants and the stochastic-case theorem statement were not read in full text (**unverified**).
- The paper is linear-quadratic. Our model is nonlinear (buoyancy) and has a hard 250 mg/L constraint, so the bound transfers only through linearisation.

## Paper 2 — Schneider, Dunbar, Wu, Böttcher, Burov, Garbuno-Inigo, Wagner, Pei, Daraio, Ferrari & Shaman (2022), "Epidemic management and control through risk-dependent individual contact interventions" (Theme 1; crisis or extreme-event operation)

### Takeaway
"Network data assimilation" (network DA) updates each node's posterior risk from sparse tests and contacts, then acts only on nodes whose risk exceeds a threshold. This decision rule translates almost one-to-one into well-by-well, risk-dependent pumping curtailment driven by sparse chloride samples.

### Cited Findings
- **Citation.** Schneider, T., Dunbar, O. R. A., Wu, J., Böttcher, L., Burov, D., Garbuno-Inigo, A., Wagner, G. L., Pei, S., Daraio, C., Ferrari, R., Shaman, J. (2022). PLOS Computational Biology 18(6): e1010171, published 23 June 2022. DOI 10.1371/journal.pcbi.1010171 — [PLOS](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1010171); [PMC9223336](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9223336/); [IDEAS/RePEc](https://ideas.repec.org/a/plo/pcbi00/1010171.html).
- **Caltech authors.**
  - The arXiv preprint gives the Caltech contact address tapio@caltech.edu [arXiv 2109.10970](https://arxiv.org/abs/2109.10970).
  - The published PDF is hosted on the Caltech Daraio lab site [Daraio lab PDF](https://www.daraio.caltech.edu/publications/Schneider_et_al_PLOS_2022.pdf).
  - MIT DSpace also holds it (Wagner, Ferrari) [MIT DSpace](https://dspace.mit.edu/handle/1721.1/148069).
  - The per-author affiliation lines (Dunbar, Wu, Burov, Daraio at Caltech) were not read directly (**partly unverified**). Schneider at Caltech is confirmed.
- **Tool.** Data assimilation on a contact network produces frequently updated individual risk assessments. These decide who is contacted or isolated — [PLOS](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1010171).
- **Decision threshold.** In the main simulations a classification threshold of 1% was fixed. At the start of interventions this gave roughly a 40% true-positive rate and under about 9% false positives. The authors note that a threshold adapted to current prevalence may improve results — [PLOS/arXiv](https://arxiv.org/pdf/2109.10970).
- **Results (New York City COVID-19 simulations).**
  - Epidemic control with fewer than half the deaths of the NYC lockdown, isolating typically only 5–10% of the population at any time.
  - Up to 2× more infections identified than contact tracing using the same data.
  - With roughly ≥75% adoption and compliance, deaths fall by up to a factor of 4 relative to standard test-trace-isolate.
  - Sources: [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9223336/); [PLOS](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1010171).

### Inferences
- **The tool in math (my condensation).** Posterior π_i(t) = P(node i in the harmful state | tests, contacts) comes from ensemble DA. Act on i if π_i(t) > c. The threshold c is chosen on the true-positive/false-positive trade-off, i.e. the ROC curve.
- **How it changes our decision rule.**
  - Replace the field-wide rule ("cut all pumping when the alarm fires") with a well-by-well rule: curtail well i when P(Cl_screen,i > 250 mg/L next season | heads, chloride samples) > c.
  - Hydraulic connectivity between wells, including private drought wells, plays the role of the contact network.
  - A single annual chloride sample is the analogue of a sparse diagnostic test. This is exactly SPIRANCA's re-anchoring sample, now also propagated to neighbouring wells through the DA.
  - The rule pushes towards targeted, smaller curtailments and towards placing new samples where π_i is near c (largest classification value).
- **Innovation: the risk-network pumping rule with a prevalence-adaptive threshold.**
  - Let c(t) depend on the drought state: lower c when the recharge anomaly is persistent.
  - Show analytically that, for SPIRANCA's anchor-regression alarm, c maps to α in q_{1−α}(b).
  - Numerically compare three strategies on a 5-well MONTIMI-GO field under AR(1) drought: uniform curtailment, a fixed-c risk-dependent rule and an adaptive-c rule.
  - Metric: exceedance-years at supply screens per m³ of curtailed water.

### Gaps
- The setting is epidemiological, not hydrological. The DA method's assumptions (discrete node states, contact networks) need re-deriving for continuous chloride fields.

## Paper 3 — Kurth, Subramanian, Harrington, Pathak, Mardani, Hall, Miele, Kashinath & Anandkumar (2023), "FourCastNet: Accelerating Global High-Resolution Weather Forecasting Using Adaptive Fourier Neural Operators" (Theme 2; intense-rainfall emulator, huge ensembles)

### Takeaway
A neural-operator emulator of global weather runs about five orders of magnitude faster than numerical weather prediction (NWP). That makes ensembles of thousands of members affordable, and such ensembles are the practical route to tail probabilities of intense rainfall that our recharge and flood scenarios need.

### Cited Findings
- **Citation.** Kurth, T., Subramanian, S., Harrington, P., Pathak, J., Mardani, M., Hall, D., Miele, A., Kashinath, K., Anandkumar, A. (2023). PASC '23: Proceedings of the Platform for Advanced Scientific Computing Conference, Davos, 26–28 June 2023. DOI 10.1145/3592979.3593412. The article number and pages were not confirmed (**unverified**) — [CaltechAUTHORS copy](https://authors.library.caltech.edu/records/k959a-53q45); [arXiv 2208.05419](https://arxiv.org/abs/2208.05419).
- **Caltech author.** The Caltech repository copy lists Animashree Anandkumar at the California Institute of Technology. The ar5iv version of the preprint lists NVIDIA and Caltech, and her email on the paper is NVIDIA. The other authors are NVIDIA or NERSC/LBNL — [CaltechAUTHORS](https://authors.library.caltech.edu/records/k959a-53q45); [ar5iv](https://ar5iv.labs.arxiv.org/html/2208.05419).
- **Award.** Best paper at PASC23 — [PASC23 awarded contributions](https://pasc-conference.org/editions/pasc23/program/plenary-sessions/awarded-contributions/).
- **Results.**
  - Medium-range forecasts about five orders of magnitude faster than NWP "while approaching state-of-the-art accuracy".
  - Training time-to-solution of 67.4 min on 3,072 GPUs (JUWELS Booster), and an 80,000× faster time-to-solution than state-of-the-art NWP in inference.
  - Scaling up to 3,808 NVIDIA A100 GPUs.
  - "Enables enormous ensembles that could be used to improve predictions of rare weather extremes."
  - Sources: [arXiv 2208.05419](https://arxiv.org/abs/2208.05419); [CaltechAUTHORS](https://authors.library.caltech.edu/records/k959a-53q45).
- **Companion preprint (not peer-reviewed; label as preprint).** arXiv 2202.11214, also in CaltechAUTHORS 115597, states:
  - a week-long forecast in under 2 seconds;
  - large ensembles "with thousands of ensemble-members";
  - relevance to extremes such as tropical cyclones, extra-tropical cyclones and atmospheric rivers.

  Sources: [arXiv 2202.11214](https://arxiv.org/abs/2202.11214v1); [CaltechAUTHORS 115597](https://authors.library.caltech.edu/115597).

### Inferences
- **The tool in math.** This is a general AFNO description, not quoted from the paper. The autoregressive emulator is x_{t+Δt} = F_θ(x_t). Its spatial mixing is a learned operator applied in Fourier space, z ↦ 𝓕⁻¹[W_θ(𝓕z)]. For decisions, the key is the ensemble estimator of a tail probability: p̂ = (1/N) Σ_n 1{R_n > r*}, with relative standard error √((1−p)/(Np)).
- **Sample-size consequence (my arithmetic).** A 1%-per-season intense-rainfall event estimated to ±10% relative error needs N ≈ 0.99/(0.01·0.01) ≈ 9,900 members. That is only affordable with an emulator.
- **How it changes MONTIMI-GO and SPIRANCA-GO.**
  - Replace the Gaussian AR(1) forcing with emulator-ensemble rainfall, downscaled to the Fushë-Kuqe catchment, to drive (i) the inland-inflow factor and (ii) compound cases where an intense-rainfall storm co-occurs with storm surge at the sea boundary.
  - Estimate q_{1−α}(b) in m(b) from ensemble tails, e.g. a peaks-over-threshold fit, instead of a Gaussian quantile. Heavier tails would widen the margin.
  - For intense rainfall alone, chloride at the screen should fall because inflow rises. The decision shift comes from compound surge-plus-rain events and from flood-driven damage to wells near the coast.
- **Limitation.** FourCastNet forecasts weather out to about a week at 0.25° (ERA5 grid). It does not resolve multi-year drought persistence or a small Adriatic catchment without downscaling.
- **Innovation: a tail-calibrated certified margin.**
  - Prove that, if the rainfall anomaly has a generalized-Pareto tail with shape ξ > 0, the Gaussian-calibrated q_{1−α} undercovers by a computable factor.
  - Test numerically: margins from Gaussian AR(1) versus a heavy-tailed ensemble, run through MONTIMI-GO, with compound surge events.

### Gaps
- Precipitation skill and extreme-precipitation results are in the preprint, not verified in the PASC version.
- No Caltech-campus, peer-reviewed paper on extreme-precipitation statistics or scaling was found outside the covered list.

## Paper 4 — Farahmand, Reager & Madani (2021), "Drought Cascade in the Terrestrial Water Cycle: Evidence From Remote Sensing" (Theme 3; drought propagation to groundwater)

### Takeaway
Drought starts in the atmosphere (vapour-pressure deficit) and reaches total water storage, including groundwater, with growing delays. So our inland-inflow forcing and our alarm anchors should be lagged or filtered drivers, with an atmospheric early-warning anchor, not same-year rainfall.

### Cited Findings
- **Citation.** Farahmand, A., Reager, J. T., Madani, N. (2021). Geophysical Research Letters 48(14), e2021GL093482. DOI 10.1029/2021GL093482 — [Wiley/AGU](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2021gl093482); [ADS](https://ui.adsabs.harvard.edu/abs/2021GeoRL..4893482F/abstract); [GFZ GRACE bibliography](https://www-app2.gfz.de/grace-references/b2hd-2021GeoRL..4893482F.html).
- **Affiliations (clearly labelled JPL).**
  - Reager and Madani are at the Jet Propulsion Laboratory, California Institute of Technology, Pasadena [JPL Reager](https://science.jpl.nasa.gov/people/Reager); [JPL Madani](https://science.jpl.nasa.gov/people/madani/).
  - Farahmand's corresponding email is a JPL domain, but a ResearchGate listing gives California State University Los Angeles [ResearchGate](https://www.researchgate.net/publication/352923902_Drought_Cascade_in_the_Terrestrial_Water_Cycle_Evidence_From_Remote_Sensing).
  - No Caltech-campus author: this is a JPL-labelled paper.
- **Method.**
  - Data: satellite vapour-pressure deficit (VPD), precipitation and GRACE terrestrial water storage (TWS), plus reanalysis column soil moisture.
  - Cases: four major US drought events.
  - Framing: drought starts in atmosphere–land interactions and propagates through soil moisture, surface water and groundwater with delays.
  - The authors report emergent timing patterns that may improve drought predictability.
  - Sources: [Wiley abstract](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2021gl093482); [ADS](https://ui.adsabs.harvard.edu/abs/2021GeoRL..4893482F/abstract).
- **Typical lags, second-hand.** A 2025 GRACE-FO presentation by Reager credits the paper with the precipitation → soil moisture → TWS cascade and gives typical lags of about 2.5 months for soil moisture and about 8 months for TWS. These figures come from slides, not the paper text (**unverified in the paper**) — [Reager 2025 slides](https://cpaess.ucar.edu/sites/default/files/grace-fo-2025-presentation/reager-jt.pdf).
- **VPD lead time.** Citing work reports that VPD detected drought onset months before precipitation. A later VPD index found earlier detection than precipitation-based indices by about 1.33 months on average — [Zeraati et al. 2024, Earth and Space Science](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2023EA003273).

### Inferences
- **The tool in math (my condensation).**
  - Each variable gets a standardised drought index; onset and termination times are dated, and the lags between compartments are estimated.
  - A minimal model consistent with this is a linear-reservoir cascade: τ_k ds_k/dt = s_{k−1} − s_k, for VPD/P → soil moisture → TWS/groundwater.
  - Groundwater response is then rainfall filtered by a kernel h(t) that peaks months later and decays slowly.
- **How it changes MONTIMI-GO.**
  - Replace the instantaneous recharge scaling with a filtered drive: Q_in(t) = Q̄ [1 + β Σ_j h_j r_{t−j}].
  - Combined with AR(1) persistence (φ = 0.7), this delays both the onset and the recovery of inland inflow.
  - Decision consequences: curtail pumping on the atmospheric signal, before the heads fall; restore pumping later than rainfall recovery suggests, because of the longer TWS recovery. That is an asymmetric, more conservative rule after droughts.
- **How it changes SPIRANCA-GO.** Add a VPD anomaly and the filtered rainfall r̃ = h∗r as recorded anchors. Anchor regression certifies shifts only within the span of the anchors. Lagged anchors would extend the certified shift class to persistent drought, and VPD gives early-warning lead time.
- **Innovation: a cascade-anchored alarm.**
  - Theorem target: with anchors A = (VPD_t, r_t, r̃_t, pumping_t), the SPIRANCA margin m(b) certifies all shifts in span(A), which includes the multi-year drought direction absent from the (r, pumping) span.
  - Numerical test: AR(1) rainfall through a two-reservoir cascade into MONTIMI-GO. Compare the false-alarm and miss rates of the two-anchor and four-anchor alarms through a 3-year drought and recovery.

### Gaps
- The exact lag numbers and the case-study list from the paper's full text were not read (**unverified**).
- The US results may not transfer to a Mediterranean karst-alluvial setting.

## Paper 5 — Humphrey, Berg, Ciais, Gentine, Jung, Reichstein, Seneviratne & Frankenberg (2021), "Soil moisture–atmosphere feedback dominates land carbon uptake variability" (Themes 4 and 3; interventional or counterfactual attribution under drought)

### Takeaway
Factorial "switch-off" model experiments act as an intervention: soil moisture is set to its seasonal climatology. Comparing with the control run separates a direct drought effect from an indirect feedback effect, and the indirect one dominates. The same design applied to our simulator would show whether salinisation is driven directly by recharge or indirectly by the human response (private drought abstraction).

### Cited Findings
- **Citation.** Humphrey, V., Berg, A., Ciais, P., Gentine, P., Jung, M., Reichstein, M., Seneviratne, S. I., Frankenberg, C. (2021). Nature 592(7852), 65–69. DOI 10.1038/s41586-021-03325-5. Published online 31 March 2021; open access, CC BY 4.0 — [PMC8012209](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8012209/); [IDEAS/RePEc](https://ideas.repec.org/a/nat/nature/v592y2021i7852d10.1038_s41586-021-03325-5.html).
- **Caltech authors.** Humphrey (lead) and Frankenberg (Caltech GPS); the paper is in CaltechAUTHORS — [CaltechAUTHORS:20210405-150952485](https://resolver.caltech.edu/CaltechAUTHORS:20210405-150952485); [Caltech news](https://ese.caltech.edu/news/soil-moisture-drives-year-to-year-change-in-land-carbon-uptake-1).
- **Method.** GLACE-CMIP5 coupled factorial simulations. Non-seasonal soil-moisture variability is removed in one experiment and compared with a control — [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8012209/).
- **Results.**
  - Soil-moisture variability drives about 90% of the inter-annual variability in global land carbon uptake, mainly through photosynthesis.
  - Soil moisture–atmosphere feedback amplifies temperature and humidity anomalies and strengthens the direct effects of soil water stress.
  - Sources: [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8012209/).
- **Direct versus indirect split.** Press coverage gives the direct effect as about a quarter and the indirect effect as about 75% — [MPI-BGC press release](https://www.bgc-jena.mpg.de/en/pm-soil-moisture).

### Inferences
- **The tool in math (my formalisation).** Write Y = carbon flux in the paper, or chloride at the screen for us.
  - Total effect of driver D: Var[Y] − Var[Y | do(D = climatology)].
  - Direct effect: computed with the feedback path frozen.
  - Indirect effect: the remainder.
  - This is a do-intervention on a simulator, so it is a valid interventional estimand within the model, unlike an observational regression.
- **How it changes MONTIMI-GO.** Run a 2³ factorial design: recharge variability on/off × private-abstraction drought response on/off × sea-level variability on/off. Decompose the chloride variance at the supply screen into main effects and interactions.
  - If the indirect path dominates, as in the paper's atmospheric feedback (drought → private abstraction → lower heads → intrusion), then the decision lever is regulating or metering private abstraction rather than cutting utility pumping.
  - Well placement should also move away from clusters of private wells.
- **How it changes SPIRANCA-GO.** The feedback path is not in the span of the recorded anchors (rainfall, utility pumping), so the anchor-regression certificate does not cover it. Either add private abstraction (or a proxy, e.g. electricity use) as an anchor, or inflate δ̄ by the simulated indirect share.
- **Innovation: a causal decomposition certificate for salinisation.**
  - Prove that the factorial decomposition is additive up to an interaction term, and bound that term by the cross-sensitivity of the screen chloride to (recharge, abstraction) from the MONTIMI-GO adjoint.
  - Test numerically whether the bound predicts the observed interaction in the 2³ runs, and whether a SPIRANCA alarm with the extra anchor stays valid under the human-feedback shift.

### Gaps
- The paper concerns carbon uptake, not water supply. The 75%/25% split is from a press release, not checked in the paper text.

## Paper 6 — Frederikse, Landerer, Caron, Adhikari, Parkes, Humphrey, Dangendorf, Hogarth, Zanna, Cheng & Wu (2020), "The causes of sea-level rise since 1900" (Theme 4 attribution; compound or sea-boundary case)

### Takeaway
A closed, probabilistic sea-level budget splits sea-level change into named causes with uncertainties. That gives a structured, attributable way to build the sea-boundary scenarios of our model, and to decide which component's uncertainty matters for chloride at the screen.

### Cited Findings
- **Citation.** Frederikse, T., Landerer, F., Caron, L., Adhikari, S., Parkes, D., Humphrey, V. W., Dangendorf, S., Hogarth, P., Zanna, L., Cheng, L., Wu, Y.-H. (2020). Nature 584(7821), 393–397, published 19 August 2020. DOI 10.1038/s41586-020-2591-3 — [IDEAS/RePEc](https://ideas.repec.org/a/nat/nature/v584y2020i7821d10.1038_s41586-020-2591-3.html); [CaltechAUTHORS 105088](https://authors.library.caltech.edu/105088).
- **Caltech/JPL authors.** Per the EGU record, Landerer, Caron and Adhikari are at JPL (Caltech), and Humphrey is in Caltech's Division of Geological and Planetary Sciences (a campus author). Frederikse was a JPL postdoctoral fellow — [EGU2020-7907](https://meetingorganizer.copernicus.org/EGU2020/EGU2020-7907.html); [JPL news](https://www.jpl.nasa.gov/news/nasa-led-study-reveals-the-causes-of-sea-level-rise-since-1900/).
- **Results.**
  - The budget reconciles observed global-mean sea-level rise since 1900 with the sum of processes, so no additional processes are required.
  - Ice-mass loss, predominantly from glaciers, caused twice as much rise as thermal expansion.
  - A sharp increase in reservoir impoundment explains the lower-than-average rates in the 1970s.
  - Sources: [CaltechAUTHORS](https://authors.library.caltech.edu/105088); [JPL news](https://www.jpl.nasa.gov/news/nasa-led-study-reveals-the-causes-of-sea-level-rise-since-1900/).
- **Conflict between sources on the high-rate decade.** The published abstract (Caltech record) attributes the high rates to glaciers and Greenland in the 1940s. The EGU abstract says the 1930s — [CaltechAUTHORS](https://authors.library.caltech.edu/105088) vs [EGU2020-7907](https://meetingorganizer.copernicus.org/EGU2020/EGU2020-7907.html).
- **Rate.** The global-mean rate is described as about 1.5 mm/yr since 1900. The precise figure and its interval were not confirmed (**unverified**) — [search summary of the abstract](https://bibliotheque.meteo.fr/pub/DOC00051568-the-causes-sea-level-rise-since-1900.html).

### Inferences
- **The tool in math (my condensation).** GMSL(t) = Σ_k c_k(t) + ε(t), with components: thermosteric, glaciers, Greenland, Antarctica, land water and reservoirs. Each c_k has its own probabilistic ensemble, and closure means ε stays within uncertainty.
- **How it changes MONTIMI-GO.**
  - Write the sea Dirichlet head as h_sea(t) = MSL₀ + Σ_k c_k(t) + VLM(t) + tide(t) + surge(t). Here VLM(t) is local vertical land motion; it is not in a global budget and must be measured locally.
  - Draw each component from its own uncertainty band rather than one lumped sea-level-rise scenario.
  - Decision effects: well setback distance and the chloride margin respond mainly to the slow, attributable components, while surge drives short exceedance spikes.
  - This argues for monitoring both a tide gauge and GNSS vertical land motion at the coast.
- **Innovation: a budget-structured sea boundary with goal-oriented attribution.**
  - Compute the variance share of each c_k (and of VLM and surge) in the 2050 chloride at the screen, using the MONTIMI-GO adjoint and Monte Carlo.
  - Theorem target: under linearised response, the chloride variance decomposes as Σ_k (∂Cl/∂h_sea)² Var(c_k) plus covariances. Monitoring value is then highest for the component with the largest product of sensitivity and uncertainty.
  - Use the result to choose which coastal measurement to fund, and how much inland to move the supply well.

### Gaps
- Regional (Adriatic) budget components and local vertical land motion are not provided by this global study as far as verified. Storm-surge extremes are not part of it.
- It is an attribution budget, not a formal causal-inference method. The "causal" label applies only in the attribution sense.
