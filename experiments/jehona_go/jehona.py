"""JEHONA-GO core (jehona: the echo). Design-based dynamic causal effects of pumping on seawater intrusion.

The finite population. N coastal aquifer compartments (units), each with one supply well, observed for
36 monthly periods. In every period the well pumps (w = 1) or not (w = 0). Potential outcomes are fixed
functions of the whole assignment path of the unit (no interference between units), computed by a
transient sharp-interface model:
  Sy dh/dt = T d2h/dx2 - (Q w_t / dx) delta(x - x_w)      on 0 < x < L,
  h(0) = 0 (sea), T dh/dx(L) = q_in (regional inflow),
  equilibrium toe x_eq(t): the first x from the coast where h >= delta*b = 1 m (Ghyben-Herzberg),
  toe dynamics dx_toe/dt = (x_eq - x_toe)/tau, with tau = tau_adv when the toe advances and the much
  longer tau_ret when it retreats (intrusion is fast, flushing is slow): a nonlinear memory.
Outcomes per period: head at the supply well (linear in the path), toe position (nonlinear) and the
fraction of the month in which the toe is beyond the supply well ("salinization exposure").
Exogenous forcing, part of the fixed population: the regional inflow varies with the season and from
year to year, q_in(t) = q_in (1 + 0.3 sin(2 pi (t + 1/2)/12 + phi_i) + 0.2 a_{i,year}); it is observed and
given to the surrogate as well.

The surrogate (a deliberately wrong model): the same equations with T x 0.8, Sy x 1.4 and a symmetric
toe relaxation of 90 days, i.e. wrong memory and no hysteresis.
"""
import numpy as np
from scipy.linalg import solve_banded

DAYS, NSUB = 30.0, 10
DT = DAYS / NSUB
L, NX = 4000.0, 81
DX = L / (NX - 1)
X = np.linspace(0.0, L, NX)
HC = 1.0                    # delta * b: the base of the aquifer is reached where h < 1 m
NT = 36                     # months in the experiment
OUTS = ['head', 'toe', 'sal']


def make_units(n, seed=2026):
    rng = np.random.default_rng(seed)
    U = []
    for _ in range(n):
        T = rng.uniform(400, 1500)                    # transmissivity, m2/d
        Sy = rng.uniform(0.05, 0.20)                  # specific yield
        x0 = rng.uniform(400, 800)                    # natural toe position (no pumping), m
        qin = T / x0                                  # regional inflow per unit width, m2/d
        xw = rng.uniform(900, 1400)                   # supply well, m from the coast
        vmax = min(1.5, 0.95 * xw / x0)
        v = rng.uniform(0.6, vmax)                    # steady head at the well under full pumping, m
        Q = qin - v * T / xw                          # pumping per unit width, m2/d
        U.append(dict(T=T, Sy=Sy, qin=qin, xw=xw, Q=Q, tau_adv=rng.uniform(20, 60), tau_ret=rng.uniform(120, 360),
                      phase=rng.uniform(0, 2 * np.pi), ya=rng.standard_normal(4)))
    return U


def surrogate(u):
    s = dict(u); s['T'] = 0.8 * u['T']; s['Sy'] = 1.4 * u['Sy']; s['tau_adv'] = s['tau_ret'] = 90.0
    return s


def _matrix(u, steady=False):
    """banded matrix for nodes 1..NX-1 (node 0 is the sea, h = 0)."""
    n = NX - 1; c = u['T'] / DX ** 2; a = 0.0 if steady else u['Sy'] / DT
    ab = np.zeros((3, n))
    ab[1, :] = a + 2 * c
    ab[0, 1:] = -c                                   # super-diagonal
    ab[2, :-1] = -c                                  # sub-diagonal
    ab[2, n - 2] = -2 * c                            # Neumann at x = L (ghost node)
    return ab


def _rhs_const(u, t=None):
    """inflow term at x = L; with t (month index) the seasonal and yearly forcing is applied."""
    n = NX - 1; b = np.zeros(n)
    q = u['qin'] if t is None else u['qin'] * (1 + 0.3 * np.sin(2 * np.pi * (t + 0.5) / 12 + u['phase']) + 0.2 * u['ya'][t // 12])
    b[n - 1] = 2 * q / DX
    return b


IW = None


def _well(u):
    return int(round(u['xw'] / DX)) - 1             # index among nodes 1..NX-1


def x_eq(h):
    """first position from the coast where h >= HC (h: (NX-1, R) heads at nodes 1..NX-1)."""
    H = np.vstack([np.zeros((1, h.shape[1])), h])
    ok = H >= HC
    any_ = ok.any(0)
    j = np.argmax(ok, 0)
    j = np.where(any_, j, NX - 1)
    jm = np.maximum(j - 1, 0)
    h1, h0 = H[j, np.arange(H.shape[1])], H[jm, np.arange(H.shape[1])]
    frac = np.where(h1 > h0, (HC - h0) / np.where(h1 > h0, h1 - h0, 1.0), 0.0)
    x = X[jm] + np.clip(frac, 0, 1) * DX
    return np.where(any_, x, L)


def initial_state(u, pump=0.5):
    """steady state under a historical pumping rate pump * Q, with the toe at equilibrium."""
    b = _rhs_const(u); iw = _well(u); b = b.copy(); b[iw] -= pump * u['Q'] / DX
    h = solve_banded((1, 1), _matrix(u, steady=True), b)
    return h, float(x_eq(h[:, None])[0])


def simulate(u, W):
    """W: (R, NT) paths for one unit (0/1, or a constant fraction for a reference run).
    Returns {'head','toe','sal'}: (R, NT)."""
    W = np.asarray(W, float); R = W.shape[0]
    h0, xt0 = initial_state(u)
    h = np.repeat(h0[:, None], R, 1); xt = np.full(R, xt0)
    ab = _matrix(u); iw = _well(u); a = u['Sy'] / DT
    out = {k: np.zeros((R, W.shape[1])) for k in OUTS}
    for t in range(W.shape[1]):
        b = _rhs_const(u, t)
        sink = u['Q'] * W[:, t] / DX
        hs = np.zeros(R); sal = np.zeros(R)
        for _ in range(NSUB):
            rhs = a * h + b[:, None]
            rhs[iw] -= sink
            h = solve_banded((1, 1), ab, rhs)
            xe = x_eq(h)
            tau = np.where(xe > xt, u['tau_adv'], u['tau_ret'])
            xt = xt + DT * (xe - xt) / tau
            hs += h[iw]; sal += (xt >= u['xw'])
        out['head'][:, t] = hs / NSUB; out['toe'][:, t] = xt; out['sal'][:, t] = sal / NSUB
    return out


def walsh(f):
    """fast Walsh-Hadamard transform along axis 0 of an array with 2**m rows; returns the coefficients
    f_hat(S) = mean_w f(w) chi_S(w), chi_S(w) = prod_{j in S} (2 w_j - 1), rows indexed by subsets S
    (bit j of the row index = coordinate j), the same convention as the paths."""
    a = np.array(f, dtype=float).copy(); n = a.shape[0]; hgap = 1
    while hgap < n:
        a = a.reshape((n // (2 * hgap), 2, hgap) + a.shape[1:])
        x, y = a[:, 0].copy(), a[:, 1].copy()
        a[:, 0], a[:, 1] = x + y, y - x                # bit = 1 gets (+1), bit = 0 gets (-1) for chi
        a = a.reshape((n,) + a.shape[3:]); hgap *= 2
    return a / n


def paths_all(m):
    """all 2**m paths of length m; row r has w_j = bit j of r."""
    r = np.arange(2 ** m)
    return ((r[:, None] >> np.arange(m)[None, :]) & 1).astype(float)


def design_paths(rng, R, N, B, nt=NT):
    """Bernoulli(1/2) switchback with blocks of B months, independent across units and blocks: (R, N, nt)."""
    nb = -(-nt // B)
    blk = (rng.random((R, N, nb)) < 0.5).astype(float)
    return np.repeat(blk, B, axis=2)[:, :, :nt], blk
