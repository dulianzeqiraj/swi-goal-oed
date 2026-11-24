"""MONTIMI-GO stage 0: checks of the assembled solver quoted in section 3 of the note.
  (a) Newton on one coupled step converges quadratically (exact Jacobian); Picard between flow and salt stagnates;
  (b) the one-pass split against the coupled step for time steps of 1, 0.5, 0.25 and 0.125 years;
  (c) adjoint gradients against central differences (pumping rate, recharge rate).
Output res/checks.json"""
import os, sys, json, time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mg_model as M
import mg_setup as S

RES = os.path.join(HERE, 'res')


def main():
    out = {}
    g = S.GF
    P = dict(S.MED)
    L = dict(xs=S.XS[0], xr=None); Q = 5.0
    y0, yp, zp, _ = S.present_state(g, P, {})
    N = g.N
    m = M.Model(g, P=P, layout=S.forecast_layout(L, Q), dt_yr=S.DT_YR)
    m.Wn = [None, (m.W_out, m.W_in)]
    t = S.T0 + m.dt
    # (a) Newton from the split pass
    yo, zo = yp, zp
    res_newton = []
    y = yo.copy()
    for k in range(6):
        R = m.residual(y, yo, zo, t, 1)
        res_newton.append(float(np.abs(R).max()))
        if res_newton[-1] < 1e-13:
            break
        y = y + spla.spsolve(m.jac(y, yo, t, 1).tocsc(), -R)
    # Picard
    Ah = spla.splu(m.Ah)
    mem_h = m.mh_coef[0] * zo[:N] + m.mh_coef[1] * zo[N:2 * N]
    mem_c = m.mc_coef[0] * zo[2 * N:3 * N] + m.mc_coef[1] * zo[3 * N:]
    Dcoef, _ = m.disp(m.Gh @ yo[:N] + m.Gc @ yo[N:] + m.g0(t - m.dt))
    h, c = yo[:N].copy(), yo[N:].copy()
    dcs = []
    for it in range(30):
        h = Ah.solve(m.st_h * yo[:N] + mem_h - g.Div @ (m.Gc @ c + m.g0(t)) - m.W_out + m.W_in)
        Qf = m.Gh @ h + m.Gc @ c + m.g0(t)
        Ac, ghost = m.transport_matrix(Qf, Dcoef, m.W_in)
        cn = spla.spsolve(Ac.tocsc(), m.st_c * yo[N:] + mem_c - g.Div @ (Qf * ghost))
        dcs.append(float(np.abs(cn - c).max())); c = cn
    out['newton_residuals'] = res_newton
    out['picard_dc'] = dcs
    # (b) split against coupled for four time steps
    rows = []
    for dt in (1.0, 0.5, 0.25, 0.125):
        r = dict(dt=dt)
        for cpl in ('full', 'split'):
            mm = M.Model(g, P=P, opts=dict(coupling=cpl), dt_yr=dt)
            tt = time.time()
            J = mm.run(y0=yp, z0=zp, schedule=[(int(round(S.FORE_YR / dt)), S.forecast_layout(L, Q))], t0=S.T0, keep=False, toe=False)
            r[cpl] = J; r[cpl + '_cpu'] = time.time() - tt
        rows.append(r)
        print(r, flush=True)
    out['split'] = rows
    # (c) gradient checks on the complete assembly (history + forecast, from the pre-development state)
    Lr = dict(xs=S.XS[0], xr=S.XR[5])
    mm = M.Model(g, P=P, dt_yr=S.DT_YR)
    ys = mm.steady()
    sched = lambda Qx, qr: [(S.NH, S.HIST), (S.NF, dict(S.forecast_layout(Lr, Qx), qr=qr))]
    J0 = mm.run(y0=ys, schedule=sched(Q, 1.0))
    adj = mm.adjoint()
    h = 1e-4
    Jq = [M.Model(g, P=P, dt_yr=S.DT_YR).run(y0=ys, schedule=sched(Q + s * h, 1.0), keep=False, toe=False) for s in (1, -1)]
    Jr = [M.Model(g, P=P, dt_yr=S.DT_YR).run(y0=ys, schedule=sched(Q, 1.0 + s * h), keep=False, toe=False) for s in (1, -1)]
    out['grad'] = dict(J=J0, dJdQ_adj=adj['dJ_dQ'], dJdQ_fd=(Jq[0] - Jq[1]) / (2 * h),
                       dJdqr_adj=float(adj['dJ_dqr_col'][g.column(Lr['xr'])]), dJdqr_fd=(Jr[0] - Jr[1]) / (2 * h))
    print(out['grad'])
    json.dump(out, open(os.path.join(RES, 'checks.json'), 'w'), indent=1)




def grad_check_2():
    """second gradient check at a layout whose net seaward flux past the supply well is not near zero."""
    g = S.GF
    P = dict(S.MED)
    Lr = dict(xs=S.XS[0], xr=S.XR[2])
    Q = 5.0
    mm = M.Model(g, P=P, dt_yr=S.DT_YR)
    ys = mm.steady()
    sched = lambda Qx, qr: [(S.NH, S.HIST), (S.NF, dict(S.forecast_layout(Lr, Qx), qr=qr))]
    J0 = mm.run(y0=ys, schedule=sched(Q, 1.0))
    adj = mm.adjoint()
    out = dict(J=J0, layout=S.lay_name(Lr), Q=Q, dJdQ_adj=adj['dJ_dQ'], dJdqr_adj=float(adj['dJ_dqr_col'][g.column(Lr['xr'])]))
    for h in (1e-3, 1e-4, 1e-5):
        Jq = [M.Model(g, P=P, dt_yr=S.DT_YR).run(y0=ys, schedule=sched(Q + s * h, 1.0), keep=False, toe=False) for s in (1, -1)]
        Jr = [M.Model(g, P=P, dt_yr=S.DT_YR).run(y0=ys, schedule=sched(Q, 1.0 + s * h), keep=False, toe=False) for s in (1, -1)]
        out[f'fd_{h:g}'] = dict(dJdQ=(Jq[0] - Jq[1]) / (2 * h), dJdqr=(Jr[0] - Jr[1]) / (2 * h))
    print(out)
    d = json.load(open(os.path.join(RES, 'checks.json')))
    d['grad2'] = out
    json.dump(d, open(os.path.join(RES, 'checks.json'), 'w'), indent=1)


if __name__ == '__main__':
    if sys.argv[1:] == ['grad2']:
        grad_check_2()
    else:
        main()
        grad_check_2()
