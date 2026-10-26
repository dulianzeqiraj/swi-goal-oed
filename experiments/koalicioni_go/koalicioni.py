"""KOALICIONI-GO: which coalition of well-record holders the Fushe-Kuqe utility should form, in what order to merge,
when to stop, and how to share the value fairly -- all before any record is shared.

Innovation of literature review 56 (second review on the topic of Fawkes, Ter-Minassian, Ivanova, Shalit & Holmes,
AISTATS 2025, "Is merging worth it?"). It extends BASHKIMI-GO (review 55, ../bashkimi_go), whose truth generator,
physics-informed Bayesian CATE model and decision value it reuses, from one merge to coalitions of holders.

Holders (host = water utility, as in review 55): monitoring agency (inland, balanced), private irrigators (mid plain,
mostly pumped hard), coastal hotels (ALWAYS pumped hard in summer, p = 1), municipal coastal wells (capped by law,
ALWAYS pumped low, p = 0) and a research campaign (designed). Hotels and municipal wells each see one pumping regime
near the coast: alone they barely identify the effect there; together they do (Proposition K2).
For every world (plausible aquifer):
  * predicted decision value V(S) of every coalition S of the five holders, from the sum of their Gram matrices
    (Proposition K1), and the realised gain R(S), averaged over NREP draws of the holders' outcomes;
  * merge policies under a cost c per merged holder: best single holder (BASHKIMI-GO), all holders, greedy
    (non-adaptive), optimal coalition by V(S) - c|S|, and ADAPTIVE sequential merging (merge the holder of largest
    value, update with its actual records, re-value the rest, stop when no value exceeds c);
  * Shapley and Banzhaf shares of the holders (and of the host as a veto player), convexity and the core;
  * robustness of the shares to noise on the coalition values (the Data Banzhaf claim) and privacy: per-holder noise
    on clipped whitened information, after which all coalition values are post-processing (no composition).
Run: see run_all.sh (KOA_DRIFT=1: physics-informed model with a drift field; KOA_MODEL=local: local statistical model)
"""
import os, sys, json, time, itertools
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'bashkimi_go'))
import bashkimi as B

OUT = os.path.join(HERE, 'res')
B.HOLDERS = [
    dict(key='U', name='Water utility (host)', nw=20, ns=3, d=(4.0, 10.0), p=0.90),
    dict(key='A', name='Monitoring agency', nw=60, ns=5, d=(3.0, 14.5), p=0.50),
    dict(key='I', name='Private irrigators', nw=30, ns=4, d=(1.5, 5.0), p=0.85),
    dict(key='H', name='Coastal hotels', nw=8, ns=4, d=(0.2, 1.5), p=1.0),
    dict(key='M', name='Municipal coastal wells', nw=10, ns=4, d=(0.2, 2.0), p=0.0),
    dict(key='R', name='Research campaign', nw=12, ns=2, d=(0.2, 14.5), p=0.50),
]
NH = len(B.HOLDERS) - 1                     # candidates
DRIFT = os.environ.get('KOA_DRIFT', '0') == '1'   # scenario b: unmodelled local coastal drift in truth and model
LOCAL = os.environ.get('KOA_MODEL', 'phys') == 'local'   # scenario c: local statistical model, no physics (needs DRIFT)
if LOCAL:
    DRIFT = True
TAG = '_local' if LOCAL else ('_drift' if DRIFT else '')
SD_DRIFT = 0.08                             # sd of the local seasonal drift at the coast (log chloride)
DECAY_D = 3.0                               # km, decay of the local drift inland
ELL_D = 2.5                                 # km, range of the local drift field (squared exponential)


def kse(c1, c2, ell):
    m = B.m
    D2 = (m.cx[c1][:, None] - m.cx[c2][None]) ** 2 + (m.cy[c1][:, None] - m.cy[c2][None]) ** 2
    return np.exp(-D2 / ell ** 2)


_KD = None
def drift_basis():
    global _KD
    if _KD is None:
        K = kse(B.UCELL, B.UCELL, ELL_D) + 1e-6 * np.eye(B.NU)
        _KD = (K, np.linalg.inv(K))
    return _KD


def world_drift(i):
    """scenario b: the world of review 55 plus a local coastal drift field the groundwater model does not contain;
    the Bayesian model gets a matching baseline field (predictive process on the same lattice)."""
    w = B.make_world(i)
    rng = np.random.default_rng([660000, i])
    cells = np.unique(np.concatenate([x['wells'] for x in w['W']] + [w['tg']]))
    K = kse(cells, cells, ELL_D) + 1e-8 * np.eye(len(cells))
    f = np.linalg.cholesky(K) @ rng.standard_normal(len(cells))
    amp = SD_DRIFT * np.exp(-B.DIST[cells] / DECAY_D)
    dd = dict(zip(cells, amp * f))
    for x in w['W']:
        x['ymean'] = x['ymean'] + np.array([dd[c] for c in x['cells']])
        x['y'] = x['y'] + np.array([dd[c] for c in x['cells']])
    return w


def design_drift(x):
    Phi, sd = B.design(x)
    K, Ki = drift_basis()
    Ab = (SD_DRIFT * np.exp(-B.DIST[x['cells']] / DECAY_D))[:, None] * (kse(x['cells'], B.UCELL, ELL_D) @ Ki)
    return np.c_[Phi[:, :B.PB], Ab, Phi[:, B.PB:]], sd


def prior_drift():
    mu, S = B.prior()
    K, _ = drift_basis()
    p0, nu = len(mu), B.NU
    mu2 = np.r_[mu[:B.PB], np.zeros(nu), mu[B.PB:]]
    S2 = np.zeros((p0 + nu, p0 + nu))
    S2[:B.PB, :B.PB] = S[:B.PB, :B.PB]; S2[B.PB:B.PB + nu, B.PB:B.PB + nu] = K
    S2[B.PB + nu:, B.PB + nu:] = S[B.PB:, B.PB:]
    return mu2, S2


# ---- scenario c: a local statistical CATE model without the groundwater physics
AMP_B = lambda d: 0.12 * np.exp(-d / DECAY_D)          # local baseline field (systematic and local drift)
AMP_T = lambda d: 0.25 * np.exp(-d / 2.5) + 0.01       # local CATE field: larger near the sea
_KT = None
def cate_basis():
    global _KT
    if _KT is None:
        ell = float(B.CAL['ell'])
        K = kse(B.UCELL, B.UCELL, ell) + 1e-6 * np.eye(B.NU)
        _KT = (K, np.linalg.inv(K), ell)
    return _KT


def rows_local(cells, a):
    d = B.DIST[cells]
    _, KDi = drift_basis(); _, KTi, ell = cate_basis()
    Ab = AMP_B(d)[:, None] * (kse(cells, B.UCELL, ELL_D) @ KDi)
    At = AMP_T(d)[:, None] * (kse(cells, B.UCELL, ell) @ KTi)
    one = np.ones((len(cells), 1))
    return np.c_[one, Ab, a[:, None] * np.c_[one, At]]


def design_local(x):
    B.load_calib()
    sd = np.sqrt(B.sig_base() ** 2 + x['a'] * (0.3 * AMP_T(B.DIST[x['cells']])) ** 2)
    return rows_local(x['cells'], x['a']), sd


def prior_local():
    B.load_calib()
    KD, _ = drift_basis(); KT, _, _ = cate_basis(); nu = B.NU
    p = 2 * (1 + nu)
    mu = np.zeros(p); mu[0] = 0.03; mu[1 + nu] = 0.05
    S = np.zeros((p, p)); S[0, 0] = 0.05 ** 2; S[1:1 + nu, 1:1 + nu] = KD
    S[1 + nu, 1 + nu] = 0.1 ** 2; S[2 + nu:, 2 + nu:] = KT
    return mu, S


def targets_local(cells, lt):
    C = rows_local(cells, np.ones(len(cells)))
    C[:, :1 + B.NU] = 0.0
    return C, (0.3 * AMP_T(B.DIST[cells])) ** 2


def targets_drift(cells, lt):
    Ct, vn = B.targets(cells, lt)
    return np.c_[Ct[:, :B.PB], np.zeros((len(cells), B.NU)), Ct[:, B.PB:]], vn
SUBSETS = [s for r in range(NH + 1) for s in itertools.combinations(range(NH), r)]   # includes ()
IDX = {s: i for i, s in enumerate(SUBSETS)}
COSTS = (0.0, 0.01, 0.02, 0.04)
NREP = 20
EPS = (1.0, 3.0, 10.0, 30.0)
LAM_C = 0.3
SIGMAS = (0.001, 0.003, 0.01)               # noise on coalition values (robustness of Shapley vs Banzhaf)


def mask(s):
    m = np.zeros(NH, bool); m[list(s)] = True; return m


# ------------------------------------------------------------------ cooperative-game quantities
def shapley(v):
    """v: dict subset -> value over the NH candidates."""
    from math import factorial
    phi = np.zeros(NH)
    for s in SUBSETS:
        for k in range(NH):
            if k in s:
                continue
            t = tuple(sorted(s + (k,)))
            w = factorial(len(s)) * factorial(NH - len(s) - 1) / factorial(NH)
            phi[k] += w * (v[t] - v[s])
    return phi


def banzhaf(v):
    b = np.zeros(NH)
    for s in SUBSETS:
        for k in range(NH):
            if k not in s:
                b[k] += v[tuple(sorted(s + (k,)))] - v[s]
    return b / 2 ** (NH - 1)


def convex_and_core(v, tol=1e-9):
    """game of the host (veto player 0) and the candidates 1..NH: w(T) = V(T without host) if host in T else 0.
    Returns: supermodular?, Shapley allocation in the core?, host share of the Shapley value."""
    from math import factorial
    n = NH + 1
    def w(T):
        if 0 not in T:
            return 0.0
        return v[tuple(sorted(k - 1 for k in T if k != 0))]
    players = range(n)
    allT = [T for r in range(n + 1) for T in itertools.combinations(players, r)]
    W = {T: w(T) for T in allT}
    phi = np.zeros(n)
    for T in allT:
        for k in players:
            if k in T:
                continue
            U = tuple(sorted(T + (k,)))
            phi[k] += factorial(len(T)) * factorial(n - len(T) - 1) / factorial(n) * (W[U] - W[T])
    conv = True
    for T in allT:
        for k in players:
            for l in players:
                if k < l and k not in T and l not in T:
                    Tk = tuple(sorted(T + (k,))); Tl = tuple(sorted(T + (l,))); Tkl = tuple(sorted(T + (k, l)))
                    if W[Tkl] - W[Tk] < W[Tl] - W[T] - tol:
                        conv = False
    core = all(phi[list(T)].sum() >= W[T] - 1e-9 for T in allT if T)
    tot = W[tuple(players)]
    return conv, core, float(phi[0] / tot) if tot > 0 else 0.0, phi


# ------------------------------------------------------------------ one world
def run_world(i, nrep=NREP):
    if LOCAL:
        mu, S = prior_local(); w = world_drift(i)
        Ct, vn = targets_local(w['tg'], w['tg_lt']); D = [design_local(x) for x in w['W']]
    elif DRIFT:
        mu, S = prior_drift(); w = world_drift(i)
        Ct, vn = targets_drift(w['tg'], w['tg_lt']); D = [design_drift(x) for x in w['W']]
    else:
        mu, S = B.prior(); w = B.make_world(i)
        Ct, vn = B.targets(w['tg'], w['tg_lt']); D = [B.design(x) for x in w['W']]
    m0, S0 = B.posterior(D[0][0], D[0][1], w['W'][0]['y'], mu, S)
    P0 = np.linalg.inv(S0); P0 = 0.5 * (P0 + P0.T)
    a0 = B.act(Ct @ m0, B.qform(Ct, S0) + vn)
    L0 = B.true_loss(a0, w['tau_t'])
    Q = [D[k + 1][0] / D[k + 1][1][:, None] for k in range(NH)]
    G = [q.T @ q for q in Q]
    Pm0 = P0 @ m0

    def value_of(Pcur, mcur, Scur, Gadd):
        S1 = np.linalg.inv(Pcur + Gadd)
        return float(B.decision_value(mcur, Scur, 0.5 * (S1 + S1.T), Ct, vn)[0].sum())

    # predicted values and the EIG of the CATE parameters of every coalition
    V, EIGc = {}, {}
    if LOCAL:
        i1 = 1 + B.NU; i2 = 2 * (1 + B.NU)
    else:
        i1 = B.PB + (B.NU if DRIFT else 0); i2 = i1 + B.PT + B.NU
    _, lg0 = np.linalg.slogdet(S0[i1:i2, i1:i2])
    for s in SUBSETS:
        Gs = sum((G[k] for k in s), np.zeros_like(P0))
        S1 = np.linalg.inv(P0 + Gs)
        V[s] = float(B.decision_value(m0, S0, S1, Ct, vn)[0].sum()) if s else 0.0
        EIGc[s] = 0.5 * (lg0 - np.linalg.slogdet(S1[i1:i2, i1:i2])[1]) if s else 0.0
    # outcomes: replicate draws of every candidate's records
    Z = [[(w['W'][k + 1]['y'] if r == 0 else B.draw_y(i, k + 1, r, B.HOLDERS[k + 1], w['W'][k + 1])) / D[k + 1][1]
          for r in range(nrep)] for k in range(NH)]
    bvec = [[Q[k].T @ Z[k][r] for r in range(nrep)] for k in range(NH)]

    def loss_after(s, r):
        if not s:
            return L0
        Ps = P0 + sum(G[k] for k in s)
        S1 = np.linalg.inv(Ps); m1 = S1 @ (Pm0 + sum(bvec[k][r] for k in s))
        return B.true_loss(B.act(Ct @ m1, B.qform(Ct, S1) + vn), w['tau_t'])

    LOSS = {s: [loss_after(s, r) for r in range(nrep)] for s in SUBSETS}
    R = {s: L0 - float(np.mean(LOSS[s])) for s in SUBSETS}

    # merge policies
    pol = {}
    for c in COSTS:
        out = {}
        single = max(range(NH), key=lambda k: V[(k,)])
        out['single'] = (single,) if V[(single,)] > c else ()
        out['all'] = tuple(range(NH))
        g = ()
        while True:
            cand = [(V[tuple(sorted(g + (k,)))] - V[g], k) for k in range(NH) if k not in g]
            if not cand:
                break
            dv, k = max(cand)
            if dv <= c:
                break
            g = tuple(sorted(g + (k,)))
        out['greedy'] = g
        out['optimal'] = max(SUBSETS, key=lambda s: V[s] - c * len(s))
        out['eig_greedy'] = None
        res = {k: dict(set=list(s), net=R[s] - c * len(s)) for k, s in out.items() if s is not None}
        # adaptive sequential merging
        nets, sizes, orders = [], [], []
        for r in range(nrep):
            Pcur, mcur, Scur = P0.copy(), m0.copy(), S0.copy(); rem = list(range(NH)); merged = []
            while rem:
                vals = [value_of(Pcur, mcur, Scur, G[k]) for k in rem]
                j = int(np.argmax(vals))
                if vals[j] <= c:
                    break
                k = rem.pop(j); merged.append(k)
                Pnew = Pcur + G[k]; Snew = np.linalg.inv(Pnew); Snew = 0.5 * (Snew + Snew.T)
                mcur = Snew @ (Pcur @ mcur + bvec[k][r]); Pcur, Scur = Pnew, Snew
            loss = B.true_loss(B.act(Ct @ mcur, B.qform(Ct, Scur) + vn), w['tau_t'])
            nets.append(L0 - loss - c * len(merged)); sizes.append(len(merged)); orders.append(merged)
        res['adaptive'] = dict(net=float(np.mean(nets)), size=float(np.mean(sizes)), first=[o[0] if o else -1 for o in orders])
        res['oracle'] = dict(net=max(R[s] - c * len(s) for s in SUBSETS))
        pol[str(c)] = res

    # games
    vS = {s: V[s] for s in SUBSETS}; vR = {s: R[s] for s in SUBSETS}
    shV, shR, bzV, bzR = shapley(vS), shapley(vR), banzhaf(vS), banzhaf(vR)
    convV, coreV, hostV, phiV = convex_and_core(vS)
    convR, coreR, hostR, _ = convex_and_core(vR)
    pairs = {f'{a}{b}': dict(pred=V[(a, b)] - V[(a,)] - V[(b,)], real=R[(a, b)] - R[(a,)] - R[(b,)],
                              eig=EIGc[(a, b)] - EIGc[(a,)] - EIGc[(b,)]) for a, b in itertools.combinations(range(NH), 2)}
    # robustness of Shapley and Banzhaf rankings to noise on the coalition values
    rng = np.random.default_rng([880000, i])
    from scipy.stats import kendalltau
    rob = {}
    for sg in SIGMAS:
        ks, kb = [], []
        for _ in range(50):
            vn_ = {s: (vS[s] + sg * rng.standard_normal() if s else 0.0) for s in SUBSETS}
            ks.append(kendalltau(shV, shapley(vn_)).statistic); kb.append(kendalltau(bzV, banzhaf(vn_)).statistic)
        rob[str(sg)] = dict(shapley=float(np.nanmean(ks)), banzhaf=float(np.nanmean(kb)))
    # privacy: noise once per holder on clipped whitened information; all coalitions by post-processing
    L0c = np.linalg.cholesky(S0)
    Mw = []
    for k in range(NH):
        Rw = Q[k] @ L0c; nr = np.sum(Rw ** 2, 1); wc = np.minimum(1, LAM_C / nr)
        Mw.append((Rw * wc[:, None]).T @ Rw)
    p = P0.shape[0]; iu = np.triu_indices(p)
    priv = {}
    for e in EPS:
        noisy = []
        for k in range(NH):
            E = np.zeros((p, p)); E[iu] = B.GM_EXTRA[e] * LAM_C * rng.standard_normal(len(iu[0])); E = E + np.triu(E, 1).T
            noisy.append(Mw[k] + E)
        vP = {}
        for s in SUBSETS:
            vP[s] = B.value_from_whitened(sum(noisy[k] for k in s), L0c, m0, S0, Ct, vn) if s else 0.0
        res = {}
        for c in COSTS:
            sp = max(SUBSETS, key=lambda s: vP[s] - c * len(s))
            res[str(c)] = dict(net=R[sp] - c * len(sp), same=bool(sp == max(SUBSETS, key=lambda s: V[s] - c * len(s))))
        shP = shapley(vP)
        res['shapley_tau'] = float(kendalltau(shV, shP).statistic)
        priv[str(e)] = res
    vclip = {s: (B.value_from_whitened(sum(Mw[k] for k in s), L0c, m0, S0, Ct, vn) if s else 0.0) for s in SUBSETS}
    return dict(i=i, L0=L0, V={','.join(map(str, s)): V[s] for s in SUBSETS}, R={','.join(map(str, s)): R[s] for s in SUBSETS},
                EIG={','.join(map(str, s)): EIGc[s] for s in SUBSETS}, Vclip={','.join(map(str, s)): vclip[s] for s in SUBSETS},
                pol=pol, shapV=shV.tolist(), shapR=shR.tolist(), banzV=bzV.tolist(), banzR=bzR.tolist(),
                convV=convV, coreV=coreV, hostShareV=hostV, convR=convR, coreR=coreR, hostShareR=hostR, phiV=phiV.tolist(),
                pairs=pairs, rob=rob, priv=priv, treated=[float(x['a'].mean()) for x in w['W'][1:]])


def run(n):
    B.load_calib(); B.V.zeta_chol(); B.model_fields()
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    with Pool(4) as pool:
        Rr = pool.map(run_world, range(n), chunksize=1)
    json.dump(Rr, open(os.path.join(OUT, f'runs{TAG}_{n}.json'), 'w'))
    print(f'{n} worlds in {time.time() - t0:.0f} s')


B.GM_EXTRA = {e: B.gm_mult(e) for e in EPS}

if __name__ == '__main__':
    if sys.argv[1] == 'run':
        run(int(sys.argv[2]))
    elif sys.argv[1] == 'one':
        t0 = time.time(); r = run_world(int(sys.argv[2]), nrep=6)
        print(f'{time.time() - t0:.1f} s; treated shares', np.round(r['treated'], 2))
        for k, v in r['V'].items():
            print(f"  {{{k}}}: V {v:.4f}  R {r['R'][k]:+.4f}  EIG {r['EIG'][k]:.2f}  clip {r['Vclip'][k]:.4f}")
        print('pairs', {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in r['pairs'].items()})
        print('pol', json.dumps(r['pol'])[:900])
        print('shapV', np.round(r['shapV'], 4), 'banzV', np.round(r['banzV'], 4), 'conv/core', r['convV'], r['coreV'], 'host share', round(r['hostShareV'], 3))
        print('rob', r['rob']); print('priv', r['priv'])
