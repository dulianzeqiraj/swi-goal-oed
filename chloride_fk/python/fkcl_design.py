"""Goal-oriented design of new chloride sampling in existing wells of the Fushe-Kuqe-Lezhe sector.

Goal Q: area of the coastal sector whose upper-layer (first-aquifer) chloride exceeds 250 mg/L [km2]
(secondary goal: the same area for the second aquifer, mid-depth screens).
Candidates: the 79 wells inside the aquifer polygon and the chloride model sector, each sampled at one of
three depths (upper, middle, base) -> 237 candidate samples.
Observation: y = log10(Cl) + e, e ~ N(0, SIG^2) (analytical, sampling and representativeness error).

Criteria
  linear EIG    -1/2 ln(1 - R^2_Q(S)),  R^2_Q(S) = b_S' (C_SS + SIG^2 I)^-1 b_S / var(Q)   (ensemble moments;
                Lemma 1 of the companion study / Theorem 1 of the SINERGO note)
  exact EIG     I(B; Y_S) of the goal discretized in NB equiprobable bins, by likelihood reweighting of the
                posterior ensemble (leave-one-out over unique members); a lower bound on I(Q; Y_S)
Search: greedy, pairwise greedy (SINERGO), exhaustive over the top candidates for k = 2 and 3.
Outputs ../results/design_*.json/csv
"""
import os
import sys
import json
import itertools
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fkcl_model as M  # noqa: E402

RES = os.path.join(HERE, '..', 'results')
SIG = 0.10
NB = 8
DEPTHS = ['sh', 'mid', 'dp']


def candidates(m):
    W = pd.read_excel(M.fk.default_xlsx(), sheet_name='2_All_Wells')
    x = (W.X_GaussKruger.to_numpy(float) - m.base.x0) / 1000
    y = (W.Y_GaussKruger.to_numpy(float) - m.base.y0) / 1000
    i = np.round(x / m.dx).astype(int); j = np.round(y / m.dx).astype(int)
    ok = (i >= 0) & (i < m.base.nx) & (j >= 0) & (j < m.base.ny)
    cell = np.full(len(W), -1); cell[ok] = m.base.idx[j[ok], i[ok]]
    good = (cell >= 0) & (W.Inside_Aquifer.eq('YES').to_numpy())
    good &= np.where(cell >= 0, m.valid[np.maximum(cell, 0)], False)
    return pd.DataFrame(dict(well=W.Well_ID[good].astype(str).to_numpy(), x_km=x[good], y_km=y[good],
                             cell=cell[good], dist_km=m.dist[cell[good]]))


def r2(Cov, b, varq, S):
    S = list(S)
    if not S:
        return 0.0
    CS = Cov[np.ix_(S, S)] + SIG ** 2 * np.eye(len(S))
    bS = b[S]
    return float(bS @ np.linalg.solve(CS, bS) / varq)


def eig_lin(Cov, b, varq, S):
    return -0.5 * np.log(max(1.0 - r2(Cov, b, varq, S), 1e-12))


def greedy(Cov, b, varq, k, start=()):
    S = list(start)
    while len(S) < k:
        best = max((c for c in range(len(b)) if c not in S), key=lambda c: eig_lin(Cov, b, varq, S + [c]))
        S.append(best)
    return S


def pair_greedy(Cov, b, varq, k, pool):
    S = []
    while len(S) + 2 <= k:
        best, bv = None, -1
        for a, c in itertools.combinations([p for p in pool if p not in S], 2):
            v = eig_lin(Cov, b, varq, S + [a, c])
            if v > bv:
                best, bv = [a, c], v
        S += best
    if len(S) < k:
        S = greedy(Cov, b, varq, k, S)
    return S


def swap(Cov, b, varq, S, pool):
    S = list(S); cur = eig_lin(Cov, b, varq, S); improved = True
    while improved:
        improved = False
        for i in range(len(S)):
            for c in pool:
                if c in S:
                    continue
                T = S.copy(); T[i] = c
                v = eig_lin(Cov, b, varq, T)
                if v > cur + 1e-12:
                    S, cur, improved = T, v, True
    return S


def exact_eig(G, Qbin, S, rng, nrep=1):
    """I(B; Y_S) by leave-one-out likelihood reweighting over the ensemble rows of G (log10 Cl at candidates)."""
    n = G.shape[0]
    pB = np.bincount(Qbin, minlength=NB) / n
    HB = -np.sum(pB[pB > 0] * np.log(pB[pB > 0]))
    GS = G[:, S]
    one = np.eye(NB)[Qbin]
    Hc = 0.0
    for _ in range(nrep):
        Y = GS + SIG * rng.standard_normal(GS.shape)
        D = ((Y[:, None, :] - GS[None, :, :]) ** 2).sum(-1) / (2 * SIG ** 2)
        np.fill_diagonal(D, np.inf)
        D -= D.min(1, keepdims=True)
        Wt = np.exp(-D); Wt /= Wt.sum(1, keepdims=True)
        pb = Wt @ one
        Hc += np.mean(-np.sum(np.where(pb > 0, pb * np.log(np.maximum(pb, 1e-300)), 0.0), 1))
    return HB - Hc / nrep


def main():
    m = M.Model()
    E = np.load(os.path.join(RES, 'post_ensemble.npz'))
    _, uniq = np.unique(E['idx'], return_index=True)
    uniq = np.sort(uniq)
    A = m.area / 1e6
    v = m.valid
    Q = {'sh': ((E['Cl_sh'][uniq] > M.CL_LIMIT) & v).sum(1) * A,
         'mid': ((E['Cl_mid'][uniq] > M.CL_LIMIT) & v).sum(1) * A}
    cand = candidates(m)
    labels, cols = [], []
    for d in DEPTHS:
        F = np.log10(E['Cl_' + d][uniq][:, cand.cell.to_numpy()].astype(float))
        cols.append(F)
        labels += [f'{w}:{d}' for w in cand.well]
    G = np.hstack(cols)                       # members x 3*n_wells
    nW = len(cand)
    rng = np.random.default_rng(3)
    out = dict(n_members=int(len(uniq)), n_wells=nW, sig=SIG, nbins=NB, goals={})
    rows = []
    for gname, q in Q.items():
        Gc = G - G.mean(0)
        qc = q - q.mean()
        Cov = Gc.T @ Gc / (len(q) - 1)
        b = Gc.T @ qc / (len(q) - 1)
        varq = qc @ qc / (len(q) - 1)
        single = np.array([eig_lin(Cov, b, varq, [c]) for c in range(G.shape[1])])
        Qbin = np.minimum((np.argsort(np.argsort(q)) * NB) // len(q), NB - 1)
        top = list(np.argsort(-single)[:40])
        # exact vs linear for the 40 best single samples + 40 random
        test = top + list(rng.choice(np.setdiff1d(np.arange(G.shape[1]), top), 40, replace=False))
        ex1 = np.array([exact_eig(G, Qbin, [c], rng) for c in test])
        from scipy.stats import spearmanr
        rho1 = spearmanr(single[test], ex1).correlation
        res = dict(var_Q=float(varq), Q_quantiles=[float(np.quantile(q, a)) for a in (0.05, 0.5, 0.95)],
                   spearman_single_linear_vs_exact=float(rho1), designs={})
        pool = top[:25]
        for k in (1, 2, 3, 4, 5):
            Sg = greedy(Cov, b, varq, k)
            Sp = pair_greedy(Cov, b, varq, k, pool) if k >= 2 else Sg
            Sb = max([Sg, Sp], key=lambda S: eig_lin(Cov, b, varq, S))
            Ss = swap(Cov, b, varq, Sb, top)
            entry = {}
            for nm, S in (('greedy', Sg), ('pair_greedy', Sp), ('best_swap', Ss)):
                entry[nm] = dict(sites=[labels[c] for c in S], eig_lin=eig_lin(Cov, b, varq, S),
                                 eig_exact=exact_eig(G, Qbin, S, rng))
            if k in (2, 3):
                best, bv = None, -1
                for S in itertools.combinations(top, k):
                    vv = eig_lin(Cov, b, varq, list(S))
                    if vv > bv:
                        best, bv = list(S), vv
                entry['exhaustive_top40'] = dict(sites=[labels[c] for c in best], eig_lin=bv,
                                                 eig_exact=exact_eig(G, Qbin, best, rng))
            res['designs'][k] = entry
        # reference designs: the published monitoring wells that fall in the sector (A13, A10), upper screens
        ref = [labels.index(f'{w}:sh') for w in ('A13', 'A10') if f'{w}:sh' in labels]
        res['published_in_sector_upper'] = dict(sites=[labels[c] for c in ref], eig_lin=eig_lin(Cov, b, varq, ref),
                                               eig_exact=exact_eig(G, Qbin, ref, rng))
        # depth value: best single sample per depth
        res['best_single_by_depth'] = {d: dict(site=labels[int(np.argmax(single[i * nW:(i + 1) * nW])) + i * nW],
                                               eig_lin=float(single[i * nW:(i + 1) * nW].max()))
                                       for i, d in enumerate(DEPTHS)}
        out['goals'][gname] = res
        for c in range(G.shape[1]):
            w_, d_ = labels[c].split(':')
            r_ = cand[cand.well == w_].iloc[0]
            rows.append(dict(goal=gname, well=w_, depth=d_, x_km=r_.x_km, y_km=r_.y_km, dist_km=r_.dist_km,
                             eig_lin=single[c]))
        # EIG field over all sector cells (single sample), upper and middle depth
        for d in ('sh', 'mid'):
            F = np.log10(E['Cl_' + d][uniq][:, v].astype(float))
            Fc = F - F.mean(0)
            cv = Fc.T @ qc / (len(q) - 1)
            vg = (Fc ** 2).sum(0) / (len(q) - 1)
            r2c = cv ** 2 / (varq * (vg + SIG ** 2))
            fld = np.full(m.Nc, np.nan); fld[v] = -0.5 * np.log(np.maximum(1 - r2c, 1e-12))
            np.save(os.path.join(RES, f'eigfield_{gname}_{d}.npy'), fld.astype(np.float32))
    pd.DataFrame(rows).to_csv(os.path.join(RES, 'design_candidates.csv'), index=False, float_format='%.5g')
    json.dump(out, open(os.path.join(RES, 'design_summary.json'), 'w'), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))


if __name__ == '__main__':
    main()
