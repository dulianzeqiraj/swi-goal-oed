"""TRONDITJA-GO ("tronditja": the jolt): steps 1-3 of the implementation of the TERMETET note (earthquake, aquifer,
liquefaction) and the innovation, as numerical checks. usage: python tronditja_exp.py -> res/tronditja.json, res/tronditja_series.npz

E1  The liquefaction module (Boulanger and Idriss 2014, LPI): structural checks, the derivative (4.9) and the closed form
    for d ln FS / d z_w, an example profile, and the error of re-normalising q_c1Ncs with the earthquake-time stress.
E2  The coseismic step: Okada (1985) for four published source models of the 26 November 2019 Durres earthquake
    (geometry from the abstracts; missing lengths and slips derived from the moment magnitude), areal strain at the
    free surface, the undrained step of a layer under the free surface dp0 = -kappa (de_xx + de_yy) with
    kappa = (2GB/3)(1+nu_u)/(1-nu_u) (soft surface sand against a stiffer confined aquifer, and the note's (2.2) as
    written), its drainage during the shaking, and the earthquake as a natural pumping test (the relaxation identifies
    the leakage time far better than a year of seasons).
E3  The 2019 hindcast, designed on a synthetic coastal plain: how many CPT sites are needed to tell whether the water
    table of the day and the coseismic step improve the prediction of where liquefaction occurred (paired AUC, DeLong).
E4  The innovation: the joint safe window for liquefaction and seawater intrusion at a low port (where it closes with
    relative sea-level rise and the design acceleration), and a daily "if the earthquake happened today" bulletin.
All parameters of the coastal plain, the soils and the ground motion are illustrative; the coordinates are local (km
from the fault centroid), not a map of Durres."""
import json
import os
import time

import numpy as np
from scipy.special import erf, ndtr

import liq
from okada85 import okada85, surface_strain

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
T0 = time.time()
RNG = np.random.default_rng(20261109)

Z = np.arange(0.05, 20.0, 0.1)          # cell centres (m)
DZ = 0.1
GAMMA = 19.0                            # unit weight (kN/m3), the same above and below the water table
M_EQ = 6.4
RHO_G = 9.81                            # kN/m3
NU = 0.25                               # Poisson's ratio of the crust (Okada half-space)
MU = 30e9                               # shear modulus of the crust (Pa), for moment-derived slips
# the undrained step of a layer under the free surface: dp0 = -kappa (de_xx + de_yy), kappa in kPa (liq.areal_kappa)
SOFT = dict(G=50e3, B=0.98, nu_u=0.49)  # loose saturated sand near the surface (shear-wave speed about 160 m/s)
CONF = dict(G=0.5e6, B=0.90, nu_u=0.45)  # confined aquifer in older, stiffer sediment (about 500 m/s)
KAPPA_SOFT = liq.areal_kappa(**SOFT)
KAPPA_CONF = liq.areal_kappa(**CONF)
KAPPA_CONF_BAND = (liq.areal_kappa(0.25e6, 0.90, 0.45), liq.areal_kappa(1.0e6, 0.90, 0.45))   # G 0.25-1 GPa
ALPHA_M = 5.0e6                         # B K_u of the note's (2.2), there applied to the volumetric strain of the crust
KAPPA_NOTE = ALPHA_M * (1 - 2 * NU) / (1 - NU)   # the same per unit areal strain: ev = (1-2nu)/(1-nu) ea at the surface
EA_BIG = 0.75e-6                        # areal strain above which the sign agreement of the models is counted
R = {}
S = {}


def mw_to_potency(mw):
    return 10 ** (1.5 * mw + 9.1) / MU


# ------------------------------------------------------------------------------------------------ E1
print('E1 liquefaction module', flush=True)
E1 = {}
E1['msf_at_7p5'] = float(liq.msf(100.0, 7.5))
E1['ksigma_at_pa'] = float(liq.k_sigma(100.0, liq.PA))
E1['rd_surface'] = float(liq.rd(0.0, M_EQ))
E1['crr_q100'] = float(liq.crr75(100.0))
zz = Z[None, :]
qq = np.full((1, Z.size), 95.0); LL = np.ones_like(qq, bool); GG = np.full_like(qq, GAMMA)
h = 1e-4
fsp, csrp, _, _ = liq.fs_profile(Z, DZ, qq, LL, GG, 1.5 + h, 0.3, M_EQ)
fsm, csrm, _, _ = liq.fs_profile(Z, DZ, qq, LL, GG, 1.5 - h, 0.3, M_EQ)
fsp, fsm = np.where(np.isfinite(fsp), fsp, 1.0), np.where(np.isfinite(fsm), fsm, 1.0)
_, _, _, svp0 = liq.fs_profile(Z, DZ, qq, LL, GG, 1.5, 0.3, M_EQ)
k = Z > 1.7
E1['eq49_max_rel_err'] = float(np.max(np.abs((np.log(csrp) - np.log(csrm))[0, k] / (2 * h) + liq.GW / svp0[0, k])
                                      / (liq.GW / svp0[0, k])))
ksr = 1 - liq.c_sigma(qq) * np.log(np.maximum(svp0, 1) / liq.PA)
k2 = k & (np.abs(ksr[0] - 1.1) > 1e-3)
fd = (np.log(fsp) - np.log(fsm))[0, k2] / (2 * h)
cf = liq.dlnfs_dzw(Z, DZ, qq, GG, 1.5, 0.3, M_EQ)[0, k2]
E1['dlnfs_max_rel_err'] = float(np.max(np.abs(fd - cf) / np.abs(cf)))

# an example coastal profile: crust, three sands separated by silty clays
layers = [(0.0, 1.2, False, 0), (1.2, 4.6, True, 82), (4.6, 6.2, False, 0), (6.2, 9.4, True, 104),
          (9.4, 11.6, False, 0), (11.6, 15.2, True, 132), (15.2, 20.0, False, 0)]
qex = np.zeros(Z.size); lex = np.zeros(Z.size, bool)
rng_cpt = np.random.default_rng(31)
jit = np.zeros(Z.size)                              # CPT-like jitter: AR(1) with a 0.3 m correlation length
for i in range(1, Z.size):
    jit[i] = np.exp(-DZ / 0.3) * jit[i - 1] + np.sqrt(1 - np.exp(-2 * DZ / 0.3)) * rng_cpt.standard_normal()
for a, b, isl, qv in layers:
    sel = (Z >= a) & (Z < b)
    lex[sel] = isl
    qex[sel] = qv * np.exp(0.09 * jit[sel]) if isl else 0
qex = np.where(lex, qex, 30.0)
ex = {}
for zw in (0.8, 1.6, 2.6):
    fs, csr, crr, svp = liq.fs_profile(Z, DZ, qex, lex, GAMMA, zw, 0.25, M_EQ)
    ex[str(zw)] = dict(lpi=float(liq.lpi(Z, DZ, fs)))
    S[f'e1_fs_{zw}'] = np.where(np.isfinite(fs), fs, np.nan); S[f'e1_csr_{zw}'] = csr; S[f'e1_crr_{zw}'] = crr
S['e1_z'] = Z; S['e1_q'] = np.where(lex, qex, np.nan); S['e1_liq'] = lex
E1['example'] = ex
zw_grid = np.linspace(0.3, 6.0, 115)
for a in (0.15, 0.25, 0.35):
    S[f'e1_lpi_a{a}'] = np.array([liq.lpi_profile(Z, DZ, qex, lex, GAMMA, w, a, M_EQ) for w in zw_grid])
S['e1_zw_grid'] = zw_grid
# the error of re-normalising the density index with the earthquake-time stress (CPT made with z_w = 2.0 m)
_, _, svp_cpt = liq.stresses(Z, DZ, GAMMA, 2.0)
lpi_right, lpi_wrong = [], []
for w in zw_grid:
    _, _, svp_eq = liq.stresses(Z, DZ, GAMMA, w)
    qw = np.where(lex, liq.cn_renormalise(qex, svp_cpt, svp_eq), qex)
    lpi_right.append(liq.lpi_profile(Z, DZ, qex, lex, GAMMA, w, 0.25, M_EQ))
    lpi_wrong.append(liq.lpi_profile(Z, DZ, qw, lex, GAMMA, w, 0.25, M_EQ))
lpi_right, lpi_wrong = np.array(lpi_right), np.array(lpi_wrong)
S['e1_lpi_right'] = lpi_right; S['e1_lpi_wrong'] = lpi_wrong
sl_r = np.polyfit(zw_grid[(zw_grid >= 0.8) & (zw_grid <= 2.6)], lpi_right[(zw_grid >= 0.8) & (zw_grid <= 2.6)], 1)[0]
sl_w = np.polyfit(zw_grid[(zw_grid >= 0.8) & (zw_grid <= 2.6)], lpi_wrong[(zw_grid >= 0.8) & (zw_grid <= 2.6)], 1)[0]
E1['lpi_slope_per_m'] = dict(right=float(sl_r), renormalised=float(sl_w), understated=float(1 - sl_w / sl_r))
R['E1'] = E1
print(f'  example LPI {[round(v["lpi"], 1) for v in ex.values()]}; slope {sl_r:.2f} vs {sl_w:.2f} per m', flush=True)

# ------------------------------------------------------------------------------------------------ E2
print('E2 coseismic step', flush=True)
# four published source models (abstracts in Crossref); strike from the NW-SE trend of the structure (N160 deg),
# set by the dip direction; lengths and slips derived from Mw where the abstract gives none (uniform slip)
SOURCES = [
    dict(key='ganas', label='Ganas et al. 2020', strike=340.0, dip=23.0, depth=16.5e3, L=22e3, W=13e3, slip=0.55,
         note='dip 23 E, centroid 16.5 km, 22 x 13 km, 0.55 m (abstract)'),
    dict(key='matraku', label='Matraku et al. 2023', strike=340.0, dip=40.0, depth=15e3, L=20e3, W=11e3,
         slip=mw_to_potency(6.38) / (20e3 * 11e3), note='dip 40 E, 15 km, Mw 6.38, max slip 1.4 m (abstract); '
                                                     '20 x 11 km and uniform slip from Mw (here)'),
    dict(key='govorcin', label='Govorcin et al. 2020', strike=150.0, dip=71.0, depth=17e3, L=18e3,
         W=12e3 / np.sin(np.radians(71.0)), slip=mw_to_potency(6.3) / (18e3 * 12e3 / np.sin(np.radians(71.0))),
         note='dip 71 SW, slip at 11-23 km, Mw 6.3 (abstract); L 18 km and uniform slip from Mw (here)'),
    dict(key='vdheiden', label='van der Heiden et al. 2026', strike=315.0, dip=30.0, depth=15e3, L=20e3,
         W=6e3 / np.sin(np.radians(30.0)), slip=mw_to_potency(6.4) / (20e3 * 6e3 / np.sin(np.radians(30.0))),
         note='about 30 NE, 12-18 km, M 6.4 (abstract); L 20 km and uniform slip from Mw (here)'),
]
xg = np.linspace(-40e3, 40e3, 161)
XE, XN = np.meshgrid(xg, xg)
E2 = {'sources': [], 'alpha_M_kPa': ALPHA_M}
dh_stack, ea_stack = [], []
for src in SOURCES:
    args = (src['depth'], src['strike'], src['dip'], src['L'], src['W'], 90.0, src['slip'])
    _, _, uz = okada85(XE, XN, *args, nu=NU)
    exx, eyy, _, ev = surface_strain(XE, XN, *args, nu=NU)
    ea = exx + eyy
    dh = -KAPPA_CONF * ea / RHO_G                   # head step in the confined aquifer (m)
    dh_soft = -KAPPA_SOFT * ea / RHO_G              # in the soft surface sand
    dh_note = -ALPHA_M * ev / RHO_G                 # the note's (2.2) as written
    S[f'e2_uz_{src["key"]}'] = uz.astype(np.float32); S[f'e2_dh_{src["key"]}'] = dh.astype(np.float32)
    S[f'e2_ea_{src["key"]}'] = ea.astype(np.float32)
    dh_stack.append(dh); ea_stack.append(ea)
    mw = (np.log10(MU * src['slip'] * src['L'] * src['W']) - 9.1) / 1.5
    E2['sources'].append(dict(key=src['key'], label=src['label'], strike=src['strike'], dip=src['dip'],
                              depth_km=src['depth'] / 1e3, L_km=src['L'] / 1e3, W_km=src['W'] / 1e3,
                              slip_m=float(src['slip']), mw=float(mw), note=src['note'],
                              uz_max_m=float(uz.max()), uz_min_m=float(uz.min()),
                              ev_max=float(ev.max()), ev_min=float(ev.min()), ea_max=float(ea.max()),
                              ea_min=float(ea.min()), dh_conf_max_m=float(dh.max()), dh_conf_min_m=float(dh.min()),
                              dh_soft_max_m=float(dh_soft.max()), dh_soft_min_m=float(dh_soft.min()),
                              dh_note_max_m=float(dh_note.max()), dh_note_min_m=float(dh_note.min()),
                              area_dh_conf_gt_10cm_km2=float(np.sum(np.abs(dh) > 0.1) * (0.5 ** 2))))
    print(f"  {src['label']}: Mw {mw:.2f}, uz {uz.min():+.3f}..{uz.max():+.3f} m, dh confined {dh.min():+.2f}.."
          f"{dh.max():+.2f} m, soft sand {dh_soft.min():+.3f}..{dh_soft.max():+.3f} m", flush=True)
dh_stack, ea_stack = np.array(dh_stack), np.array(ea_stack)
agree = np.abs(np.sum(np.sign(ea_stack), axis=0)) == 4
S['e2_dh_mean'] = dh_stack.mean(0).astype(np.float32); S['e2_dh_sd'] = dh_stack.std(0).astype(np.float32)
S['e2_agree'] = agree; S['e2_x'] = xg
big = np.max(np.abs(ea_stack), axis=0) > EA_BIG
S['e2_big'] = big
E2['ea_big'] = EA_BIG
E2['sign_agreement_where_any_ea_gt_big'] = float(np.mean(agree[big]))
E2['kappa_kPa'] = dict(soft=KAPPA_SOFT, confined=KAPPA_CONF, confined_band=list(KAPPA_CONF_BAND), note=KAPPA_NOTE)
E2['layers'] = dict(soft=SOFT, confined=CONF)
E2['dh_per_areal_microstrain_m'] = dict(soft=KAPPA_SOFT * 1e-6 / RHO_G, confined=KAPPA_CONF * 1e-6 / RHO_G,
                                        note=KAPPA_NOTE * 1e-6 / RHO_G)
E2['note_over_soft'] = KAPPA_NOTE / KAPPA_SOFT; E2['note_over_confined'] = KAPPA_NOTE / KAPPA_CONF
# transect across the strike of the Ganas model, through the centroid
az = np.radians(340.0 + 90.0)
s_tr = np.linspace(-35e3, 35e3, 281)
tr = {}
for src in SOURCES:
    args = (src['depth'], src['strike'], src['dip'], src['L'], src['W'], 90.0, src['slip'])
    exx, eyy, _, _ = surface_strain(s_tr * np.sin(az), s_tr * np.cos(az), *args, nu=NU)
    tr[src['key']] = exx + eyy
    S[f'e2_tr_{src["key"]}'] = -KAPPA_CONF * tr[src['key']] / RHO_G
S['e2_tr_s'] = s_tr
S['e2_tr_soft_mean'] = -KAPPA_SOFT * np.mean([tr[k] for k in tr], axis=0) / RHO_G
# drainage during the shaking: share of the step left after 15 s in sand connected to the water table
Ls = np.array([0.5, 1, 2, 3, 5, 8, 12])
E2['share_left_after_15s'] = {f'{L:g} m': float(erf(L / (2 * np.sqrt(1.0 * 15.0)))) for L in Ls}
# the earthquake as a natural pumping test: a confined sand below a leaky clay relaxes as exp(-t/tau)
tau_true, dh0_true, noise = 3.0, 0.3, 0.02          # days, m, m (15-min logger in the confined aquifer)
t_eq = np.arange(0, 20, 1 / 96)
obs = dh0_true * np.exp(-t_eq / tau_true) + noise * RNG.standard_normal(t_eq.size)
from scipy.optimize import curve_fit
f_exp = lambda t, a, tau: a * np.exp(-t / tau)
popt, pcov = curve_fit(f_exp, t_eq, obs, p0=(0.5, 1.0))
boot = []
for _ in range(300):
    ob = popt[0] * np.exp(-t_eq / popt[1]) + noise * RNG.standard_normal(t_eq.size)
    boot.append(curve_fit(f_exp, t_eq, ob, p0=popt)[0][1])
ci_eq = np.quantile(boot, [0.025, 0.975])
# the same leakage time from one year of seasonal forcing: a leaky aquifer follows a seasonal drive with a phase lag
# atan(omega tau); with daily heads (2 cm noise) and an amplitude of 0.5 m the lag is barely resolved
omega = 2 * np.pi / 365.25
t_yr = np.arange(0, 365.25, 1.0)
lag_hat = []
for _ in range(300):
    hs = 0.5 * np.cos(omega * t_yr - np.arctan(omega * tau_true)) + noise * RNG.standard_normal(t_yr.size)
    A = np.column_stack([np.cos(omega * t_yr), np.sin(omega * t_yr)])
    c, s_ = np.linalg.lstsq(A, hs, rcond=None)[0]
    lag_hat.append(np.tan(np.arctan2(s_, c)) / omega)
ci_season = np.quantile(lag_hat, [0.025, 0.975])
E2['natural_test'] = dict(tau_true_d=tau_true, tau_hat_d=float(popt[1]), ci95_quake_d=[float(v) for v in ci_eq],
                          ci95_season_d=[float(v) for v in ci_season],
                          width_ratio=float((ci_season[1] - ci_season[0]) / (ci_eq[1] - ci_eq[0])))
S['e2_relax_t'] = t_eq; S['e2_relax_obs'] = obs; S['e2_relax_fit'] = f_exp(t_eq, *popt)
R['E2'] = E2
print(f'  sign agreement {E2["sign_agreement_where_any_ea_gt_big"]:.2f}; tau CI quake {ci_eq.round(2)}, '
      f'season {ci_season.round(2)}', flush=True)

# ------------------------------------------------------------------------------------------------ E3
print('E3 hindcast design', flush=True)
# a synthetic coastal plain over the fault models: coast striking N160, 10 km WSW of the centroid
NPOOL = 900
gx = np.linspace(-30, 30, 241)
GX, GY = np.meshgrid(gx, gx)
white = RNG.standard_normal(GX.shape)
# anisotropic smoothing, elongated along N160 (the structural trend of the liquefaction zones)
kx = np.fft.fftfreq(gx.size, d=gx[1] - gx[0])
KX, KY = np.meshgrid(kx, kx)
th = np.radians(340.0)
ka = KX * np.sin(th) + KY * np.cos(th); kb = KX * np.cos(th) - KY * np.sin(th)
field = np.real(np.fft.ifft2(np.fft.fft2(white) * np.exp(-(2 * np.pi) ** 2 * ((6.0 * ka) ** 2 + (1.6 * kb) ** 2) / 2)))
field = (field - field.mean()) / field.std()
S['e3_field'] = field.astype(np.float32); S['e3_gx'] = gx
coast_x = lambda y: -10.0 - 0.364 * y              # km
ys = RNG.uniform(-24, 24, NPOOL * 3)
dcs = RNG.uniform(0.2, 8.0, NPOOL * 3)
xs = coast_x(ys) + dcs / np.cos(np.radians(20.0))
keep = (np.abs(xs) < 29) & (np.abs(ys) < 29)
xs, ys, dcs = xs[keep][:NPOOL], ys[keep][:NPOOL], dcs[keep][:NPOOL]
ix = np.clip(np.searchsorted(gx, xs), 0, gx.size - 1); iy = np.clip(np.searchsorted(gx, ys), 0, gx.size - 1)
susc = field[iy, ix]
n = xs.size


def profiles(nsite, susc_vec, rng, sand_base=0.25, sand_amp=0.35, q_med=100.0, crust=(0.5, 2.0)):
    """Layered profiles: a non-liquefiable crust, then sands and silty clays as a two-state Markov chain whose sand
    share follows the susceptibility; sand density index lognormal around 95, increasing with depth."""
    liqm = np.zeros((nsite, Z.size), bool)
    q = np.full((nsite, Z.size), 30.0)
    psand = sand_base + sand_amp * ndtr(susc_vec)
    for i in range(nsite):
        z = rng.uniform(*crust)
        while z < 20.0:
            is_sand = rng.uniform() < psand[i]
            thick = rng.exponential(2.2 if is_sand else 1.6) + 0.3
            sel = (Z >= z) & (Z < z + thick)
            if is_sand:
                liqm[i, sel] = True
                q[i, sel] = np.exp(rng.normal(np.log(q_med) + 0.012 * z, 0.22))
            z += thick
    return q, liqm


qP, lP = profiles(n, susc, RNG)
zbar = np.clip(0.6 + 0.35 * dcs + 0.3 * RNG.standard_normal(n), 0.3, 4.0)
amp = 0.45 + 0.08 * dcs
day_eq = 330.0                                      # 26 November
zw_eq = np.clip(zbar - amp * np.cos(2 * np.pi * (day_eq - 35.0) / 365.25), 0.2, None)
Rh = np.sqrt((xs * 1e3) ** 2 + (ys * 1e3) ** 2 + 16.5e3 ** 2) / 1e3
amax_med = 0.22 * ((Rh + 10) / (20 + 10)) ** -1.0
amax_true = amax_med * np.exp(0.30 * RNG.standard_normal(n))
ea_src = {}
for src in SOURCES:
    args = (src['depth'], src['strike'], src['dip'], src['L'], src['W'], 90.0, src['slip'])
    exx, eyy, _, _ = surface_strain(xs * 1e3, ys * 1e3, *args, nu=NU)
    ea_src[src['key']] = exx + eyy
# the most favourable case for the test: the step of the note's (2.2) as written (KAPPA_NOTE) in the truth and in M2, M3;
# M4 uses the coefficient of the soft surface sand
dp_true = -KAPPA_NOTE * ea_src['ganas']              # kPa
dp_ens = -KAPPA_NOTE * np.mean([ea_src[k] for k in ea_src], axis=0)
dp_soft = -KAPPA_SOFT * ea_src['ganas']


def site_lpi(zw, dp, amax):
    f = liq.drainage_factor(Z, lP, zw) if np.any(dp != 0) else 0.0
    return liq.lpi_profile(Z, DZ, qP, lP, GAMMA, zw[:, None], amax[:, None], M_EQ, dp=dp[:, None] * f)


lpi_true = site_lpi(zw_eq, dp_true, amax_true)
p_obs = 1 / (1 + np.exp(-(lpi_true - 5.0) / 1.5))
obs_liq = (RNG.uniform(size=n) < p_obs).astype(int)
pred = dict(M0=site_lpi(zbar, np.zeros(n), amax_med),
            M1=site_lpi(zw_eq, np.zeros(n), amax_med),
            M2=site_lpi(zw_eq, dp_ens, amax_med),
            M3=site_lpi(zw_eq, dp_true, amax_med),
            M4=site_lpi(zw_eq, dp_soft, amax_med))


def delong(y, *scores):
    """AUCs and their covariance (DeLong et al. 1988) for scores on the same cases."""
    pos, neg = y == 1, y == 0
    V10, V01, aucs = [], [], []
    for s in scores:
        X, Y = s[pos][:, None], s[neg][None, :]
        psi = (X > Y) + 0.5 * (X == Y)
        V10.append(psi.mean(1)); V01.append(psi.mean(0)); aucs.append(psi.mean())
    S10, S01 = np.cov(np.array(V10)), np.cov(np.array(V01))
    return np.array(aucs), S10 / pos.sum() + S01 / neg.sum()


aucs, cov = delong(obs_liq, *[pred[k] for k in ('M0', 'M1', 'M2', 'M3')])
E3 = dict(n_pool=int(n), liquefied_share=float(obs_liq.mean()),
          auc_full_pool={k: float(a) for k, a in zip(('M0', 'M1', 'M2', 'M3'), aucs)},
          dp_true_kPa=dict(min=float(dp_true.min()), max=float(dp_true.max())),
          dp_soft_kPa=dict(min=float(dp_soft.min()), max=float(dp_soft.max())),
          lpi_change_from_step=dict(median_abs=float(np.median(np.abs(pred['M3'] - pred['M1']))),
                                    p90_abs=float(np.quantile(np.abs(pred['M3'] - pred['M1']), 0.9))),
          lpi_change_soft=dict(median_abs=float(np.median(np.abs(pred['M4'] - pred['M1']))),
                               p90_abs=float(np.quantile(np.abs(pred['M4'] - pred['M1']), 0.9)),
                               max_abs=float(np.max(np.abs(pred['M4'] - pred['M1'])))))
NS = [30, 60, 120, 240, 480]
power = {'season (M1 vs M0)': [], 'step, ensemble source (M2 vs M1)': [], 'step, true source (M3 vs M1)': []}
for N in NS:
    hits = np.zeros(3)
    for _ in range(400):
        idx = RNG.choice(n, N, replace=False)
        y = obs_liq[idx]
        if y.sum() < 5 or (1 - y).sum() < 5:
            continue
        a, C = delong(y, *[pred[k][idx] for k in ('M0', 'M1', 'M2', 'M3')])
        for j, (i1, i0) in enumerate(((1, 0), (2, 1), (3, 1))):
            var = C[i1, i1] + C[i0, i0] - 2 * C[i1, i0]
            if var > 0 and (a[i1] - a[i0]) / np.sqrt(var) > 1.645:
                hits[j] += 1
    for j, key in enumerate(power):
        power[key].append(float(hits[j] / 400))
E3['n_sites'] = NS; E3['power'] = power
S['e3_x'] = xs; S['e3_y'] = ys; S['e3_obs'] = obs_liq; S['e3_lpi_true'] = lpi_true
for k_ in pred:
    S[f'e3_{k_}'] = pred[k_]
S['e3_dp_true'] = dp_true; S['e3_dp_soft'] = dp_soft; S['e3_ea'] = ea_src['ganas']
R['E3'] = E3
print(f'  AUC {E3["auc_full_pool"]}; power {power}', flush=True)

# ------------------------------------------------------------------------------------------------ E4
print('E4 joint window and daily bulletin', flush=True)
NPORT = 60
qp, lp = profiles(NPORT, np.zeros(NPORT), RNG, sand_base=0.45, sand_amp=0.0, q_med=125.0, crust=(1.0, 2.0))
ZS_PORT = 2.0          # ground elevation above mean sea level (m)
LPI_MAX = 5.0
M_INT = 20.0 / 40.0    # fresh head above sea level that keeps the interface 20 m deep (Ghyben-Herzberg, 3.7)
A_SEAS = 0.30          # residual seasonal swing of the managed head (m)
amax_grid = np.linspace(0.10, 0.45, 36)
zw_grid4 = np.arange(0.0, 8.01, 0.05)
zstar = np.zeros((NPORT, amax_grid.size))
for j, a in enumerate(amax_grid):
    L4 = np.array([liq.lpi_profile(Z, DZ, qp, lp, GAMMA, w, a, M_EQ) for w in zw_grid4])   # (nzw, NPORT)
    over = L4 > LPI_MAX
    last = np.where(over.any(0), zw_grid4.size - 1 - np.argmax(over[::-1], axis=0), -1)
    zstar[:, j] = np.where(last >= 0, zw_grid4[np.minimum(last + 1, zw_grid4.size - 1)], 0.0)
zstar_cert = np.quantile(zstar, 0.9, axis=0)              # water-table depth that keeps 90% of the port safe
eta_grid = np.linspace(0.0, 1.2, 121)
width = (ZS_PORT - zstar_cert[None, :]) - (eta_grid[:, None] + M_INT)
eta_close = ZS_PORT - zstar_cert - M_INT - A_SEAS        # all-year window closes here
S['e4_amax'] = amax_grid; S['e4_eta'] = eta_grid; S['e4_width'] = width; S['e4_zstar'] = zstar
S['e4_zstar_cert'] = zstar_cert; S['e4_eta_close'] = eta_close
E4 = dict(z_s=ZS_PORT, lpi_max=LPI_MAX, m_int=M_INT, a_seas=A_SEAS,
          zstar_cert_at={f'{a:.2f}': float(zstar_cert[np.argmin(np.abs(amax_grid - a))]) for a in (0.15, 0.25, 0.35)},
          eta_close_at={f'{a:.2f}': float(eta_close[np.argmin(np.abs(amax_grid - a))]) for a in (0.15, 0.25, 0.35)},
          amax_window_open_today=float(amax_grid[eta_close >= 0].max()) if np.any(eta_close >= 0) else None,
          window_table=[dict(amax=float(amax_grid[j]), zstar_cert=float(zstar_cert[j]),
                             zstar_median=float(np.median(zstar[:, j])), eta_close=float(eta_close[j]))
                        for j in [int(np.argmin(np.abs(amax_grid - a))) for a in (0.15, 0.18, 0.20, 0.22, 0.25)]])
# the daily bulletin: natural water table at the port through 2027, design earthquake M 6.4, a_max 0.22 g (lognormal)
days = np.arange(365)
zw_day = np.clip(1.45 + 0.55 * np.cos(2 * np.pi * (days - 35 - 182.6) / 365.25), 0.3, None)
NDRAW = 12
a_draw = 0.22 * np.exp(0.35 * RNG.standard_normal(NDRAW))
lpi_day = np.zeros((days.size, NPORT * NDRAW))
for d in days:
    vals = [liq.lpi_profile(Z, DZ, qp, lp, GAMMA, zw_day[d], a, M_EQ) for a in a_draw]
    lpi_day[d] = np.concatenate(vals)
q05, q50, q95 = np.quantile(lpi_day, [0.05, 0.5, 0.95], axis=1)
pexc = np.mean(lpi_day > LPI_MAX, axis=1)
S['e4_days'] = days; S['e4_zw_day'] = zw_day; S['e4_lpi_q05'] = q05; S['e4_lpi_q50'] = q50; S['e4_lpi_q95'] = q95
S['e4_pexc'] = pexc
E4['bulletin'] = dict(pexc_min=float(pexc.min()), pexc_max=float(pexc.max()), day_max=int(np.argmax(pexc)),
                      day_min=int(np.argmin(pexc)), lpi_median_range=[float(q50.min()), float(q50.max())],
                      zw_range=[float(zw_day.min()), float(zw_day.max())], n_draw=NDRAW, n_port=NPORT)
R['E4'] = E4
print(f'  z* (90%) at 0.25 g: {E4["zstar_cert_at"]["0.25"]:.2f} m; window closes at eta {E4["eta_close_at"]}; '
      f'P(LPI>5) {pexc.min():.2f}..{pexc.max():.2f}', flush=True)

R['setup'] = dict(z_max=20.0, dz=DZ, gamma=GAMMA, M=M_EQ, alpha_M_kPa=ALPHA_M, kappa_kPa=E2['kappa_kPa'],
                  nu=NU, mu_Pa=MU, design_note='illustrative soils, ground motion and coastal plain; local coordinates')
R['runtime_s'] = time.time() - T0
os.makedirs(RES, exist_ok=True)
with open(os.path.join(RES, 'tronditja.json'), 'w') as fh:
    json.dump(R, fh, indent=1)
np.savez_compressed(os.path.join(RES, 'tronditja_series.npz'), **S)
print(f'saved res/tronditja.json ({R["runtime_s"]:.0f} s)')
