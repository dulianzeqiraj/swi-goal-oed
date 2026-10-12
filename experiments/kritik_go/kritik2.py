"""KRITIK-GO, input-output version: a head logger measures the recharge forcing, a salinity logger
the slow toe response; the recovery rate k of the toe (resilience, k -> 0 at the tipping point) is
estimated by input-output identification instead of from the toe's own fluctuations.

Uses the model, prior and parameters of kritik.py (Strack saddle-node + OU recharge anomalies).

1. Criteria for the salinity position s (head logger fixed at 1 000 m):
   J_IO(s)  Fisher information on ln k at near-critical states (Q in [0.85, 0.95] Q_c), with the
            response gain and the mean as nuisance parameters, averaged over the prior;
   J_PAS(s) the same for the passive (salinity-only) Whittle likelihood;
   J0(s)    status design: precision on the current toe position.
2. Stationary validation: 300 prior draws, far state (0.6 Q_c) vs near state (0.9 Q_c), 10 years of
   weekly data: AUC of the passive indicator (best of lag-1 autocorrelation and variance) and of the
   input-output estimate k_hat, and the relative error of k_hat in the near state.
3. Ramp validation for three designs (status, KRITIK-GO, sentinel at the well): alarm when k_hat over
   the trailing 5 years falls below a threshold set for 5 % false alarms on the null runs.
"""
import json, sys
import numpy as np
from scipy.stats import norm
import kritik as KR

rng = np.random.default_rng(7)
DT_W = 1.0 / 52.0                 # weekly logger averages
SUB = 7                           # daily sub-steps
SIG_H = 0.02                      # head logger noise [m]
S_HEAD = 1000.0                   # head logger position [m]
KGRID = np.exp(np.linspace(np.log(0.01), np.log(5.0), 90))   # 1/yr
OM = np.linspace(-150, 150, 60001)


def moments(k, g):
    """E[xi^2], E[xi dxi], E[dxi^2] for xi = response to OU forcing, d = derivative wrt ln k."""
    S_eps = 2 * KR.SIG_E ** 2 * KR.THETA / (1 + (OM * KR.THETA) ** 2)
    G = g / (k + 1j * OM)
    dG = -k * g / (k + 1j * OM) ** 2           # d/d ln k
    m = lambda A, B: np.real(np.trapezoid(A * np.conj(B) * S_eps, OM)) / (2 * np.pi)
    return m(G, G), m(G, dG), m(dG, dG)


def criteria(n_prior=200, T=10.0):
    Kp, qp = KR.draw_params(n_prior)
    N = T / DT_W
    J_io = np.zeros(len(KR.S_POS)); J_pas = np.zeros(len(KR.S_POS)); J0 = np.zeros(len(KR.S_POS))
    for Ki, qi in zip(Kp, qp):
        mu = Ki * KR.Phi_toe / (qi * KR.d); lc = KR.lam_crit(mu)
        for f in np.linspace(0.85, 0.95, 5):
            Xs, k, S_xi, var = KR.linear_toe(mu, f * lc)
            g = Xs / KR.TAU
            e11, e12, e22 = moments(k, g)
            resid = e22 - e12 ** 2 / e11               # nuisance gain projected out
            sd = np.sqrt(KR.W_MIX ** 2 + var * KR.d ** 2)
            a = norm.pdf((Xs * KR.d - KR.S_POS) / sd) * KR.d / sd
            J_io += N * a ** 2 * resid / KR.SIG_C ** 2
            J_pas += np.array([KR.whittle_info_lnk(s, Xs, k, S_xi, var) for s in KR.S_POS])
        Xs, k, S_xi, var = KR.linear_toe(mu, 0.5 * KR.lamc0 * KR.q00 / qi)
        J0 += norm.pdf((Xs * KR.d - KR.S_POS) / KR.W_MIX) ** 2
    n = len(Kp) * 5
    return J_io / n, J_pas / n, J0 / J0.max()


# ---------------------------------------------------------------- simulation of logger data
def head_at(s, q, Q, K):
    Phi = (q / K) * s + Q / (2 * np.pi * K) * np.log(abs(s - KR.d) / (s + KR.d))
    return np.where(Phi >= KR.Phi_toe, (Phi - KR.Phi_toe) / KR.B + KR.delta * KR.D,
                    KR.delta * (KR.D - KR.B) + np.sqrt(2 * KR.delta * np.maximum(Phi, 0)))


def simulate(Kp, qp, Q_of_t, years, burn=3.0, X0=None):
    """weekly salinity at all S_POS and head at S_HEAD; Q_of_t(t) [m3/d] per run (array)."""
    n = len(Kp); mu = Kp * KR.Phi_toe / (qp * KR.d)
    if X0 is None:
        X0 = np.array([KR.stable_root(m_, Q_of_t(0.0)[i] / (np.pi * qp[i] * KR.d)) for i, m_ in enumerate(mu)])
    X = X0.copy(); eps = KR.SIG_E * rng.standard_normal(n)
    dt = DT_W / SUB; nW = int(round(years / DT_W)); nB = int(round(burn / DT_W))
    Xw = np.zeros((nW, n)); Ew = np.zeros((nW, n)); Qw = np.zeros((nW, n)); tip = np.full(n, np.inf)
    t = -burn
    for w in range(nB + nW):
        accX = 0; accE = 0
        for _ in range(SUB):
            Q = Q_of_t(max(t, 0.0)); lam = Q / (np.pi * qp * KR.d)
            e1 = np.maximum(eps, -0.7); Xc = np.minimum(X, 0.995)
            drift = (mu / (1 + e1) - KR.F(Xc, lam / (1 + e1))) / KR.TAU
            X = np.where(np.isfinite(tip), 0.995, np.minimum(X + drift * dt, 0.995))
            eps = eps - eps / KR.THETA * dt + KR.SIG_E * np.sqrt(2 * dt / KR.THETA) * rng.standard_normal(n)
            t += dt
            new = (X >= 0.95) & ~np.isfinite(tip) & (t > 0); tip[new] = t
            accX = accX + X; accE = accE + eps
        if w >= nB:
            i = w - nB; Xw[i] = accX / SUB; Ew[i] = accE / SUB; Qw[i] = Q_of_t(max(t, 0.0))
    C = norm.cdf((Xw[:, :, None] * KR.d - KR.S_POS) / KR.W_MIX) + KR.SIG_C * rng.standard_normal((nW, n, len(KR.S_POS)))
    H = head_at(S_HEAD, qp * (1 + np.maximum(Ew, -0.7)), Qw, Kp) + SIG_H * rng.standard_normal((nW, n))
    return C, H, tip, Xw


def filt(u, k):
    """exponential filter z_t = sum_s exp(-k (t-s)) u_s dt over the whole record (warm start)."""
    a = np.exp(-k * DT_W); z = np.zeros_like(u); acc = np.zeros(u.shape[1:])
    for t in range(u.shape[0]):
        acc = a * acc + (1 - a) / k * u[t]; z[t] = acc
    return z


def to_toe(c, s):
    """toe position from base salinity through the inverse probit, with inverse-variance weights
    (samples near 0 or 1 carry almost no information about the toe)."""
    cc = np.clip(c, 0.005, 0.995)
    zq = norm.ppf(cc)
    x = s + KR.W_MIX * zq
    w = (norm.pdf(zq) / (KR.W_MIX * KR.SIG_C)) ** 2
    w = np.where((c > 0.02) & (c < 0.98), w, 0.0)
    return x, w


def wls_k(x, w, Z_list, kgrid, ends=None, WIN=None):
    """weighted least squares of the toe series x on [1, z_k^(1), ..., z_k^(m)], z = filtered inputs.
    If ends is None the whole record is used once; otherwise trailing windows of length WIN.
    Returns k_hat, the F statistic of the first input, and the summed weight."""
    def S(A):
        if ends is None:
            return A.sum(0)[None]
        cs = np.concatenate([np.zeros((1,) + A.shape[1:]), np.cumsum(A, 0)])
        return cs[ends] - cs[ends - WIN]
    m = len(Z_list) + 1
    best = None
    for k in kgrid:
        Z = [np.ones_like(x)] + [np.broadcast_to(filt(Zi, k).reshape(Zi.shape + (1,) * (x.ndim - Zi.ndim)), x.shape) for Zi in Z_list]
        A = np.stack([np.stack([S(w * Z[i] * Z[j]) for j in range(m)], -1) for i in range(m)], -2)
        b = np.stack([S(w * Z[i] * x) for i in range(m)], -1)
        sxx = S(w * x * x)
        A = A + 1e-9 * np.eye(m)
        coef = np.linalg.solve(A, b[..., None])[..., 0]
        rss = sxx - (coef * b).sum(-1)
        # model without the first input, for its F statistic
        idx = [0] + list(range(2, m))
        A0 = A[..., idx, :][..., :, idx]; b0 = b[..., idx]
        coef0 = np.linalg.solve(A0, b0[..., None])[..., 0]
        rss0 = sxx - (coef0 * b0).sum(-1)
        Fs = (rss0 - rss) / np.maximum(rss, 1e-12) * np.maximum(S(np.where(w > 0, 1.0, 0.0)) - m, 1)
        if best is None:
            best = rss.copy(); khat = np.full(rss.shape, k); Fst = Fs.copy()
        else:
            better = rss < best
            best = np.where(better, rss, best); khat = np.where(better, k, khat); Fst = np.where(better, Fs, Fst)
    return khat, Fst, S(w)


def passive_indicators(y):
    """lag-1 autocorrelation and variance of monthly means after linear detrending."""
    nT = y.shape[0] // 4 * 4
    m = y[:nT].reshape(nT // 4, 4, *y.shape[1:]).mean(1)
    tt = np.arange(m.shape[0]) - (m.shape[0] - 1) / 2
    tt = tt.reshape(-1, *([1] * (m.ndim - 1)))
    r = m - m.mean(0) - (m * tt).sum(0) / (tt ** 2).sum() * tt
    ar1 = (r[1:] * r[:-1]).sum(0) / ((r ** 2).sum(0) + 1e-30)
    return ar1, (r ** 2).mean(0)


def auc(pos, neg):
    """P(pos > neg) with ties counted as 1/2."""
    pos = np.asarray(pos)[:, None]; neg = np.asarray(neg)[None, :]
    return float(np.mean((pos > neg) + 0.5 * (pos == neg)))


if __name__ == '__main__':
    out = {}
    J_io, J_pas, J0 = criteria()
    out['S_POS'] = KR.S_POS.tolist(); out['J_io'] = J_io.tolist(); out['J_pas'] = J_pas.tolist(); out['J0'] = J0.tolist()
    s_star = float(KR.S_POS[J_io.argmax()]); s_stat = float(KR.S_POS[J0.argmax()])
    out['s_star'] = s_star; out['s_status'] = s_stat
    print(f'KRITIK-GO (IO) argmax {s_star:.0f} m; status argmax {s_stat:.0f} m; '
          f'max information on ln k: IO {J_io.max():.1f}, passive {J_pas.max():.2f} (ratio {J_io.max() / J_pas.max():.0f})')

    # ---------------- stationary validation: far (0.6 Qc) vs near (0.9 Qc)
    NT = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    Kp, qp = KR.draw_params(NT)
    mu = Kp * KR.Phi_toe / (qp * KR.d); lc = np.array([KR.lam_crit(m_) for m_ in mu]); Qc = lc * np.pi * qp * KR.d
    res = {}
    for name, f in [('far', 0.6), ('near', 0.85)]:
        C, H, tip, Xw = simulate(Kp, qp, lambda t, f=f: f * Qc + 0 * t, years=13.0)
        warm = int(round(3.0 / DT_W))
        u = H - H.mean(0)
        x, wgt = to_toe(C, KR.S_POS)
        x[:warm] = 0.0; wgt[:warm] = 0.0                      # warm-up of the input filter only
        khat, Fst, Sw = wls_k(x, wgt, [u], KGRID)
        khat, Fst, Sw = khat[0], Fst[0], Sw[0]
        ar1, var = passive_indicators(C[warm:])
        ktrue = np.array([KR.Fp(KR.stable_root(m_, f * l_), f * l_) / KR.TAU for m_, l_ in zip(mu, lc)])
        # oracle: the same estimators on the true toe series (perfect, unsaturated observation)
        xo = Xw * KR.d; wo = np.ones_like(xo); xo[:warm] = 0.0; wo[:warm] = 0.0
        ko = wls_k(xo, wo, [u], KGRID)[0][0]
        ar1o, _ = passive_indicators(Xw[warm:])
        res[name] = dict(khat=khat, F=Fst, Sw=Sw, ar1=ar1, var=var, tip=np.isfinite(tip), ktrue=ktrue, k_oracle=ko,
                         kpas=-12 * np.log(np.clip(ar1, 1e-3, 0.9999)), kpas_oracle=-12 * np.log(np.clip(ar1o, 1e-3, 0.9999)))
        print(f'{name}: true k median {np.median(ktrue):.3f}/yr; runs that tipped in the window {np.isfinite(tip).mean():.2f}')
    ok = ~res['near']['tip'] & ~res['far']['tip']
    rows = []
    for j, s in enumerate(KR.S_POS):
        a_io = auc(-res['near']['khat'][ok, j], -res['far']['khat'][ok, j])
        a_ar = auc(res['near']['ar1'][ok, j], res['far']['ar1'][ok, j])
        a_var = auc(res['near']['var'][ok, j], res['far']['var'][ok, j])
        kt = res['near']['ktrue'][ok]
        rel = np.median(np.abs(res['near']['khat'][ok, j] - kt) / kt)
        relp = np.median(np.abs(res['near']['kpas'][ok, j] - kt) / kt)
        rows.append(dict(s=float(s), auc_io=a_io, auc_ar1=a_ar, auc_var=a_var, relerr_near=float(rel), relerr_pas=float(relp)))
        print(f's={s:5.0f} m  J_io={J_io[j]:9.1f}  J_pas={J_pas[j]:6.2f}  AUC IO {a_io:.2f} | AR1 {a_ar:.2f} var {a_var:.2f} | '
              f'rel. error of k near: IO {rel:.2f}, passive {relp:.2f}')
    kt = res['near']['ktrue'][ok]
    out['oracle_io'] = float(np.median(np.abs(res['near']['k_oracle'][ok] - kt) / kt))
    out['oracle_pas'] = float(np.median(np.abs(res['near']['kpas_oracle'][ok] - kt) / kt))
    out['oracle_io_far'] = float(np.median(np.abs(res['far']['k_oracle'][ok] - res['far']['ktrue'][ok]) / res['far']['ktrue'][ok]))
    out['ktrue_near_median'] = float(np.median(kt)); out['ktrue_far_median'] = float(np.median(res['far']['ktrue'][ok]))
    out['tip_near'] = float(res['near']['tip'].mean())
    from scipy.stats import spearmanr
    out['spearman_Jio_acc'] = float(spearmanr(J_io, [-r['relerr_near'] for r in rows]).correlation)
    out['spearman_J0_acc'] = float(spearmanr(J0, [-r['relerr_near'] for r in rows]).correlation)
    print(f"oracle (true toe): IO {out['oracle_io']:.2f} (far {out['oracle_io_far']:.2f}), passive {out['oracle_pas']:.2f}; "
          f"Spearman(criterion, accuracy): KRITIK-GO {out['spearman_Jio_acc']:.2f}, status {out['spearman_J0_acc']:.2f}")
    out['stationary'] = rows; out['n_stationary'] = int(ok.sum())
    json.dump(out, open('kritik2_results.json', 'w'), indent=1)
    if len(sys.argv) < 3:
        sys.exit(0)

    # ---------------- ramp validation for three designs
    NR = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    designs = {'status': s_stat, 'kritik': s_star, 'well': 1900.0}
    jsel = [int(np.argmin(np.abs(KR.S_POS - v))) for v in designs.values()]
    Kr, qr = KR.draw_params(NR); K0r, q0r = KR.draw_params(NR)
    C1, H1, tip1, _ = simulate(Kr, qr, lambda t: KR.Qc0 * (0.5 + 0.8 * t / KR.YEARS) + 0 * Kr, years=KR.YEARS)
    C0, H0, tip0, _ = simulate(K0r, q0r, lambda t: 0.5 * KR.Qc0 + 0 * K0r, years=KR.YEARS)
    WIN = int(5 / DT_W); STEP = 26
    ends = np.arange(WIN, C1.shape[0] + 1, STEP)
    tW = np.arange(C1.shape[0]) * DT_W
    def scan(C, H, j, ramp):
        x, wgt = to_toe(C[:, :, j], KR.S_POS[j])
        u = H - H[:WIN].mean(0)
        qin = (0.8 * tW / KR.YEARS) if ramp else 0.0 * tW            # pumping change, known to the operator
        Zl = [u, np.broadcast_to(qin[:, None], u.shape).copy()] if ramp else [u]
        kh, Fs, Sw = wls_k(x, wgt, Zl, KGRID[::2], ends=ends, WIN=WIN)
        return kh, np.where(Sw > 0, Fs, 0.0)
    from scipy.stats import f as fdist
    Fcrit = fdist.ppf(0.999, 1, 50)
    tipw = np.where(np.isfinite(tip1), tip1 / DT_W, np.inf)
    ramp = {}
    for (name, s), j in zip(designs.items(), jsel):
        k0, F0 = scan(C0, H0, j, False); k1, F1 = scan(C1, H1, j, True)
        stat0 = np.where(F0 > Fcrit, k0, np.inf).min(0)            # lowest credible k_hat on each null run
        thr = np.quantile(stat0, 0.05)                              # 5 % false alarms
        hit = (F1 > Fcrit) & (k1 <= thr) & (ends[:, None] < tipw[None, :])
        first = np.where(hit.any(0), ends[np.argmax(hit, 0)], np.nan)
        lead = (tipw - first) * DT_W
        tipped = np.isfinite(tip1)
        p2 = float(np.mean(tipped & (lead >= 2)) / tipped.mean()); p1 = float(np.mean(tipped & (lead >= 1)) / tipped.mean())
        med = float(np.nanmedian(np.where(tipped, lead, np.nan)))
        ramp[name] = dict(s=s, thr=float(thr), p_lead2=p2, p_lead1=p1, median_lead=med, false_alarm=0.05)
        print(f'ramp, {name:7s} (s={s:.0f} m): k threshold {thr:.3f}/yr, P(lead>=2y)={p2:.2f}, P(lead>=1y)={p1:.2f}, median lead {med:.1f} y')
    out['ramp'] = ramp; out['ramp_tip_frac'] = float(np.isfinite(tip1).mean())
    json.dump(out, open('kritik2_results.json', 'w'), indent=1)
