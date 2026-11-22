r"""Text of the TRONDITJA-GO implementation report (English). blocks(R, C) returns the block list; every number comes
from res/tronditja.json (R) and res/okada_checks.json (C). Conventions: $inline math$, **bold**, *italic*,
[text](url) hyperlink, [[key]] equation number, {{key}} figure or table number, <<key>> a value from the results."""
import math

NOTE = 'TERMETET note'

REFS = [
    dict(key='1', text='Okada, Y. (1985). Surface deformation due to shear and tensile faults in a half-space. Bulletin '
                       'of the Seismological Society of America 75(4), 1135–1154.',
         url='https://doi.org/10.1785/BSSA0750041135'),
    dict(key='2', text='Okada, Y. (1992). Internal deformation due to shear and tensile faults in a half-space. Bulletin '
                       'of the Seismological Society of America 82(2), 1018–1040.',
         url='https://doi.org/10.1785/bssa0820021018'),
    dict(key='3', text='Hanks, T. C., & Kanamori, H. (1979). A moment magnitude scale. Journal of Geophysical Research: '
                       'Solid Earth 84(B5), 2348–2350.', url='https://doi.org/10.1029/JB084iB05p02348'),
    dict(key='4', text='Ganas, A., et al. (2020). Ground deformation and seismic fault model of the M6.4 Durres '
                       '(Albania) Nov. 26, 2019 earthquake, based on GNSS/InSAR observations. Geosciences 10, 210.',
         url='https://doi.org/10.3390/geosciences10060210'),
    dict(key='5', text='Govorčin, M., et al. (2020). Geodetic source modeling of the 2019 Mw 6.3 Durrës, Albania, '
                       'earthquake: partial rupture of a blind reverse fault. Geophysical Research Letters 47, '
                       'e2020GL088990.', url='https://doi.org/10.1029/2020GL088990'),
    dict(key='6', text='Matraku, K., et al. (2023). The 26 November 2019 Durrës earthquake, Albania: coseismic '
                       'displacements and occurrence of slow slip events in the year following the earthquake. '
                       'Geophysical Journal International 234, 807–838.', url='https://doi.org/10.1093/gji/ggad101'),
    dict(key='7', text='van der Heiden, V., et al. (2026). Analysis of the 2019 Mw 6.4 Durrës, Albania, aftershock '
                       'sequence: basement involved thrusting at the eastern Adriatic plate margin. Geophysical Journal '
                       'International 246, ggag155.', url='https://doi.org/10.1093/gji/ggag155'),
    dict(key='8', text='Mavroulis, S., Lekkas, E., & Carydis, P. (2021). Liquefaction phenomena induced by the 26 '
                       'November 2019, Mw = 6.4 Durrës (Albania) earthquake and liquefaction susceptibility assessment '
                       'in the affected area. Geosciences 11, 215.', url='https://doi.org/10.3390/geosciences11050215'),
    dict(key='9', text='Boulanger, R. W., & Idriss, I. M. (2014). CPT and SPT based liquefaction triggering procedures. '
                       'Report UCD/CGM-14/01, Center for Geotechnical Modeling, University of California, Davis.',
         url=None),
    dict(key='10', text='Boulanger, R. W., & Idriss, I. M. (2016). CPT-based liquefaction triggering procedure. Journal '
                        'of Geotechnical and Geoenvironmental Engineering 142, 04015065.',
         url='https://doi.org/10.1061/(asce)gt.1943-5606.0001388'),
    dict(key='11', text='Maurer, B. W., et al. (2014). Evaluation of the liquefaction potential index for assessing '
                        'liquefaction hazard in Christchurch, New Zealand. Journal of Geotechnical and Geoenvironmental '
                        'Engineering 140, 04014032.', url='https://doi.org/10.1061/(asce)gt.1943-5606.0001117'),
    dict(key='12', text='Rice, J. R., & Cleary, M. P. (1976). Some basic stress diffusion solutions for fluid-saturated '
                        'elastic porous media with compressible constituents. Reviews of Geophysics 14, 227–241.',
         url='https://doi.org/10.1029/rg014i002p00227'),
    dict(key='13', text='Wang, C.-Y., & Manga, M. (2021). Water and Earthquakes. Springer International Publishing.',
         url='https://doi.org/10.1007/978-3-030-64308-9'),
    dict(key='14', text='Wang, C.-Y., & Chia, Y. (2008). Mechanism of water level changes during earthquakes: near field '
                        'versus intermediate field. Geophysical Research Letters 35(12).',
         url='https://doi.org/10.1029/2008GL034227'),
    dict(key='15', text='DeLong, E. R., DeLong, D. M., & Clarke-Pearson, D. L. (1988). Comparing the areas under two or '
                        'more correlated receiver operating characteristic curves: a nonparametric approach. '
                        'Biometrics 44(3), 837–845.', url='https://doi.org/10.2307/2531595'),
    dict(key='16', text='Werner, A. D., et al. (2013). Seawater intrusion processes, investigation and management: '
                        'recent advances and future challenges. Advances in Water Resources 51, 3–26.',
         url='https://doi.org/10.1016/j.advwatres.2012.03.004'),
    dict(key='17', text='Grant, A. R. R., et al. (2021). Changes in liquefaction severity in the San Francisco Bay Area '
                        'with sea-level rise. Geo-Extreme 2021, 308–317.', url='https://doi.org/10.1061/9780784483695.030'),
    dict(key='18', text='Befus, K. M., et al. (2020). Increasing threat of coastal groundwater hazards from sea-level '
                        'rise in California. Nature Climate Change 10, 946–952.',
         url='https://doi.org/10.1038/s41558-020-0874-1'),
    dict(key='19', text='Zhang, G., Robertson, P. K., & Brachman, R. W. I. (2002). Estimating liquefaction-induced ground '
                        'settlements from CPT for level ground. Canadian Geotechnical Journal 39(5), 1168–1180.',
         url='https://doi.org/10.1139/t02-047'),
    dict(key='20', text='Hughes, J. D., Leake, S. A., Galloway, D. L., & White, J. T. (2022). Documentation for the '
                        'Skeletal Storage, Compaction, and Subsidence (CSUB) Package of MODFLOW 6. U.S. Geological '
                        'Survey Techniques and Methods 6-A62.', url='https://doi.org/10.3133/tm6A62'),
    dict(key='D1', text='Zeqiraj, D. (2026). Tërmeti, akuiferi, veprimet njerëzore dhe përmbytjet: sistemi i ekuacioneve '
                        'të çiftuara për bregdetin Durrës–Fushë Kuqe (the TERMETET note). Working note, 31 October '
                        '2026; revised version docs/research_notes/TERMETET_CERTAIN-COAST_Termeti_Akuiferi_Permbytjet_'
                        'Sistemi_i_Ekuacioneve_rishikuar.docx in this repository.', url=None),
    dict(key='D2', text='CERTAIN-COAST (2026). Certified early warning to protect water, port and energy infrastructure on '
                        'a sinking Adriatic coast. Technical annex of the NATO SPS application (draft), '
                        'docs/certain_coast/CERTAIN-COAST_Technical_Annex.docx in this repository.', url=None),
]


def all_refs():
    return REFS


def pc(x, d=0):
    return f'{100 * x:.{d}f}%'


def sci(x, d=1):
    e = int(math.floor(math.log10(abs(x))))
    m = x / 10 ** e
    sup = str(e).replace('-', '⁻').translate(str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹'))
    return f'{m:.{d}f}×10{sup}'


def cm(x):
    return f'{100 * x:.0f} cm'


def values(R, C):
    E1, E2, E3, E4 = R['E1'], R['E2'], R['E3'], R['E4']
    V = {}
    V['msf'] = f"{E1['msf_at_7p5']:.3f}"
    V['ks'] = f"{E1['ksigma_at_pa']:.3f}"
    V['rd0'] = f"{E1['rd_surface']:.3f}"
    V['crr100'] = f"{E1['crr_q100']:.3f}"
    V['e49'] = sci(E1['eq49_max_rel_err'])
    V['edl'] = sci(E1['dlnfs_max_rel_err'])
    for zw in ('0.8', '1.6', '2.6'):
        V['lpi' + zw.replace('.', '')] = f"{E1['example'][zw]['lpi']:.1f}"
    sl = E1['lpi_slope_per_m']
    V['sl_r'], V['sl_w'], V['sl_u'] = f"{abs(sl['right']):.1f}", f"{abs(sl['renormalised']):.1f}", pc(sl['understated'])
    # Okada checks
    c1 = C['C1_jump_equals_slip']
    V['c1'] = sci(max(v['max_abs_err'] for v in c1.values()))
    V['c2'] = sci(max(C['C2_point_source_rel_err'].values()))
    V['c3_long'] = pc(C['C3_plane_strain']['long_fault_max_change_nu_025_to_040'], 1)
    V['c3_short'] = pc(C['C3_plane_strain']['short_fault_max_change_nu_025_to_040'], 1)
    c4 = C['C4_sense']
    V['c4_rev'], V['c4_nor'] = f"{c4['reverse_uz_over_hanging_wall']:+.3f}", f"{c4['normal_uz_over_hanging_wall']:+.3f}"
    V['c4_lle'], V['c4_llw'] = f"{c4['left_lateral_un_east_side']:+.3f}", f"{c4['left_lateral_un_west_side']:+.3f}"
    V['c5'] = sci(max(C['C5_strain_step_rel_change'].values()))
    # E2
    for s in E2['sources']:
        k = s['key']
        V[f'{k}_mw'] = f"{s['mw']:.2f}"; V[f'{k}_slip'] = f"{s['slip_m']:.2f}"
        V[f'{k}_L'] = f"{s['L_km']:.0f}"; V[f'{k}_W'] = f"{s['W_km']:.1f}".rstrip('0').rstrip('.')
        V[f'{k}_cmin'] = f"{s['dh_conf_min_m']:.2f}"; V[f'{k}_cmax'] = f"+{s['dh_conf_max_m']:.2f}"
        V[f'{k}_smin'] = cm(s['dh_soft_min_m']); V[f'{k}_smax'] = '+' + cm(s['dh_soft_max_m'])
        V[f'{k}_nmin'] = f"{s['dh_note_min_m']:.1f}"; V[f'{k}_nmax'] = f"+{s['dh_note_max_m']:.1f}"
        V[f'{k}_eamax'] = f"{s['ea_max'] * 1e6:.1f}"; V[f'{k}_eamin'] = f"{s['ea_min'] * 1e6:.1f}"
    cmins = [s['dh_conf_min_m'] for s in E2['sources']]; cmaxs = [s['dh_conf_max_m'] for s in E2['sources']]
    smins = [s['dh_soft_min_m'] for s in E2['sources']]; smaxs = [s['dh_soft_max_m'] for s in E2['sources']]
    V['c_lo'], V['c_hi'] = f'{-max(cmins):.1f}', f'{-min(cmins):.1f}'
    V['c_up_lo'], V['c_up_hi'] = f'{min(cmaxs):.1f}', f'{max(cmaxs):.1f}'
    V['s_lo'], V['s_hi'] = f'{-100 * max(smins):.0f}', f'{-100 * min(smins):.0f}'
    V['s_up_lo'], V['s_up_hi'] = f'{100 * min(smaxs):.0f}', f'{100 * max(smaxs):.0f}'
    kp = E2['kappa_kPa']
    V['k_soft'] = f"{kp['soft'] / 1e3:.0f} MPa"; V['k_conf'] = f"{kp['confined'] / 1e6:.2f} GPa"
    V['k_band'] = f"{kp['confined_band'][0] / 1e6:.2f}–{kp['confined_band'][1] / 1e6:.2f} GPa"
    V['k_note'] = f"{kp['note'] / 1e6:.2f} GPa"
    pm = E2['dh_per_areal_microstrain_m']
    V['pm_soft'] = f"{1000 * pm['soft']:.0f} mm"; V['pm_conf'] = f"{1000 * pm['confined']:.0f} mm"
    V['pm_note'] = f"{1000 * pm['note']:.0f} mm"
    V['r_soft'] = f"{E2['note_over_soft']:.0f}"; V['r_conf'] = f"{E2['note_over_confined']:.1f}"
    V['agree'] = pc(E2['sign_agreement_where_any_ea_gt_big'])
    V['ea_big'] = f"{E2['ea_big'] * 1e6:.2f}"
    sh = E2['share_left_after_15s']
    for L in ('0.5', '1', '2', '3', '5', '8', '12'):
        V['sh' + L.replace('.', '')] = pc(sh[f'{L} m'])
    nt = E2['natural_test']
    V['tau_hat'] = f"{nt['tau_hat_d']:.2f}"
    V['ci_q'] = f"{nt['ci95_quake_d'][0]:.2f}–{nt['ci95_quake_d'][1]:.2f}"
    V['ci_s'] = f"{nt['ci95_season_d'][0]:.2f}–{nt['ci95_season_d'][1]:.2f}"
    V['ci_r'] = f"{nt['width_ratio']:.1f}"
    lay = E2['layers']
    V['G_soft'] = f"{lay['soft']['G'] / 1e3:.0f} MPa"; V['G_conf'] = f"{lay['confined']['G'] / 1e6:.1f} GPa"
    # E3
    V['n_pool'] = str(E3['n_pool']); V['liq_share'] = pc(E3['liquefied_share'])
    for k, a in E3['auc_full_pool'].items():
        V['auc_' + k] = f'{a:.3f}'
    pw = E3['power']; N = E3['n_sites']
    keys = {'season (M1 vs M0)': 'ps', 'step, ensemble source (M2 vs M1)': 'pe', 'step, true source (M3 vs M1)': 'pt'}
    for key, short in keys.items():
        for n, v in zip(N, pw[key]):
            V[f'{short}{n}'] = pc(v)
    V['ub_med'] = f"{E3['lpi_change_from_step']['median_abs']:.2f}"
    V['ub_p90'] = f"{E3['lpi_change_from_step']['p90_abs']:.1f}"
    V['so_med'] = f"{E3['lpi_change_soft']['median_abs']:.2f}"
    V['so_p90'] = f"{E3['lpi_change_soft']['p90_abs']:.2f}"
    V['so_max'] = f"{E3['lpi_change_soft']['max_abs']:.2f}"
    V['dp_lo'] = f"{E3['dp_true_kPa']['min']:.0f}"; V['dp_hi'] = f"+{E3['dp_true_kPa']['max']:.1f}"
    V['dps_lo'] = f"{E3['dp_soft_kPa']['min']:.2f}"; V['dps_hi'] = f"+{E3['dp_soft_kPa']['max']:.2f}"
    # E4
    V['zs'] = f"{E4['z_s']:.1f}"; V['mint'] = f"{E4['m_int']:.1f}"; V['aseas'] = f"{E4['a_seas']:.1f}"
    for r in E4['window_table']:
        a = f"{r['amax']:.2f}".replace('.', '')
        V[f'zc{a}'] = f"{r['zstar_cert']:.2f}"; V[f'zm{a}'] = f"{r['zstar_median']:.2f}"
        V[f'ec{a}'] = f"{r['eta_close']:.2f}"
        V[f'yr{a}'] = (f"about {2026 + r['eta_close'] / 0.009:.0f}" if r['eta_close'] > 0 else 'closed already')
    b = E4['bulletin']
    V['p_min'], V['p_max'] = f"{b['pexc_min']:.2f}", f"{b['pexc_max']:.2f}"
    V['p_ratio'] = f"{b['pexc_max'] / b['pexc_min']:.1f}"
    V['zwd_lo'], V['zwd_hi'] = f"{b['zw_range'][0]:.1f}", f"{b['zw_range'][1]:.1f}"
    V['nport'] = str(b['n_port']); V['ndraw'] = str(b['n_draw']); V['nsamp'] = str(b['n_port'] * b['n_draw'])
    V['rt'] = f"{R['runtime_s']:.0f}"
    return V


def fill(x, V):
    if isinstance(x, str):
        for k, v in V.items():
            x = x.replace('<<' + k + '>>', v)
        assert '<<' not in x, x[x.index('<<'):x.index('<<') + 40]
        return x
    if isinstance(x, (list, tuple)):
        return type(x)(fill(y, V) for y in x)
    return x


def blocks(R, C):
    V = values(R, C)
    BL = []

    def A(b):
        BL.append(fill(b, V))

    A(('title', 'TRONDITJA-GO: the earthquake, the aquifer and liquefaction, implemented'))
    A(('subtitle', 'The first three steps of the TERMETET note as tested code: the liquefaction module with the pore '
                   'pressure of the day, the coseismic step from four published models of the 26 November 2019 Durrës '
                   'earthquake, and the design of the 2019 hindcast; with a joint safe window for liquefaction and '
                   'seawater intrusion and a daily bulletin'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · implementation report with numerical checks · follows the working '
                 'note of 31 October 2026 on the earthquake, the aquifer, human action and floods [D1]'))

    # ------------------------------------------------------------------------------------------ 1
    A(('h', '1. Outcome'))
    A(('bbox', [
        r'**What was built.** Three modules in experiments/tronditja_go: the liquefaction triggering of Boulanger and '
        r'Idriss [9, 10] with the liquefaction potential index (LPI) [11], driven by the pore pressure at the moment '
        r'of the earthquake; Okada’s solution for a rectangular fault [1], written here and checked against five '
        r'independent tests; and the three experiments E1–E3 of the plan, with the innovation E4. Everything runs in '
        r'about <<rt>> s. Figure {{chain}} shows the chain.',
        r'**Liquefaction module (E1).** All structural checks pass ($MSF$ = <<msf>> at $M$ 7.5, $K_\sigma$ = <<ks>> at '
        r'$\sigma_v^{\prime} = P_a$). Equation (4.9) of [D1] holds to <<e49>>. A new closed form for the full sensitivity, '
        r'$\partial \ln FS / \partial z_w = (\gamma_w/\sigma_v^{\prime})(1 - C_\sigma/K_\sigma)$, holds to <<edl>>. In the '
        r'example profile the LPI falls from <<lpi08>> to <<lpi26>> when the water table drops from 0.8 to 2.6 m, '
        r'about <<sl_r>> per metre. Re-normalising the CPT resistance with the stress of the day, a tempting shortcut, '
        r'understates that slope by <<sl_u>>.',
        r'**The coseismic step (E2): a correction of magnitude.** The four published source models [4–7] agree on '
        r'the sign of the step over <<agree>> of the area where the strain matters. Its size, however, depends on '
        r'the layer. A layer under the free surface takes the horizontal strain of the crust and adjusts vertically, '
        r'so its pore pressure follows its own shear modulus: $\Delta p_0 = -\kappa\, \Delta\varepsilon_a$, '
        r'$\kappa = \tfrac{2}{3} G B (1+\nu_u)/(1-\nu_u)$. In a confined aquifer ($G$ = <<G_conf>>) the head falls by '
        r'<<c_lo>>–<<c_hi>> m over the hanging wall and rises by <<c_up_lo>>–<<c_up_hi>> m in front of it. In the soft '
        r'surface sand ($G$ = <<G_soft>>) it falls by <<s_lo>>–<<s_hi>> cm and rises by <<s_up_lo>>–<<s_up_hi>> cm. '
        r'Equation (2.2) of [D1], applied to the volumetric strain of the half-space, gives <<r_soft>> times the '
        r'soft-sand value.',
        r'**Consequence.** For liquefaction of the surface sands the static step is negligible next to the seasonal '
        r'swing of the water table (about 1 m). It matters for the confined aquifer and its wells. Rises of metres '
        r'in liquefied areas, such as those of Chi-Chi cited in [D1], cannot come from the static strain of a soft '
        r'layer. They point to the volumetric change caused by the shaking itself (Wang and Chia [14] use laboratory '
        r'data on saturated sediments under cyclic loading), which the CSR–CRR comparison already represents.',
        r'**The earthquake as a free pumping test (E2).** A <<ci_q>>-day 95% interval for the leakage time of the '
        r'confined aquifer follows from 20 days of logger data after a 0.3 m step. A whole year of seasonal heads '
        r'gives <<ci_s>> days, an interval <<ci_r>> times wider.',
        r'**The 2019 hindcast (E3).** On a synthetic coastal plain, even with the largest step (the upper bound of '
        r'(2.2) as written), 480 sites with CPT give a power of <<pt480>> to detect the step and <<ps480>> to detect '
        r'the water table of the day. The 2019 liquefaction map [8] cannot test the chain; the well records of '
        r'November 2019 can.',
    ]))
    A(('box', [
        r'**Innovation: TRONDITJA-GO** (*tronditja*: the jolt). Three results are new. (i) **Which aquifer feels the '
        r'earthquake.** The static step of a layer under the free surface follows its own shear modulus, $\kappa = '
        r'\tfrac{2}{3} G B (1+\nu_u)/(1-\nu_u)$: centimetres in soft surface sand, up to a metre in a confined '
        r'aquifer, and <<r_soft>> times less in the soft sand than (2.2) as written. The step therefore leaves the '
        r'liquefaction of the surface sands and stays in the confined aquifer and its wells. (ii) **The earthquake as a '
        r'free pumping test.** The relaxation of that step identifies the leakage time <<ci_r>> times more sharply than a '
        r'year of seasonal heads. (iii) **A design result.** The 2019 liquefaction map cannot test the step, and tests '
        r'the water table of the day only with several hundred CPTs.',
        r'The certified safe window and the liquefaction state "if the design earthquake struck now" are concepts of the '
        r'CERTAIN-COAST proposal [D2]: its multi-hazard window and its indicator $I_2$. TRONDITJA-GO computes them with '
        r'the liquefaction module. For one managed head the window between liquefaction and intrusion closes at '
        r'$\eta_{close}(a) = z_s - z^*(a) - m_{int} - A$: at the synthetic port of E4, at <<ec020>> m of relative '
        r'sea-level rise for 0.20 g (<<yr020>> at an illustrative 9 mm/yr), and it is already closed at 0.22 g. The '
        r'probability that the LPI exceeds 5 if the earthquake struck that day moves between <<p_min>> (late July) and '
        r'<<p_max>> (early February), a factor of <<p_ratio>> that a static hazard map hides.',
        r'The building blocks are published [1, 9–11, 13, 16]; sea-level rise and liquefaction have been studied '
        r'together [17, 18]. In the sources read for this note we did not find the step coefficient of a layer under '
        r'the free surface used to decide which aquifer feels an earthquake, nor the coseismic step used as a pumping '
        r'test of the leakage time.',
    ]))
    A(('img', 'chain', 17.0))
    A(('cap', r'Figure {{chain}}. TRONDITJA-GO in six steps, each with its computed field: (1) the four source models '
              r'(thick line: top edge of the fault); (2) the mean head step in the confined aquifer; (3) the share of '
              r'the step left after 15 s of shaking; (4) LPI against the depth of the water table; (5) the joint safe '
              r'window against sea-level rise and design acceleration; (6) the daily bulletin.'))

    # ------------------------------------------------------------------------------------------ 2
    A(('h', '2. What was implemented'))
    A(('p', r'The note [D1] proposed three first steps: the liquefaction module, the coseismic step from the published '
            r'source models, and a hindcast of the 2019 liquefaction. Table {{files}} lists what each step became. '
            r'The parameters of the coastal plain, the soils and the ground motion are illustrative and the '
            r'coordinates are local (km from the fault centroid); this is a test of the method, not a map of Durrës.'))
    A(('cap', r'Table {{files}}. The modules, what they compute and how they were checked.'))
    A(('table', ['Step of [D1]', 'Module', 'What it computes', 'Checked by'], [
        ['1. Liquefaction', 'liq.py', r'$\sigma_v$, $u$, $\sigma_v^{\prime}$, CSR, CRR, FS, LPI, $\partial \ln FS/\partial z_w$',
         r'structural values; finite differences of (4.9) and of the closed form'],
        ['2. Coseismic step', 'okada85.py, liq.py', r'surface displacement and strain [1]; $\Delta p_0 = '
         r'-\kappa\, \Delta\varepsilon_a$; drainage share $f$', 'okada_checks.py (five tests); Biot’s law (1.1)'],
        ['3. Hindcast design', 'tronditja_exp.py, E3', 'AUC of four predictors; power against the number of sites',
         r'DeLong covariance [15]; 400 resamples per size'],
        ['Innovation', 'tronditja_exp.py, E4', 'joint window, closing sea level, daily bulletin',
         'quantiles over 60 profiles and 12 accelerations'],
    ], [3.0, 3.1, 6.1, 4.8], 9.5))

    # ------------------------------------------------------------------------------------------ 3
    A(('h', '3. E1: the liquefaction module'))
    A(('h2', '3.1 The pore pressure of the day'))
    A(('p', r'The module follows (4.2)–(4.8) of [D1] (Boulanger and Idriss [9], eqs. 2.2, 2.7, 2.14, 2.16, 2.19, '
            r'2.20 and 2.24). One change is needed. In (4.1) the coseismic step was added to the water table. A step '
            r'of pore pressure in a sand below a clay is not a movement of the water table: the water table is where '
            r'$u = 0$, and it does not move in the seconds of shaking. The step enters the pore pressure:'))
    A(('eq', 'u', r'u(z) = \gamma_w \left(z - z_w\right)_+ + f(z)\, \Delta p_0(z), \qquad \sigma_v^{\prime}(z) = \sigma_v(z) - '
                  r'u(z), \qquad \sigma_v(z) = \int_0^z \gamma_t\, dz^{\prime}'))
    A(('p', r'where $z_w$ is the depth of the water table on the day, $\Delta p_0$ the undrained step (Section 4) and '
            r'$f$ the share of it left at the end of the shaking (Section 4.5). Then, with $q = q_{c1Ncs}$,'))
    A(('eq', 'fs', r'\mathrm{FS} = \frac{\mathrm{CRR}_{7.5,1}(q)\; \mathrm{MSF}(q, M)\; K_\sigma(q, \sigma_v^{\prime})}'
                   r'{0.65\, (\sigma_v/\sigma_v^{\prime})\, (a_{\max}/g)\, r_d(z, M)}, \qquad \mathrm{LPI} = '
                   r'\int_0^{20\,\mathrm{m}} \max(0, 1 - \mathrm{FS})\, (10 - 0.5 z)\, dz'))
    A(('p', r'with the functions of (4.3)–(4.7) of [D1]. $FS$ is set to infinity above the water table and in soils '
            r'that cannot liquefy (clays and silts with $I_c$ above 2.6).'))
    A(('h2', '3.2 What the CPT resistance is, and the shortcut to avoid'))
    A(('p', r'$q_{c1Ncs}$ is a density index: the tip resistance normalised with the effective stress at the time of '
            r'the CPT. It describes the sand and does not change when the water table moves later. The water table of '
            r'the day enters only through CSR and $K_\sigma$. Re-normalising $q_{c1Ncs}$ with the stress of the day '
            r'(through $C_N = (P_a/\sigma_v^{\prime})^m \le 1.7$) mixes the state of the sand with the state of the water. '
            r'For the example profile, with the CPT made at a water table of 2.0 m, the shortcut gives an LPI slope '
            r'of <<sl_w>> per metre instead of <<sl_r>>: it understates the effect of the water table by <<sl_u>> '
            r'(Figure {{e1}}e, dashed).'))
    A(('h2', '3.3 The sensitivity to the water table in closed form'))
    A(('prop', 'Proposition 1 (sensitivity of the factor of safety).', [
        r'Below the water table, with the same unit weight above and below it, $q_{c1Ncs}$ fixed and $\Delta p_0 = 0$,',
        ('eq', 'dlnfs', r'\frac{\partial \ln \mathrm{FS}}{\partial z_w} = \frac{\gamma_w}{\sigma_v^{\prime}} \left(1 - '
                        r'\frac{C_\sigma}{K_\sigma}\right) \;\; \text{if } K_\sigma < 1.1; \qquad '
                        r'\frac{\partial \ln \mathrm{FS}}{\partial z_w} = \frac{\gamma_w}{\sigma_v^{\prime}} \;\; '
                        r'\text{if } K_\sigma = 1.1'),
        r'The first factor is (4.9) of [D1] with the opposite sign; the second is the share that $K_\sigma$ takes back. '
        r'Because $C_\sigma \le 0.3$ and $K_\sigma$ is near 1, a deeper water table always raises $FS$.',
    ]))
    A(('proof', r'$CRR_{7.5,1}$ and $MSF$ depend on $q$ and $M$ only, and $r_d$ on $z$ and $M$. Below the water table '
                r'$\partial \sigma_v^{\prime} / \partial z_w = \gamma_w$ and $\sigma_v$ does not change. Hence $\partial \ln CSR '
                r'/ \partial z_w = -\gamma_w / \sigma_v^{\prime}$, which is (4.9). From (4.7), $\partial K_\sigma / \partial z_w '
                r'= -C_\sigma \gamma_w / \sigma_v^{\prime}$ below the cap and zero on it. Subtracting the logarithmic '
                r'derivative of CSR from that of $K_\sigma$ gives [[dlnfs]].'))
    A(('p', r'Table {{t1}} lists the structural checks. Both derivatives agree with central finite differences to about '
            r'$10^{-10}$, the rounding level of the differences.'))
    A(('cap', r'Table {{t1}}. Checks of the liquefaction module.'))
    A(('table', ['Check', 'Expected', 'Computed'], [
        [r'$MSF$ at $M$ = 7.5', '1 (definition)', '<<msf>>'],
        [r'$K_\sigma$ at $\sigma_v^{\prime} = P_a$', '1 (definition)', '<<ks>>'],
        [r'$r_d$ at the surface, $M$ = 6.4', 'close to 1', '<<rd0>>'],
        [r'$CRR_{7.5,1}$ at $q_{c1Ncs}$ = 100', 'from (4.5)', '<<crr100>>'],
        ['(4.9) against finite differences', 'relative error ≈ 0', '<<e49>>'],
        ['[[dlnfs]] against finite differences', 'relative error ≈ 0', '<<edl>>'],
    ], [7.0, 4.5, 5.5], 9.5))
    A(('h2', '3.4 An example profile'))
    A(('p', r'A coastal profile of a 1.2 m crust over three sands (median $q_{c1Ncs}$ of 82, 104 and 132, with '
            r'CPT-like scatter) separated by silty clays was shaken by $M$ 6.4 at 0.25 g with the water table at 0.8, '
            r'1.6 and 2.6 m. The LPI is <<lpi08>>, <<lpi16>> and <<lpi26>> (Figure {{e1}}). The upper sand carries most '
            r'of the LPI, because there the stress is low and the weight $10 - 0.5z$ is high; this is why the LPI is so '
            r'sensitive to the water table when the liquefiable layers are shallow, as Maurer et al. [11] observed.'))
    A(('img', 'e1', 17.0))
    A(('cap', r'Figure {{e1}}. E1. (a) The profile: crust and silty clays hatched, sands shaded, $q_{c1Ncs}$ as a line. '
              r'(b) CSR for three water tables and CRR of the sands. (c) Factor of safety; shaded where FS < 1. '
              r'(d) The LPI integrand and the LPI for each water table. (e) LPI against the depth of the water table '
              r'for three accelerations; dashed: the shortcut of Section 3.2. Shading: high (5–15) and very high '
              r'(over 15) LPI.'))

    # ------------------------------------------------------------------------------------------ 4
    A(('h', '4. E2: the coseismic step'))
    A(('h2', '4.1 Okada’s solution, written and checked'))
    A(('p', r'The surface displacement of a rectangular dislocation in an elastic half-space [1] was written in numpy '
            r'(okada85.py), and the horizontal strains were taken by fourth-order central differences. The note '
            r'cites Okada [2], the internal-deformation form; the surface form [1] is the one needed for a shallow '
            r'layer (Section 4.3). Five tests that do not use the code itself (okada_checks.py) all pass (Table '
            r'{{t2}}).'))
    A(('cap', r'Table {{t2}}. Independent checks of okada85.py.'))
    A(('table', ['Test', 'What must hold', 'Result'], [
        ['C1. Fault reaching the surface', 'jump of displacement across the trace = slip vector (strike-slip, '
         'and reverse at 45°)', 'error ≤ <<c1>> m per m of slip'],
        ['C2. Point-source limit', 'a 200 m fault far away = the point-source formulas of [1] × area',
         'relative error ≤ <<c2>>'],
        ['C3. Plane strain', r'a 2000 km fault: surface displacement independent of $\nu$',
         r'<<c3_long>> change for $\nu$ 0.25 → 0.40 (20 km fault: <<c3_short>>)'],
        ['C4. Sense of motion', 'reverse lifts the hanging wall, normal lowers it; left-lateral moves the far side left',
         r'$u_z$ = <<c4_rev>> and <<c4_nor>> m; $u_n$ = <<c4_lle>> (east), <<c4_llw>> (west) m'],
        ['C5. Strain step', 'strain independent of the difference step (1, 2, 4 m)', 'relative change ≤ <<c5>>'],
    ], [3.6, 7.6, 5.8], 9.5))
    A(('h2', '4.2 Four published source models'))
    A(('p', r'The geometry of each model was taken from its abstract; what an abstract did not give was derived from the '
            r'moment magnitude with uniform slip, $M_0 = \mu L W s$, $M_w = (\log_{10} M_0 - 9.1)/1.5$ [3], '
            r'$\mu$ = 30 GPa (Table {{t3}}). The strike follows the NW–SE trend of the structure, set by the dip '
            r'direction. All four are reverse faults (rake 90°).'))
    A(('cap', r'Table {{t3}}. The source ensemble. Bold: from the abstract of the paper; the rest derived here.'))
    A(('table', ['Model', 'Dip', 'Centroid depth', 'L × W (km)', 'Slip (m)', 'Mw here'], [
        ['Ganas et al. 2020 [4]', '**23° E**', '**16.5 km**', '**22 × 13**', '**0.55**', '<<ganas_mw>>'],
        ['Matraku et al. 2023 [6]', '**40° E**', '**15 km**', '20 × 11', '<<matraku_slip>> (uniform)',
         '**<<matraku_mw>>**'],
        ['Govorčin et al. 2020 [5]', '**71° SW**', '17 km (**slip at 11–23 km**)', '18 × <<govorcin_W>>',
         '<<govorcin_slip>> (uniform)', '**<<govorcin_mw>>**'],
        ['van der Heiden et al. 2026 [7]', '**about 30° NE**', '15 km (**12–18 km**)', '20 × <<vdheiden_W>>',
         '<<vdheiden_slip>> (uniform)', '**<<vdheiden_mw>>**'],
    ], [4.3, 2.4, 3.6, 2.4, 2.6, 1.7], 9.5))
    A(('h2', '4.3 The undrained step in a layer under the free surface'))
    A(('p', r'Equation (2.2) of [D1] gives the step as $\Delta p_0 = -B K_u \Delta\varepsilon_v$, with '
            r'$\Delta\varepsilon_v$ the volumetric strain of the half-space (2.1). That is right for an aquifer as '
            r'stiff as the half-space. The sediments of a coastal plain are much softer and lie in a layer tens to '
            r'hundreds of metres thick, against a deformation field that varies over kilometres. Such a layer takes '
            r'the horizontal strain of the crust beneath it, while its top is free: $\sigma_{zz} = 0$.'))
    A(('prop', 'Proposition 2 (the step under a free surface).', [
        r'For an undrained ($\zeta = 0$) poroelastic layer obeying (1.1)–(1.2) of [D1], with imposed horizontal strains '
        r'and $\sigma_{zz} = 0$,',
        ('eq', 'kappa', r'\Delta p_0 = -\kappa\, \Delta\varepsilon_a, \qquad \Delta\varepsilon_a = \Delta\varepsilon_{xx} + '
                        r'\Delta\varepsilon_{yy}, \qquad \kappa = \frac{2 G B}{3}\, \frac{1 + \nu_u}{1 - \nu_u}'),
        r'with $G$, $B$ and $\nu_u$ of the layer. Equivalently $\Delta p_0 = -B K_u \Delta\varepsilon_v$ with the '
        r'volumetric strain of the layer, $\Delta\varepsilon_v = \Delta\varepsilon_a (1 - 2\nu_u)/(1 - \nu_u)$, not '
        r'that of the half-space. A soft saturated layer ($\nu_u \to 1/2$) deforms at almost constant volume, and '
        r'$\kappa \to 2 G B$: the step scales with the shear modulus of the layer, not with the stiffness of its '
        r'water.',
    ]))
    A(('proof', r'With $\zeta = 0$, (1.2) gives $p = -\alpha M \varepsilon_v$, and (1.1) becomes undrained elasticity '
                r'with $\lambda_u = 2 G \nu_u / (1 - 2\nu_u)$. Then $\sigma_{zz} = 0$ gives $\varepsilon_{zz} = '
                r'-\nu_u \varepsilon_a / (1 - \nu_u)$, so $\varepsilon_v = \varepsilon_a (1 - 2\nu_u)/(1 - \nu_u)$. '
                r'With $\alpha M = B K_u$ and $K_u = 2G(1+\nu_u)/[3(1 - 2\nu_u)]$, $p = -B K_u \varepsilon_v$ is '
                r'[[kappa]]. The identity was checked against (1.1)–(1.2) solved directly for five random materials, '
                r'to $2\times10^{-16}$.'))
    A(('p', r'At the surface of the half-space $\Delta\varepsilon_v = \Delta\varepsilon_a (1 - 2\nu)/(1 - \nu)$, so '
            r'(2.2) as written corresponds to $\kappa_{(2.2)} = B K_u (1 - 2\nu)/(1 - \nu)$ = <<k_note>> for '
            r'$B K_u$ = 5 GPa and $\nu$ = 0.25. Table {{t4}} compares the three coefficients. The confined aquifer and '
            r'the soft sand are placeholders until $G$ is measured (seismic CPT or surface waves) and $B$ is taken '
            r'from the tidal response of the wells, as Section 8 of [D1] proposes.'))
    A(('cap', r'Table {{t4}}. The step coefficient and the step over the four source models. Head per microstrain '
              r'of areal strain; ranges are the extremes of the four maps.'))
    A(('table', ['Layer', 'G, B, νu', 'κ', 'Head per microstrain', 'Fall (hanging wall)',
                 'Rise (in front)'], [
        ['Soft surface sand', r'<<G_soft>>, 0.98, 0.49', '<<k_soft>>', '<<pm_soft>>', '<<s_lo>>–<<s_hi>> cm',
         '<<s_up_lo>>–<<s_up_hi>> cm'],
        ['Confined aquifer', r'<<G_conf>>, 0.90, 0.45', '<<k_conf>>', '<<pm_conf>>', '<<c_lo>>–<<c_hi>> m',
         '<<c_up_lo>>–<<c_up_hi>> m'],
        ['(2.2) as written', r'$B K_u$ = 5 GPa, $\nu$ = 0.25', '<<k_note>>', '<<pm_note>>', '<<r_soft>> × soft sand',
         '<<r_conf>> × confined'],
    ], [3.3, 3.6, 2.0, 2.6, 2.8, 2.7], 9.5))
    A(('h2', '4.4 The pattern and the agreement of the models'))
    A(('p', r'All four models put a fall of the head over the hanging wall, where the uplifted crust is stretched, and '
            r'a rise in front of the buried top edge and behind the fault, where it is squeezed (Figure {{e2}}a–d). '
            r'Where the areal strain of any model exceeds <<ea_big>> microstrain, the four agree on the sign over '
            r'<<agree>> of the area. They disagree in a ring around the fall (Figure {{e2}}e, dotted), whose position '
            r'is set by the dip: the 71° model of Govorčin et al. narrows the fall and moves the rise towards the '
            r'trace. The ensemble therefore carries a real epistemic spread, as [D1] anticipated, but not in the sign '
            r'over the hanging wall.'))
    A(('h2', '4.5 Drainage during the shaking'))
    A(('p', r'A sand connected to the water table through sand drains during the shaking. For one-dimensional '
            r'diffusion from the water table, the share of the step left after a shaking of duration $t_s$ at depth '
            r'$L$ below the water table is'))
    A(('eq', 'f', r'f(L) = \operatorname{erf}\left(\frac{L}{2\sqrt{D\, t_s}}\right) \;\; \text{for sand connected '
                  r'through sand;} \qquad f = 1 \;\; \text{for sand sealed by clay}'))
    A(('p', r'With a diffusivity of 1 m²/s and 15 s of shaking, <<sh05>> of the step is left at 0.5 m, <<sh2>> at 2 m, '
            r'<<sh5>> at 5 m and <<sh12>> at 12 m (Figure {{e2}}g). The shallow sands that dominate the LPI lose most of '
            r'a step in seconds; a sand sealed by clay keeps it.'))
    A(('h2', '4.6 The earthquake as a free pumping test'))
    A(('p', r'After the step, a confined sand below a leaky clay relaxes as $\Delta h(t) = \Delta h_0 e^{-t/\tau}$, '
            r'which is (2.3) of [D1] reduced to one compartment. The leakage time $\tau$ is the quantity that a '
            r'pumping test measures. A 0.3 m step with $\tau$ = 3 days was recorded every 15 minutes with 2 cm noise for '
            r'20 days. The fit gives $\hat\tau$ = <<tau_hat>> days and a 95% bootstrap interval of <<ci_q>> days. The '
            r'same $\tau$ from the phase lag of a whole year of daily heads (amplitude 0.5 m, same noise) has an '
            r'interval of <<ci_s>> days, <<ci_r>> times wider (Figure {{e2}}h). Every well in the confined aquifer that '
            r'logged the night of 26 November 2019 holds such a test.'))
    A(('img', 'e2', 16.0))
    A(('cap', r'Figure {{e2}}. E2. (a–d) Head step in the confined aquifer for the four source models; contours at '
              r'−0.5, −0.25, −0.1, 0.1 and 0.25 m; white dashed: uplift of 2, 5 and 10 cm; thick line: top edge of the '
              r'fault. (e) Mean of the four; dotted where they disagree on the sign; A–A′: the transect. (f) The step '
              r'along A–A′: the four models in the confined aquifer, the band of the mean for $G$ from 0.25 to 1 GPa, '
              r'and the mean in the soft surface sand. (g) Share of the step left after the shaking, '
              r'[[f]]. (h) The relaxation after a 0.3 m step and the 95% intervals of $\tau$ from the earthquake and '
              r'from a year of seasons.'))

    # ------------------------------------------------------------------------------------------ 5
    A(('h', '5. E3: designing the 2019 hindcast'))
    A(('p', r'The third step of [D1] is to ask whether the water table of the day and the step improve the prediction of '
            r'where liquefaction occurred in 2019 [8]. Before collecting data, the test was designed on a synthetic '
            r'coastal plain: <<n_pool>> sites within 8 km of a coast that strikes N160°, over the fault of Ganas et al., '
            r'each with a layered profile whose share of sand follows a smooth susceptibility field, a seasonal '
            r'water table, and a peak acceleration that decays with distance with lognormal scatter. The truth uses '
            r'the water table of 26 November and the largest step, (2.2) as written; <<liq_share>> of the sites '
            r'liquefy. Four predictors were compared by the area under the ROC curve (AUC), with the DeLong '
            r'covariance for paired AUCs [15] and a one-sided test at 5%:'))
    A(('b', r'M0: mean water table; M1: water table of the day; M2: M1 plus the step of the four-model mean; M3: M1 plus '
            r'the step of the true source.'))
    A(('p', r'On all <<n_pool>> sites the AUCs are <<auc_M0>>, <<auc_M1>>, <<auc_M2>> and <<auc_M3>> (Figure {{e3}}b). '
            r'The gains are small because most of the information sits in the soil and the shaking. Table {{t5}} gives '
            r'the power: the chance that a hindcast with $N$ mapped sites detects the gain.'))
    A(('cap', r'Table {{t5}}. Power of the paired-AUC test (400 resamples per size, one-sided, 5%).'))
    A(('table', ['Test', 'N = 30', '60', '120', '240', '480'], [
        ['Water table of the day (M1 vs M0)', '<<ps30>>', '<<ps60>>', '<<ps120>>', '<<ps240>>', '<<ps480>>'],
        ['Step, four-model mean (M2 vs M1)', '<<pe30>>', '<<pe60>>', '<<pe120>>', '<<pe240>>', '<<pe480>>'],
        ['Step, true source (M3 vs M1)', '<<pt30>>', '<<pt60>>', '<<pt120>>', '<<pt240>>', '<<pt480>>'],
    ], [6.2, 2.1, 2.1, 2.1, 2.1, 2.1], 9.5))
    A(('p', r'With the coefficient of soft sand (Section 4.3) the step changes the LPI of a site by a median of '
            r'<<so_med>> and at most <<so_max>>, against a median of <<ub_med>> for the upper bound (Figure {{e3}}d). '
            r'No number of sites would detect it. **Design conclusion:** the liquefaction map of 2019 cannot test '
            r'the coseismic step, and it tests the water table of the day only with several hundred CPTs at mapped '
            r'sites. The step should be tested where it is large, in the confined aquifer, on the well records of '
            r'November 2019 (Section 4.6). A liquefaction hindcast remains useful to calibrate the triggering at the '
            r'site, but with its low power stated in advance.'))
    A(('img', 'e3', 17.0))
    A(('cap', r'Figure {{e3}}. E3. (a) The synthetic plain: sites without and with liquefaction (size: LPI), the coast and '
              r'the fault. (b) ROC curves and AUCs of the four predictors. (c) Power against the number of mapped sites '
              r'(upper-bound step). (d) Change of LPI caused by the step, against the areal strain at the site: (2.2) '
              r'as written (orange) and soft surface sand (blue).'))

    # ------------------------------------------------------------------------------------------ 6
    A(('h', '6. E4: the joint safe window and the daily bulletin, computed'))
    A(('h2', '6.1 Two limits on one head'))
    A(('p', r'Let $h$ be the managed head at a low coastal site above mean sea level, $z_s$ the ground elevation and '
            r'$z^*(a)$ the depth that the water table must keep for the LPI to stay below 5 under the design '
            r'acceleration $a$, certified as the 90% quantile over the profiles of the site. Liquefaction asks for '
            r'$h \le z_s - z^*(a)$. The Ghyben–Herzberg relation (3.7) of [D1] keeps the interface at least 20 m deep '
            r'if $h \ge \eta + m_{int}$ with $m_{int}$ = 20/40 = <<mint>> m, $\eta$ being the relative sea-level rise '
            r'[16]. This is the certified multi-hazard window of the proposal [D2], written for one managed head. The '
            r'window and its width are'))
    A(('eq', 'window', r'\eta + m_{int} \;\le\; h \;\le\; z_s - z^*(a), \qquad W(\eta, a) = z_s - z^*(a) - \eta - m_{int}'))
    A(('p', r'A head that swings by $A$ over the year stays inside all year only if $W \ge A$. The window closes for '
            r'good at'))
    A(('eq', 'close', r'\eta_{close}(a) = z_s - z^*(a) - m_{int} - A'))
    A(('p', r'Both limits move the wrong way with time: sea-level rise and subsidence (3.3)–(3.5) of [D1] raise $\eta$; a '
            r'larger design acceleration deepens $z^*$. Pumping to fight liquefaction lowers $h$ towards intrusion; '
            r'recharge to fight intrusion raises it towards liquefaction.'))
    A(('h2', '6.2 The port of E4'))
    A(('p', r'A synthetic low port: ground at $z_s$ = <<zs>> m, <<nport>> CPT-like profiles with sands from 1–2 m '
            r'depth, $A$ = <<aseas>> m. Table {{t6}} and Figure {{e4}} give the result. The median profile needs no '
            r'lowering up to 0.22 g; the window is set by the weakest tenth of the port.'))
    A(('cap', r'Table {{t6}}. The water table that keeps 90% of the port below LPI 5, and the sea level at which the '
              r'all-year window closes. Years at an illustrative 9 mm/yr of relative sea-level rise (4 mm/yr of sea and '
              r'5 mm/yr of subsidence, not measured values).'))
    A(('table', ['Design acceleration', 'z* certified (90%)', 'z* median', 'η at closing', 'Year'], [
        ['0.15 g', '<<zc015>> m', '<<zm015>> m', '<<ec015>> m', '<<yr015>>'],
        ['0.18 g', '<<zc018>> m', '<<zm018>> m', '<<ec018>> m', '<<yr018>>'],
        ['0.20 g', '<<zc020>> m', '<<zm020>> m', '<<ec020>> m', '<<yr020>>'],
        ['0.22 g', '<<zc022>> m', '<<zm022>> m', '<<ec022>> m', '<<yr022>>'],
        ['0.25 g', '<<zc025>> m', '<<zm025>> m', '<<ec025>> m', '<<yr025>>'],
    ], [3.6, 3.4, 2.8, 2.8, 4.4], 9.5))
    A(('img', 'e4', 17.0))
    A(('cap', r'Figure {{e4}}. E4. (a) Width of the joint window against relative sea-level rise and design '
              r'acceleration; the solid line is where it equals the seasonal swing, the dashed line where it vanishes; '
              r'top axis: years at an illustrative 9 mm/yr. (b) The two limits on the head: liquefaction (blue, '
              r'certified) and intrusion (orange) for three sea levels. (c) The water table needed for LPI ≤ 5 in each '
              r'of the 60 profiles, their median and the certified 90% line.'))
    A(('h2', '6.3 The daily bulletin'))
    A(('p', r'The same profiles give, for each day $d$, the probability that the LPI exceeds 5 if the design '
            r'earthquake ($M$ 6.4, median 0.22 g, lognormal scatter 0.35) struck that day:'))
    A(('eq', 'bulletin', r'P_d = \Pr\left[\mathrm{LPI} > 5 \mid \text{earthquake on day } d\right] = \frac{1}{N_p N_a} '
                         r'\sum_{i=1}^{N_p} \sum_{j=1}^{N_a} \mathbf{1}\left[\mathrm{LPI}_i\left(z_w(d), a_j\right) > 5\right]'))
    A(('p', r'with $N_p$ = <<nport>> profiles and $N_a$ = <<ndraw>> accelerations. With the natural water table '
            r'moving between <<zwd_lo>> and <<zwd_hi>> m, $P_d$ moves between <<p_min>> in late July and <<p_max>> in '
            r'early February (Figure {{e5}}). With the logger network of the project, $z_w(d)$ is measured, and the '
            r'bulletin can be issued daily, with the conformal or certified bounds of the CERTAIN-COAST cycle in '
            r'place of the plain quantiles used here.'))
    A(('img', 'e5', 17.0))
    A(('cap', r'Figure {{e5}}. The daily bulletin for the port in 2027. Top: the water table. Middle: the median and the '
              r'5–95% band of the LPI over profiles and accelerations. Bottom: the probability that the LPI exceeds 5 '
              r'if the earthquake struck that day.'))

    # ------------------------------------------------------------------------------------------ 7
    A(('h', '7. What changes in the note'))
    A(('p', r'The revised Albanian note [D1] carries these changes. Its first page lists them, and each new paragraph '
            r'opens with a short bold title:'))
    A(('b', r'**(4.1)–(4.2).** The step enters the pore pressure, $u = \gamma_w (z - z_w)_+ + f \Delta p_0$ '
            r'[[u]], with the drainage share [[f]]; the water table does not jump.'))
    A(('b', r'**(2.2).** For a layer under the free surface, $\Delta p_0 = -\kappa\, \Delta\varepsilon_a$ [[kappa]]; '
            r'in soft sand the step is centimetres. The mechanism paragraph now separates the static step from the '
            r'volumetric change caused by the shaking (Wang and Chia [14]), which CSR–CRR already contains, so that '
            r'it is not counted twice.'))
    A(('b', r'**(2.4).** The constant: from $e = 3E/(4\pi r^3)$ and $\log_{10} E = 5.24 + 1.44 M$ it is −4.38, not '
            r'−4.62; for $M$ 6.4 the radius of $e$ = 0.1 J/m³ becomes 88 km instead of 73 km. Both are larger than '
            r'the distance from the 2019 source to the Durrës–Fushë Kuqe coast (a few tens of kilometres), so no '
            r'decision there depends on it. Wang and Chia [14] present the relation as new; its printed constant '
            r'must be read there before use.'))
    A(('b', r'**4.5.** $q_{c1Ncs}$ is fixed by the CPT; the full sensitivity is [[dlnfs]]; the shortcut of '
            r'Section 3.2 biases the slope by <<sl_u>>.'))
    A(('b', r'**3.3.** The compaction equations are those of the CSUB package of MODFLOW 6 [20], which replaces SUB-WT.'))
    A(('b', r'**5.6.** Settlement from liquefaction is the integral of the post-shaking volumetric strain over depth, '
            r'with the strain from $FS$ and $q_{c1Ncs}$ as in Zhang et al. [19]; the coefficients are taken from that '
            r'paper, not repeated here.'))

    # ------------------------------------------------------------------------------------------ 8
    A(('h', '8. Limits'))
    A(('p', r'The soils, the coastal plain and the ground motion are synthetic, and the port is not a real port. The '
            r'source models use uniform slip on one rectangle; the published slip distributions are richer. The '
            r'half-space is homogeneous; a layered crust changes the strain near the surface. The layer coefficients '
            r'$G$, $B$ and $\nu_u$ are assumed, not measured; Proposition 2 assumes a layer thin against the '
            r'deformation field and fully undrained during the step. The cyclic generation of pore pressure is left '
            r'inside CSR–CRR, as the triggering procedure intends, and is not modelled as a separate step. Drainage '
            r'during the shaking is one-dimensional. The hindcast design uses one source as the truth and the upper '
            r'bound of the step, so its powers are optimistic. The window uses one intrusion criterion (an interface '
            r'20 m deep) and a 90% quantile over 60 profiles; the year axis rests on an illustrative rate. The '
            r'bulletin uses a fixed scenario earthquake, not a hazard curve. The settlement and the flood steps of '
            r'[D1] were not implemented.'))
    A(('p', r'*Verification note.* The external references [1–20] were checked in Crossref (DOI, authors, title, '
            r'venue), November 2026, except the report [9], which has no DOI. The geometry of the source models comes '
            r'from their abstracts. The note was drafted with the help of an AI assistant. Every number is computed by '
            r'experiments/tronditja_go (tronditja_exp.py, okada_checks.py; results in res/) and inserted by the build '
            r'script.'))
    A(('refs',))
    return BL
