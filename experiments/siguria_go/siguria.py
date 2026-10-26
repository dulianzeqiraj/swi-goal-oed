"""SIGURIA-GO: an uncertainty, risk, robustness and uniqueness certificate for a managed-aquifer-recharge
(MAR) scheme at Fushe-Kuqe, on the model and truth generator of VENDI-GO (../vendi_go/vendi.py).

For a fixed aquifer the heads at the supply wells are affine in the recharge rates, and the delivered
rate of a well is min(q, c) with c its unknown injectivity. Hence (Proposition S1) the head deficit
D(q) = max_w (h_c - H_w(q)) is convex in the rates q, the CVaR of D is convex, and the
minimum-recharge scheme under a CVaR constraint is a linear programme over scenarios. The certificate:
  U  uncertainty: the risk of the scheme is itself uncertain (it depends on the unknown aquifer):
     distribution over aquifers of the climate-conditional intrusion probability;
  R  risk: P(A or B intruded), CVaR_0.05 of the deficit, the minimum-recharge CVaR scheme (LP);
  B  robustness: (i) a finite-sample, distribution-free scenario certificate (Campi-Garatti sampling and
     discarding, d = 3 rates) checked on 20 000 fresh scenarios; (ii) the Wasserstein robustness radius
     rho* = alpha * (-CVaR_alpha(D)) in metres of head (Proposition S3): every distribution of the two
     supply-well heads within W1 distance rho* (sup-norm) keeps CVaR_alpha(D) <= 0; compared with the
     distributional error of ignoring the sub-zonal field (coupling bound); (iii) a moment-robust bound;
  N  uniqueness: (i) of the optimal rates: range of every rate over the optimal face of the LP;
     (ii) of the optimal siting: exhaustive search over all 380 364 lattice triples, the near-optimal
     (Rashomon) set, a simultaneous confidence set for the best design, discrete deflation (the best
     designs that share no well within 2 km), and the probability that the design optimal for the
     prior is optimal for the true aquifer.
Run: python3 siguria.py ensemble ; python3 siguria.py analyse
"""
import os, sys, json, time
import numpy as np
from scipy.special import ndtr
from scipy.stats import norm, beta as betad
from scipy.optimize import linprog
import scipy.sparse as sp
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'vendi_go'))
import vendi as V

OUT = os.path.join(HERE, 'res')
ALPHA = 0.05          # CVaR tail
QMAX = 20000.0        # m3/d, pump limit of one MAR well in the rate LP
BETA = 1e-6           # confidence parameter of the scenario certificate
N_SEARCH, N_LP, N_VAL = 4000, 4000, 20000
if os.environ.get('SIG_SMALL'):                       # smoke test
    N_SEARCH, N_LP, N_VAL = 120, 120, 300
    OUT = os.path.join(HERE, 'res_small')
DEFL_KM = 2.0


# ------------------------------------------------------------------ scenario ensembles
def member(args):
    seed, model = args
    rng = np.random.default_rng(seed)
    th = V.LG @ rng.standard_normal(V.NZ)                    # theta, eta, xi first: the 'model' and 'truth'
    eta = V.SIG_ETA * rng.standard_normal(V.K)               # members with the same seed share them, and the
    xi = V.SIG_XI * rng.standard_normal()                    # truth adds the sub-zonal field zeta
    ze = V.draw_zeta(rng) if model == 'truth' else None
    hn, u = V.fields(th, ze)
    cs = V.SITE
    lT = np.log(V.m.K0c[cs] * V.BTH) + th[V.m.zone[cs]] + (ze[cs] if ze is not None else 0.0)
    c = V.QD * np.exp(lT) / V.TREF * np.exp(eta)
    dA = V.QA * u[V.cA, 0] + V.QB * u[V.cB, 0]
    dB = V.QA * u[V.cB, 0] + V.QB * u[V.cB, 1]
    return (np.array([hn[V.cA], hn[V.cB], dA, dB, xi]), u[cs, 0].astype(np.float32),
            u[cs, 1].astype(np.float32), c.astype(np.float32))


def ensemble(name, n, seed0, model='truth'):
    with Pool(4, initializer=V.init_worker) as pool:
        R = pool.map(member, [(seed0 + s, model) for s in range(n)], chunksize=50)
    np.savez(os.path.join(OUT, f'ens_{name}.npz'), S=np.array([r[0] for r in R]), gA=np.array([r[1] for r in R]),
             gB=np.array([r[2] for r in R]), c=np.array([r[3] for r in R]))


def load(name):
    d = np.load(os.path.join(OUT, f'ens_{name}.npz'))
    return {k: d[k] for k in d.files}


# ------------------------------------------------------------------ risk of designs
def cond_risk(E, cells_q):
    """climate-conditional P(A or B intruded) for every aquifer: cells_q = (site indices, rates)."""
    sites, q = cells_q
    S = E['S']; d = np.minimum(q[None, :], E['c'][:, sites])
    rA = (d * E['gA'][:, sites]).sum(1); rB = (d * E['gB'][:, sites]).sum(1)
    tA = (V.HC - (S[:, 0] - S[:, 2] + rA)) / S[:, 0]; tB = (V.HC - (S[:, 1] - S[:, 3] + rB)) / S[:, 1]
    return ndtr(np.maximum(tA, tB) / V.SIG_XI)


def deficit(E, sites, q, with_xi=True):
    """head deficit D = max_w (h_c - H_w) per scenario (climate sample xi of the scenario)."""
    S = E['S']; d = np.minimum(q[None, :], E['c'][:, sites])
    xi = S[:, 4] if with_xi else 0.0
    HA = (1 + xi) * S[:, 0] - S[:, 2] + (d * E['gA'][:, sites]).sum(1)
    HB = (1 + xi) * S[:, 1] - S[:, 3] + (d * E['gB'][:, sites]).sum(1)
    return np.maximum(V.HC - HA, V.HC - HB), HA, HB


def cvar(x, a=ALPHA):
    """CVaR_a of a loss sample (mean of the worst a-fraction, Rockafellar-Uryasev)."""
    x = np.sort(x)[::-1]; n = len(x); k = a * n; m = int(np.floor(k))
    return (x[:m].sum() + (k - m) * (x[m] if m < n else 0.0)) / k


def search(E, Q=V.QD, chunk=4000):
    """exhaustive search over all lattice triples: mean risk over aquifers and, for every aquifer,
    its own optimal triple (what one would build knowing the aquifer)."""
    tp = V.triples(); S = E['S']; n = len(S)
    dq = np.minimum(Q, E['c']).astype(np.float32)
    cA = (dq * E['gA']).astype(np.float32); cB = (dq * E['gB']).astype(np.float32)
    baseA = (S[:, 0] - S[:, 2]).astype(np.float32); baseB = (S[:, 1] - S[:, 3]).astype(np.float32)
    iA = (1 / S[:, 0]).astype(np.float32); iB = (1 / S[:, 1]).astype(np.float32)
    mean = np.empty(len(tp)); best_r = np.full(n, np.inf); best_d = np.zeros(n, int)
    for s in range(0, len(tp), chunk):
        t = tp[s:s + chunk]
        rA = cA[:, t[:, 0]] + cA[:, t[:, 1]] + cA[:, t[:, 2]]
        rB = cB[:, t[:, 0]] + cB[:, t[:, 1]] + cB[:, t[:, 2]]
        z = np.maximum((V.HC - baseA[:, None] - rA) * iA[:, None], (V.HC - baseB[:, None] - rB) * iB[:, None])
        r = ndtr(z / V.SIG_XI)
        mean[s:s + chunk] = r.mean(0)
        j = np.argmin(r, 1); rb = r[np.arange(n), j]
        upd = rb < best_r; best_r[upd] = rb[upd]; best_d[upd] = s + j[upd]
    return mean, best_d, best_r


# ------------------------------------------------------------------ rates: CVaR LP and scenario programme
def rate_lp(E, sites, mode='cvar', keep=None, budget=None):
    """'cvar': minimum total recharge sum q s.t. CVaR_alpha(D) <= 0; 'robust': minimum total recharge s.t.
    D_i <= 0 for every kept scenario; 'cvarmin': minimum CVaR_alpha(D) s.t. sum q <= budget. Delivered rates
    d_ik <= q_k, d_ik <= c_ik. Returns the LP result and the LP data."""
    S = E['S']; n = len(S) if keep is None else len(keep)
    idx = np.arange(len(S)) if keep is None else keep
    m = len(sites)
    gA = E['gA'][idx][:, sites].astype(float); gB = E['gB'][idx][:, sites].astype(float)
    cc = E['c'][idx][:, sites].astype(float)
    HA0 = (1 + S[idx, 4]) * S[idx, 0] - S[idx, 2]; HB0 = (1 + S[idx, 4]) * S[idx, 1] - S[idx, 3]
    # variables: q (m), d (n*m), [t, u (n)] for cvar
    nq, nd = m, n * m
    cv_ = mode in ('cvar', 'cvarmin')
    nv = nq + nd + ((1 + n) if cv_ else 0)
    rows, cols, vals, b = [], [], [], []
    r = 0
    # deficit rows: h_c - H0_w - sum_k g_wk d_k (- t - u_i) <= 0
    for (g, H0) in ((gA, HA0), (gB, HB0)):
        for i in range(n):
            for k in range(m):
                rows.append(r); cols.append(nq + i * m + k); vals.append(-g[i, k])
            if cv_:
                rows += [r, r]; cols += [nq + nd, nq + nd + 1 + i]; vals += [-1.0, -1.0]
            b.append(H0[i] - V.HC); r += 1
    # d_ik - q_k <= 0
    for i in range(n):
        for k in range(m):
            rows += [r, r]; cols += [nq + i * m + k, k]; vals += [1.0, -1.0]; b.append(0.0); r += 1
    if mode == 'cvar':                                       # t + sum u / (alpha n) <= 0
        rows.append(r); cols.append(nq + nd); vals.append(1.0)
        for i in range(n):
            rows.append(r); cols.append(nq + nd + 1 + i); vals.append(1.0 / (ALPHA * n))
        b.append(0.0); r += 1
    if mode == 'cvarmin':                                    # sum q <= budget
        for k in range(m):
            rows.append(r); cols.append(k); vals.append(1.0)
        b.append(budget); r += 1
    A = sp.csr_matrix((vals, (rows, cols)), shape=(r, nv))
    bounds = [(0, QMAX)] * nq + [(0, float(c)) for c in cc.ravel()]
    if cv_:
        bounds += [(None, None)] + [(0, None)] * n
    cost = np.zeros(nv)
    if mode == 'cvarmin':
        cost[nq + nd] = 1.0; cost[nq + nd + 1:] = 1.0 / (ALPHA * n)
    else:
        cost[:nq] = 1.0
    res = linprog(cost, A_ub=A, b_ub=np.array(b), bounds=bounds, method='highs')
    return res, (cost, A, np.array(b), bounds)


def face_ranges(res, lp, m, tol=1e-7):
    """range of every rate over the optimal face: min / max q_k s.t. feasibility and cost <= opt(1 + tol)."""
    cost, A, b, bounds = lp
    A2 = sp.vstack([A, sp.csr_matrix(cost[None, :])]); b2 = np.r_[b, res.fun + tol * max(1.0, abs(res.fun))]
    out = []
    for k in range(m):
        e = np.zeros(len(cost)); e[k] = 1.0
        lo = linprog(e, A_ub=A2, b_ub=b2, bounds=bounds, method='highs').fun
        hi = -linprog(-e, A_ub=A2, b_ub=b2, bounds=bounds, method='highs').fun
        out.append((float(lo), float(hi)))
    return out


def cg_epsilon(N, r, d, beta=BETA):
    """Campi-Garatti (2011) sampling-and-discarding: the smallest eps with
    C(r+d-1, r) * sum_{i<r+d} C(N, i) eps^i (1-eps)^(N-i) <= beta."""
    from scipy.special import gammaln
    logc = gammaln(r + d) - gammaln(r + 1) - gammaln(d)
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        val = logc + np.log(max(betad.cdf(1 - mid, N - (r + d - 1), r + d), 1e-300))   # binomial tail via beta cdf
        lo, hi = (mid, hi) if val > np.log(beta) else (lo, mid)
    return hi


# ------------------------------------------------------------------ analysis
def designs_near(tp, j, km=DEFL_KM):
    """indices of triples sharing at least one well within km of a well of triple j."""
    xy = np.c_[V.m.cx[V.SITE], V.m.cy[V.SITE]]
    P = xy[tp[j]]
    D = np.min([np.hypot(xy[tp][:, a, 0][:, None] - P[None, :, 0], xy[tp][:, a, 1][:, None] - P[None, :, 1]).min(1)
                for a in range(3)], axis=0)
    return D < km


def analyse():
    t0 = time.time(); V.load_setup(); V.zeta_chol()
    Es, El, Ev, Em = load('search'), load('lp'), load('val'), load('model')
    tp = V.triples(); out = {}
    # ---- uniqueness of the siting: exhaustive search on the search ensemble, model ensemble for comparison
    mean_s, best_d, best_r = search(Es)
    mean_m, _, _ = search(Em)
    order = np.argsort(mean_s); jbest = int(order[0])
    print(f'exhaustive search over {len(tp)} triples ({time.time() - t0:.0f} s): best {V.SITE[tp[jbest]].tolist()} risk {mean_s[jbest]:.4f}')
    prag = np.array(V.prag_sites(V.Belief()))
    jprag = int(np.flatnonzero((np.sort(tp, 1) == np.sort(prag)).all(1))[0])
    jmodel = int(np.argmin(mean_m))
    # Rashomon set and deflation
    rash = {f'{d:g}': int((mean_s <= mean_s[jbest] + d).sum()) for d in (0.0025, 0.005, 0.01, 0.02)}
    defl, mask = [], np.zeros(len(tp), bool)
    for _ in range(5):
        cand = np.where(mask, np.inf, mean_s); j = int(np.argmin(cand))
        defl.append(j); mask |= designs_near(tp, j)
    # simultaneous confidence set for the best (top 300 by search risk, evaluated on the validation set)
    top = order[:300]
    Rv = np.array([cond_risk(Ev, (tp[j], np.full(3, V.QD))) for j in top])      # (300, Nval)
    zc = norm.ppf(1 - 0.05 / (len(top) - 1)); nv = Rv.shape[1]
    beaten = np.zeros(len(top), bool)                         # i is dropped if some j is significantly better
    for j in range(len(top)):
        dif = Rv - Rv[j]; md = dif.mean(1); se = dif.std(1, ddof=1) / np.sqrt(nv) + 1e-15
        beaten |= (md / se > zc)
    conf = [int(top[i]) for i in range(len(top)) if not beaten[i]]
    # probability of optimality across aquifers
    p_same = float(np.mean(best_d == jbest))
    near_best = designs_near(tp, jbest)
    def close_all(j, k, km=DEFL_KM):                       # every well of k within km of a well of j
        xy = np.c_[V.m.cx[V.SITE], V.m.cy[V.SITE]]
        P, Q_ = xy[tp[j]], xy[tp[k]]
        return bool(np.all(np.hypot(Q_[:, None, 0] - P[None, :, 0], Q_[:, None, 1] - P[None, :, 1]).min(1) < km))
    p_close = float(np.mean([close_all(jbest, k) for k in best_d]))
    vals, cnt = np.unique(best_d, return_counts=True); pr = cnt / cnt.sum()
    out['uniqueness_siting'] = dict(
        best=V.SITE[tp[jbest]].tolist(), best_xy=[[float(V.m.cx[c]), float(V.m.cy[c])] for c in V.SITE[tp[jbest]]],
        risk_best_search=float(mean_s[jbest]), second=float(mean_s[order[1]]), rashomon=rash,
        deflation=[dict(sites=V.SITE[tp[j]].tolist(), xy=[[float(V.m.cx[c]), float(V.m.cy[c])] for c in V.SITE[tp[j]]],
                        risk=float(mean_s[j])) for j in defl],
        conf_set_size=len(conf), conf_set_risk_range=[float(mean_s[conf].min()), float(mean_s[conf].max())],
        conf_set_wells=sorted(set(int(V.SITE[s]) for j in conf for s in tp[j])),
        p_oracle_equals_best=p_same, p_oracle_close_best=p_close, n_distinct_oracle=int(len(vals)),
        entropy_bits=float(-(pr * np.log2(pr)).sum()), top_oracle_freq=float(pr.max()),
        prag=dict(sites=V.SITE[prag].tolist(), risk_search=float(mean_s[jprag]), rank=int((mean_s < mean_s[jprag]).sum()) + 1),
        model_best=dict(sites=V.SITE[tp[jmodel]].tolist(), risk_model=float(mean_m[jmodel]), risk_truth=float(mean_s[jmodel]),
                        rank_truth=int((mean_s < mean_s[jmodel]).sum()) + 1))
    print(json.dumps(out['uniqueness_siting'], indent=1))
    # ---- certificates for three schemes
    schemes = {'best': tp[jbest], 'prag': tp[jprag], 'model_best': tp[jmodel]}
    for nm, sites in schemes.items():
        q = np.full(3, V.QD)
        r_aq = cond_risk(Ev, (sites, q))                    # U: risk over aquifers (climate integrated)
        D, HA, HB = deficit(Ev, sites, q)
        Dm, _, _ = deficit(Em, sites, q)                    # 12-zone model ensemble (misspecified)
        # coupling bound on W1 between model and truth heads: same theta, xi, eta, the truth adds zeta
        cv = cvar(D); rho = ALPHA * max(0.0, -cv); cv10 = cvar(D, 0.10); rho10 = 0.10 * max(0.0, -cv10)
        mu = np.array([HA.mean(), HB.mean()]); sd = np.array([HA.std(), HB.std()])
        cant = float(min(1.0, sum(s ** 2 / (s ** 2 + (m_ - V.HC) ** 2) if m_ > V.HC else 1.0 for m_, s in zip(mu, sd))))
        out[nm] = dict(sites=V.SITE[sites].tolist(), fixed_rate=V.QD,
                       risk=float(np.mean(D > 0)), risk_se=float(np.std(D > 0) / np.sqrt(len(D))),
                       risk_climate_integrated=float(r_aq.mean()),
                       risk_over_aquifers=dict(q50=float(np.quantile(r_aq, .5)), q90=float(np.quantile(r_aq, .9)),
                                               q99=float(np.quantile(r_aq, .99)), p_above_10pct=float(np.mean(r_aq > 0.1))),
                       cvar=float(cv), rho_star_m=float(rho), cvar10=float(cv10), rho10_m=float(rho10), cantelli=cant,
                       gaussian=float(1 - V.bvnu(-(mu[0] - V.HC) / sd[0], -(mu[1] - V.HC) / sd[1], np.corrcoef(HA, HB)[0, 1])),
                       risk_model_ensemble=float(np.mean(Dm > 0)), cvar_model=float(cvar(Dm)))
        print(nm, json.dumps(out[nm]))
    # coupling distance between the 12-zone model and the truth for the best scheme: paired draws
    Pm, Pt = Em, Es                                          # paired: same theta, eta, xi; truth adds zeta
    sites = schemes['best']; q = np.full(3, V.QD)
    _, HAm, HBm = deficit(Pm, sites, q); _, HAt, HBt = deficit(Pt, sites, q)
    w1 = float(np.mean(np.maximum(np.abs(HAm - HAt), np.abs(HBm - HBt))))
    Dt, _, _ = deficit(Pt, sites, q); Dm_, _, _ = deficit(Pm, sites, q)
    out['misspecification'] = dict(w1_coupling_bound_m=w1, cvar_model=float(cvar(Dm_)), cvar_truth=float(cvar(Dt)),
                                   rho_star_model=float(ALPHA * max(0, -cvar(Dm_))),
                                   risk_model=float(np.mean(Dm_ > 0)), risk_truth=float(np.mean(Dt > 0)))
    print('misspecification', out['misspecification'])
    # ---- rates: CVaR LP and scenario programme for the best siting
    sites = schemes['best']
    out['cvar_split'] = cvar_split(El, Ev, sites)
    print('cvar split', out['cvar_split'])
    Dmax, _, _ = deficit(El, sites, np.full(3, QMAX))
    keep = np.flatnonzero(Dmax <= 0); r_disc = len(El['S']) - len(keep)
    Dmv, _, _ = deficit(Ev, sites, np.full(3, QMAX))
    out['unfixable'] = dict(lp=float(1 - len(keep) / len(El['S'])), val=float(np.mean(Dmv > 0)), qmax=QMAX)
    res2, lp2 = rate_lp(El, sites, 'robust', keep)
    qr = res2.x[:3]; Dv2, _, _ = deficit(Ev, sites, qr)
    eps = cg_epsilon(len(El['S']), r_disc, 3)
    fr2 = face_ranges(res2, lp2, 3)
    out['scenario'] = dict(q=qr.tolist(), total=float(qr.sum()), discarded=int(r_disc), N=int(len(El['S'])), d=3, beta=BETA,
                           eps_certificate=float(eps), val_violation=float(np.mean(Dv2 > 0)),
                           val_violation_se=float(np.std(Dv2 > 0) / np.sqrt(len(Dv2))), face_ranges=fr2)
    print('scenario', out['scenario'])
    # ---- after the pilot tests: the schemes VENDI-GO builds for prior truths 0..N_AT-1, certified under its posterior
    with Pool(4, initializer=V.init_worker) as pool:
        AG = pool.map(after_light, range(N_AT), chunksize=1)
    pr = np.array([a['risk_climate_integrated'] for a in AG]); trv = np.array([a['truth_risk_fixed_rate'] for a in AG])
    rho = np.array([a['rho_star_m'] for a in AG]); eps = np.array([a['scenario']['eps'] for a in AG])
    rho10 = np.array([a['rho10_m'] for a in AG])
    sct = np.array([a['scenario']['truth_risk'] for a in AG])
    out['after_tests_all'] = dict(n=len(AG), truths=list(range(N_AT)), frac_certified=float(np.mean(rho > 0)),
                                  frac_certified10=float(np.mean(rho10 > 0)), rho10_median_certified=float(np.median(rho10[rho10 > 0])) if np.any(rho10 > 0) else 0.0,
                                  frac_post_below_5pct=float(np.mean(pr < 0.05)), frac_post_below_10pct=float(np.mean(pr < 0.10)),
                                  post_risk_mean=float(pr.mean()), truth_risk_mean=float(trv.mean()),
                                  prior_risk_same_mean=float(np.mean([a['prior_risk_same_scheme'] for a in AG])),
                                  rho_median_certified=float(np.median(rho[rho > 0])) if np.any(rho > 0) else 0.0,
                                  eps_median=float(np.median(eps)), eps_q90=float(np.quantile(eps, .9)),
                                  scen_truth_le_eps=float(np.mean(sct <= eps)), unfixable_median=float(np.median([a['unfixable'] for a in AG])),
                                  rows=[dict(truth=a['truth'], post=a['risk_climate_integrated'], truth_risk=a['truth_risk_fixed_rate'],
                                             rho=a['rho_star_m'], rho10=a['rho10_m'], eps=a['scenario']['eps'], scen_truth=a['scenario']['truth_risk'],
                                             unfixable=a['unfixable'], tests=len(a['tested'])) for a in AG])
    print('after tests, all', json.dumps({k: v for k, v in out['after_tests_all'].items() if k != 'rows'}))
    tex = int(np.argsort(pr)[len(pr) // 2])                 # the typical case: median posterior risk
    out['after_tests'] = after_tests(tex)
    print('after tests, typical case', json.dumps(out['after_tests']))
    json.dump(out, open(os.path.join(OUT, 'siguria.json'), 'w'), indent=1)
    np.savez(os.path.join(OUT, 'siguria_fig.npz'), r_prior=POST['r_prior'],
             r_post=POST['r'], truth_risk=POST['truth'], best_d=best_d, mean_s=mean_s[order[:2000]], order=order[:2000],
             conf=np.array(conf), defl=np.array(defl), jbest=jbest)
    print(f'done {time.time() - t0:.0f} s')


BUDGET = 3 * 5000.0


def cvar_split(El, Ev, sites, truth=None, full=True):
    """the split of a recharge budget among the three wells that minimises CVaR_alpha of the deficit, its
    validation, and the range of each rate over the optimal face (uniqueness)."""
    res, lp = rate_lp(El, sites, 'cvarmin', budget=BUDGET)
    q = res.x[:len(sites)]; Dv, _, _ = deficit(Ev, sites, q)
    Deq, _, _ = deficit(Ev, sites, np.full(len(sites), BUDGET / len(sites)))
    out = dict(budget=BUDGET, q=q.tolist(), status=int(res.status), cvar_lp=float(res.fun), val_cvar=float(cvar(Dv)),
               val_risk=float(np.mean(Dv > 0)), equal_split_cvar=float(cvar(Deq)), equal_split_risk=float(np.mean(Deq > 0)),
               face_ranges=face_ranges(res, lp, len(sites)) if full else None)
    if truth is not None:
        tr, cells = truth
        out['truth_risk'] = float(V.truth_risk(tr, cells, np.minimum(q, tr['c'][cells])))
    return out


POST = {}
N_AT = 24 if not os.environ.get('SIG_SMALL') else 4


def after_light(tex):
    return after_tests(tex, full=False)
def posterior_ensemble(B, T, cmeas, n, seed):
    """scenarios of the supply-well quantities, sensitivities and injectivities drawn from the (linearised Gaussian)
    belief of VENDI-GO; tested sites keep their measured injectivity."""
    rng = np.random.default_rng(seed)
    L = np.linalg.cholesky(B.P + 1e-10 * np.eye(V.DZ))
    Z = B.mz[None, :] + rng.standard_normal((n, V.DZ)) @ L.T
    Y = B.f0[None, :] + (Z[:, :V.NZ] - B.mz[:V.NZ]) @ B.F.T + Z[:, V.NZ:V.NZ + V.NY]
    k = np.arange(V.K)
    hnA, hnB = V.RCH * np.exp(Y[:, V.PHA]), V.RCH * np.exp(Y[:, V.PHB])
    uAA, uAB, uBB = np.exp(Y[:, V.GA(V.JA)]), np.exp(Y[:, V.GA(V.JB)]), np.exp(Y[:, V.GB(V.JB)])
    c = np.exp(V.LOGC0[None, :] + Z[:, V.ZS] + Z[:, V.ZETA0 + k] + V.SIG_ETA * rng.standard_normal((n, V.K)))
    for s, cm in zip(T, cmeas):
        c[:, s] = cm
    xi = V.SIG_XI * rng.standard_normal(n)
    S = np.c_[hnA, hnB, V.QA * uAA + V.QB * uAB, V.QA * uAB + V.QB * uBB, xi]
    return dict(S=S, gA=np.exp(Y[:, V.GA(k)]).astype(np.float32), gB=np.exp(Y[:, V.GB(k)]).astype(np.float32), c=c.astype(np.float32))


def after_tests(tex, prior_best=None, full=True):
    tr = V.make_truth(tex); cap = {}
    orig = V.finish
    def fin(tr_, B, T, qT, name, extra=None):
        cap.update(B=B, T=list(T)); return orig(tr_, B, T, qT, name, extra)
    V.finish = fin
    res = V.vendi(tr)
    V.finish = orig
    B, T = cap['B'], cap['T']
    cmeas = [float(np.exp(np.log(tr['c'][V.SITE[s]]) + V.SIG_C * tr['n_c'][V.SITE[s]])) for s in T]
    sites = np.array(res['sites'])
    Ep = posterior_ensemble(B, T, cmeas, N_VAL, 123)
    El_ = posterior_ensemble(B, T, cmeas, N_LP, 456)
    q = np.full(len(sites), V.QD)
    r_aq = cond_risk(Ep, (sites, q)); D, _, _ = deficit(Ep, sites, q)
    cv = cvar(D); cv10 = cvar(D, 0.10)
    truth = float(V.truth_risk(tr, V.SITE[sites], np.minimum(q, tr['c'][V.SITE[sites]])))
    # minimum-recharge scheme under the posterior: scenario programme, certificate and its truth risk
    Dmax, _, _ = deficit(El_, sites, np.full(len(sites), QMAX))
    keep = np.flatnonzero(Dmax <= 0)
    res2, lp2 = rate_lp(El_, sites, 'robust', keep)
    qr = res2.x[:len(sites)]
    eps = cg_epsilon(N_LP, N_LP - len(keep), len(sites))
    Dv, _, _ = deficit(Ep, sites, qr)
    truth_r = float(V.truth_risk(tr, V.SITE[sites], np.minimum(qr, tr['c'][V.SITE[sites]])))
    split = cvar_split(El_, Ep, sites, truth=(tr, V.SITE[sites]), full=full)
    Dmv, _, _ = deficit(Ep, sites, np.full(len(sites), QMAX))
    # prior certificate of the same scheme for comparison
    Ev = load('val')
    r_pr = cond_risk(Ev, (sites, q))
    if full:
        POST.update(r=r_aq, truth=truth, r_prior=r_pr)
    return dict(truth=tex, tested=[int(V.SITE[s]) for s in T], sites=V.SITE[sites].tolist(), vendi_post_risk=res['post_risk'],
                risk=float(np.mean(D > 0)), risk_climate_integrated=float(r_aq.mean()),
                risk_over_aquifers=dict(q50=float(np.quantile(r_aq, .5)), q90=float(np.quantile(r_aq, .9)), q99=float(np.quantile(r_aq, .99))),
                cvar=float(cv), rho_star_m=float(ALPHA * max(0.0, -cv)), cvar10=float(cv10), rho10_m=float(0.10 * max(0.0, -cv10)),
                truth_risk_fixed_rate=truth,
                prior_risk_same_scheme=float(r_pr.mean()), prior_q90_same_scheme=float(np.quantile(r_pr, .9)),
                cvar_split=split, unfixable=float(np.mean(Dmv > 0)),
                scenario=dict(q=qr.tolist(), total=float(qr.sum()), discarded=int(N_LP - len(keep)), eps=float(eps),
                              post_violation=float(np.mean(Dv > 0)), truth_risk=truth_r,
                              face_ranges=face_ranges(res2, lp2, len(sites)) if full else None))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'analyse'
    os.makedirs(OUT, exist_ok=True)
    if cmd == 'ensemble':
        V.load_setup(); V.zeta_chol(); t0 = time.time()
        ensemble('search', N_SEARCH, 7_000_000); ensemble('lp', N_LP, 8_000_000)
        ensemble('val', N_VAL, 9_000_000); ensemble('model', N_SEARCH, 7_000_000, 'model')
        print(f'ensembles done {time.time() - t0:.0f} s')
    else:
        analyse()
