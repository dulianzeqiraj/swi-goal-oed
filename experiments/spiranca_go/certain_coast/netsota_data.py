"""Content of the CERTAIN-COAST review "A monitoring network that is optimal today may not be optimal tomorrow".
Each paper was checked in Crossref, arXiv or the official proceedings (authors, year, venue, pages) and its institution
is the one printed in the paper. Equations are given in a common notation; where it differs from the paper's own, the
form is ours and the result is the paper's (said so in the entry)."""

SUBTITLE = ('State of the art 2020–2026: twenty key papers from Oxford, Caltech, UC Berkeley, MIT and Harvard, their '
            'mathematics, what they leave open, and what they mean for the monitoring network of CERTAIN-COAST')

INNOVATION = ('A network with a certified lifetime. CERTAIN-COAST designs its monitoring network not only for the coast of '
              'today but with the date until which it stays near-optimal, computed from the same coupled model that '
              'moves the saline wedge with relative sea level, pumping and earthquakes, and it re-designs the network with '
              'a rule that moves only the mobile sensors, and only when the information they would regain for the '
              'warnings is worth more than moving them.')

WHY = ('A monitoring network is designed for a question, and at the coast the answer moves. Relative sea level '
       '$R(t)=\\eta(t)-u_z(t)$ rises with the sea and with the subsidence of the coastal plain and pushes the saline wedge '
       'inland; pumping follows demand and droughts; an earthquake steps the pore pressure of each layer and can open or '
       'close leakage paths; and the sensors themselves drift, foul or fail. The boreholes stay where they were drilled. A '
       'network that was optimal on the day it was installed can therefore watch the wrong place a decade later, and '
       'nobody notices until a warning is missed.')

ILLUSTRATION = ('Figure 1 shows the effect on a one-dimensional coastal aquifer with a sharp interface [C2] and '
                'illustrative values. With relative '
                'sea level rising by 12 mm/yr, the toe of the wedge moves from {t0:.0f} m to {t20:.0f} m from the coast '
                'in 20 years and to {t40:.0f} m in 40 years. Five chloride sensors placed today by D-optimality keep '
                '{e10} of the efficiency of the best network after 10 years and {e20} after 20: their lifetime at '
                '$\\varepsilon=0.5$ is {life} years. A network designed for the whole 40-year horizon avoids this decline '
                'but starts at {r0} of today\'s optimum and stays above one half only from year {ra}; over 40 years the '
                'two average {mt} and {mr}. Only re-design keeps the network at the optimum, and re-design has a cost. '
                'This is the question the literature below answers in parts.')

PAPERS_INTRO = ('The papers were chosen for their mathematics and for what they say about a design that must change in '
                'time. For each: where to find it, what it did, its key equation, its main result, what it leaves open '
                'for a coastal multi-hazard network, and the step CERTAIN-COAST takes beyond it. Equations are written '
                'in a common notation; where it differs from the paper\'s, the form is ours and the result is the '
                'paper\'s.')


# ------------------------------------------------------------------------------------------------------------------
OXFORD_A = [
    dict(inst='Oxford (Department of Statistics)',
         cite='Foster, A., Ivanova, D. R., Malik, I. and Rainforth, T. (2021). Deep adaptive design: amortizing '
              'sequential Bayesian experimental design. Proceedings of the 38th International Conference on Machine '
              'Learning, PMLR 139, 3384–3395.',
         doi='https://proceedings.mlr.press/v139/foster21a.html', free='https://arxiv.org/abs/2103.02438',
         free_label='arXiv',
         done='A design policy, a neural network that maps the history of designs and outcomes to the next design, is '
              'trained before the experiment on a bound of the information the whole sequence gathers; during the '
              'experiment each new design costs one forward pass. Adaptivity itself becomes the object of the '
              'optimisation.',
         math=[(r'\xi_t=\pi\left(h_{t-1}\right),\qquad \mathcal{I}_T(\pi)=\mathbb{E}_{p(\theta)\,p(h_T\mid\theta,\pi)}'
                r'\left[\log p\left(h_T\mid\theta,\pi\right)-\log p\left(h_T\mid\pi\right)\right]',
                'the policy and the total expected information gain of the history $h_T$ it generates;'),
               (r'\mathcal{L}_T(\pi,L)=\mathbb{E}\left[\log\frac{p\left(h_T\mid\theta_0,\pi\right)}{\frac{1}{L+1}'
                r'\sum_{\ell=0}^{L}p\left(h_T\mid\theta_{\ell},\pi\right)}\right]\le\mathcal{I}_T(\pi)',
                'the sequential contrastive bound (sPCE) on which the policy is trained, with $L$ contrastive samples:')],
         theorem='The total information gain of a policy is the mutual information between the parameters and the whole '
                 'history, and the sPCE bound increases to it as $L\\to\\infty$.',
         gap='The model and its parameters are fixed during the experiment and the likelihood must be explicit; there is '
             'no moving system, no cost of moving a sensor and no spatial PDE.',
         beyond='CERTAIN-COAST trains the same kind of policy on the assembled system of the project, whose state moves '
                'with relative sea level, pumping and earthquakes, and lets it propose moves of the mobile sensors only; '
                'the certified lifetime and the value of the warnings decide whether a move is made.'),
    dict(inst='Oxford (Department of Statistics)',
         cite='Hedman, M., Ivanova, D. R., Guan, C. and Rainforth, T. (2025). Step-DAD: semi-amortized policy-based '
              'Bayesian experimental design. Proceedings of the 42nd International Conference on Machine Learning, '
              'PMLR 267, 22904–22923.',
         doi='https://proceedings.mlr.press/v267/hedman25a.html', free='https://arxiv.org/abs/2507.14057',
         free_label='arXiv',
         done='A policy trained before the experiment is refined during it: at chosen steps it is re-fitted to the '
              'posterior given the data gathered so far and then used for the remaining designs. This test-time '
              'refinement gave better decisions and more robustness than fully amortized design and other sequential '
              'methods.',
         math=[(r'\phi_{\tau}=\underset{\phi}{\arg\max}\ \mathcal{L}_{\tau+1:T}\left(\pi_{\phi};\ p\left(\theta\mid '
                r'h_{\tau}\right)\right)',
                'in our notation, the refinement at step $\\tau$: the bound on the information of the remaining designs, '
                'with the posterior $p(\\theta\\mid h_\\tau)$ in place of the prior:')],
         theorem='Empirical: the semi-amortized policy outperformed fully amortized policies and other sequential design '
                 'methods on the benchmarks of the paper.',
         gap='The refinement responds to new data, not to a system that changes: the parameters are static, and there is '
             'no field network with fixed boreholes or relocation costs.',
         beyond='The re-design epochs of CERTAIN-COAST, the yearly review and the review after an earthquake or a storm, '
                'are refinement steps of this kind, but they are triggered by the certified lifetime of the network and '
                'by events in the coupled model, not by the data alone.'),
    dict(inst='Oxford (Department of Statistics), with Edinburgh',
         cite='Ivanova, D. R., Foster, A., Kleinegesse, S., Gutmann, M. U. and Rainforth, T. (2021). Implicit deep '
              'adaptive design: policy-based experimental design without likelihoods. Advances in Neural Information '
              'Processing Systems 34 (NeurIPS 2021).',
         doi='https://proceedings.neurips.cc/paper/2021/file/d811406316b669ad3d370d78b51b1d2e-Paper.pdf',
         free='https://arxiv.org/abs/2111.02329', free_label='arXiv',
         done='Extends policy-based design to models that can only be simulated: a policy and a critic network are '
              'trained together on likelihood-free bounds of the total information gain, so the designs need only '
              'forward runs of a differentiable simulator, and each design is produced in milliseconds.',
         math=[(r'\mathcal{L}^{\mathrm{NCE}}_T\left(\pi,U_{\psi};L\right)=\mathbb{E}\left[\log\frac{\exp U_{\psi}'
                r'\left(h_T,\theta_0\right)}{\frac{1}{L+1}\sum_{i=0}^{L}\exp U_{\psi}\left(h_T,\theta_i\right)}\right]',
                'the InfoNCE bound with a learned critic $U_\\psi$ (an NWJ bound is used as well):')],
         theorem='Both objectives are lower bounds on the total information gain of the policy and need only simulated '
                 'pairs of parameters and histories.',
         gap='Needs a differentiable simulator or surrogate and heavy offline training; the model is stationary and the '
             'horizon fixed; no spatial network constraints, drift or sensor failure.',
         beyond='The variable-density flow and transport model of CERTAIN-COAST has no tractable likelihood; its fast copy '
                'with a certified error (T2.4) is the differentiable simulator such a policy needs, so likelihood-free '
                'policy design becomes possible for the coastal network.'),
    dict(inst='Oxford (Department of Statistics)',
         cite='Rainforth, T., Foster, A., Ivanova, D. R. and Bickford Smith, F. (2024). Modern Bayesian experimental '
              'design. Statistical Science 39(1), 100–114.',
         doi='https://doi.org/10.1214/23-STS915', free='https://arxiv.org/abs/2302.14545', free_label='arXiv',
         done='A review of how Bayesian experimental design became practical: estimators and bounds of the expected '
              'information gain, gradient-based design, and the move from static to adaptive and to amortized, '
              'policy-based design. Robustness to a misspecified model is named as a main open problem.',
         math=[(r'\mathrm{EIG}(\xi)=\mathbb{E}_{p(\theta)\,p(y\mid\theta,\xi)}\left[\log p(y\mid\theta,\xi)-\log '
                r'p(y\mid\xi)\right],\qquad \xi_t=\underset{\xi}{\arg\max}\ \mathrm{EIG}\left(\xi\mid h_{t-1}\right)',
                'the criterion and the classical greedy adaptive step, in which the posterior after $h_{t-1}$ is the '
                'prior of step $t$:')],
         theorem='A review: it orders the field along the axis static, adaptive, policy-based design.',
         gap='Generic: no spatio-temporal PDE inverse problem, no drifting parameters, no relocation costs and no '
             'multi-physics observations.',
         beyond='CERTAIN-COAST meets the misspecification the review names with the anchor-calibrated margins of the '
                'project: a design is judged by the information that survives a wrong simulator, not by its nominal '
                'information.'),
]

BERKELEY_A = [
    dict(inst='UC Berkeley (Simchowitz), with Washington',
         cite='Wagenmaker, A., Simchowitz, M. and Jamieson, K. (2021). Task-optimal exploration in linear dynamical '
              'systems. Proceedings of the 38th International Conference on Machine Learning, PMLR 139, 10641–10652.',
         doi='https://proceedings.mlr.press/v139/wagenmaker21a.html', free='https://arxiv.org/abs/2102.05214',
         free_label='arXiv',
         done='Asks what must be learned about an unknown linear dynamical system to perform a given task, derives '
              'instance- and task-dependent lower bounds, and casts exploration as a task-optimal design problem; an '
              'algorithm that re-solves this design with its current estimates is shown to be instance- and '
              'task-optimal.',
         math=[(r'\min_{\pi}\ \mathrm{tr}\left(\mathcal{H}\left(\theta_{\star}\right)\Gamma_T\left(\pi;\theta_{\star}'
                r'\right)^{-1}\right)',
                'in our notation, the task-optimal design: the information $\\Gamma_T$ gathered by the exploration '
                'policy $\\pi$, weighted by the Hessian $\\mathcal{H}$ of the task loss (A-optimality when there is no '
                'task):')],
         theorem='No method beats the task-optimal design value on an instance, and certainty-equivalent decisions with '
                 're-solved designs attain it up to constants; task-agnostic exploration can be arbitrarily worse.',
         gap='It designs inputs, not sensor sites, for time-invariant linear dynamics and one fixed task.',
         beyond='The tasks of CERTAIN-COAST are the three warnings, and their weight moves in time, the wedge for the '
                'wellfields, the water table under the port after an earthquake; the network is designed for these '
                'tasks and re-solved at each review.'),
]

HARVARD_D = [
    dict(inst='Harvard (Computer Science), with Virginia',
         cite='Mate, A., Killian, J. A., Xu, H., Perrault, A. and Tambe, M. (2020). Collapsing bandits and their '
              'application to public health interventions. Advances in Neural Information Processing Systems 33 '
              '(NeurIPS 2020).',
         doi='https://proceedings.neurips.cc/paper/2020/file/b460cf6b09878b00a3e1ad4c72344ccd-Paper.pdf',
         free='https://arxiv.org/abs/2007.04432', free_label='arXiv',
         done='Restless bandits in which each arm is a two-state Markov chain whose state is seen only when the arm is '
              'acted on, while the other arms evolve unobserved. Under a budget of actions per round it derives '
              'conditions under which Whittle-index policies are optimal and computes the indices about three orders of '
              'magnitude faster than earlier methods.',
         math=[(r'b_{t+1}=\begin{cases}P^{a}_{s_t,1}, & \text{arm acted on, state } s_t \text{ seen}\\ b_t\,P^{p}_{1,1}'
                r'+\left(1-b_t\right)P^{p}_{0,1}, & \text{arm passive}\end{cases}',
                'in our notation, the belief that an arm is in the good state collapses when it is observed and drifts '
                'otherwise;'),
               (r'W(b)=\inf\left\{m:\ Q_m(b,\text{passive})\ge Q_m(b,\text{active})\right\}',
                'the Whittle index, the subsidy that makes passivity as good as action; each round the arms with the '
                'largest indices are acted on:')],
         theorem='Indexability holds under conditions for which threshold policies are optimal, which gives fast and in '
                 'some cases closed-form indices.',
         gap='Binary states with known, stationary transitions; independent arms with no hydraulic coupling between '
             'wells; the reward is a state, not information about the saline front.',
         beyond='The visits of CERTAIN-COAST, chloride sampling and logger servicing, are such a budgeted restless problem, '
                'but the wells share one aquifer; the project ranks visits by the value of the warning they restore, '
                'computed from the coupled model, instead of by independent arm indices.'),
    dict(inst='Harvard (Computer Science)',
         cite='Wang, K., Xu, L., Taneja, A. and Tambe, M. (2023). Optimistic Whittle index policy: online learning for '
              'restless bandits. Proceedings of the AAAI Conference on Artificial Intelligence 37(8), 10131–10139.',
         doi='https://doi.org/10.1609/aaai.v37i8.26207', free='https://arxiv.org/abs/2205.15372', free_label='arXiv',
         done='The first online-learning algorithm built on the Whittle index for restless bandits whose transitions are '
              'unknown: upper confidence bounds on the transition probabilities give optimistic indices through a '
              'bilinear program, and the policy learns the dynamics while it schedules.',
         math=[(r'\mathrm{Reg}(T)=\sum_{t=1}^{T}\left(V^{\pi^{\star}}-V^{\pi_t}\right)=O\left(H\sqrt{T\log T}\right)',
                'the regret over $T$ episodes of horizon $H$:')],
         theorem='The optimistic Whittle policy has sublinear frequentist regret $O(H\\sqrt{T\\log T})$.',
         gap='Stationary finite-state transitions with episodic resets; no drift, no spatial coupling and no information '
             'objective.',
         beyond='Coastal dynamics are not stationary, so CERTAIN-COAST does not learn them from visits alone: the coupled '
                'model carries the drift of sea level, subsidence and pumping, and learning corrects only its residual, '
                'which the conformal margins certify.'),
]

HARVARD_C = [
    dict(inst='Harvard (Statistics; Computer Science)',
         cite='Zhang, K. W., Janson, L. and Murphy, S. A. (2021). Statistical inference with M-estimators on adaptively '
              'collected data. Advances in Neural Information Processing Systems 34 (NeurIPS 2021), 7460–7471.',
         doi='https://papers.nips.cc/paper/2021/hash/3d7d9461075eb7c37fbbfcad1d7042c1-Abstract.html',
         free='https://arxiv.org/abs/2104.14074', free_label='arXiv',
         done='Shows that ordinary M-estimators on data gathered by bandit algorithms do not give valid confidence '
              'intervals, and proposes adaptively weighted M-estimators, with square-root importance weights against a '
              'stabilising policy, that are uniformly asymptotically normal.',
         math=[(r'\hat{\theta}_T=\underset{\theta}{\arg\max}\ \sum_{t=1}^{T}W_t\,m_{\theta}\left(Y_t,X_t,A_t\right),'
                r'\qquad W_t=\sqrt{\frac{\pi^{\mathrm{sta}}_t\left(A_t,X_t\right)}{\pi_t\left(A_t,X_t,H_{t-1}\right)}}',
                'the weighted estimator and its weights:')],
         theorem='Adaptively weighted M-estimators are uniformly asymptotically normal under adaptive data collection, '
                 'so their confidence regions are asymptotically valid.',
         gap='Needs randomised designs with known selection probabilities, which deterministic information-maximising '
             'designs are not; no spatial structure and no nonstationarity.',
         beyond='Once a network is re-designed from its own data, the data are no longer a fixed design. CERTAIN-COAST '
                'calibrates its bands on simulated aquifers in which the same re-design rule runs, so the selection '
                'effect is inside the calibration.'),
]

BERKELEY_C = [
    dict(inst='UC Berkeley (EECS)',
         cite='Perdomo, J., Zrnic, T., Mendler-Dünner, C. and Hardt, M. (2020). Performative prediction. Proceedings of '
              'the 37th International Conference on Machine Learning, PMLR 119, 7599–7609.',
         doi='https://proceedings.mlr.press/v119/perdomo20a.html', free='https://arxiv.org/abs/2002.06673',
         free_label='arXiv',
         done='Formalises prediction when deploying a model changes the distribution of the data it is judged on, '
              'introduces performative stability and repeated risk minimisation, and gives the conditions under which '
              'retraining converges to a stable point with near-minimal loss.',
         math=[(r'\theta_{t+1}=\underset{\theta}{\arg\min}\ \mathbb{E}_{Z\sim\mathcal{D}\left(\theta_t\right)}\,\ell(Z;'
                r'\theta),\qquad \left\|\theta_t-\theta_{\mathrm{PS}}\right\|\le\left(\frac{\varepsilon\beta}{\gamma}'
                r'\right)^{t}\left\|\theta_0-\theta_{\mathrm{PS}}\right\|',
                'repeated risk minimisation and its linear convergence when the loss is $\\gamma$-strongly convex and '
                '$\\beta$-smooth and the distribution map is $\\varepsilon$-sensitive, $\\varepsilon<\\gamma/\\beta$:')],
         theorem='Retraining contracts at rate $\\varepsilon\\beta/\\gamma$ to a unique performatively stable point when '
                 '$\\varepsilon<\\gamma/\\beta$, and the condition is tight.',
         gap='The response has no memory, whereas an aquifer carries state; there is no sensing or design component.',
         beyond='The warnings of CERTAIN-COAST change the pumping and the pumping changes the aquifer, so the optimal '
                'network is a fixed point of a feedback loop; the project computes it on the assembled system with the '
                'decisions inside, so the feedback is modelled, not assumed away.'),
    dict(inst='UC Berkeley (EECS; Statistics)',
         cite='Fannjiang, C., Bates, S., Angelopoulos, A. N., Listgarten, J. and Jordan, M. I. (2022). Conformal '
              'prediction under feedback covariate shift for biomolecular design. Proceedings of the National Academy '
              'of Sciences 119(43), e2204569119.',
         doi='https://doi.org/10.1073/pnas.2204569119', free='https://arxiv.org/abs/2202.03613', free_label='arXiv',
         done='When the next test inputs are chosen by a design algorithm that has seen the training data, training and '
              'test data become dependent (feedback covariate shift); weighted conformal sets are proven valid in '
              'finite samples for any design algorithm and any model.',
         math=[(r'\mathbb{P}\left(Y_{n+1}\in C_{\alpha}\left(X_{n+1}\right)\right)\ge 1-\alpha,\qquad X_{n+1}\mid D\sim'
                r'\tilde{P}_{X;D}',
                'finite-sample coverage at the designed input, whose law $\\tilde{P}_{X;D}$ depends on the data $D$:')],
         theorem='Under feedback covariate shift the weighted conformal set covers the response at the designed point '
                 'with probability at least $1-\\alpha$.',
         gap='One design round with a known randomised design density, independent data and a scalar response; it '
             'chooses where to predict, not where to measure, and the system does not change between rounds.',
         beyond='Re-siting sensors with a model fitted to today\'s data creates the same feedback; CERTAIN-COAST carries '
                'the weighting into the anchor calibration of its margins, so the bands at newly placed sensors stay '
                'valid.'),
]

FIELD_E = [
    dict(inst='Harvard (Earth and Planetary Sciences; Computer Science; SEAS), with Washington',
         cite='Kelp, M. M., Lin, S., Kutz, J. N. and Mickley, L. J. (2022). A new approach for determining optimal '
              'placement of PM2.5 air quality sensors: case study for the contiguous United States. Environmental '
              'Research Letters 17(3), 034034.',
         doi='https://doi.org/10.1088/1748-9326/ac548f', free='https://doi.org/10.1088/1748-9326/ac548f',
         free_label='open access (journal)',
         done='Extracts the modes of 2000–2016 PM2.5 fields on time scales from one day to more than a decade by '
              'multiresolution dynamic mode decomposition and ranks sensor sites by QR column pivoting on them. 53% of '
              'the optimised sites lie west of the 100th meridian, against 32% of the present EPA network: a network '
              'sited for past variability misses the areas now reached by wildfire smoke.',
         math=[(r'\Psi_r^{\top}C^{\top}=QR,\qquad \hat{x}=\Psi_r\left(C\Psi_r\right)^{\dagger}y',
                'in standard form, QR column pivoting on the $r$ leading modes $\\Psi_r$ picks the sensor rows $C$, '
                'greedily maximising $|\\det C\\Psi_r|$, and the field is rebuilt from the readings $y$:')],
         theorem='Empirical; column pivoting is a greedy surrogate for D-optimal row selection.',
         gap='Data-driven, deterministic and retrospective: it needs long dense records, which a coastal aquifer lacks, '
             'and cannot anticipate where the saline front will be.',
         beyond='CERTAIN-COAST takes the modes from the physics instead of the past: the coupled model projects where the '
                'wedge, the land and the water table will move under relative sea-level rise, so the network can be '
                're-sited before the record shows the change.'),
    dict(inst='UC Berkeley (Environmental Science, Policy and Management; Civil and Environmental Engineering), with '
              'Berkeley Laboratory',
         cite='Meray, A. O., Sturla, S., Siddiquee, M. R., Serata, R., Uhlemann, S., Gonzalez-Raymat, H. et al. (2022). '
              'PyLEnM: a machine learning framework for long-term groundwater contamination monitoring strategies. '
              'Environmental Science & Technology 56(9), 5973–5983.',
         doi='https://doi.org/10.1021/acs.est.1c07440', free='https://escholarship.org/uc/item/45z6q6px',
         free_label='eScholarship',
         done='An open-source framework that modernises the long-term groundwater monitoring of the Savannah River Site '
              'F-Area: clustering of wells and analytes, spatial interpolation, estimation from in-situ proxies, and the '
              'choice of the smallest set of existing wells that keeps the estimation error within a tolerance.',
         math=[(r'\hat{z}(\mathbf{x})=k\left(\mathbf{x},X_S\right)^{\top}\left(K_{SS}+\sigma^2 I\right)^{-1}\mathbf{z}_S,'
                r'\qquad S^{\star}=\underset{S\subseteq\mathcal{W}}{\arg\min}\ |S|\ \ \text{s.t.}\ \ \mathrm{err}\left('
                r'\hat{z}_S\right)\le\tau',
                'in our notation, Gaussian-process interpolation from the retained wells $S$ and the reduction of the '
                'network:')],
         theorem='Algorithmic and empirical: a legacy well network can be pruned and partly replaced by in-situ sensors.',
         gap='Retrospective: it assumes the past spatial structure persists, with no forecast of a moving front and no '
             'guarantee.',
         beyond='CERTAIN-COAST keeps or drops a well by the information it will give on the wedge in the coming years, '
                'computed from the coupled model with relative sea level, not by its past record.'),
    dict(inst='UC Berkeley (Civil and Environmental Engineering; Public Health), with Washington',
         cite='Wang, Y., Marshall, J. D. and Apte, J. S. (2024). U.S. ambient air monitoring network has inadequate '
              'coverage under new PM2.5 standard. Environmental Science & Technology Letters 11(11), 1220–1226.',
         doi='https://doi.org/10.1021/acs.estlett.4c00605', free='https://doi.org/10.26434/chemrxiv-2024-9j3xl-v2',
         free_label='ChemRxiv',
         done='When the annual PM2.5 standard was tightened to 9 µg/m³ in 2024, the network designed for the old '
              'standard no longer detected many exceedances: according to the authors, about 44% of exceeding urban '
              'areas, home to some 20 million people, would go undetected, and ten priority sites would cut the '
              'population in unmonitored hotspots by 67%.',
         math=[(r'\mathrm{Cov}(S)=\frac{\#\left\{a\in\mathcal{A}_{\mathrm{exc}}:\ a\cap S\neq\emptyset\right\}}{\#'
                r'\mathcal{A}_{\mathrm{exc}}}',
                'in our notation, the share of exceeding areas $\\mathcal{A}_{\\mathrm{exc}}$ that the network $S$ '
                'captures:')],
         theorem='Empirical: a network adequate for the old goal fails the new one, and a few targeted additions recover '
                 'most of the loss.',
         gap='Air quality; a one-off audit with no sequential rule and no propagated model uncertainty.',
         beyond='The goal of a coastal network also changes, when a threshold is revised or a new asset is protected; '
                'CERTAIN-COAST computes the efficiency of the network for each warning and each threshold agreed with '
                'the end-user, so a change of goal triggers a re-design rather than a missed exceedance.'),
]

MITCALTECH_B = [
    dict(inst='Caltech (Dunbar, Schneider, Stuart); Howland also MIT',
         cite='Dunbar, O. R. A., Howland, M. F., Schneider, T. and Stuart, A. M. (2022). Ensemble-based experimental '
              'design for targeting data acquisition to inform climate models. Journal of Advances in Modeling Earth '
              'Systems 14(9), e2022MS002997.',
         doi='https://doi.org/10.1029/2022MS002997', free='https://arxiv.org/abs/2201.06998', free_label='arXiv',
         done='An ensemble-based Bayesian design algorithm, inside the calibrate–emulate–sample loop with ensemble Kalman '
              'inversion, that picks the regions and times where targeted extra data would most reduce the uncertainty '
              'of climate-model parameters. In an idealised general circulation model the most informative targets were '
              'often, but not always, near the intertropical convergence zone, and physical intuition could pick worse '
              'ones.',
         math=[(r'\theta^{(j)}_{n+1}=\theta^{(j)}_{n}+C^{\theta\mathcal{G}}_{n}\left(C^{\mathcal{G}\mathcal{G}}_{n}+\Gamma'
                r'\right)^{-1}\left(y+\eta^{(j)}_{n}-\mathcal{G}\left(\theta^{(j)}_{n}\right)\right)',
                'the ensemble Kalman update used for the calibration, in standard form;'),
               (r'd^{\star}=\underset{d}{\arg\max}\ \frac{1}{2}\log\det\left(\Gamma_{\mathrm{pr}}\Gamma_{\mathrm{post}}(d)^{-1}'
                r'\right),\qquad \Gamma_{\mathrm{post}}(d)^{-1}=\Gamma_{\mathrm{pr}}^{-1}+G_d^{\top}\Gamma_d^{-1}G_d',
                'in our notation, the information gain of a candidate region and time $d$ under the Gaussian '
                'approximation, with $G_d$ estimated from the ensemble:')],
         theorem='No formal theorem; calibrate–emulate–sample needs about $10^2$ forward runs against about $10^5$ for '
                 'traditional Bayesian calibration.',
         gap='It chooses where to obtain extra data, not where to install sensors with a cost; the model structure is '
             'assumed right; there is no sensor drift and no mix of sensor types.',
         beyond='CERTAIN-COAST runs the same loop on the coastal model: the ensemble of the assimilation gives the design '
                'sensitivities at each review, and the cost of moving a sensor and the certified lifetime of the network '
                'are added to the criterion.'),
    dict(inst='MIT (Carlone, Jadbabaie), with Pennsylvania',
         cite='Tzoumas, V., Carlone, L., Pappas, G. J. and Jadbabaie, A. (2021). LQG control and sensing co-design. IEEE '
              'Transactions on Automatic Control 66(4), 1468–1483.',
         doi='https://doi.org/10.1109/TAC.2020.2997661', free='https://arxiv.org/abs/1802.08376', free_label='arXiv',
         done='Chooses, at every time step, the sensors of a linear time-varying system together with its controller: the '
              'best control performance under a sensing budget, or the cheapest sensing that meets a performance bound. '
              'A separation principle partly decouples sensing, estimation and control; no polynomial algorithm '
              'guarantees a constant factor on every instance, yet polynomial algorithms with per-instance guarantees '
              'follow from approximate supermodularity.',
         math=[(r'x_{t+1}=A_t x_t+B_t u_t+w_t,\qquad y_t=C_t\left(\mathcal{S}_t\right)x_t+v_t\left(\mathcal{S}_t\right)',
                'the system observed by the sensor set $\\mathcal{S}_t$ active at step $t$;'),
               (r'\mathcal{S}^{\star}_{1:T}\in\underset{\mathcal{S}_{1:T}}{\arg\min}\ \sum_{t=1}^{T}\mathrm{tr}\left['
                r'\Theta_t\,\Sigma_{t\mid t}\left(\mathcal{S}_{1:t}\right)\right]',
                'in our notation, the separated sensing problem: the Kalman error covariance $\\Sigma_{t\\mid t}$ weighted '
                'by $\\Theta_t$, a weight that comes from the control task:')],
         theorem='Per-instance approximation guarantees for polynomial-time co-design through approximate '
                 'supermodularity; no polynomial algorithm guarantees a constant factor on every instance.',
         gap='Linear-Gaussian with known matrices; switching sensors on and off is free; no density-driven intrusion, no '
             'structural change after an earthquake and no sensor drift.',
         beyond='The weight $\\Theta_t$ is the point: sensors are chosen for the decision, not for the state. CERTAIN-COAST '
                'uses the value of the warnings as that weight, lets it move in time, and replaces free switching by the '
                'real cost of moving a sensor.'),
    dict(inst='MIT (Mechanical Engineering)',
         cite='Blanchard, A. and Sapsis, T. (2022). Informative path planning for anomaly detection in environment '
              'exploration and monitoring. Ocean Engineering 243, 110242.',
         doi='https://doi.org/10.1016/j.oceaneng.2021.110242', free='https://arxiv.org/abs/2005.10040', free_label='arXiv',
         done='Plans the path of a vehicle that searches for strong anomalies, with acquisition functions built on an '
              'output-weighted, probabilistic definition of an anomaly. Tested on seafloor bathymetry from real data and '
              'on moving anomalies, it works even when the prior belief about where the anomalies are is wrong.',
         math=[(r'w(\mathbf{x})=\frac{p_{\mathbf{x}}(\mathbf{x})}{p_{\mu}\left(\mu(\mathbf{x})\right)},\qquad a(\mathbf{x})'
                r'=\frac{1}{\sigma^2(\mathbf{x})}\int\mathrm{cov}\left(\mathbf{x},\mathbf{x}^{\prime}\right)^2w\left('
                r'\mathbf{x}^{\prime}\right)d\mathbf{x}^{\prime}',
                'the likelihood ratio, large where the predicted output is rare or extreme, and the likelihood-weighted '
                'integrated variance reduction that uses it:')],
         theorem='No formal theorem; the output weighting rests on the result that, for a known output variance, the usual '
                 'variance and information criteria ignore the observed outputs [C4].',
         gap='One mobile sensor and a two-dimensional surrogate without physics or guarantees; fixed wells, multi-modal '
             'data and drift are not treated.',
         beyond='A moving saline front is a moving anomaly. CERTAIN-COAST weights the information of a sensor by how close '
                'its reading comes to a warning threshold, takes the anomaly from the coupled model, and keeps fixed wells '
                'and mobile sensors in one design.'),
    dict(inst='Caltech (Electrical Engineering)',
         cite='Guo, N. and Kostina, V. (2021). Optimal causal rate-constrained sampling for a class of continuous Markov '
              'processes. IEEE Transactions on Information Theory 67(12), 7876–7890.',
         doi='https://doi.org/10.1109/TIT.2021.3114142', free='https://arxiv.org/abs/2002.01581', free_label='arXiv',
         done='Finds the causal policies that sample, encode and decode a continuous Markov process so as to minimise the '
              'real-time mean-square error under a limit in bits per second: the optimal encoder sends one bit when the '
              'innovation crosses one of two thresholds, and the distortion-rate function of the Ornstein–Uhlenbeck '
              'process is computed.',
         math=[(r'\min\ \limsup_{T\to\infty}\frac{1}{T}\,\mathbb{E}\int_0^T\left(X_t-\hat{X}_t\right)^2dt\ \ \text{s.t. '
                r'rate}\le R,\qquad \tau_{i+1}=\inf\left\{t>\tau_i:\ X_t-\hat{X}_t\notin\left(a_-,a_+\right)\right\}',
                'in our notation, the tracking objective under a rate limit and the optimal event-triggered sampling '
                'times:')],
         theorem='For the class of continuous Markov processes considered, which includes the Ornstein–Uhlenbeck process, '
                 'the two-threshold, one-bit causal code is optimal.',
         gap='One scalar process with a known Markov model; no spatial placement, no fusion of sensors, no model change.',
         beyond='It proves that a logger should report when the process departs from its prediction. CERTAIN-COAST applies '
                'the principle to its loggers and to the manual samples between which chloride can cross the limit, with '
                'the threshold set by the warning rather than by a mean-square error.'),
]

MITCALTECH_C = [
    dict(inst='MIT (Aeronautics and Astronautics)',
         cite='Jagalur-Mohan, J. and Marzouk, Y. (2021). Batch greedy maximization of non-submodular functions: '
              'guarantees and applications to experimental design. Journal of Machine Learning Research 22(252), 1–62.',
         doi='https://jmlr.org/papers/v22/20-1023.html', free='https://arxiv.org/abs/2006.04554', free_label='arXiv',
         done='Analyses batch greedy heuristics (standard, distributed and stochastic) for maximising non-decreasing set '
              'functions that are not submodular, with guarantees through submodularity and supermodularity ratios; for '
              'Bayesian design in linear inverse problems it bounds these ratios for the mutual information and applies '
              'the result to sensor placement for climate models.',
         math=[(r'f(\mathcal{S})=I\left(x;y_{\mathcal{S}}\right)=\frac{1}{2}\log\det\left(G_{\mathcal{S}}\Gamma_{\mathrm{pr}}'
                r'G_{\mathcal{S}}^{\top}+\Gamma_{\varepsilon,\mathcal{S}}\right)-\frac{1}{2}\log\det\Gamma_{\varepsilon,'
                r'\mathcal{S}}',
                'the mutual information of a sensor set $\\mathcal{S}$ in a linear-Gaussian model, in standard form;'),
               (r'\gamma=\min_{L,S:\ L\cap S=\emptyset}\ \frac{\sum_{j\in S}\left[f\left(L\cup\{j\}\right)-f(L)\right]}'
                r'{f\left(L\cup S\right)-f(L)}',
                'the submodularity ratio on which the guarantees rest (a supermodularity ratio is used with it):')],
         theorem='Approximation guarantees for batch greedy selection in terms of the submodularity and supermodularity '
                 'ratios, and bounds on these ratios for the mutual information in linear Bayesian inverse problems.',
         gap='A static, one-shot, linear-Gaussian design: no dynamics, model error, drift, costs per sensor type or '
             'nonlinear intrusion physics.',
         beyond='Correlated errors, such as the barometric interference of the loggers on one hub, make the information '
                'non-submodular; CERTAIN-COAST uses these guarantees for the greedy re-selection at each review, after the '
                'correctable interference has been removed.'),
    dict(inst='MIT (Jadbabaie), with Pennsylvania',
         cite='Tzoumas, V., Jadbabaie, A. and Pappas, G. J. (2022). Robust and adaptive sequential submodular '
              'optimization. IEEE Transactions on Automatic Control 67(1), 89–104.',
         doi='https://doi.org/10.1109/TAC.2020.3046222', free='https://arxiv.org/abs/1909.11783', free_label='arXiv',
         done='Defines robust sequential submodular maximisation: at each step a designer selects elements such as '
              'sensors, failures or attacks remove some, and both adapt to what they have seen. The RAM algorithm, the '
              'first scalable one for the problem, runs online, adapts to the history of failures and was near-optimal '
              'against failures from worst-case to random.',
         math=[(r'\max_{\mathcal{A}_1}\min_{\mathcal{B}_1\subseteq\mathcal{A}_1}\cdots\max_{\mathcal{A}_T}\min_{\mathcal{B}'
                r'_T\subseteq\mathcal{A}_T}f\left(\mathcal{A}_1\setminus\mathcal{B}_1,\dots,\mathcal{A}_T\setminus'
                r'\mathcal{B}_T\right),\quad\left|\mathcal{A}_t\right|\le\alpha_t,\ \left|\mathcal{B}_t\right|\le\beta_t',
                'in our notation, the alternating game of selections $\\mathcal{A}_t$ and failures $\\mathcal{B}_t$;'),
               (r'\kappa_f=1-\min_{v\in\mathcal{V}}\frac{f(\mathcal{V})-f\left(\mathcal{V}\setminus\{v\}\right)}'
                r'{f\left(\{v\}\right)}',
                'the total curvature on which the a priori bounds depend:')],
         theorem='Polynomial running time, a priori suboptimality bounds for any number of failures among the selected '
                 'elements, and tight a posteriori bounds.',
         gap='Failures are discrete removals, not gradual drift or bias; the objective must be known and near-submodular; '
             'no physics, model change or installation cost.',
         beyond='A coastal network loses loggers to fouling, floods and earthquakes. CERTAIN-COAST treats a failed sensor '
                'as a removal in the same game and re-selects among the mobile sensors with the failure history, while '
                'the correctable drift is removed by reference channels instead of abandoning the sensor.'),
    dict(inst='Caltech (Owhadi, Computing and Mathematical Sciences), with co-authors at other universities',
         cite='Huan, S., Guinness, J., Katzfuss, M., Owhadi, H. and Schäfer, F. (2025). Sparse inverse Cholesky '
              'factorization of dense kernel matrices by greedy conditional selection. SIAM/ASA Journal on Uncertainty '
              'Quantification 13(3), 1649–1679.',
         doi='https://doi.org/10.1137/23M1606253', free='https://arxiv.org/abs/2307.11648', free_label='arXiv',
         done='Builds sparse inverse-Cholesky factors of kernel matrices by greedy selection instead of nearest '
              'neighbours: each step adds the point with the most mutual information about the target points given the '
              'points already chosen. Fast partial-Cholesky algorithms make the selection cheap, and it improves on '
              'nearest-neighbour selection in Gaussian-process regression and preconditioning.',
         math=[(r'k_{i+1}=\underset{k\notin I}{\arg\max}\ \frac{\mathrm{Var}\left[y_k\mid y_I\right]}{\mathrm{Var}\left['
                r'y_k\mid y_I,y_{\mathrm{Pr}}\right]}\iff\underset{k\notin I}{\arg\max}\ I\left(y_k;y_{\mathrm{Pr}}\mid '
                r'y_I\right)',
                'in our notation, greedy conditional selection of the next point $k$ given the selected set $I$ and the '
                'targets $\\mathrm{Pr}$:')],
         theorem='Choosing $k$ of $N$ points costs $O(Nk^2)$ instead of the naive $O(Nk^4)$, and $O(Nk^2+Nm^2+m^3)$ for $m$ '
                 'targets.',
         gap='A fixed, stationary kernel with no dynamics or PDE; fixed targets; drift or model change means refitting '
             'the kernel; no installation costs.',
         beyond='The targets of CERTAIN-COAST move: the toe of the wedge, the supply wells, the water table under the port. '
                'The selection is cheap enough to be repeated at every review with the targets and the covariance taken '
                'from the coupled model of that year.'),
]

GROUPS = [
    ('A. Re-designing as data arrive: sequential and policy-based design', OXFORD_A + BERKELEY_A),
    ('B. Designs for evolving fields: targeting, sensor scheduling and event-triggered sampling', MITCALTECH_B),
    ('C. Guarantees for greedy re-selection, failures and moving targets', MITCALTECH_C),
    ('D. When the world drifts or reacts: valid learning and inference after re-design', BERKELEY_C + HARVARD_C),
    ('E. Monitoring what cannot be watched everywhere: restless bandits', HARVARD_D),
    ('F. Real networks that went out of date', FIELD_E),
]
_n = 0
for _, _items in GROUPS:
    for _it in _items:
        _n += 1
        _it['n'] = _n

COVER = [
    ['[1] Deep adaptive design (Oxford)', '✓', '–', '~', '✓', '–'],
    ['[2] Step-DAD (Oxford)', '✓', '~', '~', '–', '–'],
    ['[3] Implicit deep adaptive design (Oxford)', '✓', '–', '~', '✓', '–'],
    ['[4] Modern Bayesian design, review (Oxford)', '✓', '~', '–', '–', '–'],
    ['[5] Task-optimal exploration (Berkeley)', '✓', '–', '✓', '✓', '–'],
    ['[6] Ensemble-based targeting (Caltech)', '✓', '–', '~', '–', '~'],
    ['[7] LQG control and sensing co-design (MIT)', '✓', '–', '✓', '✓', '–'],
    ['[8] Path planning for anomalies (MIT)', '✓', '~', '✓', '–', '~'],
    ['[9] Event-triggered sampling (Caltech)', '✓', '–', '–', '✓', '–'],
    ['[10] Batch greedy, non-submodular (MIT)', '–', '–', '~', '✓', '~'],
    ['[11] Robust adaptive submodular (MIT)', '✓', '~', '–', '✓', '–'],
    ['[12] Greedy conditional selection (Caltech)', '–', '–', '✓', '✓', '–'],
    ['[13] Performative prediction (Berkeley)', '✓', '✓', '–', '✓', '–'],
    ['[14] Feedback covariate shift (Berkeley)', '~', '✓', '–', '✓', '–'],
    ['[15] Inference on adaptive data (Harvard)', '–', '~', '–', '✓', '–'],
    ['[16] Collapsing bandits (Harvard)', '✓', '–', '–', '✓', '–'],
    ['[17] Optimistic Whittle index (Harvard)', '✓', '~', '–', '✓', '–'],
    ['[18] PM2.5 sensor placement (Harvard)', '~', '✓', '–', '–', '✓'],
    ['[19] Groundwater monitoring, PyLEnM (Berkeley)', '~', '–', '–', '–', '✓'],
    ['[20] PM2.5 network under a new standard (Berkeley)', '~', '✓', '✓', '–', '✓'],
    ['**CERTAIN-COAST (proposed)**', '**✓**', '**✓**', '**✓**', '**✓ lifetime**', '**✓**'],
]

SOLVED = [
    'Adaptive design is practical: policies trained before the experiment choose each new design in milliseconds and '
    'can be refined as data arrive [1–4], and re-solving a task-weighted design with the current model is provably '
    'optimal for learning a linear system [5].',
    'Sensing can be scheduled in time for a decision rather than for the state, with per-instance guarantees [7]; data '
    'can be targeted in space and time with the ensembles of a large model [6]; sampling can be weighted toward rare '
    'and dangerous outputs and follow moving anomalies [8]; event-triggered reporting is optimal for tracking a '
    'Markov process under a reporting budget [9]; and operational ocean forecasting already recomputes its sampling '
    'plan from every new forecast [C3].',
    'Greedy re-selection has guarantees beyond submodularity [10], survives adaptive failures [11] and is cheap enough '
    'to repeat when the targets move [12].',
    'Guarantees survive feedback: retraining converges when predictions change the world [13], conformal sets stay '
    'valid when the design depends on the data [14], and estimates stay valid on adaptively collected data [15].',
    'Monitoring under a budget of visits is a restless bandit with fast indices [16] that can be learned online [17]; '
    'and three field studies show that real networks go out of date when the system or the goal changes [18–20].',
]

OPEN = [
    'No study gives the date at which a fixed network stops being near-optimal for a hazard that moves with relative '
    'sea level: the lifetime of a network is not a quantity of the literature.',
    'Adaptive designs move every sensor freely [1–3, 6–9]; real networks have fixed boreholes and a few mobile sensors, '
    'and the cost of moving them is not in the criteria [1–17].',
    'The system itself changes, but the parameters are static in the policy-based methods [1–4], the dynamics are '
    'time-invariant in the guarantees [5, 7, 13], and the bandit models are stationary [16, 17].',
    'The goals are single and fixed; a network that serves three warnings whose weights move in time, the wedge at the '
    'wellfields, the water table under the port after an earthquake, the extreme sea level, is not treated.',
    'The field re-designs are retrospective [18–20]: they find the gap after the record shows it.',
]

STEP_INTRO = ('CERTAIN-COAST combines what the literature solves separately into one rule for a real network. First, '
              'the lifetime of the network is certified rather than guessed: the efficiency of the installed network is '
              'bounded from below along an ensemble of futures of relative sea level, pumping and earthquakes generated '
              'by the coupled model and calibrated as the warnings are, and the certified lifetime is the first time '
              'that lower bound falls below $1-\\varepsilon$:')
STEP_LIFETIME = ('Here $\\underline{e}_t(\\xi)$ is the lower confidence bound of the efficiency at time $t$ and $\\delta$ '
                 'the tolerated probability of overstating the lifetime. A design is accepted only if its certified '
                 'lifetime reaches the next scheduled review, and the network design report states it.')
STEP_RULE = ('Second, the network is re-designed at each yearly review and after each strong earthquake or storm, but '
             'only where it pays. The boreholes stay; the mobile sensors (loggers, seismic nodes, fibre segments) can be '
             'moved or added among the positions $\\Xi(\\xi_k)$ reachable from the present network, and the move from '
             '$\\xi_k$ is made when the value of information until the next review, $V_t$, the expected avoided loss of '
             'the warnings in the cost-loss metric of the proposal, exceeds the cost $c$ of moving:')
STEP_BULLETS = [
    'The design keeps the goal of the warnings: $V_t$ is computed for the three alarms together, so a sensor that '
    'serves the port after an earthquake can outrank one that served the wellfield before it; the weights move in time '
    'as the weight $\\Theta_t$ does in sensing–control co-design [7].',
    'The policy is learned once and applied at every review: an amortized design policy [1, 3], refined at each review '
    'as in [2] and trained on the assembled system of the project, proposes the moves, and the rule above, with the '
    'certified lifetime, decides them. This is the pattern of the deep reinforcement learning agent and its shield in '
    'the decision part of the proposal.',
    'Failures and drift are part of the design: a lost logger is a removal in the robust sequential game [11], and the '
    'correctable drift is removed by barometers and sealed reference channels, which stay design candidates at every '
    're-design.',
    'The guarantees survive the re-design: the bands at newly placed sensors are calibrated with the feedback weighting '
    'of [14], on simulated aquifers in which the same re-design rule runs [15].',
    'Each earthquake is also a free experiment: the pore-pressure step and its relaxation identify the leakage of each '
    'layer, and the re-design after the event uses that information at once.',
]
ONE_SENTENCE = ('The literature knows how to design a network that is optimal at one time, how to adapt a design as data '
                'arrive, and how to keep guarantees when distributions shift; CERTAIN-COAST adds the date until which a '
                'real, fixed coastal network stays near-optimal, certified from the physics that moves the hazards, and a '
                'rule that moves only what pays to move.')
NOTE = ('Verification note. The references were checked in Crossref, arXiv or the official proceedings (authors, title, '
        'venue, pages) in November 2026; the institutions are those printed in the papers. Figure 1 is computed by '
        'netsota_fig.py with illustrative values, not with measurements at the sites. The note was drafted with the '
        'help of an AI assistant.')
OTHER = [
    ('C1', 'Lindley, D. V. (1956). On a measure of the information provided by an experiment. The Annals of '
           'Mathematical Statistics 27(4), 986–1005.', 'https://doi.org/10.1214/aoms/1177728069'),
    ('C2', 'Glover, R. E. (1959). The pattern of fresh-water flow in a coastal aquifer. Journal of Geophysical Research '
           '64(4), 457–459.', 'https://doi.org/10.1029/JZ064i004p00457'),
    ('C3', 'Lermusiaux, P. F. J., Haley, P. J., Mirabito, C., Mule, E. M., DiMarco, S. F., Dancer, A. et al. (2024). '
           'Real-time ocean probabilistic forecasts, reachability analysis, and adaptive sampling in the Gulf of Mexico. '
           'OCEANS 2024 – Halifax, 1–10.', 'https://doi.org/10.1109/OCEANS55160.2024.10754153'),
    ('C4', 'Sapsis, T. P. (2020). Output-weighted optimal sampling for Bayesian regression and rare event statistics '
           'using few samples. Proceedings of the Royal Society A 476(2234), 20190834.',
     'https://doi.org/10.1098/rspa.2019.0834'),
]
