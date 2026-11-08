"""PREJARDHJA-GO ("prejardhja" = provenance): how to meet the water demand when nobody knows where the chloride comes
from. Tests P0-P6 of Stakeholder decisions V, a state-of-the-art review (unknown chloride source).

usage: python prejardhja_exp.py            -> res/prejardhja.json (about 2 minutes)

Test bed. A utility meets a dry-season demand D from a coastal wellfield A (cheap; a wetland loses spring flow when A
pumps more than 6 hm3), an inland wellfield B in a farming area (above 4 hm3 the water is taken from irrigation), a deep
wellfield C (expensive energy) and an alternative supply X (mobile desalination or transfer, 5 hm3 at most). The
delivered blend must stay below L = 250 mg/L. Four source hypotheses reproduce today's chloride exactly but predict
different dry-season chloride for a change of pumping:
  SWI lateral seawater intrusion  - chloride at A rises with the pumping of A (and of B);
  UP  upconing of deep saline water - chloride at C rises steeply with the pumping of C;
  DRY drought (evapoconcentration, less dilution) - A and B rise whatever the pumping, the deep C is buffered;
  ANT return flow and wastewater  - chloride at B rises steeply with the pumping of B.
Four tracer tests can be bought before deciding: T1 Br/Cl, T2 water isotopes (evaporation index), T3 depth profiles
from multilevel wells, T4 nitrate and boron. All numbers are illustrative (to be calibrated for Durres).

PREJARDHJA-GO.
  C1 plausible-source set  S(y) = {k : E_k(y) < 1/beta},  E_k = mean_{j!=k} p_j(y)/p_k(y)   (e-value; no prior)
  C2 robust allocation     min social cost  s.t.  P_k(blend > L) <= alpha  for all k in S(y)   ->  risk <= alpha+beta
  C3 test choice           by the expected cost of the C2 decision under a planning prior (prior used only here)
  C4 anytime-valid monitoring: the e-values of monthly samples multiply (test martingale, Ville's inequality)
  C5 stakeholder ledger    who pays for not knowing the source; the split of the risk budget delta = alpha + beta
"""
import itertools
import json
import os
import time

import numpy as np
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'res')
T_START = time.time()

# ------------------------------------------------------------------------------------------------ the test bed
SRC = ['SWI', 'UP', 'DRY', 'ANT']
K = len(SRC)
D, L = 12.0, 250.0                                   # demand (hm3 per dry-season year), limit of the blend (mg/L)
CAP = np.array([8.0, 6.0, 5.0, 5.0])                 # A, B, C, X
Q0 = np.array([7.0, 3.0, 2.0])                       # today's pumping of A, B, C
CL_NOW = np.array([230.0, 170.0, 140.0])             # today's chloride at A, B, C (mg/L)
CL_X = 30.0
PRICE = np.array([150.0, 200.0, 400.0, 1100.0])      # kEUR per hm3 for A, B, C, X
C_UNMET = 4000.0                                     # kEUR per hm3 not delivered (rationing, tourism losses)
FARM_FREE, C_FARM = 4.0, 350.0                       # B above 4 hm3 is water taken from the farmers
WET_FREE, C_WET = 6.0, 300.0                         # A above 6 hm3 dries the wetland springs
SIG = np.array([25.0, 25.0, 20.0])                   # sd of the dry-season chloride within a source (mg/L)
DRIFT = {'SWI': [140, 25, 5], 'UP': [30, 0, 220], 'DRY': [90, 110, 15], 'ANT': [20, 200, 5]}
GAIN = {'SWI': [[35, 10, 0], [5, 8, 0], [0, 0, 2]],  # mg/L per hm3: rows = chloride at A, B, C; cols = pumping A, B, C
        'UP': [[10, 0, 4], [0, 3, 0], [0, 0, 80]],
        'DRY': [[5, 2, 0], [2, 5, 0], [0, 0, 3]],
        'ANT': [[2, 3, 0], [0, 45, 0], [0, 0, 2]]}
TESTS = ['T1', 'T2', 'T3', 'T4']
TNAME = {'T1': 'Br/Cl ratio', 'T2': 'water isotopes', 'T3': 'depth profiles', 'T4': 'nitrate and boron'}
TCOST = np.array([5.0, 15.0, 150.0, 12.0])           # kEUR per campaign
MU = np.array([[3.4, 5.2, 3.0, 1.6],                 # T1 Br/Cl (mass ratio x 1000)
               [0.3, 0.0, 2.2, 1.6],                 # T2 evaporation index (permil below the meteoric line)
               [1.2, 2.4, -0.8, -1.0],               # T3 vertical salinity gradient index (+ = saltier at depth)
               [0.1, 0.0, 0.4, 2.0]])                # T4 nitrate-boron index
SD = np.array([0.6, 0.7, 0.7, 0.6])                  # sd of one campaign (four samples averaged)
PRIOR = np.array([0.55, 0.15, 0.20, 0.10])           # planning prior (expert belief: "it is the sea")
DELTA = 0.10                                         # risk budget: P(blend > 250 mg/L in the dry season)
BETA0 = 0.05
BETAS = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]
N_SIM = 20000
RNG = np.random.default_rng(20261108)


def chloride_mean(src_mix, q, drift=None, gain=None):
    """Mean dry-season chloride at A, B, C for decisions q (n x 4); src_mix = dict source -> weight."""
    drift, gain = drift or DRIFT, gain or GAIN
    m = np.zeros((q.shape[0], 3))
    for s, w in src_mix.items():
        m += w * (CL_NOW + np.array(drift[s], float) + (q[:, :3] - Q0) @ np.array(gain[s], float).T)
    return m


def exceed_prob(src_mix, q, drift=None, gain=None):
    m = chloride_mean(src_mix, q, drift, gain)
    M = (q[:, :3] * (m - L)).sum(1) + q[:, 3] * (CL_X - L)
    sd = np.sqrt((q[:, :3] ** 2 * SIG ** 2).sum(1))
    with np.errstate(divide='ignore', invalid='ignore'):
        p = np.where(sd > 0, norm.cdf(M / np.where(sd > 0, sd, 1.0)), (M > 0).astype(float))
    return p


def blend_mean(src_mix, q):
    m = chloride_mean(src_mix, q)
    tot = q.sum(1)
    return ((q[:, :3] * m).sum(1) + q[:, 3] * CL_X) / np.where(tot > 0, tot, 1.0)


def ledger(q):
    """Social cost split by who pays: utility (supply), households (unmet demand), farmers, wetland."""
    unmet = np.maximum(0.0, D - q.sum(1))
    return dict(utility=q @ PRICE, households=C_UNMET * unmet, farmers=C_FARM * np.maximum(0.0, q[:, 1] - FARM_FREE),
                wetland=C_WET * np.maximum(0.0, q[:, 0] - WET_FREE))


def make_grid(step=0.25):
    axes = [np.arange(0.0, c + 1e-9, step) for c in CAP]
    g = np.stack([a.ravel() for a in np.meshgrid(*axes, indexing='ij')], 1)
    return g[g.sum(1) <= D + 1e-9]


Q = make_grid()
LED = ledger(Q)
COST = sum(LED.values())
SUBSETS = [tuple(k for k in range(K) if (b >> k) & 1) for b in range(1 << K)]   # index = bitmask
print(f'grid: {len(Q)} decisions', flush=True)


def best(mask):
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        raise RuntimeError('no feasible decision')
    return int(idx[np.argmin(COST[idx])])


class Geometry:
    """Exceedance probabilities, robust decisions and the Pareto front for one set of source models."""

    def __init__(self, drift, gain, delta=DELTA, betas=BETAS):
        self.drift, self.gain = drift, gain
        self.P = np.stack([exceed_prob({s: 1.0}, Q, drift, gain) for s in SRC])   # K x N
        self.delta = delta
        self.dec_set = {beta: np.array([self.for_set(SUBSETS[b], delta - beta) if b else -1 for b in range(1 << K)])
                        for beta in betas}
        self.oracle = np.array([self.for_set((k,), delta) for k in range(K)])
        self.worst = self.for_set(tuple(range(K)), delta)
        self.bayes_prior = best(PRIOR @ self.P <= delta + 1e-12)
        order = np.argsort(COST, kind='stable')
        front, FP = [], np.empty((0, K))
        for i in order:
            p = self.P[:, i]
            if FP.shape[0] and np.any(np.all(FP <= p + 1e-12, axis=1)):
                continue
            front.append(i)
            FP = np.vstack([FP, p])
        self.front = np.array(front)

    def for_set(self, members, level):
        return best(np.all(self.P[list(members)] <= level + 1e-12, axis=0)) if members else best(np.ones(len(Q), bool))

    def bayes(self, post, level=None):
        """Cheapest decision with posterior-mixture exceedance <= level, for each row of post (n x K)."""
        level = self.delta if level is None else level
        out = np.empty(post.shape[0], int)
        PF = self.P[:, self.front]
        for a in range(0, post.shape[0], 2000):
            Rm = post[a:a + 2000] @ PF <= level + 1e-12
            j = np.argmax(Rm, axis=1)
            if not Rm[np.arange(Rm.shape[0]), j].all():
                raise RuntimeError('no feasible Bayes decision')
            out[a:a + 2000] = self.front[j]
        return out


G0 = Geometry(DRIFT, GAIN)
P, DEC_SET, DEC_ORACLE, DEC_WORST, DEC_BAYES_PRIOR, FRONT = G0.P, G0.dec_set, G0.oracle, G0.worst, G0.bayes_prior, G0.front
print(f'Pareto front: {len(FRONT)} decisions ({time.time() - T_START:.0f} s)', flush=True)


def bayes_decisions(post, level=DELTA):
    return G0.bayes(post, level)


# ------------------------------------------------------------------------------------------------ tracer data
def simulate(tests, true_mu, n, sd_scale=1.0):
    """Campaign values y (n x len(tests)) when the true signature means are true_mu (len 4 vector per test)."""
    t = list(tests)
    return true_mu[t][None, :] + sd_scale * SD[t][None, :] * RNG.standard_normal((n, len(t)))


def loglik(tests, y, offset_tol=0.0, sd_scale=1.0):
    """log p_j(y) up to a common constant, n x K. With offset_tol > 0 the sup over signature offsets |o| <= tol (in
    campaign sd units); sd_scale < 1 for the mean of several campaigns."""
    t = list(tests)
    if not t:
        return np.zeros((y.shape[0], K))
    z = np.abs(y[:, :, None] - MU[t][None, :, :]) / (sd_scale * SD[t][None, :, None])
    if offset_tol:
        z = np.maximum(0.0, z - offset_tol)
    return -0.5 * (z ** 2).sum(1)


def evalue_sets(ll_num, ll_den, beta):
    """Bitmask of S(y) = {k : mean_{j!=k} p_j/p_k < 1/beta}; numerator and denominator log-likelihoods (n x K)."""
    if beta == 0:
        return np.full(ll_num.shape[0], (1 << K) - 1)
    E = np.zeros_like(ll_num)
    for k in range(K):
        others = [j for j in range(K) if j != k]
        E[:, k] = np.exp(ll_num[:, others] - ll_den[:, [k]]).mean(1)
    keep = E < 1.0 / beta
    return (keep * (1 << np.arange(K))).sum(1)


def softmax(a):
    a = a - a.max(1, keepdims=True)
    e = np.exp(a)
    return e / e.sum(1, keepdims=True)


def entropy(p):
    with np.errstate(divide='ignore', invalid='ignore'):
        return -np.where(p > 0, p * np.log2(p), 0.0).sum(-1)


def summarize(idx, true_mix, extra_cost=0.0):
    """Exact exceedance (averaged over the data) and expected cost of decisions idx under a true source mixture."""
    idx = np.atleast_1d(idx)
    p = exceed_prob(true_mix, Q[idx])
    out = dict(exceed=float(p.mean()), cost=float(COST[idx].mean() + extra_cost))
    for k_, v in LED.items():
        out[k_] = float(v[idx].mean())
    out['tests'] = float(extra_cost)
    out['unmet_hm3'] = float(np.maximum(0, D - Q[idx].sum(1)).mean())
    return out


def qdict(i):
    return dict(zip(['A', 'B', 'C', 'X'], [float(v) for v in Q[i]]))


R = dict(setup=dict(D=D, L=L, cap=CAP.tolist(), q0=Q0.tolist(), cl_now=CL_NOW.tolist(), cl_x=CL_X, price=PRICE.tolist(),
                    c_unmet=C_UNMET, farm_free=FARM_FREE, c_farm=C_FARM, wet_free=WET_FREE, c_wet=C_WET,
                    sig=SIG.tolist(), drift=DRIFT, gain=GAIN, tests=TESTS, tname=TNAME, tcost=TCOST.tolist(),
                    mu=MU.tolist(), sd=SD.tolist(), prior=PRIOR.tolist(), delta=DELTA, beta0=BETA0, n_sim=N_SIM,
                    grid=len(Q), front=len(FRONT), src=SRC))

# ------------------------------------------------------------------------------------------------ P0: acting on the wrong story
print('P0 wrong-story matrix', flush=True)
P0 = dict(dec={}, cross=[], blend=[], cost={})
for j, s in enumerate(SRC):
    i = DEC_ORACLE[j]
    P0['dec'][s] = qdict(i)
    P0['cost'][s] = float(COST[i])
P0['cross'] = [[float(P[i_true, DEC_ORACLE[j]]) for j in range(K)] for i_true in range(K)]
P0['blend'] = [[float(blend_mean({SRC[i_true]: 1.0}, Q[[DEC_ORACLE[j]]])[0]) for j in range(K)] for i_true in range(K)]
P0['today'] = dict(exceed=[float(exceed_prob({s: 1.0}, np.array([[*Q0, 0.0]]))[0]) for s in SRC],
                   blend=[float(blend_mean({s: 1.0}, np.array([[*Q0, 0.0]]))[0]) for s in SRC])
P0['worst'] = dict(dec=qdict(DEC_WORST), cost=float(COST[DEC_WORST]))
P0['bayes_prior'] = dict(dec=qdict(DEC_BAYES_PRIOR), cost=float(COST[DEC_BAYES_PRIOR]),
                         exceed=[float(P[k, DEC_BAYES_PRIOR]) for k in range(K)])
R['P0'] = P0

# ------------------------------------------------------------------------------------------------ P2: which tests to buy
print('P2 test choice', flush=True)
TSUBS = [tuple(t for t in range(4) if (b >> t) & 1) for b in range(16)]
H0 = float(entropy(PRIOR))


def run_p2(geo):
    rows_out = []
    for ti, ts in enumerate(TSUBS):
        freq = {beta: np.zeros((K, 1 << K)) for beta in BETAS}
        hpost = np.zeros(K)
        for k in range(K):
            y = simulate(ts, MU[:, k], N_SIM)
            ll = loglik(ts, y)
            hpost[k] = entropy(softmax(ll + np.log(PRIOR))).mean() if ts else H0
            for beta in BETAS:
                freq[beta][k] = np.bincount(evalue_sets(ll, ll, beta), minlength=1 << K) / N_SIM
        eig = max(0.0, H0 - float(PRIOR @ hpost))
        rows = {}
        for beta in BETAS:
            dec = geo.dec_set[beta]
            cost_k = np.array([sum(freq[beta][k, b_] * COST[dec[b_]] for b_ in range(1, 1 << K)) for k in range(K)])
            exc_k = np.array([sum(freq[beta][k, b_] * geo.P[k, dec[b_]] for b_ in range(1, 1 << K)) for k in range(K)])
            cover_k = np.array([sum(freq[beta][k, b_] for b_ in range(1, 1 << K) if (b_ >> k) & 1) for k in range(K)])
            size = float(PRIOR @ np.array([sum(freq[beta][k, b_] * bin(b_).count('1') for b_ in range(1, 1 << K))
                                           for k in range(K)]))
            rows[str(beta)] = dict(cost=float(PRIOR @ cost_k + TCOST[list(ts)].sum()), decision_cost=float(PRIOR @ cost_k),
                                   cost_k=cost_k.tolist(), exceed_k=exc_k.tolist(), cover_k=cover_k.tolist(), size=size)
        bb = min(BETAS, key=lambda b_: rows[str(b_)]['cost'])
        rows_out.append(dict(tests=[TESTS[t] for t in ts], test_cost=float(TCOST[list(ts)].sum()), eig=eig,
                             beta_best=bb, best=rows[str(bb)], by_beta=rows))
    no_test = rows_out[0]['best']['cost']
    for r in rows_out:
        r['net'] = no_test - r['best']['cost']                          # decision value net of the test cost
        r['value'] = r['net'] + r['test_cost']                         # decision value before the test cost
    budgets = sorted(set(r['test_cost'] for r in rows_out))
    curve = []
    for bgt in budgets:
        ok = [i for i, r in enumerate(rows_out) if r['test_cost'] <= bgt + 1e-9]
        i_dec = min(ok, key=lambda i: rows_out[i]['best']['cost'])
        i_inf = max(ok, key=lambda i: (round(rows_out[i]['eig'], 9), -rows_out[i]['test_cost']))
        curve.append(dict(budget=bgt, dec=rows_out[i_dec]['tests'], dec_cost=rows_out[i_dec]['best']['cost'],
                          dec_eig=rows_out[i_dec]['eig'], info=rows_out[i_inf]['tests'],
                          info_cost=rows_out[i_inf]['best']['cost'], info_eig=rows_out[i_inf]['eig']))
    eigs = np.array([r['eig'] for r in rows_out]); vals = np.array([r['value'] for r in rows_out])
    rank = lambda v: np.argsort(np.argsort(v))
    bi = int(np.argmin([r['best']['cost'] for r in rows_out]))
    single = [r for r in rows_out if len(r['tests']) == 1]
    return dict(rows=rows_out, best=rows_out[bi]['tests'], best_index=bi, beta_best=rows_out[bi]['beta_best'],
                curve=curve, h0=H0, spearman=float(np.corrcoef(rank(eigs), rank(vals))[0, 1]),
                best_single_info=max(single, key=lambda r: r['eig'])['tests'],
                best_single_dec=min(single, key=lambda r: r['best']['cost'])['tests'],
                oracle=[qdict(i) for i in geo.oracle], oracle_cost=[float(COST[i]) for i in geo.oracle],
                worst=qdict(geo.worst), worst_cost=float(COST[geo.worst]),
                gap=max(c['info_cost'] - c['dec_cost'] for c in curve))


R['P2'] = run_p2(G0)
best_ti = R['P2']['best_index']
TSTAR, BSTAR = TSUBS[best_ti], R['P2']['beta_best']
P2 = R['P2']['rows']
# variant geometry: the deep saline water rises under the coastal wellfield A (not under C)
DRIFT_A = dict(DRIFT); GAIN_A = dict(GAIN)
DRIFT_A['UP'] = [150, 5, 5]
GAIN_A['UP'] = [[45, 0, 0], [0, 3, 0], [0, 0, 2]]
G1 = Geometry(DRIFT_A, GAIN_A)
R['P2_upA'] = run_p2(G1)
R['P2_upA']['drift_up'] = DRIFT_A['UP']; R['P2_upA']['gain_up'] = GAIN_A['UP']
print(f'  best tests {R["P2"]["best"]} beta {BSTAR}; upconing under A: {R["P2_upA"]["best"]} '
      f'({time.time() - T_START:.0f} s)', flush=True)

# ------------------------------------------------------------------------------------------------ P1: policies per true source
print('P1 policies', flush=True)
ts = TSTAR
tc = float(TCOST[list(ts)].sum())
P1 = {}
for k in range(K):
    y = simulate(ts, MU[:, k], N_SIM)
    ll = loglik(ts, y)
    sm = evalue_sets(ll, ll, BSTAR)
    sm5 = evalue_sets(ll, ll, BETA0)
    post = softmax(ll + np.log(PRIOR))
    flat = softmax(ll)
    # equivalence with the flat-posterior threshold (check of Proposition 1)
    thr = BSTAR / (K - 1 + BSTAR) if BSTAR else 0.0
    sm_flat = ((flat > thr) * (1 << np.arange(K))).sum(1) if BSTAR else np.full(N_SIM, (1 << K) - 1)
    true = {SRC[k]: 1.0}
    pol = {
        'oracle': summarize(np.full(N_SIM, DEC_ORACLE[k]), true),
        'assume_swi': summarize(np.full(N_SIM, DEC_ORACLE[0]), true),
        'bayes_prior': summarize(np.full(N_SIM, DEC_BAYES_PRIOR), true),
        'worst': summarize(np.full(N_SIM, DEC_WORST), true),
        'map': summarize(DEC_ORACLE[np.argmax(post, 1)], true, tc),
        'bayes_post': summarize(bayes_decisions(post), true, tc),
        'prejardhja': summarize(DEC_SET[BSTAR][sm], true, tc),
        'prejardhja_b05': summarize(DEC_SET[BETA0][sm5], true, tc),
    }
    pol['prejardhja']['cover'] = float(((sm >> k) & 1).mean())
    pol['prejardhja']['size'] = float(np.mean([bin(b).count('1') for b in sm]))
    pol['prejardhja']['empty'] = int((sm == 0).sum())
    pol['prejardhja']['flat_equiv'] = bool(np.array_equal(sm, sm_flat))
    pol['prejardhja_b05']['cover'] = float(((sm5 >> k) & 1).mean())
    pol['map']['wrong'] = float((np.argmax(post, 1) != k).mean())
    P1[SRC[k]] = pol
prior_avg = {p: {m: float(sum(PRIOR[k] * P1[SRC[k]][p][m] for k in range(K))) for m in ('exceed', 'cost', 'utility',
             'households', 'farmers', 'wetland', 'tests', 'unmet_hm3')} for p in P1['SWI']}
R['P1'] = dict(tests=[TESTS[t] for t in ts], beta=BSTAR, alpha=DELTA - BSTAR, by_source=P1, prior_avg=prior_avg,
               max_exceed={p: max(P1[s][p]['exceed'] for s in SRC) for p in P1['SWI']})
print(f'  done ({time.time() - T_START:.0f} s)', flush=True)

# ------------------------------------------------------------------------------------------------ P3: the risk split and the ledger
print('P3 risk split and ledger', flush=True)
split = []
for beta in BETAS:
    row = P2[best_ti]['by_beta'][str(beta)]
    split.append(dict(beta=beta, alpha=DELTA - beta, cost=row['cost'], exceed_k=row['exceed_k'], cover_k=row['cover_k'],
                      size=row['size']))
led = {}
for p in ('oracle', 'prejardhja', 'worst', 'bayes_post', 'assume_swi'):
    led[p] = {m: prior_avg[p][m] for m in ('utility', 'households', 'farmers', 'wetland', 'tests', 'cost')}
R['P3'] = dict(split=split, ledger=led,
               ignorance=prior_avg['prejardhja']['cost'] - prior_avg['oracle']['cost'],
               ignorance_worst=prior_avg['worst']['cost'] - prior_avg['oracle']['cost'])

# ------------------------------------------------------------------------------------------------ P4: anytime-valid monitoring
print('P4 monitoring', flush=True)
MON_T = [0, 3]                     # monthly Br/Cl and nitrate-boron samples (one sample: sd twice a campaign)
MONTHS = 12
N_MON = 20000
beta = BETA0
P4 = dict(tests=[TESTS[t] for t in MON_T], months=MONTHS, beta=beta, by_source={})
zcrit = norm.ppf(1 - beta / (2 * len(MON_T)))
for k in range(K):
    ll = np.zeros((N_MON, K)); ssum = np.zeros((N_MON, len(MON_T)))
    ever_out = np.zeros(N_MON, bool); naive_out = np.zeros(N_MON, bool)
    stop = np.full(N_MON, MONTHS); stopped = np.zeros(N_MON, bool); stop_set = np.full(N_MON, (1 << K) - 1)
    size_t, cost_t, out_t, naive_t = [], [], [], []
    for t in range(1, MONTHS + 1):
        y = MU[MON_T, k][None, :] + 2 * SD[MON_T][None, :] * RNG.standard_normal((N_MON, len(MON_T)))
        z = (y[:, :, None] - MU[MON_T][None, :, :]) / (2 * SD[MON_T])[None, :, None]
        ll += -0.5 * (z ** 2).sum(1)
        ssum += y
        sm = evalue_sets(ll, ll, beta)
        ever_out |= ((sm >> k) & 1) == 0
        zt = np.abs(ssum / t - MU[MON_T, k][None, :]) / (2 * SD[MON_T][None, :] / np.sqrt(t))
        naive_out |= (zt > zcrit).any(1)
        new = (~stopped) & ((np.array([bin(b).count('1') for b in sm]) == 1) | (t == MONTHS))
        stop[new] = t; stop_set[new] = sm[new]; stopped |= new
        size_t.append(float(np.mean([bin(b).count('1') for b in sm])))
        out_t.append(float(ever_out.mean())); naive_t.append(float(naive_out.mean()))
        cost_t.append(float(COST[DEC_SET[beta][sm]].mean()))
    dec = DEC_SET[beta][stop_set]
    P4['by_source'][SRC[k]] = dict(ever_out=float(ever_out.mean()), naive_out=float(naive_out.mean()), size_t=size_t,
                                   out_t=out_t, naive_t=naive_t, oracle_cost=float(COST[DEC_ORACLE[k]]),
                                   cost_t=cost_t, stop_mean=float(stop.mean()),
                                   stop_exceed=float(P[k, dec].mean()), stop_cost=float(COST[dec].mean()))
R['P4'] = P4
print(f'  done ({time.time() - T_START:.0f} s)', flush=True)

# ------------------------------------------------------------------------------------------------ P5: stress tests
print('P5 stress tests', flush=True)
# mixture-aware variants: the hypotheses are the four sources and their pairwise mixtures (weights 1/4, 1/2, 3/4).
#  'endpoints': a mixture kept in S(y) asks the decision to be safe for both of its sources, which makes it safe for every
#               mixture of the two (the blend excess is linear in the weights and the spread does not depend on the source)
#  'exact'    : the decision must be safe for each kept hypothesis itself (pure or mixed)
HYP = [((k,), (1.0,)) for k in range(K)] + [((i, j), (lam, 1 - lam)) for i in range(K) for j in range(i + 1, K)
                                            for lam in (0.25, 0.5, 0.75)]
HMU = np.stack([sum(w * MU[:, k] for k, w in zip(ks, ws)) for ks, ws in HYP], 1)      # 4 tests x H
HBIT = np.array([sum(1 << k for k in ks) for ks, _ in HYP])
PH = np.stack([exceed_prob({SRC[k]: w for k, w in zip(ks, ws)}, Q) for ks, ws in HYP])   # H x N


def exact_decisions(keep, level):
    """Cheapest decision safe (<= level) for every kept hypothesis; solved once per distinct kept pattern."""
    pats, inv = np.unique(keep, axis=0, return_inverse=True)
    dec = np.array([best(np.all(PH[p] <= level + 1e-12, axis=0)) for p in pats])
    return dec[inv.ravel()], len(pats)


def mixture_sets(ts, y, beta, sd_scale=1.0):
    t = list(ts)
    z = (y[:, :, None] - HMU[t][None, :, :]) / (sd_scale * SD[t][None, :, None])
    ll = -0.5 * (z ** 2).sum(1)                                                          # n x H
    H = ll.shape[1]
    keep = np.zeros_like(ll, bool)
    for h in range(H):
        others = [g for g in range(H) if g != h]
        keep[:, h] = np.exp(ll[:, others] - ll[:, [h]]).mean(1) < 1.0 / beta
    bits = np.zeros(y.shape[0], int)
    for h in range(H):
        bits |= np.where(keep[:, h], HBIT[h], 0)
    return bits, keep


P5 = dict(mixtures={}, offset={}, mixture_aware_pure={}, mixture_exact_pure={})
MIXES = (('SWI+DRY', {'SWI': 0.5, 'DRY': 0.5}), ('DRY+ANT', {'DRY': 0.5, 'ANT': 0.5}), ('SWI+UP', {'SWI': 0.5, 'UP': 0.5}),
         ('SWI+UP 0.4', {'SWI': 0.4, 'UP': 0.6}))
for name, mix in MIXES:
    ks = [SRC.index(s_) for s_ in mix]
    mu_true = sum(w * MU[:, SRC.index(s_)] for s_, w in mix.items())
    y = simulate(TSTAR, mu_true, N_SIM)
    ll = loglik(TSTAR, y)
    sm = evalue_sets(ll, ll, BSTAR)
    post = softmax(ll + np.log(PRIOR))
    mbits, keep = mixture_sets(TSTAR, y, BSTAR)
    dex, npat = exact_decisions(keep, DELTA - BSTAR)
    P5['mixtures'][name] = dict(
        prejardhja=summarize(DEC_SET[BSTAR][sm], mix, tc), mixture_aware=summarize(DEC_SET[BSTAR][mbits], mix, tc),
        mixture_exact=summarize(dex, mix, tc), patterns=npat,
        bayes_post=summarize(bayes_decisions(post), mix, tc), map=summarize(DEC_ORACLE[np.argmax(post, 1)], mix, tc),
        worst=summarize(np.full(N_SIM, DEC_WORST), mix),
        oracle_mix=summarize(np.full(1, best(exceed_prob(mix, Q) <= DELTA + 1e-12)), mix),
        both=float(np.mean([all((b_ >> j) & 1 for j in ks) for b_ in sm])),
        one=float(np.mean([any((b_ >> j) & 1 for j in ks) for b_ in sm])),
        both_aware=float(np.mean([all((b_ >> j) & 1 for j in ks) for b_ in mbits])))
for k in range(K):                                       # what the mixture-aware variant costs when the source is pure
    y = simulate(TSTAR, MU[:, k], N_SIM)
    mbits, keep = mixture_sets(TSTAR, y, BSTAR)
    P5['mixture_aware_pure'][SRC[k]] = summarize(DEC_SET[BSTAR][mbits], {SRC[k]: 1.0}, tc)
    P5['mixture_exact_pure'][SRC[k]] = summarize(exact_decisions(keep, DELTA - BSTAR)[0], {SRC[k]: 1.0}, tc)
    P5['mixture_exact_pure'][SRC[k]]['size'] = float(keep.sum(1).mean())
for key in ('mixture_aware_pure', 'mixture_exact_pure'):
    P5[key]['prior_cost'] = float(sum(PRIOR[k] * P5[key][SRC[k]]['cost'] for k in range(K)))
P5['n_hyp'] = len(HYP)

# how much more data the mixture-aware decision needs: n campaigns averaged (sd / sqrt(n))
P5['campaigns'] = []
for n_c in (1, 4, 9, 16):
    sc = 1.0 / np.sqrt(n_c)
    row = dict(n=n_c, pure=0.0, exact=0.0, exact_size=0.0, mix_exceed_pure={}, mix_exceed_exact={})
    for k in range(K):
        y = simulate(TSTAR, MU[:, k], N_SIM, sd_scale=sc)
        ll = loglik(TSTAR, y, sd_scale=sc)
        row['pure'] += PRIOR[k] * COST[DEC_SET[BSTAR][evalue_sets(ll, ll, BSTAR)]].mean()
        _, keep = mixture_sets(TSTAR, y, BSTAR, sd_scale=sc)
        row['exact'] += PRIOR[k] * COST[exact_decisions(keep, DELTA - BSTAR)[0]].mean()
        row['exact_size'] += PRIOR[k] * keep.sum(1).mean()
    for name, mix in MIXES[2:3]:
        mu_true = sum(w * MU[:, SRC.index(s_)] for s_, w in mix.items())
        y = simulate(TSTAR, mu_true, N_SIM, sd_scale=sc)
        ll = loglik(TSTAR, y, sd_scale=sc)
        row['mix_exceed_pure'][name] = float(exceed_prob(mix, Q[DEC_SET[BSTAR][evalue_sets(ll, ll, BSTAR)]]).mean())
        _, keep = mixture_sets(TSTAR, y, BSTAR, sd_scale=sc)
        row['mix_exceed_exact'][name] = float(exceed_prob(mix, Q[exact_decisions(keep, DELTA - BSTAR)[0]]).mean())
    row['pure'] = float(row['pure'] + n_c * tc); row['exact'] = float(row['exact'] + n_c * tc)
    row['exact_size'] = float(row['exact_size'])
    P5['campaigns'].append(row)

# signature drift: every end-member mean moved by 1 sd towards the nearest other source (the hardest direction)
tst = list(TSTAR)
for tol in (0.0, 1.0):
    rows = {}
    for k in range(K):
        dist = [np.sum(((MU[tst, j] - MU[tst, k]) / SD[tst]) ** 2) if j != k else np.inf for j in range(K)]
        jn = int(np.argmin(dist))
        shift = np.zeros(4)
        dvec = (MU[tst, jn] - MU[tst, k]) / SD[tst]
        shift[tst] = np.sign(dvec) * SD[tst] * 1.0
        y = simulate(TSTAR, MU[:, k] + shift, N_SIM)
        ll_n = loglik(TSTAR, y)
        ll_d = loglik(TSTAR, y, offset_tol=tol)
        sm = evalue_sets(ll_n, ll_d, BSTAR)
        rows[SRC[k]] = dict(towards=SRC[jn], cover=float(((sm >> k) & 1).mean()),
                            size=float(np.mean([bin(b_).count('1') for b_ in sm])),
                            **summarize(DEC_SET[BSTAR][sm], {SRC[k]: 1.0}, tc))
    rows['prior_cost'] = float(sum(PRIOR[k] * rows[SRC[k]]['cost'] for k in range(K)))
    P5['offset'][str(tol)] = rows
R['P5'] = P5

# the price of safety: expected cost against the risk budget (planning prior), with and without the tests
print('P3b price of safety', flush=True)
frontier = []
for dl in (0.02, 0.05, 0.10, 0.20):
    geo = Geometry(DRIFT, GAIN, delta=dl, betas=[round(f * dl, 4) for f in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5)])
    orc = float(PRIOR @ np.array([COST[i] for i in geo.oracle]))
    y_all = [simulate(TSTAR, MU[:, k], N_SIM) for k in range(K)]
    best_c, best_b = np.inf, None
    for beta in geo.dec_set:
        c = 0.0
        for k in range(K):
            ll = loglik(TSTAR, y_all[k])
            c += PRIOR[k] * COST[geo.dec_set[beta][evalue_sets(ll, ll, beta)]].mean()
        if c + tc < best_c:
            best_c, best_b = c + tc, beta
    frontier.append(dict(delta=dl, oracle=orc, prejardhja=best_c, beta=best_b, worst=float(COST[geo.worst])))
R['P3b'] = frontier

# ------------------------------------------------------------------------------------------------ P6: guarantee on every cell
print('P6 checks', flush=True)
viol = []
for r in P2:
    for b_, row in r['by_beta'].items():
        for k in range(K):
            if row['exceed_k'][k] > DELTA + 0.004 or row['cover_k'][k] < 1 - float(b_) - 0.004:
                viol.append((r['tests'], b_, SRC[k], row['exceed_k'][k], row['cover_k'][k]))
R['P6'] = dict(cells=len(P2) * len(BETAS) * K, violations=viol,
               min_cover=min(min(row['cover_k'][k] - (1 - float(b_)) for k in range(K))
                             for r in P2 for b_, row in r['by_beta'].items()),
               max_exceed=max(max(row['exceed_k']) for r in P2 for row in r['by_beta'].values()))
R['runtime_s'] = time.time() - T_START
os.makedirs(RES, exist_ok=True)
with open(os.path.join(RES, 'prejardhja.json'), 'w') as fh:
    json.dump(R, fh, indent=1)
print(f'saved res/prejardhja.json ({R["runtime_s"]:.0f} s)')
