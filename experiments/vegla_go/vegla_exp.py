"""VEGLA-GO experiment: which extra measurement certifies the instrument, in the large-sample limit and with
finite records. Writes vegla_results.json.   Run: python3 vegla_exp.py   (about 4 minutes; the graph space is
cached in vegla_space.npz after the first run, about 1 minute).

Large-sample limit (exact): for every design the space of 16384 graphs is partitioned by the observable
d-separation signature; a class settles the validity question if all its graphs agree. Criteria per design:
  structural:   H(signature) and the expected size of the equivalence class (what a generic design maximizes)
  VEGLA-GO:     probability that validity is settled, mutual information I(valid; signature), Bayes risk of
                the validity decision.
Finite records: for draws (graph, coefficients) from the prior, n samples are simulated from the linear cyclic
model with latent confounders; all conditional-independence tests among the observed variables are run
(Fisher z, alpha = 0.05) and each graph is scored by the weighted agreement of its signature with the tests,
weight |log p - log alpha| (Hyttinen, Eberhardt & Jarvisalo, 2014). Two decision rules are compared:
  optimum:     the optimal graphs (an equivalence class) certify the instrument if all are valid, refute it if
               all are invalid, and leave it undetermined otherwise (the rule implied by the base paper);
  calibrated:  the margin m = (best score of a valid graph) - (best score of an invalid graph) certifies when
               m exceeds the 95 % quantile of m over invalid instruments, and refutes when m is below the 5 %
               quantile over valid ones; the quantiles are set on calibration draws from the prior at the
               planned record length and evaluated on independent test draws (false certification about 5 %).
VEGLA-GO ranks designs by the calibrated probability of a correct decision (preposterior analysis).
"""
import json
import os
import time
import numpy as np
from scipy.stats import norm
import vegla as V

HERE = os.path.dirname(os.path.abspath(__file__))
ALPHA = 0.05
NS = [120, 240, 960]          # 10 and 20 years of monthly records, 80 years (or 2.6 years of daily records)
M_DRAWS = 1000
SIGN = {('Z', 'Q'): 1, ('Q', 'H'): -1, ('H', 'C'): -1, ('Z', 'A'): 1, ('Z', 'H'): -1, ('R', 'H'): 1, ('R', 'Q'): -1,
        ('R', 'A'): -1, ('A', 'H'): -1, ('Q', 'C'): 1, ('C', 'Q'): -1, ('A', 'C'): 1}
Q, C, Z = V.IDX['Q'], V.IDX['C'], V.IDX['Z']


def draw_model(code, rng):
    d, bi = V.graph_edges(code)
    while True:
        B = np.zeros((V.NV, V.NV))
        for a, b in d:
            B[b, a] = SIGN[(V.NAMES[a], V.NAMES[b])] * rng.uniform(0.4, 0.9)
        if np.max(np.abs(np.linalg.eigvals(B))) < 0.95:
            break
    lam = [(a, b, rng.uniform(0.4, 0.8) * rng.choice([-1, 1]), rng.uniform(0.4, 0.8) * rng.choice([-1, 1])) for a, b in bi]
    Om = np.eye(V.NV)
    for a, b, la, lb in lam:
        Om[a, a] += la * la; Om[b, b] += lb * lb; Om[a, b] += la * lb; Om[b, a] += la * lb
    return B, lam, Om


def simulate(B, lam, n, rng):
    e = rng.standard_normal((n, V.NV))
    for a, b, la, lb in lam:
        L = rng.standard_normal(n); e[:, a] += la * L; e[:, b] += lb * L
    return np.linalg.solve(np.eye(V.NV) - B, e.T).T


def effects(B, Om):
    """true effect of do(Q) on C, and the population IV ratio cov(Z,C)/cov(Z,Q)."""
    Bc = B.copy(); Bc[Q, :] = 0
    eff = np.linalg.inv(np.eye(V.NV) - Bc)[C, Q]
    M = np.linalg.inv(np.eye(V.NV) - B); S = M @ Om @ M.T
    return float(eff), float(S[Z, C] / S[Z, Q])


def tests(X):
    """p-values of all 240 statements (Fisher z on partial correlations)."""
    n = X.shape[0]
    Cv = np.cov(X.T)
    p = np.empty(V.NST)
    for k, (x, y, S) in enumerate(V.STMTS):
        Sl = [s for s in range(V.NV) if S >> s & 1]
        idx = [x, y] + Sl
        P = np.linalg.inv(Cv[np.ix_(idx, idx)])
        r = -P[0, 1] / np.sqrt(P[0, 0] * P[1, 1])
        z = np.sqrt(max(n - len(Sl) - 3, 1)) * np.arctanh(np.clip(r, -0.999999, 0.999999))
        p[k] = 2 * norm.sf(abs(z))
    return p


def main():
    t0 = time.time()
    sig, valid = V.enumerate_space()
    out = {'alpha': ALPHA, 'n': NS, 'draws': M_DRAWS, 'designs': list(V.DESIGNS), 'exact': {}, 'sim': {}, 'examples': []}
    for kind in ['phys', 'flat']:
        w = V.prior_weights(kind)
        out['exact'][kind] = {'P_valid': float((w * valid).sum()),
                              **{nm: V.exact_design_value(sig, valid, w, obs) for nm, obs in V.DESIGNS.items()}}
    print(f'exact tables {time.time() - t0:.0f}s')
    cols = {nm: V.design_columns(obs) for nm, obs in V.DESIGNS.items()}
    sigf = sig.astype(np.float32)
    for kind in ['phys', 'flat']:
        rng = np.random.default_rng(2026 if kind == 'phys' else 2027)
        w = V.prior_weights(kind)
        codes = rng.choice(len(w), size=2 * M_DRAWS, p=w)          # first half calibration, second half test
        models = [draw_model(int(c), rng) for c in codes]
        truth = valid[codes]
        eff = np.array([effects(B, Om) for B, lam, Om in models])
        res_k = {}
        for n in NS:
            P = np.array([tests(simulate(B, lam, n, rng)) for B, lam, Om in models])     # draws x 240
            dec = P > ALPHA                                                                # True = independent
            wt = np.abs(np.log(np.clip(P, 1e-300, 1)) - np.log(ALPHA))
            res_n = {}
            cal, tst = np.arange(M_DRAWS), np.arange(M_DRAWS, 2 * M_DRAWS)
            for nm, cm in cols.items():
                s = (wt[:, cm] * (2 * dec[:, cm] - 1)).T.astype(np.float32)          # k x draws
                score = sigf[:, cm] @ s                                                # graphs x draws
                sv = np.where(valid[:, None], score, -np.inf).max(0); si = np.where(valid[:, None], -np.inf, score).max(0)
                m = sv - si                                                            # evidence margin for validity
                tc = max(float(np.quantile(m[cal][~truth[cal]], 0.95)), 0.0)
                tr = min(float(np.quantile(m[cal][truth[cal]], 0.05)), 0.0)
                ccert, crefu = m > tc, m < tr
                tv, ti = tst[truth[tst]], tst[~truth[tst]]
                calib = dict(threshold_certify=tc, threshold_refute=tr,
                             certify_valid=float(ccert[tv].mean()), refute_invalid=float(crefu[ti].mean()),
                             certify_invalid=float(ccert[ti].mean()), refute_valid=float(crefu[tv].mean()),
                             correct=float((ccert[tv].sum() + crefu[ti].sum()) / len(tst)),
                             correct_cal=float((ccert[cal][truth[cal]].sum() + crefu[cal][~truth[cal]].sum()) / len(cal)))
                sc, ct, tt, et = score[:, tst], codes[tst], truth[tst], eff[tst]        # optimum rule, test draws
                best = sc >= sc.max(axis=0, keepdims=True) - 1e-4
                nv = (best & valid[:, None]).sum(0); nb = best.sum(0)
                cert = nv == nb; refu = nv == 0; und = ~(cert | refu)
                hit = best[ct, np.arange(M_DRAWS)]
                bias = np.abs(et[:, 1] - et[:, 0]) / np.maximum(np.abs(et[:, 0]), 1e-9)
                fc = cert & ~tt
                res_n[nm] = dict(calibrated=calib,
                    certify_valid=float(cert[tt].mean()), refute_valid=float(refu[tt].mean()),
                    undetermined_valid=float(und[tt].mean()),
                    certify_invalid=float(cert[~tt].mean()), refute_invalid=float(refu[~tt].mean()),
                    undetermined_invalid=float(und[~tt].mean()),
                    correct=float(((cert & tt) | (refu & ~tt)).mean()),
                    true_graph_in_optimum=float(hit.mean()), class_size=float(np.median(nb)),
                    false_cert_rel_bias=float(np.median(bias[fc])) if fc.any() else None)
            res_k[str(n)] = res_n
            print(f'{kind} n={n} {time.time() - t0:.0f}s')
        relb = np.abs(eff[:, 1] - eff[:, 0]) / np.maximum(np.abs(eff[:, 0]), 1e-9)
        res_k['truth'] = dict(P_valid=float(truth.mean()), iv_rel_bias_invalid_median=float(np.median(relb[~truth])),
                              iv_rel_bias_valid_max=float(relb[truth].max()))
        out['sim'][kind] = res_k
    # examples: pathways that invalidate the instrument in three graphs of the space
    for edges in [[('->', 'Z', 'A'), ('->', 'A', 'H'), ('->', 'C', 'Q')],
                  [('<->', 'Z', 'R'), ('->', 'R', 'H'), ('<->', 'H', 'C')],
                  [('->', 'Z', 'H'), ('->', 'C', 'Q'), ('<->', 'Q', 'C')]]:
        code = sum(1 << V.OPT.index(e) for e in edges)
        d, bi = V.graph_edges(code)
        out['examples'].append({'edges': [' '.join(e[1:]) if e[0] == '->' else f'{e[1]}<->{e[2]}' for e in edges],
                                'valid': bool(valid[code]), 'pathways': V.open_paths(d, bi)})
    json.dump(out, open(os.path.join(HERE, 'vegla_results.json'), 'w'), indent=1)
    print(f'done {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
