"""Text of the ninth state-of-the-art review (English): the Time Series Deconfounder extracted, twenty papers, our
analogues of its Figures 1 and 2, and FSHEHTA-GO. blocks(E) returns the block list; every number comes from
res/fshehta.json and res/fshehta_case.npz. Conventions: $inline math$, **bold**, *italic*, ==yellow placeholder==,
[text](url) hyperlink, [[key]] equation number, {{key}} figure or table number."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cards_fshehta import CARDS, INST_ORDER, SOTA_ROWS  # noqa: E402

RES = os.path.join(HERE, 'res')
PAPER = 'https://proceedings.mlr.press/v119/bica20a.html'
CODE = 'https://github.com/ioanabica/Time-Series-Deconfounder'

ANCHORS = [
    dict(key='A1', text='Bica, I., Alaa, A. M., & van der Schaar, M. (2020). Time Series Deconfounder: Estimating '
                        'Treatment Effects over Time in the Presence of Hidden Confounders. Proceedings of the 37th '
                        'International Conference on Machine Learning (ICML 2020), PMLR 119 (PDF provided by the user; '
                        'the link follows the PMLR identifier bica20a of the supplement file).', url=PAPER),
    dict(key='A2', text='Bica, I., Alaa, A. M., & van der Schaar, M. (2020). Appendix: Time Series Deconfounder '
                        '(supplementary material, bica20a-supp.pdf, provided by the user). Code as given in the article: '
                        'github.com/ioanabica/Time-Series-Deconfounder.', url=CODE),
]
SYN = [
    dict(key='S1', text='Wang, Y., & Blei, D. M. (2019). The blessings of multiple causes. Journal of the American '
                        'Statistical Association (as listed in the references of A1 and A2).', url=None),
    dict(key='S2', text='D\'Amour, A. (2019). On multi-cause approaches to causal inference with unobserved confounding: '
                        'two cautionary failure cases and a promising alternative. Proceedings of the 22nd International '
                        'Conference on Artificial Intelligence and Statistics, 3478–3486 (as listed in A2).', url=None),
    dict(key='S3', text='Miao, W., Geng, Z., & Tchetgen Tchetgen, E. J. (2018). Identifying causal effects with proxy '
                        'variables of an unmeasured confounder. Biometrika 105(4), 987–993 (as listed in A2).', url=None),
    dict(key='S4', text='Kallenberg, O. (2006). Foundations of Modern Probability. Springer (Lemma 2.22, as used in A2).',
         url=None),
    dict(key='S5', text='Lim, B., Alaa, A., & van der Schaar, M. (2018). Forecasting treatment responses over time using '
                        'recurrent marginal structural networks. Advances in Neural Information Processing Systems, '
                        '7493–7503 (as listed in A2).', url=None),
    dict(key='S6', text='Robins, J. M., Hernán, M. A., & Brumback, B. (2000). Marginal structural models and causal '
                        'inference in epidemiology (as listed in A2).', url=None),
]
OTHER = [
    dict(key='D1', text='Zeqiraj, D. (2026). Reviews I–VIII of this series (GARANCIA-GO, MATJA-GO, RESHJA-GO, ANKORA-GO, '
                        'PRIRJA-GO, DYSHEMEJA-GO, SHKAKU-GO, KRIPA-GO), docs/literature/ in this repository.', url=None),
    dict(key='D2', text='Zeqiraj, D. (in preparation). From sparse hydrochemistry to decision-relevant information: '
                        'probabilistic chloride mapping and goal-oriented monitoring design for seawater intrusion in the '
                        'Fushë-Kuqe coastal aquifer, Albania (chloride_fk/ in this repository).', url=None),
    dict(key='D3', text='The code of this review: experiments/fshehta_go/ (fshehta_exp.py, fshehta_figs.py; results in '
                        'res/).', url=None),
]


def card_ref(c):
    return dict(key=c['id'], text=f"{c['authors']} ({c['year']}). {c['title']}. {c['venue']}.", url=c['links'][0][1])


def all_refs():
    return ANCHORS + [card_ref(c) for c in CARDS] + SYN + OTHER


def sgn(x, d=2):
    """signed number with a typographic minus; 0.00 without a sign."""
    if abs(x) < 0.5 * 10 ** (-d):
        return f'{0:.{d}f}'
    return f'{x:+.{d}f}'.replace('-', '−')


def pct(x, d=0, signed=True):
    v = 100 * x
    if abs(v) < 0.5 * 10 ** (-d):
        return f'{0:.{d}f}%'
    return (f'{v:+.{d}f}%' if signed else f'{v:.{d}f}%').replace('-', '−')


def sci(x):
    m, e = f'{x:.0e}'.split('e')
    sup = str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹')
    return f'{m}×10{str(int(e)).translate(sup)}'


def case_r2():
    z = np.load(os.path.join(RES, 'fshehta_case.npz'))
    D, zp, X, f = z['D'], z['zp'], z['X'], z['f']
    n = len(D)

    def r2(cols):
        M_ = np.column_stack([np.ones(n)] + cols)
        e = D - M_ @ np.linalg.lstsq(M_, D, rcond=None)[0]
        return 1 - np.var(e) / np.var(D)
    return r2([zp]), r2([X[:, 0], X[:, 1], f])


def fill_numbers(E):
    T29, T30, T31, T32 = E['T29'], E['T30'], E['T31'], E['T32']
    s = {}
    for rho, tag in (('0.9', ''), ('0.98', '_98'), ('0.5', '_50')):
        for k in (2, 8, 64):
            r = T29[f'{rho}_{k}']
            for m in ('naive', 'tsd', 'tsd_ideal', 'phys', 'both'):
                key = {'tsd_ideal': 'ideal'}.get(m, m)
                s[f'{key}{k}{tag}'] = sgn(r[m]['bias_sum'])
            s[f'cf{k}{tag}'] = sgn(r['d1']['bound'])
    r8 = T29['0.9_8']
    s['sd_tsd8'] = f'{r8["tsd"]["sd_sum"]:.2f}'; s['sd_phys8'] = f'{r8["phys"]["sd_sum"]:.2f}'
    s['sd_naive8'] = f'{r8["naive"]["sd_sum"]:.2f}'; s['sd_ideal8'] = f'{r8["tsd_ideal"]["sd_sum"]:.2f}'
    s['cond'] = sci(r8['cond']['tsd_now']); s['cond_phys'] = f'{r8["cond"]["phys"]:.0f}'
    s['cond_naive'] = f'{r8["cond"]["naive"]:.0f}'
    s['limit'] = f'{r8["naive_limit"]:.2f}'
    s['pol_tsd8'] = pct(r8['tsd']['rel_bias_pol']); s['pol_phys8'] = pct(r8['phys']['rel_bias_pol'], 1)
    s['pol_naive8'] = pct(r8['naive']['rel_bias_pol'])
    s['true_sum8'] = f'{sum(r8["beta_true"]):.2f}'
    s['psi1_tsd'] = pct(T30['1.0']['tsd']['rel_bias_b1']); s['psi1_phys'] = pct(T30['1.0']['phys']['rel_bias_b1'])
    s['psi05_tsd'] = pct(T30['0.5']['tsd']['rel_bias_b1']); s['psi05_phys'] = pct(T30['0.5']['phys']['rel_bias_b1'])
    s['psi0_tsd'] = pct(T30['0.0']['tsd']['rel_bias_b1']); s['psi0_naive'] = pct(T30['0.0']['naive']['rel_bias_b1'])
    s['psi0_ideal'] = pct(T30['0.0']['tsd_ideal']['rel_bias_b1'])
    s['psi1_ideal'] = pct(T30['1.0']['tsd_ideal']['rel_bias_b1'])
    s['cov_phys'] = f'{T30["0.0"]["phys"]["cover_b1"]:.2f}'; s['cov_orc'] = f'{T30["0.0"]["oracle"]["cover_b1"]:.2f}'
    b1 = E['T29']['0.9_8']['beta_true'][0]
    pred30 = T31['g0.3']['d4_pred_b1']
    s['d4_10'] = f'{100 * abs(pred30) / 3 / b1:.0f}%'
    s['d4_abs10'] = f'{abs(pred30) / 3:.3f}'
    fit = max(abs(T31[f'g{g}']['phys']['bias_b1'] - T31[f'g{g}']['d4_pred_b1']) / abs(T31[f'g{g}']['d4_pred_b1'])
              for g in (-0.3, -0.15, 0.15, 0.3))
    s['d4_fit'] = f'{100 * fit:.0f}%'
    s['d4_pol30'] = pct(T31['g0.3']['phys']['rel_bias_pol'])
    s['kern_fixed'] = pct(T31['t0.6']['phys']['rel_bias_pol']); s['kern_prof'] = pct(T31['t0.6']['phys_prof']['rel_bias_pol'])
    kf = [T31[f't{x}']['phys']['rel_bias_pol'] for x in ('0.6', '0.8', '1.25', '1.5')]
    kp = [T31[f't{x}']['phys_prof']['rel_bias_pol'] for x in ('0.6', '0.8', '1.25', '1.5')]
    s['kern_fixed_rng'] = f'{pct(max(kf))} to {pct(min(kf))}'
    s['kern_prof_max'] = f'{100 * max(abs(x) for x in kp):.1f}%'
    s['size'] = f'{100 * T32["none"]["reject"]:.1f}%'
    s['size1'] = f'{100 * T32["none"]["reject1"]:.1f}%'
    conf = ('multi_slow', 'multi_fast', 'single', 'wrong_phys')
    s['power'] = f'{100 * min(T32[k]["reject"] for k in conf):.0f}–{100 * max(T32[k]["reject"] for k in conf):.0f}%'
    ps = [T32[k]['tsd_pval'] for k in T32]
    s['tsd_p'] = f'{min(ps):.2f}–{max(ps):.2f}'
    s['rej1_single'] = f'{100 * T32["single"]["reject1"]:.0f}%'
    s['rej1_slow'] = f'{100 * T32["multi_slow"]["reject1"]:.0f}%'
    s['single_pol'] = pct(T32['single']['tsd']['rel_bias_pol'], 1)
    s['single_b1'] = pct(T32['single']['tsd']['rel_bias_b1'])
    s['nrep'] = str(E['nrep'])
    p29 = [T29[f'{rho}_{k}']['tsd_pval'] for rho in ('0.98', '0.9', '0.5') for k in (2, 4, 8, 16, 32, 64)]
    s['tsd_p29'] = f'{min(p29):.2f}–{max(p29):.2f}'
    r2z, r2x = case_r2()
    s['r2_tsd'] = f'{r2z:.2f}'; s['r2_phys'] = f'{r2x:.2f}'
    return s


def t29_rows(E):
    rows = []
    for rho in ('0.98', '0.9', '0.5'):
        for k in (2, 8, 16, 64):
            r = E['T29'][f'{rho}_{k}']
            rows.append([rho, str(k), sgn(r['naive']['bias_sum']), sgn(r['tsd']['bias_sum']),
                         sgn(r['tsd_ideal']['bias_sum']), sgn(r['d1']['bound']), sgn(r['phys']['bias_sum']),
                         f'{r["tsd"]["sd_sum"]:.2f} / {r["phys"]["sd_sum"]:.2f}'])
    return rows


def blocks(E):
    s = fill_numbers(E)
    B = []
    A = B.append
    A(('title', 'State of the art IX: hidden confounders over time'))
    A(('subtitle', 'The Time Series Deconfounder (Bica, Alaa & van der Schaar, ICML 2020) and its supplement, extracted; '
                   'twenty papers from Oxford, Caltech, Harvard and MIT (2020–2026) on hidden confounding in time series; '
                   'our analogues of its Figures 1 and 2 — who confounds the effect of pumping on salinity at '
                   'Fushë-Kuqe; and FSHEHTA-GO, a deconfounder anchored in the physics of the heads'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · review with a numerically tested innovation · companion to reviews '
                 'I–VIII'))
    # ------------------------------------------------------------------------------------------ 1 outcome
    A(('h', '1. Outcome'))
    A(('bbox', [
        '**The article, extracted** (Section 2): the problem and its three assumptions, the factor model over time and '
        'Theorem 1 with the proof of the supplement, the predictive checks, the recurrent factor model, the two outcome '
        'models (marginal structural models and recurrent marginal structural networks), all experiments of the paper '
        'and the supplement with their numbers (Table {{mimic}}), and what the article leaves open.',
        '**Twenty papers, five per institution, 2020–2026, each with links** (Section 4, Figure {{map}}), none of them a '
        'card of reviews I–VIII: substitutes and proxies for hidden confounders over time, panels with latent factors, '
        'checks and bounds, and physical attribution.',
        '**Our analogues of Figures 1 and 2** (Section 5, Figures {{dag}} and {{arch}}, Table {{conf}}). The treatments '
        'are the pumping rates of the $k$ wells, the outcome the salinity. The hidden **multi-cause** confounder is the '
        'dryness — heat and irrigation demand — which raises the pumping of every well and lowers the recharge; a '
        'hidden **single-cause** confounder is the crop stress of one farm, which raises one well\'s pumping and lowers '
        'the local recharge; the recharge is the path through which both reach the salt. Rain and past chloride are '
        'observed; the sea level causes the salinity but not the pumping, so it is not a confounder.',
        f'**Innovation: FSHEHTA-GO** (Section 6). The substitute of the Time Series Deconfounder is built from the past, '
        f'$Z_t=g(\\bar H_{{t-1}})$, so it cannot see the fresh weekly news of a confounder. FSHEHTA-GO builds a second '
        f'substitute from another measurement: the heads, with the known drawdown of the pumping added back and the head '
        f'kernel removed, read the recharge — the path of every hidden cause. Proposition D1: the bias left by any '
        f'history substitute does not vanish with more wells, it grows toward the unadjusted bias ({s["limit"]} in the '
        f'summed effects). Proposition D2: the physics substitute restores ignorability. Proposition D3: a physics '
        f'check falsifies the substitute and the single-cause assumption. Proposition D4: wrong physics leaks a bias '
        f'linear in the drawdown error; the head kernel is identified by the fit.',
        f'**Numbers** (T29–T32, {s["nrep"]} replications). Eight wells: the summed well effects (true sum '
        f'{s["true_sum8"]}) are overstated by {s["naive8"]} without adjustment, {s["tsd8"]} with the learned history '
        f'substitute, {s["ideal8"]} with the best possible one, and {s["phys8"]} with the physics substitute (spread '
        f'{s["sd_phys8"]} against {s["sd_tsd8"]}). Crop stress at one well biases its effect by {s["psi1_tsd"]} with the '
        f'history substitute and {s["psi1_phys"]} with the physics one. The physics check has size {s["size"]} and power '
        f'{s["power"]}; the article\'s predictive check stays at p = {s["tsd_p"]} in every scenario.',
        '**Text for the proposal** (Section 3, Table {{sotab}}) and a plan for Fushë-Kuqe: which loggers, which pumping '
        'test, which records (Section 6.6).']))
    # ------------------------------------------------------------------------------------------ 2 the article
    A(('h', '2. The article, extracted'))
    A(('h2', '2.1 What it is'))
    A(('p', f'Ioana Bica (University of Oxford and the Alan Turing Institute), Ahmed M. Alaa (UCLA) and Mihaela van der '
            f'Schaar (Alan Turing Institute, UCLA and University of Cambridge), *Time Series Deconfounder: Estimating '
            f'Treatment Effects over Time in the Presence of Hidden Confounders*, Proceedings of the 37th International '
            f'Conference on Machine Learning, PMLR 119, 2020 ([PMLR]({PAPER}); code at [github]({CODE})); 12 pages and a '
            f'9-page appendix (A1, A2). The question: estimate how a patient\'s outcome would respond to any future plan '
            f'of several simultaneous treatments, from observational records in which some causes of both the treatments '
            f'and the outcome were never recorded. The answer: exploit the fact that the hidden causes that matter act on '
            f'*several* treatments at once, infer from the pattern of the treatments over time a latent variable that '
            f'renders them conditionally independent, and use it as a substitute for the hidden confounders in a '
            f'standard outcome model. It extends the deconfounder of Wang & Blei (S1) from one time point to time series.'))
    A(('h2', '2.2 The problem and the standard assumptions'))
    A(('p', 'For patient $i$, $X_t\\in\\mathcal{X}_t$ are the time-dependent covariates, $A_t=[A_{t1},\\dots,A_{tk}]$ '
            'the $k$ treatments (causes, binary or continuous) at time $t$, and $Y_{t+1}$ the outcome; $\\bar A_t$ and '
            '$\\bar X_t$ are the histories, and $Y(\\bar a)$ the potential outcome under a treatment course $\\bar a$. The '
            'target is the potential outcome of any plan $\\bar a_{\\geq t}$ that starts at $t$, given the history:'))
    A(('eq', 'tsd1', ['\\left[Y(\\bar a_{\\geq t})\\text{ | }\\bar A_{t-1},\\bar X_t\\right].']))
    A(('p', 'A regression fitted to the observational data estimates $E[Y\\text{ | }\\bar a_{\\geq t},\\bar A_{t-1},\\bar X_t]$, '
            'which equals the target under consistency (Assumption 1: if $\\bar A_{\\geq t}=\\bar a_{\\geq t}$ the '
            'potential outcome is the observed one), positivity (Assumption 2: every treatment has non-zero probability '
            'at every history that occurs) and **sequential strong ignorability**,'))
    A(('eq', 'tsd2', ['Y(\\bar a_{\\geq t})\\perp A_t\\text{ | }\\bar A_{t-1},\\bar X_t\\qquad\\text{for all}\\ \\bar a_{\\geq '
                      't},\\ t\\in\\{0,\\dots,T\\}.']))
    A(('p', 'Ignorability holds if there are no hidden confounders, and it cannot be tested, because it involves the '
            'counterfactual outcomes. With hidden confounders, $Y(\\bar a_{\\geq t})$ and $A_t$ remain dependent given '
            'the observed history, and $E[Y(\\bar a_{\\geq t})\\text{ | }\\bar A_{t-1},\\bar X_t]\\neq E[Y\\text{ | }\\bar a_{\\geq t},'
            '\\bar A_{t-1},\\bar X_t]$ (eq. 3 of A1).'))
    A(('h2', '2.3 The factor model over time and Theorem 1'))
    A(('p', 'At each time the factor model builds a latent variable from the history, $z_t=g(\\bar h_{t-1})$ with '
            '$\\bar h_{t-1}=(\\bar a_{t-1},\\bar x_{t-1},\\bar z_{t-1})$, such that, together with $x_t$, it renders the '
            'treatments conditionally independent, and it is a latent variable model with the joint law [[tsd5]]:'))
    A(('eq', 'tsd4', ['p(a_{t1},\\dots,a_{tk}\\text{ | } z_t,x_t)=\\prod_{j=1}^{k}p(a_{tj}\\text{ | } z_t,x_t),']))
    A(('eq', 'tsd5', ['p(\\theta_{1:k},\\bar x_T,\\bar z_T,\\bar a_T)=p(\\theta_{1:k})\\,p(\\bar x_T)\\prod_{t=1}^{T}\\Big('
                      'p(z_t\\text{ | }\\bar h_{t-1})\\prod_{j=1}^{k}p(a_{tj}\\text{ | } z_t,x_t,\\theta_j)\\Big).']))
    A(('p', 'Figure 1(a) of the article draws this graph for one time step: $\\bar H_{t-1}\\to Z_t$, $Z_t$ and $X_t$ into '
            'every $A_{tj}$, and everything into the next history. Figure 1(b) explains why it works: if another '
            '**multi-cause** hidden confounder $V_t$ were not captured by $Z_t$, the treatments would not be independent '
            'given $Z_t$ and $X_t$ (d-separation), so a factor model that fits rules it out; the argument fails for a '
            '**single-cause** confounder $L_t$ that touches one treatment and the outcome. Hence the one assumption the '
            'method adds, weaker than ignorability:'))
    A(('prop', 'Assumption 3 (sequential single strong ignorability).',
            '$Y(\\bar a_{\\geq t})\\perp A_{tj}\\text{ | } X_t,\\bar H_{t-1}$ for all $\\bar a_{\\geq t}$, all $t$ and all $j$: '
            'there are no hidden single-cause confounders. The more treatments are observed, the weaker it is.'))
    A(('prop', 'Theorem 1 (A1, A2).',
            'If the distribution of the assigned causes $p(\\bar a_T)$ can be written as the factor model '
            '$p(\\theta_{1:k},\\bar x_T,\\bar z_T,\\bar a_T)$, then $Y(\\bar a_{\\geq t})\\perp(A_{t1},\\dots,A_{tk})\\text{ | }'
            '\\bar A_{t-1},\\bar X_t,\\bar Z_t$ for all $\\bar a_{\\geq t}$ and all $t$.'))
    A(('p', '**The proof of the supplement** (A2, Appendix A). *Definition 1* (sequential Kallenberg construction): the '
            'causes admit one at time $t$ if $A_{tj}=f_{tj}(Z_t,X_t,U_{tj})$ for measurable $f_{tj}$ and $U_{tj}$ '
            'marginally uniform on $[0,1]$ with $(U_{t1},\\dots,U_{tk})\\perp Y(\\bar a_{\\geq t})\\text{ | } Z_t,X_t,\\bar '
            'H_{t-1}$. *Lemma 1*: such a construction at every step gives sequential strong ignorability, because the '
            '$A_{tj}$ are then measurable functions of $(Z_t,X_t,U_{t1},\\dots,U_{tk})$ and $\\bar H_{t-1}$ contains '
            '$(\\bar Z_{t-1},\\bar X_{t-1},\\bar A_{t-1})$. *Lemma 2*: a factor model gives the construction, under the '
            'regularity condition that the domains of the causes are Borel subsets of compact intervals. By Lemma 2.22 '
            'of Kallenberg (S4) — a probability kernel into a Borel space is realised by a measurable function of a '
            'uniform variable — $A_{tj}=f_{tj}(Z_t,X_t,U_{tj})$ and $U_{tj}=h_{tj}(\\theta_j,\\omega_{tj})$ with '
            '$\\omega_{tj}$ uniform; the factor model makes the $\\omega_{tj}$ jointly independent; Assumption 3 makes '
            'each $\\omega_{tj}$ independent of $Y(\\bar a_{\\geq t})$ given $(X_t,\\bar H_{t-1})$, and the joint '
            'independence turns this into $(\\omega_{t1},\\dots,\\omega_{tk})\\perp Y(\\bar a_{\\geq t})\\text{ | } X_t,\\bar '
            'H_{t-1}$; since $Z_t$ is built without the potential outcomes and the $\\theta_j$ are point masses, '
            '$(U_{t1},\\dots,U_{tk})\\perp Y(\\bar a_{\\geq t})\\text{ | } Z_t,X_t,\\bar H_{t-1}$. Theorem 1 follows from the '
            'two lemmas.'))
    A(('h2', '2.4 Positivity, predictive checks and identifiability'))
    A(('p', 'The substitute must itself satisfy positivity; it can be enforced by choosing a latent dimension $D_Z$ below '
            'the number of treatments. Whether the fitted factor model captures the distribution of the causes is '
            'assessed by **predictive checks over time**: for the patients of a validation set, $M$ replicas of the '
            'treatments are sampled from the factor model at each time and compared with the actual treatments through'))
    A(('eq', 'tsd8', ['T(a_t)=E_Z\\left[\\log p(a_t\\text{ | } Z_t,X_t)\\right],\\qquad p_t=\\frac{1}{M}\\sum_{i=1}^{M}'
                      '\\mathbf{1}\\left(T(a^{(i)}_{t,\\text{rep}})<T(a_{t,\\text{val}})\\right),']))
    A(('p', 'whose ideal value is 0.5. On identifiability the article cites D\'Amour (S2), who showed static cases in '
            'which the deconfounder is not identified; it answers that the variance of the outcome estimates over '
            'repeated draws of $\\hat Z_t$ reveals non-identifiability (high variance), and that using the substitute '
            'trades confounding bias for estimation variance.'))
    A(('h2', '2.5 The factor model in practice'))
    A(('p', 'Standard factor models (PCA, deep exponential families) are static, so the article builds the factor model '
            'over time as a recurrent network with multitask output and variational dropout (its Figure 2):'))
    A(('eq', 'tsd10', ['Z_1=\\text{RNN}(L),\\qquad Z_t=\\text{RNN}(\\bar Z_{t-1},\\bar X_{t-1},\\bar A_{t-1},L),\\qquad '
                       'A_{tj}=\\text{FC}(X_t,Z_t;\\theta_j),\\ j=1,\\dots,k,']))
    A(('p', 'where $L$ are trainable initial parameters, the recurrent cell is an LSTM, the $k$ fully connected heads '
            '(one hidden layer, sigmoid output for binary treatments, MC dropout for continuous ones) make the treatments '
            'independent given $Z_t$ and $X_t$, and variational dropout in the recurrent part lets one sample $Z_t$ and '
            'treatment replicas for the checks and for the uncertainty. Training: Adam, 100 epochs, 30 iterations of '
            'random search over learning rate (0.01, 0.001, 0.0001), minibatch (64, 128, 256), recurrent units (32 to '
            '256), multitask units (32, 64, 128) and dropout (0.1 to 0.5) (A2, Tables 1–2; more capacity is selected '
            'when the confounding is strong). Baselines: the same network without multitask output, and an MLP factor '
            'model that sees only the previous step (A2, Appendix C). The article notes that dynamic factor models and '
            'factor-augmented autoregressions of econometrics could replace the network.'))
    A(('h2', '2.6 The outcome models'))
    A(('p', 'With the substitutes, the outcome model estimates $E[Y_{t+1}(a_t)\\text{ | }\\bar A_{t-1},\\bar X_t,\\bar Z_t]='
            'h(\\bar A_t,\\bar X_t,\\bar Z_t)$ one step ahead (A2, Appendix D). **Marginal structural models** (S6) weight '
            'each patient by the stabilised weights'))
    A(('eq', 'sw', ['SW_t=\\frac{f(A_t\\text{ | }\\bar A_{t-1})}{f(A_t\\text{ | }\\bar X_t,\\bar Z_t,\\bar A_{t-1})}=\\frac{\\prod_{j=1}'
                    '^{k}f(A_{t,j}\\text{ | }\\bar A_{t-1})}{\\prod_{j=1}^{k}f(A_{t,j}\\text{ | }\\bar X_t,\\bar Z_t,\\bar A_{t-1})},']))
    A(('p', 'with logistic propensity models in the cumulated past treatments, $X_t$, $X_{t-1}$, $Z_t$ and $Z_{t-1}$, and '
            'a weighted linear outcome model in the same terms. **Recurrent marginal structural networks** (S5) estimate '
            'the two propensities and the outcome with three recurrent networks (dropout 0.1; state sizes 6, 16 and 16; '
            'the hyperparameters of S5, A2 Table 5).'))
    A(('h2', '2.7 Experiments and their numbers'))
    A(('p', '**Simulation** (A1, Section 6). $k=3$ observed time-varying covariates, each a single-cause confounder, and '
            'one multi-cause hidden confounder follow $p$-order autoregressions ($p=5$) that depend on the past '
            'treatments:'))
    A(('eq', 'sim', ['X_{t,j}=\\frac{1}{p}\\sum_{i=1}^{p}\\left(\\alpha_{i,j}X_{t-i,j}+\\omega_{i,j}A_{t-i,j}\\right)+'
                     '\\eta_t,\\qquad Z_t=\\frac{1}{p}\\sum_{i=1}^{p}\\left(\\beta_iZ_{t-i}+\\sum_{j=1}^{k}\\lambda_{i,j}A_{t-i,j}'
                     '\\right)+\\epsilon_t,',
                     '\\pi_{tj}=\\gamma_A\\hat Z_t+(1-\\gamma_A)\\hat X_{tj},\\qquad A_{tj}\\text{ | }\\pi_{tj}\\sim\\text{Bernoulli}'
                     '\\left(\\sigma(\\lambda\\pi_{tj})\\right),\\qquad Y_{t+1}=\\gamma_YZ_{t+1}+(1-\\gamma_Y)\\frac{1}{k}\\sum_{j=1}'
                     '^{k}X_{t+1,j},']))
    A(('p', 'with $\\alpha,\\lambda\\sim N(0,0.5^2)$, $\\omega,\\beta\\sim N(1-i/p,(1/p)^2)$, $\\eta_t,\\epsilon_t\\sim '
            'N(0,0.01^2)$, $\\lambda=15$ in the treatment link, hats denoting sums over the last $p$ steps, and $\\gamma_A='
            '\\gamma_Y=\\gamma$ the degree of hidden confounding; 5000 patients, 20 to 30 steps, an 80/10/10 split, 30 '
            'simulated data sets. Results: the predictive p-values of the proposed factor model stay near 0.5 while '
            'those of the MLP factor model decay (Figure 3 of A1); the deconfounded MSM and R-MSN come close to the oracle '
            'that knows $Z_t$, with $D_Z=1$ and with the misspecified $D_Z=5$, do no harm at $\\gamma=0$ (higher variance '
            'only), and fail — no better than no adjustment — when the single-cause confounder $X_1$ is removed, which '
            'violates Assumption 3 (Figure 4 of A1). With a true $D_Z=3$, underestimating it ($D_Z=1$) still helps, and '
            '$D_Z\\geq3$ is better (A2, Appendix E.1). **Note for Section 6:** in this simulation the innovation of the '
            'hidden confounder has standard deviation 0.01, so $Z_t$ is almost a function of the past — the regime in '
            'which a substitute built from the history can work.'))
    A(('p', '**Real data** (A1, Section 7; A2, Appendix E). From MIMIC III, 6256 intensive-care patients, 25 covariates '
            '(lab tests and vital signs), daily aggregates over up to 50 steps, and three simultaneous treatments '
            '(antibiotics, vasopressors, mechanical ventilator); the outcomes are white blood cell count, blood pressure '
            'and oxygen saturation, with comorbidities and some lab tests left out, so hidden confounding is present but '
            'of unknown size. The tumour-growth simulation uses the pharmacokinetic-pharmacodynamic model of chemo- and '
            'radiotherapy with three patient subgroups as a static hidden confounder (10000/1000/1000 patients, 30 data '
            'sets). Table {{mimic}} collects the published root-mean-square errors.'))
    A(('cap', 'Table {{mimic}}. The numbers of the article (RMSE ×10², mean ± standard error). MIMIC III: A1, Table 1 (10 '
              'runs); with 3 covariates removed (temperature, glucose, haemoglobin): A2, Table 7; tumour growth '
              '(normalised by the maximum volume): A2, Table 6.'))
    A(('table', ['Setting', 'Model', 'Confounded', 'D_Z = 1', 'D_Z = 5', 'D_Z = 10', 'D_Z = 20 or other'],
       [['MIMIC, white blood cells', 'MSM', '3.90 ± 0.00', '3.55 ± 0.05', '3.56 ± 0.04', '3.58 ± 0.03', '3.54 ± 0.04'],
        ['', 'R-MSN', '2.91 ± 0.05', '2.62 ± 0.07', '2.41 ± 0.04', '2.48 ± 0.06', '2.55 ± 0.05'],
        ['MIMIC, blood pressure', 'MSM', '12.04 ± 0.00', '11.69 ± 0.14', '11.63 ± 0.10', '11.66 ± 0.14', '11.57 ± 0.12'],
        ['', 'R-MSN', '10.29 ± 0.05', '9.35 ± 0.11', '9.45 ± 0.10', '9.20 ± 0.12', '9.63 ± 0.14'],
        ['MIMIC, oxygen saturation', 'MSM', '2.92 ± 0.00', '2.42 ± 0.02', '2.43 ± 0.02', '2.42 ± 0.01', '2.40 ± 0.01'],
        ['', 'R-MSN', '1.74 ± 0.03', '1.24 ± 0.05', '1.21 ± 0.07', '1.17 ± 0.06', '1.28 ± 0.08'],
        ['MIMIC, 3 covariates removed (white blood cells)', 'MSM', '3.90 all; 4.12 removed', '3.98 ± 0.02',
         '3.85 ± 0.04', '—', 'D_Z = 3: 3.91 ± 0.03'],
        ['', 'R-MSN', '2.91 all; 3.11 removed', '3.05 ± 0.05', '2.81 ± 0.03', '—', 'D_Z = 3: 2.87 ± 0.08'],
        ['Tumour growth', 'MSM', '7.29 ± 0.14', '6.47 ± 0.16', '6.25 ± 0.14', '6.31 ± 0.11', 'oracle 6.92 ± 0.19'],
        ['', 'R-MSN', '5.31 ± 0.16', '4.76 ± 0.17', '4.79 ± 0.19', '4.54 ± 0.17', 'oracle 5.00 ± 0.15']],
       [3.6, 1.4, 2.6, 2.3, 2.3, 2.3, 2.5], 8.5, True))
    A(('p', 'In the tumour case the deconfounded models beat the oracle that knows the subgroups, because $\\bar Z_t$ also '
            'carries time dependence (A2, E.2). On MIMIC the article stresses that the results need clinical validation.'))
    A(('h2', '2.8 What the article leaves open'))
    A(('p', 'Its own discussion (A2, Appendix F) names identifiability (D\'Amour, S2; Kong et al. 2019; Wang & Blei '
            '2019b) and proxy variables in the outcome model (Miao et al., S3) as future work. Three further limits matter '
            'for an aquifer. (i) **The substitute is built from the past**: a hidden confounder with large fresh '
            'innovations — a heat wave that makes every farmer pump this week — is invisible to $g(\\bar H_{t-1})$; '
            'the article\'s simulation avoids the case (innovation 0.01). (ii) **Assumption 3 is untestable** and the '
            'predictive check cannot see its violation, nor a common innovation (Section 6.4). (iii) **No physics**: '
            'where a second measurement of the confounding path exists, as the heads measure the recharge, the method '
            'has no way to use it. FSHEHTA-GO addresses all three.'))
    # ------------------------------------------------------------------------------------------ 3 SOTA
    A(('h', '3. State of the art and the step beyond it'))
    A(('p', 'Reviews I–VIII (D1) guarantee bands for the boundary conditions, the recharge coefficient, the dispersion '
            'and the inputs of the Fushë-Kuqe aquifer when only the rain is known, and compute counterfactuals of the '
            'recharge, the heads and the salt. All of them treat the pumping as known and exogenous. It is neither: the '
            'pumping responds to the same dryness that lowers the recharge, so any estimate of what a cut in pumping '
            'would do to the salt is confounded.'))
    A(('p', '**Text for the proposal.** Causal inference with hidden confounders over time has advanced through '
            'substitutes inferred from many causes, latent-factor panels, proxies and negative controls, instruments and '
            'bounds (Sections 2 and 4). All of them build their substitute from the treatments or from the outcomes, '
            'and none can see a confounder\'s fresh innovations or test the single-cause assumption. The project goes '
            'beyond the state of the art by reading the hidden confounding path — the recharge — from a second, physical '
            'measurement, the heads, through the known drawdown of the wells (FSHEHTA-GO); by proving that substitutes '
            'built from the past leave a bias that grows with the number of wells; by a calibrated physics check of the '
            'substitute and of the single-cause assumption; and by an explicit bias band for wrong physics, so that the '
            'effect of a pumping policy on the salinity of the Fushë-Kuqe aquifer can be estimated with its '
            'confounding removed and its remaining assumptions priced.'))
    A(('cap', 'Table {{sotab}}. State of the art (2020–2026) and the step beyond it. Card numbers refer to Section 4; T '
              'numbers to the tests of Section 6; TSD is the article of Section 2.'))
    A(('table', ['Topic', 'State of the art', 'Its limit for our problem', 'Our step beyond', 'Evidence'],
       SOTA_ROWS(s), [2.5, 4.0, 3.2, 3.8, 3.5], 9, False))
    # ------------------------------------------------------------------------------------------ 4 papers
    A(('h', '4. The twenty papers'))
    A(('p', 'Five papers per institution, 2020–2026 in the version cited (Figure {{map}}), with a link to the institution '
            'at the time (JPL for Caltech), a state-of-the-art contribution, and no paper that was a card before (checked '
            'against reviews I–VIII and the covered-references list). Each card states the main result as the search '
            'results quote or closely paraphrase it, what it cannot yet do for us, three lessons (inputs, dispersion, '
            'boundary conditions) and an innovation step tied to the numbers of Section 6. Six are preprints or working '
            'papers (C3, H2, H4, M2, M3, M5), marked as such.'))
    A(('p', '**Verification.** doi.org, arxiv.org, proceedings.mlr.press, proceedings.neurips.cc and most publisher pages '
            'could not be opened in this environment; landing pages were reached through search results that quote '
            'them, and every card is marked partly verified, with what could not be confirmed.'))
    names_i = dict(Oxford='University of Oxford', Caltech='California Institute of Technology (with JPL)',
                   Harvard='Harvard University', MIT='Massachusetts Institute of Technology')

    def filled(c):
        c = dict(c)
        for k_, v_ in c.items():
            if isinstance(v_, str) and '<<' in v_:
                for key_, val_ in s.items():
                    v_ = v_.replace(f'<<{key_}>>', val_)
                assert '<<' not in v_, (c['id'], v_)
                c[k_] = v_
        return c
    for j, inst in enumerate(INST_ORDER, start=1):
        A(('h2', f'4.{j} {names_i[inst]}'))
        first = True
        for c in CARDS:
            if c['inst'] == inst:
                A(('card', filled(c)))
                if first and inst == 'Oxford':
                    A(('img', 'map', 17.0))
                    A(('cap', 'Figure {{map}}. The twenty papers against the step of the method they serve and the '
                              'unknown they inform. Colour gives the institution; a filled square is a direct lesson, an '
                              'open square an indirect one.'))
                first = False
    # ------------------------------------------------------------------------------------------ 5 our schemes
    A(('h', '5. Our schemes: who confounds the pumping at Fushë-Kuqe'))
    A(('p', 'The translation is direct. A "patient" is the aquifer, a "time step" a week, the $k$ treatments the pumping '
            'rates $A_{tj}$ of the wells, the outcome the salinity $Y_t$ (the chloride at the monitored screens, or the '
            'salinized area of review VIII), the observed covariates $X_t$ the rain $f_t$ and the past heads and '
            'chloride. Figure {{dag}} redraws the article\'s Figure 1(b) next to our case.'))
    A(('p', '**Who is a confounder, and who is not.** A confounder causes both the pumping and the salinity by a path that '
            'does not go through the pumping. Table {{conf}} sorts the variables of the problem by this rule and says '
            'what each needs.'))
    A(('img', 'dag', 17.0))
    A(('cap', 'Figure {{dag}}. Our analogue of Figure 1 of the article. (a) The graphical factor model of the Time Series '
              'Deconfounder, after its Figure 1(b): the substitute $Z_t$ is built from the history and catches the '
              'multi-cause $V_t$ but not the single-cause $L_t$. (b) Fushë-Kuqe: the dryness $D_t$ (heat, irrigation '
              'demand) drives every well and lowers the recharge, the crop stress $L_t$ of one farm drives one well and '
              'the local recharge, and both reach the salinity only through the recharge, which the heads see once the '
              'known drawdown of the pumping is accounted for. The sea level causes the salinity but not the pumping.'))
    A(('cap', 'Table {{conf}}. The variables of the pumping–salinity problem in the language of the Time Series '
              'Deconfounder, and how FSHEHTA-GO treats them.'))
    A(('table', ['Variable', 'Role', 'Observed?', 'Acts on', 'Treatment in FSHEHTA-GO'],
       [['Pumping of well $j$, $A_{tj}$', 'treatment (one of k causes)', 'yes, if metered (electricity or flow)',
         'heads (drawdown), salinity', 'the effect sought, $\\beta_j$ and the 20% cut'],
        ['Salinity $Y_t$', 'outcome', 'sparse samples, loggers', '—', 'outcome model'],
        ['Rain $f_t$', 'observed covariate; a confounder if pumping reacts to it', 'yes',
         'recharge, and pumping through irrigation', 'adjusted as $X_t$'],
        ['Dryness $D_t$: heat, evaporative and irrigation demand', 'hidden multi-cause confounder ($V_t$ of the article)',
         'no (evapotranspiration maps only in part)', 'all wells (up), recharge (down)',
         'physics substitute; the history substitute only for its predictable part'],
        ['Crop stress $L_t$ of one farm, a broken canal', 'hidden single-cause confounder ($L_t$ of the article)', 'no',
         'one well (up), local recharge or return flow (down)', 'a logger near that well; the physics check'],
        ['Recharge $R_t$, regional and local', 'mediator of the confounding: the path of $D_t$ and $L_t$', 'no (only the rain)',
         'heads, salinity', 'read from the heads (Proposition D2)'],
        ['Past heads and chloride', 'history; managers react to them (feedback)', 'yes', 'next pumping',
         'in the history; adjusted'],
        ['Surface-water deliveries', 'possible multi-cause confounder', 'partly (irrigation board)',
         'pumping (down), return-flow recharge (up)', 'covariate if the records exist; else in $R_t$'],
        ['Well properties: $T$, $S$, screen depth, distance to the coast', 'static confounder (farmers pump where it pays)',
         'partly', 'pumping, salinity response', 'well fixed effects, the $\\beta_j$ themselves'],
        ['Sea level, tide', 'cause of the salinity only', 'yes (tide gauge)', 'salinity, heads',
         'not a confounder; a precision covariate']],
       [3.2, 3.3, 2.7, 3.4, 4.4], 8.5, False))
    A(('p', 'Figure {{arch}} is our analogue of the article\'s Figure 2: the recurrent factor model becomes the history '
            'branch, and a physics branch is added next to it.'))
    A(('img', 'arch', 17.0))
    A(('cap', 'Figure {{arch}}. Our analogue of Figure 2 of the article. History branch: the factor model over time of the '
              'pumping (a recurrent network in the article, a dynamic factor model with a Kalman filter here) gives the '
              'substitute $\\hat Z_t$ and the predictive check. Physics branch: the logger heads, with the drawdown of '
              'the known pumping added back (drawdown coefficients $g$ from a pumping test) and the head kernel '
              'deconvolved (its time constant profiled on the salinity fit), give the recharge reading $\\hat R_t$. The '
              'physics check tests $A\\perp\\hat R\\text{ | }\\hat Z$; the outcome model uses the reading and returns the well '
              'effects and the policy effect with the error band of Proposition D4.'))
    # ------------------------------------------------------------------------------------------ 6 FSHEHTA-GO
    A(('h', '6. Innovation: FSHEHTA-GO, a deconfounder anchored in the heads'))
    A(('h2', '6.1 The test bed'))
    A(('p', 'A linear-response coastal aquifer in weekly steps, the first order of the Strack potential, which is linear '
            'in recharge and pumping for a fixed conductivity field (review VIII). With $k_\\tau$ the exponential kernel '
            '$(k_\\tau*x)_t=a(k_\\tau*x)_{t-1}+(1-a)x_t$, $a=e^{-1/\\tau}$:'))
    A(('eq', 'bed', ['D_t=\\rho_DD_{t-1}+\\nu_t,\\qquad L_t=0.9L_{t-1}+\\xi_t,\\qquad R_t=\\kappa f_t-bD_t+e_t,\\qquad '
                     'R^{\\text{loc}}_t=-b_LL_t,',
                     'A_{tj}=\\mu+\\lambda D_t+\\psi\\,\\mathbf{1}\\{j=1\\}L_t+\\varepsilon_{tj},',
                     'Y_t=\\sum_{j}\\beta_j(k_S*A_j)_t-\\rho\\,(k_S*R)_t-\\rho_L(k_S*R^{\\text{loc}})_t+\\eta_t,',
                     'H_{mt}=-\\sum_{j}g_{mj}(k_H*A_j)_t+q_m(k_H*R)_t+q^L_m(k_H*R^{\\text{loc}})_t+e^h_{mt}.']))
    A(('p', '$D_t$ (unit variance, persistence $\\rho_D$) is the hidden dryness, $L_t$ the crop stress near well 1, '
            '$f_t$ the seasonal rain (observed), $Y_t$ a salinity index with a 10-week kernel, $H_{mt}$ two head loggers '
            'with a 4-week kernel, one next to well 1 and one inland. The $k$ wells lie 0.5–4 km along the coast, with '
            '$\\beta_j=0.4e^{-x_j/1.5}$ and drawdown coefficients $g_{mj}=0.3e^{-|x_m-x_j|}$; $\\lambda=0.5$, '
            '$\\sigma_\\varepsilon=0.5$, $\\kappa=0.35$, $b=0.3$, $b_L=0.3$, $\\rho=\\rho_L=1$, $q=(0.5,0.5)$, $q^L=(0.5,'
            '0.02)$, logger noise 1 cm, 520 weeks after a 104-week burn-in. The estimands are the $\\beta_j$ and the effect '
            'of a 20% cut of all pumping, $-0.2\\mu\\sum_j\\beta_j$.'))
    A(('p', '**Estimators** (least squares on the convolved regressors, Newey–West errors). *No adjustment*: $Y$ on '
            '$k_S*A_j$ and $k_S*f$. *TSD substitute*: plus $\\hat Z_t$ and $k_S*\\hat Z_t$, where $\\hat Z_t=E[Z_t\\text{ | } '
            'A_1,\\dots,A_{t-1}]$ is the Kalman prediction of a one-factor dynamic factor model of the pumping — the '
            'linear-Gaussian counterpart of the article\'s recurrent factor model, $Z_t=g(\\bar H_{t-1})$. *Best history '
            'substitute*: plus $Z^*_t=E[D_t\\text{ | }\\bar D_{t-1}]=\\rho_DD_{t-1}$ and $k_S*Z^*_t$, an oracle bound for any '
            'substitute built from the past. *Static substitute*: the factor score of the current pumping (the '
            'deconfounder of S1). *Physics substitute*: plus $k_S*\\hat R_m$, with'))
    A(('eq', 'read', ['\\hat R_{mt}=\\frac{\\tilde H_{mt}-a_H\\tilde H_{m,t-1}}{1-a_H},\\qquad\\tilde H_{mt}=H_{mt}+'
                      '\\sum_{j}\\hat g_{mj}(k_{\\hat\\tau_H}*A_j)_t,']))
    A(('p', 'the head of logger $m$ with the known drawdown added back and the head kernel removed; with the profiled '
            'kernel, $\\hat\\tau_H$ minimises the residual sum of squares of the outcome regression over a grid. *True '
            'recharge*: the oracle.'))
    A(('h2', '6.2 Propositions'))
    A(('prop', 'Proposition D1 (history substitutes and the curse of many causes).',
            'Let the wells be exchangeable ($\\psi=0$), let $W$ be the controls of an estimator and $\\tilde d$, $\\tilde '
            'A_j$ the residuals of $k_S*D$ and $k_S*A_j$ after projection on $W$. The large-sample bias of the summed '
            'effects is [[d1]]. If $W$ is a function of the past and independent of the idiosyncratic pumping, then '
            '$\\text{Var}\\,\\tilde d\\geq v=(1-a_S)^2(1-\\rho_D^2)$ and the bias is at least [[d1b]], with equality for '
            'the best history substitute; this bound increases with $k$ to $\\rho b/\\lambda$, the limit of the '
            'unadjusted estimator. A substitute that is a function of the current pumping instead makes the design '
            'singular.'))
    A(('eq', 'd1', ['B(W)=\\sum_{j=1}^{k}(\\hat\\beta_j-\\beta_j)=\\frac{\\rho\\,b\\,k\\,\\sigma_{Ad}}{\\sigma_A^2+(k-1)'
                    '\\sigma_{AA\'}},',
                    '\\sigma_{Ad}=\\text{Cov}(\\tilde A_j,\\tilde d),\\qquad\\sigma_A^2=\\text{Var}\\,\\tilde A_j,\\qquad'
                    '\\sigma_{AA\'}=\\text{Cov}(\\tilde A_j,\\tilde A_l),\\ j\\neq l,']))
    A(('eq', 'd1b', ['B^*=\\frac{k\\,\\lambda\\,\\rho\\,b\\,v}{v_\\varepsilon+k\\,\\lambda^2v},\\qquad v_\\varepsilon='
                     '\\sigma_\\varepsilon^2\\frac{1-a_S}{1+a_S},\\qquad\\lim_{k\\to\\infty}B^*=\\frac{\\rho\\,b}{\\lambda}.']))
    A(('proof', 'The recharge brings the confounding term $\\rho\\,b\\,(k_S*D)$ into $Y$; after the controls, by '
                'Frisch–Waugh–Lovell, $\\hat\\beta-\\beta\\to\\Sigma_{\\tilde A\\tilde A}^{-1}\\Sigma_{\\tilde A u}$ with '
                '$u=\\rho b\\tilde d$. Exchangeability gives $\\Sigma_{\\tilde A\\tilde A}=(\\sigma_A^2-\\sigma_{AA\'})I+'
                '\\sigma_{AA\'}\\mathbf{1}\\mathbf{1}^\\top$ and $\\Sigma_{\\tilde Au}=\\rho b\\sigma_{Ad}\\mathbf{1}$; '
                'Sherman–Morrison gives $\\mathbf{1}^\\top\\Sigma^{-1}=\\mathbf{1}^\\top/(\\sigma_A^2+(k-1)\\sigma_{AA\'})$, '
                'hence [[d1]]. If $W$ is independent of $\\varepsilon$, $\\tilde A_j=\\lambda\\tilde d+k_S*\\varepsilon_j$, so '
                '$\\sigma_{Ad}=\\lambda v_d$, $\\sigma_A^2=\\lambda^2v_d+v_\\varepsilon$, $\\sigma_{AA\'}=\\lambda^2v_d$ and '
                '$B=k\\lambda\\rho bv_d/(v_\\varepsilon+k\\lambda^2v_d)$, increasing in $v_d=\\text{Var}\\,\\tilde d$. Since '
                '$(k_S*D)_t=a_S(k_S*D)_{t-1}+(1-a_S)\\rho_DD_{t-1}+(1-a_S)\\nu_t$ and $\\nu_t$ is independent of the past, '
                'no function of the past removes $(1-a_S)\\nu_t$: $v_d\\geq v$, with equality when $W$ spans '
                '$D_{t-1}$ and $(k_S*D)_{t-1}$, which $Z^*_t$ and $k_S*Z^*_t=\\rho_D(k_S*D)_{t-1}$ do. $B^*$ increases in '
                '$k$ and tends to $\\rho b/\\lambda$; the unadjusted estimator has the same limit because its $v_d=\\text{Var}(k_S*D)>v$. A substitute that is a linear function of $A_t$ makes $k_S*\\hat Z$ a linear combination of '
                'the $k_S*A_j$.'))
    A(('p', 'In words: with many wells the idiosyncratic pumping, which identifies the effect, averages out of the total, '
            'while the part of the dryness that the past cannot predict stays; the regression then credits the pumping '
            'with the salt that the fresh dryness brought. The "blessing of multiple causes" (S1) holds for substitutes '
            'built from the present, which positivity forbids; for substitutes built from the past it turns into a '
            'curse.'))
    A(('prop', 'Proposition D2 (the physics substitute).',
            'Assume (E) the hidden causes reach the salinity only through the recharge components $r_t=(R_t,R^{\\text{loc}}_t)$'
            ', and (P) the heads are linear in pumping and recharge, with known drawdown $g$ and head kernel '
            '$k_H$, and the matrix $Q=[q,q^L]$ (loggers × recharge components) has full column rank. Then $\\hat R_t=Qr_t'
            '+\\tilde e_t$ with $\\tilde e_t$ the logger noise filtered by the inverse kernel, independent of the pumping, '
            'and the regression of $Y$ on $k_S*A_j$, $k_S*f$ and $k_S*\\hat R$ estimates $\\beta$ with no confounding bias; '
            'what remains is an errors-in-variables bias that vanishes with the logger noise.'))
    A(('proof', 'Adding back $\\sum_jg_{mj}(k_H*A_j)$ removes the pumping from $H_m$ exactly, and deconvolving $k_H$ '
                'inverts the kernel: $(\\tilde H_t-a_H\\tilde H_{t-1})/(1-a_H)$ applied to $k_H*x$ returns $x_t$. So '
                '$\\hat R_t=Qr_t+\\tilde e_t$. With $c=(-\\rho,-\\rho_L)$ and logger weights $w$ such that $w^\\top Q=c$, '
                'which exist because $Q$ has full column rank, $Y=\\sum_j\\beta_jk_S*A_j+w^\\top k_S*\\hat R+\\eta-w^\\top k_S*\\tilde '
                'e$; by (E) the hidden causes enter $Y$ only through $r$, so given $k_S*\\hat R$ the error is independent '
                'of the pumping up to the term in $\\tilde e$, which is correlated with the regressor $k_S*\\hat R$ only '
                '(errors in variables) and has variance proportional to the logger noise.'))
    A(('p', 'The rank condition is the physical form of Assumption 3: instead of "every hidden cause reaches two '
            'treatments", it reads "every hidden cause leaves a recharge footprint that a logger sees". Unlike '
            'Assumption 3, it can be met by design — by placing a logger next to the well whose farm is suspect.'))
    A(('prop', 'Proposition D3 (the physics check).',
            'Under (E) and (P), if the substitute $\\hat Z_t$ deconfounds the pumping, $A_t\\perp r_t\\text{ | }\\hat Z_t,f_t$, '
            'then $A_t\\perp\\hat R_t\\text{ | }\\hat Z_t,f_t$, so the coefficient of $\\hat R_t$ is zero in the regression of every '
            '$A_{tj}$ on $(1,\\hat Z_t,f_t,\\hat R_t)$. A significant coefficient falsifies the substitute — a missed '
            'multi-cause innovation or a single-cause confounder near a logger — or the physics (P). The statistic '
            '$S=\\max_{j,m}|t_{jm}|$ is calibrated by circular time shifts of the residualised reading, which keep the '
            'autocorrelation of both series and break any link between them.'))
    A(('proof', '$\\hat R_t=Qr_t+\\tilde e_t$ with $\\tilde e\\perp A$; independence of $A_t$ and $r_t$ given $(\\hat Z_t,'
                'f_t)$ carries over to any function of $r_t$ and an independent noise. Under the null the shifted readings '
                'are draws of a series independent of the pumping with the same autocorrelation, so the rank of $S$ among '
                'the shifted statistics is approximately uniform.'))
    A(('p', 'The article\'s predictive check cannot do this: its statistic $E_Z[\\log p(a_t\\text{ | } Z_t,X_t)]$ sums '
            'per-treatment log-likelihoods, whose expectation is unchanged when the residuals share a common innovation, '
            'so the mean predictive p-value stays near 0.5 when the substitute misses a confounder.'))
    A(('prop', 'Proposition D4 (wrong physics).',
            '(i) If the drawdown coefficients are wrong by a factor $1+\\gamma$, $\\hat g=(1+\\gamma)g$, the physics '
            'estimator converges to $\\beta_j-\\gamma\\sum_mw_mg_{mj}$, with $w$ the weights of Proposition D2: a bias '
            'linear in $\\gamma$, invisible to the fit (the residual is unchanged) but caught by the physics check. (ii) A '
            'wrong head kernel leaves a residual in the fit, so $\\tau_H$ is identified by the salinity fit, and '
            'profiling it removes the bias.'))
    A(('proof', '(i) With $\\hat g=(1+\\gamma)g$ and the right kernel, $\\hat R_t=Qr_t+\\gamma gA_t+\\tilde e_t$, so $w^\\top '
                'k_S*\\hat R=w^\\top Qk_S*r+\\gamma\\sum_j(w^\\top g)_jk_S*A_j+\\dots$ and the coefficient of $k_S*A_j$ '
                'absorbs $-\\gamma(w^\\top g)_j$; the fitted values, hence the residual, do not change, while $\\hat R$ now '
                'contains $A_t$ and the check rejects. (ii) With $\\hat\\tau_H\\neq\\tau_H$, $k_S*\\hat R$ is a different '
                'filter of $r$ plus a filtered pumping term, which no linear combination of the regressors turns into '
                '$w^\\top Qk_S*r$ when the recharge has a non-degenerate spectrum; the residual variance exceeds that of '
                '$\\eta$, which the true kernel attains.'))
    A(('h2', '6.3 What the history can and cannot see'))
    A(('img', 'case', 17.0))
    A(('cap', f'Figure {{{{case}}}}. Two years of one simulated case: the hidden dryness, its best linear reading from the '
              f'history substitute (R² = {s["r2_tsd"]}) and from the two heads and the rain (R² = {s["r2_phys"]}).'))
    A(('p', f'The reading from the heads is not much more accurate in R² ({s["r2_phys"]} against {s["r2_tsd"]}); what '
            f'matters is *where* each errs. The history substitute lags the dryness and misses every fresh rise — '
            f'exactly the weeks in which all farmers pump harder — so its error is correlated with the pumping. The '
            f'reading from the heads errs by logger noise and by the recharge noise, which is independent of the '
            f'pumping. Confounding bias depends on the first kind of error only.'))
    A(('h2', '6.4 Tests T29–T32'))
    A(('p', f'**T29 — many wells, slow and fast dryness** (Proposition D1; Figure {{{{d1}}}}, Table {{{{t29}}}}). For '
            f'persistence 0.98, 0.9 and 0.5 and 2 to 64 wells. The unadjusted bias of the summed effects sits at the limit '
            f'$\\rho b/\\lambda$ = {s["limit"]}. The learned history substitute removes little ({s["tsd8"]} at 8 wells, '
            f'persistence 0.9). Even the best history substitute leaves {s["ideal8"]} at 8 wells and {s["ideal64"]} at '
            f'64, matching the closed form [[d1b]] ({s["cf8"]}, {s["cf64"]}); with a fast dryness (0.5) it leaves '
            f'{s["ideal8_50"]} at 8 wells. The physics substitute is unbiased at every $k$ ({s["phys8"]}), with a Monte '
            f'Carlo spread of {s["sd_phys8"]} against {s["sd_tsd8"]} for the learned substitute and {s["sd_ideal8"]} '
            f'for the best one: the reading explains outcome variance instead of removing treatment variation. The '
            f'static substitute makes the design singular (condition number {s["cond"]} against {s["cond_phys"]} for '
            f'the physics design), and its estimates are meaningless. For the 20% cut at 8 wells the relative bias is '
            f'{s["pol_naive8"]} unadjusted, {s["pol_tsd8"]} with the learned substitute and {s["pol_phys8"]} with the '
            f'physics one. The article\'s predictive check gives p = {s["tsd_p29"]} throughout.'))
    A(('img', 'd1', 17.0))
    A(('cap', 'Figure {{d1}}. T29: bias of the summed well effects $\\Sigma_j\\beta_j$ against the number of wells, for three '
              'persistences of the hidden dryness (95% Monte Carlo intervals). The best history substitute follows the '
              'closed form of Proposition D1 and climbs to the unadjusted limit; the physics substitute stays at zero.'))
    A(('cap', f'Table {{{{t29}}}}. T29: bias of $\\Sigma_j\\beta_j$ (true sum about 1 at 8 wells) and the Monte Carlo spread '
              f'of the learned history and the physics substitutes ({s["nrep"]} replications up to 16 wells, half as many '
              f'beyond).'))
    A(('table', ['Persistence ρ', 'Wells k', 'No adjustment', 'TSD, learned', 'Best history', 'D1 closed form', 'Physics',
                 'Spread TSD / physics'], t29_rows(E), [1.2, 1.0, 2.3, 2.3, 2.3, 2.4, 2.0, 3.5], 9, True))
    A(('p', f'**T30 — a single-cause confounder** (crop stress at well 1, persistence 0.98, 8 wells; Figure '
            f'{{{{checks}}}}a). Without it ($\\psi=0$) the effect of well 1 is overstated by {s["psi0_naive"]} unadjusted, '
            f'{s["psi0_tsd"]} with the learned and {s["psi0_ideal"]} with the best history substitute. With it '
            f'($\\psi=1$) no history substitute helps ({s["psi1_tsd"]} learned, {s["psi1_ideal"]} best), as Assumption 3 '
            f'predicts, while the logger next to well 1 lets the physics substitute bring the bias to {s["psi1_phys"]} '
            f'(the remainder is errors in variables). A single-cause confounder biases the effect of its well, not the '
            f'uniform cut: in T32 it moves $\\beta_1$ by {s["single_b1"]} but the 20% cut by {s["single_pol"]}, because '
            f'the other wells carry the common part. What one wants to decide — which well to close, or how much to cut '
            f'overall — decides which confounder hurts.'))
    A(('p', f'**T31 — wrong physics** (Proposition D4; Figure {{{{checks}}}}b, c). Drawdown coefficients 15% and 30% off '
            f'shift $\\beta_1$ linearly, {s["d4_10"]} of $\\beta_1$ per 10% of error, as predicted to within '
            f'{s["d4_fit"]}; a 30% overestimate biases the 20% cut by {s["d4_pol30"]}. The fit cannot see this, so the '
            f'drawdown must come from a pumping test, and its uncertainty enters as the band of D4. A wrong head kernel '
            f'(time constant 0.6 to 1.5 times the truth) biases the cut by {s["kern_fixed_rng"]} when kept fixed; profiled '
            f'on the salinity fit, the true time constant is recovered in every replication and the bias stays within '
            f'{s["kern_prof_max"]}.'))
    A(('p', f'**T32 — the two checks** (Proposition D3; Figure {{{{checks}}}}d; {s["nrep"]} replications, 99 shifts). '
            f'Without confounding the physics check rejects in {s["size"]} of the replications at the 5% level (well 1 '
            f'alone {s["size1"]}); with a slow or fast multi-cause dryness, a single-cause stress at well 1, or drawdown '
            f'coefficients 30% off, it rejects in {s["power"]}. The predictive check of the article returns p = '
            f'{s["tsd_p"]} in all five scenarios: it cannot tell them apart.'))
    A(('img', 'checks', 17.0))
    A(('cap', 'Figure {{checks}}. (a) T30: bias of the effect of well 1 under a single-cause confounder of strength ψ. '
              '(b) T31: bias of $\\beta_1$ under wrong drawdown coefficients, simulated and predicted by Proposition D4. '
              '(c) T31: bias of the 20% cut under a wrong head kernel, fixed and profiled. (d) T32: rejection rate of the '
              'physics check at the 5% level (green) and the mean predictive p-value of the Time Series Deconfounder '
              '(orange), in five scenarios.'))
    A(('h2', '6.5 What is new'))
    A(('b', '**A substitute from a second measurement.** Every method of Sections 2 and 4 builds its substitute from the '
            'treatments, the outcomes or their time order. FSHEHTA-GO builds it from the heads, through the part of the '
            'physics that is known (drawdown, head kernel), and leaves to statistics only what is not (dryness, crop '
            'stress).'))
    A(('b', '**The curse of many causes for history substitutes** (D1): a closed-form bias that grows with the number of '
            'wells, explaining why the article\'s simulation (innovation 0.01) works and a heat wave would not.'))
    A(('b', '**Assumption 3 made testable and designable** (D2, D3): the single-cause assumption becomes a rank condition '
            'on the loggers, met by placing them, and checked by a calibrated test that the article\'s predictive '
            'check cannot replace.'))
    A(('b', '**Priced physics** (D4): a wrong drawdown leaks a bias linear in its error — a band from the pumping-test '
            'uncertainty — and a wrong head kernel is corrected by the fit itself.'))
    A(('h2', '6.6 What it takes at Fushë-Kuqe'))
    A(('p', 'Four records, three of which the project already plans (D2): (i) weekly pumping per well or well group, '
            'from meters or electricity bills (==number of metered wells to be confirmed with the water utility and the '
            'irrigation board==); (ii) at least two head loggers, one next to the well group whose farms are most likely '
            'to pump for local reasons and one inland, with 1 cm resolution; (iii) one step-drawdown or interference '
            'pumping test per well group, for the drawdown coefficients $g$ and their uncertainty, which sets the band of '
            'Proposition D4; (iv) the rain series and the chloride sampling of reviews I–VIII. The outcome model then '
            'estimates the effect on the salinity of each well group and of a uniform cut, with the physics check run '
            'before any effect is reported.'))
    # ------------------------------------------------------------------------------------------ 7 synthesis
    A(('h', '7. Synthesis and limits'))
    A(('p', 'The Time Series Deconfounder turns many treatments into a lever on hidden confounders: if a hidden cause '
            'acts on several treatments, their pattern over time reveals it. Our problem has many treatments — the '
            'wells — and a hidden cause that acts on all of them, so the lever applies; but the cause is weather-driven, '
            'with large weekly news, and the lever only reaches what the past predicts. The aquifer offers what a '
            'hospital ward does not: a second, physical measurement of the confounding path. Reading the recharge from '
            'the heads removes the confounding that the history leaves, sees a single-cause confounder near a logger, '
            'and turns the untestable assumption into a designable and testable one. The twenty papers supply the '
            'pieces around it: proxies and negative controls (O2, H5, M5), panels and latent factors (O3, O5, M1, M3, '
            'M4), instruments and bounds (H1, H4), checks (O1, M4), and physical attribution (C1, C4, C5).'))
    A(('p', '**Limits.** The test bed is linear and Gaussian; the salinity of review VIII is nonlinear in the state, and '
            'the drawdown of an unconfined aquifer is linear only for small drawdowns. Assumption (E) fails if a hidden '
            'cause acts on the salt directly — for instance, salt carried by irrigation return flow — and then a third '
            'measurement (the chloride of the return flow) is needed. The physics check is joint: a rejection says that '
            'the substitute or the physics is wrong, not which. The Newey–West intervals under-cover in all estimators, '
            'the oracle included (coverage of $\\beta_1$ about ' + s['cov_orc'] + ' at a nominal 0.90), so coverage '
            'statements need a block bootstrap. The cards are partly verified (Section 4).'))
    A(('refs',))
    return B
