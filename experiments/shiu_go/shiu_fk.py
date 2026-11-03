"""SHIU-GO on Fushe-Kuqe with the static data of the workbook (appendix A of the note).

The workbook has no time series (rain, heads, pumping, sea level), so the dynamic routes A and B cannot be fitted
yet. What the static data and the calibrated areal model of the chloride study (chloride_fk/) can already say:

S1  Scale. The calibrated model div(K grad phi) + R = 0, K = eta K_IDW exp(theta), is homogeneous of degree one in
    (R, K): phi, heads, interface and chloride depend on R and eta only through R/eta. Checked on the model, and
    read off the 20 000-draw calibration (chloride_fk/results/calib_ensemble.npz): what the four documented facts
    fix (R/eta) and what only the K data fix (eta).
S2  Value of recharge. Share of the potential of the coastal band (SW/Adriatic band of the calibration: y 30-40 km,
    0.5-2.5 km from the shoreline, where wells 341 and 503 sample the second aquifer) that comes from recharge on
    each cell: one adjoint solve per posterior draw, 300 draws resampled by the calibration weights. The shares do
    not depend on R or eta (S1), only on the zone multipliers theta.
S3  Cover. The DRASTIC depth parameter (depth to the top of the confined aquifer, 43 wells, IDW as in the chloride
    model) in three classes; the nitrate tracer at the 31 wells with nitrate.
S4  Head loggers. Inside the sector the cover is nearly uniform (about 30 m), so the recharge zones that steady
    heads could tell apart are the north-south bands (the workbook names the Mat in the north and the Droja in the
    south as the river sources). Which 3 or 5 of the K-wells in the sector best separate the recharge of the bands
    y 24-30, 30-40 and >= 40 km (D-optimal for the two log-ratios, the scale log(R/eta) as nuisance), and the
    collinearity of other splits (Proposition 3 of the note on the real geometry).

usage: python shiu_fk.py   (writes res/shiu_fk.json)"""
import itertools
import json
import os
import sys

import numpy as np
import pandas as pd
import scipy.sparse.linalg as spla
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'chloride_fk', 'python'))
import fkcl_model as M  # noqa: E402
from fkcl_calib import masks  # noqa: E402

XLSX = os.path.join(ROOT, 'data', 'Fushe_Kuqe_All_Data.xlsx')
ENS = os.path.join(ROOT, 'chloride_fk', 'results', 'calib_ensemble.npz')
MMYR = 365.25 * 1000.0                      # m/d -> mm/yr
COVER_CLASSES = [(0.0, 15.0), (15.0, 30.0), (30.0, 1e9)]          # whole aquifer (nitrate test)
COVER_NAMES = ['thin', 'medium', 'thick']
SOIL_GROUP = {'Absent': 'G1', 'Thin': 'G1', 'Sandy silt': 'G2', 'Dusty silt': 'G2', 'Clayey silt': 'G3'}
BANDS = [(24.0, 30.0), (30.0, 40.0), (40.0, 1e9)]                 # north-south recharge bands of the sector
BAND_NAMES = ['south', 'middle', 'north']
NDRAW = 300
SIGS = (0.1, 1.0)                           # m, error of a mean head: optimistic, and the 1 m of the calibration


def wquant(x, w, qs=(0.05, 0.5, 0.95)):
    i = np.argsort(x); c = np.cumsum(w[i]); c /= c[-1]
    return [float(np.interp(q, c, x[i])) for q in qs]


def wvar(a, w):
    mu = (w * a).sum(); return float((w * (a - mu) ** 2).sum())


def wcorr(a, b, w):
    ma, mb = (w * a).sum(), (w * b).sum()
    return float((w * (a - ma) * (b - mb)).sum() / np.sqrt((w * (a - ma) ** 2).sum() * (w * (b - mb) ** 2).sum()))


def draw(z, i):
    return dict(theta=z['theta'][i], R=float(z['R'][i]), eta=float(z['eta'][i]), b_c=float(z['b_c'][i]),
                b_e=float(z['b_e'][i]), L_B=float(z['L_B'][i]), ground=float(z['ground'][i]), w=float(z['w'][i]),
                Cl_s=float(z['Cl_s'][i]))


def main():
    m = M.Model(XLSX)
    z = np.load(ENS)
    w = z['weight'] / z['weight'].sum()
    u = np.full(len(w), 1.0 / len(w))
    res = {}

    # ---------------------------------------------------------------- S1 scale invariance and what the facts fix
    p = draw(z, int(np.argmax(w)))
    o1 = m.run(p)
    errs = []
    for c in (0.37, 2.7, 10.0):
        q = dict(p); q['R'] = c * p['R']; q['eta'] = c * p['eta']
        o2 = m.run(q)
        for k in ('phi', 'h', 'zeta', 'Cl_sh', 'Cl_mid', 'Cl_dp'):
            a, b = o1[k][m.valid], o2[k][m.valid]
            errs.append(float(np.max(np.abs(a - b) / (np.abs(a) + 1e-9))))
    lr, le = np.log10(z['R']), np.log10(z['eta'])
    S1 = dict(invariance_max_rel=max(errs))
    for name, x in (('logR', lr), ('logeta', le), ('logReta', lr - le)):
        pq, qq = wquant(x, u), wquant(x, w)
        S1[name] = dict(prior=pq, post=qq, prior_w90=pq[2] - pq[0], post_w90=qq[2] - qq[0])
    S1['R_mmyr_post'] = [10 ** v * MMYR for v in S1['logR']['post']]
    S1['R_mmyr_prior'] = [10 ** v * MMYR for v in S1['logR']['prior']]
    S1['eta_post'] = wquant(z['eta'], w)
    S1['corr_prior'] = wcorr(lr, le, u); S1['corr_post'] = wcorr(lr, le, w)
    S1['var_logR'] = wvar(lr, w); S1['var_logReta'] = wvar(lr - le, w); S1['var_logeta'] = wvar(le, w)
    S1['share_var_from_K_scale'] = S1['var_logeta'] / S1['var_logR']
    S1['ess'] = float(1.0 / np.sum(w ** 2))
    res['S1'] = S1

    W = pd.read_excel(XLSX, sheet_name='2_All_Wells')
    x0, y0 = m.base.x0, m.base.y0
    W['x_km'] = (W['X_GaussKruger'] - x0) / 1000.0; W['y_km'] = (W['Y_GaussKruger'] - y0) / 1000.0
    W['depth'] = W['Piezometric_Level_m']
    Wd = W[W['depth'].notna()].copy()
    Wd['group'] = Wd['Land_Use_Soil'].map(SOIL_GROUP)
    # ---------------------------------------------------------------- S2 value of recharge (adjoint shares)
    mk = masks(m)
    band = mk['sw']
    valid = m.valid
    nv = int(valid.sum())
    g = np.where(band, 1.0 / band.sum(), 0.0)
    rng = np.random.default_rng(2026)
    idx = rng.choice(len(w), size=NDRAW, replace=True, p=w)
    shares = np.zeros((NDRAW, m.Nc))
    for r, i in enumerate(idx):
        d_ = draw(z, i)
        A = m.matrix(m.K_field(d_['theta'], d_['eta']))
        lam = spla.spsolve(A, g)                     # A is symmetric: the adjoint solve is a forward solve
        V = np.where(valid, lam * m.area, 0.0)
        shares[r] = V / V.sum()
        if r == 0:                                    # check: uniform recharge gives band-mean phi = R * sum(V)
            phi = m.solve_phi(m.K_field(d_['theta'], d_['eta']), d_['R'])
            res['S2_check_rel'] = float(abs(phi[band].mean() - d_['R'] * V.sum()) / phi[band].mean())
    dens = shares * nv                                 # value per unit area relative to the sector average
    cover, dist, cy = m.cover, m.dist, m.cy
    regions = {
        'dist_0_2.5': (dist < 2.5), 'dist_2.5_5': (dist >= 2.5) & (dist < 5), 'dist_5_10': (dist >= 5) & (dist < 10),
        'dist_10+': (dist >= 10),
        'y_24_30': (cy < 30), 'y_30_40': (cy >= 30) & (cy < 40), 'y_40+': (cy >= 40),
    }
    regions['cover_lt30'] = cover < 30.0
    regions['cover_ge30'] = cover >= 30.0
    S2 = dict(n_valid=nv, n_band=int(band.sum()), area_km2=nv * m.area / 1e6, regions={})
    for nm, msk in regions.items():
        msk = msk & valid
        sh = shares[:, msk].sum(1)
        S2['regions'][nm] = dict(area_frac=float(msk.sum() / nv), share=[float(v) for v in np.quantile(sh, [0.05, 0.5, 0.95])])
    md = np.median(dens, 0)
    near = np.argmin(np.hypot(m.cx[:, None] - Wd['x_km'].to_numpy()[None, :],
                              m.cy[:, None] - Wd['y_km'].to_numpy()[None, :]), 1)
    cell_group = Wd['group'].to_numpy()[near]
    S2['soil_groups'] = {}
    for gname in ('G1', 'G2', 'G3'):
        msk = valid & (cell_group == gname)
        sh = shares[:, msk].sum(1)
        S2['soil_groups'][gname] = dict(area_frac=float(msk.sum() / nv),
                                       share=[float(v) for v in np.quantile(sh, [0.05, 0.5, 0.95])])
    S2['thin_cover_area_frac'] = float((valid & (cover < 15.0)).sum() / nv)
    S2['dens_quantiles'] = [float(v) for v in np.quantile(md[valid], [0.05, 0.25, 0.5, 0.75, 0.95])]
    S2['dens_band'] = float(np.median(md[band]))
    # value per unit area beyond 10 km from the shore, relative to the band itself (does far recharge count fully?)
    far = valid & (dist >= 10)
    S2['dens_far_median'] = float(np.median(md[far]))
    res['S2'] = S2

    # ---------------------------------------------------------------- S3 cover classes and the nitrate tracer
    N = Wd[Wd['NO3_mg_per_L'].notna()]
    S3 = dict(n_depth=int(len(Wd)), n_no3=int(len(N)))
    rr = {}
    for c in ('depth', 'x_km', 'y_km', 'K_m_per_day'):
        r_, p_ = stats.spearmanr(N['NO3_mg_per_L'], N[c]); rr[c] = [float(r_), float(p_)]
    S3['spearman_all'] = rr
    Ns = N[N['y_km'] >= M.Y_CUT]
    r_, p_ = stats.spearmanr(Ns['NO3_mg_per_L'], Ns['depth'])
    S3['sector'] = dict(n=int(len(Ns)), spearman_depth=[float(r_), float(p_)],
                        no3_range=[float(Ns['NO3_mg_per_L'].min()), float(Ns['NO3_mg_per_L'].max())],
                        no3_median=float(Ns['NO3_mg_per_L'].median()))
    Nn = N[N['y_km'] < M.Y_CUT]
    S3['south'] = dict(n=int(len(Nn)), no3_median=float(Nn['NO3_mg_per_L'].median()),
                       no3_range=[float(Nn['NO3_mg_per_L'].min()), float(Nn['NO3_mg_per_L'].max())])
    cls = {}
    for (lo, hi), nm in zip(COVER_CLASSES, COVER_NAMES):
        sel = N[(N['depth'] >= lo) & (N['depth'] < hi)]
        cls[nm] = dict(n=int(len(sel)), no3_median=float(sel['NO3_mg_per_L'].median()),
                       no3_max=float(sel['NO3_mg_per_L'].max()))
    S3['no3_by_cover'] = cls
    # permutation p-value for the difference thin vs the rest (one-sided: thin higher)
    thin = N['depth'] < 15
    obs = np.median(N.loc[thin, 'NO3_mg_per_L']) - np.median(N.loc[~thin, 'NO3_mg_per_L'])
    prm = np.random.default_rng(7)
    vals = N['NO3_mg_per_L'].to_numpy(); t = thin.to_numpy()
    cnt = 0
    for _ in range(20000):
        pp = prm.permutation(t)
        cnt += (np.median(vals[pp]) - np.median(vals[~pp])) >= obs
    S3['thin_vs_rest'] = dict(diff_median=float(obs), p_perm=float((cnt + 1) / 20001))
    # soil and vadose classes of the 43 wells (counts), and their cover depths
    S3['soil_counts'] = {k: int(v) for k, v in Wd['Land_Use_Soil'].value_counts().items()}
    S3['vadose_counts'] = {k: int(v) for k, v in Wd['Unsaturated_Zone'].value_counts().items()}
    S3['vadose_depth_median'] = {k: float(v) for k, v in Wd.groupby('Unsaturated_Zone')['depth'].median().items()}
    S3['soil_depth_median'] = {k: float(v) for k, v in Wd.groupby('Land_Use_Soil')['depth'].median().items()}
    S3['soil_group_wells'] = {gname: dict(n=int((Wd['group'] == gname).sum()),
                                          cover_median=float(Wd.loc[Wd['group'] == gname, 'depth'].median()))
                              for gname in ('G1', 'G2', 'G3')}
    S3['cover_field'] = dict(min=float(cover[valid].min()), median=float(np.median(cover[valid])), max=float(cover[valid].max()))
    res['S3'] = S3

    # ---------------------------------------------------------------- S4 head loggers for the three cover classes
    pm = draw(z, int(np.argmax(w)))                    # most probable draw of the calibration
    for k in ('R', 'eta', 'b_c', 'b_e', 'L_B', 'ground', 'w', 'Cl_s'):
        pm[k] = wquant(z[k], w)[1]
    pm['theta'] = np.array([wquant(z['theta'][:, j], w)[1] for j in range(z['theta'].shape[1])])
    K = m.K_field(pm['theta'], pm['eta'])
    A = m.matrix(K)
    o = m.run(pm)
    phi, B = o['phi'], o['B']
    d_, _ = m.geometry(pm)
    z2 = phi < 0.5 * M.DELTA * B ** 2
    dhdphi = np.where(z2, np.sqrt(M.DELTA / (2 * np.maximum(phi, 1e-9))), 1.0 / B)
    Phi_g = []
    for (lo, hi) in BANDS:
        msk = valid & (cy >= lo) & (cy < hi)
        Phi_g.append(spla.spsolve(A, np.where(msk, pm['R'] * m.area, 0.0)))
    Phi_g = np.array(Phi_g)                            # contribution of each class to phi (sums to phi)
    res['S4_check_sum'] = float(np.max(np.abs(Phi_g.sum(0)[valid] - phi[valid]) / np.abs(phi[valid])))
    # candidate logger wells: the K-wells inside the polygon and inside the model sector
    Wk = W[W['K_m_per_day'].notna()].copy()
    cells = []
    for _, r_ in Wk.iterrows():
        jj = int(np.argmin(np.hypot(m.cx - r_['x_km'], m.cy - r_['y_km'])))
        ok = valid[jj] and np.hypot(m.cx[jj] - r_['x_km'], m.cy[jj] - r_['y_km']) < 0.25 and r_['Inside_Aquifer'] == 'YES'
        cells.append(jj if ok else -1)
    Wk['cell'] = cells
    C = Wk[Wk['cell'] >= 0].reset_index(drop=True)
    cc = C['cell'].to_numpy()
    # sensitivities of the head at each candidate (m per unit log): to log R_g of the bands (south, middle, north) and
    # to the zone multipliers theta of the K field, which trade off locally against where the recharge enters
    Jg_cells = dhdphi[:, None] * Phi_g.T                          # every cell x 3 (for new sites as well)
    Jt_cells = np.zeros((m.Nc, m.Nz))
    for zz in range(m.Nz):
        dphi = -spla.spsolve(A, m.matrix(np.where(m.zone == zz, K, 0.0)) @ phi)
        Jt_cells[:, zz] = dhdphi * dphi
        if zz == 0:                                    # finite-difference check of the theta sensitivity
            th = pm['theta'].copy(); th[0] += 1e-4
            phi_e = m.solve_phi(m.K_field(th, pm['eta']), pm['R'])
            res['S4_check_theta'] = float(np.max(np.abs((phi_e - phi)[cc] / 1e-4 - dphi[cc])) / np.max(np.abs(dphi[cc])))
    Jg, Jt = Jg_cells[cc], Jt_cells[cc]
    # parameters: u0 = log(R_middle/eta) (scale, S1), a = log(R_south/R_middle), b = log(R_north/R_middle), theta
    Jfull = np.column_stack([Jg.sum(1), Jg[:, 0], Jg[:, 2], Jt])
    P0 = np.zeros((3 + m.Nz, 3 + m.Nz))
    P0[0, 0] = 1.0 / 10.0 ** 2                         # scale: practically flat
    P0[1, 1] = P0[2, 2] = 1.0                          # log-ratios: prior sd 1 (a factor e within one sd)
    P0[3:, 3:] = np.linalg.inv(m.Gam)                  # facies prior of the zone multipliers (calibration)

    def post_ab(sel, sig, with_theta=True):
        Jm = Jfull[sel] if with_theta else Jfull[sel][:, :3]
        Pm = P0 if with_theta else P0[:3, :3]
        S = np.linalg.inv(Jm.T @ Jm / sig ** 2 + Pm)
        return S[1:3, 1:3]

    def cosines(sel):
        X = Jg[sel]
        X = X / np.linalg.norm(X, axis=0)
        G = X.T @ X
        return [float(G[0, 1]), float(G[0, 2]), float(G[1, 2])]

    n = len(C)
    out = dict(n_candidates=int(n), candidates=C['Well_ID'].tolist(), sig=list(SIGS))
    allsel = np.arange(n)
    out['all'] = dict(cos=cosines(allsel),
                      sd_ab={f'{s:g}': [float(v) for v in np.sqrt(np.diag(post_ab(allsel, s)))] for s in SIGS},
                      sd_ab_theta_known={f'{s:g}': [float(v) for v in np.sqrt(np.diag(post_ab(allsel, s, False)))] for s in SIGS})
    for kset in (3, 5):
        best = None
        for sel in itertools.combinations(range(n), kset):
            sel = np.array(sel)
            ld = float(np.linalg.slogdet(post_ab(sel, SIGS[-1]))[1])
            if best is None or ld < best[0]:
                best = (ld, sel)
        ld, sel = best
        out[f'best{kset}'] = dict(wells=C['Well_ID'].iloc[sel].tolist(), logdet=ld, cos=cosines(sel),
                                  sd_ab={f'{s:g}': [float(v) for v in np.sqrt(np.diag(post_ab(sel, s)))] for s in SIGS},
                                  cover=C['depth'].iloc[sel].tolist(),
                                  x=C['x_km'].iloc[sel].round(2).tolist(), y=C['y_km'].iloc[sel].round(2).tolist())
    # best new piezometer in the north band (no K-well there): added to the best three wells
    Jfull_cells = np.column_stack([Jg_cells.sum(1), Jg_cells[:, 0], Jg_cells[:, 2], Jt_cells])
    b3 = [int(np.flatnonzero(C['Well_ID'].to_numpy() == wid)[0]) for wid in out['best3']['wells']]
    base = Jfull[b3]
    from pyproj import Transformer
    tr = Transformer.from_crs('EPSG:28404', 'EPSG:4326', always_xy=True)
    sig = SIGS[-1]

    def best_site(cands):
        best = None
        for k in cands:
            Jm = np.vstack([base, Jfull_cells[k]])
            S = np.linalg.inv(Jm.T @ Jm / sig ** 2 + P0)
            ld = float(np.linalg.slogdet(S[1:3, 1:3])[1])
            if best is None or ld < best[0]:
                best = (ld, k)
        k = best[1]
        sds = {}
        for s in SIGS:
            Jm = np.vstack([base, Jfull_cells[k]])
            S = np.linalg.inv(Jm.T @ Jm / s ** 2 + P0)
            sds[f'{s:g}'] = [float(v) for v in np.sqrt(np.diag(S[1:3, 1:3]))]
        xg, yg = m.base.x0 + 1000 * m.cx[k], m.base.y0 + 1000 * m.cy[k]
        lon, lat = tr.transform(xg, yg)
        return dict(x_km=float(m.cx[k]), y_km=float(m.cy[k]), x_gk=float(xg), y_gk=float(yg), lat=float(lat),
                    lon=float(lon), dist_shore_km=float(dist[k]), cover_m=float(cover[k]), sd_ab=sds, n_cells=int(len(cands)))
    north = np.flatnonzero(valid & (cy >= BANDS[2][0]))
    # the north band is the main plain (x <= 9 km) and a strip about 1 km wide near x = 15 km, where K and the cover are
    # extrapolated far from any well: the plain site is the robust choice, the unrestricted optimum is reported as well
    out['new_north'] = best_site(north)
    out['new_north_plain'] = best_site(north[m.cx[north] <= 9.0])
    out['band_share_of_phi_band'] = [float(Phi_g[g][band].mean() / phi[band].mean()) for g in range(3)]
    out['band_area_frac'] = [float((valid & (cy >= lo) & (cy < hi)).sum() / nv) for lo, hi in BANDS]
    # collinearity of other splits at all candidates (static heads cannot separate them)
    def split_cos(classes):
        P = [spla.spsolve(A, np.where(valid & s, pm['R'] * m.area, 0.0)) for s in classes]
        X = np.array([dhdphi[cc] * q[cc] for q in P]).T
        X = X / np.linalg.norm(X, axis=0)
        G = X.T @ X
        return [float(G[i, j]) for i in range(len(classes)) for j in range(i + 1, len(classes))]
    out['cos_cover_lt30_ge30'] = split_cos([cover < 30, cover >= 30])
    out['cos_dist'] = split_cos([dist < 5, (dist >= 5) & (dist < 10), dist >= 10])
    out['cos_east_west'] = split_cos([m.cx < 6, m.cx >= 6])
    res['S4'] = out
    res['median_params'] = {k: (float(v) if k != 'theta' else [float(t) for t in v]) for k, v in pm.items()}

    # ---------------------------------------------------------------- arrays for the figures
    res['grid'] = dict(cx=m.cx[valid].round(3).tolist(), cy=m.cy[valid].round(3).tolist(),
                       dens=md[valid].round(4).tolist(), cover=cover[valid].round(2).tolist(),
                       band=band[valid].astype(int).tolist(), sea=m.seac[valid].astype(int).tolist(), dx=m.dx)
    res['grid_all'] = dict(cx=m.cx.round(3).tolist(), cy=m.cy.round(3).tolist(), cover=cover.round(2).tolist())
    res['wells'] = Wd[['Well_ID', 'x_km', 'y_km', 'depth', 'NO3_mg_per_L', 'K_m_per_day', 'Land_Use_Soil',
                       'Unsaturated_Zone', 'Inside_Aquifer']].to_dict(orient='list')
    with open(os.path.join(HERE, 'res', 'shiu_fk.json'), 'w') as fh:
        json.dump(res, fh, default=lambda v: None if (isinstance(v, float) and np.isnan(v)) else v)
    # log
    print('S1 invariance max rel', f"{S1['invariance_max_rel']:.1e}", '| R mm/yr post', np.round(S1['R_mmyr_post'], 0),
          'prior', np.round(S1['R_mmyr_prior'], 0))
    for k in ('logR', 'logeta', 'logReta'):
        print(f"   {k:8s} w90 prior {S1[k]['prior_w90']:.3f} post {S1[k]['post_w90']:.3f}")
    print('   corr prior/post', round(S1['corr_prior'], 3), round(S1['corr_post'], 3), '| var share from K scale',
          round(S1['share_var_from_K_scale'], 3))
    print('S2 check', res['S2_check_rel'], '| band cells', S2['n_band'], 'valid', nv)
    for nm, v in S2['regions'].items():
        print(f"   {nm:14s} area {v['area_frac']:.3f} share {np.round(v['share'], 3)}")
    print('   soil groups', {k: (round(v['area_frac'], 3), np.round(v['share'], 3).tolist()) for k, v in S2['soil_groups'].items()},
          '| thin cover area', round(S2['thin_cover_area_frac'], 4))
    print('   density quantiles', np.round(S2['dens_quantiles'], 2), 'band', round(S2['dens_band'], 2), 'far',
          round(S2['dens_far_median'], 2))
    print('S3', json.dumps({k: S3[k] for k in ('spearman_all', 'sector', 'south', 'no3_by_cover', 'thin_vs_rest')}))
    print('   vadose depth medians', S3['vadose_depth_median'])
    print('S4 checks', res['S4_check_sum'], res['S4_check_theta'], '| candidates', n, '| all cos', np.round(out['all']['cos'], 3))
    print('   all wells sd(a, b):', out['all']['sd_ab'], '| theta known:', out['all']['sd_ab_theta_known'])
    for kset in (3, 5):
        b = out[f'best{kset}']
        print(f"   best{kset}: {b['wells']} cos {np.round(b['cos'], 3)} sd_ab {b['sd_ab']} cover {b['cover']} y {b['y']}")
    for key in ('new_north', 'new_north_plain'):
        nn = out[key]
        print(f"   {key}: x {nn['x_km']:.2f} y {nn['y_km']:.2f} km (lat {nn['lat']:.4f}, lon {nn['lon']:.4f}), shore "
              f"{nn['dist_shore_km']:.1f} km, cover {nn['cover_m']:.0f} m, sd_ab {nn['sd_ab']}")
    print('   band share of band phi', np.round(out['band_share_of_phi_band'], 3), 'area', np.round(out['band_area_frac'], 3))
    print('   cos cover', np.round(out['cos_cover_lt30_ge30'], 3), 'dist', np.round(out['cos_dist'], 3), 'east/west',
          np.round(out['cos_east_west'], 3))


if __name__ == '__main__':
    main()
