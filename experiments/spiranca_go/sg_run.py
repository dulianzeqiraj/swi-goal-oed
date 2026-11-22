"""SPIRANCA-GO: run the comparison of chloride alarms and of monitoring designs on the Fushe-Kuqe sector model.
For each of NT aquifers (prior draws of the chloride study):
  record   160 seasons (40 years x 4): first 120 fit the proxy, last 40 calibrate its margin (split conformal)
  future   4000 seasons after the decision, in four scenarios: no warming; worst warming (du = DU_MAX);
           warming du ~ U(0, DU_MAX); off-span stress (private abstraction +30 %, no recharge change)
  alarm    'Y below phi* is coming' when the proxy Yhat <= phi* + margin
Methods (all use the same record):
  ols      least squares of Y on the heads X, margin from the calibration residuals
  olsA     least squares of Y on X and the anchors A (= partialling out A, then the anchor correction at test time)
  ar_cv    anchor regression (Rothenhaeusler et al. 2021) on X, gamma by blocked cross-validation (90 % quantile)
  ar_dec   anchor regression with gamma = Mahalanobis length of the decision (the gamma Theorem 1 needs to cover it)
  iv       gamma -> infinity
  olsA_c   olsA with the SPIRANCA-GO certificate added to its margin (no change of b)
  spir     SPIRANCA-GO: b minimises the certified one-sided margin; anchor correction for the recorded anchors
Designs of three monitoring wells out of 16: nearest to A1, largest record R^2 (information only), smallest
SPIRANCA-GO certified margin. Output res/sg.json
Run: python3 sg_run.py [NT] [workers]"""
import os, sys, json, time, itertools
import numpy as np
from multiprocessing import Pool
from scipy.stats import norm
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sg_model as G

ALPHA = 0.10
Z = norm.ppf(1 - ALPHA)
N_FIT, N_CAL, N_FUT = 120, 40, 4000
GAMMAS = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 1e8]
METHODS = ['ols', 'olsA', 'ar_cv', 'ar_dec', 'iv', 'olsA_c', 'spir']
SCEN = ['none', 'worst', 'uniform', 'offspan']
BED = None


def init():
    global BED
    BED = G.Bed()


# ------------------------------------------------------------------ estimators
def lsq(M, y):
    return np.linalg.lstsq(M, y, rcond=None)[0]


def anchor_fit(X, Y, A, gamma):
    """anchor regression with intercept (data centred by their means), returns (mu_X, mu_Y, b)."""
    mX, mY, mA = X.mean(0), Y.mean(), A.mean(0)
    Xc, Yc, Ac = X - mX, Y - mY, A - mA
    Q, _ = np.linalg.qr(Ac)
    f = np.sqrt(gamma) - 1.0 if gamma < 1e7 else None
    if f is None:      # limit: two-stage least squares
        b = lsq(Q.T @ Xc, Q.T @ Yc)
    else:
        Xt = Xc + f * Q @ (Q.T @ Xc); Yt = Yc + f * Q @ (Q.T @ Yc)
        b = lsq(Xt, Yt)
    return mX, mY, b


def parts(X, Y, A):
    """regressions of X and Y on the anchors: coefficient blocks and residuals."""
    A1 = np.column_stack([np.ones(len(A)), A])
    cX, cY = lsq(A1, X), lsq(A1, Y)
    return dict(A1=A1, cX=cX, cY=cY, eX=X - A1 @ cX, eY=Y - A1 @ cY, WX=cX[1:], wY=cY[1:])


KAPPA = norm.ppf(0.95)      # one-sided 95 % bound on the two estimated shifts


def spir_parts(P, A, dec):
    """the quantities the certificate needs, from the regressions on the anchors of the fitting record."""
    S = np.atleast_2d(np.cov(P['eX'].T, bias=True)); eyc = P['eY'] - P['eY'].mean()
    s = (P['eX'] * eyc[:, None]).mean(0); syy = eyc.var()
    Si = np.linalg.inv(S + 1e-12 * np.trace(S) * np.eye(len(S)))
    b0 = Si @ s; q0 = max(syy - s @ b0, 1e-12)
    g = P['WX'][0]; wr = P['wY'][0]
    Sig = Si @ g; hn = np.sqrt(max(g @ Sig, 1e-30))
    G1 = np.linalg.inv(P['A1'].T @ P['A1']) * len(A)            # (A1'A1/n)^-1
    c_r = np.sqrt(G1[1, 1] / len(A))                              # se of the r-coefficient per unit residual sd
    d1 = np.r_[1.0, dec]; d0 = np.r_[1.0, A.mean(0)]
    c_d = np.sqrt(max((d1 - d0) @ G1 @ (d1 - d0), 0.0) / len(A))  # se of the correction at the decision
    return dict(b0=b0, q0=q0, l0=wr - g @ b0, Sig=Sig, hn=hn, c_r=c_r, c_d=c_d)


def cert_terms(sd, l, Q, du_max):
    """margin added to the conformal quantile: decision bound + one-sided warming bound."""
    return KAPPA * Q['c_d'] * sd + du_max * max(0.0, l + KAPPA * Q['c_r'] * sd)


def spir_b(P, A, dec, du_max):
    """SPIRANCA-GO slope: minimise z sd(b) + cert(b). For a fixed l(b) the smallest sd(b) lies on the line
    b(tau) = b0 + tau Sig / |h|, with sd = sqrt(q0 + tau^2) and l = l0 - tau |h|, so the convex problem is 1-D."""
    from scipy.optimize import minimize_scalar
    Q = spir_parts(P, A, dec)
    f = lambda t: Z * np.sqrt(Q['q0'] + t * t) + cert_terms(np.sqrt(Q['q0'] + t * t), Q['l0'] - t * Q['hn'], Q, du_max)
    T = abs(Q['l0']) / Q['hn'] * 4 + 10 * np.sqrt(Q['q0'])
    r = minimize_scalar(f, bounds=(-T, T), method='bounded', options=dict(xatol=1e-10 * (1 + T)))
    return Q['b0'] + r.x * Q['Sig'] / Q['hn']


def predictor(name, X, Y, A, dec, du_max):
    """returns a function yhat(X, A), the slope b and the anchor-correction vector w (or None)."""
    if name in ('ols',):
        mX, mY, b = anchor_fit(X, Y, A, 1.0); w = None; mA = None
    elif name in ('olsA', 'olsA_c', 'spir'):
        P = parts(X, Y, A)
        if name == 'spir':
            b = spir_b(P, A, dec, du_max)
        else:
            b = lsq(P['eX'] - P['eX'].mean(0), P['eY'] - P['eY'].mean())
        w = P['wY'] - P['WX'] @ b
        c0 = P['cY'][0] - P['cX'][0] @ b
        return (lambda Xn, An: c0 + Xn @ b + An @ w), b, w
    elif name == 'ar_cv':
        g = cv_gamma(X, Y, A); mX, mY, b = anchor_fit(X, Y, A, g); w = None
    elif name == 'ar_dec':
        Ac = A - A.mean(0); Sa = Ac.T @ Ac / len(A)
        d = dec - A.mean(0)
        g = max(1.0, float(d @ np.linalg.solve(Sa, d)))
        mX, mY, b = anchor_fit(X, Y, A, g); w = None
    elif name == 'iv':
        mX, mY, b = anchor_fit(X, Y, A, 1e8); w = None
    return (lambda Xn, An: mY + (Xn - mX) @ b), b, w


def cv_gamma(X, Y, A, block=8):
    n = len(Y); nb = n // block
    best, bg = np.inf, 1.0
    for g in GAMMAS:
        mse = []
        for k in range(nb):
            te = np.zeros(n, bool); te[k * block:(k + 1) * block] = True
            mX, mY, b = anchor_fit(X[~te], Y[~te], A[~te], g)
            mse.append(np.mean((Y[te] - mY - (X[te] - mX) @ b) ** 2))
        q = np.quantile(mse, 0.9)
        if q < best: best, bg = q, g
    return bg


def conformal_margin(r):
    """upper (1 - alpha) split-conformal quantile of the over-prediction r = Yhat - Y."""
    r = np.sort(r); k = int(np.ceil((1 - ALPHA) * (len(r) + 1)))
    return float(r[min(k, len(r)) - 1])


# ------------------------------------------------------------------ one aquifer
def one(seed):
    rng0 = np.random.default_rng(seed)
    m = BED.m
    P = m.sample_prior(1, rng0)
    p = m.one(P, 0)
    T = BED.truth(p)
    cA = BED.cA
    phis = BED.phi_star(T, cA)
    if not np.isfinite(phis):
        return None
    # pumping scale: exceedance after the decision without warming = P_EXC_DEC (common random numbers)
    rngs = np.random.default_rng(seed + 7)
    An, S1 = G.seasons(rngs, 4000, T, 1.0, decision=G.U_DEC)
    base = S1.copy(); base[:, 1:] = 0.0
    y_R = base @ T['U'][cA]; y_P = (S1 - base) @ T['U'][cA]          # Y = y_R + s * y_P
    if np.mean(y_R < phis) > G.P_EXC_DEC:
        return None
    lo, hi = 0.0, 1.0
    while np.mean(y_R + hi * y_P < phis) < G.P_EXC_DEC and hi < 1e3:
        hi *= 2
    if hi >= 1e3:
        return None
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if np.mean(y_R + mid * y_P < phis) < G.P_EXC_DEC: lo = mid
        else: hi = mid
    s = 0.5 * (lo + hi)
    # monitoring noise in phi units (0.1 m of head through the Strack transform at the mean state)
    Am, Sm = G.seasons(np.random.default_rng(seed + 11), 400, T, s)
    phim = Sm.mean(0) @ T['U'][BED.mon_cells].T
    xsd = np.array([G.HEAD_SD * float(BED.dphi_dh(T, phim[k], c)) for k, c in enumerate(BED.mon_cells)])
    # the record
    rng = np.random.default_rng(seed + 13)
    A, S = G.seasons(rng, N_FIT + N_CAL, T, s)
    Xall = G.observe(rng, S, T, BED.mon_cells, xsd); Y = S @ T['U'][cA]
    fit, cal = slice(0, N_FIT), slice(N_FIT, N_FIT + N_CAL)
    # the futures
    fut = {}
    for sc in SCEN:
        rf = np.random.default_rng(seed + 17)
        if sc == 'uniform':
            du = rf.uniform(0, G.DU_MAX, N_FUT)
            Af, Sf = G.seasons(rf, N_FUT, T, s, decision=G.U_DEC, du=du)
        else:
            du = {'none': 0.0, 'worst': G.DU_MAX, 'offspan': 0.0}[sc]
            Af, Sf = G.seasons(rf, N_FUT, T, s, decision=G.U_DEC, du=du, h_extra=0.3 if sc == 'offspan' else 0.0)
        fut[sc] = (Af, G.observe(rf, Sf, T, BED.mon_cells, xsd), Sf @ T['U'][cA])
    dec = np.array([0.0, G.U_DEC[0], G.U_DEC[1]])
    out = dict(seed=seed, s=s, phis=phis, exc={sc: float(np.mean(fut[sc][2] < phis)) for sc in SCEN},
               y_sd=float(Y.std()), xsd_med=float(np.median(xsd)))

    def evaluate(cols, name):
        X = Xall[:, cols]
        f, b, w = predictor(name, X[fit], Y[fit], A[fit], dec, G.DU_MAX)
        marg = conformal_margin(f(X[cal], A[cal]) - Y[cal])
        cert = 0.0
        if name in ('olsA_c', 'spir'):
            P = parts(X[fit], Y[fit], A[fit]); Q = spir_parts(P, A[fit], dec)
            lb = P['wY'][0] - P['WX'][0] @ b
            cert = cert_terms(float(np.std(P['eY'] - P['eX'] @ b)), float(lb), Q, G.DU_MAX)
        marg += cert
        res = dict(margin=marg, cert=cert)
        for sc in SCEN:
            Af, Xf, Yf = fut[sc]
            yh = f(Xf[:, cols], Af)
            over = yh - Yf > marg
            bad = Yf < phis
            alarm = yh <= phis + marg
            res[sc] = dict(over=float(over.mean()), miss=float(np.mean(~alarm[bad])) if bad.any() else 0.0,
                           false=float(np.mean(alarm[~bad])) if (~bad).any() else 0.0)
        return res

    allc = list(range(len(BED.mon_cells)))
    out['all'] = {nm: evaluate(allc, nm) for nm in METHODS}
    # designs of three wells
    dA = np.hypot(BED.m.cx[BED.mon_cells] - BED.m.cx[cA], BED.m.cy[BED.mon_cells] - BED.m.cy[cA])
    near = list(np.argsort(dA)[:3])
    best_r2, best_sp = (-1, None), (np.inf, None)
    for S3 in itertools.combinations(allc, 3):
        S3 = list(S3)
        X = Xall[fit][:, S3]
        mX, mY, b = anchor_fit(X, Y[fit], A[fit], 1.0)
        r2 = 1 - np.var(Y[fit] - mY - (X - mX) @ b) / np.var(Y[fit])
        if r2 > best_r2[0]: best_r2 = (r2, S3)
        Pp = parts(X, Y[fit], A[fit]); bs = spir_b(Pp, A[fit], dec, G.DU_MAX)
        Qp = spir_parts(Pp, A[fit], dec)
        lb = Pp['wY'][0] - Pp['WX'][0] @ bs
        sd = float((Pp['eY'] - Pp['eX'] @ bs).std())
        # design score: certified margin estimated on the fitting record only (the calibration part stays clean)
        mg = Z * sd + cert_terms(sd, float(lb), Qp, G.DU_MAX)
        if mg < best_sp[0]: best_sp = (mg, S3)
    out['designs'] = {}
    for dn, S3 in (('near', near), ('r2', best_r2[1]), ('spir', best_sp[1])):
        out['designs'][dn] = dict(wells=[BED.mon_ids[k] for k in S3],
                                  spir=evaluate(S3, 'spir'), ols=evaluate(S3, 'ols'), olsA=evaluate(S3, 'olsA'))
    return out


def main():
    NT = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    W = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    t0 = time.time()
    seeds = [1000 + 37 * k for k in range(int(NT * 1.6))]
    rows = []
    with Pool(W, initializer=init) as pool:
        for r in pool.imap(one, seeds):
            if r is not None:
                rows.append(r)
                print(f"aquifer {len(rows):2d} seed {r['seed']} s {r['s']:.2f} exc {[round(r['exc'][k], 2) for k in SCEN]} "
                      f"spir worst over {r['all']['spir']['worst']['over']:.3f} olsA {r['all']['olsA']['worst']['over']:.3f} "
                      f"ols {r['all']['ols']['worst']['over']:.3f}", flush=True)
            if len(rows) >= NT:
                pool.terminate(); break
    json.dump(dict(rows=rows, alpha=ALPHA, du_max=G.DU_MAX, u_dec=G.U_DEC.tolist(), n_fit=N_FIT, n_cal=N_CAL,
                   n_fut=N_FUT, mon_ids=None, cpu_s=time.time() - t0),
              open(os.path.join(HERE, 'res', 'sg.json'), 'w'), indent=1)
    print('done in', round(time.time() - t0), 's')


if __name__ == '__main__':
    main()
