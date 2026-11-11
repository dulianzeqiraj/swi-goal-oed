"""CERTAIN-COAST illustrated guide (English, Word, OMML equations): seawater intrusion, sensors, warnings, earthquakes,
liquefaction and the joint safe window, one computed figure at a time.

usage: python build_guide.py OUT.docx [OUT.pdf]
The PDF (LibreOffice) is made while the headings still have outline levels, so it has bookmarks; the Word file then
loses them (../word_outline.py), so that Word draws no collapse arrow beside the headings.
Figures: guide_figs.py (fig/); results: res/*.mat (guide_compute.m, the open-source MATLAB package run in GNU Octave)
and ../../../tronditja_go/res. Needs pandoc (through ../../../ml_paradigms/word/omml.py)."""
import json
import os
import re
import subprocess
import sys
import tempfile
from math import erfc, log, ceil

import numpy as np
from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from scipy.io import loadmat

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(EXP, 'spiranca_go', 'certain_coast'))
sys.path.insert(1, os.path.join(EXP, 'garancia_go'))
sys.path.insert(2, os.path.join(EXP, 'ml_paradigms', 'word'))
from build_sota import run, para, table, shade, link  # noqa: E402
from word_outline import plain_headings  # noqa: E402
import omml  # noqa: E402
from build_gar_doc import Eqs, borders, no_borders, fixed_widths, numref, mrich, display_eq, rich_cell, cell_par  # noqa: E402

FIG = os.path.join(HERE, 'fig')
RES = os.path.join(HERE, 'res')
TR = os.path.join(EXP, 'tronditja_go', 'res')
NAVY, BLUE2, GREY = '1F3864', '2E6DB4', '52606D'
REPO = 'https://github.com/dulianzeqiraj/certain-coast'

REFS = [
    ('1', 'Bear, J. (1972). Dynamics of Fluids in Porous Media. American Elsevier, New York.', None),
    ('2', 'Henry, H. R. (1964). Effects of dispersion on salt encroachment in coastal aquifers. In: Sea Water in Coastal '
          'Aquifers, U.S. Geological Survey Water-Supply Paper 1613-C, C70–C84.', 'https://doi.org/10.3133/wsp1613C'),
    ('3', 'Voss, C. I., & Souza, W. R. (1987). Variable density flow and solute transport simulation of regional aquifers '
          'containing a narrow freshwater-saltwater transition zone. Water Resources Research 23(10), 1851–1866.',
     'https://doi.org/10.1029/WR023i010p01851'),
    ('4', 'Werner, A. D., & Simmons, C. T. (2009). Impact of sea-level rise on sea water intrusion in coastal aquifers. '
          'Ground Water 47(2), 197–204.', 'https://doi.org/10.1111/j.1745-6584.2008.00535.x'),
    ('5', 'Werner, A. D., et al. (2013). Seawater intrusion processes, investigation and management: recent advances and '
          'future challenges. Advances in Water Resources 51, 3–26.', 'https://doi.org/10.1016/j.advwatres.2012.03.004'),
    ('6', 'Schmorak, S., & Mercado, A. (1969). Upconing of fresh water–sea water interface below pumping wells, field '
          'study. Water Resources Research 5(6), 1290–1311.', 'https://doi.org/10.1029/WR005i006p01290'),
    ('7', 'Dagan, G., & Bear, J. (1968). Solving the problem of local interface upconing in a coastal aquifer by the '
          'method of small perturbations. Journal of Hydraulic Research 6(1), 15–44.',
     'https://doi.org/10.1080/00221686809500218'),
    ('8', 'Zeqiraj, D. (2026). Goal-oriented Bayesian experimental design for variable-density seawater intrusion: '
          'adjoint expected information gain for joint monitoring and managed-aquifer-recharge placement. Journal of '
          'Hydrology 680, 136559.', 'https://doi.org/10.1016/j.jhydrol.2026.136559'),
    ('9', 'Chaloner, K., & Verdinelli, I. (1995). Bayesian experimental design: a review. Statistical Science 10(3), '
          '273–304.', 'https://doi.org/10.1214/ss/1177009939'),
    ('10', 'Slepian, D. (1962). The one-sided barrier problem for Gaussian noise. Bell System Technical Journal 41(2), '
           '463–501.', 'https://doi.org/10.1002/j.1538-7305.1962.tb02419.x'),
    ('11', 'Healy, R. W., & Cook, P. G. (2002). Using groundwater levels to estimate recharge. Hydrogeology Journal '
           '10(1), 91–109.', 'https://doi.org/10.1007/s10040-001-0178-0'),
    ('12', 'Vovk, V., Gammerman, A., & Shafer, G. (2005). Algorithmic Learning in a Random World. Springer, New York.',
     'https://doi.org/10.1007/b106715'),
    ('13', 'Clopper, C. J., & Pearson, E. S. (1934). The use of confidence or fiducial limits illustrated in the case of '
           'the binomial. Biometrika 26(4), 404–413.', 'https://doi.org/10.1093/biomet/26.4.404'),
    ('14', 'Okada, Y. (1985). Surface deformation due to shear and tensile faults in a half-space. Bulletin of the '
           'Seismological Society of America 75(4), 1135–1154.', 'https://doi.org/10.1785/BSSA0750041135'),
    ('15', 'Ganas, A., et al. (2020). Ground deformation and seismic fault model of the M6.4 Durres (Albania) Nov. 26, '
           '2019 earthquake, based on GNSS/InSAR observations. Geosciences 10, 210.',
     'https://doi.org/10.3390/geosciences10060210'),
    ('16', 'Govorčin, M., et al. (2020). Geodetic source modeling of the 2019 Mw 6.3 Durrës, Albania, earthquake: partial '
           'rupture of a blind reverse fault. Geophysical Research Letters 47, e2020GL088990.',
     'https://doi.org/10.1029/2020GL088990'),
    ('17', 'Matraku, K., et al. (2023). The 26 November 2019 Durrës earthquake, Albania: coseismic displacements and '
           'occurrence of slow slip events in the year following the earthquake. Geophysical Journal International 234, '
           '807–838.', 'https://doi.org/10.1093/gji/ggad101'),
    ('18', 'van der Heiden, V., et al. (2026). Analysis of the 2019 Mw 6.4 Durrës, Albania, aftershock sequence: basement '
           'involved thrusting at the eastern Adriatic plate margin. Geophysical Journal International 246, ggag155.',
     'https://doi.org/10.1093/gji/ggag155'),
    ('19', 'Wang, C.-Y., & Manga, M. (2021). Water and Earthquakes. Springer International Publishing.',
     'https://doi.org/10.1007/978-3-030-64308-9'),
    ('20', 'Rice, J. R., & Cleary, M. P. (1976). Some basic stress diffusion solutions for fluid-saturated elastic porous '
           'media with compressible constituents. Reviews of Geophysics 14, 227–241.',
     'https://doi.org/10.1029/rg014i002p00227'),
    ('21', 'Boulanger, R. W., & Idriss, I. M. (2014). CPT and SPT based liquefaction triggering procedures. Report '
           'UCD/CGM-14/01, Center for Geotechnical Modeling, University of California, Davis.', None),
    ('22', 'Boulanger, R. W., & Idriss, I. M. (2016). CPT-based liquefaction triggering procedure. Journal of '
           'Geotechnical and Geoenvironmental Engineering 142, 04015065.',
     'https://doi.org/10.1061/(asce)gt.1943-5606.0001388'),
    ('23', 'Maurer, B. W., et al. (2014). Evaluation of the liquefaction potential index for assessing liquefaction '
           'hazard in Christchurch, New Zealand. Journal of Geotechnical and Geoenvironmental Engineering 140, 04014032.',
     'https://doi.org/10.1061/(asce)gt.1943-5606.0001117'),
    ('24', 'Mavroulis, S., Lekkas, E., & Carydis, P. (2021). Liquefaction phenomena induced by the 26 November 2019, '
           'Mw = 6.4 Durrës (Albania) earthquake and liquefaction susceptibility assessment in the affected area. '
           'Geosciences 11, 215.', 'https://doi.org/10.3390/geosciences11050215'),
    ('25', 'Befus, K. M., et al. (2020). Increasing threat of coastal groundwater hazards from sea-level rise in '
           'California. Nature Climate Change 10, 946–952.', 'https://doi.org/10.1038/s41558-020-0874-1'),
    ('26', 'Grant, A. R. R., et al. (2021). Changes in liquefaction severity in the San Francisco Bay Area with sea-level '
           'rise. Geo-Extreme 2021, 308–317.', 'https://doi.org/10.1061/9780784483695.030'),
]


# ------------------------------------------------------------------------------------------------ numbers
def numbers_from_results():
    m = lambda n: loadmat(os.path.join(RES, n + '.mat'), squeeze_me=True)  # noqa: E731
    H, Q, S, B, A, R_, BD, F = (m('henry'), m('henry_inflow'), m('sensors_henry'), m('between'), m('alarm'),
                                m('recharge'), m('boundary'), m('fushe_kuqe'))
    TJ = json.load(open(os.path.join(TR, 'tronditja.json')))
    N = {}
    N['henry'] = [(int(s[0]), int(s[1]), float(t), float(r), float(c)) for s, t, r, c in
                  zip(H['sizes'], H['toes'], H['resid'], H['secs'])]
    N['toe81'] = float(H['toes'][-1])
    N['secs81'] = float(H['secs'][-1])
    qf, toe = np.atleast_1d(Q['qf']), np.atleast_1d(Q['toeQ'])
    N['w06'], N['w10'], N['w14'] = (2.0 - float(toe[np.argmin(abs(qf - v))]) for v in (0.6, 1.0, 1.4))
    K, L, d = 30.0, 2000.0, 0.025
    lens = lambda x, W: np.sqrt(2 * W / (K * (1 + 1 / d)) * (L * x - x ** 2 / 2))  # noqa: E731
    N['h200'] = float(lens(L, 0.2 / 365.25))
    N['z200'] = N['h200'] / d
    N['dz'] = (N['h200'] - float(lens(L, 0.1 / 365.25))) / d
    N['qmax'] = 0.6 * np.pi * 20.0 ** 2 * 50.0 * 0.025
    N['area'], N['cells'] = float(F['baseArea']), int(F['nCells'])
    N['fk_top'], N['fk_greedy'] = float(F['topGain']), float(F['greedyGain'])
    N['fk_greedy_ids'] = ', '.join(map(str, np.atleast_1d(F['greedyID'])))
    AR, EQ = m('alarm_reliability'), m('equifinality')
    N['rel_alpha'] = [float(v) for v in np.atleast_1d(AR['alphas'])]
    N['rel_mean'] = [float(v) for v in AR['missRate'].mean(0)]
    N['rel_nrep'], N['rel_ncal'] = int(AR['nRep']), int(AR['nCal'])
    N['eq_cum1'], N['eq_cum2'], N['eq_maxdh'] = float(EQ['cum1'][-1]), float(EQ['cum2'][-1]), float(EQ['maxdh'])
    N['mon'] = ', '.join(map(str, np.atleast_1d(F['monID'])))
    N['mar'] = ', '.join(map(str, np.atleast_1d(F['marID'])))
    g, rnd = np.atleast_1d(S['greedyCurve']), S['randGains']
    N['g1'], N['g6'], N['r1'], N['r6'] = float(g[0]), float(g[-1]), float(np.median(rnd[:, 0])), float(np.median(rnd[:, -1]))
    N['g3'], N['r3'] = float(g[2]), float(np.median(rnd[:, 2]))
    x = 180 + 35 * B['pathX']
    over = x >= 250
    N['ncross'] = int(np.sum(np.diff(over.astype(int)) == 1))
    N['tail'] = 0.5 * erfc(2 / np.sqrt(2))
    N['truth'] = float(B['truthP'])
    lo, hi = np.median(B['bandLo'], 0), np.median(B['bandHi'], 0)
    N['bands'] = [(float(a), float(b)) for a, b in zip(lo, hi)]
    cover = [np.mean((B['bandLo'][:, j] <= N['truth']) & (B['bandHi'][:, j] >= N['truth'])) for j in range(4)]
    N['cover_min'], N['cover_max'] = 100 * min(cover), 100 * max(cover)
    e = R_['Rhat'][1:] - R_['Rtrue'][1:]
    N['derr'] = float(np.sqrt(np.mean(e ** 2)))
    N['rain'] = float(R_['Pr'].sum() / 3)
    N['rech'] = float(R_['Rtrue'].sum() / 3)
    n = R_['Pr'].size
    edges = np.arange(1, n + 30, 30)
    edges[-1] = n
    mt = np.add.reduceat(R_['Rtrue'][1:], edges[:-1] - 1)[:len(edges) - 1]
    mh = np.add.reduceat(np.nan_to_num(R_['Rhat'][1:]), edges[:-1] - 1)[:len(edges) - 1]
    N['merr'], N['mmean'] = float(np.sqrt(np.mean((mh - mt) ** 2))), float(np.mean(mt))
    rms = lambda a: float(np.sqrt(np.mean((a - BD['bRef']) ** 2)))  # noqa: E731
    N['bl'], N['bn'], N['bf'], N['ncomp'] = rms(BD['bL']), rms(BD['bN']), rms(BD['bF']), int(BD['nComp'])
    N['margin'], N['nev'], N['nmiss'], N['nfalse'], N['bound'] = (float(A['margin']), int(A['nEvents']),
                                                                    int(A['nMiss']), int(A['nFalse']), float(A['bound']))
    N['n_cp'] = int(ceil(log(0.05) / log(0.9)))
    E2 = TJ['E2']
    N['k_conf'], N['k_soft'] = E2['dh_per_areal_microstrain_m']['confined'], E2['dh_per_areal_microstrain_m']['soft']
    N['k_ratio'] = E2['kappa_kPa']['confined'] / E2['kappa_kPa']['soft']
    N['dh_min'] = [s_['dh_conf_min_m'] for s_ in E2['sources']]
    N['dh_max'] = [s_['dh_conf_max_m'] for s_ in E2['sources']]
    N['soft_min'] = [s_['dh_soft_min_m'] for s_ in E2['sources']]
    N['fall'] = (min(-v for v in N['dh_min']), max(-v for v in N['dh_min']))
    N['rise'] = (min(N['dh_max']), max(N['dh_max']))
    N['agree'] = 100 * E2['sign_agreement_where_any_ea_gt_big']
    N['uz_up'] = (min(s_['uz_max_m'] for s_ in E2['sources']), max(s_['uz_max_m'] for s_ in E2['sources']))
    N['uz_down'] = (min(-s_['uz_min_m'] for s_ in E2['sources']), max(-s_['uz_min_m'] for s_ in E2['sources']))
    N['share'] = {k: 100 * v for k, v in E2['share_left_after_15s'].items()}
    N['share1'] = 100 * E2['share_left_after_15s']['1 m']
    nt = E2['natural_test']
    N['ci_q'], N['ci_s'], N['ratio'] = nt['ci95_quake_d'], nt['ci95_season_d'], nt['width_ratio']
    E1 = TJ['E1']
    N['lpi'] = {k: v['lpi'] for k, v in E1['example'].items()}
    N['slope'], N['slope_wrong'], N['under'] = (E1['lpi_slope_per_m']['right'], E1['lpi_slope_per_m']['renormalised'],
                                                100 * E1['lpi_slope_per_m']['understated'])
    N['fd_err'] = E1['dlnfs_max_rel_err']
    E4 = TJ['E4']
    win = {round(w['amax'], 2): w['eta_close'] for w in E4['window_table']}
    N['eta20'], N['eta18'] = win[0.2], win[0.18]
    N['pmin'], N['pmax'] = E4['bulletin']['pexc_min'], E4['bulletin']['pexc_max']
    N['zw_range'] = E4['bulletin']['zw_range']
    return N


# ------------------------------------------------------------------------------------------------ text
def blocks(N):
    f2 = lambda v: f'{v:.2f}'  # noqa: E731
    B = []
    a = B.append
    # ---- title page
    a(('title', 'Seawater intrusion, sensors, earthquakes and liquefaction'))
    a(('subtitle', 'An illustrated guide to the CERTAIN-COAST methods, with their equations'))
    a(('byline', 'Dulian Zeqiraj · Faculty of Geology and Mining, Polytechnic University of Tirana · '
                 'NATO Science for Peace and Security application CERTAIN-COAST · November 2026'))
    a(('bbox', ['**What this guide is.** One figure at a time, it explains how CERTAIN-COAST watches a low coast where four '
                'threats share one cause: salt water entering the drinking-water wells, earthquakes, liquefaction of the '
                'sandy ground and extreme sea levels. Each chapter states the physics in a few equations, shows in a '
                'figure what they predict, and ends with what the project adds to current practice.',
                '**Every figure is computed.** By the open-source MATLAB code of the project, which also runs in the free '
                f'GNU Octave ([{REPO}]({REPO})), by the preparatory tests of the project team, or by the published model '
                'of the Fushë-Kuqe aquifer. Appendix A lists the source and the check of each figure. Where a figure '
                'uses illustrative soils, sources or ports, the caption says so.',
                '**How to read the equations.** They are written in Word’s own equation format and numbered on the '
                'right. Each symbol is explained the first time it appears; the figures can be read without them.']))
    a(('pb',))
    a(('contents',))
    a(('box', ['**The innovations at a glance.**',
               '1.  One state variable, the water table of the day, couples seawater intrusion, liquefaction, '
               'earthquakes and extreme sea levels, so one model and one network serve them all (Chapter 1).',
               '2.  An open-source variable-density model with a fast sparse Jacobian and two adjoint solves for every '
               'sensitivity, reproducing the published Henry and Fushë-Kuqe results (Chapter 2).',
               '3.  Sensors chosen for the decision; a warning band for crossings between samples; recharge read from '
               'the loggers; a model boundary learned from two piezometers (Chapter 3).',
               '4.  Warnings whose miss rate is stated in advance and checked against every logged outcome (Chapter 4).',
               '5.  The pressure step of an earthquake set by the shear modulus of the layer, and the earthquake used as '
               'a free pumping test (Chapter 5).',
               '6.  Liquefaction computed with the water table and pore pressure of the day (Chapter 6).',
               '7.  One safe window for intrusion and liquefaction, with the sea-level rise at which it closes, and a '
               'daily bulletin (Chapter 7).']))
    a(('pb',))

    # ---- 1
    a(('h', '1  One coast, one sea level'))
    a(('p', 'On the coast between Durrës and Fushë-Kuqe, and near Fier where the TAP gas pipeline comes ashore, the land '
            'is low, it subsides, and the sea is rising. The water table lies a few metres below the ground and a few '
            'decimetres above sea level. That single fact links four hazards that are usually studied by four different '
            'offices (Figure {{fig01_system}}).'))
    a(('b', '**Seawater intrusion.** Fresh groundwater floats on the denser sea water. When pumping or a drought lowers '
            'the water table, the salt water rises towards the screens of the supply wells [4, 5].'))
    a(('b', '**Liquefaction.** Loose, saturated sand loses its strength when an earthquake shakes it. The shallower the '
            'water table, the more sand is saturated and the weaker it is [25, 26].'))
    a(('b', '**Earthquakes.** A strong earthquake also squeezes or stretches the aquifer and changes its water pressure '
            'within seconds. The Mw 6.4 Durrës earthquake of 26 November 2019 caused liquefaction along this coast [24].'))
    a(('b', '**Extreme sea levels.** Storm surges and the rising mean sea level push the water table up from below and '
            'flood the port and the landfall.'))
    a(('p', 'The common driver is the relative sea level, the rise of the sea plus the sinking of the land:'))
    a(('eq', 'rsl', r'\eta_{\mathrm{rel}}(t) = \eta_{\mathrm{sea}}(t) + s(t)'))
    a(('p', r'where $\eta_{\mathrm{sea}}$ is the sea level, from tide-gauge and satellite records, and $s$ the subsidence measured by '
            'GNSS and satellite radar. A higher relative sea level lifts the water table: good for keeping salt out of '
            'the wells, bad for liquefaction. Pumping lowers it: good for liquefaction, bad for intrusion. A safe '
            'operation must keep the water table inside a window, and Chapter 7 computes that window.'))
    a(('img', 'fig01_system', 15.5))
    a(('cap', 'Figure {{fig01_system}}. The coast as one system. The relative sea level drives the water table; the '
              'water table controls intrusion and liquefaction; earthquakes add a sudden pressure step; the sensors feed '
              'one model and one alarm, whose miss rate is stated before it is used and checked against every logged '
              'outcome.'))
    a(('box', ['**Innovation.** The four hazards are coupled through one state variable, the water table of the day, so '
               'one model and one monitoring network serve all of them. Current practice keeps separate models for '
               'groundwater, for geotechnics and for coastal flooding, each blind to the variable that drives the '
               'others.']))

    # ---- 2
    a(('pb',))
    a(('h', '2  Seawater intrusion'))
    a(('h2', '2.1  The 1 : 40 rule'))
    a(('p', 'Sea water is about 2.5% denser than fresh water. In a coastal aquifer the fresh water forms a lens that '
            'floats on the salt water, in balance like a ship on the sea. Ghyben and Herzberg found the depth $z$ of the '
            'fresh–salt interface below sea level from the height $h$ of the water table above sea level [1]:'))
    a(('eq', 'gh', r'z = \frac{\rho_f}{\rho_s - \rho_f}\, h \approx 40\, h'))
    a(('p', r'with $\rho_f$ = 1000 kg/m³ and $\rho_s$ = 1025 kg/m³. Every centimetre of water table above sea level '
            'holds 40 centimetres of fresh water below it. The rule works both ways: a pumping well that lowers the water '
            'table by 0.25 m lets the salt water rise by 10 m. With horizontal flow (the Dupuit approximation) and a '
            'recharge $N$ falling on a strip of width $L$ between the coast and the groundwater divide, the water table at '
            'a distance $x$ from the coast is [1]'))
    a(('eq', 'lens', r'h(x)^2 = \frac{2N}{K\,(1 + 1/\delta)} \left( L\, x - \frac{x^2}{2} \right), \qquad '
                     r'\delta = \frac{\rho_s - \rho_f}{\rho_f}'))
    a(('p', f'where $K$ is the hydraulic conductivity. Figure {{{{fig02_lens}}}} uses $K$ = 30 m/day, $L$ = 2 km and '
            f'$\\delta$ = 0.025. With 200 mm/year of recharge the water table rises to {N["h200"]:.2f} m and the fresh '
            f'water reaches {N["z200"]:.0f} m below sea level. Half the recharge, the result of a drought or of pumping '
            f'the same amount, lifts the interface by {N["dz"]:.0f} m everywhere along the strip.'))
    a(('img', 'fig02_lens', 16.0))
    a(('cap', 'Figure {{fig02_lens}}. The freshwater lens of a coastal strip, to scale, from equations [[gh]] and '
              '[[lens]]. The dashed lines are the water table, a metre above the sea; the solid lines are the interface, '
              'forty times deeper. The shaded band is the fresh water lost when the recharge is halved.'))
    a(('h2', '2.2  The salt wedge in a variable-density model'))
    a(('p', 'The sharp interface ignores mixing. The CERTAIN-COAST model solves the full variable-density equations: the '
            'flow of water whose density depends on its salt content, and the transport of the salt by the flow and by '
            r'diffusion [3]. With the equivalent freshwater head $h$ and the relative salinity $c$ (0 for fresh water, '
            '1 for sea water):'))
    a(('eq', 'flow', r'\nabla \cdot \mathbf{q} = 0, \qquad \mathbf{q} = -K \left( \nabla h + \varepsilon\, c\, '
                     r'\mathbf{e}_z \right)'))
    a(('eq', 'transport', r'\nabla \cdot \left( \mathbf{q}\, c \right) - \nabla \cdot \left( \phi D\, \nabla c '
                          r'\right) = 0'))
    a(('p', r'where $\mathbf{q}$ is the Darcy flux, $\varepsilon$ = 0.025 the density contrast, $\mathbf{e}_z$ the '
            r'upward unit vector, $\phi$ the porosity and $D$ the diffusivity. The buoyancy term $\varepsilon c\, '
            r'\mathbf{e}_z$ makes the salt water sink and creep inland along the base of the aquifer. The standard test '
            'of such codes is the Henry problem [2]: a vertical section 2 m long and 1 m high, fresh water flowing in '
            r'from the left, the sea on the right, and the Henry number $\phi D / Q$ = 0.1, where $Q$ is the freshwater '
            'inflow.'))
    a(('img', 'fig03_henry', 16.0))
    a(('cap', f'Figure {{{{fig03_henry}}}}. The Henry benchmark computed by the certaincoast.model package on 81 × 41 '
              f'cells: relative salinity (colour), the 0.1, 0.5 and 0.9 isochlors (lines) and the Darcy flux (arrows). '
              f'Fresh water flows to the sea above the wedge; sea water enters below it, mixes and returns. The toe, '
              f'where the 0.5 isochlor meets the base, is {N["toe81"]:.4f} m from the inland boundary.'))
    a(('p', 'Table {{t_henry}} shows that the toe converges as the grid is refined and that the solver brings the '
            'residual down to round-off. The values agree with those published by Zeqiraj (2026) [8] to the fourth '
            'decimal. The solver uses a sparse Jacobian built with only 27 evaluations of the residual (coloured finite '
            'differences), so even the finest grid takes a few seconds in the free GNU Octave.'))
    a(('cap', 'Table {{t_henry}}. Grid convergence of the Henry benchmark (GNU Octave 8.4, one core).'))
    rows = [[f'{nx} × {ny}', f'{toe:.4f}', f'{toe / 2:.3f}', f'{res:.1e}', f'{sec:.1f}'] for nx, ny, toe, res, sec
            in N['henry']]
    a(('table', ['Grid (cells)', 'Toe (m)', 'Toe / length', 'Residual', 'Time (s)'], rows, [3.4, 2.8, 3.0, 3.0, 2.6], 10))
    a(('p', 'Less fresh water means a longer wedge. Figure {{fig04_inflow}} repeats the computation with 0.6 to 1.4 times '
            f'the Henry inflow, as if pumping or a drought took part of it: with 60% of the inflow the wedge reaches '
            f'{N["w06"]:.2f} m inland instead of {N["w10"]:.2f} m; with 140% it shrinks to {N["w14"]:.2f} m. This is '
            'the response that the warnings of Chapter 4 must catch in time, and it is fastest at the base of the '
            'aquifer, where the wells draw the water.'))
    a(('img', 'fig04_inflow', 16.0))
    a(('cap', 'Figure {{fig04_inflow}}. (a) The 0.5 isochlor for 0.6, 1.0 and 1.4 times the Henry inflow (41 × 21 cells). '
              '(b) Length of the salt wedge at the base, measured from the sea, against the inflow.'))
    a(('h2', '2.3  Upconing below a pumping well'))
    a(('p', r'A well pumping above the interface draws the salt water up into a cone. For a well whose bottom is a '
            r'height $d$ above the interface, the steady rise of the interface below the well is [6, 7]'))
    a(('eq', 'upcone', r'z = \frac{Q}{2\pi\, d\, K\, \delta}, \qquad Q_{\max} = 0.6\, \pi\, d^2 K\, \delta'))
    a(('p', f'The cone is stable only while $z$ stays below about $0.3\\,d$; beyond that the salt water rises into the '
            f'well, which gives the largest safe pumping rate $Q_{{\\max}}$. Figure {{{{fig05_upconing}}}} gives '
            f'$Q_{{\\max}}$ = {N["qmax"]:.0f} m³/day for $K$ = 50 m/day and $d$ = 20 m. The rule is simple, but it needs '
            '$d$, the depth of the interface below each well, which is what the monitoring network of Chapter 3 is '
            'designed to measure.'))
    a(('img', 'fig05_upconing', 15.0))
    a(('cap', 'Figure {{fig05_upconing}}. (a) Upconing of the interface below a well (schematic). (b) Rise of the interface '
              'below the well, as a fraction of the distance $d$, against the pumping rate, from equation [[upcone]]; '
              'beyond 0.3 the cone is unstable.'))
    a(('h2', '2.4  The Fushë-Kuqe aquifer'))
    a(('p', 'The same physics, on the real aquifer north of Durrës, is the published model of Zeqiraj (2026) [8]: '
            'confined flow on the real polygon with cells of 0.25 km, the conductivity interpolated from the 43 wells '
            r'where it was measured, the sea along the western margin, and a cell counted as intruded when its head '
            r'falls below $\delta$ times the depth of the aquifer base, that is 1.0 m. Recomputed with the project’s '
            f'MATLAB code, the intruded zone covers {N["area"]:.1f} km² of the {0.0625 * N["cells"]:.0f} km² aquifer '
            f'({N["cells"]} active cells; Figure {{{{fig06_fushe_kuqe}}}}a).'))
    a(('p', 'Figure {{fig06_fushe_kuqe}}b shows where a new head reading would say most about the intruded area, with the '
            f'five monitoring wells and the three recharge sites of the published design: monitoring {N["mon"]}; '
            f'recharge {N["mar"]}. The recomputation reproduces the published result exactly. The published design '
            'takes the five cells that are best one by one. Choosing five of the 32 measured wells together, with the '
            f'greedy design of Chapter 3, raises the information about the intruded area from {N["fk_top"]:.2f} to '
            f'{N["fk_greedy"]:.2f} nats, because sensors chosen together do not repeat each other.'))
    a(('img', 'fig06_fushe_kuqe', 16.0))
    a(('cap', 'Figure {{fig06_fushe_kuqe}}. The Fushë-Kuqe aquifer. (a) Heads of the steady model and the intruded zone '
              '(head below 1 m, red). (b) Information about the intruded area gained by one head reading in each cell, '
              'with the published monitoring wells and managed-recharge (MAR) sites. Data: Albanian Geological Survey '
              'and Prof. A. Beqiraj, used with their permission; model and design of Zeqiraj (2026) [8].'))
    a(('box', [f'**Innovation.** A variable-density model whose Jacobian needs 27 evaluations of the residual instead of '
               f'one per unknown, so the 81 × 41 Henry section is solved in {N["secs81"]:.1f} s in the free GNU Octave; '
               'the same derivatives give, from two adjoint solves, every sensitivity that the network design of Chapter '
               '3 needs. The model is open source and needs no licence, so the end-user can run it.']))

    # ---- 3
    a(('pb',))
    a(('h', '3  Sensors: what to measure, and where'))
    a(('p', 'Table {{t_sensors}} lists the measurements of CERTAIN-COAST and what each one tells the system. Most of '
            'them serve more than one hazard: the same logger that watches a well for salt records the water table that '
            'drives liquefaction and the pressure step of an earthquake.'))
    a(('cap', 'Table {{t_sensors}}. The measurements of CERTAIN-COAST and what each one tells.'))
    a(('table', ['Measurement', 'What it records', 'What it tells the system', 'Chapter'],
       [['Pressure, conductivity and temperature loggers, every 15 minutes', 'head, salinity, temperature',
         'the water table of the day; salinity between laboratory samples; recharge; the earthquake step and its '
         'relaxation', '3, 5, 6'],
        ['Laboratory analyses', 'chloride and major ions',
         'the salinity alarm; the origin of the salt; the calibration of the loggers', '3, 4'],
        ['Two piezometers next to the inland cut of the model', 'heads', 'the learned inland boundary', '3'],
        ['Pumping tests', 'conductivity, specific yield', 'the anchor that fixes recharge; the distance d for upconing',
         '2, 3'],
        ['GNSS stations and radar corner reflectors', 'vertical land motion',
         'subsidence s(t) in the relative sea level; the uplift of an earthquake', '1, 5'],
        ['Sea-level records (public data)', 'sea level', 'the sea level of equation [[rsl]]', '1, 7'],
        ['Seismic stations and temporary nodes', 'ground motion, ambient noise',
         'the acceleration for the liquefaction bulletin; the stiffness of the shallow ground', '5, 6, 7']],
       [4.2, 3.3, 7.4, 2.1], 9.5))
    a(('h2', '3.1  Sensors chosen for the decision'))
    a(('p', 'A monitoring network is usually designed to see everything. CERTAIN-COAST designs it for a decision: is the '
            'salt approaching the wells? A sensor is worth what it tells about that question, the goal, not what it '
            r'tells about the aquifer as a whole. Let the uncertain parameters $\theta$ have the prior covariance '
            r'$\Gamma$, let the sensors read $G\theta$ plus noise of covariance $\Gamma_n$, and let the goal be '
            r'$H\theta$. The information that the sensors give about the goal is [8, 9]'))
    a(('eq', 'eig', [r'I_F = H\Gamma G^{\top} \left( G\Gamma G^{\top} + \Gamma_n \right)^{-1} G\Gamma H^{\top}',
                     r'\mathrm{EIG} = -\frac{1}{2} \ln \left( 1 - \frac{I_F}{H\Gamma H^{\top}} \right)']))
    a(('p', r'measured in nats (one nat divides the standard deviation of the goal by $e$, about 2.7). The sensitivities $G$ and $H$ come '
            r'from two adjoint solves of the model, however many parameters there are: with $J$ the Jacobian of the '
            r'model equations $R$, $O$ the observations and $u$ the state,'))
    a(('eq', 'adj', r'J^{\top} \lambda = \left( \frac{\partial O}{\partial u} \right)^{\top}, \qquad '
                    r'G = -\lambda^{\top} \frac{\partial R}{\partial \theta}'))
    a(('p', r'and the same with the goal in place of $O$ gives $H$. Figure {{fig07_sensor_map}} applies this to the Henry '
            r'section with an uncertain conductivity field (standard deviation 0.5 in $\ln K$, correlation length 0.4 m) '
            'and a salinity sensor with 2% noise. The goal is the salt mass in the zone of the toe. The most informative '
            'places lie where the salinity changes fastest, along the 0.5 isochlor near the base.'))
    a(('img', 'fig07_sensor_map', 16.0))
    a(('cap', 'Figure {{fig07_sensor_map}}. Information about the salt mass in the dashed zone given by one salinity sensor '
              'in each cell of the Henry section (32 × 16 cells), with the isochlors. The numbered circles are the first '
              'six sensors chosen one at a time for the goal (greedy design).'))
    a(('p', f'Figure {{{{fig08_returns}}}} compares that design with 300 random designs of the same size. One well-placed '
            f'sensor gives {N["g1"]:.2f} nats, the median random sensor {N["r1"]:.2f}. Three sensors chosen for the goal '
            f'give {N["g3"]:.2f} nats against a median of {N["r3"]:.2f}; six give {N["g6"]:.2f} against {N["r6"]:.2f}, '
            'so six random sensors are worth less than one good one. The curve also flattens after the third sensor, '
            'which tells the operator when to stop buying sensors.'))
    a(('img', 'fig08_returns', 12.5))
    a(('cap', 'Figure {{fig08_returns}}. Information about the goal against the number of sensors: the goal-oriented '
              '(greedy) design and 300 random designs for each size.'))
    a(('h2', '3.2  What happens between two samples'))
    a(('p', 'Chloride is usually measured in the laboratory every few weeks or months, and the limit for drinking water '
            f'is 250 mg/L. Can the chloride cross the limit between two samples? Figure {{{{fig09_between_path}}}}a '
            'simulates a year of chloride with a mean of 180 mg/L, a standard deviation of 35 mg/L and a correlation time '
            f'of 8 days: it crosses the limit {N["ncross"]} times and none of the four quarterly samples sees it. The '
            'chloride anomaly is modelled as an Ornstein–Uhlenbeck process, the simplest random process with a memory:'))
    a(('eq', 'ou', r'dX = -\kappa\, X\, dt + \sqrt{2\kappa}\; dW'))
    a(('p', r'where $1/\kappa$ is the correlation time and $W$ a Brownian motion. The probability that the limit, $\ell$ '
            r'standard deviations above the mean, is crossed at some time in a season of length $T$ is larger than what '
            'the samples alone suggest, and it grows as the chloride changes faster (Slepian’s inequality [10]):'))
    a(('eq', 'cross', r'p = P\left( \max_{0 \le t \le T} X(t) \ge \ell \right) \ge 1 - \Phi(\ell)'))
    a(('p', f'where $\\Phi$ is the standard normal distribution. With $\\ell$ = 2 the samples alone suggest '
            f'$1 - \\Phi(2)$ = {N["tail"]:.3f}; over a season of 120 days the true probability is {N["truth"]:.2f} '
            '(Figure {{fig09_between_path}}b).'))
    a(('img', 'fig09_between_path', 16.0))
    a(('cap', 'Figure {{fig09_between_path}}. (a) One simulated year of chloride (every 6 hours) and four quarterly '
              'samples. (b) Probability that the limit is crossed in a 120-day season, against the correlation time; '
              'the dashed line is what the samples alone suggest.'))
    a(('p', r'The probability depends on the correlation time, which must be estimated from the record. One pair of '
            r'samples a lag $\Delta t$ apart carries the Fisher information'))
    a(('eq', 'pair', r'I_{\Delta t}(\kappa) = \frac{\Delta t^2 \rho^2 \left( 1 + \rho^2 \right)}{\left( 1 - \rho^2 '
                     r'\right)^2}, \qquad \rho = e^{-\kappa\, \Delta t}'))
    q, mo, w, dl = N['bands']
    a(('p', 'which collapses once the lag exceeds the correlation time (Figure {{fig10_between_bands}}b): quarterly '
            'samples say almost nothing about a chloride that changes in days. CERTAIN-COAST therefore reports a band: '
            'the smallest and the largest crossing probability over all the time scales the record allows. With eight '
            f'years of quarterly samples the median band is {q[0]:.2f}–{q[1]:.2f}, useless for a decision; monthly '
            f'samples give {mo[0]:.2f}–{mo[1]:.2f}, weekly samples {w[0]:.2f}–{w[1]:.2f} and a daily logger '
            f'{dl[0]:.2f}–{dl[1]:.2f} (Figure {{{{fig10_between_bands}}}}a). Over 40 simulated records per design the '
            f'band covered the true value in {N["cover_min"]:.0f}–{N["cover_max"]:.0f}% of them.'))
    a(('img', 'fig10_between_bands', 16.0))
    a(('cap', 'Figure {{fig10_between_bands}}. (a) Median warning band over 40 eight-year records for each sampling design, '
              'and the true probability. (b) Fisher information on the time scale carried by one pair of samples, '
              'against the lag between them (equation [[pair]], correlation time 8 days).'))
    a(('h2', '3.3  Recharge from the heads of a well'))
    a(('p', r'A logger of the water level also measures recharge. From one day to the next the head rises with the water '
            r'that reaches the water table and falls as the aquifer drains to its base level $h_b$ with a time constant '
            r'$\tau_a$. With the specific yield $S_y$ known, the recharge of day $i$ in millimetres is [11]'))
    a(('eq', 'wtf', r'R_i = 1000\, S_y \left( h_i - h_{i-1} + \frac{h_{i-1} - h_b}{\tau_a} \right)'))
    a(('p', f'Figure {{{{fig11_recharge}}}} runs three synthetic Mediterranean years ({N["rain"]:.0f} mm/year of rain, '
            f'{N["rech"]:.0f} mm/year of recharge) through a soil-water balance to the head of a well, adds 1 cm of logger '
            f'noise and recovers the recharge. The daily error is {N["derr"]:.1f} mm, as predicted by '
            r'$1000\, S_y\, \sigma \sqrt{2}$ for a noise $\sigma$, but the errors cancel over a month: the monthly error '
            f'is {N["merr"]:.1f} mm for a mean monthly recharge of {N["mmean"]:.1f} mm. One caution: heads and rain '
            r'alone cannot fix $S_y$, because multiplying the soil parameters and $S_y$ by the same factor leaves the '
            'heads unchanged; a pumping test (task T5.3) fixes it.'))
    a(('img', 'fig11_recharge', 16.0))
    a(('cap', 'Figure {{fig11_recharge}}. (a) Synthetic daily rain. (b) Head of a well, true and as logged with 1 cm noise. '
              '(c) Recharge over 30-day periods, true and estimated from the logged heads with equation [[wtf]].'))
    a(('p', f'Figure {{{{fig27_equifinality}}}} shows the caution in numbers: with five soil parameters and $S_y$ '
            f'multiplied by 1.5, the heads differ by less than {N["eq_maxdh"]:.0e} m, while the recharge of three years '
            f'goes from {N["eq_cum1"]:.0f} to {N["eq_cum2"]:.0f} mm. No amount of head data separates the two; one '
            'independent measurement does.'))
    a(('img', 'fig27_equifinality', 15.0))
    a(('cap', 'Figure {{fig27_equifinality}}. Two soil-water balances that the heads cannot tell apart. (a) Heads of a '
              'well for the estimated parameters and for five parameters multiplied by 1.5. (b) The cumulative recharge '
              'of the two.'))
    a(('h2', '3.4  The boundary where the model is cut'))
    a(('p', 'Every model must stop somewhere inland, and the usual choices at the cut, no flow or a fixed head, are '
            'guesses. CERTAIN-COAST replaces the aquifer beyond the cut by a passive boundary: a conductance $C$ and a set '
            r'of storage compartments, each with a rate $\mu_m$ and a weight $w_m$:'))
    a(('eq', 'bnd', r'q_b = C\,\psi + \sum_{m} w_m \left( \psi - y_m \right), \qquad \frac{dy_m}{dt} = \mu_m '
                    r'\left( \psi - y_m \right)'))
    a(('p', r'where $q_b$ is the flux through the cut, $\psi$ the head there and $y_m$ the state of compartment $m$. With '
            r'$C \ge 0$ and $w_m \ge 0$ the boundary can store and release water but never create energy, so the model '
            'stays stable whatever the forcing. The weights are learned from two piezometers next to the cut (task '
            f'T4.2 drills them). In Figure {{{{fig12_boundary}}}} the boundary learned from 20 years of noisy heads '
            f'predicts a drought with doubled pumping, which it never saw, within {N["bl"]:.3f} m; the no-flow and the '
            f'fixed-head boundaries are off by {N["bn"]:.2f} m and {N["bf"]:.2f} m.'))
    a(('img', 'fig12_boundary', 16.0))
    a(('cap', 'Figure {{fig12_boundary}}. (a) Head at the cut of a 2 km model of a 10 km aquifer, during a drought with '
              'doubled pumping: the whole aquifer (truth), the boundary learned from two piezometers and the two usual '
              f'boundaries. (b) Impedance of the exact boundary ({N["ncomp"]} compartments) and of the learned one (12); '
              'they agree for periods longer than about a month, which is what the prediction needs.'))
    a(('box', ['**Innovation.** Sensors chosen for the decision, not for the map: the information about the goal from two '
               'adjoint solves; a warning band that holds between samples and says which measurement closes it (a '
               'logger, or pairs of samples a few days apart); recharge read from the same loggers; and a model boundary '
               'learned from two piezometers, passive by construction.']))

    # ---- 4
    a(('pb',))
    a(('h', '4  Warnings that state their miss rate'))
    a(('p', 'A warning system can always be made to miss nothing, by warning all the time. The useful question is how '
            'often it misses, and the operator should know that number before relying on the system. CERTAIN-COAST '
            r'calibrates each alarm on past forecast errors $r_i$ = observed − forecast. The $n$ errors are sorted and '
            r'the $k$-th smallest is the margin $m$ [12]:'))
    a(('eq', 'conf', r'm = r_{(k)}, \qquad k = \lceil (n+1)(1-\alpha) \rceil, \qquad '
                     r'\text{alarm when } \hat{y} + m \ge y_{\mathrm{lim}}'))
    a(('p', r'where $\hat{y}$ is the forecast and $y_{\mathrm{lim}}$ the limit. If the new error is exchangeable with the past ones, the '
            r'alarm misses a dangerous event with a probability of at most $\alpha$, whatever the forecast model is:'))
    a(('eq', 'guar', r'P\left( y > \hat{y} + m \right) \le \alpha'))
    a(('p', r'In operation every outcome is logged. After $n$ dangerous events with $x$ misses, the exact 95% upper '
            'bound on the true miss rate is [13]'))
    a(('eq', 'cp', r'\overline{p} = \mathrm{Beta}^{-1}\left( 0.95;\; x + 1,\; n - x \right), \qquad \overline{p} = 1 - 0.05^{1/n} '
                   r'\;\text{ when } x = 0'))
    a(('p', r'where $\mathrm{Beta}^{-1}$ is the quantile of the beta distribution. Figure {{fig13_alarm}}a shows a synthetic chloride '
            f'forecast calibrated on 600 steps for $\\alpha$ = 0.10: the margin is {N["margin"]:.1f} mg/L. On the next '
            f'600 steps there were {N["nev"]} dangerous events, {"none was" if N["nmiss"] == 0 else str(N["nmiss"]) + " were"} '
            f'missed, and the alarm sounded '
            f'{N["nfalse"]} times without an event: the price of the guarantee is paid in false alarms, and it is known. '
            'Figure {{fig13_alarm}}b shows how many events the log needs before it can confirm the stated rate: '
            f'with no miss, {N["n_cp"]} events bring the bound below 0.10.'))
    a(('img', 'fig13_alarm', 16.0))
    a(('cap', 'Figure {{fig13_alarm}}. (a) A certified chloride alarm on synthetic data (120 of the 600 test steps): '
              'observed chloride, forecast, forecast plus margin, alarms and dangerous events. (b) Exact 95% upper bound '
              'on the miss rate against the number of logged events, with no miss and with 10% missed.'))
    ra, rm = N['rel_alpha'], N['rel_mean']
    a(('p', 'Does the guarantee hold when the errors are far from normal? Figure {{fig26_alarm_reliability}} repeats the '
            f'calibration {N["rel_nrep"]} times with {N["rel_ncal"]} skewed (lognormal) errors each time and counts the '
            f'misses on 2000 new errors. For stated rates of {ra[0]:.2f}, {ra[1]:.2f}, {ra[2]:.2f} and {ra[3]:.2f} the '
            f'mean observed rates are {rm[0]:.3f}, {rm[1]:.3f}, {rm[2]:.3f} and {rm[3]:.3f}. A single calibration can '
            'miss more or less often than stated, which is why the log of outcomes and the bound of equation [[cp]] '
            'stay in operation.'))
    a(('img', 'fig26_alarm_reliability', 12.5))
    a(('cap', 'Figure {{fig26_alarm_reliability}}. Observed against stated miss rate of the certified alarm over repeated '
              'calibrations with skewed errors; boxes span the middle half of the calibrations and whiskers 95% of them.'))
    a(('box', ['**Innovation.** Every warning, for the salinity of a well, liquefaction at the port or a flood level, '
               'carries a miss rate fixed before it is used, and the log of outcomes keeps it honest with an exact bound. '
               'The rule works for any forecast model, including a machine-learned one.']))

    # ---- 5
    a(('pb',))
    a(('h', '5  Earthquakes and the aquifer'))
    a(('p', 'An earthquake does more than shake. The slip on the fault strains the crust, and a saturated layer answers a '
            'change of volume with a change of pore pressure within seconds. CERTAIN-COAST computes the strain at the '
            'surface with the solution of Okada (1985) for a rectangular fault in an elastic half-space [14] and turns it '
            'into a pressure step. A layer under the free surface takes the horizontal (areal) strain of the crust '
            'below it, so that [20]'))
    a(('eq', 'dp', r'\Delta p = -C_a \left( \Delta\varepsilon_{xx} + \Delta\varepsilon_{yy} \right), \qquad '
                   r'C_a = \frac{2 G_s B}{3} \cdot \frac{1 + \nu_u}{1 - \nu_u}'))
    a(('eq', 'dh', r'\Delta h = \frac{\Delta p}{\rho_w\, g}'))
    a(('p', r'where $C_a$ is the areal stiffness of the layer, $G_s$ its shear modulus, $B$ its Skempton coefficient, $\nu_u$ its undrained Poisson '
            r'ratio, $\rho_w$ the density of water and $g$ gravity. A soft, nearly incompressible layer deforms at almost '
            r'constant volume, so its step is set by its shear modulus, not by the stiffness of its water. For a confined '
            f'aquifer in older sediment ($G_s$ = 0.5 GPa) one microstrain of areal extension lowers the head by '
            f'{N["k_conf"]:.3f} m; in soft surface sand ($G_s$ = 50 MPa) by {N["k_soft"]:.4f} m, about '
            f'{N["k_ratio"]:.0f} times less.'))
    a(('p', 'Figure {{fig14_quake_maps}} shows the head step for four published source models of the Durrës earthquake '
            f'[15–18]. They agree on the pattern, a fall of {N["fall"][0]:.1f}–{N["fall"][1]:.1f} m above the fault, '
            f'where the crust is stretched, and a rise of {N["rise"][0]:.1f}–{N["rise"][1]:.1f} m on both sides; the '
            'four models agree '
            f'on the sign of the step over {N["agree"]:.0f}% of the area where the strain exceeds 0.75 microstrain. '
            'They disagree on the exact position, which depends on the dip of the fault. Figure {{fig15_quake_transect}} '
            'cuts across the strike: the soft surface sand moves by a few centimetres only.'))
    a(('img', 'fig14_quake_maps', 15.0))
    a(('cap', 'Figure {{fig14_quake_maps}}. Sudden head change in a confined aquifer ($G_s$ = 0.5 GPa) for four published '
              'source models of the 26 November 2019 Durrës earthquake, from equations [[dp]] and [[dh]] with the Okada '
              'solution; local coordinates centred on the fault, east and north in km. The dashed outline is the surface '
              'projection of the fault plane, the thick edge its top. Contours at −0.5, −0.1 and +0.1 m.'))
    a(('img', 'fig15_quake_transect', 12.5))
    a(('cap', 'Figure {{fig15_quake_transect}}. The head step across the strike of the fault for the four source models '
              '(confined aquifer) and the mean step in soft surface sand.'))
    a(('p', 'The same slip also moves the ground up and down, and so changes at once the relative sea level of equation '
            f'[[rsl]]. The four source models put the ground above the fault {100 * N["uz_up"][0]:.0f}–'
            f'{100 * N["uz_up"][1]:.0f} cm higher and its flanks {100 * N["uz_down"][0]:.1f}–'
            f'{100 * N["uz_down"][1]:.1f} cm lower (Figure {{{{fig22_uplift}}}}): where the ground sank, the sea is '
            'closer to the wells and to the port from that day on. GNSS stations and radar corner reflectors measure '
            'this directly.'))
    a(('img', 'fig22_uplift', 15.0))
    a(('cap', 'Figure {{fig22_uplift}}. Vertical ground motion of the four source models of the Durrës earthquake (Okada '
              'solution); positive is uplift. Uplift lowers the relative sea level, subsidence raises it.'))
    a(('p', 'Where should a logger stand to record the next step? Figure {{fig23_agree}} averages the four models and '
            'hatches the area where they disagree on its sign. A logger inside a bold contour, outside the hatching, '
            'records a step larger than 10 cm whichever model is right; that is where the network places the loggers '
            'that turn earthquakes into pumping tests.'))
    a(('img', 'fig23_agree', 12.5))
    a(('cap', 'Figure {{fig23_agree}}. Mean head step of the four source models in a confined aquifer, with the area '
              'where they disagree on its sign (hatched) and the contour of a step larger than 10 cm.'))
    a(('p', r'The step does not last. In sand connected to the water table it drains during the shaking itself, as '
            r'pressure diffuses with the hydraulic diffusivity $D_h$ over the depth $\zeta$ below the water table; the share '
            r'left after a time $t$ is'))
    a(('eq', 'drain', r'f = \mathrm{erf} \left( \frac{\zeta}{2 \sqrt{D_h\, t}} \right)'))
    a(('p', f'With $D_h$ = 1 m²/s, after 15 seconds of shaking only {N["share"]["1 m"]:.0f}% of the step remains 1 m below '
            f'the water table and {N["share"]["5 m"]:.0f}% at 5 m (Figure {{{{fig24_drainage}}}}); below a clay layer the '
            'whole step stays.'))
    a(('img', 'fig24_drainage', 12.0))
    a(('cap', 'Figure {{fig24_drainage}}. Share of the coseismic step left in sand connected to the water table, against '
              'the depth below it, from equation [[drain]] with $D_h$ = 1 m²/s; points: the values used by the project. '
              'Below a clay layer the step stays whole.'))
    a(('p', 'Below the clay the step relaxes over days, as'))
    a(('eq', 'relax', r'\Delta h(t) = \Delta h_0\, e^{-t/\tau}'))
    a(('p', r'where $\tau$ is the leakage time of the clay above the aquifer, the parameter that decides how fast a '
            'contamination or a pumping effect crosses it. Figure {{fig16_natural_test}} shows why the earthquake matters '
            f'for that parameter: one earthquake recorded by a logger every 15 minutes pins $\\tau$ to '
            f'{N["ci_q"][0]:.2f}–{N["ci_q"][1]:.2f} days (95% interval), while a whole year of seasonal heads, the usual '
            f'way to estimate it, gives {N["ci_s"][0]:.2f}–{N["ci_s"][1]:.2f} days, {N["ratio"]:.1f} times wider. The '
            'earthquake is a free pumping test of the whole aquifer [19].'))
    a(('img', 'fig16_natural_test', 16.0))
    a(('cap', 'Figure {{fig16_natural_test}}. (a) Relaxation of a 0.3 m coseismic step in a confined sand below a leaky clay '
              '(synthetic logger, 2 cm noise) and the fit of equation [[relax]]. (b) 95% intervals of the leakage time '
              'from one earthquake and from one year of seasonal heads; the dashed line is the true value.'))
    a(('box', ['**Innovation.** Which layer feels the earthquake is decided by its shear modulus: a confined aquifer takes '
               'a step of decimetres, the soft surface sand one of centimetres, and the usual formula applied to the '
               'surface sand overstates it many times. Every recorded earthquake becomes a free pumping test, and the '
               'network is designed to record it.']))

    # ---- 6
    a(('pb',))
    a(('h', '6  Liquefaction'))
    a(('p', 'Liquefaction is judged layer by layer, by comparing the load of the earthquake with the resistance of the '
            'sand. The load is the cyclic stress ratio [21, 22]'))
    a(('eq', 'csr', r'\mathrm{CSR} = 0.65\, \frac{\sigma_v}{\sigma^{\prime}_v}\, \frac{a_{\max}}{g}\, r_d'))
    a(('p', r'where $\sigma_v$ and $\sigma^{\prime}_v$ are the total and the effective vertical stress, $a_{\max}$ the peak '
            r'ground acceleration and $r_d$ a depth factor. The resistance comes from the cone penetration test (CPT), '
            r'through the clean-sand normalised tip resistance $q = q_{c1Ncs}$ [21, 22]:'))
    a(('eq', 'crr', r'\mathrm{CRR}_{7.5} = \exp \left( \frac{q}{113} + \left( \frac{q}{1000} \right)^{2} - '
                    r'\left( \frac{q}{140} \right)^{3} + \left( \frac{q}{137} \right)^{4} - 2.80 \right)'))
    a(('eq', 'fs', r'\mathrm{FS} = \frac{\mathrm{CRR}_{7.5}\; \mathrm{MSF}\; K_{\sigma}}{\mathrm{CSR}}'))
    a(('p', r'where MSF corrects for the magnitude and $K_{\sigma}$ for the confining stress (Table {{t_bi}}). A layer '
            r'liquefies when $\mathrm{FS} \le 1$. The water table enters through the pore pressure of the day, $z_w$ being its '
            'depth, to which the coseismic step of Chapter 5 is added:'))
    a(('eq', 'u', r'u(z) = \gamma_w \left( z - z_w \right)_{+} + \Delta p'))
    a(('cap', 'Table {{t_bi}}. The terms of the triggering procedure of Boulanger and Idriss [21, 22] used by the project '
              '($z$ depth in m, $M$ magnitude, $P_a$ atmospheric pressure).'))
    a(('table', ['Term', 'Equation', 'Role'],
       [['$r_d$', r'$\exp\left( a(z) + b(z)\, M \right)$, with $a = -1.012 - 1.126 \sin\left( z/11.73 + '
                  r'5.133 \right)$ and $b = 0.106 + 0.118 \sin\left( z/11.28 + 5.142 \right)$',
         'how the shaking decreases with depth'],
        ['MSF', r'$1 + \left( \mathrm{MSF}_{\max} - 1 \right) \left( 8.64\, e^{-M/4} - 1.325 \right)$, with '
                r'$\mathrm{MSF}_{\max} = \min\left( 1.09 + (q/180)^{3},\; 2.2 \right)$', 'more cycles in a larger earthquake'],
        [r'$K_{\sigma}$', r'$\min\left( 1 - C_{\sigma} \ln\left( \sigma^{\prime}_v / P_a \right),\; 1.1 \right)$, with '
                          r'$C_{\sigma} = \min\left( 1/\left( 37.3 - 8.27\, q^{0.264} \right),\; 0.3 \right)$',
         'deep sand is harder to liquefy']], [1.6, 11.2, 4.2], 9.5))
    a(('p', 'The liquefaction potential index adds up the deficit of the safety factor over the top 20 m, with a weight '
            'that decreases with depth [23]:'))
    a(('eq', 'lpi', r'\mathrm{LPI} = \int_{0}^{20} F(z)\, \left( 10 - 0.5\, z \right)\, dz, \qquad F = 1 - \mathrm{FS} '
                    r'\;\text{ where } \mathrm{FS} \le 1, \;\text{ else } 0'))
    lp = N['lpi']
    a(('p', 'Figure {{fig17_liq_profile}} computes an illustrative coastal profile with three sand layers separated by '
            r'silty clay, for $a_{\max}$ = 0.25 g and a magnitude of 6.4. With the water table at 2.6 m the LPI is '
            f'{lp["2.6"]:.1f}; at 1.6 m it is {lp["1.6"]:.1f}; at 0.8 m it is {lp["0.8"]:.1f}. Above 5 the damage is '
            'usually severe [23]. Figure {{fig18_crr_chart}} shows the same sand on the chart of Boulanger and Idriss: '
            'raising the water table moves every layer upwards, across the curve.'))
    a(('img', 'fig17_liq_profile', 15.0))
    a(('cap', 'Figure {{fig17_liq_profile}}. An illustrative coastal profile. (a) CPT resistance of the three sand layers '
              '(shaded); the silty clays between them do not liquefy. (b) Factor of safety for three depths of the water '
              'table (dotted lines), with the resulting LPI.'))
    a(('img', 'fig18_crr_chart', 12.5))
    a(('cap', 'Figure {{fig18_crr_chart}}. The sand cells of the profile on the liquefaction chart: the cyclic stress '
              'ratio brought to magnitude 7.5 and 1 atm against the CPT resistance, with the resistance curve of '
              'equation [[crr]]. Points above the curve liquefy.'))
    a(('p', 'How fast does the danger grow as the water table rises? Below the water table the answer has a closed form:'))
    a(('eq', 'dfs', r'\frac{\partial \ln \mathrm{FS}}{\partial z_w} = \frac{\gamma_w}{\sigma^{\prime}_v} \left( 1 - '
                    r'\frac{C_{\sigma}}{K_{\sigma}} \right)'))
    a(('p', f'which agrees with finite differences of the full procedure to a relative error of {N["fd_err"]:.0e}. '
            'Figure {{fig19_lpi}}a shows the LPI against the depth of the water table for three accelerations: for the '
            f'example profile at 0.25 g it falls by about {-N["slope"]:.0f} for every metre of deeper water table. Figure '
            '{{fig19_lpi}}b shows a common shortcut, re-normalising the CPT resistance with the stress at the time of the '
            f'earthquake: it understates that slope by {N["under"]:.0f}%.'))
    a(('img', 'fig19_lpi', 16.0))
    a(('cap', 'Figure {{fig19_lpi}}. (a) LPI of the example profile against the depth of the water table for three peak '
              'accelerations. (b) The same at 0.25 g computed correctly (CPT resistance fixed, pore pressure of the day) '
              'and with the shortcut.'))
    a(('p', 'Figure {{fig25_lpi_chart}} puts the two drivers together for the example profile: the acceleration of the '
            'earthquake, which nobody controls, and the depth of the water table, which sea-level rise, the seasons and '
            'pumping move. Left of the bold line the LPI stays below 5. A rising water table moves the profile upwards '
            'on the chart, across the line, without any change in the earthquake.'))
    a(('img', 'fig25_lpi_chart', 13.0))
    a(('cap', 'Figure {{fig25_lpi_chart}}. LPI of the example profile against the peak ground acceleration and the depth '
              'of the water table (magnitude 6.4). The bold line is LPI = 5.'))
    a(('box', ['**Innovation.** Liquefaction computed with the water table and the pore pressure of the day, not with a '
               'design water table fixed once: the sensors that guard the wells against salt update the liquefaction '
               'risk every day, and a sea-level rise of a few decimetres translates directly into LPI.']))

    # ---- 7
    a(('pb',))
    a(('h', '7  The joint safe window and the daily bulletin'))
    a(('p', 'Intrusion and liquefaction pull the water table in opposite directions. To keep the interface at least 20 m '
            r'deep, the 1 : 40 rule requires the water table to stay at least $m_{\mathrm{int}}$ = 20/40 = 0.5 m above '
            r'the sea, whose level has risen by $\eta$. To keep the LPI below 5 for the design earthquake over 90% of the '
            r'port, the water table must stay deeper than $d_L(a_{\max})$ below the ground, which is at the elevation '
            r'$z_s$. The two limits define a window for the elevation $h_{\mathrm{wt}}$ of the water table:'))
    a(('eq', 'win', r'\eta + m_{\mathrm{int}} \;\le\; h_{\mathrm{wt}} \;\le\; z_s - d_L\left( a_{\max} \right)'))
    a(('p', r'With a seasonal swing $A$ of the managed water table, the window closes for the whole year once the sea has '
            'risen by'))
    a(('eq', 'close', r'\eta_{\mathrm{close}} = z_s - d_L\left( a_{\max} \right) - m_{\mathrm{int}} - A'))
    a(('p', 'Figure {{fig20_window}} maps the width of the window for an illustrative port 2 m above the sea, with 60 '
            r'CPT profiles. For a design acceleration of 0.15 g the window stays open up to 1.2 m of '
            f'sea-level rise; for 0.18 g it closes all year at {N["eta18"]:.2f} m and for 0.20 g at {N["eta20"]:.2f} m; '
            'for 0.22 g and above it is already closed today. Then no pumping rule can keep both hazards acceptable, and '
            'the port needs drainage or ground improvement: management has to turn into engineering, and the figure says '
            'when.'))
    a(('img', 'fig20_window', 13.5))
    a(('cap', 'Figure {{fig20_window}}. Width of the safe window of equation [[win]] against the design acceleration and '
              'the sea-level rise (illustrative port). Blue: the water table can be held between the two limits; red: '
              'no water table satisfies both. The solid line is the closing of the window; the dashed line its closing '
              'for the whole year with a seasonal swing of 0.3 m.'))
    a(('p', 'Day by day, the bulletin asks one question: if the design earthquake struck today, with today’s water table, '
            'what is the probability of severe liquefaction?'))
    a(('eq', 'bull', r'P_{\mathrm{today}} = P\left( \mathrm{LPI} > 5 \mid \text{design earthquake},\; '
                     r'z_w(\text{today}) \right)'))
    a(('p', 'Figure {{fig21_bulletin}} computes it for the illustrative port over a year, for an earthquake of magnitude '
            r'6.4 with $a_{\max}$ spread around 0.22 g: the water table moves between '
            f'{N["zw_range"][0]:.1f} and {N["zw_range"][1]:.1f} m below the ground, and the probability between '
            f'{N["pmin"]:.2f} in late summer, when it is deepest, and {N["pmax"]:.2f} in winter.'))
    a(('img', 'fig21_bulletin', 16.0))
    a(('cap', 'Figure {{fig21_bulletin}}. The daily bulletin for an illustrative port. (a) Depth of the water table over '
              'the year. (b) Probability of severe liquefaction (LPI above 5) if the design earthquake struck that day.'))
    a(('box', ['**Innovation.** One window for two hazards: the pumping rule that keeps the salt out is checked every day '
               'against the liquefaction it causes or prevents, and the sea-level rise at which the window closes is '
               'computed in advance, so the end-user knows when management must turn into engineering.']))

    # ---- 8
    a(('pb',))
    a(('h', '8  What is new'))
    a(('p', 'Table {{t_new}} summarises, for each part of the system, the usual practice, what CERTAIN-COAST adds and where '
            'this guide shows it.'))
    a(('cap', 'Table {{t_new}}. The innovations of CERTAIN-COAST shown in this guide.'))
    a(('table', ['Part', 'Usual practice', 'What CERTAIN-COAST adds', 'Figures'],
       [['Seawater intrusion', 'one model per site, fixed boundaries, slow solvers',
         'variable-density model with a learned passive boundary and a fast sparse Jacobian, open source',
         '{{fig03_henry}}, {{fig04_inflow}}, {{fig12_boundary}}'],
        ['Sensors', 'networks designed to map everything',
         'sensors chosen for the decision, from two adjoint solves; the published Fushë-Kuqe design',
         '{{fig06_fushe_kuqe}}, {{fig07_sensor_map}}, {{fig08_returns}}'],
        ['Sampling', 'samples treated as the whole truth',
         'a warning band for crossings between samples, and the measurement that closes it',
         '{{fig09_between_path}}, {{fig10_between_bands}}'],
        ['Recharge', 'from rain and soil budgets', 'from the same loggers that watch the wells, with the anchor it needs',
         '{{fig11_recharge}}, {{fig27_equifinality}}'],
        ['Warnings', 'thresholds with no stated reliability',
         'a miss rate stated in advance and checked with an exact bound', '{{fig13_alarm}}, {{fig26_alarm_reliability}}'],
        ['Earthquakes', 'the pressure step neglected, or overstated with one formula',
         'the shear modulus of the layer decides; where to record it; the earthquake as a free pumping test',
         '{{fig14_quake_maps}}–{{fig16_natural_test}}'],
        ['Liquefaction', 'a design water table fixed once',
         'the water table and pore pressure of the day; a closed-form sensitivity',
         '{{fig17_liq_profile}}–{{fig25_lpi_chart}}'],
        ['Decisions', 'one hazard at a time', 'one safe window for intrusion and liquefaction; a daily bulletin',
         '{{fig20_window}}, {{fig21_bulletin}}']], [2.6, 4.4, 7.8, 2.2], 9.5))
    a(('p', 'All the code is open source under the Apache License 2.0, written in MATLAB and running also in the free GNU '
            f'Octave, so that the end-user needs no licence: [{REPO}]({REPO}). Field data provided by the owners of '
            'wells and records stay restricted; the repository holds code and synthetic data only.'))

    # ---- appendix
    a(('h', 'Appendix A.  Where each figure comes from'))
    a(('cap', 'Table {{t_src}}. Source and check of every figure. "certaincoast" denotes the open-source MATLAB package; '
              '"earthquake experiment" the preparatory code of the project on earthquakes and liquefaction.'))
    a(('table', ['Figure', 'Computed by', 'Check'],
       [['{{fig01_system}}', 'schematic', '—'],
        ['{{fig02_lens}}, {{fig05_upconing}}', 'closed-form equations [[gh]], [[lens]] and [[upcone]]',
         'textbook solutions [1, 6, 7]'],
        ['{{fig03_henry}}, {{fig04_inflow}}', 'certaincoast.model (Henry benchmark)',
         'toe equal to the published values to 4 decimals [8]'],
        ['{{fig06_fushe_kuqe}}', 'the Fushë-Kuqe model with certaincoast.network',
         'reproduces the published design exactly [8]'],
        ['{{fig07_sensor_map}}, {{fig08_returns}}', 'certaincoast.model and certaincoast.network (adjoint)',
         'adjoint against finite differences, 1e-5'],
        ['{{fig09_between_path}}, {{fig10_between_bands}}', 'certaincoast.betweensamples',
         'bands cover the truth in 40 records per design'],
        ['{{fig11_recharge}}, {{fig27_equifinality}}', 'certaincoast.recharge',
         'daily error equal to the predicted one; heads equal to 1e-15 m'],
        ['{{fig12_boundary}}', 'certaincoast.boundary', 'exact boundary reproduces the full aquifer to 1e-13 m'],
        ['{{fig13_alarm}}, {{fig26_alarm_reliability}}', 'certaincoast.alarms',
         'exact binomial bound; mean miss rate equal to the stated one over 4000 calibrations'],
        ['{{fig14_quake_maps}}–{{fig16_natural_test}}', 'earthquake experiment (Okada solution, poroelastic step, drainage)',
         'five independent checks of the Okada code'],
        ['{{fig17_liq_profile}}–{{fig21_bulletin}}', 'earthquake experiment (liquefaction module)',
         f'closed-form derivative against finite differences, {N["fd_err"]:.0e}']], [3.2, 7.4, 6.4], 9.5))
    a(('p', 'All the tests of the open-source package (36 in version 0.1.0) pass in GNU Octave and are run in MATLAB by the '
            'continuous integration of the repository.'))
    a(('h', 'Appendix B.  Symbols'))
    a(('cap', 'Table {{t_sym}}. The symbols of the guide, by chapter.'))
    a(('table', ['Symbol', 'Meaning', 'Unit', 'Ch.'],
       [[r'$\eta_{\mathrm{rel}},\ \eta_{\mathrm{sea}},\ s$', 'relative sea level, sea level, land subsidence', 'm', '1'],
        [r'$\eta$', 'sea-level rise from today', 'm', '7'],
        [r'$h$', 'height of the water table above sea level; equivalent freshwater head', 'm', '2'],
        [r'$z$', 'depth of the fresh–salt interface below sea level (Ch. 2); depth below the ground (Ch. 6)', 'm', '2, 6'],
        [r'$\rho_f,\ \rho_s,\ \rho_w$', 'density of fresh water, sea water, water', 'kg/m³', '2, 5'],
        [r'$\delta,\ \varepsilon$', 'density contrast of sea water, about 0.025', '–', '2'],
        [r'$K$', 'hydraulic conductivity', 'm/day', '2, 3'],
        [r'$N,\ L,\ x$', 'recharge on the coastal strip, width of the strip, distance from the coast', 'mm/yr, m, m', '2'],
        [r'$c$', 'relative salinity, 0 fresh, 1 sea', '–', '2'],
        [r'$\mathbf{q},\ \phi,\ D$', 'Darcy flux, porosity, diffusivity of the salt', 'm/day, –, m²/s', '2'],
        [r'$Q,\ d$', 'inflow or pumping rate; height of the well above the interface', 'm³/day, m', '2'],
        [r'$\theta,\ \Gamma,\ \Gamma_n$', 'uncertain parameters, their prior covariance, the noise covariance', '–', '3'],
        [r'$G,\ H$', 'sensitivity of the sensors and of the goal to the parameters', '–', '3'],
        [r'$\mathrm{EIG}$', 'information the sensors give about the goal', 'nats', '3'],
        [r'$X,\ \kappa,\ \ell$', 'chloride anomaly, its rate (1 / correlation time), the limit in standard deviations',
         '–, 1/day, –', '3'],
        [r'$\Delta t,\ \rho$', 'lag between two samples, their correlation', 'day, –', '3'],
        [r'$S_y,\ h_b,\ \tau_a,\ R_i$', 'specific yield, drainage base, drainage time, daily recharge',
         '–, m, day, mm', '3'],
        [r'$q_b,\ \psi,\ C,\ w_m,\ \mu_m,\ y_m$', 'boundary flux, head at the cut, conductance, weights, rates and '
                                                   'states of the compartments', '–', '3'],
        [r'$r_i,\ m,\ \alpha,\ \hat{y},\ y_{\mathrm{lim}}$', 'forecast errors, alarm margin, stated miss rate, '
                                                                 'forecast, limit', 'as the forecast; –', '4'],
        [r'$n,\ x,\ \overline{p}$', 'logged dangerous events, misses, upper bound on the miss rate', '–', '4'],
        [r'$\Delta p,\ \Delta h,\ C_a$', 'coseismic pore-pressure and head step, areal stiffness of the layer',
         'kPa, m, kPa', '5'],
        [r'$G_s,\ B,\ \nu_u$', 'shear modulus, Skempton coefficient, undrained Poisson ratio', 'Pa, –, –', '5'],
        [r'$\zeta,\ D_h,\ f,\ \tau$', 'depth below the water table, hydraulic diffusivity, share of the step left, '
                                         'leakage time', 'm, m²/s, –, day', '5'],
        [r'$\sigma_v,\ \sigma^{\prime}_v,\ u,\ \gamma_w$', 'total and effective vertical stress, pore pressure, unit '
                                                               'weight of water', 'kPa, kPa, kPa, kN/m³', '6'],
        [r'$a_{\max},\ M,\ r_d$', 'peak ground acceleration, magnitude, depth factor', 'g, –, –', '6'],
        [r'$q,\ z_w$', 'clean-sand normalised CPT resistance $q_{c1Ncs}$, depth of the water table', '–, m', '6'],
        [r'$\mathrm{CSR},\ \mathrm{CRR},\ \mathrm{FS},\ \mathrm{LPI}$', 'load, resistance, factor of safety, '
                                                                             'liquefaction potential index', '–', '6'],
        [r'$m_{\mathrm{int}},\ d_L,\ z_s,\ A$', 'freshwater margin, safe depth of the water table, ground elevation, '
                                                  'seasonal swing', 'm', '7']],
       [4.4, 8.8, 2.4, 1.4], 9))
    a(('h', 'Appendix C.  Glossary'))
    a(('cap', 'Table {{t_glo}}. The words of the guide, in plain language.'))
    a(('table', ['Word', 'Meaning'],
       [['Aquifer', 'a layer of sand or gravel that holds groundwater and lets it flow'],
        ['Water table, head', 'the level at which groundwater stands in a well, here measured above sea level'],
        ['Piezometer', 'a narrow well with a short screen, used only to measure the head at one depth'],
        ['Isochlor', 'a line of equal salinity; on the 0.5 isochlor the water is half fresh and half sea water'],
        ['Toe of the wedge', 'where the 0.5 isochlor meets the base of the aquifer: the furthest reach of the salt'],
        ['Upconing', 'the rise of salt water into a cone below a pumping well'],
        ['Recharge', 'the part of the rain that reaches the water table'],
        ['Specific yield', 'the water released by one square metre of aquifer when the water table falls by one metre'],
        ['Adjoint solve', 'one backward computation of the model that gives the sensitivity of one output to every '
                          'parameter at once'],
        ['Information (nats)', 'how much a measurement narrows the uncertainty of the goal: one nat divides its '
                               'standard deviation by e, about 2.7'],
        ['Greedy design', 'sensors added one at a time, each time the one that adds most information'],
        ['Correlation time', 'how long a quantity, here the chloride, remembers its present value'],
        ['Warning band', 'the range of the probability of a crossing over every model the record cannot rule out'],
        ['Miss rate', 'the share of dangerous events for which the alarm did not sound'],
        ['Conformal margin', 'a margin computed from past forecast errors so that the stated miss rate holds, '
                             'whatever the forecast model'],
        ['Coseismic', 'happening during the earthquake'],
        ['Areal strain', 'the relative change of a horizontal area of ground'],
        ['Skempton coefficient', 'the share of a sudden load carried by the water in the pores'],
        ['CPT', 'cone penetration test: a cone pushed into the ground, whose resistance tells how dense the sand is'],
        ['CSR, CRR, FS', 'the load of the earthquake, the resistance of the sand, and their ratio'],
        ['LPI', 'liquefaction potential index: the deficit of safety over the top 20 m; above 5 the damage is '
                'usually severe'],
        ['Peak ground acceleration', 'the strongest acceleration of the ground during the shaking, in units of g'],
        ['GNSS, corner reflector', 'satellite positioning stations and metal targets for satellite radar, which measure '
                                   'how the ground moves up and down'],
        ['Safe window', 'the range of water-table heights for which both intrusion and liquefaction stay acceptable']],
       [4.2, 12.8], 9.5))
    a(('refs',))
    return B


# ------------------------------------------------------------------------------------------------ rendering
def style_headings(doc):
    for name, size, color, before, after in (('Heading 1', 16, NAVY, 6, 8), ('Heading 2', 12.5, BLUE2, 10, 4)):
        st = doc.styles[name]
        st.font.name = 'Arial'
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.italic = False
        st.font.color.rgb = RGBColor.from_string(color)
        rpr = st.element.get_or_add_rPr()
        fonts = rpr.find(qn('w:rFonts'))
        if fonts is None:
            fonts = OxmlElement('w:rFonts')
            rpr.append(fonts)
        for att in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
            if fonts.get(qn(att)) is not None:
                del fonts.attrib[qn(att)]
        for att in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
            fonts.set(qn(att), 'Arial')
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True


def footer(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, 'CERTAIN-COAST · an illustrated guide · page ', size=8.5, color=GREY)
    r = p.add_run()
    for kind, text in (('begin', None), (None, 'PAGE'), ('separate', None), (None, '1'), ('end', None)):
        if kind:
            fc = OxmlElement('w:fldChar')
            fc.set(qn('w:fldCharType'), kind)
            r._r.append(fc)
        elif text == 'PAGE':
            it = OxmlElement('w:instrText')
            it.set(qn('xml:space'), 'preserve')
            it.text = ' PAGE '
            r._r.append(it)
        else:
            t = OxmlElement('w:t')
            t.text = text
            r._r.append(t)
    r.font.size = Pt(8.5)
    r.font.color.rgb = RGBColor.from_string(GREY)


def number_blocks(BL):
    numbers, n_eq, n_fig, n_tab = {}, 0, 0, 0
    for b in BL:
        if b[0] == 'eq':
            n_eq += 1
            numbers[b[1]] = str(n_eq)
        elif b[0] == 'img':
            n_fig += 1
            numbers['#' + b[1]] = str(n_fig)
        elif b[0] == 'cap' and re.match(r'Table \{\{(\w+)\}\}', b[1]):
            n_tab += 1
            numbers['#' + re.match(r'Table \{\{(\w+)\}\}', b[1]).group(1)] = str(n_tab)
    return numbers, n_eq, n_fig, n_tab


def contents(doc, BL, numbers):
    t = doc.add_table(rows=1, cols=1)
    borders(t, 'C9D3E0', 6)
    fixed_widths(t, [17.0])
    c = t.rows[0].cells[0]
    shade(c, 'F7F9FC')
    p = cell_par(c, True)
    run(p, 'Contents', bold=True, size=11, color=NAVY)
    chapters, cur = [], None
    for b in BL:
        if b[0] == 'h':
            cur = [b[1], []]
            chapters.append(cur)
        elif b[0] == 'img' and cur is not None:
            cur[1].append(int(numbers['#' + b[1]]))
    for title, figs in chapters:
        p = cell_par(c, False)
        p.paragraph_format.left_indent = Cm(0.3)
        run(p, title.replace('  ', '   '), size=10.5, color='222222')
        if figs:
            span = f'Figure {figs[0]}' if len(figs) == 1 else f'Figures {figs[0]}–{figs[-1]}'
            run(p, f'   ({span})', size=9.5, color=GREY)
    p = cell_par(c, False)
    p.paragraph_format.left_indent = Cm(0.3)
    run(p, 'References', size=10.5, color='222222')


def render_refs(doc):
    doc.add_heading('References', level=1)
    for key, text, url in REFS:
        p = para(doc, 2, 0.6)
        p.paragraph_format.first_line_indent = Cm(-0.6)
        run(p, f'[{key}] ', bold=True, size=9.5, color='3D4652')
        run(p, text + ' ', size=9.5, color='3D4652')
        if url:
            link(p, url, url, size=9.5)


def main(out, pdf_out=None):
    N = numbers_from_results()
    BL = blocks(N)
    numbers, n_eq, n_fig, n_tab = number_blocks(BL)
    E = Eqs()
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.0)
    s.top_margin, s.bottom_margin = Cm(1.8), Cm(1.7)
    st = doc.styles['Normal']
    st.font.name = 'Arial'
    st.font.size = Pt(11)
    style_headings(doc)
    footer(s)
    break_next = False
    for bi, b in enumerate(BL):
        kind = b[0]
        nxt = BL[bi + 1][0] if bi + 1 < len(BL) else None
        if kind == 'title':
            para(doc, 0, before=60)
            p = para(doc, 8)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run(p, b[1], bold=True, size=24, color=NAVY)
        elif kind == 'subtitle':
            p = para(doc, 18)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run(p, b[1], size=14, color=BLUE2)
        elif kind == 'byline':
            p = para(doc, 30)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run(p, b[1], italic=True, size=10, color=GREY)
        elif kind == 'contents':
            contents(doc, BL, numbers)
        elif kind == 'h':
            h = doc.add_heading(b[1], level=1)
            if break_next:
                h.paragraph_format.page_break_before = True
                break_next = False
        elif kind == 'h2':
            doc.add_heading(b[1], level=2)
        elif kind == 'p':
            p = para(doc, 5)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            mrich(p, b[1], E, size=11, numbers=numbers)
            if nxt == 'eq':
                p.paragraph_format.keep_with_next = True
        elif kind == 'b':
            p = para(doc, 3, 0.5)
            p.paragraph_format.first_line_indent = Cm(-0.35)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run(p, '•  ', bold=True, size=11, color=BLUE2)
            mrich(p, b[1], E, size=11, numbers=numbers)
        elif kind in ('bbox', 'box'):
            t = doc.add_table(rows=1, cols=1)
            if kind == 'box':
                borders(t, '7FB58E', 8)
                fill = 'E6F4EA'
            else:
                borders(t, '9DB8DC', 6)
                fill = 'EEF4FB'
            fixed_widths(t, [17.0])
            c = t.rows[0].cells[0]
            shade(c, fill)
            for k, item in enumerate(b[1]):
                p = cell_par(c, k == 0)
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.space_after = Pt(4)
                mrich(p, item, E, size=10.5, numbers=numbers)
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            if nxt != 'pb':                             # before a new chapter the gap would fall on a page of its own
                para(doc, 6)
        elif kind == 'eq':
            display_eq(doc, E, b[2], numbers[b[1]])
        elif kind == 'img':
            p = para(doc, 2, before=4)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(os.path.join(FIG, b[1] + '.png'), width=Cm(b[2]))
        elif kind == 'cap':
            is_table = b[1].startswith('Table')
            p = para(doc, 8 if not is_table else 3)
            p.paragraph_format.keep_with_next = is_table
            text = numref(b[1], numbers)
            head, _, rest = text.partition('. ')
            run(p, head + '. ', bold=True, size=9.5, color=NAVY)
            mrich(p, rest, E, size=9.5, numbers=numbers, color='3D4652')
        elif kind == 'table':
            hdr, rows_, widths, size = b[1], b[2], b[3], b[4]
            rows = [[numref(c_, numbers) for c_ in r_] for r_ in rows_]
            plain_rows = [[re.sub(r'\*\*|\$', '', c_) for c_ in r_] for r_ in rows]
            t = table(doc, hdr, plain_rows, widths, size=size)
            for i_, r_ in enumerate(rows, start=1):
                for j_, c_ in enumerate(r_):
                    if '$' in c_ or '**' in c_:
                        rich_cell(t.rows[i_].cells[j_], c_, E, numbers, size)
            t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            for r_ in t.rows:
                r_._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            if nxt != 'pb':
                para(doc, 8)
        elif kind == 'pb':
            if nxt == 'h':                              # the chapter opens a page; never an empty page before it
                break_next = True
            else:
                p = para(doc, 0)
                p.add_run().add_break(WD_BREAK.PAGE)
        elif kind == 'refs':
            render_refs(doc)
    work = tempfile.mkdtemp()
    draft = os.path.join(work, 'draft.docx')
    doc.save(draft)
    eq_json = os.path.join(work, 'eqs.json')
    with open(eq_json, 'w', encoding='utf-8') as fh:
        json.dump(E.items, fh, ensure_ascii=False)
    omml.main(draft, eq_json, out)
    print('saved', out, '|', n_eq, 'numbered equations,', len(E.items) - n_eq, 'inline |', n_fig, 'figures |', n_tab,
          'tables')
    if pdf_out:                                         # while the headings have outline levels: PDF bookmarks
        subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', work, out], check=True,
                       capture_output=True, timeout=900)
        os.replace(os.path.join(work, os.path.splitext(os.path.basename(out))[0] + '.pdf'), pdf_out)
        print('saved', pdf_out)
    n_lvl, n_ren = plain_headings(out)
    print(f'  Word file: {n_lvl} outline levels removed, {n_ren} built-in heading styles renamed (no collapse arrows)')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'CERTAIN-COAST_Illustrated_Guide.docx',
         sys.argv[2] if len(sys.argv) > 2 else None)
