"""Text of the RINDERTIMI-GO note (English). blocks(E, T) returns the block list and the values used in the text.
Text conventions: $inline math$, **bold**, *italic*, ==yellow placeholder==, [[key]] equation number, {{key}} figure or
table number, <<name>> value filled in from res/ (rgo_eval.json, rgo_tune.json, rgo_train_loss.json)."""
import re

import numpy as np

REFS = [
    'Bogachev, V. I. (1998). Gaussian Measures. American Mathematical Society.',
    'Burgers, G., van Leeuwen, P. J., & Evensen, G. (1998). Analysis scheme in the ensemble Kalman filter. Monthly Weather Review 126(6): 1719–1724.',
    'Cenameri, S., & Beqiraj, A. (2016). Assessment of seawater intrusion in Fushë-Kuqe aquifer, Albania. Bulletin of the Geological Society of Greece 50(2): 665–670. https://doi.org/10.12681/bgsg.11772',
    'Chung, H., Kim, J., Mccann, M. T., Klasky, M. L., & Ye, J. C. (2022). Diffusion posterior sampling for general noisy inverse problems. arXiv:2209.14687.',
    'Cornes, R. C., van der Schrier, G., van den Besselaar, E. J. M., & Jones, P. D. (2018). An ensemble version of the E-OBS temperature and precipitation data sets. Journal of Geophysical Research: Atmospheres 123(17): 9391–9409. https://doi.org/10.1029/2017JD028200',
    'Dashti, M., & Stuart, A. M. (2017). The Bayesian approach to inverse problems. Handbook of Uncertainty Quantification, 311–428. Springer.',
    'Emerick, A. A., & Reynolds, A. C. (2013). Ensemble smoother with multiple data assimilation. Computers & Geosciences 55: 3–15.',
    'Huang, J., Yang, G., Wang, Z., & Park, J. J. (2024). DiffusionPDE: generative PDE-solving under partial observation. arXiv:2406.17763.',
    'Karras, T., Aittala, M., Aila, T., & Laine, S. (2022). Elucidating the design space of diffusion-based generative models. Advances in Neural Information Processing Systems 35: 26565–26577.',
    'Kovachki, N., Li, Z., Liu, B., Azizzadenesheli, K., Bhattacharya, K., Stuart, A., & Anandkumar, A. (2023). Neural operator: learning maps between function spaces with applications to PDEs. Journal of Machine Learning Research 24(89): 1–97.',
    'Li, Z., Kovachki, N., Azizzadenesheli, K., Liu, B., Bhattacharya, K., Stuart, A., & Anandkumar, A. (2020). Fourier neural operator for parametric partial differential equations. arXiv:2010.08895.',
    'Lim, J. H., Kovachki, N. B., Baptista, R., Beckham, C., Azizzadenesheli, K., Kossaifi, J., Voleti, V., Song, J., Kreis, K., Kautz, J., et al. (2023). Score-based diffusion models in function space. arXiv:2302.07400.',
    'Muñoz-Sabater, J., Dutra, E., Agustí-Panareda, A., Albergel, C., Arduini, G., Balsamo, G., Boussetta, S., Choulga, M., Harrigan, S., Hersbach, H., Martens, B., Miralles, D. G., Piles, M., Rodríguez-Fernández, N. J., Zsoter, E., Buontempo, C., & Thépaut, J.-N. (2021). ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. Earth System Science Data 13(9): 4349–4383. https://doi.org/10.5194/essd-13-4349-2021',
    'Pidstrigach, J., Marzouk, Y., Reich, S., & Wang, S. (2023). Infinite-dimensional diffusion models. arXiv:2302.10130.',
    'Rahman, M. A., Ross, Z. E., & Azizzadenesheli, K. (2022). U-NO: U-shaped neural operators. arXiv:2204.11127.',
    'Robbins, H. E. (1992). An empirical Bayes approach to statistics. In Breakthroughs in Statistics: Foundations and Basic Theory, 388–394. Springer.',
    'Rodriguez-Iturbe, I., Porporato, A., Ridolfi, L., Isham, V., & Cox, D. R. (1999). Probabilistic modelling of water balance at a point: the role of climate, soil and vegetation. Proceedings of the Royal Society A 455(1990): 3789–3805.',
    'Strack, O. D. L. (1976). A single-potential solution for regional interface problems in coastal aquifers. Water Resources Research 12(6): 1165–1174. https://doi.org/10.1029/WR012i006p01165',
    'Yao, J., Mammadov, A., Berner, J., Kerrigan, G., Ye, J. C., Azizzadenesheli, K., & Anandkumar, A. (2025). Guided diffusion sampling on function spaces with applications to PDEs. 39th Conference on Neural Information Processing Systems (NeurIPS 2025); arXiv:2505.17004v3. Code: https://github.com/neuraloperator/FunDPS',
    'Zeqiraj, D. (2026). Goal-oriented Bayesian experimental design for variable-density seawater intrusion: adjoint expected information gain for joint monitoring and managed-aquifer-recharge placement. Journal of Hydrology 680: 136559. https://doi.org/10.1016/j.jhydrol.2026.136559',
    'Internal documents: SHIU-GO, "Rain, recharge and the stochastic conditions of the coastal-aquifer equations" (November 2026; rain law, Proposition 6 and Appendix A); ASIMILIMI-GO, note on the assimilation of the boundary and initial conditions of Fushë-Kuqe (October 2026); the Fushë-Kuqe chloride study (code in chloride_fk/: Strack areal model and 20 000-draw calibration); the CERTAIN-COAST methodology (WP2, coupled model with ES-MDA); the workbook Fushe_Kuqe_All_Data.xlsx (Albanian Geological Survey, 2024, and A. Beqiraj; used with their permission).',
]


def blocks(E, T, TU):
    vals = values(E, T, TU)
    B = (static_blocks() + bc_blocks() + method_blocks() + result_blocks() + application_blocks() + closing_blocks())

    def fill(s):
        return re.sub(r'<<(\w+)>>', lambda m: vals[m.group(1)], s) if isinstance(s, str) else s

    def fill_any(x):
        if isinstance(x, (list, tuple)):
            return type(x)(fill_any(y) for y in x)
        return fill(x)
    return [tuple(fill_any(x) for x in b) for b in B], vals


# ------------------------------------------------------------------------------------------------------------ values
def values(E, T, TU):
    import rgo_model as M
    import rgo_fundps as F
    pc = lambda x, d=0: f'{100 * x:.{d}f}%'
    n = lambda x, d=0: f'{x:,.{d}f}'
    v = {}
    # set-up, from the code
    v['nx'], v['nt'] = str(M.NX), str(M.NT)
    v['L'] = n(M.L / 1000, 0); v['dx'] = n(M.DX, 0)
    v['T'] = n(M.TRANS); v['S'] = n(M.STOR, 2); v['Q'] = n(M.Q_W, 1); v['xw'] = n(M.X_W)
    v['piezo'] = ', '.join(n(p) for p in M.PIEZO)
    v['tau'] = n(M.TAU_V); v['kmed'] = n(M.KAP_MED, 2); v['klsd'] = n(M.KAP_LSD, 2)
    v['cv_k'] = pc(np.sqrt(np.exp(M.KAP_LSD ** 2) - 1))
    P = M.PRI
    v['e_sd'] = n(P['e_sd'], 2); v['e_l'] = n(P['e_l']); v['eta_m_sd'] = n(P['eta_m_sd'], 2); v['eta_sd'] = n(P['eta_sd'], 2)
    v['eta_l'] = n(P['eta_l']); v['q_m'] = n(P['q_m'], 1); v['q_m_sd'] = n(P['q_m_sd'], 1); v['q_sd'] = n(P['q_sd'], 1)
    v['q_l'] = n(P['q_l']); v['h0_sd'] = n(P['h0_sd'], 1); v['h0_l'] = n(P['h0_l']); v['ymult'] = n(P['ymult_lsd'], 1)
    v['sig_h'] = n(100 * M.SIG_H); v['sig_eta'] = n(100 * M.SIG_ETA); v['p_obs'] = pc(M.P_OBS)
    v['nz'] = str(M.NZ); v['spin'] = n(M.SPIN)
    # the solver as a linear map, against the simulator
    v['hop_err'] = f'{hop_error():.0e}'.replace('e-0', '×10⁻').replace('e-', '×10⁻')
    # training
    v['nparam'] = n(T['nparam']); v['steps'] = n(T['steps']); v['batch'] = str(T['batch'])
    v['train_min'] = n(T['seconds'] / 60); v['loss_end'] = n(float(np.mean(T['loss'][-50:])), 3)
    v['ntrain'] = n(24000)
    # sampler and evaluation
    v['nstep'] = str(E['nstep']); v['ns_a'] = str(E['ns_a']); v['ns_pure'] = str(E['ns_pure']); v['n_case'] = str(E['n_case'])
    v['rain_loss'] = E['rain']['loss'].upper() if E['rain']['loss'] == 'mse' else 'L2'
    v['rain_w'] = n(E['rain']['w']); v['pure_wP'] = n(E['pure']['wP']); v['pure_wH'] = n(E['pure']['wH'])
    v['pure_loss'] = E['pure']['loss'].upper() if E['pure']['loss'] == 'mse' else 'L2'
    Mt = {k: E['methods'][k]['agg'] for k in E['methods'] if E['methods'][k]['agg']}
    units = dict(eta=('cm', 100), qL=('m²/d', 1), r=('mm/d', 1), h0=('cm', 100), h=('cm', 100))
    dec = dict(eta=1, qL=2, r=3, h0=1, h=1)
    for m, a in Mt.items():
        for c in ('eta', 'qL', 'r', 'h0', 'h'):
            u, f = units[c]
            v[f'{m}_{c}_rf'] = n(a[c]['rmse_f'] * f, dec[c]); v[f'{m}_{c}_re'] = n(a[c]['rmse_e'] * f, dec[c])
            v[f'{m}_{c}_ratio'] = n(a[c]['ratio'], 2); v[f'{m}_{c}_sr'] = n(a[c]['sd_ratio'], 2)
            v[f'{m}_{c}_cf'] = pc(a[c]['cov_f']); v[f'{m}_{c}_ce'] = pc(a[c]['cov_e'])
            v[f'{m}_{c}_sde'] = n(a[c]['sd_e'] * f, dec[c])
        kk = a['kappa']
        v[f'{m}_k_ef'] = n(kk['abs_err_f'], 3); v[f'{m}_k_ee'] = n(kk['abs_err_e'], 3)
        v[f'{m}_k_sf'] = n(kk['sd_f'], 3); v[f'{m}_k_se'] = n(kk['sd_e'], 3); v[f'{m}_k_z'] = n(kk['z'], 2)
        v[f'{m}_fit'] = n(100 * a['fit'], 1) if np.isfinite(a['fit']) else '–'
        v[f'{m}_cons'] = n(100 * a['physics']['consistency'], 1)
        v[f'{m}_fitd'] = n(100 * a['physics']['fit_diffusion'], 1) if np.isfinite(a['physics']['fit_diffusion']) else '–'
        v[f'{m}_frms'] = n(a['f_rms'], 3)
        v[f'{m}_sec'] = n(a['seconds'])
        v[f'{m}_ndiv'] = str(E['methods'][m]['n_diverged'])
    v['nobs_B'] = n(Mt['hybrid_B']['n_obs']); v['nobs_C'] = n(Mt['hybrid_C']['n_obs'])
    pr = E['prior_sd']
    meth = dict(A='fundps_A', B='hybrid_B', C='hybrid_C')
    for c in ('eta', 'qL', 'r', 'h0'):
        u, f = units[c]
        v[f'{c}_prior'] = n(pr[c] * f, dec[c])
        for s, m in meth.items():
            v[f'{c}_lad_{s}'] = pc(Mt[m][c]['sd_e'] / pr[c])
            v[f'{c}_sde_{s}'] = n(Mt[m][c]['sd_e'] * f, dec[c])
    # the first training (weekly rain of the window in the fifth channel): diagnosis of plain guidance and ablation
    import json, os
    r1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res', 'run1_rain_channel')
    with open(os.path.join(r1, 'guidance_diagnosis.json')) as fh:
        Gd = json.load(fh)['runs']
    with open(os.path.join(r1, 'hybrid_validation.json')) as fh:
        Hv = json.load(fh)
    ch_rows = [r for r in Gd if not r['phys_operator'] and not r['bc_geometry_scaled'] and not r.get('diverged')]
    best_ch = min(ch_rows, key=lambda r: r['fit_head_channel_cm'])
    v['d_fit_ch'] = n(best_ch['fit_head_channel_cm'], 1); v['d_fit_ch_sim'] = n(best_ch['fit_resimulated_cm'], 0)
    ph_rows = [r for r in Gd if r['phys_operator'] and not r['bc_geometry_scaled'] and not r.get('diverged')]
    v['d_fit_ph_best'] = n(min(r['fit_resimulated_cm'] for r in ph_rows), 0)
    v['d_ph_sd_q_min'] = n(min(r['qL']['sd_ratio'] for r in ph_rows), 1)
    v['d_ph_sd_q_max'] = n(max(r['qL']['sd_ratio'] for r in ph_rows), 1)
    geo = [r for r in Gd if r['bc_geometry_scaled']]
    v['d_geo_div'] = str(sum(r.get('diverged', False) for r in geo)); v['d_geo_n'] = str(len(geo))
    v['d_n_cfg'] = str(len(ch_rows) + len(ph_rows))
    a2 = TU['rain'][f"{E['rain']['loss']}_{E['rain']['w']:g}"]
    for c in ('r', 'h0'):
        v[f'abl1_{c}'] = n(Hv['A'][c]['ratio_of_means'], 2)
        v[f'abl2_{c}'] = n(a2[c]['rmse_f'] / a2[c]['rmse_e'], 2)
    v['abl1_rB'] = n(Hv['B_es']['r']['ratio_of_means'], 2)
    # derived numbers and guards on the findings the text states
    A, HB, HC, PB, PC = (Mt[k] for k in ('fundps_A', 'hybrid_B', 'hybrid_C', 'pure_B', 'pure_C'))
    chans = ('eta', 'qL', 'r', 'h0')
    v['A_err_dev'] = pc(max(abs(A[c]['ratio'] - 1) for c in chans))
    v['A_sd_dev'] = pc(max(abs(A[c]['sd_ratio'] - 1) for c in chans))
    assert max(abs(A[c]['ratio'] - 1) for c in chans) < 0.25 and max(abs(A[c]['sd_ratio'] - 1) for c in chans) < 0.15, \
        'text: with the rain alone FunDPS is close to the exact posterior'
    assert all(HB[c]['ratio'] < PB[c]['ratio'] and abs(np.log(HB[c]['sd_ratio'])) < abs(np.log(PB[c]['sd_ratio']))
               for c in chans), 'text: in B the update beats plain FunDPS for every condition'
    assert all(HC[c]['ratio'] < PC[c]['ratio'] for c in ('qL', 'r', 'h0')) and HC['eta']['ratio'] > PC['eta']['ratio'], \
        'text: in C the update is better except for the sea level'
    assert HB['fit'] < 1.5 * M.SIG_H and PB['fit'] > 5 * M.SIG_H, 'text: the update fits the heads at the noise level'
    assert HB['kappa']['sd_f'] < 0.5 * HB['kappa']['sd_e'], 'text: the update is too narrow in kappa'
    assert HB['eta']['sd_ratio'] < 1 and HB['r']['sd_ratio'] > 1 and HB['h0']['sd_ratio'] > 1, 'text: narrow and wide'
    gains = [PC[c]['ratio'] / HC[c]['ratio'] for c in ('qL', 'r', 'h0')]
    v['C_gain_min'], v['C_gain_max'] = n(min(gains), 1), n(max(gains), 1)
    v['k_narrow'] = n(HB['kappa']['sd_e'] / HB['kappa']['sd_f'], 0)
    v['hyb_min'] = n(min(HB[c]['ratio'] for c in chans), 2); v['hyb_max'] = n(max(HB[c]['ratio'] for c in chans), 2)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'res', 'rgo_norm.json')) as fh:
        st = json.load(fh)
    v['f_rel'] = pc(A['f_rms'] / st['f_sd'])
    v['pure_B_fit_cm'] = n(100 * PB['fit'], 1); v['hybrid_B_fit_cm'] = n(100 * HB['fit'], 1)
    v['box'] = box_text(v)
    return v


def hop_error():
    """largest difference between the linear solver map and the simulator, on three prior draws (m)."""
    import rgo_model as M
    import rgo_fundps as F
    Rm = F.solver_matrices()
    a, _ = M.sample_prior(np.random.default_rng(4), 3)
    h0, eta, qL, r = a[:, 0, :, 0], a[:, 1, 0], a[:, 2, 0], a[:, 3, 0]
    h_lin = h0 @ Rm['h0'].T + eta @ Rm['eta'].T + qL @ Rm['qL'].T + r @ Rm['r'].T + Rm['cQ'][None]
    return float(np.abs(h_lin - a[:, 0].reshape(3, -1)).max())


def box_text(v):
    return ('**In short.** All boundary and initial conditions of the simulation (sea level, inland inflow, recharge and '
            'the initial head) are treated as one function together with the head. A denoising neural operator learns '
            'their prior from the physical simulator, and FunDPS sampling conditions it on the rain record. Heads and '
            'tide-gauge data then enter through an ensemble update with the exact aquifer solver. The test bed has an '
            'exact posterior. With the rain alone FunDPS matches it: errors within ' + v['A_err_dev'] + ' and spreads '
            'within ' + v['A_sd_dev'] + ' of the exact ones. With four head loggers the update fits the heads to ' +
            v['hybrid_B_fit_cm'] + ' cm (noise ' + v['sig_h'] + ' cm), where plain FunDPS guidance misses them by ' +
            v['pure_B_fit_cm'] + ' cm.')


# ------------------------------------------------------------------------------------------------------------ text
def static_blocks():
    return [
        ('title', 'Reconstructing all boundary conditions of a coastal aquifer from rain and the Fushë-Kuqe data'),
        ('subtitle', 'RINDËRTIMI-GO: function-space diffusion with a denoising neural operator and guided sampling (FunDPS), '
                     'joined to an ensemble update with the exact aquifer solver, for the boundary and initial conditions '
                     'of the coastal-aquifer simulation, checked against the exact posterior'),
        ('byline', 'Prepared for Assoc. Prof. Dr. Dulian Zeqiraj · Faculty of Geology and Mining, Polytechnic University '
                   'of Tirana · 4 November 2026'),

        ('h', '1. The problem and the short answer'),
        ('p', 'The coastal-aquifer simulation of our methodology (the coupled model of density-driven flow, salt and the '
              'interface) needs boundary and initial conditions. These are the sea level at the western boundary, the '
              'inflow through the inland boundaries, recharge from rain at the land surface, pumping at the wells, and '
              'the initial state of the head and of the interface. At Fushë-Kuqe none of them is measured as a time '
              'series. What we have is rain (from the European meteorological services, from IGJEO or from another '
              'source) and the Excel workbook with the static data: K from pumping tests, the depth of the cover, soil, '
              'the wells and the aquifer boundary.'),
        ('img', 'scheme', 17.0),
        ('cap', 'Figure {{scheme}}. The RINDËRTIMI-GO scheme, drawn after Figure 2 of Yao et al. (2025) for the coastal '
                'aquifer: sampling with FunDPS guidance (top left), training of the denoising neural operator (right), and '
                'the path from the data to the coupled simulation (bottom).'),
        ('p', 'The question is how to build all these conditions, with their uncertainty, as an inverse problem. The '
              'answer follows FunDPS (Yao et al., 2025). A diffusion model in function space learns the joint prior of '
              'the boundary conditions and the head, and its sampling is guided by the data we have. Field data for '
              'training do not exist, so the prior is learned from the physical simulator: the rain law of SHIU-GO, the '
              'filter of the unsaturated zone and the aquifer, with the static parameters from the workbook. Figure '
              '{{scheme}} shows the whole scheme.'),
        ('p', '*How to read Figure {{scheme}}.* Every card is a field of the model: four stripes for $\\eta$, $q_L$, $r$ and $f$ '
              'in time above the head map $h(x,t)$, with time to the right and the sea at the bottom; noisy states are shown '
              'as $a/\\sqrt{1+\\sigma^2}$. Sampling runs from GRF noise $a_N$ to the reconstruction $a_0$. The green box '
              'enlarges one step: the neural operator $D_\\theta$ gives the denoised sample $\\hat a_0$, the Heun step '
              'gives $\\hat a_{t-1}$, and the likelihood gradient $\\partial$ moves it towards the observation $u$, here the '
              'rain filtered by the unsaturated zone; $\\Pi$ keeps the boundary channels functions of time only. Training '
              'uses the EDM loss on samples of the physical prior. The FunDPS ensemble then goes through an ensemble update '
              'with the exact solver, where heads and the tide gauge enter, and the boundary conditions (90% band of '
              'scenario B, truth dashed) drive the coupled simulation.'),
        ('box', '<<box>>'),

        ('h', '2. What is taken from FunDPS'),
        ('p', 'Yao et al. (2025) build a framework for conditional sampling in inverse problems governed by partial '
              'differential equations, when the measurements are very sparse or noisy. An unconditional diffusion model '
              'is trained in function space with a neural operator, and at sampling time the samples are pulled towards '
              'the observations by a guidance gradient. Table {{tab_src}} lists what is taken and where it enters.'),
        ('cap', 'Table {{tab_src}}. The elements of FunDPS and their place in RINDËRTIMI-GO.'),
        ('table', ['Element of FunDPS', 'What it says', 'Where it enters here'],
         [['Bayesian inverse problem in function space (Section 3.1, Eqs. 1–3)',
           '$u = \\mathcal{A}(a) + \\varepsilon$; the posterior is absolutely continuous with respect to the prior, with '
           'the likelihood as Radon–Nikodym derivative (Dashti & Stuart, 2017); $\\mathcal{A}$ may contain the solution '
           'operator of the PDE', 'Observation operators [[obs]] and [[hop]]'],
          ['Noising with Gaussian random fields (Eq. 4)', '$a_t = a_0 + \\sigma_t \\varepsilon_t$, '
           '$\\varepsilon_t \\sim \\mathcal{N}(0, C_\\gamma)$ (Lim et al., 2023)', 'Noise [[noise]]'],
          ['Decomposition of the conditional score (Eq. 6)', 'conditional score = likelihood gradient + prior score',
           'Guidance [[guide]]'],
          ['Likelihood approximation (Eqs. 8–11)', '$\\tilde\\Phi_t(a_t, u) \\approx \\Phi(\\hat a_0(a_t), u)$ with '
           '$\\hat a_0 = \\text{E}[a_0 \\mid a_t]$', 'Guidance [[guide]]'],
          ['Tweedie\'s formula in Banach spaces (Theorem 3.1)', 'the conditional expectation is the Fréchet derivative of '
           'the log density with respect to the noise measure (Robbins, 1992)', 'Equation [[tweedie]]'],
          ['Guidance and weights (Eqs. 13–14, Appendix G, Table 4)', '$a \\leftarrow a - \\zeta \\nabla_a \\|u - '
           '\\mathcal{A}(D_\\theta(a, t))\\|^2$, or the L2 norm; one weight per observation type; '
           '$\\tilde\\zeta_t = \\sigma_t \\zeta$ for $\\sigma_t < 1$', 'Guidance [[guide]]'],
          ['Joint embedding', 'parameters and solution in one function; $\\mathcal{A}$ as a mask', 'The function $a$ [[joint]]'],
          ['EDM loss and Heun sampler (Karras et al., 2022)', 'preconditioning $c_{skip}, c_{out}, c_{in}$; schedule '
           '$\\sigma_i$ with $\\rho = 7$', 'Equations [[edm]] and [[sched]]'],
          ['Multi-resolution training and inference (ReNoise)', 'speed-up', 'Not used: the grid here is <<nx>> × <<nt>>'],
          ['Reported limitation: a PDE loss during sampling helps little', '—',
           'Physics enters as prior, as observation operator [[hop]] and as ensemble update [[es]]']],
         [4.4, 7.6, 5.0], 9.5),
    ]


def bc_blocks():
    return [
        ('h', '3. The boundary conditions needed and the data available'),
        ('p', 'Figure {{fk_bc}} shows where each condition enters the coastal sector of Fushë-Kuqe (y ≥ 24 km), with the '
              'geometry of the calibrated areal model of the chloride study. In that model $\\phi = 0$ at the shoreline and '
              'there is no flow through the other margins. A transient simulation needs more: the sea level in time, the '
              'inflow through the eastern margin and through the southern cut of the model, recharge in time and space, '
              'pumping and the initial state. Table {{tab_bc}} gives the list, the mathematical type of each condition, '
              'its data and its status.'),
        ('img', 'fk_bc', 17.0),
        ('cap', 'Figure {{fk_bc}}. Boundary conditions of Fushë-Kuqe. (a) Contact with the sea (blue), eastern margin '
                '(purple), southern cut of the model at y = 24 km (orange), hills in the south-west and northern margin '
                '(brown), recharge surface (green), wells with K in the Excel workbook (dots), and the loggers P3, A3, A13 '
                'and the new piezometer V2 proposed in SHIU-GO. The dotted lines are the 0.1° graticule, the size of the '
                'E-OBS and ERA5-Land rain cells; the sector spans about two to three cells. Coordinates are km from the '
                'origin of the workbook (Gauss–Krüger zone 4). (b) The conditions, their form and their data.'),
        ('cap', 'Table {{tab_bc}}. Boundary and initial conditions of the simulation and the data for each. Yellow marks '
                'what has to be confirmed.'),
        ('table', ['Condition', 'Type', 'Data', 'In RINDËRTIMI-GO'],
         [['Sea level $\\eta(t)$', 'Dirichlet at the sea contact', '==Nearest tide gauge or a sea-level product; source '
           'and period to be confirmed==', 'Reconstructed; observed in scenario C'],
          ['Inflow from the east $q_E(t)$', 'Neumann', 'Not measured', 'Reconstructed; the prior contains the zero '
           'flux of the calibrated model'],
          ['Inflow through the cut at y = 24 km $q_S(t)$', 'Neumann (a model boundary, not an aquifer boundary)',
           'Not measured', 'Reconstructed from heads'],
          ['Hills, northern margin', 'No flow', 'Assumption of the calibrated model', 'Checked with the head residuals'],
          ['Recharge $r(x,t)$', 'Areal source', 'Daily rain: E-OBS (Cornes et al., 2018), ERA5-Land (Muñoz-Sabater et '
           'al., 2021) or ==the IGJEO station (site, period and access to be confirmed)==; cover and soil from the '
           'workbook', 'Timing from rain; size from the prior and from heads (Propositions 4 and 5)'],
          ['Pumping $Q_j(t)$', 'Point sources', '==Operator records not yet available==', 'Known in the test; in the '
           'field requested or treated as unknown'],
          ['Initial state $h_0$, $\\zeta_0$', 'Initial condition', 'Calibrated areal model (Strack, 1976)',
           'Reconstructed: steady state plus a GRF']],
         [3.4, 3.0, 6.0, 4.6], 9.5),
        ('p', 'The workbook has no time series, but it fixes three things in the prior. First, K from the pumping tests '
              '(43 wells, 50–200 m/d) fixes the scale of the transmissivity, which by Proposition 5 ties the size of '
              'recharge to the heads. Second, the DRASTIC depth gives the thickness of the cover and so the delay '
              '$\\tau(x)$ of the unsaturated zone. Third, the boundary gives the geometry and the sector. Rain gives the '
              'timing of recharge.'),
    ]


def method_blocks():
    return [
        ('h', '4. Method'),
        ('h2', '4.1 The joint function and the physics'),
        ('p', 'In the test bed the aquifer is a coastal section of length $L$ = <<L>> km, with the sea at $x = 0$ and the '
              'inland boundary at $x = L$. All unknowns and data are collected in one function on $D \\times (0, T_f)$:'),
        ('eq', 'joint', 'a = \\left(h(x,t),\\ \\eta(t),\\ q_L(t),\\ r(t),\\ f(t)\\right) \\in \\mathcal{A} = L^2(D \\times (0,T_f)) \\times L^2(0,T_f)^4'),
        ('p', 'where $h$ is the head, $\\eta$ the sea level, $q_L$ the inflow through the inland boundary, $r$ the '
              'recharge and $f$ the rain filtered by the unsaturated zone. The head solves the flow equation with its '
              'boundary and initial conditions:'),
        ('eq', 'flow', ('S\\, \\frac{\\partial h}{\\partial t} = T\\, \\frac{\\partial^2 h}{\\partial x^2} + r(t) - Q\\, \\delta(x - x_w),',
                        'h(0,t) = \\eta(t), \\quad T\\, \\frac{\\partial h}{\\partial x}(L,t) = q_L(t), \\quad h(x,0) = h_0(x)')),
        ('p', 'with $T$ = <<T>> m²/d, $S$ = <<S>>, known pumping $Q$ = <<Q>> m²/d at $x_w$ = <<xw>> m and piezometers at '
              '<<piezo>> m. Recharge comes from rain through the unsaturated zone, with the Erlang kernel of order two as '
              'in SHIU-GO:'),
        ('eq', 'rech', ('r(t) = \\kappa\\, f(t) + e(t), \\quad f(t) = \\int_0^\\infty k_\\tau(s)\\, P(t - s)\\, ds, \\quad k_\\tau(s) = \\frac{s}{\\tau^2}\\, e^{-s/\\tau}')),
        ('p', 'where $\\tau$ = <<tau>> d, $\\kappa$ is the recharge coefficient and $e$ its error. The filtered rain $f$ is '
              'computed from the whole rain record, including the <<spin>> days before the window, so it carries the '
              'antecedent rain that the weekly rain of the window alone does not have. The discretisation is implicit '
              'Euler with weekly steps on <<nx>> cells × <<nt>> weeks, with a half-cell link to the sea.'),

        ('h2', '4.2 The physical prior and the role of the static data'),
        ('p', 'The prior of the joint function is built by the simulator, not from field data:'),
        ('b', 'Daily rain follows the seasonal marked Poisson law of SHIU-GO (Rodriguez-Iturbe et al., 1999), with a '
              'lognormal yearly multiplier of log standard deviation <<ymult>>.'),
        ('b', 'The coefficient $\\kappa$ is lognormal with median <<kmed>> and log standard deviation <<klsd>>; its '
              'coefficient of variation is <<cv_k>>. The error $e$ is a Gaussian process with standard deviation <<e_sd>> '
              'mm/d and correlation length <<e_l>> weeks.'),
        ('b', 'The sea level is a random mean (standard deviation <<eta_m_sd>> m) plus a Gaussian random field (<<eta_sd>> m, '
              'length <<eta_l>> weeks). The inflow $q_L$ has mean <<q_m>> ± <<q_m_sd>> m²/d plus a Gaussian random field '
              '(<<q_sd>> m²/d, <<q_l>> weeks).'),
        ('b', 'The initial condition is the steady state of the mean forcing plus a Gaussian random field in $x$ (standard '
              'deviation <<h0_sd>> m, length <<h0_l>> m).'),
        ('p', 'At Fushë-Kuqe the same route takes K and its scale from the workbook, the cover for $\\tau(x)$, the soil '
              'groups for the bucket parameters and the boundary for the geometry. The prior then carries the static '
              'data, and the neural operator learns only what the simulator allows.'),

        ('h2', '4.3 Diffusion in function space'),
        ('p', 'The noising process adds a Gaussian random field with covariance $C$ to the function (Lim et al., 2023; Yao '
              'et al., 2025, Eq. 4):'),
        ('eq', 'noise', 'a_\\sigma = a_0 + \\sigma\\, \\xi, \\quad \\xi \\sim \\gamma = \\mathcal{N}(0, C), \\quad a_0 \\sim \\nu'),
        ('p', 'For the head channel $\\xi$ is a GRF in $(x, t)$; for the four boundary channels it is a GRF in $t$ only, the '
              'same for every $x$. The covariance is squared-exponential with length 0.05 of the unit domain, the '
              'rbf_scale of FunDPS. The noisy state therefore stays in the space where the boundary conditions depend on '
              'time only (Proposition 1). The conditional expectation of the clean function is given by Theorem 3.1 of '
              'Yao et al. (2025), Tweedie\'s formula in Banach spaces:'),
        ('eq', 'tweedie', '\\hat a_0(a_\\sigma) = \\text{E}\\left[a_0 \\mid a_\\sigma\\right] = R\\, D_{H(\\gamma_\\sigma)} \\log \\frac{d\\nu_\\sigma}{d\\gamma_\\sigma}(a_\\sigma)'),
        ('p', 'where $\\gamma_\\sigma = \\mathcal{N}(0, \\sigma^2 C)$, $H(\\gamma_\\sigma)$ is the Cameron–Martin space '
              '(Bogachev, 1998), $D$ the Fréchet derivative and $R$ the Riesz map. The neural operator '
              '$D_\\theta(a, \\sigma) \\approx \\hat a_0$ is learned with the EDM loss (Karras et al., 2022):'),
        ('eq', 'edm', ('\\mathcal{L}(\\theta) = \\text{E}_{\\sigma, a_0, \\xi}\\, \\lambda(\\sigma)\\, \\| D_\\theta(a_0 + \\sigma \\xi, \\sigma) - a_0 \\|^2, \\quad \\lambda(\\sigma) = \\frac{\\sigma^2 + \\sigma_d^2}{\\sigma^2 \\sigma_d^2},',
                       '\\ln \\sigma \\sim \\mathcal{N}(-1.2,\\ 1.2^2)')),
        ('p', 'Unconditional sampling solves the probability-flow equation with Heun steps on the schedule of Karras et '
              'al. (2022):'),
        ('eq', 'sched', ('\\frac{da}{d\\sigma} = \\frac{a - D_\\theta(a, \\sigma)}{\\sigma}, \\quad \\sigma_i = \\left(\\sigma_{max}^{1/\\rho} + \\frac{i}{N-1}\\left(\\sigma_{min}^{1/\\rho} - \\sigma_{max}^{1/\\rho}\\right)\\right)^{\\rho}')),
        ('p', 'with $N$ = <<nstep>>, $\\sigma_{max}$ = 20, $\\sigma_{min}$ = 0.002 and $\\rho$ = 7. FunDPS uses '
              '$\\sigma_{max}$ = 80; here the data are normalised to a standard deviation near 1, so 20 is enough.'),

        ('h2', '4.4 The denoising neural operator'),
        ('p', 'The operator $D_\\theta$ is a Fourier neural operator (Li et al., 2020; Kovachki et al., 2023) conditioned on '
              'the noise level. FunDPS uses a U-NO (Rahman, Ross & Azizzadenesheli, 2022); on the small grid here an FNO '
              'is enough. With the EDM preconditioning,'),
        ('eq', 'precond', ('D_\\theta(a, \\sigma) = \\Pi\\left[c_{skip}(\\sigma)\\, a + c_{out}(\\sigma)\\, F_\\theta\\left(c_{in}(\\sigma)\\, a,\\ \\tfrac{1}{4}\\ln\\sigma\\right)\\right],',
                           'c_{skip} = \\frac{\\sigma_d^2}{\\sigma^2 + \\sigma_d^2}, \\quad c_{out} = \\frac{\\sigma \\sigma_d}{\\sqrt{\\sigma^2 + \\sigma_d^2}}, \\quad c_{in} = \\frac{1}{\\sqrt{\\sigma^2 + \\sigma_d^2}}')),
        ('p', 'The network $F_\\theta$ lifts the input (five channels plus the coordinates) to 32 channels, passes it through '
              'four Fourier blocks and projects it back to five channels. Each block is'),
        ('eq', 'fno', 'v_{l+1} = v_l + \\text{GELU}\\left(\\mathcal{F}^{-1}\\left(R_l \\cdot \\mathcal{F} v_l\\right) + W_l v_l + b_l + e_l(\\sigma)\\right)'),
        ('p', 'where $\\mathcal{F}$ is the Fourier transform in $(x, t)$ with 8 × 12 retained modes, $R_l$ the spectral '
              'weights, $W_l$ a pointwise layer and $e_l(\\sigma)$ the embedding of the noise level. The network has '
              '<<nparam>> parameters. The projection $\\Pi$ of the boundary channels takes the mean along $x$:'),
        ('eq', 'proj', '(\\Pi a)_c(x, t) = \\frac{1}{|D|} \\int_D a_c(x\', t)\\, dx\', \\quad c \\in \\{\\eta, q_L, r, f\\}, \\qquad (\\Pi a)_h = a_h'),
        ('p', '**Proposition 1 (projection).** $\\Pi$ is the orthogonal projection in $L^2(D)$ onto functions that do not '
              'depend on $x$. Since $a_0$ and the noise of the boundary channels lie in that space, so does '
              '$\\hat a_0 = \\text{E}[a_0 \\mid a_\\sigma]$, and'),
        ('eq', 'projbound', '\\left\\| \\Pi D_\\theta(a, \\sigma) - \\hat a_0(a) \\right\\| = \\left\\| \\Pi\\left(D_\\theta(a, \\sigma) - \\hat a_0(a)\\right) \\right\\| \\le \\left\\| D_\\theta(a, \\sigma) - \\hat a_0(a) \\right\\|'),
        ('p', 'So the projection never increases the error of the denoiser and keeps the samples in the space of boundary '
              'conditions. *Proof:* the conditional expectation of a variable with values in a closed linear subspace '
              'stays in that subspace; then $\\Pi \\hat a_0 = \\hat a_0$ and $\\|\\Pi\\| \\le 1$.'),

        ('h2', '4.5 Guided sampling with the rain'),
        ('p', 'The observations are linear functions of $a$ with noise:'),
        ('eq', 'obs', ('u_f = f(t_k), \\quad u_h = h(x_j, t_k) + \\varepsilon_h, \\quad u_\\eta = \\eta(t_k) + \\varepsilon_\\eta,',
                       '\\varepsilon_h \\sim \\mathcal{N}(0, \\sigma_h^2), \\quad \\varepsilon_\\eta \\sim \\mathcal{N}(0, \\sigma_\\eta^2)')),
        ('p', 'with $\\sigma_h$ = <<sig_h>> cm and $\\sigma_\\eta$ = <<sig_eta>> cm. Three scenarios cover the path from the '
              'data we have today to the data that can be added:'),
        ('b', '**A, rain only.** The complete filtered rain: what the workbook and a rain record give.'),
        ('b', '**B, rain and loggers.** Four piezometers are added, each read in <<p_obs>> of the weeks (about <<nobs_B>> '
              'values).'),
        ('b', '**C, B and a tide gauge.** The weekly sea level is added.'),
        ('p', 'The FunDPS guidance step (Eq. 14 of Yao et al.) follows every Heun step, with one weight per observation type '
              'and the schedule of their Appendix G, and is followed by $\\Pi$:'),
        ('eq', 'guide', ('a_{i+1} = \\Pi\\left[\\tilde a_{i+1} - \\tilde\\zeta_i\\, \\nabla_{a_i} \\sum_{k} w_k\\, \\ell\\left(\\frac{1}{m_k} \\left\\| u_k - \\mathcal{A}_k\\left(D_\\theta(a_i, \\sigma_i)\\right) \\right\\|^2\\right)\\right],',
                         '\\tilde\\zeta_i = \\min(\\sigma_i, 1), \\quad \\ell(s) = s \\ (\\text{MSE}) \\ \\text{or} \\ \\ell(s) = \\sqrt{s} \\ (\\text{L2})')),
        ('p', 'where $\\tilde a_{i+1}$ is the Heun step without guidance, $\\mathcal{A}_k$ the observation mask of type $k$ '
              'and $m_k$ the number of observations; FunDPS uses both loss types (their Table 4). In RINDËRTIMI-GO the '
              'guidance uses the filtered rain only: <<rain_loss>> loss with $w_f$ = <<rain_w>>, chosen on validation '
              'cases kept apart from the test cases.'),

        ('h2', '4.6 Why guidance alone cannot take in precise heads'),
        ('p', 'The heads could enter the same guidance. Two ways were tried. The first reads the head channel of the denoised '
              'function. The second passes the denoised boundary and initial conditions through the aquifer solver, which '
              'FunDPS allows ($\\mathcal{A}$ may contain the solution operator of the PDE). The solver is linear here, so '
              'it is an exact, differentiable linear map:'),
        ('eq', 'hop', '\\mathcal{A}_h(a) = M_h\\, \\mathcal{S}(h_0, \\eta, q_L, r) = M_h \\left(R_{h_0} h_0 + R_\\eta\\, \\eta + R_q\\, q_L + R_r\\, r + c_Q\\right)'),
        ('p', 'where $M_h$ selects the observed piezometers and weeks and the columns of $R$ are the responses of the '
              'simulator to unit impulses (largest difference from the simulator <<hop_err>> m).'),
        ('p', '**Remark 1 (explicit guidance and precise data).** Take one observed value with $\\partial D_\\theta / \\partial a '
              '\\approx 1$. A guidance step with weight $\\omega$ multiplies its residual by $1 - 2\\omega$, so it is stable '
              'only for $\\omega < 1$, and the remaining residual after the guided steps is $\\prod_i (1 - 2\\omega_i)$. The '
              'noise level $\\sigma_h$ does not appear: the guidance cannot tell a 2 cm sensor from a 20 cm one, and the '
              'spread it leaves is set by the weights and the schedule, not by the data. The exact posterior instead pulls '
              'by the fraction $s^2 / (s^2 + \\sigma_h^2)$ of the prior variance $s^2$. With 2 cm heads that fraction is '
              'close to one for many directions at once, which explicit steps with $\\omega_i = \\sigma_i \\zeta \\to 0$ do '
              'not reach. A further effect: a boundary function is stored as <<nx>> copies along $x$, so the gradient '
              'with respect to one copy is 1/<<nx>> of the gradient with respect to the function; the step that is '
              'right in $L^2(0, T)$ is <<nx>> times larger. With that step the guidance diverged in <<d_geo_div>> of the '
              '<<d_geo_n>> settings tried and was worse in the others.'),
        ('p', 'The numbers in Section 5 confirm this. RINDËRTIMI-GO therefore lets FunDPS do what it does well, a non-'
              'Gaussian prior of all the boundary conditions conditioned on the rain, and brings in the heads and the tide '
              'gauge with the exact solver.'),

        ('h2', '4.7 The ensemble update with the exact solver'),
        ('p', 'Each member $x_i = (h_{0,i}, \\eta_i, q_{L,i}, r_i)$ of the FunDPS ensemble of scenario A is updated with '
              'the perturbed-observation ensemble smoother (Burgers, van Leeuwen & Evensen, 1998; Emerick & Reynolds, '
              '2013), where the observation operator is the exact solver [[hop]] for heads and the identity for the tide '
              'gauge:'),
        ('eq', 'es', ('y_i = H x_i + c, \\quad \\hat K = \\hat C_{xy} \\left(\\hat C_{yy} + R\\right)^{-1},',
                      'x_i^{a} = x_i + \\hat K \\left(u + \\varepsilon_i - y_i\\right), \\quad \\varepsilon_i \\sim \\mathcal{N}(0, R), \\quad h_i^{a} = \\mathcal{S}(x_i^{a})')),
        ('p', 'with $\\hat C$ the ensemble covariances. The head of every updated member is simulated again, so every member '
              'is a solution of the flow equation [[flow]]. The coupled model of our methodology uses the same update '
              '(ES-MDA) for heads and chloride, so this step is the bridge between FunDPS and the methodology.'),
        ('p', '**Proposition 2 (the update is exact in the linear-Gaussian limit).** If the members are an independent '
              'sample of $\\mathcal{N}(m, P)$ and $u = Hx + c + \\varepsilon$ with $\\varepsilon \\sim \\mathcal{N}(0, R)$, '
              'then as the ensemble grows the updated members are a sample of the exact posterior '
              '$\\mathcal{N}(m + K(u - Hm - c),\\ (I - KH)P)$ with $K = PH^\\top (HPH^\\top + R)^{-1}$. *Proof:* '
              '$\\hat K \\to K$ by the law of large numbers; for fixed $K$, $x^a$ is affine in $(x_i, \\varepsilon_i)$, '
              'Gaussian with that mean and covariance $(I - KH)P(I - KH)^\\top + KRK^\\top = (I - KH)P$. Here the prior '
              'given the rain is not Gaussian (it mixes over $\\kappa$) and the ensemble is finite, so the update is an '
              'approximation; the exact posterior of Section 4.8 measures it.'),

        ('h2', '4.8 The exact posterior as the benchmark'),
        ('p', 'The test bed is built so that the posterior can be computed exactly. Let $z$ be the Gaussian vector with '
              '<<nz>> components: the departures of $\\eta$ and $q_L$ and their means, the error $e$ and the initial field.'),
        ('p', '**Proposition 3 (exact posterior).** Given the rain and $\\kappa$, the head is affine in $z$ and the '
              'observations are linear with Gaussian noise, $u = H z + \\kappa\\, g + c_0 + \\varepsilon$. Then'),
        ('eq', 'exact', ('p(z \\mid u, \\kappa) = \\mathcal{N}\\left(m_0 + \\kappa\\, m_1,\\ \\Sigma_u\\right), \\quad \\Sigma_u = \\Sigma - K H \\Sigma, \\quad K = \\Sigma H^\\top C_u^{-1},',
                         '\\log p(\\kappa \\mid u) = \\log p(\\kappa) + \\kappa\\, g^\\top C_u^{-1} r_0 - \\tfrac{1}{2}\\, \\kappa^2\\, g^\\top C_u^{-1} g + \\text{const.}')),
        ('p', 'with $C_u = H \\Sigma H^\\top + R$, $r_0 = u - H\\mu - c_0$, $m_0 = \\mu + K r_0$ and $m_1 = -K g$. The posterior '
              'is a one-dimensional mixture over $\\kappa$ with a common covariance. *Proof:* for given $\\kappa$, Gaussian '
              'conditioning gives the first part and the covariance does not depend on $\\kappa$; the density '
              '$p(u \\mid \\kappa) = \\mathcal{N}(u;\\ H\\mu + c_0 + \\kappa g,\\ C_u)$ gives a log that is quadratic in '
              '$\\kappa$. The mixture is computed on 241 values of $\\kappa$ and gives 2,000 exact samples per case.'),

        ('h2', '4.9 What rain alone gives, and the scale'),
        ('p', '**Proposition 4 (rain only).** In scenario A, $p(z, \\kappa \\mid f) = p(z)\\, p(\\kappa)$. The sea level and '
              'the inflow keep their prior, and the recharge has'),
        ('eq', 'rainonly', ('\\text{E}[r(t) \\mid f] = \\text{E}[\\kappa]\\, f(t),',
                            '\\text{Cov}\\left[r(t), r(s) \\mid f\\right] = \\text{Var}(\\kappa)\\, f(t) f(s) + k_e(t - s)')),
        ('p', 'Rain fixes the timing and the shape of recharge, not its size: the relative uncertainty at its peaks stays at '
              'the coefficient of variation of $\\kappa$, <<cv_k>>, however good the method. *Proof:* in the prior the rain '
              'is independent of $(z, \\kappa)$, and $r$ is a function of $(\\kappa, e, f)$.'),
        ('p', '**Proposition 5 (scale; Proposition 6 of SHIU-GO).** If $h$ solves [[flow]] with $(T, S, q_L, r, Q)$, it also '
              'solves the problem with $(cT, cS, c\\,q_L, c\\,r, c\\,Q)$ for every $c > 0$, with the same $\\eta$ and $h_0$. '
              'Heads therefore do not separate the size of recharge from the transmissivity unless a flux or $T$ is known. '
              'In the test $T$ and $Q$ are known, so heads identify $\\kappa$. At Fushë-Kuqe the scale is fixed by the K '
              'values of the workbook and, once available, by the pumping records. *Proof:* multiply [[flow]] by $c$.'),
    ]


def result_blocks():
    cell = lambda m, c: f'<<{m}_{c}_ratio>> · <<{m}_{c}_sr>> · <<{m}_{c}_cf>>'
    rows = []
    for m, lab in (('fundps_A', 'A: FunDPS with the rain'), ('hybrid_B', 'B: RINDËRTIMI-GO'), ('pure_B', 'B: plain FunDPS'),
                   ('hybrid_C', 'C: RINDËRTIMI-GO'), ('pure_C', 'C: plain FunDPS')):
        rows.append([lab] + [cell(m, c) for c in ('eta', 'qL', 'r', 'h0')] + [f'<<{m}_k_ef>> (<<{m}_k_ee>>)'])
    exact = [['Exact posterior sd, A / B / C'] + [f'<<{c}_sde_A>> / <<{c}_sde_B>> / <<{c}_sde_C>>' for c in ('eta', 'qL', 'r', 'h0')]
             + ['–']]
    return [
        ('h', '5. Numerical test'),
        ('h2', '5.1 Set-up'),
        ('p', 'The prior was sampled <<ntrain>> times. The operator was trained on a CPU for <<steps>> steps with batches of '
              '<<batch>>, with Adam, warm-up, cosine decay and an exponential moving average of the weights (<<train_min>> '
              'minutes; final loss <<loss_end>>). The test uses <<n_case>> truths drawn from the prior. For each truth the '
              'three scenarios share the rain and the truth, and each scenario has its own exact posterior with 2,000 '
              'samples. FunDPS gives <<ns_a>> members for scenario A in about <<fundps_A_sec>> s on four CPU cores; the '
              'ensemble update then takes less than a second. Plain FunDPS, with every observation in its guidance, gives '
              '<<ns_pure>> members per scenario. The guidance settings were chosen on two validation cases, apart from '
              'the test: <<rain_loss>> loss with $w_f$ = <<rain_w>> for the rain, and <<pure_loss>> loss with $w_f$ = '
              '<<pure_wP>>, $w_h$ = $w_\\eta$ = <<pure_wH>> for plain FunDPS.'),
        ('p', 'Every method is scored against the exact posterior of its scenario, for each boundary condition: the error '
              'of the posterior mean against the truth divided by the error of the exact posterior mean (1 is as good as '
              'possible), the posterior spread divided by the exact spread (1 is calibrated), and the share of the truth '
              'inside the 90% interval. Table {{tab_res}} gives the medians over the test cases.'),
        ('cap', 'Table {{tab_res}}. Medians over <<n_case>> test cases. Each cell gives the error ratio · spread ratio · '
                'coverage of the 90% interval for one boundary condition; the last column gives the absolute error of the '
                'recharge coefficient $\\kappa$, with that of the exact posterior in brackets. The last row gives the '
                'exact posterior standard deviation in cm, m²/d, mm/d and cm.'),
        ('table', ['Scenario and method', 'Sea level', 'Inflow', 'Recharge', 'Initial head', 'Error of κ'],
         rows + exact, [3.6, 2.7, 2.7, 2.7, 2.7, 2.6], 9.0),
        ('h2', '5.2 Rain only'),
        ('p', 'With the filtered rain alone, FunDPS reproduces the posterior that Proposition 4 describes. Its errors are '
              '<<fundps_A_eta_ratio>>, <<fundps_A_qL_ratio>>, <<fundps_A_r_ratio>> and <<fundps_A_h0_ratio>> times those of '
              'the exact posterior for sea level, inflow, recharge and initial head, and its spreads are '
              '<<fundps_A_eta_sr>>, <<fundps_A_qL_sr>>, <<fundps_A_r_sr>> and <<fundps_A_h0_sr>> times the exact ones. The '
              'sea level and the inflow keep their prior spread, as they must. Recharge follows the timing of the rain '
              'while its size stays as uncertain as $\\kappa$ allows: the error of $\\kappa$ is <<fundps_A_k_ef>>, '
              'against <<fundps_A_k_ee>> for the exact posterior. The guidance holds the filtered rain to <<fundps_A_frms>> '
              'mm/d, <<f_rel>> of its spread.'),
        ('h2', '5.3 Heads and tide gauge'),
        ('p', 'Plain FunDPS does not take in the heads. With every observation in its guidance and the solver in the head '
              'operator, its spreads in scenario B are <<pure_B_qL_sr>> times the exact spread for the inflow and '
              '<<pure_B_r_sr>> times for recharge, and its errors <<pure_B_qL_ratio>> and <<pure_B_r_ratio>> times the exact '
              'ones. The heads simulated from its boundary conditions miss the data by <<pure_B_fit_cm>> cm against a noise '
              'of <<sig_h>> cm. It diverged in <<pure_B_ndiv>> of the <<n_case>> cases of B and in <<pure_C_ndiv>> of C, '
              'and the medians are over the others. This is Remark 1 in numbers.'),
        ('p', 'The ensemble update with the exact solver does take in the heads. In scenario B the heads of the updated '
              'members fit the data to <<hybrid_B_fit_cm>> cm, the noise level, and the errors fall to '
              '<<hybrid_B_eta_ratio>>, <<hybrid_B_qL_ratio>>, <<hybrid_B_r_ratio>> and <<hybrid_B_h0_ratio>> times the '
              'exact ones. The recharge coefficient is found to within <<hybrid_B_k_ef>> (exact posterior: '
              '<<hybrid_B_k_ee>>; plain FunDPS: <<pure_B_k_ef>>). The update is not exact. With <<ns_a>> members it is too '
              'narrow in the sea level (spread <<hybrid_B_eta_sr>>) and in $\\kappa$ (spread <<hybrid_B_k_sf>> against '
              '<<hybrid_B_k_se>>). It is too wide in recharge and the initial head (<<hybrid_B_r_sr>> and '
              '<<hybrid_B_h0_sr>>), where the heads say little about short changes and the ensemble keeps directions that '
              'the exact posterior removes.'),
        ('p', 'With the tide gauge (C) the exact posterior narrows the sea level to <<eta_sde_C>> cm, and the update '
              'follows it less closely: errors <<hybrid_C_eta_ratio>> to <<hybrid_C_h0_ratio>> times the exact ones, and '
              'a coverage of <<hybrid_C_eta_cf>> for the sea level. Plain FunDPS reads the tide gauge directly in its '
              'guidance and does better on the sea level alone (error <<pure_C_eta_ratio>> times the exact one), with an '
              'interval twice too wide. For the other three conditions the update is better by a factor of '
              '<<C_gain_min>> to <<C_gain_max>>.'),
        ('h2', '5.4 What the first training showed'),
        ('p', 'A first training put the weekly rain of the window in the fifth channel. On the two validation cases its '
              'recharge error with the rain alone was <<abl1_r>> times the exact one and its initial-head error <<abl1_h0>> '
              'times; with the filtered rain these are <<abl2_r>> and <<abl2_h0>>. The same training showed why heads must '
              'not be read from the head channel. Guidance on that channel fitted the piezometers to <<d_fit_ch>> cm, while '
              'the heads simulated from the sampled boundary conditions missed them by <<d_fit_ch_sim>> cm. Passing the '
              'boundary conditions through the solver brought that miss down to <<d_fit_ph_best>> cm at best, still ten '
              'times the noise, with inflow spreads <<d_ph_sd_q_min>> to <<d_ph_sd_q_max>> times the exact one.'),
        ('h2', '5.5 Physics check, cost and the value of each data source'),
        ('p', 'The head channel of FunDPS differs from the heads simulated from its own boundary and initial conditions by '
              '<<fundps_A_cons>> cm (median). The boundary and initial conditions are therefore the product, and every head '
              'that is passed on is simulated again. FunDPS needs about <<fundps_A_sec>> s for <<ns_a>> members on four CPU '
              'cores; the update takes less than a second and the exact posterior a few seconds.'),
        ('p', 'Figure {{ladder}} shows what each data source buys. Rain alone narrows recharge to <<r_lad_A>> of its prior '
              'spread, through the timing. Four loggers narrow the inflow to <<qL_lad_B>>, recharge to <<r_lad_B>> and the '
              'initial head to <<h0_lad_B>>, and the sea level to <<eta_lad_B>>; the tide gauge then brings the sea level to '
              '<<eta_lad_C>>.'),
        ('img', 'results', 17.0),
        ('cap', 'Figure {{results}}. The first test case in the three scenarios. Grey: exact posterior, 90%. Coloured lines: '
                'RINDËRTIMI-GO, 90% band and median (FunDPS with the rain in A; then the ensemble update with the solver in '
                'B and C). Light dash-dot lines: plain FunDPS with every observation in its guidance. Dashed: truth; dots: '
                'tide-gauge readings in C. The initial head is shown as its departure from the exact posterior mean.'),
        ('img', 'ladder', 17.0),
        ('cap', 'Figure {{ladder}}. (a) Posterior spread of each boundary condition relative to its prior spread, exact '
                '(solid) and RINDËRTIMI-GO (hatched), for scenarios A, B and C. (b) Coverage of the 90% interval: exact '
                '(open), RINDËRTIMI-GO (filled) and plain FunDPS (crosses, B and C).'),
    ]


def application_blocks():
    return [
        ('h', '6. Application to Fushë-Kuqe'),
        ('p', 'The route to Fushë-Kuqe follows the same steps, with the geometry and data of Figure {{fk_bc}}. In two '
              'dimensions the flow equation [[flow]] becomes'),
        ('eq', 'flow2', ('S\\, \\frac{\\partial h}{\\partial t} = \\nabla \\cdot (T \\nabla h) + r(\\mathbf{x}, t) - \\sum_j Q_j(t)\\, \\delta(\\mathbf{x} - \\mathbf{x}_j) \\quad \\text{in } \\Omega,',
                         '\\phi = 0 \\text{ on } \\Gamma_D, \\quad T\\, \\partial_n h = q_E(t) \\text{ on } \\Gamma_E, \\quad T\\, \\partial_n h = q_S(t) \\text{ on } \\Gamma_S, \\quad T\\, \\partial_n h = 0 \\text{ on } \\Gamma_0')),
        ('p', 'with $\\phi$ the potential of Strack (1976), referred to the sea level $\\eta(t)$ on the sea contact '
              '$\\Gamma_D$, and recharge $r(\\mathbf{x}, t) = \\kappa(\\mathbf{x}) f_{\\tau(\\mathbf{x})}(t) + e(\\mathbf{x}, t)$. '
              'The steps are:'),
        ('b', '**Rain.** The daily series is taken for the cells over the sector, about two to three 0.1° cells of E-OBS or '
              'ERA5-Land, and ==the series of the IGJEO station, if it is provided==. The bias of the grid is corrected '
              'against the station, and missing days are filled with the conditional expectation from the rain law of '
              'SHIU-GO. The quality of E-OBS depends on the density of stations; ==for Albania it must be checked before '
              'use==.'),
        ('b', '**Simulator and prior.** The calibrated areal model becomes transient with [[flow2]]. $T$ comes from the '
              'calibration ensemble with the K values of the workbook; $\\tau(\\mathbf{x})$ is tied to the cover thickness '
              'and $\\kappa(\\mathbf{x})$ to the soil groups. The sea level takes the statistics of ==the tide gauge or '
              'sea-level product to be chosen==, and $q_E$, $q_S$ take Gaussian random fields around zero, which contain '
              'the no-flow boundary of the calibrated model.'),
        ('b', '**Joint function.** On the 0.25 km grid of the model, with weekly steps: $h(\\mathbf{x}, t)$, $\\eta(t)$, '
              '$q_E(s, t)$ and $q_S(s, t)$ along the margins, $r(\\mathbf{x}, t)$ and the filtered rain of the cells. The '
              'boundary channels remain functions of time, or of time and of the position $s$ along the margin, with '
              'the noise and projection of Proposition 1.'),
        ('b', '**Sampling.** Today only scenario A is possible: an ensemble of boundary conditions consistent with the '
              'prior, the rain and the static data. Proposition 4 says what it cannot give. With the loggers P3, A3, A13 '
              'and the new piezometer V2 comes scenario B, through the ensemble update with the solver; with a tide '
              'gauge, scenario C.'),
        ('b', '**Coupled simulation.** Every sample of the boundary and initial conditions goes into the coupled model: '
              'density-driven flow, salt and interface. The ensemble of simulations is the input to the questions of '
              'the methodology, such as the safe pumping window. There the head and chloride data enter with the ES-MDA '
              'of the coupled model, which is the nonlinear form of the update [[es]].'),
    ]


def closing_blocks():
    return [
        ('h', '7. What is new (the RINDËRTIMI-GO innovation)'),
        ('b', '**All boundary and initial conditions as one function, with a learned physical prior.** Sea level, inland '
              'inflow, recharge, the initial head and the filtered rain are one joint function with the head. A denoising '
              'neural operator learns its prior from the simulator, which carries the static data of the workbook, so no '
              'field time series is needed for training.'),
        ('b', '**Boundary channels kept in their own function space.** The boundary conditions are functions of time; '
              'their noise is a GRF in time only and the denoiser ends with the projection $\\Pi$. Proposition 1 shows '
              'that this never increases the error of the denoiser.'),
        ('b', '**Rain enters through the operator of the unsaturated zone.** The fifth channel is $f = k_\\tau * P$ from '
              'the whole rain record, not the raw rain of the window. It carries the antecedent rain and gives the network '
              'a smooth input. On the validation cases it cut the recharge error with the rain alone from '
              '<<abl1_r>> to <<abl2_r>> times the exact one.'),
        ('b', '**FunDPS for the rain, the exact solver for the heads.** Remark 1 shows why explicit guidance cannot take '
              'in precise heads: its pull does not depend on the noise level and is unstable when it is strong. '
              'RINDËRTIMI-GO keeps FunDPS for the non-Gaussian prior conditioned on the rain and brings in the heads and '
              'the tide gauge with an ensemble update through the exact solver (Proposition 2). This is the same update '
              'as the ES-MDA of the coupled model, so FunDPS plugs into the methodology without a new data-assimilation '
              'layer. In the test it brought the heads from <<pure_B_fit_cm>> cm to <<hybrid_B_fit_cm>> cm of the data '
              'and the inflow error from <<pure_B_qL_ratio>> to <<hybrid_B_qL_ratio>> times the exact one.'),
        ('b', '**An exact benchmark for diffusion posterior sampling in hydrogeology.** The test bed has an exact posterior '
              '(Proposition 3), so bias and calibration are measured against the true posterior, not only the error '
              'against one truth as in the FunDPS experiments.'),
        ('b', '**What each data source buys.** Propositions 4 and 5 say what rain and the workbook can and cannot give; '
              'Figure {{ladder}} measures how far each boundary condition narrows from A to B to C.'),
        ('b', '**A path for Fushë-Kuqe.** The boundary conditions are mapped on the real geometry, with their data, the '
              'scale of the rain cells and the loggers chosen in SHIU-GO (Figure {{fk_bc}}).'),
        ('b', '**Not claimed as new:** FunDPS and its theory, Tweedie\'s formula in Banach spaces, the EDM loss and sampler, '
              'the Fourier neural operator, the ensemble smoother and ES-MDA, the rain law, the Erlang kernel and the '
              'Strack model. What is new is their assembly for the boundary conditions of a coastal aquifer, the two '
              'structural choices (time-only channels with $\\Pi$, filtered rain), the hybrid with the exact solver and '
              'the exact test. The novelty check rests on the material read; it should be repeated in the bibliographic '
              'databases before publication.'),
        ('h', '8. Limitations'),
        ('b', 'The test bed is a linear coastal section in one dimension. Fushë-Kuqe needs two dimensions, density and an '
              'interface, where the posterior is no longer exact and the update needs ES-MDA iterations.'),
        ('b', 'The neural operator is small (<<nparam>> parameters) and was trained on a CPU for <<train_min>> minutes. '
              'With the rain alone it is close to the exact posterior (errors within <<A_err_dev>>, spreads within '
              '<<A_sd_dev>>), but its head channel stays <<fundps_A_cons>> cm from the solver.'),
        ('b', 'The guidance settings were chosen on two validation cases, and the ensemble has <<ns_a>> members. '
              'With these members the update leaves errors <<hyb_min>> to <<hyb_max>> times the exact ones in scenario B and a '
              'spread of $\\kappa$ <<k_narrow>> times too narrow. Larger ensembles, localisation or iterations (ES-MDA) are '
              'the next step.'),
        ('b', 'The filtered rain assumes that the delay $\\tau$ of the unsaturated zone is known. At Fushë-Kuqe it comes '
              'from the cover with an uncertainty that the prior must carry, for example through several delays.'),
        ('b', 'No rain series has been downloaded yet: the download services were blocked in this environment, so the '
              'application in Section 6 is a plan. The sea-level source and the pumping records are still missing.'),
    ]
