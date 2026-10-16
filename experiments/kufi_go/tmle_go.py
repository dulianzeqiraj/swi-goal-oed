"""TMLE-GO (extended copy for KUFI-GO: threshold regimes 'dyn@x', per-well thresholds, pumped volume,
influence curves returned): targeted estimation of the salinization risk of pumping wells under pumping regimes,
from observational well-field records with reviews at irregular (continuous) times.

Physics: the KRAMERS-GO toe model (kramers2.py). For well i the Strack toe X = x_toe/d relaxes as
    dX/dt = (mu_i / r - F(X; lam(t) / r)) / tau,   r = exp(eps - s^2/2),  eps an OU recharge process,
lam(t) = f(A(t)) * lam_crit, with A(t) = 1 (high pumping, f_hi) or 0 (low pumping, f_lo).
Salinization: X reaches 0.98 (absorbing). Outcome Y = 1{salinized by H}.

Observation and decision process (continuous time):
  reviews at the jump times of a Poisson process (rate RHO per year, at most JMAX), plus t = 0;
  at review j the operator reads the toe (X + noise SIG_OP) and sees the drought index D_j (mean eps
  over the past half year); the well may leave the monitoring programme (informative censoring,
  more likely when the reading is high); otherwise the operator sets the pumping status A_j:
      logit P(A_j = 1) = B0 + B1 (2 A_{j-1} - 1) - B2 (R_j - 0.65)/0.05 - B3 D_j / s + BW W.
  Drought raises both the pumping and the salinization risk: time-varying confounding, and pumping
  moves the toe that drives later decisions (treatment-confounder feedback).

Targets: psi_d = E[Y^{d, no censoring}] for regimes d acting at the reviews:
  'hi' always high, 'lo' always low, 'dyn' high until a toe reading exceeds XSTAR, then low for good.

Estimators (sequential regression over the review index j, i.e. over the jump times):
  naive, IPW (Hajek), ICE g-computation and TMLE, each with a misspecified or a flexible outcome
  model; influence-curve standard errors for TMLE.
"""
import os
import sys
import numpy as np
from scipy.optimize import brentq
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kramers_go'))   # kramers2.py
import kramers2 as KR

P = dict(KR.P0); P['s'] = 0.30
MU = KR.mu_of(P); LC = KR.lam_crit(MU)
F_LO, F_HI, F_PRE = 0.80, 0.95, 0.85
H, DT = 8.0, 0.02
NT = int(round(H / DT))
RHO, JMAX = 1.0, 16
SIG_OP, SIG_PRECISE = 0.02, 0.005          # toe reading noise (x d = 2000 m: 40 m and 10 m)
BURN = 0.5                                  # drought index window [yr]
B0, B1, B2, B3, BW = 0.0, 2.2, 0.4, 0.8, 0.3
A0W, A0D = 0.4, 0.9                         # initial decision
C0, C1 = -3.5, 0.5                          # monitoring drop-out at a review
WMU = 0.04                                  # well heterogeneity: mu_i = MU exp(WMU W)
XSTAR = 0.72
REGIMES = ('hi', 'lo', 'dyn')

_mu_grid = MU * np.exp(WMU * np.linspace(-3.2, 3.2, 161))
_x0_grid = np.array([brentq(lambda X: KR.F(X, F_PRE * LC) - m, 1e-9, np.sqrt(1 - F_PRE * LC)) for m in _mu_grid])


def expit(z):
    return 1.0 / (1.0 + np.exp(-z))


def regime_action(reg, Rmax):
    """Rmax: largest toe reading of the well so far (the 'dyn' rule switches to low pumping for good
    once a reading exceeds XSTAR)."""
    if reg == 'hi':
        return np.ones_like(Rmax)
    if reg == 'lo':
        return np.zeros_like(Rmax)
    x = float(reg.split('@')[1]) if '@' in reg else XSTAR     # 'dyn@0.70': threshold 0.70
    return (Rmax <= x).astype(float)


def simulate(n, rng, regime=None):
    """Simulate n wells. regime None = observational (operator policy and drop-out);
    otherwise the regime sets A at every review and nobody drops out.
    Returns a dict of (n, JMAX+1) node arrays and outcomes."""
    s, th = P['s'], P['theta']
    W = np.clip(rng.standard_normal(n), -3, 3)
    mu = MU * np.exp(WMU * W)
    X = np.interp(mu, _mu_grid, _x0_grid)
    # recharge: stationary OU, with a burn-in window so D_0 is defined
    nb = int(round(BURN / DT)); a = np.exp(-DT / th); b = s * np.sqrt(1 - a * a)
    eps = s * rng.standard_normal(n); win = np.empty((n, nb))
    for k in range(nb):
        eps = a * eps + b * rng.standard_normal(n); win[:, k] = eps
    # review steps: t = 0 plus Poisson(RHO) jump times on (0, H), at most JMAX of them
    steps = np.full((n, JMAX + 1), NT + 1, int); steps[:, 0] = 0
    for i in range(n):
        m = rng.poisson(RHO * H)
        tt = np.sort(rng.uniform(0, H, m))[:JMAX]
        st = np.unique(np.maximum(1, np.round(tt / DT).astype(int)))
        st = st[st < NT]
        steps[i, 1:1 + len(st)] = st
    J = JMAX + 1
    out = {k: np.full((n, J), np.nan) for k in ('t', 'R', 'Rp', 'D', 'A', 'Aprev')}
    reach = np.zeros((n, J), bool); cens = np.zeros((n, J), bool)
    ev = np.zeros((n, J), bool); nxt = np.zeros((n, J), bool)
    alive = np.ones(n, bool); inprog = np.ones(n, bool)       # not salinized / still monitored
    A = np.zeros(n); Aprev = np.zeros(n); jcur = np.full(n, -1); Rmax = np.full(n, -np.inf); vol = np.zeros(n)
    nextj = np.zeros(n, int)                                   # index of next review
    wpos = 0
    for k in range(NT + 1):
        # review?
        isrev = alive & (nextj <= JMAX) & (steps[np.arange(n), np.minimum(nextj, JMAX)] == k)
        if isrev.any():
            idx = np.nonzero(isrev)[0]; j = nextj[idx]
            if regime is None:
                obs = idx[inprog[idx]]
            else:
                obs = idx
            # node j reached (if still in the programme)
            jo = nextj[obs]
            if len(obs):
                prev = jcur[obs]; has = prev >= 0
                nxt[obs[has], prev[has]] = True
                reach[obs, jo] = True
                Dj = win.mean(axis=1)[obs]
                R = X[obs] + SIG_OP * rng.standard_normal(len(obs))
                Rp = X[obs] + SIG_PRECISE * rng.standard_normal(len(obs))
                out['t'][obs, jo] = k * DT; out['R'][obs, jo] = R; out['Rp'][obs, jo] = Rp
                out['D'][obs, jo] = Dj
                Rmax[obs] = np.maximum(Rmax[obs], R)
                ap = np.where(jo == 0, 0.0, 2 * Aprev[obs] - 1)
                out['Aprev'][obs, jo] = ap
                if regime is None:
                    c = (jo > 0) & (rng.random(len(obs)) < expit(C0 + C1 * (R - 0.65) / 0.05))
                    cens[obs[c], jo[c]] = True; inprog[obs[c]] = False
                    lo = np.where(jo == 0, A0W * W[obs] - A0D * Dj / s,
                                  B0 + B1 * ap - B2 * (R - 0.65) / 0.05 - B3 * Dj / s + BW * W[obs])
                    newA = (rng.random(len(obs)) < expit(lo)).astype(float)
                    keep = ~c
                    A[obs[keep]] = newA[keep]
                else:
                    if isinstance(regime, np.ndarray):          # per-well thresholds (randomized experiment)
                        A[obs] = (Rmax[obs] <= regime[obs]).astype(float)
                    else:
                        A[obs] = regime_action(regime, Rmax[obs])
                out['A'][obs, jo] = np.where(cens[obs, jo], np.nan, A[obs])
                Aprev[obs] = A[obs]; jcur[obs] = jo
            nextj[idx] += 1
        if k == NT:
            break
        # dynamics
        fq = np.where(A > 0.5, F_HI, F_LO); vol += DT * fq * alive / H
        lam = fq * LC
        r = np.exp(eps - 0.5 * s * s)
        x = X + DT * (mu / r - KR.F(X, lam / r)) / P['tau']
        x = np.maximum(x, KR.XLO)
        hit = alive & (x >= KR.XESC)
        if hit.any():
            hi_ = np.nonzero(hit)[0]
            mon = hi_[inprog[hi_]] if regime is None else hi_
            ev[mon, jcur[mon]] = True
        alive &= ~hit
        X = np.where(alive, x, KR.XESC)
        eps = a * eps + b * rng.standard_normal(n)
        win[:, wpos % nb] = eps; wpos += 1
    Y = (~alive).astype(float)
    out['Rmax'] = np.fmax.accumulate(np.where(np.isnan(out['R']), -np.inf, out['R']), axis=1)
    return dict(vol=vol, W=W, reach=reach, cens=cens, ev=ev, nxt=nxt, Y=Y, inprog=inprog, **out)


# ------------------------------------------------------------------ estimation
def logit_fit(Xm, y, w=None, ridge=1e-6, it=50):
    """(quasi-)binomial logistic regression by IRLS; y in [0, 1]."""
    n, p = Xm.shape; w = np.ones(n) if w is None else w
    beta = np.zeros(p)
    for _ in range(it):
        eta = np.clip(Xm @ beta, -30, 30); m = expit(eta)
        Wd = w * m * (1 - m) + 1e-12
        g = Xm.T @ (w * (y - m)) - ridge * beta
        Hs = (Xm * Wd[:, None]).T @ Xm + ridge * np.eye(p)
        step = np.linalg.solve(Hs, g); beta += step
        if np.max(np.abs(step)) < 1e-9:
            break
    return beta


def feats(d, j, idx, kind, design):
    """design: which variables were recorded at the reviews."""
    t = d['t'][idx, j]; W = d['W'][idx]; ap = d['Aprev'][idx, j]
    cols = [np.ones(len(idx))]
    tox = d['R'][idx, j] if design in ('op', 'op+D') else d['Rp'][idx, j]
    hasD = design.endswith('+D')
    Dv = d['D'][idx, j] / P['s'] if hasD else None
    if kind == 'mis':
        cols += [H - t]
    elif kind == 'g':
        cols += [ap, (tox - 0.65) / 0.05, W] + ([Dv] if hasD else [])
    elif kind == 'g0':
        cols += [W, (tox - 0.65) / 0.05] + ([Dv] if hasD else [])
    elif kind == 'c':
        cols += [(tox - 0.65) / 0.05]
    else:   # flexible outcome model
        z = (tox - 0.65) / 0.05; u = H - t
        cols += [z, z * z, u, z * u, W, np.log(u + 0.05)]
        if hasD:
            cols += [Dv, Dv * u, Dv * z]
    return np.column_stack(cols)


def fit_nuisance(d, design):
    """treatment model at t = 0, pooled treatment model over the later reviews, pooled drop-out model."""
    n, J = d['reach'].shape
    rows_g, ys_g, rows_c, ys_c = [], [], [], []
    for j in range(1, J):
        r = np.nonzero(d['reach'][:, j])[0]
        if len(r) == 0:
            continue
        unc = r[~d['cens'][r, j]]
        rows_g.append(feats(d, j, unc, 'g', design)); ys_g.append(d['A'][unc, j])
        rows_c.append(feats(d, j, r, 'c', design)); ys_c.append(d['cens'][r, j].astype(float))
    all0 = np.arange(n)
    bg0 = logit_fit(feats(d, 0, all0, 'g0', design), d['A'][:, 0])
    bg = logit_fit(np.vstack(rows_g), np.concatenate(ys_g))
    bc = logit_fit(np.vstack(rows_c), np.concatenate(ys_c))
    return bg0, bg, bc


def estimate(d, reg, design='op+D', kinds=('mis', 'flex'), nuis=None, gbound=0.01, return_ic=False):
    n, J = d['reach'].shape
    bg0, bg, bc = fit_nuisance(d, design) if nuis is None else nuis
    tox_name = 'R' if design in ('op', 'op+D') else 'Rp'
    # regime actions are defined on the operator's reading R (dyn regime) -- R must be recorded for 'dyn'
    # cumulative weights and follower indicators
    follow = np.zeros((n, J), bool); wcum = np.zeros((n, J))
    fprev = np.ones(n, bool); wprev = np.ones(n)
    for j in range(J):
        r = np.nonzero(d['reach'][:, j])[0]
        if len(r) == 0:
            break
        gq = expit(feats(d, j, r, 'g0', design) @ bg0) if j == 0 else expit(feats(d, j, r, 'g', design) @ bg)
        gq = np.clip(gq, gbound, 1 - gbound)
        cq = expit(feats(d, j, r, 'c', design) @ bc) if j > 0 else np.zeros(len(r))
        dj = regime_action(reg, d['Rmax'][r, j])
        Aobs = d['A'][r, j]
        ok = fprev[r] & ~d['cens'][r, j] & (Aobs == dj)
        pd = np.where(dj > 0.5, gq, 1 - gq) * (1 - cq)
        follow[r, j] = ok
        wcum[r, j] = wprev[r] / pd
        fprev = np.zeros(n, bool); fprev[r[ok]] = True
        wprev = np.zeros(n); wprev[r] = wcum[r, j]
    res = {}
    # naive and IPW: wells that followed d at all their reached nodes and were never censored
    lastj = np.where(d['reach'], np.arange(J)[None, :], -1).max(axis=1)
    fin = follow[np.arange(n), lastj]
    res['naive'] = float(d['Y'][fin].mean())
    wf = wcum[np.arange(n), lastj] * fin
    res['ipw'] = float(np.sum(wf * d['Y']) / np.sum(wf))
    for kind in kinds:
        for tm in (False, True):
            Qn = np.zeros(n)                      # Q*_{j+1} at the wells reaching node j+1
            IC = np.zeros(n)
            for j in range(J - 1, -1, -1):
                r = np.nonzero(d['reach'][:, j])[0]
                if len(r) == 0:
                    continue
                V = np.where(d['ev'][r, j], 1.0, np.where(d['nxt'][r, j], Qn[r], 0.0))
                fm = follow[r, j]
                Xr = feats(d, j, r, kind, design)
                if fm.sum() < 10 * Xr.shape[1]:          # too few followers for this model: smaller one
                    Xr = feats(d, j, r, 'mis', design)
                if fm.sum() >= 5:
                    beta = logit_fit(Xr[fm], V[fm])
                    q0 = np.clip(expit(Xr @ beta), 1e-6, 1 - 1e-6)
                else:
                    q0 = np.full(len(r), np.clip(V[fm].mean() if fm.any() else 0.5, 1e-6, 1 - 1e-6))
                if tm and fm.any():
                    off = np.log(q0 / (1 - q0)); wv = wcum[r, j][fm]; e = 0.0
                    for _ in range(50):
                        m = expit(off[fm] + e)
                        g1 = np.sum(wv * (V[fm] - m)); h1 = np.sum(wv * m * (1 - m)) + 1e-12
                        e += g1 / h1
                        if abs(g1 / h1) < 1e-10:
                            break
                    q = expit(off + e)
                else:
                    q = q0
                IC[r] += np.where(fm, wcum[r, j] * (V - q), 0.0)
                Qn = np.zeros(n); Qn[r] = q
            psi = float(Qn.mean())
            IC += Qn - psi
            key = ('tmle_' if tm else 'gcomp_') + kind
            res[key] = psi
            if tm:
                res['se_' + kind] = float(IC.std() / np.sqrt(n))
                if return_ic:
                    res['ic_' + kind] = IC
    return res


def truth(reg, n, rng, chunk=50000, with_vol=False):
    ys, vs = [], []
    for k in range(0, n, chunk):
        d = simulate(min(chunk, n - k), rng, regime=reg); ys.append(d['Y']); vs.append(d['vol'])
    y = float(np.concatenate(ys).mean())
    return (y, float(np.concatenate(vs).mean())) if with_vol else y
