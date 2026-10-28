# Harvard-authored mathematical decision tools for stakeholders under uncertainty and climate extremes (2020–2026), read for coastal-aquifer management (Fushë-Kuqe: MONTIMI-GO / SPIRANCA-GO)

Verification note for the report writer. In this session the agent proxy blocked direct access to api.crossref.org, arxiv.org and pmc.ncbi.nlm.nih.gov, so I could not open the PDFs or resolve DOIs on doi.org or Crossref. Each DOI below was checked against a publisher, proceedings or institutional-repository record that a web search returned (OUP, Lancet/Elsevier, AAAI OJS, PMLR, Nature Food via the Southampton ePrints and Harvard DASH records). Where a number or an affiliation comes only from a search summary and not from the paper text, I say so. Equations written "in our notation" are my restatement of the method as the sources describe it, not quotations.

## Selection overview and exclusions (applies to all candidates)

### Takeaway
There are six verified candidates and one reserve. They cover theme 1 (decision rules: budget-constrained RL for alert issuance; minimax-regret robust RL), theme 2 (tropical cyclones and severe floods), theme 3 (water supply / soil moisture vs. heat in drought damages) and theme 4 (incremental stochastic interventions for alert policies; two-stage causal-predictive models for storms; self-matched distributed-lag designs for floods). Every candidate has a Harvard author. I checked each one against `_already_covered_references.txt` by first-author surname, a title keyword and the DOI or arXiv id.

### Cited Findings
- Candidates kept (DOI or proceedings URL in brackets):
  1. Considine, Nethery, Wellenius, Dominici & Tec (2025), AAAI-25, "Optimizing Heat Alert Issuance with Reinforcement Learning" [10.1609/aaai.v39i27.35009]: themes 1 (+ heat extreme) — [AAAI OJS](https://ojs.aaai.org/index.php/AAAI/article/view/35009)
  2. Xu, Perrault, Fang, Chen & Tambe (2021), UAI 2021, PMLR 161:257–267, "Robust Reinforcement Learning Under Minimax Regret for Green Security" [no DOI; PMLR]: theme 1 — [PMLR](https://proceedings.mlr.press/v161/xu21a.html)
  3. Wu, Weinberger, Wellenius, Dominici & Braun (2024; online 2023), Biostatistics 25(1):57–79, heat-alert stochastic intervention [10.1093/biostatistics/kxad002]: theme 4 (+ heat; also theme 1 because it evaluates an alarm policy) — [OUP](https://academic.oup.com/biostatistics/article/25/1/57/7054586)
  4. Nethery, Katz-Christy, Kioumourtzoglou, Parks, Schumacher & Anderson (2023; online 2021), Biostatistics 24(2):449–464, tropical-cyclone causal-predictive ML [10.1093/biostatistics/kxab047]: themes 2 + 4 — [OUP](https://academic.oup.com/biostatistics/article/24/2/449/6485226)
  5. Aggarwal, Hu, Sullivan, Parks & Nethery (2025), Lancet Planetary Health 9(7), severe flooding, self-matched design [10.1016/S2542-5196(25)00132-9]: themes 2 + 4 — [Lancet](https://www.thelancet.com/journals/lanplh/article/PIIS2542-5196(25)00132-9/fulltext)
  6. Proctor, Rigden, Chan & Huybers (2022), Nature Food 3(9):753–763, water-supply specification [10.1038/s43016-022-00592-x]: theme 3 — [Southampton ePrints record](https://eprints.soton.ac.uk/481977)
  - Reserve R: Rigden, Mueller, Holbrook, Pillai & Huybers (2020), Nature Food 1(2):127–133, soil moisture × evaporative demand [10.1038/s43016-020-0028-7]: theme 3 (compound heat–dry) — [Springer/Nature Food](https://link.springer.com/article/10.1038/s43016-020-0028-7)
- Excluded because they are already covered in earlier reviews:
  - Mate, Killian, Xu, Perrault & Tambe (2020), "Collapsing bandits…" (NeurIPS 2020, arXiv 2007.04432). It is listed in the Robust-Filtering-HMM review (line 2737 of the covered list).
  - Ben-Michael, Imai & Jiang (2024), "Policy learning with asymmetric counterfactual utilities" (JASA). Covered (line 620).
  - Sherman, Huybers & Tziperman (2025), J. Climate (empirically fit EVDs for attribution). Covered (line 619).
  - Rigden, Golden, Chan & Huybers (2024), Madagascar drought. Covered (line 589).
  - Papadogeorgou, Imai, Lyall & Li (2022), JRSS-B (spatio-temporal causal inference). Covered (line 669).
  - Xu et al. (2021), "Dual-mandate patrols" (AAAI). Covered (lines 110, 142).
  - Josey et al. (2023) and Wu et al. (2024, JASA, GPS matching). Covered (lines 68, 102).

### Inferences
- None of the six candidates appears in the three "Decisive_Stakeholder" reviews, and none of their DOIs or arXiv ids appears anywhere in the covered list. My grep for "Considine", "Aggarwal", "kxad002", "kxab047", "s43016", "35009", "S2542-5196", "minimax regret", "Holbrook" and "evaporative demand" returned 0 hits.
- A useful division of labour for the review:
  - Candidates 1 and 2 give the decision rule: a budgeted alarm and a robust placement or pumping rule.
  - Candidates 3, 4 and 5 give causal estimators for what an alarm or an extreme event actually does.
  - Candidate 6 (and R) fixes the climate input: what "drought" should mean as an anchor.

### Gaps
- I found no verifiable Harvard-authored 2020–2026 paper on nonstationary extreme-precipitation statistics or on storm-surge or flood decision optimisation that is not already covered. The closest one, Sherman–Huybers–Tziperman 2025, is already covered. Theme 2 is therefore represented by hurricane and flood papers that are causal-epidemiological, not by EVT papers.
- I found no Harvard-authored paper on groundwater depletion or agricultural water decisions in 2020–2026 that I could verify. Theme 3 is represented by the Huybers-group water-supply papers.

---

## Candidate 1 — Considine et al. (2025): budget-constrained RL for heat-alert issuance (themes 1 + extreme heat)

### Takeaway
This paper is a public RL environment plus a constrained-policy recipe for when to issue an alarm during an extreme. The authors found that off-the-shelf RL performs poorly. RL becomes useful only when it is constrained by an alert budget and by a rule that forbids alerts on not-very-hot days. That maps directly onto a budgeted, certified chloride/curtailment alarm.

### Cited Findings
- **Citation.** Ellen M. Considine, Rachel C. Nethery, Gregory A. Wellenius, Francesca Dominici, Mauricio Tec (2025). "Optimizing Heat Alert Issuance with Reinforcement Learning." Proceedings of the Thirty-Ninth AAAI Conference on Artificial Intelligence (AAAI-25), AI for Social Impact Track, 39(27). DOI 10.1609/aaai.v39i27.35009. arXiv 2312.14196 (v1 Dec 2023; latest Dec 2024) — [AAAI OJS](https://ojs.aaai.org/index.php/AAAI/article/view/35009); [arXiv](https://arxiv.org/abs/2312.14196); [ML Anthology](https://mlanthology.org/aaai/2025/considine2025aaai-optimizing/)
- **Harvard authors** (affiliation line as reproduced in the search-indexed paper header):
  - Considine, Nethery, Dominici and Tec: Harvard T.H. Chan School of Public Health.
  - Tec also: Department of Computer Science, Harvard University.
  - Wellenius: Boston University School of Public Health.
  - Source: [AAAI OJS / arXiv header via search](https://ojs.aaai.org/index.php/AAAI/article/view/35009)
- **Decision tool.**
  - A new, publicly available RL environment for evaluating heat-alert policies against heat-related hospitalisations.
  - The rewards model is trained on historical weather, Medicare records and socioeconomic/geographic features. It uses Bayesian methods suited to weak, spatially varying effects.
  - Policy constraints that are needed are (i) capping the total number of alerts and (ii) preventing alerts on less-hot days. Location-specific policies are also optimised.
  - A post-hoc contrastive analysis against the U.S. National Weather Service (NWS) policy.
  - Sources: [AAAI OJS](https://ojs.aaai.org/index.php/AAAI/article/view/35009); [arXiv](https://arxiv.org/abs/2312.14196)
- **Data and comparison.**
  - Data: NWS alerts 2006–2016, Medicare hospitalisations and ambient heat index.
  - All policies, RL, NWS and baselines, are evaluated under the same alert budget.
  - Source: search summary of the paper — [AAAI OJS](https://ojs.aaai.org/index.php/AAAI/article/view/35009)
- **Main quantitative result** (from search summaries of the paper; exact percentage not retrieved):
  - The best policy, "A2C.QHI" (A2C with a heat-index-quantile restriction), significantly outperformed the NWS policy in the 30 counties studied.
  - Scaled up, it is estimated to avert about 222 non-other-heat-related ("NOHR") hospitalisations per summer across the U.S. Medicare population (2011 basis).
  - The RL gain is larger where the heat–health signal is stronger.
  - The authors caution that the fixed, historically based alert budget may need to become dynamic as climate change intensifies.
  - Sources: [AAAI OJS](https://ojs.aaai.org/index.php/AAAI/article/view/35009); [Lacuna summary](https://lacuna.tiptreesystems.com/work/optimizing-heat-alert-issuance-with-reinforcement-learning/wrk_e6296e5272ae39608c4db9131fdd9665)

### Inferences
- **Core math in our notation** (my restatement of the problem as described):
  - A constrained MDP with state s_t = (heat-index quantile, day of season, alerts used so far, recent alerts), action a_t ∈ {0,1} and reward r_t = −E[hospitalisations | s_t, a_t] from the Bayesian rewards model.
  - Problem: max_π E_π[Σ_t r_t] subject to Σ_t a_t ≤ B (budget) and a_t = 0 whenever QHI_t < q* (restriction).
- **How it changes our model.**
  - (i) The MONTIMI-GO simulator becomes the "rewards model" of an RL environment. The state is (posterior sea fraction at the screen, AR(1) rainfall state with φ = 0.7, private-abstraction proxy, sea-level/surge forecast, curtailments used). The action is {normal pumping, curtail / switch to inland well}. The reward is minus the exceedance-days of 250 mg/L Cl.
  - (ii) The budget B is a stakeholder parameter: the number of curtailment periods per year the utility and users accept.
  - (iii) The QHI-type restriction becomes "curtailment allowed only when SPIRANCA-GO's certified margin m(b) is not satisfied". The physics certificate plays the role that the heat-index restriction plays in the paper.
  - Direction: curtailments are concentrated in the second and later years of a persistent drought, where the AR(1) state is informative, rather than spread uniformly. That makes pumping more conservative late in droughts and less conservative in wet years.
  - The paper's warning that budgets should become dynamic under climate change argues for B(t) indexed to the drought state.
- **Innovation idea: "budgeted certified curtailment" (BCC).**
  - Conjecture to prove or test: under AR(1) drought persistence and a monotone sea-fraction response, the optimal budgeted policy is a threshold rule on the certified margin gap g_t = q̂_t + m(b) − 250 mg/L. The threshold falls as the remaining budget rises (an index policy).
  - Test: run MONTIMI-GO on ≥1,000 synthetic AR(1) rainfall sequences and compare exceedance-days per curtailment-day for (a) a fixed 250 mg/L trigger, (b) unconstrained RL and (c) RL constrained by the SPIRANCA margin.
  - Prediction from the paper: (b) under-performs (c).

### Gaps
- I could not open the PDF, so the exact percentage improvement, the per-county results and the precise specification of the rewards model (likelihood, priors, alert-fatigue terms) are unverified. Page numbers in AAAI 39(27) are also unverified.

---

## Candidate 2 — Xu, Perrault, Fang, Chen & Tambe (2021): minimax-regret robust RL via double oracle (theme 1)

### Takeaway
This is a general, computable minimax-regret criterion for sequential decisions when environment parameters lie in a compact uncertainty set. It is solved as a zero-sum game between the decision maker and "nature" using two RL oracles. It suits pumping and well-placement decisions where recharge, private abstraction and sea level are deeply uncertain, and it is less conservative than worst-case (maximin) design.

### Cited Findings
- **Citation.** Lily Xu, Andrew Perrault, Fei Fang, Haipeng Chen, Milind Tambe (2021). "Robust Reinforcement Learning Under Minimax Regret for Green Security." Proceedings of the Thirty-Seventh Conference on Uncertainty in Artificial Intelligence (UAI 2021), PMLR 161:257–267. arXiv 2106.08413. There is no DOI (PMLR proceedings) — [PMLR](https://proceedings.mlr.press/v161/xu21a.html); [arXiv](https://arxiv.org/abs/2106.08413)
- **Harvard authors** (as printed in the PMLR PDF header via search): Lily Xu, Andrew Perrault, Haipeng Chen and Milind Tambe, Center for Research on Computation and Society, Harvard University. Fei Fang, Carnegie Mellon University — [PMLR PDF](https://proceedings.mlr.press/v161/xu21a/xu21a.pdf); [author copy](https://haipeng-chen.github.io/files/21uai_robust_RL_deterrence.pdf)
- **Decision tool.**
  - Patrol planning is posed as a game between the defender and nature, where nature controls the adversary's behaviour parameters.
  - The criterion is minimax regret. The agent seeks minimax-regret-optimal policies; nature seeks regret-maximising parameter instantiations.
  - The algorithm, MIRROR, is double-oracle / policy-space-response-oracle based. It has two RL oracles and solves a restricted game over limited sets of strategies and parameter values.
  - It converges to an ε-max-regret-optimal strategy in finitely many iterations.
  - It applies to generic RL with a compact uncertainty set over transitions and rewards.
  - Sources: [PMLR](https://proceedings.mlr.press/v161/xu21a.html); [arXiv](https://arxiv.org/abs/2106.08413)
- **Main result.**
  - The adversary model was learned from real poaching data from Queen Elizabeth National Park, Uganda.
  - MIRROR yields low max-regret policies across horizon, park size, deterrence strength and budget.
  - The authors report evidence that patrols deter poachers in real data.
  - No numerical regret reductions were retrieved.
  - Sources: [PMLR PDF](https://proceedings.mlr.press/v161/xu21a/xu21a.pdf); [arXiv html](https://arxiv.org/html/2106.08413)

### Inferences
- **Core math in our notation.** For policy π and uncertain parameter θ ∈ Θ (compact):
  - Regret(π, θ) = V_θ(π*_θ) − V_θ(π).
  - Decision: π_MMR = argmin_{π (mixed)} max_{θ ∈ Θ} Regret(π, θ).
  - Double oracle: alternate between (i) a best-response policy to nature's current mixture and (ii) nature's regret-maximising θ against the agent's mixture, until the restricted game value converges within ε.
- **How it changes our model.**
  - Today MONTIMI-GO places the well so that the goal stays safe, which is in effect a maximin or chance-constraint design.
  - Under MIRROR, Θ = {inland inflow factor (recharge), drought private-abstraction rate, sea level + surge at the sea boundary, immobile-zone exchange rates}, and the policy = (well x-position and screen depth, seasonal pumping schedule).
  - Minimax regret penalises the opportunity cost of overly conservative inland placement in benign worlds. So it should move the recommended well seaward of the worst-case design while keeping the regret of salinisation bounded.
  - The mixed-strategy output (randomising pumping between two wells or schedules) also creates exogenous pumping variation. This strengthens the "pumping anomaly" anchor in SPIRANCA-GO, an identifiability bonus.
- **Innovation idea: "regret-certified well placement".**
  - Use the MONTIMI-GO discrete adjoint as nature's oracle (gradient ascent on regret over Θ) and the placement optimiser as the agent's oracle.
  - Candidate theorem: if the screen sea fraction is monotone in recharge (decreasing) and in sea level and abstraction (increasing), nature's best responses lie at vertices of a box Θ. The double oracle then terminates within 2^d nature strategies (d = number of uncertain drivers).
  - Test: compare placement and pumping under maximin vs. minimax regret for d = 4, and report the regret, the 250 mg/L exceedance probability and the water yield foregone.

### Gaps
- I could not retrieve numerical regret values or the exact form of the uncertainty set from the full text.
- The green-security application is not climate-related. Its relevance to our model is methodological, through the decision criterion.

---

## Candidate 3 — Wu, Weinberger, Wellenius, Dominici & Braun (2024): causal effect of shifting an alert policy, via incremental stochastic interventions in time series (theme 4, also theme 1)

### Takeaway
This paper gives a way to estimate what would happen if the authority were δ times more likely (in odds) to issue an alarm, from observational time series in which alarms are almost always issued on extreme days. Ordinary positivity/overlap fails in that setting. The authors show identification under a weaker overlap condition. This is exactly the structure of utility pumping and curtailment decisions, which depend on drought state.

### Cited Findings
- **Citation.** Xiao Wu, Kate R. Weinberger, Gregory A. Wellenius, Francesca Dominici, Danielle Braun (2024; online 2023). "Assessing the causal effects of a stochastic intervention in time series data: are heat alerts effective in preventing deaths and hospitalizations?" Biostatistics 25(1):57–79. DOI 10.1093/biostatistics/kxad002. PMID 36815555. arXiv 2102.10478 — [OUP](https://academic.oup.com/biostatistics/article/25/1/57/7054586); [doi.org link as indexed](https://doi.org/10.1093/biostatistics/kxad002); [Harvard Chan profile of D. Braun listing the paper](https://www.hsph.harvard.edu/profile/danielle-braun/)
- **Harvard authors.** Dominici and Braun are Harvard T.H. Chan School of Public Health (Biostatistics) faculty, and the paper is listed on Braun's Harvard Chan profile — [Harvard Chan profile](https://www.hsph.harvard.edu/profile/danielle-braun/). Xiao Wu later moved to Columbia — [Columbia profile](https://www.publichealth.columbia.edu/profile/xiao-wu-phd). The printed affiliation line was not read directly (see Gaps).
- **Decision tool / estimand.**
  - Overlap is violated in time-series data because alerts are rare on average days and almost always issued on extremely hot days.
  - The authors propose a stochastic intervention implemented through an incremental time-varying propensity score (ItvPS). It multiplies the odds of issuing an alert on a given day, conditional on past information, by an odds ratio.
  - The causal estimands are identified and estimable under a weaker overlap assumption.
  - The framework is extended to multiple time series (locations).
  - Source: [search summary of arXiv/OUP](https://arxiv.org/abs/2102.10478v2)
- **Main quantitative result** (search summary; the versions disagree):
  - In one version, raising the odds of alert issuance 10-fold is estimated to avert about 0.15 deaths per day per county (95% CI −0.01 to 0.32), 42 heat-stroke hospitalisations (CI −7 to 91) and 634 urinary-tract-infection hospitalisations (CI −81 to 1,327).
  - A PMC version reports a CI of 0.06–0.24 for a cumulative effect.
  - The authors characterise the evidence as weak.
  - Sources: [OUP](https://academic.oup.com/biostatistics/article/25/1/57/7054586); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11032723/); [arXiv html](https://arxiv.org/html/2102.10478)
- **Context.** A companion Harvard/BU study (Weinberger et al. 2021, Environment International 157:106834) of Medicare enrollees in 2,817 counties found heat alerts were not associated with lower all-cause mortality — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0160412021004591)

### Inferences
- **Core math in our notation.** This is the standard incremental-intervention form implied by "multiply the odds by δ".
  - With π_t(H_t) = P(A_t = 1 | H_t), the shifted policy assigns q_t^δ(H_t) = δ π_t / (δ π_t + 1 − π_t).
  - Estimand: ψ(δ) = E[Y_t^{Q^δ}].
  - Identification: sequential ignorability given the history H_t, plus consistency. Positivity is needed only where π_t > 0, not π_t ∈ (ε, 1 − ε) everywhere.
  - IPW estimator: weights Π_s [A_s q_s^δ + (1 − A_s)(1 − q_s^δ)] / [A_s π_s + (1 − A_s)(1 − π_s)].
- **How it changes our model.**
  - The utility's pumping and curtailment anomaly is not exogenous: the utility pumps more in hot, dry summers. Strong overlap therefore fails exactly where seawater-intrusion risk is highest.
  - SPIRANCA-GO treats pumping as an anchor (exogenous). Wu et al. give a complementary, history-adjusted estimator of the effect of changing the curtailment policy, δ-fold, which is valid inside the support of the record.
  - The positivity frontier {H_t : π_t(H_t) ≈ 0} is precisely where SPIRANCA-GO's alarm fails after a known pumping decision moves the screen into an unseen regime. That makes the failure diagnosable before it happens.
  - Direction: decisions that imply δ outside the record's support should trigger extra sampling (re-anchoring) before they are implemented, not after.
- **Innovation idea: "incremental-shift certificate".**
  - Define the maximal certifiable odds shift δ_max(b) as the largest δ for which the weighted effective sample size at the screen stays ≥ n_min.
  - Certify m_δ(b) = q_{1−α}(b; δ) + δ̄·max(0, ℓ(b)) only for δ ≤ δ_max.
  - Rule: if a planned pumping decision implies δ > δ_max, schedule a chloride sample within the first season (a targeted re-anchor) rather than waiting for the annual sample.
  - Test numerically in MONTIMI-GO by simulating a utility whose pumping depends on the drought state, and compare alarm coverage with and without the δ_max rule.

### Gaps
- The printed affiliations, the number of counties and years, and which CI belongs to which version could not be confirmed from the full text. The search summaries conflict on the CI.

---

## Candidate 4 — Nethery et al. (2023): integrated causal–predictive ML for tropical-cyclone impacts (themes 2 + 4)

### Takeaway
This is a two-stage tool. Stage 1 estimates storm-by-location causal effects of past tropical cyclones at fine spatial resolution. Stage 2 learns a predictive map from storm meteorology and community characteristics to those effects, so the communities most at risk from future storms can be flagged. It carries over directly to per-well event-effect estimation and prediction for storm-surge and heavy-rain salinisation events.

### Cited Findings
- **Citation.** Rachel C. Nethery, Nina Katz-Christy, Marianthi-Anna Kioumourtzoglou, Robbie M. Parks, Andrea Schumacher, G. Brooke Anderson (2023; online 28 Dec 2021). "Integrated causal-predictive machine learning models for tropical cyclone epidemiology." Biostatistics 24(2):449–464. DOI 10.1093/biostatistics/kxab047. arXiv 2010.11330 — [OUP](https://academic.oup.com/biostatistics/article/24/2/449/6485226); [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10102905/); [arXiv](https://arxiv.org/abs/2010.11330v1); [UCAR listing](https://impacts.ucar.edu/en/publications/integrated-causal-predictive-machine-learning-models-for-tropical/)
- **Harvard authors.** Nethery (Department of Biostatistics, Harvard T.H. Chan School of Public Health), per the search summary of the OUP/PMC records. Katz-Christy is also listed in the summary with Harvard Chan Biostatistics. The per-author lines were not read directly — [OUP](https://academic.oup.com/biostatistics/article/24/2/449/6485226)
- **Decision tool.**
  - A causal-inference component estimates the short-term health effects of past tropical cyclones at fine spatial resolution.
  - A predictive component relates storm meteorology and community socioeconomic and demographic traits to those effects, to identify the communities at highest risk from future storms.
  - Applied to Medicare all-cause mortality and cardiovascular and respiratory hospitalisations.
  - Source: [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10102905/)
- **Main result.**
  - Large heterogeneity of effects within and across storms.
  - Substantial TC-attributable increases in respiratory hospitalisations on average.
  - TC sustained wind speed is the primary driver of mortality and respiratory risks.
  - A search snippet reports an average excess event ratio of 8.58 (95% interval 4.34–11.86) for respiratory hospitalisations, and that storms impacting more than 25 counties were analysed. I could not verify these two numbers against the text, so treat them as unverified.
  - Sources: [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10102905/); [OUP](https://academic.oup.com/biostatistics/article/24/2/449/6485226)

### Inferences
- **Core math in our notation.**
  - Stage 1: for unit c and event s, τ_cs = Y_cs − Ŷ_cs(0), where Ŷ_cs(0) is an ML counterfactual for the no-storm outcome (or a ratio Y/Ŷ(0), an "excess event ratio").
  - Stage 2: τ̂_cs ≈ g(W_s, Z_c), where W_s is storm meteorology (wind, rain, duration) and Z_c is unit characteristics. The fitted g ranks units by predicted vulnerability for a forecasted storm W_new.
  - The underlying identification assumption is that Ŷ(0) correctly predicts the no-storm outcome from non-storm periods (no concurrent confounding shock).
- **How it changes our model.**
  - (i) Stage 1 at Fushë-Kuqe: for each past surge or heavy-rain event e and monitoring well w, estimate τ_we as the observed chloride minus the SPIRANCA-GO (anchor-regression) counterfactual chloride without the event.
  - (ii) Stage 2: regress τ̂_we on event descriptors (peak surge height, duration, rainfall total, antecedent AR(1) drought state) and well descriptors (distance to the shoreline, screen depth, clay/immobile fraction).
  - (iii) The sea boundary of MONTIMI-GO gets an event-specific surge hydrograph rather than a mean sea level. The alarm margin becomes event-specific: m_e(b) = m(b) + ĝ(W_e, Z_w)⁺.
  - (iv) Well placement avoids locations with high predicted event sensitivity.
  - The paper's finding that wind (not rainfall) drives risk suggests testing whether surge or wind set-up, rather than storm rainfall, dominates event salinisation at the screen. That would shift monitoring effort to surge-season sampling.
- **Innovation idea: "two-stage event-sensitivity emulator with a simulator check".**
  - Use MONTIMI-GO to generate τ_we for many synthetic storms (true effects known).
  - Fit Stage 2 using only the small number of field-like events available, and test (a) the rank correlation between predicted and true well vulnerabilities and (b) the coverage of an event-specific margin.
  - Theorem target: a bound on ranking error as a function of the number of observed events and the heterogeneity of g.

### Gaps
- The exact Stage 1 counterfactual model (the ML learner and the choice of control periods), the Stage 2 learner and the verified numerical effect sizes were not retrievable without full-text access.

---

## Candidate 5 — Aggarwal, Hu, Sullivan, Parks & Nethery (2025): severe floods, a self-matched design and distributed lags (themes 2 + 4)

### Takeaway
This paper is a causal design for the lagged effects of severe flood events. Each place is compared with itself in matched non-flood periods, and a distributed-lag model tracks effects during and up to four weeks after exposure. It supplies an estimator and a lag structure for what an extreme-rainfall or flood event does to chloride at a well, and it highlights that effects persist after the event.

### Cited Findings
- **Citation.** Sarika Aggarwal, Jie K. Hu, Jonathan A. Sullivan, Robbie M. Parks, Rachel C. Nethery (2025). "Severe flooding and cause-specific hospitalisation among older adults in the USA: a retrospective matched cohort analysis." The Lancet Planetary Health 9(7) (published 30 July 2025; the article number 101268 comes from a search summary and is unverified). DOI 10.1016/S2542-5196(25)00132-9. Open access, CC BY 4.0 — [Lancet Planetary Health](https://www.thelancet.com/journals/lanplh/article/PIIS2542-5196(25)00132-9/fulltext); [PMC author manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC12360453/); preprint [arXiv 2309.13142](https://arxiv.org/abs/2309.13142); code [NSAPH GitHub](https://github.com/NSAPH-Projects/floods-hospitalizations-glm)
- **Harvard authors.** Nethery is senior author (Harvard T.H. Chan School of Public Health). The listed institutions are Harvard T.H. Chan, Ohio State, UW–Madison and Columbia — [Harvard Chan news](https://hsph.harvard.edu/news/flooding-increases-hospitalization-risks-in-older-adults/); [News-Medical](https://www.news-medical.net/news/20250731/Flooding-linked-to-increased-hospitalizations-among-older-adults.aspx)
- **Decision tool.**
  - A self-matched design with a distributed-lag model tracks hospitalisation rates during and up to four weeks after severe flood exposure.
  - Flood exposure (Global Flood Database) is linked to Medicare claims by ZIP code, 2000–2016.
  - Source: [arXiv 2309.13142](https://arxiv.org/abs/2309.13142)
- **Main quantitative result.**
  - Published version, per the news summary: average increases during and after floods were 3.1% for skin diseases, 2.5% for nervous-system diseases, 1.3% for musculoskeletal diseases and 1.1% for injury/poisoning. Over 4.5 million hospitalisations and 72 major flood events were analysed — [News-Medical](https://www.news-medical.net/news/20250731/Flooding-linked-to-increased-hospitalizations-among-older-adults.aspx)
  - The preprint version differs: nervous system 3.5% (95% CI 0.6–6.4%), skin 3.4% (0.3–6.7%), injury/poisoning 1.5% (−0.07–3.2%), with 4,879,643 hospitalisations. Some effects varied with the proportion of Black residents — [arXiv 2309.13142](https://arxiv.org/abs/2309.13142)
  - Cite the Lancet version's numbers only after checking the full text.

### Inferences
- **Core math in our notation.**
  - log E[Y_{z,t}] = α_{z,m(t)} + Σ_{ℓ=0}^{L} β_ℓ X_{z,t−ℓ}, with L = 4 weeks. α_{z,m} is a fixed effect for each self-matched set (the same unit in comparable non-flood periods). The cumulative effect is exp(Σ_ℓ β_ℓ) − 1.
  - Identification: self-matching removes time-invariant unit confounders. It requires no time-varying confounding inside matched sets and no anticipation.
- **How it changes our model.**
  - (i) The recharge response in MONTIMI-GO (inland inflow factor) is currently instantaneous. The paper argues for a lagged event-response kernel β_ℓ. In our aquifer the kernel should be much longer than 4 weeks because of the two immobile zones (silt/clay memory).
  - (ii) For field data, a self-matched estimator gives the event effect on chloride at a well as post-event weeks vs. the same weeks in other years at the same well. This complements SPIRANCA-GO's anchor-regression counterfactual.
  - (iii) Monitoring: one chloride sample per year cannot identify β_ℓ. The paper's lag window implies post-event sampling bursts.
  - Direction: more post-event sampling, and alarm margins that stay elevated for a lag window after floods or surges instead of resetting immediately.
- **Innovation idea: "physics-constrained distributed lag + minimal post-event sampling".**
  - Constrain β_ℓ = Σ_{k=1}^{2} c_k e^{−λ_k ℓ}, where λ_1 and λ_2 are the MONTIMI-GO immobile-zone exchange rates.
  - Derive the minimal set of post-event sampling times (for example three samples) that identifies (c_1, c_2) and the cumulative effect.
  - Test in MONTIMI-GO whether this design recovers the simulated cumulative event effect better than one annual sample.

### Gaps
- The published version's model details (matching ratio, lag basis, overdispersion handling) and its exact estimates and article number were not confirmed from the full text.

---

## Candidate 6 — Proctor, Rigden, Chan & Huybers (2022): specifying water supply correctly (soil moisture vs. precipitation) changes drought-damage projections (theme 3)

### Takeaway
Precipitation is a poor proxy for water supply. Models that use temperature and precipitation conflate dryness with heat stress and overestimate projected damages by 28–320%. Using root-zone soil moisture together with temperature separates the two stresses. For us this means the "rainfall anomaly" anchor is probably the wrong drought variable, and a warming shift may lie outside the span of our anchors.

### Cited Findings
- **Citation.** Jonathan Proctor, Angela Rigden, Duo Chan, Peter Huybers (2022). "More accurate specification of water supply shows its importance for global crop production." Nature Food 3(9):753–763. DOI 10.1038/s43016-022-00592-x — [Southampton ePrints](https://eprints.soton.ac.uk/481977); [Harvard DASH](https://dash.harvard.edu/entities/publication/b13679b5-b0e7-4285-9397-5e50c6b9448b); [Zenodo data](https://zenodo.org/record/7041432)
- **Harvard authors.**
  - Huybers: Harvard Earth and Planetary Sciences / SEAS.
  - Proctor: Harvard Center for the Environment postdoctoral fellow in Huybers' group.
  - The paper is deposited in Harvard DASH.
  - The Zenodo record lists the coauthors' affiliations as Harvard University, UC Irvine and Woods Hole Oceanographic Institution. I did not read the printed affiliation line directly.
  - Sources: [Harvard SEAS news](https://seas.harvard.edu/news/better-understanding-crop-yields-under-climate-change); [Harvard DASH](https://dash.harvard.edu/entities/publication/b13679b5-b0e7-4285-9397-5e50c6b9448b); [Zenodo](https://zenodo.org/record/7041432)
- **Decision tool / model.** Empirical (panel) yield-response models built on satellite root-zone soil moisture and surface air temperature. They estimate the joint influence of soil moisture and temperature on maize, soybean, millet and sorghum productivity — [Southampton ePrints](https://eprints.soton.ac.uk/481977)
- **Main quantitative result.**
  - Soil-moisture models explain 30–120% more of the interannual yield variation than precipitation-based models.
  - Soil moisture and temperature contribute roughly equally to historical yield variation.
  - Under SSP5-8.5, projected end-of-century yield damages are −9% to −32% across crops.
  - Temperature-and-precipitation models overestimate damages by 28% to 320%.
  - Sources: [Southampton ePrints](https://eprints.soton.ac.uk/481977); [Harvard DASH via search](https://dash.harvard.edu/entities/publication/b13679b5-b0e7-4285-9397-5e50c6b9448b); [Harvard Crimson](https://www.thecrimson.com/article/2022/9/29/crop-yield-soil-moisture)

### Inferences
- **Core math in our notation.**
  - y_it = μ_i + h_i(t) + f(T_it) + g(SM_it) [+ interaction] + ε_it, with location fixed effects μ_i and trends h_i.
  - The decision-relevant point is a specification test: replacing P by SM changes the explained variance and the projected damages by large factors. The cause is omitted-variable / proxy bias, because P is correlated with T.
- **How it changes our model.**
  - (i) The SPIRANCA-GO anchors are (rainfall anomaly r, pumping anomaly). Anchor regression certifies only against shifts in the span of the anchors.
  - If warming acts on recharge through evapotranspiration and soil moisture, and not through rainfall, the warming shift is partly outside span{r, p}. The δ̄·max(0, ℓ(b)) term then under-certifies in hot droughts.
  - Replace or augment r with a soil-moisture or recharge anomaly (SMAP root-zone, or a soil-water-balance recharge estimate) plus a temperature / evaporative-demand anchor.
  - (ii) In MONTIMI-GO, the inland inflow factor should be driven by soil-moisture-based recharge, not scaled rainfall.
  - (iii) For private abstraction during drought, the trigger for farmer pumping is plausibly soil moisture and heat, not rainfall. Model abstraction as a function of (SM, T).
  - Direction: in compound heat–drought years, expect lower recharge and higher private abstraction than a rainfall-only model implies. That calls for more conservative pumping and wider margins. In wet-hot years the rainfall-only model may be overly pessimistic.
- **Innovation idea: "anchor-span adequacy test".**
  - Using MONTIMI-GO with an ET-driven warming scenario, compute the share of the warming-induced chloride shift explained by projection onto span{r, p} versus span{SM, T, p}.
  - Prove and test that the SPIRANCA-GO coverage loss is bounded by the norm of the orthogonal residual of the shift. This turns "is our drought variable right?" into a computable certificate.

### Gaps
- Model details such as functional forms (bins or splines), interaction terms and standard errors were not read from the full text.
- The crop-yield setting is an analogue for recharge, not a direct groundwater study. No Harvard groundwater-decision paper could be verified (see overview).

---

## Reserve R — Rigden, Mueller, Holbrook, Pillai & Huybers (2020): the soil moisture × evaporative-demand interaction (theme 3, compound heat–drought)

### Takeaway
Use this as the drought alternate if one of the six is dropped. It shows that the imbalance between atmospheric evaporative demand and soil moisture predicts damages better than temperature and precipitation. Ignoring soil moisture would roughly double the projected damage. This is a compound-event model that maps onto recharge under heat–drought.

### Cited Findings
- **Citation.** Angela J. Rigden, Nathaniel D. Mueller, N. Michele Holbrook, Natesh Pillai, Peter Huybers (2020). "Combined influence of soil moisture and atmospheric evaporative demand is important for accurately predicting US maize yields." Nature Food 1(2):127–133. DOI 10.1038/s43016-020-0028-7 — [Springer/Nature Food](https://link.springer.com/article/10.1038/s43016-020-0028-7); [Harvard DASH](https://dash.harvard.edu/entities/publication/51cde446-7e1e-4d90-8eac-e32820fe3e46); [Holbrook group (Harvard OEB) PDF](https://holbrookgroup.oeb.harvard.edu/resource/s43016-020-0028-7pdf)
- **Harvard authors.** Huybers (Harvard EPS/SEAS), Holbrook (Harvard OEB) and Pillai (Harvard Statistics). The paper is deposited in Harvard DASH. The printed affiliation line was not read directly — [Harvard DASH](https://dash.harvard.edu/entities/publication/51cde446-7e1e-4d90-8eac-e32820fe3e46)
- **Result.**
  - Using SMAP soil moisture, retrospective yield predictions based on the interaction of evaporative demand and soil moisture significantly outperform temperature and/or precipitation models.
  - Climate models agree that evaporative demand rises but disagree on root-zone soil moisture.
  - Damages conditioned only on changes in demand would be roughly twice those that also account for soil moisture.
  - Heat can sometimes help by drying excessively wet soils.
  - Source: [Springer/Nature Food via search](https://link.springer.com/article/10.1038/s43016-020-0028-7)

### Inferences
- For MONTIMI-GO, recharge R = R(SM, VPD) with an interaction term. Compound heat–drought scenarios should be specified jointly on (SM, VPD), not as independent rainfall and temperature perturbations.
- Innovation: a two-anchor (SM, VPD) version of SPIRANCA-GO, tested with AR(1)-persistent SM anomalies.

### Gaps
- Coefficients and regional breakdowns were not retrieved.
- Its 2020 date is within the window but at its edge.
