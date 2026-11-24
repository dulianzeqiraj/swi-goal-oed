"""SHKALLA-GO experiment: which laboratory experiments identify the calcite dissolution expected under an injection
barrier, when the rate law comes from a surface reaction graph (matrix-tree theorem) and depends on the activities of
Ca2+, CO3^2-, Mg2+ and SO4^2-, not on Omega alone?

Steps
 1. Banks: 60 000 draws of the graph law (prior below) and a 81 x 36 grid of the transition-state (TST) law, each run
    through the natural mixing zone (field data: Ca excess at a multilevel well) and through the barrier scenario
    (goal: calcite dissolved in the first kilometre). 400 further draws of the graph law serve as synthetic truths.
 2. Laboratory candidates: 210 solutions (7 saturation ratios x 5 Ca/CO3 activity ratios x 6 backgrounds). A lab
    experiment measures the dissolution rate with a 20% error (0.08 in log10) and an unknown laboratory prefactor, so
    lab data constrain the shape of the rate law only.
 3. Designs of eight experiments, each with the field well: the classical dilute series, a seawater series, both, the
    scenario's own waters, a parameter-oriented (D-optimal) and a goal-oriented (minimum goal variance) design.
 4. Algebra: the rank of each design's monomial matrix V (rows phi(a) = [1, aMg, aSO4, xC, xC aMg, xA, xA aSO4]) and
    the part of the goal's monomial subspace outside the row space of V (Theorem 2 of the report).
 5. Preposterior evaluation by importance weighting over the banks: error and 90% interval coverage for the goal,
    for the graph law and for the TST law fitted to the same data (the share of correct "barrier dissolves more than
    today" decisions is also stored; it is 1 for every design here and is not reported).
Writes shkalla_results.json and shkalla_bank.npz (bank outputs, about 8.5 MB, not committed). About 9 minutes on
4 cores; later runs reuse the bank and take under a minute. An optional argument sets the field error (default
0.005 mmol/L) and writes shkalla_results_sf<error>.json.
"""
import json, os, sys, time
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np
from multiprocessing import Pool
import shkalla as S

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
TAB = S.load_table()
REF = TAB['ref_la']
LKSP = REF.sum()                                    # log10 Ksp (mmol^2)
NB, NT, NG = 60000, 400, 120                        # bank, truths, design-optimization draws
SIG_L = 0.08                                        # lab error, log10 units
SIG_F = float(sys.argv[1]) if len(sys.argv) > 1 else 0.005     # field Ca-excess error, mmol/L
PRIOR = dict(lrho=(-5.0, -2.0), lpsi=(-2.0, 2.0), w=(0.05, 0.95), lKM=(-1.0, 1.5), lKS=(-1.0, 1.5))
NAMES = list(PRIOR)
CHUNK = 2500


def draw(n, seed):
    rng = np.random.default_rng(seed)
    return np.column_stack([rng.uniform(*PRIOR[k], n) for k in NAMES])


def graph_rate(U):
    return S.GraphRate(10 ** U[:, 0], 10 ** U[:, 1], U[:, 2], 10 ** U[:, 3], 10 ** U[:, 4], REF)


def _run(args):
    kind, U, line = args
    rate = graph_rate(U) if kind == 'graph' else S.TSTRate(10 ** U[:, 0], U[:, 1])
    out = S.simulate(rate, S.Chem(TAB, line))
    return out['obs'], out['G']


def run_bank(kind, U, pool):
    jobs = []
    for line in S.LINES:
        for i in range(0, len(U), CHUNK):
            jobs.append((kind, U[i:i + CHUNK], line))
    res = pool.map(_run, jobs)
    out = {}
    k = 0
    for line in S.LINES:
        obs, G = [], []
        for i in range(0, len(U), CHUNK):
            obs.append(res[k][0]); G.append(res[k][1]); k += 1
        out[f'obs_{line}'] = np.concatenate(obs); out[f'G_{line}'] = np.concatenate(G)
    return out


# ---------------------------------------------------------------- laboratory candidates
OMS = np.array([0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95])
RS = np.array([30.0, 100.0, 300.0, 1000.0, 3000.0])


def background(line, f):
    """activities of Mg and SO4 (mmol) of the unreacted mixture of seawater fraction f on a line"""
    i = int(round(f / (TAB['F'][1] - TAB['F'][0])))
    return 10 ** TAB[f'la_{line}'][2, i, 0], 10 ** TAB[f'la_{line}'][3, i, 0]


MG_MIX, SO4_MIX = background('nat', 0.2)
MG_SEA, SO4_SEA = background('nat', 1.0)
MG_FR, SO4_FR = background('nat', 0.0)
BACK = {'dilute': (0.0, 0.0), 'fresh': (MG_FR, SO4_FR), 'mix20': (MG_MIX, SO4_MIX), 'sea': (MG_SEA, SO4_SEA),
        'MgCl2': (MG_MIX, 0.0), 'Na2SO4': (0.0, SO4_MIX)}
CAND = []                                           # (background, Omega, r)
for b in BACK:
    for om in OMS:
        for r in RS:
            CAND.append((b, om, r))


def lab_la(cands):
    """log10 [aCa, aCO3, aMg, aSO4, Omega] of lab solutions, shape [5, n]"""
    out = []
    for b, om, r in cands:
        lca = 0.5 * (np.log10(om) + LKSP + np.log10(r)); lco3 = 0.5 * (np.log10(om) + LKSP - np.log10(r))
        mg, so4 = BACK[b]
        out.append([lca, lco3, np.log10(max(mg, 1e-12)), np.log10(max(so4, 1e-12)), np.log10(om)])
    return np.array(out).T


LA_C = lab_la(CAND)


def lab_shape_graph(U, la):
    """log10 of the dissolution rate per unit prefactor, [len(U), n]"""
    return np.log10(-S.graph_shape(la[:, None, :], 10 ** U[:, 1:2], U[:, 2:3], 10 ** U[:, 3:4], 10 ** U[:, 4:5], REF))


def lab_shape_tst(n, la):
    om = 10 ** la[4]
    return n[:, None] * np.log10(1 - om)[None, :]


def monomials(la):
    """phi(a) = [1, aMg, aSO4, xC, xC aMg, xA, xA aSO4] (activities in mmol), rows per composition"""
    xA = 10 ** (la[0] - REF[0]); xC = 10 ** (la[1] - REF[1]); mg = 10 ** la[2]; so4 = 10 ** la[3]
    mg = np.where(mg < 1e-9, 0.0, mg); so4 = np.where(so4 < 1e-9, 0.0, so4)
    return np.column_stack([np.ones_like(xA), mg, so4, xC, xC * mg, xA, xA * so4])


def goal_compositions(line, nq=24):
    """compositions met in the barrier (or natural) domain: f on a grid, dCa from 0 to dsat(f)"""
    F = TAB['F']; D = TAB[f'D_{line}']; out = []
    for i in range(0, len(F), 4):
        ds = TAB[f'dsat_{line}'][i]
        if ds <= 1e-6:
            continue
        for q in np.linspace(0.0, 0.95, 6):
            dd = q * ds
            la = [np.interp(dd, D, TAB[f'la_{line}'][k, i]) for k in range(4)] + [np.interp(dd, D, TAB[f'lom_{line}'][i])]
            out.append(la)
    return np.array(out).T


def span_defect(Vrows, Grows, tol=1e-8):
    """largest relative part of a goal direction outside the row space of V (0 = identifiable)"""
    sc = np.abs(np.vstack([Vrows, Grows])).max(axis=0); sc[sc == 0] = 1.0
    V = Vrows / sc; G = Grows / sc
    if len(V) == 0:
        return 1.0, 0
    u, s, vt = np.linalg.svd(V, full_matrices=False)
    rank = int((s > tol * s.max()).sum())
    B = vt[:rank]
    R = G - (G @ B.T) @ B
    return float(np.max(np.linalg.norm(R, axis=1) / np.linalg.norm(G, axis=1))), rank


# ---------------------------------------------------------------- linearized design (Fisher) at NG prior draws
def jac_fd(U, pool, h=(0.02, 0.02, 0.01, 0.02, 0.02)):
    """finite-difference Jacobians of field obs (nat) and log10 G_bar wrt the 5 transformed parameters"""
    base = run_bank('graph', U, pool)
    Jo = np.zeros((len(U), 5, 5)); Jg = np.zeros((len(U), 5))
    for k in range(5):
        Up = U.copy(); Up[:, k] += h[k]
        o = run_bank('graph', Up, pool)
        Jo[:, :, k] = (o['obs_nat'] - base['obs_nat']) / h[k]
        Jg[:, k] = (np.log10(o['G_bar']) - np.log10(base['G_bar'])) / h[k]
    return base, Jo, Jg


def lab_jac(U, la, h=1e-4):
    J = np.zeros((len(U), la.shape[1], 5))
    s0 = lab_shape_graph(U, la)
    for k in range(1, 5):
        Up = U.copy(); Up[:, k] += h
        J[:, :, k] = (lab_shape_graph(Up, la) - s0) / h
    return J                                              # column 0 (rho) stays 0: lab prefactor is unknown


PRIOR_VAR = np.array([(b - a) ** 2 / 12 for a, b in PRIOR.values()])


def post_goal_var(Jl, Jo, Jg, idx):
    """mean posterior variance of log10 G_bar for lab set idx (+ field well), linearized, lab prefactor profiled"""
    out = []
    for i in range(len(Jg)):
        H = np.diag(1 / PRIOR_VAR) + Jo[i].T @ Jo[i] / SIG_F ** 2
        if len(idx):
            A = Jl[i][idx]
            A = A - A.mean(axis=0, keepdims=True)
            H = H + A.T @ A / SIG_L ** 2
        C = np.linalg.inv(H)
        out.append(Jg[i] @ C @ Jg[i])
    return float(np.mean(out))


def logdet_shape(Jl, Jo, idx):
    out = []
    for i in range(len(Jl)):
        H = np.diag(1 / PRIOR_VAR) + Jo[i].T @ Jo[i] / SIG_F ** 2
        if len(idx):
            A = Jl[i][idx]; A = A - A.mean(axis=0, keepdims=True)
            H = H + A.T @ A / SIG_L ** 2
        out.append(np.linalg.slogdet(H)[1])
    return float(np.mean(out))


def greedy(score, n=8, maximize=False):
    idx = []
    for _ in range(n):
        best, bj = None, None
        for j in range(len(CAND)):
            if j in idx:
                continue
            v = score(idx + [j])
            if best is None or (v > best if maximize else v < best):
                best, bj = v, j
        idx.append(bj)
    return idx


def pick(back, oms, r):
    return [CAND.index((back, om, r)) for om in oms]


def main():
    t0 = time.time()
    with Pool(4) as pool:
        if os.path.exists('shkalla_bank.npz'):
            Z = dict(np.load('shkalla_bank.npz'))
        else:
            UB = draw(NB, 1); UT = draw(NT, 2)
            kk, nn = np.meshgrid(np.linspace(-6.5, -1.0, 81), np.linspace(0.5, 4.0, 36), indexing='ij')
            UTST = np.column_stack([kk.ravel(), nn.ravel()])
            B = run_bank('graph', UB, pool); T = run_bank('graph', UT, pool); Q = run_bank('tst', UTST, pool)
            Z = dict(UB=UB, UT=UT, UTST=UTST, **{f'B_{k}': v for k, v in B.items()}, **{f'T_{k}': v for k, v in T.items()},
                     **{f'Q_{k}': v for k, v in Q.items()})
            np.savez('shkalla_bank.npz', **Z)
        print(f'banks ready {time.time() - t0:.0f}s', flush=True)
        UG = draw(NG, 3)
        _, Jo, Jg = jac_fd(UG, pool)
        print(f'jacobians ready {time.time() - t0:.0f}s', flush=True)
    Jl = lab_jac(UG, LA_C)

    # ------------------------------------------------------------ designs
    D = {
        'field only': [],
        'dilute series': pick('dilute', [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95], 300.0) + [CAND.index(('dilute', 0.55, 300.0))],
        'seawater series': pick('sea', [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 0.95], 1000.0) + [CAND.index(('sea', 0.55, 1000.0))],
        'dilute + seawater': pick('dilute', [0.10, 0.40, 0.70, 0.95], 300.0) + pick('sea', [0.10, 0.40, 0.70, 0.95], 1000.0),
        'scenario waters': pick('dilute', [0.10, 0.40, 0.70], 3000.0) + pick('mix20', [0.40, 0.85], 3000.0)
                           + pick('mix20', [0.55, 0.70, 0.85], 1000.0),
    }
    D['parameter-optimal'] = greedy(lambda idx: logdet_shape(Jl, Jo, idx), maximize=True)
    D['goal-optimal'] = greedy(lambda idx: post_goal_var(Jl, Jo, Jg, idx))
    print(f'designs ready {time.time() - t0:.0f}s', flush=True)

    # ------------------------------------------------------------ algebra
    Ggoal = monomials(goal_compositions('bar'))
    Gnat = monomials(goal_compositions('nat'))
    alg = {}
    for name, idx in D.items():
        V = monomials(LA_C[:, idx]) if idx else np.zeros((0, 7))
        dg, rk = span_defect(V, Ggoal)
        dgf, rkf = span_defect(np.vstack([V, Gnat]), Ggoal)        # with the natural mixing zone as extra rows
        u0 = draw(1, 9)
        if idx:
            A = lab_jac(np.repeat(u0, 1, 0), LA_C[:, idx])[0][:, 1:]
            A = A - A.mean(axis=0, keepdims=True)
            sv = np.linalg.svd(A, compute_uv=False)
            jr = int((sv > 1e-6 * sv.max()).sum())
        else:
            jr = 0
        alg[name] = dict(rank_V=rk, defect=dg, defect_with_field=dgf, jac_rank_shape=jr,
                         lin_goal_sd=float(np.sqrt(post_goal_var(Jl, Jo, Jg, idx))),
                         points=[[CAND[j][0], float(CAND[j][1]), float(CAND[j][2])] for j in idx])
    goal_dim = span_defect(Ggoal, Ggoal)[1]

    # ------------------------------------------------------------ preposterior evaluation
    rng = np.random.default_rng(7)
    UB, UT, UTST = Z['UB'], Z['UT'], Z['UTST']
    LGb = np.log10(Z['B_G_bar']); LGt = np.log10(Z['T_G_bar']); LGq = np.log10(Z['Q_G_bar'])
    LGb_nat = np.log10(Z['B_G_nat']); LGt_nat = np.log10(Z['T_G_nat']); LGq_nat = np.log10(Z['Q_G_nat'])
    Sb = lab_shape_graph(UB, LA_C); St = lab_shape_graph(UT, LA_C); Sq = lab_shape_tst(UTST[:, 1], LA_C)
    noise_l = rng.normal(0, SIG_L, (NT, len(CAND))); noise_f = rng.normal(0, SIG_F, (NT, 5))
    lrhoL = rng.uniform(-1, 1, NT)
    dec_true = LGt > LGt_nat                                        # does the barrier dissolve more than nature?
    res = {}
    for name, idx in D.items():
        E = {'graph': [], 'tst': []}
        for t in range(NT):
            dF = Z['T_obs_nat'][t] + noise_f[t]
            out = {}
            for model, Sm, Om, LG, LGn in (('graph', Sb, Z['B_obs_nat'], LGb, LGb_nat), ('tst', Sq, Z['Q_obs_nat'], LGq, LGq_nat)):
                ll = -0.5 * ((dF[None, :] - Om) ** 2).sum(1) / SIG_F ** 2
                if idx:
                    dL = St[t, idx] + lrhoL[t] + noise_l[t, idx]
                    e = dL[None, :] - Sm[:, idx]
                    e = e - e.mean(axis=1, keepdims=True)
                    ll = ll - 0.5 * (e ** 2).sum(1) / SIG_L ** 2
                wt = np.exp(ll - ll.max()); wt /= wt.sum()
                m = float(wt @ LG); sd = float(np.sqrt(max(wt @ (LG - m) ** 2, 0)))
                o = np.argsort(LG); cw = np.cumsum(wt[o])
                lo, hi = LG[o][np.searchsorted(cw, 0.05)], LG[o][min(np.searchsorted(cw, 0.95), len(cw) - 1)]
                ess = float(1 / (wt ** 2).sum())
                pdec = float(wt @ (LG > LGn))
                E[model].append((m - LGt[t], sd, lo <= LGt[t] <= hi, ess, (pdec > 0.5) == dec_true[t]))
        out = {}
        for model in E:
            a = np.array(E[model], float)
            out[model] = dict(med_abs_err=float(np.median(np.abs(a[:, 0]))), q90_abs_err=float(np.quantile(np.abs(a[:, 0]), 0.9)),
                              bias=float(np.mean(a[:, 0])), post_sd=float(np.median(a[:, 1])), cover90=float(np.mean(a[:, 2])),
                              ess_med=float(np.median(a[:, 3])), decision=float(np.mean(a[:, 4])))
        res[name] = out
        print(name, {m: (round(out[m]['med_abs_err'], 3), round(out[m]['q90_abs_err'], 3), round(out[m]['cover90'], 2),
                         round(out[m]['ess_med'], 1)) for m in out}, flush=True)

    summ = dict(prior=PRIOR, sig_lab=SIG_L, sig_field=SIG_F, n_bank=NB, n_truth=NT, goal_dim=goal_dim,
                prior_sd_logG=float(LGt.std()), frac_bar_gt_nat=float(dec_true.mean()),
                G_bar_q=np.quantile(10 ** LGt, [0.1, 0.5, 0.9]).tolist(), G_nat_q=np.quantile(10 ** LGt_nat, [0.1, 0.5, 0.9]).tolist(),
                designs={k: dict(algebra=alg[k], **res[k]) for k in D}, mg_sea=MG_SEA, so4_sea=SO4_SEA, mg_mix=MG_MIX, so4_mix=SO4_MIX,
                ends=TAB['ends'].tolist(), lksp=float(LKSP))
    json.dump(summ, open(f'shkalla_results{"" if SIG_F == 0.005 else "_sf" + str(SIG_F)}.json', 'w'), indent=1, allow_nan=False)
    print(f'done {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
