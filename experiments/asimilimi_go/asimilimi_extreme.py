"""ASIMILIMI-GO, extreme events: updating the boundary conditions when the boundaries do something the prior did
not expect. Same aquifer as asimilimi.py (time in years, grid 100 m), daily data for three years.

Truth (per twin): the stationary boundaries of asimilimi.py plus
  storm surges   Poisson events (4 per year) at the sea boundary, amplitude 0.25 + Exp(0.5) m, decay time 2 days
                 (an extra truth state that no filter has);
  a drought      300 days from a random day in [300, 500]: recharge falls by 0.25 m/yr (an extra truth state) and
                 the unlicensed pumping E jumps by +300 m3/d per km of coast;
  sensor spikes  (only where stated) each reading is hit with probability 0.5% by an error of sd 0.8 m.
Data: daily heads at 250, 1250, 2750 and 4250 m (sd 0.02 m), and where stated a tide gauge (sd 0.01 m) that reads
the sea level (offset + anomaly + surge).

E8   regimes. Filters on the same augmented state (heads, clay compartments, sea anomaly, recharge anomaly, eta0, E):
       Gaussian   the stationary prior of asimilimi.py, E a slow random walk;
       alarm      Gaussian plus a calibrated alarm on the normalised innovation squared (chi-square, 0.999): when it
                  rings the boundary states are opened and the analysis is redone;
       IMM        interacting multiple models with three regimes that differ in the boundary process noise:
                  normal, surge (sea anomaly free) and drought or flood (recharge anomaly and E free);
     run with heads only and with heads + tide gauge.
E11  spikes and events together (heads + gauge + spikes): Gaussian, IMM, and IMM with a spike model (each reading
     may be a spike; the update is the exact mixture over 'no spike' and 'spike at sensor i', merged by moments).
     Metrics for E8 and E11: error and coverage of 90% intervals for the sea anomaly, the recharge anomaly, E and the
     unobserved head 50 m from the sea, separately on surge, drought and normal days; regime detection.
E9   spikes in the monthly ten-year setting: Gaussian update against a down-weighting update (a reading whose
     standardised residual r exceeds k = 2.5 gets its variance multiplied by (r/k)^2); error and coverage of E, eta0.
E10  the alarm of Theorem 9: false-alarm rate when the model is right, and detection power of a surge of amplitude a
     against the exact prediction 1 - prod_k F_ncx2(c; m, a^2 lambda_k).
E12  Lemma 2: river max(h, z_b) and drain (h - z_d)_+ switches keep the implicit scheme non-expansive,
     ||dh_n|| <= ||dh_0|| + sum dt ||db_k||, on 400 random pairs of forcings with floods and dry spells.
Writes res/extreme.json.
"""
import json
import os
import time
from multiprocessing import Pool

import numpy as np
from scipy.stats import chi2, norm, ncx2

import asimilimi as M

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
P = M.P
N = P['N']
NH = M.NH
DT = 1.0 / 365.25
YEARS = 3.0
NSTEP = int(round(YEARS / DT))
NTW = int(os.environ.get('NTW', 60))
BASE = ['eta_ia', 'rho', 'eta0', 'E']
Z90 = norm.ppf(0.95)
P_SPIKE, SD_SPIKE = 0.005, 0.8
KEYS = ['sea anomaly', 'recharge anomaly', 'E', 'head 50 m from the sea']
PHASES = ('surge', 'drought', 'normal')


def sqrtm_psd(A):
    w, V = np.linalg.eigh(0.5 * (A + A.T))
    return V * np.sqrt(np.clip(w, 0, None))


def models():
    A, Qc, idx = M.build(BASE + ['surge', 'dshift'])
    c = P['T'] / M.DX ** 2 / P['Sy']
    js, jd = idx['surge'], idx['dshift']
    A[0, js] += 2 * c                                          # the surge feeds the sea face like eta
    A[js, js] = -365.25 / 2.0                                  # and decays in 2 days
    A[:N, jd] += 1 / P['Sy']                                   # the drought shift acts like recharge
    Ft, Qt = M.discretise(A, Qc, DT, doublings=4)
    nf = NH + len(BASE)
    Ff = Ft[:nf, :nf].copy()
    Qf = Qt[:nf, :nf].copy()
    Qf[idx['E'], idx['E']] += 2.0 ** 2                        # E as a slow random walk (2 m3/d/km per day)
    return Ft, Qt, Ff, Qf, idx, nf


G = {}


def init():
    Ft, Qt, Ff, Qf, idx, nf = models()
    nt = Ft.shape[0]
    P0f = M.prior_cov(BASE, {k: idx[k] for k in BASE})
    P0t = np.zeros((nt, nt)); P0t[:nf, :nf] = P0f
    ie, ir, iE, isg = idx['eta_ia'], idx['rho'], idx['E'], idx['surge']
    assert isg == nf
    # filters of E8/E11 carry a surge state with the right 2-day decay (closed in the normal regime)
    ns = nf + 1
    Ffs = Ft[:ns, :ns].copy()
    Qfs = np.zeros((ns, ns)); Qfs[:nf, :nf] = Qf
    P0s = np.zeros((ns, ns)); P0s[:nf, :nf] = P0f; P0s[isg, isg] = 1e-6
    es = np.zeros(ns); es[isg] = 1.0
    obs0, obs = {}, {}
    for gauge in (False, True):
        H, sig = M.obs_matrix(nf, {k: idx[k] for k in BASE}, gauge=gauge)
        Ht = np.zeros((H.shape[0], nt)); Ht[:, :nf] = H
        if gauge:
            Ht[-1, isg] = 1.0                                  # the gauge also reads the surge
        obs0[gauge] = (H, sig, Ht)
        obs[gauge] = (Ht[:, :ns].copy(), sig, Ht)
    open_drought = np.zeros(ns); open_drought[ir] = 0.06 ** 2; open_drought[iE] = 40.0 ** 2
    q_shot = 4.0 / 365.25 * (0.5 ** 2 + 0.75 ** 2)            # surge rate x E[a^2]: the best Gaussian (second-order) model
    Qg = Qfs + np.diag(q_shot * es)
    G.update(Ft=Ft, Qt=Qt, Ff=Ff, Qf=Qf, idx=idx, nf=nf, nt=nt, P0f=P0f, Lq=sqrtm_psd(Qt), L0=sqrtm_psd(P0t), obs0=obs0,
             obs=obs, ns=ns, Ffs=Ffs, P0s=P0s, Qg=Qg, Qopen=np.diag(0.8 ** 2 * es + open_drought),
             Qs=[Qfs + np.diag(1e-6 * es), Qfs + np.diag(0.8 ** 2 * es), Qfs + np.diag(1e-6 * es + open_drought)],
             Pi=np.array([[0.986, 0.011, 0.003], [0.50, 0.50, 0.0], [0.004, 0.0, 0.996]]))


def update(mf, Cf, y, H, R):
    S = H @ Cf @ H.T + R
    nu = y - H @ mf
    K = np.linalg.solve(S, H @ Cf).T
    return mf + K @ nu, Cf - K @ H @ Cf, nu, S


def loglik(nu, S):
    return -0.5 * (nu @ np.linalg.solve(S, nu) + np.linalg.slogdet(S)[1] + len(nu) * np.log(2 * np.pi))


def sea_var(C):
    i, j = G['idx']['eta_ia'], G['idx']['surge']
    if C.shape[0] <= j:
        return C[i, i]
    return C[i, i] + C[j, j] + 2 * C[i, j]


def run_gauss(Y, H, R, alarm=False):
    Ff, Qf, P0f = G['Ffs'], G['Qg'], G['P0s']
    thr = chi2.ppf(0.999, H.shape[0])
    mm, CC = np.zeros(G['ns']), P0f.copy()
    Ms, Ds, rings = [], [], []
    for k in range(len(Y)):
        mf = Ff @ mm; Cf = Ff @ CC @ Ff.T + Qf
        m1, C1, nu, S = update(mf, Cf, Y[k], H, R)
        ring = False
        if alarm and nu @ np.linalg.solve(S, nu) > thr:       # open the boundaries and redo the analysis
            ring = True
            m1, C1, _, _ = update(mf, Cf + G['Qopen'], Y[k], H, R)
        mm, CC = m1, C1
        Ms.append(mm.copy()); Ds.append(np.append(np.diag(CC), sea_var(CC))); rings.append(ring)
    return np.array(Ms), np.array(Ds), np.array(rings), None


def run_imm(Y, H, R, spikes=False, variance_only=False):
    Ff, Qs, Pi, P0f = G['Ffs'], G['Qs'], G['Pi'], G['P0s']
    if variance_only:                                          # no surge state: the surge regime adds variance to eta_ia
        Ff, P0f = G['Ff'], G['P0f']
        ou = np.zeros(G['nf']); ou[G['idx']['eta_ia']] = 0.30 ** 2
        od = np.zeros(G['nf']); od[G['idx']['rho']] = 0.06 ** 2; od[G['idx']['E']] = 40.0 ** 2
        Qs = [G['Qf'], G['Qf'] + np.diag(ou), G['Qf'] + np.diag(od)]
    r, m = 3, H.shape[0]
    ms = [np.zeros(P0f.shape[0]) for _ in range(r)]; Cs = [P0f.copy() for _ in range(r)]
    mu = np.array([0.98, 0.01, 0.01])
    if spikes:                                                 # configurations: no spike, or a spike at sensor i
        pri = np.array([(1 - P_SPIKE) ** m] + [P_SPIKE * (1 - P_SPIKE) ** (m - 1)] * m)
        pri = pri / pri.sum()
        Radd = [np.zeros(m)] + [np.eye(m)[i] * SD_SPIKE ** 2 for i in range(m)]
    Ms, Ds, MU = [], [], []
    for k in range(len(Y)):
        cbar = Pi.T @ mu
        mix = (Pi * mu[:, None]) / np.maximum(cbar[None, :], 1e-300)
        lik = np.zeros(r)
        m0s, C0s = [], []                                     # mix the estimates of the previous step first
        for j in range(r):
            m0 = sum(mix[i, j] * ms[i] for i in range(r))
            m0s.append(m0)
            C0s.append(sum(mix[i, j] * (Cs[i] + np.outer(ms[i] - m0, ms[i] - m0)) for i in range(r)))
        for j in range(r):
            mf = Ff @ m0s[j]; Cf = Ff @ C0s[j] @ Ff.T + Qs[j]
            if not spikes:
                m1, C1, nu, S = update(mf, Cf, Y[k], H, R)
                ms[j], Cs[j], lik[j] = m1, C1, loglik(nu, S)
            else:
                outs, ll = [], np.zeros(m + 1)
                for c in range(m + 1):
                    m1, C1, nu, S = update(mf, Cf, Y[k], H, R + np.diag(Radd[c]))
                    outs.append((m1, C1)); ll[c] = np.log(pri[c]) + loglik(nu, S)
                lmax = ll.max(); wc = np.exp(ll - lmax); lik[j] = lmax + np.log(wc.sum()); wc /= wc.sum()
                mj = sum(wc[c] * outs[c][0] for c in range(m + 1))
                Cj = sum(wc[c] * (outs[c][1] + np.outer(outs[c][0] - mj, outs[c][0] - mj)) for c in range(m + 1))
                ms[j], Cs[j] = mj, Cj
        w = cbar * np.exp(lik - lik.max())
        mu = w / w.sum()
        mm = sum(mu[j] * ms[j] for j in range(r))
        CC = sum(mu[j] * (Cs[j] + np.outer(ms[j] - mm, ms[j] - mm)) for j in range(r))
        Ms.append(mm); Ds.append(np.append(np.diag(CC), sea_var(CC))); MU.append(mu.copy())
    return np.array(Ms), np.array(Ds), None, np.array(MU)


FILTERS = [('heads', 'Gaussian'), ('heads', 'alarm'), ('heads', 'IMM'),
           ('heads + gauge', 'Gaussian'), ('heads + gauge', 'IMM'),
           ('heads + gauge + spikes', 'Gaussian'), ('heads + gauge + spikes', 'IMM'), ('heads + gauge + spikes', 'IMM + spike model')]


def twin(tw, filters=None, keep=False):
    filters = filters or FILTERS
    rng = np.random.default_rng([88, tw])
    Ft, idx, nt = G['Ft'], G['idx'], G['nt']
    ie, ir, iE = idx['eta_ia'], idx['rho'], idx['E']
    Ht = G['obs'][True][2]
    sig = G['obs'][True][1]
    x = G['L0'] @ rng.standard_normal(nt)
    x[idx['surge']] = 0.0; x[idx['dshift']] = 0.0
    d0 = int(rng.integers(300, 500)); d1 = d0 + 300
    ev = np.sort(rng.integers(0, NSTEP, rng.poisson(4 * YEARS)))
    amp = 0.25 + rng.exponential(0.5, len(ev))
    X = np.zeros((NSTEP, nt)); Yg = np.zeros((NSTEP, len(sig)))
    for k in range(NSTEP):
        x = Ft @ x + G['Lq'] @ rng.standard_normal(nt)
        for e_, a_ in zip(ev, amp):
            if e_ == k:
                x[idx['surge']] += a_
        if k == d0:
            x[idx['dshift']] = -0.25; x[iE] += 300.0
        if k == d1:
            x[idx['dshift']] = 0.0; x[iE] -= 300.0
        X[k] = x
        Yg[k] = Ht @ x + rng.standard_normal(len(sig)) * sig
    spk = (rng.random(Yg.shape) < P_SPIKE) * rng.standard_normal(Yg.shape) * SD_SPIKE
    surge_days = np.zeros(NSTEP, bool)
    for e_ in ev:
        surge_days[e_:min(e_ + 6, NSTEP)] = True
    drought_days = np.zeros(NSTEP, bool); drought_days[d0:d1] = True
    phase = np.where(surge_days, 'surge', np.where(drought_days, 'drought', 'normal'))
    truth = {'sea anomaly': X[:, ie] + X[:, idx['surge']], 'recharge anomaly': X[:, ir] + X[:, idx['dshift']],
             'E': X[:, iE], 'head 50 m from the sea': X[:, 0]}
    comp = {'sea anomaly': ie, 'recharge anomaly': ir, 'E': iE, 'head 50 m from the sea': 0}
    res = {}
    if keep:
        res['_trace'] = dict(truth={k: v.tolist() for k, v in truth.items()}, events=ev.tolist(), amps=amp.tolist(), d0=d0, d1=d1,
                             spikes=np.argwhere(spk != 0).tolist())
    for data, fil in filters:
        gauge = 'gauge' in data
        H, s_, _ = G['obs0' if 'variance only' in fil else 'obs'][gauge]
        Y = Yg if gauge else Yg[:, :-1]
        if 'spikes' in data:
            Y = Y + (spk if gauge else spk[:, :-1])
        R = np.diag(s_ ** 2)
        if fil == 'Gaussian':
            Ms, Ds, rings, MU = run_gauss(Y, H, R)
        elif fil == 'alarm':
            Ms, Ds, rings, MU = run_gauss(Y, H, R, alarm=True)
        else:
            Ms, Ds, rings, MU = run_imm(Y, H, R, spikes=(fil == 'IMM + spike model'), variance_only=('variance only' in fil))
        out = dict(se={}, cov={})
        for kk in KEYS:
            j = comp[kk]
            if kk == 'sea anomaly':
                est, var = Ms[:, ie] + (Ms[:, idx['surge']] if Ms.shape[1] > idx['surge'] else 0.0), Ds[:, -1]
            else:
                est, var = Ms[:, j], Ds[:, j]
            err = est - truth[kk]; sd = np.sqrt(np.maximum(var, 1e-30))
            out['se'][kk] = {p: (err[phase == p] ** 2).tolist() for p in PHASES}
            out['cov'][kk] = {p: (np.abs(err[phase == p]) <= Z90 * sd[phase == p]).tolist() for p in PHASES}
        hit = np.where((np.arange(NSTEP) >= d0) & (Ms[:, iE] > 150.0))[0]
        out['drought_delay'] = int(hit[0] - d0) if len(hit) else NSTEP
        if fil == 'alarm':
            out['alarm'] = {p: rings[phase == p].tolist() for p in PHASES}
        if MU is not None:
            out['surge_found'] = [bool(MU[e_:min(e_ + 6, NSTEP), 1].max() > 0.5) for e_ in ev]
            out['false_surge'] = float(np.mean(MU[phase == 'normal', 1] > 0.5))
            hitd = np.where((np.arange(NSTEP) >= d0) & (MU[:, 2] > 0.5))[0]
            out['drought_regime_delay'] = int(hitd[0] - d0) if len(hitd) else NSTEP
            out['false_drought'] = float(np.mean(MU[:d0, 2] > 0.5))
        if keep:
            sea = Ms[:, ie] + (Ms[:, idx['surge']] if Ms.shape[1] > idx['surge'] else 0.0)
            out['trace'] = dict(sea=sea.tolist(), sea_sd=np.sqrt(Ds[:, -1]).tolist(), E=Ms[:, iE].tolist(), E_sd=np.sqrt(Ds[:, iE]).tolist(),
                                h50=Ms[:, 0].tolist(), h50_sd=np.sqrt(Ds[:, 0]).tolist(), mu=None if MU is None else MU.tolist())
        res[data + ' / ' + fil] = out
    return res


def e9():
    """Spikes in the monthly ten-year setting (static boundary parameters)."""
    A, Qc, idx2 = M.build(BASE)
    F, Qd = M.discretise(A, Qc, P['dt'])
    n = F.shape[0]
    H2, s2 = M.obs_matrix(n, idx2)
    P02 = M.prior_cov(BASE, idx2)
    nst = int(round(P['years'] / P['dt']))
    rng = np.random.default_rng(99)
    kH = 2.5
    res9 = {g: dict(errE=[], cE=[], err0=[], c0=[]) for g in ('Gaussian', 'down-weighting', 'Gaussian, no spikes')}
    for tw in range(200):
        X0, Yc = M.simulate(F, Qd, H2, s2, P02, nst, rng)
        Yc = Yc[0]
        spikes = rng.random(Yc.shape) < P_SPIKE
        Ys = Yc + spikes * rng.standard_normal(Yc.shape) * SD_SPIKE
        for g, Yuse in (('Gaussian', Ys), ('down-weighting', Ys), ('Gaussian, no spikes', Yc)):
            mm, CC = np.zeros(n), P02.copy()
            m2 = H2.shape[0]
            for k in range(nst):
                mf = F @ mm; Cf = F @ CC @ F.T + Qd
                yk = Yuse[k * m2:(k + 1) * m2]
                Rk = np.diag(s2 ** 2)
                if g == 'down-weighting':
                    S = H2 @ Cf @ H2.T + Rk
                    rr = (yk - H2 @ mf) / np.sqrt(np.diag(S))
                    w = np.where(np.abs(rr) > kH, (np.abs(rr) / kH) ** 2, 1.0)
                    Rk = Rk + np.diag((w - 1.0) * np.diag(S))
                mm, CC, _, _ = update(mf, Cf, yk, H2, Rk)
            for nm, ke, kc in (('E', 'errE', 'cE'), ('eta0', 'err0', 'c0')):
                j = idx2[nm]
                err = mm[j] - X0[0, j]; sd = np.sqrt(CC[j, j])
                res9[g][ke].append(err / sd); res9[g][kc].append(abs(err) <= Z90 * sd)
    return {g: dict(rms_z_E=float(np.sqrt(np.mean(np.square(v['errE'])))), coverage_E=float(np.mean(v['cE'])),
                    rms_z_eta0=float(np.sqrt(np.mean(np.square(v['err0'])))), coverage_eta0=float(np.mean(v['c0'])))
            for g, v in res9.items()}


def e10(B=4000, K0=150, W=6, amps=(0.05, 0.1, 0.25, 0.5, 0.75, 1.0)):
    """Theorem 9: calibration of the alarm when the model is right, and its power against a surge."""
    Ft, Ff, Qf, P0f, idx, nf, nt = G['Ft'], G['Ff'], G['Qf'], G['P0f'], G['idx'], G['nf'], G['nt']
    Lq, L0 = sqrtm_psd(Qf), sqrtm_psd(P0f)
    out = {}
    for gauge in (False, True):
        H, sig, Ht = G['obs0'][gauge]
        m = H.shape[0]
        R = np.diag(sig ** 2)
        c = chi2.ppf(0.999, m)
        Ks, Sinv = [], []
        C = P0f.copy()
        for k in range(K0 + W):                                # the gains do not depend on the data
            Cf = Ff @ C @ Ff.T + Qf
            S = H @ Cf @ H.T + R
            K = np.linalg.solve(S, H @ Cf).T
            C = Cf - K @ H @ Cf
            Ks.append(K); Sinv.append(np.linalg.inv(S))
        # deterministic surge response (unit amplitude, onset on day K0) seen by the sensors
        z = np.zeros(nt)
        Yd = np.zeros((K0 + W, m))
        for k in range(K0, K0 + W):
            if k > K0:
                z = Ft @ z
            else:
                z[idx['surge']] = 1.0
            Yd[k] = Ht @ z
        # innovation mean caused by the surge (the filter is linear in the data)
        md = np.zeros(nf); dev = []
        for k in range(K0 + W):
            mdf = Ff @ md
            d = Yd[k] - H @ mdf
            md = mdf + Ks[k] @ d
            if k >= K0:
                dev.append(d)
        lam = np.array([float(d @ Sinv[K0 + i] @ d) for i, d in enumerate(dev)])
        # null twins from the filter model itself (the model is right)
        rng = np.random.default_rng([10, int(gauge)])
        x = rng.standard_normal((B, nf)) @ L0.T
        mm = np.zeros((B, nf))
        null_nis, win_nu = [], []
        for k in range(K0 + W):
            x = x @ Ff.T + rng.standard_normal((B, nf)) @ Lq.T
            y = x @ H.T + rng.standard_normal((B, m)) * sig
            mf = mm @ Ff.T
            nu = y - mf @ H.T
            if k < K0:
                null_nis.append(np.einsum('bi,ij,bj->b', nu, Sinv[k], nu))
            else:
                win_nu.append(nu)
            mm = mf + nu @ Ks[k].T
        null_nis = np.array(null_nis)
        rows = []
        for a in amps:
            hits = np.zeros(B, bool)
            for i in range(W):
                nu = win_nu[i] + a * dev[i]
                hits |= np.einsum('bi,ij,bj->b', nu, Sinv[K0 + i], nu) > c
            pred = 1.0 - np.prod([ncx2.cdf(c, m, a ** 2 * l) if a ** 2 * l > 1e-12 else chi2.cdf(c, m) for l in lam])
            rows.append(dict(amplitude=a, empirical=float(hits.mean()), predicted=float(pred),
                             se=float(np.sqrt(max(pred * (1 - pred), 1e-6) / B))))
        out['heads + gauge' if gauge else 'heads'] = dict(
            m=m, threshold=float(c), null_rate=float(np.mean(null_nis > c)), null_rate_se=float(np.sqrt(0.001 * 0.999 / null_nis.size)),
            null_mean=float(null_nis.mean()), lambda_unit=lam.tolist(), rows=rows)
    return out


def e12(npairs=400, years=1.0):
    """Lemma 2: the switching river and drain keep the implicit scheme non-expansive."""
    n, Sy = N, P['Sy']
    cc = P['T'] / M.DX ** 2 / Sy                               # 1/yr
    dt = 1.0 / 365.25
    nst = int(round(years / dt))
    L = np.zeros((n, n))
    for i in range(n):
        if i > 0:
            L[i, i - 1] = cc; L[i, i] -= cc
        if i < n - 1:
            L[i, i + 1] = cc; L[i, i] -= cc
    L[0, 0] -= 2 * cc                                          # sea face at half a cell
    iriv, idrn = 20, 5
    zb, zd = 0.6, 0.8
    cr, cd = 365.25, 730.5                                     # 1/yr
    A0 = np.eye(n) / dt - L
    rng = np.random.default_rng(12)

    def forcing():
        eta = 0.1 + np.cumsum(rng.standard_normal(nst)) * 0.005 + (rng.random(nst) < 0.01) * rng.exponential(0.5, nst)
        R = np.full(nst, 0.05) + rng.standard_normal(nst) * 0.1
        fl = rng.integers(0, nst - 30); R[fl:fl + 20] += rng.uniform(3, 10)          # a flood (m/yr)
        hr = 0.9 + 0.3 * np.sin(np.arange(nst) / 58.0 + rng.uniform(0, 6))
        dr = rng.integers(0, nst - 60); hr[dr:dr + 60] = zb - 0.2                  # a dry spell
        b = np.zeros((nst, n))
        b[:, 0] += 2 * cc * eta
        b += (R / Sy)[:, None]
        b[:, iriv] += cr * hr
        return b

    def g(h):                                                  # monotone switching terms
        out = np.zeros(n); dg = np.zeros(n)
        out[iriv] = cr * max(h[iriv], zb); dg[iriv] = cr * (h[iriv] > zb)
        out[idrn] = cd * max(h[idrn] - zd, 0.0); dg[idrn] = cd * (h[idrn] > zd)
        return out, dg

    def solve(b, h0):
        Hs = np.zeros((nst, n)); h = h0.copy(); act = np.zeros((nst, 2), bool)
        for k in range(nst):
            rhs = h / dt + b[k]
            hn = h.copy()
            for it in range(60):                              # semi-smooth Newton
                gv, dg = g(hn)
                Fv = A0 @ hn + gv - rhs
                if np.max(np.abs(Fv)) < 1e-9 * (1 + np.max(np.abs(rhs))):
                    break
                hn = hn - np.linalg.solve(A0 + np.diag(dg), Fv)
            h = hn; Hs[k] = h
            act[k] = (h[iriv] <= zb, h[idrn] > zd)
        return Hs, act

    ratios, act_frac = [], []
    for p in range(npairs):
        b1 = forcing()
        b2 = forcing() if p % 2 else b1 + rng.standard_normal(b1.shape) * 0.05 * np.abs(b1).mean()
        h01 = 0.5 + rng.standard_normal(n) * 0.05; h02 = h01 + rng.standard_normal(n) * 0.05
        H1, a1 = solve(b1, h01); H2, a2 = solve(b2, h02)
        bound = np.linalg.norm(h01 - h02) + np.cumsum(dt * np.linalg.norm(b1 - b2, axis=1))
        lhs = np.linalg.norm(H1 - H2, axis=1)
        ratios.append(float(np.max(lhs / bound)))
        act_frac.append([a1[:, 0].mean(), a1[:, 1].mean(), float(np.any(a1[:, 0] != a1[0, 0])), float(np.any(a1[:, 1] != a1[0, 1]))])
    af = np.array(act_frac)
    return dict(npairs=npairs, max_ratio=float(np.max(ratios)), median_ratio=float(np.median(ratios)),
                frac_days_river_disconnected=float(af[:, 0].mean()), frac_days_drain_on=float(af[:, 1].mean()),
                frac_runs_river_switched=float(af[:, 2].mean()), frac_runs_drain_switched=float(af[:, 3].mean()))


def _twin_b(tw):
    return twin(tw, filters=[('heads + gauge', 'IMM, variance only')])


def summarise(all_res):
    out = {}
    for name in all_res[0]:
        R = [r[name] for r in all_res]
        o = dict(rmse={}, coverage={})
        for kk in KEYS:
            o['rmse'][kk] = {p: float(np.sqrt(np.mean(sum((r['se'][kk][p] for r in R), [])))) for p in PHASES}
            o['coverage'][kk] = {p: float(np.mean(sum((r['cov'][kk][p] for r in R), []))) for p in PHASES}
        d = np.array([r['drought_delay'] for r in R])
        o['drought_E_detect'] = dict(median=float(np.median(d)), q90=float(np.quantile(d, 0.9)), never=float(np.mean(d >= NSTEP)))
        if 'alarm' in R[0]:
            o['alarm_rate'] = {p: float(np.mean(sum((r['alarm'][p] for r in R), []))) for p in PHASES}
        if 'surge_found' in R[0]:
            o['surge_found'] = float(np.mean(sum((r['surge_found'] for r in R), [])))
            o['false_surge_rate'] = float(np.mean([r['false_surge'] for r in R]))
            dd = np.array([r['drought_regime_delay'] for r in R])
            o['drought_regime_detect'] = dict(median=float(np.median(dd)), q90=float(np.quantile(dd, 0.9)), never=float(np.mean(dd >= NSTEP)))
            o['false_drought_rate'] = float(np.mean([r['false_drought'] for r in R]))
        out[name] = o
    return out


def main():
    t0 = time.time()
    only = os.environ.get('ONLY', '')
    out = dict(ntwins=NTW, years=YEARS, dt_days=1, p_spike=P_SPIKE, sd_spike=SD_SPIKE)
    if only in ('', 'E8'):
        with Pool(4, initializer=init) as pool:
            all_res = []
            for i, r in enumerate(pool.imap(twin, range(NTW))):
                all_res.append(r)
                if i % 10 == 0:
                    print('twin', i, f'{time.time() - t0:.0f}s', flush=True)
        out['E8_E11'] = summarise(all_res)
        for name, o in out['E8_E11'].items():
            print(name, {k: {p: (round(o['coverage'][k][p], 3), round(o['rmse'][k][p], 4)) for p in PHASES} for k in KEYS},
                  {k: v for k, v in o.items() if k not in ('rmse', 'coverage')}, flush=True)
    if only == 'E8b':                                          # a regime that adds variance only (no event dynamics)
        fl = [('heads + gauge', 'IMM, variance only')]
        with Pool(4, initializer=init) as pool:
            all_res = list(pool.imap(_twin_b, range(NTW)))
        J = json.load(open(os.path.join(RES, 'extreme.json')))
        J['E8_E11'].update(summarise(all_res))
        json.dump(J, open(os.path.join(RES, 'extreme.json'), 'w'), indent=1)
        print('E8b', json.dumps(summarise(all_res)), flush=True)
        return
    if only == 'TRACE':
        init()
        tw = int(os.environ.get('TRACE_TW', 0))
        r = twin(tw, filters=[('heads + gauge + spikes', 'Gaussian'), ('heads + gauge + spikes', 'IMM + spike model')], keep=True)
        tr = dict(twin=tw, days=NSTEP, **r.pop('_trace'))
        tr['filters'] = {k: v['trace'] for k, v in r.items()}
        json.dump(tr, open(os.path.join(RES, 'extreme_trace.json'), 'w'))
        print('wrote res/extreme_trace.json', flush=True)
        return
    init()
    if only in ('', 'E10'):
        out['E10'] = e10()
        print('E10', json.dumps(out['E10']), flush=True)
    if only in ('', 'E12'):
        out['E12'] = e12(npairs=int(os.environ.get('NPAIRS', 400)))
        print('E12', out['E12'], flush=True)
    if only in ('', 'E9'):
        out['E9'] = e9()
        print('E9', out['E9'], flush=True)
    out['seconds'] = time.time() - t0
    if not only:
        json.dump(out, open(os.path.join(RES, 'extreme.json'), 'w'), indent=1)
        print('wrote res/extreme.json', f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
