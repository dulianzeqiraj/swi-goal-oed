"""Text of the tenth state-of-the-art review (English): sensor placement with interference correction. The robust
optimal design of Chowdhary, Attia & Alexanderian (2025) and the Certified OED framework extracted; the state of the
art in sensor placement for the NATO proposal; our scheme of who interferes with a CERTAIN-COAST piezometer; and
NDERHYRJA-GO. blocks(R) returns the block list; every number comes from res/nderhyrja.json.
Conventions: $inline math$, **bold**, *italic*, [text](url) hyperlink, [[key]] equation number, {{key}} figure or
table number."""
ARTICLE = 'https://arxiv.org/abs/2409.09137'


ANCHORS = [
    dict(key='A1', text='Chowdhary, A., Attia, A., & Alexanderian, A. (2025). Robust optimal experimental design of '
                        'infinite-dimensional Bayesian nonlinear inverse problems. arXiv:2409.09137v2 [math.NA], 12 August '
                        '2025; submitted to the editors 6 September 2025 (PDF provided by the user).', url=ARTICLE),
    dict(key='A2', text='Zeqiraj, D. (2026). Certified optimal experimental design for infinite-dimensional Bayesian '
                        'inverse problems: corrections, optimality certificates and two-sided information bounds. A '
                        'rigorous revisit of Alexanderian (2021). Draft of 3 October 2026 (Word file provided by the '
                        'user, Certified_OED_Zeqiraj_final.docx).', url=None),
]
# cited as A1 lists them
RA = [
    dict(key='R1', text='Alexanderian, A. (2021). Optimal experimental design for infinite-dimensional Bayesian inverse '
                        'problems governed by PDEs: a review. Inverse Problems 37, 043001.', url=None),
    dict(key='R2', text='Alexanderian, A., Gloor, P. J., & Ghattas, O. (2016). On Bayesian A- and D-optimal experimental '
                        'designs in infinite dimensions. Bayesian Analysis 11, 671–695.', url=None),
    dict(key='R3', text='Alexanderian, A., Petra, N., Stadler, G., & Sunseri, I. (2021). Optimal design of large-scale '
                        'Bayesian linear inverse problems under reducible model uncertainty: good to know what you '
                        'don\'t know. SIAM/ASA Journal on Uncertainty Quantification 9, 163–184.', url=None),
    dict(key='R4', text='Alexanderian, A., & Saibaba, A. K. (2018). Efficient D-optimal design of experiments for '
                        'infinite-dimensional Bayesian linear inverse problems. SIAM Journal on Scientific Computing 40, '
                        'A2956–A2985.', url=None),
    dict(key='R5', text='Atkinson, A. C., & Donev, A. N. (1992). Optimum Experimental Designs. Oxford.', url=None),
    dict(key='R6', text='Attia, A. (2024). Probabilistic approach to black-box binary optimization with budget '
                        'constraints: application to sensor placement. arXiv:2406.05830.', url=None),
    dict(key='R7', text='Attia, A., & Constantinescu, E. (2022). Optimal experimental design for inverse problems in the '
                        'presence of observation correlations. SIAM Journal on Scientific Computing 44, A2808–A2842.',
         url=None),
    dict(key='R8', text='Attia, A., Leyffer, S., & Munson, T. (2023). Robust A-optimal experimental design for Bayesian '
                        'inverse problems. arXiv:2305.03855.', url=None),
    dict(key='R9', text='Attia, A., Leyffer, S., & Munson, T. S. (2022). Stochastic learning approach for binary '
                        'optimization: application to Bayesian optimal design of experiments. SIAM Journal on Scientific '
                        'Computing 44, B395–B427.', url=None),
    dict(key='R10', text='Chaloner, K., & Verdinelli, I. (1995). Bayesian experimental design: a review. Statistical '
                         'Science 10.', url=None),
    dict(key='R11', text='Chowdhary, A., Ahmed, S. E., & Attia, A. (2024). PyOED: an extensible suite for data '
                         'assimilation and model-constrained optimal design of experiments. ACM Transactions on '
                         'Mathematical Software 50.', url=None),
    dict(key='R12', text='Go, J., & Isaac, T. (2022). Robust expected information gain for optimal Bayesian experimental '
                         'design using ambiguity sets. Proceedings of the 38th Conference on Uncertainty in Artificial '
                         'Intelligence, PMLR 180, 728–737.', url=None),
    dict(key='R13', text='Koval, K., Alexanderian, A., & Stadler, G. (2020). Optimal experimental design under '
                         'irreducible uncertainty for linear inverse problems governed by PDEs. Inverse Problems 36.',
         url=None),
    dict(key='R14', text='Lau, L. C., & Zhou, H. (2020). A local search framework for experimental design.', url=None),
    dict(key='R15', text='Pronzato, L., & Walter, E. (1988). Robust experiment design via maximin optimization. '
                         'Mathematical Biosciences 89, 161–176.', url=None),
    dict(key='R16', text='Rainforth, T., Foster, A., Ivanova, D. R., & Smith, F. B. (2024). Modern Bayesian experimental '
                         'design. Statistical Science 39, 100–114.', url=None),
    dict(key='R17', text='Uciński, D. (2005). Optimal Measurement Methods for Distributed Parameter System Identification. '
                         'CRC Press.', url=None),
    dict(key='R18', text='Villa, U., Petra, N., & Ghattas, O. (2021). hIPPYlib: an extensible software framework for '
                         'large-scale inverse problems governed by PDEs, Part I. ACM Transactions on Mathematical Software '
                         '47.', url=None),
    dict(key='R19', text='Wald, A. (1945). Statistical decision functions which minimize the maximum risk. Annals of '
                         'Mathematics 46, 265–280.', url=None),
    dict(key='R20', text='Wu, K., Chen, P., & Ghattas, O. (2023). A fast and scalable computational framework for '
                         'large-scale high-dimensional Bayesian optimal experimental design. SIAM/ASA Journal on '
                         'Uncertainty Quantification 11, 235–261.', url=None),
]
# cited as A2 lists them
RC = [
    dict(key='C1', text='Krause, A., Singh, A., & Guestrin, C. (2008). Near-optimal sensor placements in Gaussian '
                        'processes: theory, efficient algorithms and empirical studies. Journal of Machine Learning '
                        'Research 9, 235–284.', url='https://jmlr.org/papers/v9/krause08a.html'),
    dict(key='C2', text='Maio, S., & Alexanderian, A. (2025). On submodularity of the expected information gain. '
                        'arXiv:2505.04145.', url='https://arxiv.org/abs/2505.04145'),
    dict(key='C3', text='Chamon, L. F. O., & Ribeiro, A. (2017). Approximate supermodularity bounds for experimental '
                        'design. Advances in Neural Information Processing Systems 30, 5403–5412.', url=None),
    dict(key='C4', text='Müller, W. G., & Pázman, A. (2003). Measures for designs in experiments with correlated errors. '
                        'Biometrika 90(2), 423–434.', url='https://doi.org/10.1093/biomet/90.2.423'),
    dict(key='C5', text='Liu, S., Chepuri, S. P., Fardad, M., Maşazade, E., Leus, G., & Varshney, P. K. (2016). Sensor '
                        'selection for estimation with correlated measurement noise. IEEE Transactions on Signal '
                        'Processing 64(13), 3509–3522.', url='https://doi.org/10.1109/TSP.2016.2550005'),
    dict(key='C6', text='Uciński, D. (2020). D-optimal sensor selection in the presence of correlated measurement noise. '
                        'Measurement 164, 107873.', url='https://doi.org/10.1016/j.measurement.2020.107873'),
    dict(key='C7', text='Pázman, A., Hainy, M., & Müller, W. G. (2022). A convex approach to optimum design of '
                        'experiments with correlated observations. Electronic Journal of Statistics 16(2), 5659–5691.',
         url='https://doi.org/10.1214/22-EJS2071'),
    dict(key='C8', text='Hainy, M., Müller, W. G., & Pázman, A. (2025). Practical aspects of the virtual noise convex '
                        'optimum design approach for correlated responses. arXiv:2504.17651.',
         url='https://arxiv.org/abs/2504.17651'),
    dict(key='C9', text='Anderson, W. N., & Duffin, R. J. (1969). Series and parallel addition of matrices. Journal of '
                        'Mathematical Analysis and Applications 26(3), 576–594.',
         url='https://doi.org/10.1016/0022-247X(69)90200-5'),
    dict(key='C10', text='Maio, S., Alexanderian, A., Koval, K., & Nicholson, R. (2026). Multi-type sensor placement for '
                         'PDE-based Bayesian inverse problems. arXiv:2607.08074.', url='https://arxiv.org/abs/2607.08074'),
    dict(key='C11', text='Venkat, S., Henneking, S., & Ghattas, O. (2026). Sensor placement for tsunami early warning via '
                         'large-scale Bayesian optimal experimental design. arXiv:2604.08812.',
         url='https://arxiv.org/abs/2604.08812'),
    dict(key='C12', text='Huan, X., Jagalur, J., & Marzouk, Y. (2024). Optimal experimental design: formulations and '
                         'computations. Acta Numerica 33, 715–840.', url='https://doi.org/10.1017/S0962492924000023'),
    dict(key='C13', text='Attia, A., Alexanderian, A., & Saibaba, A. K. (2018). Goal-oriented optimal design of '
                         'experiments for large-scale Bayesian linear inverse problems. Inverse Problems 34(9), 095009.',
         url='https://doi.org/10.1088/1361-6420/aad210'),
    dict(key='C14', text='Alexanderian, A., & Maio, S. (2026). Submodularity of the expected information gain in '
                         'infinite-dimensional linear inverse problems. arXiv:2602.09285.',
         url='https://arxiv.org/abs/2602.09285'),
]
WEB = [
    dict(key='W1', text='Rasmussen, T. C., & Crawford, L. A. (1997). Identifying and removing barometric pressure effects '
                        'in confined and unconfined aquifers. Ground Water 35(3), 502–511.',
         url='https://doi.org/10.1111/j.1745-6584.1997.tb00111.x'),
    dict(key='W2', text='Toll, N. J., & Rasmussen, T. C. (2007). Removal of barometric pressure effects and earth tides '
                        'from observed water levels. Ground Water 45(1), 101–105.',
         url='https://doi.org/10.1111/j.1745-6584.2006.00254.x'),
]
OTHER = [
    dict(key='D1', text='Zeqiraj, D. (2026). Reviews I–IX of this series, docs/literature/ in this repository; the '
                        'CERTAIN-COAST application texts, docs/certain_coast/.', url=None),
    dict(key='D2', text='The code of this review: experiments/nderhyrja_go/ (nderhyrja_exp.py, nderhyrja_figs.py; '
                        'results in res/).', url=None),
]


def all_refs():
    return ANCHORS + RA + RC + WEB + OTHER


def f2(x):
    return f'{x:.2f}'


def pct(a, b):
    return f'{100 * (a - b) / b:.0f}%'


def fill_numbers(R):
    s = {}
    T34, T35 = R['t34'], R['t35']
    ks = sorted(int(k) for k in T34)
    s['ks'] = ks
    k = 12 if '12' in T34 else ks[-1]
    s['k'] = k
    e = T34[str(k)]
    for rule in e:
        s[f'w_{rule}'] = f2(e[rule]['worst'])
        s[f'n_{rule}'] = f2(e[rule]['nominal'])
        s[f'r_{rule}'] = e[rule]['nrefs']
    s['gain_indep'] = pct(e['nderhyrja']['worst'], e['indep']['worst'])
    s['gain_norefs'] = pct(e['nderhyrja']['worst'], e['nominal_norefs']['worst'])
    s['gain_rnorefs'] = pct(e['nderhyrja']['worst'], e['robust_norefs']['worst'])
    s['gain_nominal'] = pct(e['nderhyrja']['worst'], e['nominal']['worst'])
    s['naive_claim'] = f2(e['naive']['naive_claim'])
    s['naive_true'] = f2(e['naive']['nominal'])
    s['sdq_nd'] = f'{100 * e["nderhyrja"]["sdq_worst"]:.1f}'
    s['sdq_in'] = f'{100 * e["indep"]["sdq_worst"]:.1f}'
    s['ceil'] = f2(e['nderhyrja']['ceiling'])
    s['ceil_frac'] = f'{100 * e["nderhyrja"]["nominal"] / e["nderhyrja"]["ceiling"]:.0f}%'
    best_all = all(T34[str(kk)]['nderhyrja']['worst'] >= max(T34[str(kk)][r]['worst'] for r in T34[str(kk)]) - 1e-9
                   for kk in ks)
    s['best_all'] = best_all
    s['refs_by_k'] = ', '.join(f'{T34[str(kk)]["nderhyrja"]["nrefs"]} at k = {kk}' for kk in ks)
    g = [T35[str(kk)]['gap_pct'] for kk in ks]
    s['gap_lo'], s['gap_hi'] = f'{min(g):.0f}%', f'{max(g):.0f}%'
    s['gap_k'] = f'{T35[str(k)]["gap_pct"]:.0f}%'
    s['ub_k'], s['val_k'] = f2(T35[str(k)]['ub']), f2(T35[str(k)]['val'])
    s['ubp_k'], s['ubc_k'] = f2(T35[str(k)]['ub_plain']), f2(T35[str(k)]['ub_ceiling'])
    sm = R['t35_small']
    s['small_n'] = sm[0]['n']
    s['small_exact'] = sum(1 for x in sm if abs(x['greedy_exchange'] - x['exhaustive']) < 1e-9)
    s['small_cnt'] = len(sm)
    worst_small = max(sm, key=lambda x: x['exhaustive'] - x['greedy_exchange'])
    s['small_worst'] = (f"{100 * (worst_small['exhaustive'] - worst_small['greedy_exchange']) / worst_small['exhaustive']:.1f}% "
                        f"at k = {worst_small['k']}")
    s['small_valid'] = all(x['ub'] >= x['exhaustive'] - 1e-9 for x in sm)
    T = R['t36']
    s['t36k'] = T['k']
    for d in ('indep', 'nominal_norefs', 'nderhyrja'):
        for m in ('ignore', 'nominal', 'robust'):
            s[f'cov_{d}_{m}'] = f'{100 * T[d][m]["coverage"]:.0f}%'
            s[f'rq_{d}_{m}'] = f'{100 * T[d][m]["rmse_q"]:.1f}'
            s[f'hr_{d}_{m}'] = f'{100 * T[d][m]["rmse_heads_raw"]:.1f}'
            s[f'hc_{d}_{m}'] = f'{100 * T[d][m]["rmse_heads_corrected"]:.1f}'
    s['sdq_prior'] = f'{100 * T["sd_q_prior"]:.1f}'
    ign = [T[d]['ignore']['coverage'] for d in ('indep', 'nominal_norefs', 'nderhyrja')]
    s['cov_ign_lo'], s['cov_ign_hi'] = f'{100 * min(ign):.0f}%', f'{100 * max(ign):.0f}%'
    s['rq_gain'] = f'{100 * (1 - T["nderhyrja"]["robust"]["rmse_q"] / T["indep"]["robust"]["rmse_q"]):.0f}%'
    c33 = R['t33']['curve']
    s['b4'], s['b8'], s['b16'] = f2(c33[4]['baro']), f2(c33[8]['baro']), f2(c33[16]['baro'])
    s['bmax'] = f2(max(c['baro'] for c in c33))
    s['h8'] = f2(c33[8]['hub'])
    s['h16'] = f2(c33[16]['hub'])
    s['hfirst'] = next(c['n'] for c in c33 if c['hub'] > 1e-9)
    s['bmax_n'] = max(c33, key=lambda c: c['baro'])['n']
    s['b1'] = f2(c33[1]['baro'])
    s['both8'] = f2(c33[8]['both'])
    C = R['checks']
    s['chk'] = C
    B = R['bed']
    s['bed'] = B
    s['series_raw'] = None
    return s


def blocks(R):
    s = fill_numbers(R)
    C, B = s['chk'], s['bed']
    k = s['k']
    BL = []
    A = BL.append
    A(('title', 'State of the art X: placing sensors that interfere'))
    A(('subtitle', 'The robust optimal design of Chowdhary, Attia & Alexanderian (2025) and the Certified OED framework, '
                   'extracted; what they teach about where to put sensors; the state of the art in sensor placement for '
                   'the NATO proposal; who interferes with a CERTAIN-COAST piezometer; and NDERHYRJA-GO, a robust, '
                   'certified design that corrects the interference between sensors'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation · companion to reviews '
                 'I–IX'))
    # ---------------------------------------------------------------------------------------------- 1 outcome
    A(('h', '1. Outcome'))
    A(('bbox', [
        '**The two documents, extracted** (Section 2). The article A1 designs sensor networks that stay optimal when the '
        'error model is uncertain: a max–min problem solved with a budget-constrained probabilistic policy, a low-rank '
        'Laplace approximation of the expected information gain and adjoint eigenvalue sensitivities. The Certified OED '
        'framework A2 computes every linear-Gaussian criterion exactly in data space, attaches a certified optimality '
        'gap to every design, and shows that correlated errors must not be handled by weighting the likelihood.',
        '**What we learn** (Section 2.3): eight lessons for placing sensors, and one gap common to both: they treat '
        'correlated errors as a nuisance to guard against, never as a signal with physical sources that can be '
        '*measured and removed*.',
        '**State of the art for the NATO form** (Section 3, Table {{sota}}): eight lines of work with their sources and '
        'what each still leaves open for CERTAIN-COAST, and a paragraph ready for field 5.3 (Section 7.1).',
        f'**Who interferes** (Section 4, Figure {{{{scheme}}}}a). An unvented piezometer reads the head plus the air '
        f'pressure times its barometric efficiency, the drift of its logger, the cross-talk of its cable and the model '
        f'error. The first two are *correctable*: a barometer and a sealed reference channel on each logger hub see '
        f'them without the signal. The last two are not.',
        f'**Innovation: NDERHYRJA-GO** ("ndërhyrja", the interference; Section 5, Figure {{{{scheme}}}}b). Reference '
        f'channels become design variables, the interference sources are marginalised (the correction), the network is '
        f'chosen against the worst plausible interference, and every network carries a certified optimality gap. '
        f'Proposition N1: a reference channel carries no information alone and is worth exactly zero to the classical '
        f'and the naive criteria, yet its exact value grows as piezometers are added. Proposition N2: the correction '
        f'equals marginalisation, the corrected data give the interference-free estimate, and the information is capped '
        f'by an interference-free ceiling. Proposition N3: the worst amplitudes are the largest, and the gradient in the '
        f'remaining parameters is an exact trace formula, with no PDE solve. Proposition N4: a certified upper bound '
        f'on the robust optimum from a relaxation, the ceiling and the enumeration of the reference channels.',
        f'**Numbers** (T33–T36, test bed of {B["n_piezo"]} piezometers and {B["n_ref"]} reference channels). With '
        f'{k} sensors, the worst-case information of the NDERHYRJA-GO network is {s["w_nderhyrja"]} nats against '
        f'{s["w_indep"]} for the network that ignores the interference (+{s["gain_indep"]}) and {s["w_nominal_norefs"]} '
        f'for the exact network without reference channels (+{s["gain_norefs"]}). Its certified gap is '
        f'{s["gap_k"]} ({s["gap_lo"]}–{s["gap_hi"]} over $k$ = {s["ks"][0]}–{s["ks"][-1]}). Ignoring the interference '
        f'makes the 90% intervals of the wellfield forecast cover only {s["cov_ign_lo"]}–'
        f'{s["cov_ign_hi"]} of the cases; the correction restores {s["cov_nderhyrja_nominal"]} (nominal model) '
        f'and {s["cov_nderhyrja_robust"]} (robust model), and the forecast error falls by {s["rq_gain"]} against the '
        f'network that ignores the interference.',
        '**For the proposal** (Section 7): text for the state of the art, the methodology and the deliverables, three '
        'key performance indicators, and a field plan for the reference channels.']))
    # ---------------------------------------------------------------------------------------------- 2 the documents
    A(('h', '2. The two documents, extracted'))
    A(('h2', '2.1 Robust optimal design of Bayesian nonlinear inverse problems (A1)'))
    A(('p', f'Abhijit Chowdhary and Alen Alexanderian (North Carolina State University) and Ahmed Attia (Argonne '
            f'National Laboratory), *Robust optimal experimental design of infinite-dimensional Bayesian nonlinear '
            f'inverse problems*, [arXiv:2409.09137v2]({ARTICLE}), 12 August 2025, 28 pages, submitted on 6 September '
            f'2025. The question: an optimal sensor network depends on the elements of the inverse problem — the model, '
            f'the prior, the error model — which are uncertain; how can a network be chosen that remains good when they '
            f'vary? The answer follows Wald\'s max–min model (R19): choose the network that maximises the *worst* '
            f'utility over the admissible values $\\theta\\in\\Theta$ of the uncertain parameters,'))
    A(('eq', 'a1', ['\\max_{\\xi\\in\\mathcal{S}(N_b)}\\ \\min_{\\theta\\in\\Theta}\\ \\mathcal{U}(\\xi,\\theta),\\qquad '
                    '\\mathcal{S}(N_b)=\\Big\\{\\xi\\in\\{0,1\\}^{N_d}:\\ \\sum_i\\xi_i=N_b\\Big\\},']))
    A(('p', 'with $N_d$ candidate locations and a budget of $N_b$ sensors (Problem 1). Four observations shape the '
            'method.'))
    A(('b', '**A max–min problem must not be relaxed naively.** Relaxing the binary design to $[0,1]^{N_d}$, the '
            'standard trick of optimal design, changes the optimal set of the max–min problem (shown in R8). The article '
            'therefore optimises a *policy*: the design is a random vector with a Bernoulli law $P(\\xi\\text{ | }p)$, '
            'and the expected worst-case utility is maximised over $p\\in[0,1]^{N_d}$ (Problem 2, after R8 and R9).'))
    A(('b', '**The budget is built into the law, not into a penalty.** The conditional Bernoulli model of R6 puts mass '
            'only on designs with exactly $N_b$ active sensors, $P(\\xi\\text{ | }p,Z=z)=\\prod_{i}w_i^{\\xi_i}/R(z,\\mathcal{T})$ '
            'with $w_i=p_i/(1-p_i)$ (Definition 3.1, Problem 3). The policy gradient is estimated by sampling, '
            '$\\nabla_p\\mathcal{U}\\approx N_{ens}^{-1}\\sum_k\\min_\\theta U(\\xi[k],\\theta)\\nabla_p\\log P(\\xi[k]\\text{ | }p,Z=N_b)$, '
            'with an optimal baseline for variance reduction (eq. 3.6–3.7). No penalty parameter has to be tuned.'))
    A(('b', '**The utility is the expected information gain, made affordable.** For a nonlinear model there is no closed '
            'form, so the posterior is replaced by its Laplace approximation with the Gauss–Newton Hessian, the '
            'information gain of each synthetic data set is written through the $r\\leq N_b$ dominant eigenvalues '
            '$\\lambda_n$ of the prior-preconditioned misfit Hessian, $\\frac{1}{2}\\sum_n[\\log(1+\\lambda_n)-\\lambda_n/(1+'
            '\\lambda_n)]+\\frac{1}{2}\\lVert m_{post}-m_{pr}\\rVert^2_{C_{pr}^{-1}}$, averaged over $N_{SAA}$ data sets, and '
            'the MAP points are frozen at the all-sensor design and at the average $\\bar\\theta$ of the scenario sample '
            '(eq. 3.16–3.18). One evaluation costs $O(4N_bN_{SAA})$ PDE solves (Table 1 of A1).'))
    A(('b', '**The uncertainty sits in the error covariance.** $\\Gamma_n=\\Gamma_n(\\theta)$; a design enters as '
            '$\\hat\\Gamma_n(\\xi,\\theta)=\\mathrm{diag}(\\xi)\\Gamma_n(\\theta)\\mathrm{diag}(\\xi)$ with its pseudo-inverse '
            '(eq. 3.19), and the gradient $\\nabla_\\theta U$ needed by the inner minimisation is derived by an '
            'adjoint-based eigenvalue sensitivity (eq. 3.22–3.30; distinct dominant eigenvalues are assumed), at '
            '$O((3+5N_b)N_{SAA})$ PDE solves.'))
    A(('p', 'Algorithm 3.1 alternates an outer policy update over a finite, growing scenario sample $\\Theta^{(k)}$ with '
            'an inner L-BFGS-B minimisation over $\\Theta$ whose solution is added to the sample. **The experiments** use '
            'an elliptic PDE, $-\\nabla\\cdot(e^m\\nabla u)=0$ on the unit square, with a Gaussian prior $C_{pr}=A^{-2}$ '
            '($\\gamma=0.04$, $\\delta=0.2$), 64×64 linear finite elements (4225 degrees of freedom), $N_{SAA}=32$, '
            'FEniCS, hIPPYlib (R18) and PyOED (R11). (i) *Two sensors* with $\\Gamma_n(\\sigma_1,\\sigma_2,\\rho)$ and '
            '$\\Theta=[0.05,0.15]^2\\times[0,0.99]$: the optimum activates both, the policy degenerates to it, and — the '
            'key finding — the utility is not monotone in the noise parameters and *different designs have different '
            'worst cases*, so the worst case cannot be fixed in advance. The approximate utility correlates with a '
            'double-loop Monte Carlo estimate of the information gain ($10^5$ inner, 1000 outer samples) with Pearson '
            'coefficients above 0.99. (ii) *64 candidates, budget 8*, with $(\\Gamma_n)_{ij}=\\sigma_i\\sigma_j\\rho_{ij}'
            '(\\ell_1,\\ell_2)$, an exponential correlation in the two coordinates and $\\Theta=[0.05,0.15]^{64}\\times'
            '[0.01,2]^2$: five outer/inner iterations; the policy converged in the third but did not degenerate, because '
            'several designs have similar utility; the robust design beats 64 random designs at the worst-case '
            'parameter, and the worst-case parameter beats 64 random parameters at the robust design.'))
    A(('p', '**What it leaves open, for us.** (1) No design comes with a measure of how far it is from the robust '
            'optimum: the comparison with random designs is, in the authors\' words, "insightful" but not a guarantee. '
            '(2) The inner minimum is found by a local optimiser over a growing sample, so the worst case is the worst '
            '*found*. (3) The gradients are bespoke for the utility and for the place where $\\theta$ enters, and need '
            'distinct eigenvalues. (4) Correlated errors are something to be robust *against*; the article does not ask '
            'whether they can be *removed*. (5) The authors list future work: other criteria, non-Laplace posteriors, a '
            'probabilistic inner stage, and "greedy or exchange type algorithms" as a simple alternative for the outer '
            'stage (R14). NDERHYRJA-GO takes up (1), (2) in part, (3), (4) and the greedy–exchange alternative of (5).'))
    A(('h2', '2.2 Certified optimal experimental design (A2)'))
    A(('p', 'The Certified OED framework (A2) revisits the review of Alexanderian (R1) with one principle: *every design '
            'must come with a certificate*, a computable upper bound on how much better any design of the same size '
            'could be. Its parts that matter for sensor placement are these.'))
    A(('b', '**Exact data space (C1 of A2).** For a linear-Gaussian problem every criterion, gradient and certificate is '
            'an explicit function of three matrices of the size of the data, $K=FCF^*$, $L=FC^2F^*$ and $z=FCc$, which '
            '$n_s$ adjoint solves provide once; the information gain of a sensor set $S$ is $\\frac{1}{2}\\log\\det(I+'
            '\\Gamma_{SS}^{-1}K_{SS})$. In its advection–diffusion test the exact trace of the posterior covariance of a '
            '20-sensor design cost 20 adjoint solves, where randomised estimation still had a median error of 0.6% after '
            '256 probes.'))
    A(('b', '**Certificates (C3–C4 of A2).** An equivalence theorem on the capped simplex, Frank–Wolfe gaps, '
            'interlacing, Hadamard and Weyl bounds give every binary design — greedy, thresholded or hand-picked — a '
            'certified optimality gap without PDE solves: 0–19.9% (D) and 4.9–21% (A) for greedy designs in its test. '
            'The information gain is submodular for independent noise but not for correlated noise, so greedy selection '
            'then has no a-priori guarantee and "the certificate is the only measure of quality".'))
    A(('b', '**Correlated noise (Section 5 of A2).** Weighting the likelihood as for independent noise, '
            '$W^{1/2}\\Gamma^{-1}W^{1/2}$, overstates the information of every subset by a conditional mutual '
            'information, $\\mathrm{EIG}_{naive}(S)=I(m;y_S\\text{ | }\\eta_{S^c})\\geq\\mathrm{EIG}(S)$ (Proposition 14): it '
            'credits the design with the noise of the sensors it did *not* select — by 3.63 nats for a 10-sensor greedy '
            'design and 6.81 nats at 25 sensors in its test. The noise-inflation relaxation $P_\\rho(w)=(\\rho I+W(\\Gamma-'
            '\\rho I))^{-1}W$, an Anderson–Duffin parallel sum (C9), is exact at binary designs and operator concave if '
            'and only if $\\rho\\leq\\lambda_{\\min}(\\Gamma)$ (Theorem 15); with a diagonal inflation $R$ it is concave '
            'whenever $\\Gamma-R\\succeq0$. Certified gaps under correlated noise were 24.5% and 36.0% at $k=10$.'))
    A(('p', '**What it leaves open, for us.** The error covariance is assumed *known* (its Limitations); there is no '
            'robustness to an uncertain error model, which is exactly what A1 adds; and correlated errors are again a '
            'given, never something to be corrected by measurement.'))
    A(('h2', '2.3 What we learn for placing sensors'))
    for i, t in enumerate([
        '**Compute, do not estimate.** For linear or linearised models the whole design study lives in data space after '
        '$n_s$ adjoint solves (A2); every candidate swap, worst case and certificate is then a small dense computation.',
        '**Report every network with its certified gap** (A2). Under correlated errors greedy selection has no guarantee, '
        'and a design without a certificate is a design without a quality statement.',
        '**Never weight correlated errors naively** (A2, Proposition 14). Use the exact criterion for binary designs and '
        'the noise-inflation relaxation for bounds.',
        '**Design against the worst plausible error, not the nominal one** (A1). The worst case differs from design to '
        'design, so it cannot be chosen beforehand.',
        '**Do not relax a max–min problem naively** (A1, R8): search binary designs directly — by a policy (A1) or by '
        'greedy selection and exchange (the alternative A1 proposes).',
        '**Build the budget into the search**, not into a penalty (A1, R6).',
        '**Treat Laplace-based information as a surrogate**: it ranks designs well (correlation above 0.99 in A1) but '
        'carries no certificate (A2, Section 7.9).',
        '**The common gap.** Both documents take the error covariance as given — known (A2) or uncertain within a box '
        '(A1). Neither asks where correlated errors come from. In a groundwater network most of them have physical '
        'sources — air pressure, logger drift — that cheap reference channels can *measure*. A network that buys those '
        'channels can *remove* the correlation instead of merely guarding against it. This is the innovation of this '
        'review.'], 1):
        A(('b', f'{i}. {t}'))
    # ---------------------------------------------------------------------------------------------- 3 state of the art
    A(('h', '3. State of the art in sensor placement'))
    A(('p', 'Table {{sota}} places the two documents among the lines of work that a NATO reviewer will expect to see. '
            'Sources marked R are cited as A1 lists them, C as A2 lists them, W were checked against publisher records '
            'in this review; the full entries are in the References.'))
    A(('cap', 'Table {{sota}}. Sensor placement: lines of work, what they give, and what they leave open for '
              'CERTAIN-COAST.'))
    A(('table', ['Line of work', 'Sources', 'What it gives', 'Open for CERTAIN-COAST'], [
        ['Classical and distributed-parameter design', 'R5, R10, R17, C12, R16',
         'A-, D-, c-criteria; equivalence theorems; Bayesian design; sensor location for PDE systems',
         'Independent errors; no certificate for binary networks'],
        ['Bayesian design with PDEs on function space', 'R1, R2, R4, R20, C13, A2',
         'Mesh-independent criteria, low-rank and data-space computation, goal-oriented design, certificates (A2)',
         'Error covariance known'],
        ['Greedy selection and submodularity', 'C1, C2, C14, C3, R14',
         'Greedy with (1−1/e) guarantee for submodular criteria; local search',
         'No guarantee under correlated errors'],
        ['Correlated errors', 'C4, C5, C6, R7, C7, C8, A2',
         'Virtual-noise and noise-inflation relaxations; the naive weighting overstates (A2)',
         'Correlation taken as given, never removed'],
        ['Robust design', 'R19, R15, R13, R3, R12, R8, A1',
         'Max–min and averaged designs under model, prior or error uncertainty; ambiguity sets',
         'No optimality certificate; worst case found by local search'],
        ['Binary optimisation for placement', 'R9, R6, A1', 'Bernoulli policies with budget, stochastic gradients',
         'Sampling cost; no bound'],
        ['Several sensor types; early warning', 'C10, C11',
         'Placement of several sensor types under a cost budget; tsunami early warning by Bayesian design',
         'Reference channels that see only the error'],
        ['Correction of groundwater records', 'W1, W2',
         'Barometric efficiency and response functions; removal of air-pressure and earth-tide effects by '
         'regression deconvolution with a nearby barometer', 'Not linked to network design'],
    ], [3.3, 2.6, 6.0, 5.1], 9))
    A(('p', 'The pattern of the table is the case for the innovation: placement methods take the errors as given, and '
            'the hydrogeological literature removes air-pressure effects record by record (W1, W2) but never asks where '
            'the barometers and reference channels should go, or how many of them a network should buy at the expense '
            'of piezometers. The closest design work is the placement of several sensor types under a budget (C10). '
            'There a sensor of each type measures the state. Our reference channels measure only the error, which no '
            'classical criterion can value (Proposition N1).'))
    # ---------------------------------------------------------------------------------------------- 4 scheme
    A(('h', '4. Our scheme: who interferes with a CERTAIN-COAST piezometer'))
    A(('img', 'scheme', 17.0))
    A(('cap', 'Figure {{scheme}}. (a) The sources of a piezometer reading: the head that responds to the aquifer state, '
              'and the interference. Air pressure and logger drift are correctable — a barometer and a sealed reference '
              'channel on each logger hub see them without the signal; cable cross-talk inside a nest and the '
              'correlated model error are not. (b) The NDERHYRJA-GO loop: data-space set-up, amplitudes at their upper '
              'ends, robust greedy selection and exchange against a growing scenario set, an adversary with exact '
              'gradients, the certificate, and in operation the correction and a residual check.'))
    A(('p', 'At the wellfields and the port of Durrës, and at the Fushë-Kuqe pilot of CERTAIN-COAST, the piezometers '
            'are pressure transducers on loggers, grouped in nests (several screens in one borehole or a cluster of '
            'boreholes on one cable) and served by telemetry hubs. Their reading $y$ is the head $h=Fm$ plus five '
            'errors (Figure {{scheme}}a):'))
    A(('eq', 'model', ['y=Fm+\\big(b\\,c_a+H c_h\\big)+\\big(N c_n+e_\\ell\\big)+\\varepsilon,']))
    A(('p', 'where $c_a$ is the air pressure (in metres of water) and $b_i=\\mathrm{BE}_i+\\delta_i$ the barometric '
            'efficiency of an unvented transducer, estimated from past records with an error $\\delta_i$ (W1 shows that '
            'the response can be lagged, so a single efficiency is itself an approximation; W2); $c_h$ is the drift of '
            'the logger electronics of each hub, with loading 1 on the transducers it serves; $c_n$ the cross-talk on '
            'the shared cable of a nest; $e_\\ell$ a model error correlated over a length $\\ell$; and $\\varepsilon$ '
            'independent noise. The first bracket is correctable, the second is not. The barometer reads $c_a$ and a sealed reference channel on hub $h$ reads $c_h$, each '
            'with its own small noise and no signal. The error covariance of all candidates is'))
    A(('eq', 'gamma', ['\\Gamma(\\theta)=\\Gamma_e(\\theta)+s_a^2\\,bb^{\\mathsf{T}}+s_h^2HH^{\\mathsf{T}},\\qquad '
                       '\\Gamma_e(\\theta)=D+s_n^2NN^{\\mathsf{T}}+\\tau^2E(\\ell),']))
    A(('p', 'where $\\Gamma_e$ is the non-correctable part, and $\\theta=(s_\\varepsilon,s_a,s_h,s_n,\\tau,\\ell,\\delta_1,'
            '\\dots,\\delta_{n_p})$ lies in a box: the amplitudes between plausible lower and upper values, $\\ell$ in a range of '
            'correlation lengths and each $\\delta_i$ within $\\pm\\Delta$. Table {{sources}} lists the sources with the '
            'values of the test bed of Section 6.'))
    A(('cap', 'Table {{sources}}. Interference sources of the test bed, their reach and their correction.'))
    A(('table', ['Source', 'Affects', 'Correctable by', 'Range in the test bed'], [
        ['Air pressure × barometric efficiency', 'all unvented piezometers', 'barometer',
         f'$s_a$ = {B["lo"][1]:.2f}–{B["hi"][1]:.2f} m; BE 0.4–0.9 ± {B["delta"]:.2f}'],
        ['Logger drift', 'the piezometers of one hub', 'sealed reference channel on the hub',
         f'$s_h$ = {B["lo"][2]:.2f}–{B["hi"][2]:.2f} m'],
        ['Cable cross-talk', 'the piezometers of one nest', '— (not correctable)',
         f'$s_n$ = {B["lo"][3]:.2f}–{B["hi"][3]:.2f} m'],
        ['Model error', 'all piezometers, correlated over $\\ell$', '— (not correctable)',
         f'$\\tau$ = {B["lo"][4]:.2f}–{B["hi"][4]:.2f} m, $\\ell$ = {B["lo"][5]:.2f}–{B["hi"][5]:.2f}'],
        ['Independent noise', 'each sensor', '—', f'{100 * B["sig0"]:.0f} cm × {B["lo"][0]:.2f}–{B["hi"][0]:.2f}; '
                                                  f'barometer {1000 * B["sigb"]:.0f} mm, hub channel '
                                                  f'{1000 * B["sigr"]:.0f} mm'],
    ], [4.4, 4.0, 4.0, 4.6], 9))
    # ---------------------------------------------------------------------------------------------- 5 NDERHYRJA-GO
    A(('h', '5. NDERHYRJA-GO: robust, certified placement that corrects the interference'))
    A(('h2', '5.1 The criterion'))
    A(('p', 'A network is a set $S$ of candidates — piezometers and reference channels alike. With the data-space '
            'matrix $K=FCF^{\\mathsf{T}}$ of A2 (rows of zeros for the reference channels, which see no signal), its '
            'information about the aquifer state under the error parameters $\\theta$ is'))
    A(('eq', 'eig', ['\\mathrm{EIG}(S,\\theta)=\\frac{1}{2}\\log\\det\\big(\\Gamma_{SS}(\\theta)+K_{SS}\\big)-\\frac{1}{2}\\log'
                     '\\det\\Gamma_{SS}(\\theta),']))
    A(('p', 'and NDERHYRJA-GO seeks the network with the largest worst-case information,'))
    A(('eq', 'rob', ['\\mathrm{OPT}_k(\\Theta)=\\max_{\\lvert S\\rvert=k}\\ \\min_{\\theta\\in\\Theta}\\ \\mathrm{EIG}(S,'
                     '\\theta).']))
    A(('p', 'The four propositions below say what a reference channel is worth, what the correction does, where the '
            'worst case lies and how far a network is from this optimum.'))
    A(('h2', '5.2 What a reference channel is worth'))
    A(('prop', 'Proposition N1 (value of a reference channel).',
            'Let $r$ be a reference channel ($K_{rr}=0$, $K_{rS}=0$). Then'))
    A(('eq', 'n1', ['\\mathrm{EIG}(S\\cup r)-\\mathrm{EIG}(S)=\\frac{1}{2}\\log\\frac{\\Gamma_{rr}-\\Gamma_{rS}(\\Gamma_{SS}+'
                    'K_{SS})^{-1}\\Gamma_{Sr}}{\\Gamma_{rr}-\\Gamma_{rS}\\Gamma_{SS}^{-1}\\Gamma_{Sr}}\\ \\geq0,']))
    A(('p', 'with equality if and only if $\\Gamma_{rS}\\big(\\Gamma_{SS}^{-1}-(\\Gamma_{SS}+K_{SS})^{-1}\\big)'
            '\\Gamma_{Sr}=0$. In particular (a) a reference channel alone is worth nothing; (b) it is worth exactly '
            'nothing to any design rule that models the errors as independent, and exactly nothing to the naive '
            'weighting of A2 — so neither ever buys it; (c) its value can grow as piezometers are added, so the '
            'information gain is not submodular.'))
    A(('proof', 'Write $T=S\\cup r$ and take Schur complements on $r$ in both determinants of [[eig]]. Since $K$ has '
                'zero row and column at $r$, the complement in $\\Gamma_{TT}+K_{TT}$ is the numerator of [[n1]] and the '
                'complement in $\\Gamma_{TT}$ its denominator. $(\\Gamma_{SS}+K_{SS})^{-1}\\preceq\\Gamma_{SS}^{-1}$ gives '
                'the inequality and the equality condition. (a) $S=\\emptyset$. (b) With diagonal $\\Gamma$, '
                '$\\Gamma_{rS}=0$. For the naive weighting, $[\\Gamma^{-1}]_{TT}K_{TT}$ has a zero column at $r$, so '
                '$\\det(I+[\\Gamma^{-1}]_{TT}K_{TT})=\\det(I+[\\Gamma^{-1}]_{SS}K_{SS})$. (c) At $S=\\emptyset$ the gain is '
                'zero and it is positive once $S$ holds a piezometer that shares a source with $r$; a submodular '
                'function has non-increasing gains.'))
    A(('h2', '5.3 The correction is marginalisation, and it has a ceiling'))
    A(('prop', 'Proposition N2 (correction and ceiling).',
            'Write $\\Gamma=\\Gamma_e+B\\Sigma_cB^{\\mathsf{T}}$ with $B=[b\\ H]$ the loadings of the correctable sources '
            '$c=(c_a,c_h)$, and let $d_S=y_S-F_Sm_{pr}$. (i) *Correction.* The posterior mean of the sources is '
            '$\\hat c=\\Sigma_cB_S^{\\mathsf{T}}(K_{SS}+\\Gamma_{SS})^{-1}d_S$, and the posterior mean of the aquifer '
            'state equals the interference-free formula applied to the corrected data:'))
    A(('eq', 'n2a', ['\\hat m=m_{pr}+CF_S^{\\mathsf{T}}(K_{SS}+\\Gamma_{SS})^{-1}d_S=m_{pr}+CF_S^{\\mathsf{T}}(K_{SS}+'
                     '\\Gamma_{e,SS})^{-1}\\big(d_S-B_S\\hat c\\big).']))
    A(('p', '(ii) *Penalty.* For piezometers $P$ and reference channels $R$ with noise independent of the rest, the '
            'information lost to the interference is a conditional mutual information,'))
    A(('eq', 'n2b', ['\\mathrm{EIG}_e(P)-\\mathrm{EIG}(P\\cup R)=I(m;c\\text{ | }y_P,y_R)\\ \\geq0,\\qquad \\mathrm{EIG}_e(P)='
                     '\\frac{1}{2}\\log\\det\\big(I+\\Gamma_{e,PP}^{-1}K_{PP}\\big),']))
    A(('p', 'so no choice of reference channels can raise a network above the **correction ceiling** '
            '$\\mathrm{EIG}_e(P)$ of its piezometers. (iii) If $B_R$ has full column rank, the penalty tends to zero as '
            'the noise of the reference channels tends to zero.'))
    A(('proof', '(i) $\\hat c$ is the Gaussian conditional mean, since $\\mathrm{Cov}(c,y_S)=\\Sigma_cB_S^{\\mathsf{T}}$. '
                'With $A=K_{SS}+\\Gamma_{e,SS}$, $d_S-B_S\\hat c=(I-B_S\\Sigma_cB_S^{\\mathsf{T}}(A+B_S\\Sigma_cB_S^{\\mathsf '
                'T})^{-1})d_S=A(A+B_S\\Sigma_cB_S^{\\mathsf{T}})^{-1}d_S$, and $A^{-1}$ of this is $(K_{SS}+\\Gamma_{SS})^{-1}'
                'd_S$. (ii) By the chain rule, $I(m;y_P,y_R,c)=I(m;c)+I(m;y_P,y_R\\text{ | }c)=0+\\mathrm{EIG}_e(P)$, because '
                'given $c$ the reference readings are pure independent noise; the same quantity equals $\\mathrm{EIG}(P'
                '\\cup R)+I(m;c\\text{ | }y_P,y_R)$. (iii) With full column rank and vanishing reference noise, $c$ is a '
                'function of $y_R$ in the limit, so $I(m;c\\text{ | }y_P,y_R)\\to0$.'))
    A(('h2', '5.4 Where the worst case lies'))
    A(('prop', 'Proposition N3 (worst amplitudes and exact gradients).',
            '(i) $\\mathrm{EIG}(S,\\theta)$ is non-increasing in each amplitude $s_\\varepsilon,s_a,s_h,s_n,\\tau$, so the '
            'worst case puts all amplitudes at their upper ends, and only the shape parameters $(\\ell,\\delta)$ have to '
            'be searched. (ii) For any parameter $\\theta_j$,'))
    A(('eq', 'n3', ['\\frac{\\partial\\,\\mathrm{EIG}(S,\\theta)}{\\partial\\theta_j}=\\frac{1}{2}\\,\\mathrm{tr}\\Big[\\big((\\Gamma_'
                    '{SS}+K_{SS})^{-1}-\\Gamma_{SS}^{-1}\\big)\\,\\partial_j\\Gamma_{SS}\\Big],']))
    A(('p', 'with $\\partial_{\\delta_i}\\Gamma=s_a^2(e_ib^{\\mathsf{T}}+be_i^{\\mathsf{T}})$ and $\\partial_\\ell\\Gamma='
            '\\tau^2E(\\ell)\\circ(\\lvert x_i-x_j\\rvert/\\ell^2)$ — an exact formula in data space that needs no PDE '
            'solve and no eigenvalue sensitivity.'))
    A(('proof', '(ii) is the derivative of $\\log\\det$. (i) For an amplitude, $\\partial_j\\Gamma\\succeq0$ (a square times '
                'a fixed positive semidefinite matrix), and $(\\Gamma_{SS}+K_{SS})^{-1}-\\Gamma_{SS}^{-1}\\preceq0$, so the '
                'trace in [[n3]] is non-positive.'))
    A(('p', 'Part (i) removes 5 of the dimensions of the box from the search and makes the worst amplitudes exact. '
            'The shape parameters are not monotone — as A1 observed for its correlation parameters — and are found by '
            'an adversary, L-BFGS-B with the gradient [[n3]] from several starts.'))
    A(('h2', '5.5 How far from the robust optimum'))
    A(('prop', 'Proposition N4 (robust certificate).',
            'Let $\\Theta_f\\subset\\Theta$ be any finite scenario set, $\\Gamma_e(\\theta)$ the non-correctable part of '
            '$\\Gamma(\\theta)$, and $R_\\theta=t_\\theta\\,\\mathrm{diag}\\,\\Gamma_e(\\theta)$ with the largest '
            '$t_\\theta$ such that $\\Gamma_e(\\theta)-R_\\theta\\succeq0$. Let $g_\\theta$ and $h_\\theta$ be the '
            'noise-inflation relaxations (A2) of $\\mathrm{EIG}(\\cdot,\\theta)$ and of the ceiling '
            '$\\mathrm{EIG}_e(\\cdot,\\theta)$, both with inflation $R_\\theta$. Then for every set $R_0$ of reference '
            'channels and any points $w_1,\\dots,w_T$ of the capped simplex $\\Delta_k(R_0)$ (references fixed to '
            '$R_0$, piezometer weights in $[0,1]$ summing to $k-\\lvert R_0\\rvert$),'))
    A(('eq', 'n4', ['\\mathrm{OPT}_k(\\Theta)\\ \\leq\\ \\bar U:=\\max_{R_0}\\ \\max_{v\\in\\Delta_k(R_0)}\\ \\min_{\\theta\\in'
                    '\\Theta_f,\\ t,\\ f\\in\\{g_\\theta,h_\\theta\\}}\\Big[f(w_t)+\\nabla f(w_t)^{\\mathsf{T}}(v-w_t)\\Big],']))
    A(('p', 'and the inner maximum is a linear programme. Every network $S$ therefore carries the certified gap '
            '$\\bar U-\\min_{\\theta\\in\\Theta_f}\\mathrm{EIG}(S,\\theta)$ with respect to the scenario set.'))
    A(('proof', '$\\Theta_f\\subset\\Theta$ gives $\\mathrm{OPT}_k(\\Theta)\\leq\\mathrm{OPT}_k(\\Theta_f)$. Since $\\Gamma(\\theta)'
                '\\succeq\\Gamma_e(\\theta)\\succeq R_\\theta$, both relaxations are concave on the box and exact at '
                'binary points (Theorem 15 of A2 with a diagonal inflation, its Appendix A.6). For the optimal binary '
                'network $T$ with references $R_0$, $g_\\theta(1_T)=\\mathrm{EIG}(T,\\theta)$ and, by Proposition N2, '
                '$h_\\theta(1_T)=\\mathrm{EIG}_e(T\\cap P,\\theta)\\geq\\mathrm{EIG}(T,\\theta)$; so $\\min_\\theta'
                '\\mathrm{EIG}(T,\\theta)$ is at most the minimum of all these concave functions at $1_T\\in\\Delta_k(R_0)$. '
                'Each concave function lies below its tangent planes. Maximising the minimum of the planes over '
                '$\\Delta_k(R_0)$ and over $R_0$ gives [[n4]].'))
    A(('p', 'Three layers make the bound useful, and Section 6 measures each. The inflation borrowed from $\\Gamma_e$ is '
            'far larger than the one $\\Gamma$ itself allows, because the common air-pressure mode makes $\\Gamma$ '
            f'nearly singular in relative terms: in the test bed $t$ = {C["n4_inflation_t"]:.4f} for $\\Gamma$, against '
            'about 0.3 for $\\Gamma_e$. The ceiling cuts stop the relaxation from correcting the interference for free. '
            'The enumeration of the $2^{n_r}$ reference sets stops it from buying half a barometer.'))
    A(('h2', '5.6 The algorithm'))
    A(('box', [
        '**NDERHYRJA-GO.** *Input:* data-space matrices $K$ (and $z$ for a goal), the candidate list with its reference '
        'channels, the loadings and the box $\\Theta$, the budget $k$.',
        '**1. Set up.** $n_s$ adjoint solves give $K$ (A2). Put the amplitudes at their upper ends (Proposition N3) and '
        'start the scenario set with the ends of $\\ell$ and the two uniform shifts $\\delta=\\pm\\Delta$.',
        '**2. Robust greedy.** Add, one at a time, the candidate — piezometer or reference channel — with the largest '
        'worst-case information over the scenario set; each gain is a ratio of two Schur complements (exact).',
        '**3. Exchange.** Swap one selected and one unselected candidate while the worst case improves; restart from the '
        'best known designs (multi-start).',
        '**4. Adversary.** Minimise $\\mathrm{EIG}(S,\\theta)$ over $(\\ell,\\delta)$ by L-BFGS-B with the exact gradient '
        '[[n3]]; if it finds a worse scenario, add it and return to step 3.',
        '**5. Certificate.** Compute $\\bar U$ of [[n4]] by cutting planes and report the gap of the chosen network.',
        '**6. Operation.** Correct each reading with $\\hat c$ of Proposition N2, forecast with the robust error model, '
        'and check that the corrected residuals are no longer correlated across hubs.']))
    A(('p', 'The cost is that of A2 for the set-up and dense algebra on matrices of the size of the data afterwards: '
            'in the test bed one run of steps 2–4 took 0.2 s for a 12-sensor network on one processor core, and the '
            'certificate with its 32 reference sets 66 s. A hard rule that two sensors on the same cable must not both be active, or any other '
            'exclusion, enters steps 2–3 as a constraint and leaves $\\bar U$ valid, since it can only lower the '
            'optimum.'))
    A(('box', '**INNOVATION.** NDERHYRJA-GO turns sensor interference from a nuisance into a design variable. '
              '(1) Reference channels that see only the error — a barometer, a sealed channel on each logger hub — '
              'enter the search beside the piezometers, valued by the exact criterion that alone can see them '
              '(Proposition N1). (2) The correction is exact marginalisation, and the corrected data reproduce the '
              'interference-free estimate (Proposition N2(i)). (3) A ceiling bounds what any correction can achieve '
              '(Proposition N2(ii)). (4) The worst case is found exactly in the amplitudes and by an adversary with '
              'exact data-space gradients in the shapes (Proposition N3), which replaces the eigenvalue sensitivities of '
              'A1. (5) Every robust network carries a certified gap, which A1 lacks, built from a relaxation that is '
              'tightened by the ceiling and by enumerating the reference channels (Proposition N4). To our knowledge, '
              'neither document, nor the sources of Table {{sota}}, places reference channels by optimal design or '
              'certifies a robust network.'))
    # ---------------------------------------------------------------------------------------------- 6 tests
    A(('h', '6. Tests'))
    A(('p', f'**Test bed.** The unit square stands for 10 km of coast (sea at $y=0$) by 10 km inland. The aquifer state '
            f'is a recharge or salinity-source anomaly on a 30×30 grid with a Gaussian prior (correlation length about '
            f'0.14); the heads respond through a screened-Poisson operator, scaled so that the prior head anomaly at '
            f'the piezometers has a standard deviation of {100 * B["head_sd"]:.0f} cm. There are 16 nests of 3 '
            f'piezometers (shared cable), 4 telemetry hubs serving 4 nests each, one barometer and one sealed reference '
            f'channel per hub: {B["n_piezo"]} + {B["n_ref"]} candidates. The barometric efficiencies are drawn in '
            f'0.4–0.9 and known to $\\pm${B["delta"]:.2f}; the other ranges are those of Table {{{{sources}}}}. The '
            f'nominal error model takes the middle amplitudes, $\\ell$ = {B["nom"][5]:.2f} and $\\delta=0$. The goal of '
            f'the wellfield forecast is the mean anomaly over the wellfield ({x_wf(B)}; prior standard deviation '
            f'{s["sdq_prior"]} cm). Six design rules are compared:'))
    for rule, t in [('interference ignored', 'greedy with the errors modelled as independent (the classical rule)'),
                    ('naive correlated weighting', 'greedy with the naive criterion of A2, nominal $\\theta$'),
                    ('exact, no references', 'greedy and exchange, exact criterion, nominal $\\theta$, piezometers only'),
                    ('robust, no references', 'NDERHYRJA-GO restricted to piezometers (the robust rule of A1, solved '
                                              'by greedy and exchange)'),
                    ('exact + references (nominal)', 'greedy and exchange with the reference channels, nominal $\\theta$'),
                    ('NDERHYRJA-GO', 'robust, with the reference channels, multi-start, adversary')]:
        A(('b', f'**{rule}**: {t};'))
    A(('p', f'every network is then evaluated at the nominal $\\theta$ and at its own worst case, found by the adversary '
            f'from the pooled scenarios and six random starts.'))
    A(('p', f'**Checks of the closed forms.** The Schur gains agree with direct evaluation to '
            f'{C["schur_gain_err"]:.1e}; formula [[n1]] to {C["n1_closed_form_err"]:.1e}; the naive and the independent '
            f'criteria give the barometer a gain of exactly {C["n1_naive_gain"]:.0f}; identity [[n2a]] holds to '
            f'{C["n2_corrected_mean_err"]:.1e} (relative); the penalty [[n2b]] was positive for all 50 random networks '
            f'(smallest {C["n2_min_penalty"]:.2f} nats) and fell from {C["n2_limit_gaps"][0]:.1e} to '
            f'{C["n2_limit_gaps"][-1]:.1e} nats as the reference noise was divided by 1000; gradient [[n3]] agrees with '
            f'finite differences to {C["n3_grad_err"]:.1e}, and all amplitude derivatives were negative (largest '
            f'{C["n3_amp_derivs_max"]:.2f}); the relaxation is exact at binary networks to {C["n4_binary_err"]:.1e}, '
            f'its gradient agrees to {C["n4_grad_err"]:.1e}, and its largest second difference over 100 random '
            f'segments was {C["n4_max_second_diff"]:.2f} (concave).'))
    A(('img', 'bed', 17.0))
    A(('cap', f'Figure {{{{bed}}}}. The test bed and two {s["t36k"]}-sensor networks: the classical rule, which ignores '
              f'the interference and spreads piezometers over the nests, and NDERHYRJA-GO, which buys reference '
              f'channels and fewer piezometers.'))
    # T33
    A(('h2', '6.1 T33: what reference channels are worth'))
    A(('p', f'Figure {{{{t33}}}}a follows the value of one reference channel as the piezometers of a greedy network are '
            f'added. The barometer is worth nothing alone, {s["b1"]} nats after one piezometer, up to {s["bmax"]} after '
            f'{s["bmax_n"]}, and it settles near {s["b16"]} as the piezometers themselves begin to separate the common '
            f'mode from the spatially varying signal. The hub channel is worth nothing until the first piezometer of '
            f'its hub is selected (the {s["hfirst"]}th here); it then grows steadily, to {s["h8"]} nats after 8 and '
            f'{s["h16"]} after 16 piezometers. All five reference channels together add {s["both8"]} nats to the '
            f'8-piezometer network. Gains that grow as the network grows are the opposite of submodularity '
            f'(Proposition N1(c)). The naive and the independent criteria value the barometer at exactly zero '
            f'throughout, as Proposition N1(b) states. Figure {{{{t33}}}}b compares the networks at the '
            f'nominal $\\theta$: with {k} sensors NDERHYRJA-GO reaches {s["n_nderhyrja"]} nats, {s["ceil_frac"]} of the '
            f'correction ceiling {s["ceil"]} of its own piezometers, against {s["n_indep"]} for the classical rule.'))
    A(('img', 't33', 17.0))
    A(('cap', 'Figure {{t33}}. T33. (a) Information added by a barometer or a hub channel to a greedy network of '
              'piezometers (Proposition N1): positive and first rising for the exact criterion, zero for the naive and '
              'the independent criteria. (b) Information at the nominal error model against the number of sensors, '
              'with the correction ceiling of the NDERHYRJA-GO piezometers (Proposition N2).'))
    # T34
    A(('h2', '6.2 T34: the worst plausible interference'))
    rows = []
    for kk in s['ks']:
        e = R['t34'][str(kk)]
        rows.append([str(kk)] + [f"{e[r]['worst']:.2f}" + (f" ({e[r]['nrefs']})" if r in ('nominal', 'nderhyrja') else '')
                                 for r in ('indep', 'naive', 'nominal_norefs', 'robust_norefs', 'nominal', 'nderhyrja')]
                    + [f"{R['t35'][str(kk)]['ub']:.2f}"])
    A(('p', f'Table {{{{tab34}}}} and Figure {{{{t34}}}}a give the worst-case information of each rule. NDERHYRJA-GO is '
            f'{"the best rule at every budget" if s["best_all"] else "the best rule at most budgets"}. With {k} sensors '
            f'it reaches {s["w_nderhyrja"]} nats, against {s["w_indep"]} for the classical rule (+{s["gain_indep"]}), '
            f'{s["w_naive"]} for the naive weighting, {s["w_nominal_norefs"]} for the exact rule without references '
            f'(+{s["gain_norefs"]}), {s["w_robust_norefs"]} for the robust rule of A1 without references '
            f'(+{s["gain_rnorefs"]}) and {s["w_nominal"]} for the nominal rule with references (+{s["gain_nominal"]}). '
            f'The reference channels carry most of the gain, the robustness the smaller remainder; NDERHYRJA-GO buys '
            f'{s["refs_by_k"]}. The naive rule claims {s["naive_claim"]} nats for its network, whose exact nominal value '
            f'is {s["naive_true"]} (Proposition 14 of A2). At the worst case, the posterior standard deviation of the '
            f'wellfield anomaly is {s["sdq_nd"]} cm for NDERHYRJA-GO against {s["sdq_in"]} cm for the classical rule.'))
    A(('cap', 'Table {{tab34}}. T34. Worst-case information (nats) of six rules against the number of sensors $k$; in '
              'brackets the number of reference channels bought; last column the certified bound $\\bar U$ of T35.'))
    A(('table', ['k', 'ignored', 'naive', 'exact, no ref.', 'robust, no ref.', 'exact + ref.', 'NDERHYRJA-GO', 'Ū'],
       rows, [1.0, 2.0, 2.0, 2.2, 2.3, 2.3, 2.6, 1.6], 9))
    A(('img', 't34', 17.0))
    A(('cap', 'Figure {{t34}}. (a) T34–T35: worst-case information of the six rules and the certified upper bound on '
              'the robust optimum, with its three layers. (b) T35 on 14 candidates: greedy and exchange, the exhaustive '
              'optimum over all subsets, and the certificate.'))
    # T35
    A(('h2', '6.3 T35: certificates'))
    A(('p', f'With {k} sensors the relaxation alone bounds the robust optimum by {s["ubp_k"]} nats, the ceiling cuts '
            f'lower this to {s["ubc_k"]}, and the enumeration of the 32 reference sets to {s["ub_k"]}: the '
            f'NDERHYRJA-GO network ({s["val_k"]} nats over its scenario set) is certified within {s["gap_k"]} of the '
            f'robust optimum. Over $k$ = {s["ks"][0]}–{s["ks"][-1]} the certified gaps range from {s["gap_lo"]} to '
            f'{s["gap_hi"]}; they are widest for small networks, where the relaxation can spread a few sensors over '
            f'many candidates, as A2 reports for correlated noise (24.5–36.0% at $k=10$). On a {s["small_n"]}-candidate '
            f'instance (4 nests of one hub, the barometer and the hub channel) all subsets were enumerated over the '
            f'final scenario set (Figure {{{{t34}}}}b): greedy and exchange found the exact robust optimum in '
            f'{s["small_exact"]} of {s["small_cnt"]} budgets'
            f'{"" if s["small_exact"] == s["small_cnt"] else " (largest shortfall " + s["small_worst"] + ")"}, and the '
            f'certificate was {"above the optimum in every case, as it must be" if s["small_valid"] else "violated"}.'))
    # T36
    A(('h2', '6.4 T36: the correction in operation'))
    t = R['t36']
    A(('p', f'Two thousand synthetic years were drawn with the error parameters uniform in the box, and the {s["t36k"]}-'
            f'sensor networks of three rules were used with three error models in the forecast: interference ignored '
            f'(independent noise), corrected with the nominal model, and corrected with the robust model (upper '
            f'amplitudes and the loading errors as extra variance $s_a^2\\Delta^2/3$). Figure {{{{t36}}}}a–b and Table '
            f'{{{{tab36}}}}: ignoring the interference makes the 90% forecast intervals overconfident — '
            f'{s["cov_indep_ignore"]} coverage for the classical network and {s["cov_nderhyrja_ignore"]} for the '
            f'NDERHYRJA-GO network, whose reference channels are then wasted. The nominal correction gives '
            f'{s["cov_nderhyrja_nominal"]} and the robust correction {s["cov_nderhyrja_robust"]}. With the robust '
            f'correction, the forecast error is {s["rq_nderhyrja_robust"]} cm for NDERHYRJA-GO against '
            f'{s["rq_indep_robust"]} cm for the classical network and {s["rq_nominal_norefs_robust"]} cm without '
            f'references ({s["rq_gain"]} lower than the classical network). The corrected heads of the NDERHYRJA-GO '
            f'piezometers have a root-mean-square error of {s["hc_nderhyrja_robust"]} cm against '
            f'{s["hr_nderhyrja_robust"]} cm for the raw readings; what remains is the error that cannot be corrected '
            f'(cable cross-talk, model error, sensor noise). Figure {{{{t36}}}}c shows one season at one piezometer.'))
    rows = []
    lab = dict(indep='interference ignored', nominal_norefs='exact, no references', nderhyrja='NDERHYRJA-GO')
    for d in ('indep', 'nominal_norefs', 'nderhyrja'):
        for m, ml in (('ignore', 'ignored'), ('nominal', 'nominal'), ('robust', 'robust')):
            v = t[d][m]
            rows.append([lab[d] if m == 'ignore' else '', ml, f"{100 * v['coverage']:.1f}", f"{100 * v['rmse_q']:.1f}",
                         f"{100 * v['width']:.1f}", f"{100 * v['rmse_heads_raw']:.1f}",
                         f"{100 * v['rmse_heads_corrected']:.1f}"])
    A(('cap', 'Table {{tab36}}. T36. Wellfield forecast and corrected heads over 2000 draws: coverage of the 90% '
              'intervals (%), root-mean-square error and mean width of the forecast (cm), and error of the raw and of '
              'the corrected piezometer heads (cm).'))
    A(('table', ['Network', 'Error model', 'Coverage', 'RMSE', 'Width', 'Heads raw', 'Heads corr.'], rows,
       [3.6, 2.0, 1.9, 1.8, 1.8, 2.2, 2.4], 9))
    A(('img', 't36', 17.0))
    A(('cap', 'Figure {{t36}}. T36. (a) Coverage of the 90% intervals of the wellfield forecast, by network and by '
              'error model (dashed: nominal 90%). (b) Root-mean-square error of the forecast. (c) One season of daily '
              'heads at one NDERHYRJA-GO piezometer: raw reading, reading corrected with the barometer and the hub '
              'channel, and the true anomaly.'))
    # ---------------------------------------------------------------------------------------------- 7 NATO
    A(('h', '7. For the NATO form'))
    A(('h2', '7.1 State of the art (field 5.3, sensor placement)'))
    A(('box', [
        'Optimal sensor placement for PDE-governed inverse problems is a mature field: Bayesian A-, D- and goal-oriented '
        'criteria on function space, computed by low-rank or data-space methods, with greedy selection that is '
        'near-optimal when the criterion is submodular (Alexanderian 2021; Wu, Chen & Ghattas 2023; Krause, Singh & '
        'Guestrin 2008). Correlated measurement errors break submodularity and make the usual weighting of the '
        'likelihood overstate the information; virtual-noise and noise-inflation relaxations repair the optimisation '
        '(Liu et al. 2016; Uciński 2020; Attia & Constantinescu 2022; Pázman, Hainy & Müller 2022). Robust designs '
        'guard against an uncertain error model by maximising the worst case (Attia, Leyffer & Munson 2023; Chowdhary, '
        'Attia & Alexanderian 2025), and recent work places several sensor types (Maio et al. 2026) and designs '
        'networks for tsunami early warning (Venkat, Henneking & Ghattas 2026). Two gaps remain. First, robust designs '
        'carry no measure of how far they are from the optimum. Second, every method takes the correlated errors as '
        'given, while in groundwater networks their main sources — air pressure acting through the barometric '
        'efficiency, and logger drift — are routinely removed record by record with a nearby barometer (Rasmussen & '
        'Crawford 1997; Toll & Rasmussen 2007) but are never part of the network design. CERTAIN-COAST closes both: '
        'its monitoring design places reference channels with the piezometers, corrects the interference by '
        'marginalisation, chooses the network against the worst plausible error, and certifies how far each '
        'network is from the best possible one.']))
    A(('h2', '7.2 Methodology (monitoring design, work package on observations)'))
    A(('box', [
        f'The monitoring network of each site is designed with NDERHYRJA-GO. A linearised model of the coupled system '
        f'gives, after one adjoint solve per candidate, the data-space matrices of the design problem. The candidates '
        f'are the piezometers, salinity probes and the reference channels — one barometer per site and one sealed '
        f'channel per logger hub — and the error model includes the air pressure acting through each well\'s '
        f'barometric efficiency, logger drift, cable cross-talk and model error, each within a range estimated from '
        f'the first months of records. Greedy selection and exchange choose the network against the worst plausible '
        f'error; a certified bound states how far it is from the best possible network. In operation, every reading is '
        f'corrected for air pressure and drift before it enters the forecast, and the corrected residuals are checked '
        f'for remaining correlation. In tests, this design raised the worst-case information of a {k}-sensor network by '
        f'{s["gain_indep"]} over the classical design and kept the 90% forecast intervals calibrated '
        f'({s["cov_nderhyrja_robust"]} coverage, against {s["cov_indep_ignore"]} when the interference is ignored).']))
    A(('h2', '7.3 Deliverable, indicators and field plan'))
    A(('b', '**Deliverable.** "Certified monitoring design for the pilot sites: network layout with reference channels, '
            'interference-correction software and a design report stating the certified optimality gap of every '
            'network" (month 9, with the design of the network).'))
    A(('b', '**Indicator 1.** Certified optimality gap of every deployed network ≤ 25% of the certified bound '
            f'(test bed: {s["gap_k"]} at $k$ = {k}).'))
    A(('b', f'**Indicator 2.** Coverage of the 90% warning intervals between 88% and 95% in the live year, after '
            f'correction (test bed: {s["cov_nderhyrja_robust"]}).'))
    A(('b', f'**Indicator 3.** Root-mean-square error of the corrected heads against manual dips ≤ 3 cm and at most '
            f'half that of the raw readings (test bed: {s["hc_nderhyrja_robust"]} cm against '
            f'{s["hr_nderhyrja_robust"]} cm).'))
    A(('b', '**Field plan.** One barometer per site, logging at the same interval as the transducers; a sealed '
            'reference channel on each logger hub; barometric efficiencies (or lagged response functions) estimated '
            'from the first three months by regression deconvolution (W1, W2); vented cables where the budget allows, '
            'since they remove the air-pressure term at its source, and the design then decides whether the barometer '
            'is still worth its place.'))
    # ---------------------------------------------------------------------------------------------- 8 limitations
    A(('h', '8. Limitations'))
    for t in [
        '**Linear-Gaussian test bed.** The aquifer response is linear and synthetic, and the error amplitudes are '
        'illustrative. With a nonlinear model the criterion must be replaced by the bracket or the Laplace surrogate of '
        'A2 and A1; Propositions N1–N3 then hold for the linearised problem.',
        '**The worst case is the worst found.** Amplitudes are exact (Proposition N3), but the shape parameters are '
        'searched by a multi-start local optimiser, as in A1. The certificate holds with respect to the final scenario '
        'set, which includes every worst case found.',
        f'**Certificates are loose for small networks** ({s["gap_hi"]} at $k$ = {s["ks"][0]}), and greedy with exchange '
        f'is a heuristic: it matched the exhaustive optimum in {s["small_exact"]} of {s["small_cnt"]} small cases, '
        f'which does not show that it always does; the certificate is what bounds its shortfall.',
        '**The interference model is a choice.** A constant barometric efficiency with a bounded error stands for '
        'responses that can be lagged (W1, W2); earth tides, temperature effects on salinity probes and sensor '
        'failures are not modelled. Each can be added as a further correctable source with its own reference channel.',
        '**Static design.** One network is chosen for a stationary error model; sequential redesign as records '
        'accumulate is left for the project.']:
        A(('b', t))
    A(('refs',))
    return BL


def x_wf(B):
    x0, x1, y0, y1 = B['wellfield']
    return f'$x$ = {x0:.2f}–{x1:.2f}, $y$ = {y0:.2f}–{y1:.2f}'
