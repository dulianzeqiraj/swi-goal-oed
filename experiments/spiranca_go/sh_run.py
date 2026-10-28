"""Review 61, objective function (13) with epsilon = 5%: the cap H_max on private abstraction in a declared drought,
against the other lever, a lower decided pumping u_dec.

Same aquifers, storylines, weather and ROJA-GO watch as sx_run.py, and the same closed-loop rule (pump u_dec while the
alarm is silent, -0.3 in the season after it sounds). New:
  declared drought  the agency declares a drought when the two-year filtered gauge anomaly, known at the start of the
                    season, is below D_THR (-1 sd); while declared, private abstraction is capped at H_max times its
                    mean: H_t = Hbar min(h_t, H_max).
  configurations    (u_dec, H_max) = (0.3, none), (0.3, 1.25), (0.3, 1.0), (0.3, 0.75), (0.3, 0.5), (0.2, none), (0.1, none)
                    the alarm is refitted for each u_dec (the decision enters the SPIRANCA-GO certificate).
Scores per configuration and storyline: exceedance share, utility water (share of the planned 1 + 0.3), private water
(share of what the farmers would have pumped without a cap), total water, share of seasons under a declaration.
Output res/sh.json. Run: python3 sh_run.py [NA] [workers]"""
import os, sys, json, time
import numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sv_model as V
import sv_run as R
import sx_run as X
import mg_model as M
import mg_setup as S

D_THR = -1.0
CONFIGS = [(0.3, None), (0.3, 1.25), (0.3, 1.0), (0.3, 0.75), (0.3, 0.5), (0.2, None), (0.1, None)]
NTRAJ = X.NTRAJ
SCEN = X.SCEN
G = None


def init():
    global G
    G = V.grid_G()
    R.G = G; X.G = G


def key(cfg):
    return f"u{cfg[0]:.1f}_H{'none' if cfg[1] is None else f'{cfg[1]:.2f}'}"


def one(seed):
    tt = time.time()
    P = S.draws(1, seed)[0]
    m = V.SeasonModel(G, P=P, opts=V.OPTS, dt_yr=V.DT_YR)
    ys = m.steady()
    Hbar = 0.3 * P['q_in']
    sp = V.SeasonModel(G, P=P, opts=V.OPTS, dt_yr=V.DT_YR)
    sp.run(y0=ys, schedule=[(200, dict(xs=V.XS, Q=0.0, H=Hbar))], t0=-100 * M.YR, keep=False, toe=False)
    y0, z0 = sp.y_end, sp.z_end
    ramp = np.minimum(1.0, np.arange(1, V.N_REC + 1) / V.RAMP)
    r, u, fac, hfac, _ = V.drivers(np.random.default_rng(seed + 1), V.N_REC)
    hfac = hfac * Hbar

    def run_rec(Qbar):
        return V.simulate(G, P, y0, z0, 0.0, Qbar, r, u, fac, hfac / (V.HFRAC * Qbar), ramp)
    T_rec = V.N_REC * V.DT_YR * M.YR
    d0 = V.drivers(np.random.default_rng(seed + 100), V.N_FUT, r0=r[-1], decision=R.U_DEC)

    def end_J(Qbar):
        _, _, ye_, ze_ = run_rec(Qbar)
        JF = V.simulate(G, P, ye_, ze_, T_rec, Qbar, d0[0], d0[1], d0[2], d0[3] * Hbar / (V.HFRAC * Qbar), np.ones(V.N_FUT))[0]
        return JF[-1]
    lo, hi = 0.2, 12.0
    if end_J(hi) < R.TARGET * M.EPS_LIM:
        return None
    for _ in range(9):
        mid = np.sqrt(lo * hi)
        if end_J(mid) < R.TARGET * M.EPS_LIM: lo = mid
        else: hi = mid
    Qbar = np.sqrt(lo * hi)
    Jr, Hr, ye, ze = run_rec(Qbar)
    p_rec = ramp * (1 + u) - 1
    noise_rec = np.random.default_rng(seed + 2).standard_normal(Hr.shape) * V.HEAD_SD
    Hr_n = Hr + noise_rec
    A_rec, X_rec = R.anchor_feats(r, p_rec), R.head_feats(Hr_n)
    Y_rec = -np.log10(np.maximum(Jr, 1e-12))
    ystar = -np.log10(M.EPS_LIM)
    hscale = Hbar / (V.HFRAC * Qbar)
    drv = {sc: [X.fut_drivers(np.random.default_rng(seed + 100 + k), V.N_FUT, r[-1], sc) for k in range(NTRAJ)] for sc in SCEN}
    noiseF = [np.random.default_rng(seed + 500 + k).standard_normal((V.N_FUT, len(V.PIEZO_X))) * V.HEAD_SD for k in range(NTRAJ)]

    # alarm (SPIRANCA-GO) refitted for each decided pumping
    alarms = {}
    for ud in sorted({c[0] for c in CONFIGS}):
        dec_A = R.anchor_feats(np.r_[r, drv['none'][0][0]], np.r_[p_rec, np.full(V.N_FUT, ud)])[V.N_REC:].mean(0)
        f, b = R.predictor('spir', X_rec[R.FIT], Y_rec[R.FIT], A_rec[R.FIT], dec_A)
        res_cal = f(X_rec[R.CAL], A_rec[R.CAL]) - Y_rec[R.CAL]
        Pp = R.parts(X_rec[R.FIT], Y_rec[R.FIT], A_rec[R.FIT]); Qp = R.spir_parts(Pp, A_rec[R.FIT], dec_A)
        lb = float(R.R_DIR @ (Pp['wY'] - Pp['WX'] @ b))
        marg = R.conformal_margin(res_cal) + R.cert_terms(float(np.std(Pp['eY'] - Pp['eX'] @ b)), lb, Qp)
        d = res_cal[2:] - res_cal[:-2]
        alarms[ud] = dict(f=f, marg=marg, sd_diff=float(d.std()))

    # detectors of the watch (as in sx_run.py)
    Ph = R.parts(X_rec[R.FIT][:, :6], Y_rec[R.FIT], A_rec[R.FIT])
    rec_ix = slice(60, V.N_REC)
    e2r = R.ewma(r, 2.0)
    r_max, e2_max = float(np.abs(r[rec_ix]).max()), float(np.abs(e2r[rec_ix]).max())

    def head_resid(Xcur, Af):
        return Xcur - np.column_stack([np.ones(len(Af)), Af]) @ Ph['cX']
    eh_rec = head_resid(X_rec[:, :6], A_rec)
    dh = eh_rec[2:] - eh_rec[:-2]
    Si = np.linalg.inv(np.cov(dh[58:].T) + 1e-12 * np.eye(6))
    s_thr = float(np.einsum('ij,jk,ik->i', dh[58:], Si, dh[58:]).max())

    def detect(rg_all, A_all, Xc_all, k):
        i = V.N_REC + k
        rain = abs(rg_all[i]) > r_max or abs(R.ewma(rg_all[:i + 1], 2.0)[-1]) > e2_max
        dd = head_resid(Xc_all[i:i + 1], A_all[i:i + 1])[0] - head_resid(Xc_all[i - 2:i - 1], A_all[i - 2:i - 1])[0]
        return bool(rain or float(dd @ Si @ dd) > s_thr)

    def closed(cfg, sc, k):
        ud, hmax = cfg
        rg, fc, hf = drv[sc][k]
        rg_all = np.r_[r, rg]
        e2_all = R.ewma(rg_all, 2.0)
        uu = np.full(V.N_FUT, ud)
        J = np.zeros(V.N_FUT); Hh = np.zeros((V.N_FUT, len(V.PIEZO_X)))
        al = alarms[ud]
        w = X.Watch('roja', al['marg'], ystar, al['sd_diff'])
        y, z = ye, ze
        hp, hp0, decl = 0.0, 0.0, 0
        for j in range(V.N_FUT):
            declared = e2_all[V.N_REC + j - 1] < D_THR
            hj = min(hf[j], hmax) if (declared and hmax is not None) else hf[j]
            hp += hj; hp0 += hf[j]; decl += int(declared)
            J1, H1, y, z = V.simulate(G, P, y, z, T_rec + j * V.DT_YR * M.YR, Qbar, rg[j:j + 1], uu[j:j + 1], fc[j:j + 1],
                                      np.array([hj]) * hscale, np.ones(1))
            J[j] = J1[0]; Hh[j] = H1[0] + noiseF[k][j]
            if j == V.N_FUT - 1:
                break
            Yj = -np.log10(max(J[j], 1e-12))
            A_all = R.anchor_feats(rg_all[:V.N_REC + j + 1], np.r_[p_rec, uu[:j + 1]])
            X_all = R.head_feats(np.r_[Hr_n, Hh[:j + 1]])
            fire = detect(rg_all, A_all, X_all[:, :6], j)
            yh = float(al['f'](X_all[-1:], A_all[-1:])[0])
            cut = w.step(j, yh, Yj, fire)[0]
            uu[j + 1] = X.U_CUT if cut else ud
        util = float(np.mean(1 + uu) / (1 + R.U_DEC))
        priv = float(hp / hp0)
        tot = float((Qbar * np.sum(1 + uu) + Hbar * hp) / (Qbar * (1 + R.U_DEC) * V.N_FUT + Hbar * hp0))
        return dict(exc=float(np.mean(J > M.EPS_LIM)), water=util, priv=priv, total=tot, decl=decl / V.N_FUT,
                    cut=float(np.mean(uu < ud)), nsamp=int(w.nsamp))

    out = dict(seed=seed, Qbar=Qbar, Hbar=Hbar, res={})
    for cfg in CONFIGS:
        out['res'][key(cfg)] = {}
        for sc in SCEN:
            rs = [closed(cfg, sc, k) for k in range(NTRAJ)]
            out['res'][key(cfg)][sc] = {kk: float(np.mean([x[kk] for x in rs])) for kk in rs[0]}
    out['cpu'] = time.time() - tt
    return out


def main():
    NA = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    W = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    t0 = time.time()
    seeds = [7000 + 13 * k for k in range(int(NA * 1.5))]
    rows = []
    with Pool(W, initializer=init) as pool:
        for rr in pool.imap(one, seeds):
            if rr is not None:
                rows.append(rr)
                print(f"aquifer {len(rows):2d} seed {rr['seed']} " + ' '.join(
                    f"{k}:{max(v[s]['exc'] for s in SCEN):.3f}" for k, v in rr['res'].items()) + f" cpu {rr['cpu']:.0f}s", flush=True)
            if len(rows) >= NA:
                pool.terminate(); break
    json.dump(dict(rows=rows, configs=[key(c) for c in CONFIGS], scen=SCEN, d_thr=D_THR, ntraj=NTRAJ, cpu_s=time.time() - t0),
              open(os.path.join(HERE, 'res', 'sh.json' if NA >= 10 else 'sh_pilot.json'), 'w'), indent=1)
    print('done in', round(time.time() - t0), 's')


if __name__ == '__main__':
    main()
