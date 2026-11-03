"""Text of the SHIU-GO note (Albanian). blocks(J, K) returns the block list and the values used in the text.
Text conventions: $inline math$, **bold**, [[key]] equation number, {{key}} figure or table number, <<name>> value."""
import re

import numpy as np

REFS = [
    'Allan, A. L., & Cohen, S. N. (2020). Pathwise stochastic control with applications to robust filtering. Annals of Applied Probability 30(5): 2274–2310. https://doi.org/10.1214/19-AAP1558',
    'Andersson, W., Heiss, J., Krach, F., & Teichmann, J. (2024). Extending path-dependent NJ-ODEs to noisy observations and a dependent observation framework. Transactions on Machine Learning Research. https://openreview.net/forum?id=0T2OTVCCC1',
    'Anvari, M., Tabar, M. R. R., Peinke, J., & Lehnertz, K. (2016). Disentangling the stochastic behavior of complex time series. Scientific Reports 6: 35435. https://doi.org/10.1038/srep35435',
    'Bain, A., & Crisan, D. (2009). Fundamentals of Stochastic Filtering. Springer.',
    'Baptista, R., Marzouk, Y., & Zahm, O. (2024). On the representation and learning of monotone triangular transport maps. Foundations of Computational Mathematics 24(6): 2063–2108. https://doi.org/10.1007/s10208-023-09630-x',
    'Carrillo, J. A., Hoffmann, F., Stuart, A. M., & Vaes, U. (2024). The mean-field ensemble Kalman filter: near-Gaussian setting. SIAM Journal on Numerical Analysis 62(6): 2549–2587. https://doi.org/10.1137/24M1628207',
    'Christensen, H. M. (2020). Constraining stochastic parametrisation schemes using high-resolution simulations. Quarterly Journal of the Royal Meteorological Society 146(727): 938–962. https://doi.org/10.1002/qj.3717',
    'Cohen, S. N. (2020). Uncertainty and filtering of hidden Markov models in discrete time. Probability, Uncertainty and Quantitative Risk 5: 4. https://doi.org/10.1186/s41546-020-00046-x',
    'Eberhardt, F., Kaynar, N., & Siddiq, A. (2025). Discovering causal models with optimization: confounders, cycles, and instrument validity. Management Science 71(4): 3283–3302. https://doi.org/10.1287/mnsc.2021.02066',
    'Fan, J., Fang, C., Gu, Y., & Zhang, T. (2024). Environment invariant linear least squares. Annals of Statistics 52(5): 2268–2292. https://doi.org/10.1214/24-AOS2435',
    'Gu, Y., Fang, C., Bühlmann, P., & Fan, J. (2025). Causality pursuit from heterogeneous environments via neural adversarial invariance learning. Annals of Statistics 53(5): 2230–2257. https://doi.org/10.1214/25-AOS2541',
    'Gupta, A., & Lermusiaux, P. F. J. (2021). Neural closure models for dynamical systems. Proceedings of the Royal Society A 477(2252): 20201004. https://doi.org/10.1098/rspa.2020.1004',
    'Gupta, A., & Lermusiaux, P. F. J. (2023). Bayesian learning of coupled biogeochemical–physical models. Progress in Oceanography 216: 103050. https://doi.org/10.1016/j.pocean.2023.103050',
    'Herrera, C., Krach, F., & Teichmann, J. (2021). Neural jump ordinary differential equations: consistent continuous-time prediction and filtering. International Conference on Learning Representations (ICLR).',
    'Krach, F., Nübel, M., & Teichmann, J. (2026). Optimal estimation of generic dynamics by path-dependent neural jump ODEs. Stochastic Processes and their Applications. https://doi.org/10.1016/j.spa.2026.105058; arXiv:2206.14284v7.',
    'Lorch, L., Krause, A., & Schölkopf, B. (2024). Causal modeling with stationary diffusions. Proceedings of AISTATS 2024, PMLR 238: 1927–1935.',
    'Rodriguez-Iturbe, I., Porporato, A., Ridolfi, L., Isham, V., & Cox, D. R. (1999). Probabilistic modelling of water balance at a point: the role of climate, soil and vegetation. Proceedings of the Royal Society A 455(1990): 3789–3805.',
    'Schneider, T., Stuart, A. M., & Wu, J.-L. (2021). Learning stochastic closures using ensemble Kalman inversion. Transactions of Mathematics and Its Applications 5: 1–31. https://doi.org/10.1093/imatrm/tnab003',
    'Spantini, A., Baptista, R., & Marzouk, Y. (2022). Coupling techniques for nonlinear ensemble filtering. SIAM Review 64(4): 921–953. https://doi.org/10.1137/20M1312204',
    'Taeb, A., Bühlmann, P., & Chandrasekaran, V. (2024). Model selection over partially ordered sets. Proceedings of the National Academy of Sciences 121(8): e2314228121. https://doi.org/10.1073/pnas.2314228121',
    'Dokumente të brendshme: «Asimilimi i të dhënave për dinamikën që mungon» (8 tetor 2026); «Zbulimi i modeleve shkakësore me optimizim» (20 tetor 2026); shënimi i asimilimit të kushteve kufitare dhe fillestare të Fushë-Kuqes (ASIMILIMI-GO, tetor 2026); GJURMA-GO (rishikimi 42).',
]


def blocks(J, K):
    vals = values(J, K)
    B = static_blocks() + result_blocks(vals) + closing_blocks()

    def fill(s):
        return re.sub(r'<<(\w+)>>', lambda m: vals[m.group(1)], s) if isinstance(s, str) else s

    def fill_any(x):
        if isinstance(x, list):
            return [fill_any(y) for y in x]
        return fill(x)
    return [tuple(fill_any(x) for x in b) for b in B], vals


# ------------------------------------------------------------------------------------------------------------ values
def values(J, K):
    import shiu_model as SM
    S, runs, P = J['summary'], J['runs'], J['params']
    pc = lambda x, d=0: f'{100 * x:.{d}f}%'.replace('.', ',').replace('-', '−')
    n = lambda x, d=0: (f'{x:,.{d}f}').replace(',', ' ').replace('.', ',').replace('-', '−')
    v = {}
    # set-up (one twin for the climate numbers)
    tw = SM.simulate_twin(runs[0]['seed'])
    yr = lambda x: x.reshape(SM.N_YEARS, SM.YEAR).sum(1)
    rain, rech = yr(tw['P']), yr(tw['R'])
    normal = SM.YEAR_MULT == 1.0
    v.update(nseed=str(P['NSEED']), rain_n=n(rain[normal].mean(), -1 if False else 0), rech_n=n(rech[normal].mean()),
             rech_d=n(rech[10]), ratio=pc(rech[normal].sum() / rain[normal].sum()), pday=pc(P['P_DAY']),
             gapm=n(1 / P['P_DAY'], 1), pwell=pc(P['P_WELL']), sigo=n(100 * P['SIG_O']))
    # drought-year carry-over: the part of that year's recharge drained in earlier years (vadose memory)
    Y = SM.YEAR

    def carry_share(t_):
        m10 = np.zeros(SM.N_YEARS * Y); m10[10 * Y:11 * Y] = 1.0
        own = SM.erlang2(t_['D'] * m10, SM.TRUE['tau'])[10 * Y:11 * Y].sum()
        return 1.0 - own / t_['Rdet'][10 * Y:11 * Y].sum()
    c0 = carry_share(tw)
    c_all = [c0] + [carry_share(SM.simulate_twin(r_['seed'])) for r_ in runs[1:]]
    v.update(rain_d=n(rain[10]), carry=pc(c0), carry_med=pc(float(np.median(c_all))),
             p_share=pc(rain[10] / rain[normal].mean()), r_share=pc(rech[10] / rech[normal].mean()))
    dry_ok = (rech[10] / rech[normal].mean() > rain[10] / rain[normal].mean() + 0.15) and 0.2 < np.median(c_all) < 0.5
    # E1
    for m in ('M0', 'M1', 'A'):
        v[f'ex_{m}'] = pc(S[m]['excess_rel']['med'])
        v[f'dist_{m}'] = n(100 * np.sqrt(S[m]['dist']['med']), 1)
        v[f'cov_{m}'] = pc(S[m]['test_cov']['med'])
        v[f'corr_{m}'] = n(S[m]['corr_month']['med'], 3)
        v[f'dr_{m}'] = pc(S[m]['drought_rel_err']['med'])
        v[f'g14_{m}'] = n(S[m]['gap'][3]['med'] / S['oracle']['gap'][3]['med'], 1)
    v['cov_or'] = pc(S['oracle']['test_cov']['med']); v['corr_or'] = n(S['oracle']['corr_month']['med'], 3)
    v['g14_or'] = n(1e4 * S['oracle']['gap'][3]['med']); v['g14_M0cm'] = n(1e4 * S['M0']['gap'][3]['med'])
    v['ex_A_q'] = f"{pc(S['A']['excess_rel']['q25'])}–{pc(S['A']['excess_rel']['q75'])}"
    ap = S['A_par']
    q = lambda k, d=1: f"{n(ap[k]['med'], d)} [{n(ap[k]['q25'], d)}–{n(ap[k]['q75'], d)}]"
    v.update(a_tau=q('tau'), a_sige=q('sig_e', 2), a_sfc=q('sfc', 0), a_kL=q('kL'), a_bL=q('bL'), a_taue=q('tau_e', 0))
    rl = S['rain_law']
    v.update(rl_c0=n(rl['0']['med'] if '0' in rl else rl[0]['med'], 3), rl_c1=n((rl['1'] if '1' in rl else rl[1])['med'], 3),
             rl_d0=n((rl['3'] if '3' in rl else rl[3])['med'], 3), rl_d1=n((rl['4'] if '4' in rl else rl[4])['med'], 3))
    # E2
    B = S['B']
    for k in ('ls', 'bic', 'eills4', 'eills16'):
        v[f'b_{k}'] = pc(B[k]['test_rel_oracle']['med'])
    f = lambda k, feat: pc(B[k]['freq'][feat])
    v.update(cos_bic=f('bic', 'cos'), cos_e4=f('eills4', 'cos'), cos_e16=f('eills16', 'cos'),
             sin_bic=f('bic', 'sin'), sin_e16=f('eills16', 'sin'), one_bic=f('bic', 'one'), one_e16=f('eills16', 'one'),
             x40=f('bic', 'X40'))
    d_bic, d_e16 = B['bic']['drought']['med'], B['eills16']['drought']['med']
    v['b_drought_gain'] = pc(1 - d_e16 / d_bic)
    I = S['ident']
    cm, cc, cco = I['cos_mult_vs_closure']['med'], I['cos_mult_vs_closure_cl']['med'], I['cos_mult_vs_coastal']['med']
    v.update(cos_m=n(cm, 3), cos_cl=n(cc, 3), cos_co=n(cco, 3), inf_m=n(1 / (1 - cm ** 2)), inf_co=n(1 / (1 - cco ** 2), 1))
    # E4
    tm = np.array(K['true_month']); pj = np.array([(a, b) for a, b, c in K['probe_jumps']], float)
    summer = [4, 5, 6, 7, 8]
    v['km_lam_err'] = pc(np.nanmedian(np.abs(pj[:, 0] / tm[:, 0] - 1)))
    v['km_ab_sum'] = pc(np.nanmedian(np.abs(pj[summer, 1] / tm[summer, 1] - 1)))
    v['km_jn'] = f"{min(c for a, b, c in K['probe_jumps'])}–{max(c for a, b, c in K['probe_jumps'])}"
    kmw, kms = K['probe_km']['winter'], K['probe_km']['summer']
    v.update(kmw_lam=n(kmw['lam_km'], 2), kmw_true=n(kmw['lam_true'], 2), kmw_ab=n(kmw['abar_km'], 1),
             kmw_abt=n(kmw['abar_true'], 1), kms_lam=n(kms['lam_km'], 2), kms_true=n(kms['lam_true'], 2))
    pd_, sd_ = K['probe_drift'], K['satgauge_drift']
    v.update(pd_cE=n(pd_['cE'], 2), pd_sfc=n(pd_['sfc']), pd_kL=n(pd_['kL'], 1), pd_bL=n(pd_['bL'], 2),
             pd_sw=n(pd_['sw']), pd_mae=f"{n(K['probe_drift_mae'][0], 2)}–{n(K['probe_drift_mae'][1], 2)}",
             sg_mae=f"{n(min(K['satgauge_drift_mae']), 2)}–{n(max(K['satgauge_drift_mae']), 2)}",
             sg_sfc=n(sd_['sfc']), sg_bL=n(sd_['bL'], 1), sig_s=n(K['probe_sig_s'], 2))
    sat = np.array([a for a, b, c in K['sat_km']], float)
    v['sat_rng'] = f"{n(np.nanmin(sat), 3)}–{n(np.nanmax(sat), 2)}"
    v['sat_n'] = str(int(np.sum(np.isfinite(sat))))
    v['box'] = ('**Përgjigjja e shkurtër.** (1) Forcimi shkruhet si sistem stokastik: shiu si proces Poisson me shenja, '
                'lagështia e tokës si SDE me kërcime, zona e pangopur si kujtesë dhe gabimi i rimbushjes si proces '
                'Ornstein–Uhlenbeck shumëzues (Rruga A); ose si term shtesë në ekuacionin e filtrimit, mbi një bibliotekë '
                'tiparesh të shiut, me zgjedhje shkakësore ndërmjet viteve të lagura dhe të thata (Rruga B). (2) Ligji i '
                'forcimit zbulohet duke minimizuar humbjen e parashikimit të Krach et al. (2026) mbi vëzhgime me kohë dhe '
                'maska të rastit; teprica mbi humbjen optimale është largësia nga parashikimi optimal (Pohimi 1). (3) '
                'Ekuacionet e filtrimit dhe të transportit marrin forcimin stokastik, kujtesën, mbylljen dhe stuhitë si '
                'kërcime; filtri merr formën PD-NJ-ODE me fizikë midis vëzhgimeve. (4) Në një akuifer sintetik me '
                f'{P["NSEED"]} binjakë, Rruga A parashikon vetëm {v["ex_A"]} më keq se ligji i vërtetë, kundrejt '
                f'{v["ex_M1"]} për transferimin linear të shiut dhe {v["ex_M0"]} për forcimin gausian të shënimit të '
                f'asimilimit; Rruga B mbetet {v["b_bic"]} mbi optimumin, sepse biblioteka lineare nuk e kap pragun e kullimit.')

    # guards: the text states these findings
    chk = [S['A']['excess_rel']['med'] < 0.2, S['A']['excess_rel']['med'] < S['M1']['excess_rel']['med'] < S['M0']['excess_rel']['med'],
           B['bic']['test_rel_oracle']['med'] > 3 * S['A']['excess_rel']['med'],
           B['eills16']['freq']['cos'] < B['bic']['freq']['cos'], B['eills16']['freq']['sin'] < B['bic']['freq']['sin'],
           d_e16 < d_bic, B['eills16']['test_rel_oracle']['med'] >= B['bic']['test_rel_oracle']['med'],
           cm > 0.98, cco < 0.95, S['M0']['gap'][3]['med'] > 5 * S['oracle']['gap'][3]['med'],
           S['A']['gap'][3]['med'] < 2 * S['oracle']['gap'][3]['med'],
           abs(ap['tau']['med'] - 20) < 2, abs(ap['sig_e']['med'] - 0.25) < 0.07, ap['kL']['q75'] < 25,
           max(K['probe_drift_mae']) < 0.2, min(K['satgauge_drift_mae']) > max(K['probe_drift_mae']),
           max(K['satgauge_drift_mae']) < 0.6, kmw['lam_km'] > 1.5 * kmw['lam_true'],
           S['M0']['test_cov']['med'] > 0.93, abs(S['oracle']['test_cov']['med'] - 0.9) < 0.03, dry_ok]
    if not all(chk):
        raise SystemExit(f'SHIU-GO findings changed ({chk}): revise the text')
    return v


def static_blocks():
    B = [
        ('title', 'Shiu, rimbushja dhe kushtet stokastike në ekuacionet e akuiferit bregdetar'),
        ('subtitle', 'SHIU-GO: zbulimi i forcimit stokastik nga vëzhgime të parregullta dhe jo të plota, si ekuacion diferencial '
                     'stokastik më vete ose si shtesë në ekuacionin e filtrimit, dhe format e reja të ekuacioneve të filtrimit, '
                     'të transportit dhe të filtrit'),
        ('byline', 'Përgatitur për Prof. Asoc. Dr. Dulian Zeqiraj · Fakulteti i Gjeologjisë dhe i Minierave, UPT · 3 nëntor 2026'),

        ('h', '1. Problemi dhe përgjigjja e shkurtër'),
        ('p', 'Ekuacionet e akuiferit bregdetar kanë nevojë për kushtet dinamike stokastike që i drejtojnë: shiun, reshjet, '
              'rimbushjen, nivelin e detit dhe pompimin. Këto kushte nuk maten të plota. Shiu matet çdo ditë në një stacion, '
              'ngarkesat në piezometra në ditë të parregullta dhe jo në të gjitha njëherësh, kloruri rrallë, rimbushja kurrë '
              'drejtpërdrejt. Pyetja është si të zbulohet ligji i tyre nga të dhënat, qoftë si ekuacion diferencial stokastik '
              '(SDE) më vete, qoftë si shtesë në ekuacionin e rrjedhjes.'),
        ('p', 'Kuadri është ai i Krach, Nübel & Teichmann (2026): një bashkësi serish kohore me vëzhgime diskrete, të '
              'parregullta dhe ndoshta jo të plota të një procesi stokastik në kohë të vazhdueshme, ku kohët e vëzhgimit dhe '
              'koordinatat e vëzhguara janë të rastit. Nuk supozohet asnjë njohuri për procesin, as për kohët dhe maskat e '
              'vëzhgimit, përveç të dhënave dhe disa kushteve rregullsie. Parashikimi optimal në kuptimin L² është pritja e '
              'kushtëzuar e procesit nga informacioni i vëzhguar deri në atë çast.'),
        ('p', 'Terminologjia: «ekuacioni i filtrimit» në këtë shënim është ekuacioni i rrjedhjes së ujërave nëntokësore '
              '(filtrimi nëpër mjedisin poroz), ndërsa «filtri» është vlerësimi i gjendjes nga vëzhgimet (asimilimi). Të dyja '
              'marrin formë të re këtu, bashkë me ekuacionin e transportit.'),
        ('box', '<<box>>'),

        ('h', '2. Çfarë merret nga secili material'),
        ('cap', 'Tabela {{tab_src}}. Tri materialet dhe vendi i tyre në sistemin e ekuacioneve.'),
        ('table', ['Materiali', 'Çfarë merret', 'Ku hyn'],
         [['Krach, Nübel & Teichmann (2026), ETH Zürich',
           'Vëzhgime me kohë dhe maska të rastit; parashikimi optimal është pritja e kushtëzuar (Propozimi 2.5); funksioni i '
           'humbjes me maska dhe objektivi ekuivalent (ek. 11–13, Vërejtja 4.10); Lema 4.2; struktura «ODE midis vëzhgimeve, '
           'kërcim në vëzhgim» (ek. 10); nënshkrimi për varësinë nga rruga (Teorema 3.7); momentet e kushtëzuara (seksioni 5); '
           'filtrimi me trajnim nga simulime (Përfundimi 6.2)',
           'Modeli i vëzhgimit [[obs]], filtri [[filter]], humbja [[loss]]–[[pred]], Pohimet 1 dhe 4, Rruga A [[km]]'],
          ['Zbulimi i modeleve shkakësore me optimizim (rishikimi juaj, 20 punime)',
           'Invarianca ndërmjet mjediseve: EILLS (Fan, Fang, Gu & Zhang, 2024) dhe FAIR (Gu et al., 2025); programi i saktë '
           'MIQP me ℓ₀ (N3 i rishikimit); difuzionet stacionare si modele shkakësore (Lorch, Krause & Schölkopf, 2024); '
           'kontrolli i zbulimeve të rreme (Taeb, Bühlmann & Chandrasekaran, 2024); kërkimi me optimizim (Eberhardt, Kaynar '
           '& Siddiq, 2025)',
           'Rruga B: zgjedhja e termave të shtesës [[aug]] me [[eills]]'],
          ['Asimilimi i dinamikës që mungon (rishikimi juaj, 20 punime)',
           'N1: mbyllja e mësuar me kujtesë brenda ekuacionit të rrjedhjes (Gupta & Lermusiaux, 2021, 2023); mbyllje '
           'stokastike nga statistika (Schneider, Stuart & Wu, 2021); gabimi shumëzues 1 + e (Christensen, 2020); N2: çelësi '
           'EnKF–transport (Carrillo et al., 2024; Spantini, Baptista & Marzouk, 2022; Baptista, Marzouk & Zahm, 2024); N3: '
           'filtri i qëndrueshëm (Allan & Cohen, 2020; Cohen, 2020)',
           'Ekuacioni i filtrimit [[flow]], gabimi [[err]], çelësi [[switch]], shiriti [[band]]']],
         [3.6, 9.2, 4.2], 9.5),

        ('h', '3. Sistemi i ekuacioneve'),
        ('img', 'system', 17.0),
        ('cap', 'Figura {{system}}. Sistemi SHIU-GO. Shtresa e forcimit (lart) jep rimbushjen; ekuacionet e filtrimit dhe të '
                'transportit (në mes) lidhen nëpërmjet dendësisë; vëzhgimet në kohë të rastit ushqejnë filtrin, dhe zbulimi '
                'kthen ligjin e forcimit (shigjeta me ndërprerje).'),
        ('h2', '3.1 Shtresa e forcimit stokastik'),
        ('p', 'Shiu është një proces Poisson me shenja (Rodriguez-Iturbe et al., 1999). Ngjarjet vijnë me intensitet sezonal '
              '$\\lambda(t)$, dhe secila sjell një thellësi $a$ me shpërndarje eksponenciale me mesatare $\\bar a(t)$:'),
        ('eq', 'rain', ('P(dt) = \\int_0^\\infty a\\, N(dt, da), \\quad \\text{E}\\, N(dt, da) = \\lambda(t)\\, \\frac{e^{-a/\\bar a(t)}}{\\bar a(t)}\\, da\\, dt,',
                         '\\log \\lambda(t) = c_0 + c_1 \\cos \\omega t + c_2 \\sin \\omega t')),
        ('p', 'Lagështia e tokës $s(t)$ në zonën e rrënjëve ndjek një SDE me kërcime. Shiu e ngre me kërcime deri në '
              'kapacitetin $\\bar s$ (teprica rrjedh në sipërfaqe), ndërsa evapotranspirimi dhe kullimi e ulin midis ngjarjeve:'),
        ('eq', 'soil', ('ds_t = -\\left[c_E E_p(t) \\min\\left(1, \\frac{s_t}{s_w}\\right) + L(s_t)\\right] dt + \\sigma_s\\, dW_t + \\int_0^\\infty \\min(a, \\bar s - s_{t^-})\\, N(dt, da),',
                               'L(s) = k_L \\left(\\frac{(s - s_{fc})^+}{\\bar s - s_{fc}}\\right)^{b_L}')),
        ('p', 'Kullimi e kalon zonën e pangopur me vonesë. Kujtesa jepet nga një bërthamë plotësisht monotone ose, si këtu, nga '
              'një bërthamë Erlang e rendit dy. Kjo e fundit është Markoviane me dy rezervuarë linearë, pra me ndryshore të '
              'brendshme, siç e kërkon formalizmi Mori–Zwanzig i N1:'),
        ('eq', 'vadose', 'R_t = \\int_0^\\infty \\kappa_\\tau(u)\\, L(s_{t-u})\\, du, \\quad \\kappa_\\tau(u) = \\frac{u}{\\tau^2} e^{-u/\\tau}, \\quad \\tau \\dot r_1 = L(s_t) - r_1, \\quad \\tau \\dot r_2 = r_1 - r_2, \\quad R_t = r_2'),
        ('p', 'Rimbushja që arrin në tabelën e ujit ka një gabim shumëzues, me strukturën $1 + e$ të Christensen (2020); $e$ '
              'është një proces Ornstein–Uhlenbeck:'),
        ('eq', 'err', 'R^{tot}(x, t) = \\chi(x) (1 + e_t) R_t, \\quad de_t = -\\frac{e_t}{\\tau_e}\\, dt + \\sigma_e \\sqrt{\\frac{2}{\\tau_e}}\\, dW^e_t'),
        ('p', 'Niveli i detit dhe pompimi mbeten si në shënimin e asimilimit: anomali Ornstein–Uhlenbeck dhe stuhi si proces '
              'Poisson i përbërë me shuarje; pompimi është i njohur kur regjistrohet:'),
        ('eq', 'sea', '\\eta_t = \\eta_0 + \\eta^{tide}_t + \\eta^{ia}_t + \\eta^{surge}_t, \\quad d\\eta^{surge}_t = -\\frac{\\eta^{surge}_t}{\\tau_s}\\, dt + dJ^s_t, \\quad Q_w(t)\\ \\text{i vëzhguar me maskë}'),
        ('p', 'Ekuacionet [[rain]]–[[sea]] janë **Rruga A**: forcimi është një sistem stokastik më vete, me parametra '
              '$\\theta_F = (\\lambda, \\bar a, c_E, s_w, s_{fc}, k_L, b_L, \\tau, \\sigma_e, \\tau_e)$ për t’u zbuluar, dhe i '
              'jep ekuacionit të filtrimit rimbushjen si hyrje.'),

        ('h2', '3.2 Forma e re e ekuacionit të filtrimit (rrjedhjes)'),
        ('p', 'Ekuacioni i rrjedhjes merr formën e N1 dhe forcimin stokastik të seksionit 3.1. Ngarkesa $h$ është ngarkesa '
              'ekuivalente e ujit të ëmbël; dendësia e ndryshueshme hyn në fluksin e Darcy-t, dhe mbyllja ka kujtesë:'),
        ('eq', 'flow', ('S \\partial_t h = \\nabla \\cdot \\left[K \\left(\\nabla h + \\epsilon_\\rho \\frac{c}{c_s} \\nabla z\\right)\\right] + \\chi (1 + e_t) R_t - \\sum_w Q_w \\delta_w + \\sum_k I_k \\delta(t - T_k) \\chi_{ow}',
                               '+ \\sum_{j=1}^{J} \\gamma_j \\Psi_j(h, x) + \\int_0^{\\tau_m} \\kappa_\\phi(u)\\, h(x, t - u)\\, du + \\sigma_h \\xi')),
        ('p', 'Këtu $\\epsilon_\\rho = (\\rho_s - \\rho_f)/\\rho_f$, $\\delta_w$ është burimi pikësor i pusit $w$, $I_k$ është '
              'thellësia e ujit të detit që infiltrohet në rripin bregdetar $\\chi_{ow}$ në stuhinë $k$, $\\Psi_j$ janë funksionet '
              'bazë të termit të panjohur (Gupta & Lermusiaux, 2023), $\\kappa_\\phi$ është kujtesa e shkëmbimit me argjilat '
              '(Gupta & Lermusiaux, 2021) dhe $\\xi$ është zhurmë e bardhë në hapësirë dhe kohë. Kushtet kufitare janë:'),
        ('eq', 'bc', 'h = \\frac{\\rho_s}{\\rho_f} \\eta_t - \\epsilon_\\rho z \\ \\ \\text{në kufirin me detin}, \\qquad K \\left(\\nabla h + \\epsilon_\\rho \\frac{c}{c_s} \\nabla z\\right) \\cdot n = 0 \\ \\ \\text{në kufijtë pa rrjedhje}'),
        ('p', 'Në **Rrugën B** forcimi nuk modelohet më vete. Ekuacioni [[flow]] merr një term shtesë mbi një bibliotekë '
              'tiparesh të shiut dhe të evapotranspirimit, me një mbetje Ornstein–Uhlenbeck $\\varrho_t$:'),
        ('eq', 'aug', ('\\chi (1 + e_t) R_t \\ \\longrightarrow\\ \\sum_{j \\in S} \\beta_j \\varphi_j(t) \\chi_j(x) + \\chi \\varrho_t,',
                              '\\varphi_j \\in \\left\\{\\kappa_{\\tau_j} * P,\\ \\kappa_{\\tau_j} * E_p,\\ \\kappa_{\\tau_j} * (\\kappa * P - E_p)^+,\\ \\cos \\omega t,\\ \\sin \\omega t,\\ 1\\right\\}')),
        ('p', 'Bashkësia $S$ zgjidhet me invariancë ndërmjet viteve të lagura, normale dhe të thata (seksioni 3.8), që të '
              'mbeten vetëm termat që janë shkaqe të rimbushjes. Termat sezonalë dhe konstantja janë në bibliotekë qëllimisht: '
              'ato përshkruajnë klimën mesatare, por nuk janë shkaqe.'),

        ('h2', '3.3 Forma e re e ekuacionit të transportit'),
        ('p', 'Transporti i kripës (klorurit) merr kujtesën e shkëmbimit me zonën e palëvizshme (forma e GJURMA-GO), burimin e '
              'ujit të rimbushjes me përqendrimin e tij, një mbyllje dhe kërcimet e kripës nga përmbytjet e stuhive '
              '(overwash), kur niveli i detit kalon kreshtën e dunave. Në formën konservative me burime dhe pusa:'),
        ('eq', 'transport', ('n \\partial_t c + n \\int_0^t \\kappa_c(u)\\, \\partial_t c(x, t - u)\\, du + \\nabla \\cdot (q c) - \\nabla \\cdot (n D(q) \\nabla c) = \\chi (1 + e_t) R_t c_R',
                               '- \\sum_w Q_w \\delta_w c + \\sum_k I_k \\delta(t - T_k) \\chi_{ow} c_s + \\sum_l \\beta^c_l \\Phi_l + \\sigma_c \\xi_c')),
        ('p', 'ku $q = -K(\\nabla h + \\epsilon_\\rho (c/c_s) \\nabla z)$ dhe $c_R$ është përqendrimi i ujit të rimbushjes. Të '
              'njëjtat stuhi $T_k$ dhe të njëjtat thellësi $I_k$ hyjnë në [[flow]] si ujë dhe në [[transport]] si kripë. Kufiri me '
              'detin ndërron sipas drejtimit të rrjedhjes, dhe stuhitë janë kalimet e nivelit të detit mbi kreshtën $z_d$:'),
        ('eq', 'tbc', 'c = c_s \\ \\text{ku}\\ q \\cdot n < 0, \\qquad (n D \\nabla c) \\cdot n = 0 \\ \\text{ku}\\ q \\cdot n \\geq 0, \\qquad T_k = \\inf\\{t > T_{k-1} : \\eta_t > z_d\\}'),
        ('p', 'Rimbushja hyn në transport dy herë: nëpër shpejtësinë $q$, që varet nga $h$, dhe si burim uji me $c_R$. Një '
              'gabim në ligjin e rimbushjes e anon pra kripën dy herë, dhe kjo është arsyeja praktike për ta zbuluar ligjin e saj.'),

        ('h2', '3.4 Modeli i vëzhgimit'),
        ('p', 'Vektori i vëzhgueshëm $X_t$ përmban ngarkesat në piezometra, kloruret në puse, shiun ditor, lagështinë e tokës '
              'kur matet, nivelin e detit dhe pompimin. Ai vëzhgohet në kohë të rastit $t_i$, me maskë '
              '$M_i \\in \\{0, 1\\}^{d_X}$ dhe me zhurmë:'),
        ('eq', 'obs', 'Y_i = M_i \\odot (X_{t_i} + \\varepsilon_i), \\qquad \\mathcal{A}_t = \\sigma\\left(X_{t_i, j}, t_i, M_i : t_i \\leq t,\\ M_{i, j} = 1\\right), \\qquad \\hat X_t = \\text{E}[X_t \\mid \\mathcal{A}_t]'),
        ('p', 'Sipas Propozimit 2.5 të Krach et al. (2026), $\\hat X$ është procesi i vetëm (deri në bashkësi me masë zero) që '
              'minimizon gabimin katror të parashikimit. Supozimet 1–6 aty kërkojnë, ndër të tjera, që maskat të jenë të pavarura '
              'nga kohët dhe nga numri i vëzhgimeve, që çdo koordinatë të vëzhgohet me probabilitet pozitiv dhe që procesi të mos '
              'vëzhgohet pikërisht në një kërcim. Zhurma e vëzhgimit trajtohet nga Andersson et al. (2024).'),

        ('h2', '3.5 Forma e re e ekuacionit të filtrit'),
        ('p', 'Filtri merr strukturën e PD-NJ-ODE (ekuacioni 10 i Krach et al., 2026): një ekuacion diferencial midis '
              'vëzhgimeve dhe një kërcim në çdo vëzhgim. Forma e re vendos fizikën e seksioneve 3.1–3.3 midis vëzhgimeve dhe i '
              'lë rrjetit neural vetëm korrigjimin, me nënshkrimin e rrugës së interpoluar të vëzhgimeve si hyrje:'),
        ('eq', 'filter', ('dH_t = \\left[\\Phi(H_t, u_t; \\theta) + f_\\vartheta\\left(H_t, t, \\tau(t), \\pi_m(\\tilde X^{\\leq \\tau(t)} - X_0)\\right)\\right] dt',
                               '+ \\left[\\rho_\\vartheta\\left(H_{t^-}, Y_t, M_t, \\pi_m(\\tilde X^{\\leq t} - X_0)\\right) - H_{t^-}\\right] du_t, \\qquad \\hat X_t = g(H_t)')),
        ('p', 'Këtu $H$ është gjendja e shtuar (ngarkesat në rrjetë, $s$, $r_1$, $r_2$, $e$, kloruri dhe koeficientët e '
              'mbylljes), $\\Phi$ është diskretizimi i [[soil]]–[[transport]], $u_t$ numëron vëzhgimet, $\\tau(t)$ është çasti i '
              'vëzhgimit të fundit dhe $\\pi_m$ është nënshkrimi i cunguar i rrugës. Me $f_\\vartheta = 0$ dhe me kërcimin afin:'),
        ('eq', 'kalman', '\\rho(H_{t^-}, Y_t, M_t) = H_{t^-} + P_{t^-} C_t^\\top \\left(C_t P_{t^-} C_t^\\top + \\Gamma_t\\right)^{-1} \\left(Y_t - C_t H_{t^-}\\right), \\qquad C_t = \\text{diag}(M_t)\\, C'),
        ('p', 'filtri është filtri Kalman, ose EnKF-ja kur kovariancat merren nga ensemble-i. Me hartë transporti në vend të '
              'kërcimit afin, ai është filtri jolinear i Spantini, Baptista & Marzouk (2022); çelësi N2 zgjedh ndërmjet tyre '
              '(seksioni 3.9).'),

        ('h2', '3.6 Zbulimi: funksioni objektiv'),
        ('p', 'Parametrat e forcimit $\\theta$ dhe korrigjimi $\\vartheta$ mësohen duke minimizuar humbjen e PD-NJ-ODE me '
              'objektivin ekuivalent (Vërejtja 4.10) mbi $N$ rrugë ose dritare kohore:'),
        ('eq', 'loss', '\\hat \\Phi_N(\\theta, \\vartheta) = \\frac{1}{N} \\sum_{j=1}^{N} \\frac{1}{n_j} \\sum_{i=1}^{n_j} \\left(\\left|M_i \\odot (X_{t_i} - \\hat X_{t_i})\\right|_2 + \\left|M_i \\odot (X_{t_i} - \\hat X_{t_i^-})\\right|_2\\right)^2'),
        ('p', 'Për ligjin e forcimit përdoret pjesa e parashikimit, pra gabimi katror me maskë i parashikimit pak para çdo '
              'vëzhgimi:'),
        ('eq', 'pred', 'L_{pred}(\\theta) = \\text{E}\\left[\\frac{1}{n} \\sum_{i=1}^{n} \\left|M_i \\odot \\left(Y_i - \\hat X^\\theta_{t_i^-}\\right)\\right|_2^2\\right]'),
        ('p', 'Kur ndryshoret e fshehura (rimbushja, $e$, ndërfaqja) duhen filtruar nga të dhënat reale, korrigjimi '
              '$\\vartheta$ trajnohet mbi binjakë të simuluar nga [[rain]]–[[transport]], ku koordinatat e fshehura vëzhgohen '
              'gjatë trajnimit me probabilitet $p \\in (0, 1)$. Sipas Përfundimit 6.2 të Krach et al. (2026), dalja konvergjon '
              'atëherë te $\\text{E}[\\varphi(X_t) \\mid \\mathcal{Y}_t]$ për ligjin e simulatorit.'),

        ('h2', '3.7 Rruga A: SDE-ja e forcimit veçmas'),
        ('p', 'Kur vetë ndryshorja e forcimit vëzhgohet (një sondë lagështie ose një lizimetër), ligji i saj nxirret nga '
              'koeficientët Kramers–Moyal. Për një proces me difuzion dhe kërcime, këta e ndajnë driftin nga difuzioni dhe nga '
              'kërcimet (Anvari et al., 2016). Për SDE-në [[soil]]:'),
        ('eq', 'km', ('M_n(s) = \\lim_{\\Delta \\to 0} \\Delta^{-1}\\, \\text{E}\\left[(s_{t + \\Delta} - s_t)^n \\mid s_t = s\\right],',
                         'M_1 = \\mu(s, t) + \\lambda m_1(s), \\quad M_2 = \\sigma_s^2 + \\lambda m_2(s), \\quad M_n = \\lambda m_n(s),\\ n \\geq 3')),
        ('p', 'ku $\\mu$ është drifti i [[soil]] dhe $m_n(s) = \\text{E}[\\min(a, \\bar s - s)^n]$. Pa cungim nga ngopja, '
              '$m_n = n!\\, \\bar a^n$, prandaj $\\bar a = M_4/(4 M_3)$ dhe $\\lambda = M_3/(6 \\bar a^3)$. Me të dhëna orare '
              'është më i qëndrueshëm zbulimi i kërcimeve mbi një prag $J$, sepse shenjat eksponenciale nuk kanë kujtesë mbi prag:'),
        ('eq', 'jumps', '\\hat{\\bar a} = \\overline{\\Delta s - J}\\ \\ \\text{mbi kërcimet}, \\qquad \\hat \\lambda = \\frac{N_J}{T_{obs}}\\, e^{J / \\hat{\\bar a}}'),
        ('p', 'Këtu $N_J$ është numri i rritjeve $\\Delta s > J$ dhe $T_{obs}$ gjatësia e regjistrimit. Momentet e kushtëzuara i jep edhe PD-NJ-ODE (seksioni 5 i Krach et al., 2026), kur shtohen koordinatat '
              '$X^2, X^3, X^4$; atëherë [[km]] lexohet nga derivati i momenteve të parashikuara pak pas çdo vëzhgimi.'),

        ('h2', '3.8 Rruga B: shtesa me zgjedhje shkakësore'),
        ('p', 'Në Rrugën B gabimi i parashikimit është linear në koeficientët $\\beta$ të [[aug]]: $\\nu(\\beta) = \\nu_0 - '
              'G \\beta$, ku $G_j$ është përgjigjja e filtrit ndaj tiparit $\\varphi_j$ dhe $\\nu_0$ janë inovacionet pa forcim. '
              'Termat zgjidhen me objektivin EILLS të Fan, Fang, Gu & Zhang (2024), ku mjediset $e$ janë vitet e lagura, '
              'normale dhe të thata:'),
        ('eq', 'eills', 'Q_\\gamma(\\beta) = \\sum_e \\text{E}_e\\left[(\\nu_0 - G \\beta)^2\\right] + \\gamma \\sum_{j \\in S} \\sum_e \\left(\\text{E}_e\\left[(\\nu_0 - G \\beta) G_j\\right]\\right)^2 + \\lambda_0 |S|'),
        ('p', 'Për një bibliotekë të vogël minimumi gjendet saktësisht me numërim; për biblioteka të mëdha, programi MIQP i '
              'N3 të rishikimit të zbulimit shkakësor jep të njëjtin optimum me certifikatë. Një term që lidhet me rimbushjen '
              'vetëm në klimën mesatare, si një valë sezonale, nuk ka të njëjtin korrelacion me mbetjet në vite të ndryshme, '
              'prandaj penalizohet.'),

        ('h2', '3.9 Çelësi hibrid dhe shiriti i qëndrueshëm'),
        ('p', 'Çelësi N2 përdor kërcimin afin [[kalman]] kur parashikimi është afër gausianit dhe hartën e transportit kur '
              'largohet prej tij (Carrillo et al., 2024, Teorema 4, e vërtetuar për limitin mean-field, jo për '
              'ensemble të fundme):'),
        ('eq', 'switch', '\\hat \\varepsilon_n \\approx d_g\\left(\\mathcal{Q}\\mathcal{P}\\mu_n^M, G \\mathcal{Q}\\mathcal{P}\\mu_n^M\\right), \\qquad \\rho = \\begin{cases} \\text{afin}\\ (\\text{EnKF}), & \\hat \\varepsilon_n \\leq \\tau_g \\\\ \\text{hartë transporti}, & \\hat \\varepsilon_n > \\tau_g \\end{cases}'),
        ('p', 'Shiriti N3 jep për çdo sasi $\\varphi$ (ngarkesa në një pus, kloruri) pritjen e poshtme dhe të sipërme mbi '
              'ligjet e forcimit që pajtohen me të dhënat (Allan & Cohen, 2020; Cohen, 2020), me $\\ell$ log-përgjasën:'),
        ('eq', 'band', '\\overline{\\mathcal{E}}(\\varphi \\mid \\mathcal{A}_t) = \\text{sup}_\\theta \\left\\{\\text{E}^\\theta[\\varphi \\mid \\mathcal{A}_t] - \\frac{1}{k}\\left(\\ell(\\hat \\theta) - \\ell(\\theta)\\right)^{k\'}\\right\\}, \\qquad \\underline{\\mathcal{E}}(\\varphi \\mid \\mathcal{A}_t) = -\\overline{\\mathcal{E}}(-\\varphi \\mid \\mathcal{A}_t)'),

        ('h', '4. Pohimet'),
        ('p', '**Pohimi 1 (humbja e parashikimit identifikon ligjin e forcimit).** Le të vlejnë Supozimet 1–6 të Krach et al. '
              '(2026), me zhurmë vëzhgimi $\\varepsilon_i$ të pavarur nga $X$ dhe nga kuadri i vëzhgimeve, me mesatare zero. '
              'Atëherë për çdo parashikues $\\hat X^\\theta$ të përshtatur ndaj $\\mathcal{A}$:'),
        ('eq', 'p1', 'L_{pred}(\\theta) = L^* + D(\\theta), \\qquad D(\\theta) = \\text{E}\\left[\\frac{1}{n} \\sum_{i=1}^{n} \\left|M_i \\odot \\left(\\hat X_{t_i^-} - \\hat X^\\theta_{t_i^-}\\right)\\right|_2^2\\right] \\geq 0'),
        ('p', 'ku $L^*$ është humbja e parashikimit optimal. Nëse klasa e modeleve e përmban $\\hat X$ te $\\theta^*$ dhe '
              '$D(\\theta) > 0$ për çdo $\\theta \\neq \\theta^*$, atëherë $\\theta^*$ është minimizuesi i vetëm i $L_{pred}$. '
              'Vërtetimi. Shkruajmë $Y_i - \\hat X^\\theta_{t_i^-} = (X_{t_i} - \\hat X_{t_i^-}) + (\\hat X_{t_i^-} - \\hat '
              'X^\\theta_{t_i^-}) + \\varepsilon_i$ në koordinatat e vëzhguara. Lema 4.2 e Krach et al. (2026), që mbështetet te '
              'Supozimi 3 ($X_{t_i} = X_{t_i^-}$) dhe te pavarësia e maskave, jep zhdukjen e termit të kryqëzuar ndërmjet dy '
              'pjesëve të para. Termat e kryqëzuar me $\\varepsilon_i$ zhduken nga pavarësia dhe nga mesatarja zero; varianca e '
              'zhurmës hyn në $L^*$. Pjesa e dytë rrjedh menjëherë. ∎'),
        ('p', 'Pasoja praktike: teprica e humbjes së një modeli mbi humbjen optimale është pikërisht largësia mesatare katrore e '
              'parashikimeve të tij nga parashikimi optimal. Në test, ku parashikimi optimal njihet, të dyja maten (seksioni 5).'),
        ('p', '**Pohimi 2 (koeficientët Kramers–Moyal të tokës).** Për SDE-në [[soil]], me drift $\\mu$ të kufizuar dhe '
              'Lipschitz, intensitet $\\lambda$ të vazhdueshëm dhe shenja eksponenciale me mesatare $\\bar a$:'),
        ('eq', 'p2', 'm_n(s) = \\text{E}\\left[\\min(a, \\bar s - s)^n\\right] = n!\\, \\bar a^n\\, \\mathbb{P}\\left(n + 1, \\frac{\\bar s - s}{\\bar a}\\right) + (\\bar s - s)^n e^{-(\\bar s - s)/\\bar a}'),
        ('p', 'ku $\\mathbb{P}$ është funksioni gama jo i plotë i rregulluar, dhe relacionet [[km]] vlejnë. Mbi pragun $J$, '
              '$a - J$ ka të njëjtën shpërndarje eksponenciale dhe $\\Pr(a > J) = e^{-J/\\bar a}$, prandaj [[jumps]] është '
              'vlerësues i qëndrueshëm kur kërcimet nuk cungohen.'),
        ('p', 'Vërtetimi. Gjeneratori i [[soil]] është'),
        ('eqn', '\\mathcal{L} f = \\mu f\' + \\frac{1}{2} \\sigma_s^2 f\'\' + \\lambda \\int [f(s + \\min(a, \\bar s - s)) - f(s)]\\, \\nu(da).'),
        ('p', 'Për '
              '$f_n(y) = (y - s)^n$ në $y = s$, pjesa e difuzionit jep $\\mu$ për $n = 1$, $\\sigma_s^2$ për $n = 2$ dhe zero për '
              '$n \\geq 3$; pjesa e kërcimeve jep $\\lambda m_n(s)$. Formula e Dynkin-it jep $\\text{E} f_n(s_\\Delta) = \\Delta '
              '\\mathcal{L} f_n(s) + o(\\Delta)$. Integrimi i $x^n e^{-x/\\bar a}/\\bar a$ deri në $\\bar s - s$, plus masa në '
              'cungim, jep [[p2]]. ∎ Kushti praktik është $\\lambda \\Delta \\ll 1$: me të dhëna orare $\\lambda \\Delta '
              '\\approx 0{,}02$; me rivizitim satelitor çdo 3–6 ditë $\\lambda \\Delta \\approx 1$, dhe kufiri nuk arrihet.'),
        ('p', '**Pohimi 3 (identifikueshmëria e shtesës).** Në modelin linear dhe gausian, le të jenë $g_e$ dhe $g_\\gamma$ '
              'përgjigjet e ngarkesave të vëzhguara ndaj një gabimi shumëzues konstant $e R_t$ dhe ndaj një burimi mbyllës '
              'konstant me gjurmë $\\chi_\\gamma$. Korrelacioni posterior i dy koeficientëve është $-\\cos(g_e, g_\\gamma)$ '
              '(në metrikën e zhurmës), dhe varianca e $\\hat e$ zmadhohet me faktorin $1/(1 - \\cos^2(g_e, g_\\gamma))$. Kosinusi '
              'është 1 atëherë dhe vetëm atëherë kur $g_e \\propto g_\\gamma$; për $\\chi_\\gamma = \\chi$ kjo ndodh kur $R_t$ '
              'është konstant, që është rasti i Teoremës 5 të shënimit të asimilimit. Vërtetimi. Posteriori gausian i dy '
              'koeficientëve ka precizion $[g_e\\ g_\\gamma]^\\top \\Gamma^{-1} [g_e\\ g_\\gamma]$, dhe kufiri i '
              'Cauchy–Schwarz-it është barazim vetëm për vektorë proporcionalë. ∎ Akuiferi e filtron rimbushjen si filtër i '
              'ulët; prandaj, edhe kur $R_t$ ndryshon, kosinusi mund të jetë afër 1 (seksioni 5.3).'),
        ('p', '**Pohimi 4 (filtri Kalman si rast i veçantë dhe si orakull i testit).** Në testin e seksionit 5, kur jepen '
              'shiu dhe ligji i forcimit, gjendja $(h, e)$ është lineare dhe gausiane, dhe kohët e maskat e vëzhgimeve janë të '
              'pavarura nga procesi. Atëherë filtri Kalman me ligjin e vërtetë jep saktësisht $\\hat X_{t_i^-}$, pra objektivin e '
              'PD-NJ-ODE, me kërcimin afin [[kalman]]; prandaj $L^*$ dhe $D(\\theta)$ e Pohimit 1 maten saktë. Vërtetimi. '
              'Filtri Kalman është mesatarja e saktë e kushtëzuar për modelet hapësirë-gjendje lineare e gausiane me gjendje '
              'fillestare gausiane; kushtëzimi nga kohët dhe maskat, që janë të pavarura nga procesi, nuk e prish strukturën '
              'gausiane. ∎'),
        ('p', '**Pohimi 5 (parimi i maksimumit për transportin).** Le të jenë $\\beta^c = 0$, $\\sigma_c = 0$, përmbajtja e '
              'ujit konstante, $0 \\leq c_R \\leq c_s$, kufiri dhe gjendja fillestare në $[0, c_s]$, $I_k \\leq n b_{ow}$ për '
              'trashësinë $b_{ow}$ të shtresës që merr ujin e stuhisë, dhe $\\kappa_c$ e formës '
              '$\\sum_l \\alpha_l \\omega_l e^{-\\omega_l u}$ (zona të palëvizshme). Atëherë zgjidhja e [[transport]]–[[tbc]] '
              'mbetet në $[0, c_s]$.'),
        ('p', 'Vërtetimi. Me vazhdueshmërinë'),
        ('eqn', '\\nabla \\cdot q = \\chi (1 + e) R - \\sum_w Q_w \\delta_w + \\sum_k I_k \\delta(t - T_k) \\chi_{ow},'),
        ('p', 'forma konservative bëhet advektive, me burimet $\\chi (1 + e) R (c_R - c)$ '
              'dhe $I_k \\delta(t - T_k) \\chi_{ow} (c_s - c)$, që e shtyjnë $c$ drejt vlerave në $[0, c_s]$; pusat nuk e ndryshojnë '
              '$c$. Kujtesa është sistemi i zonave të palëvizshme $\\partial_t c_l = \\omega_l (c - c_l)$, që mbeten midis '
              'vlerave të $c$ dhe atyre fillestare. Në një maksimum të brendshëm mbi $c_s$, të gjithë termat e ulin $c$; po '
              'kështu në një minimum nën zero. Kërcimi në $T_k$ është kombinim konveks i $c$ dhe $c_s$. ∎ Një mbyllje e mësuar '
              'e ruan këtë veti vetëm kur shkruhet si divergjencë fluksi që anulohet në $c = 0$ dhe $c = c_s$, ose kur kufizohet '
              'me projeksion.'),
    ]
    return B


def result_blocks(v):
    return [
        ('h', '5. Testi numerik SHIU-GO'),
        ('h2', '5.1 Shtrati i testit'),
        ('p', 'Akuiferi është ai bregdetar linear i ASIMILIMI-GO: 5 km në 25 qeliza, deti si kusht Dirichlet në x = 0, pa '
              'rrjedhje në brendësi, T = 1 000 m²/d, Sy = 0,1, një pus në 1,5 km dhe katër piezometra në 250, 1 250, 2 750 '
              'dhe 4 250 m. Rimbushja vjen nga zinxhiri [[rain]]–[[err]], me $\\bar s$ = 200 mm, $s_w$ = 120 mm, $s_{fc}$ = '
              '130 mm, $k_L$ = 25 mm/d, $b_L$ = 3, $\\tau$ = 20 d (vonesa mesatare 40 ditë), $\\sigma_e$ = 0,25 dhe '
              '$\\tau_e$ = 90 d. Në binjakun e parë, në vitet normale shiu është <<rain_n>> mm në vit dhe rimbushja '
              '<<rech_n>> mm (<<ratio>> e shiut). Në vitin e thatësirës shiu bie në <<rain_d>> mm (<<p_share>> e '
              'normales), ndërsa rimbushja vetëm në <<rech_d>> mm (<<r_share>>): <<carry>> e saj (pa gabimin $e$) është kullim i vitit të mëparshëm që kalon zonën e pangopur me '
              'vonesë (mediana mbi binjakët <<carry_med>>). Një vit i thatë nuk është pra një vit pa rimbushje, dhe kujtesa '
              '[[vadose]] e mban këtë në ekuacione. Ngarkesat vëzhgohen në ditë të rastit me '
              'probabilitet <<pday>> në ditë (mesatarisht çdo <<gapm>> ditë), çdo piezometër me probabilitet <<pwell>>, me '
              'zhurmë <<sigo>> cm. Shiu, evapotranspirimi potencial, niveli i detit dhe pompimi njihen çdo ditë. Pas tre '
              'vitesh pa të dhëna ngarkesash, gjashtë vite (dy të lagura, dy normale, dy të thata) shërbejnë për zbulimin dhe '
              'katër për testin, njëri me thatësirë (40% e shiut normal). Gjithçka u përsërit me <<nseed>> binjakë.'),
        ('p', 'Pesë modele krahasohen në të njëjtat të dhëna. **Ligji i vërtetë** (orakulli) jep parashikimin optimal '
              '(Pohimi 4). **M0** është forcimi i shënimit të asimilimit: rimbushje mesatare konstante plus një anomali '
              'Ornstein–Uhlenbeck, pa informacion nga shiu. **M1** është transferimi linear i shiut me bërthamë Erlang. '
              '**Rruga A** është SDE-ja [[soil]]–[[err]] me gjashtë parametra të panjohur $(s_{fc}, k_L, b_L, \\tau, '
              '\\sigma_e, \\tau_e)$. **Rruga B** është shtesa [[aug]] me nëntë tipare. Të gjitha zbulohen duke minimizuar '
              '[[pred]] mbi vitet e trajnimit.'),
        ('h2', '5.2 Rruga A arrin pothuajse parashikimin optimal'),
        ('b', '**Humbja e parashikimit.** Mbi vitet e testit Rruga A është <<ex_A>> mbi ligjin e vërtetë (<<ex_A_q>> në '
              '25–75% të binjakëve), M1 <<ex_M1>> dhe M0 <<ex_M0>> (Figura {{results}}a). Sipas Pohimit 1 teprica është '
              'largësia nga parashikimi optimal; rrënja e saj mesatare katrore është <<dist_A>> cm për Rrugën A, <<dist_M1>> '
              'cm për M1 dhe <<dist_M0>> cm për M0.'),
        ('b', '**Boshllëqet e gjata.** Kur kalojnë më shumë se 14 ditë pa vëzhgim, gabimi katror i M0 është <<g14_M0>> herë '
              'ai i parashikimit optimal (<<g14_M0cm>> kundrejt <<g14_or>> cm²), i M1 <<g14_M1>> herë dhe i Rrugës A <<g14_A>> '
              'herë (Figura {{results}}b). Këtu duket vlera e ligjit të forcimit: midis vëzhgimeve parashikimi mbështetet '
              'vetëm te forcimi.'),
        ('b', '**Kalibrimi.** Intervalet 90% të ligjit të vërtetë mbulojnë <<cov_or>> të vëzhgimeve dhe ato të Rrugës A '
              '<<cov_A>>. M0 mbulon <<cov_M0>>, sepse e fryn zhurmën për të shpjeguar forcimin që nuk e njeh: intervalet e tij '
              'janë të sigurta, por të gjera.'),
        ('b', '**Rimbushja e rindërtuar.** Korrelacioni i rimbushjes mujore të filtruar me të vërtetën është <<corr_A>> për '
              'Rrugën A (<<corr_or>> me ligjin e vërtetë), <<corr_M1>> për M1 dhe <<corr_M0>> për M0 (Figura {{twin}}).'),
        ('b', '**Çfarë identifikojnë ngarkesat.** Vonesa e zonës së pangopur rikthehet saktë, $\\tau$ = <<a_tau>> ditë (e '
              'vërteta 20; mediana dhe 25–75% e binjakëve), po ashtu shkalla e gabimit $\\sigma_e$ = <<a_sige>> (0,25) dhe kapaciteti '
              'në fushë $s_{fc}$ = <<a_sfc>> mm (130). Parametrat e kullimit jo: $k_L$ = <<a_kL>> mm/d (25) dhe $b_L$ = '
              '<<a_bL>> (3) kompensojnë njëri-tjetrin, dhe $\\tau_e$ = <<a_taue>> ditë (90) mbetet i gjerë. Ngarkesat shohin '
              'rimbushjen e integruar, jo formën e kullimit; forma kërkon të dhëna nga toka (seksioni 5.4).'),
        ('b', '**Ligji i shiut** nga shimatësi rikthehet pothuajse saktë: $c_0$ = <<rl_c0>> (−1,667), $c_1$ = <<rl_c1>> '
              '(0,8), $d_0$ = <<rl_d0>> (2,526), $d_1$ = <<rl_d1>> (0,3).'),
        ('img', 'twin', 16.5),
        ('cap', 'Figura {{twin}}. Një binjak në dy vitet e para të testit (viti 10 është thatësirë). (a) Shiu ditor. (b) '
                'Rimbushja mesatare mujore: e vërteta, Rruga A dhe M0, të dyja të filtruara. (c) Ngarkesa në piezometrin në '
                '1 250 m: e vërteta, vëzhgimet në ditë të rastit, mesatarja e filtrit të Rrugës A me intervalin 90% dhe M0.'),
        ('img', 'results', 17.0),
        ('cap', 'Figura {{results}}. Rezultatet mbi <<nseed>> binjakë. (a) Humbja e parashikimit mbi vitet e testit, sa për '
                'qind mbi ligjin e vërtetë (pikat: binjakët; vija dhe numri sipër: mediana). (b) Gabimi katror mesatar i parashikimit sipas '
                'ditëve nga vëzhgimi i fundit (mediana e binjakëve).'),
        ('h2', '5.3 Rruga B: shtesa dhe zgjedhja shkakësore'),
        ('b', '**Biblioteka lineare nuk e kap pragun.** Rruga B mbetet <<b_ls>> mbi optimumin me të gjitha tiparet, <<b_bic>> '
              'me zgjedhjen BIC dhe <<b_eills4>> me invariancë (γ = 4). Pragu i kullimit dhe kujtesa e tokës janë jolineare '
              'në shi, dhe asnjë kombinim linear i filtrave të shiut nuk i zëvendëson. Struktura fizike e Rrugës A vlen më '
              'shumë se zgjedhja e termave.'),
        ('b', '**Invarianca i heq termat që nuk janë shkaqe.** Vala sezonale cos zgjidhet në <<cos_bic>> të binjakëve me BIC, '
              'në <<cos_e4>> me γ = 4 dhe në <<cos_e16>> me γ = 16; sin bie nga <<sin_bic>> në <<sin_e16>> dhe konstantja nga '
              '<<one_bic>> në <<one_e16>>. Tipari jolinear i tepricës së shiut zgjidhet në <<x40>> të binjakëve (Figura '
              '{{routeB}}a).'),
        ('b', '**Çmimi dhe fitimi.** Mbi të gjithë testin invarianca me γ = 16 humb pak (<<b_eills16>> kundrejt <<b_bic>>), '
              'por në vitin e thatësirës, mjedisin e ri, humbja e parashikimit bie me <<b_drought_gain>> kundrejt BIC. Kjo '
              'është ajo që pritet nga invarianca: pak më pak saktësi brenda klimës së njohur, më shumë qëndrueshmëri '
              'jashtë saj.'),
        ('b', '**Identifikueshmëria (Pohimi 3).** Kosinusi ndërmjet përgjigjes së ngarkesave ndaj një gabimi shumëzues të '
              'rimbushjes dhe ndaj një mbylljeje uniforme është <<cos_m>> pa filtër dhe <<cos_cl>> me filtrin, kështu që '
              'varianca e gabimit zmadhohet rreth <<inf_m>> herë kur të dy vlerësohen bashkë. Për një mbyllje të kufizuar në '
              'kilometrin e parë nga deti, kosinusi bie në <<cos_co>> dhe zmadhimi në <<inf_co>> herë. Kështu paralajmërimi '
              'i N1 merr një numër: me ngarkesa vetëm, një gabim i rimbushjes dhe një term i panjohur uniform janë pothuajse '
              'të pandashëm. Ndahen kur termi i panjohur ka gjurmë hapësinore tjetër ose kur shtohet një lloj tjetër të '
              'dhënash.'),
        ('img', 'routeB', 17.0),
        ('cap', 'Figura {{routeB}}. Rruga B. (a) Sa shpesh zgjidhet çdo tipar me BIC dhe me invariancë (γ = 4); në të '
                'djathtë, në sfond, termat që nuk janë shkaqe. (b) Gabimi i rimbushjes totale në vitin e thatësirës (mediana '
                'dhe 25–75% e binjakëve).'),
        ('h2', '5.4 Rruga A veçmas: SDE-ja e tokës nga lagështia e matur'),
        ('p', 'Pohimi 2 u testua me lagështinë e tokës të simuluar çdo orë për dhjetë vite, me tri skema matjeje.'),
        ('b', '**Sondë orare** (25% e orëve mungojnë, zhurmë 0,3 mm). Kërcimet mbi 2 mm japin intensitetin mujor të shiut me '
              'gabim relativ <<km_lam_err>> (mediana e muajve) (<<km_jn>> kërcime në muaj gjatë dhjetë viteve) dhe thellësinë mesatare në '
              'verë me gabim <<km_ab_sum>>. Në dimër thellësia nënvlerësohet, sepse toka afër ngopjes i cungon kërcimet: '
              'sonda sheh ujin që hyn në tokë, jo shiun. Drifti rikthehet pothuajse saktë: $c_E$ = <<pd_cE>> (1), '
              '$s_{fc}$ = <<pd_sfc>> mm (130), $k_L$ = <<pd_kL>> mm/d (25), $b_L$ = <<pd_bL>> (3), me gabim mesatar të '
              'driftit <<pd_mae>> mm/d (Figura {{km}}).'),
        ('b', '**Raporti i drejtpërdrejtë i momenteve** [[km]] jep në dimër $\\lambda$ = <<kmw_lam>> kundrejt <<kmw_true>> '
              'të vërtetë dhe $\\bar a$ = <<kmw_ab>> kundrejt <<kmw_abt>> mm, për shkak të cungimit; në verë <<kms_lam>> '
              'kundrejt <<kms_true>>. Momentet e larta tregojnë që ka kërcime, por ligjin e tyre e jep më mirë zbulimi i '
              'kërcimeve.'),
        ('b', '**Satelit çdo 3–6 ditë** (20% e kalimeve humbin nga retë, zhurmë 3 mm). Këtu $\\lambda \\Delta \\approx 1$ dhe '
              'vlerësimi Kramers–Moyal nuk ka kuptim: $\\lambda$ del nga <<sat_rng>> në <<sat_n>> muajt ku mund të llogaritet.'),
        ('b', '**Satelit dhe shimatës.** Me shiun ditor si kërcime të njohura, drifti mësohet nga gabimi i parashikimit midis '
              'kalimeve, me gabim mesatar <<sg_mae>> mm/d. Parametrat veçmas jo: $s_{fc}$ = <<sg_sfc>> mm dhe $b_L$ = '
              '<<sg_bL>> dalin në kufijtë e kërkimit.'),
        ('p', 'Rregulli që del për monitorimin: **shimatësi jep kërcimet, sonda orare jep driftin, sateliti me shimatësin jep '
              'funksionin e driftit, ngarkesat japin vonesën dhe shkallën e gabimit.**'),
        ('img', 'km', 17.0),
        ('cap', 'Figura {{km}}. Rruga A veçmas, nga lagështia e tokës. (a) Intensiteti mujor i ngjarjeve të shiut: i vërteti, '
                'nga kërcimet e sondës orare dhe nga koeficientët Kramers–Moyal me satelit çdo 3–6 ditë. (b) Drifti i SDE-së '
                'së tokës në verë dhe në dimër: i vërteti, nga sonda orare dhe nga sateliti me shimatës.'),
    ]


def closing_blocks():
    return [
        ('h', '6. Çfarë është e re (inovacioni SHIU-GO)'),
        ('b', '**Forcimi zbulohet nga parashikimi optimal.** Ligji i shiut, i tokës dhe i rimbushjes zbulohet duke minimizuar '
              'humbjen e PD-NJ-ODE mbi vëzhgime me kohë dhe maska të rastit. Pohimi 1 e lidh tepricën e humbjes me largësinë '
              'nga parashikimi optimal, dhe testi e mat atë: <<dist_A>> cm për Rrugën A kundrejt <<dist_M0>> cm për forcimin '
              'gausian.'),
        ('b', '**Filtri PD-NJ-ODE me fizikë.** Ekuacioni [[filter]] vendos ekuacionet e filtrimit dhe të transportit midis '
              'vëzhgimeve, dhe filtrin Kalman, EnKF-në ose hartën e transportit si kërcim në vëzhgim. Rrjetit neural i mbetet '
              'vetëm korrigjimi, me nënshkrimin e rrugës si hyrje.'),
        ('b', '**Dy rrugë me rregull të dhënash.** Rruga A (SDE veçmas) dhe Rruga B (shtesë) kanë kushte të qarta '
              'identifikimi: Pohimi 2 për SDE-në e tokës, Pohimi 3 për shtesën, dhe rregulli i monitorimit i seksionit 5.4.'),
        ('b', '**Zgjedhja shkakësore e shtesës.** Termat e shtesës zgjidhen me invariancë ndërmjet viteve të lagura, normale '
              'dhe të thata, saktësisht me numërim ose me MIQP. Në test kjo i rralloi valët sezonale dhe e përmirësoi '
              'parashikimin në thatësirë.'),
        ('b', '**Forma të reja të ekuacioneve të filtrimit dhe të transportit.** Ato marrin gabimin shumëzues të rimbushjes, '
              'kujtesën, mbylljen dhe stuhitë si kërcime, që hyjnë njëherësh si ujë në [[flow]] dhe si kripë në '
              '[[transport]]. Parimi i maksimumit (Pohimi 5) jep kushtin që duhet të plotësojë një mbyllje e mësuar.'),
        ('b', '**Nuk pretendohen si të reja:** PD-NJ-ODE dhe teoremat e saj, filtri Kalman dhe EnKF-ja, hartat e transportit, '
              'EILLS dhe MIQP-ja me ℓ₀, koeficientët Kramers–Moyal, modeli i tokës me shi Poisson, bërthama Erlang dhe '
              'gabimi Ornstein–Uhlenbeck. E re është mbledhja e tyre në një sistem për akuiferin bregdetar dhe testi që i '
              'krahason. Kontrolli i risisë mbështetet te materialet e lexuara; duhet përsëritur në bazat bibliografike para '
              'botimit.'),
        ('h', '7. Kufizimet dhe hapat për Fushë-Kuqen'),
        ('b', 'Teoria e Krach et al. (2026) supozon $N$ rrugë të pavarura; në terren ka një histori për çdo pus. Dritaret '
              'kohore ose vitet si rrugë kërkojnë kushte përzierjeje që teoremat nuk i mbulojnë; rruga tjetër është trajnimi '
              'me binjakë të simuluar (Përfundimi 6.2).'),
        ('b', 'Testi përdori rastin afin të filtrit (Kalman), që është i saktë sepse binjaku është linear dhe gausian kur jepet '
              'shiu. Rrjeti neural PD-NJ-ODE dhe korrigjimi me nënshkrim nuk u trajnuan këtu; ato janë hapi i radhës kur '
              'forcimi ose transporti bëhen jolinearë (ndërfaqja, kloruri).'),
        ('b', 'Ekuacioni i transportit, çelësi N2 dhe shiriti N3 nuk u testuan numerikisht në këtë shënim. Në test shiu ishte '
              'i plotë; ditët që mungojnë në regjistrin real trajtohen me pritjen e kushtëzuar nga ligji i shiut.'),
        ('b', 'Për Fushë-Kuqen duhen: shiu ditor nga stacioni më i afërt, evapotranspirimi potencial nga temperatura, '
              'regjistrat e parregullt të ngarkesave, regjistrat e pompimit dhe niveli i detit nga mareografi. Një sondë '
              'lagështie orare në një vend përfaqësues do ta identifikonte formën e kullimit (seksioni 5.4).'),
    ]
