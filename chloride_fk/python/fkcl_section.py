"""Variable-density chloride section A-A' across the Fushe-Kuqe sector (y = 36.5 km), from calibrated members.

For a posterior member, the section takes the areal model's geometry (aquifer top from the DRASTIC depth,
thickness from the shoreline distance), its horizontal conductivity and its freshwater discharge to the sea
on the same rows, and solves the steady variable-density problem (fkcl_vd.Section). It is compared with the
Strack sharp interface of the same member (toe position) and the transition-zone half-width w of the
calibration is compared with the simulated mixing zone.

Members: posterior 5th, 50th and 95th percentiles of the deep-wedge area. Dispersivity sensitivity on the
median member: alpha_T in {0.1, 1, 3} m (alpha_L = 10 alpha_T, min 10 m).
Usage: python3 fkcl_section.py      -> ../results/section_*.npz, section_summary.json
"""
import os
import sys
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fkcl_model as M  # noqa: E402
import fkcl_vd as V  # noqa: E402

RES = os.path.join(HERE, '..', 'results')
Y_SEC = 36.5
DXS, DZS = 50.0, 4.0


def member_params(E, i):
    keys = ['theta', 'R', 'eta', 'b_c', 'b_e', 'L_B', 'ground', 'w', 'Cl_s']
    return {k: E['p_' + k][i] for k in keys}


def build(m, p, aT=1.0, aL=10.0):
    j = int(round(Y_SEC / m.dx))
    o = m.run(p)
    # freshwater discharge to the sea per metre of coast, rows within +-1 km of the section
    K = m.K_field(p['theta'], p['eta'])
    rows = np.flatnonzero(m.seac & (np.abs(m.cy - Y_SEC) <= 1.0))
    sel = np.isin(m.sea_idx, rows)
    q_sea = K[m.sea_idx[sel]] * m.sea_cond[sel] * o['phi'][m.sea_idx[sel]]        # m3/d per cell face
    Qin = q_sea.sum() / (len(rows) * m.dxm)                                          # m2/d
    shore = m.shore_row[j]
    cells = np.flatnonzero(m.valid & (m.aj == j))
    cells = cells[np.argsort(m.cx[cells])]
    xe_km = m.cx[cells[-1]] + 0.5 * m.dx
    L = (xe_km - shore) * 1000.0
    nx = int(round(L / DXS))
    xe = np.linspace(0.0, L, nx + 1)
    xc_km = shore + 0.5 * (xe[1:] + xe[:-1]) / 1000.0
    # nearest areal cell for each column (the coastal gap takes the western-edge cell)
    near = cells[np.clip(np.searchsorted(m.cx[cells] - 0.5 * m.dx, xc_km) - 1, 0, len(cells) - 1)]
    d, B = m.geometry(p)
    top, bot = d[near], d[near] + B[near]
    zmax = np.ceil(bot.max() / DZS) * DZS
    ze = np.arange(0.0, zmax + 1e-9, DZS)
    s = V.Section(xe, ze, top, bot, K[near], aniso=0.1, eps=M.DELTA, phi=0.25, Dm=8.64e-5, aL=aL, aT=aT,
                  Qin=Qin, mode='field')
    # initial state: the member's sharp interface with its transition zone
    Zc = s.zc[s.jj]
    c0 = 0.5 * (1 + np.vectorize(__import__('math').erf)((Zc - o['zeta'][near][s.ii]) / (p['w'] * np.sqrt(2))))
    s.solve_implicit(c0=c0, max_steps=8000)
    # Strack toe of the same member on the same row, measured from the shoreline
    wedge = (o['zeta'] < o['d'] + o['B'])[cells]
    toe_strack = ((m.cx[cells][wedge].max() + 0.5 * m.dx - shore) * 1000.0) if wedge.any() else 0.0
    # simulated mixing-zone half-width: vertical distance between c = 0.16 and 0.84 (= 2 w for Phi), median
    C = s.field(s.c)
    widths = []
    for i in range(s.nx):
        col = C[:, i]; ok = np.isfinite(col)
        if ok.sum() < 5:
            continue
        z = s.zc[ok]; cc = col[ok]
        if cc.min() < 0.16 and cc.max() > 0.84 and np.all(np.diff(cc) >= -1e-6):
            z16 = np.interp(0.16, cc, z); z84 = np.interp(0.84, cc, z)
            widths.append(0.5 * (z84 - z16))
    return dict(sec=s, Qin=Qin, L=L, toe_vd=float(s.toe(0.5)), toe_strack=float(toe_strack),
                w_sim=float(np.median(widths)) if widths else float('nan'), n_w=len(widths),
                xc_km=xc_km, top=top, bot=bot, zeta=o['zeta'][near], cells=near, Cl_s=p['Cl_s'], w=p['w'])


def _job(args):
    tag, i, aT, dxs, dzs = args
    global DXS, DZS
    DXS, DZS = dxs, dzs
    m = M.Model()
    E = np.load(os.path.join(RES, 'post_ensemble.npz'))
    p = member_params(E, i)
    r = build(m, p, aT=aT, aL=max(10.0, 10 * aT))
    s = r['sec']
    if tag in ('p05', 'p50', 'p95', 'p50_fine'):
        np.savez_compressed(os.path.join(RES, f'section_{tag}.npz'), c=s.field(s.c), h=s.field(s.h), xe=s.xe, ze=s.ze,
                            top=r['top'], bot=r['bot'], zeta=r['zeta'], xc_km=r['xc_km'], Cl_s=r['Cl_s'], w=r['w'])
    return tag, dict(index=int(i), aT=aT, dx_m=dxs, dz_m=dzs, Qin_m2d=r['Qin'], L_m=r['L'], toe_vd_m=r['toe_vd'],
                     toe_strack_m=r['toe_strack'], w_calibrated_m=float(r['w']), w_simulated_m=r['w_sim'],
                     n_w_columns=r['n_w'], steps=int(s.iters), steady_gap=float(s.steady_gap), t_end_d=float(s.t_end),
                     R=float(p['R']), eta=float(p['eta']), b_c=float(p['b_c']))


def main():
    from multiprocessing import Pool
    m = M.Model()
    E = np.load(os.path.join(RES, 'post_ensemble.npz'))
    wa = (E['wedge'] & m.valid).sum(1)
    order = np.argsort(wa)
    picks = {'p05': order[int(0.05 * len(wa))], 'p50': order[int(0.5 * len(wa))], 'p95': order[int(0.95 * len(wa))]}
    jobs = [('p50_fine', picks['p50'], 1.0, 50.0, 4.0)]
    jobs += [(t, i, 1.0, 100.0, 5.0) for t, i in picks.items()]
    jobs += [(f'p50_aT{aT}', picks['p50'], aT, 100.0, 5.0) for aT in (0.1, 3.0)]
    with Pool(4) as pool:
        res = dict(pool.map(_job, jobs))
    for t in picks:
        res[t]['wedge_area_km2'] = float(wa[picks[t]] * m.area / 1e6)
    summ = dict(y_km=Y_SEC, runs=res)
    json.dump(summ, open(os.path.join(RES, 'section_summary.json'), 'w'), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == '__main__':
    main()
