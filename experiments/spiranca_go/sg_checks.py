"""Numerical checks of the three claims N1-N3 of the twenty-paper chloride note (19 October 2026).
N1  E_tau[D] = D* + m tau^2 + o(tau^2) and ESS/N ~ tau^m for the tempered ABC weights exp(-D / (2 tau^2)):
    three cases with N = 20 000 prior draws of a three-dimensional summary: target inside the image (D* = 0, m = 3),
    outside a face of the image (D* > 0, m = 4), and a redundant fact (two-dimensional image, m = 2).
N2  fixed-sequence binomial testing of pumping thresholds (Learn then Test): family-wise error <= delta without
    monotone risk; and the threshold is never below that of the simultaneous band with the same Wald statistics.
N3  EIG_8 <= EIG_16 <= I(Q; y) <= I(theta; y) <= 1/2 logdet(I + C/s^2) <= sum c_s on a linear-Gaussian ensemble
    (exact values for the Gaussian terms, nested-Monte-Carlo for the class terms).
Output res/checks.json"""
import os, json
import numpy as np
from scipy.stats import binom, norm

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(2026)


def n1():
    N = 20000
    out = {}
    U = rng.uniform(-1, 1, (N, 3))
    cases = dict(inside=(U, np.zeros(3), 3), face=(U, np.array([1.5, 0.0, 0.0]), 4))
    V = rng.uniform(-1, 1, (N, 2))
    cases['redundant'] = (np.column_stack([V, V.sum(1) / 2]), np.zeros(3), 2)
    for name, (S, s, m_th) in cases.items():
        D = ((S - s) ** 2).sum(1)
        taus = np.geomspace(0.05, 0.3, 12)
        Dbar, ess = [], []
        for t in taus:
            lw = -D / (2 * t * t); w = np.exp(lw - lw.max()); w /= w.sum()
            Dbar.append(float(w @ D)); ess.append(float(1 / (w ** 2).sum()))
        Dbar, ess = np.array(Dbar), np.array(ess)
        ok = ess > 100
        A = np.column_stack([np.ones(ok.sum()), taus[ok] ** 2])
        c = np.linalg.lstsq(A, Dbar[ok], rcond=None)[0]
        slope_ess = np.polyfit(np.log(taus[ok]), np.log(ess[ok] / N), 1)[0]
        out[name] = dict(D_star_true=float(D.min()) if name == 'face' else 0.0, D_star_hat=float(c[0]), m_hat=float(c[1]),
                         m_theory=m_th, ess_exponent=float(slope_ess), taus=taus[ok].tolist())
    return out


def n2(reps=20000, J=12, n=40, alpha=0.10, delta=0.10):
    """risk curve over thresholds Q_1 < ... < Q_J, non-monotone on purpose (a bump in the middle)."""
    R = np.array([0.02, 0.03, 0.05, 0.07, 0.12, 0.06, 0.08, 0.09, 0.11, 0.15, 0.2, 0.3])
    true_ok = R <= alpha
    fwer = 0; dom_viol = 0; jfs_mean = []; jband_mean = []
    zc = norm.ppf(1 - delta)
    for _ in range(reps):
        X = rng.binomial(n, R)
        p = binom.cdf(X, n, alpha)
        rej = p <= delta
        j = -1
        for k in range(J):
            if rej[k]: j = k
            else: break
        if j >= 0 and not np.all(true_ok[:j + 1]):
            fwer += 1
        # same Wald statistics for both rules
        ph = X / n; se = np.sqrt(np.maximum(ph * (1 - ph), 1e-4) / n)
        # sup-t critical value of J correlated-free statistics (Bonferroni-free simulation of max of J normals)
        cJ = norm.ppf(1 - delta / J)            # conservative band constant (the band uses c_J >= z_{1-delta})
        fs = ph + zc * se <= alpha
        bd = ph + cJ * se <= alpha
        jf = int(np.argmin(np.r_[fs, False])) - 1 if fs[0] else -1
        jb = int(np.argmin(np.r_[bd, False])) - 1 if bd[0] else -1
        if jf < jb: dom_viol += 1
        jfs_mean.append(jf); jband_mean.append(jb)
    return dict(fwer=fwer / reps, delta=delta, dominance_violations=dom_viol,
                mean_index_fixed_sequence=float(np.mean(jfs_mean)), mean_index_band=float(np.mean(jband_mean)),
                risk_curve=R.tolist(), n_per_arm=n)


def n3(Ns=4000, ncand=6, k=3, sig=0.1):
    """linear-Gaussian ensemble: theta ~ N(0, I_5), f = L theta (6 candidates), Q = q' theta; designs of 3."""
    L = rng.standard_normal((ncand, 5)) * 0.3; q = rng.standard_normal(5)
    import itertools
    rows = []
    for S in list(itertools.combinations(range(ncand), k))[:8]:
        S = list(S); C = L[S] @ L[S].T
        up_det = 0.5 * np.linalg.slogdet(np.eye(k) + C / sig ** 2)[1]
        up_had = float(np.sum(0.5 * np.log1p(np.diag(C) / sig ** 2)))
        # I(theta; y) = I(f_S; y) exactly the logdet term for Gaussian theta
        cov_qy = L[S] @ q; var_y = C + sig ** 2 * np.eye(k); r2 = cov_qy @ np.linalg.solve(var_y, cov_qy) / (q @ q)
        I_Q = -0.5 * np.log(1 - r2)
        # class information by Monte Carlo: B = quantile class of Q (8 and 16 classes), H(B) - E H(B | y)
        th = rng.standard_normal((Ns, 5)); Qv = th @ q; y = th @ L[S].T + sig * rng.standard_normal((Ns, k))
        # posterior of Q given y is Gaussian with known mean/var: use it to compute class probabilities exactly
        Kq = np.linalg.solve(var_y, cov_qy); mq = y @ Kq; vq = q @ q - cov_qy @ Kq
        res = {}
        for nc in (8, 16):
            edges = norm.ppf(np.linspace(0, 1, nc + 1)[1:-1]) * np.sqrt(q @ q)
            cdf = norm.cdf((edges[None, :] - mq[:, None]) / np.sqrt(vq))
            P = np.diff(np.column_stack([np.zeros(Ns), cdf, np.ones(Ns)]), axis=1)
            Hc = -(P * np.log(np.clip(P, 1e-300, 1))).sum(1).mean()
            res[nc] = float(np.log(nc) - Hc)
        rows.append(dict(S=S, eig8=res[8], eig16=res[16], I_Q=float(I_Q), I_theta=float(up_det), logdet=float(up_det), hadamard=up_had,
                         chain_ok=bool(res[8] <= res[16] + 0.01 and res[16] <= I_Q + 0.01 and I_Q <= up_det + 1e-12 and up_det <= up_had + 1e-12)))
    return rows


if __name__ == '__main__':
    out = dict(n1=n1(), n2=n2(), n3=n3())
    json.dump(out, open(os.path.join(HERE, 'res', 'checks.json'), 'w'), indent=1)
    print(json.dumps(out['n1'], indent=1)[:1500]); print(out['n2']); print([(r['S'], round(r['eig8'], 3), round(r['eig16'], 3), round(r['I_Q'], 3), round(r['logdet'], 3), round(r['hadamard'], 3), r['chain_ok']) for r in out['n3']])
