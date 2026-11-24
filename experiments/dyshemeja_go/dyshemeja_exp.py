"""DYSHEMEJA-GO: the floor of any valid band, and how far the calibrated bands of reviews I-V sit above it.

For a goal x_w (weeks w = 1..T) and data y, the exact posterior under the real law Q is a mixture over the recharge
coefficient kappa of Gaussians (test bed of reviews I-V: 32 cells x 64 weeks, four loggers). Among all bands whose
expected share of weeks outside is at most alpha under Q, the narrowest on average is the Neyman-Pearson band
{x : p_w(x | y) >= tau} with one threshold tau for all weeks and cases (Proposition F1). This script computes:
  floor      the Neyman-Pearson band, tau set so that the average miscoverage is exactly alpha
  central    the central 90% posterior interval of every week (conditional coverage 0.90)
  exact-z    exact posterior mean +- lambda* x posterior sd, lambda* the population quantile under Q
  ens*       the ensemble reconstructor's band m +- lambda* s, lambda* the population quantile under Q
Population quantities are Rao-Blackwellised: the truth of each field case is replaced by 40 draws per week from its
exact posterior under Q, which leaves every expected risk unchanged and removes most of the sampling noise.
  sims       m +- lambda s with lambda calibrated on 300 simulated aquifers (review I)
  anchors    m +- lambda s with lambda calibrated on m = 10, 20, 40 anchors (review IV), 300 draws
  exact-P    the exact posterior under the simulator's law P (Rao-Blackwellised reconstructor) as centre and scale,
             calibrated on simulations or on 20 anchors
  exact-T    the exact posterior under an enlarged simulator law in which the vadose delay is unknown too (prior
             log-uniform on 7-56 d, posterior on a grid of 7 values), calibrated on simulations drawn from that
             enlarged law or on 20 anchors
Real laws: none (Q = P), delay (35 d in the field), params (kappa median 0.25, recharge error and inflow x 1.5).
Designs (law none): rain only, 1, 2, 4, 8 loggers, 4 loggers + tide gauge.

usage: python dyshemeja_exp.py   (writes res/dyshemeja.json and res/dyshemeja_log.txt)"""
import json
import os
import sys
import time

import numpy as np
from scipy.linalg import cho_factor, cho_solve

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ankora_go'))
import ankora_exp as AX  # noqa: E402
from ankora_exp import M, X  # noqa: E402

RES = os.path.join(HERE, 'res')
ALPHA = 0.10
GOALS = AX.GOALS                      # r, qL, eta, kappa
LAWS = ('none', 'delay', 'params')
DESIGNS = {'rain only': (), '1 logger': ('L3',), '2 loggers': ('L3', 'L7'), '4 loggers': ('L0', 'L2', 'L4', 'L6'),
           '8 loggers': tuple(f'L{j}' for j in range(8)), '4 loggers + gauge': ('L0', 'L2', 'L4', 'L6', 'TG')}
DESIGN4 = ('L0', 'L2', 'L4', 'L6')
N_SIM, N_Q, N_D = 300, 600, 300
MS = (10, 20, 40)
REPS = 300
NG, NK, UMAX = 301, 241, 7.0
TAUS = np.exp(np.linspace(np.log(1e-3), np.log(1e6), 4000))   # thresholds (density units of every goal)
TAU_GRID = 7.0 * 2.0 ** (np.arange(7) / 2.0)                      # 7 ... 56 d
NPS = 40                                                         # posterior draws per week (Rao-Blackwellised risk)
LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.append(s)


def law_prior(bed, scen):
    Sig = bed.Sig.copy()
    if scen == 'params':
        for k in ('e', 'dq'):
            sl = M.SL[k]
            Sig[sl, sl] *= 2.25
    return bed.mu.copy(), Sig, (0.25 if scen == 'params' else M.KAP_MED)


def exact_post(y, rows, f, Gm, cQ, mu, Sig, kmed):
    """exact posterior of the test bed given the rain f and the data y: a mixture over a log-kappa grid of Gaussians
    in the latent z (as rgo_model.exact_posterior, with the kappa median as an argument)."""
    gk = M.kappa_response(f)
    m = len(rows)
    Hz = np.zeros((m, M.NZ)); hk = np.zeros(m); c0 = np.zeros(m); Rn = np.zeros(m)
    for k, (kind, idx) in enumerate(rows):
        if kind == 'h':
            Hz[k] = Gm[idx]; hk[k] = gk[idx]; c0[k] = cQ[idx]; Rn[k] = M.SIG_H ** 2
        else:
            Hz[k, M.SL['deta'].start + idx] = 1.0; Hz[k, M.SL['meta']] = 1.0; Rn[k] = M.SIG_ETA ** 2
    dl = M.KAP_LSD * 10.0 / (NK - 1)
    lgrid = np.log(kmed) + M.KAP_LSD * np.linspace(-5, 5, NK)
    kap = np.exp(lgrid)
    logprior = -0.5 * ((lgrid - np.log(kmed)) / M.KAP_LSD) ** 2
    if m == 0:
        logw = logprior; Spost = Sig; mz0 = mu.copy(); mz1 = np.zeros(M.NZ)
    else:
        Cy = Hz @ Sig @ Hz.T + np.diag(Rn)
        cf = cho_factor(Cy)
        K = cho_solve(cf, Hz @ Sig).T
        r0 = y - (Hz @ mu + c0)
        a_ = cho_solve(cf, r0); b_ = cho_solve(cf, hk)
        logw = logprior - 0.5 * (-2 * kap * (hk @ a_) + kap ** 2 * (hk @ b_))
        Spost = Sig - K @ Hz @ Sig
        mz0 = mu + K @ r0; mz1 = -K @ hk
    w = np.exp(logw - logw.max()); w /= w.sum()
    return dict(kap=kap, w=w, dl=dl, mz0=mz0, mz1=mz1, Spost=Spost)


def exact_post_T(y, rows, Pd, Gm, cQ, mu, Sig, kmed):
    """exact posterior when the vadose delay is unknown too: a mixture over (delay grid) x (log-kappa grid). Only
    the kappa response changes with the delay, so one factorisation of the data covariance serves all delays."""
    m = len(rows)
    fs = [M.SM.erlang2(Pd, t)[M.SPIN:].reshape(M.NT, 7).mean(1) for t in TAU_GRID]
    gks = [M.kappa_response(f) for f in fs]
    Hz = np.zeros((m, M.NZ)); c0 = np.zeros(m); Rn = np.zeros(m); idxs = []
    for k, (kind, idx) in enumerate(rows):
        if kind == 'h':
            Hz[k] = Gm[idx]; c0[k] = cQ[idx]; Rn[k] = M.SIG_H ** 2; idxs.append(idx)
        else:
            Hz[k, M.SL['deta'].start + idx] = 1.0; Hz[k, M.SL['meta']] = 1.0; Rn[k] = M.SIG_ETA ** 2; idxs.append(-1)
    idxs = np.array(idxs, dtype=int)
    lgrid = np.log(kmed) + M.KAP_LSD * np.linspace(-5, 5, NK)
    kap = np.exp(lgrid)
    logprior = -0.5 * ((lgrid - np.log(kmed)) / M.KAP_LSD) ** 2
    if m == 0:
        Spost, mz0 = Sig, mu.copy()
        mz1 = [np.zeros(M.NZ) for _ in TAU_GRID]
        logw = np.array([logprior for _ in TAU_GRID])
    else:
        Cy = Hz @ Sig @ Hz.T + np.diag(Rn)
        cf = cho_factor(Cy)
        K = cho_solve(cf, Hz @ Sig).T
        r0 = y - (Hz @ mu + c0)
        a_ = cho_solve(cf, r0)
        Spost = Sig - K @ Hz @ Sig
        mz0 = mu + K @ r0
        mz1, logw = [], []
        for gk in gks:
            hk = np.where(idxs >= 0, gk[np.maximum(idxs, 0)], 0.0)
            b_ = cho_solve(cf, hk)
            logw.append(logprior - 0.5 * (-2 * kap * (hk @ a_) + kap ** 2 * (hk @ b_)))
            mz1.append(-K @ hk)
        logw = np.array(logw)
    w = np.exp(logw - logw.max()); w /= w.sum()                       # (n_tau, NK)
    return dict(kap=kap, w=w, mz0=mz0, mz1=np.array(mz1), Spost=Spost, fs=np.array(fs))


def moments_T(post):
    """posterior mean and sd of every goal under the enlarged law."""
    w = post['w']; kap = post['kap']
    flat = w.ravel()
    o = np.argsort(-flat)
    keep = o[:int(np.searchsorted(np.cumsum(flat[o]), 1 - 1e-9)) + 1]
    ti, kj = np.unravel_index(keep, w.shape)
    ww = flat[keep] / flat[keep].sum(); kk = kap[kj]
    Mz = post['mz0'][:, None] + post['mz1'][ti].T * kk[None, :]       # (NZ, J)
    S = post['Spost']; dg = np.diag(S)
    e, d, q = M.SL['e'], M.SL['deta'], M.SL['dq']
    mi, qi = M.SL['meta'].start, M.SL['mq'].start
    comp = dict(r=(post['fs'][ti].T * kk[None, :] + Mz[e], np.sqrt(dg[e])),
                eta=(Mz[d] + Mz[mi][None, :], np.sqrt(dg[d] + 2 * S[d, mi] + S[mi, mi])),
                qL=(Mz[q] + Mz[qi][None, :], np.sqrt(dg[q] + 2 * S[q, qi] + S[qi, qi])))
    out = {}
    for k, (m_, s_) in comp.items():
        mu_ = m_ @ ww
        out[k] = (mu_, np.sqrt(s_ ** 2 + (m_ ** 2) @ ww - mu_ ** 2))
    muk = float(np.sum(ww * kk))
    out['kappa'] = (np.array([muk]), np.array([np.sqrt(np.sum(ww * (kk - muk) ** 2))]))
    return out


def marginals(post, f):
    """per goal: component means (T, J), component sd (T,), weights (J,) of the weekly posterior mixtures; kappa as
    the grid itself."""
    o = np.argsort(-post['w'])
    keep = o[:int(np.searchsorted(np.cumsum(post['w'][o]), 1 - 1e-9)) + 1]
    kap, w = post['kap'][keep], post['w'][keep] / post['w'][keep].sum()
    Mz = post['mz0'][:, None] + post['mz1'][:, None] * kap[None, :]
    S = post['Spost']; dg = np.diag(S)
    e, d, q = M.SL['e'], M.SL['deta'], M.SL['dq']
    mi, qi = M.SL['meta'].start, M.SL['mq'].start
    out = dict(r=(kap[None, :] * f[:, None] + Mz[e], np.sqrt(np.maximum(dg[e], 1e-30)), w),
               eta=(Mz[d] + Mz[mi][None, :], np.sqrt(np.maximum(dg[d] + 2 * S[d, mi] + S[mi, mi], 1e-30)), w),
               qL=(Mz[q] + Mz[qi][None, :], np.sqrt(np.maximum(dg[q] + 2 * S[q, qi] + S[qi, qi], 1e-30)), w))
    out['kappa'] = (post['kap'], post['w'], post['dl'])
    return out


def rows_density(mg, goal):
    """for each week: the posterior density on a grid sorted in decreasing order (D), the cumulative mass (C) and
    the cumulative width (CW) in that order; plus the posterior mean and sd and the central 90% half-width."""
    if goal == 'kappa':
        kap, w, dl = mg
        dk = kap * dl
        p = w / dk
        o = np.argsort(-p)
        D = p[o][None, :]; C = np.cumsum(w[o])[None, :]; CW = np.cumsum(dk[o])[None, :]
        mu = float(np.sum(w * kap)); sd = float(np.sqrt(np.sum(w * (kap - mu) ** 2)))
        cdf = np.cumsum(w)
        lo, hi = kap[np.searchsorted(cdf, 0.05)], kap[min(np.searchsorted(cdf, 0.95), len(kap) - 1)]
        return D, C, CW, np.array([mu]), np.array([sd]), np.array([(hi - lo) / 2])
    m, s, w = mg
    mu = m @ w
    sd = np.sqrt(s ** 2 + (m ** 2) @ w - mu ** 2)
    u = np.linspace(-UMAX, UMAX, NG)
    x = mu[:, None] + sd[:, None] * u[None, :]                         # (T, G)
    z = (x[:, :, None] - m[:, None, :]) / s[:, None, None]             # (T, G, J)
    p = (np.exp(-0.5 * z ** 2) / (np.sqrt(2 * np.pi) * s[:, None, None])) @ w
    dx = (sd * 2 * UMAX / (NG - 1))[:, None]
    cdf = np.cumsum(p, 1) * dx
    lo = np.array([x[t, np.searchsorted(cdf[t], 0.05)] for t in range(len(mu))])
    hi = np.array([x[t, min(np.searchsorted(cdf[t], 0.95), NG - 1)] for t in range(len(mu))])
    D = -np.sort(-p, 1)
    C = np.cumsum(D, 1) * dx
    CW = np.cumsum(np.broadcast_to(dx, D.shape), 1)
    return D, C, CW, mu, sd, (hi - lo) / 2


class Floor:
    """accumulates, on a grid of thresholds tau, the summed miscoverage and width of the Neyman-Pearson sets."""

    def __init__(self, taus):
        self.taus = taus; self.mis = np.zeros(len(taus)); self.wid = np.zeros(len(taus)); self.n = 0

    def add(self, D, C, CW):
        for t in range(D.shape[0]):
            asc = D[t][::-1]
            cnt = D.shape[1] - np.searchsorted(asc, self.taus, side='left')
            mass = np.where(cnt > 0, C[t][np.maximum(cnt - 1, 0)], 0.0)
            wid = np.where(cnt > 0, CW[t][np.maximum(cnt - 1, 0)], 0.0)
            self.mis += 1.0 - np.minimum(mass, 1.0); self.wid += wid; self.n += 1

    def solve(self, alpha=ALPHA):
        mis, wid = self.mis / self.n, self.wid / self.n
        j = int(np.searchsorted(mis, alpha))                           # mis increases with tau
        j = min(max(j, 1), len(mis) - 1)
        a = (alpha - mis[j - 1]) / (mis[j] - mis[j - 1] + 1e-300)
        return dict(halfwidth=float((wid[j - 1] + a * (wid[j] - wid[j - 1])) / 2), tau=float(self.taus[j]),
                    miscoverage=float(mis[j - 1] + a * (mis[j] - mis[j - 1])))


def moments(mg, goal):
    if goal == 'kappa':
        kap, w, _ = mg
        mu = float(np.sum(w * kap))
        return np.array([mu]), np.array([np.sqrt(np.sum(w * (kap - mu) ** 2))])
    m, s, w = mg
    mu = m @ w
    return mu, np.sqrt(s ** 2 + (m ** 2) @ w - mu ** 2)


def run_design(bed, cases, design):
    """ensemble reconstructor (reviews I-V) and exact posterior under the simulator's law P for every case."""
    rows = bed.rows(design)
    out = []
    for cs in cases:
        y = bed.data(cs, rows)
        rec = bed.reconstruct_r(cs, rows, y, 0.0)
        t = dict(eta=cs['eta'], qL=cs['qL'], r=cs['r'], kappa=np.array([cs['kappa']]))
        postP = exact_post(y, rows, cs['fo'], bed.G, bed.cQ, bed.mu, bed.Sig, M.KAP_MED)
        mgP = marginals(postP, cs['fo'])
        mom = {k: moments(mgP[k], k) for k in GOALS}
        momT = moments_T(exact_post_T(y, rows, cs['Po'], bed.G, bed.cQ, bed.mu, bed.Sig, M.KAP_MED))
        out.append(dict(t=t, m={k: rec[k][0] for k in GOALS}, s={k: rec[k][1] for k in GOALS}, y=y,
                        mP={k: mom[k][0] for k in GOALS}, sP={k: mom[k][1] for k in GOALS},
                        mT={k: momT[k][0] for k in GOALS}, sT={k: momT[k][1] for k in GOALS}))
    return out, rows


def scores_P(cases, k, tag='P'):
    return np.array([np.abs(c['t'][k] - c['m' + tag][k]) / c['s' + tag][k] for c in cases])


def case_T(bed, rng):
    """a simulated aquifer of the enlarged law: as the simulator's, with the vadose delay log-uniform on 7-56 d."""
    tau = float(np.exp(rng.uniform(np.log(TAU_GRID[0]), np.log(TAU_GRID[-1]))))
    cs = bed.case_q(rng, 'none')
    f = AX.G.filtered(cs['Po'], tau)
    gk = M.kappa_response(f)
    # rebuild the truth with the drawn delay from a fresh latent draw
    zz = bed.mu + bed.L @ rng.standard_normal(M.NZ)
    kap = np.exp(np.log(M.KAP_MED) + M.KAP_LSD * rng.standard_normal())
    tr = M.fields_from_z(zz[:, None], np.array([kap]), f, bed.G, bed.cQ, gk)
    cs.update(f=f, kappa=kap, h=tr['h'][0], eta=tr['eta'][0], qL=tr['qL'][0], r=tr['r'][0])
    return cs


def post_draws(mg, goal, rng, n=NPS):
    """n draws per week from the exact posterior: (T, n)."""
    if goal == 'kappa':
        kap, w, _ = mg
        return kap[rng.choice(len(kap), size=(1, n), p=w)]
    m, s, w = mg
    j = rng.choice(len(w), size=(m.shape[0], n), p=w)
    return np.take_along_axis(m, j, 1) + s[:, None] * rng.standard_normal((m.shape[0], n))


def evaluate(bed, scen, field, rows, sims=None, ms=MS, rs=None, simsT=None):
    """floor, central, exact-z, ens*, sims and anchor bands for one real law and one design."""
    mu, Sig, kmed = law_prior(bed, scen)
    floors = {k: Floor(TAUS) for k in GOALS}
    cen = {k: [] for k in GOALS}
    sdx = {k: [] for k in GOALS}
    rb_ex = {k: [] for k in GOALS}
    rb_en = {k: [] for k in GOALS}
    rb_P = {k: [] for k in GOALS}
    rb_T = {k: [] for k in GOALS}
    rd = np.random.default_rng(4242)
    for cs, rec in field:
        post = exact_post(rec['y'], rows, cs['f'], bed.G, bed.cQ, mu, Sig, kmed)
        mg = marginals(post, cs['f'])
        for k in GOALS:
            D, C, CW, pm, psd, ce = rows_density(mg[k], k)
            floors[k].add(D, C, CW)
            cen[k].append(ce); sdx[k].append(psd)
            xd = post_draws(mg[k], k, rd)
            rb_ex[k].append((np.abs(xd - pm[:, None]) / psd[:, None]).astype(np.float32))
            mk, sk = np.atleast_1d(rec['m'][k]), np.atleast_1d(rec['s'][k])
            rb_en[k].append((np.abs(xd - mk[:, None]) / sk[:, None]).astype(np.float32))
            rb_P[k].append((np.abs(xd - rec['mP'][k][:, None]) / rec['sP'][k][:, None]).astype(np.float32))
            rb_T[k].append((np.abs(xd - rec['mT'][k][:, None]) / rec['sT'][k][:, None]).astype(np.float32))
    res = {}
    for k in GOALS:
        floor = floors[k].solve()
        Rex, Ren = np.array(rb_ex[k]), np.array(rb_en[k])          # (n, T, NPS)
        lam_ex = float(np.quantile(Rex.ravel(), 1 - ALPHA))
        lam_en = float(np.quantile(Ren.ravel(), 1 - ALPHA))
        sq = np.array([np.mean(rec['s'][k]) for _, rec in field])
        Sq = AX.scores([rec for _, rec in field], k)
        RP = np.array(rb_P[k])
        lam_P = float(np.quantile(RP.ravel(), 1 - ALPHA))
        sP = np.array([np.mean(rec['sP'][k]) for _, rec in field])
        SP = scores_P([rec for _, rec in field], k)
        r = dict(floor=floor, central=dict(halfwidth=float(np.mean(cen[k]))),
                 exact_z=dict(halfwidth=float(lam_ex * np.mean(sdx[k])), lam=lam_ex),
                 ens_star=dict(halfwidth=float(lam_en * sq.mean()), lam=lam_en),
                 exactP_star=dict(halfwidth=float(lam_P * sP.mean()), lam=lam_P))
        RT = np.array(rb_T[k])
        lam_T = float(np.quantile(RT.ravel(), 1 - ALPHA))
        sT = np.array([np.mean(rec['sT'][k]) for _, rec in field])
        ST = scores_P([rec for _, rec in field], k, 'T')
        r['exactT_star'] = dict(halfwidth=float(lam_T * sT.mean()), lam=lam_T)
        if sims is not None:
            Ss = AX.scores(sims, k)
            lam_s = AX.crc_exact(Ss, Ss[:0], 1.0)
            r['sims'] = dict(halfwidth=float(lam_s * sq.mean()), risk=AX.realized(Sq, lam_s),
                             risk_rb=float(np.mean(Ren > lam_s)), lam=float(lam_s))
            SsP = scores_P(sims, k)
            lam_sP = AX.crc_exact(SsP, SsP[:0], 1.0)
            r['exactP_sims'] = dict(halfwidth=float(lam_sP * sP.mean()), risk=AX.realized(SP, lam_sP),
                                    risk_rb=float(np.mean(RP > lam_sP)), lam=float(lam_sP))
        if simsT is not None:
            SsT = scores_P(simsT, k, 'T')
            lam_sT = AX.crc_exact(SsT, SsT[:0], 1.0)
            r['exactT_sims'] = dict(halfwidth=float(lam_sT * sT.mean()), risk=AX.realized(ST, lam_sT),
                                    risk_rb=float(np.mean(RT > lam_sT)), lam=float(lam_sT))
        n = len(field)
        for m in ms:
            rk, hw, lm = [], [], []
            for _ in range(REPS):
                p = rs.permutation(n); ai, ti = p[:m], p[m:]
                lam = AX.crc_exact(Sq[:0], Sq[ai], 0.0)
                rk.append(AX.realized(Sq[ti], lam)); hw.append(lam * sq[ti].mean()); lm.append(lam)
            r[f'm{m}'] = dict(risk=float(np.mean(rk)), halfwidth=float(np.mean(hw)), lam=float(np.mean(lm)))
            if m == 20:
                rk, hw = [], []
                for _ in range(REPS):
                    p = rs.permutation(n); ai, ti = p[:m], p[m:]
                    lam = AX.crc_exact(SP[:0], SP[ai], 0.0)
                    rk.append(AX.realized(SP[ti], lam)); hw.append(lam * sP[ti].mean())
                r['exactP_m20'] = dict(risk=float(np.mean(rk)), halfwidth=float(np.mean(hw)))
                rk, hw = [], []
                for _ in range(REPS):
                    p = rs.permutation(n); ai, ti = p[:m], p[m:]
                    lam = AX.crc_exact(ST[:0], ST[ai], 0.0)
                    rk.append(AX.realized(ST[ti], lam)); hw.append(lam * sT[ti].mean())
                r['exactT_m20'] = dict(risk=float(np.mean(rk)), halfwidth=float(np.mean(hw)))
        res[k] = r
    return res


def main():
    t0 = time.time()
    os.makedirs(RES, exist_ok=True)
    bed = AX.QBed()
    rng = np.random.default_rng(1606)
    rs = np.random.default_rng(1707)
    out = dict(alpha=ALPHA, n_sim=N_SIM, n_q=N_Q, n_d=N_D, ms=MS, reps=REPS, ng=NG, nk=NK, laws={}, designs={})
    sim_cases = [bed.case(rng, 'true') for _ in range(N_SIM)]
    sims4, rows4 = run_design(bed, sim_cases, DESIGN4)
    simT_cases = [case_T(bed, rng) for _ in range(N_SIM)]
    simsT4, _ = run_design(bed, simT_cases, DESIGN4)
    log(f'simulations ready [{time.time() - t0:.0f}s]')
    for scen in LAWS:
        cases = [bed.case_q(rng, scen) for _ in range(N_Q)]
        field, _ = run_design(bed, cases, DESIGN4)
        out['laws'][scen] = evaluate(bed, scen, list(zip(cases, field)), rows4, sims=sims4, rs=rs, simsT=simsT4)
        for k in GOALS:
            v = out['laws'][scen][k]
            log(f'{scen:7s} {k:5s} floor {v["floor"]["halfwidth"]:.4f} (mis {v["floor"]["miscoverage"]:.3f}) '
                f'central {v["central"]["halfwidth"]:.4f} exact-z {v["exact_z"]["halfwidth"]:.4f} '
                f'ens* {v["ens_star"]["halfwidth"]:.4f} sims {v["sims"]["halfwidth"]:.4f}/{v["sims"]["risk"]:.3f} '
                f'm20 {v["m20"]["halfwidth"]:.4f}/{v["m20"]["risk"]:.3f} | exactP* {v["exactP_star"]["halfwidth"]:.4f} '
                f'exactP sims {v["exactP_sims"]["halfwidth"]:.4f}/{v["exactP_sims"]["risk"]:.3f} '
                f'exactP m20 {v["exactP_m20"]["halfwidth"]:.4f}/{v["exactP_m20"]["risk"]:.3f} | exactT* '
                f'{v["exactT_star"]["halfwidth"]:.4f} exactT sims {v["exactT_sims"]["halfwidth"]:.4f}/'
                f'{v["exactT_sims"]["risk"]:.3f} exactT m20 {v["exactT_m20"]["halfwidth"]:.4f}/{v["exactT_m20"]["risk"]:.3f}'
                f'  [{time.time() - t0:.0f}s]')
    dcases = [bed.case_q(rng, 'none') for _ in range(N_D)]
    for name, des in DESIGNS.items():
        field, rows = run_design(bed, dcases, des)
        out['designs'][name] = evaluate(bed, 'none', list(zip(dcases, field)), rows, sims=None, ms=(20,), rs=rs)
        log(f'{name:18s} ' + ' | '.join(
            f'{k} floor {out["designs"][name][k]["floor"]["halfwidth"]:.4f} m20 '
            f'{out["designs"][name][k]["m20"]["halfwidth"]:.4f}' for k in GOALS) + f'  [{time.time() - t0:.0f}s]')
    out['seconds'] = time.time() - t0
    with open(os.path.join(RES, 'dyshemeja.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    with open(os.path.join(RES, 'dyshemeja_log.txt'), 'w') as fh:
        fh.write('\n'.join(LOG) + '\n')
    log(f'done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
