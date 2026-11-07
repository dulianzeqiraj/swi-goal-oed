"""Text of the eleventh state-of-the-art review (English): warnings for what happens between samples. The path-dependent
neural jump ODE (Krach, Nübel & Teichmann) and robust pricing with neural SDEs (Gierjatowicz, Sabate-Vidales, Šiška,
Szpruch & Žurič) extracted; the state of the art for the NATO proposal; our scheme; and SHTEGU-GO. blocks(R) returns the
block list; every number comes from res/shtegu.json. Conventions: $inline math$, **bold**, *italic*, [text](url)
hyperlink, [[key]] equation number, {{key}} figure or table number."""
import math

A1_URL = 'https://doi.org/10.1016/j.spa.2026.105058'
A1_ARX = 'https://arxiv.org/abs/2206.14284'
A1_CODE = 'https://github.com/FlorianKrach/PD-NJODE'
A2_URL = 'https://ssrn.com/abstract=3646241'
A2_CODE = 'https://github.com/msabvid/robust_nsde'

ANCHORS = [
    dict(key='A1', text='Krach, F., Nübel, M., & Teichmann, J. (2026). Optimal estimation of generic dynamics by path-dependent '
                        'neural jump ODEs. Stochastic Processes and their Applications (published version: '
                        'doi.org/10.1016/j.spa.2026.105058); arXiv:2206.14284v7, 25 August 2026 (PDF provided by the user, '
                        '55 pages). Code: github.com/FlorianKrach/PD-NJODE.', url=A1_URL),
    dict(key='A2', text='Gierjatowicz, P., Sabate-Vidales, M., Šiška, D., Szpruch, L., & Žurič, Ž. (2020). Robust pricing and '
                        'hedging via neural SDEs. Working paper dated 8 July 2020, SSRN 3646241 (PDF provided by the user, '
                        '34 pages). Code: github.com/msabvid/robust_nsde.', url=A2_URL),
]
RA = [   # as listed in A1
    dict(key='R1', text='Herrera, C., Krach, F., & Teichmann, J. (2021). Neural jump ordinary differential equations: '
                        'consistent continuous-time prediction and filtering. International Conference on Learning '
                        'Representations (ICLR 2021).', url=None),
    dict(key='R2', text='Rubanova, Y., Chen, R. T. Q., & Duvenaud, D. (2019). Latent ordinary differential equations for '
                        'irregularly-sampled time series. Advances in Neural Information Processing Systems 32, 5320–5330.', url=None),
    dict(key='R3', text='De Brouwer, E., Simm, J., Arany, A., & Moreau, Y. (2019). GRU-ODE-Bayes: continuous modeling of '
                        'sporadically-observed time series. Advances in Neural Information Processing Systems 32, 7379–7390.',
         url=None),
    dict(key='R4', text='Kidger, P., Morrill, J., Foster, J., & Lyons, T. (2020). Neural controlled differential equations for '
                        'irregular time series. Advances in Neural Information Processing Systems 33.', url=None),
    dict(key='R5', text='Morrill, J., Salvi, C., Kidger, P., & Foster, J. (2021). Neural rough differential equations for long '
                        'time series. International Conference on Machine Learning, PMLR.', url=None),
    dict(key='R6', text='Andersson, W., Heiss, J., Krach, F., & Teichmann, J. (2024). Extending path-dependent NJ-ODEs to noisy '
                        'observations and a dependent observation framework. Transactions on Machine Learning Research.',
         url=None),
    dict(key='R7', text='Bain, A., & Crisan, D. (2009). Fundamentals of Stochastic Filtering. Springer.', url=None),
    dict(key='R8', text='Chevyrev, I., & Kormilitzin, A. A primer on the signature method in machine learning (as cited in '
                        'A1).', url=None),
]
RB = [   # as listed in A2
    dict(key='B1', text='Hobson, D. G. (1998). Robust hedging of the lookback option. Finance and Stochastics 2(4), 329–347.',
         url=None),
    dict(key='B2', text='Beiglböck, M., Henry-Labordère, P., & Penkner, F. (2013). Model-independent bounds for option prices: '
                        'a mass transport approach. Finance and Stochastics 17(3), 477–501.', url=None),
    dict(key='B3', text='Cox, A. M., & Obłój, J. (2011). Robust hedging of double touch barrier options. SIAM Journal on '
                        'Financial Mathematics 2(1), 141–182.', url=None),
    dict(key='B4', text='Dupire, B. (1994). Pricing with a smile. Risk 7(1), 18–20.', url=None),
    dict(key='B5', text='Cuchiero, C., Khosrawi, W., & Teichmann, J. (2020). A generative adversarial network approach to '
                        'calibration of local stochastic volatility models. arXiv:2005.02505.', url=None),
    dict(key='B6', text='Eckstein, S., Guo, G., Lim, T., & Obłój, J. (2019). Robust pricing and hedging of options on multiple '
                        'assets and its numerics. arXiv:1909.03870.', url=None),
    dict(key='B7', text='Buehler, H., Gonon, L., Teichmann, J., & Wood, B. (2019). Deep hedging. Quantitative Finance, 1–21.',
         url=None),
    dict(key='B8', text='Hernandez, A. (2016). Model calibration with neural networks. Risk.', url=None),
]
WEB = [
    dict(key='W1', text='Slepian, D. (1962). The one-sided barrier problem for Gaussian noise. Bell System Technical Journal '
                        '41(2), 463–501.', url='https://doi.org/10.1002/j.1538-7305.1962.tb02419.x'),
]
OTHER = [
    dict(key='D1', text='Zeqiraj, D. (2026). Reviews I–X of this series (GARANCIA-GO … NDERHYRJA-GO), docs/literature/ in '
                        'this repository; the CERTAIN-COAST application texts and their references, docs/certain_coast/ '
                        '(conformal risk control and online calibration: Angelopoulos et al. 2024; Gibbs and Candès 2024).',
         url=None),
    dict(key='D2', text='The code of this review: experiments/shtegu_go/ (shtegu_exp.py, shtegu_figs.py; results in res/).',
         url=None),
]


def all_refs():
    return ANCHORS + RA + RB + WEB + OTHER


def f2(x):
    return f'{x:.2f}'


def p0(x):
    return f'{100 * x:.0f}%'


def fill(R):
    s = {}
    T = R['t37']
    s['p_true'] = f2(T['p_true'])
    s['p_marg'] = f'{T["p_marginal"]:.3f}'
    s['ratio'] = f'{T["p_true"] / T["p_marginal"]:.0f}'
    s['curve0'] = f'{T["curve"][0]:.3f}'
    s['tmax'] = f'{1 / T["kgrid"][0]:.0f}'
    D = T['designs']
    for n, k in (('quarterly samples', 'q'), ('monthly samples', 'm'), ('weekly samples', 'w'), ('daily logger', 'l')):
        d = D[n]
        s[k + '_lo'], s[k + '_hi'] = f2(d['plo_med']), f2(d['phi_med'])
        s[k + '_open'] = p0(d['open_upper'])
        s[k + '_cov'] = p0(d['coverage'])
        s[k + '_seen'] = f'{100 * d["seen_mean"]:.1f}%'
        s[k + '_crb'] = (f'{d["crb_rel_se"]:.0f}' if d['crb_rel_se'] > 10 else f'{d["crb_rel_se"]:.3g}')
        s[k + '_n'] = d['n_samples']
        s[k + '_tlo'] = f'{1 / d["khi_med"]:.1f}' if d['khi_med'] < 3.9 else '0.25'
        s[k + '_thi'] = f'{1 / d["klo_med"]:.0f}'
    covs = [D[n]['coverage'] for n in D]
    s['cov_lo'], s['cov_hi'] = p0(min(covs)), p0(max(covs))
    kt = R['setup']['kappa_true']
    s['tcorr'] = f'{1 / kt:.0f}'
    s['rho_q'] = f'{math.exp(-kt * D["quarterly samples"]["step"]):.0e}'.replace('e-0', '\\cdot10^{-') + '}'
    s['l_bound'] = f'{math.sqrt(2 / (D["daily logger"]["n_samples"] - 1)):.3f}'
    s['l_pairs'] = D['daily logger']['n_samples'] - 1
    s['l_crb3'] = f'{D["daily logger"]["crb_rel_se"]:.3f}'
    C = R['checks']
    s['chk'] = C
    U = R['t38']
    s['b_true'] = f2(U['p_true'])
    s['b_marg'] = f"{U['marginals_only']['lo']:.2f}–{U['marginals_only']['hi']:.2f}"
    for n, k in (('quarterly samples', 'q'), ('monthly samples', 'm'), ('weekly samples', 'w'), ('daily logger', 'l')):
        d = U['designs'][n]
        s['b' + k] = f"{d['lo']:.2f}–{d['hi']:.2f}"
        s['bn' + k] = d['n']
    V = R['t39']
    L = V['daily logger']
    s['c_raw'] = p0(L['raw_all'])
    s['c_skew'] = p0(L['raw_high_skew'])
    s['c_cert'] = f"{100 * L['cert_split_mean']:.1f}%"
    s['c_p10'], s['c_p90'] = p0(L['cert_split_p10']), p0(L['cert_split_p90'])
    s['c_delta'] = f"{L['delta_split_median']:.3f}"
    s['c_w0'] = f2(L['width_raw'])
    s['c_w1'] = f2(L['width_raw'] + 2 * L['delta_split_median'])
    s['c_mw'] = f2(V['monthly samples']['width_raw'])
    s['c_ww'] = f2(V['weekly samples']['width_raw'])
    s['c_mraw'] = p0(V['monthly samples']['raw_all'])
    s['c_wraw'] = p0(V['weekly samples']['raw_all'])
    s['J'] = L['J']
    W = R['t40']
    names = [n for n in W if n not in ('climatology', 'N')]
    s['sk'] = [f"{100 * W[n]['skill']:.1f}%" for n in names]
    s['rate'] = p0(W['climatology']['rate'])
    s['N40'] = W['N']
    return s


def blocks(R):
    s = fill(R)
    C = s['chk']
    S = R['setup']
    BL = []
    A = BL.append
    A(('title', 'State of the art XI: warnings for what happens between samples'))
    A(('subtitle', 'The path-dependent neural jump ODE (Krach, Nübel & Teichmann, Stochastic Processes and their '
                   'Applications 2026) and robust pricing and hedging with neural SDEs (Gierjatowicz, Sabate-Vidales, '
                   'Šiška, Szpruch & Žurič, 2020), extracted; what they teach about forecasting from irregular records '
                   'under model uncertainty; the state of the art for the NATO proposal; and SHTEGU-GO, certified warnings '
                   'for the crossings that sparse samples never see'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation · companion to reviews '
                 'I–X'))
    # ------------------------------------------------------------------------------------------- 1
    A(('h', '1. Outcome'))
    A(('bbox', [
        '**The two documents, extracted** (Section 2). A1 learns the best possible forecast, the conditional expectation '
        'given what has been observed, from irregular and incomplete records of a generic, possibly path-dependent '
        'process, and proves that its neural jump ODE converges to it. A2 calibrates neural SDEs to the prices of liquid '
        'options and computes the interval of the price of an illiquid, path-dependent option over all models that fit '
        'the market, with a learned hedge as control variate.',
        '**What we learn** (Section 2.3): seven lessons and one gap common to both. A1 forecasts but gives no bound for '
        'what the model family cannot identify; A2 bounds over calibrated models but gives no guarantee when the truth '
        'lies outside the family, and neither asks which measurements would close the interval.',
        f'**The analogy** (Section 4, Figure {{{{scheme}}}}). Chloride sampled every few weeks or months pins only its '
        f'marginal law — the "liquid prices". Whether it crosses the limit **between** two samples is a path functional, '
        f'like a lookback option, and the marginals do not determine it.',
        f'**Innovation: SHTEGU-GO** ("shtegu", the path; Section 5). Proposition S1: with the marginals fixed, the '
        f'probability of crossing the limit within a season grows with the speed of the dynamics (Slepian), from the '
        f'marginal tail to 1, so sparse samples alone never bound it. Proposition S2: the information a pair of samples '
        f'carries on that speed falls as $\\tau^2e^{{-2\\kappa\\tau}}$ with the lag $\\tau$. Proposition S3: the band over '
        f'all models consistent with the records (the robust price of A2) is certified with a conformal margin. '
        f'Proposition S4: the online warning is the conditional probability of A1, and it needs the path and the head '
        f'logger when the aquifer has memory.',
        f'**Numbers** (T37–T40). With a correlation time of 8 days the chloride crosses 250 mg/L within a 120-day season '
        f'with probability {s["p_true"]}, {s["ratio"]} times the marginal tail ({s["p_marg"]}); quarterly samples see a '
        f'crossing in {s["q_seen"]} of the seasons. The band that the records leave is {s["q_lo"]}–{s["q_hi"]} with '
        f'quarterly samples, {s["m_lo"]}–{s["m_hi"]} monthly, {s["w_lo"]}–{s["w_hi"]} weekly and {s["l_lo"]}–{s["l_hi"]} '
        f'with a daily logger. When chloride is skewed, the band of the Gaussian family covered the truth in only '
        f'{s["c_raw"]} of new aquifers with a logger; the conformal margin raised this to {s["c_cert"]} on average. The '
        f'online warning gained {s["sk"][2]} in Brier skill with the head logger, against {s["sk"][1]} from the sample '
        f'path alone.',
        '**For the proposal** (Section 7): text for the state of the art and the methodology, two indicators and a '
        'sampling plan that measures the time scale of chloride at each wellfield.']))
    # ------------------------------------------------------------------------------------------- 2
    A(('h', '2. The two documents, extracted'))
    A(('h2', '2.1 Optimal estimation of generic dynamics by path-dependent neural jump ODEs (A1)'))
    A(('p', f'Florian Krach, Marc Nübel and Josef Teichmann (ETH Zurich), *Stochastic Processes and their Applications*, '
            f'2026 ([published version]({A1_URL}); [arXiv:2206.14284v7]({A1_ARX}), 25 August 2026, 55 pages; '
            f'[code]({A1_CODE})). **The problem is online forecasting**: at every time, predict a stochastic process from '
            f'the observations made so far, which arrive at random, irregular times and may cover only some of its '
            f'coordinates. The process $X$ is a generic adapted càdlàg process — possibly non-Markovian, path-dependent or '
            f'with jumps — observed at random times $t_i$ with masks $M_i\\in\\{{0,1\\}}^{{d_X}}$ that say which coordinates '
            f'were seen. The information is $\\mathcal A_t=\\sigma(X_{{t_i,j}},t_i,M_{{t_i}}:t_i\\le t,\\ M_{{t_i,j}}=1)$, and '
            f'the optimal forecast in $L^2$ is the conditional expectation $\\hat X_t=E[X_t\\text{{ | }}\\mathcal A_t]$ '
            f'(Section 2.4 of A1).'))
    A(('p', '**The model** (Definition 3.13, Algorithm 1). A latent state $H_t$ follows a neural ODE between observations '
            'and jumps at each observation through a second network; the output $Y_t=\\tilde g(H_t)$ is the forecast. Its '
            'inputs are the current time, the time of the last observation, the truncated **signature** of the interpolated '
            'observation path $\\tilde X^{\\le\\tau(t)}$ — which carries the whole observed past — the initial value, the '
            'running maximum, the number of observations and the time since the last one. **The loss** compares the output '
            'with the observed coordinates, after and before each jump:'))
    A(('eq', 'a1loss', ['\\Psi(Z)=E\\Big[\\frac{1}{n}\\sum_{i=1}^{n}\\big(\\lvert M_i\\odot(X_{t_i}-Z_{t_i})\\rvert_2+\\lvert M_i'
                        '\\odot(Z_{t_i}-Z_{t_i-})\\rvert_2\\big)^2\\Big],']))
    A(('p', 'and in practice an equivalent loss with $X_{t_i}-Z_{t_i-}$ in the second term, which trains more stably '
            '(Remark 4.10 of A1). **The guarantee** (Theorems 4.1 and 4.6): under Assumptions 1–6 — the observation '
            'times and masks independent of the process, every coordinate observable with positive probability, '
            'observation times that do not cluster, and integrability and regularity of the conditional expectation — '
            'the conditional expectation is the unique minimiser of $\\Psi$, and the trained model converges to it as '
            'the networks, the signature level and the number $N$ of training paths grow. The conditional variance and '
            'moments follow by feeding $X^2$ or $e^{uX}$ as extra coordinates (Section 5); the stochastic filtering '
            'problem — a signal never observed at test time — is solved by training on simulated pairs of signal and '
            'observations in which the signal is revealed with probability $p_k\\in(0,1)$ (Section 6). A companion paper '
            'extends the theory to noisy observations and to observation times that depend on the process (R6).'))
    A(('p', '**The experiments** (Section 8 and Appendix C). A Poisson point process (metric below $2\\cdot10^{-5}$ after '
            '30 epochs); a Brownian motion and its square for uncertainty bands (below $5\\cdot10^{-5}$); a fractional '
            'Brownian motion with Hurst parameter 0.05, where PD-NJ-ODE has the best metric, two intermediate variants '
            'about twice it and the original NJ-ODE about 16 times it; a correlated two-dimensional Brownian motion '
            'observed one coordinate at a time ($5.2\\cdot10^{-3}$), where the forecast of one coordinate reacts to '
            'observations of the other; filtering of a Brownian motion in Brownian noise ($5.4\\cdot10^{-4}$); PhysioNet '
            'patient records (test MSE $1.930\\cdot10^{-3}$ against $1.945\\cdot10^{-3}$ for NJ-ODE and '
            '$2.208\\cdot10^{-3}$ for the best latent ODE); and limit-order-book data of Bitcoin and Ethereum, where it '
            'extracts a little more than the stationary prediction while linear models and random forests overfit the '
            'noise.'))
    A(('p', '**What it leaves open, for us.** (1) It needs $N$ independent sample paths of the process; one coastal '
            'aquifer is one path, so the training paths must come from simulated aquifers, as in its filtering setting. '
            '(2) Its guarantee is asymptotic convergence in $L^2$, not a coverage statement for a finite record. (3) It '
            'forecasts the process; a warning needs a functional of the future path — whether the limit is crossed — '
            'and a bound when the dynamics are not identified by the data.'))
    A(('h2', '2.2 Robust pricing and hedging via neural SDEs (A2)'))
    A(('p', f'Patryk Gierjatowicz, Marc Sabate-Vidales, David Šiška and Lukasz Szpruch (Edinburgh, Vega Protocol, Alan '
            f'Turing Institute) and Žan Žurič (Imperial College London), working paper of 8 July 2020 '
            f'([SSRN 3646241]({A2_URL}); [code]({A2_CODE})). **The problem is model uncertainty**: many models reproduce '
            f'the prices of the liquid options, but they disagree about the price of an illiquid, path-dependent one. The '
            f'model is an SDE whose drift and diffusion are neural networks, $dX^\\theta_t=b(t,X^\\theta_t,\\theta)dt+'
            f'\\sigma(t,X^\\theta_t,\\theta)dW_t$, with the traded asset a martingale under the pricing measure. It is '
            f'calibrated to the liquid prices $p(\\Phi_i)$ and then pushed to the lowest and the highest price of the '
            f'illiquid payoff $\\Psi$ that the calibration allows:'))
    A(('eq', 'a2', ['\\inf_{\\theta}E^{Q(\\theta)}[\\Psi]\\ \\ \\text{and}\\ \\ \\text{sup}_{\\theta}E^{Q(\\theta)}[\\Psi]\\quad\\text{subject to}\\quad\\sum_{i=1}^{M}\\ell\\big('
                    'E^{Q(\\theta)}[\\Phi_i],p(\\Phi_i)\\big)=0,']))
    A(('p', 'solved by an augmented Lagrangian (Algorithms 2 and 3). Three devices make it work. **A learned hedge as '
            'control variate**: by the martingale representation theorem $\\Phi-\\int_0^TZ_sdW_s$ has the same mean and '
            'smaller variance, and a network learns $Z$ (eq. 2.4); since the mini-batch gradient of the calibration loss is '
            'biased, with a bias bounded by $\\frac{2}{N}\\operatorname{Var}^{1/2}[\\Phi^{cv}]\\,\\operatorname{Var}^{1/2}[\\partial_'
            '\\theta\\Phi]$ for the square loss (Theorem 3.2), the hedge also reduces the bias. **A tamed Euler scheme** '
            'prevents moment blow-up of neural coefficients (eq. 2.7). **A randomised, dropout-like training** that '
            'differentiates one maturity at a time keeps memory constant and is unbiased (Theorem 4.1). The experiments '
            'calibrate local-volatility and local-stochastic-volatility neural SDEs (four hidden layers of 50 units per '
            'maturity) to European options with maturities of 2–12 months and 21 strikes, with calibration errors of '
            'order $10^{-9}$ to $10^{-4}$; ten runs from different initialisations, unconstrained and pushed to the '
            'lower and upper bound, give a range of prices for a lookback option $\\max_tS_t-S_T$; the hedging error '
            'of the lookback was $E[s^2]=1.6\\cdot10^{-3}$ over 400,000 paths.'))
    A(('p', '**What it leaves open, for us.** (1) The interval is over one parametric family; it is not a guarantee if '
            'reality lies outside it, and with too little information the class of calibrated models makes the bounds '
            'too wide to use (B6, cited in A2). (2) It does not say which additional observation would narrow the '
            'interval. (3) It is set in finance, with liquid prices observed every day; a coastal aquifer offers a few '
            'irregular samples a year.'))
    A(('h2', '2.3 What we learn'))
    for i, t in enumerate([
        '**Forecast the conditional expectation, and train on what is observed, when it is observed** (A1). The loss '
        'uses only the observed coordinates at the observation times, so gaps and partial observations need no '
        'imputation.',
        '**Carry the whole observed path** (A1). For processes with memory the last value is not enough; the signature '
        'of the observed path restores the information (16 times lower error than the Markov NJ-ODE on fractional '
        'Brownian motion).',
        '**Use a second coordinate observed at other times** (A1, correlated Brownian motion). A logger that sees part of '
        'the state sharpens the forecast of a coordinate sampled rarely.',
        '**Train on simulated pairs when the target is never observed** (A1, filtering). This is how a warning for an '
        'unmeasured quantity can be trained from a calibrated simulator.',
        '**Fitting the data does not fix a path functional** (A2). Models calibrated to the same liquid prices disagree '
        'about a lookback; report the interval over all calibrated models, not one model\'s value.',
        '**Reduce variance to reduce bias** (A2, Theorem 3.2). A control variate makes the stochastic calibration and '
        'the bound computation faster and less biased.',
        '**Know when the interval is too wide** (A2, B6). With too little information the robust interval says nothing; '
        'the remedy is more information, not more modelling.',
        '**The common gap.** Neither document certifies its answer for a single, finite record when the truth is outside '
        'the model family, and neither asks which observation would close the gap. For a warning system both are the '
        'point: the warning must state how often it misses, and the monitoring design must buy the observation that '
        'makes the warning informative.'], 1):
        A(('b', f'{i}. {t}'))
    # ------------------------------------------------------------------------------------------- 3
    A(('h', '3. State of the art'))
    A(('p', 'Table {{sota}} places the two documents among the lines of work a NATO reviewer will expect. Sources marked R '
            'are cited as A1 lists them, B as A2 lists them, W was checked against the publisher record; D are the '
            'project documents.'))
    A(('cap', 'Table {{sota}}. Forecasting from irregular records and robust bounds: lines of work, what they give, and '
              'what they leave open for CERTAIN-COAST.'))
    A(('table', ['Line of work', 'Sources', 'What it gives', 'Open for CERTAIN-COAST'], [
        ['Irregular time series with neural ODEs', 'R2, R3, R4, R5', 'Latent ODEs, GRU-ODE-Bayes, neural CDEs and rough '
                                                                     'DEs for sporadic data', 'No convergence guarantee '
                                                                                              'for online forecasts'],
        ['Neural jump ODEs', 'R1, A1, R6', 'Online forecasts that converge to the conditional expectation, with jumps, '
                                           'memory, incomplete and noisy observations', 'Needs many paths; no finite-'
                                                                                         'record coverage'],
        ['Stochastic filtering', 'R7, A1', 'Conditional law of an unobserved signal', 'Needs the joint law of signal and '
                                                                                      'observations'],
        ['Robust pricing, optimal transport', 'B1, B2, B3, B6', 'Model-independent bounds for path-dependent options from '
                                                                'liquid prices', 'Bounds often too wide; no data design'],
        ['Calibration with neural networks', 'B4, B5, B8, A2', 'Neural local and stochastic volatility; calibrated '
                                                               'intervals for exotics', 'Interval within one family'],
        ['Hedging and control variates', 'B7, A2', 'Learned hedges that reduce variance and bias', 'Not a decision for '
                                                                                                   'an aquifer'],
        ['Gaussian extremes', 'W1', 'Slepian\'s inequality: a weaker correlation raises the chance of exceeding a level',
         'Not used to bound warnings from samples'],
        ['Guaranteed warnings', 'D1', 'Conformal risk control and online calibration (in the CERTAIN-COAST form)',
         'Calibrate observed outcomes, not crossings between samples'],
    ], [3.4, 2.2, 6.0, 5.4], 9))
    A(('p', 'The pattern of the table is the case for the innovation. The forecasting literature has the optimal '
            'online predictor but not its bound, and the robust-pricing literature has the bound but not its certificate '
            'or the observation that would tighten it. A coastal warning needs all three, for an event — the chloride '
            'crossing its limit between two samples — that the samples themselves rarely see.'))
    # ------------------------------------------------------------------------------------------- 4
    A(('h', '4. Our scheme: what happens between samples at a CERTAIN-COAST wellfield'))
    A(('img', 'scheme', 17.0))
    A(('cap', 'Figure {{scheme}}. (a) The analogy between robust pricing (A2) and a coastal warning. (b) One season of '
              'simulated chloride with monthly samples: the limit is crossed between samples, and the online forecast '
              '(the conditional expectation of A1 for an Ornstein–Uhlenbeck chloride) jumps at each sample and decays '
              'towards the mean between them.'))
    A(('p', f'The water utility samples chloride at the wellfield wells for laboratory analysis; conductivity loggers, '
            f'where they exist, read every few minutes. Chloride responds to pumping cycles, tides and storms within days, '
            f'and to recharge over months. Write its standardised anomaly as a stationary process with marginal law '
            f'$N(0,1)$, mean {S["mu"]:.0f} mg/L and standard deviation {S["sd"]:.0f} mg/L, so that the limit of '
            f'{S["limit"]:.0f} mg/L sits at $z={S["z0"]:.1f}$. The warning quantity is'))
    A(('eq', 'target', ['p=P\\Big(\\text{sup}_{0\\le t\\le T}c_t\\ge z\\Big),\\qquad T=120\\ \\text{days},']))
    A(('p', 'the probability that the limit is crossed at some time within a season, observed or not. The sampling '
            'campaigns pin the marginal law of $c$ at the sampling dates — the "vanilla prices"; $p$ is the "lookback". '
            'Table {{analogy}} completes the correspondence.'))
    A(('cap', 'Table {{analogy}}. Robust pricing and coastal warnings.'))
    A(('table', ['Robust pricing (A2)', 'CERTAIN-COAST', 'Consequence'], [
        ['Liquid option prices', 'Chloride statistics at the sampling dates', 'Pin the marginal law'],
        ['Illiquid lookback option', 'Crossing of the limit within the season', 'A path functional'],
        ['Neural SDEs calibrated to the market', 'Aquifer models consistent with the records', 'Many models fit'],
        ['Robust price interval', 'Band of the warning probability', 'Report the band, not one value'],
        ['Hedge as control variate', 'Analytic forecast as control variate; pumping as the lever', 'Cheaper, less biased'],
        ['Irregular order-book updates (A1)', 'Irregular samples, logger gaps', 'Train on observed coordinates'],
    ], [4.8, 5.8, 6.4], 9))
    # ------------------------------------------------------------------------------------------- 5
    A(('h', '5. SHTEGU-GO: certified warnings for what happens between samples'))
    A(('h2', '5.1 The marginals do not bound the crossing'))
    A(('prop', 'Proposition S1 (Slepian ordering and the vacuous band).',
            'Let $c$ be a stationary Ornstein–Uhlenbeck anomaly with marginal law $N(0,1)$ and correlation '
            '$E[c_sc_t]=e^{-\\kappa\\lvert t-s\\rvert}$. Then $p(\\kappa)=P(\\text{sup}_{[0,T]}c\\ge z)$ is non-decreasing in '
            '$\\kappa$, with'))
    A(('eq', 's1', ['\\lim_{\\kappa\\to0}p(\\kappa)=1-\\Phi(z),\\qquad\\lim_{\\kappa\\to\\infty}p(\\kappa)=1.']))
    A(('p', 'Hence, over all models consistent with the marginal law, the band of the warning probability is '
            '$1-\\Phi(z)\\le p<1$: the samples that pin the marginals bound the crossing only from below, by the marginal tail, '
            'and not at all from above. The same holds for any stationary Gaussian family whose correlations can be made '
            'arbitrarily small at positive lags.'))
    A(('proof', 'Slepian\'s inequality (W1): for centred Gaussian processes with equal variances, if $E[X_sX_t]\\ge '
                'E[Y_sY_t]$ for all $s,t$ then $P(\\text{sup} X\\ge z)\\le P(\\text{sup} Y\\ge z)$ (for continuous processes through finite '
                'grids). Since $e^{-\\kappa\\lvert t-s\\rvert}$ decreases in $\\kappa$, $p$ is non-decreasing. As $\\kappa\\to0$, '
                '$\\text{sup}_{[0,T]}\\lvert c_t-c_0\\rvert\\to0$ in probability, so $p\\to P(c_0\\ge z)$. As $\\kappa\\to\\infty$, the '
                'values at $m$ points spaced $T/m$ apart become independent, their maximum exceeds $z$ with probability '
                '$1-\\Phi(z)^m$, and $m$ can be taken as large as desired.'))
    A(('h2', '5.2 What a pair of samples says about the time scale'))
    A(('prop', 'Proposition S2 (information decays with the lag).',
            'For the stationary Ornstein–Uhlenbeck anomaly, one transition over a lag $\\tau$ carries the Fisher '
            'information'))
    A(('eq', 's2', ['I_\\tau(\\kappa)=\\frac{\\tau^2\\rho^2(1+\\rho^2)}{(1-\\rho^2)^2},\\qquad\\rho=e^{-\\kappa\\tau},']))
    A(('p', 'about $\\kappa$. It decreases in $\\tau$ from $1/(2\\kappa^2)$ at $\\tau\\to0$ and falls as $2\\tau^2e^{-2\\kappa\\tau}$ '
            'for $\\tau\\gg1/\\kappa$. A record of $n$ transitions at lags $\\tau_i$ cannot give $\\kappa$ a relative '
            'standard error below $\\big(\\kappa^2\\sum_iI_{\\tau_i}(\\kappa)\\big)^{-1/2}\\ge\\sqrt{2/n}$.'))
    A(('proof', 'In standardised form $c_{t+\\tau}\\text{ | }c_t\\sim N(\\rho c_t,1-\\rho^2)$. For this autoregression the '
                'Fisher information about $\\rho$ is $(1+\\rho^2)/(1-\\rho^2)^2$; the chain rule with $d\\rho/d\\kappa=-\\tau\\rho$ '
                'gives [[s2]]. Its limit at small $\\tau$ follows from $1-\\rho^2\\approx2\\kappa\\tau$; transitions of a Markov '
                'chain add their information, and $I_\\tau\\le1/(2\\kappa^2)$ gives the bound.'))
    A(('p', f'With quarterly samples and a correlation time of {s["tcorr"]} days, $\\rho={s["rho_q"]}$: the record says '
            f'that chloride decorrelates between samples, but not how fast, and the upper end of the band of S1 stays at '
            f'1. A daily logger ($n={s["l_pairs"]}$ transitions) comes close to the bound: a relative standard error of '
            f'{s["l_crb3"]} against $\\sqrt{{2/n}}={s["l_bound"]}$.'))
    A(('h2', '5.3 The band over all consistent models, certified'))
    A(('prop', 'Proposition S3 (certified robust band).',
            'Let $\\Theta(D)$ be the models of a family whose statistics match those of the record $D$ within their '
            'sampling error, and $B(D)=[\\min_{\\Theta(D)}p_\\theta,\\ \\max_{\\Theta(D)}p_\\theta]$ the robust band (the '
            'interval of A2 with the record statistics as liquid prices). Let $D_1,\\dots,D_J$ be records of aquifers '
            'drawn from a broader law — a calibrated simulator with its misspecifications, or measured anchor periods — '
            'with true probabilities $p_j$ and distances $d_j=\\operatorname{dist}(p_j,B(D_j))$, and $\\delta$ the '
            '$k$-th smallest $d_j$, with $k$ the smallest integer not below $(J+1)(1-\\alpha)$. For a new aquifer drawn from the same law,'))
    A(('eq', 's3', ['P\\big(p\\in[\\min B(D)-\\delta,\\ \\max B(D)+\\delta]\\big)\\ \\ge\\ 1-\\alpha.']))
    A(('proof', 'The new distance and $d_1,\\dots,d_J$ are exchangeable, so the rank of the new one is uniform on '
                '$\\{1,\\dots,J+1\\}$ (ties broken at random), and it is at most the $k$-th with '
                'probability at least $1-\\alpha$.'))
    A(('p', 'The margin is zero when the family contains the truth and the band is wide; it is what a narrow band pays '
            'for being computed in a family that is too small. As in reviews I–VI, the guarantee holds for the law of the '
            'calibration aquifers; anchor periods measured at the site make it hold for the site.'))
    A(('h2', '5.4 The online warning'))
    A(('prop', 'Proposition S4 (the warning as a conditional probability).',
            'Among all forecasts adapted to the information $\\mathcal A_t$ of irregular, incomplete records, the one that '
            'minimises the expected squared error against the event "the limit is crossed after $t$ and by $t+H$" is'))
    A(('eq', 's4', ['p_t=P\\Big(\\text{sup}_{t<s\\le t+H}c_s\\ge z\\ |\\ \\mathcal A_t\\Big).']))
    A(('p', 'For a Markov chloride observed in full, $p_t$ depends only on the last sample and the time since it, so it '
            'jumps at each sample and evolves deterministically between samples — the structure of the neural jump ODE. '
            'When chloride is the sum of a fast (pumping, tide) and a slow (recharge) component, $p_t$ depends on the '
            'whole observed path and on any other coordinate that sees the slow part, such as a head logger observed at '
            'other times.'))
    A(('proof', 'The conditional expectation of the indicator minimises the squared error among $\\mathcal A_t$-measurable '
                'forecasts (as for $\\hat X$ in Section 2.4 of A1). For a Markov process the future given $\\mathcal A_t$ '
                'depends on the last observed state and the elapsed time only; for the sum of two independent Markov '
                'components the observed chloride is not Markov, and the slow component is estimated better from the '
                'path and from the head.'))
    A(('h2', '5.5 The algorithm'))
    A(('box', [
        '**SHTEGU-GO.** *Input:* the warning event (the limit crossed within the season or within $H$ days), the sampling '
        'design, and a simulator family (the coupled model of CERTAIN-COAST with its uncertain parameters, or a '
        'flexible SDE family).',
        '**1. Statistics.** From the record, compute what the design can see: the marginal law at the sampling dates, the '
        'correlations at the lags it samples, and the logger features where a logger exists, each with its sampling '
        'error.',
        '**2. Robust band.** Simulate the family with exact Brownian-bridge maxima between time steps; keep the models '
        'whose statistics match within their error; report the lowest and the highest crossing probability (the inf and '
        'sup of A2).',
        '**3. Certify.** Add the conformal margin of Proposition S3 from simulated aquifers of a broader law or from '
        'measured anchor periods.',
        '**4. Design.** If the band is too wide to act on, add the observation that identifies the time scale — a '
        'conductivity logger, or pairs of samples a few days apart — as Proposition S2 prescribes, and recompute.',
        '**5. Operate.** Train the online warning $p_t$ on simulated irregular records with the squared-error loss (the '
        'principle of A1), with the observed path and the head logger as inputs; issue $p_t$ with its certified band.']))
    A(('box', '**INNOVATION.** SHTEGU-GO turns the robust bounds of mathematical finance and the online forecasts of '
              'neural jump ODEs into certified warnings for an event the samples rarely see: the crossing of a limit '
              'between two samples. (1) It shows that sparse sampling, which fixes only the marginal law, cannot bound '
              'this crossing from above (Proposition S1, through Slepian\'s inequality). (2) It gives the information a '
              'pair of samples carries on the time scale in closed form, so the monitoring design can buy exactly the '
              'observation that closes the band (Proposition S2). (3) It computes the band over all models consistent '
              'with the records, as A2 does for an exotic option, and certifies it for a single site with a conformal '
              'margin (Proposition S3), which A2 lacks. (4) It issues the warning online as the conditional probability '
              'that A1 learns, with the observed path and a head logger as inputs (Proposition S4). To our knowledge, '
              'neither document nor the sources of Table {{sota}} bounds or certifies crossings between samples of an '
              'environmental record.'))
    # ------------------------------------------------------------------------------------------- 6
    A(('h', '6. Tests'))
    A(('p', f'**Set-up.** Seasons of {S["T"]:.0f} days, simulated in steps of {S["dt"]} day with the exact maximum of a '
            f'Brownian bridge inside each step; records of {S["years"]} years; chloride mean {S["mu"]:.0f} mg/L, standard '
            f'deviation {S["sd"]:.0f} mg/L, limit {S["limit"]:.0f} mg/L ($z={S["z0"]:.1f}$). The four designs are '
            f'quarterly, monthly and weekly laboratory samples (with ±20% jitter of the dates) and a daily logger. '
            f'**Checks.** The bridge maximum adds the crossings between grid points ({C["p_bridge"]:.3f} against '
            f'{C["p_grid"]:.3f} on the grid alone, correlation time 20 days); for a very slow chloride the crossing '
            f'probability equals the marginal tail ({C["p_slow"]:.4f} against {C["p_marginal"]:.4f}); the Fisher '
            f'information [[s2]] agrees with the variance of the simulated score ({C["fisher_mc"]:.3f} against '
            f'{C["fisher_closed"]:.3f} at a 7-day lag), and its short-lag limit is {C["fisher_short"]:.4f} '
            f'$\\approx1/(2\\kappa^2)$ in units of $1/\\kappa^2$.'))
    A(('h2', '6.1 T37: the crossing between samples, and what each design says'))
    A(('p', f'With a correlation time of 8 days (Figure {{{{t37}}}}a), the chloride crosses 250 mg/L within the season '
            f'with probability {s["p_true"]}, {s["ratio"]} times the marginal tail {s["p_marg"]}. Over correlation times '
            f'from {s["tmax"]} days to a quarter of a day the probability rises from {s["curve0"]} to 1, never decreasing, '
            f'as Proposition S1 states. Each design gives a 95% likelihood-ratio interval for the time scale, and the '
            f'interval gives a band for the crossing (Table {{{{tab37}}}}; 200 records per design). The band covered the '
            f'true probability in {s["cov_lo"]}–{s["cov_hi"]} of the records. Quarterly samples left the upper end at 1 '
            f'in {s["q_open"]} of the records, and monthly samples in {s["m_open"]}. The samples themselves saw a crossing '
            f'in only {s["q_seen"]} of the seasons when quarterly, and in {s["l_seen"]} with daily readings. The '
            f'Cramér–Rao relative standard error of the time scale (Figure {{{{t37}}}}b) is {s["q_crb"]} with quarterly '
            f'samples, {s["m_crb"]} monthly, {s["w_crb"]} weekly and {s["l_crb"]} with the logger.'))
    A(('cap', 'Table {{tab37}}. T37. Median band of the crossing probability left by each design (true value '
              f'{s["p_true"]}), the share of records whose upper end stays at 1, coverage, the share of seasons in which '
              'a sample was above the limit, and the Cramér–Rao relative standard error of the time scale.'))
    rows = []
    for n, k in (('quarterly samples', 'q'), ('monthly samples', 'm'), ('weekly samples', 'w'), ('daily logger', 'l')):
        rows.append([n, str(s[k + '_n']), f"{s[k + '_lo']}–{s[k + '_hi']}", s[k + '_open'], s[k + '_cov'], s[k + '_seen'],
                     s[k + '_crb']])
    A(('table', ['Design', 'Samples', 'Band', 'Upper end at 1', 'Coverage', 'Samples see', 'Rel. s.e.'], rows,
       [3.2, 1.8, 2.6, 2.4, 2.0, 2.4, 2.0], 9))
    A(('img', 't37', 17.0))
    A(('cap', 'Figure {{t37}}. T37. (a) Probability of crossing the limit within the season against the correlation time '
              '(Proposition S1), the marginal tail, the true time scale, and the median 95% intervals of the time scale '
              'from each design (bars at the top). (b) Fisher information about the time scale per pair of samples '
              'against their lag (Proposition S2), with the lag and the Cramér–Rao relative standard error of each design.'))
    A(('h2', '6.2 T38: the band over a richer family'))
    A(('p', f'The robust problem of A2 in our setting: chloride is the sum of a fast and a slow Ornstein–Uhlenbeck '
            f'component, $c=\\sqrt w\\,X_f+\\sqrt{{1-w}}\\,X_s$, with three free parameters, and the truth has a 3-day fast '
            f'component (weight 0.6) and a 40-day slow one. A model is consistent when its correlations at the lags a '
            f'design samples are within two standard errors of the observed ones. The band over the consistent models '
            f'(Figure {{{{t38}}}}; true probability {s["b_true"]}) is {s["b_marg"]} with the marginals only, {s["bq"]} with '
            f'quarterly samples, {s["bm"]} monthly, {s["bw"]} weekly and {s["bl"]} with a daily logger '
            f'({s["bnl"]} consistent models out of the grid). Even the logger leaves a band of a quarter of the probability '
            f'scale, because three parameters fit the same correlations at the sampled lags — the phenomenon A2 reports '
            f'for exotics under perfect calibration.'))
    A(('img', 't38', 17.0))
    A(('cap', 'Figure {{t38}}. T38. Band of the crossing probability over all two-component models consistent with the '
              'statistics each design observes; dashed: the true probability.'))
    A(('h2', '6.3 T39: certification when chloride is skewed'))
    A(('p', f'Chloride is right-skewed. The test draws {2 * s["J"]} aquifers from a broader law: a two-component anomaly '
            f'pushed through a lognormal-type skewing map, with random time scales, weights, skewness, mean and standard '
            f'deviation. For each, the band is computed with the Gaussian two-component family from the aquifer\'s own '
            f'record. Half of the aquifers calibrate the margin of Proposition S3 and half test it, over 50 random '
            f'splits (Figure {{{{t39}}}}). With monthly and weekly samples the band is wide (median widths {s["c_mw"]} and '
            f'{s["c_ww"]}) and covers the truth in {s["c_mraw"]} and {s["c_wraw"]} of the aquifers, so no margin is '
            f'needed. With a daily logger the band narrows to a median {s["c_w0"]} and its coverage falls to '
            f'{s["c_raw"]} ({s["c_skew"]} for the most skewed aquifers): the family is now too small for the precision '
            f'of the data. The conformal margin (median {s["c_delta"]}) restores a coverage of {s["c_cert"]} on average '
            f'over the splits (10–90%: {s["c_p10"]}–{s["c_p90"]}; target 90%), at a median width of {s["c_w1"]}.'))
    A(('img', 't39', 17.0))
    A(('cap', 'Figure {{t39}}. T39. (a) Coverage of the true crossing probability by the band of the Gaussian family and '
              'by the certified band, for new aquifers with skewed chloride (all aquifers for the family band; mean of 50 '
              'random splits for the certified band, bars 10–90%). (b) Daily logger, first split: bands and true '
              'probabilities of the test aquifers.'))
    A(('h2', '6.4 T40: the online warning'))
    A(('p', f'The truth is the two-component chloride; laboratory samples arrive at Poisson times (on average every 14 '
            f'days) with noise; a head logger reads the slow component daily, with noise and 20% of the days missing. At a '
            f'random time the warning is the probability that the limit (here $z=1.6$, crossed in {s["rate"]} of the '
            f'30-day windows) is crossed in the next 30 days. Three forecasters are trained by the logistic loss on '
            f'{s["N40"]:,} simulated records (60% train, 40% test): with Markov features (the last sample and the time '
            f'since it), with path features of the samples (the previous sample and gap, the mean and the maximum of the '
            f'last 60 days, the number of samples) and with the head logger as well. Their Brier skill over climatology '
            f'(Figure {{{{t40}}}}) is {s["sk"][0]}, {s["sk"][1]} and {s["sk"][2]}. The sample path adds little because '
            f'fortnightly samples barely resolve the slow component; the head logger, which observes it at other times, '
            f'adds most — the incomplete-observation effect of A1, and the reason to log heads at the wellfield.'))
    A(('img', 't40', 17.0))
    A(('cap', 'Figure {{t40}}. T40. (a) Brier skill of the online warning over climatology for three sets of inputs. (b) '
              'Reliability: forecast probability against observed frequency, by decile.'))
    # ------------------------------------------------------------------------------------------- 7
    A(('h', '7. For the NATO form'))
    A(('h2', '7.1 State of the art (addition to field 5.3)'))
    A(('box', [
        'Online forecasting from irregular, incomplete records has a theory: path-dependent neural jump ODEs converge to '
        'the conditional expectation for generic, possibly path-dependent processes with jumps and incomplete '
        'observations (Herrera, Krach and Teichmann 2021; Krach, Nübel and Teichmann 2026). Robust finance bounds the '
        'price of a path-dependent option over all models that fit the liquid prices (Hobson 1998; Beiglböck, '
        'Henry-Labordère and Penkner 2013), and neural SDEs compute such intervals in practice (Gierjatowicz et al. '
        '2020). Neither is applied to environmental warnings, and both leave two gaps: the online forecast has no '
        'finite-record guarantee, and the robust interval has no certificate outside its model family and no rule for '
        'the observation that would narrow it. For seawater intrusion the gap is concrete: a sampling programme pins the '
        'marginal law of chloride but not its time scale, and by Slepian\'s inequality (Slepian 1962) the probability '
        'that the limit is crossed between samples is then bounded below by the marginal tail and not at all above.']))
    A(('h2', '7.2 Methodology (monitoring and warnings)'))
    A(('box', [
        f'For each wellfield the warning of a chloride crossing is computed for the whole season, not only at the '
        f'sampling dates. The models of the coupled simulator that are consistent with the records give a band for the '
        f'crossing probability, certified by a conformal margin calibrated on simulated aquifers and measured anchor '
        f'periods. The monitoring design adds the observation that identifies the time scale of chloride — a '
        f'conductivity logger, or pairs of samples a few days apart — where the band is too wide to act on. Online, the '
        f'warning is the conditional probability of a crossing given the irregular samples and the head logger, '
        f'learned from simulated records. In tests, a correlation time of 8 days made a crossing within a season '
        f'{s["ratio"]} times more likely than the marginal tail; quarterly samples left the band at {s["q_lo"]}–1 and a '
        f'daily logger narrowed it to {s["l_lo"]}–{s["l_hi"]}.']))
    A(('h2', '7.3 Indicators and sampling plan'))
    A(('b', '**Indicator 1.** For each wellfield, the certified band of the seasonal crossing probability is at most 0.25 '
            'wide by Month 12 (test bed: 0.04 with a daily logger, 0.81 with quarterly samples).'))
    A(('b', f'**Indicator 2.** The certified band covers the observed crossing frequency in back-testing at the stated '
            f'level, at least 90% (test bed: {s["c_cert"]} with the margin).'))
    A(('b', '**Sampling plan.** A conductivity logger in at least one production well of each wellfield, logging every '
            '15 minutes; one campaign a year of paired laboratory samples 1, 3 and 7 days apart to measure the short-lag '
            'correlation; heads logged daily at the same wells (T40); the time scale re-estimated each season.'))
    # ------------------------------------------------------------------------------------------- 8
    A(('h', '8. Limitations'))
    for t in [
        '**Simple families.** S1 and S2 are proved for a stationary Ornstein–Uhlenbeck chloride; T38 and T39 use a '
        'two-component Gaussian family on a grid instead of neural SDEs. The coupled model of CERTAIN-COAST replaces them '
        'in the project.',
        '**The forecaster is a stand-in.** T40 uses logistic regression on hand-made path features, not a neural jump '
        'ODE, and is evaluated by its Brier score, not against the true conditional probability.',
        '**Known marginals in T37.** T37 takes the marginal mean and variance as known; T39 estimates them from each '
        'record.',
        '**Certificates hold for the calibration law.** The margin of S3 is valid for aquifers drawn like the calibration '
        'aquifers; measured anchor periods are needed for the site, as in reviews I–VI.',
        '**No control variate.** The hedge of A2 was not used; with the analytic Ornstein–Uhlenbeck forecast as control '
        'variate the Monte Carlo cost of the band would fall further.']:
        A(('b', t))
    A(('refs',))
    return BL
