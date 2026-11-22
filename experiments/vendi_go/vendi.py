"""VENDI-GO: where to build managed-aquifer-recharge (MAR) wells when the aquifer, the injectivity
of every site and the future recharge are uncertain and every pilot test costs money.

Setting: the Fushe-Kuqe sector model (fk_geo.FKGeo), supply wells A1 (A) and P10 (B) as in
fk_mar_geo.py, intrusion of a supply well when its head H < h_c = 1 m.
Truth (what the field is, unknown to every policy):
  log T = log(K0 b) + theta[zone] + zeta(x), theta ~ N(0, Gam) on the 12 zones and zeta a Gaussian
     field (sd 0.35, exponential, range 2 km) that the 12-zone design model cannot represent;
  injectivity of a MAR well in cell x: c(x) = c_ref (T(x) / T_ref) exp(eta(x)), eta ~ N(0, 0.5^2) per
     cell (skin, clogging); c_ref = Q so that the median site can just take the design rate;
  future mean recharge (1 + xi) R with xi ~ N(0, 0.08^2), which no test can reveal.
  The supply wells are pumped at Q_A, Q_B such that each is intruded with probability 1/2 (prior).
  A MAR well at x delivers q(x) = min(Q, c(x)), Q = 5 000 m3/d; three wells >= 6 km apart in northing.
  Risk of a design = P(A or B intruded) over the future recharge, exact for a known aquifer:
     P = Phi(max_w (h_c - H_w) / hn_w / sd_xi), H_w the head at w for xi = 0, hn_w its natural head.
Data a policy can buy:
  Stage 0, the reciprocal step test (no drilling): stop pumping at A, then at B, for a few days and
     read every existing well in the sector. The flow matrix is symmetric, so the head rise at well j
     per unit pumping stopped at A equals the head rise at A per unit recharge at j, g_A(j), the very
     adjoint that ranks recharge sites (Proposition V1). The recovered heads give the natural heads.
  Pilot test at a candidate site (drilling + injection): measures the injectivity c and the head rise
     at A and B, i.e. q_t g_A(x) and q_t g_B(x).
Belief (all policies): Gaussian over theta, the approximation errors of every log g and log natural
  head of the 12-zone model and zeta at the sites (approximation-error approach: their mean and
  covariance come from 2 500 joint draws of theta and zeta); extended Kalman updates, relinearized
  after every test (iterated for Stage 0).
Policies: published, area and PRAG-MAR designs (built after their three pilot tests), PRAG-MAR after
  Stage 0, greedy exploitation, Thompson sampling, random tests, VENDI-GO with and without Stage 0,
  and the oracle that knows the truth. VENDI-GO tests the site with the largest knowledge gradient
  (expected fall of the minimum posterior risk over designs built from tested sites, computed by
  Gauss-Hermite preposterior quadrature) and stops when it falls below kappa = (cost of one test) /
  (loss if a supply well is intruded). Only tested sites can be built (no injection well without a
  pilot test).
Run: python3 vendi.py setup ; python3 vendi.py run 200 ; python3 vendi.py check
"""
import os, sys, json, time, itertools
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.special import ndtr
from scipy.stats import norm
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'prag_go_fushe_kuqe'))
from fk_geo import FKGeo
from bvn import bvnu

OUT = os.path.join(HERE, 'res')
m = FKGeo()
NZ = m.Nz
GAM = m.Gam
LG = np.linalg.cholesky(GAM)
RCH, BTH = m.P['R'], m.P['b']

HC = 1.0            # m, intrusion threshold at a supply well
QD = 5000.0         # m3/d, design rate of one MAR well
SPACE = 6.0         # km between MAR wells in northing (published rule)
EXCL = 1.0          # km, no MAR well closer than this to a supply well
SIG_H = 0.02        # m, error of a steady head difference read by a logger
SIG_C = 0.10        # error of log injectivity from a step-rate injection test
SIG_ETA = 0.5       # sd of the well-scale injectivity factor
SIG_ZETA, L_ZETA = 0.35, 2.0
SIG_XI = 0.08       # sd of the future change of mean recharge (fraction)
DQ_STEP = 3000.0    # m3/d, pumping step of the reciprocal test at each supply well
SNR_MIN = 3.0
NMAX = 12           # at most this many pilot tests
NRAND = 6           # tests of the random policy
DTH = 0.05          # finite-difference step of the Jacobian
N_AE = 2500
KAPPA = 0.01        # cost of one pilot test / loss if a supply well is intruded


# ------------------------------------------------------------------ geometry
def _cell_of_id(wid):
    i = int(np.flatnonzero(m.wellID == wid)[0])
    return int(m.cell_of(m.Wk[i, 0], m.Wk[i, 1]))


cA, cB = _cell_of_id('A1'), _cell_of_id('P10')
_dist = lambda c: np.hypot(m.cx - m.cx[c], m.cy - m.cy[c])
ALLOWED = m.valid & (_dist(cA) >= EXCL) & (_dist(cB) >= EXCL)
SITE = np.flatnonzero(ALLOWED & (m.ai % 4 == 0) & (m.aj % 4 == 0))      # 1 km lattice of candidates
K = len(SITE)
_obs = []
for _i in range(len(m.Wk)):
    _c = int(m.cell_of(m.Wk[_i, 0], m.Wk[_i, 1]))
    if _c >= 0 and m.valid[_c] and _c not in (cA, cB) and _c not in _obs:
        _obs.append(_c)
OBS = np.array(_obs)                       # existing wells in the sector (Stage 0 observation points)
NO = len(OBS)
CELLJ = np.r_[SITE, OBS, cA, cB]           # points whose log g_A, log g_B the belief carries
NJ = len(CELLJ)
JA, JB = NJ - 2, NJ - 1
NY = 2 * NJ + 2
PHA, PHB = 2 * NJ, 2 * NJ + 1


def GA(j): return j
def GB(j): return NJ + j


DZ = NZ + NY + K
ZETA0 = NZ + NY
YS = m.cy[SITE]
ZS = m.zone[SITE]
TREF = float(np.median(m.K0c[SITE] * BTH))
LOGC0 = np.log(QD) + np.log(m.K0c[SITE] * BTH / TREF)
FIX = np.array([PHA, PHB, GA(JA), GA(JB), GB(JA), GB(JB)])
ALL = np.r_[FIX, GA(np.arange(K)), GB(np.arange(K))]   # Y indices whose joint moments the designs need
VI = np.flatnonzero(m.valid)
EAB = np.zeros((m.Nc, 2)); EAB[cA, 0] = 1.0; EAB[cB, 1] = 1.0


# ------------------------------------------------------------------ physics
def matrix(theta, zeta=None):
    lT = np.log(m.K0c * BTH) + theta[m.zone]
    if zeta is not None:
        lT = lT + zeta
    T = np.exp(lT)
    Tf = 0.5 * (T[m.gI] + T[m.gJ])
    diag = np.zeros(m.Nc)
    np.add.at(diag, m.gI, Tf); np.add.at(diag, m.gJ, Tf)
    diag[m.sea_idx] += T[m.sea_idx] * m.sea_cond
    diag[~m.valid] = 1.0
    I = np.r_[m.gI, m.gJ, np.arange(m.Nc)]; J = np.r_[m.gJ, m.gI, np.arange(m.Nc)]
    return sp.csc_matrix((np.r_[-Tf, -Tf, diag], (I, J)), shape=(m.Nc, m.Nc))


def fields(theta, zeta=None):
    """natural head (present recharge) and u[:, w] = head rise per unit injection at supply well w,
    which by reciprocity is also g_w(x) = rise at w per unit recharge at x."""
    lu = spla.splu(matrix(theta, zeta))
    return lu.solve(m.rhs), lu.solve(EAB)


def fvec(theta, zeta=None):
    hn, u = fields(theta, zeta)
    return np.r_[np.log(u[CELLJ, 0]), np.log(u[CELLJ, 1]), np.log(hn[cA] / RCH), np.log(hn[cB] / RCH)]


def fjac(theta):
    f0 = fvec(theta); F = np.empty((NY, NZ))
    for z in range(NZ):
        e = np.zeros(NZ); e[z] = DTH
        F[:, z] = (fvec(theta + e) - fvec(theta - e)) / (2 * DTH)
    return f0, F


LZ = None
def zeta_chol():
    global LZ
    if LZ is None:
        D = np.hypot(m.cx[VI, None] - m.cx[None, VI], m.cy[VI, None] - m.cy[None, VI])
        LZ = np.linalg.cholesky(SIG_ZETA ** 2 * np.exp(-D / L_ZETA) + 1e-9 * np.eye(len(VI)))
    return LZ


def draw_zeta(rng):
    z = np.zeros(m.Nc); z[VI] = LZ @ rng.standard_normal(len(VI)); return z


# ------------------------------------------------------------------ setup: approximation errors, pumping
def ae_member(seed):
    rng = np.random.default_rng(seed)
    th = LG @ rng.standard_normal(NZ); ze = draw_zeta(rng)
    f1 = fvec(th, ze); f0 = fvec(th)
    return np.r_[f1 - f0, ze[SITE]], f1[[PHA, PHB, GA(JA), GA(JB), GB(JB)]], f0[[PHA, PHB, GA(JA), GA(JB), GB(JB)]]


def heads_sup(S, QA, QB, xi):
    hnA, hnB = RCH * np.exp(S[:, 0]), RCH * np.exp(S[:, 1])
    uAA, uAB, uBB = np.exp(S[:, 2]), np.exp(S[:, 3]), np.exp(S[:, 4])
    return (1 + xi) * hnA - QA * uAA - QB * uAB, (1 + xi) * hnB - QA * uAB - QB * uBB


def calibrate(S, xi):
    """Q_A, Q_B such that the median of H_A and of H_B is h_c (each well intruded with probability 1/2)."""
    QA = QB = 0.0
    for _ in range(60):
        lo, hi = 0.0, 1e6
        for _ in range(60):
            mid = 0.5 * (lo + hi); a, _ = heads_sup(S, mid, QB, xi)
            lo, hi = (mid, hi) if np.median(a) > HC else (lo, mid)
        QA = 0.5 * (lo + hi)
        lo, hi = 0.0, 1e6
        for _ in range(60):
            mid = 0.5 * (lo + hi); _, b = heads_sup(S, QA, mid, xi)
            lo, hi = (mid, hi) if np.median(b) > HC else (lo, mid)
        QBn = 0.5 * (lo + hi)
        if abs(QBn - QB) < 1e-4:
            QB = QBn; break
        QB = QBn
    return QA, QB


def setup():
    os.makedirs(OUT, exist_ok=True); t0 = time.time()
    zeta_chol()
    with Pool(4) as pool:
        R = pool.map(ae_member, [100000 + s for s in range(N_AE)], chunksize=25)
    E = np.array([r[0] for r in R]); S1 = np.array([r[1] for r in R]); S0 = np.array([r[2] for r in R])
    xi = SIG_XI * np.random.default_rng(424242).standard_normal(N_AE)
    QA, QB = calibrate(S1, xi)
    a, b = heads_sup(S1, QA, QB, xi)
    mu = E.mean(0); C = np.cov(E, rowvar=False); C = 0.95 * C + 0.05 * np.diag(np.diag(C))
    np.savez(os.path.join(OUT, 'setup.npz'), mu=mu, C=C, QA=QA, QB=QB, S1=S1, S0=S0, xi=xi)
    sdY = np.sqrt(np.diag(C))
    print(f'K = {K} candidate sites, {NO} existing wells for Stage 0, state dimension {DZ}')
    print(f'approximation error sd: log g at sites median {np.median(sdY[:K]):.3f} (A) {np.median(sdY[NJ:NJ + K]):.3f} (B), '
          f'log natural head {sdY[PHA]:.3f} {sdY[PHB]:.3f}; mean bias log g {np.median(mu[:K]):+.3f}')
    print(f'pumping Q_A {QA:.0f}, Q_B {QB:.0f} m3/d; P(A) {np.mean(a < HC):.3f} P(B) {np.mean(b < HC):.3f} '
          f'P(A or B) {np.mean(np.minimum(a, b) < HC):.3f}  ({time.time() - t0:.0f} s)')


_S = None
def load_setup():
    global _S, QA, QB, MZ0, P0
    if _S is None:
        _S = dict(np.load(os.path.join(OUT, 'setup.npz')))
        QA, QB = float(_S['QA']), float(_S['QB'])
        MZ0 = np.r_[np.zeros(NZ), _S['mu']]
        P0 = np.zeros((DZ, DZ)); P0[:NZ, :NZ] = GAM; P0[NZ:, NZ:] = _S['C']
        P0[np.diag_indices(DZ)] += 1e-10
    return _S


# ------------------------------------------------------------------ truth
def make_truth(i):
    rng = np.random.default_rng(530000 + i)
    th = LG @ rng.standard_normal(NZ); ze = draw_zeta(rng)
    eta = SIG_ETA * rng.standard_normal(m.Nc)
    hn, u = fields(th, ze)
    c = QD * (m.K0c * BTH * np.exp(th[m.zone] + ze) / TREF) * np.exp(eta)
    return dict(i=i, hnA=hn[cA], hnB=hn[cB], uAA=u[cA, 0], uAB=u[cB, 0], uBB=u[cB, 1], gA=u[:, 0], gB=u[:, 1], c=c,
                n_c=rng.standard_normal(m.Nc), n_h=rng.standard_normal((m.Nc, 2)),
                n_s0=rng.standard_normal((2, NO + 2)), n_nat=rng.standard_normal(2), seed=530000 + i)


def truth_risk(tr, cells, q):
    """P(A or B intruded) over the future recharge for designs (cells, rates); arrays (..., n)."""
    HA = tr['hnA'] - QA * tr['uAA'] - QB * tr['uAB'] + (q * tr['gA'][cells]).sum(-1)
    HB = tr['hnB'] - QA * tr['uAB'] - QB * tr['uBB'] + (q * tr['gB'][cells]).sum(-1)
    return ndtr(np.maximum((HC - HA) / tr['hnA'], (HC - HB) / tr['hnB']) / SIG_XI)


def risk_cells(tr, cells):
    cells = np.array([c for c in cells if m.valid[c]], int)
    if len(cells) == 0:
        return float(truth_risk(tr, np.zeros(1, int), np.zeros(1)))
    return float(truth_risk(tr, cells, np.minimum(QD, tr['c'][cells])))


# ------------------------------------------------------------------ belief
class Belief:
    def __init__(self):
        load_setup()
        self.mz = MZ0.copy(); self.P = P0.copy(); self.relin()

    def clone(self):
        b = Belief.__new__(Belief)
        b.mz, b.P, b.f0, b.F, b.Y = self.mz.copy(), self.P.copy(), self.f0.copy(), self.F.copy(), self.Y.copy()
        return b

    def relin(self):
        self.f0, self.F = fjac(self.mz[:NZ])
        self.Y = self.f0 + self.mz[NZ:NZ + NY]

    def rows(self, yidx):
        yidx = np.atleast_1d(yidx)
        H = np.zeros((len(yidx), DZ)); H[:, :NZ] = self.F[yidx]; H[np.arange(len(yidx)), NZ + yidx] = 1.0
        return H

    def update(self, H, innov, Rd):
        PH = self.P @ H.T; S = H @ PH + np.diag(Rd)
        Kg = np.linalg.solve(S, PH.T).T
        self.mz = self.mz + Kg @ innov
        self.P = self.P - Kg @ PH.T; self.P = 0.5 * (self.P + self.P.T)

    def iekf(self, yidx, yobs, sd, iters=3):
        z0, Pp = self.mz.copy(), self.P.copy(); zi = z0.copy()
        for _ in range(iters):
            f0, F = fjac(zi[:NZ])
            H = np.zeros((len(yidx), DZ)); H[:, :NZ] = F[yidx]; H[np.arange(len(yidx)), NZ + yidx] = 1.0
            innov = yobs - (f0[yidx] + zi[NZ + yidx]) - H @ (z0 - zi)
            PH = Pp @ H.T; S = H @ PH + np.diag(sd ** 2)
            Kg = np.linalg.solve(S, PH.T).T
            zi = z0 + Kg @ innov
        self.mz = zi; self.P = Pp - Kg @ PH.T; self.P = 0.5 * (self.P + self.P.T); self.relin()

    def moments(self):
        FA = self.F[ALL]
        MP = FA @ self.P[:NZ, :] + self.P[NZ + ALL, :]
        C = MP[:, :NZ] @ FA.T + MP[:, NZ + ALL]
        self.MP, self.C = MP, 0.5 * (C + C.T)

    def logc(self, k):
        """mean and variance of log c at site k (theta, zeta part plus eta)."""
        z, s = ZS[k], ZETA0 + k
        mu = LOGC0[k] + self.mz[z] + self.mz[s]
        var = self.P[z, z] + self.P[s, s] + 2 * self.P[z, s] + SIG_ETA ** 2
        return mu, var


# ------------------------------------------------------------------ designs and posterior risk
def enum_designs(ys):
    n = len(ys); out = [(-1, -1, -1)]
    for r in (1, 2, 3):
        for comb in itertools.combinations(range(n), r):
            if all(abs(ys[a] - ys[b]) >= SPACE for a, b in itertools.combinations(comb, 2)):
                out.append(tuple(comb) + (-1,) * (3 - r))
    return np.array(out, int)


def extend_designs(DT, compat, kpos):
    size = (DT >= 0).sum(1)
    cp = np.r_[np.asarray(compat, bool), True]                    # index -1 -> the padded True
    ok = (size <= 2) & np.all(cp[np.where(DT < 0, len(cp) - 1, DT)], axis=1)
    Dk = DT[ok].copy(); Dk[np.arange(len(Dk)), size[ok]] = kpos
    return np.vstack([DT, Dk])


def _coef(Yrel, n):
    eY = np.exp(Yrel)
    b0A = np.zeros(6 + 2 * n); b0B = np.zeros(6 + 2 * n)
    b0A[[0, 2, 3]] = [RCH * eY[0], -QA * eY[2], -QB * eY[3]]
    b0B[[1, 4, 5]] = [RCH * eY[1], -QA * eY[4], -QB * eY[5]]
    return b0A, b0B, eY[6:6 + n], eY[6 + n:6 + 2 * n]


def rel_index(S):
    S = np.asarray(S, int)
    return np.r_[0:6, 6 + S, 6 + K + S]


def _quads(Crel, b0A, b0B, bA, bB, Qn, Dp):
    """Var H_A, Var H_B, Cov(H_A, H_B) from the aquifer belief for designs Dp (nD x 3, empty slots = n)
    and per-node rates Qn (nnode x n): structured quadratic forms, O(nnode nD)."""
    n = len(bA)
    iA = 6 + np.arange(n); iB = 6 + n + np.arange(n)
    CbA, CbB = Crel @ b0A, Crel @ b0B
    def pad(M):
        Z = np.zeros((n + 1, n + 1)); Z[:n, :n] = M; return Z
    CAA, CBB, CAB = pad(Crel[np.ix_(iA, iA)]), pad(Crel[np.ix_(iB, iB)]), pad(Crel[np.ix_(iA, iB)])
    z = np.zeros((len(Qn), 1))
    aD = np.concatenate([Qn * bA, z], 1)[:, Dp]; bD = np.concatenate([Qn * bB, z], 1)[:, Dp]
    xA, xB = np.r_[CbA[iA], 0][Dp], np.r_[CbB[iB], 0][Dp]
    xAB, xBA = np.r_[CbB[iA], 0][Dp], np.r_[CbA[iB], 0][Dp]
    I, J = Dp[:, :, None], Dp[:, None, :]
    vA = b0A @ CbA + 2 * (aD * xA).sum(-1) + np.einsum('kdi,dij,kdj->kd', aD, CAA[I, J], aD)
    vB = b0B @ CbB + 2 * (bD * xB).sum(-1) + np.einsum('kdi,dij,kdj->kd', bD, CBB[I, J], bD)
    cv = b0A @ CbB + (aD * xAB).sum(-1) + (bD * xBA).sum(-1) + np.einsum('kdi,dij,kdj->kd', aD, CAB[I, J], bD)
    return vA, vB, cv


def risk_from_moments(muA, muB, vA, vB, cAB):
    sA, sB = np.sqrt(np.maximum(vA, 1e-12)), np.sqrt(np.maximum(vB, 1e-12))
    rho = np.clip(cAB / (sA * sB), -0.999999, 0.999999)
    return 1.0 - bvnu(-(muA - HC) / sA, -(muB - HC) / sB, rho)


def design_risk(B, S, qm, qv, D, Crel=None, Yn=None, Qn=None, drop=None):
    """posterior P(A or B intruded) of designs D among sites S: tested sites have qv = 0 and the measured
    rate, untested ones their predictive mean and variance of the delivered rate (injectivity unknown).
    Optional node arrays: Yn (nnode x nrel) means, Qn (nnode x n) rates, Crel a posterior covariance.
    Returns risk (nnode x nD) and the moments."""
    n = len(S); rel = rel_index(S)
    Y0 = B.Y[ALL[rel]]
    if Crel is None: Crel = B.C[np.ix_(rel, rel)]
    if Yn is None: Yn = Y0[None, :]
    if Qn is None: Qn = np.asarray(qm, float)[None, :]
    b0A, b0B, bA, bB = _coef(Y0, n)
    Dp = np.where(D < 0, n, D)
    vA, vB, cv = _quads(Crel, b0A, b0B, bA, bB, Qn, Dp)
    qv_ = np.asarray(qv, float).copy()
    if drop is not None: qv_[drop] = 0.0
    ivA = np.r_[qv_ * bA ** 2, 0.0][Dp].sum(1); ivB = np.r_[qv_ * bB ** 2, 0.0][Dp].sum(1)
    ivAB = np.r_[qv_ * bA * bB, 0.0][Dp].sum(1)
    clA, clB = RCH * np.exp(Y0[0]) * SIG_XI, RCH * np.exp(Y0[1]) * SIG_XI
    eY = np.exp(Yn)
    baseA = RCH * eY[:, 0] - QA * eY[:, 2] - QB * eY[:, 3]
    baseB = RCH * eY[:, 1] - QA * eY[:, 4] - QB * eY[:, 5]
    z = np.zeros((len(Yn), 1))
    muA = baseA[:, None] + np.concatenate([Qn * eY[:, 6:6 + n], z], 1)[:, Dp].sum(-1)
    muB = baseB[:, None] + np.concatenate([Qn * eY[:, 6 + n:6 + 2 * n], z], 1)[:, Dp].sum(-1)
    vA = vA + ivA + clA ** 2; vB = vB + ivB + clB ** 2; cv = cv + ivAB + clA * clB
    return risk_from_moments(muA, muB, vA, vB, cv), (muA, muB, vA, vB, cv)


def posterior_risk(B, T, qT, D=None):
    """posterior risk of every design among the tested sites T."""
    if D is None:
        D = enum_designs(YS[T]) if len(T) else np.array([(-1, -1, -1)])
    r, mom = design_risk(B, list(T), np.asarray(qT, float), np.zeros(len(T)), D)
    return r[0], D, [x[0] for x in mom]


_x5, _w5 = np.polynomial.hermite_e.hermegauss(5)
_x3, _w3 = np.polynomial.hermite_e.hermegauss(3)
_w5, _w3 = _w5 / _w5.sum(), _w3 / _w3.sum()
NODES = np.array([(a, b, c) for a in _x5 for b in _x3 for c in _x3])
WNODE = np.array([wa * wb * wc for wa in _w5 for wb in _w3 for wc in _w3])


def pilot_noise_var(B, k, qt):
    out = []
    for yi in (GA(k), GB(k)):
        g = np.exp(B.Y[yi])
        out.append((SIG_H / (qt * g)) ** 2 if qt * g >= SNR_MIN * SIG_H else 1e4)
    return out


def site_q(B, ks):
    """predictive mean and variance of the delivered rate min(Q, c) at untested sites."""
    ks = np.atleast_1d(np.asarray(ks, int))
    mu = LOGC0[ks] + B.mz[ZS[ks]] + B.mz[ZETA0 + ks]
    var = B.P[ZS[ks], ZS[ks]] + B.P[ZETA0 + ks, ZETA0 + ks] + 2 * B.P[ZS[ks], ZETA0 + ks] + SIG_ETA ** 2
    s = np.sqrt(var); lq = np.log(QD)
    E1 = np.exp(mu + var / 2) * ndtr((lq - mu - var) / s) + QD * (1 - ndtr((lq - mu) / s))
    E2 = np.exp(2 * mu + 2 * var) * ndtr((lq - mu - 2 * var) / s) + QD ** 2 * (1 - ndtr((lq - mu) / s))
    return E1, np.maximum(E2 - E1 ** 2, 0.0), mu, var


def kg_candidates(B, S, qm, qv, D, cpos, V0):
    """knowledge gradient of a pilot test at each untested site S[p], p in cpos:
    V0 - E[min over designs D of the posterior risk after the test] (Gauss-Hermite preposterior)."""
    n = len(S); rel = rel_index(S)
    Crel = B.C[np.ix_(rel, rel)]; Y0 = B.Y[ALL[rel]]
    out = []
    for p in cpos:
        k = S[p]; z, s = ZS[k], ZETA0 + k; pA, pB = 6 + k, 6 + K + k
        G = np.c_[B.MP[rel, z] + B.MP[rel, s], B.C[rel, pA], B.C[rel, pB]]
        muc, varc = B.logc(k)
        nA, nB = pilot_noise_var(B, k, min(QD, np.exp(muc)))
        cA_, cB_ = B.MP[pA, z] + B.MP[pA, s], B.MP[pB, z] + B.MP[pB, s]
        Sm = np.array([[varc + SIG_C ** 2, cA_, cB_],
                       [cA_, B.C[pA, pA] + nA, B.C[pA, pB]],
                       [cB_, B.C[pA, pB], B.C[pB, pB] + nB]])
        L = np.linalg.cholesky(Sm); Li = np.linalg.inv(L)
        Cpost = Crel - G @ np.linalg.solve(Sm, G.T)
        Yn = Y0[None, :] + NODES @ (Li @ G.T)
        qk = np.minimum(QD, np.exp(muc + NODES @ (Li @ np.array([varc, cA_, cB_]))))
        Qn = np.tile(np.asarray(qm, float), (len(NODES), 1)); Qn[:, p] = qk
        r, _ = design_risk(B, S, qm, qv, D, Crel=Cpost, Yn=Yn, Qn=Qn, drop=p)
        out.append(max(0.0, V0 - float(WNODE @ r.min(1))))
    return np.array(out)


def prag_weights(mom, i):
    """PRAG-MAR weights: gradient of P(both supply wells safe) with respect to the mean heads."""
    muA, muB, vA, vB, cAB = [x[i] for x in mom]
    sA, sB = np.sqrt(vA), np.sqrt(vB); r = np.clip(cAB / (sA * sB), -0.999, 0.999)
    zA, zB = (muA - HC) / sA, (muB - HC) / sB
    wA = norm.pdf(zA) * norm.cdf((zB - r * zA) / np.sqrt(1 - r * r)) / sA
    wB = norm.pdf(zB) * norm.cdf((zA - r * zB) / np.sqrt(1 - r * r)) / sB
    return wA, wB


def deficit_weights(mom):
    muA, muB, vA, vB, _ = mom
    return ndtr((HC - muA) / np.sqrt(vA)), ndtr((HC - muB) / np.sqrt(vB))


def site_index(B, wA, wB, T):
    """expected and optimistic reduction of the expected head deficits per site (deficit weights)."""
    k = np.arange(K)
    E1, _, mu, var = site_q(B, k)
    gA, gB = B.Y[GA(k)], B.Y[GB(k)]
    sA, sB = np.sqrt(np.diag(B.C)[6 + k]), np.sqrt(np.diag(B.C)[6 + K + k])
    mean_ix = E1 * (wA * np.exp(gA) + wB * np.exp(gB))
    opt_ix = np.minimum(QD, np.exp(mu + np.sqrt(var))) * (wA * np.exp(gA + sA) + wB * np.exp(gB + sB))
    mean_ix[T] = -np.inf; opt_ix[T] = -np.inf
    return mean_ix, opt_ix


def shortlist(B, T, wA, wB, ntop=12):
    """untested sites worth a look: the best ntop by the optimistic index, plus the best site (mean index)
    of every lattice row of northing, since the three wells must be 6 km apart in northing."""
    mean_ix, opt_ix = site_index(B, wA, wB, T)
    sel = list(np.argsort(-opt_ix)[:ntop])
    for y in np.unique(YS):
        idx = np.flatnonzero((YS == y) & np.isfinite(mean_ix))
        if len(idx):
            sel.append(idx[np.argmax(mean_ix[idx])])
    return [int(x) for x in dict.fromkeys(sel) if np.isfinite(opt_ix[x])]


def _space(B, T, qT, U):
    S = list(T) + list(U)
    E1, V1, _, _ = site_q(B, U) if len(U) else (np.zeros(0), np.zeros(0), 0, 0)
    qm = np.r_[np.asarray(qT, float), E1]; qv = np.r_[np.zeros(len(T)), V1]
    D = enum_designs(YS[S])
    r, mom = design_risk(B, S, qm, qv, D)
    return S, qm, qv, D, r[0], int(np.argmin(r[0])), mom


def plan(B, T, qT):
    """design space S = tested + shortlisted untested sites (rates: measured, or predictive mean and
    variance), all designs among S, and the current best plan. Two passes: the deficit weights of the
    second pass are taken at the best plan of the first."""
    r0, _, mom = posterior_risk(B, T, qT)
    i0 = int(np.argmin(r0))
    S, qm, qv, D, r, i, mom = _space(B, T, qT, shortlist(B, T, *deficit_weights([v[i0] for v in mom])))
    keep = [S[p] for p in D[i] if p >= 0 and S[p] not in T]
    wA, wB = deficit_weights([v[0, i] for v in mom])
    U = list(dict.fromkeys(keep + shortlist(B, T, wA, wB)))
    S, qm, qv, D, r, i, _ = _space(B, T, qT, U)
    return S, qm, qv, D, r, i, (wA, wB)


def kg_positions(B, S, D, i, T, wA, wB, ntop=6, nswap=4):
    """positions in S of the untested sites whose pilot test is valued: the untested members of the best
    plan, for every member of the plan the best nswap sites that could replace it (spacing kept), and the
    best ntop overall (optimistic index)."""
    _, opt_ix = site_index(B, wA, wB, T)
    unt = [p for p in range(len(T), len(S))]
    order = sorted(unt, key=lambda p: -opt_ix[S[p]])
    plan_p = [p for p in D[i] if p >= 0]
    out = [p for p in plan_p if p >= len(T)] + order[:ntop]
    for j in plan_p:
        others = [YS[S[p]] for p in plan_p if p != j]
        ok = [p for p in order if p not in plan_p and all(abs(YS[S[p]] - y) >= SPACE for y in others)]
        out += ok[:nswap]
    return list(dict.fromkeys(out))


def confirm_site(B, S, qm, D, i, T):
    """the untested member of the best plan that matters most (largest expected head gain)."""
    k_ = [S[p] for p in D[i] if p >= 0 and S[p] not in T]
    if not k_:
        return None
    ix = {S[p]: p for p in range(len(S))}
    return max(k_, key=lambda s: qm[ix[s]] * (np.exp(B.Y[GA(s)]) + np.exp(B.Y[GB(s)])))


# ------------------------------------------------------------------ data
_S0 = {}
def belief_s0(tr):
    """the belief after Stage 0 (computed once per truth, then copied for every policy)."""
    if tr['i'] not in _S0:
        B = Belief(); n = stage0(tr, B); _S0.clear(); _S0[tr['i']] = (B, n)
    B, n = _S0[tr['i']]
    return B.clone(), n


def stage0(tr, B):
    yidx, yobs, sd = [], [], []
    for w, (hn, ph) in enumerate(((tr['hnA'], PHA), (tr['hnB'], PHB))):
        pred = RCH * np.exp(B.Y[ph])
        yidx.append(ph); yobs.append(np.log(max(hn + SIG_H * tr['n_nat'][w], SIG_H) / RCH)); sd.append(SIG_H / pred)
    for w, (gf, Yf) in enumerate(((tr['gA'], GA), (tr['gB'], GB))):
        for jj, cell in enumerate(np.r_[OBS, cA, cB]):
            yi = Yf(K + jj); ghat = np.exp(B.Y[yi])
            if DQ_STEP * ghat < SNR_MIN * SIG_H:
                continue
            dh = DQ_STEP * gf[cell] + SIG_H * tr['n_s0'][w, jj]
            yidx.append(yi); yobs.append(np.log(max(dh, SIG_H) / DQ_STEP)); sd.append(SIG_H / (DQ_STEP * ghat))
    B.iekf(np.array(yidx), np.array(yobs), np.array(sd))
    return len(yidx)


def pilot_test(tr, B, k):
    cell = SITE[k]; ctrue = tr['c'][cell]; qt = min(QD, ctrue)
    yc = np.log(ctrue) + SIG_C * tr['n_c'][cell]
    Hs = [np.zeros(DZ)]; Hs[0][ZS[k]] = 1.0; Hs[0][ZETA0 + k] = 1.0
    innov = [yc - (LOGC0[k] + B.mz[ZS[k]] + B.mz[ZETA0 + k])]; Rd = [SIG_ETA ** 2 + SIG_C ** 2]
    for w, (yi, gt) in enumerate(((GA(k), tr['gA'][cell]), (GB(k), tr['gB'][cell]))):
        g = np.exp(B.Y[yi])
        if qt * g < SNR_MIN * SIG_H:
            continue
        dh = qt * gt + SIG_H * tr['n_h'][cell, w]
        Hs.append(B.rows(yi)[0]); innov.append(np.log(max(dh, SIG_H) / qt) - B.Y[yi]); Rd.append((SIG_H / (qt * g)) ** 2)
    B.update(np.array(Hs), np.array(innov), np.array(Rd)); B.relin()
    return min(QD, np.exp(yc))


# ------------------------------------------------------------------ policies
def finish(tr, B, T, qT, name, extra=None):
    B.moments()
    r, D, _ = posterior_risk(B, T, qT)
    i = int(np.argmin(r)); d = [T[s] for s in D[i] if s >= 0]
    cells = SITE[d] if d else np.zeros(0, int)
    out = dict(policy=name, tests=len(T), sites=[int(x) for x in d], post_risk=float(r[i]),
               risk=risk_cells(tr, cells), tested=[int(x) for x in T])
    if extra: out.update(extra)
    return out


def vendi(tr, use_s0=True, kappa=KAPPA, name='vendi', use_kg=True):
    """VENDI-GO: plan the best three-well design (untested sites with unknown injectivity), test the site
    with the largest knowledge gradient while it exceeds kappa, then confirm the untested members of the
    plan (no injection well without a pilot test). use_kg=False gives plan-and-confirm (greedy)."""
    B, nobs = belief_s0(tr) if use_s0 else (Belief(), 0)
    T, qT, kgs, why = [], [], [], []
    while len(T) < NMAX:
        B.moments()
        S, qm, qv, D, r, i, (wA, wB) = plan(B, T, qT)
        V0 = float(r[i]); k = None
        if use_kg:
            cpos = kg_positions(B, S, D, i, T, wA, wB)
            kg = kg_candidates(B, S, qm, qv, D, cpos, V0)
            j = int(np.argmax(kg)); kgs.append(float(kg[j]))
            if kg[j] >= kappa:
                k = S[cpos[j]]; why.append('kg')
        if k is None:
            k = confirm_site(B, S, qm, D, i, T)
            if k is None:
                break
            why.append('confirm')
        qT.append(pilot_test(tr, B, k)); T.append(k)
    return finish(tr, B, T, qT, name, dict(kg=kgs, why=why, s0_obs=nobs))


def greedy(tr):
    return vendi(tr, use_s0=True, name='confirm', use_kg=False)


TRIP = None
def triples():
    global TRIP
    if TRIP is None:
        t = np.array(list(itertools.combinations(range(K), 3)), np.int32)
        y = YS[t]
        ok = (np.abs(y[:, 0] - y[:, 1]) >= SPACE) & (np.abs(y[:, 0] - y[:, 2]) >= SPACE) & (np.abs(y[:, 1] - y[:, 2]) >= SPACE)
        TRIP = t[ok]
    return TRIP


def thompson(tr):
    B, _ = belief_s0(tr)
    rng = np.random.default_rng(tr['seed'] + 77)
    T, qT = [], []
    while len(T) < NMAX:
        L = np.linalg.cholesky(B.P + 1e-9 * np.eye(DZ))
        zs = B.mz + L @ rng.standard_normal(DZ)
        Ys = B.f0 + B.F @ (zs[:NZ] - B.mz[:NZ]) + zs[NZ:NZ + NY]
        k_ = np.arange(K)
        q = np.minimum(QD, np.exp(LOGC0 + zs[ZS] + zs[ZETA0 + k_] + SIG_ETA * rng.standard_normal(K)))
        q[T] = qT
        sA, sB = q * np.exp(Ys[GA(k_)]), q * np.exp(Ys[GB(k_)])
        hnA, hnB = RCH * np.exp(Ys[PHA]), RCH * np.exp(Ys[PHB])
        uAA, uAB, uBB = np.exp(Ys[GA(JA)]), np.exp(Ys[GA(JB)]), np.exp(Ys[GB(JB)])
        tp = triples()
        HA = hnA - QA * uAA - QB * uAB + sA[tp].sum(1); HB = hnB - QA * uAB - QB * uBB + sB[tp].sum(1)
        d = tp[np.argmin(np.maximum((HC - HA) / hnA, (HC - HB) / hnB))]
        new = [int(s) for s in d if s not in T]
        if not new:
            break
        k = max(new, key=lambda s: sA[s] + sB[s])
        qT.append(pilot_test(tr, B, k)); T.append(k)
    return finish(tr, B, T, qT, 'thompson')


def random_tests(tr):
    B, _ = belief_s0(tr)
    rng = np.random.default_rng(tr['seed'] + 99)
    T, qT = [], []
    for k in rng.choice(K, NRAND, replace=False):
        qT.append(pilot_test(tr, B, int(k))); T.append(int(k))
    return finish(tr, B, T, qT, 'random')


def prag_sites(B):
    B.moments()
    _, _, mom = posterior_risk(B, [], [])
    wA, wB = prag_weights(mom, 0)
    k = np.arange(K)
    score = wA * np.exp(B.Y[GA(k)]) + wB * np.exp(B.Y[GB(k)])
    sel = []
    for s in np.argsort(-score):
        if all(abs(YS[s] - YS[t]) >= SPACE for t in sel):
            sel.append(int(s))
        if len(sel) == 3:
            break
    return sel


def prag_policy(tr, use_s0, sel_prior=None):
    if use_s0:
        B, _ = belief_s0(tr); sel = prag_sites(B)
    else:
        sel = sel_prior
    return dict(policy='prag_s0' if use_s0 else 'prag_prior', tests=3, sites=sel, risk=risk_cells(tr, SITE[sel]))


def oracle(tr):
    tp = triples()
    q = np.minimum(QD, tr['c'][SITE])
    r = truth_risk(tr, SITE[tp], q[tp])
    i = int(np.argmin(r))
    return dict(policy='oracle', tests=0, sites=[int(x) for x in tp[i]], risk=float(r[i]))


# ------------------------------------------------------------------ experiment
OLD = None
def old_designs():
    global OLD
    if OLD is None:
        d = json.load(open(os.path.join(HERE, '..', 'prag_go_fushe_kuqe', 'res_geo', 'mar_geo.json')))
        OLD = {nm: [s['cell'] for s in d[nm]['sites']] for nm in ('published', 'area', 'prag')}
    return OLD


SEL_PRIOR = None
def run_truth(i):
    t0 = time.time()
    tr = make_truth(i)
    res = [dict(policy='none', tests=0, risk=risk_cells(tr, []))]
    for nm, cells in old_designs().items():
        res.append(dict(policy=nm + '_cells', tests=3, risk=risk_cells(tr, cells)))
    res.append(prag_policy(tr, False, SEL_PRIOR))
    res.append(prag_policy(tr, True))
    res.append(oracle(tr))
    res.append(random_tests(tr))
    res.append(thompson(tr))
    res.append(greedy(tr))
    res.append(vendi(tr, use_s0=False, name='vendi_noS0'))
    res.append(vendi(tr, use_s0=True))
    for r in res:
        r['truth'] = i
    print(f'truth {i}: ' + ' '.join(f"{r['policy']} {r['risk']:.3f}/{r['tests']}" for r in res) + f'  ({time.time() - t0:.0f} s)', flush=True)
    return res


def init_worker():
    zeta_chol(); load_setup(); triples(); old_designs()


def run(n, start=0):
    global SEL_PRIOR
    load_setup(); zeta_chol(); triples()
    SEL_PRIOR = prag_sites(Belief())
    t0 = time.time()
    with Pool(4, initializer=init_worker) as pool:
        R = pool.map(run_truth, range(start, start + n), chunksize=1)
    rows = [r for rr in R for r in rr]
    tag = f'_{start}_{n}'
    json.dump(dict(rows=rows, constants=dict(QD=QD, SIG_H=SIG_H, SIG_C=SIG_C, SIG_ETA=SIG_ETA, SIG_ZETA=SIG_ZETA,
                                             L_ZETA=L_ZETA, SIG_XI=SIG_XI, DQ_STEP=DQ_STEP, KAPPA=KAPPA, NMAX=NMAX,
                                             QA=QA, QB=QB, K=K, NO=NO), sel_prior=SEL_PRIOR),
              open(os.path.join(OUT, f'runs{tag}.json'), 'w'))
    summarize(rows)
    print(f'{time.time() - t0:.0f} s')


def summarize(rows, kappa=KAPPA):
    pols = list(dict.fromkeys(r['policy'] for r in rows))
    n = len(set(r['truth'] for r in rows))
    by = {p: {r['truth']: r for r in rows if r['policy'] == p} for p in pols}
    tr_ids = sorted(by['none'])
    ref = np.array([by['vendi'][t]['risk'] for t in tr_ids]) + kappa * np.array([by['vendi'][t]['tests'] for t in tr_ids])
    print(f'{n} truths; risk = P(A or B intruded); cost J = risk + kappa * tests, kappa = {kappa}')
    for p in pols:
        r = np.array([by[p][t]['risk'] for t in tr_ids]); k = np.array([by[p][t]['tests'] for t in tr_ids])
        J = r + kappa * k; d = J - ref
        extra = ''
        if 'post_risk' in by[p][tr_ids[0]]:
            pr = np.array([by[p][t]['post_risk'] for t in tr_ids]); extra = f'  mean posterior risk {pr.mean():.4f}'
        print(f'{p:16s} risk {r.mean():.4f} ± {r.std() / np.sqrt(n):.4f}  tests {k.mean():5.2f}  J {J.mean():.4f}  '
              f'J - J(vendi) {d.mean():+.4f} ± {d.std() / np.sqrt(n):.4f}{extra}')


def check():
    """Proposition V1 (reciprocity) and the accuracy of the linearized belief."""
    load_setup(); zeta_chol()
    rng = np.random.default_rng(5)
    th = LG @ rng.standard_normal(NZ); ze = draw_zeta(rng)
    lu = spla.splu(matrix(th, ze))
    u = lu.solve(EAB); g = lu.solve(EAB, trans='T')
    print(f'reciprocity: max |u - g| = {np.abs(u - g).max():.2e} (max g {g.max():.2e})')
    A = matrix(th, ze); print(f'symmetry of the flow matrix: max |A - A^T| = {abs(A - A.T).max():.2e}')
    f0, F = fjac(np.zeros(NZ))
    errs = []
    for _ in range(20):
        t = LG @ rng.standard_normal(NZ)
        errs.append(np.abs(fvec(t) - (f0 + F @ t)))
    errs = np.array(errs)
    print(f'linearization of log g, log hn at the prior mean over 20 prior draws: median abs error {np.median(errs):.4f}, 95% {np.quantile(errs, .95):.4f}')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'run'
    if cmd == 'setup':
        setup()
    elif cmd == 'check':
        check()
    elif cmd == 'one':
        load_setup(); zeta_chol(); triples(); SEL_PRIOR = prag_sites(Belief())
        run_truth(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
    else:
        run(int(sys.argv[2]) if len(sys.argv) > 2 else 200, int(sys.argv[3]) if len(sys.argv) > 3 else 0)
