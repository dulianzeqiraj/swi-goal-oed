"""VITET-GO, general logged world: any monitoring network (records y = C_r z + v) and operators who use the records
only (gain gamma x optimal on their Kalman filter of the records, plus unrecorded variation e). For a physical model
with 4 uncertain parameters (pumping as forcing) it gives the Fisher information per month of the logs, the Hessian of
the true cost of the plug-in rule, and the local minimax years tr(H I^-1) / (2 eps J*) / 12 for each monitoring network.
"""
import os
import sys

import numpy as np
from scipy.linalg import solve_discrete_are, solve_discrete_lyapunov

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'pasqyra_go'))
import pasqyra as p  # noqa: E402

NX = 4
W = p.W
Q = p.Q
R = p.R


class Net:
    """A monitoring network: rows of C_r and noise standard deviations."""

    def __init__(self, rows, sds, name):
        self.C = np.array(rows, dtype=float)
        self.V = np.diag(np.array(sds, dtype=float) ** 2)
        self.name = name
        self.ny = self.C.shape[0]


BASE_NET = Net([[0, 1, 0, 0], [0, 0, 1, 0.5]], [0.05, 0.3], 'head + sentinel chloride (baseline)')


def kf_gain(A, net):
    S = solve_discrete_are(A.T, net.C.T, W, net.V)
    M = S @ net.C.T @ np.linalg.inv(net.C @ S @ net.C.T + net.V)
    return S, M


def lq_gain(A, B):
    P = solve_discrete_are(A, B, Q, R)
    return np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)


def controller(A, B, net, gamma=1.0):
    """Records-only rule for model (A, B): xi' = F xi + G y, q = Hc xi + Dc y (observer fed its own output)."""
    K = gamma * lq_gain(A, B)
    _, M = kf_gain(A, net)
    ABK = A - B @ K
    I = np.eye(NX)
    return dict(F=ABK @ (I - M @ net.C), G=ABK @ M, Hc=-K @ (I - M @ net.C), Dc=-K @ M, K=K, M=M)


def true_cost(ct, net, A=None, B=None):
    A = p.A0 if A is None else A; B = p.B0 if B is None else B
    k = ct['F'].shape[0]
    Acl = np.block([[A + B @ ct['Dc'] @ net.C, B @ ct['Hc']], [ct['G'] @ net.C, ct['F']]])
    if np.max(np.abs(np.linalg.eigvals(Acl))) >= 1 - 1e-10:
        return float('inf')
    Gn = np.block([[np.eye(NX), B @ ct['Dc']], [np.zeros((k, NX)), ct['G']]])
    Nz = np.block([[W, np.zeros((NX, net.ny))], [np.zeros((net.ny, NX)), net.V]])
    Sig = solve_discrete_lyapunov(Acl, Gn @ Nz @ Gn.T)
    Lu = np.hstack([ct['Dc'] @ net.C, ct['Hc']])
    return float(np.trace(Q @ Sig[:NX, :NX]) + np.trace(R @ (Lu @ Sig @ Lu.T + ct['Dc'] @ net.V @ ct['Dc'].T)))


class LoggedNet:
    """Aquifer + operators (records only) with unrecorded variation e and an optional white recorded dither d.
    Joint state (z, p) with p the operators' prior estimate; noise n = (w, v, e, d)."""

    def __init__(self, net, sd_e, gamma=1.0, sd_d=0.0):
        A, B = p.A0, p.B0
        self.net = net
        K = gamma * lq_gain(A, B)
        _, M = kf_gain(A, net)
        ny = net.ny
        nn = NX + ny + 2
        self.nn = nn
        self.N = np.diag(np.concatenate([np.diag(W), np.diag(net.V), [sd_e ** 2, sd_d ** 2]]))
        Pw = np.zeros((NX, nn)); Pw[:, :NX] = np.eye(NX)
        Pv = np.zeros((ny, nn)); Pv[:, NX:NX + ny] = np.eye(ny)
        Ped = np.zeros((1, nn)); Ped[0, NX + ny] = 1.0; Ped[0, NX + ny + 1] = 1.0
        Hz = np.hstack([np.eye(NX), np.zeros((NX, NX))])
        Ez = np.hstack([M @ net.C, np.eye(NX) - M @ net.C]); Ev = M @ Pv
        self.Hq = -K @ Ez; self.Jq = -K @ Ev + Ped
        self.Hy = net.C @ Hz; self.Jy = Pv
        Phi = np.zeros((2 * NX, 2 * NX)); Gam = np.zeros((2 * NX, nn))
        Phi[:NX] = A @ Hz + B @ self.Hq; Gam[:NX] = B @ self.Jq + Pw
        Phi[NX:] = (A - B @ K) @ Ez; Gam[NX:] = (A - B @ K) @ Ev + B @ Ped
        self.Phi, self.Gam = Phi, Gam
        self.Sig = solve_discrete_lyapunov(Phi, Gam @ self.N @ Gam.T)
        self.J = float(np.trace(Q @ self.Sig[:NX, :NX]) + np.trace(R @ (self.Hq @ self.Sig @ self.Hq.T + self.Jq @ self.N @ self.Jq.T)))


def nll(theta, L, kind='phys4'):
    A, B = p.model(theta, kind)
    net = L.net
    try:
        S, M = kf_gain(A, net)
    except Exception:
        return 1e6
    Kp = A @ M
    Sth = net.C @ S @ net.C.T + net.V
    n1 = L.Phi.shape[0]
    Phi = np.zeros((n1 + NX, n1 + NX)); Gam = np.zeros((n1 + NX, L.nn))
    Phi[:n1, :n1] = L.Phi; Gam[:n1] = L.Gam
    Phi[n1:, :n1] = B @ L.Hq + Kp @ L.Hy
    Phi[n1:, n1:] = A - Kp @ net.C
    Gam[n1:] = B @ L.Jq + Kp @ L.Jy
    if np.max(np.abs(np.linalg.eigvals(Phi))) >= 1:
        return 1e6
    Sg = solve_discrete_lyapunov(Phi, Gam @ L.N @ Gam.T)
    He = np.hstack([L.Hy, -net.C])
    Se = He @ Sg @ He.T + L.Jy @ L.N @ L.Jy.T
    return 0.5 * np.linalg.slogdet(Sth)[1] + 0.5 * np.trace(np.linalg.solve(Sth, Se))


def hessian(f, x0, h):
    n = len(x0); Hm = np.zeros((n, n)); f0 = f(x0)
    for i in range(n):
        for j in range(i, n):
            if i == j:
                e = np.zeros(n); e[i] = h[i]
                Hm[i, i] = (f(x0 + e) - 2 * f0 + f(x0 - e)) / h[i] ** 2
            else:
                ei = np.zeros(n); ei[i] = h[i]; ej = np.zeros(n); ej[j] = h[j]
                Hm[i, j] = Hm[j, i] = (f(x0 + ei + ej) - f(x0 + ei - ej) - f(x0 - ei + ej) + f(x0 - ei - ej)) / (4 * h[i] * h[j])
    return Hm


def analyse(net, sd_e=0.1, gamma=1.0, sd_d=0.0, kind='phys4', rel=2e-3):
    th = p.theta_true(kind)
    h = rel * np.maximum(np.abs(th), 0.02)
    L = LoggedNet(net, sd_e, gamma, sd_d)
    I = hessian(lambda t: nll(t, L, kind), th, h)
    Js = true_cost(controller(p.A0, p.B0, net), net)
    H = hessian(lambda t: true_cost(controller(*p.model(t, kind), net), net), th, h)
    trHI = float(np.trace(H @ np.linalg.inv(I)))
    return dict(net=net.name, sd_e=sd_e, gamma=gamma, sd_d=sd_d, J_star=Js, J_op=L.J, I=I, H=H, trHI=trHI,
                years_1pct=trHI / (2 * 0.01 * Js) / 12, years_01pct=trHI / (2 * 0.001 * Js) / 12,
                logdetI=float(np.linalg.slogdet(I)[1]))
