"""Identified sets for chloride-source attribution with general tracers (the field form of ZANAFILLA-GO).

A source k mixes into a sample with water fraction f_k.  Its chloride concentration Cl_k and the signatures of the
other tracers are known only as intervals.  Each tracer t has
  - a mixing class: 'w' (mixes by water, e.g. d18O, d2H, tritium: y_t = sum_k f_k s_tk) or
    'cl' (a ratio to chloride, e.g. Br/Cl: y_t = sum_k f_k Cl_k r_tk);
  - a side: 'two' (conservative: |sum - y| <= eps), 'gain' (the aquifer may add the tracer after mixing, e.g. iodide
    from marine sediments: the sources supply at most y + eps) or 'loss' (the aquifer may remove it, e.g. boron by
    sorption: the sources supply at least y - eps);
  - observations that may be censored ('<' detection limit: 0 <= sum <= DL + eps).
Signatures of two water-class tracers of one source may be coupled by a linear relation with an interval constant
(the deuterium excess d = d2H - 8 d18O), which keeps the set a polytope (perspective of a polytope).

With c_k = f_k Cl_k and one contribution variable per source and tracer, the identified set is an exact polytope;
sharp bounds of the chloride share phi_k = c_k / sum_j c_j follow from linear programmes after the Charnes-Cooper
transform.  The module also holds the two comparators of the paper: fixed signatures (IsoSource-type ranges) and a
Bayesian mixing model with a Dirichlet prior and signatures uniform in their intervals (importance sampling)."""
import numpy as np
from scipy.optimize import linprog
from scipy.stats import norm


class Model:
    """sources: list of names; cl: K x 2 chloride intervals (mg/L); tracers: dict t -> dict(cls, side, sig (K x 2));
    joint: list of dict(a, b, coef, lo (K), hi (K)) meaning lo_k <= s_ak - coef * s_bk <= hi_k."""

    def __init__(self, sources, cl, tracers, joint=()):
        self.sources = list(sources)
        self.K = len(self.sources)
        self.cl = np.asarray(cl, float)
        self.tr = {t: dict(v, sig=np.asarray(v['sig'], float)) for t, v in tracers.items()}
        self.joint = [dict(j, lo=np.asarray(j['lo'], float), hi=np.asarray(j['hi'], float)) for j in joint]

    def fixed(self, values):
        """A copy with degenerate intervals at the given values (dict: 'Cl' -> K, t -> K); missing ones at midpoints."""
        cl = np.asarray(values.get('Cl', self.cl.mean(1)), float)
        tr = {}
        for t, v in self.tr.items():
            x = np.asarray(values.get(t, v['sig'].mean(1)), float)
            tr[t] = dict(v, sig=np.c_[x, x])
        joint = []          # fixed isotopes make the coupling redundant
        return Model(self.sources, np.c_[cl, cl], tr, joint)

    def with_interval(self, key, k, lo, hi):
        """A copy in which the interval of tracer `key` ('Cl' or a tracer) for source k is replaced."""
        cl = self.cl.copy()
        tr = {t: dict(v, sig=v['sig'].copy()) for t, v in self.tr.items()}
        if key == 'Cl':
            cl[k] = [lo, hi]
        else:
            tr[key]['sig'][k] = [lo, hi]
        return Model(self.sources, cl, tr, self.joint)


# --------------------------------------------------------------------------------------------- the polytope
def build_lp(m, obs, tset, eps, cap=None):
    """obs: dict t -> (value, cens); eps: dict t -> tolerance.  tset: tracers used ('Cl' always first).
    Returns A_ub, b_ub, A_eq, b_eq, bounds, idx."""
    K = m.K
    extra = [t for t in tset if t != 'Cl']
    nv = 2 * K + K * len(extra)
    idx = {'f': np.arange(K), 'c': K + np.arange(K)}
    for j, t in enumerate(extra):
        idx[t] = 2 * K + j * K + np.arange(K)
    A, b = [], []

    def add(coefs, rhs):
        r = np.zeros(nv)
        for col, val in coefs:
            r[col] += val
        A.append(r); b.append(rhs)

    for k in range(K):                                   # Cl_lo f <= c <= Cl_hi f
        add([(idx['c'][k], 1.0), (idx['f'][k], -m.cl[k, 1])], 0.0)
        add([(idx['c'][k], -1.0), (idx['f'][k], m.cl[k, 0])], 0.0)
    for t in extra:                                      # signature intervals, scaled by the mixing variable
        tr = m.tr[t]
        base = idx['c'] if tr['cls'] == 'cl' else idx['f']
        for k in range(K):
            lo, hi = tr['sig'][k]
            add([(idx[t][k], 1.0), (base[k], -hi)], 0.0)
            add([(idx[t][k], -1.0), (base[k], lo)], 0.0)
    for j in m.joint:                                    # coupled signatures: lo f <= v_a - coef v_b <= hi f
        if j['a'] in extra and j['b'] in extra:
            for k in range(K):
                add([(idx[j['a']][k], 1.0), (idx[j['b']][k], -j['coef']), (idx['f'][k], -j['hi'][k])], 0.0)
                add([(idx[j['a']][k], -1.0), (idx[j['b']][k], j['coef']), (idx['f'][k], j['lo'][k])], 0.0)
    for t in tset:                                       # the data
        y, cens = obs[t]
        e = eps[t]
        cols = idx['c'] if t == 'Cl' else idx[t]
        side = 'two' if t == 'Cl' else m.tr[t]['side']
        if cens == '<':
            lo, hi = -e, y + e
        else:
            lo, hi = y - e, y + e
        if side in ('two', 'gain'):
            add([(c, 1.0) for c in cols], hi)
        if side in ('two', 'loss'):
            add([(c, -1.0) for c in cols], -lo)
    Aeq = np.zeros((1, nv)); Aeq[0, idx['f']] = 1.0
    beq = np.array([1.0])
    cap = np.ones(K) if cap is None else np.asarray(cap, float)
    bounds = [(0.0, float(cap[k])) for k in range(K)] + [(0.0, None)] * K
    for t in extra:
        signed = m.tr[t]['sig'][:, 0].min() < 0
        bounds += [(None, None) if signed else (0.0, None)] * K
    return np.array(A), np.array(b), Aeq, beq, bounds, idx


def _solve(cvec, A, b, Aeq, beq, bounds):
    return linprog(cvec, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=bounds, method='highs')


def feasible(m, obs, tset, eps, cap=None):
    A, b, Aeq, beq, bounds, _ = build_lp(m, obs, tset, eps, cap)
    return _solve(np.zeros(A.shape[1]), A, b, Aeq, beq, bounds).status == 0


def share_bounds(m, obs, tset, eps, cap=None):
    """Sharp bounds of the chloride share of every source (K x 2), or None when the polytope is empty."""
    A, b, Aeq, beq, bounds, idx = build_lp(m, obs, tset, eps, cap)
    nv = A.shape[1]
    if _solve(np.zeros(nv), A, b, Aeq, beq, bounds).status != 0:
        return None
    # Charnes-Cooper: z = w / t with t = 1 / sum(c): A w - b t <= 0, Aeq w - beq t = 0, sum(c of w) = 1, t >= 0
    A2 = np.c_[A, -b]
    rows = []
    for j, (lo_j, hi_j) in enumerate(bounds):
        if hi_j is not None:
            r = np.zeros(nv + 1); r[j] = 1.0; r[-1] = -hi_j; rows.append(r)
    A2 = np.r_[A2, np.array(rows)]
    sel = np.zeros(nv + 1); sel[idx['c']] = 1.0
    Aeq2 = np.r_[np.c_[Aeq, -beq], sel[None, :]]
    beq2 = np.r_[np.zeros(len(beq)), 1.0]
    bounds2 = [(lo_j, None) for lo_j, _ in bounds] + [(0.0, None)]
    out = np.zeros((m.K, 2))
    for k in range(m.K):
        for s, sgn in ((0, 1.0), (1, -1.0)):
            cv = np.zeros(nv + 1); cv[idx['c'][k]] = sgn
            r = _solve(cv, A2, np.zeros(A2.shape[0]), Aeq2, beq2, bounds2)
            if r.status != 0:
                return None
            out[k, s] = sgn * r.fun
    return np.clip(out, 0.0, 1.0)


def fraction_bounds(m, obs, tset, eps):
    A, b, Aeq, beq, bounds, idx = build_lp(m, obs, tset, eps)
    out = np.zeros((m.K, 2))
    for k in range(m.K):
        for s, sgn in ((0, 1.0), (1, -1.0)):
            cv = np.zeros(A.shape[1]); cv[idx['f'][k]] = sgn
            r = _solve(cv, A, b, Aeq, beq, bounds)
            if r.status != 0:
                return None
            out[k, s] = sgn * r.fun
    return out


# --------------------------------------------------------------------------------------------- Bayesian comparator
def sample_prior(m, n, alpha, rng):
    """f ~ Dirichlet(alpha); signatures uniform in their intervals, coupled ones uniform on the coupled box
    (rejection).  Returns dict with 'f' (n x K), 'Cl' (n x K) and one n x K array per tracer."""
    K = m.K
    out = {'f': rng.dirichlet(np.full(K, alpha) if np.isscalar(alpha) else np.asarray(alpha), size=n)}
    out['Cl'] = rng.uniform(m.cl[:, 0], m.cl[:, 1], size=(n, K))
    for t, v in m.tr.items():
        out[t] = rng.uniform(v['sig'][:, 0], v['sig'][:, 1], size=(n, K))
    for j in m.joint:
        a, bb = j['a'], j['b']
        for k in range(K):
            bad = np.ones(n, bool)
            lo_a, hi_a = m.tr[a]['sig'][k]
            for _ in range(200):
                if not bad.any():
                    break
                nb = bad.sum()
                sb = rng.uniform(*m.tr[bb]['sig'][k], size=nb)
                d = rng.uniform(j['lo'][k], j['hi'][k], size=nb)
                sa = d + j['coef'] * sb
                ok = (sa >= lo_a) & (sa <= hi_a)
                ii = np.where(bad)[0][ok]
                out[a][ii, k] = sa[ok]; out[bb][ii, k] = sb[ok]
                bad[ii] = False
    return out


def mixture(m, P, t):
    if t == 'Cl':
        return (P['f'] * P['Cl']).sum(1)
    if m.tr[t]['cls'] == 'w':
        return (P['f'] * P[t]).sum(1)
    return (P['f'] * P['Cl'] * P[t]).sum(1)


def log_lik(m, P, obs, tset, sd):
    """Gaussian error with the same sides and censoring as the polytope (probit for one-sided and censored data)."""
    ll = np.zeros(len(P['f']))
    for t in tset:
        y, cens = obs[t]
        mu = mixture(m, P, t)
        s = sd[t]
        side = 'two' if t == 'Cl' else m.tr[t]['side']
        if cens == '<':
            ll += norm.logcdf((y - mu) / s)
        elif side == 'two':
            ll += -0.5 * ((y - mu) / s) ** 2
        elif side == 'gain':                    # y = mu + gain + noise, gain >= 0
            ll += norm.logcdf((y - mu) / s)
        else:                                   # loss
            ll += norm.logcdf((mu - y) / s)
    return ll


def posterior_shares(m, P, obs, tset, sd, q=(0.05, 0.95)):
    """Weighted mean, quantiles of the chloride shares and the effective sample size."""
    ll = log_lik(m, P, obs, tset, sd)
    w = np.exp(ll - ll.max())
    w /= w.sum()
    ess = 1.0 / np.sum(w ** 2)
    c = P['f'] * P['Cl']
    phi = c / c.sum(1, keepdims=True)
    res = np.zeros((m.K, 3))
    for k in range(m.K):
        o = np.argsort(phi[:, k])
        cw = np.cumsum(w[o])
        res[k, 0] = np.sum(w * phi[:, k])
        res[k, 1] = phi[o, k][np.searchsorted(cw, q[0])]
        res[k, 2] = phi[o, k][min(np.searchsorted(cw, q[1]), len(o) - 1)]
    return res, ess, w


# --------------------------------------------------------------------------------------------- SMC sampler
def _sig(u):
    return 0.5 * (1.0 + np.tanh(0.5 * u))


class _Param:
    """Unconstrained parameterisation of (f, Cl, signatures) for the tracers in tset: additive log-ratio for f,
    logit for every bounded quantity; a coupled pair (a = coef * b + d) is parameterised by b and d."""

    def __init__(self, m, tset, cap=None):
        self.m, self.K = m, m.K
        self.extra = [t for t in tset if t != 'Cl']
        self.cap = None if cap is None else np.asarray(cap, float)
        self.pairs = [j for j in m.joint if j['a'] in self.extra and j['b'] in self.extra]
        self.coupled = {j['a']: j for j in self.pairs}
        self.blocks = [('Cl', m.cl)]
        for t in self.extra:
            if t in self.coupled:
                j = self.coupled[t]
                self.blocks.append((t, np.c_[j['lo'], j['hi']]))      # the constant d of the pair
            else:
                self.blocks.append((t, m.tr[t]['sig']))
        self.dim = (self.K - 1) + self.K * len(self.blocks)

    def forward(self, th):
        """theta (N x dim) -> dict of arrays, log prior without the Dirichlet term, validity mask."""
        K = self.K
        z = th[:, :K - 1]
        zmax = np.maximum(z.max(1, keepdims=True), 0.0)
        e = np.exp(z - zmax)
        den = e.sum(1, keepdims=True) + np.exp(-zmax)
        f = np.c_[e / den, np.exp(-zmax) / den]
        out = {'f': f}
        lj = np.zeros(len(th))
        pos = K - 1
        for name, iv in self.blocks:
            u = th[:, pos:pos + K]
            sg = _sig(u)
            out[name] = iv[:, 0] + (iv[:, 1] - iv[:, 0]) * sg
            lj += np.sum(np.log(np.maximum(sg * (1 - sg), 1e-300)), axis=1)
            pos += K
        ok = np.ones(len(th), bool)
        for t, j in self.coupled.items():
            d = out[t]
            val = j['coef'] * out[j['b']] + d
            lo, hi = self.m.tr[t]['sig'][:, 0], self.m.tr[t]['sig'][:, 1]
            ok &= np.all((val >= lo) & (val <= hi), axis=1)
            out[t] = val
        if self.cap is not None:
            ok &= np.all(f <= self.cap[None, :] + 1e-12, axis=1)
        return out, lj, ok

    def inverse(self, P):
        """Exact prior draws (dict from sample_prior) -> theta."""
        K = self.K
        f = np.maximum(P['f'], 1e-300)
        th = [np.log(f[:, :K - 1]) - np.log(f[:, K - 1:K])]
        for name, iv in self.blocks:
            if name in self.coupled:
                j = self.coupled[name]
                x = P[name] - j['coef'] * P[j['b']]
            else:
                x = P[name]
            q = np.clip((x - iv[:, 0]) / np.maximum(iv[:, 1] - iv[:, 0], 1e-300), 1e-12, 1 - 1e-12)
            th.append(np.log(q) - np.log1p(-q))
        return np.concatenate(th, axis=1)


def smc_posterior(m, obs, tset, sd, alpha, rng, N=3000, moves=6, cap=None, target=0.5, max_stages=400):
    """Posterior of the mixing model (Dirichlet(alpha) prior on f, restricted by cap; signatures uniform in their
    intervals; the likelihood of log_lik) by adaptive tempering with random-walk Metropolis moves.
    Returns (dict of particle arrays at temperature 1, number of stages, mean acceptance)."""
    par = _Param(m, tset, cap)
    # exact prior draws with cap rejection
    P = sample_prior(m, N, alpha, rng)
    if cap is not None:
        bad = ~np.all(P['f'] <= np.asarray(cap)[None, :] + 1e-12, axis=1)
        tries = 0
        while bad.any() and tries < 400:
            Q = sample_prior(m, int(bad.sum()) * 4 + 16, alpha, rng)
            okq = np.all(Q['f'] <= np.asarray(cap)[None, :] + 1e-12, axis=1)
            ii = np.where(bad)[0]
            jj = np.where(okq)[0][:len(ii)]
            for k in P:
                P[k][ii[:len(jj)]] = Q[k][jj]
            bad[ii[:len(jj)]] = False
            tries += 1
    th = par.inverse(P)

    def evaluate(theta):
        X, lj, ok = par.forward(theta)
        lp = alpha * np.sum(np.log(np.maximum(X['f'], 1e-300)), axis=1) + lj
        lp = np.where(ok, lp, -np.inf)
        ll = np.where(ok, log_lik(m, X, obs, tset, sd), -np.inf)
        return X, lp, ll

    X, lp, ll = evaluate(th)
    beta, stages, acc_all = 0.0, 0, []
    scale = 2.38 / np.sqrt(par.dim)
    while beta < 1.0 and stages < max_stages:
        stages += 1
        dl = np.where(np.isfinite(ll), ll, -1e300)
        lo_b, hi_b = 0.0, 1.0 - beta
        def ess_of(db):
            lw = db * dl
            w = np.exp(lw - lw.max())
            return w.sum() ** 2 / np.sum(w ** 2)
        if ess_of(hi_b) >= target * N:
            db = hi_b
        else:
            for _ in range(50):
                mid = 0.5 * (lo_b + hi_b)
                if ess_of(mid) >= target * N:
                    lo_b = mid
                else:
                    hi_b = mid
            db = max(lo_b, 1e-12)
        beta = min(1.0, beta + db)
        lw = db * dl
        w = np.exp(lw - lw.max()); w /= w.sum()
        # systematic resampling
        u = (rng.uniform() + np.arange(N)) / N
        idx = np.minimum(np.searchsorted(np.cumsum(w), u), N - 1)
        th, lp, ll = th[idx], lp[idx], ll[idx]
        cov = np.cov(th.T) + 1e-8 * np.eye(par.dim)
        try:
            L = np.linalg.cholesky(cov)
        except np.linalg.LinAlgError:
            L = np.diag(np.sqrt(np.diag(cov)))
        n_mv = moves if beta < 1.0 else 3 * moves
        for _ in range(n_mv):
            prop = th + scale * rng.standard_normal(th.shape) @ L.T
            _, lp2, ll2 = evaluate(prop)
            cur = lp + beta * np.where(np.isfinite(ll), ll, -np.inf)
            new = lp2 + beta * np.where(np.isfinite(ll2), ll2, -np.inf)
            a = np.log(rng.uniform(size=N)) < (new - cur)
            th[a], lp[a], ll[a] = prop[a], lp2[a], ll2[a]
            rate = a.mean(); acc_all.append(rate)
            scale *= np.exp(0.6 * (rate - 0.25))
    X, _, _ = par.forward(th)
    return X, stages, float(np.mean(acc_all)) if acc_all else float('nan')


def shares_of(X):
    c = X['f'] * X['Cl']
    return c / c.sum(1, keepdims=True)


def summarise_shares(phi, q=(0.05, 0.95)):
    """mean, q05, q95 per source (K x 3) of equally weighted particles."""
    return np.c_[phi.mean(0), np.quantile(phi, q[0], axis=0), np.quantile(phi, q[1], axis=0)]
