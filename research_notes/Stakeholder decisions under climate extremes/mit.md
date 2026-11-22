# MIT papers (2020–2026): mathematical stakeholder decisions under uncertainty and climate extremes, for coastal-aquifer management

Six candidates (the coordinator picks 5). Each has at least one MIT author, is from 2020–2026, is peer-reviewed, and is not in `_already_covered_references.txt`. I grepped that file for each first author's surname and a title keyword: Bertsimas+"prescriptive", Barthel/Sorensen, Rudy, Schlosser, Abadie, Wüthrich. None matched. "Kallus" and "Chernozhukov" match only other papers.

Spread across themes:
- **P1 Bertsimas & Kallus (2020):** theme 1, with a drought use.
- **P2 Barthel Sorensen et al. (2024):** theme 2, rare extremes.
- **P3 Rudy & Sapsis (2023):** theme 2, extreme-event precursors and alarms.
- **P4 Schlosser et al. (2021):** theme 3, drought and water-supply risk.
- **P5 Abadie (2021):** theme 4, synthetic control.
- **P6 Chernozhukov, Wüthrich & Zhu (2021):** theme 4 with a link to theme 1, certified counterfactual inference.

Suggested pick of 5: keep P1, P2, P4 and P6, and add P3 if the link to the SPIRANCA-GO alarm matters most, or P5 if broader causal coverage matters most.

**How verification was done (please read).** In this session Crossref (api.crossref.org), doi.org, arXiv, MIT DSpace, OSTI and the publisher sites could not be fetched; the host did not resolve. Every bibliographic field below therefore comes from web-search results that index publisher, RePEc/IDEAS, ScienceDirect, ACM DL, OSTI or MIT DSpace records. The URLs are given inline.
- Where two independent index records agree on a DOI, I mark it **DOI confirmed (index)**.
- I could not open a printed byline directly. MIT affiliation therefore rests on the search-result records named inline: MIT DSpace open-access deposits, MIT News, MIT lab and award pages, and the index affiliation fields.
- Formulas marked **[formula from the paper as known; not re-read this session]** come from my prior reading of the paper. Re-check them against the PDF before you quote them as equations.

---

## P1 — Bertsimas, D. & Kallus, N. (2020). From predictive to prescriptive analytics. *Management Science*, 66(3), 1025–1044. https://doi.org/10.1287/mnsc.2018.3253

### Takeaway
This is the basic MIT "predict-then-prescribe" tool. It turns auxiliary covariates x (for us: last year's rainfall anomaly, sentinel heads, signs of private abstraction) into a conditional decision ẑ(x), using machine-learning weights over past scenarios. It also gives a "coefficient of prescriptiveness" that measures how much an auxiliary is worth for the decision. That gives a direct value-of-monitoring metric for Fushë-Kuqe.

### Cited Findings
- **Citation:** Management Science, volume 66, issue 3 (March 2020), pages 1025–1044, DOI 10.1287/mnsc.2018.3253. Published 1 March 2020. — [ACM DL record](https://dl.acm.org/doi/10.1287/mnsc.2018.3253); [SUFE academic index](https://academicnewsletter.sufe.edu.cn/info/391317); [INFORMS page](https://pubsonline.informs.org/doi/fpi/10.1287/mnsc.2018.3253). **DOI confirmed (index).**
- **MIT author:** Dimitris Bertsimas, Sloan School of Management, MIT. Nathan Kallus was at the School of ORIE, Cornell Tech. — [SUFE index affiliation fields](https://academicnewsletter.sufe.edu.cn/info/391317); MIT open-access deposit at [DSpace@MIT 1721.1/133675](https://dspace.mit.edu/handle/1721.1/133675). The preprint is [arXiv:1402.5481](https://arxiv.org/abs/1402.5481), last revised July 2018.
- **Core idea:** the paper combines ML and OR/MS into "a framework, along with specific methods, for using data to prescribe optimal decisions". The data are mainly auxiliary quantities, not only the uncertain quantities that enter the cost directly. — [arXiv abstract via search](https://arxiv.org/abs/1402.5481)
- **Weights:** kNN and kernel-regression weights are among the methods used to compute the weights. A later paper describes the work as establishing asymptotic optimality relative to an oracle that knows the full conditional distribution. — [Robust Data-driven Prescriptiveness Optimization, arXiv 2306.05937](https://arxiv.org/pdf/2306.05937)
- **Coefficient of prescriptiveness:** the paper defines it as "the analogue of R² for prescription problems". — [arXiv 1402.5481](https://arxiv.org/pdf/1402.5481)
- **Main quantitative result:** the method was applied to inventory at the distribution arm of a media company that ships about 1 billion units a year. It used internal data plus public data from IMDb, Rotten Tomatoes and Google. The data and methods gave an **88% improvement as measured by the coefficient of prescriptiveness**. — [arXiv 1402.5481](https://arxiv.org/pdf/1402.5481); [SUFE index](https://academicnewsletter.sufe.edu.cn/info/391317)
- **Critique:** a 2026 paper argues that the coefficient has no universal scale, because its upper bound varies across problems and depends on the train/test split. It proposes adjusted and expected variants. — [Electronic Research Archive 2026](https://www.aimspress.com/article/doi/10.3934/era.2026266)
- **Math [formula from the paper as known; not re-read this session]:**
  - Predictive prescription: ẑ_N(x) ∈ argmin_{z∈Z} Σ_{i=1}^{N} w_{N,i}(x) · c(z; y_i).
  - Weights for kNN: w_i = 1/k on the k nearest x_i.
  - Weights for CART: w_i = 1{x_i in the same leaf as x} divided by the leaf size. Random forests average the tree weights; kernel and LOESS weights are also used.
  - Coefficient: P = 1 − [R̂(ẑ_N) − R̂*] / [R̂(ẑ_SAA) − R̂*]. Here SAA ignores x and R̂* is the full-information (oracle) cost.
- **Theme and situation:** theme 1, normal operation. It becomes a drought tool when x carries information on drought persistence.

### Inferences
**How it changes our model:**
- **Today:** MONTIMI-GO picks a pumping rate Q and a well position against the whole recharge/surge/private-abstraction scenario set, which is effectively an SAA.
- **Proposed rule:** replace it with the conditional rule Q̂(x) = argmin_Q Σ_i w_i(x)·[unmet-demand cost(Q) + λ·max(0, C_screen(Q, ξ_i) − 250 mg/L)].
  - ξ_i = (inland-inflow factor, sea level/surge, private abstraction) is the i-th historical or simulated scenario.
  - C_screen is computed by MONTIMI-GO or its surrogate.
  - x = (r_{t−1}, h_sentinel, private-abstraction proxy).
- **Why it helps:** our rainfall is AR(1) with lag-one correlation 0.7, so r_{t−1} is genuinely predictive.
  - After a dry year the weights concentrate on scenarios where the drought continues. This pushes pumping down and/or favours the inland well, which is more conservative exactly in multi-year droughts.
  - After a wet year the rule allows more pumping. The expected unmet demand falls at the same chloride risk.
- **Extrapolation limit:** the weights only re-weight scenarios already seen. A pumping regime outside the record, which is the same failure mode as SPIRANCA-GO after a known pumping decision, cannot be prescribed from the weights alone. The anchor-shift diagnostic ℓ(b) can flag when x leaves the support.

**Innovation (PRESKRIPT-GO):** use the coefficient of prescriptiveness as a value-of-monitoring criterion.
- Compute P for each candidate auxiliary on the variable-density model: r_{t−1} alone, a sentinel-piezometer head, an electricity-use proxy for private abstraction, and combinations.
- Fund the monitoring with the largest gain in P per euro.
- Test numerically: for a newsvendor-type pumping cost under AR(1) recharge, check whether P for r_{t−1} scales roughly like φ² (≈0.49 at φ=0.7). This is a conjecture to test, not a known result.
- Add the SPIRANCA-GO certified margin as a hard constraint inside the prescription: C_screen + m(b) ≤ 250 mg/L.

### Gaps
- I did not see the printed first-page byline. The MIT affiliation comes from index affiliation fields and the DSpace@MIT deposit.
- The exact theorem conditions for asymptotic optimality were not re-read.

---

## P2 — Barthel Sorensen, B., Charalampopoulos, A., Zhang, S., Harrop, B. E., Leung, L. R. & Sapsis, T. P. (2024). A non-intrusive machine learning framework for debiasing long-time coarse resolution climate simulations and quantifying rare events statistics. *Journal of Advances in Modeling Earth Systems*, 16(3), e2023MS004122. https://doi.org/10.1029/2023MS004122

### Takeaway
An MIT (Sapsis group) tool that estimates the tails of climate variables from a cheap, biased coarse model. A neural correction operator is trained on a short period in which the coarse model is nudged toward reference data, then applied to long free runs. In the test model it recovers events with return periods about two orders of magnitude longer than the training data. This is exactly the problem of estimating 1-in-100-year recharge or chloride extremes from a few years of good data.

### Cited Findings
- **Citation:** JAMES 16, e2023MS004122 (2024); preprint arXiv 2402.18484. — [OSTI record 2328637](https://www.osti.gov/biblio/2328637); [arXiv 2402.18484](https://arxiv.org/abs/2402.18484). Volume/issue 16(3) and the DOI are as listed in an [APS DFD 2024 abstract](https://archive.aps.org/dfd/2024/r26/7). **DOI confirmed (index).** Issue 3 rests on one listing.
- **MIT authors:** the article is deposited as an "MIT Open Access Article" on [DSpace@MIT (1721.1/154212)](http://dspace.mit.edu/bitstream/handle/1721.1/154212/J%20Adv%20Model%20Earth%20Syst%20-%202024%20-%20Barthel%20Sorensen%20-%20A%20Non%E2%80%90Intrusive%20Machine%20Learning%20Framework%20for%20Debiasing%20Long%E2%80%90Time.pdf?sequence=2&isAllowed=y). The preprint is hosted at the MIT Sapsis lab. Zhang, Harrop and Leung are at Pacific Northwest National Laboratory. — [search summary of the paper and lab PDF](https://arxiv.org/abs/2402.18484)
  - Inference from the group membership, byline not seen: Barthel Sorensen, Charalampopoulos and Sapsis are in MIT Mechanical Engineering.
- **Problem:** fully resolved climate simulations are intractable, so "policy makers must rely on coarse models" that carry sub-grid bias. Earlier correction operators trained to match statistics fail for events with return periods longer than the training data, because the reference statistics have not converged. — [OSTI/ResearchGate abstract via search](https://www.osti.gov/biblio/2328637)
- **Method:** a neural-network correction operator is trained on reference data and on a coarse simulation nudged toward that reference. It is applied non-intrusively, without changing the model's equations. — [arXiv 2402.18484](https://arxiv.org/html/2402.18484)
- **Main quantitative results:**
  - On an under-resolved two-layer quasi-geostrophic model, the method quantifies events with **return periods two orders of magnitude longer than the training data**.
  - On E3SM (about 110 km), training on **8 years** of ERA5 brings the 30-year statistics into good agreement with ERA5. The error in the 36-year mean integrated vapour transport falls by **51%** compared with the free-running E3SM. — [arXiv 2402.18484](https://arxiv.org/html/2402.18484); [OSTI](https://www.osti.gov/biblio/2328637)
- **Code and follow-up:** code and data are on [Zenodo 10657047](https://zenodo.org/records/10657047). A 2026 JAMES follow-up makes the correction probabilistic (ensembles of VAE-based RNNs) — [Wiley 10.1029/2024MS004755](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2024MS004755). The follow-up's MIT affiliation was not checked.
- **Math [standard nudging form; the paper's exact architecture and loss not re-read]:**
  - Nudged training run: du/dt = F_coarse(u) − (1/τ)(u − u_ref).
  - Learn G_θ so that u_ref(t) ≈ G_θ(u_nudged(t − s : t)) over the training window.
  - Apply ũ(t) = G_θ(u_free(t − s : t)) to long free runs, and estimate tails and return levels from ũ.
- **Theme and situation:** theme 2, intense-rainfall and rare-event statistics. The same tool applies to the dry tail, so theme 3 as well.

### Inferences
**How it changes our model:**
- **Debias the drivers.** The inland-inflow factor (recharge) and the sea-boundary level currently come from coarse climate output or from synthetic AR(1) series. Train a correction operator on a short overlap period, using station rainfall or reanalysis for the Adriatic coast and the Durrës tide gauge, then run long corrected series to set (i) the design multi-day rainfall/recharge tail and (ii) the dry-tail persistence.
  - If the coarse driver under-represents multi-year droughts, the well-placement safety margin must widen: move the well inland or lower the pumping cap.
- **Debias the model itself.** Use a coarse-grid, cheaper version of MONTIMI-GO nudged toward a few fine Newton-solver runs, or toward the annual chloride sample. This gives long Monte Carlo runs for the 1-in-100-year exceedance of 250 mg/L at the screen, which is the quantity that should drive well placement.

**Innovation (NUDGE-GO):**
- Treat SPIRANCA-GO's one-chloride-sample-per-year re-anchoring as the "nudging" target. Train a correction operator on the coarse transport model nudged toward those samples, then estimate P(C_screen > 250 mg/L) at return periods 10–100× longer than the record.
- **Test on the synthetic truth:** does the well position chosen from the corrected tails match the position chosen from the true tails, and does it beat the uncorrected coarse model?
- **Candidate criterion:** decision regret as a function of training-window length. The paper's "two orders of magnitude" claim was shown for a QG model, not for transport with clay/silt memory.

### Gaps
- The precipitation-specific tail numbers in E3SM (for example extreme-precipitation return levels) were not visible in what I could access. I found no reported number specific to precipitation extremes.
- The printed byline affiliations were not seen directly.

---

## P3 — Rudy, S. H. & Sapsis, T. P. (2023). Output-weighted and relative entropy loss functions for deep learning precursors of extreme events. *Physica D: Nonlinear Phenomena*, 443, 133570. https://doi.org/10.1016/j.physd.2022.133570

### Takeaway
An MIT loss-function tool for training predictors and alarms of rare extreme events. The squared error is weighted by the inverse probability density of the true output, so rare high values are not drowned out. This plugs directly into the SPIRANCA-GO chloride alarm, whose training data are dominated by normal, low-chloride years.

### Cited Findings
- **Citation:** Physica D, volume 443, article 133570, DOI 10.1016/j.physd.2022.133570. The volume is dated 2023; the paper was online in November 2022. Preprint arXiv 2112.00825. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0167278922002743); [ResearchGate](https://www.researchgate.net/publication/365086931_Output-weighted_and_relative_entropy_loss_functions_for_deep_learning_precursors_of_extreme_events); [arXiv 2112.00825](https://arxiv.org/pdf/2112.00825). **DOI confirmed (index).**
- **MIT authors:**
  - Sapsis is William I. Koch Professor in MIT Mechanical Engineering — [MIT MechE](https://meche.mit.edu/people/faculty/sapsis@mit.edu).
  - Samuel Rudy held an NSF postdoctoral fellowship hosted at MIT, with Sapsis as sponsoring scientist — [NSF DMS-1902972](https://grantome.com/grant/NSF/DMS-1902972).
  - The MIT lab announced the Physica D acceptance on 27 November 2022 — [Sapsis lab news](https://sandlab.mit.edu/paper-on-new-ml-training-criteria-for-improving-models-for-predicting-extreme-events-has-been-accepted-to-physica-d).
  - The printed byline was not seen, so the MIT affiliation on the article itself is unverified but highly likely.
- **Problem:** systems with extreme events "by definition, yield imbalanced datasets", and standard losses "easily ignore rare events". — [arXiv 2112.00825](https://arxiv.org/pdf/2112.00825)
- **Core criterion:** the output-weighted loss L_OW weights the squared error "by the inverse of the likelihood of the true output". For example, L_OW = (1/N) Σ_i |f̂(x_i) − f(x_i)|² / p_f(f(x_i)). Plain MSE "may still be small while missing large y" when outliers are a small fraction of the data. — [arXiv 2112.00825](https://arxiv.org/pdf/2112.00825)
- **Other losses:** the paper proposes an *adjusted* output-weighted loss and relative-entropy-based losses for low-dimensional outputs. It reports significant accuracy gains for extreme-event predictions on several dynamical systems. It contrasts its losses with Guth & Sapsis's maximum adjusted area under the precision-recall curve, which is non-differentiable and hard to estimate from small samples. — [ScienceDirect abstract](https://www.sciencedirect.com/science/article/abs/pii/S0167278922002743)
  - The exact form of the adjustment and of the relative-entropy loss is unverified.
- **Later evidence:** a later paper reports that output-weighted losses significantly improve the prediction of outlier events in flows including airfoil and Kolmogorov flow. — [arXiv 2303.07056](https://arxiv.org/html/2303.07056v1)
- **Main quantitative result:** I could not confirm specific accuracy numbers from the abstract.
- **Theme and situation:** theme 2, extreme events and early warning. It applies to intense-rainfall surges in chloride and to the drought-driven rise.

### Inferences
**How it changes our model:**
- SPIRANCA-GO fits anchor regression with squared loss: min_b ‖(I − Π_A)(Y − Xb)‖² + γ‖Π_A(Y − Xb)‖², with anchors A = (r, pumping anomaly).
- **Proposed change:** use an output-weighted version with W = diag(1/p̂_Y(y_i)), where p̂_Y is a kernel estimate of the chloride (or sea-fraction) density. Compute the margin quantile q_{1−α}(b) from the weighted residual distribution.
- **Expected direction:** the alarm becomes sharper near and above 250 mg/L. There should be fewer missed exceedances in drought-persistence and storm-surge years, at the cost of some false alarms in normal years. The pumping cap tied to the alarm becomes more conservative only when the tail is actually approached.

**Innovation (output-weighted anchor regression, OW-ANCHOR-GO):**
- **Conjecture to prove or test:** the weighted anchor objective equals a worst case over anchor-span shifts under the output-tilted distribution p̃ ∝ p/p_Y. If so, it would give tail-focused shift robustness, which neither method claims on its own.
- **Numerical test on the SPIRANCA-GO synthetic record** (AR(1) rainfall with φ = 0.7, surge shocks, a known pumping step): compare the miss rate and the false-alarm rate for C > 250 mg/L, standard versus output-weighted.
- **Sampling-time rule:** place the one annual chloride sample at the time of lowest p̂_Y(predicted C), in the tail. This is an output-weighted sampling rule for re-anchoring.

### Gaps
- The printed affiliation and the headline accuracy numbers were not confirmed in this session.
- The paper is about neural predictors of dynamical systems. Moving the weighting into a linear anchor-regression alarm is our own extension.

---

## P4 — Schlosser, C. A., Sokolov, A., Strzepek, K., Thomas, T., Gao, X. & Arndt, C. (2021). The changing nature of hydroclimatic risks across South Africa. *Climatic Change*, 168, article 28. https://doi.org/10.1007/s10584-021-03235-5

### Takeaway
This is the MIT Joint Program's risk-based (probabilistic) tool for drought and water-supply planning. "Hybrid frequency distributions" combine Monte Carlo runs of global human–Earth-system uncertainty with CMIP5 spatial patterns. The result is a probability of regional drying versus wetting under each climate-policy scenario. It shows that drying risk can be skewed 3–4× over wetting, and that strong mitigation delays the regional risk by about 30 years. This gives a quantitative basis for the timing of adaptation.

### Cited Findings
- **Citation:** Climatic Change, vol. 168, article 28, published 27 October 2021, open access (CC BY 4.0), DOI 10.1007/s10584-021-03235-5. — [DSpace@MIT 1721.1/136966](https://dspace.mit.edu/handle/1721.1/136966); [OSTI 1976665](https://www.osti.gov/pages/biblio/1976665-changing-nature-hydroclimatic-risks-across-south-africa). **DOI confirmed (index).** An earlier version is MIT Joint Program Report 342 (2020) — [globalchange.mit.edu/publication/17483](https://globalchange.mit.edu/publication/17483).
- **MIT authors:** the work is from the MIT Joint Program on the Science and Policy of Global Change and is deposited on DSpace@MIT. MIT News presents it as an MIT study led by Schlosser. — [MIT News, 5 Nov 2021](https://news.mit.edu/2021/scientists-project-increased-risk-water-supplies-south-africa-this-century-1105); [MIT JP page](https://globalchange.mit.edu/publication/17483).
  - Inference: Schlosser, Sokolov, Strzepek and Gao are MIT Joint Program; Thomas and Arndt are IFPRI. The full printed byline was not seen.
- **Method:** large ensembles combine Monte Carlo projections from a human–Earth system model of intermediate complexity (the MIT IGSM) with pattern-scaled responses from CMIP5 models, for western, central and eastern South Africa, under scenarios with different levels of global abatement. — [MIT News](https://news.mit.edu/2021/scientists-project-increased-risk-water-supplies-south-africa-this-century-1105)
  - The ensembles are called hybrid frequency distributions (HFDs). The MIT JP report describes each as a **7,200-member meta-ensemble**. — [search summary of MIT JP Report 342](https://globalchange.mit.edu/publication/17483)
- **Main quantitative results:**
  - Western and central South Africa show a preponderance of risk toward lower precipitation, **3 to 4 times** the risk of higher precipitation.
  - Without emissions targets there is a **>50% chance** that mid-century warming reaches three times the current two-standard-deviation range of variability. Aggressive targets largely remove that risk.
  - Under a 1.5 °C target, the end-of-century (2065–2074) precipitation risk resembles the 2030s risk with no target. That is a delay of **about 30 years**. — [MIT News](https://news.mit.edu/2021/scientists-project-increased-risk-water-supplies-south-africa-this-century-1105); [DSpace abstract via search](https://dspace.mit.edu/handle/1721.1/136966)
- **Follow-up:** MIT JP Report 368 (2023) extends the analysis to all of Africa — [globalchange.mit.edu/publication/18066](https://globalchange.mit.edu/publication/18066).
- **Math [HFD construction as known from the MIT JP method; not re-read for this paper]:**
  - ΔX_region(τ) = ΔT_global(τ; IGSM member m, scenario s) × κ_region,j, where κ_region,j is the CMIP5 model j's regional change per degree of global warming.
  - The HFD is the empirical distribution over all (m, j) pairs. The decision metric is the probability of a drying (or warming) exceedance per decade and scenario.
- **Theme and situation:** theme 3, drought and water-supply risk, and theme 1, risk-based planning and the timing of adaptation.

### Inferences
**How it changes our model:**
- Our recharge model is stationary AR(1) (φ = 0.7) with a fixed mean. The paper supports adding a scenario-dependent, probabilistic mean shift: R_t = R̄·(1 + ΔP(τ, s)) + AR(1) anomaly.
  - ΔP is drawn from an HFD built for the Albanian Adriatic coast. That region is a Mediterranean drying hot spot, an inference consistent with Tuel & Eltahir (2020), which is already covered.
- The inland-inflow boundary factor then drifts down with a skewed distribution. The well-placement margin should be **asymmetric**: designed for the drying tail, not for symmetric ± recharge scenarios. That pushes toward more conservative pumping over time and inland well positions.
- The "30-year delay" result turns into a decision-timing question for us: how many years until P(C_screen > 250 mg/L) passes a tolerance, under each emissions scenario.

**Innovation (risk-delay / adaptation lead-time criterion):**
- Define T_s* = min{τ : P_HFD(C_screen > 250 mg/L in decade τ | scenario s) ≥ ε}, computed with the MONTIMI-GO surrogate under HFD-perturbed recharge.
- Use T_s* to decide when the well should be relocated: relocate now, or relocate when the SPIRANCA-GO alarm fires. Compare the two as a real option.
- **Numerical test:** the distribution of time-to-threshold for decisions taken now versus deferred decisions, and the expected regret of each.

### Gaps
- The HFD is built for mean seasonal or annual precipitation and temperature, not daily extremes or recharge. Mapping it to recharge is non-linear and is our own step.
- I could not see the paper's tables for the 2 °C and 1.5 °C scenarios.
- The printed author affiliations were not seen directly.

---

## P5 — Abadie, A. (2021). Using synthetic controls: feasibility, data requirements, and methodological aspects. *Journal of Economic Literature*, 59(2), 391–425. https://doi.org/10.1257/jel.20191450

### Takeaway
This is the MIT reference guide to synthetic control. It builds a counterfactual "no-intervention" trajectory for one treated unit as a convex combination of untreated donors, and it states when that is feasible. For us, the treated unit is a supply well after a known pumping change, and the donors are wells or piezometers outside its influence. It is the natural design-based check of a model-predicted pumping effect on chloride.

### Cited Findings
- **Citation:** Journal of Economic Literature, 59(2), 391–425, June 2021, DOI 10.1257/jel.20191450. — [IDEAS/RePEc](https://ideas.repec.org/a/aea/jeclit/v59y2021i2p391-425.html); [DSpace@MIT 1721.1/144417](https://dspace.mit.edu/handle/1721.1/144417). **DOI confirmed (index).**
- **MIT author:** Alberto Abadie, MIT Department of Economics. An author-hosted copy is on DSpace@MIT "in accordance with the publisher's policy". — [DSpace@MIT](https://dspace.mit.edu/entities/publication/667a4480-667d-4844-889a-050157f54f4c). The printed footnote was not seen.
- **Content:** a practical guide to synthetic control that focuses on when the method works and when it fails. It covers the design advantages, the settings where estimates are reliable or unreliable, and recent extensions. — [IDEAS/RePEc](https://ideas.repec.org/a/aea/jeclit/v59y2021i2p391-425.html)
- **Math [formula from the paper as known; not re-read this session]:**
  - Weights: W* = argmin_W Σ_h v_h (X_{1h} − Σ_{j≥2} w_j X_{jh})², subject to w_j ≥ 0 and Σ_j w_j = 1.
  - Effect: τ̂_{1t} = Y_{1t} − Σ_j w_j* Y_{jt} for t > T_0.
  - Inference by in-space placebos, using the ratio of post- to pre-intervention RMSPE.
  - Bias is small when the pre-period fit is good and T_0 is long relative to the size of the idiosyncratic noise.
  - The feasibility conditions include: no anticipation, no spillover onto donors, a donor pool similar to the treated unit, and the treated unit not being extreme relative to the donor convex hull.
- **Main quantitative result:** this is a methods guide, so there is no headline number. The empirical illustrations were not re-checked this session.
- **Theme and situation:** theme 4, counterfactual policy evaluation of a known pumping decision or a drought-time abstraction ban.

### Inferences
**How it changes our model:**
- SC gives a model-free estimate of the effect of the utility's known pumping change on screen chloride.
- That estimate (a) serves as an independent calibration target for MONTIMI-GO's buoyancy and immobile-zone exchange parameters, which control how fast and how far the screen responds, and (b) diagnoses the regime where SPIRANCA-GO fails after the pumping decision. If the SC effect is larger than the model's, the pumping cap must be lowered.
- The key aquifer-specific threat is **spillover**: donor wells inside the cone of depression or the salt-wedge response violate the no-interference condition.

**Innovation (physics-filtered synthetic control):**
- Restrict the donor pool to wells whose adjoint sensitivity ∂C_j/∂Q_treated in MONTIMI-GO is below a threshold. The adjoint is already in the test bed.
- Add the post/pre-RMSPE placebo ratio as an "alarm validity test" for SPIRANCA-GO.
- **Numerical test:** on the synthetic aquifer with a known pumping effect, compare the bias and coverage of standard SC with physics-filtered SC, with and without spillover.

### Gaps
- The printed affiliation and the exact weighting and inference formulas in the JEL version were not re-read in this session.

---

## P6 — Chernozhukov, V., Wüthrich, K. & Zhu, Y. (2021). An exact and robust conformal inference method for counterfactual and synthetic controls. *Journal of the American Statistical Association*, 116(536), 1849–1864. https://doi.org/10.1080/01621459.2021.1920957

### Takeaway
This MIT paper treats a policy effect as a counterfactual prediction plus a structural-break test. It inverts permutation (conformal) tests to get confidence sets. These are exact in finite samples when the residuals are exchangeable and approximately valid under serial dependence. This is the certified-inference counterpart of SPIRANCA-GO's margin, and it gives a principled re-anchoring trigger.

### Cited Findings
- **Citation:** JASA 116(536), 1849–1864 (2021), DOI 10.1080/01621459.2021.1920957. — [IDEAS/RePEc](https://ideas.repec.org/a/taf/jnlasa/v116y2021i536p1849-1864.html); [SUFE index](https://academicnewsletter.sufe.edu.cn/info/443659). **DOI confirmed (index).** Preprint arXiv 1712.09089, versions from 2018 to 2022 — [arXiv v9](https://arxiv.org/pdf/1712.09089v9).
- **MIT author:** Victor Chernozhukov, MIT Economics. The DSpace@MIT record lists "dc.contributor.author Chernozhukov, Victor" — [DSpace@MIT 1721.1/144458](https://dspace.mit.edu/handle/1721.1/144458?show=full).
  - From my knowledge, not verified: Wüthrich is at UC San Diego and Zhu at Brandeis.
- **Method:** permutation inference for counterfactual and synthetic-control methods. It covers difference-in-differences, factor and matrix-completion models and fused time-series panel models. — [arXiv v9](https://arxiv.org/pdf/1712.09089v9)
  - The causal question is treated as a counterfactual prediction problem plus a structural-break test, borrowing from conformal prediction. — [arXiv v9](https://arxiv.org/pdf/1712.09089v9)
- **Guarantees:** size control is exact in finite samples when the estimation residuals are exchangeable. Under serial dependence, approximate uniform size control holds under weak, checkable conditions. — [arXiv v7](https://arxiv.org/pdf/1712.09089v7)
- **Confidence sets:** obtained by inverting the test over a grid of candidate effects. Conformal inference gives no standard error. — [coresynth R docs](https://rdrr.io/cran/coresynth/man/conformal_inference.html)
- **Empirical example:** Rhode Island's inadvertent decriminalisation of indoor prostitution in 2003. The outcomes are rape rates and STIs, including log female gonorrhoea incidence. — [arXiv v7](https://arxiv.org/pdf/1712.09089v7); [mlsynth replication](https://mlsynth.readthedocs.io/en/latest/replications/cwz_conformal.html). The effect sizes were not verified.
- **Math [formula from the paper as known; not re-read this session]:**
  - Under H_0: θ = θ_0, impose the null on the post-period, fit the counterfactual model on all T periods, and obtain residuals û_t.
  - Statistic: S_q(û) = ((1/√T*) Σ_{t>T_0} |û_t|^q)^{1/q}.
  - p-value: p̂ = 1 − (1/|Π|) Σ_{π∈Π} 1{S_q(û_π) < S_q(û)}. Π is the set of moving-block (cyclic) permutations, or iid permutations.
  - The confidence set is {θ_0 : p̂(θ_0) > α}.
- **Theme and situation:** theme 4, causal effect of a known pumping decision or a drought ban. It also covers theme 1, certified decision margins.

### Inferences
**How it changes our model:**
- SPIRANCA-GO's margin q_{1−α}(b) is a residual quantile that assumes the training regime carries on.
- CWZ supplies the missing formal **test that the regime has broken**. After a known pumping change, run the conformal structural-break test on the anchor-regression residuals of screen chloride. If H_0 (no effect beyond prediction) is rejected, re-anchor immediately with a chloride sample, instead of on the fixed annual schedule.
- Our rainfall has φ = 0.7, so iid permutations are not valid. Use moving-block permutations; the paper's approximate validity under serial dependence is what licenses this.
- **Decision use:** invert the test to get a confidence set for the pumping effect on chloride. Set the largest pumping rate whose upper confidence bound keeps C_screen + effect ≤ 250 mg/L. This pushes toward a certified, data-driven pumping cap.

**Innovation (CONFORM-ANCHOR-GO, a conformal re-anchoring rule):**
- **Conjecture to test numerically:** under stationarity, block-permutation re-anchoring keeps the false re-anchoring rate at or below about α, while cutting the detection delay after a regime change compared with fixed annual sampling.
- Simulate this on the SPIRANCA-GO synthetic record with a known pumping step and drought persistence.

### Gaps
- The printed affiliations of Wüthrich and Zhu, and the exact statistic and permutation set in the JASA version, were not re-read.
- The empirical effect sizes were not verified.

---

## Exclusions, near-misses and overall verification status

### Takeaway
Several obvious MIT candidates are already in our earlier reviews and were excluded. All six kept papers passed the duplicate check. Their DOIs agree across at least two index records. MIT affiliation rests on MIT repository, news or lab records, not on a printed byline I could open.

### Cited Findings
- **Excluded as already covered** (all found in `_already_covered_references.txt`):
  - Gori, Lin, Xi & Emanuel (2022), *Nature Climate Change* 12, 171–178 (TC rainfall–surge hazard).
  - Pickering, Guth, Karniadakis & Sapsis (2022), *Nature Computational Science* 2, 823–833.
  - Zhang, Cammarata, Squires, Sapsis & Uhler (2023), *Nature Machine Intelligence* 5, 1066–1075.
  - Blanchard & Sapsis (2021), *SIAM/ASA JUQ* 9(2).
  - Sapsis & Blanchard (2022), *Phil. Trans. R. Soc. A*.
  - Tuel & Eltahir (2020), *J. Climate* 33(14).
  - Short Gianotti, Akbar, Feldman, Salvucci & Entekhabi (2020), *GRL* 47(5).
  - Chernozhukov, Newey & Singh (2022), *Econometrica*.
  - Squires & Uhler (2023), *FoCM*.
  - Bertsimas, Shtern & Sturt (2022 OR; 2023 MS).
  - Bertsimas, den Hertog & Pauphilet (2021), *SIOPT*.
  - Maragno et al. (2025), *OR*.
  - Lu, Saló-Salgado, Marzouk & Juanes (2025), *WRR*.
  - Elmachtoub & Grigas (2022), which is also not MIT.
- **Out of the date window:** the MIT water-supply planning study "Learning and flexibility for water supply infrastructure planning under groundwater resource uncertainty" (Environmental Research Letters) is from **2019** — [DSpace@MIT record](https://dspace.mit.edu/entities/publication/20128ea6-b8c8-43c4-9e05-d6ae93a48dd0). The same applies to Fletcher, Lickley & Strzepek (2019, *Nature Communications*), from my knowledge.

### Inferences
- The MIT literature in this window that offers ready-made *decision* tools for drought and groundwater is thin. P4 is the strongest MIT drought/water-supply candidate I found. A coordinator who needs a groundwater-specific MIT decision paper may have to accept a 2019 paper, which breaks the window, or a non-MIT one.
- P2 and P3 form the theme-2 pair from one group (Sapsis). If diversity of groups matters, keep only one of them.

### Gaps
- Crossref, doi.org, arXiv, DSpace@MIT, OSTI and the publisher sites were unreachable for direct fetching in this session. If those hosts are allowed in the session's network settings, a re-check against Crossref would make each DOI "Crossref-confirmed" rather than "index-confirmed".
- I found no MIT 2020–2026 paper with an explicit decision model for coastal-aquifer pumping under drought, such as robust or stochastic optimisation of groundwater abstraction. The search was not exhaustive.
- I found no verified MIT 2020–2026 paper by O'Gorman or Emanuel that both offers a decision tool and is not already covered. Emanuel's CMIP6 TC-downscaling work (J. Climate, 2021) was considered but not verified and is not included.
