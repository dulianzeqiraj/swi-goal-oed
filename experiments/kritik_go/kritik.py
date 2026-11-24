"""KRITIK-GO: goal-oriented placement of salinity sensors for early warning of a seawater-intrusion
tipping point (critical slowing down), tested by Monte Carlo.

Physics: Strack (1976) single-potential solution for a confined coastal aquifer with one pumping
well at distance d from a straight coast. Along the coast-well axis the toe satisfies
    F(X; lam) = X + (lam/2) ln((1-X)/(1+X)) = mu,   X = x/d,
    mu = K Phi_toe / (q0 d),  Phi_toe = delta B^2 / 2,  lam = Q / (pi q0 d).
F has a maximum at X_m = sqrt(1-lam); the stable toe (X < X_m) and the unstable root merge when
F(X_m) = mu: a saddle-node at the critical pumping Q_c. The toe relaxes slowly,
    dX/dt = (mu_eff(t) - F(X; lam_eff(t))) / tau,   mu_eff = mu/(1+eps), lam_eff = lam/(1+eps),
with recharge anomalies eps(t) an Ornstein-Uhlenbeck process; the recovery rate
k = F'(X*)/tau -> 0 as Q -> Q_c (critical slowing down).

Sensors: salinity at the aquifer base at distance s from the coast, c = Phi_N((x_T - s)/w) + noise;
heads respond instantly to recharge and pumping (confined storage), and serve as a control.

Criteria for one sensor position s:
  status   : precision on the current toe position, a(s)^2 with a the probit slope (what an
             informative-now design such as the published EIG field rewards);
  KRITIK-GO: Whittle Fisher information on ln k at near-critical states (Q in [0.85, 0.97] Q_c),
             averaged over the parameter prior, with the statistical linearization of the probit.
Validation: 400 ramp runs (pumping 0.5 -> 1.3 Q_c nominal over 40 years, uncertain K and q0) and
400 null runs (constant pumping); early-warning alarm = trend (Spearman) of the rolling lag-1
autocorrelation, threshold set for a 5 % false-alarm rate on the null runs.
"""
import json, sys
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm, spearmanr

rng = np.random.default_rng(2026)
# ---------------------------------------------------------------- parameters (representative)
K0, B, delta, q00, d = 100.0, 30.0, 0.025, 1.5, 2000.0     # m/d, m, -, m2/d, m
D = 40.0                                                    # base depth below sea level [m]
Phi_toe = 0.5 * delta * B ** 2
TAU = 2.0                    # toe relaxation time at Q = 0 [yr]
SIG_E, THETA = 0.20, 0.5     # recharge anomaly sd and correlation time [yr]
W_MIX = 150.0                # mixing-zone width at the base [m]
SIG_C = 0.02                 # salinity sensor noise (seawater fraction)
SIG_H = 0.05                 # head sensor noise [m]
CV_K, CV_Q = 0.30, 0.20      # prior coefficient of variation of K and q0
YEARS, NSUB = 40, 30         # 40 years, 30 sub-steps per month
NR = int(sys.argv[1]) if len(sys.argv) > 1 else 400
S_POS = np.arange(400.0, 1950.0, 100.0)    # candidate salinity-sensor positions [m]
H_POS = np.array([1000.0, 1900.0])          # head sensors (control)


def F(X, lam):
    return X + 0.5 * lam * np.log((1 - X) / (1 + X))


def Fp(X, lam):
    return 1 - lam / (1 - X ** 2)


def lam_crit(mu):
    return brentq(lambda l: F(np.sqrt(1 - l), l) - mu, 1e-9, 1 - 1e-12)


def stable_root(mu, lam):
    Xm = np.sqrt(1 - lam)
    if F(Xm, lam) < mu:
        return np.nan
    return brentq(lambda X: F(X, lam) - mu, 1e-12, Xm)


mu0 = K0 * Phi_toe / (q00 * d)
lamc0 = lam_crit(mu0)
Qc0 = lamc0 * np.pi * q00 * d


def lognorm(mean, cv, n):
    s = np.sqrt(np.log(1 + cv ** 2))
    return mean * np.exp(s * rng.standard_normal(n) - 0.5 * s ** 2)


# ---------------------------------------------------------------- criteria
DT_M = 1.0 / 12.0
T_W = 10.0                                   # trailing record used by the warning [yr]
NW = int(T_W / DT_M)
OMEGA = 2 * np.pi * np.arange(1, NW // 2 + 1) / T_W


def linear_toe(mu, lam):
    """equilibrium, recovery rate, input gain and stationary sd of the toe (in X units)."""
    Xs = stable_root(mu, lam)
    k = Fp(Xs, lam) / TAU
    g = Xs / TAU                              # d(dX/dt)/d eps at equilibrium: -(F - X) - ... = -X*
    S_eps = 2 * SIG_E ** 2 * THETA / (1 + (OMEGA * THETA) ** 2)
    S_xi = g ** 2 * S_eps / (k ** 2 + OMEGA ** 2)
    var = g ** 2 * SIG_E ** 2 * THETA / (k * (1 + k * THETA))   # exact for an OU input into a first-order relaxation
    return Xs, k, S_xi, var


def whittle_info_lnk(s, Xs, k, S_xi, var):
    sd_eff = np.sqrt(W_MIX ** 2 + var * d ** 2)          # statistical linearization of the probit
    a = norm.pdf((Xs * d - s) / sd_eff) * d / sd_eff
    S_y = a ** 2 * S_xi + SIG_C ** 2 * DT_M
    dlnS = a ** 2 * (-2 * k * S_xi / (k ** 2 + OMEGA ** 2)) / S_y
    return 0.5 * np.sum(dlnS ** 2) * k ** 2


def criteria(n_prior=300):
    Kp, qp = lognorm(K0, CV_K, n_prior), lognorm(q00, CV_Q, n_prior)
    J = np.zeros(len(S_POS)); J0 = np.zeros(len(S_POS)); xm = []
    for Ki, qi in zip(Kp, qp):
        mu = Ki * Phi_toe / (qi * d)
        lam_now = 0.5 * lamc0 * q00 / qi
        if mu >= 0.95 or lam_now >= 0.8 * lam_crit(mu):       # same rejection as the Monte Carlo
            continue
        lc = lam_crit(mu); xm.append(np.sqrt(1 - lc) * d)
        for f in np.linspace(0.85, 0.97, 7):
            Xs, k, S_xi, var = linear_toe(mu, f * lc)
            J += np.array([whittle_info_lnk(s, Xs, k, S_xi, var) for s in S_POS])
        # status: precision on the toe position now (pumping at 0.5 Q_c nominal)
        Xs, k, S_xi, var = linear_toe(mu, lam_now)
        J0 += norm.pdf((Xs * d - S_POS) / W_MIX) ** 2
    return J / J.max(), J0 / J0.max(), np.array(xm)


# ---------------------------------------------------------------- Monte Carlo
def draw_params(n):
    """prior draws, rejecting those already beyond 80 % of their own critical pumping at the start."""
    Ks, qs = [], []
    while len(Ks) < n:
        Ki, qi = lognorm(K0, CV_K, 1)[0], lognorm(q00, CV_Q, 1)[0]
        mu = Ki * Phi_toe / (qi * d)
        if mu < 0.95 and 0.5 * lamc0 * q00 / qi < 0.8 * lam_crit(mu):
            Ks.append(Ki); qs.append(qi)
    return np.array(Ks), np.array(qs)


def simulate(ramp):
    Kp, qp = draw_params(NR)
    mu = Kp * Phi_toe / (qp * d)
    nM = YEARS * 12; dt = DT_M / NSUB
    Q_of_t = (lambda t: Qc0 * (0.5 + 0.8 * t / YEARS)) if ramp else (lambda t: 0.5 * Qc0 + 0 * t)
    lam0 = Q_of_t(0.0) / (np.pi * qp * d)
    X = np.array([stable_root(m, l) if np.isfinite(stable_root(m, l)) else 0.99 for m, l in zip(mu, lam0)])
    eps = SIG_E * rng.standard_normal(NR)
    Xm_ser = np.zeros((nM, NR)); eps_m = np.zeros((nM, NR)); Qm = np.zeros(nM)
    tip = np.full(NR, np.inf)
    t = 0.0
    for m in range(nM):
        for _ in range(NSUB):
            lam = Q_of_t(t) / (np.pi * qp * d)
            e1 = np.maximum(eps, -0.7)
            Xc = np.minimum(X, 0.995)
            drift = (mu / (1 + e1) - F(Xc, lam / (1 + e1))) / TAU
            X = np.where(np.isfinite(tip), 0.995, np.minimum(X + drift * dt, 0.995))
            eps = eps - eps / THETA * dt + SIG_E * np.sqrt(2 * dt / THETA) * rng.standard_normal(NR)
            t += dt
            newtip = (X >= 0.95) & ~np.isfinite(tip)
            tip[newtip] = t
        Xm_ser[m] = X; eps_m[m] = eps; Qm[m] = Q_of_t(t)
    # sensors
    xT = Xm_ser * d                                           # (nM, NR)
    C = norm.cdf((xT[:, :, None] - S_POS[None, None, :]) / W_MIX)
    C = C + SIG_C * rng.standard_normal(C.shape)
    q_t = qp[None, :] * (1 + np.maximum(eps_m, -0.7))
    Phi_s = (q_t[:, :, None] / Kp[None, :, None]) * H_POS + (Qm[:, None, None] / (2 * np.pi * Kp[None, :, None])) * \
        np.log(np.abs(H_POS - d) / (H_POS + d))
    Hd = np.where(Phi_s >= Phi_toe, (Phi_s - Phi_toe) / B + delta * D, delta * (D - B) + np.sqrt(2 * delta * np.maximum(Phi_s, 0)))
    Hd = Hd + SIG_H * rng.standard_normal(Hd.shape)
    return dict(C=C, H=Hd, tip=tip, mu=mu, xT=xT, K=Kp, q=qp)


WIN, LTR, EVAL = 60, 120, 6


def ar1_indicator(Y):
    """rolling lag-1 autocorrelation after linear detrending in each window; Y (nM, NR)."""
    from numpy.lib.stride_tricks import sliding_window_view
    V = sliding_window_view(Y, WIN, axis=0)                    # (nM-WIN+1, NR, WIN)
    tt = np.arange(WIN) - (WIN - 1) / 2
    beta = (V * tt).sum(-1, keepdims=True) / (tt ** 2).sum()
    R = V - V.mean(-1, keepdims=True) - beta * tt
    num = (R[..., 1:] * R[..., :-1]).sum(-1); den = (R ** 2).sum(-1) + 1e-30
    return num / den                                           # (nI, NR), index i ends at month i+WIN-1


def trend_stat(I):
    """trailing Spearman correlation of the indicator with time, every EVAL months."""
    from numpy.lib.stride_tricks import sliding_window_view
    V = sliding_window_view(I, LTR, axis=0)[::EVAL]            # (nE, NR, LTR)
    rk = V.argsort(-1).argsort(-1).astype(float)
    tr = np.arange(LTR, dtype=float)
    rk -= rk.mean(-1, keepdims=True); tr -= tr.mean()
    rho = (rk * tr).sum(-1) / np.sqrt((rk ** 2).sum(-1) * (tr ** 2).sum())
    end_month = np.arange(V.shape[0]) * EVAL + LTR - 1 + WIN - 1  # month index of the last data used
    return rho, end_month


def alarms(Y, thr, tip_month):
    rho, endm = trend_stat(ar1_indicator(Y))
    # only evaluations made before the tipping month count
    ok = endm[:, None] < tip_month[None, :]
    hit = (rho > thr) & ok
    first = np.where(hit.any(0), endm[np.argmax(hit, 0)], np.nan)
    return first, rho, endm


if __name__ == '__main__':
    print(f'nominal: mu={mu0:.3f}, Q_c={Qc0:.0f} m3/d, toe now (0.5 Qc) and critical toe x_m={np.sqrt(1 - lamc0) * d:.0f} m')
    J, J0, xm = criteria()
    print('critical toe x_m under the prior: median %.0f m, 10-90%% %.0f-%.0f m' % (np.median(xm), *np.percentile(xm, [10, 90])))
    print('KRITIK-GO argmax s = %.0f m; status argmax s = %.0f m' % (S_POS[J.argmax()], S_POS[J0.argmax()]))
    R1 = simulate(True); R0 = simulate(False)
    tipm1 = np.where(np.isfinite(R1['tip']), np.floor(R1['tip'] * 12), YEARS * 12 + 1)
    tipm0 = np.full(NR, YEARS * 12 + 1.0)
    print(f'tipping in ramp runs: {np.isfinite(R1["tip"]).mean():.2f} of runs, median year {np.nanmedian(np.where(np.isfinite(R1["tip"]), R1["tip"], np.nan)):.1f}')
    res = {'S_POS': S_POS.tolist(), 'J': J.tolist(), 'J0': J0.tolist(), 'xm_med': float(np.median(xm)),
           'xm_p10': float(np.percentile(xm, 10)), 'xm_p90': float(np.percentile(xm, 90)), 'Qc0': float(Qc0),
           'sal': [], 'head': [], 'level': []}
    for j, s in enumerate(S_POS):
        rho0, _ = trend_stat(ar1_indicator(R0['C'][:, :, j]))
        thr = np.quantile(rho0.max(0), 0.95)
        first, _, _ = alarms(R1['C'][:, :, j], thr, tipm1)
        lead = (tipm1 - first) / 12.0
        tipped = np.isfinite(R1['tip'])
        p2 = np.mean(tipped & (lead >= 2)) / tipped.mean()
        p1 = np.mean(tipped & (lead >= 1)) / tipped.mean()
        med = np.nanmedian(np.where(tipped, lead, np.nan))
        # level alarm: 12-month mean salinity above 0.5 (no threshold calibration)
        Cm1 = np.array([R1['C'][max(0, m - 11):m + 1, :, j].mean(0) for m in range(YEARS * 12)])
        Cm0 = np.array([R0['C'][max(0, m - 11):m + 1, :, j].mean(0) for m in range(YEARS * 12)])
        fl = np.where((Cm1 > 0.5).any(0), np.argmax(Cm1 > 0.5, 0), np.nan)
        lead_l = (tipm1 - fl) / 12.0
        fa_l = np.mean((Cm0 > 0.5).any(0))
        res['sal'].append({'s': float(s), 'thr': float(thr), 'p_lead2': float(p2), 'p_lead1': float(p1), 'median_lead': float(med)})
        res['level'].append({'s': float(s), 'p_lead2': float(np.mean(tipped & (lead_l >= 2)) / tipped.mean()),
                             'false_alarm_null': float(fa_l), 'median_lead': float(np.nanmedian(np.where(tipped, lead_l, np.nan)))})
        print(f's={s:5.0f} m  J={J[j]:.2f} J0={J0[j]:.2f}  EWS: P(lead>=2y)={p2:.2f} P(lead>=1y)={p1:.2f} median lead {med:5.1f} y | '
              f'level: P(lead>=2y)={res["level"][-1]["p_lead2"]:.2f}, false alarm on null {fa_l:.2f}')
    for j, s in enumerate(H_POS):
        rho0, _ = trend_stat(ar1_indicator(R0['H'][:, :, j]))
        thr = np.quantile(rho0.max(0), 0.95)
        first, _, _ = alarms(R1['H'][:, :, j], thr, tipm1)
        lead = (tipm1 - first) / 12.0
        tipped = np.isfinite(R1['tip'])
        p2 = np.mean(tipped & (lead >= 2)) / tipped.mean()
        res['head'].append({'s': float(s), 'p_lead2': float(p2)})
        print(f'head sensor at {s:.0f} m: P(lead>=2y)={p2:.2f}')
    rs = spearmanr(J, [r['p_lead2'] for r in res['sal']]).correlation
    rs0 = spearmanr(J0, [r['p_lead2'] for r in res['sal']]).correlation
    res['spearman_J'] = float(rs); res['spearman_J0'] = float(rs0)
    res['tip_frac'] = float(np.isfinite(R1['tip']).mean())
    res['tip_median_year'] = float(np.nanmedian(np.where(np.isfinite(R1['tip']), R1['tip'], np.nan)))
    print(f'Spearman(criterion, P(lead>=2y)): KRITIK-GO {rs:.2f}, status {rs0:.2f}')
    json.dump(res, open('kritik_results.json', 'w'), indent=1)
    np.savez('kritik_runs.npz', xT=R1['xT'][:, :50], tip=R1['tip'], S_POS=S_POS)
