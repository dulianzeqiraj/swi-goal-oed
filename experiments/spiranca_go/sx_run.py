"""ROJA-GO: intense rainfall, drought, a causal break and a compound event on the variable-density section, with the
stakeholder decision in closed loop.

The aquifers, the record, the decision (pumping anomaly +0.3 for 30 years) and the alarms are those of sv_run.py
(Section 7 of the SPIRANCA-GO note); the same seeds give the same aquifers. The future now contains one of five
storylines, all drawn from the same weather so that only the extreme differs:
  none      ordinary weather
  rain      intense rainfall: the gauge records +2.5 sd for two years (years 18-20), but only a fifth of the excess
            infiltrates (the rest runs off), so recharge and the farmers' abstraction follow +0.5 sd
  drought   a record-shattering drought: the rainfall anomaly averages -2 sd for six years (years 8-14)
  causal    the same drought, and the farmers respond to it three times as strongly as in the record (an unrecorded
            change of the causal mechanism: private abstraction roughly doubles)
  compound  the drought, followed at once by two years of intense rainfall on dry ground (as in 'rain')
Alarms (open loop): least squares on heads and anchors (olsA) and SPIRANCA-GO (spir), each static, re-anchored by a
yearly chloride sample (ra), and with the ROJA-GO watch (roja): an extra sample whenever an extreme is detected and a
re-anchoring window that shrinks to the last sample when the drift is fast. The parts of the watch are also run alone
(trig: extra samples only; adK: adaptive window only).
Detectors (seasonal, no chloride needed): the gauge leaves the range of the record (season value or two-year filter),
or the head residuals, after removing what the anchors explain, jump by more than anything in the record.
Closed loop: the utility pumps +0.3 unless the alarm sounded in the previous season, in which case it pumps -0.3.
Output res/sx.json. Run: python3 sx_run.py [NA] [workers]"""
import os, sys, json, time
import numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sv_model as V
import sv_run as R
import mg_model as M
import mg_setup as S

NTRAJ = 6
SCEN = ['none', 'rain', 'drought', 'causal', 'compound']
W_DRY = (16, 28)            # seasons of the drought (years 8-14 of the future)
W_RAIN = (36, 40)           # intense rainfall alone (years 18-20)
W_AFTER = (28, 32)          # intense rainfall right after the drought (compound)
D_AMP, R_AMP, R_EFF, FB = 2.0, 2.5, 0.2, 0.5
U_CUT = -0.3
STRESS = {'none': (0, V.N_FUT), 'rain': (36, 48), 'drought': (16, 36), 'causal': (16, 36), 'compound': (16, 40)}
OPEN = ['olsA', 'olsA_ra', 'olsA_roja', 'spir', 'spir_ra', 'spir_trig', 'spir_adK', 'spir_roja']
CLOSED = ['spir', 'spir_ra', 'spir_roja', 'oracle']
DRIFT_C = 3.0
G = None


def init():
    global G
    G = V.grid_G()
    R.G = G


def fut_drivers(rng, n, r0, kind):
    """recorded gauge anomaly, inflow factor and private-abstraction factor of one storyline (same draws for all)."""
    r = np.empty(n); prev = r0
    for k in range(n):
        prev = V.PH * prev + np.sqrt(1 - V.PH ** 2) * rng.standard_normal(); r[k] = prev
    eR, eH = rng.standard_normal(n), rng.standard_normal(n)
    rg, re, fb = r.copy(), r.copy(), np.zeros(n)
    if kind in ('drought', 'causal', 'compound'):
        s = slice(*W_DRY); rg[s] = re[s] = 0.5 * r[s] - D_AMP
    if kind == 'causal':
        s = slice(*W_DRY); fb[s] = -FB * rg[s]
    for kk, w in (('rain', W_RAIN), ('compound', W_AFTER)):
        if kind == kk:
            s = slice(*w); rg[s] = r[s] + R_AMP; re[s] = r[s] + R_EFF * R_AMP
    fac = np.maximum(1.0 + 0.2 * re + 0.06 * eR, 0.2)
    hfac = np.maximum(1.0 - 0.25 * re + 0.15 * eH + fb, 0.0)
    return rg, fac, hfac


class Watch:
    """season-by-season alarm: static, yearly re-anchoring, or the ROJA-GO watch and its parts."""

    def __init__(self, mode, marg, ystar, sd_diff):
        self.mode, self.marg, self.ystar, self.sd_diff = mode, marg, ystar, sd_diff
        self.errs, self.nsamp, self.fired, self.drift = [], 0, -99, False

    def step(self, k, yh, Y, fire):
        if fire:
            self.fired = k
        if self.mode == 'static' or not self.errs:
            bias = 0.0
        else:
            K = R.RA_K
            if self.mode in ('roja', 'adK') and (self.drift or (self.mode == 'roja' and k - self.fired <= 2)):
                K = 1
            bias = float(np.mean(self.errs[-K:]))
        yr = yh - bias
        alarm, over = yr <= self.ystar + self.marg, yr - Y > self.marg
        if self.mode != 'static' and (k % 2 == 1 or (self.mode in ('trig', 'roja') and fire)):
            self.errs.append(yh - Y); self.nsamp += 1
            if len(self.errs) >= 2:
                self.drift = abs(self.errs[-1] - self.errs[-2]) > DRIFT_C * self.sd_diff
        return alarm, over, yr


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

    # ---------------------------------------------------------------- storylines (same weather) and open-loop futures
    drv = {sc: [fut_drivers(np.random.default_rng(seed + 100 + k), V.N_FUT, r[-1], sc) for k in range(NTRAJ)] for sc in SCEN}
    noiseF = [np.random.default_rng(seed + 500 + k).standard_normal((V.N_FUT, len(V.PIEZO_X))) * V.HEAD_SD for k in range(NTRAJ)]
    uD = np.full(V.N_FUT, R.U_DEC)
    fut = {}
    for sc in SCEN:
        fut[sc] = []
        for k in range(NTRAJ):
            rg, fc, hf = drv[sc][k]
            JF, HF, _, _ = V.simulate(G, P, ye, ze, T_rec, Qbar, rg, uD, fc, hf * hscale, np.ones(V.N_FUT))
            fut[sc].append((JF, HF + noiseF[k]))

    # ---------------------------------------------------------------- alarms fitted on the record
    dec_A = R.anchor_feats(np.r_[r, drv['none'][0][0]], np.r_[p_rec, uD])[V.N_REC:].mean(0)
    X, A = X_rec, A_rec
    alarms = {}
    for nm in ('olsA', 'spir'):
        f, b = R.predictor(nm, X[R.FIT], Y_rec[R.FIT], A[R.FIT], dec_A)
        res_cal = f(X[R.CAL], A[R.CAL]) - Y_rec[R.CAL]
        marg = R.conformal_margin(res_cal)
        if nm == 'spir':
            Pp = R.parts(X[R.FIT], Y_rec[R.FIT], A[R.FIT]); Qp = R.spir_parts(Pp, A[R.FIT], dec_A)
            lb = float(R.R_DIR @ (Pp['wY'] - Pp['WX'] @ b))
            marg += R.cert_terms(float(np.std(Pp['eY'] - Pp['eX'] @ b)), lb, Qp)
        d = res_cal[2:] - res_cal[:-2]
        alarms[nm] = dict(f=f, marg=marg, sd_diff=float(d.std()))

    # ---------------------------------------------------------------- detectors (no chloride needed)
    Ph = R.parts(X[R.FIT][:, :6], Y_rec[R.FIT], A[R.FIT])          # heads explained by the anchors
    rec_ix = slice(60, V.N_REC)
    e2 = R.ewma(r, 2.0)
    r_max, e2_max = float(np.abs(r[rec_ix]).max()), float(np.abs(e2[rec_ix]).max())

    def head_resid(Xcur, Af):
        return Xcur - np.column_stack([np.ones(len(Af)), Af]) @ Ph['cX']
    eh_rec = head_resid(X_rec[:, :6], A_rec)
    dh = eh_rec[2:] - eh_rec[:-2]
    Sd = np.cov(dh[58:].T) + 1e-12 * np.eye(6)
    Si = np.linalg.inv(Sd)
    s_rec = np.einsum('ij,jk,ik->i', dh[58:], Si, dh[58:])
    s_thr = float(s_rec.max())

    def detect(rg_all, A_all, Xc_all, k):
        """fires at future season k (index N_REC+k in the full series)."""
        i = V.N_REC + k
        rain = abs(rg_all[i]) > r_max or abs(R.ewma(rg_all[:i + 1], 2.0)[-1]) > e2_max
        e_now = head_resid(Xc_all[i:i + 1], A_all[i:i + 1])[0]
        e_bef = head_resid(Xc_all[i - 2:i - 1], A_all[i - 2:i - 1])[0]
        dd = e_now - e_bef
        head = float(dd @ Si @ dd) > s_thr
        return bool(rain or head), bool(rain), bool(head)

    out = dict(seed=seed, Qbar=Qbar, y_sd=float(Y_rec[R.FIT].std()), J_end_rec=float(Jr[-1] / M.EPS_LIM), ystar=float(ystar),
               r_max=r_max, e2_max=e2_max,
               rec_min6=float(np.min(np.convolve(r[rec_ix], np.ones(12) / 12, 'valid'))),
               marg={nm: float(alarms[nm]['marg']) for nm in alarms})

    # ---------------------------------------------------------------- open loop: exceedance and alarm validity
    out['exc'], out['exc_stress'], out['Jpeak'], out['open'], out['fire'] = {}, {}, {}, {}, {}
    series = {}
    for sc in SCEN:
        a0, a1 = STRESS[sc]
        Ys = [-np.log10(np.maximum(t[0], 1e-12)) for t in fut[sc]]
        out['exc'][sc] = float(np.mean(np.concatenate(Ys) < ystar))
        out['exc_stress'][sc] = float(np.mean(np.concatenate([y[a0:a1] for y in Ys]) < ystar))
        out['Jpeak'][sc] = float(np.median([t[0].max() / M.EPS_LIM for t in fut[sc]]))
        res = {m_: dict(over=[], over_s=[], miss=[], false=[], nsamp=[]) for m_ in OPEN}
        fires = dict(any=[], rain=[], head=[], any_stress=[], any_calm=[])
        for k in range(NTRAJ):
            rg = drv[sc][k][0]
            rg_all = np.r_[r, rg]
            A_all = R.anchor_feats(rg_all, np.r_[p_rec, uD])
            X_all = R.head_feats(np.r_[Hr_n, fut[sc][k][1]])
            Yf = Ys[k]
            fl = [detect(rg_all, A_all, X_all[:, :6], j) for j in range(V.N_FUT)]
            fa = np.array([x[0] for x in fl])
            fires['any'].append(fa.mean()); fires['rain'].append(np.mean([x[1] for x in fl])); fires['head'].append(np.mean([x[2] for x in fl]))
            stress = np.zeros(V.N_FUT, bool); stress[a0:a1] = True
            fires['any_stress'].append(fa[stress].mean() if sc != 'none' else fa.mean())
            fires['any_calm'].append(fa[~stress].mean() if sc != 'none' else fa.mean())
            for m_ in OPEN:
                base, mode = (m_.split('_') + ['static'])[:2]
                al = alarms[base]
                yh = al['f'](X_all[V.N_REC:], A_all[V.N_REC:])
                w = Watch(mode, al['marg'], ystar, al['sd_diff'])
                st = [w.step(j, yh[j], Yf[j], fa[j]) for j in range(V.N_FUT)]
                alarm = np.array([s_[0] for s_ in st]); over = np.array([s_[1] for s_ in st])
                bad = Yf < ystar
                res[m_]['over'].append(over.mean()); res[m_]['over_s'].append(over[a0:a1].mean())
                res[m_]['miss'].append(np.mean(~alarm[bad]) if bad.any() else np.nan)
                res[m_]['false'].append(np.mean(alarm[~bad]) if (~bad).any() else np.nan)
                res[m_]['nsamp'].append(w.nsamp)
                if k == 0 and m_ in ('spir', 'spir_ra', 'spir_roja'):
                    series.setdefault(sc, dict(Y=Yf.round(4).tolist(), fire=fa.astype(int).tolist(), rg=rg.round(3).tolist()))[m_] = \
                        np.array([s_[2] for s_ in st]).round(4).tolist()
        out['open'][sc] = {m_: {kk: float(np.nanmean(v)) for kk, v in d_.items()} for m_, d_ in res.items()}
        out['fire'][sc] = {kk: float(np.mean(v)) for kk, v in fires.items()}
    out['series'] = series

    # ---------------------------------------------------------------- closed loop: the stakeholder decision
    def closed(policy, sc, k):
        rg, fc, hf = drv[sc][k]
        rg_all = np.r_[r, rg]
        uu = np.full(V.N_FUT, R.U_DEC)
        J = np.zeros(V.N_FUT); Hh = np.zeros((V.N_FUT, len(V.PIEZO_X)))
        base, mode = 'spir', {'spir': 'static', 'spir_ra': 'ra', 'spir_roja': 'roja'}.get(policy, 'static')
        al = alarms[base]
        w = Watch(mode, al['marg'], ystar, al['sd_diff'])
        y, z = ye, ze
        for j in range(V.N_FUT):
            J1, H1, y, z = V.simulate(G, P, y, z, T_rec + j * V.DT_YR * M.YR, Qbar, rg[j:j + 1], uu[j:j + 1], fc[j:j + 1],
                                      hf[j:j + 1] * hscale, np.ones(1))
            J[j] = J1[0]; Hh[j] = H1[0] + noiseF[k][j]
            if j == V.N_FUT - 1:
                break
            Yj = -np.log10(max(J[j], 1e-12))
            if policy == 'oracle':
                cut = Yj <= ystar + 0.05
            else:
                A_all = R.anchor_feats(rg_all[:V.N_REC + j + 1], np.r_[p_rec, uu[:j + 1]])
                X_all = R.head_feats(np.r_[Hr_n, Hh[:j + 1]])
                fire = detect(rg_all, A_all, X_all[:, :6], j)[0] if mode == 'roja' else False
                yh = float(al['f'](X_all[-1:], A_all[-1:])[0])
                cut = w.step(j, yh, Yj, fire)[0]
            uu[j + 1] = U_CUT if cut else R.U_DEC
        Yc = -np.log10(np.maximum(J, 1e-12))
        a0, a1 = STRESS[sc]
        return dict(exc=float(np.mean(Yc < ystar)), exc_s=float(np.mean(Yc[a0:a1] < ystar)),
                    water=float(np.mean(1 + uu) / (1 + R.U_DEC)), cut=float(np.mean(uu < R.U_DEC)),
                    peak=float(J.max() / M.EPS_LIM), nsamp=int(w.nsamp))
    out['closed'] = {}
    for sc in SCEN:
        out['closed'][sc] = {}
        for pol in CLOSED:
            rs = [closed(pol, sc, k) for k in range(NTRAJ)]
            out['closed'][sc][pol] = {kk: float(np.mean([x[kk] for x in rs])) for kk in rs[0]}
        Yn = [-np.log10(np.maximum(t[0], 1e-12)) for t in fut[sc]]
        a0, a1 = STRESS[sc]
        out['closed'][sc]['none'] = dict(exc=out['exc'][sc], exc_s=out['exc_stress'][sc], water=1.0, cut=0.0,
                                         peak=float(np.mean([t[0].max() / M.EPS_LIM for t in fut[sc]])), nsamp=0)
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
                o = rr['open']; c = rr['closed']
                print(f"aquifer {len(rows):2d} seed {rr['seed']} exc {[round(rr['exc'][s], 2) for s in SCEN]} "
                      f"ra over_s {[round(o[s]['spir_ra']['over_s'], 2) for s in SCEN]} roja {[round(o[s]['spir_roja']['over_s'], 2) for s in SCEN]} "
                      f"CL exc ra {[round(c[s]['spir_ra']['exc'], 2) for s in SCEN]} roja {[round(c[s]['spir_roja']['exc'], 2) for s in SCEN]} "
                      f"cpu {rr['cpu']:.0f}s", flush=True)
            if len(rows) >= NA:
                pool.terminate(); break
    json.dump(dict(rows=rows, alpha=R.ALPHA, u_dec=R.U_DEC, u_cut=U_CUT, ntraj=NTRAJ, scen=SCEN, stress=STRESS,
                   w_dry=W_DRY, w_rain=W_RAIN, w_after=W_AFTER, d_amp=D_AMP, r_amp=R_AMP, r_eff=R_EFF, fb=FB,
                   ra_k=R.RA_K, drift_c=DRIFT_C, cpu_s=time.time() - t0),
              open(os.path.join(HERE, 'res', 'sx.json' if NA >= 10 else 'sx_pilot.json'), 'w'), indent=1)
    print('done in', round(time.time() - t0), 's')


if __name__ == '__main__':
    main()
