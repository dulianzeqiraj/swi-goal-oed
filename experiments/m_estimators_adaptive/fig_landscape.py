"""Figure 1: landscape of the base paper and the 16 reviewed works (no simulation).

The property table below is the single source of truth. It was extracted by hand from the verified reader reports
(scratchpad mv/papers/p00.md ... p16.md, sections 1-3 and 5), the earlier entries (mv/entries/pNN.md), the routes text
(mv/entries/context_routes.md) and the preprint appendix. Every value carries a short evidence note; values that rest on
indirect evidence or on our own reading are listed in `indirect` and drawn with a small corner mark in panel (b).
Outputs: results/landscape.json, figures/fig1_landscape.(png|pdf).
"""
import time

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

from common import OI, INK, MUTED, RULE, GRID, MM, panel, save, dump

# ----------------------------------------------------------------------------------------------------------------------
# 1. Categories (key -> English, Albanian cell text)
# ----------------------------------------------------------------------------------------------------------------------
ROUTE = {'A': ('weights / stabilisation (Wald)', 'pesha, stabilizim (Wald)'),
         'B': ('supermartingales / confidence sequences', 'supermartingale, sekuenca besimi'),
         'C': ('learning and prediction under adaptive collection', 'mësim dhe parashikim'),
         'D': ('structure instead of weights', 'strukturë në vend të peshave')}
RCOL = {'A': OI['blue'], 'B': OI['vermillion'], 'C': OI['green'], 'D': OI['purple']}
SETTING = {'batched': ('batched bandit', 'bandit me grupe'),
           'contextual': ('contextual bandit', 'bandit kontekstual'),
           'policy': ('adaptive experiment for policy choice', 'eksperiment për\nzgjedhje politike'),
           'bayes': ('Bayesian posterior (adaptive linear Gaussian / exp. family)', 'posterior\nbayesian'),
           'sequential': ('generic sequential', 'sekuencial i\npërgjithshëm'),
           'active': ('active learning', 'mësim aktiv'),
           'conformal': ('conformal design (feedback covariate shift)', 'projektim\nkonformal'),
           'rl': ('RL off-policy', 'RL jashtë\npolitike')}
ESTIMAND = {'means': ('arm means / ATE', 'mesatare krahësh\n/ ATE'),
            'M': ('M-estimand (parameter or functional)', 'parametër M\n$\\theta^*$'),
            'value': ('policy value', 'vlera e\npolitikës'),
            'risk': ('risk minimiser', 'minimizues\nrreziku'),
            'pred': ('prediction set', 'bashkësi\nparashikimi'),
            'ope': ('OPE value', 'vlera OPE')}
INFER = {'wald': ('Wald CLT', 'Wald (CLT)'),
         'cs': ('confidence sequence', 'sekuencë\nbesimi'),
         'lr': ('likelihood-ratio set', 'raport\npërgjasash'),
         'bayes': ('Bayesian', 'bayesiane'),
         'conformal': ('conformal', 'konformale'),
         'boot': ('bootstrap', 'bootstrap'),
         'conc': ('concentration bound (finite-sample CI)', 'kufi\npërqendrimi'),
         'none': ('none (rates / point estimates only)', 'pa interval')}
GUAR = {'asym': ('asymptotic', 'asimptotike'), 'finite': ('finite-sample', 'mostër\ne fundme'),
        'unif': ('time-uniform', 'uniforme\nnë kohë')}
YN = {'yes': ('yes', 'po'), 'no': ('no', 'jo'), 'partly': ('partly', 'pjesërisht'), '?': ('unclear', '?')}
VTYPE = {'journal': ('journal', 'revistë'), 'conference': ('conference', 'konferencë')}

# ----------------------------------------------------------------------------------------------------------------------
# 2. The property vectors (17 works)
# ----------------------------------------------------------------------------------------------------------------------
W = [
    dict(k=0, cite='Zhang, Janson & Murphy (2021)', short='Zhang, Janson & Murphy', year=2021, venue='NeurIPS',
         venue_full='Advances in Neural Information Processing Systems 34: 7460-7471', vtype='conference', group='Harvard',
         route='A', setting='contextual', estimand='M', inference='wald', guarantee='asym', prop='yes', stab='no',
         misspec='no', real='no', indirect=['misspec'],
         notes=dict(setting='history-dependent policy pi_t(A_t|X_t,H_{t-1}); simulations: two-arm and contextual Thompson sampling (p00 §3.4)',
                    inference='self-normalised chi^2 ellipsoid, Theorem 1 (uniform asymptotic normality) (p00 §2 row 17, §3.3)',
                    prop='weights W_t = sqrt(pi_sta/pi_t) need the logged pi_t; C9 bounded ratios (p00 §2 rows 12, 15d)',
                    stab='weights replace stability: conditional variance fixed under pi_sta (p00 §3.2, §5a)',
                    misspec='correct specification: target defined conditionally on (X,A) (p00 §2 row 8); explicit statement NOT re-verified (row 27c); follow-ups target the misspecified case (§3.7)',
                    real='simulations only (p00 §3.4)')),
    dict(k=1, cite='Zhang, Janson & Murphy (2020)', short='Zhang', year=2020, venue='NeurIPS',
         venue_full='Advances in Neural Information Processing Systems 33: 9818-9829', vtype='conference', group='Harvard',
         route='A', setting='batched', estimand='means', inference='wald', guarantee='asym', prop='no', stab='no',
         misspec='partly', real='no', indirect=['misspec'],
         notes=dict(estimand='arm-mean difference (margin) per batch (p01 §2 rows 11-12)',
                    inference='batch-studentised BOLS, t_{n-2} / N(0,1) reference (p01 §2 rows 10, 18)',
                    guarantee='n -> infinity with T fixed (p01 §3.1)',
                    prop='BOLS does not use the logged pi_t (p01 §3.4)',
                    stab='BOLS needs conditionally i.i.d. actions within a batch and clipping, not Lai-Wei stability (OLS does) (p01 §3.2)',
                    misspec='robust to a non-stationary baseline (abstract, p01 §2 row 17); otherwise a difference of arm means (our reading)',
                    real='simulations (T = 25 batches of n = 25) (p01 §3.4)')),
    dict(k=2, cite='Bibaut et al. (2021a)', short='Bibaut', year=2021, venue='NeurIPS',
         venue_full='Advances in Neural Information Processing Systems 34: 28548-28559', vtype='conference', group='Berkeley',
         route='A', setting='contextual', estimand='value', inference='wald', guarantee='asym', prop='yes', stab='no',
         misspec='yes', real='yes', indirect=['real'],
         notes=dict(inference='CADR: inverse-sd stabilised one-step estimator, asymptotically normal (p02 §3)',
                    prop='known logging policy g_t; DR score uses g*/g_t (p02 §3)',
                    stab='does not need asymptotic stabilisation of the logging policy; needs exploration-rate A3/A6 instead (p02 §3 limitations)',
                    misspec='outcome model need only converge to a fixed limit (A4), black-box regressors allowed (p02 §3)',
                    real='57 OpenML datasets (semi-synthetic bandit simulation) (p02 §3)')),
    dict(k=3, cite='Caria et al. (2024)', short='Caria', year=2024, venue='JEEA',
         venue_full='Journal of the European Economic Association 22(2): 781-836', vtype='journal', group='Oxford',
         route='A', setting='policy', estimand='means', inference='wald', guarantee='asym', prop='no', stab='yes',
         misspec='partly', real='yes', indirect=['misspec'],
         notes=dict(estimand='stratum x arm means (Theorem 1 item 4) (p03 §2 row 17)',
                    inference='Wald "as if assignment were not adaptive"; also randomisation p-values (exact under the sharp null) and Bayesian credible sets (p03 §2 row 24, §3.4)',
                    prop='unweighted cell means; randomisation inference needs the algorithm, not the propensities (p03 §3.4)',
                    stab='converging shares from a floor gamma/k plus a unique optimum (Assumption 1, Theorem 1 item 2) (p03 §2 rows 15, 18)',
                    misspec='saturated Bernoulli cell means; stationarity assumed (B.8) (p03 §3.6) - our reading',
                    real='field experiment, 3,770 refugees and Jordanians (p03 §3.5)')),
    dict(k=4, cite='Kasy & Sautmann (2021)', short='Kasy', year=2021, venue='Econometrica',
         venue_full='Econometrica 89(1): 113-132 (author correction note 10 Nov 2021)', vtype='journal', group='Oxford',
         route='A', setting='policy', estimand='means', inference='bayes', guarantee='asym', prop='no', stab='partly',
         misspec='partly', real='yes', indirect=['stab', 'misspec'],
         notes=dict(estimand='arm success rates theta^d; goal is the choice of the best arm (policy regret) (p04 §3.1)',
                    inference='posterior means / SDs / p_T^d; no frequentist interval (p04 §2 row 19)',
                    guarantee='T -> infinity with fixed wave size; corrected Theorem 1 (p04 §3.2)',
                    stab='unique best arm assumed; non-random limit shares are a result; link to Wald stability is our inference (p04 §2 row 20)',
                    misspec='binary outcomes, no interference, i.i.d. stationary (p04 §3.1) - our reading',
                    real='PAD agricultural-extension field implementation in India, 17 waves of 600 (p04 §3.4)')),
    dict(k=5, cite='Du, Nair & Janson (2025)', short='Du', year=2025, venue='NeurIPS',
         venue_full='Advances in Neural Information Processing Systems 38 (pages not verified)', vtype='conference', group='Harvard',
         route='A', setting='bayes', estimand='M', inference='bayes', guarantee='asym', prop='no', stab='partly',
         misspec='no', real='no', indirect=[],
         notes=dict(setting='adaptive linear Gaussian: bandits, adaptive regression, LQR (p05 §3.1)',
                    inference='Bernstein-von Mises in TV to the representative normal (p05 §2 rows 8-10)',
                    stab='BvM itself needs no stability; frequentist validity of credible sets needs it (negative result) (p05 §2 rows 9, 14)',
                    misspec='theorems stated for the correctly specified linear Gaussian / exponential-family model (p05 §3.1)',
                    real='"a range of simulations" (abstract) (p05 §3.4)')),
    dict(k=6, cite='Howard et al. (2021)', short='Howard', year=2021, venue='Ann. Statist.',
         venue_full='Annals of Statistics 49(2): 1055-1080', vtype='journal', group='Berkeley',
         route='B', setting='sequential', estimand='means', inference='cs', guarantee='unif', prop='yes', stab='no',
         misspec='yes', real='?', indirect=['prop', 'group'],
         notes=dict(estimand='means, sample ATE, covariance (p06 §3.1)',
                    prop='only Corollary 2 (ATE under adaptive P_t in [p_min, 1-p_min]) uses the known propensities; mean CSs do not (p06 §2 row 14, §3.2)',
                    stab='supermartingale + Ville: no stability or CLT (p06 §5a)',
                    misspec='nonparametric (bounded / sub-psi) conditions (p06 §3.1)',
                    real='experiments NOT verified (p06 §3.4)', group='affiliations not verified in p06; group from context_routes.md')),
    dict(k=7, cite='Emmenegger, Mutný & Krause (2023)', short='Emmenegger', year=2023, venue='NeurIPS',
         venue_full='Advances in Neural Information Processing Systems 36 (volume number not explicitly verified)', vtype='conference',
         group='ETH', route='B', setting='sequential', estimand='M', inference='lr', guarantee='unif', prop='no', stab='no',
         misspec='no', real='?', indirect=[],
         notes=dict(setting='adaptively chosen covariates / GLM bandits (p07 §3.1)',
                    inference='weighted plug-in likelihood-ratio confidence sequence (Theorem 1) (p07 §3.2)',
                    misspec='"especially suitable for problems with well-specified likelihoods" (abstract) (p07 §2 row 14)',
                    real='GLM bandits, survival analysis, noise families; data sources NOT verified (p07 §3.4)')),
    dict(k=8, cite='Pásztor, Kassraie & Krause (2024)', short='Pásztor', year=2024, venue='NeurIPS',
         venue_full='Advances in Neural Information Processing Systems 37', vtype='conference', group='ETH',
         route='B', setting='sequential', estimand='M', inference='cs', guarantee='unif', prop='no', stab='no',
         misspec='no', real='yes', indirect=['real'],
         notes=dict(setting='kernelised (dueling / logistic) bandit on an infinite domain (p08 §3.1)',
                    estimand='RKHS utility f (kernel logistic regression function) (p08 §2 row 9)',
                    misspec='Bradley-Terry link, f in RKHS with known norm bound B (p08 §2 rows 9, 14)',
                    real='Yelp-based utility (semi-synthetic) plus 7 test functions (p08 §3.3)')),
    dict(k=9, cite='Mutný & Krause (2022)', short='Mutný', year=2022, venue='NeurIPS',
         venue_full='Advances in Neural Information Processing Systems 35', vtype='conference', group='ETH',
         route='B', setting='sequential', estimand='M', inference='cs', guarantee='unif', prop='no', stab='no',
         misspec='partly', real='?', indirect=['guarantee'],
         notes=dict(setting='adaptive experimental design: queries depend on past noise (p09 §3.1)',
                    estimand='linear functional C theta of an RKHS element (p09 §2 row 4)',
                    guarantee='mixture supermartingale (time-uniform route); "for all t" wording NOT verified (p09 §2 row 18)',
                    misspec='fixed, explicitly bounded bias allowed; kernel and V_0 assumed known (p09 §3.1)',
                    real='differential equations, linear bandits, gradient maps, stability verification; data sources NOT verified (p09 §3.4)')),
    dict(k=10, cite='Bibaut et al. (2021b)', short='Bibaut', year=2021, venue='NeurIPS',
         venue_full='Advances in Neural Information Processing Systems 34: 19261-19273', vtype='conference', group='Berkeley',
         route='C', setting='contextual', estimand='risk', inference='none', guarantee='finite', prop='yes', stab='no',
         misspec='yes', real='?', indirect=['misspec', 'group'],
         notes=dict(inference='excess-risk and regret rates, no intervals (p10 §2 row 16)',
                    guarantee='high-probability (1 - 2e^{-x}) maximal inequality (p10 §2 row 13)',
                    prop='importance weights g*/g_t from the known logging policy (p10 §2 rows 10, 19)',
                    misspec='target is the best-in-class risk minimiser under the reference design - our reading of "minimise the average of a loss over a hypothesis class"',
                    real='"an empirical investigation validates our theory"; designs NOT verified (p10 §3)',
                    group='affiliations not verified in p10; group from context_routes.md')),
    dict(k=11, cite='Farquhar, Gal & Rainforth (2021)', short='Farquhar', year=2021, venue='ICLR',
         venue_full='International Conference on Learning Representations 2021 (spotlight)', vtype='conference', group='Oxford',
         route='C', setting='active', estimand='risk', inference='none', guarantee='finite', prop='yes', stab='no',
         misspec='yes', real='yes', indirect=[],
         notes=dict(estimand='population (pool) risk used for training / evaluation (p11 §3.1)',
                    inference='unbiased point estimators PURE / LURE, no CLT or intervals (p11 §2 rows 13, 16)',
                    guarantee='exact unbiasedness for every M (Theorems 1, 3) (p11 §2 row 9)',
                    prop='acquisition probabilities q must be known and positive (p11 §2 row 15)',
                    misspec='design-based: unbiased for any model (p11 §2 row 9)',
                    real='MNIST, FashionMNIST (p11 §3.4)')),
    dict(k=12, cite='Fannjiang et al. (2022)', short='Fannjiang', year=2022, venue='PNAS',
         venue_full='Proceedings of the National Academy of Sciences 119(43): e2204569119', vtype='journal', group='Berkeley',
         route='C', setting='conformal', estimand='pred', inference='conformal', guarantee='finite', prop='yes', stab='no',
         misspec='yes', real='yes', indirect=[],
         notes=dict(prop='known, randomised design density including its normalising constant (p12 §2 row 12)',
                    misspec='valid "for arbitrary regression models" (p12 §2 row 8)',
                    real='fluorescent proteins (2^13 sequences) and AAV capsids (p12 §3.2-3.3)')),
    dict(k=13, cite='Dwivedi et al. (2025)', short='Dwivedi', year=2025, venue='Ann. Statist.',
         venue_full='Annals of Statistics 53(6): 2380-2408', vtype='journal', group='Harvard',
         route='D', setting='sequential', estimand='means', inference='wald', guarantee='asym', prop='no', stab='partly',
         misspec='no', real='yes', indirect=['stab'],
         notes=dict(setting='multi-unit sequential experiment with pooled adaptive policies (p13 §2 rows 10-12)',
                    estimand='counterfactual mean of each unit at each time (p13 §2 row 10)',
                    prop='nearest neighbours, no inverse-propensity weighting (p13 §2 row 14)',
                    stab='exploration floor + conditional independence across units; a policy-stability quantity enters the 2022 CLT, final version NOT verified (p13 §2 row 18, §3.3)',
                    misspec='latent factor model, no carry-over (p13 §2 rows 15, 26)',
                    real='HeartSteps mobile-health trial (p13 §3.5)')),
    dict(k=14, cite='Duan, Jia & Wang (2020)', short='Duan', year=2020, venue='ICML',
         venue_full='Proceedings of ICML 2020, PMLR 119: 2701-2709', vtype='conference', group='Princeton',
         route='D', setting='rl', estimand='ope', inference='conc', guarantee='finite', prop='no', stab='no',
         misspec='no', real='no', indirect=[],
         notes=dict(inference='Theorem 4: computable confidence bound under Assumption 3 (filtration-adapted, adaptive data allowed) (p14 §3.3)',
                    prop='behaviour policy not known (p14 §3.1)',
                    stab='Theorem 4 needs only Assumption 3; Theorems 2-3 need i.i.d. episodes (p14 §2 row 14)',
                    misspec='Assumption 1 (Bellman completeness); no misspecification analysis (p14 §3.6)',
                    real='no experiments (p14 §3.5)')),
    dict(k=15, cite='Hao et al. (2021)', short='Hao', year=2021, venue='ICML',
         venue_full='Proceedings of ICML 2021, PMLR 139: 4074-4084', vtype='conference', group='Princeton',
         route='D', setting='rl', estimand='ope', inference='boot', guarantee='asym', prop='no', stab='yes',
         misspec='no', real='no', indirect=['stab'],
         notes=dict(inference='episode-level bootstrap; Theorem 4.2 CLT and Theorem 5.1 bootstrap consistency (p15 §3.2)',
                    stab='K independent episodes from one behaviour policy: no adaptivity across episodes (stronger than stability) (p15 §5a) - classification is ours',
                    misspec='linear FQE under completeness (Condition 4.1) (p15 §2 rows 4, 11)',
                    real='Cliff Walking, Mountain Car, sepsis simulator (simulators) (p15 §3.4)')),
    dict(k=16, cite='Zhang, Zhang, Ni & Wang (2022)', short='Zhang R.', year=2022, venue='ICML',
         venue_full='Proceedings of ICML 2022, PMLR 162: 26713-26749', vtype='conference', group='Princeton',
         route='D', setting='rl', estimand='ope', inference='boot', guarantee='asym', prop='no', stab='yes',
         misspec='partly', real='no', indirect=['stab'],
         notes=dict(inference='Z-estimator CLT (Theorem 6.1) and vanilla / multiplier bootstrap CI (Corollary 7.2) (p16 §2 rows 14-17)',
                    stab='K i.i.d. episodes from a fixed behaviour policy (p16 §2 rows 9, 19) - classification is ours',
                    misspec='without completeness the statistical error of theta-hat is still bounded, the variance formula is not (p16 §3.7)',
                    real='no experiments in the arXiv text (p16 §3.6)')),
]

# verified "builds on" relations between list works: (built-upon, builder, evidence)
REL = [
    (10, 2, '[2] restates Theorem 1 (maximal inequality) of [10] as its supplement Theorem 3 and uses it (p10 §3; p02 §3)'),
    (9, 7, '[7] cites [9] for "bias does not vanish in many infinite-dimensional Hilbert spaces" (p09 §2 row 23, §3.7)'),
    (14, 15, '[15] uses the Theorem 4 bound of [14] as baseline and reuses its Lemmas B.3, B.5, B.6, B.10 (p14 §3.7)'),
    (14, 16, '[16] cites [14] (PMLR 119: 2701-2709), recovers its Corollary 1 and matches its lower bound (p14 §3.7; p16 §3.3)'),
    (15, 16, '[16] cites [15]: same variance in the linear case (Remark 6.2), episode bootstrap (p15 §3.6; p16 §3.2, §3.4)'),
]
NOT_DRAWN = [
    '[1] -> [0]: same authors and chronology; whether the base paper cites [1] is NOT verified (p01 §2 row 22)',
    '[13] -> [0], [2]: 2022 slides of [13] cite "Zhang et al. \'21" and "Bibaut et al. \'21" without full references (p13 §2 row 30)',
    '[5] -> [0], [7] -> [0], [9] -> [0], [10] -> [0], [2] -> [0]: citation of the base paper NOT verified (p05, p07, p09, p10, p02)',
    'verified non-relations: [3] cites Hadad et al., not the base paper (p03 §2 row 29); [16] does not cite the base paper (p16 §2 row 19)',
]

# ----------------------------------------------------------------------------------------------------------------------
# 3. Derived quantities
# ----------------------------------------------------------------------------------------------------------------------
FAV = {'prop': {'no': 1.0, 'yes': 0.0}, 'stab': {'no': 1.0, 'partly': 0.5, 'yes': 0.0},
       'misspec': {'yes': 1.0, 'partly': 0.5, 'no': 0.0}, 'real': {'yes': 1.0, 'no': 0.0}}
PROFILE_COLS = [('nonasym', 'garanci jo\nasimptotike'), ('prop', 'pa\npropensitete'), ('stab', 'pa kusht\nstabiliteti'),
                ('misspec', 'i qëndrueshëm\nndaj spec.'), ('interval', 'jep interval\nose bashkësi'), ('real', 'të dhëna\nreale')]


def profile():
    out = {}
    for r in 'ABCD':
        ws = [w for w in W if w['route'] == r]
        row = {'n': len(ws), 'works': [w['k'] for w in ws]}
        row['nonasym'] = dict(score=sum(w['guarantee'] != 'asym' for w in ws), unclear=0)
        row['interval'] = dict(score=sum(w['inference'] != 'none' for w in ws), unclear=0)
        for c in ('prop', 'stab', 'misspec', 'real'):
            row[c] = dict(score=float(sum(FAV[c].get(w[c], 0.0) for w in ws)), unclear=sum(w[c] == '?' for w in ws))
        out[r] = row
    return out


def counts():
    keys = dict(route=ROUTE, vtype=VTYPE, group=None, setting=SETTING, estimand=ESTIMAND, inference=INFER, guarantee=GUAR,
                prop=YN, stab=YN, misspec=YN, real=YN)
    out = {}
    for f in keys:
        c = {}
        for w in W:
            c[w[f]] = c.get(w[f], 0) + 1
        out[f] = c
    return out


def md_table():
    hdr = ('| # | Work | Year | Venue | Type | Group | Route | Data-collection setting | Estimand | Inference | Guarantee | '
           'Needs known propensities | Needs stability | Robust to misspecification | Real data |')
    sep = '|' + '---|' * 15
    rows = [hdr, sep]
    for w in W:
        def v(f, d):
            s = d[w[f]][0]
            return s + ('*' if f in w['indirect'] else '')
        rows.append(f"| [{w['k']}] | {w['cite']} | {w['year']} | {w['venue']} | {w['vtype']} | {w['group']}"
                    f"{'*' if 'group' in w['indirect'] else ''} | {w['route']} | {v('setting', SETTING)} | {v('estimand', ESTIMAND)} | "
                    f"{v('inference', INFER)} | {v('guarantee', GUAR)} | {v('prop', YN)} | {v('stab', YN)} | {v('misspec', YN)} | {v('real', YN)} |")
    return '\n'.join(rows)


# ----------------------------------------------------------------------------------------------------------------------
# 4. Figure
# ----------------------------------------------------------------------------------------------------------------------
FIGW, FIGH = 178.0, 222.0


def ax_mm(fig, x0, y0, w, h):
    """Axes from a rectangle in mm, origin at the top-left of the figure."""
    return fig.add_axes([x0 / FIGW, 1 - (y0 + h) / FIGH, w / FIGW, h / FIGH])


def tint(c, a):
    c = np.array(plt.matplotlib.colors.to_rgb(c))
    return tuple(1 - a * (1 - c))


# timeline slots: k -> (lane offset within the lane band, x offset in years)
SLOT = {1: (0.50, 0.0), 0: (0.80, 0.0), 2: (0.50, 0.0), 4: (0.20, 0.0), 3: (0.50, 0.0), 5: (0.50, 0.0),
        6: (0.50, 0.0), 9: (0.62, 0.0), 7: (0.62, 0.0), 8: (0.50, 0.0),
        10: (0.72, 0.0), 11: (0.28, 0.0), 12: (0.50, 0.0),
        14: (0.66, 0.0), 15: (0.66, 0.0), 16: (0.66, 0.0), 13: (0.50, 0.0)}
LANE_Y = {'A': 3, 'B': 2, 'C': 1, 'D': 0}


def pos(w):
    o, dx = SLOT[w['k']]
    return w['year'] + dx, LANE_Y[w['route']] + o


def panel_a(fig):
    ax = ax_mm(fig, 30, 7, 145, 47)
    ax.set_xlim(2019.55, 2026.45); ax.set_ylim(0, 4)
    for r, y in LANE_Y.items():
        ax.add_patch(Rectangle((2019.55, y), 6.9, 1, facecolor=tint(RCOL[r], 0.07), edgecolor='none', zorder=0))
        if y > 0:
            ax.axhline(y, color=RULE, lw=0.5, zorder=0.5)
    ax.grid(False)
    for yr in range(2020, 2027):
        ax.axvline(yr, color=GRID, lw=0.6, zorder=0.6)
    ax.set_xticks(range(2020, 2027)); ax.tick_params(axis='x', length=0, pad=2.5)
    ax.set_yticks([LANE_Y[r] + 0.5 for r in 'ABCD'])
    ax.set_yticklabels([f'{r}  ' + ROUTE[r][1].replace(', ', ',\n').replace(' në vend', '\nnë vend').replace(' dhe', '\ndhe')
                        for r in 'ABCD'], fontsize=6.0)
    for t, r in zip(ax.get_yticklabels(), 'ABCD'):
        t.set_color(RCOL[r]); t.set_fontweight('bold')
    ax.tick_params(axis='y', length=0, pad=3)
    for s in ('left', 'bottom', 'top', 'right'):
        ax.spines[s].set_visible(False)
    ax.set_xlabel('viti i versionit të botuar', fontsize=6.6, labelpad=2)
    P = {w['k']: pos(w) for w in W}
    # relations (drawn first so markers sit on top)
    rad = {(10, 2): -0.42, (9, 7): 0.45, (14, 15): 0.42, (15, 16): 0.42, (14, 16): 0.40}
    for a, b, _ in REL:
        arr = FancyArrowPatch(P[a], P[b], connectionstyle=f'arc3,rad={rad[(a, b)]}', arrowstyle='-|>', mutation_scale=5.5,
                              lw=0.7, color=MUTED, shrinkA=4.2, shrinkB=4.8, zorder=2)
        ax.add_patch(arr)
    for w in W:
        x, y = P[w['k']]; c = RCOL[w['route']]
        mk = 's' if w['vtype'] == 'journal' else 'o'
        if w['k'] == 0:
            ax.plot(x, y, 'o', ms=10.5, mfc='white', mec=c, mew=0.9, zorder=3)
            ax.plot(x, y, mk, ms=6.2, mfc=c, mec='white', mew=0.6, zorder=4)
            ax.text(x + 0.13, y, '[0] Zhang, Janson & Murphy: punimi bazë', fontsize=6.0, fontweight='bold', color=INK,
                    va='center', ha='left', zorder=5)
            continue
        ax.plot(x, y, mk, ms=4.6 if mk == 'o' else 4.2, mfc=c, mec='white', mew=0.5, zorder=4)
        ax.text(x + 0.09, y, f"[{w['k']}] {w['short']}", fontsize=5.8, color=INK, va='center', ha='left', zorder=5)
    # legend (inside the empty part of lane C)
    lx, ly = 2023.25, 1.78
    items = [('o', 'konferencë'), ('s', 'revistë')]
    for i, (m, t) in enumerate(items):
        ax.plot(lx + 0.05 + i * 1.05, ly, m, ms=4.2, mfc=MUTED, mec='white', mew=0.5)
        ax.text(lx + 0.15 + i * 1.05, ly, t, fontsize=5.7, color=INK, va='center')
    ax.add_patch(FancyArrowPatch((lx - 0.02, ly - 0.42), (lx + 0.42, ly - 0.42), arrowstyle='-|>', mutation_scale=5.5, lw=0.7,
                                 color=MUTED))
    ax.text(lx + 0.5, ly - 0.42, 'X → Y: Y ndërton mbi X (e verifikuar)', fontsize=5.7, color=INK, va='center')
    ax.text(2026.42, 0.08, 'brenda vitit, pozicioni vertikal vetëm për lexueshmëri', fontsize=5.2, color=MUTED,
            ha='right', va='bottom', style='italic')
    ax.set_title('Harta kohore: 17 punime në katër rrugët e inferencës', color=INK, x=-0.17, ha='left')
    panel(ax, 'a', x=-0.2, y=1.02)


# matrix columns: (field, header, width in mm)
COLS = [('venue', 'Botimi', 15.0), ('group', 'Grupi', 13.0), ('route', 'Rruga', 7.5), ('setting', 'Mjedisi i\nmbledhjes', 19.0),
        ('estimand', 'Objektivi', 18.5), ('inference', 'Lloji i\ninferencës', 15.0), ('guarantee', 'Garancia', 13.5),
        ('prop', 'Kërkon\npropensitete\ntë njohura', 13.0), ('stab', 'Kërkon\nkusht\nstabiliteti', 12.0),
        ('misspec', 'I qëndrueshëm\nndaj spec.\ntë gabuar', 14.5), ('real', 'Të dhëna\nreale', 10.5)]
QUAL = ['#dbe8f5', '#fde3cc', '#d5efe4', '#f4dbea', '#fbf0bf', '#e2def2', '#d3edf5', '#ece5d8']
GROUPC = {'Harvard': '#f3dada', 'Berkeley': '#d9e5f3', 'Oxford': '#e2def2', 'ETH': '#dcefdc', 'Princeton': '#fbe6cb'}
GUARC = {'asym': '#eef1f5', 'finite': '#cfe2f1', 'unif': '#a8cde9'}
C_FAV, C_MID, C_BAD, C_NEU = '#cfeadb', '#fbe4b8', '#f8d2c2', '#eceef0'
LEVEL = {'prop': {'no': C_FAV, 'yes': C_BAD}, 'stab': {'no': C_FAV, 'partly': C_MID, 'yes': C_BAD},
         'misspec': {'yes': C_FAV, 'partly': C_MID, 'no': C_BAD}, 'real': {'yes': C_FAV, 'no': C_NEU}}


def cell_style(w, f):
    v = w[f]
    if f == 'venue':
        return v, ('#efe5d3' if w['vtype'] == 'journal' else '#e6ecf2'), INK, False
    if f == 'group':
        return v, GROUPC[v], INK, False
    if f == 'route':
        return v, RCOL[v], 'white', True
    if f in ('setting', 'estimand', 'inference'):
        d = dict(setting=SETTING, estimand=ESTIMAND, inference=INFER)[f]
        return d[v][1], QUAL[list(d).index(v) % len(QUAL)], INK, False
    if f == 'guarantee':
        return GUAR[v][1], GUARC[v], INK, False
    if v == '?':
        return '?', 'white', MUTED, True
    return YN[v][1], LEVEL[f][v], INK, False


def panel_b(fig):
    x0, y0, rowh, labw = 2.0, 60.0, 4.55, 34.0
    tot = labw + sum(c[2] for c in COLS)
    hh = 12.5
    H = hh + rowh * len(W) + 3 * 1.2 + 9.5
    ax = ax_mm(fig, x0, y0, tot, H)
    ax.set_xlim(0, tot); ax.set_ylim(H, 0); ax.axis('off')
    # headers
    xc = labw
    for f, h, wd in COLS:
        ax.text(xc + wd / 2, hh - 1.0, h, ha='center', va='bottom', fontsize=5.6, color=INK, linespacing=1.05)
        xc += wd
    ax.plot([0, tot], [hh, hh], color=RULE, lw=0.6)
    y = hh + 0.6
    prev = None
    for w in W:
        if prev is not None and w['route'] != prev:
            y += 1.2
        prev = w['route']
        if w['k'] == 0:
            ax.add_patch(Rectangle((0, y - 0.25), tot, rowh + 0.5, facecolor=tint(OI['blue'], 0.10), edgecolor='none', zorder=0))
        ax.add_patch(Rectangle((0.4, y + 1.2), 2.0, rowh - 2.4, facecolor=RCOL[w['route']], edgecolor='none'))
        ax.text(3.2, y + rowh / 2, f"[{w['k']}] {w['cite']}", fontsize=5.6, color=INK, va='center', ha='left',
                fontweight='bold' if w['k'] == 0 else 'normal')
        xc = labw
        for f, h, wd in COLS:
            txt, fc, tc, bold = cell_style(w, f)
            ax.add_patch(Rectangle((xc + 0.25, y + 0.2), wd - 0.5, rowh - 0.4, facecolor=fc, edgecolor=GRID, lw=0.35))
            fs = 5.0 if '\n' in txt else 5.4
            ax.text(xc + wd / 2, y + rowh / 2 + 0.1, txt, ha='center', va='center', fontsize=fs, color=tc, linespacing=0.95,
                    fontweight='bold' if bold else 'normal')
            if f in w['indirect']:
                ax.text(xc + wd - 0.55, y + 0.45, '*', ha='right', va='top', fontsize=5.6, color=MUTED)
            xc += wd
        y += rowh
    # legend
    y += 2.4
    sw = [(C_FAV, 'vetí e favorshme'), (C_MID, 'pjesërisht'), (C_BAD, 'kërkesë kufizuese'), (C_NEU, 'mungon'), ('white', 'e paqartë (?)')]
    xl = 1.0
    ax.text(xl, y + 1.0, 'Katër kolonat e fundit:', fontsize=5.5, color=INK, va='center'); xl += 21.0
    for fc, t in sw:
        ax.add_patch(Rectangle((xl, y), 3.2, 2.0, facecolor=fc, edgecolor=RULE, lw=0.4))
        ax.text(xl + 4.0, y + 1.0, t, fontsize=5.5, color=INK, va='center')
        xl += 5.0 + 1.03 * len(t)
    ax.text(xl + 1.0, y + 1.0, '*  klasifikim me evidencë indirekte ose interpretim ynë', fontsize=5.5, color=MUTED, va='center')
    y += 3.6
    xl = 1.0
    ax.text(xl, y + 1.0, 'Botimi:', fontsize=5.5, color=INK, va='center'); xl += 8.5
    for fc, t in (('#efe5d3', 'revistë'), ('#e6ecf2', 'konferencë')):
        ax.add_patch(Rectangle((xl, y), 3.2, 2.0, facecolor=fc, edgecolor=RULE, lw=0.4))
        ax.text(xl + 4.0, y + 1.0, t, fontsize=5.5, color=INK, va='center'); xl += 5.0 + 1.03 * len(t)
    xl += 4.0
    ax.text(xl, y + 1.0, 'Garancia:', fontsize=5.5, color=INK, va='center'); xl += 10.5
    for g in ('asym', 'finite', 'unif'):
        t = GUAR[g][1].replace('\n', ' ')
        ax.add_patch(Rectangle((xl, y), 3.2, 2.0, facecolor=GUARC[g], edgecolor=RULE, lw=0.4))
        ax.text(xl + 4.0, y + 1.0, t, fontsize=5.5, color=INK, va='center'); xl += 5.0 + 1.03 * len(t)
    xl += 4.0
    ax.text(xl, y + 1.0, 'Kolonat e tjera: ngjyra dallon kategoritë e shkruara në qelizë.', fontsize=5.5, color=MUTED, va='center')
    ax.text(0.0, -2.2, 'Matrica e vetive: çfarë kërkon dhe çfarë garanton secili punim', fontsize=7.6, color=INK, ha='left',
            va='bottom')
    ax.text(-1.6, -2.4, 'b', fontsize=8.6, fontweight='bold', color=INK, ha='right', va='bottom')
    return y0 + H


def rbox(ax, x, y, w, h, fc, ec, lw=0.8, z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=1.6', facecolor=fc, edgecolor=ec, lw=lw,
                                zorder=z))


def panel_c(fig, top):
    W_, H_ = 100.0, 50.0
    ax = ax_mm(fig, 2.0, top, W_, H_)
    ax.set_xlim(0, W_); ax.set_ylim(0, H_); ax.axis('off')
    # centre
    cx, cy, cw, ch = 30.0, 17.0, 40.0, 16.0
    rbox(ax, cx, cy, cw, ch, 'white', INK, lw=0.9, z=3)
    ax.text(cx + cw / 2, cy + ch - 2.2, 'kushti unifikues i CLT martingale', ha='center', va='center', fontsize=5.8,
            color=INK, fontweight='bold', zorder=4)
    ax.text(cx + cw / 2, cy + ch / 2 + 0.2,
            '$\\frac{1}{T}\\sum_{t=1}^{T}\\mathbb{E}\\left[W_t^2\\,\\dot m\\,\\dot m^{\\top}\\mid\\mathcal{H}_{t-1}\\right]\\to\\Sigma$',
            ha='center', va='center', fontsize=7.0, color=INK, zorder=4)
    ax.text(cx + cw / 2, cy + 2.2, '$\\Sigma$ jo e rastit;  $\\mathbb{E}[W_t^2 f\\mid\\mathcal{H}_{t-1}]=\\mathbb{E}_{\\pi^{\\rm sta}}[f]$',
            ha='center', va='center', fontsize=5.6, color=MUTED, zorder=4)
    spec = {'A': (1.0, 33.0, 'pesha ose stabilizim',
                  '$W_t=\\sqrt{\\pi^{\\rm sta}/\\pi_t}$, studentizim grupor,\n$\\hat\\sigma_t^{-1}$, ndarje që konvergjojnë', '[0]–[5]'),
            'B': (71.0, 33.0, 'supermartingale',
                  'mosbarazimi i Ville-s: sekuenca\nbesimi, raport përgjasash; pa CLT', '[6]–[9]'),
            'C': (1.0, 1.0, 'mësim dhe parashikim',
                  'pesha të plota $g^*/g_t$: rrezik\ni paanshëm, konformal me reagim', '[10]–[12]'),
            'D': (71.0, 1.0, 'strukturë',
                  'episode i.i.d. ose model faktorësh;\nkufi përqendrimi për të dhëna adaptive', '[13]–[16]')}
    bw, bh = 28.0, 16.0
    arrow_lab = {'A': 'e arrin', 'B': 'e anashkalon', 'C': 'e anashkalon', 'D': 'e arrin\nnga struktura'}
    for r, (x, y, t, body, ks) in spec.items():
        rbox(ax, x, y, bw, bh, tint(RCOL[r], 0.10), RCOL[r], lw=0.8, z=2)
        ax.text(x + 1.6, y + bh - 2.3, f'{r}  {t}', fontsize=6.0, color=RCOL[r], fontweight='bold', va='center', zorder=4)
        ax.text(x + 1.6, y + bh / 2 - 0.6, body, fontsize=5.2, color=INK, va='center', linespacing=1.15, zorder=4)
        ax.text(x + bw - 1.4, y + 1.7, ks, fontsize=5.4, color=MUTED, ha='right', va='center', zorder=4)
        left = x < 50; upper = y > 20
        sx = x + bw if left else x
        sy = y + (3.0 if upper else bh - 3.0)
        ex = cx + (4.0 if left else cw - 4.0)
        ey = cy + ch if upper else cy
        solid = r in ('A', 'D')
        ax.add_patch(FancyArrowPatch((sx, sy), (ex, ey), connectionstyle=f"arc3,rad={(0.25 if left == upper else -0.25)}",
                                     arrowstyle='-|>', mutation_scale=6, lw=0.9, color=RCOL[r], ls='-' if solid else (0, (3, 2)),
                                     shrinkA=1, shrinkB=1.5, zorder=2))
        lx = (sx + ex) / 2 + (-3.2 if left else 3.2)
        ly = (sy + ey) / 2 + (3.0 if upper else -3.0)
        ax.text(lx, ly, arrow_lab[r], fontsize=5.4, color=RCOL[r], ha='center', va='center', style='italic', zorder=4)
    ax.text(50, 48.6, 'Katër mënyra për të marrë (ose shmangur) variancë të kushtëzuar jo të rastit', fontsize=7.6,
            color=INK, ha='center', va='center')
    ax.text(0.5, 48.6, 'c', fontsize=8.6, fontweight='bold', color=INK, ha='right', va='center')


def panel_d(fig, top, prof):
    ax = ax_mm(fig, 125.0, top + 14.0, 50.0, 29.0)
    M = np.zeros((4, len(PROFILE_COLS))); T = [[''] * len(PROFILE_COLS) for _ in range(4)]
    for i, r in enumerate('ABCD'):
        n = prof[r]['n']
        for j, (c, _) in enumerate(PROFILE_COLS):
            s = prof[r][c]['score']; u = prof[r][c]['unclear']
            M[i, j] = s / n
            ss = f'{s:g}'
            T[i][j] = f'{ss}/{n}' + (f'\n({u} ?)' if u else '')
    cmap = LinearSegmentedColormap.from_list('lb', ['#ffffff', tint(OI['blue'], 0.35), OI['blue']])
    ax.imshow(M, cmap=cmap, vmin=0, vmax=1, aspect='auto')
    for i in range(4):
        for j in range(len(PROFILE_COLS)):
            ax.text(j, i, T[i][j], ha='center', va='center', fontsize=5.4 if '\n' not in T[i][j] else 4.9,
                    color='white' if M[i, j] > 0.62 else INK, linespacing=0.95)
    ax.set_xticks(range(len(PROFILE_COLS))); ax.set_xticklabels([c[1] for c in PROFILE_COLS], fontsize=5.4, rotation=0,
                                                               linespacing=1.0)
    ax.xaxis.tick_top(); ax.tick_params(axis='x', length=0, pad=1.5)
    ax.set_yticks(range(4)); ax.set_yticklabels([f"{r} (n={prof[r]['n']})" for r in 'ABCD'], fontsize=6.0)
    for t, r in zip(ax.get_yticklabels(), 'ABCD'):
        t.set_color(RCOL[r]); t.set_fontweight('bold')
    ax.tick_params(axis='y', length=0, pad=2)
    ax.set_xticks(np.arange(-0.5, len(PROFILE_COLS), 1), minor=True); ax.set_yticks(np.arange(-0.5, 4, 1), minor=True)
    ax.grid(False); ax.grid(which='minor', color='white', lw=1.2); ax.tick_params(which='minor', length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.text(110.0 / FIGW, 1 - (top + 1.4) / FIGH, 'Profili i rrugëve: pjesa me vetinë e favorshme', fontsize=7.6,
             color=INK, ha='left', va='center')
    fig.text(107.5 / FIGW, 1 - (top + 1.4) / FIGH, 'd', fontsize=8.6, fontweight='bold', color=INK, ha='right', va='center')
    fig.text(110.0 / FIGW, 1 - (top + 45.8) / FIGH, '«pjesërisht» numërohet 0.5; «?» numërohet si jo i favorshëm',
             fontsize=5.2, color=MUTED, ha='left', va='center', style='italic')


def main():
    t0 = time.time()
    prof = profile()
    fig = plt.figure(figsize=(FIGW * MM, FIGH * MM))
    panel_a(fig)
    bottom_b = panel_b(fig)
    panel_c(fig, bottom_b + 3.0)
    panel_d(fig, bottom_b + 3.0, prof)
    save(fig, 'fig1_landscape')
    out = dict(
        description='Property vectors of the base paper [0] and the 16 reviewed works [1]-[16]; hand-extracted from the verified '
                    'reader reports mv/papers/pNN.md (sections 1-3, 5) and the earlier entries; no simulation.',
        categories=dict(route={k: v[0] for k, v in ROUTE.items()}, setting={k: v[0] for k, v in SETTING.items()},
                        estimand={k: v[0] for k, v in ESTIMAND.items()}, inference={k: v[0] for k, v in INFER.items()},
                        guarantee={k: v[0] for k, v in GUAR.items()}, yes_no={k: v[0] for k, v in YN.items()}),
        albanian_labels=dict(route={k: v[1] for k, v in ROUTE.items()}, setting={k: v[1].replace('\n', ' ') for k, v in SETTING.items()},
                             estimand={k: v[1].replace('\n', ' ') for k, v in ESTIMAND.items()},
                             inference={k: v[1].replace('\n', ' ') for k, v in INFER.items()},
                             guarantee={k: v[1].replace('\n', ' ') for k, v in GUAR.items()}, yes_no={k: v[1] for k, v in YN.items()}),
        works=W,
        relations_drawn=[dict(built_upon=a, builder=b, evidence=e) for a, b, e in REL],
        relations_not_drawn=NOT_DRAWN,
        unclear=[dict(k=w['k'], field=f) for w in W for f in ('prop', 'stab', 'misspec', 'real') if w[f] == '?'],
        indirect=[dict(k=w['k'], field=f, note=w['notes'].get(f, '')) for w in W for f in w['indirect']],
        counts=counts(), route_profile=prof,
        profile_rule='score = number of works with the favourable value; "partly" counts 0.5; "?" counts as not favourable',
        markdown_table=md_table(), runtime_s=None)
    out['runtime_s'] = round(time.time() - t0, 2)
    dump(out, 'landscape.json')
    print(md_table())
    print('profile', {r: {c: prof[r][c] for c in prof[r]} for r in prof})
    print('runtime', out['runtime_s'])


if __name__ == '__main__':
    main()
