---
title: "The objective function of the stakeholder decision under extremes"
subtitle: "Well site, pumping rule, certified alarm and chloride sampling, robust over intense rainfall, drought and causal change (MONTIMI-GO + SPIRANCA-GO + ROJA-GO)"
author: "Dulian Zeqiraj"
---

## 1. What is decided

| Symbol | Decision | Decided by | Part of the method |
|---|---|---|---|
| $x_s$ | position of the supply-well screen | utility and water agency | MONTIMI-GO |
| $\pi$ | pumping rule: $u_{t+1}=u_{\mathrm{dec}}$ while the alarm is silent, $u_{\mathrm{cut}}$ after it sounds | utility, agreed with the stakeholders | Section 4 |
| $m$ | margin of the alarm (its certificate) | modeller | SPIRANCA-GO |
| $\sigma=(\Delta,K,B)$ | sampling rule: interval, re-anchoring window, budget of extra samples | monitoring office | ROJA-GO |
| $H_{\max}$ | cap on private abstraction in a declared drought (optional lever) | water agency | Section 6 |

## 2. The model the decision acts on (the equality constraints)

The assembled system of the section, as in the assembled-system note: flow with hydraulic memory, Darcy with buoyancy, salt with two immobile zones, $k=1,2$:

$$S_s\frac{\partial h}{\partial t}+\nabla\cdot\mathbf q=W(x_s,Q_t,H_t)-\sum_{k}s_k a_k\,(h-h_k),\qquad \frac{\partial h_k}{\partial t}=a_k\,(h-h_k)\qquad(1)$$

$$\mathbf q=-\mathbf K\,(\nabla h+\delta\,c\,\mathbf e_z)\qquad(2)$$

$$n\frac{\partial c}{\partial t}+\nabla\cdot(\mathbf q c)-c\,\nabla\cdot\mathbf q-\nabla\cdot(n\mathbf D\nabla c)+\sum_k n\,b_k a_k\,(c-c_k)=0,\qquad \frac{\partial c_k}{\partial t}=a_k\,(c-c_k)\qquad(3)$$

Boundaries and sources, where the storyline $\xi$ enters:

$$h_{\mathrm{sea}}=(1+\delta)\,\eta_\xi(t)-\delta z,\quad q_{n,\mathrm{inland}}=q_{\mathrm{in}}R_{\xi,t},\quad W=-\overline{Q}(1+u_t)\,e_Q(x_s)-\overline{H} h_{\xi,t}\,e_P\qquad(4)$$

$$R_{\xi,t}=1+0.2\,r^{\mathrm{eff}}_t+0.06\,e^R_t,\qquad h_{\xi,t}=1-(0.25+\phi_{\xi,t})\,r^{\mathrm{eff}}_t+0.15\,e^H_t\qquad(5)$$

The goal is the sea fraction over the screen $\Gamma_s$ and its chloride:

$$J_t=\frac{1}{|\Gamma_s|}\int_{\Gamma_s}c\,\mathrm dz,\qquad \mathrm{Cl}_t=C_f+J_t\,(C_s-C_f),\qquad \mathrm{Cl}_t>250\ \mathrm{mg/L}\iff J_t>\varepsilon_{\mathrm{lim}}=0.0109\qquad(6)$$

| Storyline $\xi$ | Recorded gauge $r^{g}_t$ vs. effective $r^{\mathrm{eff}}_t$ | Behaviour $\phi_{\xi,t}$ | Sea $\eta_\xi$ |
|---|---|---|---|
| ordinary | $r^g=r^{\mathrm{eff}}$, AR(1), lag-one correlation 0.7 | 0 | trend |
| intense rainfall | $r^g=r+2.5$, $r^{\mathrm{eff}}=r+0.5$ for two years (runoff) | 0 | trend (+ surge) |
| record drought | $r^g=r^{\mathrm{eff}}=0.5r-2$ for six years | 0 | trend |
| causal change | as the drought | 0.5 during the drought (pumping response ×3) | trend |
| compound | drought, then intense rainfall | 0 | trend (+ surge) |

## 3. The objective function

Deliver as much water as possible in the worst storyline, while counting the days the supply is unfit and the samples spent. The three terms inside the sum are the water delivered, the customer disruption days and the cost of samples:

$$\max_{x_s,\,\pi,\,m,\,\sigma}\ \min_{\xi\in\Xi}\ \mathbb E_{\omega}\left[\sum_{t=1}^{T}\beta^{t}\left(\overline{Q}\,(1+u_t)\,\Delta t-\lambda_D\,N_c\,\Delta t\,\mathbf{1}\{J_t>\varepsilon_{\mathrm{lim}}\}-c_s\,n_t\right)\right]\qquad(7)$$

subject to (1)–(6) and

$$\frac{1}{T}\sum_{t=1}^{T}\mathbb P_\xi(J_t>\varepsilon_{\mathrm{lim}})\le\varepsilon\qquad\text{for every }\xi\in\Xi\qquad(8)$$

$$\mathbb P_\xi(\hat Y_t-b_t-Y_t>m)\le\alpha,\qquad Y_t=-\log_{10}J_t\qquad(9)$$

$$u_{t+1}=\begin{cases}u_{\mathrm{cut}}, & A_t=1\\ u_{\mathrm{dec}}, & A_t=0\end{cases},\qquad A_t=\mathbf{1}\{\hat Y_t-b_t\le y_{\ell}+m\},\quad y_{\ell}=-\log_{10}\varepsilon_{\mathrm{lim}}\qquad(10)$$

$$n_t=\mathbf{1}\{t\ \text{ends a year}\}+\mathbf{1}\{F_t\},\qquad \sum_{t\in\text{year}}\mathbf{1}\{F_t\}\le B,\qquad b_t=\frac{1}{K_t}\sum_{j=1}^{K_t}e_{(j)}\qquad(11)$$

$$m=q_{1-\alpha}(\mathbf b)+\overline{\delta}\,\max\{0,\ell(\mathbf b)\}\qquad(12)$$

| Term | Meaning | Source |
|---|---|---|
| $\min_{\xi}$ | the worst of the five storylines; the decision must hold in all | storylines and UNSEEN (Kelder et al. 2020) |
| $\overline{Q}(1+u_t)\Delta t$ | water pumped in season $t$ | utility |
| $\lambda_D N_c\Delta t\,\mathbf{1}\{\cdot\}$ | customer disruption days, $N_c$ customers, value $\lambda_D$ per day | Becher et al. (2023) |
| $c_s n_t$ | cost of chloride samples; $B$ caps the extra ones | Considine et al. (2025) |
| (8) | exceedance share at most $\varepsilon$ in every storyline | chance constraint |
| (9), (12) | the alarm under-warns at most a share $\alpha$; $\overline{\delta}$ is the certified shift radius | SPIRANCA-GO, Theorem S2 |
| (10) | cut pumping in the season after an alarm | risk threshold (Schneider et al. 2022) |
| (11) | yearly sample, extra sample when the watch fires ($F_t$), re-anchoring on the last $K_t$ sample errors $e_{(j)}$ | ROJA-GO |

## 4. Three equivalent forms for the stakeholders

**(a) Constrained form (recommended).** Drop the penalty in (7) and keep (8): the most water in the worst storyline, with the exceedance share at most $\varepsilon$ everywhere.

$$\max_{x_s,\pi,m,\sigma}\ \min_{\xi}\ \mathbb E[\sum_t\overline{Q}(1+u_t)\Delta t]\quad\text{s.t. (1)–(6), (8)–(12)}\qquad(13)$$

**(b) Weighted form.** Keep the penalty and drop (8); $\lambda_D$ is the shadow price of (8): the water the stakeholders accept to lose to avoid one disruption day.

**(c) Minimax regret.** $\min_{\pi}\max_{\xi}[V^{\mathrm{best}}_\xi-V_\xi(\pi)]$, where $V_\xi$ is the value (7) in storyline $\xi$ and $V^{\mathrm{best}}_\xi$ the best value attainable if $\xi$ were known (Xu et al. 2021). It is less conservative than (13) when one storyline is much harder than the others.

## 5. Innovation: the inner constraints are met by construction

Problem (7)–(12) looks large, but two of its parts have closed forms, so the outer search runs over a handful of numbers.

- **The margin** (12) satisfies (9) for every shift of size up to $\overline{\delta}$ in the span of the anchors (SPIRANCA-GO, Theorem S2), with $\overline{\delta}$ taken from an UNSEEN-type ensemble instead of the short record.
- **The window** $K_t$ in (11) minimises the error bound of re-anchoring (Proposition R1 of review 61):

$$K_t=\arg\min_{K\ge1}[\sigma^2(1+\frac1K)+\frac{\rho_t^2\Delta^2(K+1)^2}{4}],\qquad K_t^2(K_t+1)=\frac{2\sigma^2}{(\rho_t\Delta)^2},\qquad K_t=1\ \text{if}\ \rho_t\Delta\ge\sigma\qquad(14)$$

- **What is left** is the outer search over $(x_s,u_{\mathrm{dec}},u_{\mathrm{cut}},B,H_{\max})$, evaluated with the simulator over the storylines; only (8) needs simulation, because (9) and (11) hold by construction.

## 6. Check on the variable-density section

Each tested rule is scored on the two numbers of the constrained form (13): the exceedance share in the worst storyline (constraint (8), $\varepsilon=10\%$) and the water delivered in the worst storyline (the objective), mean over 20 aquifers and 6 weather sequences each, 30 years after the decision.

| Rule | Worst-storyline exceedance (8) | Worst-storyline water (13) | Samples in 30 years | Feasible for $\varepsilon=10\%$ |
|---|---|---|---|---|
| No action | 59.3% (causal change) | 100.0% (ordinary) | 0 | no |
| Static alarm | 21.2% (causal change) | 76.2% (causal change) | 0 | no |
| Yearly sample (S5) | 11.5% (causal change) | 72.1% (causal change) | 29 | no |
| Screen sensor at 89% of the standard | 24.5% (causal change) | 84.4% (causal change) | 0 | no |
| ROJA-GO | 9.1% (causal change) | 71.2% (causal change) | 35 | yes |

Only **ROJA-GO** satisfies (8) with $\varepsilon=10\%$, so among the tested rules it is the solution of (13): it delivers 71% of the planned water in the worst storyline, the causal change, where the exceedance share is 9.1%. 
To tighten to $\varepsilon=5\%$ the binding storyline is the causal change, so the next lever is the cap $H_{\max}$ on private abstraction in a declared drought, or a lower $u_{\mathrm{dec}}$; the objective (13) tells how much water each costs.

*Caveat:* synthetic aquifers on a 2-D section; $\lambda_D$, $c_s$ and $\varepsilon$ are for the stakeholders to set. Code: experiments/spiranca_go/sx_run.py; results res/sx.json.