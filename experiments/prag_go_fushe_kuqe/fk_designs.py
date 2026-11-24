"""Stage 3: designs on the Fushe-Kuqe ensemble.

Goals (all binary, Ghyben-Herzberg criterion h < hcrit = delta * base = 1.0 m):
  rA    supply well A (north sector) intruded
  rAB   A or B (B: south sector) intruded
  rArea intruded area larger than 100 km^2 (the project's goal turned into a threshold)
Supply wells: in each sector (north y > 25 km, south y < 25 km) the inside well whose prior
intrusion probability is closest to 1/2, among the wells not used by the published monitoring
design; they are excluded from the candidates (pumping disturbs their own heads).

Criteria (linear ones use the project's linearization at the prior mean):
  area     Lemma 1 EIG of the intruded area (the published pipeline)
  areaEns  the same with ensemble moments
  hA       Lemma 1 EIG of the head at A (Theorem 1 for rA)
  meanAB   Lemma 1 EIG of the mean head at A and B
  pragLin  PRAG-GO closed form for rAB, linearized moments
  pragEns  the same with ensemble moments
  pragNSA  PRAG-GO for rA after the normal-score transform
  pragNS   PRAG-GO for rAB after the normal-score transform
Exact EIG: likelihood re-weighting of the inner ensemble, shared outer samples and noise.
"""
import sys, time, itertools, json
import numpy as np
from multiprocessing import Pool
from numpy.polynomial.hermite_e import hermegauss
from scipy.stats import norm, spearmanr

OUT = sys.argv[1]
SN = 0.2; HC = 1.0; AREA_T = 100.0
PUBLISHED = ['P21', 'A12', 'A13', 'A21', 'A10']
NAMES = ['area', 'areaEns', 'hA', 'meanAB', 'pragLin', 'pragEns', 'pragNSA', 'pragNS']

# ---------------------------------------------------------------- receptors from the base prior
Lb = np.load('res_base/lin.npz', allow_pickle=True); Eb = np.load('res_base/ens.npz')
ids, xy = Lb['ids'].astype(str), Lb['xy']
pb = (Eb['inner'][:, :32] < HC).mean(0)
def pick(mask):
    ok = np.flatnonzero(mask & ~np.isin(ids, PUBLISHED))
    return ok[np.argmin(np.abs(pb[ok] - 0.5))]
iA = pick(xy[:, 1] > 25.0); iB = pick(xy[:, 1] < 25.0)
CAND = np.array([k for k in range(32) if k not in (iA, iB)])
NC = len(CAND)

E = np.load(f'{OUT}/ens.npz'); L = np.load(f'{OUT}/lin.npz', allow_pickle=True)
inner, outer = E['inner'], E['outer']
gi, go = inner[:, CAND], outer[:, CAND]
hAi, hBi, ari = inner[:, iA], inner[:, iB], inner[:, 32]
QIN = np.stack([hAi < HC, np.minimum(hAi, hBi) < HC, ari > AREA_T], 1).astype(np.float64)
P0 = QIN.mean(0)


def h(p):
    p = np.clip(np.asarray(p, dtype=np.float64), 0.0, 1.0)
    return -(np.where(p > 0, p * np.log(np.where(p > 0, p, 1.0)), 0.0) + np.where(p < 1, (1 - p) * np.log(np.where(p < 1, 1 - p, 1.0)), 0.0))


# variables: 0..NC-1 candidates, NC = A, NC+1 = B, NC+2 = area
ORD = np.r_[CAND, iA, iB, 32]
S = L['S'][ORD]; GAM = L['GAM']
A_lin = S @ GAM @ S.T; mu_lin = L['mu0'][ORD]
Y = inner[:, ORD]
A_ens = np.cov(Y.T); mu_ens = Y.mean(0)
IA, IB, IR = NC, NC + 1, NC + 2


def normal_scores(v, ref):
    r = np.searchsorted(np.sort(ref), v, side='right')
    return norm.ppf(np.clip(r / (len(ref) + 1), 1e-6, 1 - 1e-6))


gl_x, gl_w = np.polynomial.legendre.leggauss(64)
def Phi2(a, b, r):
    """P(X < a, Y < b) for a standard bivariate normal with correlation r."""
    lo = -9.0; hi = np.maximum(a, lo + 1e-9)
    t = 0.5 * (hi - lo)[..., None] * gl_x + 0.5 * (hi + lo)[..., None]
    f = norm.pdf(t) * norm.cdf((b[..., None] - r * t) / np.sqrt(1 - r ** 2))
    return (0.5 * (hi - lo)[..., None] * f * gl_w).sum(-1)
hx, hw = hermegauss(24); hw = hw / hw.sum()
U1, U2 = np.meshgrid(hx, hx, indexing='ij'); W2 = np.outer(hw, hw).ravel(); UU = np.stack([U1.ravel(), U2.ravel()])


def lin_eig(A, d, g, s2):
    d = list(d); Sy = A[np.ix_(d, d)] + s2 * np.eye(len(d))
    if np.ndim(g) == 0:
        cg, vg = A[g, d], A[g, g]
    else:
        cg, vg = g @ A[:, d], g @ A @ g
    R2 = cg @ np.linalg.solve(Sy, cg) / vg
    return -0.5 * np.log(1 - min(R2, 1 - 1e-12))


def prag(A, mu, d, s2, tA, tB, two=True):
    """PRAG-GO closed form for intrusion events {z < t}: 1{zA < tA} or 1{zA < tA or zB < tB}."""
    d = list(d); Sy = A[np.ix_(d, d)] + s2 * np.eye(len(d))
    C = A[np.ix_([IA, IB], d)]
    K = C @ np.linalg.solve(Sy, C.T); Sz = A[np.ix_([IA, IB], [IA, IB])]; P = Sz - K
    if not two:
        R2 = min(K[0, 0] / Sz[0, 0], 1 - 1e-12); t = (tA - mu[IA]) / np.sqrt(Sz[0, 0])
        p = norm.cdf((t - np.sqrt(R2) * hx) / np.sqrt(1 - R2))
        return float(h(norm.cdf(t)) - (hw * h(p)).sum())
    w, V = np.linalg.eigh(K); Lk = V * np.sqrt(np.clip(w, 0, None)); m = Lk @ UU
    s = np.sqrt(np.clip(np.diag(P), 1e-12, None)); r = np.clip(P[0, 1] / (s[0] * s[1]), -0.999, 0.999)
    # P(no intrusion) = P(zA > tA, zB > tB) = Phi2(-(tA - mA)/sA, -(tB - mB)/sB, r)
    p = 1 - Phi2((mu[IA] + m[0] - tA) / s[0], (mu[IB] + m[1] - tB) / s[1], r)
    r0 = Sz[0, 1] / np.sqrt(Sz[0, 0] * Sz[1, 1])
    p0 = 1 - Phi2(np.array((mu[IA] - tA) / np.sqrt(Sz[0, 0])), np.array((mu[IB] - tB) / np.sqrt(Sz[1, 1])), r0)
    return float(h(p0) - (W2 * h(p)).sum())


def criteria(d, s2, ns):
    A_ns, mu_ns, tA_ns, tB_ns = ns
    r = {}
    r['area'] = lin_eig(A_lin, d, IR, s2)
    r['areaEns'] = lin_eig(A_ens, d, IR, s2)
    r['hA'] = lin_eig(A_lin, d, IA, s2)
    g = np.zeros(NC + 3); g[IA] = g[IB] = 0.5
    r['meanAB'] = lin_eig(A_lin, d, g, s2)
    r['pragLin'] = prag(A_lin, mu_lin, d, s2, HC, HC)
    r['pragEns'] = prag(A_ens, mu_ens, d, s2, HC, HC)
    r['pragNSA'] = prag(A_ns, mu_ns, d, 0.0, tA_ns, tB_ns, two=False)
    r['pragNS'] = prag(A_ns, mu_ns, d, 0.0, tA_ns, tB_ns)
    return [r[k] for k in NAMES]


# ---------------------------------------------------------------- exact (re-weighting)
DK = None; QW = None
def init_dk(seed=11):
    global DK, QW
    rng = np.random.default_rng(seed)
    y = go + SN * rng.standard_normal(go.shape)
    DK = np.empty((NC, go.shape[0], gi.shape[0]), dtype=np.float32)
    for k in range(NC):
        DK[k] = (y[:, k, None] - gi[None, :, k]) ** 2
    QW = QIN.astype(np.float32)


def exact_one(d):
    Ssum = DK[d[0]].copy()
    for k in d[1:]:
        Ssum += DK[k]
    Ssum -= Ssum.min(1, keepdims=True)
    Ssum *= np.float32(-1.0 / (2 * SN * SN))
    np.maximum(Ssum, np.float32(-80.0), out=Ssum)        # avoids float32 denormals; exp(-80) ~ 2e-35
    w = np.exp(Ssum, out=Ssum)
    sw = w.sum(1, dtype=np.float64); p = (w @ QW).astype(np.float64) / sw[:, None]
    ess = (sw ** 2 / np.einsum('ij,ij->i', w, w).astype(np.float64)).mean()
    return np.r_[h(P0) - h(p).mean(0), ess]


def ns_moments(seed=3):
    rng = np.random.default_rng(seed)
    yno = gi + SN * rng.standard_normal(gi.shape)
    nsY = np.column_stack([np.column_stack([normal_scores(yno[:, k], yno[:, k]) for k in range(NC)]),
                           normal_scores(hAi, hAi), normal_scores(hBi, hBi), normal_scores(ari, ari)])
    tA = normal_scores(np.array([HC]), hAi)[0]; tB = normal_scores(np.array([HC]), hBi)[0]
    return np.cov(nsY.T), nsY.mean(0), tA, tB


def crit_chunk(args):
    designs, ns = args
    return [criteria(d, SN ** 2, ns) for d in designs]


if __name__ == '__main__':
    t0 = time.time()
    print(f'{OUT}: supply well A = {ids[iA]} (P0 {pb[iA]:.3f}), B = {ids[iB]} (P0 {pb[iB]:.3f}); P0 this prior = {np.round(P0, 3)}')
    ns = ns_moments()
    init_dk()
    pubd = tuple(int(np.flatnonzero(ids[CAND] == w)[0]) for w in PUBLISHED)
    out = {'ids': ids.tolist(), 'iA': int(iA), 'iB': int(iB), 'CAND': CAND.tolist(), 'P0': P0.tolist(), 'pub': pubd}
    with Pool(4) as pool:
        # ------------- exhaustive 3-well designs
        D3 = list(itertools.combinations(range(NC), 3))
        LIN3 = np.vstack(pool.map(crit_chunk, [(D3[k::16], ns) for k in range(16)]))
        order = np.concatenate([np.arange(k, len(D3), 16) for k in range(16)])
        L3 = np.empty_like(LIN3); L3[order] = LIN3; LIN3 = L3
        print(f'3-well linear criteria {time.time() - t0:.0f}s')
        EX3 = np.array(pool.map(exact_one, D3, chunksize=20))
        print(f'3-well exact {time.time() - t0:.0f}s')
        np.savez(f'{OUT}/d3.npz', LIN=LIN3, EX=EX3, D=np.array(D3), P0=P0)
        # ------------- 5-well designs: every criterion over all designs, exact on a pool
        D5 = np.array(list(itertools.combinations(range(NC), 5)))
        LIN5 = np.vstack(pool.map(crit_chunk, [([tuple(r) for r in D5[k::64]], ns) for k in range(64)]))
        order = np.concatenate([np.arange(k, len(D5), 64) for k in range(64)])
        L5 = np.empty_like(LIN5); L5[order] = LIN5; LIN5 = L5
        print(f'5-well linear criteria ({len(D5)} designs) {time.time() - t0:.0f}s')
        rng = np.random.default_rng(5)
        pool_idx = set(rng.choice(len(D5), 3000, replace=False).tolist())
        for j in range(len(NAMES)):
            pool_idx |= set(np.argsort(-LIN5[:, j])[:200].tolist())
        pub_i = int(np.flatnonzero((D5 == np.sort(pubd)).all(1))[0]); pool_idx.add(pub_i)
        pool_idx = sorted(pool_idx)
        EX5p = np.array(pool.map(exact_one, [tuple(D5[i]) for i in pool_idx], chunksize=10))
        print(f'5-well exact on {len(pool_idx)} designs {time.time() - t0:.0f}s')
        # greedy + swap local search on the exact EIG, separately for each goal
        best = {}
        for gk in range(3):
            cur = []
            for _ in range(5):
                cands = [tuple(sorted(cur + [k])) for k in range(NC) if k not in cur]
                vals = np.array(pool.map(exact_one, cands, chunksize=2))[:, gk]
                cur = list(cands[int(np.argmax(vals))])
            val = exact_one(tuple(cur))[gk]
            improved = True
            while improved:
                improved = False
                swaps = [tuple(sorted([x for x in cur if x != a] + [b])) for a in cur for b in range(NC) if b not in cur]
                vals = np.array(pool.map(exact_one, swaps, chunksize=4))[:, gk]
                if vals.max() > val + 1e-6:
                    cur = list(swaps[int(np.argmax(vals))]); val = vals.max(); improved = True
            best[gk] = (tuple(cur), float(val))
            print(f'  goal {gk}: greedy+swap {cur} -> {val:.4f}  {time.time() - t0:.0f}s')
    np.savez(f'{OUT}/d5.npz', LIN=LIN5, D=D5, pool=np.array(pool_idx), EXp=EX5p, pub=pub_i,
             gbest=np.array([best[g][0] for g in range(3)]), gval=np.array([best[g][1] for g in range(3)]))
    json.dump(out, open(f'{OUT}/meta.json', 'w'))
    # ---------------------------------------------------------------- summary
    gnames = ['rA', 'rAB', 'rArea']
    for gk in range(3):
        ex = EX3[:, gk]; b = ex.argmax()
        print(f'[3 wells] {gnames[gk]}: optimum {D3[b]} {ex[b]:.4f} nats (H0 {h(P0[gk]):.4f}) ESS {EX3[b, 3]:.0f}')
        for j, nm in enumerate(NAMES):
            i = LIN3[:, j].argmax()
            print(f'    {nm:8s} {D3[i]} -> {ex[i] / ex[b]:.1%}  Spearman {spearmanr(LIN3[:, j], ex).correlation:.3f}')
    pidx = np.array(pool_idx)
    for gk in range(3):
        ref = max(EX5p[:, gk].max(), best[gk][1])
        print(f'[5 wells] {gnames[gk]}: best found {ref:.4f}; published {EX5p[pidx.tolist().index(pub_i), gk] / ref:.1%}')
        for j, nm in enumerate(NAMES):
            i = int(LIN5[:, j].argmax()); k = pidx.tolist().index(i)
            print(f'    {nm:8s} {[ids[CAND[v]] for v in D5[i]]} -> {EX5p[k, gk] / ref:.1%}')
    print(f'done {time.time() - t0:.0f}s')
