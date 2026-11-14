"""The innovation of the author's review of dynamic data assimilation for missing dynamics (section 4 of
"Asimilimi dinamik i të dhënave për dinamikën që mungon", 8 October 2026): three mathematical proposals N1-N3,
translated, with their equations; and how the MATLAB code of CERTAIN-COAST already carries part of N1 and N3.
Reference numbers [1]-[20] are those of the review, which are also the numbers of its cards in Section 1 of the
complete state of the art (the review's twenty papers open the document in the review's order)."""

TITLE = 'What is new: three mathematical proposals for data assimilation with missing dynamics'

INTRO = ('The three proposals below join results of the twenty papers in a way none of them does. They come from the '
         'author\'s review; the search behind them was not systematic, so they are stated as proposals: N1 ends in an '
         'open question, N2 in a conjecture, and N3 in a claim whose elementary proof is given. Their equations are new '
         'in this work and are set in red.')

# (title, text before the equation, LaTeX of the equation, text after the equation)
PROPOSALS = [
    ('N1. Markovian lifting of the memory inside the ensemble Kalman filter',
     '[3] shows that when the memory kernel is a sum of exponentials, the model with memory is exactly Markovian with '
     'internal variables. [1] proves that such lifts exist on a finite horizon (Theorems 5.4 and 5.6), but notes that '
     'the hidden variables must be initialised by assimilation (Remark 5.8). The proposal: the internal variables $r$ '
     'become part of the filtered state, and the realisation $(A,B,C)$ is estimated together with $\\theta$ by [8] or [9]:',
     r'\dot v=f_0(v)+m(v;\theta)+C\,r,\qquad \dot r=-A\,r+B\,v,\quad r(0)=0\quad\Longrightarrow\quad '
     r'C\,r(t)=\int_0^t K(t-s)\,v(s)\,ds,\qquad K(\tau)=C\,e^{-A\tau}B',
     'The equivalence follows from the variation-of-constants formula. The obstacle is identifiability: the same kernel '
     '$K$ is given by $(TAT^{-1},TB,CT^{-1})$ for every invertible $T$. It is removed by fixing '
     '$A=\\mathrm{diag}(\\alpha_1<\\dots<\\alpha_L)$, as in the form of [3], and normalising $B$: with distinct '
     'diagonal values, every $T$ that leaves $A$ unchanged is itself diagonal, so only a scaling remains. The open '
     'question: if the filter is exponentially stable, is its error bounded by the error $\\delta_L$ of the kernel with '
     '$L$ exponentials, uniformly in time? A positive answer would turn the finite-horizon existence result of [1] into '
     'a guarantee for all times.'),
    ('N2. Splitting the error: non-Gaussianity against the closure',
     'Let $\\mu_J$ be the true filter with the exact model, $\\mu_J^{K}$ the mean-field ensemble Kalman filter with '
     'the exact model and $\\mu_J^{K,\\hat\\theta}$ the same filter with the learned closure $m(\\cdot;\\hat\\theta)$. '
     'Since $d_g$ is a metric,',
     [r'd_g\big(\mu_J,\mu_J^{K,\hat\theta}\big)\le d_g\big(\mu_J,\mu_J^{K}\big)+d_g\big(\mu_J^{K},\mu_J^{K,\hat\theta}\big)',
      r'\le C_1\max_{0\le j\le J-1}d_g\big(\mathcal{Q}\mathcal{P}\mu_j,\,G\,\mathcal{Q}\mathcal{P}\mu_j\big)'
      r'+C_2\,\big\|m^{\dagger}-m(\cdot;\hat\theta)\big\|_{\infty}'],
     'The first inequality is the triangle inequality; the first term after it is bounded by Theorem 4 of [7] (under '
     'its Assumption H, near the Gaussian regime). The bound $C_2\\|m^{\\dagger}-m(\\cdot;\\hat\\theta)\\|_{\\infty}$ '
     'on the second term is a conjecture: it needs the stability of the mean-field map to perturbations of the forward '
     'model, with a norm weighted by $g(v)=1+|v|^2$. If it holds, the two sources of error separate: the first is '
     'estimated from the forecast ensemble, for example by the gap of the objective $\\mathcal{J}_k$ of [11] between the '
     'nonlinear and the affine map, the second by the validation error of the closure. The effort then goes where the '
     'error is: a transport filter [10]–[12] when the first term dominates, a better closure [1]–[5] when the second '
     'does.'),
    ('N3. Robust filtering calibrated by the posterior of the closure',
     '[8] gives, in the linear case, a Gaussian posterior $N(m_\\theta,C_\\theta)$ for the closure parameters, and an '
     'approximation of it in the nonlinear case. The proposal is to use it as the penalty of the nonlinear expectation of '
     '[18], with $\\alpha(\\theta)=\\tfrac12\\|\\theta-m_\\theta\\|^2_{C_\\theta^{-1}}$. As $k\'\\to\\infty$ the penalty '
     '$(\\alpha/k)^{k\'}$ tends to zero inside the ellipsoid $\\Theta_k=\\{\\alpha\\le k\\}$ and to infinity outside it, '
     'so in the limit the expectation is coherent:',
     r'\mathcal{E}_k\big(\varphi\mid\mathcal{Y}_t\big)=\sup_{\theta\in\Theta_k}E^{\theta}\big[\varphi\mid\mathcal{Y}_t\big],'
     r'\qquad \Theta_k=\Big\{\theta:\ \tfrac12\|\theta-m_\theta\|^2_{C_\theta^{-1}}\le k\Big\},\qquad '
     r'\theta^{\dagger}\in\Theta_k\ \Rightarrow\ -\mathcal{E}_k\big(-\varphi\mid\mathcal{Y}_t\big)\le '
     r'E^{\theta^{\dagger}}\big[\varphi\mid\mathcal{Y}_t\big]\le\mathcal{E}_k\big(\varphi\mid\mathcal{Y}_t\big)',
     'Proof of the claim: a supremum over a set that contains $\\theta^{\\dagger}$ is at least the value at '
     '$\\theta^{\\dagger}$, and likewise the infimum. If $2k$ is the $1-a$ quantile of $\\chi^2_p$, the ellipsoid is the '
     '$1-a$ credible region of the Gaussian posterior, so the band holds the true conditional expectation with posterior '
     'probability at least $1-a$ (exactly so for a linear forward map, where the posterior of [8] is exact). A Bayesian '
     'calibration of the closure is thus tied to a band that holds for every closure the data cannot exclude; the '
     'supremum is computed with a bank of filters over $\\Theta_k$, or through the Hamilton–Jacobi–Bellman problem of '
     '[17] in the Kalman–Bucy case.'),
]

IN_CC = ('These proposals are the data assimilation innovation of WP2, and the MATLAB code already '
         'carries their skeleton. The exterior of the aquifer is a sum of exponentials with fixed rates: the boundary '
         'flux $q=Cu+\\sum_m w_m(u-y_m)$ with compartment heads $\\dot y_m=\\mu_m(u-y_m)$ (exactExterior.m) is the '
         'lift of N1 with $A=\\mathrm{diag}(\\mu_m)$, and identifyFromPiezometers.m fixes twelve geometric rates and '
         'learns only $C\\ge0$ and $w_m\\ge0$, which is the normalisation that removes the unidentifiable orbit; WP2 moves '
         'the compartment heads into the filtered state. The warning band of crossingBand.m is a band of the form of '
         'N3: the smallest and largest crossing probability over every time scale the record cannot exclude (Section '
         '6.0). N2 decides, site by site, whether the next effort goes to the filter or to the closure of the coastal '
         'model.')

SHORT = ('Three proposals for data assimilation with missing dynamics: N1 puts a Markovian lift of the memory (a sum of '
         'exponentials with fixed rates, which removes the unidentifiable orbit) inside the ensemble Kalman filter; N2 '
         'splits the filtering error into a non-Gaussian part and a closure part, so that the effort goes where the '
         'error is; N3 calibrates a robust filter by the posterior of the closure, giving a band that holds for every '
         'closure the data cannot exclude. The MATLAB code already carries the lift of N1 at the boundary and a band of '
         'the form of N3 between samples.')
