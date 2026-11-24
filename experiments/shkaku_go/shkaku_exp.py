"""SHKAKU-GO: counterfactual (rung-3) bands in the stochastic structural causal model of the coastal aquifer.

Structural causal model of the test bed of reviews I-VI (32 cells x 64 weeks):
  exogenous    daily rain P; latent histories z = (sea level, inland inflow, recharge error e, initial head);
               recharge coefficient kappa; vadose delay tau
  mechanisms   f = Erlang-2 filter of P with delay tau;  r = kappa f + e;  h = G z + kappa g(f) + c_Q
The counterfactual question: in these same 64 weeks, what would recharge and the head at the pumping well (1.5 km,
no logger) have been had the rain been P' = T(P) (drought: 0.6 P; late season: rain 30 days later), given the data?
The twin world keeps z, kappa and tau; the recharge error of the twin is e' = rho e + sqrt(1 - rho^2) xi, xi a fresh
draw from the same law (rho = 1: Pearl's shared noise; rho < 1: the coupling across worlds is unknown).
Goals (weekly, 64 values):
  dr  effect on recharge     r' - r = kappa (f' - f) + (e' - e)
  dh  effect on the head     h'_w - h_w = kappa (g(f') - g(f))_w + G_e (e' - e)
  rc  counterfactual recharge r'
  hc  counterfactual head at the well h'_w
Bands (90%, share of weeks outside at most alpha):
  floor     the Neyman-Pearson band of the exact counterfactual law under the real law Q (review VI)
  star      exact posterior under the simulator law P, multiplier set at the population quantile under Q
  sims      the same, multiplier calibrated on 300 simulated twins of the simulator law (model-based guarantee)
  anc20     the same, multiplier calibrated on 20 anchor twins: anchors where the histories and kappa were measured,
            their counterfactual computed with the simulator's mechanism (factual truth + model effect)
  T_sims    exact posterior under the enlarged law (delay unknown, 7-56 d), 300 simulated twins of that law
Real laws Q: none (Q = P), delay (35 d in the field), params (kappa median 0.25, recharge error and inflow x 1.5).
Also: designs from rain only (= the interventional law, rung 2) to 8 loggers (value of abduction); the coupling
study (rho in the field 1, 0.6, 0; a band robust to every rho on a grid); a second counterfactual (late season).

usage: python shkaku_exp.py [quick]   (writes res/shkaku.json and res/shkaku_log.txt)"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'dyshemeja_go'))
import dyshemeja_exp as DX  # noqa: E402
from dyshemeja_exp import AX, M  # noqa: E402

G = AX.G                                          # rain law and vadose filter (garancia_go)
DX.NK = 1201                                      # finer kappa grid: the effects are functions of kappa alone
RES = os.path.join(HERE, 'res')
ALPHA = 0.10
QUICK = len(sys.argv) > 1 and sys.argv[1] == 'quick'
NT = M.NT
IW = M.IW                                         # pumping-well cell (1.5 km); no logger there
GOALS = ('dr', 'dh', 'rc', 'hc')
DELTA = ('dr', 'dh')                              # effects: functions of kappa (and tau) alone when rho = 1
CFS = dict(drought=lambda P: 0.6 * P, late=lambda P: np.roll(P, 30))
LAWS = ('none', 'delay', 'params')
DESIGN4 = DX.DESIGN4
DESIGNS = DX.DESIGNS
RHO_GRID = (0.0, 0.25, 0.5, 0.75, 0.9, 1.0)       # couplings covered by the robust band
RHO_TRUE = (1.0, 0.6, 0.0)
N_SIM, N_Q, N_D = (60, 120, 60) if QUICK else (300, 600, 300)
M_ANC, REPS = 20, 300
TAUS = DX.TAUS
TAU_GRID = 7.0 * 2.0 ** (np.arange(49) / 16.0)          # 7 ... 56 d, ratio 2^(1/16)
LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.append(s)


class Bed(AX.X.Bed):
    """the test bed with the well rows of the head map and a case generator that keeps the exogenous variables."""

    def __init__(self):
        super().__init__()
        self.Gw = self.G[IW * NT:(IW + 1) * NT]                       # (T, NZ) head at the well
        self.cQw = self.cQ[IW * NT:(IW + 1) * NT]
        self.e = np.arange(M.SL['e'].start, M.SL['e'].stop)
        self.Ge = self.Gw[:, self.e]                                   # (T, T) head at the well per unit recharge error
        self.Ce = M.COV['e']
        # the head response to recharge is linear in f (the steady initial head included): g(f) = Kg f
        self.Kg = np.stack([M.kappa_response(np.eye(NT)[j]) for j in range(NT)], 1)     # (NX NT, NT)
        self.Kw = self.Kg[IW * NT:(IW + 1) * NT]

    def case(self, rng, scen='none', tau=None):
        Pd = G.daily_rain(rng)
        if tau is None:
            tau = 35.0 if scen == 'delay' else M.TAU_V
        z = self.mu + self.L @ rng.standard_normal(M.NZ)
        sc = 1.0
        if scen == 'params':
            sc = 1.5
            z[M.SL['e']] *= 1.5
            z[M.SL['dq']] = self.mu[M.SL['dq']] + 1.5 * (z[M.SL['dq']] - self.mu[M.SL['dq']])
        kmed = 0.25 if scen == 'params' else M.KAP_MED
        kap = float(np.exp(np.log(kmed) + M.KAP_LSD * rng.standard_normal()))
        xi = sc * (M.CHOL['e'] @ rng.standard_normal(NT))              # fresh recharge error of the twin
        f = G.filtered(Pd, tau)
        gk = M.kappa_response(f)
        tr = M.fields_from_z(z[:, None], np.array([kap]), f, self.G, self.cQ, gk)
        return dict(Pd=Pd, tau=float(tau), z=z, xi=xi, kappa=kap, f=f, h=tr['h'][0], eta=tr['eta'][0],
                    qL=tr['qL'][0], r=tr['r'][0], eh=M.SIG_H * rng.standard_normal((M.NX, NT)),
                    ee=M.SIG_ETA * rng.standard_normal(NT))

    def well(self, f):
        return self.Kw @ f

    def twin(self, cs, cf, rho, tau=None):
        """the goals in the twin world. tau = None: the case's own delay (the truth); tau = 14 d: the simulator's
        mechanism applied to the factual truth (what an anchor can compute)."""
        tau = cs['tau'] if tau is None else tau
        P1 = CFS[cf](cs['Pd'])
        f0, f1 = G.filtered(cs['Pd'], tau), G.filtered(P1, tau)
        g0, g1 = self.well(f0), self.well(f1)
        e = cs['z'][self.e]
        de = (rho - 1.0) * e + np.sqrt(max(1.0 - rho ** 2, 0.0)) * cs['xi']
        k = cs['kappa']
        dr = k * (f1 - f0) + de
        dh = k * (g1 - g0) + self.Ge @ de
        return dict(dr=dr, dh=dh, rc=cs['r'] + dr, hc=cs['h'][IW] + dh)


def prune(w):
    o = np.argsort(-w.ravel())
    keep = o[:int(np.searchsorted(np.cumsum(w.ravel()[o]), 1 - 1e-9)) + 1]
    return keep


def cf_mix(bed, post, f0, f1, rho, Ce):
    """the counterfactual law of every goal given the data: per goal the component means (T, J), the common
    component sd (T,), the weights (J,) and, for an effect with rho = 1, the slope a (T,) with mean = kappa a."""
    keep = prune(post['w'])
    kap, w = post['kap'][keep], post['w'][keep] / post['w'][keep].sum()
    Mz = post['mz0'][:, None] + post['mz1'][:, None] * kap[None, :]
    S = post['Spost']
    g0, g1 = bed.well(f0), bed.well(f1)
    Me = Mz[bed.e]
    See = S[np.ix_(bed.e, bed.e)]
    s2 = max(1.0 - rho ** 2, 0.0)
    GeSee = bed.Ge @ See
    A_h = bed.Gw.copy(); A_h[:, bed.e] += (rho - 1.0) * bed.Ge
    v = dict(dr=(rho - 1) ** 2 * np.diag(See) + s2 * np.diag(Ce),
             dh=(rho - 1) ** 2 * np.einsum('ij,ij->i', GeSee, bed.Ge) + s2 * np.einsum('ij,jk,ik->i', bed.Ge, Ce, bed.Ge),
             rc=rho ** 2 * np.diag(See) + s2 * np.diag(Ce),
             hc=np.einsum('ij,jk,ik->i', A_h, S, A_h) + s2 * np.einsum('ij,jk,ik->i', bed.Ge, Ce, bed.Ge))
    m = dict(dr=kap[None, :] * (f1 - f0)[:, None] + (rho - 1) * Me,
             dh=kap[None, :] * (g1 - g0)[:, None] + (rho - 1) * (bed.Ge @ Me),
             rc=kap[None, :] * f1[:, None] + rho * Me,
             hc=A_h @ Mz + kap[None, :] * g1[:, None] + bed.cQw[:, None])
    out = {}
    for k in GOALS:
        sd = np.sqrt(np.maximum(v[k], 0.0))
        if k in DELTA and rho == 1.0:
            a = (f1 - f0) if k == 'dr' else (g1 - g0)
            out[k] = dict(m=m[k], s=sd, w=w, kap=kap, dl=post['dl'], a=a)
        else:
            out[k] = dict(m=m[k], s=np.maximum(sd, 1e-12), w=w, kap=kap, dl=post['dl'])
    return out


def mix_moments(d):
    mu = d['m'] @ d['w']
    return mu, np.sqrt(np.maximum(d['s'] ** 2 + (d['m'] ** 2) @ d['w'] - mu ** 2, 0.0))


def rows_density_delta(d):
    """per week: the density of an effect kappa a_t on the kappa grid, sorted decreasingly, with cumulative mass
    and cumulative width (review VI, rows_density, for a goal that is a deterministic function of kappa)."""
    kap, w, dl, a = d['kap'], d['w'], d['dl'], np.maximum(np.abs(d['a']), 1e-12)
    wid = kap[None, :] * dl * a[:, None]                               # (T, J)
    p = w[None, :] / wid
    o = np.argsort(-p, 1)
    D = np.take_along_axis(p, o, 1)
    C = np.cumsum(np.broadcast_to(w, p.shape)[np.arange(p.shape[0])[:, None], o], 1)
    CW = np.cumsum(np.take_along_axis(wid, o, 1), 1)
    return D, C, CW


def rows_density(d, k):
    """per week (D, C, CW) of the Neyman-Pearson construction. A week whose component sd is below 2% of the
    mixture sd is treated as a function of kappa alone (the component means are linear in kappa); otherwise the
    mixture density is evaluated on a grid fine enough to resolve one component."""
    if 'a' in d:
        D, C, CW = rows_density_delta(d)
        return [(D[t], C[t], CW[t]) for t in range(D.shape[0])]
    m, s, w, kap, dl = d['m'], d['s'], d['w'], d['kap'], d['dl']
    mu, sd = mix_moments(d)
    jlo, jhi = int(np.argmin(kap)), int(np.argmax(kap))
    rows = []
    for t in range(m.shape[0]):
        if s[t] < 0.02 * sd[t] and jhi != jlo:
            beta = (m[t, jhi] - m[t, jlo]) / (kap[jhi] - kap[jlo])
            wid = kap * dl * max(abs(beta), 1e-12)
            p = w / wid
            o = np.argsort(-p)
            rows.append((p[o], np.cumsum(w[o]), np.cumsum(wid[o])))
            continue
        ng = int(min(4001, max(DX.NG, np.ceil(14 * sd[t] / (s[t] / 3)))))
        x = mu[t] + sd[t] * np.linspace(-DX.UMAX, DX.UMAX, ng)
        p = (np.exp(-0.5 * ((x[:, None] - m[t][None, :]) / s[t]) ** 2) / (np.sqrt(2 * np.pi) * s[t])) @ w
        dx = sd[t] * 2 * DX.UMAX / (ng - 1)
        D = -np.sort(-p)
        rows.append((D, np.cumsum(D) * dx, dx * np.arange(1, ng + 1)))
    return rows


def add_rows(fl, rows):
    for D, C, CW in rows:
        fl.add(D[None, :], C[None, :], CW[None, :])


def post_T(bed, y, rows, Pd):
    """exact posterior when the vadose delay is unknown too (prior uniform on the fine grid of log delays): a
    mixture over delay x kappa. Only the kappa response changes with the delay, so one factorisation of the data
    covariance serves all delays (review VI, exact_post_T, with the linear map g = Kg f)."""
    from scipy.linalg import cho_factor, cho_solve
    fs = np.array([G.filtered(Pd, t) for t in TAU_GRID])                 # (n_tau, T)
    gks = bed.Kg @ fs.T                                                    # (NX NT, n_tau)
    m = len(rows)
    Hz = np.zeros((m, M.NZ)); c0 = np.zeros(m); Rn = np.zeros(m); hk = np.zeros((m, len(TAU_GRID)))
    for k, (kind, idx) in enumerate(rows):
        if kind == 'h':
            Hz[k] = bed.G[idx]; c0[k] = bed.cQ[idx]; Rn[k] = M.SIG_H ** 2; hk[k] = gks[idx]
        else:
            Hz[k, M.SL['deta'].start + idx] = 1.0; Hz[k, M.SL['meta']] = 1.0; Rn[k] = M.SIG_ETA ** 2
    lgrid = np.log(M.KAP_MED) + M.KAP_LSD * np.linspace(-5, 5, DX.NK)
    kap = np.exp(lgrid)
    logprior = -0.5 * ((lgrid - np.log(M.KAP_MED)) / M.KAP_LSD) ** 2
    if m == 0:
        return dict(kap=kap, w=np.tile(np.exp(logprior - logprior.max()), (len(TAU_GRID), 1)) /
                    (len(TAU_GRID) * np.exp(logprior - logprior.max()).sum()), mz0=bed.mu.copy(),
                    mz1=np.zeros((len(TAU_GRID), M.NZ)), Spost=bed.Sig, fs=fs)
    Cy = Hz @ bed.Sig @ Hz.T + np.diag(Rn)
    cf = cho_factor(Cy)
    K = cho_solve(cf, Hz @ bed.Sig).T
    r0 = y - (Hz @ bed.mu + c0)
    a_ = cho_solve(cf, r0); B = cho_solve(cf, hk)
    ha = hk.T @ a_; hb = np.sum(hk * B, 0)
    logw = logprior[None, :] - 0.5 * (-2 * kap[None, :] * ha[:, None] + kap[None, :] ** 2 * hb[:, None])
    w = np.exp(logw - logw.max()); w /= w.sum()
    return dict(kap=kap, w=w, mz0=bed.mu + K @ r0, mz1=(-K @ hk).T, Spost=bed.Sig - K @ Hz @ bed.Sig, fs=fs)


def cf_moments_T(bed, post, Pd, cf, rho, Ce):
    """mean and sd of every goal under the enlarged law (a mixture over delay x kappa)."""
    w = post['w']; kap = post['kap']
    keep = prune(w)
    ti, kj = np.unravel_index(keep, w.shape)
    ww = w.ravel()[keep] / w.ravel()[keep].sum(); kk = kap[kj]
    Mz = post['mz0'][:, None] + post['mz1'][ti].T * kk[None, :]
    S = post['Spost']
    P1 = CFS[cf](Pd)
    f0s = post['fs']
    f1s = np.zeros_like(f0s)
    for t in np.unique(ti):
        f1s[t] = G.filtered(P1, TAU_GRID[t])
    g0s = f0s @ bed.Kw.T; g1s = f1s @ bed.Kw.T
    Me = Mz[bed.e]
    See = S[np.ix_(bed.e, bed.e)]
    s2 = max(1.0 - rho ** 2, 0.0)
    A_h = bed.Gw.copy(); A_h[:, bed.e] += (rho - 1.0) * bed.Ge
    v = dict(dr=(rho - 1) ** 2 * np.diag(See) + s2 * np.diag(Ce),
             dh=(rho - 1) ** 2 * np.einsum('ij,jk,ik->i', bed.Ge, See, bed.Ge) + s2 * np.einsum('ij,jk,ik->i', bed.Ge, Ce, bed.Ge),
             rc=rho ** 2 * np.diag(See) + s2 * np.diag(Ce),
             hc=np.einsum('ij,jk,ik->i', A_h, S, A_h) + s2 * np.einsum('ij,jk,ik->i', bed.Ge, Ce, bed.Ge))
    m = dict(dr=kk[None, :] * (f1s - f0s)[ti].T + (rho - 1) * Me,
             dh=kk[None, :] * (g1s - g0s)[ti].T + (rho - 1) * (bed.Ge @ Me),
             rc=kk[None, :] * f1s[ti].T + rho * Me,
             hc=A_h @ Mz + kk[None, :] * g1s[ti].T + bed.cQw[:, None])
    out = {}
    for k in GOALS:
        mu = m[k] @ ww
        out[k] = (mu, np.sqrt(np.maximum(v[k] + (m[k] ** 2) @ ww - mu ** 2, 0.0)))
    return out


def score(x, c, s):
    d = np.abs(x - c)
    return np.where(s > 1e-10, d / np.maximum(s, 1e-10), np.where(d < 1e-9, 0.0, np.inf))


def model_bands(bed, cs, rows, y, cfs, rhos=(1.0,), enlarged=True):
    """exact posterior under the simulator law P (delay 14 d, rho as given) and, optionally, the enlarged law:
    the counterfactual mean and sd of every goal."""
    post = DX.exact_post(y, rows, G.filtered(cs['Pd'], M.TAU_V), bed.G, bed.cQ, bed.mu, bed.Sig, M.KAP_MED)
    postT = post_T(bed, y, rows, cs['Pd']) if enlarged else None
    f0 = G.filtered(cs['Pd'], M.TAU_V)
    out = {}
    for cf in cfs:
        f1 = G.filtered(CFS[cf](cs['Pd']), M.TAU_V)
        for rho in rhos:
            mix = cf_mix(bed, post, f0, f1, rho, bed.Ce)
            out[(cf, rho, 'P')] = {k: mix_moments(mix[k]) for k in GOALS}
            if enlarged and rho == 1.0:
                out[(cf, rho, 'T')] = cf_moments_T(bed, postT, cs['Pd'], cf, rho, bed.Ce)
    return out


def real_mix(bed, cs, rows, y, scen, cf, rho):
    """the exact counterfactual law under the real law Q (its prior, its delay, its coupling)."""
    mu, Sig, kmed = DX.law_prior(bed, scen)
    f0 = G.filtered(cs['Pd'], cs['tau'])
    f1 = G.filtered(CFS[cf](cs['Pd']), cs['tau'])
    post = DX.exact_post(y, rows, f0, bed.G, bed.cQ, mu, Sig, kmed)
    Ce = Sig[np.ix_(bed.e, bed.e)]
    return cf_mix(bed, post, f0, f1, rho, Ce)


def scores_of(cases, tw, mom, k):
    return np.array([score(t[k], m[k][0], m[k][1]) for t, m in zip(tw, mom)])


def evaluate(bed, scen, cases, rows, ys, cf, sims, simsT, rs, rho=1.0, with_floor=True):
    """floor, star, sims, anc20 and T_sims for one counterfactual, one real law, one coupling, one design."""
    tw = [bed.twin(cs, cf, rho) for cs in cases]                       # the truth of the twin world
    ta = [bed.twin(cs, cf, 1.0, tau=M.TAU_V) for cs in cases]           # what an anchor can compute
    mom = [model_bands(bed, cs, rows, y, (cf,)) for cs, y in zip(cases, ys)]
    momP = [m[(cf, 1.0, 'P')] for m in mom]
    momT = [m[(cf, 1.0, 'T')] for m in mom]
    floors = {k: DX.Floor(TAUS) for k in GOALS}
    if with_floor:
        for cs, y in zip(cases, ys):
            mix = real_mix(bed, cs, rows, y, scen, cf, rho)
            for k in GOALS:
                add_rows(floors[k], rows_density(mix[k], k))
    res = {}
    for k in GOALS:
        St = scores_of(cases, tw, momP, k)
        Sa = scores_of(cases, ta, momP, k)
        sq = np.array([np.mean(m[k][1]) for m in momP])
        lam_star = float(np.quantile(St.ravel(), 1 - ALPHA))
        r = dict(star=dict(halfwidth=float(lam_star * sq.mean()), lam=lam_star))
        if with_floor:
            r['floor'] = floors[k].solve()
        Ss = sims[k]
        lam_s = AX.crc_exact(Ss, Ss[:0], 1.0)
        r['sims'] = dict(halfwidth=float(lam_s * sq.mean()), risk=AX.realized(St, lam_s), lam=float(lam_s))
        StT = scores_of(cases, tw, momT, k)
        sT = np.array([np.mean(m[k][1]) for m in momT])
        lam_T = AX.crc_exact(simsT[k], simsT[k][:0], 1.0)
        r['T_sims'] = dict(halfwidth=float(lam_T * sT.mean()), risk=AX.realized(StT, lam_T), lam=float(lam_T))
        n = len(cases)
        rk, hw = [], []
        for _ in range(REPS):
            p = rs.permutation(n); ai, ti = p[:M_ANC], p[M_ANC:]
            lam = AX.crc_exact(Sa[:0], Sa[ai], 0.0)
            rk.append(AX.realized(St[ti], lam)); hw.append(lam * sq[ti].mean())
        r['anc20'] = dict(risk=float(np.mean(rk)), halfwidth=float(np.mean(hw)))
        res[k] = r
    return res


def sim_scores(bed, cases, rows, cfs, rhos=(1.0,), enlarged=False):
    """scores of the simulated twins (the calibration data of the model-based guarantee)."""
    out = {}
    for cs in cases:
        y = bed.data(cs, rows)
        mom = model_bands(bed, cs, rows, y, cfs, rhos, enlarged)
        for cf in cfs:
            for rho in rhos:
                tw = bed.twin(cs, cf, rho)
                key = (cf, rho, 'T' if enlarged else 'P')
                for k in GOALS:
                    out.setdefault((cf, rho), {}).setdefault(k, []).append(score(tw[k], *mom[key][k]))
    return {key: {k: np.array(v) for k, v in d.items()} for key, d in out.items()}


def coupling(bed, cases, rows, ys, cf, simsR, rs):
    """rho in the field 1, 0.6, 0: the shared-noise band (rho = 1), the band calibrated with the right rho and the
    band robust to every rho on RHO_GRID (the union of the rho-calibrated bands; 0.6 is off the grid)."""
    rhos = tuple(sorted(set(RHO_GRID) | set(RHO_TRUE)))
    mom = [model_bands(bed, cs, rows, y, (cf,), rhos, enlarged=False) for cs, y in zip(cases, ys)]
    lam = {rho: {k: AX.crc_exact(simsR[(cf, rho)][k], simsR[(cf, rho)][k][:0], 1.0) for k in GOALS} for rho in rhos}
    out = {}
    for rt in RHO_TRUE:
        tw = [bed.twin(cs, cf, rt) for cs in cases]
        floors = {k: DX.Floor(TAUS) for k in GOALS}
        for cs, y in zip(cases, ys):
            mix = real_mix(bed, cs, rows, y, 'none', cf, rt)
            for k in GOALS:
                add_rows(floors[k], rows_density(mix[k], k))
        res = {}
        for k in GOALS:
            r = dict(floor=floors[k].solve())
            X_ = np.array([t[k] for t in tw])
            for tag, rho in (('shared', 1.0), ('right', rt)):
                c = np.array([m[(cf, rho, 'P')][k][0] for m in mom]); s = np.array([m[(cf, rho, 'P')][k][1] for m in mom])
                r[tag] = dict(halfwidth=float(lam[rho][k] * s.mean()), risk=AX.realized(score(X_, c, s), lam[rho][k]))
            lo = np.min([[m[(cf, rho, 'P')][k][0] - lam[rho][k] * m[(cf, rho, 'P')][k][1] for rho in RHO_GRID]
                         for m in mom], axis=1)
            hi = np.max([[m[(cf, rho, 'P')][k][0] + lam[rho][k] * m[(cf, rho, 'P')][k][1] for rho in RHO_GRID]
                         for m in mom], axis=1)
            r['robust'] = dict(halfwidth=float(np.mean(hi - lo) / 2), risk=float(np.mean((X_ < lo) | (X_ > hi))))
            res[k] = r
        out[str(rt)] = res
    return out


def main():
    t0 = time.time()
    os.makedirs(RES, exist_ok=True)
    bed = Bed()
    rng = np.random.default_rng(2207)
    rs = np.random.default_rng(2208)
    rows4 = bed.rows(DESIGN4)
    out = dict(alpha=ALPHA, n_sim=N_SIM, n_q=N_Q, n_d=N_D, m_anc=M_ANC, reps=REPS, rho_grid=RHO_GRID,
               rho_true=RHO_TRUE, cf={}, designs={}, coupling={})
    sim_cases = [bed.case(rng) for _ in range(N_SIM)]
    simsP = sim_scores(bed, sim_cases, rows4, tuple(CFS), tuple(sorted(set(RHO_GRID) | set(RHO_TRUE))))
    simT_cases = [bed.case(rng, tau=float(np.exp(rng.uniform(np.log(TAU_GRID[0]), np.log(TAU_GRID[-1])))))
                  for _ in range(N_SIM)]
    simsT = sim_scores(bed, simT_cases, rows4, tuple(CFS), (1.0,), enlarged=True)
    log(f'simulated twins ready [{time.time() - t0:.0f}s]')
    for cf, laws in (('drought', LAWS), ('late', ('none', 'delay'))):
        out['cf'][cf] = {}
        for scen in laws:
            cases = [bed.case(rng, scen) for _ in range(N_Q)]
            ys = [bed.data(cs, rows4) for cs in cases]
            R = evaluate(bed, scen, cases, rows4, ys, cf, simsP[(cf, 1.0)], simsT[(cf, 1.0)], rs)
            out['cf'][cf][scen] = R
            for k in GOALS:
                v = R[k]; fl = v['floor']['halfwidth']
                log(f'{cf:7s} {scen:6s} {k}: floor {fl:.4g} | star {v["star"]["halfwidth"] / fl:.2f} | '
                    f'sims {v["sims"]["halfwidth"] / fl:.2f} ({v["sims"]["risk"]:.3f}) | anc20 '
                    f'{v["anc20"]["halfwidth"] / fl:.2f} ({v["anc20"]["risk"]:.3f}) | T_sims '
                    f'{v["T_sims"]["halfwidth"] / fl:.2f} ({v["T_sims"]["risk"]:.3f})  [{time.time() - t0:.0f}s]')
    cases = [bed.case(rng, 'none') for _ in range(N_Q)]
    ys = [bed.data(cs, rows4) for cs in cases]
    out['coupling'] = coupling(bed, cases, rows4, ys, 'drought', simsP, rs)
    for rt, R in out['coupling'].items():
        log(f'coupling rho={rt}: ' + ' | '.join(
            f'{k} floor {R[k]["floor"]["halfwidth"]:.4g} shared {R[k]["shared"]["halfwidth"] / R[k]["floor"]["halfwidth"]:.2f}'
            f'({R[k]["shared"]["risk"]:.3f}) right {R[k]["right"]["halfwidth"] / R[k]["floor"]["halfwidth"]:.2f}'
            f'({R[k]["right"]["risk"]:.3f}) robust {R[k]["robust"]["halfwidth"] / R[k]["floor"]["halfwidth"]:.2f}'
            f'({R[k]["robust"]["risk"]:.3f})' for k in GOALS) + f'  [{time.time() - t0:.0f}s]')
    dcases = [bed.case(rng, 'none') for _ in range(N_D)]
    for name, des in DESIGNS.items():
        rows = bed.rows(des)
        ys = [bed.data(cs, rows) for cs in dcases]
        fl = {k: DX.Floor(TAUS) for k in GOALS}
        for cs, y in zip(dcases, ys):
            mix = real_mix(bed, cs, rows, y, 'none', 'drought', 1.0)
            for k in GOALS:
                add_rows(fl[k], rows_density(mix[k], k))
        out['designs'][name] = {k: dict(floor=fl[k].solve()) for k in GOALS}
        log(f'{name:18s} ' + ' | '.join(f'{k} floor {out["designs"][name][k]["floor"]["halfwidth"]:.4g}'
                                        for k in GOALS) + f'  [{time.time() - t0:.0f}s]')
    out['seconds'] = time.time() - t0
    tag = '_quick' if QUICK else ''
    with open(os.path.join(RES, f'shkaku{tag}.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    with open(os.path.join(RES, f'shkaku{tag}_log.txt'), 'w') as fh:
        fh.write('\n'.join(LOG) + '\n')
    log(f'done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
