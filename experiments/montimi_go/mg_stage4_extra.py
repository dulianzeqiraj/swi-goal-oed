"""MONTIMI-GO stage 4: the blocks the goal cut, the toe, and the cost of each assembly.
  (a) ions: the full assembly with the seven-ion block and Gaines-Thomas exchange (median parameters, first
      reference layout at its critical rate): chloride from the ion block against chloride from the salt block,
      sodium and hardness at the screen and behind the recharge well, CPU share of the ion block;
  (b) toe: forecasts of the full assembly on the evaluation draws for three layouts at their safe rates; the toe
      relaxation law dX/dt = (a - gamma h_m - X)/tau fitted to each run; the toe as a proxy of the screen event;
  (c) cost of one 30-year forecast for every assembly.
Output res/stage4.json"""
import os, sys, json, time
import numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mg_model as M
import mg_setup as S
import ions as IO
from mg_stage3_place import grid_of

RES = os.path.join(HERE, 'res')
X_M = 500.0


def ions_run():
    st1 = json.load(open(os.path.join(RES, 'stage1.json')))
    c0 = st1['cases'][0]
    L = dict(xs=S.XS[0], xr=S.XR[5]); Q = c0['Q']
    P = dict(S.MED)
    m = M.Model(S.GF, P=P, dt_yr=S.DT_YR)
    y0 = m.steady()
    t = time.time()
    J = m.run(y0=y0, schedule=[(S.NH, S.HIST), (S.NF, S.forecast_layout(L, Q))], keep=False, ions=True)
    tot = time.time() - t
    ion = np.array(m.ion_t)                                      # mg/L at the screen, per step
    cl_salt = M.CL_F + (M.CL_S - M.CL_F) * np.array(m.Jt)
    m2 = M.Model(S.GF, P=P, dt_yr=S.DT_YR)
    t = time.time(); J2 = m2.run(y0=y0, schedule=[(S.NH, S.HIST), (S.NF, S.forecast_layout(L, Q))], keep=False)
    tot2 = time.time() - t
    hard = 2 * ion[:, IO.G.I_CA] / IO.MW[IO.G.I_CA] + 2 * ion[:, IO.G.I_MG] / IO.MW[IO.G.I_MG]
    # behind the recharge well: mid-depth cell 100 m landward of it, end of the forecast
    g = S.GF
    j = g.column(L['xr'] + 100.0); i = g.NZ // 2
    behind = m.ion.c[i * g.NX + j] * IO.MW
    k = np.flatnonzero(cl_salt > M.CL_LIM)
    out = dict(layout=S.lay_name(L), Q=Q, J_with_ions=J, J_without=J2, max_abs_cl_diff_mgL=float(np.abs(ion[:, IO.G.I_CL] - cl_salt).max()),
               cpu_with=tot, cpu_without=tot2, cpu_ion_block=m.ion_cpu,
               na_end=float(ion[-1, IO.G.I_NA]), cl_end=float(ion[-1, IO.G.I_CL]), na_max=float(ion[:, IO.G.I_NA].max()),
               na_when_cl_250=(float(ion[k[0], IO.G.I_NA]) if len(k) else None), hard_end_meq=float(hard[-1]),
               hard_fresh_meq=float(2 * IO.FRESH[IO.G.I_CA] + 2 * IO.FRESH[IO.G.I_MG]),
               behind_recharge_mgL=dict(zip(IO.SPECIES, behind.round(2).tolist())),
               series_cl=ion[:, IO.G.I_CL][::4].tolist(), series_na=ion[:, IO.G.I_NA][::4].tolist(), series_hard=hard[::4].tolist())
    return out


def toe_task(args):
    li, d, Q = args
    L = S.LAYOUTS[li]
    P = dict(S.EVA[d])
    y0, yp, zp, toeh = S.present_state(S.GF, P, {})
    m = M.Model(S.GF, P=P, dt_yr=S.DT_YR)
    J = m.run(y0=yp, z0=zp, schedule=[(S.NF, S.forecast_layout(L, Q))], t0=S.T0, keep=True, toe=True)
    g = S.GF
    j = g.column(X_M); i = g.NZ // 2
    hm = np.array([Y[i * g.NX + j] for Y in m.Y])
    X = m.toe_x
    dt = S.DT_YR
    A = np.c_[np.ones(len(X) - 1), hm[:-1], X[:-1]]
    b = np.diff(X) / dt
    coef, *_ = np.linalg.lstsq(A, b, rcond=None)
    pred = A @ coef
    r2 = 1 - np.sum((b - pred) ** 2) / max(np.sum((b - b.mean()) ** 2), 1e-12)
    tau = -1.0 / coef[2] if coef[2] < 0 else np.inf
    Xs = [X[0]]
    for n in range(len(X) - 1):
        Xs.append(Xs[-1] + dt * (coef[0] + coef[1] * hm[n] + coef[2] * Xs[-1]))
    return dict(layout=S.lay_name(L), draw=d, Q=Q, J=J, toe0=float(X[0]), toeH=float(X[-1]), tau_yr=float(tau),
                gamma=float(coef[1] * tau) if np.isfinite(tau) else None, r2=float(r2),
                toe_law_err_m=float(np.abs(np.array(Xs) - X).max()), hm_end=float(hm[-1]))


def cost_task(name):
    cfg = S.ASSEMBLIES[name]
    g = grid_of(cfg['grid'])
    P = dict(S.MED)
    y0, yp, zp, _ = S.present_state(g, P, cfg['opts'])
    L = S.LAYOUTS[0]
    ts = []
    for k in range(3):
        t = time.time(); S.forecast(g, P, cfg['opts'], yp, zp, L, 5.0); ts.append(time.time() - t)
    return name, float(np.median(ts)), g.N


def main():
    out = {}
    out['ions'] = ions_run()
    print('ions', {k: v for k, v in out['ions'].items() if not k.startswith('series')}, flush=True)
    qF = np.load(os.path.join(RES, 'qcrit_F_EVA.npz'))['Q']
    rows = [d for d in range(min(qF.shape[0], len(S.EVA))) if np.all(np.isfinite(qF[d]))]
    qF = qF[rows]
    m = int(np.floor(S.ALPHA * qF.shape[0])) + 1
    names = [S.lay_name(L) for L in S.LAYOUTS]
    pick = [names.index(n) for n in ('S2.0-R2.5', 'S2.5', 'S3.0-R1.5')]
    tasks = []
    for li in pick:
        qs = np.sort(qF[:, li][np.isfinite(qF[:, li])])
        Qstar = float(qs[m - 1])
        tasks += [(li, d, Qstar) for d in rows]
    with Pool(4) as pool:
        out['toe'] = pool.map(toe_task, tasks)
        out['cost'] = pool.map(cost_task, list(S.ASSEMBLIES))
    json.dump(out, open(os.path.join(RES, 'stage4.json'), 'w'), indent=1)
    print('cost', out['cost'])


if __name__ == '__main__':
    main()
