"""E8. KAUZ-OED step 4: ADAPTIVE switchback pumping tests on the KAUZ-OED linear aquifer (Test 1 model),
analysed design-based with known propensities.

Aquifer (copied exactly from scratchpad/num/causal_ou.py, same seed). n = 30 cells along a transect, A =
diffusion + advection toward the coast (index 29) + damping, paleochannel coupling A[22,5] += 0.6,
A[5,22] += 0.2; noise covariance Q = diag(0.2 + 0.8 U), U from default_rng(2). Pumping well p = 8, zone
g = 27, steady causal response R_gp = -(A^{-1})_{gp} = 0.0564.
Dynamics dx = (A x + a u(t) e_p) dt + dW, Cov(dW) = Q dt, simulated EXACTLY with the OU transition over
piecewise-constant forcing: x_{t+D} = e^{AD} x_t + A^{-1}(e^{AD} - I) e_p a u + eta,
eta ~ N(0, C0 - e^{AD} C0 e^{A'D}), A C0 + C0 A' + Q = 0. x_0 ~ N(0, C0) (stationary, no pumping).

Switchback. Periods k = 1..K of length ell = b + w; U_k in {0, 1} (pump at amplitude a over the whole
period or not). A salinity logger in zone g records x_g every dl time units after the burn-in b; the outcome
is the period mean Y_k = (1/M) sum_{j=1..M} x_g(t_k + b + j dl), M = w / dl.
Lag-0 effect (derived from linearity): Y_k(u_{1:k}) = Y_k(0) + a sum_{j>=0} h_j u_{k-j}, so
    tau_k = Y_k(U_{1:k-1}, 1) - Y_k(U_{1:k-1}, 0) = a h_0 = tau_0,
    h_0 = (1/M) sum_j e_g' A^{-1}(e^{A s_j} - I) e_p,  s_j = b + j dl,
a deterministic constant, and tau_0 -> a R_gp as b grows (verified by branching simulation with common
random numbers on every period of every replication).

Adaptive assignment (operationally realistic). pi_k = P(U_k = 1 | F_{k-1}),
    q_k   = Phi((delta - est_{k-1}) / se_{k-1})                 Thompson-type: P(effect tolerable)
    z_k   = (Y_{k-1} - mean(Y_{1:k-1})) / sd(Y_{1:k-1})           standardised last salinity
    pi_k  = clip(expit(logit q_k - gamma z_k), pi_min, 1 - pi_min)
(est, se = running IPW estimate and its design-based s.e.; q_k = 1/2 for k <= k_warm), delta = tau_0
(truth exactly at the decision margin). Non-adaptive switchback: pi_k = 1/2.

Estimators of tau_bar_K = (1/K) sum_k tau_k (= tau_0 here):
  naive  difference in means pumped - unpumped, Welch interval (t quantile, Welch-Satterthwaite df)
  ARX    OLS of Y_k on (1, U_k, Y_{k-1}), classical OLS interval
  IPW    tau_hat_k = (Y_k - m_{k-1}) (U_k/pi_k - (1-U_k)/(1-pi_k)), m_{k-1} = forecast from a recursive
         ARX fit on data up to k-1 (regressors 1, Y_{k-1}, U_{k-1}, U_{k-2}, U_k), evaluated as
         Yhat(0) + (1 - pi_k) beta_U (the variance-minimising predictable baseline); Wald interval with the
         conservative design-based variance sum_k tau_hat_k^2 / K^2
  AW     sum h_k tau_hat_k / sum h_k, h_k = sqrt(pi_k (1 - pi_k)), self-normalised Wald with
         sqrt(sum h_k^2 tau_hat_k^2) / sum h_k
  CS     asymptotic confidence sequence for tau_bar_t from the martingale S_t = sum (tau_hat_k - tau_k):
         |S_t| <= sqrt((rho^2 V_t + 1)/rho^2 * 2 log(sqrt(rho^2 V_t + 1)/alpha)),  V_t = sum tau_hat_k^2
         (two-sided normal mixture; also the AW version with h_k weights)
Run: python3 sim_switchback_ou.py   (about 6 min on 1 core). Output: results/switchback_ou.json
"""
import time

import numpy as np
from scipy.linalg import solve_continuous_lyapunov, expm, cholesky
from scipy.stats import norm, t as tdist

from common import dump

ALPHA = 0.05
Z = norm.ppf(1 - ALPHA / 2)


# ---------------------------------------------------------------- aquifer (exact copy of causal_ou.py)
def build_model():
    rng = np.random.default_rng(2)
    n = 30
    A = np.zeros((n, n))
    for i in range(n):
        A[i, i] = -2.0 - 0.15
        if i > 0:
            A[i, i - 1] = 1.0 + 0.35
        if i < n - 1:
            A[i, i + 1] = 1.0 - 0.35
    A[22, 5] += 0.6
    A[5, 22] += 0.2
    Q = np.diag(0.2 + 0.8 * rng.random(n))
    C0 = solve_continuous_lyapunov(A, -Q)
    Ainv = np.linalg.inv(A)
    return dict(n=n, A=A, Q=Q, C0=C0, Ainv=Ainv, p=8, g=27, R=-Ainv[27, 8])


MOD = build_model()
NX, P, G = MOD['n'], MOD['p'], MOD['g']


def transition(D):
    """Exact OU transition over a step D with constant forcing u at well p (unit amplitude)."""
    A, C0, Ainv = MOD['A'], MOD['C0'], MOD['Ainv']
    E = expm(A * D)
    Gv = Ainv @ (E - np.eye(NX)) @ np.eye(NX)[:, P]
    S = C0 - E @ C0 @ E.T
    S = 0.5 * (S + S.T)
    L = cholesky(S + 1e-13 * np.eye(NX), lower=True)
    return E, Gv, L


def step_frac(t):
    """Fraction of the steady response reached at g, t after switching on unit forcing at p."""
    A, Ainv = MOD['A'], MOD['Ainv']
    t = np.atleast_1d(t)
    return np.array([-(Ainv @ (expm(A * s) - np.eye(NX)))[G, P] / Ainv[G, P] for s in t])


def tau0_analytic(b, w, dl, a):
    s = b + dl * np.arange(1, int(round(w / dl)) + 1)
    return a * MOD['R'] * step_frac(s).mean()


def carry_analytic(b, w, dl, a, J=6):
    """h_j (j = 0..J) times a: effect on Y_k of pumping in period k - j."""
    ell = b + w
    s = b + dl * np.arange(1, int(round(w / dl)) + 1)
    out = []
    for j in range(J + 1):
        if j == 0:
            out.append(a * MOD['R'] * step_frac(s).mean())
        else:  # pumping during [-(j) ell, -(j-1) ell] relative to period start
            out.append(a * MOD['R'] * (step_frac(s + j * ell) - step_frac(s + (j - 1) * ell)).mean())
    return np.array(out)


def mix_boundary(V, rho2):
    """Two-sided normal-mixture boundary for |S_t| at variance process V (Ville + Gaussian mixture)."""
    return np.sqrt((rho2 * V + 1) / rho2 * 2 * np.log(np.sqrt(rho2 * V + 1) / ALPHA))


# ---------------------------------------------------------------- one Monte Carlo experiment (vectorised over R)
def run(R=1000, K=400, b=30.0, w=20.0, dl=1.0, a=5.0, pi_min=0.1, gamma=1.0, adaptive=True, delta=None,
        seed=0, checkpoints=(25, 50, 100, 200, 400), t0=10, rho2=None, k_warm=10, branch=False,
        keep_path=False, keep_draws=True):
    rng = np.random.default_rng(seed)
    M = int(round(w / dl))
    tau0 = tau0_analytic(b, w, dl, a)
    if delta is None:
        delta = tau0
    Eb, Gb, Lb = transition(b) if b > 0 else (None, None, None)
    Ed, Gd, Ld = transition(dl)
    EbT = Eb.T if b > 0 else None
    EdT = Ed.T
    LbT = Lb.T if b > 0 else None
    LdT = Ld.T
    x = rng.standard_normal((R, NX)) @ cholesky(MOD['C0'], lower=True).T
    # histories
    Y = np.zeros((K, R)); U = np.zeros((K, R)); PI = np.zeros((K, R)); TH = np.zeros((K, R)); MB = np.zeros((K, R))
    Hh = np.zeros((K, R))
    # recursive ARX for the baseline: regressors (1, Y_{j-1}, U_{j-1}, U_{j-2}, U_j)
    lam = 1e-2
    XtX = np.repeat(lam * np.eye(5)[None], R, 0); Xty = np.zeros((R, 5))
    S_tau = np.zeros(R); S_tau2 = np.zeros(R); S_y = np.zeros(R); S_yy = np.zeros(R)
    branch_err = 0.0
    for k in range(K):
        # ---------------- assignment probability (F_{k-1}-measurable)
        if adaptive:
            if k < k_warm:
                q = np.full(R, 0.5)
            else:
                est = S_tau / k; se = np.sqrt(S_tau2) / k
                q = norm.cdf((delta - est) / se)
            q = np.clip(q, 1e-4, 1 - 1e-4)
            if k >= 3:
                mY = S_y / k; sY = np.sqrt(np.maximum(S_yy / k - mY ** 2, 1e-12))
                zl = (Y[k - 1] - mY) / sY
            else:
                zl = np.zeros(R)
            lg = np.log(q / (1 - q)) - gamma * zl
            pi = np.clip(1 / (1 + np.exp(-lg)), pi_min, 1 - pi_min)
        else:
            pi = np.full(R, 0.5)
        # ---------------- predictable baseline m_{k-1}
        if k < 12:
            m = S_y / k if k > 0 else np.zeros(R)
        else:
            beta = np.linalg.solve(XtX, Xty[..., None])[..., 0]
            u1 = U[k - 1]; u2 = U[k - 2]
            m = beta[:, 0] + beta[:, 1] * Y[k - 1] + beta[:, 2] * u1 + beta[:, 3] * u2 + (1 - pi) * beta[:, 4]
        # ---------------- draw U_k and run the period exactly
        u = (rng.random(R) < pi).astype(float)
        noise_b = rng.standard_normal((R, NX)) @ LbT if b > 0 else None
        noise_d = rng.standard_normal((M, R, NX)) @ LdT
        if branch:   # counterfactual period with the other treatment, same noise (common random numbers)
            yb = {}
            for uu in (0.0, 1.0):
                xx = x @ EbT + a * uu * Gb + noise_b if b > 0 else x.copy()
                acc = np.zeros(R)
                for j in range(M):
                    xx = xx @ EdT + a * uu * Gd + noise_d[j]
                    acc += xx[:, G]
                yb[uu] = acc / M
            branch_err = max(branch_err, float(np.max(np.abs(yb[1.0] - yb[0.0] - tau0))))
        if b > 0:
            x = x @ EbT + (a * u)[:, None] * Gb + noise_b
        acc = np.zeros(R)
        for j in range(M):
            x = x @ EdT + (a * u)[:, None] * Gd + noise_d[j]
            acc += x[:, G]
        y = acc / M
        # ---------------- IPW increment and book-keeping
        th = (y - m) * (u / pi - (1 - u) / (1 - pi))
        Y[k] = y; U[k] = u; PI[k] = pi; TH[k] = th; MB[k] = m; Hh[k] = np.sqrt(pi * (1 - pi))
        S_tau += th; S_tau2 += th ** 2; S_y += y; S_yy += y ** 2
        if k >= 2:
            xr = np.stack([np.ones(R), Y[k - 1], U[k - 1], U[k - 2], u], 1)
            XtX += xr[:, :, None] * xr[:, None, :]; Xty += xr * y[:, None]
    # ---------------- estimators at the checkpoints (fixed-K intervals)
    out = dict(tau0=tau0, delta=delta, aR=a * MOD['R'], K=K, R=R, b=b, w=w, dl=dl, a=a, pi_min=pi_min,
               gamma=gamma, adaptive=adaptive, branch_err=branch_err, fixed={})
    cum_th = np.cumsum(TH, 0); cum_th2 = np.cumsum(TH ** 2, 0)
    cum_h = np.cumsum(Hh, 0); cum_hth = np.cumsum(Hh * TH, 0); cum_h2th2 = np.cumsum(Hh ** 2 * TH ** 2, 0)
    for Kc in checkpoints:
        if Kc > K:
            continue
        y = Y[:Kc]; uu = U[:Kc]
        n1 = uu.sum(0); n0 = Kc - n1
        with np.errstate(divide='ignore', invalid='ignore'):
            m1 = (y * uu).sum(0) / n1; m0 = (y * (1 - uu)).sum(0) / n0
            v1 = ((y - m1) ** 2 * uu).sum(0) / (n1 - 1); v0 = ((y - m0) ** 2 * (1 - uu)).sum(0) / (n0 - 1)
            se_n = np.sqrt(v1 / n1 + v0 / n0)
            df = se_n ** 4 / ((v1 / n1) ** 2 / (n1 - 1) + (v0 / n0) ** 2 / (n0 - 1))
            naive = m1 - m0
            hw_n = tdist.ppf(1 - ALPHA / 2, df) * se_n
        ok = (n1 >= 2) & (n0 >= 2)
        cov_n = np.where(ok, np.abs(naive - tau0) <= hw_n, False)
        # ARX: Y_k on (1, U_k, Y_{k-1}), k = 2..Kc
        Xa = np.stack([np.ones((Kc - 1, R)), uu[1:], y[:-1]], 2).transpose(1, 0, 2)  # R x (Kc-1) x 3
        ya = y[1:].T
        XtXa = np.einsum('rki,rkj->rij', Xa, Xa); Xtya = np.einsum('rki,rk->ri', Xa, ya)
        ba = np.linalg.solve(XtXa, Xtya[..., None])[..., 0]
        res = ya - np.einsum('rki,ri->rk', Xa, ba)
        s2 = (res ** 2).sum(1) / (Kc - 1 - 3)
        se_a = np.sqrt(s2 * np.linalg.inv(XtXa)[:, 1, 1])
        hw_a = tdist.ppf(1 - ALPHA / 2, Kc - 4) * se_a
        arx = ba[:, 1]
        cov_a = np.abs(arx - tau0) <= hw_a
        # IPW and AW
        ipw = cum_th[Kc - 1] / Kc; se_i = np.sqrt(cum_th2[Kc - 1]) / Kc
        aw = cum_hth[Kc - 1] / cum_h[Kc - 1]; se_w = np.sqrt(cum_h2th2[Kc - 1]) / cum_h[Kc - 1]
        cov_i = np.abs(ipw - tau0) <= Z * se_i
        cov_w = np.abs(aw - tau0) <= Z * se_w
        # oracle variance check for IPW: design-based conditional variance is not observable; report the t-stat sd
        d = dict(
            naive=dict(cov=cov_n.mean(), mean=np.nanmean(naive), sd=np.nanstd(naive), hw=np.nanmedian(hw_n),
                       nan=float((~ok).mean())),
            arx=dict(cov=cov_a.mean(), mean=arx.mean(), sd=arx.std(), hw=np.median(hw_a)),
            ipw=dict(cov=cov_i.mean(), mean=ipw.mean(), sd=ipw.std(), hw=np.median(Z * se_i),
                     tsd=np.std((ipw - tau0) / se_i)),
            aw=dict(cov=cov_w.mean(), mean=aw.mean(), sd=aw.std(), hw=np.median(Z * se_w),
                    tsd=np.std((aw - tau0) / se_w)),
        )
        if keep_draws and Kc == K:
            for key, v in (('naive', naive), ('arx', arx), ('ipw', ipw), ('aw', aw)):
                d[key]['draws'] = v.astype(np.float32)
        out['fixed'][str(Kc)] = d
    # ---------------- peeking: Wald at every t, and the confidence sequences
    ts = np.arange(1, K + 1)[:, None]
    est_t = cum_th / ts; se_t = np.sqrt(cum_th2) / ts
    miss_wald = (np.abs(est_t - tau0) > Z * se_t)
    estw_t = cum_hth / cum_h; sew_t = np.sqrt(cum_h2th2) / cum_h
    miss_waldw = (np.abs(estw_t - tau0) > Z * sew_t)
    if rho2 is None:
        rho2 = 1.0
    bd = mix_boundary(cum_th2, rho2)
    miss_cs = np.abs(cum_th - ts * tau0) > bd
    rho2w = rho2 / (np.median(cum_h2th2[-1] / cum_th2[-1]))  # same tuning in the AW variance units
    bdw = mix_boundary(cum_h2th2, rho2w)
    miss_csw = np.abs(cum_hth - cum_h * tau0) > bdw
    mask = ts >= t0
    ever = {}
    for key, mm in (('wald', miss_wald), ('wald_aw', miss_waldw), ('cs', miss_cs), ('cs_aw', miss_csw)):
        mm = mm & mask
        ever[key] = np.maximum.accumulate(mm, 0).mean(1)
    out['ever'] = ever
    out['t0'] = t0; out['rho2'] = rho2; out['rho2w'] = rho2w
    hw_cs = bd / ts; hw_csw = bdw / cum_h
    out['cs_hw'] = dict(cs=np.median(hw_cs, 1), cs_q=np.quantile(hw_cs, [0.1, 0.25, 0.75, 0.9], 1),
                        cs_aw=np.median(hw_csw, 1), cs_aw_q=np.quantile(hw_csw, [0.1, 0.25, 0.75, 0.9], 1),
                        wald=np.median(Z * se_t, 1), wald_aw=np.median(Z * sew_t, 1),
                        cs_mean_K=hw_cs[-1].mean(), cs_se_K=hw_cs[-1].std() / np.sqrt(R),
                        cs_aw_mean_K=hw_csw[-1].mean(), cs_aw_se_K=hw_csw[-1].std() / np.sqrt(R),
                        wald_mean_K=(Z * se_t[-1]).mean(), wald_se_K=(Z * se_t[-1]).std() / np.sqrt(R))
    # ---------------- diagnostics: martingale-difference checks and design summaries
    D = TH - tau0
    out['diag'] = dict(
        mean_D=D.mean(), se_mean_D=D.mean(1).std() / np.sqrt(K),   # se across periods of the per-period mean
        corr_D_lag1=np.corrcoef(D[1:].ravel(), D[:-1].ravel())[0, 1],
        corr_D_pi=np.corrcoef(D[k_warm:].ravel(), PI[k_warm:].ravel())[0, 1],
        mean_pi=PI.mean(), sd_pi=PI.std(), frac_clip=np.mean((PI <= pi_min + 1e-12) | (PI >= 1 - pi_min - 1e-12)),
        mean_inv_pi=np.mean(1 / (PI * (1 - PI))),
        corrU_lag1=np.corrcoef(U[1:].ravel(), U[:-1].ravel())[0, 1],
        corrY_lag1=np.corrcoef(Y[1:].ravel(), Y[:-1].ravel())[0, 1],
        sdY=Y.std(), mean_th2=np.mean(TH ** 2), mean_th2_late=np.mean(TH[100:] ** 2),
        # does pi_k settle? correlation between the average pi over the first and second halves
        pi_half_corr=np.corrcoef(PI[:K // 2].mean(0), PI[K // 2:].mean(0))[0, 1],
        pi_var_across_reps=np.var(PI[K // 2:].mean(0)),
    )
    if keep_path:
        r0 = 0
        out['path'] = dict(Y=Y[:, r0], U=U[:, r0], PI=PI[:, r0], est=est_t[:, r0], se=se_t[:, r0],
                           cs=(bd / ts)[:, r0], m=MB[:, r0])
    return out


def pilot_rho2(seed=99, t_star=200, **kw):
    """Tuning constant of the mixture fixed before the experiment from a pilot run (different seed)."""
    pr = run(R=300, K=t_star, seed=seed, checkpoints=(), keep_draws=False, **kw)
    s2 = pr['diag']['mean_th2_late']
    c = -2 * np.log(ALPHA)
    return (c + np.log(c + 1)) / (t_star * s2), s2


def main():
    t_start = time.time()
    a = 5.0; w = 20.0; dl = 1.0; b_main = 30.0; K = 400
    ev = np.linalg.eigvals(MOD['A'])
    info = dict(n=NX, p=P, g=G, R_gp=MOD['R'], a=a, aR=a * MOD['R'], w=w, dl=dl, b_main=b_main,
                ell_main=b_main + w, K=K, slowest_eig=float(ev.real.max()), fastest_eig=float(ev.real.min()),
                max_imag=float(np.abs(ev.imag).max()), relax_time=float(-1 / ev.real.max()),
                C0gg=MOD['C0'][G, G], alpha=ALPHA)
    tgrid = np.linspace(0, 70, 141)
    info['step_t'] = tgrid; info['step_frac'] = step_frac(tgrid)
    bgrid = np.linspace(0, 60, 61)
    info['b_grid'] = bgrid
    info['tau0_b'] = np.array([tau0_analytic(bb, w, dl, a) for bb in bgrid])
    info['carry_main'] = carry_analytic(b_main, w, dl, a)
    info['carry_b10'] = carry_analytic(10.0, w, dl, a)
    print('slowest eigenvalue', info['slowest_eig'], 'R_gp', MOD['R'], 'tau0(main)', tau0_analytic(b_main, w, dl, a),
          'aR', a * MOD['R'], flush=True)
    rho2, s2p = pilot_rho2(b=b_main, w=w, dl=dl, a=a)
    info['rho2'] = rho2; info['pilot_s2'] = s2p
    print('rho2', rho2, 'pilot s2', s2p, f'{time.time() - t_start:.0f}s', flush=True)
    res = dict(info=info)
    common = dict(K=K, w=w, dl=dl, a=a, rho2=rho2)
    # main adaptive experiment (with branching check), and the non-adaptive switchback
    res['main'] = run(R=2000, b=b_main, seed=11, branch=True, keep_path=True, **common)
    print('main', f'{time.time() - t_start:.0f}s', flush=True)
    res['nonadaptive'] = run(R=2000, b=b_main, seed=12, adaptive=False, **common)
    print('non-adaptive', f'{time.time() - t_start:.0f}s', flush=True)
    # short burn-in operating point (carryover + adaptivity)
    res['short'] = run(R=2000, b=10.0, seed=13, branch=True, **common)
    res['short_na'] = run(R=2000, b=10.0, seed=14, adaptive=False, **common)
    print('short', f'{time.time() - t_start:.0f}s', flush=True)
    # sweep of the burn-in b (fixed averaging window w)
    res['b_sweep'] = {}
    for i, bb in enumerate((0.0, 5.0, 10.0, 15.0, 20.0, 30.0, 40.0)):
        r = run(R=1000, b=bb, seed=100 + i, branch=True, checkpoints=(K,), keep_draws=False, **common)
        res['b_sweep'][f'{bb:g}'] = dict(tau0=r['tau0'], branch_err=r['branch_err'],
                                         fixed=r['fixed'][str(K)], ever_cs=r['ever']['cs'][-1],
                                         diag=r['diag'])
        print('b', bb, f'{time.time() - t_start:.0f}s', flush=True)
    # sweep of pi_min (price of keeping pi bounded away from 0 and 1)
    res['pimin_sweep'] = {}
    for i, pm in enumerate((0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5)):
        r = run(R=1000, b=b_main, seed=200 + i, pi_min=pm, checkpoints=(K,), keep_draws=False, **common)
        res['pimin_sweep'][f'{pm:g}'] = dict(fixed=r['fixed'][str(K)], ever=dict((k, v[-1]) for k, v in r['ever'].items()),
                                             cs_hw=r['cs_hw'], diag=r['diag'])
        print('pi_min', pm, f'{time.time() - t_start:.0f}s', flush=True)
    res['runtime_s'] = time.time() - t_start
    dump(res, 'switchback_ou.json')
    print(f'done in {res["runtime_s"]:.0f}s')


if __name__ == '__main__':
    main()
