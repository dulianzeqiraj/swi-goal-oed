import numpy as np, time
N = 20; F = 8.0; dt = 0.01
def rhs(x, Fv): return (np.roll(x, -1, 1) - np.roll(x, 2, 1)) * np.roll(x, 1, 1) - x + Fv
def run(Fv, ntraj=100, T=1000.0, seed=0, sample_every=5, keep=False):
    r = np.random.default_rng(seed); x = F + r.standard_normal((ntraj, N))
    for _ in range(int(20/dt)):  # spin-up
        k1 = rhs(x, Fv); k2 = rhs(x + .5*dt*k1, Fv); k3 = rhs(x + .5*dt*k2, Fv); k4 = rhs(x + dt*k3, Fv); x = x + dt/6*(k1+2*k2+2*k3+k4)
    nst = int(T/dt); s = np.zeros(N); out = [] if keep else None
    for t in range(nst):
        k1 = rhs(x, Fv); k2 = rhs(x + .5*dt*k1, Fv); k3 = rhs(x + .5*dt*k2, Fv); k4 = rhs(x + dt*k3, Fv); x = x + dt/6*(k1+2*k2+2*k3+k4)
        s += x.mean(0)
        if keep and t % sample_every == 0: out.append(x.copy())
    return s / nst, (np.array(out) if keep else None)
p, g = 0, 3
t0 = time.time()
dF = 1.0
Fp = np.full(N, F); Fp[p] += dF; Fm = np.full(N, F); Fm[p] -= dF
mp, _ = run(Fp, seed=1); mm, _ = run(Fm, seed=2)
Rdirect = (mp - mm) / (2 * dF)
print(f"direct response row (node p={p} forcing): {np.round(Rdirect[:8],3)}  time {time.time()-t0:.0f}s")
_, X = run(np.full(N, F), ntraj=50, T=400.0, seed=3, keep=True)   # samples every 0.05
X = X - X.mean((0, 1))
dts = 0.05; maxlag = int(4.0 / dts)
T_, M_, _ = X.shape
C = np.array([np.einsum('tmi,tmj->ij', X[lag:], X[:T_-lag]) / ((T_-lag) * M_) for lag in range(maxlag)])
Cint = C.sum(0) * dts - 0.5 * dts * C[0]
def fdt(S):
    S = list(S); Rs = Cint[np.ix_(S, S)] @ np.linalg.inv(C[0][np.ix_(S, S)]); return Rs[S.index(g), S.index(p)]
true = Rdirect[g]
print(f"true d<x_g>/dF_p = {true:.4f} | FDT full-state {fdt(range(N)):.4f} | FDT S={{p,g}} {fdt([p,g]):.4f} | naive regression {C[0][g,p]/C[0][p,p]:.4f}")
ref = fdt(range(N))
others = [i for i in range(N) if i not in (p, g)]
rng = np.random.default_rng(0)
for k in [2, 4, 6, 8]:
    S = [p, g]
    for _ in range(k):
        S.append(min((i for i in others if i not in S), key=lambda i: abs(fdt(S + [i]) - ref)))
    rnd = [abs(fdt([p, g] + list(rng.choice(others, k, replace=False))) - ref) for _ in range(200)]
    print(f"k={k} greedy S={sorted(S)} |FDT_S - FDT_full| {abs(fdt(S)-ref):.4f} | random median {np.median(rnd):.4f}")
