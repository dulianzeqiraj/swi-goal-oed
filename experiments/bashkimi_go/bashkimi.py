"""BASHKIMI-GO: which institution's well records are worth merging, before any record is shared, to decide
which Fushe-Kuqe wells may keep pumping hard in summer.

Innovation of literature review 55 (anchor: Fawkes, Ter-Minassian, Ivanova, Shalit & Holmes, AISTATS 2025,
"Is merging worth it? Securely evaluating the information gain for causal dataset acquisition").

Truth (unknown to everybody).
  Aquifer: the Fushe-Kuqe sector model (fk_geo.FKGeo) with log T = log(K0 b) + theta[zone] + zeta(x), theta ~ N(0, Gam)
    on the 12 zones and zeta a Gaussian field (sd 0.35, range 2 km), as in VENDI-GO.
  Treatment: high (a = 1) versus low (a = 0) summer pumping of a well; the high level is DQ = 1 500 m3/d more.
  Outcome: the seasonal change of log chloride at the well,
      y = b(x) + a tau(x) + u_well + e,   tau(x) = gam DQ [A^-1]_xx exp(-(h_n(x) - h_c) / lam),
    [A^-1]_xx the self-drawdown of the flow matrix A at the well, h_n the natural head, h_c = 1 m (Ghyben-Herzberg):
    extra drawdown matters where the fresh-water head margin is small, near the saltwater toe. The site chemistry
    (gam: scale of the chloride response, lam: its decay with the head margin, the drift scale) is uncertain.
  Covariates every holder records: distance to the sea d and the log T of the well's pumping test (error sd 0.25).
  Holders: the water utility (host: inland supply wells, pumped hard), the monitoring agency (many inland wells,
    balanced), private irrigators (mid plain, pumped hard), coastal hotels (few wells near the sea, very variable
    pumping) and a research campaign (designed tests anywhere). The treatment probability depends on the holder,
    hence on location, so the groups overlap poorly near the coast.
  Decision: for each of J = 40 target wells (0.3-6 km from the sea) allow high pumping (loss L (tau - t)_+) or cap it
    (loss C_CAP of water not supplied); Bayes action under the current belief.
Bayesian model shared by all holders (Gaussian, linear in the parameters):
  y = psi_b(x)'beta + a [psi_t(x)'gamma + s(x) rho(x) + s(x) nu(x)] + noise,
  psi_b = [1, log d, (log d)^2, drift shape of the mean model]; psi_t = [1, f(x; 1.0), f(x; 1.5), f(x; 2.5)],
  f(x; lam) the effect the mean 12-zone model predicts for decay length lam with the self-drawdown corrected by the
  well's pumping-test T (physics-informed CATE basis); s(x) the prior-mean effect; rho a Gaussian field for the
  relative error of the physics (squared-exponential, predictive process on a 1.5 km lattice of the coastal strip),
  nu a local nugget. Prior, field scale and range are calibrated on 400 physical draws (approximation-error approach).
Criteria of the value of merging candidate k with the host, all computed from (weighted) Gram matrices only
  (Proposition B1): EIG of all parameters, EIG of the CATE parameters (the anchor's criterion), mean EIG of the
  target CATEs, and the BASHKIMI-GO decision value: the expected fall of the Bayes risk of the capping decision
  (Proposition B3). Truth of the comparison: merge for real, decide, and score the decision with the true tau.
Run: python3 bashkimi.py calibrate ; python3 bashkimi.py run 200 ; python3 bashkimi_summary.py
"""
import os, sys, json, time
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np
import scipy.sparse.linalg as spla
from scipy.special import ndtr
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'vendi_go'))
import vendi as V

OUT = os.path.join(HERE, 'res')
m = V.m
VI = np.flatnonzero(m.valid)
HC = 1.0
DQ = 1500.0          # m3/d, high minus low summer pumping
GAM_CL = 1.5         # log-chloride change per metre of extra drawdown at the toe (central value)
LAM_H = 1.5          # m, decay of the effect with the head margin above h_c (central value)
SD_GAM = 0.6         # sd of log gam across plausible aquifers (mixing, dispersion)
SD_LAM = 0.3         # sd of log lam
SIG_E = 0.12         # season noise of the log-chloride change
SIG_U = 0.05         # well effect
SIG_LT = 0.25        # error of the pumping-test log T
T_TOL = 0.10         # tolerated log-chloride rise
L_SAL = 1.0          # loss per unit excess rise when pumping high
C_CAP = 0.03         # loss of capping (water not supplied), same units
NGH = 40
GHX, GHW = np.polynomial.hermite_e.hermegauss(NGH); GHW = GHW / GHW.sum()
S_FLOOR = 0.02       # floor of the effect scale s(x)
STRIP = 7.5          # km, coastal strip carrying the discrepancy field
LAT = 1.5            # km, lattice of the predictive process
LAMS = (1.0, 1.5, 2.5)
MODEL = os.environ.get('BASH_MODEL', 'phys')   # 'phys': physics-informed CATE basis; 'poly': generic polynomial (anchor)
TAG = '' if MODEL == 'phys' else '_' + MODEL

# distance to the sea contact (km)
_sx, _sy = m.cx[m.sea_idx], m.cy[m.sea_idx]
DIST = np.full(m.Nc, np.nan)
DIST[VI] = np.min(np.hypot(m.cx[VI, None] - _sx[None], m.cy[VI, None] - _sy[None]), axis=1) + 0.125
LT0 = np.log(m.K0c * m.P['b'])
_step = int(round(LAT / m.P['dx']))
UCELL = VI[(DIST[VI] <= STRIP) & (m.ai[VI] % _step == 0) & (m.aj[VI] % _step == 0)]
NU = len(UCELL)

HOLDERS = [  # name, wells, seasons, distance range (km), P(high pumping)
    dict(key='H', name='Water utility (host)', nw=20, ns=3, d=(4.0, 10.0), p=0.90),
    dict(key='A', name='Monitoring agency', nw=60, ns=5, d=(3.0, 14.5), p=0.50),
    dict(key='I', name='Private irrigators', nw=30, ns=4, d=(1.5, 5.0), p=0.85),
    dict(key='T', name='Coastal hotels', nw=8, ns=4, d=(0.2, 1.5), p=0.50),
    dict(key='R', name='Research campaign', nw=12, ns=2, d=(0.2, 14.5), p=0.50),
]
CAND = [1, 2, 3, 4]
NT = 40
TARGET_D = (0.3, 6.0)


# ------------------------------------------------------------------ physics
def self_drawdown(lu, cells):
    E = np.zeros((m.Nc, len(cells))); E[cells, np.arange(len(cells))] = 1.0
    return lu.solve(E)[cells, np.arange(len(cells))]


def tau_of(hn, g, gam=GAM_CL, lam=LAM_H):
    return gam * DQ * g * np.exp(-(hn - HC) / lam)


def drift_of(hn, lam=LAM_H, bsc=0.10):
    return 0.02 + bsc * np.exp(-(hn - HC) / lam)


def chem_draw(rng):
    """site hydrochemistry no model knows in advance: scale of the chloride response, its decay with the head
    margin, scale of the seasonal drift."""
    return (GAM_CL * np.exp(SD_GAM * rng.standard_normal()), LAM_H * np.exp(SD_LAM * rng.standard_normal()),
            0.10 * np.exp(0.5 * rng.standard_normal()))


_M0 = None
def model_fields():
    """natural head and self-drawdown of the mean 12-zone model at every valid cell."""
    global _M0
    if _M0 is None:
        fn = os.path.join(OUT, 'model0.npz')
        if os.path.exists(fn):
            Z = np.load(fn); _M0 = (Z['hn0'], Z['g0'])
        else:
            lu = spla.splu(V.matrix(np.zeros(m.Nz))); hn = lu.solve(m.rhs)
            g = np.zeros(m.Nc)
            for ch in np.array_split(VI, 12):
                g[ch] = self_drawdown(lu, ch)
            os.makedirs(OUT, exist_ok=True); np.savez(fn, hn0=hn, g0=g); _M0 = (hn, g)
    return _M0


# ------------------------------------------------------------------ features
def raw_features(cells, lt):
    hn0, g0 = model_fields()
    u = np.log(DIST[cells]); e = hn0[cells] - HC
    rb = np.c_[u, u ** 2, np.exp(-e / LAM_H)]
    if MODEL == 'poly':
        return rb, np.c_[u, u ** 2, lt]
    s0 = GAM_CL * DQ * g0[cells] * np.exp(LT0[cells] - lt)
    rt = np.column_stack([s0 * np.exp(-e / l) for l in LAMS])
    return rb, rt


CAL = None
def load_calib():
    global CAL
    if CAL is None:
        Z = np.load(os.path.join(OUT, f'calib{TAG}.npz'))
        CAL = {k: Z[k] for k in Z.files}
        _gp_setup()
    return CAL


def base_features(cells, lt):
    rb, rt = raw_features(cells, lt)
    return (np.c_[np.ones(len(cells)), (rb - CAL['FMUb']) / CAL['FSDb']],
            np.c_[np.ones(len(cells)), (rt - CAL['FMUt']) / CAL['FSDt']])


def k_se(c1, c2):
    D2 = (m.cx[c1][:, None] - m.cx[c2][None]) ** 2 + (m.cy[c1][:, None] - m.cy[c2][None]) ** 2
    return np.exp(-D2 / CAL['ell'] ** 2)


def _gp_setup():
    K = k_se(UCELL, UCELL) + 1e-6 * np.eye(NU)
    CAL['KUU'] = K; CAL['KUU_inv'] = np.linalg.inv(K)


def features(cells, lt):
    """Pb (baseline), Pc (CATE: physics basis and discrepancy field), s (effect scale)."""
    Pb, Pt = base_features(cells, lt)
    s = np.maximum(np.abs(Pt @ CAL['mg']), S_FLOOR)
    A = k_se(cells, UCELL) @ CAL['KUU_inv']
    return Pb, np.c_[Pt, s[:, None] * A], s


PB, PT = 4, 4


def prior():
    load_calib()
    p = PB + PT + NU
    mu = np.zeros(p); mu[:PB] = CAL['mb']; mu[PB:PB + PT] = CAL['mg']
    S = np.zeros((p, p))
    S[:PB, :PB] = CAL['Cb'] * 4.0 + 1e-4 * np.eye(PB)
    S[PB:PB + PT, PB:PB + PT] = CAL['Cg'] * 2.0 + 1e-5 * np.eye(PT)
    S[PB + PT:, PB + PT:] = CAL['s_gp'] ** 2 * CAL['KUU']
    return mu, S


def sig_base():
    return float(np.sqrt(SIG_E ** 2 + SIG_U ** 2 + CAL['res_b'] ** 2))


def design(w):
    """rows of the design and their noise sd (depends on x and a only)."""
    Pb, Pc, s = features(w['cells'], w['lt'])
    Phi = np.c_[Pb, w['a'][:, None] * Pc]
    sd = np.sqrt(sig_base() ** 2 + w['a'] * (s * CAL['s_nug']) ** 2)
    return Phi, sd


def gram(Phi, sd):
    Q = Phi / sd[:, None]
    return Q.T @ Q


def targets(cells, lt):
    _, Pc, s = features(cells, lt)
    return np.c_[np.zeros((len(cells), PB)), Pc], (s * CAL['s_nug']) ** 2


# ------------------------------------------------------------------ belief, decision and value
def posterior(Phi, sd, y, mu, S):
    Q = Phi / sd[:, None]; z = y / sd
    K = S @ Q.T
    M = Q @ K + np.eye(len(y))
    Gm = np.linalg.solve(M, K.T)
    return mu + Gm.T @ (z - Q @ mu), S - K @ Gm


def post_info(G, S):
    """posterior covariance after adding the information G (weighted Gram matrix)."""
    L = np.linalg.cholesky(S + 1e-12 * np.eye(len(S)))
    Mi = np.linalg.inv(np.eye(len(S)) + L.T @ G @ L)
    return L @ Mi @ L.T


def psiN(z):
    return np.exp(-0.5 * z * z) / np.sqrt(2 * np.pi) + z * ndtr(z)


def bayes_risk(mu, v):
    sd = np.sqrt(np.maximum(v, 1e-14))
    return np.minimum(C_CAP, L_SAL * sd * psiN((mu - T_TOL) / sd))


def act(mu, v):
    """1 = allow high pumping."""
    sd = np.sqrt(np.maximum(v, 1e-14))
    return (L_SAL * sd * psiN((mu - T_TOL) / sd) < C_CAP).astype(float)


def true_loss(a, tau):
    return float(np.sum(a * L_SAL * np.maximum(tau - T_TOL, 0) + (1 - a) * C_CAP))


def qform(C, S):
    return np.einsum('ij,jk,ik->i', C, S, C)


def decision_value(mu0, S0, S1, Ct, vn):
    """Proposition B3: expected fall of the Bayes risk at each target; the preposterior of the target mean is
    N(m0, v0 - v1) and the nugget vn is irreducible."""
    m0 = Ct @ mu0
    v0 = qform(Ct, S0); v1 = qform(Ct, S1)
    s = np.sqrt(np.maximum(v0 - v1, 0))
    r0 = bayes_risk(m0, v0 + vn)
    r1 = bayes_risk(m0[:, None] + s[:, None] * GHX[None], (v1 + vn)[:, None]) @ GHW
    return r0 - r1, v0, v1


def criteria(mu0, S0, G, Ct, vn):
    S1 = post_info(G, S0)
    i1, i2 = PB, PB + PT + NU
    _, ld0 = np.linalg.slogdet(S0); _, ld1 = np.linalg.slogdet(S1)
    _, lg0 = np.linalg.slogdet(S0[i1:i2, i1:i2]); _, lg1 = np.linalg.slogdet(S1[i1:i2, i1:i2])
    Vj, v0, v1 = decision_value(mu0, S0, S1, Ct, vn)
    return dict(eig_all=0.5 * (ld0 - ld1), eig_cate=0.5 * (lg0 - lg1),
                eig_goal=float(np.mean(0.5 * np.log((v0 + vn) / (v1 + vn)))), value=float(Vj.sum())), S1


def cate_info(G):
    """information on the CATE parameters with a flat prior on the baseline: Schur complement (Proposition B2)."""
    return G[PB:, PB:] - G[PB:, :PB] @ np.linalg.pinv(G[:PB, :PB]) @ G[:PB, PB:]


# ------------------------------------------------------------------ one world
def sample_cells(rng, dr, n):
    pool = VI[(DIST[VI] >= dr[0]) & (DIST[VI] <= dr[1])]
    return rng.choice(pool, n, replace=len(pool) < n)


def make_world(i):
    if V.LZ is None:
        V.zeta_chol()
    rng = np.random.default_rng(550000 + i)
    th = V.LG @ rng.standard_normal(m.Nz); ze = V.draw_zeta(rng)
    lu = spla.splu(V.matrix(th, ze)); hn = lu.solve(m.rhs)
    lT = LT0 + th[m.zone] + ze
    gam, lam, bsc = chem_draw(rng)
    W = []
    for h in HOLDERS:
        wells = sample_cells(rng, h['d'], h['nw'])
        cells = np.repeat(wells, h['ns'])
        widx = np.repeat(np.arange(h['nw']), h['ns'])
        a = (rng.random(len(cells)) < h['p']).astype(float)
        lt_meas = (lT[wells] + SIG_LT * rng.standard_normal(h['nw']))[widx]
        W.append(dict(wells=wells, cells=cells, widx=widx, a=a, lt=lt_meas))
    tg = sample_cells(rng, TARGET_D, NT)
    tg_lt = lT[tg] + SIG_LT * rng.standard_normal(NT)
    need = np.unique(np.r_[np.concatenate([w['wells'] for w in W]), tg])
    gq = dict(zip(need, self_drawdown(lu, need)))
    for k, (h, w) in enumerate(zip(HOLDERS, W)):
        g = np.array([gq[c] for c in w['cells']])
        w['tau'] = tau_of(hn[w['cells']], g, gam, lam)
        w['ymean'] = drift_of(hn[w['cells']], lam, bsc) + w['a'] * w['tau']
        w['y'] = draw_y(i, k, 0, h, w)
    tau_t = tau_of(hn[tg], np.array([gq[c] for c in tg]), gam, lam)
    return dict(i=i, W=W, tg=tg, tg_lt=tg_lt, tau_t=tau_t, chem=(gam, lam, bsc))


def draw_y(i, k, rep, h, w):
    """outcomes of holder k in world i, replicate rep (well effects and season noise only)."""
    r = np.random.default_rng([550000 + i, k, rep])
    return w['ymean'] + SIG_U * r.standard_normal(h['nw'])[w['widx']] + SIG_E * r.standard_normal(len(w['cells']))


# ------------------------------------------------------------------ calibration (approximation-error approach)
def calib_member(i):
    if V.LZ is None:
        V.zeta_chol()
    rng = np.random.default_rng(910000 + i)
    th = V.LG @ rng.standard_normal(m.Nz); ze = V.draw_zeta(rng)
    lu = spla.splu(V.matrix(th, ze)); hn = lu.solve(m.rhs)
    lT = LT0 + th[m.zone] + ze
    pool = VI[DIST[VI] <= 14.5]
    cells = pool[rng.choice(len(pool), 250, replace=False)]
    g = self_drawdown(lu, cells)
    lt = lT[cells] + SIG_LT * rng.standard_normal(len(cells))
    gam, lam, bsc = chem_draw(rng)
    return cells, lt, tau_of(hn[cells], g, gam, lam), drift_of(hn[cells], lam, bsc)


def calibrate(n=400):
    global CAL
    os.makedirs(OUT, exist_ok=True)
    V.zeta_chol(); model_fields()
    with Pool(4) as pool:
        R = pool.map(calib_member, range(n))
    RB, RT = zip(*[raw_features(c, lt) for c, lt, _, _ in R])
    RB, RT = np.vstack(RB), np.vstack(RT)
    CAL = dict(FMUb=RB.mean(0), FSDb=RB.std(0), FMUt=RT.mean(0), FSDt=RT.std(0))
    BG, BB, RESB = [], [], []
    for c, lt, tau, b in R:
        Xb, Xt = base_features(c, lt)
        cg, *_ = np.linalg.lstsq(Xt, tau, rcond=None); cb, *_ = np.linalg.lstsq(Xb, b, rcond=None)
        BG.append(cg); BB.append(cb); RESB.append(b - Xb @ cb)
    BG, BB = np.array(BG), np.array(BB)
    CAL.update(mg=BG.mean(0), Cg=np.cov(BG, rowvar=False), mb=BB.mean(0), Cb=np.cov(BB, rowvar=False),
               res_b=np.concatenate(RESB).std())
    # relative error of the physics basis: variance, spatial correlation (squared exponential + nugget)
    rels, bins = [], np.array([0, 0.5, 1, 1.5, 2, 3, 4, 6, 8])
    num = np.zeros(len(bins) - 1); den = np.zeros(len(bins) - 1)
    allt = []
    for (c, lt, tau, b), cg in zip(R, BG):
        Xb, Xt = base_features(c, lt)
        s = np.maximum(np.abs(Xt @ CAL['mg']), S_FLOOR)
        rel = (tau - Xt @ cg) / s
        k = (DIST[c] <= STRIP) & (s > 2 * S_FLOOR)
        r, cc = rel[k], c[k]; rels.append(r); allt.append(tau)
        D = np.hypot(m.cx[cc][:, None] - m.cx[cc][None], m.cy[cc][:, None] - m.cy[cc][None])
        P = r[:, None] * r[None]
        iu = np.triu_indices(len(r), 1)
        bi = np.digitize(D[iu], bins) - 1
        ok = (bi >= 0) & (bi < len(num))
        np.add.at(num, bi[ok], P[iu][ok]); np.add.at(den, bi[ok], 1)
    r = np.concatenate(rels); var = float(np.mean(r ** 2))
    corr = num / np.maximum(den, 1) / var
    mid = 0.5 * (bins[1:] + bins[:-1])
    best = None
    for ell in np.arange(1.0, 6.01, 0.05):
        for cfr in np.arange(0.3, 1.001, 0.01):
            e = np.sum(den * (corr - cfr * np.exp(-mid ** 2 / ell ** 2)) ** 2)
            if best is None or e < best[0]:
                best = (e, ell, cfr)
    _, ell, cfr = best
    CAL.update(ell=ell, s_gp=np.sqrt(cfr * var), s_nug=np.sqrt((1 - cfr) * var), rel_var=var, corr=corr, mid=mid)
    np.savez(os.path.join(OUT, f'calib{TAG}.npz'), **CAL)
    allt = np.concatenate(allt)
    print(f'calibration on {n} physical draws, {NU} field nodes: tau quantiles {np.round(np.quantile(allt, [.5, .9, .99]), 3)}')
    print(f'relative error of the physics basis: sd {np.sqrt(var):.3f}, spatial share {cfr:.2f}, range {ell:.2f} km; '
          f'binned correlation {np.round(corr, 2)}; baseline misfit sd {CAL["res_b"]:.3f}')
    print('prior mean gamma', np.round(CAL['mg'], 3), 'sd', np.round(np.sqrt(np.diag(CAL['Cg'])), 3))


# ------------------------------------------------------------------ privacy: clipping, sensitivity, mechanisms
EPS = (0.3, 1.0, 3.0, 10.0, 30.0)
DELTA = 1e-6
LAM_C = 0.1          # information clipping: no record may carry more than LAM_C units of whitened information
LAM_CS = (0.1, 0.3, 1.0)
NREP = 30


def gm_mult(eps, delta=DELTA):
    """analytic Gaussian mechanism (Balle & Wang 2018): sigma / sensitivity for (eps, delta)-DP."""
    def dl(s):
        return ndtr(1 / (2 * s) - eps * s) - np.exp(eps) * ndtr(-1 / (2 * s) - eps * s)
    lo, hi = 1e-3, 1e4
    for _ in range(200):
        mid = np.sqrt(lo * hi)
        lo, hi = (lo, mid) if dl(mid) <= delta else (mid, hi)
    return hi


GM = {e: gm_mult(e) for e in EPS}


def value_from_whitened(Mw, L0, mu0, S0, Ct, vn):
    """decision value when the merge adds whitened information Mw = L0' G L0 (any symmetric PSD matrix)."""
    w, U = np.linalg.eigh(0.5 * (Mw + Mw.T)); w = np.maximum(w, 0)
    S1 = L0 @ (U / (1 + w)) @ U.T @ L0.T
    return float(decision_value(mu0, S0, S1, Ct, vn)[0].sum())


def g_curve(m0, v0, vn, u):
    """value at one target as a function of the preposterior variance u of its mean (u in [0, v0])."""
    s = np.sqrt(u)
    r0 = bayes_risk(m0, v0 + vn)
    return r0 - bayes_risk(m0 + s[:, None] * GHX[None], (v0 - u + vn)[:, None]) @ GHW


def value_sensitivity(m0, v0, vn, lam_c=LAM_C, ngrid=400):
    """Proposition B4: one record with whitened information at most lam_c changes the preposterior variance of every
    target by at most kappa (v0 - u), kappa = lam_c / (1 + lam_c); the value changes by at most sum_j omega_j."""
    kap = lam_c / (1 + lam_c); om = 0.0
    for mj, vj, nj in zip(m0, v0, vn):
        u = np.linspace(0, vj, ngrid)
        g = g_curve(mj, vj, nj, u)
        gu = g_curve(mj, vj, nj, u + kap * (vj - u))
        om += float(np.max(np.abs(gu - g)))
    return om


_BE2 = None
def euclid_bound():
    """public clipping bound for 'DP alone': 95th percentile of the squared norm of a weighted record over the
    sector (treated records, model log T), computed from public geometry only."""
    global _BE2
    if _BE2 is None:
        cells = VI[DIST[VI] <= 14.5]
        w = dict(cells=cells, lt=LT0[cells], a=np.ones(len(cells)))
        Phi, sd = design(w)
        _BE2 = float(np.quantile(np.sum((Phi / sd[:, None]) ** 2, 1), 0.95))
    return _BE2


def private_values(rng, D_k, L0, mu0, S0, Ct, vn, m0t, v0t, dVs):
    """values released by each mechanism for one candidate, for every epsilon.
    A: DP alone (Euclidean clipping, noisy Gram matrix released to the host);
    B: inside MPC, information clipping in the host metric, exact value plus Gaussian noise (Proposition B4);
    C: inside MPC, information clipping, noise added to the whitened information before the value."""
    Phi, sd = D_k; Q = Phi / sd[:, None]
    p = Q.shape[1]
    B2 = euclid_bound()
    nq = np.sum(Q ** 2, 1); Qe = Q * np.sqrt(np.minimum(1, B2 / nq))[:, None]
    Ge = Qe.T @ Qe
    Rw = Q @ L0; nr = np.sum(Rw ** 2, 1)
    iu = np.triu_indices(p)
    def sym_noise(sc):
        E = np.zeros((p, p)); E[iu] = sc * rng.standard_normal(len(iu[0])); return E + np.triu(E, 1).T
    out = {'clip': {}, 'priv': {}, 'clipped_share': {}}
    for e in EPS:
        out['priv'][f'A{e}'] = value_from_whitened(L0.T @ (Ge + sym_noise(GM[e] * B2)) @ L0, L0, mu0, S0, Ct, vn)
    for lc in LAM_CS:
        wc = np.minimum(1, lc / nr)
        Mc = (Rw * wc[:, None]).T @ Rw
        vc = value_from_whitened(Mc, L0, mu0, S0, Ct, vn)
        out['clip'][str(lc)] = vc; out['clipped_share'][str(lc)] = float(np.mean(wc < 1))
        for e in EPS:
            out['priv'][f'B{lc}_{e}'] = vc + GM[e] * dVs[lc] * rng.standard_normal()
            out['priv'][f'C{lc}_{e}'] = value_from_whitened(Mc + sym_noise(GM[e] * lc), L0, mu0, S0, Ct, vn)
    return out


# ------------------------------------------------------------------ one comparison
def run_world(i, nrep=NREP, private=True):
    mu, S = prior()
    w = make_world(i)
    Ct, vn = targets(w['tg'], w['tg_lt'])
    D = [design(x) for x in w['W']]
    m0, S0 = posterior(D[0][0], D[0][1], w['W'][0]['y'], mu, S)
    a0 = act(Ct @ m0, qform(Ct, S0) + vn)
    L0 = true_loss(a0, w['tau_t'])
    GH = gram(*D[0])
    Sg = S[PB:, PB:]
    Lc = np.linalg.cholesky(S0 + 1e-12 * np.eye(len(S0)))
    m0t, v0t = Ct @ m0, qform(Ct, S0)
    def info(Gp):
        return 0.5 * np.linalg.slogdet(np.eye(len(Sg)) + Sg @ Gp)[1]
    rng = np.random.default_rng([770000, i])
    dVs = {lc: value_sensitivity(m0t, v0t, vn, lc) for lc in LAM_CS} if private else {}
    rows = []
    for k in CAND:
        G = gram(*D[k])
        cr, S1 = criteria(m0, S0, G, Ct, vn)
        gains = []
        for rep in range(nrep):
            y = w['W'][k]['y'] if rep == 0 else draw_y(i, k, rep, HOLDERS[k], w['W'][k])
            m1, S1r = posterior(D[k][0], D[k][1], y, m0, S0)
            a1 = act(Ct @ m1, qform(Ct, S1r) + vn)
            gains.append(L0 - true_loss(a1, w['tau_t']))
        ov = dict(alone=info(cate_info(G)), host=info(cate_info(GH)), merged=info(cate_info(GH + G)),
                  sumsep=info(cate_info(G) + cate_info(GH)))
        row = dict(k=k, n=len(w['W'][k]['a']), treated=float(w['W'][k]['a'].mean()), gain=float(np.mean(gains)),
                   gain1=gains[0], gain_sd=float(np.std(gains)), **cr, overlap=ov)
        if private:
            pv = private_values(rng, D[k], Lc, m0, S0, Ct, vn, m0t, v0t, dVs)
            row.update(pv)
        rows.append(row)
    return dict(i=i, L0=L0, rows=rows, n_coast=int(np.sum(DIST[w['tg']] < 2.0)), host_allow=float(a0.mean()),
                oracle_loss=true_loss((w['tau_t'] <= T_TOL + C_CAP / L_SAL).astype(float), w['tau_t']),
                chem=list(w['chem']), BE2=euclid_bound(), dV={str(k): v for k, v in dVs.items()})


def mpc_world(i):
    """the BASHKIMI-GO value of every candidate computed on secret shares (mpc.py) against floating point."""
    import mpc as P
    mu, S = prior(); w = make_world(i)
    Ct, vn = targets(w['tg'], w['tg_lt'])
    D = [design(x) for x in w['W']]
    m0, S0 = posterior(D[0][0], D[0][1], w['W'][0]['y'], mu, S)
    L0 = np.linalg.cholesky(S0 + 1e-12 * np.eye(len(S0)))
    W = L0.T @ Ct.T; m0t, v0t = Ct @ m0, qform(Ct, S0)
    cells = VI[DIST[VI] <= 14.5]
    Phi, sd = design(dict(cells=cells, lt=LT0[cells] - 0.5, a=np.ones(len(cells))))
    bw = float(np.max(np.sum(((Phi / sd[:, None]) @ L0) ** 2, 1)))     # public bound on one record's information
    out = []
    for k in CAND:
        G = gram(*D[k])
        Vf = value_from_whitened(L0.T @ G @ L0, L0, m0, S0, Ct, vn)
        P.ST.__init__()
        Vm, _ = P.value_mpc(G, L0, W, m0t, v0t, vn, GHX, GHW, T_TOL, L_SAL, C_CAP, 1 + D[k][0].shape[0] * bw)
        out.append(dict(k=k, float=Vf, mpc=Vm, mults=P.ST.mults, trunc=P.ST.trunc, cmp=P.ST.cmp, rounds=P.ST.rounds,
                        mbytes=P.ST.bytes / 1e6))
    return dict(i=i, rows=out)


def run_mpc(n):
    load_calib(); V.zeta_chol(); model_fields()
    with Pool(4) as pool:
        R = pool.map(mpc_world, range(n))
    json.dump(R, open(os.path.join(OUT, f'mpc{TAG}_{n}.json'), 'w'))
    E = np.array([[r_['mpc'] - r_['float'] for r_ in r['rows']] for r in R])
    same = np.mean([np.argmax([r_['mpc'] for r_ in r['rows']]) == np.argmax([r_['float'] for r_ in r['rows']]) for r in R])
    print(f'MPC on {n} worlds: max |error| {np.abs(E).max():.2e}, mean error {E.mean():+.2e}, same choice {same:.3f}')


def run(n):
    load_calib(); V.zeta_chol(); model_fields()
    t0 = time.time()
    with Pool(4) as pool:
        R = pool.map(run_world, range(n), chunksize=2)
    json.dump(R, open(os.path.join(OUT, f'runs{TAG}_{n}.json'), 'w'))
    print(f'{n} worlds in {time.time() - t0:.0f} s')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'calibrate':
        calibrate(int(sys.argv[2]) if len(sys.argv) > 2 else 400)
    elif cmd == 'run':
        run(int(sys.argv[2]))
    elif cmd == 'mpc':
        run_mpc(int(sys.argv[2]))
    elif cmd == 'one':
        r = run_world(int(sys.argv[2]), nrep=4)
        for x in r['rows']:
            print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in x.items() if k not in ('overlap', 'priv')})
            print('   clip', {k: round(v, 4) for k, v in x['clip'].items()}, 'share', x['clipped_share'])
            print('   ', {k: round(v, 4) for k, v in x['priv'].items()})
        print('dV', r['dV'])
