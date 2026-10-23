"""RITMI-GO experiments (review 43): what transient data identify in the augmented flow + multi-species system.
  S  steady-state blindness: Fisher information of steady data (seven ions at four wells, constant forcing run to
     equilibrium) against the transient history; the reactive exception (sulfate reduction inside the clay makes
     one combination of the clay memory visible at steady state).
  H  what the natural transient identifies: history (34 data) and history + five years of status-quo monitoring
     (monthly Cl, semi-annual major ions at wells 503, 341, 340).
  D  forcing designs during 2026-2031 (zero-mean oscillations, pauses, surges of the coastal pumping): salinity cost,
     information and goal uncertainty, linearised at the prior-mean truth.
  G  sampling design in time: greedy goal-oriented choice of 12 sampling units (a Cl sample or a major-ion campaign at
     one well) against a routine schedule with 12 units.
  V  nonlinear check: ES-MDA (100 members, 4 iterations) on R synthetic truths for history only, history + full
     monitoring, + greedy 12, + routine 12.
  T  flow memory from tides (analytic): Fisher information of tidal amplitude ratios and phase lags at three wells
     for a two-rate storage kernel, with one, two or four tidal constituents.
Writes ritmi_results.json. `python3 ritmi_exp.py S H D G T V` runs the parts given (default: all).
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import json, sys, time
import numpy as np
from multiprocessing import Pool
import ritmi_model as R
import ritmi_core as C

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
OUT = 'ritmi_results.json'
H_FD = 0.05
NV, NE, NA = 24, 100, 4
STEADY = dict(v=R.V_SQ, years=3000.0, dt=1.0)


def load():
    return json.load(open(OUT)) if os.path.exists(OUT) else {}


def save(res):
    json.dump(res, open(OUT, 'w'), indent=1)


def post_sd(J):
    S, H = C.laplace(J)
    return S, np.sqrt(np.diag(S)), float(np.linalg.slogdet(H + np.eye(H.shape[0]))[1])


def part_S():
    U = C.fd_ensemble(H_FD)
    t0 = time.time()
    st = R.simulate(C.to_P(U), steady=STEADY)
    st2 = R.simulate(C.to_P(U[:1]), steady=dict(STEADY, years=2500.0))
    drift = float(np.abs(np.log(st['final'][0] / st2['final'][0])).max())
    Js = C.jac(C.obs_steady(st), H_FD)
    ref = R.simulate(C.to_P(U), {'kind': 'const'})
    Jh = C.jac(C.obs_hist(ref), H_FD)
    _, sd_s, ld_s = post_sd(Js)
    _, sd_h, ld_h = post_sd(Jh)
    # reactive exception: steady SO4/HCO3 data see the clay memory only through r = b2 a2 k / (a2 + k)
    sub = [5, 6, 11]                                          # log a2, log b2, log k_sr
    rows = [k * 7 + j for k in range(4) for j in (R.I_SO4, R.I_HCO3)]
    sv = np.linalg.svd(Js[np.ix_(rows, sub)], compute_uv=True)
    a2, k = np.exp(C.M0[5]), np.exp(C.M0[11])
    pred = np.array([k / (a2 + k), 1.0, a2 / (a2 + k)]) * C.S0[sub]       # d log r / d u
    v1 = sv[2][0] * np.sign(sv[2][0] @ pred)
    cos = float(v1 @ pred / np.linalg.norm(pred))
    # exchange and fast memory at steady state: largest sensitivity of any steady datum
    smax = np.abs(Js).max(0)
    res = dict(sd_steady=sd_s.tolist(), sd_hist=sd_h.tolist(), logdet_steady=ld_s, logdet_hist=ld_h,
               steady_drift_last500yr=drift, so4_singular_values=sv[1].tolist(), so4_v1=v1.tolist(),
               so4_pred=(pred / np.linalg.norm(pred)).tolist(), so4_cos=cos, max_abs_sens_steady=smax.tolist(),
               fisher_eig_steady=np.linalg.eigvalsh(Js.T @ Js / C.SIG_OBS ** 2)[::-1].tolist(),
               fisher_eig_hist=np.linalg.eigvalsh(Jh.T @ Jh / C.SIG_OBS ** 2)[::-1].tolist())
    print('S: steady logdet %.2f, history logdet %.2f, drift %.1e, SO4 sv %s, cos %.3f (%.0f s)' %
          (ld_s, ld_h, drift, np.round(sv[1], 3), cos, time.time() - t0), flush=True)
    print('   sd steady', np.round(sd_s, 2)); print('   sd hist  ', np.round(sd_h, 2))
    return res


DESIGNS = ([dict(kind='const')] + [dict(kind='sine', A=65.0, P=p) for p in (0.5, 1.0, 2.0, 5.0)] +
           [dict(kind='doublet', A=65.0, P=p) for p in (2.0, 5.0)] + [dict(kind='prbs', A=65.0, P=0.25)] +
           [dict(kind='block', A=-65.0, P=p) for p in (1.0, 2.0)] + [dict(kind='block', A=65.0, P=p) for p in (1.0, 2.0)])


def dlabel(d):
    k = d['kind']
    if k == 'const':
        return 'status quo'
    if k == 'block':
        return ('pause' if d['A'] < 0 else 'surge') + ' %g yr' % d['P']
    return {'sine': 'sine', 'doublet': 'doublet', 'prbs': 'PRBS'}[k] + ' %g yr' % d['P']


def part_HD():
    U = C.fd_ensemble(H_FD)
    ref = R.simulate(C.to_P(U), {'kind': 'const'})
    Jh = C.jac(C.obs_hist(ref), H_FD)
    rows = []
    for d in DESIGNS:
        o = ref if d['kind'] == 'const' else R.simulate(C.to_P(U), d)
        Je = C.jac(C.obs_exp(o), H_FD)
        Jg = C.jac(C.goals(o), H_FD)[:3]
        S, sd, ld = post_sd(np.vstack([Jh, Je]))
        i0 = R.tindex(o['times'], R.EXP0)
        dcl = (o['cl5'][i0:, 0] - ref['cl5'][i0:, 0]) * R.MW[R.I_CL]
        i340 = slice(i0, R.tindex(o['times'], R.EXP1) + 1)
        resp = float(np.abs(np.log(o['wells'][i340, 0, 2, R.I_CL] / ref['wells'][i340, 0, 2, R.I_CL])).max())
        rows.append(dict(design=d, label=dlabel(d), cost=float(dcl.max()), relief=float(-dcl.min()), logdet=ld,
                         sd=sd.tolist(), goal_sd=np.sqrt(np.diag(Jg @ S @ Jg.T)).tolist(), resp340=resp,
                         sens_a1=float(np.linalg.norm(Je[:, 3])), sens_b1=float(np.linalg.norm(Je[:, 4])),
                         sens_E=float(np.linalg.norm(Je[:, 7]))))
        print('D %-14s cost %5.1f relief %5.1f logdet %5.2f sd(a1,b1,E) %s goal_sd %s' %
              (rows[-1]['label'], rows[-1]['cost'], rows[-1]['relief'], ld, np.round(sd[[3, 4, 7]], 2),
               np.round(rows[-1]['goal_sd'], 2)), flush=True)
    Jg0 = C.jac(C.goals(ref), H_FD)[:3]
    S_h, sd_h, ld_h = post_sd(Jh)
    hist = dict(sd=sd_h.tolist(), logdet=ld_h, goal_sd=np.sqrt(np.diag(Jg0 @ S_h @ Jg0.T)).tolist(),
                goal_sd_prior=np.sqrt(np.diag(Jg0 @ Jg0.T)).tolist(),
                goal_grad=(Jg0 / np.abs(Jg0).max(1, keepdims=True)).tolist())
    # status-quo monitoring, by data type and by well
    Je0 = C.jac(C.obs_exp(ref), H_FD)
    ncl = 3 * len(C.CL_MONTHS)
    groups = {'Cl only': list(range(ncl)), 'ions only': list(range(ncl, Je0.shape[0]))}
    for k, w in enumerate(['503', '341', '340']):
        groups['well ' + w] = [i for i in range(ncl) if i % 3 == k] + \
            [ncl + (t * 3 + k) * 6 + j for t in range(len(C.ION_TIMES)) for j in range(6)]
    by = {}
    for g, rr in groups.items():
        S, sd, ld = post_sd(np.vstack([Jh, Je0[rr]]))
        by[g] = dict(sd=sd.tolist(), logdet=ld, goal_sd=np.sqrt(np.diag(Jg0 @ S @ Jg0.T)).tolist())
    # spectral matching: the low-frequency combination log s_v - log(1 + b1 + b2) (effective front velocity)
    S_all, _, _ = post_sd(np.vstack([Jh, Je0]))
    b1, b2 = np.exp(C.M0[4]), np.exp(C.M0[6])
    g = np.zeros(C.M0.size)
    g[0] = C.S0[0]; g[4] = -C.S0[4] * b1 / (1 + b1 + b2); g[6] = -C.S0[6] * b2 / (1 + b1 + b2)
    sd_all = np.sqrt(np.diag(S_all))
    eff = dict(prior_sd=float(np.linalg.norm(g)), post_sd_hist=float(np.sqrt(g @ S_h @ g)),
               post_sd_all=float(np.sqrt(g @ S_all @ g)),
               cos_goal=[float(Jg0[i] @ g / np.linalg.norm(Jg0[i]) / np.linalg.norm(g)) for i in range(3)],
               corr_sv_b1=float(S_all[0, 4] / sd_all[0] / sd_all[4]),
               goal_grad_a1_rel=[float(abs(Jg0[i, 3]) / np.abs(Jg0[i]).max()) for i in range(3)])
    print('H effective velocity sd prior %.3f hist %.3f all %.3f cos(goal) %s corr(sv,b1) %.2f' %
          (eff['prior_sd'], eff['post_sd_hist'], eff['post_sd_all'], np.round(eff['cos_goal'], 2), eff['corr_sv_b1']), flush=True)
    return dict(hist=hist, designs=rows, monitoring_groups=by, eff=eff)


def units():
    ncl = 3 * len(C.CL_MONTHS)
    U, L = [], []
    for i in range(ncl):
        U.append([i]); L.append(['Cl', ['503', '341', '340'][i % 3], float(C.CL_MONTHS[i // 3])])
    for t in range(len(C.ION_TIMES)):
        for k in range(3):
            U.append([ncl + (t * 3 + k) * 6 + j for j in range(6)]); L.append(['ions', ['503', '341', '340'][k], float(C.ION_TIMES[t])])
    return U, L


ROUTINE = [('Cl', w, t) for w in ('503', '341', '340') for t in (2027.0, 2029.5)] + \
          [('ions', w, t) for w in ('503', '341', '340') for t in (2028.5, 2031.0)]


def part_G(k=12):
    U = C.fd_ensemble(H_FD)
    ref = R.simulate(C.to_P(U), {'kind': 'const'})
    Jh, Je = C.jac(C.obs_hist(ref), H_FD), C.jac(C.obs_exp(ref), H_FD)
    Jg = C.jac(C.goals(ref), H_FD)[:3]
    UN, LB = units()

    def gsd(rows):
        S, _, _ = post_sd(np.vstack([Jh, Je[rows]]) if rows else Jh)
        return np.sqrt(np.diag(Jg @ S @ Jg.T))
    sel, rows, path = [], [], []
    for _ in range(k):
        best = min(((np.log(gsd(rows + UN[u]) ** 2).sum(), u) for u in range(len(UN)) if u not in sel))
        sel.append(best[1]); rows += UN[best[1]]
        path.append(dict(unit=LB[best[1]], goal_sd=gsd(rows).tolist()))
    rout = [LB.index([a, b, c]) for a, b, c in ROUTINE]
    rrows = sum((UN[u] for u in rout), [])
    allrows = list(range(Je.shape[0]))
    res = dict(greedy=[LB[u] for u in sel], greedy_rows=rows, path=path, routine=[LB[u] for u in rout],
               routine_rows=rrows, goal_sd_hist=gsd([]).tolist(), goal_sd_greedy=gsd(rows).tolist(),
               goal_sd_routine=gsd(rrows).tolist(), goal_sd_all=gsd(allrows).tolist(), n_units_all=len(UN))
    print('G greedy', [tuple(x) for x in res['greedy']]); print('  goal sd hist', np.round(res['goal_sd_hist'], 2),
          'greedy', np.round(res['goal_sd_greedy'], 2), 'routine', np.round(res['goal_sd_routine'], 2),
          'all', np.round(res['goal_sd_all'], 2), flush=True)
    return res


def one_V(args):
    r, configs = args
    rng = np.random.default_rng(4300 + r)
    ut = C.M0 + C.S0 * rng.standard_normal(C.M0.size)
    out_t = R.simulate(C.to_P(ut[None, :]), {'kind': 'const'})
    yh, ye = C.obs_hist(out_t)[0], C.obs_exp(out_t)[0]
    dh = yh + C.SIG_OBS * rng.standard_normal(yh.size)
    de = ye + C.SIG_OBS * rng.standard_normal(ye.size)
    gt = C.goals(out_t)[0]
    res = dict(truth_u=ut.tolist(), truth_goals=gt.tolist())
    for name, rows in configs.items():
        rows = np.asarray(rows, int)
        d = np.concatenate([dh, de[rows]])
        fn = (lambda out, rows=rows: np.concatenate([C.obs_hist(out), C.obs_exp(out)[:, rows]], 1))
        U, out = C.esmda(d, fn, {'kind': 'const'}, np.random.default_rng(7000 + r), NE, NA)
        Gs = C.goals(out)
        res[name] = dict(goal_mean=Gs.mean(0).tolist(), goal_q05=np.quantile(Gs, 0.05, 0).tolist(),
                         goal_q95=np.quantile(Gs, 0.95, 0).tolist(), u_mean=U.mean(0).tolist(),
                         contraction=(U.std(0) / C.S0).tolist())
    return res


def part_V(G):
    configs = {'history': [], 'history + all monitoring': list(range(3 * len(C.CL_MONTHS) + 6 * 3 * len(C.ION_TIMES))),
               'history + greedy 12': G['greedy_rows'], 'history + routine 12': G['routine_rows']}
    t0 = time.time()
    with Pool(4) as pool:
        runs = pool.map(one_V, [(r, configs) for r in range(NV)])
    summ = {}
    for name in configs:
        gm = np.array([x[name]['goal_mean'] for x in runs]); gt = np.array([x['truth_goals'] for x in runs])
        lo = np.array([x[name]['goal_q05'] for x in runs]); hi = np.array([x[name]['goal_q95'] for x in runs])
        con = np.array([x[name]['contraction'] for x in runs])
        um = np.array([x[name]['u_mean'] for x in runs]); ut = np.array([x['truth_u'] for x in runs])
        summ[name] = dict(rmse=np.sqrt(((gm - gt) ** 2).mean(0)).tolist(),
                          cover90=((gt >= lo) & (gt <= hi)).mean(0).tolist(),
                          width90=(hi - lo).mean(0).tolist(), contraction=con.mean(0).tolist(),
                          z_rmse=np.sqrt((((um - ut) / C.S0) ** 2).mean(0)).tolist())
        print('V %-26s rmse %s cover %s contraction(a1,b1,a2,b2,E) %s' % (name, np.round(summ[name]['rmse'], 2),
              np.round(summ[name]['cover90'], 2), np.round(np.array(summ[name]['contraction'])[[3, 4, 5, 6, 7]], 2)), flush=True)
    print('V done in %.0f s' % (time.time() - t0))
    return dict(summary=summ, runs=runs, n_truths=NV, ne=NE, na=NA)


# ---------------------------------------------------------------------------------------------------- tides (flow)
TIDE = {'M2': 12.4206 / 24.0, 'K1': 23.9345 / 24.0, 'MSf': 14.7653, 'Sa': 365.2422}     # periods in days
XW_TIDE = np.array([500.0, 1000.0, 2000.0])                  # wells (m from the coast)
TH_TIDE = dict(D=2.0e7, a1=1.0, b1=0.5, a2=1.0 / 60.0, b2=2.0)  # T/S = 6000/3e-4 m2/d, rates (1/d), capacities
SD_TIDE = np.array([0.4, 0.3, 0.3, 0.4, 0.4])                 # prior sd of log D, log a1, log b1, log a2, log b2


def tide_response(th, w):
    """Complex ratio h(x)/h(0) for a tide of angular frequency w (rad/d) in a confined aquifer with storage memory:
    S (1 + kappa_hat(i w)) i w h = T h'', kappa_hat(l) = b1 a1/(a1 + l) + b2 a2/(a2 + l)."""
    D, a1, b1, a2, b2 = th
    lam = 1j * w
    kap = b1 * a1 / (a1 + lam) + b2 * a2 / (a2 + lam)
    k = np.sqrt(lam * (1.0 + kap) / D)
    return np.exp(-np.outer(XW_TIDE, k))                      # (wells, constituents)


def tide_obs(u, names):
    th = np.exp(u)
    w = np.array([2 * np.pi / TIDE[n] for n in names])
    r = tide_response(th, w)
    return np.concatenate([np.log(np.abs(r)).ravel(), np.angle(r).ravel()])


def part_T():
    u0 = np.log([TH_TIDE[k] for k in ('D', 'a1', 'b1', 'a2', 'b2')])
    sig = np.concatenate([np.full(1, 0.02), np.full(1, np.deg2rad(1.0))])     # 2 % amplitude, 1 degree phase
    out = {}
    for names in (['M2'], ['M2', 'K1'], ['M2', 'K1', 'MSf'], ['M2', 'K1', 'MSf', 'Sa']):
        h = 1e-4
        J = np.stack([(tide_obs(u0 + h * SD_TIDE * e, names) - tide_obs(u0 - h * SD_TIDE * e, names)) / (2 * h)
                      for e in np.eye(5)], 1)
        n = len(names) * XW_TIDE.size
        W = np.concatenate([np.full(n, 1 / 0.02 ** 2), np.full(n, 1 / np.deg2rad(1.0) ** 2)])
        Hm = J.T @ (W[:, None] * J)
        S = np.linalg.inv(Hm + np.eye(5))
        out['+'.join(names)] = dict(sd=np.sqrt(np.diag(S)).tolist(), logdet=float(np.linalg.slogdet(Hm + np.eye(5))[1]),
                                     rank=int((np.linalg.eigvalsh(Hm) > 1.0).sum()))
        print('T %-16s post sd (D,a1,b1,a2,b2) %s informed %d' % ('+'.join(names), np.round(np.sqrt(np.diag(S)), 2),
              out['+'.join(names)]['rank']), flush=True)
    # amplitude and phase along the transect, with and without memory, for the figure
    xs = np.linspace(0.0, 5000.0, 101)
    prof = {}
    for n, P in TIDE.items():
        w = 2 * np.pi / P
        for lab, th in (('memory', [TH_TIDE[k] for k in ('D', 'a1', 'b1', 'a2', 'b2')]),
                        ('no memory', [TH_TIDE['D'], 1.0, 0.0, 1.0, 0.0])):
            D, a1, b1, a2, b2 = th
            kap = b1 * a1 / (a1 + 1j * w) + b2 * a2 / (a2 + 1j * w)
            k = np.sqrt(1j * w * (1 + kap) / D)
            r = np.exp(-xs * k)
            prof[f'{n}|{lab}'] = dict(amp=np.abs(r).tolist(), phase_deg=np.rad2deg(-np.angle(r)).tolist())
    out['profiles'] = dict(x=xs.tolist(), curves=prof, periods_days=TIDE, wells=XW_TIDE.tolist(), theta=TH_TIDE)
    return out


if __name__ == '__main__':
    parts = sys.argv[1:] or ['S', 'H', 'G', 'T', 'V']
    res = load()
    t0 = time.time()
    if 'S' in parts:
        res['S'] = part_S(); save(res)
    if 'H' in parts or 'D' in parts:
        res['HD'] = part_HD(); save(res)
    if 'G' in parts:
        res['G'] = part_G(); save(res)
    if 'T' in parts:
        res['T'] = part_T(); save(res)
    if 'V' in parts:
        res['V'] = part_V(res['G']); save(res)
    print('done in %.0f s' % (time.time() - t0))
