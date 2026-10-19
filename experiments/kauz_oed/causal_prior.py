import numpy as np
from scipy.linalg import solve_continuous_lyapunov
n = 30; p, g = 8, 27
def build(adv, damp, cpl, back, qdiag):
    A = np.zeros((n, n))
    for i in range(n):
        A[i, i] = -2.0 - damp
        if i > 0: A[i, i-1] = 1.0 + adv
        if i < n-1: A[i, i+1] = 1.0 - adv
    A[22, 5] += cpl; A[5, 22] += back
    C0 = solve_continuous_lyapunov(A, -np.diag(qdiag))
    return A, C0
def fdt(A, C0, S):
    S = list(S); Ainv = np.linalg.inv(A); Cint = -Ainv @ C0
    Rs = Cint[np.ix_(S, S)] @ np.linalg.inv(C0[np.ix_(S, S)])
    return Rs[S.index(g), S.index(p)], -Ainv[g, p]
# truth = the model of causal_ou.py
rng = np.random.default_rng(2)
qtrue = 0.2 + 0.8 * rng.random(n)
At, Ct = build(0.35, 0.15, 0.6, 0.2, qtrue)
# prior ensemble: hydraulic parameters and coupling strengths uncertain, noise levels uncertain
pr = np.random.default_rng(7)
ens = [build(pr.uniform(0.25, 0.45), pr.uniform(0.08, 0.25), pr.uniform(0.2, 1.0), pr.uniform(0.0, 0.4), 0.2 + 0.8 * pr.random(n)) for _ in range(60)]
others = [i for i in range(n) if i not in (p, g)]
def ebias(S):
    return np.mean([(lambda r: (r[0] - r[1])**2)(fdt(A, C, S)) for A, C in ens])
S = [p, g]
print("truth: R=%.4f" % fdt(At, Ct, [p, g])[1])
for k in range(1, 7):
    best = min((i for i in others if i not in S), key=lambda i: ebias(S + [i]))
    S.append(best)
    est, tr = fdt(At, Ct, S)
    near = sorted(others, key=lambda i: min(abs(i-p), abs(i-g)))[:k]
    en, _ = fdt(At, Ct, [p, g] + near)
    print(f"k={k} prior-greedy S={sorted(S)} rmse_prior={np.sqrt(ebias(S)):.4f} | on truth: est {est:.4f} err {abs(est-tr):.4f} ({100*abs(est-tr)/tr:.1f}%) | nearest err {abs(en-tr):.4f}")
