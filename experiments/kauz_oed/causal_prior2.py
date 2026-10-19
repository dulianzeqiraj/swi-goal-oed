import numpy as np
exec(open('causal_prior.py').read().split("# truth = the model")[0])
pr = np.random.default_rng(7)
draw = lambda r: build(r.uniform(0.25, 0.45), r.uniform(0.08, 0.25), r.uniform(0.2, 1.0), r.uniform(0.0, 0.4), 0.2 + 0.8 * r.random(n))
ens = [draw(pr) for _ in range(60)]                       # design ensemble
tst = [draw(np.random.default_rng(1000 + s)) for s in range(200)]   # independent test truths
others = [i for i in range(n) if i not in (p, g)]
def errs(S, models):
    out = []
    for A, C in models:
        e, t = fdt(A, C, S); out.append(abs(e - t) / abs(t))
    return np.array(out)
ebias = lambda S: np.mean([(fdt(A, C, S)[0] - fdt(A, C, S)[1])**2 for A, C in ens])
base = errs([p, g], tst); naive = np.array([abs(C[g, p]/C[p, p] - fdt(A, C, [p, g])[1]) / abs(fdt(A, C, [p, g])[1]) for A, C in tst])
print(f"S={{p,g}} median rel err {np.median(base):.2f} | naive regression median rel err {np.median(naive):.2f}")
S = [p, g]; rr = np.random.default_rng(3)
for k in range(1, 7):
    S.append(min((i for i in others if i not in S), key=lambda i: ebias(S + [i])))
    near = sorted(others, key=lambda i: min(abs(i-p), abs(i-g)))[:k]
    rnd = np.median([np.median(errs([p, g] + list(rr.choice(others, k, replace=False)), tst[:40])) for _ in range(20)])
    eg, en = errs(S, tst), errs([p, g] + near, tst)
    print(f"k={k} S={sorted(S)} | median rel err greedy {np.median(eg):.3f} (90% {np.quantile(eg,.9):.3f}) | nearest {np.median(en):.3f} (90% {np.quantile(en,.9):.3f}) | random {rnd:.3f}")
