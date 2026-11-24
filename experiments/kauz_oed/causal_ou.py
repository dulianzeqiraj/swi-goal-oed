import numpy as np, itertools
from scipy.linalg import solve_continuous_lyapunov, expm
rng = np.random.default_rng(2)
n = 30
# aquifer transect: diffusion + advection toward coast (index n-1) + damping; plus a hidden regional driver coupling
A = np.zeros((n, n))
for i in range(n):
    A[i, i] = -2.0 - 0.15
    if i > 0: A[i, i-1] = 1.0 + 0.35      # advection from inland neighbour
    if i < n-1: A[i, i+1] = 1.0 - 0.35
A[0, 0] += 0.0
# long-range coupling (e.g. regional recharge / connected paleochannel) between cells 5 and 22
A[22, 5] += 0.6; A[5, 22] += 0.2
Q = np.diag(0.2 + 0.8 * rng.random(n))   # heterogeneous forcing noise
C0 = solve_continuous_lyapunov(A, -Q)    # stationary covariance: A C0 + C0 A^T + Q = 0
Ainv = np.linalg.inv(A)
p, g = 8, 27
R_true = -Ainv[g, p]                     # steady-state causal response of x_g to unit forcing at p
def fdt_partial(S):
    S = list(S); Cint = (-Ainv @ C0)     # integral_0^inf C(tau) dtau = -A^{-1} C0
    Rs = Cint[np.ix_(S, S)] @ np.linalg.inv(C0[np.ix_(S, S)])
    return Rs[S.index(g), S.index(p)]
naive = C0[g, p] / C0[p, p]
print(f"true causal response {R_true:.4f} | naive regression {naive:.4f} | FDT full {fdt_partial(range(n)):.4f} | FDT S={{p,g}} {fdt_partial([p,g]):.4f}")
others = [i for i in range(n) if i not in (p, g)]
for k in [1, 2, 3, 4, 6]:
    S = [p, g]
    for _ in range(k):
        best = min((i for i in others if i not in S), key=lambda i: abs(fdt_partial(S + [i]) - R_true))
        S.append(best)
    rnd = [abs(fdt_partial([p, g] + list(rng.choice(others, k, replace=False))) - R_true) for _ in range(300)]
    near = sorted(others, key=lambda i: min(abs(i-p), abs(i-g)))[:k]
    print(f"k={k} greedy S={sorted(S)} err {abs(fdt_partial(S)-R_true):.4f} | random median err {np.median(rnd):.4f} | nearest-neighbour err {abs(fdt_partial([p,g]+near)-R_true):.4f}")
# bias formula check: B_S = (e^{A tau})_{SH} C_HS C_SS^{-1}; integrated: (-A^{-1})_{SH} C_HS C_SS^{-1}
S = [p, g]; H = [i for i in range(n) if i not in S]
B = (-Ainv)[np.ix_(S, H)] @ C0[np.ix_(H, S)] @ np.linalg.inv(C0[np.ix_(S, S)])
print("bias formula:", round(B[1, 0], 6), " direct:", round(fdt_partial(S) - (-Ainv)[g, p], 6))
