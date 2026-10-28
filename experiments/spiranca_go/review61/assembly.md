---
title: "Assembly of the equations and the solution algorithm"
subtitle: "MONTIMI-GO (physics) with the SPIRANCA-GO / ROJA-GO decision layer: equations, coupling diagram and flowchart"
author: "Dulian Zeqiraj"
---

## 1. The assembled system

A vertical section of the coastal aquifer (unit width along the coast), finite volumes in space, implicit Euler in time. Unknowns per cell: head $h$ and sea fraction $c$; local memory states $h_k$, $c_k$ ($k=1,2$: silt and clay) are eliminated in each step.

$$S_s\frac{\partial h}{\partial t}+\nabla\cdot\mathbf q=W-\sum_{k=1}^{2}s_k a_k\,(h-h_k),\qquad \frac{\partial h_k}{\partial t}=a_k\,(h-h_k)\qquad(1)$$

$$\mathbf q=-\mathbf K\,(\nabla h+\delta\,c\,\mathbf e_z)\qquad(2)$$

$$n\frac{\partial c}{\partial t}+\nabla\cdot(\mathbf q c)-c\,\nabla\cdot\mathbf q-\nabla\cdot(n\mathbf D\nabla c)+\sum_{k=1}^{2}n\,b_k a_k\,(c-c_k)=W_{in}\,(c_{inj}-c),\qquad \frac{\partial c_k}{\partial t}=a_k\,(c-c_k)\qquad(3)$$

$$n\mathbf D\ \text{on a face}=n D_m+\frac{\alpha_L q_n^2+\alpha_T q_t^2}{|\mathbf q|}\qquad(4)$$

$$\text{ions } i\in\{\mathrm{Cl,Na,K,Ca,Mg,SO_4,HCO_3}\}:\ \text{transport as in equation 3},\qquad K_{i/j}=\frac{\beta_i^{1/z_i}\,a_j^{1/z_j}}{\beta_j^{1/z_j}\,a_i^{1/z_i}},\quad \sum_i\beta_i=1\qquad(5)$$

$$h_{\mathrm{sea}}=(1+\delta)\,\eta_\xi(t)-\delta z,\ c=1\ \text{on inflow};\quad q_{n,\mathrm{inland}}=q_{in}R_{\xi,t},\ c=0;\quad W=-\overline{Q}(1+u_t)\,e_Q(x_s)-H_t\,e_P\qquad(6)$$

$$R(y^0)=0\ \ \text{steady pre-development state},\quad\text{then 100 years of private abstraction alone}\ \to\ (y^0,z^0)\qquad(7)$$

$$J_t=\frac{1}{|\Gamma_s|}\int_{\Gamma_s}c\,\mathrm dz,\qquad \mathrm{Cl}_t=C_f+J_t\,(C_s-C_f),\qquad \mathrm{Cl}_t>250\ \mathrm{mg/L}\iff J_t>\varepsilon_{\mathrm{lim}}=0.0109\qquad(8)$$

| Symbol | Meaning | Symbol | Meaning |
|---|---|---|---|
| $h,\ c$ | head, sea fraction | $S_s,\ n,\ \mathbf K$ | storage, porosity, conductivity |
| $h_k,\ c_k$ | memory states (silt, clay) | $a_k,\ s_k,\ b_k$ | exchange rates, capacities |
| $\delta$ | density contrast (0.025) | $\alpha_L,\ \alpha_T,\ D_m$ | dispersivities, diffusion |
| $\eta_\xi,\ R_{\xi,t},\ H_t$ | sea level, recharge factor, private abstraction | $x_s,\ u_t$ | well screen, pumping anomaly |
| $\beta_i,\ a_i,\ z_i$ | exchanger fraction, activity, charge | $\Gamma_s$ | supply screen (top 20 m) |

The tests use the goal-guided assembly of MONTIMI-GO: buoyancy, the two immobile zones and full coupling are kept; the hydraulic memory terms of (1), whose weight on the goal is small, and the ions (5), which never feed back, can be switched off.

## 2. One time step, the Newton solve and the adjoint

Implicit Euler eliminates the memory states exactly, $z_k^n=\alpha_k z_k^{n-1}+\beta_k y^n$ with $\alpha_k=1/(1+a_k\Delta t)$ and $\beta_k=1-\alpha_k$, so that each step is one coupled system in $y^n=(h^n,c^n)$:

$$R_n=\begin{pmatrix}V S_s\frac{h^n-h^{n-1}}{\Delta t}+\mathrm{Div}\,\mathbf q^n-W^n+\sum_k V s_k a_k\alpha_k\,(h^n-h_k^{n-1})\\ V n\frac{c^n-c^{n-1}}{\Delta t}+\mathrm{Div}(\mathbf q^n c^n)-c^n\mathrm{Div}\,\mathbf q^n-\mathrm{Div}(n\mathbf D^{n-1}\nabla c^n)+\sum_k V n b_k a_k\alpha_k\,(c^n-c_k^{n-1})\end{pmatrix}=0\qquad(9)$$

with $\mathbf q^n=-\mathbf K(\nabla h^n+\delta c^n\mathbf e_z)$ and the dispersion of the previous step. It is solved by a chord Newton method from a split predictor (flow with the old buoyancy, then salt with those fluxes):

$$J\,\delta y^{(i)}=-R_n(y^{(i)}),\quad y^{(i+1)}=y^{(i)}+\delta y^{(i)},\quad J=\frac{\partial R_n}{\partial y^n}\ \text{refactored if}\ \|\delta c^{(i)}\|>\frac{1}{2}\|\delta c^{(i-1)}\|,\quad \text{stop: }\|\delta c\|_\infty<10^{-10},\ \|\delta h\|_\infty<10^{-8}\qquad(10)$$

The discrete adjoint of the converged scheme gives the gradient of any goal $\mathcal J$ with one backward sweep:

$$J_n^{\top}\lambda_n=g_n-B_{n+1}^{\top}\lambda_{n+1},\quad \lambda_{N+1}=0,\qquad \frac{d\mathcal J}{dp}=-\sum_n\lambda_n^{\top}\frac{\partial R_n}{\partial p},\qquad J_n=\frac{\partial R_n}{\partial y^n},\ B_{n+1}=\frac{\partial R_{n+1}}{\partial y^n},\ g_n=\left(\frac{\partial\mathcal J}{\partial y^n}\right)^{\top}\qquad(11)$$

## 3. The decision layer

$$\max_{d}\ \min_{\xi\in\Xi}\ \mathbb E_\omega\left[\sum_{t=1}^{T}\beta^t\left(\overline{Q}(1+u_t)\Delta t-\lambda_D N_c\Delta t\,\mathbf{1}\{J_t>\varepsilon_{\mathrm{lim}}\}-c_s n_t\right)\right],\qquad d=(x_s,u_{\mathrm{dec}},u_{\mathrm{cut}},B,H_{\max})\qquad(12)$$

$$\frac1T\sum_t\mathbb P_\xi(J_t>\varepsilon_{\mathrm{lim}})\le\varepsilon\ \ \forall\xi,\qquad m=q_{1-\alpha}+\overline{\delta}\max\{0,\ell\}\qquad(13\mathrm{a})$$

$$u_{t+1}=u_{\mathrm{cut}}A_t+u_{\mathrm{dec}}(1-A_t),\quad A_t=\mathbf{1}\{\hat Y_t-b_t\le y_\ell+m\},\qquad H_t=\overline{H}\min(h_{\xi,t},H_{\max})\ \text{in a declared drought}\qquad(13\mathrm{b})$$

$$n_t=\mathbf{1}\{t\ \text{ends a year}\}+\mathbf{1}\{F_t\},\qquad b_t=\frac{1}{K_t}\sum_{j=1}^{K_t}e_{(j)},\qquad K_t^2(K_t+1)=\frac{2\sigma^2}{(\rho_t\Delta)^2}\ \ (K_t=1\ \text{if}\ \rho_t\Delta\ge\sigma)\qquad(14)$$

Here $\hat Y_t$ is the SPIRANCA-GO prediction of $Y_t=-\log_{10}J_t$ from the piezometer heads and the anchors (rainfall $r$, pumping $p$), $y_\ell=-\log_{10}\varepsilon_{\mathrm{lim}}$, $F_t$ the ROJA-GO detectors (gauge outside the record, jump of the head residuals) and $e_{(j)}$ the errors at the last chloride samples. The objective note gives the meaning of each term.

## 4. Coupling diagram and flowchart

Figure 1 (next page) shows how the blocks exchange their variables within one step and how the decision layer closes the loop from one step to the next. Figure 2 (the page after) is the flowchart of the whole computation; Section 5 lists the same steps with their equations and cost.

```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

![Figure 1. The assembled system: one coupled block per step (left to centre), and the decision layer that closes the loop (right); the decision returns as a source of the next step.](/home/user/swi-goal-oed/experiments/spiranca_go/res/figA1_coupling.png){width=25.5cm}

![Figure 2. Flowchart of the solution: preparation (left), decision search (middle) and one season with the Newton solve and the decision layer (right).](/home/user/swi-goal-oed/experiments/spiranca_go/res/figA2_flowchart.png){width=24.5cm}

## 5. The solution algorithm, step by step

Algorithm 1. Steps, equations and cost on the 39 × 20 goal-graded mesh (780 cells, 1,560 unknowns per step).

| Step | Operation | Equations | Cost |
|---|---|---|---|
| 1 | Grid and parameters $\theta$; candidate set of decisions | — | — |
| 2 | Steady pre-development state: Newton on $R(y^0)=0$, tol $10^{-11}$ | (1)–(6) steady | 0.8 s |
| 3 | Spin-up: 100 years (200 steps) of private abstraction | (9)–(10) | 4 s |
| 4 | Record: 80 years, heads at six piezometers, anchors, chloride | (9)–(10), (8) | 5 s |
| 5 | Fit the decision layer: anchor regression (seasons 61–130), conformal margin + certificate (131–160), detector thresholds | (13), (14) | < 1 s |
| 6 | For each candidate $d$, storyline $\xi$ and weather $\omega$, for $t=1,\dots,60$: sources (6) → predictor → chord Newton (10) → update states, ions, $J_t$ → alarm and watch → decide $u_{t+1}$ | (6), (9)–(10), (8), (13)–(14) | 30 ms per season; 6.4 Newton iterations on average (13 at most) |
| 7 | Score each storyline; check the constraint; evaluate the objective; keep the best $d$ | (12)–(13) | — |
| 8 | Next candidate: grid over $(u_{\mathrm{dec}},u_{\mathrm{cut}},B,H_{\max})$; well site $x_s$ by the adjoint gradient | (11) | one backward sweep per storyline |
| 9 | Output the chosen decision $d_{\mathrm{opt}}$ with its margin and sampling plan | — | — |

**Remark (the closed loop costs no extra Newton work).** The decision $u_{t+1}$ depends only on what is known at the end of season $t$, so it enters the next step as a known source $W^{t+1}$ in (6). The Jacobian $J$ of (10) is the same as in an open-loop run, and the decision layer adds only the evaluation of a linear predictor and two detectors per season. A candidate decision costs 5 storylines × 6 weather sequences × 60 seasons × 30 ms ≈ 1 minute per aquifer.

**Innovation.** One time loop carries both the coupled physics and the decision: the alarm, the watch and the rule act between two Newton solves, and the adjoint of the same residual (9) gives the gradient of the goal with respect to the well site. The inner parts of the decision problem have closed forms: the margin (13) certifies the alarm, and the window (14) minimises the re-anchoring error. Only the constraint needs simulation, so the outer search runs over five numbers.

*Code:* experiments/montimi_go/mg_model.py (equations (1)–(11)), experiments/spiranca_go/sv_model.py, sx_run.py and sh_run.py (decision layer (12)–(14)); diagrams: experiments/spiranca_go/review61/asm_figs.py.