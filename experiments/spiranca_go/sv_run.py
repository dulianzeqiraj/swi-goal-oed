"""SPIRANCA-GO on the variable-density section (sv_model.py): does the certified alarm survive memory and nonlinearity?

For each aquifer (parameter draw of MONTIMI-GO):
  spin-up   pre-development equilibrium, then 100 years of the private abstraction alone (it predates the utility)
  record    80 years (160 half-year seasons): the supply well at 2 km ramps up over 10 years and then varies by season;
            rainfall, inflow and private abstraction vary as in sv_model.py. The mean pumping Qbar is set so that the
            screen sea fraction at the end of the record is a fifth of the limit (chloride about 60 mg/L).
  fit/cal   seasons 60-129 fit the alarm, 130-159 calibrate its margin (split conformal)
  future    30 years after the decision (pumping anomaly +0.3, sustained), NTRAJ weather sequences per scenario:
            no warming; worst unrecorded warming (du = DU_MAX); off-span stress (private abstraction +30 %)
  goal      Y = -log10(screen sea fraction); the standard is exceeded when Y < y* = -log10(eps_lim)
Features: anchors = rainfall anomaly and utility pumping anomaly, each with exponential filters of 2, 8 and 20 years
(memory enters through the anchor history); heads = six piezometers at mid-depth, now and filtered over 8 years.
The unrecorded warming is a persistent shift in the rainfall direction, so its direction in anchor space is the sum of
the four rainfall features. Output res/sv.json. Run: python3 sv_run.py [NA] [workers]"""
import os, sys, json, time, itertools
import numpy as np
from multiprocessing import Pool
from scipy.stats import norm
from scipy.optimize import minimize_scalar
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sv_model as V
import mg_model as M
import mg_setup as S

ALPHA = 0.10
Z = norm.ppf(1 - ALPHA)
KAPPA = norm.ppf(0.95)
FIT, CAL = slice(60, 130), slice(130, 160)
NTRAJ = 8
U_DEC = 0.3
DU_MAX = 1.0
TARGET = 0.2                      # screen sea fraction at the end of the record, as a fraction of the limit
TAUS = [2.0, 8.0, 20.0]           # years
SCEN = ['none', 'worst', 'offspan']
METHODS = ['ols', 'olsA', 'ar_cv', 'iv', 'olsA_c', 'spir']
G = None


def init():
    global G
    G = V.grid_G()


def ewma(x, tau_yr):
    a = np.exp(-V.DT_YR / tau_yr)
    out = np.empty_like(x, dtype=float); s = x[0]
    for k, v in enumerate(x):
        s = a * s + (1 - a) * v; out[k] = s
    return out


def anchor_feats(r, p):
    cols = [r, p]
    for t in TAUS:
        cols += [ewma(r, t), ewma(p, t)]
    return np.column_stack(cols)


R_DIR = np.array([1, 0] + [1, 0] * len(TAUS), float)    # a persistent rainfall shift moves every rainfall feature


def head_feats(Hn):
    return np.column_stack([Hn, np.column_stack([ewma(Hn[:, j], 8.0) for j in range(Hn.shape[1])])])


# ------------------------------------------------------------------ estimators (as in sg_run.py, with a direction)
def lsq(Mx, y):
    return np.linalg.lstsq(Mx, y, rcond=None)[0]


def anchor_fit(X, Y, A, gamma):
    mX, mY, mA = X.mean(0), Y.mean(), A.mean(0)
    Xc, Yc, Ac = X - mX, Y - mY, A - mA
    Q, _ = np.linalg.qr(Ac)
    if gamma > 1e7:
        b = lsq(Q.T @ Xc, Q.T @ Yc)
    else:
        f = np.sqrt(gamma) - 1.0
        b = lsq(Xc + f * Q @ (Q.T @ Xc), Yc + f * Q @ (Q.T @ Yc))
    return mX, mY, b


def parts(X, Y, A):
    A1 = np.column_stack([np.ones(len(A)), A])
    cX, cY = lsq(A1, X), lsq(A1, Y)
    return dict(A1=A1, cX=cX, cY=cY, eX=X - A1 @ cX, eY=Y - A1 @ cY, WX=cX[1:], wY=cY[1:])


def spir_parts(P, A, dec_A):
    S_ = np.atleast_2d(np.cov(P['eX'].T, bias=True)); eyc = P['eY'] - P['eY'].mean()
    s = (P['eX'] * eyc[:, None]).mean(0); syy = eyc.var()
    Si = np.linalg.inv(S_ + 1e-9 * np.trace(S_) / len(S_) * np.eye(len(S_)))
    b0 = Si @ s; q0 = max(syy - s @ b0, 1e-12)
    g = R_DIR @ P['WX']; wr = R_DIR @ P['wY']
    Sig = Si @ g; hn = np.sqrt(max(g @ Sig, 1e-30))
    G1 = np.linalg.inv(P['A1'].T @ P['A1'])
    d1 = np.r_[0.0, R_DIR]
    c_r = np.sqrt(max(d1 @ G1 @ d1, 0.0))
    dd = np.r_[1.0, dec_A] - np.r_[1.0, A.mean(0)]
    c_d = np.sqrt(max(dd @ G1 @ dd, 0.0))
    return dict(b0=b0, q0=q0, l0=wr - g @ b0, Sig=Sig, hn=hn, c_r=c_r, c_d=c_d)


def cert_terms(sd, l, Q):
    return KAPPA * Q['c_d'] * sd + DU_MAX * max(0.0, l + KAPPA * Q['c_r'] * sd)


def spir_b(P, A, dec_A):
    Q = spir_parts(P, A, dec_A)
    f = lambda t: Z * np.sqrt(Q['q0'] + t * t) + cert_terms(np.sqrt(Q['q0'] + t * t), Q['l0'] - t * Q['hn'], Q)
    T = abs(Q['l0']) / Q['hn'] * 4 + 10 * np.sqrt(Q['q0'])
    r = minimize_scalar(f, bounds=(-T, T), method='bounded', options=dict(xatol=1e-10 * (1 + T)))
    return Q['b0'] + r.x * Q['Sig'] / Q['hn']


def cv_gamma(X, Y, A, block=10):
    n = len(Y); nb = n // block; best, bg = np.inf, 1.0
    for gm in [0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 64.0, 1e8]:
        mse = []
        for k in range(nb):
            te = np.zeros(n, bool); te[k * block:(k + 1) * block] = True
            mX, mY, b = anchor_fit(X[~te], Y[~te], A[~te], gm)
            mse.append(np.mean((Y[te] - mY - (X[te] - mX) @ b) ** 2))
        q = np.quantile(mse, 0.9)
        if q < best: best, bg = q, gm
    return bg


def predictor(name, X, Y, A, dec_A):
    if name in ('olsA', 'olsA_c', 'spir'):
        P = parts(X, Y, A)
        b = spir_b(P, A, dec_A) if name == 'spir' else lsq(P['eX'] - P['eX'].mean(0), P['eY'] - P['eY'].mean())
        w = P['wY'] - P['WX'] @ b
        c0 = P['cY'][0] - P['cX'][0] @ b
        return (lambda Xn, An: c0 + Xn @ b + An @ w), b
    gm = {'ols': 1.0, 'iv': 1e8}.get(name) or cv_gamma(X, Y, A)
    mX, mY, b = anchor_fit(X, Y, A, gm)
    return (lambda Xn, An: mY + (Xn - mX) @ b), b


def conformal_margin(r):
    r = np.sort(r); k = int(np.ceil((1 - ALPHA) * (len(r) + 1)))
    return float(r[min(k, len(r)) - 1])


# ------------------------------------------------------------------ one aquifer
def one(seed):
    rng0 = np.random.default_rng(seed)
    P = S.draws(1, seed)[0]
    tt = time.time()
    m = V.SeasonModel(G, P=P, opts=V.OPTS, dt_yr=V.DT_YR)
    ys = m.steady()
    Hbar = 0.3 * P['q_in']
    # spin-up: 100 years of the private abstraction alone, average weather
    sp = V.SeasonModel(G, P=P, opts=V.OPTS, dt_yr=V.DT_YR)
    sp.run(y0=ys, schedule=[(200, dict(xs=V.XS, Q=0.0, H=Hbar))], t0=-100 * M.YR, keep=False, toe=False)
    y0, z0 = sp.y_end, sp.z_end
    ramp = np.minimum(1.0, np.arange(1, V.N_REC + 1) / V.RAMP)
    r, u, fac, hfac, _ = V.drivers(np.random.default_rng(seed + 1), V.N_REC)
    hfac = hfac * Hbar
    def run_rec(Qbar):
        return V.simulate(G, P, y0, z0, 0.0, Qbar, r, u, fac, hfac / (V.HFRAC * Qbar), ramp)
    # mean pumping so that the screen ends the record at TARGET of the limit (J increases with Qbar): log-bisection
    lo, hi = 0.2, 12.0
    Jhi = run_rec(hi)[0][-1]
    if Jhi < TARGET * M.EPS_LIM:
        return None
    for _ in range(9):
        mid = np.sqrt(lo * hi)
        if run_rec(mid)[0][-1] < TARGET * M.EPS_LIM: lo = mid
        else: hi = mid
    Qbar = np.sqrt(lo * hi)
    Jr, Hr, ye, ze = run_rec(Qbar)
    T_rec = V.N_REC * V.DT_YR * M.YR
    p_rec = ramp * (1 + u) - 1
    noise_rec = np.random.default_rng(seed + 2).standard_normal(Hr.shape) * V.HEAD_SD
    fut = {}
    for sc in SCEN:
        trajs = []
        for k in range(NTRAJ):
            rf = np.random.default_rng(seed + 100 + k)
            du = DU_MAX if sc == 'worst' else 0.0
            hx = 0.3 if sc == 'offspan' else 0.0
            rF, uF, facF, hfacF, _ = V.drivers(rf, V.N_FUT, r0=r[-1], decision=U_DEC, du=du, h_extra=hx)
            JF, HF, _, _ = V.simulate(G, P, ye, ze, T_rec, Qbar, rF, uF, facF, hfacF * Hbar / (V.HFRAC * Qbar), np.ones(V.N_FUT))
            nF = rf.standard_normal(HF.shape) * V.HEAD_SD
            pF = uF.copy()
            A_all = anchor_feats(np.r_[r, rF], np.r_[p_rec, pF])
            X_all = head_feats(np.r_[Hr + noise_rec, HF + nF])
            trajs.append((A_all[V.N_REC:], X_all[V.N_REC:], -np.log10(np.maximum(JF, 1e-12))))
        fut[sc] = trajs
    A_rec = anchor_feats(r, p_rec)
    X_rec = head_feats(Hr + noise_rec)
    Y_rec = -np.log10(np.maximum(Jr, 1e-12))
    ystar = -np.log10(M.EPS_LIM)
    dec_A = fut['none'][0][0].mean(0)                 # mean anchor features after the decision (no warming)
    out = dict(seed=seed, Qbar=Qbar, cpu=time.time() - tt, y_sd=float(Y_rec[FIT].std()),
               J_end_rec=float(Jr[-1] / M.EPS_LIM),
               exc={sc: float(np.mean(np.concatenate([t[2] for t in fut[sc]]) < ystar)) for sc in SCEN},
               J_end_fut={sc: float(np.median([10 ** (-t[2][-1]) for t in fut[sc]]) / M.EPS_LIM) for sc in SCEN})

    def evaluate(cols, name):
        cols2 = list(cols) + [c + 6 for c in cols]          # current and filtered heads of the chosen wells
        X = X_rec[:, cols2]
        f, b = predictor(name, X[FIT], Y_rec[FIT], A_rec[FIT], dec_A)
        marg = conformal_margin(f(X[CAL], A_rec[CAL]) - Y_rec[CAL])
        cert = 0.0
        if name in ('olsA_c', 'spir'):
            Pp = parts(X[FIT], Y_rec[FIT], A_rec[FIT]); Qp = spir_parts(Pp, A_rec[FIT], dec_A)
            lb = R_DIR @ (Pp['wY'] - Pp['WX'] @ b)
            cert = cert_terms(float(np.std(Pp['eY'] - Pp['eX'] @ b)), float(lb), Qp)
        marg += cert
        res = dict(margin=marg, cert=cert)
        for sc in SCEN:
            yh = np.concatenate([f(t[1][:, cols2], t[0]) for t in fut[sc]])
            Yf = np.concatenate([t[2] for t in fut[sc]])
            over = yh - Yf > marg; bad = Yf < ystar; alarm = yh <= ystar + marg
            late = np.concatenate([np.arange(V.N_FUT) >= V.N_FUT - 20 for _ in fut[sc]])
            res[sc] = dict(over=float(over.mean()), over_late=float(over[late].mean()),
                           miss=float(np.mean(~alarm[bad])) if bad.any() else 0.0,
                           false=float(np.mean(alarm[~bad])) if (~bad).any() else 0.0)
        return res

    allc = list(range(6))
    out['all'] = {nm: evaluate(allc, nm) for nm in METHODS}
    dist = np.abs(np.array(V.PIEZO_X) - V.XS)
    near = list(np.argsort(dist)[:3])
    best_r2, best_sp = (-1, None), (np.inf, None)
    for S3 in itertools.combinations(allc, 3):
        cols2 = list(S3) + [c + 6 for c in S3]
        X = X_rec[FIT][:, cols2]
        mX, mY, b = anchor_fit(X, Y_rec[FIT], A_rec[FIT], 1.0)
        r2 = 1 - np.var(Y_rec[FIT] - mY - (X - mX) @ b) / np.var(Y_rec[FIT])
        if r2 > best_r2[0]: best_r2 = (r2, list(S3))
        Pp = parts(X, Y_rec[FIT], A_rec[FIT]); bs = spir_b(Pp, A_rec[FIT], dec_A); Qp = spir_parts(Pp, A_rec[FIT], dec_A)
        sd = float((Pp['eY'] - Pp['eX'] @ bs).std()); lb = float(R_DIR @ (Pp['wY'] - Pp['WX'] @ bs))
        mg = Z * sd + cert_terms(sd, lb, Qp)
        if mg < best_sp[0]: best_sp = (mg, list(S3))
    out['designs'] = {dn: dict(wells=[V.PIEZO_X[k] for k in S3], spir=evaluate(S3, 'spir'), olsA=evaluate(S3, 'olsA'))
                      for dn, S3 in (('near', near), ('r2', best_r2[1]), ('spir', best_sp[1]))}
    out['cpu'] = time.time() - tt
    return out


def main():
    NA = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    W = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    t0 = time.time()
    seeds = [7000 + 13 * k for k in range(int(NA * 1.5))]
    rows = []
    with Pool(W, initializer=init) as pool:
        for r in pool.imap(one, seeds):
            if r is not None:
                rows.append(r)
                print(f"aquifer {len(rows):2d} seed {r['seed']} Qbar {r['Qbar']:.2f} exc {[round(r['exc'][k], 2) for k in SCEN]} "
                      f"spir over {[round(r['all']['spir'][k]['over'], 3) for k in SCEN]} olsA {[round(r['all']['olsA'][k]['over'], 3) for k in SCEN]} "
                      f"ols {round(r['all']['ols']['none']['over'], 3)} cpu {r['cpu']:.0f}s", flush=True)
            if len(rows) >= NA:
                pool.terminate(); break
    json.dump(dict(rows=rows, alpha=ALPHA, du_max=DU_MAX, u_dec=U_DEC, ntraj=NTRAJ, target=TARGET, taus=TAUS,
                   piezo_x=V.PIEZO_X, xs=V.XS, cpu_s=time.time() - t0), open(os.path.join(HERE, 'res', 'sv.json'), 'w'), indent=1)
    print('done in', round(time.time() - t0), 's')


if __name__ == '__main__':
    main()
