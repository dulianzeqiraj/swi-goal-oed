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

ILLUSTRATION = ('Figure 1 shows the effect on a one-dimensional coastal aquifer with illustrative values. With relative '
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

GROUPS = []          # filled below

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

COVER = []           # filled below
SOLVED = []
OPEN = []
STEP_INTRO = ''
STEP_LIFETIME = ''
STEP_RULE = ''
STEP_BULLETS = []
ONE_SENTENCE = ''
NOTE = ('Verification note. The references were checked in Crossref, arXiv or the official proceedings (authors, title, '
        'venue, pages) in November 2026; the institutions are those printed in the papers. Figure 1 is computed by '
        'netsota_fig.py with illustrative values, not with measurements at the sites. The note was drafted with the '
        'help of an AI assistant.')
OTHER = [
    ('C1', 'Lindley, D. V. (1956). On a measure of the information provided by an experiment. The Annals of '
           'Mathematical Statistics 27(4), 986–1005.', 'https://doi.org/10.1214/aoms/1177728069'),
    ('C2', 'Glover, R. E. (1959). The pattern of fresh-water flow in a coastal aquifer. Journal of Geophysical Research '
           '64(4), 457–459.', 'https://doi.org/10.1029/JZ064i004p00457'),
]
