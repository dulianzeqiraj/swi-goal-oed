"""BURIMI-GO (burimi: the source). Innovation of review 49 (causal generative modelling with very high mathematics).

The seven major ions of a coastal well (Cl, Na, K, Ca, Mg, SO4, HCO3, in meq/L) are modelled as a linear mixture of
three latent hydrochemical processes linked by a linear structural causal model, in the causal order
    s  seawater fraction (pumping-driven intrusion)          source
    W  carbonate weathering (calcite, dolomite)               W <- s (ionic-strength enhanced dissolution)
    X  reverse cation exchange in clays (Na in, Ca/Mg out)    X <- s, W
    x = x_fresh + G z + e,   z = (s, W, X),   z = A z + Omega^{1/2} eps,   e ~ N(0, diag(tau^2)).
The columns of G are the stoichiometric signatures of the processes. Regimes act as interventions: a pumping regime
changes the law of s, an irrigation/recharge regime decouples W from s (perfect intervention on W), and a clay
facies decouples X (perfect intervention on X).

Part A (identifiability): the dimension of the set of parameters that reproduce every observed covariance (the
fibre), by the rank of the Jacobian of the parameter-to-covariance map, for designs that combine known stoichiometric
columns and regimes; and whether three queries are identified on that set: (Q1) the chemistry of a sampled well if
its seawater fraction were halved, (Q2) the chemistry of a sampled well without cation exchange, do(X = 0),
(Q3) the covariance of the chemistry under an unobserved pumping regime (variance of s tripled).
Part B (estimation): maximum-likelihood fits to simulated well chemistry with measurement noise, several restarts per
data set; the error of the counterfactual chemistry against the truth and its spread over equally good fits.
Writes burimi_results.json and burimi.log.
"""
import json
import os
import time

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')          # one thread per process: the four workers run in parallel

import autograd.numpy as anp
import numpy as np
from autograd import grad, jacobian
from multiprocessing import Pool

from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
IONS = ['Cl', 'Na', 'K', 'Ca', 'Mg', 'SO4', 'HCO3']
NAMES = ['seawater', 'weathering', 'exchange']
d, n = 7, 3
# stoichiometric signatures, meq/L per unit of process (columns): seawater minus fresh water per unit fraction;
# calcite + some dolomite per meq/L dissolved; reverse exchange per meq/L of Na taken up by the clays
S = np.array([[565.0, 480.0, 10.0, 20.0, 108.0, 58.0, -2.0],
              [0.0, 0.0, 0.0, 1.0, 0.2, 0.0, 1.2],
              [0.0, -1.0, -0.05, 0.6, 0.45, 0.0, 0.0]]).T
X_FRESH = np.array([1.0, 1.2, 0.05, 3.0, 1.0, 0.5, 4.4])
TRUE = dict(sd=np.array([0.01, 0.8, 0.5]),                  # noise sd of s (fraction), W and X (meq/L)
            A=np.array([[0, 0, 0], [20.0, 0, 0], [120.0, -0.3, 0]]),
            tau=np.array([0.3, 0.3, 0.02, 0.1, 0.1, 0.05, 0.1]),   # measurement noise sd (meq/L)
            regime_sd={0: 0.025, 1: 1.5, 2: 1.2})          # sd of the intervened process in its regime
N_BASE, N_REG = 300, 150
LOWER = [(1, 0), (2, 0), (2, 1)]


# ------------------------------------------------------------------ model
def unpack(p, known, targets):
    """p: unconstrained parameters. Latent scales are fixed by unit baseline noise variance (gauge)."""
    i = 0
    cols = []
    for j in range(n):
        if j in known:
            cols.append(p[i] * S[:, j]); i += 1
        else:
            cols.append(p[i:i + d]); i += d
    G = anp.stack(cols, axis=1)
    a = p[i:i + 3]; i += 3
    newsd = anp.exp(p[i:i + len(targets)]); i += len(targets)
    logtau = p[i:i + d]; i += d
    return G, a, newsd, logtau


def Amat(a):
    return anp.array([[0.0, 0.0, 0.0], [a[0], 0.0, 0.0], [a[1], a[2], 0.0]])


def latent_cov(a, target=None, sd_t=None):
    A = Amat(a)
    om = anp.ones(n)
    if target is not None:
        mask = np.ones((n, n)); mask[target, :] = 0
        A = A * mask
        om = anp.array([sd_t ** 2 if j == target else 1.0 for j in range(n)])
    L = anp.linalg.inv(anp.eye(n) - A)
    return anp.dot(L * om, L.T)


def covs_x(p, known, targets, noise=True):
    G, a, newsd, logtau = unpack(p, known, targets)
    out = []
    for k, t in enumerate([None] + list(targets)):
        Sz = latent_cov(a) if t is None else latent_cov(a, t, newsd[k - 1])
        Sx = anp.dot(anp.dot(G, Sz), G.T)
        if noise:
            Sx = Sx + anp.diag(anp.exp(2 * logtau))
        out.append(Sx)
    return out


def true_params(known, targets):
    """True parameters in the gauge of the model (latents scaled to unit baseline noise)."""
    sd = TRUE['sd']
    G = S * sd[None, :]                                   # z_std = z / sd
    A = TRUE['A'] * sd[None, :] / sd[:, None]
    p = []
    for j in range(n):
        p += [sd[j]] if j in known else list(G[:, j])
    p += [A[1, 0], A[2, 0], A[2, 1]]
    p += [np.log(TRUE['regime_sd'][t] / sd[t]) for t in targets]
    p += list(np.log(TRUE['tau']))
    return np.array(p, float)


# ------------------------------------------------------------------ queries
def q_unit(p, known, targets, x, which):
    """Unit-level counterfactual chemistry (deviation from fresh water) of an observed deviation x."""
    G, a, newsd, logtau = unpack(p, known, targets)
    A = Amat(a)
    H = anp.dot(anp.linalg.inv(anp.dot(G.T, G)), G.T)      # abduction without measurement noise
    z = anp.dot(H, x)
    eps = z - anp.dot(A, z)
    if which == 'pump':                                  # seawater fraction halved, other noises kept
        z1 = 0.5 * z[0]
        z2 = A[1, 0] * z1 + eps[1]
        z3 = A[2, 0] * z1 + A[2, 1] * z2 + eps[2]
        zc = anp.array([z1, z2, z3])
    else:                                                # do(X = 0): no cation exchange
        zc = anp.array([z[0], z[1], 0.0])
    return anp.dot(G, zc)


def q_pop(p, known, targets):
    G, a, newsd, logtau = unpack(p, known, targets)
    Sz = latent_cov(a, 0, 3.0)                           # unobserved regime: sd of s tripled (unit baseline)
    Sx = anp.dot(anp.dot(G, Sz), G.T)
    return Sx[np.triu_indices(d)]


# ------------------------------------------------------------------ part A: identifiability by Jacobian rank
DESIGNS = [
    ('no stoichiometry, baseline only', (), ()),
    ('no stoichiometry, pumping regime', (), (0,)),
    ('no stoichiometry, irrigation regime', (), (1,)),
    ('no stoichiometry, clay-facies regime', (), (2,)),
    ('no stoichiometry, pumping + clay-facies regimes', (), (0, 2)),
    ('no stoichiometry, irrigation + clay-facies regimes', (), (1, 2)),
    ('no stoichiometry, all three regimes', (), (0, 1, 2)),
    ('seawater signature known, baseline only', (0,), ()),
    ('seawater signature known, pumping regime', (0,), (0,)),
    ('seawater signature known, clay-facies regime', (0,), (2,)),
    ('seawater signature known, pumping + clay-facies regimes', (0,), (0, 2)),
    ('seawater + weathering signatures known, baseline only', (0, 1), ()),
    ('seawater + weathering signatures known, pumping regime', (0, 1), (0,)),
    ('seawater + weathering signatures known, clay-facies regime', (0, 1), (2,)),
    ('all three signatures known, baseline only', (0, 1, 2), ()),
    ('exchange signature known only, baseline only', (2,), ()),
]


def identifiability(known, targets, x_obs):
    p = true_params(known, targets)
    f = lambda q: anp.concatenate([C[np.triu_indices(d)] for C in covs_x(q, known, targets, noise=False)])
    J = jacobian(f)(p)
    # drop the measurement-noise parameters (they do not enter the noise-free covariances)
    keep = np.arange(len(p) - d)
    J = J[:, keep]
    U, sv, Vt = np.linalg.svd(J, full_matrices=True)
    rank = int(np.sum(sv > sv[0] * 1e-9))
    N = Vt[rank:].T                                      # null space (unidentified directions)
    res = dict(n_par=len(keep), rank=rank, fibre=len(keep) - rank)
    for name, fq in [('Q1 seawater halved (unit)', lambda q: q_unit(q, known, targets, x_obs, 'pump')),
                     ('Q2 no exchange (unit)', lambda q: q_unit(q, known, targets, x_obs, 'exch')),
                     ('Q3 unobserved pumping regime (population)', lambda q: q_pop(q, known, targets))]:
        Jq = jacobian(fq)(p)[:, keep]
        if N.shape[1] == 0:
            res[name] = 0.0
        else:
            res[name] = float(np.linalg.norm(Jq @ N) / max(np.linalg.norm(Jq), 1e-12))
    return res


# ------------------------------------------------------------------ part B: estimation
def simulate(targets, rng):
    sd, A = TRUE['sd'], TRUE['A']
    data = []
    for t in [None] + list(targets):
        m = N_BASE if t is None else N_REG
        eps = rng.standard_normal((m, n)) * sd
        At = A.copy()
        if t is not None:
            At[t, :] = 0
            eps[:, t] = rng.standard_normal(m) * TRUE['regime_sd'][t]
        z = np.linalg.solve(np.eye(n) - At, eps.T).T
        x = X_FRESH + z @ S.T + rng.standard_normal((m, d)) * TRUE['tau']
        data.append(x)
    return data


def nll(p, known, targets, Ss, ns):
    tot = 0.0
    for Sx, Sk, m in zip(covs_x(p, known, targets), Ss, ns):
        sign, logdet = anp.linalg.slogdet(Sx)
        tot = tot + 0.5 * m * (logdet + anp.trace(anp.linalg.solve(Sx, Sk)))
    return tot


def fit(known, targets, data, rng, restarts):
    Ss = [np.cov(x.T, bias=True) for x in data]
    ns = [len(x) for x in data]
    f = lambda q: nll(q, known, targets, Ss, ns)
    g = grad(f)
    out = []
    p_true = true_params(known, targets)
    for r in range(restarts):
        p0 = p_true.copy()
        i = 0
        for j in range(n):                               # random start for every column and coefficient
            if j in known:
                p0[i] = abs(p_true[i]) * rng.uniform(0.3, 3); i += 1
            else:
                p0[i:i + d] = rng.standard_normal(d) * np.std(p_true[i:i + d]) * 1.5; i += d
        p0[i:i + 3] = rng.standard_normal(3) * 2.0
        p0[i + 3:i + 3 + len(targets)] += rng.standard_normal(len(targets))
        p0[-d:] = np.log(TRUE['tau']) + rng.standard_normal(d) * 0.5
        try:
            r_ = minimize(f, p0, jac=g, method='L-BFGS-B', options=dict(maxiter=3000))
            out.append((float(r_.fun), r_.x))
        except Exception:
            pass
    return out


EST = [('no stoichiometry, baseline only', (), ()),
       ('seawater + weathering signatures known, baseline only', (0, 1), ()),
       ('no stoichiometry, pumping regime', (), (0,)),
       ('no stoichiometry, irrigation + clay-facies regimes', (), (1, 2)),
       ('seawater signature known, pumping + clay-facies regimes', (0,), (0, 2)),
       ('all three signatures known, baseline only', (0, 1, 2), ())]


def _task(args):
    i, rep, known, targets, restarts = args
    rng = np.random.default_rng(1000 * i + rep + 7)
    data = simulate(targets, rng)
    return (i, rep, fit(known, targets, data, rng, restarts))


def run():
    t0 = time.time()
    rng = np.random.default_rng(49)
    # an observed well deviation (noise-free) used for the unit-level queries
    z_obs = np.array([0.012, 0.6, 1.4]) / TRUE['sd']    # in the unit-noise gauge
    x_obs = (S * TRUE['sd'][None, :]) @ z_obs
    log = [f'observed well deviation used for unit-level queries (meq/L): ' + ', '.join(f'{i} {v:.2f}' for i, v in zip(IONS, x_obs))]
    res = dict(ions=IONS, S=S.tolist(), true=dict(sd=TRUE['sd'].tolist(), A=TRUE['A'].tolist(), tau=TRUE['tau'].tolist(),
                                                     regime_sd=TRUE['regime_sd']), N_BASE=N_BASE, N_REG=N_REG, x_obs=x_obs.tolist())
    res['identifiability'] = []
    for name, known, targets in DESIGNS:
        r = identifiability(known, targets, x_obs)
        r.update(name=name, known=list(known), targets=list(targets))
        res['identifiability'].append(r)
        log.append(f'{name:58s} fibre {r["fibre"]}; unidentified share of Q1 {r["Q1 seawater halved (unit)"]:.2e}, '
                   f'Q2 {r["Q2 no exchange (unit)"]:.2e}, Q3 {r["Q3 unobserved pumping regime (population)"]:.2e}')
    # true counterfactuals
    pt0 = true_params((), ())
    cf_true = {k: np.array(q_unit(pt0, (), (), x_obs, k)) for k in ('pump', 'exch')}
    res['cf_true'] = {k: v.tolist() for k, v in cf_true.items()}
    res['estimation'] = []
    n_data, restarts = 10, 6
    tasks = [(i, rep, known, targets, restarts) for i, (name, known, targets) in enumerate(EST) for rep in range(n_data)]
    with Pool(4) as pool:
        outs = pool.map(_task, tasks)
    for i, (name, known, targets) in enumerate(EST):
        errs = {'pump': [], 'exch': []}; spread = {'pump': [], 'exch': []}; ngood = []
        for (j, rep, fits) in outs:
            if j != i or not fits:
                continue
            best = min(f[0] for f in fits)
            good = [f for f in fits if f[0] <= best + 1.0]   # equally good fits (log-likelihood within 1)
            for k in ('pump', 'exch'):
                preds = np.array([np.array(q_unit(f[1], known, targets, x_obs, k)) for f in good])
                scale = np.linalg.norm(cf_true[k] - x_obs)    # size of the counterfactual change
                e = np.linalg.norm(preds - cf_true[k][None, :], axis=1) / scale
                errs[k].append(float(np.median(e)))
                spread[k].append(float(np.max(e) - np.min(e)))
            ngood.append(len(good))
        row = dict(name=name, known=list(known), targets=list(targets), n_data=n_data, restarts=restarts,
                   err_pump_median=float(np.median(errs['pump'])), err_pump_p90=float(np.quantile(errs['pump'], 0.9)),
                   err_exch_median=float(np.median(errs['exch'])), err_exch_p90=float(np.quantile(errs['exch'], 0.9)),
                   spread_pump_median=float(np.median(spread['pump'])), spread_exch_median=float(np.median(spread['exch'])),
                   n_good_median=float(np.median(ngood)), err_pump_all=errs['pump'], err_exch_all=errs['exch'])
        res['estimation'].append(row)
        log.append(f'{name:58s} relative error of the counterfactual (median / 90th pct): seawater halved '
                   f'{row["err_pump_median"]:.3f} / {row["err_pump_p90"]:.3f}, no exchange {row["err_exch_median"]:.3f} / '
                   f'{row["err_exch_p90"]:.3f}; spread over equally good fits {row["spread_pump_median"]:.3f}, '
                   f'{row["spread_exch_median"]:.3f}')
    res['runtime_s'] = time.time() - t0
    json.dump(res, open(os.path.join(HERE, 'burimi_results.json'), 'w'), indent=1)
    txt = '\n'.join(log) + f"\nruntime {res['runtime_s']:.0f} s"
    open(os.path.join(HERE, 'burimi.log'), 'w').write(txt + '\n')
    print(txt)


if __name__ == '__main__':
    run()
