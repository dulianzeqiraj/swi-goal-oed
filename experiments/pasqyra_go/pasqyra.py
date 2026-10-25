"""PASQYRA-GO (pasqyra: the mirror). Innovation of review 51 (deep reinforcement learning at the frontier).

A deep pumping agent is to be trained offline on the utility's logs: monthly coastal head and sentinel chloride y_t, and
the pumping q_t that the operators chose. The operators also knew something that was never recorded: complaints from
private wells near the toe, a noisy reading s_t of the toe X_t. They cut pumping when the toe was advanced.

Aquifer (review 50, DRITARJA-GO), state z = (m, h, X, c):
    m' = 0.7 m + 0.5 w_m;  h' = 0.85 h + 0.3 m - 0.3 q + 0.1 w_h;  X' = 0.9 X - 0.5 h + 0.1 c + 0.1 w_X;
    c' = 0.995 c + 0.02 X + 0.02 w_c;  y = (h + 0.05 v_h, X + 0.5 c + 0.3 v_Cl);  private s = X + sd_s nu.
Cost per month (X + 0.5 c)^2 + 0.5 q^2: salinity in the capture zone of the supply wells, which the logs record
(through y_Cl), plus pumping deficit. Operator: q = -K E[z | y, s, past q] + e (e unrecorded, sd_e) + d (d a recorded
dither, sd_d; zero unless stated).

Proposition P (section 9 of the review):
 (i)  If the operators used only recorded information (plus independent noise), the observational predictor of y_{t+1}
      from the logged past (y, q) is the interventional one, for every policy, and offline learning is consistent.
 (ii) Mirror bias: with private information, the coefficient of q_t in the regression of y_{t+1} on the logged past is
      C B - C A P_D K^T / (K P_D K^T + sd_e^2), P_D = Cov(E[z|operator info] - E[z|logs]).
 (iii) Observational equivalence: an aquifer' (the observational model) with operators' who use only the logs generates
      exactly the same law of the logs; the two worlds disagree about what pumping does. No method that uses the logs
      alone can be consistent in both.
 (iv) Instrument: a recorded dither d independent of everything else identifies the aquifer from the moments
      E[eps_theta(t+1) d_(t-j)] = 0, eps_theta the prediction error of the model with pumping as forcing.
Part A (this file, exact, infinite logs): Lyapunov and Riccati computations. Writes pasqyra_results.json, pasqyra.log.
"""
import json
import os

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np
from scipy.linalg import solve_discrete_are, solve_discrete_lyapunov
from scipy.optimize import minimize, least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
A0 = np.array([[0.7, 0, 0, 0], [0.3, 0.85, 0, 0], [0, -0.5, 0.9, 0.1], [0, 0, 0.02, 0.995]])
B0 = np.array([[0.0], [-0.3], [0.0], [0.0]])
W = np.diag([0.5, 0.1, 0.1, 0.02]) ** 2
KAPPA = 0.5
C = np.array([[0, 1.0, 0, 0], [0, 0, 1.0, KAPPA]])
V = np.diag([0.05, 0.3]) ** 2
CS = np.array([[0, 0, 1.0, 0]])                         # private reading of the toe
CCL = np.array([[0, 0, 1.0, KAPPA]])                    # salinity of the supply wells' capture zone
Q = CCL.T @ CCL
R = np.array([[0.5]])
NX, NY = 4, 2
THETA0 = np.array([0.3, 0.5, 0.9, 0.1])                  # calibrated parameters: beta_q, a_Xh, a_XX, a_Xc
TH_NAMES = ['pumping -> head (0.3)', 'head -> toe (0.5)', 'toe retention (0.9)', 'clay -> toe (0.1)']
BASE = dict(sd_s=0.1, sd_e=0.1)


def model(theta, kind='phys4'):
    """World-model classes of increasing flexibility, all with pumping as a forcing (input):
    phys4: 4 uncertain physical parameters (pumping->head, head->toe, toe retention, clay->toe);
    phys8: also head retention, recharge->head, toe->clay exchange, clay retention;
    free:  every entry of A (16) and B (4) free, C and the noise covariances known (a black-box 4-state model)."""
    A = A0.copy(); B = B0.copy()
    if kind == 'free':
        return theta[:16].reshape(4, 4).copy(), theta[16:20].reshape(4, 1).copy()
    B[1, 0] = -theta[0]; A[2, 1] = -theta[1]; A[2, 2] = theta[2]; A[2, 3] = theta[3]
    if kind == 'phys8':
        A[1, 1] = theta[4]; A[1, 0] = theta[5]; A[3, 2] = theta[6]; A[3, 3] = theta[7]
    return A, B


def theta_true(kind):
    if kind == 'phys4':
        return THETA0.copy()
    if kind == 'phys8':
        return np.concatenate([THETA0, [0.85, 0.3, 0.02, 0.995]])
    return np.concatenate([A0.ravel(), B0.ravel()])


def lq_gain(A, B):
    P = solve_discrete_are(A, B, Q, R)
    return np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A), P


def kf(A, Cm, Vm):
    S = solve_discrete_are(A.T, Cm.T, W, Vm)
    M = S @ Cm.T @ np.linalg.inv(Cm @ S @ Cm.T + Vm)
    return S, M


def lqg_controller(A, B):
    """Records-only LQG controller for the model (A, B): xi' = F xi + G y, q = Hc xi + Dc y."""
    K, P = lq_gain(A, B)
    S, M = kf(A, C, V)
    ABK = A - B @ K
    return dict(F=ABK @ (np.eye(NX) - M @ C), G=ABK @ M, Hc=-K @ (np.eye(NX) - M @ C), Dc=-K @ M, K=K, P=P, S=S, M=M, A=A, B=B)


def cost(Ac, Bc, Cc, Dc, A=A0, B=B0):
    """Average true cost of the aquifer (A, B) under the LTI controller xi' = Ac xi + Bc y, q = Cc xi + Dc y."""
    k = Ac.shape[0]
    Acl = np.block([[A + B @ Dc @ C, B @ Cc], [Bc @ C, Ac]])
    if np.max(np.abs(np.linalg.eigvals(Acl))) >= 1 - 1e-10:
        return float('inf')
    Gn = np.block([[np.eye(NX), B @ Dc], [np.zeros((k, NX)), Bc]])
    Nz = np.block([[W, np.zeros((NX, NY))], [np.zeros((NY, NX)), V]])
    Sig = solve_discrete_lyapunov(Acl, Gn @ Nz @ Gn.T)
    Lu = np.hstack([Dc @ C, Cc])
    return float(np.trace(Q @ Sig[:NX, :NX]) + np.trace(R @ (Lu @ Sig @ Lu.T + Dc @ V @ Dc.T)))


def J_of(ctrl, A=A0, B=B0):
    return cost(ctrl['F'], ctrl['G'], ctrl['Hc'], ctrl['Dc'], A, B)


# ------------------------------------------------------------------ the logged world: aquifer + operators
class Logged:
    """Joint linear system of the aquifer and the operators. State xi = (z, p), p = operators' prior estimate of z.
    Noise n = (w (4), v (2), nu (1), e (1), d (1)), independent, covariance N."""

    def __init__(self, sd_s, sd_e, sd_d=0.0, gamma=1.0):
        self.sd_s, self.sd_e, self.sd_d, self.gamma = sd_s, sd_e, sd_d, gamma
        K, _ = lq_gain(A0, B0)
        K = gamma * K
        self.K = K
        if np.isfinite(sd_s):
            Ct = np.vstack([C, CS]); Vt = np.diag([0.05 ** 2, 0.3 ** 2, sd_s ** 2])
        else:
            Ct = C; Vt = V
        S, M = kf(A0, Ct, Vt)
        m = Ct.shape[0]
        nn = 4 + 2 + 1 + 1 + 1
        self.nn = nn
        self.N = np.diag(np.concatenate([np.diag(W), np.diag(V), [sd_s ** 2 if np.isfinite(sd_s) else 0.0, sd_e ** 2, sd_d ** 2]]))
        Pv = np.zeros((m, nn)); Pv[:2, 4:6] = np.eye(2)                  # operators' measurement noise
        if m == 3:
            Pv[2, 6] = 1.0
        Ez = np.hstack([M @ Ct, np.eye(NX) - M @ Ct])                  # z_hat(t|t) = Ez xi + Ev n
        Ev = M @ Pv
        Pe = np.zeros((1, nn)); Pe[0, 7] = 1.0
        Pd = np.zeros((1, nn)); Pd[0, 8] = 1.0
        Pw = np.zeros((NX, nn)); Pw[:, :4] = np.eye(4)
        Pyv = np.zeros((NY, nn)); Pyv[:, 4:6] = np.eye(2)
        self.Hq = -K @ Ez; self.Jq = -K @ Ev + Pe + Pd                   # q = Hq xi + Jq n
        self.Hz = np.hstack([np.eye(NX), np.zeros((NX, NX))]); self.Jz = np.zeros((NX, nn))
        self.Hy = C @ self.Hz; self.Jy = Pyv
        self.Hd = np.zeros((1, 2 * NX)); self.Jd = Pd
        self.Hzh = Ez; self.Jzh = Ev                                     # operators' filtered estimate
        Phi = np.zeros((2 * NX, 2 * NX)); Gam = np.zeros((2 * NX, nn))
        Phi[:NX] = A0 @ self.Hz + B0 @ self.Hq; Gam[:NX] = B0 @ self.Jq + Pw
        Phi[NX:] = (A0 - B0 @ K) @ Ez; Gam[NX:] = (A0 - B0 @ K) @ Ev + B0 @ (Pe + Pd)
        self.Phi, self.Gam = Phi, Gam
        self.Sig = solve_discrete_lyapunov(Phi, Gam @ self.N @ Gam.T)
        self.J = float(np.trace(Q @ self.Sig[:NX, :NX]) + np.trace(R @ (self.Hq @ self.Sig @ self.Hq.T + self.Jq @ self.N @ self.Jq.T)))

    def cov(self, a, b, k):
        """Cov(a_{t+k}, b_t) for a = (Ha, Ja), b = (Hb, Jb), k >= 0."""
        Ha, Ja = a; Hb, Jb = b
        out = Ha @ np.linalg.matrix_power(self.Phi, k) @ self.Sig @ Hb.T
        if k == 0:
            out = out + Ja @ self.N @ Jb.T
        else:
            out = out + Ha @ np.linalg.matrix_power(self.Phi, k - 1) @ self.Gam @ self.N @ Jb.T
        return out

    def lagged(self, which, lag):
        """Signal x_{t-lag} for which in {'y','q','z','d','zh'}: expressed through (Phi, Gam) at time t-lag."""
        return dict(y=(self.Hy, self.Jy), q=(self.Hq, self.Jq), z=(self.Hz, self.Jz), d=(self.Hd, self.Jd), zh=(self.Hzh, self.Jzh))[which], lag

    def cross(self, items_a, items_b):
        """Covariance matrix between stacked lagged signals (lists of (which, lag))."""
        rows = []
        for wa, la in items_a:
            row = []
            for wb, lb in items_b:
                a, _ = self.lagged(wa, la); b, _ = self.lagged(wb, lb)
                k = lb - la                       # a at t-la, b at t-lb: Cov(a_{s+k}, b_s) with k = lb - la
                row.append(self.cov(a, b, k) if k >= 0 else self.cov(b, a, -k).T)
            rows.append(np.hstack(row))
        return np.vstack(rows)


def regress(L, target, regs):
    Sxx = L.cross(regs, regs); Syx = L.cross([target], regs)
    coef = np.linalg.solve(Sxx, Syx.T).T
    resid = L.cross([target], [target]) - coef @ Syx.T
    return coef, resid


def window_regs(p, include_q0):
    regs = [('y', k) for k in range(p)] + [('q', k) for k in range(0 if include_q0 else 1, p + (0 if include_q0 else 1))]
    return regs


# ------------------------------------------------------------------ controllers from window rules
def window_controller(b, a):
    """q_t = sum_{k=0}^{ny-1} b_k y_{t-k} + sum_{k=1}^{nu} a_k q_{t-k}; b list of (1, NY), a list of scalars."""
    ny, nu = len(b), len(a)
    k = (ny - 1) * NY + nu
    if k == 0:
        return np.zeros((1, 1)), np.zeros((1, NY)), np.zeros((1, 1)), b[0]
    Cc = np.hstack([np.hstack(b[1:]) if ny > 1 else np.zeros((1, 0)), np.array(a).reshape(1, -1)])
    Dc = b[0]
    Ac = np.zeros((k, k)); Bc = np.zeros((k, NY))
    ky = (ny - 1) * NY
    if ky:
        Bc[:NY] = np.eye(NY)
        Ac[NY:ky, :ky - NY] = np.eye(ky - NY)
    if nu:
        Ac[ky, :] = Cc[0]; Bc[ky, :] = Dc[0]
        Ac[ky + 1:, ky:k - 1] = np.eye(nu - 1)
    return Ac, Bc, Cc, Dc


def bc_rule(L, p, with_q):
    """Behaviour clone: best linear predictor of the operators' q_t from the logged window. Observation window: y_t..y_{t-p+1};
    ARX window: y_t..y_{t-p} and q_{t-1}..q_{t-p} (the window that is exact for an order-p controller, review 50)."""
    ny = p + 1 if with_q else p
    regs = [('y', k) for k in range(ny)] + ([('q', k) for k in range(1, p + 1)] if with_q else [])
    coef, res = regress(L, ('q', 0), regs)
    b = [coef[:, NY * k:NY * k + NY] for k in range(ny)]
    a = [float(coef[0, NY * ny + k]) for k in range(p)] if with_q else []
    return b, a, float(res[0, 0])


# ------------------------------------------------------------------ black-box world models learned from the logs
def arx_model_agent(L, p):
    """Fit y_{t+1} = sum_{k<p} alpha_k y_{t-k} + sum_{k<p} beta_k q_{t-k} + eps on the logs (population least squares),
    then the optimal rule for that model (cost y_Cl^2 + R q^2), a window rule. Returns (b, a, believed cost)."""
    regs = [('y', k) for k in range(1, p + 1)] + [('q', k) for k in range(1, p + 1)]
    coef, Se = regress(L, ('y', 0), regs)                       # y_t on y_{t-1..t-p}, q_{t-1..t-p}
    al = [coef[:, NY * k:NY * k + NY] for k in range(p)]           # alpha_k multiplies y_{t-1-k}
    be = [coef[:, NY * p + k:NY * p + k + 1] for k in range(p)]    # beta_k multiplies q_{t-1-k}
    # decision state chi_t = (y_t..y_{t-p+1}, q_{t-1}..q_{t-p+1}); y_{t+1} = sum al_k y_{t-k} + be_0 q_t + sum_{k>=1} be_k q_{t-k}
    ny, nu = p * NY, p - 1
    n = ny + nu
    Am = np.zeros((n, n)); Bm = np.zeros((n, 1)); Em = np.zeros((n, NY))
    for k in range(p):
        Am[:NY, NY * k:NY * k + NY] = al[k]
    for k in range(1, p):
        Am[:NY, ny + k - 1:ny + k] = be[k]
    Bm[:NY] = be[0]; Em[:NY] = np.eye(NY)
    if p > 1:
        Am[NY:ny, :ny - NY] = np.eye(ny - NY)
        Bm[ny, 0] = 1.0
        if nu > 1:
            Am[ny + 1:, ny:n - 1] = np.eye(nu - 1)
    Qm = np.zeros((n, n)); Qm[1, 1] = 1.0                          # y_Cl,t
    try:
        P = solve_discrete_are(Am, Bm, Qm, R)
    except Exception:
        return None
    Lg = np.linalg.solve(R + Bm.T @ P @ Bm, Bm.T @ P @ Am)
    believed = float(np.trace(P @ Em @ Se @ Em.T))
    b = [-Lg[:, NY * k:NY * k + NY] for k in range(p)]
    a = [float(-Lg[0, ny + k]) for k in range(nu)]
    return b, a, believed


def prime_agent(Wp):
    """Optimal rule of the infinite-capacity world model (aquifer'), deployed with its own filter of the logs."""
    Phi, Ky, Kq, Hy, Hq = Wp['Phi'], Wp['Ky'], Wp['Kq'], Wp['Hy'], Wp['Hq']
    Ab = Phi - Kq @ Hq
    n = Ab.shape[0]
    # decision state chi = (x, eps_y); x' = Ab x + Ky eps + Kq q; eps' new noise; cost (Hy x + eps)_Cl^2 + R q^2
    Am = np.block([[Ab, Ky], [np.zeros((NY, n)), np.zeros((NY, NY))]])
    Bm = np.vstack([Kq, np.zeros((NY, 1))])
    c2 = np.hstack([Hy[1:2], np.array([[0.0, 1.0]])])
    Qm = c2.T @ c2
    P = solve_discrete_are(Am, Bm, Qm, R)
    Lg = np.linalg.solve(R + Bm.T @ P @ Bm, Bm.T @ P @ Am)
    Ex = np.vstack([np.zeros((n, NY)), np.eye(NY)])
    believed = float(np.trace(P @ Ex @ Wp['Ree'] @ Ex.T))
    Lx, Le = Lg[:, :n], Lg[:, n:]
    # controller: state x_hat; q = -Lx x - Le (y - Hy x); x' = Ab x + Ky (y - Hy x) + Kq q
    Cc = -Lx + Le @ Hy; Dc = -Le
    Ac = Ab - Ky @ Hy + Kq @ Cc; Bc = Ky + Kq @ Dc
    return (Ac, Bc, Cc, Dc), believed


# ------------------------------------------------------------------ calibration with pumping as forcing
def predictor_matrices(theta, kind='phys4'):
    A, B = model(theta, kind)
    S, M = kf(A, C, V)
    Kp = A @ M                                                    # x_{t+1} = A x + B q + Kp (y - C x)
    return A, B, Kp, C @ S @ C.T + V


def innovation_cov_and_dcross(L, theta, m_lags=0, kind='phys4'):
    """Run the model's Kalman predictor (pumping as forcing) on the logged world. Returns the stationary covariance of
    its prediction errors eps_t = y_t - C x_t and, if m_lags > 0, the cross-moments E[eps_{t+1+j}... d_t]."""
    try:
        A, B, Kp, Sth = predictor_matrices(theta, kind)
    except Exception:
        return None, None, None
    n1 = 2 * NX
    # augmented state (xi, x): x' = (A - Kp C) x + B q + Kp y
    Phi = np.zeros((n1 + NX, n1 + NX)); Gam = np.zeros((n1 + NX, L.nn))
    Phi[:n1, :n1] = L.Phi; Gam[:n1] = L.Gam
    Phi[n1:, :n1] = B @ L.Hq + Kp @ L.Hy
    Phi[n1:, n1:] = A - Kp @ C
    Gam[n1:] = B @ L.Jq + Kp @ L.Jy
    if np.max(np.abs(np.linalg.eigvals(Phi))) >= 1:
        return None, None, Sth
    Sg = solve_discrete_lyapunov(Phi, Gam @ L.N @ Gam.T)
    He = np.hstack([L.Hy, -C]); Je = L.Jy                          # eps_t = y_t - C x_t
    Se = He @ Sg @ He.T + Je @ L.N @ Je.T
    dmom = None
    if m_lags:
        # E[eps_{t+k} d_t] = He Phi^{k-1} Gam N Jd^T for k >= 1 (eps_t does not contain d_t: y_t is recorded before q_t)
        G1 = Gam @ L.N @ L.Jd.T
        out, Pk = [], np.eye(Phi.shape[0])
        for k in range(1, m_lags + 1):
            out.append((He @ Pk @ G1).ravel()); Pk = Phi @ Pk
        dmom = np.concatenate(out)
    return Se, dmom, Sth


def nll(theta, L, kind='phys4'):
    Se, _, Sth = innovation_cov_and_dcross(L, theta, kind=kind)
    if Se is None:
        return 1e6
    sign, ld = np.linalg.slogdet(Sth)
    return 0.5 * ld + 0.5 * np.trace(np.linalg.solve(Sth, Se))


def calibrate_ml(L, kind='phys4', start=None):
    start = theta_true(kind) if start is None else start
    f = lambda th: nll(th, L, kind)
    if kind != 'free':
        r = minimize(f, start, method='Nelder-Mead', options=dict(xatol=1e-10, fatol=1e-14, maxiter=40000, maxfev=80000))
        start = r.x
    r = minimize(f, start, method='BFGS', options=dict(gtol=1e-11, maxiter=5000))
    return r.x, float(r.fun)


def calibrate_iv(L, m_lags=24, kind='phys4', start=None):
    start = theta_true(kind) * 0.8 if start is None else start
    def res(th):
        _, dm, _ = innovation_cov_and_dcross(L, th, m_lags, kind)
        return dm / L.sd_d ** 2 if dm is not None else np.full(NY * m_lags, 1e3)
    r = least_squares(res, start, xtol=1e-15, ftol=1e-15, gtol=1e-15)
    return r.x, float(np.max(np.abs(r.fun)))


def calibrate_ivml(L, m_lags=24, kind='free', mu=1e4):
    """Likelihood with pumping as forcing, penalised by the dither moments: the moments pin what the logs confound
    (the response to pumping), the likelihood fills in the rest (modes that pumping does not excite)."""
    th0, _ = calibrate_iv(L, m_lags, kind)
    def f(th):
        Se, dm, Sth = innovation_cov_and_dcross(L, th, m_lags, kind)
        if Se is None:
            return 1e6
        return 0.5 * np.linalg.slogdet(Sth)[1] + 0.5 * np.trace(np.linalg.solve(Sth, Se)) + mu * np.sum((dm / L.sd_d ** 2) ** 2)
    r = minimize(f, th0, method='BFGS', options=dict(gtol=1e-10, maxiter=4000))
    return r.x


# ------------------------------------------------------------------ observational equivalence
def world_prime(L):
    """Innovations form of the logs r = (y, q) of the logged world; aquifer' and operators' that reproduce them."""
    Hr = np.vstack([L.Hy, L.Hq]); Jr = np.vstack([L.Jy, L.Jq])
    Qn = L.Gam @ L.N @ L.Gam.T; Rn = Jr @ L.N @ Jr.T; Sn = L.Gam @ L.N @ Jr.T
    P = solve_discrete_are(L.Phi.T, Hr.T, Qn, Rn, s=Sn)
    Re = Hr @ P @ Hr.T + Rn
    Kr = (L.Phi @ P @ Hr.T + Sn) @ np.linalg.inv(Re)
    Ky, Kq = Kr[:, :NY], Kr[:, NY:]
    Hy, Hq = Hr[:NY], Hr[NY:]
    # q innovation regressed on y innovation (y_t is logged before q_t)
    Lyq = Re[NY:, :NY] @ np.linalg.inv(Re[:NY, :NY])
    s_eta = (Re[NY:, NY:] - Lyq @ Re[:NY, NY:]).item()
    return dict(Phi=L.Phi, Ky=Ky, Kq=Kq, Hy=Hy, Hq=Hq, Ree=Re[:NY, :NY], Lyq=Lyq, s_eta=s_eta, Re=Re)


def world_prime_autocov(Wp, kmax):
    """Autocovariances of (y, q) generated by aquifer' (state xh, input q, noise eps_y) driven by operators' (records only)."""
    Phi, Ky, Kq, Hy, Hq, Lyq = Wp['Phi'], Wp['Ky'], Wp['Kq'], Wp['Hy'], Wp['Hq'], Wp['Lyq']
    # xh' = Phi xh + Ky eps_y + Kq eps_q ; eps_q = Lyq eps_y + eta ; y = Hy xh + eps_y ; q = Hq xh + eps_q
    n = Phi.shape[0]
    G = np.hstack([Ky + Kq @ Lyq, Kq])                               # noise (eps_y, eta)
    Nn = np.block([[Wp['Ree'], np.zeros((NY, 1))], [np.zeros((1, NY)), np.array([[Wp['s_eta']]])]])
    S = solve_discrete_lyapunov(Phi, G @ Nn @ G.T)
    H = np.vstack([Hy, Hq]); J = np.vstack([np.hstack([np.eye(NY), np.zeros((NY, 1))]), np.hstack([Lyq, np.ones((1, 1))])])
    out = [H @ S @ H.T + J @ Nn @ J.T]
    Pk = np.eye(n)
    for k in range(1, kmax + 1):
        out.append(H @ Pk @ Phi @ S @ H.T + H @ Pk @ G @ Nn @ J.T); Pk = Phi @ Pk
    return out


def logged_autocov(L, kmax):
    Hr = np.vstack([L.Hy, L.Hq]); Jr = np.vstack([L.Jy, L.Jq])
    return [L.cov((Hr, Jr), (Hr, Jr), k) for k in range(kmax + 1)]


def step_response_true(months):
    """Chloride (y_Cl) response to a sustained unit increase of pumping, the aquifer alone (open loop), months 1..n."""
    z = np.zeros((NX, 1)); out = []
    for _ in range(months):
        z = A0 @ z + B0 * 1.0; out.append(float((C @ z)[1, 0]))
    return out


def step_response_prime(Wp, months):
    """The same for aquifer': xh' = (Phi - Kq Hq) xh + Kq q + (Ky + ...) eps_y ; y = Hy xh (noise-free response)."""
    Phi, Kq, Hq, Hy = Wp['Phi'], Wp['Kq'], Wp['Hq'], Wp['Hy']
    Ap = Phi - Kq @ Hq
    x = np.zeros((Phi.shape[0], 1)); out = []
    for _ in range(months):
        x = Ap @ x + Kq * 1.0; out.append(float((Hy @ x)[1, 0]))
    return out


def one_step_effect_prime(Wp):
    return (Wp['Hy'] @ Wp['Kq']).ravel()


# ------------------------------------------------------------------ clone and behaviour-regularised agent in world'
def prime_clone(Wp):
    """Infinite-window behaviour clone: the operators' mean action given the logs, q = Hq x + Lyq (y - Hy x), run with
    the filter of the logs fed its own actions."""
    Ab = Wp['Phi'] - Wp['Kq'] @ Wp['Hq']
    Cc = Wp['Hq'] - Wp['Lyq'] @ Wp['Hy']; Dc = Wp['Lyq']
    return (Ab - Wp['Ky'] @ Wp['Hy'] + Wp['Kq'] @ Cc, Wp['Ky'] + Wp['Kq'] @ Dc, Cc, Dc)


def regularised_agent(Wp, lam):
    """Behaviour-regularised offline RL in the world model of the logs: minimise model cost + lam E[(q - q_clone)^2]."""
    Phi, Ky, Kq, Hy, Hq = Wp['Phi'], Wp['Ky'], Wp['Kq'], Wp['Hy'], Wp['Hq']
    Ab = Phi - Kq @ Hq
    n = Ab.shape[0]
    Am = np.block([[Ab, Ky], [np.zeros((NY, n)), np.zeros((NY, NY))]])
    Bm = np.vstack([Kq, np.zeros((NY, 1))])
    c2 = np.hstack([Hy[1:2], np.array([[0.0, 1.0]])])
    Fb = np.hstack([Hq, Wp['Lyq']])                                    # clone: q = Fb chi
    Qm = c2.T @ c2 + lam * Fb.T @ Fb
    Rm = R + lam
    Sm = -lam * Fb.T
    P = solve_discrete_are(Am, Bm, Qm, Rm, s=Sm)
    Lg = np.linalg.solve(Rm + Bm.T @ P @ Bm, Bm.T @ P @ Am + Sm.T)
    Lx, Le = Lg[:, :n], Lg[:, n:]
    Cc = -Lx + Le @ Hy; Dc = -Le
    return (Ab - Ky @ Hy + Kq @ Cc, Ky + Kq @ Dc, Cc, Dc)


# ------------------------------------------------------------------ main analysis
def mirror(sd_s, sd_e, p=40, gamma=1.0):
    """One-step effect of pumping on (head, chloride) estimated from the logs, against formula (ii)."""
    L = Logged(sd_s, sd_e, 0.0, gamma)
    coef, _ = regress(L, ('y', 0), [('y', k) for k in range(1, p + 1)] + [('q', k) for k in range(1, p + 1)])
    beta = coef[:, NY * p]
    regs_rec = [('y', k) for k in range(0, p)] + [('q', k) for k in range(1, p + 1)]
    czh, _ = regress(L, ('zh', 0), regs_rec)
    PD = L.cross([('zh', 0)], [('zh', 0)]) - czh @ L.cross(regs_rec, [('zh', 0)])
    kpk = (L.K @ PD @ L.K.T).item()
    pred = (C @ B0 - C @ A0 @ PD @ L.K.T / (kpk + sd_e ** 2)).ravel()
    return L, dict(beta_regression=beta.tolist(), beta_formula=pred.tolist(), beta_true=(C @ B0).ravel().tolist(),
                   private_share=kpk / (kpk + sd_e ** 2), PD_trace=float(np.trace(PD)))


def learners(L, Js, kinds=('phys4', 'phys8', 'free')):
    """Every learner trained on the (infinite) logs of L, deployed on the true aquifer: true and believed costs."""
    out = {}
    for kind in kinds:
        th, _ = calibrate_ml(L, kind)
        A, B = model(th, kind)
        ct = lqg_controller(A, B)
        out[kind] = dict(theta=th.tolist(), J=J_of(ct), J_believed=J_of(ct, A, B), n_par=len(th))
    for p in [8, 32]:
        r = arx_model_agent(L, p)
        out[f'arx{p}'] = dict(J=cost(*window_controller(r[0], r[1])), J_believed=r[2] - V[1, 1])
    Wp = world_prime(L)
    ctrl, bel = prime_agent(Wp)
    out['world_model_inf'] = dict(J=cost(*ctrl), J_believed=bel - V[1, 1])
    out['clone_inf'] = dict(J=cost(*prime_clone(Wp)))
    for p in [4, 8]:
        b, a, _ = bc_rule(L, p, True)
        out[f'clone_arx{p}'] = dict(J=cost(*window_controller(b, a)))
    for w in [8, 16]:
        b, a, _ = bc_rule(L, w, False)
        out[f'clone_obs{w}'] = dict(J=cost(*window_controller(b, a)))
    return out, Wp


def fmt(J, Js):
    return 'unstable' if not np.isfinite(J) else f'{100 * (J - Js) / Js:+.1f}%'


NAMES = {'phys4': 'physical model, 4 parameters', 'phys8': 'physical model, 8 parameters', 'free': 'black-box 4-state model (20 parameters)',
         'arx8': 'black-box ARX model, 8 lags', 'arx32': 'black-box ARX model, 32 lags', 'world_model_inf': 'world model of unlimited capacity',
         'clone_inf': 'clone, unlimited window', 'clone_arx4': 'clone, 4 past rates + 5 observations', 'clone_arx8': 'clone, 8 past rates + 9 observations',
         'clone_obs8': 'clone, 8 observations only', 'clone_obs16': 'clone, 16 observations only'}


GAMMAS = {'near-optimal': 1.0, 'timid': 0.4}


def run():
    log, res = [], {}
    Ls = lqg_controller(A0, B0)
    Js = J_of(Ls)
    Kf, Pf = lq_gain(A0, B0)
    res['J_star'] = Js; res['J_full_state'] = float(np.trace(Pf @ W))
    res['setup'] = dict(base=BASE, gammas=GAMMAS, cost='(X + 0.5 c)^2 + 0.5 q^2', private='s = X + sd_s nu', K=Kf[0].tolist(),
                        open_loop_eigs=np.sort(np.abs(np.linalg.eigvals(A0)))[::-1].tolist())
    log.append(f'records-only optimum J* = {Js:.4f}; full-state optimum {res["J_full_state"]:.4f}; open-loop eigenvalue moduli '
               f'{np.round(res["setup"]["open_loop_eigs"], 4)}')
    res['settings'] = {}
    for name, gamma in GAMMAS.items():
        R_ = {}
        L, mb = mirror(BASE['sd_s'], BASE['sd_e'], gamma=gamma)
        R_['mirror'] = mb; R_['J_op'] = L.J
        R_['J_op_no_e'] = Logged(BASE['sd_s'], 0.0, 0.0, gamma).J
        log.append(f'== operators {name} (gain {gamma} x optimal, private toe reading sd {BASE["sd_s"]}, unrecorded variation sd {BASE["sd_e"]}): '
                   f'cost {fmt(L.J, Js)}; private share of unexplained pumping {mb["private_share"]:.3f}')
        log.append(f'(ii) one-step effect of pumping on (head, chloride): true {np.round(mb["beta_true"], 4)}, logs {np.round(mb["beta_regression"], 4)}, '
                   f'formula {np.round(mb["beta_formula"], 4)}')
        out, Wp = learners(L, Js)
        out0, _ = learners(Logged(np.inf, BASE['sd_e'], 0.0, gamma), Js)
        R_['learners'] = out; R_['learners_no_private'] = out0
        for k in out:
            bel = out[k].get('J_believed')
            log.append(f'  {NAMES[k]:45s}: deployed {fmt(out[k]["J"], Js):>9s}' + (f', believed {fmt(bel, Js):>7s}' if bel is not None else ' ' * 18) +
                       f'   | without private information {fmt(out0[k]["J"], Js)}')
        log.append('  calibrated physical parameters (4): ' + ', '.join(f'{n} {v:.3f}' for n, v in zip(TH_NAMES, out['phys4']['theta'])))
        ac1 = logged_autocov(L, 60); ac2 = world_prime_autocov(Wp, 60)
        diff = max(float(np.max(np.abs(x - y))) for x, y in zip(ac1, ac2))
        st, sp = step_response_true(60), step_response_prime(Wp, 60)
        R_['equivalence'] = dict(max_abs_diff=diff, scale=max(float(np.max(np.abs(x))) for x in ac1), order_prime=int(Wp['Phi'].shape[0]),
                                 one_step_prime=one_step_effect_prime(Wp).tolist(), step_true=st, step_prime=sp)
        log.append(f'(iii) aquifer\' (order {Wp["Phi"].shape[0]}) with operators\' who use only the logs reproduces the autocovariances of the logs '
                   f'(lags 0-60) to {diff:.1e}; chloride after 12/36/60 months of one extra unit of pumping: true {st[11]:.2f}/{st[35]:.2f}/{st[59]:.2f}, '
                   f'aquifer\' {sp[11]:.2f}/{sp[35]:.2f}/{sp[59]:.2f}')
        reg = [dict(lam=lam, J=cost(*regularised_agent(Wp, lam))) for lam in [0, 0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100, 1e3, 1e4]]
        R_['regularised'] = reg
        best = min(reg, key=lambda r: r['J'] if r['J'] is not None and np.isfinite(r['J']) else 1e99)
        log.append('behaviour-regularised offline RL in the world model of the logs (lam = weight on staying close to the operators): ' +
                   ', '.join(f'{r["lam"]:g}: {fmt(r["J"], Js)}' for r in reg) + f'; best {fmt(best["J"], Js)} at lam {best["lam"]:g}')
        iv = {}
        for sd_d in [0.05, 0.2]:
            Ld = Logged(BASE['sd_s'], BASE['sd_e'], sd_d, gamma)
            row = dict(J_op=Ld.J)
            thp, mres = calibrate_iv(Ld, 24, 'phys4')
            row['phys4_iv'] = dict(theta_err=float(np.max(np.abs(thp - THETA0))), max_moment=mres, J=J_of(lqg_controller(*model(thp))))
            thf, mf = calibrate_iv(Ld, 24, 'free')
            row['free_iv'] = dict(max_moment=mf, J=J_of(lqg_controller(*model(thf, 'free'))),
                                  eigs=np.sort(np.abs(np.linalg.eigvals(model(thf, 'free')[0]))).tolist())
            thfm = calibrate_ivml(Ld, 24, 'free')
            row['free_ivml'] = dict(J=J_of(lqg_controller(*model(thfm, 'free'))),
                                    eigs=np.sort(np.abs(np.linalg.eigvals(model(thfm, 'free')[0]))).tolist())
            thml, _ = calibrate_ml(Ld, 'free')
            row['free_ml'] = J_of(lqg_controller(*model(thml, 'free')))
            row['world_model_inf'] = cost(*prime_agent(world_prime(Ld))[0])
            iv[str(sd_d)] = row
            log.append(f'(iv) dither sd {sd_d} (operators\' cost {fmt(Ld.J, Js)}): physical model by dither moments: parameter error '
                       f'{row["phys4_iv"]["theta_err"]:.1e}, deployed {fmt(row["phys4_iv"]["J"], Js)}; black-box 4-state by moments only '
                       f'{fmt(row["free_iv"]["J"], Js)} (eigenvalues {np.round(row["free_iv"]["eigs"], 3)}), by moments + likelihood '
                       f'{fmt(row["free_ivml"]["J"], Js)}, by likelihood only {fmt(row["free_ml"], Js)}; world model of the logs, dither inside '
                       f'the pumping: {fmt(row["world_model_inf"], Js)}')
        R_['iv'] = iv
        res['settings'][name] = R_
    # scan over private information and unrecorded variation (near-optimal operators)
    scan = []
    for sd_s in [0.03, 0.1, 0.3, 1.0, np.inf]:
        for sd_e in [0.03, 0.1, 0.3]:
            Lx, m = mirror(sd_s, sd_e)
            o, _ = learners(Lx, Js, kinds=('phys4', 'free'))
            row = dict(sd_s=sd_s, sd_e=sd_e, private_share=m['private_share'], beta_cl=m['beta_regression'][1], J_op=Lx.J,
                       **{k: o[k]['J'] for k in ['phys4', 'free', 'arx32', 'world_model_inf', 'clone_inf', 'clone_arx4', 'clone_obs8']},
                       believed_world=o['world_model_inf']['J_believed'], head_toe=o['phys4']['theta'][1])
            scan.append(row)
            log.append(f'scan sd_s {sd_s:>5} sd_e {sd_e:.2f}: private share {m["private_share"]:.3f}, chloride effect in the logs {m["beta_regression"][1]:+.3f}; '
                       f'phys4 {fmt(row["phys4"], Js)}, free {fmt(row["free"], Js)}, ARX32 {fmt(row["arx32"], Js)}, world model {fmt(row["world_model_inf"], Js)} '
                       f'(believed {fmt(row["believed_world"], Js)}), clone {fmt(row["clone_inf"], Js)}, clone obs8 {fmt(row["clone_obs8"], Js)}')
    res['scan'] = scan
    json.dump(clean(res), open(os.path.join(HERE, 'pasqyra_results.json'), 'w'), indent=1)
    open(os.path.join(HERE, 'pasqyra.log'), 'w').write('\n'.join(log) + '\n')
    print('\n'.join(log))


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (float, np.floating)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.ndarray):
        return clean(o.tolist())
    return o


if __name__ == '__main__':
    run()
