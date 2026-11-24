r"""Text of the PERTEJ-GO theory note (English). blocks(R) returns the block list; every number comes from
res/pertej.json. Conventions: $inline math$, **bold**, *italic*, [text](url) hyperlink, [[key]] equation number,
{{key}} figure or table number, <<key>> a value from the results (filled in by fill())."""
import math

REFS = [
    dict(key='1', text='Engquist, B., & Majda, A. (1977). Absorbing boundary conditions for the numerical simulation of '
                       'waves. Mathematics of Computation 31(139), 629–651.',
         url='https://doi.org/10.1090/S0025-5718-1977-0436612-4'),
    dict(key='2', text='Hagstrom, T. (1999). Radiation boundary conditions for the numerical simulation of waves. Acta '
                       'Numerica 8, 47–106.', url='https://doi.org/10.1017/S0962492900002890'),
    dict(key='3', text='Alpert, B., Greengard, L., & Hagstrom, T. (2000). Rapid evaluation of nonreflecting boundary '
                       'kernels for time-domain wave propagation. SIAM Journal on Numerical Analysis 37(4), 1138–1164.',
         url='https://doi.org/10.1137/S0036142998336916'),
    dict(key='4', text='Jiang, S., & Greengard, L. (2004). Fast evaluation of nonreflecting boundary conditions for the '
                       'Schrödinger equation in one dimension. Computers & Mathematics with Applications 47(6–7), '
                       '955–966.', url='https://doi.org/10.1016/S0898-1221(04)90079-X'),
    dict(key='5', text='Givoli, D. (2004). High-order local non-reflecting boundary conditions: a review. Wave Motion '
                       '39(4), 319–326.', url='https://doi.org/10.1016/j.wavemoti.2003.12.004'),
    dict(key='6', text='Schilling, R. L., Song, R., & Vondraček, Z. (2012). Bernstein Functions: Theory and Applications '
                       '(2nd ed.). De Gruyter, Berlin.', url='https://doi.org/10.1515/9783110269338'),
    dict(key='7', text='Willems, J. C. (1972). Dissipative dynamical systems part I: General theory. Archive for Rational '
                       'Mechanics and Analysis 45(5), 321–351.', url='https://doi.org/10.1007/BF00276493'),
    dict(key='8', text='Gustavsen, B., & Semlyen, A. (1999). Rational approximation of frequency domain responses by '
                       'vector fitting. IEEE Transactions on Power Delivery 14(3), 1052–1061.',
         url='https://doi.org/10.1109/61.772353'),
    dict(key='9', text='Gustavsen, B., & Semlyen, A. (2001). Enforcing passivity for admittance matrices approximated by '
                       'rational functions. IEEE Transactions on Power Systems 16(1), 97–104.',
         url='https://doi.org/10.1109/59.910786'),
    dict(key='10', text='Trefethen, L. N., & Weideman, J. A. C. (2014). The exponentially convergent trapezoidal rule. '
                        'SIAM Review 56(3), 385–458.', url='https://doi.org/10.1137/130932132'),
    dict(key='11', text='Eldén, L., Berntsson, F., & Regińska, T. (2000). Wavelet and Fourier methods for solving the '
                        'sideways heat equation. SIAM Journal on Scientific Computing 21(6), 2187–2205.',
         url='https://doi.org/10.1137/S1064827597331394'),
    dict(key='12', text='Åström, K. J., & Eykhoff, P. (1971). System identification—A survey. Automatica 7(2), 123–162.',
         url='https://doi.org/10.1016/0005-1098(71)90059-8'),
    dict(key='13', text='Arridge, S., Maass, P., Öktem, O., & Schönlieb, C.-B. (2019). Solving inverse problems using '
                        'data-driven models. Acta Numerica 28, 1–174.', url='https://doi.org/10.1017/S0962492919000059'),
    dict(key='14', text='Haggerty, R., & Gorelick, S. M. (1995). Multiple-rate mass transfer for modeling diffusion and '
                        'surface reactions in media with pore-scale heterogeneity. Water Resources Research 31(10), '
                        '2383–2400.', url='https://doi.org/10.1029/95WR10583'),
    dict(key='15', text='von Asmuth, J. R., Bierkens, M. F. P., & Maas, K. (2002). Transfer function-noise modeling in '
                        'continuous time using predefined impulse response functions. Water Resources Research 38(12), '
                        '1287.', url='https://doi.org/10.1029/2001WR001136'),
    dict(key='16', text='Bakker, M., & Schaars, F. (2019). Solving groundwater flow problems with time series analysis: '
                        'you may not even need another model. Groundwater 57(6), 826–833.',
         url='https://doi.org/10.1111/gwat.12927'),
    dict(key='17', text='Langevin, C. D., Hughes, J. D., Banta, E. R., Niswonger, R. G., Panday, S., & Provost, A. M. '
                        '(2017). Documentation for the MODFLOW 6 Groundwater Flow Model. U.S. Geological Survey '
                        'Techniques and Methods 6-A55.', url='https://doi.org/10.3133/tm6A55'),
    dict(key='18', text='Hughes, J. D., Leake, S. A., Galloway, D. L., & White, J. T. (2022). Documentation for the '
                        'Skeletal Storage, Compaction, and Subsidence (CSUB) Package of MODFLOW 6. U.S. Geological '
                        'Survey Techniques and Methods 6-A62.', url='https://doi.org/10.3133/tm6A62'),
    dict(key='19', text='Werner, A. D., & Simmons, C. T. (2009). Impact of sea-level rise on sea water intrusion in '
                        'coastal aquifers. Ground Water 47(2), 197–204.',
         url='https://doi.org/10.1111/j.1745-6584.2008.00535.x'),
    dict(key='20', text='Michael, H. A., Russoniello, C. J., & Byron, L. A. (2013). Global assessment of vulnerability to '
                        'sea-level rise in topography-limited and recharge-limited coastal groundwater systems. Water '
                        'Resources Research 49(4), 2228–2240.', url='https://doi.org/10.1002/wrcr.20213'),
    dict(key='21', text='van der Kamp, G., & Gale, J. E. (1983). Theory of earth tide and barometric effects in porous '
                        'formations with compressible grains. Water Resources Research 19(2), 538–544.',
         url='https://doi.org/10.1029/WR019i002p00538'),
    dict(key='D1', text='Zeqiraj, D. (2026). Assembling the equations of a coastal aquifer, with the placement of recharge '
                        'and pumping wells as the final goal (MONTIMI-GO). Technical note, October 2026; '
                        'docs/research_notes/Assembled_System_Equations_Placing_Recharge_and_Pumping_Wells.docx in this '
                        'repository.', url=None),
    dict(key='D2', text='Zeqiraj, D. (2026). Inputs, dispersion and boundary conditions from rain alone (GARANCIA-GO, '
                        'review I). docs/literature/ in this repository.', url=None),
    dict(key='D3', text='Zeqiraj, D. (2026). Reconstructing all boundary conditions of a coastal aquifer from rain and the '
                        'Fushë-Kuqe data (RINDËRTIMI-GO). docs/research_notes/RINDERTIMI-GO_Boundary_Conditions_FunDPS.docx '
                        'in this repository.', url=None),
]


def all_refs():
    return REFS


def pc(x, d=1):
    return f'{100 * x:.{d}f}%'


def mm(x, d=1):
    return f'{1000 * x:.{d}f} mm'


def sci(x, d=1):
    """x as a x 10^b, for the text."""
    e = int(math.floor(math.log10(abs(x))))
    m = x / 10 ** e
    sup = str(e).replace('-', '⁻').translate(str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹'))
    return f'{m:.{d}f}×10{sup}'


def values(R):
    S, N1, N2, N3, N4, N5, N6 = R['setup'], R['N1'], R['N2'], R['N3'], R['N4'], R['N5'], R['N6']
    V = {}
    cs = N1['cases']
    V['nc'] = str(N1['n_compartments'])
    V['ex_bc'] = sci(N1['exact_err']['bc'])
    V['ex_pz'] = sci(N1['exact_err']['piez'])
    V['slow'] = f"{N1['slowest_years']:.1f}"
    V['range_bc'] = f"{N1['head_range_bc']:.2f}"
    for k in ('pertej_M3', 'pertej_M6', 'pertej_M12', 'no_flow', 'fixed_head', 'ghb_calibrated'):
        V[k + '_bc'] = mm(cs[k]['rms_bc'], 2 if cs[k]['rms_bc'] < 1e-3 else 1)
        V[k + '_pz'] = mm(cs[k]['rms_piez'], 2 if cs[k]['rms_piez'] < 1e-3 else 1)
        V[k + '_mx'] = mm(cs[k]['max_bc'], 2 if cs[k]['max_bc'] < 2e-3 else 1)
    for k in ('pertej_M3', 'pertej_M6', 'pertej_M12'):
        V[k + '_zmed'] = pc(cs[k]['z_err_med'], 2 if cs[k]['z_err_med'] < 0.01 else 1)
        V[k + '_zmax'] = pc(cs[k]['z_err_max'], 2 if cs[k]['z_err_max'] < 0.01 else 1)
    V['ghb_C'] = f"{N1['ghb_C']:.3f}"
    V['ghb_Cc'] = f"{N1['ghb_C_over_c']:.3f}"
    V['ratio_m6'] = f"{cs['ghb_calibrated']['rms_bc'] / cs['pertej_M6']['rms_bc']:.0f}"
    V['ratio_m12'] = f"{cs['ghb_calibrated']['rms_bc'] / cs['pertej_M12']['rms_bc']:.0f}"
    V['C_exact'] = sci(abs(N1['C_exact']))
    for i, r in enumerate(N2['rows']):
        V[f'n2_{i}_mp'] = str(r['M_pred']); V[f'n2_{i}_e'] = pc(r['err_at_M_pred'], 2)
        V[f'n2_{i}_mm'] = str(r['M_min_same_window'])
    f_err = [r['err_at_M_pred'] / r['eps'] for r in N2['rows']]
    V['n2_f_lo'], V['n2_f_hi'] = f'{min(f_err):.1f}', f'{max(f_err):.1f}'
    more = [r['M_min_same_window'] / r['M_pred'] - 1 for r in N2['rows']]
    V['n2_more_lo'], V['n2_more_hi'] = f'{100 * min(more):.0f}', f'{100 * max(more):.0f}'
    p = N3['passive']
    V['E0'], V['Eend'] = f"{p['E0']:.1f}", f"{p['E_end']:.4f}"
    a2 = N3['negative_0.2']; a02 = N3['negative_0.02']
    V['g02'] = sci(a2['E_end_over_E0'])
    V['r02'] = f"{a2['growth_rate_per_day']:.4f}"
    V['r02_ie'] = f"{a2['predicted_rate_implicit_euler']:.4f}"
    V['r02_sd'] = f"{a2['predicted_rate_semidiscrete']:.4f}"
    V['r02_ct'] = f"{a2['predicted_rate']:.4f}"
    V['r02_match'] = sci(abs(a2['growth_rate_per_day'] - a2['predicted_rate_implicit_euler']) /
                         a2['growth_rate_per_day'], 0)
    V['g002'] = sci(a02['E_end_over_E0'])
    V['th_c'] = f"{a2['threshold_alpha']:.3f}"
    V['th_d'] = f"{a2['threshold_alpha_discrete']:.4f}"
    for r in N3['length_test']:
        L = f"{r['L_km']:g}"
        V[f'lt_{L}_a'] = f"{r['alpha_threshold']:.4f}"
        V[f'lt_{L}_r'] = sci(r['rate_per_day'], 2)
        tt = math.log(2) / abs(r['rate_per_day'])
        V[f'lt_{L}_t'] = (f'doubles in {tt / 365.25:.1f} years' if r['rate_per_day'] > 0 else
                          (f'halves in {tt:.0f} days' if tt < 365.25 else f'halves in {tt / 365.25:.1f} years'))
    c4 = N4['cases']
    for k, v in c4.items():
        for b in ('low', 'mid', 'high'):
            V[f'{k}_{b}'] = pc(v['band_err'][b], 1 if v['band_err'][b] < 1 else 0)
        V[f'{k}_pred'] = mm(v['pred_rms_bc'])
    for k in ('psi_in_band', 'psi_outside_band'):
        for b in ('low', 'mid', 'high'):
            V[f'{k}_{b}'] = pc(N4[k]['band_err'][b], 1 if N4[k]['band_err'][b] < 1 else 0)
    pr = N4['prediction_reference']
    V['pr_ex'] = sci(pr['exact'] * 1000) + ' mm'
    for k in ('fixed_head', 'no_flow', 'ghb_calibrated'):
        V['pr_' + k] = mm(pr[k], 0)
    V['pr_dh'] = f"{pr['head_change_bc']:.2f}"
    V['pr_ratio'] = f"{pr['ghb_calibrated'] / c4['broadband_2mm']['pred_rms_bc']:.0f}"
    for name, pi in N5['priors'].items():
        V[f'{name}_pct'] = f"{100 * pi['truth_percentile']:.0f}"
        V[f'{name}_d'] = f"{pi['truth_mahalanobis']:.1f}"
        V[f'{name}_p50'] = f"{pi['ens_maha_p50']:.1f}"
        V[f'{name}_p99'] = f"{pi['ens_maha_p99']:.1f}"
    for k, v in N5['cases'].items():
        for nm in ('near', 'shifted'):
            for b in ('low', 'mid', 'high'):
                V[f'n5_{k}_{nm}_{b}'] = pc(v[nm]['band_err'][b], 1 if v[nm]['band_err'][b] < 1 else 0)
            V[f'n5_{k}_{nm}_pred'] = mm(v[nm]['pred_rms_bc'])
            V[f'n5_{k}_{nm}_pct'] = f"{100 * v[nm]['pct_map']:.1f}"
        V[f'n5_{k}_plain_pct'] = f"{100 * v['near']['pct_plain']:.0f}"
        V[f'n5_{k}_dplain'] = f"{v['near']['maha_plain']:.0f}"
    hi_red = [v['band_err_plain']['high'] / v['near']['band_err']['high'] for v in N5['cases'].values()]
    V['n5_hi_lo'], V['n5_hi_hi'] = f'{min(hi_red):.1f}', f'{max(hi_red):.1f}'
    dpl = [v['near']['maha_plain'] for v in N5['cases'].values()]
    V['n5_dpl_lo'], V['n5_dpl_hi'] = f'{min(dpl):.0f}', f'{max(dpl):.0f}'
    pn = [100 * v['near']['pct_map'] for v in N5['cases'].values()]
    ps = [100 * v['shifted']['pct_map'] for v in N5['cases'].values()]
    V['n5_pn_lo'], V['n5_pn_hi'] = f'{min(pn):.1f}', f'{max(pn):.1f}'
    V['n5_ps_lo'], V['n5_ps_hi'] = f'{min(ps):.1f}', f'{max(ps):.1f}'
    c6 = N6['cases']
    V['q_sea'] = f"{N6['q_sea_mean_ref']:.3f}"
    for k, v in c6.items():
        V[f'n6_{k}_def'] = f"{v['deficit_m3_per_m']:.0f}"
        V[f'n6_{k}_end'] = pc(-v['dq_end_rel'], 1)
        V[f'n6_{k}_toe'] = '+' + pc(1 / (1 + v['dq_end_rel']) - 1, 1)
    V['n6_spread'] = f"{c6['fixed_head']['deficit_m3_per_m'] / c6['no_flow']['deficit_m3_per_m']:.1f}"
    V['n6_nf_ratio'] = f"{c6['full']['deficit_m3_per_m'] / c6['no_flow']['deficit_m3_per_m']:.1f}"
    V['n6_m6_err'] = pc(c6['pertej_M6']['deficit_m3_per_m'] / c6['full']['deficit_m3_per_m'] - 1, 0)
    V['n6_m12_err'] = pc(c6['pertej_M12']['deficit_m3_per_m'] / c6['full']['deficit_m3_per_m'] - 1, 1)
    V['n6_ghb_err'] = pc(c6['ghb_calibrated']['deficit_m3_per_m'] / c6['full']['deficit_m3_per_m'] - 1, 0)
    V['rt'] = f"{R['runtime_s']:.0f}"
    V['K_ens'] = str(N5['priors']['near']['K'])
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


def blocks(R):
    V = values(R)
    BL = []

    def A(b):
        BL.append(fill(b, V))

    A(('title', 'PËRTEJ-GO: the boundary condition the flow equation is missing'))
    A(('subtitle', 'A transparent, learnable boundary for the coastal-aquifer flow equation: which term to add where the '
                   'model is cut, why it must be passive, how few compartments it needs and when two piezometers can '
                   'learn it. Four propositions with proofs and six numerical checks'))
    A(('byline', 'Dulian Zeqiraj · November 2026 · theory note with numerical checks · follows the assembly note '
                 '(MONTIMI-GO) and its flow equation with two added terms'))

    # ------------------------------------------------------------------------------------------ 1
    A(('h', '1. Outcome'))
    A(('bbox', [
        r'**The question.** The flow equation of the series carries two added terms: the memory of the silt and clay '
        r'lenses and a learned closure $\Psi$ [D1, eq. (1)]. Where the model is cut inland, its boundary is a '
        r'prescribed inflow or a closed margin [D1, eq. (31)]. MODFLOW offers a fixed head, a prescribed flux or a '
        r'general-head boundary (GHB) [17]. None of them responds to pumping or to the sea the way the aquifer beyond '
        r'the cut does. Which term should be added so that the boundary is the true one, and can a neural network '
        r'learn it?',
        r'**The term (Proposition 1).** For every linear, confined exterior (heterogeneous, leaky or closed, of any '
        r'shape), the exact boundary is a conductance plus a completely monotone memory: '
        r'$\mathbf{q}\cdot\mathbf{n} = C u + \sum_m w_m (u - y_m)$ with $\partial_t y_m = \mu_m (u - y_m)$ and '
        r'$C, w_m, \mu_m \ge 0$. It is the lens memory of [D1] moved onto the boundary. Conversely, every such '
        r'network is the exact boundary of some physical exterior. With the <<nc>> compartments of the test exterior '
        r'the cut model reproduces the full aquifer to <<ex_bc>> m.',
        r'**Stable by construction (Proposition 2).** With $C, w_m \ge 0$ the model loses energy whatever the rest of '
        r'it is. A negative conductance $C = -0.02c$ that passes a 2 km test makes a 6 km model grow without bound.',
        r'**Few compartments (Proposition 3).** Compartments much slower or faster than the band of interest collapse '
        r'into a conductance and a boundary storage. Six compartments give <<pertej_M6_bc>> root-mean-square error '
        r'at the boundary cell over 20 years, against <<ghb_calibrated_bc>> for the best calibrated GHB '
        r'(<<ratio_m6>> times less); twelve give <<pertej_M12_bc>>.',
        r'**What two piezometers can learn (Proposition 4).** Two piezometers between the closure and the cut learn '
        r'the boundary apart from everything else in the model, but only on the band of periods that the pumping '
        r'excites. Varied pumping with 2 mm noise gives a <<broadband_2mm_mid>> error in the band and predicts a '
        r'drought with doubled pumping, never seen in the data, to <<broadband_2mm_pred>> '
        r'(calibrated GHB: <<pr_ghb_calibrated>>). A closure inside the band corrupts the boundary '
        r'(<<psi_in_band_mid>> error).',
        r'**Where the neural network goes.** The network belongs in the forcing (the inflow from rain), in a monotone '
        r'conductance and in a learned prior on the boundary (the "neural regularizer"), not inside the operator. '
        r'Trained on <<K_ens>> simulated exteriors, the prior cuts the error where the data are silent by '
        r'<<n5_hi_lo>>–<<n5_hi_hi>> times. It improves every prediction, even when built on a wrong geology.',
        r'**Sea-level rise (N6).** Over 20 years of a 0.5 m rise, the fresh water that does not reach the sea depends '
        r'on the inland boundary by a factor of <<n6_spread>>. The prescribed inflow of [D1] gives <<n6_no_flow_def>> '
        r'm³ per metre of coast, the truth <<n6_full_def>> and PËRTEJ-GO with six compartments <<n6_pertej_M6_def>>. '
        r'The cut of sea-level rise in [D1] was therefore a property of its boundary, as [D1] suspected, not of the '
        r'aquifer.',
    ]))
    A(('box', [
        r'**Innovation: PËRTEJ-GO** (*përtej*: beyond). A boundary condition that learns what lies beyond the model. '
        r'Its hypothesis class is exactly the class of linear passive exteriors: a conductance plus positive '
        r'first-order compartments, on a fixed logarithmic grid of time scales. Every member of the class is a '
        r'physical exterior, and every linear exterior is a member. The learned boundary therefore cannot be '
        r'unphysical, cannot destabilise the model and loses nothing in generality.',
        r'Three further steps are new for coastal aquifers. (i) A rule for where a neural network may enter (the '
        r'forcing and monotone conductances) and where it may not (the storages). (ii) An identifiability result that '
        r'separates the boundary from the closure $\Psi$ with two piezometers and makes the pumping schedule the '
        r'experiment that reveals the boundary. (iii) A prior learned from simulated geology that fills the periods '
        r'the data cannot reach.',
        r'Transparent boundaries built from sums of exponentials are classical for waves [1–5]. Passive '
        r'rational equivalents of an external network are standard in power systems [8, 9]. Positive '
        r'multi-exponential memories are standard for mass transfer [14] and for head time series [15, 16]. The step '
        r'taken here is to use the structure theorem as the hypothesis class of a learned boundary inside the flow '
        r'equation, with its passivity, identifiability and design consequences.',
    ]))

    # ------------------------------------------------------------------------------------------ 2
    A(('h', '2. The flow equation, the cut and the missing term'))
    A(('h2', '2.1 The equation with its two added terms'))
    A(('p', r'The assembly note writes the flow of the coastal aquifer as [D1, eq. (1)]'))
    A(('eq', 'flow', r'S_s\, \partial_t h_f + \nabla \cdot \mathbf{q} = \sum_{w} Q_w(t)\, \delta(\mathbf{x} - '
                     r'\mathbf{x}_w) - \int_{t_0}^{t} K_h(t - s)\, \partial_s h_f(\mathbf{x}, s)\, ds + \Psi(h_f, '
                     r'\mathbf{x}; \gamma) \quad \text{in } \Omega'))
    A(('p', r'where $S_s$ is the specific storage, $h_f$ the freshwater head, $\mathbf{q}$ the Darcy flux and $Q_w$ the '
            r'well rates. The first added term is the memory of the lenses. Its tail $K_h(r) = \sum_k s_k a_k '
            r'e^{-a_k r}$ is completely monotone and has an exact Markovian lift: one head $h_k$ per compartment, with '
            r'$\partial_t h_k = a_k (h_f - h_k)$ [D1, eq. (3)]. The second added term is the learned closure $\Psi$. '
            r'Both act inside the domain $\Omega$. This note is about the edge of $\Omega$.'))
    A(('h2', '2.2 The boundary at the cut'))
    A(('p', r'A model of a coastal aquifer ends somewhere inland, at a cut $\Gamma$ that geology does not mark. The '
            r'assembly note treats the land margins as receiving a prescribed regional inflow or as closed, '
            r'$\mathbf{q}\cdot\mathbf{n} = -q_{in}$ or $0$ [D1, eq. (31)]. Its limits section notes the consequence: '
            r'sea-level rise was cut "because the inland boundary of the section fixes the fresh inflow, so the whole '
            r'head field rises with the sea and almost no water moves" [D1, 19]. The other classical choices are a '
            r'fixed head and a general-head boundary $\mathbf{q}\cdot\mathbf{n} = C (h_f - \bar h)$ [17].'))
    A(('p', r'The aquifer beyond the cut (the exterior) acts on $\Omega$ only through the flux across $\Gamma$. If the '
            r'exterior is linear, that flux is its own forcing plus a linear, causal response to the history of the '
            r'head on $\Gamma$:'))
    A(('eq', 'dtn', r'\mathbf{q}\cdot\mathbf{n} = -q_{in}(t) + \mathcal{Z}\left[h_f - \bar h\right](t) \quad \text{on } '
                    r'\Gamma'))
    A(('p', r'where $q_{in}(t)$ is the inflow that would enter if the head on $\Gamma$ stayed at a reference $\bar h$, and '
            r'$\mathcal{Z}$ is the response of the exterior: a Dirichlet-to-Neumann map with memory. The three '
            r'classical boundaries are special cases: $\mathcal{Z} = 0$ is the prescribed inflow, '
            r'$\mathcal{Z}[u] = C u$ is the GHB and $C \to \infty$ is the fixed head. None of them has memory, and '
            r'the exterior always has it, because its storage fills and drains over its own time scales. The test '
            r'exterior of Section 9 has time scales up to <<slow>> years.'))
    A(('h2', '2.3 The term to add: PËRTEJ-GO'))
    A(('p', r'The response is written as a conductance plus a positive memory of the changes of the head:'))
    A(('eq', 'pertej', r'\mathcal{Z}_\theta[u](t) = C\, u(t) + \int_{t_0}^{t} K_\Gamma(t - s)\, \partial_s u(s)\, ds, '
                       r'\quad K_\Gamma(r) = \sum_{m=1}^{M} w_m\, e^{-\mu_m r}, \quad u = h_f - \bar h'))
    A(('p', r'with $C \ge 0$, $w_m \ge 0$ and $\mu_m > 0$. Exactly as for the lenses, the memory has a Markovian '
            r'lift, one state per compartment:'))
    A(('eq', 'lift', r'\mathcal{Z}_\theta[u] = C\, u + \sum_{m=1}^{M} w_m \left(u - y_m\right), \quad \partial_t y_m = '
                     r'\mu_m \left(u - y_m\right), \quad y_m(t_0) = y_{m,0}'))
    A(('p', r'Here $y_m$ is the head of compartment $m$, $w_m$ its conductance, $\sigma_m = w_m/\mu_m$ its storage and '
            r'$1/\mu_m$ its time scale. $C$ is the steady conductance from the cut to the fixed heads of the exterior '
            r'(rivers, lakes, a leaky base). The initial values $y_{m,0}$ are the legacy of the exterior, like '
            r'$h_k(t_0)$ for the lenses. An exterior at rest at $t_0$ has $y_{m,0} = u(t_0)$, and then [[lift]] equals the '
            r'convolution form [[pertej]]. In the assembled semi-discrete system [D1, eq. (38)] the boundary adds one term '
            r'to the head equation and $M$ states per boundary cell, of the same kind as the lens states:'))
    A(('eq', 'assembled', r'M_S\, \dot{\mathbf{h}} = \ldots - P_\Gamma^\top A_\Gamma \left[ C\, \mathbf{u} + \sum_{m} '
                          r'w_m \left(\mathbf{u} - \mathbf{y}_m\right) - \mathbf{q}_{in} \right], \quad '
                          r'\dot{\mathbf{y}}_m = \mu_m \left(\mathbf{u} - \mathbf{y}_m\right), \quad \mathbf{u} = '
                          r'P_\Gamma \mathbf{h} - \bar h'))
    A(('p', r'where the dots stand for the right side of (38) of [D1], $P_\Gamma$ picks the cells on $\Gamma$ and '
            r'$A_\Gamma$ holds their face areas. Figure {{scheme}} shows the construction. The rest of the note shows '
            r'that the form [[pertej]]–[[lift]] is exact (Section 3), stable (Section 4), cheap (Section 5) and learnable '
            r'(Section 6), and where a neural network fits into it (Section 7).'))
    A(('img', 'scheme', 17.0))
    A(('cap', r'Figure {{scheme}}. PËRTEJ-GO. The aquifer beyond the cut is replaced by a conductance $C$ to the far '
              r'field and $M$ compartments, each a conductance $w_m$ in series with a storage $\sigma_m$. Green marks '
              r'where a neural network may enter, violet what must stay fixed. The positions are those of the test '
              r'bed of Section 9; the exterior is not drawn to scale.'))

    # ------------------------------------------------------------------------------------------ 3
    A(('h', '3. Proposition 1: the exact boundary of any linear exterior'))
    A(('p', r'Let the exterior be discretised by any conservative scheme with positive storages and nonnegative '
            r'conductances: the cell-centred finite volumes of MODFLOW, or lumped finite elements. Any heterogeneity, '
            r'shape and number of layers is allowed. The exterior is linear (confined, or linearised about a '
            r'reference state). Apart from fixed heads it has no sources, since its own forcing is moved into '
            r'$q_{in}$ by linearity. $M_e$ is the diagonal matrix of storages. $A_e$ is the conductance matrix: the '
            r'connections inside the exterior, the conductances to its fixed heads, and the conductance $c > 0$ that '
            r'links its first cell to the boundary cell of $\Omega$. Write the boundary relation as '
            r'$\hat q(s) = Z(s)\, \hat u(s)$ in the Laplace variable $s$.'))
    A(('prop', 'Proposition 1 (structure and realisability).', [
        r'For zero initial deviation, the flux leaving $\Omega$ through the cut is $\hat q = Z(s)\, \hat u$ with',
        ('eq', 'Zs', r'Z(s) = C + \sum_{n=1}^{N_e} w_n\, \frac{s}{s + \mu_n}, \quad C \ge 0, \quad w_n \ge 0, \quad '
                     r'\mu_n > 0, \quad C + \sum_{n} w_n = c'),
        ('eq', 'Cw', r'C = c - c^2\, e_1^\top A_e^{-1} e_1, \quad w_n = \frac{c^2 \beta_n^2}{\mu_n}, \quad \beta_n = '
                     r'v_n^\top M_e^{-1/2} e_1, \quad M_e^{-1/2} A_e M_e^{-1/2}\, v_n = \mu_n v_n'),
        r'where $e_1$ marks the first exterior cell and $v_n$ are orthonormal eigenvectors. In time this is '
        r'[[pertej]]–[[lift]] with $N_e$ compartments. $C = 0$ if and only if the exterior has no fixed head (it is '
        r'closed). Conversely, any $C \ge 0$, $w_n \ge 0$, $\mu_n > 0$ is the exact boundary of a physical exterior: a '
        r'fixed head behind the conductance $C$ and $N$ isolated storage cells, cell $n$ holding storage '
        r'$\sigma_n = w_n/\mu_n$ behind conductance $w_n$.']))
    A(('proof', r'The exterior heads, measured from the reference, obey $M_e \dot v = -A_e v + c\, e_1 u$. The flux '
                r'leaving $\Omega$ is $q = c\,(u - e_1^\top v)$. With zero initial deviation, the Laplace transform gives '
                r'$(s M_e + A_e)\hat v = c\, e_1 \hat u$, so $Z(s) = c - c^2 e_1^\top (s M_e + A_e)^{-1} e_1$. '
                r'$A_e$ is symmetric and, because $c > 0$ and the exterior is connected, positive definite. Hence '
                r'$M_e^{-1/2} A_e M_e^{-1/2} = \sum_n \mu_n v_n v_n^\top$ with $\mu_n > 0$, and '
                r'$e_1^\top (s M_e + A_e)^{-1} e_1 = \sum_n \beta_n^2 / (s + \mu_n)$. Writing $1/(s + \mu) = 1/\mu - '
                r's/(\mu (s + \mu))$ gives [[Zs]], with $C = c - c^2 \sum_n \beta_n^2/\mu_n = c - c^2 e_1^\top A_e^{-1} '
                r'e_1$; letting $s \to \infty$ gives $C + \sum_n w_n = c$. To show $C \ge 0$, write $A_e = c\, e_1 '
                r'e_1^\top + A^\prime$ with $A^\prime$ positive semidefinite (the exterior without the link). Then '
                r'$e_1^\top A_e^{-1} e_1 = \max_v \left(2 v_1 - c v_1^2 - v^\top A^\prime v\right) \le \max_{v_1} '
                r'(2 v_1 - c v_1^2) = 1/c$. Equality needs a $v$ with $v_1 = 1/c$ and $A^\prime v = 0$. For a '
                r'connected exterior the kernel of $A^\prime$ is spanned by the constant vector if the exterior is '
                r'closed and is zero otherwise, so $C = 0$ exactly for a closed exterior. In time, $\hat y_n = '
                r'\mu_n/(s + \mu_n)\, \hat u$ is $\dot y_n = \mu_n (u - y_n)$, and $s/(s + \mu_n)\, \hat u = \hat u - '
                r'\hat y_n$, which is [[lift]]. For the converse, cell $n$ of the network obeys $\sigma_n \dot y_n = w_n '
                r'(u - y_n)$ and takes the flux $w_n (u - y_n)$, and the fixed head takes $C u$; the sum is [[lift]].'))
    A(('p', r'**The continuous exterior.** For a semi-infinite strip with transmissivity $T$ and storage coefficient '
            r'$S$, the exterior head is $\hat u\, e^{-\kappa x}$ with $\kappa = \sqrt{s S/T}$. The boundary is then of '
            r'half order, a continuum of compartments:'))
    A(('eq', 'half', r'Z(s) = \sqrt{S T}\, \sqrt{s} = \frac{\sqrt{S T}}{\pi} \int_0^\infty \frac{s}{s + \mu}\, '
                     r'\mu^{-1/2}\, d\mu, \quad \text{that is} \quad \mathbf{q}\cdot\mathbf{n} = \sqrt{S T}\; '
                     r'\partial_t^{1/2} u'))
    A(('p', r'with weight density $(\sqrt{S T}/\pi)\, \mu^{-1/2}$. Since Proposition 1 holds on every mesh, the structure '
            r'survives refinement. The limits have the form'))
    A(('eq', 'cbf', r'Z(s) = C + \int_{(0,\infty)} \frac{s}{s + \mu}\, \nu(d\mu), \quad K_\Gamma(r) = '
                    r'\int_{(0,\infty)} e^{-\mu r}\, \nu(d\mu), \quad \nu \ge 0'))
    A(('p', r'$Z$ is a complete Bernstein function and the memory kernel $K_\Gamma$ is completely monotone. By '
            r'Bernstein’s theorem, every completely monotone kernel is such a positive mixture of exponentials, and '
            r'the class is closed under pointwise limits [6]. This is the precise sense in which "a conductance plus '
            r'a completely monotone memory" is the true boundary condition of a linear exterior, and nothing else '
            r'is.'))
    A(('p', r'**Three remarks.** (i) *The third term is the first one moved to the boundary.* $K_\Gamma$ and the lens '
            r'tail $K_h$ of [D1] are the same object: completely monotone memories with exact Markovian lifts. The '
            r'lens memory is storage hidden inside $\Omega$, and the boundary memory is storage hidden beyond '
            r'$\Gamma$. The same structure describes multirate mass transfer into immobile zones [14]. (ii) *Both can '
            r'be run in an unmodified finite-volume code as extra cells.* A storage cell behind a conductance is an '
            r'ordinary cell. In principle MODFLOW 6 can hold them as hidden cells of an unstructured grid [17]; this '
            r'was not tested here. (iii) *Many boundary cells.* In two or three dimensions the cut has many cells. '
            r'Then $C$ and $w_n$ become positive semidefinite matrices ($w_n$ of rank one), and the exact operator is '
            r'nonlocal along the cut. A local (diagonal) approximation keeps the positivity but loses the coupling '
            r'along $\Gamma$.'))

    # ------------------------------------------------------------------------------------------ 4
    A(('h', '4. Proposition 2: passivity, and what it allows a neural network to do'))
    A(('p', r'Take the inland, fresh part of the aquifer (constant density), with the lens memory of [D1] and the '
            r'boundary [[lift]] on $\Gamma$. Remove all forcing ($Q_w = 0$, $\Psi = 0$, $q_{in} = 0$, sea at the reference '
            r'head), or, equivalently, consider the difference of two solutions with the same forcing, in which every '
            r'forcing cancels. $\mathbf{K}$ is the conductivity tensor.'))
    A(('prop', 'Proposition 2 (passivity).', [
        r'(a) The energy [[energy]] is dissipated at the rate [[dissip]]. (b) Hence the model is stable for every '
        r'$\mathbf{K}$, $S_s$, geometry and mesh, and any two runs with the same forcing converge. (c) The forcing '
        r'$q_{in}(t)$ may be any function. The conductances $C$ and $w_m$ may depend on time and on the head, '
        r'provided that they stay nonnegative and are nondecreasing in the head difference they act on. The '
        r'storages $\sigma_m$ must stay fixed or decrease in time. (d) A negative conductance $C = -\alpha c$, '
        r'$\alpha > 0$, is not passive, and whether it is stable depends on the rest of the model. For a strip of '
        r'length $L$ with the sea at $x = 0$, it has growing modes if and only if $\alpha c L > T$, at the rate given '
        r'by [[thresh]].',
        ('eq', 'energy', r'E = \frac{1}{2} \int_\Omega S_s h^2\, dV + \frac{1}{2} \sum_k \int_\Omega s_k h_k^2\, dV + '
                         r'\frac{1}{2} \sum_m \sigma_m \int_\Gamma y_m^2\, dA'),
        ('eq', 'dissip', r'\frac{dE}{dt} = -\int_\Omega \nabla h^\top \mathbf{K}\, \nabla h\, dV - \sum_k \int_\Omega '
                         r's_k a_k \left(h - h_k\right)^2 dV - \int_\Gamma \left[ C h^2 + \sum_m w_m \left(h - '
                         r'y_m\right)^2 \right] dA \le 0'),
        ('eq', 'thresh', r'\frac{\tanh z}{z} = \frac{T}{\alpha c L}, \quad \lambda = \frac{T z^2}{S L^2}, \quad '
                         r'\text{on the mesh: growth if and only if } \alpha c > \frac{T}{L - \Delta x/2}')]))
    A(('proof', r'(a) Multiply [[flow]], without forcing, by $h$ and integrate. The divergence term gives $-\int \nabla h^\top '
                r'\mathbf{K} \nabla h$ minus the boundary flux $\int_\Gamma h\, \mathbf{q}\cdot\mathbf{n}$; the sea face '
                r'(at the reference head) contributes nothing. Multiply $\partial_t h_k = a_k (h - h_k)$ by $s_k h_k$; '
                r'the sum with the lens term of [[flow]] is $-\int s_k a_k (h - h_k)^2$. Multiply $\partial_t y_m = \mu_m '
                r'(h - y_m)$ by $\sigma_m y_m$, which gives $w_m y_m (h - y_m)$. Then $-h \left[C h + \sum_m w_m (h - '
                r'y_m)\right] + \sum_m w_m y_m (h - y_m) = -C h^2 - \sum_m w_m (h - y_m)^2$. (b) $E$ is a norm of the '
                r'state and does not increase. (c) The forcing cancels in the difference of two solutions. With a '
                r'state-dependent conductance $f$, the dissipation becomes $(h_1 - h_2)(f(h_1) - f(h_2)) \ge 0$ when '
                r'$f$ is nondecreasing. A time-varying storage adds $\frac{1}{2} \dot\sigma_m y_m^2$ to [[dissip]], which is '
                r'not positive only if $\dot\sigma_m \le 0$. (d) A growing mode $h = \sinh(k x)\, e^{\lambda t}$ with '
                r'$\lambda = T k^2/S$ satisfies $T k \cosh(k L) = \alpha c \sinh(k L)$. With $z = kL$ this is [[thresh]], '
                r'which has a root $z > 0$ if and only if $T/(\alpha c L) < 1$, because $\tanh z / z$ falls from 1 to '
                r'0. On the mesh the conductance matrix $A$ is positive definite, and adding $-\alpha c\, e e^\top$ '
                r'creates one negative eigenvalue if and only if $\alpha c\, e^\top A^{-1} e > 1$. Here $e^\top A^{-1} '
                r'e$ is the resistance from the last cell to the sea, $(L - \Delta x/2)/T$.'))
    A(('p', r'Passivity is a property of the boundary alone, as in the theory of dissipative systems [7]; '
            r'stability with a non-passive term is a property of the whole model. Calibration changes the whole model: '
            r'it moves $T$, and a model may later be extended to a larger $L$. Condition [[thresh]] shows that a term that '
            r'was stable in validation can become unstable after either change. Check N3 shows this happening.'))

    # ------------------------------------------------------------------------------------------ 5
    A(('h', '5. Proposition 3: how few compartments are needed'))
    A(('p', r'The exact network has one compartment per exterior cell (<<nc>> in the test). A model needs the boundary '
            r'only on the band of periods its forcing and its questions contain: here from five days to forty years, '
            r'$[\omega_{min}, \omega_{max}]$ with $\omega = 2\pi/\text{period}$.'))
    A(('prop', 'Proposition 3 (approximation).', [
        r'(a) For $\left|s\right| = \omega$ in the band and $0 < \varepsilon < 1$, a compartment much slower than the '
        r'band acts as a conductance, and one much faster acts as a boundary storage [[collapse]]. On the band, $Z(s)$ '
        r'is therefore $C^\prime + \sigma^\prime s$ plus the compartments inside the band, with $C^\prime = C + '
        r'\sum_{slow} w_m$ and $\sigma^\prime = \sum_{fast} \sigma_m$. (b) The half-order boundary [[half]] is '
        r'approximated to a relative error of order $\varepsilon$ by the trapezoidal rule in $x = \ln \mu$ with the '
        r'nodes, weights and window [[quad]]. The count is [[count]]: it grows with the logarithm of the band and the '
        r'square of $\ln(1/\varepsilon)$. (c) All weights are positive, so the approximation is passive '
        r'(Proposition 2).',
        ('eq', 'collapse', r'\frac{s}{s + \mu} = 1 + O(\varepsilon) \ \ \text{if } \mu \le \varepsilon\, '
                           r'\omega_{min}, \qquad w\, \frac{s}{s + \mu} = \sigma s\, \left(1 + O(\varepsilon)\right) '
                           r'\ \ \text{if } \mu \ge \omega_{max}/\varepsilon'),
        ('eq', 'quad', [r'\mu_j = e^{x_j}, \quad w_j = \frac{\sqrt{S T}\, \eta}{\pi}\, e^{x_j/2}, \quad x_j = X_- + '
                        r'(j - 1) \eta, \quad \eta = \frac{\pi^2}{\ln(1/\varepsilon)},',
                        r'X_- = \ln \omega_{min} - 2 \ln \frac{2}{\pi \varepsilon}, \quad X_+ = \ln \omega_{max} + '
                        r'2 \ln \frac{2}{\pi \varepsilon}']),
        ('eq', 'count', r'M = 1 + \frac{X_+ - X_-}{\eta} = 1 + \frac{\ln(1/\varepsilon)}{\pi^2} \left[ \ln '
                        r'\frac{\omega_{max}}{\omega_{min}} + 4 \ln \frac{2}{\pi \varepsilon} \right]')]))
    A(('proof', r'(a) $s/(s + \mu) - 1 = -\mu/(s + \mu)$, whose modulus is at most $\mu/\omega \le \varepsilon$. And '
                r'$s/(s + \mu) - s/\mu = -s^2/(\mu (s + \mu))$, whose modulus relative to $\omega/\mu$ is at most '
                r'$\omega/\mu \le \varepsilon$. (b) The integrand of [[half]] in $x = \ln \mu$ is $f(x) = s\, e^{x/2}/(\pi '
                r'(s + e^x))$. For $s = i\omega$ its poles nearest to the real axis lie at $\text{Im}\, x = -\pi/2$, so '
                r'it is analytic in the strip $\left|\text{Im}\, x\right| < \pi/2$. The trapezoidal rule then '
                r'converges like $\exp(-2\pi d/\eta)$ with $d \to \pi/2$ [10], that is like $\exp(-\pi^2/\eta) = '
                r'\varepsilon$. The tails decay as $e^{x/2}/\pi$ to the left and $\omega e^{-x/2}/\pi$ to the right. '
                r'Their integrals beyond $X_-$ and $X_+$, divided by $\left|\sqrt{s}\right| = \sqrt{\omega}$, equal '
                r'$\varepsilon$ at the two band ends for the window [[quad]]. (c) is immediate.'))
    A(('p', r'Proposition 3(b) is an estimate, not a bound. The three errors add, and the trapezoidal constant is not '
            r'one. Check N2 found the error at the predicted count to be <<n2_f_lo>>–<<n2_f_hi>> times '
            r'$\varepsilon$, and the count that actually reaches $\varepsilon$ to be <<n2_more_lo>>–<<n2_more_hi>>% '
            r'larger. For a general exterior, check N1 fitted the weights by nonnegative least squares on a fixed '
            r'logarithmic grid. Over 3.5 decades, 3, 6 and 12 compartments gave median impedance errors of '
            r'<<pertej_M3_zmed>>, <<pertej_M6_zmed>> and <<pertej_M12_zmed>>: about three to four compartments per '
            r'decade are enough. The same positive rational fitting, with passivity enforced, is how external '
            r'electrical networks are reduced [8, 9].'))

    # ------------------------------------------------------------------------------------------ 6
    A(('h', '6. Proposition 4: what two piezometers can learn'))
    A(('p', r'Let heads be observed with noise at $x_1 < x_2 < L$ inside $\Omega$, near the cut at $x = L$. Assume the '
            r'band $(x_1, L)$ contains no unknown source (known recharge is allowed) and the vertically integrated '
            r'equation $S\, \partial_t h = T\, \partial_{xx} h + r$ holds in it. In this section $Z$ relates the '
            r'deviations of flux and head at $x = L$.'))
    A(('prop', 'Proposition 4 (identifiability and design).', [
        r'(a) *Separation.* For every $\omega \ne 0$ at which the heads carry signal, the heads at $x_1$ and $x_2$ '
        r'determine $Z(i\omega)$, whatever the rest of the model (the wells, the sea, the closure $\Psi$ outside the '
        r'band). The reconstruction [[sideways]] amplifies noise by about [[amp]]. (b) *Band.* At frequencies where '
        r'the forcing has no power, the data carry no information on $Z$. Outside the excited band, $Z$ is set by '
        r'the structure and the prior, not by the data. (c) *Confounding.* If an unknown source acts inside the band '
        r'(a closure $\Psi$, or an unknown inflow $q_{in}$ at the cut), it cannot be separated from $Z$ unless it is '
        r'restricted. (d) *Design.* Place two piezometers between the closure region and the cut, with no unknown '
        r'source between them and the cut. Space them about one diffusion length $\sqrt{T/(S \omega_{max})}$ apart, '
        r'and vary the pumping across the band and independently of the rain.',
        ('eq', 'sideways', r'\hat h(x, s) = A(s)\, e^{\kappa x} + B(s)\, e^{-\kappa x} + \hat h_p(x, s), \quad '
                           r'\kappa = \sqrt{s S/T}, \quad Z(s) = \frac{-T\, \partial_x \hat h(L, s)}{\hat h(L, s)}'),
        ('eq', 'amp', r'\exp\left( (L - x_2) \sqrt{\frac{\omega S}{2 T}} \right)')]))
    A(('proof', r'(a) In the band, the transformed equation $s S \hat h = T \hat h_{xx} + \hat r$ has the general solution '
                r'[[sideways]], where $\hat h_p$ is fixed by the known recharge. The two observations give a linear system '
                r'for $A$ and $B$ with determinant $-2 \sinh(\kappa (x_2 - x_1))$. For $s = i\omega$, $\omega \ne 0$, '
                r'$\kappa (x_2 - x_1)$ has a nonzero real part, so this determinant is never zero. Then $\hat h(L)$ '
                r'and $\partial_x \hat h(L)$, and hence $Z(i\omega)$, follow; nothing outside the band enters. '
                r'Continuing a solution of the heat equation sideways in this way is unique but ill-posed [11]. The '
                r'growing exponential has modulus [[amp]]. (b) A frequency absent from the forcing is absent from the '
                r'heads. In principle $Z$ is analytic, so its values on an interval fix it everywhere, but that '
                r'continuation is unstable; with noise only Proposition 3(a) and the prior remain. (c) If the truth '
                r'is $(Z, \Psi)$ with $\Psi$ acting at the boundary cell, the pair $(Z^\prime, \Psi + (Z^\prime - '
                r'Z)[u])$ produces the same heads for every $Z^\prime$. The same holds for $q_{in}$, unless it is '
                r'known or independent of the excitation. Pumping varied independently of the rain then acts as an '
                r'instrument [12]. (d) follows from (a)–(c) and from the amplification [[amp]].'))
    A(('p', r'Proposition 4 makes the boundary a target of the experimental design of the series. The pumping '
            r'schedule is the experiment. Its regime changes, months to years apart, are what make the boundary '
            r'identifiable, as persistent excitation does in system identification [12]. The two piezometers are '
            r'the sensors that this experiment needs.'))

    # ------------------------------------------------------------------------------------------ 7
    A(('h', '7. Learning PËRTEJ-GO: where the neural network goes'))
    A(('p', r'The question that led to this note was whether a neural regulariser could learn the true boundary '
            r'condition. Propositions 1–4 give the answer. A network should not replace the operator $\mathcal{Z}$. '
            r'Nothing linear lies outside the class [[pertej]]–[[lift]], a free network can leave the passive class (Proposition '
            r'2), and outside the excited band it would extrapolate without control (Proposition 4). The network has '
            r'three good places:'))
    A(('eq', 'param', r'C = \text{softplus}(a_0), \quad w_m = \text{softplus}(a_m), \quad \mu_m = \mu_1 \rho^{m-1}, '
                      r'\quad q_{in}(t) = g_\phi\left(P(t - r),\ 0 \le r \le r_{max}\right)'))
    A(('b', r'**The forcing.** $q_{in}(t)$ is the inflow from rain $P$ and may be any network $g_\phi$. It cancels in '
            r'Proposition 2, so it cannot destabilise anything. GARANCIA-GO and RINDËRTIMI-GO already reconstruct '
            r'this lateral inflow from rain [D2, D3]. PËRTEJ-GO adds the response that a prescribed inflow lacks.'))
    A(('b', r'**A monotone conductance.** $C_\theta(t, u) \ge 0$, nondecreasing in $u$, may be a network, for example '
            r'for a river that dries out or a seasonal clogging (Proposition 2(c)). The storages $\sigma_m$ stay '
            r'fixed, and the rates $\mu_m$ sit on a fixed geometric grid with three to four per decade (Proposition '
            r'3).'))
    A(('b', r'**The learned regulariser.** The network belongs in the objective, as a prior learned from geology:'))
    A(('eq', 'J', r'J(\theta) = \frac{1}{2} \sum_{k} \left\| \frac{\mathbf{d}_k - \mathbf{h}_k(\theta)}{\sigma} '
                  r'\right\|^2 - \log p_\phi\left(\mathbf{f}(Z_\theta)\right), \quad \mathbf{f}(Z) = \left( \ln '
                  r'\text{Re}\, Z(i\omega_j),\ \ln \text{Im}\, Z(i\omega_j) \right)_{j=1}^{24}'))
    A(('p', r'where $\mathbf{d}_k$ are the observed heads and $\sigma$ their noise. The density $p_\phi$ is trained on '
            r'an ensemble of simulated exteriors. Each geological scenario (lengths, heterogeneous $T$, $S$, closed or '
            r'leaky ends) gives its exact $Z$ by Proposition 1, its 48 features and so a sample. In check N5 '
            r'$p_\phi$ is a Gaussian with 1% shrinkage of its covariance, the linear case of a learned regulariser '
            r'[13]; a neural density (for example a normalising flow) replaces it when the ensemble is richer. Its '
            r'weight is not tuned: the noise level and the ensemble fix it. The gradient of $J$ comes from the '
            r'adjoint of the time stepping, which carries $M$ scalar adjoint states per boundary cell, as for the '
            r'lens compartments of [D1]. The checks below used finite differences over 13 parameters.'))

    # ------------------------------------------------------------------------------------------ 8
    A(('h', '8. Other terms the flow equation may need'))
    A(('p', r'The same test (is the term passive, or at least does it keep the maximum principle?) sorts the other '
            r'candidates. Table {{terms}} lists them.'))
    A(('cap', r'Table {{terms}}. Terms that can be added to the flow equation [[flow]], the condition under which each keeps '
              r'the model stable, and where each stands.'))
    A(('table', ['Term', 'What is added', 'Stable if', 'Status'], [
        ['Lens memory', r'$-\sum_k s_k a_k (h_f - h_k)$, with $\partial_t h_k = a_k (h_f - h_k)$',
         r'always ($s_k, a_k \ge 0$)', '[D1], eqs. (1)–(3)'],
        ['Learned closure', r'$\Psi(h_f, \mathbf{x}; \gamma)$',
         r'dissipative: $\Psi$ nonincreasing in $h_f$', '[D1], eq. (6); zero in its tests'],
        ['Boundary memory (PËRTEJ-GO)', r'$C u + \sum_m w_m (u - y_m)$ on $\Gamma$',
         r'$C, w_m \ge 0$; storages fixed', 'this note'],
        ['Inelastic storage', r'$S_s = S_{ske}$ above the preconsolidation head $h_{pc}$, $S_{skv}$ below it',
         r'always ($S_s > 0$: maximum principle)', 'MODFLOW 6 CSUB [18]; subsidence of the Durrës plain [D1]'],
        ['Tidal and barometric loading', r'$+\gamma\, S_s\, \partial_t \eta_\sigma$ ($\eta_\sigma$: vertical load in '
                                         r'head units, $\gamma$: loading efficiency)',
         'a known forcing: stability unchanged', '[21]'],
    ], [3.2, 6.2, 4.0, 3.6], 9.5))

    # ------------------------------------------------------------------------------------------ 9
    A(('h', '9. Numerical checks'))
    A(('p', r'**Test bed.** A one-dimensional coastal aquifer, 10 km long, with $T$ = 500 m²/d and $S$ = 0.05 '
            r'(diffusivity $10^4$ m²/d). It uses cell-centred finite volumes of 100 m, implicit Euler with daily '
            r'steps and 20 years of simulation. The sea is a fixed head at $x = 0$; the far end is closed. The model '
            r'sees only the first 2 km, and its cut at 2 km must stand in for the 8 km beyond. Recharge of 0.5 mm/d, '
            r'with a seasonal swing of ±80%, falls on the model domain. The well is at 0.95 km. Its pumping is either '
            r'steady (0.6 m²/d per metre of coast) or varied (regimes of 6 months to 3 years at 0.3–1.0 m²/d, with '
            r'±15% monthly changes). The piezometer is at 1.45 km, the band piezometers at 1.75 and 1.85 km, and the '
            r'boundary cell at 1.95 km. The parameters are illustrative and not calibrated for Fushë-Kuqe. All '
            r'checks run in <<rt>> s (experiments/pertej_go/pertej_exp.py).'))
    A(('h2', 'N1. The exact boundary and its reductions (Proposition 1)'))
    A(('p', r'The exact network of the 8 km closed exterior has <<nc>> compartments, $C$ = <<C_exact>> (zero up to '
            r'rounding, as Proposition 1 says for a closed exterior) and $\sum w_n = c$. With it, the cut model '
            r'reproduces the full aquifer to <<ex_bc>> m at the boundary cell and <<ex_pz>> m at the piezometer, '
            r'over 20 years in which the head at the boundary cell ranges over <<range_bc>> m. Positive reductions '
            r'with 3, 6 and 12 compartments were compared with a fixed head, a no-flow boundary and the best GHB '
            r'(conductance scanned over 70 values, best $C$ = <<ghb_C>> m/d = <<ghb_Cc>>$c$). Table {{t1}} and '
            r'Figure {{n1}} show the result.'))
    A(('cap', r'Table {{t1}}. N1: errors of the cut model against the full aquifer over 20 years with varied pumping '
              r'(root mean square and maximum at the boundary cell, root mean square at the piezometer), and the '
              r'error of the impedance over 3.5 decades (median and maximum).'))
    A(('table', ['Boundary at the cut', 'Boundary cell, rms', 'Boundary cell, max', 'Piezometer, rms',
                 'Impedance, median / max'], [
        ['Fixed head', '<<fixed_head_bc>>', '<<fixed_head_mx>>', '<<fixed_head_pz>>', '–'],
        ['No flow (prescribed inflow)', '<<no_flow_bc>>', '<<no_flow_mx>>', '<<no_flow_pz>>', '–'],
        ['Calibrated GHB', '<<ghb_calibrated_bc>>', '<<ghb_calibrated_mx>>', '<<ghb_calibrated_pz>>', '–'],
        ['PËRTEJ-GO, 3 compartments', '<<pertej_M3_bc>>', '<<pertej_M3_mx>>', '<<pertej_M3_pz>>',
         '<<pertej_M3_zmed>> / <<pertej_M3_zmax>>'],
        ['PËRTEJ-GO, 6 compartments', '<<pertej_M6_bc>>', '<<pertej_M6_mx>>', '<<pertej_M6_pz>>',
         '<<pertej_M6_zmed>> / <<pertej_M6_zmax>>'],
        ['PËRTEJ-GO, 12 (11 nonzero)', '<<pertej_M12_bc>>', '<<pertej_M12_mx>>', '<<pertej_M12_pz>>',
         '<<pertej_M12_zmed>> / <<pertej_M12_zmax>>'],
        ['Exact network, <<nc>> compartments', '<<ex_bc>> m', '–', '<<ex_pz>> m', '0'],
    ], [5.0, 2.9, 2.9, 2.9, 3.3], 9.5))
    A(('img', 'n1', 17.0))
    A(('cap', r'Figure {{n1}}. N1. (a) Head at the boundary cell in years 6–14: the full aquifer and five boundaries at '
              r'the cut. The six-compartment PËRTEJ-GO lies on the truth. (b) Root-mean-square error over 20 years '
              r'(logarithmic axis).'))
    A(('p', r'Even the best GHB, calibrated on these very data, misses by <<ghb_calibrated_bc>>, because a '
            r'conductance cannot store water. Six positive compartments cut the error <<ratio_m6>> times, and twelve '
            r'cut it <<ratio_m12>> times.'))
    A(('h2', 'N2. How many compartments the half-order boundary needs (Proposition 3)'))
    A(('cap', r'Table {{t2}}. N2: the count [[count]] against the count actually needed, for the half-order boundary [[half]] over '
              r'4 and 6 decades of period starting at 30 years.'))
    A(('table', ['Decades', 'Target ε', 'M by the count formula', 'Error at that M', 'M needed for ε'], [
        ['4', '1%', '<<n2_0_mp>>', '<<n2_0_e>>', '<<n2_0_mm>>'],
        ['4', '0.1%', '<<n2_1_mp>>', '<<n2_1_e>>', '<<n2_1_mm>>'],
        ['6', '1%', '<<n2_2_mp>>', '<<n2_2_e>>', '<<n2_2_mm>>'],
        ['6', '0.1%', '<<n2_3_mp>>', '<<n2_3_e>>', '<<n2_3_mm>>'],
    ], [2.4, 2.4, 3.2, 3.4, 3.6], 9.5))
    A(('p', r'Two more decades add only 2–4 compartments, and ten times more accuracy roughly doubles the count, as [[count]] '
            r'predicts (Figure {{n23}}a).'))
    A(('h2', 'N3. Passivity (Proposition 2)'))
    A(('p', r'Start the model without forcing from a 1 m mound around the well. With the passive exact boundary the '
            r'energy decreases at every step, from <<E0>> to <<Eend>> in five years. With $C = -0.2c$, above the '
            r'threshold, the energy grows by a factor <<g02>> in five years. Its measured growth rate, <<r02>> per '
            r'day, matches the rate of the semi-discrete model under implicit Euler (<<r02_ie>>) to a relative '
            r'<<r02_match>>. The continuous strip [[thresh]] gives <<r02_ct>>; the difference comes from the boundary term '
            r'acting on the cell-centre head, half a cell inside the face. The thresholds are $\alpha$ = <<th_c>> '
            r'for the continuum and <<th_d>> on the mesh. With $C = -0.02c$, below them, the 2 km model decays. The '
            r'same boundary in longer models (Table {{t3}}, Figure {{n23}}c) shows the danger of Proposition 2(d).'))
    A(('cap', r'Table {{t3}}. N3: the non-passive boundary $C = -0.02c$, stable in the 2 km test, in longer models.'))
    A(('table', ['Model length', 'Threshold α on the mesh', 'Growth rate (1/d)', 'Head amplitude'], [
        ['2 km', '<<lt_2_a>>', '<<lt_2_r>>', '<<lt_2_t>>'],
        ['4 km', '<<lt_4_a>>', '<<lt_4_r>>', '<<lt_4_t>>'],
        ['6 km', '<<lt_6_a>>', '<<lt_6_r>>', '<<lt_6_t>>'],
        ['8 km', '<<lt_8_a>>', '<<lt_8_r>>', '<<lt_8_t>>'],
    ], [3.0, 4.4, 4.2, 5.4], 9.5))
    A(('img', 'n23', 17.0))
    A(('cap', r'Figure {{n23}}. (a) N2: relative error of the half-order boundary with M = 4, 8 and 13 compartments on '
              r'the quadrature [[quad]]; shaded, the four decades of the design. (b) N3: energy of the unforced model '
              r'with the passive boundary and with two negative conductances. (c) N3: growth rate of the '
              r'$C = -0.02c$ boundary as the model is lengthened.'))
    A(('h2', 'N4. Learning the boundary from two piezometers (Proposition 4)'))
    A(('p', r'The boundary was learned from the two band piezometers by output error. The band cells (1.85 and 1.95 '
            r'km) were simulated with the observed head at 1.75 km and the known recharge as inputs, and the 13 '
            r'nonnegative parameters ($C$ and 12 compartments, 3.4 per decade) were chosen to reproduce the head '
            r'at 1.85 km. Nothing else of the model was used, and no noisy data were differentiated. The learned '
            r'boundary was then put into the cut model to predict a regime never seen in the data. Over 10 years, '
            r'the pumping doubles from year 2 and a drought cuts recharge to 30% in years 3–8; the head at the '
            r'boundary cell falls by <<pr_dh>> m. Table {{t4}} and Figure {{n4}} show the results.'))
    A(('cap', r'Table {{t4}}. N4: median relative error of the learned impedance in three bands of period, and '
              r'root-mean-square error of the prediction at the boundary cell. "Steady" and "varied" refer to the '
              r'pumping during the 20 years of data.'))
    A(('table', ['Data', 'Noise', '40–200 years', '30 days–10 years', '2.5–10 days', 'Prediction'], [
        ['Steady pumping', '2 mm', '<<seasonal_2mm_low>>', '<<seasonal_2mm_mid>>', '<<seasonal_2mm_high>>',
         '<<seasonal_2mm_pred>>'],
        ['Steady pumping', '10 mm', '<<seasonal_10mm_low>>', '<<seasonal_10mm_mid>>', '<<seasonal_10mm_high>>',
         '<<seasonal_10mm_pred>>'],
        ['Varied pumping', '2 mm', '<<broadband_2mm_low>>', '<<broadband_2mm_mid>>', '<<broadband_2mm_high>>',
         '<<broadband_2mm_pred>>'],
        ['Varied pumping', '10 mm', '<<broadband_10mm_low>>', '<<broadband_10mm_mid>>', '<<broadband_10mm_high>>',
         '<<broadband_10mm_pred>>'],
        ['Varied, closure in the band (1.95 km)', '2 mm', '<<psi_in_band_low>>', '<<psi_in_band_mid>>',
         '<<psi_in_band_high>>', '–'],
        ['Varied, closure outside it (1.25 km)', '2 mm', '<<psi_outside_band_low>>', '<<psi_outside_band_mid>>',
         '<<psi_outside_band_high>>', '–'],
        ['Exact boundary', '–', '–', '–', '–', '<<pr_ex>>'],
        ['Calibrated GHB · no flow · fixed head', '–', '–', '–', '–',
         '<<pr_ghb_calibrated>> · <<pr_no_flow>> · <<pr_fixed_head>>'],
    ], [4.6, 1.7, 2.3, 2.6, 2.2, 3.6], 9.5))
    A(('img', 'n4', 17.0))
    A(('cap', r'Figure {{n4}}. N4. (a) Modulus of the learned impedance against the exact one. Shaded: the band of the '
              r'data (30 days–10 years) and, in grey, periods of 2.5–10 days and 40–200 years. (b) A closure source of 0.15 m²/d '
              r'(seasonal) plus a 0.1 m²/d step in year 6, placed inside or outside the band. (c) Prediction of a '
              r'regime never seen in the data.'))
    A(('p', r'The results follow Proposition 4 point by point. Inside the band, varied pumping learns the boundary '
            r'four times better than steady pumping at the same noise (<<broadband_2mm_mid>> against '
            r'<<seasonal_2mm_mid>>). At periods of 2.5–10 days, which no forcing excites, every estimate is wrong '
            r'by more than 200%. That does not matter for the prediction, which has no power there either. Varied '
            r'pumping also reaches the 40–200 year band, beyond the 20-year record, to <<broadband_2mm_low>>, '
            r'because the positive structure links it to the band. A closure source between the piezometers and '
            r'the cut corrupts the boundary (<<psi_in_band_mid>>), while the same source outside the band leaves '
            r'it intact (<<psi_outside_band_mid>>). The learned boundary predicts the new regime to '
            r'<<broadband_2mm_pred>>, <<pr_ratio>> times better than the GHB calibrated on the full record.'))
    A(('h2', 'N5. The learned regulariser (Section 7)'))
    A(('p', r'Two priors were trained, each on <<K_ens>> simulated exteriors of 3–15 km, half closed and half leaky, '
            r'with heterogeneous, correlated $T$. The **right** prior draws the median $T$ from 150–1500 m²/d and '
            r'$S$ from 0.01–0.2. The truth lies at the <<near_pct>>th percentile of its Mahalanobis distances, '
            r'within the prior but not at its centre. The **wrong** prior draws $T$ from 40–160 m²/d and $S$ from '
            r'0.004–0.02, a geology about six times less conductive. Under it the truth lies at the '
            r'<<shifted_pct>>th percentile. The identifications of N4 were repeated with each prior (Table {{t5}}, '
            r'Figure {{n5}}).'))
    A(('cap', r'Table {{t5}}. N5: the identifications of N4 without a prior, with the right prior and with the wrong one '
              r'(median relative error of the impedance; root-mean-square error of the prediction of N4).'))
    rows = []
    lab = dict(seasonal_2mm='Steady, 2 mm', seasonal_10mm='Steady, 10 mm', broadband_2mm='Varied, 2 mm',
               broadband_10mm='Varied, 10 mm')
    for k in ('seasonal_2mm', 'seasonal_10mm', 'broadband_2mm', 'broadband_10mm'):
        rows.append([lab[k], 'none', f'<<{k}_low>>', f'<<{k}_mid>>', f'<<{k}_high>>', f'<<{k}_pred>>'])
        rows.append(['', 'right', f'<<n5_{k}_near_low>>', f'<<n5_{k}_near_mid>>', f'<<n5_{k}_near_high>>',
                     f'<<n5_{k}_near_pred>>'])
        rows.append(['', 'wrong', f'<<n5_{k}_shifted_low>>', f'<<n5_{k}_shifted_mid>>', f'<<n5_{k}_shifted_high>>',
                     f'<<n5_{k}_shifted_pred>>'])
    A(('table', ['Data', 'Prior', '40–200 years', '30 days–10 years', '2.5–10 days', 'Prediction'], rows,
       [3.4, 1.8, 2.8, 3.1, 2.8, 3.1], 9.5))
    A(('img', 'n5', 17.0))
    A(('cap', r'Figure {{n5}}. N5. (a) Steady pumping with 2 mm noise. The right prior (its 5–95% envelope in violet) '
              r'brings the boundary much closer to the truth at the shortest periods, where the data are silent. '
              r'(b) Error of the prediction of Figure {{n4}}c without a prior, with the wrong prior and with the right '
              r'one.'))
    A(('p', r'The prior helps in every case and most where the data are silent. The error at periods of 2.5–10 days '
            r'falls <<n5_hi_lo>>–<<n5_hi_hi>> times. The 40–200 year error for steady pumping with 2 mm noise falls '
            r'from <<seasonal_2mm_low>> to <<n5_seasonal_2mm_near_low>>, and every prediction improves. Two findings '
            r'qualify this. First, the wrong prior still improved every case over no prior, and it was only slightly '
            r'worse than the right one (better in one case). The prior acts mainly through the *shape* of the '
            r'impedance, which all diffusive exteriors share, while the data fix its level inside the band. This is '
            r'no licence to use a wrong prior: the Mahalanobis distance of the estimate flags it, though weakly. '
            r'Under the wrong prior the estimates sit at percentiles <<n5_ps_lo>>–<<n5_ps_hi>> of its ensemble, and '
            r'under the right one at <<n5_pn_lo>>–<<n5_pn_hi>>. The data-only estimates sit far outside both (distances '
            r'<<n5_dpl_lo>>–<<n5_dpl_hi>>, against a 99th percentile of <<near_p99>>). Second, a prior does not '
            r'replace the experiment. With steady pumping and 10 mm noise, the best prior still predicts to only '
            r'<<n5_seasonal_10mm_shifted_pred>>, while varied pumping with 2 mm noise and no prior predicts to '
            r'<<broadband_2mm_pred>>.'))
    A(('h2', 'N6. Sea-level rise: the cut that the boundary decided'))
    A(('p', r'The sea was raised by 0.5 m over 20 years on top of the forcing of N1, and each cut model was compared '
            r'with the full aquifer. The aquifer must store water as its heads rise with the sea, and that water '
            r'comes from the fresh discharge to the sea (mean <<q_sea>> m²/d per metre of coast). Less fresh '
            r'discharge moves the toe inland. In the sharp-interface equilibrium of [D1, eq. (24)] the toe distance '
            r'is inversely proportional to the fresh discharge. Table {{t6}} shows the result.'))
    A(('cap', r'Table {{t6}}. N6: fresh water that does not reach the sea during 20 years of a 0.5 m rise, the fall of '
              r'the fresh discharge at year 20, and the landward shift of the equilibrium toe that this fall would '
              r'cause [D1, eq. (24)].'))
    A(('table', ['Inland boundary', 'Fresh water lost (m³ per m of coast)', 'Discharge at year 20',
                 'Equilibrium toe'], [
        ['Full aquifer (truth)', '<<n6_full_def>>', '−<<n6_full_end>>', '<<n6_full_toe>>'],
        ['PËRTEJ-GO, 6 compartments', '<<n6_pertej_M6_def>>', '−<<n6_pertej_M6_end>>', '<<n6_pertej_M6_toe>>'],
        ['PËRTEJ-GO, 12 compartments', '<<n6_pertej_M12_def>>', '−<<n6_pertej_M12_end>>', '<<n6_pertej_M12_toe>>'],
        ['Prescribed inflow [D1, eq. (31)]', '<<n6_no_flow_def>>', '−<<n6_no_flow_end>>', '<<n6_no_flow_toe>>'],
        ['Calibrated GHB', '<<n6_ghb_calibrated_def>>', '−<<n6_ghb_calibrated_end>>', '<<n6_ghb_calibrated_toe>>'],
        ['Fixed head', '<<n6_fixed_head_def>>', '−<<n6_fixed_head_end>>', '<<n6_fixed_head_toe>>'],
    ], [5.4, 4.4, 3.6, 3.6], 9.5))
    A(('p', r'The answer to the sea-level question changes by a factor of <<n6_spread>> with the inland boundary. '
            r'The prescribed inflow, which led [D1] to cut sea-level rise, underestimates the lost fresh water '
            r'<<n6_nf_ratio>> times. It sees the storage of the 2 km model but not that of the 8 km beyond it. The '
            r'fixed head overestimates it three times, and even the GHB calibrated in N1 errs by <<n6_ghb_err>>. '
            r'PËRTEJ-GO with six compartments errs by <<n6_m6_err>>, and with twelve by <<n6_m12_err>>. The '
            r'boundary learned from piezometers in a pumping experiment (N4) therefore decides a question that the '
            r'assembly had to leave open, in line with the role of the inland boundary in the sea-level response '
            r'of coastal aquifers [19, 20].'))

    # ------------------------------------------------------------------------------------------ 10
    A(('h', '10. What PËRTEJ-GO adds'))
    A(('b', r'**A term for the flow equation with an exact pedigree.** [[pertej]]–[[lift]] is the boundary of every linear exterior '
            r'and only of physical exteriors (Proposition 1). It sits next to the two terms the series already '
            r'added and has the same mathematical form as the lens memory.'))
    A(('b', r'**Stability as a property of the learned boundary alone** (Proposition 2), with a rule for neural '
            r'networks: free in the forcing, monotone in the conductances, never in the storages. A non-passive '
            r'term that passed validation failed when the model was lengthened (N3).'))
    A(('b', r'**Logarithmic cost** (Proposition 3): 6–12 states per boundary cell, three to four per decade of period '
            r'(N1, N2).'))
    A(('b', r'**Identifiability and design** (Proposition 4): two piezometers separate the boundary from the closure '
            r'$\Psi$ and from everything inside the model, and the pumping schedule is the experiment that reveals '
            r'the boundary (N4).'))
    A(('b', r'**A learned prior from simulated geology** that repairs the periods the data cannot reach, does not '
            r'replace the experiment, and in this test was robust to a wrong geology (N5).'))
    A(('b', r'**An answer to a question the assembly left open**: whether sea-level rise matters inland depends on '
            r'the boundary, and PËRTEJ-GO reproduces the true response within <<n6_m6_err>> (N6).'))

    # ------------------------------------------------------------------------------------------ 11
    A(('h', '11. Limits'))
    A(('p', r'The propositions assume a linear (confined or linearised), fresh exterior. An unconfined exterior with '
            r'large changes of saturated thickness is only approximately linear. The sea face, where a wedge of salt '
            r'water moves, is a different problem: density couples flow and salt, and Proposition 2 covers the '
            r'constant-density part only. The checks are one-dimensional. In two and three dimensions the exact '
            r'operator is nonlocal along the cut (remark (iii) of Section 3), and the identifiability of Proposition '
            r'4 then needs piezometers along the cut; neither was tested. The count [[count]] is an estimate within a '
            r'factor of about 2.4 of $\varepsilon$. The learned prior was a Gaussian on 48 features of synthetic '
            r'ensembles; the neural density of Section 7 is proposed, not tested. The two priors are two cases, not '
            r'a study of misspecification. The inflow from rain $q_{in}$ was zero in the test bed, so its confounding '
            r'with $Z$ (Proposition 4(c)) and the instrument of varied pumping are argued, not tested. The gradient '
            r'came from finite differences, not the adjoint. The parameters are illustrative; on Fushë-Kuqe the '
            r'band, the piezometer spacing and the pumping experiment must be designed with the calibrated $T$ and '
            r'$S$.'))
    A(('p', r'*Verification note.* The external references [1–21] were checked in Crossref (DOI, authors, title, '
            r'venue), November 2026. The note was drafted with the help of an AI assistant. Every number is computed '
            r'by experiments/pertej_go/pertej_exp.py (results in res/pertej.json) and inserted by the build script.'))
    A(('refs',))
    return BL
