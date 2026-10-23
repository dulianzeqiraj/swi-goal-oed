"""ZGJEDHJA-GO: a dynamic discrete choice model of pumping at a coastal well whose agents anticipate a salinized
state that the data never show (the setting of Sasaki, Takahashi, Xin & Hu, J. Econometrics 2023).

States s = 0..4 are chloride classes seen in the data (4 = the frontier, the toe of the wedge is close); B = 5 is
the salinized, abandoned well, never observed in the sample period. Each season the farmer chooses a = 1 (high
pumping) or a = 0 (low pumping); type-I extreme value shocks; discount factor beta known.
  Covered transitions F_a(s'|s) (identified from the data): high pumping pushes chloride up, low pumping lets
  recharge push it down.
  Anticipated transition into B: from the frontier under high pumping with probability q (agents' belief, never
  realized in the sample); low pumping never salinizes from the frontier.
  Flow payoffs: u(1, s) = theta_s, u(0, s) = 0 (normalization); the salinized state pays w per season forever,
  V(B) = w / (1 - beta).
Proposition L of review 39: V on the covered states and theta_0..theta_3 are identified without (q, w); the frontier
payoff and w enter the law of the data only through the index c(q) = theta_4 + beta q w / (1 - beta).
"""
import numpy as np

S = 5
B = S
BETA = 0.9
UP = (0.10, 0.40)        # probability of moving up one class under low / high pumping
DOWN = (0.30, 0.08)      # probability of moving down one class
THETA = 1.5 - 0.25 * np.arange(S)
Q_TRUE, W_TRUE = 0.15, -1.0
TAU = 0.5                # pumping fee per high-pumping season
H, S0 = 10, 3            # horizon (seasons) and starting class of the counterfactuals


def covered_F(up=UP, down=DOWN):
    F = np.zeros((2, S, S))
    for a in (0, 1):
        for s in range(S):
            pu = up[a] if s < S - 1 else 0.0
            pd = down[a] if s > 0 else 0.0
            F[a, s, min(s + 1, S - 1)] += pu
            F[a, s, max(s - 1, 0)] += pd
            F[a, s, s] += 1 - pu - pd
    return F


F_TRUE = covered_F()


def belief(F, q):
    """Agents' transitions on S + 1 states: from the frontier under high pumping the well salinizes with prob q."""
    G = np.zeros((2, S + 1, S + 1))
    G[:, :S, :S] = F
    G[1, S - 1, :S] *= (1 - q)
    G[1, S - 1, B] = q
    G[:, B, B] = 1.0
    return G


def solve(theta, q, w, F=F_TRUE, tau=0.0, tol=1e-12):
    """Newton-Kantorovich iteration on the smoothed Bellman equation (quadratic convergence, about 6 steps);
    returns P(a = 1 | s) on the covered states, the value function and the beliefs."""
    G = belief(F, q)
    flow1 = np.r_[np.asarray(theta, float) - tau, 0.0]
    VB = w / (1 - BETA)
    V = np.zeros(S + 1)
    V[B] = VB
    I = np.eye(S + 1)
    for _ in range(100):
        v0 = BETA * G[0] @ V
        v1 = flow1 + BETA * G[1] @ V
        TV = np.logaddexp(v0, v1)
        TV[B] = VB
        p1 = 1 / (1 + np.exp(-(v1 - v0)))
        J = BETA * ((1 - p1)[:, None] * G[0] + p1[:, None] * G[1])
        J[B] = 0.0
        step = np.linalg.solve(I - J, V - TV)
        V = V - step
        if np.max(np.abs(step)) < tol:
            break
    v0 = BETA * G[0] @ V
    v1 = flow1 + BETA * G[1] @ V
    P1 = 1 / (1 + np.exp(-(v1 - v0)))
    return P1[:S], V, G


def invert(P1, F, q, w):
    """Hotz-Miller / Magnac-Thesmar inversion for given beliefs (q, w): low pumping never reaches B, so V on the
    covered states solves (I - beta F_0) V = -log P0; the payoffs follow from the log-odds."""
    P1 = np.asarray(P1, float)
    P0 = 1 - P1
    V = np.linalg.solve(np.eye(S) - BETA * F[0], -np.log(P0))
    v0 = BETA * F[0] @ V
    EV1 = F[1] @ V
    EV1[S - 1] = (1 - q) * (F[1, S - 1] @ V) + q * w / (1 - BETA)
    return np.log(P1 / P0) + v0 - BETA * EV1


def index_c(P1, F, q):
    """The identified frontier index c(q) = theta_4 + beta q w / (1 - beta) (Proposition L)."""
    th = invert(P1, F, q, 0.0)
    return th[S - 1]


def paths(theta, q, w, F, tau=0.0, qscale=1.0, horizon=H, s0=S0):
    """Risk of salinization within the horizon and expected high-pumping seasons, starting from class s0, when the
    true intrusion probability is q * qscale (agents know it) and a fee tau is charged."""
    P1, V, G = solve(theta, q * qscale, w, F, tau)
    M = np.zeros((S + 1, S + 1))
    for s in range(S + 1):
        p = P1[s] if s < S else 0.0
        M[s] = (1 - p) * G[0, s] + p * G[1, s]
    d = np.zeros(S + 1)
    d[s0] = 1.0
    pump = 0.0
    for _ in range(horizon):
        pump += d[:S] @ P1
        d = d @ M
    return d[B], pump


def gamma_fee(P1, F, q, tau=TAU):
    """Goal 1: reduction of the salinization risk from a pumping fee (identified given q; w is irrelevant)."""
    th = invert(P1, F, q, 0.0)
    return paths(th, q, 0.0, F)[0] - paths(th, q, 0.0, F, tau=tau)[0]


def gamma_recharge(P1, F, q, w):
    """Goal 2: extra high-pumping seasons when managed recharge halves the intrusion probability (needs q and w)."""
    th = invert(P1, F, q, w)
    return paths(th, q, w, F, qscale=0.5)[1] - paths(th, q, w, F)[1]


def simulate_panel(n, T, rng, theta=THETA, q=Q_TRUE, w=W_TRUE, F=F_TRUE):
    """A panel of n wells over T seasons in the sample period: choices follow the agents' anticipating policy, but
    the salinized state is never realized (the front has not arrived), so transitions follow the covered law."""
    P1, _, _ = solve(theta, q, w, F)
    s = rng.integers(0, S - 1, n)
    rec = []
    Fc = np.cumsum(F, axis=2)
    for _ in range(T):
        a = (rng.random(n) < P1[s]).astype(int)
        s2 = (rng.random(n)[:, None] > Fc[a, s]).sum(1)
        rec.append(np.stack([s, a, s2], 1))
        s = s2
    return np.concatenate(rec)


def estimate(panel, prior=0.5):
    """Frequency estimates of the choice probabilities and of the covered transitions (with a light prior count so
    that every cell is defined)."""
    s, a, s2 = panel[:, 0], panel[:, 1], panel[:, 2]
    n1 = np.bincount(s[a == 1], minlength=S) + prior
    n0 = np.bincount(s[a == 0], minlength=S) + prior
    P1 = n1 / (n1 + n0)
    F = np.zeros((2, S, S))
    for aa in (0, 1):
        for ss in range(S):
            m = (s == ss) & (a == aa)
            cnt = np.bincount(s2[m], minlength=S).astype(float)
            allowed = np.zeros(S)
            allowed[[max(ss - 1, 0), ss, min(ss + 1, S - 1)]] = 1
            cnt = cnt + prior * allowed / allowed.sum()
            F[aa, ss] = cnt / cnt.sum()
    return P1, F
