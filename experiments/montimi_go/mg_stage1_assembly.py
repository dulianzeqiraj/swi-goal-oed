"""MONTIMI-GO stage 1: let the placement goal decide the assembly.

For four reference cases (median parameters; four layouts at their critical rates on the full assembly):
  (a) goal weights of every term from one forward and one adjoint run of the full assembly, checked against actual
      runs (full removal for the terms the rule cuts, a 10 % reduction for the terms it keeps);
  (b) the rule: cut a term if its weight is below tau * eps_lim in every reference case;
  (c) the mesh: dual-weighted-residual indicator of a uniform 40-column assembly, a goal-graded 40-column mesh,
      and the effectivity of the estimate on the reference cases and on 8 further cases;
  (d) closure sensitivities: dJ per unit missing source in eight bands along the section.
Output res/stage1.json, res/grid_G.json, res/stage1_maps.npz."""
import os, sys, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mg_model as M
import mg_setup as S

RES = os.path.join(HERE, 'res')
TAU = 0.02
TERMS = [
    ('memory_h_silt', 'hydraulic memory, silt lenses', lambda s: {'memory_h': (s, 1.0)}, dict(memory_h=(False, True)), dict(s_h=(0.9 * 2e-5, 5e-5))),
    ('memory_h_clay', 'hydraulic memory, clay lenses', lambda s: {'memory_h': (1.0, s)}, dict(memory_h=(True, False)), dict(s_h=(2e-5, 0.9 * 5e-5))),
    ('immobile_silt', 'immobile zone, silt', lambda s: {'immobile': (s, 1.0)}, dict(immobile=(False, True)), None),
    ('immobile_clay', 'immobile zone, clay', lambda s: {'immobile': (1.0, s)}, dict(immobile=(True, False)), None),
    ('transverse', 'transverse dispersion', lambda s: {'transverse': s}, dict(transverse=False), None),
    ('slr', 'sea-level rise', lambda s: {'slr': s}, dict(slr=False), dict(eta_rate=0.9 * 4.0)),
    ('buoyancy', 'buoyancy (density coupling)', lambda s: {'buoyancy': s}, dict(buoyancy=False), None),
    ('same_step', 'same-step flow-salt coupling', lambda s: {'split': 1.0 - s}, dict(coupling='split'), None),
]
REF = [dict(xs=S.XS[0], xr=S.XR[5]), dict(xs=S.XS[1], xr=None), dict(xs=S.XS[2], xr=S.XR[3]), dict(xs=S.XS[3], xr=S.XR[2])]


def full_run(g, P, opts, L, Q, adjoint=True):
    m = M.Model(g, P=P, opts=opts, dt_yr=S.DT_YR)
    y0 = m.steady()
    J = m.run(y0=y0, schedule=[(S.NH, S.HIST), (S.NF, S.forecast_layout(L, Q))])
    if adjoint:
        m.adjoint()
    return J, m


def tenpct(P, key, m, L, Q, J):
    """actual change of J when the term is reduced by 10 % (kept terms), compared with -0.1 * weight."""
    if key in ('immobile_silt', 'immobile_clay'):
        bc = list(P['b_c']); bc[0 if key == 'immobile_silt' else 1] *= 0.9
        Pm = dict(P, b_c=tuple(bc))
    elif key == 'transverse':
        Pm = dict(P, aT=0.9 * P['aT'])
    elif key == 'buoyancy':
        Pm = dict(P, delta=0.9 * M.BASE['delta'])
    elif key == 'slr':
        Pm = dict(P, eta_rate=0.9 * P['eta_rate'])
    else:
        return None
    Ja, _ = full_run(S.GF, Pm, {}, L, Q, adjoint=False)
    return Ja - J


def main():
    os.makedirs(RES, exist_ok=True)
    P = dict(S.MED)
    out = dict(tau=TAU, eps_lim=M.EPS_LIM, cases=[])
    ind_cols = np.zeros(S.GF.NX)
    Ph = M.prolong(S.GU, S.GF)
    for L in REF:
        t = time.time()
        # critical rate of this layout on the full assembly (forecast from the full present state)
        y0, yp, zp, _ = S.present_state(S.GF, P, {})
        Qc, nev = S.q_crit(lambda Q: S.forecast(S.GF, P, {}, yp, zp, L, Q)[0], guess=5.0)
        J, m = full_run(S.GF, P, {}, L, Qc)
        case = dict(layout=S.lay_name(L), Q=Qc, J=J, cpu_forward=m.cpu, terms=[])
        for key, label, hd, alt, pm in TERMS:
            w = m.weight(hd)
            row = dict(key=key, label=label, weight=w)
            if abs(w) < TAU * M.EPS_LIM or key == 'same_step':
                mm = M.Model(S.GF, P=P, opts=alt, dt_yr=S.DT_YR)
                ys = mm.steady()
                Ja = mm.run(y0=ys, schedule=[(S.NH, S.HIST), (S.NF, S.forecast_layout(L, Qc))], keep=False)
                row.update(removal_pred=-w, removal_actual=Ja - J)
            else:
                d = tenpct(P, key, m, L, Qc, J)
                if d is not None:
                    row.update(ten_pred=-0.1 * w, ten_actual=d)
            case['terms'].append(row)
            print(case['layout'], key, row, flush=True)
        # closure sensitivity: a missing source of 1 mm/yr spread over a band of the section
        bands = np.linspace(0, M.BASE['L'], 9)
        sens = []
        for a, b in zip(bands[:-1], bands[1:]):
            mask = ((S.GF.xc[S.GF.J] >= a) & (S.GF.xc[S.GF.J] < b)).astype(float)
            src = 1e-3 / M.YR * S.GF.V * mask
            sens.append(float(sum(m.lam[n][:S.GF.N] @ src for n in range(1, m.nst + 1))))
        case['closure_sens_per_mm_yr'] = sens
        # adjoint ranking of recharge sites (marginal, per m2/d injected over the full thickness, forecast only)
        out_adj = m.adjoint()
        case['dJ_dqr_col'] = out_adj['dJ_dqr_col'].tolist()
        case['dJ_dQ'] = out_adj['dJ_dQ']
        # dual-weighted residual of the uniform coarse assembly (same physics)
        mH = M.Model(S.GU, P=P, dt_yr=S.DT_YR)
        yH = mH.steady()
        JH = mH.run(y0=yH, schedule=[(S.NH, S.HIST), (S.NF, S.forecast_layout(L, Qc))])
        est, col, colabs = m.dwr(mH, Ph)
        case.update(dwr_U=dict(J_H=JH, true=JH - J, est=est))
        ind_cols += colabs / max(colabs.sum(), 1e-300)
        case['indicator_col'] = colabs.tolist()
        case['time'] = time.time() - t
        out['cases'].append(case)
        print(case['layout'], 'Q', Qc, 'J', J, 'U err', JH - J, 'est', est, '%.0fs' % case['time'], flush=True)
    # the rule
    cut = [k for k, *_ in TERMS if all(abs(next(r['weight'] for r in c['terms'] if r['key'] == k)) < TAU * M.EPS_LIM for c in out['cases'])]
    out['cut'] = cut
    # the goal-graded mesh with the same number of columns as the uniform coarse mesh
    gG = M.graded_grid(ind_cols, S.GF, S.GU.NX, floor=0.02, maxw=300.0)
    json.dump(dict(xf=gG.xf.tolist(), zf=gG.zf.tolist()), open(os.path.join(RES, 'grid_G.json'), 'w'))
    out['grid_G_ncol'] = gG.NX
    out['grid_G_dx_min_max'] = [float(gG.dx.min()), float(gG.dx.max())]
    # effectivity of the DWR estimate for U and G on the reference cases and on 8 further cases
    PhG = M.prolong(gG, S.GF)
    rng = np.random.default_rng(7)
    extra = [(S.LAYOUTS[i], S.DES[j]) for i, j in zip(rng.choice(len(S.LAYOUTS), 8, replace=False), rng.choice(len(S.DES), 8, replace=False))]
    eff = []
    for i, (L, Pd) in enumerate([(L, P) for L in REF] + extra):
        Pd = dict(Pd)
        y0, yp, zp, _ = S.present_state(S.GF, Pd, {})
        Qc, _ = S.q_crit(lambda Q: S.forecast(S.GF, Pd, {}, yp, zp, L, Q)[0], guess=5.0)
        if Qc <= 0.0:
            Qc = 1.0
        J, m = full_run(S.GF, Pd, {}, L, Qc)
        row = dict(layout=S.lay_name(L), Q=Qc, J=J)
        for name, gH, Pr in (('U', S.GU, Ph), ('G', gG, PhG)):
            mH = M.Model(gH, P=Pd, dt_yr=S.DT_YR)
            yH = mH.steady()
            JH = mH.run(y0=yH, schedule=[(S.NH, S.HIST), (S.NF, S.forecast_layout(L, Qc))])
            est, _, _ = m.dwr(mH, Pr)
            row[name] = dict(J=JH, true=JH - J, est=est)
        eff.append(row)
        print('dwr', i, row, flush=True)
    out['dwr_cases'] = eff
    json.dump(out, open(os.path.join(RES, 'stage1.json'), 'w'), indent=1)
    np.savez(os.path.join(RES, 'stage1_maps.npz'), ind_cols=ind_cols, xc=S.GF.xc, xfG=gG.xf,
             lam_example=np.array(m.lam[-1]))
    print('cut:', cut, 'graded grid dx', gG.dx.round(0))


if __name__ == '__main__':
    main()
