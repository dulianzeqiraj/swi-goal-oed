"""Working document: rain, infiltration and soil moisture from groundwater levels, what an inverse problem can and
cannot recover (INFILTRIMI-GO). English, equations as native Word math (OMML), references checked in Crossref,
numbers filled from infiltrimi_results.json.

usage: python build_infiltrimi_doc.py RESULTS.json FIGDIR OUT.docx"""
import json
import os
import re
import sys
import tempfile

import numpy as np
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'spiranca_go', 'certain_coast'))
sys.path.insert(1, os.path.join(HERE, '..', 'ml_paradigms', 'word'))
from build_sota import run, para, heading, table  # noqa: E402
from build_methodology import Eqs, mrich, display_eq  # noqa: E402
from build_annex import field_run, two_columns  # noqa: E402
import omml  # noqa: E402

SIZE = 10
GREY = '52606D'

REFERENCES = [
    'Berghuijs, W. R., Collenteur, R. A., Jasechko, S., Jaramillo, F., Luijendijk, E., Moeck, C., van der Velde, Y. & '
    'Allen, S. T. (2024). Groundwater recharge is sensitive to changing long-term aridity. Nature Climate Change '
    '14(4): 357–363. https://doi.org/10.1038/s41558-024-01953-z',
    'Boumis, G., Kumar, M., Nimmo, J. R. & Clement, T. P. (2022). Influence of shallow groundwater evapotranspiration '
    'on recharge estimation using the water table fluctuation method. Water Resources Research 58(10): '
    'e2022WR032073. https://doi.org/10.1029/2022WR032073',
    'Collenteur, R. A., Bakker, M., Klammler, G. & Birk, S. (2021). Estimation of groundwater recharge from '
    'groundwater levels using nonlinear transfer function noise models and comparison to lysimeter data. Hydrology '
    'and Earth System Sciences 25(5): 2931–2949. https://doi.org/10.5194/hess-25-2931-2021',
    'Crosbie, R. S., Doble, R. C., Turnadge, C. & Taylor, A. R. (2019). Constraining the magnitude and uncertainty of '
    'specific yield for use in the water table fluctuation method of estimating recharge. Water Resources Research '
    '55(8): 7343–7361. https://doi.org/10.1029/2019WR025285',
    'Entekhabi, D., Njoku, E. G., O\'Neill, P. E., Kellogg, K. H., Crow, W. T., Edelstein, W. N., Entin, J. K., '
    'Goodman, S. D., Jackson, T. J., Johnson, J., Kimball, J., Piepmeier, J. R., Koster, R. D., Martin, N., et al. '
    '(2010). The Soil Moisture Active Passive (SMAP) mission. Proceedings of the IEEE 98(5): 704–716. '
    'https://doi.org/10.1109/JPROC.2010.2043918 (classical)',
    'Healy, R. W. & Cook, P. G. (2002). Using groundwater levels to estimate recharge. Hydrogeology Journal 10(1): '
    '91–109. https://doi.org/10.1007/s10040-001-0178-0 (classical)',
    'Moeck, C., Grech-Cumbo, N., Podgorski, J., Bretzler, A., Gurdak, J. J., Berg, M. & Schirmer, M. (2020). A '
    'global-scale dataset of direct natural groundwater recharge rates: a review of variables, processes and '
    'relationships. Science of the Total Environment 717: 137042. https://doi.org/10.1016/j.scitotenv.2020.137042',
    'Raue, A., Kreutz, C., Maiwald, T., Bachmann, J., Schilling, M., Klingmüller, U. & Timmer, J. (2009). Structural '
    'and practical identifiability analysis of partially observed dynamical models by exploiting the profile '
    'likelihood. Bioinformatics 25(15): 1923–1929. https://doi.org/10.1093/bioinformatics/btp358 (classical)',
    'Scanlon, B. R., Healy, R. W. & Cook, P. G. (2002). Choosing appropriate techniques for quantifying groundwater '
    'recharge. Hydrogeology Journal 10(1): 18–39. https://doi.org/10.1007/s10040-001-0176-2 (classical)',
    'ter Braak, C. J. F. (2006). A Markov chain Monte Carlo version of the genetic algorithm Differential Evolution: '
    'easy Bayesian computing for real parameter spaces. Statistics and Computing 16(3): 239–249. '
    'https://doi.org/10.1007/s11222-006-8769-1 (classical)',
]


def half_distance(period, D=5000.0, L=5000.0):
    """Distance from the sea at which half of the recharge-driven head fluctuation of the given period is seen."""
    w = 2 * np.pi / period

    def vis(x):
        kap = np.sqrt(1j * w / D)
        r = np.exp(-kap * x) * (1 + np.exp(-2 * kap * (L - x))) / (1 + np.exp(-2 * kap * L))
        return abs(1 - r)
    lo, hi = 0.01, L
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if vis(mid) < 0.5 else (lo, mid)
    return 0.5 * (lo + hi)


def fmt(q, v):
    if q in ('rain_mm_yr', 'recharge_mm_yr', 'theta_fc'):
        return f'{v:.0f}'
    if q in ('Sy',):
        return f'{v:.3f}'
    if q in ('Ic',):
        return f'{v:.1f}'
    return f'{v:.3f}'


def cell(s, q):
    return f'{fmt(q, s["median"])} [{fmt(q, s["q05"])}–{fmt(q, s["q95"])}]'


def blocks(r):
    su = r['setup']; tr = su['truth']; tq = r['truth']; w = r['wtf']; j = r['jacobian']
    sc = r['scenarios']; names = list(sc.keys())
    S0 = sc[names[0]]['summary']; S1 = sc[names[1]]['summary']; S4 = sc[names[-1]]['summary']
    ns = r['no_storms']['summary']
    hd = {p: half_distance(p) for p in (1, 30, 365)}
    rh = max(v['diag']['rhat_max'] for v in sc.values())
    rh = max(rh, r['no_storms']['diag']['rhat_max'])
    blind = 100 * su['days_below_field_capacity']
    w0 = np.array(sc[names[0]]['bands']['wet']); t0 = np.array(sc[names[0]]['bands']['theta'])
    t2 = np.array(sc[names[2]]['bands']['theta'])
    wet_hw = float(np.median(w0[2] - w0[0]) / 2)
    th_w = float(np.median(t0[2] - t0[0])); th_w2 = float(np.median(t2[2] - t2[0]))
    B = []
    a = B.append

    a(('status', 'Status. This working document answers one question: when we do not know exactly how much rain falls, '
                 'how much of it infiltrates and how wet the soil is, can these be recovered from groundwater levels by '
                 'an inverse problem, and what else is needed? Propositions 1–4 are proved here; Proposition 1 restates '
                 'the water-table fluctuation method (Healy and Cook, 2002) in stochastic form, and Proposition 2 is a '
                 'structural non-identifiability in the sense of Raue et al. (2009). All numbers come from a synthetic '
                 'three-year daily record built to resemble a Mediterranean coastal plain; no observed data are used.'))
    a(('h', 'Summary'))
    a(('p', '**The question.** Rain reaches the water table through a chain: the gauge reads the rain with an unknown '
            'error, part of the rain runs off, the soil stores what infiltrates, the plants take part of it back, and '
            'only what drains below the roots becomes recharge and raises the groundwater head. Every link is '
            'uncertain, and every link affects the heads. Which of these quantities can the heads tell us?'))
    a(('p', '**The answer, in six points.**'))
    a(('ul', [f'**Recharge: yes, with its timing, but in units of specific yield.** Each recharge pulse raises the head '
              f'by recharge divided by specific yield $S_{{y}}$. From a daily logger with 1 cm noise, daily recharge is '
              f'recovered within {w["daily_rmse_mm"]:.1f} mm and monthly recharge within {w["monthly_rmse_mm"]:.1f} mm, '
              f'because the errors cancel over a window, once $S_{{y}}$ is known (Proposition 1).',
              f'**Near the sea, slow recharge is hidden.** With the illustrative diffusivity of the companion documents, '
              f'a well sees half of the seasonal recharge signal at {hd[365]:.0f} m from the sea, half of the monthly '
              f'signal at {hd[30]:.0f} m and half of single storms at {hd[1]:.0f} m (Proposition 1).',
              '**Amounts in millimetres: not from the heads and the gauge alone.** Multiplying the true rain, the '
              'evapotranspiration, the infiltration capacity, the soil storage and the specific yield by the same '
              'factor leaves every head unchanged (Proposition 2). In the synthetic test the true annual rain is then '
              f'only known to lie between {S0["rain_mm_yr"]["q05"]:.0f} and {S0["rain_mm_yr"]["q95"]:.0f} mm '
              f'(truth {tq["rain_mm_yr"]:.0f} mm).',
              f'**Fractions: yes.** The share of the rain that becomes recharge, evapotranspiration or runoff does not '
              f'change under that symmetry and is recovered from the heads and the gauge alone: recharge/rain '
              f'{S0["R_over_P"]["median"]:.3f} [{S0["R_over_P"]["q05"]:.3f}–{S0["R_over_P"]["q95"]:.3f}], truth '
              f'{tq["R_over_P"]:.3f}.',
              f'**One anchor is enough for the amounts.** A pumping test (specific yield), a soil-moisture probe or a '
              f'chloride mass balance each removes the ambiguity; with all three the true rain is '
              f'{S4["rain_mm_yr"]["median"]:.0f} [{S4["rain_mm_yr"]["q05"]:.0f}–{S4["rain_mm_yr"]["q95"]:.0f}] mm and '
              f'the recharge {S4["recharge_mm_yr"]["median"]:.0f} [{S4["recharge_mm_yr"]["q05"]:.0f}–'
              f'{S4["recharge_mm_yr"]["q95"]:.0f}] mm per year (truth {tq["recharge_mm_yr"]:.0f}).',
              f'**Soil moisture and infiltration capacity have blind spots.** The heads see the soil only when it '
              f'drains: on the {blind:.0f} % of days below field capacity they carry no information on it, and the '
              f'deficit is revealed only at the first recharge of the wet season (Proposition 3); looking back from '
              f'that onset, the relative wetness is recovered within ±{wet_hw:.3f} of field capacity. The infiltration '
              f'capacity is seen only through storms that exceed it; without such storms the data give only a lower '
              f'bound (Proposition 4).']))

    a(('h', '1. The chain from rain to the water table'))
    a(('p', 'We use the simplest model that contains every link of the question, run on a daily step for one well '
            '(Table 1). The gauge rain $P_{g}$ is corrected by an unknown factor $m$ (undercatch, distance from the '
            'gauge); rain above the infiltration capacity $I_{c}$ runs off; the root zone stores the water θ; '
            'evapotranspiration takes $k_{et}$ times the potential rate, reduced when the soil is drier than field '
            'capacity $\\theta_{fc}$; water above field capacity drains to the water table with time constant '
            '$\\tau_{s}$; and the head responds to that recharge through the specific yield $S_{y}$ and drains towards a '
            'base level $h_{b}$ with time constant $\\tau_{a}$:'))
    a(('eq', 'chain', r'\begin{aligned}&P=m\,P_{g},\qquad I=\min(P,I_{c}),\qquad R=\frac{(\theta-\theta_{fc})^{+}}{\tau_{s}},\\'
                      r'&\frac{d\theta}{dt}=I-k_{et}\,\mathrm{PET}\,\min\!\left(1,\frac{\theta}{\theta_{fc}}\right)-R,\qquad '
                      r'S_{y}\frac{dh}{dt}=R-S_{y}\frac{h-h_{b}}{\tau_{a}}.\end{aligned}'))
    a(('p', 'The data are the daily gauge rain, the daily potential evapotranspiration (PET) of a weather station, and '
            'the daily head of a logger with noise $\\sigma_{h}$ = 1 cm. The unknowns are $m$, $k_{et}$, $I_{c}$, '
            '$\\theta_{fc}$, $\\tau_{s}$, the initial wetness $\\varphi_{0}=\\theta(0)/\\theta_{fc}$, $S_{y}$, $\\tau_{a}$, '
            '$h_{b}$ and $h(0)$. The model is a lumped form of the nonlinear transfer models used to estimate recharge '
            'from heads (Collenteur et al., 2021).'))
    t1 = [['m', 'True rain / gauge rain', '–', f'{tr["m"]:g}'],
          ['Ic', 'Infiltration capacity; rain above it runs off', 'mm/day', f'{tr["Ic"]:g}'],
          ['k_et', 'Evapotranspiration / potential evapotranspiration', '–', f'{tr["k_et"]:g}'],
          ['θfc', 'Root-zone storage at field capacity', 'mm', f'{tr["theta_fc"]:g}'],
          ['τs', 'Drainage time of the root zone', 'days', f'{tr["tau_s"]:g}'],
          ['Sy', 'Specific yield', '–', f'{tr["Sy"]:g}'],
          ['τa', 'Drainage time of the aquifer at the well', 'days', f'{tr["tau_a"]:g}'],
          ['Rain', 'True rain (gauge reads 1/m of it)', 'mm/year', f'{tq["rain_mm_yr"]:.0f} ({su["gauge_mm_yr"]:.0f})'],
          ['R/P, ET/P, Q/P', 'Recharge, evapotranspiration and runoff as shares of the rain', '–',
           f'{tq["R_over_P"]:.2f}, {tq["ET_over_P"]:.2f}, {tq["runoff_over_P"]:.2f}']]
    a(('cap', 'Table 1. Quantities of the chain and their values in the synthetic record.'))
    a(('table', ['Symbol', 'Meaning', 'Unit', 'Synthetic truth'], t1, [2.4, 9.0, 2.2, 3.4], 8.8))

    a(('h', '2. What the heads can and cannot tell: four propositions'))
    a(('pi', '**Proposition 1 (recharge leaves a mark, in units of specific yield).** Let the head be sampled daily with '
             'independent noise of standard deviation $\\sigma_{h}$, and let $S_{y}$, $\\tau_{a}$ and $h_{b}$ be known. '
             'The recharge depth of each step, estimated as $\\widehat{R}_{k}\\Delta t=S_{y}[(h_{k}-h_{k-1})+(h_{k-1}-h_{b})'
             '\\Delta t/\\tau_{a}]$, has error standard deviation $\\sigma_{h}S_{y}\\sqrt{1+(1-\\Delta t/\\tau_{a})^{2}}\\approx\\sqrt{2}\\,'
             '\\sigma_{h}S_{y}$ per step, and the error of its sum over any window stays of the same size, because the '
             'head differences telescope. Without $S_{y}$, only $R/S_{y}$ is recovered. In a coastal strip with the sea '
             'at $x=0$ and no flow at $x=L$, a recharge component of angular frequency ω produces a head fluctuation '
             'reduced by the factor'))
    a(('eq', 'vis', r'V(\omega,x)=\left|1-\frac{\cosh\kappa(L-x)}{\cosh\kappa L}\right|,\qquad\kappa=\sqrt{i\omega/D},'
                    r'\quad D=T/S_{y}.'))
    a(('pi', '**Proof.** The daily step of the model is $h_{k}-h_{k-1}=R_{k}\\Delta t/S_{y}-(h_{k-1}-h_{b})\\Delta t/'
             '\\tau_{a}$; solving for $R_{k}$ with noisy heads leaves the error '
             '$S_{y}[(\\varepsilon_{k}-\\varepsilon_{k-1})+\\varepsilon_{k-1}\\Delta t/\\tau_{a}]/\\Delta t$, whose '
             'variance is the stated one. Over a window the differences $\\varepsilon_{k}-\\varepsilon_{k-1}$ sum to '
             'the difference of the two end errors, and only the small terms $\\varepsilon_{k-1}\\Delta t/\\tau_{a}$ '
             'accumulate. For the strip, the Fourier transform in time of $S_{y}\\partial_{t}h=T\\partial_{x}^{2}h+r$ '
             'with $h(0)=0$ and $\\partial_{x}h(L)=0$ is $\\widehat{h}=\\widehat{r}\\,(1-\\cosh\\kappa(L-x)/\\cosh\\kappa '
             'L)/(i\\omega S_{y})$; the factor in brackets is (2). ∎'))
    a(('p', f'Reading. The heads are a good recharge meter, as the water-table fluctuation method assumes (Healy and '
            f'Cook, 2002), but the meter is calibrated in units of $S_{{y}}$, whose uncertainty passes directly into '
            f'the recharge (Crosbie et al., 2019). Factor (2) tells where to place the wells: single storms are seen '
            f'almost everywhere, but half of the seasonal recharge is lost at {hd[365]:.0f} m from the sea (Figure 2a).'))

    a(('pi', '**Proposition 2 (the scale symmetry of the chain).** For every $c>0$ and every gauge record, the '
             'parameters $(m,k_{et},I_{c},\\theta_{fc},S_{y})$ and $(cm,ck_{et},cI_{c},c\\theta_{fc},cS_{y})$, with '
             '$\\tau_{s}$, $\\varphi_{0}$, $\\tau_{a}$, $h_{b}$ and $h(0)$ unchanged, give the same heads:'))
    a(('eq', 'sym', r'h\left(t;\,c\,m,\,c\,k_{et},\,c\,I_{c},\,c\,\theta_{fc},\,c\,S_{y}\right)=h\left(t;\,m,\,k_{et},'
                    r'\,I_{c},\,\theta_{fc},\,S_{y}\right)\quad\text{for all }t.'))
    a(('pi', 'Hence (i) from the heads and the gauge these five quantities are known only up to a common factor, and the '
             'Fisher information is singular along the direction $(1,1,1,1,1)$ of their logarithms; (ii) every ratio '
             'that the symmetry leaves unchanged is free of this ambiguity: recharge/rain, evapotranspiration/rain, '
             'runoff/rain and the relative wetness $\\theta/\\theta_{fc}$; (iii) one measurement that fixes any of the '
             'five, or any amount in millimetres such as the long-term recharge, removes the ambiguity.'))
    a(('pi', '**Proof.** Suppose $\\theta$ is multiplied by $c$ on day $t$. Then $P=cmP_{g}$, '
             '$\\min(cP,cI_{c})=c\\min(P,I_{c})$, $ck_{et}\\mathrm{PET}\\min(1,c\\theta/(c\\theta_{fc}))$ and '
             '$(c\\theta-c\\theta_{fc})^{+}/\\tau_{s}$ are all multiplied by $c$, so $\\theta$ is multiplied by $c$ on '
             'day $t+1$ and the recharge $R$ on every day; the initial state $\\varphi_{0}\\theta_{fc}$ starts the '
             'induction. The head changes by $R/S_{y}$, which is unchanged. (i) The derivative of the heads along the '
             'orbit is zero, so the sensitivity matrix $J$ satisfies $Jv=0$ for the tangent $v$, and $v$ is in the null '
             'space of the Fisher matrix $J^{\\top}\\Sigma^{-1}J$. (ii) The ratios are homogeneous of degree zero. '
             '(iii) A measurement of any of these quantities has a nonzero derivative along $v$ and adds information '
             'in that direction. ∎'))
    a(('p', f'Reading. This is a structural non-identifiability: no amount of head data removes it. In the synthetic '
            f'record the Jacobian of the heads has nine singular values between {j["singular_values"][-2]:.0f} and '
            f'{j["singular_values"][0]:.0f} and one of {j["singular_values"][-1]:.1e}, and the null direction coincides '
            f'with the symmetry (cosine {j["cos_with_scale_dir"]:.4f}). With one anchor the smallest singular value '
            f'becomes {j["smallest_sv_with_pumping_test"]:.1f} (pumping test, $S_{{y}}$ within 10 %), '
            f'{j["smallest_sv_with_soil_probe"]:.1f} (soil probe, 6 mm) or {j["smallest_sv_with_chloride_balance"]:.1f} '
            f'(chloride balance, 20 %) (Figure 2b).'))

    a(('pi', '**Proposition 3 (soil moisture is seen only when the soil drains).** While $\\theta<\\theta_{fc}$ the '
             'recharge is zero and the head does not depend on $\\theta$: two soil states below field capacity give the '
             'same heads until the first recharge. If the soil holds $\\theta_{0}<\\theta_{fc}$ at the end of the dry '
             'season, the first recharge occurs at the first $t^{*}$ with'))
    a(('eq', 'def', r'\int_{t_{0}}^{t^{*}}\left(I-E\right)dt=\theta_{fc}-\theta_{0},'))
    a(('pi', 'so the onset of recharge seen in the heads measures the soil deficit in millimetres of rain, once $m$ is '
             'known, or as a fraction of $\\theta_{fc}$ otherwise.'))
    a(('pi', '**Proof.** $R=(\\theta-\\theta_{fc})^{+}/\\tau_{s}=0$ for $\\theta\\le\\theta_{fc}$, so the head equation '
             'does not contain θ; integrating the soil equation with $R=0$ until θ reaches $\\theta_{fc}$ gives (4). ∎'))
    a(('p', f'Reading. In the synthetic record the soil is below field capacity on {blind:.0f} % of the days (shaded in '
            f'Figure 1b). On those days the heads carry no information on the soil; the first autumn recharge reveals '
            f'how much the summer evapotranspiration has removed, which calibrates $k_{{et}}$ again each year. A smoother '
            f'that also uses the later heads therefore recovers the relative wetness of the dry season (Figure 4b); a '
            f'real-time filter cannot, until the onset.'))

    a(('pi', '**Proposition 4 (infiltration capacity needs storms).** The heads depend on $I_{c}$ only through days with '
             'true rain above $I_{c}$. If no day of the record exceeds $P_{\\max}$, every $I_{c}\\ge P_{\\max}$ gives '
             'the same heads, and the data give at most the lower bound $I_{c}\\ge P_{\\max}$:'))
    a(('eq', 'ic', r'\frac{\partial h(t)}{\partial I_{c}}=0\quad\text{for all }t\quad\text{if}\quad P(s)\le I_{c}\ '
                   r'\text{for all }s\le t.'))
    a(('pi', '**Proof.** $\\min(P,I_{c})=P$ for all days when $I_{c}\\ge\\max P$, so the chain does not contain $I_{c}$. ∎'))
    a(('p', f'Reading. The synthetic record has {su["storm_days_above_Ic"]} storm days above $I_{{c}}$ in three years. '
            f'With them, and with a pumping test and a soil probe, $I_{{c}}$ = {S4["Ic"]["median"]:.1f} '
            f'[{S4["Ic"]["q05"]:.1f}–{S4["Ic"]["q95"]:.1f}] mm/day (truth {tr["Ic"]:g}). In the same climate with every '
            f'storm cut below $I_{{c}}$, the posterior is {ns["Ic"]["median"]:.0f} [{ns["Ic"]["q05"]:.0f}–'
            f'{ns["Ic"]["q95"]:.0f}] mm/day: a lower bound and nothing more (Figure 4b).'))

    a(('h', '3. Which data remove which ambiguity'))
    a(('cap', 'Table 2. Data sources, what each one fixes, and the caveat at a coastal plain such as Fushë Kuqe–Mat.'))
    a(('table', ['Data', 'What it measures', 'What it fixes', 'Caveat on a coastal plain'], [
        ['Daily head loggers (1 cm)', 'Recharge pulses and their timing, in units of Sy', 'Fractions; τs, τa; onset of '
         'recharge', 'Shallow water table: evaporation from it biases the method (Boumis et al., 2022); log the '
         'pumping; place wells beyond the distance of (2)'],
        ['Rain gauge on the plain', 'Timing and relative size of the rain', 'Nothing absolute unless its catch is '
         'calibrated (m = 1)', 'Storm totals vary over short distances; gauges catch less rain in wind'],
        ['Pumping test', 'Specific yield Sy', 'The scale symmetry', 'Sy is itself uncertain; Crosbie et al. (2019) '
         'constrain its magnitude and uncertainty for this method'],
        ['Soil-moisture probe (0–1 m)', 'Soil water in mm, also when the soil is dry', 'The scale symmetry; the blind '
         'spots of Proposition 3', 'Point measurement; satellite soil moisture (Entekhabi et al., 2010) is near-surface '
         'and kilometres wide'],
        ['Chloride mass balance', 'Long-term recharge = rain × Cl(rain) / Cl(groundwater)', 'The scale symmetry',
         'Assumes that all chloride comes from rain (Scanlon et al., 2002); invalid where groundwater chloride comes from '
         'the sea, so use only inland, fresh wells'],
        ['Lysimeter', 'Drainage below the roots, in mm', 'The scale symmetry and the soil model', 'Costly; '
         'Collenteur et al. (2021) compared head-based recharge with lysimeter data'],
    ], [3.0, 4.2, 3.6, 6.2], 8.4))
    a(('p', 'Recharge varies widely with climate and land surface (Moeck et al., 2020) and shifts with long-term aridity '
            '(Berghuijs et al., 2024), so the shares of the rain should be measured at the site rather than assumed. '
            'Proposition 2 says what is needed: the heads and the gauge give the shares; one of the anchors in '
            'Table 2 gives the millimetres.'))

    a(('h', '4. Synthetic test (INFILTRIMI-GO)'))
    a(('p', f'Three years of daily rain were generated for a plain with wet winters and dry summers (true rain '
            f'{tq["rain_mm_yr"]:.0f} mm/year, potential evapotranspiration about 1040 mm/year); the gauge reads '
            f'{su["gauge_mm_yr"]:.0f} mm/year. The chain (1) with the values of Table 1 gives the true soil water, '
            f'recharge and head (Figure 1). Five data sets were inverted: S0, heads and gauge only; S1, plus a pumping '
            f'test ($S_{{y}}$ within 10 %); S2, plus a daily soil-moisture probe (6 mm); S3, plus a chloride mass '
            f'balance (mean recharge within 20 %); S4, all of them. For each, the most probable parameters were found '
            f'by bounded least squares from eight starts, and the posterior was sampled by differential-evolution '
            f'Markov chain Monte Carlo (ter Braak, 2006) with 64 chains, uniform priors on the logarithms of the '
            f'positive parameters and a move along the symmetry of Proposition 2; the largest Gelman–Rubin statistic '
            f'is {rh:.3f}.'))
    qs = [('rain_mm_yr', 'True rain (mm/year)'), ('recharge_mm_yr', 'Recharge (mm/year)'),
          ('R_over_P', 'Recharge / rain'), ('ET_over_P', 'Evapotranspiration / rain'),
          ('runoff_over_P', 'Runoff / rain'), ('Sy', 'Specific yield'), ('theta_fc', 'Field capacity (mm)'),
          ('Ic', 'Infiltration capacity (mm/day)')]
    rows = []
    for q, lab in qs:
        rows.append([lab, fmt(q, tq[q] if q in tq else tr[q])] + [cell(sc[n]['summary'][q], q) for n in names])
    a(('cap', 'Table 3. Posterior median and 90 % interval for each data set (S0 heads and gauge; S1 + pumping test; '
              'S2 + soil probe; S3 + chloride balance; S4 all).'))
    a(('table', ['Quantity', 'Truth', 'S0', 'S1', 'S2', 'S3', 'S4'], rows, [3.4, 1.4, 2.5, 2.5, 2.4, 2.4, 2.4], 7.6))
    a(('p', f'Reading. With the heads and the gauge alone (S0) the amounts are lost along the symmetry: the true rain '
            f'spans {S0["rain_mm_yr"]["q05"]:.0f}–{S0["rain_mm_yr"]["q95"]:.0f} mm and $S_{{y}}$ '
            f'{S0["Sy"]["q05"]:.2f}–{S0["Sy"]["q95"]:.2f}, limited only by the prior ranges, while the shares are found '
            f'(recharge/rain within ±{50 * S0["R_over_P"]["rel_width"]:.1f} %). Any one anchor (S1–S3) brings the '
            f'amounts back, each with the precision of its own measurement: the pumping test (10 %) and the chloride '
            f'balance (20 %) leave intervals of about ±{50 * S1["rain_mm_yr"]["rel_width"]:.0f} % and '
            f'±{50 * sc[names[3]]["summary"]["rain_mm_yr"]["rel_width"]:.0f} % on the rain, while the soil probe, which '
            f'measures millimetres every day, gives the tightest intervals of all. Figure 3 shows the ridge and how each anchor cuts it. For soil moisture the heads alone give '
            f'the shape, the relative wetness θ/θfc within a band about {2 * wet_hw:.2f} wide, but not the size: the band '
            f'of the soil water in millimetres is about {th_w:.0f} mm wide, and a probe narrows it to about '
            f'{th_w2:.0f} mm (Figure 4).'))
    a(('fig', 'infiltrimi_fig1.png', 'Figure 1. The synthetic chain. (a) True rain and the infiltration capacity. (b) Soil '
                                     'water; shaded: days below field capacity, when the heads carry no information on '
                                     'the soil (Proposition 3). (c) True recharge and its estimate from the heads with '
                                     'Sy known (Proposition 1). (d) Head at the well, true and logged.'))
    a(('fig', 'infiltrimi_fig2.png', 'Figure 2. (a) Head response to recharge at a well, relative to the response far '
                                     'inland, against its distance from the sea, for three periods (factor (2); '
                                     'D = 5000 m²/day, L = 5 km); it slightly exceeds 1 where the boundary echo returns '
                                     'in phase. (b) Singular '
                                     'values of the Jacobian of the heads: one is zero, the scale symmetry of '
                                     'Proposition 2; any one anchor lifts it.'))
    a(('fig', 'infiltrimi_fig3.png', 'Figure 3. (a) Posterior samples of the rain multiplier m and the specific yield Sy '
                                     'from the heads and the gauge alone (grey): a ridge; coloured: the 90 % segment of '
                                     'the ridge that each anchor picks. (b) 90 % '
                                     'intervals divided by the truth: amounts (rain, recharge, field capacity) need an '
                                     'anchor; shares of the rain do not.'))
    a(('fig', 'infiltrimi_fig4.png', 'Figure 4. (a) Soil water in millimetres: 90 % band from the heads and the gauge '
                                     '(grey) and the median with a soil probe (blue; its band is thinner than the line). '
                                     '(b) Relative wetness θ/θfc from the heads and the gauge alone. (c) Infiltration '
                                     'capacity: 90 % interval with storms above it and without (Proposition 4).'))

    a(('h', '5. How to do it at Fushë Kuqe–Mat'))
    a(('ul', ['**Step 1. Heads.** Daily loggers (1 cm) in three to five wells at different distances from the sea and '
              f'the rivers, at least two of them beyond about {hd[365]:.0f} m, where the seasonal recharge is seen '
              '(Proposition 1); log the pumping.',
              '**Step 2. Rain, evaporation and soil.** One rain gauge and one soil-moisture profile station on the '
              'plain, and the potential evapotranspiration of the nearest weather station (Propositions 2 and 3).',
              '**Step 3. One anchor per unit.** A pumping test in each hydrogeological unit for $S_{y}$; a chloride '
              'mass balance only in inland, fresh wells (Table 2).',
              '**Step 4. Inversion.** The chain (1) for each well, as here: least squares for the most probable '
              'parameters, then Markov chain Monte Carlo. Report the shares of the rain first, which are always '
              'identified, then the amounts with their anchors, and the soil water as a band.',
              '**Step 5. Every year.** Use the first autumn recharge to update the summer evapotranspiration '
              '(Proposition 3), and report the infiltration capacity as a lower bound until a storm exceeds it '
              '(Proposition 4).',
              '**Step 6. Link to the warning model.** Recharge is the class-P boundary of "Boundary conditions as '
              'operators": the cap on infiltration is applied to the rain record, and the aquifer response is linear.']))

    a(('h', '6. Innovation'))
    a(('p', 'The building blocks are known: the water-table fluctuation method, the bucket model of the root zone and '
            'structural identifiability. What this document adds, to our knowledge (to be verified against the '
            'literature before submission):'))
    a(('ul', ['**The scale symmetry of the rain–soil–aquifer chain (Proposition 2)** as an exact group action, with its '
              'consequence: the shares of the rain are always identifiable from the heads and the gauge, and the '
              'amounts need exactly one anchor. The choice of field measurements becomes a rank-one decision: any one '
              'of a pumping test, a soil probe, a chloride balance or a lysimeter is enough, and a second one only '
              'narrows the intervals.',
              '**A stochastic water-table fluctuation rule with telescoping errors, and a coastal visibility factor '
              '(Proposition 1)**, which says how precisely recharge is recovered and where to place wells to see it.',
              '**Blind spots of soil moisture and the deficit revealed at onset (Proposition 3)**, which turns the first '
              'autumn recharge into a yearly calibration of summer evapotranspiration.',
              '**The storm-exceedance condition for infiltration capacity (Proposition 4).**',
              '**A data-worth table for the site from one synthetic inversion (Table 3)**, ready to be repeated with the '
              'real wells.']))

    a(('h', '7. Limitations'))
    a(('ul', ['The model is lumped at one well: one root zone, one aquifer reservoir, no lateral flow, no preferential '
              'flow and no evaporation from a shallow water table, which matters on a low coastal plain (Boumis et '
              'al., 2022).',
              'The gauge error is a constant factor; in reality it varies from storm to storm, which widens every '
              'interval. Parameters are constant in time; land use and irrigation are ignored.',
              'Noise is Gaussian and the record is synthetic; with real data the model error, not the logger noise, '
              'will dominate.',
              'Factor (2) uses the illustrative diffusivity of the companion documents (5000 m²/day) and a strip; the '
              'distances must be recomputed with the calibrated aquifer.']))
    a(('refs',))
    a(('note', 'Five of the ten references are from 2019 or later. The five earlier ones are used directly: Healy and Cook '
               '(2002) and Scanlon, Healy and Cook (2002) for the methods, Raue et al. (2009) for structural '
               'identifiability, ter Braak (2006) for the sampler, and Entekhabi et al. (2010) for satellite soil '
               'moisture. Companion documents, not counted: "A deterministic-first treatment of boundary and initial '
               'conditions in groundwater models" and "Boundary conditions as operators" (10 November 2026). Code: '
               'infiltrimi_exp.py (numpy, scipy; about 8 minutes) reproduces every number, infiltrimi_figs.py draws the '
               'figures and build_infiltrimi_doc.py builds this document (folder experiments/infiltrimi_go).'))
    return B


def footer(section):
    p = section.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Rain, infiltration and soil moisture from groundwater levels · working document · page ', size=8,
        color='6B7785')
    field_run(p, 'PAGE', 8)
    run(p, ' of ', size=8, color='6B7785')
    field_run(p, 'NUMPAGES', 8)


def main(res, figdir, out):
    r = json.load(open(res))
    BL = blocks(r)
    numbers, n = {}, 0
    for b in BL:
        if b[0] == 'eq':
            n += 1; numbers[b[1]] = str(n)
    E = Eqs()
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0); s.top_margin = Cm(1.7); s.bottom_margin = Cm(1.6)
    s.footer_distance = Cm(0.8)
    st = doc.styles['Normal']; st.font.name = 'Arial'; st.font.size = Pt(SIZE)
    footer(s)
    p = para(doc, 0); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'POLYTECHNIC UNIVERSITY OF TIRANA', bold=True, size=10, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Faculty of Geology and Mining — Department of Energy Resources', size=9, color=GREY)
    p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'Rain, infiltration and soil moisture from groundwater levels', bold=True, size=16, color='1F3864')
    p = para(doc, 4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'What an inverse problem can and cannot recover, which data remove each ambiguity, and how to do it at a '
           'coastal plain: propositions with proofs and a synthetic Bayesian inversion (INFILTRIMI-GO)', bold=True,
        size=10.5, color='1F3864')
    p = para(doc, 8); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'D. Zeqiraj, Faculty of Geology and Mining, Polytechnic University of Tirana · Working document · '
           '10 November 2026', italic=True, size=8.8, color=GREY)

    for bi, b in enumerate(BL):
        kind = b[0]
        nxt = BL[bi + 1][0] if bi + 1 < len(BL) else None
        if kind == 'h':
            heading(doc, b[1], 12, before=8)
        elif kind == 'status':
            p = para(doc, 6); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, b[1], italic=True, size=9, color=GREY)
        elif kind in ('p', 'pi'):
            p = para(doc, 3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            if kind == 'pi':
                p.paragraph_format.left_indent = Cm(0.6)
            text = re.sub(r'\((\w+)\)\[eq\]', lambda m: f'({numbers[m.group(1)]})', b[1])
            mrich(p, text, E, size=SIZE)
            if nxt == 'eq':
                p.paragraph_format.keep_with_next = True
        elif kind == 'ul':
            for item in b[1]:
                p = para(doc, 2); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.left_indent = Cm(0.6); p.paragraph_format.first_line_indent = Cm(-0.35)
                run(p, '•  ', size=SIZE)
                mrich(p, item, E, size=SIZE)
            para(doc, 1)
        elif kind == 'eq':
            display_eq(doc, E, b[2], numbers[b[1]])
        elif kind == 'cap':
            p = para(doc, 3, before=3); p.paragraph_format.keep_with_next = True
            run(p, b[1], italic=True, size=8.8, color=GREY)
        elif kind == 'table':
            t = table(doc, b[1], b[2], b[3], size=b[4])
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            for i, row in enumerate(t.rows):
                row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
                if i < len(t.rows) - 1:
                    for c_ in row.cells:
                        for cp in c_.paragraphs:
                            cp.paragraph_format.keep_with_next = True
            para(doc, 3)
        elif kind == 'fig':
            p = para(doc, 2, before=4); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(os.path.join(figdir, b[1]), width=Cm(16.8))
            p = para(doc, 6)
            run(p, b[2], italic=True, size=8.8, color=GREY)
        elif kind == 'refs':
            heading(doc, 'References', 11, before=6)
            sec = doc.add_section(WD_SECTION.CONTINUOUS)
            two_columns(sec)
            for r_ in REFERENCES:
                p = para(doc, 1.5); p.paragraph_format.left_indent = Cm(0.35)
                p.paragraph_format.first_line_indent = Cm(-0.35)
                run(p, r_, size=7.6, color='3D4752')
            sec = doc.add_section(WD_SECTION.CONTINUOUS)
            cols = sec._sectPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cols')
            if cols is not None:
                cols.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}num', '1')
        elif kind == 'note':
            p = para(doc, 3, before=3); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, b[1], italic=True, size=8.2, color=GREY)

    work = tempfile.mkdtemp()
    draft = os.path.join(work, 'draft.docx'); doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh, ensure_ascii=False)
    omml.main(draft, eq_json, out)
    words = sum(len(re.sub(r'\$[^$]*\$', 'x', b[1] if isinstance(b[1], str) else ' '.join(b[1])).split())
                for b in BL if b[0] in ('p', 'pi', 'ul'))
    print('saved', out, '|', n, 'numbered equations,', len(E.items) - n, 'inline |', words, 'words |',
          len(REFERENCES), 'references')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
