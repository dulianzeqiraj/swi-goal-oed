"""Stage 3: exhaustive comparison of 3-well designs on the Henry ensemble.

Criteria (all evaluated on the same 4960 designs):
  exact  : nonlinear EIG of the threshold goals, by likelihood re-weighting of the
           inner ensemble (outer samples and noise shared across designs).
  mass   : linear-Gaussian EIG of the salt mass (the project's goal, adjoint Lemma 1).
  meanAB : linear-Gaussian EIG of the mean concentration of the two supply wells.
  cA     : linear-Gaussian EIG of the concentration at well A (Theorem 1 for risk A).
  pragAdj: PRAG-GO closed form for risk A or for risk in A or B, adjoint moments.
  pragEns: the same with ensemble moments.
  pragNS : the same with ensemble moments after a normal-score transform of every
           variable; valid because the threshold event is invariant under monotone maps.
"""
import sys, time, itertools
import numpy as np
from multiprocessing import Pool
from numpy.polynomial.hermite_e import hermegauss
from scipy.stats import norm, spearmanr

OUT = sys.argv[1]; PRIOR = sys.argv[2]
SIGMAS = [float(s) for s in sys.argv[3].split(',')] if len(sys.argv) > 3 else [0.01]
TAU = 0.01
E = np.load(f'{OUT}/ens.npz'); Lz = np.load(f'{OUT}/lin.npz')
inner, outer = E['inner'], E['outer']
gi, go = inner[:, :32], outer[:, :32]
cAi, cBi = inner[:, 32], inner[:, 33]
QIN = np.stack([cAi > TAU, np.maximum(cAi, cBi) > TAU], 1).astype(np.float64)
P0 = QIN.mean(0)
def h(p):
    p = np.asarray(p, dtype=np.float64)
    return -(np.where(p > 0, p * np.log(np.where(p > 0, p, 1.0)), 0.0) + np.where(p < 1, (1 - p) * np.log(np.where(p < 1, 1 - p, 1.0)), 0.0))
D3 = list(itertools.combinations(range(32), 3))

# ---------------------------------------------------------------- linear-Gaussian pieces
S, GAM = Lz['S'], Lz['GAM']
if PRIOR == 'facies':
    GAM = GAM + 0.5 ** 2 * np.ones_like(GAM)        # pooled Gaussian approximation of the mixture
A_adj = S @ GAM @ S.T
mu_adj = Lz['c0']                                    # 32 candidates, A, B at theta = 0
Ys = np.column_stack([gi, cAi, cBi, inner[:, 34]])
A_ens = np.cov(Ys.T); mu_ens = Ys.mean(0)


def normal_scores(v, ref):
    r = np.searchsorted(np.sort(ref), v, side='right')
    return norm.ppf(np.clip(r / (len(ref) + 1), 1e-6, 1 - 1e-6))


gl_x, gl_w = np.polynomial.legendre.leggauss(64)
def Phi2(a, b, r):
    lo = -9.0; hi = np.maximum(a, lo + 1e-9)
    t = 0.5 * (hi - lo)[..., None] * gl_x + 0.5 * (hi + lo)[..., None]
    f = norm.pdf(t) * norm.cdf((b[..., None] - r * t) / np.sqrt(1 - r ** 2))
    return (0.5 * (hi - lo)[..., None] * f * gl_w).sum(-1)
hx, hw = hermegauss(24); hw = hw / hw.sum()
U1, U2 = np.meshgrid(hx, hx, indexing='ij'); W2 = np.outer(hw, hw).ravel(); UU = np.stack([U1.ravel(), U2.ravel()])


def lin_eig(A, d, g, s2):
    """R^2 and EIG of goal row g (index or weight vector over 35) for design d."""
    d = list(d)
    Sy = A[np.ix_(d, d)] + s2 * np.eye(len(d))
    if np.ndim(g) == 0:
        cg, vg = A[g, d], A[g, g]
    else:
        cg, vg = g @ A[:, d], g @ A @ g
    R2 = cg @ np.linalg.solve(Sy, cg) / vg
    return R2, -0.5 * np.log(1 - min(R2, 1 - 1e-12))


def prag(A, mu, d, s2, tauA, tauB, two=True):
    """PRAG-GO closed form: EIG of 1{zA>tauA} (two=False) or 1{max(zA-tauA, zB-tauB)>0}."""
    d = list(d)
    Sy = A[np.ix_(d, d)] + s2 * np.eye(len(d))
    C = A[np.ix_([32, 33], d)]
    K = C @ np.linalg.solve(Sy, C.T); Sz = A[np.ix_([32, 33], [32, 33])]; P = Sz - K
    if not two:
        R2 = K[0, 0] / Sz[0, 0]; t = (tauA - mu[32]) / np.sqrt(Sz[0, 0])
        u = hx
        p = 1 - norm.cdf((t - np.sqrt(R2) * u) / np.sqrt(1 - R2))
        return h(norm.sf(t)) - (hw * h(p)).sum()
    w, V = np.linalg.eigh(K); L = V * np.sqrt(np.clip(w, 0, None)); m = L @ UU
    s = np.sqrt(np.diag(P)); r = np.clip(P[0, 1] / (s[0] * s[1]), -0.999, 0.999)
    p = 1 - Phi2((tauA - mu[32] - m[0]) / s[0], (tauB - mu[33] - m[1]) / s[1], r)
    r0 = Sz[0, 1] / np.sqrt(Sz[0, 0] * Sz[1, 1])
    p0 = 1 - Phi2(np.array((tauA - mu[32]) / np.sqrt(Sz[0, 0])), np.array((tauB - mu[33]) / np.sqrt(Sz[1, 1])), r0)
    return float(h(p0) - (W2 * h(p)).sum())


# ---------------------------------------------------------------- exact (re-weighting)
DK = None; QW = None; S2 = None
def exact_one(d):
    a, b, c = d
    Ssum = DK[a] + DK[b] + DK[c]
    Ssum -= Ssum.min(1, keepdims=True)
    w = np.exp(-Ssum / (2 * S2))
    sw = w.sum(1, dtype=np.float64); p = (w @ QW).astype(np.float64) / sw[:, None]
    p = np.clip(p, 0.0, 1.0)
    ess = (sw ** 2 / (w.astype(np.float64) ** 2).sum(1)).mean()
    return h(P0) - h(p).mean(0), ess


def init_dk(s2, n_in):
    global DK, QW, S2
    rng = np.random.default_rng(11)
    y = go + np.sqrt(s2) * rng.standard_normal(go.shape)
    DK = np.empty((32, go.shape[0], n_in), dtype=np.float32)
    for k in range(32):
        DK[k] = (y[:, k, None] - gi[None, :n_in, k]) ** 2
    QW = QIN[:n_in].astype(np.float32); S2 = s2


if __name__ == '__main__':
    print(f'prior P(A)={P0[0]:.3f}  P(A or B)={P0[1]:.3f}  inner {len(gi)}  outer {len(go)}')
    # normal-score transform: candidates are noisy observations; A and B are noise-free goals
    for s in SIGMAS:
        s2 = s * s; t0 = time.time()
        rng = np.random.default_rng(3)
        yno = gi + s * rng.standard_normal(gi.shape)
        nsY = np.column_stack([np.column_stack([normal_scores(yno[:, k], yno[:, k]) for k in range(32)]),
                               normal_scores(cAi, cAi), normal_scores(cBi, cBi)])
        A_ns = np.cov(nsY.T); mu_ns = nsY.mean(0)
        tA_ns, tB_ns = normal_scores(np.array([TAU]), cAi)[0], normal_scores(np.array([TAU]), cBi)[0]
        rows = []
        for d in D3:
            r = {}
            r['mass'] = lin_eig(A_adj, d, 34, s2)[1]
            r['meanAB'] = lin_eig(A_adj, d, np.r_[np.zeros(32), 0.5, 0.5, 0.0], s2)[1]
            r['cA'] = lin_eig(A_adj, d, 32, s2)[1]
            r['pragAdjA'] = prag(A_adj, mu_adj, d, s2, TAU, TAU, two=False)
            r['pragAdj'] = prag(A_adj, mu_adj, d, s2, TAU, TAU)
            r['pragEns'] = prag(A_ens, mu_ens, d, s2, TAU, TAU)
            r['pragNSA'] = prag(A_ns, mu_ns, d, 0.0, tA_ns, tB_ns, two=False)
            r['pragNS'] = prag(A_ns, mu_ns, d, 0.0, tA_ns, tB_ns)
            r['massEns'] = lin_eig(A_ens, d, 34, s2)[1]
            rows.append([r[k] for k in ['mass', 'meanAB', 'cA', 'pragAdjA', 'pragAdj', 'pragEns', 'pragNSA', 'pragNS', 'massEns']])
        LIN = np.array(rows)
        print(f'sigma={s}: linear criteria done {time.time() - t0:.0f}s')
        init_dk(s2, len(gi))
        with Pool(4) as p:
            res = p.map(exact_one, D3, chunksize=40)
        EX = np.array([r[0] for r in res]); ESS = np.array([r[1] for r in res])
        print(f'sigma={s}: exact done {time.time() - t0:.0f}s')
        np.savez(f'{OUT}/designs_s{s}.npz', LIN=LIN, EX=EX, ESS=ESS, D3=np.array(D3), P0=P0)
        names = ['mass', 'meanAB', 'cA', 'pragAdjA', 'pragAdj', 'pragEns', 'pragNSA', 'pragNS', 'massEns']
        for gk, gname in [(0, 'risk A'), (1, 'risk A or B')]:
            ex = EX[:, gk]; best = ex.argmax()
            print(f'  {gname}: exact optimum {D3[best]} EIG {ex[best]:.4f} nats (H0 {h(P0[gk]):.4f}), ESS {ESS[best]:.0f}')
            for j, nm in enumerate(names):
                i = LIN[:, j].argmax()
                print(f'    {nm:9s} picks {D3[i]} -> exact {ex[i]:.4f} = {ex[i] / ex[best]:.1%}   Spearman {spearmanr(LIN[:, j], ex).correlation:.3f}')
