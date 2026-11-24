import numpy as np
exec(open('causal_l96.py').read().split("p, g = 0, 3")[0])
p = 0; dF = 1.0
Fp = np.full(N, F); Fp[p] += dF; Fm = np.full(N, F); Fm[p] -= dF
R1 = (run(Fp, seed=11)[0] - run(Fm, seed=12)[0]) / 2
R2 = (run(Fp, seed=21)[0] - run(Fm, seed=22)[0]) / 2
_, X = run(np.full(N, F), ntraj=50, T=400.0, seed=3, keep=True); X = X - X.mean((0, 1))
dts = 0.05; maxlag = int(4.0 / dts); T_, M_, _ = X.shape
C = np.array([np.einsum('tmi,tmj->ij', X[lag:], X[:T_-lag]) / ((T_-lag) * M_) for lag in range(maxlag)])
Cint = C.sum(0) * dts - 0.5 * dts * C[0]
Rf = (Cint @ np.linalg.inv(C[0]))[:, p]
print("direct run A:", np.round(R1[:8], 3)); print("direct run B:", np.round(R2[:8], 3)); print("FDT full    :", np.round(Rf[:8], 3))
print("noise sd of direct (A-B)/sqrt2:", np.round(np.std(R1 - R2) / np.sqrt(2), 3), " corr(direct mean, FDT):", np.round(np.corrcoef((R1+R2)/2, Rf)[0,1], 3))
print("regression row:", np.round(C[0][:8, p] / C[0][p, p], 3))
