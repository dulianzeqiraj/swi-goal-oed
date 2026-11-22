"""ZANAFILLA-GO core: where does the chloride of a coastal well come from?

Five candidate sources mix in each sample: modern seawater (MS), relict seawater (RS), halite dissolution brine (HL),
anthropogenic chloride (AN: wastewater, fertiliser, irrigation return) and fresh recharge (FW).  The water fractions f
lie on the simplex.  Every source has a signature known only as an interval (chloride concentration, Br/Cl and B/Cl mass
ratios, d18O, d2H, tritium).  The target of a decision is the share of the chloride of a sample that comes from modern
seawater, s = f_MS Cl_MS / sum_k f_k Cl_k.

Contents
- the synthetic, physically motivated field (wells, screens, a sharp-interface wedge with a mixing zone, a relict pocket,
  a halite body that may or may not exist, anthropogenic chloride near the town) and its observations with noise;
- the identified set: the exact polytope of fractions and contributions consistent with the data within +-eps and with
  the signature intervals (Proposition 1 of the review), and sharp bounds of fractions and of the chloride share by
  linear and linear-fractional programming (Charnes-Cooper);
- the classical point inverse (non-negative least squares on the simplex with central signatures);
- an amortised neural estimator (numpy MLP with three quantile heads) and its split-conformal calibration (CQR).
All numbers of signatures and noise are illustrative, set from ranges reported in the literature; they are not data of
any site."""
import numpy as np
from scipy.optimize import linprog, nnls
from scipy.stats import norm

SOURCES = ['MS', 'RS', 'HL', 'AN', 'FW']
NAMES = {'MS': 'modern seawater', 'RS': 'relict seawater', 'HL': 'halite dissolution', 'AN': 'anthropogenic',
         'FW': 'fresh recharge'}
K = len(SOURCES)
# signature intervals [lo, hi] per source, in the order of SOURCES (illustrative)
SIG = {
    # mg/L.  The sea and the upgradient fresh water can be sampled, so their intervals are narrow; the relict water and a
    # halite brine cannot, so theirs are wide.
    'Cl':   np.array([[19500, 21500], [12000, 21000], [5000, 100000], [100, 400], [10, 25]], float),
    'BrCl': np.array([[3.35e-3, 3.5e-3], [2.9e-3, 3.8e-3], [5e-5, 5e-4], [1.2e-3, 2.8e-3], [3.0e-3, 5.0e-3]]),  # mass ratio
    'BCl':  np.array([[2.2e-4, 2.4e-4], [0.5e-4, 1.8e-4], [0.1e-4, 1.0e-4], [1.5e-3, 4.0e-3], [2.0e-4, 8.0e-4]]),
    'd18O': np.array([[1.1, 1.4], [-3.0, 0.3], [-7.5, -5.5], [-6.0, -4.8], [-7.2, -6.6]]),                  # permil
    'd2H':  np.array([[7, 9], [-22, 2], [-48, -35], [-38, -30], [-45, -41]], float),                       # permil
    'H3':   np.array([[0.4, 0.9], [0.0, 0.05], [0.0, 3.0], [3.0, 7.0], [1.0, 7.0]]),                        # TU
    # base-exchange index per unit chloride (meq per mg Cl): advancing seawater loses Na (BEX < 0), a flushed relict
    # salinity gains Na (BEX > 0), halite gives Na/Cl = 1 (about -2e-3), fresh Ca-Mg water a small positive baseline
    'BEXCl': np.array([[-5e-3, -0.5e-3], [0.5e-3, 8e-3], [-2.5e-3, -1.5e-3], [-1.5e-3, 1.5e-3], [0.0, 0.06]]),
}
# how each tracer mixes: 'cl' = ratio to chloride (contribution r_k c_k), 'w' = by water fraction (contribution s_k f_k)
KIND = {'Br': ('BrCl', 'cl'), 'B': ('BCl', 'cl'), 'BEX': ('BEXCl', 'cl'), 'd18O': ('d18O', 'w'), 'd2H': ('d2H', 'w'),
        'H3': ('H3', 'w')}
# measurement error: sd = rel * value + abs
NOISE = {'Cl': (0.03, 1.0), 'Br': (0.05, 0.005), 'B': (0.05, 0.005), 'd18O': (0.0, 0.1), 'd2H': (0.0, 1.0),
         'H3': (0.05, 0.3), 'BEX': (None, None)}
# the base-exchange index is a difference of large numbers: 2% on Na + K + Mg and on 1.0716 Cl (meq/L), plus 0.1 meq/L
BEX_REL, BEX_ABS = 0.02, 0.1
# tracer sets in the order in which they could be added; 'Cl + major ions' is what Fushe-Kuqe has today
TRACER_SETS = {'Cl': ['Cl'], 'Cl + major ions': ['Cl', 'BEX'], '+ Br': ['Cl', 'BEX', 'Br'],
               '+ d18O, d2H': ['Cl', 'BEX', 'Br', 'd18O', 'd2H'], '+ tritium': ['Cl', 'BEX', 'Br', 'd18O', 'd2H', 'H3'],
               '+ B (all)': ['Cl', 'BEX', 'Br', 'd18O', 'd2H', 'H3', 'B']}

# ---------------------------------------------------------------------------------------------- the synthetic field
WELL_X = np.array([0.4, 0.8, 1.2, 1.8, 2.5, 3.2, 4.0, 5.0, 6.0, 7.0, 8.5, 10.0])     # km from the coast
SCREENS = np.array([40.0, 110.0])                                                   # m below sea level
URBAN = (WELL_X >= 1.5) & (WELL_X <= 5.0)


def sample_ids():
    """(x, z, upper?) for the 24 samples: 12 wells, two screens."""
    xs, zs, up = [], [], []
    for i, x in enumerate(WELL_X):
        for j, z in enumerate(SCREENS):
            xs.append(x); zs.append(z); up.append(j == 0)
    return np.array(xs), np.array(zs), np.array(up)


X, Z, UP = sample_ids()
NS = len(X)


def site_caps(i):
    """Upper bounds of the water fractions of sample i from site knowledge: anthropogenic water only in upper screens
    (up to 0.35 under the town, 0.08 elsewhere), halite brine only in lower screens (up to 0.03)."""
    cap = np.ones(K)
    if UP[i]:
        cap[3] = 0.35 if URBAN[i // 2] else 0.08
        cap[2] = 0.0
    else:
        cap[3] = 0.02
        cap[2] = 0.03
    return cap


def draw_field(rng, regime='prior'):
    """Water fractions (NS x K) and true signatures of one field.
    regime 'prior': the world the neural estimator is trained on; 'shift': more relict seawater and a halite body more
    often (sources and signature intervals unchanged); 'missing': as 'prior' plus a deep brine that is not in the list."""
    a = rng.uniform(35, 100)                     # interface depth coefficient, m / sqrt(km)
    w = rng.uniform(8, 30)                       # half-width of the mixing zone, m
    m = rng.uniform(0.7, 1.0)                    # seawater fraction at the centre of the wedge
    zeta = a * np.sqrt(X)
    f_ms = m * norm.cdf((Z - zeta) / w)
    r0 = rng.uniform(0.08, 0.25) if regime == 'shift' else rng.uniform(0.0, 0.08)
    xr = rng.uniform(2.0, 8.0)
    f_rs = r0 * (Z / SCREENS[1]) * np.exp(-((X - xr) / 3.0) ** 2)
    p_hl = 0.6 if regime == 'shift' else 0.1
    f_hl = np.zeros(NS)
    if rng.uniform() < p_hl:
        xh = rng.uniform(1.0, 8.0)
        f_hl = rng.uniform(0.002, 0.02) * (~UP) * np.exp(-0.5 * ((X - xh) / 1.5) ** 2)
    a0 = rng.uniform(0.0, 0.25)
    f_an = a0 * UP * np.where(URBAN[np.repeat(np.arange(len(WELL_X)), 2)], 1.0, 0.2)
    F = np.c_[f_ms, f_rs, f_hl, f_an]
    s = F.sum(1)
    F = F / np.maximum(s, 1.0)[:, None]
    F = np.c_[F, 1.0 - F.sum(1)]
    sig = {k: rng.uniform(v[:, 0], v[:, 1]) for k, v in SIG.items()}
    extra = None
    if regime == 'missing':                      # a deep brine, Br-rich (Cl/Br about 120), not among the five sources
        xb = rng.uniform(1.0, 9.0)
        fb = rng.uniform(0.01, 0.05) * (~UP) * np.exp(-0.5 * ((X - xb) / 2.0) ** 2)
        extra = dict(f=fb, Cl=rng.uniform(40000, 80000), BrCl=rng.uniform(6e-3, 1.0e-2), BCl=rng.uniform(1e-4, 5e-4),
                     BEXCl=rng.uniform(-3e-3, -1e-3), d18O=rng.uniform(-3.0, -1.0), d2H=rng.uniform(-25, -10), H3=0.0)
        F = F * (1 - fb)[:, None]
    return F, sig, extra


def observe(F, sig, rng, extra=None, noise=True):
    """True and observed tracers of every sample (dict of arrays) and the true modern-seawater chloride share."""
    c = F * sig['Cl'][None, :]                   # chloride contributions, mg/L
    true = {'Cl': c.sum(1), 'Br': (c * sig['BrCl']).sum(1), 'B': (c * sig['BCl']).sum(1), 'BEX': (c * sig['BEXCl']).sum(1),
            'd18O': (F * sig['d18O']).sum(1), 'd2H': (F * sig['d2H']).sum(1), 'H3': (F * sig['H3']).sum(1)}
    share = c[:, 0] / true['Cl']
    if extra is not None:
        cb = extra['f'] * extra['Cl']
        true['Cl'] = true['Cl'] + cb
        true['Br'] = true['Br'] + cb * extra['BrCl']; true['B'] = true['B'] + cb * extra['BCl']
        true['BEX'] = true['BEX'] + cb * extra['BEXCl']
        for t in ('d18O', 'd2H', 'H3'):
            true[t] = true[t] + extra['f'] * extra[t]
        share = c[:, 0] / true['Cl']
    obs = {}
    for t, v in true.items():
        sd = noise_sd(t, v, true['Cl'])
        obs[t] = v + (rng.standard_normal(v.shape) * sd if noise else 0.0)
    return true, obs, share


def noise_sd(t, value, cl):
    if t == 'BEX':
        return BEX_REL * 2.0716 * np.abs(cl) / 35.453 + BEX_ABS
    rel, ab = NOISE[t]
    return rel * np.abs(value) + ab


def eps_of(t, value, k=2.5, cl=None):
    return k * noise_sd(t, value, cl)


# ---------------------------------------------------------------------------------------------- the identified set
def build_lp(obs_i, tracers, k_eps=2.5, sig=SIG, cap=None):
    """The polytope of Proposition 1 for one sample.  Variables: f (K), c (K) and one block of K contributions for
    every tracer other than Cl.  Returns A_ub, b_ub, A_eq, b_eq, bounds, index map."""
    extra = [t for t in tracers if t != 'Cl']
    nv = 2 * K + K * len(extra)
    idx = {'f': np.arange(K), 'c': K + np.arange(K)}
    for j, t in enumerate(extra):
        idx[t] = 2 * K + j * K + np.arange(K)
    A, b = [], []

    def row():
        return np.zeros(nv)
    lo, hi = sig['Cl'][:, 0], sig['Cl'][:, 1]
    for k in range(K):                           # lo_k f_k <= c_k <= hi_k f_k
        r = row(); r[idx['c'][k]] = 1; r[idx['f'][k]] = -hi[k]; A.append(r); b.append(0.0)
        r = row(); r[idx['c'][k]] = -1; r[idx['f'][k]] = lo[k]; A.append(r); b.append(0.0)
    for t in extra:
        key, kind = KIND[t]
        lo_t, hi_t = sig[key][:, 0], sig[key][:, 1]
        base = idx['c'] if kind == 'cl' else idx['f']
        for k in range(K):
            r = row(); r[idx[t][k]] = 1; r[base[k]] = -hi_t[k]; A.append(r); b.append(0.0)
            r = row(); r[idx[t][k]] = -1; r[base[k]] = lo_t[k]; A.append(r); b.append(0.0)
    for t in tracers:                            # data within +-eps
        e = eps_of(t, obs_i[t], k_eps, obs_i['Cl'])
        cols = idx['c'] if t == 'Cl' else idx[t]
        r = row(); r[cols] = 1; A.append(r); b.append(obs_i[t] + e)
        r = row(); r[cols] = -1; A.append(r); b.append(-(obs_i[t] - e))
    Aeq = np.zeros((1, nv)); Aeq[0, idx['f']] = 1
    beq = np.array([1.0])
    cap = np.ones(K) if cap is None else cap
    bounds = [(0, float(cap[k])) for k in range(K)] + [(0, None)] * K
    for t in extra:
        signed = sig[KIND[t][0]][:, 0].min() < 0
        bounds += [(None, None) if signed else (0, None)] * K
    return np.array(A), np.array(b), Aeq, beq, bounds, idx


def _lp(cvec, A, b, Aeq, beq, bounds):
    r = linprog(cvec, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=bounds, method='highs')
    return r


def feasible(obs_i, tracers, k_eps=2.5, cap=None, sig=SIG):
    A, b, Aeq, beq, bounds, idx = build_lp(obs_i, tracers, k_eps, sig=sig, cap=cap)
    r = _lp(np.zeros(A.shape[1]), A, b, Aeq, beq, bounds)
    return r.status == 0


def share_bounds(obs_i, tracers, src=0, k_eps=2.5, cap=None, sig=SIG):
    """Sharp bounds of the chloride share of source `src`, c_src / sum(c), by the Charnes-Cooper transform.
    Returns (lo, hi) or (nan, nan) when the polytope is empty."""
    A, b, Aeq, beq, bounds, idx = build_lp(obs_i, tracers, k_eps, sig=sig, cap=cap)
    nv = A.shape[1]
    # variables (w, t): A w - b t <= 0, Aeq w - beq t = 0, sum(c of w) = 1, t >= 0; bounds of w as of z (all are 0 or inf)
    A2 = np.c_[A, -b]
    rows = []
    for j, (lo_j, hi_j) in enumerate(bounds):        # finite upper bounds z_j <= u  ->  w_j - u t <= 0
        if hi_j is not None:
            r = np.zeros(nv + 1); r[j] = 1.0; r[-1] = -hi_j; rows.append(r)
    if rows:
        A2 = np.r_[A2, np.array(rows)]
    Aeq2 = np.r_[np.c_[Aeq, -beq], np.r_[np.isin(np.arange(nv), idx['c']).astype(float), 0.0][None, :]]
    beq2 = np.r_[np.zeros(len(beq)), 1.0]
    bounds2 = [(lo_j, None) for lo_j, hi_j in bounds] + [(0, None)]
    out = []
    for sgn in (1.0, -1.0):
        cv = np.zeros(nv + 1); cv[idx['c'][src]] = sgn
        r = _lp(cv, A2, np.zeros(A2.shape[0]), Aeq2, beq2, bounds2)
        if r.status != 0:
            return np.nan, np.nan
        out.append(sgn * r.fun)
    return float(np.clip(out[0], 0, 1)), float(np.clip(out[1], 0, 1))


def fraction_bounds(obs_i, tracers, k_eps=2.5, cap=None, sig=SIG):
    A, b, Aeq, beq, bounds, idx = build_lp(obs_i, tracers, k_eps, sig=sig, cap=cap)
    lo, hi = np.zeros(K), np.zeros(K)
    for k in range(K):
        cv = np.zeros(A.shape[1]); cv[idx['f'][k]] = 1
        r1 = _lp(cv, A, b, Aeq, beq, bounds); r2 = _lp(-cv, A, b, Aeq, beq, bounds)
        if r1.status != 0 or r2.status != 0:
            return None
        lo[k], hi[k] = r1.fun, -r2.fun
    return lo, hi


# ---------------------------------------------------------------------------------------------- sampling an end-member
# measurement error of a sampled end-member: relative for concentrations and ratios, absolute for isotopes and tritium
EM_REL = {'Cl': 0.05, 'BrCl': 0.03, 'BCl': 0.05, 'BEXCl': 0.25}
EM_ABS = {'d18O': 0.15, 'd2H': 1.5, 'H3': 0.05}


def characterised(sig_true, sources):
    """Signature intervals after the listed sources (indices) were sampled: each interval shrinks to the measured value
    +- its measurement error, intersected with the prior interval."""
    S = {k: v.copy() for k, v in SIG.items()}
    for src in sources:
        for key in S:
            v = sig_true[key][src]
            d = EM_REL[key] * abs(v) if key in EM_REL else EM_ABS[key]
            S[key][src] = [max(v - d, SIG[key][src][0]), min(v + d, SIG[key][src][1])]
    return S


# ---------------------------------------------------------------------------------------------- classical point inverse
def point_inverse(obs_i, tracers, cap=None):
    """Non-negative least squares on the simplex with central signatures, each tracer scaled by its error."""
    cen = {k: v.mean(1) for k, v in SIG.items()}
    rows, rhs = [], []
    for t in tracers:
        if t == 'Cl':
            sig_t = cen['Cl']
        else:
            key, kind = KIND[t]
            sig_t = cen[key] * cen['Cl'] if kind == 'cl' else cen[key]
        sd = noise_sd(t, obs_i[t], obs_i['Cl'])
        rows.append(sig_t / sd); rhs.append(obs_i[t] / sd)
    W = 1e3                                      # sum-to-one as a heavily weighted row
    A = np.vstack(rows + [W * np.ones(K)]); y = np.array(rhs + [W])
    f, _ = nnls(A, y)
    c = f * cen['Cl']
    return f, float(c[0] / max(c.sum(), 1e-12))


# ---------------------------------------------------------------------------------------------- amortised neural estimator
def features(obs, tracers):
    cols = []
    cl = np.maximum(obs['Cl'], 1e-3)
    cols.append(np.log10(cl))
    for t in tracers:
        if t == 'Cl':
            continue
        if t == 'BEX':
            cols.append(obs[t] / (cl / 35.453))
        elif KIND[t][1] == 'cl':
            cols.append(np.log10(np.maximum(obs[t], 1e-6) / cl))
        else:
            cols.append(obs[t])
    return np.c_[tuple(cols)]


class QuantileMLP:
    """Two hidden layers (tanh), three outputs passed through a sigmoid: the 5%, 50% and 95% quantiles of the share.
    Trained by Adam on the pinball loss."""
    def __init__(self, d, h=64, seed=0):
        r = np.random.default_rng(seed)
        self.W = [r.standard_normal((d, h)) / np.sqrt(d), r.standard_normal((h, h)) / np.sqrt(h), r.standard_normal((h, 3)) / np.sqrt(h)]
        self.b = [np.zeros(h), np.zeros(h), np.zeros(3)]
        self.tau = np.array([0.05, 0.5, 0.95])

    def _fwd(self, x):
        a1 = np.tanh(x @ self.W[0] + self.b[0]); a2 = np.tanh(a1 @ self.W[1] + self.b[1])
        o = 1 / (1 + np.exp(-(a2 @ self.W[2] + self.b[2])))
        return a1, a2, o

    def predict(self, x):
        x = (x - self.mu) / self.sd
        q = self._fwd(x)[2]
        return np.sort(q, axis=1)

    def fit(self, x, y, epochs=25, batch=256, lr=2e-3, seed=0):
        self.mu, self.sd = x.mean(0), x.std(0) + 1e-9
        x = (x - self.mu) / self.sd
        r = np.random.default_rng(seed)
        params = self.W + self.b
        m = [np.zeros_like(p) for p in params]; v = [np.zeros_like(p) for p in params]
        step = 0
        for ep in range(epochs):
            perm = r.permutation(len(x))
            for i in range(0, len(x), batch):
                j = perm[i:i + batch]; xb, yb = x[j], y[j][:, None]
                a1, a2, o = self._fwd(xb)
                u = yb - o
                dq = -np.where(u >= 0, self.tau, self.tau - 1) / len(j)          # d pinball / d o
                dz3 = dq * o * (1 - o)
                g = [None] * 6
                g[2] = a2.T @ dz3; g[5] = dz3.sum(0)
                da2 = dz3 @ self.W[2].T * (1 - a2 ** 2)
                g[1] = a1.T @ da2; g[4] = da2.sum(0)
                da1 = da2 @ self.W[1].T * (1 - a1 ** 2)
                g[0] = xb.T @ da1; g[3] = da1.sum(0)
                step += 1
                for k, p in enumerate(params):
                    m[k] = 0.9 * m[k] + 0.1 * g[k]; v[k] = 0.999 * v[k] + 0.001 * g[k] ** 2
                    mh = m[k] / (1 - 0.9 ** step); vh = v[k] / (1 - 0.999 ** step)
                    p -= lr * mh / (np.sqrt(vh) + 1e-8)
        return self


def cqr_margin(q, y, alpha=0.10):
    """Split-conformal margin of conformalised quantile regression (Romano, Patterson and Candes, 2019)."""
    s = np.maximum(q[:, 0] - y, y - q[:, 2])
    n = len(s)
    k = int(np.ceil((1 - alpha) * (n + 1)))
    return float(np.sort(s)[min(k, n) - 1])
