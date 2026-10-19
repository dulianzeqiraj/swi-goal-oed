"""N3. Coverage after ADAPTIVE groundwater monitoring on a synthetic coastal transect.

Physics. Steady 1-D confined flow on a coastal transect x in [0, L], L = 5 km (inland boundary at
x = 0, sea at x = L), uniform net (leakage) recharge N and transmissivity T:
    h(x) = a + b x + c x (L - x),   c = N / (2T).
Internally u = x / L and theta = (a, beta, kappa) with beta = b L, kappa = c L^2 (metres), so that
h = a + beta u + kappa u (1 - u), regressors z(u) = (1, u, u(1-u)). T = 800 m^2/d; the management
threshold is the net recharge N0 = 80 mm/yr needed to sustain the planned pumping, c0 = N0/(2T)
(kappa0 = 3.42 m). Truths: zero margin, N = N0 (c = c0); clear margin, N = 100 mm/yr (c = 1.25 c0).
a = 3.0 m (inland head), h(L) = 0.3 m (freshwater head at the shoreline), beta = -2.7 m.
Head measurements y_t = h(x_t) + eps_t, eps_t ~ N(0, sigma^2) i.i.d. and independent of the
placement given the past, sigma = 0.05 m (known).

Adaptive design (Thompson-type). Gaussian conjugate posterior for theta (known sigma, prior
N((3, -3, kappa0), I_3) in metres). At step t the planner draws kappa~ from the posterior; if
kappa~ > kappa0 (enough recharge) the next well goes to the COASTAL zone K = [0.95 L, L] (sentinel wells
in the last 250 m between the planned pumping well and the shoreline), otherwise to the CENTRAL
recharge zone C = [0.2 L, 0.7 L] (where x(L-x) is large); location uniform within the zone. So
    q_opt,t = p_t U(K) + (1 - p_t) U(C),  p_t = P(kappa > kappa0 | H_{t-1}).
Smoothed design (proposal N1): q_t = (1 - gamma) q_opt,t + gamma q_sta, q_sta = U[0, L];
gamma = 0 uses p_t clipped to [0.01, 0.99] (then supp q_t = C u K and the effective stabilising
design is q_sta restricted to C u K). Weights W_t = sqrt(q_sta(x_t) / q_t(x_t)) (base paper).
Also a non-adaptive uniform design (q_t = q_sta, W_t = 1) as reference.

Estimators of kappa (equivalently c = kappa / L^2):
  OLS-cl  ordinary least squares, classical interval with sigma_hat^2 = RSS/(n-3), t_{n-3} quantile
  OLS-sw  OLS with sandwich (HC0 x n/(n-3)) interval
  AW      adaptively weighted LS, argmin sum W_t (y_t - z_t' theta)^2, with the self-normalised sandwich
          A^{-1} B A^{-1}, A = sum W z z', B = sum W^2 r^2 z z' (x n/(n-3)); 'direct' marginal interval,
          the same with the leverage-corrected (HC3) meat, and the projection of the chi^2_3 ellipsoid of
          the base paper's theorem (guaranteed asymptotically, conservative)
  IPW     importance-weighted LS (weights W_t^2 = q_sta/q_t), sandwich interval
  CS      time-uniform confidence sequence (method of mixtures, Abbasi-Yadkori, Pal & Szepesvari 2011,
          Theorem 1, in the form without ridge bias): with S_n(theta) = sum_t w_t z_t (y_t - z_t' theta) and
          G_n = sum_t w_t^2 z_t z_t',
              {theta : S_n(theta)' (H + G_n)^{-1} S_n(theta) <= sigma^2 [2 log(1/alpha) + log det(I + H^{-1} G_n)]}
          holds for all n simultaneously with probability >= 1 - alpha, because w_t z_t is
          H_{t-1} v sigma(x_t)-measurable and eps_t ~ N(0, sigma^2) independently of it, so
          exp(eta' S_n / sigma - eta' G_n eta / 2) is a martingale for each eta; mixing eta ~ N(0, H^{-1})
          and Ville's inequality give the bound. Projected on kappa; H = 25 E_{q_sta}[z z'] (prior worth
          of 25 uniform wells). w_t = 1 (centred at OLS) and w_t = W_t (centred at AW-LS).

Misspecified case: a frozen paleochannel trough delta(x) = -0.12 exp(-(x - 4.25 km)^2 / (2 (250 m)^2))
added to the head of the margin truth; then OLS / AW / IPW converge to the L2 projections of h under
q_inf, sqrt(q_sta q_inf) and q_sta respectively (q_inf = limit design).

Exploration (zero margin, gamma = 0): which design choices make the OLS under-coverage strong
(zone geometry, clipping, prior, tempered/greedy allocation, campaigns of 10 wells).

Run: python3 sim_aquifer.py [--workers 3]   (jobs run in parallel processes, one BLAS thread each).
Output: results/aquifer.json
"""
import argparse
import multiprocessing as mp
import os
import time

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np
from scipy.stats import norm, t as tdist, chi2

from common import dump

# ---------------------------------------------------------------- setting
L_KM = 5.0
SIG = 0.05                       # m, head measurement error (known)
T_TR = 800.0                     # m^2/d
N0_MM, N1_MM = 80.0, 100.0       # mm/yr: threshold and margin truth
A_IN, H_COAST = 3.0, 0.3         # m
ZC = (0.2, 0.7)                  # central recharge zone (fraction of L)
ZK = (0.95, 1.0)                 # coastal zone (last 250 m before the shoreline)
CLIP = 0.01
PRIOR_SD = np.array([1.0, 1.0, 1.0])
GAMMAS = (0.0, 0.05, 0.1, 0.2, 0.5)
ALPHA = 0.05
NREF = 25
CK = (25, 50, 100, 200, 400)
N_EV0 = 10
BUMP = dict(A=0.12, xc=0.85, s=0.05)   # fraction of L: centre 4.25 km, sd 250 m
ZBINS = np.linspace(-5, 5, 51)
RMAIN = 10000                    # replications, correctly specified runs
RMIS = 4000                      # replications, misspecified runs (n up to 1600)
RLONG = 10000                    # replications, long correctly specified runs (n up to 1600)
REXP = 6000                      # replications, exploration runs


def kappa_of(n_mm):
    c = (n_mm / 1000.0 / 365.25) / (2 * T_TR)       # 1/m
    return c * (L_KM * 1000.0) ** 2, c


KAP0, C0 = kappa_of(N0_MM)
KAP1, C1 = kappa_of(N1_MM)
BETA = H_COAST - A_IN
PRIOR_M = np.array([A_IN, -3.0, KAP0])
SIG_STA = np.array([[1, 1 / 2, 1 / 6], [1 / 2, 1 / 3, 1 / 12], [1 / 6, 1 / 12, 1 / 30]])
HMIX = NREF * SIG_STA
LOGDET_H = np.linalg.slogdet(HMIX)[1]


def feats(u):
    return np.stack([np.ones_like(u), u, u * (1 - u)], -1)


def bump(u):
    return -BUMP['A'] * np.exp(-(u - BUMP['xc']) ** 2 / (2 * BUMP['s'] ** 2))


def head(u, kap, misspec=False):
    h = A_IN + BETA * u + kap * u * (1 - u)
    return h + bump(u) if misspec else h


# ---------------------------------------------------------------- projections (targets)
def projection(dens_fun, kap, misspec, ng=400001):
    u = np.linspace(0, 1, ng); du = u[1] - u[0]
    d = dens_fun(u); z = feats(u); h = head(u, kap, misspec)
    A = (z * d[:, None]).T @ z * du; b = (z * d[:, None]).T @ h * du
    return np.linalg.solve(A, b)


def limit_designs(gamma, zc=ZC, zk=ZK):
    """Limit design when the posterior settles on 'c > c0' (margin truth): p -> 1 (or 0.99 clipped)."""
    inK = lambda u: ((u >= zk[0]) & (u <= zk[1])) / (zk[1] - zk[0])
    inC = lambda u: ((u >= zc[0]) & (u <= zc[1])) / (zc[1] - zc[0])
    if gamma == 0:
        q = lambda u: (1 - CLIP) * inK(u) + CLIP * inC(u)
        sta = lambda u: ((u >= zc[0]) & (u <= zc[1])) * 1.0 + ((u >= zk[0]) & (u <= zk[1])) * 1.0
    else:
        q = lambda u: gamma + (1 - gamma) * inK(u)
        sta = lambda u: np.ones_like(u)
    aw = lambda u: np.sqrt(sta(u) * q(u))
    return q, aw, sta


# ---------------------------------------------------------------- simulation
def run(kap, gamma, design='ts', R=5000, n_max=400, seed=0, misspec=False, every_n=True, ck=CK,
        zc=ZC, zk=ZK, clip=CLIP, prior_sd=PRIOR_SD, keep_paths=3, kap_targets=None, est_bins=None, store=True,
        lam=1.0, greedy=False, batch=1):
    """One Monte Carlo experiment, vectorised over R replications.
    lam: tempering of the allocation probability, p_t = Phi(lam * (mu - kappa0) / s) (lam = 1: Thompson);
    greedy: p_t = 1{posterior mean > kappa0} (then clipped); batch: wells placed in campaigns of `batch`
    with the allocation probability frozen within a campaign."""
    rng = np.random.default_rng(seed)
    th = np.array([A_IN, BETA, kap])
    P0 = np.diag(1 / prior_sd ** 2); P0m = P0 @ PRIOR_M
    wK, wC = zk[1] - zk[0], zc[1] - zc[0]
    A = np.zeros((3, R, 3, 3)); b = np.zeros((3, R, 3))
    T2 = np.zeros((3, R, 3, 3)); T3 = np.zeros((3, R, 3, 3, 3)); T4 = np.zeros((3, R, 3, 3, 3, 3))
    yy = np.zeros(R); nK = np.zeros(R); nC = np.zeros(R)
    sumW2 = np.zeros(R); maxW2 = np.zeros(R)
    paths = dict(u=np.zeros((keep_paths, n_max)), p=np.zeros((keep_paths, n_max)))
    names_ev = ('olscl', 'olssw', 'aw', 'ipw', 'cs1', 'csw')
    ever = {k: np.zeros(R, bool) for k in names_ev}
    ever_curve = {k: np.full(n_max, np.nan) for k in names_ev}
    width_curve = {k: np.full(n_max, np.nan) for k in names_ev}
    pbar = np.zeros(n_max)
    out_ck = {}
    if store:
        SU = np.zeros((n_max, R)); SY = np.zeros((n_max, R)); SQ = np.zeros((n_max, R))
    for t in range(n_max):
        n = t + 1
        if design == 'ts':
            if t % batch == 0:
                P = P0[None] + A[0] / SIG ** 2
                S = np.linalg.inv(P)
                mu = np.einsum('rij,rj->ri', S, P0m[None] + b[0] / SIG ** 2)
                zpost = (mu[:, 2] - KAP0) / np.sqrt(S[:, 2, 2])
                pk_cur = (zpost > 0).astype(float) if greedy else norm.cdf(lam * zpost)
                if gamma == 0 or greedy:
                    pk_cur = np.clip(pk_cur, clip, 1 - clip)
            pk = pk_cur
            r = rng.random(R)
            coast = rng.random(R) < pk
            unif = rng.random(R) < gamma
            u = np.where(coast, zk[0] + wK * r, zc[0] + wC * r)
            u = np.where(unif, rng.random(R), u)
            inK = (u >= zk[0]) & (u <= zk[1]); inC = (u >= zc[0]) & (u <= zc[1])
            q = gamma + (1 - gamma) * (pk * inK / wK + (1 - pk) * inC / wC)
        else:
            pk = np.full(R, np.nan)
            u = rng.random(R); q = np.ones(R)
            inK = (u >= zk[0]) & (u <= zk[1]); inC = (u >= zc[0]) & (u <= zc[1])
        pbar[t] = np.nanmean(pk) if design == 'ts' else np.nan
        if keep_paths:
            paths['u'][:, t] = u[:keep_paths]; paths['p'][:, t] = pk[:keep_paths]
        z = feats(u)
        y = head(u, kap, misspec) + SIG * rng.standard_normal(R)
        W2 = 1.0 / q; W = np.sqrt(W2)
        if store:
            SU[t] = u; SY[t] = y; SQ[t] = q
        sumW2 += W2; maxW2 = np.maximum(maxW2, W2)
        nK += inK; nC += inC; yy += y * y
        zz = np.einsum('ri,rj->rij', z, z)
        zzz = np.einsum('ri,rjk->rijk', z, zz)
        z4 = np.einsum('rij,rkl->rijkl', zz, zz)
        for k, w in enumerate((np.ones(R), W, W2)):
            w2 = w * w
            A[k] += w[:, None, None] * zz; b[k] += (w * y)[:, None] * z
            T2[k] += (w2 * y * y)[:, None, None] * zz
            T3[k] += (w2 * y)[:, None, None, None] * zzz
            T4[k] += w2[:, None, None, None, None] * z4
        if n < N_EV0 or (not every_n and n not in ck):
            continue
        # ------------------------------------------------ statistics at sample size n
        st = {}
        for k, nm in enumerate(('ols', 'aw', 'ipw')):
            Ai = np.linalg.inv(A[k]); est = np.einsum('rij,rj->ri', Ai, b[k])
            Bm = T2[k] - 2 * np.einsum('rlij,rl->rij', T3[k], est) + np.einsum('rlmij,rl,rm->rij', T4[k], est, est)
            V = np.einsum('rij,rjk,rlk->ril', Ai, Bm, Ai) * n / (n - 3)
            st[nm] = dict(Ai=Ai, est=est, se=np.sqrt(np.maximum(V[:, 2, 2], 1e-300)), Bm=Bm * n / (n - 3), A=A[k])
        rss = np.maximum(yy - np.einsum('ri,ri->r', st['ols']['est'], b[0]), 1e-300)
        se_cl = np.sqrt(rss / (n - 3) * st['ols']['Ai'][:, 2, 2])
        se_known = SIG * np.sqrt(st['ols']['Ai'][:, 2, 2])
        tq = tdist.ppf(1 - ALPHA / 2, n - 3); zq = norm.ppf(1 - ALPHA / 2)
        half = dict(olscl=tq * se_cl, olssw=zq * st['ols']['se'], aw=zq * st['aw']['se'], ipw=zq * st['ipw']['se'])
        cen = dict(olscl=st['ols']['est'][:, 2], olssw=st['ols']['est'][:, 2], aw=st['aw']['est'][:, 2],
                   ipw=st['ipw']['est'][:, 2])
        for nm, kA, kG in (('cs1', 0, 0), ('csw', 1, 2)):
            HG = HMIX[None] + A[kG]
            beta2 = 2 * np.log(1 / ALPHA) + np.linalg.slogdet(HG)[1] - LOGDET_H
            a2 = st['ols' if kA == 0 else 'aw']['Ai'][:, 2, :]
            half[nm] = SIG * np.sqrt(beta2 * np.einsum('ri,rij,rj->r', a2, HG, a2))
            cen[nm] = st['ols' if kA == 0 else 'aw']['est'][:, 2]
        if every_n:
            for nm in names_ev:
                ever[nm] |= np.abs(cen[nm] - kap) > half[nm]
                ever_curve[nm][t] = ever[nm].mean()
                width_curve[nm][t] = np.median(2 * half[nm])
        if n in ck:
            o = {}
            zst = dict(olscl=(cen['olscl'] - kap) / se_cl, olssw=(cen['olssw'] - kap) / st['ols']['se'],
                       aw=(cen['aw'] - kap) / st['aw']['se'], ipw=(cen['ipw'] - kap) / st['ipw']['se'],
                       olsk=(cen['olscl'] - kap) / se_known)
            crit = dict(olscl=tq, olssw=zq, aw=zq, ipw=zq, olsk=zq)
            for nm, zv in zst.items():
                c = crit[nm]
                o[nm] = dict(cov=np.mean(np.abs(zv) <= c), up=np.mean(zv > c), lo=np.mean(zv < -c),
                             mean_z=zv.mean(), sd_z=zv.std(), skew_z=float(((zv - zv.mean()) ** 3).mean() / zv.std() ** 3),
                             hist=np.histogram(np.clip(zv, -4.999, 4.999), bins=ZBINS)[0],
                             onesided_fa=np.mean(zv > (tdist.ppf(1 - ALPHA, n - 3) if nm == 'olscl' else norm.ppf(1 - ALPHA))))
            for nm, kk in (('olssw', 'ols'), ('aw', 'aw'), ('ipw', 'ipw')):
                sv = st[kk]['A'] @ (st[kk]['est'] - th)[..., None]
                Q = np.einsum('ri,ri->r', sv[..., 0], np.linalg.solve(st[kk]['Bm'], sv)[..., 0])
                o[nm]['cov_joint'] = np.mean(Q <= chi2.ppf(1 - ALPHA, 3))
            if store:
                # leverage-corrected (HC3-type) meat: r_t^2 / (1 - h_t)^2, h_t = w_t z_t' A^{-1} z_t
                Zs = feats(SU[:n]); Ws2 = 1.0 / SQ[:n]
                for nm, kk, ws in (('olssw', 'ols', np.ones_like(Ws2)), ('aw', 'aw', np.sqrt(Ws2)), ('ipw', 'ipw', Ws2)):
                    hl = ws * np.einsum('nri,rij,nrj->nr', Zs, st[kk]['Ai'], Zs)
                    rr = SY[:n] - np.einsum('nri,ri->nr', Zs, st[kk]['est'])
                    B3 = np.einsum('nr,nri,nrj->rij', ws ** 2 * rr ** 2 / (1 - hl) ** 2, Zs, Zs)
                    V3 = np.einsum('rij,rjk,rlk->ril', st[kk]['Ai'], B3, st[kk]['Ai'])
                    st[kk]['se3'] = np.sqrt(V3[:, 2, 2])
                    z3 = (st[kk]['est'][:, 2] - kap) / st[kk]['se3']
                    o[nm]['hc3'] = dict(cov=np.mean(np.abs(z3) <= zq), up=np.mean(z3 > zq), lo=np.mean(z3 < -zq),
                                        mean_z=z3.mean(), sd_z=z3.std(), width_med=np.median(2 * zq * np.sqrt(V3[:, 2, 2])),
                                        hist=np.histogram(np.clip(z3, -4.999, 4.999), bins=ZBINS)[0],
                                        cov_proj=np.mean(np.abs(z3) <= np.sqrt(chi2.ppf(1 - ALPHA, 3))))
                    sv = st[kk]['A'] @ (st[kk]['est'] - th)[..., None]
                    Q = np.einsum('ri,ri->r', sv[..., 0], np.linalg.solve(B3, sv)[..., 0])
                    o[nm]['hc3']['cov_joint'] = np.mean(Q <= chi2.ppf(1 - ALPHA, 3))
            o['aw']['cov_uncorr'] = np.mean(np.abs(zst['aw']) <= zq * np.sqrt((n - 3) / n))
            o['aw']['cov_proj'] = np.mean(np.abs(zst['aw']) <= np.sqrt(chi2.ppf(1 - ALPHA, 3)))
            for nm in ('cs1', 'csw'):
                miss = np.abs(cen[nm] - kap) > half[nm]
                o[nm] = dict(cov=1 - miss.mean(), up=np.mean(cen[nm] - half[nm] > kap), lo=np.mean(cen[nm] + half[nm] < kap))
            for nm in ('olscl', 'olssw', 'aw', 'ipw', 'cs1', 'csw'):
                o[nm]['width_med'] = np.median(2 * half[nm])
                o[nm]['width_mean'] = np.mean(2 * half[nm])
            for nm in ('ols', 'aw', 'ipw'):
                e = st[nm]['est'][:, 2]
                o[nm + '_est'] = dict(mean=e.mean(), sd=e.std(), bias=e.mean() - kap, q05=np.quantile(e, 0.05),
                                      q95=np.quantile(e, 0.95))
                if kap_targets is not None:
                    for tn, tv in kap_targets.items():
                        o[nm + '_est']['cov_' + tn] = np.mean(np.abs(e - tv) <= zq * st[nm]['se'])
                        if store:
                            o[nm + '_est']['cov3_' + tn] = np.mean(np.abs(e - tv) <= zq * st[nm]['se3'])
                if est_bins is not None:
                    o[nm + '_est']['hist'] = np.histogram(e, bins=est_bins)[0]
            share = nK / n
            o['share_K'] = dict(mean=share.mean(), sd=share.std(), hist=np.histogram(share, bins=np.linspace(0, 1, 26))[0],
                                q05=np.quantile(share, 0.05), q95=np.quantile(share, 0.95))
            o['share_C'] = (nC / n).mean()
            o['W2'] = dict(mean=(sumW2 / n).mean(), max=maxW2.max())
            out_ck[n] = o
    res = dict(ck=out_ck, pbar=pbar, R=R, n_max=n_max, gamma=gamma, design=design, kap=kap)
    if every_n:
        res['ever'] = ever_curve; res['width'] = width_curve
    if keep_paths:
        res['paths'] = paths
    return res


VARIANTS = [
    ('base', {}),
    ('K=[0.9,1]', dict(zk=(0.9, 1.0))),
    ('K=[0.8,1]', dict(zk=(0.8, 1.0))),
    ('C=[0.35,0.65]', dict(zc=(0.35, 0.65))),
    ('C=[0.2,0.8]', dict(zc=(0.2, 0.8))),
    ('clip=0.05', dict(clip=0.05)),
    ('clip=0.001', dict(clip=0.001)),
    ('prior sd(kappa)=0.2', dict(prior_sd=np.array([1.0, 1.0, 0.2]))),
    ('prior sd(kappa)=5', dict(prior_sd=np.array([1.0, 1.0, 5.0]))),
    ('tempered lambda=0.5', dict(lam=0.5)),
    ('tempered lambda=3', dict(lam=3.0)),
    ('greedy (posterior mean)', dict(greedy=True)),
    ('campaigns of 10 wells', dict(batch=10)),
]
CKL = CK + (800, 1600)
CKM = (100, 200, 400, 800, 1600)
EST_BINS = np.linspace(3.6, 4.9, 66)


def jobs():
    J = []
    for i, g in enumerate(GAMMAS + ('unif',)):          # B. misspecified, margin truth, n up to 1600
        J.append(dict(kind='misspec', path=('misspec', f'g{g}' if g != 'unif' else 'unif'), g=g, seed=300 + i))
    for tag, kap, seed0 in (('zero', KAP0, 700), ('margin', KAP1, 800)):   # A2. long runs
        for i, g in enumerate((0.0, 0.2)):
            J.append(dict(kind='run', path=('long', f'{tag}_g{g}'), args=(kap, g),
                          kw=dict(R=RLONG, n_max=1600, seed=seed0 + i, every_n=False, ck=CKL, keep_paths=0)))
    for tag, kap, seed0 in (('zero', KAP0, 100), ('margin', KAP1, 200)):   # A. all designs, every n
        for i, g in enumerate(GAMMAS):
            J.append(dict(kind='run', path=(tag, f'g{g}'), args=(kap, g), kw=dict(R=RMAIN, seed=seed0 + i)))
        J.append(dict(kind='run', path=(tag, 'unif'), args=(kap, 1.0), kw=dict(design='unif', R=RMAIN, seed=seed0 + 9)))
    for i, (nm, kw) in enumerate(VARIANTS):            # C. exploration, zero margin, gamma = 0
        J.append(dict(kind='explore', path=('explore', nm), args=(KAP0, 0.0),
                      kw=dict(R=REXP, seed=500 + i, every_n=False, ck=(100, 400), keep_paths=0, **kw), rec=kw))
    return J


def do_job(spec):
    t0 = time.time()
    if spec['kind'] == 'misspec':
        g = spec['g']
        if g == 'unif':
            tg = dict(ols=projection(lambda u: np.ones_like(u), KAP1, True)[2])
            tg['aw'] = tg['ipw'] = tg['sta'] = tg['ols']
            r = run(KAP1, 1.0, design='unif', R=RMIS, n_max=1600, seed=spec['seed'], misspec=True, every_n=False,
                    ck=CKM, keep_paths=0, kap_targets=tg, est_bins=EST_BINS)
        else:
            qd, awd, sta = limit_designs(g)
            tg = dict(ols=projection(qd, KAP1, True)[2], aw=projection(awd, KAP1, True)[2],
                      ipw=projection(sta, KAP1, True)[2], sta=projection(lambda u: np.ones_like(u), KAP1, True)[2])
            r = run(KAP1, g, R=RMIS, n_max=1600, seed=spec['seed'], misspec=True, every_n=False, ck=CKM, keep_paths=0,
                    kap_targets=tg, est_bins=EST_BINS)
        r['targets'] = tg
    else:
        r = run(*spec['args'], **spec['kw'])
        if spec['kind'] == 'explore':
            r = dict(kw={k: (list(v) if hasattr(v, '__len__') else v) for k, v in spec['rec'].items()}, R=r['R'],
                     ck={n: {e: {k: r['ck'][n][e][k] for k in ('cov', 'up', 'lo', 'mean_z', 'sd_z', 'onesided_fa')}
                             for e in ('olscl', 'olsk', 'olssw', 'aw', 'ipw')}
                         | {'share_K_mean': r['ck'][n]['share_K']['mean'], 'share_K_sd': r['ck'][n]['share_K']['sd'],
                            'aw_hc3': r['ck'][n]['aw']['hc3']['cov'], 'olssw_hc3': r['ck'][n]['olssw']['hc3']['cov'],
                            'ols_bias': r['ck'][n]['ols_est']['bias'], 'ols_sd': r['ck'][n]['ols_est']['sd']}
                         for n in (100, 400)})
    return spec['path'], r, time.time() - t0


def brief(path, r):
    c = r['ck']
    if path[0] == 'misspec':
        return {n: (round(c[n]['ols_est']['mean'], 3), round(c[n]['aw_est']['mean'], 3), round(c[n]['ipw_est']['mean'], 3))
                for n in (400, 1600)}, {k: round(v, 3) for k, v in r['targets'].items()}
    if path[0] == 'explore':
        return {n: (round(c[n]['olscl']['cov'], 3), round(c[n]['olscl']['up'], 3), round(c[n]['olscl']['onesided_fa'], 3))
                for n in (100, 400)}
    ns = [n for n in (25, 100, 400, 1600) if n in c]
    return {n: (round(c[n]['olscl']['cov'], 3), round(c[n]['aw']['cov'], 3), round(c[n]['aw']['hc3']['cov'], 3),
                round(c[n]['ipw']['cov'], 3), round(c[n]['csw']['cov'], 3)) for n in ns}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--workers', type=int, default=3)
    a = ap.parse_args()
    t00 = time.time()
    J = dict(setting=dict(L_km=L_KM, sigma=SIG, T=T_TR, N0_mm=N0_MM, N1_mm=N1_MM, kappa0=KAP0, kappa1=KAP1,
                          c0=C0, c1=C1, a=A_IN, beta=BETA, h_coast=H_COAST, zone_C=ZC, zone_K=ZK, clip=CLIP,
                          prior_mean=PRIOR_M, prior_sd=PRIOR_SD, gammas=GAMMAS, alpha=ALPHA, n_ref=NREF,
                          checkpoints=CK, n_ev0=N_EV0, bump=BUMP, R_main=RMAIN, R_long=RLONG, R_mis=RMIS, R_explore=REXP),
             zero={}, margin={}, long=dict(ck=CKL), misspec=dict(ck=CKM, est_bins=EST_BINS, quadratic_kappa=KAP1),
             explore={})
    timing = {}
    with mp.get_context('fork').Pool(a.workers) as pool:
        for path, r, dt in pool.imap_unordered(do_job, jobs()):
            J[path[0]][path[1]] = r
            timing['/'.join(path)] = dt
            print('/'.join(path), brief(path, r), f'{dt:.1f}s', f'[{time.time() - t00:.0f}s]', flush=True)
    J['explore_order'] = [nm for nm, _ in VARIANTS]
    J['timing_s'] = timing
    J['workers'] = a.workers
    J['runtime_s'] = time.time() - t00
    print('total wall time', round(J['runtime_s'], 1), 's; summed job time', round(sum(timing.values()), 1), 's')
    dump(J, 'aquifer.json')


if __name__ == '__main__':
    main()
